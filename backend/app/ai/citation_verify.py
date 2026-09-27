"""Verifies that a cited excerpt actually appears in the retrieved chunk text
it claims to come from, rather than trusting the LLM's citation by prompt
alone. A known gap in the original prototype, closed here."""

from __future__ import annotations

import difflib
import re

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip().lower()


def verify_citation(excerpt: str, source_text: str, threshold: float = 0.85) -> tuple[bool, str | None]:
    """Returns (verified, note). Verified if the excerpt is a near-exact
    substring of source_text (allowing for whitespace differences), or if a
    sliding-window fuzzy match against source_text exceeds `threshold`."""
    norm_excerpt = _normalize(excerpt)
    norm_source = _normalize(source_text)

    if not norm_excerpt:
        return False, "empty excerpt"

    if norm_excerpt in norm_source:
        return True, None

    matcher = difflib.SequenceMatcher(None, norm_excerpt, norm_source)
    match = matcher.find_longest_match(0, len(norm_excerpt), 0, len(norm_source))
    coverage = match.size / max(len(norm_excerpt), 1)
    if coverage >= threshold:
        return True, None

    return False, f"excerpt not found in source text (best overlap {coverage:.0%})"
