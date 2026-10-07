from pathlib import Path

from scripts.validate_preprocessing_doc import validate_preprocessing


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "preprocessing.md"
MANIFEST = ROOT / "docs" / "preprocessing_manifest.yaml"


def _text() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def test_canonical_document_passes_validator_and_length_guidance():
    result = validate_preprocessing(DOCUMENT, MANIFEST)
    assert result["status"] == "PASS"
    assert result["task_count"] == 10
    assert 2500 <= result["word_count"] <= 4500
    assert result["word_count_guidance"] == "PASS"


def test_document_covers_inputs_joins_labels_and_cleaning():
    text = _text()
    for token in (
        "deliveries_train.csv", "route_legs_train.csv", "task1_test_inputs.csv",
        "route_legs_test.csv", "task2a_test_inputs.csv", "task2b_peak_day_scenarios.csv",
        "task2b_peak_day_fleet.csv", "outlets.csv", "vehicles.csv", "calendar.csv",
        "district_travel.csv", "service_allowance.csv", "submission_task1.csv",
        "submission_task2a.csv", "submission_task2b.csv",
        "deliveries_train.(route_id, seq_in_route)", "route_legs_train.(route_id, seq)",
        "service_start = max(actual arrival, window opening)",
        "service_minutes = leave_outlet_time - service_start",
        "late_flag = 1 only if actual arrival > window_close_time",
        "waiting before opening is **not service time**",
        "Arrival exactly at closing time is not late",
        "fail closed", "generic `drop invalid rows` rule",
    ):
        assert token.lower() in text.lower()


def test_document_covers_features_leakage_validation_and_models():
    text = _text().lower()
    for token in (
        "safe_core_plus_history", "planned_slack_to_close_min", "planned_early_wait_min",
        "chronology-safe history", "actual_depart_time", "actual_travel_duration_min",
        "arrival_time", "leave_outlet_time", "four expanding-window cross-validation folds",
        "catboost_regression_default", "catboost_classifier_default",
        "raw probability", "no platt or isotonic calibrator",
        "four deterministic rolling origins", "direct-global table",
        "ensemble_cb_lgb_total_equal_v1", "ensemble_cb_lgb_chilled_equal_v1",
    ):
        assert token in text


def test_document_covers_task2b_and_official_engineering_distinction():
    text = _text().lower()
    for token in (
        "does **not require a trained model**", "`order_ref` is the allocation key",
        "no return journey is added", "270 minutes", "480 minutes",
        "seven official rule groups", "wayloom engineering decision - not organizer priority",
        "or-tools cp-sat", "solver-neutral validator", "feasibility only; it does not prove optimality",
        "**official requirement.**", "**wayloom engineering decision",
    ):
        assert token in text
