# PHASE 18 — Task 2B Scenario Understanding

> **Filename:** `PHASE_18_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 18 — Task 2B Scenario Understanding  
> **Task range:** **DT-254 → DT-270**  
> **Task count:** **17**  
> **Default priority:** P0  
> **Dependency:** Phases 02–03  
> **Phase gate:** Scenario S1 demand and the available Peliyagoda fleet are correctly understood; workshop vehicles are excluded.  
> **Execution style:** Deterministic scenario loader + schema/contract validation + aggregate diagnostics only.  
> **Do not implement Phase 19 compatibility logic, Phase 20 trip calculation, Phase 21 priority scoring, Phase 22 optimizer, or Phase 23 validator in this phase.**

---

# 1. Purpose

Phase 18 establishes the **canonical Task 2B scenario contract** before any allocation logic is written.

This phase must answer, reproducibly:

- What orders belong to Scenario S1?
- What is the unique allocation key?
- Which vehicles are listed for the scenario?
- Which vehicles are actually available?
- Which vehicles are in the workshop and therefore unusable?
- Which vehicle reference fields will later determine capacity, refrigeration, vehicle type and home depot?
- Which district-travel rows and service-allowance rows are available for later trip-time calculation?
- Is the scenario strictly Peliyagoda as stated by the challenge?
- How much demand exists by brand and district?
- How much demand is chilled?
- How much demand is restricted to vans?
- What are the total weight and volume pressures?
- Which orders were deferred on the previous run?
- What does the distribution of `days_since_last_served` look like?

The output of Phase 18 is **understanding and validated canonical inputs**, not an allocation.

Phase 18 must not:

- assign any order to a vehicle;
- decide served vs deferred;
- generate an order-to-vehicle compatibility matrix;
- calculate trip minutes;
- create candidate trips;
- define solver variables;
- run CP-SAT or another optimizer;
- produce `submission_task2b.csv`;
- invent a prioritization formula;
- change Task 1 or Task 2A artifacts.

---

# 2. Official Task 2B contract

## 2.1 Task objective

Task 2B asks the team to plan deliveries for one peak day when demand exceeds available fleet capacity.

The required final Task 2B outputs are:

1. a complete allocation marking every order as `served` or `deferred`;
2. a vehicle and trip assignment for each served order;
3. a short written prioritization/deferral policy.

Task 2B does **not require a trained model**.

The judges assess:

- feasibility;
- reasoning behind prioritization;
- reasoning behind deferrals.

There is no single correct allocation.

---

# 3. Official scenario S1

Official scenario:

```text
scenario = S1
depot = Peliyagoda
```

Scenario context supplied by the challenge:

```text
A festival is one week away.
Fresh demand is rising, including dairy, meat, and produce.
It is not a payday.
There are no monsoon conditions.
Several vehicles are in the workshop.
```

These facts are scenario context.

Do not replace them with external calendar/weather information.

Do not use scenario context to silently alter hard feasibility constraints.

---

# 4. Official Task 2B inputs

Phase 18 must load and validate these official inputs.

## 4.1 Peak-day orders

```text
task2b_peak_day_scenarios.csv
```

One row per peak-day order.

Official documented fields include:

```text
scenario
order_ref
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
deferred_yesterday
days_since_last_served
```

`order_ref` is the allocation key.

Official warning:

```text
outlet_id may appear more than once
```

Therefore never use `outlet_id` as the unique order key.

---

## 4.2 Peak-day fleet

```text
task2b_peak_day_fleet.csv
```

Official documented fields include:

```text
scenario
vehicle_id
status
```

Scenario statuses identify:

```text
available
in_workshop
```

Only vehicles marked `available` may be allocated.

Vehicles marked `in_workshop` cannot be used.

---

## 4.3 Full vehicle reference

```text
vehicles.csv
```

Phase 18 loads the canonical vehicle reference because later phases need:

```text
vehicle_id
type
temp
weight_cap_kg
volume_cap_m3
depot / home depot
```

and any other official static vehicle fields.

Phase 18 validates reference coverage only.

Compatibility decisions belong to Phase 19.

---

## 4.4 District travel reference

```text
district_travel.csv
```

Official Task 2B trip-time calculation later uses:

```text
depot_to_district_freeflow_min
inter_stop_freeflow_min
```

for the trip's district.

Phase 18 loads and validates coverage.

Trip-time calculation belongs to Phase 20.

---

## 4.5 Service allowance reference

```text
service_allowance.csv
```

Official Task 2B handling-time calculation later looks up:

```text
service_allowance_min
```

by:

```text
brand + dock_type
```

Phase 18 loads and validates this reference.

Actual trip calculations belong to Phase 20.

---

# 5. Official feasibility rules — context ledger

Phase 18 must document these rules so later phases cannot accidentally change them.

It does **not** implement all of them yet.

## Rule 1 — Brand and district

All orders sharing the same:

```text
vehicle_id + trip_id
```

must belong to the same:

```text
brand
district
```

Implementation belongs mainly to Phases 20–23.

---

## Rule 2 — Refrigeration

```text
temp_requirement = chilled
```

requires:

```text
vehicle.temp = reefer
```

Reefer vehicles may also carry ambient orders.

Compatibility implementation belongs to Phase 19.

---

## Rule 3 — Vehicle access

```text
parking_constraint = van_only
```

requires:

```text
vehicle.type = van
```

Compatibility implementation belongs to Phase 19.

---

## Rule 4 — Home depot

A vehicle may serve only outlets assigned to its own depot.

Scenario S1 is Peliyagoda.

Phase 18 validates source depot facts.

Compatibility implementation belongs to Phase 19.

---

## Rule 5 — Whole orders

A served order is assigned to:

```text
exactly one vehicle
exactly one trip
```

Do not split an order.

Solver/validator implementation belongs to Phases 22–23.

---

## Rule 6 — Capacity

Per trip:

```text
sum(order_volume_m3) <= volume_cap_m3
sum(order_weight_kg) <= weight_cap_kg
```

Phase 18 summarizes demand only.

Individual compatibility belongs to Phase 19.

Trip capacity validation belongs to Phases 22–23.

---

## Rule 7 — Trips and time

Each vehicle may run at most:

```text
2 trips
```

Official daily budgets:

```text
Fresh trips:
270 minutes per vehicle

Style + Tech trips combined:
480 minutes per vehicle
```

The windows are separate.

A vehicle may run, for example:

```text
one Fresh trip
+
one Style trip
```

if each budget condition is satisfied, while still respecting the maximum of two trips overall.

Time implementation belongs to Phases 20, 22 and 23.

---

# 6. Official trip-time formula — freeze now, implement later

The official trip formula is:

```text
trip_minutes
=
outbound travel
+
inter-stop travel
+
handling time
```

where:

```text
outbound travel
=
depot_to_district_freeflow_min
counted once per trip
```

```text
inter-stop travel
=
inter_stop_freeflow_min * (number_of_orders - 1)
```

```text
handling time
=
sum(service_allowance_min for every order)
```

Officially:

```text
DO NOT add the return journey
```

because the stated budgets already allow for it.

Official example:

```text
Fresh / Gampaha / 3 orders
outbound = 37
inter-stop = 9 * (3 - 1) = 18
handling = 15 + 15 + 16 = 46

trip total = 101 minutes
```

Phase 18 may create schema/reference tests that make this later calculation possible.

It must not yet construct candidate trips or trip-duration outputs.

---

# 7. Official checker boundary

The challenge supplies:

```text
check_allocation.py
```

It checks Task 2B feasibility.

Passing the checker means:

```text
allocation satisfies the implemented feasibility checks
```

It does **not** mean:

```text
allocation is optimal
```

Judges separately assess prioritization and deferral reasoning.

Phase 18 must preserve this distinction in documentation.

---

# 8. Source hierarchy

When implementing Phase 18:

1. official Challenge Booklet;
2. official CSV/template/checker artifacts;
3. approved WayLoom master task inventory;
4. approved Phase 02–03 data-contract utilities;
5. this Phase 18 contract;
6. engineering assumptions.

If the official files contradict an engineering assumption:

```text
STOP
```

Do not silently reconcile it using general knowledge.

---

# 9. Phase 18 task registry

| Status | Task | Mark | Priority | Work item |
|---|---|---:|---:|---|
| [ ] | **DT-254** | [O] | P0 | Load peak-day orders |
| [ ] | **DT-255** | [O] | P0 | Load peak-day fleet |
| [ ] | **DT-256** | [O] | P0 | Load full vehicle reference |
| [ ] | **DT-257** | [O] | P0 | Load district travel table |
| [ ] | **DT-258** | [O] | P0 | Load service allowance |
| [ ] | **DT-259** | [O] | P0 | Filter to scenario S1 |
| [ ] | **DT-260** | [O] | P0 | Filter fleet to available vehicles |
| [ ] | **DT-261** | [O] | P0 | Exclude in_workshop vehicles |
| [ ] | **DT-262** | [O] | P0 | Confirm Peliyagoda home-depot requirement |
| [ ] | **DT-263** | [E] | P0 | Summarize demand by brand |
| [ ] | **DT-264** | [E] | P0 | Summarize demand by district |
| [ ] | **DT-265** | [E] | P0 | Summarize chilled demand |
| [ ] | **DT-266** | [E] | P0 | Summarize van-only demand |
| [ ] | **DT-267** | [E] | P0 | Summarize weight demand |
| [ ] | **DT-268** | [E] | P0 | Summarize volume demand |
| [ ] | **DT-269** | [E] | P0 | Identify previously deferred orders |
| [ ] | **DT-270** | [E] | P0 | Inspect days_since_last_served |

**Phase complete:** [ ]  
**READY FOR PHASE 19:** NO

---

# 10. Recommended repository files

Create/update:

```text
src/task2b/__init__.py
src/task2b/scenario.py
src/task2b/scenario_summary.py

scripts/inspect_task2b_scenario.py

configs/task2b_scenario.yaml

docs/task2b_scenario_spec.md

tests/test_task2b_scenario.py
tests/test_task2b_scenario_summary.py
```

Do not create yet:

```text
src/task2b/compatibility.py
src/task2b/trip_time.py
src/task2b/priority.py
src/task2b/optimizer.py
src/task2b/validator.py
```

unless an empty placeholder already exists.

Those belong to later phases.

---

# 11. Private Phase 18 outputs

Recommended local-only outputs:

```text
reports/private/phase18_task2b_scenario/
├── scenario_summary.json
├── order_schema_validation.json
├── fleet_schema_validation.json
├── reference_coverage.json
├── fleet_status_summary.json
├── demand_by_brand.csv
├── demand_by_district.csv
├── chilled_demand_summary.json
├── van_only_demand_summary.json
├── weight_demand_summary.json
├── volume_demand_summary.json
├── deferred_yesterday_summary.json
├── days_since_last_served_summary.json
├── warnings.json
└── phase18_scenario_report.md
```

Do not commit them.

Do not print private order rows or real `order_ref` values to the AI agent.

---

# 12. Recommended configuration

Create:

```text
configs/task2b_scenario.yaml
```

Recommended content:

```yaml
version: 1

scenario:
  expected_id: S1
  expected_depot: Peliyagoda

files:
  orders_manifest_key: task2b_peak_day_scenarios
  fleet_manifest_key: task2b_peak_day_fleet
  vehicles_manifest_key: vehicles
  district_travel_manifest_key: district_travel
  service_allowance_manifest_key: service_allowance

orders:
  key: order_ref
  required_columns:
    - scenario
    - order_ref
    - outlet_id
    - brand
    - district
    - depot
    - dock_type
    - parking_constraint
    - temp_requirement
    - order_weight_kg
    - order_volume_m3
    - deferred_yesterday
    - days_since_last_served

fleet:
  key: vehicle_id
  available_status: available
  workshop_status: in_workshop

vehicles:
  key: vehicle_id

district_travel:
  district_key: district

service_allowance:
  keys:
    - brand
    - dock_type

validation:
  require_unique_order_ref: true
  require_unique_fleet_vehicle_id: true
  require_all_fleet_vehicle_refs: true
  require_all_order_district_travel_refs: true
  require_all_order_service_allowance_refs: true
  require_s1_only_after_filter: true
  require_peliyagoda_orders: true
  require_peliyagoda_usable_fleet: true

summary:
  top_n_private_only: 20
  private_output_dir: reports/private/phase18_task2b_scenario
```

Use official schemas as authority if actual column names differ.

---

# 13. Canonical in-memory objects

Recommended immutable/read-only conceptual outputs:

```text
orders_s1
```

All S1 orders.

```text
fleet_s1
```

All S1 scenario fleet rows, including available and in-workshop.

```text
available_fleet_s1
```

Only vehicles marked available.

```text
vehicles_ref
```

Full official vehicle reference.

```text
district_travel_ref
```

Official district travel reference.

```text
service_allowance_ref
```

Official service allowance reference.

Do not create an allocation table in Phase 18.

---

# 14. Detailed task specifications

---

## DT-254 — Load peak-day orders

### Objective

Load:

```text
task2b_peak_day_scenarios.csv
```

through the canonical manifest/IO layer.

### Required validations

At minimum:

```text
scenario exists
order_ref exists
order_ref non-null
order_ref nonblank
outlet_id exists
brand exists
district exists
depot exists
dock_type exists
parking_constraint exists
temp_requirement exists
order_weight_kg exists
order_volume_m3 exists
deferred_yesterday exists
days_since_last_served exists
```

Validate numeric fields:

```text
order_weight_kg finite
order_weight_kg >= 0

order_volume_m3 finite
order_volume_m3 >= 0

days_since_last_served integer-like
days_since_last_served >= 0

deferred_yesterday in {0,1}
```

If `order_units` exists, validate it but do not require it for Task 2B feasibility unless the official schema requires it.

### Critical key rule

```text
order_ref
```

is the allocation key.

Do not treat:

```text
outlet_id
```

as unique.

### Tests

- valid synthetic rows;
- duplicate outlet IDs allowed;
- duplicate `order_ref` rejected;
- blank/null `order_ref` rejected;
- invalid deferred flag rejected;
- negative weight/volume rejected;
- nonfinite weight/volume rejected;
- invalid days-since value rejected.

### STOP

If `order_ref` cannot be established as unique.

---

## DT-255 — Load peak-day fleet

### Objective

Load:

```text
task2b_peak_day_fleet.csv
```

through the manifest.

### Required fields

```text
scenario
vehicle_id
status
```

### Required validation

```text
vehicle_id non-null
vehicle_id nonblank
```

Within scenario S1:

```text
vehicle_id unique
```

Validate status against official supported values present in the scenario contract.

At minimum the code must understand:

```text
available
in_workshop
```

Do not silently reinterpret unknown statuses as unavailable.

Unknown status:

```text
STOP / schema blocker
```

unless official data documentation explicitly defines it.

### Tests

- available;
- in_workshop;
- duplicate vehicle;
- blank vehicle;
- unsupported status.

---

## DT-256 — Load full vehicle reference

### Objective

Load:

```text
vehicles.csv
```

and validate the reference rows required by S1 fleet vehicles.

### Fields required later

At minimum:

```text
vehicle_id
type
temp
weight_cap_kg
volume_cap_m3
depot
```

Use the exact official home-depot column name in the real file.

### Validate

```text
vehicle_id unique

type in official allowed domain

temp in official allowed domain

weight_cap_kg > 0
volume_cap_m3 > 0

depot nonblank
```

Every S1 fleet `vehicle_id` must match exactly one vehicle reference row.

### Do not yet

- mark orders compatible;
- compute scarce vehicle types;
- allocate orders.

### Tests

- complete fleet coverage;
- missing vehicle reference fails;
- duplicate reference ID fails;
- invalid/nonpositive capacity fails.

---

## DT-257 — Load district travel table

### Objective

Load:

```text
district_travel.csv
```

for later Task 2B trip-time calculations.

### Required official fields for Task 2B

```text
district
depot_to_district_freeflow_min
inter_stop_freeflow_min
```

Use exact file schema.

### Validate

```text
district key unique for the relevant reference grain
depot_to_district_freeflow_min finite >= 0
inter_stop_freeflow_min finite >= 0
```

Every S1 order district must have the required travel reference.

If the real table is depot-specific, validate the appropriate composite key rather than collapsing it.

### Do not yet

compute:

```text
trip_minutes
```

### Tests

- valid district coverage;
- missing district fails;
- duplicate applicable key fails;
- negative/nonfinite time fails.

---

## DT-258 — Load service allowance

### Objective

Load:

```text
service_allowance.csv
```

for later handling-time calculations.

### Official lookup

```text
brand + dock_type
→ service_allowance_min
```

### Validate

```text
brand nonblank
dock_type nonblank
service_allowance_min finite >= 0
```

Applicable:

```text
brand + dock_type
```

must be unique.

Every S1 order's:

```text
brand + dock_type
```

must have a service allowance.

### Do not yet

calculate handling totals for trips.

### Tests

- exact lookup coverage;
- duplicate brand+dock key fails;
- missing pair fails;
- negative/nonfinite allowance fails.

---

## DT-259 — Filter to scenario S1

### Objective

Create canonical S1 order and fleet views.

### Rule

```text
scenario == "S1"
```

Official output scenario is always S1.

### Requirements

Filter explicitly.

After filter:

```text
all order scenario values == S1
all fleet scenario values == S1
```

Do not silently keep rows for another scenario.

Do not mutate original source frames.

### Important

If the official files contain only S1, the explicit filter still remains useful as a contract.

### Tests

- mixed synthetic S1/S2 input;
- S1 retained;
- other scenarios excluded;
- source frame unmodified;
- empty S1 fails.

---

## DT-260 — Filter fleet to available vehicles

### Objective

Create:

```text
available_fleet_s1
```

using only:

```text
status == available
```

### Rule

The official challenge says only available vehicles may be allocated.

### Requirements

Every row in available fleet must satisfy:

```text
status == available
```

Join/reference coverage to `vehicles.csv` must remain complete.

### Do not yet

decide whether a particular available vehicle can serve a particular order.

### Tests

- available retained;
- workshop excluded from available view;
- unknown status not silently treated as available;
- original fleet remains intact.

---

## DT-261 — Exclude in_workshop vehicles

### Objective

Prove unusable workshop vehicles cannot enter later allocation inputs.

### Hard invariant

```text
available_fleet_s1.vehicle_id
∩
in_workshop_vehicle_ids
=
empty
```

Maintain a separate diagnostic list/count of workshop vehicles privately.

### Defensive API recommendation

Downstream Phase 19 should consume:

```text
available_fleet_s1
```

rather than the unfiltered scenario fleet.

### Tests

- workshop vehicle absent from usable fleet;
- mixed status fixture;
- no accidental status normalization;
- exact disjointness.

### STOP

If a workshop vehicle appears in the usable fleet.

---

## DT-262 — Confirm Peliyagoda home-depot requirement

### Objective

Freeze the S1 depot interpretation.

Official scenario:

```text
S1 = Peliyagoda
```

Official home-depot rule:

```text
vehicle may serve only outlets assigned to its own depot
```

### Phase 18 checks

Orders:

```text
S1 order depot should be Peliyagoda
```

Usable vehicles:

```text
reference home depot should be Peliyagoda
```

or, if the fleet file lists vehicles from multiple home depots, only Peliyagoda-home vehicles can be candidates for S1 later.

### Canonical safe output

Recommended usable Phase 19 fleet:

```text
available
AND
home_depot == Peliyagoda
```

But Phase 18 must distinguish:

```text
scenario availability status
```

from:

```text
home-depot eligibility
```

Do not rewrite the official fleet file.

### Diagnostics

Report privately:

```text
S1 order count with non-Peliyagoda depot
available fleet count
available Peliyagoda-home fleet count
available non-Peliyagoda-home fleet count
```

### STOP

If S1 order depot contradicts the official Peliyagoda scenario without an official explanation.

---

## DT-263 — Summarize demand by brand

### Objective

Understand the peak-day brand mix.

### Official brands expected

```text
Fresh
Style
Tech
```

Use the validated official domain from earlier phases/files.

### Summaries per brand

At minimum:

```text
order_count
total_weight_kg
total_volume_m3
chilled_order_count
van_only_order_count
deferred_yesterday_count
```

Optional:

```text
mean_weight_kg
median_weight_kg
mean_volume_m3
median_volume_m3
```

### Requirements

Aggregate only.

Do not infer allocation priority yet.

### Tests

- known brand counts;
- totals reconcile to scenario total;
- unknown brand fails if outside official domain.

---

## DT-264 — Summarize demand by district

### Objective

Understand the geographic distribution of peak-day demand.

### Summaries per district

```text
order_count
total_weight_kg
total_volume_m3
brand_count
chilled_order_count
van_only_order_count
deferred_yesterday_count
```

Recommended cross-tab:

```text
brand × district
```

with:

```text
order_count
total_weight_kg
total_volume_m3
```

This is especially useful because a later trip must contain one brand and one district.

### Important

Do not create trips yet.

### Tests

- district totals reconcile;
- district reference coverage;
- same outlet appearing more than once is counted as separate orders.

---

## DT-265 — Summarize chilled demand

### Objective

Understand refrigeration pressure before compatibility modelling.

### Chilled definition

```text
temp_requirement == chilled
```

### Required summaries

```text
chilled_order_count
chilled_total_weight_kg
chilled_total_volume_m3
chilled_share_of_orders
chilled_share_of_weight
chilled_share_of_volume
```

Also summarize by:

```text
brand
district
brand + district
```

### Important interpretation

Chilled orders later require reefer vehicles.

But Phase 18 must not yet calculate the compatible vehicle set.

### Tests

- chilled vs ambient counts;
- exact totals;
- invalid temp requirement rejected.

---

## DT-266 — Summarize van-only demand

### Objective

Understand access pressure.

### Van-only definition

```text
parking_constraint == van_only
```

### Required summaries

```text
van_only_order_count
van_only_total_weight_kg
van_only_total_volume_m3
```

By:

```text
brand
district
brand + district
temp_requirement
```

Recommended critical cross-summary:

```text
van_only + chilled
```

because later those orders require a van with reefer capability.

### Important

Do not yet label them impossible or scarce.

That belongs to Phase 19 after vehicle compatibility is calculated.

### Tests

- normal vs van-only;
- chilled van-only subset;
- correct reconciliation.

---

## DT-267 — Summarize weight demand

### Objective

Quantify total and segmented weight pressure.

### Required

Overall:

```text
order_count
total_weight_kg
mean_weight_kg
median_weight_kg
max_weight_kg
p90_weight_kg
p95_weight_kg
```

By:

```text
brand
district
brand + district
temp_requirement
parking_constraint
```

### Do not yet

compare each order to each vehicle capacity.

That is Phase 19.

### Edge cases

- zero-weight order: allow if official data accepts it, but flag privately;
- negative: hard fail;
- nonfinite: hard fail.

---

## DT-268 — Summarize volume demand

### Objective

Quantify total and segmented cubic-volume pressure.

### Required

Overall:

```text
order_count
total_volume_m3
mean_volume_m3
median_volume_m3
max_volume_m3
p90_volume_m3
p95_volume_m3
```

By:

```text
brand
district
brand + district
temp_requirement
parking_constraint
```

### Do not yet

compare order volume against individual vehicles.

That belongs to Phase 19.

### Edge cases

- zero-volume order may be retained and flagged;
- negative/nonfinite fails.

---

## DT-269 — Identify previously deferred orders

### Objective

Identify orders with:

```text
deferred_yesterday == 1
```

Official meaning:

```text
the outlet was skipped on the previous run
```

### Required summaries

```text
deferred_yesterday_count
deferred_yesterday_share
total_weight_kg
total_volume_m3
```

By:

```text
brand
district
temp_requirement
parking_constraint
```

### Important

This field is a candidate prioritization signal later.

Phase 18 must not yet define a priority score or guarantee service.

Do not state:

```text
all deferred_yesterday orders must be served
```

unless the official challenge says so—it does not.

### Tests

- flag 0/1 only;
- exact count;
- separate from final Task 2B `decision`.

---

## DT-270 — Inspect days_since_last_served

### Objective

Understand service-recency pressure.

### Field

```text
days_since_last_served
```

### Required overall summary

```text
count
missing
min
mean
median
p75
p90
p95
max
```

### Recommended grouped summaries

By:

```text
brand
district
deferred_yesterday
```

Recommended distributions:

```text
0–1
2–3
4–7
8+
```

These bins are a WayLoom engineering descriptive convention, not an official organizer priority rule.

Keep configurable if implemented.

### Important

`days_since_last_served` may inform the Phase 21 priority policy.

Phase 18 must not yet choose weights or thresholds for optimization.

### Tests

- nonnegative integer;
- known quantiles/bins;
- missing policy;
- deferred and recency summarized independently.

---

# 15. Scenario-level reconciliation

Before declaring Phase 18 complete, reconcile all summaries back to the canonical S1 order set.

Required:

```text
sum(brand order_count) == total S1 orders

sum(district order_count) == total S1 orders

chilled_count <= total S1 orders

van_only_count <= total S1 orders

deferred_yesterday_count <= total S1 orders

sum(brand total_weight) ≈ overall total_weight

sum(brand total_volume) ≈ overall total_volume
```

Use tight numeric tolerance.

Do not round to force reconciliation.

---

# 16. Reference-coverage audit

Phase 18 must prove later phases have the references they need.

For every S1 order:

```text
district travel reference exists
brand + dock_type service allowance exists
```

For every S1 fleet vehicle:

```text
vehicle reference exists
```

For every available/home-depot-eligible vehicle:

```text
capacity fields present
type present
temperature capability present
home depot present
```

Coverage failures are blockers.

---

# 17. Scenario rule ledger

Generate a tracked documentation object/table in:

```text
docs/task2b_scenario_spec.md
```

Recommended fields:

```text
rule_id
official_rule
official_source
phase_implemented
phase18_validation
notes
```

Example:

```text
R01 | same brand+district per trip | official | Phase 22/23 | documented only
R02 | chilled requires reefer      | official | Phase 19    | source fields validated
R03 | van_only requires van        | official | Phase 19    | source fields validated
R04 | home depot match             | official | Phase 19    | S1 depot validated
R05 | whole order                  | official | Phase 22/23 | order_ref uniqueness validated
R06 | weight+volume capacity       | official | Phase 22/23 | capacities/data validated
R07 | <=2 trips + time budgets     | official | Phase 20/22/23 | source data validated
```

This helps prevent rule drift in later phases.

---

# 18. Required tests

Create:

```text
tests/test_task2b_scenario.py
tests/test_task2b_scenario_summary.py
```

Use synthetic fixtures only.

## Orders

- valid S1 row;
- duplicate `order_ref` fails;
- duplicate `outlet_id` allowed;
- null/blank `order_ref` fails;
- invalid brand fails if outside official domain;
- invalid temp requirement fails;
- invalid parking constraint fails when domain is known;
- negative/nonfinite weight fails;
- negative/nonfinite volume fails;
- invalid `deferred_yesterday` fails;
- negative/noninteger `days_since_last_served` fails.

## Fleet

- valid available;
- valid in_workshop;
- duplicate S1 vehicle fails;
- blank vehicle fails;
- unknown status fails;
- explicit S1 filtering.

## Vehicles

- unique vehicle references;
- S1 fleet full coverage;
- positive weight capacity;
- positive volume capacity;
- supported type;
- supported temperature capability;
- home depot present.

## District travel

- every S1 district covered;
- applicable key unique;
- finite nonnegative outbound time;
- finite nonnegative inter-stop time;
- no trip calculation produced in Phase 18.

## Service allowance

- every S1 brand+dock pair covered;
- unique pair;
- finite nonnegative allowance;
- no trip handling sum produced.

## Availability/workshop

- available view contains only available;
- workshop absent from usable view;
- workshop diagnostic count retained;
- source fleet unchanged.

## Depot

- S1 order depot Peliyagoda;
- Peliyagoda vehicle-home subset;
- non-Peliyagoda available vehicle never silently relabeled;
- scenario contradiction fails.

## Summaries

- brand reconciliation;
- district reconciliation;
- chilled count/totals;
- van-only count/totals;
- chilled+van-only cross-summary;
- weight totals;
- volume totals;
- deferred-yesterday counts;
- days-since-last-served statistics/bins.

## Privacy

- console summary contains no `order_ref`;
- no raw order rows printed;
- reports directed to private ignored path.

---

# 19. Edge cases

## Same outlet appears multiple times

Officially possible.

Treat each `order_ref` as a distinct order.

Do not collapse by `outlet_id`.

---

## Order is both chilled and van-only

Keep both facts.

Do not resolve compatibility yet.

Phase 19 will determine whether reefer vans exist.

---

## Available fleet includes non-Peliyagoda home vehicle

Do not relabel its depot.

Record and exclude it from the later Peliyagoda-compatible fleet input.

If official artifacts imply another interpretation, STOP for review.

---

## Workshop vehicle has excellent capacity

Still unusable.

No exception.

---

## Zero weight or zero volume

If source schema permits numeric zero, retain the order and flag privately.

Do not drop it.

Negative or nonfinite values fail.

---

## `days_since_last_served = 0`

Valid unless official schema says otherwise.

Do not convert to missing.

---

## `deferred_yesterday = 1`

This is a descriptive/prioritization signal.

It is not an automatic served decision.

---

## No chilled orders

Valid in synthetic tests.

Summary should return zero counts/totals without crashing.

Real scenario context suggests Fresh demand is important, but code should remain generic.

---

## No van-only orders

Valid.

Summary returns zero.

---

## Unknown district/reference gap

Hard blocker.

Do not invent travel times.

---

## Missing service allowance pair

Hard blocker.

Do not impute a handling allowance.

---

# 20. Phase 18 STOP conditions

`READY FOR PHASE 19` remains **NO** if any of the following occurs:

- `task2b_peak_day_scenarios.csv` cannot be loaded;
- `task2b_peak_day_fleet.csv` cannot be loaded;
- `vehicles.csv` cannot be loaded;
- `district_travel.csv` cannot be loaded;
- `service_allowance.csv` cannot be loaded;
- S1 orders are empty;
- `order_ref` is missing, blank or duplicated;
- code uses `outlet_id` as allocation key;
- S1 fleet vehicle IDs are duplicated;
- an unknown fleet status is silently reinterpreted;
- an `in_workshop` vehicle appears in the usable fleet;
- vehicle reference coverage is incomplete;
- an S1 district lacks travel reference;
- an S1 brand+dock pair lacks service allowance;
- S1 order depot contradicts Peliyagoda;
- usable-home-depot logic is unresolved;
- weight/volume is negative or nonfinite;
- deferred flag is outside 0/1;
- `days_since_last_served` is invalid;
- aggregate summaries do not reconcile;
- Phase 19 compatibility matrix is prematurely implemented with unapproved assumptions;
- Phase 20 trip calculation is prematurely implemented;
- optimizer logic is introduced;
- real competition rows are exposed to an external AI context;
- Task 1 or Task 2A frozen artifacts are modified;
- synthetic tests fail;
- independent review fails.

---

# 21. Definition of Done

Phase 18 passes only when:

- [ ] DT-254 PASS
- [ ] DT-255 PASS
- [ ] DT-256 PASS
- [ ] DT-257 PASS
- [ ] DT-258 PASS
- [ ] DT-259 PASS
- [ ] DT-260 PASS
- [ ] DT-261 PASS
- [ ] DT-262 PASS
- [ ] DT-263 PASS
- [ ] DT-264 PASS
- [ ] DT-265 PASS
- [ ] DT-266 PASS
- [ ] DT-267 PASS
- [ ] DT-268 PASS
- [ ] DT-269 PASS
- [ ] DT-270 PASS
- [ ] `order_ref` is the canonical unique order key
- [ ] duplicate `outlet_id` values are allowed
- [ ] S1 is explicitly filtered
- [ ] S1 depot is confirmed as Peliyagoda
- [ ] available fleet is isolated
- [ ] workshop vehicles are excluded from usable fleet
- [ ] full vehicle-reference coverage passes
- [ ] district-travel coverage passes
- [ ] service-allowance coverage passes
- [ ] brand summary reconciles
- [ ] district summary reconciles
- [ ] chilled-demand summary generated
- [ ] van-only summary generated
- [ ] weight summary generated
- [ ] volume summary generated
- [ ] previous-deferral summary generated
- [ ] `days_since_last_served` summary generated
- [ ] official feasibility-rule ledger documented
- [ ] official trip-time formula documented but not prematurely implemented
- [ ] checker-vs-optimality distinction documented
- [ ] no allocation decisions generated
- [ ] no compatibility matrix generated
- [ ] no optimizer generated
- [ ] synthetic tests pass
- [ ] full safe repository tests pass
- [ ] `python -m pip check` passes
- [ ] private outputs remain ignored
- [ ] Task 1 frozen artifacts unchanged
- [ ] Task 2A frozen artifacts unchanged
- [ ] independent Phase 18 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 18 STATUS: PASS
READY FOR PHASE 19: YES
```

---

# 22. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-18-task2b-scenario
```

Recommended commits:

```text
feat(task2b): add peak-day scenario loaders
feat(task2b): validate S1 fleet and reference coverage
feat(task2b): add scenario demand summaries
test(task2b): add Phase 18 scenario contract tests
docs(task2b): document official S1 scenario rules
```

Before commit:

```bash
git status
git diff
git diff --check
```

Ensure no private files are staged:

```text
data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
```

Run:

```bash
pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py
pytest -q
python -m pip check
```

Merge only after:

```text
LOCAL PHASE 18 SCENARIO INSPECTION: PASS
INDEPENDENT PHASE 18 REVIEW: PASS
```

---

# 23. Recommended model for Codex

From the WayLoom Codex handoff strategy:

```text
Phase 18:
GPT-5.6 Terra
Reasoning: Medium
```

Why:

- mostly deterministic rule parsing;
- schema validation;
- aggregation;
- data-contract implementation;
- no optimizer yet.

Escalate only if necessary:

```text
GPT-5.6 Sol
Reasoning: Medium
```

Do not spend the strongest model unless there is a real schema/contract ambiguity.

---

# 24. Local private-data command

Codex should implement this command but not inspect real row-level competition data in an external-agent context:

```bash
python scripts/inspect_task2b_scenario.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --config configs/task2b_scenario.yaml \
  --output-dir reports/private/phase18_task2b_scenario
```

PowerShell one-line form:

```powershell
python scripts/inspect_task2b_scenario.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --config configs/task2b_scenario.yaml --output-dir reports/private/phase18_task2b_scenario
```

Console output should be sanitized.

Recommended local status:

```text
LOCAL PHASE 18 SCENARIO INSPECTION: PASS
S1 ORDER KEY UNIQUE: YES
S1 ORDERS DEPOT = PELIYAGODA: YES
AVAILABLE FLEET FILTER: PASS
WORKSHOP VEHICLES IN USABLE FLEET: 0
VEHICLE REFERENCE COVERAGE: PASS
DISTRICT TRAVEL COVERAGE: PASS
SERVICE ALLOWANCE COVERAGE: PASS
BRAND SUMMARY RECONCILIATION: PASS
DISTRICT SUMMARY RECONCILIATION: PASS
```

Do not paste private order rows to Codex.

---

# 25. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 18 only.

PHASE:
Task 2B Scenario Understanding

TASK RANGE:
DT-254 through DT-270

EXECUTION MODE:
Controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Terra — Medium reasoning

FALLBACK:
GPT-5.6 Sol — Medium reasoning

You may perform all normal safe engineering work:
create/edit/refactor tracked Phase 18 code,
create configs/docs,
create synthetic fixtures,
run tests,
inspect tracebacks,
fix normal bugs,
rerun tests,
run pip check,
inspect git status/diff,
and self-review.

Do not stop for routine coding failures.

STOP for:
official-rule ambiguity,
restricted-data requirement,
reference/schema blocker,
conflict with a frozen prior phase,
or any need to invent a Task 2B rule not supported by the official source.

DO NOT START PHASE 19.

READ FIRST:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 18 and Task 2B
4. PHASE_18_COMPETITION_CONTRACT.md
5. relevant Phase 02/03 IO/schema utilities
6. configs/dataset_manifest.yaml
7. existing src/task2b package placeholder if present

TASK 1 AND TASK 2A ARE FROZEN.

Do not modify:
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
configs/task2a_final_models.yaml
outputs/submission_task2a.csv

PRIVATE DATA:

Do not inspect/print row-level competition data from:
data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run tests.

The human operator will run the real scenario inspection locally.

==================================================
OFFICIAL TASK 2B FACTS
==================================================

Scenario:

S1

Depot:

Peliyagoda

Context:

festival one week away
Fresh demand rising
not payday
no monsoon
several vehicles in workshop

Orders file:

task2b_peak_day_scenarios.csv

Fleet file:

task2b_peak_day_fleet.csv

References:

vehicles.csv
district_travel.csv
service_allowance.csv

Canonical allocation key:

order_ref

Do NOT use outlet_id as the unique order key.

outlet_id may appear more than once.

Only fleet rows with:

status = available

may be used.

Vehicles with:

status = in_workshop

must not enter the usable fleet.

==================================================
DOCUMENT — DO NOT YET IMPLEMENT — OFFICIAL FEASIBILITY RULES
==================================================

1. Same vehicle+trip:
   same brand and same district

2. Chilled:
   requires reefer

   Reefer may also carry ambient.

3. van_only:
   requires van

4. Home depot:
   vehicle may serve only outlets assigned to its own depot

5. Whole order:
   one served order → one vehicle + one trip
   no splitting

6. Capacity per trip:
   total volume <= volume_cap_m3
   total weight <= weight_cap_kg

7. Trips/time:
   max 2 trips per vehicle

   Fresh combined vehicle budget:
   <= 270 minutes

   Style + Tech combined vehicle budget:
   <= 480 minutes

Trip time later:

outbound
+
inter_stop * (n_orders - 1)
+
sum(service_allowance)

No return journey.

Do not implement compatibility/trip grouping/optimizer in Phase 18.

==================================================
CREATE
==================================================

src/task2b/__init__.py
src/task2b/scenario.py
src/task2b/scenario_summary.py

scripts/inspect_task2b_scenario.py

configs/task2b_scenario.yaml

docs/task2b_scenario_spec.md

tests/test_task2b_scenario.py
tests/test_task2b_scenario_summary.py

Do not create compatibility/optimizer implementation yet.

==================================================
DT-254 — LOAD PEAK-DAY ORDERS
==================================================

Load task2b_peak_day_scenarios.csv through the manifest.

Validate at least:

scenario
order_ref
outlet_id
brand
district
depot
dock_type
parking_constraint
temp_requirement
order_weight_kg
order_volume_m3
deferred_yesterday
days_since_last_served

order_ref:
non-null
nonblank
unique within S1

Duplicate outlet_id:
ALLOWED

weight/volume:
numeric
finite
>= 0

deferred_yesterday:
0 or 1

days_since_last_served:
nonnegative integer-like

==================================================
DT-255 — LOAD PEAK-DAY FLEET
==================================================

Load task2b_peak_day_fleet.csv.

Validate:

scenario
vehicle_id
status

S1 vehicle_id unique.

Understand at least:

available
in_workshop

Unknown status must not be silently interpreted.

==================================================
DT-256 — LOAD FULL VEHICLE REFERENCE
==================================================

Load vehicles.csv.

Validate relevant fields:

vehicle_id
type
temp
weight_cap_kg
volume_cap_m3
home depot / depot

vehicle_id unique.

All S1 fleet vehicles must have exactly one reference row.

Capacity:
finite
> 0

Do not calculate order compatibility yet.

==================================================
DT-257 — LOAD DISTRICT TRAVEL
==================================================

Load district_travel.csv.

Validate the official applicable key/grain.

Required Task 2B fields:

depot_to_district_freeflow_min
inter_stop_freeflow_min

finite
>= 0

Every S1 order district must have a valid applicable row.

Do not calculate trip minutes.

==================================================
DT-258 — LOAD SERVICE ALLOWANCE
==================================================

Load service_allowance.csv.

Official lookup:

brand + dock_type
→ service_allowance_min

Applicable key unique.

Allowance:
finite
>= 0

Every S1 order brand+dock_type pair must be covered.

Do not calculate handling sums/trips.

==================================================
DT-259 — FILTER S1
==================================================

Explicitly filter:

scenario == S1

for both orders and fleet.

After filter:
all scenarios must equal S1.

Input frames must remain unmodified.

S1 empty:
FAIL.

==================================================
DT-260 — AVAILABLE FLEET
==================================================

Create available_fleet_s1 using only:

status == available

Every row must satisfy that status.

Do not decide order compatibility yet.

==================================================
DT-261 — WORKSHOP EXCLUSION
==================================================

Create workshop diagnostic set.

Assert:

available vehicle IDs
intersection
in_workshop vehicle IDs
=
empty

Downstream Phase 19 should consume the usable filtered fleet rather than
the unfiltered fleet.

Workshop vehicle appearing usable:
HARD FAIL.

==================================================
DT-262 — PELIYAGODA DEPOT CONTRACT
==================================================

Official S1 depot:

Peliyagoda

Validate S1 orders are assigned to Peliyagoda.

Using vehicles.csv, validate home-depot identity.

Canonical Phase 19 usable fleet should only contain:

available
AND
home depot = Peliyagoda

Do not relabel a non-Peliyagoda vehicle.

Report counts privately.

Contradictory S1 order depot:
STOP.

==================================================
DT-263 — DEMAND BY BRAND
==================================================

Summarize per brand:

order_count
total_weight_kg
total_volume_m3
chilled_order_count
van_only_order_count
deferred_yesterday_count

Optional robust size summaries allowed.

Reconcile to total S1 orders.

No priority decisions.

==================================================
DT-264 — DEMAND BY DISTRICT
==================================================

Summarize per district:

order_count
total_weight_kg
total_volume_m3
brand_count
chilled_order_count
van_only_order_count
deferred_yesterday_count

Also generate private brand × district aggregate.

Do not create candidate trips.

==================================================
DT-265 — CHILLED DEMAND
==================================================

Definition:

temp_requirement == chilled

Summarize:

count
weight
volume
shares

by:

brand
district
brand+district

Do not calculate reefer compatibility yet.

==================================================
DT-266 — VAN-ONLY DEMAND
==================================================

Definition:

parking_constraint == van_only

Summarize:

count
weight
volume

by:

brand
district
brand+district
temp_requirement

Explicitly summarize:

van_only + chilled

Do not yet call orders impossible/scarce.

==================================================
DT-267 — WEIGHT DEMAND
==================================================

Overall:

count
sum
mean
median
max
p90
p95

By:
brand
district
brand+district
temp requirement
parking constraint

Do not compare to individual vehicles yet.

==================================================
DT-268 — VOLUME DEMAND
==================================================

Overall:

count
sum
mean
median
max
p90
p95

Same useful groupings as weight.

Do not compare to individual vehicles yet.

==================================================
DT-269 — PREVIOUSLY DEFERRED
==================================================

Definition:

deferred_yesterday == 1

Summarize:

count
share
weight
volume

by:
brand
district
temp requirement
parking constraint

This is a future priority signal only.

Do NOT automatically decide those orders are served.

==================================================
DT-270 — DAYS SINCE LAST SERVED
==================================================

Summarize:

count
missing
min
mean
median
p75
p90
p95
max

Also by:
brand
district
deferred_yesterday

Optional configurable descriptive bins:

0–1
2–3
4–7
8+

These bins are engineering EDA, not an organizer-mandated priority rule.

Do not create Phase 21 priority weights.

==================================================
REFERENCE COVERAGE
==================================================

Prove:

every S1 fleet vehicle
→ vehicles.csv reference

every S1 district
→ district_travel reference

every S1 brand+dock_type
→ service_allowance reference

Missing coverage:
FAIL.

Do not invent/impute references.

==================================================
RECONCILIATION
==================================================

Prove:

brand counts sum to total S1 orders

district counts sum to total S1 orders

brand total weight ≈ overall weight

brand total volume ≈ overall volume

chilled count <= total

van-only count <= total

deferred count <= total

Use tight floating tolerance.

Do not round to force equality.

==================================================
TESTS
==================================================

Use synthetic fixtures only.

Test:

orders:
valid schema
duplicate order_ref rejection
duplicate outlet_id allowed
blank order_ref rejection
invalid deferred flag
negative/nonfinite weight
negative/nonfinite volume
invalid days_since_last_served

fleet:
available
in_workshop
duplicate vehicle
unknown status
S1 filter

vehicles:
reference coverage
positive capacities
type/temp/home depot validation

district travel:
coverage
unique applicable key
nonnegative finite travel fields

service allowance:
brand+dock coverage
unique key
nonnegative finite allowance

availability:
workshop exclusion
available-only usable view

depot:
Peliyagoda S1
non-Peliyagoda vehicle not relabeled

summaries:
brand reconciliation
district reconciliation
chilled
van-only
chilled+van-only
weight
volume
deferred yesterday
days since last served

privacy:
no order_ref in console
no raw rows printed
private report path ignored

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After loaders:
run loader/schema tests.

After fleet/depot:
run availability/depot tests.

After summaries:
run reconciliation/summary tests.

Fix ordinary code bugs automatically.

Then run:

pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py

Then:

pytest -q

Then:

python -m pip check

Then:

git status
git diff
git diff --check

If a test requires private real data:
do not run it inside Codex.
Return the local human command.

Ensure no private data/report files are staged.

==================================================
LOCAL COMMAND
==================================================

Implement but do NOT execute against restricted competition data in Codex:

python scripts/inspect_task2b_scenario.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --config configs/task2b_scenario.yaml \
  --output-dir reports/private/phase18_task2b_scenario

Console summary must be sanitized.

==================================================
STOP CONDITIONS
==================================================

STOP if:

order_ref not unique

outlet_id is used as allocation key

S1 empty

workshop vehicle enters usable fleet

vehicle reference missing

district travel reference missing

service allowance reference missing

S1 order depot contradicts Peliyagoda

weight/volume invalid

deferred flag invalid

days-since invalid

summary reconciliation fails

Phase 19 compatibility logic is prematurely implemented with unsupported assumptions

trip calculation/optimizer is implemented early

Task 1 or Task 2A frozen artifacts change

private competition rows must be exposed

safe tests cannot pass under official rules

==================================================
RETURN ONLY
==================================================

PHASE:
18 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-254 READY / FAIL
DT-255 READY / FAIL
DT-256 READY / FAIL
DT-257 READY / FAIL
DT-258 READY / FAIL
DT-259 READY / FAIL
DT-260 READY / FAIL
DT-261 READY / FAIL
DT-262 READY / FAIL
DT-263 READY / FAIL
DT-264 READY / FAIL
DT-265 READY / FAIL
DT-266 READY / FAIL
DT-267 READY / FAIL
DT-268 READY / FAIL
DT-269 READY / FAIL
DT-270 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

S1 ORDER KEY:
PASS / FAIL

S1 FILTER:
PASS / FAIL

AVAILABLE FLEET FILTER:
PASS / FAIL

WORKSHOP EXCLUSION:
PASS / FAIL

PELIYAGODA DEPOT CONTRACT:
PASS / FAIL

VEHICLE REFERENCE COVERAGE:
PASS / FAIL

DISTRICT TRAVEL COVERAGE:
PASS / FAIL

SERVICE ALLOWANCE COVERAGE:
PASS / FAIL

BRAND SUMMARY:
PASS / FAIL

DISTRICT SUMMARY:
PASS / FAIL

CHILLED SUMMARY:
PASS / FAIL

VAN-ONLY SUMMARY:
PASS / FAIL

WEIGHT SUMMARY:
PASS / FAIL

VOLUME SUMMARY:
PASS / FAIL

DEFERRED-YESTERDAY SUMMARY:
PASS / FAIL

DAYS-SINCE-LAST-SERVED SUMMARY:
PASS / FAIL

SUMMARY RECONCILIATION:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 18 inspection command.

PHASE 18 STATUS:
AWAITING LOCAL TASK2B SCENARIO INSPECTION

READY FOR PHASE 19:
NO

Then STOP.

Do not start Phase 19.
```

---

# 26. Independent Phase 18 review prompt

Run this in a fresh Codex/Cursor session after the human local scenario inspection passes.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 18.

Do NOT implement Phase 19.
Do NOT inspect row-level private competition data.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 18
4. PHASE_18_COMPETITION_CONTRACT.md
5. src/task2b/scenario.py
6. src/task2b/scenario_summary.py
7. scripts/inspect_task2b_scenario.py
8. configs/task2b_scenario.yaml
9. docs/task2b_scenario_spec.md
10. tests/test_task2b_scenario.py
11. tests/test_task2b_scenario_summary.py
12. relevant common schema/IO utilities
13. .gitignore
14. .cursorignore if present

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 18 SCENARIO INSPECTION: <PASS/FAIL>
S1 ORDER KEY UNIQUE: <YES/NO>
S1 ORDERS DEPOT = PELIYAGODA: <YES/NO>
AVAILABLE FLEET FILTER: <PASS/FAIL>
WORKSHOP VEHICLES IN USABLE FLEET: <number>
VEHICLE REFERENCE COVERAGE: <PASS/FAIL>
DISTRICT TRAVEL COVERAGE: <PASS/FAIL>
SERVICE ALLOWANCE COVERAGE: <PASS/FAIL>
BRAND SUMMARY RECONCILIATION: <PASS/FAIL>
DISTRICT SUMMARY RECONCILIATION: <PASS/FAIL>

Do not ask the human for private rows.

AUDIT ALL TASKS:

DT-254:
orders loaded through canonical IO, order_ref validated, outlet_id not used as unique key.

DT-255:
fleet schema/status validated.

DT-256:
vehicle reference unique and covers scenario fleet.

DT-257:
district-travel reference coverage correct.

DT-258:
service allowance keyed by brand+dock_type and complete.

DT-259:
S1 filter explicit and deterministic.

DT-260:
only available vehicles enter available fleet.

DT-261:
in_workshop vehicles cannot appear in usable fleet.

DT-262:
Peliyagoda scenario/home-depot contract is correct and non-Peliyagoda vehicles are not relabeled.

DT-263:
brand summaries reconcile.

DT-264:
district summaries reconcile.

DT-265:
chilled demand correctly defined from temp_requirement.

DT-266:
van-only demand correctly defined from parking_constraint and chilled+van-only intersection summarized.

DT-267:
weight summaries valid.

DT-268:
volume summaries valid.

DT-269:
deferred_yesterday only treated as a descriptive/priority signal, not automatic service.

DT-270:
days_since_last_served is validated and summarized without creating priority weights.

GLOBAL AUDIT:

- official feasibility rules documented accurately
- return journey explicitly excluded from later trip formula
- Fresh budget 270 documented
- Style+Tech combined budget 480 documented
- maximum two trips documented
- order_ref is canonical key
- checker PASS != optimality documented
- no compatibility matrix implemented prematurely
- no trip grouping/time engine implemented prematurely
- no optimizer implemented
- no Task 1 changes
- no Task 2A changes
- private output paths ignored
- no private row output

RUN SAFE TESTS:

pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py
pytest -q
python -m pip check
git status
git diff --check

Do not run real private-data inspection.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

ORDER KEY CONTRACT:
PASS / FAIL

SCENARIO FILTER:
PASS / FAIL

AVAILABLE/WORKSHOP CONTRACT:
PASS / FAIL

PELIYAGODA DEPOT CONTRACT:
PASS / FAIL

REFERENCE COVERAGE:
PASS / FAIL

SUMMARY RECONCILIATION:
PASS / FAIL

OFFICIAL RULE LEDGER:
PASS / FAIL

PHASE-SCOPE DISCIPLINE:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN LOCAL INSPECTION:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-254: PASS/FAIL
DT-255: PASS/FAIL
DT-256: PASS/FAIL
DT-257: PASS/FAIL
DT-258: PASS/FAIL
DT-259: PASS/FAIL
DT-260: PASS/FAIL
DT-261: PASS/FAIL
DT-262: PASS/FAIL
DT-263: PASS/FAIL
DT-264: PASS/FAIL
DT-265: PASS/FAIL
DT-266: PASS/FAIL
DT-267: PASS/FAIL
DT-268: PASS/FAIL
DT-269: PASS/FAIL
DT-270: PASS/FAIL

PHASE 18 REVIEW:
PASS / FAIL

READY FOR PHASE 19:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 19.
```

---

# 27. Completion record

```markdown
# Phase 18 Completion Record

## Tasks

- [ ] DT-254
- [ ] DT-255
- [ ] DT-256
- [ ] DT-257
- [ ] DT-258
- [ ] DT-259
- [ ] DT-260
- [ ] DT-261
- [ ] DT-262
- [ ] DT-263
- [ ] DT-264
- [ ] DT-265
- [ ] DT-266
- [ ] DT-267
- [ ] DT-268
- [ ] DT-269
- [ ] DT-270

## Agent stage

- Synthetic tests: PASS / FAIL
- Full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- S1 inspection: PASS / FAIL
- order_ref unique: YES / NO
- available fleet valid: YES / NO
- workshop usable count: 0 / nonzero
- Peliyagoda contract: PASS / FAIL
- vehicle coverage: PASS / FAIL
- district travel coverage: PASS / FAIL
- service allowance coverage: PASS / FAIL
- brand reconciliation: PASS / FAIL
- district reconciliation: PASS / FAIL

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- private rows exposed to AI: NO

## Review

- Independent review: PASS / FAIL

## Verdict

PHASE 18 STATUS: PASS / FAIL
READY FOR PHASE 19: YES / NO
```

---

# 28. Final Phase 18 checklist

Before Phase 19:

- [ ] `order_ref` is unique and canonical.
- [ ] duplicate outlet IDs are allowed.
- [ ] S1 is explicitly filtered.
- [ ] S1 is confirmed as Peliyagoda.
- [ ] available fleet is isolated.
- [ ] workshop vehicles are excluded.
- [ ] every scenario vehicle has a vehicle reference.
- [ ] every order district has district-travel coverage.
- [ ] every order brand+dock pair has service-allowance coverage.
- [ ] brand demand summary reconciles.
- [ ] district demand summary reconciles.
- [ ] chilled demand is summarized.
- [ ] van-only demand is summarized.
- [ ] chilled+van-only subset is summarized.
- [ ] weight demand is summarized.
- [ ] volume demand is summarized.
- [ ] previous deferrals are summarized.
- [ ] `days_since_last_served` is summarized.
- [ ] official feasibility rules are frozen in docs.
- [ ] official trip formula is frozen in docs.
- [ ] no return journey is documented.
- [ ] Fresh 270-minute budget is documented.
- [ ] Style+Tech 480-minute budget is documented.
- [ ] max two trips is documented.
- [ ] checker feasibility vs optimality distinction is documented.
- [ ] no compatibility matrix exists yet.
- [ ] no trip-time engine exists yet.
- [ ] no optimizer exists yet.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.
- [ ] tests pass.
- [ ] local inspection passes.
- [ ] independent review passes.

Only then:

```text
PHASE 18 STATUS: PASS
READY FOR PHASE 19: YES
```
