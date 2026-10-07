"""Build the safe, config-derived Phase 30 preprocessing manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "preprocessing_manifest.yaml"

TASK1_OUTPUT_COLUMNS = ["delivery_id", "pred_service_min", "pred_late_prob"]
TASK2A_OUTPUT_COLUMNS = ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]
TASK2B_OUTPUT_COLUMNS = ["scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id"]
TASK_IDS = [f"DT-{number}" for number in range(379, 389)]
FORBIDDEN_TASK1_PREDICTORS = [
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_minutes",
    "late_flag",
]
OBJECTIVE_LEVELS = [
    ["served_order_count", "maximize"],
    ["served_previous_deferred_count", "maximize"],
    ["served_waiting_days_sum", "maximize"],
    ["served_low_flexibility_count", "maximize"],
    ["served_fresh_chilled_count", "maximize"],
    ["served_fresh_count", "maximize"],
    ["avoidable_reefer_van_assignment_count", "minimize"],
    ["avoidable_reefer_assignment_count", "minimize"],
    ["avoidable_van_assignment_count", "minimize"],
]


class PreprocessingManifestError(ValueError):
    """A frozen preprocessing fact is missing or contradictory."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreprocessingManifestError(f"Invalid safe configuration: {path.name}")
    return value


def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    value = mapping.get(key)
    if value in (None, "", [], {}):
        raise PreprocessingManifestError(f"Missing {context}.{key}")
    return value


def _dataset_inventory(dataset_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = dataset_manifest.get("artifacts") or []
    by_name = {item.get("filename"): item for item in artifacts if isinstance(item, dict)}
    usage = {
        "deliveries_train.csv": ["Task 1 labels/features", "Task 2A demand history"],
        "route_legs_train.csv": ["Task 1 historical labels and planned route context"],
        "task1_test_inputs.csv": ["Task 1 inference", "Task 2A demand history"],
        "route_legs_test.csv": ["Task 1 planned route context"],
        "task2a_test_inputs.csv": ["Task 2A forecast identity and horizon grid"],
        "task2b_peak_day_scenarios.csv": ["Task 2B scenario orders"],
        "task2b_peak_day_fleet.csv": ["Task 2B scenario availability"],
        "outlets.csv": ["Task 1 outlet, dock, access and window context"],
        "vehicles.csv": ["Task 1 vehicle context", "Task 2B capability and capacity"],
        "calendar.csv": ["Task 1 calendar context", "Task 2A ISO weeks and target-week context"],
        "district_travel.csv": ["Task 1 geography context", "Task 2B trip-time lookup"],
        "service_allowance.csv": ["Task 1 allowance context", "Task 2B handling-time lookup"],
        "submission_task1.csv": ["Task 1 official output identity"],
        "submission_task2a.csv": ["Task 2A official output identity"],
        "submission_task2b.csv": ["Task 2B official output identity"],
    }
    result: list[dict[str, Any]] = []
    for filename, tasks in usage.items():
        artifact = by_name.get(filename)
        if artifact is None:
            raise PreprocessingManifestError(f"Dataset manifest is missing {filename}")
        keys = artifact.get("primary_keys") or artifact.get("composite_keys") or artifact.get("composite_route_keys")
        result.append(
            {
                "logical_name": filename.removesuffix(".csv"),
                "filename": filename,
                "category": artifact.get("category"),
                "grain": artifact.get("grain"),
                "key_fields": keys or [],
                "used_by": tasks,
            }
        )
    return result


def build_manifest(config_root: Path = ROOT / "configs") -> dict[str, Any]:
    dataset_manifest = _load_yaml(config_root / "dataset_manifest.yaml")
    task1_features = _load_yaml(config_root / "task1_features.yaml")
    task1_validation = _load_yaml(config_root / "task1_validation.yaml")
    task1_final = _load_yaml(config_root / "task1_final_models.yaml")
    task1_inference = _load_yaml(config_root / "task1_inference.yaml")
    task2a_history = _load_yaml(config_root / "task2a_history.yaml")
    task2a_features = _load_yaml(config_root / "task2a_features.yaml")
    task2a_validation = _load_yaml(config_root / "task2a_validation.yaml")
    task2a_final = _load_yaml(config_root / "task2a_final_models.yaml")
    task2a_inference = _load_yaml(config_root / "task2a_inference.yaml")
    task2b_scenario = _load_yaml(config_root / "task2b_scenario.yaml")
    task2b_trip = _load_yaml(config_root / "task2b_trip_time.yaml")
    task2b_priority = _load_yaml(config_root / "task2b_priority.yaml")
    task2b_optimizer = _load_yaml(config_root / "task2b_optimizer.yaml")
    task2b_validation = _load_yaml(config_root / "task2b_validation.yaml")
    task2b_output = _load_yaml(config_root / "task2b_output.yaml")

    service = _require(task1_final, "service_model", "task1_final_models")
    lateness = _require(task1_final, "lateness_model", "task1_final_models")
    calibration = lateness.get("calibration") or {}
    if task1_final.get("features", {}).get("profile") != "safe_core_plus_history":
        raise PreprocessingManifestError("Task 1 frozen feature profile changed.")
    if task1_features.get("optional_context") != {
        "road_enabled": False,
        "traffic_enabled": False,
        "road_join_keys": ["date", "district"],
        "traffic_join_keys": ["district", "dow", "monsoon", "planned_arrival_hour"],
        "traffic_hour_column": "hour",
    }:
        raise PreprocessingManifestError("Task 1 optional-context contract changed.")

    history_sources = task2a_history.get("official_sources") or {}
    if history_sources != {
        "deliveries_train": "deliveries_train.csv",
        "task1_test_inputs": "task1_test_inputs.csv",
        "calendar": "calendar.csv",
    }:
        raise PreprocessingManifestError("Task 2A official history sources changed.")
    if task2a_history.get("required_dispatch_statuses") != ["attempted", "deferred", "not_run"]:
        raise PreprocessingManifestError("Task 2A dispatch-status retention changed.")
    if task2a_final.get("state") != "FROZEN":
        raise PreprocessingManifestError("Task 2A final model configuration is not frozen.")

    objective_levels = task2b_priority.get("objective_levels")
    if objective_levels != OBJECTIVE_LEVELS:
        raise PreprocessingManifestError("Task 2B objective hierarchy changed.")
    solver = task2b_optimizer.get("solver") or {}
    model = task2b_optimizer.get("model") or {}
    optimizer_time = task2b_optimizer.get("time") or {}
    if solver.get("engine") != "ortools_cp_sat" or solver.get("num_search_workers") != 1:
        raise PreprocessingManifestError("Task 2B deterministic solver contract changed.")
    if model.get("trip_ids") != [1, 2] or optimizer_time.get("include_return_leg") is not False:
        raise PreprocessingManifestError("Task 2B trip contract changed.")
    if task2b_trip.get("include_return_leg") is not False:
        raise PreprocessingManifestError("Task 2B trip-time config added a return leg.")

    return {
        "version": 1,
        "phase": 30,
        "official_requirement": (
            "Brief write-up of data preparation, label construction, data cleaning, "
            "feature engineering, and rationale."
        ),
        "source_configs": [
            "configs/dataset_manifest.yaml",
            "configs/task1_features.yaml",
            "configs/task1_validation.yaml",
            "configs/task1_final_models.yaml",
            "configs/task1_inference.yaml",
            "configs/task2a_history.yaml",
            "configs/task2a_features.yaml",
            "configs/task2a_validation.yaml",
            "configs/task2a_final_models.yaml",
            "configs/task2a_inference.yaml",
            "configs/task2b_scenario.yaml",
            "configs/task2b_trip_time.yaml",
            "configs/task2b_priority.yaml",
            "configs/task2b_optimizer.yaml",
            "configs/task2b_validation.yaml",
            "configs/task2b_output.yaml",
        ],
        "inputs": _dataset_inventory(dataset_manifest),
        "joins": [
            {"task": "Task 1 train", "left": "deliveries_train", "right": "route_legs_train", "keys": "(route_id, seq_in_route) -> (route_id, seq)", "cardinality": "one_to_one"},
            {"task": "Task 1 test", "left": "task1_test_inputs", "right": "route_legs_test", "keys": "(route_id, seq_in_route) -> (route_id, seq)", "cardinality": "one_to_one"},
            {"task": "Task 1", "left": "orders", "right": "outlets", "keys": "outlet_id", "cardinality": "many_to_one"},
            {"task": "Task 1", "left": "orders", "right": "vehicles", "keys": "vehicle_id", "cardinality": "many_to_one"},
            {"task": "Task 1", "left": "orders", "right": "calendar", "keys": "date", "cardinality": "many_to_one"},
            {"task": "Task 1", "left": "orders", "right": "district_travel", "keys": "(district, depot)", "cardinality": "many_to_one"},
            {"task": "Task 1 and Task 2B", "left": "orders", "right": "service_allowance", "keys": "(brand, dock_type)", "cardinality": "many_to_one"},
            {"task": "Task 2A", "left": "requested orders", "right": "calendar", "keys": "order_date -> date", "cardinality": "many_to_one"},
            {"task": "Task 2B", "left": "scenario fleet", "right": "vehicles", "keys": "vehicle_id", "cardinality": "one_to_one"},
            {"task": "Task 2B", "left": "trip", "right": "district_travel", "keys": "(depot, district)", "cardinality": "many_to_one"},
            {"task": "Task 2B output", "left": "official template", "right": "allocation", "keys": "order_ref", "cardinality": "one_to_one"},
        ],
        "task1_labels": {
            "eligible_dispatch_statuses": ["attempted", "deferred"],
            "excluded_dispatch_status": "not_run",
            "service_start": "max(arrival_time_dt, window_open_dt)",
            "service_minutes": "(leave_outlet_time_dt - service_start_dt) / 60",
            "late_flag": "1 only when arrival_time_dt > window_close_dt",
            "arrival_at_close_is_late": False,
            "early_wait_is_service": False,
            "midnight_handling": "deterministic route-sequence rollover with source-duration consistency check",
        },
        "cleaning": {
            "policy": "fail_closed_for_schema_identity_reference_and_impossible_values",
            "row_dropping": "no generic invalid-row dropping",
            "missing_model_features": "model-specific handling only after contract validation",
            "official_identity": "preserve exact keys and required template order",
        },
        "task1_features": {
            "profile": task1_final["features"]["profile"],
            "groups": [
                "planned timing and delivery-window context",
                "planned travel and distance",
                "order size and cargo ratios",
                "outlet brand district depot dock and access context",
                "vehicle capability capacity and planned utilization",
                "route position workload and prior planned stops",
                "calendar context and service allowance",
                "chronology-safe historical aggregates",
            ],
            "road_context_enabled": task1_features["optional_context"]["road_enabled"],
            "traffic_context_enabled": task1_features["optional_context"]["traffic_enabled"],
        },
        "task1_leakage": {
            "forbidden_direct_predictors": FORBIDDEN_TASK1_PREDICTORS,
            "historical_fit_scope": task1_inference["features"]["historical_state"]["fit_scope"],
            "test_rows_update_history": task1_inference["features"]["historical_state"]["update_from_test_rows"],
        },
        "task1_validation": {
            "final_holdout_strategy": task1_validation["final_holdout"],
            "expanding_cv": task1_validation["expanding_cv"],
            "fit_dependent_policy": task1_validation["fit_dependent_features"],
            "service_primary_metric": task1_validation["metrics"]["regression"]["primary"],
            "lateness_primary_metric": task1_validation["metrics"]["lateness_probability"]["primary"],
        },
        "task1_models": {
            "service_family": service["family"],
            "service_config_id": service["config_id"],
            "service_postprocessing": "fail_on_negative_prediction" if not service["prediction_postprocessing"]["phase09_clipping"] else "clip_to_zero",
            "lateness_family": lateness["family"],
            "lateness_config_id": lateness["config_id"],
            "calibration": calibration.get("method", "raw"),
            "calibration_protocol": calibration.get("fit_protocol", "none"),
        },
        "task2a_history": {
            "sources": list(history_sources.values()),
            "order_key": task2a_history["order_key"],
            "requested_date_column": task2a_history["requested_date_column"],
            "retained_statuses": task2a_history["required_dispatch_statuses"],
            "series_keys": task2a_history["series_keys"],
            "week_keys": task2a_history["week_keys"],
            "calendar_iso_source_of_truth": task2a_history["calendar"]["use_calendar_iso_fields_as_source_of_truth"],
            "zero_fill_policy": "confirmed_complete_interior_gaps_only",
        },
        "task2a_features": {
            "strategy": task2a_features["multihorizon"]["strategy"],
            "horizons": [task2a_features["multihorizon"]["min_horizon"], task2a_features["multihorizon"]["max_horizon"]],
            "lags": task2a_features["lags"]["values"],
            "rolling_windows": task2a_features["rolling_means"]["windows"],
            "trend_windows": task2a_features["trend"]["compare_windows"],
            "target_week_calendar_required": task2a_features["multihorizon"]["require_target_week_calendar"],
            "missing_history_policy": task2a_features["missing_history"]["policy"],
        },
        "task2a_validation": {
            "strategy": task2a_validation["backtesting"]["strategy"],
            "n_backtests": task2a_validation["backtesting"]["n_backtests"],
            "validation_horizon_weeks": task2a_validation["backtesting"]["validation_horizon_weeks"],
            "minimum_training_weeks": task2a_validation["backtesting"]["minimum_training_weeks"],
            "require_target_week_on_or_before_origin": task2a_validation["training_eligibility"]["require_target_week_on_or_before_origin"],
        },
        "task2a_models": {
            "state": task2a_final["state"],
            "final_strategy": "direct_global_table_separate_target_ensembles",
            "total_family": task2a_final["total"]["family"],
            "total_config_id": task2a_final["total"]["candidate_id"],
            "total_weights": task2a_final["total"]["component_weights"],
            "chilled_family": task2a_final["chilled_fresh"]["family"],
            "chilled_config_id": task2a_final["chilled_fresh"]["candidate_id"],
            "chilled_weights": task2a_final["chilled_fresh"]["component_weights"],
            "chilled_scope": "Fresh_only",
        },
        "task2a_postprocessing": {
            **task2a_inference["postprocessing"],
            **task2a_inference["structural_output_rules"],
            "preserve_template_order": task2a_inference["submission"]["preserve_template_order"],
        },
        "task2b_inputs": {
            "scenario": task2b_scenario["scenario"],
            "available_status": task2b_scenario["fleet"]["available_status"],
            "workshop_status": task2b_scenario["fleet"]["workshop_status"],
            "allocation_key": "order_ref",
        },
        "task2b_compatibility": {
            "pair_checks": ["refrigeration", "van_only access", "home depot", "single-order weight", "single-order volume"],
            "trip_group_checks": ["same brand", "same district", "whole order", "weight capacity", "volume capacity"],
        },
        "task2b_trip_time": {
            "formula": "depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)",
            "service_allowance_keys": task2b_trip["service_allowance_keys"],
            "include_return_leg": task2b_trip["include_return_leg"],
            "rounding": task2b_trip["rounding"],
            "fresh_budget_min": optimizer_time["fresh_budget_min"],
            "style_tech_budget_min": optimizer_time["style_tech_budget_min"],
        },
        "task2b_hard_rules": [
            "same brand and district per trip",
            "chilled requires reefer",
            "van_only requires van",
            "vehicle home depot must match",
            "whole order with no split",
            "both weight and volume capacity",
            "at most two trips plus Fresh and Style+Tech daily time budgets",
        ],
        "task2b_priority": {
            "origin": "WayLoom engineering policy; not organizer priority",
            "strategy": task2b_priority["strategy"],
            "objective_levels": objective_levels,
            "hard_rule_override": task2b_priority["hard_rule_override"],
        },
        "task2b_validation": {
            "solver": "OR-Tools CP-SAT",
            "solver_engine": solver["engine"],
            "deterministic_seed": solver["random_seed"],
            "deterministic_workers": solver["num_search_workers"],
            "require_all_objective_stages_optimal": solver["require_optimal_objective_stages_for_freeze"],
            "independent_validator": "solver-neutral feasibility audit",
            "official_checker": "feasibility only; does not prove optimality",
            "require_frozen_hash": task2b_validation["allocation"]["require_sha256_match"],
            "official_export_columns": task2b_output["output"]["exact_columns"],
        },
        "outputs": {
            "task1": TASK1_OUTPUT_COLUMNS,
            "task2a": TASK2A_OUTPUT_COLUMNS,
            "task2b": TASK2B_OUTPUT_COLUMNS,
        },
        "privacy": {
            "contains_private_rows": False,
            "contains_real_identifiers": False,
            "contains_absolute_user_paths": False,
            "reads_private_data": False,
        },
        "task_completeness": {
            "DT-379": ["2. Input datasets"],
            "DT-380": ["4.1 joins", "5.1 demand-history construction", "6.2 compatibility preparation"],
            "DT-381": ["4.2 label construction"],
            "DT-382": ["3. Shared data preparation and quality controls", "4.3 cleaning", "5.3 cleaning"],
            "DT-383": ["4.4 feature engineering", "5.4 forecasting features", "6.2 compatibility preparation"],
            "DT-384": ["4.5 leakage prevention", "5.5 leakage prevention"],
            "DT-385": ["4.6 validation", "5.6 rolling validation", "6.6 optimizer / independent validation / official export"],
            "DT-386": ["4.7 final model rationale", "5.7 final forecasting methodology and model rationale"],
            "DT-387": ["5.1 demand-history construction", "5.7 final forecasting methodology and model rationale"],
            "DT-388": ["6. Task 2B - peak-day allocation preparation"],
        },
    }


def write_manifest(output: Path = DEFAULT_OUTPUT) -> Path:
    output = output.resolve()
    if output != DEFAULT_OUTPUT.resolve():
        raise PreprocessingManifestError("Preprocessing manifest must use docs/preprocessing_manifest.yaml")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(build_manifest(), sort_keys=False, allow_unicode=False, width=110),
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_manifest(args.output)
    print("LOCAL PHASE 30 PREPROCESSING MANIFEST BUILD: PASS")
    print("SAFE CONFIG SOURCES ONLY: YES")
    print("PRIVATE DATA ACCESSED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
