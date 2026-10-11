# Task 2A demand-history specification

Phase 11 constructs requested weekly volume history only. It uses both
`deliveries_train.csv` and `task1_test_inputs.csv`, preserves every valid
`attempted`, `deferred`, and `not_run` order, and rejects duplicate IDs rather
than deduplicating them.

Demand is assigned exclusively through `order_date -> calendar.date` and the
official `calendar.iso_year` / `calendar.iso_week` fields. Dispatch dates,
routes, vehicles, and Task 1 predictions are not used.

Weekly total demand is summed by `depot`, `brand`, `iso_year`, and `iso_week`.
Fresh chilled demand is the Fresh + chilled subset; Style and Tech chilled
targets are exactly zero. A Style/Tech chilled source record is a blocker under
the configured strict policy.

The complete panel uses a calendar week spine for each observed series. Only a
complete interior absent week becomes `CONFIRMED_ZERO`; source-boundary weeks
are `BOUNDARY_PARTIAL`, incomplete calendar weeks are blockers, and unresolved
gaps are blockers. Volume and order counts reconcile exactly before output.
