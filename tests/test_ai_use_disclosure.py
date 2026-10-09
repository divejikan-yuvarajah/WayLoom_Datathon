import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCLOSURE = ROOT / "docs" / "AI_USE_DISCLOSURE.md"
CLARIFICATION_REQUEST = ROOT / "docs" / "PHASE35_ORGANIZER_CLARIFICATION_REQUEST.md"
COMMUNICATION_RECORD = ROOT / "docs" / "PHASE35_ORGANIZER_COMMUNICATION_RECORD.md"
APPROVAL_CHECKLIST = ROOT / "docs" / "PHASE35_FINAL_HUMAN_APPROVAL_CHECKLIST.md"
APPROVAL_RECORD = ROOT / "docs" / "PHASE35_FINAL_HUMAN_APPROVAL_RECORD.md"
MASTER_PLAN = ROOT / "MD Files" / "WAYLOOM_DATATHON_MASTER_PLAN.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phase35_consistency_issues(
    disclosure: str, checklist: str, communication_record: str
) -> list[str]:
    """Return semantic conflicts across the three current Phase 35 records."""
    documents = {
        "disclosure": disclosure,
        "checklist": checklist,
        "communication record": communication_record,
    }
    issues: list[str] = []

    for name, text in documents.items():
        lowered = text.lower()
        required_concepts = {
            "known dataset/notebook sharing": (
                "competition csv/dataset files",
                "private jupyter notebooks",
                "shared with chatgpt and codex",
            ),
            "real inference sharing": (
                "inference inputs",
                "identifiers",
                "predictions",
                "shared with chatgpt",
            ),
            "organizer awareness provenance": ("human_confirmed",),
            "written response provenance": ("screenshot_supported",),
            "email channel": ("email/gmail",),
            "unavailable authenticated thread": (
                "complete original",
                "authenticated",
                "headers",
            ),
            "incident-specific scope": ("disclosed incident",),
            "no blanket exemption": ("blanket exemption",),
        }
        for concept, tokens in required_concepts.items():
            if not all(token in lowered for token in tokens):
                issues.append(f"{name} is missing {concept}")

    for line in checklist.splitlines():
        lowered = line.lower()
        if (
            "organizer awareness" in lowered
            and "inference" in lowered
            and "not confirmed" in lowered
        ):
            issues.append("checklist reintroduces outdated inference-awareness status")
        if (
            "communication provenance" in lowered
            and "written evidence" in lowered
            and "not confirmed" in lowered
        ):
            issues.append("checklist reintroduces outdated communication-evidence status")

    approval_requirements = {
        "disclosure": "renewed exact-version factual approval:** `pending`",
        "checklist": "renewed approval of exact corrected versions:** `pending`",
        "communication record": "renewed exact-version human approval and narrow independent re-review pending",
    }
    for name, marker in approval_requirements.items():
        if marker not in documents[name].lower():
            issues.append(f"{name} does not keep renewed exact-version approval pending")

    return issues


def test_disclosure_answers_the_three_official_questions() -> None:
    text = _text(DISCLOSURE)

    assert "## Work that was AI-assisted" in text
    assert "## Work that was not AI-assisted" in text
    assert "How it was used" in text
    assert "## Model, automated-tool, API, and data-handling boundaries" in text


def test_all_five_master_tasks_have_exact_traceability() -> None:
    disclosure = _text(DISCLOSURE)
    master = _text(MASTER_PLAN)
    expected = {
        "DT-451": "Record all AI-assisted activities",
        "DT-452": "Record human-controlled modelling work",
        "DT-453": "Record where AI was not used",
        "DT-454": "Confirm compliance with competition restrictions",
        "DT-455": "Write final AI-tool disclosure",
    }

    for task_id, title in expected.items():
        assert f"**{task_id}**" in master
        assert title in master
        assert f"| {task_id} | {title} |" in disclosure


def test_human_attestation_is_recorded_without_premature_phase_closure() -> None:
    text = _text(DISCLOSURE)

    assert "Status: CORRECTED FINAL DRAFT — RENEWED EXACT-VERSION HUMAN APPROVAL PENDING" in text
    assert "**Attestation status:** `HUMAN CONFIRMED`" in text
    assert "**Renewed exact-version factual approval:** `PENDING`" in text
    assert "**Compliance resolution:** `DT-454 PASS" in text
    assert "READY FOR AUTHORIZED FINAL APPROVAL" in text
    assert "PHASE 35 REMAINS OPEN" in text
    assert "`COUNTS AND EXACT SCOPE PENDING`" in text
    assert "organizer approval" in text


def test_confirmed_real_data_transmission_is_not_minimized() -> None:
    text = _text(DISCLOSURE)

    assert "competition CSV/dataset files and private Jupyter notebooks were shared with ChatGPT and Codex" in text
    assert "were additionally pasted into ChatGPT" in text
    assert "derived from real competition data" in text
    assert "not synthetic demonstration records" in text
    assert "whether complete official training or test datasets were included" in text
    assert "This establishes external transmission of private competition materials." in text
    assert "no blanket exemption claimed" in text.lower()


def test_modelling_restriction_evidence_separates_technical_and_human_status() -> None:
    text = _text(DISCLOSURE)

    assert "PASS — NO PROHIBITED MODELLING IMPLEMENTATION IDENTIFIED" in text
    assert "PASS — NO ADDITIONAL RESTRICTED MODELLING TOOLS USED" in text
    assert "locally loadable CatBoost and CatBoost/LightGBM" in text
    assert "no implemented proprietary remote modelling/preprocessing API" in text
    assert "no AutoML dependency" in text
    assert "ChatGPT/Codex development assistance and confirmed information sharing" in text


def test_final_human_approval_checklist_records_direct_answers_and_stays_open() -> None:
    text = _text(APPROVAL_CHECKLIST)

    assert "Facts already recorded — verify, do not minimize" in text
    assert "Competition CSV/dataset files and private Jupyter notebooks" in text
    assert "Real competition-derived inference inputs, identifiers, and predictions" in text
    assert "One-pass authorized human response" in text
    assert "I am authorized to approve this disclosure for WayLoom Datathon" in text
    assert "ChatGPT and Cursor/OpenAI Codex are all AI assistants used in Datathon" in text
    assert "No unrecorded pretrained predictor" in text
    assert "Human decision roles: model selection" in text
    assert "Earlier-version human factual approval:** `YES — HISTORICAL`" in text
    assert "Renewed approval of exact corrected versions:** `PENDING`" in text
    assert "READY FOR AUTHORIZED FINAL APPROVAL:** `YES`" in text
    assert "READY FOR NARROW FRESH DT-455 RE-REVIEW:** `NO" in text
    assert "PHASE 35 FORMAL CLOSURE:** `NO`" in text


def test_final_verification_records_attestations_and_preserves_organizer_unknowns() -> None:
    disclosure = _text(DISCLOSURE)
    checklist = _text(APPROVAL_CHECKLIST)

    assert "## Final human verification record" in disclosure
    assert "NOT CONFIRMED BEYOND CONTINUED PARTICIPATION" in disclosure
    assert "HUMAN_CONFIRMED COMPLETE" in disclosure
    assert "no additional restricted modelling tool was used" in disclosure
    assert "Renewed exact-version approval" in disclosure
    assert "`PENDING`" in disclosure
    assert "One-pass authorized human response" in checklist
    assert "including labelled uncertainties" in checklist


def test_human_attestation_does_not_become_organizer_clearance() -> None:
    disclosure = _text(DISCLOSURE)
    checklist = _text(APPROVAL_CHECKLIST)

    assert "not organizer approval" in disclosure
    assert "not independent proof of off-repository history" in disclosure
    assert "no blanket exemption claimed" in disclosure.lower()
    assert "does not establish organizer clearance" in checklist
    assert "supersedes the earlier ambiguity without deleting or rewriting that record" in checklist


def test_reported_organizer_guidance_is_scope_limited() -> None:
    disclosure = _text(DISCLOSURE)
    record = _text(COMMUNICATION_RECORD)

    assert "ORGANIZER WRITTEN RESPONSE: SCREENSHOT_SUPPORTED" in disclosure
    assert "you can proceed as you wish" in disclosure
    assert "complete original conversation export and authenticated headers have not been inspected" in disclosure
    assert "not represented as a finding that the sharing complied" in disclosure
    assert "Organizer awareness before the response: `HUMAN_CONFIRMED`" in record
    assert "`PERMISSION_TO_CONTINUE_REPORTED`" in record
    assert "Did the response address real inference snippets shared with ChatGPT?" in record
    assert "`NOT CONFIRMED`" in record
    assert "`COUNTS AND EXACT SCOPE PENDING`" in record
    assert "must not be characterized as" in record
    assert "RENEWED EXACT-VERSION HUMAN APPROVAL AND NARROW INDEPENDENT RE-REVIEW PENDING" in record


def test_written_organizer_response_is_recorded_without_unverified_context_claim() -> None:
    disclosure = _text(DISCLOSURE)
    record = _text(COMMUNICATION_RECORD)

    assert "No problem at all!" in record
    assert "Best wishes for your final submission!" in record
    assert "Rootcode Team" in record
    assert "ORIGINAL DISCLOSURE SCOPE: HUMAN_CONFIRMED" in record
    assert "SAME-CONVERSATION CONTEXT: HUMAN_CONFIRMED" in record
    assert "YES — HUMAN_CONFIRMED SAME-CONVERSATION CONTEXT" in record
    assert "ORGANIZER WRITTEN RESPONSE: SCREENSHOT_SUPPORTED" in disclosure
    assert "authenticated headers have not been inspected" in disclosure


def test_current_phase35_documents_are_semantically_consistent() -> None:
    issues = _phase35_consistency_issues(
        _text(DISCLOSURE), _text(APPROVAL_CHECKLIST), _text(COMMUNICATION_RECORD)
    )

    assert issues == []


def test_stale_inference_awareness_statement_is_rejected() -> None:
    checklist = _text(APPROVAL_CHECKLIST)
    current = (
        "- [x] Organizer awareness of real Task 1/Task 2A inference inputs, identifiers, "
        "and predictions: `HUMAN_CONFIRMED` from the authorized representative's account "
        "of the preceding email."
    )
    mutated = checklist.replace(
        current,
        "- [x] Organizer awareness of inference snippets: `NOT CONFIRMED`.",
    )

    assert mutated != checklist
    issues = _phase35_consistency_issues(
        _text(DISCLOSURE), mutated, _text(COMMUNICATION_RECORD)
    )
    assert "checklist reintroduces outdated inference-awareness status" in issues


def test_stale_communication_evidence_statement_is_rejected() -> None:
    checklist = _text(APPROVAL_CHECKLIST)
    current = (
        "- [x] Communication provenance: channel `EMAIL/GMAIL`; the written organizer "
        "response is `SCREENSHOT_SUPPORTED`; exact date, authenticated original headers, "
        "correspondent metadata, and the complete original conversation export remain unavailable."
    )
    mutated = checklist.replace(
        current,
        "- [x] Communication provenance: team-reported “no worries”; "
        "date/time/channel/roles/written evidence `NOT CONFIRMED`.",
    )

    assert mutated != checklist
    issues = _phase35_consistency_issues(
        _text(DISCLOSURE), mutated, _text(COMMUNICATION_RECORD)
    )
    assert "checklist reintroduces outdated communication-evidence status" in issues


def test_public_records_omit_private_sender_address_and_keep_thread_pending() -> None:
    public_text = _text(DISCLOSURE) + _text(COMMUNICATION_RECORD)

    assert "info@rootcode.io" not in public_text
    assert "complete original email thread" in public_text.lower()
    assert "PENDING" in public_text


def test_organizer_request_is_sanitized_and_fail_closed() -> None:
    text = _text(CLARIFICATION_REQUEST)

    assert "competition CSV/dataset files and private Jupyter notebooks" in text
    assert "shared with ChatGPT and Codex" in text
    assert "additionally shared with ChatGPT" in text
    assert "real competition data" in text
    assert "whether complete official training or test datasets were included" in text
    assert "No confidential records, identifiers, numerical predictions" in text
    assert "Phase 35 closure as blocked" in text


def test_public_disclosure_contains_no_restricted_path_or_row_key() -> None:
    text = (
        _text(DISCLOSURE)
        + _text(CLARIFICATION_REQUEST)
        + _text(COMMUNICATION_RECORD)
        + _text(APPROVAL_CHECKLIST)
    ).lower()
    forbidden = (
        "data/raw/",
        "data/interim/",
        "reports/private/",
        "delivery_id",
        "order_ref",
        "outlet_id",
    )

    assert all(token not in text for token in forbidden)


def test_phase_35_master_flags_record_completed_independent_closure() -> None:
    master = _text(MASTER_PLAN)
    phase = master.split("### Phase 35 — AI-use disclosure", 1)[1].split(
        "### Phase 36 — README / project documentation", 1
    )[0]

    for task_id in range(451, 456):
        assert f"| [x] | **DT-{task_id}** |" in phase
    assert "**Phase complete:** [x]" in phase
    assert "**READY FOR NEXT PHASE:** YES" in phase
    assert "DT-451–DT-455 are 5/5 PASS" in phase
    assert "explicitly authorized formal closure" in phase
    assert "not recorded as a blanket exemption" in phase


def test_final_human_approval_is_bound_to_exact_current_documents() -> None:
    record = _text(APPROVAL_RECORD)
    disclosure_hash = _sha256(DISCLOSURE)
    checklist_hash = _sha256(APPROVAL_CHECKLIST)

    assert "**FINAL HUMAN APPROVAL:** `YES`" in record
    assert "Direct statement from the authorized WayLoom Datathon representative" in record
    assert "Recorded at (Asia/Colombo):** `2026-10-09T14:17:00.285+05:30`" in record
    assert "The representative explicitly confirmed they are authorized" in record
    assert f"`{disclosure_hash}`" in record
    assert f"`{checklist_hash}`" in record
    assert disclosure_hash == "715c2dca328a6792adffad5073633fcd7e362272578dbed788a8179418b6d4d3"
    assert checklist_hash == "ef448b08c5666ef691039e077e96dbae4c9f9c1b7435e4979978a2c0dc0e3c79"
    assert "does not assert a blanket competition-rule exemption" in record
    assert "DT-455 exact-version human approval gate:** `SATISFIED`" in record
    assert "Ready for narrow fresh read-only DT-455 re-review:** `YES`" in record
    assert "Phase 35 formally closed:** `NO`" in record
