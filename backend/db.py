"""
SQLite schema and helpers for The Emo Almanac.
Database file: data/emo_almanac.db
"""
from __future__ import annotations

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
        conn.commit()
    finally:
        conn.close()


def insert_playlist(playlist_id: str, name: str | None = None) -> int:
    """Insert or replace playlist; return playlist table id."""
    conn = get_connection()
    try:
        fetched_at = datetime.utcnow().isoformat() + "Z"
        conn.execute(
            "INSERT INTO playlist (playlist_id, name, fetched_at) VALUES (?, ?, ?)"
            " ON CONFLICT(playlist_id) DO UPDATE SET name=excluded.name, fetched_at=excluded.fetched_at",
            (playlist_id, name or "", fetched_at),
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
                """INSERT INTO track (playlist_id, artist, title, spotify_id, raw_lyrics, cleaned_lyrics)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    playlist_pk,
                    t["artist"],
                    t["title"],
                    t.get("spotify_id"),
                    t.get("raw_lyrics") or t.get("lyrics"),
                    t.get("cleaned_lyrics"),
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
            "SELECT id, artist, title, raw_lyrics, cleaned_lyrics, sentiment_sadness, sentiment_anger, sentiment_nostalgia FROM track WHERE playlist_id = ? ORDER BY id",
            (playlist_pk,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "artist": r["artist"],
                "title": r["title"],
                "raw_lyrics": r["raw_lyrics"],
                "cleaned_lyrics": r["cleaned_lyrics"],
                "lyrics": r["cleaned_lyrics"] or r["raw_lyrics"],
                "sentiment_sadness": r["sentiment_sadness"],
                "sentiment_anger": r["sentiment_anger"],
                "sentiment_nostalgia": r["sentiment_nostalgia"],
            }
            for r in rows
        ]
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
            "SELECT id, playlist_id, name, fetched_at FROM playlist WHERE id = ?",
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


def update_track_sentiment(track_id: int, sadness: float, anger: float, nostalgia: float) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE track SET sentiment_sadness=?, sentiment_anger=?, sentiment_nostalgia=? WHERE id=?",
            (sadness, anger, nostalgia, track_id),
        )
        conn.commit()
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
