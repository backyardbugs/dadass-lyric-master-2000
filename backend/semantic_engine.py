"""
Map-Reduce Semantic Engine — async Gemini batches with structured JSON output.
Map: 3–4 tracks per batch (speech acts, sections, metaphors, valence 0–100).
Reduce: album themes from track summaries only.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import re
import time
from collections import Counter
from statistics import mean, pstdev
from typing import Any, AsyncIterator

import requests

from backend import db

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BATCH_SIZE = int(os.getenv("SEMANTIC_BATCH_SIZE", "4"))
SEMAPHORE_LIMIT = int(os.getenv("SEMANTIC_CONCURRENCY", "2"))
MIN_REQUEST_GAP = float(os.getenv("SEMANTIC_REQUEST_GAP_SEC", "4.0"))

_VALID_ACTS = frozenset({
    "statement", "question", "command", "promise", "apology",
    "plea", "accusation", "confession", "exclamation",
})
_VALID_IMAGERY = frozenset({"concrete", "abstract", "referential"})

_SPEECH_ACT_ENUM = list(_VALID_ACTS)
_IMAGERY_ENUM = list(_VALID_IMAGERY)

# Gemini responseSchema (OpenAPI 3.0 subset)
MAP_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tracks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "track_id": {"type": "integer"},
                    "summary": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                            },
                            "required": ["label", "start", "end"],
                        },
                    },
                    "lines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "index": {"type": "integer"},
                                "act": {"type": "string", "enum": _SPEECH_ACT_ENUM},
                                "valence": {"type": "integer"},
                            },
                            "required": ["index", "act", "valence"],
                        },
                    },
                    "metaphors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phrase": {"type": "string"},
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "line": {"type": "integer"},
                                "note": {"type": "string"},
                            },
                            "required": ["phrase", "line"],
                        },
                    },
                    "imagery": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "line": {"type": "integer"},
                                "role": {"type": "string", "enum": _IMAGERY_ENUM},
                            },
                            "required": ["word", "line", "role"],
                        },
                    },
                },
                "required": ["track_id", "summary", "sections", "lines"],
            },
        },
    },
    "required": ["tracks"],
}

REDUCE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "themes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "track_ids": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["name", "description", "keywords", "track_ids"],
            },
        },
    },
    "required": ["themes"],
}

_rate_sem = asyncio.Semaphore(SEMAPHORE_LIMIT)
_throttle_lock: asyncio.Lock | None = None
_last_request_at = 0.0


def _get_api_key(byok: str | None = None) -> str | None:
    key = (byok or "").strip()
    if key:
        return key
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None


def is_enabled(byok: str | None = None) -> bool:
    if os.getenv("GEMINI_ENABLED", "1").lower() in ("0", "false", "no"):
        return bool((byok or "").strip())
    return bool(_get_api_key(byok))


def lyrics_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()[:16]


def valence_100_to_scale(v: int) -> float:
    """Convert 0–100 semantic valence to -1..1 dashboard scale."""
    clamped = max(0, min(100, int(v)))
    return round((clamped - 50) / 50, 4)


def _track_lines(track: dict) -> list[str]:
    text = track.get("cleaned_lyrics") or track.get("raw_lyrics") or ""
    return [l.strip() for l in text.split("\n") if l.strip()]


def _build_batch_markdown(batch: list[dict]) -> str:
    parts: list[str] = []
    for t in batch:
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


def _parse_gemini_json_response(data: dict) -> dict | None:
    try:
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        text = parts[0].get("text", "")
        if not text:
            return None
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None


def _gemini_generate(
    prompt: str,
    *,
    api_key: str,
    response_schema: dict[str, Any],
    temperature: float = 0.2,
    timeout: int = 180,
) -> dict | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    }
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
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
            return _parse_gemini_json_response(resp.json())
        except requests.RequestException:
            if attempt >= 3:
                return None
            time.sleep(2 ** attempt)
        except Exception:
            if attempt >= 3:
                return None
            time.sleep(2 ** attempt)
    return None


async def _throttled_gemini(
    prompt: str,
    *,
    api_key: str,
    response_schema: dict[str, Any],
    temperature: float = 0.2,
) -> dict | None:
    global _last_request_at, _throttle_lock
    if _throttle_lock is None:
        _throttle_lock = asyncio.Lock()

    async with _rate_sem:
        async with _throttle_lock:
            now = time.monotonic()
            gap = MIN_REQUEST_GAP + random.uniform(-0.4, 0.4)
            wait = max(0.0, gap - (now - _last_request_at))
            if wait > 0:
                await asyncio.sleep(wait)
            _last_request_at = time.monotonic()
        return await asyncio.to_thread(
            _gemini_generate,
            prompt,
            api_key=api_key,
            response_schema=response_schema,
            temperature=temperature,
        )


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


def _normalize_line_data(raw: list, n_lines: int) -> tuple[dict[str, str], dict[str, int]]:
    acts: dict[str, str] = {}
    valences: dict[str, int] = {}
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        idx = int(item.get("index", item.get("line", -1)))
        if idx < 0 or idx >= n_lines:
            continue
        act = str(item.get("act", "statement")).lower().strip()
        if act in _VALID_ACTS:
            acts[str(idx)] = act
        try:
            v = int(item.get("valence", 50))
            valences[str(idx)] = max(0, min(100, v))
        except (TypeError, ValueError):
            valences[str(idx)] = 50
    return acts, valences


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
    line_list = _track_lines(track)
    if not line_list:
        return None
    text = "\n".join(line_list)
    line_acts, line_valences = _normalize_line_data(raw.get("lines"), len(line_list))
    return {
        "hash": lyrics_hash(text),
        "model": GEMINI_MODEL,
        "summary": str(raw.get("summary", "")).strip(),
        "sections": _normalize_sections(raw.get("sections"), len(line_list)),
        "line_acts": line_acts,
        "line_valences": line_valences,
        "metaphors": _normalize_metaphors(raw.get("metaphors"), len(line_list)),
        "imagery": _normalize_imagery(raw.get("imagery"), len(line_list)),
    }


def _metrics_from_valences(line_valences: dict[str, int], existing: dict | None = None) -> dict:
    metrics = dict(existing or {})
    if not line_valences:
        return metrics
    scaled = [valence_100_to_scale(v) for v in line_valences.values()]
    metrics["valence"] = round(mean(scaled), 4)
    metrics["intensity"] = round(mean(abs(x) for x in scaled), 4)
    metrics["volatility"] = round(pstdev(scaled), 4) if len(scaled) > 1 else 0.0
    return metrics


def _map_prompt(md: str, batch_index: int, n_batches: int) -> str:
    note = f" (batch {batch_index + 1} of {n_batches})" if n_batches > 1 else ""
    return f"""You are a lyric narrative analyst. Analyze each track in this batch{note}.

Lyrics break sentences across lines — classify speech acts at the SENTENCE level, then assign that act to every line in the sentence.

For each line, assign valence 0–100 (0 = darkest/most distressed, 50 = neutral, 100 = brightest/most hopeful).

Rules:
- track_id must match headers exactly; include every track in the document
- sections cover all lines without gaps; use Verse/Chorus/Bridge/Intro/Outro/Pre-Chorus labels
- lines: one entry per lyric line index with act and valence
- imagery: notable content words only; referential = you/somebody/thing placeholders
- metaphors: clear metaphors/similes only, max 6 per track

Tracks:
{md}
"""


def _reduce_prompt(summaries: list[dict], dataset_name: str) -> str:
    lines = [f"- [track_id:{s['track_id']}] {s['title']}: {s['summary']}" for s in summaries]
    body = "\n".join(lines)
    return f"""You are a narrative analyst. Given these per-track summaries from the album/playlist "{dataset_name}", identify 3–6 recurring album-wide themes.

Return themes that group multiple tracks when possible. track_ids must reference the ids below.

Track summaries:
{body}
"""


async def _map_batch(
    batch: list[dict],
    batch_index: int,
    n_batches: int,
    api_key: str,
) -> dict[int, dict]:
    md = _build_batch_markdown(batch)
    if not md:
        return {}
    prompt = _map_prompt(md, batch_index, n_batches)
    parsed = await _throttled_gemini(
        prompt,
        api_key=api_key,
        response_schema=MAP_RESPONSE_SCHEMA,
    )
    if not parsed:
        return {}
    by_id = {t.get("id"): t for t in batch}
    out: dict[int, dict] = {}
    for entry in parsed.get("tracks") or []:
        if not isinstance(entry, dict):
            continue
        tid = entry.get("track_id")
        track = by_id.get(tid) or by_id.get(int(tid) if tid is not None else -1)
        if not track:
            continue
        norm = _normalize_track_entry(entry, track)
        if norm:
            out[track["id"]] = norm
    return out


async def _reduce_themes(
    track_data: dict[int, dict],
    tracks: list[dict],
    dataset_name: str,
    api_key: str,
) -> list[dict]:
    by_id = {t["id"]: t for t in tracks}
    summaries = []
    for tid, data in track_data.items():
        t = by_id.get(tid)
        if not t or not data.get("summary"):
            continue
        summaries.append({
            "track_id": tid,
            "title": t.get("title") or "Unknown",
            "summary": data["summary"],
        })
    if not summaries:
        return []
    prompt = _reduce_prompt(summaries, dataset_name)
    parsed = await _throttled_gemini(
        prompt,
        api_key=api_key,
        response_schema=REDUCE_RESPONSE_SCHEMA,
        temperature=0.15,
    )
    if not parsed:
        return []
    themes = []
    for i, th in enumerate(parsed.get("themes") or []):
        if not isinstance(th, dict) or not th.get("name"):
            continue
        themes.append({
            "name": str(th["name"]).strip(),
            "description": str(th.get("description", "")).strip(),
            "keywords": [str(k) for k in (th.get("keywords") or [])[:8]],
            "track_ids": [int(x) for x in (th.get("track_ids") or []) if str(x).isdigit()],
            "topic_index": i,
        })
    return themes


def _chunk_batches(tracks: list[dict]) -> list[list[dict]]:
    with_lyrics = [t for t in tracks if _track_lines(t)]
    batches: list[list[dict]] = []
    for i in range(0, len(with_lyrics), BATCH_SIZE):
        batches.append(with_lyrics[i : i + BATCH_SIZE])
    return batches


async def _persist_track_semantic(track_id: int, semantic: dict, existing_metrics: dict | None) -> None:
    await asyncio.to_thread(db.update_track_llm, track_id, semantic)
    merged = _metrics_from_valences(semantic.get("line_valences") or {}, existing_metrics)
    if merged:
        await asyncio.to_thread(db.update_track_metrics, track_id, merged)


async def run_semantic_engine_stream(
    *,
    tracks: list[dict],
    dataset_name: str,
    run_id: int,
    playlist_pk: int,
    api_key: str | None = None,
) -> AsyncIterator[dict]:
    """
    Async generator of progress dicts for SSE.
    Writes track semantic JSON and themes via short-lived DB connections (to_thread).
    """
    key = _get_api_key(api_key)
    if not key:
        yield {
            "status": "Semantic engine skipped (no API key).",
            "progress": 85,
            "phase": "semantic",
            "skipped": True,
        }
        return

    batches = _chunk_batches(tracks)
    if not batches:
        yield {"status": "No lyrics for semantic analysis.", "progress": 85, "phase": "semantic", "skipped": True}
        return

    n_batches = len(batches)
    await asyncio.to_thread(
        db.update_run_llm_status,
        run_id,
        {
            "ok": False,
            "status": "running",
            "message": "Semantic engine map pass in progress…",
            "tracks_enriched": 0,
            "batches_total": n_batches,
            "batches_done": 0,
        },
    )

    track_data: dict[int, dict] = {}
    errors: list[str] = []
    metrics_by_id = {t["id"]: t.get("metrics") or {} for t in tracks}

    tasks = [
        asyncio.create_task(_map_batch(batch, i, n_batches, key))
        for i, batch in enumerate(batches)
    ]
    done_count = 0
    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            done_count += 1
            if isinstance(result, dict) and result:
                for tid, sem in result.items():
                    track_data[tid] = sem
                    await _persist_track_semantic(tid, sem, metrics_by_id.get(tid))
            elif isinstance(result, dict):
                errors.append(f"batch {done_count} empty")
            yield {
                "status": f"Mapping semantic framework (Batch {done_count}/{n_batches})…",
                "progress": 55 + int(30 * done_count / n_batches),
                "phase": "semantic",
                "batch": done_count,
                "batches_total": n_batches,
                "tracks_enriched": len(track_data),
            }
            await asyncio.to_thread(
                db.update_run_llm_status,
                run_id,
                {
                    "ok": False,
                    "status": "running",
                    "message": f"Map pass {done_count}/{n_batches}",
                    "tracks_enriched": len(track_data),
                    "batches_total": n_batches,
                    "batches_done": done_count,
                },
            )
        except Exception as exc:
            errors.append(str(exc)[:80])
            done_count += 1

    if not track_data:
        status = {
            "ok": False,
            "status": "failed",
            "message": "; ".join(errors) or "Semantic map pass returned no data.",
            "tracks_enriched": 0,
        }
        await asyncio.to_thread(db.update_run_llm_status, run_id, status)
        yield {"status": "Semantic map pass failed.", "progress": 85, "phase": "semantic", "error": status["message"]}
        return

    yield {
        "status": "Synthesizing album themes…",
        "progress": 90,
        "phase": "semantic",
        "tracks_enriched": len(track_data),
    }

    themes = await _reduce_themes(track_data, tracks, dataset_name, key)
    if themes:
        await asyncio.to_thread(db.update_run_llm_themes, run_id, themes)

    enriched = len(track_data)
    total = sum(1 for t in tracks if _track_lines(t))
    final_status = {
        "ok": True,
        "status": "complete",
        "message": f"Semantic engine enriched {enriched}/{total} tracks.",
        "tracks_enriched": enriched,
        "themes_count": len(themes),
        "partial": enriched < total,
    }
    await asyncio.to_thread(db.update_run_llm_status, run_id, final_status)

    yield {
        "status": f"Semantic analysis complete ({enriched}/{total} tracks, {len(themes)} themes).",
        "progress": 95,
        "phase": "semantic",
        "tracks_enriched": enriched,
        "themes_count": len(themes),
    }


def sections_from_semantic(semantic: dict, line_list: list[str]) -> list[dict]:
    sections = []
    for s in semantic.get("sections") or []:
        start = int(s.get("start", 0))
        end = int(s.get("end", start))
        chunk = line_list[start : end + 1]
        if chunk:
            sections.append({"label": s.get("label", "Section"), "lines": chunk})
    return sections


def act_for_line(semantic: dict | None, line_index: int, fallback: str = "statement") -> str:
    if not semantic:
        return fallback
    return (semantic.get("line_acts") or {}).get(str(line_index), fallback)


def valence_for_line(semantic: dict | None, line_index: int) -> float:
    if not semantic:
        return 0.0
    raw = (semantic.get("line_valences") or {}).get(str(line_index))
    if raw is None:
        return 0.0
    return valence_100_to_scale(int(raw))


def imagery_for_word(semantic: dict | None, line_index: int, word: str) -> str | None:
    if not semantic:
        return None
    line_map = (semantic.get("imagery") or {}).get(str(line_index))
    if not line_map:
        return None
    return line_map.get(word.lower())


def corpus_speech_acts(tracks: list[dict], max_examples: int = 40) -> dict:
    """Aggregate speech acts from stored semantic line_acts across the corpus."""
    counts: Counter = Counter()
    examples: dict[str, list[dict]] = {}
    total = 0
    for t in tracks:
        sem = db.get_track_llm(t["id"]) or {}
        acts = sem.get("line_acts") or {}
        text = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
        line_list = [l.strip() for l in text.split("\n") if l.strip()]
        seen: set[str] = set()
        for idx_str, act in acts.items():
            try:
                idx = int(idx_str)
            except ValueError:
                continue
            if idx < 0 or idx >= len(line_list):
                continue
            line = line_list[idx]
            total += 1
            counts[act] += 1
            key = f"{act}:{line.lower()}"
            if act != "statement" and key not in seen:
                seen.add(key)
                bucket = examples.setdefault(act, [])
                if len(bucket) < max_examples:
                    bucket.append({"line": line, "title": t.get("title") or ""})
    return {
        "total_lines": total,
        "acts": [
            {
                "act": act,
                "count": counts[act],
                "share": round(counts[act] / max(1, total), 4),
                "examples": examples.get(act, []),
            }
            for act, _ in counts.most_common()
        ],
    }


# Back-compat aliases (llm.py callers)
sections_from_llm = sections_from_semantic
is_available = is_enabled
