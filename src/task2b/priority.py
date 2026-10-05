"""Phase 21 deterministic policy metadata and lexicographic objective support."""
from __future__ import annotations
import pandas as pd
class PriorityError(ValueError): pass
HARD_FEASIBILITY_FIELD="hard_feasible"
OBJECTIVE_LEVELS=("served_order_count","served_previous_deferred_count","served_waiting_days_sum","served_low_flexibility_count","served_fresh_chilled_count","served_fresh_count","avoidable_reefer_van_assignment_count","avoidable_reefer_assignment_count","avoidable_van_assignment_count")
HARD_SOFT_RULES={"same_brand_and_district_per_trip":"HARD_OFFICIAL","chilled_requires_reefer":"HARD_OFFICIAL","van_only_requires_van":"HARD_OFFICIAL","home_depot_match":"HARD_OFFICIAL","whole_order":"HARD_OFFICIAL","weight_and_volume_capacity":"HARD_OFFICIAL","trip_and_time_budgets":"HARD_OFFICIAL","deferred_yesterday":"SOFT_POLICY","days_since_last_served":"SOFT_POLICY","low_compatible_vehicle_count":"SOFT_POLICY","fresh_chilled":"SOFT_POLICY","fresh":"SOFT_POLICY","avoidable_specialized_vehicle_usage":"SOFT_TIEBREAKER"}
DEFERRAL_REASON_CODES=("HARD_NO_COMPATIBLE_VEHICLE","CAPACITY_COMPETITION","SCARCE_REEFER_CAPACITY","SCARCE_REEFER_VAN_CAPACITY","TRIP_SLOT_LIMIT","FRESH_TIME_BUDGET","STYLE_TECH_TIME_BUDGET","LOWER_POLICY_PRIORITY","ALTERNATIVE_FEASIBLE_ALLOCATION_CHOSEN")
def build_order_priority_metadata(orders_s1:pd.DataFrame, order_summary:pd.DataFrame, compatibility_matrix:pd.DataFrame)->pd.DataFrame:
 required={"order_ref","deferred_yesterday","days_since_last_served","brand","temp_requirement","outlet_id"}
 if required.difference(orders_s1) or "order_ref" not in order_summary: raise PriorityError("Priority inputs are incomplete.")
 if orders_s1.order_ref.duplicated().any() or not pd.to_numeric(orders_s1.deferred_yesterday).isin([0,1]).all(): raise PriorityError("Order metadata keys/signals are invalid.")
 days=pd.to_numeric(orders_s1.days_since_last_served,errors="raise")
 if (days<0).any() or not (days==days.round()).all(): raise PriorityError("days_since_last_served must be nonnegative integer-like.")
 summary_required={"order_ref","compatible_vehicle_count"}
 if summary_required.difference(order_summary.columns): raise PriorityError("Priority summary is incomplete.")
 s=order_summary[["order_ref","compatible_vehicle_count"]].copy()
 if s.order_ref.duplicated().any(): raise PriorityError("Order compatibility summary is duplicated.")
 result=orders_s1[["order_ref","outlet_id","deferred_yesterday","days_since_last_served","brand","temp_requirement"]].copy().merge(s,on="order_ref",how="left",validate="one_to_one")
 if result.compatible_vehicle_count.isna().any(): raise PriorityError("Every order needs compatibility metadata.")
 result["is_fresh"]=result.brand.eq("Fresh"); result["is_fresh_chilled"]=result.is_fresh & result.temp_requirement.eq("chilled")
 result["is_individually_impossible"]=result.compatible_vehicle_count.eq(0); result["is_singleton"]=result.compatible_vehicle_count.eq(1); result["is_low_flexibility"]=result.compatible_vehicle_count.between(1,2)
 compatible=compatibility_matrix.loc[compatibility_matrix.is_compatible].copy()
 flags=compatible.groupby("order_ref").agg(has_non_reefer_alternative=("temp",lambda x:(x!="reefer").any()),has_non_van_alternative=("type",lambda x:(x!="van").any()))
 specialized=compatible.assign(_special=compatible.temp.eq("reefer")&compatible.type.eq("van")).groupby("order_ref")
 flags["has_non_reefer_van_alternative"]=specialized._special.apply(lambda x:(~x).any())
 for c in ("has_non_reefer_alternative","has_non_van_alternative","has_non_reefer_van_alternative"): result[c]=result.order_ref.map(flags[c]).fillna(False).astype(bool)
 return result.sort_values("order_ref",kind="stable").reset_index(drop=True)
def objective_tuple(metrics:dict)->tuple: return tuple(metrics.get(k,0) if k.startswith("served_") else -metrics.get(k,0) for k in OBJECTIVE_LEVELS)
def better_objective(left:dict,right:dict)->bool:
 # Hard feasibility is a gate, never a lexicographic preference.  The
 # default keeps the pure objective helper usable for metric-only callers.
 left_feasible=bool(left.get(HARD_FEASIBILITY_FIELD,True)); right_feasible=bool(right.get(HARD_FEASIBILITY_FIELD,True))
 if left_feasible != right_feasible: return left_feasible
 if not left_feasible: return False
 return objective_tuple(left)>objective_tuple(right)
def hard_soft_classification()->dict[str,str]: return dict(HARD_SOFT_RULES)
