"""Local-only hard validation of the official Task 1 submission CSV."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.data_inventory import discover_dataset_files, load_manifest  # noqa: E402
from src.task1.final_train import load_frozen_final_config, load_yaml, resolve_negative_service_policy  # noqa: E402
from src.task1.submission import validate_task1_submission  # noqa: E402


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate outputs/submission_task1.csv against the official template.")
    p.add_argument("--raw-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--submission", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    p.add_argument("--final-config", type=Path, default=PROJECT_ROOT / "configs" / "task1_final_models.yaml")
    p.add_argument("--inference-config", type=Path, default=PROJECT_ROOT / "configs" / "task1_inference.yaml")
    return p


def _resolve_official(raw_root: Path, manifest_path: Path, filename: str) -> Path:
    manifest = load_manifest(manifest_path)
    discovered = discover_dataset_files(raw_root, manifest)
    found = discovered.get("found_artifacts") or {}
    if filename in found and found[filename].get("path"):
        return Path(found[filename]["path"])
    matches = list(Path(raw_root).rglob(filename))
    if not matches:
        raise SystemExit(f"Official file not found: {filename}")
    return matches[0]


def main() -> int:
    args = parser().parse_args()
    if not args.submission.is_file():
        raise SystemExit(f"Submission file does not exist: {args.submission}")
    if args.submission.name != "submission_task1.csv":
        raise SystemExit(f"Incorrect official filename: {args.submission.name}")
    test_inputs = pd.read_csv(_resolve_official(args.raw_root, args.manifest, "task1_test_inputs.csv"))
    template = pd.read_csv(_resolve_official(args.raw_root, args.manifest, "submission_task1.csv"))
    submission = pd.read_csv(args.submission)
    policy = "fail"
    if args.final_config.is_file():
        try:
            final_config = load_frozen_final_config(args.final_config)
            inference_config = load_yaml(args.inference_config) if args.inference_config.is_file() else {}
            policy = resolve_negative_service_policy(final_config, inference_config)
        except Exception:
            policy = "fail"
    result = validate_task1_submission(
        submission,
        test_inputs["delivery_id"],
        template_columns=list(template.columns),
        negative_policy=policy,
    )
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": 10,
        "status": "VALIDATED",
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        **result,
        "submission": str(args.submission),
    }
    (args.report_dir / "phase10_submission_validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
