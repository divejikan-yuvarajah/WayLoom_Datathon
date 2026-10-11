# PHASE 13 — Task 2A Forecasting Features

> **Canonical file:** `PHASE_13_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-204 → DT-221**  
> **Task count:** **18**  
> **Phase dependency:** **Phase 11; Phase 12 informs feature selection**  
> **Default priority:** P1  
> **Execution style:** controlled feature-engineering implementation with synthetic tests; real competition-data build is human-local  
> **Phase gate:** **Every forecast feature is either past-known at the forecast origin or known from the official calendar for the target week. No future actual demand may enter predictors.**

---

# 1. Phase purpose

Phase 13 converts the canonical weekly demand history built in Phase 11 into a leakage-safe forecasting feature system for Task 2A.

The phase must support the competition's 10-week forecast problem without borrowing actual demand from any week that would still be unknown at prediction time.

The core design is a **direct multi-horizon table**:

```text
series = depot + brand
forecast origin = latest week whose demand is known
horizon = 1..10
target week = origin + horizon weeks

predictors =
    demand information known on/before origin
    + official calendar information known for target week
    + depot
    + brand
    + forecast horizon

targets =
    target week's actual historical total volume
    target week's actual historical chilled volume
```

For example, for a historical origin at week `t`:

```text
h = 1  → target = demand at t+1
h = 5  → target = demand at t+5
h = 10 → target = demand at t+10
```

A horizon-10 row may use demand through week `t`, but it must **not** use actual demand from `t+1` through `t+9` as features.

That rule is the main safety boundary of this phase.

---

# 2. Finalized master task inventory

| Status | Task | Mark | Priority | Work item |
|---|---|---:|---:|---|
| [ ] | **DT-204** | [E] | P1 | Create lag-1 feature |
| [ ] | **DT-205** | [E] | P1 | Create lag-2 feature |
| [ ] | **DT-206** | [E] | P1 | Create lag-4 feature |
| [ ] | **DT-207** | [E] | P2 | Create lag-13 feature |
| [ ] | **DT-208** | [E] | P1 | Create lag-52 feature |
| [ ] | **DT-209** | [E] | P1 | Create rolling 4-week mean |
| [ ] | **DT-210** | [E] | P1 | Create rolling 8-week mean |
| [ ] | **DT-211** | [E] | P2 | Create rolling 13-week mean |
| [ ] | **DT-212** | [E] | P2 | Create trend features |
| [ ] | **DT-213** | [E] | P1 | Add future operating-day count |
| [ ] | **DT-214** | [E] | P1 | Add future payday count |
| [ ] | **DT-215** | [E] | P1 | Add future holiday/festival features |
| [ ] | **DT-216** | [E] | P1 | Add future festival-ramp features |
| [ ] | **DT-217** | [E] | P1 | Add monsoon features |
| [ ] | **DT-218** | [E] | P1 | Add depot |
| [ ] | **DT-219** | [E] | P1 | Add brand |
| [ ] | **DT-220** | [E] | P1 | Add forecast horizon |
| [ ] | **DT-221** | [E] | P2 | Build direct multi-horizon modelling table |

**Phase complete:** [ ]  
**READY FOR PHASE 14:** NO

---

# 3. Official Task 2A contract that Phase 13 must preserve

The official Task 2A problem is a ten-week weekly volume forecast.

The required predictions are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

The official historical-demand rules already enforced in Phase 11 remain immutable:

```text
history sources:
    deliveries_train.csv
    task1_test_inputs.csv

order identity:
    delivery_id

count:
    every unique requested order once
    including attempted, deferred and not_run

demand week:
    requested order_date

weekly grouping:
    calendar.iso_year + calendar.iso_week

chilled rule:
    Fresh may have chilled demand
    Style chilled = 0
    Tech chilled = 0
```

The official calendar provides future/historical context including:

```text
date
dow
dow_name
is_weekend
iso_year
iso_week
is_payday
festival
festival_ramp
is_holiday
monsoon
is_operating
```

The official challenge does **not** prescribe lag values, rolling windows, trend formulas, or a direct multi-horizon modelling architecture. Those are WayLoom engineering decisions from the finalized master plan.

Therefore this phase must clearly separate:

```text
OFFICIAL:
10-week depot + brand forecasting problem and official data/calendar semantics

WAYLOOM ENGINEERING:
lag definitions
rolling windows
trend definitions
feature naming
missing-history handling
direct multi-horizon table design
```

---

# 4. Frozen inputs from earlier phases

## 4.1 Canonical Phase 11 weekly history

Primary input:

```text
data/interim/task2a_weekly_panel.csv
```

Expected grain:

```text
one row per:
    depot
    brand
    iso_year
    iso_week
```

Recommended canonical ordering key:

```text
depot
brand
week_start_date
```

Required historical target columns:

```text
total_volume_m3
chilled_volume_m3
```

Phase 13 must **reuse** this panel.

Do not rebuild demand from raw orders using new logic.

## 4.2 Phase 12 EDA handoff

Phase 12 is advisory for candidate selection and diagnostics.

Useful private conclusions may inform whether optional features are enabled, but Phase 13 must not hard-code private EDA values into tracked source files.

Use Phase 12 only for questions such as:

```text
Is lag-52 sufficiently available?
Are short rolling means worth retaining?
Do calendar event features have enough support?
Are trend features stable enough to test?
```

Do not copy private historical demand statistics into source code.

## 4.3 Official calendar

Use:

```text
calendar.csv
```

through the canonical manifest/path layer.

The calendar is authoritative for:

```text
iso_year
iso_week
is_operating
is_payday
festival
festival_ramp
is_holiday
monsoon
```

Do not substitute external calendars.

---

# 5. Phase 13 outputs

Tracked implementation:

```text
src/task2a/
├── features.py
├── calendar_features.py
└── multihorizon.py

scripts/
└── build_task2a_features.py

configs/
└── task2a_features.yaml

docs/
└── task2a_feature_spec.md

tests/
├── test_task2a_features.py
└── test_task2a_multihorizon.py
```

If `src/task2a/calendar_features.py` or equivalent logic already exists from Phase 12, extend/reuse it rather than duplicating the calendar aggregation.

Private local outputs:

```text
data/interim/task2a_origin_features.csv

data/interim/task2a_multihorizon_train.csv

reports/private/phase13_task2a_features/
├── build_summary.json
├── feature_coverage.json
├── lag_validation.json
├── rolling_validation.json
├── target_week_calendar_validation.json
├── multihorizon_validation.json
├── leakage_audit.json
├── feature_registry.json
└── phase13_feature_report.md
```

No private Phase 13 table should be committed.

---

# 6. Core forecasting-time semantics

This definition is mandatory for the WayLoom Phase 13 implementation.

For every historical series:

```text
series_key = (depot, brand)
```

For every usable origin week `t`:

```text
origin week = latest week whose actual demand is assumed known
```

For each horizon:

```text
h ∈ {1,2,...,10}
```

Define:

```text
target_week = origin_week + h calendar weeks
```

## 6.1 What is allowed in predictors

At forecast origin `t`, predictors may use:

```text
historical demand at t, t-1, t-2, ...
static depot/brand identity
official calendar context for target week t+h
forecast horizon h
```

## 6.2 What is forbidden

For a row with horizon `h`, predictors must not use:

```text
actual target volume at t+h
actual chilled target at t+h
actual demand from any future week after t
rolling features that include t+1 ... t+h
future demand-derived trend
future actual demand from another series if it is not known at origin
```

Example:

```text
origin = week 20
horizon = 10

the model may use demand through week 20
it must not use actual demand from weeks 21–29
```

---

# 7. Canonical time axis

Never calculate lags purely by previous row position unless weekly continuity has been validated.

Required approach:

```text
1. validate one row per series/week
2. validate chronological ordering
3. validate unresolved Phase 11 gaps = 0
4. use week_start_date or another canonical continuous weekly index
5. sort by series + chronological week
6. then apply groupwise shifts/rolling windows
```

A one-row shift is valid only after confirming that consecutive rows represent consecutive calendar weeks.

If the panel has an unresolved missing week:

```text
STOP
```

Do not let:

```text
week 10 → week 12
```

behave as if week 12 were the immediate next week.

---

# 8. Canonical demand feature semantics

Phase 13 should build demand-history features for both target families where meaningful.

Recommended naming:

```text
total_lag_1
total_lag_2
total_lag_4
total_lag_13
total_lag_52

chilled_lag_1
chilled_lag_2
chilled_lag_4
chilled_lag_13
chilled_lag_52

total_roll_mean_4
total_roll_mean_8
total_roll_mean_13

chilled_roll_mean_4
chilled_roll_mean_8
chilled_roll_mean_13
```

For Style and Tech, chilled historical demand should already be exact zero, so chilled lags/rolling values should remain zero once sufficient history exists.

Do not create nonzero Style/Tech chilled features from imputations.

---

# 9. Lag definition used by the direct multi-horizon design

The master plan calls these lag-1, lag-2, lag-4, lag-13 and lag-52 features.

In this implementation, lag values are defined **relative to the forecast origin**, not relative to the unknown target week.

At origin week `t`:

```text
lag_1  = y[t]
lag_2  = y[t-1]
lag_4  = y[t-3]
lag_13 = y[t-12]
lag_52 = y[t-51]
```

This convention means:

```text
lag_1 = most recent known weekly demand at prediction time
```

It prevents a horizon-10 row from accidentally using demand from week `t+9`.

Implementation option:

If features are first calculated on weekly rows where row `t` represents the forecast origin, then:

```text
lag_1  = series.shift(0)
lag_2  = series.shift(1)
lag_4  = series.shift(3)
lag_13 = series.shift(12)
lag_52 = series.shift(51)
```

Do **not** blindly apply the conventional target-row `shift(1)` definition after joining the future target, because that can leak intermediate future demand into horizons greater than one.

Document this clearly in `docs/task2a_feature_spec.md`.

---

# 10. Missing feature policy

Early historical origins will not have enough history for long lags/windows.

Expected examples:

```text
first origin:
lag_1 may exist
lag_52 cannot exist

week with 6 prior/current observations:
roll_mean_4 may exist
roll_mean_8 does not
```

Phase 13 policy:

```text
DO NOT backfill from future demand
DO NOT forward-fill a lag from a different week
DO NOT use target demand as a replacement
DO NOT use full-history medians here
```

Keep unavailable history features as missing values.

The later model/preprocessing phase decides how to handle model-compatible missing values.

Feature coverage must be reported privately.

Recommended additional metadata:

```text
history_weeks_available
has_lag_13
has_lag_52
has_roll_13
```

These may be enabled only if included in the Phase 13 registry and tested.

They are optional engineering helpers, not master-inventory tasks.

---

# 11. Rolling-window semantics

Rolling means are trailing, origin-known windows ending at the origin week.

At origin `t`:

```text
roll_mean_4  = mean(y[t-3:t])
roll_mean_8  = mean(y[t-7:t])
roll_mean_13 = mean(y[t-12:t])
```

Use full windows by default:

```text
min_periods = window size
```

This avoids silently changing the meaning of a 13-week feature for early history.

Do not use centered windows.

Do not use future rows.

Do not use a rolling API that includes target-week values after the target join.

---

# 12. Trend feature semantics

DT-212 does not prescribe a single formula in the master inventory.

Use a small, transparent, deterministic set rather than a large feature explosion.

Recommended WayLoom trend features:

```text
total_trend_short_long = total_roll_mean_4 - total_roll_mean_13
chilled_trend_short_long = chilled_roll_mean_4 - chilled_roll_mean_13

total_trend_ratio_4_13 = total_roll_mean_4 / total_roll_mean_13
chilled_trend_ratio_4_13 = chilled_roll_mean_4 / chilled_roll_mean_13
```

For ratios:

```text
if denominator <= 0:
    return missing
```

Optional slope features:

```text
total_slope_8
chilled_slope_8
```

computed only from the latest 8 known observations ending at origin.

If slope features are implemented:

```text
x = [0,1,...,7]
y = known weekly demand values
fit deterministic ordinary least squares slope
```

Do not fit a slope with future values.

Do not require optional slope features if simpler trend differences are already sufficient.

---

# 13. Target-week calendar feature semantics

The target week `t+h` is in the future relative to the forecast origin, but its calendar attributes are supplied and known.

Calendar features therefore belong to the **target week**, not the origin week.

Build weekly calendar context by:

```text
calendar.csv
GROUP BY iso_year + iso_week
```

Recommended reusable target-week features:

```text
target_operating_days
target_payday_days
target_has_payday
target_holiday_days
target_has_holiday
target_festival_days
target_has_festival
target_festival_names
target_max_festival_ramp
target_mean_festival_ramp
target_monsoon_days
target_monsoon_day_fraction
target_has_monsoon_day
```

Use official calendar values only.

Do not infer future calendar context from historical averages.

---

# 14. DT-204 — Create lag-1 feature

**Mark:** [E]  
**Priority:** P1

## Objective

Create the most recent known demand feature at the forecast origin.

For a series `(depot, brand)` at origin `t`:

```text
total_lag_1 = total_volume_m3[t]
chilled_lag_1 = chilled_volume_m3[t]
```

## Inputs

```text
canonical Phase 11 weekly panel
```

## Output columns

```text
total_lag_1
chilled_lag_1
```

## Requirements

- group by `depot + brand`;
- chronological weekly order;
- current origin value only;
- no future target-week demand;
- numeric and finite when present;
- chilled invariants retained.

## Tests

Synthetic series:

```text
week 1 = 10
week 2 = 20
week 3 = 30
```

At origin week 3:

```text
lag_1 = 30
```

Leakage mutation test:

changing week 4 or later must not change week-3 lag-1.

## STOP

If `lag_1` for an origin is taken from the target week rather than the origin week, stop.

---

# 15. DT-205 — Create lag-2 feature

**Mark:** [E]  
**Priority:** P1

At origin `t`:

```text
total_lag_2 = total_volume_m3[t-1]
chilled_lag_2 = chilled_volume_m3[t-1]
```

Required:

- exact one-week-back history relative to origin;
- missing if insufficient history;
- no future fill;
- deterministic.

Synthetic expected example:

```text
history: 10, 20, 30
origin week 3
lag_2 = 20
```

---

# 16. DT-206 — Create lag-4 feature

**Mark:** [E]  
**Priority:** P1

At origin `t`:

```text
lag_4 = y[t-3]
```

This is the fourth most recent weekly observation including origin as lag-1.

Requirements:

- weekly continuity validated first;
- full series-specific shift;
- missing when fewer than four observations exist.

Synthetic test with at least five weeks must prove exact alignment.

---

# 17. DT-207 — Create lag-13 feature

**Mark:** [E]  
**Priority:** P2

At origin `t`:

```text
lag_13 = y[t-12]
```

Purpose:

```text
approximately one quarter of weekly history
```

Requirements:

- no special imputation for early history;
- coverage rate reported;
- preserve missing values where unavailable;
- generate for total and chilled demand.

Do not disable automatically because coverage is imperfect.

Phase 12 may inform whether Phase 16 later finds it useful.

---

# 18. DT-208 — Create lag-52 feature

**Mark:** [E]  
**Priority:** P1

At origin `t`:

```text
lag_52 = y[t-51]
```

## Important ISO-week note

This implementation defines lag-52 as **52 sequential weekly observations including origin as lag-1**, not "same ISO week number in previous calendar year".

This avoids ambiguous behavior around ISO week 53.

Same-week-last-year baselines are handled separately in Phase 15.

## Requirements

- complete weekly panel required;
- do not join by week number alone;
- early rows remain missing;
- report coverage;
- no future fallback.

## Tests

Include:

```text
52+ continuous weeks
ISO week 53 sequence
calendar-year boundary
```

Prove exact weekly offset.

---

# 19. DT-209 — Create rolling 4-week mean

**Mark:** [E]  
**Priority:** P1

At origin `t`:

```text
total_roll_mean_4 = mean(total[t-3:t])
chilled_roll_mean_4 = mean(chilled[t-3:t])
```

Requirements:

- trailing window;
- includes origin week;
- full 4 observations required by default;
- no centered window;
- no future values.

Tests:

```text
values = 10,20,30,40
origin = fourth week
mean = 25
```

Changing week 5+ must not change it.

---

# 20. DT-210 — Create rolling 8-week mean

**Mark:** [E]  
**Priority:** P1

At origin `t`:

```text
roll_mean_8 = mean(y[t-7:t])
```

Requirements and tests mirror DT-209 with window=8.

No partial-window substitution unless the configuration explicitly changes the policy before real results are inspected.

Default:

```text
min_periods = 8
```

---

# 21. DT-211 — Create rolling 13-week mean

**Mark:** [E]  
**Priority:** P2

At origin `t`:

```text
roll_mean_13 = mean(y[t-12:t])
```

Generate for total and chilled demand.

Report feature coverage.

Do not infer missing long-window features from future data.

---

# 22. DT-212 — Create trend features

**Mark:** [E]  
**Priority:** P2

## Required minimum

Create transparent origin-known trend features such as:

```text
total_trend_short_long
chilled_trend_short_long
```

where:

```text
trend_short_long = roll_mean_4 - roll_mean_13
```

Recommended optional normalized form:

```text
trend_ratio_4_13 = roll_mean_4 / roll_mean_13
```

with zero-denominator safety.

## Requirements

- only origin-known historical demand;
- finite when present;
- no future actuals;
- no global/full-history trend fit;
- deterministic formulas documented.

## Edge cases

```text
roll13 missing → trend missing
roll13 = 0 → ratio missing
flat history → difference 0
confirmed-zero history → safe 0 difference
```

Do not produce infinity.

---

# 23. DT-213 — Add future operating-day count

**Mark:** [E]  
**Priority:** P1

For each target week:

```text
target_operating_days = sum(calendar.is_operating)
```

Use official `calendar.csv`.

Do not infer operating days from weekdays/weekends.

## Requirements

- aggregate by target `iso_year + iso_week`;
- validate calendar-day coverage;
- numeric nonnegative integer-like value;
- target week, not origin week.

## Edge cases

A week with zero operating days is valid calendar context.

Do not force its demand target to zero.

---

# 24. DT-214 — Add future payday count

**Mark:** [E]  
**Priority:** P1

Target-week features:

```text
target_payday_days = sum(is_payday)
target_has_payday = int(target_payday_days > 0)
```

Use official calendar only.

Do not infer payday from day-of-month.

Tests:

- no payday;
- one payday;
- multiple marked days if synthetic fixture contains them;
- target week join alignment.

---

# 25. DT-215 — Add future holiday/festival features

**Mark:** [E]  
**Priority:** P1

For target week derive from official calendar:

```text
target_holiday_days
target_has_holiday
target_festival_days
target_has_festival
```

Optional categorical context:

```text
target_festival_names
```

If multiple festival names occur in one week:

- normalize blanks;
- sort unique names deterministically;
- join with a fixed delimiter;
- do not infer precedence.

Festival and holiday are distinct official fields.

Do not collapse them into one variable only.

---

# 26. DT-216 — Add future festival-ramp features

**Mark:** [E]  
**Priority:** P1

Official `festival_ramp` ranges from 0 to 1 and rises over the days before a festival.

Target-week features:

```text
target_max_festival_ramp
target_mean_festival_ramp
```

Optional:

```text
target_festival_ramp_days_positive
```

Requirements:

- validate source within [0,1];
- do not clip invalid official values silently;
- aggregate target week only;
- no historical-demand-derived festival proxy.

---

# 27. DT-217 — Add monsoon features

**Mark:** [E]  
**Priority:** P1

From official calendar target week:

```text
target_monsoon_days
target_monsoon_day_fraction
target_has_monsoon_day
```

Where:

```text
target_monsoon_days = sum(monsoon)

target_monsoon_day_fraction =
    target_monsoon_days / calendar_days_in_target_week
```

Requirements:

- official calendar only;
- support mixed weeks;
- fraction within [0,1];
- target-week alignment.

Do not use external weather services.

---

# 28. DT-218 — Add depot

**Mark:** [E]  
**Priority:** P1

Carry canonical depot from the series key.

Expected official depots include:

```text
Peliyagoda
Kandy
```

Requirements:

- non-null;
- stable across each series;
- treated as categorical metadata/feature;
- never target encoded in Phase 13;
- no private performance-based encoding.

Do not merge depots into a single global series.

---

# 29. DT-219 — Add brand

**Mark:** [E]  
**Priority:** P1

Carry canonical brand from series key.

Expected official brands:

```text
Fresh
Style
Tech
```

Requirements:

- non-null;
- categorical;
- no target encoding here;
- preserve chilled semantics.

For Style/Tech historical/direct-table chilled targets:

```text
chilled_target = 0 exactly
```

where the target week is an eligible historical week.

---

# 30. DT-220 — Add forecast horizon

**Mark:** [E]  
**Priority:** P1

For the direct modelling table:

```text
forecast_horizon ∈ {1,2,...,10}
```

Definition:

```text
forecast_horizon = number of whole weekly steps
from origin week to target week
```

Requirements:

- integer;
- 1 through 10 inclusive;
- no 0;
- no >10;
- target week exactly `origin + h weeks`;
- treated as numeric/ordinal model feature by default.

Tests must cover all ten horizon values.

---

# 31. DT-221 — Build direct multi-horizon modelling table

**Mark:** [E]  
**Priority:** P2

This is the main Phase 13 integration task.

## 31.1 Output grain

One row per:

```text
depot
brand
origin_week
forecast_horizon
```

with a historical target week when the target is observed/eligible.

Recommended unique key:

```text
depot
brand
origin_week_start_date
forecast_horizon
```

## 31.2 Required metadata

Include:

```text
depot
brand
origin_iso_year
origin_iso_week
origin_week_start_date

target_iso_year
target_iso_week
target_week_start_date

forecast_horizon
```

Target-week identifiers are metadata and safe known calendar context.

## 31.3 Predictor families

Include enabled Phase 13 predictors:

```text
origin-known lags
origin-known rolling means
origin-known trend features

target-week operating days
target-week payday features
target-week holiday/festival features
target-week festival-ramp features
target-week monsoon features

depot
brand
forecast_horizon
```

## 31.4 Historical target columns

Recommended training-only target names:

```text
target_total_volume_m3
target_chilled_volume_m3
```

These columns are labels, not features.

Never include them in the model feature registry as predictors.

## 31.5 Direct-row construction

For each series and origin `t`:

```python
for h in range(1, 11):
    target_week = origin_week + h weeks

    if historical target week is eligible and observed:
        emit training row
```

The predictor vector for all ten horizons from the same origin shares the same historical-demand features.

Only these should vary with horizon:

```text
forecast_horizon
target-week calendar features
target-week identifiers
historical target labels
```

## 31.6 Leakage rule

For origin `t`, all demand-derived predictors must satisfy:

```text
source_week <= t
```

The target satisfies:

```text
target_week = t + h
```

There must be no demand-derived predictor where:

```text
source_week > t
```

## 31.7 Late-history rows

Near the end of historical data, some origins will not have all ten future historical targets.

Phase 13 training-table policy:

```text
emit each horizon row only when that historical target week exists
and is eligible under the canonical panel rules
```

Do not fabricate target values.

Phase 14 later chooses backtest origins that have complete 10-week validation windows.

## 31.8 Historical target-week eligibility

Allowed target weeks:

```text
OBSERVED_DEMAND
CONFIRMED_ZERO
```

Do not train against unresolved/incomplete panel targets.

If Phase 11 reports unresolved target-week statuses:

```text
STOP
```

## 31.9 Output separation

Create a clear API distinction:

```text
X columns
metadata columns
y_total
y_chilled
```

Recommended helpers:

```python
get_task2a_feature_columns(...)
get_task2a_metadata_columns(...)
get_task2a_target_columns(...)
```

This prevents labels from leaking into later model code.

---

# 32. Feature registry

Create a tracked registry/config describing every Phase 13 feature.

Recommended fields:

```text
feature_name
feature_group
source
source_columns
formula
availability_type
prediction_time_safe
uses_future_actual_demand
requires_history_weeks
categorical
nullable
status
rationale
```

Recommended `availability_type` values:

```text
PAST_DEMAND
TARGET_WEEK_CALENDAR
STATIC_SERIES
FORECAST_HORIZON
```

For every enabled predictor:

```text
prediction_time_safe = true
uses_future_actual_demand = false
```

Target columns must not appear as enabled predictors.

---

# 33. Recommended `configs/task2a_features.yaml`

Example contract:

```yaml
version: 1

series_keys:
  - depot
  - brand

chronology:
  week_start_column: week_start_date
  require_continuous_weekly_panel: true

lags:
  semantics: origin_relative
  values:
    - 1
    - 2
    - 4
    - 13
    - 52

rolling_means:
  windows:
    - 4
    - 8
    - 13
  include_origin_week: true
  require_full_window: true

trend:
  short_window: 4
  long_window: 13
  include_difference: true
  include_ratio: true
  include_slope_8: false

calendar_features:
  operating_days: true
  payday_days: true
  holiday_features: true
  festival_features: true
  festival_ramp_features: true
  monsoon_features: true

multihorizon:
  min_horizon: 1
  max_horizon: 10
  strategy: direct_global_table
  require_target_week_calendar: true

missing_history:
  policy: keep_missing
  forbid_future_backfill: true
  forbid_full_history_imputation: true

private_output_dir: reports/private/phase13_task2a_features
```

Do not auto-edit this config after seeing Phase 14/15 performance unless that later phase explicitly defines a new tracked experiment.

---

# 34. Recommended implementation architecture

## `src/task2a/features.py`

Recommended functions:

```python
validate_weekly_panel_for_features(...)
add_origin_lag_features(...)
add_origin_rolling_features(...)
add_origin_trend_features(...)
build_task2a_origin_features(...)
validate_origin_features(...)
```

## `src/task2a/calendar_features.py`

Recommended functions:

```python
validate_calendar_for_forecasting(...)
build_weekly_calendar_context(...)
validate_weekly_calendar_context(...)
```

Reuse a Phase 12 implementation if it already exists and is canonical.

## `src/task2a/multihorizon.py`

Recommended functions:

```python
add_target_week_keys(...)
join_target_week_calendar_features(...)
build_direct_multihorizon_table(...)
validate_multihorizon_table(...)
audit_future_demand_leakage(...)
```

## `scripts/build_task2a_features.py`

Responsibilities:

```text
load canonical weekly panel
load official calendar
validate both
build origin features
build direct multi-horizon training table
run leakage audit
write private outputs
write sanitized console summary
```

---

# 35. Leakage audit

Phase 13 requires an explicit automated leakage audit.

For every feature, validate source lineage.

## 35.1 Demand-derived feature rule

For a direct table row:

```text
max_source_demand_week <= origin_week
```

If a demand feature source week is later than origin:

```text
FAIL
```

## 35.2 Calendar feature rule

Calendar features may use:

```text
target week t+h
```

because the calendar is supplied and known.

They must not use:

```text
target week's actual demand
```

## 35.3 Target separation

Assert:

```text
target_total_volume_m3 not in feature columns
target_chilled_volume_m3 not in feature columns
```

## 35.4 Mutation test

Synthetic test:

1. build feature row for origin `t`;
2. record predictor vector;
3. change demand values for all weeks `> t`;
4. rebuild features;
5. assert predictor vector for origin `t` is unchanged;
6. target labels are allowed to change where the changed week is the target.

This is a critical Phase 13 test.

## 35.5 Horizon-specific mutation test

For the same origin `t`:

```text
h=1
h=5
h=10
```

Changing actual demand at `t+1` must **not** change historical-demand predictors for h=5 or h=10.

If it does:

```text
STOP
```

---

# 36. Train/future feature symmetry

Although Phase 17 performs final inference, Phase 13 must design features so future construction is possible without future actual demand.

Every enabled predictor must be reproducible at forecast time from:

```text
historical weekly panel through forecast origin
+ official future calendar
+ depot
+ brand
+ requested forecast horizon
```

A feature that cannot be reproduced for the real Task 2A future rows without knowing future demand must be:

```text
DISABLED
```

Do not rely on a special hidden training-only feature.

---

# 37. Inputs and outputs summary

## Inputs

Required local/private:

```text
data/interim/task2a_weekly_panel.csv
calendar.csv via dataset manifest
```

Tracked configuration:

```text
configs/task2a_history.yaml
configs/task2a_eda.yaml
configs/task2a_features.yaml
```

Optional private Phase 12 advisory report:

```text
reports/private/phase12_task2a_eda/**
```

Codex/agent must not inspect the private report contents unless the data-use workflow is independently approved.

## Outputs

Private:

```text
data/interim/task2a_origin_features.csv
data/interim/task2a_multihorizon_train.csv
reports/private/phase13_task2a_features/**
```

Tracked:

```text
feature code
feature config
feature documentation
synthetic tests
```

---

# 38. Required synthetic tests

Create comprehensive synthetic coverage.

## 38.1 Weekly panel integrity

- duplicate series/week rejected;
- unsorted input sorted deterministically or rejected according to API contract;
- unresolved gap rejected;
- non-weekly jump detected;
- target numeric/finite/nonnegative validation;
- Style chilled exact zero;
- Tech chilled exact zero;
- Fresh chilled <= total.

## 38.2 Lag tests

For total and chilled:

- lag-1 exact;
- lag-2 exact;
- lag-4 exact;
- lag-13 exact;
- lag-52 exact;
- insufficient-history missing;
- series isolation;
- depot isolation;
- brand isolation;
- year boundary;
- ISO week 53 continuity.

## 38.3 Rolling tests

- rolling-4 exact mean;
- rolling-8 exact mean;
- rolling-13 exact mean;
- full-window minimum periods;
- no centered/future rows;
- confirmed-zero weeks included;
- separate series do not bleed together.

## 38.4 Trend tests

- increasing history → positive difference;
- decreasing history → negative difference;
- flat history → zero difference;
- zero long-window denominator → ratio missing;
- no infinity;
- optional slope exact if enabled.

## 38.5 Calendar tests

- operating-day count;
- payday count;
- has-payday;
- holiday-day count;
- festival-day count;
- deterministic multiple festival names;
- festival ramp max;
- festival ramp mean;
- ramp bounds rejection;
- monsoon days;
- monsoon fraction;
- mixed monsoon week;
- target week, not origin week;
- missing target calendar week fails;
- duplicate calendar date fails.

## 38.6 Horizon tests

- horizon 1;
- horizon 10;
- all values 1..10;
- horizon 0 rejected;
- horizon 11 rejected;
- exact target-week offset;
- year boundary target;
- ISO week 53 target.

## 38.7 Direct multi-horizon tests

- correct row key uniqueness;
- correct target total;
- correct target chilled;
- Style/Tech chilled target exact zero;
- incomplete end-of-history horizons omitted rather than fabricated;
- calendar features change by target week;
- historical demand features remain identical across horizons for same origin;
- metadata and feature/target separation;
- deterministic ordering.

## 38.8 Leakage tests

- changing future demand does not change origin features;
- changing target demand does not change predictors;
- h=10 does not use h=1 actual demand;
- rolling windows never cross origin;
- trend windows never cross origin;
- labels absent from feature columns;
- feature registry contains no future-actual-demand feature.

## 38.9 Privacy/output tests

- console summary has no private weekly values;
- no delivery IDs;
- private paths remain ignored;
- tracked docs do not embed real historical figures.

---

# 39. Edge cases

## 39.1 Short history

Expected behavior:

```text
long lags/rolling features = missing
```

Do not invent values.

## 39.2 Confirmed zero week

A confirmed zero is real history.

It must participate in:

```text
lags
rolling means
trend calculations
```

Do not turn confirmed zero into missing.

## 39.3 Unresolved gap

An unresolved missing week is not zero.

If one reaches Phase 13:

```text
STOP and return to Phase 11
```

## 39.4 Week 53

Use continuous week dates/sequential weeks.

Do not assume every ISO year has exactly 52 ISO weeks.

## 39.5 Cross-year horizon

Example:

```text
origin: ISO 2026 week 52
h=2
```

Target must be resolved by actual weekly date arithmetic/calendar mapping, not by naive `week + 2` arithmetic.

## 39.6 Multiple festivals in one week

Keep deterministic aggregate representation.

Do not select one arbitrarily.

## 39.7 Zero long rolling mean

Trend ratio denominator zero:

```text
missing
```

not infinity.

## 39.8 Style/Tech chilled history

Keep exact zeros.

Do not let generic missing-value logic convert them to nonzero values.

## 39.9 Future calendar coverage

Every historical target week used in the direct table must have official calendar coverage.

If not:

```text
STOP
```

## 39.10 Duplicate series/week

Never aggregate duplicates inside Phase 13 to hide the problem.

Return to the Phase 11 source/history contract.

---

# 40. Phase 13 STOP conditions

`READY FOR PHASE 14` must remain **NO** if any of the following is true:

- Phase 11 is not passing;
- Phase 12 review is not passing;
- canonical weekly history is rebuilt differently;
- weekly panel key is duplicated;
- unresolved missing week remains;
- weekly chronology is discontinuous without an approved panel status;
- any lag references demand after forecast origin;
- any rolling window contains a future week;
- any trend uses demand after forecast origin;
- horizon-10 predictors use actual intermediate future demand;
- target-week actual demand leaks into predictor columns;
- target labels are included in feature columns;
- target-week calendar features are aligned to the wrong week;
- official calendar coverage is missing;
- operating days are inferred from weekday rather than `is_operating`;
- payday is inferred rather than read from official calendar;
- external festival/weather/calendar data is introduced;
- Style chilled target becomes nonzero;
- Tech chilled target becomes nonzero;
- feature ratios produce infinity;
- future demand is used to fill missing lag values;
- direct table horizon is outside 1..10;
- direct table key is not unique;
- leakage mutation tests fail;
- private competition data is exposed to the external agent;
- Task 1 frozen artifacts are modified;
- synthetic tests fail;
- local build fails;
- independent review fails.

---

# 41. Phase 13 Definition of Done

Phase 13 passes only when:

- [ ] DT-204 PASS
- [ ] DT-205 PASS
- [ ] DT-206 PASS
- [ ] DT-207 PASS
- [ ] DT-208 PASS
- [ ] DT-209 PASS
- [ ] DT-210 PASS
- [ ] DT-211 PASS
- [ ] DT-212 PASS
- [ ] DT-213 PASS
- [ ] DT-214 PASS
- [ ] DT-215 PASS
- [ ] DT-216 PASS
- [ ] DT-217 PASS
- [ ] DT-218 PASS
- [ ] DT-219 PASS
- [ ] DT-220 PASS
- [ ] DT-221 PASS
- [ ] Phase 11 weekly panel reused exactly
- [ ] weekly series chronology validated
- [ ] unresolved gaps = 0
- [ ] lag semantics documented as origin-relative
- [ ] lag-1/2/4/13/52 implemented for total demand
- [ ] lag-1/2/4/13/52 implemented for chilled demand where applicable
- [ ] rolling-4/8/13 implemented with trailing origin-known windows
- [ ] trend features are past-known only
- [ ] target-week operating-day feature uses official `is_operating`
- [ ] target-week payday feature uses official `is_payday`
- [ ] target-week holiday/festival features use official calendar
- [ ] target-week festival-ramp feature uses official calendar
- [ ] target-week monsoon features use official calendar
- [ ] depot included
- [ ] brand included
- [ ] horizon 1..10 included
- [ ] direct multi-horizon table built
- [ ] target columns separated from features
- [ ] historical demand features identical across horizons for same origin
- [ ] calendar features correctly vary by target week
- [ ] future-demand mutation test passes
- [ ] horizon-intermediate-demand leakage test passes
- [ ] feature registry complete
- [ ] no infinity in engineered features
- [ ] Style/Tech chilled semantics preserved
- [ ] synthetic tests pass
- [ ] full safe regression suite passes
- [ ] local Phase 13 build passes
- [ ] private artifacts remain ignored
- [ ] Task 1 frozen artifacts unchanged
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 13 STATUS: PASS
READY FOR PHASE 14: YES
```

---

# 42. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-13-task2a-features
```

Recommended commits:

```text
feat(task2a): add leakage-safe origin lag features
feat(task2a): add rolling and trend features
feat(task2a): add target-week calendar features
feat(task2a): add direct multi-horizon feature table
test(task2a): add forecasting feature leakage tests
docs(task2a): document Phase 13 feature contract
```

Before each commit:

```bash
git status
git diff
git diff --cached --name-only
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Before merge:

```bash
pytest -q tests/test_task2a_history.py \
          tests/test_task2a_eda.py \
          tests/test_task2a_features.py \
          tests/test_task2a_multihorizon.py

pytest -q
python -m pip check
git status
```

If repository-wide tests contain a documented private-data integration test, skip only that test and record the exclusion.

Merge only after:

```text
LOCAL PHASE 13 FEATURE BUILD: PASS
INDEPENDENT PHASE 13 REVIEW: PASS
```

---

# 43. Recommended autonomous execution sequence

```text
Codex / coding agent
        ↓
Read AGENTS + handoff + Phase 13 contract
        ↓
Implement DT-204–208
Lag features
        ↓
Run targeted tests / fix ordinary failures
        ↓
Implement DT-209–212
Rolling + trend
        ↓
Run targeted tests / leakage mutation tests
        ↓
Implement DT-213–217
Target-week official calendar context
        ↓
Run calendar alignment tests
        ↓
Implement DT-218–220
Series identity + horizon
        ↓
Implement DT-221
Direct multi-horizon table
        ↓
Run full leakage suite
        ↓
Run complete safe regression suite
        ↓
STOP
        ↓
Human runs real Phase 13 build locally
        ↓
Human returns sanitized status only
        ↓
Fresh Codex review
        ↓
PASS
        ↓
Phase 14
```

---

# 44. Local Phase 13 command

Recommended CLI contract:

```bash
python scripts/build_task2a_features.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --history-config configs/task2a_history.yaml \
  --feature-config configs/task2a_features.yaml \
  --origin-output data/interim/task2a_origin_features.csv \
  --multihorizon-output data/interim/task2a_multihorizon_train.csv \
  --report-dir reports/private/phase13_task2a_features
```

PowerShell one-line equivalent:

```powershell
python scripts/build_task2a_features.py --weekly-panel data/interim/task2a_weekly_panel.csv --raw-root data/raw --manifest configs/dataset_manifest.yaml --history-config configs/task2a_history.yaml --feature-config configs/task2a_features.yaml --origin-output data/interim/task2a_origin_features.csv --multihorizon-output data/interim/task2a_multihorizon_train.csv --report-dir reports/private/phase13_task2a_features
```

The console should print only sanitized status.

Recommended final local summary:

```text
LOCAL PHASE 13 FEATURE BUILD: PASS
WEEKLY PANEL CONTINUITY: PASS
LAG FEATURES: PASS
ROLLING FEATURES: PASS
TREND FEATURES: PASS
TARGET-WEEK CALENDAR JOIN: PASS
HORIZON RANGE 1..10: PASS
MULTIHORIZON KEY UNIQUE: PASS
FUTURE-DEMAND LEAKAGE AUDIT: PASS
TARGET COLUMNS IN X: 0
STYLE CHILLED INVARIANT: PASS
TECH CHILLED INVARIANT: PASS
NONFINITE ENGINEERED FEATURES: 0
```

Do not paste private table values into the coding-agent chat.

---

# 45. Ready-to-copy Codex / Cursor implementation prompt

> This prompt is intentionally agent-neutral. It works in Codex for VS Code and can also be pasted into Cursor.

```text
You are implementing WayLoom Datathon PHASE 13 only.

PHASE:
Task 2A Forecasting Features

TASK RANGE:
DT-204 through DT-221

EXECUTION MODE:
Controlled autonomous implementation with full SAFE engineering autonomy.

You MAY:

- create/edit/refactor Phase 13 tracked source code
- create/edit config
- create/edit documentation
- create synthetic fixtures
- run targeted pytest tests
- run the full safe regression suite
- inspect tracebacks
- diagnose ordinary implementation failures
- fix ordinary bugs automatically
- rerun failing tests
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against Phase 13 DoD

Do NOT stop for routine coding/test failures that can safely be fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition row-level data
- Phase 11/12 contract inconsistency
- unresolved weekly-history gap
- forecast-time leakage that cannot be safely removed
- genuine schema/data-quality blocker
- material cross-phase design change

DO NOT START PHASE 14.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 13 and Task 2A global rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - canonical weekly history/panel semantics
5. PHASE_12_COMPETITION_CONTRACT.md
   - EDA definitions and candidate context
6. PHASE_13_COMPETITION_CONTRACT.md
7. src/task2a/history.py
8. src/task2a/eda.py if present
9. configs/task2a_history.yaml
10. configs/task2a_eda.yaml if present
11. configs/dataset_manifest.yaml
12. existing common validation/IO helpers

Do not reread unrelated Phase 00–10 contracts unless a direct dependency requires it.

TASK 1 IS FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect or print row-level/private competition content from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for all agent-run tests.

The human will execute the real Phase 13 build locally.

==================================================
OFFICIAL TASK 2A CONTRACT
==================================================

Task 2A predicts ten future weeks of:

pred_total_volume_m3
pred_chilled_volume_m3

per supplied depot + brand + forecast week.

Phase 11 canonical history MUST remain:

history = deliveries_train + task1_test_inputs
count every unique order once
include attempted/deferred/not_run
demand week = requested order_date
week keys = official calendar.iso_year + calendar.iso_week
Fresh may have chilled demand
Style chilled = exactly 0
Tech chilled = exactly 0

Do NOT rebuild history differently.

Official calendar future context includes:

is_operating
is_payday
festival
festival_ramp
is_holiday
monsoon
iso_year
iso_week

==================================================
CORE FORECAST-TIME SEMANTICS
==================================================

Series key:

depot + brand

Forecast origin t:
latest weekly demand observation assumed known.

Forecast horizon:

h = 1..10

target week:

t + h calendar weeks

Demand-derived predictors may use ONLY demand from weeks <= origin t.

Target-week official calendar context is allowed because it is known.

CRITICAL:
For h=10, do NOT use actual demand from t+1 through t+9.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2a/features.py
src/task2a/calendar_features.py
src/task2a/multihorizon.py

scripts/build_task2a_features.py

configs/task2a_features.yaml

docs/task2a_feature_spec.md

tests/test_task2a_features.py
tests/test_task2a_multihorizon.py

If calendar feature aggregation already exists from Phase 12, reuse/refactor it rather than duplicate it.

Private outputs:

data/interim/task2a_origin_features.csv
data/interim/task2a_multihorizon_train.csv
reports/private/phase13_task2a_features/**

must remain ignored.

==================================================
WEEKLY PANEL PRECONDITION
==================================================

Before feature generation assert:

unique key:
  depot + brand + iso_year + iso_week

chronological weekly continuity

unresolved Phase 11 gaps = 0

total_volume_m3 finite and >= 0

chilled_volume_m3 finite and >= 0

Fresh chilled <= total

Style chilled == 0 exactly

Tech chilled == 0 exactly

Use week_start_date / canonical continuous weekly index.

Do NOT treat the previous row as previous week until continuity is proven.

==================================================
LAG SEMANTICS — CRITICAL
==================================================

Use ORIGIN-RELATIVE lag semantics.

At forecast origin t:

lag_1  = y[t]
lag_2  = y[t-1]
lag_4  = y[t-3]
lag_13 = y[t-12]
lag_52 = y[t-51]

This definition is deliberate.

It prevents direct horizon rows from using intermediate future actual demand.

Create lag features for total and chilled series.

Never backfill missing lags from future data.

==================================================
DT-204
==================================================

Create:

total_lag_1
chilled_lag_1

using current forecast-origin demand only.

==================================================
DT-205
==================================================

Create lag-2:

value one week before origin.

==================================================
DT-206
==================================================

Create lag-4:

fourth most recent observation including origin as lag-1.

==================================================
DT-207
==================================================

Create lag-13.

Keep missing when insufficient history.

Report coverage privately.

==================================================
DT-208
==================================================

Create lag-52 as 52 sequential weekly observations including origin as lag-1.

Do NOT implement it as same ISO-week-number previous year.

Support ISO week 53 safely.

==================================================
ROLLING FEATURES
==================================================

All rolling windows are trailing and end at the forecast origin.

Use full windows by default.

No centered windows.

No future demand.

==================================================
DT-209
==================================================

Create:

total_roll_mean_4
chilled_roll_mean_4

mean of t-3..t.

==================================================
DT-210
==================================================

Create rolling 8-week means using t-7..t.

==================================================
DT-211
==================================================

Create rolling 13-week means using t-12..t.

==================================================
DT-212 — TREND
==================================================

Implement a small transparent set.

Required minimum:

total_trend_short_long = total_roll_mean_4 - total_roll_mean_13
chilled_trend_short_long = chilled_roll_mean_4 - chilled_roll_mean_13

Recommended normalized versions:

roll4 / roll13

If denominator <= 0:
return missing.

Never create infinity.

Optional slope_8 is allowed only if deterministic and past-known.

==================================================
TARGET-WEEK OFFICIAL CALENDAR FEATURES
==================================================

Build weekly calendar context by official:

iso_year + iso_week

Calendar features belong to TARGET WEEK t+h, not origin week.

Do not use external calendar/weather data.

==================================================
DT-213
==================================================

Create:

target_operating_days = sum(is_operating)

Use official is_operating.

Do not infer from weekday.

==================================================
DT-214
==================================================

Create:

target_payday_days
target_has_payday

from official is_payday.

==================================================
DT-215
==================================================

Create:

target_holiday_days
target_has_holiday
target_festival_days
target_has_festival

Optionally create deterministic target_festival_names.

Keep holiday and festival distinct.

==================================================
DT-216
==================================================

Create:

target_max_festival_ramp
target_mean_festival_ramp

Validate source festival_ramp in [0,1].

Do not clip invalid values silently.

==================================================
DT-217
==================================================

Create:

target_monsoon_days
target_monsoon_day_fraction
target_has_monsoon_day

Use official calendar monsoon only.

==================================================
DT-218
==================================================

Add depot as canonical categorical series feature.

Do not target-encode it here.

==================================================
DT-219
==================================================

Add brand as canonical categorical series feature.

Do not target-encode it here.

Preserve Style/Tech chilled-zero semantics.

==================================================
DT-220
==================================================

Add integer:

forecast_horizon

Allowed values exactly:

1..10

No 0.
No >10.

==================================================
DT-221 — DIRECT MULTI-HORIZON TABLE
==================================================

Build one training row per:

depot
brand
origin_week_start_date
forecast_horizon

Target week:

origin + forecast_horizon weeks

Include metadata:

origin_iso_year
origin_iso_week
origin_week_start_date

target_iso_year
target_iso_week
target_week_start_date

Include predictors:

origin demand lags
origin rolling means
origin trend features

target-week official calendar features

depot
brand
forecast_horizon

Training target columns:

target_total_volume_m3
target_chilled_volume_m3

TARGETS MUST NEVER BE INCLUDED IN X.

For the same origin, historical-demand predictors must be identical across h=1..10.

Only horizon/target-week calendar/target metadata/target values may differ.

Near history end:

emit a horizon row only when that historical target week actually exists and is eligible.

Do not fabricate missing targets.

Phase 14 will later choose origins with complete 10-week backtest windows.

==================================================
FEATURE REGISTRY
==================================================

Create complete tracked feature lineage.

For each feature record:

feature_name
feature_group
source
source_columns
formula
availability_type
prediction_time_safe
uses_future_actual_demand
requires_history_weeks
categorical
nullable
status
rationale

Allowed availability types:

PAST_DEMAND
TARGET_WEEK_CALENDAR
STATIC_SERIES
FORECAST_HORIZON

Every enabled predictor must have:

prediction_time_safe = true
uses_future_actual_demand = false

==================================================
LEAKAGE AUDIT — CRITICAL
==================================================

For every direct table row:

all demand-feature source weeks <= origin week

target week = origin + horizon

No demand-derived feature may come from week > origin.

Implement mutation tests:

1. build predictors for origin t
2. alter actual demand after t
3. rebuild predictors
4. predictors for origin t must remain identical

Also test:

for origin t, h=10 predictors must NOT change if actual demand at t+1 changes.

Target labels may change where the altered week is the target.

If any predictor changes because of future demand:
STOP.

==================================================
MISSING HISTORY POLICY
==================================================

If a lag/window is unavailable:

keep missing.

Do NOT:

future-backfill
forward-fill from a different week
use target demand
use full-history mean/median

Later model preprocessing handles missing values.

==================================================
REQUIRED TESTS
==================================================

Use synthetic data only.

Test:

weekly panel key uniqueness
weekly continuity
unresolved gap rejection
confirmed-zero preservation
Style/Tech chilled zero
Fresh chilled <= total

lag1 exact
lag2 exact
lag4 exact
lag13 exact
lag52 exact
lag missingness
series isolation
ISO week 53
cross-year continuity

rolling4 exact
rolling8 exact
rolling13 exact
full-window behavior
no centered/future values

trend positive/negative/flat
zero denominator
no infinity

operating-day count
payday count
holiday/festival aggregation
multiple festival names
festival-ramp bounds/max/mean
monsoon days/fraction
calendar missing target week failure

horizon 1
horizon 10
all 1..10
0 rejected
11 rejected
cross-year target-week resolution

multihorizon key uniqueness
correct historical targets
Style/Tech target chilled exact zero
end-of-history missing target omission
same-origin historical predictors identical across horizons
target calendar changes by target week
feature/metadata/target separation

future-demand mutation invariant
horizon-10 intermediate-demand leakage test
labels absent from X
feature registry lineage

privacy-safe console output
private output ignore rules

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After each logical batch:

1. run targeted tests
2. inspect failure
3. fix ordinary bug
4. rerun failing test
5. rerun Phase 13 tests
6. continue only when clean

At the end run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py

Then:

pytest -q
python -m pip check

git status
git diff

If a documented test requires private real data, do not run it in the external agent context.
Report the local human command instead.

Verify these are not staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL REAL-DATA COMMAND
==================================================

Implement but DO NOT execute against restricted private data in the external agent context:

python scripts/build_task2a_features.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --history-config configs/task2a_history.yaml \
  --feature-config configs/task2a_features.yaml \
  --origin-output data/interim/task2a_origin_features.csv \
  --multihorizon-output data/interim/task2a_multihorizon_train.csv \
  --report-dir reports/private/phase13_task2a_features

Console output must be sanitized.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 11 canonical panel is bypassed
- unresolved weekly gap exists
- duplicate weekly key exists
- lag uses demand after origin
- rolling window crosses origin
- trend uses future demand
- horizon-10 predictors use t+1..t+9 actual demand
- labels enter feature columns
- target calendar joins wrong week
- official calendar coverage missing
- external calendar/weather data introduced
- future demand fills missing features
- Style chilled becomes nonzero
- Tech chilled becomes nonzero
- horizon outside 1..10
- multihorizon key not unique
- leakage mutation test fails
- Task 1 frozen artifacts change
- private competition data must be exposed
- safe tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-204 READY
DT-205 READY
DT-206 READY
DT-207 READY
DT-208 READY
DT-209 READY
DT-210 READY
DT-211 READY
DT-212 READY
DT-213 READY
DT-214 READY
DT-215 READY
DT-216 READY
DT-217 READY
DT-218 READY
DT-219 READY
DT-220 READY
DT-221 READY

Phase 11 panel reused
weekly chronology safe
all lag features origin-relative
all rolling features trailing/origin-known
trend past-known only
target-week calendar official
horizon range exact
multihorizon table valid
targets separated from X
future-demand mutation test passes
horizon-10 intermediate-demand test passes
feature registry complete
Style/Tech chilled-zero preserved
synthetic tests pass
full safe suite passes
pip check passes
private paths protected
Task 1 unchanged
no Phase 14 code added

==================================================
RETURN ONLY
==================================================

PHASE:
13 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-204 READY / FAIL
DT-205 READY / FAIL
DT-206 READY / FAIL
DT-207 READY / FAIL
DT-208 READY / FAIL
DT-209 READY / FAIL
DT-210 READY / FAIL
DT-211 READY / FAIL
DT-212 READY / FAIL
DT-213 READY / FAIL
DT-214 READY / FAIL
DT-215 READY / FAIL
DT-216 READY / FAIL
DT-217 READY / FAIL
DT-218 READY / FAIL
DT-219 READY / FAIL
DT-220 READY / FAIL
DT-221 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 11 PANEL REUSE:
PASS / FAIL

WEEKLY CONTINUITY:
PASS / FAIL

LAG FEATURES:
PASS / FAIL

ROLLING FEATURES:
PASS / FAIL

TREND FEATURES:
PASS / FAIL

TARGET-WEEK CALENDAR FEATURES:
PASS / FAIL

HORIZON RANGE:
PASS / FAIL

MULTIHORIZON TABLE:
PASS / FAIL

TARGETS IN FEATURE MATRIX:
MUST BE 0

FUTURE-DEMAND MUTATION TEST:
PASS / FAIL

HORIZON-10 INTERMEDIATE-DEMAND LEAKAGE:
PASS / FAIL

FEATURE REGISTRY:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 13 feature-build command.

PHASE 13 STATUS:
AWAITING LOCAL TASK2A FEATURE BUILD

READY FOR PHASE 14:
NO

Then STOP.

Do not start Phase 14.
```

---

# 46. Ready-to-copy independent review prompt

Run this in a fresh Codex/Cursor session after the human-local Phase 13 build returns PASS.

```text
Perform an INDEPENDENT REVIEW of WayLoom Datathon PHASE 13.

PHASE:
Task 2A Forecasting Features

TASK RANGE:
DT-204 through DT-221

This is REVIEW ONLY.

DO NOT:

- access data/raw/**
- access data/interim/**
- access reports/private/**
- inspect private weekly demand values
- modify production code initially
- change feature definitions based on private results
- start Phase 14

==================================================
READ
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md Phase 13 section
4. PHASE_11_COMPETITION_CONTRACT.md relevant panel rules
5. PHASE_12_COMPETITION_CONTRACT.md relevant calendar definitions
6. PHASE_13_COMPETITION_CONTRACT.md
7. src/task2a/features.py
8. src/task2a/calendar_features.py if present
9. src/task2a/multihorizon.py
10. scripts/build_task2a_features.py
11. configs/task2a_features.yaml
12. docs/task2a_feature_spec.md
13. tests/test_task2a_features.py
14. tests/test_task2a_multihorizon.py
15. .gitignore
16. .cursorignore if present

==================================================
HUMAN LOCAL RESULT
==================================================

Use only this sanitized result supplied by the human:

LOCAL PHASE 13 FEATURE BUILD: <PASS/FAIL>
WEEKLY PANEL CONTINUITY: <PASS/FAIL>
LAG FEATURES: <PASS/FAIL>
ROLLING FEATURES: <PASS/FAIL>
TREND FEATURES: <PASS/FAIL>
TARGET-WEEK CALENDAR JOIN: <PASS/FAIL>
HORIZON RANGE 1..10: <PASS/FAIL>
MULTIHORIZON KEY UNIQUE: <PASS/FAIL>
FUTURE-DEMAND LEAKAGE AUDIT: <PASS/FAIL>
TARGET COLUMNS IN X: <0/NONZERO>
STYLE CHILLED INVARIANT: <PASS/FAIL>
TECH CHILLED INVARIANT: <PASS/FAIL>
NONFINITE ENGINEERED FEATURES: <0/NONZERO>

Do not request private values.

==================================================
AUDIT EVERY TASK
==================================================

DT-204:
lag-1 is current origin-known demand, not target-week demand.

DT-205:
lag-2 is one historical week behind origin.

DT-206:
lag-4 is aligned correctly.

DT-207:
lag-13 is aligned correctly and missing when insufficient history.

DT-208:
lag-52 is sequential-week based and ISO-week-53 safe.

DT-209:
rolling-4 is trailing, ends at origin, no future rows.

DT-210:
rolling-8 is trailing, ends at origin, no future rows.

DT-211:
rolling-13 is trailing, ends at origin, no future rows.

DT-212:
trend features are derived only from origin-known windows and never produce infinity.

DT-213:
target operating days use official calendar.is_operating and target week.

DT-214:
target payday count uses official is_payday.

DT-215:
target holiday/festival features preserve official separate semantics.

DT-216:
target festival-ramp features use official values and validate [0,1].

DT-217:
target monsoon features use official calendar target-week values.

DT-218:
depot is present as canonical series/static feature.

DT-219:
brand is present and chilled-zero semantics are preserved.

DT-220:
forecast_horizon is integer 1..10 and target week mapping is exact.

DT-221:
direct multi-horizon table has one unique series+origin+horizon row, targets separated from predictors, and no future demand leakage.

==================================================
CRITICAL LEAKAGE REVIEW
==================================================

Verify from code/tests that:

1. demand-derived features have source week <= origin;
2. h=10 never uses actual t+1..t+9 demand;
3. changing future demand cannot change origin predictors;
4. changing a historical target-week demand can change the label but not predictors;
5. rolling/trend windows stop at origin;
6. target_total_volume_m3 is not in X;
7. target_chilled_volume_m3 is not in X;
8. calendar context may use target week because it is officially known;
9. no external calendar/weather source is used.

If any of these fail:

PHASE 13 REVIEW = FAIL.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py

Then, if safe:

pytest -q
python -m pip check
git status

Do not run the private real-data builder.

==================================================
GIT / PRIVACY REVIEW
==================================================

Verify no tracked/staged files under:

data/raw/**
data/interim/**
reports/private/**

Verify Task 1 frozen artifacts were not modified.

==================================================
RETURN
==================================================

Return a task table:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

PHASE 11 PANEL REUSE:
PASS / FAIL

WEEKLY CONTINUITY:
PASS / FAIL

ORIGIN-RELATIVE LAG SEMANTICS:
PASS / FAIL

ROLLING/TRend LEAKAGE SAFETY:
PASS / FAIL

TARGET-WEEK CALENDAR SAFETY:
PASS / FAIL

HORIZON MAPPING:
PASS / FAIL

MULTIHORIZON KEY INTEGRITY:
PASS / FAIL

TARGET SEPARATION:
PASS / FAIL

FUTURE-DEMAND MUTATION TEST:
PASS / FAIL

HORIZON-10 INTERMEDIATE-DEMAND TEST:
PASS / FAIL

FEATURE REGISTRY:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL BUILD:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

DT-204: PASS/FAIL
DT-205: PASS/FAIL
DT-206: PASS/FAIL
DT-207: PASS/FAIL
DT-208: PASS/FAIL
DT-209: PASS/FAIL
DT-210: PASS/FAIL
DT-211: PASS/FAIL
DT-212: PASS/FAIL
DT-213: PASS/FAIL
DT-214: PASS/FAIL
DT-215: PASS/FAIL
DT-216: PASS/FAIL
DT-217: PASS/FAIL
DT-218: PASS/FAIL
DT-219: PASS/FAIL
DT-220: PASS/FAIL
DT-221: PASS/FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 13 REVIEW:
PASS / FAIL

READY FOR PHASE 14:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 14.
```

---

# 47. Human local completion record

```markdown
# Phase 13 Completion Record

## Task status

- [ ] DT-204
- [ ] DT-205
- [ ] DT-206
- [ ] DT-207
- [ ] DT-208
- [ ] DT-209
- [ ] DT-210
- [ ] DT-211
- [ ] DT-212
- [ ] DT-213
- [ ] DT-214
- [ ] DT-215
- [ ] DT-216
- [ ] DT-217
- [ ] DT-218
- [ ] DT-219
- [ ] DT-220
- [ ] DT-221

## Agent stage

- Phase 13 code complete: YES / NO
- Synthetic tests: PASS / FAIL
- Future-demand leakage audit: PASS / FAIL
- Full safe regression suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- Local feature build: PASS / FAIL
- Weekly continuity: PASS / FAIL
- Lag features: PASS / FAIL
- Rolling features: PASS / FAIL
- Trend features: PASS / FAIL
- Target calendar join: PASS / FAIL
- Horizon 1..10: PASS / FAIL
- Direct-table key unique: PASS / FAIL
- Target columns in X: 0 / NONZERO
- Future-demand mutation test: PASS / FAIL
- Style chilled: PASS / FAIL
- Tech chilled: PASS / FAIL
- Nonfinite engineered features: 0 / NONZERO

## Safety

- Task 1 artifacts changed: NO
- Private data exposed to external agent: NO
- Future actual demand used as predictor: NO
- External calendar/weather data used: NO

## Independent review

- Phase 13 review: PASS / FAIL

## Verdict

PHASE 13 STATUS: PASS / FAIL
READY FOR PHASE 14: YES / NO
```

---

# 48. Final Phase 13 checklist

Before Phase 14:

- [ ] DT-204–DT-221 all complete.
- [ ] Phase 11 weekly panel reused.
- [ ] Weekly chronology continuous.
- [ ] Lag semantics origin-relative and documented.
- [ ] lag-1 implemented.
- [ ] lag-2 implemented.
- [ ] lag-4 implemented.
- [ ] lag-13 implemented.
- [ ] lag-52 implemented.
- [ ] rolling-4 implemented.
- [ ] rolling-8 implemented.
- [ ] rolling-13 implemented.
- [ ] trend features implemented.
- [ ] target operating days official.
- [ ] target payday count official.
- [ ] target holiday/festival official.
- [ ] target festival ramp official.
- [ ] target monsoon official.
- [ ] depot included.
- [ ] brand included.
- [ ] horizon exactly 1..10.
- [ ] direct multi-horizon table built.
- [ ] direct-table key unique.
- [ ] targets separated from X.
- [ ] future-demand mutation test passes.
- [ ] h=10 intermediate-demand leakage test passes.
- [ ] missing historical features never future-filled.
- [ ] no infinities.
- [ ] Style chilled semantics preserved.
- [ ] Tech chilled semantics preserved.
- [ ] synthetic tests pass.
- [ ] full safe suite passes.
- [ ] local build passes.
- [ ] independent review passes.
- [ ] private outputs ignored.
- [ ] Task 1 remains frozen.
- [ ] no Phase 14 code added.

Only then:

```text
PHASE 13 STATUS: PASS
READY FOR PHASE 14: YES
```

