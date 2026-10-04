"""Synthetic-only tests for Phase 13 direct multi-horizon training assembly."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.build_task2a_features import sanitized_console_lines, validate_phase13_output_paths
from src.task2a.calendar_features import build_target_week_calendar_features
from src.task2a.features import FeatureValidationError, audit_future_demand_leakage
from src.task2a.multihorizon import (
    MultiHorizonValidationError,
    assemble_phase13_artifacts,
    build_direct_multihorizon_table,
    validate_multihorizon_table,
)


def _panel(n: int = 66, status: str = "OBSERVED_DEMAND") -> pd.DataFrame:
    dates = pd.date_range("2020-10-05", periods=n, freq="7D")
    iso = dates.isocalendar()
    totals = np.arange(1, n + 1, dtype=float)
    return pd.DataFrame({
        "depot": "P", "brand": "Fresh", "iso_year": iso.year.astype(int).to_numpy(), "iso_week": iso.week.astype(int).to_numpy(),
        "week_start_date": dates.to_numpy(), "week_end_date": (dates + pd.Timedelta(days=6)).to_numpy(),
        "total_volume_m3": totals, "chilled_volume_m3": totals / 2,
        "panel_status": status,
    })


def _calendar(panel: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(panel.week_start_date.min(), panel.week_start_date.max() + pd.Timedelta(days=6), freq="D")
    iso = dates.isocalendar()
    return pd.DataFrame({
        "date": dates.to_numpy(), "iso_year": iso.year.astype(int).to_numpy(), "iso_week": iso.week.astype(int).to_numpy(),
        "is_operating": [1 if value.weekday() < 5 else 0 for value in dates],
        "is_weekend": [1 if value.weekday() >= 5 else 0 for value in dates],
        "is_payday": (dates.day == 25).astype(int),
        "festival": np.where(dates.day == 10, "Zeta", ""),
        "festival_ramp": np.where(dates.day == 9, 0.5, 0.0),
        "is_holiday": (dates.day == 15).astype(int), "monsoon": (dates.month == 11).astype(int),
    })


def test_direct_table_has_horizons_target_alignment_and_tail_omission() -> None:
    panel = _panel()
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    assert table.horizon_weeks.min() == 1 and table.horizon_weeks.max() == 10
    assert pd.to_datetime(table.target_week_start_date).max() == panel.week_start_date.iloc[-1]
    assert table.loc[table.horizon_weeks.eq(10), "origin_week_start_date"].max() == panel.week_start_date.iloc[-11]
    assert (pd.to_datetime(table.target_week_start_date) - pd.to_datetime(table.origin_week_start_date)).dt.days.eq(table.horizon_weeks * 7).all()
    sample = table.loc[(table.origin_week_start_date == panel.week_start_date.iloc[20]) & (table.horizon_weeks == 10)].iloc[0]
    assert sample.target_total_volume_m3 == panel.total_volume_m3.iloc[30]
    assert sample.target_chilled_volume_m3 == panel.chilled_volume_m3.iloc[30]


def test_same_origin_predictors_are_identical_except_horizon_and_target_context() -> None:
    panel = _panel()
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    group = table.loc[table.origin_week_start_date.eq(panel.week_start_date.iloc[20])]
    safe_origin_columns = [column for column in table if column.startswith(("total_lag", "chilled_lag", "total_rolling", "chilled_rolling", "total_trend", "chilled_trend"))]
    assert len(group) == 10
    assert all(group[column].nunique(dropna=False) == 1 for column in safe_origin_columns)
    assert group.horizon_weeks.nunique() == 10
    assert group.target_iso_week.nunique() > 1


def test_h10_future_or_intermediate_mutation_never_changes_earlier_origin_predictors() -> None:
    panel = _panel()
    calendar = _calendar(panel)
    baseline = build_direct_multihorizon_table(panel, calendar)
    altered = panel.copy()
    altered.loc[altered.index >= 31, "total_volume_m3"] = 50000.0
    altered.loc[altered.index >= 31, "chilled_volume_m3"] = 25000.0
    mutated = build_direct_multihorizon_table(altered, calendar)
    key = (baseline.origin_week_start_date.eq(panel.week_start_date.iloc[20])) & baseline.horizon_weeks.eq(10)
    compare = [column for column in baseline if column.startswith(("total_lag", "chilled_lag", "total_rolling", "chilled_rolling", "total_trend", "chilled_trend"))]
    pd.testing.assert_series_equal(baseline.loc[key, compare].iloc[0], mutated.loc[key, compare].iloc[0])


def test_only_observed_or_confirmed_zero_rows_become_targets() -> None:
    panel = _panel()
    panel.loc[30, "panel_status"] = "BOUNDARY_PARTIAL"
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    assert not table.target_panel_status.eq("BOUNDARY_PARTIAL").any()
    panel.loc[31, "panel_status"] = "UNRESOLVED_GAP"
    with pytest.raises(MultiHorizonValidationError, match="unresolved"):
        build_direct_multihorizon_table(panel, _calendar(panel))


def test_target_calendar_uses_phase12_context_and_rejects_incomplete_target_week() -> None:
    panel = _panel()
    calendar = _calendar(panel)
    context = build_target_week_calendar_features(calendar)
    assert context.target_operating_days.eq(5).all()
    incomplete = calendar.drop(calendar.index[-1]).reset_index(drop=True)
    with pytest.raises(MultiHorizonValidationError, match="calendar coverage"):
        build_direct_multihorizon_table(panel, incomplete)


def test_target_calendar_is_joined_to_target_not_origin_week() -> None:
    panel = _panel()
    calendar = _calendar(panel)
    origin = panel.week_start_date.iloc[20]
    target = origin + pd.Timedelta(weeks=1)
    calendar.loc[calendar.date.between(target, target + pd.Timedelta(days=6)), "is_operating"] = 0
    table = build_direct_multihorizon_table(panel, calendar)
    row = table.loc[table.origin_week_start_date.eq(origin) & table.horizon_weeks.eq(1)].iloc[0]
    assert row.target_operating_days == 0
    assert build_target_week_calendar_features(_calendar(panel)).loc[
        lambda frame: frame.iso_year.eq(origin.isocalendar().year) & frame.iso_week.eq(origin.isocalendar().week),
        "target_operating_days",
    ].iloc[0] == 5


@pytest.mark.parametrize("brand", ["Style", "Tech"])
def test_nonfresh_direct_targets_preserve_exact_zero_chilled(brand: str) -> None:
    panel = _panel()
    panel["brand"] = brand
    panel["chilled_volume_m3"] = 0.0
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    assert table.target_chilled_volume_m3.eq(0).all()


def test_labels_are_not_features_and_validator_detects_illegal_horizon_variation() -> None:
    panel = _panel()
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    assert "target_total_volume_m3" not in [column for column in table if column.startswith("feature_")]
    bad = table.copy()
    index = bad.index[1]
    bad.loc[index, "total_lag_1"] += 1
    with pytest.raises(MultiHorizonValidationError, match="vary"):
        validate_multihorizon_table(bad)


def test_artifact_summary_is_aggregate_only_and_paths_are_private() -> None:
    panel = _panel()
    artifacts = assemble_phase13_artifacts(panel, _calendar(panel))
    assert artifacts["summary"]["status"] == "PASS"
    assert artifacts["summary"]["feature_coverage"]["n_predictors"] > 0
    allowed = validate_phase13_output_paths(
        Path("data/interim/task2a_origin_features.csv"), Path("data/interim/task2a_multihorizon_train.csv"),
        Path("reports/private/phase13_task2a_features/nested"),
    )
    assert allowed[-1].name == "nested"
    with pytest.raises(ValueError, match="inside"):
        validate_phase13_output_paths(Path("outputs/public.csv"), Path("data/interim/x.csv"), Path("reports/private/phase13_task2a_features"))


def test_lineage_audit_reconciles_each_demand_predictor_to_canonical_history() -> None:
    panel = _panel()
    table = build_direct_multihorizon_table(panel, _calendar(panel))
    audit = audit_future_demand_leakage(panel, table)
    assert audit["status"] == "PASS" and audit["reconciled_demand_feature_count"] > 0
    altered = table.copy()
    altered.loc[altered.index[0], "total_lag_1"] += 1.0
    with pytest.raises(FeatureValidationError, match="lineage mismatch"):
        audit_future_demand_leakage(panel, altered)


def test_console_summary_is_limited_to_sanitized_status_and_counts() -> None:
    lines = sanitized_console_lines({"n_origin_rows": 7, "n_multihorizon_rows": 21})
    output = "\n".join(lines).lower()
    assert "delivery_id" not in output and "total_volume" not in output and "chilled_volume" not in output
    assert lines[-1] == "PRIVATE WEEKLY VALUES OR ORDER IDENTIFIERS PRINTED: NO"
