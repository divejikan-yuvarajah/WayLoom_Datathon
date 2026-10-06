from __future__ import annotations

import pytest

from src.task1.causal_language import (
    CausalLanguageError,
    audit_causal_language,
    find_high_risk_phrases,
    require_causal_language_pass,
)
from src.task1.explainability import NONCAUSAL_DISCLAIMER


@pytest.mark.parametrize("phrase", [
    "X causes lateness.",
    "Delay was caused by congestion.",
    "X guarantees faster service.",
    "X will reduce late risk.",
    "X will increase handling time.",
    "X is the reason for the late delivery.",
    "X results in a longer visit.",
])
def test_high_risk_causal_phrases_are_flagged(phrase: str) -> None:
    assert find_high_risk_phrases(phrase)


def test_qualified_predictive_language_and_driver_term_are_allowed() -> None:
    text = (
        "X is associated with higher model risk. X contributed positively to the model score. "
        "X is a model driver, not a proven causal driver.\n\n" + NONCAUSAL_DISCLAIMER
    )
    result = audit_causal_language({"doc": text})
    assert result["status"] == "PASS"
    assert result["high_risk_phrase_count"] == 0


def test_missing_disclaimer_or_risky_claim_fails() -> None:
    with pytest.raises(CausalLanguageError):
        require_causal_language_pass({"doc": "X is associated with risk."})
    with pytest.raises(CausalLanguageError):
        require_causal_language_pass({"doc": "X causes lateness. " + NONCAUSAL_DISCLAIMER})
