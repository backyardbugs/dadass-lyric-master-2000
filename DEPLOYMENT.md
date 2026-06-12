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

### Fix the Vercel build error (`package.json` not found)

Vercel is building from the repo root, but `package.json` lives in `frontend/`.

**Do this in Vercel Dashboard → your project → Settings → General:**

1. **Root Directory** → set to `frontend`
2. Save, then redeploy

Alternatively, the repo now includes a root `vercel.json` that runs `cd frontend && npm install` — redeploy after pulling latest `main`.

### Vercel environment variables

| Variable | Example |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-SERVICE.onrender.com` |
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

### Note on `dadass-lyric-master-2000.onrender.com`

The codebase defaults to that URL. If you don't own that Render service, create your own and update `NEXT_PUBLIC_API_URL` on Vercel to match.

---

## After both are deployed

1. Open your **Vercel** URL
2. Fetch an album
3. Analyze (Gemini runs in background ~1 min)
4. Explore → Themes + track lyrics

Check backend health: `https://YOUR-RENDER-URL.onrender.com/api/status`  
Should show `"gemini_enabled": true` and after Analyze `"gemini_status": {"status": "complete", ...}`
