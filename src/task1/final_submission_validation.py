"""Strict read-only Phase 33 validation for the frozen Task 1 CSV."""

from __future__ import annotations

import numpy as np

from src.common.submission_validation import RawCSV, ValidationReport, exact_sequence, numeric_series


EXPECTED_COLUMNS = ("delivery_id", "pred_service_min", "pred_late_prob")


def validate_final_task1(submission: RawCSV, template: RawCSV) -> ValidationReport:
    report = ValidationReport()
    report.record("DT-420", submission.path.name == "submission_task1.csv", "exact filename")
    schema_ok = submission.header == EXPECTED_COLUMNS
    report.record("DT-421", schema_ok, "exact columns")
    count_ok = len(submission.rows) == len(template.rows)
    report.record("DT-422", count_ok, "template row count", abs(len(submission.rows) - len(template.rows)))

    if "delivery_id" in submission.header and "delivery_id" in template.header:
        submitted_ids = submission.frame["delivery_id"]
        template_ids = template.frame["delivery_id"]
        order_ok = count_ok and exact_sequence(submitted_ids, template_ids)
        clean = submitted_ids.ne("") & submitted_ids.eq(submitted_ids.str.strip())
        unique = not submitted_ids.duplicated().any()
        identity_ok = count_ok and clean.all() and unique and set(submitted_ids) == set(template_ids)
    else:
        order_ok = identity_ok = False
    report.record("DT-423", order_ok, "delivery_id row order")
    report.record("DT-424", identity_ok, "delivery_id identity")

    service, service_valid = numeric_series(submission, "pred_service_min")
    late, late_valid = numeric_series(submission, "pred_late_prob")
    finite = (
        schema_ok and len(service) == len(submission.rows)
        and service_valid.all() and late_valid.all()
        and np.isfinite(service).all() and np.isfinite(late).all()
        and service.ge(0).all()
    )
    report.record("DT-425", bool(finite), "finite nonnegative predictions")
    bounded = bool(finite and late.ge(0).all() and late.le(1).all())
    report.record("DT-426", bounded, "late probability range")
    return report
