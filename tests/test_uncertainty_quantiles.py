import math

import pytest

from src.uncertainty.quantiles import QuantileError, finite_sample_quantile, finite_sample_rank


def test_n_one_and_rank_clipping():
    assert finite_sample_rank(1, 0.8) == 1
    assert finite_sample_quantile([4.0], 0.9) == 4.0


@pytest.mark.parametrize(("scores", "coverage", "expected"), [
    ([4, 1, 3, 2], 0.8, 4.0),
    ([5, 1, 4, 2, 3], 0.8, 5.0),
    ([1, 2, 3, 4, 5, 6, 7, 8, 9], 0.8, 8.0),
    ([1, 2, 3, 4, 5, 6, 7, 8, 9], 0.9, 9.0),
])
def test_higher_order_statistic_without_interpolation(scores, coverage, expected):
    assert finite_sample_quantile(scores, coverage) == expected


@pytest.mark.parametrize("coverage", [0, 1, -0.1, 1.1, math.nan])
def test_invalid_coverage_rejected(coverage):
    with pytest.raises(QuantileError):
        finite_sample_quantile([1], coverage)


@pytest.mark.parametrize("scores", [[1, math.nan], [1, -0.1], [], [1, math.inf]])
def test_invalid_scores_rejected(scores):
    with pytest.raises(QuantileError):
        finite_sample_quantile(scores, 0.8)


def test_deterministic_and_sorted_semantics():
    scores = [8, 2, 6, 4, 1]
    assert finite_sample_quantile(scores, 0.8) == finite_sample_quantile(list(reversed(scores)), 0.8) == 8.0
