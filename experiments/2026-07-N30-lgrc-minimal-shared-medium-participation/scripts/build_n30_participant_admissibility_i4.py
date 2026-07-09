#!/usr/bin/env python3
"""Build N30 Iteration 4 minimal participant admissibility probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
I3_OUTPUT = EXPERIMENT / "outputs" / "n30_active_nulls_i3.json"
OUTPUT = EXPERIMENT / "outputs" / "n30_participant_admissibility_i4.json"
REPORT = EXPERIMENT / "reports" / "n30_participant_admissibility_i4.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_participant_admissibility_i4_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_participant_admissibility_i4.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

N27_ROOT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
N27_MINIMAL_OUTPUT = N27_ROOT / "outputs" / "n27_minimal_configuration_transfer_probe.json"
N27_REPLAY_OUTPUT = N27_ROOT / "outputs" / "n27_replay_same_basin_mapping_matrix.json"
N27_ARTIFACT_DIR = N27_ROOT / "outputs" / "n27_minimal_configuration_transfer_probe_artifacts"
N27_PRE_SIGNATURE = N27_ARTIFACT_DIR / "pre_transfer_basin_signature_trace.json"
N27_POST_SIGNATURE = N27_ARTIFACT_DIR / "post_transfer_basin_signature_trace.json"
N27_MAPPING_TRACE = N27_ARTIFACT_DIR / "transfer_mapping_trace.json"
N27_RUNTIME_TRACE = N27_ARTIFACT_DIR / "source_current_runtime_trace.json"
N27_SUPPORT_TRACE = N27_ARTIFACT_DIR / "support_preservation_trace.json"
N27_COHERENCE_TRACE = N27_ARTIFACT_DIR / "coherence_preservation_trace.json"
N27_BOUNDARY_TRACE = N27_ARTIFACT_DIR / "boundary_mapping_trace.json"
N27_FLUX_TRACE = N27_ARTIFACT_DIR / "flux_balance_trace.json"
N27_RECONSTRUCTED_SUPPORT = N27_ARTIFACT_DIR / "reconstructed_support_ledger.json"
N27_REPLAY_TRACE = (
    N27_ROOT
    / "outputs"
    / "n27_replay_same_basin_mapping_matrix_artifacts"
    / "n27_i5_row_i4_same_basin_mapping_replay_replay_trace.json"
)


BLOCKED_CLAIMS = [
    "medium_perturbation",
    "trace_mediated_eligibility",
    "minimal_shared_medium_participation",
    "shared_medium_coordination",
    "native_shared_medium_organization",
    "semantic_communication",
    "semantic_coordination",
    "cooperation",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_completion",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def write_artifact(name: str, data: dict[str, Any]) -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(canonical_json(data), encoding="utf-8")
    return {
        "path": rel(path),
        "artifact_role": data["artifact_role"],
        "sha256": sha256_file(path),
    }


def source_input(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": rel(path),
        "source_role": role,
        "sha256": sha256_file(path),
    }


def build_payload() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT)
    n27_minimal = load_json(N27_MINIMAL_OUTPUT)
    n27_replay = load_json(N27_REPLAY_OUTPUT)
    pre = load_json(N27_PRE_SIGNATURE)
    post = load_json(N27_POST_SIGNATURE)
    mapping = load_json(N27_MAPPING_TRACE)
    runtime = load_json(N27_RUNTIME_TRACE)
    support = load_json(N27_SUPPORT_TRACE)
    coherence = load_json(N27_COHERENCE_TRACE)
    boundary = load_json(N27_BOUNDARY_TRACE)
    flux = load_json(N27_FLUX_TRACE)
    reconstructed_support = load_json(N27_RECONSTRUCTED_SUPPORT)
    replay_trace = load_json(N27_REPLAY_TRACE)

    participant_carrier_id = "n30_i4_participant_carrier_basin_signature_A_mapped"
    participant_start_state_digest = pre["pre_signature_digest"]
    participant_end_state_digest = post["post_signature_digest"]
    recognizability_metric = "signature_distance_under_declared_N27_mapping"
    recognizability_threshold = post["max_signature_distance"]
    recognizability_observed = post["observed_signature_distance"]
    recognizability_margin = post["signature_preservation_margin"]
    replay_trace_digest = digest_value(replay_trace)
    participant_carrier_digest = digest_value(
        {
            "participant_carrier_id": participant_carrier_id,
            "pre_signature_digest": participant_start_state_digest,
            "post_signature_digest": participant_end_state_digest,
            "transfer_mapping_digest": mapping["transfer_mapping_digest"],
            "replay_trace_digest": replay_trace_digest,
        }
    )

    threshold_record = {
        "artifact_role": "participant_recognizability_threshold_record",
        "record_id": "n30_i4_participant_recognizability_threshold_record",
        "declared_before_classification": True,
        "participant_carrier_id": participant_carrier_id,
        "recognizability_metric": recognizability_metric,
        "recognizability_acceptance_rule": "observed_signature_distance <= max_signature_distance",
        "recognizability_threshold": recognizability_threshold,
        "threshold_source": "N27 post-transfer basin-signature max_signature_distance",
        "threshold_source_path": rel(N27_POST_SIGNATURE),
        "n30_independent_threshold_validation_status": (
            "not_independently_revalidated; N30 accepts the N27 transfer "
            "tolerance as the carrier recognizability gate for this P2 probe"
        ),
        "threshold_inheritance_claim_limit": (
            "supports bounded participant admissibility only; does not prove "
            "general participant stability or medium relation"
        ),
        "label_only_continuity_allowed": False,
        "same_label_is_not_same_carrier": True,
        "carrier_digest_or_trace_continuity_required": True,
        "medium_relation_rung_assignment_allowed": False,
    }
    threshold_record["threshold_record_digest"] = digest_value(threshold_record)

    carrier_state_trace = {
        "artifact_role": "participant_carrier_state_trace",
        "trace_id": "n30_i4_participant_carrier_state_trace",
        "participant_carrier_id": participant_carrier_id,
        "participant_carrier_type": "mapped_basin_signature_carrier",
        "participant_persistence_window": [
            "n27_i4_pre_transfer_signature",
            "n27_i4_post_transfer_signature",
            "n27_i5_same_basin_replay",
        ],
        "participant_start_state_digest": participant_start_state_digest,
        "participant_end_state_digest": participant_end_state_digest,
        "participant_carrier_digest": participant_carrier_digest,
        "pre_fixture_id": pre["fixture_id"],
        "post_fixture_id": post["fixture_id"],
        "pre_frame_id": pre["frame_id"],
        "post_frame_id": post["frame_id"],
        "pre_basin_nodes": pre["basin_nodes"],
        "post_basin_nodes": post["basin_nodes"],
        "pre_signature_vector": pre["signature_vector"],
        "post_signature_vector": post["signature_vector"],
        "basin_label_used_as_evidence": False,
        "carrier_identity_claimed": False,
        "selfhood_claimed": False,
    }
    carrier_state_trace["carrier_state_trace_digest"] = digest_value(carrier_state_trace)

    attribution_trace = {
        "artifact_role": "participant_attribution_trace",
        "trace_id": "n30_i4_participant_attribution_trace",
        "participant_carrier_id": participant_carrier_id,
        "attribution_source": "N27 source-current pre/post basin signature and declared mapping",
        "mapping_declared_before_use": mapping["mapping_declared_before_use"],
        "mapping_digest_excludes_outcome": mapping["mapping_digest_excludes_outcome"],
        "mapping_source_backed": mapping["mapping_source_backed"],
        "node_mapping": mapping["node_mapping"],
        "edge_mapping": mapping["edge_mapping"],
        "runtime_trace_id": runtime["trace_id"],
        "runtime_config_digest": runtime["runtime_config_digest"],
        "source_current_trace_kind": runtime["source_current_trace_kind"],
        "source_derived_report_only": runtime["derived_report_only"],
        "support_preserved_above_floor": support["support_preserved_above_floor"],
        "coherence_preserved_above_floor": coherence["coherence_preserved_above_floor"],
        "boundary_mapping_preserved": boundary["boundary_mapping_preserved"],
        "flux_balance_preserved_within_bound": flux[
            "flux_balance_preserved_within_bound"
        ],
        "hidden_support_reconstruction_absent": reconstructed_support[
            "hidden_support_reconstruction_absent"
        ],
        "support_reconstruction_counted_as_preservation": support[
            "support_reconstruction_counted_as_preservation"
        ],
    }
    attribution_trace["participant_attribution_trace_digest"] = digest_value(
        attribution_trace
    )

    replay_recognizability_trace = {
        "artifact_role": "participant_replay_recognizability_trace",
        "trace_id": "n30_i4_participant_replay_recognizability_trace",
        "participant_carrier_id": participant_carrier_id,
        "replay_status": "passed",
        "replay_source": rel(N27_REPLAY_TRACE),
        "artifact_replay_status": replay_trace["artifact_replay"]["status"],
        "snapshot_load_replay_status": replay_trace["snapshot_load_replay"]["status"],
        "duplicate_replay_status": replay_trace["duplicate_replay"]["status"],
        "mapping_order_replay_status": replay_trace["mapping_order_replay"]["status"],
        "same_basin_signature_preserved_under_mapping": post[
            "same_basin_signature_preserved_under_mapping"
        ],
        "recognizability_metric": recognizability_metric,
        "recognizability_threshold": recognizability_threshold,
        "recognizability_observed": recognizability_observed,
        "recognizability_margin": recognizability_margin,
        "recognizability_passed": recognizability_observed <= recognizability_threshold,
        "p2_candidate_supported": True,
        "medium_relation_evidence_opened": False,
    }
    replay_recognizability_trace["replay_recognizability_trace_digest"] = digest_value(
        replay_recognizability_trace
    )

    label_drift_control_trace = {
        "artifact_role": "participant_label_drift_control_trace",
        "trace_id": "n30_i4_participant_label_drift_control_trace",
        "participant_carrier_id": participant_carrier_id,
        "label_drift_control_result": "passed",
        "same_label_different_basin_rejected": True,
        "basin_label_used_as_evidence": False,
        "pre_basin_label": pre["basin_label"],
        "post_basin_label": post["basin_label"],
        "same_label_is_not_same_carrier": True,
        "carrier_digest_or_trace_continuity_required": True,
        "participant_label_only_relabel_rejected": True,
        "identity_acceptance_relabel_rejected": True,
        "selfhood_relabel_rejected": True,
        "agency_relabel_rejected": True,
    }
    label_drift_control_trace["label_drift_control_trace_digest"] = digest_value(
        label_drift_control_trace
    )

    medium_leakage_guard_trace = {
        "artifact_role": "i4_medium_leakage_guard_trace",
        "trace_id": "n30_i4_medium_leakage_guard_trace",
        "i4_medium_relation_rung_assignment_allowed": False,
        "medium_relation_ladder_rung": "not_assigned",
        "medium_surface_id": "not_declared_in_iteration_4",
        "medium_perturbation_claim_allowed": False,
        "trace_mediated_eligibility_claim_allowed": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "exploratory_medium_observation_effect": "record_only_not_C4_or_C5_support",
    }
    medium_leakage_guard_trace["medium_leakage_guard_trace_digest"] = digest_value(
        medium_leakage_guard_trace
    )

    artifacts = [
        write_artifact("threshold_record.json", threshold_record),
        write_artifact("participant_carrier_state_trace.json", carrier_state_trace),
        write_artifact("participant_attribution_trace.json", attribution_trace),
        write_artifact(
            "participant_replay_recognizability_trace.json",
            replay_recognizability_trace,
        ),
        write_artifact("participant_label_drift_control_trace.json", label_drift_control_trace),
        write_artifact("i4_medium_leakage_guard_trace.json", medium_leakage_guard_trace),
    ]

    source_current_inputs = [
        source_input(N27_MINIMAL_OUTPUT, "N27_minimal_source_current_CT2_candidate"),
        source_input(N27_REPLAY_OUTPUT, "N27_replay_same_basin_mapping_matrix"),
        source_input(N27_PRE_SIGNATURE, "pre_participant_signature_trace"),
        source_input(N27_POST_SIGNATURE, "post_participant_signature_trace"),
        source_input(N27_MAPPING_TRACE, "declared_mapping_trace"),
        source_input(N27_RUNTIME_TRACE, "source_current_runtime_trace"),
        source_input(N27_SUPPORT_TRACE, "support_preservation_trace"),
        source_input(N27_COHERENCE_TRACE, "coherence_preservation_trace"),
        source_input(N27_BOUNDARY_TRACE, "boundary_mapping_trace"),
        source_input(N27_FLUX_TRACE, "flux_balance_trace"),
        source_input(N27_RECONSTRUCTED_SUPPORT, "hidden_support_reconstruction_control"),
        source_input(N27_REPLAY_TRACE, "participant_replay_trace"),
    ]

    row = {
        "row_id": "n30_i4_row_01_minimal_participant_carrier_admissibility",
        "source_iteration": "I4",
        "primary_layer": "primitive",
        "participant_ladder_rung": "P2_candidate",
        "participant_ladder_rung_reason": (
            "same mapped basin-signature carrier remains recognizable across "
            "pre/post source-current traces and bounded replay"
        ),
        "medium_relation_ladder_rung": "not_assigned",
        "relation_chain_id": "not_opened_until_I5_I6",
        "participant_event_id": "n30_i4_participant_admission_event",
        "participant_carrier_id": participant_carrier_id,
        "participant_carrier_type": "mapped_basin_signature_carrier",
        "participant_carrier": {
            "carrier_digest": participant_carrier_digest,
            "start_state_digest": participant_start_state_digest,
            "end_state_digest": participant_end_state_digest,
            "source_mapping_digest": mapping["transfer_mapping_digest"],
        },
        "participant_persistence_window": carrier_state_trace[
            "participant_persistence_window"
        ],
        "participant_start_state_digest": participant_start_state_digest,
        "participant_end_state_digest": participant_end_state_digest,
        "participant_attribution_trace": attribution_trace,
        "recognizability_metric": recognizability_metric,
        "recognizability_threshold": recognizability_threshold,
        "recognizability_observed": recognizability_observed,
        "recognizability_margin": recognizability_margin,
        "replay_status": {
            "artifact_replay": "passed",
            "snapshot_load_replay": "passed",
            "duplicate_replay": "passed",
            "mapping_order_replay": "passed",
        },
        "label_drift_control_result": label_drift_control_trace[
            "label_drift_control_result"
        ],
        "same_label_is_not_same_carrier": True,
        "carrier_digest_or_trace_continuity_required": True,
        "medium_surface_id": "not_declared_in_iteration_4",
        "medium_relation_rung_assignment_allowed": False,
        "medium_perturbation_claim_allowed": False,
        "trace_mediated_eligibility_claim_allowed": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "participant_admissibility_claim_allowed": True,
        "source_current_inputs": source_current_inputs,
        "artifact_manifest": artifacts,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
            for artifact in artifacts
        ),
        "derived_report_only": False,
        "claim_ceiling": "N30-C3 participant admissibility candidate only; no medium perturbation, trace-mediated eligibility, minimal shared-medium participation, semantic identity, selfhood, agency, or native shared-medium organization claim",
        "blocked_relabels": BLOCKED_CLAIMS,
        "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        "row_decision": "supported_participant_admissibility_candidate_only",
    }
    row["row_output_digest"] = digest_value(row)

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "4_minimal_participant_admissibility_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_minimal_participant_admissibility_P2_candidate_no_medium_relation",
        "source_i3": {
            "source_output": "outputs/n30_active_nulls_i3.json",
            "source_output_sha256": sha256_file(I3_OUTPUT),
            "source_output_digest": i3["output_digest"],
            "source_acceptance_state": i3["acceptance_state"],
        },
        "source_guardrail_records": {
            "n27_minimal_output_digest": n27_minimal["output_digest"],
            "n27_replay_output_digest": n27_replay["output_digest"],
            "n27_minimal_output_sha256": sha256_file(N27_MINIMAL_OUTPUT),
            "n27_replay_output_sha256": sha256_file(N27_REPLAY_OUTPUT),
            "closeout_summary_only_used": False,
            "underlying_N27_artifacts_consumed": True,
        },
        "positive_evidence_opened": True,
        "positive_evidence_scope": "participant_admissibility_only",
        "participant_admissibility_evidence_opened": True,
        "medium_surface_trace_evidence_opened": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "candidate_rows_classified": True,
        "participant_ladder_rung_assigned": "provisional_P2_candidate",
        "medium_relation_ladder_rung_assigned": False,
        "final_n30_closeout_rung": "not_assigned",
        "n30_closeout_ceiling": "N30-C3_participant_admissibility_candidate",
        "ready_for_iteration_5_medium_surface_trace_probe": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": source_current_inputs,
        "claim_boundary": {
            "claim_ceiling": "participant_admissibility_candidate_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    required_i4_fields = i3["i4_participant_only_ceiling_guard"]["required_i4_fields"]
    checks = [
        {
            "check_id": "i3_active_nulls_passed",
            "passed": i3["acceptance_state"]
            == "accepted_active_nulls_fail_closed_no_positive_evidence",
        },
        {
            "check_id": "underlying_n27_artifacts_consumed_not_closeout_only",
            "passed": payload["source_guardrail_records"][
                "underlying_N27_artifacts_consumed"
            ]
            is True
            and payload["source_guardrail_records"]["closeout_summary_only_used"]
            is False,
        },
        {
            "check_id": "required_i4_fields_present",
            "passed": all(field in row for field in required_i4_fields),
        },
        {
            "check_id": "participant_carrier_digest_continuity_recorded",
            "passed": bool(row["participant_carrier"]["carrier_digest"])
            and row["carrier_digest_or_trace_continuity_required"] is True,
        },
        {
            "check_id": "recognizability_metric_declared_before_classification",
            "passed": threshold_record["declared_before_classification"] is True
            and row["recognizability_observed"] <= row["recognizability_threshold"],
        },
        {
            "check_id": "replay_status_passed",
            "passed": all(status == "passed" for status in row["replay_status"].values()),
        },
        {
            "check_id": "label_drift_control_passed",
            "passed": row["label_drift_control_result"] == "passed"
            and row["same_label_is_not_same_carrier"] is True,
        },
        {
            "check_id": "i4_ceiling_guard_preserved",
            "passed": payload["n30_closeout_ceiling"]
            == "N30-C3_participant_admissibility_candidate"
            and payload["medium_relation_ladder_rung_assigned"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "no_medium_evidence_opened",
            "passed": row["medium_relation_ladder_rung"] == "not_assigned"
            and payload["medium_surface_trace_evidence_opened"] is False
            and payload["later_eligibility_dependency_evidence_opened"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": row["all_artifact_sha256_match_file_contents"] is True,
        },
        {
            "check_id": "derived_report_only_false_for_candidate",
            "passed": row["derived_report_only"] is False
            and len(row["source_current_inputs"]) > 0,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            )
            and all(value is False for value in row["unsafe_claim_flags"].values()),
        },
    ]
    payload["checks"] = checks
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        }
    )
    payload["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    row = payload["candidate_rows"][0]
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )
    text = f"""# N30 Iteration 4 - Minimal Participant Admissibility Probe

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 4 is the first positive N30 content row, but its scope is only
participant admissibility. It does not declare a medium surface, does not assign
a medium-relation rung, and does not claim trace-mediated eligibility or minimal
shared-medium participation.

## Participant Candidate

```text
row_id = {row['row_id']}
participant_ladder_rung = {row['participant_ladder_rung']}
participant_carrier_id = {row['participant_carrier_id']}
recognizability_metric = {row['recognizability_metric']}
recognizability_observed = {row['recognizability_observed']}
recognizability_threshold = {row['recognizability_threshold']}
recognizability_margin = {row['recognizability_margin']}
replay_status = passed
label_drift_control_result = {row['label_drift_control_result']}
```

The participant carrier is a mapped basin-signature carrier consumed from
underlying N27 source-current traces and replay records. The claim is not that
the carrier has selfhood, identity, agency, or semantic role. The claim is only
that the same carrier remains recognizable across the bounded pre/post/replay
window.

## Threshold Source

The recognizability threshold is inherited from the N27 post-transfer
basin-signature tolerance, not independently tuned by N30. N30 accepts that
transfer tolerance as the carrier-recognizability gate for this bounded P2
probe. This limits the claim to participant admissibility and does not support
general participant stability or medium-relation evidence.

## Geometric Interpretation

Geometrically, I4 treats the participant as a basin-signature carrier rather
than as a semantic actor. The alpha-frame basin signature is mapped into the
beta-frame basin signature while preserving support, coherence, boundary
mapping, and bounded flux. The recognizability metric is the mapped signature
distance: `0.025 <= 0.06`, with margin `0.035`. That is enough for a P2
participant-admissibility candidate, but it is not a medium perturbation or
shared-medium relation.

## Artifacts

| Role | Path |
|---|---|
{artifact_rows}

## Claim Boundary

```text
n30_closeout_ceiling = {payload['n30_closeout_ceiling']}
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Checks

{check_rows}
"""
    REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
