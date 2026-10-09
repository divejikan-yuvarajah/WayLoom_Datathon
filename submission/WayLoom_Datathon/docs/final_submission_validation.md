# Phase 33 final submission validation

Phase 33 is a read-only gate over the three frozen official CSVs. It does not train models, regenerate predictions, optimize Task 2B, normalize values, sort rows, or repair failures.

The validator reads each CSV twice conceptually: the raw CSV representation proves headers, field counts, true blank fields, exact identifiers and textual Task 2B formatting; numeric parsing proves finite/range/invariant checks. Official templates and Task 2A brand lookup data are resolved from `configs/dataset_manifest.yaml`. No real identifiers or rows are printed.

Task 2B first passes the independent Phase 23 feasibility validator on the exact final CSV, then the existing inspected organizer-checker adapter invokes `check_allocation.py` with that same final path. Organizer-checker PASS means feasibility only, never optimality.

The script hashes all three submissions before and after every validation/checker step and fails if any byte changes. Aggregate evidence is written only under the ignored private report directory.

Human-local command:

```powershell
.\.venv\Scripts\python.exe scripts\validate_final_submissions.py --config configs\final_submission_validation.yaml --dataset-manifest configs\dataset_manifest.yaml --submission-dir outputs --report-dir reports\private\phase33_final_submissions
```

Failures are routed upstream: DT-420-DT-426 to Phase 10, DT-427-DT-432 to Phase 17, DT-433-DT-436 to Phase 24, checker bridge failures to Phase 23/33, and real feasibility failures to the Phase 22-24 chain. Phase 33 never auto-fixes a frozen submission.
