# PHASE 20 — Task 2B Trip Calculation Engine

> **Filename:** `PHASE_20_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 20 — Task 2B Trip Calculation Engine  
> **Task range:** **DT-284 → DT-292**  
> **Task count:** **9**  
> **Default phase priority:** P0  
> **Master dependency:** Phase 18  
> **Recommended execution dependency:** Phase 18 must pass; Phase 19 outputs may be reused for later linkage but are not required to define the official trip-time arithmetic.  
> **Phase gate:** The official Task 2B trip-minute formula is implemented exactly and unit-tested against the official booklet example.  
> **Execution style:** Deterministic trip-group validation + exact reference joins + exact arithmetic + unit tests.  
> **Do not implement Phase 21 prioritization, Phase 22 optimization, or Phase 23 final allocation validation in this phase.**

---

# 1. Purpose of Phase 20

Phase 20 builds the canonical **Task 2B trip-time calculation engine**.

The challenge defines a trip as a set of orders assigned to the same:

```text
vehicle_id + trip_id
```

and requires every order on that trip to share the same:

```text
brand
district
```

This phase implements the exact arithmetic needed to answer:

> If a proposed trip contains these specific orders, how many Task 2B minutes does that trip consume under the official rules?

The answer must be computed from exactly three components:

```text
outbound district travel
+
inter-stop travel
+
handling time
```

This phase must prove:

- orders in a candidate trip share one brand and one district;
- outbound travel is counted exactly once;
- inter-stop travel is counted `n_orders - 1` times;
- handling allowance is looked up per order from `brand + dock_type`;
- all handling allowances are summed;
- total trip minutes are the exact sum of the three components;
- **no return leg is added**;
- the official Gampaha example evaluates to **101 minutes**.

This phase is deliberately separated from optimization.

It must not yet decide:

- which orders should be served;
- which orders should be deferred;
- which vehicle receives which trip;
- how trips should be prioritized;
- whether a candidate trip is optimal;
- how to search all possible trip subsets;
- solver variables;
- final allocation;
- final `submission_task2b.csv`.

---

# 2. Finalized Phase 20 task inventory

The WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-284** | [O] | P0 | DT-254–DT-270 | Group candidate trips by brand + district |
| [ ] | **DT-285** | [O] | P0 | Phase 18 | Calculate outbound district travel |
| [ ] | **DT-286** | [O] | P0 | Phase 18 | Calculate inter-stop travel |
| [ ] | **DT-287** | [O] | P0 | Phase 18 | Join brand+dock service allowance |
| [ ] | **DT-288** | [O] | P0 | Phase 18 | Calculate total handling allowance |
| [ ] | **DT-289** | [O] | P0 | DT-284–DT-288 | Calculate exact trip minutes |
| [ ] | **DT-290** | [O] | P0 | Phase 18 | Do not add return leg |
| [ ] | **DT-291** | [E] | P0 | Phase 18 | Build trip-time unit tests |
| [ ] | **DT-292** | [O] | P0 | Phase 18 | Validate example from official booklet |

**Phase complete:** [ ]  
**READY FOR PHASE 21:** NO

---

# 3. Official Task 2B trip-time contract

The official booklet states:

> Each trip leaves the depot, travels to one district, and delivers its orders there.

For Task 2B, the trip duration contains only:

1. outbound travel from depot to that district;
2. travel between stops;
3. handling/service allowance at all stops.

The official rule explicitly says:

```text
DO NOT add the return journey to the depot
```

because the daily time budgets already allow for it.

---

# 4. Official exact formula

For a valid candidate trip containing `n` orders:

```text
trip_minutes
=
outbound_minutes
+
inter_stop_minutes
+
handling_minutes
```

where:

```text
outbound_minutes
=
depot_to_district_freeflow_min
```

counted exactly once.

```text
inter_stop_minutes
=
inter_stop_freeflow_min * (n_orders - 1)
```

and:

```text
handling_minutes
=
sum(service_allowance_min for each order)
```

with each service allowance looked up using:

```text
trip brand + order dock_type
```

Because all orders in a valid trip must share the same brand, using the row's own brand must produce the same trip brand.

---

# 5. Official booklet example — mandatory test

The official example is:

```text
Brand:
Fresh

District:
Gampaha

Orders:
3

Dock types:
rear_dock
rear_dock
street
```

Reference values:

```text
depot_to_district_freeflow_min = 37

inter_stop_freeflow_min = 9

Fresh + rear_dock service allowance = 15

Fresh + street service allowance = 16
```

Calculation:

```text
outbound
= 37

inter-stop
= 9 * (3 - 1)
= 18

handling
= 15 + 15 + 16
= 46

trip total
= 37 + 18 + 46
= 101 minutes
```

The engine must reproduce:

```text
101
```

exactly under normal integer reference values.

---

# 6. Additional official example — recommended secondary test

The booklet also gives:

```text
Fresh
Colombo
4 street-access stops
```

with:

```text
outbound = 24

inter-stop = 8 * (4 - 1)
           = 24

handling = 4 * 16
         = 64

trip total
= 24 + 24 + 64
= 112 minutes
```

Then:

```text
101 + 112 = 213 Fresh minutes
```

for two Fresh trips on one vehicle.

This second example is recommended as an extra regression test.

The actual **270-minute Fresh budget enforcement** belongs later to the optimizer/validator phases.

Do not turn this secondary example into Phase 20 vehicle assignment logic.

---

# 7. Official daily budgets — document now, enforce later

The challenge defines:

```text
Fresh trips combined per vehicle:
<= 270 minutes
```

and:

```text
Style + Tech trips combined per vehicle:
<= 480 minutes
```

These are separate windows.

A vehicle may run, for example:

```text
one Fresh trip
+
one Style trip
```

and those are checked against their respective budget groups.

But:

```text
each vehicle may still run at most two trips total
```

Phase 20 must document these facts.

Phase 20 does not need to assign trips to vehicles or aggregate per-vehicle time budgets yet.

That belongs to Phases 22–23.

---

# 8. Scope distinction: candidate trip pool vs actual candidate trip

To avoid premature optimization, Phase 20 uses two different concepts.

## 8.1 Brand+district pool

A **trip pool** is:

```text
all S1 orders sharing one brand + one district
```

This implements DT-284 as a deterministic grouping of orders into pools that could potentially contribute to the same trip.

A pool is **not automatically one feasible trip**.

A pool may be too large for:

- vehicle weight capacity;
- vehicle volume capacity;
- daily time budget;
- available trip slots.

Do not interpret:

```text
brand+district pool
```

as:

```text
final trip
```

---

## 8.2 Explicit candidate trip

An **explicit candidate trip** is a specified nonempty subset of order references from exactly one brand+district pool.

The trip-time engine accepts such an explicit candidate and calculates its exact minutes.

Later phases may create candidate subsets for optimization.

Phase 20 should **not enumerate all subsets** of every pool.

That can be combinatorially explosive and belongs to later optimization design.

---

# 9. Canonical Phase 20 data sources

Reuse Phase 18 canonical validated data:

```text
S1 orders
district_travel reference
service_allowance reference
```

Phase 20 does not require vehicle compatibility to calculate trip minutes.

Therefore Phase 19 output is not a hard arithmetic dependency.

However, later phases will combine:

```text
Phase 19 compatibility
+
Phase 20 trip-time engine
```

to build feasible allocations.

Do not change Phase 18 source semantics.

---

# 10. Recommended repository additions

Create/update:

```text
src/task2b/trip_groups.py
src/task2b/trip_time.py

scripts/build_task2b_trip_time_context.py

configs/task2b_trip_time.yaml

docs/task2b_trip_time_spec.md

tests/test_task2b_trip_groups.py
tests/test_task2b_trip_time.py
```

Reuse:

```text
src/task2b/scenario.py
src/task2b/scenario_summary.py
configs/task2b_scenario.yaml
```

Do not create production optimization code yet:

```text
priority.py
optimizer.py
validator.py
submission.py
```

---

# 11. Recommended private outputs

Private/local-only:

```text
data/interim/task2b_brand_district_pools.csv
data/interim/task2b_order_service_allowances.csv
```

Recommended private reports:

```text
reports/private/phase20_task2b_trip_time/
├── build_summary.json
├── pool_summary.csv
├── travel_reference_validation.json
├── service_allowance_validation.json
├── full_pool_time_diagnostics.csv
├── official_example_validation.json
├── warnings.json
└── phase20_trip_time_report.md
```

The optional:

```text
full_pool_time_diagnostics.csv
```

may treat every order in one brand+district pool as a hypothetical single trip **only to exercise arithmetic**.

It must be labeled clearly:

```text
NOT A FEASIBILITY DECISION
NOT A FINAL TRIP
```

because capacity and vehicle assignment are not evaluated here.

---

# 12. Recommended configuration

Create:

```text
configs/task2b_trip_time.yaml
```

Recommended:

```yaml
version: 1

scenario:
  expected_id: S1
  expected_depot: Peliyagoda

trip_grouping:
  required_same_brand: true
  required_same_district: true
  reject_empty_trip: true
  reject_duplicate_order_ref_within_trip: true

district_travel:
  outbound_column: depot_to_district_freeflow_min
  inter_stop_column: inter_stop_freeflow_min

service_allowance:
  keys:
    - brand
    - dock_type
  value_column: service_allowance_min

formula:
  outbound_count_per_trip: 1
  inter_stop_multiplier: n_orders_minus_one
  include_return_leg: false
  rounding: none

numeric:
  tolerance: 1.0e-9

reports:
  private_output_dir: reports/private/phase20_task2b_trip_time
```

The value:

```text
include_return_leg: false
```

is a hard official rule.

The application must reject a configuration that tries to set it to true.

---

# 13. Canonical data structures

Recommended immutable conceptual objects.

## TripPool

```text
scenario
brand
district
order_refs
order_count
```

Optional diagnostics:

```text
total_weight_kg
total_volume_m3
dock_type_counts
```

This is not a final trip.

---

## CandidateTrip

Recommended input shape:

```text
candidate_trip_id
scenario
order_refs
```

The calculator resolves the corresponding orders and validates:

```text
nonempty
unique order_refs
one brand
one district
```

No vehicle ID is required for pure time arithmetic.

---

## TripTimeBreakdown

Recommended output:

```text
candidate_trip_id

brand
district
order_count

outbound_minutes
inter_stop_minutes
handling_minutes

trip_minutes

return_minutes_added
```

Hard requirement:

```text
return_minutes_added = 0
```

Optional:

```text
service_allowance_rows_matched
```

Do not include final served/deferred decisions.

---

# 14. Detailed task specifications

---

## DT-284 — Group candidate trips by brand + district

### Objective

Create canonical S1 trip pools keyed by:

```text
brand
district
```

because the official rule requires every order on a single trip to share both.

### Input

Canonical Phase 18:

```text
orders_s1
```

### Required output

One summary row per unique:

```text
brand + district
```

with at least:

```text
scenario
brand
district
order_count
total_weight_kg
total_volume_m3
```

Recommended private-only member reference list:

```text
order_refs
```

Do not place real order lists in tracked docs.

### Important interpretation

This task does **not** mean every pool is a valid single trip.

Do not label a pool:

```text
trip_id = 1
```

or assign a vehicle.

### Candidate-trip validator

Also implement:

```text
validate_candidate_trip_orders(...)
```

which requires an explicit candidate trip to contain:

```text
one brand
one district
```

### Tests

- one brand+district pool;
- multiple districts split;
- multiple brands split;
- duplicate outlets remain separate orders;
- candidate with mixed brand rejected;
- candidate with mixed district rejected;
- empty candidate rejected;
- duplicate order_ref inside candidate rejected;
- source order table unmodified.

### STOP

If Phase 20 silently mixes brands or districts.

---

## DT-285 — Calculate outbound district travel

### Objective

Implement official Step 1.

### Rule

For one candidate trip:

```text
outbound_minutes
=
depot_to_district_freeflow_min
```

from the trip's district reference row.

Count exactly once per trip.

### Important

Do not multiply outbound by number of orders.

For a trip with:

```text
1 order
10 orders
```

outbound is still counted once.

### Reference handling

Use the Phase 18-approved district travel grain.

If the table is depot-specific, use the correct:

```text
depot + district
```

reference rather than collapsing it to district only.

Scenario S1 depot is Peliyagoda.

### Validation

Outbound value must be:

```text
numeric
finite
>= 0
```

### Tests

- one-order trip;
- multi-order trip;
- same outbound both cases;
- missing district reference fails;
- duplicate applicable reference fails;
- negative/nonfinite travel fails.

---

## DT-286 — Calculate inter-stop travel

### Objective

Implement official Step 2.

### Rule

```text
inter_stop_minutes
=
inter_stop_freeflow_min
*
(n_orders - 1)
```

### Boundaries

For:

```text
n_orders = 1
```

then:

```text
inter_stop_minutes = 0
```

For:

```text
n_orders = 2
```

then:

```text
inter_stop_minutes = one inter-stop allowance
```

For:

```text
n_orders = 3
```

then:

```text
two inter-stop journeys
```

### Invalid

```text
n_orders = 0
```

must fail because an empty trip is not a valid trip.

### Important

Do not calculate inter-stop travel based on:

```text
outlet count
```

if distinct orders can share the same outlet.

The official formula uses:

```text
number of orders
```

Therefore:

```text
n_orders = len(order_refs)
```

not:

```text
n_unique_outlets
```

### Tests

- n=1 → 0;
- n=2 → 1×reference;
- n=3 → 2×reference;
- repeated outlet IDs still count as separate orders;
- empty trip rejected;
- negative/nonfinite reference rejected.

---

## DT-287 — Join brand+dock service allowance

### Objective

Implement the official per-order handling lookup.

### Official lookup

For each order:

```text
brand + dock_type
→ service_allowance_min
```

### Trip-brand consistency

A valid trip already has one brand.

Still validate:

```text
every order.brand == trip.brand
```

### Required output

At order level:

```text
order_ref
brand
dock_type
service_allowance_min
```

private/interim only.

### Join requirements

Use:

```text
many_to_one
```

semantics from orders to the validated service-allowance reference.

Do not use:

```text
dock_type alone
```

because allowance depends on brand + dock type.

### Missing pair

Hard fail.

Do not:

```text
fill 0
use median
use another brand's allowance
```

### Tests

- same dock, different brand can map to different allowance;
- duplicate valid order rows each get an allowance;
- missing brand+dock fails;
- duplicate allowance key fails;
- zero allowance allowed if official source permits nonnegative zero;
- negative/nonfinite allowance fails.

---

## DT-288 — Calculate total handling allowance

### Objective

Implement official Step 3.

### Rule

```text
handling_minutes
=
sum(service_allowance_min for all orders in candidate trip)
```

### Important

Do not:

- use mean allowance;
- use maximum allowance;
- count only unique dock types;
- count only unique outlets.

Every order/stop contributes its allowance.

If multiple orders share the same outlet and are represented as distinct Task 2B orders on the same candidate trip, the Phase 20 engine follows the official order-count interpretation unless the official source explicitly says otherwise.

Do not silently merge them.

### Tests

- single order;
- repeated same dock type;
- mixed dock types;
- repeated outlet IDs;
- exact sum;
- no rounding.

---

## DT-289 — Calculate exact trip minutes

### Objective

Implement the canonical calculation.

### Formula

```text
trip_minutes
=
outbound_minutes
+
inter_stop_minutes
+
handling_minutes
```

### Recommended pure function

```python
calculate_trip_time(candidate_orders, district_travel_ref, service_allowance_ref)
    -> TripTimeBreakdown
```

### Required validation before calculation

Candidate must be:

```text
nonempty
unique order_ref
one scenario
one brand
one district
```

All references must be matched.

### Output

```text
outbound_minutes
inter_stop_minutes
handling_minutes
trip_minutes
return_minutes_added
```

with:

```text
return_minutes_added = 0
```

### No hidden components

Do not add:

```text
loading time
depot reload time
traffic multiplier
road disruption
driver break
parking delay
window waiting
return-to-depot time
fuel time
```

unless official Task 2B formula explicitly contains them.

It does not.

### Tests

- component sum;
- deterministic order-insensitivity;
- one-order trip;
- many-order trip;
- exact decimal arithmetic within tolerance;
- no hidden component.

---

## DT-290 — Do not add return leg

### Objective

Protect against one of the easiest Task 2B formula mistakes.

### Official rule

```text
return trip to depot is NOT added
```

The daily budgets already allow for it.

### Implementation requirements

Do not create formula like:

```text
2 * depot_to_district_freeflow_min
```

Do not add:

```text
return_minutes
```

from district reference.

Recommended hard configuration validation:

```text
include_return_leg must equal false
```

If configuration says:

```text
true
```

fail immediately.

### Regression test

Construct:

```text
outbound = 30
interstop = 10
handling = 20
```

Expected:

```text
trip_minutes = 60
```

Not:

```text
90
```

### Static/code review guard

The Phase 20 review should search for suspicious logic such as:

```text
2 * outbound
outbound + return
round_trip
```

within Phase 20 calculation code.

False positives can be reviewed manually.

---

## DT-291 — Build trip-time unit tests

### Objective

Create a comprehensive test suite before later solver integration.

Create:

```text
tests/test_task2b_trip_groups.py
tests/test_task2b_trip_time.py
```

### Required categories

#### Group validation

- same brand/district accepted;
- mixed brand rejected;
- mixed district rejected;
- empty rejected;
- duplicate `order_ref` rejected;
- repeated `outlet_id` allowed.

#### Outbound

- counted once;
- missing ref fails;
- invalid ref fails.

#### Inter-stop

- one order = zero;
- two orders = one leg;
- three orders = two legs;
- repeated outlet still counted by orders.

#### Service allowance

- `brand + dock_type` lookup;
- multiple dock types;
- missing pair fail;
- duplicate reference fail.

#### Handling

- exact per-order sum;
- no unique-dock collapse;
- no unique-outlet collapse.

#### Total

- exact component sum;
- no return;
- deterministic under order reordering.

#### Official examples

- Gampaha = 101;
- recommended Colombo = 112.

#### Phase-scope tests

- no served/deferred decision;
- no vehicle assignment;
- no optimizer dependency required by pure trip-time module.

### Required behavior

Tests must use synthetic data and official-example constants only.

Do not require real private scenario rows.

---

## DT-292 — Validate example from official booklet

### Objective

Encode the official example as a mandatory regression test and optional local validation artifact.

### Required fixture

Candidate trip:

```text
brand = Fresh
district = Gampaha
3 orders
dock types:
rear_dock
rear_dock
street
```

References:

```text
Gampaha outbound = 37
Gampaha inter-stop = 9

Fresh + rear_dock = 15
Fresh + street = 16
```

Expected breakdown:

```text
outbound_minutes = 37
inter_stop_minutes = 18
handling_minutes = 46
return_minutes_added = 0
trip_minutes = 101
```

### Hard assertion

```text
trip_minutes == 101
```

for integer fixture values.

### Recommended secondary assertion

Colombo example:

```text
outbound = 24
inter_stop = 8
4 Fresh street orders
service allowance = 16 each

trip_minutes = 112
```

And documented:

```text
101 + 112 = 213 Fresh minutes
```

but do not implement the 270-minute vehicle budget checker here unless it already exists as a pure non-optimization helper and is explicitly kept outside Phase 20 DoD.

Recommended: defer budget enforcement.

---

# 15. Optional Phase 20 diagnostic: full brand+district pool time

For the private real-data run, it is useful to exercise the engine on each complete:

```text
brand + district
```

pool.

For each pool, calculate:

```text
if all orders were hypothetically treated as one trip:
outbound
inter-stop
handling
trip minutes
```

This is only a **formula diagnostic**.

It is not a claim of feasibility.

Each row must be labeled:

```text
diagnostic_only = true
capacity_checked = false
vehicle_assigned = false
time_budget_checked = false
```

Do not feed this directly into the final solver as a pre-approved trip.

---

# 16. Numeric policy

All minutes must be treated as numeric.

Requirements:

```text
finite
>= 0
```

No rounding in core arithmetic.

If source minutes are integer, exact integer results should remain exact.

If floating values exist, compare with a tight tolerance.

Recommended:

```text
abs(a - b) <= 1e-9
```

for synthetic floating tests.

Do not use:

```text
ceil
floor
round
```

unless the official source explicitly requires it.

---

# 17. Data lineage requirements

Every `TripTimeBreakdown` should be traceable to:

```text
trip brand
trip district
order count

district travel reference row
service allowance lookup(s)
```

For private diagnostics, optionally include:

```text
district_reference_key
service_allowance_match_count
```

Do not place real order lists in tracked documentation.

---

# 18. Invariants

Phase 20 must enforce all of the following.

## Candidate structure

```text
n_orders >= 1
```

```text
order_ref unique within candidate trip
```

```text
one brand
```

```text
one district
```

## Outbound

```text
outbound_minutes
==
exactly one district outbound value
```

## Inter-stop

```text
inter_stop_minutes
==
inter_stop_reference * (n_orders - 1)
```

## Handling

```text
handling_minutes
==
sum(per-order service allowances)
```

## Total

```text
trip_minutes
==
outbound_minutes
+
inter_stop_minutes
+
handling_minutes
```

## Return

```text
return_minutes_added
==
0
```

---

# 19. Edge cases

## One-order trip

Valid.

```text
inter-stop = 0
```

Outbound still counted once.

Handling still counted once.

---

## Empty trip

Invalid.

Do not return zero minutes for an empty trip.

There is no Task 2B trip without orders.

---

## Multiple orders at same outlet

`outlet_id` may repeat across official orders.

The official formula uses number of orders and per-order allowances.

Therefore Phase 20 counts each order unless the official challenge explicitly says otherwise.

Do not collapse them by outlet.

---

## Mixed brand

Invalid trip.

Reject.

Do not split automatically inside the calculator.

---

## Mixed district

Invalid trip.

Reject.

Do not calculate multiple outbound components inside one "trip".

---

## Same brand + district but mixed temperature/access

Trip-time arithmetic is still mathematically definable.

Whether one vehicle can legally carry all of those orders is a Phase 19/22 compatibility issue.

Phase 20 should not reject a trip only because temperature/access differs unless the calculator is explicitly called in a "feasibility-enforced" later wrapper.

Pure trip-time engine validates brand+district, not vehicle compatibility.

---

## Service allowance missing for one order

Hard fail.

Do not calculate a partial handling total.

---

## Travel reference missing

Hard fail.

Do not infer a district travel value.

---

## Zero inter-stop reference

Valid if official reference provides zero.

---

## Zero service allowance

Valid if official reference provides zero.

---

## Zero outbound

Valid if official reference permits it.

Do not force positive unless the official data contract requires positive.

Phase 18 validates nonnegative.

---

# 20. Phase 20 outputs

Tracked code/config/docs:

```text
src/task2b/trip_groups.py
src/task2b/trip_time.py
scripts/build_task2b_trip_time_context.py
configs/task2b_trip_time.yaml
docs/task2b_trip_time_spec.md
tests/test_task2b_trip_groups.py
tests/test_task2b_trip_time.py
```

Private interim:

```text
data/interim/task2b_brand_district_pools.csv
data/interim/task2b_order_service_allowances.csv
```

Private reports:

```text
reports/private/phase20_task2b_trip_time/**
```

---

# 21. Required local report contents

Recommended:

```text
phase20_trip_time_report.md
```

Sections:

## Official formula

Exactly document:

```text
trip_minutes =
outbound
+
inter_stop * (n_orders - 1)
+
sum(service allowance)
```

with no return.

## Reference coverage

```text
district travel coverage
service allowance coverage
```

## Pool summary

Number of:

```text
brand+district pools
```

without private row-level details in console.

## Official example

Show only the public booklet example:

```text
37 + 18 + 46 = 101
```

## Scope statement

Explicitly state:

```text
No capacity allocation performed.
No vehicle assignment performed.
No priority policy performed.
No optimizer performed.
```

---

# 22. Tests to run

At minimum:

```bash
pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_trip_groups.py \
  tests/test_task2b_trip_time.py
```

If Phase 19 exists and passes, also run:

```bash
pytest -q \
  tests/test_task2b_compatibility.py \
  tests/test_task2b_scarcity.py
```

Then:

```bash
pytest -q
python -m pip check
```

Codex may fix normal implementation failures automatically.

Do not change official formulas to make tests pass.

---

# 23. Phase 20 STOP conditions

`READY FOR PHASE 21` remains **NO** if:

- Phase 18 has not passed;
- candidate-trip grouping allows mixed brand;
- candidate-trip grouping allows mixed district;
- empty trip is accepted;
- duplicate `order_ref` appears in one candidate trip;
- outbound is counted more than once;
- outbound is multiplied by number of orders;
- inter-stop uses `n_orders` instead of `n_orders - 1`;
- inter-stop uses unique outlet count instead of order count;
- service allowance joins on dock type only;
- service allowance is averaged instead of summed;
- handling collapses repeated orders/outlets;
- missing travel reference is imputed;
- missing service allowance is imputed;
- return journey is added;
- hidden time components are added;
- the official 101-minute example fails;
- Phase 20 starts assigning orders to vehicles;
- Phase 20 starts served/deferred decisions;
- Phase 20 introduces priority weights;
- Phase 20 enumerates a combinatorially large trip search without later-phase approval;
- optimizer/solver code is added;
- Task 1 artifacts change;
- Task 2A artifacts change;
- private competition rows must be exposed to an external agent;
- tests fail;
- local trip-time context build fails;
- independent review fails.

---

# 24. Definition of Done

Phase 20 passes only when:

- [ ] DT-284 PASS
- [ ] DT-285 PASS
- [ ] DT-286 PASS
- [ ] DT-287 PASS
- [ ] DT-288 PASS
- [ ] DT-289 PASS
- [ ] DT-290 PASS
- [ ] DT-291 PASS
- [ ] DT-292 PASS
- [ ] brand+district pools are deterministic
- [ ] explicit candidate trip validates one brand
- [ ] explicit candidate trip validates one district
- [ ] empty trip fails
- [ ] duplicate order within trip fails
- [ ] outbound counted once
- [ ] inter-stop exactly `n_orders - 1`
- [ ] repeated outlet orders still count as orders
- [ ] service allowance lookup is `brand + dock_type`
- [ ] one service allowance per order
- [ ] total handling is exact sum
- [ ] exact total formula implemented
- [ ] no return leg
- [ ] no undocumented time component
- [ ] official 101-minute example passes
- [ ] recommended 112-minute example passes
- [ ] unit tests are synthetic/public-example based
- [ ] no allocation/optimizer logic added
- [ ] full safe test suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] Task 1 remains frozen
- [ ] Task 2A remains frozen
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 20 STATUS: PASS
READY FOR PHASE 21: YES
```

---

# 25. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-20-task2b-trip-time
```

Recommended commits:

```text
feat(task2b): add brand district trip pools
feat(task2b): implement official trip time formula
test(task2b): add exact trip time regression tests
docs(task2b): document no-return Task 2B time contract
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q tests/test_task2b_trip_groups.py tests/test_task2b_trip_time.py
pytest -q
python -m pip check
```

Ensure none are staged:

```text
data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
```

Merge only after:

```text
LOCAL PHASE 20 TRIP-TIME BUILD: PASS
INDEPENDENT PHASE 20 REVIEW: PASS
```

---

# 26. Recommended Codex model

Recommended:

```text
GPT-5.6 Terra
Reasoning: High
```

Why:

- exact contract arithmetic;
- multiple reference joins;
- strict phase boundaries;
- enough cross-file logic to justify High reasoning;
- no optimizer yet.

Lower-cost option:

```text
GPT-5.6 Terra
Reasoning: Medium
```

is acceptable if the codebase is already stable.

Escalate only for a difficult cross-file bug:

```text
GPT-5.6 Sol
Reasoning: Medium
```

---

# 27. Local private-data command

Codex should implement but not execute on private competition rows:

```bash
python scripts/build_task2b_trip_time_context.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --pool-output data/interim/task2b_brand_district_pools.csv \
  --allowance-output data/interim/task2b_order_service_allowances.csv \
  --report-dir reports/private/phase20_task2b_trip_time
```

PowerShell one-line:

```powershell
python scripts/build_task2b_trip_time_context.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --scenario-config configs/task2b_scenario.yaml --trip-time-config configs/task2b_trip_time.yaml --pool-output data/interim/task2b_brand_district_pools.csv --allowance-output data/interim/task2b_order_service_allowances.csv --report-dir reports/private/phase20_task2b_trip_time
```

Recommended sanitized local summary:

```text
LOCAL PHASE 20 TRIP-TIME BUILD: PASS
BRAND+DISTRICT POOLS: PASS
DISTRICT TRAVEL COVERAGE: PASS
SERVICE ALLOWANCE COVERAGE: PASS
OUTBOUND FORMULA: PASS
INTER-STOP FORMULA: PASS
HANDLING FORMULA: PASS
NO RETURN LEG: PASS
OFFICIAL 101-MIN EXAMPLE: PASS
RECOMMENDED 112-MIN EXAMPLE: PASS
```

---

# 28. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 20 only.

PHASE:
Task 2B Trip Calculation Engine

TASK RANGE:
DT-284 through DT-292

EXECUTION MODE:
High-integrity deterministic implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Terra — High reasoning

LOWER-COST OPTION:
GPT-5.6 Terra — Medium reasoning

ESCALATE ONLY IF NECESSARY:
GPT-5.6 Sol — Medium reasoning

You MAY:

- create/edit/refactor Phase 20 tracked code
- create/edit config/docs
- create synthetic fixtures
- run targeted tests
- run full safe test suite
- inspect stack traces
- fix ordinary implementation defects
- rerun tests
- run python -m pip check
- inspect git status/diff
- verify ignored paths
- self-review against Phase 20 DoD

Do NOT stop for routine coding failures that can safely be fixed.

STOP only for:

- official rule ambiguity
- private-data requirement
- Phase 18 contract failure
- district/service reference ambiguity
- need to invent a time component not present in the booklet
- conflict with the exact official formula
- scope pressure to implement optimization early

DO NOT START PHASE 21.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 20 only
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_20_COMPETITION_CONTRACT.md
6. src/task2b/scenario.py
7. configs/task2b_scenario.yaml
8. official Task 2B rule documentation already tracked
9. common IO/validation helpers
10. existing Task 2B tests

If Phase 19 exists, read only the compatibility interfaces needed to
avoid duplicate semantics. Do not make Phase 19 a hard arithmetic
dependency unless the repository architecture already requires it.

TASK 1 AND TASK 2A ARE FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
outputs/submission_task2a.csv

==================================================
PRIVATE DATA
==================================================

Do NOT inspect or print row-level real competition data from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures and public booklet example values for all
Codex-run tests.

The human will run the real Phase 20 context build locally.

==================================================
OFFICIAL TRIP CONTRACT
==================================================

A Task 2B trip contains orders sharing:

same brand
same district

Exact formula:

trip_minutes
=
outbound_minutes
+
inter_stop_minutes
+
handling_minutes

OUTBOUND:

depot_to_district_freeflow_min

counted ONCE per trip.

INTER-STOP:

inter_stop_freeflow_min
*
(n_orders - 1)

HANDLING:

sum(
    service_allowance_min
    for every order
)

Each service allowance is looked up by:

brand + dock_type

RETURN LEG:

DO NOT ADD IT.

The official budgets already allow for return.

No extra hidden time components.

==================================================
OFFICIAL EXAMPLE
==================================================

Mandatory regression fixture:

Fresh
Gampaha
3 orders

dock types:

rear_dock
rear_dock
street

References:

outbound = 37

inter_stop = 9

Fresh+rear_dock = 15

Fresh+street = 16

Expected:

outbound = 37

inter-stop =
9 * (3-1)
= 18

handling =
15 + 15 + 16
= 46

trip total =
37 + 18 + 46
= 101

MANDATORY ASSERTION:

trip_minutes == 101

Recommended second official example:

Fresh
Colombo
4 street stops

24 + (8 * 3) + (16 * 4)
=
112

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/trip_groups.py

src/task2b/trip_time.py

scripts/build_task2b_trip_time_context.py

configs/task2b_trip_time.yaml

docs/task2b_trip_time_spec.md

tests/test_task2b_trip_groups.py

tests/test_task2b_trip_time.py

Do NOT create priority/optimizer/submission production logic.

==================================================
DT-284 — BRAND + DISTRICT TRIP POOLS
==================================================

Group S1 orders by:

brand
district

Create deterministic pool summaries.

At minimum:

scenario
brand
district
order_count
total_weight_kg
total_volume_m3

Private-only member list may contain order_refs.

IMPORTANT:

A brand+district pool is NOT automatically one feasible trip.

Do NOT:

assign vehicle
assign trip_id
declare served
declare capacity feasible

Also implement explicit candidate-trip validator.

Candidate trip must have:

>= 1 order

unique order_ref

one brand

one district

Mixed brand:
FAIL.

Mixed district:
FAIL.

Empty:
FAIL.

==================================================
DT-285 — OUTBOUND TRAVEL
==================================================

For one valid candidate trip:

outbound_minutes =
depot_to_district_freeflow_min

Count ONCE.

Do NOT multiply by number of orders.

Use the Phase 18-approved applicable travel-reference key.

For S1 the depot is Peliyagoda.

Missing/duplicate applicable reference:
FAIL.

Travel must be finite and >=0.

==================================================
DT-286 — INTER-STOP TRAVEL
==================================================

Formula:

inter_stop_minutes
=
inter_stop_freeflow_min
*
(n_orders - 1)

n=1:
0

n=2:
one inter-stop leg

n=3:
two inter-stop legs

Use number of ORDERS.

Do NOT use number of unique outlets.

Multiple official orders may share one outlet_id.

Empty trip:
FAIL.

==================================================
DT-287 — SERVICE ALLOWANCE JOIN
==================================================

For EVERY order in candidate trip:

lookup:

brand + dock_type
→ service_allowance_min

Do not join by dock_type alone.

Use many-to-one semantics.

Every pair must match exactly one reference.

Missing pair:
FAIL.

Duplicate reference pair:
FAIL.

Do not impute.

==================================================
DT-288 — TOTAL HANDLING
==================================================

handling_minutes
=
sum(
  per-order service_allowance_min
)

Count every order.

Do NOT:

take mean

take max

count unique dock types

count unique outlets

collapse duplicate outlet IDs

No rounding.

==================================================
DT-289 — EXACT TRIP MINUTES
==================================================

Implement pure deterministic calculator.

Recommended result:

brand
district
order_count

outbound_minutes
inter_stop_minutes
handling_minutes

trip_minutes

return_minutes_added

Hard invariant:

trip_minutes
=
outbound
+
inter_stop
+
handling

return_minutes_added = 0

Do not add:

loading
reload
parking delay
window waiting
traffic multiplier
road multiplier
fuel time
driver break
return journey

unless the official Task 2B source explicitly adds them.

It does not.

==================================================
DT-290 — NO RETURN LEG
==================================================

Protect this as a hard rule.

Config:

include_return_leg = false

If a config tries:

true

reject it.

Do not implement:

2 * outbound

outbound + return

round-trip distance/time

Regression fixture:

outbound = 30
inter-stop = 10
handling = 20

Expected:
60

Not:
90

==================================================
DT-291 — UNIT TEST SUITE
==================================================

Create broad synthetic/public-example tests.

GROUPING:

same brand/district accepted

mixed brand rejected

mixed district rejected

empty rejected

duplicate order_ref rejected

duplicate outlet_id allowed

OUTBOUND:

counted once

not multiplied by n

missing ref fails

INTER-STOP:

1 order -> 0

2 orders -> 1 leg

3 orders -> 2 legs

repeated outlet still counts by order

SERVICE ALLOWANCE:

brand+dock exact lookup

same dock under different brands may differ

missing pair fails

duplicate key fails

HANDLING:

exact per-order sum

repeated dock types counted per order

repeated outlet IDs counted per order

TOTAL:

component sum

no return

order-reordering invariance

OFFICIAL EXAMPLES:

Gampaha = 101

Colombo = 112

SCOPE:

no served/deferred decision

no vehicle assignment

no optimizer dependency

==================================================
DT-292 — OFFICIAL BOOKLET EXAMPLE
==================================================

Encode as mandatory test:

Fresh / Gampaha / 3 orders

rear_dock
rear_dock
street

outbound 37

inter-stop 9

allowances:

15
15
16

Expected:

outbound 37

inter-stop 18

handling 46

return 0

total 101

Hard assert total == 101.

Also recommended:

Colombo 4 street stops = 112.

==================================================
CONFIGURATION
==================================================

Create:

configs/task2b_trip_time.yaml

Require:

same brand = true

same district = true

reject empty = true

reject duplicate order_ref = true

outbound counted once

inter-stop rule = n_orders_minus_one

service allowance keys = brand + dock_type

include_return_leg = false

rounding = none

private report path

If include_return_leg != false:
FAIL.

==================================================
OPTIONAL REAL-DATA DIAGNOSTIC
==================================================

For the human local run only, you may calculate one hypothetical
"all orders in this brand+district pool" time for each pool.

This is arithmetic-only.

Label:

diagnostic_only = true

capacity_checked = false

vehicle_assigned = false

time_budget_checked = false

Do not call it a final trip.

==================================================
INVARIANTS
==================================================

Candidate:

nonempty

unique order_ref

one brand

one district

Outbound:

exactly one outbound reference

Inter-stop:

reference * (n_orders - 1)

Handling:

sum one allowance per order

Total:

outbound + inter-stop + handling

Return:

zero

==================================================
TEST / DEBUG LOOP
==================================================

After grouping:
run trip-group tests.

After outbound/inter-stop/allowance:
run component tests.

After total/no-return:
run formula tests.

After official example:
run complete Phase 20 tests.

Fix ordinary bugs automatically.

Run:

pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_trip_groups.py \
  tests/test_task2b_trip_time.py

If Phase 19 exists/passes also run:

tests/test_task2b_compatibility.py
tests/test_task2b_scarcity.py

Then:

pytest -q

python -m pip check

git status

git diff

git diff --check

If private real data is needed:

do not inspect inside Codex.

Return the local human command.

Ensure no private data/report files are staged.

==================================================
LOCAL HUMAN COMMAND
==================================================

Implement but do NOT execute private data inside Codex:

python scripts/build_task2b_trip_time_context.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --pool-output data/interim/task2b_brand_district_pools.csv \
  --allowance-output data/interim/task2b_order_service_allowances.csv \
  --report-dir reports/private/phase20_task2b_trip_time

Console output must be sanitized.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase 18 not passing

mixed-brand trip accepted

mixed-district trip accepted

empty trip accepted

duplicate order_ref inside trip accepted

outbound counted more than once

outbound multiplied by n_orders

inter-stop uses n_orders instead of n_orders-1

unique outlet count used instead of order count

service allowance joined by dock only

handling averaged instead of summed

orders collapsed by outlet

missing reference imputed

return leg added

hidden time components added

official 101-minute example fails

priority logic added

served/deferred logic added

vehicle assignment added

optimizer logic added

Task 1 changes

Task 2A changes

private rows must be exposed

tests cannot pass under official contract

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-284 READY
DT-285 READY
DT-286 READY
DT-287 READY
DT-288 READY
DT-289 READY
DT-290 READY
DT-291 READY
DT-292 READY

brand+district grouping correct

candidate validation strict

outbound once

inter-stop n-1

allowance join brand+dock

handling exact sum

total exact

return zero

101 example passes

112 example passes

no allocation

no prioritization

no optimizer

safe tests pass

pip check passes

private paths ignored

Task 1 unchanged

Task 2A unchanged

no Phase 21 production implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
20 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-284 READY / FAIL
DT-285 READY / FAIL
DT-286 READY / FAIL
DT-287 READY / FAIL
DT-288 READY / FAIL
DT-289 READY / FAIL
DT-290 READY / FAIL
DT-291 READY / FAIL
DT-292 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

BRAND+DISTRICT GROUPING:
PASS / FAIL

OUTBOUND TRAVEL:
PASS / FAIL

INTER-STOP TRAVEL:
PASS / FAIL

SERVICE ALLOWANCE JOIN:
PASS / FAIL

HANDLING TOTAL:
PASS / FAIL

EXACT TRIP MINUTES:
PASS / FAIL

RETURN LEG ADDED:
MUST BE NO

OFFICIAL 101-MIN EXAMPLE:
PASS / FAIL

RECOMMENDED 112-MIN EXAMPLE:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 20 trip-time context command.

PHASE 20 STATUS:
AWAITING LOCAL TRIP-TIME BUILD

READY FOR PHASE 21:
NO

Then STOP.

Do not start Phase 21.
```

---

# 29. Independent Phase 20 review prompt

Use a fresh Codex/Cursor session after the human local run passes.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 20.

Do NOT implement Phase 21.
Do NOT inspect private row-level competition data.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 20
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_20_COMPETITION_CONTRACT.md
6. src/task2b/trip_groups.py
7. src/task2b/trip_time.py
8. scripts/build_task2b_trip_time_context.py
9. configs/task2b_trip_time.yaml
10. docs/task2b_trip_time_spec.md
11. tests/test_task2b_trip_groups.py
12. tests/test_task2b_trip_time.py
13. .gitignore
14. .cursorignore if present

If Phase 19 has passed, optionally inspect only its public interfaces
to verify no duplicate compatibility semantics were introduced.

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 20 TRIP-TIME BUILD: <PASS/FAIL>
BRAND+DISTRICT POOLS: <PASS/FAIL>
DISTRICT TRAVEL COVERAGE: <PASS/FAIL>
SERVICE ALLOWANCE COVERAGE: <PASS/FAIL>
OUTBOUND FORMULA: <PASS/FAIL>
INTER-STOP FORMULA: <PASS/FAIL>
HANDLING FORMULA: <PASS/FAIL>
NO RETURN LEG: <PASS/FAIL>
OFFICIAL 101-MIN EXAMPLE: <PASS/FAIL>
RECOMMENDED 112-MIN EXAMPLE: <PASS/FAIL>

Do not ask for private pool/order rows.

AUDIT EVERY TASK:

DT-284:
group pools by brand+district, explicit candidate must be homogeneous,
no final trips assigned.

DT-285:
outbound reference counted exactly once.

DT-286:
inter-stop = reference × (n_orders - 1),
using order count, not unique outlet count.

DT-287:
service allowance lookup exactly brand+dock_type.

DT-288:
handling sums one allowance per order.

DT-289:
trip total exactly outbound + inter-stop + handling.

DT-290:
no return journey is added anywhere in the formula/config.

DT-291:
unit tests cover boundaries, missing refs, repeated outlets, exact sum,
no return, official examples.

DT-292:
official Gampaha example returns exactly 101.

GLOBAL AUDIT:

- no hidden loading/parking/wait/traffic/road/fuel/break components
- no served/deferred decision
- no vehicle assignment
- no priority policy
- no optimizer
- no combinatorial trip enumeration
- official 270/480 budgets documented for later phases only
- Task 1 unchanged
- Task 2A unchanged
- private output ignored
- no private IDs printed

RUN SAFE TESTS:

pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py tests/test_task2b_trip_groups.py tests/test_task2b_trip_time.py

If Phase 19 exists and passes, also run:
pytest -q tests/test_task2b_compatibility.py tests/test_task2b_scarcity.py

Then:
pytest -q
python -m pip check
git status
git diff --check

Do not run the real private-data build.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

TRIP GROUP CONTRACT:
PASS / FAIL

OUTBOUND:
PASS / FAIL

INTER-STOP:
PASS / FAIL

SERVICE ALLOWANCE:
PASS / FAIL

HANDLING:
PASS / FAIL

EXACT TOTAL:
PASS / FAIL

NO RETURN:
PASS / FAIL

OFFICIAL 101-MIN EXAMPLE:
PASS / FAIL

UNIT TEST COVERAGE:
PASS / FAIL

PHASE-SCOPE DISCIPLINE:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN LOCAL BUILD:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-284: PASS/FAIL
DT-285: PASS/FAIL
DT-286: PASS/FAIL
DT-287: PASS/FAIL
DT-288: PASS/FAIL
DT-289: PASS/FAIL
DT-290: PASS/FAIL
DT-291: PASS/FAIL
DT-292: PASS/FAIL

PHASE 20 REVIEW:
PASS / FAIL

READY FOR PHASE 21:
YES / NO

If FAIL:
list exact blockers only.

Do not automatically fix.
Do not start Phase 21.
```

---

# 30. Completion record template

```markdown
# Phase 20 Completion Record

## Tasks

- [ ] DT-284
- [ ] DT-285
- [ ] DT-286
- [ ] DT-287
- [ ] DT-288
- [ ] DT-289
- [ ] DT-290
- [ ] DT-291
- [ ] DT-292

## Agent stage

- trip-group tests: PASS / FAIL
- trip-time tests: PASS / FAIL
- official-example test: PASS / FAIL
- full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- context build: PASS / FAIL
- pool grouping: PASS / FAIL
- district reference coverage: PASS / FAIL
- service allowance coverage: PASS / FAIL
- outbound formula: PASS / FAIL
- inter-stop formula: PASS / FAIL
- handling formula: PASS / FAIL
- no return: PASS / FAIL
- 101-minute example: PASS / FAIL

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- private rows exposed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 20 STATUS: PASS / FAIL
READY FOR PHASE 21: YES / NO
```

---

# 31. Final Phase 20 checklist

Before Phase 21:

- [ ] Phase 18 passed.
- [ ] Phase 19, if completed, remains compatible and unchanged.
- [ ] brand+district pool grouping is deterministic.
- [ ] candidate trip must contain at least one order.
- [ ] candidate trip has unique order refs.
- [ ] candidate trip has one brand.
- [ ] candidate trip has one district.
- [ ] outbound travel is counted once.
- [ ] inter-stop uses exactly `n_orders - 1`.
- [ ] duplicate outlet IDs are not collapsed.
- [ ] service allowance is joined by `brand + dock_type`.
- [ ] every order contributes one handling allowance.
- [ ] handling is summed exactly.
- [ ] total is outbound + inter-stop + handling.
- [ ] return journey is never added.
- [ ] no hidden time components exist.
- [ ] official Gampaha result is 101.
- [ ] recommended Colombo result is 112.
- [ ] 270/480 budgets are documented for later enforcement.
- [ ] no vehicle assignment was created.
- [ ] no served/deferred decisions were created.
- [ ] no priority weights were created.
- [ ] no optimizer was created.
- [ ] tests pass.
- [ ] local context build passes.
- [ ] independent review passes.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.

Only then:

```text
PHASE 20 STATUS: PASS
READY FOR PHASE 21: YES
```
