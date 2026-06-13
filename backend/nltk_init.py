"""
Ensure required NLTK corpora/taggers are present before serving requests.
Run once at FastAPI startup — never download during API handlers.
"""
from __future__ import annotations

import nltk

# Package names passed to nltk.download()
_NLTK_PACKAGES = (
    "punkt",
    "punkt_tab",
    "stopwords",
    "averaged_perceptron_tagger_eng",
)

# Paths verified with nltk.data.find after download
_NLTK_PATHS = (
    "corpora/stopwords",
    "tokenizers/punkt",
    "tokenizers/punkt_tab",
    "taggers/averaged_perceptron_tagger_eng",
)


def ensure_nltk_data() -> None:
    """Download and verify NLTK data. Raises if anything is still missing."""
    for package in _NLTK_PACKAGES:
        nltk.download(package, quiet=True)
    missing: list[str] = []
    for path in _NLTK_PATHS:
        try:
            nltk.data.find(path)
        except LookupError:
            missing.append(path)
    if missing:
        raise RuntimeError(
            "NLTK data missing after startup download: " + ", ".join(missing)
        )
