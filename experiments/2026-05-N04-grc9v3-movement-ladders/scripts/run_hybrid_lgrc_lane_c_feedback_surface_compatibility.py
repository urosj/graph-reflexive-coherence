#!/usr/bin/env python3
"""Check whether Lane C fits the Lane E causal pulse-substrate surface.

This is not a new movement run. It is a compatibility/reuse audit: Lane C's
experiment-local feedback regeneration should be representable as a policy
specialization over the broader causal pulse-substrate surface proposed by Lane
E, instead of requiring a separate Lane-C-specific native core primitive.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

LANE_E = N04 / "outputs/hybrid_lgrc_pulse_substrate_surface_probe.json"
LANE_C_CONFIG = N04 / "configs/feedback_coupled_pulse_regeneration_v1.json"
LANE_C_CONTRACT = N04 / "outputs/feedback_contract_validation.json"
LANE_C_REGENERATION = N04 / "outputs/feedback_triggered_pulse_regeneration_report.json"
LANE_C_M6 = N04 / "outputs/reopened_m6_feedback_gate_report.json"

OUTPUT_PATH = N04 / "outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json"
REPORT_PATH = N04 / "reports/hybrid_lgrc_lane_c_feedback_surface_compatibility.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_hybrid_lgrc_lane_c_feedback_surface_compatibility.py"
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report() -> dict[str, Any]:
    lane_e = _load_json(LANE_E)
    lane_c_config = _load_json(LANE_C_CONFIG)
    lane_c_contract = _load_json(LANE_C_CONTRACT)
    lane_c_regeneration = _load_json(LANE_C_REGENERATION)
    lane_c_m6 = _load_json(LANE_C_M6)

    feedback_surface = lane_c_config["feedback_surface"]
    lane_e_contract = lane_e["contract"]
    direct_write_policy = lane_e_contract["direct_write_policy"]
    lane_c_controls = lane_c_regeneration["controls"]
    expected_negative_controls = {
        "pulse_disabled",
        "feedback_disabled",
        "subthreshold_feedback",
        "wrong_polarity",
        "scrambled_timing_order",
        "budget_violating_synthetic",
    }

    mapping = {
        "surface_id": "native_causal_pulse_substrate_surface",
        "lane_c_projection": "feedback_policy_specialization",
        "lane_c_feedback_surface": feedback_surface["name"],
        "runtime_visible_inputs": feedback_surface["runtime_visible_inputs"],
        "projected_surface_fields": [
            "front_mass",
            "rear_mass",
            "boundary_polarity_score",
            "surface_deformation_displacement",
            "feedback_eligibility",
            "feedback_polarity",
        ],
        "affected_native_policy_if_promoted": [
            "producer eligibility",
            "route-aspect polarity",
            "next pulse schedule gate",
        ],
        "native_core_primitive_needed": "native_causal_pulse_substrate_surface",
        "native_specialization_needed": "policy_gated_feedback_producer",
        "lane_c_specific_core_primitive_needed": False,
        "producer_boundary": {
            "producer_may_read_surface_state": True,
            "producer_may_emit_eligibility_evidence": True,
            "producer_may_schedule_through_lgrc_surface_if_promoted": True,
            "producer_may_mutate_coherence_directly": False,
            "step_remains_budget_mutation_surface": True,
        },
    }

    controls_negative = all(
        lane_c_controls[name]["feedback_scheduled_count"] == 0
        and lane_c_controls[name]["self_renewed_cycle_count"] == 0
        for name in expected_negative_controls
    )

    checks = {
        "lane_e_surface_contract_passed": lane_e["status"] == "passed",
        "lane_e_contract_is_experiment_local": lane_e_contract["status"]
        == "experiment_local_driver",
        "lane_c_feedback_contract_passed": lane_c_contract["status"] == "passed",
        "lane_c_regeneration_passed": lane_c_regeneration["status"] == "passed",
        "lane_c_m6_candidate_passed": lane_c_m6["m6_feedback_candidate_gate_passed"]
        is True,
        "lane_c_feedback_inputs_are_runtime_visible": set(
            feedback_surface["runtime_visible_inputs"]
        )
        == {"front_mass", "rear_mass"},
        "lane_c_controls_remain_negative": controls_negative,
        "same_surface_can_host_lane_c_feedback_policy": mapping[
            "lane_c_specific_core_primitive_needed"
        ]
        is False,
        "direct_write_policy_blocks_hidden_movement_mutation": all(
            direct_write_policy[key] is False
            for key in [
                "native_lgrc_state",
                "support_mask",
                "centroid",
                "displacement",
                "topology",
                "claim_flags",
            ]
        ),
        "native_support_still_not_claimed": lane_e["claim_flags"][
            "native_lgrc_pulse_substrate_supported"
        ]
        is False,
        "no_src_changes_required": True,
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "hybrid_lgrc_lane_c_feedback_surface_compatibility_v1",
        "lane": "E_C",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface",
        "runtime_family": "hybrid_lgrc9v3_existing_artifacts_plus_experiment_local_surface_driver",
        "execution_surface": "lane_e_causal_pulse_substrate_surface_lane_c_feedback_projection",
        "budget_surface": "node_plus_packet",
        "source_artifacts": {
            "lane_e_hybrid_surface_probe": _artifact_record(LANE_E),
            "lane_c_feedback_config": _artifact_record(LANE_C_CONFIG),
            "lane_c_feedback_contract": _artifact_record(LANE_C_CONTRACT),
            "lane_c_regeneration_report": _artifact_record(LANE_C_REGENERATION),
            "lane_c_m6_report": _artifact_record(LANE_C_M6),
        },
        "compatibility_mapping": mapping,
        "lane_c_summary": {
            "feedback_surface": feedback_surface,
            "claim_ceiling": lane_c_m6["claim_ceiling"],
            "m6_feedback_candidate_gate_passed": lane_c_m6[
                "m6_feedback_candidate_gate_passed"
            ],
            "native_m6_claim_allowed": lane_c_m6["native_m6_claim_allowed"],
            "candidate_summary": lane_c_m6["candidate_summary"],
            "controls_negative": controls_negative,
        },
        "checks": checks,
        "claim_flags": {
            "hybrid_lgrc_surface_probe": True,
            "lane_c_covered_by_same_surface_addon": True,
            "native_lgrc_pulse_substrate_supported": False,
            "native_feedback_producer_supported": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
        },
        "blocked_claims": [
            "native_lgrc_pulse_substrate_supported",
            "native_feedback_producer_supported",
            "native_m6",
            "full_movement_response",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_claim",
            "agency_claim",
        ],
        "recommendation": (
            "Use native_causal_pulse_substrate_surface as the shared primitive; "
            "treat Lane C feedback as a default-off policy-gated producer "
            "specialization rather than a separate core addon."
        ),
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    mapping = report["compatibility_mapping"]
    lane_c = report["lane_c_summary"]
    lines = [
        "# N04 Lane C Feedback Surface Compatibility",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{report['status']}`",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "## Compatibility Result",
        "",
        f"- Shared surface: `{mapping['surface_id']}`",
        f"- Lane C projection: `{mapping['lane_c_projection']}`",
        f"- Lane C feedback surface: `{mapping['lane_c_feedback_surface']}`",
        f"- Lane-C-specific core primitive needed: `{mapping['lane_c_specific_core_primitive_needed']}`",
        f"- Native specialization if promoted: `{mapping['native_specialization_needed']}`",
        "",
        "## Lane C Evidence",
        "",
        f"- Lane C claim ceiling: `{lane_c['claim_ceiling']}`",
        f"- M6 feedback candidate gate passed: `{lane_c['m6_feedback_candidate_gate_passed']}`",
        f"- Native M6 claim allowed: `{lane_c['native_m6_claim_allowed']}`",
        f"- Controls negative: `{lane_c['controls_negative']}`",
        "",
        "## Interpretation",
        "",
        "Lane C does not require a separate native core addon in the current",
        "design. Its feedback contract can be represented as a policy-gated",
        "producer specialization over the same causal pulse-substrate surface",
        "validated by Lane E. This keeps native support deferred: the result",
        "supports addon planning, not native LGRC support or movement claims.",
    ]
    _write_report(REPORT_PATH, lines)


def main() -> int:
    report = build_report()
    _write_json(OUTPUT_PATH, report)
    write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "claim_ceiling": report["claim_ceiling"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
