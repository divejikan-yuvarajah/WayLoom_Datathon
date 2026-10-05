"""Synthetic Phase 24 integration and evidence-resolution tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.task2b.artifact_integrity import sha256_file
from src.task2b.policy_evidence import (
    PolicyEvidenceError,
    load_phase23_candidate_if_available,
    load_phase23_pass_evidence,
)
from src.task2b.policy_writer import render_task2b_policy, write_policy_atomic
from src.task2b.submission import (
    Task2BSubmissionError,
    build_task2b_submission,
    validate_output_config,
    validate_task2b_submission,
    write_task2b_submission_atomic,
)
from tests.test_task2b_policy_writer import _evidence, _phase23_evidence, _priority_config
from tests.test_task2b_submission import _case


def test_phase23_evidence_resolution_and_candidate_hash_binding(tmp_path: Path):
    root = tmp_path / "phase23"
    run = root / "checker_runs" / "20261006T000000.000000Z"
    run.mkdir(parents=True)
    evidence = _phase23_evidence()
    candidate_dir = root / "checker_workspace"
    candidate_dir.mkdir()
    candidate = candidate_dir / "submission_task2b.csv"
    template, allocation, orders = _case()
    output = build_task2b_submission(template, allocation, orders)
    output.to_csv(candidate, index=False)
    evidence["checker_input_sha256"] = sha256_file(candidate)
    (run / "checker_evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    loaded, evidence_path = load_phase23_pass_evidence(
        root / "checker_evidence.json",
        expected_frozen_allocation_sha256=evidence["frozen_allocation_sha256"],
    )
    loaded_candidate, candidate_path = load_phase23_candidate_if_available(evidence_path, loaded)
    assert candidate_path == candidate.resolve()
    assert loaded_candidate is not None and len(loaded_candidate) == len(output)
    candidate.write_text("changed\n", encoding="utf-8")
    with pytest.raises(PolicyEvidenceError, match="hash"):
        load_phase23_candidate_if_available(evidence_path, loaded)


def test_end_to_end_synthetic_submission_policy_and_readback(tmp_path: Path):
    template, allocation, orders = _case()
    submission = build_task2b_submission(template, allocation, orders)
    output_path = tmp_path / "submission_task2b.csv"
    report = write_task2b_submission_atomic(
        output_path,
        submission,
        template,
        allocation,
        orders,
        source_allocation_sha256="f" * 64,
        known_vehicle_ids=["v1", "v2"],
        phase23_candidate=submission,
    )
    read_back = pd.read_csv(output_path, dtype="string", keep_default_na=False)
    revalidated = validate_task2b_submission(
        read_back, template, allocation, orders,
        known_vehicle_ids=["v1", "v2"], phase23_candidate=submission,
    )
    assert report["submission_task2b_sha256"] == sha256_file(output_path)
    assert revalidated["phase23_checker_candidate_parity"] == "PASS"

    policy, validation = render_task2b_policy(_evidence(), _priority_config())
    policy_path = tmp_path / "task2b_policy.md"
    assert write_policy_atomic(policy_path, policy) == sha256_file(policy_path)
    assert validation["target_met"] and policy_path.read_text(encoding="utf-8") == policy


def test_output_config_is_frozen_and_bad_filename_fails(tmp_path: Path):
    config = yaml.safe_load(open("configs/task2b_output.yaml", encoding="utf-8"))
    validate_output_config(config)
    changed = json.loads(json.dumps(config))
    changed["output"]["exact_columns"] = list(reversed(changed["output"]["exact_columns"]))
    with pytest.raises(Task2BSubmissionError, match="contract changed"):
        validate_output_config(changed)
    template, allocation, orders = _case()
    submission = build_task2b_submission(template, allocation, orders)
    with pytest.raises(Task2BSubmissionError, match="filename"):
        write_task2b_submission_atomic(
            tmp_path / "wrong.csv", submission, template, allocation, orders,
            source_allocation_sha256="a" * 64,
        )
