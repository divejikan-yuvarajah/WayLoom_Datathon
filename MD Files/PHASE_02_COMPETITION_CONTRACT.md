# PHASE 02 — Raw Dataset Inventory

> **Requested filename:** `PHASE_02_COMPETITION_CONTRACT.md`  
> **Canonical phase name in the master plan:** **Phase 02 — Raw Dataset Inventory**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-023 → DT-035**  
> **Task count:** 13  
> **Default priority:** P0  
> **Phase dependency:** Phase 01 must have passed  
> **Recommended execution style:** **Full-phase tooling implementation + human/local data run + independent review**  
> **Phase gate:** Every supplied competition file is located, categorized, locally loadable, structurally inventoried, keyed at a basic level, typed at a basic level, and classified by prediction-time availability without exposing raw competition records.

---

# 1. Purpose of Phase 02

Phase 02 creates the **first verified map of the competition dataset**.

The objective is not to clean, transform, model, visualize, optimize, or judge data quality yet. Those activities belong to later phases.

Phase 02 answers only foundational questions:

- What files were supplied?
- Where does each file belong?
- Can every CSV be read locally?
- What is the grain of each table?
- What columns exist?
- What are the likely/official keys?
- How do tables relate?
- Which fields are numerical, categorical, date/time, identifier-like, or target-related?
- Which Task 1 fields are available at prediction time?
- Which fields are historical actuals and therefore unavailable at prediction time?
- Which Task 2A fields are known for the future forecast horizon?
- Which Task 2B fields are scenario inputs rather than predictions?

The output of this phase becomes the structural foundation for:

```text
Phase 03 — Data-quality audit
Phase 04 — Task 1 label construction
Phase 06 — Task 1 feature engineering
Phase 11 — Task 2A demand construction
Phase 18 — Task 2B scenario understanding
```

No downstream work should begin until the Phase 02 inventory is trustworthy.

---

# 2. Critical competition-data safety rule for Phase 02

The official competition material restricts sharing, distribution, transmission and publication of the supplied datasets and derivatives.

Therefore Phase 02 uses a **two-layer execution model**.

## Layer A — AI-assisted code implementation

Cursor/Codex may:

- read this phase specification;
- read source code and configuration;
- read official schema/documentation already present in the project;
- write inventory utilities;
- write tests using **synthetic fixtures**;
- create the expected-file manifest;
- create documentation templates;
- review implementation code.

Cursor/Codex must **not**:

- open official CSV files;
- display official rows;
- call `head()`, `sample()`, `tail()` or equivalent on official data;
- inspect unique values from official records;
- execute the inventory script against `data/raw`;
- read private generated inventory reports;
- upload/transmit dataset contents or private derivatives.

## Layer B — local human/operator execution

The team member runs the completed inventory utility from a normal local terminal **outside the AI-agent context**.

The local inventory utility may read the official files and write metadata into an ignored private report directory.

The team member should report only:

```text
LOCAL PHASE 02 INVENTORY RUN: PASS
```

or:

```text
LOCAL PHASE 02 INVENTORY RUN: FAIL
BLOCKER TYPE: <missing file / load failure / duplicate filename / schema mismatch / other>
```

Do not paste raw rows, values, private inventory JSON, or derived competition records into Cursor/Codex.

This separation is a project safety control, not an organizer-prescribed technical architecture.

---

# 3. Official dataset contract relevant to Phase 02

The official booklet describes the Datathon data in the following groups.

## Training files

```text
deliveries_train.csv
route_legs_train.csv
```

## Test inputs

```text
task1_test_inputs.csv
route_legs_test.csv
task2a_test_inputs.csv
task2b_peak_day_scenarios.csv
task2b_peak_day_fleet.csv
```

## General/reference data

```text
outlets.csv
vehicles.csv
calendar.csv
district_travel.csv
service_allowance.csv
traffic_speed.csv
road_conditions.csv
```

## Submission templates

```text
submission_task1.csv
submission_task2a.csv
submission_task2b.csv
```

## Validation utility

```text
check_allocation.py
```

**Expected named artifacts:** 18

The official booklet also establishes these important structural facts:

- `deliveries_train.csv` contains one row per order identified by `delivery_id`.
- `task1_test_inputs.csv` contains one row per Task 1 delivery plan.
- dispatched training orders relate to route legs through `route_id` + `seq_in_route` on deliveries and `route_id` + `seq` on route legs.
- `route_legs_train.csv` contains actual journey timings.
- `route_legs_test.csv` contains planned route information rather than training actuals.
- `task2a_test_inputs.csv` contains depot + brand + future forecast-week rows identified by `row_id`.
- `task2b_peak_day_scenarios.csv` uses `order_ref` as the allocation key because one outlet may have multiple orders.
- `task2b_peak_day_fleet.csv` contains scenario vehicle availability.
- clock-time columns use `HH:MM` in Asia/Colombo.
- duration columns are measured in minutes.

Do not silently change these official meanings during local inventory.

---

# 4. Phase 02 task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---|---|---|---|
| [ ] | **DT-023** | [E] | P0 | Phase 01 | Extract `DataSet_New.zip` |
| [ ] | **DT-024** | [E] | P0 | DT-023 | Inventory every supplied file |
| [ ] | **DT-025** | [E] | P0 | DT-024 | Categorize files |
| [ ] | **DT-026** | [E] | P0 | DT-024–DT-025 | Load every CSV successfully |
| [ ] | **DT-027** | [E] | P0 | DT-026 | Record row/column counts |
| [ ] | **DT-028** | [E] | P0 | DT-026 | Record all column names |
| [ ] | **DT-029** | [E] | P0 | DT-027–DT-028 | Generate local data dictionary |
| [ ] | **DT-030** | [E] | P0 | DT-028–DT-029 | Identify primary keys |
| [ ] | **DT-031** | [E] | P0 | DT-028–DT-030 | Identify relational joins |
| [ ] | **DT-032** | [E] | P0 | DT-028–DT-029 | Identify numerical variables |
| [ ] | **DT-033** | [E] | P0 | DT-028–DT-029 | Identify categorical variables |
| [ ] | **DT-034** | [E] | P0 | DT-028–DT-029 | Identify date/time variables |
| [ ] | **DT-035** | [E] | P0 | DT-028–DT-034 | Identify future-known versus future-unknown variables |

**Phase complete:** [ ]  
**READY FOR PHASE 03:** NO

---

# 5. Required Phase 02 repository additions

Recommended tracked files:

```text
configs/
└── dataset_manifest.yaml

src/
└── common/
    └── data_inventory.py

scripts/
└── run_dataset_inventory.py

docs/
├── data_dictionary_official.md
└── phases/
    └── PHASE_02_COMPETITION_CONTRACT.md

tests/
└── test_data_inventory.py
```

Recommended **private ignored** outputs created only by the local operator run:

```text
reports/
└── private/
    └── phase02_inventory/
        ├── inventory.json
        ├── data_dictionary.json
        ├── join_map.json
        ├── variable_types.json
        ├── availability_map.json
        └── validation_summary.json
```

Update `.gitignore` and `.cursorignore` if needed:

```gitignore
reports/private/**
```

```text
reports/private/**
```

Do not commit private inventory outputs.

---

# 6. Expected dataset manifest

Create `configs/dataset_manifest.yaml` based on official filenames and purposes.

Recommended structure:

```yaml
version: 1

training:
  - filename: deliveries_train.csv
    required: true
    official_grain: one order per delivery_id
  - filename: route_legs_train.csv
    required: true
    official_grain: one route leg per leg_id

test:
  - filename: task1_test_inputs.csv
    required: true
    official_grain: one Task 1 delivery plan per delivery_id
  - filename: route_legs_test.csv
    required: true
    official_grain: one planned route leg per leg_id
  - filename: task2a_test_inputs.csv
    required: true
    official_grain: one depot-brand-forecast-week row per row_id
  - filename: task2b_peak_day_scenarios.csv
    required: true
    official_grain: one peak-day order per scenario + order_ref
  - filename: task2b_peak_day_fleet.csv
    required: true
    official_grain: one scenario vehicle-status row per scenario + vehicle_id

general:
  - filename: outlets.csv
    required: true
    official_grain: one outlet per outlet_id
  - filename: vehicles.csv
    required: true
    official_grain: one vehicle per vehicle_id
  - filename: calendar.csv
    required: true
    official_grain: one calendar date per date
  - filename: district_travel.csv
    required: true
    official_grain: one district/depot travel reference row
  - filename: service_allowance.csv
    required: true
    official_grain: one brand + dock_type allowance row
  - filename: traffic_speed.csv
    required: true
    official_grain: verify locally; booklet documents key fields but not complete grain
  - filename: road_conditions.csv
    required: true
    official_grain: verify locally; date-specific district disruption reference

templates:
  - filename: submission_task1.csv
    required: true
  - filename: submission_task2a.csv
    required: true
  - filename: submission_task2b.csv
    required: true

validation:
  - filename: check_allocation.py
    required: true
```

Do not place observed row counts or private values in this tracked manifest.

---

# 7. Detailed task specifications

---

## DT-023 — Extract `DataSet_New.zip`

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** Phase 01 PASS

### Objective

Place the official dataset under the protected local data area without exposing it to Git or coding agents.

### Why it matters

Every later phase depends on one stable local source location.

### Inputs

```text
DataSet_New.zip
```

obtained from the organizer-approved source.

### Output

Recommended:

```text
data/raw/DataSet_New/
```

or, if already extracted:

```text
data/raw/<organizer folder structure>
```

The inventory code must support either layout by recursively locating required filenames.

### Human/local instructions

1. Confirm Phase 01 data-protection rules pass.
2. Confirm `data/raw/**` is ignored by Git.
3. Confirm `data/raw/**` is excluded from Cursor indexing/access.
4. Copy `DataSet_New.zip` to a local protected location if necessary.
5. Extract it locally.
6. Do not rename official files.
7. Preserve organizer directory groupings when possible.
8. Do not move official data into `src/`, `notebooks/`, `docs/`, `outputs/` or public locations.
9. Run `git status` and confirm extracted files are not staged/tracked.
10. Do not ask Cursor/Codex to inspect the directory tree after extraction if doing so would expose private filenames beyond the official manifest.

### Safe validation

The human operator may verify locally:

```bash
git status
git check-ignore -v data/raw/...
```

Do not paste private directory listings into AI chat.

### Edge cases

- ZIP already extracted.
- ZIP contains an extra top-level directory.
- file names contain spaces.
- archive extraction creates duplicate nested copies.
- extraction tool changes filenames.
- operating system hides extensions.
- ZIP remains inside the Git root.

### Tests

Manual/local:

- archive opens successfully;
- expected official files are present;
- no official file is Git-tracked;
- no official file is accessible through the configured agent index rules.

### Definition of Done

- [ ] dataset is extracted locally;
- [ ] official filenames are preserved;
- [ ] protected raw-data path is used;
- [ ] Git does not track the extracted files;
- [ ] agent-exclusion rules remain active.

### STOP conditions

Stop if:

- `data/raw` is not ignored;
- the repository remote is public;
- files are accidentally staged;
- extraction requires uploading the archive to an external service;
- files appear corrupted or incomplete.

---

## DT-024 — Inventory every supplied file

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-023

### Objective

Confirm that every required official artifact exists exactly once and record any extra/missing artifacts locally.

### Inputs

- protected raw-data root;
- `configs/dataset_manifest.yaml`.

### Outputs

Private local:

```text
reports/private/phase02_inventory/inventory.json
```

Tracked code:

```text
src/common/data_inventory.py
```

### Implementation logic

The inventory utility should:

1. recursively search the configured raw-data root;
2. compare discovered basenames with the manifest;
3. reject ambiguous duplicates of a required filename;
4. mark each required file as:
   - found;
   - missing;
   - duplicated;
5. record safe technical metadata locally:
   - filename;
   - relative path;
   - category;
   - extension;
   - file size in bytes;
   - required flag;
6. record unexpected files separately;
7. **never read or write row values in DT-024**.

### Recommended API

```python
def discover_dataset_files(
    raw_root: Path,
    manifest: dict,
) -> dict:
    ...
```

### Do not

- print full absolute personal paths in tracked documentation;
- print file contents;
- hash files and send hashes externally unless specifically needed;
- silently choose one of two duplicate official filenames.

### Tests

Use synthetic temporary directories.

Test cases:

- all expected files present;
- one required file missing;
- duplicate required filename in two folders;
- unexpected extra file;
- filenames with spaces;
- nested top-level folder.

### Definition of Done

- [ ] all official expected names are represented in manifest;
- [ ] discovery code is recursive;
- [ ] duplicates are treated as blockers;
- [ ] missing files are treated as blockers;
- [ ] private inventory output remains ignored;
- [ ] tests use synthetic files only.

### STOP conditions

Stop if any required file is missing or duplicated in the local operator run.

---

## DT-025 — Categorize files

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-024

### Objective

Assign each supplied artifact to its official role.

### Categories

Use:

```text
training
test
general
templates
validation
```

Do not invent a sixth category unless a genuine extra organizer artifact exists and is documented.

### Expected mapping

#### Training

```text
deliveries_train.csv
route_legs_train.csv
```

#### Test

```text
task1_test_inputs.csv
route_legs_test.csv
task2a_test_inputs.csv
task2b_peak_day_scenarios.csv
task2b_peak_day_fleet.csv
```

#### General

```text
outlets.csv
vehicles.csv
calendar.csv
district_travel.csv
service_allowance.csv
traffic_speed.csv
road_conditions.csv
```

#### Templates

```text
submission_task1.csv
submission_task2a.csv
submission_task2b.csv
```

#### Validation

```text
check_allocation.py
```

### Output

Category should be stored in the manifest and private inventory.

### Tests

Synthetic manifest test:

- every required artifact maps to exactly one category;
- no artifact maps to multiple categories;
- total expected named artifacts = 18.

### Definition of Done

- [ ] every required file has exactly one category;
- [ ] categories match official purpose;
- [ ] templates are not mistaken for test data;
- [ ] checker is not treated as a CSV.

### STOP conditions

Stop if a required artifact cannot be classified from official materials.

---

## DT-026 — Load every CSV successfully

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-024–DT-025

### Objective

Verify locally that each CSV is syntactically readable without inspecting or displaying row contents.

### Important safety behavior

Cursor/Codex writes and tests the loader using synthetic CSVs.

The **human operator** executes it against official `data/raw`.

### Required behavior

For each required `.csv`:

1. open using a controlled encoding policy;
2. parse using comma-separated CSV semantics;
3. load without printing rows;
4. capture read success/failure;
5. capture only structural metadata needed by this phase;
6. close/release resources;
7. never serialize full rows into logs/reports.

### Recommended implementation

Use Pandas locally:

```python
df = pd.read_csv(path)
```

but do not call:

```python
df.head()
df.tail()
df.sample()
df.to_dict("records")
print(df)
```

The utility should write only:

```text
load_status
row_count
column_count
column_names
observed_dtype per column
```

to the ignored private report.

### Encoding policy

Recommended:

1. try `utf-8`;
2. if a byte-order mark is present, use `utf-8-sig`;
3. do not silently fall back to arbitrary encodings without recording the decision.

### Validation script behavior

Return non-zero exit code if any required CSV cannot load.

### Tests

Synthetic fixtures:

- valid CSV;
- empty-but-header CSV;
- UTF-8 BOM CSV;
- malformed CSV;
- duplicate column name behavior;
- non-CSV file excluded from loader.

### Definition of Done

- [ ] every required CSV can be loaded locally;
- [ ] loader never prints rows;
- [ ] checker `.py` is excluded;
- [ ] failures produce actionable filenames/error classes without row contents;
- [ ] local run returns PASS.

### STOP conditions

Stop if:

- any required CSV fails parsing;
- file appears corrupted;
- delimiter/encoding must be guessed without evidence;
- the only way to debug would expose private row contents to the agent.

---

## DT-027 — Record row/column counts

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-026

### Objective

Record the structural size of each CSV locally for audit/reproducibility.

### Output

Private:

```text
inventory.json
```

Fields:

```json
{
  "filename": "...",
  "row_count": 0,
  "column_count": 0
}
```

### Rules

- counts are local/private inventory metadata;
- do not hard-code expected row counts from prior analysis into production assertions;
- later phases may validate specific cardinalities based on official relationships;
- templates should also have counts recorded, but they must remain categorized as templates.

### Tests

Synthetic fixtures with known dimensions.

### Definition of Done

- [ ] every CSV has a row count;
- [ ] every CSV has a column count;
- [ ] counts are generated programmatically;
- [ ] counts are not committed/published.

### STOP conditions

Stop if any CSV reports:

- zero columns;
- unreadable structure;
- impossible parser result.

An empty template may still be structurally valid if headers exist; do not assume zero rows is automatically an error without checking the official template semantics.

---

## DT-028 — Record all column names

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-026

### Objective

Capture the exact observed column schema for every CSV.

### Output

Private:

```text
data_dictionary.json
```

Tracked safe reference:

```text
docs/data_dictionary_official.md
```

The tracked document should contain only fields documented by the official booklet, not private observed values.

### Rules

- preserve original column spelling and case;
- preserve ordering separately where relevant;
- do not normalize/rename columns in Phase 02;
- do not infer semantics for undocumented columns without marking them `observed / meaning to verify`;
- Task 1 final row-order preservation is important later, but this phase only records schema.

### Tests

Synthetic CSV with:

- normal columns;
- column containing underscore;
- column ordering;
- BOM in first header.

### Definition of Done

- [ ] all CSV column names captured locally;
- [ ] official documented columns represented in tracked reference;
- [ ] no renaming performed;
- [ ] undocumented fields clearly marked for later verification.

### STOP conditions

Stop if a required official column is absent from an expected core file.

Do not silently create missing columns.

---

## DT-029 — Generate local data dictionary

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-027–DT-028

### Objective

Create a structured description of every table and field without doing Phase 03 quality analysis.

### Private local dictionary fields

For each table:

```text
filename
category
grain
row_count
column_count
primary_key_candidate
official_purpose
```

For each column:

```text
column_name
observed_pandas_dtype
semantic_type
official_format_if_documented
official_meaning_if_documented
availability_class
notes
```

### Semantic type values

Use a controlled set:

```text
identifier
numeric_continuous
numeric_count
numeric_duration
binary_indicator
categorical
date
clock_time
time_range
ordinal_position
text
unknown
```

### Important boundary

Do **not** include:

- min/max;
- means;
- quantiles;
- unique category values;
- missing counts;
- outlier statistics;
- record samples.

Those belong to Phase 03 or later.

### Tracked official dictionary

`docs/data_dictionary_official.md` should summarize the official booklet's documented definitions.

It may safely document known official fields such as:

#### Order records

```text
delivery_id
order_date
dispatch_date
dispatch_status
outlet_id
brand
district
depot
temp_requirement
order_units
order_weight_kg
order_volume_m3
route_id
seq_in_route
vehicle_id
vehicle_type
vehicle_temp
planned_arrival_time
window_open_time
window_close_time
```

#### Route legs

```text
leg_id
date
route_id
seq
depot
vehicle_id
vehicle_type
vehicle_temp
brand
district
from_point
to_outlet
distance_km
planned_depart_time
planned_travel_duration_min
planned_arrival_time
actual_depart_time          # training only
actual_travel_duration_min  # training only
arrival_time                # training only
leave_outlet_time           # training only
monsoon
dow
```

Use the booklet as authority; do not invent meanings for fields not documented there.

### Tests

Synthetic schema dictionary generation.

### Definition of Done

- [ ] local dictionary covers every observed table/column;
- [ ] tracked dictionary is official-source grounded;
- [ ] no statistical profiling has leaked into Phase 02;
- [ ] no private row values are stored.

### STOP conditions

Stop if field meaning cannot be established and a later task would depend on guessing it.

Mark it `unknown` and carry the issue forward.

---

## DT-030 — Identify primary keys

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-029

### Objective

Record official or candidate record identifiers for each table.

### Key-status labels

Use:

```text
OFFICIAL_KEY
OFFICIAL_COMPOSITE_KEY
CANDIDATE_KEY_VERIFY_PHASE_03
NO_PRIMARY_KEY_REQUIRED
```

### Officially supported keys

| File | Key |
|---|---|
| `deliveries_train.csv` | `delivery_id` |
| `task1_test_inputs.csv` | `delivery_id` |
| `route_legs_train.csv` | `leg_id`; route relationship also uses `route_id + seq` |
| `route_legs_test.csv` | `leg_id`; route relationship also uses `route_id + seq` |
| `task2a_test_inputs.csv` | `row_id` |
| `task2b_peak_day_scenarios.csv` | `scenario + order_ref` for scenario allocation identity; `order_ref` is the allocation key within S1 |
| `task2b_peak_day_fleet.csv` | candidate composite `scenario + vehicle_id`; verify locally |
| `outlets.csv` | `outlet_id` |
| `vehicles.csv` | `vehicle_id` |
| `calendar.csv` | `date` |
| `service_allowance.csv` | `brand + dock_type` |
| `district_travel.csv` | candidate `district + depot`; verify locally |
| `traffic_speed.csv` | verify locally from full schema; do not invent |
| `road_conditions.csv` | candidate based on date-specific district context; verify locally |
| submission templates | preserve their supplied identifiers; not modelling source keys |

### Important boundary

Phase 02 identifies keys; **Phase 03 verifies uniqueness**.

Do not mark a candidate as verified unique until the data-quality audit.

### Output

Private/local key map:

```text
join_map.json
```

and tracked official key notes in `docs/data_dictionary_official.md`.

### Tests

Unit-test key metadata validation using manifest fixtures.

### Definition of Done

- [ ] official keys are distinguished from candidates;
- [ ] no candidate is falsely labelled verified;
- [ ] `outlet_id` is not used as Task 2B allocation key;
- [ ] uniqueness verification is deferred to Phase 03.

### STOP conditions

Stop if an implementation assumes a key not supported by official documentation or local schema.

---

## DT-031 — Identify relational joins

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-030

### Objective

Build the structural relationship map needed by later phases.

### Critical official Task 1 join

```text
deliveries_train.route_id
+
deliveries_train.seq_in_route

↔

route_legs_train.route_id
+
route_legs_train.seq
```

Task 1 test relationship:

```text
task1_test_inputs.route_id
+
task1_test_inputs.seq_in_route

↔

route_legs_test.route_id
+
route_legs_test.seq
```

### Core reference joins

Record at minimum:

```text
deliveries/outlet_id       → outlets/outlet_id
deliveries/vehicle_id      → vehicles/vehicle_id
deliveries/order_date      → calendar/date
deliveries/dispatch_date   → calendar/date when applicable

route_legs/vehicle_id      → vehicles/vehicle_id
route_legs/date            → calendar/date

district + depot           → district_travel (verify composite uniqueness in Phase 03)

brand + dock_type          → service_allowance

task2b/outlet_id           → outlets/outlet_id when needed
task2b fleet/vehicle_id    → vehicles/vehicle_id
```

For `traffic_speed.csv` and `road_conditions.csv`, use only join fields that are actually present and supported by the local schema/official meaning. Do not invent a join.

### Output

Private:

```text
reports/private/phase02_inventory/join_map.json
```

Tracked conceptual map may be documented without private cardinality results.

### Important boundary

Phase 02 records **join intent**.

Phase 03/04 verifies:

- key uniqueness;
- match rates;
- one-to-one cardinality;
- referential integrity.

### Tests

Use synthetic files to test join metadata representation.

### Definition of Done

- [ ] critical Task 1 join is documented exactly;
- [ ] reference joins are mapped;
- [ ] candidate joins are labelled as candidates;
- [ ] no real join cardinality is claimed before validation.

### STOP conditions

Stop if a later-required relationship cannot be expressed from the observed/official columns.

---

## DT-032 — Identify numerical variables

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-029

### Objective

Classify fields that represent measurable quantities, counts, durations, scores or numeric indicators.

### Classification guidance

Do not classify a field as continuous numeric simply because Pandas reads it as an integer.

Examples:

- `order_units` → numeric count;
- `order_weight_kg` → numeric continuous;
- `order_volume_m3` → numeric continuous;
- `seq_in_route` / `seq` → ordinal position;
- `dow` → categorical/ordinal code, not a continuous measurement;
- `monsoon` → binary indicator;
- `is_payday` → binary indicator;
- `festival_ramp` → numeric continuous bounded indicator;
- `pred_late_prob` → probability output in submission template, not an input feature at this phase.

### Officially documented numeric groups

Orders:

```text
order_units
order_weight_kg
order_volume_m3
seq_in_route
```

Route legs:

```text
seq
distance_km
planned_travel_duration_min
actual_travel_duration_min (training only)
monsoon
dow
```

Vehicles:

```text
weight_cap_kg
volume_cap_m3
km_per_l
weekly_fuel_quota_l
```

Calendar:

```text
dow
is_weekend
iso_year
iso_week
is_payday
festival_ramp
is_holiday
monsoon
is_operating
```

District travel:

```text
free_flow_kmh
depot_to_district_km
depot_to_district_freeflow_min
inter_stop_km
inter_stop_freeflow_min
```

Service allowance:

```text
service_allowance_min
```

Traffic/roads:

```text
speed_index
disruption_index
```

Task 2B:

```text
order_units
order_weight_kg
order_volume_m3
deferred_yesterday
days_since_last_served
```

### Output

Private `variable_types.json`.

### Tests

Synthetic type-classification tests.

### Definition of Done

- [ ] numeric measures distinguished from identifiers/codes;
- [ ] binary indicators labelled correctly;
- [ ] route sequence treated as position;
- [ ] output prediction columns not mistaken for observed targets.

### STOP conditions

Stop if automatic dtype inference is being used as the only semantic classification.

---

## DT-033 — Identify categorical variables

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-029

### Objective

Identify fields representing labels, operational classes, locations, statuses, access conditions or identifiers that should not be treated as numeric magnitudes.

### Common official categories

```text
brand
district
depot
temp_requirement
dispatch_status
vehicle_type
vehicle_temp
dock_type
parking_constraint
fuel_type
road_class
festival
status
scenario
```

Identifier-like categories:

```text
delivery_id
outlet_id
route_id
vehicle_id
leg_id
row_id
order_ref
from_point
to_outlet
```

### Important distinction

Keep:

```text
identifier
```

separate from:

```text
categorical_feature
```

An ID may later be used as a categorical feature only after deliberate modelling analysis.

### Output

Private `variable_types.json`.

### Tests

Synthetic schema classification.

### Definition of Done

- [ ] categorical fields identified;
- [ ] identifier fields distinguished;
- [ ] no encoding is performed yet;
- [ ] no unique-value profiling occurs in this phase.

### STOP conditions

Stop if category meanings are inferred from private values rather than official definitions when documentation is available.

---

## DT-034 — Identify date/time variables

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-029

### Objective

Classify all date, clock-time, duration and time-range fields before later parsing.

### Official date fields

```text
order_date
dispatch_date
date
calendar.date
```

### Official clock-time fields

Orders:

```text
planned_arrival_time
window_open_time
window_close_time
```

Route legs:

```text
planned_depart_time
planned_arrival_time
actual_depart_time
arrival_time
leave_outlet_time
```

Outlet:

```text
window_open_time
window_close_time
```

### Time-range field

```text
mall_window
```

Official format:

```text
HH:MM-HH:MM
```

when populated.

### Duration fields

```text
planned_travel_duration_min
actual_travel_duration_min
depot_to_district_freeflow_min
inter_stop_freeflow_min
service_allowance_min
```

Durations are numeric minutes, not clock times.

### Rules

- do not parse/transform official columns yet beyond what is necessary to classify them;
- preserve original strings;
- actual timezone convention is Asia/Colombo;
- midnight/time-boundary handling belongs to Phase 04 for Task 1;
- weekly aggregation logic belongs to Phase 11.

### Tests

Synthetic format metadata.

### Definition of Done

- [ ] dates identified;
- [ ] clock times identified;
- [ ] time ranges identified;
- [ ] durations separated from clock times;
- [ ] timezone convention recorded.

### STOP conditions

Stop if a duration is being interpreted as a clock time or vice versa.

---

## DT-035 — Identify future-known versus future-unknown variables

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-028–DT-034

### Objective

Create an explicit availability map that prevents target leakage before feature engineering begins.

This is one of the most important outputs of Phase 02.

### Availability classes

Use:

```text
KNOWN_AT_TASK1_PREDICTION
TRAINING_ACTUAL_ONLY
TARGET_DERIVED
STATIC_REFERENCE
FUTURE_CALENDAR_KNOWN
TASK2A_HISTORICAL_DEMAND
TASK2A_UNKNOWN_FUTURE_TARGET
TASK2B_SCENARIO_INPUT
SUBMISSION_OUTPUT_ONLY
NOT_APPLICABLE
REQUIRES_LATER_VERIFICATION
```

---

### Task 1 — known at prediction time

Fields supplied in Task 1 test inputs and planned route legs are eligible for later consideration because they exist before the delivery outcome.

Examples include, when present in the official test schema:

```text
delivery_id
order_date
dispatch_date
dispatch_status
outlet_id
brand
district
depot
temp_requirement
order_units
order_weight_kg
order_volume_m3
route_id
seq_in_route
vehicle_id
vehicle_type
vehicle_temp
planned_arrival_time
window_open_time
window_close_time

route-leg planned fields:
leg_id
date
route_id
seq
depot
vehicle_id
vehicle_type
vehicle_temp
brand
district
from_point
to_outlet
distance_km
planned_depart_time
planned_travel_duration_min
planned_arrival_time
monsoon
dow
```

Static reference data may also be considered later if available before prediction:

```text
outlet attributes
vehicle attributes
calendar attributes
district travel reference
service allowance
```

Traffic/road features must be classified only after confirming that the relevant record is available for the prediction date and is legitimate prediction-time information.

Do not assume every general-data field is automatically leakage-safe.

---

### Task 1 — training actuals / future unknown

These training route-leg fields are historical outcomes and must never enter prediction-time features directly:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

They are used to construct labels or historical features only under later leakage-safe rules.

Classify them:

```text
TRAINING_ACTUAL_ONLY
```

---

### Task 1 — target-derived

Future target values do not exist as input columns and will later be constructed from historical actuals:

```text
service_start
service_min
late_flag
```

Classify:

```text
TARGET_DERIVED
```

These cannot be features for their own prediction task.

---

### Task 2A — historical demand inputs

Historical orders from:

```text
deliveries_train.csv
task1_test_inputs.csv
```

contribute demand history later.

Relevant demand facts include:

```text
delivery_id
order_date
depot
brand
temp_requirement
order_volume_m3
```

The later demand builder must count each order once, including deferred and `not_run`.

Phase 02 only records availability; it does not aggregate yet.

---

### Task 2A — future-known inputs

Official future forecast rows provide:

```text
row_id
depot
brand
forecast year/week fields
```

as observed locally.

Calendar features may be future-known if they are supplied for the forecast horizon:

```text
iso_year
iso_week
operating-day information
payday
festival
festival_ramp
holiday
monsoon
```

The actual future total/chilled demand remains unknown.

Classify final demand targets:

```text
TASK2A_UNKNOWN_FUTURE_TARGET
```

---

### Task 2B

Task 2B is not a supervised prediction task.

The peak-day scenario and fleet files provide scenario inputs such as:

```text
scenario
order_ref
outlet_id
brand
district
depot
dock_type
parking_constraint
mall_window
window_open_time
window_close_time
temp_requirement
order_units
order_weight_kg
order_volume_m3
deferred_yesterday
days_since_last_served
vehicle_id
status
```

Classify:

```text
TASK2B_SCENARIO_INPUT
```

Final:

```text
decision
vehicle_id
trip_id
```

in the submission template are outputs, not input labels.

### Output

Private:

```text
reports/private/phase02_inventory/availability_map.json
```

Tracked conceptual documentation may summarize the classification rules without observed private values.

### Automated safety assertion

The codebase should expose an explicit deny-list for Task 1 direct features:

```python
TASK1_TRAINING_ACTUAL_ONLY = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
}
```

This is not yet the complete future feature whitelist. It is an early safety guard.

### Tests

Synthetic tests must verify:

- actual fields are classified `TRAINING_ACTUAL_ONLY`;
- planned fields are not mistakenly classified as training actuals;
- target-derived fields are not feature inputs;
- Task 2A future target fields are unknown;
- Task 2B scenario inputs are not classified as ML targets.

### Definition of Done

- [ ] availability taxonomy exists;
- [ ] Task 1 actual fields are explicitly denied as direct prediction features;
- [ ] Task 1 planned fields distinguished from actuals;
- [ ] Task 2A historical/future distinction exists;
- [ ] Task 2B scenario inputs distinguished from outputs;
- [ ] ambiguous fields marked for later verification instead of guessed.

### STOP conditions

Phase 02 cannot pass if prediction-time availability is ambiguous for a field the team plans to use immediately in Phase 04/06.

---

# 8. Recommended `data_inventory.py` design

Keep the module small and auditable.

Recommended public functions:

```python
load_manifest(path: Path) -> dict

discover_dataset_files(
    raw_root: Path,
    manifest: dict,
) -> dict

inspect_csv_structure(
    path: Path,
) -> dict

build_data_dictionary(
    discovered: dict,
) -> dict

build_key_map(
    dictionary: dict,
    manifest: dict,
) -> dict

build_join_map(
    dictionary: dict,
) -> dict

classify_variables(
    dictionary: dict,
) -> dict

build_availability_map(
    dictionary: dict,
) -> dict

run_inventory(
    raw_root: Path,
    manifest_path: Path,
    output_dir: Path,
) -> dict
```

Do not add cleaning, imputation, profiling, modelling or feature engineering.

---

# 9. Recommended local CLI

Create:

```text
scripts/run_dataset_inventory.py
```

Recommended usage:

```bash
python scripts/run_dataset_inventory.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-dir reports/private/phase02_inventory
```

The CLI should:

1. refuse to write outside the configured private report area by default;
2. never print data rows;
3. print only:
   - overall PASS/FAIL;
   - missing filename names, if any;
   - duplicate official filename names, if any;
   - unreadable filename names, if any;
   - location of the private local report;
4. return exit code `0` for success;
5. return non-zero for blockers.

Recommended successful console output:

```text
PHASE 02 LOCAL INVENTORY: PASS
Required artifacts located: PASS
CSV loadability: PASS
Structural inventory written to local private report directory.
No row values were printed.
```

Do not print local row counts if the command is being observed by an AI agent.

---

# 10. Synthetic test strategy

Create:

```text
tests/test_data_inventory.py
```

All tests must use temporary synthetic files.

Minimum tests:

## File discovery

- all expected files found;
- missing required file;
- duplicate basename;
- unexpected extra artifact;
- nested folders;
- spaces in directory names.

## CSV loading

- valid CSV;
- header-only CSV;
- UTF-8 BOM;
- malformed CSV fails clearly;
- `.py` checker skipped by CSV loader.

## Schema capture

- exact header order retained;
- observed dtype metadata generated;
- no sample rows in output.

## Key metadata

- official/candidate key labels represented correctly.

## Join map

- Task 1 `route_id + seq_in_route` ↔ `route_id + seq`;
- no `outlet_id` allocation-key mistake for Task 2B.

## Variable type classification

- integer ID/code not automatically treated as continuous;
- binary flag classification;
- date/time/duration distinctions.

## Availability classification

- actual journey fields are `TRAINING_ACTUAL_ONLY`;
- target-derived fields are denied;
- planned fields remain eligible for later review;
- Task 2B scenario fields marked correctly.

## Privacy/output test

Inventory report must not contain synthetic row values beyond header/schema metadata.

Use clearly fake fixtures such as:

```text
delivery_id = SYNTH001
brand = DemoBrand
```

Do not copy a real competition record into tests.

---

# 11. Local operator execution checklist

After Cursor/Codex finishes the tooling and tests:

## Step 1 — exit the AI-agent execution path

Use a normal local terminal.

## Step 2 — confirm data safety

```bash
git status
git check-ignore -v data/raw/...
git check-ignore -v reports/private/phase02_inventory/...
```

## Step 3 — run tests

```bash
pytest -q tests/test_data_inventory.py
```

## Step 4 — run inventory locally

```bash
python scripts/run_dataset_inventory.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-dir reports/private/phase02_inventory
```

## Step 5 — do not paste the private report into AI tools

Inspect locally.

Confirm:

- every required official artifact exists;
- no duplicate required filename;
- every CSV loads;
- structural outputs are produced;
- no row values appear in console;
- no private report is Git-tracked.

## Step 6 — record only phase control result

You may update a local Phase 02 completion record with:

```text
LOCAL INVENTORY RUN: PASS
```

Do not copy raw data into the record.

---

# 12. Phase 02 edge cases

## Dataset is already inside `data/raw`

Do not move it unnecessarily.

Verify ignore rules, then run local inventory.

## Dataset remains zipped

DT-023 is not complete until the required artifacts are locally accessible to the inventory utility.

Do not make the inventory code read directly from ZIP unless the team deliberately changes the phase specification.

## Duplicate filenames

Example:

```text
data/raw/copy1/deliveries_train.csv
data/raw/copy2/deliveries_train.csv
```

This is a hard stop.

Do not pick one automatically.

## Renamed official file

Do not silently map:

```text
deliveries_train (1).csv
```

to:

```text
deliveries_train.csv
```

Resolve locally and preserve the official filename.

## Unexpected files

Record them locally.

Do not assume they are valid competition inputs.

## Empty/header-only template

A submission template may have structural behavior different from a training dataset.

Do not treat template row-count characteristics as modelling data-quality failures in Phase 02.

## Pandas dtype ambiguity

Columns with missing values can cause numeric integers to load as floats.

Record observed dtype only.

Semantic validation comes later.

## Traffic/road schema not fully described in booklet

Capture actual column names locally but do not invent semantics.

Fields not supported by the official documentation should remain:

```text
REQUIRES_LATER_VERIFICATION
```

## Mall window

Treat a value formatted like:

```text
HH:MM-HH:MM
```

as `time_range`, not a single clock time.

## Actual journey fields in Task 1 training

Do not delete them.

They are needed for label construction.

They are simply forbidden as direct prediction-time inputs.

---

# 13. Phase 02 STOP CONDITIONS

`READY FOR PHASE 03` must remain **NO** if any of the following is true:

- Phase 01 has not passed.
- raw data protection is not active.
- a required official file is missing.
- a required official file exists more than once.
- an official CSV cannot be loaded locally.
- official filenames were silently renamed.
- official column names were silently renamed.
- a core documented column is missing.
- file category is unresolved.
- Task 1 route relationship is documented incorrectly.
- `outlet_id` is being treated as Task 2B allocation key.
- actual Task 1 journey fields are classified as normal prediction-time features.
- target-derived fields are classified as model inputs.
- Task 2A future demand is classified as future-known.
- Task 2B is being converted into an ML target problem.
- private inventory reports are Git-tracked.
- raw rows appear in logs or console output.
- Cursor/Codex has been given unrestricted access to `data/raw`.
- a field meaning required immediately by the next phase remains unresolved.
- synthetic tests fail.
- local inventory run fails.

Do not continue to Phase 03 to "see if the issue matters."

---

# 14. Phase 02 Definition of Done

Phase 02 passes only when:

- [ ] DT-023 PASS
- [ ] DT-024 PASS
- [ ] DT-025 PASS
- [ ] DT-026 PASS
- [ ] DT-027 PASS
- [ ] DT-028 PASS
- [ ] DT-029 PASS
- [ ] DT-030 PASS
- [ ] DT-031 PASS
- [ ] DT-032 PASS
- [ ] DT-033 PASS
- [ ] DT-034 PASS
- [ ] DT-035 PASS
- [ ] expected artifact manifest contains all 18 official named artifacts
- [ ] all required artifacts found exactly once in the local run
- [ ] every official CSV loads locally
- [ ] row/column counts recorded privately
- [ ] all column names recorded privately
- [ ] local data dictionary generated
- [ ] official/candidate keys mapped
- [ ] Task 1 route join intent mapped correctly
- [ ] numerical variables classified
- [ ] categorical/identifier variables classified
- [ ] date/time/duration variables classified
- [ ] future-known/future-unknown map exists
- [ ] Task 1 actual-field deny-list exists
- [ ] no raw rows printed
- [ ] no private report committed
- [ ] synthetic unit tests pass
- [ ] local inventory run passes
- [ ] independent review passes
- [ ] no STOP condition remains unresolved

Only then:

```text
PHASE 02 STATUS: PASS
READY FOR PHASE 03: YES
```

---

# 15. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-02-dataset-inventory
```

Do not commit extracted competition files.

Recommended commits:

```text
chore(data): add official dataset manifest
feat(inventory): add privacy-safe dataset inventory tooling
test(inventory): add synthetic dataset inventory tests
docs(data): add official-source data dictionary
chore(safety): ignore private inventory reports
```

Before every commit:

```bash
git status
git diff --cached --name-only
```

Verify no path begins with:

```text
data/raw/
data/interim/
data/processed/
reports/private/
```

Verify no staged file is an official CSV/ZIP.

Suggested pre-merge checks:

```bash
pytest -q tests/test_project_setup.py tests/test_data_inventory.py
python -m pip check
git status
```

Do not merge until local operator inventory run and independent Phase 02 review both pass.

---

# 16. Recommended execution model

Because this phase touches restricted data, use:

```text
AI AGENT
↓
implements inventory code + manifest + synthetic tests
↓
STOP

HUMAN / LOCAL TERMINAL
↓
extracts/runs inventory against official data
↓
records PASS/FAIL only
↓
STOP

AI AGENT — FRESH REVIEW CHAT
↓
reviews code, tests, phase completion status
↓
does NOT open raw/private reports
↓
PASS/FAIL
```

Do not ask Cursor/Codex to execute the raw-data inventory on your behalf.

---

# 17. Enhanced Cursor implementation prompt

```text
We are implementing WayLoom Datathon PHASE 02 only.

PHASE:
Raw Dataset Inventory

TASK RANGE:
DT-023 through DT-035

READ FIRST:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved PHASE_00_COMPETITION_CONTRACT.md
3. approved PHASE_01_COMPETITION_CONTRACT.md
4. PHASE_02_COMPETITION_CONTRACT.md
5. official Challenge Booklet schema sections already available as documentation

SOURCE AUTHORITY:
Official organizer material > approved master plan > phase specification > implementation assumptions.

CRITICAL DATA-SAFETY MODE:

You MUST NOT open, read, inspect, summarize, sample or transmit any official competition dataset file.

Do not access:
data/raw/**
data/interim/**
data/processed/**
reports/private/**

Do not run commands that read official CSV contents.

Do not use:
head
tail
sample
cat
type
Get-Content
preview
CSV viewers
notebook display
or any equivalent command against official data.

Your role in this phase is to IMPLEMENT the privacy-safe local inventory tooling and synthetic tests.

The human operator will execute the final inventory script locally outside the AI-agent context.

DO NOT begin Phase 03.

IMPLEMENT ALL TASKS:

DT-023
Document the safe local extraction procedure for DataSet_New.zip.
Do not perform the extraction yourself.
Ensure the intended raw-data path is protected by .gitignore and .cursorignore.

DT-024
Create/verify configs/dataset_manifest.yaml containing all 18 official named artifacts and their official categories.
Implement recursive file discovery in src/common/data_inventory.py.
Detect missing and duplicate required filenames.
Do not inspect file contents.

DT-025
Categorize every expected artifact as:
training
test
general
templates
validation

DT-026
Implement CSV loadability checking for LOCAL HUMAN EXECUTION.
The loader may read official CSVs only when a human runs it later.
It must never print rows or serialize record values.
Create synthetic tests for valid, malformed, header-only and BOM CSVs.
Exclude check_allocation.py from CSV loading.

DT-027
Implement row_count and column_count collection into the PRIVATE ignored report.
Do not hardcode real dataset counts.
Do not print counts to AI-observed console during the real run.

DT-028
Implement exact column-name capture.
Preserve spelling/order.
Do not rename columns.
Create docs/data_dictionary_official.md using only organizer-documented schema information.

DT-029
Implement local data-dictionary generation with:
filename
category
grain
row_count
column_count
column_name
observed_dtype
semantic_type
official_format
official_meaning
availability_class
notes

Do NOT add:
means
min/max
quantiles
unique category values
missing counts
outliers
row samples

Those belong to later phases.

DT-030
Create key metadata.
Distinguish:
OFFICIAL_KEY
OFFICIAL_COMPOSITE_KEY
CANDIDATE_KEY_VERIFY_PHASE_03
NO_PRIMARY_KEY_REQUIRED

Preserve official keys:
delivery_id
leg_id
row_id
order_ref
outlet_id
vehicle_id
calendar date
brand+dock_type where officially supported.

Do not falsely verify candidate-key uniqueness in this phase.

DT-031
Create the relational join map.

The critical official Task 1 join MUST be:

deliveries_train:
route_id + seq_in_route

to:

route_legs_train:
route_id + seq

and equivalent Task 1 test relationship.

Also document safe reference joins supported by official fields.

Do not use outlet_id as the Task 2B allocation key.

DT-032
Implement numerical semantic classification.
Distinguish:
continuous measurements
counts
durations
binary indicators
ordinal positions

Do not use Pandas dtype alone as semantic meaning.

DT-033
Implement categorical/identifier classification.
Keep identifiers separate from ordinary categorical features.

DT-034
Implement date/time classification.
Distinguish:
date
clock_time
time_range
numeric_duration

Record Asia/Colombo convention.
Do not perform Task 1 midnight logic yet.

DT-035
Implement the prediction-time availability taxonomy:

KNOWN_AT_TASK1_PREDICTION
TRAINING_ACTUAL_ONLY
TARGET_DERIVED
STATIC_REFERENCE
FUTURE_CALENDAR_KNOWN
TASK2A_HISTORICAL_DEMAND
TASK2A_UNKNOWN_FUTURE_TARGET
TASK2B_SCENARIO_INPUT
SUBMISSION_OUTPUT_ONLY
NOT_APPLICABLE
REQUIRES_LATER_VERIFICATION

Create an explicit Task 1 deny-list containing:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

These fields are historical actuals and must never become direct Task 1 prediction-time features.

Target-derived fields such as:
service_start
service_min
late_flag

must never be model inputs for their own target.

CREATE/VERIFY:

configs/dataset_manifest.yaml
src/common/data_inventory.py
scripts/run_dataset_inventory.py
docs/data_dictionary_official.md
tests/test_data_inventory.py

Update:
.gitignore
.cursorignore

to protect:

reports/private/**

The local CLI should write only to:

reports/private/phase02_inventory/

Expected private files may include:

inventory.json
data_dictionary.json
join_map.json
variable_types.json
availability_map.json
validation_summary.json

DO NOT OPEN THESE PRIVATE OUTPUTS IN CURSOR.

LOCAL CLI CONTRACT:

python scripts/run_dataset_inventory.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-dir reports/private/phase02_inventory

The CLI must:
- never print row values
- never print DataFrames
- return non-zero on missing/duplicate/unreadable required artifacts
- print only high-level PASS/FAIL and blocker filenames
- write detailed structural metadata only to the ignored private directory

TESTING:

All automated tests must use synthetic temporary datasets only.

Run:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py
python -m pip check

Do NOT run the real inventory CLI against data/raw.

Do NOT inspect reports/private.

After implementation, return:

PHASE: 02 — AGENT IMPLEMENTATION STAGE

TASK IMPLEMENTATION:
DT-023 READY / FAIL
DT-024 READY / FAIL
DT-025 READY / FAIL
DT-026 READY / FAIL
DT-027 READY / FAIL
DT-028 READY / FAIL
DT-029 READY / FAIL
DT-030 READY / FAIL
DT-031 READY / FAIL
DT-032 READY / FAIL
DT-033 READY / FAIL
DT-034 READY / FAIL
DT-035 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

SYNTHETIC TESTS:
...

DATA-SAFETY CHECK:
Did you access data/raw? MUST BE NO
Did you access reports/private? MUST BE NO
Did any official row/value enter context? MUST BE NO

LOCAL HUMAN ACTION REQUIRED:
YES

Provide only the exact local command the human should run.

PHASE 02 FINAL STATUS:
AWAITING LOCAL INVENTORY RUN

READY FOR PHASE 03:
NO

Then STOP.

Do not perform the local run.
Do not start Phase 03.
```

---

# 18. Enhanced Codex implementation prompt

```text
Implement WayLoom Datathon Phase 02 tooling only.

PHASE:
Raw Dataset Inventory

TASKS:
DT-023 through DT-035

AUTHORITATIVE FILES:
- WAYLOOM_DATATHON_MASTER_PLAN.md
- approved Phase 00 contract
- approved Phase 01 contract
- PHASE_02_COMPETITION_CONTRACT.md
- official competition schema documentation

IMPORTANT:
The official competition data is restricted.

You are NOT authorized in this task to inspect the actual dataset contents.

Do not open or read any file under:

data/raw/
data/interim/
data/processed/
reports/private/

Do not execute any script against official data.

Use only:
- repository code
- official schema documentation
- synthetic test fixtures you create yourself

The human operator will run the completed tooling locally after you stop.

IMPLEMENT ALL PHASE 02 TASKS.

1. DT-023 — extraction procedure
Document the safe local extraction process.
Verify code/config supports data under data/raw.
Do not extract the archive yourself.

2. DT-024 — file inventory
Create configs/dataset_manifest.yaml containing the 18 expected official artifacts:

TRAINING:
deliveries_train.csv
route_legs_train.csv

TEST:
task1_test_inputs.csv
route_legs_test.csv
task2a_test_inputs.csv
task2b_peak_day_scenarios.csv
task2b_peak_day_fleet.csv

GENERAL:
outlets.csv
vehicles.csv
calendar.csv
district_travel.csv
service_allowance.csv
traffic_speed.csv
road_conditions.csv

TEMPLATES:
submission_task1.csv
submission_task2a.csv
submission_task2b.csv

VALIDATION:
check_allocation.py

Implement recursive discovery.
Missing and duplicate required basenames are blockers.

3. DT-025 — file categories
Enforce one official category per required artifact.

4. DT-026 — local CSV loadability
Implement a loader designed for human/local execution.
Never display rows.
Capture only structural metadata.
Create synthetic parser tests.

5. DT-027 — row/column counts
Capture counts privately during local run.
Do not hardcode or print real counts.

6. DT-028 — columns
Capture exact observed header names/order privately.
Create docs/data_dictionary_official.md from official documented schemas only.

7. DT-029 — data dictionary
Generate structural dictionary only.
No statistical profiling and no values.

8. DT-030 — keys
Represent keys using:
OFFICIAL_KEY
OFFICIAL_COMPOSITE_KEY
CANDIDATE_KEY_VERIFY_PHASE_03
NO_PRIMARY_KEY_REQUIRED

Do not verify uniqueness yet.

9. DT-031 — joins
Critical relationship:

deliveries route_id + seq_in_route
↔
route legs route_id + seq

Document equivalent train/test relationship.

Never use outlet_id as Task 2B allocation key.
order_ref is the scenario allocation key.

10. DT-032 — numerical variables
Classify measures/counts/durations/binary/positions semantically.

11. DT-033 — categorical variables
Separate identifiers from ordinary categorical fields.

12. DT-034 — date/time variables
Separate:
date
clock_time
time_range
duration

Record Asia/Colombo.
Do not implement later time arithmetic.

13. DT-035 — prediction availability
Create explicit availability classes and a Task 1 direct-feature deny-list:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

Also classify:
service_start
service_min
late_flag

as target-derived rather than prediction inputs.

CREATE:

configs/dataset_manifest.yaml
src/common/data_inventory.py
scripts/run_dataset_inventory.py
docs/data_dictionary_official.md
tests/test_data_inventory.py

UPDATE SAFELY:

.gitignore
.cursorignore

Add:

reports/private/**

PRIVATE LOCAL OUTPUT CONTRACT:

reports/private/phase02_inventory/
  inventory.json
  data_dictionary.json
  join_map.json
  variable_types.json
  availability_map.json
  validation_summary.json

Never read those files yourself.

CLI:

python scripts/run_dataset_inventory.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-dir reports/private/phase02_inventory

CLI RULES:
- no row printing
- no DataFrame printing
- no samples
- non-zero exit on missing/duplicate/unreadable required artifact
- detailed structural metadata goes only to ignored private output
- console contains only concise PASS/FAIL and blocker filename names

TESTS:
Use synthetic temp files only.

Test:
- expected file discovery
- missing file
- duplicate filename
- unexpected file
- nested folders
- paths with spaces
- valid CSV
- malformed CSV
- BOM CSV
- header-only CSV
- exact column ordering
- no row values in structural output
- key metadata
- Task 1 join mapping
- Task 2B order_ref rule
- numerical semantic types
- categorical/identifier distinction
- date/time/duration distinction
- availability classes
- Task 1 actual-field deny-list

RUN ONLY:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py
python -m pip check

Do not run anything that reads data/raw.

Do not inspect private reports.

STOP CONDITIONS:
Follow every STOP condition in PHASE_02_COMPETITION_CONTRACT.md.
If the implementation cannot be completed without reading official data, stop and report why.

RETURN:

PHASE 02 — CODE/TOOLING STAGE

DT-023 READY/FAIL
DT-024 READY/FAIL
DT-025 READY/FAIL
DT-026 READY/FAIL
DT-027 READY/FAIL
DT-028 READY/FAIL
DT-029 READY/FAIL
DT-030 READY/FAIL
DT-031 READY/FAIL
DT-032 READY/FAIL
DT-033 READY/FAIL
DT-034 READY/FAIL
DT-035 READY/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TESTS:
...

DATA ACCESS:
Official raw files opened: NO
Private reports opened: NO
Official row values observed: NO

HUMAN LOCAL RUN REQUIRED:
YES

Print the local run command only.

PHASE 02 STATUS:
AWAITING LOCAL RUN

READY FOR PHASE 03:
NO

Then STOP.
```

---

# 19. Enhanced Phase 02 review prompt

Use this in a **fresh AI chat after the human local run**.

Do not give the private inventory report to the reviewer.

```text
Perform an independent review of WayLoom Datathon Phase 02.

DO NOT:
- open data/raw
- open data/interim
- open data/processed
- open reports/private
- execute the real inventory CLI
- inspect official competition rows
- begin Phase 03
- fix code initially

READ:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_02_COMPETITION_CONTRACT.md
3. configs/dataset_manifest.yaml
4. src/common/data_inventory.py
5. scripts/run_dataset_inventory.py
6. docs/data_dictionary_official.md
7. tests/test_data_inventory.py
8. .gitignore
9. .cursorignore

The human operator has separately run the inventory against official local data.

Human-supplied control result:

LOCAL PHASE 02 INVENTORY RUN: <PASS / FAIL>

Do not ask for private report contents.

AUDIT:

DT-023
- safe extraction procedure exists
- no agent extraction/access required

DT-024
- manifest includes exactly the required official named artifacts
- recursive discovery implemented
- missing/duplicate artifacts block success

DT-025
- training/test/general/templates/validation categorization is correct

DT-026
- CSV loadability implementation never outputs row contents
- check_allocation.py excluded
- parser failures are explicit

DT-027
- row/column counts are private structural metadata
- real counts are not hardcoded into tracked code/docs

DT-028
- column names/order captured without renaming
- official dictionary uses organizer-documented meanings only

DT-029
- dictionary is structural only
- no EDA/missing/outlier/value profiling added prematurely

DT-030
- official keys and candidate keys are distinguished
- uniqueness is not falsely claimed before Phase 03
- Task 2B outlet_id is not used as allocation key

DT-031
- Task 1 join is exactly:
  route_id + seq_in_route
  ↔
  route_id + seq
- reference joins are documented without invented assumptions

DT-032
- numeric measures/counts/durations/binary/positions are semantically distinguished

DT-033
- identifiers are separated from ordinary categoricals

DT-034
- dates, clock times, time ranges and durations are separated
- Asia/Colombo convention captured

DT-035
- availability taxonomy exists
- actual Task 1 journey fields are TRAINING_ACTUAL_ONLY
- target-derived fields cannot become predictors
- Task 2A future demand is unknown
- Task 2B is treated as a scenario/optimization task

PRIVACY/SAFETY:
- reports/private/** ignored by Git
- reports/private/** excluded from Cursor
- raw data remains ignored
- no tests contain real records
- no code logs/prints DataFrames or records
- local CLI does not emit row values

RUN ONLY SAFE TESTS:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py
python -m pip check
git status

Do not execute against raw data.

RETURN TABLE:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

SYNTHETIC TEST STATUS:
PASS / FAIL

HUMAN LOCAL INVENTORY STATUS:
PASS / FAIL

DATA-SAFETY REVIEW:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-023: PASS/FAIL
DT-024: PASS/FAIL
DT-025: PASS/FAIL
DT-026: PASS/FAIL
DT-027: PASS/FAIL
DT-028: PASS/FAIL
DT-029: PASS/FAIL
DT-030: PASS/FAIL
DT-031: PASS/FAIL
DT-032: PASS/FAIL
DT-033: PASS/FAIL
DT-034: PASS/FAIL
DT-035: PASS/FAIL

PHASE 02 REVIEW:
PASS / FAIL

READY FOR PHASE 03:
YES / NO

If FAIL:
list only exact blockers.

Do not fix them until explicitly approved.
Do not start Phase 03.
```

---

# 20. Local Phase 02 completion record template

```markdown
# Phase 02 Completion Record

## Agent tooling stage

- [ ] DT-023 tooling/docs ready
- [ ] DT-024 ready
- [ ] DT-025 ready
- [ ] DT-026 ready
- [ ] DT-027 ready
- [ ] DT-028 ready
- [ ] DT-029 ready
- [ ] DT-030 ready
- [ ] DT-031 ready
- [ ] DT-032 ready
- [ ] DT-033 ready
- [ ] DT-034 ready
- [ ] DT-035 ready

## Synthetic tests

- `pytest -q tests/test_project_setup.py tests/test_data_inventory.py`: PASS / FAIL
- `python -m pip check`: PASS / FAIL

## Local restricted-data run

- Dataset extraction: PASS / FAIL
- Required artifact discovery: PASS / FAIL
- Duplicate required artifacts: NONE / BLOCKER
- CSV loadability: PASS / FAIL
- Structural inventory generated: PASS / FAIL
- No row values printed: YES / NO
- Private inventory ignored by Git: YES / NO

Do not paste private report contents here.

## Review

- Independent Phase 02 review: PASS / FAIL
- STOP conditions unresolved: YES / NO

## Verdict

PHASE 02 STATUS: PASS / FAIL

READY FOR PHASE 03: YES / NO
```

---

# 21. Phase 02 final checklist

Before Phase 03:

- [ ] Phase 01 passed.
- [ ] Dataset extracted locally in protected storage.
- [ ] All 18 expected named official artifacts are represented in the manifest.
- [ ] All required artifacts are found exactly once locally.
- [ ] Every required CSV loads locally.
- [ ] Structural row/column counts exist privately.
- [ ] Exact column names exist privately.
- [ ] Official-source data dictionary exists.
- [ ] Local structural dictionary exists privately.
- [ ] Keys are mapped.
- [ ] Joins are mapped.
- [ ] Numeric fields classified.
- [ ] Categorical/identifier fields classified.
- [ ] Date/time/duration fields classified.
- [ ] Prediction-time availability map exists.
- [ ] Task 1 historical actual deny-list exists.
- [ ] No real rows appear in tests.
- [ ] No raw/private records appear in logs.
- [ ] Private reports are ignored.
- [ ] Synthetic tests pass.
- [ ] Local operator inventory passes.
- [ ] Independent review passes.
- [ ] No STOP condition remains.

Only then:

```text
PHASE 02 STATUS: PASS
READY FOR PHASE 03: YES
```

Do not automatically continue to Phase 03.
