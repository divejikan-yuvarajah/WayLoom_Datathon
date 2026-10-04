"""Human-local Phase 12 Task 2A EDA runner; console output is sanitized."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import load_manifest
from src.task2a.eda import load_eda_config, run_task2a_eda


def _unique_artifact(raw_root: Path, filename: str) -> Path:
    matches = list(raw_root.rglob(filename))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one official artifact named {filename}; found {len(matches)}.")
    return matches[0]


def validate_private_output_dir(output_dir: Path) -> Path:
    """Allow output only within the ignored Phase 12 private-report directory."""
    private_root = (PROJECT_ROOT / "reports" / "private" / "phase12_task2a_eda").resolve()
    resolved = output_dir.resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise ValueError("Phase 12 EDA output must be inside reports/private/phase12_task2a_eda.") from exc
    return resolved


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Run sanitized Task 2A EDA on local private data.")
    value.add_argument("--weekly-panel", type=Path, required=True)
    value.add_argument("--raw-root", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--history-config", type=Path, required=True, help="Phase 11 config; checked for expected calendar filename.")
    value.add_argument("--eda-config", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    manifest = load_manifest(args.manifest)
    manifest_names = {artifact["filename"] for artifact in manifest["artifacts"]}
    history_config = load_eda_config(args.history_config)
    calendar_name = history_config["official_sources"]["calendar"]
    if calendar_name not in manifest_names:
        raise ValueError("Phase 11 calendar source is absent from the official manifest.")
    calendar_path = _unique_artifact(args.raw_root, calendar_name)
    panel = pd.read_csv(args.weekly_panel)
    calendar = pd.read_csv(calendar_path)
    config = load_eda_config(args.eda_config)
    output_dir = validate_private_output_dir(args.output_dir)
    result = run_task2a_eda(panel, calendar, config, output_dir)
    summary = result["summary"]
    print("PHASE 12 LOCAL TASK2A EDA: PASS")
    print(f"SERIES ANALYZED: {summary['series_count']}")
    print(f"SANITIZED REPORT AND FIGURES WRITTEN: YES ({summary['figure_count']} figures)")
    print("PRIVATE WEEKLY VALUES OR ORDER IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
