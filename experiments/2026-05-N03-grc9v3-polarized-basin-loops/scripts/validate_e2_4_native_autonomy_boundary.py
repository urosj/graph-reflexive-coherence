#!/usr/bin/env python3
"""Validate E2.4 native autonomy claim boundary.

E2.4 found that native LGRC9V3 static route autonomy exists, but D2.3's
pole-surplus trigger and self-rearm semantics are still not native.  This
hardening check records that distinction before E2.5 closeout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from loop_observables import load_json, write_json


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
INPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_4_native_autonomy_feasibility.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "e2_4a_native_autonomy_boundary.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "e2_4a_native_autonomy_boundary.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/validate_e2_4_native_autonomy_boundary.py"
)


def _write_report(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E2.4-A Native Autonomy Boundary Validation",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Required Boundary",
        "",
    ]
    for key, value in result["required_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Interpretation", "", result["interpretation"], ""])
    if result["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    source = load_json(INPUT_PATH)
    audit = source["d2_3_equivalence_audit"]
    probe = source["native_static_route_probe"]
    required_boundary = {
        "native_static_route_autonomy_exists": probe["status"] == "passed",
        "native_packet_route_production_exists": bool(
            audit["native_packet_route_production_exists"]
        ),
        "native_arrival_triggered_route_forwarding_exists": bool(
            audit["native_arrival_triggered_route_forwarding_exists"]
        ),
        "native_pole_mask_route_semantics_exists": bool(
            audit["native_pole_mask_route_semantics_exists"]
        ),
        "native_source_pole_surplus_threshold_trigger_exists": bool(
            audit["native_source_pole_surplus_threshold_trigger_exists"]
        ),
        "native_d2_3_self_rearm_label_exists": bool(
            audit["native_d2_3_self_rearm_label_exists"]
        ),
        "native_d2_3_equivalent": bool(audit["native_d2_3_equivalent"]),
        "adapter_required_for_d2_3_semantics": bool(
            audit["adapter_required_for_d2_3_semantics"]
        ),
        "core_task_requested": bool(source["claim_boundary"]["core_task_requested"]),
    }
    errors: list[str] = []
    expected = {
        "native_static_route_autonomy_exists": True,
        "native_packet_route_production_exists": True,
        "native_arrival_triggered_route_forwarding_exists": True,
        "native_pole_mask_route_semantics_exists": False,
        "native_source_pole_surplus_threshold_trigger_exists": False,
        "native_d2_3_self_rearm_label_exists": False,
        "native_d2_3_equivalent": False,
        "adapter_required_for_d2_3_semantics": True,
        "core_task_requested": False,
    }
    for key, expected_value in expected.items():
        if required_boundary[key] is not expected_value:
            errors.append(
                f"{key}={required_boundary[key]!r}, expected {expected_value!r}"
            )
    result = {
        "schema": "n03_e2_4a_native_autonomy_boundary_v1",
        "branch": "E2.4-A",
        "command": COMMAND,
        "source_artifact": str(INPUT_PATH.relative_to(EXPERIMENT_ROOT)),
        "status": "passed" if not errors else "failed",
        "required_boundary": required_boundary,
        "errors": errors,
        "interpretation": (
            "E2.4-A preserves the distinction between native static route "
            "autonomy and D2.3-equivalent autonomy. Existing LGRC9V3 can "
            "natively produce route-table packet work and arrival-triggered "
            "forwarding, but D2.3 pole-mask routing, surplus-threshold trigger, "
            "and self-rearm semantics still require experiment-local adapter "
            "evidence. No core task is requested by this experiment closeout."
        ),
    }
    write_json(OUTPUT_PATH, result)
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "native_static_route_autonomy_exists": required_boundary[
                    "native_static_route_autonomy_exists"
                ],
                "native_d2_3_equivalent": required_boundary["native_d2_3_equivalent"],
                "adapter_required_for_d2_3_semantics": required_boundary[
                    "adapter_required_for_d2_3_semantics"
                ],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
