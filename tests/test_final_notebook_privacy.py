from pathlib import Path

import nbformat
import pytest

from scripts.validate_final_notebook import (
    ABSOLUTE_PATH_RE,
    INSTALL_RE,
    NETWORK_RE,
    PRIVATE_ID_RE,
    SECRET_RE,
    _source_text,
)


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"


def test_public_notebook_contains_no_private_outputs_or_unsafe_source():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    source = _source_text(notebook)
    for pattern in (ABSOLUTE_PATH_RE, PRIVATE_ID_RE, SECRET_RE, INSTALL_RE, NETWORK_RE):
        assert pattern.search(source) is None
    assert all(not cell.get("outputs") for cell in notebook.cells if cell.cell_type == "code")


@pytest.mark.parametrize(
    ("pattern", "unsafe"),
    [
        (ABSOLUTE_PATH_RE, "C:\\Users\\person\\private.csv"),
        (PRIVATE_ID_RE, "ORD12345678"),
        (SECRET_RE, "api_key=abcdefghijklmnop"),
        (INSTALL_RE, "!pip install hidden-package"),
        (NETWORK_RE, "requests.get('https://example.invalid')"),
    ],
)
def test_privacy_scanners_reject_representative_unsafe_content(pattern, unsafe):
    assert pattern.search(unsafe)

