#!/usr/bin/env python3
"""Run D1e alternating source/sink pole ring audit.

D1e asks whether distributing active source/sink-aspect polarity around the
whole fixed ring can produce stronger native circulation than a single
source/sink pair separated by passive corridor nodes.  It does not add a
circulatory proposal term, role-switching rule, phase controller, topology
change, or src/* change.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence

from loop_observables import load_json, write_json, write_jsonl  # noqa: E402
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


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1e_alternating_pole_ring.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1e_alternating_pole_ring.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "d1e_alternating_pole_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d1e_alternating_pole_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1e_alternating_pole_ring.py"
)

MATERIAL_NORMALIZED_THRESHOLD = 0.01
POLES = {
    "S1": (0, 1),
    "K2": (3, 4),
    "S2": (6, 7),
    "K1": (9, 10),
}
CHANNELS = {
    "S1_to_K2": (1, 2),
    "K2_to_S2": (4, 5),
    "S2_to_K1": (7, 8),
    "K1_to_S1": (10, 11),
}


def _initial_values(profile: str, *, node_count: int, budget: float) -> dict[int, float]:
    base = budget / node_count
    values = [base for _ in range(node_count)]
    if profile == "uniform":
        return {node_id: value for node_id, value in enumerate(values)}

    def add(nodes: Iterable[int], amount: float) -> None:
        for node_id in nodes:
            values[int(node_id)] += amount

    if profile == "alternating":
        add(POLES["S1"], 0.02)
        add(POLES["S2"], 0.02)
        add(POLES["K2"], -0.02)
        add(POLES["K1"], -0.02)
    elif profile == "alternating_strong":
        add(POLES["S1"], 0.04)
        add(POLES["S2"], 0.04)
        add(POLES["K2"], -0.04)
        add(POLES["K1"], -0.04)
    elif profile == "alternating_reversed":
        add(POLES["S1"], -0.02)
        add(POLES["S2"], -0.02)
        add(POLES["K2"], 0.02)
        add(POLES["K1"], 0.02)
    elif profile == "traveling_four_pole":
        for node_id in range(node_count):
            theta = 2.0 * math.pi * float(node_id) / float(node_count)
            values[node_id] += 0.025 * math.sin(2.0 * theta) + 0.012 * math.sin(4.0 * theta + math.pi / 4.0)
    elif profile == "one_active_pair":
        add(POLES["S1"], 0.03)
        add(POLES["K2"], -0.03)
    else:
        raise ValueError(f"unsupported D1e profile: {profile}")
    projected = _project_simplex(values, budget=budget)
    return {node_id: float(value) for node_id, value in enumerate(projected)}


def _state(*, manifest: Mapping[str, Any], profile: str) -> GRC9V3State:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    topology = PortGraphBackend()
    for node_id in fixture["nodes"]:
        allocated = topology.add_node({"role": f"d1e_{profile}_{node_id}"})
        if int(allocated) != int(node_id):
            raise RuntimeError("D1e fixture expects contiguous node ids from zero")
    coherence = _initial_values(
        profile,
        node_count=int(fixture["node_count"]),
        budget=float(manifest["budget"]["total_budget"]),
    )
    nodes = {
        node_id: GRC9V3NodeState(
            coherence=value,
            basin_mass=value,
            basin_id="configured_parent_basin",
            parent_id="configured_parent_basin",
            depth=0,
        )
        for node_id, value in coherence.items()
    }
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    defaults = manifest["default_edge_properties"]
    for edge in fixture["edges"]:
        edge_id = topology.connect_ports(
            int(edge["node_u"]),
            port_id_to_slot(int(edge["port_u"])),
            int(edge["node_v"]),
            port_id_to_slot(int(edge["port_v"])),
            {"orientation": edge.get("orientation", "clockwise")},
        )
        expected = int(edge["edge_id"])
        if int(edge_id) != expected:
            raise RuntimeError("D1e fixture expects contiguous edge ids from zero")
        conductance = float(edge.get("base_conductance", defaults["base_conductance"]))
        port_edges[edge_id] = PortEdge(
            node_u=int(edge["node_u"]),
            port_u=int(edge["port_u"]),
            node_v=int(edge["node_v"]),
            port_v=int(edge["port_v"]),
            conductance=conductance,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = conductance
        geometric_length[edge_id] = float(edge.get("geometric_length", defaults["geometric_length"]))
        temporal_delay[edge_id] = float(edge.get("temporal_delay_initial", defaults["temporal_delay_initial"]))
        flux_coupling[edge_id] = float(edge.get("flux_coupling_initial", defaults["flux_coupling_initial"]))
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
        cached_quantities={
            "budget_target_source": "fixture_manifest_budget",
            "d1e_poles": {key: list(nodes) for key, nodes in POLES.items()},
            "d1e_channels": {key: list(edges) for key, edges in CHANNELS.items()},
        },
        edge_label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "transport_ratio",
            "flux_coupling": "absolute_flux",
        },
    )


def _model(*, manifest: Mapping[str, Any], profile: str) -> GRC9V3:
    return GRC9V3.from_state(
        _state(manifest=manifest, profile=profile),
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


def _edge_flux(flux_uv: Mapping[str, float], edge_id: int) -> float:
    return float(flux_uv.get(str(edge_id), 0.0))


def _channel_flux(flux_uv: Mapping[str, float], edge_ids: Sequence[int]) -> float:
    return sum(_edge_flux(flux_uv, edge_id) for edge_id in edge_ids)


def _region_export(
    *,
    flux_uv: Mapping[str, float],
    region_nodes: Sequence[int],
    port_edges: Mapping[int, PortEdge],
) -> float:
    region = {int(node_id) for node_id in region_nodes}
    export = 0.0
    for edge_id, edge in port_edges.items():
        u_in = int(edge.node_u) in region
        v_in = int(edge.node_v) in region
        if u_in == v_in:
            continue
        flux = _edge_flux(flux_uv, int(edge_id))
        export += flux if u_in else -flux
    return export


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _cycle_count(values: Sequence[float], *, threshold: float = 1e-6) -> int:
    # Count positive-rising threshold crossings as a simple repeated-activity proxy.
    count = 0
    previous = values[0] if values else 0.0
    for value in values[1:]:
        if previous <= threshold < value:
            count += 1
        previous = value
    return count


def _run_scenario(
    *,
    manifest: Mapping[str, Any],
    scenario_id: str,
    profile: str,
) -> dict[str, Any]:
    model = _model(manifest=manifest, profile=profile)
    total_steps = int(manifest["runner_config"]["total_steps"])
    metric_config = manifest["metric_config_defaults"]
    eval_start = int(metric_config["washout_steps"])
    raw_records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    for step_index in range(total_steps):
        c_pre = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        flux_uv = _flux_map(model)
        row: dict[str, Any] = {
            "step_index": step_index,
            "loop_circulation": sum(_edge_flux(flux_uv, edge_id) for edge_id in range(12)),
            "loop_abs_flux_sum": sum(abs(_edge_flux(flux_uv, edge_id)) for edge_id in range(12)),
        }
        row["loop_normalized_circulation"] = (
            row["loop_circulation"] / row["loop_abs_flux_sum"]
            if row["loop_abs_flux_sum"] > 0.0
            else 0.0
        )
        for channel_id, edge_ids in CHANNELS.items():
            row[f"J_{channel_id}"] = _channel_flux(flux_uv, edge_ids)
        for pole_id, node_ids in POLES.items():
            row[f"C_{pole_id}_pre"] = sum(float(c_pre[str(node_id)]) for node_id in node_ids)
            export = _region_export(
                flux_uv=flux_uv,
                region_nodes=node_ids,
                port_edges=model._state.port_edges,
            )
            row[f"export_{pole_id}"] = export
            row[f"import_{pole_id}"] = -export
        model.apply_continuity()
        c_post_continuity = _coherence_map(model)
        for pole_id, node_ids in POLES.items():
            post = sum(float(c_post_continuity[str(node_id)]) for node_id in node_ids)
            row[f"delta_{pole_id}_pre_budget"] = post - row[f"C_{pole_id}_pre"]
        budget_summary = model.enforce_quadrature_budget()
        c_post_budget = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()
        rows.append(row)
        raw_records.append(
            {
                "step_index": step_index,
                "C_pre": c_pre,
                "C_post_continuity": c_post_continuity,
                "C_post_budget": c_post_budget,
                "flux_uv": flux_uv,
                "alternating_pole_row": row,
                "budget": _budget_record(
                    c_pre=c_pre,
                    c_post_continuity=c_post_continuity,
                    c_post_budget=c_post_budget,
                    summary=budget_summary,
                ),
            }
        )
    raw_path = RAW_RECORD_DIR / f"{scenario_id}_raw_records.jsonl"
    ts_path = TIMESERIES_DIR / f"{scenario_id}_timeseries.jsonl"
    write_jsonl(raw_path, raw_records)
    write_jsonl(ts_path, rows)
    eval_rows = rows[eval_start:]
    theta_export = float(metric_config["theta_export"])
    theta_import = float(metric_config["theta_import"])
    theta_mass = float(metric_config["theta_mass"])
    role_evidence: dict[str, Any] = {}
    for pole_id in POLES:
        export_mean = _mean([float(row[f"export_{pole_id}"]) for row in eval_rows])
        import_mean = _mean([float(row[f"import_{pole_id}"]) for row in eval_rows])
        delta_mean = _mean([float(row[f"delta_{pole_id}_pre_budget"]) for row in eval_rows])
        role_evidence[pole_id] = {
            "export_mean": export_mean,
            "import_mean": import_mean,
            "delta_pre_budget_mean": delta_mean,
            "source_like": export_mean > theta_export and delta_mean < -theta_mass,
            "sink_like": import_mean > theta_import and delta_mean > theta_mass,
        }
    channel_means = {
        channel_id: _mean([float(row[f"J_{channel_id}"]) for row in eval_rows])
        for channel_id in CHANNELS
    }
    loop_norms = [abs(float(row["loop_normalized_circulation"])) for row in eval_rows]
    loop_abs = [abs(float(row["loop_circulation"])) for row in eval_rows]
    channel_activity = [
        min(abs(float(row[f"J_{channel_id}"])) for channel_id in CHANNELS)
        for row in eval_rows
    ]
    cycle_proxy_count = _cycle_count(channel_activity)
    expected_roles = {
        "S1": "source_like",
        "K2": "sink_like",
        "S2": "source_like",
        "K1": "sink_like",
    }
    role_pattern_passed = all(
        bool(role_evidence[pole_id][role_key])
        for pole_id, role_key in expected_roles.items()
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    post_budget_errors = [
        abs(float(record["budget"]["after_correction"]) - float(manifest["budget"]["total_budget"]))
        for record in raw_records
    ]
    return {
        "scenario_id": scenario_id,
        "profile": profile,
        "topology": {
            "initial_node_count": initial_node_count,
            "final_node_count": final_node_count,
            "initial_edge_count": initial_edge_count,
            "final_edge_count": final_edge_count,
            "changed": initial_node_count != final_node_count or initial_edge_count != final_edge_count,
        },
        "budget": {
            "max_abs_error_post_correction": max(post_budget_errors, default=0.0),
            "passed": max(post_budget_errors, default=0.0) <= 1e-9,
        },
        "role_evidence": role_evidence,
        "channel_means": channel_means,
        "loop": {
            "max_abs_loop_circulation": max(loop_abs, default=0.0),
            "max_abs_normalized_circulation": max(loop_norms, default=0.0),
            "mean_abs_normalized_circulation": _mean(loop_norms),
            "cycle_proxy_count": cycle_proxy_count,
            "role_pattern_passed": role_pattern_passed,
            "candidate": (
                role_pattern_passed
                and max(loop_norms, default=0.0) >= MATERIAL_NORMALIZED_THRESHOLD
                and cycle_proxy_count >= int(metric_config["n_cycles_min"])
            ),
        },
        "raw_records": {"artifact_path": str(raw_path)},
        "timeseries": {"artifact_path": str(ts_path)},
    }


def _scenario_specs() -> list[dict[str, str]]:
    return [
        {"scenario_id": "d1e_uniform", "profile": "uniform"},
        {"scenario_id": "d1e_alternating", "profile": "alternating"},
        {"scenario_id": "d1e_alternating_strong", "profile": "alternating_strong"},
        {"scenario_id": "d1e_alternating_reversed", "profile": "alternating_reversed"},
        {"scenario_id": "d1e_traveling_four_pole", "profile": "traveling_four_pole"},
        {"scenario_id": "d1e_one_active_pair", "profile": "one_active_pair"},
    ]


def _summarize(scenarios: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows: list[dict[str, Any]] = []
    material_rows: list[str] = []
    role_pattern_rows: list[str] = []
    candidate_rows: list[str] = []
    for scenario in scenarios:
        loop = scenario["loop"]
        scenario_id = str(scenario["scenario_id"])
        if float(loop["max_abs_normalized_circulation"]) >= MATERIAL_NORMALIZED_THRESHOLD:
            material_rows.append(scenario_id)
        if bool(loop["role_pattern_passed"]):
            role_pattern_rows.append(scenario_id)
        if bool(loop["candidate"]):
            candidate_rows.append(scenario_id)
        compact_rows.append(
            {
                "scenario_id": scenario_id,
                "max_abs_normalized_circulation": loop["max_abs_normalized_circulation"],
                "max_abs_loop_circulation": loop["max_abs_loop_circulation"],
                "cycle_proxy_count": loop["cycle_proxy_count"],
                "role_pattern_passed": loop["role_pattern_passed"],
                "candidate": loop["candidate"],
                "topology_changed": scenario["topology"]["changed"],
                "budget_passed": scenario["budget"]["passed"],
            }
        )
    if candidate_rows:
        classification = "d1e_alternating_pole_candidate_rows_observed"
    elif material_rows or role_pattern_rows:
        classification = "d1e_partial_alternating_pole_evidence_only"
    else:
        classification = "d1e_no_alternating_pole_loop_evidence"
    return {
        "scenario_count": len(compact_rows),
        "compact_rows": compact_rows,
        "material_rows": material_rows,
        "role_pattern_rows": role_pattern_rows,
        "candidate_rows": candidate_rows,
        "max_abs_normalized_circulation": max(
            (float(row["max_abs_normalized_circulation"]) for row in compact_rows),
            default=0.0,
        ),
        "classification": classification,
        "thresholds": {
            "material_normalized_circulation_min": MATERIAL_NORMALIZED_THRESHOLD,
        },
    }


def _validate(scenarios: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for scenario in scenarios:
        if scenario["topology"]["changed"]:
            errors.append(f"{scenario['scenario_id']} changed topology")
        if not scenario["budget"]["passed"]:
            errors.append(f"{scenario['scenario_id']} failed budget audit")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D1e Alternating Source/Sink Pole Ring Audit",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{result['summary']['classification']}`",
        "",
        "D1e distributes source/sink-aspect polarity around the fixed ring:",
        "",
        "```text",
        "S1 -> K2 -> S2 -> K1 -> S1",
        "```",
        "",
        "It changes only the fixture/initialization surface; it does not add",
        "role switching, propulsion, edge storage, or a circulatory proposal term.",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Max Norm Circ | Max Abs Circ | Cycle Proxy | Role Pattern | Candidate |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {scenario} | {max_norm:.6g} | {max_abs:.6g} | {cycles} | {roles} | {candidate} |".format(
                scenario=row["scenario_id"],
                max_norm=row["max_abs_normalized_circulation"],
                max_abs=row["max_abs_loop_circulation"],
                cycles=row["cycle_proxy_count"],
                roles="yes" if row["role_pattern_passed"] else "no",
                candidate="yes" if row["candidate"] else "no",
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
    scenarios = [
        _run_scenario(manifest=manifest, **spec)
        for spec in _scenario_specs()
    ]
    summary = _summarize(scenarios)
    interpretation = (
        "D1e tests whether passive intermediate-node loss was the main issue by "
        "distributing active source/sink-aspect regions around the ring. Rows "
        "remain native evidence only if they arise without role switching, "
        "edge storage, propulsion, or a circulatory proposal term."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1e_alternating_pole_ring_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "poles": {key: list(value) for key, value in POLES.items()},
        "channels": {key: list(value) for key, value in CHANNELS.items()},
        "scenarios": scenarios,
        "summary": summary,
        "interpretation": interpretation,
        "errors": [],
    }
    errors = _validate(scenarios)
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": result["summary"]["classification"],
                "candidate_rows": result["summary"]["candidate_rows"],
                "role_pattern_rows": result["summary"]["role_pattern_rows"],
                "material_rows": result["summary"]["material_rows"],
                "max_abs_normalized_circulation": result["summary"]["max_abs_normalized_circulation"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
