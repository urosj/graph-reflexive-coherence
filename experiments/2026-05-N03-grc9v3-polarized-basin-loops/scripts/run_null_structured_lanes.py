#!/usr/bin/env python3
"""Run Iteration 4 null and structured lanes on real GRC9V3 code.

This runner uses the fixed-topology continuity surface only.  It constructs the
canonical ported-ring fixture, calls the allowed GRC9V3 methods, captures raw
per-step records, and evaluates them with the experiment-local observable
library.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
REPO_ROOT = EXPERIMENT_ROOT.parent.parent
SRC_ROOT = REPO_ROOT / "src"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/pygrc-matplotlib")
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pygrc.core import PortGraphBackend  # noqa: E402
from pygrc.models.grc_9_ports import port_id_to_slot  # noqa: E402
from pygrc.models.grc_9_state import PortEdge  # noqa: E402
from pygrc.models.grc_9_v3 import GRC9V3  # noqa: E402
from pygrc.models.grc_9_v3_state import GRC9V3NodeState, GRC9V3State  # noqa: E402

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)


MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "null_structured_lanes_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "null_structured_lanes_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "null_structured_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "null_structured_timeseries"


def _project_simplex(values: list[float], *, budget: float) -> list[float]:
    clipped = [max(0.0, float(value)) for value in values]
    total = sum(clipped)
    if total <= 0.0:
        return [budget / len(clipped) for _ in clipped]
    return [budget * value / total for value in clipped]


def _ring_theta(node_id: int, node_count: int) -> float:
    return 2.0 * math.pi * float(node_id) / float(node_count)


def _canonical_bump_values(
    *,
    node_count: int,
    budget: float,
    centers: list[float],
    amplitude: float,
    kappa: float,
) -> list[float]:
    values: list[float] = []
    base = budget / node_count
    for node_id in range(node_count):
        theta = _ring_theta(node_id, node_count)
        value = base
        for center in centers:
            value += amplitude * math.exp(kappa * math.cos(theta - center))
        values.append(value)
    return _project_simplex(values, budget=budget)


def _initial_coherence(
    *,
    manifest: Mapping[str, Any],
    lane_id: str,
    fixture: Mapping[str, Any],
) -> dict[int, float]:
    node_count = int(fixture["node_count"])
    budget = float(manifest["budget"]["total_budget"])
    defaults = manifest["initialization"]["default_parameters"]
    masks = fixture["masks"]
    if lane_id in {"U0", "U2"}:
        values = [budget / node_count for _ in range(node_count)]
    elif lane_id == "U1":
        values = _canonical_bump_values(
            node_count=node_count,
            budget=budget,
            centers=[float(value) for value in manifest["lanes"]["U1"]["bump_centers"]],
            amplitude=float(defaults["A"]),
            kappa=float(defaults["kappa"]),
        )
    elif lane_id == "S":
        values = _canonical_bump_values(
            node_count=node_count,
            budget=budget,
            centers=[float(defaults["theta_0"])],
            amplitude=float(defaults["A"]),
            kappa=float(defaults["kappa"]),
        )
        source_nodes = {int(node_id) for node_id in masks["source_aspect_nodes"]}
        sink_nodes = {int(node_id) for node_id in masks["sink_aspect_nodes"]}
        epsilon_s = float(defaults["epsilon_s"])
        epsilon_k = float(defaults["epsilon_k"])
        values = [
            value
            + (epsilon_s if node_id in source_nodes else 0.0)
            - (epsilon_k if node_id in sink_nodes else 0.0)
            for node_id, value in enumerate(values)
        ]
        values = _project_simplex(values, budget=budget)
    else:
        raise ValueError(f"unsupported Iteration 4 lane: {lane_id}")
    return {node_id: float(value) for node_id, value in enumerate(values)}


def _state_from_manifest(
    *,
    manifest: Mapping[str, Any],
    lane_id: str,
    fixture_id: str = "grc9v3_ported_ring_v1",
) -> GRC9V3State:
    fixture = manifest["fixtures"][fixture_id]
    topology = PortGraphBackend()
    for node_id in fixture["nodes"]:
        allocated = topology.add_node({"role": f"{lane_id}_ring_node_{node_id}"})
        if int(allocated) != int(node_id):
            raise RuntimeError("ported-ring fixture expects contiguous node ids from zero")

    nodes = {
        node_id: GRC9V3NodeState(
            coherence=coherence,
            basin_mass=coherence,
            basin_id="configured_parent_basin",
            parent_id="configured_parent_basin",
            depth=0,
        )
        for node_id, coherence in _initial_coherence(
            manifest=manifest,
            lane_id=lane_id,
            fixture=fixture,
        ).items()
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
        expected_edge_id = int(edge["edge_id"])
        if int(edge_id) != expected_edge_id:
            raise RuntimeError("ported-ring fixture expects contiguous edge ids from zero")
        conductance = float(edge.get("base_conductance", defaults["base_conductance"]))
        flux_uv = float(edge.get("flux_uv_initial", defaults["flux_uv_initial"]))
        port_edges[edge_id] = PortEdge(
            node_u=int(edge["node_u"]),
            port_u=int(edge["port_u"]),
            node_v=int(edge["node_v"]),
            port_v=int(edge["port_v"]),
            conductance=conductance,
            flux_uv=flux_uv,
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
        cached_quantities={"budget_target_source": "fixture_manifest_budget"},
        edge_label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "transport_ratio",
            "flux_coupling": "absolute_flux",
        },
    )


def _coherence_map(model: GRC9V3) -> dict[str, float]:
    state = model._state
    return {
        str(node_id): float(state.nodes[node_id].coherence)
        for node_id in sorted(state.nodes)
    }


def _flux_map(model: GRC9V3) -> dict[str, float]:
    state = model._state
    return {
        str(edge_id): float(state.port_edges[edge_id].flux_uv)
        for edge_id in sorted(state.port_edges)
    }


def _potential_map(model: GRC9V3) -> dict[str, float]:
    state = model._state
    return {
        str(node_id): float(state.potential.get(node_id, 0.0))
        for node_id in sorted(state.nodes)
    }


def _edge_surface_map(values: Mapping[int, float]) -> dict[str, float]:
    return {str(edge_id): float(values[edge_id]) for edge_id in sorted(values)}


def _budget_record(
    *,
    c_pre: Mapping[str, float],
    c_post_continuity: Mapping[str, float],
    c_post_budget: Mapping[str, float],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    method = str(
        summary.get("correction_method", summary.get("budget_correction_method", "unknown"))
    )
    return {
        "before_continuity": sum(float(value) for value in c_pre.values()),
        "after_continuity": sum(float(value) for value in c_post_continuity.values()),
        "after_correction": sum(float(value) for value in c_post_budget.values()),
        "correction_method": method,
        "correction_magnitude": float(
            summary.get(
                "correction_magnitude",
                abs(float(summary.get("budget_after", 0.0)) - float(summary.get("budget_before", 0.0))),
            )
        ),
        "simplex_projection_applied": method == "simplex_projection",
        "uniform_shift_applied": method == "uniform_shift",
    }


def _channel_mean(values: Mapping[str, float], edge_ids: list[int]) -> float:
    if not edge_ids:
        return 0.0
    return sum(float(values.get(str(edge_id), 0.0)) for edge_id in edge_ids) / len(edge_ids)


def _node_mean(values: Mapping[str, float], node_ids: list[int]) -> float:
    if not node_ids:
        return 0.0
    return sum(float(values.get(str(node_id), 0.0)) for node_id in node_ids) / len(node_ids)


def _initial_diagnostic_snapshot(
    *,
    manifest: Mapping[str, Any],
    model: GRC9V3,
) -> dict[str, Any]:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    c_values = _coherence_map(model)
    flux_values = _flux_map(model)
    potential_values = _potential_map(model)
    conductance_values = _edge_surface_map(model._state.base_conductance)
    return {
        "source_C_mean": _node_mean(c_values, list(masks["source_aspect_nodes"])),
        "sink_C_mean": _node_mean(c_values, list(masks["sink_aspect_nodes"])),
        "source_sink_C_mean_delta": _node_mean(c_values, list(masks["source_aspect_nodes"]))
        - _node_mean(c_values, list(masks["sink_aspect_nodes"])),
        "source_potential_mean": _node_mean(potential_values, list(masks["source_aspect_nodes"])),
        "sink_potential_mean": _node_mean(potential_values, list(masks["sink_aspect_nodes"])),
        "source_sink_potential_mean_delta": _node_mean(
            potential_values,
            list(masks["source_aspect_nodes"]),
        )
        - _node_mean(potential_values, list(masks["sink_aspect_nodes"])),
        "forward_flux_mean": _channel_mean(flux_values, list(masks["forward_channel_edges"])),
        "return_flux_mean": _channel_mean(flux_values, list(masks["return_channel_edges"])),
        "forward_conductance_mean": _channel_mean(
            conductance_values,
            list(masks["forward_channel_edges"]),
        ),
        "return_conductance_mean": _channel_mean(
            conductance_values,
            list(masks["return_channel_edges"]),
        ),
    }


def _run_lane(manifest: Mapping[str, Any], lane_id: str) -> dict[str, Any]:
    total_steps = int(manifest["runner_config"]["total_steps"])
    state = _state_from_manifest(manifest=manifest, lane_id=lane_id)
    model = GRC9V3.from_state(
        state,
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
    raw_records: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    initial_diagnostics = _initial_diagnostic_snapshot(manifest=manifest, model=model)

    for step_index in range(total_steps):
        c_pre = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        flux_uv = _flux_map(model)
        model.apply_continuity()
        c_post_continuity = _coherence_map(model)
        budget_summary = model.enforce_quadrature_budget()
        c_post_budget = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()
        raw_records.append(
            {
                "step_index": step_index,
                "C_pre": c_pre,
                "C_post_continuity": c_post_continuity,
                "C_post_budget": c_post_budget,
                "flux_uv": flux_uv,
                "budget": _budget_record(
                    c_pre=c_pre,
                    c_post_continuity=c_post_continuity,
                    c_post_budget=c_post_budget,
                    summary=budget_summary,
                ),
            }
        )

    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    raw_path = RAW_RECORD_DIR / f"{lane_id.lower()}_raw_records.jsonl"
    write_jsonl(raw_path, raw_records)
    rows = compute_observable_rows(
        manifest=manifest,
        records=raw_records,
        fixture_id="grc9v3_ported_ring_v1",
    )
    timeseries_path = TIMESERIES_DIR / f"{lane_id.lower()}_timeseries.jsonl"
    write_jsonl(timeseries_path, rows)
    report = summarize_observables(
        manifest=manifest,
        rows=rows,
        lane_id=lane_id,
        fixture_id="grc9v3_ported_ring_v1",
        timeseries_path=timeseries_path,
        controls_status={
            "topology_disabled": "configured_and_audited_no_events",
            "zero_flux_reset": "not_applicable_fresh_transport_rebuild",
            "randomized_labels_posthoc": "not_run_iteration_4",
            "shuffled_conductance": "not_run_iteration_4",
            "budget_projection_disabled_dry_run": "not_run_iteration_4",
        },
    )
    report["runtime_provenance"]["called_methods"] = [
        "rebuild_differential_state",
        "rebuild_transport_state",
        "apply_continuity",
        "enforce_quadrature_budget",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "rebuild_identity_state",
        "experiment_local_loop_observables",
    ]
    report["topology"]["initial_node_count"] = initial_node_count
    report["topology"]["final_node_count"] = final_node_count
    report["topology"]["initial_edge_count"] = initial_edge_count
    report["topology"]["final_edge_count"] = final_edge_count
    report["topology"]["changed"] = (
        initial_node_count != final_node_count or initial_edge_count != final_edge_count
    )
    report["topology"]["passed_fixed_topology_gate"] = not report["topology"]["changed"]
    report["raw_records"] = {
        "artifact_path": str(raw_path),
    }
    report["runtime_diagnostics"] = {
        "initial_transport_snapshot": initial_diagnostics,
        "budget_correction_interpretation": (
            "large correction magnitude would indicate projection is shaping the lane; "
            "Iteration 4 observed magnitudes are reported in budget.max_correction_magnitude"
        ),
    }
    return report


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Iteration 4 Null And Structured Lane Report",
        "",
        "Command:",
        "",
        "```bash",
        "python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_null_structured_lanes.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "This report uses real `GRC9V3` fixed-topology continuity execution. It",
        "does not call `step()`, spark expansion, growth, boundary behavior, birth,",
        "or pruning.",
        "",
        "## Lane Summary",
        "",
        "| Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed | Topology Changed |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for lane_id, report in result["reports"].items():
        lines.append(
            "| {lane} | {budget} | {source} | {sink} | {raw} | {role_gated} | {claim} | {topology} |".format(
                lane=lane_id,
                budget=report["budget"]["passed"],
                source=report["roles"]["source_like_measured"],
                sink=report["roles"]["sink_like_measured"],
                raw=report["cycles"]["raw_cycle_count"],
                role_gated=report["cycles"]["role_gated_cycle_count"],
                claim=report["claim_gate"]["positive_candidate_loop_claim_allowed"],
                topology=report["topology"]["changed"],
            )
        )
    lines.extend(["", "## Blocked Observations", ""])
    blocked = result.get("blocked_observations", [])
    if blocked:
        for observation in blocked:
            lines.append(
                "- `{lane}`: `{kind}`. {interpretation}".format(
                    lane=observation["lane_id"],
                    kind=observation["observation"],
                    interpretation=observation["interpretation"],
                )
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- U0/U1/U2 are null lanes and must not produce L4 positives.",
            "- S is a structured lane; any positive result remains candidate-only",
            "  while `same_parent_basin_mode = configured_parent_region_only`.",
            "- Synthetic smoke results from Iteration 3 remain separate from these",
            "  runtime traces.",
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


def _validate_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for null_lane in ("U0", "U1", "U2"):
        report = result["reports"][null_lane]
        if report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
            errors.append(f"{null_lane} unexpectedly allowed a candidate claim")
        if report["ladder"]["level"] == "L4":
            errors.append(f"{null_lane} unexpectedly reached L4 ladder level")
    for lane_id, report in result["reports"].items():
        if report["topology"]["changed"]:
            errors.append(f"{lane_id} changed topology")
        if not report["budget"]["passed"]:
            errors.append(f"{lane_id} failed budget audit")
        if report["runtime_provenance"]["runner_mode"] != "fixed_topology_continuity_runner":
            errors.append(f"{lane_id} did not use the fixed-topology runner mode")
    return errors


def _blocked_observations(reports: Mapping[str, Any]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for lane_id, report in reports.items():
        if lane_id in {"U0", "U1", "U2"} and report["phase_cascade"]["n_detected_cascades"]:
            observations.append(
                {
                    "lane_id": lane_id,
                    "observation": "null_lane_shape_cascade_without_role_gate",
                    "cascade_count": report["phase_cascade"]["n_detected_cascades"],
                    "role_gate_passed": report["claim_gate"]["role_gate_passed"],
                    "claim_allowed": report["claim_gate"]["positive_candidate_loop_claim_allowed"],
                    "interpretation": (
                        "shape-only cascade evidence is insufficient; null lane remains "
                        "blocked because measured source/sink role evidence fails"
                    ),
                }
            )
    structured = reports.get("S")
    if structured is not None and not structured["claim_gate"]["positive_candidate_loop_claim_allowed"]:
        observations.append(
            {
                "lane_id": "S",
                "observation": "structured_lane_no_candidate_loop_claim",
                "blocked_reasons": list(structured["claim_gate"]["blocked_reasons"]),
                "interpretation": (
                    "the first fixed-topology structured initialization did not produce "
                    "candidate loop evidence above null controls"
                ),
            }
        )
    return observations


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    reports = {lane_id: _run_lane(manifest, lane_id) for lane_id in ("U0", "U1", "U2", "S")}
    result = {
        "schema": "grc9v3_polarized_basin_loop_iteration4_report_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": (
            "python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
            "scripts/run_null_structured_lanes.py"
        ),
        "reports": reports,
        "blocked_observations": _blocked_observations(reports),
        "errors": [],
    }
    errors = _validate_result(result)
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(json.dumps({"status": result["status"], "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
