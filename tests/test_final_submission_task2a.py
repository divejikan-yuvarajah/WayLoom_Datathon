from pathlib import Path

import pytest

from src.common.submission_validation import read_strict_csv
from src.task2a.final_submission_validation import validate_final_task2a


HEADER = "row_id,pred_total_volume_m3,pred_chilled_volume_m3\n"


def _case(tmp_path: Path, rows="r1,10,0\nr2,12,0\nr3,15,5\n", name="submission_task2a.csv"):
    submission, template, inputs = tmp_path / name, tmp_path / "template.csv", tmp_path / "inputs.csv"
    submission.write_text(HEADER + rows, encoding="utf-8")
    template.write_text(HEADER + "r1,,\nr2,,\nr3,,\n", encoding="utf-8")
    inputs.write_text("row_id,brand\nr1,Style\nr2,Tech\nr3,Fresh\n", encoding="utf-8")
    return read_strict_csv(submission), read_strict_csv(template), read_strict_csv(inputs)


def test_valid_task2a_including_fresh_positive_and_less_than_total(tmp_path):
    assert validate_final_task2a(*_case(tmp_path)).status == "PASS"


def test_task2a_exact_filename_and_schema(tmp_path):
    assert validate_final_task2a(*_case(tmp_path, name="submission_task2a_final.csv")).checks["DT-427"] == "FAIL"
    submission, template, inputs = _case(tmp_path)
    submission.path.write_text("row_id,pred_chilled_volume_m3,pred_total_volume_m3\nr1,0,1\n", encoding="utf-8")
    assert validate_final_task2a(read_strict_csv(submission.path), template, inputs).checks["DT-427"] == "FAIL"


@pytest.mark.parametrize("rows", [
    "r1,10,0\nr2,12,0\n",
    "r2,12,0\nr1,10,0\nr3,15,5\n",
    "changed,10,0\nr2,12,0\nr3,15,5\n",
    "r1,10,0\nr1,12,0\nr3,15,5\n",
])
def test_task2a_template_identity_and_order(tmp_path, rows):
    assert validate_final_task2a(*_case(tmp_path, rows=rows)).checks["DT-428"] == "FAIL"


def test_task2a_brand_lookup_must_be_one_to_one(tmp_path):
    submission, template, inputs = _case(tmp_path)
    inputs.path.write_text("row_id,brand\nr1,Style\nr1,Tech\nr3,Fresh\n", encoding="utf-8")
    assert validate_final_task2a(submission, template, read_strict_csv(inputs.path)).checks["DT-428"] == "FAIL"


@pytest.mark.parametrize("rows", [
    "r1,-1,0\nr2,12,0\nr3,15,5\n", "r1,10,-1\nr2,12,0\nr3,15,5\n",
    "r1,nan,0\nr2,12,0\nr3,15,5\n", "r1,inf,0\nr2,12,0\nr3,15,5\n",
])
def test_task2a_predictions_finite_nonnegative(tmp_path, rows):
    assert validate_final_task2a(*_case(tmp_path, rows=rows)).checks["DT-429"] == "FAIL"


def test_style_and_tech_are_checked_separately(tmp_path):
    assert validate_final_task2a(*_case(tmp_path, rows="r1,10,0.1\nr2,12,0\nr3,15,5\n")).checks["DT-430"] == "FAIL"
    assert validate_final_task2a(*_case(tmp_path, rows="r1,10,0\nr2,12,0.1\nr3,15,5\n")).checks["DT-431"] == "FAIL"


@pytest.mark.parametrize(("chilled", "expected"), [("15", "PASS"), ("14", "PASS"), ("16", "FAIL")])
def test_chilled_relation(tmp_path, chilled, expected):
    rows = f"r1,10,0\nr2,12,0\nr3,15,{chilled}\n"
    assert validate_final_task2a(*_case(tmp_path, rows=rows)).checks["DT-432"] == expected


def test_negative_zero_is_warning_not_failure_and_no_rewrite(tmp_path):
    submission, template, inputs = _case(tmp_path, rows="r1,10,-0.0\nr2,12,0\nr3,15,5\n")
    before = submission.path.read_bytes()
    report = validate_final_task2a(submission, template, inputs)
    assert report.status == "PASS" and report.warnings
    assert submission.path.read_bytes() == before
