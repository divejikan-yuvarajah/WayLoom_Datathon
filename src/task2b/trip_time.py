"""Pure Phase 20 official trip-time formula; no allocation or budget logic."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np,pandas as pd,yaml
from src.task2b.trip_groups import validate_candidate_trip,TripGroupError
class TripTimeError(ValueError): pass
@dataclass(frozen=True)
class TripTimeBreakdown:
 brand:str; district:str; order_count:int; outbound_minutes:float; inter_stop_minutes:float; handling_minutes:float; trip_minutes:float; return_minutes_added:float=0.0
def load_trip_time_config(path:str)->dict:
 c=yaml.safe_load(open(path,encoding='utf-8'))
 expected={'same_brand':True,'same_district':True,'reject_empty_trip':True,'reject_duplicate_order_ref':True,'outbound_count':'exactly_once','inter_stop_rule':'n_orders_minus_one','service_allowance_keys':['brand','dock_type'],'include_return_leg':False,'rounding':'none'}
 if not isinstance(c,dict) or c.get('version')!=1 or any(c.get(k)!=v for k,v in expected.items()): raise TripTimeError('Trip-time configuration violates the official formula.')
 return c
def calculate_trip_time(candidate_orders:pd.DataFrame, district_travel_ref:pd.DataFrame, service_allowance_ref:pd.DataFrame)->TripTimeBreakdown:
 orders=validate_candidate_trip(candidate_orders); depot=orders.depot.iloc[0]; district=orders.district.iloc[0]; brand=orders.brand.iloc[0]
 needed={'depot','district','depot_to_district_freeflow_min','inter_stop_freeflow_min'}
 if needed.difference(district_travel_ref): raise TripTimeError('District travel reference is incomplete.')
 travel=district_travel_ref.loc[(district_travel_ref.depot==depot)&(district_travel_ref.district==district)]
 if len(travel)!=1: raise TripTimeError('Candidate trip requires exactly one district travel reference.')
 outbound,inter=(float(travel.depot_to_district_freeflow_min.iloc[0]),float(travel.inter_stop_freeflow_min.iloc[0]))
 if not np.isfinite([outbound,inter]).all() or outbound<0 or inter<0: raise TripTimeError('District travel values must be finite and nonnegative.')
 required={'brand','dock_type','service_allowance_min'}
 if required.difference(service_allowance_ref) or service_allowance_ref.duplicated(['brand','dock_type']).any(): raise TripTimeError('Service allowance reference is invalid.')
 joined=orders.merge(service_allowance_ref[['brand','dock_type','service_allowance_min']],on=['brand','dock_type'],how='left',validate='many_to_one')
 if joined.service_allowance_min.isna().any(): raise TripTimeError('Candidate trip has a missing brand+dock service allowance.')
 handling=float(joined.service_allowance_min.sum())
 if not np.isfinite(handling) or handling<0: raise TripTimeError('Service allowance must be finite and nonnegative.')
 inter_stop=inter*(len(orders)-1); total=outbound+inter_stop+handling
 return TripTimeBreakdown(brand,district,len(orders),outbound,inter_stop,handling,total,0.0)
