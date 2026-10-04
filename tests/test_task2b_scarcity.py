"""Synthetic Phase 19 scarcity diagnostics tests."""
from src.task2b.compatibility import build_compatibility_matrix,order_compatibility_summary,vehicle_scarcity_summary
from src.task2b.scarcity import build_scarcity_report
from tests.test_task2b_compatibility import _inputs
def test_scarcity_is_diagnostic_and_has_trip_slot_bound():
 o,v=_inputs(); m=build_compatibility_matrix(o,v); report=build_scarcity_report(m,order_compatibility_summary(m),vehicle_scarcity_summary(m))
 assert report['pair_count']==12 and report['trip_slot_pressure']['theoretical_trip_slot_upper_bound']==8
 assert 'REFRIGERATION_MISMATCH' in report['failure_reason_counts']
