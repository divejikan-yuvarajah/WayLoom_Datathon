from pathlib import Path

import nbformat

from scripts.build_final_notebook import build_notebook
from scripts.validate_final_notebook import FINAL_TAGS, TASK_TAGS, _all_tags


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"


def _load():
    return nbformat.read(NOTEBOOK, as_version=4)


def test_notebook_is_v4_with_python3_kernel_and_complete_task_mapping():
    notebook = _load()
    assert notebook.nbformat == 4
    assert notebook.metadata.kernelspec.name == "python3"
    assert TASK_TAGS.issubset(_all_tags(notebook))


def test_final_inference_cell_is_last_and_has_required_tags():
    notebook = _load()
    assert notebook.cells[-1].cell_type == "code"
    assert FINAL_TAGS.issubset(set(notebook.cells[-1].metadata.tags))
    assert notebook.cells[-2].cell_type == "markdown"
    assert "# Final Saved-Model Inference Demonstration" in notebook.cells[-2].source


def test_source_notebook_is_clean_and_builder_is_deterministic():
    notebook = _load()
    expected = build_notebook()
    assert notebook == expected
    for cell in notebook.cells:
        if cell.cell_type == "code":
            assert cell.source.strip()
            assert cell.execution_count is None
            assert cell.outputs == []

