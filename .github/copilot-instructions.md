# WayLoom Datathon Copilot Instructions

## Repository context and authority

This is the WayLoom submission workspace for the Rootcode Tech-Triathlon 2026 Datathon. The work is organized into numbered phases and three competition tasks:

- **Task 1:** predict service minutes and lateness probability for each delivery.
- **Task 2A:** forecast weekly total and chilled order volume by depot and brand.
- **Task 2B:** produce a feasible peak-day vehicle/trip allocation.

Use the current phase contract in `MD Files/PHASE_XX_COMPETITION_CONTRACT.md` as the implementation contract, together with `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` and `MD Files/CODEX_HANDOFF_PHASE_11_ONWARDS.md`. Resolve conflicts in this order:

1. Official challenge booklet, supplied templates/data, and `check_allocation.py`
2. `WAYLOOM_DATATHON_MASTER_PLAN.md`
3. The approved phase contract
4. Existing tested production code
5. Engineering assumptions

Do not silently alter an official rule or begin work from a later phase.

## Environment and commands

The project targets Python 3.13 and uses the local Windows virtual environment `.venv`.

Create or refresh the environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

When activation is unavailable, invoke `.\.venv\Scripts\python.exe` directly. `requirements.txt` contains direct dependencies; `requirements-lock.txt` is the recorded local freeze and should only be regenerated deliberately.

Run the complete safe test suite and dependency check:

```powershell
pytest -q
python -m pip check
```

Run one file, one test, or a focused expression:

```powershell
pytest -q tests/test_task1_features.py
pytest -q tests/test_task1_features.py::test_dt101_dt102_cross_midnight_slack_and_wait
pytest -q tests/test_task1_features.py -k "cross_midnight"
```

There is no configured Ruff, Black, mypy, tox, or package build command in the repository. Preserve the existing style and use pytest plus `pip check` as the project-defined validation. CLI scripts are run as modules/files from the repository root, for example:

```powershell
python scripts/run_dataset_inventory.py --help
python scripts/validate_task1_submission.py --help
```

Check each script's `--help` output and the applicable phase contract for required paths before running a data-processing command.

## Architecture

The repository is a configuration- and contract-driven data science pipeline:

- `src/common/` contains cross-task infrastructure: dataset discovery and manifest handling, schema assertions, data-quality checks, and local logging.
- `src/task1/` contains the complete Task 1 lifecycle. Labels are built from historical route actuals, EDA and feature builders produce leakage-safe tables, validation defines chronological folds/holdouts, baselines and advanced models are evaluated, calibration/model selection are persisted, and final training/inference exports the official submission.
- `src/task2a/` and `src/task2b/` are reserved task namespaces for the later forecasting and allocation phases; do not infer unfinished behavior from the package stubs.
- `scripts/` provides the executable orchestration layer. Scripts load YAML/configuration, resolve official artifact paths through the manifest, call `src` functions, and write reports/models/submissions to ignored local locations.
- `configs/` is the source of runtime contracts, including official schema/data-quality rules, dataset filenames and keys, model settings, and the frozen Task 1 model configuration.
- `tests/` uses synthetic fixtures and unit/integration-style checks to protect schema rules, leakage guards, chronological validation, feature construction, baselines, calibration, final training, and submission formatting.
- `data/` holds local competition inputs and derivatives; `models/`, `outputs/`, `reports/private/`, and `logs/` hold generated local artifacts. These paths are intentionally ignored by Git.

The official dataset manifest and data-quality rules are authoritative for filenames, grains, keys, required columns, enums, and Task 1 feature deny-lists. Keep transformations deterministic with the configured random seed (`42`) and preserve official template row/order and identifier columns when exporting.

## Critical data and modeling conventions

- Never inspect, print, transmit, or commit competition rows or private derivatives. Use synthetic fixtures for agent-run tests and diagnostics. Restricted locations include `data/raw/`, `data/interim/`, `data/processed/`, `reports/private/`, and generated row-level outputs.
- Do not stage CSV/ZIP competition files, `DataSet/**`, models, outputs, checker reports, logs, credentials, or secrets. Review `git status --ignored` and staged filenames before commits.
- Task 1 is frozen through the completed Phase 10 milestone. Unless a later global validation finds a genuine defect, do not modify `configs/task1_final_models.yaml`, `models/task1_service/**`, `models/task1_late/**`, or `outputs/submission_task1.csv`; do not reopen model search while implementing Task 2A/2B.
- Task 1 training-only actual route fields must never become prediction-time features: `actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, `leave_outlet_time`, `service_start`, `service_min`, and `late_flag` are protected by feature/leakage checks.
- Task 1 labels use `service_start = max(actual arrival, window opening)`, service minutes as leave time minus service start, and lateness only when arrival is strictly after window close; arrival exactly at closing is on time.
- Keep train-only preprocessing statistics, categorical vocabularies, and feature selection inside the training fold. Preserve chronological ordering, disjoint holdouts, and validation invariants rather than using random splits.
- Prefer explicit domain exceptions and existing validation helpers over silent coercion or fallback values. Schema, leakage, key-integrity, and submission-contract failures should remain visible.

## Workflow expectations

Before editing, identify the active phase and read only its contract plus the relevant source/tests. Make phase-scoped changes, add or update synthetic tests for behavior changes, and run the smallest applicable pytest target before the full suite when practical. If a task needs restricted real data, stop at the documented human-local stage and report the exact local command rather than accessing rows in the agent context.

Follow the existing end-of-phase checks:

```text
pytest -q
python -m pip check
git status
```

Do not automatically start the next phase. A phase is complete only when its Definition of Done, tests, safety checks, and gate are satisfied; report blockers for official-rule ambiguity, restricted-data access, leakage/future-information risk, frozen-contract conflicts, or material out-of-scope design changes.

