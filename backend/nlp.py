"""
NLP: sentiment (sadness, anger, nostalgia), POS-based frequency, topic modeling.
"""
from __future__ import annotations

from collections import Counter
import re

import nltk
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Minimal emotion word lists (expandable). Scale to 0-1 by presence/count.
SADNESS_WORDS = {
    "sad", "lonely", "cry", "tears", "miss", "gone", "lost", "empty", "broken",
    "heart", "hurt", "pain", "alone", "dark", "bleed", "die", "death", "goodbye",
    "leave", "left", "never", "nothing", "nowhere", "end", "fall", "falling",
}
ANGER_WORDS = {
    "hate", "angry", "mad", "rage", "fight", "burn", "scream", "kill", "blood",
    "wrong", "lie", "lies", "fake", "break", "destroy", "war", "fire", "hell",
}
NOSTALGIA_WORDS = {
    "remember", "memories", "back", "again", "used", "old", "time", "days",
    "summer", "winter", "home", "hometown", "street", "house", "yesterday",
    "childhood", "young", "first", "last", "never", "forever", "always",
}


def _normalize(t: str) -> str:
    return t.lower().strip() if t else ""


def sentiment_scores(text: str | None) -> tuple[float, float, float]:
    """
    Return (sadness, anger, nostalgia) in 0-1 range.
    Uses word-list counts normalized by text length; caps at 1.
    """
    if not text or not text.strip():
        return 0.0, 0.0, 0.0
    text = _normalize(text)
    tokens = [w for w in word_tokenize(text) if w.isalpha()]
    if not tokens:
        return 0.0, 0.0, 0.0
    n = len(tokens)
    sad = sum(1 for w in tokens if w in SADNESS_WORDS) / max(n, 1)
    ang = sum(1 for w in tokens if w in ANGER_WORDS) / max(n, 1)
    nos = sum(1 for w in tokens if w in NOSTALGIA_WORDS) / max(n, 1)
    # Cap at 1 and scale so typical values span 0-0.5
    return min(1.0, sad * 3), min(1.0, ang * 3), min(1.0, nos * 3)


def top_n_by_pos(
    tracks: list[dict],
    text_key: str = "lyrics",
    n: int = 50,
    lang: str = "english",
) -> dict[str, list[tuple[str, int]]]:
    """
    Return {"noun": [(w, c), ...], "verb": [...], "adjective": [...]}.
    Uses NLTK pos_tag; map Penn tags to noun/verb/adjective.
    """
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    except LookupError:
        nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    from nltk.corpus import stopwords
    from nltk import pos_tag

    stop = set(stopwords.words(lang))
    # Penn tag set: NN*, VB*, JJ*
    noun_tags = {"NN", "NNS", "NNP", "NNPS"}
    verb_tags = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
    adj_tags = {"JJ", "JJR", "JJS"}

    counts: dict[str, Counter] = {"noun": Counter(), "verb": Counter(), "adjective": Counter()}
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        tokens = [w for w in word_tokenize(_normalize(raw)) if w.isalpha() and w not in stop]
        if not tokens:
            continue
        tagged = pos_tag(tokens)
        for w, tag in tagged:
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


def run_lda(
    tracks: list[dict],
    text_key: str = "lyrics",
    n_topics: int = 6,
    max_df: float = 0.95,
    min_df: int = 1,
) -> tuple[list[str], list[list[tuple[int, float]]], list[int]]:
    """
    Run LDA on cleaned lyrics (one doc per track). Returns (topic_labels, per_track_weights, track_ids).
    topic_labels: list of strings (top 3 words per topic).
    per_track_weights: list of list of (topic_index, weight) for each track (same order as track_ids).
    track_ids: list of track ids for each doc (same order as per_track_weights).
    """
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    docs = []
    track_ids = []
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        docs.append(_normalize(raw))
        track_ids.append(t.get("id"))

    if len(docs) < 2 or n_topics >= len(docs):
        return [], [], []

    vectorizer = CountVectorizer(max_df=max_df, min_df=min_df, stop_words="english", max_features=2000)
    X = vectorizer.fit_transform(docs)
    vocab = vectorizer.get_feature_names_out()
    n_topics = min(n_topics, X.shape[1] - 1, X.shape[0] - 1)
    if n_topics < 1:
        return [], [], []

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20)
    W = lda.fit_transform(X)  # (n_docs, n_topics)

    # Label each topic by top 3 words
    topic_labels = []
    for i in range(n_topics):
        top_indices = lda.components_[i].argsort()[-3:][::-1]
        words = [vocab[j] for j in top_indices]
        topic_labels.append(" / ".join(words))

    # Per-doc weights (only for docs we included)
    per_track_weights = []
    for i in range(W.shape[0]):
        row = [(j, float(W[i, j])) for j in range(n_topics)]
        row.sort(key=lambda x: -x[1])
        per_track_weights.append(row)

    return topic_labels, per_track_weights, track_ids
