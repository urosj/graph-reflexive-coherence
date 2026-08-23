"""Fresh-process confirmation for one frozen B2-GR I4 discovery batch."""

from __future__ import annotations

import argparse
from pathlib import Path
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
from b2_i4_methods import evaluate_attempt, source_reconstruction_audit
from pygrc.models import GRC9V3
from run_i4_discovery_batch import CONFIG_PATH, I1_PATH, validate_prerequisites


COMMAND = (
    ".venv/bin/python experiments/2026-08-B2-GR-grc9v3-retention-mediation-"
    "constructibility/scripts/run_i4_confirmation_batch.py --batch-id {batch_id}"
)


def _crosswalk() -> dict[str, dict[str, Any]]:
    i1 = read_json(I1_PATH)
    assert_envelope_digest(i1)
    return {
        row["branch_id"]: row for row in i1["payload"]["B1_branch_crosswalk"]["rows"]
    }


def _confirm_candidate(
    candidate: dict[str, Any],
    branch_row: dict[str, Any],
    registry_row: dict[str, Any],
    config: dict[str, Any],
    formation_floor: float,
) -> dict[str, Any]:
    base_model = GRC9V3.load(str(REPO_ROOT / Path(branch_row["source_snapshot_path"])))
    source_audit = source_reconstruction_audit(base_model, branch_row, registry_row)
    reproduced = evaluate_attempt(
        base_model,
        branch_row,
        source_audit,
        candidate["preparation_spec"],
        formation_floor=formation_floor,
        numerical_uncertainty=float(
            config["i4_admission"]["numerical_uncertainty_floor"]
        ),
        persistence_horizon=int(
            config["i4_admission"]["discovery_persistence_horizon_native_steps"]
        ),
        carrier_priority=config["candidate_freeze"]["carrier_priority"],
    )
    checks = {
        "source_state_identity_matches": reproduced["source_state_digest"]
        == candidate["source_state_digest"],
        "source_reconstruction_audit_matches": reproduced[
            "source_reconstruction_digest"
        ]
        == candidate["source_reconstruction_digest"],
        "preparation_schedule_matches": reproduced["preparation_spec"]
        == candidate["preparation_spec"],
        "preparation_history_digest_matches": reproduced["preparation_history_digest"]
        == candidate["preparation_history_digest"],
        "positive_history_trace_matches": semantic_digest(
            reproduced["positive_history_audit"]
        )
        == semantic_digest(candidate["positive_history_audit"]),
        "sham_history_trace_matches": semantic_digest(reproduced["sham_history_audit"])
        == semantic_digest(candidate["sham_history_audit"]),
        "paired_history_summary_matches": semantic_digest(
            reproduced["paired_history_summary"]
        )
        == semantic_digest(candidate["paired_history_summary"]),
        "sham_preparation_trace_matches": reproduced["sham_preparation_trace_digest"]
        == candidate["sham_preparation_trace_digest"],
        "driver_exhaustion_point_matches": reproduced["preparation_history"][
            "driver_exhaustion_boundary"
        ]
        == candidate["preparation_history"]["driver_exhaustion_boundary"],
        "k0_complete_step_state_matches": reproduced["post_driver_k0_state_digest"]
        == candidate["post_driver_k0_state_digest"],
        "carrier_definition_matches": reproduced["selected_carrier_definition_id"]
        == candidate["selected_carrier_definition_id"],
        "carrier_formation_contrast_matches": semantic_digest(
            reproduced["carrier_rows"]
        )
        == semantic_digest(candidate["carrier_rows"]),
        "full_path_cleanliness_matches": reproduced["full_path_cleanliness_result"]
        == candidate["full_path_cleanliness_result"]
        == "passed_clean_primary_lane",
        "full_path_failure_modes_match": reproduced["full_path_failure_modes"]
        == candidate["full_path_failure_modes"]
        == [],
        "mechanism_execution_trace_matches": semantic_digest(
            reproduced["mechanism_execution_summary"]
        )
        == semantic_digest(candidate["mechanism_execution_summary"]),
        "internal_stage_provenance_matches": semantic_digest(
            reproduced["internal_stage_audit"]
        )
        == semantic_digest(candidate["internal_stage_audit"]),
        "admissibility_margins_match": (
            reproduced["carrier_rows"][reproduced["selected_carrier_definition_id"]][
                "formation_margin"
            ]
            == candidate["carrier_rows"][candidate["selected_carrier_definition_id"]][
                "formation_margin"
            ]
        ),
        "candidate_deduplication_identity_matches": reproduced[
            "history_aware_candidate_identity"
        ]
        == candidate["history_aware_candidate_identity"],
        "first_post_driver_transition_matches": semantic_digest(
            reproduced["persistence"]
        )
        == semantic_digest(candidate["persistence"]),
        "row_numerical_uncertainty_matches": reproduced["row_numerical_uncertainty"]
        == candidate["row_numerical_uncertainty"],
        "positive_disposition_reproduced": reproduced["row_decision"]
        == "positive_witness",
        "no_future_gate_feature_access": not reproduced[
            "future_gate_features_computed_or_accessed"
        ],
    }
    return {
        "attempt_id": candidate["attempt_id"],
        "source_branch_id": candidate["source_branch_id"],
        "fresh_model_loaded_for_candidate": True,
        "source_reconstruction_status": source_audit["status"],
        "checks": checks,
        "confirmation_result": "passed" if all(checks.values()) else "failed",
        "discovery_candidate_digest": semantic_digest(candidate),
        "reproduced_candidate_digest": semantic_digest(reproduced),
        "reproduced_candidate": reproduced,
    }


def build_confirmation(batch_id: str) -> dict[str, Any]:
    config = read_json(CONFIG_PATH)
    prerequisites = validate_prerequisites(config)
    discovery_path = (
        EXPERIMENT_ROOT / "outputs/i4_batches" / f"b2_i4_discovery_{batch_id}.json"
    )
    discovery = read_json(discovery_path)
    assert_envelope_digest(discovery)
    payload = discovery["payload"]
    if payload["batch_id"] != batch_id:
        raise ValueError("discovery batch identity mismatch")
    if payload["config_sha256"] != sha256_file(CONFIG_PATH):
        raise ValueError("I4 config changed after discovery")
    crosswalk = _crosswalk()
    formation_floor = prerequisites["thresholds"][
        config["i4_admission"]["formation_contrast_threshold_id"]
    ]
    confirmations = []
    for candidate in sorted(
        payload["candidate_records"], key=lambda row: row["attempt_id"]
    ):
        branch_id = candidate["source_branch_id"]
        confirmations.append(
            _confirm_candidate(
                candidate,
                crosswalk[branch_id],
                prerequisites["b1_registry"][branch_id],
                config,
                formation_floor,
            )
        )
    result_payload = {
        "gate_id": "B2-I4-confirmation-batch",
        "status": "passed_confirmation_execution",
        "batch_id": batch_id,
        "input_execution_revision": git("rev-parse", "HEAD"),
        "discovery_batch_path": repo_relative(discovery_path),
        "discovery_batch_sha256": sha256_file(discovery_path),
        "discovery_batch_payload_sha256": discovery["payload_sha256"],
        "config_path": repo_relative(CONFIG_PATH),
        "config_sha256": sha256_file(CONFIG_PATH),
        "candidate_count": len(payload["candidate_records"]),
        "confirmation_count": len(confirmations),
        "passed_confirmation_count": sum(
            row["confirmation_result"] == "passed" for row in confirmations
        ),
        "failed_confirmation_count": sum(
            row["confirmation_result"] == "failed" for row in confirmations
        ),
        "fresh_model_per_candidate": True,
        "endpoint_only_confirmation_allowed": False,
        "confirmation_rows": confirmations,
    }
    if find_absolute_paths(result_payload):
        raise ValueError("confirmation payload contains absolute paths")
    return envelope(
        result_payload,
        schema_version="b2_i4_confirmation_batch_v1",
        command=COMMAND.format(batch_id=batch_id),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args()
    artifact = build_confirmation(args.batch_id)
    output = (
        EXPERIMENT_ROOT
        / "outputs/i4_batches"
        / f"b2_i4_confirmation_{args.batch_id}.json"
    )
    write_json(output, artifact)
    payload = artifact["payload"]
    print(
        f"{args.batch_id}: {payload['confirmation_count']} confirmations, "
        f"{payload['failed_confirmation_count']} failed"
    )


if __name__ == "__main__":
    main()
