"""Fail-closed validation for the Phase 30 preprocessing document."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_preprocessing_manifest import TASK_IDS, build_manifest


REQUIRED_SECTIONS = (
    "official_requirement",
    "inputs",
    "joins",
    "task1_labels",
    "cleaning",
    "task1_features",
    "task1_leakage",
    "task1_validation",
    "task1_models",
    "task2a_history",
    "task2a_features",
    "task2a_validation",
    "task2a_models",
    "task2a_postprocessing",
    "task2b_inputs",
    "task2b_compatibility",
    "task2b_trip_time",
    "task2b_hard_rules",
    "task2b_priority",
    "task2b_validation",
    "outputs",
    "privacy",
    "task_completeness",
)
PLACEHOLDER_RE = re.compile(r"(?i)(?:<MODEL>|\bTBD\b|\bTODO(?:_MODEL)?\b|FINAL_MODEL_HERE|replace me)")
ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|Windows|Program Files)[\\/]|/(?:home|Users)/[^\s\"']+)")
PRIVATE_ID_RE = re.compile(r"\b(?:ORD\d{6,}|OUT\d{3,}|VEH\d{3,}|S1-\d{3,})\b")
SECRET_RE = re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9_\-]{12,}")
STALE_MODEL_RE = re.compile(r"(?i)\b(?:RandomForest|XGBoost|Prophet|LSTM)\b")
WORD_RE = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)


class PreprocessingValidationError(ValueError):
    """A Phase 30 documentation requirement failed."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreprocessingValidationError(f"Invalid YAML document: {path.name}")
    return value


def _require_tokens(text: str, tokens: list[str], label: str) -> None:
    lowered = text.lower()
    missing = [token for token in tokens if token.lower() not in lowered]
    if missing:
        raise PreprocessingValidationError(
            f"{label} is missing required semantics: {', '.join(missing)}"
        )


def _validate_manifest(manifest: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_SECTIONS if key not in manifest]
    if missing:
        raise PreprocessingValidationError("Manifest sections missing: " + ", ".join(missing))
    expected = build_manifest()
    if manifest != expected:
        differing = [key for key in expected if manifest.get(key) != expected.get(key)]
        raise PreprocessingValidationError(
            "Preprocessing manifest drift detected: " + ", ".join(differing)
        )
    if sorted(manifest["task_completeness"]) != TASK_IDS:
        raise PreprocessingValidationError("Task completeness must map DT-379 through DT-388.")
    if len(manifest["task2b_hard_rules"]) != 7:
        raise PreprocessingValidationError("Task 2B must document exactly seven hard-rule groups.")


def _validate_document(text: str, manifest: dict[str, Any]) -> None:
    headings = [
        "# WayLoom Datathon - Data Preprocessing and Methodology",
        "## 1. Purpose and scope",
        "## 2. Input datasets",
        "## 3. Shared data preparation and quality controls",
        "## 4. Task 1 - service-time and lateness preparation",
        "### 4.1 joins",
        "### 4.2 label construction",
        "### 4.3 cleaning",
        "### 4.4 feature engineering",
        "### 4.5 leakage prevention",
        "### 4.6 validation",
        "### 4.7 final model rationale",
        "## 5. Task 2A - depot demand forecasting",
        "### 5.1 demand-history construction",
        "### 5.2 weekly aggregation",
        "### 5.3 cleaning",
        "### 5.4 forecasting features",
        "### 5.5 leakage prevention",
        "### 5.6 rolling validation",
        "### 5.7 final forecasting methodology and model rationale",
        "## 6. Task 2B - peak-day allocation preparation",
        "### 6.1 scenario inputs",
        "### 6.2 compatibility preparation",
        "### 6.3 trip-time calculation",
        "### 6.4 hard-feasibility preparation",
        "### 6.5 WayLoom priority preparation",
        "### 6.6 optimizer / independent validation / official export",
        "## 7. Reproducibility and data-safety controls",
        "## 8. Final preprocessing summary",
    ]
    _require_tokens(text, headings, "preprocessing document structure")
    _require_tokens(
        text,
        [
            "deliveries_train.csv",
            "route_legs_train.csv",
            "task1_test_inputs.csv",
            "route_legs_test.csv",
            "task2a_test_inputs.csv",
            "task2b_peak_day_scenarios.csv",
            "task2b_peak_day_fleet.csv",
            "outlets.csv",
            "vehicles.csv",
            "calendar.csv",
            "district_travel.csv",
            "service_allowance.csv",
            "submission_task1.csv",
            "submission_task2a.csv",
            "submission_task2b.csv",
        ],
        "input dataset inventory",
    )
    _require_tokens(
        text,
        [
            "deliveries_train.(route_id, seq_in_route)",
            "route_legs_train.(route_id, seq)",
            "task1_test_inputs.(route_id, seq_in_route)",
            "route_legs_test.(route_id, seq)",
            "service_start = max(actual arrival, window opening)",
            "service_minutes = leave_outlet_time - service_start",
            "late_flag = 1 only if actual arrival > window_close_time",
            "waiting before opening is **not service time**",
            "arrival exactly at closing time is not late",
            "deterministic route-sequence rollover",
            "actual_depart_time",
            "actual_travel_duration_min",
            "arrival_time",
            "leave_outlet_time",
            "safe_core_plus_history",
            "chronological",
            manifest["task1_models"]["service_config_id"],
            manifest["task1_models"]["lateness_config_id"],
            "no platt or isotonic calibrator",
        ],
        "Task 1 methodology",
    )
    _require_tokens(
        text,
        [
            "uses both `deliveries_train.csv` and `task1_test_inputs.csv`",
            "attempted`, `deferred`, and `not_run",
            "requested `order_date`",
            "`iso_year` and `iso_week`",
            "Style and Tech chilled demand is exactly zero",
            "direct-global table",
            "1, 2, 4, 13, 52",
            "4, 8, 13",
            "four deterministic rolling origins",
            "next 10 weeks",
            manifest["task2a_models"]["total_config_id"],
            manifest["task2a_models"]["chilled_config_id"],
            "clips negative total/chilled predictions to zero",
            "caps chilled at total",
        ],
        "Task 2A methodology",
    )
    _require_tokens(
        text,
        [
            "does **not require a trained model**",
            "`order_ref` is the allocation key",
            "only available vehicles",
            "workshop vehicles are excluded",
            "chilled orders require reefer",
            "`van_only` outlets require a van",
            "same brand and district",
            "no split is allowed",
            "trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)",
            "No return journey is added",
            "270 minutes",
            "480 minutes",
            "Fuel quota and delivery window are not Task 2B hard constraints",
            "WayLoom engineering decision - not organizer priority",
            "OR-Tools CP-SAT",
            "All nine stages must be `OPTIMAL`",
            "feasibility only; it does not prove optimality",
            "`scenario`, `order_ref`, `outlet_id`, `decision`, `vehicle_id`, and `trip_id`",
        ],
        "Task 2B methodology",
    )
    _require_tokens(
        text,
        [
            "**Official requirement.**",
            "**WayLoom engineering decision",
            "architecture/high_level_datathon.svg",
            "architecture/task1_pipeline.svg",
            "architecture/task2a_forecasting.svg",
            "architecture/task2b_optimization.svg",
            "no private competition row",
        ],
        "official/engineering and privacy framing",
    )


def _validate_privacy(text: str) -> None:
    for pattern, label in (
        (PLACEHOLDER_RE, "placeholder"),
        (ABSOLUTE_PATH_RE, "absolute local path"),
        (PRIVATE_ID_RE, "private-looking identifier"),
        (SECRET_RE, "secret-like value"),
        (STALE_MODEL_RE, "stale model family"),
    ):
        if pattern.search(text):
            raise PreprocessingValidationError(f"{label} found in Phase 30 artifacts.")
    if "reports/private" in text.lower():
        raise PreprocessingValidationError("Private report path/content found in Phase 30 artifacts.")


def validate_preprocessing(document_path: Path, manifest_path: Path) -> dict[str, Any]:
    expected_document = (ROOT / "docs" / "preprocessing.md").resolve()
    expected_manifest = (ROOT / "docs" / "preprocessing_manifest.yaml").resolve()
    if document_path.resolve() != expected_document or manifest_path.resolve() != expected_manifest:
        raise PreprocessingValidationError("Phase 30 validation requires canonical document paths.")
    if not document_path.is_file() or document_path.stat().st_size == 0:
        raise PreprocessingValidationError("Preprocessing document is missing or empty.")
    if not manifest_path.is_file() or manifest_path.stat().st_size == 0:
        raise PreprocessingValidationError("Preprocessing manifest is missing or empty.")
    manifest = _load_yaml(manifest_path)
    _validate_manifest(manifest)
    document_text = document_path.read_text(encoding="utf-8")
    _validate_document(document_text, manifest)
    _validate_privacy(document_text + "\n" + manifest_path.read_text(encoding="utf-8"))
    word_count = len(WORD_RE.findall(document_text))
    if word_count < 1500:
        guidance = "WARNING - LIKELY TOO SHALLOW"
    elif word_count > 5500:
        guidance = 'WARNING - TOO LONG FOR "BRIEF WRITE-UP"'
    elif 2500 <= word_count <= 4500:
        guidance = "PASS"
    else:
        guidance = "ACCEPTABLE OUTSIDE RECOMMENDED BAND"
    return {
        "status": "PASS",
        "task_count": len(manifest["task_completeness"]),
        "input_count": len(manifest["inputs"]),
        "word_count": word_count,
        "word_count_guidance": guidance,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = validate_preprocessing(args.document, args.manifest)
    print("LOCAL PHASE 30 PREPROCESSING DOCUMENT VALIDATION: PASS")
    print(f"PHASE 30 TASK COVERAGE: {result['task_count']} / 10")
    print(f"DOCUMENTED INPUT ARTIFACTS: {result['input_count']}")
    print(f"DOCUMENT WORD COUNT: {result['word_count']}")
    print(f"WORD COUNT GUIDANCE: {result['word_count_guidance']}")
    print("FINAL MODEL CONFIG PARITY: PASS")
    print("OFFICIAL VS ENGINEERING DISTINCTION: PASS")
    print("PRIVATE DATA IN DOCUMENT: NO")
    print("FROZEN ARTIFACT INTEGRITY: NOT CHECKED BY THIS VALIDATOR")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
