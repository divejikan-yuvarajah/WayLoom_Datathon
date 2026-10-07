import hashlib
import json
from pathlib import Path

from scripts.export_integration_contract import export_contract
from scripts.validate_integration_contract import _validate_synthetic_health, validate_contract
from src.integration.service import load_config


ROOT = Path(__file__).resolve().parents[1]


def test_contract_export_allowlist_and_manifest(tmp_path, monkeypatch):
    # The production guard intentionally fixes exports under repository dist.
    import scripts.export_integration_contract as exporter
    import scripts.validate_integration_contract as validator

    output = tmp_path / "dist" / "integration_contract"
    monkeypatch.setattr(exporter, "assert_safe_export_root", lambda value: Path(value).resolve())
    monkeypatch.setattr(validator, "assert_safe_export_root", lambda value: Path(value).resolve())
    export_contract(ROOT / "configs" / "integration.yaml", output)
    result = validate_contract(ROOT / "configs" / "integration.yaml", output)
    collision = result["identifier_collision_audit"]
    assert collision["status"] == "NOT_RUN"
    assert collision["overlap_count"] is None
    assert result["fastapi_healthcheck"] == "PASS"

    files = sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file())
    assert "openapi.json" in files
    assert "PRIVACY_AND_DATA_BOUNDARY.md" in files
    assert len([name for name in files if name.startswith("schemas/")]) == 4
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert [entry["path"] for entry in manifest["files"]] == sorted(entry["path"] for entry in manifest["files"])
    for entry in manifest["files"]:
        assert hashlib.sha256((output / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
    joined = "\n".join(files).lower()
    assert "submission" not in joined and "model" not in joined and "private" not in joined.replace("privacy", "")


def test_repeated_export_is_reproducible(tmp_path, monkeypatch):
    import scripts.export_integration_contract as exporter
    output = tmp_path / "dist" / "integration_contract"
    monkeypatch.setattr(exporter, "assert_safe_export_root", lambda value: Path(value).resolve())
    export_contract(ROOT / "configs" / "integration.yaml", output)
    first = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    export_contract(ROOT / "configs" / "integration.yaml", output)
    second = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    assert first == second


def test_no_hardcoded_overlap_pass(tmp_path, monkeypatch):
    import scripts.export_integration_contract as exporter
    import scripts.validate_integration_contract as validator
    output = tmp_path / "dist" / "integration_contract"
    monkeypatch.setattr(exporter, "assert_safe_export_root", lambda value: Path(value).resolve())
    monkeypatch.setattr(validator, "assert_safe_export_root", lambda value: Path(value).resolve())
    export_contract(ROOT / "configs" / "integration.yaml", output)
    result = validate_contract(ROOT / "configs" / "integration.yaml", output)
    audit = result["identifier_collision_audit"]
    assert audit["status"] == "NOT_RUN"
    assert audit["overlap_count"] is None


def test_validator_healthcheck_uses_testclient():
    _validate_synthetic_health(load_config(ROOT / "configs" / "integration.yaml"))
