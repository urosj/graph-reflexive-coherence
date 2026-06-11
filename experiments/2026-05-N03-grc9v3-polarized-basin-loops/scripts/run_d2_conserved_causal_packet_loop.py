#!/usr/bin/env python3
"""Run D2 conserved causal packet loop prototype.

D2 promotes only the D1f4 causal-packet-delay mechanism into a fresh
experiment-local prototype.  It is not native GRC9V3 evidence and does not
modify src/*.

Budget invariant:

    B = sum(node coherence) + sum(in-flight packet coherence)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json, write_jsonl  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d2_conserved_causal_packet_loop.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d2_conserved_causal_packet_loop.md"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d2_conserved_causal_packet_loop_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d2_conserved_causal_packet_loop.py"
)

TOTAL_BUDGET = 1.0
NODE_COUNT = 12
PACKET_AMOUNT = 0.006
PACKET_DELAY = 3
N_CYCLES_MIN = 3
MATERIAL_NORMALIZED_THRESHOLD = 0.01
BUDGET_TOLERANCE = 1e-9

POLES = {
    "S1": (0, 1),
    "K2": (3, 4),
    "S2": (6, 7),
    "K1": (9, 10),
}

CW_CHANNELS = {
    "S1_to_K2": {
        "source": "S1",
        "target": "K2",
        "edges": (1, 2),
        "sign": 1.0,
    },
    "K2_to_S2": {
        "source": "K2",
        "target": "S2",
        "edges": (4, 5),
        "sign": 1.0,
    },
    "S2_to_K1": {
        "source": "S2",
        "target": "K1",
        "edges": (7, 8),
        "sign": 1.0,
    },
    "K1_to_S1": {
        "source": "K1",
        "target": "S1",
        "edges": (10, 11),
        "sign": 1.0,
    },
}

CCW_CHANNELS = {
    "S1_to_K1_rev": {
        "source": "S1",
        "target": "K1",
        "edges": (10, 11),
        "sign": -1.0,
    },
    "K1_to_S2_rev": {
        "source": "K1",
        "target": "S2",
        "edges": (7, 8),
        "sign": -1.0,
    },
    "S2_to_K2_rev": {
        "source": "S2",
        "target": "K2",
        "edges": (4, 5),
        "sign": -1.0,
    },
    "K2_to_S1_rev": {
        "source": "K2",
        "target": "S1",
        "edges": (1, 2),
        "sign": -1.0,
    },
}

CW_SEQUENCE = ("S1_to_K2", "K2_to_S2", "S2_to_K1", "K1_to_S1")
CCW_SEQUENCE = ("S1_to_K1_rev", "K1_to_S2_rev", "S2_to_K2_rev", "K2_to_S1_rev")


@dataclass(frozen=True)
class Packet:
    channel_id: str
    amount: float
    arrive_step: int


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _initial_nodes() -> dict[int, float]:
    return {node_id: TOTAL_BUDGET / NODE_COUNT for node_id in range(NODE_COUNT)}


def _packet_budget(packets: Sequence[Packet]) -> float:
    return sum(packet.amount for packet in packets)


def _node_budget(nodes: Mapping[int, float]) -> float:
    return sum(float(value) for value in nodes.values())


def _pole_mass(nodes: Mapping[int, float], pole_id: str) -> float:
    return sum(float(nodes[node_id]) for node_id in POLES[pole_id])


def _channel_table(direction: str) -> Mapping[str, Mapping[str, Any]]:
    if direction == "cw":
        return CW_CHANNELS
    if direction == "ccw":
        return CCW_CHANNELS
    raise ValueError(f"unsupported packet direction {direction!r}")


def _sequence(direction: str) -> tuple[str, ...]:
    if direction == "cw":
        return CW_SEQUENCE
    if direction == "ccw":
        return CCW_SEQUENCE
    raise ValueError(f"unsupported packet direction {direction!r}")


def _subtract_from_source(
    nodes: dict[int, float],
    *,
    channel_id: str,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
) -> float:
    source = str(channels[channel_id]["source"])
    source_nodes = POLES[source]
    available = sum(max(0.0, nodes[node_id]) for node_id in source_nodes)
    actual = max(0.0, min(float(amount), available))
    if actual <= 0.0:
        return 0.0
    for node_id in source_nodes:
        nodes[node_id] -= actual / len(source_nodes)
    return actual


def _add_to_target(
    nodes: dict[int, float],
    *,
    channel_id: str,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
) -> None:
    target = str(channels[channel_id]["target"])
    for node_id in POLES[target]:
        nodes[node_id] += float(amount) / len(POLES[target])


def _flux_for_event(
    channel_id: str,
    *,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
) -> dict[str, float]:
    flux = {str(edge_id): 0.0 for edge_id in range(NODE_COUNT)}
    channel = channels[channel_id]
    signed_amount = float(channel["sign"]) * float(amount)
    for edge_id in channel["edges"]:
        flux[str(edge_id)] = signed_amount / len(channel["edges"])
    return flux


def _merge_flux(maps: Sequence[Mapping[str, float]]) -> dict[str, float]:
    merged = {str(edge_id): 0.0 for edge_id in range(NODE_COUNT)}
    for flux in maps:
        for edge_id, value in flux.items():
            merged[str(edge_id)] = merged.get(str(edge_id), 0.0) + float(value)
    return merged


def _loop_metrics(flux_uv: Mapping[str, float]) -> dict[str, float]:
    values = [float(flux_uv.get(str(edge_id), 0.0)) for edge_id in range(NODE_COUNT)]
    signed = sum(values)
    abs_sum = sum(abs(value) for value in values)
    return {
        "loop_circulation": signed,
        "loop_abs_flux_sum": abs_sum,
        "loop_normalized_circulation": signed / abs_sum if abs_sum > 0.0 else 0.0,
    }


def _cycle_count(events: Sequence[str], sequence: Sequence[str]) -> int:
    expected_index = 0
    cycles = 0
    for event in events:
        if event not in sequence:
            continue
        if event != sequence[expected_index]:
            expected_index = 1 if event == sequence[0] else 0
            continue
        expected_index += 1
        if expected_index == len(sequence):
            cycles += 1
            expected_index = 0
    return cycles


def _scenario_config() -> list[dict[str, Any]]:
    return [
        {
            "lane_id": "D2-U0-no-seed",
            "direction": "cw",
            "seed": False,
            "mode": "closed_loop",
            "expected_positive": False,
        },
        {
            "lane_id": "D2-P-cw-packet-loop",
            "direction": "cw",
            "seed": True,
            "mode": "closed_loop",
            "expected_positive": True,
        },
        {
            "lane_id": "D2-R-ccw-packet-loop",
            "direction": "ccw",
            "seed": True,
            "mode": "closed_loop",
            "expected_positive": True,
        },
        {
            "lane_id": "D2-C-forward-only",
            "direction": "cw",
            "seed": True,
            "mode": "forward_only",
            "expected_positive": False,
        },
        {
            "lane_id": "D2-C-broken-return",
            "direction": "cw",
            "seed": True,
            "mode": "broken_return",
            "expected_positive": False,
        },
        {
            "lane_id": "D2-C-scrambled-order",
            "direction": "cw",
            "seed": True,
            "mode": "scrambled_order",
            "expected_positive": False,
        },
    ]


def _next_channel(
    channel_id: str,
    *,
    sequence: Sequence[str],
    mode: str,
) -> str | None:
    if mode == "forward_only":
        return sequence[0]
    if mode == "broken_return" and channel_id == sequence[-2]:
        return None
    if mode == "scrambled_order":
        scrambled = (sequence[0], sequence[2], sequence[1], sequence[3])
        return scrambled[(scrambled.index(channel_id) + 1) % len(scrambled)]
    return sequence[(sequence.index(channel_id) + 1) % len(sequence)]


def _depart(
    nodes: dict[int, float],
    packets: deque[Packet],
    *,
    channel_id: str,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
    arrive_step: int,
) -> float:
    actual = _subtract_from_source(
        nodes,
        channel_id=channel_id,
        channels=channels,
        amount=amount,
    )
    if actual > 0.0:
        packets.append(Packet(channel_id=channel_id, amount=actual, arrive_step=arrive_step))
    return actual


def _row(
    *,
    step_index: int,
    lane_id: str,
    direction: str,
    nodes_pre: Mapping[int, float],
    nodes_post: Mapping[int, float],
    packets: Sequence[Packet],
    events: Sequence[str],
    flux_uv: Mapping[str, float],
) -> dict[str, Any]:
    metrics = _loop_metrics(flux_uv)
    row: dict[str, Any] = {
        "step_index": step_index,
        "lane_id": lane_id,
        "direction": direction,
        "events": list(events),
        "flux_uv": dict(flux_uv),
        **metrics,
        "node_budget": _node_budget(nodes_post),
        "packet_budget": _packet_budget(packets),
    }
    row["total_budget"] = row["node_budget"] + row["packet_budget"]
    for pole_id in POLES:
        row[f"C_{pole_id}_pre"] = _pole_mass(nodes_pre, pole_id)
        row[f"C_{pole_id}_post"] = _pole_mass(nodes_post, pole_id)
        row[f"delta_{pole_id}"] = row[f"C_{pole_id}_post"] - row[f"C_{pole_id}_pre"]
    return row


def _run_lane(config: Mapping[str, Any], *, total_steps: int) -> list[dict[str, Any]]:
    direction = str(config["direction"])
    sequence = _sequence(direction)
    channels = _channel_table(direction)
    mode = str(config["mode"])
    nodes = _initial_nodes()
    packets: deque[Packet] = deque()
    rows: list[dict[str, Any]] = []
    if bool(config["seed"]):
        _depart(
            nodes,
            packets,
            channel_id=sequence[0],
            channels=channels,
            amount=PACKET_AMOUNT,
            arrive_step=PACKET_DELAY,
        )
    for step_index in range(total_steps):
        nodes_pre = dict(nodes)
        events: list[str] = []
        flux_maps: list[dict[str, float]] = []
        arriving = [packet for packet in packets if packet.arrive_step <= step_index]
        packets = deque(packet for packet in packets if packet.arrive_step > step_index)
        for packet in arriving:
            _add_to_target(
                nodes,
                channel_id=packet.channel_id,
                channels=channels,
                amount=packet.amount,
            )
            events.append(packet.channel_id)
            flux_maps.append(
                _flux_for_event(
                    packet.channel_id,
                    channels=channels,
                    amount=packet.amount,
                )
            )
            next_channel = _next_channel(packet.channel_id, sequence=sequence, mode=mode)
            if next_channel is not None:
                _depart(
                    nodes,
                    packets,
                    channel_id=next_channel,
                    channels=channels,
                    amount=packet.amount,
                    arrive_step=step_index + PACKET_DELAY,
                )
        rows.append(
            _row(
                step_index=step_index,
                lane_id=str(config["lane_id"]),
                direction=direction,
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                packets=tuple(packets),
                events=events,
                flux_uv=_merge_flux(flux_maps),
            )
        )
    return rows


def _summarize_lane(config: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    direction = str(config["direction"])
    sequence = _sequence(direction)
    opposite_sequence = _sequence("ccw" if direction == "cw" else "cw")
    events = [event for row in rows for event in row["events"]]
    budget_errors = [abs(float(row["total_budget"]) - TOTAL_BUDGET) for row in rows]
    cycle_count = _cycle_count(events, sequence)
    opposite_cycle_count = _cycle_count(events, opposite_sequence)
    max_norm = max((abs(float(row["loop_normalized_circulation"])) for row in rows), default=0.0)
    max_abs = max((abs(float(row["loop_circulation"])) for row in rows), default=0.0)
    packet_budget_seen = max((float(row["packet_budget"]) for row in rows), default=0.0) > 0.0
    budget_passed = max(budget_errors, default=0.0) <= BUDGET_TOLERANCE
    positive = cycle_count >= N_CYCLES_MIN and budget_passed and packet_budget_seen
    return {
        "lane_id": str(config["lane_id"]),
        "direction": direction,
        "mode": str(config["mode"]),
        "expected_positive": bool(config["expected_positive"]),
        "event_count": len(events),
        "cycle_count": cycle_count,
        "opposite_cycle_count": opposite_cycle_count,
        "max_abs_loop_circulation": max_abs,
        "max_abs_normalized_circulation": max_norm,
        "mean_abs_normalized_circulation": _mean(
            [abs(float(row["loop_normalized_circulation"])) for row in rows]
        ),
        "max_budget_error": max(budget_errors, default=0.0),
        "budget_passed": budget_passed,
        "packet_budget_seen": packet_budget_seen,
        "prototype_positive": positive,
        "expectation_passed": positive is bool(config["expected_positive"]),
    }


def _classify(summaries: Sequence[Mapping[str, Any]]) -> str:
    positives = [row["lane_id"] for row in summaries if row["prototype_positive"]]
    failed_expectations = [row["lane_id"] for row in summaries if not row["expectation_passed"]]
    if failed_expectations:
        return "d2_packet_prototype_expectation_failure"
    if positives:
        return "d2_packetized_closed_flow_positive_with_controls"
    return "d2_packetized_closed_flow_no_positive_rows"


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D2 Conserved Causal Packet Loop Prototype",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{result['classification']}`",
        "",
        "D2 promotes D1f4 causal packet delay only. It is experiment-local",
        "packetized prototype evidence, not native GRC9V3 evidence.",
        "",
        "Budget invariant:",
        "",
        "```text",
        "B = sum(node coherence) + sum(in-flight packet coherence)",
        "```",
        "",
        "## Lane Summary",
        "",
        "| Lane | Mode | Direction | Events | Cycles | Opposite Cycles | Max Norm Circ | Budget | Expected | Positive |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in result["lane_summaries"]:
        lines.append(
            "| {lane} | {mode} | {direction} | {events} | {cycles} | {opposite} | {max_norm:.6g} | {budget} | {expected} | {positive} |".format(
                lane=row["lane_id"],
                mode=row["mode"],
                direction=row["direction"],
                events=row["event_count"],
                cycles=row["cycle_count"],
                opposite=row["opposite_cycle_count"],
                max_norm=row["max_abs_normalized_circulation"],
                budget="pass" if row["budget_passed"] else "fail",
                expected="positive" if row["expected_positive"] else "negative",
                positive="yes" if row["prototype_positive"] else "no",
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], "", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    total_steps = int(manifest["runner_config"]["total_steps"])
    lane_summaries: list[dict[str, Any]] = []
    errors: list[str] = []
    for config in _scenario_config():
        rows = _run_lane(config, total_steps=total_steps)
        lane_id = str(config["lane_id"])
        path = TIMESERIES_DIR / f"{lane_id.lower().replace('-', '_')}_timeseries.jsonl"
        write_jsonl(path, rows)
        summary = _summarize_lane(config, rows)
        summary["timeseries_path"] = str(path)
        lane_summaries.append(summary)
        if not summary["budget_passed"]:
            errors.append(f"{lane_id} failed budget")
        if not summary["expectation_passed"]:
            errors.append(f"{lane_id} failed expectation")
    classification = _classify(lane_summaries)
    positive_rows = [row["lane_id"] for row in lane_summaries if row["prototype_positive"]]
    interpretation = (
        "D2 shows whether a packetized in-flight coherence layer can turn the "
        "D1e static role surface into closed-loop propagation under explicit "
        "budget accounting. Positive lanes are packetized prototype evidence "
        "only; native GRC9V3 and movement claims remain blocked."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d2_conserved_causal_packet_loop_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": COMMAND,
        "native_evidence": False,
        "positive_loop_claim_allowed": False,
        "budget_invariant": "node_coherence + in_flight_packet_coherence",
        "classification": classification,
        "positive_rows": positive_rows,
        "lane_summaries": lane_summaries,
        "interpretation": interpretation,
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification,
                "positive_rows": positive_rows,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
