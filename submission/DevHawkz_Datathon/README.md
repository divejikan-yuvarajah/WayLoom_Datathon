# WayLoom — DevHawkz Datathon Submission

Official team: **DevHawkz**. Project: **WayLoom**. Competition: **Rootcode Tech Triathlon 2026 — Datathon**.

This folder contains the WayLoom deliverables. It is an allowlisted submission copy, not the development repository.

## Required deliverables

- `DevHawkz_FinalNotebook.ipynb` - cleared source notebook with label construction, preprocessing, training/evaluation narrative and final saved-model inference cell. Its contents are byte-identical to the frozen development notebook.
- `submission_task1.csv`, `submission_task2a.csv`, `submission_task2b.csv` - official submission files at the package root for easy discovery; each is byte-identical to the corresponding copy under `outputs/`.
- `outputs/submission_task1.csv` - frozen Task 1 predictions.
- `outputs/submission_task2a.csv` - frozen Task 2A forecasts.
- `outputs/submission_task2b.csv` - frozen Scenario S1 allocation.
- `models/` - Task 1 and Task 2A saved artifacts plus `artifact_registry.json`.
- `docs/architecture/` - model, preprocessing and proposed-deployment diagrams. Proposed deployment is not represented as an already deployed service.
- `docs/preprocessing.md` and supporting specifications - data preparation, label construction, cleaning, features, validation and inference contracts.
- `docs/task2b_policy.md` - final allocation priority, constraint and deferral rationale.
- `docs/AI_USE_DISCLOSURE.md` - exact approved AI-use disclosure.

The required 3–5 minute unlisted demo-video URL is **pending**. The authorized team representative must provide and verify it before final submission; this package does not claim that a video exists.

## Environment

Use Python 3.13 in an isolated environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

The package contains repository-controlled Python modules, configuration files, schemas and registered model artifacts required by the notebook. Raw competition datasets are deliberately excluded from the ZIP. An authorized local operator must obtain them from the organizer and place them in the layout described by `configs/dataset_manifest.yaml` before executing data-dependent cells.

## Validation and notebook execution

Validate the cleared source notebook without executing private data:

```powershell
.\.venv\Scripts\python.exe scripts\validate_final_notebook.py --source DevHawkz_FinalNotebook.ipynb --config configs\final_notebook.yaml
```

The final code cell loads the registered Task 1 and Task 2A model artifacts using relative paths. Full Run All execution requires the official competition datasets and must be performed only by an authorized local operator. Do not save private execution outputs into the submitted source notebook.

## Integrity and interpretation

The three CSVs, notebook, registry and registered model artifacts are frozen. The official Task 2B checker establishes feasibility against its implemented rules, not global optimality. No unavailable Task 1/Task 2A performance value or unapproved Phase 37 result chart is included.

`SUBMISSION_MANIFEST.sha256` lists the size and SHA256 of every other archive member. Verify it after extraction before submission or evaluation.
