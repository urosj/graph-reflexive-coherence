#!/usr/bin/env python3
"""Run Branch C1 delayed/accumulator channel substrate.

C1 is a redesigned execution surface for the N03 polarized-basin-loop
experiment.  It uses existing GRC9V3 state/transport rebuilding to compute flux
proposals, but channel movement is applied through experiment-local delayed
accumulator queues.  Budget is audited as node coherence plus in-flight channel
storage.
"""

from __future__ import annotations

import copy
import json
from collections import deque
from pathlib import Path
from typing import Any, Mapping

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)
from run_kick_lanes import _apply_zero_sum_kick  # noqa: E402
from run_null_structured_lanes import (  # noqa: E402
    GRC9V3,
    GRC9V3NodeState,
    _coherence_map,
    _flux_map,
    _state_from_manifest,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "c1_delayed_accumulator_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "c1_delayed_accumulator_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "c1_delayed_accumulator_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "c1_delayed_accumulator_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_c1_delayed_accumulator.py"
)


def _manifest_for_lane(manifest: Mapping[str, Any], *, reversed_masks: bool) -> dict[str, Any]:
    lane_manifest = copy.deepcopy(dict(manifest))
    lane_manifest["scope"]["runner_mode"] = "c1_delayed_accumulator_runner"
    lane_manifest["runner_config"]["runner_sequence"] = [
        "C_pre",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "capture_flux_proposals",
        "compute_accumulator_departures",
        "apply_accumulator_arrivals",
        "capture_C_post_accumulator",
        "audit_nodes_plus_in_flight_budget",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "rebuild_identity_state",
        "experiment_local_loop_observables",
    ]
    lane_manifest["diagnostic_branch"] = {
        "branch": "C1",
        "runner_mode": "c1_delayed_accumulator_runner",
        "claim_surface": "redesigned_fixture_theory_surface",
        "full_l_positive_allowed": False,
        "reason": "same_parent_basin_mode remains configured_parent_region_only",
    }
    if reversed_masks:
        fixture = lane_manifest["fixtures"]["grc9v3_ported_ring_v1"]
        fixture["masks"] = {
            **fixture["masks"],
            **fixture["reversed_masks"],
        }
        fixture["masks"]["same_parent_basin_mode"] = "configured_parent_region_only"
    return lane_manifest


def _make_model(manifest: Mapping[str, Any], *, lane_id: str) -> GRC9V3:
    state_lane = "S" if lane_id == "S" else "U2"
    state = _state_from_manifest(manifest=manifest, lane_id=state_lane)
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


def _node_total(model: GRC9V3) -> float:
    return sum(float(node.coherence) for node in model._state.nodes.values())


def _queue_total(queue: deque[float]) -> float:
    return sum(float(value) for value in queue)


def _int_flux(flux_uv: Mapping[str, float], edge_id: int) -> float:
    return float(flux_uv.get(str(edge_id), 0.0))


def _region_mass(model: GRC9V3, nodes: list[int]) -> float:
    return sum(float(model._state.nodes[node_id].coherence) for node_id in nodes)


def _remove_from_region(model: GRC9V3, nodes: list[int], amount: float) -> float:
    amount = max(0.0, float(amount))
    mass = _region_mass(model, nodes)
    if mass <= 0.0 or amount <= 0.0:
        return 0.0
    actual = min(amount, mass)
    for node_id in nodes:
        node = model._state.nodes[node_id]
        share = float(node.coherence) / mass
        model._state.nodes[node_id] = GRC9V3NodeState(
            coherence=max(0.0, float(node.coherence) - actual * share),
            gradient_row_basis=list(node.gradient_row_basis),
            signed_hessian_row_basis=list(node.signed_hessian_row_basis),
            net_flux_summary=list(node.net_flux_summary),
            basin_mass=node.basin_mass,
            basin_id=node.basin_id,
            parent_id=node.parent_id,
            depth=node.depth,
        )
    return actual


def _add_to_region(model: GRC9V3, nodes: list[int], amount: float) -> float:
    amount = max(0.0, float(amount))
    if not nodes or amount <= 0.0:
        return 0.0
    per_node = amount / float(len(nodes))
    for node_id in nodes:
        node = model._state.nodes[node_id]
        model._state.nodes[node_id] = GRC9V3NodeState(
            coherence=float(node.coherence) + per_node,
            gradient_row_basis=list(node.gradient_row_basis),
            signed_hessian_row_basis=list(node.signed_hessian_row_basis),
            net_flux_summary=list(node.net_flux_summary),
            basin_mass=node.basin_mass,
            basin_id=node.basin_id,
            parent_id=node.parent_id,
            depth=node.depth,
        )
    return amount


def _effective_flux_map(
    *,
    fixture: Mapping[str, Any],
    forward_departure: float,
    forward_arrival: float,
    return_departure: float,
    return_arrival: float,
    dt: float,
) -> dict[str, float]:
    masks = fixture["masks"]
    effective = {str(edge["edge_id"]): 0.0 for edge in fixture["edges"]}
    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    return_edges = [int(edge_id) for edge_id in masks["return_channel_edges"]]
    if dt <= 0.0:
        return effective
    if forward_edges:
        effective[str(forward_edges[0])] += forward_departure / dt
        effective[str(forward_edges[-1])] += forward_arrival / dt
    if return_edges:
        effective[str(return_edges[0])] += return_departure / dt
        effective[str(return_edges[-1])] += return_arrival / dt
    return effective


def _step_accumulator(
    *,
    model: GRC9V3,
    manifest: Mapping[str, Any],
    forward_queue: deque[float],
    return_queue: deque[float],
) -> dict[str, Any]:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    dt = float(manifest["runner_config"]["dt"])
    source_nodes = [int(node_id) for node_id in masks["source_aspect_nodes"]]
    sink_nodes = [int(node_id) for node_id in masks["sink_aspect_nodes"]]
    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    return_edges = [int(edge_id) for edge_id in masks["return_channel_edges"]]

    c_pre = _coherence_map(model)
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    proposal_flux_uv = _flux_map(model)

    forward_proposal = max(0.0, _int_flux(proposal_flux_uv, forward_edges[0])) if forward_edges else 0.0
    return_proposal = max(0.0, _int_flux(proposal_flux_uv, return_edges[0])) if return_edges else 0.0
    forward_departure_target = dt * forward_proposal
    return_departure_target = dt * return_proposal

    forward_departure = _remove_from_region(model, source_nodes, forward_departure_target)
    return_departure = _remove_from_region(model, sink_nodes, return_departure_target)
    forward_queue.append(forward_departure)
    return_queue.append(return_departure)
    forward_arrival = forward_queue.popleft()
    return_arrival = return_queue.popleft()
    _add_to_region(model, sink_nodes, forward_arrival)
    _add_to_region(model, source_nodes, return_arrival)

    c_post = _coherence_map(model)
    node_total = _node_total(model)
    in_flight = _queue_total(forward_queue) + _queue_total(return_queue)
    budget_total = node_total + in_flight
    target = float(manifest["budget"]["total_budget"])
    effective_flux_uv = _effective_flux_map(
        fixture=fixture,
        forward_departure=forward_departure,
        forward_arrival=forward_arrival,
        return_departure=return_departure,
        return_arrival=return_arrival,
        dt=dt,
    )
    return {
        "C_pre": c_pre,
        "C_post_continuity": c_post,
        "C_post_budget": c_post,
        "flux_uv": effective_flux_uv,
        "proposal_flux_uv": proposal_flux_uv,
        "budget": {
            "before_continuity": target,
            "after_continuity": budget_total,
            "after_correction": budget_total,
            "correction_method": "none_accumulator_exact_budget",
            "correction_magnitude": 0.0,
            "simplex_projection_applied": False,
            "uniform_shift_applied": False,
        },
        "accumulator": {
            "forward_departure": forward_departure,
            "forward_arrival": forward_arrival,
            "return_departure": return_departure,
            "return_arrival": return_arrival,
            "forward_queue_total": _queue_total(forward_queue),
            "return_queue_total": _queue_total(return_queue),
            "in_flight_total": in_flight,
            "node_total": node_total,
            "nodes_plus_in_flight_total": budget_total,
            "budget_error": budget_total - target,
        },
    }


def _run_lane(
    *,
    base_manifest: Mapping[str, Any],
    lane_id: str,
    delay_steps: int,
    reversed_masks: bool = False,
) -> dict[str, Any]:
    manifest = _manifest_for_lane(base_manifest, reversed_masks=reversed_masks)
    model = _make_model(manifest, lane_id=lane_id)
    if lane_id in {"K", "K_reversed"}:
        _apply_zero_sum_kick(model=model, manifest=manifest)
    forward_queue: deque[float] = deque([0.0] * delay_steps)
    return_queue: deque[float] = deque([0.0] * delay_steps)
    raw_records: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))

    for step_index in range(int(manifest["runner_config"]["total_steps"])):
        step = _step_accumulator(
            model=model,
            manifest=manifest,
            forward_queue=forward_queue,
            return_queue=return_queue,
        )
        raw_records.append({"step_index": step_index, **step})
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()

    row_id = f"c1_{lane_id.lower()}_delay_{delay_steps}"
    raw_path = RAW_RECORD_DIR / f"{row_id}_raw_records.jsonl"
    write_jsonl(raw_path, raw_records)
    rows = compute_observable_rows(
        manifest=manifest,
        records=raw_records,
        fixture_id="grc9v3_ported_ring_v1",
    )
    timeseries_path = TIMESERIES_DIR / f"{row_id}_timeseries.jsonl"
    write_jsonl(timeseries_path, rows)
    report = summarize_observables(
        manifest=manifest,
        rows=rows,
        lane_id=lane_id,
        fixture_id="grc9v3_ported_ring_v1",
        timeseries_path=timeseries_path,
        controls_status={
            "topology_disabled": "configured_and_audited_no_events",
            "zero_flux_reset": "fresh_accumulator_queues_zeroed",
            "randomized_labels_posthoc": "not_run_c1_initial",
            "shuffled_conductance": "not_run_c1_initial",
            "budget_projection_disabled_dry_run": "not_applicable_accumulator_exact_budget",
        },
        runtime_provenance_override={
            "runner_mode": "c1_delayed_accumulator_runner",
            "called_methods": manifest["runner_config"]["runner_sequence"],
        },
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    report["topology"]["initial_node_count"] = initial_node_count
    report["topology"]["final_node_count"] = final_node_count
    report["topology"]["initial_edge_count"] = initial_edge_count
    report["topology"]["final_edge_count"] = final_edge_count
    report["topology"]["changed"] = (
        initial_node_count != final_node_count or initial_edge_count != final_edge_count
    )
    report["topology"]["passed_fixed_topology_gate"] = not report["topology"]["changed"]
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["c1_accumulator"] = {
        "delay_steps": delay_steps,
        "budget_surface": "node_coherence_plus_forward_and_return_in_flight_queues",
        "max_abs_budget_error": max(
            abs(float(record["accumulator"]["budget_error"]))
            for record in raw_records
        ),
        "max_in_flight_total": max(
            float(record["accumulator"]["in_flight_total"])
            for record in raw_records
        ),
        "final_in_flight_total": float(raw_records[-1]["accumulator"]["in_flight_total"]),
        "claim_surface": "C1_redesigned_delayed_accumulator_channel",
    }
    report["diagnostic_row"] = {
        "row_id": row_id,
        "lane_id": lane_id,
        "delay_steps": delay_steps,
        "reversed_masks": reversed_masks,
    }
    report["claim_gate"]["c1_candidate_loop_claim_allowed"] = bool(
        report["claim_gate"]["positive_candidate_loop_claim_allowed"]
    )
    report["claim_gate"]["positive_full_loop_claim_allowed"] = False
    if report["claim_gate"]["c1_candidate_loop_claim_allowed"]:
        report["claim_gate"]["blocked_reasons"] = [
            reason
            for reason in report["claim_gate"]["blocked_reasons"]
            if reason != "same_parent_basin_evidence_configured_only"
        ] + ["full_l_positive_blocked_configured_parent_only"]
    return report


def _run_rows(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for delay_steps in (3, 6, 10):
        for lane_id, reversed_masks in (
            ("U0", False),
            ("U2", False),
            ("S", False),
            ("K", False),
            ("K_reversed", True),
        ):
            reports.append(
                _run_lane(
                    base_manifest=manifest,
                    lane_id=lane_id,
                    delay_steps=delay_steps,
                    reversed_masks=reversed_masks,
                )
            )
    return reports


def _classify_reversal(reports: list[Mapping[str, Any]]) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    for delay_steps in (3, 6, 10):
        forward = next(
            report
            for report in reports
            if report["diagnostic_row"]["lane_id"] == "K"
            and report["diagnostic_row"]["delay_steps"] == delay_steps
        )
        reverse = next(
            report
            for report in reports
            if report["diagnostic_row"]["lane_id"] == "K_reversed"
            and report["diagnostic_row"]["delay_steps"] == delay_steps
        )
        pairs.append(
            {
                "delay_steps": delay_steps,
                "k_candidate": forward["claim_gate"]["c1_candidate_loop_claim_allowed"],
                "k_reversed_candidate": reverse["claim_gate"]["c1_candidate_loop_claim_allowed"],
                "k_role_gate": forward["claim_gate"]["role_gate_passed"],
                "k_reversed_role_gate": reverse["claim_gate"]["role_gate_passed"],
                "k_role_gated_cycles": forward["cycles"]["role_gated_cycle_count"],
                "k_reversed_role_gated_cycles": reverse["cycles"]["role_gated_cycle_count"],
            }
        )
    return {"pairs": pairs}


def _summarize(reports: list[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    for report in reports:
        row = report["diagnostic_row"]
        compact = {
            "row_id": row["row_id"],
            "lane_id": row["lane_id"],
            "delay_steps": row["delay_steps"],
            "source_like": report["roles"]["source_like_measured"],
            "sink_like": report["roles"]["sink_like_measured"],
            "raw_cycles": report["cycles"]["raw_cycle_count"],
            "role_gated_cycles": report["cycles"]["role_gated_cycle_count"],
            "c1_candidate_loop_claim_allowed": report["claim_gate"][
                "c1_candidate_loop_claim_allowed"
            ],
            "max_in_flight_total": report["c1_accumulator"]["max_in_flight_total"],
            "max_abs_budget_error": report["c1_accumulator"]["max_abs_budget_error"],
        }
        compact_rows.append(compact)
        if compact["c1_candidate_loop_claim_allowed"]:
            candidate_rows.append(compact)
    return {
        "row_count": len(reports),
        "candidate_row_count": len(candidate_rows),
        "candidate_rows": candidate_rows,
        "compact_rows": compact_rows,
        "classification": (
            "c1_candidate_loop_rows_observed"
            if candidate_rows
            else "c1_no_candidate_loop_rows_observed"
        ),
        "full_l_positive_allowed": False,
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for report in result["reports"]:
        row_id = report["diagnostic_row"]["row_id"]
        if report["topology"]["changed"]:
            errors.append(f"{row_id} changed topology")
        if report["c1_accumulator"]["max_abs_budget_error"] > 1e-9:
            errors.append(f"{row_id} failed nodes+in-flight budget audit")
        if report["claim_gate"]["positive_full_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a full positive claim")
        if report["runtime_provenance"]["runner_mode"] != "c1_delayed_accumulator_runner":
            errors.append(f"{row_id} did not use C1 runner mode")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch C1 Delayed Accumulator Channel Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "C1 uses a redesigned experiment-local execution surface. It computes",
        "GRC9V3 flux proposals, then moves coherence through delayed forward and",
        "return accumulator queues. Budget is audited as nodes plus in-flight",
        "storage.",
        "",
        f"Rows: `{result['summary']['row_count']}`",
        f"Candidate rows: `{result['summary']['candidate_row_count']}`",
        f"Classification: `{result['summary']['classification']}`",
        "",
        "## Row Summary",
        "",
        "| Row | Lane | Delay | Source | Sink | Raw | Role-Gated | C1 Candidate | Max In-Flight | Max Budget Error |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {row_id} | {lane} | {delay} | {source} | {sink} | {raw} | {gated} | {candidate} | {flight:.6g} | {budget:.6g} |".format(
                row_id=row["row_id"],
                lane=row["lane_id"],
                delay=row["delay_steps"],
                source=row["source_like"],
                sink=row["sink_like"],
                raw=row["raw_cycles"],
                gated=row["role_gated_cycles"],
                candidate=row["c1_candidate_loop_claim_allowed"],
                flight=row["max_in_flight_total"],
                budget=row["max_abs_budget_error"],
            )
        )
    lines.extend(
        [
            "",
            "## Reversal",
            "",
            "```json",
            json.dumps(result["reversal"], indent=2, sort_keys=True),
            "```",
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
    reports = _run_rows(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_c1_delayed_accumulator_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "branch": "C1",
        "claim_surface": "redesigned_delayed_accumulator_channel",
        "reports": reports,
        "summary": _summarize(reports),
        "reversal": _classify_reversal(reports),
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
                "rows": result["summary"]["row_count"],
                "candidate_rows": result["summary"]["candidate_row_count"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
