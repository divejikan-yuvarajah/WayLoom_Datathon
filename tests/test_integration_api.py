from fastapi.testclient import TestClient

from src.integration.service import ROUTES, create_app


client = TestClient(create_app())


def test_health_contract_and_openapi():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {
        "status": "ok", "service": "wayloom-integration",
        "contract_version": "1.0.0", "mode": "synthetic_demo",
    }
    contract = client.get("/v1/contract").json()
    assert contract["contract_version"] == "1.0.0"
    assert contract["available_endpoints"] == list(ROUTES)
    assert client.get("/openapi.json").status_code == 200


def test_model_load_safe_and_rejects_paths():
    assert client.post("/v1/models/load", json={"load": True}).json()["real_models_loaded"] is False
    rejected = client.post("/v1/models/load", json={"load": True, "model_path": "secret"})
    assert rejected.status_code == 422
    assert set(rejected.json()["error"]) == {"code", "message", "request_id"}


def test_delivery_is_deterministic_and_rejects_actuals():
    request = {
        "delivery_ref": "DEMO_DELIVERY_001", "route_distance_km": 20,
        "planned_arrival_hour": 16, "dock_type": "standard",
    }
    first = client.post("/v1/delivery-risk", json=request)
    second = client.post("/v1/delivery-risk", json=request)
    assert first.status_code == 200 and first.json() == second.json()
    rejected = client.post("/v1/delivery-risk", json={**request, "arrival_time": "12:00"})
    assert rejected.status_code == 422
    assert "arrival_time" not in str(rejected.json())


def test_forecast_and_allocation_are_safe_aggregates():
    forecast = client.post("/v1/demand-forecast", json={
        "depot": "Demo North Hub", "brand": "Style", "iso_year": 2026,
        "iso_week": 42, "forecast_horizon": 1,
    })
    assert forecast.status_code == 200
    assert forecast.json()["pred_chilled_volume_m3"] == 0
    assert "row_id" not in forecast.text
    allocation = client.post("/v1/allocation-insight", json={"scenario_ref": "DEMO_SCENARIO_01"})
    assert allocation.status_code == 200
    text = allocation.text
    for forbidden in ("order_ref", "outlet_id", "vehicle_id", "trip_id"):
        assert forbidden not in text
    summary = allocation.json()["summary"]
    assert summary["orders_served"] + summary["orders_deferred"] == summary["orders_total"]


def test_deferral_examples_are_anonymized_and_noncausal():
    response = client.get("/v1/demo/deferral-explanations")
    assert response.status_code == 200
    assert {item["reason_class"] for item in response.json()} == {"UNAVOIDABLE_HARD", "POLICY_TRADEOFF"}
    assert all("not a real-world causal claim" in item["limitations"] for item in response.json())
