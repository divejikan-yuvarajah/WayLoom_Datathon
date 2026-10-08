from pathlib import Path

import pytest

from src.common.submission_validation import read_strict_csv
from src.task2b.final_submission_validation import validate_final_task2b


HEADER = "scenario,order_ref,outlet_id,decision,vehicle_id,trip_id\n"
VALID = "S1,o1,shared,served,v1,1\nS1,o2,shared,deferred,,\nS1,o3,other,served,v2,2\n"


def _case(tmp_path: Path, rows=VALID, name="submission_task2b.csv"):
    submission, template = tmp_path / name, tmp_path / "template.csv"
    submission.write_text(HEADER + rows, encoding="utf-8")
    template.write_text(HEADER + "S1,o1,shared,(served/deferred),(e.g. VEH014),(1 or 2)\nS1,o2,shared,(served/deferred),(e.g. VEH014),(1 or 2)\nS1,o3,other,(served/deferred),(e.g. VEH014),(1 or 2)\n", encoding="utf-8")
    return read_strict_csv(submission), read_strict_csv(template)


def test_valid_task2b_allows_repeated_outlet_and_raw_blanks(tmp_path):
    assert validate_final_task2b(*_case(tmp_path)).status == "PASS"


def test_task2b_exact_filename_and_columns(tmp_path):
    assert validate_final_task2b(*_case(tmp_path, name="task2b.csv")).checks["DT-433"] == "FAIL"
    submission, template = _case(tmp_path)
    submission.path.write_text("scenario,order_ref,outlet_id,decision,vehicle_id\nS1,o1,x,served,v1\n", encoding="utf-8")
    assert validate_final_task2b(read_strict_csv(submission.path), template).checks["DT-433"] == "FAIL"


@pytest.mark.parametrize("rows", [
    "S1,o1,shared,served,v1,1\nS1,o2,shared,deferred,,\n",
    VALID + "S1,o4,x,deferred,,\n",
    "S1,o1,shared,served,v1,1\nS1,o1,shared,deferred,,\nS1,o3,other,served,v2,2\n",
    "S1,o1,wrong,served,v1,1\nS1,o2,shared,deferred,,\nS1,o3,other,served,v2,2\n",
    "S2,o1,shared,served,v1,1\nS1,o2,shared,deferred,,\nS1,o3,other,served,v2,2\n",
])
def test_all_orders_and_identity_triple(tmp_path, rows):
    assert validate_final_task2b(*_case(tmp_path, rows=rows)).checks["DT-434"] == "FAIL"


@pytest.mark.parametrize("field", ["(served/deferred)", "TODO", "TBD", "PLACEHOLDER", "<fill>", "[fill]"])
def test_placeholders_fail(tmp_path, field):
    rows = f"S1,o1,shared,{field},v1,1\nS1,o2,shared,deferred,,\nS1,o3,other,served,v2,2\n"
    assert validate_final_task2b(*_case(tmp_path, rows=rows)).checks["DT-435"] == "FAIL"


@pytest.mark.parametrize("row", [
    "S1,o1,shared,Served,v1,1", "S1,o1,shared,served ,v1,1",
    "S1,o1,shared,served,,1", "S1,o1,shared,served,v1,1.0",
    "S1,o1,shared,served,v1,trip 1", "S1,o1,shared,deferred,v1,",
    "S1,o1,shared,deferred,,NaN", "S1,o1,shared,deferred, ,",
])
def test_decision_and_dependent_field_format(tmp_path, row):
    rows = row + "\nS1,o2,shared,deferred,,\nS1,o3,other,served,v2,2\n"
    assert validate_final_task2b(*_case(tmp_path, rows=rows)).checks["DT-436"] == "FAIL"


def test_task2b_validator_never_rewrites(tmp_path):
    submission, template = _case(tmp_path)
    before = submission.path.read_bytes()
    validate_final_task2b(submission, template)
    assert submission.path.read_bytes() == before
