#!/usr/bin/env python3
"""Review whether existing N04/Phase 8 artifacts support native M6.

This is an evidence review, not a new movement fixture. It consumes the
experiment-local Lane C M6 candidate and the native Lane F surface bridge to
decide what is now unlocked and what remains unvalidated.
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

LANE_C_M6 = N04 / "outputs/reopened_m6_feedback_gate_report.json"
LANE_F_BRIDGE = N04 / "outputs/native_lgrc_lane_f_surface_bridge.json"
LANE_F_CLOSEOUT = N04 / "outputs/n04_lane_f_native_surface_closeout.json"
PHASE8_CLOSEOUT = ROOT / "implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json"

OUTPUT_PATH = N04 / "outputs/native_m6_evidence_review.json"
REPORT_PATH = N04 / "reports/native_m6_evidence_review.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/review_native_m6_evidence.py"
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": _sha256(path),
    }


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    gates = payload["native_m6_evidence_gates"]
    blockers = payload["remaining_blockers"]
    lines = [
        "# N04 Native M6 Evidence Review",
        "",
        f"Status: `{payload['status']}`",
        f"Claim ceiling: `{payload['claim_ceiling']}`",
        "",
        "## Result",
        "",
        payload["interpretation"],
        "",
        "## Evidence Cleared",
        "",
    ]
    for item in payload["evidence_cleared"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Native M6 Gates",
            "",
        ]
    )
    for key, value in gates.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
        ]
    )
    for item in blockers:
        lines.append(f"- `{item['blocker']}`: {item['description']}")
    lines.extend(
        [
            "",
            "## Next Validator",
            "",
            "The next validator must run the Lane C feedback M6 gate on a native",
            "LGRC9V3 pulse-substrate surface using the same movement substrate,",
            "native feedback producer records, native scheduled packets, and",
            "artifact-only replay chain.",
            "",
            "## Claim Flags",
            "",
            "```json",
            json.dumps(payload["claim_flags"], indent=2, sort_keys=True),
            "```",
            "",
            "Command:",
            "",
            "```bash",
            payload["environment"]["command"],
            "```",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_review() -> dict[str, Any]:
    lane_c = _load_json(LANE_C_M6)
    lane_f_bridge = _load_json(LANE_F_BRIDGE)
    lane_f_closeout = _load_json(LANE_F_CLOSEOUT)
    phase8 = _load_json(PHASE8_CLOSEOUT)

    lane_c_gates = lane_c.get("gates", {})
    bridge_flags = lane_f_bridge.get("claim_flags", {})
    bridge = lane_f_bridge.get("lane_f_bridge", {})
    positive = lane_f_bridge.get("positive_fixture", {})
    lane_f_evidence = lane_f_closeout.get("native_surface_evidence", {})

    gates = {
        "experiment_local_m6_feedback_candidate_available": (
            lane_c.get("status") == "passed"
            and lane_c.get("m6_feedback_candidate_gate_passed") is True
        ),
        "lane_c_movement_restores_pulse_conditions": (
            lane_c_gates.get("movement_restores_pulse_conditions") is True
        ),
        "lane_c_polarity_regeneration_measured": (
            lane_c_gates.get("polarity_regeneration_measured") is True
        ),
        "lane_c_repeated_cycle_persistence_self_renewed": (
            lane_c_gates.get("repeated_cycle_persistence_self_renewed") is True
        ),
        "native_pulse_substrate_surface_supported": (
            bridge_flags.get("native_lgrc_pulse_substrate_supported") is True
            and lane_f_evidence.get("native_lgrc_pulse_substrate_supported") is True
        ),
        "native_feedback_producer_schedules_from_feedback_eligibility": (
            positive.get("feedback_scheduled") is True
            and positive.get("feedback_regenerated_pulse_source")
            == "feedback_eligibility"
            and positive.get("feedback_copied_from_original_schedule") is False
        ),
        "native_artifact_chain_reconstructed": (
            bridge.get("artifact_only_full_chain_reconstructed") is True
            and lane_f_evidence.get("artifact_only_full_chain_reconstructed") is True
        ),
        "native_controls_passed": (
            lane_f_closeout.get("controls", {}).get("all_controls_passed") is True
        ),
        "native_m6_same_fixture_validator_available": False,
        "native_repeated_self_renewed_cycles_measured": False,
        "native_movement_identity_shape_gates_integrated": False,
    }

    evidence_cleared = [
        key for key, value in gates.items() if value is True
    ]
    remaining_blockers = [
        {
            "blocker": "native_m6_same_fixture_validator_absent",
            "description": (
                "No artifact yet runs the Lane C M6 feedback gate on the native "
                "Lane F pulse-substrate surface using the same S0 movement "
                "fixture and native producer records."
            ),
        },
        {
            "blocker": "native_repeated_self_renewed_cycles_not_measured",
            "description": (
                "Lane C measured three self-renewed cycles in an experiment-local "
                "adapter. Lane F proves native feedback scheduling, but does not "
                "yet measure repeated native cycles on the movement fixture."
            ),
        },
        {
            "blocker": "native_identity_shape_movement_gates_not_integrated",
            "description": (
                "Native surface evidence has not yet been reclassified through a "
                "combined M0-M5/M6 movement validator on the same artifact chain."
            ),
        },
    ]

    all_prerequisites = all(
        gates[key]
        for key in [
            "experiment_local_m6_feedback_candidate_available",
            "lane_c_movement_restores_pulse_conditions",
            "lane_c_polarity_regeneration_measured",
            "lane_c_repeated_cycle_persistence_self_renewed",
            "native_pulse_substrate_surface_supported",
            "native_feedback_producer_schedules_from_feedback_eligibility",
            "native_artifact_chain_reconstructed",
            "native_controls_passed",
        ]
    )

    native_m6_validated = all_prerequisites and all(
        gates[key]
        for key in [
            "native_m6_same_fixture_validator_available",
            "native_repeated_self_renewed_cycles_measured",
            "native_movement_identity_shape_gates_integrated",
        ]
    )

    claim_flags = {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "native_m6": native_m6_validated,
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "native_m6_evidence_review_v1",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "status": "passed_fail_closed",
        "claim_ceiling": (
            "native_m6_prerequisites_supported_validator_absent"
            if all_prerequisites
            else "native_m6_prerequisites_incomplete"
        ),
        "native_m6_evidence_gates": gates,
        "evidence_cleared": evidence_cleared,
        "remaining_blockers": remaining_blockers,
        "candidate_summary": {
            "lane_c_claim_ceiling": lane_c.get("claim_ceiling"),
            "lane_c_forward_self_renewed_cycle_count": lane_c.get(
                "candidate_summary", {}
            ).get("forward_self_renewed_cycle_count"),
            "lane_c_reversed_self_renewed_cycle_count": lane_c.get(
                "candidate_summary", {}
            ).get("reversed_self_renewed_cycle_count"),
            "lane_f_claim_ceiling": lane_f_closeout.get("claim_ceiling"),
            "phase8_claim_ceiling": phase8.get("claim_ceiling"),
        },
        "claim_flags": claim_flags,
        "source_artifacts": {
            "lane_c_m6": _artifact(LANE_C_M6),
            "lane_f_bridge": _artifact(LANE_F_BRIDGE),
            "lane_f_closeout": _artifact(LANE_F_CLOSEOUT),
            "phase8_closeout": _artifact(PHASE8_CLOSEOUT),
        },
        "interpretation": (
            "The previous M6 blocker has moved. It is no longer absence of a "
            "native feedback producer: Phase 8/Lane F now supports the native "
            "causal pulse-substrate surface and feedback scheduling from "
            "feedback eligibility. The remaining blocker is that no native "
            "same-fixture M6 validator has replayed Lane C's self-renewal gate "
            "on the S0 movement substrate using native producer artifacts. "
            "Native M6 therefore remains blocked, but the prerequisites for a "
            "native M6 validator are now present."
        ),
        "next_step": "run_native_m6_same_fixture_validator",
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "rev_parse_head": _run_git(["rev-parse", "HEAD"]),
            "diff_check": _run_git(["diff", "--check"]),
            "status_short": _run_git(["status", "--short"]),
        },
    }


def main() -> None:
    review = build_review()
    _write_json(OUTPUT_PATH, review)
    _write_report(REPORT_PATH, review)
    print(
        json.dumps(
            {
                "status": review["status"],
                "claim_ceiling": review["claim_ceiling"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
