# Task 2B Phase 20 trip time

Candidate pools are grouped only by brand and district; they are not assigned,
served, deferred, capacity-feasible, or time-budget-feasible trips.  For a
validated candidate, time is exactly outbound once plus inter-stop reference
times times `(order_count - 1)` plus one brand+dock allowance per order. No
return leg or other time component is included. Later phases enforce the two
trip maximum and Fresh 270 / Style+Tech 480 vehicle budgets.
