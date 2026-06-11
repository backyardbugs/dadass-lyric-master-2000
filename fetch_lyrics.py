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
