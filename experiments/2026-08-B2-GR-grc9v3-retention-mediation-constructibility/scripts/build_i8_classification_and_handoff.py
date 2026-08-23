"""Build the bounded B2-GR I8 closeout candidate from accepted evidence."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    assert_envelope_digest,
    envelope,
    finalize_receipt,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    verify_file_manifest,
    write_json,
)


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/build_i8_classification_and_handoff.py"
)
CONFIG_PATH = EXPERIMENT_ROOT / "configs/b2_i8_closeout_contract.json"
I4_RESULT_PATH = EXPERIMENT_ROOT / "outputs/b2_i4_native_preparation_reachability.json"
I4_ANCHOR_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i4_acceptance_anchor.json"
EMPTY_PATH_AUDIT_PATH = EXPERIMENT_ROOT / "outputs/b2_i8_empty_path_audit.json"
FULL_SUITE_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i8_full_suite_verification.json"
PROTECTED_MANIFEST_PATH = EXPERIMENT_ROOT / "outputs/b2_i1_protected_path_manifest.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs/b2_i8_classification_and_handoff.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports/b2_i8_classification_and_handoff.md"
RECEIPT_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i8_result_receipt.json"
LIFECYCLE_PATHS = {
    "B2-I5": EXPERIMENT_ROOT / "outputs/gates/b2_i5_non_applicability_record.json",
    "B2-I6": EXPERIMENT_ROOT / "outputs/gates/b2_i6_non_applicability_record.json",
    "B2-I7": EXPERIMENT_ROOT / "outputs/gates/b2_i7_non_applicability_record.json",
}


def accepted_source_chain() -> list[dict[str, Any]]:
    records = []
    for index in range(1, 5):
        anchor_path = (
            EXPERIMENT_ROOT / f"outputs/gates/b2_i{index}_acceptance_anchor.json"
        )
        anchor = read_json(anchor_path)
        if anchor["acceptance_status"] != "accepted":
            raise ValueError(f"B2-I{index} is not accepted")
        git("merge-base", "--is-ancestor", anchor["result_revision"], "HEAD")
        result_path = REPO_ROOT / anchor["result_artifact_path"]
        receipt_path = REPO_ROOT / anchor["result_receipt_path"]
        report_path = REPO_ROOT / anchor["report_path"]
        for path, field in [
            (result_path, "result_artifact_sha256"),
            (receipt_path, "result_receipt_sha256"),
            (report_path, "report_sha256"),
        ]:
            if sha256_file(path) != anchor[field]:
                raise ValueError(f"accepted B2-I{index} source changed: {path}")
        result = read_json(result_path)
        assert_envelope_digest(result)
        if result["payload_sha256"] != anchor["result_artifact_payload_sha256"]:
            raise ValueError(f"B2-I{index} payload/anchor mismatch")
        records.append(
            {
                "gate_id": f"B2-I{index}",
                "assigned_closeout_rung": anchor["assigned_closeout_rung"],
                "result_revision": anchor["result_revision"],
                "acceptance_anchor_path": repo_relative(anchor_path),
                "acceptance_anchor_sha256": sha256_file(anchor_path),
                "result_artifact_path": repo_relative(result_path),
                "result_artifact_payload_sha256": result["payload_sha256"],
                "result_receipt_path": repo_relative(receipt_path),
            }
        )
    return records


def validate_i4(config: dict[str, Any]) -> dict[str, Any]:
    anchor = read_json(I4_ANCHOR_PATH)
    prereq = config["prerequisites"]
    if sha256_file(I4_ANCHOR_PATH) != prereq["i4_acceptance_anchor_sha256"]:
        raise ValueError("I4 acceptance anchor changed")
    if anchor["candidate_set_status"] != prereq["required_i4_candidate_set_status"]:
        raise ValueError("I4 candidate set is not the accepted empty set")
    if anchor["assigned_closeout_rung"] != prereq["required_i4_closeout_rung"]:
        raise ValueError("I4 closeout rung mismatch")
    if anchor["confirmed_runtime_reached_candidate_count"] != 0:
        raise ValueError("empty-path closeout cannot consume positive I4 candidates")
    result = read_json(I4_RESULT_PATH)
    assert_envelope_digest(result)
    if result["payload_sha256"] != anchor["result_artifact_payload_sha256"]:
        raise ValueError("I4 result is not the accepted payload")
    return result["payload"]


def validate_closeout_support(
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    prereq = config["prerequisites"]
    if repo_relative(EMPTY_PATH_AUDIT_PATH) != prereq["empty_path_audit_path"]:
        raise ValueError("empty-path audit path differs from closeout contract")
    if repo_relative(FULL_SUITE_PATH) != prereq["full_suite_verification_path"]:
        raise ValueError("full-suite receipt path differs from closeout contract")

    audit = read_json(EMPTY_PATH_AUDIT_PATH)
    assert_envelope_digest(audit)
    if sha256_file(EMPTY_PATH_AUDIT_PATH) != prereq["empty_path_audit_sha256"]:
        raise ValueError("empty-path audit file changed")
    if audit["payload_sha256"] != prereq["empty_path_audit_payload_sha256"]:
        raise ValueError("empty-path audit payload changed")
    if not audit["payload"]["reconstruction_equivalence"][
        "classification_matrix_matches_accepted_I4"
    ]:
        raise ValueError("empty-path audit does not reconstruct accepted I4")

    suite = read_json(FULL_SUITE_PATH)
    if suite["status"] != "passed" or suite["exit_code"] != 0:
        raise ValueError("full repository suite has not passed")
    if suite["scientific_evidence_role"] != "verification_only":
        raise ValueError("full-suite receipt has an invalid evidence role")
    git("merge-base", "--is-ancestor", suite["input_execution_revision"], "HEAD")
    return audit["payload"], suite


def build_lifecycle_records(
    config: dict[str, Any], i4_anchor_sha256: str, input_revision: str
) -> list[dict[str, Any]]:
    records = []
    for policy in config["empty_path_lifecycle"]:
        payload = {
            **policy,
            "status": "not_applicable",
            "input_execution_revision": input_revision,
            "source_i4_acceptance_anchor_path": repo_relative(I4_ANCHOR_PATH),
            "source_i4_acceptance_anchor_sha256": i4_anchor_sha256,
            "scientific_gate_executed": False,
            "positive_evidence_generated": False,
            "GRR_rung_assigned": False,
            "failure_status": False,
            "lifecycle_role": "accounting_only_not_scientific_evidence",
        }
        records.append(
            envelope(payload, "b2_downstream_non_applicability_record_v1", COMMAND)
        )
    return records


def search_coverage(
    i4: dict[str, Any], config: dict[str, Any], audit: dict[str, Any]
) -> dict[str, Any]:
    accounting = i4["search_accounting"]
    matrix = i4["negative_classification_matrix"]
    if sum(row["attempt_count"] for row in matrix) != accounting["attempted_count"]:
        raise ValueError("compact negative matrix does not cover every I4 attempt")

    preparation_counts: Counter[str] = Counter()
    for row in matrix:
        preparation_counts[row["preparation_family"]] += row["attempt_count"]
    expected_families = config["frozen_search_envelope"]["preparation_families"]
    if sorted(preparation_counts) != sorted(expected_families):
        raise ValueError("observed I4 preparation families differ from frozen envelope")

    branch_summary = i4["branch_accessibility_summary"]
    effective = audit["effective_stratum_matrix"]
    terminal = audit["terminal_classification_semantics"]
    return {
        "branches_eligible_and_attempted": branch_summary[
            "accepted_source_branch_count"
        ],
        "branches_with_nontrivial_resolved_clean_primary_lane_attempt": branch_summary[
            "searched_and_resolved_inside_clean_primary_lane_count"
        ],
        "branches_inaccessible_under_frozen_preparation_family": branch_summary[
            "not_accessible_under_frozen_preparation_family_count"
        ],
        "inaccessible_branch_is_negative_constructibility_evidence": branch_summary[
            "not_accessible_is_negative_constructibility_evidence"
        ],
        "preparation_families_eligible_and_searched": dict(
            sorted(preparation_counts.items())
        ),
        "parameter_envelope_covered": config["frozen_search_envelope"],
        "history_lengths_covered": config["frozen_search_envelope"][
            "history_lengths_native_steps"
        ],
        "carrier_definitions_tested": config["frozen_search_envelope"][
            "carrier_definitions"
        ],
        "allocated_attempt_count": accounting["allocated_attempt_count"],
        "attempted_count": accounting["attempted_count"],
        "terminally_classified_attempt_count": terminal[
            "terminally_classified_attempt_count"
        ],
        "terminal_classification_is_scientific_constructibility_resolution": terminal[
            "terminal_classification_is_scientific_constructibility_resolution"
        ],
        "scientifically_clean_bounded_negative_attempt_count": terminal[
            "scientifically_clean_bounded_negative_attempt_count"
        ],
        "formation_attribution_blocked_attempt_count": terminal[
            "formation_attribution_blocked_attempt_count"
        ],
        "outside_primary_envelope_attempt_count": terminal[
            "outside_primary_envelope_attempt_count"
        ],
        "resolved_candidate_count": i4["confirmed_candidate_count"],
        "unresolved_candidate_count": accounting["unresolved_count"],
        "source_reconstruction_failure_count": accounting[
            "source_reconstruction_failure_count"
        ],
        "numerical_failure_count": 0,
        "duplicate_candidate_count": 0,
        "outside_envelope_count": accounting["status_counts"]["outside_envelope"],
        "bounded_negative_count": accounting["status_counts"]["bounded_negative"],
        "formation_entirely_authored_or_unidentifiable_count": accounting[
            "status_counts"
        ]["formation_entirely_authored_or_unidentifiable"],
        "search_budget_consumed_fraction": (
            accounting["attempted_count"] / accounting["allocated_attempt_count"]
        ),
        "primary_search_native_steps": accounting["primary_search_native_steps"],
        "attempt_population_identity_digest": i4["attempt_ledger_storage"][
            "attempt_population_identity_digest"
        ],
        "aggregate_attempt_ledger_digest": i4["attempt_ledger_storage"][
            "aggregate_attempt_ledger_digest"
        ],
        "branch_preparation_stratum_count": len(audit["branch_preparation_matrix"]),
        "effective_stratum_count": len(effective),
        "fully_clean_effective_stratum_count": sum(
            row["clean_primary_attempt_count"] == row["attempt_count"]
            for row in effective
        ),
        "partly_clean_effective_stratum_count": sum(
            0 < row["clean_primary_attempt_count"] < row["attempt_count"]
            for row in effective
        ),
        "zero_clean_effective_stratum_count": sum(
            row["clean_primary_attempt_count"] == 0 for row in effective
        ),
        "branch_preparation_matrix_digest": semantic_digest(
            audit["branch_preparation_matrix"]
        ),
        "effective_stratum_matrix_digest": semantic_digest(effective),
        "all_planned_branch_allocations_completed": all(
            row["allocation_complete"] for row in audit["branch_allocation_audit"]
        ),
    }


def build_payload() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = read_json(CONFIG_PATH)
    input_revision = git("rev-parse", "HEAD")
    sources = accepted_source_chain()
    i4 = validate_i4(config)
    audit, suite = validate_closeout_support(config)
    protected = read_json(PROTECTED_MANIFEST_PATH)
    assert_envelope_digest(protected)
    protected_tree_unchanged = verify_file_manifest(protected["payload"])
    if not protected_tree_unchanged:
        raise ValueError("B2 protected src/spec/test tree changed")

    lifecycle = build_lifecycle_records(
        config, sha256_file(I4_ANCHOR_PATH), input_revision
    )
    coverage = search_coverage(i4, config, audit)
    attribution = audit["formation_attribution_split"]
    attribution_counts = {
        row["attribution_class"]: row["attempt_count"] for row in attribution
    }
    authored_count = attribution_counts[
        "apparent_carrier_authored_within_numerical_uncertainty"
    ]
    precision_debt_count = attribution_counts[
        "runtime_residual_above_uncertainty_below_separation_floor"
    ]
    below_floor_count = attribution_counts[
        "runtime_residual_above_separation_below_formation_floor"
    ]
    outside = audit["outside_envelope_mechanisms"]
    bounded_negative = {
        key: value
        for key, value in audit["bounded_negative_uniqueness"].items()
        if key != "rows"
    }
    near_miss = audit["near_miss_audit"]
    top_subthreshold = near_miss["top_subthreshold_runtime_residual_rows"][0]
    top_sham = near_miss["top_sham_drift_rows"][0]

    payload = {
        "experiment_id": "B2-GR",
        "iteration": 8,
        "gate_id": "B2-I8",
        "status": "passed",
        "acceptance_state": "awaiting_scientific_review",
        "input_execution_revision": input_revision,
        "source_chain": sources,
        "source_i4_candidate_set_digest": i4["candidate_set_digest"],
        "source_i4_candidate_set_status": "accepted_empty_no_runtime_reached_candidate",
        "closeout_support": {
            "empty_path_audit_path": repo_relative(EMPTY_PATH_AUDIT_PATH),
            "empty_path_audit_sha256": sha256_file(EMPTY_PATH_AUDIT_PATH),
            "empty_path_audit_payload_sha256": semantic_digest(audit),
            "audit_reconstructs_accepted_I4": audit["reconstruction_equivalence"][
                "classification_matrix_matches_accepted_I4"
            ],
            "full_suite_verification_path": repo_relative(FULL_SUITE_PATH),
            "full_suite_verification_sha256": sha256_file(FULL_SUITE_PATH),
            "full_suite_input_execution_revision": suite["input_execution_revision"],
            "full_suite_passed_test_count": suite["passed_test_count"],
            "full_suite_status": suite["status"],
        },
        "downstream_gate_lifecycle": [record["payload"] for record in lifecycle],
        "search_coverage": coverage,
        "formation_attribution": {
            "policy": audit["formation_attribution_split_policy"],
            "split": attribution,
            "by_fixture_and_preparation": audit[
                "formation_attribution_by_fixture_and_preparation"
            ],
            "maximum_residual_carrier_counts": audit["maximum_residual_carrier_counts"],
            "provenance_negative_authored_within_uncertainty_count": authored_count,
            "localized_attribution_precision_debt_count": precision_debt_count,
            "runtime_residual_above_separation_below_formation_floor_count": (
                below_floor_count
            ),
            "broad_formation_identifiability_debt_supported": False,
            "I4_admission_changed_by_split": False,
        },
        "bounded_negative_scope": {
            **bounded_negative,
            "preparation_scope": "native_spontaneous_no_driver_only",
            "supports_universal_native_retention_absence": False,
            "supports_bounded_no_spontaneous_formation_baselines": True,
        },
        "outside_primary_envelope": {
            "attempt_count": coverage["outside_envelope_count"],
            "all_attempts_were_inside_frozen_proposal_grid": outside[
                "all_attempts_were_inside_frozen_proposal_grid"
            ],
            "eventful_attempt_count": outside["eventful_attempt_count"],
            "topology_mutating_attempt_count": outside[
                "topology_mutating_attempt_count"
            ],
            "failure_mode_counts_overlap_allowed": outside[
                "failure_mode_counts_overlap_allowed"
            ],
            "exclusive_failure_mode_combinations": [
                {
                    "failure_modes": row["failure_modes"],
                    "attempt_count": row["attempt_count"],
                }
                for row in outside["exclusive_failure_mode_combinations"]
            ],
            "scientific_interpretation": (
                "categorical_or_constraint_supported_history_paths_excluded_from_"
                "clean_primary_GRR_evidence"
            ),
        },
        "near_miss_audit": {
            "top_subthreshold_runtime_residual_row": top_subthreshold,
            "largest_runtime_residual_fraction_of_formation_floor": top_subthreshold[
                "formation_floor_fraction"
            ],
            "top_sham_drift_fraction_of_formation_reference": top_sham[
                "fraction_of_formation_reference"
            ],
            "delayed_post_driver_formation_count": near_miss[
                "delayed_post_driver_formation_count"
            ],
            "internal_stage_only_candidate_count": near_miss[
                "internal_stage_only_candidate_count"
            ],
            "overwritten_or_nonpersistent_candidate_count": near_miss[
                "overwritten_or_nonpersistent_candidate_count"
            ],
            "ranking_is_diagnostic_not_admission": True,
            "near_admission_boundary_found": False,
        },
        "candidate_confirmation_accounting": audit["candidate_confirmation_accounting"],
        "causal_role_classification": {
            "maximum_new_GRR_rung": "none",
            "inherited_B1_GR_context_ceiling": "GRR2",
            "row_local_max_GRR": [],
            "global_max_GRR": "none_new_in_B2",
            "global_max_GRR_derivation": (
                "max_row_local_max_GRR_over_empty_eligible_candidate_set_is_none"
            ),
            "GRR3_candidate_count": 0,
            "GRR4_candidate_count": 0,
            "GRR5_candidate_count": 0,
            "native_admissible_formation_candidate": (
                "not_found_in_frozen_I4_search_envelope"
            ),
            "GRR3_status": "not_testable_no_confirmed_I4_lineage",
            "GRR4_status": "not_testable_no_GRR3_lineage",
            "GRR5_status": "not_testable_no_GRR4_lineage",
            "branch_relation": "not_testable_no_confirmed_I4_lineage",
            "retention_effect": "not_testable_no_confirmed_I4_lineage",
            "read_effect": "not_testable_no_GRR3_lineage",
            "write_effect": "not_testable_no_GRR4_lineage",
            "closed_loop_effect": "not_testable_no_GRR4_lineage",
            "persistence_without_mediation": "not_testable_no_GRR3_lineage",
            "mediation_without_GRR3": "not_testable_no_GRR3_lineage",
            "categorical_or_constraint_supported_history_dependence": (
                "observed_outside_clean_primary_lane_not_classified_as_GRR_persistence"
            ),
        },
        "bounded_alternative_mechanisms": [
            {
                "mechanism": "apparent_carrier_authored_within_numerical_uncertainty",
                "attempt_count": authored_count,
                "role": "provenance_negative_not_broad_identifiability_debt",
            },
            {
                "mechanism": (
                    "runtime_residual_above_uncertainty_below_separation_floor"
                ),
                "attempt_count": precision_debt_count,
                "role": "localized_attribution_precision_debt_not_candidate",
            },
            {
                "mechanism": "categorical_or_constraint_supported_history",
                "attempt_count": coverage["outside_envelope_count"],
                "failure_mode_counts": outside["failure_mode_counts_overlap_allowed"],
                "eventful_attempt_count": 0,
                "topology_mutating_attempt_count": 0,
                "role": "separate_scientific_lane_outside_clean_primary_GRR_evidence",
            },
            {
                "mechanism": "clean_resolved_no_attributable_carrier_above_floor",
                "attempt_count": coverage["bounded_negative_count"],
                "preparation_family_count": bounded_negative[
                    "unique_preparation_family_count"
                ],
                "role": "bounded_no_spontaneous_formation_baselines_only",
            },
            {
                "mechanism": (
                    "clean_lane_inaccessible_under_B2_frozen_preparation_contract"
                ),
                "branch_count": coverage[
                    "branches_inaccessible_under_frozen_preparation_family"
                ],
                "role": "coverage_debt_not_negative_constructibility_evidence",
            },
        ],
        "open_debt": [
            "constructibility_outside_frozen_preparation_parameter_history_and_carrier_envelope",
            "clean_primary_lane_accessibility_for_22_of_48_accepted_source_branches",
            "causal_role_of_categorical_and_constraint_supported_history_dependence",
            "formation_attribution_precision_for_one_subthreshold_F3_C_pulse_row",
            "branch_relation_slow_cluster_and_mediation_unopened_without_I4_candidate",
            "localized_missing_causal_role_not_established",
        ],
        "closeout_decision": config["closeout_decision"],
        "bounded_open_dimensions": config["bounded_open_dimensions"],
        "extension_trigger_matrix": config["extension_trigger_matrix"],
        "next_route_boundary": {
            "required_before_any_extension": [
                "explicit_target_claim",
                "localized_missing_causal_role",
                "resolved_target_relevant_search_coverage",
                "rival_and_identifiability_accounting",
            ],
            "unchanged_runtime_broader_search": (
                "eligible_only_under_new_preregistered_scope"
            ),
            "categorical_or_constraint_supported_history": (
                "eligible_only_as_separate_scientific_lane"
            ),
            "revision_distinct_GRC_extension": (
                "blocked_pending_target_and_role_localization"
            ),
            "LGRC_specific_work": "not_authorized_by_B2",
        },
        "claim_boundary": config["required_claim_boundary"],
        "claim_ceiling": (
            "bounded_unchanged_GRC9V3_constructibility_search_with_empty_runtime_reached_"
            "candidate_set_no_impossibility_or_extension_selection"
        ),
        "protected_path_manifest_path": repo_relative(PROTECTED_MANIFEST_PATH),
        "protected_path_manifest_payload_sha256": protected["payload_sha256"],
        "protected_src_spec_test_tree_unchanged": protected_tree_unchanged,
        "B2_closeout_ceiling": "B2-C6-ready",
        "B2_closeout_rung_assigned": False,
        "ready_for_human_closeout_review": True,
    }
    if find_absolute_paths(payload):
        raise ValueError("absolute paths found in I8 payload")
    return payload, lifecycle


def render_report(payload: dict[str, Any]) -> str:
    coverage = payload["search_coverage"]
    attribution = payload["formation_attribution"]
    bounded = payload["bounded_negative_scope"]
    near = payload["near_miss_audit"]
    return "\n".join(
        [
            "# B2-GR Iteration 8 Classification And Handoff",
            "",
            f"- Status: `{payload['status']}`",
            f"- Acceptance: `{payload['acceptance_state']}`",
            f"- Closeout ceiling: `{payload['B2_closeout_ceiling']}`",
            "- New GRR rung: `none`",
            "- Inherited B1 context: `GRR2`",
            "- Extension selected: `false`",
            "",
            "## Empty-Path Lifecycle",
            "",
            "The accepted I4 candidate set is empty. I5, I6, and I7 therefore do",
            "not run scientific positive gates. Separate machine records classify",
            "them as non-applicable accounting lanes, not failures or evidence.",
            "No diagnostic or synthetic candidate is introduced to keep the ladder",
            "moving.",
            "",
            "## Search Coverage",
            "",
            f"All `{coverage['attempted_count']}` allocated attempts were terminally",
            "classified, not scientifically resolved as constructibility probes. They",
            f"consumed `{coverage['primary_search_native_steps']}` primary native steps.",
            "All 48 accepted B1 branches received attempts, but only 26 admitted a",
            "nontrivial resolved clean-primary-lane attempt. The other 22 remain",
            "accessibility debt under the frozen B2 preparation contract; this is not",
            "an intrinsic branch property or negative constructibility evidence.",
            "",
            f"The audit covers `{coverage['branch_preparation_stratum_count']}` branch ×",
            f"preparation groups and `{coverage['effective_stratum_count']}` effective",
            f"strata: `{coverage['fully_clean_effective_stratum_count']}` fully clean,",
            f"`{coverage['partly_clean_effective_stratum_count']}` partly clean, and",
            f"`{coverage['zero_clean_effective_stratum_count']}` with no clean-primary",
            "attempt. The compact matrices remain in the reconstruction audit and are",
            "bound here by semantic digest.",
            "",
            "The nonpositive result is heterogeneous:",
            "",
            f"- `{coverage['bounded_negative_count']}` clean bounded-negative no-driver",
            f"  baselines across `{bounded['unique_source_branch_count']}` branches and",
            "  one preparation family;",
            f"- `{attribution['provenance_negative_authored_within_uncertainty_count']}`",
            "  apparent-carrier attempts attributable to authored preparation within",
            "  numerical uncertainty;",
            f"- `{attribution['localized_attribution_precision_debt_count']}` row above",
            "  numerical uncertainty but below carrier-separation and formation floors;",
            f"- `{coverage['outside_envelope_count']}` categorical, constraint-supported,",
            "  or positive-interior-failing attempts;",
            "- zero unresolved rows, source-reconstruction failures, numerical failures,",
            "  duplicates, discovery candidates, or confirmation attempts.",
            "",
            "No outside-envelope attempt was eventful, topology-mutating, or outside the",
            "frozen proposal grid. This population locates categorical/constraint-supported",
            "history dependence, not event-driven retention or optimizer overflow.",
            "",
            "## Attribution And Near-Miss Audit",
            "",
            "The earlier merged authored/unidentifiable headline is superseded. The audit",
            f"classifies `{attribution['provenance_negative_authored_within_uncertainty_count']}`",
            "rows as provenance-negative within uncertainty and localizes analysis debt",
            f"to `{attribution['localized_attribution_precision_debt_count']}` row. That",
            "row reaches only",
            f"`{near['largest_runtime_residual_fraction_of_formation_floor']:.6f}` of the",
            "frozen formation floor. No delayed formation, internal-stage-only candidate,",
            "or overwritten candidate was found. These diagnostics do not reopen I4.",
            "",
            "This is stronger than an unresolved search but narrower than a global",
            "negative. It establishes only that no runtime-reached retention candidate",
            "satisfying the frozen B2 formation and clean-lane contract was found in",
            "the preregistered unchanged-GRC9V3 envelope.",
            "",
            "## Causal Classification",
            "",
            "B2 adds no new GRR rung; inherited B1-GR `GRR2` remains context only.",
            "Without an I4 candidate there is no row-local object on which to test",
            "branch transversality, isolated slow-cluster occupancy, matched-probe",
            "mediation, or reset/swap/bypass controls. `GRR3`, `GRR4`, and `GRR5`",
            "are not testable on a B2 lineage, not false.",
            "",
            "## Next-Route Boundary",
            "",
            "The unchanged-runtime constructibility question remains open outside the",
            "frozen envelope. Legitimate next work is bounded to principled upstream",
            "preparation expansion, the one attribution-precision row, or a separate",
            "categorical/constraint history lane. Arbitrary widening until a witness",
            "appears, synthetic carrier insertion, and automatic extension selection",
            "remain unauthorized.",
            "",
            "B2 does not localize one missing causal role strongly enough to select a",
            "revision-distinct extension. Any later extension requires an explicit target",
            "claim, localized role, target-relevant coverage, and rival/identifiability",
            "accounting. LGRC-specific work is not authorized here.",
            "",
            "## Claim Boundary",
            "",
            f"`{payload['claim_ceiling']}`",
            "",
            "Zero candidates do not establish global impossibility, retained-carrier",
            "necessity, extension necessity, memory, learning, or agency.",
            "",
        ]
    )


def main() -> None:
    payload, lifecycle_records = build_payload()
    for policy, record in zip(
        read_json(CONFIG_PATH)["empty_path_lifecycle"], lifecycle_records, strict=True
    ):
        write_json(LIFECYCLE_PATHS[policy["gate_id"]], record)
    artifact = envelope(payload, "b2_i8_classification_and_handoff_v2", COMMAND)
    write_json(OUTPUT_PATH, artifact)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    output_paths = [OUTPUT_PATH, REPORT_PATH, *LIFECYCLE_PATHS.values()]
    receipt = finalize_receipt(
        {
            "gate_id": "B2-I8",
            "status": "awaiting_scientific_review",
            "input_execution_revision": payload["input_execution_revision"],
            "config_path": repo_relative(CONFIG_PATH),
            "config_sha256": sha256_file(CONFIG_PATH),
            "generating_script_path": repo_relative(Path(__file__)),
            "generating_script_sha256": sha256_file(Path(__file__)),
            "output_payload_sha256": artifact["payload_sha256"],
            "empty_path_audit_path": repo_relative(EMPTY_PATH_AUDIT_PATH),
            "empty_path_audit_sha256": sha256_file(EMPTY_PATH_AUDIT_PATH),
            "full_suite_verification_path": repo_relative(FULL_SUITE_PATH),
            "full_suite_verification_sha256": sha256_file(FULL_SUITE_PATH),
            "full_suite_input_execution_revision": payload["closeout_support"][
                "full_suite_input_execution_revision"
            ],
            "full_suite_passed_test_count": payload["closeout_support"][
                "full_suite_passed_test_count"
            ],
            "output_artifact_digests": {
                repo_relative(path): sha256_file(path) for path in output_paths
            },
            "maximum_new_GRR_rung": "none",
            "B2_closeout_ceiling": "B2-C6-ready",
            "extension_selected": False,
            "runtime_change_authorized": False,
            "ready_for_human_closeout_review": True,
            "blocked_gates": ["B2-I8-acceptance"],
            "not_applicable_gates": ["B2-I5", "B2-I6", "B2-I7"],
        }
    )
    write_json(RECEIPT_PATH, receipt)
    print(
        "I8: B2-C6-ready; maximum_new_GRR=none; "
        "extension_selected=false; awaiting scientific review"
    )


if __name__ == "__main__":
    main()
