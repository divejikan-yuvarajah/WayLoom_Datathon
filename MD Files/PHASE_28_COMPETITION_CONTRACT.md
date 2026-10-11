# PHASE 28 — Optional WayLoom Integration Contract

> **Filename:** `PHASE_28_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 28 — Optional WayLoom Integration Contract  
> **Task range:** **DT-362 → DT-373**  
> **Task count:** **12**  
> **Phase dependency:** **Final Task 1 / Task 2A / Task 2B outputs**  
> **Default phase priority:** **P2**  
> **Master phase gate:** If implemented, integration uses schemas/synthetic examples and never exposes restricted competition data.  
> **Execution mode:** Hybrid / optional; schema-first, synthetic-demo-first, privacy-fail-closed.  
> **Critical rule:** This phase must never block the official Datathon submission.

---

# 1. Phase 28 purpose

Phase 28 creates a safe, versioned integration boundary between the completed WayLoom Datathon work and the team's Hackathon/UI work.

The official Challenge Booklet explicitly says:

```text
The Datathon challenge is judged separately from the Hackathon system.

Teams are not required to integrate their Datathon solutions into their
Hackathon build.
```

Therefore Phase 28 is **optional**.

Its purpose is not to turn the Datathon into a production web service.

Its purpose is to make the Datathon outputs easy to understand and prototype against using:

```text
JSON schemas

synthetic response examples

an optional local FastAPI service

a safe model-registry interface

privacy guards

a shareable integration package
```

The design must guarantee that restricted competition test records do not become public through the API, OpenAPI examples, frontend mocks, logs, or shared package.

---

# 2. Finalized Phase 28 master inventory

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-362** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define Task 1 JSON schema |
| [ ] | **DT-363** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define demand forecast JSON schema |
| [ ] | **DT-364** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define allocation insight JSON schema |
| [ ] | **DT-365** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define deferral explanation schema |
| [ ] | **DT-366** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Create synthetic demo responses |
| [ ] | **DT-367** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Share integration contract with Hackathon team |
| [ ] | **DT-368** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Build optional FastAPI service |
| [ ] | **DT-369** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement model loading endpoint |
| [ ] | **DT-370** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement delivery-risk endpoint |
| [ ] | **DT-371** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement demand-forecast endpoint |
| [ ] | **DT-372** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement allocation endpoint |
| [ ] | **DT-373** | [O] | P0 | Final Task 1/2A/2B outputs; optional and must not block submission | Prevent official private test records from becoming public |

**Expected Phase 28 tasks:** 12  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 29:** NO

---

# 3. Official requirements relevant to Phase 28

The official booklet establishes four constraints that dominate this phase.

## 3.1 Integration is not required

The Datathon is judged separately from the Hackathon and does not require system integration.

Therefore:

```text
Phase28 failure must not invalidate an otherwise valid Datathon submission.
```

If this optional integration becomes risky or time-consuming:

```text
stop the optional work
preserve required submission artifacts
continue required documentation/packaging phases
```

Do not compromise the competition submission to force an integration demo.

## 3.2 Data sharing restriction

The official terms say competition datasets must not be shared, distributed, or transmitted to third parties.

They also prohibit public disclosure of datasets or derivatives unless explicitly authorized.

Therefore Phase 28 must not create a public interface over private competition test rows.

## 3.3 API/model restriction

The official rules prohibit proprietary API-based modelling/preprocessing.

Phase 28 must not introduce an external prediction API.

A locally run FastAPI wrapper around already-frozen WayLoom artifacts is an engineering interface, not an external modelling API.

## 3.4 Official outputs remain unchanged

Task 1, Task 2A and Task 2B official outputs retain their exact existing contracts.

Phase 28 JSON schemas are **integration schemas**, not replacements for official CSV schemas.

---

# 4. Integration source-of-truth hierarchy

Use:

```text
Official Challenge Booklet
↓
official template/checker contracts
↓
frozen Phase10 Task1 interface
↓
frozen Phase17 Task2A interface
↓
frozen Phase21/22/24 Task2B semantics
↓
optional Phase26 deferral explanation
↓
optional Phase27 uncertainty
↓
Phase28 integration presentation
```

Phase 28 may adapt existing outputs.

It may not silently redefine them.

---

# 5. Preconditions

Before implementing Phase 28, require the completed scope to have valid frozen/final artifacts:

```text
Task1:
final models/config frozen
submission_task1.csv final

Task2A:
final models/config frozen
submission_task2a.csv final

Task2B:
frozen allocation
submission_task2b.csv final
task2b_policy.md final
```

Phase 26 and 27 are optional dependencies:

```text
Phase26 absent:
deferral explanation schema still exists,
real counterfactual content marked unavailable.

Phase27 absent:
uncertainty fields absent/optional.
```

Phase 28 must not require either optional phase.

---

# 6. Frozen artifact boundary

Do not modify:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
Task2A final model/runtime artifacts
outputs/submission_task2a.csv

data/interim/task2b_final_allocation.csv
data/interim/task2b_final_trip_summary.csv
outputs/submission_task2b.csv
docs/task2b_policy.md
```

Do not rewrite official CSVs just to make them easier to serve.

Create adapters instead.

---

# 7. Recommended repository structure

```text
src/
└── integration/
    ├── __init__.py
    ├── models.py
    ├── schemas.py
    ├── privacy.py
    ├── synthetic_data.py
    ├── adapters.py
    ├── model_registry.py
    └── service.py

app/
└── integration_api.py

schemas/
└── integration/
    ├── task1.schema.json
    ├── demand_forecast.schema.json
    ├── allocation_insight.schema.json
    └── deferral_explanation.schema.json

examples/
└── integration/
    ├── task1_response.synthetic.json
    ├── demand_forecast_response.synthetic.json
    ├── allocation_response.synthetic.json
    └── deferral_explanation.synthetic.json

docs/
└── integration/
    ├── WAYLOOM_INTEGRATION_CONTRACT.md
    ├── PRIVACY_AND_DATA_BOUNDARY.md
    └── FASTAPI_SERVICE.md

scripts/
├── export_integration_contract.py
└── validate_integration_contract.py

configs/
└── integration.yaml

tests/
├── test_integration_schemas.py
├── test_integration_synthetic_examples.py
├── test_integration_privacy.py
├── test_integration_model_registry.py
├── test_integration_api.py
└── test_integration_contract_export.py
```

---

# 8. Core architectural rule: schema-first

Phase 28 should be built in this order:

```text
1. schemas
2. synthetic examples
3. privacy guard
4. shareable contract
5. optional FastAPI
6. optional private-local model adapters
```

Do not start by wiring real competition data into HTTP routes.

---

# 9. Core architectural rule: synthetic-first

Default runtime mode:

```text
synthetic_demo
```

In this mode the service must work if these directories/files do not exist:

```text
data/raw/
data/interim/
reports/private/

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

models/task1_service/
models/task1_late/
Task2A real model artifacts
```

This property is a major privacy guarantee.

---

# 10. Recommended integration config

Create:

```text
configs/integration.yaml
```

Suggested:

```yaml
version: 1
contract_version: 1.0.0
mode: synthetic_demo

network:
  default_host: 127.0.0.1
  default_port: 8088
  cors_allow_origins: []

privacy:
  allow_competition_records: false
  allow_private_paths: false
  redact_paths_in_errors: true
  log_request_bodies: false
  log_response_bodies: false

models:
  allow_real_model_loading: false

synthetic:
  seed: 42

phase26:
  enabled_if_available: true

phase27:
  expose_uncertainty_if_available: false
```

Real model/private mode requires an explicit override.

---

# 11. Contract versioning

Start with:

```text
1.0.0
```

Use semantic versioning:

```text
major:
breaking field/endpoint change

minor:
additive optional field/endpoint

patch:
documentation/fixture correction
```

Every JSON schema should include a stable schema version.

Do not tie external consumers to a Git hash.

---

# 12. DT-362 — Define Task 1 JSON schema

The Task 1 integration response must preserve official semantics:

```text
pred_service_min
=
predicted outlet handling time in minutes

pred_late_prob
=
probability of arrival after delivery window close
```

Recommended response model:

```json
{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "delivery_ref": "DEMO_DELIVERY_001",
  "prediction": {
    "pred_service_min": 18.4,
    "pred_late_prob": 0.27
  },
  "model_status": {
    "service_model": "synthetic",
    "late_model": "synthetic"
  }
}
```

---

# 13. Task 1 integration identifier

Use:

```text
delivery_ref
```

in public/synthetic integration responses.

Do not imply this is an official `delivery_id`.

In an authorized local adapter, `delivery_id` may exist internally, but the public/synthetic schema should not require real official IDs.

This prevents accidental copy/paste of private test identifiers into a frontend demo.

---

# 14. Task 1 numeric validation

Require:

```text
pred_service_min:
finite
>= 0

pred_late_prob:
finite
>= 0
<= 1
```

Reject:

```text
NaN
Inf
negative service time
probability outside [0,1]
```

---

# 15. Task 1 request contract

The live/private request schema must derive from the frozen Task 1 inference contract.

Do not invent a new feature contract.

The request adapter must reject training-only actual outcome fields including:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

If the frozen inference contract cannot be safely exposed as a small public request:

the public synthetic endpoint should use a synthetic request envelope and deterministic mock output.

Do not weaken the frozen inference validator.

---

# 16. Task 1 request privacy

Do not accept:

```text
raw CSV path
dataset path
delivery_id list from official test
arbitrary Python object
pickled object
```

The request should be a JSON document validated by Pydantic/JSON Schema.

---

# 17. DT-363 — Define demand forecast JSON schema

The integration contract must preserve Task 2A meaning.

Recommended:

```json
{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "forecast_ref": "DEMO_FORECAST_001",
  "depot": "Demo Depot",
  "brand": "Fresh",
  "iso_year": 2026,
  "iso_week": 42,
  "forecast_horizon": 1,
  "pred_total_volume_m3": 12.5,
  "pred_chilled_volume_m3": 7.1
}
```

---

# 18. Demand forecast invariants

Require:

```text
pred_total_volume_m3 >= 0

pred_chilled_volume_m3 >= 0

pred_chilled_volume_m3 <= pred_total_volume_m3
```

For:

```text
Style
Tech
```

require:

```text
pred_chilled_volume_m3 == 0
```

These rules mirror the frozen Task 2A output semantics.

---

# 19. Demand forecast request

Recommended public request:

```json
{
  "depot": "Demo Depot",
  "brand": "Fresh",
  "iso_year": 2026,
  "iso_week": 42
}
```

Optional:

```text
forecast_horizon
```

Do not expose official private `row_id` in the public demo contract.

Synthetic mode should only resolve synthetic fixture combinations.

---

# 20. Optional uncertainty extension

If Phase 27 is implemented, an optional nested object may be added:

```json
{
  "uncertainty": {
    "status": "unofficial",
    "target_coverage": 0.90,
    "total_lower_m3": 10.2,
    "total_upper_m3": 15.8
  }
}
```

Requirements:

- optional;
- clearly unofficial;
- absent when Phase27 not available;
- not part of official Task 2A CSV.

Do not make Phase 28 depend on Phase 27.

---

# 21. DT-364 — Define allocation insight JSON schema

Task 2B official output is row-level.

The integration schema should instead expose a **safe aggregate insight**.

Recommended:

```json
{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "scenario_ref": "DEMO_SCENARIO_01",
  "summary": {
    "orders_total": 12,
    "orders_served": 10,
    "orders_deferred": 2,
    "vehicles_used": 5,
    "trips_used": 7
  },
  "constraint_summary": {
    "max_trips_per_vehicle": 2,
    "fresh_vehicle_minutes_limit": 270,
    "style_tech_vehicle_minutes_limit": 480
  },
  "reasoning": {
    "policy_name": "WayLoom lexicographic allocation policy",
    "hard_rules_precede_policy": true
  }
}
```

This is not an official submission format.

---

# 22. Allocation insight invariants

Require:

```text
orders_total >= 0

orders_served >= 0

orders_deferred >= 0

orders_served + orders_deferred == orders_total

vehicles_used >= 0

trips_used >= 0
```

Official limits exposed in the schema must be exact:

```text
max_trips_per_vehicle = 2

Fresh vehicle minutes <= 270

Style+Tech vehicle minutes <= 480
```

Do not introduce fuel/window/return-leg constraints.

---

# 23. Allocation policy summary

If the integration response describes priority, it must match Phase 21 exactly:

```text
1 maximize served orders

2 maximize served previous-deferred orders

3 maximize served waiting-days sum

4 maximize served low-flexibility orders

5 maximize Fresh chilled served

6 maximize Fresh served

7A minimize avoidable reefer-van use

7B minimize avoidable reefer use

7C minimize avoidable van use
```

Clearly label:

```text
WayLoom engineering policy
```

not:

```text
organizer-mandated priority.
```

---

# 24. Allocation privacy

Public/synthetic response must not contain:

```text
order_ref
outlet_id
vehicle_id
trip_id

order-to-vehicle mapping
trip member list
deferred order list
```

Even aggregate live data should be avoided in a public internet deployment unless explicitly authorized.

Default demo values are synthetic.

---

# 25. DT-365 — Define deferral explanation schema

Define a stable schema that works with or without Phase 26.

Recommended:

```json
{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "example_ref": "DEFERRAL_EXAMPLE_A",
  "availability": "synthetic_demo",
  "reason_class": "POLICY_TRADEOFF",
  "primary_reason_code": "LOWER_POLICY_PRIORITY",
  "secondary_reason_codes": [
    "TRIP_SLOT_LIMIT"
  ],
  "summary": "Synthetic explanation text.",
  "evidence": {
    "counterfactual_complete": true,
    "first_degraded_policy_tier": "LEVEL_2",
    "changed_order_count": 3
  },
  "limitations": "Optimization explanation under frozen rules/policy; not causal."
}
```

---

# 26. Deferral explanation enums

If Phase 26 is implemented, accepted high-level classes:

```text
UNAVOIDABLE_HARD

POLICY_TRADEOFF

ALTERNATIVE_OPTIMUM
```

Availability:

```text
available

not_available

synthetic_demo
```

When:

```text
availability = not_available
```

reason/evidence fields may be null.

Do not fabricate a real reason when Phase 26 is absent.

---

# 27. Reason-code compatibility

If Phase 26 exists:

reuse its stable reason-code registry.

Do not maintain an independent duplicate enum that can drift.

If only synthetic schema is available:

use the published vocabulary from the Phase 26 contract and mark the response synthetic.

---

# 28. Deferral explanation limitations

Every explanation schema should support a limitation field equivalent to:

> This is an optimization explanation under the frozen Task 2B scenario, official feasibility rules and WayLoom policy. It is not a real-world causal claim.

Do not write:

```text
AI decided
the AI caused
the order was definitely impossible
```

unless hard infeasibility is actually proven.

---

# 29. DT-366 — Create synthetic demo responses

Create safe tracked examples for all integration schemas.

They must be useful enough for the Hackathon team to:

```text
build UI cards
build charts
test loading states
test error states
prototype dispatcher views
prototype explanation panels
```

without needing competition records.

---

# 30. Required synthetic examples

At minimum:

```text
Task1:
delivery-risk response

Task2A:
Fresh forecast response

Task2A:
Style or Tech zero-chilled response

Task2B:
allocation aggregate response

Deferral:
hard-unavoidable synthetic response

Deferral:
policy-tradeoff synthetic response
```

Optionally:

```text
alternative optimum example

error response examples
```

---

# 31. Synthetic ID rules

Use obviously synthetic IDs:

```text
DEMO_DELIVERY_001

DEMO_FORECAST_001

DEMO_SCENARIO_01

DEFERRAL_EXAMPLE_A
```

Never:

```text
copy an official ID

take a real ID and change one digit

hash a real ID and expose the hash
```

A hash is still a derivative identifier and can create unnecessary linkage risk.

---

# 32. Synthetic numeric values

Synthetic values must be:

```text
plausible
internally consistent
not copied from private rows
```

Examples may use generic values chosen by code.

Do not sample from real private row distributions at runtime for tracked fixtures.

The fixture generator must work with no competition data present.

---

# 33. Synthetic generator

Recommended:

```text
src/integration/synthetic_data.py
```

Use deterministic seed:

```text
42
```

Better yet, use fixed explicit fixtures where random generation adds no value.

A stable mock contract is easier for frontend development.

---

# 34. DT-367 — Share integration contract with Hackathon team

Create a shareable package.

Recommended:

```text
dist/integration_contract/
├── README.md
├── contract_version.json
├── schemas/
├── examples/
├── openapi.json
├── PRIVACY_AND_DATA_BOUNDARY.md
└── manifest.json
```

Optional archive:

```text
dist/WayLoom_Integration_Contract_Synthetic.zip
```

This package may be shared with the Hackathon teammates.

---

# 35. Share-package allowlist

Allow only:

```text
documentation

JSON schemas

synthetic JSON examples

OpenAPI spec from synthetic service

version/changelog

manifest/hash list
```

Reject:

```text
data/raw/**

data/interim/**

reports/private/**

outputs/submission_task*.csv

models/**

private logs

notebook outputs containing private records
```

---

# 36. Contract manifest

Create:

```text
manifest.json
```

with:

```text
contract_version

generated_at

file list

SHA256 for each exported file

privacy_mode = synthetic_only
```

Do not include:

```text
absolute local paths

private source hashes

competition row IDs
```

---

# 37. No Hackathon dependency

Sharing the contract does not create a required dependency.

Record status as:

```text
optional_shared
```

The Datathon must remain complete even if the Hackathon team does not integrate it.

Do not:

- wait for UI changes;
- change models to satisfy frontend convenience;
- delay Datathon packaging;
- put Hackathon app secrets into this repo.

---

# 38. DT-368 — Build optional FastAPI service

Build a local demo service whose **default mode is synthetic**.

Recommended route set:

```text
GET  /health

GET  /v1/contract

POST /v1/models/load

POST /v1/delivery-risk

POST /v1/demand-forecast

POST /v1/allocation-insight

GET  /v1/demo/deferral-explanations
```

FastAPI itself is an engineering recommendation, not an official requirement.

---

# 39. FastAPI startup contract

Synthetic mode must start successfully without:

```text
competition data

official submissions

frozen model files

private reports
```

This should be validated in tests.

If import/startup touches those files:

privacy architecture is wrong.

---

# 40. FastAPI default network safety

Recommended default:

```text
host:
127.0.0.1

port:
8088

CORS:
empty allowlist
```

Do not default to:

```text
0.0.0.0

allow_origins = ["*"]
```

The user may explicitly configure a known local frontend origin.

---

# 41. Synthetic vs private-local modes

Supported:

```text
synthetic_demo
```

Optional:

```text
private_local
```

Do not implement:

```text
public_real_data
```

as a supported mode.

If a future deployment is needed, it requires a separate privacy/security review.

---

# 42. Private-local mode

Private-local mode may:

- load frozen models from allowlisted config;
- accept team-created/synthetic requests;
- return predictions locally.

It must not:

- expose official test rows;
- expose official submission table lookup;
- provide batch download of private predictions;
- return private diagnostic reports;
- bind publicly by default.

Explicit opt-in recommended:

```text
WAYLOOM_INTEGRATION_MODE=private_local

WAYLOOM_ALLOW_REAL_MODELS=1
```

---

# 43. Error handling

API responses must not contain:

```text
stack traces

absolute Windows/Linux paths

environment variables

model file paths

raw exception repr containing paths

private IDs
```

Use generic errors with:

```text
error_code

safe message

request_id
```

Detailed traceback remains local developer-only.

---

# 44. Logging

Default logs may contain:

```text
request method

route

status code

latency

service mode

request_id
```

Do not log:

```text
request body

response body

feature vectors

private IDs

filesystem paths
```

---

# 45. DT-369 — Implement model loading endpoint

Recommended route:

```text
POST /v1/models/load
```

This endpoint must load/check only **preconfigured** artifacts.

It must not accept a filesystem path from the caller.

---

# 46. Model-load request

Recommended:

```json
{
  "load": true
}
```

or no body.

Do not allow:

```json
{
  "model_path": "..."
}
```

Do not allow:

```text
config_path
pickle_path
directory
URL
```

---

# 47. Synthetic model-load response

Example:

```json
{
  "mode": "synthetic_demo",
  "real_models_loaded": false,
  "models": {
    "task1_service": "synthetic",
    "task1_late": "synthetic",
    "task2a": "synthetic"
  }
}
```

No path disclosure.

---

# 48. Private-local model registry

Implement a registry abstraction.

Recommended states:

```text
not_loaded

loaded

synthetic

error
```

Entries:

```text
task1_service

task1_late

task2a_total

task2a_chilled_or_pipeline
```

Use actual Phase 17 artifact structure.

Do not invent a separate chilled model if the frozen implementation uses another architecture.

---

# 49. No import-time model loading

Importing:

```text
app.integration_api
```

in synthetic mode must not trigger loading of frozen ML artifacts.

This supports:

- privacy;
- fast tests;
- clean frontend mocks;
- absence of competition data.

Add a regression test.

---

# 50. Model load idempotence

Repeated `POST /v1/models/load` should be safe.

Expected:

```text
first:
loaded

later:
already_loaded
```

or equivalent.

Do not:

- retrain;
- reload unnecessarily;
- modify artifacts.

---

# 51. DT-370 — Implement delivery-risk endpoint

Recommended:

```text
POST /v1/delivery-risk
```

Synthetic mode:

```text
validate synthetic request
→ deterministic synthetic result
```

Private-local mode:

```text
validate frozen prediction-time input
→ run frozen service model
→ run frozen late model/calibration
→ return integration response
```

No retraining.

---

# 52. Delivery-risk prohibited fields

The integration request must reject training-only fields:

```text
actual_depart_time

actual_travel_duration_min

arrival_time

leave_outlet_time
```

Also reject direct target/label fields.

This protects the Task 1 inference contract even in a demo API.

---

# 53. Delivery-risk output

Return:

```text
pred_service_min

pred_late_prob
```

with exact frozen semantics.

Do not return:

```text
raw model margins

calibration internals

SHAP row values

historical target features

private model paths
```

unless a later explicitly authorized debugging endpoint is created.

---

# 54. Delivery-risk synthetic determinism

Same synthetic input + same contract version must yield the same output.

Do not use unseeded randomness.

This lets the Hackathon team develop stable UI tests.

---

# 55. DT-371 — Implement demand-forecast endpoint

Recommended:

```text
POST /v1/demand-forecast
```

Public/synthetic mode:

respond only from synthetic fixtures/generator.

Do not query:

```text
outputs/submission_task2a.csv
```

to answer public requests.

---

# 56. Demand forecast output

Return:

```text
depot

brand

iso_year

iso_week

forecast_horizon

pred_total_volume_m3

pred_chilled_volume_m3
```

No official `row_id` in public demo.

Style/Tech chilled:

```text
0
```

---

# 57. Private-local forecast mode

Only if safe and already supported by frozen Phase 17 inference.

It may calculate/serve a team-authorized forecast locally.

Do not:

- accept uploaded competition history;
- expose the official test forecast table;
- return all future test rows as a batch;
- change the frozen forecast model.

---

# 58. DT-372 — Implement allocation endpoint

Recommended:

```text
POST /v1/allocation-insight
```

or a similarly named route.

Its public contract returns:

```text
synthetic aggregate insight
```

not the official row-level allocation.

---

# 59. Allocation endpoint response

Allowed public fields:

```text
scenario_ref

aggregate served/deferred counts

vehicles_used

trips_used

hard-rule limits

WayLoom policy name

optional sanitized deferral example refs
```

Not allowed:

```text
real order_ref

real vehicle_id

real outlet_id

real trip_id mapping

private solver objective details tied to actual rows
```

---

# 60. Allocation endpoint request

Recommended:

```json
{
  "scenario_ref": "DEMO_SCENARIO_01"
}
```

Do not accept:

```text
allocation CSV

orders CSV

fleet CSV

filesystem path

SQL query

arbitrary order_ref list
```

---

# 61. DT-373 — Privacy gate

DT-373 is the critical P0 task.

Even though the phase is optional, once it exists it must fail closed.

The system must prevent accidental public disclosure of official private test records.

---

# 62. Protected filesystem roots

At minimum define:

```text
data/raw

data/interim

reports/private
```

as protected.

Also protect final official submissions from public API reading:

```text
outputs/submission_task1.csv

outputs/submission_task2a.csv

outputs/submission_task2b.csv
```

The files may exist locally, but the public/synthetic API cannot read or serve them.

---

# 63. Central privacy module

Create:

```text
src/integration/privacy.py
```

Responsibilities:

```text
protected path detection

path normalization

symlink/traversal safety

safe error redaction

public field allowlists

synthetic identifier validation

contract export allowlist
```

Do not scatter privacy logic across routes.

---

# 64. Path traversal protection

Reject paths equivalent to protected paths after normalization.

Examples:

```text
data/raw/file.csv

data/../data/raw/file.csv

absolute path to reports/private

symlink into private directory
```

Better:

public API should accept no filesystem paths at all.

Still test path guards used by export/internal helpers.

---

# 65. Response allowlists

Use explicit Pydantic response models.

Do not:

```python
return internal_model.__dict__
```

or:

```python
return dataframe.to_dict(...)
```

because future internal fields may leak automatically.

Each route must map internal objects to an allowlisted public response.

---

# 66. Synthetic/offical ID collision audit

A local privacy validator may privately read official identifier sets and compute only:

```text
overlap_count
```

against synthetic fixtures.

Require:

```text
overlap_count == 0
```

Do not print overlapping IDs.

Do not store them in tracked reports.

---

# 67. OpenAPI privacy audit

Generate:

```text
openapi.json
```

from synthetic mode.

Scan:

```text
examples

defaults

descriptions

enum values
```

for:

```text
real official IDs

absolute paths

data/raw

data/interim

reports/private

submission_task*.csv paths

model artifact paths
```

Require zero private leakage.

---

# 68. No public private-record lookup endpoint

Do not implement routes like:

```text
GET /delivery/{real_delivery_id}

GET /forecast/{real_row_id}

GET /allocation/{real_order_ref}

GET /vehicle/{real_vehicle_id}
```

against official data.

Synthetic route IDs are okay.

---

# 69. No batch export endpoint

Do not implement:

```text
/download-submission

/export-all-predictions

/all-orders

/all-allocations
```

The shareable integration layer is a contract/demo, not a data publication service.

---

# 70. No raw data upload endpoint

Do not implement:

```text
/upload-dataset

/upload-orders

/upload-route-legs
```

Phase 28 does not need it and it increases exposure risk.

---

# 71. No arbitrary model URL

Do not implement model loading from:

```text
HTTP URL

S3 URL

HuggingFace path

arbitrary filesystem path
```

This is outside scope and may violate competition/model restrictions.

---

# 72. Synthetic service must run without private files

Create a test environment where protected competition paths are absent or monkeypatched unavailable.

Import and run:

```text
health

contract

model load synthetic

delivery risk synthetic

demand forecast synthetic

allocation insight synthetic
```

All should pass.

This is one of the strongest DT-373 proofs.

---

# 73. Shareable contract must be data-independent

Running:

```text
python scripts/export_integration_contract.py
```

in synthetic mode must not require:

```text
--raw-root

private report path

official submission path

model path
```

It should package tracked schema/docs/examples only.

---

# 74. Integration contract README

`WAYLOOM_INTEGRATION_CONTRACT.md` should explain:

```text
scope

official vs integration schema

contract version

endpoints

request/response models

synthetic examples

error model

Phase26 optional behavior

Phase27 optional behavior

privacy boundary

Datathon integration not required
```

No private examples.

---

# 75. Privacy documentation

Create:

```text
docs/integration/PRIVACY_AND_DATA_BOUNDARY.md
```

State clearly:

```text
synthetic_demo is the default

official private competition records are never published

official submissions are not API data sources

private_local is local/team-authorized only

no production internet deployment of private mode under this contract
```

---

# 76. FastAPI service documentation

Create:

```text
docs/integration/FASTAPI_SERVICE.md
```

Include:

```text
installation of optional deps

synthetic startup command

route list

example curl with synthetic values

mode behavior

CORS guidance

privacy warnings

shutdown
```

Do not include real IDs.

---

# 77. Optional dependency isolation

If FastAPI is missing:

prefer:

```text
requirements-integration.txt
```

rather than changing core pinned ML dependencies.

Suggested content should be selected based on compatibility with the current environment.

Do not blindly copy latest package versions.

Run:

```text
pip check
```

after any dependency change.

---

# 78. API error model

Recommended:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request does not match the integration contract.",
    "request_id": "..."
  }
}
```

Never return:

```text
C:\Users\...
/home/user/...
Traceback...
private CSV path
```

---

# 79. Health endpoint tests

`GET /health`:

- 200;
- `status=ok`;
- contract version;
- `mode=synthetic_demo`;
- no model/file paths;
- no private row counts.

---

# 80. Contract endpoint tests

`GET /v1/contract` should return:

```text
contract version

schema versions

available route names

current mode

privacy statement
```

No filesystem layout.

---

# 81. Model endpoint tests

`POST /v1/models/load`:

Synthetic mode:

```text
real_models_loaded=false
```

No real artifact required.

Attempt to send a path:

```text
model_path
```

should fail schema validation.

---

# 82. Delivery endpoint tests

Valid synthetic input:

```text
200
```

Invalid late probability cannot occur in response.

Forbidden field such as:

```text
arrival_time
```

in request:

reject.

Unknown extra field policy should be explicit and tested.

Recommended:

```text
extra = forbid
```

for request models.

---

# 83. Forecast endpoint tests

Validate:

```text
Fresh:
0 <= chilled <= total

Style:
chilled = 0

Tech:
chilled = 0
```

No official row ID.

No private-source indicator.

---

# 84. Allocation endpoint tests

Validate:

```text
served + deferred = total

max trips = 2

Fresh limit = 270

Style+Tech limit = 480
```

No row-level fields.

No real IDs.

---

# 85. Deferral demo tests

Synthetic explanation examples must be structurally consistent.

Example hard:

```text
reason_class = UNAVOIDABLE_HARD
```

Example policy:

```text
reason_class = POLICY_TRADEOFF
```

Include noncausal limitation.

Do not claim they come from the real allocation.

---

# 86. Contract export tests

`dist/integration_contract/` must contain only allowlisted files.

Reject:

```text
symlink escaping package

hidden private file

submission CSV

model file

private report

raw data
```

Manifest hashes must match.

---

# 87. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-28-integration-contract
```

Recommended commits:

```text
feat(integration): add versioned WayLoom JSON schemas
test(integration): validate synthetic fixtures and privacy boundary
feat(integration): add optional synthetic FastAPI service
feat(integration): add safe model registry and endpoints
docs(integration): publish synthetic Hackathon integration contract
```

Before commit:

```bash
git status
git diff
git diff --check
```

Then:

```bash
pytest -q
python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

---

# 88. Local contract export command

Recommended:

```bash
python scripts/export_integration_contract.py   --config configs/integration.yaml   --output-dir dist/integration_contract
```

This command should not need private competition data.

---

# 89. Local validation command

Recommended:

```bash
python scripts/validate_integration_contract.py   --config configs/integration.yaml   --contract-dir dist/integration_contract
```

Optional local-only identifier collision audit may additionally accept:

```text
--raw-root data/raw
--manifest configs/dataset_manifest.yaml
```

but must emit counts only.

---

# 90. Local synthetic FastAPI command

Recommended:

```bash
python -m uvicorn app.integration_api:app   --host 127.0.0.1   --port 8088
```

Use the actual module path implemented in the repository.

Default config must be:

```text
synthetic_demo
```

---

# 91. Recommended sanitized validation output

Target:

```text
WAYLOOM — PHASE 28 INTEGRATION CONTRACT

CONTRACT VERSION                         : 1.0.0

TASK1 JSON SCHEMA                       : PASS
DEMAND FORECAST JSON SCHEMA             : PASS
ALLOCATION INSIGHT JSON SCHEMA          : PASS
DEFERRAL EXPLANATION JSON SCHEMA        : PASS

SYNTHETIC EXAMPLES                      : PASS
SYNTHETIC/OFFICIAL ID OVERLAP           : 0

SHAREABLE CONTRACT EXPORT               : PASS
EXPORT PRIVATE FILE COUNT               : 0

FASTAPI SYNTHETIC START                 : PASS
SYNTHETIC MODE NEEDS COMPETITION DATA   : NO

MODEL LOAD ENDPOINT                     : PASS
DELIVERY-RISK ENDPOINT                  : PASS
DEMAND-FORECAST ENDPOINT                : PASS
ALLOCATION ENDPOINT                     : PASS

PUBLIC REAL TEST RECORDS                : 0
OPENAPI PRIVATE LEAKAGE                 : NO
PROTECTED PATH ACCESS                   : BLOCKED

TASK1 OFFICIAL CSV HASH                 : UNCHANGED
TASK2A OFFICIAL CSV HASH                : UNCHANGED
TASK2B OFFICIAL CSV HASH                : UNCHANGED

PHASE 28                                : PASS
READY FOR PHASE 29                      : YES
```

---

# 92. STOP conditions

`READY FOR PHASE 29` remains **NO** if:

- official submission needs modification for integration;
- Task1/Task2A/Task2B final hashes change;
- schema copies private official IDs;
- synthetic fixture copies a real row;
- synthetic service requires competition data;
- public service reads `data/raw/**`;
- public service reads `data/interim/**`;
- public service reads `reports/private/**`;
- public service reads official submission CSVs;
- arbitrary filesystem path is accepted;
- raw object/DataFrame serialization can leak internal columns;
- OpenAPI contains private IDs/paths;
- shareable package contains model/data/private report;
- FastAPI dependency changes break frozen environment;
- real/private mode is default;
- real/private mode is publicly bound by default;
- delivery request accepts training-only actual fields;
- demand endpoint exposes official private forecast rows;
- allocation endpoint exposes real row-level assignments;
- deferral endpoint exposes real private order IDs;
- external proprietary API is required;
- Hackathon integration is made a Datathon submission dependency;
- DT-373 privacy gate fails;
- tests fail;
- `pip check` fails;
- independent review fails;
- Phase 29 work is introduced early.

---

# 93. Definition of Done

Phase 28 is complete only when:

- [ ] DT-362 PASS
- [ ] DT-363 PASS
- [ ] DT-364 PASS
- [ ] DT-365 PASS
- [ ] DT-366 PASS
- [ ] DT-367 PASS
- [ ] DT-368 PASS
- [ ] DT-369 PASS
- [ ] DT-370 PASS
- [ ] DT-371 PASS
- [ ] DT-372 PASS
- [ ] DT-373 PASS
- [ ] official optional-integration statement documented
- [ ] contract version defined
- [ ] Task1 schema validates exact prediction semantics
- [ ] Task1 request rejects training-only actual fields
- [ ] demand schema enforces nonnegative total/chilled
- [ ] Style/Tech chilled = 0
- [ ] allocation insight schema exposes no row-level private assignment
- [ ] deferral explanation schema handles Phase26 absent/present honestly
- [ ] all synthetic fixtures validate
- [ ] synthetic fixtures contain no real IDs
- [ ] synthetic fixture generator needs no competition data
- [ ] shareable Hackathon contract exported
- [ ] share package allowlist passes
- [ ] share package contains zero private files
- [ ] FastAPI synthetic mode starts
- [ ] synthetic mode loads no real models/data
- [ ] model-load endpoint accepts no path
- [ ] delivery-risk endpoint deterministic/safe
- [ ] demand-forecast endpoint deterministic/safe
- [ ] allocation endpoint aggregate/synthetic only
- [ ] public serializers use allowlists
- [ ] protected-path guard passes
- [ ] no public official record lookup route
- [ ] no public batch export route
- [ ] no raw data upload route
- [ ] logs do not include bodies/private IDs
- [ ] API errors redact paths
- [ ] OpenAPI privacy audit passes
- [ ] synthetic/offical identifier overlap count = 0 in optional local audit
- [ ] Task1 official CSV hash unchanged
- [ ] Task2A official CSV hash unchanged
- [ ] Task2B official CSV hash unchanged
- [ ] frozen model/config hashes unchanged
- [ ] targeted integration tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private paths remain ignored
- [ ] independent Phase28 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 28 STATUS: PASS
OPTIONAL INTEGRATION CONTRACT: COMPLETE
PUBLIC REAL TEST RECORDS: 0
FROZEN DATATHON ARTIFACTS: UNCHANGED
READY FOR PHASE 29: YES
```

---

# 94. Phase skip rule

Phase 28 is optional.

If the FastAPI/service portion cannot be completed safely before the competition deadline:

do not weaken privacy.

Choose:

```text
PHASE 28: OPTIONAL SKIPPED / INCOMPLETE
```

and continue required Datathon phases.

Do not report Phase 28 PASS unless all DT-362–DT-373 are satisfied.

---

# 95. Recommended model

Phase 28 combines:

- schema design;
- API contracts;
- cross-phase semantics;
- private-data boundaries;
- optional model loading;
- FastAPI behavior;
- security/privacy fail-closed design.

Recommended implementation:

```text
GPT-5.6 Sol
Reasoning: High
```

Recommended independent review:

```text
GPT-5.6 Sol
Reasoning: High
```

---

# 96. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 28 only.

PHASE:
Optional WayLoom Integration Contract

TASK RANGE:
DT-362 through DT-373

EXECUTION MODE:
HYBRID / OPTIONAL INTEGRATION.
SCHEMA-FIRST.
SYNTHETIC-DEMO-FIRST.
PRIVACY-FAIL-CLOSED.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 29.

==================================================
MISSION
==================================================

Create a safe integration contract that lets the WayLoom Hackathon/UI team
understand and prototype against Datathon outputs WITHOUT exposing restricted
competition records.

Required tasks:

DT-362 Define Task 1 JSON schema
DT-363 Define demand forecast JSON schema
DT-364 Define allocation insight JSON schema
DT-365 Define deferral explanation schema
DT-366 Create synthetic demo responses
DT-367 Share integration contract with Hackathon team
DT-368 Build optional FastAPI service
DT-369 Implement model loading endpoint
DT-370 Implement delivery-risk endpoint
DT-371 Implement demand-forecast endpoint
DT-372 Implement allocation endpoint
DT-373 Prevent official private test records from becoming public

This phase is OPTIONAL and MUST NOT block the Datathon submission.

The official Challenge Booklet states that the Datathon is judged separately
from the Hackathon and teams are NOT required to integrate the Datathon
solution into the Hackathon build.

Therefore:

schema/synthetic contract quality is more important than forcing live private
competition data into a public service.

==================================================
SOURCE AUTHORITY
==================================================

Use this hierarchy:

1. Official Challenge Booklet
2. Official templates/checker/data contracts
3. WAYLOOM_DATATHON_MASTER_PLAN.md
4. Frozen Phase 10 / Phase 17 / Phase 24 contracts and outputs
5. Optional Phase 25–27 artifacts where present
6. Engineering choices in this Phase 28 contract

Official source facts to preserve:

Task1 official output:
delivery_id
pred_service_min
pred_late_prob

Task2A official output:
row_id
pred_total_volume_m3
pred_chilled_volume_m3

Task2B official output:
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

Datathon-Hackathon integration:
NOT REQUIRED.

Competition data:
competition-only use;
must not be shared/distributed to third parties;
datasets/derivatives must not be made public unless explicitly authorized.

Proprietary API-based modelling/preprocessing:
prohibited.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 28
4. PHASE_10_COMPETITION_CONTRACT.md
5. PHASE_17_COMPETITION_CONTRACT.md
6. PHASE_21_COMPETITION_CONTRACT.md
7. PHASE_22_COMPETITION_CONTRACT.md
8. PHASE_23_COMPETITION_CONTRACT.md
9. PHASE_24_COMPETITION_CONTRACT.md
10. PHASE_26_COMPETITION_CONTRACT.md if present/implemented
11. PHASE_27_COMPETITION_CONTRACT.md if present/implemented
12. PHASE_28_COMPETITION_CONTRACT.md

Inspect tracked frozen interfaces:

13. Task1 final inference input/output adapter
14. Task1 final model loading code
15. Task2A final forecast output adapter
16. Task2B final public-safe policy/summary interfaces
17. Phase26 deferral explanation interface if implemented
18. existing config/path/security helpers
19. existing tests

Do NOT inspect private real rows.

==================================================
PRECONDITIONS
==================================================

Require:

Phase 10 Task1 final artifacts:
FROZEN

Phase 17 Task2A final artifacts:
FROZEN

Phase 24 Task2B final output/policy:
FINAL

Task1/Task2A/Task2B official schemas:
known

If Phase26 is absent:
deferral explanation schema still MUST be defined,
but live/synthetic response may mark detailed counterfactual explanation as
unavailable or demo-only.

If Phase27 is absent:
do NOT invent uncertainty fields into the core integration schemas.

==================================================
PHASE 28 SAFETY PRINCIPLE
==================================================

This phase must be safe even if someone starts the optional service with the
default configuration.

DEFAULT MODE:

synthetic_demo

In synthetic_demo mode:

- no competition dataset is loaded
- no official submission file is loaded
- no private reports are loaded
- no real model artifact is required
- responses come only from tracked synthetic fixtures / deterministic mocks
- all IDs are obviously synthetic

A real-model/private-local mode MAY be implemented only if:

- explicitly enabled
- restricted to local/team-authorized use
- never serves official private test records
- never exposes private paths, hashes, row IDs or raw diagnostics
- cannot be confused with the public synthetic-demo mode

Do NOT make real/private mode the default.

==================================================
FROZEN ARTIFACTS — DO NOT MODIFY
==================================================

Do NOT modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
Task2A final model/runtime artifacts
outputs/submission_task2a.csv

data/interim/task2b_final_allocation.csv
outputs/submission_task2b.csv
docs/task2b_policy.md
Phase22/23 private evidence

Do NOT regenerate official submissions.

==================================================
PRIVATE DATA BOUNDARY
==================================================

The API/integration layer must NEVER expose row-level official private test
records publicly.

Do not embed real records into:

OpenAPI examples
JSON schemas
README snippets
unit-test fixtures
frontend mocks
Postman collections
Swagger examples
Git-tracked demo JSON
screenshots
logs
error responses

Synthetic demo IDs must be obviously synthetic, for example:

DEMO_DELIVERY_001
DEMO_FORECAST_001
DEMO_ORDER_001
DEMO_SCENARIO_01

Do not mimic a real identifier copied from competition data.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/integration/__init__.py
src/integration/models.py
src/integration/schemas.py
src/integration/privacy.py
src/integration/synthetic_data.py
src/integration/adapters.py
src/integration/model_registry.py
src/integration/service.py

scripts/export_integration_contract.py
scripts/validate_integration_contract.py

configs/integration.yaml

docs/integration/WAYLOOM_INTEGRATION_CONTRACT.md
docs/integration/PRIVACY_AND_DATA_BOUNDARY.md
docs/integration/FASTAPI_SERVICE.md

schemas/integration/task1.schema.json
schemas/integration/demand_forecast.schema.json
schemas/integration/allocation_insight.schema.json
schemas/integration/deferral_explanation.schema.json

examples/integration/task1_response.synthetic.json
examples/integration/demand_forecast_response.synthetic.json
examples/integration/allocation_response.synthetic.json
examples/integration/deferral_explanation.synthetic.json

tests/test_integration_schemas.py
tests/test_integration_synthetic_examples.py
tests/test_integration_privacy.py
tests/test_integration_model_registry.py
tests/test_integration_api.py
tests/test_integration_contract_export.py

Optional FastAPI module:

app/integration_api.py

or repository-consistent equivalent.

Do NOT start Phase29 architecture documentation.

==================================================
DEPENDENCIES
==================================================

FastAPI is optional.

If FastAPI / Pydantic are not already installed:

do NOT broadly upgrade core ML dependencies.

Prefer a separate optional integration requirements file such as:

requirements-integration.txt

with versions compatible with the existing environment.

Do not change core model library versions simply to satisfy the optional API.

If dependency installation would destabilize the frozen ML environment:

STOP FastAPI implementation and preserve the schema/synthetic contract;
Phase 28 is optional and must not block submission.

==================================================
DT-362 — TASK 1 JSON SCHEMA
==================================================

Define an integration schema for delivery-risk output.

The response must preserve official meanings:

pred_service_min:
predicted outlet handling time in minutes

pred_late_prob:
probability of arrival after the delivery window closes

Recommended response schema:

{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo" | "private_local",
  "delivery_ref": "DEMO_DELIVERY_001",
  "prediction": {
    "pred_service_min": 18.4,
    "pred_late_prob": 0.27
  },
  "model_status": {
    "service_model": "loaded" | "synthetic",
    "late_model": "loaded" | "synthetic"
  }
}

IMPORTANT:

delivery_ref is an integration/display identifier.

Do not imply it is the official delivery_id unless in an authorized local
adapter.

Do not expose a real official delivery_id in public/synthetic mode.

Validate:

pred_service_min finite and >=0

pred_late_prob finite and in [0,1]

==================================================
TASK 1 REQUEST SCHEMA
==================================================

Do NOT invent a second model feature contract.

The delivery-risk request must be defined from the frozen Task1 inference
adapter.

Use either:

A. a strongly typed Pydantic request matching the approved raw
prediction-time input contract

or

B. a repository-owned request envelope whose payload is validated by the
existing frozen inference-input validator

Do NOT allow forbidden actual/outcome fields such as:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

Do NOT accept arbitrary dicts without schema validation.

If the final inference adapter requires fields not safe/appropriate for public
demo:

synthetic_demo mode should return deterministic fixtures instead of invoking
the real model.

==================================================
DT-363 — DEMAND FORECAST JSON SCHEMA
==================================================

Define the integration response around official Task2A semantics.

Recommended response:

{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "forecast_ref": "DEMO_FORECAST_001",
  "depot": "Demo Depot",
  "brand": "Fresh",
  "iso_year": 2026,
  "iso_week": 42,
  "forecast_horizon": 1,
  "pred_total_volume_m3": 12.5,
  "pred_chilled_volume_m3": 7.1
}

Validation:

pred_total_volume_m3 >= 0

pred_chilled_volume_m3 >= 0

pred_chilled_volume_m3 <= pred_total_volume_m3

Style/Tech:
pred_chilled_volume_m3 == 0

If Phase27 is implemented:
uncertainty may appear in a clearly OPTIONAL nested object.

Do NOT make Phase27 uncertainty required.

Do NOT add uncertainty to official submission files.

==================================================
DEMAND FORECAST REQUEST
==================================================

Recommended request keys:

depot
brand
iso_year
iso_week

Optionally:
forecast_horizon

Validate brand domain against the official/frozen contract.

For public/synthetic mode:
resolve only against synthetic fixture data.

Do not query official Task2A test output by row_id in a public endpoint.

==================================================
DT-364 — ALLOCATION INSIGHT JSON SCHEMA
==================================================

This is an INTEGRATION summary/insight schema.

It is NOT the official Task2B submission schema.

Recommended response:

{
  "schema_version": "1.0",
  "source_mode": "synthetic_demo",
  "scenario_ref": "DEMO_SCENARIO_01",
  "summary": {
    "orders_total": 12,
    "orders_served": 10,
    "orders_deferred": 2,
    "vehicles_used": 5,
    "trips_used": 7
  },
  "constraint_summary": {
    "max_trips_per_vehicle": 2,
    "fresh_vehicle_minutes_limit": 270,
    "style_tech_vehicle_minutes_limit": 480
  },
  "reasoning": {
    "policy_name": "WayLoom lexicographic allocation policy",
    "hard_rules_precede_policy": true
  }
}

Only expose aggregates in public/synthetic mode.

Do NOT expose:

real order_ref
real vehicle_id
real outlet_id
real trip membership
real deferred-order list

==================================================
ALLOCATION INSIGHT POLICY ACCURACY
==================================================

If policy fields are included, they must match frozen Phase21 semantics:

1 maximize served orders
2 maximize previous-deferred served
3 maximize served waiting-days sum
4 maximize low-flexibility served
5 maximize Fresh chilled served
6 maximize Fresh served
7A minimize avoidable reefer-van use
7B minimize avoidable reefer use
7C minimize avoidable van use

Label this:

WayLoom engineering policy

not:

official organizer priority.

==================================================
DT-365 — DEFERRAL EXPLANATION SCHEMA
==================================================

Define a stable schema independent of whether Phase26 is implemented.

Recommended:

{
  "schema_version": "1.0",
  "example_ref": "DEFERRAL_EXAMPLE_A",
  "availability": "available" | "not_available" | "synthetic_demo",
  "reason_class":
    "UNAVOIDABLE_HARD" |
    "POLICY_TRADEOFF" |
    "ALTERNATIVE_OPTIMUM" |
    null,
  "primary_reason_code": "...",
  "secondary_reason_codes": [],
  "summary": "...",
  "evidence": {
    "counterfactual_complete": true,
    "first_degraded_policy_tier": "LEVEL_2",
    "changed_order_count": 3
  },
  "limitations": "Optimization explanation under frozen scenario/policy; not causal."
}

If Phase26 is not implemented:

availability can be:
not_available

and reason fields may be null.

Do NOT invent Phase26 findings.

==================================================
DEFERRAL REASON CODE VALIDATION
==================================================

If Phase26 exists, accepted reason codes must match its frozen taxonomy.

Do not duplicate or silently rename codes.

If Phase26 does not exist:
synthetic demo values may use the published schema vocabulary but must be
marked:

source_mode = synthetic_demo

Do not imply they describe the real frozen allocation.

==================================================
DT-366 — SYNTHETIC DEMO RESPONSES
==================================================

Create tracked synthetic JSON examples for every schema.

Requirements:

- obviously synthetic identifiers
- no copy of real competition rows
- no real output row IDs
- no real private values copied from reports
- valid against JSON schema/Pydantic models
- deterministic
- useful for frontend integration
- small and readable

At minimum create:

Task1 delivery-risk success example

Task2A Fresh forecast example

Task2A Style/Tech zero-chilled example

Task2B allocation aggregate example

hard-unavoidable deferral explanation example

policy-tradeoff deferral explanation example

Optional:
error examples.

==================================================
SYNTHETIC DATA GENERATOR
==================================================

Prefer deterministic fixtures or generator:

seed = 42

No dependency on:

data/raw
data/interim
reports/private
outputs/submission_task*.csv

Synthetic generation must run in a clean environment without competition data.

Add a test proving that.

==================================================
DT-367 — SHARE INTEGRATION CONTRACT
==================================================

Create a shareable integration package containing ONLY:

README/contract

JSON schemas

synthetic examples

OpenAPI schema from synthetic service if available

endpoint list

version/changelog

privacy rules

Do NOT include:

competition datasets

official submissions

model files

private reports

real row IDs

private hashes

real allocation examples

Recommended exported directory:

dist/integration_contract/

Recommended optional archive:

dist/WayLoom_Integration_Contract_Synthetic.zip

This package is safe for the Hackathon teammates to consume.

The Datathon does NOT depend on them integrating it.

==================================================
CONTRACT VERSIONING
==================================================

Use:

contract_version: 1.0.0

Schema versions should be stable.

Breaking field changes:
major version.

Additive optional fields:
minor version.

Documentation/fixture corrections:
patch version.

Do not expose Git commit hashes as required API fields.

==================================================
DT-368 — OPTIONAL FASTAPI SERVICE
==================================================

Build an optional lightweight FastAPI service.

Required default:

synthetic_demo mode

Recommended routes:

GET /health

GET /v1/contract

POST /v1/models/load

POST /v1/delivery-risk

POST /v1/demand-forecast

POST /v1/allocation-insight

GET /v1/demo/deferral-explanations

Optional:

GET /openapi.json
GET /docs

The service must start without competition data in synthetic_demo mode.

==================================================
FASTAPI CONFIG
==================================================

Recommended integration config:

version: 1
contract_version: 1.0.0
mode: synthetic_demo

network:
  default_host: 127.0.0.1
  default_port: 8088
  cors_allow_origins: []

privacy:
  allow_competition_records: false
  allow_private_paths: false
  redact_paths_in_errors: true
  log_request_bodies: false
  log_response_bodies: false

models:
  allow_real_model_loading: false

synthetic:
  seed: 42

Public/synthetic mode must keep:

allow_competition_records: false

==================================================
ERROR-HANDLING SAFETY
==================================================

Errors must not leak:

absolute filesystem paths

environment variables

private report paths

stack traces in API responses

real record IDs

model artifact paths

Use generic error messages.

Detailed logs, if any, stay local and must not include request/response bodies
containing private data.

==================================================
DT-369 — MODEL LOADING ENDPOINT
==================================================

Implement:

POST /v1/models/load

Purpose:

load/check PRECONFIGURED frozen model adapters.

Do NOT allow request fields such as:

model_path
config_path
pickle_path
directory

No arbitrary filesystem loading.

In synthetic_demo mode:

return status such as:

{
  "mode": "synthetic_demo",
  "task1_service": "synthetic",
  "task1_late": "synthetic",
  "task2a": "synthetic",
  "real_models_loaded": false
}

In explicitly enabled private_local mode:

load only configured/allowlisted frozen model locations.

Return only sanitized model status.

Do not return filesystem paths.

==================================================
MODEL REGISTRY
==================================================

Create a registry abstraction with states:

not_loaded
loaded
synthetic
error

Task1 service
Task1 lateness
Task2A total
Task2A chilled / final pipeline as applicable

The registry must not load models at import time in synthetic mode.

This allows schema/API tests without competition artifacts.

==================================================
PRIVATE-LOCAL MODEL MODE
==================================================

If implemented, require explicit opt-in such as:

WAYLOOM_INTEGRATION_MODE=private_local
WAYLOOM_ALLOW_REAL_MODELS=1

Default remains synthetic_demo.

Private-local mode still MUST NOT expose official private test rows.

It may accept team-created/synthetic input and run frozen models locally.

Do not implement arbitrary batch download of competition predictions.

Do not bind real/private mode publicly by default.

==================================================
DT-370 — DELIVERY-RISK ENDPOINT
==================================================

Implement:

POST /v1/delivery-risk

In synthetic_demo mode:

validate request against the integration request schema

return deterministic synthetic prediction

or use a fixed synthetic lookup.

In private_local model mode:

use the frozen Task1 inference adapter.

Return:

pred_service_min
pred_late_prob

with exact semantics.

Do NOT:

use actual training-only journey fields

retrain

recalibrate

modify post-processing

return internal feature rows

return SHAP/private diagnostics by default

==================================================
DELIVERY-RISK VALIDATION
==================================================

Require:

pred_service_min finite >=0

pred_late_prob finite [0,1]

response schema exact

unknown extra fields rejected unless explicitly allowed

forbidden actual fields rejected

error message sanitized

deterministic synthetic response

==================================================
DT-371 — DEMAND-FORECAST ENDPOINT
==================================================

Implement:

POST /v1/demand-forecast

Default synthetic mode:

serves only synthetic forecast fixture(s).

Do NOT expose the official Task2A private test table publicly.

If private-local forecast mode is implemented:

it must use approved frozen inference logic and an authorized local context.

Do not accept arbitrary user-supplied historical data uploads in this phase.

Return:

depot
brand
iso_year
iso_week
forecast_horizon
pred_total_volume_m3
pred_chilled_volume_m3

Style/Tech chilled must be 0.

Optional Phase27 uncertainty nested object:
only when Phase27 exists AND endpoint/config explicitly enables it.

==================================================
DT-372 — ALLOCATION ENDPOINT
==================================================

Implement:

POST /v1/allocation-insight

or repository-consistent equivalent.

PUBLIC/SYNTHETIC MODE:

return synthetic aggregate allocation insight only.

Do NOT return:

real order assignments

real vehicle assignments

real trip membership

real deferred order IDs

PRIVATE LOCAL MODE:

prefer aggregates and sanitized explanation summaries.

Do not expose official private row-level allocation through HTTP in Phase28.

If row-level behavior is needed for internal analysis:
keep it outside the public API.

==================================================
ALLOCATION ENDPOINT INPUT
==================================================

Recommended public request:

{
  "scenario_ref": "DEMO_SCENARIO_01"
}

Do NOT accept:

filesystem path

raw allocation CSV

raw order table upload

official order_ref list

arbitrary SQL/query string

==================================================
DT-373 — PREVENT PRIVATE TEST RECORDS FROM BECOMING PUBLIC
==================================================

This is P0 and the most important Phase28 requirement.

Implement fail-closed privacy boundaries.

At minimum:

1. default synthetic mode uses no competition data;

2. no public endpoint directly reads:
   data/raw/**
   data/interim/**
   reports/private/**
   outputs/submission_task*.csv

3. synthetic examples are generated without those paths;

4. API response serializers contain allowlisted fields only;

5. no route returns raw DataFrame rows;

6. no arbitrary file-path request parameters;

7. no endpoint exposes official IDs in synthetic/public mode;

8. logs do not contain request/response bodies by default;

9. exception responses redact local paths;

10. integration export package excludes private/frozen artifacts;

11. contract validation can locally compare synthetic IDs against official ID
    sets and require zero overlap WITHOUT printing those IDs;

12. public/synthetic service can be tested in an environment where competition
    data directories are absent.

==================================================
PRIVACY PATH GUARD
==================================================

Create a central guard that recognizes prohibited roots:

data/raw
data/interim
reports/private

and protected official outputs:

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

Synthetic/public code paths must never open them.

Do not rely only on developer discipline.

Test the guard.

==================================================
NO PRIVATE ROW PUBLICATION
==================================================

Even if outputs/submission_task*.csv are technically final files:

they contain official private test identifiers/results.

Do NOT publish them through the optional FastAPI service.

Phase28 integration package must demonstrate the API using synthetic values.

==================================================
SYNTHETIC-ID COLLISION AUDIT
==================================================

Human-local validation may load official identifier sets PRIVATELY and compute:

intersection_count

between official IDs and synthetic demo IDs.

Console/report:

SYNTHETIC ID OVERLAP COUNT: 0

Do not print the identifiers.

If overlap >0:

regenerate synthetic IDs.

==================================================
OPENAPI PRIVACY AUDIT
==================================================

Generate OpenAPI spec from synthetic service.

Scan:

examples
defaults
descriptions
enum values

for:

real IDs
local Windows paths
private report paths
model paths
official row dumps

Require no private source strings.

==================================================
SHAREABLE CONTRACT EXPORT
==================================================

scripts/export_integration_contract.py should produce:

dist/integration_contract/
  README.md
  contract_version.json
  schemas/
  examples/
  openapi.json
  PRIVACY_AND_DATA_BOUNDARY.md

No symlinks escaping the package.

No hidden files.

No private artifacts.

Produce a manifest listing included files and SHA256.

==================================================
CONTRACT VALIDATOR
==================================================

scripts/validate_integration_contract.py must validate:

all four schemas present

all synthetic examples validate

OpenAPI routes/schemas match contract

synthetic service starts without competition data

public mode reads no protected path

no real/private identifiers in fixtures

no private path strings in OpenAPI/examples

shareable export contains only allowlisted files

official submission hashes unchanged

frozen model/config hashes unchanged

no Phase29 files

==================================================
TESTS — SCHEMAS
==================================================

Create:

tests/test_integration_schemas.py

Test:

Task1 valid response

pred_service_min negative rejected

pred_late_prob <0 rejected

pred_late_prob >1 rejected

Demand forecast:
nonnegative
chilled <= total
Style/Tech chilled ==0

Allocation insight:
counts nonnegative
served+deferred == total when all supplied

Deferral explanation:
enum reason_class valid
availability not_available permits null reason
available requires structured reason

Unknown required version rejected

Stable schema version

==================================================
TESTS — SYNTHETIC EXAMPLES
==================================================

Create:

tests/test_integration_synthetic_examples.py

Require:

all tracked JSON examples validate

all IDs use DEMO_/DEFERRAL_EXAMPLE style

no obvious official IDs

no absolute paths

no private directory strings

deterministic generation

generation works with no data/raw directory

generation works with no outputs/submission files

==================================================
TESTS — PRIVACY
==================================================

Create:

tests/test_integration_privacy.py

Test:

synthetic mode cannot open protected paths

path traversal rejected

absolute protected path rejected

official submission path rejected

private report path rejected

API error redacts path

request/response bodies not logged

synthetic ID overlap validator returns counts only

public serializers drop unexpected internal fields

shareable export rejects protected file

shareable export rejects symlink escape

==================================================
TESTS — MODEL REGISTRY
==================================================

Create:

tests/test_integration_model_registry.py

Test:

synthetic mode loads no real model

no import-time private loading

private_local requires explicit opt-in

arbitrary model_path input impossible

configured model missing -> sanitized error

loaded status has no filesystem path

model reload idempotent

registry state deterministic

==================================================
TESTS — FASTAPI
==================================================

Create:

tests/test_integration_api.py

Using TestClient or repository-consistent local client:

GET /health -> 200

GET /v1/contract -> correct version

POST /v1/models/load -> synthetic safe status

POST /v1/delivery-risk -> valid synthetic response

forbidden actual field -> 422/400

POST /v1/demand-forecast -> valid synthetic response

Style response chilled 0

POST /v1/allocation-insight -> aggregate only

deferral demo endpoint -> anonymized

unknown fields behavior deterministic

no private paths in errors

no row-level official fields in public responses

OpenAPI generated

==================================================
TESTS — CONTRACT EXPORT
==================================================

Create:

tests/test_integration_contract_export.py

Require:

allowlisted files only

schema files present

examples present

privacy doc present

OpenAPI present if FastAPI built

manifest hashes correct

no raw/interim/private path

no official submissions

no model artifacts

no hidden private file

deterministic file ordering

zip/export reproducible where practical

==================================================
PUBLIC RESPONSE ALLOWLIST
==================================================

Use explicit response models.

Do NOT return dict(model.__dict__) or DataFrame.to_dict() directly.

Each endpoint must map internal objects to a public response allowlist.

This prevents future internal columns from leaking automatically.

==================================================
CORS / NETWORK DEFAULTS
==================================================

Default:

host = 127.0.0.1

CORS allowlist = empty

Do not set:

allow_origins=["*"]

by default.

If Hackathon frontend needs CORS:

team can explicitly configure known local origins.

Do not expose credentials.

==================================================
AUTHENTICATION
==================================================

A full auth system is out of scope for the synthetic local demo.

Because real/private mode must not be publicly deployed, do not create a false
sense of production security.

Document:

synthetic demo service only

private_local is team-local

production internet deployment of private competition-data mode is prohibited
by this Phase28 contract

==================================================
LOGGING
==================================================

Allowed logs:

route
status
latency
mode
request_id

Do not log:

request body
response body
official IDs
feature vectors
private paths
model file names if sensitive

==================================================
HEALTH ENDPOINT
==================================================

GET /health

Recommended response:

{
  "status": "ok",
  "service": "wayloom-integration",
  "contract_version": "1.0.0",
  "mode": "synthetic_demo"
}

No model paths.

No private counts.

==================================================
CONTRACT ENDPOINT
==================================================

GET /v1/contract

Return:

contract version

available endpoints

schema version mapping

mode

privacy statement

Do not return filesystem layout.

==================================================
MODEL LOAD ENDPOINT — IDEMPOTENCE
==================================================

Repeated:

POST /v1/models/load

should be safe.

Synthetic:
same status.

Private local:
already loaded -> success/already_loaded.

Do not reload/retrain models unnecessarily.

No training operation is permitted.

==================================================
DELIVERY-RISK DEMO DETERMINISM
==================================================

Given same synthetic request:

same response

under fixed contract version/seed.

Do not use unseeded random probabilities.

Frontend teams need stable mocks.

==================================================
DEMAND-FORECAST DEMO DETERMINISM
==================================================

Given same synthetic depot/brand/week:

same response.

Invalid week/brand/depot:
clear schema/domain error.

No fallback to real competition tables.

==================================================
ALLOCATION DEMO DETERMINISM
==================================================

Return fixed/generated synthetic aggregate.

Ensure:

served + deferred = total

trips >=0

vehicles_used >=0

limits exactly:
2 trips
270 Fresh
480 Style+Tech

Do not invent a different official rule.

==================================================
DEFERRAL EXPLANATION DEMO
==================================================

If synthetic hard example:

reason_class = UNAVOIDABLE_HARD

If synthetic policy example:

reason_class = POLICY_TRADEOFF

Include limitation:

optimization explanation under supplied rules/policy; not causal.

Do not say:
AI decided.

==================================================
OPTIONAL PHASE26 ADAPTER
==================================================

If Phase26 is implemented:

create an adapter from its SANITIZED demo output to the integration schema.

Do NOT read:

private deferral_reasons.csv

in public synthetic service.

Use only:

demo_examples_sanitized.json

or a similarly approved sanitized artifact.

If Phase26 is not implemented:

schema remains valid;
synthetic fixture only.

==================================================
OPTIONAL PHASE27 ADAPTER
==================================================

If Phase27 is implemented:

optional nested uncertainty object may be exposed in synthetic/private-local
integration schema.

It must be clearly:

unofficial

optional

not part of official submission

Do not require Phase27 for Phase28.

==================================================
NO DATATHON DEPENDENCY ON HACKATHON
==================================================

DT-367 means share the contract.

It does NOT mean:

wait for Hackathon implementation

change Datathon models for UI needs

make final submission depend on frontend availability

block Datathon completion on integration acceptance

Record:

integration_status = optional_shared

not:

required_dependency

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b feature/phase-28-integration-contract

Recommended commits:

feat(integration): add versioned WayLoom JSON schemas
test(integration): validate synthetic fixtures and privacy boundary
feat(integration): add optional synthetic FastAPI service
feat(integration): add safe model registry and demo endpoints
docs(integration): add Hackathon integration contract and privacy rules

Before commit:

git status
git diff
git diff --check

Run targeted integration tests.

Then:

pytest -q

python -m pip check

Never stage:

data/raw/**
data/interim/**
reports/private/**

Do not add official submission CSVs to the integration package.

==================================================
LOCAL CONTRACT EXPORT
==================================================

Expected command shape:

python scripts/export_integration_contract.py \
  --config configs/integration.yaml \
  --output-dir dist/integration_contract

No raw data arguments should be needed for synthetic export.

==================================================
LOCAL VALIDATION
==================================================

Expected:

python scripts/validate_integration_contract.py \
  --config configs/integration.yaml \
  --contract-dir dist/integration_contract

Optional PRIVATE local ID-collision audit may accept:

--raw-root data/raw
--manifest configs/dataset_manifest.yaml

but must output counts only.

Do not make raw-root required for normal contract validation.

==================================================
FASTAPI LOCAL RUN
==================================================

Synthetic mode only:

python -m uvicorn app.integration_api:app \
  --host 127.0.0.1 \
  --port 8088

or the actual repository module path.

Do not bind to 0.0.0.0 by default.

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_integration_schemas.py \
  tests/test_integration_synthetic_examples.py \
  tests/test_integration_privacy.py \
  tests/test_integration_model_registry.py \
  tests/test_integration_api.py \
  tests/test_integration_contract_export.py

Then relevant Task1/Task2A/Task2B regression tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run public/private real-data serving tests in Codex.

==================================================
STOP CONDITIONS
==================================================

STOP if:

official Datathon outputs must change for integration

Task1/Task2A/Task2B frozen artifact hash changes

integration requires publishing real competition records

integration examples contain real IDs

synthetic service reads data/raw

synthetic service reads data/interim

synthetic service reads reports/private

synthetic service reads official submission CSVs

arbitrary filesystem path accepted from API request

public response includes private/internal row fields

OpenAPI includes private paths/IDs

FastAPI dependency update destabilizes core ML environment

real/private mode becomes default

real/private mode can bind publicly by default

delivery endpoint accepts training-only actual fields

demand endpoint publishes official test rows

allocation endpoint publishes real order/vehicle/trip rows

Hackathon dependency blocks Datathon submission

external proprietary API required

Phase29 work introduced

tests fail

pip check fails

privacy review fails

==================================================
DEFINITION OF DONE
==================================================

Phase28 passes only when ALL DT-362 through DT-373 are complete.

If the optional FastAPI work cannot be implemented safely:
do not fake completion.

Because Phase28 is optional, mark the phase skipped/incomplete and continue
required Datathon work rather than weakening privacy.

Required PASS state:

DT-362 PASS
DT-363 PASS
DT-364 PASS
DT-365 PASS
DT-366 PASS
DT-367 PASS
DT-368 PASS
DT-369 PASS
DT-370 PASS
DT-371 PASS
DT-372 PASS
DT-373 PASS

Schemas versioned.

Synthetic examples valid.

Contract package shareable.

FastAPI synthetic mode starts without competition data.

Model load endpoint safe.

Delivery-risk endpoint safe.

Demand forecast endpoint safe.

Allocation endpoint aggregate/synthetic safe.

Public/private test record leakage blocked.

Official outputs unchanged.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

Task1 schema official semantics preserved

Demand forecast schema official semantics preserved

Allocation insight clearly non-official integration schema

Deferral explanation schema versioned and Phase26-optional

Synthetic fixtures contain zero real records

Hackathon package contains only allowlisted synthetic/schema/docs assets

FastAPI defaults to synthetic_demo

No import-time real model/data loading

Model endpoint accepts no path

Delivery-risk rejects actual training-only fields

Demand endpoint exposes no official test rows

Allocation endpoint exposes no real row-level assignments

Privacy path guard fail-closed

OpenAPI clean

Official submissions unchanged

Frozen model/config hashes unchanged

No Phase29 implementation

==================================================
RETURN ONLY
==================================================

PHASE:
28 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-362 READY / FAIL
DT-363 READY / FAIL
DT-364 READY / FAIL
DT-365 READY / FAIL
DT-366 READY / FAIL
DT-367 READY / FAIL
DT-368 READY / FAIL
DT-369 READY / FAIL
DT-370 READY / FAIL
DT-371 READY / FAIL
DT-372 READY / FAIL
DT-373 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

TASK1 JSON SCHEMA:
PASS / FAIL

DEMAND FORECAST JSON SCHEMA:
PASS / FAIL

ALLOCATION INSIGHT JSON SCHEMA:
PASS / FAIL

DEFERRAL EXPLANATION JSON SCHEMA:
PASS / FAIL

SYNTHETIC DEMO RESPONSES:
PASS / FAIL

SHAREABLE HACKATHON CONTRACT:
PASS / FAIL

FASTAPI SERVICE:
PASS / FAIL

MODEL LOADING ENDPOINT:
PASS / FAIL

DELIVERY-RISK ENDPOINT:
PASS / FAIL

DEMAND-FORECAST ENDPOINT:
PASS / FAIL

ALLOCATION ENDPOINT:
PASS / FAIL

DEFAULT MODE:
MUST BE synthetic_demo

SYNTHETIC MODE REQUIRES COMPETITION DATA:
MUST BE NO

PUBLIC REAL TEST RECORDS:
MUST BE 0

OPENAPI PRIVATE LEAKAGE:
MUST BE NO

OFFICIAL TASK1 CSV CHANGED:
MUST BE NO

OFFICIAL TASK2A CSV CHANGED:
MUST BE NO

OFFICIAL TASK2B CSV CHANGED:
MUST BE NO

PRIVATE REAL DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact contract-export command
2. exact contract-validation command
3. exact synthetic FastAPI run command
4. any optional local-only ID-collision audit command

PHASE 28 STATUS:
AWAITING LOCAL INTEGRATION VALIDATION

READY FOR PHASE 29:
NO

Then STOP.

Do not start Phase29.

```

---

# 97. Independent Phase 28 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 28.

PHASE:
Optional WayLoom Integration Contract

TASK RANGE:
DT-362 through DT-373

REVIEW MODE:
FRESH SESSION
READ-ONLY
PRIVACY-FIRST

Do NOT implement Phase29.
Do NOT modify files initially.
Do NOT inspect private competition rows.
Do NOT expose official test rows through the service.
Do NOT change frozen submissions/models.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase28
4. PHASE_10_COMPETITION_CONTRACT.md
5. PHASE_17_COMPETITION_CONTRACT.md
6. PHASE_21_COMPETITION_CONTRACT.md
7. PHASE_24_COMPETITION_CONTRACT.md
8. PHASE_26_COMPETITION_CONTRACT.md if present
9. PHASE_27_COMPETITION_CONTRACT.md if present
10. PHASE_28_COMPETITION_CONTRACT.md

Inspect:

11. src/integration/models.py
12. src/integration/schemas.py
13. src/integration/privacy.py
14. src/integration/synthetic_data.py
15. src/integration/adapters.py
16. src/integration/model_registry.py
17. src/integration/service.py
18. app/integration_api.py or actual API module
19. scripts/export_integration_contract.py
20. scripts/validate_integration_contract.py
21. configs/integration.yaml
22. docs/integration/WAYLOOM_INTEGRATION_CONTRACT.md
23. docs/integration/PRIVACY_AND_DATA_BOUNDARY.md
24. docs/integration/FASTAPI_SERVICE.md
25. schemas/integration/*.schema.json
26. examples/integration/*.synthetic.json
27. tests/test_integration_schemas.py
28. tests/test_integration_synthetic_examples.py
29. tests/test_integration_privacy.py
30. tests/test_integration_model_registry.py
31. tests/test_integration_api.py
32. tests/test_integration_contract_export.py

Inspect dist/integration_contract structure if generated, but do not display
private content.

HUMAN SANITIZED LOCAL RESULT:

CONTRACT EXPORT: <PASS/FAIL>
CONTRACT VALIDATION: <PASS/FAIL>

SYNTHETIC SERVICE START: <PASS/FAIL>
SYNTHETIC SERVICE REQUIRES COMPETITION DATA: <YES/NO>

TASK1 SCHEMA: <PASS/FAIL>
DEMAND FORECAST SCHEMA: <PASS/FAIL>
ALLOCATION INSIGHT SCHEMA: <PASS/FAIL>
DEFERRAL EXPLANATION SCHEMA: <PASS/FAIL>

SYNTHETIC EXAMPLES: <PASS/FAIL>

SYNTHETIC/OFFICIAL ID OVERLAP COUNT: <0 or other>

PUBLIC RESPONSE REAL RECORD COUNT: <0 or other>

OPENAPI PRIVATE LEAKAGE: <PASS/FAIL>

OFFICIAL TASK1 HASH: <UNCHANGED/FAIL>
OFFICIAL TASK2A HASH: <UNCHANGED/FAIL>
OFFICIAL TASK2B HASH: <UNCHANGED/FAIL>

Do not ask for real identifiers.

==================================================
OFFICIAL SCOPE AUDIT
==================================================

Verify the docs correctly state:

Datathon is judged separately from Hackathon.

Datathon integration into Hackathon is NOT required.

Phase28 is optional and must not block submission.

Competition datasets/derivatives are not to be publicly disclosed unless
authorized.

No claim that FastAPI is organizer-required.

==================================================
AUDIT EVERY TASK
==================================================

DT-362:
Task1 JSON schema preserves service-time and late-probability semantics.

DT-363:
Demand forecast JSON schema preserves total/chilled semantics and structural
zero chilled for Style/Tech.

DT-364:
Allocation insight schema is clearly an integration summary, not official
Task2B output schema.

DT-365:
Deferral explanation schema is stable, anonymizable and Phase26-optional.

DT-366:
Synthetic demo responses contain no private/real records and validate.

DT-367:
Shareable Hackathon contract package contains schemas/docs/synthetic examples
only.

DT-368:
Optional FastAPI service works in synthetic mode without competition data.

DT-369:
Model-loading endpoint loads only preconfigured/allowlisted models and accepts
no filesystem paths.

DT-370:
Delivery-risk endpoint uses safe schema; synthetic default; forbidden actual
fields rejected.

DT-371:
Demand forecast endpoint does not publish official Task2A test rows.

DT-372:
Allocation endpoint returns aggregate/synthetic insight, not real row-level
order assignments.

DT-373:
Fail-closed controls prevent official private test records becoming public.

==================================================
CRITICAL PRIVACY AUDIT
==================================================

Verify synthetic/public service never needs to read:

data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

Verify no public code path opens those paths.

Verify public responses use explicit allowlist response models.

Verify no direct DataFrame.to_dict()/raw object serialization can leak future
internal fields.

Verify no arbitrary path request parameters.

Verify no upload endpoint for competition datasets.

Verify default mode:
synthetic_demo.

Verify real/private mode:
explicit opt-in only.

Verify private mode is not publicly exposed by default.

==================================================
SYNTHETIC FIXTURE AUDIT
==================================================

All tracked examples must:

use obvious DEMO_/DEFERRAL_EXAMPLE IDs

contain no real identifiers

contain no local filesystem paths

contain no private hash values

contain no copied row values from private reports

validate against schemas

be deterministic

be generatable without competition directories

==================================================
TASK1 SCHEMA AUDIT
==================================================

Response:

pred_service_min finite >=0

pred_late_prob in [0,1]

Do not accept/return training-only actual outcome fields.

If request maps to frozen inference:
verify adapter uses the existing prediction-time contract.

Do not permit arbitrary feature dict that bypasses frozen input validation.

==================================================
TASK2A SCHEMA AUDIT
==================================================

pred_total_volume_m3 >=0

pred_chilled_volume_m3 >=0

chilled <= total

Style chilled =0

Tech chilled =0

Phase27 uncertainty:
optional only, if present.

No row_id from official test table in public/synthetic fixture.

==================================================
TASK2B INTEGRATION AUDIT
==================================================

Allocation insight:

aggregate only in public mode.

If policy is described:
exact frozen Phase21 order.

WayLoom policy clearly not official organizer priority.

Deferral explanations:
no real IDs.
Phase26 absence handled honestly.

No claim that organizer checker proves optimality.

==================================================
FASTAPI AUDIT
==================================================

Check:

GET /health

GET /v1/contract

POST /v1/models/load

POST /v1/delivery-risk

POST /v1/demand-forecast

POST /v1/allocation-insight

deferral demo route if implemented

OpenAPI

Default startup should succeed in a clean synthetic environment.

Error responses:
no local paths.
no stack traces.
no private IDs.

Logging:
no body logging by default.

CORS:
not wildcard by default.

Default bind:
127.0.0.1 in documented command/config.

==================================================
MODEL LOADING AUDIT
==================================================

Request cannot supply:

model_path

config_path

pickle path

directory path

In synthetic mode:
no real model import/load requirement.

Private local:
explicit opt-in.
allowlisted frozen configs only.

Response:
status only.
no filesystem path.

No training/retraining endpoint.

==================================================
CONTRACT PACKAGE AUDIT
==================================================

dist/integration_contract may contain only approved:

README/docs
schemas
synthetic examples
OpenAPI
version file
manifest

Must NOT contain:

raw data
interim data
private reports
official submissions
models
notebooks with private outputs
secrets
symlink escapes

Manifest hashes correct.

==================================================
FROZEN ARTIFACT AUDIT
==================================================

Use sanitized human evidence for official file hashes.

Task1 official submission:
unchanged.

Task2A official submission:
unchanged.

Task2B official submission:
unchanged.

Frozen model/config artifacts:
unchanged.

Phase28 must not mutate point predictions.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_integration_schemas.py \
  tests/test_integration_synthetic_examples.py \
  tests/test_integration_privacy.py \
  tests/test_integration_model_registry.py \
  tests/test_integration_api.py \
  tests/test_integration_contract_export.py

Then relevant frozen-output regression tests.

Then:

pytest -q
python -m pip check
git diff --check
git status

Do not start real public service with private data.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL OPTIONAL-SCOPE STATEMENT:
PASS / FAIL

TASK1 JSON SCHEMA:
PASS / FAIL

DEMAND FORECAST JSON SCHEMA:
PASS / FAIL

ALLOCATION INSIGHT JSON SCHEMA:
PASS / FAIL

DEFERRAL EXPLANATION JSON SCHEMA:
PASS / FAIL

SYNTHETIC DEMO RESPONSES:
PASS / FAIL

HACKATHON SHAREABLE CONTRACT:
PASS / FAIL

FASTAPI SYNTHETIC MODE:
PASS / FAIL

MODEL LOADING ENDPOINT:
PASS / FAIL

DELIVERY-RISK ENDPOINT:
PASS / FAIL

DEMAND-FORECAST ENDPOINT:
PASS / FAIL

ALLOCATION ENDPOINT:
PASS / FAIL

DEFAULT MODE:
synthetic_demo / FAIL

SYNTHETIC MODE DATA-INDEPENDENT:
PASS / FAIL

PROTECTED PATH ACCESS:
BLOCKED / FAIL

ARBITRARY FILE PATH INPUT:
BLOCKED / FAIL

REAL TEST RECORDS PUBLICLY EXPOSED:
0 / FAIL

SYNTHETIC/OFFICIAL ID OVERLAP:
0 / FAIL

OPENAPI PRIVATE LEAKAGE:
PASS / FAIL

CONTRACT PACKAGE PRIVACY:
PASS / FAIL

OFFICIAL TASK1 HASH:
UNCHANGED / FAIL

OFFICIAL TASK2A HASH:
UNCHANGED / FAIL

OFFICIAL TASK2B HASH:
UNCHANGED / FAIL

SAFE TESTS:
PASS / FAIL

PIP CHECK:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
None / exact blockers

NON-BLOCKING IMPROVEMENTS:
...

DT-362: PASS/FAIL
DT-363: PASS/FAIL
DT-364: PASS/FAIL
DT-365: PASS/FAIL
DT-366: PASS/FAIL
DT-367: PASS/FAIL
DT-368: PASS/FAIL
DT-369: PASS/FAIL
DT-370: PASS/FAIL
DT-371: PASS/FAIL
DT-372: PASS/FAIL
DT-373: PASS/FAIL

PHASE 28 INDEPENDENT REVIEW:
PASS / FAIL

OPTIONAL INTEGRATION CONTRACT:
COMPLETE / INCOMPLETE

FROZEN DATATHON ARTIFACTS:
UNCHANGED / CHANGED

READY FOR PHASE 29:
YES / NO

If PASS:

PHASE 28 INDEPENDENT REVIEW: PASS
OPTIONAL INTEGRATION CONTRACT: COMPLETE
FROZEN DATATHON ARTIFACTS: UNCHANGED
PUBLIC REAL TEST RECORDS: 0
BLOCKERS: None
READY FOR PHASE 29: YES

Then STOP.

Do not start Phase29.

```

---

# 98. Completion record

```markdown
# Phase 28 Completion Record

## Tasks

- [ ] DT-362
- [ ] DT-363
- [ ] DT-364
- [ ] DT-365
- [ ] DT-366
- [ ] DT-367
- [ ] DT-368
- [ ] DT-369
- [ ] DT-370
- [ ] DT-371
- [ ] DT-372
- [ ] DT-373

## Schemas

- [ ] Task1
- [ ] demand forecast
- [ ] allocation insight
- [ ] deferral explanation
- [ ] versioning

## Synthetic contract

- [ ] all examples validate
- [ ] zero private IDs
- [ ] data-independent generation
- [ ] shareable package exported
- [ ] package privacy manifest PASS

## API

- [ ] synthetic mode default
- [ ] health
- [ ] contract
- [ ] model load
- [ ] delivery risk
- [ ] demand forecast
- [ ] allocation insight
- [ ] deferral demo
- [ ] OpenAPI clean

## Privacy

- [ ] protected paths blocked
- [ ] arbitrary path input blocked
- [ ] no body logging
- [ ] safe errors
- [ ] no real row endpoints
- [ ] no official CSV serving
- [ ] no raw data uploads
- [ ] public real test records = 0

## Frozen artifacts

- Task1 submission changed: NO
- Task2A submission changed: NO
- Task2B submission changed: NO
- frozen model/config artifacts changed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 28 STATUS: PASS / FAIL / OPTIONAL SKIPPED
OPTIONAL INTEGRATION CONTRACT: COMPLETE / INCOMPLETE
PUBLIC REAL TEST RECORDS: 0 / FAIL
FROZEN DATATHON ARTIFACTS: UNCHANGED / CHANGED
READY FOR PHASE 29: YES / NO
```

---

# 99. Final checklist

Before Phase 29:

- [ ] exact DT-362–DT-373 coverage.
- [ ] official booklet's "integration not required" statement respected.
- [ ] JSON schemas are versioned.
- [ ] Task1 meanings preserved.
- [ ] Task2A meanings preserved.
- [ ] Task2B aggregate schema does not masquerade as official output.
- [ ] deferral explanation schema works without Phase26.
- [ ] Phase27 uncertainty remains optional.
- [ ] all tracked examples synthetic.
- [ ] zero official/private identifiers in tracked examples.
- [ ] Hackathon package contains only safe synthetic/schema/docs artifacts.
- [ ] FastAPI synthetic mode starts without competition files.
- [ ] no import-time real model loading.
- [ ] no arbitrary filesystem model loading.
- [ ] delivery endpoint rejects actual outcome fields.
- [ ] forecast endpoint does not serve official private test rows.
- [ ] allocation endpoint does not serve real row-level assignments.
- [ ] explicit public response allowlists.
- [ ] protected-path guard passes.
- [ ] error/path redaction passes.
- [ ] OpenAPI leak scan passes.
- [ ] CORS not wildcard by default.
- [ ] default bind is local-only.
- [ ] no external proprietary prediction API.
- [ ] official Task1/Task2A/Task2B hashes unchanged.
- [ ] private paths ignored/unstaged.
- [ ] safe tests pass.
- [ ] full suite passes.
- [ ] independent review passes.

Only then:

```text
PHASE 28 STATUS: PASS
OPTIONAL INTEGRATION CONTRACT: COMPLETE
PUBLIC REAL TEST RECORDS: 0
FROZEN DATATHON ARTIFACTS: UNCHANGED
READY FOR PHASE 29: YES
```
