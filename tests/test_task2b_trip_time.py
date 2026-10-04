import pandas as pd,pytest
from src.task2b.trip_time import calculate_trip_time,TripTimeError
def _refs():
 return pd.DataFrame([{'depot':'Peliyagoda','district':'Gampaha','depot_to_district_freeflow_min':37,'inter_stop_freeflow_min':9},{'depot':'Peliyagoda','district':'Colombo','depot_to_district_freeflow_min':24,'inter_stop_freeflow_min':8}]),pd.DataFrame([{'brand':'Fresh','dock_type':'rear_dock','service_allowance_min':15},{'brand':'Fresh','dock_type':'street','service_allowance_min':16}])
def _orders(district,docks): return pd.DataFrame([{'order_ref':str(i),'outlet_id':'same','brand':'Fresh','district':district,'depot':'Peliyagoda','dock_type':d} for i,d in enumerate(docks)])
def test_official_examples_and_no_return():
 t,a=_refs(); g=calculate_trip_time(_orders('Gampaha',['rear_dock','rear_dock','street']),t,a); assert (g.outbound_minutes,g.inter_stop_minutes,g.handling_minutes,g.return_minutes_added,g.trip_minutes)==(37,18,46,0,101)
 c=calculate_trip_time(_orders('Colombo',['street']*4),t,a); assert c.trip_minutes==112
def test_count_orders_and_reference_fail_closed():
 t,a=_refs(); one=calculate_trip_time(_orders('Gampaha',['street']),t,a); assert one.inter_stop_minutes==0
 with pytest.raises(TripTimeError): calculate_trip_time(_orders('Gampaha',['other']),t,a)
 with pytest.raises(TripTimeError): calculate_trip_time(_orders('Gampaha',['street']),pd.concat([t,t.iloc[[0]]]),a)
