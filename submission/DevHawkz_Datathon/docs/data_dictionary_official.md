# WayLoom Datathon — Official Data Dictionary

**Classification:** Tracked official documentation  
**Source authority:** Rootcode Tech-Triathlon 2026 Challenge Booklet & Official Competition Artifacts  
**Phase:** 02 (Raw Dataset Inventory)

This document contains only organizer-documented table schemas, field semantics, units, formats, and structural keys. It contains **no observed private values, counts, distributions, or row samples**.

---

## 1. Document Conventions

- **Timezone:** Asia/Colombo for all clock times (`HH:MM`) and dates (`YYYY-MM-DD`).
- **Durations:** Expressed in integer or continuous minutes (`_min`).
- **Distances:** Measured in kilometres (`_km`).
- **Capacities & Demands:** Measured in kilograms (`_kg`) and cubic metres (`_m3`).
- **Key Status Classification:**
  - `OFFICIAL_KEY`: Primary identifier defined by the official competition specifications.
  - `OFFICIAL_COMPOSITE_KEY`: Multi-column primary identifier established by official rules.
  - `CANDIDATE_KEY_VERIFY_PHASE_03`: Likely identifier to be empirically verified for uniqueness in Phase 03.
  - `NO_PRIMARY_KEY_REQUIRED`: Artifact serves as a submission template, script, or non-relational lookup.

---

## 2. Training Artifacts

### 2.1 `deliveries_train.csv`
- **Category:** `training`
- **Grain:** One row per customer order / delivery attempt.
- **Primary Key:** `delivery_id` (`OFFICIAL_KEY`).
- **Official Purpose:** Historical delivery records for Task 1 model training and Task 2A historical demand baseline.

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `delivery_id` | `identifier` | Alphanumeric string | Unique identifier for delivery attempt | `KNOWN_AT_TASK1_PREDICTION` |
| `order_date` | `date` | `YYYY-MM-DD` | Date customer placed order (used for Task 2A demand) | `KNOWN_AT_TASK1_PREDICTION` |
| `dispatch_date` | `date` | `YYYY-MM-DD` | Scheduled vehicle dispatch date | `KNOWN_AT_TASK1_PREDICTION` |
| `dispatch_status` | `categorical` | String code | Status: attempted, deferred, not_run | `KNOWN_AT_TASK1_PREDICTION` |
| `outlet_id` | `identifier` | Alphanumeric string | Destination retail outlet (FK to `outlets.csv`) | `KNOWN_AT_TASK1_PREDICTION` |
| `brand` | `categorical` | Categorical string | Retail brand: Fresh, Style, Tech | `KNOWN_AT_TASK1_PREDICTION` |
| `district` | `categorical` | District name | Delivery destination district | `KNOWN_AT_TASK1_PREDICTION` |
| `depot` | `categorical` | Depot name | Dispatch origin depot | `KNOWN_AT_TASK1_PREDICTION` |
| `temp_requirement` | `categorical` | String code | Required transport temperature: ambient, chilled | `KNOWN_AT_TASK1_PREDICTION` |
| `order_units` | `numeric_count` | Integer count | Total quantity of units in order | `KNOWN_AT_TASK1_PREDICTION` |
| `order_weight_kg` | `numeric_continuous` | Kilograms (float) | Total order weight in kg | `KNOWN_AT_TASK1_PREDICTION` |
| `order_volume_m3` | `numeric_continuous` | Cubic metres (float) | Total order volume in m3 | `KNOWN_AT_TASK1_PREDICTION` |
| `route_id` | `identifier` | Alphanumeric string | Assigned route identifier | `KNOWN_AT_TASK1_PREDICTION` |
| `seq_in_route` | `ordinal_position` | Integer sequence | Stop sequence within route (joins to route leg `seq`) | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_id` | `identifier` | Alphanumeric string | Assigned delivery vehicle (FK to `vehicles.csv`) | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_type` | `categorical` | Vehicle type string | Category of vehicle (van, truck) | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_temp` | `categorical` | Temperature string | Vehicle temperature equipment (reefer, ambient) | `KNOWN_AT_TASK1_PREDICTION` |
| `planned_arrival_time` | `clock_time` | `HH:MM` | Planned arrival clock time at outlet | `KNOWN_AT_TASK1_PREDICTION` |
| `window_open_time` | `clock_time` | `HH:MM` | Outlet delivery window opening time | `KNOWN_AT_TASK1_PREDICTION` |
| `window_close_time` | `clock_time` | `HH:MM` | Outlet delivery window closing time | `KNOWN_AT_TASK1_PREDICTION` |

### 2.2 `route_legs_train.csv`
- **Category:** `training`
- **Grain:** One row per route leg journey segment.
- **Primary Key:** `leg_id` (`OFFICIAL_KEY`); Route composite: `route_id + seq` (`OFFICIAL_COMPOSITE_KEY`).
- **Official Purpose:** Historical route execution timings used to construct Task 1 training labels.

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `leg_id` | `identifier` | Alphanumeric string | Unique identifier for route leg | `KNOWN_AT_TASK1_PREDICTION` |
| `date` | `date` | `YYYY-MM-DD` | Date of route execution | `KNOWN_AT_TASK1_PREDICTION` |
| `route_id` | `identifier` | Alphanumeric string | Route identifier | `KNOWN_AT_TASK1_PREDICTION` |
| `seq` | `ordinal_position` | Integer sequence | Leg stop sequence (joins to delivery `seq_in_route`) | `KNOWN_AT_TASK1_PREDICTION` |
| `depot` | `categorical` | Depot name | Dispatch departure depot | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_id` | `identifier` | Alphanumeric string | Assigned vehicle identifier | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_type` | `categorical` | Vehicle type string | Vehicle category | `KNOWN_AT_TASK1_PREDICTION` |
| `vehicle_temp` | `categorical` | Temperature string | Vehicle temperature capabilities | `KNOWN_AT_TASK1_PREDICTION` |
| `brand` | `categorical` | Brand string | Brand delivered on route | `KNOWN_AT_TASK1_PREDICTION` |
| `district` | `categorical` | District name | Delivery district | `KNOWN_AT_TASK1_PREDICTION` |
| `from_point` | `identifier` | Point identifier | Origin of leg (depot or previous outlet) | `KNOWN_AT_TASK1_PREDICTION` |
| `to_outlet` | `identifier` | Outlet identifier | Destination outlet for leg | `KNOWN_AT_TASK1_PREDICTION` |
| `distance_km` | `numeric_continuous` | Kilometres (float) | Planned leg transit distance in km | `KNOWN_AT_TASK1_PREDICTION` |
| `planned_depart_time` | `clock_time` | `HH:MM` | Planned departure clock time | `KNOWN_AT_TASK1_PREDICTION` |
| `planned_travel_duration_min` | `numeric_duration` | Minutes (float) | Planned travel time between stops in minutes | `KNOWN_AT_TASK1_PREDICTION` |
| `planned_arrival_time` | `clock_time` | `HH:MM` | Planned arrival clock time | `KNOWN_AT_TASK1_PREDICTION` |
| `actual_depart_time` | `clock_time` | `HH:MM` | Actual departure clock time (**TRAINING ONLY - DENY-LIST**) | `TRAINING_ACTUAL_ONLY` |
| `actual_travel_duration_min` | `numeric_duration` | Minutes (float) | Actual travel time in minutes (**TRAINING ONLY - DENY-LIST**) | `TRAINING_ACTUAL_ONLY` |
| `arrival_time` | `clock_time` | `HH:MM` | Actual arrival time at outlet (**TRAINING ONLY - DENY-LIST**) | `TRAINING_ACTUAL_ONLY` |
| `leave_outlet_time` | `clock_time` | `HH:MM` | Actual departure from outlet (**TRAINING ONLY - DENY-LIST**) | `TRAINING_ACTUAL_ONLY` |
| `monsoon` | `binary_indicator` | Binary 0 / 1 | Monsoon active indicator | `KNOWN_AT_TASK1_PREDICTION` |
| `dow` | `categorical` | Integer code 1-7 | Day of week code | `KNOWN_AT_TASK1_PREDICTION` |

---

## 3. Test Artifacts

### 3.1 `task1_test_inputs.csv`
- **Category:** `test`
- **Grain:** One row per planned delivery in the Task 1 test horizon.
- **Primary Key:** `delivery_id` (`OFFICIAL_KEY`).
- **Official Purpose:** Input orders requiring predictions for `pred_service_min` and `pred_late_prob`.
- **Note:** Contains same planned columns as `deliveries_train.csv`. Also used to build Task 2A historical demand.

### 3.2 `route_legs_test.csv`
- **Category:** `test`
- **Grain:** One row per planned route leg in the Task 1 test horizon.
- **Primary Key:** `leg_id` (`OFFICIAL_KEY`); Route composite: `route_id + seq` (`OFFICIAL_COMPOSITE_KEY`).
- **Official Purpose:** Planned leg details for Task 1 test deliveries.
- **Critical Official Rule:** Contains planned fields only. Actual outcome fields (`actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, `leave_outlet_time`) are absent.

### 3.3 `task2a_test_inputs.csv`
- **Category:** `test`
- **Grain:** One row per depot, brand, and future forecast week.
- **Primary Key:** `row_id` (`OFFICIAL_KEY`).
- **Official Purpose:** Target horizon instances requiring forecasts of `pred_total_order_volume_m3` and `pred_chilled_order_volume_m3`.

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `row_id` | `identifier` | Alphanumeric string | Unique forecast request identifier | `KNOWN_AT_TASK1_PREDICTION` |
| `depot` | `categorical` | Depot name | Dispatch depot to forecast | `KNOWN_AT_TASK1_PREDICTION` |
| `brand` | `categorical` | Brand name | Retail brand (Fresh, Style, Tech) | `KNOWN_AT_TASK1_PREDICTION` |
| `iso_year` | `numeric_count` | Year integer | ISO calendar year | `FUTURE_CALENDAR_KNOWN` |
| `iso_week` | `numeric_count` | Week integer 1-53 | ISO calendar week number | `FUTURE_CALENDAR_KNOWN` |

### 3.4 `task2b_peak_day_scenarios.csv`
- **Category:** `test`
- **Grain:** One row per customer order in peak day scenarios.
- **Primary Key:** `order_ref` (`OFFICIAL_KEY` within scenario S1); Composite: `scenario + order_ref`.
- **CRITICAL RULE:** `order_ref` is the allocation key. **`outlet_id` MUST NEVER be used as the allocation key.** One outlet may have multiple orders.

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `scenario` | `categorical` | Alphanumeric (e.g. S1) | Scenario identifier (S1 is evaluated) | `TASK2B_SCENARIO_INPUT` |
| `order_ref` | `identifier` | Alphanumeric string | Unique order allocation reference | `TASK2B_SCENARIO_INPUT` |
| `outlet_id` | `identifier` | Outlet identifier | Destination outlet (reference only) | `TASK2B_SCENARIO_INPUT` |
| `brand` | `categorical` | Brand name | Retail brand (Fresh, Style, Tech) | `TASK2B_SCENARIO_INPUT` |
| `district` | `categorical` | District name | Delivery district (must match trip) | `TASK2B_SCENARIO_INPUT` |
| `depot` | `categorical` | Depot name | Origin depot (Peliyagoda) | `TASK2B_SCENARIO_INPUT` |
| `dock_type` | `categorical` | Dock category | Outlet dock configuration | `TASK2B_SCENARIO_INPUT` |
| `parking_constraint` | `categorical` | Constraint string | Parking constraints (e.g. van_only) | `TASK2B_SCENARIO_INPUT` |
| `mall_window` | `time_range` | `HH:MM-HH:MM` | Mall access delivery window | `TASK2B_SCENARIO_INPUT` |
| `window_open_time` | `clock_time` | `HH:MM` | Standard outlet window opening | `TASK2B_SCENARIO_INPUT` |
| `window_close_time` | `clock_time` | `HH:MM` | Standard outlet window closing | `TASK2B_SCENARIO_INPUT` |
| `temp_requirement` | `categorical` | Temperature string | Temperature requirement (chilled/ambient) | `TASK2B_SCENARIO_INPUT` |
| `order_units` | `numeric_count` | Integer count | Total order item units | `TASK2B_SCENARIO_INPUT` |
| `order_weight_kg` | `numeric_continuous` | Kilograms (float) | Total order weight | `TASK2B_SCENARIO_INPUT` |
| `order_volume_m3` | `numeric_continuous` | Cubic metres (float) | Total order volume | `TASK2B_SCENARIO_INPUT` |
| `deferred_yesterday` | `binary_indicator` | Binary 0 / 1 | Deferred on previous day flag | `TASK2B_SCENARIO_INPUT` |
| `days_since_last_served` | `numeric_count` | Days integer | Days elapsed since outlet last served | `TASK2B_SCENARIO_INPUT` |

### 3.5 `task2b_peak_day_fleet.csv`
- **Category:** `test`
- **Grain:** One row per fleet vehicle available in peak day scenarios.
- **Primary Key:** Candidate composite `scenario + vehicle_id` (`CANDIDATE_KEY_VERIFY_PHASE_03`).
- **Critical Rules:** Only vehicles with status `available` may be used. Vehicles marked `in_workshop` CANNOT be allocated.

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `scenario` | `categorical` | Alphanumeric (e.g. S1) | Scenario identifier | `TASK2B_SCENARIO_INPUT` |
| `vehicle_id` | `identifier` | Alphanumeric string | Fleet vehicle ID (FK to `vehicles.csv`) | `TASK2B_SCENARIO_INPUT` |
| `status` | `categorical` | Status string | Availability: available, in_workshop | `TASK2B_SCENARIO_INPUT` |

---

## 4. General / Reference Artifacts

### 4.1 `outlets.csv`
- **Category:** `general`
- **Grain:** One row per retail outlet.
- **Primary Key:** `outlet_id` (`OFFICIAL_KEY`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `outlet_id` | `identifier` | Alphanumeric string | Unique retail outlet identifier | `STATIC_REFERENCE` |
| `district` | `categorical` | District name | Geographical district | `STATIC_REFERENCE` |
| `dock_type` | `categorical` | Dock category | Loading dock type (joins to service allowance) | `STATIC_REFERENCE` |
| `parking_constraint` | `categorical` | Constraint string | Parking constraints (e.g. van_only) | `STATIC_REFERENCE` |
| `window_open_time` | `clock_time` | `HH:MM` | Outlet default delivery opening time | `STATIC_REFERENCE` |
| `window_close_time` | `clock_time` | `HH:MM` | Outlet default delivery closing time | `STATIC_REFERENCE` |

### 4.2 `vehicles.csv`
- **Category:** `general`
- **Grain:** One row per fleet vehicle.
- **Primary Key:** `vehicle_id` (`OFFICIAL_KEY`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `vehicle_id` | `identifier` | Alphanumeric string | Unique vehicle identifier | `STATIC_REFERENCE` |
| `vehicle_type` | `categorical` | Type string | Vehicle class: Van, Truck | `STATIC_REFERENCE` |
| `vehicle_temp` | `categorical` | Temperature string | Equipment: reefer, ambient | `STATIC_REFERENCE` |
| `weight_cap_kg` | `numeric_continuous` | Kilograms (float) | Maximum payload weight limit in kg | `STATIC_REFERENCE` |
| `volume_cap_m3` | `numeric_continuous` | Cubic metres (float) | Maximum payload volume limit in m3 | `STATIC_REFERENCE` |
| `home_depot` | `categorical` | Depot name | Assigned base depot (Peliyagoda for S1) | `STATIC_REFERENCE` |
| `fuel_type` | `categorical` | Fuel category | Fuel classification (diesel, petrol, electric) | `STATIC_REFERENCE` |
| `km_per_l` | `numeric_continuous` | Efficiency (float) | Nominal fuel efficiency | `STATIC_REFERENCE` |
| `weekly_fuel_quota_l`| `numeric_continuous` | Litres (float) | Weekly fuel quota limit | `STATIC_REFERENCE` |

### 4.3 `calendar.csv`
- **Category:** `general`
- **Grain:** One row per calendar date.
- **Primary Key:** `date` (`OFFICIAL_KEY`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `date` | `date` | `YYYY-MM-DD` | Calendar date | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `dow` | `categorical` | Integer 1-7 | Day of week code | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `is_weekend` | `binary_indicator` | Binary 0 / 1 | Weekend indicator | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `iso_year` | `numeric_count` | Year integer | ISO calendar year | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `iso_week` | `numeric_count` | Week integer 1-53 | ISO calendar week number | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `is_payday` | `binary_indicator` | Binary 0 / 1 | Payday indicator | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `festival` | `categorical` | Festival string | Festival name or none | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `festival_ramp` | `numeric_continuous` | Continuous float | Festival buildup ramp index | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `is_holiday` | `binary_indicator` | Binary 0 / 1 | Public holiday indicator | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `monsoon` | `binary_indicator` | Binary 0 / 1 | Monsoon seasonal indicator | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |
| `is_operating` | `binary_indicator` | Binary 0 / 1 | Operating business day indicator | `STATIC_REFERENCE` / `FUTURE_CALENDAR_KNOWN` |

### 4.4 `district_travel.csv`
- **Category:** `general`
- **Grain:** One row per depot-to-district corridor.
- **Primary Key:** Candidate composite `district + depot` (`CANDIDATE_KEY_VERIFY_PHASE_03`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `depot` | `categorical` | Depot name | Origin depot | `STATIC_REFERENCE` |
| `district` | `categorical` | District name | Destination district | `STATIC_REFERENCE` |
| `free_flow_kmh` | `numeric_continuous` | km/h (float) | Nominal free-flow travel speed | `STATIC_REFERENCE` |
| `depot_to_district_km` | `numeric_continuous` | km (float) | Distance from depot to district center | `STATIC_REFERENCE` |
| `depot_to_district_freeflow_min` | `numeric_duration` | Minutes (float) | Free-flow transit duration from depot to district | `STATIC_REFERENCE` |
| `inter_stop_km` | `numeric_continuous` | km (float) | Average distance between stops in district | `STATIC_REFERENCE` |
| `inter_stop_freeflow_min` | `numeric_duration` | Minutes (float) | Average free-flow duration between stops | `STATIC_REFERENCE` |

### 4.5 `service_allowance.csv`
- **Category:** `general`
- **Grain:** One row per brand and dock type combination.
- **Primary Key:** Composite `brand + dock_type` (`OFFICIAL_COMPOSITE_KEY`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules | Availability Class |
|---|---|---|---|---|
| `brand` | `categorical` | Brand name | Retail brand (Fresh, Style, Tech) | `STATIC_REFERENCE` |
| `dock_type` | `categorical` | Dock category | Outlet dock classification | `STATIC_REFERENCE` |
| `service_allowance_min` | `numeric_duration` | Minutes (float) | Standard unloading service duration allowance | `STATIC_REFERENCE` |

### 4.6 `traffic_speed.csv`
- **Category:** `general`
- **Grain:** Traffic speed observation records.
- **Primary Key:** `CANDIDATE_KEY_VERIFY_PHASE_03` (verify composite in Phase 03).
- **Official Purpose:** Traffic speed index observations by time and corridor.

### 4.7 `road_conditions.csv`
- **Category:** `general`
- **Grain:** Road condition and disruption observation records.
- **Primary Key:** `CANDIDATE_KEY_VERIFY_PHASE_03` (verify composite in Phase 03).
- **Official Purpose:** Disruption index and road condition factors affecting transport corridors.

---

## 5. Submission Templates

### 5.1 `submission_task1.csv`
- **Category:** `templates`
- **Grain:** One row per Task 1 test delivery.
- **Primary Key:** `NO_PRIMARY_KEY_REQUIRED` (preserves input `delivery_id`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules |
|---|---|---|---|
| `delivery_id` | `identifier` | Alphanumeric string | Must match test input `delivery_id` in original row order |
| `pred_service_min` | `numeric_duration` | Minutes (float) | Predicted service duration at outlet |
| `pred_late_prob` | `numeric_continuous` | Probability [0.0, 1.0] | Predicted probability of arriving strictly after window close |

### 5.2 `submission_task2a.csv`
- **Category:** `templates`
- **Grain:** One row per Task 2A forecast target row.
- **Primary Key:** `NO_PRIMARY_KEY_REQUIRED` (preserves input `row_id`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules |
|---|---|---|---|
| `row_id` | `identifier` | Alphanumeric string | Must match test input `row_id` in original row order |
| `pred_total_order_volume_m3` | `numeric_continuous` | m3 (float >= 0) | Predicted total demand volume |
| `pred_chilled_order_volume_m3`| `numeric_continuous` | m3 (float >= 0) | Predicted chilled demand volume (MUST BE EXACTLY 0 FOR STYLE AND TECH) |

### 5.3 `submission_task2b.csv`
- **Category:** `templates`
- **Grain:** One row per Task 2B order reference in scenario S1.
- **Primary Key:** `NO_PRIMARY_KEY_REQUIRED` (preserves input `order_ref`).

| Column Name | Semantic Type | Documented Format | Official Meaning & Rules |
|---|---|---|---|
| `order_ref` | `identifier` | Alphanumeric string | Customer order allocation key in scenario S1 |
| `decision` | `categorical` | String code | Allocation decision: `served` or `deferred` |
| `vehicle_id` | `identifier` | Alphanumeric string | Assigned vehicle ID (blank if deferred) |
| `trip_id` | `identifier` | Integer string (1 or 2) | Assigned trip number (1 or 2; blank if deferred) |

---

## 6. Validation Utility

### 6.1 `check_allocation.py`
- **Category:** `validation`
- **Format:** Python executable script.
- **Official Purpose:** Validates feasibility of Task 2B allocation submission against physical and operational constraints.
- **Rule Verification:** Verifies feasibility, NOT optimality.
