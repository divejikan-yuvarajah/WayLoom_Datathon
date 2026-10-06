# Task 2B Explainable Deferral Reasoner — Technical Specification

## Scope

Phase 26 is a read-only diagnostic layer over the frozen Phase 22 allocation. It reuses the approved Phase 19 compatibility rules, Phase 20 trip-time formula, Phase 21 nine-tier policy and Phase 22 CP-SAT model. It never calls the allocation freeze workflow and never writes to canonical allocation, submission, policy or prior-phase evidence paths.

The feature is a WayLoom engineering enhancement. It is not an organizer-mandated component, and the official checker proves feasibility rather than optimality.

## Evidence sequence

For each frozen deferred order, the local reasoner performs these checks in order:

1. Recheck static whole-order compatibility and exact one-order trip time.
2. Test insertion into same-group frozen trips and creation of a legal unused trip.
3. Stop if direct insertion is possible, because that would contradict the frozen maximum-coverage objective.
4. Force the target served in a fresh instance of the approved Phase 22 model.
5. Require hard feasibility to agree with the individual evaluator.
6. For hard-feasible targets, prove all nine Phase 21 objective stages optimal.
7. Compare the forced and frozen objective vectors with MAX direction for levels 1–6 and MIN direction for 7A–7C.
8. Stop if the forced vector is better than the frozen vector.
9. Fix all forced policy optima and minimize exact allocation-row changes as a diagnostic objective.
10. Independently audit the extracted witness allocation before producing an explanation.

## Classification

- `UNAVOIDABLE_HARD` requires individual infeasibility and an infeasible forced-target hard model.
- `POLICY_TRADEOFF` requires hard feasibility and a worse optimal forced policy vector.
- `ALTERNATIVE_OPTIMUM` requires hard feasibility and an equal optimal forced policy vector.

Physical reason codes are secondary unless they directly establish hard infeasibility. Capacity, trip-slot, time-budget and specialized-vehicle labels are emitted only from recorded insertion/counterfactual evidence. Several secondary reasons may coexist.

## Minimal-change witness

For a frozen deferred order, serving it counts as a changed row. A frozen served order remains unchanged only when it stays served on the same vehicle and trip. Moving vehicle, moving trip or becoming deferred counts as changed. “Minimum” wording is allowed only after CP-SAT proves this diagnostic objective optimal with every forced policy tier fixed.

## Privacy and language

Detailed rows and counterfactual assignments stay under `reports/private/phase26_task2b_deferral_reasoner/`. Sanitized examples use `DEFERRAL_EXAMPLE_A/B` and omit order, vehicle, outlet and trip identifiers. Text is template-driven and local; no external LLM or API receives competition data.

Every explanation is explicitly limited to a solver counterfactual under the frozen scenario. It does not claim a real-world causal guarantee or imply that the organizer checker established optimality.

## Local execution

The build command must be run by the human operator because it reads restricted competition rows and performs private counterfactual solves. The validator reads the generated private evidence but does not rerun the optimizer.

