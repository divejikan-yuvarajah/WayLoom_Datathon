from dataclasses import replace

import pytest

from src.task2b.counterfactual_reasoner import ForcedCounterfactualResult
from src.task2b.deferral_explanations import (
    COUNTERFACTUAL_CAUTION,
    DeferralExplanationError,
    generate_explanation,
)
from src.task2b.direct_insertion import DirectInsertionResult, InsertionAttempt
from src.task2b.individual_feasibility import IndividualFeasibilityResult
from src.task2b.solver_data import build_solver_data
from tests.test_task2b_solver_data import _case


def _forced(*, status="OPTIMAL", relation="WORSE", tier="LEVEL 3 - waiting-days served", changes=2):
    return ForcedCounterfactualResult(
        "private-o", "OPTIMAL" if status == "OPTIMAL" else "INFEASIBLE", status,
        tuple({"status": "OPTIMAL"} for _ in range(9)) if status == "OPTIMAL" else (),
        {} if status == "OPTIMAL" else None, relation if status == "OPTIMAL" else None,
        tier if relation == "WORSE" and status == "OPTIMAL" else None,
        "OPTIMAL" if status == "OPTIMAL" else None,
        changes if status == "OPTIMAL" else None, None, None,
        {"changed_order_count": changes} if status == "OPTIMAL" else None, None,
    )


def test_hard_infeasible_is_never_labelled_lower_priority_and_text_is_cautious():
    data = build_solver_data(*_case())
    individual = IndividualFeasibilityResult("o1", 0, False, 0, None, None)
    direct = DirectInsertionResult("o1", False, ())
    explanation = generate_explanation(data, "o1", individual, direct, _forced(status="INFEASIBLE"))
    assert explanation.reason_class == "UNAVOIDABLE_HARD"
    assert explanation.primary_reason_code == "HARD_NO_COMPATIBLE_VEHICLE"
    assert "lower-priority policy choice" in explanation.human_explanation
    assert COUNTERFACTUAL_CAUTION in explanation.human_explanation
    assert "o1" not in explanation.human_explanation


def test_worse_vector_is_policy_tradeoff_with_only_supported_resource_reasons():
    data = build_solver_data(*_case())
    individual = IndividualFeasibilityResult("o1", 1, True, 1, None, "2")
    direct = DirectInsertionResult("o1", False, (
        InsertionAttempt("v1", 1, "EXISTING_SAME_GROUP", False, ("WEIGHT_CAPACITY", "FRESH_TIME_BUDGET")),
    ))
    explanation = generate_explanation(data, "o1", individual, direct, _forced())
    assert explanation.reason_class == "POLICY_TRADEOFF"
    assert explanation.primary_reason_code == "LOWER_POLICY_PRIORITY"
    assert "CAPACITY_COMPETITION" in explanation.secondary_reason_codes
    assert "FRESH_TIME_BUDGET" in explanation.secondary_reason_codes
    assert "LEVEL 3" in explanation.human_explanation
    assert "minimum" not in explanation.human_explanation.lower() or "proven closest" in explanation.human_explanation


def test_equal_vector_is_alternative_optimum_not_unavoidable():
    data = build_solver_data(*_case())
    individual = IndividualFeasibilityResult("o2", 1, True, 1, None, "2")
    direct = DirectInsertionResult("o2", False, ())
    explanation = generate_explanation(
        data, "o2", individual, direct, _forced(relation="EQUAL", tier=None)
    )
    assert explanation.reason_class == "ALTERNATIVE_OPTIMUM"
    assert explanation.primary_reason_code == "ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN"
    assert "not evidence" in explanation.human_explanation


def test_chilled_requirement_alone_does_not_create_scarcity_reason():
    data = build_solver_data(*_case())
    individual = IndividualFeasibilityResult("o1", 1, True, 1, None, "2")
    explanation = generate_explanation(
        data, "o1", individual, DirectInsertionResult("o1", False, ()),
        _forced(relation="EQUAL", tier=None),
    )
    assert "SCARCE_REEFER_CAPACITY" not in explanation.secondary_reason_codes
    assert "SCARCE_REEFER_VAN_CAPACITY" not in explanation.secondary_reason_codes


def test_direct_insert_and_incomplete_policy_evidence_fail_closed():
    data = build_solver_data(*_case())
    individual = IndividualFeasibilityResult("o1", 1, True, 1, None, "2")
    with pytest.raises(DeferralExplanationError, match="Direct insertion"):
        generate_explanation(data, "o1", individual, DirectInsertionResult("o1", True, ()), _forced())
    with pytest.raises(DeferralExplanationError, match="complete optimal"):
        generate_explanation(data, "o1", individual, DirectInsertionResult("o1", False, ()),
                             replace(_forced(), forced_solve_status="FEASIBLE", vector_relation=None))
