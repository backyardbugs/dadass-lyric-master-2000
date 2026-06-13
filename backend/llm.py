"""
Single-pass Gemini corpus analysis: build one markdown document from all tracks,
one API call (chunked if very large), parse and fan out per-track results.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from typing import Any

import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# Chunk when the corpus doc exceeds this many characters (~15 songs typical).
MAX_DOC_CHARS = int(os.getenv("GEMINI_MAX_DOC_CHARS", "70000"))
MAX_TRACKS_PER_CHUNK = int(os.getenv("GEMINI_CHUNK_TRACKS", "12"))

_VALID_ACTS = {
    "statement", "question", "command", "promise", "apology",
    "plea", "accusation", "confession", "exclamation",
}
_VALID_IMAGERY = {"concrete", "abstract", "referential"}


def is_enabled() -> bool:
    if os.getenv("GEMINI_ENABLED", "1").lower() in ("0", "false", "no"):
        return False
    return bool(GEMINI_API_KEY)


def is_available() -> bool:
    return is_enabled()


def lyrics_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()[:16]


def _track_lines(track: dict) -> list[str]:
    text = track.get("cleaned_lyrics") or track.get("raw_lyrics") or ""
    return [l.strip() for l in text.split("\n") if l.strip()]


def build_corpus_markdown(tracks: list[dict], dataset_name: str) -> str:
    """One markdown doc with stable track_id headers and numbered lines."""
    parts = [f"# Dataset: {dataset_name}", ""]
    for t in tracks:
        lines = _track_lines(t)
        if not lines:
            continue
        tid = t.get("id")
        title = t.get("title") or "Unknown"
        artist = t.get("artist") or ""
        parts.append(f"## [track_id:{tid}] {title} — {artist}")
        for i, line in enumerate(lines):
            parts.append(f"{i}|{line}")
        parts.append("")
    return "\n".join(parts).strip()


def _chunk_tracks(tracks: list[dict], dataset_name: str) -> list[list[dict]]:
    """Split tracks into chunks that fit context limits."""
    with_lyrics = [t for t in tracks if _track_lines(t)]
    if not with_lyrics:
        return []
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for t in with_lyrics:
        trial = current + [t]
        if (
            len(trial) > MAX_TRACKS_PER_CHUNK
            or len(build_corpus_markdown(trial, dataset_name)) > MAX_DOC_CHARS
        ):
            if current:
                chunks.append(current)
            current = [t]
        else:
            current = trial
    if current:
        chunks.append(current)
    return chunks


def _repair_truncated_json(text: str) -> str | None:
    """Best-effort repair when Gemini truncates mid-JSON (max output tokens)."""
    start = text.find("{")
    if start < 0:
        return None
    body = text[start:].rstrip()
    # Drop trailing incomplete key/string/value fragments
    body = re.sub(r',\s*"[^"\n\\]*$', "", body)
    body = re.sub(r':\s*"[^"\n\\]*$', ': ""', body)
    body = re.sub(r',\s*$', "", body)

    stack: list[str] = []
    in_string = False
    escape = False
    for ch in body:
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in "}]":
            if stack and stack[-1] == ch:
                stack.pop()

    if in_string:
        body += '"'
    if stack:
        body += "".join(reversed(stack))
    return body


def _extract_json(text: str) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None

    candidates: list[str] = [text]
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        candidates.append(m.group(1).strip())
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        candidates.append(text[start : end + 1])
    if start >= 0:
        repaired = _repair_truncated_json(text)
        if repaired:
            candidates.append(repaired)

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return None


def _call_gemini(prompt: str, *, temperature: float = 0.2, timeout: int = 120) -> str | None:
    if not GEMINI_API_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }
    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    for attempt in range(4):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 429:
                wait = min(60, 2 ** attempt * 8)
                msg = resp.json().get("error", {}).get("message", "")
                m = re.search(r"retry in ([0-9.]+)s", msg, re.I)
                if m:
                    wait = max(wait, float(m.group(1)) + 2)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return parts[0].get("text") if parts else None
        except Exception:
            if attempt >= 3:
                return None
            time.sleep(2 ** attempt)
    return None


def _normalize_sections(raw: list, n_lines: int) -> list[dict]:
    out = []
    for s in raw or []:
        if not isinstance(s, dict):
            continue
        label = str(s.get("label") or "Section").strip() or "Section"
        start = int(s.get("start", s.get("start_line", 0)))
        end = int(s.get("end", s.get("end_line", start)))
        start = max(0, min(start, max(0, n_lines - 1)))
        end = max(start, min(end, max(0, n_lines - 1)))
        out.append({"label": label, "start": start, "end": end})
    if not out and n_lines:
        out = [{"label": "Song", "start": 0, "end": n_lines - 1}]
    return out


def _normalize_line_acts(raw: list, n_lines: int) -> dict[str, str]:
    acts: dict[str, str] = {}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        idx = int(item.get("index", item.get("line", -1)))
        act = str(item.get("act", "statement")).lower().strip()
        if 0 <= idx < n_lines and act in _VALID_ACTS:
            acts[str(idx)] = act
    return acts


def _normalize_metaphors(raw: list, n_lines: int) -> list[dict]:
    out = []
    for m in raw or []:
        if not isinstance(m, dict):
            continue
        line = int(m.get("line", m.get("line_index", -1)))
        phrase = str(m.get("phrase", "")).strip()
        if not phrase or line < 0 or line >= n_lines:
            continue
        out.append({
            "phrase": phrase,
            "source": str(m.get("source", "")).strip(),
            "target": str(m.get("target", "")).strip(),
            "line": line,
            "note": str(m.get("note", "")).strip(),
        })
    return out[:12]


def _normalize_imagery(raw: list, n_lines: int) -> dict[str, dict[str, str]]:
    by_line: dict[str, dict[str, str]] = {}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        word = str(item.get("word", "")).lower().strip()
        role = str(item.get("role", "")).lower().strip()
        line = int(item.get("line", item.get("line_index", -1)))
        if not word or role not in _VALID_IMAGERY or line < 0 or line >= n_lines:
            continue
        by_line.setdefault(str(line), {})[word] = role
    return by_line


def _normalize_track_entry(raw: dict, track: dict) -> dict | None:
    tid = int(raw.get("track_id", track.get("id", -1)))
    if tid != track.get("id"):
        return None
    lines = _track_lines(track)
    if not lines:
        return None
    text = "\n".join(lines)
    return {
        "hash": lyrics_hash(text),
        "model": GEMINI_MODEL,
        "summary": str(raw.get("summary", "")).strip(),
        "sections": _normalize_sections(raw.get("sections"), len(lines)),
        "line_acts": _normalize_line_acts(raw.get("lines"), len(lines)),
        "metaphors": _normalize_metaphors(raw.get("metaphors"), len(lines)),
        "imagery": _normalize_imagery(raw.get("imagery"), len(lines)),
    }


def _prompt_for_chunk(md: str, *, chunk_note: str = "") -> str:
    return f"""You are a lyric craft analyst. Read this markdown corpus of song lyrics.

Lyrics break sentences across lines — classify speech acts at the SENTENCE level, then assign that act to every line in the sentence.

Return JSON only:
{{
  "themes": [
    {{
      "name": "short theme title",
      "description": "one sentence",
      "keywords": ["word1", "word2"],
      "track_ids": [1, 2]
    }}
  ],
  "tracks": [
    {{
      "track_id": 1,
      "summary": "one sentence on craft and feel",
      "sections": [{{"label": "Verse 1|Chorus|Bridge|Intro|Outro|Pre-Chorus", "start": 0, "end": 7}}],
      "lines": [{{"index": 0, "act": "statement|question|command|promise|apology|plea|accusation|confession|exclamation"}}],
      "metaphors": [{{"phrase": "from lyrics", "source": "image domain", "target": "stands for", "line": 0, "note": "brief"}}],
      "imagery": [{{"word": "from lyrics", "line": 0, "role": "concrete|abstract|referential"}}]
    }}
  ]
}}

Rules:
- track_id must match headers exactly; include every track in the document
- sections cover all lines without gaps; standard song section names
- lines: one entry per lyric line with sentence-aware acts (continuations inherit the sentence act)
- imagery: notable content words only; referential = you/somebody/thing placeholders
- metaphors: clear metaphors/similes only, max 8 per track
- themes: 3-6 human-readable themes for this corpus chunk{chunk_note}

Corpus:
{md}
"""


def _call_chunk(
    tracks: list[dict],
    dataset_name: str,
    chunk_index: int,
    n_chunks: int,
    *,
    allow_retry: bool = True,
) -> dict | None:
    md = build_corpus_markdown(tracks, dataset_name)
    if not md:
        return None
    note = f" (chunk {chunk_index + 1} of {n_chunks})" if n_chunks > 1 else ""
    prompt = _prompt_for_chunk(md, chunk_note=note)
    raw = _call_gemini(prompt)
    parsed = _extract_json(raw or "")
    if parsed or not allow_retry:
        return parsed
    # Truncated or malformed JSON — one retry with a shorter, stricter prompt
    retry_prompt = prompt + "\n\nIMPORTANT: Prior response was truncated. Return valid JSON only. Omit optional fields if needed; never cut off mid-string."
    raw_retry = _call_gemini(retry_prompt, temperature=0.1)
    return _extract_json(raw_retry or "")


def analyze_corpus(tracks: list[dict], dataset_name: str) -> dict:
    """
    One Gemini call per chunk. Returns:
    {ok, themes, track_data: {track_id: llm_json}, message, chunks}
    """
    chunks = _chunk_tracks(tracks, dataset_name)
    if not chunks:
        return {"ok": False, "themes": [], "track_data": {}, "message": "No lyrics to analyze."}

    all_themes: list[dict] = []
    track_data: dict[int, dict] = {}
    errors: list[str] = []

    for i, chunk in enumerate(chunks):
        parsed = _call_chunk(chunk, dataset_name, i, len(chunks))
        if not parsed:
            errors.append(f"chunk {i + 1} failed")
            continue
        by_id = {t.get("id"): t for t in chunk}
        for th in parsed.get("themes") or []:
            if isinstance(th, dict) and th.get("name"):
                all_themes.append({
                    "name": str(th["name"]).strip(),
                    "description": str(th.get("description", "")).strip(),
                    "keywords": [str(k) for k in (th.get("keywords") or [])[:8]],
                    "track_ids": [int(x) for x in (th.get("track_ids") or []) if str(x).isdigit()],
                    "topic_index": len(all_themes),
                })
        for entry in parsed.get("tracks") or []:
            if not isinstance(entry, dict):
                continue
            tid = entry.get("track_id")
            track = by_id.get(tid) or by_id.get(int(tid) if tid is not None else -1)
            if not track:
                continue
            norm = _normalize_track_entry(entry, track)
            if norm:
                track_data[track["id"]] = norm

    enriched = len(track_data)
    total = sum(1 for t in tracks if _track_lines(t))
    if enriched == 0:
        return {
            "ok": False,
            "themes": [],
            "track_data": {},
            "message": "; ".join(errors) or "Gemini returned no usable data.",
            "chunks": len(chunks),
        }
    return {
        "ok": True,
        "themes": all_themes,
        "track_data": track_data,
        "message": f"Enriched {enriched}/{total} tracks" + (f" ({len(chunks)} chunks)" if len(chunks) > 1 else ""),
        "chunks": len(chunks),
        "partial": enriched < total,
    }


def sections_from_llm(llm: dict, lines: list[str]) -> list[dict]:
    sections = []
    for s in llm.get("sections") or []:
        start = int(s.get("start", 0))
        end = int(s.get("end", start))
        chunk = lines[start : end + 1]
        if chunk:
            sections.append({"label": s.get("label", "Section"), "lines": chunk})
    return sections


def act_for_line(llm: dict | None, line_index: int, fallback: str) -> str:
    if not llm:
        return fallback
    acts = llm.get("line_acts") or {}
    return acts.get(str(line_index), fallback)


def imagery_for_word(llm: dict | None, line_index: int, word: str) -> str | None:
    if not llm:
        return None
    line_map = (llm.get("imagery") or {}).get(str(line_index))
    if not line_map:
        return None
    return line_map.get(word.lower())
