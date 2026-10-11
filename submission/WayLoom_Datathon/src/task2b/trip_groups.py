"""Phase 20 brand/district pools and strict candidate-trip validation."""
from __future__ import annotations
import pandas as pd
class TripGroupError(ValueError): pass
def validate_candidate_trip(orders: pd.DataFrame) -> pd.DataFrame:
 if orders.empty: raise TripGroupError('Candidate trip cannot be empty.')
 required={'order_ref','brand','district','outlet_id','depot','dock_type'}
 if required.difference(orders): raise TripGroupError('Candidate trip columns are incomplete.')
 if orders.order_ref.isna().any() or orders.order_ref.duplicated().any(): raise TripGroupError('Candidate trip order_ref must be unique.')
 if orders.brand.nunique()!=1: raise TripGroupError('Candidate trip must contain exactly one brand.')
 if orders.district.nunique()!=1: raise TripGroupError('Candidate trip must contain exactly one district.')
 return orders.copy(deep=True)
def build_brand_district_pools(orders: pd.DataFrame) -> pd.DataFrame:
 required={'scenario','brand','district','order_ref','order_weight_kg','order_volume_m3'}
 if required.difference(orders): raise TripGroupError('Order pool columns are incomplete.')
 rows=[]
 for (brand,district),group in orders.groupby(['brand','district'],sort=True):
  validate_candidate_trip(group)
  rows.append({'scenario':group.scenario.iloc[0],'brand':brand,'district':district,'order_count':len(group),'total_weight_kg':float(group.order_weight_kg.sum()),'total_volume_m3':float(group.order_volume_m3.sum()),'order_refs_private_only':'|'.join(map(str,group.order_ref)),'diagnostic_only':True,'capacity_checked':False,'vehicle_assigned':False,'time_budget_checked':False})
 return pd.DataFrame(rows)
