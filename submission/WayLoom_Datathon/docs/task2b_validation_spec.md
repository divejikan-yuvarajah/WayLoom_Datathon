# Phase 23 Task 2B allocation validation specification

## Scope and safety boundary

Phase 23 independently validates the frozen Phase 22 Task 2B allocation. It does
not run the optimizer, change the allocation or its freeze manifest, publish a
submission, or start Phase 24. Repository tests use synthetic data only. The two
commands below are intended for a human to run locally where the private source
files are available.

The validation command verifies the Phase 22 freeze state and hashes before it
loads any allocation rows. All row-level reports and checker streams are written
under `reports/private/phase23_task2b_validator/`; console output contains only
sanitized statuses and aggregate counts.

## Independent validator contract

The validator requires these frozen-allocation columns as a minimum subset:

`scenario, order_ref, outlet_id, decision, vehicle_id, trip_id`

Harmless internal diagnostic columns are allowed but are never used as
authoritative official facts. The private checker candidate always contains
exactly the six official columns above.

It independently checks:

1. the scenario is exactly `S1`, every source `order_ref` appears exactly once,
   no unknown order appears, and `outlet_id` matches its canonical source value;
2. `decision` is either `served` or `deferred`;
3. served rows have a known vehicle and trip `1` or `2`, while deferred rows
   have blank vehicle and trip fields;
4. every served order is compatible with its assigned vehicle;
5. each `vehicle_id + trip_id` contains a single brand and a single district;
6. trip weight and volume do not exceed the vehicle capacities;
7. each vehicle uses at most two trips;
8. each trip time is recomputed from canonical travel and service inputs using
   the Phase 20 formula, without a return-to-depot leg; and
9. aggregate vehicle time is at most 270 minutes for Fresh and at most 480
   minutes for Style plus Tech.

The frozen Phase 22 trip summary is hash-verified before it is read. Its exact
vehicle/trip key set and stored `trip_minutes` are then compared with the
independent recomputation; a missing, duplicate, invalid, extra, or mismatched
summary entry fails the trip-time rule.

Dock type is not a trip-grouping rule; it is used only to look up each order's
service allowance. Many orders may share one `vehicle_id + trip_id`, and the
same trip ID may be used by different vehicles. Trip IDs are not globally
unique. No `trip 2 implies trip 1` rule is imposed. Repeated `outlet_id` values
across different orders are valid. Numeric comparisons use decimal parsing and
the configured tolerance rather than optimizer output or optimizer internals.

The validator emits private identity, decision/schema, hard-rule, trip-time,
vehicle-budget, warning, summary, and Markdown reports. A checker candidate is
created in the private report workspace only after the independent validator
passes. The canonical frozen allocation is opened read-only and its hash is
checked again after validation.

## Inspected official-checker interface

The repository's actual `DataSet/check_allocation.py` interface was inspected:

- invocation: Python script with one positional candidate CSV path;
- working directory: the checker's parent directory;
- reference data: loaded relative to the checker file from `DataSet/data`;
- success: exit code `0` and the exact marker
  `FEASIBILITY: PASSED - every rule satisfied.`;
- failure indicators: a nonzero exit code, missing success marker, `FAIL:`, or
  `FEASIBILITY: FAILED`;
- accepted candidate columns: `scenario`, `order_ref`, `decision`,
  `vehicle_id`, and `trip_id`; `outlet_id` is retained and accepted as an extra
  column.

The wrapper re-inspects the checker source before executing it and refuses to
continue if that interface differs from the declared configuration. It invokes
the checker without `--example`, captures stdout and stderr, enforces a timeout,
and confirms that the checker file hash did not change during execution.

## Immutable evidence and pass rule

Each official-checker run receives a new timestamped directory beneath
`reports/private/phase23_task2b_validator/checker_runs/`. Existing run
directories are never overwritten. Evidence includes checker and candidate
hashes, frozen allocation and Phase 22 manifest hashes, Python version, working
directory, invocation mode, exit code, timeout state, pass detection, stream
hashes, UTC timestamp, Git commit, and both validator statuses. Captured stdout
and stderr are stored separately and verified against their recorded hashes.

Phase 23 can pass only when both the independent validator and the official
checker pass against the same frozen allocation and unchanged checker candidate.

## Human-local commands

Run the independent validator first:

```powershell
.\.venv\Scripts\python.exe scripts\validate_task2b_allocation.py --raw-root data\raw --manifest configs\dataset_manifest.yaml --scenario-config configs\task2b_scenario.yaml --validation-config configs\task2b_validation.yaml --allocation data\interim\task2b_final_allocation.csv --phase22-freeze-manifest reports\private\phase22_task2b_optimizer\freeze_manifest.json --report-dir reports\private\phase23_task2b_validator
```

Only after that command reports `PASS`, run the inspected official checker:

```powershell
.\.venv\Scripts\python.exe scripts\run_official_task2b_checker.py --raw-root data\raw --manifest configs\dataset_manifest.yaml --validation-config configs\task2b_validation.yaml --allocation data\interim\task2b_final_allocation.csv --report-dir reports\private\phase23_task2b_validator
```

Do not proceed to Phase 24 until the private evidence records both
`own_validator_status: PASS` and `official_checker_status: PASS`.
