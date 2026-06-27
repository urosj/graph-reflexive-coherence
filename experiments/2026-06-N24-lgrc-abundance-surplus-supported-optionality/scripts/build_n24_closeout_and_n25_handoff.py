#!/usr/bin/env python3
"""Build N24 Iteration 8 closeout and N25 handoff."""

from __future__ import annotations

import subprocess
from typing import Any

import build_n24_minimal_surplus_probe as base


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_closeout_and_n25_handoff.json"
REPORT = EXPERIMENT / "reports" / "n24_closeout_and_n25_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_closeout_and_n25_handoff.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_closeout_and_n25_handoff.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_minimal_surplus_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe_i5a.json"
)
I6A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix_i6a.json"
)
I7A_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_stress_threshold_matrix_i7a.json"
)
I7B_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_flux_envelope_probe_i7b.json"
)
I7C_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_producer_flux_conditioning_probe_i7c.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH


def source_status(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "failed_check_count": len(data.get("failed_checks", [])),
    }


def source_record(path: str, role: str) -> dict[str, Any]:
    data = base.load_json(path)
    return {
        "path": path,
        "sha256": base.sha256_file(path),
        "source_role": role,
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "failed_check_count": len(data.get("failed_checks", [])),
    }


def source_output_digest_valid(data: dict[str, Any]) -> bool:
    if "output_digest" not in data:
        return False
    expected = base.digest_value(
        {key: value for key, value in data.items() if key != "output_digest"}
    )
    return data["output_digest"] == expected


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


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


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5 = base.load_json(I5_OUTPUT_PATH)
    i6 = base.load_json(I6_OUTPUT_PATH)
    i7 = base.load_json(I7_OUTPUT_PATH)
    i5a = base.load_json(I5A_OUTPUT_PATH)
    i6a = base.load_json(I6A_OUTPUT_PATH)
    i7a = base.load_json(I7A_OUTPUT_PATH)
    i7b = base.load_json(I7B_OUTPUT_PATH)
    i7c = base.load_json(I7C_OUTPUT_PATH)
    source_outputs = [i1, i2, i3, i4, i5, i6, i7, i5a, i6a, i7a, i7b, i7c]
    all_sources_passed = all(
        source["status"] == "passed" and not source.get("failed_checks")
        for source in source_outputs
    )
    all_source_digests_valid = all(
        source_output_digest_valid(source) for source in source_outputs
    )
    unsafe_flags = unsafe_claim_flags(i2)
    claim_boundary_clean = all(value is False for value in unsafe_flags.values())
    src_clean = src_diff_empty()

    i7_boundary = i7["iteration7_boundary"]
    i7a_boundary = i7a["iteration7a_boundary"]
    i7b_boundary = i7b["iteration7b_boundary"]
    i7c_boundary = i7c["iteration7c_boundary"]
    native_ab5_supported = (
        i7_boundary["ab5_candidate_supported"] is True
        and i7a_boundary["ab5_candidate_supported"] is True
        and i7b_boundary["ab5_candidate_supported_from_i7"] is True
        and i7b_boundary["ab5_candidate_supported_from_i7a"] is True
    )
    native_n24_c6_supported = (
        i7b_boundary["n24_c6_flux_readiness_supported"] is True
        and i7c_boundary["native_n24_c6_flux_readiness_supported"] is True
    )
    producer_flux_scaffold_supported = (
        i7c_boundary["producer_mediated_flux_scaffold_supported"] is True
        and i7c_boundary["producer_mediated_flux_envelope_widened"] is True
    )
    closeout_passed = (
        all_sources_passed
        and all_source_digests_valid
        and native_ab5_supported
        and not native_n24_c6_supported
        and producer_flux_scaffold_supported
        and claim_boundary_clean
        and src_clean
    )

    final_classification = {
        "final_ab_ladder_rung": "AB5" if native_ab5_supported else "AB4",
        "final_n24_closeout_rung": "N24-C5" if native_ab5_supported else "N24-C4",
        "native_n24_c6_supported": False,
        "native_n24_c6_blocker": i7b_boundary["n24_c6_blocker"],
        "native_flux_leakage_debt": "flux_envelope_not_widened_above_1e-9",
        "producer_mediated_flux_scaffold_supported": producer_flux_scaffold_supported,
        "producer_assisted_n25_flux_scaffold_candidate": producer_flux_scaffold_supported,
        "producer_mediated_highest_conditioned_attempted_flux": i7c[
            "producer_flux_conditioning_summary_trace"
        ]["highest_producer_conditioned_attempted_flux"],
        "producer_mediated_claim_allowed_as_native": False,
        "final_global_ap4_reclassification_supported": False,
        "ap5_dependency_status": (
            "not_applicable_to_n24_positive_rows_no_proxy_reward_or_target_formation"
        ),
        "reward_maximization_supported": False,
        "semantic_choice_supported": False,
        "agency_supported": False,
        "native_support_supported": False,
        "sentience_supported": False,
        "phase8_opened": False,
        "ant_ecology_implementation_opened": False,
        "src_diff_empty": src_clean,
        "final_claim_ceiling": (
            "bounded artifact-level AB5 surplus-supported optionality candidate "
            "with producer-mediated flux-scaffold extension; native N24-C6 remains "
            "blocked by flux/leakage debt"
        ),
    }
    n25_handoff = {
        "next_experiment": "N25_spark_sub_basin_new_basin_formation",
        "handoff_status": "ready_with_native_flux_debt_and_producer_scaffold",
        "must_consume_n20_contract": True,
        "must_consume_n24_native_lane_first": True,
        "must_consume_n24_producer_extension_as_separate_lane": True,
        "native_lane": {
            "consumable_result": "AB5_N24-C5_surplus_supported_optionality",
            "source_artifacts": [
                I5_OUTPUT_PATH,
                I6_OUTPUT_PATH,
                I7_OUTPUT_PATH,
                I5A_OUTPUT_PATH,
                I6A_OUTPUT_PATH,
                I7A_OUTPUT_PATH,
                I7B_OUTPUT_PATH,
            ],
            "positive_capability": (
                "source-current surplus-supported optionality with replay/control "
                "and stress-backed jointly admissible optional branches"
            ),
            "blocking_debt": "native_flux_leakage_envelope_not_widened_above_1e-9",
            "n25_native_start_question": (
                "Can one N24 optional continuation become a distinguishable "
                "sub-basin or new-basin candidate while preserving the inherited "
                "native 1e-9 flux/leakage bound?"
            ),
        },
        "producer_assisted_lane": {
            "consumable_result": "producer_mediated_flux_conditioning_scaffold",
            "source_artifacts": [I7C_OUTPUT_PATH],
            "positive_capability": (
                "declared producer splits attempted optional flux into "
                "source-visible windows capped by the native per-window bound"
            ),
            "highest_conditioned_attempted_flux": i7c[
                "producer_flux_conditioning_summary_trace"
            ]["highest_producer_conditioned_attempted_flux"],
            "naturalization_target": "native_flux_routing_or_rate_limiting_surface",
            "n25_extension_question": (
                "Does producer-mediated flux conditioning permit a sub-basin or "
                "new-basin candidate, and can that mechanism be specified as "
                "future native LGRC naturalization debt?"
            ),
        },
        "must_not_consume_n24_as": [
            "semantic_choice",
            "reward_maximization",
            "proxy_gain",
            "agency",
            "native_support",
            "sentience",
            "phase8_implementation",
            "ant_ecology_specification",
            "native_n24_c6",
            "general_abundance_robustness",
        ],
        "required_n25_controls": [
            "label_only_new_basin_rejected",
            "single_basin_thickening_relabel_rejected",
            "merge_leakage_masquerading_as_new_basin_rejected",
            "non_replayable_transient_rejected",
            "hidden_producer_insertion_rejected",
            "producer_assisted_success_does_not_overwrite_native_failure",
            "native_flux_debt_remains_row_local",
        ],
    }
    interpretation = {
        "main_read": (
            "N24 closes natively at AB5/N24-C5. It establishes bounded "
            "surplus-supported optionality, including replay/control and stress "
            "evidence, but it does not support native N24-C6 because flux/leakage "
            "does not widen above the frozen 1e-9 bound."
        ),
        "producer_extension_read": (
            "I7-C adds a useful producer-mediated extension: a declared "
            "RC-compatible flux conditioner can split attempted optional flux "
            "into source-visible windows and carry attempted flux up to 1e-8. "
            "This is a scaffold and naturalization target, not native support."
        ),
        "n25_consequence": (
            "N25 should test spark/sub-basin/new-basin formation first under the "
            "native N24 lane, then separately under the producer-assisted lane. "
            "Producer-assisted success may identify a minimal missing mechanism, "
            "but cannot retroactively upgrade native N24-C6."
        ),
    }
    checks = [
        base.check("all_source_iterations_passed", all_sources_passed, [source_status(item) for item in source_outputs]),
        base.check("all_source_output_digests_valid", all_source_digests_valid, True),
        base.check("native_ab5_supported", native_ab5_supported is True, final_classification),
        base.check("native_n24_c6_remains_blocked", native_n24_c6_supported is False, final_classification),
        base.check("producer_scaffold_recorded_separately", producer_flux_scaffold_supported is True, final_classification),
        base.check("producer_not_reclassified_as_native", i7c["claim_boundary"]["producer_mediated_claim_allowed_as_native"] is False, i7c["claim_boundary"]),
        base.check("n25_handoff_has_two_lanes", n25_handoff["must_consume_n24_native_lane_first"] is True and n25_handoff["must_consume_n24_producer_extension_as_separate_lane"] is True, n25_handoff),
        base.check("unsafe_claim_flags_all_false", claim_boundary_clean, unsafe_flags),
        base.check("src_diff_empty", src_clean, src_clean),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_closeout_and_n25_handoff",
        "schema_version": "n24_closeout_and_n25_handoff_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": "8",
        "generated_at": GENERATED_AT,
        "status": "passed" if closeout_passed and not failed_checks else "failed",
        "acceptance_state": (
            "accepted_ab5_n24c5_closeout_with_producer_flux_scaffold_n25_handoff"
            if closeout_passed and not failed_checks
            else "failed_n24_closeout"
        ),
        "purpose": (
            "close N24, preserve native/producer-assisted distinction, and hand "
            "off to N25 spark/sub-basin/new-basin formation"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            source_record(I5_OUTPUT_PATH, "n24_i5_optional_continuation_probe"),
            source_record(I6_OUTPUT_PATH, "n24_i6_replay_control_matrix"),
            source_record(I7_OUTPUT_PATH, "n24_i7_native_stress_threshold_matrix"),
            source_record(I5A_OUTPUT_PATH, "n24_i5a_high_margin_optional_probe"),
            source_record(I6A_OUTPUT_PATH, "n24_i6a_high_margin_replay_control_matrix"),
            source_record(I7A_OUTPUT_PATH, "n24_i7a_high_margin_stress_matrix"),
            source_record(I7B_OUTPUT_PATH, "n24_i7b_native_flux_blocker"),
            source_record(I7C_OUTPUT_PATH, "n24_i7c_producer_flux_conditioning_extension"),
            source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "final_classification": final_classification,
        "n25_handoff": n25_handoff,
        "interpretation": interpretation,
        "claim_boundary": {
            "native_ab5_supported": native_ab5_supported,
            "native_n24_c6_supported": False,
            "producer_mediated_flux_scaffold_supported": producer_flux_scaffold_supported,
            "producer_mediated_claim_allowed_as_native": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "native_support_claim_allowed": False,
            "sentience_claim_allowed": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "unsafe_claim_flags": unsafe_flags,
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
    output["status"] = (
        "passed" if closeout_passed and not output["failed_checks"] else "failed"
    )
    output["acceptance_state"] = (
        "accepted_ab5_n24c5_closeout_with_producer_flux_scaffold_n25_handoff"
        if output["status"] == "passed"
        else "failed_n24_closeout"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    final = output["final_classification"]
    handoff = output["n25_handoff"]
    lines = [
        "# N24 Iteration 8 - Closeout And N25 Handoff",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Final Classification",
        "",
        "```text",
        f"final_ab_ladder_rung = {final['final_ab_ladder_rung']}",
        f"final_n24_closeout_rung = {final['final_n24_closeout_rung']}",
        f"native_n24_c6_supported = {str(final['native_n24_c6_supported']).lower()}",
        f"native_n24_c6_blocker = {final['native_n24_c6_blocker']}",
        f"producer_mediated_flux_scaffold_supported = {str(final['producer_mediated_flux_scaffold_supported']).lower()}",
        f"producer_assisted_n25_flux_scaffold_candidate = {str(final['producer_assisted_n25_flux_scaffold_candidate']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        output["interpretation"]["main_read"],
        "",
        output["interpretation"]["producer_extension_read"],
        "",
        output["interpretation"]["n25_consequence"],
        "",
        "## N25 Handoff",
        "",
        "```text",
        f"next_experiment = {handoff['next_experiment']}",
        f"handoff_status = {handoff['handoff_status']}",
        f"native_lane = {handoff['native_lane']['consumable_result']}",
        f"producer_assisted_lane = {handoff['producer_assisted_lane']['consumable_result']}",
        f"naturalization_target = {handoff['producer_assisted_lane']['naturalization_target']}",
        "```",
        "",
        "N25 should test native spark/sub-basin/new-basin formation first, then",
        "test the producer-assisted flux scaffold as a separate extension lane.",
        "",
        "## Claim Boundary",
        "",
        "```text",
        final["final_claim_ceiling"],
        "semantic choice = false",
        "reward maximization = false",
        "agency = false",
        "native support = false",
        "sentience = false",
        "Phase 8 = false",
        "ant ecology implementation = false",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
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
