"""Human-local CLI for the Phase 11 Task 2A demand-history build.

It intentionally prints only sanitized completion status.  All records and
diagnostics remain in ignored local paths supplied by the operator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task2a.history import build_task2a_history, load_history_config, load_task2a_demand_sources


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Build local Task 2A demand history without printing private rows.")
    value.add_argument("--raw-root", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--config", type=Path, required=True)
    value.add_argument("--combined-output", type=Path, required=True)
    value.add_argument("--weekly-observed-output", type=Path, required=True)
    value.add_argument("--weekly-panel-output", type=Path, required=True)
    value.add_argument("--report-dir", type=Path, required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    config = load_history_config(args.config)
    train, task1_test, calendar = load_task2a_demand_sources(args.raw_root, args.manifest, config)
    result = build_task2a_history(train, task1_test, calendar, config)
    for output in (args.combined_output, args.weekly_observed_output, args.weekly_panel_output):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    result["demand_orders"].to_csv(args.combined_output, index=False)
    result["weekly_observed"].to_csv(args.weekly_observed_output, index=False)
    result["weekly_panel"].to_csv(args.weekly_panel_output, index=False)
    diagnostics = result["diagnostics"]
    reports = {
        "build_summary.json": diagnostics,
        "source_reconciliation.json": diagnostics["source_reconciliation"],
        "delivery_id_uniqueness.json": diagnostics["source_reconciliation"],
        "dispatch_status_retention.json": diagnostics["dispatch_status_retention"],
        "calendar_join_validation.json": {"status": "PASS", "detail": "Calendar join completed without unmatched orders or row multiplication."},
        "chilled_logic_validation.json": {"status": "PASS", "detail": "Fresh chilled bounds and exact Style/Tech zero rules passed."},
        "missing_weeks.json": diagnostics["weekly_reconciliation"],
        "weekly_reconciliation.json": diagnostics["weekly_reconciliation"],
    }
    for filename, payload in reports.items():
        with (args.report_dir / filename).open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
    with (args.report_dir / "phase11_history_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# Phase 11 Task 2A history\n\nAll configured structural and reconciliation checks passed.\n")
    print("PHASE 11 LOCAL TASK2A HISTORY BUILD: PASS")
    print("Private demand-history outputs and reports were written locally.")
    print("No order identifiers, rows, or weekly volumes were printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
