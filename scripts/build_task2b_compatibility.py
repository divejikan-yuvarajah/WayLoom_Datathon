"""Build local-only Phase 19 compatibility artifacts with sanitized console output."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)) if str(ROOT) not in sys.path else None
from src.common.data_inventory import discover_dataset_files,load_manifest
from src.task2b.scenario import build_s1_scenario,load_scenario_config
from src.task2b.compatibility import build_compatibility_matrix,order_compatibility_summary,vehicle_scarcity_summary
from src.task2b.scarcity import build_scarcity_report
def main():
 p=argparse.ArgumentParser(); [p.add_argument(x,required=True,type=Path) for x in ('--raw-root','--manifest','--scenario-config','--compatibility-config','--matrix-output','--order-summary-output','--vehicle-summary-output','--report-dir')]; a=p.parse_args()
 cfg=load_scenario_config(str(a.scenario_config)); cc=yaml.safe_load(a.compatibility_config.read_text()); found=discover_dataset_files(a.raw_root,load_manifest(a.manifest))["found_artifacts"]; get=lambda n:pd.read_csv(found[cfg['files'][n]]['path'])
 s=build_s1_scenario(get('orders'),get('fleet'),get('vehicles'),get('district_travel'),get('service_allowance'),cfg)
 m=build_compatibility_matrix(s['orders_s1'],s['usable_fleet_s1'],tolerance=float(cc['tolerance'])); o=order_compatibility_summary(m,low_flexibility_threshold=int(cc['low_flexibility_threshold'])); v=vehicle_scarcity_summary(m)
 for path,frame in ((a.matrix_output,m),(a.order_summary_output,o),(a.vehicle_summary_output,v)): path.parent.mkdir(parents=True,exist_ok=True); frame.to_csv(path,index=False)
 allowed=(ROOT/'reports/private/phase19_task2b_compatibility').resolve(); report=a.report_dir.resolve()
 if not report.is_relative_to(allowed): raise ValueError('Private report path is invalid.')
 report.mkdir(parents=True,exist_ok=True); (report/'scarcity_report.json').write_text(json.dumps(build_scarcity_report(m,o,v),indent=2),encoding='utf-8')
 print('LOCAL PHASE 19 TASK2B COMPATIBILITY: PASS'); print('PRIVATE PAIRS PRINTED: NO'); return 0
if __name__=='__main__': raise SystemExit(main())
