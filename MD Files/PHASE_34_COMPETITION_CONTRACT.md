# PHASE 34 — General Automated Testing: Competition Implementation Contract

> **Canonical file:** `PHASE_34_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Authoritative inventory:** `WAYLOOM_DATATHON_MASTER_PLAN.md`, Phase 34 table  
> **Task IDs:** **DT-438 through DT-450** (exactly **13**, no omissions)  
> **Master priority/mark:** **P1 / [E]** for all tasks  
> **Master dependency:** Implemented pipelines / core modules implemented  
> **Master phase gate:** Automated test suite covers critical data rules, labels, inference and allocation constraints.  
> **Status:** Implementation contract — **not evidence that Phase 34 has passed**.

## 1. Source authority and status

1. **Official** `Challenge Booklet.pdf` (and supplied templates / `check_allocation.py`, when relevant) controls the competition rules. The booklet specifies domain requirements; it **does not prescribe** the 13 pytest tasks or particular test module filenames.
2. `WAYLOOM_DATATHON_MASTER_PLAN.md` supplies **exactly** the Phase 34 task IDs, names, dependencies, priority and gate.
3. Phase 10/17/24 frozen contracts, Phase 31 notebook closure, Phase 32 artifact registry, Phase 33 submission integrity, and current production code provide implementation context. Confirm actual local path/API signatures rather than guessing them.
4. Sections labeled **Engineering enhancement** are proposed robust test coverage, **not invented organizer requirements**. Existing tests can be reused and strengthened: no unnecessary duplication or rewrites.
5. This document is a **plan**. Repository Phase 33 closure has **not been evidenced in this conversation**. Start Phase 34 implementation only after checking Phase 33 gate according to master plan; if not closed, stop and report. Do not claim passed verification without running it.

## 2. Scope and explicit non-goals

**In scope:** pytest organization, synthetic/deterministic data fixtures, unit tests of production rules, negative and metamorphic tests, fresh-process safe saved-model tests, failure-quality reports, regression safety, CI-safe default suite. Existing 765+ passing tests are a starting point, not proof every Phase 34 acceptance criterion is satisfied.

**Out of scope:** model search/retraining, tweaking prediction thresholds, changing frozen algorithms to make tests green, regenerating submissions, rewriting existing CSVs, real-data probing, importing private rows into fixtures, committing private notebooks, changing Phase 33 validations, initiating Phase 35.

**Privacy:** `data/raw/**`, `data/interim/**`, `reports/private/**`, executed private notebooks and competition record-level content are **human-local only**. Unit tests and agent-visible outputs must use synthetic fixtures; no row-level official data/prediction prints. Logs should contain only test identifiers and aggregate status.

## 3. Preconditions and the mandatory Phase 33 gate

- Open `AGENTS.md`, `CODEX_HANDOFF_PHASE_11_ONWARDS.md`, master plan, official booklet and relevant module/phase contracts.
- Verify Phase 31 is formally closed (supplied conversation: YES), Phase 32 verified, and **Phase 33** fully closed with independent review and readiness YES **in current repository**. If Phase 33 is pending, **STOP: do not start Phase 34**; provide exact follow-up.
- Run `git status --short`; distinguish pre-existing changes from Phase 34 changes; do not silently stage, revert or overwrite them.
- Verify final official CSV SHA256 hashes, model registry and registered artifacts before modifying any phase-related files, with only safe metadata/hashes (no private contents). Preserve the baseline securely under ignored reports/private if needed.
- Inspect current pytest layout first; preserve passing tests and implement minimal sufficient new coverage.
- Confirm `.venv` runtime and correct imports; no network, installation, model loading from untrusted files, or implicit training at pytest collection time.

## 4. Official domain invariants covered by this testing phase

### Task 1: labeling and inference

- Test-plan inputs contain planned time/route data, not actual outcome-time labels; forbid actual-travel and actual-unloading outcomes as prediction-time features.
- Arrival **before** delivery-window opening implies a waiting interval; **waiting is not outlet service time**. Evaluate service duration based on the canonical existing label implementation with supplied train events.
- A delivery is late **only if actual arrival is strictly after window close**; equality with closing time is not late.
- Final Task 1 prediction columns are `delivery_id,pred_service_min,pred_late_prob`; service prediction finite and plausibly nonnegative according to frozen inference contract, probability finite and `0 <= p <= 1`. Preserve identifiers and row order.

### Task 2A: history/forecast

- History comes from **both** `deliveries_train.csv` and `task1_test_inputs.csv`, **every order exactly once** including deferred or not dispatched.
- Week comes from the **store-requested order date**, using `calendar.csv` `iso_year` / `iso_week`, not dispatched/arrival date. Handle ISO week-year changes.
- Forecast outputs `row_id,pred_total_volume_m3,pred_chilled_volume_m3`. Only **Fresh** can have chilled; **Style and Tech chilled exactly 0**; nonnegative, finite; chilled <= total.

### Task 2B: hard feasibility

- Each served order belongs to exactly one vehicle+trip (no splitting). Deferred has blank vehicle/trip. Vehicle availability excludes `in_workshop`.
- Chilled requires reefer; `van_only` requires van; home depot must match order outlet depot. A single trip is one **brand and district**.
- Trip volume and weight must each respect vehicle capacities. A vehicle performs at most **two trips total**.
- **Official exact time**: `trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (number_of_orders - 1) + sum(service_allowance_min(brand,dock_type))`. No return-to-depot leg. A trip with three Gampaha Fresh stops (2 rear dock, 1 street) is **101 min**: 37 + 9×2 + 15 + 15 + 16.
- **Per-vehicle time budgets**: Fresh combined trips <= **270 min**; Style+Tech combined trips <= **480 min**; separate windows do not increase the overall two-trip cap.
- Organizer `check_allocation.py` tests official feasibility but **does not prove optimality**. Use independent synthetic validator tests and the official checker only through its actual documented interface; do not fabricate success.

### Phase 32: model loading

- Saved-model testing must use the final trusted registry/verified loading path, verify hash **before** deserialize, maintain feature schemas, correct positive class index for lateness, calibration and embedded/explicit preprocessing where relevant, and allow reproducible fresh-process inference.
- Never import untrusted pickles/joblib payloads merely to test rejection; assert bad checksum/path/version prevents deserialization through safe mocks/stubs.

## 5. Exact master inventory

| Status | Task | Master work item | Mark | Pri | Dependency |
|---|---|---|---|---|---|
| [x] | DT-438 | Create pytest test suite | [E] | P1 | Core modules implemented |
| [x] | DT-439 | Test schemas | [E] | P1 | Implemented pipelines |
| [x] | DT-440 | Test joins | [E] | P1 | Implemented pipelines |
| [x] | DT-441 | Test time utilities | [E] | P1 | Implemented pipelines |
| [x] | DT-442 | Test label generation | [E] | P1 | Implemented pipelines |
| [x] | DT-443 | Test feature generation | [E] | P1 | Implemented pipelines |
| [x] | DT-444 | Test Task 1 inference | [E] | P1 | Implemented pipelines |
| [x] | DT-445 | Test Task 2A aggregation | [E] | P1 | Implemented pipelines |
| [x] | DT-446 | Test Task 2A forecast output constraints | [E] | P1 | Implemented pipelines |
| [x] | DT-447 | Test Task 2B compatibility rules | [E] | P1 | Implemented pipelines |
| [x] | DT-448 | Test Task 2B trip-time formula | [E] | P1 | Implemented pipelines |
| [x] | DT-449 | Test Task 2B optimizer output | [E] | P1 | Implemented pipelines |
| [x] | DT-450 | Test saved-model loading | [E] | P1 | Implemented pipelines |

**Coverage accounting:** DT-438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450 = **13/13**.

## 6. Inputs, outputs, file ownership

**Read-only inputs:** official booklet; master plan; existing production modules under `src/`; sanitized fixture builders; Phase 32 registry metadata; official checker definition; existing `pytest.ini`/`pyproject.toml`; current tests; Phase 33 compliance reports (only sanitized summaries). **Do not assume any candidate filenames below exist**; Cursor must inspect actual repository and map paths.

**Created/updated outputs (engineering recommendations):** `tests/test_phase34_*.py` modules and minimal `tests/conftest.py` updates; optionally `tests/fixtures/phase34/` **synthetic only**; `scripts/validate_phase34_tests.py` or existing runner integration if a coverage manifest is needed; ignored `reports/private/phase34_automated_testing/` summary reports without raw rows; Phase 34 completion record and master plan only **after successful independent review and required gate**.

**Files forbidden to modify:** `outputs/submission_task1.csv`, `outputs/submission_task2a.csv`, `outputs/submission_task2b.csv`, frozen `models/**`, `models/artifact_registry.json`, private datasets/reports, final notebook and frozen Task 1/2A/2B training/inference/optimizer logic (unless a confirmed blocking defect is separately authorized).

**Path principle:** discover actual files with `rg --files`, inspect `src`, `tests`, `configs`, existing Phase 32/33 scripts. The candidate paths in task sections below are search hints, not authoritative file existence claims.

## 7. Test design rules

- `pytest` is authoritative default runner; ensure tests collected on Windows `.venv` and CI Python; use `Path`, `tmp_path`, `monkeypatch`, `subprocess` with controlled input; avoid brittle separators or external CLI assumptions.
- Prefer table-driven `pytest.mark.parametrize` boundary fixtures and a few end-to-end synthetic-contract tests. Keep deterministic order and seeds, no wall-clock timing assertions, no unordered map dependencies.
- Assert behavior and invariants, not implementation trivia; avoid mocking the actual unit under test. Have oracle values independently derived from official arithmetic.
- Include passing fixtures AND negative cases; mutants that violate a rule must fail (e.g. one minute past close, third trip, wrong depot, chilled truck mismatch).
- Check IDs and ordering where a component promises preservation. For joins, test cardinality both before and after join and proper error/failure on invalid lookups.
- Explicitly avoid dataset-size assumptions unless from official templates; tests must be synthetic and not rely on private paths.
- If private parity or organizer checker requires real files, document a separate opt-in **human-local** command; do not run in agent environment or mark it independently PASS.
- Existing tests may cover requirements; build a proof matrix mapping each DT ID to actual collected pytest node IDs, expected positive/negative behaviors, and evidence. A new single test file with 13 trivial assertions is NOT sufficient.

## 8. Task-by-task implementation contracts

### DT-438 — Create pytest test suite

**Master intent:** Create pytest test suite. **Enhanced objective:** Test harness, discovery, deterministic fixtures, CI-safe default. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/conftest.py; pytest.ini or pyproject.toml; tests/test_phase34_suite.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** All 13 mapped categories discover; default run is offline/private-data-free; failure exit nonzero.

**Edge-case checklist:** test collection/import, smoke, isolated temp dirs, deterministic repeated execution. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-438 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-438):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-439 — Test schemas

**Master intent:** Test schemas. **Enhanced objective:** Column types, required headers, IDs, uniqueness, exact templates. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_schemas.py; src/common/schema*.py; configs/*`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Valid schemas accepted; missing/duplicate/case-mismatched columns rejected without coercion.

**Edge-case checklist:** empty tables, duplicate keys, missing columns, unexpected columns where exact, nullable IDs, type mismatch. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-439 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-439):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-440 — Test joins

**Master intent:** Test joins. **Enhanced objective:** Join cardinality, key completeness, no fanout or lost rows. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_joins.py; src/task1/*; src/task2a/*`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** One-to-one/verified many-to-one joins preserve left keys/order and fail on duplicate right keys.

**Edge-case checklist:** missing lookup, duplicated route legs, mismatched depot/outlet, shuffled inputs, ambiguous keys. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-440 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-440):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-441 — Test time utilities

**Master intent:** Test time utilities. **Enhanced objective:** Timestamp parsing, calendar and ISO week handling. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_time.py; src/common/*time*; src/task1/*; src/task2a/*`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Arrival/waiting and requested-date ISO week at year boundaries; deterministic time arithmetic.

**Edge-case checklist:** midnight, ISO year rollover, leap day, window exact close, timezone policy per existing implementation. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-441 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-441):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-442 — Test label generation

**Master intent:** Test label generation. **Enhanced objective:** True service duration, early wait, strict late flag. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_labels.py; src/task1/labels.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Early waiting excluded from service; exact-window-close arrival not late; arrival after close late.

**Edge-case checklist:** before opening, equal close, after close, zero-duration, bad ordering, missing actual timestamps. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-442 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-442):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-443 — Test feature generation

**Master intent:** Test feature generation. **Enhanced objective:** As-of features, temporal leakage exclusions, stable encoding. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_features.py; src/task1/*feature*; src/task2a/*feature*`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Feature schemas/order stable; outcome fields and future records cannot influence test features.

**Edge-case checklist:** future-sentinel, duplicate history, unseen category, null policy, shuffled source, missing required fields. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-443 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-443):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-444 — Test Task 1 inference

**Master intent:** Test Task 1 inference. **Enhanced objective:** Frozen service + late probabilities and ID order. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task1_inference.py; src/task1/*; src/artifacts/final_inference.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Fixture inference yields finite service and late probability in [0,1] and identity/order parity.

**Edge-case checklist:** empty allowed?, unseen categorical, corrupt schema, index permutation, multiclass class order positive=1, thresholds. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-444 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-444):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-445 — Test Task 2A aggregation

**Master intent:** Test Task 2A aggregation. **Enhanced objective:** Both sources, one order once, requested week. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task2a_history.py; src/task2a/history.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Duplicate `delivery_id` values across authoritative demand-history sources must be detected and rejected as a hard validation failure. Silent source-precedence deduplication is prohibited. Count deferred/not-run demand and aggregate by requested-date ISO year/week.

**Phase 11 reconciliation:** Phase 11 DT-177 is authoritative for the established Task 2A history behavior: uniqueness is validated within each source and after append; a cross-source duplicate is a STOP condition; `drop_duplicates()` and automatic source selection are prohibited. Phase 34 therefore tests the frozen fail-closed behavior and does not introduce a new source-precedence rule.

**Edge-case checklist:** overlap of sources, duplicate ID conflicting fields, year rollover, zero-volume, absent calendar join. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-445 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-445):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-446 — Test Task 2A forecast output constraints

**Master intent:** Test Task 2A forecast output constraints. **Enhanced objective:** Nonnegative volume; chilled <= total; Style/Tech chilled zero. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task2a_forecast.py; src/task2a/*; src/artifacts/final_inference.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Output finite; same supplied row_id identity; chilled=0 for Style/Tech; 0<=chilled<=total.

**Edge-case checklist:** NaN/inf, tiny negatives, chilled > total, case variations, unseen brands, duplicate row ids. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-446 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-446):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-447 — Test Task 2B compatibility rules

**Master intent:** Test Task 2B compatibility rules. **Enhanced objective:** Temperature, type/parking, depot, workshop, brand/district. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task2b_compatibility.py; src/task2b/*`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Reject chilled on dry vehicle, van_only on truck, wrong depot, unavailable vehicle, mixed brand/district trip.

**Edge-case checklist:** reefer ambient permissible; reefer van dual constraint; no candidate; status variants; mixed group. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-447 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-447):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-448 — Test Task 2B trip-time formula

**Master intent:** Test Task 2B trip-time formula. **Enhanced objective:** Outbound + inter-stop*(n-1) + handling; time budgets. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task2b_trip_time.py; src/task2b/trip_time.py`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Official 3-stop example 101 min; no return leg; one outbound/trip; Fresh 270 and Style+Tech combined 480, max 2 trips.

**Edge-case checklist:** one stop; second trip; budget exactly limit; one above limit; same vehicle cross-window; missing district rate. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-448 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-448):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-449 — Test Task 2B optimizer output

**Master intent:** Test Task 2B optimizer output. **Enhanced objective:** One row/order, served/deferred consistency, hard feasibility. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_task2b_optimizer.py; src/task2b/*; official checker wrapper if supported`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Synthetic allocation has total coverage, whole orders, trip IDs 1/2, capacities, grouping, budgets, scenario separation; independent feasibility validation.

**Edge-case checklist:** oversized order, no vehicle, all deferred, duplicate order_ref, cross-scenario, weight-vs-volume tradeoff, mismatched availability. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-449 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-449):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

### DT-450 — Test saved-model loading

**Master intent:** Test saved-model loading. **Enhanced objective:** Registry, integrity-before-deserialization, fresh process, parity. This objective expands the master work item with testable assertions; it does not change competition rules.

**Candidate source/test files (verify actual paths first):** `tests/test_phase34_artifact_loading.py; src/common/artifact_io.py; src/artifacts/final_inference.py; models/artifact_registry.json`.

**Inputs:** synthetic in-memory records/objects modeling the official inputs and the current verified production function signatures; small helper fixtures constructed without private competition values. Where applicable, use actual public constants/config metadata but not real rows.

**Implementation instructions:**

1. Find the canonical production method(s), pre-existing tests and official rule; record exact function names and current behavior before writing tests.
2. Create minimal synthetic positive fixtures and **independent** expected results. Confirm `pytest --collect-only -q` discovers them.
3. Implement parametrized boundary/negative fixtures. Assert precise failures or safe reject behavior; do not let broad `except` clauses mask regressions.
4. Add metamorphic cases where useful (e.g. shuffled irrelevant source row order, duplicate-key injection, permuting scenario order) and explicit invariants.
5. Run the new tests in isolation and with existing tests. Fix tests or genuine code defects only within authorized scope. A production-logic conflict is a **STOP** pending approval, not a reason to rewrite a frozen solution.
6. Record evidence as collected pytest node IDs and aggregate PASS/FAIL with no record-level contents in logs.

**Acceptance / observable result:** Synthetic artifacts loaded via registry; tampered hash rejected before load; path traversal/symlink blocked; fresh-process deterministic prediction.

**Edge-case checklist:** absent artifact, version/schema mismatch, corrupt bytes, 0/1 class mapping, wrong preprocessor, malicious pickle never executed. Keep unknown/missing/ambiguous-source behavior aligned with existing documented schema rather than inventing organizer rules.

**STOP conditions:** unexpected official semantics; dependence on non-synthetic restricted data; altered frozen predictions or registry; fragile test that passes only in the developer process; hidden training/model writes; unresolved actual-source API mismatch. Mark DT-450 FAIL/PENDING rather than faking a PASS.

**Definition of Done (DT-450):** normal + negative + boundary tests collect, run, assert official/production contract, are deterministic on repeat, do not mutate frozen files, and have independent reviewable evidence.

## 9. Cross-task integration, execution order and validation matrix

Suggested order: (1) inspect/collect existing tests and build DT coverage matrix; (2) DT-438 framework; (3) DT-439–443 shared data invariants; (4) DT-444–446 inference/forecast; (5) DT-447–449 allocation; (6) DT-450 registry; (7) full regression; (8) fresh independent review. **No need to rewrite existing mature tests just to satisfy filenames.**

| Gate | Test or proof | Must be true |
|---|---|---|
| Collection | `.venv\Scripts\python.exe -m pytest --collect-only -q` | All Phase 34 tests discover; no import-time side effects |
| Targeted | `.venv\Scripts\python.exe -m pytest -q tests/test_phase34_*.py` | Adapt for actual shell glob; all new tests pass |
| Regression | `.venv\Scripts\python.exe -m pytest -q` | No regressions; skips explained |
| Environment | `.venv\Scripts\python.exe -m pip check` | No broken dependencies |
| Repository | `git diff --check` / `git status --short` | No unintended paths, whitespace or staged secrets |
| Hash guards | SHA256 baseline and post-run official CSV/registry/models | Byte-identical, 12/12 registry entries pass if registry has 12 |
| Phase 33 | Existing final compliance gate report | Phase 33 closed before Phase 34 proceeds |
| Phase 34 traceability | DT ID -> pytest nodes -> assertions -> actual run | 13/13 coverage; no false PASS claims |
| Privacy | `git status --short --ignored` / `git check-ignore -v` | Private evidence stays ignored; no real record leaks |

**PowerShell-safe commands** (execute at repository root; confirm actual test filenames):

```powershell
cd C:\Users\ASUS\Desktop\WayLoom_Datathon
.\.venv\Scripts\python.exe -m pytest --collect-only -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
git diff --check
git status --short
```

If the environment uses other paths, adjust only after confirming. Never copy individual private CSV rows to output. If any checker or full inference needs restricted inputs, provide a sanitized human-run-only instruction instead of running it as agent.

## 10. Test fixture catalog (all synthetic)

Build or reuse named fixtures with assertions: `valid_task1_route`, `early_arrival`, `arrive_exactly_at_close`, `arrive_one_minute_late`, `route_key_duplicate`, `iso_week_year_rollover`, `mixed_source_duplicate_delivery`, `deferred_demand_order`, `task2a_nonfresh`, `task2a_chilled_gt_total`, `reefer_van_only_valid`, `dry_truck_chilled_invalid`, `unavailable_vehicle`, `wrong_home_depot`, `brand_district_mixed_trip`, `trip_single_stop`, `trip_gampaha_101min`, `vehicle_two_trips_boundary`, `vehicle_three_trips_rejected`, `fresh_270_boundary`, `styletech_480_boundary`, `tampered_registry_checksum`, `blocked_registry_traversal`, `fresh_process_fixture`.

Construct values for tests from documented *relationships* and official numeric trip example, not from actual competition rows. For malformed examples, assert controlled exceptions with useful error classes/messages where contract supports them. Avoid asserting exact ML predictions unless generated deterministically by **synthetic** saved test models or pre-existing approved parity fixtures.

## 11. Frozen file and privacy guardrails

Before-and-after comparison must cover all three official final CSVs, `models/artifact_registry.json`, registered model/checksum files, and any frozen configs governed by Phase 32. The guard may read file bytes only to compute SHA256; never display them or write them back. **Do not accidentally hash private report files and present their paths publicly.** Do not use `git add -A`. Any observed alteration to frozen artifacts is immediate STOP and report; no silent restoration because that can erase user changes.

Security tests for untrusted pickle/joblib must use mocked deserializer functions and synthetic harmless files; demonstrate hash rejection occurs **before** dangerous loading. Registry path-traversal, absolute path/symlink boundaries, JSON schema/version validation are relevant to DT-450 where supported by existing loader contract.

## 12. Failure classification and mandatory stop conditions

**P0 STOP:** official-booklet contradiction; private data access needed inside agent; failed Phase 33 closure; any CSV/model/registry mutation; true leakage of outcomes into prediction-time features; inability to reproduce registered saved-model load safely; official checker proves frozen Task 2B infeasible; hard allocation rule violated. Document exact blocker but do not patch production or official outputs without explicit authorization.

**P1 STOP/review:** new tests expose genuine frozen-module defect; contract inconsistency or missing authoritative schema; external side effects in pytest; dependency changes needed outside agreed scope; missing model/asset preventing safe offline tests. Provide the minimal remediation plan and human approval request.

**Nonblocking:** explanatory deprecation warnings, optional tests skipped for clearly documented environment reason, naming cleanup not required for assertions. No mass refactor, no implicit phase advancement.

## 13. Git workflow

1. Record baseline `git status --short`, baseline hashes and phase-gate statuses.
2. Edit only authorized test/fixture/test-config/Phase34-report files; apply minimal intentional import/packaging changes if needed.
3. Verify `git diff --stat`, `git diff --check`, and reviewed `git diff`; reject unintended production changes.
4. Run targeted, full safe regression and pip check; check hash guard PASS and ignored private report status.
5. Stage **only named approved files** if authorized; otherwise leave unstaged. **Never commit by default**; provide suggested commit message `test(phase34): harden automated competition invariants` for human approval.
6. Mark Phase 34 complete and `READY FOR NEXT PHASE: YES` **only after** implementation PASS, human-local requirements where relevant, fresh independent review PASS, and master-plan completion report reconciliation. Historic failures must not be silently rewritten.

## 14. Definition of Done — phase gate

All of the following are mandatory:

- [x] **13/13** DT tasks have credible explicit evidence of tests/assertions, not just unchecked TODOs.
- [x] Tests collect and run without private data and cover positive, negative, boundary, and official arithmetic cases as applicable.
- [x] The existing safe suite passes without ignored or masked regressions; the mapped suite produced identical repeated results.
- [x] Task 1 labels and inference, Task 2A week/forecast behavior, Task 2B feasibility/trip time, and Phase 32 secured saved-model loading are protected.
- [x] Official submissions, registry, and registered model artifacts remain byte-identical; no private rows or predictions were disclosed.
- [x] Code/test changes were reviewed, Git hygiene was checked, existing user edits were preserved, and no unauthorized commit was made.
- [x] A fresh independent read-only re-review returned PASS and explicitly authorized the completion record and master-plan status update.

## 15. Phase 34 completion record

### 15.1 Final task verdicts

| Task | Final verdict | Evidence summary |
|---|---|---|
| DT-438 | PASS | Deterministic Phase 34 manifest covers 13 tasks with 89 mappings and 87 unique collected test nodes; missing and mistargeted remediation evidence is rejected. |
| DT-439 | PASS | Production-backed schema tests reject missing, extra, reordered, duplicated, case-mismatched, header-only, malformed-identity, and incorrect-type inputs. |
| DT-440 | PASS | Composite-key, cardinality, unmatched-row, destination, and calendar-join failures are tested fail-closed. |
| DT-441 | PASS | Clock/date parsing, leap-day transitions, midnight rollover, strict-close equality, waiting exclusion, ISO rollover, and impossible chronology are covered. |
| DT-442 | PASS | Canonical service-minute and strict-lateness labels, missing values, and inconsistent labels are protected. |
| DT-443 | PASS | Train/test feature parity, forbidden direct fields, renamed leakage lineage, same-day exclusion, shuffle determinism, and future-mutation isolation are covered. |
| DT-444 | PASS | Saved-model Task 1 inference preserves schema, finite output, probability bounds, identity/order, frozen preprocessing, and no-retraining behavior. |
| DT-445 | PASS | Both demand sources, attempted/deferred/not-run demand, requested ISO week, structural chilled zeros, invalid volumes, interior zeros, and fail-closed duplicate IDs are covered. |
| DT-446 | PASS | Task 2A row identity, ten horizons, finiteness, nonnegativity, structural zeros, and chilled-not-above-total constraints are covered. |
| DT-447 | PASS | Task 2B availability, refrigeration, van access, depot, brand/district grouping, weight, and volume rules are covered. |
| DT-448 | PASS | Official 101/112-minute arithmetic, no return leg, one/two-trip behavior, trip 3 rejection, and inclusive 270/480-minute limits are covered. |
| DT-449 | PASS | Optimizer completeness, whole orders, grouping, capacity, proof status, independent hard-rule audit, and all-deferred output are covered. |
| DT-450 | PASS | Checksum-before-load, path confinement, serializer/corrupt payload rejection, registry version/reference validation, preprocessing consistency, class mapping, fresh-process load, and synthetic inference are covered. |

### 15.2 Final verification evidence

- **Phase 33 prerequisite:** PASS; DT-420-DT-437 remain 18/18 complete and Phase 33 readiness remains YES.
- **Traceability:** 89 manifest mappings, 87 unique pytest nodes; validation suite 5 passed.
- **Remediation tests:** 10 passed.
- **Mapped Phase 34 suite:** 138 passed, 1 skipped, repeated twice with identical results.
- **Full safe suite:** 858 passed, 2 skipped, 4 warnings.
- **Skipped tests:** the DT-450 symlink-escape test and the integration-privacy symlink test were skipped because Windows symlink creation was unavailable; they were not counted as executed passes.
- **Warning provenance:** one Starlette/AnyIO deprecation warning and three SHAP/Matplotlib pending-deprecation warnings; no Phase 34 correctness failure.
- **Dependency and repository checks:** `python -m pip check` PASS; `git diff --check` PASS.
- **Official CSV SHA256 guards:** PASS for Task 1, Task 2A, and Task 2B; all remained byte-identical.
- **Phase 32 artifact integrity:** registry hash unchanged; all 12 registered artifact hashes and sizes PASS.
- **Privacy:** no confidential rows, private notebook output, or private-report contents were inspected or disclosed; `reports/private/**` remained ignored and untracked.
- **Evidence provenance:** test counts and the technical verdict above come from the authorized fresh independent re-review. This administrative closure did not claim to rerun human-local Phase 33/private-data checks.

### 15.3 Independent-review history

The first independent Phase 34 review returned **FAIL** and did not authorize closure. Its five blocking findings were preserved as review history:

1. DT-438 lacked complete and accurate traceability enforcement.
2. DT-439 lacked explicit case-mismatched schema-header rejection.
3. DT-441 lacked leap-day boundary coverage.
4. DT-445 contradicted the authoritative Phase 11 fail-closed duplicate-ID rule.
5. DT-450 lacked registry-version and feature-schema/preprocessor-reference mismatch rejection.

A narrow remediation subsequently corrected the Phase 34 contract, traceability manifest, and synthetic tests without changing production behavior or frozen artifacts. The latest fresh independent re-review verified all five findings as resolved, returned **PASS** for DT-438 through DT-450, found no blockers, and explicitly authorized formal Phase 34 closure.

### 15.4 Formal status

```text
PHASE34 IMPLEMENTATION / REVIEW STATUS: PASS
PHASE33 PRECONDITION: PASS
DT-438 THROUGH DT-450: 13/13 PASS
PYTEST TRACEABILITY: 5 PASSED
PYTEST REMEDIATION: 10 PASSED
PYTEST MAPPED: 138 PASSED, 1 SKIPPED (REPEATED TWICE)
PYTEST FULL: 858 PASSED, 2 SKIPPED, 4 WARNINGS
PIP CHECK: PASS
GIT DIFF CHECK: PASS
OFFICIAL CSV HASHES: PASS - UNCHANGED
PHASE32 REGISTRY / MODEL CHECKSUMS: PASS - REGISTRY UNCHANGED, 12/12 ARTIFACTS
PRIVATE DATA PROTECTION: PASS
INDEPENDENT RE-REVIEW: PASS - FORMAL CLOSURE AUTHORIZED
BLOCKERS: NONE
PHASE COMPLETE: YES
READY FOR PHASE35: YES
```

## 16. Recommended prompts

The separate full implementation prompt is `PHASE_34_CODEX_CURSOR_PROMPT.txt`. The separate fresh read-only audit is `PHASE_34_INDEPENDENT_REVIEW_PROMPT.txt`. Both repeat the exact task IDs, precedence, gating and freeze rules. Do not confuse a test suite passing with the Phase 34 independent-review verdict.
