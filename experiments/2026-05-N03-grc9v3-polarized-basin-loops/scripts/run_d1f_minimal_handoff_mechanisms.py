#!/usr/bin/env python3
"""Run D1f minimal handoff mechanism probes.

D1f starts from the D1e alternating-pole diagnosis and adds one missing
ingredient at a time.  These lanes are experiment-local mechanism probes, not
native GRC9V3 evidence and not positive N03 loop claims.

Numeric lanes:

- D1f1: explicit phase handoff;
- D1f2: edge/corridor storage;
- D1f3: momentum retention;
- D1f4: causal packet delay;
- D1f5: adaptive role handoff.
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
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1f_minimal_handoff_mechanisms.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1f_minimal_handoff_mechanisms.md"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d1f_minimal_handoff_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1f_minimal_handoff_mechanisms.py"
)

TOTAL_BUDGET = 1.0
NODE_COUNT = 12
TRANSFER_AMOUNT = 0.006
MOMENTUM_AMOUNT = 0.004
MATERIAL_NORMALIZED_THRESHOLD = 0.01
N_CYCLES_MIN = 3

POLES = {
    "S1": (0, 1),
    "K2": (3, 4),
    "S2": (6, 7),
    "K1": (9, 10),
}
CHANNEL_EDGES = {
    "S1_to_K2": (1, 2),
    "K2_to_S2": (4, 5),
    "S2_to_K1": (7, 8),
    "K1_to_S1": (10, 11),
}
CHANNEL_SEQUENCE = ("S1_to_K2", "K2_to_S2", "S2_to_K1", "K1_to_S1")
CHANNEL_ENDPOINTS = {
    "S1_to_K2": ("S1", "K2"),
    "K2_to_S2": ("K2", "S2"),
    "S2_to_K1": ("S2", "K1"),
    "K1_to_S1": ("K1", "S1"),
}


@dataclass
class Packet:
    channel_id: str
    amount: float
    arrive_step: int


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _initial_node_mass() -> dict[int, float]:
    return {node_id: TOTAL_BUDGET / NODE_COUNT for node_id in range(NODE_COUNT)}


def _pole_mass(nodes: Mapping[int, float], pole_id: str) -> float:
    return sum(float(nodes[node_id]) for node_id in POLES[pole_id])


def _transfer(nodes: dict[int, float], source_pole: str, target_pole: str, amount: float) -> float:
    source_nodes = POLES[source_pole]
    target_nodes = POLES[target_pole]
    available = sum(max(0.0, nodes[node_id]) for node_id in source_nodes)
    actual = max(0.0, min(float(amount), available))
    if actual <= 0.0:
        return 0.0
    for node_id in source_nodes:
        nodes[node_id] -= actual / len(source_nodes)
    for node_id in target_nodes:
        nodes[node_id] += actual / len(target_nodes)
    return actual


def _flux_for_channel(channel_id: str, amount: float) -> dict[str, float]:
    flux = {str(edge_id): 0.0 for edge_id in range(NODE_COUNT)}
    for edge_id in CHANNEL_EDGES[channel_id]:
        flux[str(edge_id)] = float(amount) / len(CHANNEL_EDGES[channel_id])
    return flux


def _merge_flux(*maps: Mapping[str, float]) -> dict[str, float]:
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


def _event_cycle_count(events: Sequence[str]) -> int:
    expected_index = 0
    cycles = 0
    for event in events:
        if event != CHANNEL_SEQUENCE[expected_index]:
            if event == CHANNEL_SEQUENCE[0]:
                expected_index = 1
            else:
                expected_index = 0
            continue
        expected_index += 1
        if expected_index == len(CHANNEL_SEQUENCE):
            cycles += 1
            expected_index = 0
    return cycles


def _phase_cycle_count(rows: Sequence[Mapping[str, Any]]) -> int:
    expected_index = 0
    cycles = 0
    for row in rows:
        events = [event for event in row["events"] if event in CHANNEL_SEQUENCE]
        if len(events) == 0:
            continue
        if len(events) > 1:
            expected_index = 0
            continue
        event = events[0]
        if event != CHANNEL_SEQUENCE[expected_index]:
            expected_index = 1 if event == CHANNEL_SEQUENCE[0] else 0
            continue
        expected_index += 1
        if expected_index == len(CHANNEL_SEQUENCE):
            cycles += 1
            expected_index = 0
    return cycles


def _row(
    *,
    step_index: int,
    lane_id: str,
    nodes_pre: Mapping[int, float],
    nodes_post: Mapping[int, float],
    flux_uv: Mapping[str, float],
    events: Sequence[str],
    storage: Mapping[str, float] | None = None,
    packets: Sequence[Packet] = (),
) -> dict[str, Any]:
    metrics = _loop_metrics(flux_uv)
    row: dict[str, Any] = {
        "step_index": step_index,
        "lane_id": lane_id,
        "events": list(events),
        "flux_uv": dict(flux_uv),
        **metrics,
        "node_budget": sum(float(value) for value in nodes_post.values()),
        "storage_budget": sum(float(value) for value in (storage or {}).values()),
        "packet_budget": sum(packet.amount for packet in packets),
    }
    row["total_budget_with_mechanism"] = (
        row["node_budget"] + row["storage_budget"] + row["packet_budget"]
    )
    for pole_id in POLES:
        row[f"C_{pole_id}_pre"] = _pole_mass(nodes_pre, pole_id)
        row[f"C_{pole_id}_post"] = _pole_mass(nodes_post, pole_id)
        row[f"delta_{pole_id}"] = row[f"C_{pole_id}_post"] - row[f"C_{pole_id}_pre"]
    return row


def _run_d1f1(total_steps: int) -> list[dict[str, Any]]:
    nodes = _initial_node_mass()
    rows: list[dict[str, Any]] = []
    for step in range(total_steps):
        nodes_pre = dict(nodes)
        phase = (step // 4) % len(CHANNEL_SEQUENCE)
        active = step % 4 == 0
        events: list[str] = []
        flux_maps: list[dict[str, float]] = []
        if active:
            channel_id = CHANNEL_SEQUENCE[phase]
            source, target = CHANNEL_ENDPOINTS[channel_id]
            actual = _transfer(nodes, source, target, TRANSFER_AMOUNT)
            if actual > 0.0:
                events.append(channel_id)
                flux_maps.append(_flux_for_channel(channel_id, actual))
        rows.append(
            _row(
                step_index=step,
                lane_id="D1f1",
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                flux_uv=_merge_flux(*flux_maps),
                events=events,
            )
        )
    return rows


def _run_d1f2(total_steps: int) -> list[dict[str, Any]]:
    nodes = _initial_node_mass()
    storage = {channel_id: 0.0 for channel_id in CHANNEL_SEQUENCE}
    rows: list[dict[str, Any]] = []
    for step in range(total_steps):
        nodes_pre = dict(nodes)
        flux_maps: list[dict[str, float]] = []
        events: list[str] = []
        # Storage fills from static D1e source roles only; it has no handoff.
        for channel_id in ("S1_to_K2", "S2_to_K1"):
            source, _target = CHANNEL_ENDPOINTS[channel_id]
            actual = _transfer(nodes, source, source, 0.0)
            available = sum(nodes[node_id] for node_id in POLES[source])
            deposit = min(TRANSFER_AMOUNT, max(0.0, available * 0.05))
            for node_id in POLES[source]:
                nodes[node_id] -= deposit / len(POLES[source])
            storage[channel_id] += deposit
        for channel_id in CHANNEL_SEQUENCE:
            release = min(storage[channel_id], TRANSFER_AMOUNT * 0.65)
            if release <= 0.0:
                continue
            storage[channel_id] -= release
            _source, target = CHANNEL_ENDPOINTS[channel_id]
            for node_id in POLES[target]:
                nodes[node_id] += release / len(POLES[target])
            events.append(channel_id)
            flux_maps.append(_flux_for_channel(channel_id, release))
        rows.append(
            _row(
                step_index=step,
                lane_id="D1f2",
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                flux_uv=_merge_flux(*flux_maps),
                events=events,
                storage=storage,
            )
        )
    return rows


def _run_d1f3(total_steps: int) -> list[dict[str, Any]]:
    nodes = _initial_node_mass()
    momentum = {channel_id: MOMENTUM_AMOUNT for channel_id in CHANNEL_SEQUENCE}
    rows: list[dict[str, Any]] = []
    for step in range(total_steps):
        nodes_pre = dict(nodes)
        flux_maps: list[dict[str, float]] = []
        events: list[str] = []
        for channel_id in CHANNEL_SEQUENCE:
            source, target = CHANNEL_ENDPOINTS[channel_id]
            actual = _transfer(nodes, source, target, momentum[channel_id])
            if actual > 0.0:
                events.append(channel_id)
                flux_maps.append(_flux_for_channel(channel_id, actual))
            momentum[channel_id] *= 0.985
        rows.append(
            _row(
                step_index=step,
                lane_id="D1f3",
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                flux_uv=_merge_flux(*flux_maps),
                events=events,
            )
        )
    return rows


def _run_d1f4(total_steps: int) -> list[dict[str, Any]]:
    nodes = _initial_node_mass()
    packets: deque[Packet] = deque()
    rows: list[dict[str, Any]] = []

    def depart(channel_id: str, amount: float, arrive_step: int) -> float:
        source, _target = CHANNEL_ENDPOINTS[channel_id]
        source_nodes = POLES[source]
        available = sum(max(0.0, nodes[node_id]) for node_id in source_nodes)
        actual = max(0.0, min(float(amount), available))
        if actual <= 0.0:
            return 0.0
        for node_id in source_nodes:
            nodes[node_id] -= actual / len(source_nodes)
        packets.append(Packet(channel_id, actual, arrive_step))
        return actual

    depart("S1_to_K2", TRANSFER_AMOUNT, 2)
    for step in range(total_steps):
        nodes_pre = dict(nodes)
        flux_maps: list[dict[str, float]] = []
        events: list[str] = []
        arriving = [packet for packet in list(packets) if packet.arrive_step <= step]
        packets = deque(packet for packet in packets if packet.arrive_step > step)
        for packet in arriving:
            _source, target = CHANNEL_ENDPOINTS[packet.channel_id]
            actual = packet.amount
            for node_id in POLES[target]:
                nodes[node_id] += actual / len(POLES[target])
            events.append(packet.channel_id)
            flux_maps.append(_flux_for_channel(packet.channel_id, actual))
            next_index = (CHANNEL_SEQUENCE.index(packet.channel_id) + 1) % len(CHANNEL_SEQUENCE)
            depart(CHANNEL_SEQUENCE[next_index], actual, step + 3)
        rows.append(
            _row(
                step_index=step,
                lane_id="D1f4",
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                flux_uv=_merge_flux(*flux_maps),
                events=events,
                packets=tuple(packets),
            )
        )
    return rows


def _run_d1f5(total_steps: int) -> list[dict[str, Any]]:
    nodes = _initial_node_mass()
    active_channel = "S1_to_K2"
    refractory = 0
    rows: list[dict[str, Any]] = []
    for step in range(total_steps):
        nodes_pre = dict(nodes)
        flux_maps: list[dict[str, float]] = []
        events: list[str] = []
        if refractory > 0:
            refractory -= 1
        else:
            source, target = CHANNEL_ENDPOINTS[active_channel]
            source_mass = _pole_mass(nodes, source)
            target_before = _pole_mass(nodes, target)
            if source_mass > 0.05:
                actual = _transfer(nodes, source, target, TRANSFER_AMOUNT)
                target_after = _pole_mass(nodes, target)
                if actual > 0.0 and target_after - target_before > TRANSFER_AMOUNT * 0.5:
                    events.append(active_channel)
                    flux_maps.append(_flux_for_channel(active_channel, actual))
                    next_index = (CHANNEL_SEQUENCE.index(active_channel) + 1) % len(CHANNEL_SEQUENCE)
                    active_channel = CHANNEL_SEQUENCE[next_index]
                    refractory = 2
        rows.append(
            _row(
                step_index=step,
                lane_id="D1f5",
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                flux_uv=_merge_flux(*flux_maps),
                events=events,
            )
        )
    return rows


def _summarize_rows(lane_id: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    event_sequence = [
        event
        for row in rows
        for event in row["events"]
        if event in CHANNEL_SEQUENCE
    ]
    ordered_event_cycle_count = _event_cycle_count(event_sequence)
    phase_cycle_count = _phase_cycle_count(rows)
    budget_errors = [
        abs(float(row["total_budget_with_mechanism"]) - TOTAL_BUDGET)
        for row in rows
    ]
    max_norm = max((abs(float(row["loop_normalized_circulation"])) for row in rows), default=0.0)
    max_abs = max((abs(float(row["loop_circulation"])) for row in rows), default=0.0)
    channel_coverage = {
        channel_id: sum(1 for event in event_sequence if event == channel_id)
        for channel_id in CHANNEL_SEQUENCE
    }
    simultaneous_closed_flow_steps = sum(
        1
        for row in rows
        if set(row["events"]) == set(CHANNEL_SEQUENCE)
    )
    budget_passed = max(budget_errors, default=0.0) <= 1e-9
    phase_cycle_positive = phase_cycle_count >= N_CYCLES_MIN and budget_passed
    closed_flow_positive = (
        simultaneous_closed_flow_steps >= N_CYCLES_MIN
        and all(count > 0 for count in channel_coverage.values())
        and max_norm >= MATERIAL_NORMALIZED_THRESHOLD
        and budget_passed
    )
    return {
        "lane_id": lane_id,
        "event_count": len(event_sequence),
        "ordered_event_cycle_count": ordered_event_cycle_count,
        "phase_cycle_count": phase_cycle_count,
        "simultaneous_closed_flow_steps": simultaneous_closed_flow_steps,
        "channel_coverage": channel_coverage,
        "max_abs_loop_circulation": max_abs,
        "max_abs_normalized_circulation": max_norm,
        "mean_abs_normalized_circulation": _mean(
            [abs(float(row["loop_normalized_circulation"])) for row in rows]
        ),
        "max_budget_error": max(budget_errors, default=0.0),
        "budget_passed": budget_passed,
        "phase_cycle_positive": phase_cycle_positive,
        "closed_flow_positive": closed_flow_positive,
        "mechanism_positive": phase_cycle_positive or closed_flow_positive,
        "material_circulation": max_norm >= MATERIAL_NORMALIZED_THRESHOLD,
    }


def _run_all(total_steps: int) -> dict[str, list[dict[str, Any]]]:
    return {
        "D1f1": _run_d1f1(total_steps),
        "D1f2": _run_d1f2(total_steps),
        "D1f3": _run_d1f3(total_steps),
        "D1f4": _run_d1f4(total_steps),
        "D1f5": _run_d1f5(total_steps),
    }


def _classify(summaries: Sequence[Mapping[str, Any]]) -> str:
    phase_positive = [row for row in summaries if row["phase_cycle_positive"]]
    closed_flow_positive = [row for row in summaries if row["closed_flow_positive"]]
    if phase_positive and closed_flow_positive:
        return "d1f_phase_and_closed_flow_positive_lanes_observed"
    if phase_positive:
        return "d1f_phase_handoff_positive_lanes_observed"
    if closed_flow_positive:
        return "d1f_closed_flow_positive_lanes_observed"
    if any(row["material_circulation"] for row in summaries):
        return "d1f_material_circulation_without_cycles"
    return "d1f_no_minimal_handoff_mechanism_cycles"


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D1f Minimal Handoff Mechanism Probes",
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
        "D1f is experiment-local mechanism isolation. It is not native GRC9V3",
        "evidence and not a positive N03 loop claim.",
        "",
        "## Lane Summary",
        "",
        "| Lane | Mechanism | Events | Phase Cycles | Closed-Flow Steps | Max Norm Circ | Budget | Positive Surface |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    names = result["lane_names"]
    for row in result["lane_summaries"]:
        positive_surface = "none"
        if row["phase_cycle_positive"] and row["closed_flow_positive"]:
            positive_surface = "phase+closed-flow"
        elif row["phase_cycle_positive"]:
            positive_surface = "phase"
        elif row["closed_flow_positive"]:
            positive_surface = "closed-flow"
        lines.append(
            "| {lane} | {name} | {events} | {cycles} | {closed_flow} | {max_norm:.6g} | {budget} | {positive} |".format(
                lane=row["lane_id"],
                name=names[row["lane_id"]],
                events=row["event_count"],
                cycles=row["phase_cycle_count"],
                closed_flow=row["simultaneous_closed_flow_steps"],
                max_norm=row["max_abs_normalized_circulation"],
                budget="pass" if row["budget_passed"] else "fail",
                positive=positive_surface,
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
    lane_rows = _run_all(total_steps)
    lane_summaries: list[dict[str, Any]] = []
    for lane_id, rows in lane_rows.items():
        path = TIMESERIES_DIR / f"{lane_id.lower()}_timeseries.jsonl"
        write_jsonl(path, rows)
        summary = _summarize_rows(lane_id, rows)
        summary["timeseries_path"] = str(path)
        lane_summaries.append(summary)
    errors = [
        f"{summary['lane_id']} failed budget"
        for summary in lane_summaries
        if not summary["budget_passed"]
    ]
    classification = _classify(lane_summaries)
    interpretation = (
        "D1f isolates missing mechanisms after D1e. Positive lanes show that a "
        "specific added mechanism can generate ordered closed-loop event cycles "
        "under budget conservation, but because the mechanism is experiment-local "
        "the result is sufficiency evidence for a future prototype, not native "
        "GRC9V3 loop evidence."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1f_minimal_handoff_mechanisms_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": COMMAND,
        "lane_names": {
            "D1f1": "explicit phase handoff",
            "D1f2": "edge/corridor storage",
            "D1f3": "momentum retention",
            "D1f4": "causal packet delay",
            "D1f5": "adaptive role handoff",
        },
        "native_evidence": False,
        "positive_loop_claim_allowed": False,
        "classification": classification,
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
                "positive_lanes": [
                    row["lane_id"]
                    for row in lane_summaries
                    if row["mechanism_positive"]
                ],
                "phase_positive_lanes": [
                    row["lane_id"]
                    for row in lane_summaries
                    if row["phase_cycle_positive"]
                ],
                "closed_flow_positive_lanes": [
                    row["lane_id"]
                    for row in lane_summaries
                    if row["closed_flow_positive"]
                ],
                "material_lanes": [
                    row["lane_id"]
                    for row in lane_summaries
                    if row["material_circulation"]
                ],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
