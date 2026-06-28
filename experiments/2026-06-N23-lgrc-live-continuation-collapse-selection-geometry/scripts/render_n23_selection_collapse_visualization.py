#!/usr/bin/env python3
"""Render supporting visuals for N23 live-continuation collapse geometry."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SOURCE_PROBE = OUTPUTS / "n23_multibranch_live_set_collapse_probe.json"
SOURCE_CLOSEOUT = OUTPUTS / "n23_closeout_and_n24_handoff.json"
VISUAL_DIR = OUTPUTS / "n23_selection_collapse_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
MANIFEST_PATH = OUTPUTS / "n23_selection_collapse_visualization.json"
REPORT_PATH = REPORTS / "n23_selection_collapse_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n23_selection_collapse_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n23_selection_collapse_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n23_selection_collapse_animation.gif"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/render_n23_selection_collapse_visualization.py"
)

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "pygrc-matplotlib"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402
import networkx as nx  # noqa: E402
from PIL import Image  # noqa: E402


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


def selected_row(probe: dict[str, Any]) -> dict[str, Any]:
    rows = probe.get("candidate_rows", [])
    if not rows:
        raise ValueError("N23 probe has no candidate_rows")
    row = rows[0]
    if not isinstance(row, dict):
        raise TypeError("N23 candidate row must be a JSON object")
    return row


def branch_records(row: dict[str, Any]) -> list[dict[str, Any]]:
    records = row["branch_support_coherence_traces"]["branch_records"]
    if not isinstance(records, list) or not records:
        raise ValueError("N23 row must contain branch support/coherence records")
    return [record for record in records if isinstance(record, dict)]


def branch_label(record: dict[str, Any]) -> str:
    branch_id = str(record["branch_id"])
    return branch_id.replace("branch_edge_", "edge ").replace("_node_", " -> node ")


def build_graph(row: dict[str, Any]) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("source", label="source-current\nlive set")
    graph.add_node("collapse", label="collapse\nselection")
    graph.add_node("continuation", label="selected\ncontinuation")
    graph.add_node("counterfactuals", label="retained\ncounterfactuals")
    graph.add_node("controls", label="fail-closed\ncontrols")
    graph.add_node("claim", label="claim\nboundary")
    selected = row["collapsed_continuation_trace"]["selected_branch_id"]
    for record in branch_records(row):
        branch_id = str(record["branch_id"])
        graph.add_node(branch_id, label=branch_label(record))
        graph.add_edge("source", branch_id)
        graph.add_edge(branch_id, "collapse")
        if branch_id == selected:
            graph.add_edge("collapse", "continuation")
        else:
            graph.add_edge(branch_id, "counterfactuals")
    graph.add_edge("controls", "claim")
    graph.add_edge("collapse", "claim")
    return graph


def node_color(node: str, row: dict[str, Any]) -> str:
    selected = row["collapsed_continuation_trace"]["selected_branch_id"]
    if node == selected or node == "continuation":
        return "#2ca25f"
    if node.startswith("branch_edge_"):
        return "#f0c419"
    if node == "counterfactuals":
        return "#6baed6"
    if node == "claim":
        return "#d95f02"
    if node == "controls":
        return "#756bb1"
    return "#e6f2ef"


def positions(records: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    pos: dict[str, tuple[float, float]] = {
        "source": (-3.2, 0.0),
        "collapse": (1.15, 0.0),
        "continuation": (3.2, 0.85),
        "counterfactuals": (3.2, -0.85),
        "controls": (0.0, -2.0),
        "claim": (2.3, -2.0),
    }
    y_values = [1.35, 0.45, -0.45, -1.35, -2.25]
    for index, record in enumerate(records):
        pos[str(record["branch_id"])] = (-1.15, y_values[index % len(y_values)])
    return pos


def draw_graph(row: dict[str, Any], path: Path) -> None:
    graph = build_graph(row)
    records = branch_records(row)
    pos = positions(records)
    labels = nx.get_node_attributes(graph, "label")

    fig, ax = plt.subplots(figsize=(11.5, 7.0), facecolor="#f8f7f2")
    ax.set_facecolor("#f8f7f2")
    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=15,
        edge_color="#4c4c4c",
        width=1.8,
        connectionstyle="arc3,rad=0.04",
    )
    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=[node_color(node, row) for node in graph.nodes],
        node_size=[2600 if node.startswith("branch_edge_") else 3000 for node in graph.nodes],
        edgecolors="#263238",
        linewidths=1.3,
    )
    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        ax=ax,
        font_size=9,
        font_weight="bold",
        font_color="#1f1f1f",
    )
    selected = row["collapsed_continuation_trace"]["selected_branch_id"]
    for record in records:
        x, y = pos[str(record["branch_id"])]
        text = (
            f"score {record['support_gradient_score']}\n"
            f"margin {record['support_floor_margin']:.2f}"
        )
        ax.text(x, y - 0.44, text, ha="center", va="top", fontsize=8, color="#263238")
    ax.text(
        -3.2,
        2.3,
        "N23 I4-A source-current branch set",
        ha="left",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="#263238",
    )
    ax.text(
        -3.2,
        2.05,
        f"selected branch: {selected} | retained non-selected branches: "
        f"{row['branch_counterfactual_records']['retained_non_selected_branch_count']}",
        ha="left",
        va="center",
        fontsize=10,
        color="#455a64",
    )
    ax.text(
        -3.2,
        -2.55,
        "Visual support only: shows source-backed collapse geometry, not semantic choice or agency.",
        ha="left",
        va="center",
        fontsize=9,
        color="#7f3b08",
    )
    ax.set_axis_off()
    ax.set_xlim(-3.85, 4.0)
    ax.set_ylim(-2.8, 2.55)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def draw_frame(row: dict[str, Any], frame_index: int, path: Path) -> None:
    records = branch_records(row)
    pos = positions(records)
    selected = row["collapsed_continuation_trace"]["selected_branch_id"]
    fig, ax = plt.subplots(figsize=(7.5, 5.2), facecolor="#f8f7f2")
    ax.set_facecolor("#f8f7f2")
    ax.set_axis_off()
    ax.set_xlim(-3.7, 3.7)
    ax.set_ylim(-2.45, 2.05)

    if frame_index == 0:
        title = "t0: live branch set emitted"
        active_edges = [("source", str(record["branch_id"])) for record in records]
    elif frame_index == 1:
        title = "t1: support-gradient collapse selects one branch"
        active_edges = [(str(record["branch_id"]), "collapse") for record in records]
        active_edges.append(("collapse", "continuation"))
    else:
        title = "t2: non-selected branches retained as counterfactuals"
        active_edges = [
            (str(record["branch_id"]), "counterfactuals")
            for record in records
            if record["branch_id"] != selected
        ]
        active_edges.append(("controls", "claim"))

    nodes = ["source", "collapse", "continuation", "counterfactuals", "controls", "claim"]
    nodes.extend(str(record["branch_id"]) for record in records)
    labels = {
        "source": "live set",
        "collapse": "collapse",
        "continuation": "selected\ncontinuation",
        "counterfactuals": "counterfactual\nretention",
        "controls": "controls",
        "claim": "claim\nboundary",
    }
    labels.update({str(record["branch_id"]): branch_label(record) for record in records})

    for source, target in active_edges:
        patch = FancyArrowPatch(
            pos[source],
            pos[target],
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=2.2,
            color="#4c4c4c",
            connectionstyle="arc3,rad=0.06",
        )
        ax.add_patch(patch)

    for node in nodes:
        x, y = pos[node]
        alpha = 1.0
        if frame_index == 0 and node in {"collapse", "continuation", "counterfactuals"}:
            alpha = 0.45
        if frame_index == 1 and node in {"counterfactuals", "controls", "claim"}:
            alpha = 0.45
        if frame_index == 2 and node == "continuation":
            alpha = 0.65
        ax.scatter(
            [x],
            [y],
            s=1500 if node.startswith("branch_edge_") else 1800,
            c=node_color(node, row),
            edgecolors="#263238",
            linewidths=1.1,
            alpha=alpha,
            zorder=3,
        )
        ax.text(
            x,
            y,
            labels[node],
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#1f1f1f",
            zorder=4,
        )
    ax.text(-3.45, 1.75, title, ha="left", va="center", fontsize=13, fontweight="bold")
    ax.text(
        -3.45,
        -2.15,
        "LC6 closeout consumes this as bounded collapse/selection geometry; unsafe claims stay blocked.",
        ha="left",
        va="center",
        fontsize=8.5,
        color="#455a64",
    )
    fig.tight_layout(pad=0.4)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def combine_sequence(frame_paths: list[Path], output_path: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in frame_paths]
    widths, heights = zip(*(image.size for image in images), strict=True)
    canvas = Image.new("RGB", (sum(widths), max(heights)), "#f8f7f2")
    x_offset = 0
    for image in images:
        canvas.paste(image, (x_offset, 0))
        x_offset += image.width
    canvas.save(output_path)


def write_animation(frame_paths: list[Path], output_path: Path) -> None:
    images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in frame_paths]
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=900,
        loop=0,
        optimize=False,
    )


def write_report(manifest: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# N23 Selection/Collapse Visualization",
                "",
                "Supporting visualization for the N23 four-branch live-continuation collapse result.",
                "",
                "## Source Artifacts",
                "",
                f"- `{manifest['source_artifacts'][0]['path']}`",
                f"- `{manifest['source_artifacts'][1]['path']}`",
                "",
                "## Visual Outputs",
                "",
                f"- Graph: `{rel(GRAPH_PATH)}`",
                f"- Sequence: `{rel(SEQUENCE_PATH)}`",
                f"- Animation: `{rel(ANIMATION_PATH)}`",
                "",
                "## Claim Boundary",
                "",
                manifest["claim_boundary"],
                "",
                "The visual is an inspection aid. It does not add evidence beyond the source artifacts and does not support semantic choice, agency, native support, sentience, Phase 8 implementation, or ant ecology implementation.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    probe = load_json(SOURCE_PROBE)
    closeout = load_json(SOURCE_CLOSEOUT)
    row = selected_row(probe)

    draw_graph(row, GRAPH_PATH)
    frame_paths = [FRAMES_DIR / f"n23_selection_collapse_frame_{index:02d}.png" for index in range(3)]
    for index, frame_path in enumerate(frame_paths):
        draw_frame(row, index, frame_path)
    combine_sequence(frame_paths, SEQUENCE_PATH)
    write_animation(frame_paths, ANIMATION_PATH)

    output_files = [GRAPH_PATH, SEQUENCE_PATH, ANIMATION_PATH, *frame_paths]
    source_artifacts = [
        {"path": rel(SOURCE_PROBE), "sha256": sha256_file(SOURCE_PROBE)},
        {"path": rel(SOURCE_CLOSEOUT), "sha256": sha256_file(SOURCE_CLOSEOUT)},
    ]
    manifest: dict[str, Any] = {
        "artifact_id": "n23_selection_collapse_visualization",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "visual_outputs": [
            {"path": rel(path), "sha256": sha256_file(path), "role": path.stem}
            for path in output_files
        ],
        "visualized_row_id": row["row_id"],
        "selected_branch_id": row["collapsed_continuation_trace"]["selected_branch_id"],
        "branch_count": row["live_branch_set_trace"]["branch_count"],
        "retained_non_selected_branch_count": row["branch_counterfactual_records"][
            "retained_non_selected_branch_count"
        ],
        "final_supported_lc_ladder_rung": closeout["final_classification"][
            "final_supported_lc_ladder_rung"
        ],
        "final_n23_closeout_ladder_rung": closeout["final_classification"][
            "final_n23_closeout_ladder_rung"
        ],
        "claim_boundary": closeout["final_classification"]["final_claim_ceiling"],
        "visual_status": "supporting_artifact_level_visualization_only",
        "visual_proof_allowed": False,
        "unsafe_claims_supported": False,
    }
    manifest["output_digest"] = digest_value(manifest)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    write_report(manifest)


if __name__ == "__main__":
    main()
