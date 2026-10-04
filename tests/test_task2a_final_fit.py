"""Synthetic tests for Phase 17 frozen-only component fitting."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.task2a.features import load_feature_config
from src.task2a.final_fit import FinalFitError, final_training_rows, fit_frozen_component, predict_frozen_component
from src.task2a.model_preprocessing import feature_profile
from src.task2a.multihorizon import build_direct_multihorizon_table
from tests.test_task2a_final_inference import _calendar, _future_calendar, _grid
from tests.test_task2a_validation import _panel


ROOT = Path(__file__).resolve().parents[1]


def test_final_training_excludes_future_labels_and_chilled_is_fresh_only() -> None:
    panel = _panel(76)
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    origin = panel.week_start_date.max()
    total = final_training_rows(table, origin, "total")
    chilled = final_training_rows(table, origin, "chilled")
    assert total.target_week_start_date.le(origin).all()
    assert chilled.target_week_start_date.le(origin).all() and chilled.brand.eq("Fresh").all()
    future = table.copy()
    future.loc[future.target_week_start_date.gt(origin), "target_total_volume_m3"] = 999999.0
    pd.testing.assert_frame_equal(total, final_training_rows(future, origin, "total"))


def test_baseline_component_uses_origin_bounded_history() -> None:
    panel = _panel(76)
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    origin = panel.week_start_date.max()
    config = yaml.safe_load((ROOT / "configs/task2a_final_models.yaml").read_text(encoding="utf-8"))
    baseline = {"approach_type": "baseline", "candidate_id": "total_last_week", "family": "last_week",
                "parameters": {"enabled": True}, "final_iteration_policy": "NOT_APPLICABLE"}
    profile = feature_profile(load_feature_config(ROOT / "configs/task2a_features.yaml"))
    component = fit_frozen_component(baseline, "total", table, origin, profile)
    from src.task2a.final_inference import build_final_test_features
    features, _ = build_final_test_features(panel, _future_calendar(panel), _grid(panel),
        load_feature_config(ROOT / "configs/task2a_features.yaml"))
    values = predict_frozen_component(component, features, panel, origin, profile)
    assert len(values) == len(features)
    with pytest.raises(FinalFitError, match="target-safe"):
        final_training_rows(table.loc[table.target_week_start_date.gt(origin)], origin, "total")
