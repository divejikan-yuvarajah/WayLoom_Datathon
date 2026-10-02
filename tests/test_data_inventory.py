"""Tests for Phase 02 Data Inventory Tooling.

CRITICAL DATA SAFETY CONTRACT:
All tests in this suite MUST use synthetic temporary fixtures only.
No official competition files or records may ever be read or tested here.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

from src.common.data_inventory import (
    AVAILABILITY_CLASSES,
    KEY_STATUS_CLASSES,
    SEMANTIC_TYPES,
    TASK1_TARGET_DERIVED,
    TASK1_TRAINING_ACTUAL_ONLY,
    build_availability_map,
    build_data_dictionary,
    build_join_map,
    build_key_map,
    classify_column_availability,
    classify_column_semantic_type,
    classify_variables,
    discover_dataset_files,
    inspect_csv_structure,
    load_manifest,
    run_inventory,
)

# 18 official artifact names
OFFICIAL_18_ARTIFACTS: List[str] = [
    "deliveries_train.csv",
    "route_legs_train.csv",
    "task1_test_inputs.csv",
    "route_legs_test.csv",
    "task2a_test_inputs.csv",
    "task2b_peak_day_scenarios.csv",
    "task2b_peak_day_fleet.csv",
    "outlets.csv",
    "vehicles.csv",
    "calendar.csv",
    "district_travel.csv",
    "service_allowance.csv",
    "traffic_speed.csv",
    "road_conditions.csv",
    "submission_task1.csv",
    "submission_task2a.csv",
    "submission_task2b.csv",
    "check_allocation.py",
]


@pytest.fixture
def synthetic_manifest_path(tmp_path: Path) -> Path:
    """Create a minimal synthetic manifest containing the 18 artifacts."""
    manifest_data = {
        "version": "1.0",
        "artifacts": [
            {
                "filename": name,
                "category": "training" if "train" in name else (
                    "test" if "test" in name or "task2b" in name else (
                        "templates" if "submission" in name else (
                            "validation" if name.endswith(".py") else "general"
                        )
                    )
                ),
                "format": "python" if name.endswith(".py") else "csv",
                "required": True,
                "key_status": "OFFICIAL_KEY" if name in {"deliveries_train.csv", "outlets.csv"} else "CANDIDATE_KEY_VERIFY_PHASE_03",
                "primary_keys": ["delivery_id"] if "deliveries" in name else [],
            }
            for name in OFFICIAL_18_ARTIFACTS
        ],
    }
    manifest_file = tmp_path / "dataset_manifest.yaml"
    with manifest_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(manifest_data, f)
    return manifest_file


@pytest.fixture
def synthetic_raw_root(tmp_path: Path) -> Path:
    """Create synthetic folder with all 18 artifacts containing safe dummy schemas."""
    raw_root = tmp_path / "raw_data"
    raw_root.mkdir()

    # Nested folder with spaces to test robust recursive path handling
    nested_dir = raw_root / "DataSet Subfolder with spaces"
    nested_dir.mkdir()

    for name in OFFICIAL_18_ARTIFACTS:
        target_dir = nested_dir if "task2b" in name or "outlets" in name else raw_root
        file_path = target_dir / name

        if name.endswith(".py"):
            file_path.write_text("# synthetic check script\nprint('OK')\n", encoding="utf-8")
        elif name == "deliveries_train.csv":
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["delivery_id", "order_date", "route_id", "seq_in_route", "order_weight_kg", "order_units"])
                writer.writerow(["SYNTH_DEL_01", "2026-01-01", "R01", 1, 15.5, 3])
                writer.writerow(["SYNTH_DEL_02", "2026-01-01", "R01", 2, 22.0, 5])
        elif name == "route_legs_train.csv":
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "leg_id", "route_id", "seq", "actual_depart_time",
                    "actual_travel_duration_min", "arrival_time", "leave_outlet_time",
                ])
                writer.writerow(["SYNTH_LEG_01", "R01", 1, "08:00", 15.0, "08:15", "08:35"])
        elif name == "task2b_peak_day_scenarios.csv":
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["scenario", "order_ref", "outlet_id", "brand", "order_weight_kg"])
                writer.writerow(["S1", "ORD_001", "OUT_99", "Fresh", 50.0])
        else:
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "dummy_feature"])
                writer.writerow(["D1", 100])

    return raw_root


# -------------------------------------------------------------------------
# DT-024 / DT-025: File Discovery and Categorization Tests
# -------------------------------------------------------------------------

def test_file_discovery_all_present(synthetic_raw_root: Path, synthetic_manifest_path: Path):
    manifest = load_manifest(synthetic_manifest_path)
    result = discover_dataset_files(synthetic_raw_root, manifest)

    assert result["discovery_status"] == "PASS"
    assert result["total_found"] == 18
    assert len(result["missing_required"]) == 0
    assert len(result["duplicate_required"]) == 0


def test_file_discovery_missing_file(synthetic_raw_root: Path, synthetic_manifest_path: Path):
    # Remove one required file
    (synthetic_raw_root / "deliveries_train.csv").unlink()

    manifest = load_manifest(synthetic_manifest_path)
    result = discover_dataset_files(synthetic_raw_root, manifest)

    assert result["discovery_status"] == "FAIL"
    assert "deliveries_train.csv" in result["missing_required"]


def test_file_discovery_duplicate_filename(synthetic_raw_root: Path, synthetic_manifest_path: Path):
    # Duplicate vehicles.csv in another folder
    dup_dir = synthetic_raw_root / "extra_folder"
    dup_dir.mkdir()
    (dup_dir / "vehicles.csv").write_text("id,val\n", encoding="utf-8")

    manifest = load_manifest(synthetic_manifest_path)
    result = discover_dataset_files(synthetic_raw_root, manifest)

    assert result["discovery_status"] == "FAIL"
    assert "vehicles.csv" in result["duplicate_required"]
    assert len(result["duplicate_required"]["vehicles.csv"]) == 2


def test_file_discovery_unexpected_artifact(synthetic_raw_root: Path, synthetic_manifest_path: Path):
    (synthetic_raw_root / "unexpected_file.txt").write_text("hello", encoding="utf-8")

    manifest = load_manifest(synthetic_manifest_path)
    result = discover_dataset_files(synthetic_raw_root, manifest)

    assert result["discovery_status"] == "PASS"
    assert "unexpected_file.txt" in result["unexpected_files"]


# -------------------------------------------------------------------------
# DT-026 / DT-027 / DT-028: CSV Parsing & Schema Structure Tests
# -------------------------------------------------------------------------

def test_inspect_csv_valid(tmp_path: Path):
    csv_file = tmp_path / "test.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["col_a", "col_b", "col_c"])
        writer.writerow(["val1", 2, 3.5])

    result = inspect_csv_structure(csv_file)
    assert result["load_status"] == "SUCCESS"
    assert result["row_count"] == 1
    assert result["column_count"] == 3
    assert result["column_names"] == ["col_a", "col_b", "col_c"]


def test_inspect_csv_header_only(tmp_path: Path):
    csv_file = tmp_path / "header_only.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["col_x", "col_y"])

    result = inspect_csv_structure(csv_file)
    assert result["load_status"] == "SUCCESS"
    assert result["row_count"] == 0
    assert result["column_count"] == 2
    assert result["column_names"] == ["col_x", "col_y"]


def test_inspect_csv_utf8_bom(tmp_path: Path):
    csv_file = tmp_path / "bom.csv"
    # Write with UTF-8 BOM
    with csv_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["col_with_bom", "col_2"])
        writer.writerow(["val", 123])

    result = inspect_csv_structure(csv_file)
    assert result["load_status"] == "SUCCESS"
    assert result["column_names"][0] == "col_with_bom"


def test_inspect_csv_malformed(tmp_path: Path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_bytes(b"\x00\xff\xfe\x00corrupt")

    result = inspect_csv_structure(bad_file)
    # Either loads or reports ERROR gracefully without crashing
    assert "load_status" in result


# -------------------------------------------------------------------------
# DT-030 / DT-031: Primary Keys & Relational Joins Tests
# -------------------------------------------------------------------------

def test_primary_key_taxonomies(synthetic_manifest_path: Path):
    manifest = load_manifest(synthetic_manifest_path)
    data_dict = build_data_dictionary({}, {}, manifest)
    key_map = build_key_map(data_dict, manifest)

    assert set(key_map["key_taxonomy"]) == KEY_STATUS_CLASSES
    for k_info in key_map["keys"].values():
        assert k_info["key_status"] in KEY_STATUS_CLASSES
        assert k_info["uniqueness_verified_in_phase_02"] is False


def test_relational_joins_spec():
    join_map = build_join_map({})
    joins = join_map["joins"]

    # Verify Task 1 critical join: route_id + seq_in_route <-> route_id + seq
    task1_train_join = next((j for j in joins if j["name"] == "task1_train_route_link"), None)
    assert task1_train_join is not None
    assert task1_train_join["left_keys"] == ["route_id", "seq_in_route"]
    assert task1_train_join["right_keys"] == ["route_id", "seq"]

    # Verify Task 2B order_ref is key, outlet_id is not allocation key
    task2b_join = next((j for j in joins if j["name"] == "task2b_outlets_reference"), None)
    assert task2b_join is not None
    assert "NOT the allocation key" in task2b_join["purpose"]


# -------------------------------------------------------------------------
# DT-032 / DT-033 / DT-034: Semantic Variable Type Classification
# -------------------------------------------------------------------------

@pytest.mark.parametrize(
    "col_name,expected_type",
    [
        ("delivery_id", "identifier"),
        ("outlet_id", "identifier"),
        ("order_ref", "identifier"),
        ("seq_in_route", "ordinal_position"),
        ("seq", "ordinal_position"),
        ("planned_travel_duration_min", "numeric_duration"),
        ("service_allowance_min", "numeric_duration"),
        ("order_weight_kg", "numeric_continuous"),
        ("order_volume_m3", "numeric_continuous"),
        ("distance_km", "numeric_continuous"),
        ("order_units", "numeric_count"),
        ("iso_week", "numeric_count"),
        ("monsoon", "binary_indicator"),
        ("is_weekend", "binary_indicator"),
        ("date", "date"),
        ("order_date", "date"),
        ("planned_arrival_time", "clock_time"),
        ("window_open_time", "clock_time"),
        ("mall_window", "time_range"),
        ("brand", "categorical"),
        ("district", "categorical"),
        ("dock_type", "categorical"),
    ],
)
def test_semantic_type_classification(col_name: str, expected_type: str):
    assert classify_column_semantic_type(col_name, "test_table.csv") == expected_type


# -------------------------------------------------------------------------
# DT-035: Availability Classes & Task 1 Leakage Prevention Tests
# -------------------------------------------------------------------------

def test_task1_actual_fields_deny_list():
    for actual_col in TASK1_TRAINING_ACTUAL_ONLY:
        avail = classify_column_availability(actual_col, "route_legs_train.csv", "training")
        assert avail == "TRAINING_ACTUAL_ONLY"


def test_target_derived_fields():
    for target_col in TASK1_TARGET_DERIVED:
        avail = classify_column_availability(target_col, "deliveries_train.csv", "training")
        assert avail == "TARGET_DERIVED"


def test_task2b_scenario_inputs():
    avail = classify_column_availability("order_ref", "task2b_peak_day_scenarios.csv", "test")
    assert avail == "TASK2B_SCENARIO_INPUT"


def test_availability_map_structure():
    avail_map = build_availability_map({})
    assert set(avail_map["taxonomy"]) == AVAILABILITY_CLASSES
    assert set(avail_map["task1_direct_feature_deny_list"]) == TASK1_TRAINING_ACTUAL_ONLY
    assert set(avail_map["task1_target_derived_fields"]) == TASK1_TARGET_DERIVED


# -------------------------------------------------------------------------
# Privacy & Structural Output Guarantees (No Row Leaks)
# -------------------------------------------------------------------------

def test_run_inventory_privacy_and_structure(
    synthetic_raw_root: Path,
    synthetic_manifest_path: Path,
    tmp_path: Path,
):
    output_dir = tmp_path / "private_reports"
    summary = run_inventory(
        raw_root=synthetic_raw_root,
        manifest_path=synthetic_manifest_path,
        output_dir=output_dir,
    )

    assert summary["status"] == "PASS"

    # Verify all 6 required JSON reports exist
    required_reports = [
        "inventory.json",
        "data_dictionary.json",
        "key_map.json",
        "join_map.json",
        "variable_types.json",
        "availability_map.json",
        "validation_summary.json",
    ]
    for r in required_reports:
        p = output_dir / r
        assert p.is_file(), f"Missing report: {r}"

        # Ensure synthetic record values (e.g. SYNTH_DEL_01, SYNTH_LEG_01) are NOT in the JSON
        content = p.read_text(encoding="utf-8")
        assert "SYNTH_DEL_01" not in content, f"Row record leaked in {r}"
        assert "SYNTH_LEG_01" not in content, f"Row record leaked in {r}"


# -------------------------------------------------------------------------
# CLI Behavior Tests
# -------------------------------------------------------------------------

def test_cli_execution_pass(
    synthetic_raw_root: Path,
    synthetic_manifest_path: Path,
    tmp_path: Path,
):
    output_dir = tmp_path / "cli_reports"
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_dataset_inventory.py"

    cmd = [
        sys.executable,
        str(script_path),
        "--raw-root",
        str(synthetic_raw_root),
        "--manifest",
        str(synthetic_manifest_path),
        "--output-dir",
        str(output_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "PHASE 02 LOCAL INVENTORY: PASS" in result.stdout
    assert "No row values were printed." in result.stdout
    assert (output_dir / "validation_summary.json").exists()


def test_cli_execution_fail_on_missing_file(
    synthetic_raw_root: Path,
    synthetic_manifest_path: Path,
    tmp_path: Path,
):
    # Delete a required file
    (synthetic_raw_root / "deliveries_train.csv").unlink()

    output_dir = tmp_path / "cli_fail_reports"
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_dataset_inventory.py"

    cmd = [
        sys.executable,
        str(script_path),
        "--raw-root",
        str(synthetic_raw_root),
        "--manifest",
        str(synthetic_manifest_path),
        "--output-dir",
        str(output_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "PHASE 02 LOCAL INVENTORY: FAIL" in result.stdout
    assert "Missing required files" in result.stdout
