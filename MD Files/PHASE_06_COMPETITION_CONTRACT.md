# PHASE 06 — Task 1 Feature Engineering

> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-091 → DT-122**  
> **Task count:** **32**  
> **Dependency:** Phase 05 must have passed  
> **Execution style:** **Controlled small batches with autonomous safe testing/debugging; critical leakage tasks reviewed individually**  
> **Phase gate:** A deterministic, train/test-parity Task 1 feature builder exists; every feature is documented and available at prediction time; historical target aggregates are chronology-safe and fold-ready; actual journey/outcome fields cannot enter the model matrix.

---

## 1. Purpose

Phase 06 converts the validated Task 1 historical population and planned test inputs into a reproducible feature system for two later models:

```text
Task 1A: service_minutes regression
Task 1B: late_flag probability estimation
```

The official challenge does **not** prescribe a feature set. It explicitly allows teams to use relevant Training Data and General Data and asks teams to choose and justify features. Therefore the feature package in this phase is a **WayLoom modelling design**, constrained by the official prediction-time boundary.

The central rule is simple:

> A Task 1 feature is valid only if its information would be available when predicting the planned delivery.

Planned departure/travel/arrival information is available at prediction time. Actual journey and handling outcomes occur later and are training-only. The final feature builder must enforce this mechanically, not rely on memory.

Phase 06 does **not** choose the final model, validation strategy, hyperparameters, probability calibration, or submission predictions. Those belong to later phases.

---

## 2. Official requirements that constrain Phase 06

### 2.1 Task 1 outputs

For each planned test `delivery_id`, later phases must produce:

```text
pred_service_min
pred_late_prob
```

### 2.2 Prediction-time information

The official challenge states that at prediction time the planned departure, planned travel duration, and planned arrival are available for each delivery. Actual journey and handling times appear only in historical route records.

### 2.3 Relevant official sources

Feature engineering may use relevant fields from:

```text
deliveries_train.csv
route_legs_train.csv
task1_test_inputs.csv
route_legs_test.csv
outlets.csv
vehicles.csv
calendar.csv
district_travel.csv
service_allowance.csv
traffic_speed.csv
road_conditions.csv
```

subject to prediction-time availability and the Phase 03 coverage decisions.

### 2.4 Official route relationship

Historical and test order records map to route legs through:

```text
order.route_id + order.seq_in_route
↔
route_leg.route_id + route_leg.seq
```

The Phase 04 canonical label builder remains the only source of Task 1 targets.

### 2.5 Official time convention

```text
Clock times: HH:MM
Local context: Asia/Colombo
Duration columns: minutes
```

### 2.6 Official data/tool restrictions

Competition data must remain confidential and must not be shared/transmitted to third parties. Proprietary API-based modelling/preprocessing and fully automated end-to-end modelling tools are prohibited. AI-assisted work must be accurately disclosed.

For this project, the agent may autonomously edit code, run safe tests, debug, use Git, and create synthetic fixtures. Raw competition rows and private row-level derivatives remain outside the external-agent context unless the team has explicit organizer-approved permission for that exact workflow.

---

## 3. Non-negotiable leakage boundary

### 3.1 Training-only actual journey fields — forbidden as direct features

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

### 3.2 Target / target-derived columns — forbidden as direct features

```text
service_start_dt
service_minutes
late_flag
```

### 3.3 Forbidden derived feature principle

A feature is also forbidden if it indirectly depends on any forbidden field.

Examples of forbidden derived features:

```text
actual_delay_min = actual_arrival - planned_arrival
actual_service_so_far
actual_route_elapsed_time
actual_previous_stop_service
actual_previous_stop_late_flag
```

Changing the column name does not make leakage acceptable.

### 3.4 Historical aggregate exception

Past labels may be used only through an explicitly chronology-safe historical-statistics transformer implemented under **DT-119**. For training rows, the current row and same/future dates must not contribute to the aggregate. For validation, aggregates must be fit only on the fold's training history. For final test inference, historical aggregates may be fit on the approved historical training data only.

---

## 4. Phase 06 task registry

| Status | Task | Priority | Work item |
|---|---|---:|---|
| [ ] | **DT-091** | P0 | Build base order features |
| [ ] | **DT-092** | P0 | Add outlet reference features |
| [ ] | **DT-093** | P0 | Add dock/access features |
| [ ] | **DT-094** | P1 | Add geography/depot features |
| [ ] | **DT-095** | P0 | Add assigned vehicle features |
| [ ] | **DT-096** | P0 | Add route-position features |
| [ ] | **DT-097** | P0 | Add route stop count |
| [ ] | **DT-098** | P1 | Add normalized sequence position |
| [ ] | **DT-099** | P0 | Add first-stop indicator |
| [ ] | **DT-100** | P0 | Add planned departure/arrival time features |
| [ ] | **DT-101** | P0 | Add planned slack-to-window features |
| [ ] | **DT-102** | P1 | Add planned early-wait features |
| [ ] | **DT-103** | P0 | Add route-leg distance features |
| [ ] | **DT-104** | P0 | Add planned travel-duration features |
| [ ] | **DT-105** | P0 | Join calendar context |
| [ ] | **DT-106** | P1 | Add payday features |
| [ ] | **DT-107** | P1 | Add festival features |
| [ ] | **DT-108** | P1 | Add festival-ramp features |
| [ ] | **DT-109** | P0 | Add monsoon features |
| [ ] | **DT-110** | P1 | Add road-condition features when approved |
| [ ] | **DT-111** | P1 | Add traffic-speed features when approved |
| [ ] | **DT-112** | P0 | Add standard service-allowance feature |
| [ ] | **DT-113** | P1 | Add weight-per-unit features |
| [ ] | **DT-114** | P1 | Add volume-per-unit features |
| [ ] | **DT-115** | P1 | Add density features |
| [ ] | **DT-116** | P0 | Add planned route totals |
| [ ] | **DT-117** | P0 | Add route/vehicle utilization features |
| [ ] | **DT-118** | P0 | Add cumulative planned route-context features |
| [ ] | **DT-119** | P0 | Implement leakage-safe historical statistics |
| [ ] | **DT-120** | P0 | Build feature metadata / feature registry |
| [ ] | **DT-121** | P0 | Implement automated leakage checks |
| [ ] | **DT-122** | P0 | Enforce zero actual-journey fields in final model matrix |

**Phase complete:** [ ]  
**READY FOR PHASE 07:** NO

---

## 5. Recommended repository additions

Tracked:

```text
src/task1/
├── features.py
├── feature_registry.py
└── historical_features.py

scripts/
└── build_task1_features.py

configs/
└── task1_features.yaml

docs/
└── task1_feature_spec.md

tests/
├── test_task1_features.py
├── test_task1_feature_leakage.py
└── test_task1_historical_features.py
```

Private local outputs:

```text
data/interim/
├── task1_features_train.csv
└── task1_features_test.csv

reports/private/phase06_task1_features/
├── build_summary.json
├── feature_registry.json
├── train_test_parity.json
├── missingness_summary.json
├── historical_feature_audit.json
├── leakage_audit.json
└── feature_build_report.md
```

The private outputs must remain ignored by Git and excluded from external-agent indexing.

---

## 6. Canonical feature-builder architecture

Recommended public API:

```python
build_task1_base_table(...)
add_order_features(...)
add_outlet_features(...)
add_vehicle_features(...)
add_route_context_features(...)
add_planned_time_features(...)
add_calendar_features(...)
add_environment_features(...)
add_service_allowance(...)
add_ratio_features(...)
add_route_aggregate_features(...)
add_cumulative_planned_features(...)
fit_historical_feature_transformer(...)
transform_historical_features(...)
build_feature_registry(...)
audit_feature_leakage(...)
build_task1_feature_matrix(...)
```

The final high-level builder should support both historical training rows and Task 1 test rows using the same feature definitions.

Recommended shape:

```python
X, metadata = build_task1_feature_matrix(
    orders=...,
    route_legs=...,
    outlets=...,
    vehicles=...,
    calendar=...,
    district_travel=...,
    service_allowance=...,
    traffic_speed=...,
    road_conditions=...,
    mode="train" | "test",
    historical_transformer=...,
)
```

The builder must never derive target labels. It receives labels separately when needed by later training code.

---

# 7. Detailed implementation tasks

## DT-091 — Build base order features

**Priority:** P0  
**Execution batch:** A

### Objective

Create the starting prediction-time feature table at one row per `delivery_id`.

### Safe base fields

At minimum preserve or expose:

```text
delivery_id                 traceability only; not automatically a model feature
order_date
dispatch_date               if populated and genuinely known at prediction time
outlet_id
brand
district
depot
temp_requirement
order_units
order_weight_kg
order_volume_m3
route_id
seq_in_route
vehicle_id
vehicle_type
vehicle_temp
planned_arrival_time
window_open_time
window_close_time
```

### Rules

- Preserve `delivery_id` for traceability and later submission alignment.
- Keep raw IDs separate from the model-feature allow-list.
- Do not use `dispatch_status` as a predictor without documenting whether it exists/means the same thing for all test rows. Since all Task 1 test rows were dispatched, it is likely low-value and may create train/test artifacts; default recommendation is metadata only unless validation later supports it.
- Do not include Phase 04 labels in `X`.
- Do not mutate source columns.

### Tests

- one row per `delivery_id`;
- input order preserved;
- duplicate ID fails;
- forbidden fields excluded from candidate feature list;
- numeric order fields stay numeric.

### Definition of Done

- [ ] deterministic base table;
- [ ] one row per delivery;
- [ ] traceability preserved;
- [ ] labels absent from predictor list.

### STOP conditions

Stop if the base table changes Task 1 grain or mixes training labels into features.

---

## DT-092 — Add outlet reference features

**Priority:** P0  
**Execution batch:** A

### Objective

Join static outlet information known before delivery.

### Official outlet reference candidates

```text
brand
district
depot
dock_type
parking_constraint
mall_window
window_open_time
window_close_time
```

### Rules

- Join using `outlet_id`.
- Reuse Phase 03 reference-integrity assumptions.
- Where a field exists in both order and outlet tables, validate consistency rather than silently overwrite.
- Prefer one canonical field after successful consistency checks.
- Do not use any outcome-derived outlet statistic here; historical target statistics belong only to DT-119.

### Tests

- valid one-to-one outlet join;
- unknown outlet fails;
- duplicated outlet reference fails;
- conflicting brand/depot/window values fail or are explicitly reconciled by approved rule.

### Definition of Done

- [ ] outlet join one-to-one;
- [ ] static attributes available;
- [ ] no target-history leakage.

---

## DT-093 — Add dock/access features

**Priority:** P0  
**Execution batch:** A

### Objective

Expose operational access conditions that can plausibly affect handling or route feasibility.

### Candidate fields

```text
dock_type
parking_constraint
has_mall_window
mall_window_start_minute
mall_window_end_minute
mall_window_crosses_midnight
```

### Engineering notes

`dock_type` and `parking_constraint` may remain categorical for CatBoost-style models. Parsed mall-window features may be useful numeric context.

### Rules

- Parse `mall_window` only when present.
- Blank mall window outside malls is expected.
- Never fabricate a mall window.
- Do not convert `van_only` into a hard prediction outcome; it is a known access attribute.

### Tests

- rear_dock/street/mall_bay accepted;
- blank non-mall window handled;
- valid cross-midnight mall window parsed;
- malformed nonblank mall window fails.

### Definition of Done

- [ ] dock/access features deterministic;
- [ ] missingness semantics preserved.

---

## DT-094 — Add geography/depot features

**Priority:** P1  
**Execution batch:** A

### Objective

Represent stable spatial/operational location context without inventing geospatial coordinates.

### Candidate features

```text
district
depot
road_class                    if safely obtained from district_travel reference
depot_to_district_km
depot_to_district_freeflow_min
inter_stop_km
inter_stop_freeflow_min
```

### Rules

- Use official reference joins only.
- Do not fabricate latitude/longitude.
- Do not use external maps/geocoding.
- If `district_travel` uses a composite key, enforce it exactly.

### Tests

- correct district/depot join;
- ambiguous reference key fails;
- numeric travel references nonnegative.

### Definition of Done

- [ ] stable reference geography added;
- [ ] no external data introduced.

---

## DT-095 — Add assigned vehicle features

**Priority:** P0  
**Execution batch:** A

### Objective

Add attributes of the vehicle already assigned to the planned delivery.

### Candidate fields

```text
vehicle_type
vehicle_temp
vehicle_home_depot
weight_cap_kg
volume_cap_m3
fuel_type
km_per_l
weekly_fuel_quota_l
```

### Feature-selection caution

Fuel attributes may be known but may not improve Task 1 handling/lateness. Keep them in the candidate registry rather than assuming importance.

### Rules

- Join by `vehicle_id`.
- Validate copied type/temp/depot fields against order/route values.
- Do not compute actual fuel usage.

### Tests

- one-to-one join;
- missing assigned vehicle fails for Task 1 rows;
- type/temp mismatch fails;
- capacities positive.

### Definition of Done

- [ ] vehicle metadata available;
- [ ] no actual operational outcome added.

---

## DT-096 — Add route-position features

**Priority:** P0  
**Execution batch:** B

### Objective

Represent the order's planned position in its route.

### Features

```text
route_seq = seq_in_route
```

Optional categorical bucket:

```text
route_seq_bucket
```

Example engineering bins:

```text
0
1
2
3
4+
```

### Rules

- Position is the planned sequence from official route data.
- Do not derive position from actual arrival order.

### Tests

- starts at 0;
- route-leg `seq` matches order `seq_in_route`;
- no negative values.

### Definition of Done

- [ ] planned sequence exposed consistently.

---

## DT-097 — Add route stop count

**Priority:** P0  
**Execution batch:** B

### Objective

Measure the planned number of delivery stops on the assigned route.

### Definition

```text
route_stop_count = number of Task 1 order/leg stops with the same route_id
```

### Rules

- Count from planned route structure, not completed stops.
- Build train and test counts using their respective planned route tables.
- Do not include orphan/non-delivery rows unless official route semantics prove they represent stops in the same Task 1 route.

### Tests

- one-stop route = 1;
- multi-stop route correctly repeated on all route rows;
- route counts independent between routes.

### Definition of Done

- [ ] planned stop count available for every row.

---

## DT-098 — Add normalized sequence position

**Priority:** P1  
**Execution batch:** B

### Objective

Represent relative route position independent of route length.

### Recommended definition

```text
route_seq_fraction =
    seq_in_route / (route_stop_count - 1)
```

For a one-stop route:

```text
route_seq_fraction = 0.0
```

### Invariants

For valid route structure:

```text
0 <= route_seq_fraction <= 1
```

### Tests

- one-stop route;
- first stop of multi-stop route = 0;
- last stop = 1;
- intermediate values correct.

### Definition of Done

- [ ] normalized position deterministic;
- [ ] no divide-by-zero/infinite values.

---

## DT-099 — Add first-stop indicator

**Priority:** P0  
**Execution batch:** B

### Definition

```text
is_first_stop = 1 if seq_in_route == 0 else 0
```

### Why useful

First stops have different planned context from later stops because no earlier delivery stops have occurred.

### Rules

This is based only on planned sequence.

### Tests

- seq 0 → 1;
- seq >0 → 0;
- only binary values.

### Definition of Done

- [ ] first-stop indicator exact.

---

## DT-100 — Add planned departure/arrival time features

**Priority:** P0  
**Execution batch:** B

### Objective

Convert known planned clock fields into model-friendly time context.

### Candidate features

From `planned_depart_time` and `planned_arrival_time`:

```text
planned_depart_minute_of_day
planned_arrival_minute_of_day
planned_depart_hour
planned_arrival_hour
planned_depart_sin
planned_depart_cos
planned_arrival_sin
planned_arrival_cos
```

Optional resolved datetime fields may remain internal to feature construction and need not be model inputs.

### Cyclical encoding

For minute-of-day `m`:

```text
sin(2πm/1440)
cos(2πm/1440)
```

### Rules

- Strictly parse `HH:MM`.
- Use planned values only.
- Handle route-date/midnight resolution for interval calculations.
- Cyclical encoding is a WayLoom engineering choice, not an official requirement.

### Tests

- 00:00, 06:00, 12:00, 18:00, 23:59;
- valid cyclic range [-1,1];
- malformed time fails.

### Definition of Done

- [ ] planned time represented numerically;
- [ ] no actual clock field involved.

---

## DT-101 — Add planned slack-to-window features

**Priority:** P0  
**Execution batch:** B

### Objective

Convert the Phase 05 planned slack signal into a reproducible feature.

### Core definition

```text
planned_slack_to_close_min =
    resolved_window_close_dt - resolved_planned_arrival_dt
```

Positive means planned arrival before closing; zero means exactly at close; negative means plan is already past close.

### Candidate derivatives

```text
planned_is_after_close = int(slack < 0)
planned_is_close_boundary = int(slack == 0)
```

Optional bins may be retained as categorical candidates, but keep the raw continuous slack.

### Critical rule

Never use `arrival_time` or any actual outcome.

### Tests

- positive/zero/negative slack;
- cross-midnight window;
- planned arrival after midnight;
- source lineage proves only planned/window fields.

### Definition of Done

- [ ] slack feature leakage-safe;
- [ ] midnight-safe;
- [ ] raw continuous feature retained.

### STOP conditions

Any dependency on actual arrival is an immediate blocker.

---

## DT-102 — Add planned early-wait features

**Priority:** P1  
**Execution batch:** B

### Objective

Represent planned waiting expected when a route is scheduled before the outlet opens.

### Definition

```text
planned_early_wait_min =
    max(0, resolved_window_open_dt - resolved_planned_arrival_dt)
```

Optional:

```text
planned_arrives_before_open = int(planned_early_wait_min > 0)
```

### Important distinction

This is planned waiting, not actual waiting and not the service label.

### Tests

- planned arrival before open;
- exactly at open;
- after open;
- midnight-safe window.

### Definition of Done

- [ ] planned early-wait context available;
- [ ] no actual arrival dependency.

---

## DT-103 — Add route-leg distance features

**Priority:** P0  
**Execution batch:** B

### Objective

Use the planned road distance to the current stop.

### Core feature

```text
leg_distance_km = distance_km
```

Optional transformations for later model comparison:

```text
log1p_leg_distance_km
```

Do not force the transformed version into the final model merely because it exists.

### Tests

- nonnegative;
- train/test column parity;
- no actual traveled distance introduced.

### Definition of Done

- [ ] planned distance available.

---

## DT-104 — Add planned travel-duration features

**Priority:** P0  
**Execution batch:** B

### Objective

Use the official planned travel duration under clear-road assumptions.

### Core feature

```text
planned_travel_duration_min
```

Optional ratio candidate:

```text
planned_leg_speed_kmh =
    distance_km / (planned_travel_duration_min / 60)
```

Only compute when duration > 0; otherwise return missing + documented guard.

### Critical rule

Do not use:

```text
actual_travel_duration_min
```

### Tests

- nonnegative duration;
- ratio zero guard;
- actual field rejected.

### Definition of Done

- [ ] planned travel context present;
- [ ] no actual travel leakage.

---

## DT-105 — Join calendar context

**Priority:** P0  
**Execution batch:** C

### Objective

Add date context available before the delivery.

### Canonical date

Use the planned route/service date defined consistently by the project's Phase 03/04 date relationship. Prefer the route-leg `date` for route context and assert consistency with dispatched order date fields where applicable.

### Candidate calendar features

```text
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

### Rules

- Join to `calendar.date`.
- Coverage must already have passed Phase 03.
- Avoid redundant raw string dates as model categories unless deliberately justified.
- `dow_name` may be metadata if numeric `dow` is sufficient.

### Tests

- one-to-one date join;
- missing calendar date fails;
- Monday=0 consistency;
- train/test parity.

### Definition of Done

- [ ] canonical calendar join deterministic.

---

## DT-106 — Add payday features

**Priority:** P1  
**Execution batch:** C

### Feature

```text
is_payday
```

Optional proximity-to-payday features should **not** be invented unless supported by a clearly documented calendar rule and later validated.

### Tests

- binary 0/1;
- comes from calendar only.

### Definition of Done

- [ ] payday context included as official calendar signal.

---

## DT-107 — Add festival features

**Priority:** P1  
**Execution batch:** C

### Feature

```text
festival
```

### Rules

- Treat blank/no-festival according to official calendar semantics.
- Preserve festival as categorical context.
- Do not manually label additional festivals from external calendars.

### Tests

- blank handled consistently;
- no external enrichment.

### Definition of Done

- [ ] supplied festival context available.

---

## DT-108 — Add festival-ramp features

**Priority:** P1  
**Execution batch:** C

### Feature

```text
festival_ramp
```

Official range:

```text
0..1
```

### Rules

- Preserve continuous value.
- Optional `is_festival_ramp = festival_ramp > 0` may be added as an engineering candidate.

### Tests

- range [0,1];
- missing invalid if calendar coverage says field is required.

### Definition of Done

- [ ] continuous ramp context included.

---

## DT-109 — Add monsoon features

**Priority:** P0  
**Execution batch:** C

### Objective

Use the official known monsoon indicator.

### Canonicalization

If both route legs and calendar contain `monsoon`:

1. assert consistency where they describe the same date;
2. choose one canonical feature source in code;
3. record the source in feature metadata.

Recommended canonical source:

```text
calendar.monsoon
```

with route-leg monsoon used as a consistency check.

### Tests

- binary;
- duplicate-source mismatch raises/warns according to Phase 03 policy;
- one final feature column.

### Definition of Done

- [ ] monsoon feature has one documented source.

---

## DT-110 — Add road-condition features when approved

**Priority:** P1  
**Execution batch:** C

### Objective

Use road disruption context only if Phase 03 established a valid prediction-time join and acceptable coverage.

### Candidate feature

```text
disruption_index
```

plus other officially observed road fields only if documented and prediction-time valid.

### Rules

- Reuse the approved Phase 03 join key.
- Do not invent a join.
- Do not set missing road data to `100`/clear.
- Add an explicit missing indicator if the later modelling strategy needs it, but leave the raw missing value missing.
- If Phase 03 disabled road features, this task should produce a clean disabled state rather than forcing the feature.

### Tests

- enabled valid join;
- disabled path;
- partial coverage;
- missing stays missing;
- no actual outcome dependency.

### Definition of Done

- [ ] road feature either safely enabled or explicitly disabled.

---

## DT-111 — Add traffic-speed features when approved

**Priority:** P1  
**Execution batch:** C

### Objective

Use typical planned-context traffic speed information.

### Core candidate

```text
speed_index
```

The official interpretation states:

```text
100 = free flow
lower = slower
```

### Rules

- Reuse Phase 03-approved join dimensions.
- Typical district/hour/monsoon context must be based on known planned timing.
- Do not use actual arrival or actual travel duration to choose the traffic row.
- Do not fill missing traffic with 100 automatically.
- Optional missing indicator is acceptable.

### Tests

- planned hour used;
- actual fields intentionally absent from dependency graph;
- missing remains missing;
- disabled path works.

### Definition of Done

- [ ] traffic feature prediction-time safe or disabled.

---

## DT-112 — Add standard service-allowance feature

**Priority:** P0  
**Execution batch:** C

### Objective

Add the dispatcher's standard handling allowance as a known planning/reference feature.

### Official join

```text
brand + dock_type
↔
service_allowance.csv
```

### Feature

```text
service_allowance_min
```

### Important distinction

The allowance is a planning/reference value, not the actual service target. It may be highly informative but is legitimate because it exists independently of the historical service outcome.

### Tests

- composite join one-to-one;
- every valid brand+dock pair resolves;
- nonnegative allowance;
- label columns never used to calculate it.

### Definition of Done

- [ ] allowance available for every applicable row.

---

## DT-113 — Add weight-per-unit features

**Priority:** P1  
**Execution batch:** D

### Definition

```text
weight_per_unit_kg = order_weight_kg / order_units
```

### Zero guard

If `order_units <= 0`:

```text
weight_per_unit_kg = missing
```

and optionally:

```text
zero_or_invalid_units_flag = 1
```

Do not emit infinity.

### Tests

- normal ratio;
- zero units;
- missing numeric values;
- no infinity.

### Definition of Done

- [ ] stable ratio feature.

---

## DT-114 — Add volume-per-unit features

**Priority:** P1  
**Execution batch:** D

### Definition

```text
volume_per_unit_m3 = order_volume_m3 / order_units
```

Use the same zero-denominator policy as DT-113.

### Tests

- normal;
- zero units;
- no infinity.

### Definition of Done

- [ ] stable volume-per-unit feature.

---

## DT-115 — Add density features

**Priority:** P1  
**Execution batch:** D

### Definition

Recommended:

```text
cargo_density_kg_per_m3 = order_weight_kg / order_volume_m3
```

### Zero guard

If volume <= 0:

```text
cargo_density_kg_per_m3 = missing
```

Do not emit infinity.

### Interpretation caution

Density is an engineering ratio, not a directly observed official field. Keep its formula documented.

### Tests

- normal ratio;
- zero volume;
- no infinity/overflow.

### Definition of Done

- [ ] density feature documented and numerically safe.

---

## DT-116 — Add planned route totals

**Priority:** P0  
**Execution batch:** D

### Objective

Represent total planned workload assigned to the same route.

### Recommended route-level totals

```text
route_total_units
route_total_weight_kg
route_total_volume_m3
route_total_distance_km
route_total_planned_travel_min
route_total_service_allowance_min
route_stop_count
```

### Rules

- Aggregate only prediction-time/planned quantities.
- Use all planned Task 1 stops on the route.
- Never aggregate historical actual service/travel/late outcomes.
- Build train route totals from historical planned inputs and test route totals from test planned inputs using identical logic.

### Tests

- correct sums by route;
- separate routes independent;
- current row may contribute its own planned workload because route plan is known before execution;
- forbidden actual columns rejected.

### Definition of Done

- [ ] route totals prediction-time safe;
- [ ] train/test logic identical.

---

## DT-117 — Add route/vehicle utilization features

**Priority:** P0  
**Execution batch:** D

### Objective

Express how heavily the assigned vehicle is planned to be loaded.

### Recommended features

```text
route_weight_utilization = route_total_weight_kg / weight_cap_kg
route_volume_utilization = route_total_volume_m3 / volume_cap_m3
route_max_utilization = max(weight_utilization, volume_utilization)
```

### Rules

- Capacities come from the static vehicle reference.
- Do not clip utilization to 1. Values >1 are informative/suspicious and should be preserved unless earlier audit rules prove impossible.
- No division by zero; invalid capacity is a blocker from Phase 03.

### Tests

- normal utilization;
- >1 retained;
- exact 1;
- invalid zero capacity fails.

### Definition of Done

- [ ] planned utilization features available.

---

## DT-118 — Add cumulative planned route-context features

**Priority:** P0  
**Execution batch:** D

### Objective

Represent the planned workload before the current stop using only information known from the route plan.

### Recommended features for stops with smaller `seq`

```text
prior_stop_count
prior_planned_units
prior_planned_weight_kg
prior_planned_volume_m3
prior_leg_distance_km
prior_planned_travel_min
prior_service_allowance_min
```

Optional inclusive variants may be created if names clearly distinguish them:

```text
cumulative_through_current_...
```

### Critical rule

Do **not** use previous stops' actual:

```text
arrival_time
leave_outlet_time
actual_travel_duration_min
service_minutes
late_flag
```

Even though those are historical in training, they would not necessarily be known when producing the pre-route test predictions requested by the competition.

### Algorithm

For each `route_id`:

1. sort by `seq_in_route`;
2. compute cumulative sums of planned/static quantities;
3. shift by one stop for `prior_*` features;
4. fill first-stop prior counts/sums with zero where mathematically appropriate.

### Tests

- first stop prior values = 0;
- second stop gets first stop's planned quantities;
- route reset works;
- source dependency audit contains no actual fields.

### Definition of Done

- [ ] cumulative context uses planned quantities only;
- [ ] first-stop behavior deterministic.

---

## DT-119 — Implement leakage-safe historical statistics

**Priority:** P0  
**Execution:** **INDIVIDUAL CRITICAL GATE**

### Objective

Add historical handling/lateness priors without allowing the current or future target to leak into training or validation.

### Why this task is special

Historical target aggregates can be powerful but are one of the easiest places to leak labels. This task must be implemented as a transformer with explicit fit/transform semantics, not as a one-time groupby over the full dataset.

### Candidate statistics

Start with a small, explainable set:

```text
outlet_prior_service_median
outlet_prior_late_rate
brand_dock_prior_service_median
brand_dock_prior_late_rate
brand_prior_service_median
brand_prior_late_rate
```

Optional district/depot historical priors may be added later only if justified.

### Training-row rule

For each training row on date `D`, its historical statistics may use only records with:

```text
historical_date < D
```

Do not use same-day labels, even if row order would make them appear earlier in the DataFrame. This avoids accidental same-day cross-order leakage.

### Validation rule

The later validation phase must be able to:

```text
fit historical transformer on training fold only
transform validation fold using only that fitted history
```

Do not precompute one full-training target aggregate and carry it into chronological validation.

### Final test rule

For test inference, fit the historical transformer on the approved historical training population and transform test rows without using any test labels (none exist).

### Smoothing / fallback

Implement configurable minimum count and fallback hierarchy.

Recommended fallback example:

```text
outlet prior
→ brand+dock prior
→ brand prior
→ global historical prior
```

The global prior must also obey the same chronology/fold rule.

### Missing-history behavior

A brand-new group must receive a documented fallback, not NaN if the model pipeline cannot handle it.

### Recommended API

```python
class Task1HistoricalFeatureTransformer:
    def fit(self, X, y_service, y_late): ...
    def transform(self, X): ...
    def fit_transform_training_chronological(self, X, y_service, y_late): ...
```

The API may differ, but fit scope must be explicit.

### Required tests

- current row does not use its own target;
- future row does not influence earlier row;
- same-date rows do not influence each other;
- validation transform does not read validation targets;
- unseen outlet falls back;
- fallback still uses training history only;
- deterministic results;
- shuffled input does not change date-based historical result after key alignment.

### Definition of Done

- [ ] fit/transform separation explicit;
- [ ] strict earlier-date rule for row-wise training history;
- [ ] fold-safe transformer supported;
- [ ] fallback hierarchy documented;
- [ ] no full-dataset target encoding.

### STOP conditions

Stop Phase 06 if any historical feature can see its own, same-date, validation, or future target.

---

## DT-120 — Build feature metadata / feature registry

**Priority:** P0  
**Execution batch:** F

### Objective

Make every feature auditable and reproducible.

### Required metadata fields

For every candidate feature record:

```text
feature_name
feature_group
source_table
source_columns
formula_or_mapping
semantic_type
prediction_time_safe
uses_target_history
requires_fit
fit_scope
missing_value_policy
train_available
test_available
categorical
model_candidate
rationale
status
```

Recommended status values:

```text
ENABLED
OPTIONAL
DISABLED
HISTORICAL_FOLD_SAFE_ONLY
```

### Example

```text
feature_name: planned_slack_to_close_min
source_columns: planned_arrival_time, window_close_time
prediction_time_safe: true
uses_target_history: false
requires_fit: false
status: ENABLED
```

Forbidden example:

```text
feature_name: actual_travel_duration_min
prediction_time_safe: false
status: DISABLED
```

### Outputs

Tracked methodology:

```text
docs/task1_feature_spec.md
```

Runtime registry can be code/YAML/JSON generated from tracked definitions.

### Tests

- every produced model feature has one registry entry;
- no duplicate feature names;
- disabled feature cannot enter final allow-list;
- historical features marked as requiring fit.

### Definition of Done

- [ ] complete feature registry;
- [ ] every feature has lineage and safety status.

---

## DT-121 — Implement automated leakage checks

**Priority:** P0  
**Execution:** **INDIVIDUAL CRITICAL GATE**

### Objective

Mechanically prove the feature matrix respects the competition's prediction-time boundary.

### Layer 1 — forbidden-column deny-list

At minimum:

```python
FORBIDDEN_DIRECT_TASK1_FEATURES = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_start_dt",
    "service_minutes",
    "late_flag",
}
```

### Layer 2 — feature-lineage audit

Every enabled feature's `source_columns` must be checked against forbidden source columns.

A feature named `delay_minutes` must still fail if its lineage contains `arrival_time`.

### Layer 3 — train/test availability

Every non-historical enabled feature must be constructible in both train and Task 1 test inputs/reference tables.

### Layer 4 — fit-scope audit

Features marked `uses_target_history=true` must:

- require fitting;
- use the historical transformer;
- not exist as globally precomputed full-training target encodings.

### Layer 5 — target separation

`X` must not contain `y` columns or equivalent aliases.

### Layer 6 — deterministic column order

Train/test feature matrices should have exactly the same feature columns in the same order before model-specific encoding.

### Tests

- direct forbidden column rejected;
- renamed derived leakage rejected by lineage;
- target column rejected;
- missing test feature rejected;
- disabled feature rejected;
- valid planned feature passes;
- historical feature with missing fit metadata rejected.

### Definition of Done

- [ ] leakage audit machine-enforced;
- [ ] train/test parity enforced;
- [ ] lineage checks active.

### STOP conditions

Any enabled feature fails the leakage audit.

---

## DT-122 — Enforce zero actual-journey fields in final model matrix

**Priority:** P0  
**Execution:** **FINAL CRITICAL GATE**

### Objective

Make it impossible for actual journey information to survive into the final Task 1 model matrix.

### Required final matrix contract

Before returning `X_train` or `X_test`, assert:

```text
actual_depart_time not in columns
actual_travel_duration_min not in columns
arrival_time not in columns
leave_outlet_time not in columns
service_start_dt not in columns
service_minutes not in columns
late_flag not in columns
```

Also assert that no enabled feature has lineage to the first four actual journey fields except the explicitly controlled historical-statistics transformer, which uses only past target history and does not derive from current actual journey data.

### Defense in depth

Recommended:

1. construct from an explicit allow-list rather than dropping a deny-list at the end;
2. run deny-list assertion anyway;
3. run registry/lineage audit;
4. compare train/test matrices;
5. emit a private leakage-audit summary.

### Required tests

- inject actual field into input → final `X` still excludes or hard-fails according to API design;
- inject actual-derived feature with lineage → hard-fail;
- target fields present in labelled source → excluded from `X`;
- train/test feature column equality;
- final matrix has no forbidden names.

### Definition of Done

- [ ] final model matrix contains zero direct actual/target fields;
- [ ] allow-list/registry controls output;
- [ ] leakage audit passes.

### STOP conditions

Any actual journey or target-derived field appears in the final model feature matrix.

---

# 8. Recommended feature groups

The final registry should group features approximately as:

```text
ORDER_BASE
OUTLET_STATIC
ACCESS
GEOGRAPHY
VEHICLE_STATIC
ROUTE_POSITION
PLANNED_TIME
WINDOW_CONTEXT
ROUTE_LEG_PLAN
CALENDAR
ENVIRONMENT
SERVICE_REFERENCE
ORDER_RATIOS
ROUTE_TOTALS
VEHICLE_UTILIZATION
CUMULATIVE_PLANNED
HISTORICAL_FOLD_SAFE
```

This grouping simplifies ablation tests later.

---

# 9. Missing-value policy

Do not apply one global imputation strategy in Phase 06.

Feature-level policy belongs in the registry.

Examples:

```text
road disruption missing
→ preserve missing + optional missing indicator

traffic speed missing
→ preserve missing + optional missing indicator

weight_per_unit with zero units
→ missing + denominator guard flag

unseen historical outlet prior
→ fallback hierarchy

blank festival
→ explicit no-festival representation according to calendar semantics
```

Model-specific imputation/encoding choices can be finalized in modelling phases.

---

# 10. Train/test parity contract

The same deterministic feature code must be used for:

```text
historical training orders + route_legs_train
Task 1 test orders + route_legs_test
```

Required checks:

```text
same enabled non-target feature names
same column order
same semantic types
same categorical flags
same formula definitions
same reference joins
same missing-value policy
```

Allowed difference:

```text
historical target columns exist only outside X_train
```

Historical target-statistic features may differ in fitted values because the fit history differs, but their column definitions must remain identical.

---

# 11. Full synthetic test plan

Create/extend:

```text
tests/test_task1_features.py
tests/test_task1_historical_features.py
tests/test_task1_feature_leakage.py
```

All agent-run tests use synthetic fixtures only.

## Base/reference tests

- one row per delivery;
- outlet join;
- vehicle join;
- district travel join;
- service allowance join;
- duplicated reference key fails.

## Route tests

- seq position;
- stop count;
- sequence fraction;
- first stop;
- route totals;
- utilization;
- cumulative prior context resets per route.

## Planned-time tests

- strict HH:MM;
- minute-of-day;
- cyclical encoding;
- planned slack positive/zero/negative;
- planned early wait;
- cross-midnight window;
- actual time never referenced.

## Calendar/environment tests

- date join;
- payday;
- festival blank handling;
- festival ramp bounds;
- monsoon canonicalization;
- road enabled/disabled/partial coverage;
- traffic enabled/disabled/partial coverage;
- missing road/traffic not replaced with normal values.

## Ratio tests

- weight/unit;
- volume/unit;
- density;
- zero denominator;
- no inf/-inf.

## Historical-statistics tests

- strictly earlier date only;
- same-day exclusion;
- current-target exclusion;
- future-target exclusion;
- fold fit/transform separation;
- unseen-group fallback;
- deterministic after input shuffle.

## Registry tests

- every feature registered;
- no duplicate feature name;
- source lineage present;
- historical features require fit;
- disabled features not in allow-list.

## Leakage tests

- direct actual field rejected;
- actual-derived lineage rejected;
- target field rejected;
- train/test parity;
- no actual/target field in final matrix.

---

# 12. Edge-case catalogue

## One-stop route

```text
route_stop_count = 1
route_seq_fraction = 0
prior_stop_count = 0
prior cumulative planned sums = 0
```

## Planned route crosses midnight

Resolve planned event intervals using the same tested local-date principles as Phase 04, but never use actual timestamps.

## Planned arrival before outlet opens

`planned_early_wait_min` may be positive and is valid.

## Planned arrival after outlet closes

Negative planned slack is valid and should not be clipped.

## Route utilization > 1

Do not clip. Preserve as a signal and separately ensure upstream reference/route data are valid.

## Zero units or zero volume

Do not divide by zero. Produce missing ratio and explicit guard behavior.

## New outlet in later data

Historical outlet prior must fall back; static outlet reference still has to resolve.

## Same-day multiple orders

Do not allow same-day target labels to influence one another through DT-119 historical statistics.

## Test category unseen in training

Static categorical feature may remain valid if it exists in official references. Later model handling must support unknown categories where necessary.

## Optional road/traffic disabled

The feature builder must still succeed and produce a stable matrix without those optional columns, according to the fixed configuration used for both train and test.

## Missing optional road/traffic record

Do not drop the delivery. Preserve missingness consistently.

---

# 13. Execution plan

Phase 06 is a **hybrid high-risk feature phase**. The agent may autonomously run all safe tests, debug failures, rerun regression tests, inspect source code and Git diffs, and continue through the batches below. It must stop on a genuine leakage/contract blocker.

## Batch A — Base/static context

```text
DT-091–DT-095
```

Then run targeted tests.

## Batch B — Route/planned-time context

```text
DT-096–DT-104
```

Then run route/time/slack tests and leakage tests.

## Batch C — Calendar/environment/reference handling

```text
DT-105–DT-112
```

Then run calendar/road/traffic/service-allowance tests.

## Batch D — Ratios/route aggregates/cumulative plan

```text
DT-113–DT-118
```

Then run ratio/route aggregation tests.

## Critical Gate E — Historical target statistics

```text
DT-119
```

Implement and test independently. If any same-row, same-date, future or validation-target leakage exists, STOP.

## Batch F — Metadata

```text
DT-120
```

## Critical Gate G — Leakage auditor

```text
DT-121
```

## Final Gate H — Zero actual journey fields

```text
DT-122
```

Run the full regression suite and self-review before stopping.

---

# 14. Local feature-build CLI contract

Recommended:

```bash
python scripts/build_task1_features.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --labels data/interim/task1_training_labels.csv \
  --config configs/task1_features.yaml \
  --train-output data/interim/task1_features_train.csv \
  --test-output data/interim/task1_features_test.csv \
  --report-dir reports/private/phase06_task1_features
```

PowerShell equivalent can be run on one line.

### Local script behavior

It should:

1. resolve official files using the existing manifest;
2. build train/test features through the same code path;
3. keep targets separate;
4. run registry/leakage/parity assertions;
5. write private feature matrices;
6. write private audit reports;
7. print only high-level PASS/FAIL status;
8. return non-zero on a hard failure.

### Safe success output

```text
PHASE 06 TASK 1 FEATURE BUILD: PASS
Train feature matrix: PASS
Test feature matrix: PASS
Train/test parity: PASS
Historical feature safety: PASS
Leakage audit: PASS
Forbidden direct fields in X: 0
Detailed reports stored locally.
```

Do not print real rows or target values.

---

# 15. Phase 06 STOP conditions

`READY FOR PHASE 07` must remain **NO** if any of the following is unresolved:

- Phase 05 did not pass;
- Phase 04 canonical labels are bypassed or recomputed inconsistently;
- order/route grain changes unexpectedly;
- required outlet/vehicle/reference join fails;
- planned slack uses actual arrival;
- early-wait uses actual arrival;
- route position uses actual completion order;
- route totals include actual service/travel outcomes;
- cumulative context includes previous actual outcomes;
- road/traffic feature bypasses Phase 03-approved join logic;
- missing road/traffic is silently replaced with normal/free-flow values without an approved policy;
- any ratio contains infinity;
- historical statistic sees its own target;
- historical statistic sees same-date targets;
- historical statistic sees future targets;
- validation/test targets are used to fit a historical feature;
- feature registry is incomplete;
- enabled feature has unknown lineage;
- train/test feature definitions differ;
- actual journey field or target-derived column appears in final X;
- leakage audit fails;
- synthetic/regression tests fail;
- local feature build fails;
- private feature matrices/reports are tracked by Git;
- competition data is exposed in violation of the competition rules;
- independent review fails.

---

# 16. Definition of Done

Phase 06 passes only when:

- [ ] DT-091 PASS
- [ ] DT-092 PASS
- [ ] DT-093 PASS
- [ ] DT-094 PASS
- [ ] DT-095 PASS
- [ ] DT-096 PASS
- [ ] DT-097 PASS
- [ ] DT-098 PASS
- [ ] DT-099 PASS
- [ ] DT-100 PASS
- [ ] DT-101 PASS
- [ ] DT-102 PASS
- [ ] DT-103 PASS
- [ ] DT-104 PASS
- [ ] DT-105 PASS
- [ ] DT-106 PASS
- [ ] DT-107 PASS
- [ ] DT-108 PASS
- [ ] DT-109 PASS
- [ ] DT-110 PASS or explicitly DISABLED according to approved coverage policy
- [ ] DT-111 PASS or explicitly DISABLED according to approved coverage policy
- [ ] DT-112 PASS
- [ ] DT-113 PASS
- [ ] DT-114 PASS
- [ ] DT-115 PASS
- [ ] DT-116 PASS
- [ ] DT-117 PASS
- [ ] DT-118 PASS
- [ ] DT-119 PASS
- [ ] DT-120 PASS
- [ ] DT-121 PASS
- [ ] DT-122 PASS
- [ ] train/test feature definitions are identical
- [ ] deterministic feature order is frozen
- [ ] every feature is registered
- [ ] every feature has source lineage
- [ ] every enabled feature is prediction-time safe
- [ ] historical target features are fold-safe and chronology-safe
- [ ] no same-day target leakage
- [ ] no actual journey field in model matrix
- [ ] no target/target-derived field in model matrix
- [ ] no infinite numeric features
- [ ] optional context handling is explicit
- [ ] synthetic tests pass
- [ ] full regression suite passes
- [ ] local feature build passes
- [ ] private outputs remain ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 06 STATUS: PASS
READY FOR PHASE 07: YES
```

Do not automatically begin Phase 07.

---

# 17. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-06-task1-features
```

Recommended commits:

```text
feat(task1): add base and static reference features
feat(task1): add route and planned-time features
feat(task1): add calendar and environment features
feat(task1): add ratio and route aggregate features
feat(task1): add leakage-safe historical feature transformer
feat(task1): add feature registry and lineage metadata
test(task1): add Task 1 feature and leakage tests
docs(task1): document Task 1 feature engineering
```

The agent may autonomously create these commits if that matches the team's Git workflow, but must not stage private competition artifacts.

Before each commit:

```bash
git status
git diff --cached --name-only
```

Never stage:

```text
data/raw/**
data/interim/**
data/processed/**
reports/private/**
*.csv containing competition records
```

Before merge:

```bash
python -m pip check
pytest -q

git status
```

Merge only after:

```text
LOCAL PHASE 06 FEATURE BUILD: PASS
INDEPENDENT PHASE 06 REVIEW: PASS
```

---

# 18. Enhanced Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 06 only.

PHASE:
Task 1 Feature Engineering

TASK RANGE:
DT-091 through DT-122

EXECUTION MODE:
Controlled autonomous implementation.

You MAY:
- edit all relevant project code/config/tests/docs
- run pytest
- run pip check
- inspect stack traces
- debug failing safe tests
- create synthetic fixtures
- rerun tests until they pass
- inspect Git status/diff
- refactor Phase 06 code when necessary
- self-review against the Phase 06 Definition of Done

You MUST stop on a genuine competition-rule, leakage, cross-phase-contract, or private-data boundary issue.

Do NOT start Phase 07.

READ FIRST:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved Phase 00–05 contracts
3. PHASE_06_COMPETITION_CONTRACT.md
4. tracked Phase 03 schema/coverage code
5. tracked Phase 04 label builder
6. tracked Phase 05 EDA methodology/candidate registry if present

SOURCE PRIORITY:
Official organizer material
>
approved master plan
>
approved phase contracts
>
implementation assumptions

==================================================
DATA / COMPETITION SAFETY
==================================================

Do not open or inspect official row-level competition data inside the external-agent context.

Do not access private row-level outputs under:

data/raw/**
data/interim/**
reports/private/**

unless the project has an organizer-approved local execution mechanism that provably does not transmit the data to the model/provider.

Use synthetic fixtures for agent-run tests.

You may implement and fully test the code path without real rows.

==================================================
OFFICIAL TASK 1 PREDICTION-TIME BOUNDARY
==================================================

Planned information is available at prediction time.
Actual journey and handling outcomes are training-only.

FORBIDDEN direct model features:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

A renamed or derived feature that depends on these is also forbidden, except explicitly chronology-safe/fold-safe historical target aggregates implemented only under DT-119.

==================================================
CREATE / UPDATE
==================================================

src/task1/features.py
src/task1/feature_registry.py
src/task1/historical_features.py
scripts/build_task1_features.py
configs/task1_features.yaml
docs/task1_feature_spec.md
tests/test_task1_features.py
tests/test_task1_historical_features.py
tests/test_task1_feature_leakage.py

Keep private outputs ignored:

data/interim/task1_features_train.csv
data/interim/task1_features_test.csv
reports/private/phase06_task1_features/**

==================================================
BATCH A — DT-091 THROUGH DT-095
==================================================

Implement:

DT-091 base order features
DT-092 outlet reference features
DT-093 dock/access features
DT-094 geography/depot reference features
DT-095 vehicle reference features

Requirements:
- one row per delivery_id
- preserve delivery_id as traceability
- keep model allow-list separate from metadata IDs
- use official outlet/vehicle/reference joins
- validate duplicated/copied fields rather than silently overwrite
- no target or actual journey columns in candidate model matrix
- no external geographic enrichment

Run targeted synthetic tests.
Fix ordinary coding/test failures autonomously.

==================================================
BATCH B — DT-096 THROUGH DT-104
==================================================

Implement:

DT-096 seq_in_route
DT-097 route_stop_count
DT-098 route_seq_fraction
DT-099 is_first_stop
DT-100 planned time features
DT-101 planned slack to close
DT-102 planned early wait
DT-103 leg distance
DT-104 planned travel duration

Definitions:

route_seq_fraction =
seq_in_route / (route_stop_count - 1)

For a one-stop route:
route_seq_fraction = 0

is_first_stop = int(seq_in_route == 0)

planned_slack_to_close_min =
resolved_window_close_dt - resolved_planned_arrival_dt

planned_early_wait_min =
max(0, resolved_window_open_dt - resolved_planned_arrival_dt)

Use planned values only.
Never use actual arrival.

For planned time, support minute-of-day and optional cyclical sin/cos encoding.
Handle midnight safely using planned information.

Run route/time/slack/leakage tests.

==================================================
BATCH C — DT-105 THROUGH DT-112
==================================================

Implement:

DT-105 calendar join
DT-106 payday
DT-107 festival
DT-108 festival_ramp
DT-109 monsoon
DT-110 road conditions if Phase 03 approved
DT-111 traffic speed if Phase 03 approved
DT-112 service_allowance_min

Calendar join must preserve official:

dow
is_weekend
iso_year
iso_week
is_payday
festival
festival_ramp
is_holiday
monsoon
is_operating

Use one canonical monsoon source and verify duplicate source consistency where relevant.

Road:
- use Phase 03-approved join only
- no invented key
- missing != clear
- support clean disabled state

Traffic:
- use Phase 03-approved join only
- use planned timing/context
- never use actual_travel_duration_min
- missing != free flow
- support disabled state

Service allowance official join:
brand + dock_type

Run all Batch C tests.

==================================================
BATCH D — DT-113 THROUGH DT-118
==================================================

Implement:

DT-113 weight_per_unit_kg
DT-114 volume_per_unit_m3
DT-115 cargo_density_kg_per_m3
DT-116 planned route totals
DT-117 planned vehicle utilization
DT-118 cumulative prior planned route context

Division guards:
no infinity.

Route totals may include only planned/static values.

Recommended totals:
route_total_units
route_total_weight_kg
route_total_volume_m3
route_total_distance_km
route_total_planned_travel_min
route_total_service_allowance_min
route_stop_count

Utilization:
route_weight_utilization
route_volume_utilization
route_max_utilization

Do not clip utilization > 1.

Cumulative prior planned context:
prior_stop_count
prior_planned_units
prior_planned_weight_kg
prior_planned_volume_m3
prior_leg_distance_km
prior_planned_travel_min
prior_service_allowance_min

These MUST use planned/static quantities only.
Never previous actual service, actual travel, actual arrival, or late labels.

Run ratio/aggregate/cumulative tests.

==================================================
CRITICAL GATE — DT-119
==================================================

Implement leakage-safe historical target statistics separately.

Start with a small transparent set such as:

outlet_prior_service_median
outlet_prior_late_rate
brand_dock_prior_service_median
brand_dock_prior_late_rate
brand_prior_service_median
brand_prior_late_rate

CRITICAL TRAINING RULE:
For a training row on date D, historical target stats may use only records with date < D.

Same-date labels MUST NOT influence each other.
Current row MUST NOT influence itself.
Future rows MUST NOT influence earlier rows.

VALIDATION-READY RULE:
The transformer must support fitting on a training fold and transforming validation without reading validation targets.

FINAL TEST RULE:
Fit on historical training only, transform Task 1 test without test labels.

Implement documented fallback, for example:

outlet
→ brand+dock
→ brand
→ global training prior

All fallback statistics must obey the same fit scope.

Required tests:
- current target excluded
- same date excluded
- future target excluded
- validation target not read
- unseen outlet fallback
- deterministic under input shuffle

If ANY historical leakage test fails:
STOP PHASE 06.
Do not work around it.

==================================================
DT-120 — FEATURE REGISTRY
==================================================

Create complete metadata for every produced feature:

feature_name
feature_group
source_table
source_columns
formula_or_mapping
semantic_type
prediction_time_safe
uses_target_history
requires_fit
fit_scope
missing_value_policy
train_available
test_available
categorical
model_candidate
rationale
status

Status values:
ENABLED
OPTIONAL
DISABLED
HISTORICAL_FOLD_SAFE_ONLY

Every final model feature must have exactly one registry entry.

==================================================
CRITICAL GATE — DT-121
==================================================

Implement automated leakage audit.

Layer 1:
forbidden-name deny-list.

Layer 2:
source-lineage audit.

Layer 3:
train/test feature availability/parity.

Layer 4:
historical target feature fit-scope audit.

Layer 5:
target separation.

Layer 6:
deterministic feature column order.

Reject renamed leakage based on source lineage, not only column name.

Run dedicated leakage tests.

If an enabled feature fails:
STOP.

==================================================
FINAL GATE — DT-122
==================================================

The final model matrix must contain ZERO direct actual journey or target-derived fields.

Assert absent:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

Prefer an explicit feature allow-list built from the registry.
Also run the deny-list as defense in depth.

Assert train/test feature columns match exactly in name and order.

==================================================
AUTONOMOUS SAFE TESTING / DEBUGGING
==================================================

You have permission to:

1. run targeted synthetic tests after every batch;
2. inspect failures and stack traces;
3. fix ordinary implementation bugs;
4. rerun the failing test;
5. rerun the batch test set;
6. after all batches, run the complete regression suite;
7. run python -m pip check;
8. inspect git status/diff for accidental private artifacts;
9. self-review against the Phase 06 Definition of Done.

Do not stop for ordinary coding failures you can safely fix.

STOP only for:
- competition-rule ambiguity
- raw/private data requirement
- cross-phase contract conflict
- leakage that cannot be resolved without changing the approved design
- a genuine schema/data blocker
- a required feature impossible to build from prediction-time information

Run safe suite including at minimum:

tests/test_project_setup.py
tests/test_data_inventory.py
tests/test_data_quality.py
tests/test_schema_assertions.py
tests/test_task1_labels.py
tests/test_task1_eda.py
tests/test_task1_features.py
tests/test_task1_historical_features.py
tests/test_task1_feature_leakage.py

Then:

python -m pip check

==================================================
LOCAL REAL-DATA CLI CONTRACT
==================================================

Implement:

python scripts/build_task1_features.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --labels data/interim/task1_training_labels.csv \
  --config configs/task1_features.yaml \
  --train-output data/interim/task1_features_train.csv \
  --test-output data/interim/task1_features_test.csv \
  --report-dir reports/private/phase06_task1_features

Do not run this against private competition data in the external-agent context.
The human/local execution step will do that.

==================================================
FINAL SELF-REVIEW
==================================================

Before returning, verify:
- all DT-091..DT-122 implemented
- every feature registered
- every feature has lineage
- no actual journey feature enabled
- no target-derived feature enabled
- no same-day historical leakage
- train/test parity test passes
- ratios contain no infinities
- optional road/traffic handling is explicit
- test suite passes
- pip check passes
- private paths are not staged

==================================================
RETURN ONLY
==================================================

PHASE:
06 — AGENT IMPLEMENTATION STAGE

TASK STATUS:
DT-091 READY/FAIL
DT-092 READY/FAIL
DT-093 READY/FAIL
DT-094 READY/FAIL
DT-095 READY/FAIL
DT-096 READY/FAIL
DT-097 READY/FAIL
DT-098 READY/FAIL
DT-099 READY/FAIL
DT-100 READY/FAIL
DT-101 READY/FAIL
DT-102 READY/FAIL
DT-103 READY/FAIL
DT-104 READY/FAIL
DT-105 READY/FAIL
DT-106 READY/FAIL
DT-107 READY/FAIL
DT-108 READY/FAIL
DT-109 READY/FAIL
DT-110 READY/FAIL/DISABLED
DT-111 READY/FAIL/DISABLED
DT-112 READY/FAIL
DT-113 READY/FAIL
DT-114 READY/FAIL
DT-115 READY/FAIL
DT-116 READY/FAIL
DT-117 READY/FAIL
DT-118 READY/FAIL
DT-119 READY/FAIL
DT-120 READY/FAIL
DT-121 READY/FAIL
DT-122 READY/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

HISTORICAL FEATURE SAFETY:
PASS / FAIL

TRAIN/TEST PARITY:
PASS / FAIL

LEAKAGE AUDIT:
PASS / FAIL

FORBIDDEN FIELDS IN FINAL X:
0 / nonzero

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local feature-build command.

PHASE 06 STATUS:
AWAITING LOCAL FEATURE BUILD

READY FOR PHASE 07:
NO

Then STOP.
Do not begin Phase 07.
```

---

# 19. Enhanced independent review prompt

Use a fresh Cursor chat after the local feature build.

```text
Perform an independent review of completed WayLoom Datathon Phase 06.

DO NOT:
- open data/raw
- open data/interim
- open reports/private
- inspect real feature rows/labels
- execute the real feature builder
- modify code initially
- start Phase 07

READ:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_06_COMPETITION_CONTRACT.md
3. src/task1/features.py
4. src/task1/feature_registry.py
5. src/task1/historical_features.py
6. scripts/build_task1_features.py
7. configs/task1_features.yaml
8. docs/task1_feature_spec.md
9. tests/test_task1_features.py
10. tests/test_task1_historical_features.py
11. tests/test_task1_feature_leakage.py
12. tracked Phase 03–05 Task 1 code relevant to joins/labels/EDA
13. .gitignore
14. .cursorignore

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 06 FEATURE BUILD: <PASS / FAIL>
TRAIN FEATURE MATRIX: <PASS / FAIL>
TEST FEATURE MATRIX: <PASS / FAIL>
TRAIN/TEST PARITY: <PASS / FAIL>
HISTORICAL FEATURE SAFETY: <PASS / FAIL>
LEAKAGE AUDIT: <PASS / FAIL>
FORBIDDEN DIRECT FIELDS IN X: <0 / number>
OPTIONAL ROAD FEATURES: <ENABLED / DISABLED>
OPTIONAL TRAFFIC FEATURES: <ENABLED / DISABLED>

Do not request private reports.

AUDIT EVERY TASK DT-091 THROUGH DT-122 against the Phase 06 contract.

Pay special attention to:

1. Base grain remains one delivery_id per row.
2. Outlet/vehicle/reference joins cannot multiply rows.
3. Route stop count is planned, not actual.
4. Sequence fraction handles one-stop routes.
5. Planned time features never read actual clocks.
6. Planned slack uses planned arrival and window close only.
7. Planned early wait uses planned arrival and window open only.
8. Road/traffic joins exactly reuse Phase 03-approved logic.
9. Missing road/traffic is not silently normalized.
10. Service allowance is reference data, not target data.
11. Ratio features cannot produce inf.
12. Route totals contain planned/static inputs only.
13. Cumulative prior context contains planned/static inputs only.
14. DT-119 historical target stats use strict earlier-date history for row-wise training features.
15. Same-day targets do not influence each other.
16. Validation-ready fit/transform separation exists.
17. Feature registry covers every final feature.
18. Lineage metadata is complete.
19. Leakage audit rejects direct and derived leakage.
20. Final X contains none of:
    actual_depart_time
    actual_travel_duration_min
    arrival_time
    leave_outlet_time
    service_start_dt
    service_minutes
    late_flag
21. Train/test feature columns match exactly in name/order.

RUN SAFE TESTS ONLY:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py tests/test_task1_eda.py tests/test_task1_features.py tests/test_task1_historical_features.py tests/test_task1_feature_leakage.py

python -m pip check

git status

Do not run real-data feature construction.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

BASE/REFERENCE FEATURES:
PASS / FAIL

ROUTE/TIME FEATURES:
PASS / FAIL

CALENDAR/ENVIRONMENT:
PASS / FAIL

ROUTE AGGREGATES:
PASS / FAIL

HISTORICAL FEATURE SAFETY:
PASS / FAIL

FEATURE REGISTRY:
PASS / FAIL

LEAKAGE AUDIT:
PASS / FAIL

TRAIN/TEST PARITY:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL BUILD:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-091: PASS/FAIL
DT-092: PASS/FAIL
DT-093: PASS/FAIL
DT-094: PASS/FAIL
DT-095: PASS/FAIL
DT-096: PASS/FAIL
DT-097: PASS/FAIL
DT-098: PASS/FAIL
DT-099: PASS/FAIL
DT-100: PASS/FAIL
DT-101: PASS/FAIL
DT-102: PASS/FAIL
DT-103: PASS/FAIL
DT-104: PASS/FAIL
DT-105: PASS/FAIL
DT-106: PASS/FAIL
DT-107: PASS/FAIL
DT-108: PASS/FAIL
DT-109: PASS/FAIL
DT-110: PASS/FAIL/DISABLED
DT-111: PASS/FAIL/DISABLED
DT-112: PASS/FAIL
DT-113: PASS/FAIL
DT-114: PASS/FAIL
DT-115: PASS/FAIL
DT-116: PASS/FAIL
DT-117: PASS/FAIL
DT-118: PASS/FAIL
DT-119: PASS/FAIL
DT-120: PASS/FAIL
DT-121: PASS/FAIL
DT-122: PASS/FAIL

PHASE 06 REVIEW:
PASS / FAIL

READY FOR PHASE 07:
YES / NO

If FAIL, list exact blockers only.
Do not fix automatically.
Do not begin Phase 07.
```

---

# 20. Local execution instructions

After the agent implementation passes all safe tests:

### 20.1 Check ignore rules

```bash
git status
git check-ignore -v data/interim/task1_features_train.csv
git check-ignore -v reports/private/phase06_task1_features/leakage_audit.json
```

### 20.2 Run full local tests

```bash
pytest -q
python -m pip check
```

### 20.3 Run the real local feature build

```bash
python scripts/build_task1_features.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --labels data/interim/task1_training_labels.csv \
  --config configs/task1_features.yaml \
  --train-output data/interim/task1_features_train.csv \
  --test-output data/interim/task1_features_test.csv \
  --report-dir reports/private/phase06_task1_features
```

PowerShell one-line form:

```powershell
python scripts/build_task1_features.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --labels data/interim/task1_training_labels.csv --config configs/task1_features.yaml --train-output data/interim/task1_features_train.csv --test-output data/interim/task1_features_test.csv --report-dir reports/private/phase06_task1_features
```

### 20.4 Inspect private reports locally

Confirm:

```text
train build PASS
test build PASS
one row per delivery_id
train/test columns equal
historical feature audit PASS
same-date leakage = 0
future leakage = 0
leakage audit PASS
forbidden fields in X = 0
inf values = 0
private outputs ignored by Git
```

### 20.5 Return only sanitized control status

```text
LOCAL PHASE 06 FEATURE BUILD: PASS
TRAIN FEATURE MATRIX: PASS
TEST FEATURE MATRIX: PASS
TRAIN/TEST PARITY: PASS
HISTORICAL FEATURE SAFETY: PASS
LEAKAGE AUDIT: PASS
FORBIDDEN DIRECT FIELDS IN X: 0
OPTIONAL ROAD FEATURES: ENABLED/DISABLED
OPTIONAL TRAFFIC FEATURES: ENABLED/DISABLED
```

Then run the independent review prompt.

---

# 21. Completion record template

```markdown
# Phase 06 Completion Record

## Tasks
- [ ] DT-091
- [ ] DT-092
- [ ] DT-093
- [ ] DT-094
- [ ] DT-095
- [ ] DT-096
- [ ] DT-097
- [ ] DT-098
- [ ] DT-099
- [ ] DT-100
- [ ] DT-101
- [ ] DT-102
- [ ] DT-103
- [ ] DT-104
- [ ] DT-105
- [ ] DT-106
- [ ] DT-107
- [ ] DT-108
- [ ] DT-109
- [ ] DT-110
- [ ] DT-111
- [ ] DT-112
- [ ] DT-113
- [ ] DT-114
- [ ] DT-115
- [ ] DT-116
- [ ] DT-117
- [ ] DT-118
- [ ] DT-119
- [ ] DT-120
- [ ] DT-121
- [ ] DT-122

## Engineering checks
- Synthetic feature tests: PASS / FAIL
- Historical feature tests: PASS / FAIL
- Leakage tests: PASS / FAIL
- Full regression suite: PASS / FAIL
- pip check: PASS / FAIL

## Local feature build
- Train matrix: PASS / FAIL
- Test matrix: PASS / FAIL
- Train/test parity: PASS / FAIL
- Historical feature safety: PASS / FAIL
- Same-date leakage: 0 / nonzero
- Future leakage: 0 / nonzero
- Forbidden fields in X: 0 / nonzero
- Infinite numeric values: 0 / nonzero
- Road context: ENABLED / DISABLED
- Traffic context: ENABLED / DISABLED

## Safety
- Raw/private rows exposed to external agent: NO
- Private features committed: NO
- Actual journey field enabled: NO
- Target-derived feature enabled: NO

## Review
- Independent review: PASS / FAIL

## Verdict
PHASE 06 STATUS: PASS / FAIL
READY FOR PHASE 07: YES / NO
```

---

# 22. Final checklist

Before Phase 07:

- [ ] Phase 05 passed.
- [ ] all 32 tasks implemented.
- [ ] base grain remains one `delivery_id` per row.
- [ ] outlet/static access joins safe.
- [ ] vehicle joins safe.
- [ ] route position/stop count/sequence fraction correct.
- [ ] planned time features safe.
- [ ] planned slack safe.
- [ ] planned early wait safe.
- [ ] planned distance/travel features safe.
- [ ] calendar features joined correctly.
- [ ] payday/festival/ramp/monsoon documented.
- [ ] road handling enabled or explicitly disabled.
- [ ] traffic handling enabled or explicitly disabled.
- [ ] service allowance joined correctly.
- [ ] ratio features never produce infinity.
- [ ] route totals use planned/static values only.
- [ ] utilization uses static capacities.
- [ ] cumulative context uses planned/static values only.
- [ ] historical target features use strict prior dates/fold-safe fit.
- [ ] same-date historical leakage prevented.
- [ ] feature registry complete.
- [ ] source lineage complete.
- [ ] automated leakage audit passes.
- [ ] final X contains zero actual journey columns.
- [ ] final X contains zero target/target-derived columns.
- [ ] train/test feature columns match exactly.
- [ ] all tests pass.
- [ ] local feature build passes.
- [ ] private outputs remain ignored.
- [ ] independent review passes.
- [ ] no unresolved STOP condition.

Only then:

```text
PHASE 06 STATUS: PASS
READY FOR PHASE 07: YES
```

Do not automatically begin Phase 07.
