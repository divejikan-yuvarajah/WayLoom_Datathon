"""Read-only integrity checks for the DevHawkz submission copy.

These checks inspect only allowlisted package files and hashes, never private inputs.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "submission" / "DevHawkz_Datathon"
ZIP = ROOT / "submission" / "DevHawkz_Datathon.zip"
NOTEBOOK = "DevHawkz_FinalNotebook.ipynb"
CSV_HASHES = {
    "submission_task1.csv": "9e0faa83a8dd1401ebaf72f1b1602dc560049d4a0cfba19676dbb69bf0de7918",
    "submission_task2a.csv": "142842eef5e4a2e7a6db450c19f4062e4a6eb065481aa21720b59556f9edd55d",
    "submission_task2b.csv": "15f98c8abc434811bc8d6db6ce64c4a746d0acd401f9147d7b15c0958d62b431",
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest() -> dict[str, tuple[str, int]]:
    lines = (STAGE / "SUBMISSION_MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# SHA256  SIZE_BYTES  RELATIVE_PATH"
    entries: dict[str, tuple[str, int]] = {}
    for line in lines[1:]:
        match = re.fullmatch(r"([0-9a-f]{64})\s+(\d+)\s+(.+)", line)
        assert match, "Malformed manifest line"
        digest, size, name = match.groups()
        assert name not in entries, "Duplicate manifest member"
        entries[name] = (digest, int(size))
    return entries


def test_team_project_and_active_package_identity() -> None:
    readme = (STAGE / "README.md").read_text(encoding="utf-8")
    handoff = (ROOT / "submission" / "FINAL_SUBMISSION_HANDOFF.md").read_text(encoding="utf-8")
    config = (STAGE / "configs" / "final_notebook.yaml").read_text(encoding="utf-8")
    validator = (STAGE / "scripts" / "validate_final_notebook.py").read_text(encoding="utf-8")
    assert "Official team: **DevHawkz**" in readme
    assert "Project: **WayLoom**" in readme
    assert "OFFICIAL TEAM NAME: DevHawkz" in handoff
    assert "PROJECT NAME: WayLoom" in handoff
    assert "DevHawkz_Datathon.zip" in handoff
    assert "notebook_filename: DevHawkz_FinalNotebook.ipynb" in config
    assert 'EXPECTED_NOTEBOOK = ROOT / "DevHawkz_FinalNotebook.ipynb"' in validator
    assert "WayLoom_Datathon.zip` and staging directory are **superseded drafts**" in handoff
    for active in (readme, config, validator):
        assert "WayLoom_Datathon.zip" not in active
        assert "--source TeamName_FinalNotebook.ipynb" not in active


def test_frozen_notebook_is_byte_identical_and_cleared() -> None:
    staged = (STAGE / NOTEBOOK).read_bytes()
    assert staged == (ROOT / "TeamName_FinalNotebook.ipynb").read_bytes()
    notebook = json.loads(staged)
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert code_cells
    assert all(not cell.get("outputs") and cell.get("execution_count") is None for cell in code_cells)
    final_source = "".join(code_cells[-1]["source"])
    assert 'loader_callable = getattr(loader_module, phase32_config["loader_callable"])' in final_source
    assert "write_official_outputs=False" in final_source
    assert "loader_callable: run_saved_artifact_inference_demo" in (
        STAGE / "configs" / "final_notebook.yaml"
    ).read_text(encoding="utf-8")


def test_official_csv_copies_and_approved_disclosure() -> None:
    for name, expected in CSV_HASHES.items():
        for file in (ROOT / "outputs" / name, STAGE / name, STAGE / "outputs" / name):
            assert _digest(file.read_bytes()) == expected
    expected_disclosure = "715c2dca328a6792adffad5073633fcd7e362272578dbed788a8179418b6d4d3"
    assert _digest((STAGE / "docs" / "AI_USE_DISCLOSURE.md").read_bytes()) == expected_disclosure
    assert _digest((ROOT / "docs" / "AI_USE_DISCLOSURE.md").read_bytes()) == expected_disclosure


def test_manifest_covers_staged_files_and_exact_bytes() -> None:
    entries = _manifest()
    actual = {
        file.relative_to(STAGE).as_posix()
        for file in STAGE.rglob("*")
        if file.is_file() and file.name != "SUBMISSION_MANIFEST.sha256"
    }
    assert entries.keys() == actual
    for name, (digest, size) in entries.items():
        data = (STAGE / name).read_bytes()
        assert len(data) == size
        assert _digest(data) == digest


def test_zip_is_single_root_allowlisted_and_matches_manifest() -> None:
    entries = _manifest()
    with zipfile.ZipFile(ZIP) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        assert len(names) == len(set(names))
        expected = {f"DevHawkz_Datathon/{name}" for name in entries}
        expected.add("DevHawkz_Datathon/SUBMISSION_MANIFEST.sha256")
        assert set(names) == expected
        for info in infos:
            name = info.filename
            parts = PurePosixPath(name).parts
            assert parts[0] == "DevHawkz_Datathon"
            assert len(parts) > 1 and all(part not in ("", ".", "..") for part in parts)
            assert "\\" not in name and not name.startswith("/")
            assert not stat.S_ISLNK(info.external_attr >> 16)
            assert not name.lower().endswith((".zip", ".7z", ".rar", ".env", ".pyc"))
            assert not any(part.lower() in ("private", "__pycache__", ".git", ".venv") for part in parts)
            data = archive.read(info)
            staged = (STAGE / PurePosixPath(*parts[1:])).read_bytes()
            assert data == staged
            if name.endswith("/SUBMISSION_MANIFEST.sha256"):
                continue
            digest, size = entries["/".join(parts[1:])]
            assert len(data) == size and _digest(data) == digest
