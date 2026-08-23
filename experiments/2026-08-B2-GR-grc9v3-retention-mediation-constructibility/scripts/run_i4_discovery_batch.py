"""Execute one predeclared B2-GR I4 discovery batch."""

from __future__ import annotations

import argparse
from typing import Any

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
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


COMMAND = (
    ".venv/bin/python experiments/2026-08-B2-GR-grc9v3-retention-mediation-"
    "constructibility/scripts/run_i4_discovery_batch.py --batch-id {batch_id}"
)
CONFIG_PATH = EXPERIMENT_ROOT / "configs/b2_i4_native_preparation_contract.json"
I1_PATH = EXPERIMENT_ROOT / "outputs/b2_i1_source_handoff_inventory.json"
I2_PATH = EXPERIMENT_ROOT / "outputs/b2_i2_constructibility_schema.json"
CALIBRATION_PATH = EXPERIMENT_ROOT / "outputs/b2_i3_threshold_calibration.json"


def _compact_preparation_history(history: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": history["family"],
        "history_length": history["history_length"],
        "pulse_amount": history["pulse_amount"],
        "pulse_edge_id": history["pulse_edge_id"],
        "pulse_source_node": history["pulse_source_node"],
        "pulse_destination_node": history["pulse_destination_node"],
        "parameter_variant_id": history["parameter_variant_id"],
        "parameter_name": history["parameter_name"],
        "parameter_multiplier": history["parameter_multiplier"],
        "state_production_parameter_vector_digest": semantic_digest(
            history["state_production_parameter_vector"]
        ),
        "current_evaluation_parameter_vector_digest": semantic_digest(
            history["current_evaluation_parameter_vector"]
        ),
        "driver_exhaustion_boundary": history["driver_exhaustion_boundary"],
        "first_post_driver_transition": history["first_post_driver_transition"],
        "unplanned_washout_step_used": history["unplanned_washout_step_used"],
        "full_history_digest": semantic_digest(history),
        "full_parameter_vectors_reconstructible_from": (
            "accepted_source_snapshot_plus_frozen_parameter_variant"
        ),
    }


def batch_registry() -> dict[str, dict[str, Any]]:
    i1 = read_json(I1_PATH)
    assert_envelope_digest(i1)
    rows = sorted(
        i1["payload"]["B1_branch_crosswalk"]["rows"],
        key=lambda row: (row["fixture_id"], row["branch_id"]),
    )
    result: dict[str, dict[str, Any]] = {}
    for fixture_id in ("F1", "F2", "F3"):
        fixture_rows = [row for row in rows if row["fixture_id"] == fixture_id]
        if len(fixture_rows) != 16:
            raise ValueError(f"{fixture_id} does not contain 16 accepted branches")
        for offset in range(0, 16, 4):
            batch_number = offset // 4 + 1
            batch_id = f"{fixture_id}-{batch_number:02d}"
            result[batch_id] = {
                "batch_id": batch_id,
                "fixture_id": fixture_id,
                "branch_rows": fixture_rows[offset : offset + 4],
            }
    return result


def validate_prerequisites(config: dict[str, Any]) -> dict[str, Any]:
    prerequisite = config["prerequisites"]
    for key_prefix, path_key in (
        ("i2_schema", "i2_schema_path"),
        ("i3_acceptance_anchor", "i3_acceptance_anchor_path"),
        ("threshold_calibration", "threshold_calibration_path"),
        ("i3_adjudicator", "i3_adjudicator_path"),
        ("b1_fixed_branch_registry", "b1_fixed_branch_registry_path"),
        ("b1_grv2_acceptance_anchor", "b1_grv2_acceptance_anchor_path"),
        ("b1_numerical_tolerances", "b1_numerical_tolerances_path"),
    ):
        path = REPO_ROOT / prerequisite[path_key]
        expected = prerequisite[f"{key_prefix}_sha256"]
        if sha256_file(path) != expected:
            raise ValueError(f"{key_prefix} file identity mismatch")
    i2 = read_json(I2_PATH)
    calibration = read_json(CALIBRATION_PATH)
    anchor = read_json(REPO_ROOT / prerequisite["i3_acceptance_anchor_path"])
    assert_envelope_digest(i2)
    assert_envelope_digest(calibration)
    if i2["payload_sha256"] != prerequisite["i2_schema_payload_sha256"]:
        raise ValueError("I2 payload identity mismatch")
    if (
        calibration["payload_sha256"]
        != prerequisite["threshold_calibration_payload_sha256"]
    ):
        raise ValueError("I3 calibration payload identity mismatch")
    if anchor["acceptance_status"] != "accepted" or not anchor["ready_for_iteration_4"]:
        raise ValueError("I3 acceptance does not open I4")
    runtime_identity = read_json(I1_PATH)["payload"]["unchanged_runtime_identity"]
    changed_runtime_paths = [
        row["path"]
        for row in runtime_identity["runtime_file_records"]
        if sha256_file(REPO_ROOT / row["path"]) != row["sha256"]
    ]
    if changed_runtime_paths:
        raise ValueError(
            f"unchanged runtime identity violated: {changed_runtime_paths}"
        )
    thresholds = {
        row["threshold_id"]: float(row["instantiated_value"])
        for row in calibration["payload"]["records"]
    }
    b1_registry = read_json(REPO_ROOT / prerequisite["b1_fixed_branch_registry_path"])
    assert_envelope_digest(b1_registry)
    b1_acceptance = read_json(
        REPO_ROOT / prerequisite["b1_grv2_acceptance_anchor_path"]
    )
    if b1_acceptance["acceptance_status"] != "accepted":
        raise ValueError("B1 GRV2 acceptance anchor is not accepted")
    b1_tolerances = read_json(
        REPO_ROOT / prerequisite["b1_numerical_tolerances_path"]
    )
    return {
        "i2": i2,
        "calibration": calibration,
        "i3_anchor": anchor,
        "runtime_identity": runtime_identity,
        "thresholds": thresholds,
        "b1_registry": {
            row["branch_id"]: row for row in b1_registry["payload"]["branches"]
        },
        "b1_C_absolute_tolerance": float(
            b1_tolerances["absolute_tolerances"]["C"]
        ),
    }


def build_batch(batch_id: str) -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    prerequisites = validate_prerequisites(config)
    registry = batch_registry()
    if batch_id not in registry:
        raise ValueError(f"unknown batch id {batch_id!r}; expected {sorted(registry)}")
    batch = registry[batch_id]
    expected_count = config["batching"]["expected_batch_attempt_counts"][
        batch["fixture_id"]
    ]
    expected_primary_steps = config["batching"][
        "expected_batch_primary_search_native_steps"
    ][batch["fixture_id"]]
    branch_rows = batch["branch_rows"]
    for row in branch_rows:
        if (
            sha256_file(REPO_ROOT / row["source_snapshot_path"])
            != row["source_snapshot_sha256"]
        ):
            raise ValueError(f"source snapshot mismatch for {row['branch_id']}")
    formation_floor = prerequisites["thresholds"][
        config["i4_admission"]["formation_contrast_threshold_id"]
    ]
    rows: list[dict[str, Any]] = []
    source_audits: list[dict[str, Any]] = []
    for branch_row in branch_rows:
        branch_result = evaluate_branch(
            branch_row,
            prerequisites["b1_registry"][branch_row["branch_id"]],
            formation_floor=formation_floor,
            source_coherence_abs_tolerance=prerequisites[
                "b1_C_absolute_tolerance"
            ],
            numerical_uncertainty=float(
                config["i4_admission"]["numerical_uncertainty_floor"]
            ),
            persistence_horizon=int(
                config["i4_admission"]["discovery_persistence_horizon_native_steps"]
            ),
            carrier_priority=config["candidate_freeze"]["carrier_priority"],
        )
        source_audits.append(branch_result["source_audit"])
        rows.extend(branch_result["rows"])
    rows.sort(key=lambda row: row["attempt_id"])
    if len(rows) != expected_count:
        raise ValueError(
            f"batch {batch_id} produced {len(rows)} rows; expected {expected_count}"
        )
    attempt_rows = []
    candidate_records = []
    for row in rows:
        source_failed = row["candidate_status"] == "source_replay_failure"
        attempt = {
            "attempt_id": row["attempt_id"],
            "search_row_id": row["search_row_id"],
            "attempt_index_within_branch": row["attempt_index_within_branch"],
            "allocated_budget_slot": row["allocated_budget_slot"],
            "search_stratum_id": f"{row['fixture_id']}_all_branches_all_preparations",
            "source_branch_id": row["source_branch_id"],
            "branch_family_id": row["fixture_id"],
            "carrier_definition_id": row["selected_carrier_definition_id"]
            or "none_above_I4_discovery_floor",
            "preparation_family": row["preparation_spec"]["preparation_family"],
            "preparation_parameter_vector": {
                "amplitude_fraction": row["preparation_spec"]["amplitude_fraction"],
                "parameter_variant_id": row["preparation_spec"]["parameter_variant_id"],
            },
            "preparation_history": _compact_preparation_history(
                row["preparation_history"]
            ),
            "seed_or_rng_state_digest": (
                row["positive_k0_state"]["rng_state_sha256"]
                if "positive_k0_state" in row
                else "source_reconstruction_failed_before_attempt"
            ),
            "attempted": not source_failed,
            "budget_consumed": 0.0 if source_failed else 1.0,
            "solver_or_runtime_status": (
                "source_reconstruction_failed"
                if source_failed
                else (
                    "native_runtime_completed"
                    if row["candidate_status"] != "numerical_failure"
                    else "numerical_failure"
                )
            ),
            "resolved_status": row["resolved_status"],
            "candidate_status": row["candidate_status"],
            "primary_demotion_reason": row["primary_demotion_reason"],
            "secondary_demotion_reasons": row["secondary_demotion_reasons"],
            "rejection_reason": row["primary_demotion_reason"],
            "full_path_cleanliness_result": row.get(
                "full_path_cleanliness_result", "source_reconstruction_not_admitted"
            ),
            "full_path_failure_modes": row.get("full_path_failure_modes", []),
            "duplicate_class": "not_adjudicated_until_global_aggregation",
            "source_reconstruction_status": row.get(
                "source_reconstruction_status", "source_replay_failure"
            ),
            "history_aware_candidate_identity": row.get(
                "history_aware_candidate_identity", "not_available"
            ),
            "boundary_flags": row.get("boundary_flags", {}),
            "outlier_flags": row.get("outlier_flags", {}),
            "artifact_manifest": [
                {
                    "path": row["source_snapshot_path"],
                    "sha256": row["source_snapshot_sha256"],
                    "artifact_role": "accepted_B1_source_branch_snapshot",
                }
            ],
            "discovery_features": row["discovery_features"],
            "adjudication_feature_accessed_during_discovery": row[
                "adjudication_feature_accessed_during_discovery"
            ],
        }
        attempt_rows.append(attempt)
        if row["row_decision"] == "positive_witness":
            candidate_records.append(row)
    counts = {
        status: sum(row["row_decision"] == status for row in rows)
        for status in (
            "positive_witness",
            "bounded_negative",
            "outside_envelope",
            "numerical_failure",
            "unresolved",
        )
    }
    primary_search_native_steps = sum(
        int(row["preparation_spec"]["history_length"])
        + int(config["i4_admission"]["discovery_persistence_horizon_native_steps"])
        for row in rows
        if row["candidate_status"] != "source_replay_failure"
    )
    if all(row["status"] == "passed" for row in source_audits) and (
        primary_search_native_steps != expected_primary_steps
    ):
        raise ValueError(
            f"batch {batch_id} consumed {primary_search_native_steps} primary steps; "
            f"expected {expected_primary_steps}"
        )
    payload = {
        "gate_id": "B2-I4-discovery-batch",
        "status": "passed_batch_execution",
        "batch_id": batch_id,
        "fixture_id": batch["fixture_id"],
        "input_execution_revision": git("rev-parse", "HEAD"),
        "config_path": repo_relative(CONFIG_PATH),
        "config_sha256": sha256_file(CONFIG_PATH),
        "source_I2_payload_sha256": prerequisites["i2"]["payload_sha256"],
        "source_I3_acceptance_anchor_sha256": sha256_file(
            REPO_ROOT / config["prerequisites"]["i3_acceptance_anchor_path"]
        ),
        "source_adjudicator_schema_version": config["prerequisites"][
            "i3_adjudicator_schema_version"
        ],
        "source_adjudicator_sha256": config["prerequisites"]["i3_adjudicator_sha256"],
        "unchanged_runtime_identity_id": prerequisites["runtime_identity"][
            "identity_id"
        ],
        "branch_ids": [row["branch_id"] for row in branch_rows],
        "source_reconstruction_audits": source_audits,
        "all_source_reconstructions_passed": all(
            row["status"] == "passed" for row in source_audits
        ),
        "allocated_attempt_count": expected_count,
        "attempted_count": sum(row["attempted"] for row in attempt_rows),
        "resolved_count": sum(
            row["resolved_status"].startswith("resolved") for row in rows
        ),
        "unresolved_count": sum(
            row["resolved_status"] == "search_unresolved" for row in rows
        ),
        "candidate_count_pre_global_deduplication": len(candidate_records),
        "result_counts": counts,
        "budget_consumed_fraction": sum(
            float(row["budget_consumed"]) for row in attempt_rows
        )
        / expected_count,
        "primary_search_native_steps": primary_search_native_steps,
        "primary_search_native_step_budget": config["execution"][
            "maximum_primary_search_native_steps"
        ],
        "matched_sham_control_steps_accounted_separately": True,
        "early_stopping_used": False,
        "budget_migrated": False,
        "discovery_feature_whitelist": prerequisites["i2"]["payload"][
            "search_envelope"
        ]["discovery_feature_whitelist"],
        "future_gate_feature_blacklist": prerequisites["i2"]["payload"][
            "search_envelope"
        ]["future_gate_adjudication_feature_blacklist"],
        "attempt_rows": attempt_rows,
        "candidate_records": candidate_records,
    }
    if find_absolute_paths(payload):
        raise ValueError("batch payload contains absolute paths")
    return envelope(
        payload,
        schema_version="b2_i4_discovery_batch_v2",
        command=COMMAND.format(batch_id=batch_id),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args()
    artifact = build_batch(args.batch_id)
    output = (
        EXPERIMENT_ROOT / "outputs/i4_batches" / f"b2_i4_discovery_{args.batch_id}.json"
    )
    write_json(output, artifact)
    payload = artifact["payload"]
    print(
        f"{args.batch_id}: {payload['attempted_count']} attempts, "
        f"{payload['candidate_count_pre_global_deduplication']} candidates"
    )


if __name__ == "__main__":
    main()
