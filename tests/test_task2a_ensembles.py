"""Synthetic keyed 50/50 ensemble tests."""

from __future__ import annotations

import pandas as pd
import pytest

from src.task2a.ensembles import EnsembleError, blend_equal_weight


def _rows(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"backtest_id": ["BT01", "BT01"], "depot": ["A", "A"],
        "brand": ["Fresh", "Fresh"], "origin_week_start_date": ["2025-01-06"] * 2,
        "target_week_start_date": ["2025-01-13", "2025-01-20"], "horizon_weeks": [1, 2],
        "target_name": ["total", "total"], "y_true": [10.0, 20.0],
        "total_y_true": [10.0, 20.0], "y_pred": values,
        "phase14_backtest_signature": ["sig", "sig"]})


def test_keyed_blend_aligns_reordered_rows_and_preserves_negative_raw_value() -> None:
    blended = blend_equal_weight(_rows([-4.0, 10.0]), _rows([2.0, 30.0]).iloc[::-1], "ensemble")
    assert blended.y_pred.tolist() == [-1.0, 20.0]
    assert blended.candidate_id.eq("ensemble").all()


def test_missing_duplicate_or_wrong_signature_rejected() -> None:
    left, right = _rows([1.0, 2.0]), _rows([3.0, 4.0])
    with pytest.raises(EnsembleError, match="identical"):
        blend_equal_weight(left, right.iloc[:1], "ensemble")
    with pytest.raises(EnsembleError, match="duplicate"):
        blend_equal_weight(left, pd.concat([right, right.iloc[:1]]), "ensemble")
    right.loc[0, "phase14_backtest_signature"] = "other"
    with pytest.raises(EnsembleError, match="signatures"):
        blend_equal_weight(left, right, "ensemble")
