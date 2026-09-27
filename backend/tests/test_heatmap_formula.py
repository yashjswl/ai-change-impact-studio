import itertools

import pytest

from app.services.impact_service import (
    _band,
    compute_heat_rating,
    compute_impact_score,
    compute_readiness_score,
    find_barrier_dimension,
)


def test_barrier_dimension_first_weak_score():
    label, score = find_barrier_dimension([5, 2, 5, 5, 5])
    assert label == "Desire"
    assert score == 2


def test_barrier_dimension_none_when_all_strong():
    label, score = find_barrier_dimension([4, 4, 5, 4, 5])
    assert label is None
    assert score is None


def test_readiness_score_barrier_weighted_lower_than_naive_average():
    # Awareness=2 is the barrier; naive average would be 3.6 (72/100)
    scores = [2, 4, 4, 4, 4]
    naive_avg_pct = round(sum(scores) / len(scores) / 5 * 100)
    barrier_weighted = compute_readiness_score(scores)
    assert barrier_weighted < naive_avg_pct


def test_readiness_score_no_barrier_equals_average():
    scores = [4, 4, 5, 4, 5]
    expected = round(sum(scores) / len(scores) / 5 * 100, 1)
    assert compute_readiness_score(scores) == expected


def test_impact_score_scaling():
    assert compute_impact_score(5) == 100.0
    assert compute_impact_score(1) == 20.0


@pytest.mark.parametrize(
    "score,expected_band",
    [(0, "Low"), (33, "Low"), (34, "Medium"), (66, "Medium"), (67, "High"), (100, "High")],
)
def test_band_boundaries(score, expected_band):
    assert _band(score) == expected_band


ALL_9_CELLS = {
    ("High", "Low"): "Red",
    ("High", "Medium"): "Red",
    ("High", "High"): "Amber",
    ("Medium", "Low"): "Red",
    ("Medium", "Medium"): "Amber",
    ("Medium", "High"): "Green",
    ("Low", "Low"): "Amber",
    ("Low", "Medium"): "Green",
    ("Low", "High"): "Green",
}

BAND_REPRESENTATIVE = {"Low": 10, "Medium": 50, "High": 90}


@pytest.mark.parametrize(
    "impact_band,readiness_band", list(itertools.product(["Low", "Medium", "High"], repeat=2))
)
def test_heat_rating_matches_full_grid(impact_band, readiness_band):
    impact_score = BAND_REPRESENTATIVE[impact_band]
    readiness_score = BAND_REPRESENTATIVE[readiness_band]
    expected = ALL_9_CELLS[(impact_band, readiness_band)]
    assert compute_heat_rating(impact_score, readiness_score) == expected
