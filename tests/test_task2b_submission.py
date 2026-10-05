"""Synthetic-only Phase 24 official-template export tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.task2b.artifact_integrity import sha256_file
from src.task2b.submission import (
    OFFICIAL_COLUMNS,
    Task2BSubmissionError,
    build_task2b_submission,
    validate_task2b_submission,
    write_task2b_submission_atomic,
)


def _case():
    template = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared", "decision": "(served/deferred)", "vehicle_id": "(e.g. VEH014)", "trip_id": "(1 or 2)"},
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared", "decision": "(served/deferred)", "vehicle_id": "(e.g. VEH014)", "trip_id": "(1 or 2)"},
        {"scenario": "S1", "order_ref": "o3", "outlet_id": "other", "decision": "(served/deferred)", "vehicle_id": "(e.g. VEH014)", "trip_id": "(1 or 2)"},
    ], columns=OFFICIAL_COLUMNS)
    allocation = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared", "decision": "served", "vehicle_id": "v1", "trip_id": 1, "diagnostic": "ignored"},
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared", "decision": "deferred", "vehicle_id": "", "trip_id": "", "diagnostic": "ignored"},
        {"scenario": "S1", "order_ref": "o3", "outlet_id": "other", "decision": "served", "vehicle_id": "v2", "trip_id": 2, "diagnostic": "ignored"},
    ])
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": "o3", "outlet_id": "other"},
        {"scenario": "S1", "order_ref": "o2", "outlet_id": "shared"},
        {"scenario": "S1", "order_ref": "o1", "outlet_id": "shared"},
    ])
    return template, allocation, orders


def test_official_template_controls_schema_identity_and_row_order():
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    assert tuple(output.columns) == OFFICIAL_COLUMNS
    assert output.order_ref.tolist() == ["o2", "o1", "o3"]
    assert output.outlet_id.tolist() == template.outlet_id.tolist()
    assert output.scenario.tolist() == template.scenario.tolist()
    assert output.decision.tolist() == ["deferred", "served", "served"]
    assert output.loc[0, "vehicle_id"] == "" and output.loc[0, "trip_id"] == ""
    assert "diagnostic" not in output
    assert validate_task2b_submission(
        output, template, allocation, orders, known_vehicle_ids=["v1", "v2"]
    )["status"] == "PASS"


@pytest.mark.parametrize("target", ["template", "allocation", "orders"])
def test_missing_order_fails_exact_set_contract(target):
    template, allocation, orders = _case()
    values = {"template": template, "allocation": allocation, "orders": orders}
    values[target] = values[target].iloc[:-1].copy()
    with pytest.raises(Task2BSubmissionError, match="order sets differ"):
        build_task2b_submission(values["template"], values["allocation"], values["orders"])


def test_extra_allocation_row_and_duplicate_template_key_fail():
    template, allocation, orders = _case()
    extra = allocation.iloc[[0]].copy()
    extra.loc[:, "order_ref"] = "extra"
    with pytest.raises(Task2BSubmissionError, match="order sets differ"):
        build_task2b_submission(template, pd.concat([allocation, extra]), orders)
    duplicate = pd.concat([template, template.iloc[[0]]], ignore_index=True)
    with pytest.raises(Task2BSubmissionError, match="nonblank and unique"):
        build_task2b_submission(duplicate, allocation, orders)


@pytest.mark.parametrize(("frame", "column"), [
    ("allocation", "scenario"),
    ("allocation", "outlet_id"),
    ("orders", "scenario"),
    ("orders", "outlet_id"),
])
def test_identity_mismatch_fails_without_rewriting_template(frame, column):
    template, allocation, orders = _case()
    target = allocation if frame == "allocation" else orders
    target.loc[target.order_ref.eq("o1"), column] = "wrong"
    with pytest.raises(Task2BSubmissionError, match="identity mismatch"):
        build_task2b_submission(template, allocation, orders)


@pytest.mark.parametrize(("column", "value"), [
    ("decision", "(served/deferred)"),
    ("decision", "placeholder"),
    ("decision", "TBD"),
    ("decision", "TODO"),
    ("decision", "N/A"),
    ("decision", "-"),
    ("decision", "invalid"),
    ("vehicle_id", "(e.g. VEH014)"),
    ("trip_id", "(1 or 2)"),
    ("trip_id", "3"),
])
def test_placeholders_and_invalid_answers_are_rejected(column, value):
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    output.loc[output.order_ref.eq("o1"), column] = value
    with pytest.raises(Task2BSubmissionError):
        validate_task2b_submission(output, template, allocation, orders, known_vehicle_ids=["v1", "v2"])


def test_deferred_empty_fields_are_valid_but_populated_fields_fail():
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    validate_task2b_submission(output, template, allocation, orders)
    output.loc[output.order_ref.eq("o2"), "vehicle_id"] = "v1"
    with pytest.raises(Task2BSubmissionError, match="Deferred"):
        validate_task2b_submission(output, template, allocation, orders)


def test_unknown_served_vehicle_and_extra_index_column_fail():
    template, allocation, orders = _case()
    bad_allocation = allocation.copy()
    bad_allocation.loc[bad_allocation.order_ref.eq("o1"), "vehicle_id"] = "unknown"
    output = build_task2b_submission(template, bad_allocation, orders)
    with pytest.raises(Task2BSubmissionError, match="unknown vehicle"):
        validate_task2b_submission(
            output, template, bad_allocation, orders, known_vehicle_ids=["v1", "v2"]
        )
    output.insert(0, "Unnamed: 0", range(len(output)))
    with pytest.raises(Task2BSubmissionError, match="exact six"):
        validate_task2b_submission(output, template, allocation, orders)


def test_atomic_write_readback_hash_and_overwrite_protection(tmp_path: Path):
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    path = tmp_path / "submission_task2b.csv"
    report = write_task2b_submission_atomic(
        path, output, template, allocation, orders,
        source_allocation_sha256="a" * 64, known_vehicle_ids=["v1", "v2"],
    )
    assert report["submission_task2b_sha256"] == sha256_file(path)
    assert pd.read_csv(path).columns.tolist() == list(OFFICIAL_COLUMNS)
    with pytest.raises(Task2BSubmissionError, match="already exists"):
        write_task2b_submission_atomic(
            path, output, template, allocation, orders, source_allocation_sha256="a" * 64
        )
    with pytest.raises(Task2BSubmissionError, match="matching prior"):
        write_task2b_submission_atomic(
            path, output, template, allocation, orders,
            source_allocation_sha256="a" * 64, force=True, existing_export_manifest={}
        )
    write_task2b_submission_atomic(
        path, output, template, allocation, orders,
        source_allocation_sha256="a" * 64, force=True,
        existing_export_manifest={"phase22_frozen_allocation_sha256": "a" * 64},
    )


def test_phase23_candidate_semantic_parity_is_required():
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    candidate = output.copy()
    assert validate_task2b_submission(
        output, template, allocation, orders, phase23_candidate=candidate
    )["phase23_checker_candidate_parity"] == "PASS"
    candidate.loc[candidate.order_ref.eq("o1"), "trip_id"] = "2"
    with pytest.raises(Task2BSubmissionError, match="Phase 23"):
        validate_task2b_submission(output, template, allocation, orders, phase23_candidate=candidate)
