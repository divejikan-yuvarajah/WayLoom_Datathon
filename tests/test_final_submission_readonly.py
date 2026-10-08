from pathlib import Path

from src.common.submission_validation import read_strict_csv, sha256_file
from src.task1.final_submission_validation import validate_final_task1
from src.task2a.final_submission_validation import validate_final_task2a
from src.task2b.final_submission_validation import validate_final_task2b


def _write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    return read_strict_csv(path)


def test_pass_and_fail_validation_never_rewrite_any_input(tmp_path):
    t1 = _write(tmp_path / "submission_task1.csv", "delivery_id,pred_service_min,pred_late_prob\na,1,0.5\n")
    t1_template = _write(tmp_path / "t1.csv", "delivery_id,pred_service_min,pred_late_prob\na,,\n")
    t2 = _write(tmp_path / "submission_task2a.csv", "row_id,pred_total_volume_m3,pred_chilled_volume_m3\nr,1,2\n")
    t2_template = _write(tmp_path / "t2.csv", "row_id,pred_total_volume_m3,pred_chilled_volume_m3\nr,,\n")
    inputs = _write(tmp_path / "inputs.csv", "row_id,brand\nr,Fresh\n")
    t3 = _write(tmp_path / "submission_task2b.csv", "scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\nS1,o,x,deferred,,\n")
    t3_template = _write(tmp_path / "t3.csv", "scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\nS1,o,x,(served/deferred),(e.g. VEH014),(1 or 2)\n")
    all_files = [t1, t1_template, t2, t2_template, inputs, t3, t3_template]
    before = {item.path: sha256_file(item.path) for item in all_files}
    assert validate_final_task1(t1, t1_template).status == "PASS"
    assert validate_final_task2a(t2, t2_template, inputs).status == "FAIL"
    assert validate_final_task2b(t3, t3_template).status == "PASS"
    assert before == {item.path: sha256_file(item.path) for item in all_files}
