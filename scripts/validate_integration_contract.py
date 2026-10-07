"""Validate the synthetic Phase 28 package without competition-data access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.integration import CONTRACT_VERSION
from src.integration.contract_validation import validate_contract_payload
from src.integration.privacy import (
    PrivacyError,
    collect_synthetic_identifiers,
    collision_audit_not_run,
    assert_public_payload,
    assert_public_text,
    assert_safe_export_member,
    assert_safe_export_root,
    run_private_identifier_collision_audit,
)
from src.integration.schemas import EXAMPLE_SCHEMA, load_json
from src.integration.service import ROUTES, create_app, validate_config
from src.integration.synthetic_data import tracked_examples


def _validate_synthetic_health(config: dict[str, object]) -> None:
    with TestClient(create_app(config)) as client:
        response = client.get("/health")
    if response.status_code != 200:
        raise ValueError("Synthetic application health check failed.")
    payload = response.json()
    if payload != {
        "status": "ok",
        "service": "wayloom-integration",
        "contract_version": config["contract_version"],
        "mode": "synthetic_demo",
    }:
        raise ValueError("Synthetic application health response is invalid.")


def validate_contract(
    config_path: Path,
    contract_dir: Path,
    *,
    raw_root: Path | None = None,
    manifest_path: Path | None = None,
    run_private_id_collision_audit: bool = False,
) -> dict[str, object]:
    with config_path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_config(config)
    root = assert_safe_export_root(contract_dir)
    if not root.is_dir():
        raise ValueError("Integration contract directory is missing.")

    required = {
        "README.md", "contract_version.json", "openapi.json",
        "PRIVACY_AND_DATA_BOUNDARY.md", "manifest.json",
        "schemas/task1.schema.json", "schemas/demand_forecast.schema.json",
        "schemas/allocation_insight.schema.json", "schemas/deferral_explanation.schema.json",
    }
    files = sorted(path for path in root.rglob("*") if path.is_file())
    relative = {path.relative_to(root).as_posix() for path in files}
    missing = sorted(required - relative)
    if missing:
        raise ValueError("Integration contract is incomplete.")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise PrivacyError("Symlinks are forbidden in the shareable package.")
    for path in files:
        assert_safe_export_member(root, path)
        assert_public_text(path.read_text(encoding="utf-8"))

    manifest = load_json(root / "manifest.json")
    if manifest.get("contract_version") != CONTRACT_VERSION or manifest.get("privacy_mode") != "synthetic_only":
        raise ValueError("Contract manifest metadata is invalid.")
    listed = manifest.get("files")
    if not isinstance(listed, list):
        raise ValueError("Contract manifest file list is invalid.")
    listed_paths = [entry.get("path") for entry in listed]
    expected_list = sorted(relative - {"manifest.json"})
    if listed_paths != expected_list:
        raise ValueError("Contract manifest ordering or membership is invalid.")
    for entry in listed:
        path = root / entry["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
            raise ValueError("Contract manifest hash mismatch.")

    schemas = {name: load_json(root / "schemas" / name) for name in {
        "task1.schema.json", "demand_forecast.schema.json",
        "allocation_insight.schema.json", "deferral_explanation.schema.json",
    }}
    example_payloads: list[dict[str, object]] = []
    for filename, schema_filename in EXAMPLE_SCHEMA.items():
        payload = load_json(root / "examples" / filename)
        assert_public_payload(payload)
        validate_contract_payload(schema_filename, payload, schema=schemas[schema_filename])
        example_payloads.append(payload)

    openapi = load_json(root / "openapi.json")
    assert_public_payload(openapi)
    documented = {
        f"{method.upper()} {path}"
        for path, methods in openapi.get("paths", {}).items()
        for method in methods
    }
    if not set(ROUTES).issubset(documented):
        raise ValueError("OpenAPI route set is incomplete.")
    fresh_openapi = create_app(config).openapi()
    if set(fresh_openapi.get("paths", {})) != set(openapi.get("paths", {})):
        raise ValueError("OpenAPI route contract drift detected.")
    _validate_synthetic_health(config)

    generated_payloads = list(tracked_examples(int(config["synthetic"]["seed"])).values())
    tracked_payloads = [
        load_json(ROOT / "examples" / "integration" / filename)
        for filename in EXAMPLE_SCHEMA
    ]
    synthetic_ids = collect_synthetic_identifiers([
        *example_payloads,
        *generated_payloads,
        *tracked_payloads,
        openapi,
    ])
    if run_private_id_collision_audit:
        if raw_root is None or manifest_path is None:
            collision = {
                "status": "FAIL",
                "overlap_count": None,
                "official_id_count_by_category": None,
                "synthetic_id_count": len(synthetic_ids),
                "overlap_count_by_category": None,
                "error_code": "PRIVATE_AUDIT_INPUT_REQUIRED",
            }
        else:
            collision = run_private_identifier_collision_audit(
                raw_root=raw_root,
                manifest_path=manifest_path,
                synthetic_ids=synthetic_ids,
            )
    elif raw_root is not None or manifest_path is not None:
        collision = {
            "status": "FAIL",
            "overlap_count": None,
            "official_id_count_by_category": None,
            "synthetic_id_count": len(synthetic_ids),
            "overlap_count_by_category": None,
            "error_code": "PRIVATE_AUDIT_FLAG_REQUIRED",
        }
    else:
        collision = collision_audit_not_run()
    return {
        "file_count": len(files),
        "identifier_collision_audit": collision,
        "fastapi_healthcheck": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--contract-dir", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--run-private-id-collision-audit", action="store_true")
    args = parser.parse_args()
    result = validate_contract(
        args.config,
        args.contract_dir,
        raw_root=args.raw_root,
        manifest_path=args.manifest,
        run_private_id_collision_audit=args.run_private_id_collision_audit,
    )
    collision = result["identifier_collision_audit"]
    print("WAYLOOM — PHASE 28 INTEGRATION CONTRACT")
    print(f"CONTRACT VERSION: {CONTRACT_VERSION}")
    print("FOUR JSON SCHEMAS: PASS")
    print("SYNTHETIC EXAMPLES: PASS")
    if collision["status"] == "NOT_RUN":
        print("SYNTHETIC/OFFICIAL ID OVERLAP: NOT_RUN")
        print("IDENTIFIER COLLISION AUDIT REASON: official identifier sets were not supplied")
    else:
        counts = collision.get("overlap_count_by_category") or {}
        for category in sorted(counts):
            print(f"{category.upper().replace('_', ' ')} OVERLAP COUNT: {counts[category]}")
        print(f"SYNTHETIC/OFFICIAL ID COLLISION AUDIT: {collision['status']}")
        value = collision.get("overlap_count")
        print(f"TOTAL OVERLAP COUNT: {value if value is not None else 'UNAVAILABLE'}")
    print("SHAREABLE CONTRACT EXPORT: PASS")
    print("EXPORT PRIVATE FILE COUNT: 0")
    print("FASTAPI SYNTHETIC APP HEALTHCHECK: PASS")
    print("SYNTHETIC MODE NEEDS COMPETITION DATA: NO")
    print("OPENAPI PRIVATE LEAKAGE: NO")
    print("PROTECTED PATH ACCESS: BLOCKED")
    if collision["status"] == "PASS":
        print("LOCAL PHASE 28 INTEGRATION VALIDATION: PASS")
    elif collision["status"] == "FAIL":
        print("LOCAL PHASE 28 INTEGRATION VALIDATION: FAIL")
    else:
        print("LOCAL PHASE 28 SAFE CONTRACT VALIDATION: PASS")
        print("LOCAL PHASE 28 PRIVATE COLLISION AUDIT: NOT_RUN")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 1 if collision["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
