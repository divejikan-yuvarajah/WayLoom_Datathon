"""Synthetic-only unit tests for Phase 13 origin-safe Task 2A features."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest

from src.task2a.features import (
    FeatureValidationError,
    audit_future_demand_leakage,
    build_feature_registry,
    build_origin_demand_features,
    get_task2a_feature_columns,
    get_task2a_metadata_columns,
    get_task2a_target_columns,
    validate_feature_config,
)


def _dates(n: int = 65, start: str = "2020-10-05") -> pd.DatetimeIndex:
    return pd.date_range(start, periods=n, freq="7D")


def _panel(n: int = 65, brand: str = "Fresh", depot: str = "P") -> pd.DataFrame:
    dates = _dates(n)
    iso = dates.isocalendar()
    totals = np.arange(1, n + 1, dtype=float)
    return pd.DataFrame({
        "depot": depot, "brand": brand, "iso_year": iso.year.astype(int).to_numpy(), "iso_week": iso.week.astype(int).to_numpy(),
        "week_start_date": dates.to_numpy(), "week_end_date": (dates + pd.Timedelta(days=6)).to_numpy(),
        "total_volume_m3": totals, "chilled_volume_m3": totals / 2 if brand == "Fresh" else 0.0,
        "panel_status": "OBSERVED_DEMAND",
    })


def test_lag_semantics_rolling_and_year_boundary_are_exact() -> None:
    result = build_origin_demand_features(_panel())
    row = result.iloc[52]
    assert row.total_lag_1 == 53
    assert row.total_lag_2 == 52
    assert row.total_lag_4 == 50
    assert row.total_lag_13 == 41
    assert row.total_lag_52 == 2
    assert row.total_rolling_mean_4 == pytest.approx(np.mean([50, 51, 52, 53]))
    assert row.total_rolling_mean_13 == pytest.approx(np.mean(np.arange(41, 54)))
    assert row.total_trend_4_vs_13 == pytest.approx(np.mean([50, 51, 52, 53]) - np.mean(np.arange(41, 54)))
    assert row.history_weeks_available == 53
    assert result.iso_week.eq(53).any()  # no assumed 52-week year


def test_short_history_is_not_filled_and_safe_ratios_never_infinite() -> None:
    panel = _panel(15)
    panel["total_volume_m3"] = 0.0
    panel.loc[panel.index[-4:], "total_volume_m3"] = 2.0
    panel["chilled_volume_m3"] = panel["total_volume_m3"] / 2
    result = build_origin_demand_features(panel)
    assert result.loc[0, "total_lag_2"] != result.loc[0, "total_lag_2"]
    assert result.loc[11, "total_rolling_mean_13"] != result.loc[11, "total_rolling_mean_13"]
    zero_panel = _panel(13)
    zero_panel[["total_volume_m3", "chilled_volume_m3"]] = 0.0
    assert np.isnan(build_origin_demand_features(zero_panel).iloc[-1].total_trend_ratio_4_vs_13)
    assert not np.isinf(result.select_dtypes(include="number").to_numpy()).any()


def test_series_isolation_and_nonfresh_chilled_invariants() -> None:
    first = _panel(20, "Fresh", "A")
    second = _panel(20, "Style", "B")
    second["total_volume_m3"] = 1000.0
    result = build_origin_demand_features(pd.concat([first, second], ignore_index=True))
    fresh = result.loc[result.depot.eq("A")].reset_index(drop=True)
    style = result.loc[result.depot.eq("B")].reset_index(drop=True)
    assert fresh.loc[1, "total_lag_2"] == 1.0
    assert style.loc[1, "total_lag_2"] == 1000.0
    assert style.filter(regex="^chilled_").fillna(0).eq(0).all().all()


def test_future_mutation_cannot_change_prior_origin_features() -> None:
    panel = _panel(30)
    baseline = build_origin_demand_features(panel)
    changed = panel.copy()
    changed.loc[changed.index[20:], "total_volume_m3"] = 99999.0
    mutated = build_origin_demand_features(changed)
    columns = [name for name in baseline if name.startswith(("total_lag", "total_rolling", "total_trend", "chilled_"))]
    pd.testing.assert_frame_equal(baseline.loc[:19, columns], mutated.loc[:19, columns])


def test_duplicate_nonweekly_and_chilled_errors_block_before_features() -> None:
    panel = _panel(5)
    with pytest.raises(FeatureValidationError, match="duplicate"):
        build_origin_demand_features(pd.concat([panel, panel.iloc[[0]]], ignore_index=True))
    broken = panel.copy()
    broken.loc[2, "week_start_date"] += pd.Timedelta(days=7)
    with pytest.raises(FeatureValidationError, match="ISO|chronology"):
        build_origin_demand_features(broken)
    broken = _panel(5, "Tech")
    broken.loc[0, "chilled_volume_m3"] = 1.0
    with pytest.raises(FeatureValidationError, match="exactly zero"):
        build_origin_demand_features(broken)


def test_registry_excludes_labels_and_metadata_from_model_matrix() -> None:
    registry = build_feature_registry()
    features = get_task2a_feature_columns()
    assert {"target_total_volume_m3", "target_chilled_volume_m3"}.isdisjoint(features)
    assert set(get_task2a_metadata_columns()).isdisjoint(features)
    assert set(get_task2a_target_columns()).isdisjoint(features)
    assert registry.loc[registry.feature_name.eq("target_total_volume_m3"), "role"].iloc[0] == "excluded"
    assert registry.loc[registry.role.eq("feature"), "selection_status"].eq("enabled").all()
    required_lineage = {
        "feature_name", "feature_group", "source", "source_columns", "formula", "availability_type",
        "prediction_time_safe", "uses_future_actual_demand", "requires_history_weeks", "categorical", "nullable", "status", "rationale",
    }
    assert required_lineage.issubset(registry.columns)
    enabled = registry.loc[registry.status.eq("enabled")]
    assert enabled.prediction_time_safe.all() and not enabled.uses_future_actual_demand.any()


def test_invalid_feature_configuration_blocks_unsafe_horizon_or_windows() -> None:
    with pytest.raises(FeatureValidationError):
        validate_feature_config({"horizon": {"max_weeks": 0}})
    with pytest.raises(FeatureValidationError):
        validate_feature_config({"lags": {"weeks": [0]}})
    with pytest.raises(FeatureValidationError):
        validate_feature_config({"multihorizon": {"min_horizon": 0, "max_horizon": 10}})
