import pytest

from app.ai.rag import Chunk
from eval.metrics import (
    bootstrap_mean_ci,
    hit_at_k,
    precision_recall_f1,
    recall_at_k,
    reciprocal_rank,
    wilson_interval,
)


def chunk(doc: str, text: str) -> Chunk:
    return Chunk(doc_name=doc, doc_type="t", chunk_id=0, text=text)


GOLD_ONE = [{"doc": "a.md", "span": "refund window is 14 days"}]
GOLD_TWO = [
    {"doc": "a.md", "span": "refund window is 14 days"},
    {"doc": "b.md", "span": "daily payout run"},
]


def test_hit_requires_matching_document():
    wrong_doc = [chunk("b.md", "The refund window is 14 days.")]
    right_doc = [chunk("a.md", "The refund window is 14 days.")]
    assert hit_at_k(GOLD_ONE, wrong_doc, 5) == 0.0
    assert hit_at_k(GOLD_ONE, right_doc, 5) == 1.0


def test_span_match_ignores_case_and_line_wraps():
    wrapped = [chunk("a.md", "The REFUND window\n   is 14   days.")]
    assert hit_at_k(GOLD_ONE, wrapped, 1) == 1.0


def test_hit_respects_k_cutoff():
    ranked = [chunk("x.md", "unrelated"), chunk("y.md", "unrelated"), chunk("a.md", "refund window is 14 days")]
    assert hit_at_k(GOLD_ONE, ranked, 2) == 0.0
    assert hit_at_k(GOLD_ONE, ranked, 3) == 1.0


def test_recall_is_fraction_of_gold_spans():
    ranked = [chunk("a.md", "refund window is 14 days"), chunk("x.md", "unrelated")]
    assert recall_at_k(GOLD_TWO, ranked, 2) == 0.5
    ranked.append(chunk("b.md", "a daily payout run happens"))
    assert recall_at_k(GOLD_TWO, ranked, 3) == 1.0


def test_reciprocal_rank():
    ranked = [chunk("x.md", "n"), chunk("a.md", "refund window is 14 days")]
    assert reciprocal_rank(GOLD_ONE, ranked) == 0.5
    assert reciprocal_rank(GOLD_ONE, [chunk("x.md", "n")]) == 0.0


def test_wilson_interval_bounds_and_known_value():
    lo, hi = wilson_interval(8, 10)
    assert lo == pytest.approx(0.490, abs=0.005)
    assert hi == pytest.approx(0.943, abs=0.005)
    assert wilson_interval(0, 0) == (0.0, 0.0)
    lo, hi = wilson_interval(10, 10)
    assert hi == pytest.approx(1.0) and lo < 1.0


def test_bootstrap_ci_is_deterministic_and_brackets_mean():
    values = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0]
    lo1, hi1 = bootstrap_mean_ci(values)
    lo2, hi2 = bootstrap_mean_ci(values)
    assert (lo1, hi1) == (lo2, hi2)
    assert lo1 <= sum(values) / len(values) <= hi1


def test_precision_recall_f1():
    m = precision_recall_f1(tp=8, fp=2, fn=4)
    assert m["precision"] == pytest.approx(0.8)
    assert m["recall"] == pytest.approx(8 / 12)
    assert m["f1"] == pytest.approx(2 * 0.8 * (8 / 12) / (0.8 + 8 / 12))
    assert precision_recall_f1(0, 0, 0)["f1"] == 0.0
