"""Render Phase 29 Mermaid sources with an already-installed Mermaid CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_IDS = (
    "high_level_datathon",
    "task1_pipeline",
    "task2a_forecasting",
    "task2b_optimization",
    "proposed_deployment",
)


class ArchitectureRenderError(RuntimeError):
    """Static architecture rendering could not be completed safely."""


def _renderer() -> str:
    candidates = [
        os.environ.get("MERMAID_CLI"),
        shutil.which("mmdc"),
        str(ROOT / "node_modules" / ".bin" / "mmdc.cmd"),
        str(Path(tempfile.gettempdir()) / "wayloom-phase29-mermaid" / "node_modules" / ".bin" / "mmdc.cmd"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise ArchitectureRenderError(
        "Mermaid CLI was not found. Put mmdc on PATH, install it under repository node_modules, "
        "or set MERMAID_CLI to the executable path."
    )


def _browser() -> str | None:
    candidates = [
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        shutil.which("msedge"),
        shutil.which("chrome"),
    ]
    program_files = os.environ.get("ProgramFiles")
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    local_app_data = os.environ.get("LOCALAPPDATA")
    if program_files_x86:
        candidates.append(str(Path(program_files_x86) / "Microsoft" / "Edge" / "Application" / "msedge.exe"))
    if program_files:
        candidates.extend(
            [
                str(Path(program_files) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
                str(Path(program_files) / "Google" / "Chrome" / "Application" / "chrome.exe"),
            ]
        )
    if local_app_data:
        candidates.extend(
            [
                str(Path(local_app_data) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
                str(Path(local_app_data) / "Google" / "Chrome" / "Application" / "chrome.exe"),
            ]
        )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def _inject_metadata(svg_path: Path, source_path: Path, title: str) -> None:
    svg = svg_path.read_text(encoding="utf-8")
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    metadata = (
        f'<metadata id="wayloom-source-sha256">{digest}</metadata>'
        f'<title id="wayloom-diagram-title">{title}</title>'
    )
    match = re.search(r"<svg\b[^>]*>", svg)
    if not match:
        raise ArchitectureRenderError(f"Renderer did not produce SVG: {svg_path.name}")
    svg = svg[: match.end()] + metadata + svg[match.end() :]
    svg_path.write_text(svg, encoding="utf-8")


def render(source_dir: Path, output_dir: Path, preview_dir: Path | None = None) -> None:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    canonical = (ROOT / "docs" / "architecture").resolve()
    if source_dir != canonical or output_dir != canonical:
        raise ArchitectureRenderError("Phase 29 rendering is restricted to docs/architecture.")
    renderer = _renderer()
    if preview_dir is not None:
        preview_dir = preview_dir.resolve()
        preview_dir.mkdir(parents=True, exist_ok=True)
    manifest = yaml.safe_load((canonical / "architecture_manifest.yaml").read_text(encoding="utf-8"))
    titles = {item["diagram_id"]: item["title"] for item in manifest["diagrams"]}
    browser = _browser()
    with tempfile.TemporaryDirectory(prefix="wayloom-phase29-") as temp_dir:
        browser_args: list[str] = []
        if browser:
            config_path = Path(temp_dir) / "puppeteer.json"
            config_path.write_text(
                json.dumps(
                    {
                        "executablePath": browser,
                        "headless": True,
                        "args": [
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                            "--no-first-run",
                            "--no-default-browser-check",
                        ],
                    }
                ),
                encoding="utf-8",
            )
            browser_args = ["-p", str(config_path)]
        for diagram_id in DIAGRAM_IDS:
            source = source_dir / f"{diagram_id}.mmd"
            output = output_dir / f"{diagram_id}.svg"
            subprocess.run(
                [
                    renderer,
                    "-i",
                    str(source),
                    "-o",
                    str(output),
                    "-t",
                    "neutral",
                    "-b",
                    "white",
                    "-w",
                    "2200",
                    *browser_args,
                ],
                cwd=ROOT,
                check=True,
            )
            _inject_metadata(output, source, titles[diagram_id])
            if preview_dir is not None:
                subprocess.run(
                    [
                        renderer,
                        "-i",
                        str(source),
                        "-o",
                        str(preview_dir / f"{diagram_id}.png"),
                        "-t",
                        "neutral",
                        "-b",
                        "white",
                        "-w",
                        "2200",
                        "-s",
                        "2",
                        *browser_args,
                    ],
                    cwd=ROOT,
                    check=True,
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=ROOT / "docs" / "architecture")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "architecture")
    parser.add_argument("--preview-dir", type=Path)
    args = parser.parse_args()
    render(args.source_dir, args.output_dir, args.preview_dir)
    print("LOCAL PHASE 29 STATIC SVG RENDER: PASS")
    print("RENDERED DIAGRAM COUNT: 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
