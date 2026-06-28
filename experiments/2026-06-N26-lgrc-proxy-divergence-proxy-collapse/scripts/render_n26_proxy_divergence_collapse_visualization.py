#!/usr/bin/env python3
"""Render supporting visuals for N26 proxy divergence / proxy collapse."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SOURCE_DIVERGENCE = OUTPUTS / "n26_same_route_score_dose_divergence_probe.json"
SOURCE_COLLAPSE = OUTPUTS / "n26_proxy_collapse_perturbation_matrix.json"
SOURCE_REPLAY = OUTPUTS / "n26_replay_controls_and_ap5_gate.json"
SOURCE_CLOSEOUT = OUTPUTS / "n26_closeout_and_n27_handoff.json"
VISUAL_DIR = OUTPUTS / "n26_proxy_divergence_collapse_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
MANIFEST_PATH = OUTPUTS / "n26_proxy_divergence_collapse_visualization.json"
REPORT_PATH = REPORTS / "n26_proxy_divergence_collapse_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n26_proxy_divergence_collapse_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n26_proxy_divergence_collapse_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n26_proxy_divergence_collapse_animation.gif"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
    "scripts/render_n26_proxy_divergence_collapse_visualization.py"
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


def divergence_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("score_dose_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("N26 divergence source must contain score_dose_rows")
    return [row for row in rows if isinstance(row, dict)]


def collapse_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("proxy_collapse_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("N26 collapse source must contain proxy_collapse_rows")
    return [row for row in rows if isinstance(row, dict)]


def sink_label(row: dict[str, Any]) -> str:
    scope = str(row.get("multi_basin_scope_id", "sink"))
    if "sink0" in scope:
        return "sink 0"
    if "sink2" in scope:
        return "sink 2"
    return scope.replace("_", " ")


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("substrate", label="scoped MB6\nsubstrate")
    graph.add_node("proxy", label="producer-mediated\nproxy score")
    graph.add_node("basin", label="basin persistence\ncapacity")
    graph.add_node("divergence", label="proxy improves;\nbasin stalls")
    graph.add_node("proxy_path", label="proxy-optimized\npath")
    graph.add_node("basin_path", label="basin-deepened\npath")
    graph.add_node("perturbation", label="shared\nperturbation")
    graph.add_node("collapse", label="proxy path\ncollapses")
    graph.add_node("survival", label="basin path\nsurvives")
    graph.add_node("controls", label="replay/control\nmatrix")
    graph.add_node("ap5", label="AP5 bridge:\nscoped only")
    graph.add_node("n27", label="N27\nhandoff")
    graph.add_edges_from(
        [
            ("substrate", "proxy"),
            ("substrate", "basin"),
            ("proxy", "divergence"),
            ("basin", "divergence"),
            ("divergence", "proxy_path"),
            ("divergence", "basin_path"),
            ("proxy_path", "perturbation"),
            ("basin_path", "perturbation"),
            ("perturbation", "collapse"),
            ("perturbation", "survival"),
            ("collapse", "controls"),
            ("survival", "controls"),
            ("controls", "ap5"),
            ("ap5", "n27"),
        ]
    )
    return graph


def graph_positions() -> dict[str, tuple[float, float]]:
    return {
        "substrate": (-3.15, 0.0),
        "proxy": (-1.65, 1.05),
        "basin": (-1.65, -1.05),
        "divergence": (0.0, 0.0),
        "proxy_path": (1.55, 1.05),
        "basin_path": (1.55, -1.05),
        "perturbation": (3.0, 0.0),
        "collapse": (4.45, 1.05),
        "survival": (4.45, -1.05),
        "controls": (5.95, 0.0),
        "ap5": (7.35, 0.85),
        "n27": (7.35, -0.85),
    }


def node_color(node: str) -> str:
    if node == "substrate":
        return "#6baed6"
    if node == "proxy":
        return "#f0c419"
    if node == "basin":
        return "#2ca25f"
    if node == "divergence":
        return "#fdae6b"
    if node == "proxy_path" or node == "collapse":
        return "#d95f02"
    if node == "basin_path" or node == "survival":
        return "#74c476"
    if node == "perturbation":
        return "#9e9ac8"
    if node == "controls":
        return "#756bb1"
    if node == "ap5":
        return "#fb6a4a"
    if node == "n27":
        return "#bdd7e7"
    return "#e6f2ef"


def draw_graph(
    divergence: list[dict[str, Any]],
    collapse: list[dict[str, Any]],
    closeout: dict[str, Any],
    path: Path,
) -> None:
    graph = build_graph()
    pos = graph_positions()
    labels = nx.get_node_attributes(graph, "label")
    final_pd = closeout["final_pd_status"]
    final_ap5 = closeout["final_ap5_status"]

    fig, ax = plt.subplots(figsize=(14.0, 7.0), facecolor="#f8f7f2")
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
        connectionstyle="arc3,rad=0.05",
    )
    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=[node_color(node) for node in graph.nodes],
        node_size=[3300 if node in {"divergence", "perturbation", "controls"} else 2850 for node in graph.nodes],
        edgecolors="#263238",
        linewidths=1.3,
    )
    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        ax=ax,
        font_size=8.8,
        font_weight="bold",
        font_color="#1f1f1f",
    )

    proxy_delta = divergence[0]["proxy_delta"]
    basin_delta = divergence[0]["basin_delta"]
    basin_support = collapse[0]["basin_support_advantage"]
    proxy_advantage = collapse[0]["proxy_score_advantage"]
    row_note = ", ".join(sink_label(row) for row in divergence)
    ax.text(
        -3.55,
        2.25,
        "N26 proxy divergence / proxy collapse",
        ha="left",
        va="center",
        fontsize=16,
        fontweight="bold",
        color="#263238",
    )
    ax.text(
        -3.55,
        1.96,
        f"rows: {row_note} | proxy delta {proxy_delta:.2f} | basin delta {basin_delta:.2f} | "
        f"basin support advantage {basin_support:.2f}",
        ha="left",
        va="center",
        fontsize=10,
        color="#455a64",
    )
    ax.text(
        -3.55,
        -2.02,
        f"Final rung: {final_pd['final_supported_pd_ladder_rung']}",
        ha="left",
        va="center",
        fontsize=9,
        color="#263238",
    )
    ax.text(
        -3.55,
        -2.28,
        "Scoped artifact AP5 bridge candidate supported; native AP5 and AP5 NAT4 gap resolution remain blocked.",
        ha="left",
        va="center",
        fontsize=9,
        color="#7f3b08",
    )
    ax.text(
        1.15,
        2.15,
        f"proxy score advantage {proxy_advantage:.2f}",
        ha="left",
        va="center",
        fontsize=9,
        color="#7f3b08",
    )
    ax.text(
        4.0,
        2.15,
        "proxy path survives = false",
        ha="left",
        va="center",
        fontsize=9,
        color="#a63603",
    )
    ax.text(
        4.0,
        -2.0,
        "basin-deepened path survives = true",
        ha="left",
        va="center",
        fontsize=9,
        color="#238b45",
    )
    ax.text(
        5.85,
        -2.28,
        f"AP5 NAT4 resolved = {str(final_ap5['ap5_nat4_gap_resolved']).lower()}",
        ha="left",
        va="center",
        fontsize=9,
        color="#7f3b08",
    )
    ax.set_axis_off()
    ax.set_xlim(-3.85, 8.05)
    ax.set_ylim(-2.55, 2.5)
    fig.tight_layout(pad=0.5)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def draw_frame(
    divergence: list[dict[str, Any]],
    collapse: list[dict[str, Any]],
    closeout: dict[str, Any],
    replay: dict[str, Any],
    frame_index: int,
    path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.2), facecolor="#f8f7f2")
    ax.set_facecolor("#f8f7f2")
    ax.set_axis_off()
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-2.35, 2.15)

    nodes = {
        "substrate": (-2.35, 0.0, "scoped MB6\nsubstrate", "#6baed6"),
        "proxy": (-0.8, 1.0, "proxy\nscore", "#f0c419"),
        "basin": (-0.8, -1.0, "basin\ncapacity", "#2ca25f"),
        "challenge": (0.85, 0.0, "shared\nchallenge", "#9e9ac8"),
        "proxy_path": (2.35, 1.0, "proxy path\nfails", "#d95f02"),
        "basin_path": (2.35, -1.0, "basin path\nsurvives", "#74c476"),
        "claim": (2.35, 0.0, "PD6 / scoped\nAP5 bridge", "#fb6a4a"),
    }
    if frame_index == 0:
        title = "t0: scoped substrate and declared proxy surface"
        active_nodes = {"substrate", "proxy", "basin"}
        active_edges = [("substrate", "proxy"), ("substrate", "basin")]
        note = "N25.2 is consumed only as scoped MB6 substrate."
    elif frame_index == 1:
        title = "t1: proxy divergence"
        active_nodes = {"proxy", "basin", "challenge"}
        active_edges = [("proxy", "challenge"), ("basin", "challenge")]
        note = (
            f"proxy delta {divergence[0]['proxy_delta']:.2f}; "
            f"basin delta {divergence[0]['basin_delta']:.2f}"
        )
    elif frame_index == 2:
        title = "t2: proxy collapse under the same perturbation"
        active_nodes = {"challenge", "proxy_path", "basin_path"}
        active_edges = [("challenge", "proxy_path"), ("challenge", "basin_path")]
        note = "proxy path rejected; basin-deepened path remains inside challenge."
    else:
        title = "t3: replay/control clean closeout"
        active_nodes = {"proxy_path", "basin_path", "claim"}
        active_edges = [("proxy_path", "claim"), ("basin_path", "claim")]
        summary = replay["row_gate_summary"]
        note = (
            f"supported rows {summary['supported_row_count']}/{summary['row_count']}; "
            "native AP5 remains blocked"
        )

    for source, target in active_edges:
        patch = FancyArrowPatch(
            nodes[source][:2],
            nodes[target][:2],
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=2.2,
            color="#4c4c4c",
            connectionstyle="arc3,rad=0.06",
        )
        ax.add_patch(patch)

    for key, (x, y, label, color) in nodes.items():
        if key == "claim" and frame_index < 3:
            continue
        alpha = 1.0 if key in active_nodes else 0.35
        ax.scatter(
            [x],
            [y],
            s=1700,
            c=color,
            edgecolors="#263238",
            linewidths=1.1,
            alpha=alpha,
            zorder=3,
        )
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color="#1f1f1f",
            zorder=4,
        )

    if frame_index == 1:
        ax.add_patch(Rectangle((-3.05, -2.1), 2.4, 0.36, facecolor="#fff7bc", edgecolor="#f0c419"))
    elif frame_index == 2:
        ax.add_patch(Rectangle((-3.05, -2.1), 3.55, 0.36, facecolor="#fee6ce", edgecolor="#d95f02"))
    else:
        ax.add_patch(Rectangle((-3.05, -2.1), 4.25, 0.36, facecolor="#deebf7", edgecolor="#3182bd"))
    ax.text(-2.92, -1.92, note, ha="left", va="center", fontsize=8.5, color="#263238")

    ax.text(-3.15, 1.78, title, ha="left", va="center", fontsize=13, fontweight="bold")
    ax.text(
        -3.15,
        -2.27,
        "Visual support only: no semantic goal, choice, agency, native support, or Phase 8 claim.",
        ha="left",
        va="center",
        fontsize=8.2,
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
                "# N26 Proxy Divergence / Proxy Collapse Visualization",
                "",
                "Supporting visualization for N26 bounded proxy divergence / proxy collapse.",
                "",
                "## Source Artifacts",
                "",
                *[f"- `{source['path']}`" for source in manifest["source_artifacts"]],
                "",
                "## Visual Outputs",
                "",
                f"- Graph: `{rel(GRAPH_PATH)}`",
                f"- Sequence: `{rel(SEQUENCE_PATH)}`",
                f"- Animation: `{rel(ANIMATION_PATH)}`",
                "",
                "## Interpretation",
                "",
                "The graph shows the source-backed contrast: proxy score increases while basin persistence capacity stalls, then the proxy-optimized path fails under the same perturbation where the basin-deepened path survives.",
                "",
                "## Claim Boundary",
                "",
                manifest["claim_boundary"],
                "",
                "The visual is an inspection aid. It does not add evidence beyond the source artifacts and does not support native AP5, AP5 NAT4 gap resolution, semantic goal, choice, agency, native support, sentience, Phase 8 completion, ant ecology, or unscoped multi-basin substrate.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    divergence_source = load_json(SOURCE_DIVERGENCE)
    collapse_source = load_json(SOURCE_COLLAPSE)
    replay_source = load_json(SOURCE_REPLAY)
    closeout_source = load_json(SOURCE_CLOSEOUT)
    divergence = divergence_rows(divergence_source)
    collapse = collapse_rows(collapse_source)

    draw_graph(divergence, collapse, closeout_source, GRAPH_PATH)
    frame_paths = [
        FRAMES_DIR / f"n26_proxy_divergence_collapse_frame_{index:02d}.png"
        for index in range(4)
    ]
    for index, frame_path in enumerate(frame_paths):
        draw_frame(divergence, collapse, closeout_source, replay_source, index, frame_path)
    combine_sequence(frame_paths, SEQUENCE_PATH)
    write_animation(frame_paths, ANIMATION_PATH)

    output_files = [GRAPH_PATH, SEQUENCE_PATH, ANIMATION_PATH, *frame_paths]
    source_artifacts = [
        {"path": rel(SOURCE_DIVERGENCE), "sha256": sha256_file(SOURCE_DIVERGENCE)},
        {"path": rel(SOURCE_COLLAPSE), "sha256": sha256_file(SOURCE_COLLAPSE)},
        {"path": rel(SOURCE_REPLAY), "sha256": sha256_file(SOURCE_REPLAY)},
        {"path": rel(SOURCE_CLOSEOUT), "sha256": sha256_file(SOURCE_CLOSEOUT)},
    ]
    final_pd = closeout_source["final_pd_status"]
    final_ap5 = closeout_source["final_ap5_status"]
    manifest: dict[str, Any] = {
        "artifact_id": "n26_proxy_divergence_collapse_visualization",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "visual_outputs": [
            {"path": rel(path), "sha256": sha256_file(path), "role": path.stem}
            for path in output_files
        ],
        "visualized_divergence_row_ids": [row["row_id"] for row in divergence],
        "visualized_collapse_row_ids": [row["row_id"] for row in collapse],
        "proxy_delta": divergence[0]["proxy_delta"],
        "basin_delta": divergence[0]["basin_delta"],
        "proxy_score_advantage": collapse[0]["proxy_score_advantage"],
        "basin_support_advantage": collapse[0]["basin_support_advantage"],
        "proxy_path_survives_challenge": all(
            row["proxy_path_survives_challenge"] for row in collapse
        ),
        "basin_deepened_path_survives_challenge": all(
            row["basin_deepened_path_survives_challenge"] for row in collapse
        ),
        "final_supported_pd_ladder_rung": final_pd["final_supported_pd_ladder_rung"],
        "final_n26_closeout_rung": closeout_source["final_closeout_status"][
            "final_n26_closeout_rung"
        ],
        "scoped_artifact_ap5_bridge_candidate_supported": final_ap5[
            "scoped_artifact_ap5_bridge_candidate_supported"
        ],
        "native_ap5_bridge_supported": final_ap5["native_ap5_bridge_supported"],
        "ap5_nat4_gap_resolved": final_ap5["ap5_nat4_gap_resolved"],
        "claim_boundary": closeout_source["claim_ceiling"],
        "visual_status": "supporting_artifact_level_visualization_only",
        "visual_proof_allowed": False,
        "unsafe_claims_supported": False,
        "renderer_boundary": "visualizes source artifact structure and sequence; does not execute LGRC runtime and does not add native AP5 or agency evidence",
    }
    manifest["output_digest"] = digest_value(manifest)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    write_report(manifest)


if __name__ == "__main__":
    main()
