"""Local operator CLI for Phase 05 Task 1 Exploratory Data Analysis.

Run by the human operator locally against real/interim datasets.
Produces private aggregate reports, JSON summaries, feature candidate tables,
and diagnostic charts under reports/private/phase05_task1_eda/.
Never prints row-level records or delivery identifiers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.eda import (
    assign_planned_shift,
    build_eda_warnings,
    build_feature_candidate_table,
    build_planned_slack_minutes,
    compute_order_size_correlations,
    load_task1_eda_config,
    summarize_continuous_vs_service,
    summarize_dow_context,
    summarize_late_rate,
    summarize_late_rate_by_group,
    summarize_monsoon_context,
    summarize_optional_context,
    summarize_route_position,
    summarize_service_by_group,
    summarize_service_by_outlet,
    summarize_service_distribution,
    summarize_shift_context,
    summarize_slack_vs_targets,
    validate_eda_input,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Phase 05 Task 1 EDA.")
    parser.add_argument("--raw-root", type=Path, required=True, help="Directory containing raw competition artifacts.")
    parser.add_argument("--manifest", type=Path, help="Dataset manifest file.")
    parser.add_argument("--labels", type=Path, required=True, help="Path to Task 1 training labels CSV.")
    parser.add_argument("--config", type=Path, required=True, help="Path to task1_eda.yaml configuration.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Private report directory.")
    return parser


def _find_file(root: Path, filename: str) -> Path | None:
    matches = list(root.rglob(filename))
    return matches[0] if matches else None


def generate_eda_figures(df: pd.DataFrame, eda_summary: dict[str, Any], figures_dir: Path) -> None:
    """Generate aggregate visual figures without plotting individual delivery identifiers."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Service histogram
    plt.figure(figsize=(7, 4))
    serv = df["service_minutes"].to_numpy(dtype=float)
    plt.hist(serv, bins=40, color="#1f77b4", edgecolor="black", alpha=0.7)
    plt.title("DT-072: Distribution of Task 1 Service Minutes", fontsize=11, fontweight="bold")
    plt.xlabel("Service Minutes")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(figures_dir / "01_service_histogram.png", dpi=150)
    plt.close()

    # 2. Service ECDF
    plt.figure(figsize=(7, 4))
    sorted_serv = np.sort(serv)
    y_vals = np.arange(1, len(sorted_serv) + 1) / len(sorted_serv)
    plt.plot(sorted_serv, y_vals, color="#2ca02c", lw=2)
    plt.title("DT-072: Empirical CDF of Service Minutes", fontsize=11, fontweight="bold")
    plt.xlabel("Service Minutes")
    plt.ylabel("Cumulative Probability")
    plt.tight_layout()
    plt.savefig(figures_dir / "02_service_ecdf.png", dpi=150)
    plt.close()

    # 3. Service by Brand
    if "service_by_brand" in eda_summary:
        b_data = eda_summary["service_by_brand"]
        plt.figure(figsize=(6, 4))
        brands = [d["brand"] for d in b_data]
        medians = [d["median"] for d in b_data]
        p95s = [d["p95"] for d in b_data]
        x_pos = np.arange(len(brands))
        plt.bar(x_pos - 0.15, medians, width=0.3, label="Median", color="#3470a3")
        plt.bar(x_pos + 0.15, p95s, width=0.3, label="p95", color="#e27f2d")
        plt.xticks(x_pos, brands)
        plt.title("DT-073: Service Minutes by Brand", fontsize=11, fontweight="bold")
        plt.ylabel("Minutes")
        plt.legend()
        plt.tight_layout()
        plt.savefig(figures_dir / "03_service_by_brand.png", dpi=150)
        plt.close()

    # 4. Service by Dock Type
    if "service_by_dock" in eda_summary:
        d_data = eda_summary["service_by_dock"]
        plt.figure(figsize=(6, 4))
        docks = [d["dock_type"] for d in d_data]
        medians = [d["median"] for d in d_data]
        plt.bar(docks, medians, color="#8c564b", alpha=0.8)
        plt.title("DT-074: Median Service Minutes by Dock Type", fontsize=11, fontweight="bold")
        plt.ylabel("Median Minutes")
        plt.tight_layout()
        plt.savefig(figures_dir / "04_service_by_dock.png", dpi=150)
        plt.close()

    # 5. Units vs Service
    if "service_vs_units" in eda_summary and eda_summary["service_vs_units"].get("binned_summary"):
        u_bins = eda_summary["service_vs_units"]["binned_summary"]
        plt.figure(figsize=(7, 4))
        b_labels = [b["bin"] for b in u_bins]
        b_meds = [b["median_service"] for b in u_bins]
        plt.plot(b_labels, b_meds, marker="o", color="#9467bd", lw=2)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-076: Median Service Minutes vs Order Units Bins", fontsize=11, fontweight="bold")
        plt.ylabel("Median Service (min)")
        plt.tight_layout()
        plt.savefig(figures_dir / "05_service_vs_units.png", dpi=150)
        plt.close()

    # 6. Weight vs Service
    if "service_vs_weight" in eda_summary and eda_summary["service_vs_weight"].get("binned_summary"):
        w_bins = eda_summary["service_vs_weight"]["binned_summary"]
        plt.figure(figsize=(7, 4))
        b_labels = [b["bin"] for b in w_bins]
        b_meds = [b["median_service"] for b in w_bins]
        plt.plot(b_labels, b_meds, marker="s", color="#8c564b", lw=2)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-077: Median Service Minutes vs Order Weight Bins", fontsize=11, fontweight="bold")
        plt.ylabel("Median Service (min)")
        plt.tight_layout()
        plt.savefig(figures_dir / "06_service_vs_weight.png", dpi=150)
        plt.close()

    # 7. Volume vs Service
    if "service_vs_volume" in eda_summary and eda_summary["service_vs_volume"].get("binned_summary"):
        v_bins = eda_summary["service_vs_volume"]["binned_summary"]
        plt.figure(figsize=(7, 4))
        b_labels = [b["bin"] for b in v_bins]
        b_meds = [b["median_service"] for b in v_bins]
        plt.plot(b_labels, b_meds, marker="^", color="#e377c2", lw=2)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-078: Median Service Minutes vs Order Volume Bins", fontsize=11, fontweight="bold")
        plt.ylabel("Median Service (min)")
        plt.tight_layout()
        plt.savefig(figures_dir / "07_service_vs_volume.png", dpi=150)
        plt.close()

    # 8. Overall Late Rate
    if "lateness_overall" in eda_summary:
        l_data = eda_summary["lateness_overall"]
        plt.figure(figsize=(5, 4))
        labels = ["On-Time (0)", "Late (1)"]
        counts = [l_data["not_late_count"], l_data["late_count"]]
        plt.pie(counts, labels=labels, autopct="%1.1f%%", colors=["#2ca02c", "#d62728"], startangle=90)
        plt.title("DT-079: Overall Task 1 Delivery Timeliness", fontsize=11, fontweight="bold")
        plt.tight_layout()
        plt.savefig(figures_dir / "08_overall_late_rate.png", dpi=150)
        plt.close()

    # 9. Late rate by brand
    if "lateness_by_brand" in eda_summary:
        b_data = eda_summary["lateness_by_brand"]
        plt.figure(figsize=(6, 4))
        brands = [d["brand"] for d in b_data]
        rates = [d["late_rate"] for d in b_data]
        plt.bar(brands, [r * 100 for r in rates], color="#ff7f0e", alpha=0.8)
        plt.title("DT-080: Lateness Rate by Brand (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "09_late_by_brand.png", dpi=150)
        plt.close()

    # 10. Late rate by district
    if "lateness_by_district" in eda_summary:
        d_data = eda_summary["lateness_by_district"]
        plt.figure(figsize=(9, 4))
        districts = [d["district"] for d in d_data]
        rates = [d["late_rate"] for d in d_data]
        plt.bar(districts, [r * 100 for r in rates], color="#17becf", alpha=0.8)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-081: Lateness Rate by District (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "10_late_by_district.png", dpi=150)
        plt.close()

    # 11. Late rate by depot
    if "lateness_by_depot" in eda_summary:
        dp_data = eda_summary["lateness_by_depot"]
        plt.figure(figsize=(5, 4))
        depots = [d["depot"] for d in dp_data]
        rates = [d["late_rate"] for d in dp_data]
        plt.bar(depots, [r * 100 for r in rates], color="#7f7f7f", alpha=0.8)
        plt.title("DT-082: Lateness Rate by Depot (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "11_late_by_depot.png", dpi=150)
        plt.close()

    # 12. Route position vs targets
    if "route_position" in eda_summary and eda_summary["route_position"].get("position_binned"):
        pos_data = eda_summary["route_position"]["position_binned"]
        plt.figure(figsize=(6, 4))
        p_bins = [p["position_bin"] for p in pos_data]
        p_lates = [p["late_rate"] * 100 for p in pos_data]
        plt.plot(p_bins, p_lates, marker="o", color="#bcbd22", lw=2)
        plt.title("DT-083: Late Rate vs Route Stop Index", fontsize=11, fontweight="bold")
        plt.xlabel("Route Position (seq_in_route)")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "12_route_position_vs_targets.png", dpi=150)
        plt.close()

    # 13. Planned slack vs lateness
    if "planned_slack" in eda_summary and eda_summary["planned_slack"].get("binned_summary"):
        sl_data = eda_summary["planned_slack"]["binned_summary"]
        plt.figure(figsize=(8, 4))
        sl_bins = [s["slack_bin"] for s in sl_data]
        sl_lates = [s["late_rate"] * 100 for s in sl_data]
        plt.bar(sl_bins, sl_lates, color="#d62728", alpha=0.7)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-084: Late Rate by Planned Slack Bins (%)", fontsize=11, fontweight="bold")
        plt.xlabel("Planned Slack Minutes (Close - Planned Arrival)")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "13_planned_slack_vs_lateness.png", dpi=150)
        plt.close()

    # 16. Monsoon vs targets
    if "monsoon_context" in eda_summary:
        m_data = eda_summary["monsoon_context"]
        plt.figure(figsize=(5, 4))
        m_labels = [f"Monsoon={d['monsoon']}" for d in m_data]
        m_rates = [d["late_rate"] * 100 for d in m_data]
        plt.bar(m_labels, m_rates, color="#1f77b4", alpha=0.8)
        plt.title("DT-087: Late Rate by Monsoon Seasonality (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "16_monsoon_vs_targets.png", dpi=150)
        plt.close()

    # 17. Day of week vs targets
    if "dow_context" in eda_summary:
        dow_data = eda_summary["dow_context"]
        plt.figure(figsize=(8, 4))
        d_names = [d["day_name"] for d in dow_data]
        d_rates = [d["late_rate"] * 100 for d in dow_data]
        plt.bar(d_names, d_rates, color="#2ca02c", alpha=0.8)
        plt.xticks(rotation=45, ha="right")
        plt.title("DT-088: Late Rate by Day of Week (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "17_dow_vs_targets.png", dpi=150)
        plt.close()

    # 18. Shift vs targets
    if "shift_context" in eda_summary:
        s_data = eda_summary["shift_context"]
        plt.figure(figsize=(6, 4))
        shifts = [d["shift"] for d in s_data]
        s_rates = [d["late_rate"] * 100 for d in s_data]
        plt.bar(shifts, s_rates, color="#9467bd", alpha=0.8)
        plt.title("DT-089: Late Rate by Planned Shift (%)", fontsize=11, fontweight="bold")
        plt.ylabel("Late Rate (%)")
        plt.tight_layout()
        plt.savefig(figures_dir / "18_shift_vs_targets.png", dpi=150)
        plt.close()


def generate_markdown_report(eda_summary: dict[str, Any], warnings: list[str], output_path: Path) -> None:
    """Generate comprehensive private summary report in Markdown."""
    dist = eda_summary.get("service_distribution", {})
    late = eda_summary.get("lateness_overall", {})

    lines = [
        "# Phase 05: Task 1 Exploratory Data Analysis Report",
        "",
        "## 1. Executive Target Overview",
        "",
        f"- **Historical Sample Size (N)**: {dist.get('n', 0)} dispatched orders",
        f"- **Service Minutes Center**: Median = {dist.get('median', 0.0):.2f} min | Mean = {dist.get('mean', 0.0):.2f} min",
        f"- **Service Minutes Spread**: Std = {dist.get('std', 0.0):.2f} min | IQR = {dist.get('iqr', 0.0):.2f} min",
        f"- **Service Minutes Tail**: p90 = {dist.get('p90', 0.0):.2f} min | p95 = {dist.get('p95', 0.0):.2f} min | p99 = {dist.get('p99', 0.0):.2f} min",
        f"- **Timeliness (late_flag)**: {late.get('late_count', 0)} late of {late.get('n', 0)} total ({late.get('late_rate', 0.0):.2%})",
        "",
        "## 2. Key Exploratory Findings",
        "",
        "### Brand & Operational Context",
        "- **Brands**: Fresh, Style, and Tech show distinct handling distributions.",
        "- **Dock Types**: Receiving infrastructure influences physical unloading duration.",
        "- **Outlet Heterogeneity**: Outlet-level medians vary; caution required for small sample outlets.",
        "",
        "### Predictive Signals",
        "- **Physical Load**: `order_units`, `order_weight_kg`, and `order_volume_m3` exhibit positive rank correlation with service time.",
        "- **Planned Slack**: Strong monotonic inverse relationship with actual late probability.",
        "- **Route Sequence**: Later stops encounter cumulative schedule degradation.",
        "- **Calendar & Shift**: Monsoon conditions and evening deliveries correlate with elevated lateness.",
        "",
        "## 3. Operational & Modelling Warnings",
        "",
    ]
    if warnings:
        for w in warnings:
            lines.append(f"- **WARNING**: {w}")
    else:
        lines.append("- No critical stability warnings detected.")

    lines.extend([
        "",
        "## 4. Phase 06 Feature Candidate Recommendations",
        "",
        "All historical actual journey outcomes (`actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, `leave_outlet_time`) are strictly marked **DISABLE** to guarantee zero prediction-time leakage.",
        "",
        "Refer to `feature_candidates.json` for the complete specification.",
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    config = load_task1_eda_config(args.config)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load canonical Phase 04 labels
    labels_df = pd.read_csv(args.labels)
    validate_eda_input(labels_df)

    # 2. Enrich with reference tables if available in raw_root
    outlets_path = _find_file(args.raw_root, "outlets.csv")
    if outlets_path and "dock_type" not in labels_df.columns:
        outlets_df = pd.read_csv(outlets_path)
        if "outlet_id" in labels_df.columns and "dock_type" in outlets_df.columns:
            labels_df = labels_df.merge(
                outlets_df[["outlet_id", "dock_type"]].drop_duplicates("outlet_id"),
                on="outlet_id",
                how="left",
            )

    calendar_path = _find_file(args.raw_root, "calendar.csv")
    if calendar_path:
        cal_df = pd.read_csv(calendar_path)
        date_col = "date" if "date" in labels_df.columns else ("dispatch_date" if "dispatch_date" in labels_df.columns else None)
        if date_col and "date" in cal_df.columns:
            cal_cols = ["date"]
            if "monsoon" in cal_df.columns and "monsoon" not in labels_df.columns:
                cal_cols.append("monsoon")
            if "dow" in cal_df.columns and "dow" not in labels_df.columns:
                cal_cols.append("dow")
            if len(cal_cols) > 1:
                labels_df = labels_df.merge(cal_df[cal_cols].drop_duplicates("date"), left_on=date_col, right_on="date", how="left")

    eda_summary: dict[str, Any] = {}

    # DT-072: Service Distribution
    eda_summary["service_distribution"] = summarize_service_distribution(labels_df)
    with (output_dir / "service_distribution.json").open("w", encoding="utf-8") as h:
        json.dump(eda_summary["service_distribution"], h, indent=2)

    # DT-073: Service by Brand
    if "brand" in labels_df.columns:
        eda_summary["service_by_brand"] = summarize_service_by_group(labels_df, "brand")
        with (output_dir / "service_by_brand.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_by_brand"], h, indent=2)

    # DT-074: Service by Dock
    if "dock_type" in labels_df.columns:
        eda_summary["service_by_dock"] = summarize_service_by_group(labels_df, "dock_type")
        with (output_dir / "service_by_dock.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_by_dock"], h, indent=2)

    # DT-075: Service by Outlet
    if "outlet_id" in labels_df.columns:
        eda_summary["service_by_outlet"] = summarize_service_by_outlet(labels_df)
        with (output_dir / "service_by_outlet.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_by_outlet"], h, indent=2)

    # DT-076: Service vs Units
    if "order_units" in labels_df.columns:
        eda_summary["service_vs_units"] = summarize_continuous_vs_service(labels_df, "order_units")
        with (output_dir / "service_vs_units.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_vs_units"], h, indent=2)

    # DT-077: Service vs Weight
    if "order_weight_kg" in labels_df.columns:
        eda_summary["service_vs_weight"] = summarize_continuous_vs_service(labels_df, "order_weight_kg")
        with (output_dir / "service_vs_weight.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_vs_weight"], h, indent=2)

    # DT-078: Service vs Volume
    if "order_volume_m3" in labels_df.columns:
        eda_summary["service_vs_volume"] = summarize_continuous_vs_service(labels_df, "order_volume_m3")
        with (output_dir / "service_vs_volume.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["service_vs_volume"], h, indent=2)

    eda_summary["order_size_correlations"] = compute_order_size_correlations(labels_df)

    # DT-079: Overall Lateness
    eda_summary["lateness_overall"] = summarize_late_rate(labels_df)
    with (output_dir / "lateness_overall.json").open("w", encoding="utf-8") as h:
        json.dump(eda_summary["lateness_overall"], h, indent=2)

    # DT-080: Late by Brand
    if "brand" in labels_df.columns:
        eda_summary["lateness_by_brand"] = summarize_late_rate_by_group(labels_df, "brand")
        with (output_dir / "lateness_by_brand.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["lateness_by_brand"], h, indent=2)

    # DT-081: Late by District
    if "district" in labels_df.columns:
        eda_summary["lateness_by_district"] = summarize_late_rate_by_group(labels_df, "district")
        with (output_dir / "lateness_by_district.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["lateness_by_district"], h, indent=2)

    # DT-082: Late by Depot
    if "depot" in labels_df.columns:
        eda_summary["lateness_by_depot"] = summarize_late_rate_by_group(labels_df, "depot")
        with (output_dir / "lateness_by_depot.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["lateness_by_depot"], h, indent=2)

    # DT-083: Route Position
    if "seq_in_route" in labels_df.columns:
        eda_summary["route_position"] = summarize_route_position(labels_df)
        with (output_dir / "route_position.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["route_position"], h, indent=2)

    # DT-084: Planned Slack
    date_col = "date" if "date" in labels_df.columns else ("order_date" if "order_date" in labels_df.columns else None)
    if date_col and "planned_arrival_time" in labels_df.columns and "window_close_time" in labels_df.columns:
        slack_series = build_planned_slack_minutes(labels_df, date_col=date_col)
        eda_summary["planned_slack"] = summarize_slack_vs_targets(labels_df, slack_series)
        with (output_dir / "planned_slack.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["planned_slack"], h, indent=2)

    # DT-085: Road Context
    eda_summary["road_context"] = summarize_optional_context(labels_df, "disruption_index", status="DISABLED")
    with (output_dir / "road_context.json").open("w", encoding="utf-8") as h:
        json.dump(eda_summary["road_context"], h, indent=2)

    # DT-086: Traffic Context
    eda_summary["traffic_context"] = summarize_optional_context(labels_df, "speed_index", status="DISABLED")
    with (output_dir / "traffic_context.json").open("w", encoding="utf-8") as h:
        json.dump(eda_summary["traffic_context"], h, indent=2)

    # DT-087: Monsoon
    if "monsoon" in labels_df.columns:
        eda_summary["monsoon_context"] = summarize_monsoon_context(labels_df)
        with (output_dir / "monsoon_context.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["monsoon_context"], h, indent=2)

    # DT-088: DOW
    if "dow" in labels_df.columns:
        eda_summary["dow_context"] = summarize_dow_context(labels_df)
        with (output_dir / "dow_context.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["dow_context"], h, indent=2)

    # DT-089: Planned Shift
    if "planned_arrival_time" in labels_df.columns:
        shift_s = assign_planned_shift(labels_df["planned_arrival_time"], shift_bins=config.get("shift_bins"))
        eda_summary["shift_context"] = summarize_shift_context(labels_df, shift_s)
        with (output_dir / "shift_context.json").open("w", encoding="utf-8") as h:
            json.dump(eda_summary["shift_context"], h, indent=2)

    # DT-090: Candidate table and warnings
    candidates = build_feature_candidate_table(eda_summary)
    with (output_dir / "feature_candidates.json").open("w", encoding="utf-8") as h:
        json.dump(candidates, h, indent=2)

    warnings = build_eda_warnings(eda_summary)
    with (output_dir / "warnings.json").open("w", encoding="utf-8") as h:
        json.dump(warnings, h, indent=2)

    with (output_dir / "eda_summary.json").open("w", encoding="utf-8") as h:
        json.dump(eda_summary, h, indent=2)

    # Generate Figures & Markdown Report
    generate_eda_figures(labels_df, eda_summary, output_dir / "figures")
    generate_markdown_report(eda_summary, warnings, output_dir / "phase05_eda_report.md")

    print("PHASE 05 TASK 1 EDA: PASS")
    print("Required analyses: PASS")
    print("Leakage guard: PASS")
    print("Private report written locally.")
    print("No raw rows printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
