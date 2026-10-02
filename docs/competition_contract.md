# WayLoom Datathon Competition Contract

**Phase:** 00 — Competition Understanding & Scope Freeze  
**Status:** Frozen for Phase 00  
**Authority:** Official Rootcode Tech-Triathlon 2026 Challenge Booklet and official competition artifacts  
**Internal guidance:** `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` and WayLoom Product & Competition Master Plan

## 1. Authority and conflict handling

Source priority:

1. Official organizer clarification, if issued.
2. Official Rootcode Tech-Triathlon 2026 Challenge Booklet.
3. Official supplied templates and validation artifacts.
4. WayLoom Product & Competition Master Plan.
5. WayLoom Datathon Master Plan and phase guides.

Official requirements override internal guidance. Conflicts must be recorded; they must not be silently reconciled.

This document is documentation-only. It does not authorize data processing, model training, notebook creation, API work, optimization, or prediction generation.

## 2. Problem decomposition

The Datathon is judged separately from the Hackathon. Datathon-to-Hackathon integration is optional and is not a submission dependency.

| Task | Official problem | Required output | Nature |
|---|---|---|---|
| Task 1 | Predict outlet service time and lateness | `pred_service_min`, `pred_late_prob` for each test `delivery_id` | Two-target prediction |
| Task 2A | Forecast depot/brand demand for 10 future weeks | Total and chilled volume in m³ | Demand forecasting |
| Task 2B | Allocate the S1 peak-day fleet | Served/deferred allocation plus written policy | Feasibility and prioritization; no trained model required |

## 3. Task 1 contract [O]

**Official meaning:**

- `pred_service_min` is predicted handling/service time at the outlet, in minutes.
- `pred_late_prob` is the probability that arrival is after the outlet delivery window closes, from 0 to 1.
- Historical actual route records are used to construct training labels.
- Early arrival waits until the delivery window opens.
- Actual future journey and handling fields are unavailable at prediction time and must not become prediction features.

**Frozen label definitions:**

```text
service_start = max(actual_arrival_time, window_open_time)
service_min   = leave_outlet_time - service_start
late_flag     = 1 if actual_arrival_time > window_close_time else 0
```

Boundary rules:

- Arrival before opening: service starts at `window_open_time`.
- Arrival after opening and at/before close: service starts at actual arrival.
- Arrival exactly at close: `late_flag = 0`.
- Arrival strictly after close: `late_flag = 1`.

Submission preservation:

- Preserve every supplied `delivery_id`.
- Preserve the original Task 1 row order.
- Do not add or remove rows.
- Fill only the prediction columns.

Required Task 1 schema:

| Column | Required value |
|---|---|
| `delivery_id` | Supplied identifier, unchanged |
| `pred_service_min` | Numeric predicted service minutes |
| `pred_late_prob` | Numeric probability in `[0, 1]` |

## 4. Task 2A contract [O]

Predict volume for every supplied depot, brand, and future-week combination:

- `pred_total_volume_m3`
- `pred_chilled_volume_m3`

Mandatory demand accounting:

1. Build history from both `deliveries_train.csv` and `task1_test_inputs.csv`.
2. Count each unique order once.
3. Count `attempted`, `deferred`, and `not_run` orders as demand.
4. Use requested `order_date`, not `dispatch_date`.
5. Join `calendar.csv` and use `iso_year` and `iso_week`.
6. Only Fresh has chilled demand.
7. Style chilled prediction must be exactly `0`.
8. Tech chilled prediction must be exactly `0`.
9. The task output is volume, not vehicle or driver count.
10. Preserve supplied `row_id` values.

The requested-week interpretation is an internal freeze of the booklet’s wording because the booklet defines `order_date` as the date the store’s order was for. If an official clarification names another field, that clarification wins.

Required Task 2A schema:

| Column | Required value |
|---|---|
| `row_id` | Supplied identifier, unchanged |
| `pred_total_volume_m3` | Predicted total ordered volume |
| `pred_chilled_volume_m3` | Chilled volume; exactly zero for Style and Tech |

## 5. Task 2B contract [O]

Scenario scope:

- Scenario: `S1`
- Depot: Peliyagoda
- Use only vehicles marked `available`.
- Do not use vehicles marked `in_workshop`.
- Use `order_ref` as the allocation key.
- Every order is `served` or `deferred`.
- Served orders receive `vehicle_id` and `trip_id` 1 or 2.
- Deferred orders have blank `vehicle_id` and `trip_id`.

### Seven hard feasibility rules

1. Every `vehicle_id` + `trip_id` group has one brand and one district.
2. `chilled` orders require a reefer; a reefer may carry ambient goods.
3. `van_only` outlets require a van.
4. A vehicle may serve only its home depot’s outlets.
5. A served order is whole and assigned to one vehicle and one trip.
6. Every trip satisfies both weight and volume capacity.
7. Each vehicle runs at most two trips and satisfies the category time budgets.

Time budgets:

- Fresh total minutes per vehicle: `<= 270`.
- Style + Tech combined minutes per vehicle: `<= 480`.
- Maximum total trips per vehicle: `2`.

### Official trip formula

```text
trip_minutes =
    depot_to_district_freeflow_min
  + inter_stop_freeflow_min * (number_of_orders - 1)
  + sum(service_allowance_min)
```

- Count outbound depot-to-district travel once per trip.
- A one-order trip has zero inter-stop travel.
- Look up service allowance by brand and dock type.
- Do **not** add return-to-depot travel; the budgets already allow for it.

The official booklet’s worked example is a three-stop Fresh trip to Gampaha:

```text
37 + (9 * 2) + 15 + 15 + 16 = 101 minutes
```

`check_allocation.py` verifies feasibility, not optimality. The official template requires lowercase `served` / `deferred`, and deferred vehicle/trip fields must be blank.

Required Task 2B schema:

| Column | Required value |
|---|---|
| `scenario` | Supplied scenario, `S1` |
| `order_ref` | Supplied allocation key, unchanged |
| `outlet_id` | Supplied identifier, unchanged |
| `decision` | `served` or `deferred` |
| `vehicle_id` | Required for served; blank for deferred |
| `trip_id` | `1` or `2` for served; blank for deferred |

The written policy must explain calculations, limiting resources, unavoidable deferrals, policy-choice deferrals, and their cost/impact.

## 6. Restrictions and data confidentiality [O]

- No pretrained models, except the organizer’s stated exception for synthetic-data generation or preprocessing.
- No proprietary API-based modelling or preprocessing.
- No low-code/no-code AI tools or fully automated end-to-end modelling tools.
- Competition data may be used only for this competition.
- Do not share, distribute, transmit, publish, or disclose competition datasets or derivatives without organizer authorization.
- Maintain confidentiality.
- Cheating, plagiarism, or rule violations can result in disqualification.
- Maintain an accurate AI-tool disclosure.

**WayLoom operating rule [E]:** Do not place raw competition rows or private derivatives into prompts, public repositories, external services, or public demonstrations. If a workflow is ambiguous, stop and seek organizer clarification.

## 7. Required final deliverables [O]

- Architecture diagrams showing models, preprocessing, and proposed deployment.
- Data preprocessing document covering preparation, labels, cleaning, features, and rationale.
- Saved final model files.
- `TeamName_FinalNotebook.ipynb`.
- Notebook cells for label construction, preprocessing, training, and evaluation.
- A final notebook cell that loads saved models, demonstrates Task 1 and Task 2A inference, and prints inputs and predictions.
- `submission_task1.csv`.
- `submission_task2a.csv`.
- `submission_task2b.csv`.
- Task 2B written prioritization policy.
- AI-tool disclosure.
- Unlisted 3–5 minute demo video explaining architecture, preprocessing, labels, and challenges.
- Final `TeamName_Datathon.zip`.

## 8. Judging criteria [O]

| Criterion | Weight |
|---|---:|
| Data wrangling and label construction | 20% |
| Model and architecture implementation | 25% |
| Performance score — Task 1 and Task 2A | 20% |
| Task 2B allocation feasibility and prioritization policy | 15% |
| Creativity | 10% |
| Demo video | 10% |
| **Total** | **100%** |

Any statement about prioritizing work beyond these weights is WayLoom engineering guidance, not an organizer rule.

## 9. Official deadline [O]

**Friday, 9 October 2026 at 11:59 PM Sri Lanka time (Asia/Colombo, UTC+05:30).**

This is the only organizer deadline in this contract. All other dates must be labelled `TEAM TARGET`.

## 10. Official source map

| Contract area | Official source |
|---|---|
| Datathon separation and Task 1 | Challenge Booklet pp. 15–16 |
| Task 2A | Challenge Booklet pp. 16–17 |
| Task 2B scenario and outputs | Challenge Booklet pp. 18–19 |
| Task 2B feasibility and formula | Challenge Booklet pp. 19–21 |
| Restrictions and deliverables | Challenge Booklet pp. 22–23 |
| Data and template conventions | Challenge Booklet pp. 24–31 |
| Feasibility checker behavior | Official `check_allocation.py` artifact |
| Algebraic Task 1 formula freeze | WayLoom internal guidance, consistent with booklet semantics |

## 11. Phase 00 conflict register

1. The booklet describes Task 1 semantics but does not print the algebraic equations. The equations above are the WayLoom internal freeze consistent with those semantics. Official clarification overrides them.
2. The booklet says to use the week the store requested the order; the internal mapping to `order_date` follows the booklet’s column definition. Official clarification overrides it.
3. The booklet has prose capitalization for decisions; the official example/checker use lowercase `served` and `deferred`. Follow the executable artifact.
4. The checker warns rather than fails on populated deferred vehicle/trip fields, but the booklet requires blanks. Follow the booklet.
5. Hackathon fuel and broader operating-window rules are not Task 2B rules and must not be added to the Datathon feasibility contract.

No unresolved official/internal conflict remains for Phase 00.
