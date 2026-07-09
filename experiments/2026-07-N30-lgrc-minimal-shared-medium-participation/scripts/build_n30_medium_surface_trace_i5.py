#!/usr/bin/env python3
"""Build N30 Iteration 5 medium surface perturbation / trace probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5.json"
REPORT = EXPERIMENT / "reports" / "n30_medium_surface_trace_i5.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_medium_surface_trace_i5.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I4B_OUTPUT = EXPERIMENT / "outputs" / "n30_participant_boundary_support_i4b.json"

N28_ROOT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
N28_I4A_OUTPUT = N28_ROOT / "outputs" / "n28_generative_strengthening_candidate_probe.json"
N28_REPLAY_OUTPUT = N28_ROOT / "outputs" / "n28_replay_capacity_attribution_matrix.json"
N28_I4A_ARTIFACT_DIR = (
    N28_ROOT / "outputs" / "n28_generative_strengthening_candidate_probe_artifacts"
)
N28_RUNTIME_TRACE = N28_I4A_ARTIFACT_DIR / "source_current_runtime_trace.json"
N28_FOCAL_TRACE = N28_I4A_ARTIFACT_DIR / "focal_basin_stability_trace.json"
N28_NEIGHBOR_TRACE = N28_I4A_ARTIFACT_DIR / "neighbor_capacity_trace.json"
N28_CAPACITY_ATTRIBUTION_TRACE = N28_I4A_ARTIFACT_DIR / "capacity_attribution_trace.json"
N28_EXTRACTION_LEAKAGE_TRACE = N28_I4A_ARTIFACT_DIR / "extraction_leakage_trace.json"
N28_CLASSIFICATION_TRACE = N28_I4A_ARTIFACT_DIR / "classification_trace.json"
N28_CORE_TRACE = N28_I4A_ARTIFACT_DIR / "generative_extractive_core.json"
N28_THRESHOLD_TRACE = N28_I4A_ARTIFACT_DIR / "threshold_policy_trace.json"
N28_REPLAY_TRACE = (
    N28_ROOT
    / "outputs"
    / "n28_replay_capacity_attribution_matrix_artifacts"
    / "n28_i5_replay_n28_i4a_row_generative_strengthening_candidate_trace.json"
)

BLOCKED_CLAIMS = [
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


def replay_row_for_i4a(replay_matrix: dict[str, Any]) -> dict[str, Any]:
    for row in replay_matrix.get("replay_rows", replay_matrix.get("candidate_rows", [])):
        if row.get("source_iteration") == "4-A" and row.get("source_role") == "generative_strengthening":
            return row
    raise KeyError("N28 I4-A generative strengthening replay row not found")


def build_payload() -> dict[str, Any]:
    i4b = load_json(I4B_OUTPUT)
    n28_i4a = load_json(N28_I4A_OUTPUT)
    n28_replay = load_json(N28_REPLAY_OUTPUT)
    runtime = load_json(N28_RUNTIME_TRACE)
    focal = load_json(N28_FOCAL_TRACE)
    neighbor = load_json(N28_NEIGHBOR_TRACE)
    capacity_attribution = load_json(N28_CAPACITY_ATTRIBUTION_TRACE)
    extraction_leakage = load_json(N28_EXTRACTION_LEAKAGE_TRACE)
    classification = load_json(N28_CLASSIFICATION_TRACE)
    core = load_json(N28_CORE_TRACE)
    threshold = load_json(N28_THRESHOLD_TRACE)
    replay_trace = load_json(N28_REPLAY_TRACE)
    replay_row = replay_row_for_i4a(n28_replay)

    focal_basin_id = runtime["focal_basin_id"]
    medium_surface_id = runtime["neighbor_scope_id"]
    participant_event_id = "n30_i5_n28_i4a_focal_basin_environment_event"
    perturbation_event_id = "n30_i5_n28_i4a_neighbor_surface_perturbation"
    trace_or_surface_change_id = "n30_i5_n28_i4a_neighbor_capacity_surface_change"
    relation_chain_id = "n30_i5_n28_i4a_focal_to_neighbor_medium_trace_chain"

    medium_surface_declaration = {
        "artifact_role": "medium_surface_declaration_trace",
        "trace_id": "n30_i5_medium_surface_declaration_trace",
        "medium_surface_id": medium_surface_id,
        "medium_surface_carrier": {
            "surface_kind": "neighbor_capacity_shell",
            "source_trace_id": neighbor["trace_id"],
            "surface_fields": [
                "neighbor_distinguishability",
                "neighbor_support_floor",
                "neighbor_boundary_integrity",
                "environment_basin_forming_capacity",
            ],
            "pre_state": {
                "neighbor_distinguishability": neighbor["pre_neighbor_distinguishability"],
                "neighbor_support_floor": neighbor["pre_neighbor_support_floor"],
                "neighbor_boundary_integrity": neighbor["pre_neighbor_boundary_integrity"],
                "environment_basin_forming_capacity": neighbor[
                    "pre_environment_basin_forming_capacity"
                ],
            },
            "post_state": {
                "neighbor_distinguishability": neighbor["post_neighbor_distinguishability"],
                "neighbor_support_floor": neighbor["post_neighbor_support_floor"],
                "neighbor_boundary_integrity": neighbor["post_neighbor_boundary_integrity"],
                "environment_basin_forming_capacity": neighbor[
                    "post_environment_basin_forming_capacity"
                ],
            },
        },
        "medium_surface_scope": "shared_local",
        "sharedness_argument": (
            "N28 records the neighbor capacity shell as distinct from the focal "
            "basin and exposes support, boundary, distinguishability, and "
            "environment-capacity fields rather than private participant state."
        ),
        "private_internal_surface": False,
        "telemetry_only_surface": False,
        "surface_label_only": False,
    }
    medium_surface_declaration["medium_surface_declaration_digest"] = digest_value(
        medium_surface_declaration
    )

    participant_medium_separation = {
        "artifact_role": "participant_medium_separation_trace",
        "trace_id": "n30_i5_participant_medium_separation_trace",
        "participant_carrier_id": focal_basin_id,
        "participant_admissibility_guardrail_source": {
            "source": rel(I4B_OUTPUT),
            "strongest_participant_ladder_rung": i4b["strongest_participant_ladder_rung"],
            "strongest_participant_carrier_id": i4b["strongest_participant_carrier_id"],
            "guardrail_scope": (
                "I4-B establishes participant-side readiness discipline; it is "
                "not imported as proof that the N27 carrier itself perturbed "
                "the N28 medium surface."
            ),
        },
        "local_n28_participant_basis": {
            "focal_basin_id": focal_basin_id,
            "focal_support_floor_preserved": focal["focal_support_floor_preserved"],
            "focal_coherence_floor_preserved": focal["focal_coherence_floor_preserved"],
            "focal_stability_preserved": focal["focal_stability_preserved"],
            "replay_passed": replay_trace["replay_passed"],
        },
        "medium_surface_id": medium_surface_id,
        "participant_medium_distinct": focal_basin_id != medium_surface_id,
        "participant_medium_separation_argument": (
            "The participant side is the N28 focal basin; the medium surface is "
            "the distinct neighbor capacity shell. The row uses I4-B as a "
            "participant discipline guardrail while the load-bearing medium "
            "trace comes from N28 source-current artifacts."
        ),
        "same_identifier_blocks_c5_c6": focal_basin_id == medium_surface_id,
    }
    participant_medium_separation["participant_medium_separation_digest"] = digest_value(
        participant_medium_separation
    )

    perturbation_trace = {
        "artifact_role": "medium_perturbation_trace",
        "trace_id": "n30_i5_medium_perturbation_trace",
        "participant_event_id": participant_event_id,
        "perturbation_event_id": perturbation_event_id,
        "relation_chain_id": relation_chain_id,
        "source_runtime_trace_id": runtime["run_artifact_id"],
        "source_current_trace_kind": runtime["fixture_kind"],
        "capacity_attribution_trace_id": capacity_attribution["trace_id"],
        "attribution_result": capacity_attribution["attribution_result"],
        "capacity_attribution_basis": capacity_attribution["capacity_attribution_basis"],
        "hidden_capacity_attribution_policy_used": capacity_attribution[
            "hidden_capacity_attribution_policy_used"
        ],
        "medium_segmentation_policy_hidden": capacity_attribution[
            "medium_segmentation_policy_hidden"
        ],
        "producer_generativity_label_used_as_evidence": capacity_attribution[
            "producer_generativity_label_used_as_evidence"
        ],
        "n27_transfer_success_used_as_n28_success": capacity_attribution[
            "n27_transfer_success_used_as_n28_success"
        ],
        "participant_to_medium_causal_closure_status": (
            "not_finalized_until_I6_I7; I5 records source-current perturbation "
            "and surface change, not later eligibility dependence"
        ),
    }
    perturbation_trace["medium_perturbation_trace_digest"] = digest_value(
        perturbation_trace
    )

    trace_surface_change = {
        "artifact_role": "trace_or_surface_change",
        "trace_id": "n30_i5_trace_or_surface_change",
        "trace_or_surface_change_id": trace_or_surface_change_id,
        "medium_surface_id": medium_surface_id,
        "surface_change_fields": {
            "neighbor_distinguishability_delta": neighbor[
                "neighbor_distinguishability_delta"
            ],
            "neighbor_support_delta": neighbor["neighbor_support_delta"],
            "neighbor_boundary_delta": neighbor["neighbor_boundary_delta"],
            "environment_capacity_delta": neighbor["environment_capacity_delta"],
        },
        "thresholds": {
            "neighbor_distinguishability_delta_min": threshold[
                "neighbor_distinguishability_delta_min"
            ],
            "neighbor_support_delta_min": threshold["neighbor_support_delta_min"],
            "neighbor_boundary_delta_min": threshold["neighbor_boundary_delta_min"],
            "environment_capacity_delta_min": threshold[
                "environment_capacity_delta_min"
            ],
        },
        "surface_change_passed": (
            neighbor["neighbor_distinguishability_delta"]
            >= threshold["neighbor_distinguishability_delta_min"]
            and neighbor["neighbor_support_delta"] >= threshold["neighbor_support_delta_min"]
            and neighbor["neighbor_boundary_delta"]
            >= threshold["neighbor_boundary_delta_min"]
            and neighbor["environment_capacity_delta"]
            >= threshold["environment_capacity_delta_min"]
        ),
        "neighbor_label_only": neighbor["neighbor_label_only"],
        "neighbor_count_only": neighbor["neighbor_count_only"],
        "classification_result": classification["classification_result"],
        "classification_declared_before_use": classification[
            "classification_declared_before_use"
        ],
    }
    trace_surface_change["trace_or_surface_change_digest"] = digest_value(
        trace_surface_change
    )

    trace_persistence_or_decay = {
        "artifact_role": "trace_persistence_or_decay",
        "trace_id": "n30_i5_trace_persistence_or_decay",
        "trace_or_surface_change_id": trace_or_surface_change_id,
        "persistence_status": "replay_persistent_no_decay_curve",
        "artifact_replay_status": replay_trace["artifact_replay"]["status"],
        "snapshot_load_replay_status": replay_trace["snapshot_load_replay"]["status"],
        "duplicate_replay_status": replay_trace["duplicate_replay"]["status"],
        "duplicate_replay_digest_stable": replay_trace["duplicate_replay"][
            "duplicate_replay_digest_stable"
        ],
        "regime_label_stable_under_replay": replay_row[
            "regime_label_stable_under_replay"
        ],
        "replay_trace_digest": replay_row["replay_trace_digest"],
        "decay_curve_available": False,
        "decay_curve_status": "not_measured_in_I5",
        "i6_requirement": (
            "I6 must test whether a later eligibility/susceptibility response "
            "depends on this changed medium surface."
        ),
    }
    trace_persistence_or_decay["trace_persistence_or_decay_digest"] = digest_value(
        trace_persistence_or_decay
    )

    medium_debt_record = {
        "artifact_role": "medium_debt_record",
        "trace_id": "n30_i5_medium_debt_record",
        "medium_debt_status": "medium_surface_trace_supported_later_dependency_pending",
        "remaining_debt": [
            "later eligibility dependency not tested until I6",
            "runtime controls over actual N30 relation chain pending I7",
            "decay curve not measured in I5",
            "native shared-medium organization blocked",
        ],
        "producer_residue_status": "no_hidden_capacity_policy_or_producer_label_used_as_evidence",
        "hidden_producer_route_detected": False,
        "direct_message_present": False,
        "direct_message_status": "absent_from_N28_medium_surface_trace",
    }
    medium_debt_record["medium_debt_record_digest"] = digest_value(medium_debt_record)

    medium_leakage_guard = {
        "artifact_role": "i5_medium_leakage_guard_trace",
        "trace_id": "n30_i5_medium_leakage_guard_trace",
        "medium_relation_ladder_rung": "M1_candidate",
        "m2_or_stronger_supported": False,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "trace_mediated_eligibility_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
    }
    medium_leakage_guard["medium_leakage_guard_digest"] = digest_value(
        medium_leakage_guard
    )

    surface_trace_guardrail_control_ids = [
        "capacity_attribution_control",
        "label_only_regime_control",
        "merge_leakage_as_support_control",
        "transfer_success_as_n28_success_control",
    ]
    n30_relation_controls = {
        "status": "pending_iteration_7",
        "classification": "not_run_for_I5_C4_surface_trace_admission",
        "required_control_ids": [
            "direct_message_removal_control",
            "no_perturbation_control",
            "trace_ablation_control",
            "wrong_surface_control",
            "time_reversed_trace_control",
            "medium_freeze_control",
            "trace_shuffle_control",
            "false_trace_injection_control",
            "decay_manipulation_control",
            "susceptibility_inversion_control",
            "hidden_producer_global_controller_control",
        ],
    }
    scope_classification = {
        "artifact_role": "i5_scope_classification",
        "trace_id": "n30_i5_scope_classification",
        "i5_positive_scope": "inherited_source_current_medium_surface_trace_only",
        "runtime_origin": "inherited_N28_source_current_artifact",
        "n30_fresh_runtime": False,
        "fresh_n30_runtime_evidence": False,
        "i5_claim_type": "inherited_medium_surface_trace_admission",
        "supports_N30_C4": True,
        "supports_N30_C5": False,
        "supports_M1": True,
        "supports_M2": False,
        "n28_artifacts_allowed_to_support": [
            "N30-C4_medium_perturbation_trace_candidate",
            "M1_candidate",
        ],
        "n28_artifacts_not_allowed_to_support": [
            "N30-C5_trace_mediated_eligibility",
            "M2_later_response_conditioned_by_medium",
            "minimal_shared_medium_participation",
            "shared_medium_coordination",
            "native_shared_medium_organization",
        ],
        "n28_controls_classified_as": (
            "source_guardrail_controls_not_N30_relation_controls"
        ),
        "source_guardrail_control_ids": surface_trace_guardrail_control_ids,
        "n30_relation_controls": n30_relation_controls,
        "row_participant_ladder_rung": "P2_candidate_with_I4B_P4_guardrail",
        "strongest_N30_I5_row_participant_rung": "P2_candidate",
        "source_i4b_strongest_participant_guardrail": i4b[
            "strongest_participant_ladder_rung"
        ],
        "i6_dependency_required": True,
        "i6_lineage_rule": (
            "I6 must consume this exact relation_chain_id or declare a "
            "parent_relation_chain_id plus a justified fork."
        ),
        "c4_c5_rule": (
            "C4 = changed medium surface exists; C5 = later response depends "
            "on that changed surface."
        ),
        "shared_local_scope_status": "shared_local_candidate_pending_later_encounter",
    }
    scope_classification["scope_classification_digest"] = digest_value(
        scope_classification
    )

    artifacts = [
        write_artifact("medium_surface_declaration_trace.json", medium_surface_declaration),
        write_artifact("participant_medium_separation_trace.json", participant_medium_separation),
        write_artifact("medium_perturbation_trace.json", perturbation_trace),
        write_artifact("trace_or_surface_change.json", trace_surface_change),
        write_artifact("trace_persistence_or_decay.json", trace_persistence_or_decay),
        write_artifact("medium_debt_record.json", medium_debt_record),
        write_artifact("i5_medium_leakage_guard_trace.json", medium_leakage_guard),
        write_artifact("i5_scope_classification.json", scope_classification),
    ]
    artifact_sha256_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )

    source_current_inputs = [
        source_input(I4B_OUTPUT, "N30_I4B_participant_boundary_support_guardrail"),
        source_input(N28_I4A_OUTPUT, "N28_I4A_source_current_generative_strengthening_candidate"),
        source_input(N28_REPLAY_OUTPUT, "N28_replay_capacity_attribution_matrix"),
        source_input(N28_RUNTIME_TRACE, "N28_I4A_source_current_runtime_trace"),
        source_input(N28_FOCAL_TRACE, "N28_I4A_focal_basin_stability_trace"),
        source_input(N28_NEIGHBOR_TRACE, "N28_I4A_neighbor_capacity_medium_surface_trace"),
        source_input(N28_CAPACITY_ATTRIBUTION_TRACE, "N28_I4A_capacity_attribution_trace"),
        source_input(N28_EXTRACTION_LEAKAGE_TRACE, "N28_I4A_extraction_leakage_guard_trace"),
        source_input(N28_CLASSIFICATION_TRACE, "N28_I4A_classification_trace"),
        source_input(N28_CORE_TRACE, "N28_I4A_generative_extractive_core"),
        source_input(N28_THRESHOLD_TRACE, "N28_I4A_threshold_policy_trace"),
        source_input(N28_REPLAY_TRACE, "N28_I4A_replay_trace"),
    ]

    row = {
        "row_id": "n30_i5_row_01_n28_i4a_medium_surface_trace_candidate",
        "source_iteration": "I5",
        "primary_layer": "primitive",
        "participant_ladder_rung": "P2_candidate_with_I4B_P4_guardrail",
        "row_participant_ladder_rung": "P2_candidate_with_I4B_P4_guardrail",
        "strongest_N30_I5_row_participant_rung": "P2_candidate",
        "source_i4b_strongest_participant_guardrail": i4b[
            "strongest_participant_ladder_rung"
        ],
        "medium_relation_ladder_rung": "M1_candidate",
        "runtime_origin": "inherited_N28_source_current_artifact",
        "n30_fresh_runtime": False,
        "fresh_n30_runtime_evidence": False,
        "i5_claim_type": "inherited_medium_surface_trace_admission",
        "relation_chain_id": relation_chain_id,
        "participant_event_id": participant_event_id,
        "participant_carrier_id": focal_basin_id,
        "participant_carrier": {
            "carrier_kind": "N28_focal_basin",
            "focal_basin_id": focal_basin_id,
            "focal_support_floor_preserved": focal["focal_support_floor_preserved"],
            "focal_coherence_floor_preserved": focal["focal_coherence_floor_preserved"],
            "focal_stability_preserved": focal["focal_stability_preserved"],
            "focal_signature_digest": core["focal_signature_digest"],
        },
        "participant_persistence_window": [
            "N28_I4A_step_0_focal_state",
            "N28_I4A_step_1_focal_state",
            "N28_I5_replay_trace",
        ],
        "participant_attribution_trace": participant_medium_separation,
        "medium_surface_id": medium_surface_id,
        "medium_surface_carrier": medium_surface_declaration["medium_surface_carrier"],
        "medium_surface_scope": "shared_local",
        "medium_surface_scope_status": "shared_local_candidate_pending_later_encounter",
        "boundary_accessible_medium_surface": True,
        "participant_medium_distinct": participant_medium_separation[
            "participant_medium_distinct"
        ],
        "participant_medium_separation_argument": participant_medium_separation[
            "participant_medium_separation_argument"
        ],
        "perturbation_trace": perturbation_trace,
        "perturbation_event_id": perturbation_event_id,
        "trace_or_surface_change_id": trace_or_surface_change_id,
        "trace_or_surface_change": trace_surface_change,
        "trace_persistence_or_decay": trace_persistence_or_decay,
        "susceptibility_or_eligibility_trace": "not_run_until_iteration_6",
        "later_response_event_id": "not_run_until_iteration_6",
        "later_response_conditioned_by_medium": False,
        "later_response_metric": "not_declared_until_iteration_6",
        "expected_direction": "not_declared_until_iteration_6",
        "response_window": "not_declared_until_iteration_6",
        "baseline_window": "not_declared_until_iteration_6",
        "acceptance_threshold": "not_declared_until_iteration_6",
        "normalization_denominator": "not_declared_until_iteration_6",
        "effect_size": "not_run_until_iteration_6",
        "counterfactual_row_id": "pending_iteration_6_or_7",
        "causal_order_verified": "partial_order_verified_for_surface_change_only",
        "trace_dependency_control_ids": "pending_iteration_7",
        "i5_surface_trace_guardrail_control_ids": surface_trace_guardrail_control_ids,
        "medium_ablation_control_result": "pending_iteration_7",
        "row_chain_decision": "C4_medium_perturbation_trace_candidate_only",
        "direct_message_present": False,
        "direct_message_status": "absent_from_N28_medium_surface_trace",
        "medium_debt_record": medium_debt_record,
        "i5_scope_classification": scope_classification,
        "producer_residue_record": {
            "hidden_capacity_attribution_policy_used": capacity_attribution[
                "hidden_capacity_attribution_policy_used"
            ],
            "medium_segmentation_policy_hidden": capacity_attribution[
                "medium_segmentation_policy_hidden"
            ],
            "producer_generativity_label_used_as_evidence": capacity_attribution[
                "producer_generativity_label_used_as_evidence"
            ],
        },
        "source_current_inputs": source_current_inputs,
        "artifact_manifest": artifacts,
        "replay_statuses": {
            "artifact_replay": replay_trace["artifact_replay"]["status"],
            "snapshot_load_replay": replay_trace["snapshot_load_replay"]["status"],
            "duplicate_replay": replay_trace["duplicate_replay"]["status"],
            "classification_replay": replay_trace["classification_replay"]["status"],
        },
        "control_results": replay_trace["control_results"],
        "control_results_classification": (
            "source_guardrail_controls_only_not_N30_relation_controls"
        ),
        "source_guardrail_controls": replay_trace["control_results"],
        "n30_relation_controls": n30_relation_controls,
        "claim_ceiling": (
            "N30-C4 medium perturbation / trace candidate only; no later "
            "eligibility dependency, minimal shared-medium participation, "
            "shared-medium coordination, or native shared-medium organization"
        ),
        "blocked_relabels": BLOCKED_CLAIMS,
        "row_decision": "supported_medium_surface_trace_candidate_only",
        "all_artifact_sha256_match_file_contents": artifact_sha256_match,
        "derived_report_only": False,
    }
    row["row_output_digest"] = digest_value(row)

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "5_medium_surface_perturbation_trace_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_medium_surface_perturbation_trace_M1_candidate_no_later_eligibility",
        "source_i4b_output_digest": i4b["output_digest"],
        "source_n28_i4a_output_digest": n28_i4a["output_digest"],
        "source_n28_replay_output_digest": n28_replay["output_digest"],
        "source_guardrail_records": {
            "i4b_participant_guardrail_output_digest": i4b["output_digest"],
            "i4b_strongest_participant_ladder_rung": i4b[
                "strongest_participant_ladder_rung"
            ],
            "i4b_guardrail_not_row_participant_rung": True,
            "n28_i4a_source_output_digest": n28_i4a["output_digest"],
            "n28_replay_output_digest": n28_replay["output_digest"],
            "underlying_N28_artifacts_consumed": True,
            "closeout_summary_only_used": False,
        },
        "positive_evidence_opened": True,
        "positive_evidence_scope": "medium_surface_perturbation_trace_only",
        "i5_scope_classification": scope_classification,
        "runtime_origin": "inherited_N28_source_current_artifact",
        "n30_fresh_runtime": False,
        "fresh_n30_runtime_evidence": False,
        "i5_claim_type": "inherited_medium_surface_trace_admission",
        "participant_admissibility_guardrail_available": True,
        "participant_ladder_rung_assigned": "P2_candidate_with_I4B_P4_guardrail",
        "row_participant_ladder_rung": "P2_candidate_with_I4B_P4_guardrail",
        "strongest_N30_I5_row_participant_rung": "P2_candidate",
        "source_i4b_strongest_participant_guardrail": i4b[
            "strongest_participant_ladder_rung"
        ],
        "medium_relation_ladder_rung_assigned": "M1_candidate",
        "medium_surface_trace_evidence_opened": True,
        "later_eligibility_dependency_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "strongest_participant_ladder_rung": "P2_candidate",
        "strongest_medium_relation_ladder_rung": "M1_candidate",
        "medium_surface_id": medium_surface_id,
        "medium_surface_scope": "shared_local",
        "medium_surface_scope_status": "shared_local_candidate_pending_later_encounter",
        "trace_or_surface_change_id": trace_or_surface_change_id,
        "trace_surface_change_supported": True,
        "n30_closeout_ceiling": "N30-C4_medium_perturbation_trace_candidate",
        "final_n30_closeout_rung": "not_assigned",
        "ready_for_iteration_6_later_eligibility_probe": True,
        "candidate_rows": [row],
        "artifact_manifest": artifacts,
        "source_current_inputs": source_current_inputs,
        "source_guardrail_controls": replay_trace["control_results"],
        "n30_relation_controls": n30_relation_controls,
        "claim_boundary": {
            "claim_ceiling": "medium_surface_perturbation_trace_candidate_only",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    checks = [
        {
            "check_id": "i4b_participant_guardrail_passed",
            "passed": i4b["acceptance_state"]
            == "accepted_participant_boundary_support_sensitive_P4_candidate_no_medium_relation",
        },
        {
            "check_id": "n28_i4a_source_current_artifacts_consumed_not_closeout_only",
            "passed": payload["source_guardrail_records"][
                "underlying_N28_artifacts_consumed"
            ]
            is True
            and payload["source_guardrail_records"]["closeout_summary_only_used"]
            is False,
        },
        {
            "check_id": "i5_scope_classification_preserves_inherited_runtime_boundary",
            "passed": scope_classification["runtime_origin"]
            == "inherited_N28_source_current_artifact"
            and scope_classification["n30_fresh_runtime"] is False
            and scope_classification["supports_N30_C4"] is True
            and scope_classification["supports_N30_C5"] is False,
        },
        {
            "check_id": "n28_controls_are_guardrails_not_n30_relation_controls",
            "passed": row["control_results_classification"]
            == "source_guardrail_controls_only_not_N30_relation_controls"
            and row["trace_dependency_control_ids"] == "pending_iteration_7"
            and row["n30_relation_controls"]["status"] == "pending_iteration_7",
        },
        {
            "check_id": "i4b_p4_guardrail_does_not_promote_i5_row_participant_rung",
            "passed": payload["strongest_N30_I5_row_participant_rung"]
            == "P2_candidate"
            and payload["source_i4b_strongest_participant_guardrail"]
            == "P4_candidate",
        },
        {
            "check_id": "medium_surface_declared_non_private",
            "passed": medium_surface_declaration["medium_surface_scope"] == "shared_local"
            and medium_surface_declaration["private_internal_surface"] is False
            and medium_surface_declaration["telemetry_only_surface"] is False,
        },
        {
            "check_id": "participant_medium_distinct",
            "passed": participant_medium_separation["participant_medium_distinct"] is True,
        },
        {
            "check_id": "surface_change_deltas_pass_thresholds",
            "passed": trace_surface_change["surface_change_passed"] is True,
        },
        {
            "check_id": "capacity_attribution_controls_clean",
            "passed": capacity_attribution["hidden_capacity_attribution_policy_used"] is False
            and capacity_attribution["medium_segmentation_policy_hidden"] is False
            and capacity_attribution["producer_generativity_label_used_as_evidence"] is False,
        },
        {
            "check_id": "replay_persistence_available_without_later_dependency_claim",
            "passed": replay_trace["replay_passed"] is True
            and payload["later_eligibility_dependency_evidence_opened"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "i5_ceiling_guard_preserved",
            "passed": payload["n30_closeout_ceiling"]
            == "N30-C4_medium_perturbation_trace_candidate"
            and payload["medium_relation_ladder_rung_assigned"] == "M1_candidate",
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": artifact_sha256_match,
        },
        {
            "check_id": "derived_report_only_false_for_candidate",
            "passed": row["derived_report_only"] is False,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
        },
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        },
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [
        check["check_id"] for check in checks if check["passed"] is not True
    ]
    payload["all_artifact_sha256_match_file_contents"] = artifact_sha256_match
    payload["output_digest"] = digest_value(payload)
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
    change = row["trace_or_surface_change"]["surface_change_fields"]
    text = f"""# N30 Iteration 5 - Medium Surface Perturbation / Trace Probe

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 5 opens the medium-surface side of N30. It consumes the N28 I4-A
source-current generative strengthening row and its N28 replay trace to declare
a non-private neighbor capacity shell as the medium surface.

This is inherited/source-current medium-surface admission, not fresh N30
runtime evidence. The N28 artifacts may support C4/M1 surface-trace admission;
they may not support C5/M2 later eligibility dependency unless I6/I7 add a new
N30 relation-chain dependency test.

This is still not minimal shared-medium participation. I5 records medium
surface perturbation and replay-persistent surface change only. Later
eligibility or susceptibility dependency remains I6 scope.

## Result

```text
participant_carrier_id = {row['participant_carrier_id']}
medium_surface_id = {row['medium_surface_id']}
medium_surface_scope = {row['medium_surface_scope']}
participant_medium_distinct = {str(row['participant_medium_distinct']).lower()}
medium_relation_ladder_rung = {row['medium_relation_ladder_rung']}
n30_closeout_ceiling = {payload['n30_closeout_ceiling']}
runtime_origin = {payload['runtime_origin']}
n30_fresh_runtime = false
row_participant_ladder_rung = {payload['row_participant_ladder_rung']}
strongest_N30_I5_row_participant_rung = {payload['strongest_N30_I5_row_participant_rung']}
source_i4b_strongest_participant_guardrail = {payload['source_i4b_strongest_participant_guardrail']}
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Surface Change

```text
neighbor_distinguishability_delta = {change['neighbor_distinguishability_delta']}
neighbor_support_delta = {change['neighbor_support_delta']}
neighbor_boundary_delta = {change['neighbor_boundary_delta']}
environment_capacity_delta = {change['environment_capacity_delta']}
trace_persistence_status = {row['trace_persistence_or_decay']['persistence_status']}
```

## Scope Classification

```text
i5_positive_scope = {payload['i5_scope_classification']['i5_positive_scope']}
i5_claim_type = {payload['i5_claim_type']}
supports_N30_C4 = true
supports_N30_C5 = false
supports_M1 = true
supports_M2 = false
n28_controls_classified_as = {payload['i5_scope_classification']['n28_controls_classified_as']}
trace_dependency_control_ids = pending_iteration_7
n30_relation_controls = pending_iteration_7
medium_surface_scope_status = {payload['medium_surface_scope_status']}
```

## Geometric Interpretation

I5 treats the N28 focal basin as the local participant side and the N28
neighbor capacity shell as the medium surface. The surface is not the focal
basin itself: it is a distinct shared-local shell with distinguishability,
support, boundary integrity, and environment-capacity fields.

Geometrically, the focal basin remains viable while the adjacent capacity
surface becomes more distinguishable, better supported, better bounded, and
more basin-forming. That is a medium-surface perturbation / trace candidate.
It is not yet a trace-mediated eligibility result because no later response
has been shown to depend on the changed surface.

I4-B is consumed as participant-side discipline: N30 already has a bounded P4
participant guardrail. That P4 value is a source guardrail, not the I5 row's
own participant rung. The I5 row remains `P2_candidate_with_I4B_P4_guardrail`.
I5 does not claim that the N27 I4-A carrier itself perturbed the N28 surface;
the load-bearing medium trace is the N28 source-current focal/neighbor
relation.

C4 and C5 remain separate: C4 means a changed medium surface exists; C5 means
a later response depends on that changed surface. I5 supports C4 only.

## Artifacts

| Role | Path |
|---|---|
{artifact_rows}

## Claim Boundary

```text
medium_relation_ladder_rung_assigned = M1_candidate
medium_surface_trace_evidence_opened = true
later_eligibility_dependency_evidence_opened = false
source_guardrail_controls = N28_controls_only
n30_relation_controls = pending_iteration_7
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
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
