from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.build_final_artifacts import ArtifactBuildError, _promote_validated_candidate


ROOT = Path(__file__).resolve().parents[1]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_failed_task2a_candidate_never_mutates_canonical_bundle(tmp_path: Path) -> None:
    candidate = tmp_path / "staging/component.joblib"
    canonical = tmp_path / "canonical/component.joblib"
    registry = tmp_path / "models/artifact_registry.json"
    candidate.parent.mkdir(parents=True)
    canonical.parent.mkdir(parents=True)
    registry.parent.mkdir(parents=True)
    candidate.write_bytes(b"broken-candidate")
    canonical.write_bytes(b"canonical-sentinel")
    registry.write_text('{"status":"canonical"}', encoding="utf-8")
    before = (_hash(canonical), _hash(registry))

    with pytest.raises(ArtifactBuildError, match="validation must pass"):
        _promote_validated_candidate(
            [(candidate, canonical)],
            registry_payload={"status": "candidate"},
            registry_path=registry,
            candidate_validated=False,
        )

    assert (_hash(canonical), _hash(registry)) == before


def test_different_existing_canonical_bundle_requires_explicit_refinalization(tmp_path: Path) -> None:
    candidate = tmp_path / "staging/component.joblib"
    canonical = tmp_path / "canonical/component.joblib"
    registry = tmp_path / "models/artifact_registry.json"
    candidate.parent.mkdir(parents=True)
    canonical.parent.mkdir(parents=True)
    registry.parent.mkdir(parents=True)
    candidate.write_bytes(b"candidate")
    canonical.write_bytes(b"frozen")
    registry.write_text('{"status":"canonical"}', encoding="utf-8")
    before = (_hash(canonical), _hash(registry))

    with pytest.raises(ArtifactBuildError, match="controlled refinalization"):
        _promote_validated_candidate(
            [(candidate, canonical)],
            registry_payload={"status": "candidate"},
            registry_path=registry,
            candidate_validated=True,
        )

    assert (_hash(canonical), _hash(registry)) == before


def test_task2a_atomic_bundle_promotion_publishes_registry_last(tmp_path: Path) -> None:
    sources = [tmp_path / f"staging/file-{index}.bin" for index in range(2)]
    destinations = [tmp_path / f"canonical/file-{index}.bin" for index in range(2)]
    for index, source in enumerate(sources):
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(f"candidate-{index}".encode())
    registry = tmp_path / "models/artifact_registry.json"
    payload = {"status": "validated", "artifacts": 2}

    _promote_validated_candidate(
        list(zip(sources, destinations)),
        registry_payload=payload,
        registry_path=registry,
        candidate_validated=True,
    )

    assert [path.read_bytes() for path in destinations] == [b"candidate-0", b"candidate-1"]
    assert json.loads(registry.read_text(encoding="utf-8")) == payload
    assert not any(path.exists() for path in sources)


def test_partial_promotion_failure_rolls_back_canonical_and_registry(
    tmp_path: Path, monkeypatch
) -> None:
    sources = [tmp_path / f"staging/file-{index}.bin" for index in range(2)]
    destinations = [tmp_path / f"canonical/file-{index}.bin" for index in range(2)]
    for index, source in enumerate(sources):
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(f"candidate-{index}".encode())
    registry = tmp_path / "models/artifact_registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text('{"status":"original"}', encoding="utf-8")
    original_registry = registry.read_bytes()

    import scripts.build_final_artifacts as builder

    real_replace = builder.os.replace

    def fail_second_move(source: Path, destination: Path) -> None:
        if Path(destination) == destinations[1]:
            raise OSError("synthetic promotion failure")
        real_replace(source, destination)

    monkeypatch.setattr(builder.os, "replace", fail_second_move)
    with pytest.raises(OSError, match="synthetic promotion failure"):
        _promote_validated_candidate(
            list(zip(sources, destinations)),
            registry_payload={"status": "candidate"},
            registry_path=registry,
            candidate_validated=True,
        )

    assert not any(path.exists() for path in destinations)
    assert registry.read_bytes() == original_registry


def test_task2a_candidate_is_reloaded_and_compared_before_promotion() -> None:
    source = (ROOT / "scripts/build_final_artifacts.py").read_text(encoding="utf-8")
    load_index = source.index("loaded_candidate = load_phase31_artifact_set")
    smoke_index = source.index("run_loaded_artifact_synthetic_smoke(loaded_candidate)")
    parity_index = source.index('reloaded["predictions"]')
    promotion_index = source.index("_promote_validated_candidate(", parity_index)
    assert load_index < smoke_index < parity_index < promotion_index
