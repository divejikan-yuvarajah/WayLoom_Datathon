"""Fail-closed validation for Phase 29 architecture documentation."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_architecture_manifest import (
    EXPECTED_OBJECTIVES,
    TASK1_OUTPUT_COLUMNS,
    TASK2A_OUTPUT_COLUMNS,
    TASK2B_OUTPUT_COLUMNS,
    build_manifest,
)


DIAGRAM_IDS = (
    "high_level_datathon",
    "task1_pipeline",
    "task2a_forecasting",
    "task2b_optimization",
    "proposed_deployment",
)
PLACEHOLDER_RE = re.compile(r"(?i)(?:<MODEL>|\bTBD\b|\bTODO(?:_MODEL)?\b|FINAL_MODEL_HERE|replace me)")
ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|Windows|Program Files)[\\/]|/(?:home|Users)/[^\s\"']+)")
PRIVATE_ID_RE = re.compile(r"\b(?:ORD\d{6,}|OUT\d{3,}|VEH\d{3,}|S1-\d{3,})\b")
SECRET_RE = re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9_\-]{12,}")
STALE_MODEL_RE = re.compile(r"(?i)\b(?:RandomForest|XGBoost|Prophet|LSTM)\b")


class ArchitectureValidationError(ValueError):
    """A Phase 29 architecture contract requirement failed."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ArchitectureValidationError(f"Invalid YAML document: {path.name}")
    return value


def _require_tokens(text: str, tokens: list[str], label: str) -> None:
    lowered = text.lower()
    missing = [token for token in tokens if token.lower() not in lowered]
    if missing:
        raise ArchitectureValidationError(f"{label} is missing required semantics: {', '.join(missing)}")


def _validate_manifest(manifest: dict[str, Any]) -> None:
    expected = build_manifest()
    for key in ("version", "phase", "status", "contains_private_data", "source_configs", "task1", "task2a", "task2b", "deployment", "diagrams"):
        if manifest.get(key) != expected.get(key):
            raise ArchitectureValidationError(f"Architecture manifest drift detected in {key}.")
    commit = manifest.get("source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,40}|unavailable", commit):
        raise ArchitectureValidationError("Architecture manifest source commit is invalid.")
    if manifest["task1"]["output_columns"] != TASK1_OUTPUT_COLUMNS:
        raise ArchitectureValidationError("Task 1 official output schema changed.")
    if manifest["task2a"]["output_columns"] != TASK2A_OUTPUT_COLUMNS:
        raise ArchitectureValidationError("Task 2A official output schema changed.")
    if manifest["task2b"]["output_columns"] != TASK2B_OUTPUT_COLUMNS:
        raise ArchitectureValidationError("Task 2B official output schema changed.")
    expected_levels = [f"{direction.upper()} {name}" for name, direction in EXPECTED_OBJECTIVES]
    if manifest["task2b"]["objective_levels"] != expected_levels:
        raise ArchitectureValidationError("Task 2B objective hierarchy changed.")


def _validate_sources(architecture_dir: Path, manifest: dict[str, Any]) -> dict[str, str]:
    source_text: dict[str, str] = {}
    titles = {item["diagram_id"]: item["title"] for item in manifest["diagrams"]}
    for diagram_id in DIAGRAM_IDS:
        path = architecture_dir / f"{diagram_id}.mmd"
        if not path.is_file() or path.stat().st_size == 0:
            raise ArchitectureValidationError(f"Missing Mermaid source: {path.name}")
        text = path.read_text(encoding="utf-8")
        source_text[diagram_id] = text
        _require_tokens(text, [
            f"diagram_id: {diagram_id}", f"title: {titles[diagram_id]}",
            "phase: 29", "status: final", "contains_private_data: false", "flowchart",
        ], path.name)

    _require_tokens(source_text["high_level_datathon"], [
        "private competition data", "schema validation", "task 1", "task 2a", "task 2b",
        "catboost service regressor", "catboost late classifier", "catboost and lightgbm",
        "cp-sat", "validated final artifacts", "final submission package target",
        "submission_task1.csv", "submission_task2a.csv", "submission_task2b.csv",
    ], "high-level diagram")

    _require_tokens(source_text["task1_pipeline"], [
        "service_start = max(actual arrival, window opening)",
        "service_minutes = leave_outlet_time - service_start",
        "late_flag = 1 only when actual arrival > window_close_time",
        "early waiting is not service", "arrival exactly at close is not late",
        "prediction-time feature boundary", "actual_depart_time", "actual_travel_duration_min",
        "arrival_time", "leave_outlet_time", "safe_core_plus_history",
        "catboost_regression_default", "catboost_classifier_default",
        "raw late probability", "negative service policy: fail", "no clipping",
        *TASK1_OUTPUT_COLUMNS,
    ], "Task 1 diagram")

    _require_tokens(source_text["task2a_forecasting"], [
        "deliveries_train", "task1_test_inputs", "unique delivery_id", "counted once",
        "deferred", "not_run", "requested order_date", "iso year", "iso week",
        "depot plus brand plus requested week", "fresh chilled demand only",
        "direct-global", "lags", "rolling means", "target-week", "h = 1 through 10",
        "rolling-origin", "ten-week", "no future leakage",
        "50/50 catboost plus lightgbm ensemble", "clip negatives", "cap chilled at total",
        "style and tech chilled to zero", *TASK2A_OUTPUT_COLUMNS,
    ], "Task 2A diagram")

    _require_tokens(source_text["task2b_optimization"], [
        "s1 peak-day orders", "scenario fleet status", "vehicle capability and capacity reference",
        "district outbound and inter-stop travel reference", "service allowance by brand plus dock_type",
        "order x vehicle compatibility", "trip minutes = outbound + inter-stop x orders minus one + sum service allowance",
        "no return leg", "1. same brand and district per trip", "2. chilled requires reefer",
        "3. van_only requires van", "4. home depot must match", "5. whole order; no split",
        "6. weight and volume capacity", "7. at most two trips", "fresh <= 270 min",
        "style plus tech <= 480 min", "wayloom soft priority - not organizer priority",
        "1 max served orders", "2 max previous-deferred served", "3 max waiting-days served",
        "4 max low-flexibility served", "5 max fresh chilled served", "6 max fresh served",
        "7a min avoidable reefer-van", "7b min avoidable reefer", "7c min avoidable van",
        "or-tools cp-sat", "all nine objective stages optimal", "deterministic evidence",
        "solver-neutral feasibility validator", "feasibility only; does not prove optimality",
        *TASK2B_OUTPUT_COLUMNS,
    ], "Task 2B diagram")

    _require_tokens(source_text["proposed_deployment"], [
        "proposed deployment", "not a claim of a live production system", "secure internal environment",
        "private operational data", "internal batch scheduler", "saved model artifacts",
        "task 1 catboost inference worker", "task 2a ensemble forecast worker",
        "task 2b local cp-sat optimizer worker", "controlled official submissions",
        "aggregate technical status", "no proprietary external modelling api",
        "no public row publication", "optional phase 28", "hackathon integration not required",
    ], "deployment diagram")
    return source_text


def _validate_svg(path: Path, source: Path, title: str) -> None:
    if not path.is_file() or path.stat().st_size < 500:
        raise ArchitectureValidationError(f"Missing or empty SVG export: {path.name}")
    text = path.read_text(encoding="utf-8")
    if "<svg" not in text or ("viewBox=" not in text and not ("width=" in text and "height=" in text)):
        raise ArchitectureValidationError(f"Invalid SVG structure: {path.name}")
    try:
        ElementTree.fromstring(text)
    except ElementTree.ParseError as error:
        raise ArchitectureValidationError(f"Malformed SVG: {path.name}") from error
    expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    _require_tokens(text, [
        f'id="wayloom-source-sha256">{expected_hash}<',
        f'id="wayloom-diagram-title">{title}<',
    ], path.name)
    if re.search(r"(?i)(?:href|src)=[\"']https?://", text):
        raise ArchitectureValidationError(f"Remote SVG asset reference found: {path.name}")
    if re.search(r"(?i)(?:data:image|base64,)", text):
        raise ArchitectureValidationError(f"Embedded raster content found: {path.name}")


def _validate_privacy(files: list[Path]) -> None:
    for path in files:
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_RE.search(text):
            raise ArchitectureValidationError(f"Placeholder token found: {path.name}")
        if ABSOLUTE_PATH_RE.search(text):
            raise ArchitectureValidationError(f"Absolute local path found: {path.name}")
        if PRIVATE_ID_RE.search(text):
            raise ArchitectureValidationError(f"Private-looking identifier found: {path.name}")
        if SECRET_RE.search(text):
            raise ArchitectureValidationError(f"Secret-like value found: {path.name}")
    model_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in files
        if path.suffix in {".mmd", ".yaml"}
    )
    if STALE_MODEL_RE.search(model_text):
        raise ArchitectureValidationError("Unsupported stale model family found in architecture facts.")
    if re.search(r"(?i)hackathon integration (?:is|required|must be) required", model_text):
        raise ArchitectureValidationError("Architecture incorrectly makes Hackathon integration required.")
    if re.search(r"(?i)organizer (?:checker|check_allocation\.py).{0,30}(?:proves|certifies|verifies) optimality", model_text):
        raise ArchitectureValidationError("Architecture overclaims organizer-checker optimality.")


def validate_architecture(architecture_dir: Path, manifest_path: Path) -> dict[str, Any]:
    architecture_dir = architecture_dir.resolve()
    manifest_path = manifest_path.resolve()
    canonical = (ROOT / "docs" / "architecture").resolve()
    if architecture_dir != canonical or manifest_path != canonical / "architecture_manifest.yaml":
        raise ArchitectureValidationError("Phase 29 validation requires canonical architecture paths.")
    manifest = _load_yaml(manifest_path)
    _validate_manifest(manifest)
    sources = _validate_sources(architecture_dir, manifest)
    titles = {item["diagram_id"]: item["title"] for item in manifest["diagrams"]}
    for diagram_id in DIAGRAM_IDS:
        _validate_svg(
            architecture_dir / f"{diagram_id}.svg",
            architecture_dir / f"{diagram_id}.mmd",
            titles[diagram_id],
        )
    readme = architecture_dir / "README.md"
    if not readme.is_file():
        raise ArchitectureValidationError("Architecture README is missing.")
    _require_tokens(readme.read_text(encoding="utf-8"), [
        "## Purpose", "## Official requirement", "## Diagram index", "## Source-of-truth policy",
        "## Diagram legend", "## Required and optional architecture", "## Rendering instructions",
        "## Privacy note", "## Validation status",
        *[f"{diagram_id}.svg" for diagram_id in DIAGRAM_IDS],
    ], "architecture README")
    files = [readme, manifest_path]
    files.extend(architecture_dir / f"{diagram_id}{suffix}" for diagram_id in DIAGRAM_IDS for suffix in (".mmd", ".svg"))
    _validate_privacy(files)
    return {"diagram_count": len(sources), "static_svg_count": len(DIAGRAM_IDS), "status": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = validate_architecture(args.architecture_dir, args.manifest)
    print("LOCAL PHASE 29 ARCHITECTURE VALIDATION: PASS")
    print(f"MERMAID SOURCE COUNT: {result['diagram_count']}")
    print(f"STATIC SVG COUNT: {result['static_svg_count']}")
    print("ACTUAL FINAL MODEL NAMES VERIFIED: PASS")
    print("OFFICIAL OUTPUT SCHEMAS VERIFIED: PASS")
    print("PRIVATE DATA IN DIAGRAMS: NO")
    print("FROZEN ARTIFACT INTEGRITY: NOT CHECKED BY THIS VALIDATOR")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
