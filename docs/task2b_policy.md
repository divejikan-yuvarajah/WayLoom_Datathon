# WayLoom Task 2B priority policy

This is a WayLoom engineering policy, not an organizer-mandated priority
order. Every candidate allocation must satisfy all official hard rules before
priority is considered. An infeasible plan can never be made good by a higher
priority score.

## What good means

A good allocation serves the greatest number of individually feasible orders.
When coverage ties, it serves more previously deferred orders, then more
long-waiting demand, then orders with few compatible vehicles. Fresh chilled
and Fresh are later S1 business tiebreaks. Finally, the plan avoids consuming
reefer vans, reefers, or vans when an ordinary compatible vehicle can serve the
same order without changing a higher tier.

The decision grain is `order_ref`; repeated `outlet_id` values remain separate
orders. Unique-outlet counts are reported as diagnostics only. An impossible
order remains visible and is explained rather than silently dropped.

## Fairness rationale

Maximizing broad coverage avoids concentrating service on a small set of large
or preferred orders. Previous-deferral preference reduces repeated deferral,
while waiting days prevents long service gaps from persisting. Low-flexibility
orders have fewer recovery options, so they receive a later protection tier.
This is not a promise of perfect fairness: hard-impossible orders cannot be
rescued by policy, and repeated orders at one outlet are still counted by
`order_ref`.

The later phases should report served share, previous-deferred served share,
waiting-day summaries for served versus deferred, unique outlets served,
unique previous-deferred outlets served, and low-flexibility served share.

## Business rationale

S1 is one week before a festival and records rising Fresh demand. Fresh
chilled (including dairy, meat, and produce) receives a tiebreak before Fresh
overall because it also consumes scarce refrigerated capacity. Reefer vans
are especially specialized because they satisfy chilled and van-only demand;
avoidable use is therefore minimized only after higher tiers tie.

Style and Tech remain legitimate eligible demand and are not excluded. No
payday or monsoon bonus/penalty is invented. Task 1 predictions and direct
Task 2A forecasts are not priority signals.

## Deferral explanation vocabulary

Later allocation/validation phases may use these stable reason codes:

`HARD_NO_COMPATIBLE_VEHICLE`, `CAPACITY_COMPETITION`,
`SCARCE_REEFER_CAPACITY`, `SCARCE_REEFER_VAN_CAPACITY`, `TRIP_SLOT_LIMIT`,
`FRESH_TIME_BUDGET`, `STYLE_TECH_TIME_BUDGET`, `LOWER_POLICY_PRIORITY`, and
`ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN`.
