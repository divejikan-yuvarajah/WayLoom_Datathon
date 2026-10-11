"""Official-template Task 2B mapping, validation, and atomic export."""

from __future__ import annotations

import os
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.task2b.artifact_integrity import ALLOCATION_COLUMNS, sha256_file


class Task2BSubmissionError(ValueError):
    """The Phase 24 output contract is incomplete or unsafe."""


OFFICIAL_COLUMNS = tuple(ALLOCATION_COLUMNS)
IDENTITY_COLUMNS = ("scenario", "order_ref", "outlet_id")
ANSWER_COLUMNS = ("decision", "vehicle_id", "trip_id")
PLACEHOLDER_TOKENS = frozenset({
    "(served/deferred)",
    "(e.g. veh014)",
    "(1 or 2)",
    "placeholder",
    "tbd",
    "todo",
    "n/a",
    "-",
})


def _blank(value: object) -> bool:
    return pd.isna(value) or (isinstance(value, str) and value.strip() == "")


def _key(value: object) -> str:
    return str(value)


def _placeholder(value: object) -> bool:
    return not _blank(value) and str(value).strip().lower() in PLACEHOLDER_TOKENS


def _trip_id(value: object) -> int | None:
    if _blank(value) or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite() or number != number.to_integral_value():
        return None
    result = int(number)
    return result if result in (1, 2) else None


def validate_output_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict) or config.get("version") != 1:
        raise Task2BSubmissionError("Task 2B output configuration is invalid.")
    output = config.get("output", {})
    expected_output = {
        "filename": "submission_task2b.csv",
        "path": "outputs/submission_task2b.csv",
        "official_template_filename": "submission_task2b.csv",
        "exact_columns": list(OFFICIAL_COLUMNS),
    }
    if any(output.get(name) != value for name, value in expected_output.items()):
        raise Task2BSubmissionError("Official Task 2B output contract changed.")
    if output.get("preserve_template_row_order") is not True or output.get("write_index") is not False:
        raise Task2BSubmissionError("Template order preservation and index suppression are mandatory.")
    if output.get("refuse_overwrite_without_force") is not True:
        raise Task2BSubmissionError("Silent final-output overwrite cannot be enabled.")
    phase22 = config.get("phase22", {})
    if phase22.get("allocation_path") != "data/interim/task2b_final_allocation.csv":
        raise Task2BSubmissionError("Canonical Phase 22 allocation path changed.")
    if phase22.get("freeze_manifest_path") != "reports/private/phase22_task2b_optimizer/freeze_manifest.json":
        raise Task2BSubmissionError("Canonical Phase 22 freeze manifest path changed.")
    phase23 = config.get("phase23", {})
    if phase23.get("require_own_validator_pass") is not True or phase23.get("require_official_checker_pass") is not True:
        raise Task2BSubmissionError("Phase 23 PASS requirements cannot be weakened.")
    policy = config.get("policy", {})
    if policy.get("fresh_budget_limit") != 270 or policy.get("style_tech_budget_limit") != 480:
        raise Task2BSubmissionError("Official Task 2B time limits changed.")
    if policy.get("include_return_leg") is not False:
        raise Task2BSubmissionError("Task 2B policy must exclude the return journey.")
    if policy.get("target_max_words") != 550 or policy.get("warn_above_words") != 650:
        raise Task2BSubmissionError("Phase 24 policy length guard changed.")


def _validate_keys(frame: pd.DataFrame, label: str) -> dict[str, dict[str, Any]]:
    if "order_ref" not in frame:
        raise Task2BSubmissionError(f"{label} lacks order_ref.")
    if frame["order_ref"].map(_blank).any() or frame["order_ref"].map(_key).duplicated().any():
        raise Task2BSubmissionError(f"{label} order_ref must be nonblank and unique.")
    return {_key(row["order_ref"]): row for row in frame.to_dict("records")}


def _require_exact_key_set(left: dict[str, Any], right: dict[str, Any], message: str) -> None:
    if set(left) != set(right):
        raise Task2BSubmissionError(message)


def _assignment(row: dict[str, Any]) -> tuple[str, str, int | None]:
    decision = row.get("decision")
    if decision not in ("served", "deferred"):
        raise Task2BSubmissionError("Decision must be exactly served or deferred.")
    vehicle = "" if _blank(row.get("vehicle_id")) else str(row.get("vehicle_id"))
    trip = _trip_id(row.get("trip_id"))
    if decision == "served":
        if not vehicle or _placeholder(vehicle) or trip is None:
            raise Task2BSubmissionError("Served row has an invalid vehicle or trip assignment.")
    elif vehicle or not _blank(row.get("trip_id")):
        raise Task2BSubmissionError("Deferred row must have blank vehicle and trip fields.")
    return decision, vehicle, trip


def build_task2b_submission(
    template: pd.DataFrame,
    frozen_allocation: pd.DataFrame,
    canonical_orders: pd.DataFrame,
) -> pd.DataFrame:
    """Fill only answer columns while preserving official template identities and order."""
    if tuple(template.columns) != OFFICIAL_COLUMNS:
        raise Task2BSubmissionError("Official template columns or column order are unexpected.")
    missing = set(OFFICIAL_COLUMNS).difference(frozen_allocation.columns)
    if missing:
        raise Task2BSubmissionError("Frozen allocation is missing official columns.")
    if set(IDENTITY_COLUMNS).difference(canonical_orders.columns):
        raise Task2BSubmissionError("Canonical order source lacks identity columns.")

    template_rows = _validate_keys(template, "Official template")
    allocation_rows = _validate_keys(frozen_allocation, "Frozen allocation")
    source_rows = _validate_keys(canonical_orders, "Canonical source")
    _require_exact_key_set(template_rows, allocation_rows, "Template and frozen allocation order sets differ.")
    _require_exact_key_set(template_rows, source_rows, "Template and canonical source order sets differ.")

    result = template.loc[:, OFFICIAL_COLUMNS].copy(deep=True).reset_index(drop=True)
    for index, template_row in enumerate(template.to_dict("records")):
        key = _key(template_row["order_ref"])
        allocation_row, source_row = allocation_rows[key], source_rows[key]
        for column in IDENTITY_COLUMNS:
            expected = _key(template_row[column])
            if _key(source_row[column]) != expected or _key(allocation_row[column]) != expected:
                raise Task2BSubmissionError(f"Template identity mismatch: {column}.")
        decision, vehicle, trip = _assignment(allocation_row)
        result.at[index, "decision"] = decision
        result.at[index, "vehicle_id"] = vehicle
        result.at[index, "trip_id"] = str(trip) if trip is not None else ""
    return result


def validate_task2b_submission(
    submission: pd.DataFrame,
    template: pd.DataFrame,
    frozen_allocation: pd.DataFrame,
    canonical_orders: pd.DataFrame,
    *,
    known_vehicle_ids: Iterable[object] | None = None,
    phase23_candidate: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Fail closed on schema, identity, placeholders, and allocation parity."""
    if tuple(submission.columns) != OFFICIAL_COLUMNS or tuple(template.columns) != OFFICIAL_COLUMNS:
        raise Task2BSubmissionError("Submission must contain the exact six official columns in order.")
    if any(str(column).startswith("Unnamed:") for column in submission.columns):
        raise Task2BSubmissionError("Submission contains an accidental CSV index column.")
    if len(submission) != len(template):
        raise Task2BSubmissionError("Submission row count differs from the official template.")
    for column in IDENTITY_COLUMNS:
        if submission[column].map(_key).tolist() != template[column].map(_key).tolist():
            raise Task2BSubmissionError(f"Submission did not preserve template {column} row-by-row.")
    if not submission["scenario"].eq("S1").all():
        raise Task2BSubmissionError("Every Task 2B scenario must be exactly S1.")

    submission_rows = _validate_keys(submission, "Submission")
    template_rows = _validate_keys(template, "Official template")
    allocation_rows = _validate_keys(frozen_allocation, "Frozen allocation")
    source_rows = _validate_keys(canonical_orders, "Canonical source")
    _require_exact_key_set(submission_rows, template_rows, "Submission order set differs from template.")
    _require_exact_key_set(submission_rows, allocation_rows, "Submission order set differs from frozen allocation.")
    _require_exact_key_set(submission_rows, source_rows, "Submission order set differs from canonical source.")

    known = None if known_vehicle_ids is None else {str(value) for value in known_vehicle_ids}
    served_count = deferred_count = 0
    for key, row in submission_rows.items():
        template_row, allocation_row, source_row = template_rows[key], allocation_rows[key], source_rows[key]
        for column in IDENTITY_COLUMNS:
            expected = _key(template_row[column])
            if _key(row[column]) != expected or _key(source_row[column]) != expected or _key(allocation_row[column]) != expected:
                raise Task2BSubmissionError(f"Identity parity failed: {column}.")
        if any(_placeholder(row[column]) for column in ANSWER_COLUMNS):
            raise Task2BSubmissionError("Submission contains an answer-field placeholder.")
        assignment = _assignment(row)
        if assignment != _assignment(allocation_row):
            raise Task2BSubmissionError("Submission answer fields differ from the frozen allocation.")
        if assignment[0] == "served":
            served_count += 1
            if known is not None and assignment[1] not in known:
                raise Task2BSubmissionError("Served row uses an unknown vehicle.")
        else:
            deferred_count += 1

    checker_parity = "NOT_AVAILABLE"
    if phase23_candidate is not None:
        candidate_rows = _validate_keys(phase23_candidate, "Phase 23 checker candidate")
        _require_exact_key_set(submission_rows, candidate_rows, "Phase 23 candidate order set differs.")
        if tuple(phase23_candidate.columns) != OFFICIAL_COLUMNS:
            raise Task2BSubmissionError("Phase 23 checker candidate schema differs from the official schema.")
        if any(_assignment(submission_rows[key]) != _assignment(candidate_rows[key]) for key in submission_rows):
            raise Task2BSubmissionError("Submission differs from the Phase 23 checker candidate.")
        checker_parity = "PASS"

    return {
        "status": "PASS",
        "row_count": int(len(submission)),
        "column_list": list(OFFICIAL_COLUMNS),
        "identity_preservation": "PASS",
        "placeholder_audit": "PASS",
        "allocation_parity": "PASS",
        "phase23_checker_candidate_parity": checker_parity,
        "served_order_count": served_count,
        "deferred_order_count": deferred_count,
    }


def write_task2b_submission_atomic(
    path: Path,
    submission: pd.DataFrame,
    template: pd.DataFrame,
    frozen_allocation: pd.DataFrame,
    canonical_orders: pd.DataFrame,
    *,
    source_allocation_sha256: str,
    known_vehicle_ids: Iterable[object] | None = None,
    phase23_candidate: pd.DataFrame | None = None,
    force: bool = False,
    existing_export_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = Path(path)
    if path.name != "submission_task2b.csv":
        raise Task2BSubmissionError("Final filename must be submission_task2b.csv.")
    if path.exists():
        if not force:
            raise Task2BSubmissionError("Final Task 2B output already exists; use --force explicitly.")
        if (not existing_export_manifest
                or existing_export_manifest.get("phase22_frozen_allocation_sha256") != source_allocation_sha256):
            raise Task2BSubmissionError("Forced overwrite lacks a matching prior export manifest.")

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="task2b_submission_", suffix=".csv", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            submission.loc[:, OFFICIAL_COLUMNS].to_csv(stream, index=False, na_rep="")
        read_back = pd.read_csv(temporary, dtype="string", keep_default_na=False)
        report = validate_task2b_submission(
            read_back,
            template,
            frozen_allocation,
            canonical_orders,
            known_vehicle_ids=known_vehicle_ids,
            phase23_candidate=phase23_candidate,
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    report["submission_task2b_sha256"] = sha256_file(path)
    return report
