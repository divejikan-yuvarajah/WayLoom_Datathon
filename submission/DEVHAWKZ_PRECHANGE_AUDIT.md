# DevHawkz submission identity correction: pre-change audit

Recorded 2026-10-09 before building the DevHawkz package. This is a local release audit outside both ZIP files. The authorized representative confirmed **DevHawkz** as the registered team and **WayLoom** as the project. No separate local organizer registration record establishing a conflicting registered team name was found in the submission-facing repository material.

## Previous draft

- Folder: `submission/WayLoom_Datathon/`
- ZIP: `submission/WayLoom_Datathon.zip`
- ZIP SHA256: `949db58149522b6c956eadb3cd4413f1ecd6b7e94541647791341884d9c28319`
- ZIP size: `4,134,863` bytes; `175` file members under `WayLoom_Datathon/`
- Staging manifest: `submission/WayLoom_Datathon/SUBMISSION_MANIFEST.sha256`, SHA256 `c387deb9ddf5243955b94a1f88b58a5637bd44b4608d52256c2ed9d5a4a59134`, covering `174` other files

The previous draft is retained as historical packaging evidence. Its name and notebook filename are superseded by the new team identity.

## Protected source baseline

| Path | SHA256 | Size (bytes) |
|---|---|---:|
| `outputs/submission_task1.csv` | `9e0faa83a8dd1401ebaf72f1b1602dc560049d4a0cfba19676dbb69bf0de7918` | 255029 |
| `outputs/submission_task2a.csv` | `142842eef5e4a2e7a6db450c19f4062e4a6eb065481aa21720b59556f9edd55d` | 2104 |
| `outputs/submission_task2b.csv` | `15f98c8abc434811bc8d6db6ce64c4a746d0acd401f9147d7b15c0958d62b431` | 2918 |
| `models/artifact_registry.json` | `eb1491b782f835cd7ec5046980d3ea234c9a69e68e006a4eef885f1feef5c82d` | 14172 |
| `TeamName_FinalNotebook.ipynb` | `da7127bba73e6537631b281a70dcc17fad70f5ded5261a4ddfb624b11917f021` | 41363 |
| `docs/AI_USE_DISCLOSURE.md` | `715c2dca328a6792adffad5073633fcd7e362272578dbed788a8179418b6d4d3` | 19485 |
| `docs/PHASE35_FINAL_HUMAN_APPROVAL_CHECKLIST.md` | `ef448b08c5666ef691039e077e96dbae4c9f9c1b7435e4979978a2c0dc0e3c79` | 7486 |

All `12/12` artifacts in the registry matched their expected SHA256 and sizes before the change.

## Original Git state

Branch: `test/phase-33-final-submissions` tracking `origin/test/phase-33-final-submissions`. Staged diff: empty.

Tracked modifications: `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`, `tests/test_phase36_documentation.py`.

Pre-existing untracked paths: `MD Files/PHASE_35_COMPETITION_CONTRACT.md`, `MD Files/PHASE_35_DT455_NARROW_REREVIEW_PROMPT.txt`, `MD Files/PHASE_35_INDEPENDENT_REVIEW_PROMPT.txt`, `MD Files/PHASE_37_COMPETITION_CONTRACT.md`, three `MD Files/WAYLOOM_PHASE35_*` draft/prompt files, `configs/phase37_results_evidence.yaml`, six Phase 35 documents under `docs/`, `docs/RESULTS_EVIDENCE_INDEX.md`, `docs/RESULTS_SUMMARY.md`, `submission/`, `tests/test_ai_use_disclosure.py`, and `tests/test_phase37_results_evidence.py`.

These existing changes are preserved. The submitted package is assembled from an explicit allowlist rather than by staging the development repository.
