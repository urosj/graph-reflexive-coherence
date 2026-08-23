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
        anchor_path = EXPERIMENT_ROOT / f"outputs/gates/b2_i{index}_acceptance_anchor.json"
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
        record = envelope(payload, "b2_downstream_non_applicability_record_v1", COMMAND)
        records.append(record)
    return records


def search_coverage(i4: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    accounting = i4["search_accounting"]
    matrix = i4["negative_classification_matrix"]
    matrix_count = sum(row["attempt_count"] for row in matrix)
    if matrix_count != accounting["attempted_count"]:
        raise ValueError("compact negative matrix does not cover every I4 attempt")
    preparation_counts: Counter[str] = Counter()
    for row in matrix:
        preparation_counts[row["preparation_family"]] += row["attempt_count"]
    expected_families = config["frozen_search_envelope"]["preparation_families"]
    if sorted(preparation_counts) != sorted(expected_families):
        raise ValueError("observed I4 preparation families differ from the frozen envelope")
    branch_summary = i4["branch_accessibility_summary"]
    return {
        "branches_eligible_and_attempted": branch_summary["accepted_source_branch_count"],
        "branches_with_nontrivial_resolved_clean_primary_lane_attempt": branch_summary[
            "searched_and_resolved_inside_clean_primary_lane_count"
        ],
        "branches_inaccessible_under_frozen_preparation_family": branch_summary[
            "not_accessible_under_frozen_preparation_family_count"
        ],
        "inaccessible_branch_is_negative_constructibility_evidence": branch_summary[
            "not_accessible_is_negative_constructibility_evidence"
        ],
        "preparation_families_eligible_and_searched": dict(sorted(preparation_counts.items())),
        "parameter_envelope_covered": config["frozen_search_envelope"],
        "history_lengths_covered": config["frozen_search_envelope"][
            "history_lengths_native_steps"
        ],
        "carrier_definitions_tested": config["frozen_search_envelope"][
            "carrier_definitions"
        ],
        "allocated_attempt_count": accounting["allocated_attempt_count"],
        "attempted_count": accounting["attempted_count"],
        "resolved_attempt_count": accounting["resolved_count"],
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
        "full_path_failure_mode_counts": accounting["full_path_failure_mode_counts"],
        "attempt_population_identity_digest": i4["attempt_ledger_storage"][
            "attempt_population_identity_digest"
        ],
        "aggregate_attempt_ledger_digest": i4["attempt_ledger_storage"][
            "aggregate_attempt_ledger_digest"
        ],
    }


def build_payload() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = read_json(CONFIG_PATH)
    input_revision = git("rev-parse", "HEAD")
    sources = accepted_source_chain()
    i4 = validate_i4(config)
    protected = read_json(PROTECTED_MANIFEST_PATH)
    assert_envelope_digest(protected)
    protected_tree_unchanged = verify_file_manifest(protected["payload"])
    if not protected_tree_unchanged:
        raise ValueError("B2 protected src/spec/test tree changed")
    lifecycle = build_lifecycle_records(
        config, sha256_file(I4_ANCHOR_PATH), input_revision
    )
    coverage = search_coverage(i4, config)
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
        "downstream_gate_lifecycle": [record["payload"] for record in lifecycle],
        "search_coverage": coverage,
        "causal_role_classification": {
            "maximum_new_GRR_rung": "none",
            "inherited_B1_GR_context_ceiling": "GRR2",
            "GRR3_candidate_count": 0,
            "GRR4_candidate_count": 0,
            "GRR5_candidate_count": 0,
            "retention_effect": "not_testable_no_runtime_reached_I4_candidate",
            "read_effect": "not_testable_no_GRR3_lineage",
            "write_effect": "not_established_in_B2",
            "closed_loop_effect": "not_established_in_B2",
            "persistence_without_mediation": "not_observed_on_B2_candidate_lineage",
            "mediation_without_GRR3": "not_observed_on_B2_candidate_lineage",
        },
        "bounded_alternative_mechanisms": [
            {
                "mechanism": "directly_authored_or_unidentifiable_apparent_carrier",
                "attempt_count": coverage[
                    "formation_entirely_authored_or_unidentifiable_count"
                ],
                "role": "typed_nonpositive_result_not_native_formation",
            },
            {
                "mechanism": "eventful_categorical_or_constraint_supported_history",
                "attempt_count": coverage["outside_envelope_count"],
                "failure_mode_counts": coverage["full_path_failure_mode_counts"],
                "role": "observed_alternative_path_family_outside_clean_primary_lane",
            },
            {
                "mechanism": "clean_resolved_no_attributable_carrier_above_floor",
                "attempt_count": coverage["bounded_negative_count"],
                "role": "bounded_negative_inside_frozen_clean_lane_only",
            },
            {
                "mechanism": "clean_lane_inaccessible_branch",
                "branch_count": coverage[
                    "branches_inaccessible_under_frozen_preparation_family"
                ],
                "role": "coverage_debt_not_negative_constructibility_evidence",
            },
        ],
        "open_debt": [
            "constructibility_outside_frozen_preparation_parameter_history_and_carrier_envelope",
            "clean_primary_lane_accessibility_for_22_of_48_accepted_source_branches",
            "causal_role_of_eventful_and_constraint_supported_history_dependence",
            "branch_relation_slow_cluster_and_mediation_unopened_without_I4_candidate",
            "localized_missing_causal_role_not_established",
        ],
        "closeout_decision": config["closeout_decision"],
        "next_route_boundary": {
            "required_before_any_extension": [
                "explicit_target_claim",
                "localized_missing_causal_role",
                "resolved_target_relevant_search_coverage",
                "rival_and_identifiability_accounting",
            ],
            "unchanged_runtime_broader_search": "eligible_only_under_new_preregistered_scope",
            "revision_distinct_GRC_extension": "blocked_pending_target_and_role_localization",
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
    return "\n".join(
        [
            "# B2-GR Iteration 8 Classification And Handoff",
            "",
            f"- Status: `{payload['status']}`",
            f"- Acceptance: `{payload['acceptance_state']}`",
            f"- Closeout ceiling: `{payload['B2_closeout_ceiling']}`",
            "- New GRR rung: `none`",
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
            f"All `{coverage['attempted_count']}` allocated attempts resolved, consuming",
            f"`{coverage['primary_search_native_steps']}` primary native steps. All 48",
            "accepted B1 branches received attempts, but only 26 admitted a nontrivial",
            "resolved clean-primary-lane attempt. The other 22 remain accessibility",
            "debt and are not negative constructibility evidence.",
            "",
            "The nonpositive result is heterogeneous:",
            "",
            f"- `{coverage['bounded_negative_count']}` clean bounded-negative attempts;",
            f"- `{coverage['formation_entirely_authored_or_unidentifiable_count']}` apparent-carrier attempts whose runtime-generated component was not identifiable;",
            f"- `{coverage['outside_envelope_count']}` eventful, categorical, constraint-supported, or otherwise outside-envelope attempts;",
            "- zero unresolved rows, source-reconstruction failures, numerical failures, duplicates, or confirmed candidates.",
            "",
            "This is stronger than an unresolved search but narrower than a global",
            "negative. It establishes only that no runtime-reached retention candidate",
            "satisfying the frozen B2 formation and clean-lane contract was found in",
            "the preregistered unchanged-GRC9V3 envelope.",
            "",
            "## Causal Classification",
            "",
            "B2 adds no GRR rung above the inherited B1-GR `GRR2` context. Without an",
            "I4 candidate there is no row-local object on which to test branch",
            "transversality, isolated slow-cluster occupancy, matched-probe mediation,",
            "or reset/swap/bypass controls. Retention, mediation, write-back, and a",
            "closed loop remain unsupported in B2.",
            "",
            "## Next-Route Boundary",
            "",
            "The unchanged-runtime constructibility question remains open outside the",
            "frozen envelope. B2 identifies analysis and accessibility debt, but it",
            "does not localize one missing causal role strongly enough to select a",
            "revision-distinct extension. Any later extension requires an explicit",
            "target claim, localized role, target-relevant coverage, and rival and",
            "identifiability accounting. LGRC-specific work is not authorized here.",
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
    artifact = envelope(payload, "b2_i8_classification_and_handoff_v1", COMMAND)
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
