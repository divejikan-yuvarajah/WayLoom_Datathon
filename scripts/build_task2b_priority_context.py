"""Build local-only Phase 21 priority metadata; no final allocation."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)) if str(ROOT) not in sys.path else None
from src.common.data_inventory import discover_dataset_files,load_manifest
from src.task2b.scenario import build_s1_scenario,load_scenario_config
from src.task2b.compatibility import order_compatibility_summary
from src.task2b.priority import build_order_priority_metadata
def main():
 p=argparse.ArgumentParser(); [p.add_argument(x,required=True,type=Path) for x in ('--raw-root','--manifest','--scenario-config','--compatibility-config','--priority-config','--compatibility-summary','--compatibility-matrix','--metadata-output','--report-dir')]; a=p.parse_args(); cfg=load_scenario_config(str(a.scenario_config)); pc=yaml.safe_load(a.priority_config.read_text());
 if pc.get('strategy')!='lexicographic' or pc.get('hard_rule_override') is not False: raise ValueError('Invalid frozen priority policy.')
 f=discover_dataset_files(a.raw_root,load_manifest(a.manifest))['found_artifacts']; get=lambda n:pd.read_csv(f[cfg['files'][n]]['path']); s=build_s1_scenario(get('orders'),get('fleet'),get('vehicles'),get('district_travel'),get('service_allowance'),cfg)
 matrix=pd.read_csv(a.compatibility_matrix); summary=pd.read_csv(a.compatibility_summary); metadata=build_order_priority_metadata(s['orders_s1'],summary,matrix); a.metadata_output.parent.mkdir(parents=True,exist_ok=True); metadata.to_csv(a.metadata_output,index=False)
 allowed=(ROOT/'reports/private/phase21_task2b_priority').resolve(); report=a.report_dir.resolve()
 if not report.is_relative_to(allowed): raise ValueError('Private report path is invalid.')
 report.mkdir(parents=True,exist_ok=True); (report/'policy_status.txt').write_text('PASS\n',encoding='utf-8'); print('LOCAL PHASE 21 TASK2B PRIORITY: PASS'); print('PRIVATE PRIORITY VALUES PRINTED: NO'); return 0
if __name__=='__main__': raise SystemExit(main())
