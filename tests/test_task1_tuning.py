from __future__ import annotations

import pandas as pd
import pytest

from src.task1.tuning import (
    Task1TuningError,
    assert_bounded_search,
    bounded_grid_candidates,
    rank_classifier_candidates,
    rank_regression_candidates,
    stable_candidate_id,
)


def test_candidate_id_stable() -> None:
    a = stable_candidate_id("cat", {"depth": 7, "learning_rate": 0.05})
    b = stable_candidate_id("cat", {"learning_rate": 0.05, "depth": 7})
    assert a == b


def test_bounded_candidates_and_cap() -> None:
    candidates = bounded_grid_candidates(
        prefix="catreg",
        grid={"depth": [5, 7, 9], "learning_rate": [0.03, 0.05], "l2_leaf_reg": [3, 7]},
        max_candidates=16,
    )
    assert len(candidates) == 12
    assert_bounded_search(candidates, max_candidates=16)
    with pytest.raises(Task1TuningError):
        assert_bounded_search(candidates, max_candidates=2)


def test_regression_and_classifier_ranking() -> None:
    reg = pd.DataFrame(
        [
            {"candidate_id": "a", "fold_id": 1, "metric_name": "mae", "metric_value": 2.0},
            {"candidate_id": "a", "fold_id": 1, "metric_name": "rmse", "metric_value": 3.0},
            {"candidate_id": "a", "fold_id": 2, "metric_name": "mae", "metric_value": 1.9},
            {"candidate_id": "a", "fold_id": 2, "metric_name": "rmse", "metric_value": 3.1},
            {"candidate_id": "b", "fold_id": 1, "metric_name": "mae", "metric_value": 1.5},
            {"candidate_id": "b", "fold_id": 1, "metric_name": "rmse", "metric_value": 2.5},
            {"candidate_id": "b", "fold_id": 2, "metric_name": "mae", "metric_value": 1.7},
            {"candidate_id": "b", "fold_id": 2, "metric_name": "rmse", "metric_value": 2.6},
        ]
    )
    ranked_reg = rank_regression_candidates(reg)
    assert ranked_reg.iloc[0]["candidate_id"] == "b"

    clf = pd.DataFrame(
        [
            {"candidate_id": "x", "fold_id": 1, "metric_name": "log_loss", "metric_value": 0.45},
            {"candidate_id": "x", "fold_id": 1, "metric_name": "brier_score", "metric_value": 0.20},
            {"candidate_id": "x", "fold_id": 2, "metric_name": "log_loss", "metric_value": 0.47},
            {"candidate_id": "x", "fold_id": 2, "metric_name": "brier_score", "metric_value": 0.21},
            {"candidate_id": "y", "fold_id": 1, "metric_name": "log_loss", "metric_value": 0.35},
            {"candidate_id": "y", "fold_id": 1, "metric_name": "brier_score", "metric_value": 0.18},
            {"candidate_id": "y", "fold_id": 2, "metric_name": "log_loss", "metric_value": 0.37},
            {"candidate_id": "y", "fold_id": 2, "metric_name": "brier_score", "metric_value": 0.19},
        ]
    )
    ranked_clf = rank_classifier_candidates(clf)
    assert ranked_clf.iloc[0]["candidate_id"] == "y"
