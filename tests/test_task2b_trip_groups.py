import pandas as pd,pytest
from src.task2b.trip_groups import build_brand_district_pools,validate_candidate_trip,TripGroupError
def _orders(): return pd.DataFrame([{'scenario':'S1','order_ref':'a','outlet_id':'same','brand':'Fresh','district':'G','depot':'Peliyagoda','dock_type':'rear_dock','order_weight_kg':1,'order_volume_m3':1},{'scenario':'S1','order_ref':'b','outlet_id':'same','brand':'Fresh','district':'G','depot':'Peliyagoda','dock_type':'street','order_weight_kg':1,'order_volume_m3':1}])
def test_groups_and_candidate_invariants():
 o=_orders(); assert build_brand_district_pools(o).order_count.item()==2; assert len(validate_candidate_trip(o))==2
 for bad in (o.iloc[:0],o.assign(brand=['Fresh','Style']),o.assign(district=['G','C']),o.assign(order_ref=['a','a'])):
  with pytest.raises(TripGroupError): validate_candidate_trip(bad)
