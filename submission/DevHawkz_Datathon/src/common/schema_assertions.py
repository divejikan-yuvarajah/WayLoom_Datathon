"""Hard schema assertions for WayLoom Phase 03.

These checks enforce non-negotiable dataset contracts.
Warnings remain in the audit layer and do not raise automatically.
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from src.common.data_quality import (
    BLOCKER,
    PASS,
    audit_calendar_coverage,
    audit_categories,
    audit_dates,
    audit_numeric_ranges,
    audit_outlet_references,
    audit_primary_keys,
    audit_route_leg_keys,
    audit_times,
    audit_vehicle_references,
    make_result,
)


class SchemaAssertionError(RuntimeError):
    """Raised when a hard schema assertion fails."""


def _raise_if_blocker(results: list[dict]) -> None:
    for result in results:
        if result["status"] == BLOCKER:
            raise SchemaAssertionError(
                f"{result['rule_id']} failed for {result['table']}: {result['message']}"
            )


def assert_required_files(discovery: dict) -> dict:
    missing = discovery.get("missing_required", [])
    duplicate = discovery.get("duplicate_required", {})
    if missing:
        raise SchemaAssertionError(f"Missing required files: {', '.join(sorted(missing))}")
    if duplicate:
        raise SchemaAssertionError(
            f"Duplicate required files: {', '.join(sorted(duplicate.keys()))}"
        )
    return make_result(
        rule_id="DT-053.REQUIRED_FILES",
        status=PASS,
        table="manifest",
        message="All required files are present exactly once",
    )


def assert_required_columns(tables: dict[str, pd.DataFrame], rules: dict) -> dict:
    required_columns = rules.get("required_columns", {})
    for table_name, columns in required_columns.items():
        if table_name not in tables:
            continue
        missing = [column for column in columns if column not in tables[table_name].columns]
        if missing:
            raise SchemaAssertionError(
                f"{table_name} missing required columns: {', '.join(missing)}"
            )
    return make_result(
        rule_id="DT-053.REQUIRED_COLUMNS",
        status=PASS,
        table="schema",
        message="All configured required columns are present",
    )


def assert_official_counts(tables: dict[str, pd.DataFrame], rules: dict) -> dict:
    expected_outlets = int(rules.get("official_counts", {}).get("outlets", 120))
    expected_vehicles = int(rules.get("official_counts", {}).get("vehicles", 60))

    if "outlets.csv" in tables:
        observed = int(tables["outlets.csv"]["outlet_id"].nunique(dropna=True))
        if observed != expected_outlets:
            raise SchemaAssertionError(
                f"outlets.csv expected {expected_outlets} unique outlets but found {observed}"
            )
    if "vehicles.csv" in tables:
        observed = int(tables["vehicles.csv"]["vehicle_id"].nunique(dropna=True))
        if observed != expected_vehicles:
            raise SchemaAssertionError(
                f"vehicles.csv expected {expected_vehicles} unique vehicles but found {observed}"
            )

    return make_result(
        rule_id="DT-053.OFFICIAL_COUNTS",
        status=PASS,
        table="reference",
        message="Official outlet and vehicle counts satisfied",
    )


def assert_task1_leakage_guard(
    feature_columns: Iterable[str],
    deny_list: Iterable[str],
) -> dict:
    feature_set = set(feature_columns)
    deny = set(deny_list)
    violating = sorted(feature_set & deny)
    if violating:
        raise SchemaAssertionError(
            f"Task 1 feature leakage guard failed: {', '.join(violating)}"
        )
    return make_result(
        rule_id="DT-053.TASK1_LEAKAGE_GUARD",
        status=PASS,
        table="task1_features",
        message="Task 1 direct feature list excludes actual and target-derived columns",
    )


def collect_hard_schema_results(
    tables: dict[str, pd.DataFrame],
    discovery: dict,
    rules: dict,
    feature_columns: Optional[Iterable[str]] = None,
) -> list[dict]:
    results: list[dict] = []
    results.append(assert_required_files(discovery))
    results.append(assert_required_columns(tables, rules))
    _raise_if_blocker(audit_primary_keys(tables, rules))
    results.extend(audit_primary_keys(tables, rules))
    _raise_if_blocker(audit_route_leg_keys(tables))
    results.extend(audit_route_leg_keys(tables))
    _raise_if_blocker(audit_outlet_references(tables, rules))
    results.extend(audit_outlet_references(tables, rules))
    _raise_if_blocker(audit_vehicle_references(tables, rules))
    results.extend(audit_vehicle_references(tables, rules))
    _raise_if_blocker(audit_categories(tables, rules))
    results.extend(audit_categories(tables, rules))
    _raise_if_blocker(audit_numeric_ranges(tables, rules))
    results.extend(audit_numeric_ranges(tables, rules))
    _raise_if_blocker(audit_dates(tables))
    results.extend(audit_dates(tables))
    _raise_if_blocker(audit_times(tables))
    results.extend(audit_times(tables))
    _raise_if_blocker(audit_calendar_coverage(tables, rules))
    results.extend(audit_calendar_coverage(tables, rules))
    results.append(assert_official_counts(tables, rules))
    if feature_columns is None:
        feature_columns = []
    results.append(
        assert_task1_leakage_guard(
            feature_columns,
            rules.get("task1_direct_feature_deny_list", []),
        )
    )
    return results
