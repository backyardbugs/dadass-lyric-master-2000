"""
SSE streaming pipeline: fetch lyrics + deterministic metrics in one pass.
Phase 2 will plug the Semantic Engine Map-Reduce into this stream.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator

from backend.cleaner import clean_lyrics
from backend.fetch import extract_spotify_ref, fetch_source
from backend.metrics import run_deterministic_analysis
from backend import semantic_engine as semantic_module
from backend import db


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def _heartbeat() -> str:
    return ": keepalive\n\n"


async def _fetch_and_store(
    spotify_url: str,
    spotify_token: str | None,
) -> tuple[str, str, int, int]:
    """Fetch Spotify + lyrics and persist. Returns (source_id, source_name, playlist_pk, with_lyrics)."""
    ref = extract_spotify_ref(spotify_url)
    if not ref:
        raise ValueError("Invalid Spotify URL. Paste a playlist, album, or artist link.")

    try:
        known_lyrics = db.get_known_lyrics()
    except Exception:
        known_lyrics = {}

    kind, source_id, source_name, source_image, raw_tracks = await asyncio.to_thread(
        fetch_source,
        spotify_url,
        spotify_access_token=spotify_token,
        known_lyrics=known_lyrics,
    )

    if not raw_tracks:
        raise ValueError(f"{kind.capitalize()} is empty or could not be read.")

    for t in raw_tracks:
        t["raw_lyrics"] = t.get("lyrics")
        t["cleaned_lyrics"] = clean_lyrics(t.get("lyrics")) if t.get("lyrics") else None

    playlist_pk = await asyncio.to_thread(
        db.insert_playlist, source_id, name=source_name, image_url=source_image
    )
    await asyncio.to_thread(db.insert_tracks, playlist_pk, raw_tracks)
    with_lyrics = sum(1 for t in raw_tracks if t.get("lyrics"))
    return source_id, source_name or "", playlist_pk, with_lyrics


async def analyze_dataset_stream(
    *,
    spotify_url: str | None = None,
    playlist_id: str | None = None,
    spotify_token: str | None = None,
    gemini_api_key: str | None = None,
) -> AsyncIterator[str]:
    """
    Yield SSE events for the unified analyze-dataset pipeline.
    BYOK key is accepted but not used until Phase 2 Semantic Engine.
    """
    last_heartbeat = time.monotonic()

    def maybe_heartbeat() -> str | None:
        nonlocal last_heartbeat
        now = time.monotonic()
        if now - last_heartbeat >= 15:
            last_heartbeat = now
            return _heartbeat()
        return None

    try:
        yield _sse({"status": "Connecting to Spotify…", "progress": 2, "phase": "fetch"})

        if spotify_url and spotify_url.strip():
            yield _sse({"status": "Fetching tracklist…", "progress": 8, "phase": "fetch"})
            source_id, source_name, playlist_pk, with_lyrics = await _fetch_and_store(
                spotify_url.strip(), spotify_token
            )
            tracks = await asyncio.to_thread(db.get_tracks, playlist_pk)
            track_count = len(tracks)
            yield _sse({
                "status": f"Fetched {track_count} tracks ({with_lyrics} with lyrics)",
                "progress": 35,
                "phase": "fetch",
                "playlist_id": source_id,
                "playlist_name": source_name,
                "track_count": track_count,
            })
        elif playlist_id and playlist_id.strip():
            playlist_pk = await asyncio.to_thread(db.resolve_playlist_pk, playlist_id.strip())
            if playlist_pk is None:
                raise ValueError("Dataset not found. Fetch a Spotify URL first.")
            info = await asyncio.to_thread(db.get_playlist_info, playlist_pk)
            source_id = (info or {}).get("playlist_id") or playlist_id.strip()
            source_name = (info or {}).get("name") or ""
            tracks = await asyncio.to_thread(db.get_tracks, playlist_pk)
            track_count = len(tracks)
            if not tracks:
                raise ValueError("Dataset has no tracks.")
            yield _sse({
                "status": f"Using cached dataset ({track_count} tracks)",
                "progress": 30,
                "phase": "fetch",
                "playlist_id": source_id,
                "playlist_name": source_name,
                "track_count": track_count,
            })
        else:
            raise ValueError("Provide spotify_url or playlist_id.")

        hb = maybe_heartbeat()
        if hb:
            yield hb

        yield _sse({"status": "Running deterministic metrics…", "progress": 50, "phase": "metrics"})
        run_id = await asyncio.to_thread(run_deterministic_analysis, playlist_pk)

        yield _sse({
            "status": "Metrics complete. Starting semantic engine…",
            "progress": 55,
            "phase": "metrics",
            "run_id": run_id,
        })

        dataset_name = source_name or "Lyrics dataset"
        tracks = await asyncio.to_thread(db.get_tracks, playlist_pk)

        if semantic_module.is_enabled(gemini_api_key):
            async for event in semantic_module.run_semantic_engine_stream(
                tracks=tracks,
                dataset_name=dataset_name,
                run_id=run_id,
                playlist_pk=playlist_pk,
                api_key=gemini_api_key,
            ):
                hb = maybe_heartbeat()
                if hb:
                    yield hb
                yield _sse(event)
        else:
            yield _sse({
                "status": "Semantic engine skipped (set GEMINI_API_KEY or pass BYOK).",
                "progress": 85,
                "phase": "semantic",
                "skipped": True,
            })

        yield _sse({
            "status": "complete",
            "progress": 100,
            "phase": "done",
            "playlist_id": source_id,
            "playlist_name": source_name,
            "track_count": track_count,
            "run_id": run_id,
        })

    except ValueError as exc:
        yield _sse({"status": "error", "progress": 0, "message": str(exc)})
    except RuntimeError as exc:
        msg = str(exc)
        if "GENIUS" in msg or "SPOTIPY" in msg:
            yield _sse({"status": "error", "progress": 0, "message": "Check API keys in .env (Genius and Spotify)."})
        else:
            yield _sse({"status": "error", "progress": 0, "message": msg[:200]})
    except Exception as exc:
        msg = str(exc).strip() or "Analysis failed."
        msg_lower = msg.lower()
        if "rate" in msg_lower or "429" in msg_lower:
            yield _sse({"status": "error", "progress": 0, "message": "Rate limit hit. Wait a minute and try again."})
        elif "401" in msg or "unauthorized" in msg_lower:
            yield _sse({"status": "error", "progress": 0, "message": "Spotify authentication required. Log in with Spotify."})
        elif "404" in msg or "not found" in msg_lower:
            yield _sse({"status": "error", "progress": 0, "message": "Spotify resource not found. Check the URL."})
        else:
            yield _sse({"status": "error", "progress": 0, "message": msg.split("\n")[0][:200]})
