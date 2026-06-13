# Dad Ass Lyric Analyzer 3000 — Full Codebase Export

> Auto-generated export for LLM discussion. Excludes: `package-lock.json`, `backend/data/concreteness.tsv`, `node_modules`, `.git`.

## Table of Contents

- [./README.md](#READMEmd)
- [./DEPLOYMENT.md](#DEPLOYMENTmd)
- [./package.json](#packagejson)
- [./requirements.txt](#requirementstxt)
- [./Dockerfile](#Dockerfile)
- [./render.yaml](#renderyaml)
- [./vercel.json](#verceljson)
- [./.env.example](#envexample)
- [./render.env.example](#renderenvexample)
- [./vercel.env.example](#vercelenvexample)
- [./analyze.py](#analyzepy)
- [./fetch_lyrics.py](#fetchlyricspy)
- [./backend/__init__.py](#backendinitpy)
- [./backend/main.py](#backendmainpy)
- [./backend/db.py](#backenddbpy)
- [./backend/fetch.py](#backendfetchpy)
- [./backend/cleaner.py](#backendcleanerpy)
- [./backend/analyze.py](#backendanalyzepy)
- [./backend/nlp.py](#backendnlppy)
- [./backend/llm.py](#backendllmpy)
- [./frontend/package.json](#frontendpackagejson)
- [./frontend/tsconfig.json](#frontendtsconfigjson)
- [./frontend/next.config.mjs](#frontendnextconfigmjs)
- [./frontend/postcss.config.mjs](#frontendpostcssconfigmjs)
- [./frontend/tailwind.config.ts](#frontendtailwindconfigts)
- [./frontend/vercel.json](#frontendverceljson)
- [./frontend/components.json](#frontendcomponentsjson)
- [./frontend/.eslintrc.json](#frontendeslintrcjson)
- [./frontend/.env.local.example](#frontendenvlocalexample)
- [./frontend/app/layout.tsx](#frontendapplayouttsx)
- [./frontend/app/page.tsx](#frontendapppagetsx)
- [./frontend/app/globals.css](#frontendappglobalscss)
- [./frontend/app/explore/page.tsx](#frontendappexplorepagetsx)
- [./frontend/app/lyric-lab/page.tsx](#frontendapplyric-labpagetsx)
- [./frontend/app/api/auth/spotify/callback/route.ts](#frontendappapiauthspotifycallbackroutets)
- [./frontend/lib/api.ts](#frontendlibapits)
- [./frontend/lib/tone.ts](#frontendlibtonets)
- [./frontend/lib/utils.ts](#frontendlibutilsts)
- [./frontend/components/tracks-panel.tsx](#frontendcomponentstracks-paneltsx)
- [./frontend/components/trends-chart.tsx](#frontendcomponentstrends-charttsx)
- [./frontend/components/word-cloud.tsx](#frontendcomponentsword-cloudtsx)
- [./frontend/components/mood-flow.tsx](#frontendcomponentsmood-flowtsx)
- [./frontend/components/album-barcode.tsx](#frontendcomponentsalbum-barcodetsx)
- [./frontend/components/emotion-grid.tsx](#frontendcomponentsemotion-gridtsx)
- [./frontend/components/craft-panels.tsx](#frontendcomponentscraft-panelstsx)
- [./frontend/components/craft-extra.tsx](#frontendcomponentscraft-extratsx)
- [./frontend/components/stat-cards.tsx](#frontendcomponentsstat-cardstsx)
- [./frontend/components/mood-map.tsx](#frontendcomponentsmood-maptsx)
- [./frontend/components/mood-meter.tsx](#frontendcomponentsmood-metertsx)
- [./frontend/components/topic-bubbles.tsx](#frontendcomponentstopic-bubblestsx)
- [./frontend/components/ui/button.tsx](#frontendcomponentsuibuttontsx)
- [./frontend/components/ui/card.tsx](#frontendcomponentsuicardtsx)
- [./frontend/components/ui/dialog.tsx](#frontendcomponentsuidialogtsx)
- [./frontend/components/ui/input.tsx](#frontendcomponentsuiinputtsx)
- [./frontend/components/ui/label.tsx](#frontendcomponentsuilabeltsx)

---

## `./README.md`

*136 lines*

```markdown
# Dad Ass Lyric Analyzer 3000

Lyric analysis and writing tools for any genre: analyze Spotify playlists, albums, or artists; visualize sentiment and word frequency; and write with rhyme/thematic suggestions and a cliché detector.

**Frontend (deployed):** https://frontend-woad-xi-34.vercel.app — To use it with data, deploy the backend (e.g. Render) and set `NEXT_PUBLIC_API_URL` in Vercel to the backend URL, and set `CORS_ORIGINS` on the backend to the frontend URL.

## Push to GitHub

The project is already a git repo with one commit. To push it to GitHub:

1. **Create a new repository** on [GitHub](https://github.com/new): name it e.g. `emo-almanac` or `dadass-lyric-master-2000`, leave “Add a README” unchecked.
2. **Add the remote and push** (replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name):

   ```bash
   cd "/Users/tyler/Desktop/Dadass Lyric Master 2000"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

## Quick start

**1. Backend (Python)**

```bash
cd "/Users/tyler/Desktop/Dadass Lyric Master 2000"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Add a `.env` in the project root with your API keys (see [Setup](#setup) below). Then:

```bash
uvicorn backend.main:app --reload
```

API runs at **http://localhost:8000**.

**2. Frontend (Next.js)**

In a second terminal:

```bash
cd frontend
cp .env.local.example .env.local   # optional; defaults to http://localhost:8000
npm install
npm run dev
```

Open **http://localhost:3000**. Paste a Spotify playlist, album, or artist URL, click **Fetch lyrics**, then **Analyze**. Use **Explore** for the word cloud and sadness heatmap, and **Lyric Lab** for writing with suggestions and cliché highlighting.

## Setup

**API keys** (in project root `.env`):

- **Spotify:** [Developer Dashboard](https://developer.spotify.com/dashboard) → create app → Client ID and Client Secret.
- **Genius:** [API Clients](https://genius.com/api-clients) → create app → Access Token.

```env
SPOTIPY_CLIENT_ID=...
SPOTIPY_CLIENT_SECRET=...
GENIUS_ACCESS_TOKEN=...
```

**Frontend** (optional): in `frontend/.env.local` set `NEXT_PUBLIC_API_URL=http://localhost:8000` if the API is on a different host.

**Spotify playlist access:** Spotify’s API only allows reading playlist tracks with a **user** token (scope `playlist-read-private`), not with app-only client credentials. So in the app you must click **“Log in with Spotify”** once; after that, fetch will work for your playlists (including public ones). On Render, set `SPOTIFY_REDIRECT_URI` and `FRONTEND_URL` (see Deployment).

## Project structure

```
.
├── .env                    # API keys (do not commit)
├── requirements.txt        # Python deps
├── backend/
│   ├── main.py            # FastAPI app
│   ├── fetch.py           # Spotify + Genius fetch
│   ├── cleaner.py         # Lyric meta-tag stripping
│   ├── analyze.py        # Tokenize, top words, word context
│   ├── nlp.py            # Sentiment, POS, LDA topics
│   └── db.py             # SQLite schema and helpers
├── frontend/              # Next.js 14 (App Router), Tailwind, ShadcnUI
│   ├── app/
│   │   ├── page.tsx       # Dashboard (fetch / analyze)
│   │   ├── explore/       # Word cloud + sentiment heatmap
│   │   └── lyric-lab/     # Editor, suggestions, cliché list
│   └── lib/api.ts        # API client
└── data/
    └── emo_almanac.db    # SQLite (created on first run)
```

## Features

- **Dashboard:** Paste a Spotify playlist, album, or artist URL → Fetch lyrics (Spotify + Genius, with LRCLIB fallback) → Analyze (word frequency, sentiment, POS, topic modeling). Data stored in SQLite. Playlists require Spotify login; albums and artists don't. Artist fetch pulls the whole discography (albums + singles, deduped, capped at 150 tracks).
- **Explore:** Interactive word cloud (click a word to see lyric lines) and sadness-by-track bar chart.
- **Lyric Lab:** Text area for writing; suggestions for rhymes and thematic words from the corpus; list of words that appear in >50% of dataset songs (overused/cliché).

## Deployment

**Backend (Render.com)**

1. Push the repo to GitHub and connect it to [Render](https://render.com).
2. New → Web Service → connect repo, use **Docker** runtime (Render will use the root `Dockerfile`).
3. Add environment variables: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `GENIUS_ACCESS_TOKEN`, `CORS_ORIGINS` (your frontend URL), `SPOTIFY_REDIRECT_URI` (use the **frontend** callback URL, e.g. `https://frontend-woad-xi-34.vercel.app/api/auth/spotify/callback`, so Spotify sends users to the frontend and the token is delivered reliably), and `FRONTEND_URL` (your frontend URL). In the [Spotify app](https://developer.spotify.com/dashboard) → Edit Settings → Redirect URIs, add that same `SPOTIFY_REDIRECT_URI` value.
4. Deploy. Note: free tier uses ephemeral disk; SQLite data is lost on redeploy.

**Frontend (Vercel)**

1. Push the repo and import the project in [Vercel](https://vercel.com); set **Root Directory** to `frontend`.
2. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = `https://dadass-lyric-master-2000-1.onrender.com`
   - For Spotify login: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` (same values as backend), and `SPOTIFY_REDIRECT_URI` = `https://YOUR_VERCEL_APP.vercel.app/api/auth/spotify/callback` (your frontend callback URL). Add that exact URL to your [Spotify app](https://developer.spotify.com/dashboard) Redirect URIs too.
3. Deploy. Set the frontend URL as `CORS_ORIGINS` on the backend.

**One-command deploy (if you have CLI logged in)**

- Frontend: `cd frontend && npx vercel --prod` (set `NEXT_PUBLIC_API_URL` in Vercel dashboard to your backend URL).
- Backend: Connect the repo to Render and use the Dockerfile as above; or install Render CLI (`brew install render`), then `render login` and create a web service from the repo.

## Errors

- **Invalid playlist URL or ID** — Use a full Spotify playlist link or the 22-character playlist ID.
- **Rate limit** — Genius or Spotify limit; wait a minute and try again.
- **Check your API keys** — Ensure `.env` has correct `SPOTIPY_*` and `GENIUS_ACCESS_TOKEN`.
- **No playlist data. Run fetch first.** — Click “Fetch lyrics” before “Analyze”.
- **Spotify “something went wrong” when saving Redirect URI** — Spotify allows multiple redirect URIs, so having two is fine. If the dashboard won’t save: (1) Use the exact URL with `https://`, no trailing slash (e.g. `https://dadass-lyric-master-2000.onrender.com/api/auth/spotify/callback`). (2) Try removing all redirect URIs, click Save, then add the one you need and Save again. (3) Try another browser or an incognito window in case of cache/session issues.

## CLI (optional)

From project root with venv active:

```bash
python -m backend.fetch "https://open.spotify.com/playlist/..."
```

This writes `data/raw_lyrics.json` and does not use the DB. The web flow (Fetch → Analyze) uses the database and is the main way to run the pipeline.
```

---

## `./DEPLOYMENT.md`

*97 lines*

```markdown
# Deployment guide

This app uses **two** hosting services. They do different jobs.

```
You in the browser
       ↓
   VERCEL  ← the website (buttons, charts, lyrics viewer)
       ↓  API calls
   RENDER  ← the Python backend (fetch lyrics, analyze, Gemini)
       ↓
 Spotify / Genius / Gemini APIs
```

## Vercel = frontend only

- **What it runs:** the Next.js app in the `frontend/` folder
- **Your URL:** https://frontend-woad-xi-34.vercel.app
- **Does NOT run:** Python, Gemini, SQLite, or lyric fetching

### Fix Vercel build errors (`package.json` / Next.js not found)

The Next.js app lives in `frontend/`. Vercel must either build from that folder or use the repo root shim.

**Option A (recommended):** Vercel Dashboard → your project → **Settings → General → Root Directory** → set to `frontend` → Save → Redeploy.

**Option B (works without changing Root Directory):** Pull latest `main`. The repo includes:
- Root `package.json` with `next` (so Vercel detects the framework)
- Root `vercel.json` that runs `npm install` / `npm run build` in `frontend/`

If you still see “No Next.js version detected”, confirm **Root Directory is blank** (repo root) when using Option B, or set it to `frontend` for Option A — do not mix both.

### Vercel environment variables

| Variable | Example |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://dadass-lyric-master-2000-1.onrender.com` |
| `SPOTIFY_CLIENT_ID` | (same as Spotify dashboard) |
| `SPOTIFY_CLIENT_SECRET` | (same as Spotify dashboard) |
| `SPOTIFY_REDIRECT_URI` | `https://frontend-woad-xi-34.vercel.app/api/auth/spotify/callback` |

---

## Render = backend only

- **What it runs:** Python FastAPI (`Dockerfile` at repo root)
- **Does NOT run:** the React/Next.js UI

### Environment groups ≠ a running service

An **Environment Group** (like your `dadass` group) is just a **saved list of env vars**. It does nothing until you:

1. Create a **Web Service** on Render, AND
2. **Link** the `dadass` env group to that service (or paste the vars directly on the service)

If you only have an env group and no Web Service, Gemini vars never reach the app.

### Create the Render backend (if you don't have a service)

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**
2. Connect repo `backyardbugs/dadass-lyric-master-2000`
3. **Runtime:** Docker (uses root `Dockerfile`)
4. **Environment:** link your `dadass` group, or add vars manually:

| Variable | Purpose |
|---|---|
| `SPOTIPY_CLIENT_ID` | Spotify API |
| `SPOTIPY_CLIENT_SECRET` | Spotify API |
| `GENIUS_ACCESS_TOKEN` | Lyrics |
| `GEMINI_API_KEY` | Gemini craft pass |
| `GEMINI_MODEL` | `gemini-2.5-flash` |
| `GEMINI_ENABLED` | `1` |
| `CORS_ORIGINS` | `https://frontend-woad-xi-34.vercel.app` |
| `FRONTEND_URL` | `https://frontend-woad-xi-34.vercel.app` |
| `SPOTIFY_REDIRECT_URI` | `https://frontend-woad-xi-34.vercel.app/api/auth/spotify/callback` |

5. Deploy → copy the service URL (e.g. `https://something.onrender.com`)
6. Put that URL in Vercel as `NEXT_PUBLIC_API_URL`

### Note on backend URL

Production backend: **https://dadass-lyric-master-2000-1.onrender.com**

See `render.env.example` for every variable the Render service needs.
See `vercel.env.example` for Vercel settings.

---

## After both are deployed

1. Open your **Vercel** URL
2. Fetch an album
3. Analyze (Gemini runs in background ~1 min)
4. Explore → Themes + track lyrics

Check backend health: `https://YOUR-RENDER-URL.onrender.com/api/status`  
Should show `"gemini_enabled": true` and after Analyze `"gemini_status": {"status": "complete", ...}`
```

---

## `./package.json`

*13 lines*

```json
{
  "name": "dadass-lyric-master-2000",
  "private": true,
  "description": "Repo root shim for Vercel Next.js detection; app lives in frontend/",
  "dependencies": {
    "next": "14.2.35"
  },
  "scripts": {
    "build": "npm run build --prefix frontend",
    "dev": "npm run dev --prefix frontend",
    "start": "npm run start --prefix frontend"
  }
}
```

---

## `./requirements.txt`

*23 lines*

```text
# Dad Ass Lyric Analyzer 3000 — Data Pipeline & Backend
# Python 3.10+ recommended

# Spotify API client
spotipy>=2.23.0

# Genius lyrics API client
lyricsgenius>=3.0.0

# Web framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# NLP
nltk>=3.8.0
vaderSentiment>=3.3.2
scikit-learn>=1.3.0
pronouncing>=0.2.0
wordfreq>=3.0.0

# Data & utilities
python-dotenv>=1.0.0
requests>=2.31.0
```

---

## `./Dockerfile`

*23 lines*

```
# Backend only. Build from repo root.
FROM python:3.11-slim

WORKDIR /app

# System deps for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake NLTK data into the image so analysis works on first request
RUN python -c "import nltk; [nltk.download(p, quiet=True) for p in ['punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger_eng']]"

COPY backend/ ./backend/
RUN mkdir -p /app/data

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
ENV PORT=8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
```

---

## `./render.yaml`

*8 lines*

```yaml
# Render.com blueprint. Deploy from repo root.
# In Render dashboard set: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, GENIUS_ACCESS_TOKEN, CORS_ORIGINS (e.g. https://your-app.vercel.app)
services:
  - type: web
    name: emo-almanac-api
    runtime: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
```

---

## `./vercel.json`

*8 lines*

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "installCommand": "npm install --prefix frontend",
  "buildCommand": "npm run build --prefix frontend",
  "devCommand": "npm run dev --prefix frontend",
  "ignoreCommand": "git diff HEAD^ HEAD --quiet -- frontend/"
}
```

---

## ./.env.example

*File not found*

## `./render.env.example`

*17 lines*

```env
# Paste these into your Render Web Service (or linked Environment Group).
# Service: https://dadass-lyric-master-2000-1.onrender.com

# --- Required for fetch/analyze ---
SPOTIPY_CLIENT_ID=
SPOTIPY_CLIENT_SECRET=
GENIUS_ACCESS_TOKEN=

# --- Gemini craft pass (Analyze) ---
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
GEMINI_ENABLED=1

# --- CORS + OAuth redirects ---
CORS_ORIGINS=https://frontend-woad-xi-34.vercel.app
FRONTEND_URL=https://frontend-woad-xi-34.vercel.app
SPOTIFY_REDIRECT_URI=https://frontend-woad-xi-34.vercel.app/api/auth/spotify/callback
```

---

## `./vercel.env.example`

*9 lines*

```env
# Vercel → Project → Settings → Environment Variables

NEXT_PUBLIC_API_URL=https://dadass-lyric-master-2000-1.onrender.com

SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=https://frontend-woad-xi-34.vercel.app/api/auth/spotify/callback

# Also set Vercel Root Directory to: frontend
```

---

## `./analyze.py`

*115 lines*

```python
"""
analyze.py — Dad Ass Lyric Analyzer 3000 NLP Pipeline (Phase 1)

Loads raw lyrics from data/raw_lyrics.json and computes:
  - Top 50 most common words (excluding stopwords)

Uses NLTK for tokenization and stopwords. Run fetch_lyrics.py first to generate
raw_lyrics.json.

Usage:
    python analyze.py [path_to_raw_lyrics.json]
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter

# NLTK is used for stopwords and word tokenization (lightweight, no large models)
import nltk

# Ensure NLTK data is available (run once per environment)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Default path to raw lyrics from fetch_lyrics.py
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_RAW_PATH = DATA_DIR / "raw_lyrics.json"


def load_raw_lyrics(path: Path) -> list[dict]:
    """Load the JSON produced by fetch_lyrics.py."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """
    Light normalization: lowercase for consistent counting.
    Heavy cleaning (e.g. [Chorus], [Verse]) can be added in a dedicated cleaner later.
    """
    if not text:
        return ""
    return text.lower().strip()


def tokenize_lyrics(lyrics_list: list[dict]) -> list[str]:
    """
    Concatenate all lyrics, normalize, and tokenize into words.
    Skips entries with no lyrics.
    """
    all_text = []
    for entry in lyrics_list:
        raw = entry.get("lyrics")
        if not raw or not isinstance(raw, str):
            continue
        all_text.append(normalize_text(raw))
    combined = " ".join(all_text)
    # word_tokenize splits on punctuation and whitespace; we get words only
    tokens = word_tokenize(combined)
    # Keep only alphabetic tokens (drop numbers and stray punctuation)
    return [t for t in tokens if t.isalpha()]


def top_n_words(tokens: list[str], n: int = 50, lang: str = "english") -> list[tuple[str, int]]:
    """
    Return the top `n` most common words, excluding stopwords.
    Uses NLTK's English stopwords by default.
    """
    stop = set(stopwords.words(lang))
    filtered = [w for w in tokens if w not in stop]
    counter = Counter(filtered)
    return counter.most_common(n)


def main() -> None:
    raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RAW_PATH
    if not raw_path.exists():
        print(f"Error: Raw lyrics file not found: {raw_path}")
        print("Run fetch_lyrics.py first with a Spotify playlist URL.")
        sys.exit(1)

    print(f"Loading lyrics from {raw_path}...")
    raw = load_raw_lyrics(raw_path)
    songs_with_lyrics = sum(1 for e in raw if e.get("lyrics"))
    print(f"  {len(raw)} tracks, {songs_with_lyrics} with lyrics.")

    print("Tokenizing and counting words (excluding stopwords)...")
    tokens = tokenize_lyrics(raw)
    top50 = top_n_words(tokens, n=50)

    print("\n--- Top 50 words (excluding stopwords) ---\n")
    for i, (word, count) in enumerate(top50, 1):
        print(f"  {i:2}. {word:<20} {count:>5}")

    # Optionally write results to a JSON for later use (e.g. word cloud, suggestions)
    out_path = DATA_DIR / "top_words.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([{"word": w, "count": c} for w, c in top50], f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
```

---

## `./fetch_lyrics.py`

*163 lines*

```python
"""
fetch_lyrics.py — Dad Ass Lyric Analyzer 3000 Data Pipeline (Phase 1)

Authenticates with Spotify (playlist tracklist) and Genius (lyrics),
then saves raw track + lyrics data to a JSON file for analysis.

Usage:
    python fetch_lyrics.py "https://open.spotify.com/playlist/37i9dQZF1DX..."

Requires environment variables:
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET — from Spotify Developer Dashboard
    GENIUS_ACCESS_TOKEN — from https://genius.com/api-clients
"""

import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from lyricsgenius import Genius
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Load .env so SPOTIPY_* and GENIUS_* are available
load_dotenv()

# Output directory for raw data
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_FILE = DATA_DIR / "raw_lyrics.json"


def extract_playlist_id(url: str) -> str | None:
    """
    Extract Spotify playlist ID from a URL or raw ID.
    Handles: open.spotify.com/playlist/ID, spotify:playlist:ID, or plain ID.
    """
    if not url or not url.strip():
        return None
    url = url.strip()
    # Plain ID (22 chars, alphanumeric)
    if re.match(r"^[a-zA-Z0-9]{22}$", url):
        return url
    # spotify:playlist:ID
    m = re.search(r"spotify:playlist:([a-zA-Z0-9]{22})", url)
    if m:
        return m.group(1)
    # https://open.spotify.com/playlist/ID
    m = re.search(r"open\.spotify\.com/playlist/([a-zA-Z0-9]{22})", url)
    if m:
        return m.group(1)
    return None


def get_spotify_tracks(playlist_id: str) -> list[dict]:
    """
    Fetch all tracks from a public Spotify playlist using Client Credentials.
    Returns a list of dicts with 'artist' and 'title' (and 'spotify_id' for reference).
    """
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env or environment"
        )

    auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = Spotify(auth_manager=auth)

    tracks = []
    offset = 0
    limit = 50  # Spotify max per request

    while True:
        page = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        items = page.get("items") or []
        if not items:
            break
        for item in items:
            track = item.get("track")
            if not track:
                continue
            # Skip local or unavailable tracks
            if track.get("is_local") or not track.get("name"):
                continue
            artists = track.get("artists") or []
            artist_name = ", ".join(a.get("name", "") for a in artists) or "Unknown"
            tracks.append({
                "spotify_id": track.get("id"),
                "artist": artist_name,
                "title": track.get("name", "").strip(),
            })
        offset += len(items)
        if len(items) < limit:
            break

    return tracks


def fetch_lyrics_for_tracks(tracks: list[dict], genius_token: str) -> list[dict]:
    """
    For each track, search Genius by title + artist and attach lyrics.
    Returns the same list of dicts with a "lyrics" key added (or None if not found).
    """
    genius = Genius(genius_token)
    # Reduce noise in responses; we'll clean further in the cleaner script
    genius.remove_section_headers = True
    genius.skip_non_songs = True

    results = []
    for i, t in enumerate(tracks):
        artist, title = t["artist"], t["title"]
        print(f"  [{i+1}/{len(tracks)}] {artist} — {title}")
        lyrics = None
        try:
            # search_song(title, artist) — title first, then artist
            song = genius.search_song(title, artist)
            if song and getattr(song, "lyrics", None):
                lyrics = song.lyrics.strip()
        except Exception as e:
            print(f"    Warning: {e}")
        results.append({
            "spotify_id": t.get("spotify_id"),
            "artist": artist,
            "title": title,
            "lyrics": lyrics,
        })
    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python fetch_lyrics.py <SPOTIFY_PLAYLIST_URL_OR_ID>")
        print("Example: python fetch_lyrics.py 'https://open.spotify.com/playlist/37i9dQZF1DX...'")
        sys.exit(1)

    playlist_input = sys.argv[1]
    playlist_id = extract_playlist_id(playlist_input)
    if not playlist_id:
        print("Error: Could not parse playlist ID from URL.")
        sys.exit(1)

    genius_token = os.getenv("GENIUS_ACCESS_TOKEN")
    if not genius_token:
        raise RuntimeError("Set GENIUS_ACCESS_TOKEN in .env or environment")

    print("Fetching tracklist from Spotify...")
    tracks = get_spotify_tracks(playlist_id)
    print(f"Found {len(tracks)} tracks.")

    print("Fetching lyrics from Genius...")
    data = fetch_lyrics_for_tracks(tracks, genius_token)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved raw data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

---

## `./backend/__init__.py`

*1 lines*

```python
# Dad Ass Lyric Analyzer 3000 backend package
```

---

## `./backend/main.py`

*1020 lines*

```python
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
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
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
    gemini: dict | None = None


def _run_gemini_pass(run_id: int, playlist_pk: int, dataset_name: str) -> None:
    """Background Gemini craft pass — avoids Render's 30s HTTP timeout."""
    try:
        tracks = db.get_tracks(playlist_pk)
        db.update_run_llm_status(run_id, {
            "ok": False,
            "status": "running",
            "message": "Gemini craft pass in progress…",
            "tracks_enriched": 0,
        })
        result = llm_module.analyze_corpus(tracks, dataset_name)
        status = {
            "ok": result.get("ok", False),
            "status": "complete" if result.get("ok") else "failed",
            "message": result.get("message", ""),
            "tracks_enriched": len(result.get("track_data") or {}),
            "chunks": result.get("chunks", 0),
            "partial": result.get("partial", False),
        }
        if result.get("ok"):
            for tid, data in result["track_data"].items():
                db.update_track_llm(tid, data)
            if result.get("themes"):
                db.update_run_llm_themes(run_id, result["themes"])
        db.update_run_llm_status(run_id, status)
    except Exception as exc:
        db.update_run_llm_status(run_id, {
            "ok": False,
            "status": "failed",
            "message": str(exc)[:200],
            "tracks_enriched": 0,
        })


@app.post("/api/analyze", response_model=AnalyzeResponse)
def api_analyze(background_tasks: BackgroundTasks):
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

    gemini_result: dict | None = None
    if llm_module.is_enabled():
        info = db.get_playlist_info(playlist_pk)
        dataset_name = (info or {}).get("name") or "Lyrics dataset"
        gemini_result = {
            "ok": False,
            "status": "running",
            "message": "Gemini craft pass running in background.",
            "tracks_enriched": 0,
        }
        try:
            db.update_run_llm_status(run_id, gemini_result)
        except Exception:
            pass
        background_tasks.add_task(_run_gemini_pass, run_id, playlist_pk, dataset_name)

    msg = "Analysis complete."
    if gemini_result and gemini_result.get("status") == "running":
        msg += " Gemini craft pass is running — open Explore and refresh in about a minute."
    elif gemini_result and gemini_result.get("ok"):
        msg += f" Gemini craft pass: {gemini_result.get('tracks_enriched', 0)} tracks enriched."
    elif gemini_result and gemini_result.get("message"):
        msg += f" (Gemini: {gemini_result['message']})"

    return AnalyzeResponse(
        ok=True,
        message=msg,
        top_words=[{"word": w, "count": c} for w, c in top50],
        run_id=run_id,
        gemini=gemini_result,
    )


class StatusResponse(BaseModel):
    has_data: bool
    track_count: int
    last_analyzed: str | None
    playlist_name: str | None = None
    image_url: str | None = None
    gemini_enabled: bool = False
    gemini_status: dict | None = None


@app.get("/api/status", response_model=StatusResponse)
def api_status():
    """Return whether we have playlist data and last analysis time."""
    info = db.get_playlist_info()
    if not info:
        return StatusResponse(has_data=False, track_count=0, last_analyzed=None)
    run_id = db.get_latest_run_id(info["id"])
    last_analyzed = None
    gemini_status = None
    if run_id:
        conn = db.get_connection()
        try:
            row = conn.execute("SELECT run_at FROM analysis_run WHERE id = ?", (run_id,)).fetchone()
            if row:
                last_analyzed = row[0]
        finally:
            conn.close()
        gemini_status = db.get_run_llm_status(run_id)
    return StatusResponse(
        has_data=True,
        track_count=info["track_count"],
        last_analyzed=last_analyzed,
        playlist_name=info.get("name") or None,
        image_url=info.get("image_url") or None,
        gemini_enabled=llm_module.is_enabled(),
        gemini_status=gemini_status,
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
    """Return theme labels with top tracks. Uses Gemini themes when cached for this run."""
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
            topics.append({
                "id": th.get("topic_index", 0),
                "label": th.get("name") or "",
                "description": th.get("description") or "",
                "keywords": th.get("keywords") or [],
                "topic_index": th.get("topic_index", 0),
                "top_tracks": top_tracks,
            })
        return {"topics": topics, "source": "gemini"}

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
    """One track: metrics plus lyrics with per-line tone, rhyme, speech act.
    Gemini annotations (sections, metaphors, imagery) come from cache only — set during Analyze."""
    playlist_pk = db.get_latest_playlist_id()
    if playlist_pk is None:
        raise HTTPException(status_code=404, detail="No data.")
    tracks = db.get_tracks(playlist_pk)
    t = next((x for x in tracks if x["id"] == track_id), None)
    if t is None:
        raise HTTPException(status_code=404, detail="Track not found.")

    text = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
    flat_lines = [l.strip() for l in text.split("\n") if l.strip()]
    track_llm = db.get_track_llm(track_id)
    text_hash = llm_module.lyrics_hash("\n".join(flat_lines)) if flat_lines else ""
    if track_llm and track_llm.get("hash") != text_hash:
        track_llm = None

    if track_llm and track_llm.get("sections") and flat_lines:
        raw_sections = llm_module.sections_from_llm(track_llm, flat_lines)
        sections = [
            {
                "label": s["label"],
                "lines": s["lines"],
                "words": len(_WORD_RE.findall(" ".join(s["lines"]).lower())),
            }
            for s in raw_sections
        ]
        summary = " – ".join(s["label"] for s in sections)
        chorus_words = sum(
            s["words"] for s in sections if s["label"].split(" ")[0].lower() == "chorus"
        )
        total_words = sum(s["words"] for s in sections) or 1
        chorus_share = round(chorus_words / total_words, 3)
    else:
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics"))
        sections = st.get("sections", [])
        summary = st.get("summary", "")
        chorus_share = st.get("chorus_share", 0)

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
                "act_source": "gemini" if track_llm and str(idx) in (track_llm.get("line_acts") or {}) else "rules",
                "rhyme_letter": r["letter"],
                "rhyme_kind": r["kind"],
                "end_word": r["word"],
                "line_index": idx,
            })
            prev_line = line
            idx += 1
        annotated_sections.append({
            "label": s["label"],
            "words": s.get("words", 0),
            "lines": line_data,
        })

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
        "gemini": {
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
```

---

## `./backend/db.py`

*447 lines*

```python
"""
SQLite schema and helpers for Dad Ass Lyric Analyzer 3000.
Database file: data/emo_almanac.db
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Project root/data for DB (one level up from backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "emo_almanac.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS playlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id TEXT UNIQUE NOT NULL,
                name TEXT,
                fetched_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS track (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL REFERENCES playlist(id),
                artist TEXT NOT NULL,
                title TEXT NOT NULL,
                spotify_id TEXT,
                raw_lyrics TEXT,
                cleaned_lyrics TEXT,
                sentiment_sadness REAL,
                sentiment_anger REAL,
                sentiment_nostalgia REAL,
                UNIQUE(playlist_id, artist, title)
            );
            CREATE TABLE IF NOT EXISTS analysis_run (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL REFERENCES playlist(id),
                run_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS word_frequency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES analysis_run(id),
                word TEXT NOT NULL,
                count INTEGER NOT NULL,
                pos TEXT
            );
            CREATE TABLE IF NOT EXISTS word_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES analysis_run(id),
                word TEXT NOT NULL,
                track_id INTEGER NOT NULL REFERENCES track(id),
                line TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS topic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES analysis_run(id),
                label TEXT NOT NULL,
                topic_index INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS track_topic (
                track_id INTEGER NOT NULL REFERENCES track(id),
                run_id INTEGER NOT NULL REFERENCES analysis_run(id),
                topic_id INTEGER NOT NULL REFERENCES topic(id),
                weight REAL NOT NULL,
                PRIMARY KEY (track_id, run_id, topic_id)
            );
            CREATE INDEX IF NOT EXISTS idx_track_playlist ON track(playlist_id);
            CREATE INDEX IF NOT EXISTS idx_word_freq_run ON word_frequency(run_id);
            CREATE INDEX IF NOT EXISTS idx_word_context_run_word ON word_context(run_id, word);
        """)
        # Migrations for DBs created before these columns existed
        for ddl in (
            "ALTER TABLE track ADD COLUMN metrics_json TEXT",
            "ALTER TABLE track ADD COLUMN release_year INTEGER",
            "ALTER TABLE track ADD COLUMN album_image TEXT",
            "ALTER TABLE playlist ADD COLUMN image_url TEXT",
            "ALTER TABLE track ADD COLUMN llm_json TEXT",
            "ALTER TABLE analysis_run ADD COLUMN llm_themes_json TEXT",
            "ALTER TABLE analysis_run ADD COLUMN llm_status_json TEXT",
        ):
            try:
                conn.execute(ddl)
            except sqlite3.OperationalError:
                pass
        conn.commit()
    finally:
        conn.close()


def insert_playlist(playlist_id: str, name: str | None = None, image_url: str | None = None) -> int:
    """Insert or replace playlist; return playlist table id."""
    conn = get_connection()
    try:
        fetched_at = datetime.utcnow().isoformat() + "Z"
        conn.execute(
            "INSERT INTO playlist (playlist_id, name, fetched_at, image_url) VALUES (?, ?, ?, ?)"
            " ON CONFLICT(playlist_id) DO UPDATE SET name=excluded.name, fetched_at=excluded.fetched_at, image_url=excluded.image_url",
            (playlist_id, name or "", fetched_at, image_url),
        )
        conn.commit()
        row = conn.execute("SELECT id FROM playlist WHERE playlist_id = ?", (playlist_id,)).fetchone()
        return row[0]
    finally:
        conn.close()


def insert_tracks(playlist_pk: int, tracks: list[dict]) -> None:
    """Insert tracks with raw_lyrics and cleaned_lyrics. tracks have artist, title, spotify_id, raw_lyrics, cleaned_lyrics."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM track WHERE playlist_id = ?", (playlist_pk,))
        for t in tracks:
            conn.execute(
                """INSERT INTO track (playlist_id, artist, title, spotify_id, raw_lyrics, cleaned_lyrics, release_year, album_image)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    playlist_pk,
                    t["artist"],
                    t["title"],
                    t.get("spotify_id"),
                    t.get("raw_lyrics") or t.get("lyrics"),
                    t.get("cleaned_lyrics"),
                    t.get("release_year"),
                    t.get("album_image"),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def get_latest_playlist_id() -> int | None:
    """Return the latest playlist table id (by fetched_at), or None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM playlist ORDER BY fetched_at DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def get_tracks(playlist_pk: int | None = None) -> list[dict]:
    """Get tracks for a playlist (or latest playlist if playlist_pk is None)."""
    conn = get_connection()
    try:
        if playlist_pk is None:
            playlist_pk = get_latest_playlist_id()
        if playlist_pk is None:
            return []
        rows = conn.execute(
            "SELECT id, artist, title, raw_lyrics, cleaned_lyrics, metrics_json, release_year, album_image FROM track WHERE playlist_id = ? ORDER BY id",
            (playlist_pk,),
        ).fetchall()
        out = []
        for r in rows:
            metrics = {}
            if r["metrics_json"]:
                try:
                    metrics = json.loads(r["metrics_json"])
                except (ValueError, TypeError):
                    metrics = {}
            out.append({
                "id": r["id"],
                "artist": r["artist"],
                "title": r["title"],
                "raw_lyrics": r["raw_lyrics"],
                "cleaned_lyrics": r["cleaned_lyrics"],
                "lyrics": r["cleaned_lyrics"] or r["raw_lyrics"],
                "metrics": metrics,
                "release_year": r["release_year"],
                "album_image": r["album_image"],
            })
        return out
    finally:
        conn.close()


def get_known_lyrics() -> dict[tuple[str, str], str]:
    """(artist, title) -> raw lyrics for every track we've ever fetched lyrics for.
    Lets refetches reuse lyrics instead of hammering the lyrics APIs."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT artist, title, raw_lyrics FROM track WHERE raw_lyrics IS NOT NULL AND raw_lyrics != ''"
        ).fetchall()
        return {(r["artist"].lower(), r["title"].lower()): r["raw_lyrics"] for r in rows}
    finally:
        conn.close()


def get_baseline_tracks(exclude_playlist_pk: int) -> list[dict]:
    """Lyrics of all tracks from other datasets (for the lyrics-baseline comparison)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT raw_lyrics, cleaned_lyrics FROM track WHERE playlist_id != ?",
            (exclude_playlist_pk,),
        ).fetchall()
        return [{"raw_lyrics": r["raw_lyrics"], "cleaned_lyrics": r["cleaned_lyrics"]} for r in rows]
    finally:
        conn.close()


def get_playlist_info(playlist_pk: int | None = None) -> dict | None:
    """Get playlist id, name, fetched_at, track_count. Uses latest if playlist_pk is None."""
    conn = get_connection()
    try:
        if playlist_pk is None:
            playlist_pk = get_latest_playlist_id()
        if playlist_pk is None:
            return None
        row = conn.execute(
            "SELECT id, playlist_id, name, fetched_at, image_url FROM playlist WHERE id = ?",
            (playlist_pk,),
        ).fetchone()
        if not row:
            return None
        count = conn.execute("SELECT COUNT(*) FROM track WHERE playlist_id = ?", (playlist_pk,)).fetchone()[0]
        return {
            "id": row["id"],
            "playlist_id": row["playlist_id"],
            "name": row["name"],
            "fetched_at": row["fetched_at"],
            "image_url": row["image_url"],
            "track_count": count,
        }
    finally:
        conn.close()


def insert_analysis_run(playlist_pk: int) -> int:
    """Record an analysis run; return run id."""
    conn = get_connection()
    try:
        run_at = datetime.utcnow().isoformat() + "Z"
        conn.execute(
            "INSERT INTO analysis_run (playlist_id, run_at) VALUES (?, ?)",
            (playlist_pk, run_at),
        )
        run_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        return run_id
    finally:
        conn.close()


def delete_word_frequencies_for_run(run_id: int) -> None:
    """Remove all word_frequency rows for a run (call before inserting new analysis)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM word_frequency WHERE run_id = ?", (run_id,))
        conn.commit()
    finally:
        conn.close()


def insert_word_frequencies(run_id: int, word_counts: list[tuple[str, int]], pos: str | None = None) -> None:
    """Insert word frequency rows. word_counts: list of (word, count)."""
    conn = get_connection()
    try:
        for word, count in word_counts:
            conn.execute(
                "INSERT INTO word_frequency (run_id, word, count, pos) VALUES (?, ?, ?, ?)",
                (run_id, word, count, pos),
            )
        conn.commit()
    finally:
        conn.close()


def insert_word_contexts(run_id: int, word_contexts: list[tuple[str, int, str]]) -> None:
    """Insert (word, track_id, line) for word context."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM word_context WHERE run_id = ?", (run_id,))
        for word, track_id, line in word_contexts:
            conn.execute(
                "INSERT INTO word_context (run_id, word, track_id, line) VALUES (?, ?, ?, ?)",
                (run_id, word, track_id, line),
            )
        conn.commit()
    finally:
        conn.close()


def get_latest_run_id(playlist_pk: int | None = None) -> int | None:
    if playlist_pk is None:
        playlist_pk = get_latest_playlist_id()
    if playlist_pk is None:
        return None
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM analysis_run WHERE playlist_id = ? ORDER BY run_at DESC LIMIT 1",
            (playlist_pk,),
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def update_track_metrics(track_id: int, metrics: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE track SET metrics_json=? WHERE id=?",
            (json.dumps(metrics), track_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_track_llm(track_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT llm_json FROM track WHERE id=?", (track_id,)).fetchone()
        if not row or not row[0]:
            return None
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            return None
    finally:
        conn.close()


def update_track_llm(track_id: int, llm: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE track SET llm_json=? WHERE id=?",
            (json.dumps(llm), track_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_run_llm_themes(run_id: int, themes: list[dict]) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE analysis_run SET llm_themes_json=? WHERE id=?",
            (json.dumps(themes), run_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_run_llm_status(run_id: int, status: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE analysis_run SET llm_status_json=? WHERE id=?",
            (json.dumps(status), run_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_run_llm_themes(run_id: int) -> list[dict] | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT llm_themes_json FROM analysis_run WHERE id=?",
            (run_id,),
        ).fetchone()
        if not row or not row[0]:
            return None
        try:
            data = json.loads(row[0])
            return data if isinstance(data, list) else None
        except (ValueError, TypeError):
            return None
    finally:
        conn.close()


def get_run_llm_status(run_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT llm_status_json FROM analysis_run WHERE id=?",
            (run_id,),
        ).fetchone()
        if not row or not row[0]:
            return None
        try:
            data = json.loads(row[0])
            return data if isinstance(data, dict) else None
        except (ValueError, TypeError):
            return None
    finally:
        conn.close()


def insert_topics(run_id: int, labels: list[str]) -> list[int]:
    """Insert topic labels for a run; return list of topic ids."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM topic WHERE run_id = ?", (run_id,))
        ids = []
        for i, label in enumerate(labels):
            cur = conn.execute(
                "INSERT INTO topic (run_id, label, topic_index) VALUES (?, ?, ?) RETURNING id",
                (run_id, label, i),
            )
            row = cur.fetchone()
            if row:
                ids.append(row[0])
        conn.commit()
        return ids
    finally:
        conn.close()


def insert_track_topics(run_id: int, topic_id: int, track_weights: list[tuple[int, float]]) -> None:
    """track_weights: list of (track_id, weight)."""
    conn = get_connection()
    try:
        for track_id, weight in track_weights:
            conn.execute(
                "INSERT OR REPLACE INTO track_topic (track_id, run_id, topic_id, weight) VALUES (?, ?, ?, ?)",
                (track_id, run_id, topic_id, weight),
            )
        conn.commit()
    finally:
        conn.close()
```

---

## `./backend/fetch.py`

*380 lines*

```python
"""
Fetch pipeline: Spotify playlist -> Genius lyrics.
Callable from FastAPI or CLI. Does not write to DB; returns list[dict].
"""
from __future__ import annotations

import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from dotenv import load_dotenv
from lyricsgenius import Genius
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class _TokenAuth:
    """Auth manager that returns a pre-obtained access token (for OAuth user token)."""

    def __init__(self, access_token: str):
        self._token = access_token

    def get_access_token(self, as_dict: bool = False):
        if as_dict:
            return {"access_token": self._token, "token_type": "Bearer", "expires_in": -1}
        return self._token


def extract_playlist_id(url: str) -> str | None:
    """Extract Spotify playlist ID from URL or raw ID."""
    ref = extract_spotify_ref(url)
    return ref[1] if ref and ref[0] == "playlist" else None


def extract_spotify_ref(url: str) -> tuple[str, str] | None:
    """Extract (kind, id) from a Spotify playlist/album/artist URL, URI, or raw ID.
    Raw 22-char IDs are assumed to be playlists."""
    if not url or not url.strip():
        return None
    url = url.strip()
    if re.match(r"^[a-zA-Z0-9]{22}$", url):
        return ("playlist", url)
    for kind in ("playlist", "album", "artist"):
        m = re.search(rf"spotify:{kind}:([a-zA-Z0-9]{{22}})", url)
        if m:
            return (kind, m.group(1))
        m = re.search(rf"open\.spotify\.com/(?:intl-[a-z\-]+/)?{kind}/([a-zA-Z0-9]{{22}})", url)
        if m:
            return (kind, m.group(1))
    return None


def _release_year(release_date: str | None) -> int | None:
    if not release_date:
        return None
    m = re.match(r"(\d{4})", release_date)
    return int(m.group(1)) if m else None


def _spotify_client(access_token: str | None = None) -> Spotify:
    """Spotify client from a user OAuth token, or app client credentials."""
    if access_token:
        return Spotify(auth_manager=_TokenAuth(access_token))
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env")
    return Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def get_spotify_tracks(playlist_id: str, access_token: str | None = None) -> list[dict]:
    """Fetch all tracks from a Spotify playlist. Use access_token (OAuth) for any playlist; else client credentials (public only, may 403)."""
    sp = _spotify_client(access_token)
    market = None if access_token else os.getenv("SPOTIFY_MARKET", "US")
    tracks = []
    skipped = 0
    offset = 0
    limit = 50
    while True:
        page = sp.playlist_tracks(playlist_id, offset=offset, limit=limit, market=market)
        items = page.get("items") or []
        if not items:
            break
        for item in items:
            track = item.get("track")
            if not track or track.get("is_local") or not track.get("name"):
                skipped += 1
                continue
            artists = track.get("artists") or []
            artist_name = ", ".join(a.get("name", "") for a in artists) or "Unknown"
            tracks.append({
                "spotify_id": track.get("id"),
                "artist": artist_name,
                "title": track.get("name", "").strip(),
                "release_year": _release_year((track.get("album") or {}).get("release_date")),
            })
        offset += len(items)
        if len(items) < limit:
            break
    if not tracks and skipped:
        raise ValueError(
            "This playlist only contains local files or podcast episodes, which Spotify's API can't read."
        )
    return tracks


def _image_url(images: list | None) -> str | None:
    if not images:
        return None
    return (images[0] or {}).get("url")


def get_playlist_data(playlist_id: str, access_token: str | None = None) -> tuple[str | None, str | None, list[dict]]:
    """Return (playlist_name, image_url, tracks) for a playlist."""
    tracks = get_spotify_tracks(playlist_id, access_token=access_token)
    name = None
    image = None
    try:
        sp = _spotify_client(access_token)
        info = sp.playlist(playlist_id, fields="name,images") or {}
        name = info.get("name")
        image = _image_url(info.get("images"))
    except Exception:
        pass
    return name, image, tracks


def get_album_data(album_id: str, access_token: str | None = None) -> tuple[str, str | None, list[dict]]:
    """Return ("Artist — Album", cover_url, tracks) for an album. Works with app credentials (no login)."""
    sp = _spotify_client(access_token)
    album = sp.album(album_id)
    album_artist = ", ".join(a.get("name", "") for a in album.get("artists") or []) or "Unknown"
    name = f"{album_artist} — {album.get('name', '')}".strip(" —")
    year = _release_year(album.get("release_date"))
    cover = _image_url(album.get("images"))
    tracks = []
    page = album.get("tracks") or {}
    while True:
        for tr in page.get("items") or []:
            if not tr or not tr.get("name"):
                continue
            artist = ", ".join(a.get("name", "") for a in tr.get("artists") or []) or album_artist
            tracks.append({
                "spotify_id": tr.get("id"),
                "artist": artist,
                "title": tr["name"].strip(),
                "release_year": year,
                "album_image": cover,
            })
        if not page.get("next"):
            break
        page = sp.next(page)
    return name, cover, tracks


def _dedupe_title_key(title: str) -> str:
    """Normalize a title so 'Song', 'Song - Acoustic' and 'Song (Remastered)' dedupe together."""
    base = title.split(" - ")[0]
    base = re.sub(r"\s*[\(\[].*?[\)\]]", "", base)
    return base.lower().strip()


def get_artist_data(
    artist_id: str, access_token: str | None = None, max_tracks: int = 150
) -> tuple[str, str | None, list[dict]]:
    """Return (artist_name, artist_image_url, tracks) across the artist's albums and singles,
    deduped by title. Works with app credentials (no login). Capped at max_tracks."""
    sp = _spotify_client(access_token)
    artist = sp.artist(artist_id)
    name = artist.get("name") or "Unknown"
    artist_image = _image_url(artist.get("images"))

    albums: list[tuple[str, int | None, str | None]] = []
    # Spotify rejects limits above 10 on this endpoint for newer apps ("Invalid limit")
    page = sp.artist_albums(artist_id, include_groups="album,single", limit=10)
    while page:
        for a in page.get("items") or []:
            if a and a.get("id"):
                albums.append((a["id"], _release_year(a.get("release_date")), _image_url(a.get("images"))))
        page = sp.next(page) if page.get("next") else None

    tracks: list[dict] = []
    seen: set[str] = set()
    # Fetch per album: the batch /v1/albums?ids= endpoint is 403 Forbidden for newer apps.
    for album_id, year, cover in albums:
        if len(tracks) >= max_tracks:
            break
        try:
            page = sp.album_tracks(album_id, limit=50)
        except Exception:
            continue
        while page:
            for tr in page.get("items") or []:
                if not tr or not tr.get("name"):
                    continue
                if artist_id not in [a.get("id") for a in tr.get("artists") or []]:
                    continue
                key = _dedupe_title_key(tr["name"])
                if not key or key in seen:
                    continue
                seen.add(key)
                tracks.append({
                    "spotify_id": tr.get("id"),
                    "artist": name,
                    "title": tr["name"].strip(),
                    "release_year": year,
                    "album_image": cover,
                })
            page = sp.next(page) if page.get("next") else None
    return name, artist_image, tracks[:max_tracks]


_LRCLIB_UA = "DadAssLyricAnalyzer/0.1.0"


def _title_matches(query: str, candidate: str) -> bool:
    """Loose title match so the fuzzy fallback can't return a different song."""
    def norm(s: str) -> set[str]:
        return set(re.findall(r"[a-z']+", s.lower()))

    q, c = norm(query), norm(candidate)
    if not q or not c:
        return False
    overlap = len(q & c) / len(q)
    return overlap >= 0.6 or q <= c or c <= q


def _lrclib_get(url: str, params: dict, headers: dict) -> requests.Response:
    """GET with one retry on rate limiting / transient errors."""
    r = requests.get(url, params=params, headers=headers, timeout=10)
    if r.status_code in (429, 500, 502, 503):
        time.sleep(2)
        r = requests.get(url, params=params, headers=headers, timeout=10)
    return r


def _fetch_lyrics_lrclib(artist: str, title: str) -> str | None:
    """Fetch plain lyrics from LRCLIB (free, no key, no scraping). Fallback when Genius is blocked."""
    headers = {"User-Agent": _LRCLIB_UA}
    # Spotify joins multiple artists with ", "; LRCLIB usually indexes the primary artist.
    primary_artist = artist.split(",")[0].strip()
    try:
        r = _lrclib_get(
            "https://lrclib.net/api/get",
            params={"artist_name": primary_artist, "track_name": title},
            headers=headers,
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("instrumental"):
                return None
            lyrics = (data.get("plainLyrics") or "").strip()
            if lyrics:
                return lyrics
        # Fuzzy search fallback for slight title/artist mismatches — but verify the
        # result is actually the same song, not just something by the same artist.
        r = _lrclib_get(
            "https://lrclib.net/api/search",
            params={"artist_name": primary_artist, "track_name": title},
            headers=headers,
        )
        if r.status_code == 200:
            for item in r.json() or []:
                if item.get("instrumental"):
                    continue
                if not _title_matches(title, item.get("trackName") or ""):
                    continue
                if not _title_matches(primary_artist, item.get("artistName") or ""):
                    continue
                lyrics = (item.get("plainLyrics") or "").strip()
                if lyrics:
                    return lyrics
    except Exception:
        pass
    return None


def fetch_lyrics_for_tracks(
    tracks: list[dict],
    genius_token: str | None = None,
    known_lyrics: dict[tuple[str, str], str] | None = None,
) -> list[dict]:
    """For each track, search Genius (falling back to LRCLIB) and attach lyrics.
    known_lyrics ((artist, title) -> lyrics) is consulted first so refetches
    don't re-download. Returns list of {artist, title, spotify_id, lyrics}."""
    token = genius_token or os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Set GENIUS_ACCESS_TOKEN in .env")
    genius = Genius(token)
    genius.remove_section_headers = True
    genius.skip_non_songs = True
    genius_blocked = threading.Event()
    known = known_lyrics or {}

    def resolve(t: dict) -> dict:
        artist, title = t["artist"], t["title"]
        cached = known.get((artist.lower(), title.lower()))
        if cached:
            return {**t, "lyrics": cached}
        # Strip version suffixes ("Song - 2025 Mix", "Song - Live") for better search hits
        search_title = re.sub(r"\s+-\s.*$", "", title).strip() or title
        lyrics = None
        if not genius_blocked.is_set():
            try:
                song = genius.search_song(search_title, artist)
                if song and getattr(song, "lyrics", None):
                    lyrics = song.lyrics.strip()
            except Exception as e:
                # Cloudflare blocks Genius page scraping from datacenter IPs; once we see a
                # 403, stop wasting time on Genius for the rest of the batch.
                if "403" in str(e):
                    genius_blocked.set()
        if not lyrics:
            lyrics = _fetch_lyrics_lrclib(artist, search_title)
        return {**t, "lyrics": lyrics}

    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(resolve, tracks))


def fetch_source(
    url: str,
    spotify_access_token: str | None = None,
    known_lyrics: dict[tuple[str, str], str] | None = None,
) -> tuple[str, str, str | None, str | None, list[dict]]:
    """
    Full fetch for a playlist, album, or artist URL: Spotify tracks -> lyrics.
    Playlists need a user OAuth token (Spotify policy); albums and artists work with app credentials.
    Returns (kind, spotify_id, name, image_url, tracks).
    """
    ref = extract_spotify_ref(url)
    if not ref:
        raise ValueError("Invalid Spotify URL. Paste a playlist, album, or artist link.")
    kind, source_id = ref
    if kind == "playlist":
        name, image, tracks = get_playlist_data(source_id, access_token=spotify_access_token)
    elif kind == "album":
        name, image, tracks = get_album_data(source_id, access_token=spotify_access_token)
    else:
        name, image, tracks = get_artist_data(source_id, access_token=spotify_access_token)
    if not tracks:
        raise ValueError(f"{kind.capitalize()} is empty or could not be read")
    return kind, source_id, name, image, fetch_lyrics_for_tracks(tracks, known_lyrics=known_lyrics)


def fetch_playlist(playlist_url: str, spotify_access_token: str | None = None) -> list[dict]:
    """
    Full fetch: parse URL -> Spotify tracks -> lyrics.
    Accepts playlist, album, or artist URLs. Returns list of {artist, title, spotify_id, lyrics}.
    """
    _, _, _, _, tracks = fetch_source(playlist_url, spotify_access_token=spotify_access_token)
    return tracks


if __name__ == "__main__":
    import sys
    import json
    from backend.cleaner import clean_lyrics as clean

    if len(sys.argv) < 2:
        print("Usage: python -m backend.fetch <PLAYLIST_URL>")
        sys.exit(1)
    try:
        data = fetch_playlist(sys.argv[1])
        for d in data:
            d["cleaned_lyrics"] = clean(d.get("lyrics")) if d.get("lyrics") else None
        out = Path(__file__).resolve().parent.parent / "data" / "raw_lyrics.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} tracks to {out}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

---

## `./backend/cleaner.py`

*39 lines*

```python
"""
Lyric cleaner: strip meta-tags and normalize punctuation.
Used after fetch and before analysis.
"""
from __future__ import annotations

import re


def clean_lyrics(text: str | None) -> str:
    """
    Strip meta-tags like [Chorus], [Verse 1], [Bridge], (x2), etc.
    Normalize punctuation: collapse repeated punctuation, standardize apostrophes.
    """
    if not text or not isinstance(text, str):
        return ""
    s = text.strip()

    # Remove section headers: [Chorus], [Verse 1], [Verse 2], [Bridge], [Pre-Chorus], [Outro], [Intro], [Hook], etc.
    s = re.sub(r"\[[\w\s\-']+\]", "", s, flags=re.IGNORECASE)

    # Remove (x2), (x3), (Repeat), (2x), etc.
    s = re.sub(r"\(\s*x?\d+\s*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\(\s*repeat\s*\)", "", s, flags=re.IGNORECASE)

    # Standardize apostrophes (curly/smart quotes and backticks to straight)
    s = s.replace("'", "'").replace("'", "'")
    s = s.replace("`", "'")
    s = s.replace(""", '"').replace(""", '"')

    # Collapse multiple spaces/newlines to single newline, then trim each line
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    # Collapse repeated punctuation at end of line (e.g. "!!!")
    lines = [re.sub(r"([.!?,…;:])\1+", r"\1", line) for line in lines]
    s = "\n".join(lines)

    # Collapse multiple newlines to one
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()
```

---

## `./backend/analyze.py`

*94 lines*

```python
"""
Analysis: tokenize lyrics, top N words, word context.
Uses NLTK. Callable with list of track dicts (id, lyrics or cleaned_lyrics).
"""

from collections import Counter
from pathlib import Path

import nltk

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)
try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def _normalize(text: str) -> str:
    if not text:
        return ""
    return text.lower().strip()


def tokenize_lyrics(lyrics_list: list[dict], text_key: str = "lyrics") -> list[str]:
    """Concatenate all lyrics from track dicts, normalize, tokenize. Returns flat list of words (alpha only)."""
    all_text = []
    for entry in lyrics_list:
        raw = entry.get(text_key) or entry.get("cleaned_lyrics") or entry.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        all_text.append(_normalize(raw))
    combined = " ".join(all_text)
    tokens = word_tokenize(combined)
    return [t for t in tokens if t.isalpha()]


def top_n_words(tokens: list[str], n: int = 50, lang: str = "english") -> list[tuple[str, int]]:
    """Top n words excluding stopwords. Returns list of (word, count)."""
    stop = set(stopwords.words(lang))
    filtered = [w for w in tokens if w not in stop]
    return Counter(filtered).most_common(n)


def build_word_contexts(tracks: list[dict], text_key: str = "lyrics") -> list[tuple[str, int, str]]:
    """
    For each track with id and lyrics, split into lines and record (word, track_id, line) for each word in line.
    Returns list of (word, track_id, line). Lines are normalized (lower, strip).
    """
    result = []
    for t in tracks:
        track_id = t.get("id")
        if track_id is None:
            continue
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        for line in raw.splitlines():
            line = _normalize(line)
            if not line:
                continue
            words = [w for w in word_tokenize(line) if w.isalpha()]
            for w in words:
                result.append((w.lower(), track_id, line))
    return result


def get_track_tokens_by_document(tracks: list[dict], text_key: str = "lyrics") -> list[tuple[int, list[str]]]:
    """Return list of (track_id, list of tokens) for each track that has lyrics. For topic modeling."""
    out = []
    for t in tracks:
        track_id = t.get("id")
        if track_id is None:
            continue
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        tokens = [w for w in word_tokenize(_normalize(raw)) if w.isalpha()]
        if tokens:
            out.append((track_id, tokens))
    return out
```

---

## `./backend/nlp.py`

*1012 lines*

```python
"""
Craft-focused lyric analysis:
- Tone: per-line VADER sentiment -> valence / intensity / volatility per track
- Repetition: repeated-line ratio and corpus hooks (most repeated lines)
- Rhyme: end-rhyme density and most-used rhyme pairs (CMU pronouncing dictionary)
- Point of view: pronoun profile (I / you / we / they)
- Signature words: corpus usage vs general-English frequency (wordfreq)
- POS-based word frequency
- Themes: TF-IDF + NMF topic extraction
"""
from __future__ import annotations

import math
import re
from collections import Counter
from statistics import mean, pstdev

import nltk
import pronouncing
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordfreq import zipf_frequency

_vader = SentimentIntensityAnalyzer()

_WORD_RE = re.compile(r"[a-z][a-z']*")

# Vocalizations and non-lexical filler — noise for word-choice analysis.
VOCALIZATIONS = {
    "na", "la", "da", "doo", "doot", "oh", "ooh", "oohs", "whoa", "woah", "yeah",
    "hey", "uh", "huh", "mmm", "mm", "hmm", "ah", "aah", "ha", "oo", "ow", "ayy",
    "ay", "yo", "ohh", "ohhh", "woo", "dee", "dum", "bum", "sha", "ba", "bah",
}

PRONOUN_GROUPS = {
    "i": {"i", "me", "my", "mine", "myself", "i'm", "i've", "i'll", "i'd"},
    "you": {"you", "your", "yours", "yourself", "you're", "you've", "you'll", "you'd"},
    "we": {"we", "us", "our", "ours", "ourselves", "we're", "we've", "we'll", "we'd"},
    "they": {
        "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs",
        "he's", "she's", "they're", "they've", "they'll",
    },
}


def _tokens(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _lines(text: str) -> list[str]:
    return [l.strip() for l in text.split("\n") if l.strip()]


def _norm_line(line: str) -> str:
    return " ".join(_tokens(line))


_phones_cache: dict[str, list[str] | None] = {}


def _phones(word: str) -> list[str] | None:
    """First CMU pronunciation as a phoneme list, cached."""
    if word in _phones_cache:
        return _phones_cache[word]
    plist = pronouncing.phones_for_word(word)
    result = plist[0].split() if plist else None
    _phones_cache[word] = result
    return result


def _rhyme_part(word: str) -> str | None:
    phones = pronouncing.phones_for_word(word)
    if not phones:
        return None
    part = pronouncing.rhyming_part(phones[0])
    return part or None


def _vowel_signature(rhyme_part: str | None) -> str | None:
    """Vowel sounds of the rhyming part, stress stripped — the basis of slant rhyme."""
    if not rhyme_part:
        return None
    vowels = [re.sub(r"\d", "", p) for p in rhyme_part.split() if p[-1].isdigit()]
    return " ".join(vowels) or None


def _syllables(word: str) -> int:
    phones = _phones(word)
    if phones:
        return sum(1 for p in phones if p[-1].isdigit()) or 1
    # Fallback heuristic: vowel groups
    groups = re.findall(r"[aeiouy]+", word.lower())
    return max(1, len(groups))


_PLOSIVES = {"P", "B", "T", "D", "K", "G"}
_SIBILANTS = {"S", "Z", "SH", "ZH", "CH", "JH"}
_SOFT = {"L", "R", "M", "N", "NG", "W", "Y"}  # liquids, nasals, glides


def end_rhyme_scheme(lines: list[str], window: int = 4) -> list[dict]:
    """Per-line end-rhyme info: letter (A, B, ... shared by rhyming lines),
    kind ('perfect' | 'slant' | None), and the end word.
    Lines rhyme if their rhyming parts match exactly (perfect) or share the
    same vowel sounds with different consonants (slant), within `window` lines."""
    enders = []
    for line in lines:
        toks = _tokens(line)
        w = toks[-1] if toks else ""
        part = _rhyme_part(w) if w else None
        enders.append({"word": w, "part": part, "sig": _vowel_signature(part)})

    n = len(enders)
    # Union lines that rhyme within the window
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        parent[find(i)] = find(j)

    kinds: list[str | None] = [None] * n
    for i in range(n):
        ei = enders[i]
        if not ei["sig"]:
            continue
        for j in range(i + 1, min(i + 1 + window, n)):
            ej = enders[j]
            if not ej["sig"] or ei["word"] == ej["word"]:
                continue
            if ei["part"] == ej["part"]:
                union(i, j)
                kinds[i] = kinds[i] or "perfect"
                kinds[j] = kinds[j] or "perfect"
            elif ei["sig"] == ej["sig"]:
                union(i, j)
                kinds[i] = kinds[i] or "slant"
                kinds[j] = kinds[j] or "slant"

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    letters: dict[int, str] = {}
    next_letter = 0
    out = []
    for i in range(n):
        root = find(i)
        letter = ""
        if len(groups[root]) >= 2:
            if root not in letters:
                letters[root] = chr(ord("A") + (next_letter % 26))
                next_letter += 1
            letter = letters[root]
        out.append({"word": enders[i]["word"], "letter": letter, "kind": kinds[i]})
    return out


def sound_metrics(lines: list[str]) -> dict:
    """Sound-level craft metrics: syllables, slant/internal rhyme, alliteration,
    assonance, phoneme texture."""
    if not lines:
        return {}
    # Syllables per line
    syl_counts = []
    for line in lines:
        toks = _tokens(line)
        if toks:
            syl_counts.append(sum(_syllables(w) for w in toks))
    syl_mean = mean(syl_counts) if syl_counts else 0.0
    syl_std = pstdev(syl_counts) if len(syl_counts) > 1 else 0.0

    # End rhymes: perfect vs slant participation
    scheme = end_rhyme_scheme(lines, window=2)
    known = [s for s in scheme if s["word"] and _phones(s["word"])]
    perfect = sum(1 for s in scheme if s["kind"] == "perfect")
    slant = sum(1 for s in scheme if s["kind"] == "slant")
    n_known = max(1, len(known))

    # Internal rhyme: vowel-signature matches between non-identical words inside a line
    internal_pairs = 0
    total_words = 0
    allit_lines = 0
    assonance_scores = []
    class_counts = {"plosive": 0, "sibilant": 0, "soft": 0, "other_consonant": 0}
    for line in lines:
        toks = [w for w in _tokens(line) if len(w) > 2]
        total_words += len(toks)
        sigs = []
        initials = []
        vowel_counts: Counter = Counter()
        n_vowels = 0
        for w in toks:
            part = _rhyme_part(w)
            sigs.append((w, _vowel_signature(part)))
            phones = _phones(w)
            if phones:
                first = re.sub(r"\d", "", phones[0])
                initials.append(first if not phones[0][-1].isdigit() else None)
                for p in phones:
                    base = re.sub(r"\d", "", p)
                    if p[-1].isdigit():
                        vowel_counts[base] += 1
                        n_vowels += 1
                    elif base in _PLOSIVES:
                        class_counts["plosive"] += 1
                    elif base in _SIBILANTS:
                        class_counts["sibilant"] += 1
                    elif base in _SOFT:
                        class_counts["soft"] += 1
                    else:
                        class_counts["other_consonant"] += 1
            else:
                initials.append(None)
        for a in range(len(sigs)):
            for b in range(a + 1, len(sigs)):
                if sigs[a][1] and sigs[a][1] == sigs[b][1] and sigs[a][0] != sigs[b][0]:
                    internal_pairs += 1
        # Alliteration: 2+ nearby words sharing an initial consonant sound
        for a in range(len(initials) - 1):
            windowed = [x for x in initials[a:a + 3] if x]
            if len(windowed) >= 2 and len(set(windowed)) < len(windowed):
                allit_lines += 1
                break
        if n_vowels >= 4 and vowel_counts:
            assonance_scores.append(vowel_counts.most_common(1)[0][1] / n_vowels)

    n_cons = sum(class_counts.values()) or 1
    return {
        "syllables_per_line": round(syl_mean, 2),
        "syllable_consistency": round(max(0.0, 1 - (syl_std / syl_mean)) if syl_mean else 0.0, 3),
        "perfect_rhyme_density": round(perfect / n_known, 4),
        "slant_rhyme_density": round(slant / n_known, 4),
        "internal_rhyme": round(internal_pairs / max(1, total_words), 4),
        "alliteration": round(allit_lines / max(1, len(lines)), 4),
        "assonance": round(mean(assonance_scores), 4) if assonance_scores else 0.0,
        "plosive_ratio": round(class_counts["plosive"] / n_cons, 4),
        "sibilant_ratio": round(class_counts["sibilant"] / n_cons, 4),
        "soft_ratio": round(class_counts["soft"] / n_cons, 4),
    }


def rhyme_stats(lines: list[str], window: int = 2) -> tuple[float, list[tuple[str, str]]]:
    """Return (end-rhyme density, rhyme pairs).
    Density = fraction of line endings that perfect-rhyme with another ending
    within `window` lines (among endings the CMU dictionary knows).
    Identical end words don't count as rhymes."""
    enders: list[tuple[str, str | None]] = []
    for line in lines:
        toks = _tokens(line)
        if not toks:
            continue
        w = toks[-1]
        enders.append((w, _rhyme_part(w)))
    known = [(w, p) for w, p in enders if p]
    if len(known) < 2:
        return 0.0, []
    rhymed: set[int] = set()
    pairs: list[tuple[str, str]] = []
    for i in range(len(enders)):
        wi, pi = enders[i]
        if not pi:
            continue
        for j in range(i + 1, min(i + 1 + window, len(enders))):
            wj, pj = enders[j]
            if not pj or wi == wj:
                continue
            if pi == pj:
                rhymed.add(i)
                rhymed.add(j)
                pairs.append(tuple(sorted((wi, wj))))  # type: ignore[arg-type]
    return len(rhymed) / len(known), pairs


def track_metrics(text: str | None) -> dict:
    """Per-track craft metrics. All values are floats/ints; safe for JSON."""
    if not text or not text.strip():
        return {}
    lines = _lines(text)
    tokens = _tokens(text)
    lexical = [t for t in tokens if t not in VOCALIZATIONS]
    if not lines or not tokens:
        return {}

    compounds = [_vader.polarity_scores(l)["compound"] for l in lines]
    valence = mean(compounds)
    intensity = mean(abs(c) for c in compounds)
    volatility = pstdev(compounds) if len(compounds) > 1 else 0.0

    norm = [_norm_line(l) for l in lines]
    norm = [n for n in norm if n]
    line_counts = Counter(norm)
    repetition = 1 - (len(line_counts) / len(norm)) if norm else 0.0

    rhyme_density, _ = rhyme_stats(lines)

    pron = {k: sum(1 for t in tokens if t in group) for k, group in PRONOUN_GROUPS.items()}

    metrics = {
        "valence": round(valence, 4),
        "intensity": round(intensity, 4),
        "volatility": round(volatility, 4),
        "words": len(tokens),
        "unique_words": len(set(lexical)),
        "diversity": round(len(set(lexical)) / len(lexical), 4) if lexical else 0.0,
        "lines": len(lines),
        "words_per_line": round(len(tokens) / len(lines), 2),
        "repetition": round(repetition, 4),
        "rhyme_density": round(rhyme_density, 4),
        "pronouns": pron,
    }
    metrics.update(sound_metrics(lines))
    metrics.update(diction_metrics(text))
    return metrics


# ---------- Diction: concreteness & sensory language ----------

_CONC_PATH = __import__("pathlib").Path(__file__).resolve().parent / "data" / "concreteness.tsv"
_conc_dict: dict[str, float] | None = None


def _concreteness_dict() -> dict[str, float]:
    """Brysbaert et al. (2014) concreteness norms: 1 (abstract) .. 5 (concrete)."""
    global _conc_dict
    if _conc_dict is None:
        d: dict[str, float] = {}
        try:
            with open(_CONC_PATH, encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) == 2:
                        try:
                            d[parts[0]] = float(parts[1])
                        except ValueError:
                            pass
        except OSError:
            pass
        _conc_dict = d
    return _conc_dict


_IRREGULAR_LEMMAS = {
    "feet": "foot", "teeth": "tooth", "men": "man", "women": "woman",
    "children": "child", "mice": "mouse", "geese": "goose", "leaves": "leaf",
    "knives": "knife", "wives": "wife", "lives": "life", "selves": "self",
}


def _lemma_candidates(w: str) -> list[str]:
    """Cheap morphology so 'feet', 'burning', 'cried' find their lemma's rating."""
    out = []
    if w in _IRREGULAR_LEMMAS:
        out.append(_IRREGULAR_LEMMAS[w])
    if w.endswith("ies") and len(w) > 4:
        out.append(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3:
        out.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        out.append(w[:-1])
    if w.endswith("ing") and len(w) > 5:
        out.extend([w[:-3], w[:-3] + "e"])
        if len(w) > 6 and w[-4] == w[-5]:
            out.append(w[:-4])
    if w.endswith("ed") and len(w) > 4:
        out.extend([w[:-2], w[:-1]])
        if len(w) > 5 and w[-3] == w[-4]:
            out.append(w[:-3])
    if w.endswith("ied") and len(w) > 4:
        out.append(w[:-3] + "y")
    return out


def concreteness_for(word: str) -> float | None:
    d = _concreteness_dict()
    if word in d:
        return d[word]
    for cand in _lemma_candidates(word):
        if cand in d:
            return d[cand]
    return None


SENSORY_WORDS = {
    "sight": {
        "see", "saw", "seen", "look", "looked", "looking", "watch", "watched", "stare",
        "staring", "eyes", "light", "dark", "darkness", "bright", "shine", "shining",
        "glow", "glowing", "color", "colors", "red", "blue", "green", "white", "black",
        "golden", "pale", "shadow", "shadows", "neon", "blinding", "glitter", "flash",
        "mirror", "moonlight", "sunlight", "sunset", "sunrise", "sky", "stars",
    },
    "sound": {
        "hear", "heard", "listen", "listening", "sound", "sounds", "loud", "quiet",
        "silence", "silent", "scream", "screaming", "whisper", "whispering", "echo",
        "ring", "ringing", "song", "singing", "sang", "noise", "hum", "humming",
        "static", "thunder", "siren", "sirens", "radio", "music", "voice", "voices",
    },
    "touch": {
        "touch", "touched", "feel", "felt", "hold", "holding", "held", "warm", "warmth",
        "cold", "freezing", "burn", "burning", "soft", "rough", "skin", "hands",
        "fingers", "arms", "shiver", "shaking", "trembling", "numb", "ache", "aching",
        "breath", "breathing", "heartbeat", "squeeze", "pull", "push", "kiss", "kissed",
    },
    "taste": {
        "taste", "tasted", "sweet", "bitter", "sour", "salt", "salty", "sugar", "honey",
        "wine", "whiskey", "beer", "coffee", "cigarette", "cigarettes", "smoke", "drink",
        "drinking", "drunk", "tongue", "lips", "mouth", "blood", "poison",
    },
    "smell": {
        "smell", "smells", "scent", "perfume", "cologne", "gasoline", "smoky", "incense",
        "fragrance", "stale", "fresh", "rot", "rotting", "musty",
    },
}


# Generic person/thing words: rated "concrete" by the norms (raters picture a
# person), but they function as abstractions in lyrics, not images.
GENERIC_INDEFINITES = {
    "somebody", "someone", "something", "somewhere", "anybody", "anyone",
    "anything", "anywhere", "nobody", "nothing", "nowhere", "everybody",
    "everyone", "everything", "everywhere", "thing", "things", "stuff",
    "one", "ones", "way", "time", "times",
}


def diction_metrics(text: str) -> dict:
    """Concreteness profile and sensory-language counts."""
    stop = _stopwords()
    tokens = [w for w in _tokens(text) if w not in VOCALIZATIONS]
    content = [w for w in tokens if w not in stop and w not in GENERIC_INDEFINITES]
    scores = [s for s in (concreteness_for(w) for w in content) if s is not None]
    sensory = {k: sum(1 for w in tokens if w in words) for k, words in SENSORY_WORDS.items()}
    n = max(1, len(tokens))
    return {
        "concreteness": round(mean(scores), 3) if scores else 0.0,
        "pct_concrete": round(sum(1 for s in scores if s >= 4.0) / max(1, len(scores)), 4),
        "pct_abstract": round(sum(1 for s in scores if s <= 2.5) / max(1, len(scores)), 4),
        "sensory_per_100": round(sum(sensory.values()) / n * 100, 2),
        "sensory": sensory,
    }


# ---------- Speech acts ----------

_ACT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("apology", re.compile(r"\b(i'?m sorry|sorry|forgive me|i apologi[sz]e|my fault)\b", re.I)),
    ("promise", re.compile(r"\b(i('| wi)ll always|i('| wi)ll never|i swear|i promise|i('| wi)ll be there|never gonna|i won'?t ever|till the day i die)\b", re.I)),
    ("plea", re.compile(r"\b(please|i('m| am) begg?ing|don'?t leave|don'?t go|stay with me|come back|i need you)\b", re.I)),
    ("accusation", re.compile(r"\b(you never|you always|you lied|you don'?t even|how could you|you made me|it'?s your fault|you said you)\b", re.I)),
    ("confession", re.compile(r"\b(i'?ve been|i never told|truth is|the truth is|i confess|i admit|honestly,? i|i gotta admit)\b", re.I)),
]

_QUESTION_STARTS = re.compile(
    r"^(what|when|where|why|who|how|do|does|did|am|are|is|was|were|will|would|can|could|should|have|has|had)\s+(i|you|we|they|he|she|it|this|that)\b",
    re.I,
)

_IMPERATIVE_STARTS = {
    # High-precision imperative openers only. "remember"/"forget" are deliberately
    # excluded: in lyrics they're overwhelmingly recall ("...can't / Remember what it is"),
    # not commands.
    "come", "hold", "take", "tell", "let", "stop", "wait", "listen", "look",
    "stay", "go", "run", "give", "leave", "save", "call", "say", "keep",
    "close", "open", "turn", "wake", "don't", "dont", "put", "throw", "show", "kiss",
    "drive", "meet", "bring", "follow", "breathe", "hang",
}

# A line ending in one of these is mid-sentence; the next line continues it.
_CONTINUATION_ENDERS = {
    "and", "but", "or", "so", "than", "like", "if", "when", "while", "then",
    "cause", "'cause", "to", "of", "for", "with", "at", "on", "in", "by", "from",
    "into", "over", "under", "through", "the", "a", "an", "my", "your", "his",
    "her", "our", "their", "its", "that", "who", "which", "whom", "where",
    "i'm", "you're", "we're", "they're", "i've", "i'll", "i'd", "not", "never",
}

_MODALS = {
    "can", "can't", "cannot", "could", "couldn't", "will", "won't", "would",
    "wouldn't", "should", "shouldn't", "must", "might", "may", "don't", "didn't",
    "doesn't", "gonna", "wanna", "gotta", "tryna", "to",
}


def _dangling_clause(prev_line: str | None) -> bool:
    """True when prev_line ends mid-sentence, so the next line is a continuation
    (e.g. "But can't for the life of me / Remember what it is")."""
    if not prev_line:
        return False
    toks = _tokens(prev_line)
    if not toks:
        return False
    if toks[-1] in _CONTINUATION_ENDERS:
        return True
    # A modal/aux/"to" with no verb after it means its verb starts the next line.
    last_modal = max((i for i, w in enumerate(toks) if w in _MODALS), default=-1)
    if last_modal >= 0:
        try:
            nltk.data.find("taggers/averaged_perceptron_tagger_eng")
        except LookupError:
            nltk.download("averaged_perceptron_tagger_eng", quiet=True)
        from nltk import pos_tag

        tagged = pos_tag(toks[last_modal + 1:])
        return not any(tag.startswith("VB") for _, tag in tagged)
    return False


def classify_speech_act(line: str, prev_line: str | None = None) -> str:
    """Primary speech act of a lyric line, by transparent rules.
    Lines that continue the previous line's sentence are not classified as
    questions/commands — lyrics spread sentences across lines."""
    stripped = line.strip()
    lowered = stripped.lower()
    for act, pattern in _ACT_PATTERNS:
        if pattern.search(lowered):
            return act
    if _dangling_clause(prev_line):
        return "statement"
    if stripped.endswith("?") or _QUESTION_STARTS.match(lowered):
        return "question"
    first = (_tokens(lowered) or [""])[0]
    if first in _IMPERATIVE_STARTS or lowered.startswith("don't "):
        return "command"
    if stripped.endswith("!"):
        return "exclamation"
    return "statement"


def speech_acts_profile(tracks: list[dict], text_key: str = "cleaned_lyrics", max_examples: int = 40) -> dict:
    """Corpus speech-act counts with example lines per act."""
    counts: Counter = Counter()
    examples: dict[str, list[dict]] = {}
    total = 0
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        seen_in_track: set[str] = set()
        prev: str | None = None
        for line in _lines(text):
            n = _norm_line(line)
            if not n:
                continue
            act = classify_speech_act(line, prev_line=prev)
            prev = line
            total += 1
            counts[act] += 1
            key = f"{act}:{n}"
            if act != "statement" and key not in seen_in_track:
                seen_in_track.add(key)
                bucket = examples.setdefault(act, [])
                if len(bucket) < max_examples and not any(e["line"].lower() == line.lower() for e in bucket):
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


def line_valence(line: str) -> float:
    return _vader.polarity_scores(line)["compound"]


# ---------- Corpus-level craft analysis ----------

def _stopwords() -> set[str]:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords

    return set(stopwords.words("english"))


def _corpus_counts(tracks: list[dict], text_key: str = "cleaned_lyrics") -> tuple[Counter, Counter]:
    """(word counts, song spread) for content words, vocalizations excluded."""
    stop = _stopwords() | VOCALIZATIONS
    counts: Counter = Counter()
    song_spread: Counter = Counter()
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        toks = [w for w in _tokens(text) if w not in stop and len(w) > 2 and "'" not in w]
        counts.update(toks)
        song_spread.update(set(toks))
    return counts, song_spread


def signature_words(
    tracks: list[dict],
    text_key: str = "cleaned_lyrics",
    top: int = 30,
    baseline_counts: Counter | None = None,
) -> dict:
    """Words this corpus over-uses. If baseline_counts (word counts from other
    lyrics) is provided and substantial, rank by log-odds with an informative
    Dirichlet prior (Monroe et al.) against that lyrics baseline — this filters
    out generic 'song words'. Otherwise fall back to comparing against
    general-English frequencies (wordfreq)."""
    counts, song_spread = _corpus_counts(tracks, text_key)
    total = sum(counts.values())
    if total == 0:
        return {"baseline": "none", "words": []}
    min_count = max(3, total // 4000)

    use_lyrics_baseline = baseline_counts is not None and sum(baseline_counts.values()) >= 20000
    out = []
    if use_lyrics_baseline:
        bg_total = sum(baseline_counts.values())
        prior_total = 500.0  # strength of the prior, in pseudo-words
        for word, c in counts.items():
            if c < min_count or song_spread[word] < 2:
                continue
            a_w = prior_total * (baseline_counts[word] + 0.5) / bg_total
            y1, n1 = c, total
            y2, n2 = baseline_counts[word], bg_total
            d = math.log((y1 + a_w) / (n1 + prior_total - y1 - a_w)) - math.log(
                (y2 + a_w) / (n2 + prior_total - y2 - a_w)
            )
            var = 1.0 / (y1 + a_w) + 1.0 / (y2 + a_w)
            z = d / math.sqrt(var)
            rate1 = c / total
            rate2 = (y2 + 0.5) / bg_total
            out.append({
                "word": word,
                "count": c,
                "songs": song_spread[word],
                "ratio": round(rate1 / rate2, 1),
                "score": round(z, 3),
            })
    else:
        for word, c in counts.items():
            if c < min_count or song_spread[word] < 2:
                continue
            corpus_zipf = math.log10(c / total * 1e9)
            eng_zipf = zipf_frequency(word, "en")
            if eng_zipf == 0:
                eng_zipf = 1.5  # very rare in general English
            score = corpus_zipf - eng_zipf
            out.append({
                "word": word,
                "count": c,
                "songs": song_spread[word],
                "ratio": round(10 ** score, 1),
                "score": round(score, 3),
            })
    out.sort(key=lambda x: x["score"], reverse=True)
    return {
        "baseline": "other artists you've fetched" if use_lyrics_baseline else "everyday English",
        "words": out[:top],
    }


def section_contrast(tracks: list[dict]) -> dict:
    """Verse vs chorus craft comparison across the corpus."""
    buckets: dict[str, dict] = {
        "verse": {"lines": [], "tokens": []},
        "chorus": {"lines": [], "tokens": []},
    }
    for t in tracks:
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics"))
        for s in st.get("sections", []):
            base = s["label"].split(" ")[0].lower()
            key = "chorus" if base == "chorus" else ("verse" if base in ("verse", "song") else None)
            if key is None:
                continue
            buckets[key]["lines"].extend(s["lines"])
            buckets[key]["tokens"].extend(_tokens(" ".join(s["lines"])))

    out = {}
    stop = _stopwords()
    for key, b in buckets.items():
        lines, tokens = b["lines"], b["tokens"]
        if not lines or not tokens:
            out[key] = None
            continue
        compounds = [line_valence(l) for l in lines]
        content = [w for w in tokens if w not in stop and w not in VOCALIZATIONS and w not in GENERIC_INDEFINITES]
        scores = [s for s in (concreteness_for(w) for w in content) if s is not None]
        syls = [sum(_syllables(w) for w in _tokens(l)) for l in lines if _tokens(l)]
        out[key] = {
            "lines": len(lines),
            "words": len(tokens),
            "valence": round(mean(compounds), 4),
            "diversity": round(len(set(content)) / max(1, len(content)), 4),
            "concreteness": round(mean(scores), 3) if scores else 0.0,
            "syllables_per_line": round(mean(syls), 2) if syls else 0.0,
            "words_per_line": round(len(tokens) / len(lines), 2),
        }
    return out


def corpus_hooks(tracks: list[dict], text_key: str = "cleaned_lyrics", top: int = 12) -> list[dict]:
    """Most repeated lines across the corpus — the hooks they lean on."""
    line_counts: Counter = Counter()
    line_songs: dict[str, set] = {}
    display: dict[str, str] = {}
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        for line in _lines(text):
            n = _norm_line(line)
            if not n or len(n.split()) < 3:
                continue
            line_counts[n] += 1
            display.setdefault(n, line)
            line_songs.setdefault(n, set()).add(t.get("title") or "")
    out = []
    for n, c in line_counts.most_common(top * 3):
        if c < 3:
            break
        songs = line_songs.get(n) or set()
        out.append({
            "line": display[n],
            "count": c,
            "songs": len(songs),
            "example": sorted(songs)[0] if songs else "",
        })
        if len(out) >= top:
            break
    return out


def corpus_rhyme_pairs(tracks: list[dict], text_key: str = "cleaned_lyrics", top: int = 15) -> list[dict]:
    """Most-used end-rhyme pairs across the corpus."""
    pair_counts: Counter = Counter()
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        _, pairs = rhyme_stats(_lines(text))
        pair_counts.update(pairs)
    return [
        {"a": a, "b": b, "count": c}
        for (a, b), c in pair_counts.most_common(top)
        if c >= 2
    ]


def pov_profile(tracks: list[dict]) -> dict:
    """Aggregate pronoun mix across the corpus, as share of all pronoun uses."""
    totals = Counter()
    for t in tracks:
        m = t.get("metrics") or {}
        pron = m.get("pronouns") or {}
        for k, v in pron.items():
            totals[k] += v
    s = sum(totals.values())
    if s == 0:
        return {"i": 0, "you": 0, "we": 0, "they": 0, "total": 0}
    return {
        "i": round(totals["i"] / s, 4),
        "you": round(totals["you"] / s, 4),
        "we": round(totals["we"] / s, 4),
        "they": round(totals["they"] / s, 4),
        "total": s,
    }


# ---------- Song structure ----------

_SECTION_HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

_SECTION_CANON = [
    ("pre-chorus", "Pre-Chorus"), ("pre chorus", "Pre-Chorus"),
    ("chorus", "Chorus"), ("refrain", "Chorus"), ("hook", "Chorus"),
    ("verse", "Verse"), ("bridge", "Bridge"), ("intro", "Intro"),
    ("outro", "Outro"), ("interlude", "Interlude"),
    ("instrumental", "Instrumental"), ("solo", "Solo"), ("breakdown", "Bridge"),
]

CHORUS_LABELS = {"Chorus"}


def _canon_section(name: str) -> str | None:
    n = name.lower()
    for key, label in _SECTION_CANON:
        if key in n:
            return label
    return None


def _sections_from_repeated_runs(lines: list[str]) -> list[dict]:
    """Chorus detection for lyrics without stanza breaks: the longest run of
    2+ consecutive lines that repeats (non-overlapping) is the chorus."""
    n = len(lines)
    if n == 0:
        return []
    norm = [_norm_line(l) for l in lines]

    found: tuple[int, list[int]] | None = None
    for L in range(min(10, n // 2), 1, -1):
        grams: dict[tuple, list[int]] = {}
        for i in range(n - L + 1):
            key = tuple(norm[i:i + L])
            if not any(key):
                continue
            grams.setdefault(key, []).append(i)
        candidates = []
        for key, poss in grams.items():
            picked: list[int] = []
            last_end = -1
            for p in poss:
                if p > last_end:
                    picked.append(p)
                    last_end = p + L - 1
            if len(picked) >= 2:
                candidates.append(picked)
        if candidates:
            picked = max(candidates, key=lambda ps: (len(ps), -ps[0]))
            found = (L, picked)
            break

    if not found:
        return [{"label": "Song", "lines": lines}]

    L, starts = found
    chorus_ranges = [(s, s + L) for s in starts]
    sections: list[dict] = []
    pos = 0
    n_choruses_seen = 0
    for ci, (cs, ce) in enumerate(chorus_ranges):
        if pos < cs:
            gap = lines[pos:cs]
            label = "Verse"
            if n_choruses_seen >= 2 and ci == len(chorus_ranges) - 1:
                label = "Bridge"
            elif n_choruses_seen == 0 and len(gap) <= 2:
                label = "Intro"
            sections.append({"label": label, "lines": gap})
        sections.append({"label": "Chorus", "lines": lines[cs:ce]})
        n_choruses_seen += 1
        pos = ce
    if pos < n:
        tail = lines[pos:]
        sections.append({"label": "Outro" if len(tail) <= 2 else "Verse", "lines": tail})
    return sections


def song_structure(raw: str | None, cleaned: str | None) -> dict:
    """Detect song sections.
    Uses [Verse]/[Chorus] headers when the source (Genius) provides them;
    otherwise marks stanzas that repeat (near-)verbatim as choruses.
    Returns {"sections": [{label, lines, words}], "summary", "chorus_share"}."""
    sections: list[dict] = []
    header_lines = (raw or "").split("\n") if raw else []
    has_headers = any(_SECTION_HEADER_RE.match(l) for l in header_lines)

    if has_headers:
        current: dict | None = None
        for l in header_lines:
            m = _SECTION_HEADER_RE.match(l)
            if m:
                label = _canon_section(m.group(1))
                if label is None:
                    # Credit/metadata header like [Produced by ...]; skip it
                    continue
                current = {"label": label, "lines": []}
                sections.append(current)
                continue
            text = l.strip()
            if not text:
                continue
            if current is None:
                current = {"label": "Verse", "lines": []}
                sections.append(current)
            current["lines"].append(text)
        sections = [s for s in sections if s["lines"]]

    if not sections:
        src = cleaned or raw or ""
        stanzas = [s.strip() for s in re.split(r"\n\s*\n", src) if s.strip()]
        if len(stanzas) > 1:
            norm = [" ".join(_tokens(s)) for s in stanzas]
            counts = Counter(norm)
            for s, n in zip(stanzas, norm):
                label = "Chorus" if counts[n] >= 2 and n else "Verse"
                sections.append({"label": label, "lines": [l.strip() for l in s.split("\n") if l.strip()]})
        else:
            # Flat line list (e.g. LRCLIB synced lyrics): find the chorus as a
            # repeated run of consecutive lines.
            sections = _sections_from_repeated_runs(_lines(src))

    # Number repeated verse sections (Verse 1, Verse 2...)
    verse_count = sum(1 for s in sections if s["label"] == "Verse")
    seen_verses = 0
    for s in sections:
        s["words"] = len(_tokens(" ".join(s["lines"])))
        if s["label"] == "Verse" and verse_count > 1:
            seen_verses += 1
            s["label"] = f"Verse {seen_verses}"

    total_words = sum(s["words"] for s in sections) or 1
    chorus_words = sum(
        s["words"] for s in sections if s["label"].split(" ")[0] in CHORUS_LABELS
    )
    summary = " – ".join(s["label"] for s in sections)
    return {
        "sections": sections,
        "summary": summary,
        "chorus_share": round(chorus_words / total_words, 3),
    }


# ---------- POS frequency (kept) ----------

def top_n_by_pos(
    tracks: list[dict],
    text_key: str = "lyrics",
    n: int = 50,
    lang: str = "english",
) -> dict[str, list[tuple[str, int]]]:
    """Return {"noun": [(w, c), ...], "verb": [...], "adjective": [...]}."""
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    except LookupError:
        nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    from nltk import pos_tag

    stop = _stopwords() | VOCALIZATIONS
    noun_tags = {"NN", "NNS", "NNP", "NNPS"}
    verb_tags = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
    adj_tags = {"JJ", "JJR", "JJS"}

    counts: dict[str, Counter] = {"noun": Counter(), "verb": Counter(), "adjective": Counter()}
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        tokens = [w for w in word_tokenize(raw.lower()) if w.isalpha() and w not in stop]
        if not tokens:
            continue
        for w, tag in pos_tag(tokens):
            if tag in noun_tags:
                counts["noun"][w] += 1
            elif tag in verb_tags:
                counts["verb"][w] += 1
            elif tag in adj_tags:
                counts["adjective"][w] += 1
    return {
        "noun": counts["noun"].most_common(n),
        "verb": counts["verb"].most_common(n),
        "adjective": counts["adjective"].most_common(n),
    }


# ---------- Themes (TF-IDF + NMF) ----------

def run_topics(
    tracks: list[dict],
    text_key: str = "lyrics",
    n_topics: int = 6,
) -> tuple[list[str], list[list[tuple[int, float]]], list[int]]:
    """
    Extract themes with TF-IDF + NMF (cleaner than LDA on small lyric corpora).
    Returns (topic_labels, per_track_weights, track_ids).
    """
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = []
    track_ids = []
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        docs.append(raw.lower())
        track_ids.append(t.get("id"))

    if len(docs) < 4:
        return [], [], []
    n_topics = max(2, min(n_topics, len(docs) // 2))

    stop = sorted(_stopwords() | VOCALIZATIONS)
    vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b[a-z][a-z']+\b",
        stop_words=stop,
        min_df=2,
        max_df=0.8,
        max_features=3000,
        sublinear_tf=True,
    )
    try:
        X = vectorizer.fit_transform(docs)
    except ValueError:
        return [], [], []
    if X.shape[1] < n_topics:
        return [], [], []
    vocab = vectorizer.get_feature_names_out()

    nmf = NMF(n_components=n_topics, random_state=42, init="nndsvda", max_iter=400)
    W = nmf.fit_transform(X)  # (n_docs, n_topics)

    topic_labels = []
    for i in range(n_topics):
        top_indices = nmf.components_[i].argsort()[-5:][::-1]
        topic_labels.append(" / ".join(vocab[j] for j in top_indices))

    per_track_weights = []
    for i in range(W.shape[0]):
        row_total = float(W[i].sum()) or 1.0
        row = [(j, float(W[i, j]) / row_total) for j in range(n_topics)]
        row.sort(key=lambda x: -x[1])
        per_track_weights.append(row)

    return topic_labels, per_track_weights, track_ids
```

---

## `./backend/llm.py`

*361 lines*

```python
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


def _extract_json(text: str) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            data = json.loads(m.group(1).strip())
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            pass
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


def _call_chunk(tracks: list[dict], dataset_name: str, chunk_index: int, n_chunks: int) -> dict | None:
    md = build_corpus_markdown(tracks, dataset_name)
    if not md:
        return None
    note = f" (chunk {chunk_index + 1} of {n_chunks})" if n_chunks > 1 else ""
    raw = _call_gemini(_prompt_for_chunk(md, chunk_note=note))
    return _extract_json(raw or "")


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
```

---

## `./frontend/package.json`

*35 lines*

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@radix-ui/react-dialog": "^1.1.15",
    "@radix-ui/react-label": "^2.1.8",
    "@radix-ui/react-slot": "^1.2.4",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.575.0",
    "next": "14.2.35",
    "react": "^18",
    "react-dom": "^18",
    "recharts": "^3.7.0",
    "tailwind-merge": "^3.5.0",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "eslint": "^8",
    "eslint-config-next": "14.2.35",
    "postcss": "^8",
    "tailwindcss": "^3.4.1",
    "typescript": "^5"
  }
}
```

---

## `./frontend/tsconfig.json`

*26 lines*

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## `./frontend/next.config.mjs`

*4 lines*

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {};

export default nextConfig;
```

---

## `./frontend/postcss.config.mjs`

*8 lines*

```javascript
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
  },
};

export default config;
```

---

## `./frontend/tailwind.config.ts`

*63 lines*

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
```

---

## `./frontend/vercel.json`

*5 lines*

```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "installCommand": "npm install"
}
```

---

## `./frontend/components.json`

*23 lines*

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "rtl": false,
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {}
}
```

---

## `./frontend/.eslintrc.json`

*3 lines*

```json
{
  "extends": ["next/core-web-vitals", "next/typescript"]
}
```

---

## `./frontend/.env.local.example`

*9 lines*

```env
# Optional: override API URL (default is production backend)
# NEXT_PUBLIC_API_URL=https://dadass-lyric-master-2000-1.onrender.com
# For local backend: NEXT_PUBLIC_API_URL=http://localhost:8000

# Required for Spotify login (OAuth callback on frontend):
# SPOTIFY_CLIENT_ID=...        (same as backend SPOTIPY_CLIENT_ID)
# SPOTIFY_CLIENT_SECRET=...    (same as backend SPOTIPY_CLIENT_SECRET)
# SPOTIFY_REDIRECT_URI=http://localhost:3000/api/auth/spotify/callback   (local)
# On Vercel: SPOTIFY_REDIRECT_URI=https://your-app.vercel.app/api/auth/spotify/callback
```

---

## `./frontend/app/layout.tsx`

*35 lines*

```tsx
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Dad Ass Lyric Analyzer 3000",
  description: "Lyric analysis and writing tools for any genre",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-950 text-zinc-100`}
      >
        {children}
      </body>
    </html>
  );
}
```

---

## `./frontend/app/page.tsx`

*250 lines*

```tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getStatus, fetchPlaylist, runAnalyze, getAuthStatus, getSpotifyLoginUrl, exchangeSpotifyCode, setSpotifyToken } from "@/lib/api";

export default function DashboardPage() {
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [status, setStatus] = useState<Awaited<ReturnType<typeof getStatus>> | null>(null);
  const [spotifyLoggedIn, setSpotifyLoggedIn] = useState(false);
  const [authChecking, setAuthChecking] = useState(true);
  const [loading, setLoading] = useState<"fetch" | "analyze" | null>(null);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadStatus = async () => {
    try {
      const s = await getStatus();
      setStatus(s);
    } catch {
      setStatus({ has_data: false, track_count: 0, last_analyzed: null, playlist_name: null, image_url: null });
    }
  };

  const loadAuthStatus = async (): Promise<boolean> => {
    try {
      const a = await getAuthStatus();
      setSpotifyLoggedIn(a.spotify);
      return a.spotify;
    } catch {
      setSpotifyLoggedIn(false);
      return false;
    }
  };

  useEffect(() => {
    loadStatus();
    const params = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null;
    const spotifyParam = params?.get("spotify") ?? null;

    if (spotifyParam === "ok") {
      setMessage({ type: "success", text: "Connected to Spotify! You can fetch playlists now." });
      const run = async () => {
        // Read from current URL inside callback so we have it after hydration
        const search = typeof window !== "undefined" ? window.location.search : "";
        const urlParams = search ? new URLSearchParams(search) : null;
        const tokenFromQuery = urlParams?.get("token") ?? null;
        const hash = typeof window !== "undefined" ? window.location.hash.slice(1) : "";
        const hashParams = hash ? new URLSearchParams(hash) : null;
        const tokenFromFragment = hashParams?.get("token") ?? null;
        const token = tokenFromQuery || tokenFromFragment;
        const code = urlParams?.get("code") ?? null;

        if (token) {
          setSpotifyToken(token);
          window.history.replaceState({}, "", window.location.pathname);
        } else if (code) {
          try {
            const { access_token } = await exchangeSpotifyCode(code);
            setSpotifyToken(access_token);
            window.history.replaceState({}, "", window.location.pathname);
          } catch {
            setMessage({ type: "error", text: "Could not complete Spotify connection. Try logging in again." });
            window.history.replaceState({}, "", window.location.pathname);
          }
        } else {
          setMessage({ type: "error", text: "Missing token. Try logging in with Spotify again." });
          window.history.replaceState({}, "", window.location.pathname);
        }
        const ok = await loadAuthStatus();
        setAuthChecking(false);
        if (!ok) {
          setTimeout(() => loadAuthStatus(), 3000);
          setTimeout(() => loadAuthStatus(), 10000);
        }
      };
      run();
      return;
    }
    if (spotifyParam === "auth_denied") {
      window.history.replaceState({}, "", window.location.pathname);
      setMessage({ type: "error", text: "Spotify login was cancelled or denied." });
    } else if (spotifyParam === "exchange_failed" || spotifyParam === "no_token") {
      const reason = params?.get("reason") ?? "";
      window.history.replaceState({}, "", window.location.pathname);
      let text = "Spotify connection failed. Try logging in again.";
      if (reason === "env") {
        text = "Server missing Spotify keys. Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in Vercel → Settings → Environment Variables.";
      } else if (/redirect|mismatch/i.test(decodeURIComponent(reason))) {
        text = "Redirect URI mismatch. In Spotify Dashboard → Edit Settings → Redirect URIs, add exactly: " + (typeof window !== "undefined" ? window.location.origin + "/api/auth/spotify/callback" : "this app’s callback URL");
      }
      setMessage({ type: "error", text });
    }

    loadAuthStatus().finally(() => setAuthChecking(false));
  }, []);

  const onFetch = async () => {
    if (!playlistUrl.trim()) {
      setMessage({ type: "error", text: "Enter a Spotify playlist, album, or artist URL." });
      return;
    }
    setLoading("fetch");
    setMessage(null);
    try {
      await fetchPlaylist(playlistUrl.trim());
      setMessage({ type: "success", text: "Lyrics fetched successfully." });
      await loadStatus();
    } catch (e) {
      const text = e instanceof Error ? e.message : "Fetch failed.";
      setMessage({ type: "error", text });
      if (text.includes("Log in with Spotify") || text.includes("401")) {
        setSpotifyToken(null);
        await loadAuthStatus();
      }
    } finally {
      setLoading(null);
    }
  };

  const onAnalyze = async () => {
    setLoading("analyze");
    setMessage(null);
    try {
      const res = await runAnalyze();
      setMessage({ type: "success", text: res.message || "Analysis complete." });
      await loadStatus();
      if (res.gemini?.status === "running") {
        setMessage({
          type: "success",
          text: (res.message || "Analysis complete.") + " Open Explore — Gemini themes will appear in about a minute.",
        });
      }
    } catch (e) {
      setMessage({ type: "error", text: e instanceof Error ? e.message : "Analysis failed." });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">Dad Ass Lyric Analyzer 3000</h1>
          <p className="text-zinc-400 mt-1">Lyric analysis & writing tools for any genre</p>
        </header>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Data pipeline</CardTitle>
            <CardDescription>Paste a Spotify playlist, album, or artist URL, fetch lyrics, then run analysis. Spotify requires you to log in once to read playlists; albums and artists work without login.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3 items-center">
              {authChecking && (
                <span className="text-zinc-400 text-sm">Checking login…</span>
              )}
              {!authChecking && spotifyLoggedIn && (
                <span className="text-emerald-400 text-sm">Logged in with Spotify</span>
              )}
              <Button variant="outline" className="border-zinc-600" asChild>
                <a href={getSpotifyLoginUrl()} rel="noopener noreferrer">
                  {spotifyLoggedIn ? "Reconnect Spotify" : "Log in with Spotify"}
                </a>
              </Button>
              {!authChecking && !spotifyLoggedIn && (
                <span className="text-zinc-500 text-sm">Required to fetch playlists (not albums/artists)</span>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="playlist-url">Spotify playlist, album, or artist URL</Label>
              <Input
                id="playlist-url"
                placeholder="https://open.spotify.com/playlist/… or /album/… or /artist/…"
                value={playlistUrl}
                onChange={(e) => setPlaylistUrl(e.target.value)}
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={onFetch} disabled={loading !== null} className="bg-rose-600 hover:bg-rose-700">
                {loading === "fetch" ? "Fetching…" : "Fetch lyrics"}
              </Button>
              <Button
                onClick={onAnalyze}
                disabled={loading !== null || !status?.has_data}
                variant="outline"
                className="border-zinc-600"
              >
                {loading === "analyze" ? "Analyzing… (includes Gemini craft pass)" : "Analyze"}
              </Button>
            </div>
            {message && (
              <div className="flex flex-wrap items-center gap-2">
                <p className={message.type === "success" ? "text-emerald-400 text-sm" : "text-rose-400 text-sm"}>
                  {message.text}
                </p>
                {message.type === "error" && /try again|starting up/i.test(message.text) && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="text-zinc-400 hover:text-zinc-200"
                    onClick={async () => {
                      setMessage(null);
                      setAuthChecking(true);
                      await loadAuthStatus();
                      await loadStatus();
                      setAuthChecking(false);
                    }}
                  >
                    Retry
                  </Button>
                )}
              </div>
            )}
            {status && (
              <p className="text-zinc-500 text-sm">
                {status.has_data
                  ? `Fetched ${status.track_count} tracks${status.playlist_name ? ` from “${status.playlist_name}”` : ""}.${status.last_analyzed ? " Analysis complete." : " Run Analyze to see results."}`
                  : "Run fetch first with a playlist, album, or artist URL."}
              </p>
            )}
          </CardContent>
        </Card>

        {status?.has_data && status?.last_analyzed && (
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle>Explore</CardTitle>
              <CardDescription>View visualizations and write in the Lyric Lab.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3">
              <Button asChild variant="outline" className="border-zinc-600">
                <Link href="/explore">Word cloud & sentiment heatmap</Link>
              </Button>
              <Button asChild variant="outline" className="border-zinc-600">
                <Link href="/lyric-lab">Lyric Lab</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
```

---

## `./frontend/app/globals.css`

*81 lines*

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}

@keyframes float-in {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.9);
  }
  to {
    opacity: 1;
  }
}

.animate-float-in {
  animation: float-in 0.45s ease-out both;
}



@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 96.1%;
    --secondary-foreground: 0 0% 9%;
    --muted: 0 0% 96.1%;
    --muted-foreground: 0 0% 45.1%;
    --accent: 0 0% 96.1%;
    --accent-foreground: 0 0% 9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 89.8%;
    --input: 0 0% 89.8%;
    --ring: 0 0% 3.9%;
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
    --chart-3: 197 37% 24%;
    --chart-4: 43 74% 66%;
    --chart-5: 27 87% 67%;
    --radius: 0.5rem;
  }
  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
    --chart-3: 30 80% 55%;
    --chart-4: 280 65% 60%;
    --chart-5: 340 75% 55%;
  }
}
```

---

## `./frontend/app/explore/page.tsx`

*421 lines*

```tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { WordCloud } from "@/components/word-cloud";
import { MoodMeter } from "@/components/mood-meter";
import { StatCards } from "@/components/stat-cards";
import { MoodMap } from "@/components/mood-map";
import { MoodFlow } from "@/components/mood-flow";
import { EmotionGrid } from "@/components/emotion-grid";
import { TopicBubbles } from "@/components/topic-bubbles";
import { SignatureWords, Hooks, RhymePairs, PovProfile } from "@/components/craft-panels";
import { SoundProfilePanel, DictionPanel, SpeechActsPanel, SectionContrastPanel } from "@/components/craft-extra";
import { AlbumBarcode } from "@/components/album-barcode";
import { TrendsChart } from "@/components/trends-chart";
import { TracksPanel } from "@/components/tracks-panel";
import {
  getTopWords,
  getSentimentHeatmap,
  getWordContext,
  getStats,
  getTopics,
  getCraft,
  getTrends,
  getTracks,
  getWordStats,
  getBarcode,
  getStatus,
  type Stats,
  type Topic,
  type Craft,
  type TrendYear,
  type HeatmapTrack,
  type TrackSummary,
  type WordStat,
  type BarcodeTrack,
} from "@/lib/api";

export default function ExplorePage() {
  const [topWords, setTopWords] = useState<{ word: string; count: number }[]>([]);
  const [heatmapTracks, setHeatmapTracks] = useState<HeatmapTrack[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [topicsSource, setTopicsSource] = useState<string | undefined>();
  const [craft, setCraft] = useState<Craft | null>(null);
  const [trendYears, setTrendYears] = useState<TrendYear[]>([]);
  const [trackList, setTrackList] = useState<TrackSummary[]>([]);
  const [wordStats, setWordStats] = useState<Record<string, WordStat>>({});
  const [barcode, setBarcode] = useState<BarcodeTrack[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [contexts, setContexts] = useState<{ line: string; artist: string; title: string }[]>([]);
  const [contextLoading, setContextLoading] = useState(false);
  const [geminiPending, setGeminiPending] = useState(false);

  const loadExploreData = async () => {
    const [wordsRes, heatRes, statsRes, topicsRes, craftRes, trendsRes, tracksRes, wordStatsRes, barcodeRes] =
      await Promise.allSettled([
        getTopWords(undefined, 100),
        getSentimentHeatmap(),
        getStats(),
        getTopics(),
        getCraft(),
        getTrends(),
        getTracks(),
        getWordStats(),
        getBarcode(),
      ]);
    setTopWords(wordsRes.status === "fulfilled" ? wordsRes.value.top_words : []);
    setHeatmapTracks(heatRes.status === "fulfilled" ? heatRes.value.tracks : []);
    setStats(statsRes.status === "fulfilled" && statsRes.value.has_data ? statsRes.value : null);
    setTopics(topicsRes.status === "fulfilled" ? topicsRes.value.topics : []);
    setTopicsSource(topicsRes.status === "fulfilled" ? topicsRes.value.source : undefined);
    setCraft(craftRes.status === "fulfilled" && craftRes.value.has_data ? craftRes.value : null);
    setTrendYears(trendsRes.status === "fulfilled" ? trendsRes.value.years : []);
    setTrackList(tracksRes.status === "fulfilled" ? tracksRes.value.tracks : []);
    setWordStats(wordStatsRes.status === "fulfilled" ? wordStatsRes.value.words : {});
    setBarcode(barcodeRes.status === "fulfilled" ? barcodeRes.value.tracks : []);
  };

  useEffect(() => {
    (async () => {
      setLoading(true);
      await loadExploreData();
      try {
        const st = await getStatus();
        setGeminiPending(st.gemini_status?.status === "running");
      } catch {
        /* ignore */
      }
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    if (!geminiPending) return;
    const id = setInterval(async () => {
      try {
        const st = await getStatus();
        if (st.gemini_status?.status === "running") return;
        setGeminiPending(false);
        await loadExploreData();
      } catch {
        /* ignore */
      }
    }, 5000);
    return () => clearInterval(id);
  }, [geminiPending]);

  const onWordClick = async (word: string) => {
    setSelectedWord(word);
    setContexts([]);
    setContextLoading(true);
    try {
      const res = await getWordContext(word);
      setContexts(res.contexts);
    } catch {
      setContexts([]);
    } finally {
      setContextLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        <header className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-4">
            {stats?.image_url && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={stats.image_url}
                alt=""
                className="w-16 h-16 rounded-lg object-cover border border-zinc-800 shadow-lg"
              />
            )}
            <div>
              <h1 className="text-3xl font-black tracking-tight">Explore</h1>
              <p className="text-zinc-500 text-sm">
                {stats?.name ? (
                  <>
                    Dataset: <span className="text-zinc-300 font-semibold">{stats.name}</span>
                  </>
                ) : (
                  "Visualizations of your lyric dataset."
                )}
              </p>
            </div>
          </div>
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        {loading ? (
          <p className="text-zinc-500">Loading…</p>
        ) : (
          <>
            {geminiPending && (
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
                Gemini craft pass still running… themes and track details will update automatically (usually under a minute).
              </div>
            )}
            <div className="grid lg:grid-cols-5 gap-6">
              <Card className="bg-zinc-900 border-zinc-800 lg:col-span-2">
                <CardHeader>
                  <CardTitle>Overall tone</CardTitle>
                  <CardDescription>How dark or bright the writing reads.</CardDescription>
                </CardHeader>
                <CardContent>
                  {stats ? (
                    <MoodMeter
                      valence={stats.avg_valence ?? 0}
                      intensity={stats.avg_intensity ?? 0}
                      volatility={stats.avg_volatility ?? 0}
                    />
                  ) : (
                    <p className="text-zinc-500 text-sm">Run analysis first.</p>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800 lg:col-span-3">
                <CardHeader>
                  <CardTitle>Highlights</CardTitle>
                  <CardDescription>Standout tracks and dataset totals.</CardDescription>
                </CardHeader>
                <CardContent>
                  {stats ? <StatCards stats={stats} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Tracks &amp; lyrics</CardTitle>
                <CardDescription>
                  Every track with word counts and detected structure. Click one to read the lyrics —
                  hover any word for usage data.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TracksPanel tracks={trackList} wordStats={wordStats} onWordClick={onWordClick} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Word cloud</CardTitle>
                <CardDescription>
                  Filter by part of speech, click a word to see its lyric lines.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <WordCloud words={topWords} onWordClick={onWordClick} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Signature words</CardTitle>
                <CardDescription>
                  The words this writer returns to far more than everyday English does — their fingerprint.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <SignatureWords craft={craft} onWordClick={onWordClick} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Sound &amp; rhyme habits</CardTitle>
                <CardDescription>
                  How the lyrics sound: rhyme types, sound devices, and the consonant palette.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <SoundProfilePanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Show vs tell</CardTitle>
                <CardDescription>
                  Concrete imagery vs abstract ideas, and which senses the writing reaches for.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {craft ? <DictionPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Hooks &amp; repetition</CardTitle>
                  <CardDescription>The most repeated lines in the dataset.</CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <Hooks craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>

              <div className="space-y-6">
                <Card className="bg-zinc-900 border-zinc-800">
                  <CardHeader>
                    <CardTitle>Favorite rhymes</CardTitle>
                    <CardDescription>End-rhyme pairs they reach for most.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {craft ? <RhymePairs craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                  </CardContent>
                </Card>

                <Card className="bg-zinc-900 border-zinc-800">
                  <CardHeader>
                    <CardTitle>Point of view</CardTitle>
                    <CardDescription>Who the songs speak as, and to.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {craft ? <PovProfile craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Speech acts</CardTitle>
                  <CardDescription>
                    What the lines are doing: questions, commands, promises, pleas, accusations…
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <SpeechActsPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Verse vs chorus</CardTitle>
                  <CardDescription>How the writing changes when the chorus hits.</CardDescription>
                </CardHeader>
                <CardContent>
                  {craft ? <SectionContrastPanel craft={craft} /> : <p className="text-zinc-500 text-sm">Run analysis first.</p>}
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Mood map</CardTitle>
                <CardDescription>
                  Each track plotted by valence (dark ↔ bright) and emotional intensity. Bubble size =
                  mood volatility.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <MoodMap tracks={heatmapTracks} />
              </CardContent>
            </Card>

            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Emotional arc</CardTitle>
                  <CardDescription>Valence and intensity across the tracklist.</CardDescription>
                </CardHeader>
                <CardContent>
                  <MoodFlow tracks={heatmapTracks} />
                </CardContent>
              </Card>

              <Card className="bg-zinc-900 border-zinc-800">
                <CardHeader>
                  <CardTitle>Tone heatmap</CardTitle>
                  <CardDescription>Valence, intensity, and volatility for every track.</CardDescription>
                </CardHeader>
                <CardContent>
                  <EmotionGrid tracks={heatmapTracks} />
                </CardContent>
              </Card>
            </div>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Album barcode</CardTitle>
                <CardDescription>
                  Every song line by line — the emotional shape of the whole dataset in one image.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AlbumBarcode tracks={barcode} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Themes</CardTitle>
                <CardDescription>
                  Recurring ideas across the dataset. After Analyze, Gemini names the themes; otherwise
                  TF-IDF + NMF word clusters.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TopicBubbles topics={topics} source={topicsSource} />
              </CardContent>
            </Card>

            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Over the years</CardTitle>
                <CardDescription>
                  How the writing changed by release year: tone, vocabulary range, rhyme habits.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TrendsChart years={trendYears} />
              </CardContent>
            </Card>
          </>
        )}
      </div>

      <Dialog open={!!selectedWord} onOpenChange={(open) => !open && setSelectedWord(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>&ldquo;{selectedWord}&rdquo; in the dataset</DialogTitle>
          </DialogHeader>
          {contextLoading ? (
            <p className="text-zinc-500">Loading…</p>
          ) : contexts.length === 0 ? (
            <p className="text-zinc-500">No contexts found.</p>
          ) : (
            <ul className="space-y-3 text-sm">
              {contexts.map((c, i) => (
                <li key={i} className="border-b border-zinc-800 pb-2">
                  <p className="text-zinc-200 italic">&ldquo;{c.line}&rdquo;</p>
                  <p className="text-zinc-500 mt-1">
                    {c.artist} — {c.title}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

---

## `./frontend/app/lyric-lab/page.tsx`

*125 lines*

```tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getSuggestRhymes, getSuggestThematic, checkCliche } from "@/lib/api";

export default function LyricLabPage() {
  const [text, setText] = useState("");
  const [highlightedWords, setHighlightedWords] = useState<string[]>([]);
  const [suggestWord, setSuggestWord] = useState("");
  const [rhymes, setRhymes] = useState<string[]>([]);
  const [thematic, setThematic] = useState<string[]>([]);
  const [suggestLoading, setSuggestLoading] = useState(false);

  useEffect(() => {
    if (!text.trim()) {
      setHighlightedWords([]);
      return;
    }
    checkCliche(text).then((r) => setHighlightedWords(r.cliche_words)).catch(() => setHighlightedWords([]));
  }, [text]);

  const onSuggest = async () => {
    const w = suggestWord.trim().toLowerCase();
    if (!w) return;
    setSuggestLoading(true);
    try {
      const [rRes, tRes] = await Promise.all([getSuggestRhymes(w), getSuggestThematic(w)]);
      setRhymes(rRes.rhymes || []);
      setThematic(tRes.thematic || []);
    } catch {
      setRhymes([]);
      setThematic([]);
    } finally {
      setSuggestLoading(false);
    }
  };

  const insertWord = (word: string) => {
    setText((prev) => prev + (prev.endsWith(" ") || prev.length === 0 ? "" : " ") + word);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Lyric Lab</h1>
          <Button asChild variant="outline" size="sm" className="border-zinc-600">
            <Link href="/">Back to dashboard</Link>
          </Button>
        </header>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Write lyrics</CardTitle>
            <CardDescription>
              Words that appear in more than 50% of the dataset are highlighted. Use suggestions for rhymes and thematic words.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              className="w-full min-h-[200px] rounded border border-zinc-700 bg-zinc-800 p-3 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-rose-500"
              placeholder="Type your lyrics here…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              spellCheck={false}
            />
            {highlightedWords.length > 0 && (
              <p className="text-sm text-amber-400">
                Overused in dataset (highlighted): {highlightedWords.join(", ")}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900 border-zinc-800">
          <CardHeader>
            <CardTitle>Suggestions</CardTitle>
            <CardDescription>Enter a word to get rhymes and thematic alternatives from the dataset.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2 items-center">
              <input
                type="text"
                className="rounded border border-zinc-700 bg-zinc-800 px-3 py-2 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-rose-500 w-40"
                placeholder="Word"
                value={suggestWord}
                onChange={(e) => setSuggestWord(e.target.value)}
              />
              <Button onClick={onSuggest} disabled={suggestLoading} className="bg-rose-600 hover:bg-rose-700">
                {suggestLoading ? "Loading…" : "Suggest"}
              </Button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Rhymes</h3>
                <div className="flex flex-wrap gap-2">
                  {rhymes.length === 0 && !suggestLoading && <span className="text-zinc-500 text-sm">—</span>}
                  {rhymes.map((w) => (
                    <Button key={w} variant="outline" size="sm" className="border-zinc-600" onClick={() => insertWord(w)}>
                      {w}
                    </Button>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Thematic</h3>
                <div className="flex flex-wrap gap-2">
                  {thematic.length === 0 && !suggestLoading && <span className="text-zinc-500 text-sm">—</span>}
                  {thematic.map((w) => (
                    <Button key={w} variant="outline" size="sm" className="border-zinc-600" onClick={() => insertWord(w)}>
                      {w}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

---

## `./frontend/app/api/auth/spotify/callback/route.ts`

*67 lines*

```typescript
/**
 * Spotify OAuth callback (runs on frontend domain).
 * Receives code from Spotify, exchanges for token, redirects to app with token.
 * Same-origin redirect ensures the token is not stripped by proxies.
 */
import { NextRequest, NextResponse } from "next/server";

const SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const { searchParams } = url;
  const code = searchParams.get("code");
  const error = searchParams.get("error");
  // Must exactly match the redirect_uri used in the authorize step. Prefer the configured
  // value: behind proxies/port-forwards the Host header (url.origin) can differ from the
  // address Spotify actually redirected to (e.g. localhost vs 127.0.0.1).
  const redirectUri = process.env.SPOTIFY_REDIRECT_URI || `${url.origin}${url.pathname}`;
  const baseAppUrl = url.origin;

  if (error || !code) {
    return NextResponse.redirect(`${baseAppUrl}/?spotify=auth_denied`);
  }

  const clientId = process.env.SPOTIFY_CLIENT_ID ?? process.env.SPOTIPY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET ?? process.env.SPOTIPY_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed&reason=env`);
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: redirectUri,
  });
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

  let accessToken: string;
  try {
    const res = await fetch(SPOTIFY_TOKEN_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${auth}`,
      },
      body: body.toString(),
    });
    if (!res.ok) {
      const text = await res.text();
      console.error("Spotify token exchange failed:", res.status, text);
      const reason = encodeURIComponent(res.status === 400 ? "redirect_uri or code mismatch" : `Spotify ${res.status}`);
      return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed&reason=${reason}`);
    }
    const data = (await res.json()) as { access_token?: string };
    const token = data.access_token;
    if (!token) {
      return NextResponse.redirect(`${baseAppUrl}/?spotify=no_token`);
    }
    accessToken = token;
  } catch (e) {
    console.error("Spotify token exchange error:", e);
    return NextResponse.redirect(`${baseAppUrl}/?spotify=exchange_failed`);
  }

  const tokenParam = encodeURIComponent(accessToken);
  return NextResponse.redirect(`${baseAppUrl}/?spotify=ok&token=${tokenParam}`);
}
```

---

## `./frontend/lib/api.ts`

*383 lines*

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://dadass-lyric-master-2000-1.onrender.com";

let spotifyToken: string | null = null;
if (typeof window !== "undefined") {
  try {
    const stored = sessionStorage.getItem("spotify_token");
    if (stored) spotifyToken = stored;
  } catch {
    /* ignore */
  }
}

export function setSpotifyToken(token: string | null) {
  spotifyToken = token;
  try {
    if (typeof window !== "undefined") {
      if (token) sessionStorage.setItem("spotify_token", token);
      else sessionStorage.removeItem("spotify_token");
    }
  } catch {
    /* ignore */
  }
}

/** Sync in-memory token from sessionStorage (e.g. after reload or when chunk loads late). */
function syncTokenFromStorage() {
  if (typeof window === "undefined") return;
  if (spotifyToken) return;
  try {
    const s = sessionStorage.getItem("spotify_token");
    if (s) spotifyToken = s;
  } catch {
    /* ignore */
  }
}

function authHeaders(): Record<string, string> {
  syncTokenFromStorage();
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (spotifyToken) h["Authorization"] = `Bearer ${spotifyToken}`;
  return h;
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      credentials: "include",
      headers: { ...authHeaders(), ...options?.headers },
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Network error";
    if (/failed to fetch|load failed|network error/i.test(msg)) {
      throw new Error("Could not reach the server. If this keeps happening, the backend may be starting up (try again in 30 seconds).");
    }
    throw e;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }
  return res.json();
}

export type Status = {
  has_data: boolean;
  track_count: number;
  last_analyzed: string | null;
  playlist_name: string | null;
  image_url: string | null;
  gemini_enabled?: boolean;
  gemini_status?: { ok?: boolean; status?: string; message?: string; tracks_enriched?: number } | null;
};

export const getSpotifyLoginUrl = () => `${API_BASE}/api/auth/spotify`;

export async function exchangeSpotifyCode(code: string): Promise<{ access_token: string }> {
  const res = await fetch(`${API_BASE}/api/auth/exchange?code=${encodeURIComponent(code)}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
  }
  return res.json();
}

export async function getAuthStatus(): Promise<{ spotify: boolean }> {
  return fetchApi<{ spotify: boolean }>("/api/auth/status");
}

export async function getStatus(): Promise<Status> {
  return fetchApi<Status>("/api/status");
}

export async function fetchPlaylist(playlistUrl: string): Promise<{ ok: boolean; message: string; track_count: number; playlist_id?: string }> {
  return fetchApi("/api/fetch", {
    method: "POST",
    body: JSON.stringify({ playlist_url: playlistUrl }),
  });
}

const ANALYZE_TIMEOUT_MS = 120000;

export async function runAnalyze(): Promise<{
  ok: boolean;
  message: string;
  top_words: { word: string; count: number }[];
  run_id: number;
  gemini?: { ok?: boolean; status?: string; message?: string; tracks_enriched?: number } | null;
}> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ANALYZE_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      credentials: "include",
      headers: authHeaders(),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err));
    }
    return res.json();
  } catch (e) {
    clearTimeout(timeoutId);
    if (e instanceof Error && e.name === "AbortError") {
      throw new Error("Analysis timed out. Gemini craft pass can take a few minutes on larger albums — try again or use a smaller dataset.");
    }
    const msg = e instanceof Error ? e.message : "Network error";
    if (/failed to fetch|load failed|network error/i.test(msg)) {
      throw new Error("Analysis request failed—server may have timed out. Try a smaller playlist or try again in a minute.");
    }
    throw e;
  }
}

export async function getTopWords(pos?: string, limit = 100): Promise<{ top_words: { word: string; count: number }[]; run_id: number | null }> {
  const q = pos ? `?pos=${pos}&limit=${limit}` : `?limit=${limit}`;
  return fetchApi(`/api/top-words${q}`);
}

export type HeatmapTrack = {
  track_index: number;
  title: string;
  artist: string;
  valence: number;
  intensity: number;
  volatility: number;
  release_year: number | null;
};

export async function getSentimentHeatmap(): Promise<{ tracks: HeatmapTrack[] }> {
  return fetchApi("/api/sentiment/heatmap");
}

export type SpeechAct = {
  act: string;
  count: number;
  share: number;
  examples: { line: string; title: string }[];
};

export type SectionStats = {
  lines: number;
  words: number;
  valence: number;
  diversity: number;
  concreteness: number;
  syllables_per_line: number;
  words_per_line: number;
} | null;

export type SoundProfile = {
  syllables_per_line?: number;
  syllable_consistency?: number;
  perfect_rhyme_density?: number;
  slant_rhyme_density?: number;
  internal_rhyme?: number;
  alliteration?: number;
  assonance?: number;
  plosive_ratio?: number;
  sibilant_ratio?: number;
  soft_ratio?: number;
  concreteness?: number;
  pct_concrete?: number;
  pct_abstract?: number;
  sensory_per_100?: number;
  sensory_totals?: Record<string, number>;
};

export type Craft = {
  has_data: boolean;
  signature_words?: { word: string; count: number; songs: number; ratio: number; score: number }[];
  signature_baseline?: string;
  hooks?: { line: string; count: number; songs: number; example: string }[];
  rhyme_pairs?: { a: string; b: string; count: number }[];
  pov?: { i: number; you: number; we: number; they: number; total: number };
  speech_acts?: { total_lines: number; acts: SpeechAct[] };
  sound?: SoundProfile;
  section_contrast?: { verse: SectionStats; chorus: SectionStats };
};

export async function getCraft(): Promise<Craft> {
  return fetchApi("/api/craft");
}

export type TrackSummary = {
  id: number;
  index: number;
  title: string;
  artist: string;
  release_year: number | null;
  album_image: string | null;
  has_lyrics: boolean;
  words: number;
  unique_words: number;
  valence: number;
  intensity: number;
  volatility: number;
  rhyme_density: number;
  repetition: number;
  structure: string;
  chorus_share: number;
};

export async function getTracks(): Promise<{ tracks: TrackSummary[] }> {
  return fetchApi("/api/tracks");
}

export type TrackLine = {
  text: string;
  valence: number;
  act: string;
  act_source?: "gemini" | "rules";
  rhyme_letter: string;
  rhyme_kind: "perfect" | "slant" | null;
  end_word: string;
  line_index?: number;
};

export type TrackMetaphor = {
  phrase: string;
  source: string;
  target: string;
  line: number;
  note: string;
};

export type TrackGemini = {
  available: boolean;
  summary: string;
  metaphors: TrackMetaphor[];
  imagery: Record<string, Record<string, string>>;
};

export type TrackSection = { label: string; lines: TrackLine[]; words: number };

export type TrackDetail = {
  id: number;
  title: string;
  artist: string;
  release_year: number | null;
  album_image: string | null;
  metrics: {
    valence?: number;
    intensity?: number;
    volatility?: number;
    words?: number;
    unique_words?: number;
    diversity?: number;
    repetition?: number;
    rhyme_density?: number;
    perfect_rhyme_density?: number;
    slant_rhyme_density?: number;
    internal_rhyme?: number;
    alliteration?: number;
    assonance?: number;
    syllables_per_line?: number;
    concreteness?: number;
    words_per_line?: number;
  };
  sections: TrackSection[];
  summary: string;
  chorus_share: number;
  gemini?: TrackGemini;
};

export async function getTrack(id: number): Promise<TrackDetail> {
  return fetchApi(`/api/track/${id}`);
}

export type WordStat = { count: number; songs: number; ratio: number; conc?: number };

export async function getWordStats(): Promise<{ words: Record<string, WordStat> }> {
  return fetchApi("/api/word-stats");
}

export type BarcodeTrack = { id: number; title: string; values: number[] };

export async function getBarcode(): Promise<{ tracks: BarcodeTrack[] }> {
  return fetchApi("/api/barcode");
}

export type TrendYear = {
  year: number;
  tracks: number;
  valence: number;
  intensity: number;
  diversity: number;
  words_per_track: number;
  rhyme_density: number;
};

export async function getTrends(): Promise<{ years: TrendYear[] }> {
  return fetchApi("/api/trends");
}

export async function getWordContext(word: string): Promise<{ word: string; contexts: { line: string; artist: string; title: string }[] }> {
  return fetchApi(`/api/word-context?word=${encodeURIComponent(word)}`);
}

export type Topic = {
  id: number;
  label: string;
  description?: string;
  keywords?: string[];
  topic_index: number;
  top_tracks: { title: string; artist: string; weight: number }[];
};

export async function getTopics(): Promise<{ topics: Topic[]; source?: "gemini" | "nmf" | "none" }> {
  return fetchApi("/api/topics");
}

export type Superlative = { title: string; artist: string; value: number } | null;

export type Stats = {
  has_data: boolean;
  name?: string | null;
  image_url?: string | null;
  track_count?: number;
  analyzed_count?: number;
  total_words?: number;
  unique_words?: number;
  avg_words_per_track?: number;
  avg_valence?: number;
  avg_intensity?: number;
  avg_volatility?: number;
  avg_rhyme_density?: number;
  avg_repetition?: number;
  superlatives?: {
    darkest: Superlative;
    brightest: Superlative;
    most_volatile: Superlative;
    biggest_vocabulary: Superlative;
    most_repetitive: Superlative;
    densest_rhymes: Superlative;
  };
};

export async function getStats(): Promise<Stats> {
  return fetchApi("/api/stats");
}

export async function getSuggestRhymes(word: string): Promise<{ word: string; rhymes: string[] }> {
  return fetchApi(`/api/suggest/rhymes?word=${encodeURIComponent(word)}`);
}

export async function getSuggestThematic(word: string): Promise<{ word: string; thematic: string[] }> {
  return fetchApi(`/api/suggest/thematic?word=${encodeURIComponent(word)}`);
}

export async function getClicheWords(): Promise<{ words: string[] }> {
  return fetchApi("/api/cliche-words");
}

export async function checkCliche(text: string): Promise<{ cliche_words: string[] }> {
  return fetchApi("/api/cliche-check", { method: "POST", body: JSON.stringify({ text }) });
}
```

---

## `./frontend/lib/tone.ts`

*29 lines*

```typescript
/** Translate raw tone metrics into 0–100 scales with plain names.
 * Raw valence is −1…+1 (typical lyric corpora sit within ±0.4);
 * intensity/volatility are 0…1 (typically under 0.4). */

const clamp = (v: number) => Math.max(0, Math.min(100, Math.round(v)));

/** 0 = darkest, 50 = neutral, 100 = brightest. */
export const brightness = (valence: number) => clamp(50 + valence * 125);

/** How emotionally charged the language is. 0 = plain description. */
export const heat = (intensity: number) => clamp(intensity * 250);

/** How hard the tone swings line to line. */
export const whiplash = (volatility: number) => clamp(volatility * 250);

export function brightnessLabel(score: number): string {
  if (score >= 65) return "Bright";
  if (score >= 55) return "Warm";
  if (score >= 45) return "Mixed";
  if (score >= 35) return "Somber";
  return "Dark";
}

/** Color for a line/word valence: indigo (dark) through zinc to amber (bright). */
export function valenceColor(valence: number, alpha = 0.85): string {
  if (valence > 0.05) return `rgba(251, 191, 36, ${Math.min(1, 0.15 + valence) * alpha})`;
  if (valence < -0.05) return `rgba(99, 102, 241, ${Math.min(1, 0.15 - valence) * alpha})`;
  return `rgba(113, 113, 122, ${0.25 * alpha})`;
}
```

---

## `./frontend/lib/utils.ts`

*6 lines*

```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

---

## `./frontend/components/tracks-panel.tsx`

*418 lines*

```tsx
"use client";

import { useMemo, useState } from "react";
/* eslint-disable @next/next/no-img-element */
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getTrack, type TrackSummary, type TrackDetail, type TrackLine, type WordStat } from "@/lib/api";
import { brightness, valenceColor } from "@/lib/tone";

const WORD_SPLIT = /([A-Za-z][A-Za-z']*)/;

type Lens = "plain" | "tone" | "concreteness" | "frequency";

const LENSES: { key: Lens; label: string; hint: string }[] = [
  { key: "plain", label: "Plain", hint: "" },
  { key: "tone", label: "Tone", hint: "Line background: indigo = dark, amber = bright." },
  { key: "concreteness", label: "Concrete vs abstract", hint: "Green = concrete image, violet = abstract idea, gray = referential (you, somebody). Uses Gemini when cached from Analyze." },
  { key: "frequency", label: "Their favorites", hint: "Stronger pink = a word this writer uses more across the dataset." },
];

const RHYME_COLORS = [
  "text-rose-300 border-rose-500/40",
  "text-sky-300 border-sky-500/40",
  "text-amber-300 border-amber-500/40",
  "text-emerald-300 border-emerald-500/40",
  "text-violet-300 border-violet-500/40",
  "text-pink-300 border-pink-500/40",
  "text-teal-300 border-teal-500/40",
  "text-orange-300 border-orange-500/40",
];

const ACT_STYLES: Record<string, string> = {
  question: "bg-sky-500/15 text-sky-300",
  command: "bg-orange-500/15 text-orange-300",
  promise: "bg-emerald-500/15 text-emerald-300",
  apology: "bg-violet-500/15 text-violet-300",
  plea: "bg-rose-500/15 text-rose-300",
  accusation: "bg-red-500/15 text-red-300",
  confession: "bg-amber-500/15 text-amber-300",
  exclamation: "bg-pink-500/15 text-pink-300",
};

function dotColor(v: number): string {
  const b = brightness(v);
  if (b > 55) return "bg-amber-400";
  if (b < 45) return "bg-indigo-400";
  return "bg-zinc-500";
}

function concColor(conc: number | undefined): string | undefined {
  if (conc === undefined) return undefined;
  if (conc >= 4) return "#6ee7b7";
  if (conc <= 2.5) return "#c4b5fd";
  return undefined;
}

function imageryColor(role: string | undefined): string | undefined {
  if (role === "concrete") return "#6ee7b7";
  if (role === "abstract") return "#c4b5fd";
  if (role === "referential") return "#71717a";
  return undefined;
}

function HoverableLine({
  line,
  lens,
  stats,
  maxCount,
  geminiImagery,
  onHover,
  onWordClick,
}: {
  line: TrackLine;
  lens: Lens;
  stats: Record<string, WordStat>;
  maxCount: number;
  geminiImagery?: Record<string, string>;
  onHover: (word: string | null, x: number, y: number) => void;
  onWordClick?: (word: string) => void;
}) {
  const parts = line.text.split(WORD_SPLIT);
  return (
    <span>
      {parts.map((part, i) => {
        const key = part.toLowerCase().replace(/^'+|'+$/g, "");
        const stat = i % 2 === 1 ? stats[key] : undefined;
        if (!stat) return <span key={i}>{part}</span>;
        const style: React.CSSProperties = {};
        if (lens === "concreteness") {
          const role = geminiImagery?.[key];
          const c = role ? imageryColor(role) : concColor(stat.conc);
          if (c) style.color = c;
        } else if (lens === "frequency" && stat.count >= 3) {
          const p = Math.log(stat.count) / Math.log(Math.max(2, maxCount));
          style.backgroundColor = `rgba(244, 63, 94, ${0.12 + 0.45 * p})`;
          style.borderRadius = 3;
        }
        return (
          <span
            key={i}
            style={style}
            className="cursor-pointer rounded-sm hover:bg-rose-500/25 hover:text-rose-200"
            onMouseEnter={(e) => onHover(key, e.clientX, e.clientY)}
            onMouseLeave={() => onHover(null, 0, 0)}
            onClick={() => onWordClick?.(key)}
          >
            {part}
          </span>
        );
      })}
    </span>
  );
}

/** Line-by-line self-similarity matrix: choruses appear as bright blocks. */
function SimilarityMatrix({ lines }: { lines: string[] }) {
  const sets = useMemo(
    () => lines.map((l) => new Set(l.toLowerCase().match(/[a-z']+/g) || [])),
    [lines],
  );
  const n = Math.min(sets.length, 80);
  if (n < 6) return null;
  const size = Math.min(280, n * 6);
  const cell = size / n;
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (j > i) continue;
      const a = sets[i];
      const b = sets[j];
      if (!a.size || !b.size) continue;
      let inter = 0;
      a.forEach((w) => {
        if (b.has(w)) inter++;
      });
      const sim = inter / (a.size + b.size - inter);
      if (sim < 0.25) continue;
      cells.push(
        <rect key={`${i}-${j}`} x={j * cell} y={i * cell} width={cell} height={cell} fill={`rgba(244, 63, 94, ${0.25 + sim * 0.75})`} />,
        i !== j ? (
          <rect key={`${j}-${i}`} x={i * cell} y={j * cell} width={cell} height={cell} fill={`rgba(244, 63, 94, ${0.25 + sim * 0.75})`} />
        ) : null,
      );
    }
  }
  return (
    <div className="mt-1">
      <svg width={size} height={size} className="rounded border border-zinc-800 bg-zinc-950">
        {cells}
      </svg>
      <p className="text-[11px] text-zinc-600 mt-1 max-w-[280px]">
        Repetition fingerprint: each pixel compares two lines (top-left = start). Bright blocks =
        repeated sections like choruses.
      </p>
    </div>
  );
}

function MetricChip({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full border border-zinc-700 px-2.5 py-1 text-xs text-zinc-300">
      <span className="text-zinc-500">{label}</span> {value}
    </span>
  );
}

export function TracksPanel({
  tracks,
  wordStats,
  onWordClick,
}: {
  tracks: TrackSummary[];
  wordStats: Record<string, WordStat>;
  onWordClick?: (word: string) => void;
}) {
  const [open, setOpen] = useState<TrackDetail | null>(null);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [hover, setHover] = useState<{ word: string; x: number; y: number } | null>(null);
  const [lens, setLens] = useState<Lens>("plain");
  const maxCount = useMemo(
    () => Math.max(1, ...Object.values(wordStats).map((s) => s.count)),
    [wordStats],
  );

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No tracks. Run fetch first.</p>;

  const openTrack = async (t: TrackSummary) => {
    if (!t.has_lyrics) return;
    setLoadingId(t.id);
    try {
      setOpen(await getTrack(t.id));
    } catch {
      /* ignore */
    } finally {
      setLoadingId(null);
    }
  };

  const onHover = (word: string | null, x: number, y: number) => {
    setHover(word ? { word, x, y } : null);
  };
  const hoverStat = hover ? wordStats[hover.word] : null;

  const allLines = open ? open.sections.flatMap((s) => s.lines.map((l) => l.text)) : [];
  const rhymeLetters = open
    ? Array.from(new Set(open.sections.flatMap((s) => s.lines.map((l) => l.rhyme_letter)).filter(Boolean)))
    : [];
  const letterClass = (letter: string) =>
    RHYME_COLORS[rhymeLetters.indexOf(letter) % RHYME_COLORS.length] || RHYME_COLORS[0];

  return (
    <div>
      <div className="max-h-[420px] overflow-y-auto rounded-lg border border-zinc-800 divide-y divide-zinc-800/70">
        {tracks.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => openTrack(t)}
            disabled={!t.has_lyrics}
            className="w-full text-left px-3 py-2 hover:bg-zinc-800/50 disabled:opacity-40 disabled:cursor-default transition-colors"
          >
            <div className="flex items-center gap-2.5">
              {t.album_image ? (
                <img src={t.album_image} alt="" className="w-8 h-8 rounded object-cover shrink-0" />
              ) : (
                <span className="w-8 h-8 rounded bg-zinc-800 shrink-0" />
              )}
              <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor(t.valence)}`} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold truncate">{t.title}</span>
                  {t.release_year && <span className="text-zinc-600 text-xs shrink-0">{t.release_year}</span>}
                  <span className="ml-auto shrink-0 text-xs text-zinc-500 font-mono">
                    {t.has_lyrics ? `${t.words}w` : "no lyrics"}
                  </span>
                </div>
                {t.has_lyrics && (
                  <p className="text-[11px] text-zinc-500 mt-0.5 truncate">
                    {t.structure || "—"}
                    {t.chorus_share > 0 && ` · chorus carries ${Math.round(t.chorus_share * 100)}% of words`}
                    {loadingId === t.id && " · loading…"}
                  </p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
      <p className="text-[11px] text-zinc-600 mt-2">
        Dot = tone (indigo dark, amber bright). Click a track to read its lyrics with rhyme scheme,
        per-word data, and a repetition fingerprint.
      </p>

      <Dialog open={!!open} onOpenChange={(o) => !o && setOpen(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-h-[85vh] overflow-y-auto max-w-3xl">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  {open.album_image && (
                    <img src={open.album_image} alt="" className="w-10 h-10 rounded object-cover" />
                  )}
                  <span>
                    {open.title}
                    <span className="text-zinc-500 font-normal"> — {open.artist}{open.release_year ? `, ${open.release_year}` : ""}</span>
                  </span>
                </DialogTitle>
              </DialogHeader>
              <div className="flex flex-wrap gap-1.5 mb-1">
                <MetricChip label="words" value={String(open.metrics.words ?? 0)} />
                <MetricChip label="unique" value={String(open.metrics.unique_words ?? 0)} />
                <MetricChip label="brightness" value={`${brightness(open.metrics.valence ?? 0)}/100`} />
                <MetricChip label="syllables/line" value={(open.metrics.syllables_per_line ?? 0).toFixed(1)} />
                <MetricChip
                  label="rhyme"
                  value={`${Math.round(((open.metrics.perfect_rhyme_density ?? 0) + (open.metrics.slant_rhyme_density ?? 0)) * 100)}% (${Math.round((open.metrics.slant_rhyme_density ?? 0) * 100)}% slant)`}
                />
                <MetricChip label="repeated lines" value={`${Math.round((open.metrics.repetition ?? 0) * 100)}%`} />
                {open.chorus_share > 0 && (
                  <MetricChip label="chorus share" value={`${Math.round(open.chorus_share * 100)}%`} />
                )}
              </div>
              {open.summary && <p className="text-xs text-zinc-500 font-mono">{open.summary}</p>}
              {open.gemini?.summary && (
                <p className="text-xs text-emerald-400/90 mt-1 leading-relaxed">{open.gemini.summary}</p>
              )}
              {open.gemini?.metaphors && open.gemini.metaphors.length > 0 && (
                <div className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-3 my-2">
                  <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Metaphors &amp; images</p>
                  <ul className="space-y-2">
                    {open.gemini.metaphors.map((m, i) => (
                      <li key={i} className="text-xs text-zinc-300">
                        <span className="text-rose-300 font-semibold">&ldquo;{m.phrase}&rdquo;</span>
                        {m.source && m.target && (
                          <span className="text-zinc-400"> — {m.source} → {m.target}</span>
                        )}
                        {m.note && <span className="text-zinc-500 block mt-0.5">{m.note}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2 my-2">
                <span className="text-[11px] uppercase tracking-widest text-zinc-500">view:</span>
                {LENSES.map((l) => (
                  <button
                    key={l.key}
                    type="button"
                    onClick={() => setLens(l.key)}
                    className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors ${
                      lens === l.key
                        ? "bg-rose-600 border-rose-600 text-white"
                        : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
              {LENSES.find((l) => l.key === lens)?.hint && (
                <p className="text-[11px] text-zinc-600 mb-2">{LENSES.find((l) => l.key === lens)?.hint}</p>
              )}

              <div className="grid md:grid-cols-[1fr_auto] gap-6">
                <div className="space-y-5 text-sm text-zinc-200">
                  {open.sections.map((s, i) => (
                    <div key={i}>
                      <p className="text-[11px] uppercase tracking-widest text-rose-400/80 font-semibold mb-1">
                        {s.label} <span className="text-zinc-600 normal-case tracking-normal">· {s.words} words</span>
                      </p>
                      {s.lines.map((line, j) => {
                        const lineIdx = line.line_index ?? j;
                        const geminiImagery = open.gemini?.imagery?.[String(lineIdx)];
                        return (
                        <div
                          key={j}
                          className="flex items-baseline gap-2 rounded px-1 -mx-1"
                          style={lens === "tone" ? { backgroundColor: valenceColor(line.valence, 0.25) } : undefined}
                        >
                          <p className="leading-relaxed flex-1">
                            <HoverableLine
                              line={line}
                              lens={lens}
                              stats={wordStats}
                              maxCount={maxCount}
                              geminiImagery={geminiImagery}
                              onHover={onHover}
                              onWordClick={onWordClick}
                            />
                            {line.act !== "statement" && (
                              <span
                                className={`ml-2 align-middle text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded ${ACT_STYLES[line.act] || "bg-zinc-700/40 text-zinc-400"}`}
                                title={line.act_source === "gemini" ? "Sentence-aware (Gemini)" : "Rule-based"}
                              >
                                {line.act}
                              </span>
                            )}
                          </p>
                          {line.rhyme_letter && (
                            <span
                              className={`shrink-0 w-7 text-center text-[10px] font-mono border rounded ${letterClass(line.rhyme_letter)}`}
                              title={line.rhyme_kind === "slant" ? "slant rhyme (vowels match)" : "perfect rhyme"}
                            >
                              {line.rhyme_letter}
                              {line.rhyme_kind === "slant" ? "~" : ""}
                            </span>
                          )}
                        </div>
                      );})}
                    </div>
                  ))}
                  <p className="text-[11px] text-zinc-600">
                    Rhyme scheme: lines sharing a letter rhyme with each other; ~ marks slant rhymes
                    (vowel sounds match, consonants don&apos;t).
                  </p>
                </div>
                <SimilarityMatrix lines={allLines} />
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {hover && hoverStat && (
        <div
          className="fixed z-[60] pointer-events-none rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-xs shadow-xl"
          style={{
            left: Math.min(hover.x + 12, typeof window !== "undefined" ? window.innerWidth - 230 : hover.x),
            top: hover.y + 14,
          }}
        >
          <p className="font-bold text-rose-300">{hover.word}</p>
          <p className="text-zinc-300">
            ×{hoverStat.count} in dataset · {hoverStat.songs} song{hoverStat.songs === 1 ? "" : "s"}
          </p>
          {hoverStat.conc !== undefined && (
            <p className="text-zinc-400">
              {hoverStat.conc >= 4 ? "concrete" : hoverStat.conc <= 2.5 ? "abstract" : "in between"} ({hoverStat.conc}/5)
            </p>
          )}
          <p className="text-zinc-500">
            {hoverStat.ratio >= 2
              ? `${hoverStat.ratio >= 100 ? Math.round(hoverStat.ratio) : hoverStat.ratio}× more than everyday English`
              : hoverStat.ratio <= 0.5
                ? "rarer here than in everyday English"
                : "typical English frequency"}
          </p>
          <p className="text-zinc-600 mt-0.5">click for every lyric line</p>
        </div>
      )}
    </div>
  );
}
```

---

## `./frontend/components/trends-chart.tsx`

*55 lines*

```tsx
"use client";

import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { TrendYear } from "@/lib/api";

function TrendTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: TrendYear }> }) {
  if (!active || !payload?.length) return null;
  const y = payload[0]?.payload;
  if (!y) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">{y.year} · {y.tracks} track{y.tracks === 1 ? "" : "s"}</p>
      <p className="text-amber-300">valence {y.valence >= 0 ? "+" : ""}{y.valence.toFixed(2)}</p>
      <p className="text-sky-400">lexical diversity {(y.diversity * 100).toFixed(0)}%</p>
      <p className="text-violet-400">rhyme density {(y.rhyme_density * 100).toFixed(0)}%</p>
      <p className="text-zinc-400">{y.words_per_track.toFixed(0)} words/track</p>
    </div>
  );
}

export function TrendsChart({ years }: { years: TrendYear[] }) {
  if (years.length < 2)
    return (
      <p className="text-zinc-500 text-sm">
        Release years aren&apos;t available for this dataset — fetch an artist or album to see
        how the writing changed over time.
      </p>
    );

  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={years} margin={{ top: 8, right: 16, bottom: 0, left: -18 }}>
          <XAxis dataKey="year" tick={{ fill: "#71717a", fontSize: 10 }} />
          <YAxis tick={{ fill: "#71717a", fontSize: 10 }} />
          <ReferenceLine y={0} stroke="#3f3f46" />
          <Tooltip content={<TrendTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="valence" name="valence" stroke="#fbbf24" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="diversity" name="lexical diversity" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="rhyme_density" name="rhyme density" stroke="#a78bfa" strokeWidth={2} dot={{ r: 3 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## `./frontend/components/word-cloud.tsx`

*154 lines*

```tsx
"use client";

import { useEffect, useState } from "react";
import { getTopWords } from "@/lib/api";

type WordItem = { word: string; count: number };

const POS_TABS = [
  { key: undefined, label: "Everything" },
  { key: "noun", label: "Nouns" },
  { key: "verb", label: "Verbs" },
  { key: "adjective", label: "Adjectives" },
] as const;

const PALETTE = [
  "text-rose-400 hover:bg-rose-500/20",
  "text-fuchsia-400 hover:bg-fuchsia-500/20",
  "text-violet-400 hover:bg-violet-500/20",
  "text-sky-400 hover:bg-sky-500/20",
  "text-amber-400 hover:bg-amber-500/20",
  "text-emerald-400 hover:bg-emerald-500/20",
  "text-zinc-300 hover:bg-zinc-500/20",
];

/** Deterministic hash so each word keeps its color/tilt across renders. */
function hash(word: string): number {
  let h = 0;
  for (let i = 0; i < word.length; i++) h = (h * 31 + word.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function fontSize(count: number, min: number, max: number): number {
  if (max <= min) return 16;
  const p = Math.sqrt((count - min) / (max - min));
  return Math.round(13 + p * 30);
}

export function WordCloud({
  words,
  onWordClick,
}: {
  words: WordItem[];
  onWordClick?: (word: string) => void;
}) {
  const [pos, setPos] = useState<string | undefined>(undefined);
  const [shown, setShown] = useState<WordItem[]>(words);
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getTopWords(pos, 600)
      .then((res) => !cancelled && setShown(pos === undefined && res.top_words.length === 0 ? words : res.top_words))
      .catch(() => !cancelled && setShown(pos === undefined ? words : []))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [pos, words]);

  if (words.length === 0) return <p className="text-zinc-500 text-sm">No words yet. Run analysis first.</p>;

  const counts = shown.map((w) => w.count);
  const min = counts.length ? Math.min(...counts) : 0;
  const max = counts.length ? Math.max(...counts) : 1;

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4 items-center">
        {POS_TABS.map((tab) => (
          <button
            key={tab.label}
            type="button"
            onClick={() => setPos(tab.key)}
            className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
              pos === tab.key
                ? "bg-rose-600 border-rose-600 text-white"
                : "border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setShowAll(!showAll)}
          className="ml-auto px-3 py-1 rounded-full text-xs font-semibold border border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200 transition-colors"
        >
          {showAll ? "Cloud view" : "Full list"}
        </button>
      </div>
      {loading ? (
        <p className="text-zinc-500 text-sm p-4">Loading…</p>
      ) : shown.length === 0 ? (
        <p className="text-zinc-500 text-sm p-4">Nothing here — run Analyze again to tag parts of speech.</p>
      ) : showAll ? (
        <div>
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search words…"
            className="w-full max-w-xs mb-3 rounded-md bg-zinc-800 border border-zinc-700 px-3 py-1.5 text-sm outline-none focus:border-zinc-500"
          />
          <div className="max-h-[360px] overflow-y-auto rounded-lg border border-zinc-800">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
              {shown
                .filter((w) => !filter || w.word.includes(filter.toLowerCase()))
                .map((w) => (
                  <button
                    key={w.word}
                    type="button"
                    onClick={() => onWordClick?.(w.word)}
                    className="flex justify-between gap-2 px-3 py-1.5 text-sm hover:bg-zinc-800/60 text-left border-b border-r border-zinc-800/50"
                  >
                    <span className="truncate">{w.word}</span>
                    <span className="text-zinc-500 font-mono text-xs">{w.count}</span>
                  </button>
                ))}
            </div>
          </div>
          <p className="text-[11px] text-zinc-600 mt-2">
            All {shown.length} words{pos ? ` tagged as ${pos}s` : ""}, by count. Click one for its lyric lines.
          </p>
        </div>
      ) : (
        <div className="flex flex-wrap gap-x-2 gap-y-1 justify-center items-baseline p-4 min-h-[200px]">
          {shown.slice(0, 80).map((w, i) => {
            const h = hash(w.word);
            const tilt = (h % 5) - 2;
            return (
              <button
                key={w.word}
                type="button"
                title={`“${w.word}” × ${w.count} — click for lyric lines`}
                className={`rounded px-1.5 font-bold leading-tight transition-transform duration-150 hover:scale-125 hover:z-10 animate-float-in ${PALETTE[h % PALETTE.length]}`}
                style={{
                  fontSize: fontSize(w.count, min, max),
                  transform: `rotate(${tilt}deg)`,
                  animationDelay: `${Math.min(i * 18, 900)}ms`,
                }}
                onClick={() => onWordClick?.(w.word)}
              >
                {w.word}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

---

## `./frontend/components/mood-flow.tsx`

*65 lines*

```tsx
"use client";

import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { HeatmapTrack } from "@/lib/api";
import { brightness, heat } from "@/lib/tone";

type Point = HeatmapTrack & { b: number; h: number };

function FlowTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: Point }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">#{t.track_index + 1} {t.title}</p>
      <p className="text-amber-300">brightness {t.b}/100</p>
      <p className="text-rose-400">heat {t.h}/100</p>
    </div>
  );
}

export function MoodFlow({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length < 2) return <p className="text-zinc-500 text-sm">Need at least two tracks for an arc.</p>;
  const points: Point[] = tracks.map((t) => ({ ...t, b: brightness(t.valence), h: heat(t.intensity) }));

  return (
    <div>
      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={points} margin={{ top: 8, right: 16, bottom: 0, left: -22 }}>
            <defs>
              <linearGradient id="grad-bright" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#fbbf24" stopOpacity={0.45} />
                <stop offset="50%" stopColor="#a1a1aa" stopOpacity={0.05} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.45} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="track_index"
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickFormatter={(v: number) => `#${v + 1}`}
            />
            <YAxis domain={[0, 100]} tick={{ fill: "#71717a", fontSize: 10 }} />
            <ReferenceLine y={50} stroke="#3f3f46" />
            <Tooltip content={<FlowTooltip />} />
            <Area type="monotone" dataKey="b" stroke="#fbbf24" fill="url(#grad-bright)" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="h" stroke="#f43f5e" strokeWidth={1.5} dot={false} strokeDasharray="4 3" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[11px] text-zinc-600 mt-1">
        Solid: brightness (above 50 = brighter, below = darker). Dashed: heat.
      </p>
    </div>
  );
}
```

---

## `./frontend/components/album-barcode.tsx`

*44 lines*

```tsx
"use client";

import { useState } from "react";
import type { BarcodeTrack } from "@/lib/api";
import { valenceColor } from "@/lib/tone";

export function AlbumBarcode({ tracks }: { tracks: BarcodeTrack[] }) {
  const [hover, setHover] = useState<string | null>(null);
  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run fetch first.</p>;

  return (
    <div>
      <div className="space-y-1.5">
        {tracks.map((t) => (
          <div
            key={t.id}
            className="flex items-center gap-3"
            onMouseEnter={() => setHover(t.title)}
            onMouseLeave={() => setHover(null)}
          >
            <span className="w-40 shrink-0 text-right text-xs text-zinc-400 truncate">{t.title}</span>
            <div className="flex-1 flex h-6 rounded-sm overflow-hidden bg-zinc-900">
              {t.values.map((v, i) => (
                <div
                  key={i}
                  className="h-full"
                  style={{ width: `${100 / t.values.length}%`, backgroundColor: valenceColor(v, 1) }}
                  title={`line ${i + 1}`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-zinc-500 mt-2 h-4">
        {hover ? (
          <span className="text-zinc-300">{hover}</span>
        ) : (
          "Each row is a song; each stripe is one line, colored by tone (indigo = dark, amber = bright, grey = neutral)."
        )}
      </p>
    </div>
  );
}
```

---

## `./frontend/components/emotion-grid.tsx`

*67 lines*

```tsx
"use client";

import { useMemo, useState } from "react";
import type { HeatmapTrack } from "@/lib/api";
import { brightness, heat, whiplash } from "@/lib/tone";

export function EmotionGrid({ tracks }: { tracks: HeatmapTrack[] }) {
  const [hovered, setHovered] = useState<HeatmapTrack | null>(null);
  const maxH = useMemo(() => Math.max(10, ...tracks.map((t) => heat(t.intensity))), [tracks]);
  const maxW = useMemo(() => Math.max(10, ...tracks.map((t) => whiplash(t.volatility))), [tracks]);

  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  const cellW = tracks.length > 60 ? 8 : tracks.length > 30 ? 14 : 22;

  const rows: { label: string; color: (t: HeatmapTrack) => string }[] = [
    {
      label: "brightness",
      color: (t) => {
        const p = (brightness(t.valence) - 50) / 50; // -1..1
        return p >= 0
          ? `rgba(251, 191, 36, ${0.1 + 0.9 * p})`
          : `rgba(99, 102, 241, ${0.1 + 0.9 * -p})`;
      },
    },
    { label: "heat", color: (t) => `rgba(244, 63, 94, ${0.08 + 0.92 * (heat(t.intensity) / maxH)})` },
    { label: "whiplash", color: (t) => `rgba(52, 211, 153, ${0.08 + 0.92 * (whiplash(t.volatility) / maxW)})` },
  ];

  return (
    <div>
      <div className="overflow-x-auto pb-2">
        <div className="min-w-fit">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center gap-1 mb-1">
              <span className="w-20 shrink-0 text-right pr-2 text-[11px] uppercase tracking-wider text-zinc-500">
                {row.label}
              </span>
              {tracks.map((t) => (
                <button
                  key={`${row.label}-${t.track_index}`}
                  type="button"
                  aria-label={`${t.title} ${row.label}`}
                  onMouseEnter={() => setHovered(t)}
                  onMouseLeave={() => setHovered(null)}
                  className="h-7 rounded-[3px] transition-transform hover:scale-y-125 hover:ring-1 hover:ring-zinc-300"
                  style={{ width: cellW, backgroundColor: row.color(t) }}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
      <p className="text-xs text-zinc-500 h-5 mt-1">
        {hovered ? (
          <>
            <span className="text-zinc-200 font-semibold">{hovered.title}</span>
            {" — "}brightness {brightness(hovered.valence)} · heat {heat(hovered.intensity)} · whiplash{" "}
            {whiplash(hovered.volatility)}
          </>
        ) : (
          "Hover a cell — each column is a track in order. Brightness: indigo = dark, amber = bright."
        )}
      </p>
    </div>
  );
}
```

---

## `./frontend/components/craft-panels.tsx`

*134 lines*

```tsx
"use client";

import type { Craft } from "@/lib/api";

export function SignatureWords({
  craft,
  onWordClick,
}: {
  craft: Craft;
  onWordClick?: (word: string) => void;
}) {
  const words = craft.signature_words ?? [];
  if (words.length === 0)
    return <p className="text-zinc-500 text-sm">Not enough data — fetch a few more songs.</p>;
  const maxScore = Math.max(...words.map((w) => w.score), 0.001);
  return (
    <div>
      <ul className="space-y-1.5">
        {words.slice(0, 18).map((w) => (
          <li key={w.word} className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => onWordClick?.(w.word)}
              className="w-28 shrink-0 text-right font-bold text-rose-300 hover:text-rose-200 hover:underline truncate"
              title={`See lyric lines with “${w.word}”`}
            >
              {w.word}
            </button>
            <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded bg-gradient-to-r from-rose-600 to-amber-500"
                style={{ width: `${Math.max(4, (w.score / maxScore) * 100)}%` }}
              />
            </div>
            <span className="w-52 shrink-0 text-xs text-zinc-500">
              <span className="font-mono text-zinc-300">{w.ratio >= 100 ? Math.round(w.ratio) : w.ratio}×</span> vs{" "}
              {craft.signature_baseline ?? "everyday English"} · {w.songs} song{w.songs === 1 ? "" : "s"}
            </span>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        &ldquo;28×&rdquo; means the word shows up 28 times more often here than in the comparison corpus
        ({craft.signature_baseline ?? "everyday English"}) — a deliberate word choice, not background
        vocabulary. The comparison automatically switches to other artists you&apos;ve fetched once
        enough lyrics accumulate, which filters out generic song words. Click a word to see every line
        it appears in.
      </p>
    </div>
  );
}

export function Hooks({ craft }: { craft: Craft }) {
  const hooks = craft.hooks ?? [];
  if (hooks.length === 0)
    return <p className="text-zinc-500 text-sm">No heavily repeated lines found.</p>;
  return (
    <ul className="space-y-2">
      {hooks.slice(0, 8).map((h, i) => (
        <li key={i} className="flex items-baseline gap-3 border-b border-zinc-800/70 pb-2">
          <span className="shrink-0 font-mono text-amber-400 text-sm">×{h.count}</span>
          <div className="min-w-0">
            <p className="italic text-zinc-200 leading-snug">&ldquo;{h.line}&rdquo;</p>
            <p className="text-[11px] text-zinc-500">
              {h.songs > 1 ? `${h.songs} songs, incl. ` : ""}{h.example}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function RhymePairs({ craft }: { craft: Craft }) {
  const pairs = craft.rhyme_pairs ?? [];
  if (pairs.length === 0)
    return <p className="text-zinc-500 text-sm">No repeated end-rhyme pairs found.</p>;
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {pairs.map((p, i) => (
          <span
            key={i}
            className="px-3 py-1.5 rounded-full border border-violet-500/30 bg-violet-500/10 text-sm"
          >
            <span className="font-bold">{p.a}</span>
            <span className="text-zinc-500 mx-1">/</span>
            <span className="font-bold">{p.b}</span>
            <span className="text-zinc-500 text-xs ml-1.5 font-mono">×{p.count}</span>
          </span>
        ))}
      </div>
      <p className="text-[11px] text-zinc-600 mt-3">
        Perfect end-rhymes within two lines of each other (CMU pronunciation dictionary), counted
        across the whole dataset.
      </p>
    </div>
  );
}

const POV_ROWS = [
  { key: "i" as const, label: "I / me / my", desc: "confessional", color: "bg-rose-500" },
  { key: "you" as const, label: "you / your", desc: "direct address", color: "bg-amber-500" },
  { key: "we" as const, label: "we / us / our", desc: "communal", color: "bg-emerald-500" },
  { key: "they" as const, label: "he / she / they", desc: "narrative", color: "bg-sky-500" },
];

export function PovProfile({ craft }: { craft: Craft }) {
  const pov = craft.pov;
  if (!pov || !pov.total) return <p className="text-zinc-500 text-sm">No pronoun data yet.</p>;
  return (
    <div>
      <div className="flex h-5 rounded-full overflow-hidden mb-4">
        {POV_ROWS.map((r) => (
          <div key={r.key} className={r.color} style={{ width: `${pov[r.key] * 100}%` }} />
        ))}
      </div>
      <ul className="space-y-2">
        {POV_ROWS.map((r) => (
          <li key={r.key} className="flex items-center gap-2 text-sm">
            <span className={`w-2.5 h-2.5 rounded-full ${r.color}`} />
            <span className="w-28 font-semibold">{r.label}</span>
            <span className="font-mono text-zinc-300">{(pov[r.key] * 100).toFixed(0)}%</span>
            <span className="text-zinc-500 text-xs">{r.desc}</span>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        Share of all pronoun uses ({pov.total.toLocaleString()} total). Who the songs are written to —
        and from.
      </p>
    </div>
  );
}
```

---

## `./frontend/components/craft-extra.tsx`

*234 lines*

```tsx
"use client";

import { useState } from "react";
import type { Craft, SectionStats } from "@/lib/api";
import { brightness } from "@/lib/tone";

function Bar({ label, value, max, color, display }: { label: string; value: number; max: number; color: string; display: string }) {
  return (
    <li className="flex items-center gap-3 text-sm">
      <span className="w-36 shrink-0 text-right text-zinc-400">{label}</span>
      <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
        <div className={`h-full rounded ${color}`} style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
      </div>
      <span className="w-16 shrink-0 text-xs font-mono text-zinc-300">{display}</span>
    </li>
  );
}

export function SoundProfilePanel({ craft }: { craft: Craft }) {
  const s = craft.sound;
  if (!s || s.syllables_per_line === undefined)
    return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const pct = (v?: number) => `${Math.round((v ?? 0) * 100)}%`;
  return (
    <div className="grid md:grid-cols-2 gap-x-8 gap-y-5">
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Rhyme &amp; sound devices</p>
        <ul className="space-y-2">
          <Bar label="perfect rhyme" value={s.perfect_rhyme_density ?? 0} max={0.6} color="bg-violet-500" display={pct(s.perfect_rhyme_density)} />
          <Bar label="slant rhyme" value={s.slant_rhyme_density ?? 0} max={0.6} color="bg-violet-400/70" display={pct(s.slant_rhyme_density)} />
          <Bar label="internal rhyme" value={s.internal_rhyme ?? 0} max={0.2} color="bg-fuchsia-500" display={pct(s.internal_rhyme)} />
          <Bar label="alliteration" value={s.alliteration ?? 0} max={0.6} color="bg-sky-500" display={pct(s.alliteration)} />
          <Bar label="assonance" value={s.assonance ?? 0} max={0.6} color="bg-teal-500" display={pct(s.assonance)} />
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          Share of line endings that rhyme (perfect = full sound match, slant = vowels only);
          alliteration = share of lines with repeated starting sounds.
        </p>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Phoneme texture</p>
        <ul className="space-y-2">
          <Bar label="soft (l, m, n, r, w)" value={s.soft_ratio ?? 0} max={0.6} color="bg-emerald-500" display={pct(s.soft_ratio)} />
          <Bar label="plosive (p, b, t, k)" value={s.plosive_ratio ?? 0} max={0.6} color="bg-orange-500" display={pct(s.plosive_ratio)} />
          <Bar label="sibilant (s, z, sh)" value={s.sibilant_ratio ?? 0} max={0.6} color="bg-amber-500" display={pct(s.sibilant_ratio)} />
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          The consonant palette: soft sounds feel gentle, plosives punch, sibilants hiss.
        </p>
        <p className="text-sm text-zinc-300 mt-4">
          <span className="text-zinc-500">syllables per line:</span>{" "}
          <span className="font-mono">{(s.syllables_per_line ?? 0).toFixed(1)}</span>
          <span className="text-zinc-500 ml-3">meter consistency:</span>{" "}
          <span className="font-mono">{Math.round((s.syllable_consistency ?? 0) * 100)}%</span>
        </p>
      </div>
    </div>
  );
}

export function DictionPanel({ craft }: { craft: Craft }) {
  const s = craft.sound;
  if (!s || s.concreteness === undefined)
    return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const sensory = s.sensory_totals || {};
  const maxSense = Math.max(1, ...Object.values(sensory));
  const conc = s.concreteness ?? 0;
  const pos = Math.max(0, Math.min(100, ((conc - 1) / 4) * 100));
  return (
    <div className="grid md:grid-cols-2 gap-x-8 gap-y-5">
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Concrete vs abstract</p>
        <div className="relative h-4 rounded-full bg-gradient-to-r from-violet-500/60 via-zinc-600/50 to-emerald-500/60">
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-6 rounded bg-zinc-100 border border-zinc-400"
            style={{ left: `calc(${pos}% - 6px)` }}
          />
        </div>
        <div className="flex justify-between text-[11px] text-zinc-500 mt-1">
          <span>abstract (ideas)</span>
          <span className="font-mono text-zinc-300">{conc.toFixed(2)} / 5</span>
          <span>concrete (things)</span>
        </div>
        <p className="text-sm text-zinc-300 mt-3">
          <span className="font-mono">{Math.round((s.pct_concrete ?? 0) * 100)}%</span>{" "}
          <span className="text-zinc-500">of content words are concrete,</span>{" "}
          <span className="font-mono">{Math.round((s.pct_abstract ?? 0) * 100)}%</span>{" "}
          <span className="text-zinc-500">abstract.</span>
        </p>
        <p className="text-[11px] text-zinc-600 mt-2">
          Based on the Brysbaert concreteness norms (40k words rated 1–5 by people). Concrete
          writing shows; abstract writing tells.
        </p>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-widest text-zinc-500 mb-2">Sensory language</p>
        <ul className="space-y-2">
          {(["sight", "sound", "touch", "taste", "smell"] as const).map((k) => (
            <Bar
              key={k}
              label={k}
              value={sensory[k] ?? 0}
              max={maxSense}
              color={{ sight: "bg-amber-500", sound: "bg-sky-500", touch: "bg-rose-500", taste: "bg-emerald-500", smell: "bg-violet-500" }[k]}
              display={String(sensory[k] ?? 0)}
            />
          ))}
        </ul>
        <p className="text-[11px] text-zinc-600 mt-2">
          Mentions of each sense across the dataset — which senses this writer reaches for.
        </p>
      </div>
    </div>
  );
}

const ACT_LABELS: Record<string, string> = {
  statement: "statements",
  question: "questions",
  command: "commands",
  exclamation: "exclamations",
  promise: "promises",
  apology: "apologies",
  plea: "pleas",
  accusation: "accusations",
  confession: "confessions",
};

export function SpeechActsPanel({ craft }: { craft: Craft }) {
  const [openAct, setOpenAct] = useState<string | null>(null);
  const sa = craft.speech_acts;
  if (!sa || !sa.acts?.length) return <p className="text-zinc-500 text-sm">Run analysis first.</p>;
  const interesting = sa.acts.filter((a) => a.act !== "statement");
  const statements = sa.acts.find((a) => a.act === "statement");
  const selected = interesting.find((a) => a.act === openAct);
  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-3">
        {interesting.map((a) => (
          <button
            key={a.act}
            type="button"
            onClick={() => setOpenAct(openAct === a.act ? null : a.act)}
            className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
              openAct === a.act
                ? "bg-rose-600 border-rose-600 text-white"
                : "border-zinc-700 text-zinc-300 hover:border-zinc-500"
            }`}
          >
            {ACT_LABELS[a.act] || a.act} <span className="font-mono text-xs opacity-80">×{a.count}</span>
          </button>
        ))}
      </div>
      {selected ? (
        <ul className="space-y-1.5 max-h-64 overflow-y-auto pr-2">
          {selected.examples.map((e, i) => (
            <li key={i} className="text-sm border-b border-zinc-800/60 pb-1.5">
              <span className="italic text-zinc-200">&ldquo;{e.line}&rdquo;</span>
              <span className="text-zinc-500 text-xs ml-2">{e.title}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-zinc-500 text-sm">
          Click a category to read those lines.
          {statements && ` The rest (${Math.round(statements.share * 100)}% of lines) are plain statements.`}
        </p>
      )}
    </div>
  );
}

function ContrastRow({
  label,
  verse,
  chorus,
  format,
}: {
  label: string;
  verse: number;
  chorus: number;
  format: (v: number) => string;
}) {
  const max = Math.max(verse, chorus, 0.0001);
  return (
    <li className="text-sm">
      <p className="text-zinc-400 mb-1">{label}</p>
      <div className="grid grid-cols-2 gap-2 items-center">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
            <div className="h-full bg-sky-500 rounded" style={{ width: `${(verse / max) * 100}%` }} />
          </div>
          <span className="text-xs font-mono w-12 text-zinc-300">{format(verse)}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-3 rounded bg-zinc-800 overflow-hidden">
            <div className="h-full bg-rose-500 rounded" style={{ width: `${(chorus / max) * 100}%` }} />
          </div>
          <span className="text-xs font-mono w-12 text-zinc-300">{format(chorus)}</span>
        </div>
      </div>
    </li>
  );
}

export function SectionContrastPanel({ craft }: { craft: Craft }) {
  const c = craft.section_contrast;
  const verse: SectionStats = c?.verse ?? null;
  const chorus: SectionStats = c?.chorus ?? null;
  if (!verse || !chorus)
    return (
      <p className="text-zinc-500 text-sm">
        Not enough labeled choruses detected in this dataset to compare against verses.
      </p>
    );
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 mb-3 text-center text-[11px] uppercase tracking-widest">
        <p className="text-sky-400">verses · {verse.words.toLocaleString()} words</p>
        <p className="text-rose-400">choruses · {chorus.words.toLocaleString()} words</p>
      </div>
      <ul className="space-y-3">
        <ContrastRow label="Brightness" verse={brightness(verse.valence)} chorus={brightness(chorus.valence)} format={(v) => `${Math.round(v)}`} />
        <ContrastRow label="Vocabulary variety (unique words %)" verse={verse.diversity * 100} chorus={chorus.diversity * 100} format={(v) => `${Math.round(v)}%`} />
        <ContrastRow label="Concreteness (1–5)" verse={verse.concreteness} chorus={chorus.concreteness} format={(v) => v.toFixed(1)} />
        <ContrastRow label="Words per line" verse={verse.words_per_line} chorus={chorus.words_per_line} format={(v) => v.toFixed(1)} />
        <ContrastRow label="Syllables per line" verse={verse.syllables_per_line} chorus={chorus.syllables_per_line} format={(v) => v.toFixed(1)} />
      </ul>
      <p className="text-[11px] text-zinc-600 mt-3">
        How the writing changes when the chorus hits — most writers simplify and brighten.
      </p>
    </div>
  );
}
```

---

## `./frontend/components/stat-cards.tsx`

*87 lines*

```tsx
"use client";

import type { Stats, Superlative } from "@/lib/api";
import { brightness, whiplash } from "@/lib/tone";

function HighlightCard({
  title,
  item,
  format,
  accent,
}: {
  title: string;
  item: Superlative;
  format: (v: number) => string;
  accent: string;
}) {
  if (!item) return null;
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-4 hover:border-zinc-600 hover:-translate-y-0.5 transition-all">
      <p className={`text-[11px] uppercase tracking-widest font-semibold ${accent}`}>{title}</p>
      <p className="font-bold leading-tight mt-2">{item.title}</p>
      <p className="text-xs text-zinc-500 truncate">{item.artist}</p>
      <p className={`text-sm mt-2 font-mono ${accent}`}>{format(item.value)}</p>
    </div>
  );
}

export function StatCards({ stats }: { stats: Stats }) {
  const s = stats.superlatives;
  if (!s) return null;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.track_count?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">tracks</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.total_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">words</p>
        </div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
          <p className="text-2xl font-black">{stats.unique_words?.toLocaleString()}</p>
          <p className="text-xs text-zinc-500">unique words</p>
        </div>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <HighlightCard
          title="Darkest track"
          item={s.darkest}
          format={(v) => `brightness ${brightness(v)}/100`}
          accent="text-indigo-400"
        />
        <HighlightCard
          title="Brightest track"
          item={s.brightest}
          format={(v) => `brightness ${brightness(v)}/100`}
          accent="text-amber-400"
        />
        <HighlightCard
          title="Biggest mood swings"
          item={s.most_volatile}
          format={(v) => `whiplash ${whiplash(v)}/100`}
          accent="text-emerald-400"
        />
        <HighlightCard
          title="Biggest vocabulary"
          item={s.biggest_vocabulary}
          format={(v) => `${v} unique words`}
          accent="text-sky-400"
        />
        <HighlightCard
          title="Most repetitive"
          item={s.most_repetitive}
          format={(v) => `${(v * 100).toFixed(0)}% repeated lines`}
          accent="text-rose-400"
        />
        <HighlightCard
          title="Densest rhymes"
          item={s.densest_rhymes}
          format={(v) => `${(v * 100).toFixed(0)}% line endings rhyme`}
          accent="text-violet-400"
        />
      </div>
    </div>
  );
}
```

---

## `./frontend/components/mood-map.tsx`

*84 lines*

```tsx
"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { HeatmapTrack } from "@/lib/api";
import { brightness, heat, whiplash } from "@/lib/tone";

type Point = HeatmapTrack & { b: number; h: number; w: number };

function MoodTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: Point }> }) {
  if (!active || !payload?.length) return null;
  const t = payload[0]?.payload;
  if (!t) return null;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900/95 px-3 py-2 text-xs shadow-xl">
      <p className="font-bold text-zinc-100">{t.title}</p>
      <p className="text-zinc-500 mb-1">{t.artist}</p>
      <p className="text-amber-300">brightness {t.b}/100</p>
      <p className="text-rose-400">heat {t.h}/100</p>
      <p className="text-emerald-400">whiplash {t.w}/100 (bubble size)</p>
    </div>
  );
}

export function MoodMap({ tracks }: { tracks: HeatmapTrack[] }) {
  if (tracks.length === 0) return <p className="text-zinc-500 text-sm">No data. Run analysis first.</p>;

  const points: Point[] = tracks.map((t) => ({
    ...t,
    b: brightness(t.valence),
    h: heat(t.intensity),
    w: whiplash(t.volatility),
  }));
  const hMax = Math.min(100, Math.max(30, ...points.map((p) => p.h)) * 1.15);

  return (
    <div className="relative">
      <div className="h-[380px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 18, right: 24, bottom: 8, left: -16 }}>
            <XAxis
              type="number"
              dataKey="b"
              domain={[0, 100]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              name="brightness"
              label={{ value: "dark ← brightness → bright", position: "insideBottom", fill: "#a1a1aa", fontSize: 11, dy: 8 }}
            />
            <YAxis
              type="number"
              dataKey="h"
              domain={[0, hMax]}
              tick={{ fill: "#71717a", fontSize: 10 }}
              name="heat"
              label={{ value: "heat →", angle: -90, position: "insideTopLeft", fill: "#a1a1aa", fontSize: 11, dx: 18 }}
            />
            <ZAxis type="number" dataKey="w" range={[40, 420]} name="whiplash" />
            <ReferenceLine x={50} stroke="#3f3f46" strokeDasharray="4 4" />
            <Tooltip content={<MoodTooltip />} cursor={{ strokeDasharray: "3 3", stroke: "#52525b" }} />
            <Scatter data={points} isAnimationActive>
              {points.map((p, i) => {
                const hue = 240 + (p.b / 100) * 120; // indigo (dark) -> amber-ish (bright)
                return <Cell key={i} fill={`hsla(${hue}, 75%, 62%, 0.75)`} stroke="#18181b" />;
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <span className="absolute left-12 top-2 text-[10px] uppercase tracking-widest text-indigo-400/80">dark &amp; charged</span>
      <span className="absolute right-4 top-2 text-[10px] uppercase tracking-widest text-amber-400/80">bright &amp; charged</span>
      <span className="absolute left-12 bottom-12 text-[10px] uppercase tracking-widest text-zinc-500">dark &amp; understated</span>
      <span className="absolute right-4 bottom-12 text-[10px] uppercase tracking-widest text-zinc-500">bright &amp; understated</span>
    </div>
  );
}
```

---

## `./frontend/components/mood-meter.tsx`

*111 lines*

```tsx
"use client";

import { useEffect, useState } from "react";
import { brightness, heat, whiplash, brightnessLabel } from "@/lib/tone";

function polar(cx: number, cy: number, r: number, deg: number) {
  const rad = ((deg - 180) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const s = polar(cx, cy, r, startDeg);
  const e = polar(cx, cy, r, endDeg);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return `M ${s.x.toFixed(2)} ${s.y.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${e.x.toFixed(2)} ${e.y.toFixed(2)}`;
}

export function MoodMeter({
  valence,
  intensity,
  volatility,
}: {
  valence: number;
  intensity: number;
  volatility: number;
}) {
  const b = brightness(valence);
  const [shown, setShown] = useState(50);
  useEffect(() => {
    const t = setTimeout(() => setShown(b), 150);
    return () => clearTimeout(t);
  }, [b]);

  const W = 260;
  const H = 150;
  const CX = W / 2;
  const CY = 130;
  const R = 100;
  const needleDeg = (shown / 100) * 180;
  const tip = polar(CX, CY, R - 18, needleDeg);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[280px]">
        <defs>
          <linearGradient id="tone-arc" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#a1a1aa" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
        </defs>
        <path d={arcPath(CX, CY, R, 0, 180)} fill="none" stroke="url(#tone-arc)" strokeWidth={16} strokeLinecap="round" opacity={0.85} />
        {(["dark", "neutral", "bright"] as const).map((t, i) => {
          const p = polar(CX, CY, R + 14, i * 90);
          return (
            <text key={t} x={p.x} y={p.y} fill="#52525b" fontSize={9} textAnchor="middle">
              {t}
            </text>
          );
        })}
        <line
          x1={CX}
          y1={CY}
          x2={tip.x}
          y2={tip.y}
          stroke="#fafafa"
          strokeWidth={3}
          strokeLinecap="round"
          style={{ transition: "all 1.2s cubic-bezier(.3,1.2,.4,1)" }}
        />
        <circle cx={CX} cy={CY} r={6} fill="#fafafa" />
      </svg>
      <p className="text-4xl font-black tracking-tight -mt-2">
        {b}
        <span className="text-base font-medium text-zinc-500"> / 100</span>
      </p>
      <p className="mt-1 text-lg font-bold bg-gradient-to-r from-indigo-400 via-zinc-300 to-amber-400 bg-clip-text text-transparent">
        {brightnessLabel(b)}
      </p>
      <div className="grid grid-cols-2 gap-3 mt-4 w-full max-w-[260px] text-center">
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{heat(intensity)}<span className="text-xs text-zinc-600">/100</span></p>
          <p className="text-[11px] text-zinc-500">heat</p>
        </div>
        <div className="rounded-lg border border-zinc-800 p-2">
          <p className="text-lg font-bold">{whiplash(volatility)}<span className="text-xs text-zinc-600">/100</span></p>
          <p className="text-[11px] text-zinc-500">whiplash</p>
        </div>
      </div>
      <div className="text-zinc-500 text-[11px] mt-4 space-y-1.5 max-w-[270px]">
        <p>
          <span className="text-zinc-300 font-semibold">Brightness</span> — does the language read
          positive or negative? 50 is neutral; &ldquo;I love it here&rdquo; pushes up,
          &ldquo;everything is ruined&rdquo; pushes down.
        </p>
        <p>
          <span className="text-zinc-300 font-semibold">Heat</span> — how emotionally charged the
          wording is, in either direction. Plain description scores near 0.
        </p>
        <p>
          <span className="text-zinc-300 font-semibold">Whiplash</span> — how hard the tone swings
          from one line to the next. High = bright and dark lines side by side.
        </p>
        <p className="text-zinc-600">
          Every lyric line is scored by the VADER sentiment model, then averaged per song and
          rescaled to 0–100.
        </p>
      </div>
    </div>
  );
}
```

---

## `./frontend/components/topic-bubbles.tsx`

*78 lines*

```tsx
"use client";

import type { Topic } from "@/lib/api";

const GRADIENTS = [
  "from-rose-500/20 to-fuchsia-500/10 border-rose-500/30",
  "from-sky-500/20 to-indigo-500/10 border-sky-500/30",
  "from-amber-500/20 to-orange-500/10 border-amber-500/30",
  "from-emerald-500/20 to-teal-500/10 border-emerald-500/30",
  "from-violet-500/20 to-purple-500/10 border-violet-500/30",
  "from-pink-500/20 to-rose-500/10 border-pink-500/30",
];

export function TopicBubbles({ topics, source }: { topics: Topic[]; source?: string }) {
  if (topics.length === 0)
    return <p className="text-zinc-500 text-sm">No themes yet — run Analyze on a dataset with a few tracks.</p>;

  const isGemini = source === "gemini";

  return (
    <div>
      {isGemini && (
        <p className="text-[11px] text-emerald-400/80 mb-3">
          Named themes from the Gemini craft pass — what this writer keeps returning to across the corpus.
        </p>
      )}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {topics.map((topic, i) => (
          <div
            key={topic.id}
            className={`rounded-xl border bg-gradient-to-br p-4 hover:-translate-y-0.5 transition-transform ${GRADIENTS[i % GRADIENTS.length]}`}
          >
            <p className="text-[11px] uppercase tracking-widest text-zinc-400 mb-2">
              {isGemini ? "theme" : "topic"} #{topic.topic_index + 1}
            </p>
            {isGemini ? (
              <>
                <p className="text-base font-bold text-zinc-100 mb-1">{topic.label}</p>
                {topic.description && (
                  <p className="text-xs text-zinc-400 mb-2 leading-relaxed">{topic.description}</p>
                )}
              </>
            ) : (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {topic.label.split(" / ").map((word) => (
                  <span key={word} className="px-2 py-0.5 rounded-full bg-zinc-950/60 text-sm font-bold">
                    {word}
                  </span>
                ))}
              </div>
            )}
            {(topic.keywords?.length ?? 0) > 0 && isGemini && (
              <div className="flex flex-wrap gap-1 mb-3">
                {topic.keywords!.map((word) => (
                  <span key={word} className="px-2 py-0.5 rounded-full bg-zinc-950/50 text-[11px] text-zinc-300">
                    {word}
                  </span>
                ))}
              </div>
            )}
            {topic.top_tracks?.length > 0 && (
              <ul className="space-y-1">
                {topic.top_tracks.map((t, j) => (
                  <li key={j} className="text-xs text-zinc-400 truncate">
                    {!isGemini && (
                      <span className="text-zinc-600 font-mono mr-1">{Math.round(t.weight * 100)}%</span>
                    )}
                    {t.title}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## `./frontend/components/ui/button.tsx`

*57 lines*

```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline:
          "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

---

## `./frontend/components/ui/card.tsx`

*76 lines*

```tsx
import * as React from "react"

import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-xl border bg-card text-card-foreground shadow",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

---

## `./frontend/components/ui/dialog.tsx`

*122 lines*

```tsx
"use client"

import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 text-center sm:text-left",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
```

---

## `./frontend/components/ui/input.tsx`

*22 lines*

```tsx
import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
```

---

## `./frontend/components/ui/label.tsx`

*26 lines*

```tsx
"use client"

import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const labelVariants = cva(
  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root> &
    VariantProps<typeof labelVariants>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants(), className)}
    {...props}
  />
))
Label.displayName = LabelPrimitive.Root.displayName

export { Label }
```

---
