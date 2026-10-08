from pathlib import Path

import pytest

from src.common.submission_validation import read_strict_csv
from src.task1.final_submission_validation import validate_final_task1


HEADER = "delivery_id,pred_service_min,pred_late_prob\n"


def _files(tmp_path: Path, body="d1,10,0\nd2,20,1\n", name="submission_task1.csv"):
    template = tmp_path / "template.csv"
    submission = tmp_path / name
    template.write_text(HEADER + "d1,,\nd2,,\n", encoding="utf-8")
    submission.write_text(HEADER + body, encoding="utf-8")
    return read_strict_csv(submission), read_strict_csv(template)


def test_valid_task1_and_probability_endpoints(tmp_path):
    report = validate_final_task1(*_files(tmp_path))
    assert report.status == "PASS"


@pytest.mark.parametrize(("name", "task"), [
    ("Submission_Task1.csv", "DT-420"),
    ("submission_task1_final.csv", "DT-420"),
])
def test_wrong_filename_fails(tmp_path, name, task):
    report = validate_final_task1(*_files(tmp_path, name=name))
    assert report.checks[task] == "FAIL"


@pytest.mark.parametrize(("header", "row"), [
    ("delivery_id,pred_late_prob,pred_service_min\n", "d1,0,10\n"),
    ("delivery_id,pred_service_min\n", "d1,10\n"),
    ("delivery_id,pred_service_min,pred_late_prob,debug\n", "d1,10,0,x\n"),
])
def test_exact_columns_required(tmp_path, header, row):
    submission, template = _files(tmp_path)
    submission.path.write_text(header + row, encoding="utf-8")
    assert validate_final_task1(read_strict_csv(submission.path), template).checks["DT-421"] == "FAIL"


@pytest.mark.parametrize(("body", "task"), [
    ("d1,10,0\n", "DT-422"),
    ("d2,20,1\nd1,10,0\n", "DT-423"),
    ("changed,10,0\nd2,20,1\n", "DT-424"),
    ("d1,10,0\nd1,20,1\n", "DT-424"),
    (",10,0\nd2,20,1\n", "DT-424"),
])
def test_row_and_id_integrity(tmp_path, body, task):
    assert validate_final_task1(*_files(tmp_path, body=body)).checks[task] == "FAIL"


@pytest.mark.parametrize("body", [
    "d1,,0\nd2,20,1\n", "d1,nan,0\nd2,20,1\n", "d1,inf,0\nd2,20,1\n",
    "d1,-inf,0\nd2,20,1\n", "d1,-1,0\nd2,20,1\n",
])
def test_predictions_must_be_finite_and_service_nonnegative(tmp_path, body):
    assert validate_final_task1(*_files(tmp_path, body=body)).checks["DT-425"] == "FAIL"


@pytest.mark.parametrize("probability", ["-0.0001", "1.0001", "nan", "inf", "text", ""])
def test_probability_range_rejects_invalid_values(tmp_path, probability):
    body = f"d1,10,{probability}\nd2,20,0.5\n"
    assert validate_final_task1(*_files(tmp_path, body=body)).checks["DT-426"] == "FAIL"


def test_task1_validator_never_rewrites(tmp_path):
    submission, template = _files(tmp_path)
    before = submission.path.read_bytes()
    validate_final_task1(submission, template)
    assert submission.path.read_bytes() == before
