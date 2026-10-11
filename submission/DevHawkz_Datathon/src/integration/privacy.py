"""Central fail-closed privacy controls for Phase 28."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTECTED_RELATIVE_PATHS = (
    Path("data/raw"),
    Path("data/interim"),
    Path("reports/private"),
    Path("outputs/submission_task1.csv"),
    Path("outputs/submission_task2a.csv"),
    Path("outputs/submission_task2b.csv"),
)
PROTECTED_TEXT_MARKERS = (
    "data/raw", "data\\raw", "data/interim", "data\\interim",
    "reports/private", "reports\\private", "submission_task1.csv",
    "submission_task2a.csv", "submission_task2b.csv", "models/task1_",
)
ROW_LEVEL_FIELDS = {
    "order_ref", "outlet_id", "vehicle_id", "trip_id", "delivery_id", "row_id",
    "actual_depart_time", "actual_travel_duration_min", "arrival_time", "leave_outlet_time",
}
ALLOWED_EXPORT_ROOT_FILES = {
    "README.md", "contract_version.json", "openapi.json",
    "PRIVACY_AND_DATA_BOUNDARY.md", "manifest.json",
}
OFFICIAL_ID_COLUMNS = (
    "delivery_id",
    "row_id",
    "order_ref",
    "outlet_id",
    "vehicle_id",
    "scenario",
)


class PrivacyError(ValueError):
    """A public operation crossed the Phase 28 privacy boundary."""


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalized_path(path: str | Path, *, base: Path = PROJECT_ROOT) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve(strict=False)


def assert_not_protected_path(path: str | Path, *, base: Path = PROJECT_ROOT) -> Path:
    candidate = normalized_path(path, base=base)
    for relative in PROTECTED_RELATIVE_PATHS:
        protected = (PROJECT_ROOT / relative).resolve(strict=False)
        if candidate == protected or _within(candidate, protected):
            raise PrivacyError("Protected resource access is blocked.")
    return candidate


def assert_safe_export_root(path: str | Path, *, project_root: Path = PROJECT_ROOT) -> Path:
    root = normalized_path(path, base=project_root)
    allowed_parent = (project_root / "dist").resolve(strict=False)
    if root.name != "integration_contract" or root.parent != allowed_parent:
        raise PrivacyError("Contract export must target the configured integration package directory.")
    assert_not_protected_path(root, base=project_root)
    return root


def assert_safe_export_member(root: Path, member: Path) -> None:
    resolved_root = root.resolve(strict=False)
    resolved_member = member.resolve(strict=False)
    if not _within(resolved_member, resolved_root):
        raise PrivacyError("Contract package member escapes the export directory.")
    relative = resolved_member.relative_to(resolved_root)
    if any(part.startswith(".") for part in relative.parts):
        raise PrivacyError("Hidden package members are forbidden.")
    if len(relative.parts) == 1:
        if relative.as_posix() not in ALLOWED_EXPORT_ROOT_FILES:
            raise PrivacyError("Unexpected root-level contract file.")
    elif relative.parts[0] not in {"schemas", "examples"}:
        raise PrivacyError("Unexpected contract package directory.")
    if member.is_symlink():
        raise PrivacyError("Symlinks are forbidden in the shareable package.")


def assert_public_text(value: str) -> None:
    lowered = value.lower().replace("\\", "/")
    if any(marker.lower().replace("\\", "/") in lowered for marker in PROTECTED_TEXT_MARKERS):
        raise PrivacyError("Protected path marker found in public content.")
    if re.search(r"[a-zA-Z]:[/\\](?:Users|Windows|Program Files)[/\\]", value):
        raise PrivacyError("Absolute local path found in public content.")
    if re.search(r"/(?:home|Users|var|tmp)/[^\s\"']+", value):
        raise PrivacyError("Absolute local path found in public content.")


def assert_public_payload(payload: Any) -> None:
    if isinstance(payload, dict):
        forbidden = ROW_LEVEL_FIELDS.intersection(payload)
        if forbidden:
            raise PrivacyError("Row-level field found in public payload.")
        for key, value in payload.items():
            assert_public_text(str(key))
            assert_public_payload(value)
    elif isinstance(payload, list):
        for value in payload:
            assert_public_payload(value)
    elif isinstance(payload, str):
        assert_public_text(payload)


def validate_synthetic_identifier(value: str) -> bool:
    return bool(re.fullmatch(r"(?:DEMO_(?:DELIVERY|FORECAST|SCENARIO)_[0-9]{2,3}|DEFERRAL_EXAMPLE_[A-Z])", value))


def synthetic_overlap_count(synthetic_ids: set[str], official_ids: set[str]) -> int:
    """Return a count only; never return or log the intersecting identifiers."""
    return len(synthetic_ids.intersection(official_ids))


def collect_synthetic_identifiers(payloads: Iterable[Any]) -> set[str]:
    """Collect only identifiers in the reserved synthetic namespaces."""
    found: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str) and validate_synthetic_identifier(value):
            found.add(value)

    for payload in payloads:
        visit(payload)
    return found


def collision_audit_not_run() -> dict[str, Any]:
    return {
        "status": "NOT_RUN",
        "overlap_count": None,
        "official_id_count_by_category": None,
        "synthetic_id_count": None,
        "overlap_count_by_category": None,
        "reason": "official identifier sets were not supplied",
    }


def audit_identifier_sets(
    synthetic_ids: set[str],
    official_ids_by_category: Mapping[str, set[str]],
) -> dict[str, Any]:
    """Return aggregate counts only; identifier values never leave this function."""
    categories = {
        name: {str(value).strip() for value in values if str(value).strip()}
        for name, values in official_ids_by_category.items()
    }
    overlap_values: set[str] = set()
    overlaps: dict[str, int] = {}
    for name, values in sorted(categories.items()):
        matched = synthetic_ids.intersection(values)
        overlaps[name] = len(matched)
        overlap_values.update(matched)
    total = len(overlap_values)
    return {
        "status": "PASS" if total == 0 else "FAIL",
        "overlap_count": total,
        "official_id_count_by_category": {
            name: len(values) for name, values in sorted(categories.items())
        },
        "synthetic_id_count": len(synthetic_ids),
        "overlap_count_by_category": overlaps,
    }


def _load_official_identifier_sets(raw_root: Path, manifest_path: Path) -> dict[str, set[str]]:
    approved_root = (PROJECT_ROOT / "data" / "raw").resolve(strict=False)
    approved_manifest = (PROJECT_ROOT / "configs" / "dataset_manifest.yaml").resolve(strict=False)
    if raw_root.resolve(strict=False) != approved_root or manifest_path.resolve(strict=False) != approved_manifest:
        raise PrivacyError("Private identifier audit inputs are not repository-approved.")
    if not raw_root.is_dir() or not manifest_path.is_file():
        raise PrivacyError("Private identifier audit inputs are unavailable.")
    with manifest_path.open("r", encoding="utf-8") as stream:
        manifest = yaml.safe_load(stream)
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, list):
        raise PrivacyError("Private identifier audit manifest is invalid.")

    official = {column: set() for column in OFFICIAL_ID_COLUMNS}
    for artifact in artifacts:
        if not isinstance(artifact, dict) or artifact.get("format") != "csv":
            continue
        filename = artifact.get("filename")
        if not isinstance(filename, str) or not filename.lower().endswith(".csv"):
            raise PrivacyError("Private identifier audit manifest is invalid.")
        matches = list(raw_root.rglob(filename))
        if len(matches) != 1:
            raise PrivacyError("Private identifier audit artifact discovery failed.")
        with matches[0].open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise PrivacyError("Private identifier audit artifact has no header.")
            selected = set(reader.fieldnames).intersection(OFFICIAL_ID_COLUMNS)
            for row in reader:
                for column in selected:
                    value = str(row.get(column) or "").strip()
                    if value:
                        official[column].add(value)
    return official


def run_private_identifier_collision_audit(
    *,
    raw_root: Path,
    manifest_path: Path,
    synthetic_ids: set[str],
) -> dict[str, Any]:
    """Run the explicit human-local audit and convert errors to a safe FAIL result."""
    try:
        official = _load_official_identifier_sets(raw_root, manifest_path)
        return audit_identifier_sets(synthetic_ids, official)
    except Exception:
        return {
            "status": "FAIL",
            "overlap_count": None,
            "official_id_count_by_category": None,
            "synthetic_id_count": len(synthetic_ids),
            "overlap_count_by_category": None,
            "error_code": "PRIVATE_AUDIT_ERROR",
        }


def safe_error_message(_error: BaseException | str) -> str:
    """Deliberately discard exception text, which may contain local paths or IDs."""
    return "The request could not be completed safely."
