from __future__ import annotations

import pandas as pd
import pytest

from src.task1.validation import (
    Task1ValidationError,
    build_task1_validation_plan,
    make_final_chronological_holdout,
    resolve_validation_date,
    sort_task1_history_chronologically,
    transform_validation_historical_features,
)


def _config(**overrides: object) -> dict:
    cfg = {
        "validation_date": {
            "column": "route_date",
            "fallback_column": "dispatch_date",
            "require_consistency_when_both_present": True,
        },
        "ordering": {"tie_breakers": ["route_id", "seq_in_route", "delivery_id"]},
        "final_holdout": {"calendar_days": 3, "same_date_atomic": True},
        "expanding_cv": {
            "n_folds": 2, "validation_calendar_days": 2, "gap_calendar_days": 0,
            "minimum_training_calendar_days": 2, "same_date_atomic": True,
            "require_expanding_train": True,
        },
    }
    cfg.update(overrides)
    return cfg


def _history(days: int = 12) -> pd.DataFrame:
    rows = []
    for day in range(1, days + 1):
        date = f"2026-01-{day:02d}"
        # Busy date: two rows must remain atomic.
        for seq in (0, 1):
            rows.append(
                {
                    "delivery_id": f"D{day:02d}_{seq}", "route_date": date,
                    "dispatch_date": date, "route_id": f"R{day:02d}",
                    "seq_in_route": seq, "outlet_id": "O1", "brand": "Fresh",
                    "dock_type": "rear_dock",
                }
            )
    return pd.DataFrame(rows)


def test_dt123_chronological_sort_is_stable_and_non_mutating() -> None:
    frame = _history(4).sample(frac=1, random_state=3)
    before = frame.copy(deep=True)
    sorted_frame = sort_task1_history_chronologically(frame, _config())
    pd.testing.assert_frame_equal(frame, before)
    assert sorted_frame["_validation_date"].is_monotonic_increasing
    date_one = sorted_frame[sorted_frame["_validation_date"] == pd.Timestamp("2026-01-01")]
    assert date_one["seq_in_route"].tolist() == [0, 1]


def test_dt123_missing_and_invalid_dates_fail() -> None:
    frame = _history(3).drop(columns=["route_date", "dispatch_date"])
    with pytest.raises(Task1ValidationError, match="Missing validation date"):
        resolve_validation_date(frame)
    frame = _history(3)
    frame.loc[0, "route_date"] = "not-a-date"
    with pytest.raises(Task1ValidationError, match="invalid"):
        resolve_validation_date(frame)


def test_dt124_holdout_latest_atomic_and_disjoint() -> None:
    sorted_frame = sort_task1_history_chronologically(_history(), _config())
    split = make_final_chronological_holdout(sorted_frame, _config())
    assert max(split.development_dates) < min(split.holdout_dates)
    assert not (set(split.development_dates) & set(split.holdout_dates))
    assert len(split.holdout_index) == 6  # 3 latest dates x 2 rows


def test_dt124_insufficient_history_fails() -> None:
    sorted_frame = sort_task1_history_chronologically(_history(1), _config())
    with pytest.raises(Task1ValidationError, match="Insufficient"):
        make_final_chronological_holdout(sorted_frame, _config())


def test_dt125_dt126_expanding_folds_are_disjoint_and_holdout_free() -> None:
    plan = build_task1_validation_plan(_history(14), _config())
    holdout_dates = set(plan["holdout"].holdout_dates)
    assert len(plan["folds"]) == 2
    prior_train_n = 0
    for fold in plan["folds"]:
        assert max(fold.train_dates) < min(fold.validation_dates)
        assert not set(fold.train_dates) & set(fold.validation_dates)
        assert not set(fold.validation_dates) & holdout_dates
        assert len(fold.train_index) > prior_train_n
        prior_train_n = len(fold.train_index)


def test_dt126_validation_targets_do_not_change_validation_historical_features() -> None:
    train = pd.DataFrame(
        {
            "route_date": ["2026-01-01", "2026-01-02"],
            "outlet_id": ["O1", "O1"], "brand": ["Fresh", "Fresh"], "dock_type": ["rear_dock", "rear_dock"],
        }
    )
    valid = pd.DataFrame(
        {
            "route_date": ["2026-01-03", "2026-01-03"],
            "outlet_id": ["O1", "O1"], "brand": ["Fresh", "Fresh"], "dock_type": ["rear_dock", "rear_dock"],
        }
    )
    out_a = transform_validation_historical_features(
        train, pd.Series([10.0, 20.0]), pd.Series([0, 1]), valid, date_col="route_date"
    )
    # Deliberately no validation y argument exists in transform API.
    out_b = transform_validation_historical_features(
        train, pd.Series([10.0, 20.0]), pd.Series([0, 1]), valid, date_col="route_date"
    )
    pd.testing.assert_frame_equal(out_a, out_b)
    assert out_a.iloc[0].equals(out_a.iloc[1])  # same-date validation rows cannot update each other
