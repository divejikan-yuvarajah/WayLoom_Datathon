"""Build the safe, config-derived Phase 29 architecture manifest."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "architecture" / "architecture_manifest.yaml"

TASK1_OUTPUT_COLUMNS = ["delivery_id", "pred_service_min", "pred_late_prob"]
TASK2A_OUTPUT_COLUMNS = ["row_id", "pred_total_volume_m3", "pred_chilled_volume_m3"]
TASK2B_OUTPUT_COLUMNS = ["scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id"]
FORBIDDEN_TASK1_ACTUALS = [
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
]
EXPECTED_OBJECTIVES = [
    ("served_order_count", "maximize"),
    ("served_previous_deferred_count", "maximize"),
    ("served_waiting_days_sum", "maximize"),
    ("served_low_flexibility_count", "maximize"),
    ("served_fresh_chilled_count", "maximize"),
    ("served_fresh_count", "maximize"),
    ("avoidable_reefer_van_assignment_count", "minimize"),
    ("avoidable_reefer_assignment_count", "minimize"),
    ("avoidable_van_assignment_count", "minimize"),
]


class ArchitectureManifestError(ValueError):
    """A frozen architecture fact is missing or contradictory."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArchitectureManifestError(f"Invalid safe configuration: {path.name}")
    return value


def _source_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    value = mapping.get(key)
    if value in (None, "", [], {}):
        raise ArchitectureManifestError(f"Missing {context}.{key}")
    return value


def build_manifest(config_root: Path = ROOT / "configs") -> dict[str, Any]:
    task1 = _load_yaml(config_root / "task1_final_models.yaml")
    task2a = _load_yaml(config_root / "task2a_final_models.yaml")
    task2a_features = _load_yaml(config_root / "task2a_features.yaml")
    optimizer = _load_yaml(config_root / "task2b_optimizer.yaml")
    priority = _load_yaml(config_root / "task2b_priority.yaml")

    service = _require(task1, "service_model", "task1")
    late = _require(task1, "lateness_model", "task1")
    feature_info = _require(task1, "features", "task1")
    calibration = late.get("calibration") or {}
    clipping = bool((service.get("prediction_postprocessing") or {}).get("phase09_clipping"))
    if clipping:
        service_postprocessing = "clip_to_zero"
    else:
        service_postprocessing = "fail_on_negative_prediction"

    multihorizon = _require(task2a_features, "multihorizon", "task2a_features")
    if multihorizon.get("strategy") != "direct_global_table":
        raise ArchitectureManifestError("Task 2A direct-global strategy changed.")
    if [multihorizon.get("min_horizon"), multihorizon.get("max_horizon")] != [1, 10]:
        raise ArchitectureManifestError("Task 2A horizons are not exactly 1..10.")

    total = _require(task2a, "total", "task2a")
    chilled = _require(task2a, "chilled_fresh", "task2a")
    if task2a.get("state") != "FROZEN":
        raise ArchitectureManifestError("Task 2A final configuration is not frozen.")
    structural = task2a.get("structural_output_rules") or {}
    postprocessing = task2a.get("phase17_postprocessing") or {}
    if structural != {"style_chilled_zero": True, "tech_chilled_zero": True}:
        raise ArchitectureManifestError("Task 2A structural chilled-zero rules changed.")
    if postprocessing.get("clip_negative") is not True or postprocessing.get("enforce_chilled_le_total") is not True:
        raise ArchitectureManifestError("Task 2A final postprocessing changed.")

    solver = _require(optimizer, "solver", "task2b_optimizer")
    model = _require(optimizer, "model", "task2b_optimizer")
    time = _require(optimizer, "time", "task2b_optimizer")
    objective_levels = [tuple(item) for item in _require(priority, "objective_levels", "task2b_priority")]
    if objective_levels != EXPECTED_OBJECTIVES:
        raise ArchitectureManifestError("Task 2B objective order differs from the frozen policy.")
    if solver.get("engine") != "ortools_cp_sat":
        raise ArchitectureManifestError("Task 2B solver is not the frozen OR-Tools CP-SAT engine.")
    if model.get("trip_ids") != [1, 2] or time.get("include_return_leg") is not False:
        raise ArchitectureManifestError("Task 2B trip contract changed.")

    return {
        "version": 1,
        "phase": 29,
        "status": "final",
        "contains_private_data": False,
        "source_commit": _source_commit(),
        "source_configs": [
            "configs/task1_final_models.yaml",
            "configs/task2a_final_models.yaml",
            "configs/task2a_features.yaml",
            "configs/task2b_optimizer.yaml",
            "configs/task2b_priority.yaml",
        ],
        "task1": {
            "feature_profile": _require(feature_info, "profile", "task1.features"),
            "service_model_family": _require(service, "family", "task1.service_model"),
            "service_config_id": _require(service, "config_id", "task1.service_model"),
            "late_model_family": _require(late, "family", "task1.lateness_model"),
            "late_config_id": _require(late, "config_id", "task1.lateness_model"),
            "late_calibration": calibration.get("method", "raw"),
            "late_calibration_protocol": calibration.get("fit_protocol", "none"),
            "service_postprocessing": service_postprocessing,
            "prediction_time_actual_fields_forbidden": FORBIDDEN_TASK1_ACTUALS,
            "output_columns": TASK1_OUTPUT_COLUMNS,
        },
        "task2a": {
            "forecast_horizon_weeks": 10,
            "feature_strategy": multihorizon["strategy"],
            "final_strategy": "direct_global_table_separate_target_ensembles",
            "total_model_family": _require(total, "family", "task2a.total"),
            "total_config_id": _require(total, "candidate_id", "task2a.total"),
            "total_component_count": len(total.get("component_candidates") or []),
            "chilled_model_family_or_strategy": _require(chilled, "family", "task2a.chilled_fresh"),
            "chilled_config_id": _require(chilled, "candidate_id", "task2a.chilled_fresh"),
            "chilled_scope": "Fresh_only; Style_and_Tech_structural_zero",
            "chilled_component_count": len(chilled.get("component_candidates") or []),
            "history_sources": ["deliveries_train", "task1_test_inputs"],
            "postprocessing": ["clip_negative", "enforce_chilled_le_total", "Style_chilled_zero", "Tech_chilled_zero"],
            "output_columns": TASK2A_OUTPUT_COLUMNS,
        },
        "task2b": {
            "solver": "OR-Tools CP-SAT",
            "solver_engine": solver["engine"],
            "deterministic_workers": solver.get("num_search_workers"),
            "require_optimal_objective_stages_for_freeze": solver.get("require_optimal_objective_stages_for_freeze"),
            "max_trips_per_vehicle": len(model["trip_ids"]),
            "fresh_minutes_limit": time.get("fresh_budget_min"),
            "style_tech_minutes_limit": time.get("style_tech_budget_min"),
            "include_return_leg": time.get("include_return_leg"),
            "policy_name": priority.get("policy_name"),
            "policy_origin": "WayLoom engineering policy; not organizer priority",
            "objective_levels": [f"{direction.upper()} {name}" for name, direction in objective_levels],
            "output_columns": TASK2B_OUTPUT_COLUMNS,
        },
        "deployment": {
            "status": "proposed",
            "default_execution": "private_local_batch",
            "external_proprietary_modelling_api": False,
            "hackathon_integration_required": False,
            "phase28_integration_contract": "optional_synthetic_or_internal",
        },
        "diagrams": [
            {"diagram_id": "high_level_datathon", "title": "High-level WayLoom Datathon architecture", "status": "final", "contains_private_data": False},
            {"diagram_id": "task1_pipeline", "title": "Task 1 service-time and lateness pipeline", "status": "final", "contains_private_data": False},
            {"diagram_id": "task2a_forecasting", "title": "Task 2A ten-week demand forecasting pipeline", "status": "final", "contains_private_data": False},
            {"diagram_id": "task2b_optimization", "title": "Task 2B peak-day optimization pipeline", "status": "final", "contains_private_data": False},
            {"diagram_id": "proposed_deployment", "title": "Proposed private batch deployment", "status": "final", "contains_private_data": False},
        ],
    }


def write_manifest(output: Path = DEFAULT_OUTPUT) -> Path:
    output = output.resolve()
    expected_root = (ROOT / "docs" / "architecture").resolve()
    if output.parent != expected_root or output.name != "architecture_manifest.yaml":
        raise ArchitectureManifestError("Architecture manifest output must use the canonical documentation path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(build_manifest(), sort_keys=False, allow_unicode=False), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_manifest(args.output)
    print("LOCAL PHASE 29 ARCHITECTURE MANIFEST BUILD: PASS")
    print("PRIVATE DATA ACCESSED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
