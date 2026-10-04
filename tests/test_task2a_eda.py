"""Synthetic-only tests for Phase 12 Task 2A EDA."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.task2a.eda import (
    EDAValidationError,
    analyze_festival_context,
    analyze_festival_ramp,
    analyze_holiday_context,
    analyze_monsoon_context,
    analyze_operating_days,
    analyze_payday_context,
    analyze_recent_trend,
    analyze_yearly_seasonality,
    build_weekly_calendar_context,
    compare_same_week_across_years,
    detect_weekly_spikes,
    run_task2a_eda,
    summarize_fresh_chilled_demand,
    summarize_weekly_total_demand,
    validate_task2a_eda_input,
)
from scripts.run_task2a_eda import validate_private_output_dir


def _panel(dates: list[str], values: list[float] | None = None, brand: str = "Fresh") -> pd.DataFrame:
    dates_parsed = pd.to_datetime(dates)
    iso = dates_parsed.isocalendar()
    volume = values or [10.0] * len(dates)
    chilled = [min(2.0, value) if brand == "Fresh" else 0.0 for value in volume]
    return pd.DataFrame({
        "depot": ["Peliyagoda"] * len(dates), "brand": [brand] * len(dates), "iso_year": iso.year.astype(int).tolist(), "iso_week": iso.week.astype(int).tolist(),
        "week_start_date": dates_parsed, "week_end_date": dates_parsed + pd.Timedelta(days=6),
        "total_volume_m3": volume, "chilled_volume_m3": chilled,
        "panel_status": ["OBSERVED_DEMAND"] * len(dates),
    })


def _weekly_dates(year: int, weeks: list[int]) -> list[str]:
    import datetime
    return [datetime.date.fromisocalendar(year, week, 1).isoformat() for week in weeks]


def _calendar(dates: list[str]) -> pd.DataFrame:
    chunks = []
    for start in dates:
        days = pd.date_range(start, periods=7, freq="D")
        iso = days.isocalendar()
        chunks.append(pd.DataFrame({
            "date": days, "iso_year": iso.year.astype(int), "iso_week": iso.week.astype(int),
            "is_operating": [1, 1, 1, 1, 1, 0, 0], "is_weekend": [0, 0, 0, 0, 0, 1, 1],
            "is_payday": [0, 1, 0, 0, 0, 0, 0], "festival": ["", "Zeta", "", "Alpha", "Zeta", "", ""],
            "festival_ramp": [0.0, .25, .5, .75, 1.0, .5, 0.0],
            "is_holiday": [0, 0, 1, 0, 0, 0, 0], "monsoon": [0, 1, 1, 0, 0, 0, 0],
        }))
    return pd.concat(chunks, ignore_index=True)


def test_panel_validation_rejects_duplicate_keys_bad_targets_and_blockers() -> None:
    good = _panel(_weekly_dates(2020, [52, 53]) + _weekly_dates(2021, [1, 2]), [0, 4, 5, 6])
    assert len(validate_task2a_eda_input(good)) == 4
    with pytest.raises(EDAValidationError, match="duplicate"):
        validate_task2a_eda_input(pd.concat([good, good.iloc[[0]]], ignore_index=True))
    for bad in (-1.0, np.nan, np.inf):
        invalid = good.copy()
        invalid["total_volume_m3"] = invalid.total_volume_m3.astype(float)
        invalid.loc[0, "total_volume_m3"] = bad
        with pytest.raises(EDAValidationError):
            validate_task2a_eda_input(invalid)
    invalid = good.copy()
    invalid.loc[0, "chilled_volume_m3"] = 1
    with pytest.raises(EDAValidationError, match="exceeds"):
        validate_task2a_eda_input(invalid)
    for brand in ("Style", "Tech"):
        invalid = _panel(_weekly_dates(2024, [1]), [5], brand)
        invalid.loc[0, "chilled_volume_m3"] = 1
        with pytest.raises(EDAValidationError, match="exactly zero"):
            validate_task2a_eda_input(invalid)
    invalid = good.copy()
    invalid.loc[0, "panel_status"] = "UNRESOLVED_GAP"
    with pytest.raises(EDAValidationError, match="unresolved"):
        validate_task2a_eda_input(invalid)
    invalid = good.copy()
    invalid.loc[0, "iso_week"] = 54
    with pytest.raises(EDAValidationError, match="ISO"):
        validate_task2a_eda_input(invalid)
    invalid = good.copy()
    invalid.loc[0, "iso_week"] = 51
    with pytest.raises(EDAValidationError, match="dates and official ISO"):
        validate_task2a_eda_input(invalid)


def test_weekly_calendar_context_aggregates_official_fields_deterministically() -> None:
    dates = _weekly_dates(2024, [1, 2])
    panel = _panel(dates)
    context = build_weekly_calendar_context(_calendar(dates), panel)
    week = context.loc[context.iso_week.eq(1)].iloc[0]
    assert week.calendar_days == 7
    assert week.operating_days == 5
    assert week.weekend_days == 2
    assert week.payday_days == 1 and week.has_payday == 1
    assert week.holiday_days == 1 and week.has_holiday == 1
    assert week.festival_days == 3 and week.has_festival == 1
    assert week.festival_names == "Alpha|Zeta"
    assert week.max_festival_ramp == 1.0
    assert week.mean_festival_ramp == pytest.approx(3 / 7)
    assert week.monsoon_days == 2 and week.monsoon_day_fraction == pytest.approx(2 / 7)
    assert week.has_monsoon_day == 1


def test_calendar_rejects_invalid_flags_ramp_and_partial_panel_coverage() -> None:
    dates = _weekly_dates(2024, [1])
    panel = _panel(dates)
    for column, value in (("is_payday", 2), ("is_holiday", -1), ("monsoon", 3), ("is_operating", 4), ("festival_ramp", 1.1), ("festival_ramp", -.1)):
        calendar = _calendar(dates)
        calendar.loc[0, column] = value
        with pytest.raises(EDAValidationError):
            build_weekly_calendar_context(calendar, panel)
    with pytest.raises(EDAValidationError, match="coverage"):
        build_weekly_calendar_context(_calendar(dates).iloc[:-1], panel)


def test_total_and_fresh_chilled_summaries_preserve_zero_and_safe_share() -> None:
    dates = _weekly_dates(2024, [1, 2, 3])
    panel = _panel(dates, [10, 0, 30])
    panel.loc[0, "chilled_volume_m3"] = 3
    panel.loc[1, "chilled_volume_m3"] = 0
    totals = summarize_weekly_total_demand(panel)
    assert totals.iloc[0].n_weeks == 3
    assert totals.iloc[0].min_total_volume_m3 == 0
    assert totals.iloc[0].start_week == dates[0]
    summary, fresh = summarize_fresh_chilled_demand(panel)
    assert summary.iloc[0].n_weeks == 3
    assert summary.iloc[0].mean_chilled_share == pytest.approx((3 / 10 + 2 / 30) / 2)
    assert np.isnan(fresh.loc[1, "chilled_share"])
    assert not np.isinf(fresh.chilled_share.dropna()).any()


def test_trends_up_down_flat_short_and_zero_prior_are_explicit() -> None:
    dates = _weekly_dates(2023, list(range(1, 15)))
    for values, sign in ((list(range(1, 15)), 1), (list(range(14, 0, -1)), -1), ([5] * 14, 0)):
        result = analyze_recent_trend(_panel(dates, values), windows=[4], minimum_history_weeks=4).iloc[0]
        assert result.status == "SUFFICIENT"
        assert result.descriptive_slope == pytest.approx(0.0) if sign == 0 else np.sign(result.descriptive_slope) == sign
    short = analyze_recent_trend(_panel(dates[:3], [1, 2, 3]), windows=[4], minimum_history_weeks=4).iloc[0]
    assert short.status == "INSUFFICIENT_HISTORY"
    assert pd.isna(short.recent_mean)
    zero_prior = analyze_recent_trend(_panel(dates[:8], [0, 0, 0, 0, 2, 2, 2, 2]), windows=[4], minimum_history_weeks=4).iloc[0]
    assert zero_prior.absolute_change == 2
    assert pd.isna(zero_prior.percent_change)


def test_trend_comparison_support_is_not_reported_sufficient_without_prior_window() -> None:
    dates = _weekly_dates(2023, list(range(1, 27)))
    at_13 = analyze_recent_trend(_panel(dates[:13], list(range(1, 14))), windows=[13], minimum_history_weeks=8).iloc[0]
    assert at_13.rolling_status == "SUFFICIENT"
    assert at_13.comparison_status == "INSUFFICIENT_PRIOR_HISTORY"
    assert at_13.status == "INSUFFICIENT_PRIOR_HISTORY"
    assert pd.isna(at_13.prior_equal_length_mean)
    at_26 = analyze_recent_trend(_panel(dates, list(range(1, 27))), windows=[13], minimum_history_weeks=8).iloc[0]
    assert at_26.status == "SUFFICIENT"
    assert at_26.comparison_status == "SUFFICIENT"


def test_seasonality_and_same_week_comparison_support_week53_and_missing_year() -> None:
    all_weeks = pd.date_range(_weekly_dates(2020, [1])[0], _weekly_dates(2026, [53])[0], freq="7D").strftime("%Y-%m-%d").tolist()
    frame = _panel(all_weeks, [10.0] * len(all_weeks))
    frame.loc[frame.iso_year.eq(2026) & frame.iso_week.eq(53), "total_volume_m3"] = 20.0
    frame.loc[frame.iso_week.eq(53) & frame.iso_year.eq(2020), "total_volume_m3"] = 10.0
    one_year = _panel(_weekly_dates(2024, [1, 2]), [0, 2], brand="Style")
    frame = pd.concat([frame, one_year], ignore_index=True)
    season = analyze_yearly_seasonality(frame, minimum_years=2)
    week53 = season.loc[season.iso_week.eq(53)].iloc[0]
    assert week53.n_years == 2 and week53.seasonality_support == "SUPPORTED"
    same = compare_same_week_across_years(frame)
    week53_same = same.loc[same.iso_week.eq(53)].iloc[0]
    assert week53_same.years == [2020, 2026]
    assert week53_same.first_year == 2020 and week53_same.last_year == 2026
    import json
    assert json.loads(week53_same.year_over_year_changes)[0]["from_year"] == 2020
    style = same.loc[same.brand.eq("Style") & same.iso_week.eq(1)].iloc[0]
    assert style.status == "SAME_WEEK_COMPARISON_UNAVAILABLE"
    zero_dates = pd.date_range(_weekly_dates(2023, [1])[0], _weekly_dates(2024, [2])[0], freq="7D").strftime("%Y-%m-%d").tolist()
    zero_base = _panel(zero_dates, [1.0] * len(zero_dates))
    zero_base.loc[zero_base.iso_year.eq(2023) & zero_base.iso_week.eq(2), "total_volume_m3"] = 0
    zero_base.loc[zero_base.iso_year.eq(2023) & zero_base.iso_week.eq(2), "chilled_volume_m3"] = 0
    zero_base.loc[zero_base.iso_year.eq(2024) & zero_base.iso_week.eq(2), "total_volume_m3"] = 5
    zero_base.loc[zero_base.iso_year.eq(2024) & zero_base.iso_week.eq(2), "chilled_volume_m3"] = 2
    changes = json.loads(compare_same_week_across_years(zero_base).query("iso_week == 2").iloc[0].year_over_year_changes)[0]
    assert changes["absolute_change"] == 5 and changes["percent_change"] is None


def test_calendar_context_analyses_keep_festival_holiday_distinct_and_support() -> None:
    dates = _weekly_dates(2024, [1, 2, 3])
    panel = _panel(dates, [10, 20, 30])
    calendar = _calendar(dates)
    calendar.loc[calendar.iso_week.eq(2), "festival"] = ""
    calendar.loc[calendar.iso_week.eq(2), "is_holiday"] = 0
    calendar.loc[calendar.iso_week.eq(3), "festival"] = ""
    calendar.loc[calendar.iso_week.eq(3), "is_holiday"] = 1
    context = build_weekly_calendar_context(calendar, panel)
    festival, names = analyze_festival_context(panel, context)
    assert set(festival.has_festival) == {0, 1}
    assert festival.n_weeks.sum() == len(panel)
    assert set(names.festival_name) == {"Alpha", "Zeta"}
    assert names.support_warning.eq("LOW_SUPPORT").all()
    ramp_weekly, ramp = analyze_festival_ramp(panel, context)
    assert ramp_weekly.max_festival_ramp.between(0, 1).all()
    assert ramp.n_weeks.sum() == len(panel)
    payday = analyze_payday_context(panel, context)
    holiday = analyze_holiday_context(panel, context)
    assert payday.n_weeks.sum() == 3 and holiday.n_weeks.sum() == 3
    assert analyze_monsoon_context(panel, context)[1].n_weeks.sum() == 3
    assert analyze_operating_days(panel, context).n_weeks.sum() == 3


def test_operating_day_zero_is_kept_without_per_day_infinity() -> None:
    dates = _weekly_dates(2024, [1, 2])
    panel = _panel(dates, [7, 9])
    # Phase 11's canonical panel can already include this field; EDA must
    # prefer the freshly aggregated official calendar context without suffixes.
    panel["operating_days"] = [6, 6]
    calendar = _calendar(dates)
    calendar.loc[calendar.iso_week.eq(1), "is_operating"] = 0
    context = build_weekly_calendar_context(calendar, panel)
    assert context.loc[context.iso_week.eq(1), "operating_days"].iloc[0] == 0
    result = analyze_operating_days(panel, context)
    assert 0 in result.operating_days.values
    assert np.isfinite(result.mean_volume).all()


def test_spike_detector_flags_up_and_down_without_mutating_target() -> None:
    dates = _weekly_dates(2023, list(range(1, 15)))
    values = [10] * 8 + [100, 10, 10, 10, 10, -0.01]
    # Keep valid nonnegative targets; a low positive point is the downward anomaly.
    values[-1] = 0
    panel = _panel(dates, values)
    before = panel.total_volume_m3.copy(deep=True)
    result = detect_weekly_spikes(panel, window=8, minimum_history=8, threshold=3.5)
    assert result.loc[result.iso_week.eq(9), "spike_direction"].iloc[0] == "UP"
    assert result.loc[result.iso_week.eq(14), "spike_direction"].iloc[0] == "DOWN"
    assert panel.total_volume_m3.equals(before)
    assert result.robust_z.dropna().map(np.isfinite).all()


def test_spike_mad_zero_insufficient_and_trend_safe() -> None:
    dates = _weekly_dates(2023, list(range(1, 14)))
    flat = detect_weekly_spikes(_panel(dates, [4] * 13), window=8, minimum_history=8)
    assert flat.iloc[-1].robust_z == 0
    assert not flat.iloc[-1].spike_flag
    change = detect_weekly_spikes(_panel(dates, [4] * 8 + [8] * 5), window=8, minimum_history=8)
    assert change.iloc[8].robust_z_status == "MAD_ZERO_DIFFERENT"
    assert change.iloc[8].spike_flag and pd.isna(change.iloc[8].robust_z)
    insufficient = detect_weekly_spikes(_panel(dates[:7], [1] * 7), window=13, minimum_history=8)
    assert insufficient.robust_z_status.eq("INSUFFICIENT_HISTORY").all()
    trend = detect_weekly_spikes(_panel(dates, list(range(1, 14))), window=8, minimum_history=8)
    assert not trend.loc[trend.rolling_history_n.ge(8), "spike_flag"].any()


def test_full_runner_writes_aggregate_private_outputs_and_figures(tmp_path: Path) -> None:
    dates = _weekly_dates(2024, [1, 2, 3])
    panel = _panel(dates, [10, 0, 30])
    panel["operating_days"] = [6, 6, 6]
    result = run_task2a_eda(panel, _calendar(dates), {"trend": {"windows_weeks": [2], "minimum_history_weeks": 2}}, tmp_path / "reports" / "private", make_plots=True)
    output = tmp_path / "reports" / "private"
    assert result["summary"]["status"] == "PASS"
    for name in ("eda_summary.json", "weekly_calendar_context.json", "feature_candidates.json", "warnings.json", "phase12_eda_report.md", "total_demand_summary.csv", "spike_analysis.csv"):
        assert (output / name).is_file()
    assert list((output / "figures").glob("*.png"))
    assert result["spikes"].total_volume_m3.tolist() == panel.total_volume_m3.tolist()


def test_cli_output_directory_is_limited_to_phase12_private_reports(tmp_path: Path) -> None:
    allowed = validate_private_output_dir(Path("reports/private/phase12_task2a_eda/nested"))
    assert allowed.name == "nested"
    with pytest.raises(ValueError, match="inside reports/private"):
        validate_private_output_dir(tmp_path / "public")
    with pytest.raises(ValueError, match="inside reports/private"):
        validate_private_output_dir(Path("reports/private/other_phase"))
