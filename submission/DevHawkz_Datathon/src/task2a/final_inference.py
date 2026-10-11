"""Phase 17 direct Task 2A final inference using only frozen Phase 16 choices."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.task2a.calendar_features import build_target_week_calendar_features, validate_target_calendar_coverage
from src.task2a.eda import validate_task2a_eda_input
from src.task2a.features import build_origin_demand_features, get_task2a_feature_columns
from src.task2a.final_fit import FinalFitError, fit_frozen_component, predict_frozen_component
from src.task2a.model_preprocessing import feature_profile
from src.task2a.model_selection import validate_final_model_config


OFFICIAL_ROW_ORDER = "__official_row_order"
VALID_BRANDS = {"Fresh", "Style", "Tech"}


class FinalInferenceError(ValueError):
    """A Phase 17 final-inference invariant was violated."""


def validate_inference_config(config: dict[str, Any], final_config: dict[str, Any]) -> None:
    expected_horizons = list(range(1, 11))
    if not isinstance(config, dict) or config.get("version") != 1 or config.get("required_frozen_state") != "FROZEN":
        raise FinalInferenceError("Phase 17 inference configuration is invalid.")
    if config.get("forecast_origin") != "latest_complete_historical_week" or config.get("require_global_origin") is not True:
        raise FinalInferenceError("Phase 17 must use one latest complete global historical origin.")
    if config.get("expected_horizons") != expected_horizons or config.get("future_calendar_coverage_required") is not True:
        raise FinalInferenceError("Phase 17 must require official horizons 1..10 and calendar coverage.")
    if config.get("postprocessing") != final_config.get("phase17_postprocessing"):
        raise FinalInferenceError("Phase 17 inference config conflicts with frozen postprocessing.")
    if config.get("structural_output_rules") != final_config.get("structural_output_rules"):
        raise FinalInferenceError("Phase 17 inference config conflicts with frozen structural-zero rules.")
    if config.get("submission") != {"key": "row_id", "preserve_template_order": True, "atomic_write": True}:
        raise FinalInferenceError("Phase 17 submission mapping must preserve official row_id and template order.")


def load_task2a_test_inputs(frame: pd.DataFrame) -> pd.DataFrame:
    if OFFICIAL_ROW_ORDER in frame.columns:
        raise FinalInferenceError("Official Task 2A test input uses the reserved row-order marker.")
    required = {"row_id", "depot", "brand", "iso_year", "iso_week"}
    missing = required.difference(frame.columns)
    if missing:
        raise FinalInferenceError("Task 2A test input is missing: " + ", ".join(sorted(missing)))
    result = frame.copy()
    result.insert(0, OFFICIAL_ROW_ORDER, np.arange(len(result), dtype=int))
    if result.empty:
        raise FinalInferenceError("Task 2A test input must contain at least one row.")
    row_id = result.row_id.astype("string").str.strip()
    if row_id.isna().any() or row_id.eq("").any() or row_id.duplicated().any():
        raise FinalInferenceError("Task 2A row_id must be nonblank and unique.")
    if result.depot.isna().any() or result.depot.astype("string").str.strip().eq("").any():
        raise FinalInferenceError("Task 2A depot must be nonblank.")
    if result.brand.isna().any() or not result.brand.isin(VALID_BRANDS).all():
        raise FinalInferenceError("Task 2A brand must be Fresh, Style, or Tech.")
    result["iso_year"] = pd.to_numeric(result.iso_year, errors="raise").astype(int)
    result["iso_week"] = pd.to_numeric(result.iso_week, errors="raise").astype(int)
    if not result.iso_week.between(1, 53).all():
        raise FinalInferenceError("Task 2A ISO week is outside 1..53.")
    return result


def final_forecast_origin(panel: pd.DataFrame, requested_series: pd.DataFrame) -> pd.Timestamp:
    history = validate_task2a_eda_input(panel)
    latest = history.week_start_date.max().normalize()
    if "week_status" not in history or not history.loc[history.week_start_date.eq(latest), "week_status"].isin(
        ["OBSERVED_DEMAND", "CONFIRMED_ZERO"]
    ).all():
        raise FinalInferenceError("Latest historical week is not a complete approved demand week.")
    required = requested_series[["depot", "brand"]].drop_duplicates()
    available = history.loc[history.week_start_date.eq(latest), ["depot", "brand"]]
    check = required.merge(available, on=["depot", "brand"], how="left", indicator=True)
    if not check._merge.eq("both").all():
        raise FinalInferenceError("A requested Task 2A series lacks the canonical final origin week.")
    return latest


def build_final_test_features(panel: pd.DataFrame, calendar: pd.DataFrame, test_inputs: pd.DataFrame,
                              feature_config: dict[str, Any]) -> tuple[pd.DataFrame, pd.Timestamp]:
    grid = load_task2a_test_inputs(test_inputs)
    origin = final_forecast_origin(panel, grid)
    history = validate_task2a_eda_input(panel)
    origins = build_origin_demand_features(history.loc[history.week_start_date.le(origin)], feature_config)
    origins = origins.loc[origins.week_start_date.eq(origin)].copy()
    calendar_features = validate_target_calendar_coverage(build_target_week_calendar_features(calendar))
    dates = pd.to_datetime(calendar["date"], errors="raise")
    calendar_weeks = pd.DataFrame({"iso_year": pd.to_numeric(calendar["iso_year"], errors="raise"),
                                   "iso_week": pd.to_numeric(calendar["iso_week"], errors="raise"), "date": dates})
    starts = calendar_weeks.groupby(["iso_year", "iso_week"], as_index=False).date.min().rename(columns={"date": "target_week_start_date"})
    future = grid.merge(starts, on=["iso_year", "iso_week"], how="left", validate="many_to_one")
    future = future.merge(calendar_features, on=["iso_year", "iso_week"], how="left", validate="many_to_one")
    if future.target_week_start_date.isna().any() or future.target_calendar_days.isna().any() or not future.target_calendar_days.eq(7).all():
        raise FinalInferenceError("Official future calendar coverage is incomplete.")
    future["target_week_start_date"] = pd.to_datetime(future.target_week_start_date).dt.normalize()
    future["horizon_weeks"] = ((future.target_week_start_date - origin).dt.days // 7).astype(int)
    if not future.target_week_start_date.gt(origin).all() or not future.horizon_weeks.between(1, 10).all():
        raise FinalInferenceError("Official target weeks must map from final origin to horizons 1..10.")
    expected_horizons = set(range(1, 11))
    coverage = future.groupby(["depot", "brand"], sort=False).horizon_weeks.agg(set)
    if not coverage.map(lambda values: values == expected_horizons).all() or future.duplicated(["depot", "brand", "horizon_weeks"]).any():
        raise FinalInferenceError("Each official depot/brand series must cover every horizon 1..10 exactly once.")
    future = future.rename(columns={"iso_year": "target_iso_year", "iso_week": "target_iso_week"})
    origins = origins.rename(columns={"week_start_date": "origin_week_start_date", "iso_year": "origin_iso_year",
        "iso_week": "origin_iso_week", "week_status": "origin_panel_status",
        "demand_feature_max_source_week": "origin_demand_feature_max_source_week"})
    feature_rows = future.merge(origins, on=["depot", "brand"], how="left", validate="many_to_one")
    if len(feature_rows) != len(grid) or feature_rows.origin_week_start_date.isna().any():
        raise FinalInferenceError("Official test grid includes a series unavailable at final origin.")
    profile_columns = get_task2a_feature_columns(feature_config)
    missing = [column for column in profile_columns if column not in feature_rows]
    if missing:
        raise FinalInferenceError("Final feature frame lacks the frozen Phase 13 predictor profile.")
    if not feature_rows.origin_demand_feature_max_source_week.le(origin).all():
        raise FinalInferenceError("Final demand-derived feature source exceeds final forecast origin.")
    return feature_rows.sort_values(OFFICIAL_ROW_ORDER, kind="stable").reset_index(drop=True), origin


def postprocess_predictions(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    result = frame.copy()
    required = {"raw_pred_total_volume_m3", "raw_pred_chilled_volume_m3", "brand"}
    if required.difference(result.columns):
        raise FinalInferenceError("Raw final predictions are incomplete.")
    raw = result[["raw_pred_total_volume_m3", "raw_pred_chilled_volume_m3"]].to_numpy(dtype=float)
    if not np.isfinite(raw).all():
        raise FinalInferenceError("Raw final predictions contain NaN/Inf before postprocessing.")
    result.loc[result.brand.isin(["Style", "Tech"]), "raw_pred_chilled_volume_m3"] = 0.0
    total_raw = result.raw_pred_total_volume_m3.to_numpy(dtype=float)
    chilled_raw = result.raw_pred_chilled_volume_m3.to_numpy(dtype=float)
    total = np.maximum(total_raw, 0.0)
    chilled = np.maximum(chilled_raw, 0.0)
    capped = chilled > total
    result["pred_total_volume_m3"] = total
    result["pred_chilled_volume_m3"] = np.minimum(chilled, total)
    if not result.loc[result.brand.isin(["Style", "Tech"]), "pred_chilled_volume_m3"].eq(0.0).all():
        raise FinalInferenceError("Structural chilled zero was not preserved through postprocessing.")
    return result, {"negative_total_clipped_count": int((total_raw < 0).sum()),
                    "negative_chilled_clipped_count": int((chilled_raw < 0).sum()),
                    "chilled_capped_to_total_count": int(capped.sum())}


def run_final_inference(panel: pd.DataFrame, training_table: pd.DataFrame, calendar: pd.DataFrame,
                        test_inputs: pd.DataFrame, final_config: dict[str, Any],
                        feature_config: dict[str, Any]) -> dict[str, Any]:
    validate_final_model_config(final_config)
    features, origin = build_final_test_features(panel, calendar, test_inputs, feature_config)
    profile = feature_profile(feature_config)
    if final_config["feature_profile"]["registry_hash"] != profile["registry_hash"]:
        raise FinalInferenceError("Frozen final configuration has a different feature registry.")
    total = fit_frozen_component(final_config["total"], "total", training_table, origin, profile)
    chilled = fit_frozen_component(final_config["chilled_fresh"], "chilled", training_table, origin, profile)
    total_raw = predict_frozen_component(total, features, panel, origin, profile)
    chilled_raw = np.zeros(len(features), dtype=float)
    fresh = features.brand.eq("Fresh")
    chilled_raw[fresh.to_numpy()] = predict_frozen_component(chilled, features.loc[fresh].reset_index(drop=True), panel, origin, profile)
    raw = features[[OFFICIAL_ROW_ORDER, "row_id", "brand"]].copy()
    raw["raw_pred_total_volume_m3"] = total_raw
    raw["raw_pred_chilled_volume_m3"] = chilled_raw
    final, corrections = postprocess_predictions(raw)
    return {"predictions": final, "features": features, "final_origin": origin,
            "corrections": corrections, "model_search_performed": False,
            "future_actual_demand_used": False}
