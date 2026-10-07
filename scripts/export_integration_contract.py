"""Build the allowlisted, synthetic-only Phase 28 share package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.integration import CONTRACT_VERSION
from src.integration.privacy import assert_public_text, assert_safe_export_member, assert_safe_export_root
from src.integration.schemas import generated_schemas
from src.integration.service import create_app, validate_config
from src.integration.synthetic_data import tracked_examples


DOCS = {
    "README.md": ROOT / "docs" / "integration" / "WAYLOOM_INTEGRATION_CONTRACT.md",
    "PRIVACY_AND_DATA_BOUNDARY.md": ROOT / "docs" / "integration" / "PRIVACY_AND_DATA_BOUNDARY.md",
}
SCHEMA_SOURCE = ROOT / "schemas" / "integration"
EXAMPLE_SOURCE = ROOT / "examples" / "integration"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def export_contract(config_path: Path, output_dir: Path) -> Path:
    with config_path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_config(config)
    if config["mode"] != "synthetic_demo":
        raise ValueError("Shareable export requires synthetic_demo mode.")
    output = assert_safe_export_root(output_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for filename, source in DOCS.items():
        content = source.read_text(encoding="utf-8")
        assert_public_text(content)
        _write_bytes(output / filename, content.encode("utf-8"))
    _write_bytes(output / "contract_version.json", _json_bytes({
        "contract_version": CONTRACT_VERSION,
        "integration_status": "optional_shared",
        "privacy_mode": "synthetic_only",
    }))
    expected_schemas = generated_schemas()
    for filename, schema in sorted(expected_schemas.items()):
        source = SCHEMA_SOURCE / filename
        if json.loads(source.read_text(encoding="utf-8")) != schema:
            raise ValueError("Tracked integration schema drift detected.")
        _write_bytes(output / "schemas" / filename, source.read_bytes())
    expected_examples = tracked_examples(int(config["synthetic"]["seed"]))
    for filename, example in sorted(expected_examples.items()):
        source = EXAMPLE_SOURCE / filename
        if json.loads(source.read_text(encoding="utf-8")) != example:
            raise ValueError("Tracked synthetic example drift detected.")
        _write_bytes(output / "examples" / filename, source.read_bytes())
    openapi = create_app(config).openapi()
    openapi_text = _json_bytes(openapi)
    assert_public_text(openapi_text.decode("utf-8"))
    _write_bytes(output / "openapi.json", openapi_text)

    members = sorted(
        (path for path in output.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(output).as_posix(),
    )
    for member in members:
        assert_safe_export_member(output, member)
        assert_public_text(member.read_text(encoding="utf-8"))
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": config["export"]["generated_at"],
        "privacy_mode": "synthetic_only",
        "files": [
            {
                "path": member.relative_to(output).as_posix(),
                "sha256": hashlib.sha256(member.read_bytes()).hexdigest(),
            }
            for member in members
        ],
    }
    _write_bytes(output / "manifest.json", _json_bytes(manifest))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = export_contract(args.config, args.output_dir)
    print("LOCAL PHASE 28 CONTRACT EXPORT: PASS")
    print(f"EXPORTED FILE COUNT: {sum(1 for p in output.rglob('*') if p.is_file())}")
    print("EXPORT PRIVATE FILE COUNT: 0")
    print("PRIVATE IDENTIFIERS PRINTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
