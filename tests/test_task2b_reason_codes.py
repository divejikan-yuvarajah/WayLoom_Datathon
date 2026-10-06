import pytest
import yaml

from src.task2b.priority import DEFERRAL_REASON_CODES
from src.task2b.reason_codes import (
    POLICY_TRADEOFF,
    REASON_TAXONOMY,
    ReasonCodeError,
    validate_reason_assignment,
    validate_taxonomy,
)


def test_taxonomy_exactly_preserves_phase21_codes_and_evidence_metadata():
    validate_taxonomy()
    assert tuple(REASON_TAXONOMY) == DEFERRAL_REASON_CODES
    assert len(REASON_TAXONOMY) == len(set(REASON_TAXONOMY))
    assert all(item.definition and item.required_evidence and item.allowed_wording
               and item.forbidden_overclaim for item in REASON_TAXONOMY.values())


def test_reason_class_compatibility_and_unknown_codes_fail_closed():
    assert validate_reason_assignment(
        POLICY_TRADEOFF, "LOWER_POLICY_PRIORITY", ["CAPACITY_COMPETITION"]
    )
    with pytest.raises(ReasonCodeError, match="Unknown reason code"):
        validate_reason_assignment(POLICY_TRADEOFF, "RENAMED_REASON")
    with pytest.raises(ReasonCodeError, match="incompatible"):
        validate_reason_assignment(POLICY_TRADEOFF, "HARD_NO_COMPATIBLE_VEHICLE")


def test_phase26_config_keeps_diagnostic_safety_controls_enabled():
    config = yaml.safe_load(open("configs/task2b_deferral_reasoner.yaml", encoding="utf-8"))
    assert config["counterfactual"]["force_target_served"] is True
    assert config["counterfactual"]["require_optimal_policy_stages"] is True
    assert config["counterfactual"]["num_search_workers"] == 1
    assert config["minimal_change"]["require_optimal"] is True
    assert config["direct_insertion"]["fail_if_direct_insert_possible"] is True
    assert config["classification"]["allow_unresolved"] is False
    assert config["demo"]["max_examples"] == 2
