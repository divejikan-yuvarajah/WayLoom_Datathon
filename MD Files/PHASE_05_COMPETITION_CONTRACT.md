# PHASE 05 — Task 1 Exploratory Data Analysis

> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks:** DT-072 → DT-090  
> **Task count:** 19  
> **Dependency:** Phase 04 PASS  
> **Execution:** Full-phase EDA tooling + local private run + independent review  
> **Gate:** Understand Task 1 target behavior and prediction-time-safe candidate inputs without leakage, target mutation, or premature modelling.

---

## 1. Purpose

Phase 05 explores the historical Task 1 training population created by the canonical Phase 04 label builder. It is descriptive, not a modelling phase.

The phase must explain:

- the shape and tail of `service_minutes`;
- overall `late_flag` balance;
- service patterns by brand, dock type, outlet, order size and route position;
- lateness patterns by brand, district and depot;
- the relationship between planned time slack and actual lateness;
- whether approved road, traffic, monsoon, calendar and planned time-of-day context appear worth testing later;
- where sample sizes are too small for confident interpretation;
- which fields should be kept, treated cautiously, deferred, or disabled in Phase 06.

The official challenge requires predictions of `pred_service_min` and `pred_late_prob`, but it does **not** prescribe a particular EDA method or chart set. All EDA design choices in this phase are WayLoom engineering choices unless explicitly marked as official.

---

## 2. Official Task 1 constraints carried into EDA

The official labels remain:

```text
service_start = max(actual arrival, window opening)
service_minutes = leave_outlet_time - service_start
late_flag = 1 only when actual arrival > window_close_time
```

Arrival exactly at closing time is **not late**. Early waiting is not service time.

At prediction time, planned departure, planned travel duration and planned arrival are available. Actual journey and handling outcomes are historical-only.

Therefore these are **forbidden as ordinary explanatory variables**:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

These are **target-derived** and may be summarized only as targets, never proposed as direct predictors of themselves:

```text
service_start_dt
service_minutes
late_flag
```

Phase 05 must reuse the canonical Phase 04 labels; it must not reconstruct the targets with a second implementation.

---

## 3. Data-safety model

Cursor/Codex may implement EDA code, tests, config and safe documentation using synthetic data. They must not open or inspect:

```text
data/raw/**
data/interim/**
reports/private/**
```

The human operator runs the real EDA locally. Detailed figures and statistics belong under:

```text
reports/private/phase05_task1_eda/
```

Only sanitized status should be returned to an AI agent, for example:

```text
LOCAL PHASE 05 EDA: PASS
ALL REQUIRED ANALYSES GENERATED: YES
LEAKAGE GUARD: PASS
EMPTY REQUIRED SEGMENTS: 0
```

---

## 4. Task registry

| Status | Task | Priority | Work item |
|---|---|---:|---|
| [ ] | **DT-072** | P0 | Service-time distribution |
| [ ] | **DT-073** | P1 | Service time by brand |
| [ ] | **DT-074** | P1 | Service time by dock type |
| [ ] | **DT-075** | P1 | Service time by outlet |
| [ ] | **DT-076** | P1 | Service time vs order units |
| [ ] | **DT-077** | P1 | Service time vs order weight |
| [ ] | **DT-078** | P1 | Service time vs order volume |
| [ ] | **DT-079** | P0 | Overall lateness rate |
| [ ] | **DT-080** | P1 | Lateness by brand |
| [ ] | **DT-081** | P1 | Lateness by district |
| [ ] | **DT-082** | P1 | Lateness by depot |
| [ ] | **DT-083** | P1 | Targets by route position |
| [ ] | **DT-084** | P0 | Planned slack vs lateness |
| [ ] | **DT-085** | P1 | Road-condition context |
| [ ] | **DT-086** | P1 | Traffic-speed context |
| [ ] | **DT-087** | P1 | Monsoon context |
| [ ] | **DT-088** | P1 | Day-of-week context |
| [ ] | **DT-089** | P1 | Planned time-of-day / shift |
| [ ] | **DT-090** | P0 | Final EDA chart/report package |

**READY FOR PHASE 06:** NO

---

## 5. Required files

Tracked:

```text
src/task1/eda.py
scripts/run_task1_eda.py
configs/task1_eda.yaml
docs/task1_eda_method.md
tests/test_task1_eda.py
```

Private local outputs:

```text
reports/private/phase05_task1_eda/
├── phase05_eda_report.md
├── eda_summary.json
├── service_distribution.json
├── service_by_brand.json
├── service_by_dock.json
├── service_by_outlet.json
├── service_vs_units.json
├── service_vs_weight.json
├── service_vs_volume.json
├── lateness_overall.json
├── lateness_by_brand.json
├── lateness_by_district.json
├── lateness_by_depot.json
├── route_position.json
├── planned_slack.json
├── road_context.json
├── traffic_context.json
├── monsoon_context.json
├── dow_context.json
├── shift_context.json
├── feature_candidates.json
├── warnings.json
└── figures/
```

Private outputs must remain ignored by Git and excluded from AI indexing.

---

## 6. EDA principles

Every grouped analysis must include sample size `n`. For service time, prefer robust summaries in addition to the mean:

```text
n, mean, median, std, p25, p75, p90, p95, p99, min, max
```

For lateness:

```text
n, late_count, not_late_count, late_rate
```

Optional Wilson confidence intervals are allowed if tested and documented as an engineering aid, not an official requirement.

Use wording such as:

```text
associated with
shows a descriptive pattern
candidate for later validation
```

Do not use causal language.

Do not remove, clip or winsorize labels in this phase. Do not resample the late class. Do not fit final models.

---

## 7. Suggested config

Create `configs/task1_eda.yaml`:

```yaml
version: 1
service_quantiles: [0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
grouping:
  minimum_group_n_for_primary_chart: 20
  minimum_group_n_for_rate_interpretation: 30
continuous_analysis:
  quantile_bins: 10
planned_slack:
  bins_min: [-999999, -60, -30, -15, 0, 15, 30, 60, 999999]
shift_bins:
  - {name: overnight, start_hour: 0, end_hour: 6}
  - {name: morning, start_hour: 6, end_hour: 12}
  - {name: afternoon, start_hour: 12, end_hour: 18}
  - {name: evening, start_hour: 18, end_hour: 24}
privacy:
  private_output_dir: reports/private/phase05_task1_eda
```

The shift bins are a WayLoom engineering convention, not an organizer-defined category.

---

# 8. Detailed tasks

## DT-072 — Analyze service-time distribution

### Objective
Understand the regression target's center, spread, skew and upper tail.

### Inputs
`service_minutes` from the canonical Phase 04 label builder.

### Required outputs
Statistics:

```text
n, missing, mean, std, min, p25, median, p75, p90, p95, p99, max, IQR
```

Recommended figures:

- histogram;
- ECDF;
- boxplot.

### Tests
- known synthetic quantiles;
- negative/nonfinite service rejected;
- empty input fails clearly;
- no row identifiers written to aggregate output.

### Edge cases
- strongly skewed distribution;
- very long but valid services;
- repeated identical values.

### STOP
If any negative/nonfinite label appears, return to Phase 04 instead of hiding it.

### DoD
- [ ] robust statistics produced;
- [ ] aggregate charts produced;
- [ ] no label mutation.

---

## DT-073 — Analyze service time by brand

### Objective
Compare historical service patterns across `Fresh`, `Style`, and `Tech`.

### Required metrics
For each brand:

```text
n, mean, median, p75, p90, p95
```

### Recommended figure
Boxplot/violin or median-with-interval view with sample counts.

### Interpretation
Brand is known at prediction time and is a legitimate later candidate, but a group difference is descriptive rather than causal.

### Tests
Synthetic brands with known medians.

### STOP
Unexpected brand category indicates an upstream integrity problem.

### DoD
- [ ] official brand groups summarized;
- [ ] counts included;
- [ ] no causal conclusion.

---

## DT-074 — Analyze service time by dock type

### Objective
Explore whether handling time differs by receiving arrangement.

Official dock types:

```text
rear_dock
street
mall_bay
```

### Input join
Use the approved `outlet_id → outlets` relationship to obtain `dock_type` if needed.

### Metrics

```text
n, mean, median, p75, p90, p95
```

### Tests
- safe reference join;
- invalid/missing outlet reference not silently dropped.

### DoD
- [ ] dock type joined safely;
- [ ] service comparison generated;
- [ ] small groups flagged.

---

## DT-075 — Analyze service time by outlet

### Objective
Measure outlet-level variability without creating leakage-prone target encodings.

### Metrics

```text
n, mean_service, median_service, p90_service
```

### Required safeguards
- always report `n`;
- flag outlets below the configured minimum group size;
- show sample-count distribution;
- do not create full-history target encoding for later modelling here.

### Recommended private figures
- outlet sample-size distribution;
- outlet median service for sufficiently large groups;
- sample size vs median service.

### STOP
Do not recommend raw full-history outlet target means as safe model features.

### DoD
- [ ] outlet variation quantified;
- [ ] small-sample risk documented;
- [ ] no target encoding generated.

---

## DT-076 — Analyze service time vs order units

### Objective
Understand the descriptive relationship between `order_units` and service time.

### Required analysis
- valid-pair count;
- Spearman correlation;
- optional Pearson as secondary;
- quantile-binned summary;
- scatter/hexbin or sampled aggregate visualization.

Binned output:

```text
n, units_min, units_max, median_units, mean_service, median_service, p90_service
```

### Tests
- monotonic synthetic relationship;
- constant feature;
- repeated values;
- safe quantile-bin fallback when duplicate edges occur.

### DoD
- [ ] binned summary generated;
- [ ] rank relationship reported;
- [ ] no model fitted.

---

## DT-077 — Analyze service time vs order weight

Use the same continuous-variable template for `order_weight_kg`.

Also record the correlation among units/weight/volume privately as a possible multicollinearity warning for later modelling.

### DoD
- [ ] weight-service relationship summarized;
- [ ] sample size and quantile bins present;
- [ ] no final feature decision made.

---

## DT-078 — Analyze service time vs order volume

Use the same continuous-variable template for `order_volume_m3`.

### DoD
- [ ] volume-service relationship summarized;
- [ ] tail behavior considered;
- [ ] no automatic transform chosen.

---

## DT-079 — Analyze overall lateness rate

### Objective
Understand the class balance of the Task 1 probability target.

### Metrics

```text
n, late_count, not_late_count, late_rate
```

Optional Wilson interval.

### Rules
Reuse canonical `late_flag`. Do not reconstruct it. Do not resample, choose class weights, thresholds, or calibrators.

### Tests
Known synthetic class rate.

### DoD
- [ ] class balance recorded;
- [ ] no resampling/modelling.

---

## DT-080 — Analyze lateness by brand

For each official brand report:

```text
n, late_count, late_rate
```

Recommended: rate chart with sample-size labels.

### DoD
- [ ] brand late rates generated;
- [ ] small groups flagged;
- [ ] no class-weight decision made.

---

## DT-081 — Analyze lateness by district

### Metrics

```text
district, n, late_count, late_rate
```

### Caution
District can be entangled with depot, brand mix, route design, traffic and road conditions. Do not call it causal.

### DoD
- [ ] valid districts summarized;
- [ ] counts shown;
- [ ] no causal claim.

---

## DT-082 — Analyze lateness by depot

Official depots:

```text
Peliyagoda
Kandy
```

Report:

```text
n, late_count, late_rate
```

### DoD
- [ ] depot comparison generated;
- [ ] sample sizes shown;
- [ ] interaction/confounding caution documented.

---

## DT-083 — Analyze target behavior by route position

### Primary field
`seq_in_route`, where route position starts at 0.

### Required summaries
For exact sequence where sample size permits:

```text
n, median_service, late_rate
```

Also compare:

```text
is_first_stop = seq_in_route == 0
```

against later stops.

If high sequence values are sparse, group transparently, for example:

```text
0, 1, 2, 3, 4+
```

### Rule
Do not use actual completion information to construct route position.

### DoD
- [ ] route-position pattern summarized;
- [ ] sparse groups handled transparently;
- [ ] first-stop comparison available.

---

## DT-084 — Analyze planned time slack versus lateness

### Objective
Measure one of the strongest intuitive prediction-time candidates: planned margin before the outlet closes.

### Engineering definition

```text
planned_slack_min = window_close_planned_dt - planned_arrival_dt
```

Interpretation:

```text
positive → planned arrival before close
zero     → planned arrival exactly at close
negative → planned schedule already beyond close
```

### Required analysis
- slack distribution;
- late rate by configured slack bin;
- service median by slack bin as secondary;
- Spearman relationship where meaningful;
- focused view around 0 minutes.

Recommended bins:

```text
< -60
[-60,-30)
[-30,-15)
[-15,0)
[0,15)
[15,30)
[30,60)
>=60
```

### Leakage rule
Never use actual arrival to calculate planned slack.

### Midnight rule
Use approved planned datetime/window resolution logic; do not subtract raw clock strings.

### Tests
- positive slack;
- zero slack;
- negative slack;
- cross-midnight window;
- actual arrival intentionally ignored.

### STOP
Any use of actual arrival in slack calculation fails the phase.

### DoD
- [ ] planned slack is leakage-safe;
- [ ] zero boundary handled;
- [ ] slack-lateness relationship summarized.

---

## DT-085 — Analyze road-condition context

### Objective
Determine whether approved road-condition context is useful enough to carry forward.

### Source
`road_conditions.csv` through the Phase 03-approved join only.

### Requirements
- report coverage first;
- do not invent missing keys;
- do not fill missing road condition as clear;
- analyze available `disruption_index` only where the approved join succeeds.

Suggested summaries:

```text
coverage_n, coverage_rate, missing_n
```

Then, for available observations:

- disruption-index distribution;
- service summaries by sensible bins;
- late rate by bins;
- Spearman with service.

If Phase 03 disabled road context, return cleanly as:

```text
NOT_APPLICABLE / DISABLED
```

### DoD
- [ ] coverage documented;
- [ ] no missing=clear assumption;
- [ ] candidate status recorded.

---

## DT-086 — Analyze traffic-speed context

### Objective
Explore Task 1 target behavior against approved prediction-time traffic context.

The official material documents `speed_index` with `100` representing free flow and lower values slower traffic.

### Requirements
- use Phase 03-approved join dimensions;
- report coverage;
- never use `actual_travel_duration_min` as explanatory context;
- never set missing traffic to free flow automatically.

### Suggested summaries
- speed-index distribution;
- service by speed-index bin;
- late rate by speed-index bin;
- Spearman with service.

### DoD
- [ ] traffic context analyzed if enabled;
- [ ] actual travel outcomes not used;
- [ ] coverage recorded.

---

## DT-087 — Analyze monsoon context

Use the approved prediction-time monsoon indicator.

For monsoon 0/1 report:

```text
n, median_service, p90_service, late_count, late_rate
```

Do not make causal claims; monsoon may correlate with road/traffic context.

### DoD
- [ ] monsoon groups summarized;
- [ ] counts included;
- [ ] descriptive wording only.

---

## DT-088 — Analyze day-of-week context

Official calendar convention:

```text
dow = 0..6
Monday = 0
```

### Metrics by day

```text
n, median_service, p90_service, late_rate
```

Display Monday → Sunday in order, not alphabetically.

Do not infer operating status from weekday alone; if used, rely on official `is_operating`.

### DoD
- [ ] ordered DOW summary;
- [ ] official calendar convention preserved.

---

## DT-089 — Analyze planned time-of-day / shift context

### Default basis
Use `planned_arrival_time`.

Default WayLoom engineering bins:

```text
overnight  00:00–05:59
morning    06:00–11:59
afternoon  12:00–17:59
evening    18:00–23:59
```

These are not official categories and must remain configurable.

### Metrics

```text
shift, n, median_service, p90_service, late_rate
```

Optional planned-arrival hour chart if sample size is adequate.

### Leakage rule
Do not define shift from actual arrival.

### Tests
All boundary times: 00:00, 05:59, 06:00, 11:59, 12:00, 17:59, 18:00, 23:59.

### DoD
- [ ] shift definition documented as engineering-only;
- [ ] based on planned time only;
- [ ] summaries generated.

---

## DT-090 — Produce final EDA chart/report package

### Objective
Create a coherent private evidence package that informs Phase 06 without performing model selection.

### Required private outputs

```text
phase05_eda_report.md
eda_summary.json
feature_candidates.json
warnings.json
figures/
```

### Recommended figures
1. service histogram;
2. service ECDF;
3. service by brand;
4. service by dock type;
5. units vs service;
6. weight vs service;
7. volume vs service;
8. overall late rate;
9. late rate by brand;
10. late rate by district;
11. late rate by depot;
12. route position vs targets;
13. planned slack vs late rate;
14. road context if enabled;
15. traffic context if enabled;
16. monsoon vs targets;
17. DOW vs targets;
18. shift vs targets.

### Feature-candidate table
Required columns:

```text
feature
prediction_time_safe
eda_signal
sample_coverage
stability_warning
phase06_recommendation
reason
```

Allowed recommendations:

```text
KEEP_CANDIDATE
KEEP_WITH_CAUTION
DEFER
DISABLE
```

Examples:

```text
brand → prediction_time_safe=true
planned_slack_min → prediction_time_safe=true
actual_travel_duration_min → prediction_time_safe=false, recommendation=DISABLE
```

### Warnings section
Include:

- heavy target tail;
- late-class imbalance;
- small groups;
- outlet overfitting risk;
- units/weight/volume multicollinearity candidates;
- road/traffic coverage gaps;
- any constant/near-constant context;
- any pattern too unstable to act on.

### DoD
- [ ] all analyses represented;
- [ ] figures generated;
- [ ] candidate table generated;
- [ ] warnings documented;
- [ ] no modelling or causal conclusion.

---

# 9. Recommended implementation API

`src/task1/eda.py` should expose small deterministic functions, for example:

```python
validate_eda_input(...)
summarize_service_distribution(...)
summarize_service_by_group(...)
summarize_late_rate(...)
summarize_late_rate_by_group(...)
summarize_continuous_vs_service(...)
summarize_route_position(...)
build_planned_slack_minutes(...)
summarize_slack_vs_targets(...)
summarize_optional_context(...)
assign_planned_shift(...)
build_feature_candidate_table(...)
build_eda_warnings(...)
generate_task1_eda(...)
```

Plot functions may remain in the same module or a separate plotting module if justified.

---

# 10. Input validation and leakage guard

Before EDA, assert:

```text
delivery_id unique
service_minutes finite
service_minutes >= 0
late_flag ∈ {0,1}
```

Maintain an explicit classification such as:

```text
service_minutes              TARGET
late_flag                    TARGET
brand                        SAFE_CANDIDATE
district                     SAFE_CANDIDATE
depot                        SAFE_CANDIDATE
dock_type                    SAFE_CANDIDATE
outlet_id                    SAFE_IDENTIFIER_CANDIDATE
order_units                  SAFE_CANDIDATE
order_weight_kg              SAFE_CANDIDATE
order_volume_m3              SAFE_CANDIDATE
seq_in_route                 SAFE_CANDIDATE
planned_arrival_time         SAFE_CANDIDATE
planned_slack_min            SAFE_DERIVED_CANDIDATE
monsoon                      SAFE_IF_APPROVED
dow                          SAFE_CANDIDATE
actual_depart_time           FORBIDDEN
actual_travel_duration_min   FORBIDDEN
arrival_time                 FORBIDDEN
leave_outlet_time            FORBIDDEN
service_start_dt             TARGET_DERIVED
```

If an EDA helper tries to use a forbidden field as an explanatory input, raise an explicit error.

---

# 11. Test plan

Create `tests/test_task1_eda.py` with synthetic data only.

Minimum tests:

### Input integrity
- negative service rejected;
- nonfinite service rejected;
- invalid late flag rejected;
- duplicate delivery ID rejected;
- forbidden explanatory field rejected.

### Service summaries
- known quantiles;
- empty data fails;
- one-row group handled where meaningful.

### Group summaries
- count/median/late rate correct;
- small-group warning.

### Continuous analysis
- quantile binning;
- duplicate bin edges;
- constant feature;
- missing pairs;
- Spearman calculation.

### Planned slack
- positive;
- zero;
- negative;
- cross-midnight window;
- actual arrival ignored.

### Route position
- first stop sequence 0;
- later stop;
- sparse high sequence grouping.

### Optional context
- road disabled state;
- traffic disabled state;
- partial coverage;
- no missing=clear/free-flow fallback.

### Calendar/time
- monsoon 0/1;
- DOW order 0..6;
- all shift boundaries;
- shift based on planned arrival only.

### Candidate table
- actual journey fields always `DISABLE`;
- target columns never candidates;
- safe planned features can remain candidates.

### Privacy
- aggregate reports contain no row-record list;
- plots do not annotate delivery IDs by default.

---

# 12. Local CLI contract

Implement:

```bash
python scripts/run_task1_eda.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --labels data/interim/task1_training_labels.csv \
  --config configs/task1_eda.yaml \
  --output-dir reports/private/phase05_task1_eda
```

If the project rebuilds labels internally, it must call the canonical Phase 04 builder rather than duplicating label formulas.

Safe console output:

```text
PHASE 05 TASK 1 EDA: PASS
Required analyses: PASS
Leakage guard: PASS
Private report written locally.
No raw rows printed.
```

Do not print row-level records, delivery IDs, full outlet rankings, or private category tables.

---

# 13. Edge cases

- Heavy service tail: keep and document; do not delete.
- Late imbalance: record only; do not resample.
- Tiny outlet group: flag instability.
- Constant feature: return correlation as unavailable instead of crashing.
- Repeated quantile edges: reduce bin count safely and document.
- Missing optional road/traffic context: preserve row and mark missing/disabled.
- Same outlet with multiple orders: preserve `delivery_id` grain.
- Midnight planned windows: use approved datetime resolution.
- Negative planned slack: valid and potentially informative.
- Planned arrival exactly at closing: slack = 0; do not call it actual lateness.
- Correlated units/weight/volume: document, do not automatically drop columns.

---

# 14. STOP conditions

`READY FOR PHASE 06` must remain **NO** if:

- Phase 04 has not passed;
- labels are recomputed differently from the canonical builder;
- any target is negative/nonfinite or late flag is not binary;
- actual journey outcomes are used as predictor-style EDA variables;
- planned slack uses actual arrival;
- shift uses actual arrival;
- route position uses future/actual route completion information;
- labels are clipped/removed to improve plots;
- classes are resampled;
- road/traffic logic bypasses Phase 03-approved joins;
- missing optional context is silently treated as normal/free-flow/clear;
- high-cardinality grouped analyses omit sample size;
- private reports are tracked;
- real data is exposed to the coding agent;
- synthetic tests fail;
- local EDA run fails;
- required report/figure package is missing;
- independent review fails.

---

# 15. Definition of Done

Phase 05 is complete only when:

- [ ] DT-072 PASS
- [ ] DT-073 PASS
- [ ] DT-074 PASS
- [ ] DT-075 PASS
- [ ] DT-076 PASS
- [ ] DT-077 PASS
- [ ] DT-078 PASS
- [ ] DT-079 PASS
- [ ] DT-080 PASS
- [ ] DT-081 PASS
- [ ] DT-082 PASS
- [ ] DT-083 PASS
- [ ] DT-084 PASS
- [ ] DT-085 PASS or documented DISABLED/NOT_APPLICABLE
- [ ] DT-086 PASS or documented DISABLED/NOT_APPLICABLE
- [ ] DT-087 PASS
- [ ] DT-088 PASS
- [ ] DT-089 PASS
- [ ] DT-090 PASS
- [ ] canonical Phase 04 labels reused
- [ ] no target drift/recalculation
- [ ] no actual-outcome explanatory feature
- [ ] all grouped outputs include sample counts
- [ ] planned slack is leakage-safe
- [ ] optional road/traffic coverage rules preserved
- [ ] private figures/report generated
- [ ] feature-candidate table generated
- [ ] warnings generated
- [ ] synthetic tests pass
- [ ] local EDA run passes
- [ ] private outputs remain ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 05 STATUS: PASS
READY FOR PHASE 06: YES
```

---

# 16. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-05-task1-eda
```

Suggested commits:

```text
feat(task1): add privacy-safe EDA utilities
feat(task1): add service target summaries
feat(task1): add lateness summaries
feat(task1): add planned slack and route position analysis
feat(task1): add environmental context analysis
test(task1): add synthetic EDA tests
docs(task1): document Task 1 EDA methodology
```

Before commits:

```bash
git status
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
python -m pip check
pytest -q tests/test_project_setup.py \
          tests/test_data_inventory.py \
          tests/test_data_quality.py \
          tests/test_schema_assertions.py \
          tests/test_task1_labels.py \
          tests/test_task1_eda.py
git status
```

Merge only after local EDA and independent review both pass.

---

# 17. Enhanced Cursor implementation prompt

```text
We are implementing WayLoom Datathon PHASE 05 only.

PHASE:
Task 1 Exploratory Data Analysis

TASK RANGE:
DT-072 through DT-090

EXECUTION MODE:
Full EDA tooling phase is allowed.
Use synthetic fixtures only.
STOP after Phase 05 tooling/tests.

READ FIRST:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved Phase 00–04 contracts
3. PHASE_05_COMPETITION_CONTRACT.md
4. existing tracked Task 1 label/schema utilities

SOURCE PRIORITY:
Official organizer material > approved master plan > phase contracts > implementation assumptions.

DATA SAFETY:
DO NOT access data/raw/**, data/interim/**, or reports/private/**.
DO NOT inspect real labels or official rows.
DO NOT run real EDA.

OFFICIAL BOUNDARY:
Reuse canonical Phase 04 service_minutes and late_flag.
Do not recalculate labels with new logic.

FORBIDDEN predictor-style fields:
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

Target-derived fields service_start_dt, service_minutes and late_flag may be summarized only as targets.

CREATE:
src/task1/eda.py
scripts/run_task1_eda.py
configs/task1_eda.yaml
docs/task1_eda_method.md
tests/test_task1_eda.py

IMPLEMENT ALL TASKS:
DT-072 robust service distribution;
DT-073 service by brand;
DT-074 service by dock type;
DT-075 service by outlet with small-sample warnings and no target encoding;
DT-076 service vs order_units;
DT-077 service vs order_weight_kg;
DT-078 service vs order_volume_m3;
DT-079 overall late rate;
DT-080 late by brand;
DT-081 late by district;
DT-082 late by depot;
DT-083 route position and first-stop analysis;
DT-084 planned slack using window-close planned datetime minus planned-arrival datetime, never actual arrival;
DT-085 road context using only Phase 03-approved mapping and no missing=clear fallback;
DT-086 traffic context using approved mapping, never actual travel duration, no missing=free-flow fallback;
DT-087 monsoon;
DT-088 DOW with 0=Monday;
DT-089 planned-arrival shift using configurable engineering bins;
DT-090 private EDA report/figures plus feature-candidate table.

STATISTICAL RULES:
Every grouped result includes n.
Service summaries use mean + robust median/quantiles.
Late summaries use n + late_count + late_rate.
Prefer Spearman for continuous descriptive relationships.
Handle repeated qcut edges safely.
Do not make causal claims.
Do not fit CatBoost/LightGBM/XGBoost.
Do not resample classes.
Do not clip/drop labels.

FEATURE CANDIDATE TABLE COLUMNS:
feature
prediction_time_safe
eda_signal
sample_coverage
stability_warning
phase06_recommendation
reason

Allowed recommendations:
KEEP_CANDIDATE
KEEP_WITH_CAUTION
DEFER
DISABLE

Training-only actuals must be DISABLE.

TEST synthetic cases for:
invalid targets;
duplicate delivery_id;
forbidden explanatory fields;
service/group summaries;
small-group warnings;
quantile bins;
constant feature;
planned slack positive/zero/negative/cross-midnight;
actual arrival ignored by slack;
first-stop logic;
road/traffic disabled and partial coverage;
no missing=clear/free-flow assumption;
monsoon;
DOW ordering;
shift boundaries;
feature-candidate leakage guard;
privacy-safe report structure.

RUN ONLY:
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py tests/test_task1_eda.py
python -m pip check

DO NOT run real EDA.

LOCAL CLI CONTRACT:
python scripts/run_task1_eda.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --labels data/interim/task1_training_labels.csv --config configs/task1_eda.yaml --output-dir reports/private/phase05_task1_eda

CLI must print high-level PASS/FAIL only and write detailed results privately.

RETURN:
PHASE: 05 — AGENT IMPLEMENTATION STAGE
DT-072 READY/FAIL
DT-073 READY/FAIL
DT-074 READY/FAIL
DT-075 READY/FAIL
DT-076 READY/FAIL
DT-077 READY/FAIL
DT-078 READY/FAIL
DT-079 READY/FAIL
DT-080 READY/FAIL
DT-081 READY/FAIL
DT-082 READY/FAIL
DT-083 READY/FAIL
DT-084 READY/FAIL
DT-085 READY/FAIL/NOT_APPLICABLE
DT-086 READY/FAIL/NOT_APPLICABLE
DT-087 READY/FAIL
DT-088 READY/FAIL
DT-089 READY/FAIL
DT-090 READY/FAIL
FILES CREATED: ...
FILES MODIFIED: ...
SYNTHETIC TESTS: ...
LEAKAGE GUARD: PASS/FAIL
DATA SAFETY: official/private data accessed = NO
HUMAN LOCAL ACTION REQUIRED: YES
Print exact local command.
PHASE 05 STATUS: AWAITING LOCAL EDA RUN
READY FOR PHASE 06: NO

Then STOP. Do not start Phase 06.
```

---

# 18. Enhanced Codex implementation prompt

```text
Implement WayLoom Datathon PHASE 05 tooling only.

PHASE: Task 1 Exploratory Data Analysis
TASKS: DT-072 through DT-090
MODE: Full-phase tooling + synthetic tests only.

Read the approved master plan, Phase 00–04 contracts, PHASE_05_COMPETITION_CONTRACT.md, and existing tracked Task 1 label/schema code.

Do not access data/raw/**, data/interim/**, or reports/private/**.
Do not run real-data EDA.

Reuse canonical Phase 04 labels. Never implement a second label formula.

Never treat these as prediction-time explanatory variables:
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

Implement:
- robust service distribution;
- service by brand/dock/outlet;
- service vs units/weight/volume;
- overall late rate;
- late by brand/district/depot;
- route-position/first-stop analysis;
- leakage-safe planned slack;
- approved road context;
- approved traffic context;
- monsoon;
- DOW;
- planned-arrival shift;
- final private EDA package and feature-candidate table.

Rules:
- every grouped result includes n;
- service uses median/quantiles plus mean;
- late uses n/late_count/late_rate;
- no target clipping/removal;
- no resampling;
- no model fitting;
- no causal claims;
- no target encoding;
- no missing road=clear;
- no missing traffic=free-flow;
- planned slack and shift use planned values only.

Create:
src/task1/eda.py
scripts/run_task1_eda.py
configs/task1_eda.yaml
docs/task1_eda_method.md
tests/test_task1_eda.py

Use synthetic tests only. Run:
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py tests/test_task1_eda.py
python -m pip check

Implement local CLI:
python scripts/run_task1_eda.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --labels data/interim/task1_training_labels.csv --config configs/task1_eda.yaml --output-dir reports/private/phase05_task1_eda

Do not execute it yourself.

Return task-by-task READY/FAIL status for DT-072..DT-090, files, tests, leakage status, data-safety status, and the local command.
Then STOP with READY FOR PHASE 06 = NO until local EDA and review pass.
```

---

# 19. Enhanced independent review prompt

```text
Perform an independent review of completed WayLoom Datathon Phase 05.

DO NOT open data/raw, data/interim, or reports/private.
DO NOT execute the real EDA.
DO NOT modify code initially.
DO NOT start Phase 06.

READ:
WAYLOOM_DATATHON_MASTER_PLAN.md
PHASE_05_COMPETITION_CONTRACT.md
src/task1/eda.py
scripts/run_task1_eda.py
configs/task1_eda.yaml
docs/task1_eda_method.md
tests/test_task1_eda.py
tracked Phase 04 label code/spec
relevant tracked Phase 03 coverage utilities
.gitignore
.cursorignore

HUMAN LOCAL CONTROL RESULT:
LOCAL PHASE 05 EDA: <PASS/FAIL>
ALL REQUIRED ANALYSES GENERATED: <YES/NO>
LEAKAGE GUARD: <PASS/FAIL>
EMPTY REQUIRED SEGMENTS: <0/number>
OPTIONAL ROAD CONTEXT: <PASS/WARNING/DISABLED>
OPTIONAL TRAFFIC CONTEXT: <PASS/WARNING/DISABLED>

Audit every task DT-072 through DT-090.

Verify especially:
- canonical labels are reused;
- no second label implementation exists;
- every grouped analysis includes n;
- outlet analysis has small-sample protection and no target encoding;
- planned_slack uses planned arrival and window close only;
- shift uses planned arrival only;
- road mapping comes from Phase 03 and missing does not mean clear;
- traffic mapping comes from Phase 03 and actual travel duration is never used;
- DOW is 0=Monday and ordered correctly;
- no label clipping/removal;
- no class resampling;
- no model fitting;
- no real records in tests/docs;
- private outputs are ignored.

Run safe tests only:
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py tests/test_task1_eda.py
python -m pip check
git status

RETURN:
| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then report:
CANONICAL LABEL REUSE: PASS/FAIL
LEAKAGE PROTECTION: PASS/FAIL
STATISTICAL ROBUSTNESS: PASS/FAIL
OPTIONAL CONTEXT HANDLING: PASS/FAIL
SYNTHETIC TESTS: PASS/FAIL
HUMAN LOCAL EDA: PASS/FAIL
DATA SAFETY: PASS/FAIL
BLOCKERS: ...
NON-BLOCKING IMPROVEMENTS: ...
DT-072..DT-090 individual status
PHASE 05 REVIEW: PASS/FAIL
READY FOR PHASE 06: YES/NO

If FAIL, list exact blockers only. Do not fix automatically. Do not start Phase 06.
```

---

# 20. Local execution

After the agent implementation stage:

```bash
git status
git check-ignore -v reports/private/phase05_task1_eda/eda_summary.json
pytest -q tests/test_task1_eda.py
```

Then run locally:

```bash
python scripts/run_task1_eda.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --labels data/interim/task1_training_labels.csv \
  --config configs/task1_eda.yaml \
  --output-dir reports/private/phase05_task1_eda
```

PowerShell one-line equivalent:

```powershell
python scripts/run_task1_eda.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --labels data/interim/task1_training_labels.csv --config configs/task1_eda.yaml --output-dir reports/private/phase05_task1_eda
```

Inspect the private report and charts locally. Return only sanitized status:

```text
LOCAL PHASE 05 EDA: PASS
ALL REQUIRED ANALYSES GENERATED: YES
LEAKAGE GUARD: PASS
EMPTY REQUIRED SEGMENTS: 0
OPTIONAL ROAD CONTEXT: PASS/WARNING/DISABLED
OPTIONAL TRAFFIC CONTEXT: PASS/WARNING/DISABLED
```

Then run the independent review prompt.

---

# 21. Completion record

```markdown
# Phase 05 Completion Record

- DT-072: PASS/FAIL
- DT-073: PASS/FAIL
- DT-074: PASS/FAIL
- DT-075: PASS/FAIL
- DT-076: PASS/FAIL
- DT-077: PASS/FAIL
- DT-078: PASS/FAIL
- DT-079: PASS/FAIL
- DT-080: PASS/FAIL
- DT-081: PASS/FAIL
- DT-082: PASS/FAIL
- DT-083: PASS/FAIL
- DT-084: PASS/FAIL
- DT-085: PASS/FAIL/DISABLED
- DT-086: PASS/FAIL/DISABLED
- DT-087: PASS/FAIL
- DT-088: PASS/FAIL
- DT-089: PASS/FAIL
- DT-090: PASS/FAIL

Synthetic tests: PASS/FAIL
Leakage guard: PASS/FAIL
Local EDA: PASS/FAIL
Private outputs ignored: YES/NO
Independent review: PASS/FAIL

PHASE 05 STATUS: PASS/FAIL
READY FOR PHASE 06: YES/NO
```

Do not automatically begin Phase 06.
