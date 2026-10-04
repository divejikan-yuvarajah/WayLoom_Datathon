"""Synthetic-only Phase 17 final-grid, leakage, and postprocessing tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from src.task2a.features import load_feature_config
from src.task2a.final_inference import (FinalInferenceError, build_final_test_features,
    final_forecast_origin, load_task2a_test_inputs, postprocess_predictions, run_final_inference,
    validate_inference_config)
from src.task2a.multihorizon import build_direct_multihorizon_table
from tests.test_task2a_validation import _calendar, _panel


ROOT = Path(__file__).resolve().parents[1]


def _future_calendar(panel: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(panel.week_start_date.min(), panel.week_start_date.max() + pd.Timedelta(weeks=10, days=6), freq="D")
    iso = dates.isocalendar()
    return pd.DataFrame({"date": dates, "iso_year": iso.year.to_numpy(dtype=int), "iso_week": iso.week.to_numpy(dtype=int),
        "is_operating": (dates.dayofweek < 5).astype(int), "is_weekend": (dates.dayofweek >= 5).astype(int),
        "is_payday": (dates.day == 25).astype(int), "festival": "", "festival_ramp": 0.0,
        "is_holiday": 0, "monsoon": 0})


def _grid(panel: pd.DataFrame) -> pd.DataFrame:
    origin = panel.week_start_date.max()
    target = pd.date_range(origin + pd.Timedelta(weeks=1), periods=10, freq="7D")
    iso = target.isocalendar()
    rows = []
    for depot, brand in panel[["depot", "brand"]].drop_duplicates().itertuples(index=False):
        for i, (year, week) in enumerate(zip(iso.year, iso.week, strict=True), start=1):
            rows.append({"row_id": f"{depot}-{brand}-{i}", "depot": depot, "brand": brand,
                         "iso_year": int(year), "iso_week": int(week)})
    return pd.DataFrame(rows)


def _config() -> dict:
    config = yaml.safe_load((ROOT / "configs/task2a_final_models.yaml").read_text(encoding="utf-8"))
    for winner in (config["total"], config["chilled_fresh"]):
        for component in winner["component_candidates"]:
            if component["family"] == "catboost":
                component["parameters"]["iterations"] = 5
            else:
                component["parameters"]["n_estimators"] = 5
            component["final_iteration_policy"]["value"] = 5
    return config


def test_inference_config_requires_frozen_phase16_rules() -> None:
    config = yaml.safe_load((ROOT / "configs/task2a_inference.yaml").read_text(encoding="utf-8"))
    frozen = _config()
    validate_inference_config(config, frozen)
    bad = deepcopy(config)
    bad["postprocessing"]["clip_negative"] = False
    with pytest.raises(FinalInferenceError, match="postprocessing"):
        validate_inference_config(bad, frozen)


def test_test_grid_origin_calendar_and_horizons_are_exact() -> None:
    panel = _panel(76)
    grid = _grid(panel)
    loaded = load_task2a_test_inputs(grid)
    assert loaded["__official_row_order"].tolist() == list(range(len(grid)))
    features, origin = build_final_test_features(panel, _future_calendar(panel), grid,
                                                 load_feature_config(ROOT / "configs/task2a_features.yaml"))
    assert origin == final_forecast_origin(panel, grid)
    assert set(features.horizon_weeks) == set(range(1, 11))
    assert features.target_week_start_date.gt(origin).all()
    assert features.origin_demand_feature_max_source_week.le(origin).all()


def test_bad_official_grid_is_rejected() -> None:
    panel, grid = _panel(76), _grid(_panel(76))
    duplicate = pd.concat([grid, grid.iloc[[0]]], ignore_index=True)
    with pytest.raises(FinalInferenceError, match="unique"):
        load_task2a_test_inputs(duplicate)
    bad = grid.copy()
    bad.loc[0, "brand"] = "Unknown"
    with pytest.raises(FinalInferenceError, match="Fresh"):
        load_task2a_test_inputs(bad)
    bad = grid.copy()
    bad.loc[0, "iso_week"] = int(panel.iloc[-1].iso_week)
    with pytest.raises(FinalInferenceError, match="horizons"):
        build_final_test_features(panel, _future_calendar(panel), bad,
                                  load_feature_config(ROOT / "configs/task2a_features.yaml"))
    with pytest.raises(FinalInferenceError, match="every horizon"):
        build_final_test_features(panel, _future_calendar(panel), grid.iloc[1:],
                                  load_feature_config(ROOT / "configs/task2a_features.yaml"))


def test_postprocessing_structural_zero_clipping_and_capping() -> None:
    raw = pd.DataFrame({"brand": ["Fresh", "Style", "Tech", "Fresh"],
        "raw_pred_total_volume_m3": [-2.0, 3.0, 0.0, 2.0],
        "raw_pred_chilled_volume_m3": [-1.0, 9.0, 4.0, 8.0]})
    final, report = postprocess_predictions(raw)
    assert final.pred_total_volume_m3.tolist() == [0.0, 3.0, 0.0, 2.0]
    assert final.pred_chilled_volume_m3.tolist() == [0.0, 0.0, 0.0, 2.0]
    assert report == {"negative_total_clipped_count": 1, "negative_chilled_clipped_count": 1,
                      "chilled_capped_to_total_count": 1}
    raw.loc[0, "raw_pred_total_volume_m3"] = np.nan
    with pytest.raises(FinalInferenceError, match="NaN/Inf"):
        postprocess_predictions(raw)


def test_frozen_ensemble_inference_is_direct_and_deterministic() -> None:
    panel = _panel(76)
    calendar = _future_calendar(panel)
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    grid = _grid(panel)
    features = load_feature_config(ROOT / "configs/task2a_features.yaml")
    first = run_final_inference(panel, table, calendar, grid, _config(), features)
    second = run_final_inference(panel, table, calendar, grid, _config(), features)
    pd.testing.assert_frame_equal(first["predictions"], second["predictions"])
    assert len(first["predictions"]) == len(grid)
    assert np.isfinite(first["predictions"][["pred_total_volume_m3", "pred_chilled_volume_m3"]].to_numpy()).all()
    assert first["predictions"].loc[first["predictions"].brand.eq("Tech"), "pred_chilled_volume_m3"].eq(0.0).all()
    changed = panel.copy()
    changed.loc[changed.week_start_date.eq(changed.week_start_date.max()), "total_volume_m3"] += 1000
    changed_result = run_final_inference(changed, build_direct_multihorizon_table(changed, _calendar(changed)),
        calendar, grid, _config(), features)
    # A direct final forecast must not update later horizons from an h=1 outcome;
    # all changes here arise only from origin-known history, not recursive use.
    assert changed_result["features"].groupby(["depot", "brand"])["total_lag_1"].nunique().eq(1).all()
