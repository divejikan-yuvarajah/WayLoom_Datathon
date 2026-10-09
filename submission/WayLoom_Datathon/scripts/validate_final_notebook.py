"""Validate the public Phase 31 source notebook and optional private executions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import nbformat
import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"
EXPECTED_CONFIG = ROOT / "configs" / "final_notebook.yaml"
TASK_TAGS = {f"dt-{number}" for number in range(389, 412)}
FINAL_TAGS = {"dt-404", "dt-405", "dt-406", "dt-407", "dt-408", "final-inference"}
BROKEN_TAGS = {"scratch", "temporary", "broken", "debug", "debug-final"}

ABSOLUTE_PATH_RE = re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|Windows|Program Files)[\\/]|/(?:home|Users)/[^\s\"']+)")
PRIVATE_ID_RE = re.compile(r"\b(?:ORD\d{6,}|OUT\d{3,}|VEH\d{3,}|S1-\d{3,}|W\d{4,})\b")
SECRET_RE = re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*[A-Za-z0-9_\-]{12,}")
PLACEHOLDER_RE = re.compile(r"(?i)(?:<MODEL>|\bTBD\b|\bTODO(?:_MODEL)?\b|FINAL_MODEL_HERE|replace me)")
INSTALL_RE = re.compile(r"(?im)^\s*(?:!|%)(?:pip|conda)\s+install\b")
NETWORK_RE = re.compile(
    r"(?i)(?:requests\.(?:get|post)|urllib\.(?:request|urlopen)|\bwget\b|\bcurl\b|"
    r"boto3|google\.cloud|azure\.storage|s3://|gs://)"
)
PROPRIETARY_API_RE = re.compile(r"(?i)(?:openai\.|anthropic\.|cohere\.|vertexai\.|bedrock)")
STALE_MODEL_RE = re.compile(r"(?i)\b(?:RandomForest|XGBoost|Prophet|LSTM)\b")


class FinalNotebookValidationError(ValueError):
    """A Phase 31 notebook contract is incomplete or unsafe."""


def load_config(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalNotebookValidationError("Final-notebook config must be a mapping.")
    return value


def _canonical(path: Path, expected: Path, label: str) -> None:
    if path.resolve() != expected.resolve():
        raise FinalNotebookValidationError(f"{label} must use canonical path {expected.relative_to(ROOT)}.")


def _source_text(notebook: Any) -> str:
    return "\n".join(str(cell.get("source", "")) for cell in notebook.cells)


def _all_tags(notebook: Any) -> set[str]:
    tags: set[str] = set()
    for cell in notebook.cells:
        tags.update(str(tag) for tag in cell.get("metadata", {}).get("tags", []))
    return tags


def _require_tokens(text: str, tokens: list[str], label: str) -> None:
    lowered = text.lower()
    missing = [token for token in tokens if token.lower() not in lowered]
    if missing:
        raise FinalNotebookValidationError(f"{label} is missing: {', '.join(missing)}")


def _validate_config(config: dict[str, Any]) -> None:
    if config.get("version") != 1 or config.get("notebook_filename") != EXPECTED_NOTEBOOK.name:
        raise FinalNotebookValidationError("Final-notebook version or filename is invalid.")
    execution = config.get("execution") or {}
    if execution.get("kernel_name") != "python3" or execution.get("working_directory") != ".":
        raise FinalNotebookValidationError("Notebook kernel or working-directory contract changed.")
    private_dir = str(execution.get("private_output_dir", "")).replace("\\", "/")
    if private_dir != "reports/private/phase31_final_notebook":
        raise FinalNotebookValidationError("Notebook execution evidence must remain in the Phase 31 private directory.")
    if int((config.get("content") or {}).get("max_demo_rows", 0)) not in {1, 2, 3}:
        raise FinalNotebookValidationError("Demo-row limit must be between one and three.")
    final = config.get("final_inference") or {}
    required_true = {
        "require_saved_model_reload",
        "require_final_cell_is_last_cell",
        "require_final_cell_self_contained",
        "require_task1_demo",
        "require_task2a_demo",
        "require_clear_input_print",
        "require_clear_prediction_print",
        "require_submission_parity_check",
        "do_not_write_official_outputs",
    }
    if any(final.get(key) is not True for key in required_true):
        raise FinalNotebookValidationError("A required final-inference safety gate is disabled.")
    phase32 = config.get("phase32") or {}
    if phase32.get("status") not in {"AWAITING_PHASE32", "PASS"}:
        raise FinalNotebookValidationError("Phase 32 gate must be AWAITING_PHASE32 or PASS.")
    if not all(phase32.get(key) for key in ("artifact_registry", "loader_module", "loader_callable")):
        raise FinalNotebookValidationError("Phase 32 handoff interface is incomplete.")
    if phase32["status"] == "PASS" and not (ROOT / phase32["artifact_registry"]).is_file():
        raise FinalNotebookValidationError("Phase 32 is marked PASS but its artifact registry is missing.")


def _validate_privacy_and_hygiene(notebook: Any) -> None:
    text = _source_text(notebook)
    for pattern, label in (
        (ABSOLUTE_PATH_RE, "absolute workstation path"),
        (PRIVATE_ID_RE, "hardcoded private-looking identifier"),
        (SECRET_RE, "secret-like value"),
        (PLACEHOLDER_RE, "unfinished placeholder"),
        (INSTALL_RE, "environment-install command"),
        (NETWORK_RE, "network/download client"),
        (PROPRIETARY_API_RE, "proprietary inference API"),
        (STALE_MODEL_RE, "stale model family"),
    ):
        if pattern.search(text):
            raise FinalNotebookValidationError(f"Source notebook contains {label}.")
    if any(str(tag).lower() in BROKEN_TAGS for tag in _all_tags(notebook)):
        raise FinalNotebookValidationError("Source notebook contains a broken/temporary/debug cell tag.")
    for cell in notebook.cells:
        if cell.cell_type == "code" and not str(cell.source).strip():
            raise FinalNotebookValidationError("Source notebook contains an abandoned empty code cell.")
        if cell.cell_type == "code" and (cell.get("outputs") or cell.get("execution_count") is not None):
            raise FinalNotebookValidationError("Tracked source notebook must have cleared outputs and execution counts.")


def _validate_semantics(notebook: Any) -> None:
    text = _source_text(notebook)
    _require_tokens(
        text,
        [
            "WayLoom Datathon",
            "Rootcode Tech-Triathlon 2026",
            "Final Competition Notebook",
            "authorized competition submission workflow",
            "Task 1",
            "pred_service_min",
            "pred_late_prob",
            "Task 2A",
            "10 future weeks",
            "pred_total_volume_m3",
            "pred_chilled_volume_m3",
            "Task 2B",
            "constraint optimization",
            "scenario, order_ref, outlet_id, decision, vehicle_id, trip_id",
        ],
        "project overview",
    )
    _require_tokens(
        text,
        [
            "service_start = max(actual arrival, window opening)",
            "service_minutes = leave_outlet_time - service_start",
            "late_flag = 1 only if actual arrival > window_close_time",
            "early waiting is not service",
            "arrival exactly at close is not late",
            "build_task1_training_labels",
            "build_task1_feature_tables",
            "actual_depart_time",
            "actual_travel_duration_min",
            "arrival_time",
            "leave_outlet_time",
            "safe_core_plus_history",
            "catboost_regression_default",
            "catboost_classifier_default",
        ],
        "Task 1 contract",
    )
    _require_tokens(
        text,
        [
            "deliveries_train.csv",
            "task1_test_inputs.csv",
            "attempted, deferred, and not_run",
            "requested order_date",
            "iso_year and iso_week",
            "build_task2a_history",
            "build_direct_multihorizon_table",
            "build_rolling_origin_plan",
            "four deterministic rolling origins",
            "10-week",
            "ensemble_cb_lgb_total_equal_v1",
            "ensemble_cb_lgb_chilled_equal_v1",
            "Style and Tech chilled predictions are exactly zero",
        ],
        "Task 2A contract",
    )
    _require_tokens(
        text,
        [
            "does not require a trained model",
            "trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)",
            "No return leg",
            "Fresh <= 270",
            "Style+Tech <= 480",
            "WayLoom engineering priority policy",
            "feasibility only",
            "outputs/submission_task2b.csv",
            "docs/task2b_policy.md",
        ],
        "Task 2B contract",
    )


def _validate_final_cell(notebook: Any, config: dict[str, Any]) -> None:
    if not notebook.cells or notebook.cells[-1].cell_type != "code":
        raise FinalNotebookValidationError("The final notebook cell must be code.")
    final_cell = notebook.cells[-1]
    tags = set(final_cell.get("metadata", {}).get("tags", []))
    if not FINAL_TAGS.issubset(tags):
        raise FinalNotebookValidationError("Final code cell is missing required DT/semantic tags.")
    previous = notebook.cells[-2] if len(notebook.cells) > 1 else None
    if previous is None or previous.cell_type != "markdown" or "# Final Saved-Model Inference Demonstration" not in previous.source:
        raise FinalNotebookValidationError("Final inference heading must immediately precede the final code cell.")
    source = str(final_cell.source)
    _require_tokens(
        source,
        [
            "from pathlib import Path",
            "import importlib",
            "configs/final_notebook.yaml",
            "phase32",
            "AWAITING_PHASE32",
            "loader_module",
            "loader_callable",
            "TASK 1 - INPUTS",
            "TASK 1 - PREDICTIONS",
            "TASK 2A - INPUTS",
            "TASK 2A - PREDICTIONS",
            "TASK 1 SAVED-MODEL PARITY: PASS",
            "TASK 2A SAVED-MODEL PARITY: PASS",
            "max_demo_rows",
        ],
        "final inference cell",
    )
    forbidden = (
        "train_final_models(",
        "run_advanced_backtests(",
        "run_final_inference(",
        ".to_csv(",
        "write_submission",
        "export_task",
        "outputs/submission_task1.csv",
        "outputs/submission_task2a.csv",
    )
    present = [token for token in forbidden if token in source]
    if present:
        raise FinalNotebookValidationError("Final cell trains or writes official outputs: " + ", ".join(present))
    if int((config.get("privacy") or {}).get("max_demo_rows", 0)) > 3:
        raise FinalNotebookValidationError("Privacy demo-row limit exceeds three.")


def validate_source_notebook(source: Path, config_path: Path) -> dict[str, Any]:
    _canonical(source, EXPECTED_NOTEBOOK, "Source notebook")
    _canonical(config_path, EXPECTED_CONFIG, "Final-notebook config")
    if not source.is_file() or source.stat().st_size == 0:
        raise FinalNotebookValidationError("Source notebook is missing or empty.")
    config = load_config(config_path)
    _validate_config(config)
    notebook = nbformat.read(source, as_version=4)
    if notebook.nbformat != 4 or not notebook.cells:
        raise FinalNotebookValidationError("Notebook must be nonempty nbformat v4.")
    kernelspec = notebook.metadata.get("kernelspec") or {}
    if kernelspec.get("name") != config["execution"]["kernel_name"]:
        raise FinalNotebookValidationError("Notebook kernelspec does not match config.")
    tags = _all_tags(notebook)
    missing_tasks = sorted(TASK_TAGS - tags)
    if missing_tasks:
        raise FinalNotebookValidationError("Notebook task tags missing: " + ", ".join(missing_tasks))
    _validate_privacy_and_hygiene(notebook)
    _validate_semantics(notebook)
    _validate_final_cell(notebook, config)
    return {
        "notebook": notebook,
        "config": config,
        "cell_count": len(notebook.cells),
        "code_cell_count": sum(cell.cell_type == "code" for cell in notebook.cells),
        "task_count": len(TASK_TAGS & tags),
        "phase32_status": config["phase32"]["status"],
    }


def _output_text(notebook: Any) -> str:
    parts: list[str] = []
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                parts.append(str(output.get("text", "")))
            elif output.get("output_type") in {"execute_result", "display_data"}:
                data = output.get("data") or {}
                parts.append(str(data.get("text/plain", "")))
    return "\n".join(parts)


def _assert_no_errors(notebook: Any, label: str) -> None:
    errors = [
        output
        for cell in notebook.cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    if errors:
        raise FinalNotebookValidationError(f"{label} contains {len(errors)} execution error output(s).")


def validate_run_all_execution(path: Path, source_result: dict[str, Any]) -> None:
    notebook = nbformat.read(path, as_version=4)
    if len(notebook.cells) != source_result["cell_count"]:
        raise FinalNotebookValidationError("Run-all notebook cell count differs from source.")
    _assert_no_errors(notebook, "Run-all notebook")
    counts = [cell.execution_count for cell in notebook.cells if cell.cell_type == "code"]
    if any(count is None for count in counts) or counts != sorted(counts) or len(set(counts)) != len(counts):
        raise FinalNotebookValidationError("Run-all code cells were not executed once in fresh ordered sequence.")
    _require_tokens(
        _output_text(notebook),
        [
            "TASK 1 - INPUTS",
            "TASK 1 - PREDICTIONS",
            "TASK 2A - INPUTS",
            "TASK 2A - PREDICTIONS",
            "TASK 1 SAVED-MODEL PARITY: PASS",
            "TASK 2A SAVED-MODEL PARITY: PASS",
        ],
        "run-all output",
    )


def validate_final_cell_execution(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if len(code_cells) != 1 or code_cells[0].execution_count is None:
        raise FinalNotebookValidationError("Final-cell-only evidence must contain one executed code cell.")
    _assert_no_errors(notebook, "Final-cell-only notebook")
    _require_tokens(
        _output_text(notebook),
        [
            "TASK 1 - INPUTS",
            "TASK 1 - PREDICTIONS",
            "TASK 2A - INPUTS",
            "TASK 2A - PREDICTIONS",
            "TASK 1 SAVED-MODEL PARITY: PASS",
            "TASK 2A SAVED-MODEL PARITY: PASS",
        ],
        "final-cell-only output",
    )


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FinalNotebookValidationError(f"Required private evidence is missing: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalNotebookValidationError(f"Private evidence is not a JSON object: {path.name}")
    return value


def validate_private_runtime_evidence(
    executed: Path,
    final_cell_executed: Path,
    config: dict[str, Any],
) -> None:
    private_dir = (ROOT / config["execution"]["private_output_dir"]).resolve()
    expected_run_all = private_dir / "TeamName_FinalNotebook.executed.ipynb"
    expected_final_only = private_dir / "final_cell_only.executed.ipynb"
    if executed.resolve() != expected_run_all or final_cell_executed.resolve() != expected_final_only:
        raise FinalNotebookValidationError("Executed notebook evidence must use canonical private paths.")

    manifest = _load_json_object(private_dir / "run_manifest.json")
    run_summary = _load_json_object(private_dir / "execution_summary.json")
    final_summary = _load_json_object(private_dir / "final_cell_only_summary.json")
    parity = _load_json_object(private_dir / "final_inference_parity.json")
    frozen = _load_json_object(private_dir / "frozen_hash_audit.json")

    if manifest.get("run-all_status") != "PASS" or manifest.get("final-cell-only_status") != "PASS":
        raise FinalNotebookValidationError("Private run manifest does not prove both required executions.")
    if run_summary.get("status") != "PASS" or run_summary.get("mode") != "run-all":
        raise FinalNotebookValidationError("Run-all execution summary is incomplete.")
    if final_summary.get("status") != "PASS" or final_summary.get("mode") != "final-cell-only":
        raise FinalNotebookValidationError("Final-cell-only execution summary is incomplete.")
    if parity.get("status") != "PASS" or parity.get("task1_saved_model_parity") != "PASS" or parity.get(
        "task2a_saved_model_parity"
    ) != "PASS":
        raise FinalNotebookValidationError("Saved-model inference parity evidence is incomplete.")
    if parity.get("runs") != {"run-all": "PASS", "final-cell-only": "PASS"}:
        raise FinalNotebookValidationError("Parity evidence does not cover both fresh-kernel executions.")
    runs = frozen.get("runs") or {}
    if frozen.get("status") != "PASS" or frozen.get("official_outputs") != "UNCHANGED" or frozen.get(
        "saved_model_artifacts"
    ) != "UNCHANGED":
        raise FinalNotebookValidationError("Frozen-artifact audit did not pass.")
    for mode in ("run-all", "final-cell-only"):
        record = runs.get(mode) or {}
        if record.get("status") != "PASS" or record.get("before") != record.get("after"):
            raise FinalNotebookValidationError(f"Frozen-artifact hashes changed during {mode} execution.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Phase 31 final notebook.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--executed", type=Path)
    parser.add_argument("--final-cell-executed", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_source_notebook(args.source, args.config)
    runtime_requested = args.executed is not None or args.final_cell_executed is not None
    if runtime_requested and result["phase32_status"] != "PASS":
        raise FinalNotebookValidationError("Private execution evidence cannot close Phase 31 before Phase 32 PASS.")
    if runtime_requested and (args.executed is None or args.final_cell_executed is None):
        raise FinalNotebookValidationError("Final closure requires both run-all and final-cell-only evidence.")
    if runtime_requested:
        validate_run_all_execution(args.executed, result)
        validate_final_cell_execution(args.final_cell_executed)
        validate_private_runtime_evidence(args.executed, args.final_cell_executed, result["config"])

    print("WAYLOOM - PHASE 31 FINAL NOTEBOOK")
    print("SOURCE NOTEBOOK STRUCTURE: PASS")
    print(f"TASK MAPPING DT-389-DT-411: PASS ({result['task_count']} / 23)")
    print("FINAL CELL IS LAST CELL: PASS")
    print("BROKEN/TEMP CELLS: 0")
    print("PRIVATE OUTPUTS IN SOURCE NOTEBOOK: NO")
    if result["phase32_status"] == "PASS":
        print("PHASE32 SAVED ARTIFACT GATE: PASS")
        print("CLEAN-KERNEL RUN-ALL: PASS" if args.executed else "CLEAN-KERNEL RUN-ALL: PENDING")
        print(
            "FINAL-CELL-ONLY FRESH KERNEL: PASS"
            if args.final_cell_executed
            else "FINAL-CELL-ONLY FRESH KERNEL: PENDING"
        )
    else:
        print("PHASE32 SAVED ARTIFACT GATE: AWAITING_PHASE32")
        print("FINAL CLEAN-RUN CLOSURE: PENDING")
    print("LOCAL PHASE 31 NOTEBOOK CORE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
