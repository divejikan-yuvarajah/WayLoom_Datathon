"""Static and manual-review safeguards for noncausal model explanations."""

from __future__ import annotations

import re
from typing import Mapping


NONCAUSAL_DISCLAIMER_MARKERS = (
    "model associations",
    "not causal effects",
)

HIGH_RISK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("causes", re.compile(r"\bcauses?\b", re.IGNORECASE)),
    ("caused_by", re.compile(r"\bcaused\s+by\b", re.IGNORECASE)),
    ("guarantees", re.compile(r"\bguarantees?\b", re.IGNORECASE)),
    ("will_reduce", re.compile(r"\bwill\s+reduce\b", re.IGNORECASE)),
    ("will_increase", re.compile(r"\bwill\s+increase\b", re.IGNORECASE)),
    ("the_reason_for", re.compile(r"\bthe\s+reason\s+for\b", re.IGNORECASE)),
    ("results_in", re.compile(r"\bresults?\s+in\b", re.IGNORECASE)),
)


class CausalLanguageError(ValueError):
    """Raised when a narrative overstates predictive evidence."""


def find_high_risk_phrases(text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line_number, line in enumerate(str(text).splitlines(), start=1):
        for label, pattern in HIGH_RISK_PATTERNS:
            for match in pattern.finditer(line):
                findings.append({
                    "rule": label,
                    "line": line_number,
                    "matched_phrase": match.group(0),
                })
    return findings


def has_noncausal_disclaimer(text: str) -> bool:
    normalized = " ".join(str(text).lower().split())
    return all(marker in normalized for marker in NONCAUSAL_DISCLAIMER_MARKERS)


def audit_causal_language(documents: Mapping[str, str], *, require_disclaimer: bool = True) -> dict[str, object]:
    violations: list[dict[str, object]] = []
    missing_disclaimer: list[str] = []
    for name, text in sorted(documents.items()):
        for finding in find_high_risk_phrases(text):
            violations.append({"document": name, **finding})
        if require_disclaimer and not has_noncausal_disclaimer(text):
            missing_disclaimer.append(name)
    status = "PASS" if not violations and not missing_disclaimer else "FAIL"
    return {
        "status": status,
        "high_risk_phrase_count": len(violations),
        "violations": violations,
        "missing_disclaimer_documents": missing_disclaimer,
        "driver_definition": "driver means model driver or predictive association, not causal driver",
        "manual_review_checklist": {
            "claims_describe_model_behavior_only": status == "PASS",
            "direction_claims_require_distribution_evidence": True,
            "correlated_feature_caution_present": True,
            "actionability_not_inferred_from_rank": True,
        },
    }


def require_causal_language_pass(documents: Mapping[str, str], *, require_disclaimer: bool = True) -> dict[str, object]:
    result = audit_causal_language(documents, require_disclaimer=require_disclaimer)
    if result["status"] != "PASS":
        raise CausalLanguageError(
            "Explainability narrative contains unsupported causal language or lacks the required disclaimer."
        )
    return result
