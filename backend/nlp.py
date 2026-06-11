"""
Craft-focused lyric analysis:
- Tone: per-line VADER sentiment -> valence / intensity / volatility per track
- Repetition: repeated-line ratio and corpus hooks (most repeated lines)
- Rhyme: end-rhyme density and most-used rhyme pairs (CMU pronouncing dictionary)
- Point of view: pronoun profile (I / you / we / they)
- Signature words: corpus usage vs general-English frequency (wordfreq)
- POS-based word frequency
- Themes: TF-IDF + NMF topic extraction
"""
from __future__ import annotations

import math
import re
from collections import Counter
from statistics import mean, pstdev

import nltk
import pronouncing
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordfreq import zipf_frequency

_vader = SentimentIntensityAnalyzer()

_WORD_RE = re.compile(r"[a-z][a-z']*")

# Vocalizations and non-lexical filler — noise for word-choice analysis.
VOCALIZATIONS = {
    "na", "la", "da", "doo", "doot", "oh", "ooh", "oohs", "whoa", "woah", "yeah",
    "hey", "uh", "huh", "mmm", "mm", "hmm", "ah", "aah", "ha", "oo", "ow", "ayy",
    "ay", "yo", "ohh", "ohhh", "woo", "dee", "dum", "bum", "sha", "ba", "bah",
}

PRONOUN_GROUPS = {
    "i": {"i", "me", "my", "mine", "myself", "i'm", "i've", "i'll", "i'd"},
    "you": {"you", "your", "yours", "yourself", "you're", "you've", "you'll", "you'd"},
    "we": {"we", "us", "our", "ours", "ourselves", "we're", "we've", "we'll", "we'd"},
    "they": {
        "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs",
        "he's", "she's", "they're", "they've", "they'll",
    },
}


def _tokens(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _lines(text: str) -> list[str]:
    return [l.strip() for l in text.split("\n") if l.strip()]


def _norm_line(line: str) -> str:
    return " ".join(_tokens(line))


def _rhyme_part(word: str) -> str | None:
    phones = pronouncing.phones_for_word(word)
    if not phones:
        return None
    part = pronouncing.rhyming_part(phones[0])
    return part or None


def rhyme_stats(lines: list[str], window: int = 2) -> tuple[float, list[tuple[str, str]]]:
    """Return (end-rhyme density, rhyme pairs).
    Density = fraction of line endings that perfect-rhyme with another ending
    within `window` lines (among endings the CMU dictionary knows).
    Identical end words don't count as rhymes."""
    enders: list[tuple[str, str | None]] = []
    for line in lines:
        toks = _tokens(line)
        if not toks:
            continue
        w = toks[-1]
        enders.append((w, _rhyme_part(w)))
    known = [(w, p) for w, p in enders if p]
    if len(known) < 2:
        return 0.0, []
    rhymed: set[int] = set()
    pairs: list[tuple[str, str]] = []
    for i in range(len(enders)):
        wi, pi = enders[i]
        if not pi:
            continue
        for j in range(i + 1, min(i + 1 + window, len(enders))):
            wj, pj = enders[j]
            if not pj or wi == wj:
                continue
            if pi == pj:
                rhymed.add(i)
                rhymed.add(j)
                pairs.append(tuple(sorted((wi, wj))))  # type: ignore[arg-type]
    return len(rhymed) / len(known), pairs


def track_metrics(text: str | None) -> dict:
    """Per-track craft metrics. All values are floats/ints; safe for JSON."""
    if not text or not text.strip():
        return {}
    lines = _lines(text)
    tokens = _tokens(text)
    lexical = [t for t in tokens if t not in VOCALIZATIONS]
    if not lines or not tokens:
        return {}

    compounds = [_vader.polarity_scores(l)["compound"] for l in lines]
    valence = mean(compounds)
    intensity = mean(abs(c) for c in compounds)
    volatility = pstdev(compounds) if len(compounds) > 1 else 0.0

    norm = [_norm_line(l) for l in lines]
    norm = [n for n in norm if n]
    line_counts = Counter(norm)
    repetition = 1 - (len(line_counts) / len(norm)) if norm else 0.0

    rhyme_density, _ = rhyme_stats(lines)

    pron = {k: sum(1 for t in tokens if t in group) for k, group in PRONOUN_GROUPS.items()}

    return {
        "valence": round(valence, 4),
        "intensity": round(intensity, 4),
        "volatility": round(volatility, 4),
        "words": len(tokens),
        "unique_words": len(set(lexical)),
        "diversity": round(len(set(lexical)) / len(lexical), 4) if lexical else 0.0,
        "lines": len(lines),
        "words_per_line": round(len(tokens) / len(lines), 2),
        "repetition": round(repetition, 4),
        "rhyme_density": round(rhyme_density, 4),
        "pronouns": pron,
    }


# ---------- Corpus-level craft analysis ----------

def _stopwords() -> set[str]:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords

    return set(stopwords.words("english"))


def signature_words(tracks: list[dict], text_key: str = "cleaned_lyrics", top: int = 30) -> list[dict]:
    """Words this corpus uses far more than everyday English.
    Score = log10 ratio of corpus rate (per billion words) to wordfreq's
    general-English rate. Filtered to words used in 2+ songs."""
    stop = _stopwords() | VOCALIZATIONS
    counts: Counter = Counter()
    song_spread: Counter = Counter()
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        toks = [w for w in _tokens(text) if w not in stop and len(w) > 2 and "'" not in w]
        counts.update(toks)
        song_spread.update(set(toks))

    total = sum(counts.values())
    if total == 0:
        return []
    min_count = max(3, total // 4000)
    out = []
    for word, c in counts.items():
        if c < min_count or song_spread[word] < 2:
            continue
        corpus_zipf = math.log10(c / total * 1e9)
        eng_zipf = zipf_frequency(word, "en")
        if eng_zipf == 0:
            eng_zipf = 1.5  # very rare in general English
        score = corpus_zipf - eng_zipf
        out.append({
            "word": word,
            "count": c,
            "songs": song_spread[word],
            "ratio": round(10 ** score, 1),
            "score": round(score, 3),
        })
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:top]


def corpus_hooks(tracks: list[dict], text_key: str = "cleaned_lyrics", top: int = 12) -> list[dict]:
    """Most repeated lines across the corpus — the hooks they lean on."""
    line_counts: Counter = Counter()
    line_songs: dict[str, set] = {}
    display: dict[str, str] = {}
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        for line in _lines(text):
            n = _norm_line(line)
            if not n or len(n.split()) < 3:
                continue
            line_counts[n] += 1
            display.setdefault(n, line)
            line_songs.setdefault(n, set()).add(t.get("title") or "")
    out = []
    for n, c in line_counts.most_common(top * 3):
        if c < 3:
            break
        songs = line_songs.get(n) or set()
        out.append({
            "line": display[n],
            "count": c,
            "songs": len(songs),
            "example": sorted(songs)[0] if songs else "",
        })
        if len(out) >= top:
            break
    return out


def corpus_rhyme_pairs(tracks: list[dict], text_key: str = "cleaned_lyrics", top: int = 15) -> list[dict]:
    """Most-used end-rhyme pairs across the corpus."""
    pair_counts: Counter = Counter()
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        _, pairs = rhyme_stats(_lines(text))
        pair_counts.update(pairs)
    return [
        {"a": a, "b": b, "count": c}
        for (a, b), c in pair_counts.most_common(top)
        if c >= 2
    ]


def pov_profile(tracks: list[dict]) -> dict:
    """Aggregate pronoun mix across the corpus, as share of all pronoun uses."""
    totals = Counter()
    for t in tracks:
        m = t.get("metrics") or {}
        pron = m.get("pronouns") or {}
        for k, v in pron.items():
            totals[k] += v
    s = sum(totals.values())
    if s == 0:
        return {"i": 0, "you": 0, "we": 0, "they": 0, "total": 0}
    return {
        "i": round(totals["i"] / s, 4),
        "you": round(totals["you"] / s, 4),
        "we": round(totals["we"] / s, 4),
        "they": round(totals["they"] / s, 4),
        "total": s,
    }


# ---------- POS frequency (kept) ----------

def top_n_by_pos(
    tracks: list[dict],
    text_key: str = "lyrics",
    n: int = 50,
    lang: str = "english",
) -> dict[str, list[tuple[str, int]]]:
    """Return {"noun": [(w, c), ...], "verb": [...], "adjective": [...]}."""
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    except LookupError:
        nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    from nltk import pos_tag

    stop = _stopwords() | VOCALIZATIONS
    noun_tags = {"NN", "NNS", "NNP", "NNPS"}
    verb_tags = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
    adj_tags = {"JJ", "JJR", "JJS"}

    counts: dict[str, Counter] = {"noun": Counter(), "verb": Counter(), "adjective": Counter()}
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        tokens = [w for w in word_tokenize(raw.lower()) if w.isalpha() and w not in stop]
        if not tokens:
            continue
        for w, tag in pos_tag(tokens):
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


# ---------- Themes (TF-IDF + NMF) ----------

def run_topics(
    tracks: list[dict],
    text_key: str = "lyrics",
    n_topics: int = 6,
) -> tuple[list[str], list[list[tuple[int, float]]], list[int]]:
    """
    Extract themes with TF-IDF + NMF (cleaner than LDA on small lyric corpora).
    Returns (topic_labels, per_track_weights, track_ids).
    """
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = []
    track_ids = []
    for t in tracks:
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        docs.append(raw.lower())
        track_ids.append(t.get("id"))

    if len(docs) < 4:
        return [], [], []
    n_topics = max(2, min(n_topics, len(docs) // 2))

    stop = sorted(_stopwords() | VOCALIZATIONS)
    vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b[a-z][a-z']+\b",
        stop_words=stop,
        min_df=2,
        max_df=0.8,
        max_features=3000,
        sublinear_tf=True,
    )
    try:
        X = vectorizer.fit_transform(docs)
    except ValueError:
        return [], [], []
    if X.shape[1] < n_topics:
        return [], [], []
    vocab = vectorizer.get_feature_names_out()

    nmf = NMF(n_components=n_topics, random_state=42, init="nndsvda", max_iter=400)
    W = nmf.fit_transform(X)  # (n_docs, n_topics)

    topic_labels = []
    for i in range(n_topics):
        top_indices = nmf.components_[i].argsort()[-5:][::-1]
        topic_labels.append(" / ".join(vocab[j] for j in top_indices))

    per_track_weights = []
    for i in range(W.shape[0]):
        row_total = float(W[i].sum()) or 1.0
        row = [(j, float(W[i, j]) / row_total) for j in range(n_topics)]
        row.sort(key=lambda x: -x[1])
        per_track_weights.append(row)

    return topic_labels, per_track_weights, track_ids
