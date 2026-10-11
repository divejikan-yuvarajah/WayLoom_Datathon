# PHASE 22 — Task 2B Optimization Solver

> **Filename:** `PHASE_22_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 22 — Task 2B Optimization Solver  
> **Task range:** **DT-299 → DT-319**  
> **Task count:** **21**  
> **Default phase priority:** **P0**  
> **Master dependency:** **Phases 19–21**  
> **Operational dependency:** Phases **18, 19, 20, and 21 must all be PASS** before the real S1 solve is frozen.  
> **Phase gate:** A final allocation exists that satisfies all seven official Task 2B hard rules and the frozen WayLoom priority policy.  
> **Execution mode:** High-risk deterministic constraint optimization with independent post-solve audit.  
> **Recommended solver:** **Google OR-Tools CP-SAT** as specified by the finalized WayLoom master inventory.  
> **Do not start Phase 23 until this phase independently audits and freezes the allocation.**

---

# 1. Phase 22 purpose

Phase 22 turns the already validated Task 2B contracts into a real allocation solver.

Earlier phases have deliberately separated the problem into:

```text
Phase 18
canonical S1 scenario + fleet + references
        ↓
Phase 19
order-to-vehicle compatibility + scarcity
        ↓
Phase 20
exact official trip-time arithmetic
        ↓
Phase 21
transparent frozen prioritization policy
        ↓
PHASE 22
constraint optimization
```

Phase 22 must produce one complete private allocation in which every S1 order is either:

```text
served
```

or:

```text
deferred
```

and every served order has:

```text
one available vehicle_id
+
one trip_id in {1,2}
```

The optimizer must never violate an official feasibility rule merely to improve the priority objective.

The phase ends by freezing a canonical private allocation for Phase 23 independent validation.

Phase 22 does **not** yet create the final organizer submission file.

That belongs to Phase 24.

---

# 2. Source hierarchy

Use the following authority order:

1. **Official Challenge Booklet Task 2B rules and official files**
2. **Official supplied templates/checker**
3. **Finalized `WAYLOOM_DATATHON_MASTER_PLAN.md`**
4. **Approved Phase 18–21 contracts**
5. **This Phase 22 implementation contract**
6. **Engineering implementation choices**

If an engineering choice conflicts with the official seven Task 2B rules:

```text
OFFICIAL RULE WINS
```

If the source files expose an unresolved ambiguity:

```text
STOP
```

Do not silently invent a rule.

---

# 3. Finalized Phase 22 master inventory

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-299** | [E] | P0 | DT-293–DT-298 | Install/configure OR-Tools |
| [ ] | **DT-300** | [E] | P0 | Phases 19–21 | Define order assignment variables |
| [ ] | **DT-301** | [E] | P0 | Phases 19–21 | Define vehicle/trip usage variables |
| [ ] | **DT-302** | [O] | P0 | Phases 19–21 | Enforce one decision per order |
| [ ] | **DT-303** | [O] | P0 | Phases 19–21 | Enforce whole-order assignment |
| [ ] | **DT-304** | [O] | P0 | Phases 19–21 | Enforce same-brand-per-trip |
| [ ] | **DT-305** | [O] | P0 | Phases 19–21 | Enforce same-district-per-trip |
| [ ] | **DT-306** | [O] | P0 | Phases 19–21 | Enforce reefer rule |
| [ ] | **DT-307** | [O] | P0 | Phases 19–21 | Enforce van-only rule |
| [ ] | **DT-308** | [O] | P0 | Phases 19–21 | Enforce home-depot rule |
| [ ] | **DT-309** | [O] | P0 | Phases 19–21 | Enforce weight capacity |
| [ ] | **DT-310** | [O] | P0 | Phases 19–21 | Enforce volume capacity |
| [ ] | **DT-311** | [O] | P0 | Phases 19–21 | Enforce maximum two trips per vehicle |
| [ ] | **DT-312** | [O] | P0 | Phases 19–21 | Enforce Fresh ≤270 minutes |
| [ ] | **DT-313** | [O] | P0 | Phases 19–21 | Enforce Style+Tech ≤480 minutes |
| [ ] | **DT-314** | [E] | P0 | Phases 19–21 | Add prioritization objective |
| [ ] | **DT-315** | [E] | P0 | DT-299–DT-314 | Solve initial feasible allocation |
| [ ] | **DT-316** | [E] | P0 | Phases 19–21 | Inspect solver status |
| [ ] | **DT-317** | [E] | P0 | Phases 19–21 | Validate every served trip manually/independently |
| [ ] | **DT-318** | [E] | P0 | Phases 19–21 | Tune prioritization objective |
| [ ] | **DT-319** | [E] | P0 | DT-315–DT-318 | Freeze final allocation |

**Expected tasks:** 21  
**Phase complete:** [ ]  
**READY FOR PHASE 23:** NO

---

# 4. Official Task 2B output semantics relevant to the solver

The official Task 2B submission ultimately requires one row per:

```text
order_ref
```

with:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Official decision semantics:

```text
decision = served
→ vehicle_id populated
→ trip_id is 1 or 2
```

```text
decision = deferred
→ vehicle_id blank
→ trip_id blank
```

`order_ref` is the allocation key because:

```text
outlet_id may appear more than once
```

Phase 22 must optimize by `order_ref`, never by unique outlet.

---

# 5. The seven official hard rules — immutable

The optimizer must encode all seven.

## H1 — Same brand and district per trip

Every order sharing:

```text
vehicle_id + trip_id
```

must have the same:

```text
brand
district
```

## H2 — Refrigeration

```text
temp_requirement = chilled
→ vehicle.temp = reefer
```

Reefer vehicles may also carry ambient orders.

## H3 — Vehicle access

```text
parking_constraint = van_only
→ vehicle.type = van
```

## H4 — Home depot

Vehicle may serve only orders/outlets assigned to its home depot.

Scenario S1 is Peliyagoda.

## H5 — Whole order

Every served order is assigned to exactly one:

```text
vehicle + trip
```

No splitting.

## H6 — Capacity

For each trip:

```text
sum(order_weight_kg)
<=
vehicle.weight_cap_kg
```

and:

```text
sum(order_volume_m3)
<=
vehicle.volume_cap_m3
```

Both are mandatory.

## H7 — Trips and time

Each vehicle:

```text
<= 2 trips total
```

and:

```text
sum(Fresh trip minutes)
<= 270
```

and:

```text
sum(Style + Tech trip minutes)
<= 480
```

The Fresh and Style+Tech windows are separate.

One vehicle may therefore perform:

```text
one Fresh trip
+
one Style/Tech trip
```

if all hard rules pass and there are at most two trips total.

---

# 6. Official trip-time formula — reuse Phase 20 exactly

Do not reimplement a different time formula inside the optimizer.

For one trip:

```text
trip_minutes
=
outbound
+
inter_stop
+
handling
```

where:

```text
outbound
=
depot_to_district_freeflow_min
```

counted once.

```text
inter_stop
=
inter_stop_freeflow_min
*
(number_of_orders - 1)
```

```text
handling
=
sum(service_allowance_min for every order)
```

and:

```text
RETURN JOURNEY IS NOT ADDED
```

The official Gampaha example remains:

```text
37 + 18 + 46 = 101 minutes
```

Phase 22 must use the same coefficients/reference semantics validated in Phase 20.

---

# 7. Frozen WayLoom priority policy from Phase 21

Hard feasibility exists outside the objective.

Among feasible allocations, Phase 22 must preserve this lexicographic order exactly:

```text
LEVEL 1
maximize served_order_count

LEVEL 2
maximize served_previous_deferred_count

LEVEL 3
maximize served_waiting_days_sum

LEVEL 4
maximize served_low_flexibility_count

LEVEL 5
maximize served_fresh_chilled_count

LEVEL 6
maximize served_fresh_count

LEVEL 7A
minimize avoidable_reefer_van_assignment_count

LEVEL 7B
minimize avoidable_reefer_assignment_count

LEVEL 7C
minimize avoidable_van_assignment_count
```

Do not reorder these after seeing the real allocation.

Do not introduce a new objective term without reopening Phase 21.

---

# 8. Recommended solver architecture

Use:

```text
OR-Tools CP-SAT
```

with binary/integer variables only.

Recommended tracked files:

```text
src/task2b/solver_data.py
src/task2b/optimizer.py
src/task2b/lexicographic_solver.py
src/task2b/solution.py
src/task2b/solution_audit.py
src/task2b/cp_scaling.py

scripts/run_task2b_optimizer.py
scripts/freeze_task2b_allocation.py

configs/task2b_optimizer.yaml

docs/task2b_optimizer_spec.md

tests/test_task2b_solver_data.py
tests/test_task2b_optimizer_constraints.py
tests/test_task2b_lexicographic_solver.py
tests/test_task2b_solution_audit.py
tests/test_task2b_allocation_freeze.py
```

Reuse rather than duplicate:

```text
src/task2b/scenario.py
src/task2b/compatibility.py
src/task2b/scarcity.py
src/task2b/trip_time.py
src/task2b/priority.py
src/task2b/policy_metrics.py
```

---

# 9. Private Phase 22 outputs

Recommended:

```text
data/interim/task2b_solver_allocation_candidate.csv
data/interim/task2b_final_allocation.csv
data/interim/task2b_final_trip_summary.csv
```

Private report directory:

```text
reports/private/phase22_task2b_optimizer/
├── run_manifest.json
├── solver_status.json
├── objective_stages.json
├── objective_vector.json
├── solver_statistics.json
├── served_trip_audit.csv
├── hard_rule_audit.json
├── allocation_summary.json
├── freeze_manifest.json
├── warnings.json
└── phase22_optimizer_report.md
```

Do not commit row-level private outputs.

Do not create:

```text
outputs/submission_task2b.csv
```

in Phase 22.

That belongs to Phase 24.

---

# 10. Recommended optimizer config

Create:

```text
configs/task2b_optimizer.yaml
```

Recommended structure:

```yaml
version: 1

solver:
  engine: ortools_cp_sat
  random_seed: 42
  num_search_workers: 1
  max_time_seconds_per_objective_stage: 120
  log_search_progress: false

  require_optimal_objective_stages_for_freeze: true
  allow_feasible_only_final_freeze: false

model:
  trip_ids:
    - 1
    - 2

  enforce_trip_2_requires_trip_1: true

  assignment_variables_only_for_compatible_pairs: true

  independently_recheck_compatibility_contract: true

scaling:
  strategy: exact_decimal
  max_decimal_places: 6
  reject_rounding: true

time:
  fresh_budget_min: 270
  style_tech_budget_min: 480
  include_return_leg: false

objective:
  source_config: configs/task2b_priority.yaml
  strategy: lexicographic

freeze:
  canonical_allocation_path: data/interim/task2b_final_allocation.csv
  canonical_trip_summary_path: data/interim/task2b_final_trip_summary.csv
  prevent_overwrite_if_frozen: true

reports:
  private_output_dir: reports/private/phase22_task2b_optimizer
```

The numeric time budgets are official.

The exact solver settings are engineering choices.

---

# 11. CP-SAT numeric scaling contract

CP-SAT uses integer coefficients.

Official source values such as:

```text
order_volume_m3
weight_cap_kg
service/travel minutes
```

may be represented as decimals.

Do not round them silently to integers.

Implement an exact deterministic scaling layer.

Recommended strategy:

1. Convert numeric source values using:

```python
Decimal(str(value))
```

2. Determine the required decimal precision for each numeric family:

```text
weight
volume
time
```

3. Choose a scale:

```text
10 ** max_decimal_places_observed
```

subject to the configured safe maximum.

4. Convert every value exactly.

5. Reverse/check conversion in tests.

If a value cannot be represented exactly within the configured precision:

```text
STOP
```

Do not round to make the solver work.

Recommended helpers:

```python
derive_exact_scale(...)
to_scaled_int(...)
from_scaled_int(...)
validate_exact_scaling(...)
```

Record the chosen scales privately in the run manifest.

---

# 12. Canonical solver sets

Recommended notation.

Orders:

```text
O
```

Available usable vehicles:

```text
V
```

Trip slots:

```text
T = {1,2}
```

Brand+district groups:

```text
G
```

Each order belongs to exactly one:

```text
g(o) = (brand_o, district_o)
```

Compatible vehicle set from Phase 19:

```text
C(o) ⊆ V
```

Only create assignment variables for:

```text
v ∈ C(o)
```

This reduces the model and structurally blocks known-incompatible pairs.

However, the Phase 22 model builder must independently assert that Phase 19 compatibility is consistent with the official static rules.

Do not blindly trust a corrupted compatibility matrix.

---

# 13. Recommended decision variables

## 13.1 Order service/defer variables

For every order `o`:

```text
serve[o] ∈ {0,1}

defer[o] ∈ {0,1}
```

## 13.2 Assignment variables

For each compatible:

```text
order o
vehicle v
trip t ∈ {1,2}
```

create:

```text
x[o,v,t] ∈ {0,1}
```

meaning:

```text
order o is served by vehicle v on trip t
```

Do not create `x` for incompatible order/vehicle pairs.

## 13.3 Trip usage variables

For every:

```text
vehicle v
trip t
```

create:

```text
use_trip[v,t] ∈ {0,1}
```

## 13.4 Trip group variables

For every:

```text
vehicle v
trip t
brand+district group g
```

create:

```text
use_group[v,t,g] ∈ {0,1}
```

meaning the trip is assigned to that one brand+district group.

This makes H1 linear and transparent.

## 13.5 Optional trip-minute variables

Create:

```text
trip_minutes[v,t] ∈ nonnegative integer
```

in the chosen scaled time unit.

These are useful for extraction/audit.

---

# 14. DT-299 — Install/configure OR-Tools

## Objective

Add and smoke-test OR-Tools CP-SAT.

## Requirements

Use local Python package:

```text
ortools
```

Do not use:

```text
remote optimization API
proprietary solver API
cloud AutoML/optimization service
```

The official competition restrictions prohibit sending competition data to external proprietary modelling/preprocessing systems.

The solver must run locally.

## Dependency policy

Do not guess an arbitrary newest version.

Use the repository’s normal dependency pinning policy.

Recommended process:

1. inspect current Python version;
2. install a compatible local `ortools`;
3. record the working version in `requirements.txt` / lock file according to project convention;
4. run a tiny synthetic CP-SAT smoke model;
5. run `python -m pip check`.

## Smoke test

Example:

```text
bool x
maximize x
```

Expected:

```text
OPTIMAL
x = 1
```

## STOP

If OR-Tools cannot be installed cleanly in the project environment.

Do not silently replace the required Phase 22 solver with a different external service.

---

# 15. DT-300 — Define order assignment variables

## Objective

Create assignment decisions only for legal order/vehicle candidate pairs.

For:

```text
o ∈ O
v ∈ C(o)
t ∈ {1,2}
```

create:

```text
x[o,v,t]
```

## Required metadata

Maintain deterministic maps:

```text
order_ref → order index
vehicle_id → vehicle index
trip id → 1/2
group → brand+district
```

Sort source identifiers before variable creation for reproducibility.

## Impossible orders

If:

```text
C(o) = ∅
```

create no assignment variable for that order.

Later enforce:

```text
serve[o] = 0
defer[o] = 1
```

## Tests

- correct variable count;
- no variable for incompatible pair;
- both trip slots available for compatible pair;
- duplicate outlet does not collapse order variables;
- deterministic names/indexes.

---

# 16. DT-301 — Define vehicle/trip usage variables

## Objective

Represent whether each of a vehicle’s two allowed trip slots is used.

Create:

```text
use_trip[v,1]
use_trip[v,2]
```

and group-selection variables.

Required constraints:

```text
sum_g use_group[v,t,g]
=
use_trip[v,t]
```

Therefore:

```text
unused trip → no group
used trip → exactly one brand+district group
```

Link assignments:

```text
x[o,v,t]
<=
use_trip[v,t]
```

and:

```text
x[o,v,t]
<=
use_group[v,t,g(o)]
```

Prevent empty used trips:

```text
sum_o x[o,v,t]
>=
use_trip[v,t]
```

Also:

```text
sum_o x[o,v,t]
<=
M * use_trip[v,t]
```

where `M` is a safe deterministic order-count upper bound.

## Symmetry-breaking engineering rule

Recommended:

```text
use_trip[v,2]
<=
use_trip[v,1]
```

This means:

```text
a vehicle never uses trip 2 while trip 1 is empty
```

This is not an official business rule.

It is a safe symmetry breaker because trip labels 1 and 2 are otherwise interchangeable under the official constraints.

Document it explicitly as engineering only.

---

# 17. DT-302 — Enforce one decision per order

For every order:

```text
serve[o] + defer[o] = 1
```

Exactly one decision.

No order may be:

```text
both served and deferred
```

or:

```text
neither
```

For individually impossible orders:

```text
serve[o] = 0
defer[o] = 1
```

This is hard feasibility, not policy.

Tests:

- every order exactly one decision;
- impossible forced deferred;
- no missing decision.

---

# 18. DT-303 — Enforce whole-order assignment

For every order:

```text
sum_{v,t} x[o,v,t]
=
serve[o]
```

Consequences:

If served:

```text
exactly one vehicle/trip assignment
```

If deferred:

```text
zero assignments
```

This enforces:

```text
no split across vehicles
no split across trips
```

Do not model partial volume/weight served.

Tests:

- served has exactly one x=1;
- deferred all x=0;
- two-vehicle split impossible;
- two-trip split impossible.

---

# 19. DT-304 — Enforce same brand per trip

This should be structural through the group variables.

Each order belongs to:

```text
g(o) = (brand, district)
```

Assignment requires:

```text
x[o,v,t]
<=
use_group[v,t,g(o)]
```

and a used trip selects exactly one group.

Therefore all assigned orders share one brand.

Do not use a soft penalty.

It is an official hard rule.

Independent audit must still re-check the extracted solution.

---

# 20. DT-305 — Enforce same district per trip

The same group-variable design enforces one district per trip.

Do not permit one trip to include two districts and add two outbound values.

That would violate the official Task 2B definition.

Tests:

- mixed-brand same-district infeasible;
- same-brand mixed-district infeasible;
- same brand+district feasible if all other constraints pass.

---

# 21. DT-306 — Enforce reefer rule

Phase 19 compatibility already filters:

```text
chilled → reefer
```

Phase 22 must enforce it defensively.

Required model-builder audit:

For every assignment variable:

```text
if order.temp_requirement == chilled:
    vehicle.temp must equal reefer
```

If Phase 19 says a chilled/non-reefer pair is compatible:

```text
STOP
```

Do not quietly accept corrupted upstream compatibility.

Do not block ambient orders from reefer vehicles.

Tests:

- chilled/reefer variable allowed;
- chilled/non-reefer variable absent/rejected;
- ambient/reefer allowed.

---

# 22. DT-307 — Enforce van-only rule

For every assignment variable:

```text
if parking_constraint == van_only:
    vehicle.type must equal van
```

If Phase 19 permits:

```text
van_only + truck
```

treat it as an upstream contract failure.

Do not force non-van-only orders away from vans.

---

# 23. DT-308 — Enforce home-depot rule

For every assignment candidate:

```text
vehicle_home_depot == order.depot
```

S1 expected:

```text
Peliyagoda
```

Any incompatible depot pair must have no assignment variable.

Do not relabel depots.

---

# 24. DT-309 — Enforce weight capacity

For each:

```text
vehicle v
trip t
```

constraint:

```text
sum_o scaled_weight[o] * x[o,v,t]
<=
scaled_weight_capacity[v] * use_trip[v,t]
```

Using `* use_trip` ensures:

```text
unused trip → zero load
```

The model already ensures no assignments on unused trips, but keeping the expression explicit helps auditability.

Equality at capacity is valid.

Do not use individual-fit checks as a substitute for combined trip capacity.

Tests:

- two individually fitting orders can still jointly exceed capacity and be rejected;
- equal total passes;
- one unit above fails;
- exact scaling preserves decimals.

---

# 25. DT-310 — Enforce volume capacity

For every vehicle/trip:

```text
sum_o scaled_volume[o] * x[o,v,t]
<=
scaled_volume_capacity[v] * use_trip[v,t]
```

Both:

```text
DT-309 weight
AND
DT-310 volume
```

must pass.

Do not optimize one and ignore the other.

Tests:

- weight passes, volume fails → infeasible combination;
- volume passes, weight fails → infeasible combination;
- both pass → potentially feasible.

---

# 26. Linear exact trip-minute expression inside CP-SAT

The optimizer must represent the Phase 20 formula linearly.

Because a used trip selects exactly one brand+district group, define:

```text
trip_minutes[v,t]
=
outbound component
+
inter-stop component
+
handling component
```

Recommended linear construction.

For group `g` with district `d(g)`:

```text
outbound component
=
sum_g outbound[d(g)] * use_group[v,t,g]
```

For each assigned order:

```text
handling contribution
=
service_allowance[o] * x[o,v,t]
```

For inter-stop, use the identity:

```text
inter_stop_rate * (n_orders - 1)
=
inter_stop_rate * n_orders
-
inter_stop_rate
```

Since all assigned orders share one selected district:

```text
inter-stop component
=
sum_o inter_stop[d(o)] * x[o,v,t]
-
sum_g inter_stop[d(g)] * use_group[v,t,g]
```

Therefore:

```text
trip_minutes[v,t]
=
sum_g outbound[d(g)] * use_group[v,t,g]
+
sum_o (
    service_allowance[o]
    +
    inter_stop[d(o)]
) * x[o,v,t]
-
sum_g inter_stop[d(g)] * use_group[v,t,g]
```

When trip unused:

```text
all terms = 0
```

When one order:

```text
inter-stop = 0
```

When `n` orders:

```text
inter-stop = rate*(n-1)
```

This must match Phase 20 exactly.

Do not add return travel.

---

# 27. DT-311 — Enforce maximum two trips per vehicle

The variable domain already contains:

```text
trip 1
trip 2
```

but still add explicit clarity:

```text
use_trip[v,1] + use_trip[v,2] <= 2
```

Do not create trip 3 variables.

Recommended symmetry breaker:

```text
use_trip[v,2] <= use_trip[v,1]
```

Tests:

- zero trips;
- one trip;
- two trips;
- no third trip representation;
- trip2-only solution normalized to trip1.

---

# 28. DT-312 — Enforce Fresh ≤270 minutes

For every vehicle:

```text
sum(Fresh trip minutes for vehicle)
<=
270
```

Do not apply the 270-minute budget to:

```text
Style
Tech
```

Create a linear Fresh expression directly from Fresh group/order terms.

Recommended:

```text
fresh_minutes[v]
=
sum over trip slots
(
  Fresh outbound
  +
  Fresh inter-stop
  +
  Fresh handling
)
```

Then:

```text
fresh_minutes[v]
<=
270 * time_scale
```

## Critical edge case

Two Fresh trips:

```text
150 minutes
+
130 minutes
=
280
```

must be infeasible even though each trip individually is under 270.

Official budget is per vehicle's combined Fresh trips.

## Mixed day

One Fresh trip plus one Style trip:

Fresh counts only toward:

```text
270
```

Style counts only toward:

```text
480 Style+Tech
```

---

# 29. DT-313 — Enforce Style+Tech ≤480 minutes

For every vehicle:

```text
sum(Style trip minutes + Tech trip minutes)
<=
480
```

Style and Tech are combined into the same official budget.

Do not give:

```text
Style 480
+
Tech 480
```

as separate budgets.

Example:

```text
Style = 300
Tech = 200
combined = 500
```

must fail.

Fresh does not consume this 480-minute budget.

A vehicle may have:

```text
one Fresh trip
one Tech trip
```

if:

```text
Fresh <=270
Tech <=480
total trips <=2
```

---

# 30. DT-314 — Add prioritization objective

Implement the Phase 21 lexicographic objective **exactly**.

Do not collapse it into one arbitrary weighted score.

## Sequential lexicographic solve

Recommended process:

### Stage 1

```text
maximize served_order_count
```

Require:

```text
OPTIMAL
```

Record optimum:

```text
z1
```

Then add:

```text
served_order_count == z1
```

### Stage 2

```text
maximize served_previous_deferred_count
```

Require OPTIMAL.

Fix optimum.

Continue through all objective levels.

### Level expressions

Level 1:

```text
sum_o serve[o]
```

Level 2:

```text
sum_o deferred_yesterday[o] * serve[o]
```

Level 3:

```text
sum_o days_since_last_served[o] * serve[o]
```

Level 4:

```text
sum_o is_low_flexibility[o] * serve[o]
```

Level 5:

```text
sum_o is_fresh_chilled[o] * serve[o]
```

Level 6:

```text
sum_o is_fresh[o] * serve[o]
```

Level 7A:

```text
minimize sum avoidable_reefer_van_assignment_cost[o,v] * x[o,v,t]
```

Level 7B:

```text
minimize sum avoidable_reefer_assignment_cost[o,v] * x[o,v,t]
```

Level 7C:

```text
minimize sum avoidable_van_assignment_cost[o,v] * x[o,v,t]
```

Each avoidable cost must come from Phase 21 metadata/Phase 19 compatibility, not solver outcomes.

## Hard requirement

A lower stage may never change a higher-stage optimum.

Add equality constraints after each optimal stage.

---

# 31. Specialized-resource objective coefficients

For each assignment pair:

## Avoidable reefer-van

Cost 1 if:

```text
vehicle.type = van
AND vehicle.temp = reefer
AND order.has_non_reefer_van_alternative = true
```

else 0.

## Avoidable reefer

Cost 1 if:

```text
vehicle.temp = reefer
AND order.has_non_reefer_alternative = true
```

else 0.

## Avoidable van

Cost 1 if:

```text
vehicle.type = van
AND order.has_non_van_alternative = true
```

else 0.

These are assignment tiebreak costs only.

Necessary use of a specialized vehicle has cost:

```text
0
```

for "avoidable" purposes.

---

# 32. DT-315 — Solve initial feasible allocation

Before the full lexicographic solve, run a model-feasibility smoke solve.

Recommended:

```text
no business objective
```

or:

```text
simple maximize served count
```

with a short safe time limit.

Purpose:

- prove model is valid;
- prove CP-SAT can find a solution;
- catch contradictory hard constraints.

Because deferral is allowed, a structurally correct model should normally have at least the all-deferred solution.

Therefore:

```text
INFEASIBLE
```

is usually a model/data-contract blocker and must be investigated.

Do not freeze the initial feasible solution.

After smoke feasibility passes, execute the full lexicographic solve.

Private candidate output may be written as:

```text
data/interim/task2b_solver_allocation_candidate.csv
```

---

# 33. DT-316 — Inspect solver status

Recognize and handle CP-SAT statuses explicitly.

Required categories:

```text
OPTIMAL
FEASIBLE
INFEASIBLE
MODEL_INVALID
UNKNOWN
```

## Feasibility smoke solve

Accepted:

```text
FEASIBLE
OPTIMAL
```

## Each frozen objective stage

Required:

```text
OPTIMAL
```

if:

```text
require_optimal_objective_stages_for_freeze = true
```

Default is true.

## FEASIBLE but not OPTIMAL

The result may be useful for debugging.

It is **not eligible for final freeze** under the default contract.

Recommended action:

- inspect time limit;
- inspect model size;
- improve formulation;
- increase local stage time;
- use hints from previous objective stage;
- preserve policy ordering.

Do not lower policy standards merely to freeze a result quickly.

## INFEASIBLE

Blocker.

Because deferred decisions exist, inspect for a modelling bug or invalid hard constraint.

## MODEL_INVALID

Hard blocker.

## UNKNOWN

Hard blocker for final freeze.

Record for every objective stage:

```text
stage id
direction
status
objective value
best bound
wall time
branches
conflicts
```

when supported by the solver API.

---

# 34. Solution extraction contract

Convert solver assignments into exactly one row per S1 `order_ref`.

Recommended private schema:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

If:

```text
serve[o] = 1
```

extract exactly one:

```text
vehicle_id
trip_id
```

If:

```text
defer[o] = 1
```

set:

```text
vehicle_id = blank
trip_id = blank
```

Do not sort by vehicle/trip for the canonical order-level allocation.

Preserve a deterministic order, preferably the original S1 order order marker from Phase 18.

Phase 24 will restore exact official template ordering again.

---

# 35. Trip-summary extraction

Also create a private trip summary grouped by:

```text
vehicle_id
trip_id
```

Recommended fields:

```text
vehicle_id
trip_id
brand
district
order_count
total_weight_kg
total_volume_m3
weight_cap_kg
volume_cap_m3
outbound_minutes
inter_stop_minutes
handling_minutes
trip_minutes
budget_group
```

Optional:

```text
order_refs
```

private only.

This summary is diagnostic and feeds DT-317.

---

# 36. DT-317 — Validate every served trip manually/independently

This is a mandatory independent audit before freeze.

Do **not** validate merely by reading CP-SAT variable values and assuming the constraints worked.

Extract the allocation into ordinary tables and recompute every rule using canonical upstream helpers.

For every served order/trip independently verify:

## A. Order decision

Every S1 order appears exactly once.

Decision is:

```text
served
deferred
```

## B. Assignment

Served:

```text
vehicle populated
trip in {1,2}
```

Deferred:

```text
vehicle blank
trip blank
```

## C. Available fleet

Assigned vehicle is:

```text
S1
available
not in_workshop
```

## D. Brand + district

Every vehicle+trip group has:

```text
one brand
one district
```

## E. Refrigeration

Every chilled served order:

```text
assigned vehicle temp = reefer
```

## F. Van-only

Every van-only served order:

```text
assigned vehicle type = van
```

## G. Home depot

Every served pair:

```text
vehicle home depot == order depot
```

## H. Whole order

Each served `order_ref` appears in exactly one trip.

## I. Weight

Recompute actual trip sum:

```text
<= weight cap
```

## J. Volume

Recompute:

```text
<= volume cap
```

## K. Trip time

Call the canonical Phase 20 trip calculator on the extracted actual trip.

Do not trust the CP-SAT `trip_minutes` variable as the only evidence.

Assert solver-reported and independently calculated minutes are equal.

## L. Max trips

Each vehicle:

```text
<=2 nonempty trips
```

## M. Fresh time

Each vehicle:

```text
sum actual Fresh trip minutes <=270
```

## N. Style+Tech time

Each vehicle:

```text
sum actual Style + Tech trip minutes <=480
```

Any failure:

```text
DO NOT FREEZE
```

This is an internal Phase 22 audit.

Phase 23 will still build the formal independent validator and use the official checker later.

---

# 37. DT-318 — Tune prioritization objective

The master inventory calls for objective tuning.

Because Phase 21 already froze the policy, **tuning must not change policy meaning**.

Allowed tuning:

```text
increase max solve time

improve variable filtering

improve deterministic ordering

add safe symmetry breaking

reuse solver hints

optimize linear formulation

reduce redundant variables

change CP-SAT search parameters

mathematically equivalent implementation of the same lexicographic tiers
```

Not allowed without reopening Phase 21:

```text
reorder objective tiers

change low-flexibility threshold after seeing results

add new priority signals

make Fresh more important because the first output looks nicer

drop backlog fairness

convert a hard constraint to a soft penalty

convert a soft policy signal to a hard rule

change specialized-resource order

choose policy based on final deferrals
```

## Recommended tuning workflow

1. Run full lexicographic solver with frozen defaults.
2. Inspect status/runtime only.
3. If every stage is OPTIMAL and audit passes:
   no policy tuning required.
4. If some stage times out:
   tune solver mechanics.
5. Re-run all objective stages.
6. Confirm the objective vector is stable/optimal.
7. Re-run independent trip audit.

Do not compare several different business policies on real S1 and choose the most attractive one.

---

# 38. Determinism

Recommended for final run:

```text
random_seed = 42
num_search_workers = 1
```

Build sets/variables in stable sorted order.

Use deterministic:

```text
order_ref ordering
vehicle_id ordering
group ordering
trip ordering
objective level ordering
```

Run the final solve twice.

Required before freeze:

```text
same objective vector
same hard-rule validity
```

Prefer:

```text
same allocation
```

with the chosen deterministic settings.

If multiple equivalent optima still produce different allocations:

- confirm objective vectors are exactly identical;
- strengthen only safe engineering symmetry breakers;
- do not add a new hidden business priority merely to choose one.

---

# 39. Engineering symmetry breakers

Allowed examples:

```text
trip 2 cannot be used unless trip 1 is used
```

Potentially:

```text
stable variable ordering
```

Avoid symmetry breakers that change which customer orders are preferred.

Do not add:

```text
prefer lower vehicle_id
prefer lower order_ref
```

as business objectives.

If such deterministic ordering is ever used purely to select among identical optima, document it explicitly as implementation-only and confirm it does not affect any Phase 21 metric.

Default recommendation:

```text
fixed seed + single worker + trip-slot symmetry only
```

---

# 40. DT-319 — Freeze final allocation

Freeze only after all of the following:

```text
all lexicographic stages = OPTIMAL

objective order = Phase 21 exact order

every served trip passes independent audit

every S1 order has exactly one decision

no official hard-rule violation

determinism check passes

Task 1/2A artifacts unchanged
```

## Canonical private files

Write:

```text
data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv
```

## Freeze manifest

Create:

```text
reports/private/phase22_task2b_optimizer/freeze_manifest.json
```

Include:

```text
phase = 22

state = FROZEN

solver_engine

ortools_version

solver_config_hash

scenario_config_hash

compatibility_config_hash

trip_time_config_hash

priority_config_hash

source artifact hashes where safe

allocation_sha256

trip_summary_sha256

objective_strategy = lexicographic

objective_stage statuses

objective vector

all_hard_rules_audited = true

manual_independent_trip_audit = PASS

frozen_at

git_commit if available
```

Do not copy row-level allocation contents into tracked config.

## Overwrite protection

After freeze:

```text
normal optimizer command must refuse to overwrite the frozen canonical allocation
```

unless the user explicitly enters an approved re-open flow.

Do not silently regenerate it during later phases.

---

# 41. Freeze/reopen policy

Once Phase 22 is frozen:

```text
Phase 23 validates it
Phase 24 converts it into official template output
```

If Phase 23 finds a blocker:

```text
do not edit the CSV manually
```

Instead:

1. record the failed rule;
2. reopen Phase 22 explicitly;
3. fix model/contract issue;
4. rerun complete lexicographic optimization;
5. rerun independent audit;
6. produce a new freeze manifest/hash;
7. rerun Phase 23.

This preserves traceability.

---

# 42. Solver-model assertions before solve

Before calling CP-SAT, validate:

```text
S1 order_ref unique

usable vehicle_id unique

every assignment pair is Phase19-compatible

every assignment pair independently passes:
  refrigeration
  access
  depot
  individual weight fit
  individual volume fit

all orders have one group

all group brand/district values valid

Phase20 district travel references complete

Phase20 service allowance references complete

Phase21 priority metadata complete

objective levels exactly match config

include_return_leg = false

budgets exactly 270 and 480

trip IDs exactly {1,2}
```

Any mismatch:

```text
STOP BEFORE SOLVE
```

---

# 43. Required synthetic test suite

Create:

```text
tests/test_task2b_solver_data.py
tests/test_task2b_optimizer_constraints.py
tests/test_task2b_lexicographic_solver.py
tests/test_task2b_solution_audit.py
tests/test_task2b_allocation_freeze.py
```

Use synthetic fixtures only.

---

# 44. DT-299 tests — OR-Tools

- import works;
- tiny CP-SAT model returns OPTIMAL;
- package version recorded;
- no remote solver;
- pip check passes.

---

# 45. DT-300 tests — assignment variables

- variable only for compatible order/vehicle pair;
- both trip slots;
- no variable for incompatible pair;
- impossible order has zero x variables;
- deterministic variable names.

---

# 46. DT-301 tests — trip usage

- unused trip has no assignments;
- used trip has at least one order;
- used trip selects exactly one group;
- trip2 without trip1 blocked by symmetry rule;
- group/use links correct.

---

# 47. DT-302/303 tests — decisions + whole orders

- serve+defer exactly one;
- served assigned exactly once;
- deferred assigned zero times;
- order cannot split vehicles;
- order cannot split trips;
- impossible order forced deferred.

---

# 48. DT-304/305 tests — brand + district

- same brand+district group feasible;
- mixed brand same trip infeasible;
- mixed district same trip infeasible;
- two different vehicle trips may use different groups;
- trip1 and trip2 of same vehicle may use different groups.

---

# 49. DT-306 tests — reefer

- chilled→reefer enforced;
- chilled→dry impossible;
- ambient→reefer allowed;
- upstream compatibility mismatch causes model-build failure.

---

# 50. DT-307 tests — van-only

- van_only→van;
- van_only→truck impossible;
- normal→van allowed;
- normal→truck allowed.

---

# 51. DT-308 tests — depot

- matching depot accepted;
- mismatch variable rejected/model-build failure;
- no relabeling.

---

# 52. DT-309 tests — weight

- below cap;
- exact cap;
- combined exact cap;
- combined above cap infeasible;
- decimal scaling exact.

---

# 53. DT-310 tests — volume

- below cap;
- exact cap;
- combined above cap;
- weight-pass volume-fail infeasible;
- volume-pass weight-fail infeasible;
- scaling exact.

---

# 54. DT-311 tests — two trips

- zero trips valid;
- one trip valid;
- two trips valid;
- no trip 3;
- trip2-only blocked/normalized.

---

# 55. DT-312 tests — Fresh time

- one Fresh trip under 270;
- exactly 270 valid;
- 271 invalid;
- two Fresh trips individually under but combined >270 invalid;
- official 101+112 = 213 accepted;
- Fresh does not consume Style+Tech budget.

---

# 56. DT-313 tests — Style+Tech time

- one Style under 480;
- one Tech under 480;
- Style+Tech combined exactly 480 valid;
- combined 481 invalid;
- two Style trips combined >480 invalid;
- Fresh time separate.

---

# 57. Trip-time expression parity tests

For synthetic candidate trips:

```text
CP-SAT linear trip_minutes expression
==
Phase20 calculate_trip_time(...)
```

Test:

- one order;
- two orders;
- three orders;
- mixed dock types;
- public 101-minute example;
- public 112-minute example;
- no return leg.

This is critical.

---

# 58. DT-314 tests — objective

Use tiny synthetic allocation problems where expected winner is obvious.

## Coverage dominates backlog

Plan A:

```text
10 served
1 previous-deferred
```

Plan B:

```text
9 served
5 previous-deferred
```

Solver must select A.

## Backlog breaks tie

Same served count.

More previous-deferred wins.

## Waiting-days

Higher served waiting-days wins only when Levels 1–2 tie.

## Low flexibility

Only acts after Levels 1–3 tie.

## Fresh chilled

Only after Levels 1–4 tie.

## Fresh

Only after Levels 1–5 tie.

## Resource stewardship

Only after all service/fairness/business tiers tie.

---

# 59. Lexicographic integrity tests

For each stage:

```text
previous objective equality constraints remain active
```

Test a synthetic case where a lower objective would prefer sacrificing one higher-level unit.

The solver must not permit it.

Do not rely only on expected final allocation.

Inspect/fix every stage optimum.

---

# 60. DT-315/316 tests — status handling

- feasibility smoke returns FEASIBLE/OPTIMAL;
- optimal stage accepted;
- FEASIBLE-only stage not freeze eligible;
- INFEASIBLE blocks;
- MODEL_INVALID blocks;
- UNKNOWN blocks;
- status report complete.

---

# 61. DT-317 tests — independent audit

Take synthetic extracted allocations and deliberately violate one rule at a time.

Audit must detect:

```text
duplicate/missing decision

served without vehicle

deferred with vehicle

workshop vehicle

mixed brand

mixed district

chilled on non-reefer

van-only on truck

wrong depot

split/duplicate order

overweight trip

over-volume trip

third trip

Fresh >270

Style+Tech >480

solver trip minutes != Phase20 recomputation
```

Also verify a correct allocation passes.

---

# 62. DT-318 tests — tuning boundary

Tests/config guards must reject:

```text
objective tier reorder

new policy term

low-flexibility threshold change relative to frozen Phase21

hard-rule softening
```

Allow:

```text
time-limit increase

solver hinting

safe formulation optimization

symmetry breaker
```

---

# 63. DT-319 tests — freeze

- all stages OPTIMAL required;
- audit PASS required;
- canonical allocation written;
- canonical trip summary written;
- SHA256 manifest correct;
- freeze state FROZEN;
- second normal overwrite attempt rejected;
- changed allocation hash detected;
- no official submission file created.

---

# 64. End-to-end synthetic solver test

Build a complete small synthetic scenario with:

```text
multiple brands

multiple districts

one chilled order

one van-only order

one chilled+van-only order

one previously deferred order

different days_since_last_served

one capacity bottleneck

one time-budget bottleneck

two vehicles
```

Run:

```text
solver data build
→ model build
→ feasibility smoke
→ full lexicographic solve
→ solution extraction
→ independent audit
→ freeze
```

Expected:

```text
all official rules pass

objective vector matches expected hierarchy

allocation deterministic

freeze succeeds
```

No real competition data.

---

# 65. Edge cases

## All orders can be deferred

Officially every order must receive a decision.

Deferral is allowed.

Therefore an all-deferred solution is structurally feasible if output fields are valid.

It is not policy-optimal when any order can feasibly be served because Level 1 maximizes served count.

This is why `INFEASIBLE` usually indicates a modelling error.

---

## Individually impossible order

Force:

```text
serve=0
defer=1
```

Do not waste solve time trying to serve it.

Keep it in output.

---

## One vehicle can handle Fresh and Style

Allowed if:

```text
two trips maximum

Fresh minutes <=270

Style+Tech minutes <=480
```

The two budget groups remain separate.

---

## One vehicle has two Fresh trips

Allowed if combined Fresh minutes:

```text
<=270
```

---

## One vehicle has one Style and one Tech trip

Allowed if combined Style+Tech minutes:

```text
<=480
```

---

## Same vehicle uses two districts

Allowed only if:

```text
different trip IDs
```

Each individual trip still uses exactly one district.

---

## Same vehicle uses two brands

Allowed only across separate trips.

One trip cannot mix brands.

---

## Reefer serving ambient

Allowed.

Resource stewardship may prefer a non-reefer alternative only at the final tiebreak tier.

---

## Van serving normal-access outlet

Allowed.

Resource stewardship may prefer a non-van alternative later.

---

## Exact capacity boundary

Valid.

Do not subtract an arbitrary safety margin.

---

## Exact time budget boundary

Valid:

```text
Fresh = 270

Style+Tech = 480
```

---

## Multiple optimal allocations

Do not invent a new customer-priority rule.

Use deterministic solver settings and safe symmetry handling.

If final allocations still differ but objective vector is identical, document this rather than changing business policy post-hoc.

---

# 66. Independent audit report requirements

`served_trip_audit.csv` should contain one row per used:

```text
vehicle_id + trip_id
```

Recommended fields:

```text
vehicle_id
trip_id
brand
district

order_count

total_weight_kg
weight_cap_kg
weight_ok

total_volume_m3
volume_cap_m3
volume_ok

trip_minutes_solver
trip_minutes_recomputed
time_match

fresh_minutes_vehicle
fresh_budget_ok

style_tech_minutes_vehicle
style_tech_budget_ok

brand_ok
district_ok
reefer_ok
van_only_ok
home_depot_ok

trip_count_vehicle
max_two_trips_ok

overall_trip_audit_ok
```

Private only.

Do not commit it.

---

# 67. Objective-stage report

Create:

```text
objective_stages.json
```

For each level:

```text
level_id
direction
status
objective_value
best_bound
wall_time_seconds
fixed_for_next_stage
```

Required final state:

```text
all levels OPTIMAL
all fixed_for_next_stage = true
```

before allocation freeze.

---

# 68. Run manifest

Create private:

```text
run_manifest.json
```

Recommended content:

```text
phase = 22

solver = OR-Tools CP-SAT

ortools version

Python version

git commit

input/config hashes

scales

order count

usable vehicle count

assignment variable count

trip-use variable count

group-use variable count

objective strategy

random seed

worker count

time limit

include_return_leg = false

Phase19 compatibility reused = yes

Phase20 time formula reused = yes

Phase21 objective reused = yes

Task1 changed = no

Task2A changed = no
```

Do not expose row-level private details.

---

# 69. Local execution workflow

The real S1 run is local/private.

Recommended command:

```bash
python scripts/run_task2b_optimizer.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --priority-config configs/task2b_priority.yaml \
  --optimizer-config configs/task2b_optimizer.yaml \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --priority-metadata data/interim/task2b_priority_metadata.csv \
  --candidate-output data/interim/task2b_solver_allocation_candidate.csv \
  --trip-summary-output data/interim/task2b_final_trip_summary.csv \
  --report-dir reports/private/phase22_task2b_optimizer
```

After the full run and audit pass:

```bash
python scripts/freeze_task2b_allocation.py \
  --candidate-allocation data/interim/task2b_solver_allocation_candidate.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --optimizer-config configs/task2b_optimizer.yaml \
  --priority-config configs/task2b_priority.yaml \
  --report-dir reports/private/phase22_task2b_optimizer \
  --output data/interim/task2b_final_allocation.csv
```

Use one-line PowerShell variants if required.

Codex must implement the commands but must not inspect private scenario rows in an external context.

---

# 70. Recommended sanitized local result

The console should reveal status, not private order IDs.

Target:

```text
LOCAL PHASE 22 OPTIMIZER: PASS

OR-TOOLS CP-SAT: PASS

MODEL BUILD: PASS

FEASIBILITY SMOKE: PASS

OFFICIAL HARD RULES ENCODED: 7 / 7

LEXICOGRAPHIC OBJECTIVE STAGES: OPTIMAL

LEVEL 1: OPTIMAL
LEVEL 2: OPTIMAL
LEVEL 3: OPTIMAL
LEVEL 4: OPTIMAL
LEVEL 5: OPTIMAL
LEVEL 6: OPTIMAL
LEVEL 7A: OPTIMAL
LEVEL 7B: OPTIMAL
LEVEL 7C: OPTIMAL

INDEPENDENT SERVED-TRIP AUDIT: PASS

MIXED BRAND TRIPS: 0
MIXED DISTRICT TRIPS: 0
CHILLED/NON-REEFER VIOLATIONS: 0
VAN-ONLY/TRUCK VIOLATIONS: 0
WRONG-DEPOT VIOLATIONS: 0
WEIGHT VIOLATIONS: 0
VOLUME VIOLATIONS: 0
VEHICLES WITH >2 TRIPS: 0
FRESH BUDGET VIOLATIONS: 0
STYLE+TECH BUDGET VIOLATIONS: 0

DETERMINISM CHECK: PASS

FINAL ALLOCATION FREEZE: PASS
```

Do not print private counts/IDs unless necessary for local debugging.

---

# 71. STOP conditions

`READY FOR PHASE 23` remains **NO** if any of these occur:

- Phase 19 is not PASS;
- Phase 20 is not PASS;
- Phase 21 is not PASS;
- OR-Tools fails to install/import;
- solver uses a remote service;
- numeric scaling rounds official values;
- assignment variable exists for an officially incompatible pair;
- one order can receive multiple decisions;
- a served order can be split;
- one trip can mix brands;
- one trip can mix districts;
- chilled can use a non-reefer;
- van-only can use a truck;
- wrong-depot assignment is possible;
- trip weight can exceed capacity;
- trip volume can exceed capacity;
- third trip can be used;
- Fresh vehicle minutes can exceed 270;
- Style+Tech vehicle minutes can exceed 480;
- return journey is added;
- CP-SAT trip time differs from Phase 20;
- lexicographic tier order differs from Phase 21;
- lower objective sacrifices a higher-level optimum;
- arbitrary unproven objective weights are introduced;
- final objective stage returns only FEASIBLE under default freeze policy;
- any stage is INFEASIBLE/MODEL_INVALID/UNKNOWN;
- independent served-trip audit fails;
- real allocation is manually edited after solve;
- objective policy is changed after seeing final deferrals;
- final allocation is overwritten after freeze without explicit reopen flow;
- `outputs/submission_task2b.csv` is created prematurely;
- Task 1 frozen artifacts change;
- Task 2A frozen artifacts change;
- private scenario rows are exposed to an external AI agent;
- safe test suite fails;
- `pip check` fails;
- independent Phase 22 review fails.

---

# 72. Definition of Done

Phase 22 is complete only when:

- [ ] DT-299 PASS
- [ ] DT-300 PASS
- [ ] DT-301 PASS
- [ ] DT-302 PASS
- [ ] DT-303 PASS
- [ ] DT-304 PASS
- [ ] DT-305 PASS
- [ ] DT-306 PASS
- [ ] DT-307 PASS
- [ ] DT-308 PASS
- [ ] DT-309 PASS
- [ ] DT-310 PASS
- [ ] DT-311 PASS
- [ ] DT-312 PASS
- [ ] DT-313 PASS
- [ ] DT-314 PASS
- [ ] DT-315 PASS
- [ ] DT-316 PASS
- [ ] DT-317 PASS
- [ ] DT-318 PASS
- [ ] DT-319 PASS
- [ ] OR-Tools CP-SAT is local and reproducible
- [ ] exact decimal scaling exists and never silently rounds
- [ ] assignment variables only cover compatible pairs
- [ ] Phase 19 compatibility is independently sanity-checked
- [ ] each order has exactly one served/deferred decision
- [ ] every served order has exactly one assignment
- [ ] same-brand rule is hard
- [ ] same-district rule is hard
- [ ] chilled→reefer is hard
- [ ] van-only→van is hard
- [ ] home depot is hard
- [ ] weight capacity is hard
- [ ] volume capacity is hard
- [ ] maximum two trips is hard
- [ ] Fresh combined budget ≤270 is hard
- [ ] Style+Tech combined budget ≤480 is hard
- [ ] Phase 20 trip arithmetic is reused exactly
- [ ] no return journey is included
- [ ] Phase 21 lexicographic objective order is exact
- [ ] every lexicographic stage is OPTIMAL before freeze
- [ ] all higher-tier optimum values are fixed before lower-tier solve
- [ ] solution extraction is one row per `order_ref`
- [ ] every served trip independently re-audited
- [ ] solver minutes match Phase 20 recalculation
- [ ] deterministic rerun passes
- [ ] `data/interim/task2b_final_allocation.csv` frozen
- [ ] `data/interim/task2b_final_trip_summary.csv` frozen
- [ ] freeze manifest hashes match
- [ ] normal overwrite of frozen allocation is blocked
- [ ] final official Task 2B submission not yet created
- [ ] synthetic tests pass
- [ ] full safe repository suite passes
- [ ] `python -m pip check` passes
- [ ] private paths are ignored
- [ ] Task 1 remains frozen
- [ ] Task 2A remains frozen
- [ ] independent Phase 22 review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 22 STATUS: PASS
FINAL TASK 2B ALLOCATION: FROZEN
READY FOR PHASE 23: YES
```

---

# 73. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-22-task2b-optimizer
```

Recommended commits:

```text
build(task2b): add local OR-Tools CP-SAT dependency
feat(task2b): add Task 2B solver data and variables
feat(task2b): encode seven official allocation constraints
feat(task2b): add frozen lexicographic policy objective
feat(task2b): add independent solution audit
feat(task2b): add allocation freeze workflow
test(task2b): add Phase 22 constraint and objective tests
docs(task2b): document optimizer formulation and freeze contract
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run the Phase 22 tests.

Then:

```bash
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

Do not stage the private final allocation.

Merge only after:

```text
LOCAL PHASE 22 OPTIMIZER: PASS
INDEPENDENT PHASE 22 REVIEW: PASS
```

---

# 74. Recommended Codex model

This is one of the highest-risk phases in the Datathon.

It combines:

- OR-Tools CP-SAT modelling;
- 21 implementation tasks;
- exact hard constraints;
- trip-time linearization;
- decimal integer scaling;
- sequential lexicographic optimization;
- deterministic extraction;
- independent post-solve audit;
- freeze/reproducibility safeguards.

Recommended:

```text
GPT-5.6 Sol
Reasoning: High
```

If your Codex environment exposes a stronger work/coding model and you have enough usage, this is one of the few phases where escalation is justified.

Lower-token fallback:

```text
GPT-5.6 Terra
Reasoning: High
```

Do **not** use a low-reasoning setting for initial Phase 22 formulation.

After the solver architecture is stable, smaller/faster models are acceptable for narrow test fixes.

---

# 75. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 22 only.

PHASE:
Task 2B Optimization Solver

TASK RANGE:
DT-299 through DT-319

EXECUTION MODE:
HIGH-RISK controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
Use the strongest cost-reasonable coding/reasoning model available.
Preferred in our project plan:
GPT-5.6 Sol — High reasoning

Lower-token fallback:
GPT-5.6 Terra — High reasoning

Do NOT use low reasoning for the initial solver formulation.

You MAY:

- create/edit/refactor Phase 22 tracked source code
- add/configure local OR-Tools
- update requirements using the repository's normal pinning convention
- create configs/docs
- create synthetic solver fixtures
- run targeted pytest tests
- run the complete safe regression suite
- inspect stack traces
- diagnose ordinary implementation failures
- fix ordinary code/model bugs automatically
- rerun failed tests
- run python -m pip check
- inspect git status/diff
- run git diff --check
- verify ignore rules
- self-review against Phase 22 Definition of Done

Do NOT stop for ordinary implementation/test failures that can safely be fixed.

STOP for:

- official Task 2B rule ambiguity
- requirement to expose private competition rows
- Phase 19/20/21 not passing
- unresolved source/reference inconsistency
- solver formulation requiring violation of official rules
- policy-objective conflict with frozen Phase 21
- numeric values that cannot be represented without silent rounding
- material cross-phase design change

DO NOT START PHASE 23.

==================================================
READ FIRST
==================================================

Read completely/targetedly:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 22 section
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. PHASE_20_COMPETITION_CONTRACT.md
7. PHASE_21_COMPETITION_CONTRACT.md
8. PHASE_22_COMPETITION_CONTRACT.md

Then inspect:

9. src/task2b/scenario.py
10. src/task2b/compatibility.py
11. src/task2b/scarcity.py
12. src/task2b/trip_groups.py
13. src/task2b/trip_time.py
14. src/task2b/priority.py
15. src/task2b/policy_metrics.py

16. configs/task2b_scenario.yaml
17. configs/task2b_compatibility.yaml
18. configs/task2b_trip_time.yaml
19. configs/task2b_priority.yaml

20. all existing Task 2B tests

Use existing approved interfaces.

Do not duplicate or reinterpret upstream contracts.

TASK 1 AND TASK 2A ARE FROZEN.

Do NOT modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
outputs/submission_task2a.csv

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect/print real private competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for all Codex-run solver tests.

Implement real-data commands but leave execution to the human operator.

Do not print:

real order_ref values
real vehicle/order assignments
real deferred-order lists
real trip member lists
private objective counts

==================================================
OFFICIAL TASK 2B HARD RULES
==================================================

Encode all seven as HARD constraints:

H1
same brand + same district for all orders on one vehicle_id + trip_id

H2
chilled -> reefer
reefer may carry ambient

H3
van_only -> van

H4
vehicle home depot == order depot

H5
whole order
served order assigned to exactly one vehicle and one trip
no splitting

H6
per trip:
sum weight <= weight_cap_kg
AND
sum volume <= volume_cap_m3

H7
each vehicle <=2 trips

Fresh trip minutes combined per vehicle <=270

Style + Tech trip minutes combined per vehicle <=480

Do NOT import delivery windows, fuel quotas, Task1 lateness, or wider
Hackathon constraints as Task 2B hard rules.

==================================================
OFFICIAL TRIP TIME
==================================================

Reuse Phase 20 EXACTLY.

trip_minutes
=
outbound
+
inter_stop
+
handling

outbound:
depot_to_district_freeflow_min once per trip

inter-stop:
inter_stop_freeflow_min * (n_orders - 1)

handling:
sum service_allowance_min for EVERY order,
lookup by brand + dock_type

RETURN:
DO NOT ADD.

CP-SAT trip-time expressions must match the Phase20 pure calculator in
synthetic parity tests.

==================================================
FROZEN PHASE 21 POLICY
==================================================

Hard feasibility is outside the objective.

Use EXACT lexicographic order:

LEVEL 1 MAX
served_order_count

LEVEL 2 MAX
served_previous_deferred_count

LEVEL 3 MAX
served_waiting_days_sum

LEVEL 4 MAX
served_low_flexibility_count

LEVEL 5 MAX
served_fresh_chilled_count

LEVEL 6 MAX
served_fresh_count

LEVEL 7A MIN
avoidable_reefer_van_assignment_count

LEVEL 7B MIN
avoidable_reefer_assignment_count

LEVEL 7C MIN
avoidable_van_assignment_count

Do not change/reorder tiers after seeing the real allocation.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/solver_data.py

src/task2b/cp_scaling.py

src/task2b/optimizer.py

src/task2b/lexicographic_solver.py

src/task2b/solution.py

src/task2b/solution_audit.py

scripts/run_task2b_optimizer.py

scripts/freeze_task2b_allocation.py

configs/task2b_optimizer.yaml

docs/task2b_optimizer_spec.md

tests/test_task2b_solver_data.py

tests/test_task2b_optimizer_constraints.py

tests/test_task2b_lexicographic_solver.py

tests/test_task2b_solution_audit.py

tests/test_task2b_allocation_freeze.py

Do NOT create the final organizer submission_task2b.csv.

Phase 24 owns final template export.

==================================================
DT-299 — OR-TOOLS
==================================================

Install/configure local:

ortools

Use CP-SAT locally.

Do not call a remote optimization API.

Follow repository dependency pinning convention.

Do not guess an arbitrary latest package version.

Run a tiny synthetic CP-SAT smoke test.

Run:

python -m pip check

Record installed OR-Tools version in private run manifest.

==================================================
EXACT NUMERIC SCALING
==================================================

CP-SAT requires integer coefficients.

Do NOT round official decimals.

Implement exact Decimal-based scaling for:

weight
volume
time

Recommended:

Decimal(str(value))

derive exact scale from decimal precision

convert to integer exactly

reject values that exceed configured supported precision

Do not use approximate float rounding.

Test scale round-trip.

==================================================
CANONICAL SETS
==================================================

Orders:
O

Usable vehicles:
V

Trip slots:
T = {1,2}

Brand+district groups:
G

Each order:
g(o) = (brand, district)

Compatible vehicle set:
C(o)

Only create assignment variables when:

v in C(o)

But independently recheck the official compatibility facts when building
solver data.

If Phase19 compatibility disagrees with official raw/reference facts:
STOP.

==================================================
DT-300 — ORDER ASSIGNMENT VARIABLES
==================================================

For each compatible:

order o
vehicle v
trip t in {1,2}

create:

x[o,v,t] BoolVar

Meaning:

order o served by vehicle v on trip t

Create:

serve[o]
defer[o]

Do not create x for incompatible pairs.

Impossible order with C(o)=empty:
no x variables.

Use deterministic sorted identifiers and stable variable names.

==================================================
DT-301 — VEHICLE/TRIP VARIABLES
==================================================

For every vehicle+trip:

use_trip[v,t] BoolVar

For every vehicle+trip+brand/district group:

use_group[v,t,g] BoolVar

Enforce:

sum_g use_group[v,t,g]
=
use_trip[v,t]

Link assignment:

x[o,v,t]
<=
use_trip[v,t]

x[o,v,t]
<=
use_group[v,t,g(o)]

Prevent empty used trips:

sum_o x[o,v,t]
>=
use_trip[v,t]

and upper-bound assignments by:

safe_M * use_trip[v,t]

Engineering symmetry breaker:

use_trip[v,2] <= use_trip[v,1]

Document as implementation-only, not organizer policy.

==================================================
DT-302 — ONE DECISION PER ORDER
==================================================

For every order:

serve[o] + defer[o] = 1

Exactly one.

Impossible:

serve[o] = 0

defer[o] = 1

==================================================
DT-303 — WHOLE-ORDER ASSIGNMENT
==================================================

For every order:

sum_{v,t} x[o,v,t]
=
serve[o]

Therefore:

served -> exactly one assignment

deferred -> zero assignments

No partial volume.

No split across trips.

No split across vehicles.

==================================================
DT-304 / DT-305 — SAME BRAND + DISTRICT
==================================================

Use group variables.

Every used trip selects exactly one:

brand + district

Assignment only allowed into the order's group.

Therefore a trip can never mix:

brands

or:

districts

Tests must prove both constraints independently.

==================================================
DT-306 — REEFER RULE
==================================================

Only assignment variables satisfying:

chilled -> reefer

may exist.

Recompute/check against vehicle/order facts.

If Phase19 contains chilled+non-reefer compatible pair:
STOP.

Ambient + reefer remains allowed.

==================================================
DT-307 — VAN-ONLY RULE
==================================================

Only assignment variable if:

van_only -> vehicle.type == van

Normal-access orders may use vans.

==================================================
DT-308 — HOME DEPOT
==================================================

Only assignment variable if:

vehicle_home_depot == order.depot

For S1 expected Peliyagoda.

No relabeling.

==================================================
DT-309 — WEIGHT CAPACITY
==================================================

For each vehicle+trip:

sum(
  scaled_weight[o] * x[o,v,t]
)
<=
scaled_weight_capacity[v] * use_trip[v,t]

Combined trip capacity.

Do not rely only on Phase19 individual fit.

Equality valid.

==================================================
DT-310 — VOLUME CAPACITY
==================================================

For each vehicle+trip:

sum(
  scaled_volume[o] * x[o,v,t]
)
<=
scaled_volume_capacity[v] * use_trip[v,t]

Both volume and weight must pass.

==================================================
TRIP MINUTE EXPRESSION
==================================================

Create trip_minutes[v,t].

Use the exact linear Phase20 equivalent.

For selected group g with district d(g):

outbound:
sum_g outbound[d(g)] * use_group[v,t,g]

handling/inter-stop order term:
sum_o (
    service_allowance[o]
    +
    inter_stop[d(o)]
) * x[o,v,t]

subtract one inter-stop rate when trip used:
sum_g inter_stop[d(g)] * use_group[v,t,g]

Thus:

trip_minutes[v,t]
=
outbound group sum
+
order contribution sum
-
selected inter-stop group sum

This yields:

outbound
+
inter_stop*(n_orders-1)
+
handling

No return journey.

Add equality constraint to trip_minutes IntVar.

Test parity against Phase20 pure calculator.

==================================================
DT-311 — MAX TWO TRIPS
==================================================

Trip domain is exactly:

1
2

Explicit:

use_trip[v,1] + use_trip[v,2] <= 2

Do not create trip 3.

Keep:

use_trip[v,2] <= use_trip[v,1]

as safe symmetry breaking.

==================================================
DT-312 — FRESH <=270
==================================================

For every vehicle:

sum of its Fresh trip minutes
<=
270 minutes

Use scaled exact time.

Combined across both trip slots.

Two Fresh trips:

101 + 112 = 213

must pass.

Two Fresh trips with total 271:

must fail.

Exactly 270:
pass.

Fresh minutes must NOT consume Style+Tech 480 budget.

==================================================
DT-313 — STYLE + TECH <=480
==================================================

For every vehicle:

Style trip minutes
+
Tech trip minutes

combined across both trips

<=480.

Do not give separate 480 budgets to Style and Tech.

Exactly 480:
pass.

481:
fail.

Fresh remains separate.

==================================================
DT-314 — LEXICOGRAPHIC OBJECTIVE
==================================================

Implement sequential objective stages.

For each stage:

1. set objective

2. solve

3. require OPTIMAL for final-freeze workflow

4. capture optimum

5. add equality fixing that optimum

6. continue to next level

LEVEL 1:
maximize sum serve[o]

LEVEL 2:
maximize sum deferred_yesterday[o]*serve[o]

LEVEL 3:
maximize sum days_since_last_served[o]*serve[o]

LEVEL 4:
maximize sum is_low_flexibility[o]*serve[o]

LEVEL 5:
maximize sum is_fresh_chilled[o]*serve[o]

LEVEL 6:
maximize sum is_fresh[o]*serve[o]

LEVEL 7A:
minimize avoidable reefer-van assignment count

LEVEL 7B:
minimize avoidable reefer assignment count

LEVEL 7C:
minimize avoidable van assignment count

Never let a lower stage reduce any fixed higher-stage optimum.

==================================================
AVOIDABLE SPECIALIZED ASSIGNMENTS
==================================================

For assignment x[o,v,t]:

REEFER VAN AVOIDABLE COST = 1 when:

vehicle is van+reefer

AND

order has_non_reefer_van_alternative

Otherwise 0.

REEFER AVOIDABLE COST = 1 when:

vehicle is reefer

AND

order has_non_reefer_alternative

Otherwise 0.

VAN AVOIDABLE COST = 1 when:

vehicle is van

AND

order has_non_van_alternative

Otherwise 0.

Necessary specialized usage is not penalized as avoidable.

==================================================
DT-315 — INITIAL FEASIBLE ALLOCATION
==================================================

Run a feasibility smoke solve before full policy optimization.

Purpose:

model validity

constraint consistency

basic solution extraction

Accepted smoke status:

FEASIBLE
or
OPTIMAL

Do not freeze this smoke result.

Because deferral is allowed, INFEASIBLE usually signals a modelling or
data-contract problem.

Then run the complete lexicographic solve.

==================================================
DT-316 — SOLVER STATUS
==================================================

Handle explicitly:

OPTIMAL
FEASIBLE
INFEASIBLE
MODEL_INVALID
UNKNOWN

For initial smoke:

FEASIBLE/OPTIMAL acceptable.

For every lexicographic stage under default freeze contract:

OPTIMAL required.

FEASIBLE-only:
debug/tune, but do not freeze.

INFEASIBLE:
block.

MODEL_INVALID:
block.

UNKNOWN:
block.

Record stage:

status
objective
best bound
wall time
branches/conflicts where available.

==================================================
SOLUTION EXTRACTION
==================================================

Create one private row per order_ref:

scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

served:
vehicle populated
trip_id 1 or 2

deferred:
vehicle blank
trip blank

Use deterministic/original order sequence.

Also build private trip summary by:

vehicle_id + trip_id

with:

brand
district
order count
weight
volume
capacity
Phase20 time breakdown
budget group

==================================================
DT-317 — INDEPENDENT SERVED-TRIP AUDIT
==================================================

Do NOT trust the solver model alone.

After extraction, recompute all rules independently using ordinary
dataframe/Python logic and canonical Phase19/20 helpers.

Audit:

every order exactly one decision

served fields populated

deferred fields blank

assigned vehicle available/not workshop

one brand per trip

one district per trip

chilled -> reefer

van_only -> van

home depot match

whole order assigned once

trip weight <= cap

trip volume <= cap

trip time recomputed with Phase20

solver trip minutes == recomputed minutes

vehicle trip count <=2

vehicle Fresh minutes <=270

vehicle Style+Tech minutes <=480

Any failure:
DO NOT FREEZE.

This is still separate from the formal Phase23 validator/checker.

==================================================
DT-318 — TUNE PRIORITIZATION OBJECTIVE
==================================================

Phase21 policy meaning is already FROZEN.

Allowed tuning ONLY:

solver time limit

CP-SAT search parameters

variable filtering

linear formulation efficiency

safe symmetry breaking

solver hints

deterministic ordering

mathematically equivalent lexicographic encoding

Not allowed:

reorder tiers

change low-flex threshold

add/remove policy signal

make Fresh more important based on output

drop fairness

soften hard rule

change policy because a particular real order was deferred

Recommended process:

if all objective stages OPTIMAL + audit PASS:
do not change policy.

if stage is FEASIBLE-only/slow:
tune solver mechanics only.

Then rerun from Stage 1.

==================================================
DETERMINISM
==================================================

Recommended final:

random_seed = 42

num_search_workers = 1

stable sorted construction

Run final solve twice.

Require:

same objective vector

same audit result

prefer same allocation.

Do not invent new customer priority simply to break equivalent-optimum
symmetry.

==================================================
DT-319 — FREEZE FINAL ALLOCATION
==================================================

Freeze only when:

all lexicographic stages OPTIMAL

all 7 hard rules pass independent audit

trip-time parity PASS

objective hierarchy exact

determinism PASS

Write private canonical:

data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv

Create private freeze manifest with:

state = FROZEN

solver/version

config hashes

allocation SHA256

trip summary SHA256

objective strategy/vector

all stage statuses

audit PASS

git commit

timestamp

After freeze:

normal optimizer command must refuse to overwrite the canonical allocation.

Do not create final submission_task2b.csv yet.

==================================================
FREEZE REOPEN RULE
==================================================

If Phase23 later finds a failure:

Do NOT manually edit final allocation CSV.

Explicitly reopen Phase22.

Fix the model.

Rerun full lexicographic solve.

Rerun independent audit.

Freeze a new allocation/hash.

Then rerun Phase23.

==================================================
REQUIRED TESTS
==================================================

Create:

tests/test_task2b_solver_data.py

tests/test_task2b_optimizer_constraints.py

tests/test_task2b_lexicographic_solver.py

tests/test_task2b_solution_audit.py

tests/test_task2b_allocation_freeze.py

Use synthetic data only.

Test:

OR-TOOLS:
local smoke model OPTIMAL

SCALING:
exact decimal conversion
no silent rounding
round-trip

VARIABLES:
compatible-only assignment vars
two trip slots
impossible no-x
deterministic names

DECISION:
serve+defer=1
impossible forced defer

WHOLE ORDER:
served exactly one assignment
deferred zero
no split

BRAND/DISTRICT:
mixed brand impossible
mixed district impossible

REEFER:
chilled reefer only
ambient reefer allowed

VAN:
van-only van only
normal van allowed

DEPOT:
match only

WEIGHT:
combined trip capacity

VOLUME:
combined trip capacity

TRIPS:
0/1/2 allowed
no 3
trip2 symmetry

TIME:
Phase20 parity
one order
multi order
101 example
112 example
no return

FRESH:
exact 270 pass
271 fail
combined two trips

STYLE+TECH:
exact 480 pass
481 fail
Style+Tech combined

OBJECTIVE:
all Phase21 dominance relationships

STATUS:
FEASIBLE smoke accepted
OPTIMAL stage required
other statuses blocked

AUDIT:
one deliberate failure per official rule detected

TUNING GUARD:
policy reorder rejected

FREEZE:
hashes
overwrite block
state FROZEN

END-TO-END:
synthetic scenario
→ solve
→ audit
→ freeze
→ deterministic rerun

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-299:
run OR-Tools/scaling smoke tests.

After DT-300–303:
run variable/decision/whole-order tests.

After DT-304–313:
run every hard-constraint test.

Do not continue if any official hard-rule test is red.

After DT-314:
run lexicographic hierarchy tests.

After DT-315–317:
run status/extraction/independent-audit tests.

After DT-318–319:
run tuning-guard/freeze/determinism tests.

Fix ordinary engineering defects automatically.

Do NOT alter official rules or Phase21 policy ordering to make tests pass.

Then run all Task2B safe tests.

At minimum:

pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_compatibility.py \
  tests/test_task2b_scarcity.py \
  tests/test_task2b_trip_groups.py \
  tests/test_task2b_trip_time.py \
  tests/test_task2b_priority.py \
  tests/test_task2b_policy_metrics.py \
  tests/test_task2b_solver_data.py \
  tests/test_task2b_optimizer_constraints.py \
  tests/test_task2b_lexicographic_solver.py \
  tests/test_task2b_solution_audit.py \
  tests/test_task2b_allocation_freeze.py

Then:

pytest -q

python -m pip check

git status

git diff

git diff --check

If real private scenario data is required:

do NOT inspect it in Codex.

Return the exact local human command.

Verify no private paths are staged.

==================================================
LOCAL HUMAN OPTIMIZER COMMAND
==================================================

Implement but DO NOT execute real private scenario data inside Codex:

python scripts/run_task2b_optimizer.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --priority-config configs/task2b_priority.yaml \
  --optimizer-config configs/task2b_optimizer.yaml \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --priority-metadata data/interim/task2b_priority_metadata.csv \
  --candidate-output data/interim/task2b_solver_allocation_candidate.csv \
  --trip-summary-output data/interim/task2b_final_trip_summary.csv \
  --report-dir reports/private/phase22_task2b_optimizer

==================================================
LOCAL FREEZE COMMAND
==================================================

After optimizer + independent audit PASS:

python scripts/freeze_task2b_allocation.py \
  --candidate-allocation data/interim/task2b_solver_allocation_candidate.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --optimizer-config configs/task2b_optimizer.yaml \
  --priority-config configs/task2b_priority.yaml \
  --report-dir reports/private/phase22_task2b_optimizer \
  --output data/interim/task2b_final_allocation.csv

Console output must remain sanitized.

Do not print private order assignments.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase19 not PASS

Phase20 not PASS

Phase21 not PASS

OR-Tools unavailable

remote solver used

numeric values rounded

incompatible assignment variable created

one decision per order not enforced

order splitting possible

mixed brand trip possible

mixed district trip possible

chilled non-reefer possible

van-only truck possible

wrong depot possible

weight over-cap possible

volume over-cap possible

third trip possible

Fresh >270 possible

Style+Tech >480 possible

return leg added

solver time != Phase20 calculator

objective order differs from Phase21

lower tier can sacrifice higher tier

unproven weighted objective replaces lexicographic

objective stage not OPTIMAL for freeze

solver status invalid/infeasible/unknown

independent audit fails

policy changed after seeing final deferrals

manual edit used to fix allocation

frozen allocation overwritten silently

final submission_task2b.csv created early

Task1 changes

Task2A changes

private rows must be exposed

tests cannot pass under official contract

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-299 READY
DT-300 READY
DT-301 READY
DT-302 READY
DT-303 READY
DT-304 READY
DT-305 READY
DT-306 READY
DT-307 READY
DT-308 READY
DT-309 READY
DT-310 READY
DT-311 READY
DT-312 READY
DT-313 READY
DT-314 READY
DT-315 READY
DT-316 READY
DT-317 READY
DT-318 READY
DT-319 READY

OR-Tools local

exact numeric scaling

assignment domain safe

decision constraint safe

whole order safe

brand safe

district safe

reefer safe

van-only safe

depot safe

weight safe

volume safe

max trips safe

Fresh budget safe

Style+Tech budget safe

Phase20 time parity

Phase21 objective exact

all objective stages OPTIMAL-capable

status handling complete

solution extraction complete

independent audit complete

tuning boundary guarded

determinism checked

freeze workflow complete

no Phase23 implementation

no Task2B official submission yet

safe tests pass

full suite passes

pip check passes

private paths ignored

Task1 unchanged

Task2A unchanged

==================================================
RETURN ONLY
==================================================

PHASE:
22 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-299 READY / FAIL
DT-300 READY / FAIL
DT-301 READY / FAIL
DT-302 READY / FAIL
DT-303 READY / FAIL
DT-304 READY / FAIL
DT-305 READY / FAIL
DT-306 READY / FAIL
DT-307 READY / FAIL
DT-308 READY / FAIL
DT-309 READY / FAIL
DT-310 READY / FAIL
DT-311 READY / FAIL
DT-312 READY / FAIL
DT-313 READY / FAIL
DT-314 READY / FAIL
DT-315 READY / FAIL
DT-316 READY / FAIL
DT-317 READY / FAIL
DT-318 READY / FAIL
DT-319 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

OR-TOOLS CP-SAT:
PASS / FAIL

EXACT NUMERIC SCALING:
PASS / FAIL

ORDER DECISION MODEL:
PASS / FAIL

WHOLE-ORDER ASSIGNMENT:
PASS / FAIL

SAME-BRAND RULE:
PASS / FAIL

SAME-DISTRICT RULE:
PASS / FAIL

REEFER RULE:
PASS / FAIL

VAN-ONLY RULE:
PASS / FAIL

HOME-DEPOT RULE:
PASS / FAIL

WEIGHT CAPACITY:
PASS / FAIL

VOLUME CAPACITY:
PASS / FAIL

MAX TWO TRIPS:
PASS / FAIL

FRESH <=270:
PASS / FAIL

STYLE+TECH <=480:
PASS / FAIL

PHASE20 TRIP-TIME PARITY:
PASS / FAIL

PHASE21 LEXICOGRAPHIC OBJECTIVE:
PASS / FAIL

OBJECTIVE STAGE OPTIMALITY:
PASS / FAIL

SOLVER STATUS HANDLING:
PASS / FAIL

INDEPENDENT SERVED-TRIP AUDIT:
PASS / FAIL

OBJECTIVE-TUNING POLICY GUARD:
PASS / FAIL

DETERMINISM:
PASS / FAIL

ALLOCATION FREEZE WORKFLOW:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local optimizer command
2. exact local freeze command

PHASE 22 STATUS:
AWAITING LOCAL OPTIMIZER RUN

FINAL TASK 2B ALLOCATION:
NOT YET FROZEN

READY FOR PHASE 23:
NO

Then STOP.

Do not start Phase 23.
```

---

# 76. Independent Phase 22 review prompt

Use a fresh Codex/Cursor session after the local optimizer and freeze both pass.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 22.

Do NOT implement Phase 23.
Do NOT run the real private S1 optimizer.
Do NOT inspect private row-level allocation data.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 22
4. PHASE_19_COMPETITION_CONTRACT.md
5. PHASE_20_COMPETITION_CONTRACT.md
6. PHASE_21_COMPETITION_CONTRACT.md
7. PHASE_22_COMPETITION_CONTRACT.md

8. src/task2b/solver_data.py
9. src/task2b/cp_scaling.py
10. src/task2b/optimizer.py
11. src/task2b/lexicographic_solver.py
12. src/task2b/solution.py
13. src/task2b/solution_audit.py

14. scripts/run_task2b_optimizer.py
15. scripts/freeze_task2b_allocation.py

16. configs/task2b_optimizer.yaml
17. configs/task2b_priority.yaml
18. configs/task2b_trip_time.yaml
19. configs/task2b_compatibility.yaml

20. docs/task2b_optimizer_spec.md

21. tests/test_task2b_solver_data.py
22. tests/test_task2b_optimizer_constraints.py
23. tests/test_task2b_lexicographic_solver.py
24. tests/test_task2b_solution_audit.py
25. tests/test_task2b_allocation_freeze.py

26. .gitignore
27. .cursorignore if present

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 22 OPTIMIZER: <PASS/FAIL>

OR-TOOLS CP-SAT: <PASS/FAIL>
MODEL BUILD: <PASS/FAIL>
FEASIBILITY SMOKE: <PASS/FAIL>

OFFICIAL HARD RULES ENCODED: <7/7 or other>

LEXICOGRAPHIC OBJECTIVE STAGES: <OPTIMAL / other>

LEVEL 1: <status>
LEVEL 2: <status>
LEVEL 3: <status>
LEVEL 4: <status>
LEVEL 5: <status>
LEVEL 6: <status>
LEVEL 7A: <status>
LEVEL 7B: <status>
LEVEL 7C: <status>

INDEPENDENT SERVED-TRIP AUDIT: <PASS/FAIL>

MIXED BRAND TRIPS: <0/nonzero>
MIXED DISTRICT TRIPS: <0/nonzero>
CHILLED/NON-REEFER VIOLATIONS: <0/nonzero>
VAN-ONLY/TRUCK VIOLATIONS: <0/nonzero>
WRONG-DEPOT VIOLATIONS: <0/nonzero>
WEIGHT VIOLATIONS: <0/nonzero>
VOLUME VIOLATIONS: <0/nonzero>
VEHICLES WITH >2 TRIPS: <0/nonzero>
FRESH BUDGET VIOLATIONS: <0/nonzero>
STYLE+TECH BUDGET VIOLATIONS: <0/nonzero>

DETERMINISM CHECK: <PASS/FAIL>
FINAL ALLOCATION FREEZE: <PASS/FAIL>

Do not ask the human for the private allocation rows.

==================================================
AUDIT EVERY MASTER TASK
==================================================

DT-299:
OR-Tools local CP-SAT configured safely.

DT-300:
assignment variables only for compatible order/vehicle pairs.

DT-301:
trip-use/group variables correctly linked and empty trips impossible.

DT-302:
one served/deferred decision per order.

DT-303:
whole order exactly one assignment when served.

DT-304:
same brand hard constraint.

DT-305:
same district hard constraint.

DT-306:
chilled->reefer, ambient->reefer still allowed.

DT-307:
van_only->van.

DT-308:
home depot hard rule.

DT-309:
combined trip weight constraint.

DT-310:
combined trip volume constraint.

DT-311:
at most two trips.

DT-312:
Fresh combined <=270 per vehicle.

DT-313:
Style+Tech combined <=480 per vehicle.

DT-314:
Phase21 lexicographic objective exactly reproduced.

DT-315:
initial feasibility solve exists and is not the final freeze.

DT-316:
all CP-SAT statuses handled safely.

DT-317:
independent post-extraction audit recomputes rules, including Phase20 time.

DT-318:
tuning cannot modify policy meaning.

DT-319:
freeze requires optimal stages, passing audit and hashes; overwrite protected.

==================================================
CRITICAL FORMULA AUDIT
==================================================

Verify CP-SAT trip minutes are mathematically equivalent to:

outbound
+
inter_stop*(n_orders-1)
+
sum(service allowance)

No return.

Verify synthetic parity tests include:

101-minute Gampaha example

112-minute Colombo example

==================================================
CRITICAL OBJECTIVE AUDIT
==================================================

Exact order:

1 max served count

2 max previous-deferred served

3 max served waiting-days sum

4 max low-flexibility served

5 max Fresh chilled served

6 max Fresh served

7A min avoidable reefer-van use

7B min avoidable reefer use

7C min avoidable van use

Hard feasibility is outside the objective.

Every optimum fixed before next stage.

No arbitrary big-weight policy.

==================================================
CRITICAL FREEZE AUDIT
==================================================

Verify:

all objective stages must be OPTIMAL for freeze

independent audit required

determinism check required

allocation hash stored

trip summary hash stored

normal overwrite blocked

no manual post-solve editing path

no final outputs/submission_task2b.csv created in Phase22

==================================================
RUN SAFE TESTS
==================================================

Run relevant Task2B suite, including:

pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_compatibility.py \
  tests/test_task2b_scarcity.py \
  tests/test_task2b_trip_groups.py \
  tests/test_task2b_trip_time.py \
  tests/test_task2b_priority.py \
  tests/test_task2b_policy_metrics.py \
  tests/test_task2b_solver_data.py \
  tests/test_task2b_optimizer_constraints.py \
  tests/test_task2b_lexicographic_solver.py \
  tests/test_task2b_solution_audit.py \
  tests/test_task2b_allocation_freeze.py

Then:

pytest -q

python -m pip check

git status

git diff --check

Do not execute real optimizer/freeze on private data.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OR-TOOLS LOCAL SOLVER:
PASS / FAIL

EXACT SCALING:
PASS / FAIL

SEVEN HARD RULES:
PASS / FAIL

PHASE20 TIME PARITY:
PASS / FAIL

PHASE21 OBJECTIVE PARITY:
PASS / FAIL

LEXICOGRAPHIC OPTIMALITY GUARD:
PASS / FAIL

SOLVER STATUS SAFETY:
PASS / FAIL

INDEPENDENT AUDIT:
PASS / FAIL

DETERMINISM:
PASS / FAIL

FREEZE INTEGRITY:
PASS / FAIL

NO FINAL SUBMISSION YET:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN LOCAL OPTIMIZER RUN:
PASS / FAIL

HUMAN LOCAL FREEZE:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-299: PASS/FAIL
DT-300: PASS/FAIL
DT-301: PASS/FAIL
DT-302: PASS/FAIL
DT-303: PASS/FAIL
DT-304: PASS/FAIL
DT-305: PASS/FAIL
DT-306: PASS/FAIL
DT-307: PASS/FAIL
DT-308: PASS/FAIL
DT-309: PASS/FAIL
DT-310: PASS/FAIL
DT-311: PASS/FAIL
DT-312: PASS/FAIL
DT-313: PASS/FAIL
DT-314: PASS/FAIL
DT-315: PASS/FAIL
DT-316: PASS/FAIL
DT-317: PASS/FAIL
DT-318: PASS/FAIL
DT-319: PASS/FAIL

PHASE 22 REVIEW:
PASS / FAIL

FINAL TASK 2B ALLOCATION:
FROZEN / NOT FROZEN

READY FOR PHASE 23:
YES / NO

If FAIL:
list exact blockers only.

Do not automatically change policy or official constraints.
Do not start Phase 23.
```

---

# 77. Completion record

```markdown
# Phase 22 Completion Record

## Tasks

- [ ] DT-299
- [ ] DT-300
- [ ] DT-301
- [ ] DT-302
- [ ] DT-303
- [ ] DT-304
- [ ] DT-305
- [ ] DT-306
- [ ] DT-307
- [ ] DT-308
- [ ] DT-309
- [ ] DT-310
- [ ] DT-311
- [ ] DT-312
- [ ] DT-313
- [ ] DT-314
- [ ] DT-315
- [ ] DT-316
- [ ] DT-317
- [ ] DT-318
- [ ] DT-319

## Solver

- [ ] OR-Tools local
- [ ] exact scaling
- [ ] hard rules 7/7
- [ ] Phase20 time parity
- [ ] Phase21 objective parity
- [ ] all lexicographic stages optimal

## Audit

- [ ] served-trip audit PASS
- [ ] Fresh budgets PASS
- [ ] Style+Tech budgets PASS
- [ ] deterministic rerun PASS

## Freeze

- [ ] allocation frozen
- [ ] trip summary frozen
- [ ] SHA256 hashes recorded
- [ ] overwrite protection active

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- private allocation exposed to AI: NO
- final Task2B submission created: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 22 STATUS: PASS / FAIL
FINAL TASK 2B ALLOCATION: FROZEN / NOT FROZEN
READY FOR PHASE 23: YES / NO
```

---

# 78. Final checklist

Before Phase 23:

- [ ] Phases 19–21 passed.
- [ ] OR-Tools is local.
- [ ] exact numeric scaling is proven.
- [ ] assignment domain excludes incompatible pairs.
- [ ] each order has exactly one decision.
- [ ] served order has exactly one assignment.
- [ ] same brand enforced.
- [ ] same district enforced.
- [ ] chilled→reefer enforced.
- [ ] van-only→van enforced.
- [ ] home depot enforced.
- [ ] weight capacity enforced.
- [ ] volume capacity enforced.
- [ ] max two trips enforced.
- [ ] Fresh combined minutes ≤270.
- [ ] Style+Tech combined minutes ≤480.
- [ ] no return journey.
- [ ] CP-SAT time equals Phase20 calculation.
- [ ] Phase21 objective ordering exact.
- [ ] all objective stages OPTIMAL.
- [ ] independent served-trip audit PASS.
- [ ] deterministic rerun PASS.
- [ ] final allocation frozen.
- [ ] freeze hash recorded.
- [ ] freeze overwrite protection active.
- [ ] no manual post-solve row editing.
- [ ] no final `submission_task2b.csv` yet.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.
- [ ] private allocation remains private.
- [ ] independent Phase22 review PASS.

Only then:

```text
PHASE 22 STATUS: PASS
FINAL TASK 2B ALLOCATION: FROZEN
READY FOR PHASE 23: YES
```
