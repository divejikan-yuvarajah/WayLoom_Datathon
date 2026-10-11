"""Stable Phase 26 reason taxonomy for Task 2B deferrals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.task2b.priority import DEFERRAL_REASON_CODES


UNAVOIDABLE_HARD = "UNAVOIDABLE_HARD"
POLICY_TRADEOFF = "POLICY_TRADEOFF"
ALTERNATIVE_OPTIMUM = "ALTERNATIVE_OPTIMUM"
UNRESOLVED = "UNRESOLVED"

REASON_CLASSES = (UNAVOIDABLE_HARD, POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM)


@dataclass(frozen=True)
class ReasonDefinition:
    code: str
    definition: str
    required_evidence: str
    allowed_wording: str
    forbidden_overclaim: str
    allowed_classes: tuple[str, ...]


_DEFINITIONS = (
    ReasonDefinition(
        "HARD_NO_COMPATIBLE_VEHICLE",
        "No available vehicle passes every static official compatibility rule for the whole order.",
        "Zero compatible vehicles and a forced-target hard solve that is infeasible.",
        "No available vehicle can legally carry the whole order under the frozen scenario.",
        "Do not attribute the result to lower policy priority.",
        (UNAVOIDABLE_HARD,),
    ),
    ReasonDefinition(
        "CAPACITY_COMPETITION",
        "The order is feasible alone, but relevant insertion or counterfactual paths need weight/volume displacement or repacking.",
        "A relevant insertion path is blocked by weight or volume and the target is individually feasible.",
        "Weight or volume capacity is part of the allocation tradeoff.",
        "Do not claim capacity is the sole cause when other blockers are present.",
        (POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "SCARCE_REEFER_CAPACITY",
        "A chilled order depends on the available reefer pool and solver-grounded evidence implicates that pool.",
        "Chilled requirement, compatible vehicles restricted to reefers, and relevant resource-blocker evidence.",
        "Reefer availability is involved in the solver tradeoff.",
        "Do not label every chilled deferral as reefer scarcity.",
        (POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "SCARCE_REEFER_VAN_CAPACITY",
        "A chilled van-only order depends on the reefer-van subset and evidence implicates that subset.",
        "Chilled plus van-only, compatible vehicles restricted to reefer vans, and relevant resource-blocker evidence.",
        "Reefer-van availability is involved in the solver tradeoff.",
        "Do not infer scarcity from requirements alone.",
        (POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "TRIP_SLOT_LIMIT",
        "Compatible vehicles have no unused official trip slot for a required new trip without rearrangement.",
        "A relevant different-group insertion path records NO_FREE_TRIP_SLOT.",
        "The two-trip limit is part of the allocation tradeoff.",
        "Do not call an individually infeasible order trip-slot constrained.",
        (POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "FRESH_TIME_BUDGET",
        "The official per-vehicle Fresh time budget blocks an otherwise relevant path.",
        "Exact Phase 20 time arithmetic exceeds 270 minutes.",
        "The Fresh time budget blocks this path under the frozen assumptions.",
        "Do not claim a real-world causal effect.",
        (UNAVOIDABLE_HARD, POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "STYLE_TECH_TIME_BUDGET",
        "The official combined Style and Tech time budget blocks an otherwise relevant path.",
        "Exact Phase 20 time arithmetic exceeds 480 minutes.",
        "The combined Style and Tech time budget blocks this path under the frozen assumptions.",
        "Do not claim a real-world causal effect.",
        (UNAVOIDABLE_HARD, POLICY_TRADEOFF, ALTERNATIVE_OPTIMUM),
    ),
    ReasonDefinition(
        "LOWER_POLICY_PRIORITY",
        "Forcing the hard-feasible order worsens the frozen Phase 21 lexicographic objective vector.",
        "All forced stages are optimal and the direction-aware vector relation is WORSE.",
        "The frozen allocation keeps the higher-ranked policy outcome.",
        "Do not apply to a hard-infeasible order.",
        (POLICY_TRADEOFF,),
    ),
    ReasonDefinition(
        "ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN",
        "An equally policy-optimal feasible allocation can serve the order, but the frozen equivalent optimum does not.",
        "All forced stages are optimal and the forced objective vector equals the baseline vector.",
        "The frozen allocation is one of multiple policy-equivalent feasible solutions.",
        "Do not call the deferral unavoidable.",
        (ALTERNATIVE_OPTIMUM,),
    ),
)

REASON_TAXONOMY = {item.code: item for item in _DEFINITIONS}


class ReasonCodeError(ValueError):
    """The reason taxonomy or a reason assignment is invalid."""


def validate_taxonomy() -> None:
    """Prove exact continuity with the Phase 21 vocabulary."""
    if tuple(REASON_TAXONOMY) != tuple(DEFERRAL_REASON_CODES):
        raise ReasonCodeError("Phase 26 silently renamed or reordered a Phase 21 reason code.")
    if len(REASON_TAXONOMY) != len(_DEFINITIONS):
        raise ReasonCodeError("Reason codes must be unique.")
    for item in _DEFINITIONS:
        if not all((item.definition, item.required_evidence, item.allowed_wording, item.forbidden_overclaim)):
            raise ReasonCodeError(f"Reason metadata is incomplete: {item.code}.")
        if not item.allowed_classes or not set(item.allowed_classes).issubset(REASON_CLASSES):
            raise ReasonCodeError(f"Reason/class mapping is invalid: {item.code}.")


def validate_reason_assignment(reason_class: str, primary: str,
                               secondary: Iterable[str] = ()) -> tuple[str, ...]:
    validate_taxonomy()
    if reason_class not in REASON_CLASSES:
        raise ReasonCodeError(f"Unknown final reason class: {reason_class}.")
    codes = (primary, *tuple(secondary))
    if len(set(codes)) != len(codes):
        raise ReasonCodeError("Primary and secondary reason codes must be unique.")
    for code in codes:
        if code not in REASON_TAXONOMY:
            raise ReasonCodeError(f"Unknown reason code: {code}.")
        if reason_class not in REASON_TAXONOMY[code].allowed_classes:
            raise ReasonCodeError(f"Reason code {code} is incompatible with {reason_class}.")
    return codes


validate_taxonomy()
