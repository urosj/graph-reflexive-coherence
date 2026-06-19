#!/usr/bin/env python3
"""Render supporting graph visuals for N18 Iteration 8 shared-medium stress."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SOURCE_ARTIFACT = OUTPUTS / "n18_shared_medium_stress_matrix.json"
N16_GEOMETRY_SOURCE = (
    ROOT
    / "experiments"
    / "2026-06-N16-lgrc-self-environment-boundary"
    / "outputs"
    / "n16_selected_interaction_probe_matrix.json"
)
VISUAL_DIR = OUTPUTS / "n18_iteration8_shared_medium_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
GEOMETRY_FRAMES_DIR = VISUAL_DIR / "geometry_frames"
MANIFEST_PATH = OUTPUTS / "n18_iteration8_shared_medium_visualization.json"
REPORT_PATH = REPORTS / "n18_iteration8_shared_medium_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n18_i8_shared_medium_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n18_i8_shared_medium_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n18_i8_shared_medium_animation.gif"
GEOMETRY_GRAPH_PATH = VISUAL_DIR / "n18_i8_b4c5_source_geometry_graph.png"
GEOMETRY_SEQUENCE_PATH = VISUAL_DIR / "n18_i8_b4c5_source_geometry_sequence.png"
GEOMETRY_ANIMATION_PATH = VISUAL_DIR / "n18_i8_b4c5_source_geometry_animation.gif"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/render_n18_iteration8_shared_medium_visualization.py"
)

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "pygrc-matplotlib"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402
import networkx as nx  # noqa: E402
from PIL import Image  # noqa: E402


TRACE_KEYS = [
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
]

NODE_LABELS = {
    "support": "support\nAP3",
    "memory": "memory\ncontext",
    "regulation": "regulation\nAP3",
    "selection": "selection\nAP4",
    "proxy": "proxy/target\nAP5",
    "boundary": "boundary\nAP6",
    "loop_feedback": "loop feedback\nAP7",
    "shared_medium": "shared medium\nstress",
    "neighbor": "neighbor\nbasin",
    "budget": "budget\ngate",
    "claim_boundary": "claim\nboundary",
}

POSITIONS = {
    "support": (-2.8, 0.2),
    "regulation": (-1.55, 0.2),
    "selection": (-0.3, 0.2),
    "proxy": (0.95, 0.2),
    "boundary": (2.2, 0.2),
    "loop_feedback": (3.45, 0.2),
    "memory": (-0.8, 1.25),
    "shared_medium": (2.15, 1.35),
    "neighbor": (3.45, 1.35),
    "budget": (2.2, -1.0),
    "claim_boundary": (3.45, -1.0),
}

BASE_EDGES = [
    ("support", "regulation", "support_to_regulation"),
    ("regulation", "selection", "regulation_to_selection"),
    ("memory", "selection", "memory_context_to_selection"),
    ("selection", "proxy", "selection_to_proxy"),
    ("proxy", "boundary", "proxy_to_boundary"),
    ("boundary", "loop_feedback", "boundary_to_loop_feedback"),
    ("loop_feedback", "support", "closure_return"),
    ("shared_medium", "boundary", "shared_medium_pressure"),
    ("shared_medium", "neighbor", "neighbor_leakage"),
    ("boundary", "budget", "budget_surface"),
    ("claim_boundary", "loop_feedback", "claim_gate"),
]

GEOMETRY_POSITIONS = {
    "b4_c5_a0": (-2.15, 0.72),
    "b4_c5_a1": (-2.15, -0.05),
    "b4_c5_a2": (-0.95, 0.32),
    "b4_c5_medium": (0.6, 0.28),
    "b4_c5_neighbor0": (2.05, 0.66),
    "b4_c5_neighbor1": (2.05, -0.17),
}

GEOMETRY_LABELS = {
    "b4_c5_a0": "A0",
    "b4_c5_a1": "A1",
    "b4_c5_a2": "A2\nboundary",
    "b4_c5_medium": "shared\nmedium",
    "b4_c5_neighbor0": "B0\nneighbor",
    "b4_c5_neighbor1": "B1",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def row_by_id(artifact: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in artifact["rows"]:
        if row["row_id"] == row_id:
            return row
    raise KeyError(row_id)


def score_color(score: float | None, floor: float = 0.8) -> str:
    if score is None:
        return "#d7d7d7"
    if score < floor:
        return "#d95f02"
    if score <= floor + 0.003:
        return "#f0c419"
    return "#2ca25f"


def decision_color(decision: str) -> str:
    return {
        "supported": "#2ca25f",
        "partial": "#f0c419",
        "rejected": "#d95f02",
    }.get(decision, "#9e9e9e")


def trace_scores(row: dict[str, Any]) -> dict[str, float]:
    return {
        "support": row["support_state_trace"]["continuity_score"],
        "memory": row["memory_context_trace"]["continuity_score"],
        "regulation": row["regulation_trace"]["continuity_score"],
        "selection": row["selection_context_trace"]["continuity_score"],
        "proxy": row["proxy_target_trace"]["continuity_score"],
        "boundary": row["boundary_separation_trace"]["continuity_score"],
        "loop_feedback": row["closed_loop_feedback_trace"]["continuity_score"],
    }


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    for node in NODE_LABELS:
        graph.add_node(node)
    for source, target, edge_id in BASE_EDGES:
        graph.add_edge(source, target, edge_id=edge_id)
    return graph


def edge_score(row: dict[str, Any], edge_id: str) -> float | None:
    if edge_id == "closure_return":
        return row["closed_loop_feedback_trace"]["continuity_score"]
    if edge_id == "shared_medium_pressure":
        return row["cross_axis_continuity_evidence"]["window_score"]
    if edge_id == "neighbor_leakage":
        return None
    if edge_id == "budget_surface":
        return row["budget_surface"]["budget_headroom"]
    if edge_id == "claim_gate":
        return None
    link = row["linked_trace_continuity"].get(edge_id)
    if link:
        return link["continuity_score"]
    return None


def edge_color(row: dict[str, Any], edge_id: str) -> str:
    if edge_id == "neighbor_leakage":
        return "#8c6d31"
    if edge_id == "budget_surface":
        return "#2ca25f" if row["budget_surface"]["valid"] else "#d95f02"
    if edge_id == "claim_gate":
        return "#636363"
    score = edge_score(row, edge_id)
    return score_color(score)


def draw_visual_frame(
    *,
    row: dict[str, Any],
    title: str,
    subtitle: str,
    notes: list[str],
    output_path: Path,
    active_edges: set[str] | None = None,
    side_rows: list[dict[str, Any]] | None = None,
) -> None:
    active_edges = active_edges or set()
    side_rows = side_rows or []
    graph = build_graph()
    scores = trace_scores(row)
    node_colors = []
    for node in graph.nodes:
        if node in scores:
            node_colors.append(score_color(scores[node]))
        elif node == "budget":
            node_colors.append("#2ca25f" if row["budget_surface"]["valid"] else "#d95f02")
        elif node == "claim_boundary":
            node_colors.append("#636363")
        elif node == "shared_medium":
            node_colors.append("#80b1d3")
        else:
            node_colors.append("#d7b365")

    figure = plt.figure(figsize=(14, 8), facecolor="#f8f8f5")
    axis = figure.add_axes((0.035, 0.08, 0.64, 0.82))
    panel = figure.add_axes((0.71, 0.08, 0.26, 0.82))
    axis.set_axis_off()
    panel.set_axis_off()

    edge_colors = [
        edge_color(row, graph.edges[edge]["edge_id"]) for edge in graph.edges
    ]
    edge_widths = [
        4.2 if graph.edges[edge]["edge_id"] in active_edges else 2.0
        for edge in graph.edges
    ]
    edge_styles = [
        "dashed"
        if graph.edges[edge]["edge_id"] in {"neighbor_leakage", "claim_gate"}
        else "solid"
        for edge in graph.edges
    ]

    for style in sorted(set(edge_styles)):
        styled_edges = [
            edge for edge, edge_style in zip(graph.edges, edge_styles, strict=True)
            if edge_style == style
        ]
        styled_colors = [
            edge_color(row, graph.edges[edge]["edge_id"]) for edge in styled_edges
        ]
        styled_widths = [
            4.2 if graph.edges[edge]["edge_id"] in active_edges else 2.0
            for edge in styled_edges
        ]
        nx.draw_networkx_edges(
            graph,
            POSITIONS,
            ax=axis,
            edgelist=styled_edges,
            edge_color=styled_colors,
            width=styled_widths,
            arrows=True,
            arrowsize=18,
            connectionstyle="arc3,rad=0.07",
            style=style,
        )

    nx.draw_networkx_nodes(
        graph,
        POSITIONS,
        ax=axis,
        node_size=2500,
        node_color=node_colors,
        edgecolors="#333333",
        linewidths=1.4,
    )
    nx.draw_networkx_labels(
        graph,
        POSITIONS,
        labels=NODE_LABELS,
        ax=axis,
        font_size=9,
        font_weight="bold",
    )

    edge_labels = {}
    for source, target, data in graph.edges(data=True):
        edge_id = data["edge_id"]
        score = edge_score(row, edge_id)
        if edge_id == "budget_surface":
            edge_labels[(source, target)] = f"headroom {score:.2f}"
        elif edge_id == "neighbor_leakage":
            edge_labels[(source, target)] = "leakage ctrl"
        elif edge_id == "claim_gate":
            edge_labels[(source, target)] = "unsafe blocked"
        elif score is not None:
            edge_labels[(source, target)] = f"{score:.3f}"
    nx.draw_networkx_edge_labels(
        graph,
        POSITIONS,
        edge_labels=edge_labels,
        ax=axis,
        font_size=8,
        bbox={"boxstyle": "round,pad=0.18", "fc": "#f8f8f5", "ec": "none", "alpha": 0.85},
    )

    axis.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=14)
    axis.text(-3.55, -1.65, subtitle, fontsize=10, color="#333333")
    axis.set_xlim(-3.65, 4.05)
    axis.set_ylim(-1.85, 1.78)

    panel.text(
        0.0,
        0.98,
        "N18 I8 shared-medium stress",
        fontsize=12,
        fontweight="bold",
        va="top",
    )
    panel.text(
        0.0,
        0.91,
        f"row_decision = {row['row_decision']}",
        fontsize=11,
        color=decision_color(row["row_decision"]),
        fontweight="bold",
    )
    panel.text(
        0.0,
        0.85,
        f"window = {row['horizon_window']['window_id']} / rung = {row['stress_ladder_rung']}",
        fontsize=9.5,
    )
    panel.text(
        0.0,
        0.80,
        f"budget_headroom = {row['budget_surface']['budget_headroom']:.2f}",
        fontsize=9.5,
    )
    panel.text(
        0.0,
        0.75,
        f"boundary->loop = {row['linked_trace_continuity']['boundary_to_loop_feedback']['continuity_score']:.3f}",
        fontsize=9.5,
    )
    y = 0.67
    panel.text(0.0, y, "Notes", fontsize=11, fontweight="bold")
    y -= 0.045
    for note in notes:
        panel.text(0.0, y, f"- {note}", fontsize=9.0, va="top", wrap=True)
        y -= 0.085
    if side_rows:
        y -= 0.02
        panel.text(0.0, y, "Controls / limits", fontsize=11, fontweight="bold")
        y -= 0.05
        for side_row in side_rows:
            panel.text(
                0.0,
                y,
                f"{side_row['row_decision']}: {side_row['stress_id'].replace('i8_l5_', '')}",
                fontsize=8.4,
                color=decision_color(side_row["row_decision"]),
                va="top",
                wrap=True,
            )
            y -= 0.075

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=130)
    plt.close(figure)


def build_geometry_graph(geometry_row: dict[str, Any]) -> nx.Graph:
    graph = nx.Graph()
    for node, side in geometry_row["boundary_side_assignments"].items():
        graph.add_node(node, side=side)
    for edge in geometry_row["boundary_edges"]:
        graph.add_edge(
            edge["left"],
            edge["right"],
            event=edge["event"],
            weight=edge["weight"],
            left_side=edge["left_side"],
            right_side=edge["right_side"],
        )
    return graph


def geometry_node_color(node: str, side: str) -> str:
    if node == "b4_c5_medium":
        return "#80b1d3"
    if side == "derived_internal_side":
        return "#8dd3c7"
    return "#d9b56f"


def draw_geometry_frame(
    *,
    geometry_row: dict[str, Any],
    i8_row: dict[str, Any],
    title: str,
    subtitle: str,
    notes: list[str],
    output_path: Path,
    active_events: set[str] | None = None,
    show_i8_overlay: bool = False,
) -> None:
    active_events = active_events or set()
    graph = build_geometry_graph(geometry_row)
    probe = geometry_row["boundary_surface"]["probe_decomposition"]
    metrics = geometry_row["source_current"]["challenge_transform"]["metrics"]
    challenge = geometry_row["source_current"]["challenge_profile"]

    figure = plt.figure(figsize=(14, 8), facecolor="#f8f8f5")
    axis = figure.add_axes((0.035, 0.08, 0.64, 0.82))
    panel = figure.add_axes((0.71, 0.08, 0.26, 0.82))
    axis.set_axis_off()
    panel.set_axis_off()

    axis.add_patch(
        Ellipse(
            (-1.75, 0.32),
            width=2.25,
            height=1.55,
            facecolor="#8dd3c7",
            edgecolor="#277467",
            alpha=0.20,
            linewidth=1.8,
            zorder=0,
        )
    )
    axis.add_patch(
        Ellipse(
            (0.6, 0.28),
            width=1.05,
            height=1.12,
            facecolor="#80b1d3",
            edgecolor="#2a6f9e",
            alpha=0.22,
            linewidth=1.8,
            zorder=0,
        )
    )
    axis.add_patch(
        Ellipse(
            (2.05, 0.24),
            width=1.22,
            height=1.55,
            facecolor="#d9b56f",
            edgecolor="#8c6d31",
            alpha=0.22,
            linewidth=1.8,
            zorder=0,
        )
    )

    axis.text(-2.72, 1.25, "basin A / derived internal side", fontsize=10, fontweight="bold")
    axis.text(0.08, 1.10, "shared medium", fontsize=10, fontweight="bold")
    axis.text(1.48, 1.25, "neighbor basin / external side", fontsize=10, fontweight="bold")

    node_colors = [
        geometry_node_color(node, graph.nodes[node]["side"])
        for node in graph.nodes
    ]
    edge_colors = [
        "#1b9e77" if graph.edges[edge]["event"] == "shared_medium_boundary_exchange" else "#8c6d31"
        for edge in graph.edges
    ]
    edge_widths = [
        5.0 if graph.edges[edge]["event"] in active_events else 2.8
        for edge in graph.edges
    ]

    nx.draw_networkx_edges(
        graph,
        GEOMETRY_POSITIONS,
        ax=axis,
        edge_color=edge_colors,
        width=edge_widths,
        style="solid",
    )
    nx.draw_networkx_nodes(
        graph,
        GEOMETRY_POSITIONS,
        ax=axis,
        node_size=2700,
        node_color=node_colors,
        edgecolors="#333333",
        linewidths=1.5,
    )
    nx.draw_networkx_labels(
        graph,
        GEOMETRY_POSITIONS,
        labels=GEOMETRY_LABELS,
        ax=axis,
        font_size=10,
        font_weight="bold",
    )

    edge_labels = {}
    for source, target, data in graph.edges(data=True):
        if data["event"] == "shared_medium_boundary_exchange":
            edge_labels[(source, target)] = f"A-medium\nw={data['weight']:.2f}"
        else:
            edge_labels[(source, target)] = f"neighbor-medium\nw={data['weight']:.2f}"
    nx.draw_networkx_edge_labels(
        graph,
        GEOMETRY_POSITIONS,
        edge_labels=edge_labels,
        ax=axis,
        font_size=8.5,
        bbox={"boxstyle": "round,pad=0.18", "fc": "#f8f8f5", "ec": "none", "alpha": 0.88},
    )

    axis.annotate(
        f"shared-medium pressure {challenge['shared_medium_pressure']:.2f}",
        xy=GEOMETRY_POSITIONS["b4_c5_medium"],
        xytext=(0.05, -1.02),
        arrowprops={"arrowstyle": "->", "color": "#2a6f9e", "lw": 2.0},
        fontsize=9.5,
        color="#1f4f71",
    )
    axis.annotate(
        f"leakage {probe['shared_medium_leakage']:.3f}",
        xy=GEOMETRY_POSITIONS["b4_c5_neighbor0"],
        xytext=(1.30, -0.88),
        arrowprops={"arrowstyle": "->", "color": "#8c6d31", "lw": 1.8},
        fontsize=9.5,
        color="#6f541d",
    )

    axis.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=14)
    axis.text(-2.9, -1.38, subtitle, fontsize=10, color="#333333")
    axis.set_xlim(-3.05, 2.92)
    axis.set_ylim(-1.55, 1.58)

    panel.text(0.0, 0.98, "B4/C5 source geometry", fontsize=12, fontweight="bold", va="top")
    panel.text(0.0, 0.91, f"source row = {geometry_row['row_id']}", fontsize=9.3)
    panel.text(0.0, 0.86, f"basin_count = {geometry_row['basin_count']}", fontsize=9.3)
    panel.text(0.0, 0.81, f"basin_separation = {geometry_row['basin_separation_score']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.76, f"boundary_exclusivity = {geometry_row['boundary_exclusivity_score']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.71, f"shared_medium_leakage = {geometry_row['shared_medium_leakage']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.66, f"neighbor_leakage = {geometry_row['leakage_into_neighbor_basin']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.61, f"merge_pressure = {geometry_row['merge_confusion_pressure']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.56, f"internal_coherence = {metrics['internal_coherence']:.3f}", fontsize=9.3)
    panel.text(0.0, 0.51, f"retained_flux = {metrics['retained_flux']:.3f}", fontsize=9.3)

    if show_i8_overlay:
        panel.text(0.0, 0.44, "I8 h4/L5 overlay", fontsize=11, fontweight="bold")
        panel.text(
            0.0,
            0.39,
            f"boundary->loop = {i8_row['linked_trace_continuity']['boundary_to_loop_feedback']['continuity_score']:.3f}",
            fontsize=9.3,
        )
        panel.text(0.0, 0.34, f"budget_headroom = {i8_row['budget_surface']['budget_headroom']:.2f}", fontsize=9.3)
        panel.text(0.0, 0.29, f"row_decision = {i8_row['row_decision']}", fontsize=9.3, color=decision_color(i8_row["row_decision"]), fontweight="bold")
        y = 0.21
    else:
        y = 0.44

    panel.text(0.0, y, "Notes", fontsize=11, fontweight="bold")
    y -= 0.045
    for note in notes:
        panel.text(0.0, y, f"- {note}", fontsize=8.7, va="top", wrap=True)
        y -= 0.082

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=130)
    plt.close(figure)


def render_sequence(frame_paths: list[Path], output_path: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in frame_paths]
    width, height = images[0].size
    thumb_width = width // 2
    thumb_height = height // 2
    thumbs = [image.resize((thumb_width, thumb_height)) for image in images]
    sheet = Image.new("RGB", (thumb_width * 2, thumb_height * 3), "#f8f8f5")
    for index, image in enumerate(thumbs):
        x = (index % 2) * thumb_width
        y = (index // 2) * thumb_height
        sheet.paste(image, (x, y))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def render_animation(frame_paths: list[Path], output_path: Path) -> None:
    frames = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in frame_paths]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1250,
        loop=0,
        optimize=False,
    )


def render_report(manifest: dict[str, Any]) -> None:
    lines = [
        "# N18 Iteration 8 Shared-Medium Visualization",
        "",
        "This is a supporting artifact-level visualization for N18 Iteration 8.",
        "It is not a native LGRC telemetry run and does not create new evidence.",
        "",
        "Generated artifacts:",
        "",
        f"- Stress relation graph: `{manifest['artifacts']['static_graph']}`",
        f"- Stress sequence panel: `{manifest['artifacts']['sequence_panel']}`",
        f"- Stress animation: `{manifest['artifacts']['animation']}`",
        f"- B4/C5 source geometry graph: `{manifest['artifacts']['geometry_graph']}`",
        f"- B4/C5 source geometry sequence panel: `{manifest['artifacts']['geometry_sequence_panel']}`",
        f"- B4/C5 source geometry animation: `{manifest['artifacts']['geometry_animation']}`",
        f"- Manifest: `{rel(MANIFEST_PATH)}`",
        "",
        "Renderer boundary:",
        "",
        "```text",
        manifest["renderer_boundary"],
        "```",
        "",
        "Summary:",
        "",
        "```json",
        json.dumps(manifest["visual_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "Geometry summary:",
        "",
        "```json",
        json.dumps(manifest["geometry_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "Claim boundary:",
        "",
        "```text",
        manifest["claim_boundary"],
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    source = load_json(SOURCE_ARTIFACT)
    geometry_source = load_json(N16_GEOMETRY_SOURCE)
    row_01 = row_by_id(source, "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded")
    row_02 = row_by_id(source, "n18_i8_row_02_h4_shared_medium_merge_pressure_limit")
    row_03 = row_by_id(source, "n18_i8_row_03_h4_shared_medium_budget_limit")
    row_04 = row_by_id(source, "n18_i8_row_04_h4_compound_shared_medium_limit")
    row_05 = row_by_id(source, "n18_i8_row_05_b4c5_original_reverse_replay_relabel_control")
    row_06 = row_by_id(source, "n18_i8_row_06_derived_paired_as_original_b4c5_relabel_control")
    row_07 = row_by_id(source, "n18_i8_row_07_resource_shared_medium_merge_relabel_control")
    geometry_row = row_by_id(geometry_source, "n16_i6_row_b4_c5")

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    frame_specs = [
        (
            row_01,
            "Frame 1 - AP3-AP7 stack before shared-medium stress",
            "The artifact-level closure stack is already horizon-bounded at h4.",
            [
                "support, memory, regulation, selection, proxy, boundary, and loop feedback are represented",
                "visualization uses I8 source rows; it is not native telemetry",
            ],
            {"support_to_regulation", "regulation_to_selection", "memory_context_to_selection"},
            [],
        ),
        (
            row_01,
            "Frame 2 - Shared-medium pressure enters boundary channel",
            "Shared-medium stress is introduced without changing h4 or budget policy.",
            [
                "shared medium pressure is routed through boundary separability",
                "claim boundary blocks resource/shared-medium relabeling",
            ],
            {"shared_medium_pressure", "proxy_to_boundary"},
            [],
        ),
        (
            row_01,
            "Frame 3 - Minimal positive shared-medium row",
            "The row passes exactly at the loop-feedback floor.",
            [
                "boundary_to_loop_feedback = 0.800",
                "budget_headroom = 0.01",
                "AP8 remains false pending I9/I10 classification",
            ],
            {"boundary_to_loop_feedback", "closure_return", "budget_surface"},
            [],
        ),
        (
            row_02,
            "Frame 4 - Merge pressure limit",
            "Merge pressure makes the row partial rather than supported.",
            [
                "boundary and loop feedback drop below the 0.800 floor",
                "partial rows remain requirement limits",
            ],
            {"shared_medium_pressure", "neighbor_leakage", "boundary_to_loop_feedback"},
            [row_02],
        ),
        (
            row_04,
            "Frame 5 - Compound shared-medium failure",
            "Compound stress fails closed instead of widening the envelope.",
            [
                "budget is invalid and trace axes fall below floor",
                "failed rows are not positive AP8 evidence",
            ],
            {"shared_medium_pressure", "budget_surface", "boundary_to_loop_feedback"},
            [row_03, row_04],
        ),
        (
            row_01,
            "Frame 6 - I8 handoff state",
            "The useful result is narrow, local, and bottleneck-aware.",
            [
                "minimal shared-medium separability is supported",
                "B4/C5 and derived-as-original relabels remain blocked",
                "boundary_to_loop_feedback is preserved as I9 bottleneck",
            ],
            {"claim_gate", "boundary_to_loop_feedback", "closure_return"},
            [row_05, row_06, row_07],
        ),
    ]

    frame_paths: list[Path] = []
    for index, (row, title, subtitle, notes, active_edges, side_rows) in enumerate(frame_specs):
        frame_path = FRAMES_DIR / f"n18_i8_shared_medium_frame_{index:02d}.png"
        draw_visual_frame(
            row=row,
            title=title,
            subtitle=subtitle,
            notes=notes,
            output_path=frame_path,
            active_edges=active_edges,
            side_rows=side_rows,
        )
        frame_paths.append(frame_path)

    draw_visual_frame(
        row=row_01,
        title="N18 I8 shared-medium stress graph",
        subtitle="Static source-backed visualization of the minimal positive I8 row.",
        notes=[
            "supported row is valid only at h4/L5",
            "boundary_to_loop_feedback sits exactly at the 0.800 floor",
            "visualization is supporting interpretation, not new evidence",
        ],
        output_path=GRAPH_PATH,
        active_edges={"shared_medium_pressure", "boundary_to_loop_feedback", "closure_return"},
        side_rows=[row_02, row_03, row_04],
    )
    render_sequence(frame_paths, SEQUENCE_PATH)
    render_animation(frame_paths, ANIMATION_PATH)

    GEOMETRY_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    geometry_frame_specs = [
        (
            "Frame 1 - B4/C5 source side assignments",
            "The geometry graph starts from recorded N16 side assignments, not from stress-stage axes.",
            [
                "basin A nodes are the derived internal side",
                "shared medium and neighbor nodes are the derived external side",
                "group hulls are visual aids; side assignments are source-backed",
            ],
            set(),
            False,
        ),
        (
            "Frame 2 - Recorded B4/C5 boundary exchanges",
            "Only the two serialized boundary exchange edges are drawn as source geometry edges.",
            [
                "A2 exchanges with the shared medium at weight 0.10",
                "neighbor0 exchanges with the shared medium at weight 0.08",
                "the original B4/C5 source remains one-sided",
            ],
            {"shared_medium_boundary_exchange", "neighbor_medium_exchange"},
            False,
        ),
        (
            "Frame 3 - Shared-medium separability metrics",
            "The source geometry remains separable under the recorded C5 pressure.",
            [
                "basin separation and boundary exclusivity sit above their floors",
                "shared-medium leakage and merge pressure remain below ceilings",
                "neighbor leakage is measured separately from retained flux",
            ],
            {"shared_medium_boundary_exchange", "neighbor_medium_exchange"},
            False,
        ),
        (
            "Frame 4 - N18 I8 h4/L5 stress overlay",
            "I8 overlays long-horizon stress on the B4/C5 source geometry without changing the geometry source.",
            [
                "I8 preserves h4/L5 and keeps AP8 provisional before closeout",
                "boundary_to_loop_feedback is the limiting 0.800 link",
                "the overlay is interpretation, not native telemetry",
            ],
            {"shared_medium_boundary_exchange"},
            True,
        ),
    ]
    geometry_frame_paths: list[Path] = []
    for index, (title, subtitle, notes, active_events, show_i8_overlay) in enumerate(geometry_frame_specs):
        frame_path = GEOMETRY_FRAMES_DIR / f"n18_i8_b4c5_source_geometry_frame_{index:02d}.png"
        draw_geometry_frame(
            geometry_row=geometry_row,
            i8_row=row_01,
            title=title,
            subtitle=subtitle,
            notes=notes,
            output_path=frame_path,
            active_events=active_events,
            show_i8_overlay=show_i8_overlay,
        )
        geometry_frame_paths.append(frame_path)

    draw_geometry_frame(
        geometry_row=geometry_row,
        i8_row=row_01,
        title="N18 I8 B4/C5 source geometry graph",
        subtitle="Source-backed geometry substrate used by the shared-medium stress interpretation.",
        notes=[
            "renders recorded B4/C5 nodes, side assignments, and boundary edges",
            "metrics come from the N16 selected interaction probe",
            "I8 overlay preserves the h4/L5 bottleneck rather than adding geometry",
        ],
        output_path=GEOMETRY_GRAPH_PATH,
        active_events={"shared_medium_boundary_exchange", "neighbor_medium_exchange"},
        show_i8_overlay=True,
    )
    render_sequence(geometry_frame_paths, GEOMETRY_SEQUENCE_PATH)
    render_animation(geometry_frame_paths, GEOMETRY_ANIMATION_PATH)

    artifacts = {
        "static_graph": rel(GRAPH_PATH),
        "sequence_panel": rel(SEQUENCE_PATH),
        "animation": rel(ANIMATION_PATH),
        "frames": [rel(path) for path in frame_paths],
        "geometry_graph": rel(GEOMETRY_GRAPH_PATH),
        "geometry_sequence_panel": rel(GEOMETRY_SEQUENCE_PATH),
        "geometry_animation": rel(GEOMETRY_ANIMATION_PATH),
        "geometry_frames": [rel(path) for path in geometry_frame_paths],
    }
    file_hashes = {
        key: sha256_file(ROOT / path)
        for key, path in artifacts.items()
        if isinstance(path, str)
    }
    file_hashes["frames"] = {
        rel(path): sha256_file(path)
        for path in frame_paths
    }
    file_hashes["geometry_frames"] = {
        rel(path): sha256_file(path)
        for path in geometry_frame_paths
    }
    manifest = {
        "artifact_id": "n18_iteration8_shared_medium_visualization",
        "status": "passed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "source_artifact": rel(SOURCE_ARTIFACT),
        "source_sha256": sha256_file(SOURCE_ARTIFACT),
        "source_geometry_artifact": rel(N16_GEOMETRY_SOURCE),
        "source_geometry_sha256": sha256_file(N16_GEOMETRY_SOURCE),
        "artifacts": artifacts,
        "artifact_sha256": file_hashes,
        "renderer_reuse": {
            "reused_libraries": ["matplotlib", "networkx", "PIL"],
            "direct_pygrc_graph_checkpoint_renderer_used": False,
            "reason": (
                "N18 Iteration 8 is an artifact-level stress matrix and does "
                "not contain native LGRC telemetry graph checkpoints."
            ),
        },
        "renderer_boundary": (
            "supporting artifact-level visualization only; animation shows "
            "source-row/phase progression from the I8 matrix plus B4/C5 source geometry, "
            "not native LGRC runtime execution"
        ),
        "claim_boundary": (
            "does not add evidence, does not open AP8, does not open Phase 8, "
            "does not support agency or native support"
        ),
        "visual_summary": {
            "iteration": 8,
            "positive_row": row_01["row_id"],
            "positive_row_decision": row_01["row_decision"],
            "max_supported_horizon": "h4",
            "highest_positive_stress_ladder_rung": "L5",
            "boundary_to_loop_feedback_score": row_01["linked_trace_continuity"]["boundary_to_loop_feedback"]["continuity_score"],
            "budget_headroom": row_01["budget_surface"]["budget_headroom"],
            "limit_rows": {
                row_02["row_id"]: row_02["row_decision"],
                row_03["row_id"]: row_03["row_decision"],
                row_04["row_id"]: row_04["row_decision"],
            },
            "relabel_controls": {
                row_05["row_id"]: row_05["row_decision"],
                row_06["row_id"]: row_06["row_decision"],
                row_07["row_id"]: row_07["row_decision"],
            },
        },
        "geometry_summary": {
            "geometry_source_row": geometry_row["row_id"],
            "geometry_source_status": "source_backed_artifact_geometry",
            "basin_count": geometry_row["basin_count"],
            "nodes": geometry_row["boundary_side_assignments"],
            "boundary_edges": geometry_row["boundary_edges"],
            "basin_separation_score": geometry_row["basin_separation_score"],
            "boundary_exclusivity_score": geometry_row["boundary_exclusivity_score"],
            "shared_medium_pressure": geometry_row["source_current"]["challenge_profile"]["shared_medium_pressure"],
            "shared_medium_leakage": geometry_row["shared_medium_leakage"],
            "leakage_into_neighbor_basin": geometry_row["leakage_into_neighbor_basin"],
            "merge_confusion_pressure": geometry_row["merge_confusion_pressure"],
            "i8_overlay_row": row_01["row_id"],
            "i8_overlay_role": "h4_L5_stress_overlay_not_geometry_source",
            "native_lgrc_runtime_geometry_checkpoint_available": False,
        },
        "output_digest": "pending",
    }
    digest_input = dict(manifest)
    digest_input.pop("output_digest", None)
    manifest["output_digest"] = digest_value(digest_input)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    render_report(manifest)


if __name__ == "__main__":
    main()
