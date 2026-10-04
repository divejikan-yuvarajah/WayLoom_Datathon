"""Synthetic-only tests of the frozen Phase 14 rolling-origin contract."""

from __future__ import annotations

from pathlib import Path
from argparse import Namespace

import numpy as np
import pandas as pd
import pytest

from scripts import build_task2a_validation_plan as plan_script
from scripts.build_task2a_validation_plan import validate_private_output_dir
from src.task2a.features import get_task2a_feature_columns
from src.task2a.multihorizon import build_direct_multihorizon_table
from src.task2a.validation import (
    ForecastValidationError,
    build_rolling_origin_plan,
    load_validation_config,
    validate_ten_week_window,
)


ROOT = Path(__file__).resolve().parents[1]


def _panel(weeks: int = 76, series: tuple[tuple[str, str], ...] = (("A", "Fresh"), ("A", "Tech"))) -> pd.DataFrame:
    dates = pd.date_range("2020-10-05", periods=weeks, freq="7D")
    iso = dates.isocalendar()
    chunks = []
    for depot, brand in series:
        totals = np.arange(1, weeks + 1, dtype=float) + (10 if depot == "B" else 0)
        chunks.append(pd.DataFrame({
            "depot": depot, "brand": brand,
            "iso_year": iso.year.to_numpy(dtype=int), "iso_week": iso.week.to_numpy(dtype=int),
            "week_start_date": dates.to_numpy(), "week_end_date": (dates + pd.Timedelta(days=6)).to_numpy(),
            "total_volume_m3": totals,
            "chilled_volume_m3": totals / 2 if brand == "Fresh" else np.zeros(weeks),
            "panel_status": "OBSERVED_DEMAND",
        }))
    return pd.concat(chunks, ignore_index=True)


def _calendar(panel: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(panel.week_start_date.min(), panel.week_start_date.max() + pd.Timedelta(days=6), freq="D")
    iso = dates.isocalendar()
    return pd.DataFrame({
        "date": dates.to_numpy(), "iso_year": iso.year.to_numpy(dtype=int), "iso_week": iso.week.to_numpy(dtype=int),
        "is_operating": (dates.dayofweek < 5).astype(int), "is_weekend": (dates.dayofweek >= 5).astype(int),
        "is_payday": (dates.day == 25).astype(int), "festival": "", "festival_ramp": 0.0,
        "is_holiday": 0, "monsoon": 0,
    })


def _config(*, backtests: int = 2, minimum: int = 20) -> dict:
    config = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    config["backtesting"]["n_backtests"] = backtests
    config["backtesting"]["minimum_training_weeks"] = minimum
    return config


def _inputs(weeks: int = 76, series: tuple[tuple[str, str], ...] = (("A", "Fresh"), ("A", "Tech"))) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = _panel(weeks, series)
    return panel, build_direct_multihorizon_table(panel, _calendar(panel))


def test_rolling_plan_is_deterministic_and_training_uses_label_cutoff() -> None:
    panel, table = _inputs()
    config = _config()
    plan = build_rolling_origin_plan(panel, table, None, config)
    shuffled = build_rolling_origin_plan(panel.sample(frac=1, random_state=4), table.sample(frac=1, random_state=5), None, config)
    splits = plan["splits"]
    assert [split.origin_week_start_date for split in splits] == [split.origin_week_start_date for split in shuffled["splits"]]
    assert len(splits) == 2 and splits[1].origin_week_start_date - splits[0].origin_week_start_date >= pd.Timedelta(weeks=10)
    assert set(splits[0].train_indices).issubset(set(splits[1].train_indices))
    for split in splits:
        train = plan["table"].iloc[split.train_indices]
        valid = plan["table"].iloc[split.validation_indices]
        assert len(valid) == 20
        assert train.target_week_start_date.max() <= split.origin_week_start_date
        assert valid.target_week_start_date.min() > split.origin_week_start_date
        assert not set(split.train_indices).intersection(split.validation_indices)
        leaked_candidate = plan["table"].loc[
            plan["table"].origin_week_start_date.lt(split.origin_week_start_date)
            & plan["table"].target_week_start_date.gt(split.origin_week_start_date)
        ]
        assert not leaked_candidate.empty
        assert not set(leaked_candidate.index).intersection(split.train_indices)


def test_origin_choice_ignores_target_magnitude_and_future_labels() -> None:
    panel, table = _inputs()
    config = _config()
    baseline = build_rolling_origin_plan(panel, table, None, config)
    changed = panel.copy()
    changed["total_volume_m3"] += 1000
    changed.loc[changed.brand.eq("Fresh"), "chilled_volume_m3"] += 100
    changed_table = build_direct_multihorizon_table(changed, _calendar(changed))
    mutated = build_rolling_origin_plan(changed, changed_table, None, config)
    assert [split.origin_week_start_date for split in baseline["splits"]] == [split.origin_week_start_date for split in mutated["splits"]]


def test_frozen_default_selects_four_full_windows_for_six_synthetic_series() -> None:
    required = tuple((depot, brand) for depot in ("A", "B") for brand in ("Fresh", "Style", "Tech"))
    panel, table = _inputs(117, required)
    config = load_validation_config(ROOT / "configs/task2a_validation.yaml")
    plan = build_rolling_origin_plan(panel, table, None, config)
    assert len(plan["splits"]) == 4
    assert [split.origin_week_start_date for split in plan["splits"]] == [
        panel.week_start_date.iloc[index] for index in (76, 86, 96, 106)
    ]
    assert all(len(split.validation_indices) == 60 for split in plan["splits"])


@pytest.mark.parametrize("horizon", [0, 11])
def test_out_of_range_horizons_fail(horizon: int) -> None:
    panel, table = _inputs()
    table.loc[table.index[0], "horizon_weeks"] = horizon
    with pytest.raises(ForecastValidationError):
        build_rolling_origin_plan(panel, table, None, _config())


def test_exact_window_rejects_missing_duplicate_and_misaligned_horizon() -> None:
    panel, table = _inputs()
    origin = panel.week_start_date.iloc[30]
    series = ("A", "Fresh")
    validate_ten_week_window(table, origin, series)
    block = table.loc[table.depot.eq("A") & table.brand.eq("Fresh") & table.origin_week_start_date.eq(origin)].copy()
    with pytest.raises(ForecastValidationError):
        validate_ten_week_window(block.loc[block.horizon_weeks.ne(5)], origin, series)
    with pytest.raises(ForecastValidationError):
        validate_ten_week_window(pd.concat([block.loc[block.horizon_weeks.ne(5)], block.loc[block.horizon_weeks.eq(4)]]), origin, series)
    block.loc[block.horizon_weeks.eq(10), "target_week_start_date"] += pd.Timedelta(weeks=1)
    with pytest.raises(ForecastValidationError):
        validate_ten_week_window(block, origin, series)


def test_global_origin_rejects_incomplete_required_series_and_short_history() -> None:
    panel, table = _inputs()
    latest = panel.week_start_date.iloc[-11]
    missing = table.loc[~(table.depot.eq("A") & table.brand.eq("Tech")
                          & table.origin_week_start_date.eq(latest) & table.horizon_weeks.eq(10))]
    plan = build_rolling_origin_plan(panel, missing, None, _config())
    assert plan["splits"][-1].origin_week_start_date < latest
    with pytest.raises(ForecastValidationError, match="INSUFFICIENT_BACKTEST_HISTORY"):
        build_rolling_origin_plan(panel, table, None, _config(backtests=4, minimum=70))
    absent = table.loc[table.brand.ne("Tech")]
    with pytest.raises(ForecastValidationError, match="Required panel series"):
        build_rolling_origin_plan(panel, absent, None, _config())


def test_future_demand_mutations_leave_entire_validation_x_unchanged() -> None:
    panel, table = _inputs()
    config = _config()
    baseline = build_rolling_origin_plan(panel, table, None, config)
    origin = baseline["splits"][-1].origin_week_start_date
    changed = panel.copy()
    mask = changed.week_start_date.gt(origin)
    changed.loc[mask, "total_volume_m3"] = 9999.0
    changed.loc[mask & changed.brand.eq("Fresh"), "chilled_volume_m3"] = 1234.0
    changed_table = build_direct_multihorizon_table(changed, _calendar(changed))
    altered = build_rolling_origin_plan(changed, changed_table, None, config)
    before = baseline["table"].iloc[baseline["splits"][-1].validation_indices]
    after = altered["table"].iloc[altered["splits"][-1].validation_indices]
    predictors = get_task2a_feature_columns()
    pd.testing.assert_frame_equal(before[predictors].reset_index(drop=True), after[predictors].reset_index(drop=True))
    before_h10 = before.loc[before.horizon_weeks.eq(10), predictors].reset_index(drop=True)
    after_h10 = after.loc[after.horizon_weeks.eq(10), predictors].reset_index(drop=True)
    pd.testing.assert_frame_equal(before_h10, after_h10)
    assert not before.target_total_volume_m3.equals(after.target_total_volume_m3)


def test_future_source_metadata_and_target_tampering_fail() -> None:
    panel, table = _inputs()
    future_source = table.copy()
    future_source.loc[future_source.index[0], "origin_demand_feature_max_source_week"] = (
        pd.Timestamp(future_source.loc[future_source.index[0], "origin_week_start_date"]) + pd.Timedelta(weeks=1))
    with pytest.raises(ForecastValidationError, match="source|origin"):
        build_rolling_origin_plan(panel, future_source, None, _config())
    bad_label = table.copy()
    bad_label.loc[bad_label.index[0], "target_total_volume_m3"] += 1
    with pytest.raises(ForecastValidationError, match="disagrees"):
        build_rolling_origin_plan(panel, bad_label, None, _config())


def test_cross_year_and_iso_week_53_window_is_valid() -> None:
    panel, table = _inputs()
    origin = pd.Timestamp("2020-12-14")
    assert panel.loc[panel.week_start_date.gt(origin) & panel.week_start_date.le(origin + pd.Timedelta(weeks=10)), "iso_week"].eq(53).any()
    validate_ten_week_window(table, origin, ("A", "Fresh"))


def test_private_path_is_restricted() -> None:
    assert validate_private_output_dir(Path("reports/private/phase14_task2a_validation"))
    with pytest.raises(ValueError):
        validate_private_output_dir(Path("reports/public"))


def test_csv_round_trip_matches_local_script_input_types(tmp_path: Path) -> None:
    panel, table = _inputs()
    panel_path = tmp_path / "synthetic_panel.csv"
    table_path = tmp_path / "synthetic_direct.csv"
    panel.to_csv(panel_path, index=False)
    table.to_csv(table_path, index=False)
    restored_panel = pd.read_csv(panel_path)
    restored_table = pd.read_csv(table_path)
    plan = build_rolling_origin_plan(restored_panel, restored_table, None, _config())
    assert len(plan["splits"]) == 2


def test_local_script_writes_private_metadata_and_sanitized_console(tmp_path: Path, monkeypatch, capsys) -> None:
    panel, table = _inputs()
    panel_path = tmp_path / "synthetic_panel.csv"
    table_path = tmp_path / "synthetic_direct.csv"
    panel.to_csv(panel_path, index=False)
    table.to_csv(table_path, index=False)
    output = tmp_path / "reports" / "private" / "phase14_task2a_validation"
    monkeypatch.setattr(plan_script, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(plan_script, "load_validation_config", lambda _: _config())
    monkeypatch.setattr(plan_script, "parse_args", lambda: Namespace(
        weekly_panel=panel_path, multihorizon_table=table_path,
        feature_config=ROOT / "configs/task2a_features.yaml",
        validation_config=ROOT / "configs/task2a_validation.yaml", output_dir=output,
    ))
    assert plan_script.main() == 0
    report = (output / "validation_plan.json").read_text(encoding="utf-8")
    console = capsys.readouterr().out
    assert '"backtest_id": "BT01"' in report
    assert '"train_indices"' in report and '"validation_indices"' in report
    assert "target_total_volume_m3" not in report
    assert "target_total_volume_m3" not in console and "delivery_id" not in console
    assert "LOCAL PHASE 14 VALIDATION PLAN: PASS" in console
