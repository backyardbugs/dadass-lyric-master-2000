"""
analyze.py — CLI word-frequency helper (uses metrics.py, no NLTK).

Usage:
    python analyze.py [path_to_raw_lyrics.json]
"""

import json
import sys
from collections import Counter
from pathlib import Path

from backend.metrics import stopwords, tokens

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_RAW_PATH = DATA_DIR / "raw_lyrics.json"


def load_raw_lyrics(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of track objects")
    return data


def top_n_words_from_tracks(tracks: list[dict], n: int = 50) -> list[tuple[str, int]]:
    stop = stopwords()
    all_tokens: list[str] = []
    for entry in tracks:
        text = entry.get("lyrics") or entry.get("cleaned_lyrics") or entry.get("raw_lyrics") or ""
        if isinstance(text, str) and text.strip():
            all_tokens.extend(tokens(text))
    filtered = [w for w in all_tokens if w not in stop]
    return Counter(filtered).most_common(n)


def main() -> None:
    raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RAW_PATH
    if not raw_path.exists():
        print(f"File not found: {raw_path}")
        print("Run fetch_lyrics.py first, or pass a path to raw_lyrics.json")
        sys.exit(1)
    tracks = load_raw_lyrics(raw_path)
    print(f"Loaded {len(tracks)} tracks from {raw_path}")
    top50 = top_n_words_from_tracks(tracks, n=50)
    print("\n--- Top 50 words (excluding stopwords) ---\n")
    for i, (word, count) in enumerate(top50, 1):
        print(f"{i:3}. {word:20} {count}")


if __name__ == "__main__":
    main()
