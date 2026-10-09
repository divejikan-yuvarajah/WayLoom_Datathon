"""Task 1 exploratory data analysis utilities (Phase 05).

All analyses in this module are descriptive and leakage-safe.
They reuse the canonical Phase 04 targets (service_minutes, late_flag)
and prohibit prediction-time leakage of actual journey outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import yaml

from src.task1.labels import combine_local_date_clock, parse_clock

# Forbidden as prediction-time explanatory features
TASK1_FORBIDDEN_PREDICTOR_FEATURES = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
}

# Target-derived fields that must never be predictors of themselves
TASK1_TARGET_DERIVED_FIELDS = {
    "service_start_dt",
    "service_minutes",
    "late_flag",
}


class Task1EdaBlockerError(ValueError):
    """Raised when an EDA input or analysis violates integrity or leakage rules."""


def load_task1_eda_config(config_path: Path | str) -> dict[str, Any]:
    """Load and validate Phase 05 YAML configuration."""
    with Path(config_path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def assert_no_eda_feature_leakage(feature_columns: list[str]) -> None:
    """Guard against direct prediction-time feature leakage in EDA inputs."""
    violating = sorted(set(feature_columns) & TASK1_FORBIDDEN_PREDICTOR_FEATURES)
    if violating:
        raise Task1EdaBlockerError(
            "Task 1 forbidden actual journey fields used as explanatory inputs: "
            + ", ".join(violating)
        )


def compute_wilson_score_interval(
    count: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Compute Wilson score interval for binomial proportions."""
    if total <= 0:
        return 0.0, 0.0
    z = 1.959963984540054 if abs(confidence - 0.95) < 1e-4 else stats.norm.ppf(1 - (1 - confidence) / 2)
    p = count / total
    denom = 1 + (z**2) / total
    center = (p + (z**2) / (2 * total)) / denom
    margin = (z * math.sqrt((p * (1 - p) + (z**2) / (4 * total)) / total)) / denom
    low = max(0.0, float(center - margin))
    high = min(1.0, float(center + margin))
    if count == total and total > 0:
        high = 1.0
    if count == 0 and total > 0:
        low = 0.0
    return low, high


def validate_eda_input(df: pd.DataFrame) -> None:
    """Validate input DataFrame conforms to Phase 04 canonical targets and invariants."""
    required = {"delivery_id", "service_minutes", "late_flag"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1EdaBlockerError(f"Missing required EDA columns: {missing}")

    if df["delivery_id"].duplicated().any():
        raise Task1EdaBlockerError("delivery_id must be unique in Task 1 EDA dataset.")

    service = pd.to_numeric(df["service_minutes"], errors="coerce")
    if service.isna().any():
        raise Task1EdaBlockerError("service_minutes contains missing or non-numeric values.")
    if not np.isfinite(service.to_numpy(dtype=float)).all():
        raise Task1EdaBlockerError("service_minutes contains non-finite values.")
    if (service < 0).any():
        raise Task1EdaBlockerError("service_minutes cannot be negative.")

    late = pd.to_numeric(df["late_flag"], errors="coerce")
    if late.isna().any():
        raise Task1EdaBlockerError("late_flag contains missing or non-numeric values.")
    unique_late = set(late.dropna().unique())
    if not unique_late.issubset({0, 1}):
        raise Task1EdaBlockerError("late_flag must be strictly binary (0 or 1).")


# DT-072: Service time distribution
def summarize_service_distribution(df: pd.DataFrame) -> dict[str, Any]:
    """DT-072: Robust center, spread, and tail summary of canonical service_minutes."""
    validate_eda_input(df)
    service = pd.to_numeric(df["service_minutes"], errors="raise").to_numpy(dtype=float)
    n = int(len(service))
    if n == 0:
        raise Task1EdaBlockerError("Input data for service distribution summary is empty.")

    p25 = float(np.percentile(service, 25))
    p75 = float(np.percentile(service, 75))
    return {
        "n": n,
        "missing": 0,
        "mean": float(np.mean(service)),
        "std": float(np.std(service, ddof=1)) if n > 1 else 0.0,
        "min": float(np.min(service)),
        "p25": p25,
        "median": float(np.median(service)),
        "p75": p75,
        "p90": float(np.percentile(service, 90)),
        "p95": float(np.percentile(service, 95)),
        "p99": float(np.percentile(service, 99)),
        "max": float(np.max(service)),
        "iqr": float(p75 - p25),
    }


# DT-073 & DT-074: Service time by group
def summarize_service_by_group(
    df: pd.DataFrame,
    group_col: str,
    *,
    min_group_n: int = 20,
) -> list[dict[str, Any]]:
    """Grouped robust service time summary."""
    validate_eda_input(df)
    assert_no_eda_feature_leakage([group_col])
    if group_col not in df.columns:
        raise Task1EdaBlockerError(f"Group column {group_col} not found in DataFrame.")

    results: list[dict[str, Any]] = []
    for val, grp in df.groupby(group_col, dropna=False):
        n = int(len(grp))
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        mean_val = float(np.mean(service)) if n > 0 else 0.0
        med_val = float(np.median(service)) if n > 0 else 0.0
        p75_val = float(np.percentile(service, 75)) if n > 0 else 0.0
        p90_val = float(np.percentile(service, 90)) if n > 0 else 0.0
        p95_val = float(np.percentile(service, 95)) if n > 0 else 0.0
        results.append(
            {
                group_col: str(val) if not pd.isna(val) else "MISSING",
                "n": n,
                "mean": mean_val,
                "median": med_val,
                "p75": p75_val,
                "p90": p90_val,
                "p95": p95_val,
                "small_sample_warning": bool(n < min_group_n),
            }
        )
    return results


# DT-075: Service time by outlet
def summarize_service_by_outlet(
    df: pd.DataFrame,
    *,
    outlet_col: str = "outlet_id",
    min_group_n: int = 20,
) -> dict[str, Any]:
    """DT-075: Outlet-level service variation without creating target encodings."""
    validate_eda_input(df)
    assert_no_eda_feature_leakage([outlet_col])
    if outlet_col not in df.columns:
        raise Task1EdaBlockerError(f"Outlet column {outlet_col} not found in DataFrame.")

    outlet_summaries: list[dict[str, Any]] = []
    sample_sizes: list[int] = []
    small_sample_count = 0

    for outlet_id, grp in df.groupby(outlet_col, dropna=False):
        n = int(len(grp))
        sample_sizes.append(n)
        is_small = n < min_group_n
        if is_small:
            small_sample_count += 1
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        outlet_summaries.append(
            {
                "outlet_id": str(outlet_id) if not pd.isna(outlet_id) else "MISSING",
                "n": n,
                "mean_service": float(np.mean(service)),
                "median_service": float(np.median(service)),
                "p90_service": float(np.percentile(service, 90)),
                "small_sample_warning": is_small,
            }
        )

    sizes_arr = np.array(sample_sizes, dtype=float) if sample_sizes else np.array([0.0])
    return {
        "unique_outlets": len(outlet_summaries),
        "small_sample_outlets": small_sample_count,
        "sample_size_distribution": {
            "min": int(np.min(sizes_arr)),
            "median": float(np.median(sizes_arr)),
            "mean": float(np.mean(sizes_arr)),
            "max": int(np.max(sizes_arr)),
        },
        "target_encoding_created": False,
        "outlet_summaries": outlet_summaries,
    }


# DT-076, DT-077, DT-078: Continuous order attributes vs service_minutes
def summarize_continuous_vs_service(
    df: pd.DataFrame,
    feature_col: str,
    *,
    num_bins: int = 10,
) -> dict[str, Any]:
    """DT-076..078: Continuous predictor vs service_minutes via rank correlation and quantile bins."""
    validate_eda_input(df)
    assert_no_eda_feature_leakage([feature_col])
    if feature_col not in df.columns:
        raise Task1EdaBlockerError(f"Continuous column {feature_col} not found in DataFrame.")

    valid = df[[feature_col, "service_minutes"]].dropna().copy()
    n_valid = int(len(valid))
    if n_valid < 2:
        return {
            "feature": feature_col,
            "valid_pairs": n_valid,
            "spearman_rho": None,
            "spearman_pvalue": None,
            "pearson_r": None,
            "binned_summary": [],
            "constant_feature": True,
        }

    x = pd.to_numeric(valid[feature_col], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(valid["service_minutes"], errors="coerce").to_numpy(dtype=float)
    valid_mask = np.isfinite(x) & np.isfinite(y)
    x = x[valid_mask]
    y = y[valid_mask]
    n_valid = len(x)

    is_constant = bool(np.all(x == x[0])) if n_valid > 0 else True
    if is_constant or n_valid < 2:
        spearman_rho, spearman_p = None, None
        pearson_r = None
    else:
        sp_res = stats.spearmanr(x, y)
        spearman_rho = float(sp_res.correlation) if np.isfinite(sp_res.correlation) else None
        spearman_p = float(sp_res.pvalue) if np.isfinite(sp_res.pvalue) else None
        try:
            pe_res = stats.pearsonr(x, y)
            pearson_r = float(pe_res[0]) if np.isfinite(pe_res[0]) else None
        except Exception:
            pearson_r = None

    # Quantile bins with duplicate edge fallback
    binned_summary: list[dict[str, Any]] = []
    if n_valid > 0 and not is_constant:
        valid_df = pd.DataFrame({feature_col: x, "service_minutes": y})
        # Try qcut, fallback to rank qcut or cut if duplicate edges
        try:
            valid_df["bin"], bin_edges = pd.qcut(valid_df[feature_col], q=num_bins, retbins=True, duplicates="drop")
        except ValueError:
            valid_df["bin"] = pd.cut(valid_df[feature_col], bins=num_bins)

        for bin_label, grp in valid_df.groupby("bin", observed=True):
            n_bin = int(len(grp))
            x_vals = grp[feature_col].to_numpy()
            y_vals = grp["service_minutes"].to_numpy()
            binned_summary.append(
                {
                    "bin": str(bin_label),
                    "n": n_bin,
                    "min": float(np.min(x_vals)),
                    "median": float(np.median(x_vals)),
                    "max": float(np.max(x_vals)),
                    "mean_service": float(np.mean(y_vals)),
                    "median_service": float(np.median(y_vals)),
                    "p90_service": float(np.percentile(y_vals, 90)),
                }
            )

    return {
        "feature": feature_col,
        "valid_pairs": n_valid,
        "spearman_rho": spearman_rho,
        "spearman_pvalue": spearman_p,
        "pearson_r": pearson_r,
        "constant_feature": is_constant,
        "binned_summary": binned_summary,
    }


def compute_order_size_correlations(df: pd.DataFrame) -> dict[str, float | None]:
    """Compute Spearman correlation among units, weight, and volume for multicollinearity check."""
    cols = ["order_units", "order_weight_kg", "order_volume_m3"]
    present = [c for c in cols if c in df.columns]
    results: dict[str, float | None] = {}
    for i in range(len(present)):
        for j in range(i + 1, len(present)):
            c1, c2 = present[i], present[j]
            pair_df = df[[c1, c2]].dropna()
            if len(pair_df) > 1:
                rho = stats.spearmanr(pair_df[c1], pair_df[c2]).correlation
                results[f"{c1}_vs_{c2}"] = float(rho) if np.isfinite(rho) else None
            else:
                results[f"{c1}_vs_{c2}"] = None
    return results


# DT-079: Overall lateness
def summarize_late_rate(df: pd.DataFrame) -> dict[str, Any]:
    """DT-079: Overall late class rate and Wilson confidence interval."""
    validate_eda_input(df)
    late = pd.to_numeric(df["late_flag"], errors="raise").to_numpy(dtype=int)
    n = int(len(late))
    late_count = int(np.sum(late == 1))
    not_late_count = int(np.sum(late == 0))
    rate = float(late_count / n) if n > 0 else 0.0
    w_low, w_high = compute_wilson_score_interval(late_count, n)
    return {
        "n": n,
        "late_count": late_count,
        "not_late_count": not_late_count,
        "late_rate": rate,
        "wilson_ci_95": [w_low, w_high],
    }


# DT-080, DT-081, DT-082: Lateness by group
def summarize_late_rate_by_group(
    df: pd.DataFrame,
    group_col: str,
    *,
    min_group_n: int = 30,
) -> list[dict[str, Any]]:
    """DT-080..082: Grouped lateness rate by brand, district, or depot."""
    validate_eda_input(df)
    assert_no_eda_feature_leakage([group_col])
    if group_col not in df.columns:
        raise Task1EdaBlockerError(f"Group column {group_col} not found in DataFrame.")

    results: list[dict[str, Any]] = []
    for val, grp in df.groupby(group_col, dropna=False):
        n = int(len(grp))
        late_s = pd.to_numeric(grp["late_flag"], errors="raise").to_numpy(dtype=int)
        late_count = int(np.sum(late_s == 1))
        not_late_count = int(np.sum(late_s == 0))
        rate = float(late_count / n) if n > 0 else 0.0
        w_low, w_high = compute_wilson_score_interval(late_count, n)
        results.append(
            {
                group_col: str(val) if not pd.isna(val) else "MISSING",
                "n": n,
                "late_count": late_count,
                "not_late_count": not_late_count,
                "late_rate": rate,
                "wilson_ci_95": [w_low, w_high],
                "small_sample_warning": bool(n < min_group_n),
            }
        )
    return results


# DT-083: Route position
def summarize_route_position(df: pd.DataFrame) -> dict[str, Any]:
    """DT-083: Route sequence position and first stop vs later stops analysis."""
    validate_eda_input(df)
    if "seq_in_route" not in df.columns:
        raise Task1EdaBlockerError("Missing seq_in_route in DataFrame for route position analysis.")

    seq_numeric = pd.to_numeric(df["seq_in_route"], errors="coerce")
    if seq_numeric.isna().any():
        raise Task1EdaBlockerError("seq_in_route contains missing or non-numeric values.")

    df_copy = df.copy()
    df_copy["seq_num"] = seq_numeric
    df_copy["is_first_stop"] = (seq_numeric == 0).astype(int)

    # First stop vs later stop
    first_vs_later: list[dict[str, Any]] = []
    for is_first, grp in df_copy.groupby("is_first_stop"):
        n = int(len(grp))
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        late = pd.to_numeric(grp["late_flag"], errors="raise").to_numpy(dtype=int)
        first_vs_later.append(
            {
                "stop_type": "first_stop (seq=0)" if is_first == 1 else "later_stop (seq>0)",
                "n": n,
                "median_service": float(np.median(service)) if n > 0 else 0.0,
                "late_rate": float(np.mean(late == 1)) if n > 0 else 0.0,
            }
        )

    # Position bins: 0, 1, 2, 3, 4+
    def _bin_pos(val: float) -> str:
        if val == 0:
            return "0"
        elif val == 1:
            return "1"
        elif val == 2:
            return "2"
        elif val == 3:
            return "3"
        else:
            return "4+"

    df_copy["pos_bin"] = df_copy["seq_num"].apply(_bin_pos)
    order = ["0", "1", "2", "3", "4+"]
    position_binned: list[dict[str, Any]] = []
    for p_label in order:
        grp = df_copy[df_copy["pos_bin"] == p_label]
        n = int(len(grp))
        if n == 0:
            continue
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        late = pd.to_numeric(grp["late_flag"], errors="raise").to_numpy(dtype=int)
        position_binned.append(
            {
                "position_bin": p_label,
                "n": n,
                "median_service": float(np.median(service)),
                "late_rate": float(np.mean(late == 1)),
            }
        )

    return {
        "first_vs_later": first_vs_later,
        "position_binned": position_binned,
    }


# DT-084: Planned slack vs lateness
def build_planned_slack_minutes(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    planned_arrival_col: str = "planned_arrival_time",
    window_close_col: str = "window_close_time",
    window_open_col: str = "window_open_time",
) -> pd.Series:
    """DT-084: Compute leakage-safe planned slack = window_close_planned_dt - planned_arrival_dt.

    Uses planned timestamps ONLY. Never accesses actual arrival or actual departure.
    """
    required = {date_col, planned_arrival_col, window_close_col}
    missing = sorted(required - set(df.columns))
    if missing:
        raise Task1EdaBlockerError(f"Missing required planned slack columns: {missing}")

    # Explicit guard: ensure no actual arrival is used
    if "arrival_time" in df.columns and planned_arrival_col == "arrival_time":
        raise Task1EdaBlockerError("planned_slack cannot use actual arrival_time!")

    slack_values: list[float] = []
    for _, row in df.iterrows():
        d_val = row[date_col]
        plan_arr = row[planned_arrival_col]
        win_close = row[window_close_col]

        if pd.isna(plan_arr) or str(plan_arr).strip() == "":
            raise Task1EdaBlockerError(f"planned_arrival_time is missing for delivery {row.get('delivery_id')}")
        if pd.isna(win_close) or str(win_close).strip() == "":
            raise Task1EdaBlockerError(f"window_close_time is missing for delivery {row.get('delivery_id')}")

        plan_arr_dt = combine_local_date_clock(d_val, plan_arr, day_offset=0)
        win_close_dt = combine_local_date_clock(d_val, win_close, day_offset=0)

        # Cross-midnight window handling if window_open is present
        if window_open_col in df.columns and pd.notna(row[window_open_col]):
            win_open = str(row[window_open_col]).strip()
            if win_open:
                o_h, o_m = parse_clock(win_open)
                c_h, c_m = parse_clock(str(win_close).strip())
                if (c_h, c_m) < (o_h, o_m):
                    win_close_dt = win_close_dt + timedelta(days=1)

        slack_min = (win_close_dt - plan_arr_dt).total_seconds() / 60.0
        slack_values.append(slack_min)

    return pd.Series(slack_values, index=df.index, name="planned_slack_min", dtype=float)


def summarize_slack_vs_targets(
    df: pd.DataFrame,
    slack_series: pd.Series,
    *,
    bins: list[float] | None = None,
) -> dict[str, Any]:
    """DT-084: Distribution of planned slack and lateness / service rates by slack bin."""
    validate_eda_input(df)
    if bins is None:
        bins = [-999999.0, -60.0, -30.0, -15.0, 0.0, 15.0, 30.0, 60.0, 999999.0]

    bin_labels = [
        "< -60",
        "[-60,-30)",
        "[-30,-15)",
        "[-15,0)",
        "[0,15)",
        "[15,30)",
        "[30,60)",
        ">=60",
    ]

    working_df = pd.DataFrame(
        {
            "slack": slack_series,
            "late_flag": pd.to_numeric(df["late_flag"], errors="raise"),
            "service_minutes": pd.to_numeric(df["service_minutes"], errors="raise"),
        }
    )

    valid_slack = working_df["slack"].dropna().to_numpy(dtype=float)
    n = len(valid_slack)
    if n == 0:
        return {"n": 0, "slack_distribution": {}, "binned_summary": [], "spearman_slack_vs_late": None}

    slack_dist = {
        "n": n,
        "min": float(np.min(valid_slack)),
        "median": float(np.median(valid_slack)),
        "mean": float(np.mean(valid_slack)),
        "max": float(np.max(valid_slack)),
        "negative_slack_count": int(np.sum(valid_slack < 0)),
        "zero_slack_count": int(np.sum(valid_slack == 0)),
        "positive_slack_count": int(np.sum(valid_slack > 0)),
    }

    working_df["slack_bin"] = pd.cut(
        working_df["slack"],
        bins=bins,
        labels=bin_labels,
        right=False,
    )

    binned_summary: list[dict[str, Any]] = []
    for label in bin_labels:
        grp = working_df[working_df["slack_bin"] == label]
        n_bin = int(len(grp))
        if n_bin == 0:
            binned_summary.append(
                {
                    "slack_bin": label,
                    "n": 0,
                    "late_count": 0,
                    "late_rate": 0.0,
                    "median_service": 0.0,
                }
            )
            continue
        late_arr = grp["late_flag"].to_numpy(dtype=int)
        serv_arr = grp["service_minutes"].to_numpy(dtype=float)
        binned_summary.append(
            {
                "slack_bin": label,
                "n": n_bin,
                "late_count": int(np.sum(late_arr == 1)),
                "late_rate": float(np.mean(late_arr == 1)),
                "median_service": float(np.median(serv_arr)),
            }
        )

    # Spearman between slack and late_flag
    sp_res = stats.spearmanr(working_df["slack"], working_df["late_flag"])
    sp_rho = float(sp_res.correlation) if np.isfinite(sp_res.correlation) else None

    return {
        "n": n,
        "slack_distribution": slack_dist,
        "binned_summary": binned_summary,
        "spearman_slack_vs_late": sp_rho,
    }


# DT-085 & DT-086: Environmental / contextual joins (road & traffic)
def summarize_optional_context(
    df: pd.DataFrame,
    feature_col: str,
    *,
    status: str = "ENABLED",
    bins: int = 5,
) -> dict[str, Any]:
    """DT-085/DT-086: Coverage and relationship for road disruption or traffic speed index.

    Never defaults missing road to clear or missing traffic to free flow.
    """
    validate_eda_input(df)
    if status != "ENABLED" or feature_col not in df.columns:
        return {
            "feature": feature_col,
            "status": "NOT_APPLICABLE / DISABLED",
            "coverage_n": 0,
            "coverage_rate": 0.0,
            "missing_n": int(len(df)),
            "binned_summary": [],
            "spearman_with_service": None,
        }

    total_n = int(len(df))
    valid = df[[feature_col, "service_minutes", "late_flag"]].dropna().copy()
    cov_n = int(len(valid))
    cov_rate = float(cov_n / total_n) if total_n > 0 else 0.0
    missing_n = total_n - cov_n

    if cov_n < 2:
        return {
            "feature": feature_col,
            "status": "PARTIAL_COVERAGE",
            "coverage_n": cov_n,
            "coverage_rate": cov_rate,
            "missing_n": missing_n,
            "binned_summary": [],
            "spearman_with_service": None,
        }

    x = pd.to_numeric(valid[feature_col], errors="coerce").to_numpy(dtype=float)
    y_serv = pd.to_numeric(valid["service_minutes"], errors="coerce").to_numpy(dtype=float)
    y_late = pd.to_numeric(valid["late_flag"], errors="coerce").to_numpy(dtype=int)

    sp_serv = stats.spearmanr(x, y_serv).correlation
    spearman_service = float(sp_serv) if np.isfinite(sp_serv) else None

    binned_summary: list[dict[str, Any]] = []
    if not np.all(x == x[0]):
        valid["bin"] = pd.qcut(valid[feature_col], q=bins, duplicates="drop")
        for b_lbl, grp in valid.groupby("bin", observed=True):
            n_b = int(len(grp))
            binned_summary.append(
                {
                    "bin": str(b_lbl),
                    "n": n_b,
                    "median_service": float(grp["service_minutes"].median()),
                    "late_rate": float((grp["late_flag"] == 1).mean()),
                }
            )

    return {
        "feature": feature_col,
        "status": "ENABLED",
        "coverage_n": cov_n,
        "coverage_rate": cov_rate,
        "missing_n": missing_n,
        "binned_summary": binned_summary,
        "spearman_with_service": spearman_service,
    }


# DT-087: Monsoon context
def summarize_monsoon_context(df: pd.DataFrame, *, monsoon_col: str = "monsoon") -> list[dict[str, Any]]:
    """DT-087: Lateness and service by approved prediction-time monsoon indicator (0/1)."""
    validate_eda_input(df)
    if monsoon_col not in df.columns:
        raise Task1EdaBlockerError(f"Monsoon column {monsoon_col} not found in DataFrame.")

    results: list[dict[str, Any]] = []
    for val, grp in df.groupby(monsoon_col):
        n = int(len(grp))
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        late = pd.to_numeric(grp["late_flag"], errors="raise").to_numpy(dtype=int)
        late_count = int(np.sum(late == 1))
        results.append(
            {
                "monsoon": int(val) if pd.notna(val) else "MISSING",
                "n": n,
                "median_service": float(np.median(service)) if n > 0 else 0.0,
                "p90_service": float(np.percentile(service, 90)) if n > 0 else 0.0,
                "late_count": late_count,
                "late_rate": float(late_count / n) if n > 0 else 0.0,
            }
        )
    return results


# DT-088: Day-of-week context
def summarize_dow_context(df: pd.DataFrame, *, dow_col: str = "dow") -> list[dict[str, Any]]:
    """DT-088: Official calendar day-of-week (0=Monday..6=Sunday) target behavior."""
    validate_eda_input(df)
    if dow_col not in df.columns:
        raise Task1EdaBlockerError(f"Day-of-week column {dow_col} not found in DataFrame.")

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    results: list[dict[str, Any]] = []

    for d in range(7):
        grp = df[df[dow_col] == d]
        n = int(len(grp))
        if n == 0:
            results.append(
                {
                    "dow": d,
                    "day_name": day_names[d],
                    "n": 0,
                    "median_service": 0.0,
                    "p90_service": 0.0,
                    "late_rate": 0.0,
                }
            )
            continue
        service = pd.to_numeric(grp["service_minutes"], errors="raise").to_numpy(dtype=float)
        late = pd.to_numeric(grp["late_flag"], errors="raise").to_numpy(dtype=int)
        results.append(
            {
                "dow": d,
                "day_name": day_names[d],
                "n": n,
                "median_service": float(np.median(service)),
                "p90_service": float(np.percentile(service, 90)),
                "late_rate": float(np.mean(late == 1)),
            }
        )
    return results


# DT-089: Shift / planned time of day
def assign_planned_shift(
    clock_series: pd.Series,
    *,
    shift_bins: list[dict[str, Any]] | None = None,
) -> pd.Series:
    """DT-089: Classify planned clock string (HH:MM) into configurable shift bins.

    Never uses actual arrival time.
    Default bins:
      overnight: 00:00-05:59 (hour in [0, 5])
      morning:   06:00-11:59 (hour in [6, 11])
      afternoon: 12:00-17:59 (hour in [12, 17])
      evening:   18:00-23:59 (hour in [18, 23])
    """
    if shift_bins is None:
        shift_bins = [
            {"name": "overnight", "start_hour": 0, "end_hour": 6},
            {"name": "morning", "start_hour": 6, "end_hour": 12},
            {"name": "afternoon", "start_hour": 12, "end_hour": 18},
            {"name": "evening", "start_hour": 18, "end_hour": 24},
        ]

    shifts: list[str] = []
    for val in clock_series:
        if pd.isna(val) or str(val).strip() == "":
            shifts.append("UNKNOWN")
            continue
        h, m = parse_clock(str(val).strip())
        assigned = "UNKNOWN"
        for sb in shift_bins:
            if sb["start_hour"] <= h < sb["end_hour"]:
                assigned = sb["name"]
                break
        shifts.append(assigned)
    return pd.Series(shifts, index=clock_series.index, name="shift")


def summarize_shift_context(
    df: pd.DataFrame,
    shift_series: pd.Series,
) -> list[dict[str, Any]]:
    """DT-089: Target summaries by planned shift."""
    validate_eda_input(df)
    working_df = pd.DataFrame(
        {
            "shift": shift_series,
            "service_minutes": pd.to_numeric(df["service_minutes"], errors="raise"),
            "late_flag": pd.to_numeric(df["late_flag"], errors="raise"),
        }
    )

    results: list[dict[str, Any]] = []
    for shift_name, grp in working_df.groupby("shift"):
        n = int(len(grp))
        service = grp["service_minutes"].to_numpy(dtype=float)
        late = grp["late_flag"].to_numpy(dtype=int)
        results.append(
            {
                "shift": str(shift_name),
                "n": n,
                "median_service": float(np.median(service)) if n > 0 else 0.0,
                "p90_service": float(np.percentile(service, 90)) if n > 0 else 0.0,
                "late_rate": float(np.mean(late == 1)) if n > 0 else 0.0,
            }
        )
    return results


# DT-090: Feature candidate table and warnings
def build_feature_candidate_table(eda_summary: dict[str, Any]) -> list[dict[str, Any]]:
    """DT-090: Build structured feature-candidate table for Phase 06 transition."""
    candidates = [
        {
            "feature": "brand",
            "prediction_time_safe": True,
            "eda_signal": "Categorical variation across Fresh/Style/Tech service time and lateness",
            "sample_coverage": "Complete",
            "stability_warning": "None; official 3-brand categorical domain",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Known at order entry, well-represented in both train and test",
        },
        {
            "feature": "dock_type",
            "prediction_time_safe": True,
            "eda_signal": "Handling time differences by receiving dock configuration",
            "sample_coverage": "Complete via outlet master reference",
            "stability_warning": "Small mall_bay frequency requires care",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Fixed outlet characteristic known before dispatch",
        },
        {
            "feature": "outlet_id",
            "prediction_time_safe": True,
            "eda_signal": "High cardinality outlet-level handling variation",
            "sample_coverage": "120 unique official outlets",
            "stability_warning": "Small per-outlet sample sizes risk severe overfitting",
            "phase06_recommendation": "KEEP_WITH_CAUTION",
            "reason": "Target encoding without out-of-fold regularization is unsafe",
        },
        {
            "feature": "order_units",
            "prediction_time_safe": True,
            "eda_signal": "Positive rank correlation with service handling duration",
            "sample_coverage": "Complete in order delivery records",
            "stability_warning": "Highly correlated with weight and volume",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Physical shipment quantity directly impacts loading/unloading time",
        },
        {
            "feature": "order_weight_kg",
            "prediction_time_safe": True,
            "eda_signal": "Continuous relationship with service duration",
            "sample_coverage": "Complete",
            "stability_warning": "Multicollinearity with units/volume",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Shipment mass known prior to departure",
        },
        {
            "feature": "order_volume_m3",
            "prediction_time_safe": True,
            "eda_signal": "Continuous relationship with service duration",
            "sample_coverage": "Complete",
            "stability_warning": "Multicollinearity with units/weight",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Cubic volume impacts unloading mechanics",
        },
        {
            "feature": "district",
            "prediction_time_safe": True,
            "eda_signal": "Correlated with route length and regional traffic",
            "sample_coverage": "Complete 12-district domain",
            "stability_warning": "Confounded with depot and brand routing",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Geographic delivery zone known in advance",
        },
        {
            "feature": "depot",
            "prediction_time_safe": True,
            "eda_signal": "Operational base differences (Peliyagoda vs Kandy)",
            "sample_coverage": "Complete",
            "stability_warning": "Two-level categorical; interacts with geographic footprint",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Origin hub fixed for each route",
        },
        {
            "feature": "seq_in_route",
            "prediction_time_safe": True,
            "eda_signal": "Cumulative delivery progression; first-stop vs later stop",
            "sample_coverage": "Complete for dispatched orders",
            "stability_warning": "Sparse observations at high stop indices",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Route sequence is planned prior to vehicle departure",
        },
        {
            "feature": "planned_slack_min",
            "prediction_time_safe": True,
            "eda_signal": "Strong inverse relationship with actual late_flag",
            "sample_coverage": "Complete across planned delivery schedules",
            "stability_warning": "Negative slack cases must be preserved as continuous signals",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Derived entirely from planned arrival and window close; leakage-safe",
        },
        {
            "feature": "monsoon",
            "prediction_time_safe": True,
            "eda_signal": "Weather season effect on transit and handling speeds",
            "sample_coverage": "Complete in calendar table",
            "stability_warning": "Seasonal binary indicator",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Approved calendar reference feature",
        },
        {
            "feature": "dow",
            "prediction_time_safe": True,
            "eda_signal": "Day-of-week demand and traffic seasonality",
            "sample_coverage": "Complete (0=Monday..6=Sunday)",
            "stability_warning": "None; official calendar day-of-week",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Known calendar date",
        },
        {
            "feature": "planned_shift",
            "prediction_time_safe": True,
            "eda_signal": "Time-of-day traffic and receiving congestion variations",
            "sample_coverage": "Complete from planned_arrival_time",
            "stability_warning": "Engineering convention; boundary hours must remain fixed",
            "phase06_recommendation": "KEEP_CANDIDATE",
            "reason": "Constructed strictly from planned arrival time",
        },
        {
            "feature": "road_disruption_index",
            "prediction_time_safe": True,
            "eda_signal": "Potential corridor disruption index",
            "sample_coverage": "Partial coverage across routes",
            "stability_warning": "Missing keys must not be imputed as clear (100)",
            "phase06_recommendation": "DEFER",
            "reason": "Requires rigorous imputation validation before feature inclusion",
        },
        {
            "feature": "traffic_speed_index",
            "prediction_time_safe": True,
            "eda_signal": "Traffic congestion speed index",
            "sample_coverage": "Partial coverage",
            "stability_warning": "Missing values must not default to free-flow (100)",
            "phase06_recommendation": "DEFER",
            "reason": "Requires baseline join stability testing in Phase 06",
        },
        # FORBIDDEN ACTUAL JOURNEY OUTCOMES: STRICTLY DISABLED
        {
            "feature": "actual_depart_time",
            "prediction_time_safe": False,
            "eda_signal": "Actual route departure timestamp",
            "sample_coverage": "Training historical records only",
            "stability_warning": "CRITICAL PREDICTION-TIME LEAKAGE",
            "phase06_recommendation": "DISABLE",
            "reason": "Historical actual outcome unavailable at prediction time",
        },
        {
            "feature": "actual_travel_duration_min",
            "prediction_time_safe": False,
            "eda_signal": "Actual observed travel duration",
            "sample_coverage": "Training historical records only",
            "stability_warning": "CRITICAL PREDICTION-TIME LEAKAGE",
            "phase06_recommendation": "DISABLE",
            "reason": "Historical actual outcome unavailable at prediction time",
        },
        {
            "feature": "arrival_time",
            "prediction_time_safe": False,
            "eda_signal": "Actual arrival timestamp at outlet",
            "sample_coverage": "Training historical records only",
            "stability_warning": "CRITICAL PREDICTION-TIME LEAKAGE",
            "phase06_recommendation": "DISABLE",
            "reason": "Historical actual outcome unavailable at prediction time; directly defines late_flag",
        },
        {
            "feature": "leave_outlet_time",
            "prediction_time_safe": False,
            "eda_signal": "Actual outlet departure timestamp",
            "sample_coverage": "Training historical records only",
            "stability_warning": "CRITICAL PREDICTION-TIME LEAKAGE",
            "phase06_recommendation": "DISABLE",
            "reason": "Historical actual outcome unavailable at prediction time; directly defines service_minutes",
        },
    ]
    return candidates


def build_eda_warnings(eda_summary: dict[str, Any]) -> list[str]:
    """Compile analytical and operational warnings from EDA findings."""
    warnings: list[str] = []
    serv_dist = eda_summary.get("service_distribution", {})
    if serv_dist.get("p99", 0) > 3 * serv_dist.get("median", 1):
        warnings.append(
            f"Heavy service-time upper tail: p99 ({serv_dist.get('p99'):.1f}m) is substantially higher than median ({serv_dist.get('median'):.1f}m). Robust loss (MAE/Huber) recommended."
        )

    late_ov = eda_summary.get("lateness_overall", {})
    lr = late_ov.get("late_rate", 0.0)
    if lr < 0.20 or lr > 0.80:
        warnings.append(
            f"Late class imbalance observed (late_rate = {lr:.1%}). Evaluate PR-AUC and log-loss alongside ROC-AUC."
        )

    outlet_ov = eda_summary.get("service_by_outlet", {})
    if outlet_ov.get("small_sample_outlets", 0) > 0:
        warnings.append(
            f"{outlet_ov.get('small_sample_outlets')} outlets have fewer than 20 observations. Raw target encoding would severely overfit."
        )

    corr = eda_summary.get("order_size_correlations", {})
    for pair, val in corr.items():
        if val is not None and abs(val) > 0.85:
            warnings.append(
                f"High collinearity between order sizing attributes ({pair}: rho={val:.2f}). Tree models handle this naturally, but linear models will suffer."
            )

    road_ctx = eda_summary.get("road_context", {})
    if road_ctx.get("status") != "ENABLED" or road_ctx.get("coverage_rate", 1.0) < 0.90:
        warnings.append("Road disruption context has incomplete coverage. Do not assume missing equals clear.")

    traffic_ctx = eda_summary.get("traffic_context", {})
    if traffic_ctx.get("status") != "ENABLED" or traffic_ctx.get("coverage_rate", 1.0) < 0.90:
        warnings.append("Traffic speed index context has incomplete coverage. Do not assume missing equals free-flow.")

    return warnings
