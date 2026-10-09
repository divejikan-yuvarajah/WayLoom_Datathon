"""Phase 19 independent Task 2B order/vehicle compatibility checks only."""
from __future__ import annotations

import numpy as np
import pandas as pd

REASON_CODES = ("REFRIGERATION_MISMATCH", "VAN_ONLY_ACCESS_MISMATCH", "HOME_DEPOT_MISMATCH", "WEIGHT_EXCEEDS_CAPACITY", "VOLUME_EXCEEDS_CAPACITY")

class CompatibilityError(ValueError): pass

def build_compatibility_matrix(orders: pd.DataFrame, usable_vehicles: pd.DataFrame, *, tolerance: float = 1e-9) -> pd.DataFrame:
    """Evaluate every official rule for every pair; retain incompatible rows."""
    if orders.order_ref.duplicated().any() or orders.order_ref.isna().any(): raise CompatibilityError("order_ref must be unique.")
    if usable_vehicles.vehicle_id.duplicated().any(): raise CompatibilityError("usable vehicle_id must be unique.")
    if usable_vehicles.empty: raise CompatibilityError("At least one usable vehicle is required for compatibility diagnostics.")
    required_o={"order_ref","outlet_id","temp_requirement","parking_constraint","depot","order_weight_kg","order_volume_m3"}
    required_v={"vehicle_id","type","temp","depot","weight_cap_kg","volume_cap_m3"}
    if required_o.difference(orders) or required_v.difference(usable_vehicles): raise CompatibilityError("Compatibility input columns are incomplete.")
    if not set(orders.temp_requirement).issubset({"chilled","ambient"}) or not set(usable_vehicles.temp).issubset({"reefer","ambient"}): raise CompatibilityError("Temperature domain is invalid.")
    if not set(usable_vehicles.type).issubset({"van","truck"}): raise CompatibilityError("Vehicle type domain is invalid.")
    left=orders.copy(deep=True); right=usable_vehicles.copy(deep=True)
    left["_x"]=1; right["_x"]=1
    pairs=left.merge(right,on="_x",suffixes=("_order","_vehicle"),validate="many_to_many").drop(columns="_x")
    pairs["refrigeration_ok"]=(pairs.temp_requirement.ne("chilled") | pairs.temp.eq("reefer"))
    pairs["access_ok"]=(pairs.parking_constraint.ne("van_only") | pairs.type.eq("van"))
    pairs["home_depot_ok"]=pairs.depot_order.eq(pairs.depot_vehicle)
    pairs["weight_ok"]=pd.to_numeric(pairs.order_weight_kg).le(pd.to_numeric(pairs.weight_cap_kg)+tolerance)
    pairs["volume_ok"]=pd.to_numeric(pairs.order_volume_m3).le(pd.to_numeric(pairs.volume_cap_m3)+tolerance)
    checks=[("refrigeration_ok",REASON_CODES[0]),("access_ok",REASON_CODES[1]),("home_depot_ok",REASON_CODES[2]),("weight_ok",REASON_CODES[3]),("volume_ok",REASON_CODES[4])]
    pairs["is_compatible"]=pairs[[name for name,_ in checks]].all(axis=1)
    pairs["failure_reasons"]=["|".join(code for name,code in checks if not bool(row[name])) for _,row in pairs.iterrows()]
    pairs["weight_utilization_if_alone"]=pairs.order_weight_kg/pairs.weight_cap_kg
    pairs["volume_utilization_if_alone"]=pairs.order_volume_m3/pairs.volume_cap_m3
    pairs["max_utilization_if_alone"]=pairs[["weight_utilization_if_alone","volume_utilization_if_alone"]].max(axis=1)
    pairs=pairs.sort_values(["order_ref","vehicle_id"],kind="stable").reset_index(drop=True)
    if len(pairs)!=len(orders)*len(usable_vehicles) or pairs.duplicated(["order_ref","vehicle_id"]).any(): raise CompatibilityError("Order-vehicle cross product is invalid.")
    if not pairs.is_compatible.eq(pairs[["refrigeration_ok","access_ok","home_depot_ok","weight_ok","volume_ok"]].all(axis=1)).all(): raise CompatibilityError("Pair invariant failed.")
    return pairs

def order_compatibility_summary(matrix: pd.DataFrame, *, low_flexibility_threshold: int=2) -> pd.DataFrame:
    total=matrix.vehicle_id.nunique()
    summary=matrix.groupby("order_ref",as_index=False).agg(compatible_vehicle_count=("is_compatible","sum"))
    summary["total_usable_vehicle_count"]=total; summary["compatible_vehicle_share"]=summary.compatible_vehicle_count/total if total else 0.0
    summary["individually_impossible"]=summary.compatible_vehicle_count.eq(0)
    summary["flexibility_category"]=np.select([summary.compatible_vehicle_count.eq(0),summary.compatible_vehicle_count.eq(1),summary.compatible_vehicle_count.le(low_flexibility_threshold)], ["IMPOSSIBLE","SINGLETON","LOW_FLEXIBILITY"], default="FLEXIBLE")
    return summary

def vehicle_scarcity_summary(matrix: pd.DataFrame) -> pd.DataFrame:
    base=matrix[["vehicle_id"]].drop_duplicates().sort_values("vehicle_id").reset_index(drop=True)
    compatible=matrix.loc[matrix.is_compatible].copy()
    counts=compatible.groupby("vehicle_id",as_index=False).agg(compatible_order_count=("order_ref","size"), compatible_chilled_order_count=("temp_requirement",lambda x:int(x.eq("chilled").sum())), compatible_van_only_order_count=("parking_constraint",lambda x:int(x.eq("van_only").sum())), compatible_chilled_van_only_order_count=("order_ref",lambda x:0))
    specialized=compatible.temp_requirement.eq("chilled") & compatible.parking_constraint.eq("van_only")
    counts["compatible_chilled_van_only_order_count"]=compatible.loc[specialized].groupby("vehicle_id").size().reindex(counts.vehicle_id,fill_value=0).to_numpy()
    order_counts=order_compatibility_summary(matrix).set_index("order_ref").compatible_vehicle_count
    exclusive=compatible.loc[compatible.order_ref.map(order_counts).eq(1)].groupby("vehicle_id").agg(exclusive_order_count=("order_ref","size"), exclusive_chilled_order_count=("temp_requirement",lambda x:int(x.eq("chilled").sum())))
    result=base.merge(counts,on="vehicle_id",how="left").merge(exclusive,on="vehicle_id",how="left").fillna(0)
    exclusive_specialized=compatible.loc[compatible.order_ref.map(order_counts).eq(1) & compatible.temp_requirement.eq("chilled") & compatible.parking_constraint.eq("van_only")].groupby("vehicle_id").size()
    result["exclusive_chilled_van_only_order_count"]=result.vehicle_id.map(exclusive_specialized).fillna(0).astype(int)
    return result
