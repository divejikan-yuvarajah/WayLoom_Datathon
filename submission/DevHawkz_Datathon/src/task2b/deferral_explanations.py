"""Evidence-grounded classification and deterministic Phase 26 wording."""

from __future__ import annotations

from dataclasses import dataclass

from src.task2b.counterfactual_reasoner import ForcedCounterfactualResult
from src.task2b.direct_insertion import DirectInsertionResult
from src.task2b.individual_feasibility import IndividualFeasibilityResult
from src.task2b.reason_codes import (
    ALTERNATIVE_OPTIMUM,
    POLICY_TRADEOFF,
    REASON_TAXONOMY,
    UNAVOIDABLE_HARD,
    validate_reason_assignment,
)
from src.task2b.solver_data import SolverData


COUNTERFACTUAL_CAUTION = (
    "This is a solver counterfactual under the frozen Task 2B assumptions, "
    "not a claim about what would definitely happen in real operations or a real-world causal effect."
)


@dataclass(frozen=True)
class DeferralExplanation:
    reason_class: str
    primary_reason_code: str
    secondary_reason_codes: tuple[str, ...]
    evidence_level: str
    resource_evidence_summary: str
    human_explanation: str
    counterfactual_complete: bool


class DeferralExplanationError(ValueError):
    """Evidence is insufficient or inconsistent for a final explanation."""


def _resource_reasons(data: SolverData, order_ref: str,
                      direct: DirectInsertionResult) -> tuple[str, ...]:
    blockers = set(direct.blocker_codes)
    reasons: set[str] = set()
    if blockers & {"WEIGHT_CAPACITY", "VOLUME_CAPACITY"}:
        reasons.add("CAPACITY_COMPETITION")
    if "NO_FREE_TRIP_SLOT" in blockers:
        reasons.add("TRIP_SLOT_LIMIT")
    if "FRESH_TIME_BUDGET" in blockers:
        reasons.add("FRESH_TIME_BUDGET")
    if "STYLE_TECH_TIME_BUDGET" in blockers:
        reasons.add("STYLE_TECH_TIME_BUDGET")
    order = data.order_rows[order_ref]
    compatible = [data.vehicle_rows[v] for o, v in data.compatible_pairs if o == order_ref]
    physical = blockers & {
        "WEIGHT_CAPACITY", "VOLUME_CAPACITY", "NO_FREE_TRIP_SLOT",
        "FRESH_TIME_BUDGET", "STYLE_TECH_TIME_BUDGET",
    }
    if physical and compatible and order["temp_requirement"] == "chilled" and all(
        vehicle["temp"] == "reefer" for vehicle in compatible
    ):
        reasons.add("SCARCE_REEFER_CAPACITY")
    if (physical and compatible and order["temp_requirement"] == "chilled"
            and order["parking_constraint"] == "van_only"
            and all(vehicle["temp"] == "reefer" and vehicle["type"] == "van"
                    for vehicle in compatible)):
        reasons.add("SCARCE_REEFER_VAN_CAPACITY")
    return tuple(code for code in REASON_TAXONOMY if code in reasons)


def classify_deferral(data: SolverData, order_ref: str,
                      individual: IndividualFeasibilityResult,
                      direct: DirectInsertionResult,
                      counterfactual: ForcedCounterfactualResult) -> tuple[str, str, tuple[str, ...]]:
    if direct.direct_insert_possible:
        raise DeferralExplanationError("Direct insertion contradicts Phase 22 Level 1 optimality.")
    if not individual.individually_feasible:
        if counterfactual.hard_status != "INFEASIBLE":
            raise DeferralExplanationError("Hard-unavoidable classification lacks solver proof.")
        primary = (
            "HARD_NO_COMPATIBLE_VEHICLE"
            if individual.compatible_vehicle_count == 0
            else individual.time_blocker_code
        )
        if primary is None:
            raise DeferralExplanationError("Hard infeasibility has no supported reason code.")
        validate_reason_assignment(UNAVOIDABLE_HARD, primary)
        return UNAVOIDABLE_HARD, primary, ()
    if counterfactual.forced_solve_status != "OPTIMAL" or counterfactual.vector_relation is None:
        raise DeferralExplanationError("Hard-feasible target lacks complete optimal counterfactual evidence.")
    secondary = _resource_reasons(data, order_ref, direct)
    if counterfactual.vector_relation == "WORSE":
        reason_class, primary = POLICY_TRADEOFF, "LOWER_POLICY_PRIORITY"
    elif counterfactual.vector_relation == "EQUAL":
        reason_class, primary = ALTERNATIVE_OPTIMUM, "ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN"
    else:
        raise DeferralExplanationError("A better-than-baseline vector is a Phase 22 contradiction.")
    validate_reason_assignment(reason_class, primary, secondary)
    return reason_class, primary, secondary


def _resource_phrase(codes: tuple[str, ...]) -> str:
    labels = {
        "CAPACITY_COMPETITION": "weight/volume capacity",
        "SCARCE_REEFER_CAPACITY": "the specialized reefer pool",
        "SCARCE_REEFER_VAN_CAPACITY": "the specialized reefer-van subset",
        "TRIP_SLOT_LIMIT": "the two-trip slot limit",
        "FRESH_TIME_BUDGET": "the Fresh time budget",
        "STYLE_TECH_TIME_BUDGET": "the combined Style and Tech time budget",
    }
    values = [labels[code] for code in codes if code in labels]
    return ", ".join(values) if values else "no single physical bottleneck isolated by direct insertion"


def generate_explanation(data: SolverData, order_ref: str,
                         individual: IndividualFeasibilityResult,
                         direct: DirectInsertionResult,
                         counterfactual: ForcedCounterfactualResult) -> DeferralExplanation:
    reason_class, primary, secondary = classify_deferral(
        data, order_ref, individual, direct, counterfactual
    )
    resource = _resource_phrase(secondary)
    if reason_class == UNAVOIDABLE_HARD:
        if primary == "HARD_NO_COMPATIBLE_VEHICLE":
            evidence = "no available vehicle passes all static whole-order compatibility rules"
        elif primary == "FRESH_TIME_BUDGET":
            evidence = "every compatible one-order Fresh trip exceeds the 270-minute budget"
        else:
            evidence = "every compatible one-order Style/Tech trip exceeds the 480-minute budget"
        resource = evidence
        text = (
            f"This order is hard-unavoidable under the frozen scenario because {evidence}. "
            "The forced-target hard model is infeasible, so this is not a lower-priority policy choice. "
            + COUNTERFACTUAL_CAUTION
        )
    elif reason_class == POLICY_TRADEOFF:
        if not counterfactual.first_degraded_tier:
            raise DeferralExplanationError("Policy tradeoff lacks its first degraded tier.")
        change = (
            f"The proven closest counterfactual requires {counterfactual.minimum_changed_orders} allocation-row changes. "
            if counterfactual.minimal_change_status == "OPTIMAL"
            else f"A counterfactual was found with {counterfactual.change_summary['changed_order_count']} changes. "
        )
        text = (
            "This order is feasible in isolation but cannot be inserted into the frozen plan without changing assignments. "
            f"The forced optimal counterfactual first worsens {counterfactual.first_degraded_tier}. "
            f"Supported resource evidence: {resource}. {change}"
            "The frozen allocation therefore keeps the higher-ranked WayLoom policy outcome. "
            + COUNTERFACTUAL_CAUTION
        )
    else:
        change = (
            f"The proven closest counterfactual requires {counterfactual.minimum_changed_orders} allocation-row changes. "
            if counterfactual.minimal_change_status == "OPTIMAL"
            else f"A counterfactual was found with {counterfactual.change_summary['changed_order_count']} changes. "
        )
        text = (
            "This order can be served in an alternative allocation with the same frozen WayLoom policy objective vector. "
            f"Supported resource evidence: {resource}. {change}"
            "The frozen allocation is one of multiple policy-equivalent feasible solutions, not evidence that the order was hard-impossible. "
            + COUNTERFACTUAL_CAUTION
        )
    if order_ref in text:
        raise DeferralExplanationError("Human explanation exposed the private order reference.")
    return DeferralExplanation(
        reason_class, primary, secondary, "SOLVER_PROVEN", resource, text, True
    )
