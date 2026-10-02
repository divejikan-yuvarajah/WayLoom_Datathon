from pathlib import Path

import yaml

from src.common.logging_utils import get_logger


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "configs",
    "data/raw",
    "data/interim",
    "data/processed",
    "docs",
    "docs/architecture",
    "docs/phases",
    "notebooks",
    "src",
    "src/common",
    "src/task1",
    "src/task2a",
    "src/task2b",
    "models",
    "outputs",
    "reports/figures",
    "reports/metrics",
    "reports/checker",
    "tests",
]


def test_required_directories_exist():
    missing = [path for path in REQUIRED_DIRS if not (ROOT / path).is_dir()]
    assert not missing, f"Missing directories: {missing}"


def test_configs_parse():
    for relative_path in ("configs/paths.yaml", "configs/model_config.yaml"):
        with (ROOT / relative_path).open(encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        assert isinstance(config, dict)


def test_random_seed_is_frozen():
    with (ROOT / "configs/model_config.yaml").open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    assert config["project"]["random_seed"] == 42


def test_logger_is_local_and_does_not_duplicate_handlers():
    logger = get_logger("setup-test")
    handler_count = len(logger.handlers)
    same_logger = get_logger("setup-test")

    assert same_logger is logger
    assert len(logger.handlers) == handler_count
    assert logger.propagate is False
    assert all(
        getattr(handler, "_wayloom_console_handler", False)
        for handler in logger.handlers
    )
