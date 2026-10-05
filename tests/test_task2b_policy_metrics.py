import pandas as pd
from src.task2b.policy_metrics import calculate_policy_metrics
from tests.test_task2b_compatibility import _inputs
from src.task2b.compatibility import build_compatibility_matrix,order_compatibility_summary
from src.task2b.priority import build_order_priority_metadata
def test_policy_metrics_are_order_level_and_deterministic():
 o,v=_inputs(); o['deferred_yesterday']=[1,0,0]; o['days_since_last_served']=[4,1,0]; m=build_compatibility_matrix(o,v); meta=build_order_priority_metadata(o,order_compatibility_summary(m),m); alloc=pd.DataFrame({'order_ref':['o1','o2','o3'],'served':[True,False,True]}); x=calculate_policy_metrics(alloc,meta,m); assert x['served_order_count']==2 and x['unique_outlets_served']==2 and x['deferred_order_count']==1; assert calculate_policy_metrics(alloc,meta,m)==x
