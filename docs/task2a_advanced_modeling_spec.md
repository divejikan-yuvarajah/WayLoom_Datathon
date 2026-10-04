# Task 2A Phase 16 advanced forecasting

Phase 16 fits CatBoost and LightGBM total-demand models on every eligible
depot and brand series, plus separate Fresh-only chilled models. All four use
the same Phase 13 safe feature registry, the same Phase 14 rolling-origin
splits, and the Phase 14 raw-prediction metrics. CatBoost handles categorical
features natively. LightGBM uses fold-train median imputation and one-hot
encoding; unseen validation categories are ignored by the fitted encoder.

The local runner rebuilds the canonical Phase 14 plan and verifies the
persisted signature and exact training/validation row indices. Each fold uses
only training rows whose target week is at or before its origin. Validation
labels are passed solely to early stopping and scoring. Every horizon in a
ten-week validation block uses the same origin-derived demand features.
Neither model uses a pre-trained checkpoint or external modelling service.

The runner requires the Phase 15 reference manifest, reference IDs, and raw
baseline predictions. It verifies their signature, labels, series, target
weeks, and horizons. Five candidates per target are compared: the frozen
reference, CatBoost, LightGBM, their 50/50 blend, and a 50/50 blend of the
best single advanced model and the reference. Ensemble alignment uses the
complete backtest, series, origin, target, and horizon key. A missing row,
failed fold, duplicate key, or nonfinite prediction stops the run.

The predeclared selection gate requires an advanced candidate to improve
pooled MAE by strictly more than 0.5% versus the reference. A perfect
reference remains champion. Among eligible candidates within 0.5% of the
best MAE, the tie breaks use RMSE, P90 absolute error, backtest MAE standard
deviation, then simplicity. Fresh chilled is scored only on Fresh. Style and
Tech chilled values remain structural zeros. Negative predictions and raw
Fresh chilled predictions above raw total predictions are diagnostics;
Phase 16 does not alter them.

Candidate diagnostics pair each target with the corresponding raw opposite-
target candidate on the full frozen validation key. Fresh chilled-versus-total
counts therefore compare two predictions, never a prediction with a validation
label. Candidate-level tables contain only that candidate's scored target;
Fresh chilled per-series rows exclude Style/Tech structural-zero rows. CatBoost
`trained_iterations` counts evaluated rounds, even if its best-model retention
keeps fewer trees; `stopped_early` compares evaluated rounds with the configured
maximum.

The runner writes private predictions, fold early-stopping information,
candidate summaries, per-series and horizon metrics, backtest metrics,
selection decisions, and a sanitized manifest under
`reports/private/phase16_task2a_advanced/`. It prints only status lines.
The tracked `configs/task2a_final_models.yaml` starts in a pending state.
After reviewing the private diagnostics, the operator runs the freeze command;
that command validates both selected champions and writes a score-free
`FROZEN` configuration. A median of all valid fold best iterations, rounded
half-up and bounded by the configured maximum, is recorded for model
components. A baseline champion has no iteration count.
Rerunning the freeze command with an identical validated selection is a
no-write success. If the new selection differs from an existing `FROZEN`
configuration, the command stops without replacing it; review that change
explicitly before any new freeze.

From PowerShell, run the private experiment locally:

```powershell
python scripts/run_task2a_advanced_models.py `
  --weekly-panel data/interim/task2a_weekly_panel.csv `
  --multihorizon-table data/interim/task2a_multihorizon_train.csv `
  --feature-config configs/task2a_features.yaml `
  --validation-config configs/task2a_validation.yaml `
  --baseline-results reports/private/phase15_task2a_baselines `
  --model-config configs/task2a_advanced_models.yaml `
  --output-dir reports/private/phase16_task2a_advanced
```

Then, after inspecting the private report:

```powershell
python scripts/freeze_task2a_model_config.py `
  --advanced-config configs/task2a_advanced_models.yaml `
  --validation-config configs/task2a_validation.yaml `
  --feature-config configs/task2a_features.yaml `
  --selection reports/private/phase16_task2a_advanced/selection_decisions.json `
  --output configs/task2a_final_models.yaml
```
