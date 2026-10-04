"""Freeze the two Phase 16 local champion decisions for Phase 17 use."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task2a.advanced_models import load_advanced_config
from src.task2a.features import load_feature_config
from src.task2a.model_preprocessing import feature_profile
from src.task2a.model_selection import load_selection_decisions, validate_final_model_config
from src.task2a.baseline_evaluation import phase14_backtest_signature_from_metadata
from src.task2a.validation import load_validation_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--advanced-config", required=True, type=Path)
    parser.add_argument("--validation-config", required=True, type=Path)
    parser.add_argument("--feature-config", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--phase14-plan", type=Path,
                        default=PROJECT_ROOT / "reports/private/phase14_task2a_validation/validation_plan.json")
    return parser.parse_args()


def build_final_config(selection: dict, advanced_config: dict, feature_config: dict,
                       validation_config: dict, *, feature_path: str,
                       validation_path: str) -> dict:
    from src.task2a.advanced_models import validate_advanced_config
    from src.task2a.validation import validate_validation_config
    from src.task2a.features import validate_feature_config
    validate_advanced_config(advanced_config)
    validate_feature_config(feature_config)
    validate_validation_config(validation_config)
    profile = feature_profile(feature_config)
    if selection.get("feature_registry_hash") != profile["registry_hash"] or selection.get("feature_profile_id") != profile["profile_id"]:
        raise ValueError("Local champion selection used a different Phase 13 feature profile.")
    if selection.get("style_chilled_zero") is not True or selection.get("tech_chilled_zero") is not True:
        raise ValueError("Local champion selection lost structural chilled-zero rules.")
    config = {"version": 1, "state": "FROZEN",
        "source_contracts": {"history": "phase11", "features": "phase13", "validation": "phase14",
                             "baselines": "phase15", "selection": "phase16"},
        "feature_profile": {"registry_path": feature_path, "profile_id": profile["profile_id"],
                            "registry_hash": profile["registry_hash"]},
        "validation": {"config_path": validation_path,
                       "backtest_signature": selection["phase14_backtest_signature"]},
        "selection_policy": {"primary_metric": "mae", "relative_tie_tolerance_pct": 0.5,
                             "prefer_simpler_within_tolerance": True},
        "total": selection["total"], "chilled_fresh": selection["chilled_fresh"],
        "structural_output_rules": {"style_chilled_zero": True, "tech_chilled_zero": True},
        "phase17_postprocessing": {"clip_negative": True, "enforce_chilled_le_total": True,
                                   "rounding": "none"},
        "seeds": {"default": 42}, "selection_complete": True}
    validate_final_model_config(config)
    return config


def main() -> int:
    args = parse_args()
    allowed = (PROJECT_ROOT / "configs/task2a_final_models.yaml").resolve()
    if args.output.resolve() != allowed:
        raise ValueError("Frozen Task 2A config output must be configs/task2a_final_models.yaml.")
    manifest_path = args.selection.parent / "run_manifest.json"
    if not args.selection.is_file() or not manifest_path.is_file():
        print("PHASE 16 FREEZE: BLOCKED — local advanced modelling run has not completed.", file=sys.stderr)
        print("Missing required Phase 16 artifact(s): " + ", ".join(
            name for name, path in (("selection_decisions.json", args.selection),
                                    ("run_manifest.json", manifest_path)) if not path.is_file()), file=sys.stderr)
        print("Run scripts/run_task2a_advanced_models.py successfully before freezing; "
              "see docs/task2a_advanced_modeling_spec.md for the local command.", file=sys.stderr)
        return 2
    current = yaml.safe_load(allowed.read_text(encoding="utf-8")) if allowed.exists() else None
    selection = load_selection_decisions(args.selection)
    expected_signature = phase14_backtest_signature_from_metadata(
        json.loads(args.phase14_plan.read_text(encoding="utf-8")))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if selection["phase14_backtest_signature"] != expected_signature or manifest.get("phase14_backtest_signature") != expected_signature:
        raise ValueError("Phase 16 selection no longer matches the frozen Phase 14 plan.")
    if manifest.get("phase15_references_verified") is not True or manifest.get("forbidden_feature_count") != 0:
        raise ValueError("Phase 16 reference or feature safety audit is incomplete.")
    if manifest.get("feature_registry_hash") != selection.get("feature_registry_hash"):
        raise ValueError("Phase 16 selection and manifest feature registry differ.")
    config = build_final_config(selection, load_advanced_config(args.advanced_config),
        load_feature_config(args.feature_config), load_validation_config(args.validation_config),
        feature_path="configs/task2a_features.yaml", validation_path="configs/task2a_validation.yaml")
    if isinstance(current, dict) and current.get("state") == "FROZEN":
        validate_final_model_config(current)
        if current != config:
            print("PHASE 16 FREEZE: BLOCKED — the existing FROZEN Task 2A config differs "
                  "from the new validated selection; refusing to replace it.", file=sys.stderr)
            return 2
        state = "FROZEN (UNCHANGED)"
    else:
        # Write LF explicitly: Path.write_text translates newlines to CRLF on Windows,
        # which Git reports as trailing whitespace for this tracked YAML file.
        allowed.write_bytes(yaml.safe_dump(config, sort_keys=False).encode("utf-8"))
        state = "FROZEN"
    print(f"LOCAL TASK 2A FINAL CONFIG: {state}")
    print("TOTAL CHAMPION: ONE")
    print("FRESH CHILLED CHAMPION: ONE")
    print("PRIVATE BACKTEST METRICS WRITTEN TO CONFIG: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
