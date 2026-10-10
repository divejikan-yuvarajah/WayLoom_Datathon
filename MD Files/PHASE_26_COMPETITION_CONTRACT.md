# PHASE 26 — Hero Feature: Explainable Deferral Reasoner

> **Filename:** `PHASE_26_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 26 — Hero Feature — Explainable Deferral Reasoner  
> **Task range:** **DT-350 → DT-357**  
> **Task count:** **8**  
> **Phase dependency:** **Phases 22–24**  
> **Default phase priority:** **P2**  
> **Master phase gate:** If implemented, deferral explanations are solver-grounded and do not displace required work.  
> **Execution mode:** Optional read-only counterfactual analysis over the frozen Task 2B solution.  
> **Do not modify the frozen Task 2B allocation, final CSV or final written policy.**

---

# 1. Phase 26 purpose

Phase 26 builds WayLoom's optional **Explainable Deferral Reasoner**.

The official Task 2B challenge asks teams to:

```text
explain allocation priority and deferral decisions
```

and states that judges assess:

```text
feasibility
+
reasoning behind decisions
```

The official written-policy requirement asks teams to show the calculations behind the allocation, identify what limited service, and explain:

```text
which deferrals were unavoidable
which were a choice
what those deferrals cost / impacted
```

The organizer checker:

```text
check_allocation.py
```

confirms feasibility only.

It does **not** prove optimality or explain why a specific order was deferred.

Phase 26 fills that interpretability gap with a solver-grounded counterfactual reasoner.

It must answer, for each frozen deferred order:

```text
Could this order legally be served at all?

Could it simply be inserted into the current frozen allocation?

If we force it served and re-optimize under the SAME official rules and
SAME frozen WayLoom policy, what changes?

Which policy tier becomes worse first?

Which resource constraints contribute to the tradeoff?

Is the deferral truly hard-unavoidable, a policy tradeoff, or merely one
choice among multiple policy-equivalent optima?
```

This is a **WayLoom engineering hero feature**, not an official mandatory algorithm.

---

# 2. Finalized Phase 26 master inventory

The finalized master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-350** | [C] | P2 | DT-319 + DT-337–DT-342 | Build reason-code taxonomy |
| [ ] | **DT-351** | [C] | P2 | Phases 22–24 | Detect individually infeasible orders |
| [ ] | **DT-352** | [C] | P2 | Phases 22–24 | Detect shared resource bottleneck |
| [ ] | **DT-353** | [C] | P2 | Phases 22–24 | Force deferred order in counterfactual solve |
| [ ] | **DT-354** | [C] | P2 | Phases 22–24 | Measure what must change to serve it |
| [ ] | **DT-355** | [C] | P2 | Phases 22–24 | Classify unavoidable vs policy tradeoff |
| [ ] | **DT-356** | [C] | P2 | Phases 22–24 | Generate human-readable deferral explanation |
| [ ] | **DT-357** | [C] | P2 | Phases 22–24 | Select 1–2 strong demo examples |

**Expected Phase 26 tasks:** 8  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 27:** NO

---

# 3. Official Task 2B source facts Phase 26 must respect

The official Task 2B source says:

- Scenario is `S1`.
- Depot is Peliyagoda.
- Only vehicles with `status = available` may be allocated.
- Every order must be `served` or `deferred`.
- Served orders receive `vehicle_id` and `trip_id`.
- Deferred orders leave vehicle/trip blank.
- `order_ref` is the allocation key.
- There is no single correct allocation.
- Judges assess feasibility and reasoning.

The official seven hard rules remain immutable:

1. same brand and district per trip;
2. chilled orders require reefer;
3. `van_only` requires van;
4. home-depot match;
5. whole order / no split;
6. both weight and volume capacity;
7. at most two trips per vehicle plus the official time budgets.

Exact official trip time remains:

```text
trip_minutes
=
depot_to_district_freeflow_min
+
inter_stop_freeflow_min × (number_of_orders - 1)
+
sum(service_allowance_min by brand + dock_type)
```

Return journey is not added.

Official daily vehicle budgets remain:

```text
Fresh <= 270 minutes

Style + Tech combined <= 480 minutes
```

Phase 26 must never weaken these constraints in a published explanation.

---

# 4. Official vs WayLoom scope

## Official requirement

The team must explain deferrals and reasoning.

## WayLoom engineering enhancement

The following are **not** organizer-prescribed methods:

```text
reason-code taxonomy

direct-insertion analysis

forced-order counterfactual optimization

objective-vector comparison

minimal-change counterfactual witness

demo-example selection
```

They are WayLoom methods used to make the explanation more defensible.

Do not claim:

```text
"the organizer requires counterfactual optimization"
```

---

# 5. Why this phase exists after Phase 24

Phase 24 already produced the official final:

```text
outputs/submission_task2b.csv
```

and final written policy.

Phase 26 must **not retroactively alter them**.

Its role is to support:

- stronger demo storytelling;
- judge Q&A;
- explainability visuals;
- later notebook/evidence material;
- precise answers to "why was this order deferred?"

If Phase 26 discovers a genuine contradiction in the frozen Task 2B allocation:

```text
STOP
```

Do not silently change the final CSV.

The relevant frozen phase must be reopened explicitly.

---

# 6. Preconditions

Before implementation/local real run, require:

```text
PHASE 22: PASS / FROZEN

PHASE 23: PASS

PHASE 24: PASS / FINAL
```

Require:

```text
Phase 22 frozen allocation hash valid

Phase 22 frozen objective vector valid

Phase 21 priority config hash valid

Phase 23 organizer checker PASS

Phase 24 final submission parity PASS
```

If any precondition fails:

```text
PHASE 26 BLOCKED
```

---

# 7. Frozen artifacts

Phase 26 must not modify:

```text
data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv

reports/private/phase22_task2b_optimizer/freeze_manifest.json

outputs/submission_task2b.csv

docs/task2b_policy.md

configs/task2b_priority.yaml
```

It also must not change:

```text
Task 1 frozen artifacts

Task 2A frozen artifacts
```

Counterfactual allocations are diagnostics only.

They are not official outputs.

---

# 8. Frozen-hash guard

Before the real Phase 26 run, hash at least:

```text
data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv

outputs/submission_task2b.csv

docs/task2b_policy.md

configs/task2b_priority.yaml
```

After reasoner generation, hash them again.

Require exact equality.

If any differs:

```text
PHASE 26 FAIL
```

---

# 9. Recommended implementation files

Create/update:

```text
src/task2b/reason_codes.py

src/task2b/individual_feasibility.py

src/task2b/direct_insertion.py

src/task2b/counterfactual_reasoner.py

src/task2b/counterfactual_delta.py

src/task2b/deferral_explanations.py

src/task2b/demo_example_selector.py

scripts/build_task2b_deferral_reasoner.py

scripts/validate_task2b_deferral_reasoner.py

configs/task2b_deferral_reasoner.yaml

docs/task2b_deferral_reasoner.md

docs/task2b_deferral_reasoner_spec.md

tests/test_task2b_reason_codes.py

tests/test_task2b_individual_feasibility.py

tests/test_task2b_direct_insertion.py

tests/test_task2b_counterfactual_reasoner.py

tests/test_task2b_counterfactual_delta.py

tests/test_task2b_deferral_explanations.py

tests/test_task2b_demo_example_selector.py
```

Reuse approved Phase 19–22 helpers.

Do not duplicate the official hard constraints into an inconsistent second solver when existing Phase 22 model-building interfaces can be reused.

---

# 10. Private Phase 26 outputs

Recommended:

```text
reports/private/phase26_task2b_deferral_reasoner/
├── run_manifest.json
├── deferral_reasons.csv
├── deferral_reason_summary.json
├── individual_feasibility_audit.csv
├── direct_insertion_audit.csv
├── counterfactual_objective_audit.csv
├── counterfactual_change_audit.csv
├── resource_bottleneck_audit.csv
├── reason_consistency_audit.json
├── demo_examples_private.json
├── demo_examples_sanitized.json
├── frozen_hash_audit.json
└── phase26_reasoner_report.md
```

No Phase 26 output should be written into:

```text
data/interim/task2b_final_allocation.csv

outputs/submission_task2b.csv
```

---

# 11. Private deferral-reason schema

Recommended one row per frozen deferred `order_ref`:

```text
order_ref

reason_class

primary_reason_code

secondary_reason_codes

evidence_level

compatible_vehicle_count

individually_feasible

direct_insert_possible

forced_solve_status

forced_policy_vector_relation

first_degraded_policy_tier

minimum_changed_orders

served_to_deferred_count

deferred_to_served_count

reassigned_served_count

affected_vehicle_count

affected_trip_count

resource_evidence_summary

human_explanation

counterfactual_complete
```

This row-level file is private.

Competition-facing artifacts should use anonymized labels.

---

# 12. High-level reason classes

Define exactly:

```text
UNAVOIDABLE_HARD

POLICY_TRADEOFF

ALTERNATIVE_OPTIMUM
```

Optional internal-only processing state:

```text
UNRESOLVED
```

But final Phase 26 PASS requires:

```text
unresolved deferred orders = 0
```

unless the team explicitly decides to skip Phase 26 as optional.

Do not publish guessed explanations.

---

# 13. DT-350 — Build reason-code taxonomy

Phase 21 already defined a stable deferral vocabulary.

Phase 26 should formalize and operationalize it.

Required codes:

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

Do not silently rename them.

---

# 14. Reason-code registry contract

Each code should define:

```text
code

reason_class compatibility

short label

technical definition

minimum evidence required

allowed human wording

forbidden overclaim

official constraint/resource association
```

Recommended object:

```python
ReasonCodeDefinition
```

The registry must reject:

```text
unknown code

duplicate code

code/class contradiction
```

---

# 15. HARD_NO_COMPATIBLE_VEHICLE

Use only when:

```text
compatible_vehicle_count == 0
```

across the **available** S1 fleet after all static official compatibility checks:

```text
refrigeration

van-only

home depot

individual weight

individual volume
```

Allowed wording:

```text
"No available vehicle can legally carry the whole order under the static
Task 2B compatibility constraints."
```

Do not say:

```text
"the optimizer chose not to serve it"
```

---

# 16. CAPACITY_COMPETITION

Use only when:

- target is individually feasible;
- the current shared allocation creates weight/volume competition;
- direct insertion is blocked by trip capacity or the forced counterfactual requires displacement/repacking supported by capacity evidence.

Do not use merely because the order has nonzero weight/volume.

---

# 17. SCARCE_REEFER_CAPACITY

Use only when:

- target is chilled;
- legal compatible options depend on reefer capability;
- actual direct-insertion/counterfactual evidence shows the reefer pool is relevant to the tradeoff.

Do not assign to every chilled deferred order automatically.

---

# 18. SCARCE_REEFER_VAN_CAPACITY

Use only when:

```text
temp_requirement = chilled

parking_constraint = van_only
```

and legal options depend on the reefer-van subset **and** counterfactual evidence shows that subset is resource-constrained.

This is a stronger/more specific reason than generic reefer scarcity.

Avoid double-counting as the sole primary cause when evidence is mixed.

---

# 19. TRIP_SLOT_LIMIT

Use when:

- a target cannot use an existing same-brand+district trip;
- serving it would require a new trip;
- compatible vehicles already use both allowed trip slots or a counterfactual must rearrange trips because of the two-trip cap.

Official rule:

```text
at most two trips total per vehicle
```

Do not invent:

```text
trip 1 must exist before trip 2
```

as an official reason.

---

# 20. FRESH_TIME_BUDGET

Use when the official:

```text
Fresh <=270 minutes per vehicle
```

budget is directly implicated in:

- one-order hard infeasibility; or
- direct insertion failure; or
- counterfactual reallocation pressure.

Do not call Fresh time limiting without evidence.

---

# 21. STYLE_TECH_TIME_BUDGET

Use when the official:

```text
Style + Tech combined <=480 minutes per vehicle
```

budget is directly implicated.

Style and Tech share the same budget.

Do not treat them as separate 480-minute budgets.

---

# 22. LOWER_POLICY_PRIORITY

Use when:

- the target is hard-feasible;
- force-serving it yields a lexicographically **worse** objective vector than the frozen baseline;
- the first degraded Phase 21 policy tier is identified.

This is a policy reason, not a physical hard-constraint reason.

It should usually be accompanied by one or more physical resource/context reasons where evidence supports them.

---

# 23. ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN

Use when:

- force-serving the target is hard-feasible;
- the forced counterfactual reproduces the **same entire Phase 21 objective vector** as the frozen solution.

Meaning:

```text
the frozen allocation is one of multiple policy-equivalent feasible optima
```

Do not label the order:

```text
unavoidable
```

or:

```text
lower policy priority
```

when the full objective vector is equal.

---

# 24. Evidence levels

Recommended internal evidence levels:

```text
PROVEN_HARD

PROVEN_COUNTERFACTUAL_POLICY

DIRECT_INSERTION_RESOURCE

SPECIALIZED_RESOURCE_CONTEXT

DESCRIPTIVE_ONLY
```

Strong human claims must use:

```text
PROVEN_HARD
```

or:

```text
PROVEN_COUNTERFACTUAL_POLICY
```

Resource context may be secondary.

Do not promote descriptive scarcity into proof.

---

# 25. DT-351 — Detect individually infeasible orders

"Individually infeasible" means:

> Even if every other order were removed from consideration, no available vehicle could legally serve this whole order under the official hard constraints.

This is stronger than:

```text
deferred in the frozen solution
```

---

# 26. Individual feasibility — static stage

Use the Phase 19 compatibility matrix.

For each frozen deferred order:

```text
compatible_vehicle_count
```

If:

```text
0
```

then:

```text
individually_feasible = false

reason_class = UNAVOIDABLE_HARD

primary_reason_code = HARD_NO_COMPATIBLE_VEHICLE
```

---

# 27. Individual feasibility — exact single-order trip stage

For each statically compatible vehicle, calculate a one-order trip.

Official formula becomes:

```text
trip_minutes
=
outbound
+
0
+
service_allowance
```

because:

```text
number_of_orders - 1 = 0
```

Apply:

```text
Fresh <=270
```

or:

```text
Style+Tech <=480
```

as appropriate.

If at least one available compatible vehicle can legally run the order alone:

```text
individually_feasible = true
```

---

# 28. Individual hard-time infeasibility

If:

```text
compatible_vehicle_count > 0
```

but every one-order legal trip exceeds the applicable official daily budget:

the order is still hard-unavoidable.

Primary/secondary reason should identify:

```text
FRESH_TIME_BUDGET
```

or:

```text
STYLE_TECH_TIME_BUDGET
```

as proven hard evidence.

Do not force everything into `HARD_NO_COMPATIBLE_VEHICLE`.

---

# 29. Defensive compatibility recheck

Although Phase 19 already validated static compatibility, Phase 26 should fail closed if:

```text
Phase19 compatible pair
```

violates:

```text
chilled→reefer

van_only→van

home depot

individual weight fit

individual volume fit
```

This is an upstream-contract contradiction.

Do not generate explanations on inconsistent inputs.

---

# 30. DT-352 — Detect shared resource bottleneck

A useful resource explanation must distinguish:

```text
cannot serve this order at all
```

from:

```text
cannot simply add this order to the frozen plan without changing something
```

Build a direct-insertion analyzer.

---

# 31. Direct-insertion question

For each individually feasible frozen deferred order:

> Can it be added to the **existing frozen allocation** while keeping every other order's decision and assignment unchanged?

If yes:

```text
direct_insert_possible = true
```

If no:

record why each legal insertion path fails.

---

# 32. Existing same-group trip insertion

For each compatible vehicle and each frozen trip with the same:

```text
brand
district
```

evaluate adding the target.

Recompute:

```text
trip weight

trip volume

exact trip minutes

vehicle Fresh total

vehicle Style+Tech total
```

Require all official hard rules.

Do not use approximate residual capacity.

Use exact Phase 20 arithmetic.

---

# 33. New-trip insertion

If a compatible vehicle has fewer than two used trips:

consider placing the target into a new trip.

The new trip is:

```text
one brand

one district

one order initially
```

Check:

```text
capacity

single-order trip time

vehicle time budget

max two trips
```

Do not require trip IDs to be globally unique.

---

# 34. Direct-insertion blocker taxonomy

Internal diagnostic blockers may include:

```text
GROUP_MISMATCH_REQUIRES_NEW_TRIP

NO_FREE_TRIP_SLOT

WEIGHT_CAPACITY

VOLUME_CAPACITY

FRESH_TIME_BUDGET

STYLE_TECH_TIME_BUDGET

STATIC_COMPATIBILITY
```

These internal labels are not new official rules.

They are diagnostic evidence mapped to the stable reason taxonomy.

---

# 35. Critical Level-1 contradiction guard

Phase 22's first objective is:

```text
maximize served_order_count
```

Therefore:

If a frozen deferred order can be inserted directly without changing any other decision/assignment and without violating any hard rule, then the frozen allocation was not Level-1 optimal.

That is a **hard blocker**.

Phase 26 must return:

```text
DIRECT_INSERTION_CONTRADICTION
```

and stop.

Do not write:

```text
"it was deferred because of lower priority"
```

---

# 36. Resource bottleneck evidence standards

A physical reason should be stated only when supported.

For example:

```text
CAPACITY_COMPETITION
```

needs capacity evidence.

```text
TRIP_SLOT_LIMIT
```

needs actual two-trip pressure.

```text
FRESH_TIME_BUDGET
```

needs actual 270-minute blocking evidence.

```text
SCARCE_REEFER_CAPACITY
```

needs specialized resource involvement beyond merely being chilled.

One deferral may legitimately have multiple secondary reasons.

---

# 37. DT-353 — Force deferred order in counterfactual solve

For every frozen deferred order, create a diagnostic solve with:

```text
serve[target_order] == 1
```

Use the exact approved Phase 22 hard-constraint model.

Do not build a looser explanation-only model.

Do not alter:

```text
official constraints

Phase21 priority hierarchy

numeric scaling

trip-time formula
```

---

# 38. Counterfactual feasibility smoke

Run the hard model with target forced served.

## Individually hard-infeasible order

Expected:

```text
INFEASIBLE
```

## Individually feasible order

Expected:

```text
FEASIBLE
or
OPTIMAL
```

If the individual evaluator and hard model disagree:

```text
STOP
```

Because all other orders can be deferred, a truly individually feasible order should be hard-feasible when forced served.

---

# 39. Why this consistency rule is powerful

Task 2B permits deferral.

Therefore, for an order that fits at least one available vehicle by itself and fits its single-order time budget:

```text
serve target
defer all others
```

should be a hard-feasible allocation.

If the Phase 22 model says otherwise:

the model and individual feasibility logic disagree.

Do not classify the order until resolved.

---

# 40. Forced lexicographic policy solve

For every hard-feasible target, run the same Phase 21 objective sequence:

```text
Level 1 MAX served_order_count

Level 2 MAX served_previous_deferred_count

Level 3 MAX served_waiting_days_sum

Level 4 MAX served_low_flexibility_count

Level 5 MAX served_fresh_chilled_count

Level 6 MAX served_fresh_count

Level 7A MIN avoidable_reefer_van_assignment_count

Level 7B MIN avoidable_reefer_assignment_count

Level 7C MIN avoidable_van_assignment_count
```

Require every stage:

```text
OPTIMAL
```

before claiming a complete reason.

---

# 41. Baseline policy vector

The baseline objective vector must come from frozen Phase 22 evidence.

Recommended:

1. load frozen vector from Phase 22 manifest/report;
2. recompute vector from frozen allocation using Phase 21 metric helpers;
3. require equality.

If not equal:

```text
STOP
```

No counterfactual comparison is trustworthy until baseline evidence is consistent.

---

# 42. Direction-aware objective vector representation

Create a strongly typed structure such as:

```python
PolicyObjectiveVector
```

Each level should record:

```text
level_id

name

direction

value
```

Directions:

```text
MAX for 1–6

MIN for 7A–7C
```

Never compare raw tuples without direction semantics.

---

# 43. Forced-vector trichotomy

For an individually feasible forced-target solve, compare:

```text
forced objective vector
```

to:

```text
frozen baseline vector
```

Exactly one relation:

```text
WORSE

EQUAL

BETTER
```

---

# 44. BETTER-than-baseline is impossible under a correct freeze

The force-served model adds a constraint.

Its feasible set is a subset of the original Phase 22 feasible set.

Therefore, if Phase 22 truly found the lexicographic optimum:

```text
forced vector
```

cannot be:

```text
BETTER
```

than baseline.

If it is:

```text
PHASE 22 OPTIMALITY/EVIDENCE CONTRADICTION
```

Stop Phase 26.

This is a powerful integrity check.

---

# 45. EQUAL forced vector

If:

```text
forced vector == baseline vector
```

then there exists an equally policy-optimal feasible allocation that serves the target.

Classification:

```text
ALTERNATIVE_OPTIMUM
```

Primary reason:

```text
ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN
```

Do not call the deferral unavoidable.

---

# 46. WORSE forced vector

If the forced vector is lexicographically worse:

the target can be served legally, but doing so sacrifices a higher-ranked WayLoom policy outcome.

Classification:

```text
POLICY_TRADEOFF
```

Primary reason:

```text
LOWER_POLICY_PRIORITY
```

Then identify the first degraded policy tier.

---

# 47. First degraded policy tier

Examples:

## Level 1

```text
Serving the target reduces the maximum number of total orders served.
```

## Level 2

```text
Total coverage can be preserved, but fewer previously-deferred orders can be served.
```

## Level 3

```text
Earlier tiers stay equal, but total served waiting-days is lower.
```

## Level 4

```text
Earlier tiers equal, but fewer low-flexibility orders are served.
```

## Level 5

```text
Earlier tiers equal, but fewer Fresh chilled orders are served.
```

## Level 6

```text
Earlier tiers equal, but fewer Fresh orders are served.
```

## Level 7A/B/C

```text
Service/fairness tiers remain equal, but specialized-resource stewardship is worse.
```

This is the policy-grounded explanation.

---

# 48. DT-354 — Measure what must change to serve it

A counterfactual allocation can differ from the frozen plan in many ways.

Phase 26 should find a **closest policy-optimal forced-target witness**.

This is diagnostic only.

---

# 49. Diagnostic minimal-change solve

After the forced-target lexicographic vector is fully solved:

1. add equality constraints fixing every objective level to its forced-target optimum;
2. add one final diagnostic objective:
   minimize allocation rows changed from frozen solution.

This final objective must **not** be added to Phase 21 or Phase 22.

It is explanation-only.

---

# 50. Changed-order definition

For each order:

Frozen state:

```text
decision
vehicle_id
trip_id
```

Counterfactual state:

same fields.

A row is unchanged only if all relevant assignment semantics match.

For frozen deferred order:

```text
changed[o] = serve[o]
```

For frozen served at `(v0,t0)`:

```text
changed[o] = 1 - x[o,v0,t0]
```

Thus any:

```text
served→deferred

vehicle reassignment

trip reassignment
```

counts as changed.

---

# 51. Minimum-change claim standard

If diagnostic solve status:

```text
OPTIMAL
```

you may say:

```text
"the closest policy-optimal counterfactual requires X changed allocation rows"
```

If only:

```text
FEASIBLE
```

you may only say:

```text
"a counterfactual was found with X changes"
```

But Phase 26 final gate should require OPTIMAL if the feature advertises minimum changes.

---

# 52. Counterfactual change metrics

Measure:

```text
changed_order_count

served_to_deferred_count

deferred_to_served_count

served_reassigned_count

affected_vehicle_count

affected_trip_count
```

Also compare affected resource usage:

```text
weight

volume

Fresh minutes

Style+Tech minutes

trip slots

specialized vehicle use
```

Detailed IDs remain private.

---

# 53. Policy-delta metrics

Record difference between:

```text
baseline vector
forced vector
```

with direction-aware normalized deltas.

For MAX tiers:

```text
forced - baseline
```

For MIN tiers, consider storing both raw delta and a normalized:

```text
worsening_amount
```

where positive means worse.

This avoids confusing demo logic.

---

# 54. DT-355 — Classify unavoidable vs policy tradeoff

Use strict solver-grounded classification.

---

# 55. UNAVOIDABLE_HARD

Require:

```text
no hard-feasible allocation can serve target
```

Evidence should agree across:

```text
individual feasibility
forced hard solve
```

Do not use the word:

```text
unavoidable
```

without this proof.

---

# 56. POLICY_TRADEOFF

Require:

```text
forced target hard-feasible
```

and:

```text
forced lexicographic vector WORSE than frozen baseline
```

Meaning:

the frozen WayLoom policy prefers another feasible allocation.

This is a choice under constrained resources, not hard impossibility.

---

# 57. ALTERNATIVE_OPTIMUM

Require:

```text
forced target hard-feasible
```

and:

```text
forced vector EQUAL to baseline
```

Meaning:

the frozen solution chose one policy-equivalent optimum among multiple feasible alternatives.

This category is especially valuable for honest explainability.

Do not pretend every final solver choice is uniquely justified.

---

# 58. Classification consistency matrix

| Hard feasible? | Forced policy vector | Classification |
|---|---|---|
| No | N/A | `UNAVOIDABLE_HARD` |
| Yes | Worse | `POLICY_TRADEOFF` |
| Yes | Equal | `ALTERNATIVE_OPTIMUM` |
| Yes | Better | **BLOCKER — Phase 22 contradiction** |

---

# 59. Resource codes vs classification

Resource reasons are supporting evidence.

Example:

```text
reason_class:
POLICY_TRADEOFF

primary_reason_code:
LOWER_POLICY_PRIORITY

secondary_reason_codes:
[
  TRIP_SLOT_LIMIT,
  SCARCE_REEFER_CAPACITY
]
```

Do not collapse classification and physical evidence into one ambiguous label.

---

# 60. DT-356 — Generate human-readable explanation

Use deterministic local templates.

Do not send private orders to an LLM/API.

Inputs:

```text
reason class

reason codes

counterfactual relation

first degraded tier

change metrics

resource evidence

selected safe order context
```

Output:

```text
human_explanation
```

---

# 61. Explanation goals

Every explanation should communicate:

```text
1. feasibility status

2. optimization/policy status

3. relevant constrained resource

4. counterfactual proof

5. minimum/observed allocation change

6. limitation of the claim
```

Do not overwhelm the user with solver variable names.

---

# 62. Hard-unavoidable explanation template

Allowed structure:

> This order was deferred because no available vehicle can legally serve it under the Task 2B hard constraints. When the reasoner forced it to be served, the hard-constraint model was infeasible. Under the frozen S1 scenario this is therefore a hard-unavoidable deferral.

Use only when proven.

---

# 63. Policy-tradeoff explanation template

Allowed structure:

> This order is legally serviceable, but it cannot be added to the frozen plan without changing other assignments. When forced served, the best legal counterfactual first worsens WayLoom's frozen policy at **[tier]**. The closest policy-optimal forced counterfactual changes **[X]** allocation rows. The current deferral is therefore a shared-resource/policy tradeoff rather than hard infeasibility.

Add resource evidence only where verified.

---

# 64. Alternative-optimum explanation template

Allowed structure:

> This order can be served in a legal alternative allocation with the same complete WayLoom policy objective vector. The closest equivalent counterfactual changes **[X]** allocation rows. The frozen solution is therefore one of multiple policy-equivalent optima; this order was not hard-impossible.

This is more honest than fabricating a unique reason.

---

# 65. Physical reason wording

Allowed examples:

```text
"The frozen plan has no remaining direct insertion path because all
compatible vehicles would exceed the Fresh time budget or require a third
trip."

"The target depends on a small reefer-van-compatible vehicle set, and the
counterfactual reallocates that specialized capacity."
```

Only use if supported.

---

# 66. Avoid false sole-cause claims

If direct insertion paths fail for mixed reasons:

```text
weight on some vehicles

time on others

trip slots on others
```

do not claim:

```text
"weight capacity caused the deferral"
```

Preferred:

```text
"multiple shared constraints block direct insertion, including capacity and
time/trip-slot pressure."
```

---

# 67. Counterfactual is optimization evidence, not causal inference

These counterfactuals answer:

```text
what the optimization model must change under the frozen rules
```

They do not prove:

```text
what would definitely happen in real operations
```

Include a short limitation:

> Counterfactual explanations are conditional on the official Task 2B rules, supplied S1 data and the frozen WayLoom policy; they are optimization explanations, not real-world causal estimates.

---

# 68. DT-357 — Select 1–2 strong demo examples

Phase 26 should select at most:

```text
2
```

strong examples for later demo use.

Do not select examples manually by looking for dramatic private IDs.

Use deterministic evidence quality.

---

# 69. Preferred demo composition

Ideal:

```text
Example A:
UNAVOIDABLE_HARD

Example B:
POLICY_TRADEOFF
```

If no hard-unavoidable deferral exists:

```text
Example A:
POLICY_TRADEOFF

Example B:
ALTERNATIVE_OPTIMUM
```

or two policy tradeoffs with clearly different bottleneck evidence.

---

# 70. Demo-example scoring

Recommended criteria:

```text
counterfactual_complete

all required solver stages OPTIMAL

reason consistency PASS

clear first degraded tier

clear resource evidence

small/easy-to-explain change set

reason-class diversity

privacy-safe context
```

Tie-break:

```text
stable original order position
```

Not:

```text
largest order_ref

most dramatic value

manual cherry-pick
```

---

# 71. Demo anonymization

Use:

```text
DEFERRAL_EXAMPLE_A

DEFERRAL_EXAMPLE_B
```

Do not expose real:

```text
order_ref

outlet_id

vehicle_id

changed-order IDs
```

by default.

Safe contextual fields may include:

```text
brand

district

chilled/ambient

van_only status

compatible vehicle count

first degraded policy tier

aggregate change count

reason code
```

when needed.

---

# 72. Demo example output

Private:

```text
demo_examples_private.json
```

Sanitized:

```text
demo_examples_sanitized.json
```

The sanitized file should contain no direct identifiers.

Later demo phases can use it without reopening private row-level analysis.

---

# 73. Recommended reasoner config

Create:

```text
configs/task2b_deferral_reasoner.yaml
```

Recommended structure:

```yaml
version: 1

frozen:
  require_phase22_frozen: true
  require_phase23_pass: true
  require_phase24_pass: true
  require_hash_stability: true

reason_codes:
  source: phase21

direct_insertion:
  enabled: true
  fail_if_direct_insert_possible: true

counterfactual:
  force_target_served: true
  require_optimal_policy_stages: true
  random_seed: 42
  num_search_workers: 1
  max_time_seconds_per_stage: 120

minimal_change:
  enabled: true
  require_optimal: true

classification:
  allow_multiple_secondary_reasons: true
  allow_unresolved: false

demo:
  max_examples: 2
  anonymize_identifiers: true
  deterministic: true

privacy:
  private_report_dir: reports/private/phase26_task2b_deferral_reasoner
```

---

# 74. Solver reuse requirements

Phase 26 should reuse:

```text
Phase22 solver data

Phase22 hard constraints

Phase21 objective expressions

Phase20 trip-time helpers
```

Do not duplicate official constraints into a subtly different counterfactual solver.

If the existing optimizer builder needs a small diagnostic hook such as:

```text
force_serve_order_ref
```

implement it without changing default Phase 22 behavior.

Regression tests must prove normal Phase 22 behavior is unchanged.

---

# 75. Counterfactual path isolation

Counterfactual outputs must never target:

```text
data/interim/task2b_final_allocation.csv

data/interim/task2b_solver_allocation_candidate.csv

outputs/submission_task2b.csv
```

Recommended:

```text
reports/private/phase26_task2b_deferral_reasoner/counterfactuals/
```

or in-memory only.

No call to:

```text
freeze_allocation()
```

is allowed from Phase 26.

---

# 76. Counterfactual solver determinism

Use the same deterministic principles as Phase 22:

```text
fixed random seed

stable order construction

single worker where required for reproducibility

stable group ordering
```

Record solver version.

Repeated synthetic/local runs should yield:

```text
same objective relation

same minimum change count

same demo example selection
```

subject to frozen software/config.

---

# 77. Counterfactual runtime strategy

A full 9-stage solve for every deferred order may be computationally expensive.

Allowed optimizations:

- reuse immutable preprocessed solver data;
- cache canonical references;
- warm-start from frozen allocation where supported;
- use forced target hints;
- skip full policy solve for proven hard-infeasible orders;
- run different deferred orders independently;
- deterministic batching.

Not allowed:

- skipping policy levels;
- reducing hard constraints;
- accepting FEASIBLE-only as proof;
- changing objective tier order;
- sampling deferred orders while claiming all are explained.

---

# 78. Completeness requirement

For final Phase 26 PASS:

```text
every frozen deferred order
```

must have a completed reason record.

Require:

```text
reason row count == frozen deferred order count
```

Require:

```text
unresolved = 0
```

If runtime makes this impossible:

Phase 26 is optional.

It is better to skip/incomplete the hero feature than publish weak explanations.

---

# 79. Run manifest

Create private:

```text
run_manifest.json
```

Recommended:

```text
phase = 26

frozen allocation SHA256

frozen trip summary SHA256

final submission SHA256

final policy SHA256

priority config SHA256

optimizer config SHA256

reasoner config SHA256

deferred order count

individual hard-infeasible count

counterfactual solve count

counterfactual resolved count

counterfactual unresolved count

reason class counts

reason code counts

demo example count

solver version

seed

workers

git commit

timestamp
```

No row IDs.

---

# 80. Reason consistency audit

Create:

```text
reason_consistency_audit.json
```

Require:

```text
every deferred order has one reason class

every primary reason code exists

all secondary codes exist

class/code combinations valid

hard-unavoidable has hard proof

policy tradeoff has WORSE forced vector

alternative optimum has EQUAL vector

no forced vector BETTER than baseline

no direct insertion contradiction

no unresolved counterfactual

human text matches structured reason

demo examples are resolved/anonymized
```

---

# 81. DT-350 tests — reason taxonomy

Create:

```text
tests/test_task2b_reason_codes.py
```

Cover:

```text
all nine stable Phase21 codes

unique codes

nonempty definitions

valid evidence requirements

valid class compatibility

unknown code rejection

no silent code rename
```

---

# 82. DT-351 tests — individual feasibility

Create:

```text
tests/test_task2b_individual_feasibility.py
```

Cover:

```text
zero compatible vehicles

chilled with dry-only fleet

van_only with truck-only fleet

wrong depot

individual overweight

individual over-volume

single legal compatible vehicle

Fresh one-order time 270

Fresh one-order time 271

Style/Tech 480

Style/Tech 481

repeated outlet irrelevant because key is order_ref
```

---

# 83. DT-352 tests — direct insertion

Create:

```text
tests/test_task2b_direct_insertion.py
```

Cover:

```text
same brand+district trip with spare capacity/time

same group weight blocker

same group volume blocker

Fresh budget blocker

Style+Tech budget blocker

different group with free trip slot

different group with two used trips

mixed blocker paths

direct insertion possible -> hard contradiction guard
```

---

# 84. DT-353 tests — counterfactual reasoner

Create:

```text
tests/test_task2b_counterfactual_reasoner.py
```

Cover:

```text
hard-infeasible target -> forced INFEASIBLE

individually feasible -> forced feasible

all 9 policy levels solved

FEASIBLE-only stage rejected

UNKNOWN rejected

MODEL_INVALID rejected

forced vector better than baseline rejected

forced vector equal accepted

forced vector worse accepted
```

---

# 85. Objective-vector comparator tests

Do not rely on raw tuple comparison.

Test:

```text
MAX level higher better

MAX lower worse

MIN level lower better

MIN higher worse

first difference determines lexicographic relation

all equal

Level7 direction correctness
```

---

# 86. DT-354 tests — counterfactual delta

Create:

```text
tests/test_task2b_counterfactual_delta.py
```

Cover:

```text
target deferred→served counts changed

frozen served same vehicle/trip unchanged

served moved vehicle changed

served moved trip changed

served→deferred changed

policy vector fixed before minimal-change objective

minimum-change OPTIMAL

FEASIBLE-only not allowed for "minimum" claim
```

---

# 87. DT-355 tests — classification

Cover exact matrix:

```text
hard infeasible
→ UNAVOIDABLE_HARD

hard feasible + forced vector WORSE
→ POLICY_TRADEOFF

hard feasible + forced vector EQUAL
→ ALTERNATIVE_OPTIMUM

hard feasible + forced vector BETTER
→ BLOCKER
```

Also:

```text
hard order never LOWER_POLICY_PRIORITY

alternative optimum never "unavoidable"

policy tradeoff never "cannot legally be served"
```

---

# 88. Resource-reason tests

Require:

```text
SCARCE_REEFER_CAPACITY
```

only with actual reefer evidence.

Require:

```text
SCARCE_REEFER_VAN_CAPACITY
```

only with chilled + van_only and specialized evidence.

Require capacity/trip/time codes only with corresponding blocker evidence.

Multiple reasons allowed.

No sole-cause overclaim.

---

# 89. DT-356 tests — explanation text

Create:

```text
tests/test_task2b_deferral_explanations.py
```

Check:

- deterministic output;
- class named correctly;
- counterfactual evidence stated correctly;
- first policy tier included for tradeoff;
- minimum-change wording only if proven;
- no real IDs in sanitized text;
- no "AI decided";
- no unsupported causal wording;
- no monetary claims;
- no hard-impossible wording for policy tradeoff.

---

# 90. DT-357 tests — demo selector

Create:

```text
tests/test_task2b_demo_example_selector.py
```

Cover:

```text
max two examples

deterministic

classification diversity preferred

unresolved excluded

hard example preferred when clean

policy tradeoff selected when strong

alternative optimum usable when appropriate

stable tie-break

anonymized labels

no real IDs
```

---

# 91. End-to-end synthetic reasoner test

Build a synthetic scenario containing:

```text
one hard-unavoidable deferred order

one policy-tradeoff deferred order

one alternative-optimum deferred order

shared reefer scarcity

trip-slot pressure

capacity pressure

time pressure
```

Run:

```text
taxonomy

individual feasibility

direct insertion

forced counterfactual

policy vector comparison

minimal-change witness

classification

text generation

demo selection
```

Require exact expected classes.

No private data.

---

# 92. Edge case — no deferred orders

If frozen allocation serves everything:

```text
deferred_order_count = 0
```

Phase 26 should not invent examples.

Return:

```text
NO DEFERRALS TO EXPLAIN
```

DT-350 taxonomy can still exist.

DT-351–DT-356 become vacuously complete with zero reason rows.

DT-357 selects zero examples.

This should be a valid Phase 26 outcome.

---

# 93. Edge case — all deferred orders hard-infeasible

Then demo selector may choose up to two hard examples with different evidence if available.

Do not fabricate a policy-tradeoff example for diversity.

---

# 94. Edge case — all deferred orders are policy-equivalent alternatives

Then classification should honestly report:

```text
ALTERNATIVE_OPTIMUM
```

Do not force `LOWER_POLICY_PRIORITY`.

This may reveal the solver has many equivalent optima, which is legitimate.

---

# 95. Edge case — multiple physical blockers

If direct-insertion paths fail for different reasons:

record multiple secondary codes.

Do not arbitrarily choose one "true" cause unless counterfactual/relaxation evidence uniquely supports it.

---

# 96. Edge case — specialized resource necessary, not avoidable

A chilled order always needs reefer.

That does not by itself prove:

```text
SCARCE_REEFER_CAPACITY
```

Scarcity requires evidence that the limited reefer set constrains the allocation.

---

# 97. Edge case — forced solve timeout

If any required stage returns:

```text
FEASIBLE
UNKNOWN
```

instead of:

```text
OPTIMAL
```

do not guess the classification.

Mark:

```text
UNRESOLVED
```

Phase 26 cannot PASS with unresolved published explanations.

Allowed remediation:

- increase local time limit;
- improve formulation;
- use hints;
- preserve exact policy/hard rules.

---

# 98. Edge case — direct insertion is possible

This is not a normal reason result.

It is a contradiction:

```text
frozen Level1 optimum should have served one more order
```

Stop and reopen upstream Phase 22 review.

Do not continue Phase 26.

---

# 99. Edge case — forced vector is better

Also a contradiction.

If forcing the target improves the objective vector:

the frozen baseline was not lexicographically optimal under the same model.

Stop.

---

# 100. Edge case — baseline vector recomputation differs

If metrics computed from frozen allocation do not match Phase 22 frozen objective evidence:

do not choose one silently.

Stop and investigate.

---

# 101. Human-readable reason does not alter official policy

Phase 26 may reveal a more precise reason than the Phase 24 one-page policy.

Do not automatically edit:

```text
docs/task2b_policy.md
```

If the team later chooses to incorporate the hero explanation into the official policy:

explicitly reopen Phase 24

rebuild policy evidence

rerun Phase 24 validation

update hashes

rerun final audit

Otherwise keep Phase 24 final.

---

# 102. Recommended documentation

Create:

```text
docs/task2b_deferral_reasoner.md
```

Recommended sections:

```text
1. What the reasoner does
2. Official rules it preserves
3. Reason classes
4. Reason codes
5. Individual-feasibility check
6. Direct-insertion analysis
7. Forced-order counterfactual
8. Policy-vector comparison
9. Minimal-change witness
10. Demo examples
11. Limitations
```

No private real order IDs.

---

# 103. Explainability limitation statement

Include:

> The reasoner explains the frozen optimization under the supplied S1 data, official Task 2B feasibility rules and WayLoom's frozen priority policy. It does not estimate real-world causal effects, future operational behavior, or monetary impact.

---

# 104. Local build command

Recommended shape:

```bash
python scripts/build_task2b_deferral_reasoner.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --priority-config configs/task2b_priority.yaml \
  --optimizer-config configs/task2b_optimizer.yaml \
  --reasoner-config configs/task2b_deferral_reasoner.yaml \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --priority-metadata data/interim/task2b_priority_metadata.csv \
  --allocation data/interim/task2b_final_allocation.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --submission outputs/submission_task2b.csv \
  --report-dir reports/private/phase26_task2b_deferral_reasoner
```

Use actual repository interface names if different.

---

# 105. Local validation command

Recommended:

```bash
python scripts/validate_task2b_deferral_reasoner.py \
  --reasoner-config configs/task2b_deferral_reasoner.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --submission outputs/submission_task2b.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --report-dir reports/private/phase26_task2b_deferral_reasoner
```

---

# 106. Recommended sanitized local output

Target:

```text
WAYLOOM — PHASE 26 EXPLAINABLE DEFERRAL REASONER

PHASE22 FROZEN HASH                     : PASS
PHASE23 VALIDATION                      : PASS
PHASE24 FINAL OUTPUT                    : PASS

REASON TAXONOMY                         : PASS

DEFERRED ORDERS COVERED                 : PASS
INDIVIDUAL FEASIBILITY                  : PASS

DIRECT INSERTION CONTRADICTIONS         : 0

FORCED COUNTERFACTUALS                  : PASS
REQUIRED POLICY STAGES OPTIMAL          : PASS

BASELINE OBJECTIVE VECTOR               : PASS
BETTER-THAN-BASELINE CONTRADICTIONS     : 0

MINIMAL-CHANGE COUNTERFACTUALS          : PASS

UNRESOLVED REASONS                      : 0
REASON CONSISTENCY                      : PASS

HUMAN EXPLANATIONS                      : PASS

DEMO EXAMPLES SELECTED                  : 1–2
DEMO IDENTIFIERS ANONYMIZED             : PASS

FROZEN ALLOCATION UNCHANGED             : PASS
FINAL submission_task2b.csv UNCHANGED   : PASS
TASK2B POLICY UNCHANGED                 : PASS

PHASE 26                                : PASS
READY FOR PHASE 27                      : YES
```

No private IDs.

---

# 107. STOP conditions

`READY FOR PHASE 27` remains **NO** if:

- Phase 22 is not frozen;
- Phase 23 is not PASS;
- Phase 24 is not PASS;
- frozen allocation hash mismatch;
- trip-summary hash mismatch;
- final submission hash mismatch;
- priority config hash mismatch;
- reason code not in frozen taxonomy;
- static compatibility contradiction;
- individual feasibility and forced hard solve disagree;
- a frozen deferred order can be directly inserted without changing others;
- baseline objective vector mismatch;
- forced objective vector is better than baseline;
- any required counterfactual policy stage is not OPTIMAL;
- minimum-change solve is not OPTIMAL while claiming minimum;
- unresolved reason remains;
- hard-infeasible order is labeled lower priority;
- policy tradeoff is labeled hard-unavoidable;
- alternative optimum is labeled unavoidable;
- resource reason lacks evidence;
- reefer scarcity is inferred merely from chilled requirement;
- explanation says "AI decided";
- explanation overclaims causal real-world effect;
- public/demo output exposes private IDs;
- counterfactual allocation writes into canonical Phase 22 paths;
- Phase 24 final output changes;
- Phase 24 policy changes;
- Phase 21 objective changes;
- official checker changes;
- Task 1/Task 2A frozen artifacts change;
- external LLM/API receives private competition rows;
- Phase 27 work introduced;
- tests fail;
- `pip check` fails;
- independent review fails.

---

# 108. Definition of Done

Phase 26 is complete only when:

- [ ] DT-350 PASS
- [ ] DT-351 PASS
- [ ] DT-352 PASS
- [ ] DT-353 PASS
- [ ] DT-354 PASS
- [ ] DT-355 PASS
- [ ] DT-356 PASS
- [ ] DT-357 PASS
- [ ] Phase 22 frozen hash verified
- [ ] Phase 23 PASS verified
- [ ] Phase 24 PASS verified
- [ ] reason-code registry exactly reflects stable Phase 21 codes
- [ ] every deferred order covered exactly once
- [ ] individually infeasible orders proven
- [ ] direct insertion evaluated for every individually feasible deferred order
- [ ] direct insertion contradiction count = 0
- [ ] forced target hard solve consistent with individual feasibility
- [ ] exact Phase 22 hard constraints reused
- [ ] exact Phase 21 objective order reused
- [ ] every required forced policy stage OPTIMAL
- [ ] baseline objective vector recomputes exactly
- [ ] forced vector is never better than baseline
- [ ] direction-aware vector comparator tested
- [ ] minimum-change witness runs only after policy vector fixed
- [ ] minimum-change solve OPTIMAL
- [ ] every hard-unavoidable reason has hard proof
- [ ] every policy-tradeoff reason has WORSE-vector proof
- [ ] every alternative-optimum reason has EQUAL-vector proof
- [ ] physical resource reasons are evidence-grounded
- [ ] no false sole-bottleneck claims
- [ ] deterministic human explanation generated
- [ ] counterfactual limitation disclosed
- [ ] unresolved reason count = 0
- [ ] 0–2 demo examples selected appropriately
- [ ] demo example IDs anonymized
- [ ] no private IDs in competition-facing artifacts
- [ ] no canonical allocation written
- [ ] frozen Task 2B allocation hash unchanged
- [ ] frozen trip-summary hash unchanged
- [ ] final `submission_task2b.csv` hash unchanged
- [ ] final `task2b_policy.md` hash unchanged
- [ ] safe Phase 26 tests pass
- [ ] relevant Phase 19–24 tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] independent Phase 26 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 26 STATUS: PASS
EXPLAINABLE DEFERRAL REASONER: COMPLETE
FROZEN TASK 2B ALLOCATION: UNCHANGED
READY FOR PHASE 27: YES
```

---

# 109. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-26-deferral-reasoner
```

Recommended commits:

```text
feat(task2b): add deferral reason taxonomy and individual feasibility
feat(task2b): add direct-insertion and forced-order counterfactual reasoner
feat(task2b): add policy-vector and minimal-change explanation
feat(task2b): add anonymized deferral demo example selection
test(task2b): add counterfactual deferral reasoner coverage
docs(task2b): document solver-grounded deferral explanations
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

Do not commit private real counterfactual reason tables to a public repository.

---

# 110. Recommended model

Phase 26 is one of the more reasoning-intensive optional phases because it combines:

- official hard-constraint integrity;
- frozen lexicographic optimization;
- counterfactual solving;
- direction-aware objective comparison;
- minimum-change witness optimization;
- strict unavoidable-vs-choice classification;
- explainability language.

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

Do not use a low-reasoning setting for the initial counterfactual formulation.

---

# 111. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 26 only.

PHASE:
Hero Feature — Explainable Deferral Reasoner

TASK RANGE:
DT-350 through DT-357

EXECUTION MODE:
OPTIONAL HIGH-INTEGRITY SOLVER-GROUNDED EXPLANATION FEATURE.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 27.

==================================================
MISSION
==================================================

Build a solver-grounded reasoner that explains WHY a frozen Task 2B order
was deferred without changing the official allocation.

Required work:

DT-350 Build reason-code taxonomy
DT-351 Detect individually infeasible orders
DT-352 Detect shared resource bottleneck
DT-353 Force deferred order in counterfactual solve
DT-354 Measure what must change to serve it
DT-355 Classify unavoidable vs policy tradeoff
DT-356 Generate human-readable deferral explanation
DT-357 Select 1–2 strong demo examples

This is a HERO / EXPLANATION feature.

It must NOT:
- change the Phase 22 frozen allocation
- change Phase 21 priority policy
- change outputs/submission_task2b.csv
- change docs/task2b_policy.md
- weaken official hard constraints
- rewrite Phase 23 checker evidence
- claim organizer checker proves optimality
- invent causal explanations

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 26
4. PHASE_19_COMPETITION_CONTRACT.md
5. PHASE_20_COMPETITION_CONTRACT.md
6. PHASE_21_COMPETITION_CONTRACT.md
7. PHASE_22_COMPETITION_CONTRACT.md
8. PHASE_23_COMPETITION_CONTRACT.md
9. PHASE_24_COMPETITION_CONTRACT.md
10. PHASE_26_COMPETITION_CONTRACT.md

Inspect existing Task 2B implementation:

11. src/task2b/compatibility.py
12. src/task2b/scarcity.py
13. src/task2b/trip_time.py
14. src/task2b/priority.py
15. src/task2b/policy_metrics.py
16. src/task2b/solver_data.py
17. src/task2b/optimizer.py
18. src/task2b/lexicographic_solver.py
19. src/task2b/solution.py
20. src/task2b/solution_audit.py
21. src/task2b/allocation_validator.py

Inspect configs:

22. configs/task2b_scenario.yaml
23. configs/task2b_compatibility.yaml
24. configs/task2b_trip_time.yaml
25. configs/task2b_priority.yaml
26. configs/task2b_optimizer.yaml
27. configs/task2b_validation.yaml

Inspect relevant Task 2B tests.

Do not assume interface names if repository differs.
Reuse approved implementations rather than duplicate hard constraints.

==================================================
OFFICIAL SOURCE BOUNDARY
==================================================

The official Task 2B challenge requires:

- every order served/deferred
- served orders assigned vehicle + trip
- all seven feasibility rules
- a short prioritization policy explaining allocation priority/deferrals
- calculations behind the allocation
- what limited service
- which deferrals were unavoidable
- which deferrals were choices
- their operational consequences/cost

The booklet explicitly says:

there is no single correct allocation

judges assess feasibility and reasoning

check_allocation.py proves feasibility, NOT optimality

The Explainable Deferral Reasoner itself is a WayLoom engineering hero
feature.

Do NOT describe it as organizer-mandated.

==================================================
PRECONDITIONS
==================================================

Require:

Phase 22 final allocation:
FROZEN

Phase 23:
PASS

Phase 24:
PASS / FINAL

Phase 21 priority config:
frozen

Phase 22 objective vector:
available

Phase 22 freeze hashes:
valid

Phase 23 official checker:
PASS

Phase 24 submission:
final

If any precondition fails:
STOP.

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect private real competition rows in external-agent context.

Use synthetic fixtures for Codex-run tests.

The human will execute real counterfactual reasoning locally.

Do not print:

real order_ref values

real vehicle/order assignments

real changed-order lists

real trip membership

private counterfactual allocation rows

Private local reports may contain row-level evidence where necessary.

Competition/demo-facing examples must be anonymized.

==================================================
FROZEN ARTIFACTS — MUST NOT CHANGE
==================================================

Do NOT modify:

data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv

reports/private/phase22_task2b_optimizer/freeze_manifest.json

outputs/submission_task2b.csv

docs/task2b_policy.md

configs/task2b_priority.yaml

Phase 22 optimizer semantics

Official check_allocation.py

Task1 / Task2A frozen outputs

Compute pre/post hashes where appropriate.

Any frozen Task 2B allocation/output hash change:
FAIL.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/reason_codes.py

src/task2b/individual_feasibility.py

src/task2b/direct_insertion.py

src/task2b/counterfactual_reasoner.py

src/task2b/counterfactual_delta.py

src/task2b/deferral_explanations.py

src/task2b/demo_example_selector.py

scripts/build_task2b_deferral_reasoner.py

scripts/validate_task2b_deferral_reasoner.py

configs/task2b_deferral_reasoner.yaml

docs/task2b_deferral_reasoner.md

docs/task2b_deferral_reasoner_spec.md

tests/test_task2b_reason_codes.py

tests/test_task2b_individual_feasibility.py

tests/test_task2b_direct_insertion.py

tests/test_task2b_counterfactual_reasoner.py

tests/test_task2b_counterfactual_delta.py

tests/test_task2b_deferral_explanations.py

tests/test_task2b_demo_example_selector.py

Do NOT create Phase27 uncertainty work.

==================================================
PHASE26 PRIVATE OUTPUTS
==================================================

Use:

reports/private/phase26_task2b_deferral_reasoner/

Recommended artifacts:

run_manifest.json

deferral_reasons.csv

deferral_reason_summary.json

individual_feasibility_audit.csv

direct_insertion_audit.csv

counterfactual_objective_audit.csv

counterfactual_change_audit.csv

resource_bottleneck_audit.csv

reason_consistency_audit.json

demo_examples_private.json

demo_examples_sanitized.json

frozen_hash_audit.json

phase26_reasoner_report.md

Do not write counterfactual allocations into canonical Phase22 paths.

==================================================
REASONER OUTPUT GRAIN
==================================================

Private deferral reason table:

one row per FROZEN deferred order_ref.

At minimum:

order_ref

reason_class

primary_reason_code

secondary_reason_codes

evidence_level

compatible_vehicle_count

individually_feasible

direct_insert_possible

forced_solve_status

forced_policy_vector_relation

first_degraded_policy_tier

minimum_changed_orders

served_to_deferred_count

deferred_to_served_count

reassigned_served_count

resource_evidence_summary

human_explanation

counterfactual_complete

Keep row-level table PRIVATE.

==================================================
DT-350 — REASON-CODE TAXONOMY
==================================================

Use the Phase21 vocabulary as the canonical starting point.

Required stable reason codes:

HARD_NO_COMPATIBLE_VEHICLE

CAPACITY_COMPETITION

SCARCE_REEFER_CAPACITY

SCARCE_REEFER_VAN_CAPACITY

TRIP_SLOT_LIMIT

FRESH_TIME_BUDGET

STYLE_TECH_TIME_BUDGET

LOWER_POLICY_PRIORITY

ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN

Do NOT silently rename existing Phase21 codes.

Define three high-level reason classes:

UNAVOIDABLE_HARD

POLICY_TRADEOFF

ALTERNATIVE_OPTIMUM

Optional internal state:

UNRESOLVED

but Phase26 cannot PASS with unresolved final deferred explanations.

==================================================
REASON CODE SEMANTICS
==================================================

HARD_NO_COMPATIBLE_VEHICLE:

No AVAILABLE vehicle legally fits the whole order under static official
compatibility:
refrigeration
van-only
home depot
individual weight
individual volume

CAPACITY_COMPETITION:

The target is individually feasible, but direct insertion/current shared
allocation is blocked by trip weight/volume capacity and a counterfactual
requires displacement/repacking.

SCARCE_REEFER_CAPACITY:

Chilled demand depends on the available reefer pool and solver-grounded
evidence shows specialized reefer capacity/flexibility is part of the
tradeoff.

SCARCE_REEFER_VAN_CAPACITY:

Chilled + van_only demand depends on reefer vans and solver-grounded evidence
shows that specialized subset is part of the tradeoff.

TRIP_SLOT_LIMIT:

Serving the target in the frozen plan would require a new trip on compatible
vehicles whose two official trip slots are already consumed, unless other
orders/trips are rearranged.

FRESH_TIME_BUDGET:

The official per-vehicle Fresh <=270 minute constraint blocks direct
insertion or creates a counterfactual tradeoff.

STYLE_TECH_TIME_BUDGET:

The official combined Style+Tech <=480 minute constraint blocks direct
insertion or creates a counterfactual tradeoff.

LOWER_POLICY_PRIORITY:

The order is hard-feasible, but forcing it served makes the frozen Phase21
lexicographic objective vector worse.

ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN:

The order can be served while preserving the entire Phase21 objective vector;
the frozen solution is one of multiple policy-equivalent feasible optima.

==================================================
TAXONOMY DESIGN RULES
==================================================

reason_class and reason_code are different concepts.

Example:

reason_class:
POLICY_TRADEOFF

primary_reason_code:
LOWER_POLICY_PRIORITY

secondary_reason_codes:
[
  TRIP_SLOT_LIMIT,
  FRESH_TIME_BUDGET
]

Do not force one physical bottleneck code when evidence shows several.

Allow multiple secondary resource reasons.

Every code must have:

definition

required evidence

allowed human wording

forbidden overclaim

==================================================
DT-351 — INDIVIDUALLY INFEASIBLE ORDERS
==================================================

Evaluate every frozen deferred order independently.

Use:

Phase19 AVAILABLE compatible vehicle set

plus exact Phase20 one-order trip time.

Step 1:
static compatibility.

If compatible_vehicle_count == 0:

individually_feasible = false

reason_class = UNAVOIDABLE_HARD

primary_reason_code = HARD_NO_COMPATIBLE_VEHICLE

Step 2:
for every statically compatible vehicle, evaluate the order alone on one trip.

Apply exact official trip formula:

outbound
+
0 inter-stop
+
service allowance

Then applicable vehicle budget:

Fresh:
<=270

Style/Tech:
<=480

If at least one compatible vehicle can legally run that one-order trip:

individually_feasible = true

If none can:

individually_feasible = false

use the appropriate hard time-budget reason evidence.

Do not call shared trip-slot pressure an individual infeasibility.

An order alone needs only one trip.

==================================================
INDIVIDUAL FEASIBILITY CONSISTENCY
==================================================

Because Phase19 compatibility already includes:

refrigeration

van-only

home depot

individual weight

individual volume

a statically compatible vehicle should satisfy those checks.

Recheck defensively.

If Phase19 says compatible but static official rule fails:

STOP.

Do not hide upstream inconsistency.

==================================================
DT-352 — SHARED RESOURCE BOTTLENECK
==================================================

Build a DIRECT INSERTION analysis against the frozen allocation.

This asks:

"Could this deferred order be inserted into the existing frozen plan without
changing any other order's decision or assignment?"

For every compatible vehicle, evaluate:

A. existing trip with same brand + district

Can target be added while preserving:

weight

volume

vehicle Fresh budget or Style+Tech budget

B. unused trip slot

Can a new legal trip be created while preserving:

max 2 trips

brand/district rule

single-order trip capacity

vehicle time budget

If ANY direct insertion is feasible:

direct_insert_possible = true

This is a critical diagnostic.

==================================================
DIRECT INSERTION CONTRADICTION
==================================================

The Phase22 Level1 objective maximizes served order count.

Therefore, if a frozen deferred order can be inserted directly without
changing any other assignment and without violating any hard rule:

this contradicts the frozen Level1 optimum.

STOP.

Do NOT explain it away as policy.

Return a Phase22 optimality/integrity blocker.

==================================================
DIRECT INSERTION BLOCKER EVIDENCE
==================================================

For each attempted insertion path record blockers:

GROUP_MISMATCH_REQUIRES_NEW_TRIP

NO_FREE_TRIP_SLOT

WEIGHT_CAPACITY

VOLUME_CAPACITY

FRESH_TIME_BUDGET

STYLE_TECH_TIME_BUDGET

STATIC_COMPATIBILITY

Do not expose these internal diagnostic labels as new official reason codes.

Map supported blockers to Phase21 reason codes.

==================================================
RESOURCE SCARCITY EVIDENCE
==================================================

Specialized scarcity codes require evidence.

SCARCE_REEFER_VAN_CAPACITY:

target is chilled AND van_only

AND compatible vehicles are constrained to reefer vans

AND counterfactual/direct-insertion evidence shows this specialized set is
actually involved in the tradeoff.

SCARCE_REEFER_CAPACITY:

target is chilled

AND legal compatible vehicles require reefer capability

AND evidence shows reefer availability/use is involved in the tradeoff.

Do not label every chilled deferral:
SCARCE_REEFER_CAPACITY

just because chilled requires reefer.

Requirement alone is not bottleneck evidence.

==================================================
DT-353 — FORCE DEFERRED ORDER IN COUNTERFACTUAL SOLVE
==================================================

For every frozen deferred order:

rebuild the exact Phase22 hard-constraint model from approved components.

Add:

serve[target_order] == 1

Do NOT alter any other official hard rule.

Do NOT alter Phase21 policy.

Do NOT write this counterfactual into canonical allocation paths.

==================================================
COUNTERFACTUAL PRECHECK
==================================================

First run a forced-target feasibility solve.

For individually infeasible target:

expected:
INFEASIBLE

If individual evaluator says impossible but forced solver says feasible:
STOP.

For individually feasible target:

expected:
FEASIBLE / OPTIMAL feasibility smoke

If individually feasible but forced hard model is INFEASIBLE:

STOP.

Because all other orders are allowed to defer, an individually feasible
target should be hard-feasible by itself.

This indicates a model/evaluator inconsistency.

==================================================
FORCED LEXICOGRAPHIC SOLVE
==================================================

If target is hard-feasible:

run the EXACT frozen Phase21 lexicographic sequence under:

serve[target] == 1

Required objective order:

1 MAX served_order_count

2 MAX served_previous_deferred_count

3 MAX served_waiting_days_sum

4 MAX served_low_flexibility_count

5 MAX served_fresh_chilled_count

6 MAX served_fresh_count

7A MIN avoidable_reefer_van_assignment_count

7B MIN avoidable_reefer_assignment_count

7C MIN avoidable_van_assignment_count

Every stage must be:

OPTIMAL

before making a strong counterfactual explanation.

FEASIBLE-only / UNKNOWN:
UNRESOLVED

Phase26 cannot publish strong reason text for that order.

==================================================
BASELINE OBJECTIVE VECTOR
==================================================

Load the frozen baseline Phase22 objective vector from validated evidence.

Also recompute it from the frozen allocation using canonical Phase21 metric
helpers where possible.

Require exact agreement.

If mismatch:
STOP.

==================================================
DIRECTION-AWARE OBJECTIVE VECTOR COMPARISON
==================================================

Implement a canonical comparison that understands:

MAX levels 1–6

MIN levels 7A–7C

For forced target vector versus frozen baseline vector, exactly one should
hold:

WORSE

EQUAL

BETTER

Because forcing a target shrinks the feasible set, a correctly frozen
lexicographic optimum means:

forced vector must never be BETTER than baseline.

If BETTER:
STOP.

That is a Phase22 optimality/evidence contradiction.

==================================================
DT-354 — MEASURE WHAT MUST CHANGE TO SERVE IT
==================================================

After obtaining the best forced-target policy vector:

fix every forced-target objective level to its optimum.

Then add a DIAGNOSTIC objective:

minimize the number of allocation rows changed from the frozen solution.

This objective is NOT part of Phase21 policy.

It is used only to find the closest witness counterfactual among solutions
that are already equally optimal within the forced-target world.

==================================================
CHANGE METRIC
==================================================

For each order compare frozen assignment state:

decision

vehicle_id

trip_id

to counterfactual state.

Recommended binary changed[o]:

If frozen target/order is deferred:

changed[o] = serve[o]

For a frozen served order assigned to (v0,t0):

changed[o] = 1 - x[o,v0,t0]

This means unchanged only if it remains served on the exact same assignment.

Minimize:

sum changed[o]

Require this diagnostic minimization to be:

OPTIMAL

before using phrases such as:

"minimum changes required"

If only FEASIBLE:

say:

"a counterfactual was found with X changes"

not:

"at least/minimum X changes"

==================================================
COUNTERFACTUAL DELTA OUTPUT
==================================================

Measure privately:

changed_order_count

served_to_deferred_count

deferred_to_served_count

served_reassigned_count

affected_vehicle_count

affected_trip_count

baseline objective vector

forced objective vector

direction-aware objective deltas

first degraded policy tier

baseline vs forced resource utilization for affected vehicles

Do not expose changed order_refs in public/demo assets.

==================================================
FIRST DEGRADED POLICY TIER
==================================================

For a WORSE forced vector, identify the FIRST lexicographic level where the
forced vector is worse.

Examples:

LEVEL 1:
total coverage would be lower

LEVEL 2:
same coverage, fewer previously-deferred orders served

LEVEL 3:
same earlier tiers, lower waiting-days served

LEVEL 4:
same earlier tiers, fewer low-flexibility orders served

LEVEL 5:
same earlier tiers, fewer Fresh chilled orders served

LEVEL 6:
same earlier tiers, fewer Fresh orders served

LEVEL 7A/B/C:
same service/fairness tiers but worse specialized-resource stewardship

This is the strongest policy-grounded explanation of why the frozen solution
preferred another allocation.

==================================================
DT-355 — CLASSIFY UNAVOIDABLE VS POLICY TRADEOFF
==================================================

Classification rules:

A. UNAVOIDABLE_HARD

Use only when no hard-feasible allocation can serve the target.

Evidence:

individual infeasibility
+
forced-target hard solve INFEASIBLE

Typical code:

HARD_NO_COMPATIBLE_VEHICLE

or hard time-budget reason when proven.

B. POLICY_TRADEOFF

Use when:

target forced served is hard-feasible

AND

forced lexicographic objective vector is WORSE than frozen baseline.

Primary:

LOWER_POLICY_PRIORITY

Secondary:

solver-grounded physical resource reasons.

C. ALTERNATIVE_OPTIMUM

Use when:

target forced served is hard-feasible

AND

forced objective vector == frozen baseline.

Primary:

ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN

Meaning:

there exists an equally policy-optimal allocation that serves this target,
but the frozen solution selected a different equivalent optimum.

Do not call it unavoidable.

==================================================
NO FALSE UNAVOIDABLE CLAIM
==================================================

A deferred order is NOT automatically unavoidable.

"Deferred" means only that the frozen chosen allocation did not serve it.

The reasoner must prove hard infeasibility before using:

unavoidable

cannot be served

no feasible allocation can serve it

==================================================
NO FALSE POLICY CLAIM
==================================================

Do not call a hard-infeasible order:

lower priority

The solver did not prefer another order over it.

It simply could not legally serve it under hard constraints.

==================================================
DT-356 — HUMAN-READABLE EXPLANATION
==================================================

Use deterministic template-driven text.

Do not call an external LLM with private rows.

Generate explanation from reason/evidence objects.

Every explanation should answer:

1. Is the order hard-unavoidable, a policy tradeoff, or an equivalent optimum?

2. What official constraint/resource evidence matters?

3. What did the forced counterfactual prove?

4. If feasible, what policy tier changes first?

5. What minimum allocation change was required, if proven?

6. What is NOT being claimed?

==================================================
HUMAN EXPLANATION — HARD TEMPLATE
==================================================

Example structure:

"This order was deferred because no available vehicle can legally carry the
whole order under the Task 2B hard constraints. The counterfactual model was
infeasible when this order was forced to be served, so the deferral is
classified as hard-unavoidable under the frozen scenario."

Only use this when proven.

==================================================
HUMAN EXPLANATION — POLICY TRADEOFF TEMPLATE
==================================================

Example structure:

"This order is feasible in isolation, but it cannot be added to the frozen
plan without changing other assignments. When forced served, the best legal
counterfactual first worsens WayLoom's policy at [tier]. The closest
counterfactual requires [verified aggregate change]. The frozen allocation
therefore keeps the higher-ranked policy outcome."

Add physical evidence only when supported:

capacity

reefer/reefer-van scarcity

trip slots

Fresh time

Style+Tech time

==================================================
HUMAN EXPLANATION — ALTERNATIVE OPTIMUM TEMPLATE
==================================================

Example:

"This order can be served in an alternative allocation with the same frozen
WayLoom policy objective vector. Serving it requires [verified change count]
allocation changes. The current frozen allocation is therefore one of
multiple policy-equivalent feasible solutions, rather than evidence that the
order was hard-impossible."

==================================================
COUNTERFACTUAL LANGUAGE CAUTION
==================================================

These are solver counterfactuals under the frozen scenario assumptions.

Do NOT write:

"This is what would definitely happen in real operations."

Preferred:

"Under the Task 2B constraints and frozen WayLoom policy..."

"The solver counterfactual shows..."

"This identifies an optimization tradeoff, not a real-world causal effect."

==================================================
DT-357 — SELECT 1–2 STRONG DEMO EXAMPLES
==================================================

Select at most:

2

demo examples.

Selection must be deterministic and evidence-quality driven.

Prefer complementary examples.

Recommended target set:

Example A:
UNAVOIDABLE_HARD
if one exists with clean evidence.

Example B:
POLICY_TRADEOFF
with clear first degraded tier and resource evidence.

If no hard-unavoidable example exists:

choose:
one policy tradeoff
+
one alternative optimum

or two distinct well-supported policy tradeoffs.

==================================================
DEMO EXAMPLE QUALITY SCORE
==================================================

Do not select examples simply because they have dramatic IDs or large values.

Rank explanation quality using criteria such as:

counterfactual status fully OPTIMAL

reason classification complete

clear primary reason

clear resource evidence

small/easy-to-explain minimal change set

different reason class/code from first example

no ambiguous/unresolved evidence

Tie break:

stable original order position

Keep identifiers private.

==================================================
DEMO ANONYMIZATION
==================================================

Public/demo labels:

DEFERRAL_EXAMPLE_A

DEFERRAL_EXAMPLE_B

Do not expose real:

order_ref

vehicle_id

outlet_id

unless explicitly necessary and authorized.

A demo example may safely state limited contextual information such as:

brand

district

temperature requirement

van-only requirement

compatible vehicle count

first degraded policy tier

aggregate number of changes

only when appropriate for competition use.

==================================================
CONFIG
==================================================

Create:

configs/task2b_deferral_reasoner.yaml

Recommended shape:

version: 1

reason_codes:
  source: phase21

counterfactual:
  force_target_served: true
  require_optimal_policy_stages: true
  random_seed: 42
  num_search_workers: 1
  max_time_seconds_per_stage: 120

minimal_change:
  enabled: true
  require_optimal: true

direct_insertion:
  enabled: true
  fail_if_direct_insert_possible: true

classification:
  allow_multiple_secondary_reasons: true
  allow_unresolved: false

demo:
  max_examples: 2
  anonymize_identifiers: true
  deterministic: true

frozen:
  require_phase22_hash_match: true
  require_phase23_pass: true
  require_phase24_pass: true

Never change the frozen Phase21 objective order.

==================================================
COUNTERFACTUAL SOLVER SAFETY
==================================================

Reuse the approved Phase22 solver formulation.

Do not duplicate hard constraints if avoidable.

Counterfactual output paths must be separate.

Do not call:

freeze_allocation()

Do not write:

data/interim/task2b_final_allocation.csv

Do not write:

outputs/submission_task2b.csv

Do not overwrite Phase22 run/evidence.

Use diagnostic mode only.

==================================================
RUN MANIFEST
==================================================

Record:

phase = 26

Phase22 frozen allocation SHA256

Phase22 trip summary SHA256

Phase21 priority config SHA256

Phase22 optimizer config SHA256

counterfactual config SHA256

deferred order count

counterfactuals attempted

counterfactuals resolved

counterfactuals unresolved

reason-class counts

reason-code counts

solver version

random seed

workers

git commit

No row IDs in the aggregate manifest.

==================================================
TESTS — TAXONOMY
==================================================

Test:

all required Phase21 reason codes exist

codes unique

definitions nonempty

evidence requirements defined

class/code compatibility validated

unknown code rejected

no silent rename

==================================================
TESTS — INDIVIDUAL FEASIBILITY
==================================================

Synthetic:

zero compatible vehicles
→ UNAVOIDABLE_HARD

one dry vehicle + chilled order
→ no static compatibility

van_only + truck only
→ no compatibility

whole order exceeds capacity
→ no compatibility

one compatible vehicle
→ individually feasible if single-order time fits

Fresh single-order time = 270
→ feasible

Fresh = 271
→ individually infeasible

Style/Tech = 480
→ feasible

Style/Tech = 481
→ individually infeasible

==================================================
TESTS — DIRECT INSERTION
==================================================

Synthetic:

same group + spare capacity + spare time
→ direct insert possible

same group + overweight
→ WEIGHT blocker

same group + over-volume
→ VOLUME blocker

same group + Fresh time over
→ Fresh budget blocker

same group + Style/Tech over
→ 480 blocker

different group + unused trip slot
→ new trip considered

different group + two trips already used
→ trip-slot blocker

direct insertion feasible for frozen deferred order
→ Phase22 contradiction / hard fail

==================================================
TESTS — COUNTERFACTUAL SOLVE
==================================================

Synthetic:

hard-infeasible target forced served
→ INFEASIBLE

individually feasible target
→ forced hard solve feasible

forced vector BETTER than baseline
→ contradiction / hard fail

forced vector EQUAL
→ ALTERNATIVE_OPTIMUM

forced vector WORSE
→ POLICY_TRADEOFF

all 9 stages must be OPTIMAL

FEASIBLE-only stage
→ unresolved / Phase26 fail

==================================================
TESTS — DIRECTION-AWARE VECTOR
==================================================

Test:

MAX tier higher is better

MIN tier lower is better

first degraded tier correct

equal vector exact

Level7A/B/C direction handled correctly

No naive tuple comparison.

==================================================
TESTS — MINIMAL CHANGE
==================================================

Test:

frozen deferred target forced served

changed metric correct

served retained same v/t = unchanged

served moved vehicle = changed

served moved trip = changed

served becomes deferred = changed

target deferred→served = changed

minimal-change objective solved only after forced policy vector fixed

OPTIMAL required for "minimum" wording

==================================================
TESTS — CLASSIFICATION
==================================================

hard infeasible
→ UNAVOIDABLE_HARD

forced feasible + worse vector
→ POLICY_TRADEOFF

forced feasible + equal vector
→ ALTERNATIVE_OPTIMUM

hard-infeasible never labelled lower priority

policy tradeoff never labelled hard unavoidable

equivalent optimum never labelled unavoidable

==================================================
TESTS — RESOURCE REASONS
==================================================

SCARCE_REEFER_CAPACITY only with actual evidence

SCARCE_REEFER_VAN only with chilled+van_only + evidence

CAPACITY_COMPETITION only when capacity blocks relevant insertion/tradeoff

TRIP_SLOT_LIMIT only with actual slot pressure

FRESH_TIME_BUDGET only with Fresh evidence

STYLE_TECH_TIME_BUDGET only with Style/Tech evidence

Multiple secondary reasons allowed

Do not overclaim sole cause.

==================================================
TESTS — HUMAN TEXT
==================================================

Test deterministic templates.

Require:

reason class stated accurately

counterfactual language

policy tier if tradeoff

resource reason only when evidence

no "AI decided"

no unsupported "unavoidable"

no real order_ref in public text

no row dump

no monetary claim

no real-world causal guarantee

==================================================
TESTS — DEMO SELECTION
==================================================

At most 2 examples.

Deterministic.

Prefer classification diversity.

Reject unresolved example.

Anonymize labels.

No real IDs in sanitized output.

Stable tie break.

==================================================
FROZEN HASH TEST
==================================================

Before local real reasoner run, hash:

data/interim/task2b_final_allocation.csv

data/interim/task2b_final_trip_summary.csv

outputs/submission_task2b.csv

docs/task2b_policy.md

After reasoner generation:

require all hashes unchanged.

==================================================
LOCAL HUMAN COMMAND
==================================================

Implement but do not execute private real counterfactuals in external-agent
context.

Expected command shape:

python scripts/build_task2b_deferral_reasoner.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --compatibility-config configs/task2b_compatibility.yaml \
  --trip-time-config configs/task2b_trip_time.yaml \
  --priority-config configs/task2b_priority.yaml \
  --optimizer-config configs/task2b_optimizer.yaml \
  --reasoner-config configs/task2b_deferral_reasoner.yaml \
  --compatibility-matrix data/interim/task2b_compatibility_matrix.csv \
  --priority-metadata data/interim/task2b_priority_metadata.csv \
  --allocation data/interim/task2b_final_allocation.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --submission outputs/submission_task2b.csv \
  --report-dir reports/private/phase26_task2b_deferral_reasoner

Use the actual repository CLI if it differs.

Then validate:

python scripts/validate_task2b_deferral_reasoner.py \
  --reasoner-config configs/task2b_deferral_reasoner.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --submission outputs/submission_task2b.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --report-dir reports/private/phase26_task2b_deferral_reasoner

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_task2b_reason_codes.py \
  tests/test_task2b_individual_feasibility.py \
  tests/test_task2b_direct_insertion.py \
  tests/test_task2b_counterfactual_reasoner.py \
  tests/test_task2b_counterfactual_delta.py \
  tests/test_task2b_deferral_explanations.py \
  tests/test_task2b_demo_example_selector.py

Then relevant Phase19–24 Task2B tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run private real counterfactuals in Codex.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase22 not frozen

Phase23 not PASS

Phase24 not PASS

frozen allocation hash mismatch

priority config hash mismatch

baseline objective vector mismatch

direct insertion exists for frozen deferred order

individual evaluator and forced hard solve disagree

forced vector better than baseline

counterfactual stage not OPTIMAL

minimal-change solve not OPTIMAL when claiming minimum changes

reason unresolved

reasoner requires changing hard rules

reasoner changes Phase21 objective order

reasoner writes canonical allocation

reasoner changes final submission

reasoner changes Task2B policy

reasoner changes Phase22/23 evidence

reason code lacks solver evidence

hard-infeasible order labelled lower priority

feasible policy tradeoff labelled hard-unavoidable

alternative optimum labelled unavoidable

demo example unresolved

public example exposes private IDs

external LLM/API required for private explanation generation

Phase27 work introduced

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-350 READY
DT-351 READY
DT-352 READY
DT-353 READY
DT-354 READY
DT-355 READY
DT-356 READY
DT-357 READY

taxonomy exact

individual feasibility exact

direct insertion analysis exact

forced solve exact Phase22 hard rules

forced objective exact Phase21 policy

baseline objective vector matches frozen evidence

vector comparison direction-aware

no better-than-baseline contradiction

minimum-change witness exact

unavoidable proof strict

policy tradeoff proof strict

alternative optimum proof strict

resource codes evidence-grounded

human text deterministic

demo examples anonymized

all frozen hashes unchanged

no Phase27 implementation

==================================================
RETURN ONLY
==================================================

PHASE:
26 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-350 READY / FAIL
DT-351 READY / FAIL
DT-352 READY / FAIL
DT-353 READY / FAIL
DT-354 READY / FAIL
DT-355 READY / FAIL
DT-356 READY / FAIL
DT-357 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

REASON TAXONOMY:
PASS / FAIL

INDIVIDUAL INFEASIBILITY:
PASS / FAIL

DIRECT INSERTION ANALYSIS:
PASS / FAIL

COUNTERFACTUAL FORCE-SERVE:
PASS / FAIL

POLICY VECTOR COMPARISON:
PASS / FAIL

MINIMAL-CHANGE COUNTERFACTUAL:
PASS / FAIL

UNAVOIDABLE VS POLICY CLASSIFICATION:
PASS / FAIL

HUMAN-READABLE EXPLANATION:
PASS / FAIL

DEMO EXAMPLE SELECTOR:
PASS / FAIL

PHASE22 FROZEN ALLOCATION CHANGED:
MUST BE NO

PHASE24 FINAL SUBMISSION CHANGED:
MUST BE NO

PHASE24 POLICY CHANGED:
MUST BE NO

PRIVATE REAL DATA ACCESSED:
NO

EXTERNAL API USED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local reasoner command
2. exact local reasoner validation command

PHASE 26 STATUS:
AWAITING LOCAL COUNTERFACTUAL RUN

READY FOR PHASE 27:
NO

Then STOP.

Do not start Phase27.

```

---

# 112. Independent Phase 26 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 26.

PHASE:
Hero Feature — Explainable Deferral Reasoner

TASK RANGE:
DT-350 through DT-357

Do NOT implement Phase27.
Do NOT modify code initially.
Do NOT run private real counterfactuals.
Do NOT inspect private row-level reason tables.
Do NOT change frozen Task2B artifacts.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase26
4. PHASE_19_COMPETITION_CONTRACT.md
5. PHASE_20_COMPETITION_CONTRACT.md
6. PHASE_21_COMPETITION_CONTRACT.md
7. PHASE_22_COMPETITION_CONTRACT.md
8. PHASE_23_COMPETITION_CONTRACT.md
9. PHASE_24_COMPETITION_CONTRACT.md
10. PHASE_26_COMPETITION_CONTRACT.md

Inspect:

11. src/task2b/reason_codes.py
12. src/task2b/individual_feasibility.py
13. src/task2b/direct_insertion.py
14. src/task2b/counterfactual_reasoner.py
15. src/task2b/counterfactual_delta.py
16. src/task2b/deferral_explanations.py
17. src/task2b/demo_example_selector.py

18. scripts/build_task2b_deferral_reasoner.py
19. scripts/validate_task2b_deferral_reasoner.py

20. configs/task2b_deferral_reasoner.yaml
21. configs/task2b_priority.yaml
22. configs/task2b_optimizer.yaml

23. docs/task2b_deferral_reasoner_spec.md
24. docs/task2b_deferral_reasoner.md where safe

25. tests/test_task2b_reason_codes.py
26. tests/test_task2b_individual_feasibility.py
27. tests/test_task2b_direct_insertion.py
28. tests/test_task2b_counterfactual_reasoner.py
29. tests/test_task2b_counterfactual_delta.py
30. tests/test_task2b_deferral_explanations.py
31. tests/test_task2b_demo_example_selector.py

Also inspect relevant Phase19–24 implementation/tests.

HUMAN SANITIZED LOCAL RESULT:

FROZEN ALLOCATION HASH: <PASS/FAIL>
FINAL SUBMISSION HASH: <PASS/FAIL>
PHASE24 POLICY HASH: <PASS/FAIL>

DEFERRED ORDERS COVERED: <count>/<count>
UNRESOLVED REASONS: <0 or other>

INDIVIDUAL FEASIBILITY: <PASS/FAIL>
DIRECT INSERTION CONTRADICTIONS: <0 or other>

COUNTERFACTUAL FORCE-SERVE: <PASS/FAIL>
ALL REQUIRED COUNTERFACTUAL POLICY STAGES OPTIMAL: <PASS/FAIL>

BASELINE OBJECTIVE VECTOR: <PASS/FAIL>
BETTER-THAN-BASELINE CONTRADICTIONS: <0 or other>

MINIMAL-CHANGE SOLVES: <PASS/FAIL>

UNAVOIDABLE_HARD COUNT: <aggregate>
POLICY_TRADEOFF COUNT: <aggregate>
ALTERNATIVE_OPTIMUM COUNT: <aggregate>

REASON CONSISTENCY AUDIT: <PASS/FAIL>
DEMO EXAMPLES: <count>
DEMO IDS ANONYMIZED: <PASS/FAIL>

Do not ask for real order_ref values.

==================================================
AUDIT TASKS
==================================================

DT-350:
taxonomy matches Phase21 stable vocabulary.

DT-351:
individual infeasibility is strict and hard-rule grounded.

DT-352:
shared resource reasons require evidence; direct-insert contradiction blocks.

DT-353:
force-serve uses exact Phase22 hard model and exact Phase21 objective.

DT-354:
change measurement fixes forced policy optimum first and then minimizes
allocation changes.

DT-355:
hard-unavoidable vs policy tradeoff vs alternative optimum classifications
are logically correct.

DT-356:
human text is deterministic, accurate, anonymized and noncausal.

DT-357:
1–2 demo examples are deterministic, strong, complementary and anonymized.

==================================================
CRITICAL LOGIC AUDIT
==================================================

Verify:

If compatible_vehicle_count == 0:
hard-unavoidable is valid.

If individually feasible:
forced hard solve must be feasible because all other orders can defer.

A mismatch blocks.

A direct insertion into the frozen allocation with no other changes:
blocks because Phase22 Level1 should have served one more order.

Baseline frozen objective vector must match recomputed Phase21 metrics.

Forced feasible set is a subset of baseline feasible set.

Therefore forced objective vector:
may be WORSE or EQUAL,
must never be BETTER.

BETTER blocks Phase22 integrity.

==================================================
POLICY VECTOR AUDIT
==================================================

Exact direction order:

1 MAX served
2 MAX previous-deferred served
3 MAX waiting-days served
4 MAX low-flexibility served
5 MAX Fresh chilled served
6 MAX Fresh served
7A MIN avoidable reefer-van
7B MIN avoidable reefer
7C MIN avoidable van

Verify direction-aware comparison.

No naive tuple comparison.

==================================================
MINIMAL-CHANGE AUDIT
==================================================

Verify diagnostic minimization occurs ONLY after all forced-target policy
objectives are fixed.

It must not become a hidden Phase21 objective.

Verify changed-state semantics:

deferred→served = changed

served→deferred = changed

served same vehicle+trip = unchanged

served moved vehicle/trip = changed

"minimum changes" wording only when diagnostic solve OPTIMAL.

==================================================
CLASSIFICATION AUDIT
==================================================

UNAVOIDABLE_HARD:

requires hard infeasibility proof.

POLICY_TRADEOFF:

requires forced hard-feasible + objective vector WORSE.

ALTERNATIVE_OPTIMUM:

requires forced hard-feasible + objective vector EQUAL.

Hard infeasible must not be described as lower priority.

Policy tradeoff must not be described as hard impossible.

Alternative optimum must not be described as unavoidable.

==================================================
RESOURCE-REASON AUDIT
==================================================

Verify:

reefer scarcity not assigned merely because target is chilled.

reefer-van scarcity not assigned without chilled+van_only and actual evidence.

capacity competition requires actual capacity blocker evidence.

trip-slot requires actual two-trip pressure.

Fresh time requires 270-budget evidence.

Style/Tech time requires 480-budget evidence.

Multiple secondary reasons are allowed.

Avoid unsupported sole-cause claims.

==================================================
OFFICIAL SCOPE AUDIT
==================================================

Verify docs clearly state:

reasoner is WayLoom engineering hero feature

official checker proves feasibility, not optimality

official challenge asks teams to explain deferrals/reasoning

counterfactual reasoner does not change official feasibility rules

==================================================
FROZEN ARTIFACT AUDIT
==================================================

Using sanitized evidence:

Phase22 allocation unchanged.

Phase22 trip summary unchanged.

Phase24 final submission unchanged.

Phase24 policy unchanged.

Phase22/23 evidence unchanged.

No canonical counterfactual allocation written.

==================================================
PRIVACY AUDIT
==================================================

Public/demo outputs must not expose:

order_ref

outlet_id

vehicle_id

changed-order lists

raw counterfactual allocations

unless explicitly authorized.

Demo examples should use:

DEFERRAL_EXAMPLE_A
DEFERRAL_EXAMPLE_B

Detailed evidence remains private.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_task2b_reason_codes.py \
  tests/test_task2b_individual_feasibility.py \
  tests/test_task2b_direct_insertion.py \
  tests/test_task2b_counterfactual_reasoner.py \
  tests/test_task2b_counterfactual_delta.py \
  tests/test_task2b_deferral_explanations.py \
  tests/test_task2b_demo_example_selector.py

Then relevant Phase19–24 Task2B tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run private real counterfactuals.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

REASON TAXONOMY:
PASS / FAIL

INDIVIDUAL FEASIBILITY:
PASS / FAIL

DIRECT INSERTION INTEGRITY:
PASS / FAIL

COUNTERFACTUAL HARD MODEL PARITY:
PASS / FAIL

COUNTERFACTUAL POLICY PARITY:
PASS / FAIL

OBJECTIVE VECTOR COMPARISON:
PASS / FAIL

BETTER-THAN-BASELINE GUARD:
PASS / FAIL

MINIMAL-CHANGE FAITHFULNESS:
PASS / FAIL

UNAVOIDABLE CLASSIFICATION:
PASS / FAIL

POLICY-TRADEOFF CLASSIFICATION:
PASS / FAIL

ALTERNATIVE-OPTIMUM CLASSIFICATION:
PASS / FAIL

RESOURCE-REASON EVIDENCE:
PASS / FAIL

HUMAN EXPLANATION QUALITY:
PASS / FAIL

DEMO EXAMPLE QUALITY:
PASS / FAIL

PRIVACY:
PASS / FAIL

FROZEN ARTIFACTS:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
None / exact blockers

NON-BLOCKING IMPROVEMENTS:
...

DT-350: PASS/FAIL
DT-351: PASS/FAIL
DT-352: PASS/FAIL
DT-353: PASS/FAIL
DT-354: PASS/FAIL
DT-355: PASS/FAIL
DT-356: PASS/FAIL
DT-357: PASS/FAIL

PHASE 26 INDEPENDENT REVIEW:
PASS / FAIL

EXPLAINABLE DEFERRAL REASONER:
COMPLETE / INCOMPLETE

FROZEN TASK2B ALLOCATION:
UNCHANGED / CHANGED

READY FOR PHASE 27:
YES / NO

If PASS:

PHASE 26 INDEPENDENT REVIEW: PASS
EXPLAINABLE DEFERRAL REASONER: COMPLETE
FROZEN TASK2B ALLOCATION: UNCHANGED
BLOCKERS: None
READY FOR PHASE 27: YES

Then STOP.

Do not start Phase27.

```

---

# 113. Completion record

```markdown
# Phase 26 Completion Record

## Tasks

- [ ] DT-350
- [ ] DT-351
- [ ] DT-352
- [ ] DT-353
- [ ] DT-354
- [ ] DT-355
- [ ] DT-356
- [ ] DT-357

## Integrity

- [ ] Phase22 frozen hash PASS
- [ ] Phase23 PASS
- [ ] Phase24 PASS
- [ ] baseline objective vector PASS
- [ ] direct-insertion contradictions = 0
- [ ] forced vector better-than-baseline contradictions = 0

## Reasons

- [ ] taxonomy PASS
- [ ] all deferred orders covered
- [ ] hard-unavoidable proof strict
- [ ] policy-tradeoff proof strict
- [ ] alternative-optimum proof strict
- [ ] unresolved = 0
- [ ] resource evidence grounded

## Counterfactuals

- [ ] all required policy stages OPTIMAL
- [ ] minimum-change solve OPTIMAL
- [ ] all change metrics generated
- [ ] no canonical counterfactual output written

## Demo

- [ ] 0–2 strong examples selected
- [ ] deterministic
- [ ] anonymized
- [ ] no private IDs

## Frozen outputs

- allocation changed: NO
- trip summary changed: NO
- submission_task2b.csv changed: NO
- task2b_policy.md changed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 26 STATUS: PASS / FAIL
EXPLAINABLE DEFERRAL REASONER: COMPLETE / INCOMPLETE
FROZEN TASK2B ALLOCATION: UNCHANGED / CHANGED
READY FOR PHASE 27: YES / NO
```

---

# 114. Final checklist

Before Phase 27:

- [ ] exact DT-350–DT-357 coverage.
- [ ] no frozen Task 2B artifact changed.
- [ ] reason taxonomy matches Phase 21.
- [ ] every deferred order classified.
- [ ] no unresolved counterfactual.
- [ ] zero direct-insertion contradictions.
- [ ] zero better-than-baseline forced vectors.
- [ ] individual feasibility matches forced hard feasibility.
- [ ] exact Phase 22 constraints reused.
- [ ] exact Phase 21 policy reused.
- [ ] every forced objective stage OPTIMAL.
- [ ] minimal-change counterfactual OPTIMAL.
- [ ] hard-unavoidable claims proven.
- [ ] policy-tradeoff claims proven.
- [ ] alternative-optimum claims proven.
- [ ] physical resource codes supported.
- [ ] explanations deterministic.
- [ ] explanations do not overclaim causality.
- [ ] demo examples anonymized.
- [ ] safe tests pass.
- [ ] full suite passes.
- [ ] independent review passes.

Only then:

```text
PHASE 26 STATUS: PASS
EXPLAINABLE DEFERRAL REASONER: COMPLETE
FROZEN TASK 2B ALLOCATION: UNCHANGED
READY FOR PHASE 27: YES
```
