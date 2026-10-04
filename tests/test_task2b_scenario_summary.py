"""Synthetic aggregate-only Phase 18 summary tests."""

from __future__ import annotations

from src.task2b.scenario import build_s1_scenario
from src.task2b.scenario_summary import build_scenario_summaries
from tests.test_task2b_scenario import _frames


def test_phase18_aggregate_summaries_reconcile_and_cover_required_views() -> None:
    scenario = build_s1_scenario(*_frames())
    summary = build_scenario_summaries(scenario["orders_s1"])
    assert summary["overall"]["order_count"] == 2
    assert int(summary["demand_by_brand"].order_count.sum()) == 2
    assert int(summary["demand_by_district"].order_count.sum()) == 2
    assert summary["chilled"]["chilled_order_count"] == 1
    assert "brand_count" in summary["demand_by_district"]
    assert "chilled_by_brand_district" in summary
    assert summary["van_only"]["van_only_chilled_order_count"] == 1
    assert "van_only_by_brand_district" in summary
    assert summary["deferred_yesterday"]["count"] == 1
    assert "deferred_by_temp_requirement" in summary and "days_by_deferred_yesterday" in summary
    assert summary["days_since_last_served"]["p90"] >= summary["days_since_last_served"]["median"]
