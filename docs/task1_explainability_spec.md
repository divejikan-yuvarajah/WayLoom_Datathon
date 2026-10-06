# Task 1 Explainability Specification

## Scope

Phase 25 explains the saved Phase 10 service-time regressor and lateness classifier without retraining, tuning, feature reselection, prediction changes, or external data transfer. The canonical Phase 06/10 test-feature builder is the only feature pipeline.

## Frozen-artifact guard

The builder hashes the final model configuration, each saved model bundle component, and `submission_task1.csv` before and after explanation generation. Any difference is a hard failure. The final predictions regenerated during the run must also match the frozen submission numerically.

## Population and sampling

The explanation population is the materialized Phase 06 Task 1 test feature matrix used by the frozen modelling pipeline. Loading this artifact avoids rebuilding historical training state during a post-hoc phase. Exact saved-schema checks and full frozen-submission prediction parity prove that it preserves the Phase 10 inference semantics. A deterministic stable-hash sample of at most 2,000 rows is used for global SHAP, with seed 42. If fewer rows exist, all rows are used. Local examples are selected deterministically from the full prediction population: closest to median service prediction and highest late probability, both with original-position tie-breaking.

## Feature and leakage contract

Feature names, ordering, categorical columns, missing-value handling, historical state and enabled profile come from the saved schema and canonical inference code. Direct actual journey fields and targets are rejected. Chronology-safe historical features retain their frozen training-history-only contract.

## Importance and SHAP

Trustworthy model-native importance is preferred. Otherwise mean absolute SHAP is used and labelled as a fallback. CatBoost uses native `ShapValues`; LightGBM and XGBoost use verified native contribution APIs. Supported sklearn models may use a local SHAP explainer only when reconstruction succeeds and frozen preprocessing semantics are preserved.

Service contributions reconstruct the raw service prediction. Lateness contributions reconstruct the base classifier output in its documented space. Service post-processing and lateness calibration are verified separately against the frozen inference functions. Raw-margin SHAP is never presented as a probability-point change.

## Reporting and privacy

Aggregate tables, anonymous local records, audits and plots are written under `reports/private/phase25_task1_explainability/`. Public-facing prose contains no row identifier. Business-driver claims require schema membership, leakage safety, material attribution and interpretable prediction-time meaning. Importance/SHAP disagreement is reported rather than hidden.

## Interpretation boundary

“Driver” means model driver or predictive association, not causal driver. Mean absolute SHAP measures strength, not direction. Correlated features can share attribution, ranks are model-specific, and rank does not establish actionability.

These explanations describe how the trained model uses observed features. They reflect model associations and attribution, not causal effects.
