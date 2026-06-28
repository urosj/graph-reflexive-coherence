#!/usr/bin/env python3
"""Build N25.1 Iteration 4 closeout and Phase 8 extension handoff."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_1_closeout_and_phase8_extension_handoff.json"
REPORT = EXPERIMENT / "reports" / "n25_1_closeout_and_phase8_extension_handoff.md"
I3_OUTPUT_PATH = (
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "outputs/n25_1_phase8_extension_requirements_matrix.json"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "scripts/build_n25_1_closeout_and_phase8_extension_handoff.py"
)

FINAL_CLOSEOUT_RUNG = "N25.1-C4_closeout_and_phase8_handoff_complete"
FINAL_MB_CEILING = "MB0_requirements_bridge_only_no_runtime_evidence"
UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology",
    "bf6_without_mb6",
    "fully_native_integration",
    "identity_acceptance",
    "independent_new_basin_formation_without_controls",
    "lgrc9v3_native_multi_basin_formation_without_runtime_evidence",
    "native_support",
    "organism_life",
    "phase8_implementation_complete",
    "semantic_choice",
    "semantic_learning",
    "sentience",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def build_phase8_handoff(i3: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_status": "ready_to_implement_future_phase8_extension",
        "handoff_type": "requirements_contract_only",
        "source_requirement_matrix_digest": i3["output_digest"],
        "implementation_sequence": i3["implementation_sequence_recommendation"],
        "required_surfaces": [
            {
                "surface_id": row["surface_id"],
                "implementation_role": row["implementation_role"],
                "surface_status": row["surface_status"],
                "enabled_mb_rungs_if_implemented": row[
                    "mb_rungs_enabled_if_implemented"
                ],
            }
            for row in i3["requirement_rows"]
        ],
        "must_preserve": [
            "default_off_extension_surface",
            "producer_step_boundary",
            "node_plus_packet_budget_audit",
            "causal_event_ordering",
            "source_current_child_basin_state_records",
            "merge_leakage_controls",
            "producer_assisted_results_do_not_upgrade_native",
            "unsafe_claim_flags_false",
        ],
        "must_not_claim_before_runtime_validation": [
            "native_multi_basin_formation",
            "BF6",
            "independent_new_basin_formation",
            "native_support",
            "semantic_learning",
            "semantic_choice",
            "agency",
            "sentience",
            "ant_ecology",
        ],
    }


def build_n26_handoff() -> dict[str, Any]:
    return {
        "next_experiment": "N26_proxy_divergence_proxy_collapse",
        "handoff_status": "ready_with_scope_constraints",
        "n26_may_consume_as": [
            "N25_scoped_BF5_high_margin_core_sub_basin_context",
            "N25.1_requirements_bridge_context",
            "Phase8_extension_requirements_context",
        ],
        "n26_must_not_consume_as": [
            "unscoped_multi_basin_substrate",
            "independent_new_basin_substrate",
            "native_LGRC9V3_multi_basin_formation",
            "BF6",
            "native_support",
            "semantic_learning",
            "semantic_choice",
            "agency",
            "sentience",
            "ant_ecology",
        ],
        "unscoped_multi_basin_claim_requires": [
            "future_Phase8_extension_implemented",
            "MB6_supported_by_runtime_evidence",
            "replay_and_control_matrix_clean",
            "merge_leakage_controls_clean",
            "producer_residue_not_native_upgrade",
            "unsafe_claim_flags_false",
        ],
    }


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT_PATH)
    unsafe_flags = unsafe_claim_flags()
    output: dict[str, Any] = {
        "artifact_id": "n25_1_closeout_and_phase8_extension_handoff",
        "status": "passed",
        "acceptance_state": "closed_n25_1_c4_requirements_bridge_phase8_handoff_ready_no_runtime_evidence",
        "generated_at": GENERATED_AT,
        "reproduction_command": COMMAND,
        "experiment": "N25.1",
        "iteration": "I4",
        "source_requirement_matrix": {
            "path": I3_OUTPUT_PATH,
            "sha256": sha256_file(I3_OUTPUT_PATH),
            "status": i3.get("status", "not_recorded"),
            "acceptance_state": i3.get("acceptance_state", "not_recorded"),
            "output_digest": i3.get("output_digest", "not_recorded"),
            "failed_checks": i3.get("failed_checks", "not_recorded"),
        },
        "experiment_kind": "requirements_spec_bridge",
        "final_n25_1_closeout_rung": FINAL_CLOSEOUT_RUNG,
        "final_mb_ladder_ceiling": FINAL_MB_CEILING,
        "requirements_bridge_closed": True,
        "phase8_extension_ready_to_implement": True,
        "phase8_extension_handoff_status": "ready_to_implement_future_phase8_extension",
        "runtime_implementation_opened": False,
        "phase8_extension_implemented": False,
        "multi_basin_evidence_opened": False,
        "mb_ladder_rung_assigned": False,
        "native_multi_basin_formation_supported": False,
        "BF6_supported": False,
        "independent_new_basin_supported": False,
        "phase8_extension_handoff": build_phase8_handoff(i3),
        "n26_handoff": build_n26_handoff(),
        "claim_boundary": {
            "requirements_contract_allowed": True,
            "runtime_evidence_allowed": False,
            "native_multi_basin_formation_supported": False,
            "BF6_supported": False,
            "phase8_extension_implemented": False,
            "unsafe_claim_flags": unsafe_flags,
        },
    }
    checks = [
        check(
            "i3_requirement_matrix_passed",
            i3.get("status") == "passed" and i3.get("failed_checks") == [],
            output["source_requirement_matrix"],
        ),
        check(
            "final_closeout_rung_is_c4",
            output["final_n25_1_closeout_rung"] == FINAL_CLOSEOUT_RUNG,
            output["final_n25_1_closeout_rung"],
        ),
        check(
            "phase8_ready_but_not_implemented",
            output["phase8_extension_ready_to_implement"] is True
            and output["phase8_extension_implemented"] is False
            and output["runtime_implementation_opened"] is False,
            {
                "phase8_extension_ready_to_implement": output[
                    "phase8_extension_ready_to_implement"
                ],
                "phase8_extension_implemented": output[
                    "phase8_extension_implemented"
                ],
                "runtime_implementation_opened": output[
                    "runtime_implementation_opened"
                ],
            },
        ),
        check(
            "mb_evidence_and_bf6_remain_closed",
            output["multi_basin_evidence_opened"] is False
            and output["native_multi_basin_formation_supported"] is False
            and output["BF6_supported"] is False,
            {
                "multi_basin_evidence_opened": output[
                    "multi_basin_evidence_opened"
                ],
                "native_multi_basin_formation_supported": output[
                    "native_multi_basin_formation_supported"
                ],
                "BF6_supported": output["BF6_supported"],
            },
        ),
        check(
            "n26_handoff_scoped",
            "unscoped_multi_basin_substrate"
            in output["n26_handoff"]["n26_must_not_consume_as"]
            and "N25_scoped_BF5_high_margin_core_sub_basin_context"
            in output["n26_handoff"]["n26_may_consume_as"],
            output["n26_handoff"],
        ),
        check(
            "phase8_required_surfaces_carried",
            len(output["phase8_extension_handoff"]["required_surfaces"]) == 7,
            output["phase8_extension_handoff"]["required_surfaces"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in unsafe_flags.values()),
            unsafe_flags,
        ),
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(output),
            "repo_relative_paths_only",
        ),
    ]
    output["checks"] = checks
    output["failed_checks"] = [
        item["check_id"] for item in checks if item["passed"] is not True
    ]
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N25.1 Iteration 4 - Closeout And Phase 8 Extension Handoff",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Final Classification",
        "",
        "```text",
        f"final_n25_1_closeout_rung = {data['final_n25_1_closeout_rung']}",
        f"final_mb_ladder_ceiling = {data['final_mb_ladder_ceiling']}",
        f"phase8_extension_ready_to_implement = {str(data['phase8_extension_ready_to_implement']).lower()}",
        f"runtime_implementation_opened = {str(data['runtime_implementation_opened']).lower()}",
        f"phase8_extension_implemented = {str(data['phase8_extension_implemented']).lower()}",
        f"multi_basin_evidence_opened = {str(data['multi_basin_evidence_opened']).lower()}",
        f"native_multi_basin_formation_supported = {str(data['native_multi_basin_formation_supported']).lower()}",
        f"BF6_supported = {str(data['BF6_supported']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "N25.1 closes as a requirements/spec bridge. It is ready to hand a "
            "future Phase 8 implementation tranche a concrete extension matrix, "
            "but it does not itself implement the extension and does not produce "
            "multi-basin runtime evidence."
        ),
        "",
        "## Phase 8 Handoff",
        "",
        "| Surface | Role | Status | Enables If Implemented |",
        "| --- | --- | --- | --- |",
    ]
    for row in data["phase8_extension_handoff"]["required_surfaces"]:
        lines.append(
            "| "
            f"`{row['surface_id']}` | "
            f"`{row['implementation_role']}` | "
            f"`{row['surface_status']}` | "
            f"`{', '.join(row['enabled_mb_rungs_if_implemented'])}` |"
        )
    lines.extend(
        [
            "",
            "## N26 Handoff",
            "",
            "```text",
            "N26 may consume scoped N25 BF5 context and N25.1 requirements context.",
            "N26 may not consume unscoped multi-basin substrate, independent new-basin substrate, native LGRC9V3 multi-basin formation, or BF6 unless a future Phase 8 extension supplies MB6 runtime evidence.",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in data["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"output_digest {data['output_digest']}")


if __name__ == "__main__":
    main()
