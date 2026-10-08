"""Human-local read-only Phase 33 gate for the three frozen submissions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest  # noqa: E402
from src.common.submission_validation import hash_snapshot, read_strict_csv, sha256_file  # noqa: E402
from src.task1.final_submission_validation import validate_final_task1  # noqa: E402
from src.task2a.final_submission_validation import validate_final_task2a  # noqa: E402
from src.task2b.checker_runner import (  # noqa: E402
    discover_official_checker_interface,
    locate_official_checker,
)
from src.task2b.final_submission_validation import (  # noqa: E402
    run_final_official_checker,
    run_independent_task2b_validator,
    validate_final_task2b,
)
from src.task2b.scenario import build_s1_scenario, load_scenario_config  # noqa: E402


TASK_LABELS = {
    "DT-420": "FILENAME", "DT-421": "COLUMNS", "DT-422": "ROW COUNT",
    "DT-423": "ROW ORDER", "DT-424": "IDS UNCHANGED", "DT-425": "PREDICTIONS FINITE",
    "DT-426": "PROBABILITIES [0,1]", "DT-427": "FILENAME", "DT-428": "ROW IDS UNCHANGED",
    "DT-429": "PREDICTIONS NONNEGATIVE", "DT-430": "STYLE CHILLED = 0",
    "DT-431": "TECH CHILLED = 0", "DT-432": "CHILLED <= TOTAL",
    "DT-433": "FILENAME", "DT-434": "ALL ORDERS PRESENT",
    "DT-435": "PLACEHOLDERS REMOVED", "DT-436": "DECISION/FIELD FORMAT",
    "DT-437": "OFFICIAL check_allocation.py",
}


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dataset-manifest", type=Path, required=True)
    parser.add_argument("--submission-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    return parser.parse_args()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="phase33_", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _require_config(config: dict[str, Any], args: argparse.Namespace) -> None:
    expected_names = {
        "task1": "submission_task1.csv",
        "task2a": "submission_task2a.csv",
        "task2b": "submission_task2b.csv",
    }
    if config.get("version") != 1 or config.get("filenames") != expected_names:
        raise ValueError("Phase 33 filename/config contract is invalid.")
    if config.get("integrity") != {"read_only": True, "pre_post_sha256_equal": True}:
        raise ValueError("Phase 33 read-only guard cannot be weakened.")
    privacy = config.get("privacy", {})
    if privacy.get("print_ids") is not False or privacy.get("print_rows") is not False:
        raise ValueError("Phase 33 privacy controls cannot be weakened.")
    expected_report = (ROOT / privacy.get("report_dir", "")).resolve()
    if args.report_dir.resolve() != expected_report or not args.report_dir.resolve().is_relative_to((ROOT / "reports/private").resolve()):
        raise ValueError("Phase 33 reports must use the configured private directory.")


def _load_official(found: dict[str, Any], filename: str):
    entry = found.get(filename, {})
    path = entry.get("path")
    if not path:
        raise ValueError(f"Official artifact is unavailable or duplicated: {filename}")
    return read_strict_csv(Path(path))


def _scenario(found: dict[str, Any], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
    scenario_config = load_scenario_config(str(ROOT / config["task2b"]["scenario_config"]))
    keys = scenario_config["files"]
    dtypes = {
        "orders": {"order_ref": "string", "outlet_id": "string", "order_weight_kg": "string", "order_volume_m3": "string"},
        "fleet": {"vehicle_id": "string"},
        "vehicles": {"vehicle_id": "string", "weight_cap_kg": "string", "volume_cap_m3": "string"},
        "district_travel": {"depot_to_district_freeflow_min": "string", "inter_stop_freeflow_min": "string"},
        "service_allowance": {"service_allowance_min": "string"},
    }

    def load(key: str) -> pd.DataFrame:
        return pd.read_csv(found[keys[key]]["path"], dtype=dtypes.get(key))

    return build_s1_scenario(
        load("orders"), load("fleet"), load("vehicles"),
        load("district_travel"), load("service_allowance"), scenario_config,
    )


def main() -> int:
    args = _args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    _require_config(config, args)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    if args.submission_dir.resolve() != (ROOT / config["submission_dir"]).resolve():
        raise ValueError("Submission directory differs from the Phase 33 configuration.")
    paths = {name: args.submission_dir / filename for name, filename in config["filenames"].items()}
    pre_hashes = hash_snapshot(paths.values())

    manifest = load_manifest(args.dataset_manifest)
    raw_root = ROOT / config["raw_root"]
    discovered = discover_dataset_files(raw_root, manifest)
    if discovered.get("discovery_status") != "PASS":
        raise ValueError("Required official artifacts are missing or duplicated.")
    found = discovered["found_artifacts"]

    submissions = {name: read_strict_csv(path) for name, path in paths.items()}
    templates = {name: _load_official(found, filename) for name, filename in config["filenames"].items()}
    task1 = validate_final_task1(submissions["task1"], templates["task1"])
    task2a = validate_final_task2a(
        submissions["task2a"], templates["task2a"], _load_official(found, "task2a_test_inputs.csv")
    )
    task2b = validate_final_task2b(submissions["task2b"], templates["task2b"])

    validation_config = yaml.safe_load((ROOT / config["task2b"]["validation_config"]).read_text(encoding="utf-8"))
    independent = {"status": "NOT_RUN"}
    checker_status = "NOT_RUN"
    checker_evidence: dict[str, Any] = {"status": "NOT_RUN", "semantics": "feasibility_only"}
    structural_pass = task1.status == task2a.status == task2b.status == "PASS"
    if structural_pass:
        try:
            independent = run_independent_task2b_validator(
                submissions["task2b"], _scenario(found, config), validation_config
            )
        except Exception as exc:  # fail closed without printing row-level diagnostics
            independent = {"status": "FAIL", "error_type": type(exc).__name__}
    if independent.get("status") == "PASS":
        try:
            checker_config = validation_config["official_checker"]
            checker_path = locate_official_checker(ROOT, raw_root, manifest, checker_config["repository_path"])
            interface = discover_official_checker_interface(checker_path, validation_config)
            result = run_final_official_checker(interface, paths["task2b"], independent["status"])
            checker_status = result.status
            (args.report_dir / "checker_stdout.txt").write_text(result.stdout, encoding="utf-8")
            (args.report_dir / "checker_stderr.txt").write_text(result.stderr, encoding="utf-8")
            checker_evidence = {
                "status": result.status,
                "checker_filename": Path(result.command[1]).name,
                "checker_sha256": result.checker_sha256,
                "invocation_mode": result.invocation_mode,
                "input_mode": "direct_final_file",
                "working_directory": result.working_directory,
                "final_submission_sha256": result.candidate_sha256,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
                "pass_detected": result.pass_detected,
                "stdout_sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(),
                "stderr_sha256": hashlib.sha256(result.stderr.encode("utf-8")).hexdigest(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "semantics": "feasibility_only",
            }
        except Exception as exc:  # missing/crashed/unsafe checker is a gate failure
            checker_status = "FAIL"
            checker_evidence = {
                "status": "FAIL", "error_type": type(exc).__name__,
                "semantics": "feasibility_only",
            }
    task2b.record("DT-437", checker_status == "PASS", "official checker")

    post_hashes = hash_snapshot(paths.values())
    hashes_unchanged = pre_hashes == post_hashes
    all_pass = task1.status == task2a.status == task2b.status == "PASS" and independent.get("status") == "PASS" and hashes_unchanged
    timestamp = datetime.now(timezone.utc).isoformat()
    _atomic_json(args.report_dir / "task1_validation.json", task1.as_dict())
    _atomic_json(args.report_dir / "task2a_validation.json", task2a.as_dict())
    _atomic_json(args.report_dir / "task2b_validation.json", {**task2b.as_dict(), "independent_validator": independent})
    _atomic_json(args.report_dir / "official_checker_evidence.json", checker_evidence)
    _atomic_json(args.report_dir / "final_submission_hashes.json", {"pre": pre_hashes, "post": post_hashes, "unchanged": hashes_unchanged})
    _atomic_json(args.report_dir / "run_manifest.json", {
        "phase": 33, "timestamp": timestamp, "read_only": True,
        "template_paths": {name: str(templates[name].path.resolve().relative_to(ROOT)) for name in templates},
        "template_sha256": {name: sha256_file(templates[name].path) for name in templates},
        "private_identifiers_printed": False,
    })
    _atomic_json(args.report_dir / "phase33_gate.json", {
        "phase": 33, "status": "PASS" if all_pass else "FAIL",
        **task1.checks, **task2a.checks, **task2b.checks,
        "task1_hash_unchanged": pre_hashes.get(config["filenames"]["task1"]) == post_hashes.get(config["filenames"]["task1"]),
        "task2a_hash_unchanged": pre_hashes.get(config["filenames"]["task2a"]) == post_hashes.get(config["filenames"]["task2a"]),
        "task2b_hash_unchanged": pre_hashes.get(config["filenames"]["task2b"]) == post_hashes.get(config["filenames"]["task2b"]),
        "independent_task2b_validator": independent.get("status"),
        "official_checker": checker_status,
        "official_checker_semantics": "feasibility_only",
    })

    print("WAYLOOM - PHASE 33 FINAL SUBMISSION VALIDATION")
    for section, tasks in (("TASK1", task1.checks), ("TASK2A", task2a.checks), ("TASK2B", task2b.checks)):
        print(f"\n{section}")
        for task, status in tasks.items():
            print(f"{task} {TASK_LABELS[task]:<34}: {status}")
    failures = task1.failures + task2a.failures + task2b.failures
    for failure in failures:
        print(
            f"FAILURE {failure['task']} {failure['check']}: "
            f"COUNT={failure['failure_count']}"
        )
    print(f"INDEPENDENT TASK2B VALIDATOR             : {independent.get('status')}")
    print("OFFICIAL CHECKER SEMANTICS               : FEASIBILITY ONLY")
    print("\nREAD-ONLY HASH GUARD")
    for filename in config["filenames"].values():
        print(f"{filename:<40}: {'UNCHANGED' if pre_hashes.get(filename) == post_hashes.get(filename) else 'CHANGED'}")
    print(f"\nPHASE 33                                 : {'PASS' if all_pass else 'FAIL'}")
    print(f"READY FOR PHASE 34                       : {'YES' if all_pass else 'NO'}")
    print("PRIVATE IDENTIFIERS PRINTED              : NO")
    return 0 if all_pass else 1


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as exc:  # sanitized: never print row-level exception details
        print("WAYLOOM - PHASE 33 FINAL SUBMISSION VALIDATION")
        print("PHASE 33                                 : FAIL")
        print(f"AGGREGATE ERROR TYPE                      : {type(exc).__name__}")
        print("PRIVATE IDENTIFIERS PRINTED              : NO")
        exit_code = 1
    raise SystemExit(exit_code)
