# WayLoom Datathon judge walkthrough

This is a concise, privacy-safe route through the WayLoom submission. It identifies evidence without displaying competition rows, identifiers, predictions, or private reports.

## 1. Orient to the three tasks

Start with the root [README](../README.md). Its project-objectives table separates:

- Task 1 service-duration and lateness-probability prediction;
- Task 2A 10-week depot/brand total and chilled-volume forecasting;
- Task 2B deterministic peak-day allocation and deferral reasoning.

The authoritative competition requirements are the [Challenge Booklet](../MD%20Files/Challenge%20Booklet.pdf). The README is a WayLoom navigation aid and does not replace an official deliverable.

## 2. Review architecture and methodology

Open the [architecture index](architecture/README.md), then the high-level and three task diagrams. The proposed-deployment view is explicitly a proposal, not a production-deployment claim.

Read [preprocessing and methodology](preprocessing.md) for dataset roles, validated joins, Task 1 labels, feature construction, leakage controls, Task 2A rolling validation, and Task 2B feasibility preparation. It distinguishes official rules from WayLoom engineering decisions.

## 3. Inspect the final notebook safely

Review [TeamName_FinalNotebook.ipynb](../TeamName_FinalNotebook.ipynb) as source. Its final cell is designed to reload registered Task 1 and Task 2A saved models instead of using hidden in-memory fitted objects. Do not execute it unless the operator is authorized to use the local competition inputs, and do not save executed private outputs into the source notebook.

A source-only structural validation is available:

```powershell
.\.venv\Scripts\python.exe scripts\validate_final_notebook.py --source TeamName_FinalNotebook.ipynb --config configs\final_notebook.yaml
```

## 4. Review model integrity

Read [model artifacts](model_artifacts.md). The local `models/artifact_registry.json` binds 12 required model, metadata, schema, and manifest entries to sizes and SHA256 checksums. The secured loader verifies allowed repository-relative paths, serializer, schema references, and checksum before deserialization. Task 2B uses optimization, not a trained predictive model.

## 5. Verify output contracts without opening rows

The official filenames and columns are:

- `submission_task1.csv`: `delivery_id`, `pred_service_min`, `pred_late_prob`;
- `submission_task2a.csv`: `row_id`, `pred_total_volume_m3`, `pred_chilled_volume_m3`;
- `submission_task2b.csv`: `scenario`, `order_ref`, `outlet_id`, `decision`, `vehicle_id`, `trip_id`.

Read [final submission validation](final_submission_validation.md) for the read-only Phase 33 gates. Do not display CSV contents. The organizer Task 2B checker proves feasibility only, not optimality.

## 6. Review Task 2B reasoning

Read the [Task 2B prioritization policy](task2b_policy.md). It separates official hard feasibility from WayLoom's lexicographic service priorities, applies the no-return-leg trip formula, and explains deferral impact without inventing monetary cost.

## 7. Review reproducibility and tests

Read [reproducibility notes](reproducibility.md), then run the safe synthetic/documentation checks from the README. Seed 42 and the reference dependency snapshot improve repeatability; protected artifact/output hashes are the release-integrity baseline. Clean-environment reproduction remains pending Phase 39.

## 8. Review disclosure and pending deliverables

Read the [AI-use disclosure](AI_USE_DISCLOSURE.md) with its current status intact. Phase 35 remains open pending factual approval and independent review. Results evidence is pending Phase 37, the unlisted demo video is pending Phase 38, and final folder/ZIP/upload actions are pending Phases 40–42.

The Phase 36 documentation implementation itself remains open until a fresh read-only independent review issues eight separate DT-456–DT-463 verdicts and a later authorized administrative update changes the master-plan flags.

