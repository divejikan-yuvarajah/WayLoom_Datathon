"""Local-only Phase 10 final retraining on the allowed historical Task 1 population."""

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

from src.task1.final_train import (  # noqa: E402
    load_frozen_final_config,
    save_model_bundle,
    train_final_models,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Retrain frozen Phase 09 Task 1 models on full historical data.")
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--feature-registry", type=Path, required=True)
    p.add_argument("--final-config", type=Path, required=True)
    p.add_argument("--service-model-dir", type=Path, required=True)
    p.add_argument("--late-model-dir", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    _ = args.feature_registry  # registry is consumed via the frozen feature profile + Phase 06 columns
    final_config = load_frozen_final_config(args.final_config)
    X = pd.read_csv(args.features, low_memory=False)
    labels = pd.read_csv(args.labels, low_memory=False)
    if len(X) != len(labels):
        raise SystemExit("Feature/label row count mismatch.")
    trained = train_final_models(X, labels["service_minutes"], labels["late_flag"], final_config)
    save_model_bundle(
        args.service_model_dir,
        model=trained["service_model"],
        metadata=trained["service_metadata"],
        schema=trained["schema"],
    )
    save_model_bundle(
        args.late_model_dir,
        model=trained["late_model"],
        metadata=trained["late_metadata"],
        schema=trained["schema"],
        calibration=trained["calibrator"],
    )
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": 10,
        "status": "TRAINED",
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "service_config_id": final_config["service_model"]["config_id"],
        "late_config_id": final_config["lateness_model"]["config_id"],
        "training_row_count": int(len(X)),
        "service_model_dir": str(args.service_model_dir),
        "late_model_dir": str(args.late_model_dir),
        "model_search": False,
    }
    (args.report_dir / "phase10_final_train_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
