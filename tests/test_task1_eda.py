from __future__ import annotations

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.task1.eda import (
    Task1EdaBlockerError,
    assert_no_eda_feature_leakage,
    assign_planned_shift,
    build_eda_warnings,
    build_feature_candidate_table,
    build_planned_slack_minutes,
    compute_wilson_score_interval,
    load_task1_eda_config,
    summarize_continuous_vs_service,
    summarize_dow_context,
    summarize_late_rate,
    summarize_late_rate_by_group,
    summarize_monsoon_context,
    summarize_optional_context,
    summarize_route_position,
    summarize_service_by_group,
    summarize_service_by_outlet,
    summarize_service_distribution,
    summarize_shift_context,
    summarize_slack_vs_targets,
    validate_eda_input,
)


def _synthetic_eda_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "service_minutes": 15.0,
                "late_flag": 0,
                "brand": "Fresh",
                "dock_type": "rear_dock",
                "outlet_id": "OUT001",
                "district": "District1",
                "depot": "Peliyagoda",
                "order_units": 10,
                "order_weight_kg": 50.0,
                "order_volume_m3": 1.5,
                "seq_in_route": 0,
                "date": "2026-01-05",
                "planned_arrival_time": "08:00",
                "window_open_time": "07:00",
                "window_close_time": "09:00",
                "monsoon": 0,
                "dow": 0,
            },
            {
                "delivery_id": "DEL002",
                "service_minutes": 25.0,
                "late_flag": 1,
                "brand": "Style",
                "dock_type": "street",
                "outlet_id": "OUT002",
                "district": "District2",
                "depot": "Kandy",
                "order_units": 20,
                "order_weight_kg": 100.0,
                "order_volume_m3": 3.0,
                "seq_in_route": 1,
                "date": "2026-01-05",
                "planned_arrival_time": "13:30",
                "window_open_time": "12:00",
                "window_close_time": "13:00",
                "monsoon": 1,
                "dow": 0,
            },
            {
                "delivery_id": "DEL003",
                "service_minutes": 35.0,
                "late_flag": 0,
                "brand": "Tech",
                "dock_type": "mall_bay",
                "outlet_id": "OUT001",
                "district": "District1",
                "depot": "Peliyagoda",
                "order_units": 30,
                "order_weight_kg": 150.0,
                "order_volume_m3": 4.5,
                "seq_in_route": 2,
                "date": "2026-01-06",
                "planned_arrival_time": "19:00",
                "window_open_time": "18:00",
                "window_close_time": "20:00",
                "monsoon": 0,
                "dow": 1,
            },
        ]
    )


# Input Integrity & Leakage Guard
def test_validate_eda_input_passes_valid_data() -> None:
    df = _synthetic_eda_df()
    validate_eda_input(df)


def test_validate_eda_input_rejects_negative_service() -> None:
    df = _synthetic_eda_df()
    df.loc[0, "service_minutes"] = -5.0
    with pytest.raises(Task1EdaBlockerError, match="service_minutes cannot be negative"):
        validate_eda_input(df)


def test_validate_eda_input_rejects_nonfinite_service() -> None:
    df = _synthetic_eda_df()
    df.loc[0, "service_minutes"] = np.nan
    with pytest.raises(Task1EdaBlockerError, match="missing or non-numeric"):
        validate_eda_input(df)


def test_validate_eda_input_rejects_invalid_late_flag() -> None:
    df = _synthetic_eda_df()
    df.loc[0, "late_flag"] = 2
    with pytest.raises(Task1EdaBlockerError, match="strictly binary"):
        validate_eda_input(df)


def test_validate_eda_input_rejects_duplicate_delivery_id() -> None:
    df = _synthetic_eda_df()
    df.loc[1, "delivery_id"] = "DEL001"
    with pytest.raises(Task1EdaBlockerError, match="delivery_id must be unique"):
        validate_eda_input(df)


def test_assert_no_eda_feature_leakage_rejects_forbidden_actuals() -> None:
    with pytest.raises(Task1EdaBlockerError, match="forbidden actual journey fields"):
        assert_no_eda_feature_leakage(["brand", "actual_travel_duration_min"])

    with pytest.raises(Task1EdaBlockerError, match="forbidden actual journey fields"):
        assert_no_eda_feature_leakage(["arrival_time"])


# DT-072: Service Distribution
def test_dt072_service_distribution_metrics() -> None:
    df = _synthetic_eda_df()
    summary = summarize_service_distribution(df)
    assert summary["n"] == 3
    assert summary["min"] == 15.0
    assert summary["median"] == 25.0
    assert summary["max"] == 35.0
    assert summary["mean"] == 25.0
    assert summary["iqr"] == pytest.approx(10.0)


def test_dt072_service_distribution_empty_raises() -> None:
    df = _synthetic_eda_df().iloc[0:0]
    with pytest.raises(Task1EdaBlockerError, match="empty"):
        summarize_service_distribution(df)


# DT-073 & DT-074: Service by Group
def test_dt073_service_by_brand() -> None:
    df = _synthetic_eda_df()
    brand_summ = summarize_service_by_group(df, "brand", min_group_n=2)
    assert len(brand_summ) == 3
    brand_dict = {d["brand"]: d for d in brand_summ}
    assert brand_dict["Fresh"]["n"] == 1
    assert brand_dict["Fresh"]["median"] == 15.0
    assert brand_dict["Fresh"]["small_sample_warning"] is True


def test_dt074_service_by_dock_type() -> None:
    df = _synthetic_eda_df()
    dock_summ = summarize_service_by_group(df, "dock_type")
    assert len(dock_summ) == 3
    dock_dict = {d["dock_type"]: d for d in dock_summ}
    assert dock_dict["rear_dock"]["median"] == 15.0


# DT-075: Service by Outlet
def test_dt075_service_by_outlet_safeguards() -> None:
    df = _synthetic_eda_df()
    outlet_summ = summarize_service_by_outlet(df, min_group_n=2)
    assert outlet_summ["target_encoding_created"] is False
    assert outlet_summ["unique_outlets"] == 2
    assert outlet_summ["small_sample_outlets"] == 1  # OUT002 has n=1 < 2


# DT-076, 077, 078: Continuous Predictors vs Service
def test_dt076_service_vs_units_spearman() -> None:
    df = _synthetic_eda_df()
    res = summarize_continuous_vs_service(df, "order_units", num_bins=2)
    assert res["valid_pairs"] == 3
    assert res["spearman_rho"] == pytest.approx(1.0)
    assert res["constant_feature"] is False
    assert len(res["binned_summary"]) > 0


def test_dt076_constant_feature_handling() -> None:
    df = _synthetic_eda_df()
    df["constant_col"] = 10.0
    res = summarize_continuous_vs_service(df, "constant_col")
    assert res["constant_feature"] is True
    assert res["spearman_rho"] is None


# DT-079: Overall Lateness & Wilson Interval
def test_dt079_overall_lateness() -> None:
    df = _synthetic_eda_df()
    late_summary = summarize_late_rate(df)
    assert late_summary["n"] == 3
    assert late_summary["late_count"] == 1
    assert late_summary["not_late_count"] == 2
    assert late_summary["late_rate"] == pytest.approx(1 / 3)
    w_low, w_high = late_summary["wilson_ci_95"]
    assert 0.0 <= w_low <= late_summary["late_rate"] <= w_high <= 1.0


def test_compute_wilson_interval_edges() -> None:
    assert compute_wilson_score_interval(0, 0) == (0.0, 0.0)
    low, high = compute_wilson_score_interval(10, 10)
    assert low > 0.60
    assert high == pytest.approx(1.0)


# DT-080, 081, 082: Lateness by Group
def test_dt080_to_082_late_by_group() -> None:
    df = _synthetic_eda_df()
    res_brand = summarize_late_rate_by_group(df, "brand")
    b_map = {d["brand"]: d["late_rate"] for d in res_brand}
    assert b_map["Fresh"] == 0.0
    assert b_map["Style"] == 1.0

    res_depot = summarize_late_rate_by_group(df, "depot")
    d_map = {d["depot"]: d["late_rate"] for d in res_depot}
    assert d_map["Peliyagoda"] == 0.0
    assert d_map["Kandy"] == 1.0


# DT-083: Route Position
def test_dt083_route_position() -> None:
    df = _synthetic_eda_df()
    pos_summ = summarize_route_position(df)
    first_vs_later = {d["stop_type"]: d for d in pos_summ["first_vs_later"]}
    assert first_vs_later["first_stop (seq=0)"]["n"] == 1
    assert first_vs_later["first_stop (seq=0)"]["late_rate"] == 0.0
    assert first_vs_later["later_stop (seq>0)"]["n"] == 2


# DT-084: Planned Slack (Leakage-Safe)
def test_dt084_planned_slack_calculation() -> None:
    df = _synthetic_eda_df()
    slack_s = build_planned_slack_minutes(df)
    # DEL001: arrival 08:00, close 09:00 -> +60 min
    # DEL002: arrival 13:30, close 13:00 -> -30 min
    # DEL003: arrival 19:00, close 20:00 -> +60 min
    assert list(slack_s) == [60.0, -30.0, 60.0]

    slack_summ = summarize_slack_vs_targets(df, slack_s)
    assert slack_summ["n"] == 3
    assert slack_summ["slack_distribution"]["negative_slack_count"] == 1
    assert slack_summ["slack_distribution"]["positive_slack_count"] == 2


def test_dt084_planned_slack_cross_midnight_window() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "DEL010",
                "service_minutes": 20.0,
                "late_flag": 0,
                "date": "2026-01-05",
                "planned_arrival_time": "23:30",
                "window_open_time": "22:00",
                "window_close_time": "02:00",  # crosses midnight
            }
        ]
    )
    slack_s = build_planned_slack_minutes(df)
    # 23:30 on 2026-01-05 to 02:00 on 2026-01-06 is 150 min
    assert slack_s.iloc[0] == 150.0


def test_dt084_planned_slack_zero_slack() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "DEL020",
                "service_minutes": 10.0,
                "late_flag": 0,
                "date": "2026-01-05",
                "planned_arrival_time": "10:00",
                "window_open_time": "08:00",
                "window_close_time": "10:00",
            }
        ]
    )
    slack_s = build_planned_slack_minutes(df)
    assert slack_s.iloc[0] == 0.0


def test_dt084_planned_slack_never_uses_actual_arrival() -> None:
    df = _synthetic_eda_df()
    df["arrival_time"] = "09:30"
    with pytest.raises(Task1EdaBlockerError, match="cannot use actual arrival_time"):
        build_planned_slack_minutes(df, planned_arrival_col="arrival_time")


# DT-085 & DT-086: Environmental Context Coverage
def test_dt085_and_dt086_disabled_state() -> None:
    df = _synthetic_eda_df()
    res = summarize_optional_context(df, "disruption_index", status="DISABLED")
    assert res["status"] == "NOT_APPLICABLE / DISABLED"
    assert res["coverage_n"] == 0
    assert res["coverage_rate"] == 0.0


# DT-087 & DT-088: Monsoon and DOW
def test_dt087_monsoon_context() -> None:
    df = _synthetic_eda_df()
    m_summ = summarize_monsoon_context(df)
    assert len(m_summ) == 2


def test_dt088_dow_context_order() -> None:
    df = _synthetic_eda_df()
    dow_summ = summarize_dow_context(df)
    assert len(dow_summ) == 7
    assert dow_summ[0]["day_name"] == "Monday"
    assert dow_summ[6]["day_name"] == "Sunday"


# DT-089: Planned Shift Classification
def test_dt089_assign_planned_shift_boundaries() -> None:
    clocks = pd.Series(["00:00", "05:59", "06:00", "11:59", "12:00", "17:59", "18:00", "23:59"])
    shifts = assign_planned_shift(clocks)
    expected = [
        "overnight",
        "overnight",
        "morning",
        "morning",
        "afternoon",
        "afternoon",
        "evening",
        "evening",
    ]
    assert list(shifts) == expected


def test_dt089_shift_context_summary() -> None:
    df = _synthetic_eda_df()
    shifts = assign_planned_shift(df["planned_arrival_time"])
    summ = summarize_shift_context(df, shifts)
    assert len(summ) == 3


# DT-090: Feature Candidates & Leakage Guard
def test_dt090_feature_candidate_table_marks_actuals_disabled() -> None:
    eda_summary = {
        "service_distribution": {"median": 20.0, "p99": 30.0},
        "lateness_overall": {"late_rate": 0.25},
        "service_by_outlet": {"small_sample_outlets": 0},
        "order_size_correlations": {},
    }
    candidates = build_feature_candidate_table(eda_summary)
    cand_map = {c["feature"]: c for c in candidates}

    # Verify actual journey features are marked DISABLE and prediction_time_safe = False
    for forbidden in ["actual_depart_time", "actual_travel_duration_min", "arrival_time", "leave_outlet_time"]:
        assert cand_map[forbidden]["prediction_time_safe"] is False
        assert cand_map[forbidden]["phase06_recommendation"] == "DISABLE"

    # Verify planned features are prediction_time_safe = True
    assert cand_map["brand"]["prediction_time_safe"] is True
    assert cand_map["planned_slack_min"]["prediction_time_safe"] is True


def test_dt090_eda_warnings_generation() -> None:
    eda_summary = {
        "service_distribution": {"median": 10.0, "p99": 60.0},  # Heavy tail > 3x median
        "lateness_overall": {"late_rate": 0.05},  # Imbalance < 0.20
        "service_by_outlet": {"small_sample_outlets": 5},
        "order_size_correlations": {"order_units_vs_order_weight_kg": 0.95},
        "road_context": {"status": "DISABLED", "coverage_rate": 0.0},
        "traffic_context": {"status": "DISABLED", "coverage_rate": 0.0},
    }
    warnings = build_eda_warnings(eda_summary)
    assert any("Heavy service-time" in w for w in warnings)
    assert any("imbalance" in w for w in warnings)
    assert any("outlets have fewer than" in w for w in warnings)
    assert any("High collinearity" in w for w in warnings)
