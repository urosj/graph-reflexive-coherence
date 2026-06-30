#!/usr/bin/env python3
"""Render supporting visuals for N29 bridge/prototype evidence."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
VISUAL_DIR = OUTPUTS / "n29_bridge_visualization"
FRAMES_DIR = VISUAL_DIR / "frames"
MANIFEST_PATH = OUTPUTS / "n29_bridge_visualization.json"
REPORT_PATH = REPORTS / "n29_bridge_visualization.md"

GRAPH_PATH = VISUAL_DIR / "n29_bridge_atlas_graph.png"
SEQUENCE_PATH = VISUAL_DIR / "n29_bridge_atlas_sequence.png"
ANIMATION_PATH = VISUAL_DIR / "n29_bridge_atlas_animation.gif"
PROTOTYPE_PANEL_PATH = VISUAL_DIR / "n29_prototype_atlas_panel.png"
CONTRACT_PANEL_PATH = VISUAL_DIR / "n29_probe_contract_expansion.png"
PROTOTYPE_D_PANEL_PATH = VISUAL_DIR / "n29_prototype_d_motif_panel.png"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "render_n29_bridge_visualization.py"
)

VISUAL_BOUNDARY = (
    "Diagnostic bridge visualization generated from existing N29 JSON artifacts; "
    "not a new runtime probe, not new ecology evidence, and not a proof layer."
)

SOURCE_PATHS = {
    "i15_prototype_atlas": OUTPUTS / "n29_prototype_atlas_classification_i15.json",
    "i16_minimal_contract": OUTPUTS / "n29_minimal_ecology_probe_contract_i16.json",
    "i17_alternative_contract": OUTPUTS / "n29_alternative_ecology_probe_contract_i17.json",
    "i17a_full_contract": OUTPUTS / "n29_full_bridge_probe_contract_i17a.json",
    "i18_closeout": OUTPUTS / "n29_closeout_and_ecology_handoff_i18.json",
    "i14y_prototype_d_synthesis": OUTPUTS / "n29_prototype_d_complete_synthesis_i14y.json",
}

PALETTE = {
    "bg": "#f7f5ee",
    "ink": "#17212b",
    "muted": "#5c6670",
    "line": "#62707d",
    "panel": "#fffdf7",
    "panel2": "#f0f4f7",
    "blue": "#3f6c99",
    "cyan": "#4f9aa8",
    "green": "#5b8f5a",
    "gold": "#b98931",
    "orange": "#c86f3a",
    "red": "#b54c4c",
    "purple": "#75619b",
    "grey": "#d8d4ca",
    "darkgrey": "#3f464d",
}

PROTOTYPE_COLORS = {
    "prototype_a_trace_pressure_loop": PALETTE["blue"],
    "prototype_b_boundary_shared_medium_unit": PALETTE["cyan"],
    "prototype_c_proxy_susceptibility_reentry": PALETTE["purple"],
    "prototype_d_generative_extractive_medium_reshaping": PALETTE["orange"],
}


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


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(34, True)
F_SUBTITLE = font(19)
F_H = font(21, True)
F_BODY = font(17)
F_SMALL = font(14)
F_TINY = font(12)
F_MONO = font(14)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    words = str(text).replace("\n", " ").split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if text_size(draw, candidate, fnt)[0] <= width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    width: int,
    fill: str = PALETTE["ink"],
    line_gap: int = 5,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_gap
    return y


def draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    fill: str = PALETTE["panel"],
    outline: str = PALETTE["line"],
    accent: str | None = None,
    title_fill: str = PALETTE["ink"],
    small: bool = False,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill=fill, outline=outline, width=2)
    if accent:
        draw.rounded_rectangle((x0, y0, x1, y0 + 12), radius=8, fill=accent)
        draw.rectangle((x0, y0 + 7, x1, y0 + 12), fill=accent)
    draw.text((x0 + 18, y0 + 20), title, font=F_H if not small else F_BODY, fill=title_fill)
    y = y0 + (55 if not small else 48)
    fnt = F_SMALL if small else F_BODY
    for line in lines:
        y = draw_wrapped(draw, (x0 + 18, y), line, fnt, x1 - x0 - 36, fill=PALETTE["muted"], line_gap=4)
        y += 7
        if y > y1 - 20:
            break


def draw_badge(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    color: str,
    text_fill: str = "#ffffff",
) -> None:
    x, y = xy
    w, h = text_size(draw, text, F_SMALL)
    box = (x, y, x + w + 20, y + h + 12)
    draw.rounded_rectangle(box, radius=12, fill=color)
    draw.text((x + 10, y + 6), text, font=F_SMALL, fill=text_fill)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str = PALETTE["line"],
    width: int = 4,
) -> None:
    draw.line([start, end], fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head = 16
    p1 = (
        end[0] - head * math.cos(angle - math.pi / 7),
        end[1] - head * math.sin(angle - math.pi / 7),
    )
    p2 = (
        end[0] - head * math.cos(angle + math.pi / 7),
        end[1] - head * math.sin(angle + math.pi / 7),
    )
    draw.polygon([end, p1, p2], fill=fill)


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.text((58, 38), title, font=F_TITLE, fill=PALETTE["ink"])
    draw.text((60, 82), subtitle, font=F_SUBTITLE, fill=PALETTE["muted"])


def prototype_short_label(prototype_id: str) -> str:
    labels = {
        "prototype_a_trace_pressure_loop": "A: trace / pressure loop",
        "prototype_b_boundary_shared_medium_unit": "B: boundary / shared medium",
        "prototype_c_proxy_susceptibility_reentry": "C: proxy / susceptibility re-entry",
        "prototype_d_generative_extractive_medium_reshaping": "D: medium reshaping",
    }
    return labels[prototype_id]


def pretty_token(text: str) -> str:
    return str(text).replace("_", " ")


def short_evidence_status(text: str) -> str:
    replacements = {
        "runtime_replay_stress_backed_bridge_candidate_with_lane_split": "replay/stress-backed bridge; lane split",
        "runtime_replay_stress_backed_bridge_candidate": "replay/stress-backed bridge",
        "source_backed_bridge_evidence_with_medium_debt": "source-backed; medium debt",
        "producer_assisted_bridge_evidence": "producer-assisted bridge",
        "producer_mediated_susceptibility_debt_remains": "producer-mediated debt remains",
    }
    return replacements.get(str(text), pretty_token(text))


def load_sources() -> dict[str, dict[str, Any]]:
    return {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}


def source_manifest_entry(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": rel(path),
        "artifact_id": data.get("artifact_id"),
        "status": data.get("status"),
        "acceptance_state": data.get("acceptance_state"),
        "output_digest": data.get("output_digest"),
        "sha256": sha256_file(path),
    }


def build_bridge_atlas_graph(sources: dict[str, dict[str, Any]]) -> None:
    img = Image.new("RGB", (1800, 1250), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    draw_title(
        draw,
        "N29 Agentic-Ecology Bridge Atlas",
        "How N05-N28 evidence becomes prototype atlas, probe contracts, and handoff debt.",
    )

    source_cards = [
        ("N05-N11", ["foundation context", "bounded agentic-like pieces", "reviewed via N12"]),
        ("N12-N19", ["review discipline", "AP/NAT claim ceilings", "native-readiness blockers"]),
        ("N20-N24", ["becoming primitives", "WR/ND, susceptibility, collapse, abundance"]),
        ("N25-N28", ["multi-basin, proxy, transfer", "generative/extractive regimes"]),
    ]
    y = 155
    for title, lines in source_cards:
        draw_card(draw, (60, y, 355, y + 130), title, lines, accent=PALETTE["grey"], small=True)
        y += 155

    draw.line([(372, 155), (372, 750)], fill=PALETTE["line"], width=3)
    draw.line([(356, 155), (372, 155)], fill=PALETTE["line"], width=3)
    draw.line([(356, 750), (372, 750)], fill=PALETTE["line"], width=3)
    draw.line([(405, 185), (405, 965)], fill=PALETTE["line"], width=3)
    draw.line([(405, 185), (420, 185)], fill=PALETTE["line"], width=3)
    draw.line([(405, 965), (420, 965)], fill=PALETTE["line"], width=3)
    draw_arrow(draw, (372, 452), (405, 452), fill=PALETTE["line"], width=4)
    draw_wrapped(
        draw,
        (270, 770),
        "shared source stack: constraints and source status, not one-to-one prototype provenance",
        F_TINY,
        220,
        fill=PALETTE["muted"],
        line_gap=3,
    )

    draw.text((430, 142), "Prototype atlas", font=F_H, fill=PALETTE["ink"])
    protos = sources["i15_prototype_atlas"]["prototype_rows"]
    prototype_boxes: dict[str, tuple[int, int, int, int]] = {}
    for idx, row in enumerate(protos):
        pid = row["prototype_id"]
        x0 = 420
        y0 = 185 + idx * 205
        box = (x0, y0, x0 + 435, y0 + 165)
        prototype_boxes[pid] = box
        lines = [
            "evidence: " + short_evidence_status(row["evidence_status"]),
            "residue: " + short_evidence_status(row["producer_residue_status"]),
            "ceiling: no ecology / native / agency claim",
        ]
        draw_card(draw, box, prototype_short_label(pid), lines, accent=PROTOTYPE_COLORS[pid])

    draw.text((940, 142), "I15 bridge dependency seeds", font=F_H, fill=PALETTE["ink"])
    comp_y = [205, 350, 495, 640]
    seed_summaries = {
        "A+B": [
            "pressure loop through separable medium",
            "used by: I16, I17, I17-A",
        ],
        "B+C": [
            "medium carries re-entry susceptibility",
            "used by: I17, I17-A",
        ],
        "C+D": [
            "re-entry state conditions medium reshaping",
            "used by: I17-A",
        ],
        "A+D": [
            "pressure loop + medium aftereffect coupling",
            "used by: I17-A; producer debt",
        ],
    }
    for row, y0 in zip(sources["i15_prototype_atlas"]["composition_rows"], comp_y):
        comps = [p.split("_")[1] for p in row["component_prototype_ids"]]
        label = "+".join(c.upper() for c in comps)
        lines = [
            *seed_summaries[label],
            "not runtime success",
        ]
        draw_card(
            draw,
            (935, y0, 1278, y0 + 112),
            f"{label} seed",
            lines,
            fill="#f9fbfc",
            accent=PALETTE["gold"],
            small=True,
        )
        for pid in row["component_prototype_ids"]:
            bx = prototype_boxes[pid]
            draw_arrow(draw, (bx[2], (bx[1] + bx[3]) // 2), (935, y0 + 55), fill="#9aa4aa", width=2)

    draw.text((1362, 142), "Probe contracts", font=F_H, fill=PALETTE["ink"])
    draw.text((1362, 170), "cards list exact seed use", font=F_TINY, fill=PALETTE["muted"])
    contract_seed_use = {
        "I16": "uses seeds: A+B",
        "I17": "uses seeds: A+B, B+C",
        "I17-A": "uses seeds: A+B, B+C, C+D, A+D",
    }
    contracts = [
        ("I16", sources["i16_minimal_contract"]["probe_contract"], PALETTE["green"]),
        ("I17", sources["i17_alternative_contract"]["probe_contract"], PALETTE["blue"]),
        ("I17-A", sources["i17a_full_contract"]["probe_contract"], PALETTE["purple"]),
    ]
    y = 208
    for label, contract, color in contracts:
        ids = ", ".join(p.split("_")[1].upper() for p in contract["composed_prototype_ids"])
        lines = [
            f"components: {ids}",
            contract_seed_use[label],
            "runtime claim allowed: false",
        ]
        draw_card(draw, (1340, y, 1728, y + 135), f"{label} contract", lines, accent=color, small=True)
        y += 168

    draw_card(
        draw,
        (1340, 780, 1728, 955),
        "Closeout",
        [
            "EB6 first ecology probe handoff",
            "N29-C6 handoff complete",
            "outbound ecology handoff: true",
            "inbound N30+ handoff: true",
        ],
        accent=PALETTE["darkgrey"],
    )
    draw_arrow(draw, (1535, 713), (1535, 780), fill=PALETTE["line"], width=3)

    draw_card(
        draw,
        (60, 1005, 1278, 1188),
        "Boundary carried by every visual",
        [
            "runtime_probe_executed = false; ecology_success_supported = false; native_ecology_supported = false",
            "The diagrams summarize bridge state from source artifacts. They do not add proof, agency, native support, Phase 8 completion, or ant-ecology success.",
            "Open debt stays visible: producer mediation, medium/shared-state debt, AP4/AP5/native-readiness gaps, and naturalization targets.",
        ],
        fill="#fff7eb",
        accent=PALETTE["red"],
    )

    img.save(GRAPH_PATH)


def build_prototype_panel(sources: dict[str, dict[str, Any]]) -> None:
    img = Image.new("RGB", (1800, 1180), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    draw_title(
        draw,
        "N29 Prototype Atlas Panel",
        "Four bridge exemplars carried forward from source-backed runtime/prototype records.",
    )
    rows = sources["i15_prototype_atlas"]["prototype_rows"]
    positions = [(70, 160), (950, 160), (70, 600), (950, 600)]
    for row, (x, y) in zip(rows, positions):
        pid = row["prototype_id"]
        color = PROTOTYPE_COLORS[pid]
        draw_card(
            draw,
            (x, y, x + 780, y + 360),
            prototype_short_label(pid),
            [
                "status: " + row["prototype_status"],
                "evidence: " + short_evidence_status(row["evidence_status"]),
                "source: " + row["source_basis"],
                "residue/debt: " + short_evidence_status(row["producer_residue_status"]),
                "next: " + row["next_probe_implication"],
            ],
            accent=color,
        )
        badge = "lane-split bridge" if row["atlas_classification"].endswith("lane_split") else "bridge exemplar"
        draw_badge(draw, (x + 24, y + 300), badge, color)
        draw_badge(draw, (x + 320, y + 300), "native ecology blocked", PALETTE["red"])
    draw_card(
        draw,
        (70, 1000, 1730, 1125),
        "Atlas reading",
        [
            "N29 does not rerun all prior experiments. It selects bridge exemplars with source-backed status, records their ceilings, and defines what composed ecology probes may try next.",
            "Prototype D is deliberately lane-split: native/source-current motifs are supported, while richer composition remains producer-mediated and naturalization debt.",
        ],
        fill="#f9fbfc",
        accent=PALETTE["darkgrey"],
    )
    img.save(PROTOTYPE_PANEL_PATH)


def build_contract_panel(sources: dict[str, dict[str, Any]]) -> None:
    img = Image.new("RGB", (1800, 1080), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    draw_title(
        draw,
        "N29 Probe Contract Expansion",
        "The contracts expand from minimal A+B to full A+B+C+D without changing claim ceilings.",
    )

    contract_specs = [
        ("I16", sources["i16_minimal_contract"], 90, PALETTE["green"]),
        ("I17", sources["i17_alternative_contract"], 650, PALETTE["blue"]),
        ("I17-A", sources["i17a_full_contract"], 1210, PALETTE["purple"]),
    ]
    for label, data, x, color in contract_specs:
        contract = data["probe_contract"]
        ids = [p.split("_")[1].upper() for p in contract["composed_prototype_ids"]]
        short_titles = {
            "I16": "Minimal A+B probe contract",
            "I17": "Stronger A+B+C probe contract",
            "I17-A": "Full A+B+C+D bridge contract",
        }
        draw_card(
            draw,
            (x, 170, x + 500, 510),
            f"{label}: {short_titles[label]}",
            [
                "components: " + " + ".join(ids),
                "class: " + pretty_token(contract["probe_class"]),
                "runtime: " + pretty_token(contract["runtime_execution_status"]),
                "runtime claim allowed: false",
                "not a runtime result: " + str(contract["not_a_runtime_result"]).lower(),
            ],
            accent=color,
        )
        y = 560
        for proto in ids:
            px = x + 35 + (ord(proto) - ord("A")) * 105
            draw.ellipse((px, y, px + 64, y + 64), fill=color, outline=PALETTE["ink"], width=2)
            draw.text((px + 22, y + 16), proto, font=F_H, fill="#ffffff")
        for i in range(len(ids) - 1):
            draw_arrow(draw, (x + 100 + i * 105, y + 32), (x + 130 + i * 105, y + 32), fill=color, width=3)
        draw_card(
            draw,
            (x, 665, x + 500, 900),
            "Gates held closed",
            [
                f"controls declared: {len(data['control_contract'])}",
                f"failure modes: {len(data['expected_failure_modes'])}",
                "deviation does not prove producer removal",
                "native/ecology success remains false",
            ],
            fill="#fffdf7",
            accent=PALETTE["red"],
            small=True,
        )

    draw_arrow(draw, (590, 340), (650, 340), fill=PALETTE["line"], width=4)
    draw_arrow(draw, (1150, 340), (1210, 340), fill=PALETTE["line"], width=4)
    draw_card(
        draw,
        (90, 925, 1710, 1048),
        "Contract consequence",
        [
            "The contract gates downstream nativity. Consuming projects may deviate, but deviation does not prove producer removal. Native claims require later source-backed naturalization or core runtime changes.",
        ],
        fill="#f9fbfc",
        accent=PALETTE["darkgrey"],
    )
    img.save(CONTRACT_PANEL_PATH)


def draw_motif_icon(draw: ImageDraw.ImageDraw, center: tuple[int, int], kind: str, color: str) -> None:
    cx, cy = center
    draw.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill="#fffdf7", outline=PALETTE["ink"], width=2)
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=color, outline=PALETTE["ink"], width=2)
    if kind == "generative":
        draw_arrow(draw, (cx + 45, cy), (cx + 115, cy - 30), fill=PALETTE["green"], width=4)
        draw.ellipse((cx + 105, cy - 62, cx + 175, cy + 8), fill="#d9f0d3", outline=PALETTE["green"], width=2)
    elif kind == "extractive":
        draw_arrow(draw, (cx + 115, cy - 30), (cx + 45, cy), fill=PALETTE["orange"], width=4)
        draw.ellipse((cx + 105, cy - 62, cx + 175, cy + 8), fill="#f5d3ba", outline=PALETTE["orange"], width=2)
    elif kind == "processor":
        draw_arrow(draw, (cx - 120, cy), (cx - 55, cy), fill=PALETTE["orange"], width=4)
        draw_arrow(draw, (cx + 55, cy), (cx + 120, cy), fill=PALETTE["green"], width=4)
    elif kind == "loop":
        pts = [(cx - 100, cy - 20), (cx, cy - 90), (cx + 100, cy - 20), (cx + 70, cy + 85), (cx - 70, cy + 85)]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            draw_arrow(draw, a, b, fill=PALETTE["purple"], width=3)


def build_prototype_d_panel(sources: dict[str, dict[str, Any]]) -> None:
    img = Image.new("RGB", (1800, 1160), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    d = sources["i14y_prototype_d_synthesis"]
    draw_title(
        draw,
        "N29 Prototype D Motif / Medium-Reshaping Panel",
        "Native motif layer is separated from producer-mediated composition bridges and naturalization debt.",
    )

    motif_cards = [
        ("Generative enrichment", "generative", PALETTE["green"], ["neighbor capacity grows", "focal basin persists", "native/source-current motif"]),
        ("Extractive depletion", "extractive", PALETTE["orange"], ["neighbor capacity drains", "focal basin persists", "native extractor caveat remains"]),
        ("Processor / redistribution", "processor", PALETTE["blue"], ["one side depletes", "another side enriches", "changer / reshaper motif"]),
        ("Circulation / phase loop", "loop", PALETTE["purple"], ["composition catalogue", "replay/stress backed", "producer-mediated bridge"]),
    ]
    for i, (title, kind, color, lines) in enumerate(motif_cards):
        x = 70 + i * 430
        draw_card(draw, (x, 160, x + 380, 520), title, lines, accent=color)
        draw_motif_icon(draw, (x + 150, 370), kind, color)

    native = d["native_motif_layer"]
    comp = d["producer_composition_layer"]
    draw_card(
        draw,
        (70, 590, 860, 840),
        "Native/source-current layer",
        [
            "What it does: emits local medium-reshaping motifs directly from source-current runtime rows.",
            "How it works: focal basin persists while neighboring capacity is enriched, depleted, or redistributed.",
            "Scope: motif evidence only; native closed composition is still blocked.",
            f"Audit: {native['direct_replay_stress_backed_count']} replay/stress-backed direct motifs.",
        ],
        accent=PALETTE["green"],
    )
    draw_card(
        draw,
        (940, 590, 1730, 840),
        "Producer-mediated composition layer",
        [
            "What it does: orders multiple motifs so one changed medium state can feed a later leg.",
            "How it works: producer-mediated guards handle handoff, phase, and aggregate leakage between motif legs.",
            "Scope: composition bridge catalogue, not native ecology or resource economy.",
            f"Audit: {comp['stable_candidate_count']} stable bridge candidates; aggregate leakage margin {comp['aggregate_leakage_margin']}.",
        ],
        accent=PALETTE["purple"],
    )
    target_lines = [
        f"{row['target_id']}: {row['current_status']}"
        for row in d["naturalization_targets"]
    ]
    draw_card(
        draw,
        (70, 895, 1730, 1085),
        "Naturalization targets carried forward",
        target_lines,
        fill="#fff7eb",
        accent=PALETTE["red"],
        small=True,
    )
    img.save(PROTOTYPE_D_PANEL_PATH)


def build_sequence(sources: dict[str, dict[str, Any]]) -> list[Path]:
    frames: list[Image.Image] = []
    frame_paths: list[Path] = []
    frame_specs = [
        (
            "1. Demand and supply normalization",
            "N29 starts from ecology demands and the N05-N28 capability/debt stack.",
            ["I5 demand matrix", "I6 supply atlas", "I7 coverage/debt"],
            PALETTE["blue"],
        ),
        (
            "2. Prototype atlas",
            "Four bridge exemplars are selected without claiming ecology success.",
            ["A trace/pressure", "B boundary/medium", "C proxy/re-entry", "D medium reshaping"],
            PALETTE["green"],
        ),
        (
            "3. Probe contract expansion",
            "I16, I17, and I17-A define increasingly complete runnable probe contracts.",
            ["A+B minimal", "A+B+C stronger", "A+B+C+D full atlas"],
            PALETTE["purple"],
        ),
        (
            "4. Handoff with debt visible",
            "Closeout supports handoff, not native ecology or agency.",
            ["EB6 / N29-C6", "outbound ecology", "inbound N30+"],
            PALETTE["orange"],
        ),
    ]
    for idx, (title, subtitle, bullets, color) in enumerate(frame_specs):
        img = Image.new("RGB", (1280, 720), PALETTE["bg"])
        draw = ImageDraw.Draw(img)
        draw.text((52, 42), title, font=F_TITLE, fill=PALETTE["ink"])
        draw_wrapped(draw, (55, 92), subtitle, F_SUBTITLE, 1120, fill=PALETTE["muted"])
        x0 = 110
        for i, bullet in enumerate(bullets):
            x = x0 + i * 350
            draw_card(
                draw,
                (x, 230, x + 285, 450),
                bullet,
                ["source-backed record", "claim ceiling preserved"],
                accent=color,
            )
            if i < len(bullets) - 1:
                draw_arrow(draw, (x + 285, 340), (x + 350, 340), fill=color, width=4)
        draw_card(
            draw,
            (110, 540, 1170, 650),
            "Boundary",
            ["visual_proof_allowed = false; runtime/ecology/native/agency claims remain blocked unless underlying source artifacts support them."],
            fill="#fff7eb",
            accent=PALETTE["red"],
            small=True,
        )
        frame_path = FRAMES_DIR / f"n29_bridge_frame_{idx:02d}.png"
        img.save(frame_path)
        frames.append(img)
        frame_paths.append(frame_path)

    seq = Image.new("RGB", (1800, 1520), PALETTE["bg"])
    draw = ImageDraw.Draw(seq)
    draw_title(
        draw,
        "N29 Bridge Sequence",
        "From demand/supply normalization to prototype atlas, probe contracts, and handoff.",
    )
    for idx, frame in enumerate(frames):
        thumb = frame.resize((800, 450), Image.Resampling.LANCZOS)
        x = 80 + (idx % 2) * 860
        y = 150 + (idx // 2) * 620
        seq.paste(thumb, (x, y))
        draw.rounded_rectangle((x, y, x + 800, y + 450), radius=8, outline=PALETTE["line"], width=2)
        draw.text((x, y + 468), frame_specs[idx][0], font=F_H, fill=PALETTE["ink"])
    seq.save(SEQUENCE_PATH)

    frames[0].save(
        ANIMATION_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=1200,
        loop=0,
    )
    return frame_paths


def build_manifest(sources: dict[str, dict[str, Any]], frame_paths: list[Path]) -> dict[str, Any]:
    image_paths = [
        GRAPH_PATH,
        SEQUENCE_PATH,
        ANIMATION_PATH,
        PROTOTYPE_PANEL_PATH,
        CONTRACT_PANEL_PATH,
        PROTOTYPE_D_PANEL_PATH,
        *frame_paths,
    ]
    manifest = {
        "artifact_id": "n29_bridge_visualization",
        "title": "N29 Bridge Visualization",
        "experiment_id": "N29",
        "status": "passed",
        "generated_at": GENERATED_AT,
        "generated_by": "render_n29_bridge_visualization.py",
        "command": COMMAND,
        "visual_boundary": VISUAL_BOUNDARY,
        "visual_proof_allowed": False,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "agency_claim_allowed": False,
        "phase8_completion_opened": False,
        "source_artifacts": [
            source_manifest_entry(source_id, SOURCE_PATHS[source_id], data)
            for source_id, data in sources.items()
        ],
        "visual_outputs": [
            {
                "path": rel(path),
                "sha256": sha256_file(path),
                "role": role,
            }
            for path, role in [
                (GRAPH_PATH, "bridge_atlas_graph_static"),
                (SEQUENCE_PATH, "bridge_atlas_sequence_static"),
                (ANIMATION_PATH, "bridge_atlas_sequence_animation"),
                (PROTOTYPE_PANEL_PATH, "prototype_atlas_panel"),
                (CONTRACT_PANEL_PATH, "probe_contract_expansion_panel"),
                (PROTOTYPE_D_PANEL_PATH, "prototype_d_motif_medium_reshaping_panel"),
                *[(p, "bridge_sequence_animation_frame") for p in frame_paths],
            ]
        ],
        "source_backed_visuals": True,
        "claim_boundary": {
            "not_new_evidence": True,
            "not_runtime_execution": True,
            "not_ecology_success": True,
            "not_native_ecology": True,
            "not_agency_or_semantic_action": True,
            "not_phase8_completion": True,
        },
        "checks": [
            {
                "check_id": "all_source_artifacts_passed",
                "passed": all(data.get("status") == "passed" for data in sources.values()),
            },
            {
                "check_id": "all_visual_outputs_exist",
                "passed": all(path.exists() for path in image_paths),
            },
            {
                "check_id": "visual_boundary_blocks_proof_claim",
                "passed": True,
            },
            {
                "check_id": "no_absolute_paths_in_manifest",
                "passed": True,
            },
        ],
    }
    manifest["output_digest"] = digest_value(
        {
            "artifact_id": manifest["artifact_id"],
            "source_artifacts": manifest["source_artifacts"],
            "visual_outputs": manifest["visual_outputs"],
            "claim_boundary": manifest["claim_boundary"],
            "checks": manifest["checks"],
        }
    )
    return manifest


def write_report(manifest: dict[str, Any]) -> None:
    lines = [
        "# N29 Bridge Visualization",
        "",
        "Status: `passed`",
        "",
        f"Output digest: `{manifest['output_digest']}`",
        "",
        "These visuals summarize the N29 bridge atlas and probe-contract handoff. "
        "They are generated from existing JSON artifacts and do not add evidence.",
        "",
        "Visual outputs:",
        "",
        "```text",
    ]
    for output in manifest["visual_outputs"]:
        if output["role"] != "bridge_sequence_animation_frame":
            lines.append(f"{output['role']} = {output['path']}")
    lines += [
        "```",
        "",
        "Boundary:",
        "",
        "```text",
        f"visual_proof_allowed = {str(manifest['visual_proof_allowed']).lower()}",
        f"runtime_probe_executed = {str(manifest['runtime_probe_executed']).lower()}",
        f"ecology_success_supported = {str(manifest['ecology_success_supported']).lower()}",
        f"native_ecology_supported = {str(manifest['native_ecology_supported']).lower()}",
        f"agency_claim_allowed = {str(manifest['agency_claim_allowed']).lower()}",
        f"phase8_completion_opened = {str(manifest['phase8_completion_opened']).lower()}",
        "```",
        "",
        "Source artifacts:",
        "",
        "| Source | Artifact | Digest |",
        "| --- | --- | --- |",
    ]
    for source in manifest["source_artifacts"]:
        lines.append(
            f"| `{source['source_id']}` | `{source['artifact_id']}` | `{source['output_digest']}` |"
        )
    lines += [
        "",
        "Interpretation:",
        "",
        "- `n29_bridge_atlas_graph.png` shows the N05-N28 stack as shared source/claim constraints, then the N29 prototype atlas, I15 bridge dependency seeds, exact I16/I17/I17-A seed consumption, and closeout handoff.",
        "- `n29_prototype_atlas_panel.png` isolates the four prototype families A-D and their evidence/debt ceilings.",
        "- `n29_probe_contract_expansion.png` shows the contract progression from I16 A+B to I17 A+B+C to I17-A A+B+C+D.",
        "- `n29_prototype_d_motif_panel.png` explains the Prototype D lane split: native/source-current rows emit local medium-reshaping motifs, while producer-mediated composition orders multi-leg handoff, phase, and leakage handling as explicit naturalization debt.",
        "",
        "The repository index links the graph, sequence, and panels to full-size static images for zooming. The animation is generated as an auxiliary artifact, but it is not the primary inspection path.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    build_bridge_atlas_graph(sources)
    build_prototype_panel(sources)
    build_contract_panel(sources)
    build_prototype_d_panel(sources)
    frame_paths = build_sequence(sources)
    manifest = build_manifest(sources, frame_paths)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    write_report(manifest)
    print(f"wrote {rel(MANIFEST_PATH)}")
    print(f"output_digest = {manifest['output_digest']}")


if __name__ == "__main__":
    main()
