#!/usr/bin/env python3
"""Run Iteration 5 one-time zero-sum kick lanes on real GRC9V3 code."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)
from run_null_structured_lanes import (  # noqa: E402
    GRC9V3,
    GRC9V3NodeState,
    _budget_record,
    _coherence_map,
    _flux_map,
    _initial_diagnostic_snapshot,
    _project_simplex,
    _state_from_manifest,
)


EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "kick_lanes_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "kick_lanes_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "kick_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "kick_timeseries"


def _manifest_for_lane(manifest: Mapping[str, Any], *, reversed_masks: bool) -> dict[str, Any]:
    lane_manifest = copy.deepcopy(dict(manifest))
    if reversed_masks:
        fixture = lane_manifest["fixtures"]["grc9v3_ported_ring_v1"]
        fixture["masks"] = {
            **fixture["masks"],
            **fixture["reversed_masks"],
        }
        fixture["masks"]["same_parent_basin_mode"] = "configured_parent_region_only"
        fixture["masks"]["claim_ceiling_note"] = (
            "configured_parent_region_only supports candidate loop claims until "
            "flux_successor_basin evidence is implemented"
        )
    return lane_manifest


def _apply_zero_sum_kick(
    *,
    model: GRC9V3,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    source_nodes = {int(node_id) for node_id in masks["source_aspect_nodes"]}
    sink_nodes = {int(node_id) for node_id in masks["sink_aspect_nodes"]}
    delta = float(manifest["initialization"]["default_parameters"]["kick_delta"])
    ordered_node_ids = sorted(model._state.nodes)
    before_values = [float(model._state.nodes[node_id].coherence) for node_id in ordered_node_ids]
    kicked_values = [
        value
        + (delta if node_id in source_nodes else 0.0)
        - (delta if node_id in sink_nodes else 0.0)
        for node_id, value in zip(ordered_node_ids, before_values)
    ]
    projected_values = _project_simplex(
        kicked_values,
        budget=float(manifest["budget"]["total_budget"]),
    )
    pre_projection_sum = sum(kicked_values)
    post_projection_sum = sum(projected_values)
    projection_l1_delta = sum(
        abs(projected - kicked)
        for projected, kicked in zip(projected_values, kicked_values)
    )
    for node_id, coherence in zip(ordered_node_ids, projected_values):
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
    return {
        "kick_step": int(manifest["lanes"]["K"]["kick_step"]),
        "kick_delta": delta,
        "source_nodes": sorted(source_nodes),
        "sink_nodes": sorted(sink_nodes),
        "pre_kick_sum": sum(before_values),
        "pre_projection_sum": pre_projection_sum,
        "post_projection_sum": post_projection_sum,
        "projection_l1_delta": projection_l1_delta,
        "zero_sum_before_projection": abs(pre_projection_sum - sum(before_values)) <= 1e-12,
        "budget_preserved_after_projection": abs(
            post_projection_sum - float(manifest["budget"]["total_budget"])
        )
        <= 1e-12,
        "external_source_sink_terms_enabled": False,
    }


def _make_model(manifest: Mapping[str, Any], *, lane_id: str) -> GRC9V3:
    state = _state_from_manifest(manifest=manifest, lane_id="U2")
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


def _run_kick_lane(
    *,
    manifest: Mapping[str, Any],
    lane_id: str,
    reversed_masks: bool,
) -> dict[str, Any]:
    lane_manifest = _manifest_for_lane(manifest, reversed_masks=reversed_masks)
    total_steps = int(lane_manifest["runner_config"]["total_steps"])
    model = _make_model(lane_manifest, lane_id=lane_id)
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    kick_audit = _apply_zero_sum_kick(model=model, manifest=lane_manifest)
    initial_diagnostics = _initial_diagnostic_snapshot(manifest=lane_manifest, model=model)
    raw_records: list[dict[str, Any]] = []

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
                "kick_applied": step_index == kick_audit["kick_step"],
            }
        )

    raw_path = RAW_RECORD_DIR / f"{lane_id.lower()}_raw_records.jsonl"
    write_jsonl(raw_path, raw_records)
    rows = compute_observable_rows(
        manifest=lane_manifest,
        records=raw_records,
        fixture_id="grc9v3_ported_ring_v1",
    )
    timeseries_path = TIMESERIES_DIR / f"{lane_id.lower()}_timeseries.jsonl"
    write_jsonl(timeseries_path, rows)
    report = summarize_observables(
        manifest=lane_manifest,
        rows=rows,
        lane_id=lane_id,
        fixture_id="grc9v3_ported_ring_v1",
        timeseries_path=timeseries_path,
        controls_status={
            "topology_disabled": "configured_and_audited_no_events",
            "zero_flux_reset": "not_applicable_fresh_transport_rebuild",
            "randomized_labels_posthoc": "not_run_iteration_5",
            "shuffled_conductance": "blocked_non_informative_uniform_conductance_surface",
            "budget_projection_disabled_dry_run": (
                "blocked_no_separate_approved_projection_disabled_runner"
            ),
        },
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    report["runtime_provenance"]["called_methods"] = [
        "apply_experiment_local_zero_sum_kick",
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
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["kick_audit"] = kick_audit
    report["runtime_diagnostics"] = {
        "initial_transport_snapshot_after_kick": initial_diagnostics,
    }
    report["roles"]["reversal_outcome"] = "pending_pairwise_comparison"
    return report


def _classify_reversal(forward: Mapping[str, Any], reverse: Mapping[str, Any]) -> dict[str, Any]:
    forward_claim = bool(forward["claim_gate"]["positive_candidate_loop_claim_allowed"])
    reverse_claim = bool(reverse["claim_gate"]["positive_candidate_loop_claim_allowed"])
    forward_roles = bool(forward["claim_gate"]["role_gate_passed"])
    reverse_roles = bool(reverse["claim_gate"]["role_gate_passed"])
    if forward_claim and reverse_claim:
        outcome = "antisymmetric_pass"
        reason = "both directions allow candidate claims under their own reversed masks"
    elif forward_claim and not reverse_claim:
        outcome = "substrate_biased_pass"
        reason = "forward kick allows a candidate claim but reversed kick does not"
    elif not forward_claim and reverse_claim:
        outcome = "substrate_biased_pass"
        reason = "reversed kick allows a candidate claim but forward kick does not"
    elif forward_roles or reverse_roles:
        outcome = "failure"
        reason = "role evidence appears in at least one direction but no candidate claim is allowed"
    else:
        outcome = "failure"
        reason = "neither kick direction produced paired role-gated loop evidence"
    return {
        "outcome": outcome,
        "reason": reason,
        "forward_claim_allowed": forward_claim,
        "reversed_claim_allowed": reverse_claim,
        "forward_role_gate": forward_roles,
        "reversed_role_gate": reverse_roles,
        "forward_role_gated_cycles": int(forward["cycles"]["role_gated_cycle_count"]),
        "reversed_role_gated_cycles": int(reverse["cycles"]["role_gated_cycle_count"]),
    }


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Iteration 5 One-Time Kick Lane Report",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_kick_lanes.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "This report uses real `GRC9V3` fixed-topology continuity execution with",
        "one experiment-local zero-sum kick applied before the first transport",
        "rebuild. It does not call `step()`, spark expansion, growth, boundary",
        "behavior, birth, or pruning.",
        "",
        "## Lane Summary",
        "",
        "| Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for lane_id, report in result["reports"].items():
        lines.append(
            "| {lane} | {budget} | {source} | {sink} | {raw} | {role_gated} | {claim} |".format(
                lane=lane_id,
                budget=report["budget"]["passed"],
                source=report["roles"]["source_like_measured"],
                sink=report["roles"]["sink_like_measured"],
                raw=report["cycles"]["raw_cycle_count"],
                role_gated=report["cycles"]["role_gated_cycle_count"],
                claim=report["claim_gate"]["positive_candidate_loop_claim_allowed"],
            )
        )
    reversal = result["reversal"]
    lines.extend(
        [
            "",
            "## Reversal Outcome",
            "",
            f"- outcome: `{reversal['outcome']}`",
            f"- reason: {reversal['reason']}",
            "",
            "## Blocked Controls",
            "",
            "- shuffled conductance: blocked as non-informative for uniform conductance surface",
            "- budget-projection-disabled dry run: blocked pending a separate approved diagnostic runner",
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
    for lane_id, report in result["reports"].items():
        if not report["budget"]["passed"]:
            errors.append(f"{lane_id} failed budget conservation")
        if report["topology"]["changed"]:
            errors.append(f"{lane_id} changed topology")
        if not report["kick_audit"]["zero_sum_before_projection"]:
            errors.append(f"{lane_id} kick was not zero-sum before projection")
        if not report["kick_audit"]["budget_preserved_after_projection"]:
            errors.append(f"{lane_id} kick did not preserve budget after projection")
    if result["reversal"]["outcome"] not in {"antisymmetric_pass", "substrate_biased_pass", "failure"}:
        errors.append("reversal outcome is not one of the allowed labels")
    return errors


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    reports = {
        "K": _run_kick_lane(manifest=manifest, lane_id="K", reversed_masks=False),
        "K_reversed": _run_kick_lane(
            manifest=manifest,
            lane_id="K_reversed",
            reversed_masks=True,
        ),
    }
    reversal = _classify_reversal(reports["K"], reports["K_reversed"])
    for report in reports.values():
        report["roles"]["reversal_outcome"] = reversal["outcome"]
    result = {
        "schema": "grc9v3_polarized_basin_loop_iteration5_report_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": (
            ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
            "scripts/run_kick_lanes.py"
        ),
        "reports": reports,
        "reversal": reversal,
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
