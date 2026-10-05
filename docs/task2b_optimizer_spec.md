# Phase 22 Task 2B optimizer

This phase uses local OR-Tools CP-SAT 9.15.6755, pinned in
`requirements-lock.txt`. Its inputs are the validated Phase 18 S1 scenario,
the complete Phase 19 compatibility matrix, Phase 20 travel and service
references, and Phase 21 priority metadata. Real S1 rows stay in private
local files; agent tests use synthetic fixtures.

## Execution plan

1. Validate the S1 orders, available Peliyagoda fleet, complete matrix,
   frozen priority profile, and exact Decimal scaling before creating a model.
2. Create assignment variables only for independently verified compatible
   pairs. Enforce all seven official hard rules with integer CP-SAT constraints.
   Sort interchangeable trip groups and identical-vehicle usage to remove
   search symmetry without changing any feasible policy outcome.
3. Solve feasibility, then each of the nine Phase 21 objectives sequentially.
   Require OPTIMAL at every stage and fix its optimum before the next stage.
4. Extract one decision per `order_ref`. Independently recompute trips from
   ordinary tables with the Phase 20 calculator and exact Decimal arithmetic.
5. Repeat the stable-seed, one-worker solve and compare the objective vector,
   allocation, and audit. Write private candidate and report artifacts.
6. Freeze the audited candidate only after hashes, all OPTIMAL stage records,
   audit, determinism, and unchanged config hashes are verified.

## Hard model

For order `o`, `serve[o] + defer[o] = 1` and
`sum(x[o,v,t]) = serve[o]`. Only compatible `(o,v)` pairs have assignments.
Each used `(vehicle,trip)` selects one brand/district group, has at least one
order, and respects both weight and volume capacity. Trips are exactly 1 and
2. `use_trip[v,2] <= use_trip[v,1]` is an engineering symmetry breaker, not
an official business rule.

The integer trip-minute expression is outbound once, plus each assigned
order's handling and inter-stop rate, minus the selected group's one
inter-stop rate. Thus a trip of `n` orders has `outbound + inter*(n-1) +
handling`. Return travel is zero. Across both trips per vehicle, Fresh minutes
are at most 270 and the combined Style plus Tech minutes are at most 480.
Weight, volume, and time coefficients use separate exact decimal scales.
Unsupported precision fails before solving.

## Objective and statuses

The nine levels follow `configs/task2b_priority.yaml` exactly: served count,
previous deferrals, waiting days, low flexibility, Fresh chilled, Fresh,
avoidable reefer-van, avoidable reefer, and avoidable van use. The final three
are minimized. A specialized assignment costs one only when the order has a
compatible less-specialized alternative of the relevant type.

The initial smoke solve accepts FEASIBLE or OPTIMAL. Every objective stage
requires OPTIMAL; FEASIBLE, INFEASIBLE, MODEL_INVALID, and UNKNOWN stop the
freeze path. A FEASIBLE stage receives a solution hint and is retried with
increasing configured limits (120, 360, then 900 seconds). Exhaustion still
blocks freeze and names the stage without exposing its objective value.
Solver time, bound, branches, conflicts, and attempt statuses are recorded
privately. Solver time limits may be tuned without changing a hard rule,
objective tier, flexibility threshold, or policy signal.

## Independent audit and freeze

The audit checks all S1 order decisions, assignment fields, available fleet,
brand/district grouping, refrigeration, van access, home depot, whole order,
both capacities, exact trip time, two-trip maximum, and separate daily time
budgets. It compares the CP-SAT minute value with Phase 20 recomputation.
Audit failure blocks candidate export and freeze.

The local optimizer writes a private candidate allocation, trip summary, and
report under `data/interim` and `reports/private`. The freeze command copies
the candidate atomically to `data/interim/task2b_final_allocation.csv` and
writes `freeze_manifest.json` with artifact hashes and the complete required
solver, scenario, compatibility, trip-time, and priority configuration hashes.
Partial configuration evidence is rejected. The normal optimizer also rejects
any candidate-output path that resolves to the canonical allocation path, even
before that canonical file exists. Only the freeze command may create it. A
subsequent normal optimizer or freeze run refuses to overwrite the canonical
allocation. Phase 22 does not create `outputs/submission_task2b.csv`.

An explicit `--controlled-reopen-freeze-evidence` freeze mode may regenerate
an incomplete freeze manifest from the original validated run evidence. It
requires the separate candidate to hash-identically to the existing canonical
allocation, validates all five configuration hashes and all freeze gates, and
never writes the allocation or trip-summary files. Normal freeze mode retains
strict overwrite refusal.
