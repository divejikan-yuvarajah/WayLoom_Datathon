# WayLoom Results Summary

> **Status:** PREPARATORY FINAL DRAFT — SAFE EVIDENCE ONLY; FRESH PHASE 37 INDEPENDENT REVIEW PENDING.  
> **Scope:** Internal competition-evidence summary, **not approved for public or demo release**. Do not publish, link from public materials, or distribute it as an organizer-approved result. This is not an additional organizer deliverable, a leaderboard result, or formal Phase 37 closure.  
> **Privacy:** No competition row, identifier, private notebook output, or confidential forecast value is reproduced here.

## Evidence policy

Every result below is either (a) an already tracked repository aggregate with a named source, or (b) explicitly `NOT AVAILABLE`. A configured metric or a passing schema/checksum test is not presented as model accuracy. The official judging weights are rubric weights, not measured scores. Detailed provenance appears in [RESULTS_EVIDENCE_INDEX.md](RESULTS_EVIDENCE_INDEX.md).

## DT-464 — Produce final Task 1 metrics table

The repository specifies a chronological final holdout of the latest 42 days and four expanding-window validation folds. It defines MAE and RMSE for service time and log loss, Brier score, ROC-AUC and calibration diagnostics for lateness. No safe, approved aggregate values for those metrics are present in the tracked evidence package.

| Target | Metric | Definition | Unit | Evaluation split | Result |
|---|---|---|---|---|---|
| Service time | MAE | mean absolute error on raw predictions | minutes | chronological validation/final 42-day holdout | **NOT AVAILABLE** |
| Service time | RMSE | square root of mean squared error on raw predictions | minutes | chronological validation/final 42-day holdout | **NOT AVAILABLE** |
| Late probability | Log loss | binary cross-entropy for the positive class `arrival_dt > window_close_dt` | unitless | chronological validation/final 42-day holdout | **NOT AVAILABLE** |
| Late probability | Brier score | mean squared probability error | unitless | chronological validation/final 42-day holdout | **NOT AVAILABLE** |
| Late probability | ROC-AUC | ranking discrimination for the same positive class | unitless | chronological validation/final 42-day holdout | **NOT AVAILABLE** |

Service time starts at `max(arrival_dt, window_open_dt)`, so early waiting is excluded. Arrival exactly at close is not late. There is no organizer test-label or leaderboard accuracy claim.

## DT-465 — Compare Task 1 baseline vs final model

The frozen selection configuration records a CatBoost service-time model and a CatBoost lateness classifier with raw calibration, and records that baseline/final comparison was completed during model selection. The tracked safe package does not contain approved numerical baseline and final metrics. Therefore absolute scores, percentage improvement, and claims such as “outperformed by X%” are **NOT AVAILABLE**.

| Comparison | Baseline | Frozen final | Numerical result |
|---|---|---|---|
| Service time | configured validation baselines | CatBoost regressor | **NOT AVAILABLE** |
| Late probability | configured validation baselines | CatBoost classifier; raw probability policy | **NOT AVAILABLE** |

## DT-466 — Produce calibration visualization

**Visualization status: NOT AVAILABLE.** The repository defines lateness calibration diagnostics but contains no approved public calibration-bin table or curve data. Rendering a reliability diagram from invented, private, or reconstructed values would be misleading. A proposed future chart specification is: predicted-probability bins on the x-axis, observed late rate on the y-axis, a diagonal reference, bin counts, split identifier, and the same strict late-positive definition used above.

## DT-467 — Produce Task 1 feature explanation

The existing tracked SHAP summary identifies the following highest global mean-absolute-SHAP features:

| Model | Highest-ranked features in tracked order |
|---|---|
| Service time | `outlet_prior_service_median`, `festival_ramp`, `order_volume_m3`, `monsoon`, `order_weight_kg` |
| Late risk | `planned_slack_to_close_min`, `monsoon`, `outlet_prior_late_rate`, `planned_arrival_cos`, `prior_planned_units` |

Mean absolute SHAP describes attribution strength, not a universal direction or causal effect. Late-model SHAP values are in raw-margin log-odds and are not probability-point changes. Correlation, redundancy and interactions can distribute attribution among features.

These rankings remain internal evidence. No explicit owner authorization for public release is recorded in the Phase 37 claim package, so they are not selected as a public/demo asset.

## DT-468 — Produce Task 2A backtesting results

The frozen validation design uses the latest four eligible rolling origins, at least ten weeks apart, with a complete ten-week horizon and at least 52 historical weeks per series. Total-volume selection uses pooled MAE; Fresh chilled selection uses Fresh-only pooled MAE. RMSE, WAPE, bias in cubic metres and 90th-percentile absolute error are secondary diagnostics.

| Target | Metric | Horizon and aggregation | Result |
|---|---|---|---|
| Total volume | pooled MAE | four rolling origins; all required depot/brand series; horizons 1–10 | **NOT AVAILABLE** |
| Total volume | RMSE / WAPE / bias / P90 absolute error | same frozen backtests | **NOT AVAILABLE** |
| Fresh chilled volume | pooled Fresh-only MAE | same frozen backtests | **NOT AVAILABLE** |
| Fresh chilled volume | RMSE / WAPE / bias / P90 absolute error | same frozen backtests | **NOT AVAILABLE** |

History combines the two official order sources, counts each order once including deferred/not-run demand, and assigns demand by requested-date ISO year/week. Cross-source duplicate order keys must fail closed. Style and Tech chilled demand are structural zeros and are excluded from Fresh chilled model selection.

## DT-469 — Compare Task 2A baselines/final model

The frozen final configuration uses 50/50 CatBoost and LightGBM ensembles for total and Fresh chilled volume. It records that comparison and selection were completed. Approved baseline-versus-final numerical values are **NOT AVAILABLE**, so no error reduction or winning margin is claimed.

| Target | Compared candidates | Frozen final | Numerical result |
|---|---|---|---|
| Total volume | configured baselines and candidate models | 50/50 CatBoost + LightGBM | **NOT AVAILABLE** |
| Fresh chilled volume | configured baselines and candidate models | 50/50 CatBoost + LightGBM | **NOT AVAILABLE** |

The fixed inference policy creates the ten-week grid, sets Style/Tech chilled to zero, clips negative predictions, and caps chilled at total. These are output constraints, not predictive-accuracy evidence.

## DT-470 — Produce future-demand chart

**Visualization status: NOT AVAILABLE.** The frozen official forecast values are confidential and this repository contains no approved public aggregate chart series. The chart must not be reconstructed from the official submission. If an authorized aggregate is later supplied, the specification is a ten-week line chart by brand (and depot only where disclosure-safe), with total and chilled cubic metres clearly separated, structural Style/Tech chilled zeros labelled, and no row IDs or small-cell slices.

## DT-471 — Produce Task 2B scarcity summary

The tracked policy reports the following aggregate constraint picture for Scenario S1. The YAML manifest is the authoritative Phase 37 numerical-claim register. These values are retained as internal competition evidence; a tracked source does not establish publication approval, which remains `PENDING` for public or demo use.

| Claim ID | Scarcity indicator | Value | Unit |
|---|---|---:|---|
| N-T2B-007 | Usable home-depot vehicles | 28 | vehicles |
| N-T2B-008 | Usable reefers | 4 | vehicles |
| N-T2B-009 | Usable reefer vans | 1 | vehicles |
| N-T2B-010 | Workshop-unavailable vehicles | 10 | vehicles |
| N-T2B-011 | Used trip slots | 44 | trip slots |
| N-T2B-012 | Theoretical trip slots | 56 | trip slots |
| N-T2B-013 | Peak Fresh vehicle time | 268 | minutes |
| N-T2B-014 | Fresh vehicle time limit | 270 | minutes |
| N-T2B-015 | Peak Style plus Tech vehicle time | 183 | minutes |
| N-T2B-016 | Style plus Tech vehicle time limit | 480 | minutes |
| N-T2B-017 | Peak trip weight loading | 99.2 | percent |
| N-T2B-018 | Peak trip volume loading | 99.7 | percent |
| N-T2B-019 | Deferred orders with no compatible available vehicle | 1 | orders |
| N-T2B-020 | Deferred orders with an individually compatible vehicle but allocation tradeoffs | 5 | orders |

The final row describes orders that still competed for legal brand/district trips, whole-order capacity, trip slots and vehicle time. It does not prove a single-resource counterfactual cause or global optimality.

## DT-472 — Produce served/deferred summary

| Claim ID | Outcome or impact | Value | Unit |
|---|---|---:|---|
| N-T2B-001 | Served whole orders | 79 | orders |
| N-T2B-002 | Total Scenario S1 orders | 85 | orders |
| N-T2B-003 | Deferred whole orders | 6 | orders |
| N-T2B-004 | Served share rounded to one decimal place | 92.9 | percent |
| N-T2B-005 | Deferred share rounded to one decimal place | 7.1 | percent |
| N-T2B-006 | Total outcome share | 100.0 | percent |
| N-T2B-021 | Previously deferred orders | 10 | orders |
| N-T2B-022 | Previously deferred orders served | 9 | orders |
| N-T2B-023 | Previously deferred orders still deferred | 1 | orders |
| N-T2B-024 | Deferred Fresh orders | 5 | orders |
| N-T2B-025 | Deferred Style orders | 1 | orders |
| N-T2B-026 | Outlets affected by deferral | 6 | outlets |
| N-T2B-027 | Deferred demand units | 1,188 | units |
| N-T2B-028 | Deferred demand weight | 9,770.9 | kg |
| N-T2B-029 | Deferred demand volume | 81.57 | m3 |
| N-T2B-030 | Chilled deferred orders | 5 | orders |
| N-T2B-031 | Chilled deferred volume | 40.91 | m3 |
| N-T2B-032 | Mean deferred-order wait | 2 | days |
| N-T2B-033 | Maximum deferred-order wait | 5 | days |

These are tracked internal aggregates, not newly computed row-level results. They are not selected for public release while publication approval remains pending. The data contains no monetary cost field, so no currency impact is claimed.

## DT-473 — Produce solver/checker evidence

The frozen allocation was reported as passing both the independent validator and the inspected official checker in the Phase 33 completion record and corresponding master-plan closure. This is recorded human-local execution evidence subsequently accepted during the Phase 33 independent closure review; the Phase 37 remediation did not rerun the private official checker. The validator contract checks S1 coverage, whole-order decisions, vehicle/trip fields, compatibility, one brand and district per trip, volume/weight capacity, at most two trips, the outbound-plus-interstop-plus-service time formula with no return leg, and combined 270-minute Fresh / 480-minute Style+Tech budgets.

**Interpretation boundary:** the official checker demonstrates feasibility against its implemented rules. It does not prove a unique global optimum, a competition rank, or a judging score.

## DT-474 — Select only strongest charts for demo

No Phase 37 result chart or numerical table is currently selected for public/demo release. The Task 1 feature explanation and Task 2B aggregate tables are internal candidates only because explicit owner publication approval is not recorded. Architecture/process visuals already independently reviewed in Phase 36 may be used according to their existing scope, but they are not reclassified as Phase 37 result evidence here.

Do **not** show a Task 1 calibration curve, Task 1 metric comparison, Task 2A backtest score chart, future-demand chart, SHAP ranking, or Task 2B numerical table until the corresponding aggregate source and publication approval are recorded. This fail-closed shortlist prevents an unapproved internal claim from becoming a public result.

## Limitations and review status

- Task 1 numerical validation results: **NOT AVAILABLE** in approved tracked evidence.
- Task 2A numerical backtest results and public forecast series: **NOT AVAILABLE**.
- Official submission integrity and saved-model checks do not substitute for accuracy metrics.
- Task 2B results are frozen-policy aggregates; feasibility does not imply optimality.
- Task 1 feature rankings and Task 2B numerical aggregates remain internal evidence; public/demo publication approval is pending.
- Phase 35 organizer guidance is incident-specific and is not a blanket competition-rule exemption.
- Phase 37 master tasks, phase-complete status and readiness remain open until a fresh independent read-only review and subsequent authorized administrative closure.
