"""Fixed, deterministic synthetic fixtures with no filesystem dependencies."""

from __future__ import annotations

import hashlib

from src.integration.models import (
    AllocationInsightRequest,
    AllocationInsightResponse,
    DeliveryRiskRequest,
    DeferralExplanationResponse,
    DemandForecastRequest,
    DemandForecastResponse,
    Task1Response,
)


LIMITATION = (
    "This is an optimization explanation under the supplied rules and WayLoom policy; "
    "it is not a real-world causal claim."
)


def _unit_interval(value: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def delivery_risk(request: DeliveryRiskRequest, *, seed: int = 42) -> Task1Response:
    signal = _unit_interval(request.model_dump_json(), seed)
    service = round(8.0 + request.route_distance_km * 0.18 + signal * 8.0, 1)
    late = round(min(0.95, 0.08 + signal * 0.48 + (0.12 if request.planned_arrival_hour >= 17 else 0)), 3)
    return Task1Response(
        source_mode="synthetic_demo",
        delivery_ref=request.delivery_ref,
        prediction={"pred_service_min": service, "pred_late_prob": late},
        model_status={"service_model": "synthetic", "late_model": "synthetic"},
    )


def demand_forecast(request: DemandForecastRequest, *, seed: int = 42) -> DemandForecastResponse:
    signal = _unit_interval(request.model_dump_json(), seed)
    total = round(7.5 + signal * 9.0 + request.forecast_horizon * 0.4, 2)
    chilled = round(total * (0.42 + signal * 0.18), 2) if request.brand == "Fresh" else 0.0
    ref_no = 1 if request.brand == "Fresh" else 2 if request.brand == "Style" else 3
    return DemandForecastResponse(
        source_mode="synthetic_demo",
        forecast_ref=f"DEMO_FORECAST_{ref_no:03d}",
        **request.model_dump(),
        pred_total_volume_m3=total,
        pred_chilled_volume_m3=chilled,
    )


def allocation_insight(request: AllocationInsightRequest) -> AllocationInsightResponse:
    return AllocationInsightResponse(
        source_mode="synthetic_demo",
        scenario_ref=request.scenario_ref,
        summary={
            "orders_total": 12,
            "orders_served": 10,
            "orders_deferred": 2,
            "vehicles_used": 5,
            "trips_used": 7,
        },
        constraint_summary={},
        reasoning={
            "policy_name": "WayLoom lexicographic allocation policy",
            "policy_origin": "WayLoom engineering policy",
            "hard_rules_precede_policy": True,
        },
        deferral_example_refs=["DEFERRAL_EXAMPLE_A", "DEFERRAL_EXAMPLE_B"],
    )


def deferral_explanations() -> list[DeferralExplanationResponse]:
    return [
        DeferralExplanationResponse(
            source_mode="synthetic_demo",
            example_ref="DEFERRAL_EXAMPLE_A",
            availability="synthetic_demo",
            reason_class="UNAVOIDABLE_HARD",
            primary_reason_code="HARD_NO_COMPATIBLE_VEHICLE",
            secondary_reason_codes=[],
            summary="No synthetic demo vehicle satisfies every whole-order compatibility rule.",
            evidence={
                "counterfactual_complete": True,
                "first_degraded_policy_tier": "HARD_FEASIBILITY",
                "changed_order_count": 0,
            },
            limitations=LIMITATION,
        ),
        DeferralExplanationResponse(
            source_mode="synthetic_demo",
            example_ref="DEFERRAL_EXAMPLE_B",
            availability="synthetic_demo",
            reason_class="POLICY_TRADEOFF",
            primary_reason_code="LOWER_POLICY_PRIORITY",
            secondary_reason_codes=["TRIP_SLOT_LIMIT"],
            summary="Serving this synthetic example would degrade a higher-ranked WayLoom policy tier.",
            evidence={
                "counterfactual_complete": True,
                "first_degraded_policy_tier": "LEVEL_2",
                "changed_order_count": 3,
            },
            limitations=LIMITATION,
        ),
    ]


def tracked_examples(seed: int = 42) -> dict[str, dict]:
    delivery = delivery_risk(DeliveryRiskRequest(
        delivery_ref="DEMO_DELIVERY_001", route_distance_km=26.0,
        planned_arrival_hour=16, dock_type="standard",
    ), seed=seed)
    fresh = demand_forecast(DemandForecastRequest(
        depot="Demo Depot", brand="Fresh", iso_year=2026, iso_week=42,
    ), seed=seed)
    style = demand_forecast(DemandForecastRequest(
        depot="Demo North Hub", brand="Style", iso_year=2026, iso_week=43,
    ), seed=seed)
    allocation = allocation_insight(AllocationInsightRequest(scenario_ref="DEMO_SCENARIO_01"))
    hard, policy = deferral_explanations()
    return {
        "task1_response.synthetic.json": delivery.model_dump(mode="json"),
        "demand_forecast_response.synthetic.json": fresh.model_dump(mode="json"),
        "demand_forecast_style_response.synthetic.json": style.model_dump(mode="json"),
        "allocation_response.synthetic.json": allocation.model_dump(mode="json"),
        "deferral_explanation.synthetic.json": hard.model_dump(mode="json"),
        "deferral_explanation_policy.synthetic.json": policy.model_dump(mode="json"),
    }
