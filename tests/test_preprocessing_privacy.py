from pathlib import Path

import pytest

from scripts.validate_preprocessing_doc import (
    ABSOLUTE_PATH_RE,
    PLACEHOLDER_RE,
    PRIVATE_ID_RE,
    SECRET_RE,
    STALE_MODEL_RE,
    _validate_privacy,
)


ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "docs" / "preprocessing.md", ROOT / "docs" / "preprocessing_manifest.yaml"]


def test_preprocessing_artifacts_pass_privacy_scan():
    _validate_privacy("\n".join(path.read_text(encoding="utf-8") for path in FILES))


@pytest.mark.parametrize(
    "pattern,value",
    [
        (ABSOLUTE_PATH_RE, r"C:\Users\person\private.csv"),
        (ABSOLUTE_PATH_RE, "/home/person/private.csv"),
        (PRIVATE_ID_RE, "ORD0092308"),
        (PRIVATE_ID_RE, "VEH014"),
        (PLACEHOLDER_RE, "FINAL_MODEL_HERE"),
        (SECRET_RE, "api_key=abcdefghijklmnop"),
        (STALE_MODEL_RE, "Prophet"),
    ],
)
def test_privacy_patterns_reject_unsafe_examples(pattern, value):
    assert pattern.search(value)


def test_document_does_not_embed_private_or_raw_data_paths():
    joined = "\n".join(path.read_text(encoding="utf-8") for path in FILES).lower()
    assert "reports/private" not in joined
    assert "data/raw" not in joined
    assert "data\\raw" not in joined
    assert "s3://" not in joined and "gs://" not in joined and "azure://" not in joined
