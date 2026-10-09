"""Phase 19 aggregate scarcity diagnostics; these never make allocation decisions."""
from __future__ import annotations
import pandas as pd

def build_scarcity_report(matrix: pd.DataFrame, order_summary: pd.DataFrame, vehicle_summary: pd.DataFrame) -> dict:
    compatible=matrix.loc[matrix.is_compatible]
    orders=matrix[["order_ref","temp_requirement","parking_constraint","order_weight_kg","order_volume_m3"]].drop_duplicates("order_ref")
    chilled=order_summary.merge(orders[["order_ref","temp_requirement","parking_constraint"]],on="order_ref")
    chilled_orders=orders.loc[orders.temp_requirement.eq("chilled")]
    reefer_ids=set(matrix.loc[matrix.temp.eq("reefer"),"vehicle_id"])
    reefer_van_ids=set(matrix.loc[matrix.temp.eq("reefer") & matrix.type.eq("van"),"vehicle_id"])
    specialized=chilled.loc[chilled.temp_requirement.eq("chilled") & chilled.parking_constraint.eq("van_only")]
    reasons={code:int(matrix.failure_reasons.str.split("\\|").map(lambda x: code in x).sum()) for code in ("REFRIGERATION_MISMATCH","VAN_ONLY_ACCESS_MISMATCH","HOME_DEPOT_MISMATCH","WEIGHT_EXCEEDS_CAPACITY","VOLUME_EXCEEDS_CAPACITY")}
    return {"pair_count":int(len(matrix)),"compatible_pair_count":int(len(compatible)),"failure_reason_counts":reasons,
      "reefer_pressure":{"available_reefer_vehicle_count":len(reefer_ids),"chilled_order_count":int(len(chilled_orders)),"chilled_total_weight_kg":float(chilled_orders.order_weight_kg.sum()),"chilled_total_volume_m3":float(chilled_orders.order_volume_m3.sum()),"chilled_singleton_count":int((chilled.loc[chilled.temp_requirement.eq("chilled"),"compatible_vehicle_count"]==1).sum()),"chilled_low_flexibility_count":int((chilled.loc[chilled.temp_requirement.eq("chilled"),"compatible_vehicle_count"]<=2).sum()),"chilled_impossible_count":int((chilled.loc[chilled.temp_requirement.eq("chilled"),"compatible_vehicle_count"]==0).sum()),"compatible_chilled_orders_per_reefer":int(vehicle_summary.loc[vehicle_summary.vehicle_id.isin(reefer_ids),"compatible_chilled_order_count"].sum()),"exclusive_chilled_orders_per_reefer":int(vehicle_summary.loc[vehicle_summary.vehicle_id.isin(reefer_ids),"exclusive_chilled_order_count"].sum())},
      "reefer_van_pressure":{"available_reefer_van_count":len(reefer_van_ids),"chilled_van_only_order_count":int(len(specialized)),"chilled_van_only_total_weight_kg":float(chilled_orders.loc[chilled_orders.order_ref.isin(specialized.order_ref),"order_weight_kg"].sum()),"chilled_van_only_total_volume_m3":float(chilled_orders.loc[chilled_orders.order_ref.isin(specialized.order_ref),"order_volume_m3"].sum()),"singleton_count":int((specialized.compatible_vehicle_count==1).sum()),"impossible_count":int((specialized.compatible_vehicle_count==0).sum()),"compatible_specialized_orders_per_reefer_van":int(vehicle_summary.loc[vehicle_summary.vehicle_id.isin(reefer_van_ids),"compatible_chilled_van_only_order_count"].sum()),"exclusive_specialized_orders_per_reefer_van":int(vehicle_summary.loc[vehicle_summary.vehicle_id.isin(reefer_van_ids),"exclusive_chilled_van_only_order_count"].sum())},
      "trip_slot_pressure":{"theoretical_trip_slot_upper_bound":int(2*matrix.vehicle_id.nunique()),"unique_brand_district_groups":int(matrix[["brand","district"]].drop_duplicates().shape[0]),"impossible_orders":int(order_summary.individually_impossible.sum()),"singleton_orders":int(order_summary.compatible_vehicle_count.eq(1).sum()),"low_flexibility_orders":int(order_summary.compatible_vehicle_count.le(2).sum())},
      "vehicle_summary_row_count":int(len(vehicle_summary))}
