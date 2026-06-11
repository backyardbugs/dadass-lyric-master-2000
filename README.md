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
   - `NEXT_PUBLIC_API_URL` = your backend URL (e.g. `https://dadass-lyric-master-2000.onrender.com`).
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
