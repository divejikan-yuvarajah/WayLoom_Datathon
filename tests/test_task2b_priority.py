import pandas as pd
from src.task2b.priority import build_order_priority_metadata,better_objective,hard_soft_classification
from tests.test_task2b_compatibility import _inputs
from src.task2b.compatibility import order_compatibility_summary,build_compatibility_matrix
def test_metadata_signals_alternatives_and_objective_order():
 o,v=_inputs(); o['deferred_yesterday']=[1,0,0]; o['days_since_last_served']=[4,1,0]; m=build_compatibility_matrix(o,v); meta=build_order_priority_metadata(o,order_compatibility_summary(m),m)
 assert len(meta)==3 and meta.order_ref.tolist()==['o1','o2','o3']; assert meta.loc[meta.order_ref=='o3','is_individually_impossible'].item() == True
 assert better_objective({'served_order_count':10},{'served_order_count':9}); assert better_objective({'served_order_count':10,'served_previous_deferred_count':3},{'served_order_count':10,'served_previous_deferred_count':2})
 assert better_objective({'hard_feasible':True,'served_order_count':1},{'hard_feasible':False,'served_order_count':99})
 assert not better_objective({'hard_feasible':False,'served_order_count':99},{'hard_feasible':True,'served_order_count':1})
 assert hard_soft_classification()['chilled_requires_reefer']=='HARD_OFFICIAL'
