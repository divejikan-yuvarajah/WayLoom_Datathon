# Task 2B Phase 18 scenario contract

Phase 18 validates and summarizes Scenario S1 only.  `order_ref` is the
canonical allocation key; duplicated `outlet_id` values are valid.

The scenario depot is Peliyagoda.  Later phases must consume only the
available, Peliyagoda-home fleet view.  Vehicles in `in_workshop` are never
usable.  Private Phase 18 diagnostics record the non-Peliyagoda S1-order
count and available fleet counts split by Peliyagoda-home status.

The following official rules are documented here but intentionally deferred:

- Phase 19: chilled orders require a reefer; `van_only` orders require a van;
  vehicle home depot must match the order depot.
- Phases 20, 22, and 23: each vehicle/trip contains one brand and district;
  orders are whole; capacity applies per trip; at most two trips per vehicle;
  Fresh has a 270-minute budget and Style/Tech a 480-minute combined budget.
- Phase 20 trip formula: `depot_to_district_freeflow_min +
  inter_stop_freeflow_min * (number_of_orders - 1) + sum(service_allowance_min)`.
  No return journey is added.
- Phase 22 allocates; Phase 23 validates.  Checker PASS proves feasibility,
  not allocation optimality.

Phase 18 performs no compatibility matrix construction, trip calculation,
priority scoring, optimization, or submission creation.  Its local reports
are aggregate-only and remain under `reports/private/phase18_task2b_scenario`.
