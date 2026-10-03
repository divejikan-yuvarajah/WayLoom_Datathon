from __future__ import annotations

import pandas as pd
import pytest

from src.task1.labels import (
    ELIGIBLE_DISPATCHED,
    EXPECTED_EXCLUDED_NOT_RUN,
    TASK1_FORBIDDEN_DIRECT_FEATURES,
    Task1EligibilityBlockerError,
    Task1JoinBlockerError,
    assert_no_task1_direct_feature_leakage,
    build_task1_training_labels,
    classify_label_eligibility,
    compute_late_flag,
    compute_service_minutes,
    compute_service_start,
    combine_local_date_clock,
    detect_duplicate_join_matches,
    detect_unmatched_dispatched_and_orphan_legs,
    inspect_long_service_candidates,
    join_orders_to_route_legs,
    parse_clock,
    resolve_delivery_window_datetimes,
    resolve_local_datetime_columns,
    resolve_route_actual_datetimes,
    select_dispatched_orders,
    summarize_task1_targets,
    validate_outlet_destination_consistency,
    validate_task1_join_integrity,
    validate_task1_labels,
)


def _base_deliveries() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "dispatch_status": "attempted",
                "outlet_id": "OUT001",
                "route_id": "R001",
                "seq_in_route": 0,
            },
            {
                "delivery_id": "DEL002",
                "dispatch_status": "deferred",
                "outlet_id": "OUT002",
                "route_id": "R002",
                "seq_in_route": 1,
            },
            {
                "delivery_id": "DEL003",
                "dispatch_status": "not_run",
                "outlet_id": "OUT003",
                "route_id": "",
                "seq_in_route": pd.NA,
            },
        ],
        index=[100, 101, 102],
    )


def test_select_dispatched_orders_retains_attempted_and_deferred() -> None:
    deliveries = _base_deliveries()
    selected = select_dispatched_orders(deliveries)
    assert list(selected["dispatch_status"]) == ["attempted", "deferred"]
    assert list(selected["delivery_id"]) == ["DEL001", "DEL002"]


def test_select_dispatched_orders_excludes_not_run() -> None:
    deliveries = _base_deliveries()
    selected = select_dispatched_orders(deliveries)
    assert "not_run" not in set(selected["dispatch_status"])


def test_select_dispatched_orders_preserves_source_order_and_traceability() -> None:
    deliveries = _base_deliveries()
    selected = select_dispatched_orders(deliveries)
    assert list(selected.index) == [100, 101]
    assert list(selected["delivery_id"]) == ["DEL001", "DEL002"]


def test_select_dispatched_orders_does_not_mutate_input() -> None:
    deliveries = _base_deliveries()
    before = deliveries.copy(deep=True)
    _ = select_dispatched_orders(deliveries)
    pd.testing.assert_frame_equal(deliveries, before)


def test_classify_label_eligibility_marks_expected_exclusion_for_not_run() -> None:
    deliveries = _base_deliveries()
    classified = classify_label_eligibility(deliveries)
    status_by_id = dict(zip(classified["delivery_id"], classified["task1_label_eligibility"]))
    assert status_by_id["DEL003"] == EXPECTED_EXCLUDED_NOT_RUN


def test_classify_label_eligibility_marks_dispatched_rows_as_eligible_when_assignment_exists() -> None:
    deliveries = _base_deliveries()
    classified = classify_label_eligibility(deliveries)
    status_by_id = dict(zip(classified["delivery_id"], classified["task1_label_eligibility"]))
    assert status_by_id["DEL001"] == ELIGIBLE_DISPATCHED
    assert status_by_id["DEL002"] == ELIGIBLE_DISPATCHED


def test_classify_label_eligibility_raises_blocker_when_dispatched_route_id_missing() -> None:
    deliveries = _base_deliveries()
    deliveries.loc[100, "route_id"] = ""
    with pytest.raises(Task1EligibilityBlockerError):
        classify_label_eligibility(deliveries)


def test_classify_label_eligibility_raises_blocker_when_dispatched_seq_in_route_missing() -> None:
    deliveries = _base_deliveries()
    deliveries.loc[101, "seq_in_route"] = pd.NA
    with pytest.raises(Task1EligibilityBlockerError):
        classify_label_eligibility(deliveries)


def test_classify_label_eligibility_does_not_mutate_input() -> None:
    deliveries = _base_deliveries()
    before = deliveries.copy(deep=True)
    _ = classify_label_eligibility(deliveries)
    pd.testing.assert_frame_equal(deliveries, before)


def test_select_dispatched_orders_handles_trimmed_dispatch_status_values() -> None:
    deliveries = _base_deliveries()
    deliveries.loc[100, "dispatch_status"] = "attempted "
    selected = select_dispatched_orders(deliveries)
    assert list(selected["delivery_id"]) == ["DEL001", "DEL002"]


def test_classify_label_eligibility_rejects_missing_dispatch_status() -> None:
    deliveries = _base_deliveries()
    deliveries.loc[101, "dispatch_status"] = pd.NA
    with pytest.raises(ValueError, match="dispatch_status contains missing values"):
        classify_label_eligibility(deliveries)


def _route_legs_base() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "leg_id": "LEG001",
                "route_id": "R001",
                "seq": 0,
                "to_outlet": "OUT001",
                "date": "2026-01-01",
                "arrival_time": "08:00",
                "leave_outlet_time": "08:15",
            },
            {
                "leg_id": "LEG002",
                "route_id": "R002",
                "seq": 1,
                "to_outlet": "OUT002",
                "date": "2026-01-01",
                "arrival_time": "09:00",
                "leave_outlet_time": "09:20",
            },
        ]
    )


def test_join_orders_to_route_legs_uses_official_composite_key_and_left_join() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    dispatched = dispatched[dispatched["delivery_id"].isin(["DEL001", "DEL002"])]
    route_legs = _route_legs_base()
    joined = join_orders_to_route_legs(dispatched, route_legs)

    assert list(joined["delivery_id"]) == ["DEL001", "DEL002"]
    assert list(joined["_merge"]) == ["both", "both"]
    assert list(joined["leg_id"]) == ["LEG001", "LEG002"]
    assert "source_row_index" in joined.columns


def test_join_orders_to_route_legs_keeps_unmatched_dispatched_rows_visible() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = _route_legs_base().iloc[[0]].copy()
    joined = join_orders_to_route_legs(dispatched, route_legs)
    merge_by_id = dict(zip(joined["delivery_id"], joined["_merge"]))
    assert merge_by_id["DEL001"] == "both"
    assert merge_by_id["DEL002"] == "left_only"


def test_join_orders_to_route_legs_accepts_same_seq_across_different_routes() -> None:
    dispatched = pd.DataFrame(
        [
            {"delivery_id": "DEL010", "dispatch_status": "attempted", "route_id": "RA", "seq_in_route": 0},
            {"delivery_id": "DEL011", "dispatch_status": "attempted", "route_id": "RB", "seq_in_route": 0},
        ],
        index=[10, 11],
    )
    route_legs = pd.DataFrame(
        [
            {"leg_id": "LEGA", "route_id": "RA", "seq": 0},
            {"leg_id": "LEGB", "route_id": "RB", "seq": 0},
        ]
    )
    joined = join_orders_to_route_legs(dispatched, route_legs)
    assert list(joined["_merge"]) == ["both", "both"]
    assert list(joined["leg_id"]) == ["LEGA", "LEGB"]


def test_join_orders_to_route_legs_raises_when_route_key_is_duplicated() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = pd.concat([_route_legs_base(), _route_legs_base().iloc[[0]]], ignore_index=True)
    with pytest.raises(Task1JoinBlockerError):
        join_orders_to_route_legs(dispatched, route_legs)


def test_join_orders_to_route_legs_raises_on_missing_join_columns() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = _route_legs_base().drop(columns=["seq"])
    with pytest.raises(Task1JoinBlockerError):
        join_orders_to_route_legs(dispatched, route_legs)


def test_join_orders_to_route_legs_raises_on_reserved_trace_column_collision() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    dispatched["source_row_index"] = dispatched.index
    with pytest.raises(Task1JoinBlockerError, match="reserved trace column"):
        join_orders_to_route_legs(dispatched, _route_legs_base())


def test_validate_task1_join_integrity_passes_for_perfect_match() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    summary = validate_task1_join_integrity(joined, expected_dispatched_count=len(dispatched))
    assert summary["joined_row_count"] == len(dispatched)
    assert summary["duplicate_delivery_count"] == 0
    assert summary["unmatched_count"] == 0
    assert summary["multiplied_rows_count"] == 0


def test_validate_task1_join_integrity_fails_when_unmatched_rows_exist() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base().iloc[[0]].copy())
    with pytest.raises(Task1JoinBlockerError, match="matched exactly one route leg"):
        validate_task1_join_integrity(joined, expected_dispatched_count=len(dispatched))


def test_validate_task1_join_integrity_fails_when_joined_row_count_mismatch() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    with pytest.raises(Task1JoinBlockerError, match="row count does not match"):
        validate_task1_join_integrity(joined.iloc[[0]].copy(), expected_dispatched_count=len(dispatched))


def test_validate_task1_join_integrity_fails_when_delivery_id_not_unique() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    broken = pd.concat([joined, joined.iloc[[0]].copy()], ignore_index=True)
    broken.loc[len(broken) - 1, "_merge"] = "both"
    with pytest.raises(Task1JoinBlockerError, match="delivery_id is not unique"):
        validate_task1_join_integrity(broken, expected_dispatched_count=len(broken))


def test_dt059_detect_unmatched_dispatched_orders_raises_blocker() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base().iloc[[0]].copy())
    with pytest.raises(Task1JoinBlockerError, match="unmatched dispatched orders detected"):
        detect_unmatched_dispatched_and_orphan_legs(joined, _route_legs_base().iloc[[0]].copy())


def test_dt059_reports_orphan_route_legs_separately() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = pd.concat(
        [
            _route_legs_base(),
            pd.DataFrame(
                [
                    {
                        "leg_id": "LEG999",
                        "route_id": "R999",
                        "seq": 0,
                        "to_outlet": "OUT999",
                        "date": "2026-01-01",
                        "arrival_time": "11:00",
                        "leave_outlet_time": "11:10",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    joined = join_orders_to_route_legs(dispatched, route_legs)
    summary = detect_unmatched_dispatched_and_orphan_legs(joined, route_legs)
    assert summary["unmatched_dispatched_count"] == 0
    assert summary["orphan_route_leg_count"] == 1


def test_dt060_duplicate_join_checks_pass_on_clean_inputs() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = _route_legs_base()
    joined = join_orders_to_route_legs(dispatched, route_legs)
    summary = detect_duplicate_join_matches(dispatched, route_legs, joined)
    assert summary["duplicate_dispatched_key_count"] == 0
    assert summary["duplicate_route_key_count"] == 0
    assert summary["duplicate_delivery_count"] == 0
    assert summary["multiplied_rows_count"] == 0


def test_dt060_duplicate_join_checks_fail_on_duplicate_route_key() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    route_legs = pd.concat([_route_legs_base(), _route_legs_base().iloc[[0]]], ignore_index=True)
    joined = pd.DataFrame(
        [
            {"delivery_id": "DEL001", "source_row_index": 100},
            {"delivery_id": "DEL002", "source_row_index": 101},
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="duplicate route leg"):
        detect_duplicate_join_matches(dispatched, route_legs, joined)


def test_dt060_duplicate_join_checks_fail_on_duplicate_dispatched_key() -> None:
    dispatched = pd.DataFrame(
        [
            {"delivery_id": "DEL001", "dispatch_status": "attempted", "route_id": "R001", "seq_in_route": 0},
            {"delivery_id": "DEL002", "dispatch_status": "deferred", "route_id": "R001", "seq_in_route": 0},
        ]
    )
    route_legs = _route_legs_base()
    joined = pd.DataFrame(
        [
            {"delivery_id": "DEL001", "source_row_index": 1},
            {"delivery_id": "DEL002", "source_row_index": 2},
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="duplicate dispatched"):
        detect_duplicate_join_matches(dispatched, route_legs, joined)


def test_dt060_same_seq_different_route_is_valid() -> None:
    dispatched = pd.DataFrame(
        [
            {"delivery_id": "DEL010", "dispatch_status": "attempted", "route_id": "RA", "seq_in_route": 0},
            {"delivery_id": "DEL011", "dispatch_status": "attempted", "route_id": "RB", "seq_in_route": 0},
        ]
    )
    route_legs = pd.DataFrame(
        [
            {"leg_id": "LEGA", "route_id": "RA", "seq": 0},
            {"leg_id": "LEGB", "route_id": "RB", "seq": 0},
        ]
    )
    joined = join_orders_to_route_legs(dispatched, route_legs)
    summary = detect_duplicate_join_matches(dispatched, route_legs, joined)
    assert summary["duplicate_route_key_count"] == 0
    assert summary["duplicate_dispatched_key_count"] == 0


def test_dt061_outlet_destination_consistency_passes() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    summary = validate_outlet_destination_consistency(joined)
    assert summary["destination_mismatch_count"] == 0
    assert summary["matched_rows"] == 2


def test_dt061_outlet_destination_consistency_fails_on_mismatch() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    joined.loc[joined["delivery_id"] == "DEL002", "to_outlet"] = "OUT999"
    with pytest.raises(Task1JoinBlockerError, match="destination mismatch"):
        validate_outlet_destination_consistency(joined)


def test_dt062_parse_clock_valid_cases() -> None:
    assert parse_clock("00:00") == (0, 0)
    assert parse_clock("07:10") == (7, 10)
    assert parse_clock("23:59") == (23, 59)


def test_dt062_parse_clock_rejects_invalid_values() -> None:
    with pytest.raises(Task1JoinBlockerError, match="Invalid clock value"):
        parse_clock("24:00")
    with pytest.raises(Task1JoinBlockerError, match="Invalid clock format"):
        parse_clock("7:10")
    with pytest.raises(Task1JoinBlockerError, match="Invalid clock format"):
        parse_clock("0710")


def test_dt062_combine_local_date_clock() -> None:
    ts = combine_local_date_clock("2026-01-06", "07:10")
    assert str(ts) == "2026-01-06 07:10:00"


def test_dt062_resolve_local_datetime_columns_preserves_raw_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "date": "2026-01-06",
                "actual_depart_time": "07:30",
                "arrival_time": "08:00",
                "leave_outlet_time": "08:15",
                "window_open_time": "07:00",
                "window_close_time": "10:00",
            }
        ]
    )
    before = df.copy(deep=True)
    resolved = resolve_local_datetime_columns(
        df,
        date_column="date",
        clock_columns=[
            "actual_depart_time",
            "arrival_time",
            "leave_outlet_time",
            "window_open_time",
            "window_close_time",
        ],
        required_clock_columns=["actual_depart_time", "arrival_time", "leave_outlet_time"],
    )

    pd.testing.assert_frame_equal(df, before)
    assert "actual_depart_time_dt" in resolved.columns
    assert "arrival_time_dt" in resolved.columns
    assert "leave_outlet_time_dt" in resolved.columns
    assert "window_open_time_dt" in resolved.columns
    assert "window_close_time_dt" in resolved.columns
    assert str(resolved.loc[0, "arrival_time_dt"]) == "2026-01-06 08:00:00"


def test_dt062_required_blank_actual_time_fails() -> None:
    df = pd.DataFrame(
        [
            {
                "date": "2026-01-06",
                "actual_depart_time": "",
                "arrival_time": "08:00",
                "leave_outlet_time": "08:15",
            }
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="required clock column actual_depart_time"):
        resolve_local_datetime_columns(
            df,
            date_column="date",
            clock_columns=["actual_depart_time", "arrival_time", "leave_outlet_time"],
            required_clock_columns=["actual_depart_time", "arrival_time", "leave_outlet_time"],
        )


def test_dt063_resolve_route_actual_datetimes_daytime_route() -> None:
    route_legs = pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": 0,
                "date": "2026-01-06",
                "actual_depart_time": "07:30",
                "arrival_time": "08:00",
                "leave_outlet_time": "08:15",
                "actual_travel_duration_min": 30.0,
            }
        ]
    )
    resolved = resolve_route_actual_datetimes(route_legs, travel_tolerance_min=0.5)
    assert str(resolved.loc[0, "actual_depart_time_dt"]) == "2026-01-06 07:30:00"
    assert str(resolved.loc[0, "arrival_time_dt"]) == "2026-01-06 08:00:00"
    assert str(resolved.loc[0, "leave_outlet_time_dt"]) == "2026-01-06 08:15:00"
    assert resolved.loc[0, "arrival_day_offset"] == 0


def test_dt063_orders_text_sequences_numerically_for_route_chronology() -> None:
    route_legs = pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": "10",
                "date": "2026-01-06",
                "actual_depart_time": "07:20",
                "arrival_time": "07:30",
                "leave_outlet_time": "07:35",
                "actual_travel_duration_min": 10.0,
            },
            {
                "route_id": "R1",
                "seq": "2",
                "date": "2026-01-06",
                "actual_depart_time": "07:00",
                "arrival_time": "07:10",
                "leave_outlet_time": "07:15",
                "actual_travel_duration_min": 10.0,
            },
        ],
        index=[10, 2],
    )
    resolved = resolve_route_actual_datetimes(route_legs, travel_tolerance_min=0.5)

    assert str(resolved.loc[2, "arrival_time_dt"]) == "2026-01-06 07:10:00"
    assert str(resolved.loc[10, "arrival_time_dt"]) == "2026-01-06 07:30:00"


def test_dt063_resolve_route_actual_datetimes_midnight_rollover() -> None:
    route_legs = pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": 0,
                "date": "2026-01-06",
                "actual_depart_time": "23:50",
                "arrival_time": "00:10",
                "leave_outlet_time": "00:30",
                "actual_travel_duration_min": 20.0,
            }
        ]
    )
    resolved = resolve_route_actual_datetimes(route_legs, travel_tolerance_min=0.5)
    assert str(resolved.loc[0, "actual_depart_time_dt"]) == "2026-01-06 23:50:00"
    assert str(resolved.loc[0, "arrival_time_dt"]) == "2026-01-07 00:10:00"
    assert str(resolved.loc[0, "leave_outlet_time_dt"]) == "2026-01-07 00:30:00"
    assert resolved.loc[0, "arrival_day_offset"] == 1


def test_dt063_window_anchor_and_cross_midnight_window() -> None:
    route_legs = pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": 0,
                "date": "2026-01-06",
                "actual_depart_time": "23:50",
                "arrival_time": "00:10",
                "leave_outlet_time": "00:30",
                "actual_travel_duration_min": 20.0,
                "window_open_time": "23:00",
                "window_close_time": "01:00",
            }
        ]
    )
    resolved_route = resolve_route_actual_datetimes(route_legs, travel_tolerance_min=0.5)
    resolved_windows = resolve_delivery_window_datetimes(resolved_route)
    assert str(resolved_windows.loc[0, "window_open_dt"]) == "2026-01-06 23:00:00"
    assert str(resolved_windows.loc[0, "window_close_dt"]) == "2026-01-07 01:00:00"


def test_dt063_impossible_chronology_raises_on_travel_conflict() -> None:
    route_legs = pd.DataFrame(
        [
            {
                "route_id": "R1",
                "seq": 0,
                "date": "2026-01-06",
                "actual_depart_time": "23:50",
                "arrival_time": "00:10",
                "leave_outlet_time": "00:30",
                "actual_travel_duration_min": 5.0,
            }
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="chronology conflicts"):
        resolve_route_actual_datetimes(route_legs, travel_tolerance_min=1.0)


def test_dt064_service_start_uses_max_of_arrival_and_window_open() -> None:
    df = pd.DataFrame(
        [
            {
                "arrival_time_dt": pd.Timestamp("2026-01-06 07:10:00"),
                "window_open_dt": pd.Timestamp("2026-01-06 07:30:00"),
            },
            {
                "arrival_time_dt": pd.Timestamp("2026-01-06 07:40:00"),
                "window_open_dt": pd.Timestamp("2026-01-06 07:30:00"),
            },
        ]
    )
    resolved = compute_service_start(df)
    assert str(resolved.loc[0, "service_start_dt"]) == "2026-01-06 07:30:00"
    assert str(resolved.loc[1, "service_start_dt"]) == "2026-01-06 07:40:00"


def test_dt065_service_minutes_excludes_early_waiting_official_example() -> None:
    df = pd.DataFrame(
        [
            {
                "service_start_dt": pd.Timestamp("2026-01-06 07:30:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 07:50:00"),
            }
        ]
    )
    resolved = compute_service_minutes(df)
    assert resolved.loc[0, "service_minutes"] == 20.0


def test_dt065_service_minutes_late_and_midnight_cases() -> None:
    df = pd.DataFrame(
        [
            {
                "service_start_dt": pd.Timestamp("2026-01-06 08:10:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:32:00"),
            },
            {
                "service_start_dt": pd.Timestamp("2026-01-06 23:55:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-07 00:20:00"),
            },
        ]
    )
    resolved = compute_service_minutes(df)
    assert resolved.loc[0, "service_minutes"] == 22.0
    assert resolved.loc[1, "service_minutes"] == 25.0


def test_dt065_service_minutes_negative_raises() -> None:
    df = pd.DataFrame(
        [
            {
                "service_start_dt": pd.Timestamp("2026-01-06 08:30:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:20:00"),
            }
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="cannot be negative"):
        compute_service_minutes(df)


def test_dt066_late_flag_strict_boundary() -> None:
    df = pd.DataFrame(
        [
            {
                "arrival_time_dt": pd.Timestamp("2026-01-06 07:59:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
            },
            {
                "arrival_time_dt": pd.Timestamp("2026-01-06 08:00:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
            },
            {
                "arrival_time_dt": pd.Timestamp("2026-01-06 08:01:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
            },
        ]
    )
    resolved = compute_late_flag(df)
    assert list(resolved["late_flag"]) == [0, 0, 1]


def test_dt067_validate_task1_labels_passes_for_valid_fixture() -> None:
    dispatched = select_dispatched_orders(_base_deliveries())
    joined = join_orders_to_route_legs(dispatched, _route_legs_base())
    enriched = resolve_route_actual_datetimes(
        pd.DataFrame(
            [
                {
                    "route_id": "R001",
                    "seq": 0,
                    "date": "2026-01-06",
                    "actual_depart_time": "07:30",
                    "arrival_time": "08:00",
                    "leave_outlet_time": "08:15",
                    "actual_travel_duration_min": 30.0,
                    "window_open_time": "07:00",
                    "window_close_time": "10:00",
                }
            ]
        ),
        travel_tolerance_min=0.5,
    )
    enriched = resolve_delivery_window_datetimes(enriched)
    enriched = compute_service_start(enriched)
    enriched = compute_service_minutes(enriched)
    enriched = compute_late_flag(enriched)
    enriched["delivery_id"] = ["DEL001"]
    enriched["_merge"] = ["both"]
    summary = validate_task1_labels(enriched)
    assert summary["row_count"] == 1
    assert summary["matched_dispatched_count"] == 1
    assert summary["late_count"] == 0
    assert summary["on_time_count"] == 1


def test_dt067_validate_task1_labels_fails_on_bad_late_flag() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "arrival_time_dt": pd.Timestamp("2026-01-06 08:01:00"),
                "window_open_dt": pd.Timestamp("2026-01-06 07:00:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
                "service_start_dt": pd.Timestamp("2026-01-06 08:01:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:20:00"),
                "service_minutes": 19.0,
                "late_flag": 0,
                "_merge": "both",
            }
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="late_flag"):
        validate_task1_labels(df)


def test_dt067_validate_task1_labels_fails_on_duplicate_delivery_id() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "arrival_time_dt": pd.Timestamp("2026-01-06 08:01:00"),
                "window_open_dt": pd.Timestamp("2026-01-06 07:00:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
                "service_start_dt": pd.Timestamp("2026-01-06 08:01:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:20:00"),
                "service_minutes": 19.0,
                "late_flag": 1,
                "_merge": "both",
            },
            {
                "delivery_id": "DEL001",
                "arrival_time_dt": pd.Timestamp("2026-01-06 08:02:00"),
                "window_open_dt": pd.Timestamp("2026-01-06 07:00:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
                "service_start_dt": pd.Timestamp("2026-01-06 08:02:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:22:00"),
                "service_minutes": 20.0,
                "late_flag": 1,
                "_merge": "both",
            },
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="delivery_id must be unique"):
        validate_task1_labels(df)


def test_dt067_validate_task1_labels_rejects_missing_datetime_or_late_flag() -> None:
    df = pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "arrival_time_dt": pd.NaT,
                "window_open_dt": pd.Timestamp("2026-01-06 07:00:00"),
                "window_close_dt": pd.Timestamp("2026-01-06 08:00:00"),
                "service_start_dt": pd.Timestamp("2026-01-06 07:00:00"),
                "leave_outlet_time_dt": pd.Timestamp("2026-01-06 08:20:00"),
                "service_minutes": 80.0,
                "late_flag": pd.NA,
            }
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="arrival_time_dt contains missing"):
        validate_task1_labels(df)


def test_dt068_inspect_long_service_candidates() -> None:
    df = pd.DataFrame(
        [
            {"delivery_id": "A", "service_minutes": 10.0},
            {"delivery_id": "B", "service_minutes": 120.0},
            {"delivery_id": "C", "service_minutes": 5.0},
        ]
    )
    candidates = inspect_long_service_candidates(df, threshold_minutes=60.0)
    assert list(candidates["delivery_id"]) == ["B"]
    assert list(candidates["service_minutes"]) == [120.0]


def test_dt068_inspect_long_service_candidates_rejects_negative_threshold() -> None:
    df = pd.DataFrame([{"delivery_id": "A", "service_minutes": 10.0}])
    with pytest.raises(Task1JoinBlockerError, match="threshold_minutes"):
        inspect_long_service_candidates(df, threshold_minutes=-1.0)


def test_dt069_summarize_task1_targets() -> None:
    df = pd.DataFrame(
        [
            {"service_minutes": 20.0, "late_flag": 0},
            {"service_minutes": 22.0, "late_flag": 1},
            {"service_minutes": 24.0, "late_flag": 0},
        ]
    )
    summary = summarize_task1_targets(df)
    assert summary["service_minutes"]["count"] == 3
    assert summary["late_flag"]["late_count"] == 1
    assert summary["late_flag"]["not_late_count"] == 2
    assert summary["late_flag"]["late_rate"] == pytest.approx(1 / 3)


def test_dt069_summarize_task1_targets_rejects_non_binary_late_flag() -> None:
    df = pd.DataFrame(
        [
            {"service_minutes": 20.0, "late_flag": 2},
        ]
    )
    with pytest.raises(Task1JoinBlockerError, match="late_flag"):
        summarize_task1_targets(df)


def _deliveries_for_builder() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "delivery_id": "DEL001",
                "dispatch_status": "attempted",
                "route_id": "R001",
                "seq_in_route": 0,
                "outlet_id": "OUT001",
                "window_open_time": "07:00",
                "window_close_time": "10:00",
            },
            {
                "delivery_id": "DEL002",
                "dispatch_status": "not_run",
                "route_id": "",
                "seq_in_route": pd.NA,
                "outlet_id": "OUT003",
                "window_open_time": "08:00",
                "window_close_time": "11:00",
            },
        ]
    )


def _route_legs_for_builder() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "leg_id": "LEG001",
                "route_id": "R001",
                "seq": 0,
                "to_outlet": "OUT001",
                "date": "2026-01-06",
                "actual_depart_time": "07:30",
                "actual_travel_duration_min": 30.0,
                "arrival_time": "08:00",
                "leave_outlet_time": "08:15",
            }
        ]
    )


def test_dt070_task1_forbidden_feature_set_contract() -> None:
    assert TASK1_FORBIDDEN_DIRECT_FEATURES == {
        "actual_depart_time",
        "actual_travel_duration_min",
        "arrival_time",
        "leave_outlet_time",
        "service_start_dt",
        "service_minutes",
        "late_flag",
    }


def test_dt070_leakage_guard_rejects_forbidden_columns() -> None:
    with pytest.raises(Task1JoinBlockerError, match="feature leakage"):
        assert_no_task1_direct_feature_leakage(["order_units", "arrival_time"])


def test_dt070_leakage_guard_allows_safe_columns() -> None:
    assert_no_task1_direct_feature_leakage(["order_units", "window_open_time", "route_id"])


def test_dt071_build_task1_training_labels_passes_and_is_deterministic() -> None:
    deliveries = _deliveries_for_builder()
    route_legs = _route_legs_for_builder()
    deliveries_before = deliveries.copy(deep=True)
    route_legs_before = route_legs.copy(deep=True)

    labeled, diagnostics = build_task1_training_labels(
        deliveries_train=deliveries,
        route_legs_train=route_legs,
        travel_tolerance_min=0.5,
        long_service_threshold_minutes=30.0,
    )

    pd.testing.assert_frame_equal(deliveries, deliveries_before)
    pd.testing.assert_frame_equal(route_legs, route_legs_before)

    assert list(labeled["delivery_id"]) == ["DEL001"]
    assert "service_start_dt" in labeled.columns
    assert "service_minutes" in labeled.columns
    assert "late_flag" in labeled.columns
    assert diagnostics["join_integrity"]["unmatched_count"] == 0
    assert diagnostics["label_validation"]["row_count"] == 1
    assert diagnostics["target_summary"]["late_flag"]["late_count"] == 0

    labeled_again, diagnostics_again = build_task1_training_labels(
        deliveries_train=deliveries,
        route_legs_train=route_legs,
        travel_tolerance_min=0.5,
        long_service_threshold_minutes=30.0,
    )
    pd.testing.assert_frame_equal(labeled, labeled_again)
    assert diagnostics == diagnostics_again


def test_dt071_build_task1_training_labels_fails_on_unmatched_dispatched_order() -> None:
    deliveries = _deliveries_for_builder()
    route_legs = _route_legs_for_builder().assign(route_id="R999")
    with pytest.raises(Task1JoinBlockerError, match="matched exactly one route leg"):
        build_task1_training_labels(
            deliveries_train=deliveries,
            route_legs_train=route_legs,
            travel_tolerance_min=0.5,
        )
