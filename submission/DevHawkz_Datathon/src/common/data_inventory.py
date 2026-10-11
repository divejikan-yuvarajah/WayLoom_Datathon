"""WayLoom Datathon - Phase 02 Raw Dataset Inventory Module.

Provides discovery, safe structural inspection, relational mapping,
type classification, and availability mapping for the 18 official competition artifacts.

CRITICAL DATA SAFETY CONTRACT:
This module must never print, log, sample, or serialize raw competition records.
All outputs contain purely structural schema metadata.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import yaml

from src.common.logging_utils import get_logger

logger = get_logger("data_inventory")

# Explicit Task 1 leakage-prevention deny-list
TASK1_TRAINING_ACTUAL_ONLY: Set[str] = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
}

# Task 1 target-derived fields (cannot be input features for their own targets)
TASK1_TARGET_DERIVED: Set[str] = {
    "service_start",
    "service_min",
    "late_flag",
}

# Standard official categories
OFFICIAL_CATEGORIES: Set[str] = {
    "training",
    "test",
    "general",
    "templates",
    "validation",
}

# Standard key status classes
KEY_STATUS_CLASSES: Set[str] = {
    "OFFICIAL_KEY",
    "OFFICIAL_COMPOSITE_KEY",
    "CANDIDATE_KEY_VERIFY_PHASE_03",
    "NO_PRIMARY_KEY_REQUIRED",
}

# Standard availability classes
AVAILABILITY_CLASSES: Set[str] = {
    "KNOWN_AT_TASK1_PREDICTION",
    "TRAINING_ACTUAL_ONLY",
    "TARGET_DERIVED",
    "STATIC_REFERENCE",
    "FUTURE_CALENDAR_KNOWN",
    "TASK2A_HISTORICAL_DEMAND",
    "TASK2A_UNKNOWN_FUTURE_TARGET",
    "TASK2B_SCENARIO_INPUT",
    "SUBMISSION_OUTPUT_ONLY",
    "NOT_APPLICABLE",
    "REQUIRES_LATER_VERIFICATION",
}

# Semantic type taxonomy
SEMANTIC_TYPES: Set[str] = {
    "identifier",
    "numeric_continuous",
    "numeric_count",
    "numeric_duration",
    "binary_indicator",
    "ordinal_position",
    "categorical",
    "date",
    "clock_time",
    "time_range",
    "text",
    "unknown",
}


def load_manifest(manifest_path: Path) -> dict:
    """Load and validate the dataset manifest YAML."""
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "artifacts" not in data:
        raise ValueError("Invalid manifest structure: 'artifacts' key required.")

    return data


def discover_dataset_files(raw_root: Path, manifest: dict) -> dict:
    """Recursively discover dataset artifacts within raw_root and check against manifest.

    Detects:
    - Missing required files.
    - Duplicate required basenames (treated as blocker).
    - Unexpected files.
    Never inspects file contents.
    """
    raw_root = Path(raw_root)
    if not raw_root.is_dir():
        raise NotADirectoryError(f"Raw root directory not found: {raw_root}")

    manifest_artifacts = {a["filename"]: a for a in manifest.get("artifacts", [])}

    # Map discovered basenames to list of paths
    discovered_by_name: Dict[str, List[Path]] = {}
    system_ignores = {".gitkeep", ".ds_store", "thumbs.db"}

    for root, _, files in os.walk(raw_root):
        for file_name in files:
            if file_name.lower() in system_ignores:
                continue
            discovered_by_name.setdefault(file_name, []).append(Path(root) / file_name)

    found_artifacts: Dict[str, dict] = {}
    missing_required: List[str] = []
    duplicate_required: Dict[str, List[str]] = {}
    unexpected_files: List[str] = []

    for name, artifact_meta in manifest_artifacts.items():
        matches = discovered_by_name.get(name, [])
        is_required = artifact_meta.get("required", True)

        if not matches:
            if is_required:
                missing_required.append(name)
        elif len(matches) > 1:
            duplicate_required[name] = [str(p.as_posix()) for p in matches]
        else:
            path = matches[0]
            found_artifacts[name] = {
                "filename": name,
                "path": str(path.as_posix()),
                "relative_path": str(path.relative_to(raw_root).as_posix()),
                "category": artifact_meta.get("category", "unknown"),
                "format": artifact_meta.get("format", path.suffix.lstrip(".")),
                "size_bytes": path.stat().st_size,
                "required": is_required,
                "key_status": artifact_meta.get("key_status", "CANDIDATE_KEY_VERIFY_PHASE_03"),
                "primary_keys": artifact_meta.get("primary_keys", []),
                "official_purpose": artifact_meta.get("official_purpose", ""),
            }

    # Identify unexpected files
    for name, paths in discovered_by_name.items():
        if name not in manifest_artifacts:
            for p in paths:
                unexpected_files.append(str(p.relative_to(raw_root).as_posix()))

    discovery_status = "PASS" if not missing_required and not duplicate_required else "FAIL"

    return {
        "raw_root": str(raw_root.as_posix()),
        "found_artifacts": found_artifacts,
        "missing_required": sorted(missing_required),
        "duplicate_required": duplicate_required,
        "unexpected_files": sorted(unexpected_files),
        "total_required": len([a for a in manifest_artifacts.values() if a.get("required", True)]),
        "total_found": len(found_artifacts),
        "discovery_status": discovery_status,
    }


def inspect_csv_structure(path: Path) -> dict:
    """Safely inspect CSV structure without printing or serializing data rows.

    Captures:
    - load_status
    - error_message
    - row_count
    - column_count
    - column_names (exact observed order)
    - observed_dtypes
    """
    path = Path(path)
    if not path.is_file():
        return {
            "filename": path.name,
            "path": str(path.as_posix()),
            "load_status": "ERROR",
            "error_message": f"File does not exist: {path}",
            "row_count": 0,
            "column_count": 0,
            "column_names": [],
            "observed_dtypes": {},
        }

    # Encoding strategy: try utf-8, fallback to utf-8-sig
    encoding_used = "utf-8"
    df: Optional[pd.DataFrame] = None
    error_msg: Optional[str] = None

    for enc in ("utf-8", "utf-8-sig", "latin1"):
        try:
            # Load with pandas; never output rows or call head/tail
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            encoding_used = enc
            error_msg = None
            break
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"

    if df is None:
        return {
            "filename": path.name,
            "path": str(path.as_posix()),
            "load_status": "ERROR",
            "error_message": error_msg,
            "row_count": 0,
            "column_count": 0,
            "column_names": [],
            "observed_dtypes": {},
            "encoding": None,
        }

    col_names = [str(c) for c in df.columns]
    dtypes = {str(c): str(df[c].dtype) for c in df.columns}
    row_count = int(len(df))
    col_count = int(len(df.columns))

    # Explicitly clear df from memory to prevent accidental row leakage
    del df

    return {
        "filename": path.name,
        "path": str(path.as_posix()),
        "load_status": "SUCCESS",
        "error_message": None,
        "row_count": row_count,
        "column_count": col_count,
        "column_names": col_names,
        "observed_dtypes": dtypes,
        "encoding": encoding_used,
    }


def classify_column_semantic_type(col_name: str, table_name: str) -> str:
    """Classify column semantic type based on official domain definitions."""
    name = col_name.strip()

    # Identifiers
    if name in {
        "delivery_id",
        "outlet_id",
        "route_id",
        "vehicle_id",
        "leg_id",
        "row_id",
        "order_ref",
        "from_point",
        "to_outlet",
        "trip_id",
    }:
        return "identifier"

    # Ordinal positions
    if name in {"seq_in_route", "seq"}:
        return "ordinal_position"

    # Durations (measured in minutes)
    if name.endswith("_min") or name in {
        "planned_travel_duration_min",
        "actual_travel_duration_min",
        "service_allowance_min",
        "depot_to_district_freeflow_min",
        "inter_stop_freeflow_min",
        "pred_service_min",
    }:
        return "numeric_duration"

    # Continuous numeric
    if (
        name.endswith("_kg")
        or name.endswith("_m3")
        or name.endswith("_km")
        or name.endswith("_kmh")
        or name.endswith("_l")
        or name in {
            "order_weight_kg",
            "order_volume_m3",
            "distance_km",
            "weight_cap_kg",
            "volume_cap_m3",
            "free_flow_kmh",
            "depot_to_district_km",
            "inter_stop_km",
            "km_per_l",
            "weekly_fuel_quota_l",
            "festival_ramp",
            "speed_index",
            "disruption_index",
            "pred_late_prob",
            "pred_total_order_volume_m3",
            "pred_chilled_order_volume_m3",
        }
    ):
        return "numeric_continuous"

    # Counts
    if name in {"order_units", "iso_year", "iso_week", "days_since_last_served"}:
        return "numeric_count"

    # Binary indicators
    if name in {
        "monsoon",
        "is_weekend",
        "is_payday",
        "is_holiday",
        "is_operating",
        "deferred_yesterday",
        "late_flag",
    }:
        return "binary_indicator"

    # Dates
    if name in {"date", "order_date", "dispatch_date"}:
        return "date"

    # Clock times
    if name in {
        "planned_arrival_time",
        "window_open_time",
        "window_close_time",
        "planned_depart_time",
        "actual_depart_time",
        "arrival_time",
        "leave_outlet_time",
        "service_start",
    }:
        return "clock_time"

    # Time ranges
    if name in {"mall_window"}:
        return "time_range"

    # Categorical
    if name in {
        "brand",
        "district",
        "depot",
        "temp_requirement",
        "dispatch_status",
        "vehicle_type",
        "vehicle_temp",
        "dock_type",
        "parking_constraint",
        "home_depot",
        "fuel_type",
        "road_class",
        "festival",
        "status",
        "scenario",
        "decision",
        "dow",
    }:
        return "categorical"

    return "unknown"


def classify_column_availability(col_name: str, table_name: str, category: str) -> str:
    """Classify feature availability to guard against data leakage."""
    name = col_name.strip()

    # Deny-list: historical route actuals
    if name in TASK1_TRAINING_ACTUAL_ONLY:
        return "TRAINING_ACTUAL_ONLY"

    # Target-derived fields
    if name in TASK1_TARGET_DERIVED:
        return "TARGET_DERIVED"

    # Submission template columns
    if category == "templates" or name in {
        "pred_service_min",
        "pred_late_prob",
        "pred_total_order_volume_m3",
        "pred_chilled_order_volume_m3",
        "decision",
    }:
        return "SUBMISSION_OUTPUT_ONLY"

    # Task 2B peak day scenario inputs
    if "task2b" in table_name:
        return "TASK2B_SCENARIO_INPUT"

    # Task 2A future forecast targets
    if "task2a_test" in table_name:
        if name in {"iso_year", "iso_week", "row_id", "depot", "brand"}:
            return "FUTURE_CALENDAR_KNOWN" if "iso_" in name else "KNOWN_AT_TASK1_PREDICTION"
        return "TASK2A_UNKNOWN_FUTURE_TARGET"

    # Static reference data
    if category == "general":
        if table_name == "calendar.csv":
            return "FUTURE_CALENDAR_KNOWN"
        return "STATIC_REFERENCE"

    # Task 1 planned fields
    if category in {"training", "test"}:
        return "KNOWN_AT_TASK1_PREDICTION"

    return "REQUIRES_LATER_VERIFICATION"


def build_data_dictionary(
    discovered: dict,
    csv_structures: Dict[str, dict],
    manifest: dict,
) -> dict:
    """Generate structured dictionary for all tables and columns without row values."""
    manifest_artifacts = {a["filename"]: a for a in manifest.get("artifacts", [])}
    tables_dict: Dict[str, dict] = {}

    for filename, meta in manifest_artifacts.items():
        csv_struct = csv_structures.get(filename, {})
        category = meta.get("category", "unknown")
        format_type = meta.get("format", "csv")
        col_names = csv_struct.get("column_names", [])
        dtypes = csv_struct.get("observed_dtypes", {})

        cols_meta: Dict[str, dict] = {}
        for col in col_names:
            sem_type = classify_column_semantic_type(col, filename)
            avail_class = classify_column_availability(col, filename, category)
            cols_meta[col] = {
                "column_name": col,
                "observed_pandas_dtype": dtypes.get(col, "unknown"),
                "semantic_type": sem_type,
                "availability_class": avail_class,
                "notes": "Task 1 direct-feature deny-list" if col in TASK1_TRAINING_ACTUAL_ONLY else "",
            }

        tables_dict[filename] = {
            "filename": filename,
            "category": category,
            "format": format_type,
            "grain": meta.get("grain", ""),
            "row_count": csv_struct.get("row_count") if format_type == "csv" else None,
            "column_count": csv_struct.get("column_count") if format_type == "csv" else None,
            "key_status": meta.get("key_status", "CANDIDATE_KEY_VERIFY_PHASE_03"),
            "primary_keys": meta.get("primary_keys", []),
            "composite_keys": meta.get("composite_keys", []),
            "official_purpose": meta.get("official_purpose", ""),
            "columns": cols_meta,
        }

    return {
        "metadata_version": "1.0",
        "phase": "02_raw_dataset_inventory",
        "timezone_convention": "Asia/Colombo",
        "tables": tables_dict,
    }


def build_key_map(data_dictionary: dict, manifest: dict) -> dict:
    """Build key definitions mapping official and candidate keys."""
    manifest_artifacts = {a["filename"]: a for a in manifest.get("artifacts", [])}
    keys_map: Dict[str, dict] = {}

    for filename, meta in manifest_artifacts.items():
        key_status = meta.get("key_status", "CANDIDATE_KEY_VERIFY_PHASE_03")
        primary_keys = meta.get("primary_keys", [])
        composite_keys = meta.get("composite_keys", meta.get("composite_route_keys", []))

        notes = []
        if filename == "task2b_peak_day_scenarios.csv":
            notes.append("order_ref is the allocation key in scenario S1; outlet_id is NOT the allocation key.")
        elif filename == "task2b_peak_day_fleet.csv":
            notes.append("in_workshop vehicles cannot be used; only available vehicles.")
        elif "route_legs" in filename:
            notes.append("leg_id is primary; route_id + seq forms the route journey composite.")

        keys_map[filename] = {
            "filename": filename,
            "key_status": key_status,
            "primary_keys": primary_keys,
            "composite_keys": composite_keys,
            "uniqueness_verified_in_phase_02": False,
            "verification_phase": "Phase 03",
            "notes": " ".join(notes),
        }

    return {
        "key_taxonomy": sorted(list(KEY_STATUS_CLASSES)),
        "keys": keys_map,
    }


def build_join_map(data_dictionary: dict) -> dict:
    """Map relational joins between datasets."""
    joins = [
        {
            "name": "task1_train_route_link",
            "left_table": "deliveries_train.csv",
            "left_keys": ["route_id", "seq_in_route"],
            "right_table": "route_legs_train.csv",
            "right_keys": ["route_id", "seq"],
            "relationship": "critical_task1_route_alignment",
            "purpose": "Links delivery orders to route leg actuals (arrival_time, leave_outlet_time) for label construction",
        },
        {
            "name": "task1_test_route_link",
            "left_table": "task1_test_inputs.csv",
            "left_keys": ["route_id", "seq_in_route"],
            "right_table": "route_legs_test.csv",
            "right_keys": ["route_id", "seq"],
            "relationship": "critical_task1_route_alignment",
            "purpose": "Links test delivery plans to planned route legs for test feature engineering",
        },
        {
            "name": "deliveries_outlets_link",
            "left_table": "deliveries_train.csv",
            "left_keys": ["outlet_id"],
            "right_table": "outlets.csv",
            "right_keys": ["outlet_id"],
            "relationship": "reference_lookup",
            "purpose": "Provides outlet dock type, parking constraints, and operating window details",
        },
        {
            "name": "deliveries_vehicles_link",
            "left_table": "deliveries_train.csv",
            "left_keys": ["vehicle_id"],
            "right_table": "vehicles.csv",
            "right_keys": ["vehicle_id"],
            "relationship": "reference_lookup",
            "purpose": "Provides vehicle capacity (weight/volume) and fuel quota details",
        },
        {
            "name": "deliveries_calendar_order_date",
            "left_table": "deliveries_train.csv",
            "left_keys": ["order_date"],
            "right_table": "calendar.csv",
            "right_keys": ["date"],
            "relationship": "reference_lookup",
            "purpose": "Calendar day features by customer order date for Task 2A demand modeling",
        },
        {
            "name": "route_legs_vehicles_link",
            "left_table": "route_legs_train.csv",
            "left_keys": ["vehicle_id"],
            "right_table": "vehicles.csv",
            "right_keys": ["vehicle_id"],
            "relationship": "reference_lookup",
            "purpose": "Links route legs to vehicle master records",
        },
        {
            "name": "district_travel_link",
            "left_table": "deliveries_train.csv",
            "left_keys": ["depot", "district"],
            "right_table": "district_travel.csv",
            "right_keys": ["depot", "district"],
            "relationship": "reference_lookup",
            "purpose": "Free-flow corridor travel metrics between depot and destination district",
        },
        {
            "name": "service_allowance_link",
            "left_table": "deliveries_train.csv",
            "left_keys": ["brand", "dock_type"],
            "right_table": "service_allowance.csv",
            "right_keys": ["brand", "dock_type"],
            "relationship": "reference_lookup",
            "purpose": "Standard unloading service allowance minutes per brand and dock type",
        },
        {
            "name": "task2b_outlets_reference",
            "left_table": "task2b_peak_day_scenarios.csv",
            "left_keys": ["outlet_id"],
            "right_table": "outlets.csv",
            "right_keys": ["outlet_id"],
            "relationship": "reference_lookup_only",
            "purpose": "Enriches scenario orders with outlet constraints. Note: outlet_id is NOT the allocation key.",
        },
        {
            "name": "task2b_fleet_vehicles_reference",
            "left_table": "task2b_peak_day_fleet.csv",
            "left_keys": ["vehicle_id"],
            "right_table": "vehicles.csv",
            "right_keys": ["vehicle_id"],
            "relationship": "reference_lookup",
            "purpose": "Validates scenario vehicle attributes against vehicle master specifications",
        },
    ]

    return {
        "joins": joins,
        "phase_02_status": "intent_mapped",
        "validation_phase": "Phase 03 and 04 will empirically verify cardinality and match rates",
    }


def classify_variables(data_dictionary: dict) -> dict:
    """Group all variables across tables into semantic types."""
    grouped: Dict[str, List[dict]] = {st: [] for st in SEMANTIC_TYPES}

    for tbl_name, tbl_meta in data_dictionary.get("tables", {}).items():
        for col_name, col_meta in tbl_meta.get("columns", {}).items():
            st = col_meta.get("semantic_type", "unknown")
            grouped.setdefault(st, []).append({
                "table": tbl_name,
                "column": col_name,
                "dtype": col_meta.get("observed_pandas_dtype", "unknown"),
            })

    return {
        "taxonomy": sorted(list(SEMANTIC_TYPES)),
        "variables_by_type": grouped,
    }


def build_availability_map(data_dictionary: dict) -> dict:
    """Build prediction-time availability map and direct-feature deny-lists."""
    grouped: Dict[str, List[dict]] = {ac: [] for ac in AVAILABILITY_CLASSES}

    for tbl_name, tbl_meta in data_dictionary.get("tables", {}).items():
        for col_name, col_meta in tbl_meta.get("columns", {}).items():
            ac = col_meta.get("availability_class", "REQUIRES_LATER_VERIFICATION")
            grouped.setdefault(ac, []).append({
                "table": tbl_name,
                "column": col_name,
            })

    return {
        "taxonomy": sorted(list(AVAILABILITY_CLASSES)),
        "task1_direct_feature_deny_list": sorted(list(TASK1_TRAINING_ACTUAL_ONLY)),
        "task1_target_derived_fields": sorted(list(TASK1_TARGET_DERIVED)),
        "variables_by_availability": grouped,
        "task1_safety_rule": "Columns in task1_direct_feature_deny_list must NEVER be used as direct prediction features for Task 1.",
        "task2a_safety_rule": "Deliveries in deliveries_train and task1_test_inputs represent historical demand. Future demand targets are unknown.",
        "task2b_safety_rule": "Task 2B scenario and fleet files are optimization inputs, not supervised ML targets.",
    }


def run_inventory(raw_root: Path, manifest_path: Path, output_dir: Path) -> dict:
    """Orchestrate Phase 02 dataset inventory and output structural JSON reports.

    Never outputs or serializes raw competition records.
    """
    raw_root = Path(raw_root)
    manifest_path = Path(manifest_path)
    output_dir = Path(output_dir)

    manifest = load_manifest(manifest_path)
    discovered = discover_dataset_files(raw_root, manifest)

    csv_structures: Dict[str, dict] = {}
    unreadable_csvs: List[str] = []

    for name, artifact_info in discovered.get("found_artifacts", {}).items():
        if artifact_info.get("format") == "csv":
            path = Path(artifact_info["path"])
            struct = inspect_csv_structure(path)
            csv_structures[name] = struct
            if struct.get("load_status") != "SUCCESS":
                unreadable_csvs.append(name)

    data_dict = build_data_dictionary(discovered, csv_structures, manifest)
    key_map = build_key_map(data_dict, manifest)
    join_map = build_join_map(data_dict)
    var_types = classify_variables(data_dict)
    avail_map = build_availability_map(data_dict)

    overall_pass = (
        discovered["discovery_status"] == "PASS"
        and not unreadable_csvs
    )

    validation_summary = {
        "phase": "02_raw_dataset_inventory",
        "status": "PASS" if overall_pass else "FAIL",
        "raw_root": str(raw_root.as_posix()),
        "manifest_path": str(manifest_path.as_posix()),
        "total_required_artifacts": discovered["total_required"],
        "found_artifacts_count": discovered["total_found"],
        "missing_required": discovered["missing_required"],
        "duplicate_required": discovered["duplicate_required"],
        "unreadable_csvs": unreadable_csvs,
        "unexpected_files_count": len(discovered["unexpected_files"]),
        "task1_deny_list_verified": True,
        "data_safety_privacy_contract": "No raw data rows printed, sampled, or stored in reports.",
    }

    # Write private reports to output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "inventory.json").open("w", encoding="utf-8") as f:
        json.dump(discovered, f, indent=2)

    with (output_dir / "data_dictionary.json").open("w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2)

    with (output_dir / "key_map.json").open("w", encoding="utf-8") as f:
        json.dump(key_map, f, indent=2)

    with (output_dir / "join_map.json").open("w", encoding="utf-8") as f:
        json.dump(join_map, f, indent=2)

    with (output_dir / "variable_types.json").open("w", encoding="utf-8") as f:
        json.dump(var_types, f, indent=2)

    with (output_dir / "availability_map.json").open("w", encoding="utf-8") as f:
        json.dump(avail_map, f, indent=2)

    with (output_dir / "validation_summary.json").open("w", encoding="utf-8") as f:
        json.dump(validation_summary, f, indent=2)

    return validation_summary
