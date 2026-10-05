"""Synthetic aggregate evidence and deterministic Phase 24 policy tests."""

from __future__ import annotations

import json
import sys

import pandas as pd
import pytest
import yaml

from src.task2b.checker_evidence import build_checker_evidence
from src.task2b.checker_runner import CheckerRunResult
from src.task2b.policy_evidence import (
    PolicyEvidenceError,
    build_task2b_policy_evidence,
    validate_policy_evidence,
)
from src.task2b.policy_writer import PolicyWriterError, render_task2b_policy, validate_policy_text


def _phase23_evidence():
    result = CheckerRunResult(
        status="PASS", pass_detected=True, exit_code=0, stdout="PASS", stderr="",
        timed_out=False, command=(sys.executable, "checker.py", "candidate.csv"),
        working_directory="private", checker_sha256="a" * 64,
        candidate_sha256="b" * 64,
        invocation_mode="python_script_single_positional_candidate",
    )
    return build_checker_evidence(
        result,
        frozen_allocation_sha256="c" * 64,
        phase22_freeze_manifest_sha256="d" * 64,
        python_version="test",
        own_validator_status="PASS",
        git_commit="commit",
        timestamp="2026-10-06T00:00:00+00:00",
    )


def _inputs():
    orders = pd.DataFrame([
        {"scenario": "S1", "order_ref": "ORDER-1", "outlet_id": "OUTLET-A", "brand": "Fresh", "temp_requirement": "chilled", "order_units": 10, "order_weight_kg": 100, "order_volume_m3": 2, "deferred_yesterday": 1, "days_since_last_served": 5},
        {"scenario": "S1", "order_ref": "ORDER-2", "outlet_id": "OUTLET-A", "brand": "Style", "temp_requirement": "ambient", "order_units": 20, "order_weight_kg": 200, "order_volume_m3": 3, "deferred_yesterday": 0, "days_since_last_served": 2},
        {"scenario": "S1", "order_ref": "ORDER-3", "outlet_id": "OUTLET-B", "brand": "Fresh", "temp_requirement": "chilled", "order_units": 30, "order_weight_kg": 300, "order_volume_m3": 4, "deferred_yesterday": 1, "days_since_last_served": 8},
        {"scenario": "S1", "order_ref": "ORDER-4", "outlet_id": "OUTLET-C", "brand": "Tech", "temp_requirement": "ambient", "order_units": 40, "order_weight_kg": 400, "order_volume_m3": 5, "deferred_yesterday": 0, "days_since_last_served": 4},
    ])
    allocation = pd.DataFrame([
        {"scenario": "S1", "order_ref": "ORDER-1", "decision": "served", "vehicle_id": "VEH-1", "trip_id": 1},
        {"scenario": "S1", "order_ref": "ORDER-2", "decision": "served", "vehicle_id": "VEH-2", "trip_id": 1},
        {"scenario": "S1", "order_ref": "ORDER-3", "decision": "deferred", "vehicle_id": None, "trip_id": None},
        {"scenario": "S1", "order_ref": "ORDER-4", "decision": "deferred", "vehicle_id": None, "trip_id": None},
    ])
    fleet = pd.DataFrame([
        {"scenario": "S1", "vehicle_id": "VEH-1", "status": "available"},
        {"scenario": "S1", "vehicle_id": "VEH-2", "status": "available"},
        {"scenario": "S1", "vehicle_id": "VEH-3", "status": "in_workshop"},
    ])
    vehicles = pd.DataFrame([
        {"vehicle_id": "VEH-1", "type": "van", "temp": "reefer", "depot": "Peliyagoda"},
        {"vehicle_id": "VEH-2", "type": "truck", "temp": "ambient", "depot": "Peliyagoda"},
        {"vehicle_id": "VEH-3", "type": "van", "temp": "reefer", "depot": "Peliyagoda"},
    ])
    compatibility = pd.DataFrame({
        "order_ref": ["ORDER-1", "ORDER-2", "ORDER-3", "ORDER-4"],
        "compatible_vehicle_count": [1, 2, 0, 1],
    })
    trips = pd.DataFrame([
        {"vehicle_id": "VEH-1", "trip_id": 1, "brand": "Fresh", "trip_minutes": 100, "weight_kg": 100, "volume_m3": 2, "weight_cap_kg": 500, "volume_cap_m3": 10},
        {"vehicle_id": "VEH-2", "trip_id": 1, "brand": "Style", "trip_minutes": 200, "weight_kg": 200, "volume_m3": 3, "weight_cap_kg": 400, "volume_cap_m3": 6},
    ])
    return orders, allocation, fleet, vehicles, compatibility, trips, _phase23_evidence()


def _priority_config():
    return yaml.safe_load(open("configs/task2b_priority.yaml", encoding="utf-8"))


def _evidence():
    return build_task2b_policy_evidence(*_inputs(), trip_summary_sha256="e" * 64)


def test_aggregate_policy_evidence_calculations_and_privacy():
    evidence = _evidence()
    m = evidence["metrics"]
    assert (m["total_orders"], m["served_orders"], m["deferred_orders"]) == (4, 2, 2)
    assert m["served_by_brand"] == {"Fresh": 1, "Style": 1}
    assert m["deferred_by_brand"] == {"Fresh": 1, "Tech": 1}
    assert (m["served_units"], m["deferred_units"]) == (30.0, 70.0)
    assert (m["deferred_weight_kg"], m["deferred_volume_m3"]) == (700.0, 9.0)
    assert (m["deferred_chilled_orders"], m["deferred_chilled_volume_m3"]) == (1, 4.0)
    assert (m["previously_deferred_total"], m["previously_deferred_served"], m["previously_deferred_still_deferred"]) == (2, 1, 1)
    assert (m["deferred_days_since_last_served_sum"], m["deferred_days_since_last_served_mean"], m["deferred_days_since_last_served_max"]) == (12.0, 6.0, 8.0)
    assert (m["individually_impossible_deferred_count"], m["low_flexibility_deferred_count"]) == (1, 1)
    assert (m["available_vehicle_count"], m["workshop_vehicle_count"]) == (2, 1)
    assert (m["available_reefer_count"], m["available_reefer_van_count"]) == (1, 1)
    assert (m["used_trip_count"], m["available_trip_slot_upper_bound"]) == (2, 4)
    assert (m["max_fresh_minutes_used_by_vehicle"], m["max_style_tech_minutes_used_by_vehicle"]) == (100.0, 200.0)
    payload = json.dumps(evidence)
    assert "ORDER-" not in payload and "OUTLET-" not in payload and "VEH-" not in payload
    assert set(evidence["metrics"]) == set(evidence["provenance"])


def test_policy_contains_required_concepts_and_only_evidence_backed_facts():
    evidence = _evidence()
    policy, validation = render_task2b_policy(evidence, _priority_config())
    lower = policy.lower()
    for phrase in (
        "wayloom engineering policy", "official feasibility", "limiting resources",
        "no compatible available vehicle", "could be added without a tradeoff",
        "operational cost and impact", "no monetary cost field", "no return journey",
        "fresh minutes", "style+tech minutes",
        "trip_minutes = outbound + inter_stop * (n_orders - 1) + sum(service_allowance_min)",
    ):
        assert phrase in lower
    assert validation["status"] == "PASS" and validation["target_met"]
    assert validation["numeric_fact_count"] > 20
    assert "ORDER-" not in policy and "VEH-" not in policy and "OUTLET-" not in policy
    assert not any(symbol in policy for symbol in ("$", "£", "€", "₹"))


def test_policy_evidence_rejects_contradictions_and_failed_phase23():
    evidence = _evidence()
    evidence["metrics"]["total_orders"] = 99
    with pytest.raises(PolicyEvidenceError, match="reconcile"):
        validate_policy_evidence(evidence)
    inputs = list(_inputs())
    inputs[-1]["official_checker_status"] = "FAIL"
    with pytest.raises(PolicyEvidenceError, match="Phase 23"):
        build_task2b_policy_evidence(*inputs, trip_summary_sha256="e" * 64)


def test_policy_rejects_unknown_fact_missing_concept_currency_and_private_id():
    evidence = _evidence()
    policy, validation = render_task2b_policy(evidence, _priority_config())
    broken_facts = dict(validation["used_facts"])
    broken_facts["unknown"] = {"rendered": "999"}
    with pytest.raises(PolicyWriterError):
        validate_policy_text(policy, evidence, used_facts=broken_facts)
    with pytest.raises(PolicyWriterError, match="required concepts"):
        validate_policy_text(policy.replace("## Limiting resources", "## Constraints"), evidence)
    with pytest.raises(PolicyWriterError, match="monetary"):
        validate_policy_text(policy + "LKR 100\n", evidence)
    with pytest.raises(PolicyWriterError, match="private"):
        validate_policy_text(policy + "ORDER-1\n", evidence, private_identifiers=["ORDER-1"])
    with pytest.raises(PolicyWriterError, match="placeholder"):
        validate_policy_text(policy + "{{unknown_fact}}\n", evidence)


def test_priority_order_change_and_material_length_excess_fail():
    evidence = _evidence()
    config = _priority_config()
    config["objective_levels"] = list(reversed(config["objective_levels"]))
    with pytest.raises(PolicyWriterError, match="Phase 21"):
        render_task2b_policy(evidence, config)
    policy, _ = render_task2b_policy(evidence, _priority_config())
    with pytest.raises(PolicyWriterError, match="one-page"):
        validate_policy_text(policy + (" extra" * 700), evidence)


def test_policy_evidence_requires_complete_hash_bindings():
    evidence = _evidence()
    evidence["bindings"]["trip_summary_sha256"] = "bad"
    with pytest.raises(PolicyEvidenceError, match="hash bindings"):
        validate_policy_evidence(evidence)
