from pathlib import Path

from scripts.validate_architecture_docs import _validate_sources


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs/architecture"


def test_all_diagram_sources_cover_required_semantics():
    import yaml

    manifest = yaml.safe_load((ARCH / "architecture_manifest.yaml").read_text(encoding="utf-8"))
    sources = _validate_sources(ARCH, manifest)
    assert set(sources) == {
        "high_level_datathon", "task1_pipeline", "task2a_forecasting",
        "task2b_optimization", "proposed_deployment",
    }


def test_task2b_excludes_non_rules_and_separates_policy():
    text = (ARCH / "task2b_optimization.mmd").read_text(encoding="utf-8").lower()
    assert "not hard constraints" in text
    assert "wayloom soft priority - not organizer priority" in text
    assert "feasibility only; does not prove optimality" in text
    assert "no return leg" in text


def test_task1_and_task2a_official_outputs_do_not_include_optional_fields():
    task1 = (ARCH / "task1_pipeline.mmd").read_text(encoding="utf-8")
    task2a = (ARCH / "task2a_forecasting.mmd").read_text(encoding="utf-8")
    assert "SHAP" not in task1 and "uncertainty" not in task1.lower()
    assert "uncertainty" not in task2a.lower()
