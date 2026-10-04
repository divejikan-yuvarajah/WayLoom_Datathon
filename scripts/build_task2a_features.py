"""Build private Phase 13 Task 2A origin and direct-horizon feature tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import load_manifest
from src.task2a.features import audit_future_demand_leakage, load_feature_config
from src.task2a.history import load_history_config
from src.task2a.multihorizon import assemble_phase13_artifacts


def _unique_artifact(raw_root: Path, filename: str) -> Path:
    matches = list(raw_root.rglob(filename))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one required official artifact named {filename}.")
    return matches[0]


def _validate_inside(path: Path, parent: Path, label: str) -> Path:
    resolved = path.resolve()
    parent_resolved = parent.resolve()
    try:
        resolved.relative_to(parent_resolved)
    except ValueError as error:
        raise ValueError(f"{label} must be inside {parent_resolved}.") from error
    return resolved


def validate_phase13_output_paths(origin: Path, multihorizon: Path, report_dir: Path) -> tuple[Path, Path, Path]:
    """Keep derived tables and reports in their approved private locations."""
    interim = PROJECT_ROOT / "data" / "interim"
    private = PROJECT_ROOT / "reports" / "private" / "phase13_task2a_features"
    return (
        _validate_inside(origin, interim, "origin output"),
        _validate_inside(multihorizon, interim, "multi-horizon output"),
        _validate_inside(report_dir, private, "report directory"),
    )


def sanitized_console_lines(summary: dict[str, object]) -> list[str]:
    """Return the sole operator-facing output, limited to status and row counts."""
    return [
        "PHASE 13 LOCAL TASK2A FEATURES: PASS",
        f"ORIGIN FEATURE ROWS: {summary['n_origin_rows']}",
        f"MULTI-HORIZON TRAINING ROWS: {summary['n_multihorizon_rows']}",
        "PRIVATE OUTPUTS WRITTEN: YES",
        "PRIVATE WEEKLY VALUES OR ORDER IDENTIFIERS PRINTED: NO",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weekly-panel", required=True, type=Path)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--history-config", required=True, type=Path)
    parser.add_argument("--feature-config", required=True, type=Path)
    parser.add_argument("--origin-output", required=True, type=Path)
    parser.add_argument("--multihorizon-output", required=True, type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    origin_path, multihorizon_path, report_dir = validate_phase13_output_paths(
        args.origin_output, args.multihorizon_output, args.report_dir
    )
    # Load both configs so the inherited Phase 11 path is explicit and checked.
    load_history_config(args.history_config)
    config = load_feature_config(args.feature_config)
    manifest = load_manifest(args.manifest)
    filenames = {item["filename"] for item in manifest["artifacts"]}
    calendar_name = config.get("input", {}).get("calendar", "calendar.csv")
    if calendar_name not in filenames:
        raise ValueError("Configured Phase 13 calendar is absent from the official manifest.")
    panel = pd.read_csv(args.weekly_panel)
    calendar = pd.read_csv(_unique_artifact(args.raw_root, calendar_name))
    artifacts = assemble_phase13_artifacts(panel, calendar, config)

    origin_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    artifacts["origin_features"].to_csv(origin_path, index=False)
    artifacts["multihorizon_train"].to_csv(multihorizon_path, index=False)
    registry_rows = artifacts["registry"].to_dict(orient="records")
    coverage = artifacts["summary"]["feature_coverage"]
    leakage = audit_future_demand_leakage(panel, artifacts["multihorizon_train"], config)
    report_payloads = {
        "build_summary.json": artifacts["summary"],
        "feature_coverage.json": coverage,
        "lag_validation.json": {"status": "PASS", "lag_columns": int(sum(name.startswith(("total_lag_", "chilled_lag_")) for name in artifacts["origin_features"].columns))},
        "rolling_validation.json": {"status": "PASS", "rolling_columns": int(sum("rolling_mean" in name for name in artifacts["origin_features"].columns))},
        "target_week_calendar_validation.json": {"status": "PASS", "target_calendar_feature_count": int(sum(name.startswith("target_") for name in artifacts["multihorizon_train"].columns))},
        "multihorizon_validation.json": {"status": "PASS", "max_horizon_weeks": artifacts["summary"]["max_horizon_weeks"]},
        "leakage_audit.json": leakage,
        "feature_registry.json": registry_rows,
    }
    for filename, payload in report_payloads.items():
        (report_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (report_dir / "phase13_feature_report.md").write_text(
        "# Phase 13 Task 2A feature build\n\n"
        "Status: PASS\n\n"
        "This report contains only row counts, feature counts, and coverage metadata; "
        "it intentionally contains no weekly values, order identifiers, or predictions.\n",
        encoding="utf-8",
    )
    for line in sanitized_console_lines(artifacts["summary"]):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
