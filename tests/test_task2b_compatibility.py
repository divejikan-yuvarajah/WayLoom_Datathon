"""Synthetic Phase 19 pairwise compatibility tests."""
from __future__ import annotations
import pandas as pd
from src.task2b.compatibility import build_compatibility_matrix,order_compatibility_summary,vehicle_scarcity_summary
def _inputs():
 o=pd.DataFrame([{'order_ref':'o1','outlet_id':'x','temp_requirement':'chilled','parking_constraint':'van_only','depot':'Peliyagoda','order_weight_kg':10.,'order_volume_m3':1.,'brand':'Fresh','district':'D'}, {'order_ref':'o2','outlet_id':'x','temp_requirement':'ambient','parking_constraint':'normal','depot':'Peliyagoda','order_weight_kg':1.,'order_volume_m3':10.,'brand':'Style','district':'D'}, {'order_ref':'o3','outlet_id':'z','temp_requirement':'chilled','parking_constraint':'normal','depot':'Peliyagoda','order_weight_kg':20.,'order_volume_m3':1.,'brand':'Fresh','district':'E'}])
 v=pd.DataFrame([{'vehicle_id':'v1','type':'van','temp':'reefer','depot':'Peliyagoda','weight_cap_kg':10.,'volume_cap_m3':1.}, {'vehicle_id':'v2','type':'truck','temp':'ambient','depot':'Peliyagoda','weight_cap_kg':10.,'volume_cap_m3':20.}, {'vehicle_id':'v3','type':'van','temp':'ambient','depot':'Other','weight_cap_kg':100.,'volume_cap_m3':100.}, {'vehicle_id':'v4','type':'truck','temp':'reefer','depot':'Peliyagoda','weight_cap_kg':1.,'volume_cap_m3':1.}])
 return o,v
def test_cross_product_rules_and_reasons_are_complete():
 o,v=_inputs(); m=build_compatibility_matrix(o,v); assert len(m)==12 and not m.duplicated(['order_ref','vehicle_id']).any()
 assert m.loc[(m.order_ref=='o1')&(m.vehicle_id=='v1'),'is_compatible'].item()
 assert not m.loc[(m.order_ref=='o1')&(m.vehicle_id=='v2'),'refrigeration_ok'].item()
 assert not m.loc[(m.order_ref=='o1')&(m.vehicle_id=='v4'),'access_ok'].item()
 assert m.loc[(m.order_ref=='o2')&(m.vehicle_id=='v1'),'refrigeration_ok'].item()
 assert not m.loc[m.vehicle_id.eq('v3'),'home_depot_ok'].any()
 assert 'WEIGHT_EXCEEDS_CAPACITY' in m.loc[(m.order_ref=='o3')&(m.vehicle_id=='v1'),'failure_reasons'].item()
def test_order_and_vehicle_summaries_retain_zero_cases():
 o,v=_inputs(); m=build_compatibility_matrix(o,v); summary=order_compatibility_summary(m); vehicles=vehicle_scarcity_summary(m)
 assert len(summary)==3 and summary.total_usable_vehicle_count.eq(4).all()
 assert len(vehicles)==4 and {'exclusive_order_count','compatible_chilled_order_count'}.issubset(vehicles)
