# WayLoom Integration Contract 1.0.0

This optional contract gives the Hackathon team a stable, synthetic interface to the completed Datathon work. Datathon judging and submission do not depend on this integration.

The package contains versioned JSON schemas, deterministic synthetic examples, an OpenAPI document, and privacy guidance. Integration JSON is an engineering presentation layer; it does not replace any official CSV contract.

JSON Schema validates structure and schema-expressible conditions. WayLoom semantic validation additionally enforces relational invariants such as chilled volume not exceeding total volume and served plus deferred orders equalling total orders.

## Endpoints

- `GET /health` reports service mode and contract version.
- `GET /v1/contract` lists the supported contract surface.
- `POST /v1/models/load` initializes synthetic model states. It accepts no path.
- `POST /v1/delivery-risk` returns predicted outlet handling minutes and probability of arrival after the delivery-window close.
- `POST /v1/demand-forecast` returns total and chilled weekly volume forecasts.
- `POST /v1/allocation-insight` returns only a synthetic aggregate allocation summary.
- `GET /v1/demo/deferral-explanations` returns anonymized synthetic explanations.

All request models reject unknown fields. Errors have a safe code, message, and request identifier without local details.

## Semantics

Task 1 fields retain their frozen meanings: `pred_service_min` is predicted outlet handling time in minutes and `pred_late_prob` is the probability of arrival after delivery-window close.

Task 2A forecasts are nonnegative, chilled volume never exceeds total volume, and Style/Tech chilled volume is zero. Optional uncertainty, if later enabled, is explicitly unofficial and is never part of the official output.

Task 2B responses are synthetic aggregates, not official row-level allocations. Hard rules precede the WayLoom engineering policy. The policy maximizes served orders, prior deferrals, waiting-days sum, low-flexibility service, Fresh chilled service, and Fresh service, then minimizes avoidable reefer-van, reefer, and van use.

Deferral explanations use the stable Phase 26 vocabulary when available. Synthetic fixtures remain available when Phase 26 is absent. Explanations describe optimization under supplied rules and policy; they are not causal claims.

## Versioning

The contract uses semantic versioning. Major versions break fields or endpoints, minor versions add optional fields or endpoints, and patches correct documentation or fixtures. Schema version `1.0` is stable within contract version `1.0.0`.

Default mode is `synthetic_demo`. It is data-independent and uses only obvious demo identifiers and fixed/generated values. `private_local` requires explicit team authorization and a separate security decision; it is not a public deployment mode.
