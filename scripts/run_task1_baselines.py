"""Local-only fixed Phase 08 Task 1 baseline experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd
import yaml
import sklearn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.baselines import (
    ConstantLateProbabilityBaseline, GlobalMedianServiceBaseline,
    HierarchicalLateRateBaseline, HierarchicalServiceMedianBaseline,
    aggregate_fold_results, evaluate_baseline_fold, fit_predict_linear_baseline,
    fit_predict_logistic_baseline,
)
from src.task1.feature_registry import build_feature_registry
from src.task1.features import audit_feature_leakage
from src.task1.validation import build_task1_validation_plan, load_task1_validation_config


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run Phase 08 Task 1 baselines on Phase 07 development folds.")
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--feature-registry", type=Path, required=True)
    p.add_argument("--validation-config", type=Path, required=True)
    p.add_argument("--baseline-config", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p


def _config(path: Path) -> dict:
    with path.open(encoding="utf-8") as h:
        return yaml.safe_load(h) or {}


def _git_hash() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except Exception:
        return None


def main() -> int:
    args = parser().parse_args()
    X = pd.read_csv(args.features)
    labels = pd.read_csv(args.labels)
    if len(X) != len(labels):
        raise ValueError("Feature/label row count mismatch.")
    if not X.index.equals(labels.index):
        raise ValueError("Feature/label indexes must align exactly before Phase 07 fold indexing.")
    if not args.feature_registry.exists():
        raise FileNotFoundError(args.feature_registry)
    validation_cfg = load_task1_validation_config(args.validation_config)
    baseline_cfg = _config(args.baseline_config)
    if baseline_cfg.get("validation", {}).get("use_phase07_plan") is not True:
        raise ValueError("Phase 08 requires the frozen Phase 07 validation plan.")
    if baseline_cfg.get("validation", {}).get("use_final_holdout") is not False:
        raise ValueError("Phase 08 must not evaluate the final holdout.")
    private_root = (PROJECT_ROOT / "reports" / "private").resolve()
    if not args.output_dir.resolve().is_relative_to(private_root):
        raise ValueError("Phase 08 output must remain below reports/private/.")
    historical = {c for c in X.columns if c.startswith(("outlet_prior_", "brand_dock_prior_", "brand_prior_"))}
    registry = build_feature_registry(list(X.columns), historical_columns=historical)
    # Validate direct-name, target-separation, and registry-lineage defenses before fitting.
    audit_feature_leakage(X, X.copy(), registry)
    plan = build_task1_validation_plan(labels, validation_cfg)
    y_service = labels["service_minutes"]
    y_late = labels["late_flag"]
    all_rows: list[dict] = []
    segment_rows: list[dict] = []
    group_count_rows: list[dict] = []
    seg = baseline_cfg["segments"] if "segments" in baseline_cfg else validation_cfg["segments"]
    experiment_id = "phase08_task1_fixed_baselines"
    convergence_rows: list[dict] = []

    # The frozen plan indexes originate from labels and align row-for-row with Phase 06 features.
    for fold in plan["folds"]:
        tr, va = fold.train_index, fold.validation_index
        if set(tr) & set(va) or set(va) & set(plan["holdout"].holdout_index):
            raise ValueError("Phase 07 fold/holdout isolation violated.")
        if max(fold.train_dates) >= min(fold.validation_dates):
            raise ValueError("Phase 07 chronology violated.")
        Xtr, Xva = X.loc[tr], X.loc[va]
        ys_tr, ys_va = y_service.loc[tr], y_service.loc[va]
        yl_tr, yl_va = y_late.loc[tr], y_late.loc[va]
        service_models = {
            "service_global_median": GlobalMedianServiceBaseline().fit(Xtr, ys_tr).predict(Xva),
            "service_brand_median": HierarchicalServiceMedianBaseline(use_dock=False).fit(Xtr, ys_tr).predict(Xva),
            "service_brand_dock_median": HierarchicalServiceMedianBaseline().fit(Xtr, ys_tr).predict(Xva),
            "service_linear_regression": fit_predict_linear_baseline(Xtr, ys_tr, Xva, registry=registry).predictions,
        }
        grouped_late = HierarchicalLateRateBaseline().fit(Xtr, yl_tr)
        late_models = {
            "late_constant_probability": ConstantLateProbabilityBaseline().fit(Xtr, yl_tr).predict_proba(Xva),
            "late_brand_dock_rate": grouped_late.predict_proba(Xva),
        }
        for (_, row), train_count in zip(Xva.iterrows(), grouped_late.validation_group_counts_):
            group_count_rows.append(
                {
                    "experiment_id": experiment_id,
                    "model_name": "late_brand_dock_rate",
                    "fold_id": fold.fold,
                    "brand": row["brand"] if pd.notna(row["brand"]) else "__MISSING__",
                    "dock_type": row["dock_type"] if pd.notna(row["dock_type"]) else "__MISSING__",
                    "train_group_count": train_count,
                }
            )
        logistic = fit_predict_logistic_baseline(
            Xtr, yl_tr, Xva, registry=registry,
            max_iter=int(baseline_cfg["logistic_regression"]["max_iter"]),
            C=float(baseline_cfg["logistic_regression"]["C"]),
            random_state=int(baseline_cfg["logistic_regression"]["random_state"]),
        )
        convergence_rows.append(
            {"experiment_id": experiment_id, "fold_id": fold.fold, "model_name": "late_logistic_regression",
             "unsupported": logistic.unsupported, "convergence_warning": logistic.convergence_warning}
        )
        if not logistic.unsupported:
            late_models["late_logistic_regression"] = logistic.predictions
        for name, pred in service_models.items():
            rows, segments = evaluate_baseline_fold(
                model_name=name, target="service", fold=fold, y_valid=ys_va, prediction=pred,
                segment_frame=Xva, segment_fields=seg["fields"], segment_config=seg,
            )
            for row in rows:
                row["experiment_id"] = experiment_id
            for row in segments:
                row["experiment_id"] = experiment_id
            all_rows.extend(rows); segment_rows.extend(segments)
        for name, pred in late_models.items():
            rows, segments = evaluate_baseline_fold(
                model_name=name, target="late", fold=fold, y_valid=yl_va, prediction=pred,
                segment_frame=Xva, segment_fields=seg["fields"], segment_config=seg,
            )
            for row in rows:
                row["experiment_id"] = experiment_id
            for row in segments:
                row["experiment_id"] = experiment_id
            all_rows.extend(rows); segment_rows.extend(segments)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(all_rows)
    result.to_csv(args.output_dir / "fold_results.csv", index=False)
    aggregate_fold_results(result).to_csv(args.output_dir / "model_summary.csv", index=False)
    pd.DataFrame(segment_rows).to_csv(args.output_dir / "segment_diagnostics.csv", index=False)
    pd.DataFrame(group_count_rows).to_csv(args.output_dir / "group_rate_diagnostics.csv", index=False)
    pd.DataFrame(convergence_rows).to_csv(args.output_dir / "convergence_warnings.csv", index=False)
    manifest = {
        "experiment_id": experiment_id, "phase": "08",
        "created_at": datetime.now(timezone.utc).isoformat(), "git_commit": _git_hash(),
        "config_hash": hashlib.sha256(args.baseline_config.read_bytes()).hexdigest(),
        "validation_plan_version": validation_cfg.get("version"),
        "feature_registry_version": args.feature_registry.name,
        "seed": 42,
        "library_versions": {"pandas": pd.__version__, "scikit_learn": sklearn.__version__},
        "FINAL_HOLDOUT_ACCESSED": "NO", "SAME_DEVELOPMENT_FOLDS_USED": "YES",
        "PREPROCESSING_FIT_ON_TRAIN_ONLY": "YES", "PROHIBITED_ACTUAL_FEATURES_USED": "NO",
        "HYPERPARAMETER_TUNING_PERFORMED": "NO", "FINAL_MODEL_SELECTED": "NO",
    }
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (args.output_dir / "phase08_baseline_report.md").write_text(
        "# Phase 08 Baselines\n\nFINAL HOLDOUT ACCESSED: NO\n\nSAME DEVELOPMENT FOLDS USED: YES\n\n"
        "PREPROCESSING FIT ON TRAIN ONLY: YES\n\nPROHIBITED ACTUAL FEATURES USED: NO\n\n"
        "HYPERPARAMETER TUNING PERFORMED: NO\n\nFINAL MODEL SELECTED: NO\n",
        encoding="utf-8",
    )
    print("PHASE 08 TASK 1 BASELINES: PASS")
    print("Development folds only: PASS")
    print("Final holdout accessed: NO")
    print("No row-level records printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
