import inspect
from pathlib import Path

import pytest
import yaml

from scripts.validate_final_submissions import TASK_LABELS, _require_config
from src.common.submission_validation import SubmissionValidationError, read_strict_csv


def test_all_18_phase33_task_mappings_are_present():
    assert set(TASK_LABELS) == {f"DT-{number}" for number in range(420, 438)}


def test_config_freezes_filenames_and_read_only_controls():
    config = yaml.safe_load(Path("configs/final_submission_validation.yaml").read_text(encoding="utf-8"))
    assert config["filenames"] == {
        "task1": "submission_task1.csv",
        "task2a": "submission_task2a.csv",
        "task2b": "submission_task2b.csv",
    }
    assert config["integrity"] == {"read_only": True, "pre_post_sha256_equal": True}
    assert config["privacy"] == {
        "report_dir": "reports/private/phase33_final_submissions",
        "print_ids": False,
        "print_rows": False,
    }


@pytest.mark.parametrize("content", [
    "a,a\n1,2\n", "Unnamed: 0,a\n0,1\n", "a,b\n1\n", "a,b\n,\n",
])
def test_strict_csv_preflight_rejects_bad_csv(tmp_path, content):
    path = tmp_path / "bad.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(SubmissionValidationError):
        read_strict_csv(path)


def test_missing_csv_fails(tmp_path):
    with pytest.raises(SubmissionValidationError):
        read_strict_csv(tmp_path / "missing.csv")


def test_validator_contains_no_hardcoded_real_row_counts():
    source = Path("scripts/validate_final_submissions.py").read_text(encoding="utf-8")
    assert "85" not in source
    assert "OPTIMALITY" not in source


def test_console_task_labels_are_aggregate_only():
    labels = " ".join(TASK_LABELS.values())
    assert not any(name in labels for name in ("delivery_id", "row_id", "order_ref", "outlet_id", "vehicle_id"))


def test_config_validation_rejects_weak_integrity(tmp_path):
    config = yaml.safe_load(Path("configs/final_submission_validation.yaml").read_text(encoding="utf-8"))
    config["integrity"]["read_only"] = False
    args = type("Args", (), {"report_dir": Path("reports/private/phase33_final_submissions")})()
    with pytest.raises(ValueError, match="read-only"):
        _require_config(config, args)


def test_orchestrator_returns_nonzero_unless_every_gate_passes():
    source = inspect.getsource(__import__("scripts.validate_final_submissions", fromlist=["main"]).main)
    assert "return 0 if all_pass else 1" in source
    assert "checker_status == \"PASS\"" in source
    assert "hashes_unchanged" in source
