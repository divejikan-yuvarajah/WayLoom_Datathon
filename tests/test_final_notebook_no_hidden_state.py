from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "TeamName_FinalNotebook.ipynb"


def test_final_cell_resolves_every_external_dependency_it_uses():
    source = nbformat.read(NOTEBOOK, as_version=4).cells[-1].source
    for token in (
        "from pathlib import Path",
        "import importlib",
        "import yaml",
        "_phase31_root(Path.cwd())",
        'phase31_root / "configs/final_notebook.yaml"',
        "artifact_registry",
        "loader_callable(",
    ):
        assert token in source


def test_final_cell_does_not_depend_on_variables_created_by_prior_cells():
    source = nbformat.read(NOTEBOOK, as_version=4).cells[-1].source
    for prior_state in (
        "task1_service_replay",
        "task1_late_replay",
        "task2a_all_predictions",
        "weekly_panel",
        "deliveries_train",
        "task1_test_inputs",
        "%run",
        "get_ipython",
    ):
        assert prior_state not in source
