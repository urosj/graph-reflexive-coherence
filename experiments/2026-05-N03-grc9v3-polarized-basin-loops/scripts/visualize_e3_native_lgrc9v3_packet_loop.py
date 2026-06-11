#!/usr/bin/env python3
"""Build a replayable SVG visualization of the native E3 packet-loop run."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENT_ROOT.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

import run_e3_native_lgrc9v3_packet_loop_reproduction as e3  # noqa: E402
from pygrc.models.lgrc_9_v3_runtime import (  # noqa: E402
    LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY,
)


OUTPUT_JSON = EXPERIMENT_ROOT / "outputs" / "e3_native_lgrc9v3_packet_loop_visualization.json"
OUTPUT_SVG = EXPERIMENT_ROOT / "reports" / "e3_native_lgrc9v3_packet_loop_visualization.svg"
OUTPUT_MD = EXPERIMENT_ROOT / "reports" / "e3_native_lgrc9v3_packet_loop_visualization.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/visualize_e3_native_lgrc9v3_packet_loop.py"
)

POLE_COLORS = {
    "S1": "#2563eb",
    "K2": "#16a34a",
    "S2": "#9333ea",
    "K1": "#dc2626",
}


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _text(
    x: float,
    y: float,
    value: object,
    *,
    size: int = 16,
    weight: str = "400",
    fill: str = "#111827",
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
        f"{_escape(value)}</text>"
    )


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = "#374151",
    width: float = 2.0,
    marker: bool = False,
    dash: str | None = None,
) -> str:
    marker_attr = ' marker-end="url(#arrow)"' if marker else ""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{stroke}" stroke-width="{width:.1f}" stroke-linecap="round"'
        f"{marker_attr}{dash_attr}/>"
    )


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = "#ffffff",
    stroke: str = "#d1d5db",
    width: float = 1.0,
    rx: float = 6.0,
    opacity: float = 1.0,
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{width:.1f}" '
        f'opacity="{opacity:.3f}"/>'
    )


def _circle(
    x: float,
    y: float,
    r: float,
    *,
    fill: str,
    stroke: str = "#111827",
    width: float = 2.0,
) -> str:
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width:.1f}"/>'
    )


def _collect_direction(direction: str, *, duplicate_probe: bool = False) -> dict[str, Any]:
    model, report = e3._run_positive(direction=direction, duplicate_probe=duplicate_probe)
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    cached = runtime["cached_quantities"]
    self_rearms = list(cached.get(LGRC9V3_SELF_REARM_EVIDENCE_LOG_KEY, ()))
    packet_records = list(runtime["packet_ledger"]["packet_event_records"])
    route_aspect = e3.build_route_aspect(direction=direction).to_artifact()
    return {
        "direction": direction,
        "report": report,
        "route_aspect": route_aspect,
        "self_rearms": self_rearms,
        "packet_event_records": packet_records,
        "event_count": len(snapshot["events"]),
        "node_proper_time": runtime["node_proper_time"],
    }


def _draw_route_panel(
    *,
    x: float,
    y: float,
    title: str,
    route_aspect: dict[str, Any],
    report: dict[str, Any],
) -> str:
    parts: list[str] = []
    parts.append(_rect(x, y, 660, 300, fill="#f9fafb", stroke="#d1d5db", rx=8))
    parts.append(_text(x + 24, y + 36, title, size=22, weight="700"))
    parts.append(
        _text(
            x + 24,
            y + 64,
            f"cycles={report['cycle_count']}  self-rearms={report['self_rearm_count']}  triggers={report['trigger_count']}",
            size=14,
            fill="#374151",
        )
    )
    coords = {
        "S1": (x + 120, y + 150),
        "K2": (x + 330, y + 90),
        "S2": (x + 540, y + 150),
        "K1": (x + 330, y + 230),
    }
    if route_aspect["direction"] == "counter_clockwise":
        coords = {
            "S1": (x + 120, y + 150),
            "K1": (x + 330, y + 90),
            "S2": (x + 540, y + 150),
            "K2": (x + 330, y + 230),
        }

    for channel in route_aspect["channels"]:
        source = channel["source_pole_id"]
        target = channel["target_pole_id"]
        sx, sy = coords[source]
        tx, ty = coords[target]
        parts.append(_line(sx, sy, tx, ty, stroke="#4b5563", width=3, marker=True))
        mx, my = (sx + tx) / 2, (sy + ty) / 2
        parts.append(_text(mx, my - 10, channel["channel_id"], size=12, fill="#374151", anchor="middle"))

    for pole, (px, py) in coords.items():
        parts.append(_circle(px, py, 34, fill=POLE_COLORS[pole]))
        parts.append(_text(px, py + 6, pole, size=18, weight="700", fill="#ffffff", anchor="middle"))
        node_ids = route_aspect["pole_regions"][pole]
        parts.append(_text(px, py + 54, f"node {node_ids[0]}", size=12, fill="#4b5563", anchor="middle"))

    parts.append(_text(x + 24, y + 278, f"route digest {report['route_aspect_digest'][:16]}...", size=12, fill="#6b7280"))
    return "\n".join(parts)


def _draw_timeline(
    *,
    x: float,
    y: float,
    title: str,
    run: dict[str, Any],
) -> str:
    parts: list[str] = []
    self_rearms = run["self_rearms"]
    report = run["report"]
    parts.append(_rect(x, y, 1400, 210, fill="#ffffff", stroke="#d1d5db", rx=8))
    parts.append(_text(x + 24, y + 34, title, size=20, weight="700"))
    parts.append(
        _text(
            x + 24,
            y + 60,
            "Each box is a completed native self-rearm: parent arrival -> producer surplus trigger -> child departure.",
            size=13,
            fill="#4b5563",
        )
    )
    box_w = 98
    gap = 10
    start_x = x + 24
    box_y = y + 88
    for cycle_index in range(3):
        cx = start_x + cycle_index * (4 * (box_w + gap) + 18)
        parts.append(_rect(cx - 8, box_y - 18, 4 * (box_w + gap) + 4, 110, fill="#f3f4f6", stroke="#e5e7eb", rx=8))
        parts.append(_text(cx, box_y - 28, f"cycle {cycle_index + 1}", size=12, weight="700", fill="#4b5563"))
    for index, event in enumerate(self_rearms[:12]):
        cycle = index // 4
        step = index % 4
        bx = start_x + cycle * (4 * (box_w + gap) + 18) + step * (box_w + gap)
        source = event["source_pole_id"]
        color = POLE_COLORS.get(source, "#6b7280")
        parts.append(_rect(bx, box_y, box_w, 82, fill="#f9fafb", stroke=color, width=2, rx=6))
        parts.append(_rect(bx, box_y, box_w, 18, fill=color, stroke=color, width=1, rx=6))
        parts.append(_text(bx + box_w / 2, box_y + 14, source, size=12, weight="700", fill="#ffffff", anchor="middle"))
        parts.append(_text(bx + 8, box_y + 38, event["trigger_channel_id"], size=11, fill="#111827"))
        parts.append(_text(bx + 8, box_y + 56, f"T={event['producer_event_time_key']}", size=11, fill="#4b5563"))
        parts.append(_text(bx + 8, box_y + 73, f"surplus={event['surplus_after_arrival']:.3f}", size=11, fill="#4b5563"))
    parts.append(
        _text(
            x + 24,
            y + 192,
            f"max event budget error={report['max_event_budget_error']}  topology_changed={report['topology_changed']}  native_d2_3_equivalent={report['native_d2_3_equivalent']}",
            size=13,
            fill="#374151",
        )
    )
    return "\n".join(parts)


def _build_svg(summary: dict[str, Any]) -> str:
    cw = summary["runs"]["clockwise"]
    ccw = summary["runs"]["counter_clockwise"]
    parts: list[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1160" viewBox="0 0 1600 1160">'
    )
    parts.append(
        """
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563"/>
  </marker>
  <style>
    text { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  </style>
</defs>
"""
    )
    parts.append(_rect(0, 0, 1600, 1160, fill="#f3f4f6", stroke="#f3f4f6", rx=0))
    parts.append(_text(60, 72, "E3 Native LGRC9V3 Self-Rearming Packet Loop", size=34, weight="800"))
    parts.append(
        _text(
            60,
            104,
            "Native route-aspects + surplus-trigger production + self-rearm evidence; no native GRC9V3 proposal-flux, movement, or agency claim.",
            size=16,
            fill="#374151",
        )
    )

    badge_y = 130
    badges = [
        ("native LGRC9V3", "#1d4ed8"),
        ("D2.3 equivalent", "#047857"),
        ("budget error 0.0", "#4338ca"),
        ("controls passed", "#b45309"),
        ("movement blocked", "#be123c"),
    ]
    bx = 60
    for label, color in badges:
        width = 18 + len(label) * 9
        parts.append(_rect(bx, badge_y, width, 28, fill=color, stroke=color, rx=5))
        parts.append(_text(bx + width / 2, badge_y + 19, label, size=13, weight="700", fill="#ffffff", anchor="middle"))
        bx += width + 12

    parts.append(
        _draw_route_panel(
            x=60,
            y=190,
            title="Clockwise native route",
            route_aspect=cw["route_aspect"],
            report=cw["report"],
        )
    )
    parts.append(
        _draw_route_panel(
            x=780,
            y=190,
            title="Counter-clockwise native route",
            route_aspect=ccw["route_aspect"],
            report=ccw["report"],
        )
    )
    parts.append(_draw_timeline(x=60, y=530, title="Clockwise self-rearm timeline", run=cw))
    parts.append(_draw_timeline(x=60, y=780, title="Counter-clockwise self-rearm timeline", run=ccw))

    parts.append(_rect(60, 1040, 1400, 70, fill="#fff7ed", stroke="#fdba74", rx=8))
    parts.append(_text(84, 1068, "Claim boundary", size=18, weight="700", fill="#9a3412"))
    parts.append(
        _text(
            84,
            1094,
            "Supported: native LGRC9V3 packetized self-rearming loop. Blocked: native GRC9V3 proposal-flux loop, movement/locomotion, agency, biology.",
            size=14,
            fill="#7c2d12",
        )
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _compact_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "direction": run["direction"],
        "report": run["report"],
        "route_aspect": run["route_aspect"],
        "self_rearm_sequence": [
            {
                "index": index,
                "parent_arrival_channel_id": event["parent_arrival_channel_id"],
                "trigger_channel_id": event["trigger_channel_id"],
                "source_pole_id": event["source_pole_id"],
                "target_pole_id": event["target_pole_id"],
                "producer_event_time_key": event["producer_event_time_key"],
                "child_departure_event_time_key": event["child_departure_event_time_key"],
                "surplus_after_arrival": event["surplus_after_arrival"],
                "trigger_threshold": event["trigger_threshold"],
                "budget_after_child_departure": event["budget_after_child_departure"],
                "self_rearm_evidence_id": event["self_rearm_evidence_id"],
            }
            for index, event in enumerate(run["self_rearms"])
        ],
        "packet_event_record_count": len(run["packet_event_records"]),
        "event_count": run["event_count"],
        "node_proper_time": run["node_proper_time"],
    }


def main() -> None:
    cw = _collect_direction("clockwise", duplicate_probe=True)
    ccw = _collect_direction("counter_clockwise")
    summary = {
        "status": "passed",
        "classification": "e3_native_lgrc9v3_packet_loop_visualization",
        "command": COMMAND,
        "source_command": e3.COMMAND,
        "visualizes": [
            "outputs/e3_1_native_positive_reproduction.json",
            "configs/e3_native_lgrc9v3_packet_loop_route_manifest.json",
        ],
        "runs": {
            "clockwise": _compact_run(cw),
            "counter_clockwise": _compact_run(ccw),
        },
        "claim_boundary": {
            "native_lgrc9v3_packet_loop_supported": True,
            "native_grc9v3_proposal_flux_loop_evidence": False,
            "movement_claim_allowed": False,
            "agency_claim_allowed": False,
            "biology_claim_allowed": False,
        },
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    OUTPUT_SVG.write_text(_build_svg({"runs": {"clockwise": cw, "counter_clockwise": ccw}}))
    OUTPUT_MD.write_text(
        "# E3 Native LGRC9V3 Packet-Loop Visualization\n\n"
        "Command:\n\n"
        "```bash\n"
        f"{COMMAND}\n"
        "```\n\n"
        "Generated artifacts:\n\n"
        f"- `{OUTPUT_SVG.relative_to(EXPERIMENT_ROOT)}`\n"
        f"- `{OUTPUT_JSON.relative_to(EXPERIMENT_ROOT)}`\n\n"
        "The SVG visualizes the native clockwise and counter-clockwise E3 routes, "
        "the first three completed cycles for each direction, and the claim "
        "boundary. It is regenerated from native LGRC9V3 E3 positive runs, not "
        "from the old D2.3 prototype runner.\n\n"
        "Summary:\n\n"
        "```json\n"
        + json.dumps(
            {
                "clockwise": summary["runs"]["clockwise"]["report"],
                "counter_clockwise": summary["runs"]["counter_clockwise"]["report"],
                "claim_boundary": summary["claim_boundary"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n```\n"
    )
    print(json.dumps({"status": "passed", "svg": str(OUTPUT_SVG), "json": str(OUTPUT_JSON)}, sort_keys=True))


if __name__ == "__main__":
    main()
