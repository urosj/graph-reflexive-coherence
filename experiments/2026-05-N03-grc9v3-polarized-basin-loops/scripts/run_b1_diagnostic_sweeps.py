#!/usr/bin/env python3
"""Run Branch B1 diagnostic sweeps for polarized basin loops.

Branch B is diagnostic-only.  It reuses the fixed-topology GRC9V3 continuity
runner from Iterations 4/5, but every row is capped as sensitivity evidence:
no positive loop claim may be promoted from this script.
"""

from __future__ import annotations

import copy
import json
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
    _budget_record,
    _coherence_map,
    _flux_map,
    _initial_diagnostic_snapshot,
    _state_from_manifest,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "b1_diagnostic_sweeps_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "b1_diagnostic_sweeps_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "b1_diagnostic_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "b1_diagnostic_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_b1_diagnostic_sweeps.py"
)


def _arc_edges(*, start_edge: int, stop_node: int, node_count: int) -> list[int]:
    """Return clockwise edge ids from `start_edge` until the edge reaches stop_node."""

    edge_ids: list[int] = []
    edge_id = start_edge % node_count
    for _ in range(node_count):
        edge_ids.append(edge_id)
        if (edge_id + 1) % node_count == stop_node % node_count:
            return edge_ids
        edge_id = (edge_id + 1) % node_count
    raise ValueError("arc did not reach stop node")


def _ring_fixture_variant(
    *,
    base_fixture: Mapping[str, Any],
    node_count: int,
    mask_width: int,
    spacing: str,
) -> dict[str, Any]:
    """Build an in-memory GRC9V3 ported-ring fixture variant."""

    if mask_width < 1:
        raise ValueError("mask_width must be positive")
    if node_count < 4 * mask_width:
        raise ValueError("node_count is too small for disjoint source/sink masks")
    spacing_offsets = {
        "half": node_count // 2,
        "third": node_count // 3,
        "quarter": node_count // 4,
    }
    if spacing not in spacing_offsets:
        raise ValueError(f"unsupported spacing: {spacing}")
    sink_start = spacing_offsets[spacing]
    source_nodes = list(range(mask_width))
    sink_nodes = [(sink_start + offset) % node_count for offset in range(mask_width)]
    if set(source_nodes) & set(sink_nodes):
        raise ValueError("source and sink masks overlap")

    edges = [
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
    ]
    source_internal = list(range(max(0, mask_width - 1)))
    sink_internal = [(sink_start + offset) % node_count for offset in range(max(0, mask_width - 1))]
    forward_edges = _arc_edges(
        start_edge=(source_nodes[-1] % node_count),
        stop_node=sink_nodes[0],
        node_count=node_count,
    )
    return_edges = _arc_edges(
        start_edge=(sink_nodes[-1] % node_count),
        stop_node=source_nodes[0],
        node_count=node_count,
    )

    masks = dict(base_fixture["masks"])
    masks.update(
        {
            "source_aspect_nodes": source_nodes,
            "sink_aspect_nodes": sink_nodes,
            "forward_channel_edges": forward_edges,
            "return_channel_edges": return_edges,
            "source_internal_edges": source_internal,
            "sink_internal_edges": sink_internal,
            "parent_basin_nodes": list(range(node_count)),
            "same_parent_basin_mode": "configured_parent_region_only",
        }
    )
    fixture = dict(base_fixture)
    fixture.update(
        {
            "fixture_id": "grc9v3_ported_ring_v1",
            "node_count": node_count,
            "edge_count": node_count,
            "nodes": list(range(node_count)),
            "edges": edges,
            "masks": masks,
            "reversed_masks": {
                "source_aspect_nodes": sink_nodes,
                "sink_aspect_nodes": source_nodes,
                "forward_channel_edges": return_edges,
                "return_channel_edges": forward_edges,
                "source_internal_edges": sink_internal,
                "sink_internal_edges": source_internal,
            },
            "variant_parameters": {
                "node_count": node_count,
                "mask_width": mask_width,
                "spacing": spacing,
            },
        }
    )
    return fixture


def _variant_manifest(
    base_manifest: Mapping[str, Any],
    *,
    node_count: int = 12,
    mask_width: int = 2,
    spacing: str = "half",
    epsilon: float | None = None,
    kick_delta: float | None = None,
) -> dict[str, Any]:
    """Return an in-memory manifest variant without mutating the fixture file."""

    manifest = copy.deepcopy(dict(base_manifest))
    fixture = _ring_fixture_variant(
        base_fixture=base_manifest["fixtures"]["grc9v3_ported_ring_v1"],
        node_count=node_count,
        mask_width=mask_width,
        spacing=spacing,
    )
    manifest["fixtures"]["grc9v3_ported_ring_v1"] = fixture
    defaults = manifest["initialization"]["default_parameters"]
    if epsilon is not None:
        defaults["epsilon_s"] = float(epsilon)
        defaults["epsilon_k"] = float(epsilon)
    if kick_delta is not None:
        defaults["kick_delta"] = float(kick_delta)
    manifest["diagnostic_branch"] = {
        "branch": "B1",
        "claim_ceiling": "diagnostic_sensitivity_map_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
        "variant_is_in_memory_only": True,
    }
    return manifest


def _make_model(manifest: Mapping[str, Any], *, lane_id: str) -> GRC9V3:
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


def _run_fixed_topology_trace(
    *,
    manifest: Mapping[str, Any],
    lane_id: str,
) -> tuple[GRC9V3, list[dict[str, Any]]]:
    model_lane = "S" if lane_id == "S" else "U2"
    model = _make_model(manifest, lane_id=model_lane)
    if lane_id == "K":
        _apply_zero_sum_kick(model=model, manifest=manifest)

    raw_records: list[dict[str, Any]] = []
    for step_index in range(int(manifest["runner_config"]["total_steps"])):
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
    return model, raw_records


def _apply_diagnostic_ceiling(report: dict[str, Any]) -> None:
    """Force Branch B claim behavior to remain diagnostic-only."""

    would_candidate = bool(report["claim_gate"]["positive_candidate_loop_claim_allowed"])
    would_full = bool(report["claim_gate"]["positive_full_loop_claim_allowed"])
    blocked_reasons = list(report["claim_gate"].get("blocked_reasons", []))
    if "diagnostic_branch_claim_ceiling" not in blocked_reasons:
        blocked_reasons.append("diagnostic_branch_claim_ceiling")
    report["claim_gate"]["would_candidate_loop_claim_without_diagnostic_ceiling"] = would_candidate
    report["claim_gate"]["would_full_loop_claim_without_diagnostic_ceiling"] = would_full
    report["claim_gate"]["positive_candidate_loop_claim_allowed"] = False
    report["claim_gate"]["positive_full_loop_claim_allowed"] = False
    report["claim_gate"]["diagnostic_branch_claim_ceiling_applied"] = True
    report["claim_gate"]["blocked_reasons"] = blocked_reasons
    report["blocked_claims"] = blocked_reasons
    report["diagnostic_branch"] = {
        "branch": "B1",
        "claim_ceiling": "diagnostic_sensitivity_map_not_positive_loop_claim",
        "positive_loop_claim_allowed": False,
        "interpretation": (
            "A passing diagnostic row may identify a condition for a future named "
            "tranche, but cannot promote a loop claim in Branch B."
        ),
    }


def _run_diagnostic_row(
    *,
    base_manifest: Mapping[str, Any],
    row_id: str,
    axis: str,
    lane_id: str,
    node_count: int = 12,
    mask_width: int = 2,
    spacing: str = "half",
    epsilon: float | None = None,
    kick_delta: float | None = None,
) -> dict[str, Any]:
    manifest = _variant_manifest(
        base_manifest,
        node_count=node_count,
        mask_width=mask_width,
        spacing=spacing,
        epsilon=epsilon,
        kick_delta=kick_delta,
    )
    model, raw_records = _run_fixed_topology_trace(manifest=manifest, lane_id=lane_id)
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
            "zero_flux_reset": "not_applicable_fresh_transport_rebuild",
            "randomized_labels_posthoc": "not_run_b1",
            "shuffled_conductance": "not_run_b1",
            "budget_projection_disabled_dry_run": "not_run_b1",
        },
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    initial_diagnostics = _initial_diagnostic_snapshot(manifest=manifest, model=model)
    report["runtime_provenance"]["called_methods"] = [
        "apply_experiment_local_zero_sum_kick" if lane_id == "K" else "initialize_structured_lane",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "apply_continuity",
        "enforce_quadrature_budget",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "rebuild_identity_state",
        "experiment_local_loop_observables",
    ]
    report["topology"]["final_node_count"] = final_node_count
    report["topology"]["final_edge_count"] = final_edge_count
    report["topology"]["changed"] = (
        report["topology"]["initial_node_count"] != final_node_count
        or report["topology"]["initial_edge_count"] != final_edge_count
    )
    report["topology"]["passed_fixed_topology_gate"] = not report["topology"]["changed"]
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["diagnostic_row"] = {
        "row_id": row_id,
        "axis": axis,
        "lane_id": lane_id,
        "node_count": node_count,
        "mask_width": mask_width,
        "spacing": spacing,
        "epsilon": epsilon,
        "kick_delta": kick_delta,
    }
    report["runtime_diagnostics"] = {
        "transport_rebuild_snapshot": initial_diagnostics,
        "source_sink_C_mean_delta_after_rebuild": initial_diagnostics[
            "source_sink_C_mean_delta"
        ],
        "source_sink_potential_mean_delta_after_rebuild": initial_diagnostics[
            "source_sink_potential_mean_delta"
        ],
        "forward_return_flux_mean_delta_after_rebuild": initial_diagnostics[
            "forward_flux_mean"
        ]
        - initial_diagnostics["return_flux_mean"],
        "interpretation": (
            "Transport audit records whether initialized polarity survives the "
            "first differential/transport rebuild before diagnostic scoring."
        ),
    }
    _apply_diagnostic_ceiling(report)
    return report


def _diagnostic_rows(base_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for epsilon in (0.005, 0.01, 0.02, 0.04):
        rows.append(
            _run_diagnostic_row(
                base_manifest=base_manifest,
                row_id=f"b1_1_s_epsilon_{epsilon:g}".replace(".", "p"),
                axis="B1.1_amplitude_s_modulation",
                lane_id="S",
                epsilon=epsilon,
            )
        )
    for kick_delta in (0.005, 0.01, 0.02, 0.04):
        rows.append(
            _run_diagnostic_row(
                base_manifest=base_manifest,
                row_id=f"b1_1_k_delta_{kick_delta:g}".replace(".", "p"),
                axis="B1.1_amplitude_k_kick",
                lane_id="K",
                kick_delta=kick_delta,
            )
        )
    for width in (1, 2, 3):
        for lane_id in ("S", "K"):
            rows.append(
                _run_diagnostic_row(
                    base_manifest=base_manifest,
                    row_id=f"b1_2_{lane_id.lower()}_width_{width}",
                    axis="B1.2_mask_width",
                    lane_id=lane_id,
                    mask_width=width,
                )
            )
    for node_count in (12, 24, 48):
        for lane_id in ("S", "K"):
            rows.append(
                _run_diagnostic_row(
                    base_manifest=base_manifest,
                    row_id=f"b1_3_{lane_id.lower()}_n_{node_count}",
                    axis="B1.3_ring_size",
                    lane_id=lane_id,
                    node_count=node_count,
                )
            )
    for spacing in ("half", "third", "quarter"):
        for lane_id in ("S", "K"):
            rows.append(
                _run_diagnostic_row(
                    base_manifest=base_manifest,
                    row_id=f"b1_4_{lane_id.lower()}_spacing_{spacing}",
                    axis="B1.4_spacing",
                    lane_id=lane_id,
                    spacing=spacing,
                )
            )
    return rows


def _summarize_rows(reports: list[Mapping[str, Any]]) -> dict[str, Any]:
    promising = [
        {
            "row_id": report["diagnostic_row"]["row_id"],
            "axis": report["diagnostic_row"]["axis"],
            "lane_id": report["diagnostic_row"]["lane_id"],
            "role_gated_cycle_count": report["cycles"]["role_gated_cycle_count"],
            "would_candidate_loop_claim_without_diagnostic_ceiling": report["claim_gate"][
                "would_candidate_loop_claim_without_diagnostic_ceiling"
            ],
        }
        for report in reports
        if int(report["cycles"]["role_gated_cycle_count"]) > 0
        or bool(report["claim_gate"]["would_candidate_loop_claim_without_diagnostic_ceiling"])
    ]
    return {
        "row_count": len(reports),
        "promising_row_count": len(promising),
        "promising_rows": promising,
        "interpretation": (
            "promising_conditions_require_new_named_tranche"
            if promising
            else "no_role_gated_cascades_detected_fixture_mechanism_mismatch_likely"
        ),
        "positive_loop_claim_allowed": False,
    }


def _validate_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for report in result["reports"]:
        row_id = report["diagnostic_row"]["row_id"]
        if report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a candidate claim in diagnostic branch")
        if report["claim_gate"]["positive_full_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a full loop claim in diagnostic branch")
        if report["topology"]["changed"]:
            errors.append(f"{row_id} changed topology")
        if not report["budget"]["passed"]:
            errors.append(f"{row_id} failed budget audit")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch B1 Diagnostic Sweep Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "Branch B1 is diagnostic-only. It uses real `GRC9V3` fixed-topology",
        "continuity execution, but it cannot promote a positive loop claim.",
        "",
        f"Rows: `{result['summary']['row_count']}`",
        f"Promising diagnostic rows: `{result['summary']['promising_row_count']}`",
        f"Interpretation: `{result['summary']['interpretation']}`",
        "",
        "## Row Summary",
        "",
        "| Row | Axis | Lane | Param | Source | Sink | Raw | Role-Gated | Would Claim | Claim Allowed | Max Correction |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | ---: |",
    ]
    for report in result["reports"]:
        row = report["diagnostic_row"]
        param = (
            f"eps={row['epsilon']}"
            if row["epsilon"] is not None
            else f"kick={row['kick_delta']}"
            if row["kick_delta"] is not None
            else f"N={row['node_count']},w={row['mask_width']},spacing={row['spacing']}"
        )
        lines.append(
            "| {row_id} | {axis} | {lane} | {param} | {source} | {sink} | {raw} | {gated} | {would} | {claim} | {corr:.6g} |".format(
                row_id=row["row_id"],
                axis=row["axis"],
                lane=row["lane_id"],
                param=param,
                source=report["roles"]["source_like_measured"],
                sink=report["roles"]["sink_like_measured"],
                raw=report["cycles"]["raw_cycle_count"],
                gated=report["cycles"]["role_gated_cycle_count"],
                would=report["claim_gate"]["would_candidate_loop_claim_without_diagnostic_ceiling"],
                claim=report["claim_gate"]["positive_candidate_loop_claim_allowed"],
                corr=report["budget"]["max_correction_magnitude"],
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
    reports = _diagnostic_rows(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_b1_diagnostic_sweeps_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "branch": "B1",
        "claim_ceiling": "diagnostic_sensitivity_map_not_positive_loop_claim",
        "reports": reports,
        "summary": _summarize_rows(reports),
        "errors": [],
    }
    errors = _validate_result(result)
    result["errors"] = errors
    result["status"] = "pass" if not errors else "fail"
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "rows": result["summary"]["row_count"],
                "promising_rows": result["summary"]["promising_row_count"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
