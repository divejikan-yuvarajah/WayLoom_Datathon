# WayLoom Datathon Official Requirements Checklist

**Phase:** 00  
**Status convention:** `[ ]` not verified, `[x]` verified, `[!]` blocked  
**Scope:** Documentation only; no raw competition data was accessed.

Every row below is an official requirement or a direct official-artifact check. Internal implementation recommendations are marked `[E]` and are not presented as organizer requirements.

| Status | Requirement ID | Requirement | Official source | Future owner |
|---|---|---|---|---|
| [x] | REQ-GEN-001 | Datathon is judged separately from Hackathon; integration is not required | Booklet p. 15 | DT-002 / Phase 00 |
| [x] | REQ-GEN-002 | Datathon has Task 1, Task 2A, and Task 2B | Booklet pp. 15–18 | DT-002 / Phase 00 |
| [x] | REQ-T1-001 | Predict `pred_service_min` for every planned test `delivery_id` | Booklet pp. 15–16 | DT-003 / Phases 04, 10 |
| [x] | REQ-T1-002 | Predict `pred_late_prob` in `[0,1]` | Booklet pp. 15–16 | DT-003 / Phase 10 |
| [x] | REQ-T1-003 | Construct labels from historical actual route records | Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-004 | Early arrival waits until window opening | Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-005 | `service_start = max(actual_arrival_time, window_open_time)` | Internal freeze consistent with Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-006 | `service_min = leave_outlet_time - service_start` | Internal freeze consistent with Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-007 | Late means actual arrival strictly after window close | Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-008 | Arrival exactly at window close is not late | Strict-after interpretation of Booklet p. 15 | DT-003 / Phase 04 |
| [x] | REQ-T1-009 | Actual future journey/handling fields cannot be prediction-time features | Booklet p. 15 | DT-003 / Phase 06 |
| [x] | REQ-T1-010 | Preserve every Task 1 `delivery_id` and original row order | Booklet pp. 16, 25 | DT-003/007 / Phase 10 |
| [x] | REQ-T1-011 | Fill only Task 1 prediction columns; do not add/remove rows | Booklet p. 16 | DT-007 / Phase 10 |
| [x] | REQ-T1-012 | Task 1 schema is `delivery_id`, `pred_service_min`, `pred_late_prob` | Booklet p. 16 | DT-007 / Phase 10 |
| [x] | REQ-T2A-001 | Forecast total and chilled volume by depot, brand, and future week | Booklet pp. 16–17 | DT-004 / Phase 17 |
| [x] | REQ-T2A-002 | Build history from both `deliveries_train.csv` and `task1_test_inputs.csv` | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-003 | Count every unique order once | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-004 | Attempted orders represent demand | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-005 | Deferred orders represent demand | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-006 | `not_run` orders represent demand | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-007 | Use requested `order_date`, not `dispatch_date` | Booklet p. 17 plus column definitions p. 26 | DT-004 / Phase 11 |
| [x] | REQ-T2A-008 | Use calendar `iso_year` and `iso_week` | Booklet p. 17 | DT-004 / Phase 11 |
| [x] | REQ-T2A-009 | Style chilled prediction is exactly zero | Booklet p. 17 | DT-004 / Phase 17 |
| [x] | REQ-T2A-010 | Tech chilled prediction is exactly zero | Booklet p. 17 | DT-004 / Phase 17 |
| [x] | REQ-T2A-011 | Output is volume, not vehicle/driver count | Booklet p. 16 | DT-004 / Phase 17 |
| [x] | REQ-T2A-012 | Preserve supplied `row_id` values | Booklet p. 17 | DT-007 / Phase 17 |
| [x] | REQ-T2A-013 | Task 2A schema is `row_id`, `pred_total_volume_m3`, `pred_chilled_volume_m3` | Booklet p. 17 | DT-007 / Phase 17 |
| [x] | REQ-T2B-001 | Scenario is S1 | Booklet p. 18 | DT-005 / Phase 18 |
| [x] | REQ-T2B-002 | Scenario depot is Peliyagoda | Booklet p. 18 | DT-005 / Phase 18 |
| [x] | REQ-T2B-003 | Use only vehicles marked available | Booklet p. 18 | DT-005 / Phase 18 |
| [x] | REQ-T2B-004 | Do not use in-workshop vehicles | Booklet p. 18 | DT-005 / Phase 18 |
| [x] | REQ-T2B-005 | Use `order_ref` as allocation key | Booklet p. 19 | DT-005 / Phase 22 |
| [x] | REQ-T2B-006 | Every order is served or deferred | Booklet pp. 18–19 | DT-005 / Phase 24 |
| [x] | REQ-T2B-007 | Served orders receive vehicle and trip | Booklet p. 19 | DT-005 / Phase 24 |
| [x] | REQ-T2B-008 | Deferred orders have blank vehicle/trip fields | Booklet p. 19 | DT-005 / Phase 24 |
| [x] | REQ-T2B-009 | Same brand and district per trip | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-010 | Chilled requires reefer | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-011 | `van_only` requires van | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-012 | Home-depot restriction | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-013 | Whole orders only | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-014 | Enforce both weight and volume capacity | Booklet p. 20 | DT-005 / Phase 22 |
| [x] | REQ-T2B-015 | Maximum two trips per vehicle | Booklet pp. 20–21 | DT-005/006 / Phase 22 |
| [x] | REQ-T2B-016 | Fresh total per vehicle is at most 270 minutes | Booklet p. 21 | DT-006 / Phase 22 |
| [x] | REQ-T2B-017 | Style + Tech combined per vehicle is at most 480 minutes | Booklet p. 21 | DT-006 / Phase 22 |
| [x] | REQ-T2B-018 | Use exact official trip formula | Booklet pp. 20–21 | DT-006 / Phase 20 |
| [x] | REQ-T2B-019 | Do not add return-to-depot travel | Booklet p. 20 | DT-006 / Phase 20 |
| [x] | REQ-T2B-020 | `submission_task2b.csv` preserves scenario/order_ref/outlet_id | Booklet pp. 18–19 | DT-007 / Phase 24 |
| [x] | REQ-T2B-021 | Replace all placeholders | Booklet p. 19 | DT-007 / Phase 24 |
| [x] | REQ-T2B-022 | Submit written prioritization policy | Booklet p. 21 | DT-005 / Phase 24 |
| [x] | REQ-T2B-023 | Checker establishes feasibility, not optimality | Booklet p. 31 and checker artifact | DT-005 / Phase 23 |
| [x] | REQ-REST-001 | No prohibited pretrained models | Booklet p. 22 | DT-008 / Phase 35 |
| [x] | REQ-REST-002 | No proprietary API modelling/preprocessing | Booklet p. 22 | DT-008 / Phase 35 |
| [x] | REQ-REST-003 | No low-code/no-code or fully automated end-to-end modelling | Booklet p. 22 | DT-008 / Phase 35 |
| [x] | REQ-REST-004 | Use supplied data only for this competition | Booklet p. 22 | DT-008 / Phases 01, 40 |
| [x] | REQ-REST-005 | Do not share/distribute/transmit datasets or derivatives | Booklet p. 22 | DT-008 / Phases 01, 40 |
| [x] | REQ-REST-006 | Do not publish/disclose datasets or derivatives without authorization | Booklet p. 22 | DT-008 / Phase 40 |
| [x] | REQ-REST-007 | Maintain confidentiality and integrity | Booklet p. 22 | DT-008 / Phases 01, 35 |
| [x] | REQ-REST-008 | Provide AI-tool disclosure | Booklet p. 22 | DT-008 / Phase 35 |
| [x] | REQ-SUB-001 | Provide architecture diagrams | Booklet p. 22 | DT-010 / Phase 29 |
| [x] | REQ-SUB-002 | Provide preprocessing document | Booklet p. 22 | DT-010 / Phase 30 |
| [x] | REQ-SUB-003 | Save final model files | Booklet p. 22 | DT-010 / Phase 32 |
| [x] | REQ-SUB-004 | Provide `TeamName_FinalNotebook.ipynb` | Booklet p. 22 | DT-010 / Phase 31 |
| [x] | REQ-SUB-005 | Retain label/preprocessing/training/evaluation notebook cells | Booklet p. 22 | DT-010 / Phase 31 |
| [x] | REQ-SUB-006 | Final notebook loads saved models and prints Task 1/2A inference | Booklet p. 22 | DT-010 / Phase 31 |
| [x] | REQ-SUB-007 | Provide all three official CSVs | Booklet pp. 22, 25 | DT-007 / Phases 10, 17, 24 |
| [x] | REQ-SUB-008 | Provide Task 2B written policy | Booklet p. 21 | DT-010 / Phase 24 |
| [x] | REQ-SUB-009 | Provide unlisted 3–5 minute demo | Booklet p. 22 | DT-010 / Phase 38 |
| [x] | REQ-SUB-010 | Compress final folder as `TeamName_Datathon.zip` | Booklet p. 23 | DT-010 / Phase 42 |
| [x] | REQ-SCORE-001 | Data wrangling and label construction = 20% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-SCORE-002 | Model and architecture implementation = 25% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-SCORE-003 | Task 1/Task 2A performance = 20% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-SCORE-004 | Task 2B feasibility and policy = 15% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-SCORE-005 | Creativity = 10% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-SCORE-006 | Demo video = 10% | Booklet p. 23 | DT-009 / Phase 37 |
| [x] | REQ-DEAD-001 | Official deadline is 9 October 2026, 11:59 PM Sri Lanka time | Booklet p. 23 | DT-010 / Phase 42 |

## Tool-use decision table

| Activity | Officially permitted? | Phase 00 action |
|---|---|---|
| Read official documentation | Yes | Proceed |
| Read/process raw CSVs for later Datathon work | Outside Phase 00 scope | Defer to Phase 02 |
| Send raw competition rows to an external AI/API service | Prohibited or ambiguous under confidentiality rules | STOP and seek organizer clarification |
| Use a prohibited pretrained model | No | Do not use |
| Use proprietary API modelling/preprocessing | No | Do not use |
| Use low-code/no-code end-to-end modelling | No | Do not use |
| Use AI coding assistance with no raw data disclosure and full disclosure | Internal engineering workflow; disclose use | Record in AI disclosure |

## Phase 00 acceptance

- [x] DT-000 — official rules mapped.
- [x] DT-001 — checklist created.
- [x] DT-002 — three problems separated.
- [x] DT-003 — Task 1 target contract frozen.
- [x] DT-004 — Task 2A demand contract frozen.
- [x] DT-005 — Task 2B feasibility contract frozen.
- [x] DT-006 — trip formula and budgets frozen.
- [x] DT-007 — submission schemas frozen.
- [x] DT-008 — restrictions recorded.
- [x] DT-009 — judging criteria recorded.
- [x] DT-010 — deadline and team-target schedule recorded.

