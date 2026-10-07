# WayLoom Datathon - Data Preprocessing and Methodology

## 1. Purpose and scope

This document is the competition-facing summary of how WayLoom prepared data for Task 1 service-time and lateness prediction, Task 2A depot demand forecasting, and Task 2B peak-day allocation. It covers the final implemented pipelines only: input selection, joins, label construction, deterministic cleaning, feature engineering, leakage prevention, validation, model rationale, and optimization preparation. It does not reproduce the full source code or experiment history.

The official requirement is a brief write-up of data preparation, label construction, data cleaning, feature engineering, and rationale. Official rules are labelled **Official requirement** below. Choices that were not prescribed by the organizers are labelled **WayLoom engineering decision**. This distinction is important: the Task 1 label definitions and Task 2B feasibility rules are official, while the selected feature sets, validation mechanics, model families, and lexicographic allocation policy are engineering choices validated within the project.

The matching architecture views are the [high-level system](architecture/high_level_datathon.svg), [Task 1 pipeline](architecture/task1_pipeline.svg), [Task 2A pipeline](architecture/task2a_forecasting.svg), [Task 2B pipeline](architecture/task2b_optimization.svg), and [proposed deployment](architecture/proposed_deployment.svg). Those diagrams give the flow; this document explains the data decisions behind it. No private competition row, real identifier, private report content, or model score is reproduced here.

## 2. Input datasets

The inventory below contains only datasets used by the final core pipelines. `traffic_speed.csv` and `road_conditions.csv` exist in the official package, but their optional Task 1 feature switches are disabled in the frozen configuration, so they are not described as final predictors.

| Logical file | Competition area | Grain and key | Final use |
|---|---|---|---|
| `deliveries_train.csv` | Training Data | One row per historical order; `delivery_id` | Task 1 order context and dispatched training population; Task 2A requested-demand history |
| `route_legs_train.csv` | Training Data | One row per historical route leg; `(route_id, seq)` | Task 1 actual route events for labels and planned route context for features |
| `task1_test_inputs.csv` | Test Data | One row per planned delivery; `delivery_id` | Task 1 inference inputs and the later-order portion of Task 2A demand history |
| `route_legs_test.csv` | Test Data | One row per planned route leg; `(route_id, seq)` | Task 1 planned departure, travel, distance, and arrival context; no actual events |
| `task2a_test_inputs.csv` | Test Data | One row per depot, brand, and forecast week; `row_id` | Task 2A forecast grid, horizon identity, and output order |
| `task2b_peak_day_scenarios.csv` | Test Data | One row per peak-day order; `order_ref` | S1 demand, access, temperature, size, and priority metadata |
| `task2b_peak_day_fleet.csv` | Test Data | One row per scenario vehicle; `(scenario, vehicle_id)` | Available versus workshop status for S1 |
| `outlets.csv` | General Data | One row per outlet; `outlet_id` | Task 1 dock, parking, brand, district, depot, and delivery-window reference |
| `vehicles.csv` | General Data | One row per vehicle; `vehicle_id` | Task 1 vehicle context; Task 2B type, refrigeration, capacity, and home depot |
| `calendar.csv` | General Data | One row per date; `date` | Task 1 calendar context; official Task 2A ISO weeks and target-week context |
| `district_travel.csv` | General Data | One row per depot and district | Task 1 geography context and Task 2B outbound/inter-stop free-flow times |
| `service_allowance.csv` | General Data | One row per brand and dock type | Task 1 reference allowance and Task 2B per-stop handling time |
| `submission_task1.csv` | Submission Template | One row per Task 1 delivery | Preserves `delivery_id` and original row order; receives two predictions |
| `submission_task2a.csv` | Submission Template | One row per Task 2A forecast request | Preserves `row_id`; receives total and chilled forecasts |
| `submission_task2b.csv` | Submission Template | One row per S1 `order_ref` | Preserves scenario/order/outlet identity; receives decision, vehicle, and trip |

`check_allocation.py` is an organizer validation script rather than a dataset. It is used after WayLoom's independent Task 2B validator. Passing it confirms feasibility only, not optimality.

## 3. Shared data preparation and quality controls

The pipelines treat schema and identity as contracts rather than opportunities for silent repair. Required columns, key uniqueness, categorical domains, parseable timestamps, finite numeric values, and reference coverage are checked before derived values are created. Many-to-one and one-to-one joins declare their expected cardinality. A missing reference, duplicated right-side key, row multiplication, or missing official identity causes a failure instead of an unnoticed row drop.

| Issue or risk | Affected tasks | Implemented decision | Rationale and behavior | Rule source |
|---|---|---|---|---|
| Wrong or missing schema | All | Require named columns and valid domains before processing | Prevents a plausible-looking output from a structurally different input; fail closed | WayLoom engineering |
| Duplicate official key | All | Require unique `delivery_id`, `row_id`, or `order_ref` at its contracted grain | Protects label, forecast, and allocation identity; fail closed | Official identity plus engineering guard |
| Ambiguous reference lookup | All | Require unique reference keys and declared merge cardinality | Prevents row multiplication and arbitrary lookup selection; fail closed | WayLoom engineering |
| Date/time parsing | Task 1, Task 2A | Parse strict clocks/dates and validate chronology or ISO-week coverage | Preserves delivery-window and forecast-week meaning; fail closed | Official semantics plus engineering handling |
| Missing model feature | Task 1, Task 2A | Separate contract failures from model-level missing handling | Required references fail; permitted historical gaps remain missing for the frozen model pipeline | WayLoom engineering |
| Non-finite or impossible numeric value | All | Reject non-finite values; require nonnegative demand and positive capacities where applicable | Protects labels, ratios, forecasts, and constraints | WayLoom engineering |
| Unknown categorical value | All | Validate official domains where fixed; frozen model preprocessing handles permitted missing/unknown categories | Avoids silently reinterpreting official categories | Official domains plus engineering guard |
| Submission identity drift | All | Fill the official template and preserve required keys and row order | Keeps predictions and decisions aligned with scoring identities; fail closed | Official requirement |

The implementation does not apply a generic `drop invalid rows` rule. Task-specific eligibility is explicit: for example, Task 1 labels use dispatched `attempted` and `deferred` orders, while `not_run` has no route outcome and is intentionally excluded from Task 1 label construction. By contrast, all three statuses are retained for Task 2A requested demand. Where model preprocessing legitimately needs a representation for missing predictors, it happens only after the semantic data contract has passed.

## 4. Task 1 - service-time and lateness preparation

### 4.1 joins

The official historical relationship is:

`deliveries_train.(route_id, seq_in_route) <-> route_legs_train.(route_id, seq)`

The frozen implementation performs a left, one-to-one validated join after selecting dispatched (`attempted` or `deferred`) orders. It requires unique route-position keys, preserves the dispatched row count, rejects unmatched orders and row multiplication, and checks that the joined leg destination agrees with the order outlet. The equivalent test-time relationship is `task1_test_inputs.(route_id, seq_in_route) <-> route_legs_test.(route_id, seq)`. The official statement that every Task 1 test delivery matches exactly one test route leg is enforced rather than assumed.

Additional reference joins are many-to-one: orders to outlets on `outlet_id`; orders to vehicles on `vehicle_id`; dates to calendar rows on `date`; depot/district to district travel on `(depot, district)`; and brand/dock type to service allowance on `(brand, dock_type)`. The pipeline checks reference-key uniqueness, missing coverage, and conflicts between duplicated descriptive fields. Test joins use planned route information only.

### 4.2 label construction

**Official requirement.** Actual route events are used to construct historical targets. For an arrival timestamp `arrival_time`, delivery-window opening `window_open_time`, and completion timestamp `leave_outlet_time`:

`service_start = max(actual arrival, window opening)`

`service_minutes = leave_outlet_time - service_start`

An early vehicle therefore waits until the outlet opens, and waiting before opening is **not service time**. For lateness:

`late_flag = 1 only if actual arrival > window_close_time`

The comparison is strict. Arrival exactly at closing time is not late. A late delivery remains delivered in the supplied scenario; lateness describes its arrival boundary rather than cancellation.

**WayLoom engineering decision - midnight handling.** Clock fields are combined with the route date and processed using deterministic route-sequence rollover. When a later event clock would otherwise precede the previous event, the implementation advances the service-day offset deterministically. It checks the resolved departure-to-arrival duration against `actual_travel_duration_min` within the validated tolerance. Cross-midnight outlet windows are anchored around the resolved arrival rather than naively assigned to one calendar day. This engineering handling supports the official formulas; it is not an additional organizer rule.

Label-quality guards require complete event clocks, valid window clocks, finite and nonnegative `service_minutes`, a binary `late_flag`, and coherent event order. Regression tests cover early waiting, arrival at close, arrival after close, overnight routes, and route-leg join integrity.

### 4.3 cleaning

Dispatch status is stripped and validated against the known domain. `not_run` orders are excluded only from Task 1 labels because they lack a completed route outcome; missing route assignment on an allegedly dispatched order is a blocker. Route sequence must be numeric and nonnegative. Planned and actual times are parsed separately so test inference cannot accidentally depend on actual-event logic.

Outlet, vehicle, district-travel, calendar, and service-allowance keys must be unique. Order/reference conflicts in brand, district, depot, window, vehicle type, or temperature capability are rejected. Capacities must be positive before utilization ratios are computed. Ratio features may remain missing when a denominator is not positive, but infinite values are rejected. The final service prediction policy also fails on negative model output; the frozen Task 1 configuration does not clip or take an absolute value.

### 4.4 feature engineering

Only the frozen `safe_core_plus_history` profile is described. Road-condition and traffic-speed feature branches are disabled.

| Final feature family | Representative implemented context | Prediction-time source and transformation | Rationale |
|---|---|---|---|
| Planned timing and windows | Planned arrival/departure minute, cyclical clock terms, slack to close, early-wait minutes | Planned route leg and outlet window; date-aware calculation | Represents schedule pressure while respecting availability |
| Planned travel | Leg distance, planned travel minutes, planned leg speed | Planned route leg | Captures expected journey context without actual travel outcomes |
| Order size | Units, weight, volume, weight/unit, volume/unit, density | Order record; guarded ratios | Represents handling scale and cargo form |
| Outlet and access | Brand, district, depot, dock type, parking constraint, mall-window context | Order plus outlet reference | Represents operational context available before service |
| Vehicle and utilization | Vehicle type/temp, capacities, route weight/volume totals and utilization | Assigned planned vehicle plus planned route | Represents planned workload and capability |
| Route structure | Stop sequence, stop count, sequence fraction, first-stop flag | Planned route assignment | Captures position within the planned run |
| Prior planned workload | Cumulative prior units, weight, volume, distance, travel, and allowances | Earlier planned stops on the same route | Describes workload before the current stop without using outcomes |
| Calendar and allowance | Day/week, payday, holiday, festival, monsoon, operating status, reference service allowance | Calendar and brand/dock reference | Represents known operating context |
| Chronology-safe history | Outlet, brand, and dock historical target aggregates | Prior eligible training records only | Adds recurring service patterns without current-row outcomes |

Important derived formulas include `planned_slack_to_close_min = planned window close - planned arrival` and `planned_early_wait_min = max(0, planned window open - planned arrival)`. Route aggregates sum planned order and leg quantities, and prior-stop features use cumulative values minus the current stop. Historical transforms are fit on the eligible historical training population and transform test rows without test labels or state updates.

### 4.5 leakage prevention

Actual historical events are legitimate label sources but prohibited as direct current-row predictors. The final feature boundary rejects `actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, `leave_outlet_time`, `service_start`, `service_minutes`, and `late_flag`. It also audits feature lineage, not only column names, and requires exact train/test feature name and order parity.

Historical target-derived features are computed chronologically. During validation, their state is fit on the training portion and validation targets are not used during transform. At final inference, historical state is fit from the historical training population only; Task 1 test rows do not update that state. Planned departure, planned travel, planned arrival, static references, and known calendar context remain available at prediction time.

### 4.6 validation

**WayLoom engineering decision.** Task 1 uses stable chronological ordering, a final holdout consisting of the last 42 calendar days, and four expanding-window cross-validation folds with 42-day validation windows. Dates remain atomic so records from the same date are not split across train and validation. A minimum 180 training calendar days is required. Fit-dependent preprocessing is fit on each training portion and then applied to its validation portion.

Service-time selection uses mean absolute error as the primary metric, with RMSE, median absolute error, and tail absolute error as supporting diagnostics. Lateness probability selection uses log loss as primary and Brier score plus discrimination/calibration diagnostics as secondary evidence. Segment diagnostics are descriptive and do not replace the frozen primary selection rule.

### 4.7 final model rationale

The final service model is CatBoost regression configuration `catboost_regression_default`; the final lateness model is CatBoost classification configuration `catboost_classifier_default`. These are the frozen selections from the time-aware validation process, not claims of universal superiority. CatBoost is compatible with the mixed numeric/categorical operational feature table and avoids requiring a public expansion of every encoded category.

The service model uses no clipping: negative inference is treated as a pipeline failure. The lateness output is the positive-class probability for `late_flag = 1`. Calibration selection retained the raw probability under a chronological out-of-fold comparison, so no Platt or isotonic calibrator is claimed. The official output remains exactly `delivery_id`, `pred_service_min`, and `pred_late_prob`, with the original template identity and order preserved.

## 5. Task 2A - depot demand forecasting

### 5.1 demand-history construction

**Official requirement.** Demand history uses both `deliveries_train.csv` and `task1_test_inputs.csv`. Each source must contain one unique `delivery_id` per order, and the appended sources must remain globally unique. The implementation does not auto-deduplicate conflicting identifiers because choosing one would hide a source-contract problem.

Every requested order counts once, including `attempted`, `deferred`, and `not_run`. Demand is assigned to requested `order_date`, never to a later `dispatch_date`. Task 1 route outcomes and Task 1 predictions are not used: `task1_test_inputs` contributes demand history because each row is an order request, not because its delivery outcome is known.

### 5.2 weekly aggregation

Requested `order_date` is joined many-to-one to `calendar.date`; the official calendar supplies `iso_year` and `iso_week`. Volumes and order counts are aggregated by depot, brand, ISO year, and ISO week. Total demand sums `order_volume_m3`. Chilled demand sums only Fresh orders whose temperature requirement is chilled. Style and Tech chilled demand is exactly zero, and chilled volume may not exceed total volume.

A weekly calendar spine is built for each observed depot/brand series. Observed weeks remain observed. Only complete interior calendar gaps are classified as confirmed zero and filled with zero; boundary partial weeks and unresolved or incomplete gaps are labelled rather than guessed. Order counts and volume totals are reconciled back to the appended order universe without rounding.

### 5.3 cleaning

Both order sources require nonblank unique identifiers, parseable requested dates, supported statuses, and finite nonnegative volume. Calendar dates must be unique, ISO week must be within 1-53, and operating flags must be binary. All requested dates must match the calendar. A non-Fresh chilled source record violates the strict frozen policy and fails validation rather than being silently reclassified.

The weekly panel rejects duplicate series/week keys, non-finite or negative targets, chilled above total, unresolved gaps, and failed reconciliation. Missing lag or rolling values caused by insufficient history are deliberately kept missing; the pipeline forbids future backfill and full-history imputation.

### 5.4 forecasting features

The final method builds one direct-global table across depot/brand series and horizons 1 through 10.

| Final feature family | Implemented values | Availability and rationale |
|---|---|---|
| Series identity | Depot and brand | Static grouping context shared by the global models |
| Forecast horizon | `horizon_weeks` from 1 to 10 | Lets one model represent different lead times directly |
| Demand lags | Total and chilled lags 1, 2, 4, 13, 52 | Origin-relative known demand; captures recent and seasonal context |
| Rolling demand | Trailing means over 4, 8, 13 weeks | Smooths short- and medium-window history; full window required |
| Trend proxies | 4-week minus 13-week mean and guarded ratio | Represents recent movement relative to a longer baseline |
| History depth | Weeks available at the origin | Distinguishes mature from shorter series histories |
| Target-week calendar | Operating/weekend/payday/holiday/festival/monsoon aggregates | Known calendar context for the forecasted week |

For this implementation, “lag 1” is the known demand at the forecast origin; larger lags move backward from that origin. Rolling windows are trailing and inclusive of the origin. The source lineage records the latest demand week used and requires it to be no later than the forecast origin.

### 5.5 leakage prevention

Targets and origin/target metadata are excluded from the predictor registry. Future actual demand is never used to form features for an earlier origin. Lag, rolling, and trend values are independently recomputed from the canonical weekly panel during audit, and their recorded source bound must be at or before the origin.

Rolling validation preserves chronology and fits model-dependent preprocessing only on each training fold. For LightGBM components, numeric median imputation and categorical one-hot encoding are fit on the fold training rows; unknown categories are ignored at transform. CatBoost components use their frozen native-categorical path. Target-week calendar fields are allowed because the calendar is known in advance, while future realized volume is not.

### 5.6 rolling validation

**WayLoom engineering decision.** Validation uses four deterministic rolling origins. Each origin evaluates the complete next 10 weeks, advances in 10-week steps, shares origins across series, and requires at least 52 training weeks. Training eligibility requires every target week and demand-feature source week to be on or before the relevant origin contract.

Mean absolute error is primary for both total and Fresh chilled volume. RMSE, weighted absolute percentage error, mean bias, and tail absolute error are supporting diagnostics. Chilled scoring is evaluated on Fresh, while Style and Tech are separately checked as structural zeros. Raw predictions are diagnosed before final postprocessing so clipping does not disguise unstable candidates.

### 5.7 final forecasting methodology and model rationale

The frozen strategy is `direct_global_table_separate_target_ensembles`. Total volume and Fresh chilled volume are modelled separately. Each target uses an equal-weight 50/50 ensemble of CatBoost and LightGBM: `ensemble_cb_lgb_total_equal_v1` for total and `ensemble_cb_lgb_chilled_equal_v1` for Fresh chilled. This documents the final time-aware selection outcome, not a claim that the ensemble is universally best. The two tree families provide complementary representations while sharing the same origin-safe business feature contract.

Final inference uses one latest complete global historical origin and generates direct forecasts for horizons 1-10. Fresh rows receive chilled-model predictions; Style and Tech start at structural zero. Non-finite raw predictions fail. The frozen postprocessing then clips negative total/chilled predictions to zero, caps chilled at total, and reasserts Style/Tech chilled zero. No rounding is applied. The official `row_id` and template order are preserved in `submission_task2a.csv` with exactly `pred_total_volume_m3` and `pred_chilled_volume_m3`.

## 6. Task 2B - peak-day allocation preparation

Task 2B does **not require a trained model**. It is deterministic scenario optimization over supplied S1 orders, fleet availability, and reference tables. Compatibility indicators, trip-time coefficients, capacity/time limits, and priority metadata are derived optimization inputs, not ML features.

### 6.1 scenario inputs

The pipeline explicitly filters scenario S1 and requires the expected Peliyagoda depot. `order_ref` is the allocation key; duplicate outlet identifiers are allowed because one outlet can have multiple orders. Orders require nonblank identity/context, supported temperature and access domains, nonnegative finite weight/volume, and validated previous-deferral metadata.

Fleet status must be either `available` or `in_workshop`. Only available vehicles enter the candidate fleet, workshop vehicles are excluded, and the usable fleet is further restricted to vehicles whose reference home depot matches Peliyagoda. Vehicle references require unique identifiers, valid type/temperature categories, and positive weight and volume capacities.

### 6.2 compatibility preparation

The implementation creates the order-by-usable-vehicle candidate matrix and evaluates five pairwise conditions: chilled orders require reefer capability; `van_only` outlets require a van; home depot must match; the whole order must fit vehicle weight capacity; and it must fit vehicle volume capacity. Failure reasons are retained for audit. Compatible-vehicle counts provide low-flexibility metadata for the engineering policy, but do not override feasibility.

At trip grouping time, orders sharing vehicle and trip must also have the same brand and district. An order is assigned whole to at most one vehicle/trip; no split is allowed. The optimizer separately enforces aggregate trip weight and aggregate trip volume.

### 6.3 trip-time calculation

**Official requirement.** For a same-brand, same-district trip with `num_orders` stops:

`trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)`

Outbound travel is counted exactly once. Inter-stop travel is zero for one order and uses one fewer journey than stops. Each stop's service allowance is looked up by `(brand, dock_type)`. No return journey is added because the official budgets already allow for it. The public booklet regression example for three Fresh Gampaha orders totals 101 minutes; this is an official illustrative calculation, not a private scenario disclosure.

### 6.4 hard-feasibility preparation

The seven official rule groups are kept distinct and independently auditable:

1. Every trip contains one brand and one district.
2. Chilled orders use reefer vehicles; reefers may also carry ambient goods.
3. A `van_only` outlet uses a van.
4. A vehicle serves only its home depot.
5. A served order is whole and assigned once; it is not split.
6. Both trip weight and trip volume stay within capacity.
7. Each vehicle runs at most two trips; its Fresh trips total at most 270 minutes and its Style plus Tech trips total at most 480 minutes.

Fuel quota and delivery window are not Task 2B hard constraints in the supplied allocation task. Task 1 lateness predictions and Task 2A forecasts are also not imported as hard rules. Adding any of these would change the official feasibility problem.

### 6.5 WayLoom priority preparation

**WayLoom engineering decision - not organizer priority.** After feasibility, the frozen lexicographic policy solves nine objectives sequentially:

1. Maximize served order count.
2. Maximize served previous-deferred count.
3. Maximize served waiting-days sum.
4. Maximize served low-flexibility count.
5. Maximize served Fresh chilled count.
6. Maximize served Fresh count.
7. Minimize avoidable reefer-van assignments.
8. Minimize avoidable reefer assignments.
9. Minimize avoidable van assignments.

The last three are the policy's 7A/7B/7C conservation levels. `hard_rule_override` is false: a priority never makes an infeasible assignment permissible. The hierarchy is transparent and deterministic so the written policy can explain trade-offs without inventing monetary costs.

### 6.6 optimizer / independent validation / official export

The optimizer uses deterministic OR-Tools CP-SAT with binary serve/defer and compatible assignment variables, trip-use/group structure, capacity/time constraints, a fixed seed, and one search worker. Each lexicographic stage fixes the previous optimum before solving the next. All nine stages must be `OPTIMAL` before the canonical allocation can be frozen; feasible-only termination is insufficient for the project freeze gate.

After solving, an independent solution audit and deterministic evidence are recorded. Phase 23 then applies a separate solver-neutral validator to identity, decision domains, fleet availability, refrigeration, access, home depot, whole-order assignment, same-brand/district grouping, both capacities, exact trip time, trip count, and daily budgets. The organizer `check_allocation.py` is run on a private exact-column candidate and validates feasibility only; it does not prove optimality.

The frozen allocation is exported through the official template without changing scenario, `order_ref`, outlet identity, or row order. The exact six columns are `scenario`, `order_ref`, `outlet_id`, `decision`, `vehicle_id`, and `trip_id`. Served rows require vehicle and trip 1 or 2; deferred rows leave both blank. The written prioritization policy is a separate document.

## 7. Reproducibility and data-safety controls

Final model and optimizer choices are stored in versioned YAML configs. Model training and optimization use deterministic seeds; CP-SAT uses one worker. Saved model bundles carry their feature schema/metadata, and inference refuses ad-hoc features or retraining. Task 2A checks its frozen feature-registry hash before final fitting. Submission writers use canonical templates, validate read-back structure, preserve identity/order, and use controlled writes.

Task 2B adds allocation and trip-summary hash checks, freeze overwrite protection, deterministic evidence, an independent validator, and the organizer checker. These controls distinguish reproducibility evidence from modelling claims: a hash protects artifact identity, while validation establishes semantic correctness.

Execution is local over private competition data. The preprocessing manifest and this document are generated from safe tracked configs and source code only. They contain no private rows, real identifiers, raw data excerpts, private report contents, credentials, or absolute user paths. No proprietary external prediction or preprocessing API is required. The optional Phase 28 integration contract and optional later explainability/uncertainty components do not alter official Task 1, Task 2A, or Task 2B outputs.

## 8. Final preprocessing summary

Task 1 joins each dispatched historical order to exactly one route leg, constructs waiting-aware service minutes and a strict-after-close late label, and transforms prediction-time planned/reference/history context under chronological validation. Its frozen outputs come from two CatBoost configurations, with raw lateness probability and a fail-on-negative service policy.

Task 2A constructs requested demand from both required order sources, retains attempted/deferred/not-run orders, maps requested dates to official ISO weeks, and builds origin-safe lag, rolling, trend, horizon, and target-calendar features. Four rolling origins select separate equal-weight CatBoost/LightGBM ensembles for total and Fresh chilled volume, followed by the frozen nonnegative/chilled constraints.

Task 2B validates S1 order and fleet identity, builds capability/capacity compatibility, calculates the official no-return trip duration, enforces all seven feasibility groups, and applies a separate WayLoom lexicographic policy in deterministic CP-SAT. Independent and organizer feasibility checks precede the exact six-column export. Across all tasks, the governing principle is to fail on contract ambiguity, preserve official identities, and keep private competition records out of documentation.
