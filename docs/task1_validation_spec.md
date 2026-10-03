# Task 1 Validation Design (Phase 07)

## Frozen chronology contract

- The canonical validation date is `route_date`; Phase 04 labels may expose the
  same route-leg field as `date`, which is treated as a legacy alias only.
- The final holdout contains the latest configured calendar period.
- Development dates are strictly earlier than holdout dates.
- Expanding folds operate only inside development.
- Every date is atomic: it may not occur on both sides of any split.

## Fit-scope protocol

For each fold, learned operations follow this exact sequence:

1. Fit preprocessing and historical target statistics on fold training rows only.
2. Transform training rows.
3. Transform the complete validation window without validation labels.
4. Fit a model and score frozen metrics.

Historical target features use strict earlier-date history for training rows;
same-date outcomes cannot influence one another.

## Frozen metrics

- Service regression primary: MAE.
- Service secondary: RMSE, median absolute error, P90 absolute error.
- Lateness probability primary: log loss.
- Lateness probability secondary: Brier score.
- ROC-AUC, average precision, and ECE are diagnostics; unavailable ranking
  metrics are explicitly reported as `null` for single-class samples.

## Local command

```powershell
python scripts/build_task1_validation_plan.py --labels data/interim/task1_training_labels.csv --features data/interim/task1_features_train.csv --feature-registry configs/task1_features.yaml --config configs/task1_validation.yaml --output-dir reports/private/phase07_task1_validation
```
