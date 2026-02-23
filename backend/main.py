"""
FastAPI app for The Emo Almanac.
Run: uvicorn backend.main:app --reload
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from spotipy.oauth2 import SpotifyOAuth

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from backend.cleaner import clean_lyrics
from backend.fetch import extract_playlist_id, fetch_playlist
from backend.analyze import tokenize_lyrics, top_n_words, build_word_contexts
from backend.nlp import sentiment_scores, top_n_by_pos, run_lda
from backend import db

app = FastAPI(title="The Emo Almanac API", version="0.1.0")

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
        raise RuntimeError("Set SPOTIFY_REDIRECT_URI in env (e.g. https://your-app.onrender.com/api/auth/spotify/callback)")
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
    auth_url = oauth.get_authorize_url(state="emo_almanac")
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
    response = RedirectResponse(url=frontend_url + "?spotify=ok")
    response.set_cookie(
        key="spotify_token",
        value=access_token,
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return response


@app.get("/api/auth/status")
def api_auth_status(request: Request):
    """Return whether user has logged in with Spotify (for playlist access)."""
    token = request.cookies.get("spotify_token")
    return {"spotify": bool(token)}


@app.post("/api/fetch", response_model=FetchResponse)
def api_fetch(body: FetchRequest, request: Request):
    """Fetch playlist from Spotify and lyrics from Genius; clean and store in DB. Uses Spotify OAuth token if present."""
    playlist_id = extract_playlist_id(body.playlist_url)
    if not playlist_id:
        raise HTTPException(status_code=400, detail="Invalid playlist URL or ID")
    spotify_token = request.cookies.get("spotify_token")
    try:
        raw_tracks = fetch_playlist(body.playlist_url, spotify_access_token=spotify_token)
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
            raise HTTPException(status_code=500, detail="API key problem. Check your Spotify and Genius keys in Render dashboard.")
        if "404" in msg or "not found" in msg_lower:
            raise HTTPException(status_code=404, detail="Playlist not found. Check the URL and that the playlist is public.")
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
        raise HTTPException(status_code=400, detail="Playlist is empty or could not be read.")
    # Clean lyrics and add cleaned_lyrics
    for t in raw_tracks:
        t["raw_lyrics"] = t.get("lyrics")
        t["cleaned_lyrics"] = clean_lyrics(t.get("lyrics")) if t.get("lyrics") else None
    playlist_pk = db.insert_playlist(playlist_id)
    db.insert_tracks(playlist_pk, raw_tracks)
    return FetchResponse(
        ok=True,
        message=f"Fetched {len(raw_tracks)} tracks.",
        track_count=len(raw_tracks),
        playlist_id=playlist_id,
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
            sad, ang, nos = sentiment_scores(raw)
            db.update_track_sentiment(t["id"], sad, ang, nos)
    except Exception:
        pass

    try:
        by_pos = top_n_by_pos(tracks, text_key=text_key, n=30)
        for pos_name, pairs in by_pos.items():
            db.insert_word_frequencies(run_id, pairs, pos=pos_name)
    except Exception:
        pass

    try:
        topic_labels, per_track_weights, doc_track_ids = run_lda(tracks, text_key=text_key, n_topics=6)
        if topic_labels and per_track_weights and doc_track_ids:
            topic_ids = db.insert_topics(run_id, topic_labels)
            for topic_idx, topic_id in enumerate(topic_ids):
                weights = [(doc_track_ids[i], per_track_weights[i][topic_idx][1]) for i in range(len(per_track_weights))]
                db.insert_track_topics(run_id, topic_id, weights)
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
    """Return tracks with sadness (and anger, nostalgia) for heatmap. Order by track index."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        return {"tracks": []}
    tracks = db.get_tracks(playlist_pk)
    out = []
    for i, t in enumerate(tracks):
        out.append({
            "track_index": i,
            "title": t["title"],
            "artist": t["artist"],
            "sadness": t.get("sentiment_sadness") if t.get("sentiment_sadness") is not None else 0,
            "anger": t.get("sentiment_anger") if t.get("sentiment_anger") is not None else 0,
            "nostalgia": t.get("sentiment_nostalgia") if t.get("sentiment_nostalgia") is not None else 0,
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
    """Return topic labels and optionally songs per topic from latest run."""
    run_id = db.get_latest_run_id()
    if run_id is None:
        return {"topics": []}
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT id, label, topic_index FROM topic WHERE run_id = ? ORDER BY topic_index",
            (run_id,),
        ).fetchall()
        topics = []
        for r in rows:
            topics.append({
                "id": r[0],
                "label": r[1],
                "topic_index": r[2],
            })
        return {"topics": topics}
    finally:
        conn.close()


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
