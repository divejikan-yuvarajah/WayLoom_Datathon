# PHASE 19 — Task 2B Compatibility Engine

> **Filename:** `PHASE_19_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 19 — Task 2B Compatibility Engine  
> **Task range:** **DT-271 → DT-283**  
> **Task count:** **13**  
> **Default phase priority:** P1  
> **Dependency:** Phase 18  
> **Phase gate:** Every S1 order has a validated compatible-vehicle set and every individually impossible order is identified before any trip grouping or optimization begins.  
> **Execution style:** Deterministic hard-rule compatibility filtering + scarcity diagnostics.  
> **Do not implement trip grouping/time calculation, priority scoring, optimization, or final allocation in this phase.**

---

# 1. Purpose

Phase 19 converts the validated Scenario S1 inputs from Phase 18 into a **canonical order-to-vehicle compatibility engine**.

This phase answers:

- Which available Peliyagoda vehicles could legally carry each order **by themselves**?
- Which vehicles satisfy refrigeration requirements?
- Which vehicles satisfy `van_only` access?
- Which vehicles satisfy home-depot rules?
- Which vehicles can physically fit the complete order by both weight and volume?
- Which orders have no compatible vehicle at all and are therefore **individually impossible to serve**?
- Which orders have only one or a few compatible vehicles and therefore consume scarce resources?
- How scarce are reefers?
- How scarce are reefer vans?
- What does compatibility imply about potential trip-slot pressure?

The output of Phase 19 is **compatibility and scarcity information**.

It is **not** yet an allocation.

A vehicle being compatible with an order means only:

> The vehicle is individually capable of carrying that order under the Phase 19 hard filters.

It does **not** mean:

- that the order is selected to be served;
- that the order can share a trip with another order;
- that a feasible trip exists under same-brand/same-district rules;
- that the vehicle has enough remaining capacity after other orders are added;
- that trip time fits the vehicle’s Fresh or Style+Tech time budget;
- that the vehicle still has one of its two trip slots available.

Those later constraints belong to Phases 20–23.

---

# 2. Official Task 2B compatibility rules used in this phase

The official challenge requires the following hard rules. Phase 19 implements the **order-level compatibility subset** of them.

## 2.1 Refrigeration

Official rule:

```text
temp_requirement = chilled
→ vehicle.temp must be reefer
```

A reefer may carry ambient orders.

Therefore:

```text
chilled + reefer = allowed
chilled + ambient vehicle = forbidden
ambient + reefer = allowed
ambient + ambient vehicle = allowed
```

Do not reserve reefers for chilled orders in the hard compatibility engine.

Resource reservation is a later optimization/policy decision.

---

## 2.2 Vehicle access

Official rule:

```text
parking_constraint = van_only
→ vehicle.type must be van
```

Therefore:

```text
van_only + van = allowed
van_only + truck = forbidden
```

For orders that are not `van_only`, do not invent additional access restrictions unless the official data contract explicitly defines them.

---

## 2.3 Home depot

Official rule:

> A vehicle may serve only outlets assigned to its own depot.

Scenario S1 is Peliyagoda.

Phase 18 should already have established the usable candidate fleet as:

```text
scenario = S1
status = available
vehicle home depot = Peliyagoda
```

Phase 19 must still enforce depot compatibility defensively at the pair level.

Never relabel a vehicle’s home depot.

---

## 2.4 Whole-order individual fit

Official whole-order rule:

> A served order must be assigned to one vehicle and one trip; orders cannot be split.

Therefore an order can only be compatible with a vehicle if the **entire order** fits that vehicle individually.

Weight condition:

```text
order_weight_kg <= vehicle.weight_cap_kg
```

Volume condition:

```text
order_volume_m3 <= vehicle.volume_cap_m3
```

Both must be true.

Do not divide a large order across two vehicles to manufacture compatibility.

---

# 3. Official rules documented but not fully implemented in Phase 19

The remaining hard rules still matter, but they require trip context.

## Same brand + same district per trip

Orders sharing:

```text
vehicle_id + trip_id
```

must share one brand and one district.

This belongs to trip grouping / optimization later.

Phase 19 may carry brand and district into the compatibility table for future joins, but must not group trips yet.

---

## Max two trips per vehicle

Official limit:

```text
<= 2 trips per vehicle
```

A compatibility pair does not consume a trip slot yet.

Do not remove a vehicle from an order’s compatibility set merely because some other order may use it later.

---

## Time budgets

Official vehicle-level time budgets:

```text
Fresh trips combined <= 270 minutes

Style + Tech trips combined <= 480 minutes
```

Phase 19 does not yet know final trip groups.

Do not calculate these budgets here.

---

# 4. Source hierarchy

When implementing Phase 19, use:

1. official Challenge Booklet;
2. official Task 2B input/reference files;
3. approved WayLoom master inventory;
4. approved Phase 18 scenario contract and code;
5. this Phase 19 contract;
6. engineering assumptions.

If the real official files contradict an engineering assumption:

```text
STOP
```

Do not silently repair or reinterpret.

---

# 5. Phase 19 canonical task registry

| Status | Task | Mark | Priority | Work item |
|---|---|---:|---:|---|
| [ ] | **DT-271** | [O] | P0 | Generate order-to-vehicle compatibility matrix |
| [ ] | **DT-272** | [O] | P0 | Enforce refrigeration compatibility |
| [ ] | **DT-273** | [O] | P0 | Enforce van-only compatibility |
| [ ] | **DT-274** | [O] | P0 | Enforce vehicle home depot |
| [ ] | **DT-275** | [O] | P0 | Check whether each order fits a vehicle by weight |
| [ ] | **DT-276** | [O] | P0 | Check whether each order fits a vehicle by volume |
| [ ] | **DT-277** | [O] | P0 | Identify orders individually impossible to serve |
| [ ] | **DT-278** | [E] | P1 | Count compatible vehicles per order |
| [ ] | **DT-279** | [E] | P1 | Calculate vehicle scarcity |
| [ ] | **DT-280** | [E] | P1 | Identify reefer bottleneck |
| [ ] | **DT-281** | [E] | P1 | Identify reefer-van bottleneck |
| [ ] | **DT-282** | [E] | P1 | Identify trip-slot bottlenecks |
| [ ] | **DT-283** | [E] | P1 | Produce Task 2B scarcity report |

**Phase complete:** [ ]  
**READY FOR PHASE 20:** NO

---

# 6. Required repository additions

Create/update:

```text
src/task2b/compatibility.py
src/task2b/scarcity.py

scripts/build_task2b_compatibility.py

configs/task2b_compatibility.yaml

docs/task2b_compatibility_spec.md

tests/test_task2b_compatibility.py
tests/test_task2b_scarcity.py
```

Reuse:

```text
src/task2b/scenario.py
src/task2b/scenario_summary.py
configs/task2b_scenario.yaml
```

Do **not** create production implementations yet for:

```text
trip_time.py
priority.py
optimizer.py
validator.py
submission.py
```

unless an empty placeholder already exists.

---

# 7. Private Phase 19 outputs

Recommended local-only artifacts:

```text
data/interim/task2b_compatibility_matrix.csv
data/interim/task2b_order_compatibility_summary.csv
data/interim/task2b_vehicle_scarcity_summary.csv
```

Private reports:

```text
reports/private/phase19_task2b_compatibility/
├── build_summary.json
├── compatibility_rule_counts.json
├── impossible_orders_summary.json
├── order_compatibility_counts.csv
├── vehicle_scarcity.csv
├── reefer_bottleneck.json
├── reefer_van_bottleneck.json
├── trip_slot_pressure.json
├── warnings.json
└── phase19_scarcity_report.md
```

Do not commit these.

Do not print real `order_ref` lists or vehicle/order pairs to the AI agent.

---

# 8. Recommended configuration

Create:

```text
configs/task2b_compatibility.yaml
```

Suggested structure:

```yaml
version: 1

scenario:
  expected_id: S1
  expected_depot: Peliyagoda

orders:
  key: order_ref
  chilled_value: chilled
  van_only_value: van_only

fleet:
  usable_status: available

vehicles:
  key: vehicle_id
  van_type_value: van
  reefer_temp_value: reefer

compatibility:
  enforce_refrigeration: true
  enforce_van_only: true
  enforce_home_depot: true
  enforce_individual_weight_fit: true
  enforce_individual_volume_fit: true

  require_all_rules_true: true

scarcity:
  low_compatible_vehicle_threshold: 2
  singleton_compatible_vehicle_threshold: 1

  trip_slot_capacity_per_vehicle: 2

reports:
  private_output_dir: reports/private/phase19_task2b_compatibility
```

The scarcity thresholds above are **WayLoom diagnostics**, not official feasibility rules.

Keep them configurable and clearly labeled as engineering summaries.

---

# 9. Canonical compatibility grain

The compatibility table grain must be exactly:

```text
one row per:
order_ref + vehicle_id
```

for the Phase 18 usable candidate fleet.

Recommended keys:

```text
scenario
order_ref
vehicle_id
```

Since Phase 19 operates only S1, `scenario` may be carried for traceability.

Required uniqueness:

```text
(order_ref, vehicle_id)
```

must be unique.

Never build compatibility at:

```text
outlet_id + vehicle_id
```

because an outlet may have multiple distinct orders.

---

# 10. Recommended compatibility-table schema

At minimum:

```text
scenario
order_ref
outlet_id
brand
district
order_depot
temp_requirement
parking_constraint
order_weight_kg
order_volume_m3

vehicle_id
vehicle_type
vehicle_temp
vehicle_home_depot
weight_cap_kg
volume_cap_m3

refrigeration_ok
access_ok
home_depot_ok
weight_ok
volume_ok

is_compatible

incompatibility_reason_count
incompatibility_reasons
```

Optional useful fields:

```text
weight_utilization_if_alone
volume_utilization_if_alone
max_utilization_if_alone
```

Those utilization fields are order-level diagnostics only.

Do not confuse them with final trip utilization.

---

# 11. Rule evaluation strategy

For every order × usable vehicle pair, evaluate each rule **independently**.

Recommended:

```text
refrigeration_ok
access_ok
home_depot_ok
weight_ok
volume_ok
```

Then:

```text
is_compatible =
refrigeration_ok
AND access_ok
AND home_depot_ok
AND weight_ok
AND volume_ok
```

Do not short-circuit in a way that hides other failed rules from diagnostics.

For example, if an order fails both refrigeration and volume, record both reasons.

This improves the scarcity report and later explanations.

---

# 12. Incompatibility reason vocabulary

Use stable machine-readable reason codes.

Recommended:

```text
REFRIGERATION_MISMATCH
VAN_ONLY_ACCESS_MISMATCH
HOME_DEPOT_MISMATCH
WEIGHT_EXCEEDS_CAPACITY
VOLUME_EXCEEDS_CAPACITY
```

Do not use free-form prose as the only machine representation.

Recommended:

```text
incompatibility_reasons
```

stored internally as:

```text
list[str]
```

and serialized deterministically when writing CSV.

Order reason codes consistently.

---

# 13. Detailed task specifications

---

## DT-271 — Generate order-to-vehicle compatibility matrix

### Objective

Create the canonical cross-product of:

```text
S1 orders
×
Phase 18 usable candidate vehicles
```

and attach all order/vehicle fields required to evaluate Phase 19 rules.

### Inputs

From Phase 18:

```text
orders_s1
available/home-depot-safe vehicle candidate view
vehicles_ref
```

Use the Phase 18 validated loader rather than rereading files with new semantics.

### Required preconditions

Orders:

```text
order_ref unique
scenario = S1
depot = Peliyagoda
```

Vehicles:

```text
status = available
reference row exists
home-depot interpretation resolved
```

### Cross-product cardinality

If:

```text
O = number of S1 orders
V = number of usable candidate vehicles
```

then before applying pair-level filters:

```text
compatibility candidate row count = O * V
```

Record this privately.

### Important

Do not physically remove incompatible pairs before recording rule outcomes.

Recommended table keeps all candidate pairs with:

```text
is_compatible = true/false
```

This enables diagnostics.

A smaller `compatible_pairs` view may be derived afterward.

### Tests

- exact cross-product row count;
- unique order+vehicle pairs;
- no order dropped;
- no usable vehicle dropped;
- duplicate outlet IDs do not collapse orders;
- source frames unmodified;
- deterministic ordering.

### STOP

If pair uniqueness/cardinality is broken.

---

## DT-272 — Enforce refrigeration compatibility

### Objective

Implement the official chilled → reefer rule.

### Rule

```text
if order.temp_requirement == chilled:
    refrigeration_ok = vehicle.temp == reefer
else:
    refrigeration_ok = True
```

### Important asymmetry

Reefer may carry ambient.

Therefore:

```text
ambient order + reefer vehicle
```

must remain compatible on refrigeration.

Do not implement:

```text
ambient only on ambient vehicles
```

That would incorrectly over-restrict the fleet.

### Invalid source values

If order temperature or vehicle temperature is outside the validated official domain:

```text
FAIL / STOP
```

Do not guess.

### Tests

- chilled + reefer → true;
- chilled + non-reefer → false;
- ambient + reefer → true;
- ambient + non-reefer → true;
- invalid order temp fails;
- invalid vehicle temp fails.

---

## DT-273 — Enforce van-only compatibility

### Objective

Implement official outlet-access compatibility.

### Rule

```text
if order.parking_constraint == van_only:
    access_ok = vehicle.type == van
else:
    access_ok = True
```

### Important

Do not force non-van-only orders onto trucks.

A van may serve a non-van-only order unless some other official rule blocks it.

### Avoid undocumented restrictions

Fields such as:

```text
mall_window
dock_type
delivery windows
```

exist in scenario data, but the official Task 2B seven hard rules do not state an additional Phase 19 vehicle-type restriction based on those fields.

Do not invent one.

### Tests

- van_only + van → true;
- van_only + truck → false;
- normal access + van → true;
- normal access + truck → true;
- invalid parking value follows approved schema policy.

---

## DT-274 — Enforce vehicle home depot

### Objective

Implement the official depot compatibility rule pairwise.

### Rule

```text
home_depot_ok =
vehicle_home_depot == order.depot
```

For S1, expected:

```text
Peliyagoda == Peliyagoda
```

### Defensive reason

Even if Phase 18 already filtered vehicles to Peliyagoda-home vehicles, keep the pair-level check.

This prevents a later regression from accidentally introducing a non-home vehicle.

### Do not

rewrite order depot or vehicle depot.

### Tests

- matching depot → true;
- mismatch → false;
- blank depot fails;
- no auto-normalization beyond approved string normalization.

### STOP

If official depot values cannot be reconciled exactly enough to apply the rule.

---

## DT-275 — Check whether each order fits a vehicle by weight

### Objective

Enforce individual whole-order weight feasibility.

### Rule

```text
weight_ok =
order_weight_kg <= weight_cap_kg
```

Use a documented numeric tolerance only for floating-point representation, not to materially exceed capacity.

Recommended:

```text
epsilon = 1e-9
weight_ok =
order_weight_kg <= weight_cap_kg + epsilon
```

### Boundary

Equal capacity is valid:

```text
order_weight_kg == weight_cap_kg
→ true
```

### Whole-order rule

Do not divide the order.

If one order weighs more than every usable vehicle’s capacity, it may become individually impossible.

### Optional diagnostic

```text
weight_utilization_if_alone =
order_weight_kg / weight_cap_kg
```

### Tests

- below capacity;
- exactly at capacity;
- above capacity;
- tiny floating tolerance;
- no order splitting;
- positive capacities already validated.

---

## DT-276 — Check whether each order fits a vehicle by volume

### Objective

Enforce individual whole-order volume feasibility.

### Rule

```text
volume_ok =
order_volume_m3 <= volume_cap_m3
```

Recommended numeric tolerance:

```text
epsilon = 1e-9
```

### Boundary

Equal volume capacity is valid.

### Optional diagnostic

```text
volume_utilization_if_alone =
order_volume_m3 / volume_cap_m3
```

Recommended:

```text
max_utilization_if_alone =
max(weight_utilization_if_alone,
    volume_utilization_if_alone)
```

### Important

Weight passing does not compensate for volume failure.

Both weight and volume must pass.

### Tests

- below capacity;
- exactly equal;
- above capacity;
- weight-pass/volume-fail pair becomes incompatible;
- volume-pass/weight-fail pair becomes incompatible.

---

## DT-277 — Identify orders individually impossible to serve

### Objective

Identify S1 orders with **zero compatible vehicles** after all Phase 19 hard filters.

For each order:

```text
compatible_vehicle_count =
sum(is_compatible)
```

Then:

```text
individually_impossible =
compatible_vehicle_count == 0
```

### Meaning

An individually impossible order cannot be served under the currently available S1 fleet even as a one-order trip.

This is a hard physical/compatibility finding.

### It is different from

```text
feasible individually but later deferred due to:
trip capacity competition,
trip-slot limits,
time budgets,
priority tradeoffs.
```

Do not call every later deferred order "impossible".

### Diagnostic reasons

For impossible orders, summarize why candidate vehicles failed.

Examples:

```text
all fail refrigeration
all fail van-only access
all fail weight
all fail volume
combinations of failures
```

Do not expose real order IDs in tracked docs.

### Tests

- one compatible vehicle → not impossible;
- zero compatible → impossible;
- impossible because chilled+no reefer;
- impossible because van_only+no van;
- impossible because weight;
- impossible because volume;
- multiple simultaneous reasons.

### STOP

If impossible orders are silently removed from later Task 2B order universe.

They must remain orders and will ultimately be deferred unless official data/logic changes.

---

## DT-278 — Count compatible vehicles per order

### Objective

Quantify flexibility/scarcity for each order.

Required per order:

```text
compatible_vehicle_count
total_usable_vehicle_count
compatible_vehicle_share
```

where:

```text
compatible_vehicle_share =
compatible_vehicle_count / total_usable_vehicle_count
```

if total usable vehicles > 0.

Recommended categories:

```text
IMPOSSIBLE       count = 0
SINGLETON        count = 1
LOW_FLEXIBILITY  count <= configured low threshold
FLEXIBLE         otherwise
```

These categories are engineering diagnostics.

They are not official priority rules.

### Also useful

Break compatible vehicles by:

```text
vehicle_type
vehicle_temp
```

for private diagnostics.

### Tests

- count correctness;
- singleton;
- zero count;
- share correctness;
- zero usable fleet handled as blocker.

---

## DT-279 — Calculate vehicle scarcity

### Objective

Measure how heavily each usable vehicle is demanded by order compatibility.

For each vehicle, calculate at minimum:

```text
compatible_order_count
compatible_chilled_order_count
compatible_van_only_order_count
compatible_chilled_van_only_order_count
```

Recommended diagnostic:

```text
compatibility_load_share =
compatible_order_count / total_S1_orders
```

Also calculate:

```text
exclusive_order_count
```

where an exclusive order is one whose:

```text
compatible_vehicle_count == 1
```

and that vehicle is this vehicle.

### Recommended vehicle scarcity interpretation

A vehicle is operationally scarce when:

- it is the only compatible option for some orders; or
- it belongs to a small specialized fleet type/capability used by many constrained orders.

Do not convert this directly into an allocation objective yet.

### Optional engineering scarcity score

If implemented, keep it diagnostic and transparent.

Example:

```text
vehicle_scarcity_score =
exclusive_order_count * 10
+
compatible_chilled_van_only_order_count * 3
+
compatible_chilled_order_count
```

However, because Phase 21 owns the actual priority/objective design, the safest Phase 19 default is:

> report raw scarcity indicators rather than freeze a weighted score.

### Tests

- compatible-order count;
- exclusive-order count;
- specialized counts;
- vehicle with no compatible orders;
- deterministic ranking.

---

## DT-280 — Identify reefer bottleneck

### Objective

Quantify chilled-demand dependence on reefer vehicles.

### Official basis

Chilled orders require reefer vehicles.

### Required scenario metrics

At minimum:

```text
available_reefer_vehicle_count
chilled_order_count
chilled_total_weight_kg
chilled_total_volume_m3

chilled_orders_with_1_compatible_vehicle
chilled_orders_with_2_or_fewer_compatible_vehicles
chilled_individually_impossible_count
```

Recommended:

```text
reefer_vehicle_ids_private_only
compatible_chilled_orders_per_reefer
exclusive_chilled_orders_per_reefer
```

### Important limitation

Do not claim:

```text
reefer capacity is sufficient for the day
```

from Phase 19 compatibility alone.

A reefer might individually fit many orders but later fail:

- trip grouping;
- combined trip capacity;
- trip-slot limit;
- time budget.

Therefore wording should be:

```text
order-level reefer compatibility pressure
```

not:

```text
final fleet sufficiency
```

### Tests

- no chilled orders;
- chilled with multiple reefers;
- chilled singleton;
- chilled impossible;
- ambient compatibility does not consume a hard reservation.

---

## DT-281 — Identify reefer-van bottleneck

### Objective

Quantify orders requiring the intersection of:

```text
chilled
+
van_only
```

Official consequence:

```text
vehicle.temp = reefer
AND
vehicle.type = van
```

### Required metrics

```text
available_reefer_van_count

chilled_van_only_order_count
chilled_van_only_total_weight_kg
chilled_van_only_total_volume_m3

chilled_van_only_singleton_count
chilled_van_only_impossible_count
```

For each reefer van privately:

```text
compatible_chilled_van_only_order_count
exclusive_chilled_van_only_order_count
```

### Why important

Reefer vans are a specialized intersection resource.

But Phase 19 must not yet "reserve" a specific reefer van for a specific order.

That is a later allocation decision.

### Tests

- reefer van qualifies;
- reefer truck fails van-only access;
- ambient van fails chilled refrigeration;
- no reefer vans;
- singleton reefer-van order;
- impossible chilled+van-only order.

---

## DT-282 — Identify trip-slot bottlenecks

### Objective

Create an **order-level lower-bound/pressure diagnostic** related to the official maximum of two trips per vehicle.

This task must remain diagnostic because Phase 19 does not yet form trips.

### Official fact

Each available vehicle can run at most:

```text
2 trips
```

### Safe Phase 19 diagnostic

Compute:

```text
usable_vehicle_count
theoretical_trip_slot_upper_bound =
2 * usable_vehicle_count
```

This is only a structural upper bound.

It does not guarantee those slots can serve any particular order.

Also compute compatibility-constrained slot indicators.

Recommended by order class:

```text
chilled-compatible vehicle count
van-compatible vehicle count
reefer-van-compatible vehicle count

corresponding theoretical compatible trip-slot upper bound =
2 * compatible vehicle count
```

### Brand+district group diagnostic

Since final trips must contain one brand + one district, calculate the number of nonempty order groups:

```text
unique brand+district groups
```

and privately summarize group demand.

But do **not** claim one group equals one trip.

A brand+district group may require multiple trips because of:

- capacity;
- time;
- access/temperature splits;
- whole-order combinations.

### Optional lower bound

You may calculate a conservative **minimum number of trips implied by individual group weight/volume totals** only if it is mathematically valid and clearly documented.

However, because heterogeneous vehicle capacities complicate this and Phase 20/22 will calculate actual trips, the recommended Phase 19 default is:

```text
do not freeze a trip-count lower bound from aggregate capacity
```

Instead report:

```text
number of brand+district groups
number of orders with <=1 compatible vehicle
number with <=2 compatible vehicles
theoretical max fleet trip slots
specialized-resource trip-slot upper bounds
```

### Tests

- max trip-slot upper bound = 2 × usable vehicles;
- zero usable fleet blocker;
- brand+district group count;
- no accidental trip construction;
- no claim that group count equals required trips.

---

## DT-283 — Produce Task 2B scarcity report

### Objective

Produce a private, decision-support report that Phase 21 can use when defining priority policy and Phase 22 can use when debugging solver behavior.

### Required sections

## A. Scenario/fleet recap

```text
S1 order count
usable vehicle count
workshop vehicle count
Peliyagoda vehicle count
```

## B. Compatibility health

```text
total candidate pairs
compatible pair count
compatible pair share

orders impossible
orders singleton
orders low-flexibility
orders flexible
```

## C. Failure-reason summary

Count pair failures by:

```text
REFRIGERATION_MISMATCH
VAN_ONLY_ACCESS_MISMATCH
HOME_DEPOT_MISMATCH
WEIGHT_EXCEEDS_CAPACITY
VOLUME_EXCEEDS_CAPACITY
```

Also summarize impossible-order reason patterns.

## D. Reefer pressure

Required DT-280 metrics.

## E. Reefer-van pressure

Required DT-281 metrics.

## F. Vehicle scarcity

For each vehicle privately:

```text
compatible_order_count
exclusive_order_count
specialized-compatible counts
```

Tracked docs should not contain real vehicle/order lists unless authorized.

## G. Trip-slot pressure

Required DT-282 diagnostics.

## H. Implications for later phases

Use cautious language:

```text
Phase 21 should consider preserving scarce specialized vehicles.
Phase 22 must still prove trip capacity/time feasibility.
Compatibility count alone is not an allocation priority.
```

Do not finalize priority weights.

### Required private files

At minimum:

```text
phase19_scarcity_report.md
build_summary.json
compatibility_rule_counts.json
impossible_orders_summary.json
reefer_bottleneck.json
reefer_van_bottleneck.json
trip_slot_pressure.json
warnings.json
```

### Definition of report quality

The report must distinguish:

```text
hard incompatibility
```

from:

```text
scarcity diagnostic
```

from:

```text
future optimization decision
```

---

# 14. Compatibility invariants

Before Phase 19 can pass:

## Pair-level

For every pair:

```text
is_compatible
==
refrigeration_ok
AND access_ok
AND home_depot_ok
AND weight_ok
AND volume_ok
```

## Refrigeration

Every compatible chilled pair must have:

```text
vehicle_temp == reefer
```

## Van-only

Every compatible van-only pair must have:

```text
vehicle_type == van
```

## Depot

Every compatible pair must have:

```text
vehicle_home_depot == order_depot
```

## Weight

Every compatible pair must satisfy:

```text
order_weight_kg <= weight_cap_kg + tolerance
```

## Volume

Every compatible pair must satisfy:

```text
order_volume_m3 <= volume_cap_m3 + tolerance
```

## Order coverage

Every S1 order must have exactly one summary row even if:

```text
compatible_vehicle_count = 0
```

## Fleet coverage

Every Phase 18 usable vehicle must appear in the vehicle scarcity summary even if it is compatible with zero orders.

---

# 15. Required synthetic tests

Create:

```text
tests/test_task2b_compatibility.py
tests/test_task2b_scarcity.py
```

Use synthetic fixtures only.

## Cross product

- 3 orders × 4 vehicles = 12 candidate pairs;
- unique `order_ref+vehicle_id`;
- duplicate outlet IDs remain distinct;
- source frames not mutated;
- deterministic order.

## Refrigeration

- chilled + reefer passes;
- chilled + ambient vehicle fails;
- ambient + reefer passes;
- ambient + ambient passes.

## Access

- van_only + van passes;
- van_only + truck fails;
- unrestricted + van passes;
- unrestricted + truck passes.

## Depot

- same depot passes;
- mismatch fails;
- no silent relabeling.

## Weight

- below;
- equal;
- above;
- floating boundary tolerance.

## Volume

- below;
- equal;
- above;
- floating boundary tolerance.

## Combined compatibility

- all true → compatible;
- each individual failure makes incompatible;
- multiple failures recorded;
- deterministic reason-code order.

## Impossible orders

- zero compatible vehicles;
- chilled/no reefer;
- van-only/no van;
- too heavy;
- too large;
- mixed reasons;
- impossible order retained in summary.

## Compatible count

- zero;
- one;
- two;
- many;
- compatible share.

## Vehicle scarcity

- compatible order count;
- exclusive order count;
- specialized counts;
- zero-demand vehicle;
- stable sorting.

## Reefer pressure

- no chilled demand;
- one reefer;
- multiple reefers;
- chilled singleton;
- chilled impossible.

## Reefer-van pressure

- reefer van qualifies;
- reefer truck fails van-only;
- ambient van fails chilled;
- zero reefer vans;
- exclusive specialized order.

## Trip-slot pressure

- theoretical upper bound = 2×usable vehicles;
- group count by brand+district;
- specialized compatible slot count;
- no actual trip rows generated.

## Privacy

- no real IDs printed;
- report writer accepts synthetic data only in tests;
- private paths configured.

---

# 16. Edge cases

## No usable vehicles

This is a hard scenario blocker for compatibility construction.

All orders would have zero compatible vehicles, but the official scenario is expected to provide available vehicles.

Recommended:

```text
STOP
```

rather than pretend Phase 19 succeeded normally.

---

## No reefer vehicles

Allowed as a logical synthetic case.

All chilled orders become individually impossible.

Do not reclassify chilled as ambient.

---

## No vans

All `van_only` orders become individually impossible.

Do not relax access rule.

---

## No reefer vans

All orders that are both:

```text
chilled
AND van_only
```

become impossible unless an official vehicle type/temp representation indicates a qualifying vehicle.

Do not allow reefer trucks into van-only sites.

---

## One order compatible with every vehicle

Valid.

It is highly flexible.

Do not artificially reduce its compatibility set to "save" scarce vehicles.

That belongs to optimization.

---

## One order compatible with only one vehicle

Valid.

Mark as singleton / scarce.

Do not automatically allocate it yet.

---

## Vehicle fits weight but not volume

Incompatible.

---

## Vehicle fits volume but not weight

Incompatible.

---

## Vehicle exactly equals order capacity

Compatible.

---

## Reefer serving ambient

Compatible.

---

## Truck serving non-van-only order

Compatible on access if no other rule blocks it.

---

## Multiple orders at same outlet

Each `order_ref` remains independent.

Do not collapse compatibility by outlet.

---

# 17. Scarcity interpretation principles

Phase 19 diagnostics may inform Phase 21, but must not silently become hard rules.

Use language such as:

```text
scarce
specialized
low flexibility
single compatible vehicle
high compatibility demand
potential bottleneck
```

Avoid:

```text
must serve first
guaranteed to defer
reserve this exact vehicle
optimal allocation
```

unless a later phase proves it.

---

# 18. Phase 19 STOP conditions

`READY FOR PHASE 20` remains **NO** if:

- Phase 18 has not passed;
- usable candidate fleet is undefined;
- `order_ref` is not unique;
- candidate matrix cardinality/uniqueness is wrong;
- refrigeration rule is reversed or over-restrictive;
- ambient orders are incorrectly forbidden from reefers;
- van-only orders can use trucks;
- non-van-only orders are incorrectly forced to trucks;
- home-depot rule is not enforced;
- order splitting is used to manufacture compatibility;
- weight equality at capacity is treated as invalid;
- volume equality at capacity is treated as invalid;
- only one capacity dimension is checked;
- individually impossible orders are dropped;
- compatibility count summary omits zero-compatible orders;
- vehicle scarcity summary omits zero-order vehicles;
- reefer bottleneck is claimed to prove full-day feasibility;
- reefer-van scarcity is confused with final allocation;
- trip-slot diagnostic constructs actual trips prematurely;
- Phase 20 trip-time logic is prematurely implemented;
- Phase 21 priority weights are frozen prematurely;
- optimizer/solver code is introduced;
- Task 1 frozen artifacts are modified;
- Task 2A frozen artifacts are modified;
- private real order/vehicle pair data is exposed to an external AI agent;
- tests fail;
- local Phase 19 build fails;
- independent review fails.

---

# 19. Definition of Done

Phase 19 passes only when:

- [ ] DT-271 PASS
- [ ] DT-272 PASS
- [ ] DT-273 PASS
- [ ] DT-274 PASS
- [ ] DT-275 PASS
- [ ] DT-276 PASS
- [ ] DT-277 PASS
- [ ] DT-278 PASS
- [ ] DT-279 PASS
- [ ] DT-280 PASS
- [ ] DT-281 PASS
- [ ] DT-282 PASS
- [ ] DT-283 PASS
- [ ] compatibility grain is `order_ref + vehicle_id`
- [ ] cross-product cardinality is correct
- [ ] every S1 order appears in order summary
- [ ] every usable vehicle appears in vehicle summary
- [ ] refrigeration logic matches official rule
- [ ] ambient orders may use reefers
- [ ] van-only requires van
- [ ] home depot enforced
- [ ] whole-order individual weight fit enforced
- [ ] whole-order individual volume fit enforced
- [ ] both capacity dimensions required
- [ ] stable incompatibility reason codes exist
- [ ] individually impossible orders identified and retained
- [ ] compatible vehicle counts calculated
- [ ] singleton/low-flexibility diagnostics produced
- [ ] vehicle scarcity diagnostics produced
- [ ] reefer bottleneck summarized
- [ ] reefer-van bottleneck summarized
- [ ] trip-slot pressure diagnostic produced without building trips
- [ ] private scarcity report produced
- [ ] hard rules vs diagnostic scarcity vs later optimization clearly separated
- [ ] no trip-time engine added
- [ ] no priority policy frozen
- [ ] no optimizer added
- [ ] synthetic tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] Task 1 frozen artifacts unchanged
- [ ] Task 2A frozen artifacts unchanged
- [ ] independent review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 19 STATUS: PASS
READY FOR PHASE 20: YES
```

---

# 20. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-19-task2b-compatibility
```

Recommended commits:

```text
feat(task2b): add order vehicle compatibility engine
feat(task2b): enforce Task 2B individual hard compatibility rules
feat(task2b): add impossible-order and scarcity diagnostics
test(task2b): add compatibility and scarcity tests
docs(task2b): document compatibility boundaries and scarcity semantics
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q tests/test_task2b_scenario.py \
          tests/test_task2b_scenario_summary.py \
          tests/test_task2b_compatibility.py \
          tests/test_task2b_scarcity.py

pytest -q

python -m pip check
```

Ensure none of these are staged:

```text
data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
```

Merge only after:

```text
LOCAL PHASE 19 COMPATIBILITY BUILD: PASS
INDEPENDENT PHASE 19 REVIEW: PASS
```

---

# 21. Recommended model for Codex

Phase 19 has more cross-rule logic than Phase 18, but it is still deterministic.

Recommended:

```text
GPT-5.6 Terra
Reasoning: High
```

Escalate if a difficult multi-file bug or schema ambiguity appears:

```text
GPT-5.6 Sol
Reasoning: Medium/High
```

There is no need to use the most expensive model by default.

---

# 22. Local private-data command

Codex should implement, but the human should run locally:

```bash
python scripts/build_task2b_compatibility.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --matrix-output data/interim/task2b_compatibility_matrix.csv \
  --order-summary-output data/interim/task2b_order_compatibility_summary.csv \
  --vehicle-summary-output data/interim/task2b_vehicle_scarcity_summary.csv \
  --report-dir reports/private/phase19_task2b_compatibility
```

PowerShell one-line:

```powershell
python scripts/build_task2b_compatibility.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --scenario-config configs/task2b_scenario.yaml --compatibility-config configs/task2b_compatibility.yaml --matrix-output data/interim/task2b_compatibility_matrix.csv --order-summary-output data/interim/task2b_order_compatibility_summary.csv --vehicle-summary-output data/interim/task2b_vehicle_scarcity_summary.csv --report-dir reports/private/phase19_task2b_compatibility
```

Recommended sanitized console result:

```text
LOCAL PHASE 19 COMPATIBILITY BUILD: PASS
PAIR KEY UNIQUE: YES
REFRIGERATION RULE: PASS
VAN-ONLY RULE: PASS
HOME-DEPOT RULE: PASS
WEIGHT FIT RULE: PASS
VOLUME FIT RULE: PASS
ORDER SUMMARY COVERAGE: PASS
VEHICLE SUMMARY COVERAGE: PASS
IMPOSSIBLE ORDERS IDENTIFIED: YES
REEFER BOTTLENECK ANALYSIS: PASS
REEFER-VAN BOTTLENECK ANALYSIS: PASS
TRIP-SLOT PRESSURE ANALYSIS: PASS
```

Exact counts should remain private unless intentionally disclosed.

---

# 23. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 19 only.

PHASE:
Task 2B Compatibility Engine

TASK RANGE:
DT-271 through DT-283

EXECUTION MODE:
Controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Terra — High reasoning

FALLBACK:
GPT-5.6 Sol — Medium/High reasoning

You MAY:

- create/edit/refactor Phase 19 tracked code
- create/edit configs
- create/edit docs
- create synthetic fixtures
- run targeted tests
- run the complete safe test suite
- inspect tracebacks
- fix ordinary implementation bugs
- rerun failed tests
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against Phase 19 Definition of Done

Do NOT stop for normal coding/test failures that can be safely fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to expose private competition rows
- Phase 18 not passing
- unresolved schema/reference blocker
- compatibility rule conflict with official Task 2B requirements
- need to invent a hard rule not supported by the booklet
- material change outside Phase 19 scope

DO NOT START PHASE 20.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 19
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. src/task2b/scenario.py
7. src/task2b/scenario_summary.py
8. configs/task2b_scenario.yaml
9. docs/task2b_scenario_spec.md
10. existing Task 2B tests
11. common validation/IO utilities

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

Do NOT inspect or print real competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run implementation/tests.

The human operator will run the real Phase 19 compatibility build locally.

Do not print real order_ref values or real order-vehicle pair tables.

==================================================
OFFICIAL PHASE 19 HARD COMPATIBILITY RULES
==================================================

Canonical order key:

order_ref

Compatibility grain:

order_ref + vehicle_id

Start from:

S1 orders
×
Phase 18 usable available Peliyagoda fleet

Then evaluate independently:

refrigeration_ok
access_ok
home_depot_ok
weight_ok
volume_ok

Final:

is_compatible =
all five rule booleans

==================================================
REFRIGERATION
==================================================

Official:

chilled order
→ reefer vehicle required

Reefer may carry ambient.

Therefore:

chilled + reefer = allowed

chilled + non-reefer = forbidden

ambient + reefer = allowed

ambient + non-reefer = allowed

Do not reserve reefer vehicles yet.

==================================================
VAN-ONLY
==================================================

Official:

parking_constraint = van_only
→ vehicle.type = van

Therefore:

van_only + van = allowed

van_only + truck = forbidden

non-van-only + van = allowed

non-van-only + truck = allowed

Do not invent additional access restrictions.

==================================================
HOME DEPOT
==================================================

Official:

vehicle may serve only outlets assigned to its home depot.

Pair rule:

vehicle_home_depot == order_depot

S1 expected:

Peliyagoda

Keep this check even if Phase 18 already filtered the fleet.

==================================================
WEIGHT
==================================================

Whole-order fit:

order_weight_kg <= weight_cap_kg

Equal capacity passes.

Use only a tiny documented floating representation tolerance.

Do not split orders.

==================================================
VOLUME
==================================================

Whole-order fit:

order_volume_m3 <= volume_cap_m3

Equal capacity passes.

Both weight AND volume must be true.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/compatibility.py
src/task2b/scarcity.py

scripts/build_task2b_compatibility.py

configs/task2b_compatibility.yaml

docs/task2b_compatibility_spec.md

tests/test_task2b_compatibility.py
tests/test_task2b_scarcity.py

Do NOT create production:

trip-time grouping engine
priority policy
optimizer
final validator
submission builder

==================================================
DT-271 — COMPATIBILITY MATRIX
==================================================

Build the full candidate cross product:

S1 orders
×
usable candidate vehicles

Before filtering.

If O orders and V usable vehicles:

candidate row count = O * V

Require unique:

order_ref + vehicle_id

Carry required order/vehicle attributes.

Keep all candidate pairs with rule booleans.

Create compatible-only view afterward if needed.

Do not drop incompatible pairs from the diagnostic matrix.

==================================================
DT-272 — REFRIGERATION
==================================================

Implement:

if chilled:
    vehicle_temp must equal reefer
else:
    pass refrigeration

Test all four ambient/chilled × reefer/non-reefer combinations.

Invalid domains fail.

==================================================
DT-273 — VAN-ONLY ACCESS
==================================================

Implement:

if parking_constraint == van_only:
    vehicle_type must equal van
else:
    access passes

Do not force unrestricted orders away from vans.

==================================================
DT-274 — HOME DEPOT
==================================================

Implement pair-level:

vehicle_home_depot == order_depot

Do not rewrite depot strings using unsupported assumptions.

Mismatch → incompatible.

==================================================
DT-275 — WEIGHT FIT
==================================================

Implement whole-order individual fit.

weight_ok =
order_weight_kg <= weight_cap_kg + tiny_tolerance

Equal is valid.

No splitting.

==================================================
DT-276 — VOLUME FIT
==================================================

Implement:

volume_ok =
order_volume_m3 <= volume_cap_m3 + tiny_tolerance

Equal is valid.

Both weight_ok AND volume_ok required.

Optional diagnostics:

weight_utilization_if_alone
volume_utilization_if_alone
max_utilization_if_alone

These are NOT final trip utilization.

==================================================
INCOMPATIBILITY REASONS
==================================================

Use deterministic reason codes:

REFRIGERATION_MISMATCH
VAN_ONLY_ACCESS_MISMATCH
HOME_DEPOT_MISMATCH
WEIGHT_EXCEEDS_CAPACITY
VOLUME_EXCEEDS_CAPACITY

Record all failed reasons for a pair.

Do not hide secondary failures by short-circuiting.

==================================================
DT-277 — INDIVIDUALLY IMPOSSIBLE ORDERS
==================================================

Per order:

compatible_vehicle_count =
number of is_compatible pairs

individually_impossible =
compatible_vehicle_count == 0

Retain impossible orders.

Do not drop them from later Task 2B order universe.

Summarize failure patterns privately.

Differentiate:

individually impossible

from:

feasible individually but later deferred because of shared resource limits.

==================================================
DT-278 — COMPATIBLE VEHICLE COUNT
==================================================

For every order calculate:

compatible_vehicle_count
total_usable_vehicle_count
compatible_vehicle_share

Engineering diagnostic categories:

IMPOSSIBLE
SINGLETON
LOW_FLEXIBILITY
FLEXIBLE

Use configured thresholds.

Do not turn these categories into allocation decisions.

==================================================
DT-279 — VEHICLE SCARCITY
==================================================

For every usable vehicle calculate:

compatible_order_count

compatible_chilled_order_count

compatible_van_only_order_count

compatible_chilled_van_only_order_count

exclusive_order_count

where exclusive means:

order compatible with exactly one vehicle,
and that vehicle is this one.

Prefer raw indicators over an arbitrary weighted scarcity score.

Do not define Phase 21 priority weights here.

==================================================
DT-280 — REEFER BOTTLENECK
==================================================

Report:

available reefer count

chilled order count/weight/volume

chilled singleton count

chilled <=2-compatible count

chilled impossible count

compatible/exclusive chilled order counts by reefer privately

Do NOT claim that order-level compatibility proves full-day time/capacity sufficiency.

==================================================
DT-281 — REEFER-VAN BOTTLENECK
==================================================

For orders:

chilled AND van_only

required vehicle:

reefer AND van

Report:

available reefer-van count

chilled+van-only order count/weight/volume

singleton count

impossible count

compatible/exclusive specialized-order counts per reefer van privately

Do not reserve specific vehicles yet.

==================================================
DT-282 — TRIP-SLOT BOTTLENECK DIAGNOSTIC
==================================================

Official:

max 2 trips per vehicle

Safe diagnostic:

theoretical_trip_slot_upper_bound =
2 * usable_vehicle_count

Also report:

unique brand+district groups

order counts by brand+district

orders with:
0 compatible vehicles
1 compatible vehicle
<=2 compatible vehicles

specialized-resource theoretical compatible slot counts

IMPORTANT:

Do NOT construct actual trips.

Do NOT claim:

number of brand+district groups
=
number of required trips

Capacity/time can require multiple trips.

==================================================
DT-283 — SCARCITY REPORT
==================================================

Generate private report containing:

scenario/fleet recap

compatibility pair summary

impossible orders aggregate

singleton/low-flexibility counts

pair failure-reason counts

reefer pressure

reefer-van pressure

vehicle scarcity indicators

trip-slot pressure

warnings

later-phase implications

Clearly distinguish:

HARD INCOMPATIBILITY

vs

SCARCITY DIAGNOSTIC

vs

FUTURE OPTIMIZATION DECISION

Do not finalize priority weights.

==================================================
INVARIANTS
==================================================

For every pair:

is_compatible
=
refrigeration_ok
AND access_ok
AND home_depot_ok
AND weight_ok
AND volume_ok

Every compatible chilled pair:
vehicle_temp = reefer

Every compatible van_only pair:
vehicle_type = van

Every compatible pair:
vehicle_home_depot = order_depot

Every compatible pair:
order weight <= capacity

Every compatible pair:
order volume <= capacity

Every S1 order:
appears in order summary

Every usable vehicle:
appears in vehicle scarcity summary

==================================================
TESTS
==================================================

Use synthetic fixtures only.

CROSS PRODUCT:

exact O*V rows

unique order+vehicle

duplicate outlet IDs remain distinct

source inputs unmodified

deterministic ordering

REFRIGERATION:

chilled+reefer pass

chilled+ambient vehicle fail

ambient+reefer pass

ambient+ambient pass

ACCESS:

van_only+van pass

van_only+truck fail

unrestricted+van pass

unrestricted+truck pass

DEPOT:

match pass

mismatch fail

WEIGHT:

below/equal/above

floating tolerance

VOLUME:

below/equal/above

weight-pass volume-fail

volume-pass weight-fail

COMBINED:

all true compatible

each failure incompatible

multiple reason codes retained

IMPOSSIBLE:

zero-compatible

chilled no reefer

van_only no van

too heavy

too large

mixed reason

order remains present

COUNTS:

zero
one
two
many
share

VEHICLE SCARCITY:

compatible counts

exclusive counts

specialized counts

zero-order vehicle retained

REEFER:

no chilled
singleton
multiple reefers
impossible

REEFER VAN:

qualifying reefer van
reefer truck fails access
ambient van fails chilled
no qualifying vehicle

TRIP SLOT:

2 * usable vehicles

brand+district group count

no trip rows created

PRIVACY:

no real IDs printed

private outputs ignored

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After matrix/core-rule implementation:

run compatibility tests.

After impossible/count logic:

run order-summary tests.

After scarcity/bottleneck work:

run scarcity tests.

Fix ordinary implementation bugs automatically.

Then run:

pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_compatibility.py \
  tests/test_task2b_scarcity.py

Then:

pytest -q

Then:

python -m pip check

Then:

git status
git diff
git diff --check

If real private data is required:

do not inspect it inside Codex.

Return the exact local human command.

Ensure these remain unstaged/ignored:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL HUMAN COMMAND
==================================================

Implement but do NOT execute against private real data inside Codex:

python scripts/build_task2b_compatibility.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --matrix-output data/interim/task2b_compatibility_matrix.csv \
  --order-summary-output data/interim/task2b_order_compatibility_summary.csv \
  --vehicle-summary-output data/interim/task2b_vehicle_scarcity_summary.csv \
  --report-dir reports/private/phase19_task2b_compatibility

Console summary must be sanitized.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase 18 has not passed

usable fleet undefined

order_ref not unique

matrix pair key not unique

cross-product cardinality wrong

ambient orders incorrectly blocked from reefer

van_only orders allowed on trucks

home depot not enforced

orders split to create compatibility

weight or volume equality incorrectly rejected

only one capacity dimension checked

impossible orders dropped

zero-compatible orders missing from summaries

zero-order vehicles missing from vehicle summary

scarcity diagnostics are converted into hard allocation rules

reefer compatibility is claimed to prove full-day feasibility

actual trips are constructed

trip times are calculated

priority weights are frozen

optimizer code is introduced

Task 1 changes

Task 2A changes

private rows must be exposed

safe tests cannot pass

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-271 READY
DT-272 READY
DT-273 READY
DT-274 READY
DT-275 READY
DT-276 READY
DT-277 READY
DT-278 READY
DT-279 READY
DT-280 READY
DT-281 READY
DT-282 READY
DT-283 READY

compatibility grain correct

full candidate cross product correct

all pair rules independent

ambient may use reefer

van-only requires van

home depot enforced

weight fit enforced

volume fit enforced

both capacity dimensions required

reason codes deterministic

impossible orders retained

compatible counts correct

vehicle scarcity correct

reefer bottleneck summarized

reefer-van bottleneck summarized

trip-slot pressure diagnostic only

scarcity report complete

no trip engine

no priority scoring

no optimizer

safe tests pass

pip check passes

private paths ignored

Task 1 unchanged

Task 2A unchanged

no Phase 20 implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
19 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-271 READY / FAIL
DT-272 READY / FAIL
DT-273 READY / FAIL
DT-274 READY / FAIL
DT-275 READY / FAIL
DT-276 READY / FAIL
DT-277 READY / FAIL
DT-278 READY / FAIL
DT-279 READY / FAIL
DT-280 READY / FAIL
DT-281 READY / FAIL
DT-282 READY / FAIL
DT-283 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

COMPATIBILITY MATRIX:
PASS / FAIL

REFRIGERATION RULE:
PASS / FAIL

VAN-ONLY RULE:
PASS / FAIL

HOME-DEPOT RULE:
PASS / FAIL

WEIGHT FIT:
PASS / FAIL

VOLUME FIT:
PASS / FAIL

IMPOSSIBLE ORDER DETECTION:
PASS / FAIL

COMPATIBLE VEHICLE COUNTS:
PASS / FAIL

VEHICLE SCARCITY:
PASS / FAIL

REEFER BOTTLENECK:
PASS / FAIL

REEFER-VAN BOTTLENECK:
PASS / FAIL

TRIP-SLOT PRESSURE:
PASS / FAIL

SCARCITY REPORT:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 19 compatibility-build command.

PHASE 19 STATUS:
AWAITING LOCAL COMPATIBILITY BUILD

READY FOR PHASE 20:
NO

Then STOP.

Do not start Phase 20.
```

---

# 24. Independent Phase 19 review prompt

Use a fresh Codex/Cursor session after the human local build passes.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 19.

Do NOT implement Phase 20.
Do NOT inspect private row-level compatibility data.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 19
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. src/task2b/scenario.py
7. src/task2b/compatibility.py
8. src/task2b/scarcity.py
9. scripts/build_task2b_compatibility.py
10. configs/task2b_scenario.yaml
11. configs/task2b_compatibility.yaml
12. docs/task2b_compatibility_spec.md
13. tests/test_task2b_compatibility.py
14. tests/test_task2b_scarcity.py
15. .gitignore
16. .cursorignore if present

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 19 COMPATIBILITY BUILD: <PASS/FAIL>
PAIR KEY UNIQUE: <YES/NO>
REFRIGERATION RULE: <PASS/FAIL>
VAN-ONLY RULE: <PASS/FAIL>
HOME-DEPOT RULE: <PASS/FAIL>
WEIGHT FIT RULE: <PASS/FAIL>
VOLUME FIT RULE: <PASS/FAIL>
ORDER SUMMARY COVERAGE: <PASS/FAIL>
VEHICLE SUMMARY COVERAGE: <PASS/FAIL>
IMPOSSIBLE ORDERS IDENTIFIED: <YES/NO>
REEFER BOTTLENECK ANALYSIS: <PASS/FAIL>
REEFER-VAN BOTTLENECK ANALYSIS: <PASS/FAIL>
TRIP-SLOT PRESSURE ANALYSIS: <PASS/FAIL>

Do not ask for real order IDs or pair tables.

AUDIT EVERY TASK:

DT-271:
canonical order_ref+vehicle_id candidate matrix, correct cross product,
no order/outlet collapsing.

DT-272:
chilled requires reefer, ambient may use reefer.

DT-273:
van_only requires van, unrestricted orders may still use vans.

DT-274:
home depot pair rule enforced defensively.

DT-275:
whole-order weight fit, equality valid.

DT-276:
whole-order volume fit, equality valid, both dimensions required.

DT-277:
zero-compatible orders identified and retained.

DT-278:
compatible vehicle count/share correct.

DT-279:
vehicle scarcity indicators and exclusive-order counts correct.

DT-280:
reefer bottleneck is diagnostic only and does not claim final feasibility.

DT-281:
chilled+van_only correctly requires reefer+van.

DT-282:
trip-slot pressure stays diagnostic and does not construct actual trips.

DT-283:
scarcity report clearly separates hard incompatibility,
scarcity diagnostic, and future optimization decisions.

GLOBAL AUDIT:

- stable incompatibility reason codes
- no order splitting
- no final served/deferred decision
- no trip-time engine
- no priority weights
- no optimizer
- Task 1 unchanged
- Task 2A unchanged
- private output ignored
- no private row output

RUN SAFE TESTS:

pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py tests/test_task2b_compatibility.py tests/test_task2b_scarcity.py

pytest -q

python -m pip check

git status

git diff --check

Do not run the real compatibility build.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

MATRIX GRAIN/CARDINALITY:
PASS / FAIL

REFRIGERATION:
PASS / FAIL

VAN-ONLY ACCESS:
PASS / FAIL

HOME DEPOT:
PASS / FAIL

WEIGHT/VOLUME:
PASS / FAIL

IMPOSSIBLE ORDER RETENTION:
PASS / FAIL

SCARCITY DIAGNOSTICS:
PASS / FAIL

REEFER BOTTLENECK:
PASS / FAIL

REEFER-VAN BOTTLENECK:
PASS / FAIL

TRIP-SLOT SCOPE DISCIPLINE:
PASS / FAIL

NO ALLOCATION/POLICY/OPTIMIZER:
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

DT-271: PASS/FAIL
DT-272: PASS/FAIL
DT-273: PASS/FAIL
DT-274: PASS/FAIL
DT-275: PASS/FAIL
DT-276: PASS/FAIL
DT-277: PASS/FAIL
DT-278: PASS/FAIL
DT-279: PASS/FAIL
DT-280: PASS/FAIL
DT-281: PASS/FAIL
DT-282: PASS/FAIL
DT-283: PASS/FAIL

PHASE 19 REVIEW:
PASS / FAIL

READY FOR PHASE 20:
YES / NO

If FAIL:
list exact blockers only.

Do not automatically fix.
Do not start Phase 20.
```

---

# 25. Completion record template

```markdown
# Phase 19 Completion Record

## Tasks

- [ ] DT-271
- [ ] DT-272
- [ ] DT-273
- [ ] DT-274
- [ ] DT-275
- [ ] DT-276
- [ ] DT-277
- [ ] DT-278
- [ ] DT-279
- [ ] DT-280
- [ ] DT-281
- [ ] DT-282
- [ ] DT-283

## Agent stage

- compatibility tests: PASS / FAIL
- scarcity tests: PASS / FAIL
- full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- compatibility build: PASS / FAIL
- pair key unique: YES / NO
- order coverage: PASS / FAIL
- vehicle coverage: PASS / FAIL
- core rules: PASS / FAIL
- impossible-order detection: PASS / FAIL
- scarcity report: PASS / FAIL

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- private pair rows exposed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 19 STATUS: PASS / FAIL
READY FOR PHASE 20: YES / NO
```

---

# 26. Final Phase 19 checklist

Before Phase 20:

- [ ] Phase 18 passed.
- [ ] compatibility matrix grain is `order_ref + vehicle_id`.
- [ ] cross-product cardinality is correct.
- [ ] duplicate outlet IDs are not collapsed.
- [ ] chilled requires reefer.
- [ ] reefer may carry ambient.
- [ ] van-only requires van.
- [ ] unrestricted orders may still use vans.
- [ ] home-depot matching is enforced.
- [ ] whole-order weight fit is enforced.
- [ ] whole-order volume fit is enforced.
- [ ] both capacity dimensions are required.
- [ ] equality at capacity is accepted.
- [ ] incompatibility reasons are deterministic.
- [ ] impossible orders remain in the Task 2B order universe.
- [ ] compatible vehicle counts are complete.
- [ ] singleton/low-flexibility diagnostics are complete.
- [ ] every usable vehicle is in scarcity output.
- [ ] reefer pressure is summarized.
- [ ] reefer-van pressure is summarized.
- [ ] trip-slot pressure remains diagnostic.
- [ ] no trip-time engine exists yet.
- [ ] no priority weights are frozen.
- [ ] no optimizer exists.
- [ ] private outputs remain ignored.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.
- [ ] tests pass.
- [ ] local build passes.
- [ ] independent review passes.

Only then:

```text
PHASE 19 STATUS: PASS
READY FOR PHASE 20: YES
```
