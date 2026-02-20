"""
analyze.py — The Emo Almanac NLP Pipeline (Phase 1)

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
