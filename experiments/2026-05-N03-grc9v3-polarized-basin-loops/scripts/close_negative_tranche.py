#!/usr/bin/env python3
"""Close N03 first tranche as a fail-closed negative result.

This script aggregates the existing fixture, synthetic-observable, U/S runtime,
and K runtime reports.  It does not rerun dynamics and does not import
`src/pygrc`; it validates report semantics and records the first-tranche claim
ceiling.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = ROOT / "outputs"
REPORT_DIR = ROOT / "reports"
OUTPUT_PATH = OUTPUT_DIR / "negative_tranche_closeout.json"
REPORT_PATH = REPORT_DIR / "negative_tranche_closeout.md"

INPUT_REPORTS = {
    "fixture_manifest_validation": OUTPUT_DIR / "fixture_manifest_validation.json",
    "observable_smoke": OUTPUT_DIR / "loop_observables_smoke_report.json",
    "null_structured_lanes": OUTPUT_DIR / "null_structured_lanes_report.json",
    "kick_lanes": OUTPUT_DIR / "kick_lanes_report.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _report_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _lane_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        lane_id: {
            "budget_passed": bool(lane["budget"]["passed"]),
            "topology_changed": bool(lane["topology"]["changed"]),
            "ladder_level": str(lane["ladder"]["level"]),
            "source_role": bool(lane["roles"]["source_like_measured"]),
            "sink_role": bool(lane["roles"]["sink_like_measured"]),
            "raw_cycle_count": int(lane["cycles"]["raw_cycle_count"]),
            "role_gated_cycle_count": int(lane["cycles"]["role_gated_cycle_count"]),
            "candidate_claim_allowed": bool(
                lane["claim_gate"]["positive_candidate_loop_claim_allowed"]
            ),
            "blocked_reasons": list(lane["claim_gate"]["blocked_reasons"]),
            "primary_scientific_blocker": lane["claim_gate"].get(
                "primary_scientific_blocker"
            ),
        }
        for lane_id, lane in report["reports"].items()
    }


def _validate_inputs(reports: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for name, report in reports.items():
        if report.get("status") != "pass":
            errors.append(f"{name} status is not pass")

    smoke = reports["observable_smoke"]
    for lane_id, lane in smoke["reports"].items():
        if lane_id.startswith("budget_drift"):
            if lane["budget"]["passed"]:
                errors.append(f"{lane_id} should fail budget gate")
            if lane["claim_gate"]["positive_candidate_loop_claim_allowed"]:
                errors.append(f"{lane_id} should not allow a candidate claim")
            if "budget_gate_failed" not in lane["claim_gate"]["blocked_reasons"]:
                errors.append(f"{lane_id} should record budget_gate_failed")

    runtime_reports = (
        reports["null_structured_lanes"]["reports"],
        reports["kick_lanes"]["reports"],
    )
    for lane_group in runtime_reports:
        for lane_id, lane in lane_group.items():
            if not lane["budget"]["passed"]:
                errors.append(f"{lane_id} runtime budget gate failed")
            if lane["topology"]["changed"]:
                errors.append(f"{lane_id} changed topology")
            if lane["claim_gate"]["positive_candidate_loop_claim_allowed"]:
                errors.append(f"{lane_id} unexpectedly allows a candidate claim")
            if lane["cycles"]["role_gated_cycle_count"] != 0:
                errors.append(f"{lane_id} unexpectedly has role-gated cycles")

    u1 = reports["null_structured_lanes"]["reports"]["U1"]
    if int(u1["cycles"]["raw_cycle_count"]) <= 0:
        errors.append("U1 should preserve the recorded shape-only cascade warning")
    if int(u1["cycles"]["role_gated_cycle_count"]) != 0:
        errors.append("U1 should have zero role-gated cycles")

    return errors


def _build_payload(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    errors = _validate_inputs(reports)
    null_structured = reports["null_structured_lanes"]
    kick = reports["kick_lanes"]
    return {
        "schema": "grc9v3_polarized_basin_loop_negative_tranche_closeout_v1",
        "experiment_id": "2026-05-N03-grc9v3-polarized-basin-loops",
        "status": "pass" if not errors else "fail",
        "classification": "negative_fixed_topology_first_tranche",
        "result": (
            "No polarized basin loop was observed on the first 12-node "
            "fixed-topology GRC9V3 ported-ring fixture under S/K lanes."
        ),
        "not_an_implementation_failure": True,
        "threshold_or_classifier_tuning_performed": False,
        "positive_claim_promoted": False,
        "input_reports": {
            name: _report_ref(path)
            for name, path in INPUT_REPORTS.items()
        },
        "validated_surfaces": [
            "fixed_topology_grc9v3_runtime_bridge",
            "observable_library_on_real_traces",
            "budget_topology_provenance_reporting",
            "null_rejection_behavior",
            "role_gated_blocking_of_shape_only_cascades",
        ],
        "not_validated_surfaces": [
            "L4_conserved_internal_loop",
            "L5_self_regulating_pulse_generator",
            "L6_boundary_couplable_loop",
            "movement_or_locomotion_precursor_evidence",
        ],
        "gate_policy": {
            "positive_claim_requires_budget_gate": True,
            "positive_claim_requires_fixed_topology_gate": True,
            "positive_claim_requires_measured_source_sink_roles": True,
            "positive_claim_requires_flux_closure": True,
            "positive_claim_requires_role_gated_cascades": True,
            "full_positive_claim_requires_single_parent_basin_evidence": True,
            "raw_cascades_are_shape_evidence_only": True,
        },
        "lane_summaries": {
            "null_structured": _lane_summary(null_structured),
            "kick": _lane_summary(kick),
        },
        "blocked_observations": list(null_structured.get("blocked_observations", [])),
        "reversal": dict(kick["reversal"]),
        "branch_b_diagnostic_sweeps": {
            "status": "not_started",
            "claim_ceiling": "diagnostic_sensitivity_map_not_positive_loop_claim",
            "axes": [
                "S_modulation_amplitude",
                "K_kick_strength",
                "source_sink_mask_width",
                "ring_size",
                "conductance_asymmetry_or_channel_structure",
                "source_sink_spacing",
                "forward_return_asymmetry",
                "budget_correction_magnitude",
                "transport_rebuild_behavior",
            ],
        },
        "branch_c_fixture_theory_redesign": {
            "status": "not_started",
            "requires_new_fixture_manifest": True,
            "requires_new_claim_ceiling": True,
        },
        "later_surfaces": {
            "L5_self_regulation": "unopened_l4_not_established",
            "L6_boundary_coupling": "unopened_l5_not_established",
            "multi_pole_appendix_a": "deferred_two_aspect_l4_not_established",
            "movement_ladders_handoff": "blocked_no_l4_loop_evidence",
        },
        "errors": errors,
    }


def _write_markdown(payload: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lane_rows: list[str] = []
    for group_name, lanes in payload["lane_summaries"].items():
        for lane_id, lane in lanes.items():
            lane_rows.append(
                "| {group} | {lane} | {budget} | {source} | {sink} | {raw} | {gated} | {claim} |".format(
                    group=group_name,
                    lane=lane_id,
                    budget=lane["budget_passed"],
                    source=lane["source_role"],
                    sink=lane["sink_role"],
                    raw=lane["raw_cycle_count"],
                    gated=lane["role_gated_cycle_count"],
                    claim=lane["candidate_claim_allowed"],
                )
            )
    lines = [
        "# Iteration 6 Negative Tranche Closeout",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/close_negative_tranche.py",
        "```",
        "",
        f"Status: `{payload['status']}`",
        f"Classification: `{payload['classification']}`",
        "",
        payload["result"],
        "",
        "This is a valid negative result, not an implementation failure. No",
        "classifier or threshold tuning was performed to rescue the first tranche.",
        "",
        "## Lane Summary",
        "",
        "| Group | Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
        *lane_rows,
        "",
        "## Validated",
        "",
        *[f"- `{item}`" for item in payload["validated_surfaces"]],
        "",
        "## Not Validated",
        "",
        *[f"- `{item}`" for item in payload["not_validated_surfaces"]],
        "",
        "## Future Branches",
        "",
        "- Branch B diagnostic sweeps remain unopened and have claim ceiling",
        "  `diagnostic_sensitivity_map_not_positive_loop_claim`.",
        "- Branch C fixture/theory redesign remains unopened and requires a new",
        "  fixture manifest plus a new claim ceiling.",
        "- L5, L6, multi-pole Appendix A, and movement-ladders handoff remain",
        "  blocked/deferred because L4 was not established.",
        "",
        "## Errors",
        "",
    ]
    if payload["errors"]:
        lines.extend(f"- {error}" for error in payload["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    missing = [name for name, path in INPUT_REPORTS.items() if not path.exists()]
    if missing:
        print(json.dumps({"status": "fail", "errors": [f"missing {name}" for name in missing]}))
        return 1
    reports = {name: _load_json(path) for name, path in INPUT_REPORTS.items()}
    payload = _build_payload(reports)
    _write_json(OUTPUT_PATH, payload)
    _write_markdown(payload)
    print(json.dumps({"status": payload["status"], "errors": payload["errors"]}, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
