#!/usr/bin/env python3
"""Run C3.5 three-channel accumulator / phase-channel diagnostics.

This is a separate C3 surface after the fixed-topology three-pole runtime
failed to generate network closure.  It keeps topology fixed and audits budget
as node coherence plus explicit channel accumulator storage.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from loop_observables import load_json, write_json, write_jsonl  # noqa: E402
from run_c1_delayed_accumulator import _add_to_region, _node_total, _remove_from_region  # noqa: E402
from run_c3_three_pole_diagnostic import (  # noqa: E402
    _channel_flux,
    _pole_rows,
    _runtime_model,
    _summarize_pole_rows,
    _three_pole_fixture,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "c3_5_three_channel_accumulator_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "c3_5_three_channel_accumulator_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "c3_5_three_channel_accumulator_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "c3_5_three_channel_accumulator_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_c3_5_three_channel_accumulator.py"
)


CHANNEL_ORDER = ("R1_R2", "R2_R3", "R3_R1")
CHANNEL_ENDPOINTS = {
    "R1_R2": ("R1", "R2"),
    "R2_R3": ("R2", "R3"),
    "R3_R1": ("R3", "R1"),
}


@dataclass(frozen=True)
class PhaseChannelPolicy:
    policy_id: str
    delay_steps: int
    mode: str
    refractory_steps: int = 0


@dataclass
class ChannelState:
    queue: deque[float]
    refractory_left: int = 0


def _policies() -> list[PhaseChannelPolicy]:
    return [
        PhaseChannelPolicy("parallel_delay_3", delay_steps=3, mode="parallel"),
        PhaseChannelPolicy("parallel_delay_6", delay_steps=6, mode="parallel"),
        PhaseChannelPolicy("cyclic_phase_delay_3", delay_steps=3, mode="cyclic"),
        PhaseChannelPolicy("cyclic_phase_delay_6", delay_steps=6, mode="cyclic"),
        PhaseChannelPolicy("cyclic_phase_delay_10", delay_steps=10, mode="cyclic"),
        PhaseChannelPolicy(
            "cyclic_phase_delay_6_refractory_10",
            delay_steps=6,
            mode="cyclic",
            refractory_steps=10,
        ),
    ]


def _coherence_map(model: Any) -> dict[str, float]:
    return {
        str(node_id): float(node.coherence)
        for node_id, node in sorted(model._state.nodes.items())
    }


def _proposal_flux_map(model: Any) -> dict[str, float]:
    return {
        str(edge_id): float(edge.flux_uv)
        for edge_id, edge in sorted(model._state.port_edges.items())
    }


def _empty_effective_flux(fixture: Mapping[str, Any]) -> dict[str, float]:
    return {str(edge["edge_id"]): 0.0 for edge in fixture["edges"]}


def _queue_total(states: Mapping[str, ChannelState]) -> float:
    return sum(sum(state.queue) for state in states.values())


def _effective_flux(
    *,
    fixture: Mapping[str, Any],
    departures: Mapping[str, float],
    arrivals: Mapping[str, float],
    dt: float,
) -> dict[str, float]:
    flux = _empty_effective_flux(fixture)
    for channel_id, edges in fixture["channels"].items():
        channel_edges = [int(edge_id) for edge_id in edges]
        if not channel_edges or dt <= 0.0:
            continue
        flux[str(channel_edges[0])] += float(departures.get(channel_id, 0.0)) / dt
        flux[str(channel_edges[-1])] += float(arrivals.get(channel_id, 0.0)) / dt
    return flux


def _active_channel(policy: PhaseChannelPolicy, phase_index: int) -> str | None:
    if policy.mode == "parallel":
        return None
    return CHANNEL_ORDER[phase_index % len(CHANNEL_ORDER)]


def _step_phase_channel(
    *,
    model: Any,
    manifest: Mapping[str, Any],
    fixture: Mapping[str, Any],
    policy: PhaseChannelPolicy,
    states: Mapping[str, ChannelState],
    phase_index: int,
) -> tuple[dict[str, Any], int]:
    dt = float(manifest["runner_config"]["dt"])
    c_pre = _coherence_map(model)
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    proposal = _proposal_flux_map(model)
    active = _active_channel(policy, phase_index)
    departures = {channel_id: 0.0 for channel_id in CHANNEL_ORDER}
    arrivals = {channel_id: 0.0 for channel_id in CHANNEL_ORDER}

    for channel_id in CHANNEL_ORDER:
        if active is not None and channel_id != active:
            states[channel_id].queue.append(0.0)
            arrivals[channel_id] = states[channel_id].queue.popleft()
            continue
        if states[channel_id].refractory_left > 0:
            states[channel_id].refractory_left -= 1
            states[channel_id].queue.append(0.0)
            arrivals[channel_id] = states[channel_id].queue.popleft()
            continue
        source_pole, _target_pole = CHANNEL_ENDPOINTS[channel_id]
        source_nodes = [int(node_id) for node_id in fixture["poles"][source_pole]]
        channel_edges = [int(edge_id) for edge_id in fixture["channels"][channel_id]]
        proposal_flux = max(0.0, _channel_flux(proposal, channel_edges))
        departure = _remove_from_region(model, source_nodes, dt * proposal_flux)
        states[channel_id].queue.append(departure)
        arrival = states[channel_id].queue.popleft()
        departures[channel_id] = departure
        arrivals[channel_id] = arrival

    for channel_id, arrival in arrivals.items():
        if arrival <= 0.0:
            continue
        _source_pole, target_pole = CHANNEL_ENDPOINTS[channel_id]
        target_nodes = [int(node_id) for node_id in fixture["poles"][target_pole]]
        _add_to_region(model, target_nodes, arrival)
        if policy.mode == "cyclic" and channel_id == active:
            phase_index = (phase_index + 1) % len(CHANNEL_ORDER)
            if policy.refractory_steps:
                states[channel_id].refractory_left = policy.refractory_steps

    c_post = _coherence_map(model)
    in_flight = _queue_total(states)
    total = _node_total(model) + in_flight
    target = float(manifest["budget"]["total_budget"])
    return (
        {
            "C_pre": c_pre,
            "C_post_continuity": c_post,
            "C_post_budget": c_post,
            "flux_uv": _effective_flux(
                fixture=fixture,
                departures=departures,
                arrivals=arrivals,
                dt=dt,
            ),
            "proposal_flux_uv": proposal,
            "budget": {
                "before_continuity": target,
                "after_continuity": total,
                "after_correction": total,
                "correction_method": "none_three_channel_accumulator_exact_budget",
                "correction_magnitude": 0.0,
                "simplex_projection_applied": False,
                "uniform_shift_applied": False,
            },
            "accumulator": {
                "phase_index": phase_index,
                "active_channel": active or "parallel",
                "departures": departures,
                "arrivals": arrivals,
                "channel_storage": {
                    channel_id: sum(state.queue) for channel_id, state in states.items()
                },
                "in_flight_total": in_flight,
                "node_total": _node_total(model),
                "nodes_plus_accumulators_total": total,
                "budget_error": total - target,
            },
        },
        phase_index,
    )


def _run_policy_lane(
    *,
    manifest: Mapping[str, Any],
    policy: PhaseChannelPolicy,
    lane_id: str,
) -> dict[str, Any]:
    fixture = _three_pole_fixture()
    model = _runtime_model(lane_id, manifest)
    states = {
        channel_id: ChannelState(deque([0.0] * policy.delay_steps))
        for channel_id in CHANNEL_ORDER
    }
    phase_index = 0
    initial_nodes = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edges = len(tuple(model._state.topology.iter_live_edge_ids()))
    raw_records: list[dict[str, Any]] = []
    for step_index in range(int(manifest["runner_config"]["total_steps"])):
        step_record, phase_index = _step_phase_channel(
            model=model,
            manifest=manifest,
            fixture=fixture,
            policy=policy,
            states=states,
            phase_index=phase_index,
        )
        raw_records.append({"step_index": step_index, **step_record})
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()

    row_id = f"c3_5_{lane_id.lower()}_{policy.policy_id}"
    raw_path = RAW_RECORD_DIR / f"{row_id}_raw_records.jsonl"
    write_jsonl(raw_path, raw_records)
    rows = _pole_rows(fixture=fixture, records=raw_records)
    ts_path = TIMESERIES_DIR / f"{row_id}_timeseries.jsonl"
    write_jsonl(ts_path, rows)
    report = _summarize_pole_rows(
        rows=rows,
        lane_id=lane_id,
        runner_mode="c3_5_three_channel_accumulator_runner",
        metric_config=manifest["metric_config_defaults"],
    )
    final_nodes = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edges = len(tuple(model._state.topology.iter_live_edge_ids()))
    max_budget_error = max(abs(record["accumulator"]["budget_error"]) for record in raw_records)
    report["topology"] = {
        "initial_node_count": initial_nodes,
        "final_node_count": final_nodes,
        "initial_edge_count": initial_edges,
        "final_edge_count": final_edges,
        "changed": initial_nodes != final_nodes or initial_edges != final_edges,
    }
    report["policy"] = {
        "policy_id": policy.policy_id,
        "mode": policy.mode,
        "delay_steps": policy.delay_steps,
        "refractory_steps": policy.refractory_steps,
    }
    report["accumulator_budget"] = {
        "budget_surface": "node_coherence_plus_three_channel_accumulators",
        "max_abs_budget_error": max_budget_error,
        "max_in_flight_total": max(record["accumulator"]["in_flight_total"] for record in raw_records),
        "passed": max_budget_error <= 1e-9,
    }
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["timeseries"] = {"artifact_path": str(ts_path)}
    report["diagnostic_row"] = {
        "row_id": row_id,
        "lane_id": lane_id,
        "policy_id": policy.policy_id,
    }
    report["would_candidate_without_diagnostic_ceiling"] = bool(
        report["three_pole_candidate_claim_allowed"]
    )
    report["three_pole_candidate_claim_allowed"] = False
    report["blocked_reasons"] = list(report["blocked_reasons"]) + [
        "three_pole_diagnostic_claim_ceiling"
    ]
    return report


def _run_reports(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for policy in _policies():
        for lane_id in ("P", "P_reversed"):
            reports.append(_run_policy_lane(manifest=manifest, policy=policy, lane_id=lane_id))
    serious_policy = next(policy for policy in _policies() if policy.policy_id == "cyclic_phase_delay_6")
    for lane_id in ("U0", "U3"):
        reports.append(_run_policy_lane(manifest=manifest, policy=serious_policy, lane_id=lane_id))
    return reports


def _summarize_reports(reports: list[Mapping[str, Any]]) -> dict[str, Any]:
    compact: list[dict[str, Any]] = []
    promising: list[dict[str, Any]] = []
    for report in reports:
        row = {
            "row_id": report["diagnostic_row"]["row_id"],
            "lane_id": report["diagnostic_row"]["lane_id"],
            "policy_id": report["diagnostic_row"]["policy_id"],
            "network_closure_score": report["network_closure_score"],
            "raw_three_pole_cascade_count": report["raw_three_pole_cascade_count"],
            "role_gated_three_pole_cascade_count": report[
                "role_gated_three_pole_cascade_count"
            ],
            "would_candidate_without_diagnostic_ceiling": report[
                "would_candidate_without_diagnostic_ceiling"
            ],
            "max_in_flight_total": report["accumulator_budget"]["max_in_flight_total"],
            "max_abs_budget_error": report["accumulator_budget"]["max_abs_budget_error"],
        }
        compact.append(row)
        if row["role_gated_three_pole_cascade_count"] or row["would_candidate_without_diagnostic_ceiling"]:
            promising.append(row)
    return {
        "row_count": len(reports),
        "promising_row_count": len(promising),
        "promising_rows": promising,
        "compact_rows": compact,
        "classification": (
            "c3_5_candidate_conditions_observed"
            if promising
            else "c3_5_no_three_pole_candidate_conditions"
        ),
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for report in result["reports"]:
        row_id = report["diagnostic_row"]["row_id"]
        if report["topology"]["changed"]:
            errors.append(f"{row_id} changed topology")
        if not report["accumulator_budget"]["passed"]:
            errors.append(f"{row_id} failed accumulator budget audit")
        if report["three_pole_candidate_claim_allowed"]:
            errors.append(f"{row_id} promoted a diagnostic claim")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# C3.5 Three-Channel Accumulator Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "C3.5 is a three-pole diagnostic surface, not a positive loop-claim tranche.",
        "",
        f"Rows: `{result['summary']['row_count']}`",
        f"Promising rows: `{result['summary']['promising_row_count']}`",
        f"Classification: `{result['summary']['classification']}`",
        "",
        "## Compact Summary",
        "",
        "| Row | Lane | Policy | Closure | Raw | Role-Gated | Would Claim | Max In-Flight | Max Budget Error |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {row_id} | {lane} | {policy} | {closure:.6g} | {raw} | {gated} | {would} | {flight:.6g} | {budget:.6g} |".format(
                row_id=row["row_id"],
                lane=row["lane_id"],
                policy=row["policy_id"],
                closure=row["network_closure_score"],
                raw=row["raw_three_pole_cascade_count"],
                gated=row["role_gated_three_pole_cascade_count"],
                would=row["would_candidate_without_diagnostic_ceiling"],
                flight=row["max_in_flight_total"],
                budget=row["max_abs_budget_error"],
            )
        )
    lines.extend(["", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    reports = _run_reports(manifest)
    summary = _summarize_reports(reports)
    result = {
        "schema": "grc9v3_polarized_basin_loop_c3_5_three_channel_accumulator_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "claim_ceiling": "three_pole_diagnostic_surface_not_positive_loop_claim",
        "reports": reports,
        "summary": summary,
        "errors": [],
    }
    errors = _validate(result)
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": summary["classification"],
                "promising_rows": summary["promising_row_count"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
