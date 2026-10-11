"""Deterministic, aggregate-only Phase 24 Task 2B policy writer."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from src.task2b.artifact_integrity import sha256_file
from src.task2b.policy_evidence import PolicyEvidenceError, validate_policy_evidence
from src.task2b.priority import OBJECTIVE_LEVELS


class PolicyWriterError(ValueError):
    """The policy would be unsupported, incomplete, or too long."""


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


@dataclass
class _FactBook:
    evidence: dict[str, Any]
    used: dict[str, dict[str, Any]] = field(default_factory=dict)

    def value(self, key: str, *, suffix: str = "") -> str:
        parts = key.split(".")
        root = parts[0]
        if root not in self.evidence["metrics"]:
            raise PolicyWriterError(f"Unknown policy fact: {key}.")
        value: Any = self.evidence["metrics"][root]
        for part in parts[1:]:
            if not isinstance(value, dict) or part not in value:
                raise PolicyWriterError(f"Unknown policy fact: {key}.")
            value = value[part]
        sources = self.evidence["provenance"].get(root)
        if not sources:
            raise PolicyWriterError(f"Policy fact lacks provenance: {key}.")
        rendered = _format_value(value) + suffix
        self.used[key] = {"value": value, "rendered": rendered, "source_artifacts": sources}
        return rendered


def _validate_priority_config(priority_config: dict[str, Any]) -> None:
    expected = [
        [name, "maximize" if name.startswith("served_") else "minimize"]
        for name in OBJECTIVE_LEVELS
    ]
    if (priority_config.get("version") != 1
            or priority_config.get("strategy") != "lexicographic"
            or priority_config.get("objective_levels") != expected
            or priority_config.get("hard_rule_override") is not False):
        raise PolicyWriterError("Frozen Phase 21 lexicographic policy changed.")


def _brand_summary(facts: _FactBook, metric: str) -> str:
    values = facts.evidence["metrics"][metric]
    if not values:
        return "none"
    return ", ".join(
        f"{brand} {facts.value(f'{metric}.{brand}')}"
        for brand in sorted(values)
    )


def render_task2b_policy(
    evidence: dict[str, Any],
    priority_config: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Render the competition policy solely from approved aggregate facts."""
    try:
        validate_policy_evidence(evidence)
    except PolicyEvidenceError as exc:
        raise PolicyWriterError(str(exc)) from exc
    _validate_priority_config(priority_config)
    facts = _FactBook(evidence)
    m = evidence["metrics"]

    fleet_sentence = (
        f"The usable home-depot fleet contained {facts.value('available_vehicle_count')} vehicles, "
        f"including {facts.value('available_reefer_count')} reefers and "
        f"{facts.value('available_reefer_van_count')} reefer vans; "
        f"{facts.value('workshop_vehicle_count')} listed vehicles were unavailable in the workshop."
    )
    slot_sentence = (
        f"The plan used {facts.value('used_trip_count')} of the theoretical "
        f"{facts.value('available_trip_slot_upper_bound')} available trip slots. "
        f"The highest per-vehicle use was {facts.value('max_fresh_minutes_used_by_vehicle')} of "
        f"{facts.value('fresh_budget_limit')} Fresh minutes and "
        f"{facts.value('max_style_tech_minutes_used_by_vehicle')} of "
        f"{facts.value('style_tech_budget_limit')} Style+Tech minutes. "
        f"Peak trip loading reached {facts.value('max_trip_weight_utilization_percent', suffix='%')} by weight "
        f"and {facts.value('max_trip_volume_utilization_percent', suffix='%')} by volume."
    )
    impossible = int(m["individually_impossible_deferred_count"])
    if impossible:
        limiting_sentence = (
            f"Hard vehicle compatibility was a demonstrated direct limiter: "
            f"{facts.value('individually_impossible_deferred_count')} deferred orders had no compatible "
            "available vehicle for the whole order."
        )
    else:
        limiting_sentence = (
            "No deferred order was individually impossible from vehicle compatibility alone. "
            "The aggregate evidence therefore does not label a single specialized fleet class as the sole bottleneck."
        )

    feasible_deferred = int(m["individually_feasible_deferred_count"])
    if feasible_deferred:
        choice_sentence = (
            f"The remaining {facts.value('individually_feasible_deferred_count')} deferred orders each had at "
            "least one compatible vehicle in isolation, but that does not mean they could be added without a tradeoff. "
            "Their deferral reflects competition for legal brand-district trips, whole-order capacity, trip slots, "
            "and vehicle time under the frozen allocation."
        )
    else:
        choice_sentence = (
            "No deferred order remained in the individually feasible shared-resource category; all deferrals were "
            "accounted for by direct compatibility impossibility, rather than a claim that another order could be "
            "added without a tradeoff."
        )

    text = f"""# WayLoom Task 2B Prioritization Policy

## Allocation objective

This is a WayLoom engineering policy, not an organizer-mandated priority rule. Official feasibility always dominates priority. Among feasible allocations, WayLoom first maximized the number of served orders; ties then favored previously deferred demand, greater waiting days, low-flexibility orders, Fresh chilled demand, and Fresh demand. Only after those coverage and fairness tiers tied did it conserve avoidable reefer-van, reefer, and van use.

The frozen plan serves {facts.value('served_orders')} of {facts.value('total_orders')} orders ({facts.value('served_share_percent', suffix='%')}) and defers {facts.value('deferred_orders')} ({facts.value('deferred_share_percent', suffix='%')}). Served and deferred decisions remain at `order_ref` grain; repeated outlets are not collapsed.

## Feasibility and calculation method

Every served order is assigned whole to one available home-depot vehicle and trip. A trip contains one brand and district; chilled demand requires a reefer, `van_only` demand requires a van, and both weight and volume capacities apply. Each vehicle uses at most two trips. Trip time is calculated as:

`trip_minutes = outbound + inter_stop * (n_orders - 1) + sum(service_allowance_min)`

Outbound travel is counted once, handling is included for every stop, and no return journey is added. A vehicle's combined Fresh trips must stay within {facts.value('fresh_budget_limit')} minutes, while its combined Style+Tech trips must stay within {facts.value('style_tech_budget_limit')} minutes.

## Limiting resources

{fleet_sentence} {slot_sentence} {limiting_sentence} These are aggregate indicators of constraint pressure; they are not an unsupported counterfactual claim that one resource alone caused every deferral.

## Deferral rationale

Orders with no compatible available vehicle were directly unavoidable under the hard constraints. {choice_sentence} Under equal feasibility, the frozen lexicographic policy selected service by total coverage, prior deferral, waiting time, low flexibility, Fresh chilled/Fresh demand, and specialized-vehicle conservation - not by an AI-generated discretionary rule.

Of {facts.value('previously_deferred_total')} previously deferred orders, {facts.value('previously_deferred_served')} are served and {facts.value('previously_deferred_still_deferred')} remain deferred. Deferred demand by brand is {_brand_summary(facts, 'deferred_by_brand')}.

## Operational cost and impact

The {facts.value('deferred_orders')} deferrals affect {facts.value('unique_deferred_outlet_count')} outlets and represent {facts.value('deferred_units')} units, {facts.value('deferred_weight_kg')} kg, and {facts.value('deferred_volume_m3')} m3. This includes {facts.value('deferred_chilled_orders')} chilled orders totaling {facts.value('deferred_chilled_volume_m3')} m3. Deferred orders have a mean wait of {facts.value('deferred_days_since_last_served_mean')} days and a maximum of {facts.value('deferred_days_since_last_served_max')} days since last service.

The supplied data contains no monetary cost field, so this policy reports deferral impact operationally rather than inventing a currency estimate.
"""
    text = text.strip() + "\n"
    validation = validate_policy_text(text, evidence, used_facts=facts.used)
    return text, validation


def validate_policy_text(
    policy: str,
    evidence: dict[str, Any],
    *,
    used_facts: dict[str, dict[str, Any]] | None = None,
    private_identifiers: Iterable[object] | None = None,
    target_max_words: int = 550,
    warn_above_words: int = 650,
) -> dict[str, Any]:
    validate_policy_evidence(evidence)
    lower = policy.lower()
    required = {
        "allocation_objective": "## allocation objective",
        "calculation_method": "## feasibility and calculation method",
        "limiting_resources": "## limiting resources",
        "deferral_rationale": "## deferral rationale",
        "cost_impact": "## operational cost and impact",
        "wayloom_not_official": "wayloom engineering policy, not an organizer-mandated priority rule",
        "trip_formula": "trip_minutes = outbound + inter_stop * (n_orders - 1) + sum(service_allowance_min)",
        "no_return": "no return journey",
        "monetary_disclaimer": "no monetary cost field",
        "unavoidable_standard": "no compatible available vehicle",
        "shared_tradeoff": "could be added without a tradeoff",
    }
    missing = [name for name, phrase in required.items() if phrase not in lower]
    if missing:
        raise PolicyWriterError(f"Policy is missing required concepts: {', '.join(missing)}.")
    if "PHASE24_LOCAL_GENERATION_REQUIRED" in policy or re.search(r"\{\{[^{}]+\}\}", policy):
        raise PolicyWriterError("Policy contains an unresolved generation placeholder.")
    if any(token in policy for token in ("$", "£", "€", "₹")) or re.search(r"\b(?:LKR|USD|Rs\.?)[ ]*\d", policy, re.IGNORECASE):
        raise PolicyWriterError("Policy contains an unsupported monetary amount.")
    if private_identifiers is not None:
        identifiers = {str(value) for value in private_identifiers if str(value).strip()}
        leaked = [value for value in identifiers if value in policy]
        if leaked:
            raise PolicyWriterError("Policy contains a private row-level identifier.")
    words = re.findall(r"\b[\w+%-]+\b", policy)
    word_count = len(words)
    if word_count > warn_above_words:
        raise PolicyWriterError("Policy materially exceeds the one-page engineering guard.")
    if used_facts is None:
        used_facts = {}
    for key, record in used_facts.items():
        root = key.split(".")[0]
        if root not in evidence["provenance"] or record.get("rendered") not in policy:
            raise PolicyWriterError(f"Policy fact is not traceable in the rendered text: {key}.")
    return {
        "status": "PASS",
        "word_count": word_count,
        "target_max_words": target_max_words,
        "warn_above_words": warn_above_words,
        "target_met": word_count <= target_max_words,
        "warning": None if word_count <= target_max_words else "Policy exceeds the preferred 550-word target.",
        "required_concepts": {name: "PASS" for name in required},
        "used_facts": used_facts,
        "numeric_fact_count": len(used_facts),
    }


def write_policy_atomic(path: Path, policy: str) -> str:
    path = Path(path)
    if path.name != "task2b_policy.md":
        raise PolicyWriterError("Final policy filename must be task2b_policy.md.")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix="task2b_policy_", suffix=".md", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(policy)
        if temporary.read_text(encoding="utf-8") != policy:
            raise PolicyWriterError("Policy write-back verification failed.")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return sha256_file(path)
