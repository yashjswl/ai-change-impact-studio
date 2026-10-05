"""Verifies that a cited excerpt actually appears in the source text it claims
to come from, rather than trusting the LLM's citation by prompt alone.

`verify_citation` is the production entry point. It matches at the word level
inside a sliding window of the source, so a one-word edit or an added list
marker still verifies, while a fabricated, paraphrased or misattributed excerpt
does not. `verify_citation_contiguous` is the earlier character-level matcher,
kept so the evaluation in `backend/eval` can report before/after numbers.
"""

from __future__ import annotations

import difflib
import re

_WHITESPACE_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"\w+")

# Windows that share fewer than this fraction of the excerpt's words are skipped
# before the (more expensive) sequence alignment. Matched words can never exceed
# shared words, so this only affects the reported best overlap, not a decision at
# any threshold above this floor.
_PRUNE_FLOOR = 0.5


def _normalize(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip().lower()


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def verify_citation_contiguous(
    excerpt: str, source_text: str, threshold: float = 0.85, autojunk: bool = True
) -> tuple[bool, str | None]:
    """Character-level check: the excerpt must be a substring of the source, or
    its longest contiguous matching block must cover `threshold` of it.

    Weaknesses (measured in backend/eval): with difflib's default autojunk the
    fuzzy path collapses on sources over 200 characters, and a single edited
    word splits the longest block and drops coverage under the threshold."""
    norm_excerpt = _normalize(excerpt)
    norm_source = _normalize(source_text)

    if not norm_excerpt:
        return False, "empty excerpt"
    if norm_excerpt in norm_source:
        return True, None

    matcher = difflib.SequenceMatcher(None, norm_excerpt, norm_source, autojunk=autojunk)
    match = matcher.find_longest_match(0, len(norm_excerpt), 0, len(norm_source))
    coverage = match.size / max(len(norm_excerpt), 1)
    if coverage >= threshold:
        return True, None
    return False, f"excerpt not found in source text (best overlap {coverage:.0%})"


def verify_citation_tokens(
    excerpt: str, source_text: str, threshold: float = 0.85, strict_numbers: bool = True
) -> tuple[bool, str | None]:
    """Word-level check: slide a window over the source and align the excerpt's
    words against it. Verified when the best window matches at least
    `threshold` of the excerpt's words, in order.

    With `strict_numbers`, every number in the excerpt must also be matched in
    that window. A tolerant word match would otherwise accept an excerpt whose
    only difference is an altered figure ("$75" quoted as "$85"), which is the
    most damaging kind of misquote."""
    excerpt_words = _words(excerpt)
    if not excerpt_words:
        return False, "empty excerpt"
    source_words = _words(source_text)
    n = len(excerpt_words)

    # Exact (normalized) containment is the common case and needs no alignment.
    if _contains_sequence(source_words, excerpt_words):
        return True, None

    number_idx = [i for i, w in enumerate(excerpt_words) if any(ch.isdigit() for ch in w)]
    wanted = set(excerpt_words)
    window = n + max(3, n // 3)  # slack for inserted words
    hits_prefix = [0]
    for word in source_words:
        hits_prefix.append(hits_prefix[-1] + (1 if word in wanted else 0))

    best_any = 0.0  # best overlap ignoring numbers, used for the failure note
    best_accepted = 0.0  # best overlap among windows that also satisfy the number rule
    for start in range(0, max(1, len(source_words) - n + 1)):
        end = min(start + window, len(source_words))
        shared = hits_prefix[end] - hits_prefix[start]
        if shared < _PRUNE_FLOOR * n:
            continue
        matcher = difflib.SequenceMatcher(None, excerpt_words, source_words[start:end], autojunk=False)
        blocks = matcher.get_matching_blocks()
        ratio = sum(block.size for block in blocks) / n
        best_any = max(best_any, ratio)
        if strict_numbers and number_idx:
            matched_idx = {i for block in blocks for i in range(block.a, block.a + block.size)}
            if not all(i in matched_idx for i in number_idx):
                continue
        best_accepted = max(best_accepted, ratio)
        if best_accepted >= 1.0:
            break

    if best_accepted >= threshold:
        return True, None
    if best_any >= threshold:
        return False, "excerpt matches the source except for a number"
    return False, f"excerpt not found in source text (best word overlap {best_any:.0%})"


def _contains_sequence(haystack: list[str], needle: list[str]) -> bool:
    n = len(needle)
    first = needle[0]
    for i in range(len(haystack) - n + 1):
        if haystack[i] == first and haystack[i : i + n] == needle:
            return True
    return False


def verify_citation(excerpt: str, source_text: str, threshold: float = 0.85) -> tuple[bool, str | None]:
    """Production verifier. Returns (verified, note)."""
    return verify_citation_tokens(excerpt, source_text, threshold)
