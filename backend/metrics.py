"""
Deterministic lyric metrics — no NLTK, VADER, or sklearn.
Rhyme/syllable math via CMU pronouncing; tokenization via regex.
"""
from __future__ import annotations

import re
from collections import Counter
from statistics import mean, pstdev

import pronouncing

# Contractions preserved: ain't, don't, i'm
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']+")

VOCALIZATIONS = {
    "na", "la", "da", "doo", "doot", "oh", "ooh", "oohs", "whoa", "woah", "yeah",
    "hey", "uh", "huh", "mmm", "mm", "hmm", "ah", "aah", "ha", "oo", "ow", "ayy",
    "ay", "yo", "ohh", "ohhh", "woo", "dee", "dum", "bum", "sha", "ba", "bah",
}

GENERIC_INDEFINITES = {
    "somebody", "someone", "something", "somewhere", "anybody", "anyone",
    "anything", "anywhere", "nobody", "nothing", "nowhere", "everybody",
    "everyone", "everything", "everywhere", "thing", "things", "stuff",
    "one", "ones", "way", "time", "times",
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

# Compact English stopword set (replaces NLTK corpora)
ENGLISH_STOPWORDS = frozenset({
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves",
})

_PLOSIVES = {"P", "B", "T", "D", "K", "G"}
_SIBILANTS = {"S", "Z", "SH", "ZH", "CH", "JH"}
_SOFT = {"L", "R", "M", "N", "NG", "W", "Y"}

_SECTION_HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
_SECTION_CANON = [
    ("pre-chorus", "Pre-Chorus"), ("pre chorus", "Pre-Chorus"),
    ("chorus", "Chorus"), ("refrain", "Chorus"), ("hook", "Chorus"),
    ("verse", "Verse"), ("bridge", "Bridge"), ("intro", "Intro"),
    ("outro", "Outro"), ("interlude", "Interlude"),
    ("instrumental", "Instrumental"), ("solo", "Solo"), ("breakdown", "Bridge"),
]
CHORUS_LABELS = {"Chorus"}

_phones_cache: dict[str, list[str] | None] = {}


def tokens(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def lines(text: str) -> list[str]:
    return [l.strip() for l in text.split("\n") if l.strip()]


def norm_line(line: str) -> str:
    return " ".join(tokens(line))


def stopwords() -> set[str]:
    return set(ENGLISH_STOPWORDS)


def _phones(word: str) -> list[str] | None:
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
    if not rhyme_part:
        return None
    vowels = [re.sub(r"\d", "", p) for p in rhyme_part.split() if p[-1].isdigit()]
    return " ".join(vowels) or None


def syllables(word: str) -> int:
    phones = _phones(word)
    if phones:
        return sum(1 for p in phones if p[-1].isdigit()) or 1
    groups = re.findall(r"[aeiouy]+", word.lower())
    return max(1, len(groups))


def end_rhyme_scheme(line_list: list[str], window: int = 4) -> list[dict]:
    enders = []
    for line in line_list:
        toks = tokens(line)
        w = toks[-1] if toks else ""
        part = _rhyme_part(w) if w else None
        enders.append({"word": w, "part": part, "sig": _vowel_signature(part)})

    n = len(enders)
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


def rhyme_stats(line_list: list[str], window: int = 2) -> tuple[float, list[tuple[str, str]]]:
    enders: list[tuple[str, str | None]] = []
    for line in line_list:
        toks = tokens(line)
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


def sound_metrics(line_list: list[str]) -> dict:
    if not line_list:
        return {}
    syl_counts = []
    for line in line_list:
        toks = tokens(line)
        if toks:
            syl_counts.append(sum(syllables(w) for w in toks))
    syl_mean = mean(syl_counts) if syl_counts else 0.0
    syl_std = pstdev(syl_counts) if len(syl_counts) > 1 else 0.0

    scheme = end_rhyme_scheme(line_list, window=2)
    known = [s for s in scheme if s["word"] and _phones(s["word"])]
    perfect = sum(1 for s in scheme if s["kind"] == "perfect")
    slant = sum(1 for s in scheme if s["kind"] == "slant")
    n_known = max(1, len(known))

    internal_pairs = 0
    total_words = 0
    allit_lines = 0
    assonance_scores = []
    class_counts = {"plosive": 0, "sibilant": 0, "soft": 0, "other_consonant": 0}
    for line in line_list:
        toks = [w for w in tokens(line) if len(w) > 2]
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
        "alliteration": round(allit_lines / max(1, len(line_list)), 4),
        "assonance": round(mean(assonance_scores), 4) if assonance_scores else 0.0,
        "plosive_ratio": round(class_counts["plosive"] / n_cons, 4),
        "sibilant_ratio": round(class_counts["sibilant"] / n_cons, 4),
        "soft_ratio": round(class_counts["soft"] / n_cons, 4),
    }


def track_metrics(text: str | None) -> dict:
    """Per-track deterministic metrics. Valence fields are 0 until Semantic Engine (Phase 2)."""
    if not text or not text.strip():
        return {}
    line_list = lines(text)
    toks = tokens(text)
    lexical = [t for t in toks if t not in VOCALIZATIONS]
    if not line_list or not toks:
        return {}

    norm = [norm_line(l) for l in line_list]
    norm = [n for n in norm if n]
    line_counts = Counter(norm)
    repetition = 1 - (len(line_counts) / len(norm)) if norm else 0.0
    rhyme_density, _ = rhyme_stats(line_list)
    pron = {k: sum(1 for t in toks if t in group) for k, group in PRONOUN_GROUPS.items()}

    metrics = {
        "valence": 0.0,
        "intensity": 0.0,
        "volatility": 0.0,
        "words": len(toks),
        "unique_words": len(set(lexical)),
        "diversity": round(len(set(lexical)) / len(lexical), 4) if lexical else 0.0,
        "lines": len(line_list),
        "words_per_line": round(len(toks) / len(line_list), 2),
        "repetition": round(repetition, 4),
        "rhyme_density": round(rhyme_density, 4),
        "pronouns": pron,
    }
    metrics.update(sound_metrics(line_list))
    return metrics


def line_valence(line: str) -> float:
    """Placeholder until Semantic Engine provides 0–100 valence (Phase 2)."""
    return 0.0


def tokenize_lyrics(lyrics_list: list[dict], text_key: str = "lyrics") -> list[str]:
    all_text = []
    for entry in lyrics_list:
        raw = entry.get(text_key) or entry.get("cleaned_lyrics") or entry.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        all_text.append(raw.lower().strip())
    return tokens(" ".join(all_text))


def top_n_words(tok_list: list[str], n: int = 50) -> list[tuple[str, int]]:
    stop = stopwords()
    filtered = [w for w in tok_list if w not in stop]
    return Counter(filtered).most_common(n)


def build_word_contexts(track_list: list[dict], text_key: str = "lyrics") -> list[tuple[str, int, str]]:
    result = []
    for t in track_list:
        track_id = t.get("id")
        if track_id is None:
            continue
        raw = t.get(text_key) or t.get("cleaned_lyrics") or t.get("raw_lyrics")
        if not raw or not isinstance(raw, str):
            continue
        for line in raw.splitlines():
            normalized = line.lower().strip()
            if not normalized:
                continue
            for w in tokens(normalized):
                result.append((w, track_id, normalized))
    return result


def _canon_section(name: str) -> str | None:
    n = name.lower()
    for key, label in _SECTION_CANON:
        if key in n:
            return label
    return None


def _sections_from_repeated_runs(line_list: list[str]) -> list[dict]:
    n = len(line_list)
    if n == 0:
        return []
    norm = [norm_line(l) for l in line_list]
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
        return [{"label": "Song", "lines": line_list}]
    L, starts = found
    chorus_ranges = [(s, s + L) for s in starts]
    sections: list[dict] = []
    pos = 0
    n_choruses_seen = 0
    for ci, (cs, ce) in enumerate(chorus_ranges):
        if pos < cs:
            gap = line_list[pos:cs]
            label = "Verse"
            if n_choruses_seen >= 2 and ci == len(chorus_ranges) - 1:
                label = "Bridge"
            elif n_choruses_seen == 0 and len(gap) <= 2:
                label = "Intro"
            sections.append({"label": label, "lines": gap})
        sections.append({"label": "Chorus", "lines": line_list[cs:ce]})
        n_choruses_seen += 1
        pos = ce
    if pos < n:
        tail = line_list[pos:]
        sections.append({"label": "Outro" if len(tail) <= 2 else "Verse", "lines": tail})
    return sections


def song_structure(raw: str | None, cleaned: str | None) -> dict:
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
            norm = [" ".join(tokens(s)) for s in stanzas]
            counts = Counter(norm)
            for s, n in zip(stanzas, norm):
                label = "Chorus" if counts[n] >= 2 and n else "Verse"
                sections.append({"label": label, "lines": [l.strip() for l in s.split("\n") if l.strip()]})
        else:
            sections = _sections_from_repeated_runs(lines(src))

    verse_count = sum(1 for s in sections if s["label"] == "Verse")
    seen_verses = 0
    for s in sections:
        s["words"] = len(tokens(" ".join(s["lines"])))
        if s["label"] == "Verse" and verse_count > 1:
            seen_verses += 1
            s["label"] = f"Verse {seen_verses}"

    total_words = sum(s["words"] for s in sections) or 1
    chorus_words = sum(s["words"] for s in sections if s["label"].split(" ")[0] in CHORUS_LABELS)
    return {
        "sections": sections,
        "summary": " – ".join(s["label"] for s in sections),
        "chorus_share": round(chorus_words / total_words, 3),
    }


def corpus_hooks(track_list: list[dict], text_key: str = "cleaned_lyrics", top: int = 12) -> list[dict]:
    line_counts: Counter = Counter()
    line_songs: dict[str, set] = {}
    display: dict[str, str] = {}
    for t in track_list:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        for line in lines(text):
            n = norm_line(line)
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


def corpus_rhyme_pairs(track_list: list[dict], text_key: str = "cleaned_lyrics", top: int = 15) -> list[dict]:
    pair_counts: Counter = Counter()
    for t in track_list:
        text = t.get(text_key) or t.get("raw_lyrics") or ""
        _, pairs = rhyme_stats(lines(text))
        pair_counts.update(pairs)
    return [{"a": a, "b": b, "count": c} for (a, b), c in pair_counts.most_common(top) if c >= 2]


def pov_profile(track_list: list[dict]) -> dict:
    totals = Counter()
    for t in track_list:
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


def section_contrast(track_list: list[dict]) -> dict:
    """Verse vs chorus word stats (tone/concreteness deferred to Semantic Engine)."""
    buckets: dict[str, dict] = {
        "verse": {"lines": [], "tokens": []},
        "chorus": {"lines": [], "tokens": []},
    }
    for t in track_list:
        st = song_structure(t.get("raw_lyrics"), t.get("cleaned_lyrics"))
        for s in st.get("sections", []):
            base = s["label"].split(" ")[0].lower()
            key = "chorus" if base == "chorus" else ("verse" if base in ("verse", "song") else None)
            if key is None:
                continue
            buckets[key]["lines"].extend(s["lines"])
            buckets[key]["tokens"].extend(tokens(" ".join(s["lines"])))

    out = {}
    stop = stopwords()
    for key, b in buckets.items():
        line_list, toks = b["lines"], b["tokens"]
        if not line_list or not toks:
            out[key] = None
            continue
        content = [w for w in toks if w not in stop and w not in VOCALIZATIONS]
        syls = [sum(syllables(w) for w in tokens(l)) for l in line_list if tokens(l)]
        out[key] = {
            "lines": len(line_list),
            "words": len(toks),
            "valence": 0.0,
            "diversity": round(len(set(content)) / max(1, len(content)), 4),
            "concreteness": 0.0,
            "syllables_per_line": round(mean(syls), 2) if syls else 0.0,
            "words_per_line": round(len(toks) / len(line_list), 2),
        }
    return out


def run_deterministic_analysis(playlist_pk: int) -> int:
    """Tokenize, word frequencies, per-track metrics. Returns analysis run id."""
    from backend import db

    tracks = db.get_tracks(playlist_pk)
    if not tracks:
        raise ValueError("No tracks found.")

    text_key = "cleaned_lyrics"
    tok_list = tokenize_lyrics(tracks, text_key=text_key)
    if not tok_list:
        text_key = "raw_lyrics"
        tok_list = tokenize_lyrics(tracks, text_key=text_key)
    if not tok_list:
        raise ValueError("No lyrics to analyze.")

    top50 = top_n_words(tok_list, n=50)
    word_contexts = build_word_contexts(tracks, text_key=text_key)
    if not word_contexts:
        word_contexts = build_word_contexts(tracks, text_key="raw_lyrics")

    run_id = db.insert_analysis_run(playlist_pk)
    db.delete_word_frequencies_for_run(run_id)
    db.insert_word_frequencies(run_id, top50, pos=None)
    db.insert_word_contexts(run_id, word_contexts)

    for t in tracks:
        raw = t.get("cleaned_lyrics") or t.get("raw_lyrics") or ""
        db.update_track_metrics(t["id"], track_metrics(raw))

    db.update_run_llm_status(run_id, {
        "ok": False,
        "status": "pending",
        "message": "Awaiting semantic engine map pass.",
        "tracks_enriched": 0,
    })
    return run_id
