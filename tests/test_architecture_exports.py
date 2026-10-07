import hashlib
from pathlib import Path
from xml.etree import ElementTree

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs/architecture"


def test_all_static_svg_exports_are_valid_and_current():
    manifest = yaml.safe_load((ARCH / "architecture_manifest.yaml").read_text(encoding="utf-8"))
    titles = {item["diagram_id"]: item["title"] for item in manifest["diagrams"]}
    assert len(titles) == 5
    for diagram_id, title in titles.items():
        source = ARCH / f"{diagram_id}.mmd"
        export = ARCH / f"{diagram_id}.svg"
        assert source.is_file() and export.is_file() and export.stat().st_size > 500
        text = export.read_text(encoding="utf-8")
        ElementTree.fromstring(text)
        assert "<svg" in text
        assert "viewBox=" in text or ("width=" in text and "height=" in text)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert f'id="wayloom-source-sha256">{digest}<' in text
        assert f'id="wayloom-diagram-title">{title}<' in text
        assert "data:image" not in text.lower() and "base64," not in text.lower()
        assert not any(marker in text.lower() for marker in ('href="http://', "href='http://", 'href="https://', "href='https://"))


def test_export_titles_are_unique_and_stable():
    manifest = yaml.safe_load((ARCH / "architecture_manifest.yaml").read_text(encoding="utf-8"))
    titles = [item["title"] for item in manifest["diagrams"]]
    assert len(titles) == len(set(titles)) == 5


def test_task2a_export_has_presentation_friendly_aspect_ratio():
    root = ElementTree.fromstring((ARCH / "task2a_forecasting.svg").read_text(encoding="utf-8"))
    view_box = root.attrib.get("viewBox", "").split()
    assert len(view_box) == 4
    width, height = map(float, view_box[2:])
    assert width > 0 and height > 0
    assert width / height <= 5.0, (
        f"Task 2A SVG is pathologically wide for fit-to-page viewing: {width:g} x {height:g}"
    )
