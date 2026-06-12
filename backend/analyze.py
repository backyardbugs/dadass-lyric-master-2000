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
