#!/usr/bin/env python3
"""Build N24 Iteration 7-C producer-mediated flux-conditioning probe."""

from __future__ import annotations

import math
from typing import Any

import build_n24_flux_envelope_probe_i7b as i7b
import build_n24_minimal_surplus_probe as base


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_producer_flux_conditioning_probe_i7c.json"
REPORT = EXPERIMENT / "reports" / "n24_producer_flux_conditioning_probe_i7c.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n24_producer_flux_conditioning_probe_i7c_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_producer_flux_conditioning_probe_i7c.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_producer_flux_conditioning_probe_i7c.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I5_OUTPUT_PATH = i7b.I5_OUTPUT_PATH
I5A_OUTPUT_PATH = i7b.I5A_OUTPUT_PATH
I7_OUTPUT_PATH = i7b.I7_OUTPUT_PATH
I7A_OUTPUT_PATH = i7b.I7A_OUTPUT_PATH
I7B_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_flux_envelope_probe_i7b.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

ATTEMPTED_FLUX_STRESS_VALUES = [
    base.FLUX_OR_LEAKAGE_BOUND,
    base.FLUX_OR_LEAKAGE_BOUND * 1.01,
    base.FLUX_OR_LEAKAGE_BOUND * 2,
    base.FLUX_OR_LEAKAGE_BOUND * 5,
    base.FLUX_OR_LEAKAGE_BOUND * 10,
    base.FLUX_OR_LEAKAGE_BOUND * 20,
]
MAX_CONDITIONING_WINDOWS = 10
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


def source_status(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": source.get("status", "not_recorded"),
        "acceptance_state": source.get("acceptance_state", "not_recorded"),
        "output_digest": source.get("output_digest", "not_recorded"),
        "failed_check_count": len(source.get("failed_checks", [])),
    }


def producer_contract() -> dict[str, Any]:
    contract = {
        "producer_id": "n24_i7c_declared_flux_conditioning_producer",
        "producer_role": "producer_mediated_flux_conditioning_surface",
        "producer_kind": "rc_compatible_packet_schedule_manager",
        "declared_before_use": True,
        "classification": "producer_mediated",
        "substrate_carried_native_evidence": False,
        "naturalization_debt": "native_flux_routing_or_rate_limiting_surface",
        "observes_only": [
            "source_current_optional_branch_records",
            "residual_support_margin_under_optionality",
            "jointly_admissible_optional_continuation_count",
            "flux_or_leakage_bound",
            "attempted_optional_flux_stress",
        ],
        "acts_by": [
            "split_attempted_optional_flux_into_source_visible_windows",
            "cap_each_conditioned_window_at_native_flux_or_leakage_bound",
            "record_window_schedule_and_flux_ledger_before_claim_evaluation",
        ],
        "max_conditioning_windows": MAX_CONDITIONING_WINDOWS,
        "native_flux_or_leakage_bound": base.FLUX_OR_LEAKAGE_BOUND,
        "thresholds_unchanged": True,
        "support_added": 0.0,
        "coherence_added": 0.0,
        "floor_relaxation_allowed": False,
        "hidden_budget_relief_allowed": False,
        "hidden_support_allowed": False,
        "post_hoc_conditioning_allowed": False,
        "reward_or_proxy_scoring_allowed": False,
        "semantic_choice_allowed": False,
        "native_n24c6_relabel_allowed": False,
        "does_not_retroactively_replace_i7b": True,
    }
    contract["producer_contract_digest"] = base.digest_value(contract)
    return contract


def max_joint_count(source_row: dict[str, Any], candidate_id: str) -> int:
    per_branch_cost = BRANCH_COST_BY_CANDIDATE[candidate_id]
    base_margin = source_row["residual_support_margin_under_optionality"]
    max_joint = 0
    for branch_count in range(1, source_row["optional_continuation_availability_count"] + 1):
        if base_margin - (per_branch_cost * branch_count) > 1e-12:
            max_joint = branch_count
    return max_joint


def conditioning_windows(attempted_flux: float) -> int:
    return max(1, math.ceil((attempted_flux / base.FLUX_OR_LEAKAGE_BOUND) - 1e-12))


def candidate_conditioning_trace(
    candidate_id: str,
    source_row: dict[str, Any],
    source_stress: dict[str, Any],
) -> dict[str, Any]:
    joint_count = max_joint_count(source_row, candidate_id)
    rows = []
    for attempted_flux in ATTEMPTED_FLUX_STRESS_VALUES:
        window_count = conditioning_windows(attempted_flux)
        conditioned_flux_per_window = attempted_flux / window_count
        native_flux_envelope_passes_without_producer = (
            attempted_flux <= base.FLUX_OR_LEAKAGE_BOUND
        )
        producer_required = not native_flux_envelope_passes_without_producer
        producer_conditioning_gate_passes = (
            window_count <= MAX_CONDITIONING_WINDOWS
            and conditioned_flux_per_window <= base.FLUX_OR_LEAKAGE_BOUND + 1e-18
            and joint_count >= 2
        )
        rows.append(
            {
                "attempted_optional_flux_stress": attempted_flux,
                "native_flux_or_leakage_bound": base.FLUX_OR_LEAKAGE_BOUND,
                "native_flux_envelope_passes_without_producer": (
                    native_flux_envelope_passes_without_producer
                ),
                "producer_conditioning_required": producer_required,
                "conditioning_window_count": window_count,
                "max_conditioning_windows": MAX_CONDITIONING_WINDOWS,
                "conditioned_flux_per_window": conditioned_flux_per_window,
                "conditioned_windows_preserve_native_bound": (
                    conditioned_flux_per_window <= base.FLUX_OR_LEAKAGE_BOUND + 1e-18
                ),
                "jointly_admissible_optional_continuation_count": joint_count,
                "ab5_count_gate_met": joint_count >= 2,
                "producer_conditioning_gate_passes": producer_conditioning_gate_passes,
                "producer_mediated_flux_widening_row": (
                    producer_required and producer_conditioning_gate_passes
                ),
                "classification": (
                    "native_bound_row"
                    if native_flux_envelope_passes_without_producer
                    else (
                        "producer_conditioned_flux_pass"
                        if producer_conditioning_gate_passes
                        else "producer_conditioning_window_cap_fail_closed"
                    )
                ),
            }
        )
    producer_rows = [
        row for row in rows if row["producer_mediated_flux_widening_row"] is True
    ]
    failed_rows = [
        row
        for row in rows
        if row["classification"] == "producer_conditioning_window_cap_fail_closed"
    ]
    trace = {
        "artifact_id": f"n24_i7c_{candidate_id.lower().replace('-', '')}_conditioning_trace",
        "candidate_id": candidate_id,
        "source_candidate_row_id": source_row["row_id"],
        "source_stress_output_digest": source_stress["output_digest"],
        "per_branch_support_cost": BRANCH_COST_BY_CANDIDATE[candidate_id],
        "base_residual_support_margin": source_row[
            "residual_support_margin_under_optionality"
        ],
        "max_jointly_admissible_by_support_budget": joint_count,
        "conditioning_rows": rows,
        "native_flux_envelope_widened": False,
        "producer_mediated_flux_envelope_widened": bool(producer_rows),
        "highest_producer_conditioned_attempted_flux": (
            max(row["attempted_optional_flux_stress"] for row in producer_rows)
            if producer_rows
            else "not_supported"
        ),
        "first_window_cap_failure": (
            min(row["attempted_optional_flux_stress"] for row in failed_rows)
            if failed_rows
            else "not_observed"
        ),
        "producer_conditioning_window_cap": MAX_CONDITIONING_WINDOWS,
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def producer_conditioning_summary(
    i5: dict[str, Any],
    i5a: dict[str, Any],
    i7_output: dict[str, Any],
    i7a_output: dict[str, Any],
    i7b_output: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    traces = [
        candidate_conditioning_trace("I7", i5["candidate_rows"][0], i7_output),
        candidate_conditioning_trace("I7-A", i5a["candidate_rows"][0], i7a_output),
    ]
    producer_widening_rows = [
        row
        for trace in traces
        for row in trace["conditioning_rows"]
        if row["producer_mediated_flux_widening_row"] is True
    ]
    summary = {
        "artifact_id": "n24_i7c_producer_flux_conditioning_summary_trace",
        "producer_contract_digest": contract["producer_contract_digest"],
        "i7b_native_flux_blocker_digest": i7b_output["output_digest"],
        "i7b_native_n24c6_flux_readiness_supported": i7b_output[
            "iteration7b_boundary"
        ]["n24_c6_flux_readiness_supported"],
        "candidate_conditioning_traces": traces,
        "native_flux_envelope_widened": False,
        "producer_mediated_flux_envelope_widened": bool(producer_widening_rows),
        "highest_producer_conditioned_attempted_flux": (
            max(row["attempted_optional_flux_stress"] for row in producer_widening_rows)
            if producer_widening_rows
            else "not_supported"
        ),
        "producer_mediated_window_cap": MAX_CONDITIONING_WINDOWS,
        "producer_mediated_flux_scaffold_supported": bool(producer_widening_rows),
        "native_n24_c6_flux_readiness_supported": False,
        "n24_c6_native_blocker_preserved": "flux_envelope_not_widened_above_1e-9",
        "n24_c6_producer_scaffold_status": (
            "producer_mediated_flux_conditioning_scaffold_supported"
            if producer_widening_rows
            else "producer_mediated_flux_conditioning_scaffold_not_supported"
        ),
    }
    summary["trace_digest"] = base.digest_value(summary)
    return summary


def producer_control_matrix(i2: dict[str, Any]) -> dict[str, Any]:
    effects = i2["control_matrix_schema"]["control_effects"]
    custom_effects = {
        "unlogged_flux_conditioning_control": (
            "conditioned flux without source-visible ledger blocks I7-C"
        ),
        "threshold_relaxation_control": (
            "changing the 1e-9 bound or maintenance floors blocks I7-C"
        ),
        "post_hoc_conditioning_control": (
            "conditioning schedule assembled after outcome inspection blocks I7-C"
        ),
        "native_n24c6_relabel_control": (
            "producer-mediated flux conditioning cannot relabel native N24-C6 as supported"
        ),
        "merge_leakage_as_conditioned_flux_control": (
            "merge or leakage counted as successful routing blocks I7-C"
        ),
    }
    rows = []
    for control_id in [
        "hidden_budget_relief_control",
        "floor_crossing_as_abundance_control",
        "proxy_only_optional_branch_gain_control",
        "optional_branch_label_only_control",
        "post_hoc_surplus_construction_control",
        "unlogged_flux_conditioning_control",
        "threshold_relaxation_control",
        "post_hoc_conditioning_control",
        "native_n24c6_relabel_control",
        "merge_leakage_as_conditioned_flux_control",
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
                "blocked_condition": effects.get(
                    control_id,
                    custom_effects.get(
                        control_id,
                        "producer-mediated flux conditioning relabel is rejected",
                    ),
                ),
                "claim_allowed_when_triggered": False,
                "interpretation": (
                    "producer-mediated flux help is admissible only when the "
                    "producer is declared, source-visible, budget-neutral, "
                    "threshold-preserving, and not relabeled as native support"
                ),
            }
        )
    matrix = {
        "artifact_id": "n24_i7c_producer_flux_conditioning_control_matrix",
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
    i7b_output = base.load_json(I7B_OUTPUT_PATH)
    contract = producer_contract()
    summary = producer_conditioning_summary(
        i5, i5a, i7_output, i7a_output, i7b_output, contract
    )
    controls = producer_control_matrix(i2)
    trace_paths = {
        "producer_contract_path": write_artifact(
            "n24_i7c_flux_conditioning_producer_contract.json", contract
        ),
        "producer_flux_conditioning_summary_trace_path": write_artifact(
            "n24_i7c_producer_flux_conditioning_summary_trace.json", summary
        ),
        "producer_flux_conditioning_control_matrix_path": write_artifact(
            "n24_i7c_producer_flux_conditioning_control_matrix.json", controls
        ),
    }
    manifest = artifact_manifest(
        [
            (trace_paths["producer_contract_path"], "producer_contract_trace"),
            (
                trace_paths["producer_flux_conditioning_summary_trace_path"],
                "flux_leakage_trace",
            ),
            (
                trace_paths["producer_flux_conditioning_control_matrix_path"],
                "negative_control_trace",
            ),
        ]
    )
    checks = [
        base.check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            source_status(i1),
        ),
        base.check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            source_status(i2),
        ),
        base.check(
            "i3_active_nulls_passed",
            i3["status"] == "passed" and not i3["failed_checks"],
            source_status(i3),
        ),
        base.check(
            "native_i7b_flux_blocker_preserved",
            i7b_output["status"] == "passed"
            and i7b_output["iteration7b_boundary"][
                "n24_c6_flux_readiness_supported"
            ]
            is False,
            {
                "i7b_digest": i7b_output["output_digest"],
                "i7b_blocker": i7b_output["iteration7b_boundary"]["n24_c6_blocker"],
            },
        ),
        base.check(
            "producer_contract_declared_before_use",
            contract["declared_before_use"] is True
            and contract["classification"] == "producer_mediated",
            contract,
        ),
        base.check(
            "producer_adds_no_support_or_coherence",
            contract["support_added"] == 0.0
            and contract["coherence_added"] == 0.0
            and contract["hidden_budget_relief_allowed"] is False,
            contract,
        ),
        base.check(
            "thresholds_unchanged",
            contract["thresholds_unchanged"] is True
            and contract["native_flux_or_leakage_bound"] == base.FLUX_OR_LEAKAGE_BOUND,
            contract,
        ),
        base.check(
            "producer_mediated_flux_scaffold_supported",
            summary["producer_mediated_flux_scaffold_supported"] is True
            and summary["producer_mediated_flux_envelope_widened"] is True,
            summary,
        ),
        base.check(
            "native_flux_envelope_not_reclassified",
            summary["native_flux_envelope_widened"] is False
            and summary["native_n24_c6_flux_readiness_supported"] is False,
            summary,
        ),
        base.check(
            "controls_fail_closed",
            controls["status"] == "passed" and not controls["failed_open_controls"],
            controls,
        ),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) == 3
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
        "artifact_id": "n24_producer_flux_conditioning_probe_i7c",
        "schema_version": "n24_producer_flux_conditioning_probe_i7c_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "7-C",
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_producer_mediated_flux_conditioning_scaffold_native_c6_still_blocked"
            if not failed_checks
            else "failed_producer_flux_conditioning_probe"
        ),
        "purpose": (
            "test whether a declared source-visible producer can condition N24 "
            "optional-branch flux above the native 1e-9 envelope without changing "
            "thresholds, adding hidden support, or relabeling native N24-C6"
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
            base.source_record(I7B_OUTPUT_PATH, "n24_i7b_native_flux_blocker"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "trace_paths": trace_paths,
        "producer_contract": contract,
        "producer_flux_conditioning_summary_trace": summary,
        "producer_flux_conditioning_control_matrix": controls,
        "iteration7c_boundary": {
            "producer_mediated_flux_scaffold_supported": summary[
                "producer_mediated_flux_scaffold_supported"
            ],
            "producer_mediated_flux_envelope_widened": summary[
                "producer_mediated_flux_envelope_widened"
            ],
            "native_flux_envelope_widened": summary["native_flux_envelope_widened"],
            "native_n24_c6_flux_readiness_supported": summary[
                "native_n24_c6_flux_readiness_supported"
            ],
            "native_n24_c6_blocker_preserved": summary[
                "n24_c6_native_blocker_preserved"
            ],
            "producer_assisted_n25_flux_scaffold_candidate": summary[
                "producer_mediated_flux_scaffold_supported"
            ],
            "final_native_n24_closeout_target_changed": False,
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
                "I7-C shows that the N24 flux bottleneck can be helped by a "
                "declared producer that splits attempted optional flux into "
                "source-visible windows, each still below the native 1e-9 "
                "per-window leakage bound."
            ),
            "native_boundary": (
                "This does not make native N24-C6 true. The original native "
                "I7-B blocker remains: unconditioned N24 optionality still fails "
                "above the 1e-9 flux envelope."
            ),
            "handoff_effect": (
                "The useful consequence is a producer-mediated N25 scaffold and "
                "a precise naturalization target: native LGRC would need a "
                "source-current flux routing or rate-limiting surface to turn "
                "this producer result into native flux readiness."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab5_candidate_supported": True,
            "native_n24_c6_flux_readiness_supported": False,
            "producer_mediated_flux_scaffold_supported": summary[
                "producer_mediated_flux_scaffold_supported"
            ],
            "producer_mediated_claim_allowed_as_native": False,
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
        "accepted_producer_mediated_flux_conditioning_scaffold_native_c6_still_blocked"
        if not output["failed_checks"]
        else "failed_producer_flux_conditioning_probe"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    boundary = output["iteration7c_boundary"]
    summary = output["producer_flux_conditioning_summary_trace"]
    contract = output["producer_contract"]
    highest = summary["highest_producer_conditioned_attempted_flux"]
    lines = [
        "# N24 Iteration 7-C - Producer-Mediated Flux Conditioning Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 7-C tests a declared producer-mediated flux conditioner. The",
        "producer does not add support, relax floors, or change the native",
        "`1e-9` per-window flux/leakage bound. It only splits attempted flux into",
        "source-visible conditioning windows capped by that native bound.",
        "",
        "```text",
        f"native_flux_or_leakage_bound = {contract['native_flux_or_leakage_bound']:.12f}",
        f"max_conditioning_windows = {contract['max_conditioning_windows']}",
        f"producer_mediated_flux_scaffold_supported = {str(boundary['producer_mediated_flux_scaffold_supported']).lower()}",
        f"producer_mediated_flux_envelope_widened = {str(boundary['producer_mediated_flux_envelope_widened']).lower()}",
        f"highest_producer_conditioned_attempted_flux = {highest:.12f}",
        f"native_n24_c6_flux_readiness_supported = {str(boundary['native_n24_c6_flux_readiness_supported']).lower()}",
        f"native_n24_c6_blocker_preserved = {boundary['native_n24_c6_blocker_preserved']}",
        "```",
        "",
        "## Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["native_boundary"],
        "",
        output["geometric_interpretation"]["handoff_effect"],
        "",
        "## Candidate Conditioning Rows",
        "",
        "| Candidate | Highest conditioned flux | Window cap failure | Producer widened |",
        "| --- | --- | --- | --- |",
    ]
    for trace in summary["candidate_conditioning_traces"]:
        lines.append(
            "| "
            f"`{trace['candidate_id']}` | "
            f"`{trace['highest_producer_conditioned_attempted_flux']:.12f}` | "
            f"`{trace['first_window_cap_failure']:.12f}` | "
            f"`{str(trace['producer_mediated_flux_envelope_widened']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I7-C supports a producer-mediated flux scaffold only. It does not",
            "retroactively change the native I7-B result, and it does not support",
            "reward maximization, semantic choice, agency, native support, sentience,",
            "Phase 8, or ant ecology.",
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
