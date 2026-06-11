#!/usr/bin/env python3
"""Audit the N04 native M6 validation checklist."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
SOURCE_PATH = N04 / "outputs/native_m6_same_fixture_validator.json"
OUTPUT_PATH = N04 / "outputs/native_m6_validation_checklist_audit.json"
REPORT_PATH = N04 / "reports/native_m6_validation_checklist_audit.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/audit_native_m6_validation_list.py"
)

TOL = 1e-12
SCHEDULED_REASON = "feedback_coupled_pulse_packet_departure_scheduled"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _scheduled_cycles(direction: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        cycle
        for cycle in direction.get("cycles", [])
        if cycle.get("producer_reason_code") == SCHEDULED_REASON
    ]


def _unique(values: list[Any]) -> bool:
    return len(values) == len(set(values))


def _direction_cycle_audit(direction: dict[str, Any]) -> dict[str, Any]:
    cycles = direction.get("cycles", [])
    scheduled = _scheduled_cycles(direction)
    scheduled_ids = [cycle.get("scheduled_event_id") for cycle in scheduled]
    surface_digests = [cycle.get("surface_digest") for cycle in scheduled]
    regenerated_sources = [cycle.get("regenerated_pulse_source") for cycle in cycles]
    copied_flags = [cycle.get("copied_from_original_schedule") for cycle in cycles]
    return {
        "direction": direction.get("direction"),
        "seeded_first_response_required": direction.get("seeded_first_response_required"),
        "self_renewed_cycle_count": direction.get("self_renewed_cycle_count"),
        "cycle_record_count": len(cycles),
        "scheduled_cycle_count": len(scheduled),
        "scheduled_event_ids_unique": _unique(scheduled_ids),
        "surface_digests_unique": _unique(surface_digests),
        "all_scheduled_from_feedback_eligibility": all(
            source == "feedback_eligibility" for source in regenerated_sources
        ),
        "no_cycle_copied_from_original_schedule": all(flag is False for flag in copied_flags),
        "scheduled_event_ids": scheduled_ids,
        "surface_digests": surface_digests,
        "boundary_polarity_scores": [
            cycle.get("boundary_polarity_score") for cycle in cycles
        ],
    }


def _control_reason(control: dict[str, Any]) -> str:
    return str(control.get("primary_blocker") or control.get("reason_code") or "")


def _build_audit(source: dict[str, Any]) -> dict[str, Any]:
    forward = source["forward"]
    reversed_ = source["reversed"]
    forward_cycles = _direction_cycle_audit(forward)
    reversed_cycles = _direction_cycle_audit(reversed_)
    forward_validator = forward.get("artifact_validator", {})
    reversed_validator = reversed_.get("artifact_validator", {})
    controls = source.get("controls", {})
    control_reasons = {
        key: _control_reason(value)
        for key, value in controls.items()
    }
    broad_claim_flags = {
        key: value
        for key, value in source.get("claim_flags", {}).items()
        if key not in {"native_m6", "native_m6_candidate_gate_passed"}
    }
    dx_forward = float(forward["centroid_delta"])
    dx_reversed = float(reversed_["centroid_delta"])

    checks = {
        "seeded_first_contact_vs_self_renewed_later_pulses": {
            "passed": (
                forward_cycles["seeded_first_response_required"] is True
                and reversed_cycles["seeded_first_response_required"] is True
                and forward_cycles["scheduled_cycle_count"] == 3
                and reversed_cycles["scheduled_cycle_count"] == 3
                and forward_cycles["all_scheduled_from_feedback_eligibility"]
                and reversed_cycles["all_scheduled_from_feedback_eligibility"]
                and forward_cycles["no_cycle_copied_from_original_schedule"]
                and reversed_cycles["no_cycle_copied_from_original_schedule"]
            ),
            "evidence": {
                "forward": forward_cycles,
                "reversed": reversed_cycles,
            },
        },
        "native_artifact_chain_replay": {
            "passed": (
                forward_validator.get("valid") is True
                and reversed_validator.get("valid") is True
                and not forward_validator.get("failure_reasons")
                and not reversed_validator.get("failure_reasons")
            ),
            "evidence": {
                "validator": "validate_lgrc9v3_causal_pulse_substrate_surface_artifacts",
                "forward_surface_row_count": forward_validator.get("surface_row_count"),
                "reversed_surface_row_count": reversed_validator.get("surface_row_count"),
                "forward_validated_surface_ids": forward_validator.get(
                    "validated_surface_ids", []
                ),
                "reversed_validated_surface_ids": reversed_validator.get(
                    "validated_surface_ids", []
                ),
            },
            "limitation": (
                "The artifact validator passes and surface ids are serialized, but "
                "the native M6 JSON stores producer/event chain details as digests "
                "rather than a full per-cycle expanded chain."
            ),
        },
        "cycle_count_semantics": {
            "passed": (
                forward["self_renewed_cycle_count"] == len(_scheduled_cycles(forward))
                and reversed_["self_renewed_cycle_count"] == len(_scheduled_cycles(reversed_))
                and forward_cycles["scheduled_event_ids_unique"]
                and reversed_cycles["scheduled_event_ids_unique"]
                and forward_cycles["surface_digests_unique"]
                and reversed_cycles["surface_digests_unique"]
            ),
            "evidence": {
                "forward_self_renewed_cycle_count": forward["self_renewed_cycle_count"],
                "reversed_self_renewed_cycle_count": reversed_[
                    "self_renewed_cycle_count"
                ],
                "forward_scheduled_event_ids": forward_cycles["scheduled_event_ids"],
                "reversed_scheduled_event_ids": reversed_cycles["scheduled_event_ids"],
            },
        },
        "forward_reversed_symmetry": {
            "passed": (
                dx_forward > 0.0
                and dx_reversed < 0.0
                and math.isclose(abs(dx_forward), abs(dx_reversed), abs_tol=1e-9)
                and forward.get("front_mask") == reversed_.get("front_mask")
                and forward.get("rear_mask") == reversed_.get("rear_mask")
                and source.get("movement_substrate") == "S0_chain_v1"
                and source.get("direction_parity", {}).get("passed") is True
            ),
            "evidence": {
                "forward_centroid_delta": dx_forward,
                "reversed_centroid_delta": dx_reversed,
                "front_mask": forward.get("front_mask"),
                "rear_mask": forward.get("rear_mask"),
                "movement_substrate": source.get("movement_substrate"),
            },
        },
        "identity_shape_same_fixture_scope": {
            "passed": (
                source.get("movement_substrate") == "S0_chain_v1"
                and source.get("gates", {}).get("topology_fixed") is True
                and forward.get("identity_shape_gates_passed") is True
                and reversed_.get("identity_shape_gates_passed") is True
                and all(value is False for value in broad_claim_flags.values())
            ),
            "evidence": {
                "movement_substrate": source.get("movement_substrate"),
                "forward_profile_similarity": forward.get("profile_similarity"),
                "reversed_profile_similarity": reversed_.get("profile_similarity"),
                "forward_width_relative_change": forward.get("width_relative_change"),
                "reversed_width_relative_change": reversed_.get("width_relative_change"),
                "blocked_claim_flags": broad_claim_flags,
            },
        },
        "controls_fail_for_distinct_blockers": {
            "passed": (
                all(control.get("passed") is True for control in controls.values())
                and len(set(control_reasons.values())) == len(control_reasons)
                and all(control_reasons.values())
            ),
            "evidence": control_reasons,
        },
        "runtime_producers_do_not_emit_claims": {
            "passed": (
                forward_validator.get("movement_claim_allowed") is False
                and reversed_validator.get("movement_claim_allowed") is False
                and forward_validator.get("native_m6") is False
                and reversed_validator.get("native_m6") is False
                and all(value is False for value in broad_claim_flags.values())
            ),
            "evidence": {
                "forward_artifact_validator_claims": {
                    "movement_claim_allowed": forward_validator.get(
                        "movement_claim_allowed"
                    ),
                    "native_m6": forward_validator.get("native_m6"),
                },
                "reversed_artifact_validator_claims": {
                    "movement_claim_allowed": reversed_validator.get(
                        "movement_claim_allowed"
                    ),
                    "native_m6": reversed_validator.get("native_m6"),
                },
                "report_claim_flags": source.get("claim_flags", {}),
            },
        },
    }

    passed = all(check["passed"] for check in checks.values())
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "native_m6_validation_checklist_audit_v1",
        "status": "passed" if passed else "failed",
        "source_artifact": str(SOURCE_PATH.relative_to(ROOT)),
        "claim_ceiling": source.get("claim_ceiling"),
        "native_m6_candidate_gate_passed": source.get(
            "native_m6_candidate_gate_passed"
        ),
        "checks": checks,
        "summary": (
            "The native M6 validation checklist passes. The current evidence "
            "supports a bounded same-fixture native M6 candidate, with broader "
            "movement, locomotion-like, adaptive topology, biological, agency, "
            "identity-acceptance, and inherited-N03 claims still blocked."
            if passed
            else "At least one native M6 validation checklist item failed."
        ),
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# N04 Native M6 Validation Checklist Audit",
        "",
        f"Status: `{payload['status']}`",
        f"Claim ceiling: `{payload['claim_ceiling']}`",
        "",
        "## Summary",
        "",
        payload["summary"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, check in payload["checks"].items():
        lines.append(f"| `{key}` | `{check['passed']}` |")
    lines.extend(["", "## Notes", ""])
    chain_check = payload["checks"]["native_artifact_chain_replay"]
    lines.append(f"- Artifact-chain limitation: {chain_check['limitation']}")
    lines.append(
        "- Producer/runtime claim boundary is validated by artifact validator "
        "`native_m6=false` and report-level broad claim flags remaining false."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source = _load_json(SOURCE_PATH)
    payload = _build_audit(source)
    _write_json(OUTPUT_PATH, payload)
    _write_report(REPORT_PATH, payload)
    if payload["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
