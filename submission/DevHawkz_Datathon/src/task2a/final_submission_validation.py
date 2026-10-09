"""Strict read-only Phase 33 validation for the frozen Task 2A CSV."""

from __future__ import annotations

import numpy as np

from src.common.submission_validation import RawCSV, ValidationReport, exact_sequence, numeric_series


EXPECTED_COLUMNS = ("row_id", "pred_total_volume_m3", "pred_chilled_volume_m3")


def validate_final_task2a(submission: RawCSV, template: RawCSV, test_inputs: RawCSV) -> ValidationReport:
    report = ValidationReport()
    schema_ok = submission.header == EXPECTED_COLUMNS
    report.record("DT-427", submission.path.name == "submission_task2a.csv" and schema_ok, "filename/schema")

    identity_ok = False
    brand_map: dict[str, str] = {}
    if "row_id" in submission.header and "row_id" in template.header and {"row_id", "brand"}.issubset(test_inputs.header):
        ids = submission.frame["row_id"]
        template_ids = template.frame["row_id"]
        lookup = test_inputs.frame[["row_id", "brand"]]
        lookup_ok = lookup["row_id"].ne("").all() and not lookup["row_id"].duplicated().any()
        identity_ok = (
            len(ids) == len(template_ids) and exact_sequence(ids, template_ids)
            and ids.ne("").all() and ids.eq(ids.str.strip()).all() and not ids.duplicated().any()
            and lookup_ok and set(ids) == set(lookup["row_id"])
        )
        if lookup_ok:
            brand_map = dict(zip(lookup["row_id"], lookup["brand"]))
    report.record("DT-428", identity_ok, "row_id identity/order")

    total, total_valid = numeric_series(submission, "pred_total_volume_m3")
    chilled, chilled_valid = numeric_series(submission, "pred_chilled_volume_m3")
    numeric_ok = (
        schema_ok and total_valid.all() and chilled_valid.all()
        and np.isfinite(total).all() and np.isfinite(chilled).all()
        and total.ge(0).all() and chilled.ge(0).all()
    )
    report.record("DT-429", bool(numeric_ok), "finite nonnegative predictions")

    if numeric_ok and identity_ok:
        brands = submission.frame["row_id"].map(brand_map)
        style_ok = chilled[brands.eq("Style")].eq(0).all()
        tech_ok = chilled[brands.eq("Tech")].eq(0).all()
        relation_ok = chilled.le(total).all()
        raw_chilled = submission.frame["pred_chilled_volume_m3"]
        if ((chilled.eq(0)) & raw_chilled.str.match(r"^-0(?:\.0*)?$", na=False)).any():
            report.warnings.append("Negative zero is semantically valid but noncanonical formatting.")
    else:
        style_ok = tech_ok = relation_ok = False
    report.record("DT-430", bool(style_ok), "Style chilled exact zero")
    report.record("DT-431", bool(tech_ok), "Tech chilled exact zero")
    report.record("DT-432", bool(relation_ok), "chilled less than or equal to total")
    return report
