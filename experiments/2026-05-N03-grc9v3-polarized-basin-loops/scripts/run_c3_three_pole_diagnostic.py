#!/usr/bin/env python3
"""Run C3 three-pole phase-substrate diagnostics.

C3 is a new diagnostic surface.  It asks whether a three-pole phase target
`R1 -> R2 -> R3 -> R1` can support recurrent ordered cycling under fixed
topology.  This script implements C3.1-C3.4: fixture/masks, observables,
synthetic validator, and real fixed-topology GRC9V3 runtime execution.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence

from run_null_structured_lanes import (  # noqa: E402
    GRC9V3,
    GRC9V3NodeState,
    GRC9V3State,
    PortEdge,
    PortGraphBackend,
    _budget_record,
    _coherence_map,
    _flux_map,
    _project_simplex,
    port_id_to_slot,
)
from loop_observables import load_json, write_json, write_jsonl  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "c3_three_pole_diagnostic_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "c3_three_pole_diagnostic_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "c3_three_pole_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "c3_three_pole_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_c3_three_pole_diagnostic.py"
)


def _three_pole_fixture(*, node_count: int = 12) -> dict[str, Any]:
    return {
        "fixture_id": "c3_three_pole_ported_ring_v1",
        "type": "three_pole_ported_ring",
        "node_count": node_count,
        "edge_count": node_count,
        "nodes": list(range(node_count)),
        "edges": [
            {
                "edge_id": edge_id,
                "node_u": edge_id,
                "port_u": 6,
                "node_v": (edge_id + 1) % node_count,
                "port_v": 4,
                "orientation": "clockwise",
                "base_conductance": 1.0,
                "geometric_length": 1.0,
                "flux_uv_initial": 0.0,
            }
            for edge_id in range(node_count)
        ],
        "poles": {
            "R1": [0, 1],
            "R2": [4, 5],
            "R3": [8, 9],
        },
        "channels": {
            "R1_R2": [1, 2, 3],
            "R2_R3": [5, 6, 7],
            "R3_R1": [9, 10, 11],
        },
        "internal_edges": {
            "R1": [0],
            "R2": [4],
            "R3": [8],
        },
        "phase_target": ["R1", "R2", "R3", "R1"],
        "same_parent_basin_mode": "configured_parent_region_only",
    }


def _int_value(mapping: Mapping[Any, Any], key: int) -> float:
    if key in mapping:
        return float(mapping[key])
    return float(mapping.get(str(key), 0.0))


def _region_mass(coherence: Mapping[Any, Any], nodes: Iterable[int]) -> float:
    return sum(_int_value(coherence, int(node_id)) for node_id in nodes)


def _channel_flux(flux_uv: Mapping[Any, Any], edges: Iterable[int]) -> float:
    return sum(_int_value(flux_uv, int(edge_id)) for edge_id in edges)


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _pole_rows(
    *,
    fixture: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    poles = fixture["poles"]
    channels = fixture["channels"]
    rows: list[dict[str, Any]] = []
    for record in records:
        c_pre = record["C_pre"]
        c_post_continuity = record["C_post_continuity"]
        c_post_budget = record["C_post_budget"]
        flux_uv = record["flux_uv"]
        r1_pre = _region_mass(c_pre, poles["R1"])
        r2_pre = _region_mass(c_pre, poles["R2"])
        r3_pre = _region_mass(c_pre, poles["R3"])
        r1_cont = _region_mass(c_post_continuity, poles["R1"])
        r2_cont = _region_mass(c_post_continuity, poles["R2"])
        r3_cont = _region_mass(c_post_continuity, poles["R3"])
        row = {
            "step_index": int(record["step_index"]),
            "C_R1": _region_mass(c_post_budget, poles["R1"]),
            "C_R2": _region_mass(c_post_budget, poles["R2"]),
            "C_R3": _region_mass(c_post_budget, poles["R3"]),
            "Delta_C_R1_pre_budget": r1_cont - r1_pre,
            "Delta_C_R2_pre_budget": r2_cont - r2_pre,
            "Delta_C_R3_pre_budget": r3_cont - r3_pre,
            "P_R1_R2": _channel_flux(flux_uv, channels["R1_R2"]),
            "P_R2_R3": _channel_flux(flux_uv, channels["R2_R3"]),
            "P_R3_R1": _channel_flux(flux_uv, channels["R3_R1"]),
            "budget_error_post_correction": float(
                record.get("budget", {}).get("after_correction", sum(float(v) for v in c_post_budget.values()))
            )
            - 1.0,
            "budget_correction_magnitude": float(
                record.get("budget", {}).get("correction_magnitude", 0.0)
            ),
        }
        rows.append(row)
    return rows


def _indices(rows: Sequence[Mapping[str, Any]], predicate: Any) -> list[int]:
    return [idx for idx, row in enumerate(rows) if predicate(row)]


def _three_pole_cascades(
    rows: Sequence[Mapping[str, Any]],
    *,
    theta_mass: float,
    theta_flux: float,
    max_stage_lag: int,
) -> list[dict[str, Any]]:
    steps = [int(row["step_index"]) for row in rows]
    r1_drop = _indices(rows, lambda row: float(row["Delta_C_R1_pre_budget"]) < -theta_mass)
    p12 = _indices(rows, lambda row: float(row["P_R1_R2"]) > theta_flux)
    r2_rise = _indices(rows, lambda row: float(row["Delta_C_R2_pre_budget"]) > theta_mass)
    p23 = _indices(rows, lambda row: float(row["P_R2_R3"]) > theta_flux)
    r3_rise = _indices(rows, lambda row: float(row["Delta_C_R3_pre_budget"]) > theta_mass)
    p31 = _indices(rows, lambda row: float(row["P_R3_R1"]) > theta_flux)
    r1_rise = _indices(rows, lambda row: float(row["Delta_C_R1_pre_budget"]) > theta_mass)
    stage_sets = (p12, r2_rise, p23, r3_rise, p31, r1_rise)
    cascades: list[dict[str, Any]] = []
    consumed_refills: set[int] = set()
    for first in r1_drop:
        stages = [first]
        cursor = first
        for candidates in stage_sets:
            next_index = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate > cursor
                    and candidate - cursor <= max_stage_lag
                    and (candidates is not r1_rise or candidate not in consumed_refills)
                ),
                None,
            )
            if next_index is None:
                stages = []
                break
            stages.append(next_index)
            cursor = next_index
        if len(stages) != 7:
            continue
        consumed_refills.add(stages[-1])
        cascades.append(
            {
                "R1_drop_step": steps[stages[0]],
                "P_R1_R2_step": steps[stages[1]],
                "R2_rise_step": steps[stages[2]],
                "P_R2_R3_step": steps[stages[3]],
                "R3_rise_step": steps[stages[4]],
                "P_R3_R1_step": steps[stages[5]],
                "R1_refill_step": steps[stages[6]],
            }
        )
    return cascades


def _summarize_pole_rows(
    *,
    rows: Sequence[Mapping[str, Any]],
    lane_id: str,
    runner_mode: str,
    metric_config: Mapping[str, Any],
) -> dict[str, Any]:
    washout = int(metric_config["washout_steps"])
    min_eval = int(metric_config["min_eval_steps"])
    theta_mass = float(metric_config["theta_mass"])
    theta_flux = float(metric_config["theta_export"])
    max_stage_lag = int(metric_config["phase_cascade_max_stage_lag"])
    n_cycles_min = int(metric_config["n_cycles_min"])
    eval_rows = [row for row in rows if int(row["step_index"]) >= washout]
    eval_rows = eval_rows[:min_eval] if len(eval_rows) >= min_eval else eval_rows
    p12_mean = _mean([float(row["P_R1_R2"]) for row in eval_rows])
    p23_mean = _mean([float(row["P_R2_R3"]) for row in eval_rows])
    p31_mean = _mean([float(row["P_R3_R1"]) for row in eval_rows])
    network_closure = min(
        _clip01(p12_mean / theta_flux if theta_flux else 0.0),
        _clip01(p23_mean / theta_flux if theta_flux else 0.0),
        _clip01(p31_mean / theta_flux if theta_flux else 0.0),
    )
    cascades = _three_pole_cascades(
        eval_rows,
        theta_mass=theta_mass,
        theta_flux=theta_flux,
        max_stage_lag=max_stage_lag,
    )
    raw_count = len(cascades)
    role_gate = p12_mean > theta_flux and p23_mean > theta_flux and p31_mean > theta_flux
    role_gated_count = raw_count if role_gate else 0
    budget_passed = max((abs(float(row["budget_error_post_correction"])) for row in rows), default=0.0) <= 1e-9
    candidate_allowed = (
        runner_mode != "synthetic_trace_validator"
        and budget_passed
        and role_gated_count >= n_cycles_min
    )
    return {
        "lane_id": lane_id,
        "runner_mode": runner_mode,
        "network_closure_score": network_closure,
        "P_R1_R2_mean": p12_mean,
        "P_R2_R3_mean": p23_mean,
        "P_R3_R1_mean": p31_mean,
        "raw_three_pole_cascade_count": raw_count,
        "role_gated_three_pole_cascade_count": role_gated_count,
        "n_cycles_min": n_cycles_min,
        "phase_pattern_target": "R1 -> R2 -> R3 -> R1",
        "three_pole_candidate_claim_allowed": candidate_allowed,
        "budget_passed": budget_passed,
        "cascades": cascades[:10],
        "blocked_reasons": [
            reason
            for reason, blocked in (
                ("synthetic_trace_not_runtime_evidence", runner_mode == "synthetic_trace_validator"),
                ("budget_gate_failed", not budget_passed),
                ("role_gated_cycle_gate_failed", role_gated_count < n_cycles_min),
                ("three_pole_diagnostic_claim_ceiling", True),
            )
            if blocked
        ],
    }


def _empty_flux() -> dict[str, float]:
    return {str(edge_id): 0.0 for edge_id in range(12)}


def _coherence_from_pole_masses(r1: float, r2: float, r3: float) -> dict[str, float]:
    values = {str(node_id): 0.02 for node_id in range(12)}
    for node_id in (0, 1):
        values[str(node_id)] = r1 / 2.0
    for node_id in (4, 5):
        values[str(node_id)] = r2 / 2.0
    for node_id in (8, 9):
        values[str(node_id)] = r3 / 2.0
    neutral = 1.0 - sum(values.values())
    for node_id in (2, 3, 6, 7, 10, 11):
        values[str(node_id)] += neutral / 6.0
    return values


def _synthetic_records(kind: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    masses = [0.2, 0.2, 0.2]
    for step in range(90):
        pre = _coherence_from_pole_masses(*masses)
        post = dict(pre)
        flux = _empty_flux()
        cycle_pos = step % 18
        if kind == "ordered":
            if cycle_pos == 2:
                masses[0] -= 0.01
            elif cycle_pos == 3:
                flux.update({"1": 0.001, "2": 0.001, "3": 0.001})
            elif cycle_pos == 4:
                masses[1] += 0.01
            elif cycle_pos == 5:
                masses[1] -= 0.01
                flux.update({"5": 0.001, "6": 0.001, "7": 0.001})
            elif cycle_pos == 6:
                masses[2] += 0.01
            elif cycle_pos == 7:
                masses[2] -= 0.01
                flux.update({"9": 0.001, "10": 0.001, "11": 0.001})
            elif cycle_pos == 8:
                masses[0] += 0.01
        elif kind == "scrambled":
            if cycle_pos in {2, 5, 8}:
                flux.update({"9": 0.001, "10": 0.001, "11": 0.001})
        elif kind == "two_pole":
            if cycle_pos == 2:
                masses[0] -= 0.01
                flux.update({"1": 0.001, "2": 0.001, "3": 0.001})
            elif cycle_pos == 3:
                masses[1] += 0.01
        post = _coherence_from_pole_masses(*masses)
        budget_after = sum(post.values())
        if kind == "budget_drift" and step > 30:
            budget_after += 0.01
        records.append(
            {
                "step_index": step,
                "C_pre": pre,
                "C_post_continuity": post,
                "C_post_budget": post,
                "flux_uv": flux,
                "budget": {
                    "before_continuity": 1.0,
                    "after_continuity": budget_after,
                    "after_correction": budget_after,
                    "correction_method": "synthetic",
                    "correction_magnitude": 0.0,
                },
            }
        )
    return records


def _synthetic_suite(metric_config: Mapping[str, Any]) -> dict[str, Any]:
    fixture = _three_pole_fixture()
    reports: dict[str, Any] = {}
    expected = {
        "ordered": True,
        "scrambled": False,
        "two_pole": False,
        "budget_drift": False,
    }
    errors: list[str] = []
    for lane_id in expected:
        records = _synthetic_records(lane_id)
        rows = _pole_rows(fixture=fixture, records=records)
        path = TIMESERIES_DIR / f"c3_synthetic_{lane_id}.jsonl"
        write_jsonl(path, rows)
        report = _summarize_pole_rows(
            rows=rows,
            lane_id=lane_id,
            runner_mode="synthetic_trace_validator",
            metric_config=metric_config,
        )
        detected = report["role_gated_three_pole_cascade_count"] >= int(metric_config["n_cycles_min"])
        if detected != expected[lane_id]:
            errors.append(f"synthetic {lane_id} expected detected={expected[lane_id]} got {detected}")
        reports[lane_id] = report
    return {"reports": reports, "errors": errors}


def _runtime_initial_values(lane_id: str, *, budget: float = 1.0) -> dict[int, float]:
    node_count = 12
    values = [budget / node_count for _ in range(node_count)]
    if lane_id == "P":
        for node_id in (0, 1):
            values[node_id] += 0.02
        for node_id in (4, 5):
            values[node_id] += 0.005
        for node_id in (8, 9):
            values[node_id] -= 0.01
    elif lane_id == "P_reversed":
        for node_id in (8, 9):
            values[node_id] += 0.02
        for node_id in (4, 5):
            values[node_id] += 0.005
        for node_id in (0, 1):
            values[node_id] -= 0.01
    elif lane_id == "U3":
        for node_id in (0, 1, 4, 5, 8, 9):
            values[node_id] += 0.01
    projected = _project_simplex(values, budget=budget)
    return {node_id: value for node_id, value in enumerate(projected)}


def _runtime_state(lane_id: str, manifest: Mapping[str, Any]) -> GRC9V3State:
    fixture = _three_pole_fixture()
    topology = PortGraphBackend()
    for node_id in fixture["nodes"]:
        allocated = topology.add_node({"role": f"c3_{lane_id}_{node_id}"})
        if int(allocated) != int(node_id):
            raise RuntimeError("C3 fixture expects contiguous node ids")
    nodes = {
        node_id: GRC9V3NodeState(
            coherence=coherence,
            basin_mass=coherence,
            basin_id="configured_parent_basin",
            parent_id="configured_parent_basin",
            depth=0,
        )
        for node_id, coherence in _runtime_initial_values(
            lane_id,
            budget=float(manifest["budget"]["total_budget"]),
        ).items()
    }
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for edge in fixture["edges"]:
        edge_id = topology.connect_ports(
            int(edge["node_u"]),
            port_id_to_slot(int(edge["port_u"])),
            int(edge["node_v"]),
            port_id_to_slot(int(edge["port_v"])),
            {"orientation": "clockwise"},
        )
        port_edges[edge_id] = PortEdge(
            node_u=int(edge["node_u"]),
            port_u=int(edge["port_u"]),
            node_v=int(edge["node_v"]),
            port_v=int(edge["port_v"]),
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0
    return GRC9V3State(
        topology=topology,
        nodes=nodes,
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
        potential={node_id: node.coherence for node_id, node in nodes.items()},
        sink_set=set(),
        basins={0: set(nodes)},
        hierarchy={"configured_parent_basin": list(nodes)},
        budget_target=float(manifest["budget"]["total_budget"]),
        cached_quantities={"budget_target_source": "c3_fixture_budget"},
        edge_label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "transport_ratio",
            "flux_coupling": "absolute_flux",
        },
    )


def _runtime_model(lane_id: str, manifest: Mapping[str, Any]) -> GRC9V3:
    return GRC9V3.from_state(
        _runtime_state(lane_id, manifest),
        {
            "dt": float(manifest["runner_config"]["dt"]),
            "constitutive_semantic_modes": {
                "boundary_mode": "prune",
                "quadrature_mode": "unit_measure",
                "budget_correction_method": "simplex_projection",
                "spark_lane": "current_hybrid_signed_hessian",
            },
            "evolution": {
                "lambda_birth": 0.0,
                "alpha_seed": 0.1,
                "rng_seed": 0,
            },
        },
    )


def _run_runtime_lane(lane_id: str, manifest: Mapping[str, Any]) -> dict[str, Any]:
    model = _runtime_model(lane_id, manifest)
    raw: list[dict[str, Any]] = []
    initial_nodes = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edges = len(tuple(model._state.topology.iter_live_edge_ids()))
    for step in range(int(manifest["runner_config"]["total_steps"])):
        c_pre = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        flux = _flux_map(model)
        model.apply_continuity()
        c_post_continuity = _coherence_map(model)
        budget_summary = model.enforce_quadrature_budget()
        c_post_budget = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()
        raw.append(
            {
                "step_index": step,
                "C_pre": c_pre,
                "C_post_continuity": c_post_continuity,
                "C_post_budget": c_post_budget,
                "flux_uv": flux,
                "budget": _budget_record(
                    c_pre=c_pre,
                    c_post_continuity=c_post_continuity,
                    c_post_budget=c_post_budget,
                    summary=budget_summary,
                ),
            }
        )
    raw_path = RAW_RECORD_DIR / f"c3_runtime_{lane_id.lower()}_raw_records.jsonl"
    write_jsonl(raw_path, raw)
    fixture = _three_pole_fixture()
    rows = _pole_rows(fixture=fixture, records=raw)
    ts_path = TIMESERIES_DIR / f"c3_runtime_{lane_id.lower()}_timeseries.jsonl"
    write_jsonl(ts_path, rows)
    report = _summarize_pole_rows(
        rows=rows,
        lane_id=lane_id,
        runner_mode="c3_fixed_topology_continuity_runner",
        metric_config=manifest["metric_config_defaults"],
    )
    final_nodes = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edges = len(tuple(model._state.topology.iter_live_edge_ids()))
    report["topology"] = {
        "initial_node_count": initial_nodes,
        "final_node_count": final_nodes,
        "initial_edge_count": initial_edges,
        "final_edge_count": final_edges,
        "changed": initial_nodes != final_nodes or initial_edges != final_edges,
    }
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["timeseries"] = {"artifact_path": str(ts_path)}
    return report


def _runtime_suite(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reports = {
        lane_id: _run_runtime_lane(lane_id, manifest)
        for lane_id in ("U0", "U3", "P", "P_reversed")
    }
    errors = [
        f"{lane_id} changed topology"
        for lane_id, report in reports.items()
        if report["topology"]["changed"]
    ]
    return {"reports": reports, "errors": errors}


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# C3 Three-Pole Diagnostic Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "C3 is a three-pole diagnostic surface, not a positive loop-claim tranche.",
        "",
        "## Synthetic Validator",
        "",
        "| Lane | Raw Cascades | Role-Gated Cascades | Budget |",
        "| --- | ---: | ---: | --- |",
    ]
    for lane_id, report in result["synthetic"]["reports"].items():
        lines.append(
            f"| {lane_id} | {report['raw_three_pole_cascade_count']} | "
            f"{report['role_gated_three_pole_cascade_count']} | {report['budget_passed']} |"
        )
    lines.extend(
        [
            "",
            "## Runtime Fixed-Topology",
            "",
            "| Lane | Network Closure | Raw Cascades | Role-Gated Cascades | Candidate | Topology Changed |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for lane_id, report in result["runtime"]["reports"].items():
        lines.append(
            "| {lane} | {closure:.6g} | {raw} | {gated} | {candidate} | {topology} |".format(
                lane=lane_id,
                closure=report["network_closure_score"],
                raw=report["raw_three_pole_cascade_count"],
                gated=report["role_gated_three_pole_cascade_count"],
                candidate=report["three_pole_candidate_claim_allowed"],
                topology=report["topology"]["changed"],
            )
        )
    lines.extend(
        [
            "",
            "## Classification",
            "",
            f"`{result['classification']}`",
            "",
            "## Errors",
            "",
        ]
    )
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    synthetic = _synthetic_suite(manifest["metric_config_defaults"])
    runtime = _runtime_suite(manifest)
    runtime_candidates = [
        lane_id
        for lane_id, report in runtime["reports"].items()
        if report["three_pole_candidate_claim_allowed"]
    ]
    errors = list(synthetic["errors"]) + list(runtime["errors"])
    classification = (
        "c3_runtime_candidate_rows_observed"
        if runtime_candidates
        else "c3_fixed_topology_no_three_pole_candidate_rows"
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_c3_three_pole_diagnostic_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": COMMAND,
        "claim_ceiling": "three_pole_diagnostic_surface_not_positive_loop_claim",
        "fixture": _three_pole_fixture(),
        "synthetic": synthetic,
        "runtime": runtime,
        "runtime_candidate_lanes": runtime_candidates,
        "classification": classification,
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification,
                "runtime_candidate_lanes": runtime_candidates,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
