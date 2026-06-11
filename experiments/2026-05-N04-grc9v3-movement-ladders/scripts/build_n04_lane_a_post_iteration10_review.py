#!/usr/bin/env python3
"""Build N04 Lane A2 post-Lane-B / post-Iteration-10 evidence review."""

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

ARTIFACTS = {
    "a1_evidence_ladder": N04 / "outputs/n04_evidence_ladder_audit.json",
    "lane_b_closeout": N04 / "outputs/n04_lane_b_direction_parity_closeout.json",
    "lane_b_lock": N04 / "outputs/n04_lane_b_lock_audit.json",
    "lane_b_reversed_telemetry": N04
    / "outputs/reversed_e3_pulse_telemetry_validation.json",
    "lane_b_boundary": N04 / "outputs/reversed_e3_pulse_boundary_coupling_report.json",
    "lane_b_m4_m5": N04 / "outputs/reversed_e3_pulse_m4_m5_classification.json",
    "iteration_10_m6": N04 / "outputs/self_renewing_movement_candidate_report.json",
}

OUTPUT_PATH = N04 / "outputs/n04_lane_a_post_iteration10_review.json"
REPORT_PATH = N04 / "reports/n04_lane_a_post_iteration10_review.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_lane_a_post_iteration10_review.py"
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


def _artifact_record(path: Path) -> dict[str, Any]:
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


def build_review() -> dict[str, Any]:
    data = {key: _load_json(path) for key, path in ARTIFACTS.items()}
    artifacts = {key: _artifact_record(path) for key, path in ARTIFACTS.items()}

    lane_b = data["lane_b_closeout"]
    lane_b_m4_m5 = data["lane_b_m4_m5"]
    iteration_10 = data["iteration_10_m6"]

    updated_ladder = [
        {
            "level": "M0_M3_fixed_substrate",
            "classification": "unchanged_from_A1_movement_negative",
            "allowed_evidence": [
                "fixed-substrate nulls remain negative",
                "B1/B1_reversed remain subthreshold directional bias only",
                "identity and shape safety gates do not promote movement",
            ],
            "blocked_claims": [
                "fixed_substrate_movement_response",
                "identity_preserving_displacement",
            ],
            "source": artifacts["a1_evidence_ladder"]["path"],
        },
        {
            "level": "M4_M5_direction_parity",
            "classification": "m5_direction_parity_supported_boundary_response",
            "allowed_evidence": [
                "native true counter-clockwise E3 telemetry is available and validated",
                "forward and true reversed telemetry use the same S0 mapping and classifier",
                "opposite-signed response has matched boundary score and pulse-locked windows",
            ],
            "blocked_claims": [
                "unrestricted_movement",
                "locomotion_like_basin_dynamics",
                "adaptive_topology_movement",
            ],
            "source": artifacts["lane_b_closeout"]["path"],
            "summary": {
                "claim_ceiling": lane_b["claim_ceiling"],
                "m5_candidate_gate_passed": lane_b_m4_m5[
                    "m5_candidate_gate_passed"
                ],
                "m5_full_direction_parity_gate_passed": lane_b_m4_m5[
                    "m5_full_direction_parity_gate_passed"
                ],
                "direction_parity": lane_b_m4_m5["direction_parity"],
            },
        },
        {
            "level": "M6_self_renewal",
            "classification": "m6_not_opened_feedback_path_absent",
            "allowed_evidence": [
                "repeated boundary-response persistence is measured",
                "identity and shape/economy gates remain bounded for the boundary fixture",
            ],
            "blocked_claims": [
                "self_renewing_movement",
                "locomotion_like_basin_dynamics",
                "movement_restores_pulse_conditions",
                "polarity_regeneration",
            ],
            "source": artifacts["iteration_10_m6"]["path"],
            "summary": {
                "claim_ceiling": iteration_10["m6_result"]["claim_ceiling"],
                "m6_opened": iteration_10["m6_result"]["m6_opened"],
                "m6_gate_passed": iteration_10["m6_result"]["m6_gate_passed"],
                "primary_blocker": iteration_10["m6_result"]["primary_blocker"],
            },
        },
    ]

    claim_flags = {
        "movement_claim_allowed": False,
        "boundary_coupled_movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "native_lgrc9v3_e3_pulse_used": True,
        "native_grc9v3_proposal_flux_control_used": False,
        "native_grc9v3_proposal_flux_loop_claim": False,
        "m6_opened": False,
    }

    checks = {
        "a1_remains_valid": data["a1_evidence_ladder"]["status"] == "passed",
        "lane_b_locked": data["lane_b_lock"]["status"] == "passed",
        "lane_b_promoted_to_direction_parity_boundary_response": (
            lane_b["claim_ceiling"]
            == "m5_direction_parity_supported_boundary_response"
        ),
        "iteration_10_failed_closed": iteration_10["status"] == "passed_fail_closed",
        "m6_not_opened": iteration_10["m6_result"]["m6_opened"] is False,
        "all_claim_flags_blocked": all(
            claim_flags[key] is False
            for key in [
                "movement_claim_allowed",
                "boundary_coupled_movement_claim_allowed",
                "loop_driven_movement_claim_allowed",
                "locomotion_like_claim_allowed",
                "adaptive_topology_entry_allowed",
                "movement_claim_inherited_from_n03",
                "native_grc9v3_proposal_flux_control_used",
                "native_grc9v3_proposal_flux_loop_claim",
                "m6_opened",
            ]
        ),
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_lane_a_post_iteration10_review_v1",
        "lane": "A",
        "iteration": "A2",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "m5_direction_parity_supported_boundary_response__m6_blocked",
        "updated_evidence_ladder": updated_ladder,
        "allowed_evidence_labels": [
            "fixed_substrate_negative",
            "subthreshold_directional_bias",
            "state_mediated_boundary_coupling_fixture_positive",
            "m5_direction_parity_supported_boundary_response",
            "m6_not_opened_feedback_path_absent",
        ],
        "blocked_claims": [
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "self_renewing_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_or_agency_claim",
            "movement_inherited_from_n03",
        ],
        "claim_flags": claim_flags,
        "checks": checks,
        "source_artifacts": artifacts,
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(review: dict[str, Any]) -> None:
    lines = [
        "# N04 Lane A2 Post-Iteration-10 Review",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{review['status']}`",
        f"Claim ceiling: `{review['claim_ceiling']}`",
        "",
        "## Updated Evidence Ladder",
        "",
        "| Level | Classification | Source |",
        "|---|---|---|",
    ]
    for item in review["updated_evidence_ladder"]:
        lines.append(
            f"| `{item['level']}` | `{item['classification']}` | `{item['source']}` |"
        )
    lines.extend(["", "## Allowed Evidence Labels", ""])
    for label in review["allowed_evidence_labels"]:
        lines.append(f"- `{label}`")
    lines.extend(["", "## Blocked Claims", ""])
    for claim in review["blocked_claims"]:
        lines.append(f"- `{claim}`")
    lines.extend(["", "## Checks", "", "| Check | Passed |", "|---|---:|"])
    for key, value in review["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A2 updates Lane A after Lane B and Iteration 10. Lane B is promoted",
            "from control-limited M5 candidate to direction-parity-supported",
            "boundary response. Iteration 10 then fails closed for M6 because the",
            "S0 boundary response does not feed back into native E3 pulse-generating",
            "conditions. The strongest current N04 ceiling is therefore",
            "`m5_direction_parity_supported_boundary_response` with M6 blocked.",
            "",
        ]
    )
    _write_report(REPORT_PATH, lines)


def main() -> int:
    review = build_review()
    _write_json(OUTPUT_PATH, review)
    write_report(review)
    print(
        json.dumps(
            {
                "status": review["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if review["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
