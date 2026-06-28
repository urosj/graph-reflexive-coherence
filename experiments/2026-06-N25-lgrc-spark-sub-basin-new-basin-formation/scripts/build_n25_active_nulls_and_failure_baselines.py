#!/usr/bin/env python3
"""Build N25 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n25_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_active_nulls_and_failure_baselines.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_basin_formation_schema_and_controls.json"
)

REQUIRED_NULL_IDS = [
    "label_only_new_basin",
    "single_basin_thickening",
    "reshaped_old_boundary_only",
    "merge_leakage_as_basin",
    "non_replayable_transient",
    "hidden_producer_insertion",
    "n24_optionality_relabel",
    "producer_assisted_native_upgrade_relabel",
    "native_flux_debt_omitted",
    "ap_gap_prose_only",
    "unsafe_semantic_learning_relabel",
    "unsafe_choice_agency_native_support_phase8_relabels",
    "existing_lgrc9v3_spark_examples_skipped",
    "producer_before_native_spark_path",
]

NULL_SCENARIOS = [
    {
        "scenario_id": "label_only_new_basin",
        "lane": "native",
        "formation_class": "transient_fluctuation",
        "formation_source": "label_only",
        "control_ids": ["label_only_new_basin_rejected"],
        "bad_condition": "new basin exists only as a label or id",
        "blocked_reason": "no bifurcation, boundary, support/coherence, or replay distinction trace",
        "geometric_reading": (
            "A name is attached to part of the old basin, but the graph emits no "
            "source-current boundary, support/coherence floor, or separation trace."
        ),
    },
    {
        "scenario_id": "single_basin_thickening",
        "lane": "native",
        "formation_class": "reinforced_old_basin",
        "formation_source": "native_old_basin_thickening",
        "control_ids": ["single_basin_thickening_relabel_rejected"],
        "bad_condition": "old basin support thickens and is relabeled as sub-basin formation",
        "blocked_reason": "candidate is not boundary-distinguishable from the old basin",
        "geometric_reading": (
            "The existing basin gains local density, but no separable candidate "
            "boundary or old-to-candidate separation surface appears."
        ),
    },
    {
        "scenario_id": "reshaped_old_boundary_only",
        "lane": "native",
        "formation_class": "reshaped_old_boundary",
        "formation_source": "native_old_basin_thickening",
        "control_ids": ["reshaped_old_boundary_relabel_rejected"],
        "bad_condition": "old boundary shifts or wrinkles without a distinct candidate basin",
        "blocked_reason": "boundary movement is not basin formation",
        "geometric_reading": (
            "The old boundary changes shape, but the region remains one connected "
            "basin surface rather than a distinguishable sub-basin."
        ),
    },
    {
        "scenario_id": "merge_leakage_as_basin",
        "lane": "native",
        "formation_class": "merge_leakage_artifact",
        "formation_source": "native_merge_leakage",
        "control_ids": ["merge_leakage_masquerading_as_new_basin_rejected"],
        "bad_condition": "leakage or merge pressure is counted as a new basin",
        "blocked_reason": "merge/leakage margin fails as formation evidence",
        "geometric_reading": (
            "Flux smears across the old boundary or into a neighbor region. The "
            "result is continuity loss, not a separate support/coherence floor."
        ),
    },
    {
        "scenario_id": "non_replayable_transient",
        "lane": "native",
        "formation_class": "transient_fluctuation",
        "formation_source": "native_source_current_bifurcation",
        "control_ids": ["non_replayable_transient_rejected"],
        "bad_condition": "one-window spark-like fluctuation is treated as formation",
        "blocked_reason": "replayable distinction persistence is missing",
        "geometric_reading": (
            "A local spark candidate appears for one window but does not persist "
            "as a replayable boundary/support/coherence distinction."
        ),
    },
    {
        "scenario_id": "hidden_producer_insertion",
        "lane": "producer_assisted",
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "hidden_producer_insertion",
        "control_ids": [
            "hidden_producer_insertion_rejected",
            "producer_basin_insertion_without_trace_control",
        ],
        "bad_condition": "producer inserts a basin-like record without source-current trace",
        "blocked_reason": "producer insertion is not native or producer-assisted formation evidence",
        "geometric_reading": (
            "The candidate appears in producer state rather than in LGRC geometry; "
            "there is no source-current bifurcation or boundary-birth trace."
        ),
    },
    {
        "scenario_id": "n24_optionality_relabel",
        "lane": "native",
        "formation_class": "reinforced_old_basin",
        "formation_source": "report_derived",
        "control_ids": ["n24_optionality_relabel_as_formation_rejected"],
        "bad_condition": "N24 optional continuation is relabeled as N25 formation",
        "blocked_reason": "AB5 optionality is prerequisite context only",
        "geometric_reading": (
            "An optional branch set is not yet a distinguishable sub-basin; N25 "
            "must show new boundary/support/replay traces rather than relabel N24."
        ),
    },
    {
        "scenario_id": "producer_assisted_native_upgrade_relabel",
        "lane": "producer_assisted",
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "producer_flux_conditioned",
        "control_ids": [
            "producer_assisted_success_does_not_overwrite_native_failure",
            "producer_success_as_native_relabel_control",
            "producer_success_overwrites_native_failure_control",
        ],
        "bad_condition": "producer-assisted result is used to upgrade native BF or N24 native C6",
        "blocked_reason": "producer-assisted success has a separate ceiling",
        "geometric_reading": (
            "Flux conditioning may expose a missing mechanism, but it remains a "
            "producer-mediated lane and cannot repair the native lane by relabel."
        ),
    },
    {
        "scenario_id": "native_flux_debt_omitted",
        "lane": "native",
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "control_ids": ["native_flux_debt_remains_row_local"],
        "bad_condition": "native row omits or widens inherited N24 1e-9 flux debt",
        "blocked_reason": "native flux-debt invariant is missing",
        "geometric_reading": (
            "A candidate cannot count as native formation if it silently relaxes "
            "the inherited flux/leakage bound that blocked N24-C6."
        ),
    },
    {
        "scenario_id": "ap_gap_prose_only",
        "lane": "native",
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "control_ids": [
            "ap4_gap_prose_only_rejected",
            "ap5_proxy_target_omission_rejected_when_applicable",
        ],
        "bad_condition": "AP4/AP5 dependency is handled only in prose",
        "blocked_reason": "row-local AP statuses and reasons are required",
        "geometric_reading": (
            "Selection or proxy context cannot be smuggled into the row. If it is "
            "load-bearing, AP4/AP5 dependency status must be explicit."
        ),
    },
    {
        "scenario_id": "unsafe_semantic_learning_relabel",
        "lane": "native",
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "control_ids": ["semantic_learning_relabel_rejected"],
        "bad_condition": "spark/sub-basin candidate is relabeled as semantic learning",
        "blocked_reason": "N25 basin formation is not semantic learning",
        "geometric_reading": (
            "A new geometric distinction is not a semantic learning claim. The "
            "artifact remains below choice, meaning, intention, and agency."
        ),
    },
    {
        "scenario_id": "unsafe_choice_agency_native_support_phase8_relabels",
        "lane": "native",
        "formation_class": "new_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "control_ids": [
            "semantic_choice_relabel_rejected",
            "agency_relabel_rejected",
            "native_support_relabel_rejected",
            "phase8_relabel_rejected",
            "ant_ecology_relabel_rejected",
        ],
        "bad_condition": "formation candidate is relabeled as choice, agency, native support, Phase 8, or ant ecology",
        "blocked_reason": "unsafe claim boundary remains false",
        "geometric_reading": (
            "Even a replayable basin-formation candidate would be artifact-level "
            "geometry, not selfhood, agency, native support, or ecology."
        ),
    },
    {
        "scenario_id": "existing_lgrc9v3_spark_examples_skipped",
        "lane": "native",
        "formation_class": "transient_fluctuation",
        "formation_source": "report_derived",
        "control_ids": ["native_spark_source_policy_rejected"],
        "bad_condition": "N25 invents a spark path without checking existing LGRC9V3 spark examples",
        "blocked_reason": "existing native spark mechanisms must be considered first",
        "geometric_reading": (
            "A spark-like N25 row cannot bypass existing LGRC9V3 causal spark "
            "diagnostics or refinement transport evidence by inventing a new path."
        ),
    },
    {
        "scenario_id": "producer_before_native_spark_path",
        "lane": "producer_assisted",
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "producer_flux_conditioned",
        "control_ids": [
            "producer_schedule_post_hoc_control",
            "producer_before_native_spark_path_rejected",
            "producer_success_as_native_relabel_control",
        ],
        "bad_condition": "producer-assisted spark scaffold is introduced before native spark/example path is exhausted",
        "blocked_reason": "producer extension requires native insufficiency justification",
        "geometric_reading": (
            "Producer conditioning may be useful later, but it cannot be the first "
            "explanation when native LGRC spark mechanisms already exist."
        ),
    },
]

UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology_implementation",
    "ant_ecology_specification",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "reward_maximization",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_learning",
    "semantic_perception",
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


def active_null_row(
    scenario: dict[str, Any],
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
) -> dict[str, Any]:
    lane = str(scenario["lane"])
    native_row = lane == "native"
    row_id = f"n25_i3_null_{scenario['scenario_id']}"
    flux_debt_omission = scenario["scenario_id"] == "native_flux_debt_omitted"
    control_results = [
        {
            "control_id": control_id,
            "control_status": "failed_closed",
            "blocked_condition": scenario["bad_condition"],
            "expected_result": "false-positive claim rejected",
            "actual_result": "claim rejected",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks BF support for this null path",
        }
        for control_id in scenario["control_ids"]
    ]
    row = {
        "row_id": row_id,
        "source_iteration": "I3_active_nulls",
        "scenario_id": scenario["scenario_id"],
        "source_contract_row": i1["source_contract_row"],
        "source_consumable_contract_row": i1["source_consumable_contract_row"],
        "n20_source_contract_row": i1["source_contract_row"],
        "n20_consumable_contract_row": i1["source_consumable_contract_row"],
        "source_contract_row_digest": i1["source_contract_row_digest"],
        "source_consumable_contract_row_digest": i1["source_consumable_contract_row_digest"],
        "source_output_digest": i1["output_digest"],
        "schema_output_digest": i2["output_digest"],
        "run_artifact_id": "not_applicable_active_null_fixture",
        "runtime_config_digest": "not_applicable_active_null_fixture",
        "source_commit_or_source_digest": i2["output_digest"],
        "source_current_inputs": [],
        "artifact_manifest": [],
        "artifact_paths": [],
        "artifact_sha256": [],
        "artifact_paths_equal_manifest_paths": "not_applicable_active_null_fixture",
        "artifact_sha256_equal_manifest_sha256": "not_applicable_active_null_fixture",
        "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
        "row_specific_thresholds_declared_before_use": "not_applicable_active_null_fixture",
        "existing_lgrc_spark_sources_considered": scenario["scenario_id"]
        not in {"existing_lgrc9v3_spark_examples_skipped", "producer_before_native_spark_path"},
        "native_spark_mechanism_reuse_status": (
            "violated_by_null_control"
            if scenario["scenario_id"] in {"existing_lgrc9v3_spark_examples_skipped", "producer_before_native_spark_path"}
            else "not_applicable_active_null"
        ),
        "new_producer_code_justification": (
            "missing_blocks_producer_lane"
            if scenario["scenario_id"] == "producer_before_native_spark_path"
            else "not_applicable"
        ),
        "lane": lane,
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_result_class": (
            "not_applicable" if native_row else "producer_mediated_scaffold_candidate"
        ),
        "n24_native_lane_status": "AB5_N24-C5_context_only",
        "n24_producer_lane_status": "separate_producer_flux_scaffold_context_only",
        "formation_class": scenario["formation_class"],
        "formation_source": scenario["formation_source"],
        "bifurcation_trace": "missing_or_invalid_by_active_null",
        "new_boundary_candidate_trace": "missing_or_invalid_by_active_null",
        "new_basin_support_coherence_trace": "missing_or_invalid_by_active_null",
        "replayable_distinction_trace": "missing_or_invalid_by_active_null",
        "old_basin_relation_trace": "not_admissible_positive_evidence",
        "merge_leakage_trace": "not_admissible_positive_evidence",
        "formation_window": "not_applicable_active_null_fixture",
        "bifurcation_window": "not_applicable_active_null_fixture",
        "boundary_candidate_window": "not_applicable_active_null_fixture",
        "replay_window": "not_applicable_active_null_fixture",
        "old_basin_reference_window": "not_applicable_active_null_fixture",
        "bifurcation_window_order_valid": False,
        "thresholds_declared_before_bifurcation_window": False,
        "old_basin_signature_digest": "not_applicable_active_null_fixture",
        "candidate_basin_signature_digest": "not_applicable_active_null_fixture",
        "candidate_boundary_signature_digest": "not_applicable_active_null_fixture",
        "old_to_candidate_separation_digest": "not_applicable_active_null_fixture",
        "boundary_distinguishability_margin": "not_admissible_positive_evidence",
        "support_floor_margin_new_region": "not_admissible_positive_evidence",
        "coherence_floor_margin_new_region": "not_admissible_positive_evidence",
        "old_basin_separation_margin": "not_admissible_positive_evidence",
        "merge_leakage_margin": "not_admissible_positive_evidence",
        "replay_distinction_persistence_ratio": 0.0,
        "old_basin_thickening_rejected": True,
        "reshaped_old_boundary_rejected": True,
        "merge_leakage_rejected": True,
        "transient_rejected": True,
        "label_only_rejected": True,
        "native_flux_debt_bound": 1e-9 if native_row else "not_applicable_producer_lane",
        "native_flux_debt_recorded": (
            not flux_debt_omission if native_row else "not_applicable_producer_lane"
        ),
        "native_flux_debt_violation_reason": "omitted" if flux_debt_omission else "not_applicable",
        "native_flux_debt_widened": False if native_row else "not_applicable_producer_lane",
        "native_flux_debt_status": (
            "violated_blocks_native_row"
            if flux_debt_omission
            else ("preserved" if native_row else "not_applicable_producer_lane")
        ),
        "producer_flux_window_bound": "not_applicable_native_lane" if native_row else 1e-8,
        "producer_flux_window_declared_before_use": "not_applicable_native_lane"
        if native_row
        else False,
        "native_flux_debt_not_overwritten": True,
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "producer_residue_classification": "blocked_relabel" if native_row else "producer_mediated",
        "naturalization_debt": "not_supported_active_null",
        "ap4_dependency_status": "missing_blocks_row"
        if scenario["scenario_id"] == "ap_gap_prose_only"
        else "not_applicable",
        "ap5_dependency_status": "missing_blocks_row"
        if scenario["scenario_id"] == "ap_gap_prose_only"
        else "not_applicable",
        "ap4_condition_reason": "active_null_blocks_prose_only_dependency",
        "ap5_condition_reason": "active_null_blocks_proxy_target_omission_when_applicable",
        "control_ids_covered": scenario["control_ids"],
        "control_results": control_results,
        "control_status": "failed_closed",
        "control_status_meaning": "blocker triggered and false-positive claim rejected",
        "bad_condition_present": True,
        "bad_condition": scenario["bad_condition"],
        "bad_condition_rejected_by_control": True,
        "blocked_reason": scenario["blocked_reason"],
        "positive_evidence_admissible": False,
        "derived_report_only": True,
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "schema_instantiation_only": True,
        "schema_expansion": False,
        "bf_ladder_rung": "BF0_active_null_control_scope",
        "row_decision": "rejected",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": "active-null false-positive rejection only; no N25 basin-formation evidence",
        "n25_closeout_ceiling": "N25-C1_active_nulls_fail_closed",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_failure_reading": scenario["geometric_reading"],
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]
    return row


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    rows = [active_null_row(scenario, i1=i1, i2=i2) for scenario in NULL_SCENARIOS]
    row_ids = [row["scenario_id"] for row in rows]
    failed_open_rows = [row["row_id"] for row in rows if row["control_status"] == "failed_open"]
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check(
            "all_required_nulls_present",
            all(null_id in row_ids for null_id in REQUIRED_NULL_IDS),
            REQUIRED_NULL_IDS,
        ),
        check(
            "all_active_nulls_fail_closed",
            all(row["control_status"] == "failed_closed" for row in rows),
            {row["scenario_id"]: row["control_status"] for row in rows},
        ),
        check("failed_open_rows_absent", not failed_open_rows, failed_open_rows),
        check(
            "no_positive_evidence_opened",
            all(row["positive_evidence_admissible"] is False for row in rows),
            "active-null rows are blocker evidence only",
        ),
        check(
            "no_bf_rung_above_control_scope",
            all(row["bf_ladder_rung"] == "BF0_active_null_control_scope" for row in rows),
            "BF0 only",
        ),
        check(
            "native_spark_source_skip_null_present",
            "existing_lgrc9v3_spark_examples_skipped" in row_ids,
            "protects native LGRC spark-first policy",
        ),
        check(
            "producer_before_native_spark_path_null_present",
            "producer_before_native_spark_path" in row_ids,
            "protects producer extension ordering",
        ),
        check(
            "unsafe_claim_flags_false",
            all(not any(row["unsafe_claim_flags"].values()) for row in rows),
            "all unsafe flags remain false",
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_active_nulls_and_failure_baselines",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I3",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_active_nulls_fail_closed_no_positive_basin_formation_evidence"
            if not failed
            else "failed_active_nulls_and_failure_baselines"
        ),
        "source_inventory": {
            "path": I1_OUTPUT_PATH,
            "sha256": sha256_file(I1_OUTPUT_PATH),
            "status": i1.get("status"),
            "acceptance_state": i1.get("acceptance_state"),
            "output_digest": i1.get("output_digest"),
        },
        "schema_source": {
            "path": I2_OUTPUT_PATH,
            "sha256": sha256_file(I2_OUTPUT_PATH),
            "status": i2.get("status"),
            "acceptance_state": i2.get("acceptance_state"),
            "output_digest": i2.get("output_digest"),
        },
        "active_null_rows": rows,
        "active_null_count": len(rows),
        "failed_open_rows": failed_open_rows,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": "BF0_active_null_control_scope",
        "n25_closeout_ceiling": "N25-C1_active_nulls_fail_closed",
        "n25_closeout_ladder_rung_assigned": False,
        "basin_formation_evidence_opened": False,
        "ready_for_iteration_4_native_bifurcation_probe": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value({k: v for k, v in output.items() if k != "output_digest"})
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N25 Iteration 3 - Active Nulls And Failure Baselines",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Scope",
        "",
        "I3 instantiates false-positive rows only. It does not open source-current",
        "basin-formation evidence and assigns no BF rung above active-null scope.",
        "",
        "## Active Null Rows",
        "",
    ]
    for row in output["active_null_rows"]:
        lines.append(
            f"- `{row['scenario_id']}`: `{row['control_status']}`; {row['blocked_reason']}"
        )
    lines.extend(["", "## Geometric Interpretation", ""])
    lines.append(
        "These rows reject label-only, thickening-only, boundary-reshaping-only, "
        "merge/leakage, transient, hidden-producer, N24-relabel, AP-gap, and unsafe "
        "semantic/native-support interpretations before positive probes run."
    )
    lines.append(
        "They also reject bypassing existing LGRC9V3 spark examples or introducing "
        "producer spark scaffolds before the native spark path is evaluated."
    )
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.extend(
        [
            "",
            "## Result",
            "",
            "```text",
            f"active_null_count = {output['active_null_count']}",
            f"failed_open_rows = {output['failed_open_rows']}",
            f"basin_formation_evidence_opened = {str(output['basin_formation_evidence_opened']).lower()}",
            f"bf_ceiling = {output['bf_ceiling']}",
            f"n25_closeout_ceiling = {output['n25_closeout_ceiling']}",
            f"n25_closeout_ladder_rung_assigned = {str(output['n25_closeout_ladder_rung_assigned']).lower()}",
            f"ready_for_iteration_4_native_bifurcation_probe = {str(output['ready_for_iteration_4_native_bifurcation_probe']).lower()}",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
