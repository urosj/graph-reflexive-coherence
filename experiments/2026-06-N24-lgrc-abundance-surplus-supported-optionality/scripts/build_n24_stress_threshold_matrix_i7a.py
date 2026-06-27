#!/usr/bin/env python3
"""Build N24 Iteration 7-A stress matrix for the I5-A/I6-A variant."""

from __future__ import annotations

from typing import Any

import build_n24_minimal_surplus_probe as base
import build_n24_stress_threshold_matrix as i7


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_stress_threshold_matrix_i7a.json"
REPORT = EXPERIMENT / "reports" / "n24_stress_threshold_matrix_i7a.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_stress_threshold_matrix_i7a_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_stress_threshold_matrix_i7a.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_stress_threshold_matrix_i7a.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i7.I4_OUTPUT_PATH
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe_i5a.json"
)
I6A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix_i6a.json"
)
I7_OUTPUT_PATH = i7.I7_OUTPUT_PATH if hasattr(i7, "I7_OUTPUT_PATH") else (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

BRANCH_STRESS_COSTS_I7A = [0.0, 0.1, 0.2, 0.3, 0.38, 0.4, 0.5, 0.576, 0.6]
MAINTENANCE_DRAIN_STRESS_I7A = [0.0, 0.1, 0.5, 1.0, 1.05, 1.15, 1.151]


def write_artifact(name: str, data: dict[str, Any]) -> str:
    path = ARTIFACT_DIR / name
    base.write_json(path, data)
    return base.rel(path)


def artifact_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": base.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def unsafe_claim_flags(i2: dict[str, Any]) -> dict[str, bool]:
    return {
        claim: False
        for claim in sorted(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
    }


def no_absolute_paths(data: Any) -> bool:
    text = base.canonical_json(data)
    forbidden = [
        "/" + "home/",
        "/" + "tmp/",
        "file" + "://",
        "C" + ":\\",
        "/" + "Users/",
    ]
    return all(token not in text for token in forbidden)


def maintenance_floor_boundary_trace_i7a(i5a_row: dict[str, Any]) -> dict[str, Any]:
    base_support = i5a_row["support_floor_result"]["observed_support"]
    base_coherence = i5a_row["coherence_floor_result"]["observed_coherence"]
    floors = [9.85, 10.0, 10.5, 11.0, 11.001]
    rows = []
    for floor in floors:
        support_margin = base_support - floor
        coherence_margin = base_coherence - floor
        rows.append(
            {
                "candidate_floor": floor,
                "support_margin": support_margin,
                "coherence_margin": coherence_margin,
                "floor_preserved": support_margin >= -i7.EPSILON
                and coherence_margin >= -i7.EPSILON,
                "positive_surplus_preserved": support_margin > i7.EPSILON
                and coherence_margin > i7.EPSILON,
                "classification": (
                    "surplus_preserved"
                    if support_margin > i7.EPSILON
                    and coherence_margin > i7.EPSILON
                    else (
                        "at_floor_edge"
                        if abs(support_margin) <= i7.EPSILON
                        and abs(coherence_margin) <= i7.EPSILON
                        else "floor_crossing_fail_closed"
                    )
                ),
            }
        )
    trace = {
        "artifact_id": "n24_i7a_maintenance_floor_boundary_trace",
        "source_candidate_row_id": i5a_row["row_id"],
        "observed_min_support": base_support,
        "observed_min_coherence": base_coherence,
        "declared_support_floor": base.SUPPORT_FLOOR,
        "declared_coherence_floor": base.COHERENCE_FLOOR,
        "floor_rows": rows,
        "highest_floor_with_positive_surplus": max(
            row["candidate_floor"] for row in rows if row["positive_surplus_preserved"]
        ),
        "floor_crossing_control_fail_closed_at": [
            row["candidate_floor"]
            for row in rows
            if row["classification"] == "floor_crossing_fail_closed"
        ],
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def build_traces(i5a_row: dict[str, Any], i2: dict[str, Any]) -> dict[str, Any]:
    previous_branch_costs = i7.BRANCH_STRESS_COSTS
    previous_drain_stress = i7.MAINTENANCE_DRAIN_STRESS
    i7.BRANCH_STRESS_COSTS = BRANCH_STRESS_COSTS_I7A
    i7.MAINTENANCE_DRAIN_STRESS = MAINTENANCE_DRAIN_STRESS_I7A
    try:
        surplus_trace = i7.surplus_margin_threshold_trace(i5a_row)
        branch_trace = i7.optional_branch_capacity_trace(i5a_row)
        flux_trace = i7.flux_leakage_boundary_trace(i5a_row)
        combined_trace = i7.combined_ab5_stress_gate_trace(branch_trace, flux_trace)
    finally:
        i7.BRANCH_STRESS_COSTS = previous_branch_costs
        i7.MAINTENANCE_DRAIN_STRESS = previous_drain_stress
    floor_trace = maintenance_floor_boundary_trace_i7a(i5a_row)
    controls = i7.stress_control_matrix(i2)
    return {
        "surplus_trace": surplus_trace,
        "branch_trace": branch_trace,
        "floor_trace": floor_trace,
        "flux_trace": flux_trace,
        "combined_trace": combined_trace,
        "controls": controls,
    }


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5a = base.load_json(I5A_OUTPUT_PATH)
    i6a = base.load_json(I6A_OUTPUT_PATH)
    i7_original = base.load_json(I7_OUTPUT_PATH)
    i5a_row = i5a["candidate_rows"][0]
    traces = build_traces(i5a_row, i2)

    trace_paths = {
        "surplus_margin_threshold_trace_path": write_artifact(
            "n24_i7a_surplus_margin_threshold_trace.json", traces["surplus_trace"]
        ),
        "optional_branch_capacity_trace_path": write_artifact(
            "n24_i7a_optional_branch_capacity_trace.json", traces["branch_trace"]
        ),
        "maintenance_floor_boundary_trace_path": write_artifact(
            "n24_i7a_maintenance_floor_boundary_trace.json", traces["floor_trace"]
        ),
        "flux_leakage_boundary_trace_path": write_artifact(
            "n24_i7a_flux_leakage_boundary_trace.json", traces["flux_trace"]
        ),
        "combined_ab5_stress_gate_trace_path": write_artifact(
            "n24_i7a_combined_ab5_stress_gate_trace.json", traces["combined_trace"]
        ),
        "stress_control_matrix_path": write_artifact(
            "n24_i7a_stress_control_matrix.json", traces["controls"]
        ),
    }
    ab5_supported = traces["combined_trace"]["combined_ab5_gate_supported"]
    summary_trace = {
        "artifact_id": "n24_i7a_stress_threshold_summary_trace",
        "i6a_source_output_digest": i6a["output_digest"],
        "support_budget_count_gate_met": traces["branch_trace"][
            "support_budget_can_reach_ab5_count_gate_under_nonzero_stress"
        ],
        "nonzero_flux_stress_clean": traces["flux_trace"][
            "any_nonzero_flux_stress_preserves_bound"
        ],
        "combined_ab5_gate_supported": ab5_supported,
        "combined_best_passing_row": traces["combined_trace"]["best_passing_row"],
        "ab5_candidate_supported": ab5_supported,
        "ab5_blocker": (
            "none"
            if ab5_supported
            else "no_combined_nonzero_stress_row_preserves_count_and_flux"
        ),
        "classification": (
            "higher_margin_support_axis_flux_at_bound_ab5_candidate"
            if ab5_supported
            else "alternative_ab4_only"
        ),
        "does_not_replace_i7": True,
    }
    summary_trace["trace_digest"] = base.digest_value(summary_trace)
    trace_paths["stress_threshold_summary_trace_path"] = write_artifact(
        "n24_i7a_stress_threshold_summary_trace.json", summary_trace
    )
    manifest = artifact_manifest(
        [
            (trace_paths["surplus_margin_threshold_trace_path"], "surplus_margin_trace"),
            (trace_paths["optional_branch_capacity_trace_path"], "optional_branch_trace"),
            (trace_paths["maintenance_floor_boundary_trace_path"], "maintenance_floor_trace"),
            (trace_paths["flux_leakage_boundary_trace_path"], "flux_leakage_trace"),
            (trace_paths["combined_ab5_stress_gate_trace_path"], "replay_trace"),
            (trace_paths["stress_control_matrix_path"], "negative_control_trace"),
            (trace_paths["stress_threshold_summary_trace_path"], "replay_trace"),
        ]
    )
    checks = [
        base.check("i1_inventory_passed", i1["status"] == "passed" and not i1["failed_checks"], i7.source_status(i1)),
        base.check("i2_schema_passed", i2["status"] == "passed" and not i2["failed_checks"], i7.source_status(i2)),
        base.check("i3_active_nulls_passed", i3["status"] == "passed" and not i3["failed_checks"], i7.source_status(i3)),
        base.check("i4_surplus_probe_passed", i4["status"] == "passed" and not i4["failed_checks"], i7.source_status(i4)),
        base.check("i5a_optional_probe_passed", i5a["status"] == "passed" and not i5a["failed_checks"], i7.source_status(i5a)),
        base.check("i6a_ab4_candidate_ready", i6a["status"] == "passed" and not i6a["failed_checks"] and i6a["iteration6a_boundary"]["ab4_candidate_supported"] is True, i7.source_status(i6a)),
        base.check("original_i7_preserved", i7_original["status"] == "passed" and not i7_original["failed_checks"], {
            "i7_digest": i7_original["output_digest"],
            "i7_replaced": False,
        }),
        base.check(
            "higher_margin_support_axis_mapped",
            traces["surplus_trace"]["highest_stress_preserving_minimum_surplus_margin"]
            >= 1.0
            and traces["branch_trace"]["support_budget_can_reach_ab5_count_gate_under_nonzero_stress"]
            is True,
            {
                "highest_stress_preserving_minimum_surplus_margin": traces[
                    "surplus_trace"
                ]["highest_stress_preserving_minimum_surplus_margin"],
                "best_passing_row": traces["combined_trace"]["best_passing_row"],
            },
        ),
        base.check(
            "flux_bottleneck_still_at_bound",
            traces["combined_trace"]["best_passing_row"]["optional_flux_stress"]
            == base.FLUX_OR_LEAKAGE_BOUND
            and any(
                row["classification"] == "flux_leakage_fail_closed"
                for row in traces["flux_trace"]["flux_rows"]
            ),
            traces["flux_trace"],
        ),
        base.check(
            "ab5_supported_as_alternative_not_replacement",
            ab5_supported is True and summary_trace["does_not_replace_i7"] is True,
            summary_trace,
        ),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) == 7
            and all(item["sha256"] == base.sha256_file(item["path"]) for item in manifest),
            manifest,
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in unsafe_claim_flags(i2).values()),
            unsafe_claim_flags(i2),
        ),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_stress_threshold_matrix_i7a",
        "schema_version": "n24_stress_threshold_matrix_i7a_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "7-A",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_alternative_higher_margin_ab5_candidate_flux_bottleneck_remains"
            if not failed_checks
            else "failed_alternative_stress_threshold_matrix"
        ),
        "purpose": "stress-test the I5-A/I6-A high-margin optionality variant without replacing I7",
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(I5A_OUTPUT_PATH, "n24_i5a_alternative_optional_probe"),
            base.source_record(I6A_OUTPUT_PATH, "n24_i6a_alternative_replay_control_matrix"),
            base.source_record(I7_OUTPUT_PATH, "n24_i7_original_stress_context"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "trace_paths": trace_paths,
        "surplus_margin_threshold_trace": traces["surplus_trace"],
        "optional_branch_capacity_trace": traces["branch_trace"],
        "maintenance_floor_boundary_trace": traces["floor_trace"],
        "flux_leakage_boundary_trace": traces["flux_trace"],
        "combined_ab5_stress_gate_trace": traces["combined_trace"],
        "stress_control_matrix": traces["controls"],
        "stress_threshold_summary_trace": summary_trace,
        "iteration7a_boundary": {
            "provisional_ab_ladder_rung": "AB5",
            "ab4_candidate_supported": True,
            "ab5_candidate_supported": ab5_supported,
            "ab5_or_stronger_supported": ab5_supported,
            "does_not_replace_i7": True,
            "support_axis_stronger_than_i7": True,
            "flux_axis_bottleneck_remains": True,
            "ready_for_iteration_8_closeout": not failed_checks,
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
        },
        "geometric_interpretation": {
            "short_read": (
                "I7-A strengthens the support-budget side of N24: the alternative "
                "variant keeps two branches jointly admissible at per-branch cost "
                "0.5, much wider than I7's 0.05. The flux axis still only passes "
                "at the frozen 1e-9 bound."
            ),
            "claim_boundary": (
                "This corroborates AB5 across a higher-margin support setup but "
                "does not broaden flux robustness and does not replace I7. Reward, "
                "semantic choice, agency, native support, sentience, Phase 8, and "
                "ant ecology remain blocked."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab5_candidate_supported": ab5_supported,
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "native_support_claim_allowed": False,
            "sentience_claim_allowed": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "unsafe_claim_flags": unsafe_claim_flags(i2),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["no_absolute_paths"] = no_absolute_paths(output)
    output["checks"].append(
        base.check("no_absolute_paths", output["no_absolute_paths"] is True, True)
    )
    output["failed_checks"] = [
        item for item in output["checks"] if item["passed"] is not True
    ]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_alternative_higher_margin_ab5_candidate_flux_bottleneck_remains"
        if not output["failed_checks"]
        else "failed_alternative_stress_threshold_matrix"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    best = output["stress_threshold_summary_trace"]["combined_best_passing_row"]
    boundary = output["iteration7a_boundary"]
    lines = [
        "# N24 Iteration 7-A - Alternative Stress And Threshold Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 7-A stress-tests the I5-A/I6-A high-margin optionality variant.",
        "It strengthens the support-budget side of the AB5 result but confirms the",
        "flux/leakage bottleneck remains at the frozen 1e-9 bound.",
        "",
        "```text",
        f"best_combined_per_branch_support_cost = {best['per_branch_support_cost']:.12f}",
        f"best_combined_optional_flux_stress = {best['optional_flux_stress']:.12f}",
        f"best_combined_joint_count = {best['max_jointly_admissible_by_support_budget']}",
        f"ab5_candidate_supported = {str(boundary['ab5_candidate_supported']).lower()}",
        f"support_axis_stronger_than_i7 = {str(boundary['support_axis_stronger_than_i7']).lower()}",
        f"flux_axis_bottleneck_remains = {str(boundary['flux_axis_bottleneck_remains']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    base.write_json(OUTPUT, output)
    output = base.load_json(base.rel(OUTPUT))
    write_report(output)
    if output["failed_checks"]:
        raise SystemExit(f"failed checks: {output['failed_checks']}")


if __name__ == "__main__":
    main()
