# Task 1 Final Training and Inference Specification (Phase 10)

Phase 10 retrains **exactly** the frozen Phase 09 service and lateness configurations on the allowed historical Task 1 population, saves reloadable bundles, and generates `outputs/submission_task1.csv` from those saved artifacts.

This phase does **not** search models, tune hyperparameters, reopen the final holdout, change the feature profile, add class weighting, or resample.

## Frozen configuration

Canonical source: `configs/task1_final_models.yaml`

Runtime refuses to train or infer when:

- the file is missing
- `status` is `PLACEHOLDER_UNFROZEN`
- `development_selection_complete` is not true
- `final_holdout_confirmation_complete` is not true
- more than one service or lateness configuration is present
- family, config ID, or final iteration policy is blank

## Local commands

Final training (human, restricted data):

```bash
python scripts/train_task1_final_models.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --report-dir reports/private/phase10_task1_final
```

Saved-model inference (human, restricted data):

```bash
python scripts/run_task1_inference.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --output outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final
```

Submission validation (human, restricted data):

```bash
python scripts/validate_task1_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final
```

## Training contract

- Use the frozen family, hyperparameters, feature profile, seed, iteration count, and preprocessing policy.
- Train on the complete allowed historical population. Do not open a new validation split for early stopping or search.
- Forbidden inference/target fields never enter `X`.
- Class-weight and resampling stay at the frozen Phase 09 policy (`none` unless already frozen; Phase 10 must not introduce `balanced`, SMOTE, oversampling, or undersampling).
- If Phase 09 selected raw probability, keep raw probability.
- If Phase 09 selected sigmoid or isotonic calibration, refit that calibrator on historical labels only and save it.

## Saved bundles

`models/task1_service/`

- `model.joblib`
- `metadata.json`
- `feature_schema.json`

`models/task1_late/`

- `model.joblib`
- `metadata.json`
- `feature_schema.json`
- `calibration.joblib` only when calibration is frozen

Metadata records task, family, config ID, seed, feature schema hash, registry version, library versions, training row count, training date range, and git commit when available. It never stores row-level training data.

## Inference contract

1. Load official `task1_test_inputs.csv` and stamp `__official_row_order` before any join or sort.
2. Left-join `route_legs_test.csv` on `route_id + seq_in_route` ↔ `route_id + seq` with `validate="one_to_one"` and `indicator=True`.
3. Fail on unmatched rows, duplicate route keys, or `outlet_id != to_outlet`.
4. Generate test features through the canonical Phase 06 pipeline. No ad-hoc test feature functions.
5. Historical target statistics are fit on historical training data only, then frozen. Test rows stay unlabeled and do not update later test rows.
6. Compare generated feature names and order to the saved training schema. Any difference stops inference.
7. Load saved models. Missing artifacts fail; inference never retrains.
8. Service output is numeric, finite, one value per official row. Apply `clip_to_zero` only when that policy is already frozen. Otherwise negatives fail. `abs()` is forbidden.
9. Lateness output is the probability of `late_flag = 1`, taken from verified `classes_` metadata, then frozen calibration if selected. Hard `predict()` is not the submission output. Values must be finite and in `[0, 1]`. Broken probabilities are not clamped.
10. Restore official row order and keep the exact `delivery_id` sequence.
11. Fill only `pred_service_min` and `pred_late_prob` on the official template. Export atomically to `outputs/submission_task1.csv` with `index=False`.

## Serialization proof

Train → save → discard in-memory objects → reload → predict the same `X` → assert numerically equivalent predictions. Repeat inference from identical saved artifacts; outputs must match.
