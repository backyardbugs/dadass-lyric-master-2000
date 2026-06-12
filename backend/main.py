"""
FastAPI app for Dad Ass Lyric Analyzer 3000.
Run: uvicorn backend.main:app --reload
"""
from __future__ import annotations

import secrets
import time
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from spotipy.oauth2 import SpotifyOAuth

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from spotipy import Spotify

from backend.cleaner import clean_lyrics
from backend.fetch import _TokenAuth, extract_spotify_ref, fetch_source
from backend.analyze import tokenize_lyrics, top_n_words, build_word_contexts
from backend.nlp import (
    GENERIC_INDEFINITES,
    VOCALIZATIONS,
    _corpus_counts,
    _stopwords,
    classify_speech_act,
    concreteness_for,
    corpus_hooks,
    corpus_rhyme_pairs,
    end_rhyme_scheme,
    line_valence,
    pov_profile,
    run_topics,
    section_contrast,
    signature_words,
    song_structure,
    speech_acts_profile,
    top_n_by_pos,
    track_metrics,
)
from backend import db
from backend import llm as llm_module

app = FastAPI(title="Dad Ass Lyric Analyzer 3000 API", version="0.1.0")

import os
import re
_cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://frontend-woad-xi-34.vercel.app",
]
if os.getenv("CORS_ORIGINS"):
    _cors_origins.extend(o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip())
# Allow any Vercel deployment (same project)
_cors_origin_regex = re.compile(r"^https://(frontend-[a-z0-9-]+-backyardbugs-projects\.vercel\.app|.*\.vercel\.app)$")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex.pattern,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# One-time codes for token exchange (works when cross-site cookies are blocked)
_spotify_code_store: dict[str, tuple[str, float]] = {}
_CODE_TTL_SEC = 300


def _get_spotify_token_from_request(request: Request) -> str | None:
    """Token from cookie (same-site or when third-party cookies allowed) or Authorization header."""
    token = request.cookies.get("spotify_token")
    if token:
        return token
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:].strip() or None
    return None


@app.on_event("startup")
def startup():
    db.init_db()


class FetchRequest(BaseModel):
    playlist_url: str


class FetchResponse(BaseModel):
    ok: bool
    message: str
    track_count: int
    playlist_id: str | None = None


def _get_spotify_oauth():
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    if not redirect_uri:
        raise RuntimeError(
            "Set SPOTIFY_REDIRECT_URI in env. Use the frontend callback URL so Spotify sends users to the frontend, e.g. https://your-frontend.vercel.app/api/auth/spotify/callback"
        )
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID", ""),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET", ""),
        redirect_uri=redirect_uri,
        scope="playlist-read-private playlist-read-collaborative",
    )


@app.get("/api/auth/spotify")
def api_auth_spotify():
    """Redirect user to Spotify to authorize playlist access."""
    oauth = _get_spotify_oauth()
    auth_url = oauth.get_authorize_url(state="lyric_analyzer")
    return RedirectResponse(url=auth_url)


@app.get("/api/auth/spotify/callback")
def api_auth_spotify_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    """Exchange code for token, set cookie, redirect to frontend."""
    frontend_url = os.getenv("FRONTEND_URL", "https://frontend-woad-xi-34.vercel.app")
    if error or not code:
        return RedirectResponse(url=frontend_url + "?spotify=auth_denied")
    try:
        oauth = _get_spotify_oauth()
        token_info = oauth.get_access_token(code)
        if isinstance(token_info, dict):
            access_token = token_info.get("access_token")
        else:
            access_token = getattr(token_info, "access_token", None) or str(token_info)
        if not access_token:
            return RedirectResponse(url=frontend_url + "?spotify=no_token")
    except Exception:
        return RedirectResponse(url=frontend_url + "?spotify=exchange_failed")
    # Pass token in query so frontend gets it (fragments are often stripped on redirect).
    # Do not log redirect_url. Frontend clears the URL immediately after reading.
    redirect_url = frontend_url + "?spotify=ok&token=" + quote(access_token, safe="")
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="spotify_token",
        value=access_token,
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return response


def _clean_expired_codes():
    now = time.time()
    expired = [k for k, (_, exp) in _spotify_code_store.items() if exp <= now]
    for k in expired:
        _spotify_code_store.pop(k, None)


@app.get("/api/auth/exchange")
def api_auth_exchange(code: str | None = None):
    """Exchange one-time code for access token (for when cross-site cookies are blocked)."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    _clean_expired_codes()
    now = time.time()
    if code in _spotify_code_store:
        token, expiry = _spotify_code_store.pop(code)
        if expiry > now:
            return {"access_token": token}
    raise HTTPException(status_code=400, detail="Invalid or expired code")


def _spotify_token_valid(token: str) -> bool:
    """Return True if the token is valid (not expired)."""
    if not token:
        return False
    try:
        sp = Spotify(auth_manager=_TokenAuth(token))
        sp.current_user()
        return True
    except Exception:
        return False


@app.get("/api/auth/status")
def api_auth_status(request: Request):
    """Return whether user has a valid Spotify token (for playlist access)."""
    token = _get_spotify_token_from_request(request)
    return {"spotify": _spotify_token_valid(token)}


@app.post("/api/fetch", response_model=FetchResponse)
def api_fetch(body: FetchRequest, request: Request):
    """Fetch a playlist, album, or artist from Spotify plus lyrics; clean and store in DB. Uses Spotify OAuth token if present."""
    ref = extract_spotify_ref(body.playlist_url)
    if not ref:
        raise HTTPException(status_code=400, detail="Invalid Spotify URL. Paste a playlist, album, or artist link.")
    kind, source_id = ref
    spotify_token = _get_spotify_token_from_request(request)
    try:
        known_lyrics = db.get_known_lyrics()
    except Exception:
        known_lyrics = {}
    try:
        kind, source_id, source_name, source_image, raw_tracks = fetch_source(
            body.playlist_url, spotify_access_token=spotify_token, known_lyrics=known_lyrics
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        msg = str(e)
        if "GENIUS" in msg or "SPOTIPY" in msg:
            raise HTTPException(status_code=500, detail="Check your API keys in .env (Genius and Spotify).")
        raise HTTPException(status_code=500, detail=msg)
    except Exception as e:
        msg = str(e).strip()
        msg_lower = msg.lower()
        if "rate" in msg_lower or "429" in msg_lower:
            raise HTTPException(status_code=429, detail="Rate limit hit. Wait a minute and try again.")
        if "timeout" in msg_lower or "timed out" in msg_lower:
            raise HTTPException(status_code=504, detail="Request timed out. Try again.")
        if "401" in msg or "unauthorized" in msg_lower or "invalid" in msg_lower and "token" in msg_lower:
            # Spotify returns 401 "Valid user authentication required" when reading
            # playlists with an app-only token — that means "log in", not "bad keys".
            if "user authentication required" in msg_lower or not spotify_token:
                raise HTTPException(
                    status_code=401,
                    detail="Log in with Spotify first (Spotify requires this to read playlists). Click “Log in with Spotify” above.",
                )
            raise HTTPException(
                status_code=401,
                detail="Your Spotify session expired. Click “Log in with Spotify” again.",
            )
        if "404" in msg or "not found" in msg_lower:
            # Spotify-generated playlists (Made For You, Daily Mix, editorial) start with
            # 37i9dQZF and have been blocked from the Web API since Nov 2024 — they 404 for everyone.
            if kind == "playlist" and source_id.startswith("37i9dQZF"):
                raise HTTPException(
                    status_code=404,
                    detail="This is a Spotify-made playlist (Made For You / Daily Mix / editorial). Spotify blocks these from its API, so they can't be fetched. Use a playlist created by a person — e.g. one of your own.",
                )
            raise HTTPException(status_code=404, detail=f"{kind.capitalize()} not found. Check the URL and that it is public.")
        if "403" in msg or "forbidden" in msg_lower:
            if not spotify_token:
                raise HTTPException(
                    status_code=401,
                    detail="Log in with Spotify first (Spotify requires this to read playlists). Click “Log in with Spotify” above.",
                )
            raise HTTPException(
                status_code=403,
                detail="Playlist is private or access denied. In Spotify, right‑click the playlist → Make Public, then try again.",
            )
        # Surface the real error (first line, no secrets) so user can debug
        detail = msg.split("\n")[0][:200] if msg else "Fetch failed."
        raise HTTPException(status_code=500, detail=detail)
    if not raw_tracks:
        raise HTTPException(status_code=400, detail=f"{kind.capitalize()} is empty or could not be read.")
    # Clean lyrics and add cleaned_lyrics
    for t in raw_tracks:
        t["raw_lyrics"] = t.get("lyrics")
        t["cleaned_lyrics"] = clean_lyrics(t.get("lyrics")) if t.get("lyrics") else None
    playlist_pk = db.insert_playlist(source_id, name=source_name, image_url=source_image)
    db.insert_tracks(playlist_pk, raw_tracks)
    with_lyrics = sum(1 for t in raw_tracks if t.get("lyrics"))
    label = f" from {source_name}" if source_name else ""
    return FetchResponse(
        ok=True,
        message=f"Fetched {len(raw_tracks)} tracks{label} ({with_lyrics} with lyrics).",
        track_count=len(raw_tracks),
        playlist_id=source_id,
    )


class AnalyzeResponse(BaseModel):
    ok: bool
    message: str
    top_words: list[dict]
    run_id: int


@app.post("/api/analyze", response_model=AnalyzeResponse)
def api_analyze():
    """Run word frequency, sentiment, POS, topic modeling on latest playlist and store results."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        raise HTTPException(status_code=400, detail="No playlist data. Run fetch first.")
    tracks = db.get_tracks(playlist_pk)
    if not tracks:
        raise HTTPException(status_code=400, detail="No tracks found.")
    text_key = "cleaned_lyrics"
    tokens = tokenize_lyrics(tracks, text_key=text_key)
    if not tokens:
        text_key = "raw_lyrics"
        tokens = tokenize_lyrics(tracks, text_key=text_key)
    if not tokens:
        raise HTTPException(status_code=400, detail="No lyrics to analyze. Fetch a playlist with lyrics first.")
    top50 = top_n_words(tokens, n=50)
    word_contexts = build_word_contexts(tracks, text_key=text_key)
    if not word_contexts:
        word_contexts = build_word_contexts(tracks, text_key="raw_lyrics")

    run_id = db.insert_analysis_run(playlist_pk)
    db.delete_word_frequencies_for_run(run_id)
    db.insert_word_frequencies(run_id, top50, pos=None)
    db.insert_word_contexts(run_id, word_contexts)

    try:
        for t in tracks:
            raw = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
            metrics = track_metrics(raw)
            db.update_track_metrics(t["id"], metrics)
    except Exception:
        pass

    try:
        by_pos = top_n_by_pos(tracks, text_key=text_key, n=500)
        for pos_name, pairs in by_pos.items():
            db.insert_word_frequencies(run_id, pairs, pos=pos_name)
    except Exception:
        pass

    try:
        topic_labels, per_track_weights, doc_track_ids = run_topics(tracks, text_key=text_key, n_topics=6)
        if topic_labels and per_track_weights and doc_track_ids:
            topic_ids = db.insert_topics(run_id, topic_labels)
            for topic_idx, topic_id in enumerate(topic_ids):
                weights = [(doc_track_ids[i], per_track_weights[i][topic_idx][1]) for i in range(len(per_track_weights))]
                db.insert_track_topics(run_id, topic_id, weights)
    except Exception:
        pass

    # LLM corpus themes (Gemini) — human-readable theme names
    if llm_module.is_available():
        try:
            themes = llm_module.analyze_corpus_themes(tracks)
            if themes:
                db.update_run_llm_themes(run_id, themes)
        except Exception:
            pass

    return AnalyzeResponse(
        ok=True,
        message="Analysis complete.",
        top_words=[{"word": w, "count": c} for w, c in top50],
        run_id=run_id,
    )


class StatusResponse(BaseModel):
    has_data: bool
    track_count: int
    last_analyzed: str | None
    playlist_name: str | None = None
    image_url: str | None = None
    llm_available: bool = False


@app.get("/api/status", response_model=StatusResponse)
def api_status():
    """Return whether we have playlist data and last analysis time."""
    info = db.get_playlist_info()
    if not info:
        return StatusResponse(has_data=False, track_count=0, last_analyzed=None)
    run_id = db.get_latest_run_id(info["id"])
    last_analyzed = None
    if run_id:
        conn = db.get_connection()
        try:
            row = conn.execute("SELECT run_at FROM analysis_run WHERE id = ?", (run_id,)).fetchone()
            if row:
                last_analyzed = row[0]
        finally:
            conn.close()
    return StatusResponse(
        has_data=True,
        track_count=info["track_count"],
        last_analyzed=last_analyzed,
        playlist_name=info.get("name") or None,
        image_url=info.get("image_url") or None,
        llm_available=llm_module.is_available(),
    )


@app.get("/api/top-words")
def api_top_words(pos: str | None = None, limit: int = 100):
    """Return top words from latest analysis run. pos: null (overall), noun, verb, adj."""
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"top_words": [], "run_id": None}
    conn = db.get_connection()
    try:
        if pos:
            rows = conn.execute(
                "SELECT word, count FROM word_frequency WHERE run_id = ? AND pos = ? ORDER BY count DESC LIMIT ?",
                (run_id, pos, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT word, count FROM word_frequency WHERE run_id = ? AND (pos IS NULL OR pos = '') ORDER BY count DESC LIMIT ?",
                (run_id, limit),
            ).fetchall()
        top_words = [{"word": r[0], "count": r[1]} for r in rows]
        return {"top_words": top_words, "run_id": run_id}
    finally:
        conn.close()


@app.get("/api/sentiment/heatmap")
def api_sentiment_heatmap():
    """Per-track tone metrics in track order: valence (-1..1, dark to bright),
    intensity (0..1, how emotionally charged), volatility (line-to-line mood swing)."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"tracks": []}
    tracks = db.get_tracks(playlist_pk)
    out = []
    for i, t in enumerate(tracks):
        m = t.get("metrics") or {}
        out.append({
            "track_index": i,
            "title": t["title"],
            "artist": t["artist"],
            "valence": m.get("valence", 0),
            "intensity": m.get("intensity", 0),
            "volatility": m.get("volatility", 0),
            "release_year": t.get("release_year"),
        })
    return {"tracks": out}


@app.get("/api/word-context")
def api_word_context(word: str):
    """Return lines where the word appears, with artist/title. For word cloud click-through."""
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Missing word parameter")
    word = word.strip().lower()
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"word": word, "contexts": []}
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT wc.line, t.artist, t.title FROM word_context wc
               JOIN track t ON t.id = wc.track_id WHERE wc.run_id = ? AND wc.word = ? LIMIT 50""",
            (run_id, word),
        ).fetchall()
        contexts = [{"line": r[0], "artist": r[1], "title": r[2]} for r in rows]
        return {"word": word, "contexts": contexts}
    finally:
        conn.close()


@app.get("/api/topics")
def api_topics():
    """Return theme labels with top tracks. Prefers Gemini themes when available."""
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"topics": [], "source": "none"}
    llm_themes = db.get_run_llm_themes(run_id)
    if llm_themes:
        playlist_pk = db.get_latest_playlist_id()
        tracks = db.get_tracks(playlist_pk) if playlist_pk else []
        by_id = {t["id"]: t for t in tracks}
        topics = []
        for th in llm_themes:
            top_tracks = []
            ids = th.get("track_ids") or []
            n = max(1, len(ids))
            for tid in ids[:5]:
                t = by_id.get(tid)
                if t:
                    top_tracks.append({
                        "title": t["title"],
                        "artist": t["artist"],
                        "weight": round(1.0 / n, 3),
                    })
            label = th.get("name") or " / ".join(th.get("keywords") or [])
            topics.append({
                "id": th.get("topic_index", 0),
                "label": label,
                "description": th.get("description") or "",
                "keywords": th.get("keywords") or [],
                "topic_index": th.get("topic_index", 0),
                "top_tracks": top_tracks,
            })
        return {"topics": topics, "source": "llm"}

    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT id, label, topic_index FROM topic WHERE run_id = ? ORDER BY topic_index",
            (run_id,),
        ).fetchall()
        topics = []
        for r in rows:
            track_rows = conn.execute(
                """SELECT t.title, t.artist, tt.weight FROM track_topic tt
                   JOIN track t ON t.id = tt.track_id
                   WHERE tt.run_id = ? AND tt.topic_id = ?
                   ORDER BY tt.weight DESC LIMIT 3""",
                (run_id, r[0]),
            ).fetchall()
            topics.append({
                "id": r[0],
                "label": r[1],
                "description": "",
                "keywords": r[1].split(" / ") if r[1] else [],
                "topic_index": r[2],
                "top_tracks": [
                    {"title": tr[0], "artist": tr[1], "weight": tr[2]} for tr in track_rows
                ],
            })
        return {"topics": topics, "source": "nmf"}
    finally:
        conn.close()


_WORD_RE = re.compile(r"[a-z][a-z']*")


@app.get("/api/stats")
def api_stats():
    """Corpus stats and standout tracks for the latest dataset (for the Explore page)."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"has_data": False}
    tracks = db.get_tracks(playlist_pk)
    if not tracks:
        return {"has_data": False}
    info = db.get_playlist_info(playlist_pk)

    vocab: set[str] = set()
    total_words = 0
    per_track = []
    for t in tracks:
        text = (t.get("cleaned_lyrics") or t.get("raw_lyrics") or "").lower()
        words = _WORD_RE.findall(text)
        total_words += len(words)
        vocab.update(words)
        m = t.get("metrics") or {}
        if not m:
            continue
        per_track.append({
            "title": t["title"],
            "artist": t["artist"],
            "words": m.get("words", len(words)),
            "unique": m.get("unique_words", 0),
            "diversity": m.get("diversity", 0.0),
            "valence": m.get("valence", 0.0),
            "intensity": m.get("intensity", 0.0),
            "volatility": m.get("volatility", 0.0),
            "repetition": m.get("repetition", 0.0),
            "rhyme_density": m.get("rhyme_density", 0.0),
        })

    scored = [p for p in per_track if p["words"] > 0]
    substantial = [p for p in scored if p["words"] >= 40] or scored

    def _pick(items, key, reverse=True):
        if not items:
            return None
        p = sorted(items, key=lambda x: x[key], reverse=reverse)[0]
        return {"title": p["title"], "artist": p["artist"], "value": round(p[key], 3)}

    n = len(scored)
    return {
        "has_data": True,
        "name": (info or {}).get("name") or None,
        "image_url": (info or {}).get("image_url") or None,
        "track_count": len(tracks),
        "analyzed_count": n,
        "total_words": total_words,
        "unique_words": len(vocab),
        "avg_words_per_track": round(total_words / len(tracks), 1) if tracks else 0,
        "avg_valence": round(sum(p["valence"] for p in scored) / n, 4) if n else 0,
        "avg_intensity": round(sum(p["intensity"] for p in scored) / n, 4) if n else 0,
        "avg_volatility": round(sum(p["volatility"] for p in scored) / n, 4) if n else 0,
        "avg_rhyme_density": round(sum(p["rhyme_density"] for p in scored) / n, 4) if n else 0,
        "avg_repetition": round(sum(p["repetition"] for p in scored) / n, 4) if n else 0,
        "superlatives": {
            "darkest": _pick(scored, "valence", reverse=False),
            "brightest": _pick(scored, "valence"),
            "most_volatile": _pick(scored, "volatility"),
            "biggest_vocabulary": _pick(substantial, "unique"),
            "most_repetitive": _pick(substantial, "repetition"),
            "densest_rhymes": _pick(substantial, "rhyme_density"),
        },
    }


_craft_cache: dict[int, dict] = {}


_SOUND_AVG_KEYS = [
    "syllables_per_line", "syllable_consistency", "perfect_rhyme_density",
    "slant_rhyme_density", "internal_rhyme", "alliteration", "assonance",
    "plosive_ratio", "sibilant_ratio", "soft_ratio",
    "concreteness", "pct_concrete", "pct_abstract", "sensory_per_100",
]


@app.get("/api/craft")
def api_craft():
    """Craft analysis of the corpus: signature words, hooks, rhyme pairs,
    point of view, speech acts, sound/diction profile, verse vs chorus contrast."""
    run_id = db.get_latest_run_id()
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"has_data": False}
    cache_key = run_id or -1
    if cache_key in _craft_cache:
        return _craft_cache[cache_key]
    tracks = db.get_tracks(playlist_pk)
    if not tracks:
        return {"has_data": False}

    # Lyrics baseline from every other dataset fetched into this DB
    baseline_tracks = db.get_baseline_tracks(playlist_pk)
    baseline_counts, _ = _corpus_counts(baseline_tracks) if baseline_tracks else (None, None)
    sig = signature_words(tracks, baseline_counts=baseline_counts)

    # Corpus sound/diction averages from stored per-track metrics
    with_metrics = [t["metrics"] for t in tracks if t.get("metrics")]
    sound = {}
    if with_metrics:
        for key in _SOUND_AVG_KEYS:
            vals = [m.get(key) for m in with_metrics if m.get(key) is not None]
            if vals:
                sound[key] = round(sum(vals) / len(vals), 4)
        sensory_totals: dict[str, int] = {}
        for m in with_metrics:
            for k, v in (m.get("sensory") or {}).items():
                sensory_totals[k] = sensory_totals.get(k, 0) + v
        sound["sensory_totals"] = sensory_totals

    result = {
        "has_data": True,
        "signature_words": sig["words"],
        "signature_baseline": sig["baseline"],
        "hooks": corpus_hooks(tracks),
        "rhyme_pairs": corpus_rhyme_pairs(tracks),
        "pov": pov_profile(tracks),
        "speech_acts": speech_acts_profile(tracks),
        "sound": sound,
        "section_contrast": section_contrast(tracks),
    }
    _craft_cache.clear()
    _craft_cache[cache_key] = result
    return result


@app.get("/api/tracks")
def api_tracks():
    """All tracks in the latest dataset with per-track metrics and structure summary."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"tracks": []}
    tracks = db.get_tracks(playlist_pk)
    out = []
    for i, t in enumerate(tracks):
        m = t.get("metrics") or {}
        has_lyrics = bool(t.get("cleaned_lyrics") or t.get("raw_lyrics"))
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics")) if has_lyrics else {}
        out.append({
            "id": t["id"],
            "index": i,
            "title": t["title"],
            "artist": t["artist"],
            "release_year": t.get("release_year"),
            "album_image": t.get("album_image"),
            "has_lyrics": has_lyrics,
            "words": m.get("words", 0),
            "unique_words": m.get("unique_words", 0),
            "valence": m.get("valence", 0),
            "intensity": m.get("intensity", 0),
            "volatility": m.get("volatility", 0),
            "rhyme_density": m.get("rhyme_density", 0),
            "repetition": m.get("repetition", 0),
            "structure": st.get("summary", ""),
            "chorus_share": st.get("chorus_share", 0),
        })
    return {"tracks": out}


@app.get("/api/track/{track_id}")
def api_track(track_id: int):
    """One track: metrics plus lyrics split into labeled sections, with per-line
    data: tone, rhyme-scheme letter (perfect/slant), and speech act.
    Uses Gemini for section labels, sentence-aware speech acts, and metaphors when available."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        raise HTTPException(status_code=404, detail="No data.")
    tracks = db.get_tracks(playlist_pk)
    t = next((x for x in tracks if x["id"] == track_id), None)
    if t is None:
        raise HTTPException(status_code=404, detail="Track not found.")

    text = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
    flat_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Lazy LLM analysis — cached per track until lyrics change
    track_llm = db.get_track_llm(track_id)
    text_hash = llm_module.lyrics_hash("\n".join(flat_lines)) if flat_lines else ""
    if flat_lines and llm_module.is_available():
        if not track_llm or track_llm.get("hash") != text_hash:
            fresh = llm_module.analyze_track(t["title"], t["artist"], flat_lines)
            if fresh:
                db.update_track_llm(track_id, fresh)
                track_llm = fresh

    if track_llm and track_llm.get("sections"):
        raw_sections = llm_module.sections_from_llm(track_llm, flat_lines)
        sections = [{"label": s["label"], "lines": s["lines"], "words": len(_WORD_RE.findall(" ".join(s["lines"]).lower()))} for s in raw_sections]
        summary = " – ".join(s["label"] for s in sections)
        chorus_words = sum(s["words"] for s in sections if s["label"].split(" ")[0].lower() == "chorus")
        total_words = sum(s["words"] for s in sections) or 1
        chorus_share = round(chorus_words / total_words, 3)
    else:
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics"))
        sections = st.get("sections", [])
        summary = st.get("summary", "")
        chorus_share = st.get("chorus_share", 0)

    # Per-line annotations over the whole song so rhyme letters span sections
    all_lines = [line for s in sections for line in s["lines"]]
    scheme = end_rhyme_scheme(all_lines)
    idx = 0
    prev_line: str | None = None
    annotated_sections = []
    for s in sections:
        line_data = []
        for line in s["lines"]:
            r = scheme[idx] if idx < len(scheme) else {"letter": "", "kind": None, "word": ""}
            rule_act = classify_speech_act(line, prev_line=prev_line)
            act = llm_module.act_for_line(track_llm, idx, rule_act)
            line_data.append({
                "text": line,
                "valence": round(line_valence(line), 3),
                "act": act,
                "act_source": "llm" if track_llm and str(idx) in (track_llm.get("line_acts") or {}) else "rules",
                "rhyme_letter": r["letter"],
                "rhyme_kind": r["kind"],
                "end_word": r["word"],
                "line_index": idx,
            })
            prev_line = line
            idx += 1
        annotated_sections.append({"label": s["label"], "words": s.get("words", 0), "lines": line_data})

    return {
        "id": t["id"],
        "title": t["title"],
        "artist": t["artist"],
        "release_year": t.get("release_year"),
        "album_image": t.get("album_image"),
        "metrics": t.get("metrics") or {},
        "sections": annotated_sections,
        "summary": summary,
        "chorus_share": chorus_share,
        "llm": {
            "available": bool(track_llm),
            "summary": (track_llm or {}).get("summary") or "",
            "metaphors": (track_llm or {}).get("metaphors") or [],
            "imagery": (track_llm or {}).get("imagery") or {},
        },
    }


_word_stats_cache: dict[int, dict] = {}


@app.get("/api/word-stats")
def api_word_stats():
    """Corpus stats for every word (for hover tooltips in the lyrics viewer):
    count, number of songs it appears in, and usage ratio vs everyday English."""
    import math

    from wordfreq import zipf_frequency

    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"words": {}}
    if playlist_pk in _word_stats_cache:
        return _word_stats_cache[playlist_pk]
    tracks = db.get_tracks(playlist_pk)
    counts: dict[str, int] = {}
    songs: dict[str, int] = {}
    for t in tracks:
        text = (t.get("cleaned_lyrics") or t.get("raw_lyrics") or "").lower()
        toks = _WORD_RE.findall(text)
        for w in toks:
            counts[w] = counts.get(w, 0) + 1
        for w in set(toks):
            songs[w] = songs.get(w, 0) + 1
    total = sum(counts.values()) or 1
    # Pronouns/function words and generic indefinites are rated by the norms but
    # don't function as imagery — leave their concreteness out of the lens.
    no_conc = _stopwords() | GENERIC_INDEFINITES | VOCALIZATIONS
    words = {}
    for w, c in counts.items():
        corpus_zipf = math.log10(c / total * 1e9)
        eng = zipf_frequency(w, "en") or 1.5
        entry = {
            "count": c,
            "songs": songs.get(w, 0),
            "ratio": round(10 ** (corpus_zipf - eng), 1),
        }
        if w not in no_conc:
            conc = concreteness_for(w)
            if conc is not None:
                entry["conc"] = round(conc, 2)
        words[w] = entry
    result = {"words": words}
    _word_stats_cache.clear()
    _word_stats_cache[playlist_pk] = result
    return result


_barcode_cache: dict[int, dict] = {}


@app.get("/api/barcode")
def api_barcode():
    """Per-track, per-line tone values for the album barcode visualization."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"tracks": []}
    if playlist_pk in _barcode_cache:
        return _barcode_cache[playlist_pk]
    tracks = db.get_tracks(playlist_pk)
    out = []
    for t in tracks:
        text = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            continue
        out.append({
            "id": t["id"],
            "title": t["title"],
            "values": [round(line_valence(l), 3) for l in lines],
        })
    result = {"tracks": out}
    _barcode_cache.clear()
    _barcode_cache[playlist_pk] = result
    return result


@app.get("/api/trends")
def api_trends():
    """Per-year averages (valence, lexical diversity, words per track) for
    datasets with release years — e.g. artist discographies."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"years": []}
    tracks = db.get_tracks(playlist_pk)
    by_year: dict[int, list[dict]] = {}
    for t in tracks:
        y = t.get("release_year")
        m = t.get("metrics") or {}
        if not y or not m:
            continue
        by_year.setdefault(y, []).append(m)
    years = []
    for y in sorted(by_year):
        ms = by_year[y]
        n = len(ms)
        years.append({
            "year": y,
            "tracks": n,
            "valence": round(sum(m.get("valence", 0) for m in ms) / n, 4),
            "intensity": round(sum(m.get("intensity", 0) for m in ms) / n, 4),
            "diversity": round(sum(m.get("diversity", 0) for m in ms) / n, 4),
            "words_per_track": round(sum(m.get("words", 0) for m in ms) / n, 1),
            "rhyme_density": round(sum(m.get("rhyme_density", 0) for m in ms) / n, 4),
        })
    return {"years": years}


# --- Lyric Lab: suggestions and cliche check ---

@app.get("/api/suggest/rhymes")
def api_suggest_rhymes(word: str, limit: int = 15):
    """Return rhyming words for the given word (using pronouncing library)."""
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Missing word parameter")
    word = word.strip().lower()
    try:
        import pronouncing
        rhymes = pronouncing.rhymes(word)
        return {"word": word, "rhymes": rhymes[:limit]}
    except Exception as e:
        return {"word": word, "rhymes": [], "error": str(e)}


@app.get("/api/suggest/thematic")
def api_suggest_thematic(word: str, limit: int = 20):
    """Return thematically related words from corpus (top words that co-occur in same topic or top overall)."""
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Missing word parameter")
    word = word.strip().lower()
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"word": word, "thematic": []}
    conn = db.get_connection()
    try:
        # Return top words from same run (excluding the word itself) as simple thematic neighborhood
        rows = conn.execute(
            "SELECT word, count FROM word_frequency WHERE run_id = ? AND (pos IS NULL OR pos = '') AND word != ? ORDER BY count DESC LIMIT ?",
            (run_id, word, limit),
        ).fetchall()
        thematic = [r[0] for r in rows]
        return {"word": word, "thematic": thematic}
    finally:
        conn.close()


class ClicheCheckRequest(BaseModel):
    text: str


@app.get("/api/cliche-words")
def api_cliche_words():
    """Return set of words that appear in >50% of songs (for client-side highlighting)."""
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"words": []}
    info = db.get_playlist_info()
    if not info or info["track_count"] == 0:
        return {"words": []}
    n_tracks = info["track_count"]
    threshold = max(1, int(n_tracks * 0.5) + 1)
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT word FROM word_context WHERE run_id = ?
               GROUP BY word HAVING COUNT(DISTINCT track_id) >= ?""",
            (run_id, threshold),
        ).fetchall()
        words = [r[0] for r in rows]
        return {"words": words}
    finally:
        conn.close()


@app.post("/api/cliche-check")
def api_cliche_check(body: ClicheCheckRequest):
    """Tokenize text and return which words are in the >50% cliche set."""
    from nltk.tokenize import word_tokenize
    cliche_res = api_cliche_words()
    cliche_set = set(cliche_res.get("words", []))
    text = (body.text or "").lower()
    tokens = [w for w in word_tokenize(text) if w.isalpha()]
    found = [w for w in tokens if w in cliche_set]
    return {"cliche_words": list(dict.fromkeys(found))}
