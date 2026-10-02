# Phase 03 Data Quality Rules

This document describes the **methods and rule classes only** for the WayLoom Datathon Phase 03 audit. It does **not** contain private competition findings, row values, counts, identifiers, or local report contents.

## Purpose

Phase 03 is an **audit-only** phase. The goal is to determine whether the official datasets are structurally trustworthy enough for Phase 04 and later modelling work.

The audit must never mutate raw official files. It may only classify findings as:

- `PASS`
- `EXPECTED`
- `WARNING`
- `BLOCKER`
- `NOT_APPLICABLE`

## Rule Families

### DT-036 Missing values

- Use rule-based conditional missingness.
- `dispatch_status = not_run` may legitimately allow blank `dispatch_date` and blank `route_id`.
- `mall_window` may be blank outside mall-constrained outlets.
- `festival` may be blank when no festival applies.
- Required identifiers such as `delivery_id`, `leg_id`, `row_id`, `outlet_id`, `vehicle_id`, `date`, `order_ref`, and `scenario` must not silently be missing.

### DT-037 Complete duplicate rows

- Detect exact duplicated rows only.
- Never call `drop_duplicates()` on official raw data in Phase 03.

### DT-038 Duplicate primary keys

- Validate official unique keys and defined composite keys.
- Candidate keys remain candidate until explicitly verified.

### DT-039 Semantic types

- Validate semantic parseability, not just Pandas inferred dtypes.
- Distinguish identifiers, categorical fields, counts, continuous numeric values, binary flags, dates, clock times, time ranges, and duration-minute fields.

### DT-040 Dates

- Validate nonblank dates using official date semantics.
- Preserve original raw values.
- Respect dispatch semantics for `attempted`, `deferred`, and `not_run`.

### DT-041 Times

- Validate `HH:MM` clock times and `HH:MM-HH:MM` mall windows.
- Do not reject midnight-crossing routes through naive clock-time ordering.

### DT-042 Official categories

- Enforce only official organizer-documented enums and reference-backed domains.
- Do not silently normalize casing or whitespace in raw data.

### DT-043 Impossible numeric values

- Enforce official nonnegative, strictly positive, bounded, and binary rules.
- Negative order sizes are `BLOCKER`.
- Zero order sizes are `WARNING` unless a stronger official rule exists.

### DT-044 Extreme values / outliers

- Use robust techniques such as IQR or MAD.
- Outliers are review candidates, not automatic errors.
- No clipping, dropping, winsorizing, or replacement is allowed in Phase 03.

### DT-045 Order identity

- `delivery_id` must be unique in `deliveries_train.csv` and `task1_test_inputs.csv`.
- Cross-file `delivery_id` overlap must be documented because Task 2A later combines both histories.
- `order_ref` is the Task 2B allocation key and must be unique within scenario `S1`.
- `outlet_id` must never be treated as the Task 2B order identity.

### DT-046 Route-leg identity

- `leg_id` must be unique in both route-leg files.
- `(route_id, seq)` must be unique within each route-leg file.
- Full Task 1 order-to-route join proof is deferred to Phase 04.

### DT-047 Outlet reference integrity

- Local audit must verify 120 unique outlets.
- All outlet references must resolve against `outlets.csv`.
- Where copied attributes exist, compare them against the official outlet reference.
- Multiple Fresh orders for the same outlet and date may be valid.

### DT-048 Vehicle reference integrity

- Local audit must verify 60 unique vehicles.
- Assigned vehicle IDs must resolve against `vehicles.csv`.
- Where copied attributes exist, compare vehicle type, temperature, and depot consistency.
- Blank vehicle assignment is expected for `not_run` rows.

### DT-049 Calendar coverage

- `calendar.csv` must cover all required Task 1 dates and Task 2A forecast weeks.
- Validate `dow`, ISO week/year, weekend flags, and binary indicators using the supplied calendar.
- Do not derive `is_operating` from weekday alone.

### DT-050 Road-condition coverage

- Road-condition mapping must use locally resolved schema information only.
- Do not invent join keys.
- Missing road coverage must not silently default to “clear”.

### DT-051 Traffic-speed coverage

- Traffic coverage must use locally resolved schema information only.
- Do not invent joins.
- Do not use actual journey outcomes as traffic features.
- Missing traffic must not silently default to free-flow.

### DT-052 Train/test compatibility

- Compare compatible categories across train/test datasets.
- Valid unseen categories are `WARNING`.
- Invalid official/reference categories are `BLOCKER`.

### DT-053 Hard schema assertions

Hard assertions enforce:

- required files;
- required columns;
- unique identifiers and route keys;
- official outlet and vehicle counts;
- official enums and binary/bounded fields;
- date/time formatting;
- outlet and vehicle reference integrity;
- required calendar coverage;
- Task 1 leakage deny-list.

Warnings stay in the audit report and do not automatically raise.

### DT-054 Private audit report

The human local run writes the full detailed report to:

`reports/private/phase03_data_quality/phase03_audit_report.md`

This tracked document must remain methods-only and must never include private audit results.
