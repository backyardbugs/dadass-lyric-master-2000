"""
Gemini-powered lyric understanding for Phase 3:
- Corpus themes with human-readable names
- Per-track section labels, sentence-aware speech acts, metaphors, imagery roles
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

_VALID_ACTS = {
    "statement", "question", "command", "promise", "apology",
    "plea", "accusation", "confession", "exclamation",
}
_VALID_IMAGERY = {"concrete", "abstract", "referential"}


def is_available() -> bool:
    return bool(GEMINI_API_KEY)


def lyrics_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()[:16]


def _extract_json(text: str) -> dict | list | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def _call_gemini(prompt: str, *, temperature: float = 0.2, max_retries: int = 3) -> str | None:
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
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=90)
            if resp.status_code == 429:
                wait = min(45, 2 ** attempt * 5)
                retry = resp.json().get("error", {}).get("message", "")
                m = re.search(r"retry in ([0-9.]+)s", retry, re.I)
                if m:
                    wait = max(wait, float(m.group(1)) + 1)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return parts[0].get("text") if parts else None
        except Exception:
            if attempt + 1 >= max_retries:
                return None
            time.sleep(2 ** attempt)
    return None


def _numbered_lines(lines: list[str]) -> str:
    return "\n".join(f"{i}: {line}" for i, line in enumerate(lines))


def _normalize_sections(raw: list, n_lines: int) -> list[dict]:
    out = []
    for s in raw or []:
        if not isinstance(s, dict):
            continue
        label = str(s.get("label") or "Section").strip() or "Section"
        start = int(s.get("start", s.get("start_line", 0)))
        end = int(s.get("end", s.get("end_line", start)))
        start = max(0, min(start, n_lines - 1 if n_lines else 0))
        end = max(start, min(end, n_lines - 1 if n_lines else 0))
        out.append({"label": label, "start": start, "end": end})
    if not out and n_lines:
        out = [{"label": "Song", "start": 0, "end": n_lines - 1}]
    return out


def _normalize_line_acts(raw: list, n_lines: int) -> dict[int, str]:
    acts: dict[int, str] = {}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        idx = int(item.get("index", item.get("line", -1)))
        act = str(item.get("act", "statement")).lower().strip()
        if 0 <= idx < n_lines and act in _VALID_ACTS:
            acts[idx] = act
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
    return out[:20]


def _normalize_imagery(raw: list, n_lines: int) -> dict[int, dict[str, str]]:
    """line_index -> {word: role}"""
    by_line: dict[int, dict[str, str]] = {}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        word = str(item.get("word", "")).lower().strip()
        role = str(item.get("role", "")).lower().strip()
        line = int(item.get("line", item.get("line_index", -1)))
        if not word or role not in _VALID_IMAGERY or line < 0 or line >= n_lines:
            continue
        by_line.setdefault(line, {})[word] = role
    return by_line


def analyze_track(title: str, artist: str, lines: list[str]) -> dict | None:
    """Return LLM annotations for one song, or None on failure."""
    if not lines or not is_available():
        return None
    text_hash = lyrics_hash("\n".join(lines))
    prompt = f"""You are a lyric analyst helping a songwriter study craft. Analyze this song's lyrics.

Song: "{title}" by {artist}
Lines are numbered. Lyrics often break one sentence across multiple lines — classify speech acts at the SENTENCE level, then assign that act to every line in the sentence.

Return JSON only:
{{
  "summary": "one sentence on this song's lyrical craft and feel",
  "sections": [{{"label": "Verse 1|Chorus|Bridge|Intro|Outro|Pre-Chorus", "start": 0, "end": 7}}],
  "lines": [{{"index": 0, "act": "statement|question|command|promise|apology|plea|accusation|confession|exclamation", "sentence_id": 0}}],
  "metaphors": [{{"phrase": "exact phrase from lyrics", "source": "literal image/domain", "target": "what it stands for", "line": 0, "note": "brief why"}}],
  "imagery": [{{"word": "word from lyrics", "line": 0, "role": "concrete|abstract|referential"}}]
}}

Rules:
- sections must cover all lines without gaps or overlaps; use standard song section names
- for speech acts: lines that continue a previous sentence inherit its act (not a new command/question)
- imagery roles: concrete = touchable/visible image; abstract = idea/emotion; referential = pronouns/generic placeholders (you, somebody, thing)
- only include clear metaphors/similes, not every line
- imagery: include notable content words, especially ones that could be misread in isolation

Lyrics:
{_numbered_lines(lines[:120])}
"""
    raw = _call_gemini(prompt)
    parsed = _extract_json(raw or "")
    if not isinstance(parsed, dict):
        return None

    n = len(lines)
    sections = _normalize_sections(parsed.get("sections"), n)
    line_acts = _normalize_line_acts(parsed.get("lines"), n)
    metaphors = _normalize_metaphors(parsed.get("metaphors"), n)
    imagery = _normalize_imagery(parsed.get("imagery"), n)

    return {
        "hash": text_hash,
        "model": GEMINI_MODEL,
        "summary": str(parsed.get("summary", "")).strip(),
        "sections": sections,
        "line_acts": {str(k): v for k, v in line_acts.items()},
        "metaphors": metaphors,
        "imagery": {str(k): v for k, v in imagery.items()},
    }


def analyze_corpus_themes(tracks: list[dict], *, max_tracks: int = 30) -> list[dict] | None:
    """Human-readable themes across a lyric corpus."""
    if not is_available():
        return None
    samples = []
    for t in tracks:
        text = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
        if not text.strip():
            continue
        excerpt = "\n".join(l.strip() for l in text.split("\n") if l.strip())[:800]
        samples.append({
            "title": t.get("title") or "",
            "artist": t.get("artist") or "",
            "excerpt": excerpt,
            "id": t.get("id"),
        })
        if len(samples) >= max_tracks:
            break
    if len(samples) < 2:
        return None

    catalog = json.dumps(samples, ensure_ascii=False)
    prompt = f"""You are a lyric analyst. Read these song excerpts from one dataset and identify 4-6 recurring THEMES (not just word lists).

Return JSON only:
{{
  "themes": [
    {{
      "name": "short human theme name",
      "description": "one sentence explaining what the writer keeps returning to",
      "keywords": ["word1", "word2", "word3"],
      "track_titles": ["Song Title 1", "Song Title 2"]
    }}
  ]
}}

Rules:
- theme names should read like chapter titles, not random keywords
- track_titles must come from the input list
- keywords are supporting evidence, not the theme name itself

Songs:
{catalog}
"""
    raw = _call_gemini(prompt, temperature=0.3)
    parsed = _extract_json(raw or "")
    if not isinstance(parsed, dict):
        return None
    themes = []
    title_to_id = {(t.get("title") or "").lower(): t.get("id") for t in tracks}
    for i, th in enumerate(parsed.get("themes") or []):
        if not isinstance(th, dict):
            continue
        name = str(th.get("name", "")).strip()
        if not name:
            continue
        track_ids = []
        for title in th.get("track_titles") or []:
            tid = title_to_id.get(str(title).lower())
            if tid is not None:
                track_ids.append(tid)
        themes.append({
            "name": name,
            "description": str(th.get("description", "")).strip(),
            "keywords": [str(k) for k in (th.get("keywords") or [])[:8]],
            "track_ids": track_ids,
            "topic_index": i,
        })
    return themes or None


def sections_from_llm(llm: dict, lines: list[str]) -> list[dict]:
    """Build section objects with line text from stored LLM section ranges."""
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
    return acts.get(str(line_index), acts.get(line_index, fallback))


def imagery_for_word(llm: dict | None, line_index: int, word: str) -> str | None:
    if not llm:
        return None
    line_map = (llm.get("imagery") or {}).get(str(line_index)) or (llm.get("imagery") or {}).get(line_index)
    if not line_map:
        return None
    return line_map.get(word.lower())
