"""
Fetch pipeline: Spotify playlist -> Genius lyrics.
Callable from FastAPI or CLI. Does not write to DB; returns list[dict].
"""
from __future__ import annotations

import os
import re
import time
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
    if not url or not url.strip():
        return None
    url = url.strip()
    if re.match(r"^[a-zA-Z0-9]{22}$", url):
        return url
    m = re.search(r"spotify:playlist:([a-zA-Z0-9]{22})", url)
    if m:
        return m.group(1)
    m = re.search(r"open\.spotify\.com/playlist/([a-zA-Z0-9]{22})", url)
    if m:
        return m.group(1)
    return None


def get_spotify_tracks(playlist_id: str, access_token: str | None = None) -> list[dict]:
    """Fetch all tracks from a Spotify playlist. Use access_token (OAuth) for any playlist; else client credentials (public only, may 403)."""
    if access_token:
        auth = _TokenAuth(access_token)
        sp = Spotify(auth_manager=auth)
        market = None
    else:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env")
        auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = Spotify(auth_manager=auth)
        market = os.getenv("SPOTIFY_MARKET", "US")
    tracks = []
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


_LRCLIB_UA = "EmoAlmanac/0.1.0"


def _fetch_lyrics_lrclib(artist: str, title: str) -> str | None:
    """Fetch plain lyrics from LRCLIB (free, no key, no scraping). Fallback when Genius is blocked."""
    headers = {"User-Agent": _LRCLIB_UA}
    # Spotify joins multiple artists with ", "; LRCLIB usually indexes the primary artist.
    primary_artist = artist.split(",")[0].strip()
    try:
        r = requests.get(
            "https://lrclib.net/api/get",
            params={"artist_name": primary_artist, "track_name": title},
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            lyrics = (r.json().get("plainLyrics") or "").strip()
            if lyrics:
                return lyrics
        # Fuzzy search fallback for slight title/artist mismatches
        r = requests.get(
            "https://lrclib.net/api/search",
            params={"artist_name": primary_artist, "track_name": title},
            headers=headers,
            timeout=10,
        )
        if r.status_code == 200:
            for item in r.json() or []:
                lyrics = (item.get("plainLyrics") or "").strip()
                if lyrics:
                    return lyrics
    except Exception:
        pass
    return None


def fetch_lyrics_for_tracks(tracks: list[dict], genius_token: str | None = None) -> list[dict]:
    """For each track, search Genius (falling back to LRCLIB) and attach lyrics.
    Returns list of {artist, title, spotify_id, lyrics}."""
    token = genius_token or os.getenv("GENIUS_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Set GENIUS_ACCESS_TOKEN in .env")
    genius = Genius(token)
    genius.remove_section_headers = True
    genius.skip_non_songs = True
    results = []
    for i, t in enumerate(tracks):
        if i > 0:
            time.sleep(0.4)
        artist, title = t["artist"], t["title"]
        lyrics = None
        try:
            song = genius.search_song(title, artist)
            if song and getattr(song, "lyrics", None):
                lyrics = song.lyrics.strip()
        except Exception:
            # Genius page scraping is often blocked (Cloudflare) from datacenter IPs
            pass
        if not lyrics:
            lyrics = _fetch_lyrics_lrclib(artist, title)
        results.append({
            "spotify_id": t.get("spotify_id"),
            "artist": artist,
            "title": title,
            "lyrics": lyrics,
        })
    return results


def fetch_playlist(playlist_url: str, spotify_access_token: str | None = None) -> list[dict]:
    """
    Full fetch: parse URL -> Spotify tracks -> Genius lyrics.
    Use spotify_access_token (from OAuth) to read any playlist; without it, client credentials may 403.
    Returns list of {artist, title, spotify_id, lyrics}.
    """
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        raise ValueError("Invalid playlist URL or ID")
    tracks = get_spotify_tracks(playlist_id, access_token=spotify_access_token)
    if not tracks:
        raise ValueError("Playlist is empty or could not be read")
    return fetch_lyrics_for_tracks(tracks)


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
