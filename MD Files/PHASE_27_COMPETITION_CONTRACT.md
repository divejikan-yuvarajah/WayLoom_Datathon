# PHASE 27 — Optional Forecast Uncertainty

> **Filename:** `PHASE_27_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 27 — Optional Forecast Uncertainty  
> **Task range:** **DT-358 → DT-361**  
> **Task count:** **4**  
> **Phase dependency:** **Final Task 1 / Task 2A models**  
> **Default phase priority:** **P3**  
> **Master phase gate:** If implemented, uncertainty outputs are clearly unofficial and do not alter official CSV schemas.  
> **Execution mode:** Optional read-only uncertainty layer around frozen Task 1 service predictions and Task 2A demand forecasts.  
> **Critical rule:** Official Task 1 and Task 2A submission files remain point-prediction-only.

---

# 1. Phase 27 purpose

Phase 27 adds an **optional uncertainty layer** around two already-frozen WayLoom prediction systems:

```text
Task 1:
pred_service_min

Task 2A:
pred_total_volume_m3
pred_chilled_volume_m3
```

The purpose is to support planning conversations such as:

```text
How uncertain is this service-time estimate?

How wide is the historical forecast-error band at week 1 versus week 10?

How much should planners trust a point forecast when capacity is tight?
```

The official competition, however, requires only point predictions.

Therefore Phase 27 must create uncertainty as **separate diagnostic artifacts**.

It must not change:

```text
submission_task1.csv

submission_task2a.csv
```

or their schemas.

---

# 2. Finalized Phase 27 master inventory

The finalized WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-358** | [C] | P3 | Final Task 1/Task 2A models | Estimate service prediction uncertainty |
| [ ] | **DT-359** | [C] | P2 | Final Task 1/Task 2A models | Estimate forecast uncertainty |
| [ ] | **DT-360** | [C] | P2 | Final Task 1/Task 2A models | Build forecast confidence intervals |
| [ ] | **DT-361** | [O] | P0 | Final Task 1/Task 2A models | Keep unofficial uncertainty fields out of official CSV |

**Expected Phase 27 tasks:** 4  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 28:** NO

---

# 3. Official source contract

The official Challenge Booklet defines Task 1 final output as:

```text
delivery_id
pred_service_min
pred_late_prob
```

and says teams must:

```text
keep delivery_id values and row order exactly as supplied
do not add or remove rows
fill only the two prediction columns
```

The official Task 2A final output is:

```text
row_id
pred_total_volume_m3
pred_chilled_volume_m3
```

with supplied `row_id` preserved.

The booklet does **not** prescribe uncertainty columns or intervals.

Therefore:

```text
Phase 27 uncertainty is unofficial WayLoom analysis.
```

No uncertainty field may be added to either official submission CSV.

---

# 4. Official prediction targets Phase 27 may reference

## Task 1

Official:

```text
pred_service_min
```

means predicted outlet handling/service time in minutes.

Phase 27 estimates uncertainty around this service prediction only.

The Phase 27 master inventory does not ask for uncertainty around:

```text
pred_late_prob
```

so do not expand scope without an explicit later task.

## Task 2A

Official:

```text
pred_total_volume_m3
```

is total ordered volume.

```text
pred_chilled_volume_m3
```

is the chilled portion.

Only Fresh has chilled demand.

For Style and Tech:

```text
pred_chilled_volume_m3 = 0
```

Phase 27 uncertainty must preserve that structural zero rule.

---

# 5. "Confidence interval" terminology

DT-360 is named:

```text
Build forecast confidence intervals
```

in the finalized master inventory.

Technically, residual/conformal-style intervals around future demand are more appropriately called:

```text
prediction intervals

forecast uncertainty intervals

target-coverage intervals
```

rather than confidence intervals for an expected mean.

Therefore:

- keep the DT-360 task name unchanged for inventory consistency;
- use statistically accurate terminology in implementation/docs;
- do not claim a confidence/probability interpretation unsupported by the method.

---

# 6. Statistical integrity principle

A useful uncertainty interval must not be calibrated from data the model already fitted directly.

Phase 27 requires:

```text
out-of-sample residuals
```

from the frozen historical validation process.

Do not use:

```text
training residuals
```

from the final model fit.

Training residuals usually understate uncertainty and would create an overconfident interval.

---

# 7. Valid uncertainty-calibration residual sources

Allowed:

## Preferred

Saved OOS validation predictions from the frozen model-selection process.

## Acceptable fallback

Deterministic recreation of the **same frozen validation protocol**, producing predictions for rows that were not used to fit the evaluation model that predicted them.

Not allowed:

```text
final model prediction on its own training rows

Task 1 future/test labels

Task 2A future test outcomes

manually invented error bands

error percentages guessed from MAE
```

---

# 8. Recreating validation does not reopen model selection

If archived OOS predictions are unavailable, Phase 27 may reproduce the frozen evaluation procedure strictly to recover OOS residuals.

Such models are:

```text
diagnostic evaluation clones
```

not new champions.

Require identical:

- features;
- preprocessing;
- hyperparameters;
- split logic;
- seeds;
- target construction.

The results must not be used to retune final point models.

---

# 9. Frozen artifacts

Treat as immutable:

```text
configs/task1_final_models.yaml

models/task1_service/**

models/task1_late/**

outputs/submission_task1.csv

configs/task2a_final_models.yaml

Task2A final saved model/runtime artifacts

outputs/submission_task2a.csv
```

Also do not change final Task 2B outputs.

---

# 10. Frozen hash guard

Before the real Phase 27 run, calculate hashes for at least:

```text
configs/task1_final_models.yaml

Task1 final service model bundle

outputs/submission_task1.csv

configs/task2a_final_models.yaml

Task2A final model bundle(s)

outputs/submission_task2a.csv
```

After Phase 27:

require exact equality.

Any change is a blocker.

---

# 11. Recommended implementation files

Create/update:

```text
src/uncertainty/__init__.py

src/uncertainty/quantiles.py

src/uncertainty/residual_sources.py

src/uncertainty/service_intervals.py

src/uncertainty/forecast_intervals.py

src/uncertainty/coverage.py

src/uncertainty/reporting.py

scripts/build_phase27_uncertainty.py

scripts/validate_phase27_uncertainty.py

configs/phase27_uncertainty.yaml

docs/phase27_uncertainty.md

docs/phase27_uncertainty_spec.md

tests/test_uncertainty_quantiles.py

tests/test_service_uncertainty.py

tests/test_forecast_uncertainty.py

tests/test_uncertainty_coverage.py

tests/test_uncertainty_official_schema_guard.py
```

Do not create Phase 28 integration implementation.

---

# 12. Private Phase 27 outputs

Use:

```text
reports/private/phase27_uncertainty/
```

Recommended:

```text
run_manifest.json

task1_service_residual_calibration.json

task1_service_uncertainty.csv

task1_service_uncertainty_summary.json

task2a_total_residual_calibration.csv

task2a_chilled_residual_calibration.csv

task2a_forecast_uncertainty.csv

task2a_uncertainty_summary.json

coverage_diagnostics.json

fallback_diagnostics.json

official_schema_guard.json

frozen_hash_audit.json

phase27_uncertainty_report.md

figures/
```

No private uncertainty CSV should be written into `outputs/`.

---

# 13. Recommended coverage levels

Default engineering target-coverage levels:

```text
80%
90%
```

Why:

- enough distinction for planning;
- less statistically fragile than a default 95% interval when calibration samples are limited;
- useful for comparing interval width growth by horizon.

95% may be optional when sample size supports it.

Do not call 80/90 official requirements.

---

# 14. Finite-sample conformal-style quantile

Given absolute calibration residuals:

```text
s_i = |y_i - yhat_i|
```

for target coverage:

```text
c = 1 - alpha
```

use:

```text
k = ceil((n + 1) * c)
```

then clip:

```text
k ∈ [1,n]
```

and use the:

```text
k-th ordered residual
```

as interval radius.

This avoids interpolating downward between order statistics.

---

# 15. Why the contract says "conformal-style"

Classic finite-sample conformal coverage statements depend on assumptions such as exchangeability.

Task 2A is a temporal forecasting problem.

Residuals across time may be dependent or distribution-shifted.

Therefore Phase 27 must be careful.

Use:

```text
conformal-style residual interval
```

unless the exact implementation/assumptions justify stronger language.

Do not claim guaranteed future coverage merely because the quantile formula resembles split conformal prediction.

---

# 16. Calibration provenance

Every interval artifact must record:

```text
residual source

OOS validation split/folds

target

horizon/group

sample count

coverage level

quantile method

fallback if any
```

No interval should exist without provenance.

---

# 17. DT-358 — Estimate service prediction uncertainty

DT-358 applies to:

```text
Task1 pred_service_min
```

not to lateness probability.

Use OOS residuals of the **final selected service configuration** under the frozen Task 1 validation process.

Residual:

```text
r_i
=
actual_service_minutes_i
-
predicted_service_minutes_i
```

Calibration score:

```text
|r_i|
```

---

# 18. Service residual prediction semantics

The OOS validation prediction must use the same semantics as the frozen final submission:

```text
raw model prediction
→ frozen service post-processing
→ pred_service_min
```

If final inference clips negatives to zero, validation residuals should be measured against the clipped/final prediction if the uncertainty interval is intended around the submitted point prediction.

Do not calibrate around raw output and then apply it to a different final point definition without documenting the mismatch.

---

# 19. Service uncertainty interval

For frozen point prediction:

```text
p
```

and calibrated radius:

```text
q_c
```

raw symmetric interval:

```text
[p - q_c, p + q_c]
```

Apply physical service lower bound:

```text
lower = max(0, p - q_c)
upper = max(lower, p + q_c)
```

Require:

```text
lower <= p <= upper
```

---

# 20. Task 1 private service uncertainty artifact

Recommended:

```text
task1_service_uncertainty.csv
```

Columns:

```text
delivery_id

pred_service_min

service_lower_80
service_upper_80
service_width_80

service_lower_90
service_upper_90
service_width_90

calibration_method

calibration_sample_count
```

`delivery_id` remains private in this artifact.

Do not put these columns in official Task 1 output.

---

# 21. Service uncertainty summary

Recommended aggregate statistics:

```text
calibration_n

residual_mean_abs

residual_median_abs

q80

q90

mean_width_80

mean_width_90

median_width_80

median_width_90

lower_bound_clipping_rate
```

If independent/OOS coverage evaluation exists:

report it separately.

If not:

state that coverage performance was not independently evaluated.

---

# 22. Service uncertainty grouping

Required baseline:

```text
global residual calibration
```

Optional:

predeclared segment-specific intervals.

Do not automatically create per-outlet or high-cardinality groups.

Recommended minimum per optional segment:

```text
30 OOS residuals
```

When sparse:

fallback to global.

Record fallback.

---

# 23. Why global is the default

Global calibration is:

- easier to reproduce;
- less likely to overfit small groups;
- robust for an optional Phase 27 feature.

Its limitation:

```text
interval width may not adapt to heteroscedastic service-time behavior
```

Document this instead of hiding it.

---

# 24. Task 1 coverage claims

If Phase 7/9 provided multiple OOS folds or a valid untouched evaluation residual set, empirical coverage may be estimated honestly.

If only one holdout residual set is available and the same residuals calibrate the interval:

do not present its in-sample-to-calibration coverage as independent validation.

Prefer:

```text
target coverage level
calibration radius
interval width diagnostics
```

plus an honest limitation.

---

# 25. DT-359 — Estimate forecast uncertainty

DT-359 applies to Task 2A:

```text
pred_total_volume_m3

pred_chilled_volume_m3
```

Use OOS errors from the frozen Phase 14 rolling 10-week validation design.

This is critical because uncertainty generally changes with forecast horizon.

---

# 26. Required Task 2A OOS residual schema

For each rolling validation prediction retain:

```text
fold/origin

depot

brand

target

forecast_horizon

actual

prediction

residual

absolute_residual
```

Target values:

```text
total

chilled
```

Do not use future Task2A test target values because they are not available.

---

# 27. Forecast horizon

Every validation/test forecast row must map to:

```text
horizon = 1,2,...,10
```

relative to its forecast origin.

Use calendar/year-week semantics from the frozen Task 2A pipeline.

Do not assume raw CSV row index equals horizon.

---

# 28. Primary Task 2A calibration strategy

Use:

```text
target + forecast_horizon
```

as the primary calibration grain.

For example:

```text
total, h=1

total, h=2

...

total, h=10

Fresh chilled, h=1

...

Fresh chilled, h=10
```

This allows uncertainty to widen with horizon if historical validation errors support it.

---

# 29. Sparse horizon fallback

Recommended config:

```text
min_residuals_per_horizon = 20
```

If a target+horizon group is below the threshold:

fallback to:

```text
pooled target-specific OOS residuals
```

Do not silently use a tiny calibration set.

Record:

```text
requested_group

group_n

fallback_group

fallback_n
```

---

# 30. Optional brand-aware hierarchy

Advanced optional hierarchy:

```text
target + brand + horizon
→ target + horizon
→ target pooled
```

Only enable if predeclared and sample sizes are strong.

Do not select the best grouping after examining Task2A future test rows.

---

# 31. Total-volume interval

For point:

```text
p_total
```

and radius:

```text
q_total
```

create:

```text
lower_total
=
max(0, p_total - q_total)

upper_total
=
max(lower_total, p_total + q_total)
```

Require:

```text
lower_total <= p_total <= upper_total
```

---

# 32. Fresh chilled interval

For Fresh:

```text
p_chilled
```

create raw:

```text
lower_chilled_raw
=
max(0, p_chilled - q_chilled)

upper_chilled_raw
=
max(lower_chilled_raw, p_chilled + q_chilled)
```

The radius must come from valid Fresh chilled OOS residuals.

---

# 33. Style and Tech chilled uncertainty

Official Task 2A rule:

```text
Style chilled = 0

Tech chilled = 0
```

This is structural, not an uncertain fitted output.

Therefore Phase 27 should use:

```text
Style:
[0,0]

Tech:
[0,0]
```

for chilled-volume uncertainty intervals.

Do not generate a positive chilled upper bound for these brands.

---

# 34. Total/chilled physical coherence

Because chilled volume is a component of total volume:

- all bounds must be nonnegative;
- point chilled must remain <= point total.

For presentation coherence, recommended:

```text
chilled_upper_coherent
=
min(chilled_upper_raw, total_upper)
```

then:

```text
chilled_lower_coherent
=
min(chilled_lower_raw, chilled_upper_coherent)
```

---

# 35. Raw vs coherent interval distinction

Coherence clipping changes an interval after calibration.

Therefore preserve enough metadata to distinguish:

```text
raw calibrated chilled interval
```

from:

```text
coherence-adjusted presentation interval
```

Do not claim the adjusted interval inherits exactly the same empirical/conformal coverage property.

---

# 36. DT-360 — Build forecast confidence intervals

DT-360 operationalizes the Task 2A intervals.

The phase contract will keep the master task name:

```text
forecast confidence intervals
```

but artifacts/docs should prefer:

```text
forecast uncertainty intervals
```

or:

```text
prediction intervals
```

unless a true confidence interval for a mean is explicitly implemented.

---

# 37. Task 2A private uncertainty artifact

Recommended:

```text
task2a_forecast_uncertainty.csv
```

Columns:

```text
row_id

depot

brand

iso_year

iso_week

forecast_horizon

pred_total_volume_m3

total_lower_80
total_upper_80

total_lower_90
total_upper_90

pred_chilled_volume_m3

chilled_lower_80_raw
chilled_upper_80_raw

chilled_lower_80
chilled_upper_80

chilled_lower_90_raw
chilled_upper_90_raw

chilled_lower_90
chilled_upper_90

total_calibration_source
total_calibration_n

chilled_calibration_source
chilled_calibration_n
```

This is private/unofficial.

---

# 38. Interval nesting

Because the 90% target interval uses a higher residual quantile than 80%:

expect:

```text
90% width >= 80% width
```

for the same calibration source.

If not:

quantile implementation or fallback logic is inconsistent.

If different fallback groups are used across levels, handle carefully and document it.

Preferred:

same calibration group for all configured coverage levels per row.

---

# 39. Sequential rolling backtest coverage

Preferred Task 2A uncertainty evaluation:

For validation origin:

```text
t
```

calibrate using only residuals from origins:

```text
< t
```

then evaluate whether actual outcomes at origin t fall within the generated intervals.

This produces a more honest historical coverage diagnostic.

---

# 40. Why sequential coverage matters

If the same residual is used both:

```text
to set q
```

and:

```text
to test coverage
```

coverage statistics are optimistic/descriptive.

Sequential backtesting avoids this leakage across rolling folds where sufficient history exists.

---

# 41. Early-fold handling

Early folds may have too little prior residual history.

Do not invent coverage.

Record:

```text
coverage_status = unavailable_insufficient_prior_calibration
```

until enough residuals exist.

---

# 42. Task 2A coverage diagnostics

Recommended private aggregate:

```text
target

coverage_level

horizon

evaluation_n

empirical_coverage

mean_interval_width

median_interval_width

calibration_strategy
```

Optional brand level only with sufficient sample.

---

# 43. Task 1 coverage diagnostics

If an independent validation source exists:

report analogous empirical coverage.

Otherwise:

do not fabricate an independent coverage metric.

A Phase 27 report can still be useful with:

```text
calibration q values

interval widths

clipping rate

residual distribution
```

---

# 44. Distribution shift limitation

The official calendar contains factors such as:

```text
festival

payday

monsoon
```

Task 2A future periods may differ from historical validation periods.

Residual intervals based on historical performance assume historical errors remain informative.

Therefore report:

```text
future interval coverage can degrade under distribution shift
```

Do not call coverage guaranteed.

---

# 45. Forecast uncertainty is not additional demand

Intervals describe prediction uncertainty.

Do not transform:

```text
upper bound
```

into an official extra-volume requirement.

Later product/design integration may choose to use upper bounds for safety planning, but Phase 27 itself should not change Task 2A target semantics.

---

# 46. DT-361 — Keep unofficial uncertainty fields out of official CSV

This is the highest-priority Phase 27 task:

```text
P0
```

even though Phase 27 overall is optional.

If Phase 27 is implemented, official schemas must remain exactly frozen.

---

# 47. Task 1 official schema guard

Require exact columns:

```text
delivery_id

pred_service_min

pred_late_prob
```

Require exact row count and order as already frozen.

No:

```text
service_lower_80

service_upper_90

service_uncertainty
```

---

# 48. Task 2A official schema guard

Require exact columns:

```text
row_id

pred_total_volume_m3

pred_chilled_volume_m3
```

No:

```text
total_lower_90

total_upper_90

chilled_lower_90

confidence_interval
```

---

# 49. Official file hash guard

Before Phase 27:

record SHA256 of:

```text
outputs/submission_task1.csv

outputs/submission_task2a.csv
```

After Phase 27:

require exact match.

This proves Phase 27 did not mutate the official outputs.

---

# 50. Point-prediction parity

The private uncertainty artifact may repeat the official point predictions.

Require exact parity by identifier.

Task 1:

```text
delivery_id

pred_service_min
```

Task 2A:

```text
row_id

pred_total_volume_m3

pred_chilled_volume_m3
```

Any mismatch:

```text
STOP
```

---

# 51. Separation of writers

Official submission writers and uncertainty writers must be separate.

Recommended:

```text
official writer
→ outputs/submission_task*.csv

uncertainty writer
→ reports/private/phase27_uncertainty/*.csv
```

Never add a boolean flag such as:

```text
include_uncertainty=True
```

to the official competition writer if that creates risk of accidental extra columns.

Prefer physically separate output functions.

---

# 52. Recommended configuration

Create:

```text
configs/phase27_uncertainty.yaml
```

Recommended:

```yaml
version: 1

coverage_levels:
  - 0.80
  - 0.90

quantile:
  method: finite_sample_higher
  require_oos_residuals: true

task1_service:
  enabled: true
  calibration_source: frozen_oos_validation
  grouping: global
  optional_segment_grouping: null
  min_segment_residuals: 30
  lower_bound: 0.0

task2a:
  enabled: true
  calibration_source: frozen_rolling_oos
  grouping: horizon
  min_residuals_per_horizon: 20
  fallback: pooled_target

  chilled_zero_brands:
    - Style
    - Tech

  enforce_nonnegative: true
  create_coherent_chilled_view: true

coverage_evaluation:
  task2a_sequential_backtest: true
  task1_independent_only_if_available: true

official_schema_guard:
  enabled: true
  require_hash_stability: true

privacy:
  private_report_dir: reports/private/phase27_uncertainty
  include_ids_only_in_private_artifacts: true
```

---

# 53. Run manifest

Create:

```text
run_manifest.json
```

Recommended fields:

```text
phase = 27

task1_final_config_sha256

task1_submission_sha256

task2a_final_config_sha256

task2a_submission_sha256

uncertainty_config_sha256

service_residual_source

service_residual_count

task2a_residual_source

task2a_validation_origin_count

coverage_levels

quantile_method

horizon_grouping

fallback_policy

software/library versions

git_commit

timestamp
```

No row-level IDs.

---

# 54. Residual-source audit

Create:

```text
residual_source_audit
```

for each target.

Require:

```text
is_out_of_sample = true

validation_contract_id / split reference present

actual target source is historical train/validation only

prediction generated without fitting that row

no future test target source
```

If the repository cannot establish these facts:

do not calibrate intervals.

---

# 55. Task 1 service private output validation

Require:

```text
one row per official delivery_id

same order as official Task1 output if convenient

pred_service_min exact match

no duplicate delivery_id

all bounds finite

all bounds nonnegative

lower <= point <= upper

90% interval contains/equal 80% interval when same calibration group
```

---

# 56. Task 2A private output validation

Require:

```text
one row per official row_id

same row order as Task2A template/final output

point values exact match

forecast_horizon in 1..10

bounds finite

bounds nonnegative

lower <= point <= upper

Style/Tech chilled bounds exactly 0

Fresh chilled coherent upper <= total upper

calibration source nonblank
```

---

# 57. Tests — quantile engine

Create:

```text
tests/test_uncertainty_quantiles.py
```

Required cases:

```text
n=1

small n

80%

90%

rank ceiling

rank clipping

no interpolation

NaN rejection

negative score rejection

coverage <=0 rejected

coverage >=1 rejected

stable deterministic output
```

---

# 58. Tests — service uncertainty

Create:

```text
tests/test_service_uncertainty.py
```

Cover:

```text
valid OOS residuals

in-sample residual rejection

point inside interval

lower clipped to 0

zero residual

90 width >= 80 width

point prediction exact parity

global calibration

segment fallback if enabled

insufficient calibration failure
```

---

# 59. Tests — forecast uncertainty

Create:

```text
tests/test_forecast_uncertainty.py
```

Cover:

```text
horizon mapping 1..10

horizon-specific q

sparse horizon pooled fallback

missing fallback failure

total interval invariants

Fresh chilled intervals

Style chilled [0,0]

Tech chilled [0,0]

raw vs coherent chilled bounds

coherent chilled upper <= total upper

point prediction parity

row_id coverage

row order
```

---

# 60. Tests — coverage

Create:

```text
tests/test_uncertainty_coverage.py
```

Cover:

```text
coverage calculation

mean/median width

horizon grouping

sequential rolling evaluation

future residual leakage rejection

insufficient-prior-fold status

calibration coverage tagged as descriptive

independent coverage tagged correctly

no false confidence guarantee
```

---

# 61. Tests — official schema guard

Create:

```text
tests/test_uncertainty_official_schema_guard.py
```

Cover:

```text
Task1 exact schema

Task2A exact schema

attempted extra Task1 interval column rejected

attempted extra Task2A interval column rejected

pre/post SHA256 stable

official file writer not used for uncertainty artifacts

private writer cannot target outputs/submission_task1.csv

private writer cannot target outputs/submission_task2a.csv
```

---

# 62. End-to-end synthetic test

Create synthetic:

Task1 OOS service residuals

Task1 official point file

Task2A rolling OOS residuals across horizons

Task2A point forecasts across Fresh/Style/Tech

Run:

```text
residual provenance validation

quantile calibration

service intervals

Task2A intervals

fallback

coherence transformation

coverage diagnostics

official schema/hash guard
```

Expected:

```text
PASS
```

No real data.

---

# 63. Edge case — archived OOS residuals absent

Do not fall back to training residuals.

Allowed:

recreate the frozen validation protocol.

If not possible:

```text
PHASE 27 OPTIONAL UNCERTAINTY: BLOCKED
NO VALID OOS RESIDUAL SOURCE
```

Since Phase 27 is optional, this is preferable to invalid uncertainty.

---

# 64. Edge case — very small sample

With small `n`, a high coverage quantile may become the maximum residual.

That is statistically expected.

Do not reduce the interval solely because it looks wide.

Report:

```text
calibration_n
```

and limitation.

---

# 65. Edge case — all residuals zero

Then:

```text
q = 0
```

and interval collapses to the point prediction.

This is valid for the synthetic case.

Do not inject arbitrary minimum width.

---

# 66. Edge case — negative service lower

Clip at:

```text
0
```

because service minutes cannot be negative.

Record clipping frequency.

---

# 67. Edge case — zero Task2A point forecast

For total:

historical residual uncertainty may still give a positive upper bound.

For Fresh chilled:

same.

For Style/Tech chilled:

structural zero stays `[0,0]`.

---

# 68. Edge case — raw chilled upper exceeds total upper

Do not permit the presentation interval to imply chilled greater than total.

Create coherent view as documented.

Retain raw calibrated bounds for audit.

---

# 69. Edge case — fallback changes interval nesting

Use one calibration group per row/target across all configured coverage levels.

This preserves:

```text
90% q >= 80% q
```

Avoid selecting a different fallback group per coverage level.

---

# 70. Edge case — new horizon outside 1..10

Official Task2A horizon is exactly 10 future weeks.

If a row maps outside:

```text
1..10
```

STOP.

Do not extrapolate uncertainty rules silently.

---

# 71. Edge case — nonstationary residuals

If residual diagnostics show error width changes strongly over time:

report it.

Do not silently pool across all history and claim stable uncertainty.

Optional more advanced temporal weighting is out of scope unless explicitly predeclared and validated.

---

# 72. Edge case — missing chilled historical residuals

If Fresh chilled OOS residuals are unavailable:

do not invent chilled intervals.

Stop Task2A chilled uncertainty generation.

Style/Tech remain structural `[0,0]`.

---

# 73. Edge case — coverage below target

Historical empirical coverage may be below the requested 80/90%.

Do not "fix" it by retuning point forecasts.

You may:

- report the result;
- revisit interval calibration methodology within Phase 27;
- use a more conservative predeclared fallback.

Do not alter official point models.

---

# 74. Honest reporting principle

A good uncertainty feature is allowed to say:

```text
"historical 90% target intervals achieved 84% coverage in sequential
backtesting"
```

if that is what happened.

Do not hide undercoverage.

Optional uncertainty that is honest is better than visually impressive but invalid intervals.

---

# 75. Documentation

Create:

```text
docs/phase27_uncertainty.md
```

Recommended sections:

```text
1. Scope and unofficial status
2. Residual calibration source
3. Task1 service intervals
4. Task2A horizon-based intervals
5. Coverage diagnostics
6. Total/chilled coherence
7. Limitations
8. Official CSV schema guard
```

No private identifiers.

---

# 76. Required limitation statement

Include language equivalent to:

> These intervals summarize uncertainty observed in the frozen historical validation process. They are unofficial planning diagnostics and do not alter the competition submission. Historical coverage may not transfer exactly to future periods, especially under temporal or demand-regime shifts.

---

# 77. Official schema statement

Include:

```text
Task1 official submission remains:
delivery_id, pred_service_min, pred_late_prob

Task2A official submission remains:
row_id, pred_total_volume_m3, pred_chilled_volume_m3
```

No uncertainty fields are submitted.

---

# 78. Privacy

Detailed interval rows are competition-data derivatives.

Keep:

```text
task1_service_uncertainty.csv

task2a_forecast_uncertainty.csv
```

private.

Competition-facing docs may show aggregate interval width/coverage summaries if authorized.

Do not publish real identifier-level intervals publicly.

---

# 79. Recommended local build command

```bash
python scripts/build_phase27_uncertainty.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --uncertainty-config configs/phase27_uncertainty.yaml \
  --task1-final-config configs/task1_final_models.yaml \
  --task1-submission outputs/submission_task1.csv \
  --task2a-final-config configs/task2a_final_models.yaml \
  --task2a-submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase27_uncertainty \
  --summary-output docs/phase27_uncertainty.md
```

Use the actual repository residual/evaluation interfaces.

Do not hard-code guessed validation artifact paths.

---

# 80. Recommended local validation command

```bash
python scripts/validate_phase27_uncertainty.py \
  --config configs/phase27_uncertainty.yaml \
  --task1-final-config configs/task1_final_models.yaml \
  --task1-submission outputs/submission_task1.csv \
  --task2a-final-config configs/task2a_final_models.yaml \
  --task2a-submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase27_uncertainty \
  --summary docs/phase27_uncertainty.md
```

---

# 81. Recommended sanitized local output

Target:

```text
WAYLOOM — PHASE 27 OPTIONAL UNCERTAINTY

TASK1 FINAL MODEL/CONFIG                  : PASS
TASK2A FINAL MODEL/CONFIG                 : PASS

TASK1 SERVICE OOS RESIDUAL SOURCE         : PASS
TASK1 SERVICE UNCERTAINTY                 : PASS

TASK2A OOS RESIDUAL SOURCE                : PASS
TASK2A HORIZON CALIBRATION                : PASS
TASK2A FALLBACK LOGIC                     : PASS

FORECAST UNCERTAINTY INTERVALS            : PASS
COVERAGE DIAGNOSTICS                      : PASS

STYLE CHILLED INTERVAL                    : [0,0]
TECH CHILLED INTERVAL                     : [0,0]

POINT PREDICTIONS UNCHANGED               : PASS

TASK1 OFFICIAL SCHEMA                     : PASS
TASK2A OFFICIAL SCHEMA                    : PASS

submission_task1.csv HASH                 : UNCHANGED
submission_task2a.csv HASH                : UNCHANGED

PHASE 27                                  : PASS
READY FOR PHASE 28                        : YES
```

---

# 82. STOP conditions

`READY FOR PHASE 28` remains **NO** if:

- frozen Task 1 service model/config unavailable;
- frozen Task 2A model/config unavailable;
- official Task1 or Task2A submission missing;
- valid OOS residual source cannot be established;
- training residuals would be used;
- Task1 test labels would be required;
- Task2A future test outcomes would be required;
- frozen validation split would be changed silently;
- point model would be retrained/tuned for uncertainty;
- Task1 service point changes;
- Task2A point changes;
- Task1 official schema changes;
- Task2A official schema changes;
- uncertainty column appears in official CSV;
- official CSV hash changes;
- residual quantile implementation is nondeterministic;
- sparse horizon uses an unapproved/unstable fallback;
- horizon mapping is not 1–10;
- Style/Tech chilled interval differs from `[0,0]`;
- Fresh chilled interval lacks valid OOS calibration;
- coherent interval is mislabeled as having unchanged coverage;
- future fold residuals leak backward;
- coverage language overclaims guarantees;
- private identifiers are exposed publicly;
- Task2B final artifacts change;
- Phase 28 work appears;
- tests fail;
- `python -m pip check` fails;
- independent review fails.

---

# 83. Definition of Done

Phase 27 is complete only when:

- [ ] DT-358 PASS
- [ ] DT-359 PASS
- [ ] DT-360 PASS
- [ ] DT-361 PASS
- [ ] Task1 final service config verified frozen
- [ ] Task2A final config verified frozen
- [ ] Task1 official submission exists
- [ ] Task2A official submission exists
- [ ] valid Task1 OOS service residual source established
- [ ] no Task1 in-sample residual calibration
- [ ] valid Task2A rolling OOS residual source established
- [ ] no future Task2A target leakage
- [ ] finite-sample quantile helper tested
- [ ] 80% service interval generated
- [ ] 90% service interval generated
- [ ] service bounds nonnegative
- [ ] service point contained in every interval
- [ ] Task1 point predictions unchanged
- [ ] Task2A horizon 1–10 mapping validated
- [ ] horizon-based total uncertainty generated
- [ ] sparse-horizon fallback deterministic
- [ ] Fresh chilled uncertainty generated
- [ ] Style chilled interval `[0,0]`
- [ ] Tech chilled interval `[0,0]`
- [ ] raw chilled bounds preserved
- [ ] coherent chilled view generated/labelled
- [ ] total/chilled points unchanged
- [ ] coverage diagnostics generated honestly
- [ ] sequential rolling coverage used where feasible
- [ ] calibration vs evaluation coverage clearly distinguished
- [ ] no unsupported guarantee language
- [ ] Task1 official schema exact
- [ ] Task2A official schema exact
- [ ] Task1 official file hash unchanged
- [ ] Task2A official file hash unchanged
- [ ] uncertainty artifacts stay private
- [ ] docs identify uncertainty as unofficial
- [ ] docs use prediction/uncertainty interval terminology accurately
- [ ] frozen model/config hashes unchanged
- [ ] Task2B final artifacts unchanged
- [ ] targeted Phase27 tests pass
- [ ] relevant Task1/Task2A regression tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] independent Phase27 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 27 STATUS: PASS
OPTIONAL UNCERTAINTY LAYER: COMPLETE
OFFICIAL TASK1/TASK2A SUBMISSIONS: UNCHANGED
READY FOR PHASE 28: YES
```

---

# 84. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-27-uncertainty
```

Recommended commits:

```text
feat(uncertainty): add finite-sample residual interval utilities
feat(task1): add service prediction uncertainty diagnostics
feat(task2a): add horizon-aware forecast uncertainty intervals
test(uncertainty): protect official submission schemas
docs(uncertainty): document empirical uncertainty and limitations
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run targeted tests.

Then:

```bash
pytest -q

python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Do not commit private identifier-level uncertainty files to a public repository.

---

# 85. Recommended model

Phase 27 is optional, but statistically subtle.

Risks include:

- invalid in-sample residual calibration;
- temporal leakage;
- unstable horizon quantiles;
- misleading "confidence" language;
- coherence transformations changing coverage meaning;
- accidental modification of official CSV schemas.

Recommended implementation:

```text
GPT-5.6 Sol
Reasoning: High
```

Recommended independent review:

```text
GPT-5.6 Sol
Reasoning: High
```

---

# 86. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 27 only.

PHASE:
Optional Forecast Uncertainty

TASK RANGE:
DT-358 through DT-361

EXECUTION MODE:
OPTIONAL, READ-ONLY UNCERTAINTY LAYER OVER FROZEN TASK 1 / TASK 2A POINT MODELS.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 28.

==================================================
MISSION
==================================================

Add a statistically honest uncertainty layer around the already-frozen:

Task 1 service-time predictions

and

Task 2A demand forecasts

without changing any official competition submission schema or point
prediction.

Required tasks:

DT-358 Estimate service prediction uncertainty

DT-359 Estimate forecast uncertainty

DT-360 Build forecast confidence intervals

DT-361 Keep unofficial uncertainty fields out of official CSV

IMPORTANT:

The official challenge requires POINT predictions only.

Uncertainty outputs are WayLoom engineering artifacts.

Do not add uncertainty columns to:

outputs/submission_task1.csv

outputs/submission_task2a.csv

Do not change point predictions.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 27
4. PHASE_07_COMPETITION_CONTRACT.md
   - Task1 validation contract
5. PHASE_09_COMPETITION_CONTRACT.md
   - Task1 model evaluation
6. PHASE_10_COMPETITION_CONTRACT.md
   - frozen Task1 inference
7. PHASE_14_COMPETITION_CONTRACT.md
   - Task2A rolling validation
8. PHASE_16_COMPETITION_CONTRACT.md
   - Task2A advanced evaluation
9. PHASE_17_COMPETITION_CONTRACT.md
   - frozen Task2A inference
10. PHASE_27_COMPETITION_CONTRACT.md

Inspect:

11. frozen Task1 final model config
12. frozen Task1 evaluation/validation artifact interfaces
13. frozen Task1 inference/post-processing code
14. frozen Task2A final model config
15. Task2A rolling-origin validation implementation
16. Task2A final inference/post-processing code
17. official submission writers/validators
18. relevant tests

Do not assume validation residual artifact names.
Discover actual repository interfaces.

==================================================
OFFICIAL SOURCE CONTRACT
==================================================

Official Task1 final CSV contains only:

delivery_id
pred_service_min
pred_late_prob

Official Task2A final CSV contains only:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

The Challenge Booklet does not require uncertainty fields.

Therefore:

uncertainty intervals are unofficial/diagnostic WayLoom artifacts.

Never add columns such as:

service_lower
service_upper
forecast_lower
forecast_upper
confidence
uncertainty

to official submission files.

==================================================
TERMINOLOGY — IMPORTANT
==================================================

Use:

prediction interval

forecast uncertainty interval

empirical coverage interval

where technically appropriate.

The master task DT-360 uses the wording:

"forecast confidence intervals"

but residual-based/conformal-style bands around future demand are generally
prediction intervals, not confidence intervals for the expected mean.

Do NOT claim:

"95% confidence that the true value lies here"

unless a method with that exact interpretation has been implemented and its
assumptions are justified.

Preferred report wording:

"90% target-coverage forecast uncertainty interval"

or:

"90% empirical/conformal-style prediction interval"

depending on method.

==================================================
PRECONDITIONS
==================================================

Require:

Task1 final service model:
FROZEN

Task1 submission:
FINAL

Task2A final total/chilled models:
FROZEN

Task2A submission:
FINAL

Task1 frozen validation contract available

Task2A rolling 10-week validation contract available

No unresolved leakage blocker

If valid OUT-OF-SAMPLE residuals cannot be obtained:

STOP.

Do NOT calibrate uncertainty from in-sample training residuals.

==================================================
FROZEN ARTIFACTS — MUST NOT CHANGE
==================================================

Do NOT modify:

configs/task1_final_models.yaml

models/task1_service/**

models/task1_late/**

outputs/submission_task1.csv

configs/task2a_final_models.yaml

Task2A final model/runtime artifacts

outputs/submission_task2a.csv

Task2B final artifacts

Hash the relevant frozen artifacts before/after the real Phase27 run.

Any change:
FAIL.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/uncertainty/__init__.py

src/uncertainty/quantiles.py

src/uncertainty/residual_sources.py

src/uncertainty/service_intervals.py

src/uncertainty/forecast_intervals.py

src/uncertainty/coverage.py

src/uncertainty/reporting.py

scripts/build_phase27_uncertainty.py

scripts/validate_phase27_uncertainty.py

configs/phase27_uncertainty.yaml

docs/phase27_uncertainty.md

docs/phase27_uncertainty_spec.md

tests/test_uncertainty_quantiles.py

tests/test_service_uncertainty.py

tests/test_forecast_uncertainty.py

tests/test_uncertainty_coverage.py

tests/test_uncertainty_official_schema_guard.py

Do NOT create Phase28 integration work.

==================================================
PRIVATE OUTPUTS
==================================================

Use:

reports/private/phase27_uncertainty/

Recommended:

run_manifest.json

task1_service_residual_calibration.json

task1_service_uncertainty.csv

task1_service_uncertainty_summary.json

task2a_total_residual_calibration.csv

task2a_chilled_residual_calibration.csv

task2a_forecast_uncertainty.csv

task2a_uncertainty_summary.json

coverage_diagnostics.json

fallback_diagnostics.json

official_schema_guard.json

frozen_hash_audit.json

phase27_uncertainty_report.md

figures/
  task1_service_interval_width.png
  task2a_interval_width_by_horizon.png
  task2a_empirical_coverage_by_horizon.png

Do not put unofficial interval columns into outputs/.

==================================================
UNCERTAINTY LEVELS
==================================================

Recommended default target coverage levels:

80%
90%

Config:

coverage_levels:
  - 0.80
  - 0.90

Why not default 95%:

calibration samples may be limited, especially horizon-specific Task2A
residuals.

95% may be enabled only if calibration sample size is adequate and the
report states the sample count.

These coverage levels are WayLoom engineering choices.

==================================================
OUT-OF-SAMPLE RESIDUAL REQUIREMENT
==================================================

Intervals must be calibrated using OUT-OF-SAMPLE prediction errors.

Acceptable sources:

1. saved validation/OOF predictions from the frozen model-selection process;

2. deterministic recreation of the FROZEN validation procedure that produces
   predictions on rows not used to fit the corresponding evaluation model.

Do NOT use:

final model predictions on its own training rows

training residuals

Task1 test outcomes

Task2A future test targets

private manual estimates

If archived OOS residuals are unavailable and recreating them would require
changing the frozen modelling contract:

STOP.

==================================================
NO FINAL MODEL RETUNING
==================================================

If validation recreation is needed, evaluation clones may reproduce the
frozen historical validation protocol.

They are diagnostic calibration models only.

They must use:

same model family

same feature logic

same hyperparameters

same split logic

same preprocessing

same random seeds

Do not use their results to retune or replace the final point models.

==================================================
FINITE-SAMPLE CONFORMAL QUANTILE
==================================================

Implement a deterministic finite-sample quantile helper for absolute
residual scores.

Given calibration scores:

s_i = |y_i - yhat_i|

and target coverage:

c = 1 - alpha

use a finite-sample conformal-style rank:

k = ceil((n + 1) * c)

clipped to [1, n]

q = kth order statistic of sorted calibration scores

Equivalent implementation may use a quantile method with the same
higher-order-statistic semantics.

Document exact implementation.

Do not use interpolation that silently reduces the finite-sample rank.

==================================================
IMPORTANT COVERAGE CLAIM
==================================================

Do NOT claim universal finite-sample coverage if the assumptions do not
support it.

Task2A is time-series forecasting and rolling residuals are not generally
exchangeable IID observations.

Therefore report:

target coverage level

calibration sample size

empirical backtest coverage where honestly measurable

limitations due to temporal dependence / distribution shift

Use "conformal-style" unless the implemented assumptions justify stronger
conformal coverage language.

==================================================
DT-358 — SERVICE PREDICTION UNCERTAINTY
==================================================

Target:

Task1 pred_service_min ONLY.

Do not add an uncertainty model for pred_late_prob in Phase27 unless a later
explicit task requires it.

Use the frozen service inference definition, including its final
post-processing.

Calibration residual:

abs(
  actual service_minutes
  -
  validation final service prediction
)

The validation prediction must use the SAME final inference semantics,
including any frozen nonnegative clipping/post-processing.

==================================================
SERVICE CALIBRATION SOURCE
==================================================

Preferred:

saved out-of-sample service validation predictions from Phase7–10 for the
selected final service configuration.

Require columns/semantics equivalent to:

actual_service_min

pred_service_min

split/fold metadata

No Task1 test labels.

If multiple frozen validation folds exist:

pool OOS residuals only if the validation contract allows it.

Record fold/source provenance.

==================================================
SERVICE INTERVAL
==================================================

For each official Task1 point prediction p and quantile q_c:

raw interval:

[p - q_c, p + q_c]

Physical lower bound:

lower = max(0, p - q_c)

upper = max(lower, p + q_c)

Require:

lower <= p <= upper

pred_service_min unchanged.

Store intervals only in private Phase27 artifact.

==================================================
SERVICE OUTPUT
==================================================

Private:

task1_service_uncertainty.csv

Recommended columns:

delivery_id

pred_service_min

service_lower_80

service_upper_80

service_width_80

service_lower_90

service_upper_90

service_width_90

calibration_method

calibration_sample_count

Do NOT publish delivery_id in docs/plots.

Do NOT write these columns into submission_task1.csv.

==================================================
SERVICE UNCERTAINTY SUMMARY
==================================================

Report aggregate:

calibration residual count

residual MAE

residual median absolute error

q80

q90

mean interval width

median interval width

min/max interval width

fraction lower-clipped at zero

If an independent coverage evaluation set exists:

report empirical coverage.

If not:

say:

independent coverage evaluation not available

rather than using calibration-set coverage as if it were independent.

==================================================
OPTIONAL SERVICE SEGMENT CALIBRATION
==================================================

Do NOT create sparse segment-specific intervals by default.

Global service residual calibration is the required robust baseline.

Optional segment calibration may be enabled only for predeclared groups such
as:

brand

or another frozen business segment

if every segment has sufficient OOS residual count.

Recommended minimum:

30 calibration residuals per segment

If not enough:

fallback to global.

Record fallback.

Do not choose segments after inspecting interval performance.

==================================================
DT-359 — FORECAST UNCERTAINTY
==================================================

Target:

Task2A total volume

and

Task2A chilled volume

Use the frozen Phase14 rolling 10-week validation design.

Forecast uncertainty must be calibrated from historical OUT-OF-SAMPLE
rolling-origin forecast errors.

Do not use future Task2A test targets.

==================================================
TASK2A RESIDUAL GRAIN
==================================================

For every validation prediction record:

target:

total
or
chilled

forecast_horizon:

1 through 10

actual

prediction

residual

absolute residual

brand

depot

fold/origin

The calibration must know forecast horizon.

Do not collapse horizon information before evaluating whether horizon-specific
uncertainty is feasible.

==================================================
TASK2A PRIMARY CALIBRATION
==================================================

Primary engineering method:

horizon-specific additive absolute-residual conformal-style intervals.

For each target and horizon h:

score =
|actual - prediction|

calibrate q(h, coverage)

This captures the common pattern that uncertainty can grow with forecast
horizon.

==================================================
TASK2A SPARSE-HORIZON FALLBACK
==================================================

Config:

min_residuals_per_horizon: 20

If a target+horizon calibration group has fewer than the minimum:

fallback to target-level pooled OOS residuals.

Record:

requested group

sample count

fallback source

Do not silently estimate an unstable horizon quantile from 2–3 points.

If even pooled target residuals are insufficient:

STOP for that target.

==================================================
OPTIONAL BRAND-AWARE CALIBRATION
==================================================

Do NOT use brand+horizon residual groups by default unless sample counts are
strong.

Optional hierarchy:

target + brand + horizon

fallback target + horizon

fallback target pooled

Only enable if predeclared in config and every fallback is deterministic.

Never tune subgroup choice on future test data.

==================================================
TASK2A TOTAL INTERVAL
==================================================

For total volume point p_total:

lower_total =
max(0, p_total - q_total)

upper_total =
max(lower_total, p_total + q_total)

Require point inside interval.

==================================================
TASK2A CHILLED INTERVAL
==================================================

Official rule:

Style and Tech chilled predictions are exactly 0.

Therefore unofficial chilled uncertainty for:

Style
Tech

must be:

lower = 0
upper = 0

Do NOT invent chilled uncertainty for brands whose official chilled demand is
structurally zero.

For Fresh:

use Fresh chilled OOS residual calibration.

Raw:

lower_chilled =
max(0, p_chilled - q_chilled)

upper_chilled =
max(lower_chilled, p_chilled + q_chilled)

==================================================
PHYSICAL COHERENCE — TOTAL VS CHILLED
==================================================

Because chilled volume is part of total volume, presentation intervals should
not imply impossible negative values.

At minimum:

all bounds >= 0

chilled point <= total point
(as already guaranteed by Phase17)

For interval coherence, generate BOTH:

raw calibrated chilled bounds

and

presentation-coherent chilled bounds

Recommended coherent upper:

min(raw_chilled_upper, total_upper)

Recommended coherent lower:

min(raw_chilled_lower, coherent_chilled_upper)

Do NOT claim the coherence-adjusted interval has the exact same marginal
coverage guarantee as the raw interval.

Store/report both or clearly label the coherent transformation.

==================================================
DT-360 — BUILD FORECAST CONFIDENCE INTERVALS
==================================================

Implement the Task2A uncertainty artifact.

Use the terminology:

forecast uncertainty intervals

prediction intervals

The master task name may remain:

forecast confidence intervals

in task tracking.

Do not mislabel them statistically in competition-facing prose.

==================================================
TASK2A PRIVATE OUTPUT
==================================================

Private:

task2a_forecast_uncertainty.csv

Recommended columns:

row_id

depot

brand

iso_year

iso_week

forecast_horizon

pred_total_volume_m3

total_lower_80

total_upper_80

total_lower_90

total_upper_90

pred_chilled_volume_m3

chilled_lower_80_raw

chilled_upper_80_raw

chilled_lower_80

chilled_upper_80

chilled_lower_90_raw

chilled_upper_90_raw

chilled_lower_90

chilled_upper_90

total_calibration_source

total_calibration_n

chilled_calibration_source

chilled_calibration_n

Do not put these fields into submission_task2a.csv.

==================================================
FORECAST HORIZON MAPPING
==================================================

Map each future Task2A row to horizon:

1..10

using the frozen forecast origin and official supplied future-week sequence.

Do not infer horizon from row order alone unless the frozen Task2A contract
explicitly guarantees it.

Preferred:

derive from canonical year/week/date sequence.

Validate every test row maps to exactly one horizon 1–10.

==================================================
FORECAST COVERAGE DIAGNOSTICS
==================================================

Where validation history supports honest evaluation, report:

coverage target

empirical coverage

average interval width

median interval width

by:

target

coverage level

horizon

Optionally brand if sample size is adequate.

Do not report calibration-set coverage as an unbiased performance estimate.

==================================================
SEQUENTIAL BACKTEST COVERAGE — PREFERRED
==================================================

If the existing rolling-origin validation contains enough folds:

evaluate interval calibration sequentially.

For validation fold t:

calibrate interval quantiles using ONLY residuals from earlier eligible folds

evaluate coverage on fold t

This is preferred for Task2A because it avoids using the same residuals for
both calibration and coverage scoring.

If insufficient earlier folds:

mark coverage evaluation unavailable for those early folds.

Do not leak future-fold residuals backward.

==================================================
TASK1 COVERAGE EVALUATION
==================================================

If Task1 validation has multiple OOS folds/splits:

use an analogous train-calibration/evaluation chronology where feasible.

If Task1 has only a single frozen holdout:

do not split/redefine it merely to make a coverage number look good unless
the Phase27 config explicitly defines a reproducible calibration/evaluation
subsplit without affecting model selection.

Preferred conservative behavior:

calibrate intervals from the valid OOS residuals

report interval quantiles/widths

avoid a strong independent coverage claim.

==================================================
DT-361 — OFFICIAL CSV SCHEMA GUARD
==================================================

This is P0 and mandatory if Phase27 is implemented.

Before Phase27:

hash:

outputs/submission_task1.csv

outputs/submission_task2a.csv

Record exact schemas.

After Phase27:

recompute hashes and schemas.

Require exact equality.

Task1 official schema must remain:

delivery_id
pred_service_min
pred_late_prob

Task2A official schema must remain:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

No extra uncertainty field is permitted.

==================================================
OFFICIAL FILE SCHEMA NEGATIVE TEST
==================================================

Add a test that deliberately attempts to append:

service_lower_90

or:

total_upper_90

to the official submission writer.

The official schema validator must reject it.

Uncertainty artifact writer and official submission writer must be separate.

==================================================
DO NOT CHANGE POINT FORECASTS
==================================================

For every private uncertainty artifact:

point prediction columns must exactly equal the frozen official submission
point predictions by identifier.

Task1:

delivery_id
pred_service_min

Task2A:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

If any point differs:

STOP.

Phase27 is not allowed to "improve" point forecasts.

==================================================
CONFIG
==================================================

Create:

configs/phase27_uncertainty.yaml

Recommended:

version: 1

coverage_levels:
  - 0.80
  - 0.90

quantile:
  method: finite_sample_higher
  require_oos_residuals: true

task1_service:
  enabled: true
  calibration_source: frozen_oos_validation
  grouping: global
  optional_segment_grouping: null
  min_segment_residuals: 30
  lower_bound: 0.0

task2a:
  enabled: true
  calibration_source: frozen_rolling_oos
  grouping: horizon
  min_residuals_per_horizon: 20
  fallback: pooled_target
  chilled_zero_brands:
    - Style
    - Tech
  enforce_nonnegative: true
  create_coherent_chilled_view: true

coverage_evaluation:
  task2a_sequential_backtest: true
  task1_independent_only_if_available: true

official_schema_guard:
  enabled: true
  require_hash_stability: true

privacy:
  private_report_dir: reports/private/phase27_uncertainty
  include_ids_only_in_private_artifacts: true

Do not add late-probability uncertainty in this phase.

==================================================
RUN MANIFEST
==================================================

Create:

run_manifest.json

Include:

phase = 27

Task1 final config SHA256

Task1 submission SHA256

Task2A final config SHA256

Task2A submission SHA256

uncertainty config SHA256

service residual provenance

service residual count

Task2A residual provenance

Task2A fold/origin count

coverage levels

quantile method

horizon grouping/fallback policy

library versions

git commit

timestamp

No private row values.

==================================================
TESTS — QUANTILE ENGINE
==================================================

Create:

tests/test_uncertainty_quantiles.py

Test:

finite sample n=1

small n

even/odd n

80% level

90% level

rank clipping

sorted order statistic

no interpolation lowering the rank

invalid coverage <=0 or >=1 rejected

NaN residual rejected

negative residual score rejected

deterministic result

==================================================
TESTS — SERVICE UNCERTAINTY
==================================================

Create:

tests/test_service_uncertainty.py

Test:

OOS residual source required

in-sample residual source rejected

interval contains point

lower >=0

upper >= point

80% interval <= 90% interval width

zero residual case

negative raw lower clipped

service point unchanged

deterministic calibration

segment fallback if enabled

insufficient global residuals rejected

==================================================
TESTS — TASK2A FORECAST UNCERTAINTY
==================================================

Create:

tests/test_forecast_uncertainty.py

Test:

horizon 1..10 mapping

horizon-specific quantile

sparse horizon fallback

pooled fallback

missing fallback rejected

total lower >=0

point inside interval

Fresh chilled interval

Style chilled [0,0]

Tech chilled [0,0]

coherent chilled upper <= total upper

raw and coherent chilled bounds distinguished

point forecasts unchanged

row_id coverage exact

no row reorder if private output preserves template order

==================================================
TESTS — COVERAGE
==================================================

Create:

tests/test_uncertainty_coverage.py

Test:

empirical coverage calculation

interval width calculation

by-horizon aggregation

sequential fold calibration uses earlier folds only

future-fold residual leakage rejected

insufficient early fold returns unavailable, not fabricated

calibration-set coverage clearly tagged if computed

no unsupported "confidence guarantee" label

==================================================
TESTS — OFFICIAL SCHEMA GUARD
==================================================

Create:

tests/test_uncertainty_official_schema_guard.py

Test:

Task1 exact official schema

Task2A exact official schema

attempted Task1 uncertainty column rejected

attempted Task2A interval column rejected

pre/post official file SHA256 unchanged

Task1 point predictions unchanged

Task2A point predictions unchanged

no outputs/submission_task1_uncertainty.csv unless explicitly private

no outputs/submission_task2a_uncertainty.csv

uncertainty writer targets reports/private only

==================================================
EDGE CASE — NO ARCHIVED RESIDUALS
==================================================

If archived OOS residuals are absent:

attempt deterministic recreation of the frozen validation protocol only if
the repository already supports it.

Do not invent a new split.

Do not use training residuals.

If valid OOS residuals still cannot be obtained:

Phase27 should return:

UNCERTAINTY CALIBRATION BLOCKED:
NO VALID OUT-OF-SAMPLE RESIDUAL SOURCE

Because Phase27 is optional, this is safer than publishing fake intervals.

==================================================
EDGE CASE — VERY SMALL CALIBRATION N
==================================================

Finite-sample quantiles can become very wide.

Do not smooth them downward merely for presentation.

Record calibration n.

If below configured minimum:

use predeclared fallback.

If no fallback:

mark unavailable / stop target interval generation.

==================================================
EDGE CASE — ZERO DEMAND / ZERO PREDICTION
==================================================

Total interval:

lower remains 0

upper may be positive if historical OOS error supports it.

Style/Tech chilled interval:

always [0,0].

Fresh chilled:

may have positive upper even when point is 0 if OOS chilled residuals support
uncertainty.

Do not force Fresh chilled interval to [0,0] merely because point is zero.

==================================================
EDGE CASE — COHERENCE CLIPPING
==================================================

If raw chilled upper > total upper:

coherent chilled upper may be clipped to total upper.

Record:

coherence_adjusted = true

Do not hide raw interval.

Do not claim raw conformal coverage automatically transfers unchanged to the
coherence-adjusted interval.

==================================================
EDGE CASE — NONSTATIONARITY
==================================================

Festival/payday/monsoon/calendar context can create distribution shift.

Intervals calibrated from historical residuals are conditional on historical
error behavior.

Include limitation:

actual future uncertainty may differ under changed demand regimes.

Do not claim guaranteed future coverage.

==================================================
EDGE CASE — TASK1 HETEROSCEDASTICITY
==================================================

Global service intervals have constant q width except for lower clipping.

If residual spread clearly varies by segment:

report this limitation.

Do not post-hoc create many sparse subgroups unless predeclared and adequately
supported.

==================================================
REPORTING
==================================================

Create:

docs/phase27_uncertainty.md

Keep it aggregate/privacy-safe.

Recommended sections:

1. Scope
2. Why uncertainty is unofficial
3. Task1 service uncertainty method
4. Task2A forecast uncertainty method
5. Coverage/interval diagnostics
6. Physical constraints
7. Limitations
8. Official schema guard

Do not include real delivery_id/row_id values.

==================================================
REPORT LANGUAGE
==================================================

Preferred:

"90% target-coverage interval"

"empirical forecast uncertainty interval"

"conformal-style residual interval"

"historical backtest coverage"

Avoid:

"the real demand has a 90% probability of being inside this interval"

unless method/assumptions justify a probabilistic interpretation.

Avoid:

"guaranteed 90% coverage"

for time-series intervals.

==================================================
FIGURES
==================================================

Optional privacy-safe figures:

Task1:
distribution of interval widths

Task2A:
interval width by horizon

Task2A:
empirical sequential coverage by horizon where available

Do not plot raw private IDs.

Do not publish real competition-derived figures publicly unless authorized.

==================================================
VALIDATION SCRIPT
==================================================

Create:

scripts/validate_phase27_uncertainty.py

Require:

valid OOS residual provenance

coverage levels valid

quantile method valid

service interval invariants

Task2A interval invariants

Style/Tech chilled [0,0]

no point-prediction changes

official Task1 schema unchanged

official Task2A schema unchanged

official file hashes unchanged

private output path only

frozen model/config hashes unchanged

no Phase28 artifacts

==================================================
LOCAL BUILD COMMAND
==================================================

Implement but do not execute private real-data uncertainty in external-agent
context.

Expected shape:

python scripts/build_phase27_uncertainty.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --uncertainty-config configs/phase27_uncertainty.yaml \
  --task1-final-config configs/task1_final_models.yaml \
  --task1-submission outputs/submission_task1.csv \
  --task2a-final-config configs/task2a_final_models.yaml \
  --task2a-submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase27_uncertainty \
  --summary-output docs/phase27_uncertainty.md

If actual repository validation residual paths must be supplied, use the
repository's discovered interfaces.

Do not invent unsupported artifact paths.

==================================================
LOCAL VALIDATION COMMAND
==================================================

Expected:

python scripts/validate_phase27_uncertainty.py \
  --config configs/phase27_uncertainty.yaml \
  --task1-final-config configs/task1_final_models.yaml \
  --task1-submission outputs/submission_task1.csv \
  --task2a-final-config configs/task2a_final_models.yaml \
  --task2a-submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase27_uncertainty \
  --summary docs/phase27_uncertainty.md

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_uncertainty_quantiles.py \
  tests/test_service_uncertainty.py \
  tests/test_forecast_uncertainty.py \
  tests/test_uncertainty_coverage.py \
  tests/test_uncertainty_official_schema_guard.py

Then relevant Task1 final inference tests.

Then relevant Task2A rolling validation/final inference tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not execute private real uncertainty generation in Codex.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Task1 frozen service model/config unavailable

Task2A frozen models/config unavailable

Task1 or Task2A official submission missing

valid OOS residuals unavailable

training residuals would be required

test labels would be required

uncertainty recreation changes validation split

point models would need retuning

service point predictions change

Task2A point predictions change

official Task1 schema changes

official Task2A schema changes

uncertainty columns appear in official CSV

Style/Tech chilled interval not [0,0]

forecast horizon mapping ambiguous

future validation residuals leak backward

quantile calibration sample insufficient and no fallback exists

coverage guarantee is overstated

coherent interval transformation is mislabeled as unchanged coverage

frozen model/config/submission hash changes

Task2B artifact changes

Phase28 work introduced

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-358 READY
DT-359 READY
DT-360 READY
DT-361 READY

service OOS residual calibration

service intervals nonnegative

service point predictions unchanged

Task2A rolling OOS residual calibration

horizon-aware forecast intervals

fallback deterministic

Fresh chilled uncertainty handled

Style/Tech chilled exactly zero interval

raw/coherent chilled interval distinction

coverage language honest

official schemas exact

official submission hashes unchanged

no uncertainty fields in official CSVs

no Phase28 implementation

==================================================
RETURN ONLY
==================================================

PHASE:
27 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-358 READY / FAIL
DT-359 READY / FAIL
DT-360 READY / FAIL
DT-361 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

TASK1 SERVICE OOS RESIDUAL SOURCE:
PASS / FAIL

TASK1 SERVICE UNCERTAINTY:
PASS / FAIL

TASK2A OOS RESIDUAL SOURCE:
PASS / FAIL

TASK2A HORIZON UNCERTAINTY:
PASS / FAIL

FORECAST INTERVALS:
PASS / FAIL

COVERAGE DIAGNOSTICS:
PASS / FAIL

STYLE/TECH CHILLED [0,0]:
PASS / FAIL

POINT PREDICTIONS UNCHANGED:
PASS / FAIL

TASK1 OFFICIAL SCHEMA UNCHANGED:
PASS / FAIL

TASK2A OFFICIAL SCHEMA UNCHANGED:
PASS / FAIL

submission_task1.csv HASH UNCHANGED:
PASS / FAIL

submission_task2a.csv HASH UNCHANGED:
PASS / FAIL

TASK2B FINAL ARTIFACTS CHANGED:
MUST BE NO

PRIVATE REAL DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local uncertainty-build command
2. exact local uncertainty-validation command

PHASE 27 STATUS:
AWAITING LOCAL UNCERTAINTY RUN

READY FOR PHASE 28:
NO

Then STOP.

Do not start Phase28.

```

---

# 87. Independent Phase 27 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 27.

PHASE:
Optional Forecast Uncertainty

TASK RANGE:
DT-358 through DT-361

Do NOT implement Phase28.
Do NOT modify code initially.
Do NOT run private real uncertainty generation.
Do NOT inspect private row-level interval files.
Do NOT modify frozen Task1/Task2A models or submissions.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase27
4. PHASE_07_COMPETITION_CONTRACT.md
5. PHASE_10_COMPETITION_CONTRACT.md
6. PHASE_14_COMPETITION_CONTRACT.md
7. PHASE_17_COMPETITION_CONTRACT.md
8. PHASE_27_COMPETITION_CONTRACT.md

Inspect:

9. src/uncertainty/quantiles.py
10. src/uncertainty/residual_sources.py
11. src/uncertainty/service_intervals.py
12. src/uncertainty/forecast_intervals.py
13. src/uncertainty/coverage.py
14. src/uncertainty/reporting.py

15. scripts/build_phase27_uncertainty.py
16. scripts/validate_phase27_uncertainty.py

17. configs/phase27_uncertainty.yaml
18. docs/phase27_uncertainty_spec.md
19. docs/phase27_uncertainty.md where safe

20. tests/test_uncertainty_quantiles.py
21. tests/test_service_uncertainty.py
22. tests/test_forecast_uncertainty.py
23. tests/test_uncertainty_coverage.py
24. tests/test_uncertainty_official_schema_guard.py

Also inspect relevant frozen Task1 and Task2A validation/inference code.

HUMAN SANITIZED LOCAL RESULT:

TASK1 SERVICE OOS RESIDUAL SOURCE: <PASS/FAIL>
TASK1 SERVICE CALIBRATION N: <number>
TASK1 SERVICE UNCERTAINTY: <PASS/FAIL>

TASK2A OOS RESIDUAL SOURCE: <PASS/FAIL>
TASK2A ROLLING FOLDS/ORIGINS: <number>
TASK2A HORIZON UNCERTAINTY: <PASS/FAIL>
TASK2A FALLBACK DIAGNOSTICS: <PASS/FAIL>

COVERAGE DIAGNOSTICS: <PASS/FAIL>

STYLE/TECH CHILLED [0,0]: <PASS/FAIL>
FRESH CHILLED INTERVALS: <PASS/FAIL>

POINT PREDICTIONS UNCHANGED: <PASS/FAIL>

TASK1 OFFICIAL SCHEMA UNCHANGED: <PASS/FAIL>
TASK2A OFFICIAL SCHEMA UNCHANGED: <PASS/FAIL>

submission_task1.csv HASH UNCHANGED: <PASS/FAIL>
submission_task2a.csv HASH UNCHANGED: <PASS/FAIL>

Do not ask for private IDs or future actual targets.

==================================================
AUDIT MASTER TASKS
==================================================

DT-358:
service prediction uncertainty uses valid OOS residuals and frozen service
point semantics.

DT-359:
Task2A forecast uncertainty uses rolling OOS errors and horizon-aware logic.

DT-360:
forecast interval construction is numerically/statistically defensible and
honestly described.

DT-361:
official Task1/Task2A CSV schemas and hashes remain unchanged.

==================================================
CRITICAL RESIDUAL AUDIT
==================================================

Reject:

in-sample training residuals

final model fitted-row residuals

Task1 test labels

Task2A future test outcomes

future validation folds leaking into earlier sequential coverage evaluation

Accept only:

saved OOS validation residuals

or deterministic recreation of frozen OOS validation protocol.

==================================================
QUANTILE AUDIT
==================================================

Verify finite-sample conformal-style rank:

k = ceil((n + 1) * coverage)

clipped to valid rank

q = kth sorted absolute residual

No interpolation that reduces q.

Coverage levels valid.

Deterministic.

==================================================
SERVICE AUDIT
==================================================

Verify:

Task1 target is service prediction uncertainty only.

Calibration residual compares actual service label with OOS final service
prediction semantics.

Interval lower >=0.

Point inside every interval.

80% interval no wider than 90% only in the expected nesting direction:
90% width >= 80% width.

Frozen service point unchanged.

No unsupported independent coverage claim if only calibration residuals exist.

==================================================
TASK2A AUDIT
==================================================

Verify:

rolling-origin OOS residuals

horizon mapping 1..10

horizon-specific quantiles where adequate

deterministic pooled fallback where sparse

no future leakage

total intervals nonnegative

Fresh chilled intervals calibrated from valid chilled residuals

Style chilled interval [0,0]

Tech chilled interval [0,0]

coherent chilled transformation distinguished from raw calibrated interval

No false unchanged-coverage claim after coherence clipping.

==================================================
TERMINOLOGY AUDIT
==================================================

The master says "forecast confidence intervals".

Verify implementation/docs do not overstate that wording.

Preferred:

forecast uncertainty interval

prediction interval

target-coverage interval

conformal-style residual interval

Reject unjustified:

95% confidence that true demand lies inside

guaranteed coverage

probability of future target being in interval

unless a valid probabilistic method/assumption supports it.

==================================================
OFFICIAL SCHEMA AUDIT
==================================================

Task1 official schema exactly:

delivery_id
pred_service_min
pred_late_prob

Task2A official schema exactly:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

No uncertainty columns.

Verify official file hashes unchanged.

Verify private uncertainty writers cannot target official output path.

==================================================
POINT-PREDICTION PARITY
==================================================

Private uncertainty artifacts may repeat the frozen point predictions.

Require exact semantic parity by identifier.

No Phase27 smoothing/recalibration/reforecasting of point predictions.

==================================================
COVERAGE AUDIT
==================================================

If empirical coverage is reported:

verify whether it is:

independent/sequential backtest coverage

or calibration-set descriptive coverage

The report must distinguish them.

For Task2A sequential coverage:

fold t intervals may use residuals only from earlier eligible folds.

==================================================
PRIVACY AUDIT
==================================================

Public docs/figures:

no delivery_id

no row_id

no raw future rows

no private residual rows

Private interval CSVs remain ignored/unstaged.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_uncertainty_quantiles.py \
  tests/test_service_uncertainty.py \
  tests/test_forecast_uncertainty.py \
  tests/test_uncertainty_coverage.py \
  tests/test_uncertainty_official_schema_guard.py

Then relevant Task1 and Task2A final/validation tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run real private uncertainty generation.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OOS RESIDUAL INTEGRITY — TASK1:
PASS / FAIL

OOS RESIDUAL INTEGRITY — TASK2A:
PASS / FAIL

FINITE-SAMPLE QUANTILE:
PASS / FAIL

SERVICE UNCERTAINTY:
PASS / FAIL

TASK2A HORIZON UNCERTAINTY:
PASS / FAIL

SPARSE-HORIZON FALLBACK:
PASS / FAIL

FORECAST INTERVAL CONSTRUCTION:
PASS / FAIL

CHILLED/TOTAL COHERENCE:
PASS / FAIL

COVERAGE CLAIM QUALITY:
PASS / FAIL

STYLE/TECH CHILLED ZERO:
PASS / FAIL

POINT PREDICTION PARITY:
PASS / FAIL

TASK1 OFFICIAL SCHEMA:
PASS / FAIL

TASK2A OFFICIAL SCHEMA:
PASS / FAIL

OFFICIAL FILE HASH STABILITY:
PASS / FAIL

PRIVACY:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
None / exact blockers

NON-BLOCKING IMPROVEMENTS:
...

DT-358: PASS/FAIL
DT-359: PASS/FAIL
DT-360: PASS/FAIL
DT-361: PASS/FAIL

PHASE 27 INDEPENDENT REVIEW:
PASS / FAIL

OPTIONAL UNCERTAINTY LAYER:
COMPLETE / INCOMPLETE

OFFICIAL TASK1/TASK2A SUBMISSIONS:
UNCHANGED / CHANGED

READY FOR PHASE 28:
YES / NO

If PASS:

PHASE 27 INDEPENDENT REVIEW: PASS
OPTIONAL UNCERTAINTY LAYER: COMPLETE
OFFICIAL TASK1/TASK2A SUBMISSIONS: UNCHANGED
BLOCKERS: None
READY FOR PHASE 28: YES

Then STOP.

Do not start Phase28.

```

---

# 88. Completion record

```markdown
# Phase 27 Completion Record

## Tasks

- [ ] DT-358
- [ ] DT-359
- [ ] DT-360
- [ ] DT-361

## Residual integrity

- [ ] Task1 OOS residuals valid
- [ ] Task2A rolling OOS residuals valid
- [ ] no training-residual calibration
- [ ] no future/test target leakage

## Task1

- [ ] service 80% interval
- [ ] service 90% interval
- [ ] nonnegative bounds
- [ ] point unchanged
- [ ] coverage claims honest

## Task2A

- [ ] horizon 1–10
- [ ] horizon calibration
- [ ] deterministic fallback
- [ ] total intervals
- [ ] Fresh chilled intervals
- [ ] Style chilled [0,0]
- [ ] Tech chilled [0,0]
- [ ] raw/coherent distinction
- [ ] point forecasts unchanged

## Official outputs

- [ ] Task1 schema unchanged
- [ ] Task2A schema unchanged
- [ ] submission_task1.csv hash unchanged
- [ ] submission_task2a.csv hash unchanged
- [ ] no uncertainty columns in outputs/

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 27 STATUS: PASS / FAIL
OPTIONAL UNCERTAINTY LAYER: COMPLETE / INCOMPLETE
OFFICIAL TASK1/TASK2A SUBMISSIONS: UNCHANGED / CHANGED
READY FOR PHASE 28: YES / NO
```

---

# 89. Final checklist

Before Phase 28:

- [ ] exact DT-358–DT-361 coverage.
- [ ] Task1 service uncertainty uses OOS residuals.
- [ ] Task2A uncertainty uses rolling OOS residuals.
- [ ] no test/future outcome leakage.
- [ ] finite-sample quantile deterministic.
- [ ] service bounds nonnegative.
- [ ] Task1 point forecast unchanged.
- [ ] Task2A horizon mapping exact 1–10.
- [ ] horizon-specific uncertainty/fallback validated.
- [ ] total intervals nonnegative.
- [ ] Fresh chilled uncertainty valid.
- [ ] Style/Tech chilled `[0,0]`.
- [ ] raw/coherent chilled intervals distinguished.
- [ ] coverage wording does not overclaim.
- [ ] official Task1 schema unchanged.
- [ ] official Task2A schema unchanged.
- [ ] official file hashes unchanged.
- [ ] uncertainty artifacts private/unofficial.
- [ ] Task2B frozen artifacts unchanged.
- [ ] safe tests pass.
- [ ] full suite passes.
- [ ] independent review passes.

Only then:

```text
PHASE 27 STATUS: PASS
OPTIONAL UNCERTAINTY LAYER: COMPLETE
OFFICIAL TASK1/TASK2A SUBMISSIONS: UNCHANGED
READY FOR PHASE 28: YES
```
