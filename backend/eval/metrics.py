"""Retrieval and classification metrics, plus confidence intervals.

A gold item is an evidence span in a named document. A retrieved chunk covers
it when the chunk comes from that document and contains the span (after
whitespace/case normalization), so labels do not depend on chunk boundaries.
"""

from __future__ import annotations

import math
import random
from typing import Iterable, Sequence

from app.ai.rag import Chunk

from .corpus import normalize


def covers(chunk: Chunk, gold_item: dict) -> bool:
    return chunk.doc_name == gold_item["doc"] and normalize(gold_item["span"]) in normalize(chunk.text)


def covered_flags(gold: Sequence[dict], retrieved: Sequence[Chunk], k: int) -> list[bool]:
    top = list(retrieved)[:k]
    return [any(covers(c, g) for c in top) for g in gold]


def hit_at_k(gold: Sequence[dict], retrieved: Sequence[Chunk], k: int) -> float:
    """1.0 if any gold span is covered by the top-k chunks."""
    return 1.0 if any(covered_flags(gold, retrieved, k)) else 0.0


def recall_at_k(gold: Sequence[dict], retrieved: Sequence[Chunk], k: int) -> float:
    """Fraction of gold spans covered by the top-k chunks."""
    flags = covered_flags(gold, retrieved, k)
    return sum(flags) / len(flags) if flags else 0.0


def reciprocal_rank(gold: Sequence[dict], retrieved: Sequence[Chunk]) -> float:
    """1/rank of the first retrieved chunk that covers any gold span, else 0."""
    for rank, chunk in enumerate(retrieved, start=1):
        if any(covers(chunk, g) for g in gold):
            return 1.0 / rank
    return 0.0


def wilson_interval(successes: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def bootstrap_mean_ci(values: Iterable[float], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap 95% interval for a mean (fixed seed for reproducibility)."""
    vals = list(values)
    if not vals:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(vals, k=len(vals))) / len(vals) for _ in range(n_boot))
    return (means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1])


def precision_recall_f1(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}
