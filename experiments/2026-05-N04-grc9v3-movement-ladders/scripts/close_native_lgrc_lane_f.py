#!/usr/bin/env python3
"""Close N04 Lane F after native LGRC surface bridge validation.

This closeout consumes the Phase 8 Iteration 56 Lane F bridge artifact and
records the N04 interpretation: native pulse-substrate surface support is
validated, while movement, native M6, agency, and identity claims remain
blocked.
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
SOURCE_PATH = N04 / "outputs/native_lgrc_lane_f_surface_bridge.json"
OUTPUT_PATH = N04 / "outputs/n04_lane_f_native_surface_closeout.json"
REPORT_PATH = N04 / "reports/n04_lane_f_native_surface_closeout.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/close_native_lgrc_lane_f.py"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run_git_command(args: list[str]) -> dict[str, Any]:
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


def _load_bridge() -> dict[str, Any]:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"missing Lane F bridge artifact: {SOURCE_PATH}")
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


def _expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _control_summary(bridge: dict[str, Any]) -> dict[str, Any]:
    controls = bridge.get("controls", [])
    return {
        "control_count": len(controls),
        "all_controls_passed": all(control.get("passed") is True for control in controls),
        "primary_blockers": {
            control.get("lane_id", "unknown"): control.get("primary_blocker")
            for control in controls
        },
    }


def _build_closeout(bridge: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    flags = bridge.get("claim_flags", {})
    lane_f_bridge = bridge.get("lane_f_bridge", {})
    positive_fixture = bridge.get("positive_fixture", {})
    validator = positive_fixture.get("artifact_validator", {})
    controls = _control_summary(bridge)

    _expect(
        bridge.get("schema") == "movement_ladder_report_v1",
        "source bridge schema is not movement_ladder_report_v1",
        failures,
    )
    _expect(
        bridge.get("runtime_family") == "LGRC9V3",
        "source bridge runtime_family is not LGRC9V3",
        failures,
    )
    _expect(
        flags.get("native_lgrc_pulse_substrate_supported") is True,
        "native surface support flag is not true",
        failures,
    )
    _expect(
        flags.get("native_causal_pulse_substrate_surface_validated") is True,
        "native surface validation flag is not true",
        failures,
    )
    _expect(
        validator.get("valid") is True
        and validator.get("native_lgrc_pulse_substrate_supported") is True,
        "artifact-only validator did not support the native surface",
        failures,
    )
    _expect(
        lane_f_bridge.get("artifact_only_full_chain_reconstructed") is True,
        "artifact-only full causal chain was not reconstructed",
        failures,
    )
    _expect(
        lane_f_bridge.get("regenerated_native_pulse_work_not_copied_from_original_e3_schedule")
        is True,
        "regenerated native pulse work copying audit did not pass",
        failures,
    )
    _expect(controls["all_controls_passed"], "not all Lane F controls passed", failures)

    blocked_claim_flags = {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "native_m6": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "movement_claim_inherited_from_n03": False,
    }
    for field, expected in blocked_claim_flags.items():
        _expect(
            flags.get(field) is expected,
            f"claim flag {field} is not blocked as expected",
            failures,
        )

    status = "passed" if not failures else "failed"
    closeout: dict[str, Any] = {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_lane_f_native_surface_closeout_v1",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "budget_surface": "node_plus_packet",
        "source_artifact": {
            "path": str(SOURCE_PATH.relative_to(ROOT)),
            "sha256": _sha256(SOURCE_PATH),
            "report_kind": bridge.get("report_kind"),
        },
        "lane_f_status": "native_surface_support_complete" if status == "passed" else "failed",
        "claim_ceiling": (
            "native_lgrc_pulse_substrate_surface_supported"
            if status == "passed"
            else "lane_f_closeout_failed"
        ),
        "native_surface_evidence": {
            "native_lgrc_pulse_substrate_supported": flags.get(
                "native_lgrc_pulse_substrate_supported"
            ),
            "native_causal_pulse_substrate_surface_validated": flags.get(
                "native_causal_pulse_substrate_surface_validated"
            ),
            "artifact_only_full_chain_reconstructed": lane_f_bridge.get(
                "artifact_only_full_chain_reconstructed"
            ),
            "validated_chain": lane_f_bridge.get("validated_chain", []),
            "regenerated_pulse_source": lane_f_bridge.get("regenerated_pulse_source"),
            "regenerated_native_pulse_work_not_copied_from_original_e3_schedule": (
                lane_f_bridge.get(
                    "regenerated_native_pulse_work_not_copied_from_original_e3_schedule"
                )
            ),
            "coupling_scheduled": positive_fixture.get("coupling_scheduled"),
            "feedback_scheduled": positive_fixture.get("feedback_scheduled"),
            "surface_row_count": positive_fixture.get("surface_row_count"),
            "topology_changed": positive_fixture.get("topology", {}).get(
                "topology_changed"
            ),
            "topology_events_enabled": positive_fixture.get("topology", {}).get(
                "topology_events_enabled"
            ),
        },
        "controls": controls,
        "topology_lineage": {
            "lgrc3_lineage_transport_implemented": False,
            "decision": "deferred_for_native_surface_v1",
            "control_lane": "F_topology_lineage_deferred_control",
            "claim_impact": "does_not_block_fixed_topology_native_surface_support",
        },
        "claim_flags": {
            **blocked_claim_flags,
            "native_causal_pulse_substrate_surface_enabled": flags.get(
                "native_causal_pulse_substrate_surface_enabled"
            ),
            "native_causal_pulse_substrate_surface_validated": flags.get(
                "native_causal_pulse_substrate_surface_validated"
            ),
            "native_lgrc_pulse_substrate_supported": flags.get(
                "native_lgrc_pulse_substrate_supported"
            ),
        },
        "n04_interpretation": (
            "Lane F validates native LGRC causal pulse-substrate surface support "
            "as artifact-validatable scheduling evidence. It does not validate "
            "movement, native M6, agency, biological behavior, or RC identity "
            "acceptance."
        ),
        "next_step": "phase8_iteration_57_closeout",
        "validation": {
            "status": status,
            "failure_reasons": failures,
        },
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "rev_parse_head": _run_git_command(["rev-parse", "HEAD"]),
            "status_short": _run_git_command(["status", "--short"]),
        },
    }
    return closeout


def _write_report(closeout: dict[str, Any]) -> None:
    evidence = closeout["native_surface_evidence"]
    controls = closeout["controls"]
    validation = closeout["validation"]
    flags = closeout["claim_flags"]
    lines = [
        "# N04 Lane F Native Surface Closeout",
        "",
        "## Result",
        "",
        f"- status: `{validation['status']}`",
        f"- lane_f_status: `{closeout['lane_f_status']}`",
        f"- claim_ceiling: `{closeout['claim_ceiling']}`",
        f"- source_artifact: `{closeout['source_artifact']['path']}`",
        "",
        "Lane F is complete as native LGRC pulse-substrate surface support. It is",
        "not a movement, native M6, agency, biological, or RC identity-acceptance",
        "claim.",
        "",
        "## Evidence",
        "",
        f"- native_lgrc_pulse_substrate_supported: `{evidence['native_lgrc_pulse_substrate_supported']}`",
        f"- native_causal_pulse_substrate_surface_validated: `{evidence['native_causal_pulse_substrate_surface_validated']}`",
        f"- artifact_only_full_chain_reconstructed: `{evidence['artifact_only_full_chain_reconstructed']}`",
        f"- validated_chain: `{', '.join(evidence['validated_chain'])}`",
        f"- regenerated_pulse_source: `{evidence['regenerated_pulse_source']}`",
        "- regenerated_native_pulse_work_not_copied_from_original_e3_schedule: "
        f"`{evidence['regenerated_native_pulse_work_not_copied_from_original_e3_schedule']}`",
        f"- controls_passed: `{controls['all_controls_passed']}`",
        f"- control_count: `{controls['control_count']}`",
        "",
        "## Blocked Claims",
        "",
    ]
    for field in (
        "movement_claim_allowed",
        "loop_driven_movement_claim_allowed",
        "locomotion_like_claim_allowed",
        "adaptive_topology_entry_allowed",
        "native_m6",
        "biological_claim_allowed",
        "agency_claim_allowed",
        "identity_acceptance_claim_allowed",
        "movement_claim_inherited_from_n03",
    ):
        lines.append(f"- {field}: `{flags[field]}`")
    lines.extend(
        [
            "",
            "## Topology",
            "",
            "- LGRC-3 lineage transport remains deferred for native surface v1.",
            "- The positive Lane F bridge is fixed-topology and reports no topology change.",
            "",
            "## Next Step",
            "",
            "`phase8_iteration_57_closeout`",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    bridge = _load_bridge()
    closeout = _build_closeout(bridge)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload_without_artifacts = dict(closeout)
    payload_without_artifacts.pop("artifacts", None)
    closeout["artifacts"] = {
        "json": {
            "path": str(OUTPUT_PATH.relative_to(ROOT)),
            "payload_sha256_without_artifacts": _digest_json(payload_without_artifacts),
        },
        "markdown": {
            "path": str(REPORT_PATH.relative_to(ROOT)),
        },
    }
    OUTPUT_PATH.write_text(json.dumps(closeout, indent=2, sort_keys=True), encoding="utf-8")
    _write_report(closeout)

    closeout["artifacts"]["markdown"]["sha256"] = _sha256(REPORT_PATH)
    OUTPUT_PATH.write_text(json.dumps(closeout, indent=2, sort_keys=True), encoding="utf-8")

    if closeout["validation"]["status"] != "passed":
        raise SystemExit("Lane F closeout failed; see output artifact")


if __name__ == "__main__":
    main()
