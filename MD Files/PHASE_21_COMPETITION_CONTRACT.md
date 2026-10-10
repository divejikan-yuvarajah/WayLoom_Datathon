# PHASE 21 — Task 2B Priority-Policy Design

> **Filename:** `PHASE_21_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 21 — Task 2B Priority-Policy Design  
> **Task range:** **DT-293 → DT-298**  
> **Task count:** **6**  
> **Default phase priority:** P1  
> **Dependency:** Phases 18–20  
> **Phase gate:** A transparent prioritization policy is documented separately from the seven official hard feasibility rules.  
> **Execution style:** Policy definition + deterministic objective specification + rationale + synthetic tests.  
> **Do not run the allocation optimizer or produce the final Task 2B allocation in this phase.**

---

# 1. Purpose

Phase 21 defines **what WayLoom means by a good Task 2B allocation** before Phase 22 builds the optimization solver.

The official challenge deliberately does not prescribe one optimal allocation. It requires:

- a complete served/deferred allocation;
- a vehicle/trip assignment for served orders;
- a short written policy explaining prioritization and deferral decisions.

The organizer states that there is **no single correct allocation** and that judges assess:

```text
feasibility
+
reasoning behind prioritization
+
reasoning behind deferrals
```

Therefore Phase 21 must create an explicit, auditable policy that can later be translated into a solver objective.

This policy must answer:

- What outcome are we trying to maximize?
- How do we treat orders skipped yesterday?
- How do we use `days_since_last_served` fairly?
- How do we respond to scarce reefers and reefer vans?
- How much weight do we give the S1 business context that Fresh demand is rising one week before a festival?
- How do we distinguish fairness from business urgency?
- How do we prevent scarce specialized vehicles from being consumed unnecessarily?
- How do we explain deferrals without pretending the policy is an official rule?
- Should Phase 22 use a weighted objective or lexicographic objective?

Phase 21 produces the policy contract.

Phase 22 implements it.

---

# 2. Finalized Phase 21 task inventory

The finalized WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-293** | [E] | P1 | DT-271–DT-292 | Decide what good allocation means |
| [ ] | **DT-294** | [E] | P1 | Phases 18–20 | Design transparent prioritization policy |
| [ ] | **DT-295** | [E] | P1 | Phases 18–20 | Distinguish hard rules from our priority policy |
| [ ] | **DT-296** | [E] | P1 | Phases 18–20 | Decide lexicographic or weighted objective |
| [ ] | **DT-297** | [E] | P1 | Phases 18–20 | Document fairness rationale |
| [ ] | **DT-298** | [E] | P1 | Phases 18–20 | Document business rationale |

**Expected Phase 21 tasks:** 6  
**Phase complete:** [ ]  
**READY FOR PHASE 22:** NO

---

# 3. Official source facts relevant to priority policy

## 3.1 Organizer does not define one correct priority order

The official brief does **not** say:

```text
Fresh must always beat Style
Style must always beat Tech
older orders must always be served
deferred_yesterday must always be served
largest-volume orders must be served first
```

Do not present any such policy as an official requirement.

Those would be WayLoom choices.

---

## 3.2 Official scenario context

Scenario S1:

```text
depot = Peliyagoda

festival = one week away

Fresh demand = rising,
including dairy, meat and produce

payday = no

monsoon = no

several vehicles = in workshop
```

These are organizer-provided context facts.

They may inform the policy.

They do not override hard feasibility.

---

## 3.3 Official fairness-relevant fields

The scenario data contains:

```text
deferred_yesterday
```

meaning:

```text
1 if the outlet was skipped on the previous run
```

and:

```text
days_since_last_served
```

meaning:

```text
days since the outlet last received a delivery
```

These are legitimate, transparent policy signals.

The organizer does not prescribe the exact formula or thresholds for using them.

---

## 3.4 Official scarcity context

The official hard rules make some resources specialized:

```text
chilled
→ reefer

van_only
→ van

chilled + van_only
→ reefer van
```

Phase 19 should already quantify:

```text
compatible_vehicle_count
singleton orders
low-flexibility orders
reefer pressure
reefer-van pressure
```

Phase 21 may use these as **scarcity/flexibility signals**.

Do not turn them into new feasibility rules.

---

# 4. The most important separation in Phase 21

WayLoom must maintain three distinct layers.

## Layer A — Official hard feasibility rules

These cannot be violated.

They determine whether an allocation is valid.

## Layer B — WayLoom priority policy

These decide which **feasible** orders are preferred when capacity is insufficient.

They are engineering/business choices.

## Layer C — Solver tie-breaking/resource stewardship

These choose among allocations that are equivalent on the higher policy goals.

They must not quietly become hidden business rules.

This distinction must appear in:

```text
docs/task2b_policy.md
configs/task2b_priority.yaml
Phase 22 objective implementation
final written Task 2B policy
```

---

# 5. Official hard rules — immutable

Phase 21 must reproduce these accurately in its policy documentation but must not relabel them as preference signals.

## H1 — same brand + district per trip

Orders on the same:

```text
vehicle_id + trip_id
```

must share:

```text
brand
district
```

## H2 — refrigeration

```text
chilled → reefer
```

Reefer may carry ambient.

## H3 — access

```text
van_only → van
```

## H4 — home depot

Vehicle home depot must match the order/outlet depot.

S1 is Peliyagoda.

## H5 — whole order

No splitting.

One served order gets one vehicle and one trip.

## H6 — capacity

Per trip:

```text
sum weight <= weight_cap_kg

sum volume <= volume_cap_m3
```

## H7 — trips and time

```text
max 2 trips per vehicle

Fresh minutes <= 270 per vehicle

Style + Tech minutes <= 480 per vehicle
```

using the official Phase 20 trip-time formula.

---

# 6. Fields that must NOT become unofficial hard rules

The Task 2B input includes other fields such as:

```text
window_open_time
window_close_time
mall_window
dock_type
```

`dock_type` is used by the official service-allowance trip-time formula.

However, the seven official Task 2B feasibility rules do not define delivery-window feasibility or fuel constraints as additional Task 2B hard rules.

Therefore Phase 21 must not silently introduce:

```text
delivery-window constraint
fuel quota constraint
Hackathon route constraint
Task 1 lateness constraint
```

into the Task 2B objective/feasibility contract.

If the official checker/source later proves otherwise, revise explicitly.

Do not import unrelated Hackathon rules.

---

# 7. Recommended repository additions

Create/update:

```text
src/task2b/priority.py
src/task2b/policy_metrics.py

scripts/build_task2b_priority_context.py

configs/task2b_priority.yaml

docs/task2b_policy.md
docs/task2b_priority_spec.md

tests/test_task2b_priority.py
tests/test_task2b_policy_metrics.py
```

Reuse:

```text
src/task2b/scenario.py
src/task2b/compatibility.py
src/task2b/scarcity.py
src/task2b/trip_time.py
```

Do not create or run final solver logic yet.

Phase 22 owns:

```text
optimizer.py
solver variables
assignment decisions
served/deferred solution
objective execution
```

---

# 8. Phase 21 output artifacts

Tracked:

```text
configs/task2b_priority.yaml
docs/task2b_policy.md
docs/task2b_priority_spec.md
src/task2b/priority.py
src/task2b/policy_metrics.py
tests/test_task2b_priority.py
tests/test_task2b_policy_metrics.py
```

Private/local:

```text
data/interim/task2b_priority_metadata.csv

reports/private/phase21_task2b_priority/
├── policy_context_summary.json
├── priority_signal_coverage.json
├── fairness_context.json
├── business_context.json
├── scarcity_context.json
├── objective_spec_validation.json
├── warnings.json
└── phase21_policy_context_report.md
```

The tracked policy must not embed private scenario row lists or private counts unless explicitly authorized.

---

# 9. Canonical policy signals

Phase 21 uses only transparent fields that exist before allocation.

Recommended signals:

```text
deferred_yesterday

days_since_last_served

brand

temp_requirement

compatible_vehicle_count

individually_impossible

low_flexibility

singleton_compatibility
```

Optional resource-stewardship metadata for later assignment tie-breaking:

```text
order_has_non_reefer_alternative

order_has_non_van_alternative

order_has_non_reefer_van_alternative
```

These should be derived from Phase 19 compatibility.

Do not use final solver outcomes as priority inputs.

---

# 10. Default WayLoom policy choice

## Chosen structure

WayLoom will use a:

```text
LEXICOGRAPHIC OBJECTIVE
```

not one single arbitrary weighted score.

This is an engineering decision, not an official requirement.

### Why lexicographic

It is more transparent because:

- higher-level policy goals cannot be traded away by a large lower-level numerical weight;
- judges can understand the policy in plain language;
- there is no need to pretend that "one deferred order equals 17.3 units of Fresh urgency";
- fairness and business goals remain auditable;
- solver behavior can be explained tier by tier.

Phase 22 may encode lexicographic solving using sequential optimization stages or a rigorously proven equivalent scaling.

Do **not** use huge unproven "big weights" that risk objective overflow or unintended trade-offs.

---

# 11. Frozen lexicographic priority order

The recommended WayLoom policy for Phase 22 is:

## Level 1 — Maximize total served orders

```text
maximize:
number of individually feasible orders served
```

Why first:

- demand exceeds capacity;
- broad service coverage is easy to explain;
- prevents one very large or high-score order from crowding out many feasible orders without explicit reason.

Individually impossible orders are excluded from the feasible served set by hard constraints, not by the policy.

---

## Level 2 — Maximize previously deferred orders served

Among allocations with the same maximum served-order count:

```text
maximize:
sum(served_i * deferred_yesterday_i)
```

Why:

- directly addresses backlog from the previous run;
- is grounded in an official scenario field;
- provides a clear fairness explanation.

This is not a guarantee that every previously deferred order is served.

Hard feasibility and higher-level total coverage still apply.

---

## Level 3 — Maximize service-recency fairness

Among allocations tied on Levels 1–2:

```text
maximize:
sum(
  served_i * days_since_last_served_i
)
```

Why:

- gives preference to outlets that have waited longer;
- reduces repeated neglect;
- uses an official scenario field.

Important:

This is a tiebreaking fairness objective, not a hard service entitlement.

---

## Level 4 — Maximize low-flexibility order coverage

Among allocations tied on Levels 1–3:

```text
maximize:
number of served orders with:
0 < compatible_vehicle_count <= low_flexibility_threshold
```

Default engineering threshold:

```text
2
```

Why:

- an order with one or two compatible vehicles has fewer recovery options than a flexible order;
- it helps avoid leaving constrained orders until all specialized capacity is already consumed.

Important:

This does not override feasibility.

Individually impossible:

```text
compatible_vehicle_count = 0
```

cannot be made feasible by priority.

---

## Level 5 — Maximize Fresh chilled coverage

Among allocations tied above:

```text
maximize:
served orders where:
brand = Fresh
AND
temp_requirement = chilled
```

Why:

- official S1 context says Fresh demand is rising one week before a festival;
- the example specifically mentions dairy, meat and produce;
- chilled demand depends on scarce refrigerated capacity.

This is a **business-context tiebreaker**, not an official mandate.

---

## Level 6 — Maximize overall Fresh coverage

Among allocations still tied:

```text
maximize:
served orders where brand = Fresh
```

Why:

- S1 specifically calls out rising Fresh demand.

Again:

```text
Fresh priority is WayLoom policy,
not organizer hard rule.
```

---

## Level 7 — Minimize avoidable specialized-vehicle use

Among allocations with identical service/fairness/business outcomes, prefer assignments that conserve specialized capacity.

Recommended sub-order:

### 7A

Minimize:

```text
avoidable reefer-van assignments
```

where the served order has another compatible vehicle that is not a reefer van.

### 7B

Minimize:

```text
avoidable reefer assignments
```

for ambient orders that have a compatible non-reefer alternative.

### 7C

Minimize:

```text
avoidable van assignments
```

for non-van-only orders that have a compatible non-van alternative.

Why:

- preserves scarce flexibility;
- aligns with Phase 19 bottleneck analysis;
- only operates after higher policy outcomes are fixed.

This is resource stewardship, not a hard rule.

---

# 12. Why total served orders is Level 1

A policy could instead put backlog fairness first.

WayLoom deliberately chooses:

```text
served-order coverage first
```

because otherwise one previously deferred, very large order could theoretically force the solver to sacrifice many feasible orders solely to satisfy the first lexicographic tier.

That tradeoff would be difficult to justify without an official instruction.

By putting total served count first:

- the plan serves as many confirmed orders as possible;
- fairness then decides who gets the limited slots among equally broad allocations;
- business urgency and scarcity are still respected as later tiers.

This is a deliberate engineering decision.

Document it.

---

# 13. Why the policy does not maximize volume first

WayLoom does not make:

```text
total served m3
```

the primary objective.

Reason:

- volume-first can favor a small number of very large orders;
- Task 2B asks for complete order-level served/deferred decisions;
- order coverage is easier to explain as broad customer service.

Volume and weight still remain hard capacity constraints.

They can be reported as outcome metrics later.

They are not the Phase 21 primary objective.

---

# 14. Why the policy does not make Fresh an overriding first priority

The scenario says Fresh demand is rising.

It does **not** say:

```text
serve Fresh regardless of all other brands
```

Therefore WayLoom uses Fresh/chilled as a later business-context tiebreaker after:

```text
overall service coverage
backlog fairness
service recency
low-flexibility access
```

This avoids turning contextual information into a hidden absolute rule.

---

# 15. Why scarcity is not itself a hard priority

Phase 19 may show that an order has only one compatible vehicle.

That does not automatically mean:

```text
must serve
```

because:

- another order may have stronger fairness/business reasons;
- that one vehicle may need to serve several other constrained orders;
- trip capacity/time may make combinations infeasible.

Scarcity is therefore:

```text
priority/tiebreak context
```

not:

```text
official hard feasibility rule.
```

---

# 16. Outlet repetition and fairness

Officially:

```text
outlet_id may appear more than once
```

Allocation remains keyed by:

```text
order_ref
```

The default Phase 21 objective is therefore defined at **order level**.

However:

```text
deferred_yesterday
days_since_last_served
```

describe outlet service history.

This can cause an outlet with multiple orders to receive fairness credit more than once.

Phase 21 must acknowledge this explicitly.

## Default WayLoom decision

Keep the optimizer objective order-level because:

- official submission decisions are per `order_ref`;
- one Fresh outlet may legitimately have separate ambient and chilled orders;
- serving one order does not necessarily satisfy the other order's demand.

But final reporting should also include:

```text
unique outlets served
unique previously deferred outlets served
```

as fairness diagnostics.

Do not change the optimizer to outlet-level service unless deliberately approved later.

---

# 17. Individually impossible orders

From Phase 19:

```text
compatible_vehicle_count = 0
```

means the order is individually impossible under the available S1 fleet.

Policy handling:

```text
hard feasibility:
cannot serve

priority:
does not override impossibility

explanation:
deferred because no available compatible vehicle can legally carry the whole order
```

Do not assign an artificial low priority to impossible orders and pretend the solver chose not to serve them.

Their deferral reason is:

```text
hard infeasibility
```

not:

```text
policy preference.
```

---

# 18. Deferral explanation taxonomy

Phase 21 should define a stable explanation taxonomy for later use.

Recommended categories:

```text
HARD_NO_COMPATIBLE_VEHICLE

CAPACITY_COMPETITION

SCARCE_REEFER_CAPACITY

SCARCE_REEFER_VAN_CAPACITY

TRIP_SLOT_LIMIT

FRESH_TIME_BUDGET

STYLE_TECH_TIME_BUDGET

LOWER_POLICY_PRIORITY

ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN
```

Not all reasons can be assigned until after Phase 22 solves and Phase 23 validates.

Phase 21 defines the vocabulary and semantics only.

Do not guess final deferral reason before seeing the final allocation.

---

# 19. Required policy metrics

Implement pure metric helpers so Phase 22 can compare candidate allocations without duplicating definitions.

Recommended metrics:

```text
served_order_count

deferred_order_count

served_share

served_previous_deferred_count

served_previous_deferred_share

served_waiting_days_sum

served_waiting_days_mean

served_low_flexibility_count

served_fresh_chilled_count

served_fresh_count

unique_outlets_served

unique_previous_deferred_outlets_served
```

Assignment stewardship metrics:

```text
avoidable_reefer_van_assignment_count

avoidable_reefer_assignment_count

avoidable_van_assignment_count
```

These metric functions may accept **synthetic candidate allocations** in tests.

Do not run the optimizer.

---

# 20. Objective vector representation

Implement a transparent objective-vector representation.

Recommended:

```python
PolicyObjectiveVector(
    served_order_count,
    served_previous_deferred_count,
    served_waiting_days_sum,
    served_low_flexibility_count,
    served_fresh_chilled_count,
    served_fresh_count,
    negative_avoidable_reefer_van_assignments,
    negative_avoidable_reefer_assignments,
    negative_avoidable_van_assignments,
)
```

All entries can then be compared lexicographically in descending order if minimization terms are stored as negative counts.

Alternative:

store explicit:

```text
direction = maximize/minimize
```

per tier.

That is clearer.

Recommended config representation:

```yaml
objective:
  strategy: lexicographic

  levels:
    - id: maximize_served_orders
      direction: maximize

    - id: maximize_previous_deferred_served
      direction: maximize

    - id: maximize_waiting_days_served
      direction: maximize

    - id: maximize_low_flexibility_served
      direction: maximize

    - id: maximize_fresh_chilled_served
      direction: maximize

    - id: maximize_fresh_served
      direction: maximize

    - id: minimize_avoidable_reefer_van_use
      direction: minimize

    - id: minimize_avoidable_reefer_use
      direction: minimize

    - id: minimize_avoidable_van_use
      direction: minimize
```

Do not use one undocumented weighted sum.

---

# 21. Weighted-objective alternative — rejected by default

Document that Phase 21 considered:

```text
single weighted score
```

for example:

```text
served_count*w1
+ deferred_yesterday*w2
+ waiting_days*w3
+ Fresh urgency*w4
...
```

but did not choose it as the default because:

- arbitrary scaling can hide tradeoffs;
- high magnitudes can overpower intended priorities;
- changing weights after seeing results can become post-hoc tuning;
- judges may find lexicographic rules easier to audit.

Phase 22 DT-318 may tune implementation details **without changing the policy meaning**.

If a later technical reason requires a weighted encoding, it must be mathematically proven equivalent to the frozen lexicographic order.

---

# 22. Phase 22 tuning boundary

The master inventory later includes:

```text
DT-318
Tune prioritization objective
```

Phase 21 must constrain what "tuning" is allowed to mean.

Allowed later tuning:

- solver implementation mechanics;
- mathematically equivalent lexicographic weight scaling;
- search settings;
- deterministic tie-breaking;
- performance improvements that do not change policy tier ordering.

Not allowed without reopening Phase 21:

- moving Fresh above total service coverage;
- removing backlog fairness;
- changing low-flexibility threshold after inspecting which orders get served;
- adding new private-score-driven priority terms;
- changing hard rules into soft penalties;
- changing soft policy preferences into hard constraints.

---

# 23. Recommended configuration

Create:

```text
configs/task2b_priority.yaml
```

Suggested content:

```yaml
version: 1

policy:
  name: WayLoom_S1_Transparent_Lexicographic
  strategy: lexicographic

hard_rules:
  source: official_task2b
  count: 7
  priority_may_override: false

signals:
  deferred_yesterday:
    enabled: true
    source: task2b_peak_day_scenarios

  days_since_last_served:
    enabled: true
    source: task2b_peak_day_scenarios

  compatible_vehicle_count:
    enabled: true
    source: phase19

  fresh_chilled:
    enabled: true
    source:
      - brand
      - temp_requirement

  fresh:
    enabled: true
    source:
      - brand

low_flexibility:
  compatible_vehicle_count_max: 2
  impossible_count_value: 0
  impossible_is_priority_eligible: false

objective:
  levels:
    - id: served_order_count
      direction: maximize

    - id: previous_deferred_served
      direction: maximize

    - id: waiting_days_served
      direction: maximize

    - id: low_flexibility_served
      direction: maximize

    - id: fresh_chilled_served
      direction: maximize

    - id: fresh_served
      direction: maximize

    - id: avoidable_reefer_van_use
      direction: minimize

    - id: avoidable_reefer_use
      direction: minimize

    - id: avoidable_van_use
      direction: minimize

scope:
  use_delivery_windows_as_hard_rule: false
  use_fuel_quota_as_hard_rule: false
  use_task1_predictions: false
  use_task2a_forecasts_as_order_priority: false

determinism:
  use_order_ref_as_business_priority: false

reports:
  private_output_dir: reports/private/phase21_task2b_priority
```

---

# 24. DT-293 — Decide what good allocation means

## Objective

Write a measurable definition of a "good" Task 2B allocation.

## Frozen WayLoom definition

A good allocation:

1. satisfies **all official hard feasibility rules**;
2. serves as many individually feasible orders as possible;
3. among equally broad allocations, gives fair consideration to orders/outlets that were skipped yesterday;
4. favors longer-waiting demand when coverage is tied;
5. protects low-flexibility orders from being crowded out by flexible orders when possible;
6. uses S1 Fresh/chilled business context as a later tiebreaker;
7. conserves scarce specialized vehicles when doing so does not reduce higher-level policy outcomes;
8. provides explicit reasons for unavoidable or policy-driven deferrals.

## Required outputs

Tracked:

```text
docs/task2b_policy.md
```

with a plain-English "What good means" section.

Code:

```text
src/task2b/policy_metrics.py
```

with measurable policy metrics.

## Tests

Synthetic allocation comparison proving:

- infeasible allocation is never considered "good" regardless of policy score;
- higher served count beats lower served count;
- when served count ties, more previous-deferred orders served wins;
- later tiers only break earlier-tier ties.

## STOP

If the policy cannot be expressed as measurable metrics.

---

# 25. DT-294 — Design transparent prioritization policy

## Objective

Convert the "good allocation" definition into a reproducible policy that a dispatcher/judge can understand.

## Required policy language

Recommended plain-English version:

> WayLoom first requires every allocation to satisfy the official feasibility rules. Among feasible plans, it serves as many orders as possible. When multiple plans serve the same number of orders, it gives preference to orders that were deferred on the previous run, then to outlets that have waited longer since their last delivery. It next protects low-flexibility orders that have few compatible vehicles, gives a modest tiebreak preference to Fresh chilled and then Fresh demand because S1 occurs one week before a festival with rising Fresh demand, and finally avoids consuming reefer vans, reefers and vans unnecessarily when ordinary vehicles could serve the same order.

This paragraph is an engineering recommendation.

Do not label it as organizer wording.

## Required properties

Policy must be:

```text
transparent
deterministic
predeclared
feasibility-respecting
auditable
explainable
```

## Do not include

- hidden AI-generated score;
- model-based priority prediction;
- arbitrary importance inferred from private outcome;
- post-hoc rules selected after seeing final allocation.

## Tests

Policy config parses deterministically.

Every signal has documented:

```text
source
meaning
official/engineering status
objective tier
```

---

# 26. DT-295 — Distinguish hard rules from priority policy

## Objective

Prevent the most dangerous Task 2B design error:

```text
mixing feasibility constraints with preferences
```

## Required rule classification table

Create in:

```text
docs/task2b_priority_spec.md
```

Columns:

```text
rule_or_signal
classification
source
can_be_violated
phase_enforced
notes
```

Required examples:

| Rule/signal | Classification | Can policy override? |
|---|---|---|
| same brand+district per trip | HARD_OFFICIAL | No |
| chilled→reefer | HARD_OFFICIAL | No |
| van_only→van | HARD_OFFICIAL | No |
| home depot | HARD_OFFICIAL | No |
| whole order | HARD_OFFICIAL | No |
| weight+volume capacity | HARD_OFFICIAL | No |
| max 2 trips/time budgets | HARD_OFFICIAL | No |
| deferred_yesterday | SOFT_POLICY | Yes, may still be deferred |
| days_since_last_served | SOFT_POLICY | Yes |
| low compatible-vehicle count | SOFT_POLICY | Yes |
| Fresh chilled | SOFT_POLICY | Yes |
| Fresh | SOFT_POLICY | Yes |
| avoidable reefer use | SOFT_TIEBREAKER | Yes |

## Code requirement

Implement enums/constants such as:

```text
HARD_OFFICIAL
SOFT_POLICY
SOFT_TIEBREAKER
DIAGNOSTIC_ONLY
```

Do not make a hard official rule configurable to "off" in the priority file.

Hard rule toggles belong nowhere in the policy.

## Tests

- hard rules cannot be overridden by objective;
- `deferred_yesterday` is not treated as hard;
- Fresh priority is not treated as hard;
- scarcity is not treated as hard.

---

# 27. DT-296 — Decide lexicographic or weighted objective

## Decision

Choose:

```text
LEXICOGRAPHIC
```

## Objective order

Freeze:

```text
1. maximize served order count

2. maximize served previous-deferred count

3. maximize sum of days_since_last_served among served orders

4. maximize served low-flexibility orders

5. maximize served Fresh chilled orders

6. maximize served Fresh orders

7. minimize avoidable reefer-van assignments

8. minimize avoidable reefer assignments

9. minimize avoidable van assignments
```

## Important

Hard feasibility sits **outside** this list.

A lexicographically superior but infeasible allocation is invalid.

## Phase 22 encoding requirement

Phase 22 must preserve exact tier ordering.

Preferred:

```text
sequential solve/fix optimum per level
```

Acceptable:

```text
mathematically proven equivalent integer weighting
```

Not acceptable:

```text
arbitrary big weights with no dominance proof
```

## Unit tests

Implement objective-vector comparison tests.

Examples:

### Example A

Allocation A:

```text
served = 10
deferred-yesterday served = 2
```

Allocation B:

```text
served = 9
deferred-yesterday served = 5
```

Winner:

```text
A
```

because Level 1 dominates.

### Example B

Both served = 10.

A serves 3 previous-deferred.

B serves 2.

Winner:

```text
A
```

### Example C

Levels 1–2 tied.

Higher total waiting-days served wins.

### Example D

All policy tiers tied except avoidable reefer use.

Lower avoidable reefer use wins.

---

# 28. DT-297 — Document fairness rationale

## Objective

Explain why the policy is fair without claiming perfect fairness.

## Required rationale

### Broad coverage

Serving as many feasible orders as possible prevents the allocation from concentrating the day on a few large/high-priority orders.

### Previous deferrals

An outlet/order skipped on the previous run receives preference when service coverage is otherwise equal.

This reduces repeated deferral.

### Waiting time

`days_since_last_served` helps prevent outlets with long service gaps from being continually postponed.

### Low flexibility

Orders that can use only one or two available vehicles have less recovery flexibility.

Using this as a later tiebreak helps avoid systematically disadvantaging constrained outlets.

### No impossible promise

An individually impossible order cannot be made feasible by fairness preference.

Its deferral should be explained as a physical/resource limitation.

### Multi-order outlets

Fairness is optimized per `order_ref`, while unique-outlet fairness metrics are also reported to avoid hiding repeated-outlet effects.

## Required diagnostics for later phases

Recommend reporting:

```text
served share

previous-deferred served share

mean/median days-since among served vs deferred

unique outlets served

unique previous-deferred outlets served

low-flexibility served share
```

No private values need to be embedded in the tracked rationale.

---

# 29. DT-298 — Document business rationale

## Objective

Explain how the policy responds to the S1 business context.

## Required business rationale

### Rising Fresh demand

S1 occurs one week before a festival and explicitly states that Fresh demand is rising.

Therefore Fresh receives a later tiebreak preference.

### Chilled Fresh

The scenario specifically mentions dairy, meat and produce.

Chilled Fresh orders also depend on scarce refrigerated capacity.

Therefore:

```text
Fresh chilled
```

receives a tiebreak before general Fresh.

### Scarce specialized resources

Reefer vans satisfy both:

```text
chilled
+
van_only
```

and are especially constrained.

The policy avoids consuming specialized resources unnecessarily when an ordinary compatible vehicle can serve the same order with no loss on higher policy tiers.

### Style and Tech remain legitimate demand

The policy must explicitly state:

```text
Style and Tech are not excluded.
```

They may be served whenever feasible and can beat Fresh orders at higher policy levels such as:

```text
overall service coverage
previous deferral
longer service gap
low flexibility
```

### No payday / no monsoon

The S1 context says:

```text
not payday
no monsoon
```

WayLoom does not invent extra penalties or bonuses for those conditions.

They are context facts, not objective terms.

---

# 30. Policy metadata builder

Implement a pure metadata function.

Recommended:

```python
build_order_priority_metadata(
    orders_s1,
    order_compatibility_summary,
    compatibility_matrix,
) -> pd.DataFrame
```

Required output per `order_ref`:

```text
order_ref

deferred_yesterday

days_since_last_served

is_fresh

is_fresh_chilled

compatible_vehicle_count

is_individually_impossible

is_singleton

is_low_flexibility

has_non_reefer_alternative

has_non_van_alternative

has_non_reefer_van_alternative
```

Optional:

```text
outlet_id
```

for local fairness diagnostics.

Do not include solver decision columns.

---

# 31. Specialized-resource alternative definitions

Use compatibility data, not guesswork.

## has_non_reefer_alternative

True if an order has at least one compatible vehicle with:

```text
vehicle.temp != reefer
```

Relevant mainly for ambient orders.

## has_non_van_alternative

True if at least one compatible vehicle has:

```text
vehicle.type != van
```

Relevant only when the order is not `van_only`.

## has_non_reefer_van_alternative

For an order compatible with a reefer van, true if it has at least one compatible vehicle that is **not simultaneously**:

```text
type = van
AND temp = reefer
```

Phase 22 can use these flags to count avoidable specialized assignments.

---

# 32. Priority data validation

Before producing metadata:

```text
order_ref unique

deferred_yesterday in {0,1}

days_since_last_served integer-like >= 0

compatible_vehicle_count integer >= 0

individually_impossible
==
compatible_vehicle_count == 0
```

Required consistency:

```text
is_singleton
==
compatible_vehicle_count == 1
```

```text
is_low_flexibility
==
0 < compatible_vehicle_count <= threshold
```

Impossible orders are:

```text
not policy-eligible for served preference
```

because hard feasibility cannot serve them.

---

# 33. Required synthetic tests

Create:

```text
tests/test_task2b_priority.py
tests/test_task2b_policy_metrics.py
```

Use synthetic fixtures only.

## Signal construction

- deferred flag 0/1;
- days-since validation;
- Fresh indicator;
- Fresh chilled indicator;
- compatible count;
- impossible;
- singleton;
- low flexibility;
- non-reefer alternative;
- non-van alternative;
- non-reefer-van alternative.

## Hard vs soft classification

- seven official hard-rule classes;
- deferred signal soft;
- waiting-days soft;
- Fresh soft;
- scarcity soft;
- resource stewardship soft tiebreak.

## Objective order

- served count dominates backlog;
- backlog dominates waiting-days;
- waiting-days dominates low-flexibility;
- low-flexibility dominates Fresh chilled;
- Fresh chilled dominates Fresh;
- higher-level tie must exist before lower-level matters.

## Specialized-resource minimization

- only applies after higher levels tie;
- reefer van conservation before reefer conservation;
- reefer conservation before general van conservation.

## Impossible order

- cannot become served just because its policy attributes are high;
- policy metrics classify deferral as hard infeasibility context.

## Repeated outlet

- distinct order_refs remain distinct;
- unique-outlet diagnostic does not double-count outlet;
- order-level metric may count both orders explicitly.

## Business context

- Style/Tech are not assigned zero priority;
- Fresh preference is only later tier;
- no payday/monsoon bonus;
- no delivery-window hard rule;
- no Task 1 prediction signal;
- no Task 2A forecast signal used as direct order priority.

## Determinism

- config order stable;
- metric calculations deterministic;
- objective vector deterministic;
- no randomness.

---

# 34. Policy review examples

Use synthetic examples in tests/docs.

## Example 1 — coverage beats backlog

Plan A:

```text
10 orders served
1 was deferred yesterday
```

Plan B:

```text
9 orders served
4 were deferred yesterday
```

Policy winner:

```text
Plan A
```

because broad coverage is Level 1.

---

## Example 2 — backlog breaks equal-coverage tie

Both serve:

```text
10 orders
```

Plan A serves:

```text
3 previous-deferred orders
```

Plan B serves:

```text
2
```

Winner:

```text
Plan A
```

---

## Example 3 — waiting time breaks later tie

Both plans:

```text
served count = 10
previous-deferred served = 3
```

Plan A serves total:

```text
42 waiting-days
```

Plan B:

```text
35
```

Winner:

```text
Plan A
```

---

## Example 4 — business context is not absolute

Plan A serves one additional non-Fresh order.

Plan B serves fewer total orders but more Fresh.

Winner:

```text
Plan A
```

because total coverage is higher.

This proves Fresh is not a hidden hard priority.

---

## Example 5 — resource conservation

All higher policy metrics are identical.

Plan A uses a reefer van for an ambient, non-van-only order even though a dry truck is compatible.

Plan B uses the dry truck.

Winner:

```text
Plan B
```

because specialized capacity is conserved.

---

# 35. Deferral explanation principles

Later, every deferred order should be explainable using:

1. hard infeasibility;
2. shared capacity/time competition;
3. policy tradeoff.

Avoid vague wording such as:

```text
solver decided
AI decided
low score
```

Prefer:

```text
Deferred because no available compatible vehicle could carry the complete chilled van-only order.

Deferred because available compatible trip capacity was consumed by a plan that served more orders and more previously deferred demand under the frozen policy.

Deferred after higher-priority fairness tiers were satisfied; the order remained feasible but lower in the lexicographic policy.
```

Phase 21 defines explanation style.

Phase 24 will produce the final short policy.

---

# 36. Private policy-context report

The local script may summarize actual signal distribution privately.

Recommended:

```text
policy_context_summary.json
```

with aggregate counts only.

Possible aggregates:

```text
order count

individually impossible count

previously deferred count

low-flexibility count

singleton count

Fresh count

Fresh chilled count

orders with avoidable specialized alternatives
```

Do not print row-level IDs.

This report helps the human confirm the policy is relevant to S1.

It must not change the policy after looking at counts.

---

# 37. No post-hoc policy fitting

This is critical.

Do not run multiple policy orders on the real scenario and choose whichever gives the nicest served/deferred story.

Phase 21 freezes the policy **before Phase 22 final allocation**.

Phase 22 may debug solver correctness.

It must not "optimize the policy narrative" after seeing who gets deferred.

Any material change to the policy ordering requires:

```text
reopen Phase 21
document reason
rerun Phase 22/23
```

---

# 38. Phase 21 STOP conditions

`READY FOR PHASE 22` remains **NO** if:

- Phases 18–20 are not passing;
- official hard rules are mixed with soft priority signals;
- any priority rule is presented as organizer-mandated when it is not;
- `deferred_yesterday` is made a hard must-serve rule;
- `days_since_last_served` is made a hard must-serve threshold without official support;
- Fresh is made an absolute hard priority;
- Style or Tech are effectively excluded;
- impossible orders are allowed to override feasibility;
- delivery windows/fuel/Hackathon constraints are imported as Task 2B hard rules without official support;
- objective strategy is not explicit;
- weighted vs lexicographic decision is unresolved;
- lexicographic tier order is not frozen;
- arbitrary weighted "big-M objective" is used without proof of equivalence;
- scarcity is turned into a hard compatibility rule;
- resource stewardship can sacrifice a higher-level policy goal;
- policy uses Task 1 predictions;
- policy uses Task 2A forecast outputs as direct per-order priority;
- policy is changed after inspecting the final allocation;
- solver/allocation is implemented prematurely;
- Task 1 artifacts change;
- Task 2A artifacts change;
- private scenario rows must be exposed to an external AI agent;
- synthetic tests fail;
- local priority-context validation fails;
- independent review fails.

---

# 39. Definition of Done

Phase 21 passes only when:

- [ ] DT-293 PASS
- [ ] DT-294 PASS
- [ ] DT-295 PASS
- [ ] DT-296 PASS
- [ ] DT-297 PASS
- [ ] DT-298 PASS
- [ ] official seven hard rules documented separately
- [ ] hard rules cannot be overridden by policy
- [ ] definition of "good allocation" is measurable
- [ ] policy is plain-English explainable
- [ ] policy signals have explicit source lineage
- [ ] `deferred_yesterday` policy meaning documented
- [ ] `days_since_last_served` policy meaning documented
- [ ] repeated-outlet fairness issue documented
- [ ] low-flexibility signal grounded in Phase 19
- [ ] Fresh/chilled business context grounded in S1
- [ ] Style and Tech remain eligible
- [ ] no payday/monsoon invented priority term
- [ ] lexicographic strategy frozen
- [ ] Level 1 served-order coverage frozen
- [ ] Level 2 previous-deferral fairness frozen
- [ ] Level 3 waiting-days fairness frozen
- [ ] Level 4 low-flexibility coverage frozen
- [ ] Level 5 Fresh chilled tiebreak frozen
- [ ] Level 6 Fresh tiebreak frozen
- [ ] specialized-resource stewardship frozen as lower tiebreak
- [ ] weighted-objective alternative explicitly rejected by default
- [ ] policy metrics implemented
- [ ] policy metadata builder implemented
- [ ] deferral explanation taxonomy defined
- [ ] fairness rationale documented
- [ ] business rationale documented
- [ ] no optimizer/allocation generated
- [ ] synthetic tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs remain ignored
- [ ] Task 1 remains frozen
- [ ] Task 2A remains frozen
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 21 STATUS: PASS
READY FOR PHASE 22: YES
```

---

# 40. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-21-task2b-priority-policy
```

Recommended commits:

```text
feat(task2b): add priority metadata and policy metrics
docs(task2b): define transparent lexicographic allocation policy
test(task2b): add priority objective contract tests
docs(task2b): document fairness and business rationale
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q \
  tests/test_task2b_priority.py \
  tests/test_task2b_policy_metrics.py

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
LOCAL PHASE 21 POLICY CONTEXT: PASS
INDEPENDENT PHASE 21 REVIEW: PASS
```

---

# 41. Recommended Codex model

Phase 21 is primarily:

```text
reasoning
policy design
documentation
deterministic metric code
```

It does not need an optimizer yet.

Recommended low-token choice:

```text
GPT-5.6 Luna
Reasoning: Medium
```

If Luna is unavailable:

```text
GPT-5.6 Terra
Reasoning: Medium
```

Escalate only if the repository integration becomes difficult:

```text
GPT-5.6 Sol
Reasoning: Medium
```

Use the stronger model for Phase 22 instead.

---

# 42. Local private-data command

Codex should implement but not execute against private scenario rows:

```bash
python scripts/build_task2b_priority_context.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --priority-config configs/task2b_priority.yaml \
  --compatibility-summary data/interim/task2b_order_compatibility_summary.csv \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --metadata-output data/interim/task2b_priority_metadata.csv \
  --report-dir reports/private/phase21_task2b_priority
```

PowerShell one-line:

```powershell
python scripts/build_task2b_priority_context.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --scenario-config configs/task2b_scenario.yaml --compatibility-config configs/task2b_compatibility.yaml --priority-config configs/task2b_priority.yaml --compatibility-summary data/interim/task2b_order_compatibility_summary.csv --compatibility-matrix data/interim/task2b_compatibility_matrix.csv --metadata-output data/interim/task2b_priority_metadata.csv --report-dir reports/private/phase21_task2b_priority
```

Recommended sanitized output:

```text
LOCAL PHASE 21 POLICY CONTEXT: PASS
HARD/SOFT RULE SEPARATION: PASS
PRIORITY METADATA COVERAGE: PASS
IMPOSSIBLE ORDER POLICY GUARD: PASS
LEXICOGRAPHIC OBJECTIVE SPEC: PASS
FAIRNESS RATIONALE: PASS
BUSINESS RATIONALE: PASS
SPECIALIZED-RESOURCE TIEBREAK: PASS
```

Do not print actual order priority rows.

---

# 43. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 21 only.

PHASE:
Task 2B Priority-Policy Design

TASK RANGE:
DT-293 through DT-298

EXECUTION MODE:
Policy-design and deterministic-support-code phase with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Luna — Medium reasoning

FALLBACK:
GPT-5.6 Terra — Medium reasoning

ESCALATE ONLY IF NECESSARY:
GPT-5.6 Sol — Medium reasoning

You MAY:

- create/edit/refactor tracked Phase 21 code
- create/update configs
- create/update documentation
- create synthetic fixtures
- run targeted tests
- run the full safe regression suite
- inspect tracebacks
- fix ordinary implementation bugs
- rerun tests
- run python -m pip check
- inspect git status/diff
- run git diff --check
- self-review against Phase 21 DoD

Do NOT stop for routine coding/test failures that can safely be fixed.

STOP only for:

- official-rule ambiguity
- requirement to expose private competition rows
- Phase 18/19/20 contract failure
- conflict between official hard rules and policy design
- need to invent an unsupported hard constraint
- unresolved objective-policy decision
- pressure to inspect final solver output before freezing policy

DO NOT START PHASE 22.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 21 and Task 2B rules
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. PHASE_20_COMPETITION_CONTRACT.md
7. PHASE_21_COMPETITION_CONTRACT.md
8. src/task2b/scenario.py
9. src/task2b/compatibility.py
10. src/task2b/scarcity.py
11. src/task2b/trip_time.py
12. configs/task2b_scenario.yaml
13. configs/task2b_compatibility.yaml
14. configs/task2b_trip_time.yaml
15. docs/task2b_scenario_spec.md
16. docs/task2b_compatibility_spec.md
17. docs/task2b_trip_time_spec.md
18. existing Task 2B tests

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

Do NOT inspect or print real scenario rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for all agent-run policy tests.

The human will run the real policy-context command locally.

Do NOT print actual:

order_ref
priority metadata rows
compatibility pair rows
private scenario counts

==================================================
OFFICIAL VS ENGINEERING BOUNDARY
==================================================

OFFICIAL HARD RULES:

1. same brand + district per trip
2. chilled requires reefer
3. van_only requires van
4. vehicle home depot must match
5. whole order / no split
6. both weight and volume capacity
7. max 2 trips + official Fresh/Style-Tech time budgets

Policy MUST NEVER override these.

OFFICIAL SCENARIO CONTEXT:

S1 = Peliyagoda

festival one week away

Fresh demand rising,
including dairy, meat and produce

not payday

no monsoon

vehicles in workshop

OFFICIAL POLICY-RELEVANT FIELDS:

deferred_yesterday

days_since_last_served

The exact priority objective is a WayLoom engineering choice.

Never describe it as organizer-mandated.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/priority.py

src/task2b/policy_metrics.py

scripts/build_task2b_priority_context.py

configs/task2b_priority.yaml

docs/task2b_policy.md

docs/task2b_priority_spec.md

tests/test_task2b_priority.py

tests/test_task2b_policy_metrics.py

Do NOT implement/run the Phase 22 optimizer.

Do NOT create a final served/deferred allocation.

==================================================
DT-293 — DECIDE WHAT GOOD ALLOCATION MEANS
==================================================

Freeze this definition:

A good allocation:

1. satisfies every official hard rule

2. serves as many individually feasible orders as possible

3. among equal-coverage plans, serves more orders that were deferred yesterday

4. then favors demand with longer days_since_last_served

5. then protects low-flexibility orders with few compatible vehicles

6. then gives a modest S1 business tiebreak to Fresh chilled

7. then to Fresh overall

8. then conserves specialized reefer-van / reefer / van capacity when ordinary alternatives exist

9. can explain every deferral as:
   hard infeasibility,
   shared resource competition,
   or policy tradeoff

Implement measurable policy metrics.

Do not use final solver output to define "good."

==================================================
DT-294 — TRANSPARENT PRIORITIZATION POLICY
==================================================

Create docs/task2b_policy.md.

Plain-English recommended policy:

WayLoom first requires every allocation to satisfy the official
feasibility rules. Among feasible plans, it serves as many orders as
possible. When plans serve the same number of orders, it favors orders
deferred on the previous run, then outlets/orders that have waited longer
since their last delivery. It next protects orders with few compatible
vehicles, gives a later tiebreak preference to Fresh chilled and Fresh
demand because S1 is one week before a festival with rising Fresh demand,
and finally avoids consuming specialized reefer vans, reefers and vans
unnecessarily when ordinary compatible vehicles can serve the same order.

Clearly mark:

THIS IS WAYLOOM POLICY,
NOT AN OFFICIAL ORGANIZER PRIORITY ORDER.

Policy must be:

transparent
deterministic
predeclared
auditable
feasibility-respecting

No hidden AI score.

No ML priority model.

==================================================
DT-295 — HARD VS SOFT SEPARATION
==================================================

Create an explicit classification table.

Classes:

HARD_OFFICIAL

SOFT_POLICY

SOFT_TIEBREAKER

DIAGNOSTIC_ONLY

Classify:

same brand+district = HARD_OFFICIAL

chilled->reefer = HARD_OFFICIAL

van_only->van = HARD_OFFICIAL

home depot = HARD_OFFICIAL

whole order = HARD_OFFICIAL

weight+volume = HARD_OFFICIAL

max trips/time budgets = HARD_OFFICIAL

deferred_yesterday = SOFT_POLICY

days_since_last_served = SOFT_POLICY

low compatible count = SOFT_POLICY

Fresh chilled = SOFT_POLICY

Fresh = SOFT_POLICY

avoidable specialized vehicle use = SOFT_TIEBREAKER

Hard rules cannot be switched off by priority config.

Hard rules cannot be violated for a high-priority order.

Do not import delivery windows/fuel as extra Task 2B hard rules.

==================================================
DT-296 — CHOOSE OBJECTIVE STRATEGY
==================================================

Choose:

LEXICOGRAPHIC

Do NOT use one arbitrary weighted sum.

Freeze exact tier order:

LEVEL 1:
maximize served_order_count

LEVEL 2:
maximize served_previous_deferred_count

LEVEL 3:
maximize served_waiting_days_sum

LEVEL 4:
maximize served_low_flexibility_count

LEVEL 5:
maximize served_fresh_chilled_count

LEVEL 6:
maximize served_fresh_count

LEVEL 7A:
minimize avoidable_reefer_van_assignment_count

LEVEL 7B:
minimize avoidable_reefer_assignment_count

LEVEL 7C:
minimize avoidable_van_assignment_count

Hard feasibility exists outside these tiers.

Preferred Phase 22 implementation:

sequential lexicographic optimization.

Acceptable alternative:

mathematically proven equivalent integer weighting.

Unacceptable:

arbitrary big weights without dominance proof.

==================================================
LEVEL 1 RATIONALE
==================================================

Coverage is first.

Reason:

A previously deferred but very large order should not automatically
force the system to defer many otherwise feasible orders simply because
backlog fairness was placed above coverage.

WayLoom first maximizes order coverage.

Fairness then breaks equal-coverage ties.

Document this engineering choice.

==================================================
LOW FLEXIBILITY
==================================================

Default:

low_flexibility =
0 < compatible_vehicle_count <= 2

Threshold:
2

This is an engineering policy threshold.

individually impossible:

compatible_vehicle_count == 0

is NOT priority-eligible because feasibility cannot serve it.

Do not modify the threshold after observing the final allocation.

==================================================
FRESH BUSINESS TIEBREAK
==================================================

Fresh chilled is above general Fresh only as a later tiebreak.

Reason:

S1 explicitly says Fresh demand is rising and mentions dairy, meat and
produce one week before a festival.

Do NOT make Fresh absolute.

Style and Tech remain legitimate demand and can beat Fresh at higher
levels:

served coverage
previous deferral
waiting time
low flexibility

==================================================
SPECIALIZED-VEHICLE STEWARDSHIP
==================================================

After all order-selection policy tiers tie:

prefer fewer avoidable uses of:

1. reefer vans
2. reefers
3. vans

"avoidable" means the assigned order had another compatible alternative
that did not consume that specialized capability.

Derive alternatives from Phase 19 compatibility.

Do not classify necessary specialized assignments as waste.

==================================================
DT-297 — FAIRNESS RATIONALE
==================================================

Document:

BROAD COVERAGE:
serve as many feasible orders as possible.

PREVIOUS DEFERRAL:
reduce repeated skipping.

WAITING TIME:
favor longer service gaps after higher-level ties.

LOW FLEXIBILITY:
avoid systematically disadvantaging outlets with few legal vehicle options.

IMPOSSIBLE ORDERS:
priority cannot override physical infeasibility.

REPEATED OUTLETS:
allocation key remains order_ref.
Fairness objective is order-level.
Also report unique-outlet fairness metrics to expose repeated-outlet effects.

Recommended later fairness diagnostics:

served_share

previous-deferred served share

served/deferred waiting-days distribution

unique outlets served

unique previous-deferred outlets served

low-flexibility served share

Do not claim this is mathematically perfect fairness.

==================================================
DT-298 — BUSINESS RATIONALE
==================================================

Document:

S1 is one week before a festival.

Fresh demand is rising.

Fresh chilled depends on scarce reefers.

Reefer vans are especially flexible/scarce because they can satisfy both:

chilled
+
van_only

Therefore business tie-breakers:

Fresh chilled
then Fresh overall

and specialized-resource conservation.

Style and Tech are NOT excluded.

No payday bonus because S1 is explicitly not payday.

No monsoon penalty because S1 explicitly says no monsoon.

Do not invent unsupported business terms.

==================================================
POLICY METADATA BUILDER
==================================================

Implement:

build_order_priority_metadata(...)

Output one row per order_ref with:

order_ref

deferred_yesterday

days_since_last_served

is_fresh

is_fresh_chilled

compatible_vehicle_count

is_individually_impossible

is_singleton

is_low_flexibility

has_non_reefer_alternative

has_non_van_alternative

has_non_reefer_van_alternative

No served/deferred decision column.

No solver output.

==================================================
ALTERNATIVE FLAGS
==================================================

Use Phase 19 compatibility matrix.

has_non_reefer_alternative:

at least one compatible vehicle that is not reefer.

has_non_van_alternative:

at least one compatible vehicle that is not van.

has_non_reefer_van_alternative:

at least one compatible vehicle not simultaneously:
type=van and temp=reefer.

These flags support later "avoidable specialized use" metrics.

==================================================
OBJECTIVE VECTOR / POLICY METRICS
==================================================

Implement pure helpers for synthetic/candidate allocations.

Metrics:

served_order_count

deferred_order_count

served_share

served_previous_deferred_count

served_previous_deferred_share

served_waiting_days_sum

served_waiting_days_mean

served_low_flexibility_count

served_fresh_chilled_count

served_fresh_count

unique_outlets_served

unique_previous_deferred_outlets_served

avoidable_reefer_van_assignment_count

avoidable_reefer_assignment_count

avoidable_van_assignment_count

Do not run the real optimizer.

==================================================
DEFERRAL-REASON TAXONOMY
==================================================

Define stable future categories:

HARD_NO_COMPATIBLE_VEHICLE

CAPACITY_COMPETITION

SCARCE_REEFER_CAPACITY

SCARCE_REEFER_VAN_CAPACITY

TRIP_SLOT_LIMIT

FRESH_TIME_BUDGET

STYLE_TECH_TIME_BUDGET

LOWER_POLICY_PRIORITY

ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN

Do not assign final reasons yet.

Phase 22/23 results determine the actual cause.

==================================================
POLICY CONFIG
==================================================

Create:

configs/task2b_priority.yaml

Include:

strategy = lexicographic

low_flexibility threshold = 2

exact objective tier order

signal sources

hard-policy override = false

delivery-window hard-rule use = false

fuel-rule use = false

Task 1 predictions use = false

Task 2A forecasts as direct per-order priority = false

private report path

Do not make hard official feasibility configurable from this file.

==================================================
TESTS
==================================================

Use synthetic fixtures only.

SIGNALS:

deferred 0/1

days-since valid

Fresh indicator

Fresh chilled indicator

compatible count

impossible

singleton

low-flexibility

alternative flags

HARD/SOFT:

all seven hard official rules classified hard

deferred soft

waiting soft

Fresh soft

scarcity soft

specialized stewardship tiebreak

OBJECTIVE:

served count dominates backlog

backlog dominates waiting

waiting dominates low flexibility

low flexibility dominates Fresh chilled

Fresh chilled dominates Fresh

Fresh dominates resource stewardship

RESOURCE:

avoidable reefer-van minimized only after higher tie

avoidable reefer minimized after reefer-van

avoidable van minimized after reefer

IMPOSSIBLE:

high fairness/business signal cannot override zero compatible vehicles

REPEATED OUTLET:

two order_refs remain distinct

unique-outlet diagnostic counts outlet once

order-level metrics may count two orders

BUSINESS:

Style and Tech remain eligible

Fresh preference is not absolute

no payday term

no monsoon term

no delivery-window hard rule

no Task1 prediction input

no Task2A forecast-as-order-priority input

DETERMINISM:

same input = same metadata

same candidate allocation = same objective vector

config tier order stable

no randomness

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After policy metadata:
run signal tests.

After hard/soft classification:
run classification tests.

After objective specification:
run lexicographic comparison tests.

After fairness/business docs:
run policy-schema/doc-contract tests.

Fix ordinary implementation bugs automatically.

Then run:

pytest -q \
  tests/test_task2b_priority.py \
  tests/test_task2b_policy_metrics.py

Also run relevant upstream Task 2B tests:

pytest -q \
  tests/test_task2b_scenario.py \
  tests/test_task2b_scenario_summary.py \
  tests/test_task2b_compatibility.py \
  tests/test_task2b_scarcity.py \
  tests/test_task2b_trip_groups.py \
  tests/test_task2b_trip_time.py

Then:

pytest -q

python -m pip check

git status

git diff

git diff --check

If private real data is needed:

do not inspect it in Codex.

Return the exact local human command.

Verify no private paths are staged.

==================================================
LOCAL HUMAN COMMAND
==================================================

Implement but do NOT execute private scenario data inside Codex:

python scripts/build_task2b_priority_context.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --priority-config configs/task2b_priority.yaml \
  --compatibility-summary data/interim/task2b_order_compatibility_summary.csv \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --metadata-output data/interim/task2b_priority_metadata.csv \
  --report-dir reports/private/phase21_task2b_priority

Console output must remain sanitized.

Do not print order-level priority rows.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phases 18–20 are not passing

hard feasibility mixed with policy preference

deferred_yesterday becomes hard must-serve

days-since becomes unsupported hard threshold

Fresh becomes absolute hard priority

Style/Tech are excluded

impossible order can override feasibility

delivery windows/fuel imported as hard Task2B rules

objective strategy unresolved

objective tier order not frozen

arbitrary weighted score introduced

scarcity becomes hard compatibility rule

resource stewardship can sacrifice higher policy tiers

Task1 predictions used

Task2A forecast used as direct order priority

policy changed after final allocation inspection

optimizer/allocation logic added

Task1 artifacts change

Task2A artifacts change

private rows must be exposed

tests cannot pass under contract

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-293 READY
DT-294 READY
DT-295 READY
DT-296 READY
DT-297 READY
DT-298 READY

good-allocation definition measurable

policy transparent

hard/soft separation exact

lexicographic strategy frozen

served count Level 1

previous deferral Level 2

waiting-days Level 3

low-flexibility Level 4

Fresh chilled Level 5

Fresh Level 6

specialized-resource stewardship last

impossible orders cannot override feasibility

Style/Tech remain eligible

fairness rationale complete

business rationale complete

deferral taxonomy defined

priority metadata builder complete

policy metric helpers complete

no optimizer

no final allocation

safe tests pass

pip check passes

private outputs ignored

Task1 unchanged

Task2A unchanged

no Phase22 production implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
21 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-293 READY / FAIL
DT-294 READY / FAIL
DT-295 READY / FAIL
DT-296 READY / FAIL
DT-297 READY / FAIL
DT-298 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

GOOD-ALLOCATION DEFINITION:
PASS / FAIL

TRANSPARENT POLICY:
PASS / FAIL

HARD/SOFT RULE SEPARATION:
PASS / FAIL

LEXICOGRAPHIC OBJECTIVE:
PASS / FAIL

OBJECTIVE TIER ORDER:
PASS / FAIL

FAIRNESS RATIONALE:
PASS / FAIL

BUSINESS RATIONALE:
PASS / FAIL

IMPOSSIBLE-ORDER POLICY GUARD:
PASS / FAIL

SPECIALIZED-RESOURCE TIEBREAK:
PASS / FAIL

DEFERRAL REASON TAXONOMY:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 21 policy-context command.

PHASE 21 STATUS:
AWAITING LOCAL POLICY CONTEXT VALIDATION

READY FOR PHASE 22:
NO

Then STOP.

Do not start Phase 22.
```

---

# 44. Independent Phase 21 review prompt

Use a fresh Codex/Cursor session after the human local policy-context run passes.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 21.

Do NOT implement Phase 22.
Do NOT run the optimizer.
Do NOT inspect private row-level scenario data.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 21
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. PHASE_20_COMPETITION_CONTRACT.md
7. PHASE_21_COMPETITION_CONTRACT.md
8. src/task2b/priority.py
9. src/task2b/policy_metrics.py
10. scripts/build_task2b_priority_context.py
11. configs/task2b_priority.yaml
12. docs/task2b_policy.md
13. docs/task2b_priority_spec.md
14. tests/test_task2b_priority.py
15. tests/test_task2b_policy_metrics.py
16. .gitignore
17. .cursorignore if present

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 21 POLICY CONTEXT: <PASS/FAIL>
HARD/SOFT RULE SEPARATION: <PASS/FAIL>
PRIORITY METADATA COVERAGE: <PASS/FAIL>
IMPOSSIBLE ORDER POLICY GUARD: <PASS/FAIL>
LEXICOGRAPHIC OBJECTIVE SPEC: <PASS/FAIL>
FAIRNESS RATIONALE: <PASS/FAIL>
BUSINESS RATIONALE: <PASS/FAIL>
SPECIALIZED-RESOURCE TIEBREAK: <PASS/FAIL>

Do not ask for private order-level priority rows.

AUDIT TASKS:

DT-293:
"good allocation" is measurable and feasibility-first.

DT-294:
plain-English prioritization policy is transparent and predeclared.

DT-295:
all seven official feasibility rules are separated from soft policy.

DT-296:
lexicographic objective chosen explicitly and exact tier order frozen.

DT-297:
fairness rationale covers broad coverage, previous deferral,
waiting time, low flexibility, impossible orders and repeated outlets.

DT-298:
business rationale accurately uses S1 Fresh/festival context without
excluding Style/Tech or inventing payday/monsoon effects.

AUDIT OBJECTIVE ORDER EXACTLY:

1 served_order_count — maximize

2 served_previous_deferred_count — maximize

3 served_waiting_days_sum — maximize

4 served_low_flexibility_count — maximize

5 served_fresh_chilled_count — maximize

6 served_fresh_count — maximize

7A avoidable_reefer_van_assignment_count — minimize

7B avoidable_reefer_assignment_count — minimize

7C avoidable_van_assignment_count — minimize

Verify:

hard feasibility is outside objective

no arbitrary weighted sum

no priority can serve impossible order

Fresh is not absolute

Style/Tech remain eligible

no delivery-window/fuel hard rules imported

no Task1/Task2A outputs used as direct per-order priority

no solver/allocation added

RUN SAFE TESTS:

pytest -q tests/test_task2b_priority.py tests/test_task2b_policy_metrics.py

pytest -q tests/test_task2b_scenario.py tests/test_task2b_scenario_summary.py tests/test_task2b_compatibility.py tests/test_task2b_scarcity.py tests/test_task2b_trip_groups.py tests/test_task2b_trip_time.py

pytest -q

python -m pip check

git status

git diff --check

Do not run the real policy-context script.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

GOOD-ALLOCATION DEFINITION:
PASS / FAIL

POLICY TRANSPARENCY:
PASS / FAIL

HARD/SOFT SEPARATION:
PASS / FAIL

LEXICOGRAPHIC STRATEGY:
PASS / FAIL

OBJECTIVE ORDER:
PASS / FAIL

FAIRNESS RATIONALE:
PASS / FAIL

BUSINESS RATIONALE:
PASS / FAIL

IMPOSSIBLE ORDER GUARD:
PASS / FAIL

SPECIALIZED RESOURCE STEWARDSHIP:
PASS / FAIL

NO UNOFFICIAL HARD RULES:
PASS / FAIL

NO OPTIMIZER/FINAL ALLOCATION:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN LOCAL CONTEXT RUN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-293: PASS/FAIL
DT-294: PASS/FAIL
DT-295: PASS/FAIL
DT-296: PASS/FAIL
DT-297: PASS/FAIL
DT-298: PASS/FAIL

PHASE 21 REVIEW:
PASS / FAIL

READY FOR PHASE 22:
YES / NO

If FAIL:
list exact blockers only.

Do not automatically fix.
Do not start Phase 22.
```

---

# 45. Completion record

```markdown
# Phase 21 Completion Record

## Tasks

- [ ] DT-293
- [ ] DT-294
- [ ] DT-295
- [ ] DT-296
- [ ] DT-297
- [ ] DT-298

## Policy

- [ ] good-allocation definition frozen
- [ ] hard/soft separation frozen
- [ ] lexicographic strategy frozen
- [ ] tier order frozen
- [ ] fairness rationale complete
- [ ] business rationale complete
- [ ] deferral taxonomy defined

## Agent stage

- priority tests: PASS / FAIL
- policy metric tests: PASS / FAIL
- upstream Task 2B tests: PASS / FAIL
- full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- policy context: PASS / FAIL
- metadata coverage: PASS / FAIL
- impossible-order guard: PASS / FAIL
- objective config: PASS / FAIL

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- private rows exposed: NO
- optimizer run: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 21 STATUS: PASS / FAIL
READY FOR PHASE 22: YES / NO
```

---

# 46. Final Phase 21 checklist

Before Phase 22:

- [ ] Phase 18 passed.
- [ ] Phase 19 passed.
- [ ] Phase 20 passed.
- [ ] official hard rules remain immutable.
- [ ] hard rules are separate from priority policy.
- [ ] "good allocation" is measurable.
- [ ] broad served-order coverage is Level 1.
- [ ] previous-deferral fairness is Level 2.
- [ ] service-recency fairness is Level 3.
- [ ] low-flexibility coverage is Level 4.
- [ ] Fresh chilled is Level 5.
- [ ] Fresh overall is Level 6.
- [ ] specialized-resource conservation is last.
- [ ] impossible orders cannot override feasibility.
- [ ] Style and Tech remain eligible.
- [ ] repeated-outlet fairness caveat is documented.
- [ ] no payday/monsoon bonus is invented.
- [ ] no delivery-window/fuel Task 2B hard rule is invented.
- [ ] no Task 1 prediction signal is used.
- [ ] no Task 2A forecast signal is used as direct order priority.
- [ ] lexicographic strategy is frozen before solver results.
- [ ] weighted alternative is rejected unless mathematically equivalent.
- [ ] priority metadata builder works.
- [ ] policy metrics work.
- [ ] fairness rationale is complete.
- [ ] business rationale is complete.
- [ ] deferral explanation taxonomy is defined.
- [ ] no optimizer exists yet.
- [ ] no final allocation has been produced.
- [ ] local policy-context validation passes.
- [ ] independent review passes.

Only then:

```text
PHASE 21 STATUS: PASS
READY FOR PHASE 22: YES
```
