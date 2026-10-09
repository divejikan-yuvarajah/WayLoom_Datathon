# Phase 37 Results Evidence Index

> **Status:** Prepared for fresh independent review. Phase 37 is not formally closed.  
> **Safety boundary:** This index references tracked repository sources only. It contains no private rows, real identifiers, executed-notebook output, or confidential forecast values. It and the linked results summary are internal drafts, not approved public or demo assets. An unlisted video is accessible to anyone with its link.

## Provenance levels

| Level | Meaning |
|---|---|
| `OFFICIAL_RULE` | Verified competition requirement; not measured performance. |
| `REPO_VERIFIED` | Tracked source/configuration/documentation inspected; describes implementation or method. |
| `SAFE_TEST_RUN` | Synthetic/documentation checks executed during implementation; not an independent review or private-data result. |
| `HUMAN_LOCAL_REPORTED` | Sanitized result reported from an authorized local run; not rerun here. |
| `TRACKED_INTERNAL_AGGREGATE` | A non-row-level aggregate in a tracked source; its presence does **not** establish publication approval. |
| `SANITIZED_AGGREGATE_APPROVED` | Exact aggregate and audience have explicit owner approval to disclose, with provenance recorded. No Phase 37 result currently has this status. |
| `UNVERIFIED` | Evidence is missing or not approved for this package; report `NOT AVAILABLE`. |

## Evidence catalog

| ID | Source | Scope | Level |
|---|---|---|---|
| E-P37-001 | `MD Files/Challenge Booklet.pdf`, Datathon printed pp. 15–25 | Official Task 1, Task 2A, Task 2B, deliverables and judging rules | `OFFICIAL_RULE` |
| E-P37-002 | `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`, Phase 37 | Exact DT-464–DT-474 inventory and phase gate | `REPO_VERIFIED` |
| E-P37-003 | `configs/task1_validation.yaml` | Task 1 chronological split and metric contract | `REPO_VERIFIED` |
| E-P37-004 | `configs/task1_final_models.yaml` | Frozen Task 1 model families/calibration policy | `REPO_VERIFIED` |
| E-P37-005 | `docs/task1_label_spec.md` | Service/late definitions and leakage boundary | `REPO_VERIFIED` |
| E-P37-006 | `docs/task1_explainability.md` | Tracked global SHAP feature rankings and caveats; public/demo approval pending | `TRACKED_INTERNAL_AGGREGATE` |
| E-P37-007 | `configs/task2a_validation.yaml` and `docs/task2a_validation_spec.md` | Four-origin, ten-week rolling validation and metric definitions | `REPO_VERIFIED` |
| E-P37-008 | `configs/task2a_final_models.yaml` and `docs/task2a_final_inference_spec.md` | Frozen ensembles and output constraints | `REPO_VERIFIED` |
| E-P37-009 | `docs/task2b_policy.md` | Frozen allocation aggregate outcomes, scarcity and policy; public/demo approval pending | `TRACKED_INTERNAL_AGGREGATE` |
| E-P37-010 | `docs/task2b_validation_spec.md` | Independent-validator and official-checker semantics | `REPO_VERIFIED` |
| E-P37-011 | `MD Files/PHASE_33_COMPETITION_CONTRACT.md`, final completion record | Human-local Phase 33 checker execution and recorded PASS; not rerun during Phase 37 | `HUMAN_LOCAL_REPORTED` |
| E-P37-012 | `docs/AI_USE_DISCLOSURE.md` and `docs/PHASE35_ORGANIZER_COMMUNICATION_RECORD.md` | Truthful AI/data-sharing history and incident-specific organizer guidance | `REPO_VERIFIED` |
| E-P37-013 | `configs/phase37_results_evidence.yaml` | Machine-readable Phase 37 claim/task manifest | `REPO_VERIFIED` |
| E-P37-014 | `tests/test_phase37_results_evidence.py` | Synthetic semantic, mutation, privacy and traceability tests | `SAFE_TEST_RUN` |
| E-P37-015 | `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`, Phase 33 closure note | Independently reviewed Phase 33 closure and readiness record | `REPO_VERIFIED` |

## Exact task traceability

| Task | Exact master work item | Evidence | Implemented result | Verdict before independent review |
|---|---|---|---|---|
| DT-464 | Produce final Task 1 metrics table | E-P37-003, 005, 013 | Defined table with unavailable values explicitly labelled | `PREP_ONLY` |
| DT-465 | Compare Task 1 baseline vs final model | E-P37-003, 004, 013 | Candidate/final families recorded; numerical comparison unavailable | `PREP_ONLY` |
| DT-466 | Produce calibration visualization | E-P37-003, 005, 013 | Safe chart specification; bin data unavailable | `BLOCKED` |
| DT-467 | Produce Task 1 feature explanation | E-P37-006, 013 | Tracked feature rankings and caveats summarized; publication approval pending | `PREP_ONLY` |
| DT-468 | Produce Task 2A backtesting results | E-P37-007, 013 | Protocol/result schema recorded; values unavailable | `PREP_ONLY` |
| DT-469 | Compare Task 2A baselines/final model | E-P37-007, 008, 013 | Frozen ensemble choice recorded; numerical comparison unavailable | `PREP_ONLY` |
| DT-470 | Produce future-demand chart | E-P37-008, 013 | Safe chart specification; approved series unavailable | `BLOCKED` |
| DT-471 | Produce Task 2B scarcity summary | E-P37-009, 013 | Complete internal aggregate scarcity table; public approval pending | `PREP_ONLY` |
| DT-472 | Produce served/deferred summary | E-P37-009, 013 | Complete internal served/deferred and impact aggregates; public approval pending | `PREP_ONLY` |
| DT-473 | Produce solver/checker evidence | E-P37-010, E-P37-011, E-P37-015 | Human-local execution, recorded PASS and independently reviewed closure distinguished | `PASS_CANDIDATE` |
| DT-474 | Select only strongest charts for demo | E-P37-006, 009, 013 | No Phase 37 result asset publicly selected while approval is pending | `PREP_ONLY` |

`PASS_CANDIDATE` is an implementation assessment, not a master checkbox or independent-review verdict. Formal Phase 37 closure remains pending.

## Numerical claim register

`configs/phase37_results_evidence.yaml` is the authoritative Phase 37 numerical-claim register. The table below is a human-readable mirror that the tests compare field-for-field against the YAML. Every entry is sourced from E-P37-009 using the calculation or extraction recorded in the YAML, is classified `internal competition evidence only`, has publication approval `PENDING`, and is **not selected for public release**. A tracked source alone is not treated as publication permission. Task 1/2A result values remain deliberately absent.

| Claim ID | Definition | Value | Unit | Population |
|---|---|---:|---|---|
| N-T2B-001 | served whole orders | 79 | orders | all 85 Scenario S1 orders |
| N-T2B-002 | total Scenario S1 orders | 85 | orders | all Scenario S1 orders |
| N-T2B-003 | deferred whole orders | 6 | orders | all 85 Scenario S1 orders |
| N-T2B-004 | served share rounded to one decimal place | 92.9 | percent | all 85 Scenario S1 orders |
| N-T2B-005 | deferred share rounded to one decimal place | 7.1 | percent | all 85 Scenario S1 orders |
| N-T2B-006 | total outcome share | 100.0 | percent | all 85 Scenario S1 orders |
| N-T2B-007 | usable home-depot vehicles | 28 | vehicles | Scenario S1 home-depot fleet after availability filtering |
| N-T2B-008 | usable reefers | 4 | vehicles | usable Scenario S1 home-depot vehicles |
| N-T2B-009 | usable reefer vans | 1 | vehicles | usable Scenario S1 home-depot vehicles |
| N-T2B-010 | workshop-unavailable vehicles | 10 | vehicles | listed Scenario S1 vehicles |
| N-T2B-011 | used trip slots | 44 | trip slots | frozen Scenario S1 allocation |
| N-T2B-012 | theoretical trip slots | 56 | trip slots | 28 usable vehicles at no more than two trips each |
| N-T2B-013 | peak Fresh vehicle time | 268 | minutes | vehicles assigned Fresh trips in the frozen Scenario S1 allocation |
| N-T2B-014 | Fresh vehicle time limit | 270 | minutes | combined Fresh trips per vehicle |
| N-T2B-015 | peak Style plus Tech vehicle time | 183 | minutes | vehicles assigned Style or Tech trips in the frozen Scenario S1 allocation |
| N-T2B-016 | Style plus Tech vehicle time limit | 480 | minutes | combined Style and Tech trips per vehicle |
| N-T2B-017 | peak trip weight loading | 99.2 | percent | trips in the frozen Scenario S1 allocation |
| N-T2B-018 | peak trip volume loading | 99.7 | percent | trips in the frozen Scenario S1 allocation |
| N-T2B-019 | deferred orders with no compatible available vehicle | 1 | orders | six deferred Scenario S1 orders |
| N-T2B-020 | deferred orders with an individually compatible vehicle but allocation tradeoffs | 5 | orders | six deferred Scenario S1 orders |
| N-T2B-021 | previously deferred orders | 10 | orders | Scenario S1 orders marked previously deferred |
| N-T2B-022 | previously deferred orders served | 9 | orders | ten previously deferred Scenario S1 orders |
| N-T2B-023 | previously deferred orders still deferred | 1 | orders | ten previously deferred Scenario S1 orders |
| N-T2B-024 | deferred Fresh orders | 5 | orders | six deferred Scenario S1 orders |
| N-T2B-025 | deferred Style orders | 1 | orders | six deferred Scenario S1 orders |
| N-T2B-026 | outlets affected by deferral | 6 | outlets | six deferred Scenario S1 orders |
| N-T2B-027 | deferred demand units | 1188 | units | six deferred Scenario S1 orders |
| N-T2B-028 | deferred demand weight | 9770.9 | kg | six deferred Scenario S1 orders |
| N-T2B-029 | deferred demand volume | 81.57 | m3 | six deferred Scenario S1 orders |
| N-T2B-030 | chilled deferred orders | 5 | orders | six deferred Scenario S1 orders |
| N-T2B-031 | chilled deferred volume | 40.91 | m3 | five chilled deferred Scenario S1 orders |
| N-T2B-032 | mean deferred-order wait | 2 | days | six deferred Scenario S1 orders |
| N-T2B-033 | maximum deferred-order wait | 5 | days | six deferred Scenario S1 orders |

## Missing evidence register

On 2026-10-09, the team representative stated that an existing **approved aggregate-only** Task 1/Task 2A evidence record could not be confirmed and that no explicit owner approval had been given to publish/show the Task 1 SHAP explanation or Task 2B numerical claims in the demo. This confirms the current approval gap; it does not prove that no historical private evaluation exists. A metadata-only search of the explicit non-private `docs/`, `configs/` and `MD Files/` trees found no candidate with an exact publication-approval record. Private reports were not opened or searched. No score, chart or release permission is inferred from this search.

| Missing evidence | Affected tasks | Required before reporting a number/chart |
|---|---|---|
| Approved Task 1 metric aggregates with split/source provenance | DT-464, DT-465 | Authorized sanitized aggregate artifact; exact metrics, units, split, coverage and approval |
| Approved Task 1 reliability bins | DT-466 | Authorized bin counts, predicted means, observed late rates and split provenance |
| Approved Task 2A backtest aggregates | DT-468, DT-469 | Authorized rolling-origin aggregate artifact with horizon/target/series coverage |
| Approved public Task 2A forecast series | DT-470 | Authorized aggregate values and audience approval; never derive them from the official submission here |
| Owner publication approval for Task 1 SHAP and Task 2B aggregates | DT-467, DT-471, DT-472, DT-474 | Named owner, exact approved claim/asset IDs, approved audience, approval time and source record |

## Authorized local aggregate handoff procedure

If an authorized human operator elects to release currently unavailable evidence, the extraction stays entirely local and must not expose private rows, identifiers, labels, predictions, notebooks or source files to an external AI service.

1. Use the already frozen evaluation split and production metric functions; do not retrain, retune or evaluate against organizer test data without ground truth.
2. Produce a local aggregate-only record. Task 1 requires metric name, value, unit, target, positive-class definition, split/fold coverage, sample count and calculation version. Calibration additionally requires bin edges, counts, mean predicted probabilities and observed late rates. Task 2A requires target, value, m3 unit, rolling origins, horizons, series coverage and aggregation method.
3. A human reviewer confirms that the aggregate cannot reveal rows, identifiers, confidential forecast values or unsafe small subgroups.
4. The evidence owner records the exact approved claim/asset IDs, audience, approval decision, timestamp and approval-record path. Until this happens, publication status remains `PENDING` and `selected_for_public_release` remains false.
5. Add the sanitized local artifact to the evidence catalog and run the structured consistency/mutation tests before changing any `NOT AVAILABLE` value or selecting a chart.

## Interpretation safeguards

- Service time is in minutes and excludes early waiting; lateness is strictly after window close.
- Task 2A uses requested-date ISO weeks, counts each official order once across both sources, and fails closed on cross-source duplicates.
- Style and Tech chilled values are structural zeros, not model-achievement evidence.
- Task 2B trip time excludes a depot return; Fresh and Style+Tech combined limits are 270 and 480 minutes, with no more than two trips per vehicle.
- Official checker PASS means feasibility under implemented rules, not global optimality or judge score.
- The Phase 35 organizer response is represented only for the disclosed incident and is not a blanket waiver.
