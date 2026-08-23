"""Reconstruct I4 transiently and retain only compact empty-path audit evidence."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    assert_envelope_digest,
    envelope,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    write_json,
)
from b2_i4_methods import evaluate_branch
from run_i4_discovery_batch import (
    CONFIG_PATH as I4_CONFIG_PATH,
    batch_registry,
    validate_prerequisites,
)


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/build_i8_empty_path_audit.py"
)
CONFIG_PATH = EXPERIMENT_ROOT / "configs/b2_i8_empty_path_audit_contract.json"
I4_RESULT_PATH = EXPERIMENT_ROOT / "outputs/b2_i4_native_preparation_reachability.json"
I4_ANCHOR_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i4_acceptance_anchor.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs/b2_i8_empty_path_audit.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports/b2_i8_empty_path_audit.md"


def attribution_class(residual: float, policy: dict[str, Any]) -> str:
    if residual <= policy["authored_within_numerical_uncertainty_ceiling"]:
        return "apparent_carrier_authored_within_numerical_uncertainty"
    if residual <= policy["carrier_separation_floor"]:
        return "runtime_residual_above_uncertainty_below_separation_floor"
    if residual <= policy["formation_admission_floor"]:
        return "runtime_residual_above_separation_below_formation_floor"
    raise ValueError("merged attribution row has residual above the formation floor")


def classification_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["fixture_id"],
        row["source_branch_id"],
        row["preparation_spec"]["preparation_family"],
        row["candidate_status"],
        row["primary_demotion_reason"],
        tuple(row.get("full_path_failure_modes", [])),
    )


def compact_matrix(counter: Counter[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [
        {
            "branch_family_id": key[0],
            "source_branch_id": key[1],
            "preparation_family": key[2],
            "candidate_status": key[3],
            "primary_demotion_reason": key[4],
            "full_path_failure_modes": list(key[5]),
            "attempt_count": count,
        }
        for key, count in sorted(counter.items())
    ]


def _counter_rows(
    groups: dict[tuple[Any, ...], Counter[str]], fields: list[str]
) -> list[dict[str, Any]]:
    return [
        {
            **dict(zip(fields, key, strict=True)),
            "status_counts": dict(sorted(counts.items())),
            "attempt_count": sum(counts.values()),
            "clean_primary_attempt_count": sum(
                count
                for status, count in counts.items()
                if status in {
                    "bounded_negative",
                    "formation_entirely_authored_or_unidentifiable",
                    "internal_stage_only_candidate",
                    "overwritten_or_nonpersistent_after_driver",
                    "positive_witness_pending_fresh_process_confirmation",
                }
            ),
        }
        for key, counts in sorted(groups.items())
    ]


def build_payload() -> dict[str, Any]:
    audit_config = read_json(CONFIG_PATH)
    i4_config = read_json(I4_CONFIG_PATH)
    i4_result = read_json(I4_RESULT_PATH)
    assert_envelope_digest(i4_result)
    accepted = read_json(I4_ANCHOR_PATH)
    if accepted["acceptance_status"] != "accepted":
        raise ValueError("I4 is not accepted")
    if sha256_file(I4_ANCHOR_PATH) != audit_config[
        "source_i4_acceptance_anchor_sha256"
    ]:
        raise ValueError("I4 acceptance anchor changed")
    if i4_result["payload_sha256"] != accepted["result_artifact_payload_sha256"]:
        raise ValueError("I4 result/acceptance mismatch")
    git("merge-base", "--is-ancestor", accepted["result_revision"], "HEAD")
    prerequisites = validate_prerequisites(i4_config)
    registry = batch_registry()
    formation_floor = prerequisites["thresholds"][
        i4_config["i4_admission"]["formation_contrast_threshold_id"]
    ]
    split_policy = audit_config["attribution_split"]
    if formation_floor != split_policy["formation_admission_floor"]:
        raise ValueError("audit formation floor differs from accepted I4")

    attempt_ids: list[str] = []
    status_counts: Counter[str] = Counter()
    failure_mode_counts: Counter[str] = Counter()
    failure_mode_combinations: Counter[tuple[str, ...]] = Counter()
    classification_counts: Counter[tuple[Any, ...]] = Counter()
    branch_preparation: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    effective_strata: dict[tuple[Any, ...], Counter[str]] = defaultdict(Counter)
    branch_allocations: dict[str, Counter[str]] = defaultdict(Counter)
    attribution_counts: Counter[str] = Counter()
    attribution_by_family: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    attribution_residuals: dict[str, list[float]] = defaultdict(list)
    maximum_residual_carrier_counts: Counter[str] = Counter()
    bounded_rows: list[dict[str, Any]] = []
    near_misses: list[dict[str, Any]] = []
    sham_drift_rows: list[dict[str, Any]] = []
    outside_samples: dict[tuple[str, ...], list[str]] = defaultdict(list)
    source_reconstruction_failures = 0
    candidate_count = 0
    delayed_count = 0
    internal_stage_count = 0
    overwritten_count = 0

    for batch_id, batch in sorted(registry.items()):
        for branch_row in batch["branch_rows"]:
            result = evaluate_branch(
                branch_row,
                prerequisites["b1_registry"][branch_row["branch_id"]],
                formation_floor=formation_floor,
                source_coherence_abs_tolerance=prerequisites[
                    "b1_C_absolute_tolerance"
                ],
                numerical_uncertainty=float(
                    i4_config["i4_admission"]["numerical_uncertainty_floor"]
                ),
                persistence_horizon=int(
                    i4_config["i4_admission"][
                        "discovery_persistence_horizon_native_steps"
                    ]
                ),
                carrier_priority=i4_config["candidate_freeze"]["carrier_priority"],
            )
            if result["source_audit"]["status"] != "passed":
                source_reconstruction_failures += 1
            for row in result["rows"]:
                attempt_ids.append(row["attempt_id"])
                status = row["candidate_status"]
                status_counts[status] += 1
                classification_counts[classification_key(row)] += 1
                modes = tuple(row.get("full_path_failure_modes", []))
                failure_mode_combinations[modes] += 1
                for mode in modes:
                    failure_mode_counts[mode] += 1
                prep = row["preparation_spec"]
                branch_preparation[(row["source_branch_id"], prep["preparation_family"])][
                    status
                ] += 1
                effective_key = (
                    row["source_branch_id"],
                    prep["preparation_family"],
                    prep["history_length"],
                    prep["parameter_variant_id"],
                    prep["amplitude_fraction"],
                )
                effective_strata[effective_key][status] += 1
                branch_allocations[row["source_branch_id"]]["attempted"] += 1
                branch_allocations[row["source_branch_id"]][status] += 1
                if status == "positive_witness_pending_fresh_process_confirmation":
                    candidate_count += 1
                elif status == "unresolved_delayed_post_driver_formation":
                    delayed_count += 1
                elif status == "internal_stage_only_candidate":
                    internal_stage_count += 1
                elif status == "overwritten_or_nonpersistent_after_driver":
                    overwritten_count += 1

                if status == "formation_entirely_authored_or_unidentifiable":
                    carrier_rows = row["carrier_rows"]
                    max_carrier, max_row = max(
                        carrier_rows.items(),
                        key=lambda item: item[1]["runtime_generated_residual_norm"],
                    )
                    residual = float(max_row["runtime_generated_residual_norm"])
                    split = attribution_class(residual, split_policy)
                    attribution_counts[split] += 1
                    attribution_by_family[(row["fixture_id"], prep["preparation_family"])][
                        split
                    ] += 1
                    attribution_residuals[split].append(residual)
                    maximum_residual_carrier_counts[max_carrier] += 1
                    near_misses.append(
                        {
                            "attempt_id": row["attempt_id"],
                            "source_branch_id": row["source_branch_id"],
                            "fixture_id": row["fixture_id"],
                            "preparation_family": prep["preparation_family"],
                            "history_length": prep["history_length"],
                            "parameter_variant_id": prep["parameter_variant_id"],
                            "amplitude_fraction": prep["amplitude_fraction"],
                            "maximum_residual_carrier": max_carrier,
                            "maximum_runtime_generated_residual_norm": residual,
                            "formation_floor": formation_floor,
                            "formation_floor_fraction": residual / formation_floor,
                            "attribution_split": split,
                            "sham_drift_fraction": row["sham_drift"][
                                "fraction_of_formation_reference"
                            ],
                        }
                    )
                if status == "bounded_negative":
                    bounded_rows.append(
                        {
                            "attempt_id": row["attempt_id"],
                            "source_branch_id": row["source_branch_id"],
                            "fixture_id": row["fixture_id"],
                            "preparation_family": prep["preparation_family"],
                            "state_identity_digest": row["state_identity_digest"],
                            "history_aware_candidate_identity": row[
                                "history_aware_candidate_identity"
                            ],
                            "symmetry_signature": row[
                                "symmetry_signature_for_characterization_only"
                            ],
                        }
                    )
                if modes and len(outside_samples[modes]) < 12:
                    outside_samples[modes].append(row["attempt_id"])
                sham_drift_rows.append(
                    {
                        "attempt_id": row["attempt_id"],
                        "candidate_status": status,
                        "fraction_of_formation_reference": row["sham_drift"][
                            "fraction_of_formation_reference"
                        ],
                    }
                )
            print(
                f"audit {batch_id} {branch_row['branch_id']}: "
                f"{len(result['rows'])} attempts",
                flush=True,
            )

    accepted_payload = i4_result["payload"]
    if len(attempt_ids) != 9648 or len(set(attempt_ids)) != 9648:
        raise ValueError("audit did not reconstruct 9,648 unique attempts")
    if semantic_digest(sorted(attempt_ids)) != accepted_payload["attempt_ledger_storage"][
        "attempt_population_identity_digest"
    ]:
        raise ValueError("audit attempt population differs from accepted I4")
    if compact_matrix(classification_counts) != accepted_payload[
        "negative_classification_matrix"
    ]:
        raise ValueError("audit classification matrix differs from accepted I4")
    if dict(sorted(status_counts.items())) != accepted_payload["search_accounting"][
        "status_counts"
    ]:
        raise ValueError("audit status counts differ from accepted I4")
    if dict(sorted(failure_mode_counts.items())) != accepted_payload[
        "search_accounting"
    ]["full_path_failure_mode_counts"]:
        raise ValueError("audit failure-mode counts differ from accepted I4")

    near_misses.sort(
        key=lambda row: (-row["formation_floor_fraction"], row["attempt_id"])
    )
    sham_drift_rows.sort(
        key=lambda row: (-row["fraction_of_formation_reference"], row["attempt_id"])
    )
    branch_rows = []
    for branch_id, counts in sorted(branch_allocations.items()):
        expected = 361 if "-f3-" in branch_id else 121
        branch_rows.append(
            {
                "source_branch_id": branch_id,
                "planned_attempt_count": expected,
                "executed_attempt_count": counts["attempted"],
                "allocation_complete": counts["attempted"] == expected,
                "status_counts": dict(
                    sorted(
                        (status, count)
                        for status, count in counts.items()
                        if status != "attempted"
                    )
                ),
            }
        )

    split_summary = []
    for split in split_policy["classes"]:
        values = attribution_residuals[split]
        split_summary.append(
            {
                "attribution_class": split,
                "attempt_count": attribution_counts[split],
                "minimum_runtime_generated_residual_norm": min(values) if values else None,
                "maximum_runtime_generated_residual_norm": max(values) if values else None,
            }
        )

    payload = {
        "audit_id": audit_config["audit_id"],
        "status": "passed",
        "input_execution_revision": git("rev-parse", "HEAD"),
        "source_i4_acceptance_anchor_path": repo_relative(I4_ANCHOR_PATH),
        "source_i4_acceptance_anchor_sha256": sha256_file(I4_ANCHOR_PATH),
        "source_i4_result_payload_sha256": i4_result["payload_sha256"],
        "audit_contract_path": repo_relative(CONFIG_PATH),
        "audit_contract_sha256": sha256_file(CONFIG_PATH),
        "reconstruction_equivalence": {
            "attempt_count": len(attempt_ids),
            "attempt_population_identity_digest": semantic_digest(sorted(attempt_ids)),
            "classification_matrix_matches_accepted_I4": True,
            "status_counts_match_accepted_I4": True,
            "failure_mode_counts_match_accepted_I4": True,
            "source_reconstruction_failure_count": source_reconstruction_failures,
        },
        "terminal_classification_semantics": {
            "terminally_classified_attempt_count": len(attempt_ids),
            "scientifically_clean_bounded_negative_attempt_count": status_counts[
                "bounded_negative"
            ],
            "formation_attribution_blocked_attempt_count": status_counts[
                "formation_entirely_authored_or_unidentifiable"
            ],
            "outside_primary_envelope_attempt_count": status_counts[
                "outside_envelope"
            ],
            "terminal_classification_is_scientific_constructibility_resolution": False,
        },
        "formation_attribution_split_policy": split_policy,
        "formation_attribution_split": split_summary,
        "formation_attribution_by_fixture_and_preparation": [
            {
                "fixture_id": key[0],
                "preparation_family": key[1],
                "split_counts": dict(sorted(counts.items())),
                "attempt_count": sum(counts.values()),
            }
            for key, counts in sorted(attribution_by_family.items())
        ],
        "maximum_residual_carrier_counts": dict(
            sorted(maximum_residual_carrier_counts.items())
        ),
        "branch_preparation_matrix": _counter_rows(
            branch_preparation, ["source_branch_id", "preparation_family"]
        ),
        "effective_stratum_matrix": _counter_rows(
            effective_strata, audit_config["effective_stratum_dimensions"]
        ),
        "branch_allocation_audit": branch_rows,
        "bounded_negative_uniqueness": {
            "attempt_count": len(bounded_rows),
            "unique_source_branch_count": len(
                {row["source_branch_id"] for row in bounded_rows}
            ),
            "unique_preparation_family_count": len(
                {row["preparation_family"] for row in bounded_rows}
            ),
            "unique_state_identity_count": len(
                {row["state_identity_digest"] for row in bounded_rows}
            ),
            "unique_history_aware_identity_count": len(
                {row["history_aware_candidate_identity"] for row in bounded_rows}
            ),
            "unique_symmetry_signature_count": len(
                {row["symmetry_signature"] for row in bounded_rows}
            ),
            "rows": bounded_rows,
        },
        "outside_envelope_mechanisms": {
            "failure_mode_counts_overlap_allowed": dict(
                sorted(failure_mode_counts.items())
            ),
            "exclusive_failure_mode_combinations": [
                {
                    "failure_modes": list(modes),
                    "attempt_count": count,
                    "sample_attempt_ids": outside_samples[modes],
                }
                for modes, count in sorted(failure_mode_combinations.items())
                if modes
            ],
            "eventful_attempt_count": sum(
                count
                for modes, count in failure_mode_combinations.items()
                if any(mode.startswith("eventful_") for mode in modes)
            ),
            "topology_mutating_attempt_count": sum(
                count
                for modes, count in failure_mode_combinations.items()
                if any(mode.startswith("topology_mutation_") for mode in modes)
            ),
            "all_attempts_were_inside_frozen_proposal_grid": True,
        },
        "near_miss_audit": {
            "ranking_is_diagnostic_not_admission": True,
            "top_subthreshold_runtime_residual_rows": near_misses[
                : audit_config["near_miss_sample_limit"]
            ],
            "top_sham_drift_rows": sham_drift_rows[
                : audit_config["near_miss_sample_limit"]
            ],
            "delayed_post_driver_formation_count": delayed_count,
            "internal_stage_only_candidate_count": internal_stage_count,
            "overwritten_or_nonpersistent_candidate_count": overwritten_count,
        },
        "candidate_confirmation_accounting": {
            "discovery_candidate_count_before_confirmation": candidate_count,
            "fresh_confirmation_attempt_count": accepted_payload[
                "discovery_candidate_count"
            ],
            "fresh_confirmation_failure_count": accepted_payload[
                "failed_confirmation_count"
            ],
            "confirmed_candidate_count": accepted_payload[
                "confirmed_candidate_count"
            ],
        },
        "scientific_boundary": {
            "I4_candidate_set_reopened": False,
            "GRR_rung_assigned": False,
            "retention_or_mediation_tested": False,
            "extension_selected": False,
            "runtime_change_authorized": False,
            "full_attempt_rows_retained": False,
            "audit_role": "closeout_interpretation_hardening_only",
        },
    }
    if find_absolute_paths(payload):
        raise ValueError("empty-path audit contains absolute paths")
    return payload


def render_report(payload: dict[str, Any]) -> str:
    terminal = payload["terminal_classification_semantics"]
    split = payload["formation_attribution_split"]
    unique = payload["bounded_negative_uniqueness"]
    outside = payload["outside_envelope_mechanisms"]
    return "\n".join(
        [
            "# B2-GR I8 Empty-Path Audit",
            "",
            "## Terminal Classification Is Not Scientific Resolution",
            "",
            f"All `{terminal['terminally_classified_attempt_count']}` attempts received a",
            "terminal machine classification. Only",
            f"`{terminal['scientifically_clean_bounded_negative_attempt_count']}` are",
            "clean bounded negatives; terminal classification does not mean the",
            "constructibility question was scientifically resolved for every attempt.",
            "",
            "## Formation Attribution Split",
            "",
            *[
                f"- `{row['attribution_class']}`: `{row['attempt_count']}`"
                for row in split
            ],
            "",
            "The split uses the already frozen I4 numerical-uncertainty, separation,",
            "and formation floors. It changes no I4 admission and creates no candidate.",
            "",
            "## Bounded-Negative Scope",
            "",
            f"The `{unique['attempt_count']}` bounded negatives cover",
            f"`{unique['unique_source_branch_count']}` source branches and",
            f"`{unique['unique_preparation_family_count']}` preparation family. They",
            "must not be interpreted as broad nontrivial-preparation coverage.",
            "",
            "## Outside-Envelope Mechanisms",
            "",
            f"Eventful attempts: `{outside['eventful_attempt_count']}`.",
            f"Topology-mutating attempts: `{outside['topology_mutating_attempt_count']}`.",
            "All proposals were inside the frozen proposal grid; outside-envelope",
            "status arose from observed path-cleanliness failures, whose exact",
            "overlapping and exclusive distributions are retained in the JSON audit.",
            "",
            "## Boundary",
            "",
            "This audit hardens interpretation only. It reopens no I4 candidate,",
            "assigns no GRR rung, runs no retention or mediation gate, and selects no",
            "extension. Full reconstructed rows existed only in memory and are not",
            "retained as a second ledger.",
            "",
        ]
    )


def main() -> None:
    payload = build_payload()
    artifact = envelope(payload, "b2_i8_empty_path_audit_v1", COMMAND)
    write_json(OUTPUT_PATH, artifact)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    print(
        "I8 empty-path audit: reconstructed 9648 attempts; "
        "compact interpretation evidence written",
        flush=True,
    )


if __name__ == "__main__":
    main()
