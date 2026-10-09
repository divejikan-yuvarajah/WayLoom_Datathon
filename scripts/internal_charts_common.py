"""Shared, human-local helpers for PRIVATE WayLoom results charts.

These helpers never send data over a network, print data values, or write into
the submission tree. Run the task-specific scripts only on the team's local PC.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "reports" / "private"
OUTPUT = PRIVATE_ROOT / "internal_results_charts"
BLUE = "#2563EB"
NAVY = "#0F172A"
ACCENT = "#60A5FA"


class ChartEvidenceError(ValueError):
    """Missing, inconsistent, or unsupported chart evidence."""


def private_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PRIVATE_ROOT.resolve()):
        raise ChartEvidenceError("Chart input/output must stay inside reports/private.")
    return resolved


def source(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.is_file():
        raise ChartEvidenceError("Required local source is missing.")
    return candidate


def private_source(path: str) -> Path:
    return private_path(source(path))


def json_source(path: str, *, private: bool = False) -> dict:
    candidate = private_source(path) if private else source(path)
    value = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ChartEvidenceError("Evidence record is not a mapping.")
    return value


def yaml_source(path: str) -> dict:
    value = yaml.safe_load(source(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ChartEvidenceError("Configuration is not a mapping.")
    return value


def csv_source(path: str, *, private: bool = False, **read_kwargs) -> pd.DataFrame:
    candidate = private_source(path) if private else source(path)
    frame = pd.read_csv(candidate, **read_kwargs)
    if frame.empty:
        raise ChartEvidenceError("Chart source has no rows.")
    return frame


def columns(frame: pd.DataFrame, required: tuple[str, ...]) -> None:
    if any(name not in frame for name in required):
        raise ChartEvidenceError("Chart source is missing required columns.")


def numeric(frame: pd.DataFrame, name: str, *, nonnegative: bool = False) -> pd.Series:
    values = pd.to_numeric(frame[name], errors="coerce")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ChartEvidenceError("Chart source has missing/nonfinite numeric values.")
    if nonnegative and (values < 0).any():
        raise ChartEvidenceError("Chart source has negative values where forbidden.")
    return values.astype(float)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canvas(title: str, subtitle: str, ylabel: str):
    plt.rcParams.update({
        "font.family": ["Inter", "Arial", "DejaVu Sans"],
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "text.color": NAVY,
        "axes.labelcolor": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "axes.edgecolor": "#CBD5E1",
        "font.size": 12,
    })
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.subplots_adjust(left=0.09, right=0.96, top=0.79, bottom=0.17)
    fig.text(0.09, 0.91, title, fontsize=24, fontweight="bold", color=NAVY)
    fig.text(0.09, 0.855, subtitle, fontsize=12, color=NAVY)
    fig.text(0.09, 0.055, "PRIVATE / INTERNAL ONLY", fontsize=15,
             color=BLUE, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#E2E8F0", linewidth=0.9)
    ax.set_axisbelow(True)
    for edge in ("top", "right"):
        ax.spines[edge].set_visible(False)
    return fig, ax


def save(fig, filename: str) -> None:
    private_path(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = private_path(OUTPUT / filename)
    if destination.exists():
        raise ChartEvidenceError("Existing private chart will not be overwritten.")
    try:
        fig.savefig(destination, dpi=120, facecolor="white")
    finally:
        plt.close(fig)
    print(f"CREATED: {filename} (private local directory)")


def skip(filename: str, reason: str) -> None:
    # Only fixed, non-sensitive reasons are passed by the task scripts.
    print(f"SKIPPED: {filename} — {reason}")
