#!/usr/bin/env python3
"""Build E2.5 LGRC9V3 runtime compatibility closeout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from loop_observables import load_json, write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_lgrc9v3_runtime_closeout.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_lgrc9v3_runtime_closeout.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/build_e2_5_runtime_closeout.py"
)

ARTIFACTS = {
    "e2_0": EXPERIMENT_ROOT / "outputs" / "e2_0_runtime_feasibility.json",
    "e2_1": EXPERIMENT_ROOT / "outputs" / "e2_1_scheduled_packet_route_replay.json",
    "e2_2": EXPERIMENT_ROOT / "outputs" / "e2_2_runtime_ledger_extraction.json",
    "e2_3": EXPERIMENT_ROOT / "outputs" / "e2_3_adapter_triggered_runtime_loop.json",
    "e2_3a": EXPERIMENT_ROOT / "outputs" / "e2_3a_adapter_triggered_runtime_loop_hardening.json",
    "e2_4": EXPERIMENT_ROOT / "outputs" / "e2_4_native_autonomy_feasibility.json",
    "e2_4a": EXPERIMENT_ROOT / "outputs" / "e2_4a_native_autonomy_boundary.json",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(EXPERIMENT_ROOT))


def _status(name: str, artifact: Mapping[str, Any]) -> str:
    return str(artifact.get("status", "unknown"))


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.5 LGRC9V3 Runtime Compatibility Closeout",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "Selected classifications:",
        "",
    ]
    lines.extend(f"- `{item}`" for item in result["selected_classifications"])
    lines.extend(
        [
            "",
            "Boundary:",
            "",
            "```text",
            "native_grc9v3_evidence = false",
            "native_lgrc9v3_execution = true",
            "native_packet_execution = true",
            "native_static_route_autonomy = true",
            "adapter_triggered_runtime_compatible = true",
            "native_d2_3_equivalent_autonomy = false",
            "core_task_requested = false",
            "movement_claim_allowed = false",
            "```",
            "",
            "## Evidence Chain",
            "",
            "| Branch | Status | Classification / result | Artifact |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in result["evidence_chain"]:
        lines.append(
            f"| {row['branch']} | {row['status']} | {row['classification']} | `{row['artifact']}` |"
        )
    lines.extend(["", "## Final Conclusions", ""])
    lines.extend(f"- {item}" for item in result["final_conclusions"])
    lines.extend(["", "## Next Decision", "", result["next_branch_decision"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    artifacts = {name: load_json(path) for name, path in ARTIFACTS.items()}
    statuses = {name: _status(name, artifact) for name, artifact in artifacts.items()}
    required_passed = all(status == "passed" for status in statuses.values())
    e2_3 = artifacts["e2_3"]
    e2_4a = artifacts["e2_4a"]
    native_packet_execution = bool(
        artifacts["e2_1"]["claim_ceiling"]["native_packet_execution"]
    )
    adapter_triggered_runtime = bool(
        e2_3["claim_ceiling"]["adapter_driven_runtime_execution"]
    )
    native_static_route_autonomy = bool(
        e2_4a["required_boundary"]["native_static_route_autonomy_exists"]
    )
    native_d2_3_equivalent = bool(e2_4a["required_boundary"]["native_d2_3_equivalent"])
    adapter_required = bool(
        e2_4a["required_boundary"]["adapter_required_for_d2_3_semantics"]
    )
    core_task_requested = False
    selected_classifications = [
        "native_packet_execution_compatible",
        "adapter_triggered_runtime_compatible",
    ]
    if native_static_route_autonomy:
        selected_classifications.append("native_static_route_autonomy_available")
    if adapter_required and not native_d2_3_equivalent:
        selected_classifications.append("missing_native_surplus_trigger_primitive")
    errors: list[str] = []
    if not required_passed:
        errors.append(f"not all prerequisite artifacts passed: {statuses}")
    if not native_packet_execution:
        errors.append("native packet execution was not established")
    if not adapter_triggered_runtime:
        errors.append("adapter-triggered runtime compatibility was not established")
    if native_d2_3_equivalent:
        errors.append("native D2.3 equivalence unexpectedly true")
    evidence_chain = [
        {
            "branch": "E2.0",
            "status": statuses["e2_0"],
            "classification": "single scheduled packet feasibility",
            "artifact": _rel(ARTIFACTS["e2_0"]),
        },
        {
            "branch": "E2.1",
            "status": statuses["e2_1"],
            "classification": "scheduled native packet route replay",
            "artifact": _rel(ARTIFACTS["e2_1"]),
        },
        {
            "branch": "E2.2",
            "status": statuses["e2_2"],
            "classification": "runtime ledger extraction and ledger-only validation",
            "artifact": _rel(ARTIFACTS["e2_2"]),
        },
        {
            "branch": "E2.3",
            "status": statuses["e2_3"],
            "classification": e2_3["classification"],
            "artifact": _rel(ARTIFACTS["e2_3"]),
        },
        {
            "branch": "E2.3-A",
            "status": statuses["e2_3a"],
            "classification": "adapter-triggered runtime hardening passed",
            "artifact": _rel(ARTIFACTS["e2_3a"]),
        },
        {
            "branch": "E2.4",
            "status": statuses["e2_4"],
            "classification": artifacts["e2_4"]["classification"],
            "artifact": _rel(ARTIFACTS["e2_4"]),
        },
        {
            "branch": "E2.4-A",
            "status": statuses["e2_4a"],
            "classification": "native autonomy boundary validation passed",
            "artifact": _rel(ARTIFACTS["e2_4a"]),
        },
    ]
    final_conclusions = [
        "Existing LGRC9V3 can execute scheduled packet departure/arrival events.",
        "Existing LGRC9V3 can replay the declared D2.3 packet route when packets are scheduled.",
        "E2.3 demonstrates a D2.3-aligned adapter-triggered runtime loop with controls preserved.",
        "E2.2 extracts replayable E1-compatible ledgers from E2.3 runtime evidence.",
        "Existing LGRC9V3 native static-route autonomy exists through causal flux routes and autonomous producers.",
        "Existing native autonomy is not D2.3-equivalent because pole-mask route semantics, source-pole surplus threshold trigger, and D2.3 self-rearm labels remain adapter-derived.",
        "No movement, locomotion, agency, biological, or native GRC9V3 loop claim is made.",
        "No `src/*` change or core task is requested by this experiment closeout.",
    ]
    result = {
        "schema": "n03_e2_5_lgrc9v3_runtime_closeout_v1",
        "branch": "E2.5",
        "command": COMMAND,
        "status": "passed" if not errors else "failed",
        "selected_classifications": selected_classifications,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": True,
            "native_packet_execution": native_packet_execution,
            "native_static_route_autonomy": native_static_route_autonomy,
            "adapter_triggered_runtime_compatible": adapter_triggered_runtime,
            "native_d2_3_equivalent_autonomy": native_d2_3_equivalent,
            "adapter_required_for_d2_3_semantics": adapter_required,
            "core_task_requested": core_task_requested,
            "movement_claim_allowed": False,
        },
        "evidence_chain": evidence_chain,
        "final_conclusions": final_conclusions,
        "next_branch_decision": (
            "Close E2. Future work may either publish N03 with this bounded "
            "runtime classification, or open a separate core-design task for a "
            "native pole-surplus trigger primitive. That core task is not "
            "requested by this experiment closeout."
        ),
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "selected_classifications": selected_classifications,
                "core_task_requested": core_task_requested,
                "native_d2_3_equivalent_autonomy": native_d2_3_equivalent,
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
