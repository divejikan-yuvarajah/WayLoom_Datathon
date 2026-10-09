# WayLoom — Rootcode Tech-Triathlon 2026 Datathon

WayLoom is a local, reproducible solution for the three Datathon tasks: predicting delivery service time and lateness risk, forecasting weekly depot demand, and producing a feasible peak-day vehicle allocation. The repository keeps the prediction, forecasting, and optimization workflows separate while sharing schema validation, time handling, artifact integrity, and privacy controls.

This README is the Phase 36 project guide. Phase 36 implementation is awaiting a fresh independent review; its master-plan task boxes and readiness flag intentionally remain open. The Phase 35 AI-use disclosure also remains open pending its own factual approval and review.

## Project objectives

| Task | Objective | Official output interface |
|---|---|---|
| Task 1 | Predict service duration and the probability that a dispatched delivery arrives late. Waiting before an outlet opens is excluded from service time, and arrival exactly at closing time is not late. | `submission_task1.csv`: `delivery_id`, `pred_service_min`, `pred_late_prob`; the supplied identifiers and original row order are preserved. |
| Task 2A | Forecast total and chilled volume for each supplied depot, brand, and ISO week over the 10-week horizon. Requested demand includes attempted, deferred, and not-run orders once each. | `submission_task2a.csv`: `row_id`, `pred_total_volume_m3`, `pred_chilled_volume_m3`; identifiers and template order are preserved. Predictions are nonnegative, Style/Tech chilled volume is zero, and chilled volume cannot exceed total volume. |
| Task 2B | Allocate or defer each peak-day order under vehicle compatibility, capacity, trip-count, and time-budget constraints, then explain the prioritization policy. | `submission_task2b.csv`: `scenario`, `order_ref`, `outlet_id`, `decision`, `vehicle_id`, `trip_id`; served orders use trip 1 or 2 and deferred assignment fields are blank. |

The official brief, inputs, deliverables, judging criteria, and submission-template conventions are in the [Challenge Booklet](MD%20Files/Challenge%20Booklet.pdf). The [master plan](MD%20Files/WAYLOOM_DATATHON_MASTER_PLAN.md) controls the internal phase gates.

## Implemented approach

- **Task 1:** deterministic joins and pre-event feature construction feed separate locally trained CatBoost service-regression and lateness-classification bundles. Actual route outcomes are used only to construct historical labels. The final inference path preserves the registered feature schema and uses positive-class probability for lateness.
- **Task 2A:** unique requested orders from the historical and later-order sources form an ISO-week demand panel. Origin-relative lag, rolling, trend, horizon, and known-calendar features feed separate equal-weight CatBoost/LightGBM ensembles for total volume and Fresh chilled volume. Frozen postprocessing enforces the official output constraints.
- **Task 2B:** a deterministic CP-SAT workflow enforces home-depot, reefer, van-only, whole-order, brand/district trip grouping, weight/volume capacity, two-trip, and time-budget rules. Its lexicographic priorities are WayLoom engineering choices; passing the organizer checker establishes feasibility, not optimality.

The [architecture index](docs/architecture/README.md) links the high-level, task-specific, and proposed-deployment diagrams. The [preprocessing and methodology document](docs/preprocessing.md) contains the detailed joins, labels, features, leakage controls, validation design, and rationale.

## Repository structure

| Path | Role |
|---|---|
| `TeamName_FinalNotebook.ipynb` | Competition notebook containing project context, label/preprocessing/training/evaluation cells, and the final saved-model inference cell. |
| `src/task1/`, `src/task2a/`, `src/task2b/` | Production logic for prediction, forecasting, and allocation. |
| `src/common/`, `src/artifacts/` | Shared validation and checksum-verified artifact-loading controls. |
| `configs/` | Versioned pipeline, inference, validation, and reproducibility settings. |
| `scripts/` | Command-line build, validation, notebook-execution, and integrity entry points. |
| `models/` | Local frozen model bundles, schemas, metadata, and the authoritative artifact registry. Treat the contents as controlled competition artifacts. |
| `outputs/` | Local frozen copies of the three official submission CSVs. Do not publish or regenerate them during documentation or review work. |
| `docs/` | Architecture, preprocessing, model-artifact, validation, policy, disclosure, and reviewer guidance. |
| `tests/` | Deterministic pytest coverage using synthetic fixtures; it does not establish private-data parity. |
| `MD Files/` | Official booklet, master plan, and phase contracts/review records. |
| `data/`, `reports/` | Local restricted inputs, derivatives, and evidence. Their confidential contents are not documentation examples and must not be staged or shared. |

See the [repository data policy](docs/repository_data_policy.md) before handling competition material.

## Environment setup

The recorded reference environment is Windows PowerShell with Python 3.13.7. The artifact registry records the exact runtime/library versions used by the frozen models. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-lock.txt
python -m pip check
```

`requirements-lock.txt` is the reference environment snapshot; `requirements.txt` lists direct project dependencies. If activation is unavailable, invoke `.\.venv\Scripts\python.exe` directly. No GPU, hosted API, Docker image, or AutoML platform is required by the documented local workflow.

The installation command may access package indexes. It does not download competition data. Competition inputs must already be present in the team's authorized local environment and must never be uploaded to reproduce a command.

## Running and validating the notebook

First run the source-only structural validation; it does not execute private data or overwrite the notebook:

```powershell
.\.venv\Scripts\python.exe scripts\validate_final_notebook.py --source TeamName_FinalNotebook.ipynb --config configs\final_notebook.yaml
```

An authorized human-local operator can execute a disposable copy top-to-bottom with the configured 7,200-second cell timeout:

```powershell
.\.venv\Scripts\python.exe scripts\execute_final_notebook.py --input TeamName_FinalNotebook.ipynb --output reports\private\phase31_final_notebook\TeamName_FinalNotebook.executed.ipynb --config configs\final_notebook.yaml --mode run-all
```

The executed copy belongs only in an ignored local directory. Do not overwrite or commit the source notebook, copy executed outputs into documentation, or run the command where the required competition inputs are unauthorized. A previously recorded human-local clean-kernel Run All and separate final-cell-only run passed; this README work did not rerun those private-data checks.

The final notebook cell reloads Task 1 and Task 2A artifacts through the secured registry path rather than depending on fitted objects left in kernel memory. The final cell demonstrates inference but is configured not to rewrite the official CSVs.

## Model files and secured loading

`models/artifact_registry.json` is the authoritative inventory for 12 required Task 1 and Task 2A entries:

- Task 1 service and lateness CatBoost model bundles, metadata, and feature schemas;
- Task 2A total-volume and chilled-volume CatBoost/LightGBM ensemble bundles, metadata, shared feature schema, and ensemble manifest.

Registry entries use repository-relative paths and record serializer, target, feature schema, model family, byte size, SHA256, library versions, load entry point, and inference entry point. The loader rejects absolute/traversal/network paths, unsupported serializers, schema/reference mismatches, missing files, and checksum mismatches before deserialization. Task 2B is an optimization workflow and therefore has no trained predictive-model artifact.

For the artifact contract and validation boundaries, see [model artifacts](docs/model_artifacts.md). Do not load an unregistered or untrusted serialized file.

## How outputs are generated

The official CSVs are frozen outputs, not README examples. Their generation paths are:

1. **Task 1:** build prediction-time features using planned/order/reference information, securely load the frozen service and lateness bundles, infer by `delivery_id`, validate finite service values and probabilities in `[0,1]`, and fill the original template order.
2. **Task 2A:** construct the canonical requested-demand history, build direct-horizon features, securely load the two frozen ensemble bundles, infer total and Fresh chilled volume, enforce nonnegative/brand/chilled-cap constraints, and map results to the template by `row_id` in template order.
3. **Task 2B:** solve the frozen peak-day scenario under the hard rules, independently validate the allocation, run the organizer feasibility checker, and export decisions into the official template without changing its identity/order fields.

The Phase 33 validator is read-only over the final CSVs and guards each file's hash before and after validation. Its design is documented in [final submission validation](docs/final_submission_validation.md). Do not rerun training, inference, optimization, or exporters merely to inspect the deliverables.

## Task 2B time and prioritization rules

For a same-brand, same-district trip, the official duration is:

`trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)`

There is no added return leg. Each vehicle may run at most two trips; combined Fresh trips must fit 270 minutes, and combined Style/Tech trips must fit their separate 480-minute budget. Feasibility always dominates WayLoom's nine-tier lexicographic prioritization. Read the [Task 2B prioritization policy](docs/task2b_policy.md) for the final calculation and deferral rationale.

## Reproducibility

- The project seed is **42**. It is recorded in model, optimizer, notebook, and integration configurations and passed to the supported CatBoost, LightGBM, scikit-learn, and solver paths.
- `requirements-lock.txt` and registry runtime metadata capture the reference versions. Use the project virtual environment rather than a system Jupyter kernel.
- Task 1 split logic and Task 2A rolling origins are chronological and deterministic. Task 2A LightGBM components use single-threaded fitting in the frozen candidate configuration.
- The final notebook execution wrapper sets `PYTHONHASHSEED` from `configs/final_notebook.yaml` before starting the kernel.
- Seeds improve repeatability but do not guarantee byte-identical retraining across operating systems, processor architectures, dependency versions, or thread schedules. Frozen artifact hashes and output hashes, rather than retraining, are the release-integrity reference.

More detail is in [reproducibility notes](docs/reproducibility.md). A clean-environment end-to-end reproduction remains a later Phase 39 gate; it is not claimed complete here.

## Safe verification

These commands use tracked source and synthetic fixtures. They do not prove private-data parity:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_phase36_documentation.py
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pip check
git diff --check
git status --short
git diff --cached --name-only
```

Use the [judge walkthrough](docs/DATATHON_JUDGE_WALKTHROUGH.md) for a concise, row-free review route. A fresh read-only Phase 36 review must independently verify these docs and the protected hashes before any Phase 36 completion flag changes.

## Deliverables and current status

| Deliverable | Repository location/status |
|---|---|
| Architecture diagrams | [Architecture index](docs/architecture/README.md) — implemented; proposed deployment is explicitly labelled proposed. |
| Preprocessing document | [Preprocessing and methodology](docs/preprocessing.md) — implemented. |
| Final model files | Controlled local `models/` artifacts; registered and checksum-guarded. |
| Final notebook | [TeamName_FinalNotebook.ipynb](TeamName_FinalNotebook.ipynb) — source notebook present. |
| Task 1, Task 2A, Task 2B CSVs | Frozen controlled files under `outputs/`; exact filenames and schemas are documented above, with no row content reproduced here. |
| Task 2B written policy | [Prioritization policy](docs/task2b_policy.md) — implemented. |
| AI-tool disclosure | [AI-use disclosure](docs/AI_USE_DISCLOSURE.md) — draft; Phase 35 and final human approval remain open. |
| Results summary | Pending Phase 37; no competition metric is invented here. |
| Demo video | Pending Phase 38; no URL or completion claim exists yet. |
| Final folder/ZIP/upload | Pending Phases 40–42 and authorized human submission. |

## Privacy, limitations, and review boundaries

- Competition datasets, row-level derivatives, identifiers, predictions, executed notebook outputs, private evidence, and secrets are confidential. Do not place them in documentation, prompts, screenshots, logs, commits, or public repositories.
- The tests in this repository use synthetic fixtures unless a command is explicitly described as human-local. Passing them does not substitute for authorized private validation.
- No final performance score is claimed before Phase 37. No production deployment is claimed; the deployment architecture is a proposal.
- The factual AI-use record includes known external sharing and unresolved scope details. The team-reported organizer response is not described as blanket written clearance. Refer to the disclosure itself and do not infer broader permission.
- Phase 36 implementation does not close Phase 35, change any official submission/model/notebook byte, begin Phase 37, or authorize packaging/upload.
