from pathlib import Path

import pytest

from scripts.validate_architecture_docs import (
    ABSOLUTE_PATH_RE,
    PLACEHOLDER_RE,
    PRIVATE_ID_RE,
    SECRET_RE,
    _validate_privacy,
)


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs/architecture"


def _architecture_files():
    return sorted(path for path in ARCH.iterdir() if path.suffix in {".md", ".yaml", ".mmd", ".svg"})


def test_architecture_files_pass_privacy_scan():
    _validate_privacy(_architecture_files())


@pytest.mark.parametrize("pattern,value", [
    (ABSOLUTE_PATH_RE, r"C:\Users\person\private.csv"),
    (ABSOLUTE_PATH_RE, "/home/person/private.csv"),
    (PRIVATE_ID_RE, "ORD0092308"),
    (PRIVATE_ID_RE, "VEH014"),
    (PLACEHOLDER_RE, "FINAL_MODEL_HERE"),
    (SECRET_RE, "api_key=abcdefghijklmnop"),
])
def test_privacy_patterns_reject_unsafe_examples(pattern, value):
    assert pattern.search(value)


def test_no_private_or_external_storage_references():
    joined = "\n".join(path.read_text(encoding="utf-8") for path in _architecture_files()).lower()
    assert "reports/private" not in joined
    assert "s3://" not in joined
    assert "gs://" not in joined
    assert "azure://" not in joined
