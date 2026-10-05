"""Pure Phase 21 policy metrics for synthetic/candidate allocations."""
from __future__ import annotations
import pandas as pd
from src.task2b.priority import PriorityError
def calculate_policy_metrics(allocation:pd.DataFrame, metadata:pd.DataFrame, compatibility_matrix:pd.DataFrame|None=None)->dict:
 if not {"order_ref","served"}.issubset(allocation) or allocation.order_ref.duplicated().any(): raise PriorityError("Allocation must have unique order_ref and served flag.")
 if not set(allocation.served.dropna().unique()).issubset({True,False,0,1}): raise PriorityError("served must be boolean.")
 frame=allocation.merge(metadata,on="order_ref",how="left",validate="one_to_one")
 if frame.deferred_yesterday.isna().any(): raise PriorityError("Allocation contains unknown order_ref.")
 served=frame.loc[frame.served.astype(bool)]; deferred=frame.loc[~frame.served.astype(bool)]
 result={"served_order_count":int(len(served)),"deferred_order_count":int(len(deferred)),"served_share":float(len(served)/len(frame)) if len(frame) else 0.0,"served_previous_deferred_count":int(served.deferred_yesterday.sum()),"served_previous_deferred_share":float(served.deferred_yesterday.sum()/frame.deferred_yesterday.sum()) if frame.deferred_yesterday.sum() else 0.0,"served_waiting_days_sum":int(served.days_since_last_served.sum()),"served_waiting_days_mean":float(served.days_since_last_served.mean()) if len(served) else 0.0,"served_low_flexibility_count":int(served.is_low_flexibility.sum()),"served_fresh_chilled_count":int(served.is_fresh_chilled.sum()),"served_fresh_count":int(served.is_fresh.sum()),"unique_outlets_served":int(served.outlet_id.nunique()),"unique_previous_deferred_outlets_served":int(served.loc[served.deferred_yesterday.eq(1),"outlet_id"].nunique())}
 result.update({"avoidable_reefer_van_assignment_count":0,"avoidable_reefer_assignment_count":0,"avoidable_van_assignment_count":0})
 if compatibility_matrix is not None and "vehicle_id" in allocation:
  pairs=compatibility_matrix.loc[compatibility_matrix.is_compatible].copy()
  for _,row in served.dropna(subset=["vehicle_id"]).iterrows():
   options=pairs.loc[pairs.order_ref.eq(row.order_ref)]; assigned=pairs.loc[(pairs.order_ref==row.order_ref)&(pairs.vehicle_id==row.vehicle_id)]
   if assigned.empty: raise PriorityError("Assigned vehicle is not compatible.")
   v=assigned.iloc[0]; alternatives=options.loc[options.vehicle_id.ne(row.vehicle_id)]
   if v.type=="van" and v.temp=="reefer" and not ((alternatives.type!="van")|(alternatives.temp!="reefer")).any(): result["avoidable_reefer_van_assignment_count"]+=1
   elif v.temp=="reefer" and not (alternatives.temp!="reefer").any(): result["avoidable_reefer_assignment_count"]+=1
   elif v.type=="van" and not (alternatives.type!="van").any(): result["avoidable_van_assignment_count"]+=1
 return result
