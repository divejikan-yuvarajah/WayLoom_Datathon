# Task 1 Label Construction Specification

This document records the tracked implementation contract. It contains no
competition rows or private results.

## Historical population

- Keep `dispatch_status` values `attempted` and `deferred`.
- Exclude `not_run` as an expected no-outcome population.
- Missing `route_id` or `seq_in_route` on a dispatched order is a blocker.

## Official join

Join:

```text
deliveries_train.(route_id, seq_in_route)
↔ route_legs_train.(route_id, seq)
```

The join is a left join with one-to-one validation and an audit indicator.
Unmatched dispatched orders and destination mismatches are blockers.

## Official labels

```text
service_start_dt = max(arrival_dt, window_open_dt)
service_minutes = (leave_outlet_dt - service_start_dt).total_seconds() / 60
late_flag = int(arrival_dt > window_close_dt)
```

Early waiting is excluded from service time. Arrival exactly at the window
close is not late.

## Time handling

Clock values are parsed strictly as `HH:MM` and combined with local,
timezone-naive dates under the Asia/Colombo convention. Midnight rollover is
resolved deterministically and checked against actual travel duration.

## Leakage boundary

The following fields are training-only or target-derived and are forbidden as
direct Task 1 prediction features:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

## Canonical implementation

The reusable implementation is:

```python
build_task1_training_labels(deliveries_train, route_legs_train)
```

The local operator CLI is:

```powershell
python scripts/build_task1_labels.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --output data/interim/task1_training_labels.csv --report-dir reports/private/phase04_task1_labels
```

The CLI is intended for local human execution only. It does not print rows or
row-level identifiers.
