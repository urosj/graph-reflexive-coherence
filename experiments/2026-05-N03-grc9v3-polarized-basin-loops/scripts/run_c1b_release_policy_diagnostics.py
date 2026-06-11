#!/usr/bin/env python3
"""Run C1-B accumulator release-policy diagnostics.

This runner keeps C1's experiment-local accumulator substrate, but replaces the
first fixed-delay queue with release policies: passive leak, threshold,
hysteresis, hysteresis plus refractory, and a minimal coupled forward/return
gate.  It is a diagnostic sensitivity map, not a positive loop-claim tranche.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from loop_observables import (  # noqa: E402
    compute_observable_rows,
    load_json,
    summarize_observables,
    write_json,
    write_jsonl,
)
from run_c1_delayed_accumulator import (  # noqa: E402
    _add_to_region,
    _effective_flux_map,
    _int_flux,
    _manifest_for_lane,
    _make_model,
    _node_total,
    _remove_from_region,
)
from run_kick_lanes import _apply_zero_sum_kick  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "c1b_release_policy_report.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "c1b_release_policy_report.md"
RAW_RECORD_DIR = EXPERIMENT_ROOT / "outputs" / "c1b_release_policy_raw_records"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "c1b_release_policy_timeseries"


COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_c1b_release_policy_diagnostics.py"
)


@dataclass
class ChannelPolicyState:
    accumulator: float = 0.0
    open_gate: bool = False
    refractory_left: int = 0


@dataclass(frozen=True)
class ReleasePolicy:
    policy_id: str
    kind: str
    leak: float = 0.0
    theta_release: float = 0.0
    theta_low: float = 0.0
    theta_high: float = 0.0
    release_fraction: float = 1.0
    refractory_steps: int = 0
    no_delay: bool = False
    coupled: bool = False
    forward_enabled: bool = True
    return_enabled: bool = True


def _clip_release(amount: float, accumulator: float) -> float:
    return max(0.0, min(float(amount), float(accumulator)))


def _release_from_policy(
    *,
    policy: ReleasePolicy,
    state: ChannelPolicyState,
    channel: str,
    coupled_phase: str,
) -> tuple[float, str]:
    """Return release amount and next coupled phase label."""

    accumulator = state.accumulator
    if not ((channel == "forward" and policy.forward_enabled) or (channel == "return" and policy.return_enabled)):
        return 0.0, coupled_phase
    if policy.coupled:
        if channel == "forward" and coupled_phase not in {"forward_ready", "both_ready"}:
            return 0.0, coupled_phase
        if channel == "return" and coupled_phase != "return_ready":
            return 0.0, coupled_phase
    if policy.no_delay:
        release = accumulator
    elif policy.kind == "passive_leak":
        release = policy.leak * accumulator
    elif policy.kind == "threshold":
        release = policy.release_fraction * accumulator if accumulator > policy.theta_release else 0.0
    elif policy.kind == "hysteretic":
        if state.open_gate and accumulator < policy.theta_low:
            state.open_gate = False
        if not state.open_gate and accumulator > policy.theta_high:
            state.open_gate = True
        release = policy.release_fraction * accumulator if state.open_gate else 0.0
    elif policy.kind == "hysteretic_refractory":
        if state.refractory_left > 0:
            state.refractory_left -= 1
            return 0.0, coupled_phase
        if state.open_gate and accumulator < policy.theta_low:
            state.open_gate = False
        if not state.open_gate and accumulator > policy.theta_high:
            state.open_gate = True
        release = policy.release_fraction * accumulator if state.open_gate else 0.0
        if release > 0.0:
            state.refractory_left = policy.refractory_steps
            state.open_gate = False
    else:
        raise ValueError(f"unsupported release policy kind: {policy.kind}")
    release = _clip_release(release, accumulator)
    state.accumulator -= release
    if policy.coupled and release > 0.0:
        if channel == "forward":
            coupled_phase = "return_ready"
        elif channel == "return":
            coupled_phase = "forward_ready"
    return release, coupled_phase


def _policy_specs() -> list[ReleasePolicy]:
    specs = [ReleasePolicy(policy_id="no_delay", kind="threshold", no_delay=True)]
    specs.extend(
        ReleasePolicy(policy_id=f"passive_leak_{leak:g}".replace(".", "p"), kind="passive_leak", leak=leak)
        for leak in (0.05, 0.1, 0.2, 0.4)
    )
    specs.extend(
        ReleasePolicy(
            policy_id=f"threshold_t{theta:g}_r{fraction:g}".replace(".", "p"),
            kind="threshold",
            theta_release=theta,
            release_fraction=fraction,
        )
        for theta in (0.0005, 0.001, 0.002)
        for fraction in (0.5, 1.0)
    )
    specs.extend(
        ReleasePolicy(
            policy_id=f"hysteretic_h{high:g}_r{fraction:g}".replace(".", "p"),
            kind="hysteretic",
            theta_high=high,
            theta_low=high / 2.0,
            release_fraction=fraction,
        )
        for high in (0.001, 0.002)
        for fraction in (0.5, 1.0)
    )
    specs.extend(
        ReleasePolicy(
            policy_id=f"hysteretic_ref_h{high:g}_rf{refractory}".replace(".", "p"),
            kind="hysteretic_refractory",
            theta_high=high,
            theta_low=high / 2.0,
            release_fraction=0.75,
            refractory_steps=refractory,
        )
        for high in (0.001, 0.002)
        for refractory in (5, 10, 20)
    )
    specs.extend(
        [
            ReleasePolicy(
                policy_id="coupled_hysteretic_ref_h0p001_rf10",
                kind="hysteretic_refractory",
                theta_high=0.001,
                theta_low=0.0005,
                release_fraction=0.75,
                refractory_steps=10,
                coupled=True,
            ),
            ReleasePolicy(
                policy_id="forward_only_hysteretic_ref_h0p001_rf10",
                kind="hysteretic_refractory",
                theta_high=0.001,
                theta_low=0.0005,
                release_fraction=0.75,
                refractory_steps=10,
                forward_enabled=True,
                return_enabled=False,
            ),
            ReleasePolicy(
                policy_id="return_only_hysteretic_ref_h0p001_rf10",
                kind="hysteretic_refractory",
                theta_high=0.001,
                theta_low=0.0005,
                release_fraction=0.75,
                refractory_steps=10,
                forward_enabled=False,
                return_enabled=True,
            ),
        ]
    )
    return specs


def _step_release_policy(
    *,
    model: Any,
    manifest: Mapping[str, Any],
    policy: ReleasePolicy,
    forward_state: ChannelPolicyState,
    return_state: ChannelPolicyState,
    coupled_phase: str,
) -> tuple[dict[str, Any], str]:
    fixture = manifest["fixtures"]["grc9v3_ported_ring_v1"]
    masks = fixture["masks"]
    dt = float(manifest["runner_config"]["dt"])
    source_nodes = [int(node_id) for node_id in masks["source_aspect_nodes"]]
    sink_nodes = [int(node_id) for node_id in masks["sink_aspect_nodes"]]
    forward_edges = [int(edge_id) for edge_id in masks["forward_channel_edges"]]
    return_edges = [int(edge_id) for edge_id in masks["return_channel_edges"]]

    c_pre = {str(node_id): float(node.coherence) for node_id, node in model._state.nodes.items()}
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    proposal_flux_uv = {
        str(edge_id): float(edge.flux_uv)
        for edge_id, edge in model._state.port_edges.items()
    }
    forward_proposal = max(0.0, _int_flux(proposal_flux_uv, forward_edges[0])) if forward_edges else 0.0
    return_proposal = max(0.0, _int_flux(proposal_flux_uv, return_edges[0])) if return_edges else 0.0
    forward_input = _remove_from_region(model, source_nodes, dt * forward_proposal)
    return_input = _remove_from_region(model, sink_nodes, dt * return_proposal)
    forward_state.accumulator += forward_input
    return_state.accumulator += return_input
    forward_release, coupled_phase = _release_from_policy(
        policy=policy,
        state=forward_state,
        channel="forward",
        coupled_phase=coupled_phase,
    )
    _add_to_region(model, sink_nodes, forward_release)
    return_release, coupled_phase = _release_from_policy(
        policy=policy,
        state=return_state,
        channel="return",
        coupled_phase=coupled_phase,
    )
    _add_to_region(model, source_nodes, return_release)

    c_post = {str(node_id): float(node.coherence) for node_id, node in model._state.nodes.items()}
    in_flight = forward_state.accumulator + return_state.accumulator
    total = _node_total(model) + in_flight
    target = float(manifest["budget"]["total_budget"])
    effective_flux_uv = _effective_flux_map(
        fixture=fixture,
        forward_departure=forward_input,
        forward_arrival=forward_release,
        return_departure=return_input,
        return_arrival=return_release,
        dt=dt,
    )
    return (
        {
            "C_pre": c_pre,
            "C_post_continuity": c_post,
            "C_post_budget": c_post,
            "flux_uv": effective_flux_uv,
            "proposal_flux_uv": proposal_flux_uv,
            "budget": {
                "before_continuity": target,
                "after_continuity": total,
                "after_correction": total,
                "correction_method": "none_release_policy_exact_budget",
                "correction_magnitude": 0.0,
                "simplex_projection_applied": False,
                "uniform_shift_applied": False,
            },
            "accumulator": {
                "forward_input": forward_input,
                "forward_release": forward_release,
                "return_input": return_input,
                "return_release": return_release,
                "forward_accumulator": forward_state.accumulator,
                "return_accumulator": return_state.accumulator,
                "in_flight_total": in_flight,
                "node_total": _node_total(model),
                "nodes_plus_accumulator_total": total,
                "budget_error": total - target,
                "coupled_phase": coupled_phase,
            },
        },
        coupled_phase,
    )


def _manifest_for_c1b(base_manifest: Mapping[str, Any], *, reversed_masks: bool) -> dict[str, Any]:
    manifest = _manifest_for_lane(base_manifest, reversed_masks=reversed_masks)
    manifest["scope"]["runner_mode"] = "c1b_release_policy_runner"
    manifest["runner_config"]["runner_sequence"] = [
        "C_pre",
        "rebuild_differential_state",
        "rebuild_transport_state",
        "capture_flux_proposals",
        "accumulate_channel_inputs",
        "apply_release_policy",
        "capture_C_post_release",
        "audit_nodes_plus_accumulator_budget",
        "experiment_local_loop_observables",
    ]
    return manifest


def _run_policy_lane(
    *,
    base_manifest: Mapping[str, Any],
    policy: ReleasePolicy,
    lane_id: str,
    reversed_masks: bool = False,
) -> dict[str, Any]:
    manifest = _manifest_for_c1b(base_manifest, reversed_masks=reversed_masks)
    model = _make_model(manifest, lane_id=lane_id)
    if lane_id in {"K", "K_reversed"}:
        _apply_zero_sum_kick(model=model, manifest=manifest)
    forward_state = ChannelPolicyState()
    return_state = ChannelPolicyState()
    coupled_phase = "forward_ready"
    records: list[dict[str, Any]] = []
    initial_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    initial_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    for step_index in range(int(manifest["runner_config"]["total_steps"])):
        step, coupled_phase = _step_release_policy(
            model=model,
            manifest=manifest,
            policy=policy,
            forward_state=forward_state,
            return_state=return_state,
            coupled_phase=coupled_phase,
        )
        records.append({"step_index": step_index, **step})
        model.rebuild_differential_state()
        model.rebuild_transport_state()
        model.rebuild_identity_state()

    row_id = f"c1b_{lane_id.lower()}_{policy.policy_id}"
    raw_path = RAW_RECORD_DIR / f"{row_id}_raw_records.jsonl"
    write_jsonl(raw_path, records)
    rows = compute_observable_rows(
        manifest=manifest,
        records=records,
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
            "zero_flux_reset": "fresh_accumulator_state_zeroed",
            "randomized_labels_posthoc": "not_run_c1b",
            "shuffled_conductance": "not_run_c1b",
            "budget_projection_disabled_dry_run": "not_applicable_accumulator_exact_budget",
            "release_policy_control": policy.policy_id,
        },
        runtime_provenance_override={
            "runner_mode": "c1b_release_policy_runner",
            "called_methods": manifest["runner_config"]["runner_sequence"],
        },
    )
    final_node_count = len(tuple(model._state.topology.iter_live_node_ids()))
    final_edge_count = len(tuple(model._state.topology.iter_live_edge_ids()))
    report["topology"]["initial_node_count"] = initial_node_count
    report["topology"]["initial_edge_count"] = initial_edge_count
    report["topology"]["final_node_count"] = final_node_count
    report["topology"]["final_edge_count"] = final_edge_count
    report["topology"]["changed"] = (
        initial_node_count != final_node_count or initial_edge_count != final_edge_count
    )
    max_budget_error = max(abs(float(record["accumulator"]["budget_error"])) for record in records)
    max_in_flight = max(float(record["accumulator"]["in_flight_total"]) for record in records)
    report["raw_records"] = {"artifact_path": str(raw_path)}
    report["release_policy"] = {
        "policy_id": policy.policy_id,
        "kind": policy.kind,
        "leak": policy.leak,
        "theta_release": policy.theta_release,
        "theta_low": policy.theta_low,
        "theta_high": policy.theta_high,
        "release_fraction": policy.release_fraction,
        "refractory_steps": policy.refractory_steps,
        "no_delay": policy.no_delay,
        "coupled": policy.coupled,
        "forward_enabled": policy.forward_enabled,
        "return_enabled": policy.return_enabled,
    }
    report["accumulator_budget"] = {
        "budget_surface": "node_coherence_plus_forward_return_accumulators",
        "max_abs_budget_error": max_budget_error,
        "max_in_flight_total": max_in_flight,
        "passed": max_budget_error <= 1e-9,
    }
    report["diagnostic_row"] = {
        "row_id": row_id,
        "lane_id": lane_id,
        "policy_id": policy.policy_id,
        "reversed_masks": reversed_masks,
    }
    would_candidate = bool(report["claim_gate"]["positive_candidate_loop_claim_allowed"])
    report["claim_gate"]["would_candidate_loop_claim_without_diagnostic_ceiling"] = would_candidate
    report["claim_gate"]["positive_candidate_loop_claim_allowed"] = False
    report["claim_gate"]["positive_full_loop_claim_allowed"] = False
    report["claim_gate"]["diagnostic_release_policy_ceiling_applied"] = True
    report["claim_gate"]["blocked_reasons"] = list(report["claim_gate"]["blocked_reasons"]) + [
        "diagnostic_release_policy_claim_ceiling"
    ]
    report["blocked_claims"] = report["claim_gate"]["blocked_reasons"]
    return report


def _run_rows(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for policy in _policy_specs():
        reports.append(_run_policy_lane(base_manifest=manifest, policy=policy, lane_id="S"))
        reports.append(_run_policy_lane(base_manifest=manifest, policy=policy, lane_id="K"))
    # Minimal null/control subset across the serious oscillator-like policy.
    control_policy = next(policy for policy in _policy_specs() if policy.policy_id == "coupled_hysteretic_ref_h0p001_rf10")
    for lane_id, reversed_masks in (("U0", False), ("U2", False), ("K_reversed", True)):
        reports.append(
            _run_policy_lane(
                base_manifest=manifest,
                policy=control_policy,
                lane_id=lane_id,
                reversed_masks=reversed_masks,
            )
        )
    return reports


def _summarize(reports: list[Mapping[str, Any]]) -> dict[str, Any]:
    compact_rows: list[dict[str, Any]] = []
    promising_rows: list[dict[str, Any]] = []
    for report in reports:
        row = report["diagnostic_row"]
        compact = {
            "row_id": row["row_id"],
            "lane_id": row["lane_id"],
            "policy_id": row["policy_id"],
            "source_like": report["roles"]["source_like_measured"],
            "sink_like": report["roles"]["sink_like_measured"],
            "raw_cycles": report["cycles"]["raw_cycle_count"],
            "role_gated_cycles": report["cycles"]["role_gated_cycle_count"],
            "would_candidate_loop_claim_without_diagnostic_ceiling": report["claim_gate"][
                "would_candidate_loop_claim_without_diagnostic_ceiling"
            ],
            "max_in_flight_total": report["accumulator_budget"]["max_in_flight_total"],
            "max_abs_budget_error": report["accumulator_budget"]["max_abs_budget_error"],
        }
        compact_rows.append(compact)
        if compact["role_gated_cycles"] or compact["would_candidate_loop_claim_without_diagnostic_ceiling"]:
            promising_rows.append(compact)
    return {
        "row_count": len(reports),
        "promising_row_count": len(promising_rows),
        "promising_rows": promising_rows,
        "compact_rows": compact_rows,
        "classification": (
            "release_policy_promising_rows_observed"
            if promising_rows
            else "release_policy_no_role_gated_cycles_observed"
        ),
        "positive_loop_claim_allowed": False,
    }


def _validate(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for report in result["reports"]:
        row_id = report["diagnostic_row"]["row_id"]
        if report["topology"]["changed"]:
            errors.append(f"{row_id} changed topology")
        if not report["accumulator_budget"]["passed"]:
            errors.append(f"{row_id} failed accumulator budget audit")
        if report["claim_gate"]["positive_candidate_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a candidate claim from diagnostic sweep")
        if report["claim_gate"]["positive_full_loop_claim_allowed"]:
            errors.append(f"{row_id} promoted a full loop claim")
    return errors


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# C1-B Release Policy Diagnostic Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "C1-B is a diagnostic release-policy sensitivity map, not a positive",
        "loop-claim tranche.",
        "",
        f"Rows: `{result['summary']['row_count']}`",
        f"Promising rows: `{result['summary']['promising_row_count']}`",
        f"Classification: `{result['summary']['classification']}`",
        "",
        "## Compact Summary",
        "",
        "| Row | Lane | Policy | Source | Sink | Raw | Role-Gated | Would Claim | Max In-Flight | Max Budget Error |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in result["summary"]["compact_rows"]:
        lines.append(
            "| {row_id} | {lane} | {policy} | {source} | {sink} | {raw} | {gated} | {would} | {flight:.6g} | {budget:.6g} |".format(
                row_id=row["row_id"],
                lane=row["lane_id"],
                policy=row["policy_id"],
                source=row["source_like"],
                sink=row["sink_like"],
                raw=row["raw_cycles"],
                gated=row["role_gated_cycles"],
                would=row["would_candidate_loop_claim_without_diagnostic_ceiling"],
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
    reports = _run_rows(manifest)
    result = {
        "schema": "grc9v3_polarized_basin_loop_c1b_release_policy_diagnostics_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pending_validation",
        "command": COMMAND,
        "branch": "C1-B",
        "claim_ceiling": "diagnostic_release_policy_sensitivity_map_not_positive_loop_claim",
        "reports": reports,
        "summary": _summarize(reports),
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
                "promising_rows": result["summary"]["promising_row_count"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
