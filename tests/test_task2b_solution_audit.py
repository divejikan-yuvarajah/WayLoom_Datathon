"""Synthetic independent audit tests, including deliberately corrupted rows."""
import pandas as pd
import pytest

from src.task2b.lexicographic_solver import solve_lexicographic
from src.task2b.optimizer import build_optimizer_model
from src.task2b.solution import extract_allocation, extract_solver_trip_minutes
from src.task2b.solution_audit import AuditError, TRIP_SUMMARY_COLUMNS, audit_allocation, audit_objective_vector
from src.task2b.solver_data import build_solver_data
from tests.test_task2b_solver_data import _case


def _solved():
    scenario, matrix, metadata, config, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, config, priority)
    bundle = build_optimizer_model(data)
    result = solve_lexicographic(bundle, config)
    allocation = extract_allocation(bundle, result)
    return data, allocation, extract_solver_trip_minutes(bundle, result)


def test_recomputes_hard_rules_from_extracted_rows():
    data, allocation, minutes = _solved()
    assert audit_allocation(allocation, data, minutes).status == "PASS"
    assert len(audit_allocation(allocation, data, minutes).trip_summary) == 2
    bad = allocation.copy()
    bad.loc[bad.order_ref.eq("o1"), "trip_id"] = bad.loc[bad.order_ref.eq("o2"), "trip_id"].iloc[0]
    with pytest.raises(AuditError, match="mixes"):
        audit_allocation(bad, data)
    bad = allocation.copy()
    bad.loc[bad.order_ref.eq("o1"), "vehicle_id"] = "workshop"
    with pytest.raises(AuditError, match="unavailable"):
        audit_allocation(bad, data)
    bad = allocation.copy()
    bad.loc[bad.order_ref.eq("o1"), "decision"] = "deferred"
    with pytest.raises(AuditError, match="Deferred"):
        audit_allocation(bad, data)
    with pytest.raises(AuditError, match="CP-SAT trip time"):
        audit_allocation(allocation, data, {key: value + 1 for key, value in minutes.items()})


def test_preserves_repeated_outlet_order_grain():
    data, allocation, _ = _solved()
    assert allocation.order_ref.nunique() == len(data.order_ids)
    assert allocation.outlet_id.nunique() == 1
    duplicate = pd.concat([allocation, allocation.iloc[[0]]], ignore_index=True)
    with pytest.raises(AuditError, match="exactly one"):
        audit_allocation(duplicate, data)


def test_independent_objective_reconciliation():
    scenario, matrix, metadata, config, priority = _case()
    data = build_solver_data(scenario, matrix, metadata, config, priority)
    bundle = build_optimizer_model(data)
    result = solve_lexicographic(bundle, config)
    allocation = extract_allocation(bundle, result)
    assert audit_objective_vector(allocation, data, result.objective_vector) == result.objective_vector
    bad = dict(result.objective_vector)
    bad["served_order_count"] += 1
    with pytest.raises(AuditError, match="objective"):
        audit_objective_vector(allocation, data, bad)


def test_all_deferred_retains_empty_trip_summary_schema():
    data, allocation, _ = _solved()
    allocation["decision"] = "deferred"
    allocation["vehicle_id"] = None
    allocation["trip_id"] = None
    result = audit_allocation(allocation, data)
    assert result.status == "PASS" and result.trip_summary.empty
    assert tuple(result.trip_summary.columns) == TRIP_SUMMARY_COLUMNS


def test_audit_accepts_exact_numeric_strings_from_private_loader():
    scenario, matrix, metadata, config, priority = _case()
    scenario["service_allowance_ref"]["service_allowance_min"] = (
        scenario["service_allowance_ref"].service_allowance_min.astype(str)
    )
    data = build_solver_data(scenario, matrix, metadata, config, priority)
    bundle = build_optimizer_model(data)
    result = solve_lexicographic(bundle, config)
    allocation = extract_allocation(bundle, result)
    assert audit_allocation(allocation, data, extract_solver_trip_minutes(bundle, result)).status == "PASS"
