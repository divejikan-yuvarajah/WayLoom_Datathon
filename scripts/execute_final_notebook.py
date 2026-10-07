"""Execute the Phase 31 notebook in a fresh kernel and write private evidence."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import nbformat
import yaml
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INPUT = ROOT / "TeamName_FinalNotebook.ipynb"
EXPECTED_CONFIG = ROOT / "configs" / "final_notebook.yaml"


class FinalNotebookExecutionError(ValueError):
    """The private notebook execution contract was violated."""


def _load_config(path: Path) -> dict[str, Any]:
    if path.resolve() != EXPECTED_CONFIG.resolve():
        raise FinalNotebookExecutionError("Execution requires configs/final_notebook.yaml.")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalNotebookExecutionError("Final-notebook config is invalid.")
    return value


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_path(path: Path) -> str:
    if path.is_file():
        return _sha256(path)
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(item for item in path.rglob("*") if item.is_file()):
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(_sha256(child).encode("ascii"))
        return digest.hexdigest()
    raise FinalNotebookExecutionError(f"Frozen integrity path is missing: {path.relative_to(ROOT)}")


def _phase32_artifact_paths(config: dict[str, Any]) -> list[Path]:
    phase32 = config.get("phase32") or {}
    if phase32.get("status") != "PASS":
        raise FinalNotebookExecutionError(
            "PHASE32 SAVED ARTIFACT GATE: AWAITING_PHASE32. Complete DT-412-DT-419 before execution."
        )
    registry_path = ROOT / str(phase32.get("artifact_registry", ""))
    if not registry_path.is_file():
        raise FinalNotebookExecutionError("Phase 32 artifact registry is missing.")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    artifacts = registry.get("artifacts") if isinstance(registry, dict) else None
    if not isinstance(artifacts, list) or not artifacts:
        raise FinalNotebookExecutionError("Phase 32 artifact registry has no artifacts.")
    paths = [registry_path.resolve()]
    paths.extend((ROOT / str(entry.get("relative_path", ""))).resolve() for entry in artifacts)
    if any(not _inside(path, ROOT) for path in paths):
        raise FinalNotebookExecutionError("Phase 32 artifact path escapes the repository.")
    return paths


def _integrity_paths(config: dict[str, Any]) -> list[Path]:
    integrity = config.get("integrity") or {}
    paths: list[Path] = []
    for key in ("official_outputs", "frozen_configs", "existing_model_roots"):
        values = integrity.get(key)
        if not isinstance(values, list) or not values:
            raise FinalNotebookExecutionError(f"Integrity list {key} is missing.")
        paths.extend((ROOT / str(value)).resolve() for value in values)
    paths.extend(_phase32_artifact_paths(config))
    unique = list(dict.fromkeys(paths))
    if any(not _inside(path, ROOT) for path in unique):
        raise FinalNotebookExecutionError("A frozen integrity path escapes the repository.")
    return unique


def _snapshot(paths: list[Path]) -> dict[str, str]:
    return {path.relative_to(ROOT).as_posix(): _hash_path(path) for path in paths}


def _error_count(notebook: Any) -> int:
    return sum(
        output.get("output_type") == "error"
        for cell in notebook.cells
        for output in cell.get("outputs", [])
    )


def _output_text(notebook: Any) -> str:
    parts: list[str] = []
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                parts.append(str(output.get("text", "")))
            elif output.get("output_type") in {"execute_result", "display_data"}:
                parts.append(str((output.get("data") or {}).get("text/plain", "")))
    return "\n".join(parts)


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def _package_versions() -> dict[str, str]:
    names = ("numpy", "pandas", "scikit-learn", "catboost", "lightgbm", "nbformat", "nbclient")
    result: dict[str, str] = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "NOT_INSTALLED"
    return result


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _load_private_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return default
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalNotebookExecutionError(f"Private evidence is not a JSON object: {path.name}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute the Phase 31 notebook privately.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--mode", choices=("run-all", "final-cell-only"), required=True)
    parser.add_argument("--timeout", type=int)
    return parser.parse_args()


def main() -> int:
    if platform.system() == "Windows":
        # pyzmq requires add_reader support, which the default Proactor loop does
        # not provide. Configure the supported selector loop before nbclient asks
        # jupyter_core to create its execution event loop.
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    args = parse_args()
    if args.input.resolve() != EXPECTED_INPUT.resolve():
        raise FinalNotebookExecutionError("Input must be TeamName_FinalNotebook.ipynb.")
    config = _load_config(args.config)
    private_dir = (ROOT / config["execution"]["private_output_dir"]).resolve()
    output = args.output.resolve()
    if not _inside(output, private_dir) or output == args.input.resolve():
        raise FinalNotebookExecutionError("Executed notebook must be written under the Phase 31 private directory.")
    timeout = int(args.timeout or config["execution"]["timeout_seconds"])
    if timeout < 1:
        raise FinalNotebookExecutionError("Execution timeout must be positive.")

    source = nbformat.read(args.input, as_version=4)
    if not source.cells or source.cells[-1].cell_type != "code":
        raise FinalNotebookExecutionError("Source notebook final cell is not code.")
    if args.mode == "final-cell-only":
        notebook = nbformat.v4.new_notebook(
            metadata=dict(source.metadata), cells=[nbformat.from_dict(dict(source.cells[-1]))]
        )
        notebook.cells[0].outputs = []
        notebook.cells[0].execution_count = None
    else:
        notebook = source

    frozen_paths = _integrity_paths(config)
    before = _snapshot(frozen_paths)
    private_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)
    start = time.perf_counter()
    old_hash_seed = os.environ.get("PYTHONHASHSEED")
    os.environ["PYTHONHASHSEED"] = str(config["reproducibility"]["random_seed"])
    try:
        client = NotebookClient(
            notebook,
            timeout=timeout,
            kernel_name=config["execution"]["kernel_name"],
            resources={"metadata": {"path": str(ROOT)}},
            allow_errors=False,
        )
        executed = client.execute()
    finally:
        if old_hash_seed is None:
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = old_hash_seed
    duration = time.perf_counter() - start
    ended_at = datetime.now(timezone.utc)
    after = _snapshot(frozen_paths)
    if before != after:
        raise FinalNotebookExecutionError("Frozen output/model artifact hash changed during notebook execution.")
    errors = _error_count(executed)
    if errors:
        raise FinalNotebookExecutionError(f"Executed notebook contains {errors} error output(s).")
    text = _output_text(executed)
    markers = (
        "TASK 1 - INPUTS",
        "TASK 1 - PREDICTIONS",
        "TASK 2A - INPUTS",
        "TASK 2A - PREDICTIONS",
        "TASK 1 SAVED-MODEL PARITY: PASS",
        "TASK 2A SAVED-MODEL PARITY: PASS",
    )
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise FinalNotebookExecutionError("Final inference output markers missing: " + ", ".join(missing))

    nbformat.write(executed, output)
    summary = {
        "phase": 31,
        "mode": args.mode,
        "status": "PASS",
        "source_notebook_sha256": _sha256(args.input),
        "executed_notebook_sha256": _sha256(output),
        "kernel": config["execution"]["kernel_name"],
        "python_version": platform.python_version(),
        "package_versions": _package_versions(),
        "execution_start_utc": started_at.isoformat(),
        "execution_end_utc": ended_at.isoformat(),
        "runtime_seconds": round(duration, 6),
        "cell_count": len(executed.cells),
        "code_cell_count": sum(cell.cell_type == "code" for cell in executed.cells),
        "error_output_count": errors,
        "final_cell_is_last": bool(executed.cells and executed.cells[-1].cell_type == "code"),
        "phase32_artifact_status": "PASS",
        "task1_parity_status": "PASS",
        "task2a_parity_status": "PASS",
        "frozen_output_hash_status": "UNCHANGED",
        "model_artifact_hash_status": "UNCHANGED",
        "git_commit": _git_commit(),
    }
    summary_name = "execution_summary.json" if args.mode == "run-all" else "final_cell_only_summary.json"
    _write_json(private_dir / summary_name, summary)
    parity_path = private_dir / "final_inference_parity.json"
    parity = _load_private_json(parity_path, {"phase": 31, "runs": {}})
    parity.setdefault("runs", {})[args.mode] = "PASS"
    parity.update(
        {
            "status": "PASS",
            "saved_artifacts_loaded": True,
            "task1_saved_model_parity": "PASS",
            "task2a_saved_model_parity": "PASS",
        }
    )
    _write_json(parity_path, parity)

    frozen_audit_path = private_dir / "frozen_hash_audit.json"
    frozen_audit = _load_private_json(frozen_audit_path, {"phase": 31, "runs": {}})
    frozen_audit.setdefault("runs", {})[args.mode] = {
        "status": "PASS",
        "before": before,
        "after": after,
    }
    frozen_audit.update(
        {
            "status": "PASS",
            "official_outputs": "UNCHANGED",
            "saved_model_artifacts": "UNCHANGED",
        }
    )
    _write_json(frozen_audit_path, frozen_audit)

    manifest_path = private_dir / "run_manifest.json"
    manifest = _load_private_json(manifest_path, {"phase": 31})
    manifest[f"{args.mode}_status"] = "PASS"
    manifest[f"{args.mode}_executed_notebook_sha256"] = summary["executed_notebook_sha256"]
    manifest["phase32_artifact_status"] = "PASS"
    manifest["frozen_output_hash_status"] = "UNCHANGED"
    manifest["model_artifact_hash_status"] = "UNCHANGED"
    manifest["final_inference_parity_evidence"] = parity_path.name
    manifest["frozen_hash_audit_evidence"] = frozen_audit_path.name
    manifest["git_commit"] = summary["git_commit"]
    _write_json(manifest_path, manifest)

    print(f"LOCAL PHASE 31 {args.mode.upper()} EXECUTION: PASS")
    print("EXECUTION ERRORS: 0")
    print("TASK 1 SAVED-MODEL PARITY: PASS")
    print("TASK 2A SAVED-MODEL PARITY: PASS")
    print("OFFICIAL OUTPUTS CHANGED: NO")
    print("SAVED MODEL ARTIFACTS CHANGED: NO")
    print("PRIVATE ROW VALUES PRINTED BY WRAPPER: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
