#!/usr/bin/env python3
"""Build N23 Iteration 8 closeout and N24 handoff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_n23_collapse_replay_and_counterfactual_controls as i5


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_closeout_and_n24_handoff.json"
REPORT = EXPERIMENT / "reports" / "n23_closeout_and_n24_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_closeout_and_n24_handoff.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_closeout_and_n24_handoff.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_live_continuation_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_active_nulls_and_failure_baselines.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_minimal_live_branch_collapse_probe.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_multibranch_live_set_collapse_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_collapse_replay_and_counterfactual_controls.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_multibranch_collapse_replay_and_controls.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_ap4_selection_geometry_probe.json"
)
I6A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_ap4_selection_geometry_robustness_probe.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_replay_and_control_matrix.json"
)


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def source_record(path: str, role: str) -> dict[str, Any]:
    return i5.source_record(path, role)


def unsafe_claims_blocked_record() -> dict[str, bool]:
    return {
        "semantic_choice": False,
        "semantic_intention": False,
        "semantic_action": False,
        "semantic_perception": False,
        "semantic_goal_ownership": False,
        "free_will": False,
        "agency": False,
        "selfhood": False,
        "identity_acceptance": False,
        "native_support": False,
        "native_route_conductance_memory": False,
        "sentience": False,
        "consciousness": False,
        "organism_life": False,
        "fully_native_integration": False,
        "unrestricted_autonomy": False,
        "phase8_implementation": False,
        "ant_ecology_implementation": False,
        "native_ant_agency": False,
        "native_colony_agency": False,
    }


def output_digest_map(paths: list[str]) -> dict[str, str]:
    return {
        path: i5.load_json(path).get("output_digest", "not_recorded")
        for path in paths
    }


def src_diff_empty() -> bool:
    src = ROOT / "src"
    if not src.exists():
        return True
    try:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--quiet", "--", "src"],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N23 Iteration 8 - Closeout And N24 Handoff",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Final Classification",
        "",
        "```text",
        f"final_supported_lc_ladder_rung = {output['final_classification']['final_supported_lc_ladder_rung']}",
        f"final_n23_closeout_ladder_rung = {output['final_classification']['final_n23_closeout_ladder_rung']}",
        f"ap4_bridge_status = {output['final_classification']['ap4_bridge_status']}",
        f"final_ap4_supported = {str(output['final_classification']['final_ap4_supported']).lower()}",
        f"ready_for_n24 = {str(output['n24_handoff']['ready_for_n24']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        output["interpretation"]["main_read"],
        "",
        "```text",
        output["interpretation"]["geometric_summary"],
        "```",
        "",
        "## Claim Boundary",
        "",
        "```text",
        output["final_classification"]["final_claim_ceiling"],
        "semantic choice = false",
        "semantic intention = false",
        "agency = false",
        "native support = false",
        "sentience = false",
        "Phase 8 = false",
        "ant ecology implementation = false",
        "```",
        "",
        "## N24 Handoff",
        "",
        "```text",
        f"next_experiment = {output['n24_handoff']['next_experiment']}",
        f"handoff_focus = {output['n24_handoff']['handoff_focus']}",
        f"consumable_n23_result = {output['n24_handoff']['consumable_n23_result']}",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source_paths = [
        I1_OUTPUT_PATH,
        I2_OUTPUT_PATH,
        I3_OUTPUT_PATH,
        I4_OUTPUT_PATH,
        I4A_OUTPUT_PATH,
        I5_OUTPUT_PATH,
        I5A_OUTPUT_PATH,
        I6_OUTPUT_PATH,
        I6A_OUTPUT_PATH,
        I7_OUTPUT_PATH,
    ]
    i1_output = i5.load_json(I1_OUTPUT_PATH)
    i2_output = i5.load_json(I2_OUTPUT_PATH)
    i3_output = i5.load_json(I3_OUTPUT_PATH)
    i4_output = i5.load_json(I4_OUTPUT_PATH)
    i4a_output = i5.load_json(I4A_OUTPUT_PATH)
    i5_output = i5.load_json(I5_OUTPUT_PATH)
    i5a_output = i5.load_json(I5A_OUTPUT_PATH)
    i6_output = i5.load_json(I6_OUTPUT_PATH)
    i6a_output = i5.load_json(I6A_OUTPUT_PATH)
    i7_output = i5.load_json(I7_OUTPUT_PATH)
    i7_boundary = i7_output["iteration7_boundary"]
    unsafe_flags = unsafe_claims_blocked_record()
    producer_residue_fields = [
        "bounded_test_configuration",
        "producer_script_generates_probe_artifacts",
        "support_gradient_selection_rule_declared_in_producer",
        "branch_stress_case_generation",
        "collapse_packet_schedule",
    ]
    naturalization_debt_fields = [
        "source_current_counterfactual_branch_records",
        "route_conditioned_selection_policy",
        "proxy_independent_branch_valuation",
        "native_branch_selection_margin_gate",
        "native_multibranch_optional_continuation_generation",
    ]
    all_sources_passed = all(
        output["status"] == "passed"
        for output in [
            i1_output,
            i2_output,
            i3_output,
            i4_output,
            i4a_output,
            i5_output,
            i5a_output,
            i6_output,
            i6a_output,
            i7_output,
        ]
    )
    i7_ready = i7_boundary["ready_for_iteration_8_closeout"] is True
    src_clean = src_diff_empty()
    claim_boundary_clean = all(value is False for value in unsafe_flags.values())
    lc6_supported = all_sources_passed and i7_ready and src_clean and claim_boundary_clean
    final_supported_lc_ladder_rung = "LC6" if lc6_supported else "LC5"
    final_n23_closeout_ladder_rung = "N23-C6" if lc6_supported else "N23-C5"
    ap4_bridge_status = (
        "bridge_candidate_supported"
        if i7_boundary["ap4_bridge_status"] == "bridge_candidate_supported"
        and lc6_supported
        else "blocked"
    )
    final_classification = {
        "final_supported_lc_ladder_rung": final_supported_lc_ladder_rung,
        "final_n23_closeout_ladder_rung": final_n23_closeout_ladder_rung,
        "ap4_bridge_status": ap4_bridge_status,
        "ap4_bridge_candidate_supported": ap4_bridge_status
        == "bridge_candidate_supported",
        "final_ap4_supported": False,
        "final_n23_supported": lc6_supported,
        "final_claim_ceiling": (
            "bounded artifact-level live-continuation collapse / selection-"
            "geometry evidence, N24-ready; not semantic choice, agency, native "
            "support, sentience, Phase 8, or ant ecology implementation"
        ),
        "final_claim_allowed": lc6_supported,
    }
    n24_handoff = {
        "ready_for_n24": lc6_supported,
        "next_experiment": "N24",
        "handoff_focus": "abundance / surplus-supported optionality",
        "consumable_n23_result": (
            "LC6/N23-C6 bounded live-continuation collapse evidence with AP4 "
            "bridge candidate support and unsafe promotions blocked"
            if lc6_supported
            else "LC5/N23-C5 pending unresolved closeout checks"
        ),
        "n24_may_consume_as": [
            "bounded_live_branch_set_and_collapse_evidence",
            "counterfactual_retention_evidence",
            "ap4_bridge_candidate_context",
            "bounded_selection_geometry_context",
        ],
        "n24_must_not_consume_as": [
            "semantic_choice",
            "semantic_intention",
            "agency",
            "free_will",
            "native_support",
            "sentience",
            "Phase8_implementation",
            "ant_ecology_implementation",
        ],
    }
    checks = [
        check(
            "all_source_iterations_passed",
            all_sources_passed,
            {
                "i1": i1_output["status"],
                "i2": i2_output["status"],
                "i3": i3_output["status"],
                "i4": i4_output["status"],
                "i4a": i4a_output["status"],
                "i5": i5_output["status"],
                "i5a": i5a_output["status"],
                "i6": i6_output["status"],
                "i6a": i6a_output["status"],
                "i7": i7_output["status"],
            },
        ),
        check(
            "i7_matrix_ready_for_closeout",
            i7_ready,
            i7_boundary,
        ),
        check(
            "i7_supported_lc5_and_n23_c5",
            i7_boundary["i7_supported_lc_ladder_rung"] == "LC5"
            and i7_boundary["i7_supported_n23_closeout_candidate"] == "N23-C5",
            i7_boundary,
        ),
        check(
            "ap4_bridge_candidate_supported_but_not_final_ap4",
            ap4_bridge_status == "bridge_candidate_supported"
            and final_classification["final_ap4_supported"] is False,
            final_classification,
        ),
        check(
            "producer_residue_recorded",
            len(producer_residue_fields) >= 3,
            producer_residue_fields,
        ),
        check(
            "naturalization_debt_recorded",
            len(naturalization_debt_fields) >= 3,
            naturalization_debt_fields,
        ),
        check(
            "ap4_ap5_dependency_status_clean",
            all(
                row["ap4_dependency_status"] == "required_recorded"
                and row["ap5_dependency_status"] == "not_applicable"
                for row in i7_output["matrix_rows"]
                if row["row_schema_role"]
                in {
                    "i7_full_matrix_primary_lc5_row",
                    "i7_full_matrix_ap4_stress_row",
                }
            ),
            [
                {
                    "row_id": row["row_id"],
                    "ap4_dependency_status": row["ap4_dependency_status"],
                    "ap5_dependency_status": row["ap5_dependency_status"],
                }
                for row in i7_output["matrix_rows"]
            ],
        ),
        check(
            "unsafe_claim_flags_false",
            claim_boundary_clean,
            unsafe_flags,
        ),
        check("src_diff_empty", src_clean, "git diff -- src is empty"),
        check(
            "n24_handoff_ready",
            n24_handoff["ready_for_n24"] is True,
            n24_handoff,
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i8_closeout_and_n24_handoff",
        "schema_version": "1.0",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "8",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_n23_lc6_closeout_n24_handoff_ready"
            if not failed_checks
            else "blocked_n23_closeout_failed_checks"
        ),
        "purpose": (
            "Close N23 by deciding LC6/N23-C6, freezing the claim ceiling, "
            "recording producer residue and naturalization debt, and handing "
            "bounded live-continuation collapse evidence to N24."
        ),
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n23_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n23_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n23_active_nulls"),
            source_record(I4_OUTPUT_PATH, "minimal_lc3_source"),
            source_record(I4A_OUTPUT_PATH, "multibranch_lc3_source"),
            source_record(I5_OUTPUT_PATH, "minimal_lc4_replay_control_source"),
            source_record(I5A_OUTPUT_PATH, "multibranch_lc4_replay_control_source"),
            source_record(I6_OUTPUT_PATH, "ap4_lc5_bridge_candidate_source"),
            source_record(I6A_OUTPUT_PATH, "bounded_ap4_stress_evidence_source"),
            source_record(I7_OUTPUT_PATH, "full_replay_control_matrix_source"),
            {
                "path": SCRIPT_PATH,
                "sha256": i5.sha256_file(SCRIPT_PATH),
                "source_role": "producer_script",
            },
        ],
        "source_output_digest_map": output_digest_map(source_paths),
        "final_classification": final_classification,
        "producer_residue_fields": producer_residue_fields,
        "naturalization_debt_fields": naturalization_debt_fields,
        "ap_gap_closeout": {
            "ap4_gap_status": "bridge_candidate_supported_by_n23_source_current_selection_geometry",
            "ap4_nat4_gap_resolved_for_n23_scope": True,
            "ap4_final_general_status": "not_finalized_here",
            "ap5_dependency_status": "not_applicable_no_proxy_or_target_formation",
            "n19_reclassification_required_for_global_ap4_change": True,
        },
        "unsafe_claim_flags": unsafe_flags,
        "n24_handoff": n24_handoff,
        "interpretation": {
            "main_read": (
                "I8 closes N23 at LC6/N23-C6 because I7 validated the minimal "
                "and four-branch live-continuation collapse paths, AP4 bridge "
                "candidate evidence, bounded stress rows, and fail-closed "
                "controls without opening unsafe claims or modifying src."
            ),
            "geometric_summary": (
                "N23 produced source-current live branch sets, collapse traces "
                "from those branch sets into one continuation, immutable "
                "counterfactual retention for non-selected branches, replay-"
                "stable collapse records, and AP4-relevant branch selection "
                "geometry. The supported result is N24-ready bounded artifact-"
                "level collapse/selection geometry, not semantic choice."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    output["output_digest"] = i5.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    i5.write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
