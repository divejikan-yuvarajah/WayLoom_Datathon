# Phase 27 — Forecast uncertainty

## Scope

This optional WayLoom engineering layer adds private uncertainty artifacts around the frozen Task 1 service-time and Task 2A demand point predictions. Official CSV schemas and point predictions remain unchanged.

## Task 1 service uncertainty method

The service interval uses 19917 out-of-sample expanding-fold residuals from the frozen Phase 7/9 validation procedure. For each target coverage, the additive score is the finite-sample higher order statistic of absolute residuals. Lower bounds are clipped at zero. Independent coverage evaluation is not available; calibration residual coverage is not presented as independent evidence.

## Task 2A forecast uncertainty method

The forecast intervals use frozen Phase 16 rolling-origin OOS predictions with Phase 17 post-processing. Calibration is horizon-specific when sample size permits and otherwise uses the predeclared pooled-target fallback. The targets are total volume and Fresh chilled volume. Style and Tech chilled intervals remain exactly [0,0].

## Coverage and interval diagnostics

Sequential historical backtest diagnostics calibrate each evaluated origin only from earlier eligible origins. Available diagnostic groups: 120. These are empirical historical diagnostics, not guaranteed future coverage.

## Physical constraints

All bounds are nonnegative. Raw Fresh chilled bounds are retained, and a separate presentation-coherent view clips chilled upper bounds to total upper bounds. That transformation is not claimed to preserve unchanged marginal coverage.

## Limitations

Intervals are conformal-style residual intervals conditional on historical error behavior. Time dependence, distribution shift, festival/payday/monsoon regimes, and Task 1 heteroscedasticity can make future uncertainty differ. No universal finite-sample or probabilistic coverage guarantee is claimed.

## Official schema guard

`submission_task1.csv` remains `delivery_id,pred_service_min,pred_late_prob`. `submission_task2a.csv` remains `row_id,pred_total_volume_m3,pred_chilled_volume_m3`. Unofficial interval fields are written only below `reports/private/phase27_uncertainty/`.
