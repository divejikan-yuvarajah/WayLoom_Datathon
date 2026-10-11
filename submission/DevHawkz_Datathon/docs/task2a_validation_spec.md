# Task 2A Phase 14 validation contract

The official Task 2A forecast horizon is ten weeks. WayLoom freezes a rolling-origin backtest and local metrics here before model comparison in Phase 15. The source of demand remains the Phase 11 weekly panel and the direct feature table remains Phase 13's output.

## Backtests

At each validation origin `t`, all required `(depot, brand)` series forecast the exact target weeks `t+1` through `t+10`. The default chooses the latest four eligible origins, spaced at least ten weeks apart, with at least 52 known historical weeks per series. Origins are chosen from weekly date/status coverage only. If coverage cannot support four complete windows, the build stops with `INSUFFICIENT_BACKTEST_HISTORY`; the horizon is never shortened.

Training includes a direct-table row only when **its target week is on or before `t`**. An earlier training origin alone is insufficient: its horizon could carry a still-future label. Validation includes rows whose origin is exactly `t`, once for every horizon and required series. All dates use continuous weekly dates, so ISO week 53 and year boundaries need no special arithmetic.

The planner returns a canonically sorted direct table and split indices. `validation_plan.json` records exact indices and the sort basis for subsequent model runs. Fit-dependent imputers, encoders, scalers, learned statistics and models must be fitted on `train_indices` only. The same ten-week block is predicted at once; actual outcomes from early horizons cannot update later predictors. Target-week official calendar attributes are the only permitted future-week features.

## Frozen metric contract

Total-volume model selection uses pooled MAE across all selected backtests, series and horizons. Fresh chilled selection uses Fresh-only pooled MAE. Secondary metrics are RMSE, WAPE, mean prediction bias in cubic metres, and the 90th percentile absolute error. `WAPE = 100 * sum(abs(error)) / sum(actual)`; a zero actual sum yields null. Metrics use raw, unrounded predictions. Negative values and chilled-above-total are counted diagnostically; Phase 14 does not clip or cap forecasts. Nonfinite predictions cannot receive a score.

The reusable evaluator requires the frozen plan's backtest IDs and required series as arguments. A missing backtest or series fails scoring. It reports each backtest/series, equal-weight macro series results, pooled micro results, backtest stability, and every horizon. Style and Tech chilled actuals must be exactly zero; their chilled score is marked `STRUCTURAL_ZERO` and excluded from primary chilled selection.

## Private local build

Run this command locally. It writes plan metadata only under `reports/private/phase14_task2a_validation` and prints sanitized status:

```powershell
python scripts/build_task2a_validation_plan.py `
  --weekly-panel data/interim/task2a_weekly_panel.csv `
  --multihorizon-table data/interim/task2a_multihorizon_train.csv `
  --feature-config configs/task2a_features.yaml `
  --validation-config configs/task2a_validation.yaml `
  --output-dir reports/private/phase14_task2a_validation
```
