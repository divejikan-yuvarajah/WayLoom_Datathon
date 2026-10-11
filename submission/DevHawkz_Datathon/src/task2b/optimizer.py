"""Phase 22 CP-SAT hard-constraint model; no private I/O."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from src.task2b.priority import OBJECTIVE_LEVELS
from src.task2b.solver_data import SolverData


TRIP_IDS = (1, 2)


@dataclass
class ModelBundle:
    model: cp_model.CpModel
    data: SolverData
    serve: dict
    defer: dict
    x: dict
    use_trip: dict
    use_group: dict
    trip_minutes: dict
    objectives: dict


def _group_time(data: SolverData, group: tuple[str, str]) -> tuple[int, int]:
    return (data.outbound[("Peliyagoda", group[1])], data.inter_stop[("Peliyagoda", group[1])])


def build_optimizer_model(data: SolverData) -> ModelBundle:
    model = cp_model.CpModel()
    serve = {o: model.NewBoolVar(f"serve_{i}") for i, o in enumerate(data.order_ids)}
    defer = {o: model.NewBoolVar(f"defer_{i}") for i, o in enumerate(data.order_ids)}
    x = {(o, v, t): model.NewBoolVar(f"x_{i}_{j}_{t}")
         for i, o in enumerate(data.order_ids)
         for j, v in enumerate(data.vehicle_ids)
         if (o, v) in data.compatible_pairs for t in TRIP_IDS}
    use_trip = {(v, t): model.NewBoolVar(f"use_{j}_{t}")
                for j, v in enumerate(data.vehicle_ids) for t in TRIP_IDS}
    use_group = {(v, t, g): model.NewBoolVar(f"group_{j}_{t}_{k}")
                 for j, v in enumerate(data.vehicle_ids) for t in TRIP_IDS
                 for k, g in enumerate(data.groups)}
    feasible_vehicle_groups = {(v, data.order_group[o]) for o, v in data.compatible_pairs}
    for (v, t, g), variable in use_group.items():
        if (v, g) not in feasible_vehicle_groups:
            model.Add(variable == 0)
    for o in data.order_ids:
        model.Add(serve[o] + defer[o] == 1)
        assignments = [var for (oo, _, _), var in x.items() if oo == o]
        model.Add(sum(assignments) == serve[o])
        if not assignments:
            model.Add(serve[o] == 0)
            model.Add(defer[o] == 1)
    max_minutes = max((data.outbound[("Peliyagoda", g[1])] for g in data.groups), default=0) + sum(
        data.service[o] + data.inter_stop[("Peliyagoda", data.order_group[o][1])] for o in data.order_ids)
    trip_minutes = {}
    for v in data.vehicle_ids:
        model.Add(use_trip[v, 1] + use_trip[v, 2] <= 2)
        model.Add(use_trip[v, 2] <= use_trip[v, 1])  # engineering symmetry breaker
        # Trip numbers have no independent business meaning. Sorting their
        # selected groups removes equivalent trip-1/trip-2 permutations.
        group_rank = {g: rank for rank, g in enumerate(data.groups, start=1)}
        model.Add(sum(group_rank[g] * use_group[v, 1, g] for g in data.groups) <=
                  sum(group_rank[g] * use_group[v, 2, g] for g in data.groups)
                  + len(data.groups) * (1 - use_trip[v, 2]))
        for t in TRIP_IDS:
            assignments = [(o, var) for (o, vv, tt), var in x.items() if vv == v and tt == t]
            model.Add(sum(use_group[v, t, g] for g in data.groups) == use_trip[v, t])
            model.Add(sum(var for _, var in assignments) >= use_trip[v, t])
            model.Add(sum(var for _, var in assignments) <= len(data.order_ids) * use_trip[v, t])
            for o, var in assignments:
                model.Add(var <= use_trip[v, t])
                model.Add(var <= use_group[v, t, data.order_group[o]])
            model.Add(sum(data.weight[o] * var for o, var in assignments) <= data.weight_cap[v] * use_trip[v, t])
            model.Add(sum(data.volume[o] * var for o, var in assignments) <= data.volume_cap[v] * use_trip[v, t])
            minutes = model.NewIntVar(0, max_minutes, f"minutes_{v}_{t}")
            trip_minutes[v, t] = minutes
            model.Add(minutes == sum((outbound - inter) * use_group[v, t, g]
                                     for g in data.groups for outbound, inter in [_group_time(data, g)])
                      + sum((data.service[o] + data.inter_stop[("Peliyagoda", data.order_group[o][1])]) * var
                            for o, var in assignments))
        for brand, budget in (("Fresh", 270), ("StyleTech", 480)):
            selected = (lambda g: g[0] == "Fresh") if brand == "Fresh" else (lambda g: g[0] in ("Style", "Tech"))
            terms = []
            for t in TRIP_IDS:
                terms.extend((outbound - inter) * use_group[v, t, g]
                             for g in data.groups if selected(g) for outbound, inter in [_group_time(data, g)])
                terms.extend((data.service[o] + data.inter_stop[("Peliyagoda", data.order_group[o][1])]) * var
                             for (o, vv, tt), var in x.items() if vv == v and tt == t and selected(data.order_group[o]))
            model.Add(sum(terms) <= budget * data.scales["time"])
    # Vehicles with the same capabilities and capacities are interchangeable.
    # Use lower stable IDs first; swapping their entire schedules preserves
    # every hard constraint and all nine Phase 21 objective values.
    by_signature = {}
    for v in data.vehicle_ids:
        row = data.vehicle_rows[v]
        signature = (row["type"], row["temp"], row["depot"],
                     data.weight_cap[v], data.volume_cap[v])
        by_signature.setdefault(signature, []).append(v)
    for identical in by_signature.values():
        for earlier, later in zip(identical, identical[1:]):
            model.Add(sum(use_trip[earlier, t] for t in TRIP_IDS) >=
                      sum(use_trip[later, t] for t in TRIP_IDS))
    objectives = {
        "served_order_count": sum(serve.values()),
        "served_previous_deferred_count": sum(int(data.metadata_rows[o]["deferred_yesterday"]) * serve[o] for o in data.order_ids),
        "served_waiting_days_sum": sum(int(data.metadata_rows[o]["days_since_last_served"]) * serve[o] for o in data.order_ids),
        "served_low_flexibility_count": sum(int(str(data.metadata_rows[o]["is_low_flexibility"]) == "True") * serve[o] for o in data.order_ids),
        "served_fresh_chilled_count": sum(int(str(data.metadata_rows[o]["is_fresh_chilled"]) == "True") * serve[o] for o in data.order_ids),
        "served_fresh_count": sum(int(str(data.metadata_rows[o]["is_fresh"]) == "True") * serve[o] for o in data.order_ids),
    }
    for name, vehicle_test, alternative in (
        ("avoidable_reefer_van_assignment_count", lambda v: v["temp"] == "reefer" and v["type"] == "van", "has_non_reefer_van_alternative"),
        ("avoidable_reefer_assignment_count", lambda v: v["temp"] == "reefer", "has_non_reefer_alternative"),
        ("avoidable_van_assignment_count", lambda v: v["type"] == "van", "has_non_van_alternative"),
    ):
        objectives[name] = sum(var for (o, v, _), var in x.items()
                               if vehicle_test(data.vehicle_rows[v]) and str(data.metadata_rows[o][alternative]) == "True")
    if tuple(objectives) != OBJECTIVE_LEVELS:
        raise ValueError("Model objective does not match the Phase 21 policy.")
    return ModelBundle(model, data, serve, defer, x, use_trip, use_group, trip_minutes, objectives)
