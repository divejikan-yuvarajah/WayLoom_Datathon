# Task 2A Phase 13 feature specification

Phase 13 builds origin-safe features for direct, 1-to-10-week Task 2A demand forecasts. It consumes the validated Phase 11 weekly panel and uses Phase 12's canonical official-calendar aggregation.

## Timing contract

An origin is a known weekly demand row at time `t`. For each origin and horizon `h` (1 through 10), the direct training target is demand at `t+h`.

- `total_lag_1` and `chilled_lag_1` are the observed values at `t`.
- `lag_k` is the value at `t-(k-1)`; no later value is read or back-filled.
- Rolling means are trailing and include the origin: a 4-week mean uses `t-3:t`.
- Trend features compare the safe trailing 4- and 13-week means. Ratios are null when the long mean is zero or unavailable; infinity is never emitted.
- Target-week calendar predictors are allowed because they are taken only from the supplied official daily calendar. Phase 13 calls `build_weekly_calendar_context` from Phase 12 rather than reimplementing daily aggregation.

Every row carries `depot`, `brand`, and `horizon_weeks`. For a fixed series and origin, all demand-derived predictors are identical across horizons. Only horizon, target-week calendar context, target-week metadata, and target labels can differ.

## Labels and eligibility

The only labels are `target_total_volume_m3` and `target_chilled_volume_m3`. They are excluded from the registry feature matrix. A target row is admitted only when its Phase 11 status is `OBSERVED_DEMAND` or `CONFIRMED_ZERO`; boundary-partial, unresolved, and incomplete rows cannot become training labels.

The input validator enforces unique depot/brand/ISO-week keys, a continuous weekly chronology, finite nonnegative totals, Fresh chilled bounded by total, and exact zero chilled demand for Style and Tech.

## Registry and outputs

`feature_registry.json` records each field's source, availability time, transformation, null policy, type, selection status, and leakage risk. The local build also writes `leakage_audit.json`, which independently reconciles every demand-derived predictor to the Phase 11 panel at its origin. Origin and multi-horizon tables are private derived data under `data/interim`; reports are confined to `reports/private/phase13_task2a_features` and contain metadata only.

## Local operator command

```powershell
python scripts/build_task2a_features.py `
  --weekly-panel data/interim/task2a_weekly_panel.csv `
  --raw-root data/raw `
  --manifest configs/dataset_manifest.yaml `
  --history-config configs/task2a_history.yaml `
  --feature-config configs/task2a_features.yaml `
  --origin-output data/interim/task2a_origin_features.csv `
  --multihorizon-output data/interim/task2a_multihorizon_train.csv `
  --report-dir reports/private/phase13_task2a_features
```

The command prints only sanitized status and counts. Do not share the resulting private files.
