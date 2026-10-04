"""Build local-only Phase 20 pools and order allowances; console is sanitized."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)) if str(ROOT) not in sys.path else None
from src.common.data_inventory import discover_dataset_files,load_manifest
from src.task2b.scenario import build_s1_scenario,load_scenario_config
from src.task2b.trip_groups import build_brand_district_pools
from src.task2b.trip_time import load_trip_time_config
def main():
 p=argparse.ArgumentParser(); [p.add_argument(x,required=True,type=Path) for x in ('--raw-root','--manifest','--scenario-config','--trip-time-config','--pool-output','--allowance-output','--report-dir')]; a=p.parse_args(); cfg=load_scenario_config(str(a.scenario_config)); load_trip_time_config(str(a.trip_time_config)); f=discover_dataset_files(a.raw_root,load_manifest(a.manifest))['found_artifacts']; get=lambda n:pd.read_csv(f[cfg['files'][n]]['path'])
 s=build_s1_scenario(get('orders'),get('fleet'),get('vehicles'),get('district_travel'),get('service_allowance'),cfg); pools=build_brand_district_pools(s['orders_s1']); allowances=s['orders_s1'].merge(s['service_allowance_ref'][['brand','dock_type','service_allowance_min']],on=['brand','dock_type'],how='left',validate='many_to_one')
 if allowances.service_allowance_min.isna().any(): raise ValueError('Missing service allowance.')
 for path,frame in ((a.pool_output,pools),(a.allowance_output,allowances)): path.parent.mkdir(parents=True,exist_ok=True); frame.to_csv(path,index=False)
 allowed=(ROOT/'reports/private/phase20_task2b_trip_time').resolve(); report=a.report_dir.resolve()
 if not report.is_relative_to(allowed): raise ValueError('Private report path is invalid.')
 report.mkdir(parents=True,exist_ok=True); (report/'trip_time_context_status.txt').write_text('PASS\n',encoding='utf-8'); print('LOCAL PHASE 20 TASK2B TRIP TIME: PASS'); print('PRIVATE ORDER VALUES PRINTED: NO'); return 0
if __name__=='__main__': raise SystemExit(main())
