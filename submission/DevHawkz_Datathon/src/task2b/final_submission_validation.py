"""Strict raw-format and checker bridge for the frozen Task 2B CSV."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from src.common.submission_validation import RawCSV, ValidationReport, exact_sequence, sha256_file
from src.task2b.allocation_validator import validate_frozen_task2b_allocation
from src.task2b.checker_runner import OfficialCheckerInterface, CheckerRunResult, run_official_checker


EXPECTED_COLUMNS = ("scenario", "order_ref", "outlet_id", "decision", "vehicle_id", "trip_id")
IDENTITY_COLUMNS = ("scenario", "order_ref", "outlet_id")
PLACEHOLDER = re.compile(
    r"^(?:\(served/deferred\)|\(e\.g\.\s*veh014\)|\(1 or 2\)|todo|tbd|placeholder|fill here|n/a|none|null|-|<.*>|\[.*\])$",
    re.IGNORECASE,
)


def validate_final_task2b(submission: RawCSV, template: RawCSV) -> ValidationReport:
    report = ValidationReport()
    schema_ok = submission.header == EXPECTED_COLUMNS
    report.record("DT-433", submission.path.name == "submission_task2b.csv" and schema_ok, "filename/schema")
    identity_ok = False
    if schema_ok and template.header == EXPECTED_COLUMNS:
        frame, expected = submission.frame, template.frame
        keys = frame["order_ref"]
        identity_ok = (
            len(frame) == len(expected) and keys.ne("").all() and keys.eq(keys.str.strip()).all()
            and not keys.duplicated().any()
            and all(exact_sequence(frame[column], expected[column]) for column in IDENTITY_COLUMNS)
            and frame["scenario"].eq("S1").all()
        )
    report.record("DT-434", identity_ok, "order and identity-triple coverage")

    if schema_ok:
        frame = submission.frame
        answers = frame[["decision", "vehicle_id", "trip_id"]]
        placeholder_count = int(answers.apply(lambda column: column.str.strip().str.match(PLACEHOLDER)).sum().sum())
        placeholders_ok = placeholder_count == 0 and frame["decision"].ne("").all()
        format_ok = True
        for row in frame.itertuples(index=False):
            if row.decision not in ("served", "deferred"):
                format_ok = False
            elif row.decision == "served":
                format_ok &= row.vehicle_id != "" and row.vehicle_id == row.vehicle_id.strip() and row.trip_id in ("1", "2")
            else:
                format_ok &= row.vehicle_id == "" and row.trip_id == ""
    else:
        placeholder_count, placeholders_ok, format_ok = 1, False, False
    report.record("DT-435", bool(placeholders_ok), "answer placeholders", placeholder_count)
    report.record("DT-436", bool(format_ok), "decision/dependent raw-field format")
    return report


def run_independent_task2b_validator(
    submission: RawCSV,
    scenario: dict[str, pd.DataFrame],
    validation_config: dict[str, Any],
) -> dict[str, Any]:
    allocation = submission.frame.copy(deep=True)
    report = validate_frozen_task2b_allocation(
        allocation,
        scenario["orders_s1"],
        scenario["fleet_s1"],
        scenario["vehicles_ref"],
        scenario["district_travel_ref"],
        scenario["service_allowance_ref"],
        validation_config,
    )
    return {
        "status": report.overall_status,
        "checked_order_count": report.checked_order_count,
        "checked_trip_count": report.checked_trip_count,
    }


def run_final_official_checker(
    interface: OfficialCheckerInterface,
    final_submission: Path,
    independent_status: str,
) -> CheckerRunResult:
    if independent_status != "PASS":
        raise ValueError("Official checker requires independent Task 2B validator PASS.")
    before = sha256_file(final_submission)
    result = run_official_checker(interface, final_submission)
    if sha256_file(final_submission) != before:
        raise RuntimeError("Official checker modified the final Task 2B CSV.")
    return result


def require_byte_identical_staged_copy(final_submission: Path, staged_copy: Path) -> str:
    """Guard the fallback mode for checkers that cannot accept the final path directly."""
    final_hash = sha256_file(final_submission)
    if sha256_file(staged_copy) != final_hash:
        raise ValueError("Staged checker input is not byte-identical to the final submission.")
    return final_hash
