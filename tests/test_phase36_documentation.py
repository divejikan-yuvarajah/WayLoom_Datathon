"""Deterministic, synthetic-only checks for Phase 36 documentation."""

from __future__ import annotations

import ntpath
import re
import shlex
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
WALKTHROUGH = ROOT / "docs" / "DATATHON_JUDGE_WALKTHROUGH.md"
TRACEABILITY = ROOT / "docs" / "PHASE36_DOCUMENTATION_TRACEABILITY.md"
MASTER = ROOT / "MD Files" / "WAYLOOM_DATATHON_MASTER_PLAN.md"
SUBMISSION_CONFIG = ROOT / "configs" / "final_submission_validation.yaml"
NOTEBOOK_CONFIG = ROOT / "configs" / "final_notebook.yaml"
APPROVED_NOTEBOOK_OUTPUT = (
    "reports/private/phase31_final_notebook/teamname_finalnotebook.executed.ipynb"
)

EXPECTED_TASKS = {
    "DT-456": "Write Datathon README",
    "DT-457": "Explain project objectives",
    "DT-458": "Explain folder structure",
    "DT-459": "Explain environment setup",
    "DT-460": "Explain how to run notebook",
    "DT-461": "Explain model files",
    "DT-462": "Explain how outputs are generated",
    "DT-463": "Document random seed/reproducibility",
}

EXPECTED_SCHEMAS = {
    "submission_task1.csv": (
        "delivery_id",
        "pred_service_min",
        "pred_late_prob",
    ),
    "submission_task2a.csv": (
        "row_id",
        "pred_total_volume_m3",
        "pred_chilled_volume_m3",
    ),
    "submission_task2b.csv": (
        "scenario",
        "order_ref",
        "outlet_id",
        "decision",
        "vehicle_id",
        "trip_id",
    ),
}

REQUIRED_HEADINGS = (
    "Project objectives",
    "Implemented approach",
    "Repository structure",
    "Environment setup",
    "Running and validating the notebook",
    "Model files and secured loading",
    "How outputs are generated",
    "Reproducibility",
    "Safe verification",
    "Deliverables and current status",
    "Privacy, limitations, and review boundaries",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _local_link_targets(text: str, source: Path) -> list[Path]:
    targets: list[Path] = []
    for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        value = raw.strip().split(maxsplit=1)[0].strip("<>")
        if not value or value.startswith(("#", "http://", "https://", "mailto:")):
            continue
        relative = unquote(value.split("#", 1)[0])
        targets.append((source.parent / Path(relative)).resolve())
    return targets


def _validate_local_links(text: str, source: Path) -> None:
    missing = [path for path in _local_link_targets(text, source) if not path.exists()]
    if missing:
        names = ", ".join(path.name for path in missing)
        raise ValueError(f"Broken local documentation link(s): {names}")


def _validate_documented_scripts(text: str) -> None:
    normalized = text.replace("\\", "/")
    scripts = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", normalized))
    missing = [value for value in sorted(scripts) if not (ROOT / value).is_file()]
    if missing:
        raise ValueError(f"Unknown documented script(s): {missing}")


def _validate_notebook_run_command(text: str, config: dict) -> None:
    lines = [
        line.strip()
        for line in text.splitlines()
        if "scripts\\execute_final_notebook.py" in line
        or "scripts/execute_final_notebook.py" in line
    ]
    if len(lines) != 1:
        raise ValueError("README must contain exactly one notebook execution command.")
    command = lines[0]
    try:
        tokens = [token.strip('"') for token in shlex.split(command, posix=False)]
    except ValueError as exc:
        raise ValueError("Documented notebook command is malformed.") from exc

    def argument(flag: str) -> str:
        positions = [index for index, token in enumerate(tokens) if token == flag]
        if len(positions) != 1:
            raise ValueError(f"Documented notebook command requires exactly one {flag} argument.")
        index = positions[0]
        if index + 1 >= len(tokens) or tokens[index + 1].startswith("--"):
            raise ValueError(f"Documented notebook command has a missing or malformed {flag} value.")
        return tokens[index + 1]

    documented_input = argument("--input")
    documented_output = argument("--output")
    documented_config = argument("--config")
    documented_mode = argument("--mode")
    if PureWindowsPath(documented_input) != PureWindowsPath("TeamName_FinalNotebook.ipynb"):
        raise ValueError("Documented notebook input does not match the executor contract.")
    if PureWindowsPath(documented_config) != PureWindowsPath("configs/final_notebook.yaml"):
        raise ValueError("Documented notebook config does not match the executor contract.")
    if documented_mode != "run-all":
        raise ValueError("Documented notebook mode must be run-all.")

    # Model Windows Path.resolve()/relative_to() semantics without relying on
    # the host OS. Normalization collapses '.' and '..'; relative_to rejects
    # traversal and similar-prefix sibling directories.
    synthetic_root = PureWindowsPath("C:/WayLoom_Datathon")

    def resolved(value: str) -> PureWindowsPath:
        path = PureWindowsPath(value)
        joined = path if path.is_absolute() else synthetic_root / path
        return PureWindowsPath(ntpath.normpath(str(joined)))

    configured_root = resolved(str(config["execution"]["private_output_dir"]))
    output = resolved(documented_output)
    try:
        relative = output.relative_to(configured_root)
    except ValueError as exc:
        raise ValueError(
            "Documented notebook output is outside the configured private directory."
        ) from exc
    if not relative.parts or output.suffixes[-2:] != [".executed", ".ipynb"]:
        raise ValueError("Documented notebook output must be a disposable executed copy.")


def _validate_schemas(text: str) -> None:
    for filename, columns in EXPECTED_SCHEMAS.items():
        position = text.find(f"`{filename}`")
        if position < 0:
            raise ValueError(f"Missing official filename: {filename}")
        section = text[position : position + 500]
        cursor = -1
        for column in columns:
            cursor = section.find(f"`{column}`", cursor + 1)
            if cursor < 0:
                raise ValueError(f"Missing or misordered {filename} column: {column}")


def _validate_status_honesty(text: str) -> None:
    required = (
        "Phase 35 AI-use disclosure also remains open",
        "awaiting a fresh independent review",
        "Pending Phase 37",
        "Pending Phase 38",
        "Pending Phases 40–42",
        "does not close Phase 35",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ValueError(f"Missing pending-status qualification(s): {missing}")
    if re.search(r"(?:youtube\.com|youtu\.be)/", text, flags=re.IGNORECASE):
        raise ValueError("A demo-video URL cannot be documented before Phase 38 evidence exists.")
    forbidden_claims = (
        "Phase 36 formally closed",
        "Phase 35 formally closed",
        "organizer blanket clearance",
    )
    if any(claim.lower() in text.lower() for claim in forbidden_claims):
        raise ValueError("Documentation overstates a pending phase or organizer response.")


def _validate_public_safety(text: str) -> None:
    forbidden = (
        "c:\\users\\",
        "c:/users/",
        "reports/private/",
        "reports\\private\\",
        "data/raw/",
        "data\\raw\\",
    )
    lowered = text.lower().replace("\\", "/")
    # The executor contract requires this exact ignored location. Allow the path
    # itself, but continue rejecting any other private-report reference.
    lowered = lowered.replace(APPROVED_NOTEBOOK_OUTPUT, "<approved-notebook-output>")
    hits = [token for token in forbidden if token in lowered]
    if re.search(r"(?<![a-z0-9])sk-[a-z0-9_-]{8,}", lowered):
        hits.append("secret-like API token")
    private_content_markers = (
        '"output_type":',
        '"execution_count":',
        "-----begin private key-----",
        "-----begin openssh private key-----",
    )
    hits.extend(marker for marker in private_content_markers if marker in lowered)
    if hits:
        raise ValueError(f"Private path or secret-like token in documentation: {hits}")


def _traceability_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    pattern = re.compile(r"^\| (DT-\d{3}) \| ([^|]+) \|", re.MULTILINE)
    for task, title in pattern.findall(text):
        rows.append((task, title.strip()))
    return rows


def _validate_traceability(text: str) -> None:
    rows = _traceability_rows(text)
    tasks = [task for task, _ in rows]
    if tasks != list(EXPECTED_TASKS):
        raise ValueError("Traceability must contain exactly DT-456 through DT-463 once and in order.")
    if dict(rows) != EXPECTED_TASKS:
        raise ValueError("Traceability titles do not match the local master plan.")


def test_readme_is_coherent_and_covers_all_phase36_sections() -> None:
    text = _text(README)
    assert len(re.findall(r"^# ", text, flags=re.MULTILINE)) == 1
    headings = set(re.findall(r"^## (.+)$", text, flags=re.MULTILINE))
    assert set(REQUIRED_HEADINGS).issubset(headings)
    assert "Task 1" in text and "Task 2A" in text and "Task 2B" in text


def test_all_local_markdown_links_resolve() -> None:
    for path in (README, WALKTHROUGH, TRACEABILITY):
        _validate_local_links(_text(path), path)


def test_broken_relative_link_is_rejected(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.md"
    candidate.write_text("[missing](docs/not-present.md)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Broken local documentation link"):
        _validate_local_links(_text(candidate), candidate)


def test_official_filenames_and_columns_match_phase33_config() -> None:
    text = _text(README)
    _validate_schemas(text)
    config = yaml.safe_load(_text(SUBMISSION_CONFIG))
    assert tuple(config["task1"]["expected_columns"]) == EXPECTED_SCHEMAS["submission_task1.csv"]
    assert tuple(config["task2a"]["expected_columns"]) == EXPECTED_SCHEMAS["submission_task2a.csv"]
    assert tuple(config["task2b"]["expected_columns"]) == EXPECTED_SCHEMAS["submission_task2b.csv"]


def test_incorrect_official_column_is_rejected() -> None:
    mutated = _text(README).replace("`pred_chilled_volume_m3`", "`pred_cold_volume_m3`", 1)
    with pytest.raises(ValueError, match="pred_chilled_volume_m3"):
        _validate_schemas(mutated)


def test_documented_cli_entrypoints_and_manifests_exist() -> None:
    combined = _text(README) + _text(WALKTHROUGH)
    _validate_documented_scripts(combined)
    required = (
        ROOT / "requirements.txt",
        ROOT / "requirements-lock.txt",
        ROOT / "configs" / "final_notebook.yaml",
        ROOT / "models" / "artifact_registry.json",
    )
    assert all(path.is_file() for path in required)


def test_documented_notebook_command_uses_configured_private_output() -> None:
    config = yaml.safe_load(_text(NOTEBOOK_CONFIG))
    _validate_notebook_run_command(_text(README), config)


def test_notebook_command_outside_private_output_is_rejected() -> None:
    config = yaml.safe_load(_text(NOTEBOOK_CONFIG))
    mutated = _text(README).replace(
        r"reports\private\phase31_final_notebook\TeamName_FinalNotebook.executed.ipynb",
        r"tmp\TeamName_FinalNotebook.executed.ipynb",
        1,
    )
    with pytest.raises(ValueError, match="outside the configured private directory"):
        _validate_notebook_run_command(mutated, config)


@pytest.mark.parametrize(
    "bad_output",
    (
        r"outputs\TeamName_FinalNotebook.executed.ipynb",
        r"reports\private\phase31_final_notebook\..\escaped\TeamName_FinalNotebook.executed.ipynb",
        r"reports\private\phase31_final_notebook_backup\TeamName_FinalNotebook.executed.ipynb",
    ),
)
def test_notebook_command_rejects_outside_traversal_and_prefix_sibling(
    bad_output: str,
) -> None:
    config = yaml.safe_load(_text(NOTEBOOK_CONFIG))
    mutated = _text(README).replace(
        r"reports\private\phase31_final_notebook\TeamName_FinalNotebook.executed.ipynb",
        bad_output,
        1,
    )
    with pytest.raises(ValueError, match="outside the configured private directory"):
        _validate_notebook_run_command(mutated, config)


@pytest.mark.parametrize(
    "replacement",
    (
        "",
        "--output",
        "--output --config",
    ),
)
def test_notebook_command_rejects_missing_or_malformed_output(replacement: str) -> None:
    config = yaml.safe_load(_text(NOTEBOOK_CONFIG))
    command_part = (
        r"--output reports\private\phase31_final_notebook\TeamName_FinalNotebook.executed.ipynb"
    )
    mutated = _text(README).replace(command_part, replacement, 1)
    with pytest.raises(ValueError, match="--output|notebook execution command"):
        _validate_notebook_run_command(mutated, config)


def test_unknown_documented_script_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown documented script"):
        _validate_documented_scripts("run scripts\\does_not_exist.py now")


def test_master_inventory_and_traceability_are_exact_and_open() -> None:
    master = _text(MASTER)
    phase = master.split("### Phase 36 — README / project documentation", 1)[1].split(
        "### Phase 37 — Results summary and competition evidence", 1
    )[0]
    for task, title in EXPECTED_TASKS.items():
        assert f"| [ ] | **{task}** | [E] | P1 | Stable repository and outputs | {title} |" in phase
    assert "**Phase complete:** [ ]" in phase
    assert "**READY FOR NEXT PHASE:** NO" in phase
    _validate_traceability(_text(TRACEABILITY))


def test_duplicate_or_mistitled_traceability_is_rejected() -> None:
    original = _text(TRACEABILITY)
    duplicate = original.replace("| DT-463 |", "| DT-462 |", 1)
    with pytest.raises(ValueError, match="exactly DT-456 through DT-463"):
        _validate_traceability(duplicate)
    mistitled = original.replace("Write Datathon README", "Write a different guide", 1)
    with pytest.raises(ValueError, match="titles do not match"):
        _validate_traceability(mistitled)


def test_setup_notebook_models_outputs_and_reproducibility_are_factual() -> None:
    text = _text(README)
    required = (
        "Python 3.13.7",
        "requirements-lock.txt",
        "--mode run-all",
        "7,200-second cell timeout",
        "12 required Task 1 and Task 2A entries",
        "checksum mismatches before deserialization",
        "The project seed is **42**",
        "PYTHONHASHSEED",
        "do not guarantee byte-identical retraining",
        "clean-environment end-to-end reproduction remains a later Phase 39 gate",
    )
    assert all(phrase in text for phrase in required)


def test_task_rules_and_output_generation_are_not_conflated() -> None:
    text = _text(README)
    required = (
        "arrival exactly at closing time is not late",
        "Style/Tech chilled volume is zero",
        "chilled volume cannot exceed total volume",
        "passing the organizer checker establishes feasibility, not optimality",
        "There is no added return leg",
        "at most two trips",
        "270 minutes",
        "480-minute budget",
        "Do not rerun training, inference, optimization, or exporters",
    )
    assert all(phrase in text for phrase in required)


def test_pending_status_and_public_safety_fail_closed() -> None:
    combined = _text(README) + _text(WALKTHROUGH) + _text(TRACEABILITY)
    _validate_status_honesty(_text(README))
    _validate_public_safety(combined)


def test_fabricated_video_or_personal_path_is_rejected() -> None:
    fabricated = _text(README) + "\nDemo: https://youtu.be/example\n"
    with pytest.raises(ValueError, match="demo-video URL"):
        _validate_status_honesty(fabricated)
    with pytest.raises(ValueError, match="Private path"):
        _validate_public_safety(r"Open C:\Users\Example\private-output.csv")
    with pytest.raises(ValueError, match="Private path"):
        _validate_public_safety("Open reports/private/unapproved-evidence.json")


def test_sanctioned_notebook_output_path_is_public_safe_to_document() -> None:
    _validate_public_safety(
        r"--output reports\private\phase31_final_notebook\TeamName_FinalNotebook.executed.ipynb"
    )


@pytest.mark.parametrize(
    "private_content",
    (
        '{"output_type": "execute_result", "execution_count": 1}',
        "-----BEGIN PRIVATE KEY-----",
        "reports/private/phase31_final_notebook/private-output.json",
    ),
)
def test_unexpected_private_content_exposure_is_rejected(private_content: str) -> None:
    with pytest.raises(ValueError, match="Private path"):
        _validate_public_safety(private_content)
