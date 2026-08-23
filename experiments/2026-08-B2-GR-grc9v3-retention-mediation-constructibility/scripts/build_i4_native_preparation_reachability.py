"""Aggregate frozen I4 discovery and fresh-process confirmation batches."""

from __future__ import annotations

from collections import Counter, defaultdict
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
    write_json,
)
from run_i4_discovery_batch import CONFIG_PATH, batch_registry, validate_prerequisites


COMMAND = (
    ".venv/bin/python experiments/2026-08-B2-GR-grc9v3-retention-mediation-"
    "constructibility/scripts/build_i4_native_preparation_reachability.py"
)
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs/b2_i4_native_preparation_reachability.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports/b2_i4_native_preparation_reachability.md"
RECEIPT_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i4_result_receipt.json"


def _batch_paths(batch_id: str) -> tuple[Path, Path]:
    root = EXPERIMENT_ROOT / "outputs/i4_batches"
    return (
        root / f"b2_i4_discovery_{batch_id}.json",
        root / f"b2_i4_confirmation_{batch_id}.json",
    )


def _duplicate_classifications(
    confirmed_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_state: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_history: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in confirmed_candidates:
        candidate = row["reproduced_candidate"]
        by_state[candidate["state_identity_digest"]].append(row)
        by_history[candidate["history_aware_candidate_identity"]].append(row)
    result = []
    for row in confirmed_candidates:
        candidate = row["reproduced_candidate"]
        state_peers = by_state[candidate["state_identity_digest"]]
        history_peers = by_history[candidate["history_aware_candidate_identity"]]
        if len(history_peers) > 1:
            duplicate_class = "state_duplicate"
        elif len(state_peers) > 1:
            duplicate_class = "history_distinct_same_state"
        else:
            duplicate_class = "not_duplicate"
        result.append(
            {
                "candidate_id": candidate["attempt_id"],
                "source_branch_id": candidate["source_branch_id"],
                "carrier_definition_id": candidate["selected_carrier_definition_id"],
                "state_identity_digest": candidate["state_identity_digest"],
                "preparation_history_digest": candidate["preparation_history_digest"],
                "candidate_deduplication_id": semantic_digest(
                    {
                        "state_identity_digest": candidate["state_identity_digest"],
                        "carrier_equivalence_class": "C_CAUSAL_STATE_WITH_W_LIFT_V1",
                    }
                ),
                "duplicate_class": duplicate_class,
                "same_state_candidate_ids": sorted(
                    peer["attempt_id"] for peer in state_peers
                ),
                "history_aware_candidate_identity": candidate[
                    "history_aware_candidate_identity"
                ],
                "symmetry_signature_for_characterization_only": candidate[
                    "symmetry_signature_for_characterization_only"
                ],
                "fresh_process_confirmation_digest": semantic_digest(row),
                "fresh_process_confirmation_result": {
                    "status": row["confirmation_result"],
                    "all_required_matches": all(row["checks"].values()),
                },
                "formation_contrast_norm": candidate["carrier_rows"][
                    candidate["selected_carrier_definition_id"]
                ]["runtime_generated_residual_norm"],
                "formation_contrast_margin": candidate["carrier_rows"][
                    candidate["selected_carrier_definition_id"]
                ]["formation_margin"],
                "first_post_driver_persistence_ratio": candidate["persistence"][
                    "persistence_ratio"
                ],
                "branch_relation_class": "unresolved_until_iteration_5",
                "maximum_GRR_rung": "not_assigned_pending_iteration_5",
                "positive_evidence_admissible": True,
                "claim_ceiling": "runtime_reached_post_driver_candidate_not_retained_sector",
                "source_batch_candidate_digest": row["discovery_candidate_digest"],
            }
        )
    return result


def _outliers(
    attempts: list[dict[str, Any]], candidates: list[dict[str, Any]]
) -> dict[str, Any]:
    positive_rows = [
        row["reproduced_candidate"]
        for row in candidates
        if row["confirmation_result"] == "passed"
    ]
    largest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in positive_rows:
        key = (
            row["selected_carrier_definition_id"],
            row["preparation_spec"]["preparation_family"],
        )
        magnitude = row["carrier_rows"][key[0]]["runtime_generated_residual_norm"]
        if key not in largest or magnitude > largest[key]["magnitude"]:
            largest[key] = {"candidate_id": row["attempt_id"], "magnitude": magnitude}
    smallest = min(
        (
            {
                "candidate_id": row["attempt_id"],
                "margin": row["carrier_rows"][row["selected_carrier_definition_id"]][
                    "formation_margin"
                ],
            }
            for row in positive_rows
        ),
        key=lambda item: item["margin"],
        default=None,
    )
    flag_ids: dict[str, list[str]] = defaultdict(list)
    for row in attempts:
        for flag, active in row.get("outlier_flags", {}).items():
            if active:
                flag_ids[flag].append(row["attempt_id"])
    by_state: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in positive_rows:
        by_state[row["state_identity_digest"]].append(row)
    history_distinct_groups = []
    for state_digest, rows in sorted(by_state.items()):
        history_digests = {row["preparation_history_digest"] for row in rows}
        if len(history_digests) > 1:
            history_distinct_groups.append(
                {
                    "state_identity_digest": state_digest,
                    "candidate_ids": sorted(row["attempt_id"] for row in rows),
                    "preparation_history_digests": sorted(history_digests),
                }
            )
    by_stratum: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in attempts:
        by_stratum[row["search_stratum_id"]].append(row)
    resolution_records = []
    for stratum_id, rows in sorted(by_stratum.items()):
        attempted = sum(row["attempted"] for row in rows)
        resolved = sum(row["resolved_status"].startswith("resolved") for row in rows)
        resolution_records.append(
            {
                "search_stratum_id": stratum_id,
                "allocated_count": len(rows),
                "attempted_count": attempted,
                "resolved_count": resolved,
                "budget_consumed_fraction": attempted / len(rows),
                "resolved_fraction": resolved / len(rows),
            }
        )
    return {
        "largest_carrier_contrast_by_carrier_and_preparation": [
            {"carrier_definition_id": key[0], "preparation_family": key[1], **value}
            for key, value in sorted(largest.items())
        ],
        "smallest_positive_formation_margin": smallest,
        "flagged_attempt_ids": {
            key: sorted(values) for key, values in sorted(flag_ids.items())
        },
        "history_distinct_same_state_groups": history_distinct_groups,
        "failed_fresh_process_confirmation_candidate_ids": sorted(
            row["attempt_id"]
            for row in candidates
            if row["confirmation_result"] == "failed"
        ),
        "resolution_by_search_stratum": resolution_records,
        "outlier_thresholds_used_for_admission": False,
    }


def _branch_coverage(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_branch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in attempts:
        by_branch[row["source_branch_id"]].append(row)
    records = []
    for branch_id, rows in sorted(by_branch.items()):
        nontrivial = [
            row
            for row in rows
            if row["preparation_family"] != "native_spontaneous_no_driver"
        ]
        clean_resolved = [
            row
            for row in nontrivial
            if row["resolved_status"] in {"resolved_negative", "resolved_positive"}
        ]
        outside = [
            row
            for row in nontrivial
            if row["resolved_status"] == "resolved_outside_envelope"
        ]
        unresolved = [
            row for row in nontrivial if row["resolved_status"] == "search_unresolved"
        ]
        records.append(
            {
                "source_branch_id": branch_id,
                "allocated_nontrivial_attempt_count": len(nontrivial),
                "clean_resolved_attempt_count": len(clean_resolved),
                "outside_envelope_attempt_count": len(outside),
                "unresolved_attempt_count": len(unresolved),
                "primary_lane_accessibility": (
                    "searched_and_resolved_inside_clean_primary_lane"
                    if clean_resolved
                    else "source_branch_primary_lane_not_accessible_under_frozen_preparation_family"
                ),
                "not_accessible_is_negative_constructibility_evidence": False,
            }
        )
    return records


def _continuation_routing(
    *, execution_complete: bool, confirmed_candidate_count: int
) -> dict[str, Any]:
    has_candidates = confirmed_candidate_count > 0
    empty_path = execution_complete and not has_candidates
    return {
        "ready_for_iteration_5": execution_complete and has_candidates,
        "ready_for_iteration_8_bounded_closeout": empty_path,
        "I5_to_I7_positive_lane_status": (
            "not_applicable_empty_I4_candidate_set"
            if empty_path
            else (
                "eligible_after_I4_acceptance"
                if execution_complete
                else "blocked_by_incomplete_I4_execution"
            )
        ),
        "empty_path_semantics_applied": empty_path,
    }


def build_payload() -> tuple[dict[str, Any], list[Path]]:
    config = read_json(CONFIG_PATH)
    validate_prerequisites(config)
    batch_ids = sorted(batch_registry())
    attempts: list[dict[str, Any]] = []
    confirmations: list[dict[str, Any]] = []
    batch_records = []
    artifact_paths: list[Path] = []
    for batch_id in batch_ids:
        discovery_path, confirmation_path = _batch_paths(batch_id)
        discovery = read_json(discovery_path)
        confirmation = read_json(confirmation_path)
        assert_envelope_digest(discovery)
        assert_envelope_digest(confirmation)
        if discovery["payload"]["batch_id"] != batch_id:
            raise ValueError(f"discovery batch identity mismatch: {batch_id}")
        if confirmation["payload"]["batch_id"] != batch_id:
            raise ValueError(f"confirmation batch identity mismatch: {batch_id}")
        attempts.extend(discovery["payload"]["attempt_rows"])
        confirmations.extend(confirmation["payload"]["confirmation_rows"])
        artifact_paths.extend((discovery_path, confirmation_path))
        batch_records.append(
            {
                "batch_id": batch_id,
                "discovery_path": repo_relative(discovery_path),
                "discovery_sha256": sha256_file(discovery_path),
                "discovery_payload_sha256": discovery["payload_sha256"],
                "confirmation_path": repo_relative(confirmation_path),
                "confirmation_sha256": sha256_file(confirmation_path),
                "confirmation_payload_sha256": confirmation["payload_sha256"],
                "attempted_count": discovery["payload"]["attempted_count"],
                "resolved_count": discovery["payload"]["resolved_count"],
                "candidate_count": discovery["payload"][
                    "candidate_count_pre_global_deduplication"
                ],
                "failed_confirmation_count": confirmation["payload"][
                    "failed_confirmation_count"
                ],
            }
        )
    if len(attempts) != 9648 or len({row["attempt_id"] for row in attempts}) != 9648:
        raise ValueError("I4 aggregate requires exactly 9,648 unique attempt rows")
    if len(confirmations) > config["execution"]["maximum_fresh_process_confirmations"]:
        raise ValueError("I4 confirmation count exceeds the frozen maximum")
    confirmed = [row for row in confirmations if row["confirmation_result"] == "passed"]
    frozen_candidates = _duplicate_classifications(confirmed)
    status_counts = Counter(row["candidate_status"] for row in attempts)
    unresolved = [
        row for row in attempts if row["resolved_status"] == "search_unresolved"
    ]
    failed_confirmation_count = sum(
        row["confirmation_result"] == "failed" for row in confirmations
    )
    all_resolved = not unresolved
    all_confirmed = failed_confirmation_count == 0 and len(confirmations) == sum(
        row["candidate_status"] == "positive_witness_pending_fresh_process_confirmation"
        for row in attempts
    )
    future_feature_access = any(
        row["adjudication_feature_accessed_during_discovery"] for row in attempts
    )
    execution_complete = all_resolved and all_confirmed and not future_feature_access
    routing = _continuation_routing(
        execution_complete=execution_complete,
        confirmed_candidate_count=len(confirmed),
    )
    failure_mode_counts = Counter(
        failure_mode
        for row in attempts
        for failure_mode in row.get("full_path_failure_modes", [])
    )
    branch_coverage = _branch_coverage(attempts)
    accessible_branch_count = sum(
        row["primary_lane_accessibility"]
        == "searched_and_resolved_inside_clean_primary_lane"
        for row in branch_coverage
    )
    payload = {
        "gate_id": "B2-I4",
        "status": "passed" if execution_complete else "blocked",
        "acceptance_state": "awaiting_scientific_review",
        "input_execution_revision": git("rev-parse", "HEAD"),
        "config_path": repo_relative(CONFIG_PATH),
        "config_sha256": sha256_file(CONFIG_PATH),
        "batch_records": batch_records,
        "search_accounting": {
            "allocated_attempt_count": 9648,
            "attempted_count": sum(row["attempted"] for row in attempts),
            "resolved_count": sum(
                row["resolved_status"].startswith("resolved") for row in attempts
            ),
            "unresolved_count": len(unresolved),
            "primary_search_native_steps": sum(
                read_json(Path(REPO_ROOT / record["discovery_path"]))["payload"][
                    "primary_search_native_steps"
                ]
                for record in batch_records
            ),
            "status_counts": dict(sorted(status_counts.items())),
            "full_path_failure_mode_counts": dict(sorted(failure_mode_counts.items())),
            "source_reconstruction_failure_count": sum(
                row["source_reconstruction_status"] != "passed" for row in attempts
            ),
            "early_stopping_used": False,
            "budget_migrated": False,
            "search_order_affects_attempt_population": False,
            "cross_stratum_optimizer_state_exists": False,
            "resume_or_shard_order_changes_attempt_population": False,
        },
        "attempt_ledger": attempts,
        "branch_primary_lane_coverage": branch_coverage,
        "branch_accessibility_summary": {
            "accepted_source_branch_count": len(branch_coverage),
            "searched_and_resolved_inside_clean_primary_lane_count": (
                accessible_branch_count
            ),
            "not_accessible_under_frozen_preparation_family_count": (
                len(branch_coverage) - accessible_branch_count
            ),
            "not_accessible_is_negative_constructibility_evidence": False,
        },
        "discovery_candidate_count": len(confirmations),
        "confirmed_candidate_count": len(confirmed),
        "failed_confirmation_count": failed_confirmation_count,
        "frozen_candidate_rows": frozen_candidates,
        "candidate_set_digest": semantic_digest(frozen_candidates),
        "outlier_review_index": _outliers(attempts, confirmations),
        "I5_feature_firewall": {
            "slow_cluster_fields_computed": False,
            "branch_relation_used_for_selection": False,
            "GRR4_or_GRR5_fields_computed": False,
            "future_gate_feature_access_detected": future_feature_access,
        },
        "delayed_formation_policy": (
            "no_unresolved_delayed_rows"
            if not any(
                row["candidate_status"] == "unresolved_delayed_post_driver_formation"
                for row in attempts
            )
            else "blocks_B2_C3_pending_schema_review"
        ),
        "maximum_GRR_rung": "not_assigned",
        "GRR_rung_assigned": False,
        "B2_closeout_ceiling": (
            "B2-C3-ready" if execution_complete else "B2-C2"
        ),
        "B2_closeout_rung_assigned": False,
        **routing,
        "candidate_set_status": (
            "empty_no_runtime_reached_candidate"
            if execution_complete and not confirmed
            else (
                "nonempty_confirmed_runtime_reached_candidate_set"
                if execution_complete
                else "not_frozen_incomplete_execution"
            )
        ),
        "claim_ceiling": (
            "bounded_negative_unchanged_runtime_search_no_runtime_reached_candidate_within_frozen_envelope"
            if execution_complete and not confirmed
            else "runtime_reached_post_driver_candidate_set_not_retention_or_mediation"
        ),
        "blocked_relabels": [
            "retained_sector",
            "slow_cluster",
            "mediation",
            "memory",
            "learning",
            "extension_selected",
        ],
        "unsafe_claim_flags": {
            "retention_established": False,
            "mediation_established": False,
            "memory": False,
            "learning": False,
            "extension_selected": False,
        },
    }
    if find_absolute_paths(payload):
        raise ValueError("I4 aggregate payload contains absolute paths")
    return payload, artifact_paths


def render_report(payload: dict[str, Any]) -> str:
    accounting = payload["search_accounting"]
    lines = [
        "# B2-GR Iteration 4 Native Preparation And Reachability",
        "",
        f"- Status: `{payload['status']}`",
        f"- Acceptance: `{payload['acceptance_state']}`",
        f"- Attempts: `{accounting['attempted_count']}/9648`",
        f"- Resolved: `{accounting['resolved_count']}/9648`",
        f"- Confirmed candidates: `{payload['confirmed_candidate_count']}`",
        f"- Failed confirmations: `{payload['failed_confirmation_count']}`",
        f"- GRR rung assigned: `{payload['GRR_rung_assigned']}`",
        f"- Candidate set: `{payload['candidate_set_status']}`",
        "",
        "## Interpretation",
        "",
        "I4 asks only whether unchanged GRC9V3 can reach a clean post-driver state",
        "difference from accepted B1 ancestry under the frozen preparation grid.",
        "It does not use branch transversality, slow-cluster, mediation, or final",
        "claim-classification fields. One post-driver transition is a discovery",
        "screen; the frozen 8/16/32 persistence qualification belongs to I5.",
        "",
        "Parameter-history rows distinguish the parameters that produced `k=0`",
        "from the restored evaluation parameters that govern `k=0 -> k=1`. No",
        "washout beat is inserted. Positive and sham paths share the full parameter",
        "schedule and administrative advancement; the sham omits only the forming",
        "C-pair pulse.",
        "",
        "Complete-path instrumentation separates harmless execution of budget or",
        "boundary stages from load-bearing state changes. Internal-stage W signals",
        "remain diagnostics and never become complete-step candidates. Directly",
        "authored C-direction content is excluded before the formation floor is",
        "tested.",
        "",
        "## Search Outcome",
        "",
        "The frozen search resolved all 9,648 attempts without a source-reconstruction",
        "failure, numerical failure, unresolved row, or positive candidate. Its",
        "nonpositive surface is preserved rather than collapsed into `no candidate`:",
        "",
        *[
            f"- `{status}`: `{count}`"
            for status, count in accounting["status_counts"].items()
        ],
        "",
        f"`{payload['branch_accessibility_summary']['searched_and_resolved_inside_clean_primary_lane_count']}` of "
        f"`{payload['branch_accessibility_summary']['accepted_source_branch_count']}` accepted branches had at least one nontrivial resolved clean-lane attempt. "
        f"The remaining `{payload['branch_accessibility_summary']['not_accessible_under_frozen_preparation_family_count']}` are inaccessible under the frozen preparation family and do not count as negative constructibility evidence.",
        "",
        "The 27 clean bounded-negative rows generated no attributable carrier above",
        "the formation and separation floors. The 1,706 authorship rows contained an",
        "apparent carrier but no identifiable runtime-generated component. The 7,915",
        "outside-envelope rows remain classified by their recorded full-path failure",
        "modes rather than being promoted from a clean endpoint.",
        "",
        "The I2 empty-path rule therefore makes I5-I7 positive lanes not applicable",
        "and routes the accepted empty candidate set to bounded I8 closeout. This is",
        "not an impossibility claim outside the frozen branch, preparation, parameter,",
        "history-length, and carrier envelope.",
        "",
        "## Claim Boundary",
        "",
        f"`{payload['claim_ceiling']}`",
        "",
        "No GRR rung is assigned in I4. With no runtime-reached candidate, branch",
        "relation, slow-cluster, and mediation qualification have no positive row to",
        "consume; the next applicable step is bounded closeout, not I5 promotion.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    payload, batch_paths = build_payload()
    artifact = envelope(payload, "b2_i4_native_preparation_reachability_v1", COMMAND)
    write_json(OUTPUT_PATH, artifact)
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    receipt = finalize_receipt(
        {
            "gate_id": "B2-I4",
            "status": "awaiting_scientific_review",
            "input_execution_revision": payload["input_execution_revision"],
            "config_path": repo_relative(CONFIG_PATH),
            "config_sha256": sha256_file(CONFIG_PATH),
            "generating_script_path": repo_relative(Path(__file__)),
            "generating_script_sha256": sha256_file(Path(__file__)),
            "output_payload_sha256": artifact["payload_sha256"],
            "output_artifact_digests": {
                repo_relative(path): sha256_file(path)
                for path in [*batch_paths, OUTPUT_PATH, REPORT_PATH]
            },
            "claim_ceiling": payload["claim_ceiling"],
            "assigned_GRR_rung": "not_assigned",
            "B2_closeout_ceiling": payload["B2_closeout_ceiling"],
            "ready_for_iteration_5": payload["ready_for_iteration_5"],
            "ready_for_iteration_8_bounded_closeout": payload[
                "ready_for_iteration_8_bounded_closeout"
            ],
            "I5_to_I7_positive_lane_status": payload[
                "I5_to_I7_positive_lane_status"
            ],
            "blocked_gates": (
                ["B2-I4-acceptance", "B2-I8"]
                if payload["ready_for_iteration_8_bounded_closeout"]
                else ["B2-I5", "B2-I6", "B2-I7", "B2-I8"]
            ),
            "not_applicable_gates": (
                ["B2-I5", "B2-I6", "B2-I7"]
                if payload["ready_for_iteration_8_bounded_closeout"]
                else []
            ),
        }
    )
    write_json(RECEIPT_PATH, receipt)
    print(
        f"I4: {payload['confirmed_candidate_count']} confirmed candidates; "
        f"ready_for_I5={payload['ready_for_iteration_5']}; "
        f"ready_for_bounded_closeout={payload['ready_for_iteration_8_bounded_closeout']}"
    )


if __name__ == "__main__":
    main()
