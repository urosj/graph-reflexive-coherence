#!/usr/bin/env python3
"""Build the E1.4 LGRC9V3 compatibility report.

E1.4 classifies the D2.3 packetized pulse mechanism against existing LGRC9V3
surfaces using only E1 artifacts.  It records whether the result is native,
adapter-compatible, blocked by a missing primitive, or not LGRC-aligned.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from loop_observables import load_json, write_json  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
INVENTORY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_surface_inventory.json"
LEDGER_SUMMARY_PATH = EXPERIMENT_ROOT / "outputs" / "e1_d2_3_lgrc_event_ledger_summary.json"
LEDGER_VALIDATION_PATH = EXPERIMENT_ROOT / "outputs" / "e1_ledger_only_validation.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e1_lgrc9v3_compatibility.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e1_lgrc9v3_compatibility.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/build_e1_4_lgrc9v3_compatibility.py"
)


def _classify(
    inventory: Mapping[str, Any],
    ledger_summary: Mapping[str, Any],
    ledger_validation: Mapping[str, Any],
) -> dict[str, Any]:
    findings = inventory["findings"]
    existing_runtime_surfaces_sufficient = all(
        bool(findings[key])
        for key in (
            "packet_departure_records_exist",
            "packet_arrival_records_exist",
            "packet_ledger_with_in_flight_amount_exists",
            "event_time_key_serialized",
            "proper_time_serialized",
            "event_time_key_distinct_from_node_proper_time",
            "budget_reconstructable",
            "route_or_channel_surface_exists",
        )
    )
    ledger_conversion_passed = ledger_summary["status"] == "passed"
    ledger_only_validation_passed = ledger_validation["status"] == "passed"
    state_trigger_native = bool(findings["native_state_trigger_surface_exists"])
    missing_surfaces = list(inventory["missing_surfaces"])

    native_surface_compatible = (
        existing_runtime_surfaces_sufficient
        and ledger_conversion_passed
        and ledger_only_validation_passed
        and state_trigger_native
        and not missing_surfaces
    )
    adapter_compatible = (
        existing_runtime_surfaces_sufficient
        and ledger_conversion_passed
        and ledger_only_validation_passed
        and not native_surface_compatible
    )
    missing_runtime_primitive = (
        not existing_runtime_surfaces_sufficient
        and ledger_conversion_passed
        and ledger_only_validation_passed
    )
    not_lgrc_aligned = not ledger_only_validation_passed

    if native_surface_compatible:
        classification = "native_surface_compatible"
    elif adapter_compatible:
        classification = "adapter_compatible"
    elif missing_runtime_primitive:
        classification = "missing_runtime_primitive"
    else:
        classification = "not_lgrc_aligned"

    return {
        "classification": classification,
        "native_surface_compatible": native_surface_compatible,
        "adapter_compatible": adapter_compatible,
        "missing_runtime_primitive": missing_runtime_primitive,
        "not_lgrc_aligned": not_lgrc_aligned,
        "existing_runtime_surfaces_sufficient": existing_runtime_surfaces_sufficient,
        "ledger_conversion_passed": ledger_conversion_passed,
        "ledger_only_validation_passed": ledger_only_validation_passed,
        "state_trigger_native": state_trigger_native,
    }


def _proposed_surfaces() -> list[dict[str, str]]:
    return [
        {
            "missing_surface": "d2_3_pole_channel_route_manifest",
            "proposed_experiment_surface": "e1_pole_channel_route_manifest",
            "possible_native_surface": "LGRC9V3CausalRouteManifest",
            "reason": (
                "D2.3 route semantics are pole/channel-level. Existing LGRC9V3 "
                "routes are node/edge packet routes."
            ),
        },
        {
            "missing_surface": "source_pole_surplus_trigger_policy",
            "proposed_experiment_surface": "e1_source_pole_surplus_trigger_policy",
            "possible_native_surface": "LGRC9V3StateTriggerPolicy",
            "reason": (
                "D2.3 uses a measured pole surplus threshold to authorize "
                "packet departure. Existing LGRC9V3 has packet producers, but "
                "not this named trigger."
            ),
        },
        {
            "missing_surface": "d2_3_self_rearm_event_kind",
            "proposed_experiment_surface": "e1_self_rearm_evidence",
            "possible_native_surface": "LGRC9V3SelfRearmEvidence",
            "reason": (
                "The runtime can represent arrival and later departure. The "
                "semantic label that returned coherence recreated the trigger "
                "is experiment-level evidence."
            ),
        },
    ]


def _build_result() -> dict[str, Any]:
    inventory = load_json(INVENTORY_PATH)
    ledger_summary = load_json(LEDGER_SUMMARY_PATH)
    ledger_validation = load_json(LEDGER_VALIDATION_PATH)
    classification = _classify(inventory, ledger_summary, ledger_validation)
    core_task = {
        "request_now": False,
        "reason": (
            "E1 can complete as an adapter-only alignment record. A core "
            "LGRC9V3 task should only be requested if a later branch requires "
            "native runtime execution of pole/channel route manifests or "
            "surplus-trigger packet production."
        ),
        "future_core_task_trigger": (
            "Promote only if the next branch asks LGRC9V3.step/run_event_queue "
            "to natively produce the D2.3 event ledger rather than validate an "
            "experiment-local adapter ledger."
        ),
    }
    result = {
        "schema": "n03_e1_lgrc9v3_compatibility_v1",
        "branch": "E1.4",
        "command": COMMAND,
        "status": "complete",
        "classification": classification,
        "claim_boundary": {
            "native_grc9v3_evidence": False,
            "native_lgrc9v3_execution": False,
            "adapter_only": True,
            "movement_claim_allowed": False,
        },
        "source_artifacts": {
            "surface_inventory": str(INVENTORY_PATH.relative_to(EXPERIMENT_ROOT)),
            "ledger_summary": str(LEDGER_SUMMARY_PATH.relative_to(EXPERIMENT_ROOT)),
            "ledger_validation": str(LEDGER_VALIDATION_PATH.relative_to(EXPERIMENT_ROOT)),
        },
        "sufficient_existing_surfaces": inventory["sufficient_surfaces"],
        "missing_or_adapter_surfaces": inventory["missing_surfaces"],
        "proposed_surface_names": _proposed_surfaces(),
        "ledger_validation_summary": {
            "validated_lane_count": ledger_validation["validated_lane_count"],
            "ledger_positive_lanes": ledger_validation["ledger_positive_lanes"],
            "checks": ledger_validation["checks"],
            "symmetry_passed": ledger_validation["symmetry_audit"]["passed"],
        },
        "core_task_recommendation": core_task,
        "interpretation": (
            "D2.3 is LGRC-aligned and adapter-compatible. The packet mechanism "
            "can be represented as LGRC-style causal packet history and validated "
            "from that ledger alone. It is not yet native LGRC9V3 runtime "
            "execution because pole/channel route semantics, surplus-trigger "
            "policy, and self-rearm evidence remain experiment-local adapter "
            "surfaces."
        ),
    }
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    classification = result["classification"]
    lines = [
        "# E1.4 LGRC9V3 Compatibility Report",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{classification['classification']}`",
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
        "## Outcome Matrix",
        "",
        "| Outcome | Value |",
        "| --- | --- |",
        f"| `native_surface_compatible` | `{classification['native_surface_compatible']}` |",
        f"| `adapter_compatible` | `{classification['adapter_compatible']}` |",
        f"| `missing_runtime_primitive` | `{classification['missing_runtime_primitive']}` |",
        f"| `not_lgrc_aligned` | `{classification['not_lgrc_aligned']}` |",
        "",
        "## Interpretation",
        "",
        result["interpretation"],
        "",
        "## Sufficient Existing Surfaces",
        "",
    ]
    lines.extend(f"- `{surface}`" for surface in result["sufficient_existing_surfaces"])
    lines.extend(["", "## Missing Or Adapter-Only Surfaces", ""])
    for surface in result["missing_or_adapter_surfaces"]:
        lines.extend(
            [
                f"- `{surface['surface']}`: `{surface['status']}`",
                f"  {surface['reason']}",
            ]
        )
    lines.extend(["", "## Proposed Surface Names", ""])
    for surface in result["proposed_surface_names"]:
        lines.extend(
            [
                f"- `{surface['missing_surface']}`",
                f"  - experiment: `{surface['proposed_experiment_surface']}`",
                f"  - possible native: `{surface['possible_native_surface']}`",
                f"  - reason: {surface['reason']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Core Task Recommendation",
            "",
            f"Request core task now: `{result['core_task_recommendation']['request_now']}`",
            "",
            result["core_task_recommendation"]["reason"],
            "",
            "Future trigger:",
            "",
            result["core_task_recommendation"]["future_core_task_trigger"],
            "",
            "## Ledger Validation Summary",
            "",
            f"- validated lanes: `{result['ledger_validation_summary']['validated_lane_count']}`",
            f"- ledger-positive lanes: `{', '.join(result['ledger_validation_summary']['ledger_positive_lanes'])}`",
            f"- direction symmetry passed: `{result['ledger_validation_summary']['symmetry_passed']}`",
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
                "classification": result["classification"]["classification"],
                "request_core_task_now": result["core_task_recommendation"]["request_now"],
                "adapter_only": result["claim_boundary"]["adapter_only"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
