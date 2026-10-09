from __future__ import annotations

import copy
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "docs" / "RESULTS_SUMMARY.md"
INDEX_PATH = ROOT / "docs" / "RESULTS_EVIDENCE_INDEX.md"
MANIFEST_PATH = ROOT / "configs" / "phase37_results_evidence.yaml"
MASTER_PATH = ROOT / "MD Files" / "WAYLOOM_DATATHON_MASTER_PLAN.md"
README_PATH = ROOT / "README.md"

EXPECTED_TASKS = {
    "DT-464": "Produce final Task 1 metrics table",
    "DT-465": "Compare Task 1 baseline vs final model",
    "DT-466": "Produce calibration visualization",
    "DT-467": "Produce Task 1 feature explanation",
    "DT-468": "Produce Task 2A backtesting results",
    "DT-469": "Compare Task 2A baselines/final model",
    "DT-470": "Produce future-demand chart",
    "DT-471": "Produce Task 2B scarcity summary",
    "DT-472": "Produce served/deferred summary",
    "DT-473": "Produce solver/checker evidence",
    "DT-474": "Select only strongest charts for demo",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_manifest() -> dict:
    return yaml.safe_load(_read(MANIFEST_PATH))


def _normalise_number(value: object) -> Decimal:
    try:
        return Decimal(str(value).replace(",", ""))
    except InvalidOperation as exc:
        raise AssertionError(f"not a numeric claim value: {value!r}") from exc


def _parse_claim_rows(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    claims: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    pattern = re.compile(
        r"^\| (N-T2B-\d{3}) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|(?: ([^|]+?) \|)?$",
        re.MULTILINE,
    )
    for claim_id, definition, value, unit, population in pattern.findall(text):
        if claim_id in claims:
            duplicates.append(claim_id)
        claims[claim_id] = {
            "definition": definition.strip(),
            "value": value.strip(),
            "unit": unit.strip(),
            "population": population.strip(),
        }
    return claims, duplicates


def _validate_claim_consistency(data: dict, summary: str, index: str) -> list[str]:
    errors: list[str] = []
    items = data.get("numeric_claims", {}).get("items", [])
    required = {
        "id", "definition", "value", "unit", "population", "source", "evidence_id",
        "extraction_provenance", "audience", "publication_approval",
        "approval_provenance", "selected_for_public_release",
    }
    manifest: dict[str, dict] = {}
    for claim in items:
        missing = required - set(claim)
        if missing:
            errors.append(f"claim {claim.get('id')} missing provenance fields: {sorted(missing)}")
            continue
        claim_id = claim["id"]
        if claim_id in manifest:
            errors.append(f"duplicate claim ID: {claim_id}")
        manifest[claim_id] = claim
        if claim["source"] != "docs/task2b_policy.md" or claim["evidence_id"] != "E-P37-009":
            errors.append(f"claim {claim_id} has incorrect source provenance")
        if not claim["extraction_provenance"]:
            errors.append(f"claim {claim_id} has missing extraction provenance")
        if not claim["approval_provenance"]:
            errors.append(f"claim {claim_id} has missing publication approval provenance")
        if claim["selected_for_public_release"] and claim["publication_approval"] != "APPROVED":
            errors.append(f"unapproved claim selected for public release: {claim_id}")

    summary_claims, summary_duplicates = _parse_claim_rows(summary)
    index_claims, index_duplicates = _parse_claim_rows(index)
    for claim_id in summary_duplicates + index_duplicates:
        errors.append(f"duplicate displayed claim ID: {claim_id}")
    manifest_ids = set(manifest)
    if set(summary_claims) != manifest_ids:
        errors.append("displayed summary claim IDs do not exactly match the manifest")
    if set(index_claims) != manifest_ids:
        errors.append("evidence-index claim IDs do not exactly match the manifest")

    for claim_id in manifest_ids & set(summary_claims) & set(index_claims):
        canonical = manifest[claim_id]
        for location, displayed in (("summary", summary_claims[claim_id]), ("index", index_claims[claim_id])):
            if displayed["definition"].casefold() != str(canonical["definition"]).casefold():
                errors.append(f"{claim_id} definition contradicts {location}")
            if _normalise_number(displayed["value"]) != _normalise_number(canonical["value"]):
                errors.append(f"{claim_id} value contradicts {location}")
            if displayed["unit"] != canonical["unit"]:
                errors.append(f"{claim_id} unit contradicts {location}")
        if index_claims[claim_id]["population"] != canonical["population"]:
            errors.append(f"{claim_id} population contradicts index")
    return errors


def _validate_checker_evidence(index: str) -> list[str]:
    errors: list[str] = []
    e011 = next((line for line in index.splitlines() if line.startswith("| E-P37-011 |")), "")
    if "PHASE_33_COMPETITION_CONTRACT.md" not in e011 or "docs/final_submission_validation.md" in e011:
        errors.append("E-P37-011 does not cite the actual Phase 33 completion record")
    e015 = next((line for line in index.splitlines() if line.startswith("| E-P37-015 |")), "")
    if "WAYLOOM_DATATHON_MASTER_PLAN.md" not in e015 or "Phase 33 closure" not in e015:
        errors.append("E-P37-015 does not cite the independently reviewed Phase 33 closure")
    task = next((line for line in index.splitlines() if line.startswith("| DT-473 |")), "")
    if not all(evidence in task for evidence in ("E-P37-010", "E-P37-011", "E-P37-015")):
        errors.append("DT-473 does not distinguish checker semantics, execution and closure evidence")
    return errors


def _validate_publication_boundary(data: dict, summary: str, index: str, readme: str) -> list[str]:
    """Tracked aggregates are not public assets without claim-specific approval."""
    errors: list[str] = []
    for evidence_id in ("E-P37-006", "E-P37-009"):
        row = next((line for line in index.splitlines() if line.startswith(f"| {evidence_id} |")), "")
        if "`TRACKED_INTERNAL_AGGREGATE`" not in row or "approval pending" not in row:
            errors.append(f"{evidence_id} overstates publication approval")
    claims = data.get("numeric_claims", {})
    if claims.get("source_provenance") != "TRACKED_INTERNAL_AGGREGATE":
        errors.append("claim-register provenance overstates publication approval")
    if any(
        claim.get("publication_approval") != "PENDING" or claim.get("selected_for_public_release") is not False
        for claim in claims.get("items", [])
    ):
        errors.append("a Task 2B claim is released without recorded owner approval")
    if "not approved for public or demo release" not in summary:
        errors.append("results summary lacks its internal-only release boundary")
    if "publication approval, which remains `PENDING`" not in summary:
        errors.append("Task 2B summary overstates publication approval")
    if "](docs/RESULTS_SUMMARY.md)" in readme or "not approved for public or demo release" not in readme:
        errors.append("public README exposes or mislabels the internal results summary")
    if "An unlisted video is accessible to anyone with its link" not in index:
        errors.append("demo release boundary is not explicit")
    return errors


def _validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    tasks = data.get("tasks", [])
    actual = {item.get("id"): item.get("title") for item in tasks}
    if actual != EXPECTED_TASKS:
        errors.append("task inventory does not match the exact Phase 37 master inventory")
    if len(tasks) != 11:
        errors.append("Phase 37 must have exactly 11 task records")
    if data.get("phase_complete") is not False or data.get("ready_for_next_phase") is not False:
        errors.append("Phase 37 must remain open before independent review")
    if data.get("dependency") != "Final metrics/outputs":
        errors.append("wrong Phase 37 dependency")
    for metric in data.get("metrics", []):
        required = {"id", "task", "target", "metric", "formula", "unit", "split", "source", "provenance", "audience", "value"}
        if not required.issubset(metric):
            errors.append(f"metric {metric.get('id')} lacks provenance fields")
            continue
        if metric["value"] != "NOT_AVAILABLE" and metric["provenance"] != "SANITIZED_AGGREGATE_APPROVED":
            errors.append(f"metric {metric['id']} has a value without aggregate approval")
        if metric["value"] != "NOT_AVAILABLE" and metric["audience"] in {"internal_definition_only", "private"}:
            errors.append(f"metric {metric['id']} has a value not approved for the summary audience")
        if metric["unit"] == "percent" and metric["metric"] in {"MAE", "RMSE", "pooled MAE"}:
            errors.append(f"metric {metric['id']} has an incompatible unit")
    privacy = data.get("privacy", {})
    if not privacy or any(privacy.values()):
        errors.append("private rows, identifiers, official values, and notebook outputs must all be disabled")
    if data.get("numeric_claims", {}).get("authority") != "CANONICAL_PHASE37_NUMERICAL_CLAIM_REGISTER":
        errors.append("numeric claim register is not marked authoritative")
    return errors


def _validate_source_paths(data: dict) -> list[str]:
    errors: list[str] = []
    sources = {m.get("source") for m in data.get("metrics", [])}
    sources.update(item.get("source") for item in data.get("numeric_claims", {}).get("items", []))
    sources.update(v.get("source") for v in data.get("visuals", {}).get("selected", []))
    sources.update(v.get("source") for v in data.get("visuals", {}).get("internal_candidates", []))
    for source in sources:
        if not source:
            errors.append("missing source path")
            continue
        candidate = Path(source)
        if candidate.is_absolute() or ".." in candidate.parts or not (ROOT / candidate).is_file():
            errors.append(f"invalid or stale source path: {source}")
    return errors


def _validate_phase_prerequisites(master: str) -> list[str]:
    errors: list[str] = []
    phase35 = master.split("### Phase 35", 1)[1].split("### Phase 36", 1)[0]
    phase36 = master.split("### Phase 36", 1)[1].split("### Phase 37", 1)[0]
    for task_id in range(451, 456):
        if f"| [x] | **DT-{task_id}** |" not in phase35:
            errors.append(f"Phase 35 task DT-{task_id} is not closed")
    for task_id in range(456, 464):
        if f"| [x] | **DT-{task_id}** |" not in phase36:
            errors.append(f"Phase 36 task DT-{task_id} is not closed")
    for name, block in (("Phase 35", phase35), ("Phase 36", phase36)):
        if "**Phase complete:** [x]" not in block or "**READY FOR NEXT PHASE:** YES" not in block:
            errors.append(f"{name} completion/readiness gate is not closed")
    return errors


def _validate_summary(text: str) -> list[str]:
    errors: list[str] = []
    for task_id, title in EXPECTED_TASKS.items():
        if f"## {task_id} — {title}" not in text:
            errors.append(f"missing exact section for {task_id}")
    required_semantics = [
        "early waiting is excluded",
        "Arrival exactly at close is not late",
        "strict late-positive definition",
        "requested-date ISO year/week",
        "Cross-source duplicate order keys must fail closed",
        "Style and Tech chilled demand are structural zeros",
        "no return leg",
        "270-minute Fresh / 480-minute Style+Tech",
        "at most two trips",
        "does not prove a unique global optimum",
        "not a blanket competition-rule exemption",
    ]
    for phrase in required_semantics:
        if phrase not in text:
            errors.append(f"missing semantic safeguard: {phrase}")
    if text.count("**NOT AVAILABLE**") < 8:
        errors.append("unavailable Task 1/2A results are not explicit enough")
    if re.search(r"\b(?:delivery|order|outlet|row)[_-]?(?:id|ref)\s*[=:]\s*[A-Z0-9-]{4,}", text, re.I):
        errors.append("possible real identifier disclosed")
    if "reports/private/" in text or "data/raw/" in text:
        errors.append("private path leaked into results summary")
    if re.search(r"organizer\s+(?:test|withheld).*?(?:accuracy|mae|rmse|log\s*loss|auc)\s*(?:=|:)\s*\d", text, re.I):
        errors.append("unsupported organizer-held-out performance claim")
    return errors


def test_master_phase37_inventory_exact() -> None:
    master = _read(MASTER_PATH)
    block = master[master.index("### Phase 37"):master.index("### Phase 38")]
    rows = re.findall(r"\| \[ \] \| \*\*(DT-\d+)\*\* \| \[E\] \| P1 \| Final metrics/outputs \| ([^|]+) \|", block)
    assert dict((task, title.strip()) for task, title in rows) == EXPECTED_TASKS
    assert "**Phase complete:** [ ]" in block
    assert "**READY FOR NEXT PHASE:** NO" in block


def test_manifest_is_exact_and_phase_stays_open() -> None:
    assert _validate_manifest(_load_manifest()) == []


def test_results_summary_has_exact_task_sections_and_semantics() -> None:
    assert _validate_summary(_read(SUMMARY_PATH)) == []


def test_evidence_index_maps_all_tasks_once() -> None:
    text = _read(INDEX_PATH)
    for task_id, title in EXPECTED_TASKS.items():
        assert text.count(f"| {task_id} | {title} |") == 1
    assert "Formal Phase 37 closure remains pending" in text


def test_task2b_claim_register_matches_summary_and_index_exactly() -> None:
    assert _validate_claim_consistency(
        _load_manifest(), _read(SUMMARY_PATH), _read(INDEX_PATH)
    ) == []


def test_phase33_checker_evidence_uses_actual_completion_and_closure_records() -> None:
    assert _validate_checker_evidence(_read(INDEX_PATH)) == []


def test_internal_aggregate_provenance_is_not_mislabelled_as_public_approval() -> None:
    assert _validate_publication_boundary(
        _load_manifest(), _read(SUMMARY_PATH), _read(INDEX_PATH), _read(README_PATH)
    ) == []


def test_mutation_rejects_approval_inferred_from_tracked_source() -> None:
    index = _read(INDEX_PATH).replace(
        "| `TRACKED_INTERNAL_AGGREGATE` |",
        "| `SANITIZED_AGGREGATE_APPROVED` |",
        1,
    )
    row = next(line for line in index.splitlines() if line.startswith("| E-P37-009 |"))
    index = index.replace(row, row.replace("`TRACKED_INTERNAL_AGGREGATE`", "`SANITIZED_AGGREGATE_APPROVED`"))
    errors = _validate_publication_boundary(
        _load_manifest(), _read(SUMMARY_PATH), index, _read(README_PATH)
    )
    assert "E-P37-009 overstates publication approval" in errors


def test_mutation_rejects_public_link_to_unapproved_results() -> None:
    readme = _read(README_PATH) + "\n[Public results](docs/RESULTS_SUMMARY.md)\n"
    errors = _validate_publication_boundary(
        _load_manifest(), _read(SUMMARY_PATH), _read(INDEX_PATH), readme
    )
    assert "public README exposes or mislabels the internal results summary" in errors


def test_all_manifest_sources_exist_and_are_relative() -> None:
    data = _load_manifest()
    assert _validate_source_paths(data) == []


def test_phase35_and_phase36_prerequisites_are_really_closed() -> None:
    assert _validate_phase_prerequisites(_read(MASTER_PATH)) == []


def test_task1_label_semantics_match_tracked_spec() -> None:
    labels = _read(ROOT / "docs" / "task1_label_spec.md")
    summary = _read(SUMMARY_PATH)
    assert "max(arrival_dt, window_open_dt)" in labels
    assert "arrival_dt > window_close_dt" in labels
    assert "early waiting is excluded" in summary
    assert "Arrival exactly at close is not late" in summary


def test_task1_feature_rankings_match_approved_source() -> None:
    source = _read(ROOT / "docs" / "task1_explainability.md")
    summary = _read(SUMMARY_PATH)
    features = [
        "outlet_prior_service_median", "festival_ramp", "order_volume_m3", "monsoon",
        "order_weight_kg", "planned_slack_to_close_min", "outlet_prior_late_rate",
        "planned_arrival_cos", "prior_planned_units",
    ]
    for feature in features:
        assert feature in source and feature in summary
    assert "not a universal direction" in summary
    assert "does not establish a universal direction" in source


def test_task2a_semantics_and_constraints_are_explicit() -> None:
    summary = _read(SUMMARY_PATH)
    assert "counts each order once including deferred/not-run demand" in summary
    assert "requested-date ISO year/week" in summary
    assert "Cross-source duplicate order keys must fail closed" in summary
    assert "ten-week grid" in summary
    assert "Style and Tech chilled demand are structural zeros" in summary
    assert "caps chilled at total" in summary


def test_task2b_aggregates_match_tracked_policy() -> None:
    source = _read(ROOT / "docs" / "task2b_policy.md")
    summary = _read(SUMMARY_PATH)
    required = ["79 of 85", "92.9%", "6 (7.1%)", "28 vehicles", "4 reefers", "44 of the theoretical 56", "268 of 270", "183 of 480", "99.2%", "99.7%", "1,188 units", "9,770.9 kg", "81.57 m3", "40.91 m3"]
    for claim in required:
        assert claim in source
    claims, duplicates = _parse_claim_rows(summary)
    assert duplicates == []
    assert len(claims) == 33
    assert claims["N-T2B-001"]["value"] == "79"
    assert claims["N-T2B-018"]["value"] == "99.7"
    assert claims["N-T2B-031"]["value"] == "40.91"


def test_checker_is_feasibility_not_optimality() -> None:
    summary = _read(SUMMARY_PATH)
    validator = _read(ROOT / "docs" / "task2b_validation_spec.md")
    assert "FEASIBILITY: PASSED - every rule satisfied." in validator
    assert "does not prove a unique global optimum" in summary
    assert "no return leg" in summary
    assert "at most two trips" in summary


def test_unavailable_visuals_are_not_selected() -> None:
    data = _load_manifest()
    selected_tasks = {v["task"] for v in data["visuals"]["selected"]}
    internal_tasks = {v["task"] for v in data["visuals"]["internal_candidates"]}
    unavailable_tasks = {v["task"] for v in data["visuals"]["unavailable"]}
    assert unavailable_tasks == {"DT-466", "DT-470"}
    assert internal_tasks == {"DT-467", "DT-471", "DT-472"}
    assert all(v["publication_approval"] == "PENDING" for v in data["visuals"]["internal_candidates"])
    assert selected_tasks == set()
    assert selected_tasks.isdisjoint(unavailable_tasks)


def test_no_private_paths_or_identifier_samples_in_public_results_docs() -> None:
    combined = _read(SUMMARY_PATH) + "\n" + _read(INDEX_PATH)
    assert "reports/private/" not in combined
    assert "data/raw/" not in combined
    assert "youtube.com" not in combined.lower()
    assert "youtu.be" not in combined.lower()
    assert not re.search(r"\b(?:delivery|order|outlet|row)[_-]?(?:id|ref)\s*[=:]\s*[A-Z0-9-]{4,}", combined, re.I)


def test_phase35_scope_is_not_expanded() -> None:
    disclosure = _read(ROOT / "docs" / "AI_USE_DISCLOSURE.md")
    organizer = _read(ROOT / "docs" / "PHASE35_ORGANIZER_COMMUNICATION_RECORD.md")
    summary = _read(SUMMARY_PATH)
    assert "not treated as a blanket exemption" in disclosure
    assert "must not be characterized as" in organizer
    assert "not a blanket competition-rule exemption" in summary


def test_mutation_rejects_invented_metric_value() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["metrics"][0]["value"] = 4.2
    assert any("without aggregate approval" in error for error in _validate_manifest(mutant))


def test_mutation_rejects_missing_metric_split() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    del mutant["metrics"][0]["split"]
    assert any("lacks provenance fields" in error for error in _validate_manifest(mutant))


def test_mutation_rejects_claim_id_shift_between_markdown_and_yaml() -> None:
    summary = _read(SUMMARY_PATH).replace("| N-T2B-007 |", "| N-T2B-034 |", 1)
    errors = _validate_claim_consistency(_load_manifest(), summary, _read(INDEX_PATH))
    assert "displayed summary claim IDs do not exactly match the manifest" in errors


def test_mutation_rejects_duplicate_claim_id() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["numeric_claims"]["items"].append(copy.deepcopy(mutant["numeric_claims"]["items"][0]))
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert "duplicate claim ID: N-T2B-001" in errors


def test_mutation_rejects_displayed_claim_missing_from_manifest() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["numeric_claims"]["items"] = mutant["numeric_claims"]["items"][1:]
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert "displayed summary claim IDs do not exactly match the manifest" in errors


def test_mutation_rejects_contradictory_claim_value() -> None:
    summary = _read(SUMMARY_PATH).replace(
        "| N-T2B-001 | Served whole orders | 79 | orders |",
        "| N-T2B-001 | Served whole orders | 78 | orders |",
        1,
    )
    errors = _validate_claim_consistency(_load_manifest(), summary, _read(INDEX_PATH))
    assert "N-T2B-001 value contradicts summary" in errors


def test_mutation_rejects_incorrect_claim_unit() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["numeric_claims"]["items"][0]["unit"] = "kg"
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert "N-T2B-001 unit contradicts summary" in errors
    assert "N-T2B-001 unit contradicts index" in errors


def test_mutation_rejects_missing_claim_source_provenance() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    del mutant["numeric_claims"]["items"][0]["source"]
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert any("N-T2B-001 missing provenance fields" in error for error in errors)


def test_mutation_rejects_missing_publication_approval() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    del mutant["numeric_claims"]["items"][0]["publication_approval"]
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert any("N-T2B-001 missing provenance fields" in error for error in errors)


def test_mutation_rejects_unapproved_claim_selected_for_public_release() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["numeric_claims"]["items"][0]["selected_for_public_release"] = True
    errors = _validate_claim_consistency(mutant, _read(SUMMARY_PATH), _read(INDEX_PATH))
    assert "unapproved claim selected for public release: N-T2B-001" in errors


def test_mutation_rejects_incorrect_checker_pass_reference() -> None:
    index = _read(INDEX_PATH).replace(
        "`MD Files/PHASE_33_COMPETITION_CONTRACT.md`, final completion record",
        "`docs/final_submission_validation.md`",
        1,
    )
    assert "E-P37-011 does not cite the actual Phase 33 completion record" in _validate_checker_evidence(index)


def test_mutation_rejects_wrong_task1_error_unit() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["metrics"][0]["unit"] = "percent"
    assert any("incompatible unit" in error for error in _validate_manifest(mutant))


@pytest.mark.parametrize(
    ("old", "new", "expected_error"),
    [
        ("Arrival exactly at close is not late", "Arrival at close is late", "Arrival exactly at close is not late"),
        ("Cross-source duplicate order keys must fail closed", "Cross-source duplicates use first-row precedence", "Cross-source duplicate order keys must fail closed"),
        ("no return leg", "a return leg is added", "no return leg"),
        ("270-minute Fresh / 480-minute Style+Tech", "300-minute Fresh / 500-minute Style+Tech", "270-minute Fresh / 480-minute Style+Tech"),
        ("does not prove a unique global optimum", "proves the unique global optimum", "does not prove a unique global optimum"),
        ("not a blanket competition-rule exemption", "is blanket competition clearance", "not a blanket competition-rule exemption"),
    ],
)
def test_semantic_mutations_fail(old: str, new: str, expected_error: str) -> None:
    text = _read(SUMMARY_PATH)
    assert old in text
    mutant = text.replace(old, new, 1)
    assert any(expected_error in error for error in _validate_summary(mutant))


def test_phase37_does_not_claim_withheld_accuracy_or_start_phase38() -> None:
    combined = _read(SUMMARY_PATH) + "\n" + _read(INDEX_PATH)
    assert "There is no organizer test-label or leaderboard accuracy claim" in combined
    assert "Phase 37 is not formally closed" in combined
    assert not re.search(r"Phase\s*38\s+(?:has\s+)?started", combined, re.I)


def test_mutation_rejects_unsupported_heldout_score() -> None:
    mutant = _read(SUMMARY_PATH) + "\nOrganizer withheld test accuracy = 0.99.\n"
    assert "unsupported organizer-held-out performance claim" in _validate_summary(mutant)


def test_mutation_rejects_stale_relative_source_link() -> None:
    data = _load_manifest()
    mutant = copy.deepcopy(data)
    mutant["metrics"][0]["source"] = "docs/does_not_exist_phase37.md"
    assert any("invalid or stale source path" in error for error in _validate_source_paths(mutant))


def test_mutation_rejects_reopened_phase35_gate() -> None:
    master = _read(MASTER_PATH)
    mutant = master.replace("| [x] | **DT-451** |", "| [ ] | **DT-451** |", 1)
    assert "Phase 35 task DT-451 is not closed" in _validate_phase_prerequisites(mutant)
