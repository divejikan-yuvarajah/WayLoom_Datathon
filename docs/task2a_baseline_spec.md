# Task 2A Phase 15 baselines

Phase 15 evaluates only four fixed, transparent baselines on the frozen Phase 14 rolling-origin plan. It creates no origins and does not fit an advanced model.

For each origin, baseline state is built from the canonical weekly panel where `week_start_date <= origin_week_start_date`. Total candidates are `total_last_week`, `total_recent_mean_4`, `total_same_week_last_year`, and `total_seasonal_recent_weighted`. Recent mean uses the four trailing weeks through the origin. Seasonal lookup uses `(target_iso_year - 1, target_iso_week)` for the same depot and brand, never a blind 52-week shift; unavailable seasonal values fall back to the recent mean. The weighted baseline is fixed at 0.50 recent plus 0.50 seasonal, with the same frozen fallback.

Fresh chilled candidates use chilled history independently. Style and Tech chilled predictions are exactly zero. Predictions are evaluated raw: no rounding, clipping, or chilled-to-total cap occurs in Phase 15.

Candidate selection uses pooled Phase 14 MAE, then RMSE, P90 absolute error, backtest-MAE standard deviation, and fixed simplicity order. The result is a reference baseline for Phase 16 comparison, never a final Task 2A model.

The local command writes only private artifacts under `reports/private/phase15_task2a_baselines` and prints sanitized status.
