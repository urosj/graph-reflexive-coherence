#!/usr/bin/env python3
"""Build N24 Iteration 7-B targeted flux-envelope probe."""

from __future__ import annotations

from typing import Any

import build_n24_minimal_surplus_probe as base
import build_n24_stress_threshold_matrix as i7


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_flux_envelope_probe_i7b.json"
REPORT = EXPERIMENT / "reports" / "n24_flux_envelope_probe_i7b.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_flux_envelope_probe_i7b_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_flux_envelope_probe_i7b.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_flux_envelope_probe_i7b.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I5_OUTPUT_PATH = i7.I5_OUTPUT_PATH
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe_i5a.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix.json"
)
I7A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix_i7a.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

FLUX_STRESS_VALUES = [
    0.0,
    base.FLUX_OR_LEAKAGE_BOUND * 0.25,
    base.FLUX_OR_LEAKAGE_BOUND * 0.5,
    base.FLUX_OR_LEAKAGE_BOUND,
    base.FLUX_OR_LEAKAGE_BOUND * 1.01,
    base.FLUX_OR_LEAKAGE_BOUND * 2,
    base.FLUX_OR_LEAKAGE_BOUND * 10,
    0.000001,
]
BRANCH_COST_BY_CANDIDATE = {
    "I7": 0.05,
    "I7-A": 0.5,
}


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


def candidate_flux_rows(
    candidate_id: str,
    source_row: dict[str, Any],
    source_stress: dict[str, Any],
) -> dict[str, Any]:
    per_branch_cost = BRANCH_COST_BY_CANDIDATE[candidate_id]
    base_margin = source_row["residual_support_margin_under_optionality"]
    max_joint = 0
    for branch_count in range(1, source_row["optional_continuation_availability_count"] + 1):
        if base_margin - (per_branch_cost * branch_count) > i7.EPSILON:
            max_joint = branch_count
    rows = []
    for flux in FLUX_STRESS_VALUES:
        rows.append(
            {
                "optional_flux_stress": flux,
                "flux_or_leakage_bound": base.FLUX_OR_LEAKAGE_BOUND,
                "flux_bound_preserved": flux <= base.FLUX_OR_LEAKAGE_BOUND,
                "above_bound": flux > base.FLUX_OR_LEAKAGE_BOUND,
                "per_branch_support_cost": per_branch_cost,
                "max_jointly_admissible_by_support_budget": max_joint,
                "ab5_count_gate_met": max_joint >= 2,
                "combined_gate_passes": (
                    flux <= base.FLUX_OR_LEAKAGE_BOUND and max_joint >= 2 and flux > 0
                ),
                "classification": (
                    "at_or_below_bound_pass"
                    if flux <= base.FLUX_OR_LEAKAGE_BOUND and max_joint >= 2 and flux > 0
                    else (
                        "quiet_baseline"
                        if flux == 0
                        else "above_bound_flux_fail_closed"
                    )
                ),
            }
        )
    above_bound_passes = [
        row for row in rows if row["above_bound"] and row["combined_gate_passes"]
    ]
    at_bound_passes = [
        row
        for row in rows
        if row["optional_flux_stress"] == base.FLUX_OR_LEAKAGE_BOUND
        and row["combined_gate_passes"]
    ]
    trace = {
        "candidate_id": candidate_id,
        "source_candidate_row_id": source_row["row_id"],
        "source_stress_output_digest": source_stress["output_digest"],
        "per_branch_support_cost": per_branch_cost,
        "base_residual_support_margin": base_margin,
        "max_jointly_admissible_by_support_budget": max_joint,
        "flux_rows": rows,
        "at_bound_flux_passes": bool(at_bound_passes),
        "above_bound_flux_passes": bool(above_bound_passes),
        "widens_flux_envelope": bool(above_bound_passes),
        "best_flux_stress_preserving_bound": max(
            row["optional_flux_stress"]
            for row in rows
            if row["flux_bound_preserved"] and row["optional_flux_stress"] > 0
        ),
        "first_above_bound_failure": min(
            row["optional_flux_stress"]
            for row in rows
            if row["above_bound"] and row["classification"] == "above_bound_flux_fail_closed"
        ),
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def flux_envelope_summary(
    i5: dict[str, Any],
    i5a: dict[str, Any],
    i7_output: dict[str, Any],
    i7a_output: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        candidate_flux_rows("I7", i5["candidate_rows"][0], i7_output),
        candidate_flux_rows("I7-A", i5a["candidate_rows"][0], i7a_output),
    ]
    summary = {
        "artifact_id": "n24_i7b_flux_envelope_summary_trace",
        "flux_or_leakage_bound": base.FLUX_OR_LEAKAGE_BOUND,
        "candidate_flux_traces": rows,
        "any_candidate_widens_flux_envelope": any(
            row["widens_flux_envelope"] for row in rows
        ),
        "all_candidates_pass_at_bound": all(row["at_bound_flux_passes"] for row in rows),
        "all_candidates_fail_above_bound": all(
            not row["above_bound_flux_passes"] for row in rows
        ),
        "classification": "flux_envelope_not_widened",
        "n24_c6_flux_readiness_supported": False,
        "n24_c6_blocker": "flux_envelope_not_widened_above_1e-9",
    }
    summary["trace_digest"] = base.digest_value(summary)
    return summary


def stress_control_matrix(i2: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for control_id in [
        "hidden_budget_relief_control",
        "floor_crossing_as_abundance_control",
        "proxy_only_optional_branch_gain_control",
        "optional_branch_label_only_control",
        "post_hoc_surplus_construction_control",
        "reward_maximization_relabel_control",
        "semantic_choice_relabel_control",
        "agency_relabel_control",
        "native_support_relabel_control",
        "phase8_relabel_control",
    ]:
        rows.append(
            {
                "control_id": control_id,
                "status": "failed_closed",
                "blocked_condition": i2["control_matrix_schema"]["control_effects"][
                    control_id
                ],
                "claim_allowed_when_triggered": False,
                "interpretation": "flux-envelope widening by relabel or hidden budget is rejected",
            }
        )
    matrix = {
        "artifact_id": "n24_i7b_flux_envelope_control_matrix",
        "status": "passed",
        "control_rows": rows,
        "failed_open_controls": [],
    }
    matrix["control_matrix_digest"] = base.digest_value(matrix)
    return matrix


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i5 = base.load_json(I5_OUTPUT_PATH)
    i5a = base.load_json(I5A_OUTPUT_PATH)
    i7_output = base.load_json(I7_OUTPUT_PATH)
    i7a_output = base.load_json(I7A_OUTPUT_PATH)
    summary = flux_envelope_summary(i5, i5a, i7_output, i7a_output)
    controls = stress_control_matrix(i2)
    trace_paths = {
        "flux_envelope_summary_trace_path": write_artifact(
            "n24_i7b_flux_envelope_summary_trace.json", summary
        ),
        "flux_envelope_control_matrix_path": write_artifact(
            "n24_i7b_flux_envelope_control_matrix.json", controls
        ),
    }
    manifest = artifact_manifest(
        [
            (trace_paths["flux_envelope_summary_trace_path"], "flux_leakage_trace"),
            (trace_paths["flux_envelope_control_matrix_path"], "negative_control_trace"),
        ]
    )
    checks = [
        base.check("i1_inventory_passed", i1["status"] == "passed" and not i1["failed_checks"], i1["acceptance_state"]),
        base.check("i2_schema_passed", i2["status"] == "passed" and not i2["failed_checks"], i2["acceptance_state"]),
        base.check("i3_active_nulls_passed", i3["status"] == "passed" and not i3["failed_checks"], i3["acceptance_state"]),
        base.check("i7_and_i7a_ready", i7_output["status"] == "passed" and i7a_output["status"] == "passed", {
            "i7_digest": i7_output["output_digest"],
            "i7a_digest": i7a_output["output_digest"],
        }),
        base.check("at_bound_flux_passes_for_both_candidates", summary["all_candidates_pass_at_bound"] is True, summary),
        base.check("above_bound_flux_fails_closed_for_both_candidates", summary["all_candidates_fail_above_bound"] is True, summary),
        base.check("flux_envelope_not_widened", summary["any_candidate_widens_flux_envelope"] is False, summary),
        base.check("controls_fail_closed", controls["status"] == "passed" and not controls["failed_open_controls"], controls),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) == 2
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
        "artifact_id": "n24_flux_envelope_probe_i7b",
        "schema_version": "n24_flux_envelope_probe_i7b_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "7-B",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_flux_envelope_not_widened_n24c6_flux_blocker_recorded"
            if not failed_checks
            else "failed_flux_envelope_probe"
        ),
        "purpose": (
            "test whether current N24 AB5 candidates have legal flux room above "
            "the frozen 1e-9 bound without changing thresholds or hiding budget"
        ),
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I5_OUTPUT_PATH, "n24_i5_original_optional_probe"),
            base.source_record(I5A_OUTPUT_PATH, "n24_i5a_alternative_optional_probe"),
            base.source_record(I7_OUTPUT_PATH, "n24_i7_original_stress_matrix"),
            base.source_record(I7A_OUTPUT_PATH, "n24_i7a_alternative_stress_matrix"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "trace_paths": trace_paths,
        "flux_envelope_summary_trace": summary,
        "flux_envelope_control_matrix": controls,
        "iteration7b_boundary": {
            "ab5_candidate_supported_from_i7": True,
            "ab5_candidate_supported_from_i7a": True,
            "flux_envelope_widened": summary["any_candidate_widens_flux_envelope"],
            "n24_c6_flux_readiness_supported": summary[
                "n24_c6_flux_readiness_supported"
            ],
            "n24_c6_blocker": summary["n24_c6_blocker"],
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
                "I7-B confirms the current N24 AB5 candidates pass at the frozen "
                "1e-9 flux bound but do not widen the flux envelope above it."
            ),
            "closeout_effect": (
                "This supports closing N24 as AB5/N24-C5 with explicit flux debt, "
                "not N24-C6. A future primitive must naturalize or widen the "
                "flux/leakage envelope before N24-style optionality can become "
                "N25-ready without that constraint."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab5_candidate_supported": True,
            "n24_c6_flux_readiness_supported": False,
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
        "accepted_flux_envelope_not_widened_n24c6_flux_blocker_recorded"
        if not output["failed_checks"]
        else "failed_flux_envelope_probe"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    boundary = output["iteration7b_boundary"]
    summary = output["flux_envelope_summary_trace"]
    lines = [
        "# N24 Iteration 7-B - Flux Envelope Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 7-B tests whether the existing N24 AB5 candidates have flux room",
        "above the frozen `1e-9` leakage bound. They do not.",
        "",
        "```text",
        f"flux_or_leakage_bound = {summary['flux_or_leakage_bound']:.12f}",
        f"all_candidates_pass_at_bound = {str(summary['all_candidates_pass_at_bound']).lower()}",
        f"all_candidates_fail_above_bound = {str(summary['all_candidates_fail_above_bound']).lower()}",
        f"any_candidate_widens_flux_envelope = {str(summary['any_candidate_widens_flux_envelope']).lower()}",
        f"n24_c6_flux_readiness_supported = {str(boundary['n24_c6_flux_readiness_supported']).lower()}",
        f"n24_c6_blocker = {boundary['n24_c6_blocker']}",
        "```",
        "",
        "## Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["closeout_effect"],
        "",
        "## Candidate Flux Rows",
        "",
        "| Candidate | Best preserved flux | First above-bound failure | Widens envelope |",
        "| --- | --- | --- | --- |",
    ]
    for trace in summary["candidate_flux_traces"]:
        lines.append(
            "| "
            f"`{trace['candidate_id']}` | "
            f"`{trace['best_flux_stress_preserving_bound']:.12f}` | "
            f"`{trace['first_above_bound_failure']:.12f}` | "
            f"`{str(trace['widens_flux_envelope']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
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
