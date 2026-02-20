"""
Lyric cleaner: strip meta-tags and normalize punctuation.
Used after fetch and before analysis.
"""
from __future__ import annotations

import re


def clean_lyrics(text: str | None) -> str:
    """
    Strip meta-tags like [Chorus], [Verse 1], [Bridge], (x2), etc.
    Normalize punctuation: collapse repeated punctuation, standardize apostrophes.
    """
    if not text or not isinstance(text, str):
        return ""
    s = text.strip()

    # Remove section headers: [Chorus], [Verse 1], [Verse 2], [Bridge], [Pre-Chorus], [Outro], [Intro], [Hook], etc.
    s = re.sub(r"\[[\w\s\-']+\]", "", s, flags=re.IGNORECASE)

    # Remove (x2), (x3), (Repeat), (2x), etc.
    s = re.sub(r"\(\s*x?\d+\s*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\(\s*repeat\s*\)", "", s, flags=re.IGNORECASE)

    # Standardize apostrophes (curly/smart quotes and backticks to straight)
    s = s.replace("'", "'").replace("'", "'")
    s = s.replace("`", "'")
    s = s.replace(""", '"').replace(""", '"')

    # Collapse multiple spaces/newlines to single newline, then trim each line
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    # Collapse repeated punctuation at end of line (e.g. "!!!")
    lines = [re.sub(r"([.!?,…;:])\1+", r"\1", line) for line in lines]
    s = "\n".join(lines)

    # Collapse multiple newlines to one
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()
