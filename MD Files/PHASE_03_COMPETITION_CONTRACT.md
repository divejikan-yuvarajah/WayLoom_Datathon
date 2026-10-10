# PHASE 03 — Data-Quality Audit

> **Requested filename:** `PHASE_03_COMPETITION_CONTRACT.md`  
> **Canonical phase name:** **Phase 03 — Data-Quality Audit**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-036 → DT-054**  
> **Task count:** 19  
> **Default priority:** P0  
> **Phase dependency:** Phase 02 must have passed  
> **Recommended execution style:** **Hybrid — audit tooling in batches; critical integrity checks individually reviewed; real-data execution locally outside the AI-agent context**  
> **Phase gate:** Core integrity assertions pass, or every non-blocking exception is explicitly documented before Task 1 label/model work begins.

---

# 1. Purpose of Phase 03

Phase 03 verifies that the supplied competition datasets are structurally trustworthy enough to support later label construction, feature engineering, forecasting, optimization, and submission generation.

This phase must answer:

- Are required fields unexpectedly missing?
- Are there full duplicate records?
- Are official/candidate keys duplicated?
- Can numerical/date/time fields be parsed correctly?
- Do official categorical fields contain valid values?
- Are numerical values impossible, suspicious, or merely extreme?
- Are order IDs unique?
- Are route-leg identifiers and route-position keys safe to use?
- Do outlet and vehicle references agree across tables?
- Does the calendar cover the dates/weeks needed later?
- Can road-condition and traffic reference data be joined for the relevant periods?
- Do train/test datasets contain compatible categories?
- Can these expectations be converted into automated assertions?
- Is there a reproducible audit report that records all exceptions without modifying the raw competition files?

Phase 03 is an **audit phase**, not a cleaning phase.

**Never modify the raw official CSV files to make a check pass.**

If an issue requires later cleaning, exclusion, fallback logic, or feature handling:

1. preserve the raw fact;
2. record the issue;
3. classify its severity;
4. define the later treatment;
5. implement that treatment in the appropriate downstream phase.

---

# 2. Source and authority hierarchy

Use this order:

1. **Official Rootcode Tech-Triathlon 2026 Challenge Booklet**
2. **Official competition files/templates/checker**
3. **Approved `WAYLOOM_DATATHON_MASTER_PLAN.md`**
4. **Approved Phase 00–02 contracts**
5. **This Phase 03 implementation guide**
6. Implementation assumptions

If a check conflicts with the official booklet, the official booklet wins.

Do not convert an engineering expectation into an organizer requirement.

---

# 3. Official dataset facts that Phase 03 must preserve

The official booklet establishes the following facts relevant to this audit.

## 3.1 General time conventions

- clock times use `HH:MM`;
- timezone/context is **Asia/Colombo**;
- columns ending in `_time` contain clock times;
- duration fields ending in `_duration_min` are measured in minutes.

## 3.2 Order records

`deliveries_train.csv` and `task1_test_inputs.csv` contain one row per order.

Officially documented order semantics include:

```text
delivery_id        unique order identifier / Task 1 prediction key
order_date         requested order date
dispatch_date      dispatch date; blank if it never ran
dispatch_status    attempted | deferred | not_run
outlet_id
brand
district
depot
temp_requirement   chilled | ambient
order_units
order_weight_kg
order_volume_m3
route_id           blank if it never ran
seq_in_route       route position, starting at 0
vehicle_id
vehicle_type
vehicle_temp
planned_arrival_time
window_open_time
window_close_time
```

`task1_test_inputs.csv` contains later Task 1 plans and all are dispatched.

## 3.3 Route-leg records

`route_legs_train.csv` and `route_legs_test.csv` contain one row per route leg.

Official route fields include:

```text
leg_id
date
route_id
seq
depot
vehicle_id
vehicle_type
vehicle_temp
brand
district
from_point
to_outlet
distance_km
planned_depart_time
planned_travel_duration_min
planned_arrival_time
monsoon
dow
```

Training route records additionally contain actual fields:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

Each dispatched training order should correspond to exactly one route leg through:

```text
deliveries_train.(route_id, seq_in_route)
↔
route_legs_train.(route_id, seq)
```

The exact Task 1 one-to-one join proof belongs to Phase 04, but Phase 03 must ensure the underlying keys are structurally capable of supporting it.

## 3.4 Outlet reference

Official outlet rules include:

```text
outlet_id              OUT001 through OUT120
brand                  Fresh | Style | Tech
district               one of 12 districts
depot                  Peliyagoda | Kandy
dock_type              rear_dock | street | mall_bay
parking_constraint     normal | van_only | mall_dock
mall_window             HH:MM-HH:MM; blank outside malls
window_open_time        HH:MM
window_close_time       HH:MM
```

The competition describes **120 outlets**.

## 3.5 Vehicle reference

Official vehicle rules include:

```text
vehicle_id              VEH001 through VEH060
type                    truck | van
temp                    reefer | ambient
weight_cap_kg
volume_cap_m3
fuel_type
km_per_l
weekly_fuel_quota_l
depot                   home depot
```

The competition describes **60 vehicles**.

## 3.6 Calendar

Official calendar semantics include:

```text
date
dow                     0..6, Monday = 0
dow_name
is_weekend              0 | 1
iso_year
iso_week
is_payday               0 | 1
festival
festival_ramp           0..1
is_holiday              0 | 1
monsoon                 0 | 1
is_operating            0 | 1
```

`calendar.csv` is the official calendar source for history and forecast periods.

## 3.7 Travel / allowance / environment tables

Officially documented fields include:

### `district_travel.csv`

```text
district
depot
road_class              urban | suburban | highway | hill
free_flow_kmh
depot_to_district_km
depot_to_district_freeflow_min
inter_stop_km
inter_stop_freeflow_min
```

### `service_allowance.csv`

```text
brand
dock_type
service_allowance_min
```

one row per brand + dock type.

### `traffic_speed.csv`

Documented key fields include:

```text
monsoon                  0 | 1
speed_index              100 = free flow; lower = slower
```

The full local schema identified in Phase 02 must determine the actual join key. Do not invent one.

### `road_conditions.csv`

Documented key field includes:

```text
disruption_index         100 = clear; lower = disrupted
```

It represents date-specific district disruption. The full local schema from Phase 02 determines the actual join key.

## 3.8 Task 2B scenario fields relevant to validation

The official scenario uses:

```text
scenario                 always S1
order_ref                unique order identifier within scenario; allocation key
outlet_id
brand
district
depot
dock_type
parking_constraint
mall_window
window_open_time
window_close_time
temp_requirement
order_units
order_weight_kg
order_volume_m3
deferred_yesterday       0 | 1
days_since_last_served
```

Fleet status:

```text
scenario                 S1
vehicle_id
status                   available | in_workshop
```

Do **not** use `outlet_id` as the Task 2B allocation key.

---

# 4. Data-safety execution model

Phase 03 requires examining the official data for quality, but competition data and derivatives must not be shared or transmitted to third-party tools.

Use the same safety model as Phase 02.

## AI-agent stage

Cursor/Codex may:

- read this specification;
- read tracked code/config/docs;
- implement audit functions;
- implement schema assertions;
- write synthetic tests;
- review code;
- review a **sanitized PASS/FAIL completion status**.

Cursor/Codex must not:

- open `data/raw/**`;
- inspect real CSV rows;
- inspect `reports/private/**`;
- inspect lists of private row IDs;
- inspect private category-value reports;
- execute the real audit against the competition dataset.

## Local operator stage

The human runs the completed audit from a normal local terminal.

Detailed findings are written under:

```text
reports/private/phase03_data_quality/
```

and remain local/ignored.

When returning to Cursor/Codex, share only high-level control statuses, for example:

```text
LOCAL PHASE 03 AUDIT: PASS
BLOCKING ASSERTIONS: 0
DOCUMENTED WARNINGS: YES
```

or:

```text
LOCAL PHASE 03 AUDIT: FAIL
BLOCKER CODE: DUPLICATE_PRIMARY_KEY
AFFECTED TABLE: <official filename only>
```

Do not paste private row values or private audit files.

---

# 5. Phase 03 severity model

Every audit rule must return one of:

```text
PASS
EXPECTED
WARNING
BLOCKER
NOT_APPLICABLE
```

## PASS

Rule satisfied.

## EXPECTED

The condition is explicitly valid under official semantics.

Example:

```text
dispatch_date is blank for dispatch_status = not_run
```

## WARNING

Data may be valid but needs downstream treatment or investigation.

Examples:

- statistically extreme but non-impossible order volume;
- unseen test category that has a valid reference-table record;
- partial road-condition coverage where the feature can be omitted/fallback-treated later.

## BLOCKER

A core structural fact needed later is invalid.

Examples:

- duplicate `delivery_id` where it must be unique;
- duplicate `leg_id`;
- missing official required identifier;
- invalid Task 1 route key structure;
- unknown `outlet_id` in an order;
- unknown `vehicle_id` in a dispatched order;
- invalid official enum value;
- malformed nonblank clock time;
- calendar does not cover a date required for downstream grouping;
- an official required file/schema assertion fails.

**Rule:** Phase 03 can pass with documented `WARNING` results, but not with unresolved `BLOCKER` results.

---

# 6. Phase 03 task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---|---|---|---|
| [ ] | **DT-036** | [E] | P0 | Phase 02 | Check missing values |
| [ ] | **DT-037** | [E] | P0 | Phase 02 | Check complete duplicate rows |
| [ ] | **DT-038** | [E] | P0 | Phase 02 | Check duplicate primary keys |
| [ ] | **DT-039** | [E] | P0 | Phase 02 | Validate data types |
| [ ] | **DT-040** | [E] | P0 | Phase 02 | Validate date formats |
| [ ] | **DT-041** | [E] | P0 | Phase 02 | Validate time formats |
| [ ] | **DT-042** | [E] | P0 | Phase 02 | Validate categorical values |
| [ ] | **DT-043** | [E] | P0 | Phase 02 | Check negative or impossible numeric values |
| [ ] | **DT-044** | [E] | P0 | Phase 02 | Check extreme values and outliers |
| [ ] | **DT-045** | [E] | P0 | Phase 02 | Check order ID uniqueness |
| [ ] | **DT-046** | [E] | P0 | Phase 02 | Check route-leg key uniqueness |
| [ ] | **DT-047** | [E] | P0 | Phase 02 | Check outlet-reference consistency |
| [ ] | **DT-048** | [E] | P0 | Phase 02 | Check vehicle-reference consistency |
| [ ] | **DT-049** | [E] | P0 | Phase 02 | Check calendar coverage |
| [ ] | **DT-050** | [E] | P0 | Phase 02 | Check road-condition coverage |
| [ ] | **DT-051** | [E] | P0 | Phase 02 | Check traffic-speed coverage |
| [ ] | **DT-052** | [E] | P0 | Phase 02 | Check train/test category compatibility |
| [ ] | **DT-053** | [E] | P0 | Phase 02 | Create automated schema assertions |
| [ ] | **DT-054** | [E] | P0 | Phase 02 | Produce dataset-audit report |

**Phase complete:** [ ]  
**READY FOR PHASE 04:** NO

---

# 7. Required repository additions

Recommended tracked files:

```text
configs/
└── data_quality_rules.yaml

src/common/
├── data_quality.py
└── schema_assertions.py

scripts/
└── run_data_quality_audit.py

docs/
└── data_quality_rules.md

tests/
├── test_data_quality.py
└── test_schema_assertions.py
```

Private local outputs:

```text
reports/private/phase03_data_quality/
├── audit_summary.json
├── missingness.json
├── duplicate_rows.json
├── key_integrity.json
├── type_validation.json
├── date_validation.json
├── time_validation.json
├── category_validation.json
├── numeric_validation.json
├── outlier_review.json
├── reference_integrity.json
├── coverage.json
├── train_test_compatibility.json
└── phase03_audit_report.md
```

`reports/private/**` must remain ignored by Git and excluded from Cursor indexing.

---

# 8. Audit configuration design

Create:

```text
configs/data_quality_rules.yaml
```

Do not store private observed values in this tracked file.

Recommended structure:

```yaml
version: 1

severity:
  hard_fail: BLOCKER
  warning: WARNING

official_counts:
  outlets: 120
  vehicles: 60

official_enums:
  brand: [Fresh, Style, Tech]
  dispatch_status: [attempted, deferred, not_run]
  temp_requirement: [chilled, ambient]
  outlet_depot: [Peliyagoda, Kandy]
  dock_type: [rear_dock, street, mall_bay]
  parking_constraint: [normal, van_only, mall_dock]
  vehicle_type: [truck, van]
  vehicle_temp: [reefer, ambient]
  road_class: [urban, suburban, highway, hill]
  task2b_scenario: [S1]
  task2b_vehicle_status: [available, in_workshop]

binary_columns:
  - monsoon
  - is_weekend
  - is_payday
  - is_holiday
  - is_operating
  - deferred_yesterday

bounded_numeric:
  festival_ramp:
    min: 0
    max: 1
  dow:
    min: 0
    max: 6

nonnegative_numeric_patterns:
  - "*_kg"
  - "*_m3"
  - "*_km"
  - "*_min"

strictly_positive_when_present:
  - weight_cap_kg
  - volume_cap_m3
  - km_per_l
  - weekly_fuel_quota_l
  - free_flow_kmh

private_report_dir:
  "reports/private/phase03_data_quality"
```

For fields whose official domains are not completely documented, use reference-integrity checks rather than inventing a whitelist.

---

# 9. Detailed task specifications

---

## DT-036 — Check missing values

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Identify missing values and distinguish:

- officially expected blanks;
- conditionally required fields;
- suspicious missing values;
- blocking missing identifiers/references.

### Inputs

Official CSVs loaded locally through the existing privacy-safe data layer.

### Outputs

Private:

```text
missingness.json
```

### Rules

Do **not** treat every blank as an error.

#### Expected/conditional order blanks

Official semantics explicitly allow:

```text
dispatch_date = blank
route_id      = blank
```

when an order never ran (`dispatch_status = not_run`).

Other assignment fields may also be unavailable for an order that never ran. The exact local rule should be expressed conditionally rather than globally forcing non-null values.

For:

```text
dispatch_status in {attempted, deferred}
```

fields needed to describe a dispatched order should normally be present:

```text
dispatch_date
route_id
seq_in_route
vehicle_id
vehicle_type
vehicle_temp
planned_arrival_time
```

If any are blank, classify as at least `WARNING`, and as `BLOCKER` if later official label/join logic cannot be performed.

#### Outlet reference

`mall_window` may be blank outside mall-constrained outlets.

A non-mall outlet should not be forced to have a mall window.

#### Calendar

`festival` may be blank when no festival applies.

#### Core identifiers

These should not be missing in tables where they are the row key:

```text
delivery_id
leg_id
row_id
outlet_id
vehicle_id
date
order_ref
scenario
```

### Implementation requirements

Build a rule engine that supports:

```text
required
conditionally_required
allowed_missing
```

Do not hardcode ad hoc `dropna()` calls.

### Tests

Synthetic tests:

- valid `not_run` row with expected blanks → EXPECTED;
- `attempted` row missing `route_id` → BLOCKER/WARNING according to configured rule;
- missing `delivery_id` → BLOCKER;
- blank non-mall `mall_window` → EXPECTED;
- blank `festival` → EXPECTED.

### Edge cases

- empty string vs whitespace;
- strings `"NA"`, `"N/A"`, `"null"` mistakenly parsed as text;
- Pandas `NaN` in numeric fields;
- nullable integers;
- BOM/header artifacts.

### Definition of Done

- [ ] missingness is rule-based;
- [ ] official expected blanks are not false errors;
- [ ] required identifiers are protected;
- [ ] no row is deleted;
- [ ] private report is generated locally.

### STOP conditions

Stop if required identifiers are missing or if missingness rules contradict official dispatch semantics.

---

## DT-037 — Check complete duplicate rows

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Detect exact duplicate rows without automatically deleting them.

### Implementation

For every CSV:

```python
duplicate_mask = df.duplicated(keep=False)
```

Record privately:

```text
duplicate_row_count
affected_row_positions_or_keys
```

Do not print rows.

### Severity

- exact duplicates in primary-keyed operational/reference tables: likely `BLOCKER`;
- duplicates in templates: investigate, but identifier uniqueness determines blocking status;
- exact duplicated reference rows: `BLOCKER` if they create ambiguous joins.

### Important rule

**Never call `drop_duplicates()` on raw data in Phase 03.**

Audit first. Cleaning decisions must be explicit and later reproducible.

### Tests

Synthetic:

- no duplicates;
- one duplicated row;
- same key but different values (not a complete duplicate — handled by DT-038);
- duplicate blank/header-only behavior.

### Definition of Done

- [ ] all CSVs checked;
- [ ] exact duplicates distinguished from duplicate keys;
- [ ] no automatic deletion occurs.

### STOP conditions

Stop if exact duplicates make a required official key ambiguous.

---

## DT-038 — Check duplicate primary keys

**Execution:** Batch A, followed by individual review for any failure  
**Mark:** [E]  
**Priority:** P0

### Objective

Verify that official row identifiers are unique where the booklet defines them as unique.

### Hard-key checks

At minimum:

```text
deliveries_train.csv          delivery_id
task1_test_inputs.csv         delivery_id
route_legs_train.csv          leg_id
route_legs_test.csv           leg_id
task2a_test_inputs.csv        row_id
outlets.csv                   outlet_id
vehicles.csv                  vehicle_id
calendar.csv                  date
service_allowance.csv         brand + dock_type
```

Task 2B:

```text
task2b_peak_day_scenarios.csv
scenario + order_ref
```

Task 2B fleet:

```text
scenario + vehicle_id
```

where that composite was confirmed in Phase 02.

Candidate keys from Phase 02 must be validated, not silently promoted.

### Important distinction

A table may have:

```text
unique row key
```

and separately:

```text
join key
```

For example, `leg_id` identifies a route-leg record, while `route_id + seq` is the join key required by Task 1.

DT-046 handles route-leg join-key uniqueness explicitly.

### Tests

Synthetic duplicate primary/composite keys.

### Definition of Done

- [ ] all official keys checked;
- [ ] candidate keys clearly marked;
- [ ] duplicates are blockers rather than silently deduplicated.

### STOP conditions

Any duplicate in an official unique identifier is a Phase 03 blocker until resolved/documented from an authoritative source.

---

## DT-039 — Validate data types

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Validate semantic parseability rather than trusting Pandas' automatically inferred dtype.

### Type families

Use:

```text
identifier/string
categorical/string
integer/count
numeric/continuous
binary
date
clock_time
time_range
duration_minutes
```

### Rules

Examples:

```text
order_units                    integer/count
order_weight_kg                numeric
order_volume_m3                numeric
seq_in_route                   integer/position where present
seq                            integer/position
distance_km                    numeric
planned_travel_duration_min    numeric duration
actual_travel_duration_min     numeric duration
monsoon                        binary
dow                            integer 0..6
festival_ramp                  numeric 0..1
```

IDs should be treated as strings even if they contain digits.

### Implementation

Use non-destructive parse checks:

```python
pd.to_numeric(..., errors="coerce")
```

or equivalent, comparing invalid parse count only for nonblank values.

Do not overwrite original columns.

### Tests

- numeric-as-string valid;
- invalid numeric token;
- nullable integer;
- ID with leading zeros;
- binary value 2 should not pass binary validation.

### Definition of Done

- [ ] every tracked field has semantic type validation;
- [ ] IDs remain strings;
- [ ] parse failures are recorded;
- [ ] raw columns are untouched.

### STOP conditions

Required modelling/constraint fields with nonblank unparseable values are blockers.

---

## DT-040 — Validate date formats

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Verify that all nonblank date fields represent valid calendar dates.

### Candidate date columns

```text
order_date
dispatch_date
date
calendar.date
```

plus any Phase 02 observed field classified as `date`.

### Rules

- parse nonblank values strictly enough to detect invalid dates;
- preserve raw values;
- do not assume date order from string comparison;
- `dispatch_date` blank for `not_run` is valid;
- date-sequence/business-logic checks belong to later tasks when relevant.

### Suggested check

Use a local parser and record:

```text
nonblank_count
invalid_date_count
```

privately.

Do not print invalid raw values to AI-observed output.

### Useful semantic warnings

For dispatched orders:

```text
dispatch_date < order_date
```

is suspicious and should be reported as a warning/blocker candidate, but do not silently "correct" it.

For:

```text
dispatch_status = attempted
```

official semantics say dispatched on `order_date`; a mismatch is a strong integrity warning and may be a blocker for demand/dispatch interpretation.

For:

```text
dispatch_status = deferred
```

`dispatch_date` should logically be later than the requested date; validate locally and document exceptions.

### Tests

- leap date;
- invalid month/day;
- blank allowed date;
- attempted same-day dispatch;
- deferred later dispatch;
- not_run blank dispatch.

### Definition of Done

- [ ] all date fields parse;
- [ ] dispatch-status/date semantics checked;
- [ ] no dates modified.

### STOP conditions

Invalid nonblank date values in required rows are blockers.

---

## DT-041 — Validate time formats

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Verify all nonblank clock times follow valid `HH:MM` semantics and all time ranges are valid.

### Clock-time fields

Examples:

```text
planned_arrival_time
window_open_time
window_close_time
planned_depart_time
actual_depart_time
arrival_time
leave_outlet_time
```

### Time-range field

```text
mall_window
```

when populated.

### Rules

Valid clock time:

```text
00:00 through 23:59
```

Valid mall window:

```text
HH:MM-HH:MM
```

Do not conclude that a row is invalid merely because:

```text
leave_outlet_time < arrival_time
```

as string/clock values.

A route may cross midnight. Chronological time reconstruction belongs to Phase 04.

### Tests

- `07:30` valid;
- `7:30` invalid if strict `HH:MM` is required;
- `24:00` invalid;
- `23:59` valid;
- `08:00-10:30` valid range;
- blank non-mall mall window expected;
- crossing-midnight clock sequence must not be rejected by naive comparison.

### Definition of Done

- [ ] clock-time formatting validated;
- [ ] mall-window formatting validated;
- [ ] no midnight assumptions introduced.

### STOP conditions

Malformed nonblank official time fields are blockers for rows required by later tasks.

---

## DT-042 — Validate categorical values

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Validate official enumerations and reference-backed categories without inventing domains for undocumented fields.

### Official enum checks

At minimum:

```text
brand:
Fresh | Style | Tech

dispatch_status:
attempted | deferred | not_run

temp_requirement:
chilled | ambient

depot:
Peliyagoda | Kandy

dock_type:
rear_dock | street | mall_bay

parking_constraint:
normal | van_only | mall_dock

vehicle type:
truck | van

vehicle temperature:
reefer | ambient

road_class:
urban | suburban | highway | hill

Task 2B scenario:
S1

Task 2B fleet status:
available | in_workshop
```

Binary values:

```text
0 | 1
```

for official binary fields.

### For undocumented categories

Use reference-table consistency or train/test compatibility.

Do not invent a whitelist based on a few observed values.

### Tests

- exact official category;
- unknown category;
- casing typo;
- whitespace around category;
- numeric category accidentally loaded as string.

### Definition of Done

- [ ] official enums enforced;
- [ ] unknown values reported;
- [ ] no automatic case/whitespace cleanup is applied to raw data.

### STOP conditions

An invalid official enum value in a required row is a blocker until treatment is explicitly documented.

---

## DT-043 — Check negative or impossible numeric values

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Detect values that are structurally or physically impossible.

### Hard range checks

Examples:

```text
order_units >= 0
order_weight_kg >= 0
order_volume_m3 >= 0
distance_km >= 0
planned_travel_duration_min >= 0
actual_travel_duration_min >= 0
service_allowance_min >= 0
depot_to_district_km >= 0
depot_to_district_freeflow_min >= 0
inter_stop_km >= 0
inter_stop_freeflow_min >= 0
days_since_last_served >= 0
```

Vehicle operational quantities should be strictly positive when present:

```text
weight_cap_kg > 0
volume_cap_m3 > 0
km_per_l > 0
weekly_fuel_quota_l > 0
free_flow_kmh > 0
```

Official bounded fields:

```text
dow in [0, 6]
festival_ramp in [0, 1]
binary fields in {0, 1}
```

### Speed/disruption indices

The booklet states:

```text
100 = free flow / clear
lower values = slower / disrupted
```

Do not impose an undocumented lower bound beyond basic numeric plausibility unless the local official data definition supports it.

Negative indices are suspicious; classify them as at least WARNING and confirm before making them blocking.

### Zero order sizes

The booklet defines order units/weight/volume as order size. A zero value may be suspicious but is not explicitly forbidden in the booklet.

Therefore:

```text
negative = BLOCKER
zero = WARNING unless another official rule proves impossibility
```

### Tests

Synthetic boundary tests.

### Definition of Done

- [ ] impossible negatives identified;
- [ ] official bounded values enforced;
- [ ] zero values not overclassified without evidence;
- [ ] raw values remain untouched.

### STOP conditions

Impossible numeric values in required keys/constraints that would invalidate later calculations are blockers.

---

## DT-044 — Check extreme values and outliers

**Execution:** Batch A  
**Mark:** [E]  
**Priority:** P0

### Objective

Identify extreme but potentially valid values for later modelling review.

### Important distinction

```text
Impossible value ≠ outlier
```

DT-043 handles impossible values.

DT-044 handles unusual values that may still be real within the synthetic scenario.

### Recommended local methods

For continuous/count variables:

- robust quantiles;
- IQR;
- median absolute deviation;
- upper-tail inspection;
- group-aware comparison where later useful.

Do not run outlier logic on:

- IDs;
- binary flags;
- categorical codes;
- dates/times represented numerically;
- submission placeholders.

### Candidate variables

```text
order_units
order_weight_kg
order_volume_m3
distance_km
planned_travel_duration_min
actual_travel_duration_min
service_allowance_min
vehicle capacities
travel reference metrics
days_since_last_served
```

### No automatic treatment

Phase 03 must not:

- winsorize;
- clip;
- drop;
- log-transform;
- replace outliers.

The private report should record candidates for later EDA/model phases.

### Tests

Synthetic distribution with known extreme value.

### Definition of Done

- [ ] outliers detected separately from impossible values;
- [ ] no automatic cleaning;
- [ ] later-review candidates recorded privately.

### STOP conditions

Outliers alone are not a blocker unless they violate an official hard rule or reveal parse corruption.

---

## DT-045 — Check order ID uniqueness

**Execution:** **INDIVIDUAL CRITICAL TASK**  
**Mark:** [E]  
**Priority:** P0

### Objective

Prove that order identifiers behave according to official semantics before Task 1/2A work.

### Checks

#### `deliveries_train.csv`

```text
delivery_id
```

must be nonblank and unique within the file.

#### `task1_test_inputs.csv`

```text
delivery_id
```

must be nonblank and unique within the file.

#### Cross-file overlap

Check whether the same `delivery_id` appears in both:

```text
deliveries_train.csv
task1_test_inputs.csv
```

For Task 2A, history will later be built by appending these files and counting each unique order once.

Therefore cross-file duplicates are a **critical warning/blocker for demand-history construction** and must be understood before Phase 11.

Do not deduplicate silently.

#### Task 2B

Within scenario S1:

```text
order_ref
```

is the allocation key and must be unique.

Do not substitute `outlet_id`.

### Tests

Synthetic:

- unique IDs;
- duplicated train ID;
- duplicated test ID;
- train/test overlap;
- two Task 2B orders same outlet but different `order_ref` → valid;
- duplicate `order_ref` → blocker.

### Definition of Done

- [ ] order IDs unique in each official order table;
- [ ] cross-file overlap status recorded;
- [ ] Task 2B order_ref uniqueness proven;
- [ ] no silent deduplication.

### STOP conditions

Any unexplained duplicate official order identifier blocks dependent work.

---

## DT-046 — Check route-leg key uniqueness

**Execution:** **INDIVIDUAL CRITICAL TASK**  
**Mark:** [E]  
**Priority:** P0

### Objective

Ensure route-leg keys are structurally safe for the Phase 04 Task 1 join.

### Checks

For training and test route legs:

```text
leg_id
```

must be unique.

Also verify the Task 1 join key:

```text
route_id + seq
```

is unique in:

```text
route_legs_train.csv
route_legs_test.csv
```

The booklet states `seq` is the route position and each dispatched order matches exactly one route leg.

A duplicated:

```text
(route_id, seq)
```

would make that relationship ambiguous.

### Order-side structural checks

For dispatched order rows with a route:

```text
route_id
seq_in_route
```

must be nonblank and `seq_in_route >= 0`.

Do not perform the complete one-to-one order-to-leg match yet; that belongs to the dedicated Task 1 join tasks in Phase 04.

### Tests

Synthetic:

- unique leg IDs and route keys;
- duplicate `leg_id`;
- duplicate `(route_id, seq)`;
- same `seq` on different route IDs is valid;
- same route with different seq is valid.

### Definition of Done

- [ ] leg_id unique;
- [ ] route_id+seq unique;
- [ ] route-side join key is safe;
- [ ] order-side dispatched key fields structurally valid.

### STOP conditions

Duplicate `(route_id, seq)` is a Phase 03 blocker.

---

## DT-047 — Check outlet-reference consistency

**Execution:** **INDIVIDUAL CRITICAL TASK**  
**Mark:** [E]  
**Priority:** P0

### Objective

Ensure every outlet-referencing record points to a valid official outlet and copied outlet attributes do not contradict the reference table.

### Core checks

`outlets.csv`:

- exactly 120 unique `outlet_id` rows as stated by the competition;
- IDs follow the official range/pattern where practical;
- brand ∈ Fresh/Style/Tech;
- district/depot populated;
- access fields valid.

Referenced `outlet_id` values in:

```text
deliveries_train.csv
task1_test_inputs.csv
route_legs_train.csv (to_outlet)
route_legs_test.csv (to_outlet)
task2b_peak_day_scenarios.csv
```

must exist in `outlets.csv`.

### Attribute consistency

Where the same official attributes are copied into an order/scenario/route record, compare against reference:

```text
brand
district
depot
window_open_time
window_close_time
dock_type                where present
parking_constraint       where present
mall_window              where present
```

Do not overwrite mismatches.

### Fresh double-order edge case

The booklet explicitly allows a Fresh outlet to have separate dry and chilled orders for the same date.

Therefore:

```text
same outlet_id + same order_date
```

is **not** a duplicate-order error by itself.

### Tests

Synthetic:

- valid reference;
- unknown outlet;
- brand mismatch;
- depot mismatch;
- two valid orders for same Fresh outlet/date;
- Task 2B same outlet with multiple order_ref values.

### Definition of Done

- [ ] 120 unique official outlets confirmed locally;
- [ ] all outlet references resolve;
- [ ] copied attributes checked;
- [ ] valid multiple-order scenario not falsely rejected.

### STOP conditions

Unknown outlet IDs or contradictory core outlet identity fields are blockers until understood.

---

## DT-048 — Check vehicle-reference consistency

**Execution:** **INDIVIDUAL CRITICAL TASK**  
**Mark:** [E]  
**Priority:** P0

### Objective

Ensure vehicle references resolve to the official fleet and copied vehicle attributes are consistent.

### Core checks

`vehicles.csv`:

- exactly 60 unique vehicles;
- IDs follow official range/pattern where practical;
- `type` ∈ truck/van;
- `temp` ∈ reefer/ambient;
- capacities positive;
- depot valid.

References from:

```text
deliveries_train.csv
task1_test_inputs.csv
route_legs_train.csv
route_legs_test.csv
task2b_peak_day_fleet.csv
```

must resolve when a vehicle assignment is present.

### Attribute consistency

Compare:

```text
deliveries.vehicle_type  ↔ vehicles.type
deliveries.vehicle_temp  ↔ vehicles.temp
deliveries.depot         ↔ vehicles.depot when the assignment is meant to serve that depot

route_legs.vehicle_type  ↔ vehicles.type
route_legs.vehicle_temp  ↔ vehicles.temp
route_legs.depot         ↔ vehicles.depot
```

For `not_run` orders, blank vehicle assignment is expected.

### Important boundary

Do not validate full load feasibility in Phase 03.

Capacity/temperature/van-only trip feasibility belongs to Task 2B or operational planning logic.

This task validates reference consistency only.

### Tests

Synthetic:

- valid vehicle;
- unknown vehicle;
- type mismatch;
- temperature mismatch;
- home-depot mismatch;
- not_run with blank vehicle.

### Definition of Done

- [ ] 60 unique vehicles confirmed locally;
- [ ] assigned vehicle references resolve;
- [ ] type/temp/depot copied attributes checked;
- [ ] no raw value is corrected automatically.

### STOP conditions

Unknown vehicle IDs in dispatched/route records or contradictory reference identity are blockers.

---

## DT-049 — Check calendar coverage

**Execution:** Batch C  
**Mark:** [E]  
**Priority:** P0

### Objective

Ensure `calendar.csv` covers every date/week needed by Task 1 and Task 2A.

### Date coverage

Collect required dates locally from:

```text
deliveries_train.order_date
deliveries_train.dispatch_date where present
task1_test_inputs.order_date
task1_test_inputs.dispatch_date where present
route_legs_train.date
route_legs_test.date
```

Every valid nonblank date should join to `calendar.date`.

### Task 2A week coverage

For each forecast year/week in `task2a_test_inputs.csv`, verify `calendar.csv` contains the corresponding ISO week.

Do not forecast yet.

### Calendar consistency checks

Validate locally:

```text
calendar.date unique
dow corresponds to date with Monday = 0
iso_year / iso_week correspond to the date's ISO calendar
is_weekend consistent with dow
festival_ramp in [0,1]
binary flags in {0,1}
```

Do not infer `is_operating` solely from weekday because holidays/other calendar context may close operations. Use the supplied field as the official operating-date indicator.

### Tests

Synthetic:

- complete coverage;
- missing date;
- missing forecast week;
- incorrect dow;
- incorrect ISO week;
- Sunday/weekend handling.

### Definition of Done

- [ ] all required historical/test dates covered;
- [ ] all Task 2A forecast weeks represented;
- [ ] calendar internal consistency checked.

### STOP conditions

Missing calendar coverage for a date/week required by downstream official logic is a blocker.

---

## DT-050 — Check road-condition coverage

**Execution:** Batch C  
**Mark:** [E]  
**Priority:** P0

### Objective

Measure whether date-specific road-condition data can be joined for the records where the team may later use it.

### Important source boundary

The booklet describes `road_conditions.csv` as date-specific district disruptions and documents `disruption_index`, but does not prescribe a complete feature set.

Therefore:

- use the Phase 02 observed schema/join map locally;
- do not invent keys;
- do not require road conditions as a model feature;
- do not silently assume missing road conditions mean "clear".

### Local coverage checks

Using locally resolved join keys:

1. validate key fields are nonblank;
2. validate key uniqueness if the table is intended as one row per join key;
3. measure coverage against relevant Task 1 train/test route/order records;
4. record missing-coverage rate privately;
5. classify:
   - complete/near-complete → PASS;
   - partial but usable → WARNING;
   - schema/join unresolved → BLOCKER for using this feature, not necessarily for the entire Datathon.

### No default imputation in Phase 03

Do not set missing `disruption_index = 100`.

A fallback may be designed later with validation and documentation.

### Tests

Synthetic date+district coverage fixture.

### Definition of Done

- [ ] join keys are explicit locally;
- [ ] coverage measured;
- [ ] gaps documented;
- [ ] no invented clear-road default.

### STOP conditions

If the join cannot be defined, road-condition features must remain disabled until resolved.

The whole Phase 03 may still pass if road-condition use is explicitly disabled and no official task depends on it directly.

---

## DT-051 — Check traffic-speed coverage

**Execution:** Batch C  
**Mark:** [E]  
**Priority:** P0

### Objective

Measure whether `traffic_speed.csv` can support planned Task 1 traffic features.

### Source boundary

The booklet documents traffic as typical congestion by district/hour and explicitly documents:

```text
monsoon
speed_index
```

Use the actual Phase 02 schema locally to determine all join dimensions.

Do not invent a district/hour key if the local schema differs.

### Checks

1. validate join-key fields;
2. validate key uniqueness where appropriate;
3. validate `speed_index` numeric;
4. measure coverage against planned route-leg date/hour/district/monsoon combinations;
5. separate:
   - training planned-context coverage;
   - Task 1 test planned-context coverage.

### Important rule

Only prediction-time-valid traffic context may later become a feature.

Do not use actual travel time as a traffic feature.

### Missing coverage

Do not automatically interpret missing rows as free-flow traffic.

Classify gaps and defer fallback decisions to feature-engineering/model phases.

### Tests

Synthetic coverage matrix.

### Definition of Done

- [ ] traffic join dimensions resolved locally;
- [ ] coverage measured;
- [ ] train/test gaps identified privately;
- [ ] no leakage introduced.

### STOP conditions

Unresolved traffic mapping blocks use of traffic features, not necessarily the whole Datathon if those features are disabled.

---

## DT-052 — Check train/test category compatibility

**Execution:** Batch C  
**Mark:** [E]  
**Priority:** P0

### Objective

Identify categories that appear in prediction/scenario inputs but not in historical training data.

### Task 1 comparisons

Compare equivalent fields between:

```text
deliveries_train.csv
task1_test_inputs.csv
```

and:

```text
route_legs_train.csv
route_legs_test.csv
```

Candidate fields:

```text
brand
district
depot
temp_requirement
vehicle_type
vehicle_temp
```

and any approved categorical feature identified later.

### Task 2A

Verify every test combination:

```text
depot + brand
```

has historical demand support in the combined history source, or mark unseen combinations clearly.

Do not build the combined weekly demand table yet.

### Task 2B

Scenario categories should resolve to official references and valid official enums.

### Severity

An unseen category is not automatically corrupt data.

Classify:

```text
WARNING
```

if the value is valid in a reference table but absent from model training.

Classify:

```text
BLOCKER
```

if it is invalid against official/reference definitions.

### Tests

Synthetic:

- all categories seen;
- valid unseen category;
- invalid category;
- unseen depot-brand forecast series.

### Definition of Done

- [ ] Task 1 train/test compatibility checked;
- [ ] Task 2A series support checked;
- [ ] valid unseen categories separated from invalid categories;
- [ ] modelling fallback requirement documented.

### STOP conditions

Do not start advanced feature/model work while an invalid category remains unresolved.

---

## DT-053 — Create automated schema assertions

**Execution:** **INDIVIDUAL CRITICAL TASK**  
**Mark:** [E]  
**Priority:** P0

### Objective

Convert Phase 02/03 knowledge into reusable, deterministic assertions so later phases cannot silently proceed on a broken dataset.

### Output

```text
src/common/schema_assertions.py
tests/test_schema_assertions.py
```

### Required assertion families

At minimum:

#### Files/schema

- required files exist;
- required columns exist;
- official keys exist.

#### Unique identifiers

- order keys;
- route leg IDs;
- route join keys;
- outlet IDs;
- vehicle IDs;
- calendar dates;
- Task 2B order_ref within scenario.

#### Official counts

- `outlets.csv` = 120 unique outlets;
- `vehicles.csv` = 60 unique vehicles.

#### Official enums

- brands;
- dispatch statuses;
- temperature requirement;
- depots;
- dock/access categories;
- vehicle type/temp;
- Task 2B scenario/status;
- binary flags;
- road classes where applicable.

#### Formatting

- valid dates;
- valid `HH:MM`;
- valid mall-window format;
- nonnegative/positive bounds;
- `dow` range;
- `festival_ramp` range.

#### References

- outlet references resolve;
- vehicle references resolve;
- required calendar coverage.

#### Leakage guard

Assert that direct Task 1 feature lists do not contain:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start
service_min
late_flag
```

The first four are training actuals; the latter three are target-derived.

### Assertion behavior

Do not make every warning raise an exception.

Implement:

```text
assertions = hard contract
audit warnings = reportable observations
```

Hard assertions should fail fast.

Warnings should be returned in structured reports.

### Tests

Tests must use synthetic fixtures only and prove both:

```text
valid fixture → PASS
invalid fixture → expected assertion failure
```

### Definition of Done

- [ ] reusable schema assertions exist;
- [ ] critical official rules are machine-enforced;
- [ ] warnings are not confused with hard failures;
- [ ] leakage guard exists;
- [ ] synthetic tests cover failures.

### STOP conditions

Phase 03 cannot pass while hard schema assertions fail on the local official dataset.

---

## DT-054 — Produce dataset-audit report

**Execution:** Final Phase 03 task  
**Mark:** [E]  
**Priority:** P0

### Objective

Create a concise but complete audit record that explains what was checked, what passed, what warnings exist, and what downstream treatment is required.

### Private report

Generate:

```text
reports/private/phase03_data_quality/phase03_audit_report.md
```

The report may contain private aggregate diagnostics because it remains local and ignored.

### Required sections

```text
1. Audit scope
2. Data files audited
3. Rule/severity definitions
4. Missing-value findings
5. Duplicate-row findings
6. Key-integrity findings
7. Type/date/time validation
8. Category validation
9. Impossible numeric findings
10. Outlier review
11. Order ID integrity
12. Route-leg key integrity
13. Outlet reference integrity
14. Vehicle reference integrity
15. Calendar coverage
16. Road-condition coverage
17. Traffic-speed coverage
18. Train/test compatibility
19. Automated schema assertion result
20. Blocking issues
21. Non-blocking warnings
22. Downstream treatment decisions
23. Phase verdict
```

### Tracked documentation

`docs/data_quality_rules.md` should describe **methods and rules only**, not private competition results.

Do not commit the private report.

### Required final verdict

```text
PHASE 03 STATUS: PASS / FAIL
BLOCKERS: <count>
WARNINGS DOCUMENTED: YES / NO
READY FOR PHASE 04: YES / NO
```

### Definition of Done

- [ ] all DT-036–DT-053 results represented;
- [ ] blockers explicit;
- [ ] warnings have treatment notes;
- [ ] no raw-data mutation occurred;
- [ ] report is private/ignored;
- [ ] tracked documentation contains only safe methods/rules.

### STOP conditions

`READY FOR PHASE 04` cannot be YES with unresolved blockers.

---

# 10. Recommended implementation architecture

## `src/common/data_quality.py`

Recommended functions:

```python
audit_missing_values(...)
audit_complete_duplicates(...)
audit_primary_keys(...)
audit_semantic_types(...)
audit_dates(...)
audit_times(...)
audit_categories(...)
audit_numeric_ranges(...)
audit_outliers(...)
audit_order_ids(...)
audit_route_leg_keys(...)
audit_outlet_references(...)
audit_vehicle_references(...)
audit_calendar_coverage(...)
audit_road_coverage(...)
audit_traffic_coverage(...)
audit_train_test_compatibility(...)
build_audit_summary(...)
```

Every function should return structured results rather than print rows.

Recommended result shape:

```python
{
    "rule_id": "DT-045.ORDER_ID_UNIQUE",
    "status": "PASS",
    "table": "deliveries_train.csv",
    "severity": "BLOCKER",
    "affected_count": 0,
    "private_detail_ref": None,
    "message": "delivery_id is unique"
}
```

Do not expose private row content in console messages.

## `src/common/schema_assertions.py`

Keep hard schema/integrity contracts separate from exploratory audit warnings.

## `scripts/run_data_quality_audit.py`

The local CLI orchestrates the full audit.

---

# 11. Local audit CLI contract

Recommended command:

```bash
python scripts/run_data_quality_audit.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --rules configs/data_quality_rules.yaml \
  --output-dir reports/private/phase03_data_quality
```

### Console output

Safe output should look like:

```text
PHASE 03 LOCAL DATA-QUALITY AUDIT: PASS
Hard schema assertions: PASS
Blocking rules: 0
Warnings present: YES
Detailed report written to local private report directory.
No raw row values were printed.
```

On failure:

```text
PHASE 03 LOCAL DATA-QUALITY AUDIT: FAIL
Blocking rules: 2
Blocker codes:
- DT-046.ROUTE_KEY_UNIQUE
- DT-049.CALENDAR_COVERAGE
Detailed private report written locally.
No raw row values were printed.
```

Do not print:

- actual record values;
- row samples;
- full lists of IDs;
- category-value lists;
- private paths outside the project-relative report path.

---

# 12. Recommended execution grouping

Phase 03 should **not** be treated as one blind full-phase run.

Use four batches plus individual reviews.

## Batch A — General data quality

```text
DT-036 Missing values
DT-037 Full duplicates
DT-038 Primary-key duplicates
DT-039 Semantic data types
DT-040 Date formats
DT-041 Time formats
DT-042 Categories
DT-043 Impossible numeric values
DT-044 Extreme values/outliers
```

Agent implements together using synthetic tests.

Then human local audit checkpoint.

## Critical Integrity Block — execute/review individually

```text
DT-045 Order ID uniqueness
DT-046 Route-leg key uniqueness
DT-047 Outlet-reference consistency
DT-048 Vehicle-reference consistency
```

Each should receive an explicit PASS before moving to coverage checks.

## Batch C — Coverage and train/test compatibility

```text
DT-049 Calendar coverage
DT-050 Road-condition coverage
DT-051 Traffic-speed coverage
DT-052 Train/test category compatibility
```

## Critical Automation Gate

```text
DT-053 Automated schema assertions
```

Implement and review alone.

## Final report

```text
DT-054 Dataset-audit report
```

Then run the Phase 03 completion audit.

---

# 13. Synthetic test strategy

Create:

```text
tests/test_data_quality.py
tests/test_schema_assertions.py
```

All tests must use synthetic data.

Minimum coverage:

## Missing values

- expected not_run blanks;
- invalid missing key;
- conditional dispatched fields.

## Duplicates

- complete duplicate;
- duplicate key with different values;
- valid repeated outlet across multiple orders.

## Types

- numeric parse success/failure;
- ID string handling;
- binary validation.

## Dates/times

- valid/invalid dates;
- valid/invalid HH:MM;
- valid/invalid time range;
- no naive midnight rejection.

## Categories

- valid enums;
- invalid enums;
- valid reference-backed unseen category.

## Numeric ranges

- negative weight/volume/duration;
- zero suspicious but not always hard-fail;
- capacity positivity;
- dow/festival_ramp boundaries.

## Outliers

- extreme but valid numeric value → warning, not deletion.

## IDs

- duplicate delivery_id;
- cross-file delivery overlap;
- duplicate order_ref;
- same outlet with multiple order_ref values.

## Route keys

- duplicate leg_id;
- duplicate `(route_id, seq)`;
- same seq across different routes valid.

## References

- unknown outlet;
- outlet-attribute mismatch;
- unknown vehicle;
- vehicle-type/temp/depot mismatch.

## Calendar

- missing date;
- wrong dow;
- wrong ISO week;
- missing Task 2A forecast week.

## Coverage

- complete/partial road coverage;
- complete/partial traffic coverage.

## Compatibility

- unseen but valid category;
- invalid category;
- unseen depot-brand forecast combination.

## Assertions

- valid synthetic project passes;
- one hard violation fails predictably;
- warnings do not throw unless configured as hard.

---

# 14. Edge-case catalogue

## `not_run` order

Valid possibilities include blank dispatch/route fields.

Do not classify all such blanks as errors.

## Deferred order

The requested `order_date` remains the demand date for Task 2A even if dispatch happens later.

Phase 03 may validate date/status consistency but must not rewrite the requested date.

## Same Fresh outlet/date with two orders

Valid because Fresh may place separate ambient and chilled orders.

Do not deduplicate by:

```text
outlet_id + order_date
```

## Two Task 2B orders for one outlet

Valid.

Use:

```text
order_ref
```

as order identity.

## Midnight route

Clock times alone may appear to go backwards when crossing midnight.

Do not flag this from lexical/time-of-day ordering in Phase 03.

## Mall window blank

Expected outside mall-constrained outlets.

## Festival blank

Expected when no festival applies.

## Extreme Tech order

May be legitimate.

Outlier ≠ error.

## Missing road/traffic feature

May mean the optional feature is unusable.

It does not automatically invalidate an official prediction task.

## Unseen test category

Valid if it exists in official references; modelling code later needs unknown-category handling.

## Raw data error vs extraction error

Never edit official raw data.

If a file appears corrupted, re-download/re-extract from the organizer-approved source before designing a cleaning workaround.

---

# 15. Phase 03 global STOP conditions

Phase 03 must remain:

```text
READY FOR PHASE 04: NO
```

if any of the following is unresolved:

- Phase 02 did not pass.
- Official raw data is modified in-place.
- A required key is missing.
- An official unique key is duplicated.
- `delivery_id` uniqueness fails.
- `order_ref` uniqueness within Task 2B scenario fails.
- `leg_id` uniqueness fails.
- `(route_id, seq)` is duplicated in route-leg data.
- required dispatched-order route fields are structurally unusable.
- an order references an unknown outlet.
- a route/order/fleet row references an unknown required vehicle.
- official enum validation fails.
- required nonblank date cannot parse.
- required nonblank time cannot parse.
- an impossible negative/invalid bounded value affects core task logic.
- calendar coverage is missing for required Task 1/2A dates/weeks.
- automated hard schema assertions fail.
- private audit outputs are Git-tracked.
- raw/private data has been exposed to the coding agent.
- audit tests fail.
- local audit returns FAIL.
- any warning that directly affects Phase 04 label construction has no treatment decision.

Road/traffic feature coverage alone does not have to block Phase 04 if those optional features are explicitly disabled until resolved.

---

# 16. Phase 03 Definition of Done

Phase 03 is complete only when:

- [ ] DT-036 PASS
- [ ] DT-037 PASS
- [ ] DT-038 PASS
- [ ] DT-039 PASS
- [ ] DT-040 PASS
- [ ] DT-041 PASS
- [ ] DT-042 PASS
- [ ] DT-043 PASS
- [ ] DT-044 PASS
- [ ] DT-045 PASS
- [ ] DT-046 PASS
- [ ] DT-047 PASS
- [ ] DT-048 PASS
- [ ] DT-049 PASS
- [ ] DT-050 PASS or documented optional-feature WARNING
- [ ] DT-051 PASS or documented optional-feature WARNING
- [ ] DT-052 PASS or all valid unseen categories have a treatment plan
- [ ] DT-053 PASS
- [ ] DT-054 PASS
- [ ] no raw official file was modified
- [ ] all hard assertions pass
- [ ] all blockers are zero
- [ ] warnings are documented
- [ ] Task 1 critical join keys are structurally safe
- [ ] outlet and vehicle references are consistent
- [ ] required calendar coverage exists
- [ ] synthetic tests pass
- [ ] real local audit passes
- [ ] private reports remain ignored
- [ ] independent review passes

Then:

```text
PHASE 03 STATUS: PASS
READY FOR PHASE 04: YES
```

---

# 17. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-03-data-quality
```

Recommended commits:

```text
chore(quality): add data-quality rule configuration
feat(quality): add general dataset audit checks
feat(quality): add key and reference integrity checks
feat(quality): add coverage and compatibility checks
feat(schema): add hard schema assertions
test(quality): add synthetic data-quality tests
docs(quality): document audit rules and severity policy
```

Before every commit:

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
```

Before merge:

```bash
python -m pip check
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py
git status
```

Merge only after:

```text
LOCAL PHASE 03 AUDIT: PASS
INDEPENDENT PHASE 03 REVIEW: PASS
```

---

# 18. Enhanced Cursor implementation prompt

```text
We are implementing WayLoom Datathon PHASE 03 only.

PHASE:
Data-Quality Audit

TASK RANGE:
DT-036 through DT-054

READ FIRST:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved PHASE_00_COMPETITION_CONTRACT.md
3. approved PHASE_01_COMPETITION_CONTRACT.md
4. approved PHASE_02_COMPETITION_CONTRACT.md
5. PHASE_03_COMPETITION_CONTRACT.md
6. tracked official-source data dictionary/configuration from Phase 02

OFFICIAL SOURCE PRIORITY:
Challenge Booklet / official artifacts
>
approved master plan
>
phase contracts
>
implementation assumptions

==================================================
CRITICAL DATA SAFETY
==================================================

Do NOT open, inspect, preview, summarize or transmit real competition data.

Do NOT access:

data/raw/**
data/interim/**
data/processed/**
reports/private/**

Do NOT run the real Phase 03 audit against official CSVs.

Do NOT use:
head()
tail()
sample()
cat
type
Get-Content
CSV preview
notebook display
or any equivalent operation on official data.

Your job is to implement audit code and SYNTHETIC tests.

The human operator will run the finished audit locally outside the AI-agent context.

Do NOT start Phase 04.

==================================================
CORE PHASE RULE
==================================================

Phase 03 is AUDIT ONLY.

Never mutate official raw files.

Do not:
drop rows
deduplicate
fill missing values
clip outliers
replace categories
correct dates/times
rename official columns

Audit and report only.

Every rule must classify results using:

PASS
EXPECTED
WARNING
BLOCKER
NOT_APPLICABLE

Phase 03 may pass with documented warnings.
It may NOT pass with unresolved blockers.

==================================================
IMPLEMENTATION FILES
==================================================

CREATE:

configs/data_quality_rules.yaml

src/common/data_quality.py

src/common/schema_assertions.py

scripts/run_data_quality_audit.py

docs/data_quality_rules.md

tests/test_data_quality.py

tests/test_schema_assertions.py

UPDATE ONLY IF NEEDED:

.gitignore
.cursorignore

Ensure:

reports/private/**

remains ignored/excluded.

==================================================
DT-036 — MISSING VALUES
==================================================

Implement conditional missingness.

Do not classify every blank as invalid.

Officially valid examples include:

dispatch_status = not_run
→ dispatch_date may be blank
→ route_id may be blank

mall_window may be blank outside malls.

festival may be blank when there is no festival.

Hard identifiers such as:
delivery_id
leg_id
row_id
outlet_id
vehicle_id
calendar date
order_ref/scenario where applicable

must not be silently missing.

For attempted/deferred dispatched orders, route/vehicle/planned fields required for delivery history should be present or explicitly reported.

Do not delete rows.

==================================================
DT-037 — COMPLETE DUPLICATES
==================================================

Detect exact duplicated records in every CSV.

Do not call drop_duplicates() on raw data.

Report privately only.

==================================================
DT-038 — DUPLICATE PRIMARY KEYS
==================================================

Validate official unique identifiers and composite keys.

At minimum:

deliveries_train.delivery_id
task1_test_inputs.delivery_id
route_legs_train.leg_id
route_legs_test.leg_id
task2a_test_inputs.row_id
outlets.outlet_id
vehicles.vehicle_id
calendar.date
service_allowance.(brand,dock_type)
task2b scenario.(scenario,order_ref)
task2b fleet.(scenario,vehicle_id) where confirmed

Candidate keys must remain clearly labelled until validated.

==================================================
DT-039 — DATA TYPES
==================================================

Validate semantic parseability rather than relying on Pandas dtype.

Distinguish:

identifier
categorical
integer/count
numeric continuous
binary
date
clock time
time range
duration minutes

Never convert IDs into numeric magnitude.

==================================================
DT-040 — DATE FORMATS
==================================================

Validate all nonblank official dates.

Preserve raw strings/values.

Audit official dispatch semantics:

attempted:
dispatch_date should correspond to requested day under official definition.

deferred:
dispatch is later due to capacity shortfall.

not_run:
dispatch_date blank is valid.

Do not rewrite any dates.

==================================================
DT-041 — TIME FORMATS
==================================================

Validate HH:MM.

Valid range:
00:00–23:59

Validate mall_window as:
HH:MM-HH:MM
when present.

Do NOT reject routes based on naive time ordering.
Routes may cross midnight.

Phase 04 handles time reconstruction.

==================================================
DT-042 — CATEGORICAL VALUES
==================================================

Enforce organizer-documented enums.

brand:
Fresh
Style
Tech

dispatch_status:
attempted
deferred
not_run

temp_requirement:
chilled
ambient

depot:
Peliyagoda
Kandy

dock_type:
rear_dock
street
mall_bay

parking_constraint:
normal
van_only
mall_dock

vehicle type:
truck
van

vehicle temp:
reefer
ambient

road_class:
urban
suburban
highway
hill

Task2B scenario:
S1

Task2B fleet status:
available
in_workshop

Official binary indicators:
0 or 1

Do not silently trim/fix invalid raw values.

==================================================
DT-043 — IMPOSSIBLE NUMERIC VALUES
==================================================

Hard nonnegative examples:

order_units
order_weight_kg
order_volume_m3
distance_km
planned_travel_duration_min
actual_travel_duration_min
service_allowance_min
depot_to_district_km
depot_to_district_freeflow_min
inter_stop_km
inter_stop_freeflow_min
days_since_last_served

Strictly positive when present:

vehicle weight capacity
vehicle volume capacity
km_per_l
weekly_fuel_quota_l
free_flow_kmh

Official bounds:

dow in [0,6]
festival_ramp in [0,1]
binary columns in {0,1}

Negative order size = BLOCKER.
Zero order size = WARNING unless an official rule proves it impossible.

Do not invent undocumented bounds for speed/disruption index.

==================================================
DT-044 — EXTREME VALUES / OUTLIERS
==================================================

Implement robust outlier detection for relevant continuous/count fields.

Allowed methods include:
IQR
MAD
quantile flags

Outlier != invalid.

Do NOT:
drop
clip
winsorize
replace

Store detailed findings privately.

==================================================
DT-045 — ORDER ID UNIQUENESS
CRITICAL INDIVIDUAL CHECK
==================================================

Validate:

deliveries_train.delivery_id unique

task1_test_inputs.delivery_id unique

Check train/test delivery_id overlap because Task 2A later appends both and counts unique orders.

Do not silently deduplicate overlap.

For Task 2B:

order_ref must be unique within S1.

Two orders may share the same outlet_id.
That is valid.

Never use outlet_id as Task 2B order identity.

==================================================
DT-046 — ROUTE-LEG KEY UNIQUENESS
CRITICAL INDIVIDUAL CHECK
==================================================

Validate:

route_legs_train.leg_id unique
route_legs_test.leg_id unique

and:

(route_id, seq)

unique within route_legs_train and route_legs_test.

For dispatched orders:

route_id and seq_in_route must be structurally usable.

Do NOT perform the full Phase 04 order-to-leg join yet.

==================================================
DT-047 — OUTLET REFERENCE CONSISTENCY
CRITICAL INDIVIDUAL CHECK
==================================================

Validate the official outlet reference.

Local audit should confirm:
120 unique outlets.

Referenced outlet IDs from:
deliveries_train
task1_test_inputs
route_legs_train.to_outlet
route_legs_test.to_outlet
task2b_peak_day_scenarios

must resolve to outlets.csv.

Where copied fields exist, check consistency:

brand
district
depot
window_open_time
window_close_time
dock_type
parking_constraint
mall_window

Important:
A Fresh outlet may have separate dry/chilled orders on the same date.
Do not treat repeated outlet_id + date as a duplicate.

==================================================
DT-048 — VEHICLE REFERENCE CONSISTENCY
CRITICAL INDIVIDUAL CHECK
==================================================

Local audit should confirm:
60 unique vehicles.

Validate assigned vehicle IDs against vehicles.csv.

Compare copied metadata where available:

vehicle_type ↔ vehicles.type
vehicle_temp ↔ vehicles.temp
depot ↔ vehicles.depot

not_run orders may have no assignment.

Do not perform trip-capacity feasibility here.

==================================================
DT-049 — CALENDAR COVERAGE
==================================================

Validate calendar coverage for:

deliveries_train.order_date
deliveries_train.dispatch_date where present
task1_test_inputs.order_date
task1_test_inputs.dispatch_date where present
route_legs_train.date
route_legs_test.date

Also ensure every Task 2A forecast iso_year + iso_week is represented in calendar.csv.

Validate internal calendar consistency:

date unique
dow corresponds to date, Monday=0
iso_year/iso_week correspond to date
is_weekend agrees with dow
festival_ramp in [0,1]
binary flags are 0/1

Do not infer is_operating only from weekday.
Use the supplied calendar field.

==================================================
DT-050 — ROAD CONDITION COVERAGE
==================================================

road_conditions is optional model context, not a mandatory feature.

Use the Phase 02 local schema/join information.

Do not invent join keys.

Measure local coverage against relevant Task 1 dates/districts.

Do not automatically set missing disruption_index to 100.

If mapping cannot be resolved:
disable road feature for later phases until resolved.

This may be WARNING rather than full Phase blocker if road features are not required.

==================================================
DT-051 — TRAFFIC SPEED COVERAGE
==================================================

Use the actual Phase 02 local schema.

Do not invent missing district/hour key fields.

Validate speed_index is numeric.

Measure historical and Task 1 test planned-context coverage.

Do not replace missing traffic with free-flow automatically.

Do not use actual travel duration as traffic context.

==================================================
DT-052 — TRAIN/TEST CATEGORY COMPATIBILITY
==================================================

Compare compatible categorical columns between:

deliveries_train vs task1_test_inputs

route_legs_train vs route_legs_test

Check future Task 2A depot+brand combinations have historical support.

Check Task 2B categories against references/official enums.

Valid unseen test category:
WARNING

Invalid official/reference category:
BLOCKER

Do not model anything yet.

==================================================
DT-053 — AUTOMATED SCHEMA ASSERTIONS
CRITICAL INDIVIDUAL GATE
==================================================

Create reusable hard assertions for:

required files/columns
unique identifiers
route join key uniqueness
120 outlets
60 vehicles
official enums
binary/bounded fields
date/time formatting
reference integrity
calendar coverage

Add leakage guard that fails if a direct Task 1 feature list contains:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start
service_min
late_flag

The first four are training actuals.
The final three are target-derived.

Hard assertions fail fast.

Warnings remain structured audit results and should not raise automatically.

==================================================
DT-054 — DATASET AUDIT REPORT
==================================================

The LOCAL HUMAN RUN must create:

reports/private/phase03_data_quality/phase03_audit_report.md

It must summarize all DT-036 through DT-053 checks.

Tracked docs/data_quality_rules.md must describe methods/rules only.

Never commit the private report.

==================================================
LOCAL CLI
==================================================

Implement:

python scripts/run_data_quality_audit.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --rules configs/data_quality_rules.yaml \
  --output-dir reports/private/phase03_data_quality

The CLI must:

- never print raw rows
- never print DataFrames
- never print full ID lists
- never print private category lists
- return non-zero when blockers exist
- output only safe blocker rule codes + official filename
- store detailed findings privately

==================================================
SYNTHETIC TESTING
==================================================

All agent-run tests use synthetic fixtures only.

Create comprehensive tests for:

missingness
complete duplicates
duplicate keys
semantic types
date parsing
HH:MM/time ranges
official enums
numeric bounds
outlier warnings
delivery_id uniqueness
cross-file ID overlap
order_ref uniqueness
route leg key uniqueness
outlet references
vehicle references
calendar coverage
road coverage
traffic coverage
train/test compatibility
hard schema assertions
leakage guard

Run ONLY:

pytest -q \
  tests/test_project_setup.py \
  tests/test_data_inventory.py \
  tests/test_data_quality.py \
  tests/test_schema_assertions.py

python -m pip check

Do NOT run real-data audit.

==================================================
EXECUTION CHECKPOINTS
==================================================

Implement in this order:

BATCH A:
DT-036–DT-044

CRITICAL:
DT-045
DT-046
DT-047
DT-048

BATCH C:
DT-049–DT-052

CRITICAL:
DT-053

FINAL:
DT-054

After each critical task, ensure its synthetic tests pass before continuing.

==================================================
FINAL RESPONSE
==================================================

Return only:

PHASE:
03 — AGENT IMPLEMENTATION STAGE

TASK IMPLEMENTATION:
DT-036 READY/FAIL
DT-037 READY/FAIL
DT-038 READY/FAIL
DT-039 READY/FAIL
DT-040 READY/FAIL
DT-041 READY/FAIL
DT-042 READY/FAIL
DT-043 READY/FAIL
DT-044 READY/FAIL
DT-045 READY/FAIL
DT-046 READY/FAIL
DT-047 READY/FAIL
DT-048 READY/FAIL
DT-049 READY/FAIL
DT-050 READY/FAIL
DT-051 READY/FAIL
DT-052 READY/FAIL
DT-053 READY/FAIL
DT-054 READY/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

SYNTHETIC TESTS:
...

DATA-SAFETY:
data/raw accessed: MUST BE NO
reports/private accessed: MUST BE NO
official row values observed: MUST BE NO
raw files modified: MUST BE NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local audit command.

PHASE 03 STATUS:
AWAITING LOCAL AUDIT

READY FOR PHASE 04:
NO

Then STOP.

Do not run the real audit.
Do not begin Phase 04.
```

---

# 19. Enhanced Codex implementation prompt

```text
Implement WayLoom Datathon Phase 03 tooling only.

PHASE:
Data-Quality Audit

TASK RANGE:
DT-036 through DT-054

Read:
- WAYLOOM_DATATHON_MASTER_PLAN.md
- approved Phase 00–02 contracts
- PHASE_03_COMPETITION_CONTRACT.md
- tracked Phase 02 manifest/data-dictionary documentation

Official organizer material is the highest authority.

==================================================
DATA ACCESS RESTRICTION
==================================================

Do not open or read:

data/raw/**
data/interim/**
data/processed/**
reports/private/**

Do not run the real audit.

Use only tracked code/config/docs and synthetic fixtures.

The human will run the final audit locally.

==================================================
AUDIT-ONLY RULE
==================================================

Do not mutate raw official data.

No:
dropna
drop_duplicates on official files
imputation
clipping
winsorization
category replacement
date correction
column renaming
raw CSV rewrite

Implement detection/reporting only.

Use statuses:

PASS
EXPECTED
WARNING
BLOCKER
NOT_APPLICABLE

==================================================
CREATE
==================================================

configs/data_quality_rules.yaml
src/common/data_quality.py
src/common/schema_assertions.py
scripts/run_data_quality_audit.py
docs/data_quality_rules.md
tests/test_data_quality.py
tests/test_schema_assertions.py

Ensure reports/private/** stays ignored by Git/Cursor.

==================================================
IMPLEMENT EVERY TASK
==================================================

DT-036:
Conditional missing-value checks.
Respect expected not_run/mall/festival blanks.

DT-037:
Exact duplicate-row detection.
Never auto-remove.

DT-038:
Official/candidate primary-key duplicate checks.

DT-039:
Semantic data-type validation.

DT-040:
Valid dates + dispatch-status/date semantics.

DT-041:
HH:MM + HH:MM-HH:MM validation.
Do not reject midnight-crossing sequences.

DT-042:
Organizer-documented enum validation.

DT-043:
Impossible/negative/bounded numeric checks.

DT-044:
Robust outlier flags only; no treatment.

DT-045:
Critical order-ID uniqueness:
- deliveries_train.delivery_id
- task1_test_inputs.delivery_id
- cross-file overlap status
- Task2B order_ref within scenario
Do not deduplicate.

DT-046:
Critical route-leg key uniqueness:
- leg_id
- route_id + seq
Do not perform full Phase 04 join yet.

DT-047:
Critical outlet reference consistency:
- 120 unique outlets
- all order/route/scenario references resolve
- copied identity/access fields checked
- repeated same Fresh outlet/date can be valid

DT-048:
Critical vehicle reference consistency:
- 60 unique vehicles
- assigned vehicle references resolve
- copied type/temp/depot fields agree
- blank not_run assignment allowed

DT-049:
Calendar date/week coverage and internal consistency.

DT-050:
Road-condition join/coverage using Phase 02 local schema only.
Do not invent keys or assume missing = clear.

DT-051:
Traffic-speed join/coverage using Phase 02 local schema only.
Do not invent keys or use actual travel fields.

DT-052:
Train/test category compatibility.
Valid unseen = warning.
Invalid official/reference category = blocker.

DT-053:
Critical hard schema assertions.

Include leakage deny-list:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start
service_min
late_flag

DT-054:
Private dataset-audit report generator.

==================================================
OFFICIAL ENUMS / BOUNDS TO SUPPORT
==================================================

brand:
Fresh | Style | Tech

dispatch_status:
attempted | deferred | not_run

temp_requirement:
chilled | ambient

depot:
Peliyagoda | Kandy

dock_type:
rear_dock | street | mall_bay

parking_constraint:
normal | van_only | mall_dock

vehicle type:
truck | van

vehicle temperature:
reefer | ambient

road_class:
urban | suburban | highway | hill

Task2B scenario:
S1

Task2B fleet status:
available | in_workshop

dow:
0..6, Monday=0

festival_ramp:
0..1

binary official flags:
0 or 1

==================================================
LOCAL CLI CONTRACT
==================================================

Implement:

python scripts/run_data_quality_audit.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --rules configs/data_quality_rules.yaml \
  --output-dir reports/private/phase03_data_quality

Console output must contain only:

overall PASS/FAIL
hard assertion PASS/FAIL
blocker count
warning presence
blocker rule codes + official filename where needed

Never print:
rows
DataFrames
full ID lists
private category lists
raw invalid values

Detailed diagnostics go only to ignored private reports.

==================================================
TESTS
==================================================

Synthetic fixtures only.

Test every DT-036–DT-053 rule family.

Run:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py

python -m pip check

Do not execute anything on real raw data.

==================================================
EXECUTION ORDER
==================================================

Batch A:
DT-036–044

Critical individual checks:
DT-045
DT-046
DT-047
DT-048

Batch C:
DT-049–052

Critical gate:
DT-053

Final:
DT-054

If a critical implementation test fails:
STOP and report it.

==================================================
RETURN
==================================================

PHASE 03 — CODE/TOOLING STAGE

DT-036 READY/FAIL
DT-037 READY/FAIL
DT-038 READY/FAIL
DT-039 READY/FAIL
DT-040 READY/FAIL
DT-041 READY/FAIL
DT-042 READY/FAIL
DT-043 READY/FAIL
DT-044 READY/FAIL
DT-045 READY/FAIL
DT-046 READY/FAIL
DT-047 READY/FAIL
DT-048 READY/FAIL
DT-049 READY/FAIL
DT-050 READY/FAIL
DT-051 READY/FAIL
DT-052 READY/FAIL
DT-053 READY/FAIL
DT-054 READY/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TESTS:
...

DATA ACCESS:
official raw files opened: NO
private reports opened: NO
official row values observed: NO
raw files modified: NO

LOCAL HUMAN RUN REQUIRED:
YES

Print the exact local audit command.

PHASE 03 STATUS:
AWAITING LOCAL AUDIT

READY FOR PHASE 04:
NO

STOP.
```

---

# 20. Enhanced Phase 03 review prompt

Use a **fresh Cursor/Codex chat** after the local audit.

Do not attach the private audit report.

```text
Perform an independent review of completed WayLoom Datathon Phase 03.

DO NOT:
- open data/raw
- open data/interim
- open data/processed
- open reports/private
- run the real audit
- inspect official rows
- modify code initially
- begin Phase 04

READ:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_03_COMPETITION_CONTRACT.md
3. configs/data_quality_rules.yaml
4. src/common/data_quality.py
5. src/common/schema_assertions.py
6. scripts/run_data_quality_audit.py
7. docs/data_quality_rules.md
8. tests/test_data_quality.py
9. tests/test_schema_assertions.py
10. relevant tracked Phase 02 manifest/docs
11. .gitignore
12. .cursorignore

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 03 AUDIT: <PASS / FAIL>
BLOCKING ASSERTIONS: <0 or number>
DOCUMENTED WARNINGS: <YES / NO>

Do not ask for the private report or raw values.

AUDIT EVERY TASK:

DT-036:
Expected/conditional missing values are separated from invalid missingness.

DT-037:
Exact duplicates are detected and never auto-deleted.

DT-038:
Official keys are checked without silent deduplication.

DT-039:
Semantic types are validated.

DT-040:
Dates parse and dispatch status/date semantics are represented safely.

DT-041:
HH:MM and mall time ranges validated without naive midnight logic.

DT-042:
Official enums are source-grounded.

DT-043:
Impossible numeric values and official bounds are enforced without inventing unsupported constraints.

DT-044:
Outliers are warnings/review candidates, not automatic deletions.

DT-045:
delivery_id/order_ref integrity is correct.
Repeated outlet_id is not treated as repeated order identity.

DT-046:
leg_id and route_id+seq uniqueness are enforced.
Full Task 1 join is correctly deferred to Phase 04.

DT-047:
Outlet references are checked against the 120-outlet reference and valid multiple-order behavior is allowed.

DT-048:
Vehicle references are checked against the 60-vehicle reference.

DT-049:
Calendar covers all required dates/weeks and internal ISO/dow logic is checked.

DT-050:
Road coverage uses actual locally resolved schema and no missing=clear assumption.

DT-051:
Traffic coverage does not use actual journey information or invented joins.

DT-052:
Valid unseen categories are distinguished from invalid values.

DT-053:
Hard schema assertions exist and leakage deny-list contains:
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start
service_min
late_flag

DT-054:
Private report generation exists and tracked docs contain methods only.

PRIVACY:
- no raw data embedded in tests
- no real record values in code/docs
- reports/private ignored
- console avoids raw values
- raw files are never mutated

RUN ONLY SAFE TESTS:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py

python -m pip check

git status

Do not execute the real audit.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

SYNTHETIC TEST STATUS:
PASS / FAIL

HUMAN LOCAL AUDIT STATUS:
PASS / FAIL

HARD ASSERTIONS:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING WARNINGS:
...

DT-036: PASS/FAIL
DT-037: PASS/FAIL
DT-038: PASS/FAIL
DT-039: PASS/FAIL
DT-040: PASS/FAIL
DT-041: PASS/FAIL
DT-042: PASS/FAIL
DT-043: PASS/FAIL
DT-044: PASS/FAIL
DT-045: PASS/FAIL
DT-046: PASS/FAIL
DT-047: PASS/FAIL
DT-048: PASS/FAIL
DT-049: PASS/FAIL
DT-050: PASS/FAIL
DT-051: PASS/FAIL
DT-052: PASS/FAIL
DT-053: PASS/FAIL
DT-054: PASS/FAIL

PHASE 03 REVIEW:
PASS / FAIL

READY FOR PHASE 04:
YES / NO

If FAIL:
list exact blockers only.

Do not fix anything until explicitly approved.
Do not begin Phase 04.
```

---

# 21. Local Phase 03 execution instructions

After the agent implementation stage passes synthetic tests:

## Step 1 — Use a normal local terminal

Do not run the raw-data audit through an AI-agent terminal/session.

## Step 2 — Verify ignored paths

```bash
git status
git check-ignore -v reports/private/phase03_data_quality/audit_summary.json
```

## Step 3 — Run safe test suite

```bash
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py
```

## Step 4 — Run real local audit

```bash
python scripts/run_data_quality_audit.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --rules configs/data_quality_rules.yaml \
  --output-dir reports/private/phase03_data_quality
```

Windows PowerShell, one line:

```powershell
python scripts/run_data_quality_audit.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --rules configs/data_quality_rules.yaml --output-dir reports/private/phase03_data_quality
```

## Step 5 — Inspect private report locally

Do not upload it to Cursor/Codex.

Resolve any local blockers.

## Step 6 — Return only the control result

Example:

```text
LOCAL PHASE 03 AUDIT: PASS
BLOCKING ASSERTIONS: 0
DOCUMENTED WARNINGS: YES
```

Then run the independent review prompt.

---

# 22. Phase 03 completion record template

```markdown
# Phase 03 Completion Record

## Tasks

- [ ] DT-036
- [ ] DT-037
- [ ] DT-038
- [ ] DT-039
- [ ] DT-040
- [ ] DT-041
- [ ] DT-042
- [ ] DT-043
- [ ] DT-044
- [ ] DT-045
- [ ] DT-046
- [ ] DT-047
- [ ] DT-048
- [ ] DT-049
- [ ] DT-050
- [ ] DT-051
- [ ] DT-052
- [ ] DT-053
- [ ] DT-054

## Agent / synthetic stage

- Synthetic tests: PASS / FAIL
- Schema-assertion tests: PASS / FAIL
- pip check: PASS / FAIL

## Local official-data audit

- Missing-value audit: PASS / WARNING / BLOCKER
- Duplicate-row audit: PASS / WARNING / BLOCKER
- Key integrity: PASS / FAIL
- Type/date/time validation: PASS / FAIL
- Category validation: PASS / FAIL
- Numeric validation: PASS / WARNING / FAIL
- Order IDs: PASS / FAIL
- Route keys: PASS / FAIL
- Outlet references: PASS / FAIL
- Vehicle references: PASS / FAIL
- Calendar coverage: PASS / FAIL
- Road coverage: PASS / WARNING / DISABLED
- Traffic coverage: PASS / WARNING / DISABLED
- Train/test compatibility: PASS / WARNING / FAIL
- Hard schema assertions: PASS / FAIL

## Safety

- Raw files modified: NO
- Private report committed: NO
- Raw rows shared with AI tools: NO

## Blockers

- Count:
- Codes:

## Warnings

- Documented: YES / NO
- Downstream treatment recorded: YES / NO

## Review

- Independent review: PASS / FAIL

## Verdict

PHASE 03 STATUS: PASS / FAIL

READY FOR PHASE 04: YES / NO
```

---

# 23. Final Phase 03 checklist

Before Phase 04:

- [ ] Phase 02 passed.
- [ ] all 19 Phase 03 tasks implemented.
- [ ] synthetic tests pass.
- [ ] no raw dataset was mutated.
- [ ] missing values classified correctly.
- [ ] exact duplicates audited.
- [ ] primary keys audited.
- [ ] semantic types audited.
- [ ] dates/times validated.
- [ ] official enums validated.
- [ ] impossible numbers checked.
- [ ] outliers recorded without automatic removal.
- [ ] order IDs unique.
- [ ] route-leg IDs unique.
- [ ] `route_id + seq` unique.
- [ ] outlet references consistent.
- [ ] 120 unique outlets confirmed locally.
- [ ] vehicle references consistent.
- [ ] 60 unique vehicles confirmed locally.
- [ ] calendar coverage complete for required dates/weeks.
- [ ] road coverage status documented.
- [ ] traffic coverage status documented.
- [ ] train/test compatibility documented.
- [ ] hard schema assertions pass.
- [ ] Task 1 leakage deny-list exists.
- [ ] private audit report exists locally.
- [ ] blockers = 0.
- [ ] warnings have downstream treatment notes.
- [ ] private reports remain ignored.
- [ ] independent review passes.

Only then:

```text
PHASE 03 STATUS: PASS
READY FOR PHASE 04: YES
```

**Do not begin Phase 04 automatically.** Phase 04 contains high-risk label construction and must be executed task-by-task/small-batch according to its own implementation contract.
