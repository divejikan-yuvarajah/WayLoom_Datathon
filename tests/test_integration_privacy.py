from pathlib import Path

import pytest

from src.integration.adapters import public_model_dict
from src.integration.models import HealthResponse
from src.integration.privacy import (
    PrivacyError,
    audit_identifier_sets,
    assert_not_protected_path,
    assert_public_payload,
    assert_safe_export_member,
    collision_audit_not_run,
    collect_synthetic_identifiers,
    run_private_identifier_collision_audit,
    safe_error_message,
    synthetic_overlap_count,
)


@pytest.mark.parametrize("value", [
    "data/raw/example.csv",
    "data/../data/raw/example.csv",
    "data/interim/example.csv",
    "reports/private/evidence.json",
    "outputs/submission_task1.csv",
    "outputs/submission_task2a.csv",
    "outputs/submission_task2b.csv",
])
def test_protected_paths_rejected(value):
    with pytest.raises(PrivacyError):
        assert_not_protected_path(value)


def test_absolute_protected_path_rejected():
    absolute = Path.cwd() / "reports" / "private" / "evidence.json"
    with pytest.raises(PrivacyError):
        assert_not_protected_path(absolute)


def test_safe_error_discards_sensitive_input():
    result = safe_error_message(RuntimeError(r"failure at C:\Users\someone\secret.csv"))
    assert "Users" not in result and "secret" not in result


def test_public_payload_and_serializer_are_allowlisted():
    with pytest.raises(PrivacyError):
        assert_public_payload({"order_ref": "anything"})
    assert public_model_dict(HealthResponse(mode="synthetic_demo"))["status"] == "ok"
    with pytest.raises(TypeError):
        public_model_dict({"unexpected_internal_field": "secret"})


def test_overlap_validator_returns_count_only():
    assert synthetic_overlap_count({"DEMO_DELIVERY_001", "X"}, {"X", "REAL"}) == 1


def test_collision_audit_without_private_inputs_is_not_run():
    result = collision_audit_not_run()
    assert result["status"] == "NOT_RUN"
    assert result["overlap_count"] is None


def test_collision_audit_zero_overlap_passes_and_returns_counts_only():
    result = audit_identifier_sets(
        {"DEMO_DELIVERY_001"},
        {"delivery_id": {"OFFICIAL_001"}, "row_id": {"ROW_001"}},
    )
    assert result["status"] == "PASS" and result["overlap_count"] == 0
    assert "OFFICIAL_001" not in str(result) and "ROW_001" not in str(result)


def test_collision_audit_detects_overlap_without_returning_value():
    result = audit_identifier_sets(
        {"DEMO_DELIVERY_001"},
        {"delivery_id": {"DEMO_DELIVERY_001"}},
    )
    assert result["status"] == "FAIL" and result["overlap_count"] == 1
    assert "DEMO_DELIVERY_001" not in str(result)


def test_synthetic_identifier_collection_and_malformed_private_input(tmp_path):
    identifiers = collect_synthetic_identifiers([
        {"delivery_ref": "DEMO_DELIVERY_001", "other": "not-an-id"}
    ])
    assert identifiers == {"DEMO_DELIVERY_001"}
    result = run_private_identifier_collision_audit(
        raw_root=tmp_path / "not-approved",
        manifest_path=tmp_path / "manifest.yaml",
        synthetic_ids=identifiers,
    )
    assert result["status"] == "FAIL" and result["overlap_count"] is None
    assert "not-approved" not in str(result)


def test_export_member_rejects_escape_and_symlink(tmp_path):
    root = tmp_path / "integration_contract"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    with pytest.raises(PrivacyError):
        assert_safe_export_member(root, outside)
    link = root / "openapi.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks unavailable on this host")
    with pytest.raises(PrivacyError):
        assert_safe_export_member(root, link)
