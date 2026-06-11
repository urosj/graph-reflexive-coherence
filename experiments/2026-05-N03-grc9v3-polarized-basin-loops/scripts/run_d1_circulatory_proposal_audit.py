#!/usr/bin/env python3
"""Run D1 circulatory proposal audit.

D1 asks whether the current GRC9V3 proposal surface can produce nonzero signed
loop circulation around a closed cycle, independent of source/sink masks.  It
does not add circulatory terms, phase controllers, topology changes, or src/*
changes.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping

from loop_observables import load_json, write_json, write_jsonl  # noqa: E402
from run_kick_lanes import _apply_zero_sum_kick  # noqa: E402
from run_null_structured_lanes import (  # noqa: E402
    GRC9V3,
    GRC9V3NodeState,
    _budget_record,
    _coherence_map,
    _flux_map,
    _project_simplex,
    _state_from_manifest,
)
from run_c3_three_pole_diagnostic import _runtime_model, _three_pole_fixture  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d1_circulatory_proposal_audit.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d1_circulatory_proposal_audit.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "d1_circulation_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d1_circulation_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d1_circulatory_proposal_audit.py"
)


def _make_grc9v3_model(manifest: Mapping[str, Any], *, lane_id: str) -> GRC9V3:
    state = _state_from_manifest(manifest=manifest, lane_id=lane_id)
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


def _apply_ring_profile(model: GRC9V3, profile: str, *, budget: float) -> None:
    node_ids = sorted(model._state.nodes)
    count = len(node_ids)
    base = budget / count
    values: list[float] = []
    for index, _node_id in enumerate(node_ids):
        theta = 2.0 * math.pi * float(index) / float(count)
        if profile == "sinusoid":
            value = base + 0.025 * math.sin(theta)
        elif profile == "traveling_phase_seed":
            value = base + 0.018 * math.sin(theta) + 0.012 * math.sin(2.0 * theta + math.pi / 3.0)
        elif profile == "sawtooth":
            value = base + 0.02 * (float(index) / float(count - 1) - 0.5)
        else:
            raise ValueError(f"unsupported ring profile: {profile}")
        values.append(value)
    projected = _project_simplex(values, budget=budget)
    for node_id, coherence in zip(node_ids, projected):
        node = model._state.nodes[node_id]
        model._state.nodes[node_id] = GRC9V3NodeState(
            coherence=float(coherence),
            gradient_row_basis=list(node.gradient_row_basis),
            signed_hessian_row_basis=list(node.signed_hessian_row_basis),
            net_flux_summary=list(node.net_flux_summary),
            basin_mass=node.basin_mass,
            basin_id=node.basin_id,
            parent_id=node.parent_id,
            depth=node.depth,
        )


def _closed_cycle_edge_ids(model: GRC9V3) -> list[int]:
    return sorted(int(edge_id) for edge_id in model._state.port_edges)


def _circulation_metrics(
    *,
    flux_uv: Mapping[str, float],
    cycle_edges: list[int],
    channel_edges: Mapping[str, list[int]] | None = None,
) -> dict[str, Any]:
    values = [float(flux_uv.get(str(edge_id), 0.0)) for edge_id in cycle_edges]
    signed = sum(values)
    abs_sum = sum(abs(value) for value in values)
    metrics: dict[str, Any] = {
        "loop_circulation": signed,
        "loop_abs_flux_sum": abs_sum,
        "loop_mean_abs_flux": fmean([abs(value) for value in values]) if values else 0.0,
        "loop_normalized_circulation": signed / abs_sum if abs_sum > 0.0 else 0.0,
    }
    if channel_edges is not None:
        for channel_id, edge_ids in channel_edges.items():
            metrics[f"{channel_id}_circulation"] = sum(
                float(flux_uv.get(str(edge_id), 0.0)) for edge_id in edge_ids
            )
    return metrics


def _run_model_audit(
    *,
    manifest: Mapping[str, Any],
    scenario_id: str,
    model: GRC9V3,
    channel_edges: Mapping[str, list[int]] | None = None,
) -> dict[str, Any]:
    cycle_edges = _closed_cycle_edge_ids(model)
    total_steps = int(manifest["runner_config"]["total_steps"])
    raw_records: list[dict[str, Any]] = []
    circulation_rows: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    for step_index in range(total_steps):
        c_pre = _coherence_map(model)
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        flux_uv = _flux_map(model)
        circ = _circulation_metrics(
            flux_uv=flux_uv,
            cycle_edges=cycle_edges,
            channel_edges=channel_edges,
        )
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
                "circulation": circ,
                "budget": _budget_record(
                    c_pre=c_pre,
                    c_post_continuity=c_post_continuity,
                    c_post_budget=c_post_budget,
                    summary=budget_summary,
                ),
            }
        )
        circulation_rows.append({"step_index": step_index, **circ})
    raw_path = RAW_RECORD_DIR / f"{scenario_id}_raw_records.jsonl"
    ts_path = TIMESERIES_DIR / f"{scenario_id}_circulation.jsonl"
    write_jsonl(raw_path, raw_records)
    write_jsonl(ts_path, circulation_rows)
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    abs_circ = [abs(float(row["loop_circulation"])) for row in circulation_rows]
    norm_circ = [abs(float(row["loop_normalized_circulation"])) for row in circulation_rows]
    mean_abs_flux = [float(row["loop_mean_abs_flux"]) for row in circulation_rows]
    post_budget_errors = [
        abs(float(record["budget"]["after_correction"]) - float(manifest["budget"]["total_budget"]))
        for record in raw_records
    ]
    return {
        "scenario_id": scenario_id,
        "cycle_edges": cycle_edges,
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
        "circulation": {
            "max_abs_loop_circulation": max(abs_circ, default=0.0),
            "mean_abs_loop_circulation": fmean(abs_circ) if abs_circ else 0.0,
            "max_abs_normalized_circulation": max(norm_circ, default=0.0),
            "mean_abs_normalized_circulation": fmean(norm_circ) if norm_circ else 0.0,
            "initial_loop_circulation": circulation_rows[0]["loop_circulation"] if circulation_rows else 0.0,
            "final_loop_circulation": circulation_rows[-1]["loop_circulation"] if circulation_rows else 0.0,
            "initial_mean_abs_flux": mean_abs_flux[0] if mean_abs_flux else 0.0,
            "final_mean_abs_flux": mean_abs_flux[-1] if mean_abs_flux else 0.0,
            "persistence_ratio_final_over_initial_abs": (
                abs(circulation_rows[-1]["loop_circulation"])
                / abs(circulation_rows[0]["loop_circulation"])
                if circulation_rows and abs(circulation_rows[0]["loop_circulation"]) > 1e-15
                else None
            ),
        },
        "raw_records": {"artifact_path": str(raw_path)},
        "timeseries": {"artifact_path": str(ts_path)},
    }


def _ring_scenarios(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for lane_id in ("U0", "U1", "S"):
        model = _make_grc9v3_model(manifest, lane_id=lane_id)
        scenarios.append(
            _run_model_audit(
                manifest=manifest,
                scenario_id=f"d1_ring_{lane_id.lower()}",
                model=model,
            )
        )
    k_model = _make_grc9v3_model(manifest, lane_id="U2")
    _apply_zero_sum_kick(model=k_model, manifest=manifest)
    scenarios.append(
        _run_model_audit(manifest=manifest, scenario_id="d1_ring_kick", model=k_model)
    )
    for profile in ("sinusoid", "traveling_phase_seed", "sawtooth"):
        model = _make_grc9v3_model(manifest, lane_id="U2")
        _apply_ring_profile(
            model,
            profile,
            budget=float(manifest["budget"]["total_budget"]),
        )
        scenarios.append(
            _run_model_audit(
                manifest=manifest,
                scenario_id=f"d1_ring_profile_{profile}",
                model=model,
            )
        )
    return scenarios


def _three_pole_scenarios(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    fixture = _three_pole_fixture()
    channels = {
        channel_id: [int(edge_id) for edge_id in edge_ids]
        for channel_id, edge_ids in fixture["channels"].items()
    }
    return [
        _run_model_audit(
            manifest=manifest,
            scenario_id=f"d1_three_pole_{lane_id.lower()}",
            model=_runtime_model(lane_id, manifest),
            channel_edges=channels,
        )
        for lane_id in ("U0", "U3", "P", "P_reversed")
    ]


def _summarize(scenarios: list[Mapping[str, Any]]) -> dict[str, Any]:
    compact = [
        {
            "scenario_id": scenario["scenario_id"],
            "max_abs_loop_circulation": scenario["circulation"]["max_abs_loop_circulation"],
            "mean_abs_loop_circulation": scenario["circulation"]["mean_abs_loop_circulation"],
            "max_abs_normalized_circulation": scenario["circulation"]["max_abs_normalized_circulation"],
            "initial_loop_circulation": scenario["circulation"]["initial_loop_circulation"],
            "final_loop_circulation": scenario["circulation"]["final_loop_circulation"],
            "initial_mean_abs_flux": scenario["circulation"]["initial_mean_abs_flux"],
            "final_mean_abs_flux": scenario["circulation"]["final_mean_abs_flux"],
            "topology_changed": scenario["topology"]["changed"],
            "budget_passed": scenario["budget"]["passed"],
        }
        for scenario in scenarios
    ]
    max_norm = max((row["max_abs_normalized_circulation"] for row in compact), default=0.0)
    max_abs = max((row["max_abs_loop_circulation"] for row in compact), default=0.0)
    if max_abs <= 1e-12:
        classification = "d1_no_loop_circulation_observed"
    elif max_norm < 0.01:
        classification = "d1_weak_residual_loop_circulation_observed"
    else:
        classification = "d1_material_loop_circulation_observed"
    return {
        "scenario_count": len(scenarios),
        "compact_rows": compact,
        "max_abs_loop_circulation": max_abs,
        "max_abs_normalized_circulation": max_norm,
        "classification": classification,
        "classification_thresholds": {
            "none_abs_max": 1e-12,
            "material_normalized_min": 0.01,
        },
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for scenario in result["scenarios"]:
        if scenario["topology"]["changed"]:
            errors.append(f"{scenario['scenario_id']} changed topology")
        if not scenario["budget"]["passed"]:
            errors.append(f"{scenario['scenario_id']} failed budget audit")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D1 Circulatory Proposal Audit",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "D1 audits the existing GRC9V3 proposal surface. It does not add",
        "circulatory terms, phase controllers, or topology changes.",
        "",
        f"Classification: `{result['summary']['classification']}`",
        f"Max abs loop circulation: `{result['summary']['max_abs_loop_circulation']}`",
        f"Max abs normalized circulation: `{result['summary']['max_abs_normalized_circulation']}`",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Max Abs Circ | Max Norm Circ | Initial Circ | Final Circ | Initial Mean Abs Flux | Final Mean Abs Flux |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {scenario} | {max_abs:.6g} | {max_norm:.6g} | {initial:.6g} | {final:.6g} | {initial_flux:.6g} | {final_flux:.6g} |".format(
                scenario=row["scenario_id"],
                max_abs=row["max_abs_loop_circulation"],
                max_norm=row["max_abs_normalized_circulation"],
                initial=row["initial_loop_circulation"],
                final=row["final_loop_circulation"],
                initial_flux=row["initial_mean_abs_flux"],
                final_flux=row["final_mean_abs_flux"],
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
    scenarios = _ring_scenarios(manifest) + _three_pole_scenarios(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_d1_circulatory_proposal_audit_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "target_metric": "loop_circulation(t) = signed sum of flux_uv around a declared closed cycle",
        "scenarios": scenarios,
        "summary": _summarize(scenarios),
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
                "classification": result["summary"]["classification"],
                "max_abs_loop_circulation": result["summary"]["max_abs_loop_circulation"],
                "max_abs_normalized_circulation": result["summary"]["max_abs_normalized_circulation"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
