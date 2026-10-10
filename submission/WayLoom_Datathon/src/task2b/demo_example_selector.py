"""Deterministic, privacy-safe selection of at most two Phase 26 examples."""

from __future__ import annotations

from typing import Any, Iterable


class DemoSelectionError(ValueError):
    """Demo examples are unresolved or cannot be anonymized safely."""


def _quality(record: dict[str, Any]) -> tuple[int, int, int, int]:
    complete = int(bool(record.get("counterfactual_complete")))
    resource = int(bool(record.get("secondary_reason_codes")))
    minimum = record.get("minimum_changed_orders")
    easy = -int(minimum) if minimum is not None else -10**9
    original = -int(record.get("original_order_position", 10**9))
    return complete, resource, easy, original


def select_demo_examples(records: Iterable[dict[str, Any]], *, max_examples: int = 2
                         ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if max_examples < 1 or max_examples > 2:
        raise DemoSelectionError("Phase 26 permits one or two demo examples.")
    candidates = [dict(record) for record in records if record.get("counterfactual_complete") is True]
    if not candidates:
        raise DemoSelectionError("No resolved deferral is available for a demo.")
    by_class = {
        name: sorted(
            [item for item in candidates if item.get("reason_class") == name],
            key=_quality, reverse=True,
        )
        for name in ("UNAVOIDABLE_HARD", "POLICY_TRADEOFF", "ALTERNATIVE_OPTIMUM")
    }
    if by_class["UNAVOIDABLE_HARD"]:
        selected = [by_class["UNAVOIDABLE_HARD"][0]]
        complement = by_class["POLICY_TRADEOFF"] or by_class["ALTERNATIVE_OPTIMUM"]
    elif by_class["POLICY_TRADEOFF"]:
        selected = [by_class["POLICY_TRADEOFF"][0]]
        complement = by_class["ALTERNATIVE_OPTIMUM"]
    else:
        selected = [by_class["ALTERNATIVE_OPTIMUM"][0]]
        complement = []
    if max_examples == 2 and len(candidates) > 1:
        remaining = [item for item in candidates if item is not selected[0]]
        remaining.sort(key=_quality, reverse=True)
        selected.append((complement or remaining)[0])
    private, sanitized = [], []
    for index, record in enumerate(selected):
        label = f"DEFERRAL_EXAMPLE_{chr(ord('A') + index)}"
        private.append({"example_label": label, **record})
        public = {
            "example_label": label,
            "reason_class": record.get("reason_class"),
            "primary_reason_code": record.get("primary_reason_code"),
            "secondary_reason_codes": list(record.get("secondary_reason_codes") or []),
            "brand": record.get("brand"),
            "district": record.get("district"),
            "temperature_requirement": record.get("temp_requirement"),
            "van_only": bool(record.get("van_only", False)),
            "compatible_vehicle_count": int(record.get("compatible_vehicle_count", 0)),
            "first_degraded_policy_tier": record.get("first_degraded_policy_tier"),
            "minimum_changed_orders": record.get("minimum_changed_orders"),
            "human_explanation": record.get("human_explanation"),
        }
        forbidden = {"order_ref", "vehicle_id", "outlet_id", "trip_id"}
        if forbidden.intersection(public) or any(
            record.get(key) is not None
            and str(record.get(key)).strip() != ""
            and str(record.get(key)) in str(public)
            for key in forbidden
        ):
            raise DemoSelectionError("Sanitized demo output contains a private identifier.")
        sanitized.append(public)
    return private, sanitized
