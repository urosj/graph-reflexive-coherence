#!/usr/bin/env python3
"""Run D1c native port-rotation circulation audit.

D1c asks whether the existing GRC9V3 row/column port mechanics expose stronger
native circulation when the fixed topology is organized as a local port-cycle
rotation rather than as a direct source/sink channel loop.  It does not add a
circulatory proposal term, phase controller, topology change, or src/* change.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

from loop_observables import load_json, write_json  # noqa: E402
from run_d1_circulatory_proposal_audit import _run_model_audit  # noqa: E402
from run_null_structured_lanes import (  # noqa: E402
    GRC9V3,
    GRC9V3NodeState,
    GRC9V3State,
    PortEdge,
    PortGraphBackend,
    port_id_to_slot,
    _project_simplex,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
D1_OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1_circulatory_proposal_audit.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1c_port_rotation_audit.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1c_port_rotation_audit.md"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1c_port_rotation_audit.py"
)

PORT_PERIMETER_CW = (1, 2, 3, 6, 9, 8, 7, 4)
PORT_PERIMETER_CCW = tuple(reversed(PORT_PERIMETER_CW))
MATERIAL_NORMALIZED_THRESHOLD = 0.01


def _rotation_values(
    profile: str,
    *,
    node_count: int,
    budget: float,
    reverse_phase: bool = False,
) -> dict[int, float]:
    base = budget / node_count
    values: list[float] = []
    for node_id in range(node_count):
        theta = 2.0 * math.pi * float(node_id) / float(node_count)
        if reverse_phase:
            theta = -theta
        if profile == "uniform":
            value = base
        elif profile == "single_bump":
            value = base + 0.035 * math.exp(1.4 * math.cos(theta))
        elif profile == "traveling_phase_seed":
            value = (
                base
                + 0.026 * math.sin(theta)
                + 0.017 * math.sin(2.0 * theta + math.pi / 4.0)
                + 0.008 * math.cos(3.0 * theta - math.pi / 6.0)
            )
        elif profile == "quadrature":
            value = base + 0.022 * math.sin(theta) - 0.018 * math.cos(2.0 * theta)
        elif profile == "alternating":
            value = base + (0.02 if node_id % 2 == 0 else -0.02)
        else:
            raise ValueError(f"unsupported rotation profile: {profile}")
        values.append(value)
    projected = _project_simplex(values, budget=budget)
    return {node_id: float(value) for node_id, value in enumerate(projected)}


def _rotation_state(
    *,
    port_cycle: Sequence[int],
    profile: str,
    manifest: Mapping[str, Any],
    reverse_phase: bool = False,
) -> GRC9V3State:
    node_count = len(port_cycle)
    topology = PortGraphBackend()
    for node_id in range(node_count):
        allocated = topology.add_node({"role": f"d1c_rotation_{profile}_{node_id}"})
        if int(allocated) != node_id:
            raise RuntimeError("D1c rotation fixture expects contiguous node ids")

    coherence = _rotation_values(
        profile,
        node_count=node_count,
        budget=float(manifest["budget"]["total_budget"]),
        reverse_phase=reverse_phase,
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
    for node_id in range(node_count):
        next_node_id = (node_id + 1) % node_count
        port_id = int(port_cycle[node_id])
        edge_id = topology.connect_ports(
            node_id,
            port_id_to_slot(port_id),
            next_node_id,
            port_id_to_slot(port_id),
            {
                "orientation": "port_rotation",
                "port_cycle_index": node_id,
                "port_id": port_id,
            },
        )
        if int(edge_id) != node_id:
            raise RuntimeError("D1c rotation fixture expects contiguous edge ids")
        port_edges[edge_id] = PortEdge(
            node_u=node_id,
            port_u=port_id,
            node_v=next_node_id,
            port_v=port_id,
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
        cached_quantities={
            "budget_target_source": "fixture_manifest_budget",
            "d1c_port_cycle": list(port_cycle),
        },
        edge_label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "transport_ratio",
            "flux_coupling": "absolute_flux",
        },
    )


def _rotation_model(
    *,
    manifest: Mapping[str, Any],
    port_cycle: Sequence[int],
    profile: str,
    reverse_phase: bool = False,
) -> GRC9V3:
    state = _rotation_state(
        port_cycle=port_cycle,
        profile=profile,
        manifest=manifest,
        reverse_phase=reverse_phase,
    )
    return GRC9V3.from_state(
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


def _scenario_specs() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": "d1c_rotation_cw_uniform",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "uniform",
        },
        {
            "scenario_id": "d1c_rotation_cw_single_bump",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "single_bump",
        },
        {
            "scenario_id": "d1c_rotation_cw_traveling_phase_seed",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "traveling_phase_seed",
        },
        {
            "scenario_id": "d1c_rotation_cw_quadrature",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "quadrature",
        },
        {
            "scenario_id": "d1c_rotation_cw_alternating",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "alternating",
        },
        {
            "scenario_id": "d1c_rotation_ccw_traveling_phase_seed",
            "port_cycle": PORT_PERIMETER_CCW,
            "profile": "traveling_phase_seed",
        },
        {
            "scenario_id": "d1c_rotation_ccw_quadrature",
            "port_cycle": PORT_PERIMETER_CCW,
            "profile": "quadrature",
        },
        {
            "scenario_id": "d1c_rotation_cw_traveling_phase_seed_reversed",
            "port_cycle": PORT_PERIMETER_CW,
            "profile": "traveling_phase_seed",
            "reverse_phase": True,
        },
    ]


def _summarize(scenarios: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        compact_rows.append(
            {
                "scenario_id": scenario["scenario_id"],
                "max_abs_loop_circulation": scenario["circulation"]["max_abs_loop_circulation"],
                "mean_abs_loop_circulation": scenario["circulation"]["mean_abs_loop_circulation"],
                "max_abs_normalized_circulation": scenario["circulation"]["max_abs_normalized_circulation"],
                "mean_abs_normalized_circulation": scenario["circulation"]["mean_abs_normalized_circulation"],
                "initial_loop_circulation": scenario["circulation"]["initial_loop_circulation"],
                "final_loop_circulation": scenario["circulation"]["final_loop_circulation"],
                "initial_mean_abs_flux": scenario["circulation"]["initial_mean_abs_flux"],
                "final_mean_abs_flux": scenario["circulation"]["final_mean_abs_flux"],
                "topology_changed": scenario["topology"]["changed"],
                "budget_passed": scenario["budget"]["passed"],
            }
        )
    max_norm = max((row["max_abs_normalized_circulation"] for row in compact_rows), default=0.0)
    max_abs = max((row["max_abs_loop_circulation"] for row in compact_rows), default=0.0)
    material_rows = [
        row["scenario_id"]
        for row in compact_rows
        if row["max_abs_normalized_circulation"] >= MATERIAL_NORMALIZED_THRESHOLD
    ]
    if material_rows:
        classification = "d1c_material_port_rotation_circulation_observed"
    elif max_abs > 1e-12:
        classification = "d1c_weak_residual_port_rotation_circulation_observed"
    else:
        classification = "d1c_no_port_rotation_circulation_observed"
    return {
        "scenario_count": len(compact_rows),
        "compact_rows": compact_rows,
        "max_abs_loop_circulation": max_abs,
        "max_abs_normalized_circulation": max_norm,
        "material_rows": material_rows,
        "classification": classification,
        "classification_thresholds": {
            "none_abs_max": 1e-12,
            "material_normalized_min": MATERIAL_NORMALIZED_THRESHOLD,
        },
    }


def _d1_baseline() -> dict[str, Any]:
    if not D1_OUTPUT_PATH.exists():
        return {"available": False}
    d1 = load_json(D1_OUTPUT_PATH)
    summary = d1.get("summary", {})
    return {
        "available": True,
        "classification": summary.get("classification"),
        "max_abs_loop_circulation": summary.get("max_abs_loop_circulation"),
        "max_abs_normalized_circulation": summary.get("max_abs_normalized_circulation"),
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
        "# D1c Port-Rotation Circulation Audit",
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
        f"Max abs loop circulation: `{result['summary']['max_abs_loop_circulation']}`",
        f"Max abs normalized circulation: `{result['summary']['max_abs_normalized_circulation']}`",
        "",
        "D1c audits native GRC9V3 fixed-topology port-rotation fixtures. It",
        "does not add a circulatory proposal term or modify `src/*`.",
        "",
        "Port cycle:",
        "",
        "```text",
        "clockwise: 1 -> 2 -> 3 -> 6 -> 9 -> 8 -> 7 -> 4 -> 1",
        "counter-clockwise: reverse(clockwise)",
        "```",
        "",
        "## Baseline",
        "",
        "Prior D1 direct/channel-flow baseline:",
        "",
        "```json",
        json.dumps(result["d1_baseline"], indent=2, sort_keys=True),
        "```",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Max Abs Circ | Mean Abs Circ | Max Norm Circ | Mean Norm Circ | Initial Circ | Final Circ | Final Mean Abs Flux |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {scenario} | {max_abs:.6g} | {mean_abs:.6g} | {max_norm:.6g} | {mean_norm:.6g} | {initial:.6g} | {final:.6g} | {final_flux:.6g} |".format(
                scenario=row["scenario_id"],
                max_abs=row["max_abs_loop_circulation"],
                mean_abs=row["mean_abs_loop_circulation"],
                max_norm=row["max_abs_normalized_circulation"],
                mean_norm=row["mean_abs_normalized_circulation"],
                initial=row["initial_loop_circulation"],
                final=row["final_loop_circulation"],
                final_flux=row["final_mean_abs_flux"],
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
    scenarios = []
    for spec in _scenario_specs():
        model = _rotation_model(
            manifest=manifest,
            port_cycle=spec["port_cycle"],
            profile=spec["profile"],
            reverse_phase=bool(spec.get("reverse_phase", False)),
        )
        scenario = _run_model_audit(
            manifest=manifest,
            scenario_id=spec["scenario_id"],
            model=model,
            channel_edges={
                "port_rotation_cycle": list(range(len(spec["port_cycle"]))),
            },
        )
        scenario["port_rotation_fixture"] = {
            "port_cycle": list(spec["port_cycle"]),
            "profile": spec["profile"],
            "reverse_phase": bool(spec.get("reverse_phase", False)),
        }
        scenarios.append(scenario)
    summary = _summarize(scenarios)
    interpretation = (
        "Port-rotation fixtures are native GRC9V3 fixed-topology tests. "
        "A material result would require normalized circulation >= "
        f"{MATERIAL_NORMALIZED_THRESHOLD}. Weak residual rows remain diagnostic "
        "only and do not promote loop evidence."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1c_port_rotation_audit_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "target_metric": "port_rotation_loop_circulation(t) = signed sum of flux_uv around a declared port-cycle fixture",
        "port_cycle": {
            "clockwise": list(PORT_PERIMETER_CW),
            "counter_clockwise": list(PORT_PERIMETER_CCW),
        },
        "d1_baseline": _d1_baseline(),
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
                "max_abs_loop_circulation": result["summary"]["max_abs_loop_circulation"],
                "max_abs_normalized_circulation": result["summary"]["max_abs_normalized_circulation"],
                "material_rows": result["summary"]["material_rows"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
