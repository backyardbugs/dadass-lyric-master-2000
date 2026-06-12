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


_phones_cache: dict[str, list[str] | None] = {}


def _phones(word: str) -> list[str] | None:
    """First CMU pronunciation as a phoneme list, cached."""
    if word in _phones_cache:
        return _phones_cache[word]
    plist = pronouncing.phones_for_word(word)
    result = plist[0].split() if plist else None
    _phones_cache[word] = result
    return result


def _rhyme_part(word: str) -> str | None:
    phones = pronouncing.phones_for_word(word)
    if not phones:
        return None
    part = pronouncing.rhyming_part(phones[0])
    return part or None


def _vowel_signature(rhyme_part: str | None) -> str | None:
    """Vowel sounds of the rhyming part, stress stripped — the basis of slant rhyme."""
    if not rhyme_part:
        return None
    vowels = [re.sub(r"\d", "", p) for p in rhyme_part.split() if p[-1].isdigit()]
    return " ".join(vowels) or None


def _syllables(word: str) -> int:
    phones = _phones(word)
    if phones:
        return sum(1 for p in phones if p[-1].isdigit()) or 1
    # Fallback heuristic: vowel groups
    groups = re.findall(r"[aeiouy]+", word.lower())
    return max(1, len(groups))


_PLOSIVES = {"P", "B", "T", "D", "K", "G"}
_SIBILANTS = {"S", "Z", "SH", "ZH", "CH", "JH"}
_SOFT = {"L", "R", "M", "N", "NG", "W", "Y"}  # liquids, nasals, glides


def end_rhyme_scheme(lines: list[str], window: int = 4) -> list[dict]:
    """Per-line end-rhyme info: letter (A, B, ... shared by rhyming lines),
    kind ('perfect' | 'slant' | None), and the end word.
    Lines rhyme if their rhyming parts match exactly (perfect) or share the
    same vowel sounds with different consonants (slant), within `window` lines."""
    enders = []
    for line in lines:
        toks = _tokens(line)
        w = toks[-1] if toks else ""
        part = _rhyme_part(w) if w else None
        enders.append({"word": w, "part": part, "sig": _vowel_signature(part)})

    n = len(enders)
    # Union lines that rhyme within the window
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        parent[find(i)] = find(j)

    kinds: list[str | None] = [None] * n
    for i in range(n):
        ei = enders[i]
        if not ei["sig"]:
            continue
        for j in range(i + 1, min(i + 1 + window, n)):
            ej = enders[j]
            if not ej["sig"] or ei["word"] == ej["word"]:
                continue
            if ei["part"] == ej["part"]:
                union(i, j)
                kinds[i] = kinds[i] or "perfect"
                kinds[j] = kinds[j] or "perfect"
            elif ei["sig"] == ej["sig"]:
                union(i, j)
                kinds[i] = kinds[i] or "slant"
                kinds[j] = kinds[j] or "slant"

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    letters: dict[int, str] = {}
    next_letter = 0
    out = []
    for i in range(n):
        root = find(i)
        letter = ""
        if len(groups[root]) >= 2:
            if root not in letters:
                letters[root] = chr(ord("A") + (next_letter % 26))
                next_letter += 1
            letter = letters[root]
        out.append({"word": enders[i]["word"], "letter": letter, "kind": kinds[i]})
    return out


def sound_metrics(lines: list[str]) -> dict:
    """Sound-level craft metrics: syllables, slant/internal rhyme, alliteration,
    assonance, phoneme texture."""
    if not lines:
        return {}
    # Syllables per line
    syl_counts = []
    for line in lines:
        toks = _tokens(line)
        if toks:
            syl_counts.append(sum(_syllables(w) for w in toks))
    syl_mean = mean(syl_counts) if syl_counts else 0.0
    syl_std = pstdev(syl_counts) if len(syl_counts) > 1 else 0.0

    # End rhymes: perfect vs slant participation
    scheme = end_rhyme_scheme(lines, window=2)
    known = [s for s in scheme if s["word"] and _phones(s["word"])]
    perfect = sum(1 for s in scheme if s["kind"] == "perfect")
    slant = sum(1 for s in scheme if s["kind"] == "slant")
    n_known = max(1, len(known))

    # Internal rhyme: vowel-signature matches between non-identical words inside a line
    internal_pairs = 0
    total_words = 0
    allit_lines = 0
    assonance_scores = []
    class_counts = {"plosive": 0, "sibilant": 0, "soft": 0, "other_consonant": 0}
    for line in lines:
        toks = [w for w in _tokens(line) if len(w) > 2]
        total_words += len(toks)
        sigs = []
        initials = []
        vowel_counts: Counter = Counter()
        n_vowels = 0
        for w in toks:
            part = _rhyme_part(w)
            sigs.append((w, _vowel_signature(part)))
            phones = _phones(w)
            if phones:
                first = re.sub(r"\d", "", phones[0])
                initials.append(first if not phones[0][-1].isdigit() else None)
                for p in phones:
                    base = re.sub(r"\d", "", p)
                    if p[-1].isdigit():
                        vowel_counts[base] += 1
                        n_vowels += 1
                    elif base in _PLOSIVES:
                        class_counts["plosive"] += 1
                    elif base in _SIBILANTS:
                        class_counts["sibilant"] += 1
                    elif base in _SOFT:
                        class_counts["soft"] += 1
                    else:
                        class_counts["other_consonant"] += 1
            else:
                initials.append(None)
        for a in range(len(sigs)):
            for b in range(a + 1, len(sigs)):
                if sigs[a][1] and sigs[a][1] == sigs[b][1] and sigs[a][0] != sigs[b][0]:
                    internal_pairs += 1
        # Alliteration: 2+ nearby words sharing an initial consonant sound
        for a in range(len(initials) - 1):
            windowed = [x for x in initials[a:a + 3] if x]
            if len(windowed) >= 2 and len(set(windowed)) < len(windowed):
                allit_lines += 1
                break
        if n_vowels >= 4 and vowel_counts:
            assonance_scores.append(vowel_counts.most_common(1)[0][1] / n_vowels)

    n_cons = sum(class_counts.values()) or 1
    return {
        "syllables_per_line": round(syl_mean, 2),
        "syllable_consistency": round(max(0.0, 1 - (syl_std / syl_mean)) if syl_mean else 0.0, 3),
        "perfect_rhyme_density": round(perfect / n_known, 4),
        "slant_rhyme_density": round(slant / n_known, 4),
        "internal_rhyme": round(internal_pairs / max(1, total_words), 4),
        "alliteration": round(allit_lines / max(1, len(lines)), 4),
        "assonance": round(mean(assonance_scores), 4) if assonance_scores else 0.0,
        "plosive_ratio": round(class_counts["plosive"] / n_cons, 4),
        "sibilant_ratio": round(class_counts["sibilant"] / n_cons, 4),
        "soft_ratio": round(class_counts["soft"] / n_cons, 4),
    }


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

    metrics = {
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
    metrics.update(sound_metrics(lines))
    metrics.update(diction_metrics(text))
    return metrics


# ---------- Diction: concreteness & sensory language ----------

_CONC_PATH = __import__("pathlib").Path(__file__).resolve().parent / "data" / "concreteness.tsv"
_conc_dict: dict[str, float] | None = None


def _concreteness_dict() -> dict[str, float]:
    """Brysbaert et al. (2014) concreteness norms: 1 (abstract) .. 5 (concrete)."""
    global _conc_dict
    if _conc_dict is None:
        d: dict[str, float] = {}
        try:
            with open(_CONC_PATH, encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) == 2:
                        try:
                            d[parts[0]] = float(parts[1])
                        except ValueError:
                            pass
        except OSError:
            pass
        _conc_dict = d
    return _conc_dict


def concreteness_for(word: str) -> float | None:
    return _concreteness_dict().get(word)


SENSORY_WORDS = {
    "sight": {
        "see", "saw", "seen", "look", "looked", "looking", "watch", "watched", "stare",
        "staring", "eyes", "light", "dark", "darkness", "bright", "shine", "shining",
        "glow", "glowing", "color", "colors", "red", "blue", "green", "white", "black",
        "golden", "pale", "shadow", "shadows", "neon", "blinding", "glitter", "flash",
        "mirror", "moonlight", "sunlight", "sunset", "sunrise", "sky", "stars",
    },
    "sound": {
        "hear", "heard", "listen", "listening", "sound", "sounds", "loud", "quiet",
        "silence", "silent", "scream", "screaming", "whisper", "whispering", "echo",
        "ring", "ringing", "song", "singing", "sang", "noise", "hum", "humming",
        "static", "thunder", "siren", "sirens", "radio", "music", "voice", "voices",
    },
    "touch": {
        "touch", "touched", "feel", "felt", "hold", "holding", "held", "warm", "warmth",
        "cold", "freezing", "burn", "burning", "soft", "rough", "skin", "hands",
        "fingers", "arms", "shiver", "shaking", "trembling", "numb", "ache", "aching",
        "breath", "breathing", "heartbeat", "squeeze", "pull", "push", "kiss", "kissed",
    },
    "taste": {
        "taste", "tasted", "sweet", "bitter", "sour", "salt", "salty", "sugar", "honey",
        "wine", "whiskey", "beer", "coffee", "cigarette", "cigarettes", "smoke", "drink",
        "drinking", "drunk", "tongue", "lips", "mouth", "blood", "poison",
    },
    "smell": {
        "smell", "smells", "scent", "perfume", "cologne", "gasoline", "smoky", "incense",
        "fragrance", "stale", "fresh", "rot", "rotting", "musty",
    },
}


def diction_metrics(text: str) -> dict:
    """Concreteness profile and sensory-language counts."""
    stop = _stopwords()
    tokens = [w for w in _tokens(text) if w not in VOCALIZATIONS]
    content = [w for w in tokens if w not in stop]
    scores = [s for s in (concreteness_for(w) for w in content) if s is not None]
    sensory = {k: sum(1 for w in tokens if w in words) for k, words in SENSORY_WORDS.items()}
    n = max(1, len(tokens))
    return {
        "concreteness": round(mean(scores), 3) if scores else 0.0,
        "pct_concrete": round(sum(1 for s in scores if s >= 4.0) / max(1, len(scores)), 4),
        "pct_abstract": round(sum(1 for s in scores if s <= 2.5) / max(1, len(scores)), 4),
        "sensory_per_100": round(sum(sensory.values()) / n * 100, 2),
        "sensory": sensory,
    }


# ---------- Speech acts ----------

_ACT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("apology", re.compile(r"\b(i'?m sorry|sorry|forgive me|i apologi[sz]e|my fault)\b", re.I)),
    ("promise", re.compile(r"\b(i('| wi)ll always|i('| wi)ll never|i swear|i promise|i('| wi)ll be there|never gonna|i won'?t ever|till the day i die)\b", re.I)),
    ("plea", re.compile(r"\b(please|i('m| am) begg?ing|don'?t leave|don'?t go|stay with me|come back|i need you)\b", re.I)),
    ("accusation", re.compile(r"\b(you never|you always|you lied|you don'?t even|how could you|you made me|it'?s your fault|you said you)\b", re.I)),
    ("confession", re.compile(r"\b(i'?ve been|i never told|truth is|the truth is|i confess|i admit|honestly,? i|i gotta admit)\b", re.I)),
]

_QUESTION_STARTS = re.compile(
    r"^(what|when|where|why|who|how|do|does|did|am|are|is|was|were|will|would|can|could|should|have|has|had)\s+(i|you|we|they|he|she|it|this|that)\b",
    re.I,
)

_IMPERATIVE_STARTS = {
    "come", "hold", "take", "tell", "let", "stop", "wait", "listen", "look", "remember",
    "forget", "stay", "go", "run", "give", "leave", "save", "call", "say", "keep",
    "close", "open", "turn", "wake", "don't", "dont", "put", "throw", "show", "kiss",
    "drive", "meet", "bring", "follow", "breathe", "hang",
}


def classify_speech_act(line: str) -> str:
    """Primary speech act of a lyric line, by transparent rules."""
    stripped = line.strip()
    lowered = stripped.lower()
    for act, pattern in _ACT_PATTERNS:
        if pattern.search(lowered):
            return act
    if stripped.endswith("?") or _QUESTION_STARTS.match(lowered):
        return "question"
    first = (_tokens(lowered) or [""])[0]
    if first in _IMPERATIVE_STARTS or lowered.startswith("don't "):
        return "command"
    if stripped.endswith("!"):
        return "exclamation"
    return "statement"


def speech_acts_profile(tracks: list[dict], text_key: str = "cleaned_lyrics", max_examples: int = 40) -> dict:
    """Corpus speech-act counts with example lines per act."""
    counts: Counter = Counter()
    examples: dict[str, list[dict]] = {}
    total = 0
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        seen_in_track: set[str] = set()
        for line in _lines(text):
            n = _norm_line(line)
            if not n:
                continue
            act = classify_speech_act(line)
            total += 1
            counts[act] += 1
            key = f"{act}:{n}"
            if act != "statement" and key not in seen_in_track:
                seen_in_track.add(key)
                bucket = examples.setdefault(act, [])
                if len(bucket) < max_examples and not any(e["line"].lower() == line.lower() for e in bucket):
                    bucket.append({"line": line, "title": t.get("title") or ""})
    return {
        "total_lines": total,
        "acts": [
            {
                "act": act,
                "count": counts[act],
                "share": round(counts[act] / max(1, total), 4),
                "examples": examples.get(act, []),
            }
            for act, _ in counts.most_common()
        ],
    }


def line_valence(line: str) -> float:
    return _vader.polarity_scores(line)["compound"]


# ---------- Corpus-level craft analysis ----------

def _stopwords() -> set[str]:
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords

    return set(stopwords.words("english"))


def _corpus_counts(tracks: list[dict], text_key: str = "cleaned_lyrics") -> tuple[Counter, Counter]:
    """(word counts, song spread) for content words, vocalizations excluded."""
    stop = _stopwords() | VOCALIZATIONS
    counts: Counter = Counter()
    song_spread: Counter = Counter()
    for t in tracks:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        toks = [w for w in _tokens(text) if w not in stop and len(w) > 2 and "'" not in w]
        counts.update(toks)
        song_spread.update(set(toks))
    return counts, song_spread


def signature_words(
    tracks: list[dict],
    text_key: str = "cleaned_lyrics",
    top: int = 30,
    baseline_counts: Counter | None = None,
) -> dict:
    """Words this corpus over-uses. If baseline_counts (word counts from other
    lyrics) is provided and substantial, rank by log-odds with an informative
    Dirichlet prior (Monroe et al.) against that lyrics baseline — this filters
    out generic 'song words'. Otherwise fall back to comparing against
    general-English frequencies (wordfreq)."""
    counts, song_spread = _corpus_counts(tracks, text_key)
    total = sum(counts.values())
    if total == 0:
        return {"baseline": "none", "words": []}
    min_count = max(3, total // 4000)

    use_lyrics_baseline = baseline_counts is not None and sum(baseline_counts.values()) >= 20000
    out = []
    if use_lyrics_baseline:
        bg_total = sum(baseline_counts.values())
        prior_total = 500.0  # strength of the prior, in pseudo-words
        for word, c in counts.items():
            if c < min_count or song_spread[word] < 2:
                continue
            a_w = prior_total * (baseline_counts[word] + 0.5) / bg_total
            y1, n1 = c, total
            y2, n2 = baseline_counts[word], bg_total
            d = math.log((y1 + a_w) / (n1 + prior_total - y1 - a_w)) - math.log(
                (y2 + a_w) / (n2 + prior_total - y2 - a_w)
            )
            var = 1.0 / (y1 + a_w) + 1.0 / (y2 + a_w)
            z = d / math.sqrt(var)
            rate1 = c / total
            rate2 = (y2 + 0.5) / bg_total
            out.append({
                "word": word,
                "count": c,
                "songs": song_spread[word],
                "ratio": round(rate1 / rate2, 1),
                "score": round(z, 3),
            })
    else:
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
    return {
        "baseline": "other artists you've fetched" if use_lyrics_baseline else "everyday English",
        "words": out[:top],
    }


def section_contrast(tracks: list[dict]) -> dict:
    """Verse vs chorus craft comparison across the corpus."""
    buckets: dict[str, dict] = {
        "verse": {"lines": [], "tokens": []},
        "chorus": {"lines": [], "tokens": []},
    }
    for t in tracks:
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics"))
        for s in st.get("sections", []):
            base = s["label"].split(" ")[0].lower()
            key = "chorus" if base == "chorus" else ("verse" if base in ("verse", "song") else None)
            if key is None:
                continue
            buckets[key]["lines"].extend(s["lines"])
            buckets[key]["tokens"].extend(_tokens(" ".join(s["lines"])))

    out = {}
    stop = _stopwords()
    for key, b in buckets.items():
        lines, tokens = b["lines"], b["tokens"]
        if not lines or not tokens:
            out[key] = None
            continue
        compounds = [line_valence(l) for l in lines]
        content = [w for w in tokens if w not in stop and w not in VOCALIZATIONS]
        scores = [s for s in (concreteness_for(w) for w in content) if s is not None]
        syls = [sum(_syllables(w) for w in _tokens(l)) for l in lines if _tokens(l)]
        out[key] = {
            "lines": len(lines),
            "words": len(tokens),
            "valence": round(mean(compounds), 4),
            "diversity": round(len(set(content)) / max(1, len(content)), 4),
            "concreteness": round(mean(scores), 3) if scores else 0.0,
            "syllables_per_line": round(mean(syls), 2) if syls else 0.0,
            "words_per_line": round(len(tokens) / len(lines), 2),
        }
    return out


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


# ---------- Song structure ----------

_SECTION_HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

_SECTION_CANON = [
    ("pre-chorus", "Pre-Chorus"), ("pre chorus", "Pre-Chorus"),
    ("chorus", "Chorus"), ("refrain", "Chorus"), ("hook", "Chorus"),
    ("verse", "Verse"), ("bridge", "Bridge"), ("intro", "Intro"),
    ("outro", "Outro"), ("interlude", "Interlude"),
    ("instrumental", "Instrumental"), ("solo", "Solo"), ("breakdown", "Bridge"),
]

CHORUS_LABELS = {"Chorus"}


def _canon_section(name: str) -> str | None:
    n = name.lower()
    for key, label in _SECTION_CANON:
        if key in n:
            return label
    return None


def _sections_from_repeated_runs(lines: list[str]) -> list[dict]:
    """Chorus detection for lyrics without stanza breaks: the longest run of
    2+ consecutive lines that repeats (non-overlapping) is the chorus."""
    n = len(lines)
    if n == 0:
        return []
    norm = [_norm_line(l) for l in lines]

    found: tuple[int, list[int]] | None = None
    for L in range(min(10, n // 2), 1, -1):
        grams: dict[tuple, list[int]] = {}
        for i in range(n - L + 1):
            key = tuple(norm[i:i + L])
            if not any(key):
                continue
            grams.setdefault(key, []).append(i)
        candidates = []
        for key, poss in grams.items():
            picked: list[int] = []
            last_end = -1
            for p in poss:
                if p > last_end:
                    picked.append(p)
                    last_end = p + L - 1
            if len(picked) >= 2:
                candidates.append(picked)
        if candidates:
            picked = max(candidates, key=lambda ps: (len(ps), -ps[0]))
            found = (L, picked)
            break

    if not found:
        return [{"label": "Song", "lines": lines}]

    L, starts = found
    chorus_ranges = [(s, s + L) for s in starts]
    sections: list[dict] = []
    pos = 0
    n_choruses_seen = 0
    for ci, (cs, ce) in enumerate(chorus_ranges):
        if pos < cs:
            gap = lines[pos:cs]
            label = "Verse"
            if n_choruses_seen >= 2 and ci == len(chorus_ranges) - 1:
                label = "Bridge"
            elif n_choruses_seen == 0 and len(gap) <= 2:
                label = "Intro"
            sections.append({"label": label, "lines": gap})
        sections.append({"label": "Chorus", "lines": lines[cs:ce]})
        n_choruses_seen += 1
        pos = ce
    if pos < n:
        tail = lines[pos:]
        sections.append({"label": "Outro" if len(tail) <= 2 else "Verse", "lines": tail})
    return sections


def song_structure(raw: str | None, cleaned: str | None) -> dict:
    """Detect song sections.
    Uses [Verse]/[Chorus] headers when the source (Genius) provides them;
    otherwise marks stanzas that repeat (near-)verbatim as choruses.
    Returns {"sections": [{label, lines, words}], "summary", "chorus_share"}."""
    sections: list[dict] = []
    header_lines = (raw or "").split("\n") if raw else []
    has_headers = any(_SECTION_HEADER_RE.match(l) for l in header_lines)

    if has_headers:
        current: dict | None = None
        for l in header_lines:
            m = _SECTION_HEADER_RE.match(l)
            if m:
                label = _canon_section(m.group(1))
                if label is None:
                    # Credit/metadata header like [Produced by ...]; skip it
                    continue
                current = {"label": label, "lines": []}
                sections.append(current)
                continue
            text = l.strip()
            if not text:
                continue
            if current is None:
                current = {"label": "Verse", "lines": []}
                sections.append(current)
            current["lines"].append(text)
        sections = [s for s in sections if s["lines"]]

    if not sections:
        src = cleaned or raw or ""
        stanzas = [s.strip() for s in re.split(r"\n\s*\n", src) if s.strip()]
        if len(stanzas) > 1:
            norm = [" ".join(_tokens(s)) for s in stanzas]
            counts = Counter(norm)
            for s, n in zip(stanzas, norm):
                label = "Chorus" if counts[n] >= 2 and n else "Verse"
                sections.append({"label": label, "lines": [l.strip() for l in s.split("\n") if l.strip()]})
        else:
            # Flat line list (e.g. LRCLIB synced lyrics): find the chorus as a
            # repeated run of consecutive lines.
            sections = _sections_from_repeated_runs(_lines(src))

    # Number repeated verse sections (Verse 1, Verse 2...)
    verse_count = sum(1 for s in sections if s["label"] == "Verse")
    seen_verses = 0
    for s in sections:
        s["words"] = len(_tokens(" ".join(s["lines"])))
        if s["label"] == "Verse" and verse_count > 1:
            seen_verses += 1
            s["label"] = f"Verse {seen_verses}"

    total_words = sum(s["words"] for s in sections) or 1
    chorus_words = sum(
        s["words"] for s in sections if s["label"].split(" ")[0] in CHORUS_LABELS
    )
    summary = " – ".join(s["label"] for s in sections)
    return {
        "sections": sections,
        "summary": summary,
        "chorus_share": round(chorus_words / total_words, 3),
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
