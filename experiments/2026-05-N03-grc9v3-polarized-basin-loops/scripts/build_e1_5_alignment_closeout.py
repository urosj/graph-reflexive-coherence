#!/usr/bin/env python3
"""Build the E1.5 LGRC9V3 alignment closeout report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from loop_observables import load_json, write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
SURFACE_INVENTORY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_surface_inventory.json"
LEDGER_SCHEMA_VALIDATION_PATH = EXPERIMENT_ROOT / "outputs" / "e1_event_ledger_schema_validation.json"
LEDGER_SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_d2_3_lgrc_event_ledger_summary.json"
LEDGER_VALIDATION_PATH = EXPERIMENT_ROOT / "outputs" / "e1_ledger_only_validation.json"
COMPATIBILITY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_compatibility.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_alignment_closeout.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_lgrc9v3_alignment_closeout.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/build_e1_5_alignment_closeout.py"
)


def _build_result() -> dict[str, Any]:
    inventory = load_json(SURFACE_INVENTORY_PATH)
    schema_validation = load_json(LEDGER_SCHEMA_VALIDATION_PATH)
    ledger_summary = load_json(LEDGER_SUMMARY_PATH)
    ledger_validation = load_json(LEDGER_VALIDATION_PATH)
    compatibility = load_json(COMPATIBILITY_PATH)

    prior_commands = {
        "E1.0": inventory["command"],
        "E1.1": schema_validation["command"],
        "E1.2": ledger_summary["command"],
        "E1.3": ledger_validation["command"],
        "E1.4": compatibility["command"],
        "E1.5": COMMAND,
    }
    artifacts = {
        "E1.0": [
            "outputs/e1_lgrc9v3_surface_inventory.json",
            "reports/e1_lgrc9v3_surface_inventory.md",
        ],
        "E1.1": [
            "configs/e1_lgrc9v3_event_ledger_schema.json",
            "outputs/e1_event_ledger_schema_validation.json",
            "reports/e1_event_ledger_schema_validation.md",
        ],
        "E1.2": [
            "outputs/e1_d2_3_lgrc_event_ledgers/*.jsonl",
            "outputs/e1_d2_3_lgrc_event_ledger_summary.json",
            "reports/e1_d2_3_lgrc_event_ledger_summary.md",
        ],
        "E1.3": [
            "outputs/e1_ledger_only_validation.json",
            "reports/e1_ledger_only_validation.md",
        ],
        "E1.4": [
            "outputs/e1_lgrc9v3_compatibility.json",
            "reports/e1_lgrc9v3_compatibility.md",
        ],
        "E1.5": [
            "outputs/e1_lgrc9v3_alignment_closeout.json",
            "reports/e1_lgrc9v3_alignment_closeout.md",
        ],
    }
    final_decision = {
        "selected_outcome": (
            "stop_and_publish_n03_native_grc9v3_negative_packet_positive_"
            "lgrc_adapter_compatible"
        ),
        "adapter_only_alignment_record": True,
        "experiment_local_e2_proposal": False,
        "core_lgrc9v3_task_requested": False,
        "movement_ladders_handoff_now": False,
        "reason": (
            "E1 answered its central question: D2.3 can be faithfully "
            "represented as LGRC9V3-style causal packet history. The result is "
            "adapter-compatible, not native runtime execution, so E1 should "
            "close without requesting a core task or movement handoff."
        ),
        "next_branch_if_pursued_later": (
            "Can native LGRC9V3.step or LGRC9V3.run_event_queue produce the "
            "D2.3 event ledger through declared runtime primitives?"
        ),
    }
    result = {
        "schema": "n03_e1_lgrc9v3_alignment_closeout_v1",
        "branch": "E1.5",
        "command": COMMAND,
        "status": "complete",
        "final_decision": final_decision,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": False,
            "adapter_only": True,
            "movement_claim_allowed": False,
        },
        "summary_claims": {
            "native_fixed_topology_grc9v3_proposal_flux": "negative_for_loop_generation_under_tested_fixtures",
            "experiment_local_packetized_mechanism": "positive_for_self_rearming_packet_pulse_under_controls",
            "lgrc_style_event_ledger": "validated_from_ledger_only",
            "lgrc9v3_compatibility": compatibility["classification"]["classification"],
            "core_task_requested": compatibility["core_task_recommendation"]["request_now"],
        },
        "validated_evidence": {
            "surface_inventory_classification": inventory["alignment"]["classification"],
            "schema_validation_status": schema_validation["status"],
            "converted_lane_count": ledger_summary["converted_lane_count"],
            "ledger_event_count": ledger_summary["total_event_count"],
            "ledger_only_validation_status": ledger_validation["status"],
            "ledger_positive_lanes": ledger_validation["ledger_positive_lanes"],
            "compatibility_classification": compatibility["classification"]["classification"],
        },
        "commands": prior_commands,
        "artifacts": artifacts,
        "blocked_claims": [
            "native GRC9V3 loop formation",
            "native LGRC9V3 execution",
            "movement or locomotion",
            "agency or intention",
            "biological behavior",
            "multi-pole native behavior",
        ],
        "open_future_question": final_decision["next_branch_if_pursued_later"],
    }
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E1.5 LGRC9V3 Alignment Closeout",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "Final decision:",
        "",
        f"`{result['final_decision']['selected_outcome']}`",
        "",
        result["final_decision"]["reason"],
        "",
        "Boundary:",
        "",
        "```text",
        "native_grc9v3_evidence = false",
        "native_lgrc9v3_execution = false",
        "adapter_only = true",
        "movement_claim_allowed = false",
        "```",
        "",
        "## Summary Claims",
        "",
    ]
    for key, value in result["summary_claims"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Validated Evidence", ""])
    for key, value in result["validated_evidence"].items():
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Commands", ""])
    for step, command in result["commands"].items():
        lines.extend([f"### {step}", "", "```bash", command, "```", ""])
    lines.extend(["## Artifacts", ""])
    for step, artifacts in result["artifacts"].items():
        lines.append(f"### {step}")
        lines.append("")
        for artifact in artifacts:
            lines.append(f"- `{artifact}`")
        lines.append("")
    lines.extend(["## Blocked Claims", ""])
    lines.extend(f"- {claim}" for claim in result["blocked_claims"])
    lines.extend(
        [
            "",
            "## Future Question",
            "",
            result["open_future_question"],
            "",
            "E1 does not open that branch. It closes as an adapter-only alignment",
            "record.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    result = _build_result()
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "selected_outcome": result["final_decision"]["selected_outcome"],
                "core_task_requested": result["summary_claims"]["core_task_requested"],
                "native_lgrc9v3_execution": result["claim_boundary"]["native_lgrc9v3_execution"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
