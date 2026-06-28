#!/usr/bin/env python3
"""Render supporting visuals for N24 surplus-supported optionality."""

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
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SOURCE_PROBE = OUTPUTS / "n24_optional_continuation_set_probe_i5a.json"
SOURCE_CLOSEOUT = OUTPUTS / "n24_closeout_and_n25_handoff.json"
VISUAL_DIR = OUTPUTS / "n24_abundance_optionality_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
MANIFEST_PATH = OUTPUTS / "n24_abundance_optionality_visualization.json"
REPORT_PATH = REPORTS / "n24_abundance_optionality_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n24_abundance_optionality_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n24_abundance_optionality_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n24_abundance_optionality_animation.gif"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/render_n24_abundance_optionality_visualization.py"
)

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "pygrc-matplotlib"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402
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
        raise ValueError("N24 probe has no candidate_rows")
    row = rows[0]
    if not isinstance(row, dict):
        raise TypeError("N24 candidate row must be a JSON object")
    return row


def branch_records(row: dict[str, Any]) -> list[dict[str, Any]]:
    records = row["optional_branch_records"]
    if not isinstance(records, list) or not records:
        raise ValueError("N24 row must contain optional branch records")
    return [record for record in records if isinstance(record, dict)]


def build_graph(row: dict[str, Any]) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("maintenance", label="maintenance\nbasin")
    graph.add_node("surplus", label="surplus\nmargin")
    graph.add_node("optionality", label="optional\nset")
    graph.add_node("flux", label="native flux\nbound")
    graph.add_node("producer", label="producer\nextension")
    graph.add_node("claim", label="claim\nboundary")
    for record in branch_records(row):
        branch_id = str(record["branch_id"])
        graph.add_node(branch_id, label=f"node {record['target_node_id']}\noptional")
        graph.add_edge("maintenance", branch_id)
        graph.add_edge(branch_id, "optionality")
    graph.add_edge("maintenance", "surplus")
    graph.add_edge("optionality", "flux")
    graph.add_edge("producer", "flux")
    graph.add_edge("optionality", "claim")
    graph.add_edge("flux", "claim")
    return graph


def positions(records: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    pos: dict[str, tuple[float, float]] = {
        "maintenance": (-2.6, 0.0),
        "surplus": (-2.6, 1.45),
        "optionality": (1.45, 0.0),
        "flux": (2.95, -1.25),
        "producer": (1.35, -1.95),
        "claim": (3.2, 0.85),
    }
    y_values = [1.2, 0.0, -1.2, -2.1]
    for index, record in enumerate(records):
        pos[str(record["branch_id"])] = (-0.35, y_values[index % len(y_values)])
    return pos


def node_color(node: str) -> str:
    if node == "maintenance":
        return "#2ca25f"
    if node == "surplus":
        return "#74c476"
    if node.startswith("n24_i5a_branch_"):
        return "#6baed6"
    if node == "optionality":
        return "#f0c419"
    if node == "flux":
        return "#d95f02"
    if node == "producer":
        return "#9e9ac8"
    if node == "claim":
        return "#fdae6b"
    return "#e6f2ef"


def draw_graph(row: dict[str, Any], closeout: dict[str, Any], path: Path) -> None:
    records = branch_records(row)
    graph = build_graph(row)
    pos = positions(records)
    labels = nx.get_node_attributes(graph, "label")

    fig, ax = plt.subplots(figsize=(11.6, 7.0), facecolor="#f8f7f2")
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
        node_color=[node_color(node) for node in graph.nodes],
        node_size=[2600 if node.startswith("n24_i5a_branch_") else 3100 for node in graph.nodes],
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
    for record in records:
        x, y = pos[str(record["branch_id"])]
        ax.text(
            x,
            y - 0.46,
            f"support margin {record['support_surplus_margin_after']:.2f}\n"
            f"flux cost {record['optional_flux_cost']:.1f}",
            ha="center",
            va="top",
            fontsize=8,
            color="#263238",
        )
    final = closeout["final_classification"]
    ax.text(
        -3.35,
        2.35,
        "N24 I5-A source-current optional continuation set",
        ha="left",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="#263238",
    )
    ax.text(
        -3.35,
        2.08,
        f"optional continuations: {row['optional_continuation_count']} | "
        f"native closeout: {final['final_ab_ladder_rung']}/{final['final_n24_closeout_rung']}",
        ha="left",
        va="center",
        fontsize=10,
        color="#455a64",
    )
    ax.text(
        -3.35,
        -2.55,
        "N24 closes with native flux debt preserved; producer flux scaffold is a separate extension lane.",
        ha="left",
        va="center",
        fontsize=9,
        color="#7f3b08",
    )
    ax.set_axis_off()
    ax.set_xlim(-3.65, 3.95)
    ax.set_ylim(-2.8, 2.6)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def draw_frame(row: dict[str, Any], closeout: dict[str, Any], frame_index: int, path: Path) -> None:
    records = branch_records(row)
    pos = positions(records)
    fig, ax = plt.subplots(figsize=(7.5, 5.2), facecolor="#f8f7f2")
    ax.set_facecolor("#f8f7f2")
    ax.set_axis_off()
    ax.set_xlim(-3.45, 3.65)
    ax.set_ylim(-2.45, 2.15)

    if frame_index == 0:
        title = "t0: maintenance basin above declared floors"
        active_nodes = {"maintenance", "surplus"}
        active_edges = [("maintenance", "surplus")]
    elif frame_index == 1:
        title = "t1: optional branches are source-current and same-window"
        active_nodes = {"maintenance", "optionality", *[str(record["branch_id"]) for record in records]}
        active_edges = [("maintenance", str(record["branch_id"])) for record in records]
        active_edges.extend((str(record["branch_id"]), "optionality") for record in records)
    else:
        title = "t2: flux debt bounds native claim; producer lane stays separate"
        active_nodes = {"optionality", "flux", "producer", "claim"}
        active_edges = [("optionality", "flux"), ("producer", "flux"), ("flux", "claim")]

    node_labels = {
        "maintenance": "maintenance\nbasin",
        "surplus": "support/coherence\nsurplus",
        "optionality": "optional\nset",
        "flux": "native flux\nbound",
        "producer": "producer\nscaffold",
        "claim": "claim\nboundary",
    }
    node_labels.update(
        {str(record["branch_id"]): f"node {record['target_node_id']}" for record in records}
    )
    all_nodes = [
        "maintenance",
        "surplus",
        *[str(record["branch_id"]) for record in records],
        "optionality",
        "flux",
        "producer",
        "claim",
    ]
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
    for node in all_nodes:
        x, y = pos[node]
        alpha = 1.0 if node in active_nodes else 0.4
        ax.scatter(
            [x],
            [y],
            s=1500 if node.startswith("n24_i5a_branch_") else 1800,
            c=node_color(node),
            edgecolors="#263238",
            linewidths=1.1,
            alpha=alpha,
            zorder=3,
        )
        ax.text(
            x,
            y,
            node_labels[node],
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#1f1f1f",
            zorder=4,
        )

    if frame_index == 0:
        margin = row["residual_support_margin_under_optionality"]
        ax.add_patch(Rectangle((-3.2, -2.18), 2.35, 0.34, facecolor="#e5f5e0", edgecolor="#2ca25f"))
        ax.text(-3.05, -2.01, f"residual support margin {margin:.2f}", fontsize=8.5, va="center")
    elif frame_index == 1:
        ax.add_patch(Rectangle((-3.2, -2.18), 2.95, 0.34, facecolor="#deebf7", edgecolor="#3182bd"))
        ax.text(-3.05, -2.01, "three admissible optional branches", fontsize=8.5, va="center")
    else:
        ax.add_patch(Rectangle((-3.2, -2.18), 3.8, 0.34, facecolor="#fee6ce", edgecolor="#d95f02"))
        ax.text(
            -3.05,
            -2.01,
            f"native bound {closeout['final_classification']['native_flux_leakage_debt']}",
            fontsize=8.5,
            va="center",
        )
    ax.text(-3.25, 1.82, title, ha="left", va="center", fontsize=13, fontweight="bold")
    ax.text(
        -3.25,
        -2.35,
        "Visual support only: no reward, semantic choice, agency, native support, or Phase 8 claim.",
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
        duration=950,
        loop=0,
        optimize=False,
    )


def write_report(manifest: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# N24 Abundance/Optionality Visualization",
                "",
                "Supporting visualization for N24 surplus-supported optionality.",
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
                "The visual is an inspection aid. It does not add evidence beyond the source artifacts and does not support reward maximization, semantic choice, agency, native support, sentience, Phase 8 implementation, or ant ecology implementation.",
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

    draw_graph(row, closeout, GRAPH_PATH)
    frame_paths = [FRAMES_DIR / f"n24_abundance_optionality_frame_{index:02d}.png" for index in range(3)]
    for index, frame_path in enumerate(frame_paths):
        draw_frame(row, closeout, index, frame_path)
    combine_sequence(frame_paths, SEQUENCE_PATH)
    write_animation(frame_paths, ANIMATION_PATH)

    output_files = [GRAPH_PATH, SEQUENCE_PATH, ANIMATION_PATH, *frame_paths]
    source_artifacts = [
        {"path": rel(SOURCE_PROBE), "sha256": sha256_file(SOURCE_PROBE)},
        {"path": rel(SOURCE_CLOSEOUT), "sha256": sha256_file(SOURCE_CLOSEOUT)},
    ]
    final = closeout["final_classification"]
    manifest: dict[str, Any] = {
        "artifact_id": "n24_abundance_optionality_visualization",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "visual_outputs": [
            {"path": rel(path), "sha256": sha256_file(path), "role": path.stem}
            for path in output_files
        ],
        "visualized_row_id": row["row_id"],
        "optional_continuation_count": row["optional_continuation_count"],
        "residual_support_margin_under_optionality": row[
            "residual_support_margin_under_optionality"
        ],
        "residual_coherence_margin_under_optionality": row[
            "residual_coherence_margin_under_optionality"
        ],
        "final_ab_ladder_rung": final["final_ab_ladder_rung"],
        "final_n24_closeout_rung": final["final_n24_closeout_rung"],
        "native_n24_c6_supported": final["native_n24_c6_supported"],
        "producer_mediated_flux_scaffold_supported": final[
            "producer_mediated_flux_scaffold_supported"
        ],
        "claim_boundary": final["final_claim_ceiling"],
        "visual_status": "supporting_artifact_level_visualization_only",
        "visual_proof_allowed": False,
        "unsafe_claims_supported": False,
    }
    manifest["output_digest"] = digest_value(manifest)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    write_report(manifest)


if __name__ == "__main__":
    main()
