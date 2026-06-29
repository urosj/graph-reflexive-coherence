#!/usr/bin/env python3
"""Render supporting visuals for N28 generative/extractive persistence."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
VISUAL_DIR = OUTPUTS / "n28_generative_extractive_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
MANIFEST_PATH = OUTPUTS / "n28_generative_extractive_visualization.json"
REPORT_PATH = REPORTS / "n28_generative_extractive_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n28_generative_extractive_pattern_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n28_generative_extractive_pattern_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n28_generative_extractive_pattern_animation.gif"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "render_n28_generative_extractive_visualization.py"
)

CONSERVATION_CAVEAT = (
    "The visualization plots local focal-basin and neighborhood capacity metrics; "
    "it does not plot or audit global total-coherence invariance."
)

SOURCE_CASES = [
    {
        "case_id": "generative_enrichment",
        "title": "Generative enrichment",
        "short_label": "generative",
        "source_path": OUTPUTS / "n28_primary_generative_candidate_probe.json",
        "regime": "generative",
        "source_iteration": "4",
        "caption": "neighbor grows; focal remains stable",
        "color": "#2ca25f",
    },
    {
        "case_id": "extractive_persistence",
        "title": "Extractive persistence",
        "short_label": "extractive",
        "source_path": OUTPUTS / "n28_primary_extractive_contrast_probe.json",
        "regime": "extractive",
        "source_iteration": "4-B",
        "caption": "neighbor degrades; focal remains stable",
        "color": "#d95f02",
    },
    {
        "case_id": "competitive_redistribution",
        "title": "Competitive redistribution",
        "short_label": "competitive",
        "source_path": OUTPUTS / "n28_primary_competitive_neutral_contrast_probe.json",
        "regime": "competitive",
        "source_iteration": "4-D",
        "caption": "capacity shifts between lobes",
        "color": "#756bb1",
    },
    {
        "case_id": "neutral_circulation",
        "title": "Neutral circulation",
        "short_label": "neutral",
        "source_path": OUTPUTS / "n28_competitive_neutral_mechanism_diversity_probe.json",
        "regime": "neutral",
        "source_iteration": "4-E",
        "caption": "gain/loss/buffer circulation",
        "color": "#3182bd",
    },
]

SOURCE_CLOSEOUT = OUTPUTS / "n28_closeout_and_n29_handoff.json"
SOURCE_CLASSIFICATION = OUTPUTS / "n28_controls_ap_dependency_claim_classification.json"

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "pygrc-matplotlib"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(data: Any) -> str:
    return hashlib.sha256(compact_json(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def source_row(data: dict[str, Any]) -> dict[str, Any]:
    rows = data.get("candidate_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("N28 source artifact must contain candidate_rows")
    row = rows[0]
    if not isinstance(row, dict):
        raise TypeError("N28 candidate row must be a JSON object")
    return row


def selected_case(config: dict[str, Any]) -> dict[str, Any]:
    data = load_json(config["source_path"])
    row = source_row(data)
    focal = row["focal_basin_stability_trace"]
    capacity = row["neighborhood_capacity_delta_trace"]
    attribution = row["capacity_attribution_trace"]
    classification = row.get("regime_classification_result") or row.get(
        "generative_classification_result"
    )
    case = {
        **config,
        "source_output_digest": data["output_digest"],
        "source_sha256": sha256_file(config["source_path"]),
        "source_artifact_id": data["artifact_id"],
        "row_id": row["row_id"],
        "row_digest": row["row_digest"],
        "focal_pre_support": focal["pre_support_min"],
        "focal_post_support": focal["post_support_min"],
        "focal_pre_coherence": focal["pre_coherence_min"],
        "focal_post_coherence": focal["post_coherence_min"],
        "focal_pre_stability": focal["pre_stability_score"],
        "focal_post_stability": focal["post_stability_score"],
        "support_floor": focal["support_floor"],
        "neighbor_pre_capacity": capacity["pre_environment_basin_forming_capacity"],
        "neighbor_post_capacity": capacity["post_environment_basin_forming_capacity"],
        "environment_capacity_delta": capacity["environment_capacity_delta"],
        "neighbor_support_delta": capacity["neighbor_support_delta"],
        "neighbor_boundary_delta": capacity["neighbor_boundary_delta"],
        "neighbor_distinguishability_delta": capacity["neighbor_distinguishability_delta"],
        "extraction_cost": row["focal_extraction_cost_trace"]["value"],
        "extraction_cost_ceiling": row["focal_extraction_cost_trace"]["ceiling"],
        "flattening": row["extractive_flattening_trace"]["value"],
        "flattening_ceiling": row["extractive_flattening_trace"]["ceiling"],
        "merge_leakage": row["merge_leakage_trace"]["value"],
        "merge_leakage_ceiling": row["merge_leakage_trace"]["ceiling"],
        "classification_result": classification["classification_result"],
        "classification_reason": classification["classification_reason"],
        "attribution_result": attribution["attribution_result"],
        "mechanism_class": attribution.get("mechanism_class", "capacity_gain"),
        "route_lobe_a_capacity_delta": attribution.get("route_lobe_a_capacity_delta"),
        "route_lobe_b_capacity_delta": attribution.get("route_lobe_b_capacity_delta"),
        "inflow_lobe_capacity_delta": attribution.get("inflow_lobe_capacity_delta"),
        "outflow_lobe_capacity_delta": attribution.get("outflow_lobe_capacity_delta"),
        "buffer_lobe_capacity_delta": attribution.get("buffer_lobe_capacity_delta"),
    }
    case["case_digest"] = digest_value(
        {
            key: case[key]
            for key in [
                "row_id",
                "row_digest",
                "regime",
                "environment_capacity_delta",
                "neighbor_support_delta",
                "neighbor_boundary_delta",
                "neighbor_distinguishability_delta",
                "extraction_cost",
                "flattening",
                "merge_leakage",
            ]
        }
    )
    return case


def signed_text(value: float) -> str:
    return f"{value:+.3f}"


def metric_color(value: float) -> str:
    if value > 0.0005:
        return "#2ca25f"
    if value < -0.0005:
        return "#d95f02"
    return "#6b6b6b"


def draw_arrow(ax: Any, start: tuple[float, float], end: tuple[float, float], color: str, rad: float = 0.0) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.3,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arrow)


def draw_basin_pair(ax: Any, case: dict[str, Any], stage: str, compact: bool = False) -> None:
    ax.set_axis_off()
    ax.set_xlim(-2.25, 2.65)
    ax.set_ylim(-1.7, 1.7)
    pre = stage == "pre"
    cap = case["neighbor_pre_capacity"] if pre else case["neighbor_post_capacity"]
    support = case["focal_pre_support"] if pre else case["focal_post_support"]
    stability = case["focal_pre_stability"] if pre else case["focal_post_stability"]
    neighbor_radius = 0.54 + max(0.0, min(0.22, (cap - 0.58) * 0.55))
    focal = Circle((-1.05, 0.0), 0.72, facecolor="#d9f0a3", edgecolor="#263238", linewidth=1.3)
    neighbor = Circle((1.08, 0.0), neighbor_radius, facecolor=case["color"], edgecolor="#263238", alpha=0.82, linewidth=1.3)
    ax.add_patch(focal)
    ax.add_patch(neighbor)
    label_size = 8.1 if compact else 8.5
    metric_size = 7.0 if compact else 7.5
    metric_y = -1.03 if compact else -0.55
    cap_y = -1.03 if compact else -0.55
    ax.text(-1.05, 0.1, "focal\nbasin", ha="center", va="center", fontsize=label_size, fontweight="bold")
    ax.text(-1.05, metric_y, f"s {support:.3f}\nst {stability:.3f}", ha="center", va="center", fontsize=metric_size)
    ax.text(1.08, 0.08, "neighbor\nfield", ha="center", va="center", fontsize=label_size, fontweight="bold", color="#111111")
    ax.text(1.08, cap_y, f"cap {cap:.3f}", ha="center", va="center", fontsize=metric_size, color="#111111")
    if not pre:
        regime = case["regime"]
        if regime == "generative":
            draw_arrow(ax, (-0.2, 0.45), (0.45, 0.45), "#238b45", 0.05)
            ax.text(0.15, 0.78, "enrich", ha="center", va="center", fontsize=8, color="#238b45")
        elif regime == "extractive":
            draw_arrow(ax, (0.45, 0.45), (-0.2, 0.45), "#a63603", -0.05)
            ax.text(0.15, 0.78, "drain", ha="center", va="center", fontsize=8, color="#a63603")
        elif regime == "competitive":
            draw_arrow(ax, (0.65, 0.52), (1.55, 0.52), "#756bb1", 0.16)
            draw_arrow(ax, (1.55, -0.52), (0.65, -0.52), "#756bb1", 0.16)
            ax.text(1.1, 1.08, "redistribute", ha="center", va="center", fontsize=8, color="#54278f")
        else:
            draw_arrow(ax, (0.55, 0.48), (1.45, 0.48), "#3182bd", 0.32)
            draw_arrow(ax, (1.55, -0.48), (0.65, -0.48), "#3182bd", 0.32)
            ax.text(1.1, 1.08, "circulate", ha="center", va="center", fontsize=8, color="#08519c")
    if compact:
        ax.text(0.0, -1.4, stage, ha="center", va="center", fontsize=8, color="#455a64")


def draw_delta_bars(ax: Any, case: dict[str, Any], show_title: bool = True) -> None:
    ax.set_axis_off()
    labels = ["env", "support", "boundary", "dist.", "extract", "flat.", "leak"]
    values = [
        case["environment_capacity_delta"],
        case["neighbor_support_delta"],
        case["neighbor_boundary_delta"],
        case["neighbor_distinguishability_delta"],
        -case["extraction_cost"],
        -case["flattening"],
        -case["merge_leakage"],
    ]
    ax.set_xlim(-0.12, 0.14)
    ax.set_ylim(-0.8, len(labels) - 0.2)
    ax.axvline(0, color="#263238", linewidth=1.0)
    for index, (label, value) in enumerate(zip(labels, values)):
        color = metric_color(value)
        left = min(0, value)
        width = abs(value)
        ax.add_patch(Rectangle((left, index - 0.25), width, 0.48, facecolor=color, alpha=0.86))
        ax.text(-0.118, index, label, ha="left", va="center", fontsize=7.5, color="#263238")
        ax.text(0.136, index, signed_text(value), ha="right", va="center", fontsize=7.3, color="#263238")
    if show_title:
        ax.text(0.01, len(labels) - 0.02, "delta / cost", ha="center", va="bottom", fontsize=8.5, fontweight="bold")


def draw_pattern_panel(ax: Any, case: dict[str, Any]) -> None:
    ax.set_axis_off()
    ax.set_xlim(-3.4, 3.5)
    ax.set_ylim(-2.15, 2.15)
    focal = Circle((-1.9, 0.0), 0.7, facecolor="#d9f0a3", edgecolor="#263238", linewidth=1.4)
    neighbor = Circle((1.55, 0.0), 0.68, facecolor=case["color"], edgecolor="#263238", alpha=0.83, linewidth=1.4)
    ax.add_patch(focal)
    ax.add_patch(neighbor)
    ax.text(-1.9, 0.08, "focal\nstable", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(1.55, 0.08, case["short_label"], ha="center", va="center", fontsize=9, fontweight="bold")

    if case["regime"] == "generative":
        draw_arrow(ax, (-1.05, 0.15), (0.8, 0.15), "#238b45", 0.05)
        ax.text(-0.1, 0.55, "neighbor capacity rises", ha="center", fontsize=8.2, color="#238b45")
    elif case["regime"] == "extractive":
        draw_arrow(ax, (0.85, 0.15), (-1.05, 0.15), "#a63603", -0.05)
        ax.text(-0.1, 0.55, "capacity drains / flattens", ha="center", fontsize=8.2, color="#a63603")
    elif case["regime"] == "competitive":
        draw_arrow(ax, (0.75, 0.62), (2.25, 0.62), "#756bb1", 0.18)
        draw_arrow(ax, (2.25, -0.62), (0.75, -0.62), "#756bb1", 0.18)
        ax.text(1.5, 1.04, "opposed lobe shifts", ha="center", fontsize=8.2, color="#54278f")
    else:
        draw_arrow(ax, (0.75, 0.62), (2.25, 0.62), "#3182bd", 0.34)
        draw_arrow(ax, (2.25, -0.62), (0.75, -0.62), "#3182bd", 0.34)
        ax.text(1.5, 1.04, "three-lobe circulation", ha="center", fontsize=8.2, color="#08519c")

    ax.text(-3.25, 1.78, case["title"], ha="left", va="center", fontsize=12, fontweight="bold", color="#263238")
    ax.text(-3.25, 1.49, f"I{case['source_iteration']} row: {case['row_id']}", ha="left", va="center", fontsize=7.6, color="#455a64")
    ax.text(
        -3.25,
        -1.55,
        f"env {signed_text(case['environment_capacity_delta'])} | "
        f"support {signed_text(case['neighbor_support_delta'])} | "
        f"boundary {signed_text(case['neighbor_boundary_delta'])}",
        ha="left",
        va="center",
        fontsize=8.4,
        color="#263238",
    )
    ax.text(
        -3.25,
        -1.84,
        f"extract {case['extraction_cost']:.3f} | flat {case['flattening']:.3f} | leak {case['merge_leakage']:.3f}",
        ha="left",
        va="center",
        fontsize=8.1,
        color="#7f3b08",
    )


def draw_graph(cases: list[dict[str, Any]], closeout: dict[str, Any], path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 9.2), facecolor="#f8f7f2")
    for ax, case in zip(axes.flat, cases):
        ax.set_facecolor("#f8f7f2")
        draw_pattern_panel(ax, case)
    fig.suptitle(
        "N28 source-backed generative / extractive persistence pattern classes",
        fontsize=16,
        fontweight="bold",
        color="#263238",
        y=0.985,
    )
    fig.text(
        0.02,
        0.018,
        "Local metric projection only; total-coherence invariance is not plotted or audited here.",
        ha="left",
        va="bottom",
        fontsize=9,
        color="#455a64",
    )
    fig.text(
        0.98,
        0.018,
        f"final: {closeout['final_ge_ladder_rung']}",
        ha="right",
        va="bottom",
        fontsize=8.8,
        color="#455a64",
    )
    fig.subplots_adjust(left=0.025, right=0.985, bottom=0.06, top=0.92, hspace=0.24, wspace=0.18)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def draw_sequence(cases: list[dict[str, Any]], path: Path) -> None:
    fig = plt.figure(figsize=(16.2, 13.2), facecolor="#f8f7f2")
    grid = fig.add_gridspec(len(cases), 4, width_ratios=[0.9, 1.08, 1.08, 1.2], hspace=0.36, wspace=0.26)
    for row_index, case in enumerate(cases):
        label_ax = fig.add_subplot(grid[row_index, 0])
        label_ax.set_axis_off()
        label_ax.text(0.0, 0.72, case["title"], ha="left", va="center", fontsize=11.5, fontweight="bold", color="#263238")
        label_ax.text(0.0, 0.43, case["caption"], ha="left", va="center", fontsize=8.2, color="#455a64", wrap=True)
        label_ax.text(0.0, 0.16, f"I{case['source_iteration']} | {case['classification_result']}", ha="left", va="center", fontsize=8, color="#7f3b08")

        pre_ax = fig.add_subplot(grid[row_index, 1])
        pre_ax.set_facecolor("#f8f7f2")
        draw_basin_pair(pre_ax, case, "pre", compact=True)
        if row_index == 0:
            pre_ax.set_title("before", fontsize=11, fontweight="bold")

        post_ax = fig.add_subplot(grid[row_index, 2])
        post_ax.set_facecolor("#f8f7f2")
        draw_basin_pair(post_ax, case, "post", compact=True)
        if row_index == 0:
            post_ax.set_title("after", fontsize=11, fontweight="bold")

        delta_ax = fig.add_subplot(grid[row_index, 3])
        delta_ax.set_facecolor("#f8f7f2")
        draw_delta_bars(delta_ax, case, show_title=False)
        if row_index == 0:
            delta_ax.set_title("recorded deltas / costs", fontsize=11, fontweight="bold")
    fig.suptitle("N28 pattern sequence: before / after / delta by class", fontsize=16, fontweight="bold", y=0.988)
    fig.text(
        0.02,
        0.012,
        "Costs are negative bars. Deltas are local metrics; total-coherence invariance is not shown.",
        ha="left",
        va="bottom",
        fontsize=9,
        color="#455a64",
    )
    fig.subplots_adjust(left=0.03, right=0.98, bottom=0.055, top=0.93)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def draw_frame(case: dict[str, Any], frame_index: int, path: Path) -> None:
    fig = plt.figure(figsize=(9.2, 6.0), facecolor="#f8f7f2")
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.7], width_ratios=[1.0, 1.0], hspace=0.18)
    pre_ax = fig.add_subplot(grid[0, 0])
    post_ax = fig.add_subplot(grid[0, 1])
    delta_ax = fig.add_subplot(grid[1, :])
    draw_basin_pair(pre_ax, case, "pre")
    draw_basin_pair(post_ax, case, "post")
    draw_delta_bars(delta_ax, case)
    pre_ax.set_title("before", fontsize=10, fontweight="bold")
    post_ax.set_title("after", fontsize=10, fontweight="bold")
    fig.suptitle(f"N28 {frame_index + 1}/4: {case['title']}", fontsize=15, fontweight="bold", y=0.98)
    fig.text(
        0.5,
        0.03,
        f"{case['caption']} | local env {signed_text(case['environment_capacity_delta'])} | "
        "not a total-coherence audit",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#455a64",
    )
    fig.subplots_adjust(left=0.055, right=0.955, bottom=0.11, top=0.88, hspace=0.26, wspace=0.18)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def save_animation(frame_paths: list[Path], target: Path) -> None:
    frames = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in frame_paths]
    frames[0].save(
        target,
        save_all=True,
        append_images=frames[1:],
        duration=1450,
        loop=0,
        optimize=False,
    )
    for frame in frames:
        frame.close()


def write_manifest(
    cases: list[dict[str, Any]],
    closeout: dict[str, Any],
    classification: dict[str, Any],
    frame_paths: list[Path],
) -> dict[str, Any]:
    visual_outputs = {
        "graph_png": {"path": rel(GRAPH_PATH), "sha256": sha256_file(GRAPH_PATH)},
        "sequence_png": {"path": rel(SEQUENCE_PATH), "sha256": sha256_file(SEQUENCE_PATH)},
        "animation_gif": {"path": rel(ANIMATION_PATH), "sha256": sha256_file(ANIMATION_PATH)},
        "frames": [
            {"path": rel(path), "sha256": sha256_file(path)}
            for path in frame_paths
        ],
    }
    source_artifacts = [
        {
            "source_role": "n28_closeout",
            "path": rel(SOURCE_CLOSEOUT),
            "output_digest": closeout["output_digest"],
            "sha256": sha256_file(SOURCE_CLOSEOUT),
        },
        {
            "source_role": "n28_i7_claim_classification",
            "path": rel(SOURCE_CLASSIFICATION),
            "output_digest": classification["output_digest"],
            "sha256": sha256_file(SOURCE_CLASSIFICATION),
        },
    ]
    for case in cases:
        source_artifacts.append(
            {
                "source_role": f"n28_{case['case_id']}_source_row",
                "path": rel(case["source_path"]),
                "output_digest": case["source_output_digest"],
                "sha256": case["source_sha256"],
                "row_id": case["row_id"],
                "row_digest": case["row_digest"],
            }
        )
    manifest = {
        "artifact_id": "n28_generative_extractive_visualization",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "visual_status": "passed",
        "visualized_case_count": len(cases),
        "visualized_classes": [case["case_id"] for case in cases],
        "final_ge_ladder_rung": closeout["final_ge_ladder_rung"],
        "final_n28_closeout_rung": closeout["final_n28_closeout_rung"],
        "broad_margin_robustness_supported": closeout["broad_margin_robustness_supported"],
        "ap4_nat4_gap_resolved": closeout["ap4_nat4_gap_resolved"],
        "ap5_nat4_gap_resolved": closeout["ap5_nat4_gap_resolved"],
        "visual_proof_allowed": False,
        "renderer_boundary": (
            "source-backed diagnostic projection from recorded N28 row metrics; "
            "not a new proof layer and not a full runtime geometry replay"
        ),
        "conservation_caveat": CONSERVATION_CAVEAT,
        "global_total_coherence_invariance_audited": False,
        "global_total_coherence_checksum_present": False,
        "local_metric_deltas_are_total_coherence_deltas": False,
        "source_artifacts": source_artifacts,
        "visual_outputs": visual_outputs,
        "case_summaries": [
            {
                "case_id": case["case_id"],
                "row_id": case["row_id"],
                "source_iteration": case["source_iteration"],
                "classification_result": case["classification_result"],
                "environment_capacity_delta": case["environment_capacity_delta"],
                "neighbor_support_delta": case["neighbor_support_delta"],
                "neighbor_boundary_delta": case["neighbor_boundary_delta"],
                "neighbor_distinguishability_delta": case["neighbor_distinguishability_delta"],
                "extraction_cost": case["extraction_cost"],
                "flattening": case["flattening"],
                "merge_leakage": case["merge_leakage"],
            }
            for case in cases
        ],
        "claim_boundary": {
            "visuals_are_inspection_aids_only": True,
            "semantic_cooperation_claim_allowed": False,
            "agency_claim_allowed": False,
            "native_support_claim_allowed": False,
            "phase8_completion_claim_allowed": False,
            "ant_ecology_claim_allowed": False,
            "broad_margin_robustness_claim_allowed": False,
        },
        "unsafe_claim_flags": {
            "semantic_cooperation": False,
            "semantic_choice": False,
            "semantic_goal_ownership": False,
            "agency": False,
            "native_support": False,
            "selfhood": False,
            "identity_acceptance": False,
            "sentience": False,
            "organism_life": False,
            "ant_ecology_implementation": False,
            "phase8_completion": False,
            "native_ap5": False,
            "ap4_nat4_gap_resolution": False,
            "ap5_nat4_gap_resolution": False,
            "broad_margin_robustness": False,
        },
    }
    manifest["output_digest"] = digest_value(manifest)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    return manifest


def write_report(manifest: dict[str, Any]) -> None:
    rows = [
        "| Class | Source row | Env delta | Support delta | Boundary delta | Classification |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in manifest["case_summaries"]:
        rows.append(
            f"| `{case['case_id']}` | `{case['row_id']}` | "
            f"`{case['environment_capacity_delta']:+.3f}` | "
            f"`{case['neighbor_support_delta']:+.3f}` | "
            f"`{case['neighbor_boundary_delta']:+.3f}` | "
            f"`{case['classification_result']}` |"
        )
    report = f"""# N28 Generative / Extractive Persistence Visualization

Status: `{manifest['visual_status']}`

Output digest: `{manifest['output_digest']}`

This visualization is a source-backed diagnostic projection over four N28
pattern classes. The plotted deltas are local focal-basin and neighborhood
capacity metrics, not global total-coherence deltas:

{chr(10).join(rows)}

Visual outputs:

```text
graph_png = {manifest['visual_outputs']['graph_png']['path']}
sequence_png = {manifest['visual_outputs']['sequence_png']['path']}
animation_gif = {manifest['visual_outputs']['animation_gif']['path']}
```

Boundary:

```text
visual_proof_allowed = {str(manifest['visual_proof_allowed']).lower()}
renderer_boundary = {manifest['renderer_boundary']}
conservation_caveat = {manifest['conservation_caveat']}
global_total_coherence_invariance_audited = {str(manifest['global_total_coherence_invariance_audited']).lower()}
global_total_coherence_checksum_present = {str(manifest['global_total_coherence_checksum_present']).lower()}
local_metric_deltas_are_total_coherence_deltas = {str(manifest['local_metric_deltas_are_total_coherence_deltas']).lower()}
broad_margin_robustness_supported = {str(manifest['broad_margin_robustness_supported']).lower()}
ap4_nat4_gap_resolved = {str(manifest['ap4_nat4_gap_resolved']).lower()}
ap5_nat4_gap_resolved = {str(manifest['ap5_nat4_gap_resolved']).lower()}
```

Conservation caveat:

The plotted before/after bars are local focal-basin and neighborhood capacity
metrics. They should not be read as global total-coherence changes. N28 records
environment-capacity budget compatibility, but it does not compute a global
total-coherence checksum before/after the visualized rows.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    cases = [selected_case(config) for config in SOURCE_CASES]
    closeout = load_json(SOURCE_CLOSEOUT)
    classification = load_json(SOURCE_CLASSIFICATION)

    draw_graph(cases, closeout, GRAPH_PATH)
    draw_sequence(cases, SEQUENCE_PATH)
    frame_paths: list[Path] = []
    for index, case in enumerate(cases):
        frame_path = FRAMES_DIR / f"n28_generative_extractive_frame_{index:02d}_{case['short_label']}.png"
        draw_frame(case, index, frame_path)
        frame_paths.append(frame_path)
    save_animation(frame_paths, ANIMATION_PATH)
    manifest = write_manifest(cases, closeout, classification, frame_paths)
    write_report(manifest)


if __name__ == "__main__":
    main()
