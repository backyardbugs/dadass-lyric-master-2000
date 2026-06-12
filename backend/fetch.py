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
