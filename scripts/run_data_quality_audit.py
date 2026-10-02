#!/usr/bin/env python
"""WayLoom Datathon - Phase 03 local data-quality audit CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_quality import (
    audit_calendar_coverage,
    audit_categories,
    audit_complete_duplicates,
    audit_dates,
    audit_missing_values,
    audit_numeric_ranges,
    audit_order_ids,
    audit_outliers,
    audit_primary_keys,
    audit_road_coverage,
    audit_route_leg_keys,
    audit_semantic_types,
    audit_times,
    audit_train_test_compatibility,
    audit_traffic_coverage,
    audit_outlet_references,
    audit_vehicle_references,
    build_audit_summary,
    load_rules,
    load_tables_for_audit,
    write_phase03_private_reports,
)
from src.common.schema_assertions import SchemaAssertionError, collect_hard_schema_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 03 data-quality audit without printing raw rows."
    )
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rules = load_rules(args.rules)
        discovery, tables = load_tables_for_audit(args.raw_root, args.manifest)
    except Exception as exc:
        print("PHASE 03 LOCAL DATA-QUALITY AUDIT: FAIL")
        print(f"Blocking rules: 1")
        print("Blocker codes:")
        print("- DT-053.LOAD_FAILURE")
        print("Detailed private report written locally.")
        print("No raw row values were printed.")
        return 1

    sections = {
        "missingness": audit_missing_values(tables, rules),
        "duplicate_rows": audit_complete_duplicates(tables),
        "key_integrity": audit_primary_keys(tables, rules)
        + audit_order_ids(tables)
        + audit_route_leg_keys(tables),
        "type_validation": audit_semantic_types(tables),
        "date_validation": audit_dates(tables),
        "time_validation": audit_times(tables),
        "category_validation": audit_categories(tables, rules),
        "numeric_validation": audit_numeric_ranges(tables, rules),
        "outlier_review": audit_outliers(tables, rules),
        "reference_integrity": audit_outlet_references(tables, rules)
        + audit_vehicle_references(tables, rules),
        "coverage": audit_calendar_coverage(tables, rules)
        + audit_road_coverage(tables, rules)
        + audit_traffic_coverage(tables, rules),
        "train_test_compatibility": audit_train_test_compatibility(tables, rules),
    }

    hard_assertion_status = "PASS"
    try:
        hard_results = collect_hard_schema_results(
            tables=tables,
            discovery=discovery,
            rules=rules,
            feature_columns=[],
        )
    except SchemaAssertionError as exc:
        hard_assertion_status = "FAIL"
        hard_results = [
            {
                "rule_id": "DT-053.HARD_ASSERTION_FAILURE",
                "status": "BLOCKER",
                "severity": "BLOCKER",
                "table": "schema",
                "affected_count": 1,
                "message": str(exc),
                "details": {},
            }
        ]
    sections["hard_schema_assertions"] = hard_results

    summary = build_audit_summary(sections)
    summary["hard_schema_assertions"] = hard_assertion_status

    write_phase03_private_reports(args.output_dir, sections, summary)

    has_blockers = summary["blocker_count"] > 0
    if not has_blockers:
        print("PHASE 03 LOCAL DATA-QUALITY AUDIT: PASS")
        print(f"Hard schema assertions: {hard_assertion_status}")
        print(f"Blocking rules: {summary['blocker_count']}")
        print(f"Warnings present: {'YES' if summary['warning_count'] else 'NO'}")
        print("Detailed report written to local private report directory.")
        print("No raw row values were printed.")
        return 0

    print("PHASE 03 LOCAL DATA-QUALITY AUDIT: FAIL")
    print(f"Hard schema assertions: {hard_assertion_status}")
    print(f"Blocking rules: {summary['blocker_count']}")
    print("Blocker codes:")
    for code in summary["blocker_rule_codes"]:
        print(f"- {code}")
    print("Detailed private report written locally.")
    print("No raw row values were printed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
