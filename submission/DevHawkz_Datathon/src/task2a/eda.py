"""Descriptive, privacy-safe Phase 12 EDA over the canonical Task 2A panel."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


class EDAValidationError(ValueError):
    """Raised when canonical panel or official calendar input violates contract."""


SERIES_KEYS = ["depot", "brand"]
WEEK_KEYS = ["iso_year", "iso_week"]
PANEL_KEYS = SERIES_KEYS + WEEK_KEYS
CALENDAR_CONTEXT_COLUMNS = [
    "calendar_days", "operating_days", "weekend_days", "payday_days", "has_payday",
    "holiday_days", "has_holiday", "festival_days", "has_festival", "festival_names",
    "max_festival_ramp", "mean_festival_ramp", "monsoon_days", "monsoon_day_fraction",
    "has_monsoon_day",
]


def load_eda_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise EDAValidationError("Task 2A EDA configuration must be a mapping.")
    return config


def _require(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise EDAValidationError(f"{label} missing required columns: {', '.join(missing)}")


def _numeric(frame: pd.DataFrame, column: str, label: str) -> pd.Series:
    converted = pd.to_numeric(frame[column], errors="coerce")
    if converted.isna().any() or not np.isfinite(converted.to_numpy(dtype=float)).all():
        raise EDAValidationError(f"{label}.{column} must contain finite numeric values.")
    return converted


def validate_task2a_eda_input(panel: pd.DataFrame) -> pd.DataFrame:
    """Validate without changing the caller's canonical Phase 11 panel."""
    required = PANEL_KEYS + ["total_volume_m3", "chilled_volume_m3"]
    _require(panel, required, "weekly panel")
    result = panel.copy(deep=True)
    for column in SERIES_KEYS:
        values = result[column].astype("string").str.strip()
        if values.isna().any() or values.eq("").any():
            raise EDAValidationError(f"weekly panel.{column} contains null or blank keys.")
        result[column] = values
    if not result["brand"].isin(["Fresh", "Style", "Tech"]).all():
        raise EDAValidationError("weekly panel.brand contains values outside the official brand domain.")
    for column, low, high in (("iso_year", 1, None), ("iso_week", 1, 53)):
        values = _numeric(result, column, "weekly panel")
        if not np.equal(values, np.floor(values)).all() or (values < low).any() or (high is not None and (values > high).any()):
            raise EDAValidationError(f"weekly panel.{column} contains invalid ISO values.")
        result[column] = values.astype(int)
    if result.duplicated(PANEL_KEYS).any():
        raise EDAValidationError("weekly panel contains duplicate depot/brand/ISO-week keys.")
    for column in ("total_volume_m3", "chilled_volume_m3"):
        result[column] = _numeric(result, column, "weekly panel")
        if (result[column] < 0).any():
            raise EDAValidationError(f"weekly panel.{column} must be nonnegative.")
    if (result["chilled_volume_m3"] > result["total_volume_m3"]).any():
        raise EDAValidationError("weekly panel chilled volume exceeds total volume.")
    for brand in ("Style", "Tech"):
        if not result.loc[result.brand.eq(brand), "chilled_volume_m3"].eq(0).all():
            raise EDAValidationError(f"{brand} chilled volume must be exactly zero.")
    status_col = "panel_status" if "panel_status" in result.columns else "week_status" if "week_status" in result.columns else None
    if status_col is None:
        raise EDAValidationError("weekly panel requires Phase 11 panel_status/week_status.")
    status = result[status_col].astype("string").str.upper()
    if status.isna().any() or status.eq("").any():
        raise EDAValidationError("weekly panel contains missing week status.")
    blockers = status.str.contains("UNRESOLVED|INCOMPLETE|BLOCKER", regex=True)
    if blockers.any():
        raise EDAValidationError("weekly panel contains unresolved or incomplete Phase 11 weeks.")
    result["week_status"] = status
    if "week_start_date" in result:
        result["week_start_date"] = pd.to_datetime(result["week_start_date"], errors="coerce").dt.normalize()
        if result["week_start_date"].isna().any():
            raise EDAValidationError("weekly panel.week_start_date contains invalid dates.")
    else:
        # ISO week Monday is used only to order already assigned official ISO keys.
        result["week_start_date"] = pd.to_datetime(
            result["iso_year"].astype(str) + "-W" + result["iso_week"].astype(str).str.zfill(2) + "-1",
                format="%G-W%V-%u", errors="coerce",
            )
    panel_iso = result["week_start_date"].dt.isocalendar()
    if not result["iso_year"].eq(panel_iso.year.to_numpy()).all() or not result["iso_week"].eq(panel_iso.week.to_numpy()).all():
        raise EDAValidationError("weekly panel dates and official ISO year/week keys are inconsistent.")
    result = result.sort_values(SERIES_KEYS + ["week_start_date", *WEEK_KEYS], kind="stable").reset_index(drop=True)
    if result.duplicated(SERIES_KEYS + ["week_start_date"]).any():
        raise EDAValidationError("weekly panel chronology has duplicate dates within a series.")
    for _, group in result.groupby(SERIES_KEYS, sort=False):
        dates = group.week_start_date.sort_values().diff().dropna().dt.days
        if not dates.eq(7).all():
            raise EDAValidationError("weekly panel chronology contains a missing or nonweekly interval.")
    return result


def validate_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    required = ["date", "iso_year", "iso_week", "is_operating", "is_weekend", "is_payday", "festival", "festival_ramp", "is_holiday", "monsoon"]
    _require(calendar, required, "official calendar")
    result = calendar.copy(deep=True)
    result["date"] = pd.to_datetime(result["date"], errors="coerce").dt.normalize()
    if result["date"].isna().any() or result["date"].duplicated().any():
        raise EDAValidationError("official calendar dates must be valid and unique.")
    for column, high in (("iso_year", None), ("iso_week", 53)):
        values = _numeric(result, column, "official calendar")
        if not np.equal(values, np.floor(values)).all() or (values < 1).any() or (high is not None and (values > high).any()):
            raise EDAValidationError(f"official calendar.{column} contains invalid values.")
        result[column] = values.astype(int)
    actual_iso = result["date"].dt.isocalendar()
    if not result["iso_year"].eq(actual_iso.year.to_numpy()).all() or not result["iso_week"].eq(actual_iso.week.to_numpy()).all():
        raise EDAValidationError("official calendar date and ISO year/week fields are inconsistent.")
    for column in ("is_operating", "is_weekend", "is_payday", "is_holiday", "monsoon"):
        values = _numeric(result, column, "official calendar")
        if not values.isin([0, 1]).all():
            raise EDAValidationError(f"official calendar.{column} must be in {{0,1}}.")
        result[column] = values.astype(int)
    result["festival_ramp"] = _numeric(result, "festival_ramp", "official calendar")
    if ((result["festival_ramp"] < 0) | (result["festival_ramp"] > 1)).any():
        raise EDAValidationError("official calendar.festival_ramp must be in [0,1].")
    result["festival"] = result["festival"].fillna("").astype("string").str.strip()
    return result


def build_weekly_calendar_context(calendar: pd.DataFrame, panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """Aggregate only official daily context, rejecting incomplete represented weeks."""
    cal = validate_calendar(calendar)
    cal["_has_festival"] = cal["festival"].ne("").astype(int)
    rows = []
    for (year, week), group in cal.groupby(WEEK_KEYS, sort=True):
        names = sorted(set(group.loc[group["festival"].ne(""), "festival"].astype(str)))
        rows.append({
            "iso_year": int(year), "iso_week": int(week), "calendar_days": int(len(group)),
            "operating_days": int(group.is_operating.sum()), "weekend_days": int(group.is_weekend.sum()),
            "payday_days": int(group.is_payday.sum()), "has_payday": int(group.is_payday.sum() > 0),
            "holiday_days": int(group.is_holiday.sum()), "has_holiday": int(group.is_holiday.sum() > 0),
            "festival_days": int(group._has_festival.sum()), "has_festival": int(group._has_festival.sum() > 0),
            "festival_names": "|".join(names), "max_festival_ramp": float(group.festival_ramp.max()),
            "mean_festival_ramp": float(group.festival_ramp.mean()), "monsoon_days": int(group.monsoon.sum()),
            "monsoon_day_fraction": float(group.monsoon.mean()), "has_monsoon_day": int(group.monsoon.sum() > 0),
        })
    weekly = pd.DataFrame(rows, columns=WEEK_KEYS + CALENDAR_CONTEXT_COLUMNS)
    if panel is not None:
        validated = validate_task2a_eda_input(panel)
        keys = validated[WEEK_KEYS].drop_duplicates()
        coverage = keys.merge(weekly[WEEK_KEYS + ["calendar_days"]], on=WEEK_KEYS, how="left", validate="one_to_one")
        if coverage.calendar_days.isna().any() or not coverage.calendar_days.eq(7).all():
            raise EDAValidationError("official calendar coverage is incomplete for one or more Phase 11 panel weeks.")
    return weekly


def _summary(group: pd.DataFrame, value: str, name: str) -> dict[str, Any]:
    values = group[value].astype(float)
    return {
        "n_weeks": int(values.count()), f"mean_{name}": float(values.mean()), f"median_{name}": float(values.median()),
        f"std_{name}": float(values.std(ddof=1)) if len(values) > 1 else None,
        f"min_{name}": float(values.min()), f"p25_{name}": float(values.quantile(.25)),
        f"p75_{name}": float(values.quantile(.75)), f"p90_{name}": float(values.quantile(.90)),
        f"p95_{name}": float(values.quantile(.95)), f"max_{name}": float(values.max()),
    }


def summarize_weekly_total_demand(panel: pd.DataFrame) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    rows = []
    for keys, group in frame.groupby(SERIES_KEYS, sort=True):
        row = dict(zip(SERIES_KEYS, keys))
        row.update({"start_week": str(group.week_start_date.min().date()), "end_week": str(group.week_start_date.max().date())})
        row.update(_summary(group, "total_volume_m3", "total_volume_m3"))
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_fresh_chilled_demand(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = validate_task2a_eda_input(panel)
    fresh = frame.loc[frame.brand.eq("Fresh")].copy()
    fresh["chilled_share"] = np.divide(
        fresh.chilled_volume_m3.to_numpy(dtype=float), fresh.total_volume_m3.to_numpy(dtype=float),
        out=np.full(len(fresh), np.nan), where=fresh.total_volume_m3.to_numpy(dtype=float) != 0,
    )
    rows = []
    for depot, group in fresh.groupby("depot", sort=True):
        shares = group.chilled_share.dropna()
        rows.append({"depot": depot, "n_weeks": int(len(group)), "mean_chilled_volume_m3": float(group.chilled_volume_m3.mean()),
                     "median_chilled_volume_m3": float(group.chilled_volume_m3.median()), "p90_chilled_volume_m3": float(group.chilled_volume_m3.quantile(.9)),
                     "max_chilled_volume_m3": float(group.chilled_volume_m3.max()), "n_defined_chilled_share": int(len(shares)),
                     "mean_chilled_share": float(shares.mean()) if len(shares) else None,
                     "median_chilled_share": float(shares.median()) if len(shares) else None})
    return pd.DataFrame(rows), fresh


def analyze_recent_trend(panel: pd.DataFrame, windows: list[int] | tuple[int, ...] = (4, 8, 13), minimum_history_weeks: int = 8) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    rows = []
    for keys, group in frame.groupby(SERIES_KEYS, sort=True):
        group = group.sort_values("week_start_date", kind="stable")
        values = group.total_volume_m3.astype(float).to_numpy()
        for window in windows:
            if int(window) < 1:
                raise EDAValidationError("Trend windows must be positive integers.")
            recent = values[-int(window):]
            rolling_ready = len(values) >= max(int(window), int(minimum_history_weeks))
            prior = values[-2 * int(window):-int(window)] if rolling_ready and len(values) >= 2 * int(window) else np.array([])
            comparison_ready = rolling_ready and len(prior) == int(window)
            status = "SUFFICIENT" if comparison_ready else "INSUFFICIENT_PRIOR_HISTORY" if rolling_ready else "INSUFFICIENT_HISTORY"
            row = dict(zip(SERIES_KEYS, keys)) | {"window_weeks": int(window), "n_weeks": int(len(values)),
                "status": status,
                "rolling_status": "SUFFICIENT" if rolling_ready else "INSUFFICIENT_HISTORY",
                "comparison_status": "SUFFICIENT" if comparison_ready else status,
                "latest_rolling_mean": float(np.mean(recent)) if len(values) >= int(window) else None,
                "latest_rolling_median": float(np.median(recent)) if len(values) >= int(window) else None,
                "recent_mean": float(np.mean(recent)) if rolling_ready else None,
                "prior_equal_length_mean": float(np.mean(prior)) if len(prior) == int(window) else None,
                "absolute_change": None, "percent_change": None, "descriptive_slope": None}
            if rolling_ready:
                if len(prior) == int(window):
                    row["absolute_change"] = float(np.mean(recent) - np.mean(prior))
                    if not np.isclose(np.mean(prior), 0.0):
                        row["percent_change"] = float((np.mean(recent) - np.mean(prior)) / abs(np.mean(prior)) * 100)
                row["descriptive_slope"] = float(np.polyfit(np.arange(len(recent)), recent, 1)[0]) if len(recent) > 1 else 0.0
            rows.append(row)
    return pd.DataFrame(rows)


def analyze_yearly_seasonality(panel: pd.DataFrame, minimum_years: int = 2) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    grouped = frame.groupby(SERIES_KEYS + ["iso_week"], sort=True)
    rows = []
    for keys, group in grouped:
        values = group.total_volume_m3.astype(float)
        years = group.iso_year.nunique()
        rows.append(dict(zip(SERIES_KEYS + ["iso_week"], keys)) | {"n_years": int(years), "mean_volume": float(values.mean()),
                     "median_volume": float(values.median()), "std_volume": float(values.std(ddof=1)) if len(values) > 1 else None,
                     "min_volume": float(values.min()), "max_volume": float(values.max()),
                     "seasonality_support": "SUPPORTED" if years >= minimum_years else "INSUFFICIENT"})
    return pd.DataFrame(rows)


def _context_comparison(frame: pd.DataFrame, context: str, value: str = "total_volume_m3") -> pd.DataFrame:
    rows = []
    for keys, group in frame.groupby(SERIES_KEYS + [context], dropna=False, sort=True):
        row = dict(zip(SERIES_KEYS + [context], keys))
        row["n_weeks"] = int(len(group))
        for metric, fn in (("mean_volume", "mean"), ("median_volume", "median"), ("p90_volume", "p90")):
            row[metric] = float(group[value].mean() if fn == "mean" else group[value].median() if fn == "median" else group[value].quantile(.9))
        rows.append(row)
    return pd.DataFrame(rows)


def _attach_context(panel: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    if context.duplicated(WEEK_KEYS).any():
        raise EDAValidationError("weekly calendar context contains duplicate ISO keys.")
    # Phase 11 panels may already carry operating_days. Phase 12 must use the
    # aggregate built here from official daily calendar.is_operating values.
    frame = frame.drop(columns=["operating_days"], errors="ignore")
    return frame.merge(context, on=WEEK_KEYS, how="left", validate="many_to_one")


def analyze_festival_context(panel: pd.DataFrame, context: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _attach_context(panel, context)
    if frame.has_festival.isna().any():
        raise EDAValidationError("calendar context is missing a panel week.")
    compare = _context_comparison(frame, "has_festival")
    by_name = frame.loc[frame.has_festival.eq(1)].copy()
    by_name["festival_name"] = by_name.festival_names.str.split("|")
    by_name = by_name.explode("festival_name").loc[lambda x: x.festival_name.ne("")]
    by_name = by_name.drop_duplicates(PANEL_KEYS + ["festival_name"])
    name_rows = []
    for keys, group in by_name.groupby(SERIES_KEYS + ["festival_name"], sort=True):
        vals = group.total_volume_m3
        name_rows.append(dict(zip(SERIES_KEYS + ["festival_name"], keys)) | {"n_weeks": int(len(group)), "mean_volume": float(vals.mean()), "median_volume": float(vals.median()),
                            "support_warning": "LOW_SUPPORT" if len(group) < 2 else "DESCRIPTIVE_ONLY"})
    return compare, pd.DataFrame(name_rows)


def analyze_festival_ramp(panel: pd.DataFrame, context: pd.DataFrame, bins: list[float] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _attach_context(panel, context)
    edges = bins or [0.0, .25, .5, .75, 1.000001]
    if len(edges) < 2 or edges[0] != 0 or edges[-1] <= 1 or any(b <= a for a, b in zip(edges, edges[1:])):
        raise EDAValidationError("Festival-ramp bins must increase from 0 through a value above 1.")
    frame["ramp_bin"] = pd.cut(frame.max_festival_ramp, bins=edges, right=False, include_lowest=True)
    summary = _context_comparison(frame, "ramp_bin")
    return frame[SERIES_KEYS + WEEK_KEYS + ["max_festival_ramp", "mean_festival_ramp", "ramp_bin"]], summary


def analyze_payday_context(panel: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    return _context_comparison(_attach_context(panel, context), "has_payday")


def analyze_holiday_context(panel: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    return _context_comparison(_attach_context(panel, context), "has_holiday")


def analyze_monsoon_context(panel: pd.DataFrame, context: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _attach_context(panel, context)
    compare = _context_comparison(frame, "has_monsoon_day")
    fraction = _context_comparison(frame, "monsoon_day_fraction")
    return compare, fraction


def analyze_operating_days(panel: pd.DataFrame, context: pd.DataFrame) -> pd.DataFrame:
    frame = _attach_context(panel, context)
    frame["volume_per_operating_day"] = np.divide(frame.total_volume_m3, frame.operating_days,
        out=np.full(len(frame), np.nan), where=frame.operating_days.to_numpy() > 0)
    return _context_comparison(frame, "operating_days")


def compare_same_week_across_years(panel: pd.DataFrame) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    rows = []
    for keys, group in frame.groupby(SERIES_KEYS + ["iso_week"], sort=True):
        group = group.sort_values("iso_year", kind="stable")
        values = group.total_volume_m3.astype(float).to_numpy()
        years = group.iso_year.astype(int).to_numpy()
        yoy = []
        for i in range(1, len(values)):
            absolute = float(values[i] - values[i - 1])
            pct = float(absolute / abs(values[i - 1]) * 100) if not np.isclose(values[i - 1], 0) else None
            yoy.append({"from_year": int(years[i - 1]), "to_year": int(years[i]), "absolute_change": absolute, "percent_change": pct})
        rows.append(dict(zip(SERIES_KEYS + ["iso_week"], keys)) | {"n_years": int(len(values)), "first_year": int(years[0]), "last_year": int(years[-1]),
                    "years": years.tolist(), "volumes_by_year": values.tolist(),
                    "year_over_year_changes": json.dumps(yoy, sort_keys=True), "years_json": json.dumps(years.tolist()),
                    "volumes_by_year_json": json.dumps(values.tolist()), "median_same_week_volume": float(np.median(values)),
                    "same_week_variability": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                    "status": "AVAILABLE" if len(values) >= 2 else "SAME_WEEK_COMPARISON_UNAVAILABLE"})
    return pd.DataFrame(rows)


def detect_weekly_spikes(panel: pd.DataFrame, context: pd.DataFrame | None = None, window: int = 13,
                         minimum_history: int = 8, threshold: float = 3.5, iqr_multiplier: float = 1.5) -> pd.DataFrame:
    frame = validate_task2a_eda_input(panel)
    original_targets = frame["total_volume_m3"].copy(deep=True)
    if window < 1 or minimum_history < 1 or threshold <= 0:
        raise EDAValidationError("Spike detector window, minimum history, and threshold must be positive.")
    rows = []
    for keys, group in frame.groupby(SERIES_KEYS, sort=True):
        group = group.sort_values("week_start_date", kind="stable").reset_index(drop=True)
        values = group.total_volume_m3.astype(float).to_numpy()
        q1, q3 = np.quantile(values, [.25, .75])
        iqr = q3 - q1
        for i, row in group.iterrows():
            prior = values[max(0, i - window):i]
            median = float(np.median(prior)) if len(prior) else None
            mad = float(np.median(np.abs(prior - median))) if len(prior) else None
            robust_z = None
            score_status = "INSUFFICIENT_HISTORY"
            flag = False
            direction = "NONE"
            if len(prior) >= minimum_history:
                score_status = "AVAILABLE"
                delta = float(values[i] - median)
                if np.isclose(mad, 0.0):
                    score_status = "MAD_ZERO_EQUAL" if np.isclose(delta, 0.0) else "MAD_ZERO_DIFFERENT"
                    robust_z = 0.0 if np.isclose(delta, 0.0) else None
                    flag = not np.isclose(delta, 0.0)
                else:
                    robust_z = float(.6745 * delta / mad)
                    flag = abs(robust_z) >= threshold
                direction = "UP" if flag and delta > 0 else "DOWN" if flag else "NONE"
            out = {**dict(zip(SERIES_KEYS, keys)), "iso_year": int(row.iso_year), "iso_week": int(row.iso_week),
                   "week_start_date": str(row.week_start_date.date()), "total_volume_m3": float(values[i]), "spike_direction": direction,
                   "spike_flag": bool(flag), "rolling_history_n": int(len(prior)), "rolling_median": median, "rolling_mad": mad,
                   "robust_z": robust_z, "robust_z_status": score_status,
                   "secondary_iqr_flag": bool(values[i] < q1 - iqr_multiplier * iqr or values[i] > q3 + iqr_multiplier * iqr),
                   "week_status": str(row.week_status)}
            rows.append(out)
    result = pd.DataFrame(rows)
    if context is not None:
        result = result.merge(context[WEEK_KEYS + ["has_festival", "max_festival_ramp", "has_payday", "has_holiday", "monsoon_day_fraction", "operating_days"]],
                              on=WEEK_KEYS, how="left", validate="many_to_one")
    if not original_targets.equals(frame["total_volume_m3"]):
        raise EDAValidationError("Spike detector mutated historical target values.")
    return result


def build_task2a_feature_candidate_table(trends: pd.DataFrame | None = None, seasonality: pd.DataFrame | None = None,
                                        context: pd.DataFrame | None = None, spikes: pd.DataFrame | None = None) -> pd.DataFrame:
    trend_support = int(trends.loc[trends.status.eq("SUFFICIENT"), SERIES_KEYS].drop_duplicates().shape[0]) if trends is not None else 0
    seasonal_support = int(seasonality.loc[seasonality.seasonality_support.eq("SUPPORTED")].shape[0]) if seasonality is not None else 0
    festival_weeks = int(context.has_festival.sum()) if context is not None else 0
    spike_count = int(spikes.spike_flag.sum()) if spikes is not None else 0
    candidates = [
        ("recent_lag_rolling_demand", "historical targets", f"{trend_support} series have at least one supported configured trend window", "No; only after target week is observed", trend_support, "KEEP_CANDIDATE", "Phase 13 must align lags to the forecast origin."),
        ("iso_week", "official calendar", f"{seasonal_support} series/week profiles meet minimum year support", "Yes", seasonal_support, "KEEP_CANDIDATE", "Use official ISO week and preserve week 53."),
        ("festival", "official calendar", "Festival-week association is descriptive only", "Yes where future calendar is supplied", festival_weeks, "KEEP_WITH_CAUTION", "Sparse names and confounding require validation."),
        ("festival_ramp", "official calendar", "Ramp-bin association is descriptive only", "Yes where future calendar is supplied", festival_weeks, "KEEP_WITH_CAUTION", "Use official values and validate out of sample."),
        ("payday", "official calendar", "Payday-week association is descriptive only", "Yes where future calendar is supplied", int(context.has_payday.sum()) if context is not None else 0, "KEEP_WITH_CAUTION", "Use official payday flag only."),
        ("holiday", "official calendar", "Holiday-week association is descriptive only", "Yes where future calendar is supplied", int(context.has_holiday.sum()) if context is not None else 0, "KEEP_WITH_CAUTION", "Keep distinct from festival."),
        ("monsoon", "official calendar", "Mixed-week association is descriptive only", "Yes only if future official value is available", int(context.has_monsoon_day.sum()) if context is not None else 0, "DEFER", "Confirm future availability and stability in Phase 13."),
        ("operating_days", "official calendar", "Demand by operating-day support", "Yes where future calendar is supplied", len(context) if context is not None else 0, "KEEP_CANDIDATE", "Use official is_operating sums."),
        ("spike_indicator", "historical targets", f"{spike_count} descriptive rolling-MAD flags; targets retained", "No", int(len(spikes)) if spikes is not None else 0, "DEFER", "Do not make an anomaly indicator from future target values."),
    ]
    return pd.DataFrame([{"candidate": n, "source": s, "historical_signal": sig, "future_known_at_prediction_time": future,
                          "support": support, "stability_warning": reason if rec in {"KEEP_WITH_CAUTION", "DEFER"} else "validate in rolling-origin backtests",
                          "phase13_recommendation": rec, "reason": reason} for n, s, sig, future, support, rec, reason in candidates])


def build_task2a_eda_warnings(panel: pd.DataFrame, trends: pd.DataFrame, seasonality: pd.DataFrame, spikes: pd.DataFrame,
                              context: pd.DataFrame) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if trends.status.ne("SUFFICIENT").any():
        insufficient = trends.status.ne("SUFFICIENT")
        warnings.append({"code": "INSUFFICIENT_TREND_SUPPORT", "count": int(insufficient.sum()),
                         "detail": "Some configured windows lack a supported rolling summary or equal-length prior comparison."})
    if seasonality.seasonality_support.eq("INSUFFICIENT").any():
        warnings.append({"code": "INSUFFICIENT_SEASONAL_SUPPORT", "count": int(seasonality.seasonality_support.eq("INSUFFICIENT").sum()), "detail": "Some ISO weeks occur in fewer than the configured number of years."})
    if spikes.spike_flag.any():
        warnings.append({"code": "DESCRIPTIVE_SPIKES", "count": int(spikes.spike_flag.sum()), "detail": "Flagged targets were retained unchanged."})
    if context.calendar_days.ne(7).any():
        warnings.append({"code": "PARTIAL_CALENDAR_WEEKS", "count": int(context.calendar_days.ne(7).sum()), "detail": "Calendar contains partial ISO weeks."})
    return warnings


def _plot_outputs(panel: pd.DataFrame, fresh: pd.DataFrame, figures: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures.mkdir(parents=True, exist_ok=True)
    for (depot, brand), group in panel.groupby(SERIES_KEYS, sort=True):
        fig, ax = plt.subplots(figsize=(10, 4))
        group = group.sort_values("week_start_date")
        ax.plot(group.week_start_date, group.total_volume_m3, marker=".", linewidth=1)
        ax.set(title=f"Weekly total demand — {depot} / {brand}", xlabel="Week", ylabel="Volume (m³)")
        fig.tight_layout()
        fig.savefig(figures / f"total_{depot}_{brand}.png", dpi=140)
        plt.close(fig)
    for depot, group in fresh.groupby("depot", sort=True):
        group = group.sort_values("week_start_date")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(group.week_start_date, group.total_volume_m3, label="Total", linewidth=1)
        ax.plot(group.week_start_date, group.chilled_volume_m3, label="Chilled", linewidth=1)
        ax.set(title=f"Fresh total and chilled demand — {depot}", xlabel="Week", ylabel="Volume (m³)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(figures / f"fresh_chilled_{depot}.png", dpi=140)
        plt.close(fig)


def run_task2a_eda(panel: pd.DataFrame, calendar: pd.DataFrame, config: dict[str, Any], output_dir: str | Path,
                   *, make_plots: bool = True) -> dict[str, Any]:
    """Run all Phase 12 descriptive analyses and write private aggregate artifacts."""
    frame = validate_task2a_eda_input(panel)
    context = build_weekly_calendar_context(calendar, frame)
    total = summarize_weekly_total_demand(frame)
    chilled, fresh = summarize_fresh_chilled_demand(frame)
    trend_cfg = config.get("trend", {})
    trends = analyze_recent_trend(frame, trend_cfg.get("windows_weeks", [4, 8, 13]), trend_cfg.get("minimum_history_weeks", 8))
    seasonal = analyze_yearly_seasonality(frame, config.get("seasonality", {}).get("week_of_year_min_support_years", 2))
    festival, festival_names = analyze_festival_context(frame, context)
    ramp_weekly, ramp_bins = analyze_festival_ramp(frame, context, config.get("festival_ramp", {}).get("bins"))
    payday = analyze_payday_context(frame, context)
    holidays = analyze_holiday_context(frame, context)
    monsoon, monsoon_fraction = analyze_monsoon_context(frame, context)
    operating = analyze_operating_days(frame, context)
    same_week = compare_same_week_across_years(frame)
    spike_cfg = config.get("spikes", {})
    spikes = detect_weekly_spikes(frame, context, int(spike_cfg.get("trailing_window_weeks", 13)),
                                  int(spike_cfg.get("minimum_history_weeks", 8)), float(spike_cfg.get("robust_z_threshold", 3.5)),
                                  float(spike_cfg.get("iqr_multiplier", 1.5)))
    candidates = build_task2a_feature_candidate_table(trends, seasonal, context, spikes)
    warnings = build_task2a_eda_warnings(frame, trends, seasonal, spikes, context)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    table_outputs = {
        "total_demand_summary.csv": total, "chilled_demand_summary.csv": chilled, "trend_analysis.csv": trends,
        "seasonality_analysis.csv": seasonal, "festival_analysis.csv": festival, "festival_name_analysis.csv": festival_names,
        "festival_ramp_weekly.csv": ramp_weekly, "festival_ramp_analysis.csv": ramp_bins, "payday_analysis.csv": payday,
        "holiday_analysis.csv": holidays, "monsoon_analysis.csv": monsoon, "monsoon_fraction_analysis.csv": monsoon_fraction,
        "operating_days_analysis.csv": operating, "same_week_across_years.csv": same_week, "spike_analysis.csv": spikes,
    }
    for filename, table in table_outputs.items():
        table.to_csv(destination / filename, index=False)
    context.to_json(destination / "weekly_calendar_context.json", orient="records", indent=2)
    candidates.to_json(destination / "feature_candidates.json", orient="records", indent=2)
    (destination / "warnings.json").write_text(json.dumps(warnings, indent=2, sort_keys=True), encoding="utf-8")
    summary = {"status": "PASS", "panel_rows": int(len(frame)), "series_count": int(frame[SERIES_KEYS].drop_duplicates().shape[0]),
               "calendar_week_count": int(len(context)), "analysis_tables": sorted(table_outputs),
               "figure_count": 0, "warnings_count": len(warnings), "private_data_rows_printed": False}
    if make_plots:
        _plot_outputs(frame, fresh, destination / "figures")
        summary["figure_count"] = len(list((destination / "figures").glob("*.png")))
    (destination / "eda_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    report = ["# Phase 12 Task 2A EDA", "", "All analyses are descriptive associations over the canonical Phase 11 weekly panel.",
              "Targets were preserved; anomaly flags do not remove or alter weeks.", "", f"Series analyzed: {summary['series_count']}",
              f"Panel rows: {summary['panel_rows']}", f"Calendar weeks: {summary['calendar_week_count']}", f"Warnings: {len(warnings)}", "",
              "See the aggregate CSV tables and figures in this private output directory."]
    (destination / "phase12_eda_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"summary": summary, "warnings": warnings, "total_summary": total, "chilled_summary": chilled,
            "trend": trends, "seasonality": seasonal, "calendar_context": context, "spikes": spikes, "feature_candidates": candidates}
