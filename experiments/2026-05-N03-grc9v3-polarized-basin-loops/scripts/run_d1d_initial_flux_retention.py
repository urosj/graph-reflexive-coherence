#!/usr/bin/env python3
"""Run D1d initial circulating-flux retention audit.

D1d asks whether native GRC9V3 treats initialized closed-ring `flux_uv` as a
persistent corridor-flow state or whether rebuild_transport_state overwrites it
with potential-driven proposal flux.  It does not add a circulatory proposal
term, edge storage, phase controller, topology change, or src/* change.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

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
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1d_initial_flux_retention.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1d_initial_flux_retention.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "d1d_initial_flux_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d1d_initial_flux_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1d_initial_flux_retention.py"
)

MATERIAL_RETENTION_THRESHOLD = 0.1
MATERIAL_NORMALIZED_THRESHOLD = 0.01


def _initial_values(profile: str, *, node_count: int, budget: float) -> dict[int, float]:
    base = budget / node_count
    values: list[float] = []
    for node_id in range(node_count):
        theta = 2.0 * math.pi * float(node_id) / float(node_count)
        if profile == "uniform":
            value = base
        elif profile == "single_bump":
            value = base + 0.03 * math.exp(1.5 * math.cos(theta))
        elif profile == "traveling_phase_seed":
            value = base + 0.025 * math.sin(theta) + 0.015 * math.sin(2.0 * theta + math.pi / 3.0)
        elif profile == "source_sink":
            value = base
            if node_id in (0, 1):
                value += 0.015
            if node_id in (6, 7):
                value -= 0.015
        else:
            raise ValueError(f"unsupported D1d profile: {profile}")
        values.append(value)
    projected = _project_simplex(values, budget=budget)
    return {node_id: float(value) for node_id, value in enumerate(projected)}


def _state(
    *,
    manifest: Mapping[str, Any],
    profile: str,
    initial_flux: float,
    flux_direction: int,
) -> GRC9V3State:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    topology = PortGraphBackend()
    for node_id in fixture["nodes"]:
        allocated = topology.add_node({"role": f"d1d_{profile}_{node_id}"})
        if int(allocated) != int(node_id):
            raise RuntimeError("D1d fixture expects contiguous node ids from zero")
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
            raise RuntimeError("D1d fixture expects contiguous edge ids from zero")
        flux_uv = float(flux_direction) * float(initial_flux)
        port_edges[edge_id] = PortEdge(
            node_u=int(edge["node_u"]),
            port_u=int(edge["port_u"]),
            node_v=int(edge["node_v"]),
            port_v=int(edge["port_v"]),
            conductance=float(edge.get("base_conductance", defaults["base_conductance"])),
            flux_uv=flux_uv,
        )
        base_conductance[edge_id] = float(edge.get("base_conductance", defaults["base_conductance"]))
        geometric_length[edge_id] = float(edge.get("geometric_length", defaults["geometric_length"]))
        temporal_delay[edge_id] = float(edge.get("temporal_delay_initial", defaults["temporal_delay_initial"]))
        flux_coupling[edge_id] = abs(flux_uv)
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
            "d1d_initial_flux": float(initial_flux),
            "d1d_initial_flux_direction": int(flux_direction),
        },
        edge_label_computation_mode={
            "geometric_length": "fixed_port_chart",
            "temporal_delay": "transport_ratio",
            "flux_coupling": "initial_absolute_flux",
        },
    )


def _model(
    *,
    manifest: Mapping[str, Any],
    profile: str,
    initial_flux: float,
    flux_direction: int,
) -> GRC9V3:
    return GRC9V3.from_state(
        _state(
            manifest=manifest,
            profile=profile,
            initial_flux=initial_flux,
            flux_direction=flux_direction,
        ),
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


def _cycle_metrics(flux_uv: Mapping[str, float], edge_count: int) -> dict[str, float]:
    values = [float(flux_uv.get(str(edge_id), 0.0)) for edge_id in range(edge_count)]
    signed = sum(values)
    abs_sum = sum(abs(value) for value in values)
    mean = fmean(values) if values else 0.0
    mean_abs = fmean([abs(value) for value in values]) if values else 0.0
    return {
        "loop_circulation": signed,
        "loop_abs_flux_sum": abs_sum,
        "loop_mean_flux": mean,
        "loop_mean_abs_flux": mean_abs,
        "loop_normalized_circulation": signed / abs_sum if abs_sum > 0.0 else 0.0,
    }


def _run_retention_scenario(
    *,
    manifest: Mapping[str, Any],
    scenario_id: str,
    profile: str,
    initial_flux: float,
    flux_direction: int,
) -> dict[str, Any]:
    model = _model(
        manifest=manifest,
        profile=profile,
        initial_flux=initial_flux,
        flux_direction=flux_direction,
    )
    edge_count = len(model._state.port_edges)
    total_steps = int(manifest["runner_config"]["total_steps"])
    initial_flux_uv = _flux_map(model)
    initial_metrics = _cycle_metrics(initial_flux_uv, edge_count)
    raw_records: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    first_rebuild_metrics: dict[str, float] | None = None
    for step_index in range(total_steps):
        c_pre = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        flux_uv = _flux_map(model)
        metrics = _cycle_metrics(flux_uv, edge_count)
        if first_rebuild_metrics is None:
            first_rebuild_metrics = dict(metrics)
        model.apply_continuity()
        c_post_continuity = _coherence_map(model)
        budget_summary = model.enforce_quadrature_budget()
        c_post_budget = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()
        row = {"step_index": step_index, **metrics}
        rows.append(row)
        raw_records.append(
            {
                "step_index": step_index,
                "C_pre": c_pre,
                "C_post_continuity": c_post_continuity,
                "C_post_budget": c_post_budget,
                "flux_uv": flux_uv,
                "circulation": metrics,
                "budget": _budget_record(
                    c_pre=c_pre,
                    c_post_continuity=c_post_continuity,
                    c_post_budget=c_post_budget,
                    summary=budget_summary,
                ),
            }
        )
    raw_path = RAW_RECORD_DIR / f"{scenario_id}_raw_records.jsonl"
    ts_path = TIMESERIES_DIR / f"{scenario_id}_retention.jsonl"
    write_jsonl(raw_path, raw_records)
    write_jsonl(ts_path, rows)
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    post_budget_errors = [
        abs(float(record["budget"]["after_correction"]) - float(manifest["budget"]["total_budget"]))
        for record in raw_records
    ]
    initial_signed = abs(initial_metrics["loop_circulation"])
    first_signed = abs((first_rebuild_metrics or {})["loop_circulation"])
    final_signed = abs(rows[-1]["loop_circulation"]) if rows else 0.0
    initial_abs_sum = initial_metrics["loop_abs_flux_sum"]
    first_abs_sum = (first_rebuild_metrics or {}).get("loop_abs_flux_sum", 0.0)
    final_abs_sum = rows[-1]["loop_abs_flux_sum"] if rows else 0.0
    max_norm = max((abs(row["loop_normalized_circulation"]) for row in rows), default=0.0)
    return {
        "scenario_id": scenario_id,
        "profile": profile,
        "initial_flux": float(initial_flux),
        "flux_direction": int(flux_direction),
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
        "retention": {
            "initial_loop_circulation": initial_metrics["loop_circulation"],
            "first_rebuild_loop_circulation": (first_rebuild_metrics or {}).get("loop_circulation", 0.0),
            "final_loop_circulation": rows[-1]["loop_circulation"] if rows else 0.0,
            "initial_abs_flux_sum": initial_abs_sum,
            "first_rebuild_abs_flux_sum": first_abs_sum,
            "final_abs_flux_sum": final_abs_sum,
            "first_rebuild_signed_retention_ratio": first_signed / initial_signed if initial_signed > 0.0 else None,
            "final_signed_retention_ratio": final_signed / initial_signed if initial_signed > 0.0 else None,
            "first_rebuild_abs_flux_retention_ratio": first_abs_sum / initial_abs_sum if initial_abs_sum > 0.0 else None,
            "final_abs_flux_retention_ratio": final_abs_sum / initial_abs_sum if initial_abs_sum > 0.0 else None,
            "max_abs_normalized_circulation_after_rebuild": max_norm,
        },
        "raw_records": {"artifact_path": str(raw_path)},
        "timeseries": {"artifact_path": str(ts_path)},
    }


def _scenario_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for initial_flux in (0.01, 0.05, 0.1):
        specs.append(
            {
                "scenario_id": f"d1d_uniform_clockwise_flux_{str(initial_flux).replace('.', 'p')}",
                "profile": "uniform",
                "initial_flux": initial_flux,
                "flux_direction": 1,
            }
        )
    for profile in ("single_bump", "source_sink", "traveling_phase_seed"):
        specs.append(
            {
                "scenario_id": f"d1d_{profile}_clockwise_flux_0p05",
                "profile": profile,
                "initial_flux": 0.05,
                "flux_direction": 1,
            }
        )
    specs.append(
        {
            "scenario_id": "d1d_source_sink_counterclockwise_flux_0p05",
            "profile": "source_sink",
            "initial_flux": 0.05,
            "flux_direction": -1,
        }
    )
    return specs


def _summarize(scenarios: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows: list[dict[str, Any]] = []
    retained_rows: list[str] = []
    material_rows: list[str] = []
    for scenario in scenarios:
        retention = scenario["retention"]
        first_ratio = retention["first_rebuild_signed_retention_ratio"]
        max_norm = float(retention["max_abs_normalized_circulation_after_rebuild"])
        if first_ratio is not None and float(first_ratio) >= MATERIAL_RETENTION_THRESHOLD:
            retained_rows.append(str(scenario["scenario_id"]))
        if max_norm >= MATERIAL_NORMALIZED_THRESHOLD:
            material_rows.append(str(scenario["scenario_id"]))
        compact_rows.append(
            {
                "scenario_id": scenario["scenario_id"],
                "initial_flux": scenario["initial_flux"],
                "initial_loop_circulation": retention["initial_loop_circulation"],
                "first_rebuild_loop_circulation": retention["first_rebuild_loop_circulation"],
                "final_loop_circulation": retention["final_loop_circulation"],
                "first_rebuild_signed_retention_ratio": first_ratio,
                "final_signed_retention_ratio": retention["final_signed_retention_ratio"],
                "first_rebuild_abs_flux_retention_ratio": retention["first_rebuild_abs_flux_retention_ratio"],
                "max_abs_normalized_circulation_after_rebuild": max_norm,
                "topology_changed": scenario["topology"]["changed"],
                "budget_passed": scenario["budget"]["passed"],
            }
        )
    if material_rows:
        classification = "d1d_material_circulation_after_initial_flux"
    elif retained_rows:
        classification = "d1d_initial_flux_partly_retained_without_material_circulation"
    else:
        classification = "d1d_initial_flux_erased_by_transport_rebuild"
    return {
        "scenario_count": len(compact_rows),
        "compact_rows": compact_rows,
        "retained_rows": retained_rows,
        "material_rows": material_rows,
        "classification": classification,
        "thresholds": {
            "material_signed_retention_min": MATERIAL_RETENTION_THRESHOLD,
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
        "# D1d Initial Circulating-Flux Retention Audit",
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
        "D1d initializes a closed ring with nonzero clockwise/counter-clockwise",
        "`flux_uv` on every edge, then runs the native fixed-topology GRC9V3",
        "transport rebuild. It tests whether initialized flux behaves like",
        "persistent corridor flow.",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Init Flux | Init Circ | First Rebuild Circ | Final Circ | First Signed Retention | Final Signed Retention | First Abs-Flux Retention | Max Norm After Rebuild |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        first_ratio = row["first_rebuild_signed_retention_ratio"]
        final_ratio = row["final_signed_retention_ratio"]
        abs_ratio = row["first_rebuild_abs_flux_retention_ratio"]
        lines.append(
            "| {scenario} | {initial_flux:.6g} | {initial:.6g} | {first:.6g} | {final:.6g} | {first_ratio} | {final_ratio} | {abs_ratio} | {max_norm:.6g} |".format(
                scenario=row["scenario_id"],
                initial_flux=row["initial_flux"],
                initial=row["initial_loop_circulation"],
                first=row["first_rebuild_loop_circulation"],
                final=row["final_loop_circulation"],
                first_ratio="n/a" if first_ratio is None else f"{float(first_ratio):.6g}",
                final_ratio="n/a" if final_ratio is None else f"{float(final_ratio):.6g}",
                abs_ratio="n/a" if abs_ratio is None else f"{float(abs_ratio):.6g}",
                max_norm=row["max_abs_normalized_circulation_after_rebuild"],
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
        _run_retention_scenario(manifest=manifest, **spec)
        for spec in _scenario_specs()
    ]
    summary = _summarize(scenarios)
    interpretation = (
        "D1d tests initialized flux as a native GRC9V3 state surface. If "
        "transport rebuild erases the initialized signed circulation, then "
        "`flux_uv` is behaving as a recomputed proposal rather than a persistent "
        "corridor-flow or momentum state. Any blood/vein-like closed-flow model "
        "would need explicit edge/corridor coherence, packet, accumulator, or "
        "momentum state outside plain native GRC9V3 fixed-topology continuity."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1d_initial_flux_retention_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "target": "closed-ring initialized flux retention under native GRC9V3 transport rebuild",
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
                "retained_rows": result["summary"]["retained_rows"],
                "material_rows": result["summary"]["material_rows"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
