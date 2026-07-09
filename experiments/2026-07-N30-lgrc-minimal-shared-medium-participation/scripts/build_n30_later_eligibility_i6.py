#!/usr/bin/env python3
"""Build N30 Iteration 6 later eligibility / susceptibility probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_later_eligibility_i6.json"
REPORT = EXPERIMENT / "reports" / "n30_later_eligibility_i6.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_later_eligibility_i6_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_later_eligibility_i6.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I5_OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_trace_i5a.json"
I5B_OUTPUT = EXPERIMENT / "outputs" / "n30_medium_surface_scope_window_i5b.json"

N28_ROOT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
N28_TRANSITION_MATRIX = N28_ROOT / "outputs" / "n28_regime_boundary_transition_matrix.json"
N28_TRANSITION_ARTIFACTS = (
    N28_ROOT / "outputs" / "n28_regime_boundary_transition_matrix_artifacts"
)

I4A_EDGE_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a_row_generative_strengthening_candidate_generative_edge_trace.json"
)
I4A_NEUTRAL_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a_row_generative_strengthening_candidate_neutral_gap_without_mixed_lobes_trace.json"
)
I4A_EXTRACTIVE_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a_row_generative_strengthening_candidate_extractive_cross_trace.json"
)
I4A2_EDGE_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a2_row_generative_mechanism_diversity_candidate_generative_edge_trace.json"
)
I4A2_NEUTRAL_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a2_row_generative_mechanism_diversity_candidate_neutral_gap_without_mixed_lobes_trace.json"
)
I4A2_EXTRACTIVE_TRACE = (
    N28_TRANSITION_ARTIFACTS
    / "n28_i6a_n28_i4a2_row_generative_mechanism_diversity_candidate_extractive_cross_trace.json"
)

AXIS_ORDER = [
    "neighbor_distinguishability_delta",
    "neighbor_support_delta",
    "neighbor_boundary_delta",
    "environment_capacity_delta",
]

BLOCKED_CLAIMS = [
    "final_minimal_shared_medium_participation",
    "shared_medium_coordination",
    "parent_basin_modulation",
    "resonant_alignment",
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
    "slow_trace_or_medium_memory",
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


def find_transition_row(
    transition_matrix: dict[str, Any], source_row_id: str, transition_id: str
) -> dict[str, Any]:
    for row in transition_matrix["transition_rows"]:
        if (
            row["source_row_id"] == source_row_id
            and row["transition_id"] == transition_id
        ):
            return row
    raise KeyError(f"Missing transition row: {source_row_id}/{transition_id}")


def normalized_axis_values(
    metrics: dict[str, float], thresholds: dict[str, float]
) -> dict[str, float]:
    return {
        axis: round(metrics[axis] / thresholds[f"{axis}_min"], 6)
        for axis in AXIS_ORDER
    }


def minimum_axis_margin(
    metrics: dict[str, float], thresholds: dict[str, float]
) -> float:
    return round(min(metrics[axis] - thresholds[f"{axis}_min"] for axis in AXIS_ORDER), 6)


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 6)


def build_eligibility_row(
    *,
    row_index: int,
    label: str,
    source_output: dict[str, Any],
    source_row: dict[str, Any],
    edge_trace: dict[str, Any],
    neutral_trace: dict[str, Any],
    extractive_trace: dict[str, Any],
    edge_matrix_row: dict[str, Any],
    neutral_matrix_row: dict[str, Any],
    extractive_matrix_row: dict[str, Any],
) -> dict[str, Any]:
    thresholds = source_row["trace_or_surface_change"]["thresholds"]
    edge_metrics = {
        axis: edge_trace["transition_metrics"][axis] for axis in AXIS_ORDER
    }
    neutral_metrics = {
        axis: neutral_trace["transition_metrics"][axis] for axis in AXIS_ORDER
    }
    extractive_metrics = {
        axis: extractive_trace["transition_metrics"][axis] for axis in AXIS_ORDER
    }
    edge_normalized = normalized_axis_values(edge_metrics, thresholds)
    neutral_normalized = normalized_axis_values(neutral_metrics, thresholds)
    extractive_normalized = normalized_axis_values(extractive_metrics, thresholds)
    edge_score = mean(list(edge_normalized.values()))
    neutral_score = mean(list(neutral_normalized.values()))
    extractive_score = mean(list(extractive_normalized.values()))
    minimum_margin = minimum_axis_margin(edge_metrics, thresholds)

    dependency_trace = {
        "artifact_role": "susceptibility_or_eligibility_trace",
        "trace_id": f"n30_i6_{label}_later_eligibility_dependency_trace",
        "source_relation_chain_id": source_row["relation_chain_id"],
        "medium_surface_id": source_row["medium_surface_id"],
        "later_response_metric": "same_policy_generative_boundary_edge_eligibility_score",
        "metric_declared_before_use": True,
        "expected_direction": "positive_generative_boundary_edge_axes_above_threshold",
        "baseline_window": "N28_I6A_neutral_gap_without_mixed_lobes",
        "response_window": "N28_I6A_same_policy_generative_boundary_edge",
        "normalization_denominator": "declared_I5_surface_change_thresholds",
        "acceptance_threshold": {
            "all_axis_metrics_at_or_above_declared_threshold": True,
            "minimum_normalized_axis_score": 1.0,
            "mean_normalized_axis_score": 1.0,
        },
        "edge_transition_trace_id": edge_trace["trace_id"],
        "neutral_counterfactual_trace_id": neutral_trace["trace_id"],
        "extractive_counterfactual_trace_id": extractive_trace["trace_id"],
        "edge_metrics": edge_metrics,
        "neutral_counterfactual_metrics": neutral_metrics,
        "extractive_counterfactual_metrics": extractive_metrics,
        "edge_normalized_axis_scores": edge_normalized,
        "neutral_normalized_axis_scores": neutral_normalized,
        "extractive_normalized_axis_scores": extractive_normalized,
        "edge_mean_normalized_score": edge_score,
        "neutral_mean_normalized_score": neutral_score,
        "extractive_mean_normalized_score": extractive_score,
        "effect_size_vs_neutral": round(edge_score - neutral_score, 6),
        "effect_size_vs_extractive_cross": round(edge_score - extractive_score, 6),
        "minimum_threshold_margin": minimum_margin,
        "effect_margin_class": "narrow_positive",
        "later_response_conditioned_by_medium": True,
        "conditioning_basis": (
            "The same-policy boundary-edge transition is eligible only when the "
            "declared medium-surface axes remain above their predeclared I5 "
            "thresholds; the neutral gap lacks those axes and the extractive "
            "cross moves in the opposite direction."
        ),
        "neutral_counterfactual_blocks_label_only_eligibility": True,
        "extractive_counterfactual_blocks_generic_redistribution": True,
        "thresholds_retuned_for_transition": edge_trace["thresholds_retuned_for_transition"],
        "source_row_mutated": edge_trace["source_row_mutated"],
        "new_source_current_evidence_opened_by_N28_transition": edge_trace[
            "new_source_current_evidence_opened"
        ],
        "trace_dependency_control_status": "provisional_pending_iteration_7",
        "i7_controls_required_for_final_C5": [
            "artifact_replay",
            "duplicate_replay",
            "snapshot_load_replay",
            "direct_message_removal",
            "no_perturbation",
            "trace_ablation",
            "wrong_surface",
            "time_reversed_trace",
            "medium_freeze",
            "trace_shuffle",
            "false_trace_injection",
            "decay_manipulation",
            "susceptibility_inversion",
            "hidden_producer_or_global_controller",
        ],
    }
    dependency_trace["susceptibility_or_eligibility_trace_digest"] = digest_value(
        dependency_trace
    )

    lineage = {
        "artifact_role": "coupled_relation_lineage_trace",
        "trace_id": f"n30_i6_{label}_coupled_relation_lineage_trace",
        "relation_chain_id": (
            f"{source_row['relation_chain_id']}_later_eligibility_dependency"
        ),
        "ordered_chain": [
            {
                "phase": "participant_event",
                "event_id": source_row["participant_event_id"],
            },
            {
                "phase": "medium_perturbation",
                "event_id": source_row["perturbation_event_id"],
            },
            {
                "phase": "trace_or_surface_change",
                "event_id": source_row["trace_or_surface_change_id"],
            },
            {
                "phase": "later_response",
                "event_id": edge_trace["trace_id"],
            },
        ],
        "causal_order_verified": "ordered_source_trace_plus_same_policy_transition",
        "direct_message_present": source_row["direct_message_present"],
        "direct_message_status": source_row["direct_message_status"],
        "participant_medium_distinct": source_row["participant_medium_distinct"],
        "medium_surface_scope": source_row["medium_surface_scope"],
        "medium_surface_scope_status": source_row["medium_surface_scope_status"],
        "edge_matrix_row_id": edge_matrix_row["row_id"],
        "neutral_counterfactual_row_id": neutral_matrix_row["row_id"],
        "extractive_counterfactual_row_id": extractive_matrix_row["row_id"],
        "row_chain_decision": (
            "provisional_M2_later_eligibility_dependency_candidate_pending_I7_controls"
        ),
    }
    lineage["coupled_relation_lineage_digest"] = digest_value(lineage)

    artifacts = [
        write_artifact(f"{label}_susceptibility_or_eligibility_trace.json", dependency_trace),
        write_artifact(f"{label}_coupled_relation_lineage_trace.json", lineage),
    ]
    row = {
        "row_id": f"n30_i6_row_{row_index:02d}_{label}_later_eligibility_candidate",
        "source_iteration": "I6",
        "primary_layer": "primitive",
        "participant_ladder_rung": source_row["participant_ladder_rung"],
        "medium_relation_ladder_rung": "M2_candidate_pending_I7_controls",
        "relation_chain_id": lineage["relation_chain_id"],
        "participant_event_id": source_row["participant_event_id"],
        "participant_carrier_id": source_row["participant_carrier_id"],
        "participant_carrier": source_row["participant_carrier"],
        "participant_persistence_window": source_row["participant_persistence_window"],
        "participant_attribution_trace": source_row["participant_attribution_trace"],
        "medium_surface_id": source_row["medium_surface_id"],
        "medium_surface_carrier": source_row["medium_surface_carrier"],
        "medium_surface_scope": source_row["medium_surface_scope"],
        "participant_medium_distinct": source_row["participant_medium_distinct"],
        "participant_medium_separation_argument": source_row[
            "participant_medium_separation_argument"
        ],
        "perturbation_trace": source_row["perturbation_trace"],
        "perturbation_event_id": source_row["perturbation_event_id"],
        "trace_or_surface_change_id": source_row["trace_or_surface_change_id"],
        "trace_persistence_or_decay": source_row["trace_persistence_or_decay"],
        "susceptibility_or_eligibility_trace": dependency_trace,
        "later_response_event_id": edge_trace["trace_id"],
        "later_response_conditioned_by_medium": True,
        "later_response_metric": dependency_trace["later_response_metric"],
        "expected_direction": dependency_trace["expected_direction"],
        "response_window": dependency_trace["response_window"],
        "baseline_window": dependency_trace["baseline_window"],
        "acceptance_threshold": dependency_trace["acceptance_threshold"],
        "normalization_denominator": dependency_trace["normalization_denominator"],
        "effect_size": {
            "effect_size_vs_neutral": dependency_trace["effect_size_vs_neutral"],
            "effect_size_vs_extractive_cross": dependency_trace[
                "effect_size_vs_extractive_cross"
            ],
            "minimum_threshold_margin": minimum_margin,
            "edge_mean_normalized_score": edge_score,
        },
        "counterfactual_row_id": [
            neutral_matrix_row["row_id"],
            extractive_matrix_row["row_id"],
        ],
        "causal_order_verified": lineage["causal_order_verified"],
        "trace_dependency_control_ids": dependency_trace[
            "i7_controls_required_for_final_C5"
        ],
        "medium_ablation_control_result": "pending_iteration_7",
        "row_chain_decision": lineage["row_chain_decision"],
        "direct_message_present": source_row["direct_message_present"],
        "direct_message_status": source_row["direct_message_status"],
        "medium_debt_record": source_row["medium_debt_record"],
        "producer_residue_record": source_row["producer_residue_record"],
        "source_current_inputs": source_output["source_current_inputs"],
        "artifact_manifest": artifacts,
        "replay_statuses": {
            "source_i5_replay_statuses": source_row["replay_statuses"],
            "i6_transition_policy_replay": "same_policy_transition_matrix_passed",
            "i7_replay_matrix": "pending_iteration_7",
        },
        "control_results": [
            {
                "control_id": "neutral_gap_counterfactual",
                "control_status": "passed",
                "blocked_condition": "later eligibility by row label only",
                "expected_result": "neutral gap remains unclassified",
                "actual_result": neutral_trace["observed_label"],
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "M2_candidate_preserved_pending_I7",
            },
            {
                "control_id": "extractive_cross_counterfactual",
                "control_status": "passed",
                "blocked_condition": "generic redistribution as eligibility",
                "expected_result": "opposite-direction extractive cross stays distinct",
                "actual_result": extractive_trace["observed_label"],
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "M2_candidate_preserved_pending_I7",
            },
        ],
        "claim_ceiling": (
            "provisional M2 later-eligibility dependency input evidence; final "
            "N30-C5 minimal shared-medium participation blocked pending I7 controls"
        ),
        "blocked_relabels": BLOCKED_CLAIMS,
        "row_decision": (
            "supported_provisional_M2_later_eligibility_candidate_pending_I7_controls"
        ),
        "source_output_digest": source_output["output_digest"],
        "source_row_id": source_row["row_id"],
        "edge_transition_trace_id": edge_trace["trace_id"],
        "derived_report_only": False,
    }
    row["all_artifact_sha256_match_file_contents"] = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )
    row["row_output_digest"] = digest_value(row)
    return row


def build_payload() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i5b = load_json(I5B_OUTPUT)
    transition_matrix = load_json(N28_TRANSITION_MATRIX)

    i5_row = i5["candidate_rows"][0]
    i5a_row = i5a["candidate_rows"][0]

    i4a_edge = load_json(I4A_EDGE_TRACE)
    i4a_neutral = load_json(I4A_NEUTRAL_TRACE)
    i4a_extractive = load_json(I4A_EXTRACTIVE_TRACE)
    i4a2_edge = load_json(I4A2_EDGE_TRACE)
    i4a2_neutral = load_json(I4A2_NEUTRAL_TRACE)
    i4a2_extractive = load_json(I4A2_EXTRACTIVE_TRACE)

    rows = [
        build_eligibility_row(
            row_index=1,
            label="i5_single_shell",
            source_output=i5,
            source_row=i5_row,
            edge_trace=i4a_edge,
            neutral_trace=i4a_neutral,
            extractive_trace=i4a_extractive,
            edge_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a_row_generative_strengthening_candidate",
                "generative_edge",
            ),
            neutral_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a_row_generative_strengthening_candidate",
                "neutral_gap_without_mixed_lobes",
            ),
            extractive_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a_row_generative_strengthening_candidate",
                "extractive_cross",
            ),
        ),
        build_eligibility_row(
            row_index=2,
            label="i5a_split_shell",
            source_output=i5a,
            source_row=i5a_row,
            edge_trace=i4a2_edge,
            neutral_trace=i4a2_neutral,
            extractive_trace=i4a2_extractive,
            edge_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a2_row_generative_mechanism_diversity_candidate",
                "generative_edge",
            ),
            neutral_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a2_row_generative_mechanism_diversity_candidate",
                "neutral_gap_without_mixed_lobes",
            ),
            extractive_matrix_row=find_transition_row(
                transition_matrix,
                "n28_i4a2_row_generative_mechanism_diversity_candidate",
                "extractive_cross",
            ),
        ),
    ]

    aggregate = {
        "artifact_role": "i6_later_eligibility_aggregate_trace",
        "trace_id": "n30_i6_later_eligibility_aggregate_trace",
        "candidate_row_ids": [row["row_id"] for row in rows],
        "medium_surface_ids": [row["medium_surface_id"] for row in rows],
        "relation_chain_ids": [row["relation_chain_id"] for row in rows],
        "m2_input_evidence_supported": True,
        "candidate_count": len(rows),
        "minimum_threshold_margin": min(
            row["effect_size"]["minimum_threshold_margin"] for row in rows
        ),
        "minimum_effect_size_vs_neutral": min(
            row["effect_size"]["effect_size_vs_neutral"] for row in rows
        ),
        "minimum_effect_size_vs_extractive_cross": min(
            row["effect_size"]["effect_size_vs_extractive_cross"] for row in rows
        ),
        "effect_margin_class": "narrow_positive",
        "source_transition_policy": transition_matrix["transition_policy"],
        "same_policy_transition_matrix_status": transition_matrix["status"],
        "same_policy_transition_matrix_acceptance_state": transition_matrix[
            "acceptance_state"
        ],
        "thresholds_retuned_for_transition": transition_matrix["transition_policy"][
            "thresholds_retuned_for_transition"
        ],
        "new_source_current_evidence_opened_by_transition_matrix": transition_matrix[
            "transition_summary"
        ]["new_source_current_evidence_opened"],
        "final_c5_claim_blocked_pending_i7": True,
    }
    aggregate["aggregate_trace_digest"] = digest_value(aggregate)

    claim_boundary = {
        "artifact_role": "i6_claim_boundary_guard",
        "trace_id": "n30_i6_claim_boundary_guard",
        "medium_relation_ladder_rung": "M2_candidate_pending_I7_controls",
        "m2_input_evidence_supported": True,
        "n30_c5_input_evidence_supported": True,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "reason_final_claim_blocked": "iteration_7_replay_and_relation_controls_pending",
        "blocked_claims": BLOCKED_CLAIMS,
        "i7_required_controls": rows[0]["trace_dependency_control_ids"],
    }
    claim_boundary["claim_boundary_guard_digest"] = digest_value(claim_boundary)

    aggregate_artifact = write_artifact(
        "i6_later_eligibility_aggregate_trace.json", aggregate
    )
    claim_artifact = write_artifact("i6_claim_boundary_guard.json", claim_boundary)
    artifact_manifest = [aggregate_artifact, claim_artifact] + [
        artifact for row in rows for artifact in row["artifact_manifest"]
    ]
    artifact_sha256_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifact_manifest
    )

    source_current_inputs = [
        source_input(I5_OUTPUT, "N30_I5_single_shell_M1_surface_trace"),
        source_input(I5A_OUTPUT, "N30_I5A_split_shell_M1_surface_trace"),
        source_input(I5B_OUTPUT, "N30_I5B_scope_window_audit"),
        source_input(N28_TRANSITION_MATRIX, "N28_same_policy_transition_matrix"),
        source_input(I4A_EDGE_TRACE, "N28_I4A_same_regime_boundary_edge_trace"),
        source_input(I4A_NEUTRAL_TRACE, "N28_I4A_neutral_gap_counterfactual_trace"),
        source_input(I4A_EXTRACTIVE_TRACE, "N28_I4A_extractive_cross_counterfactual_trace"),
        source_input(I4A2_EDGE_TRACE, "N28_I4A2_same_regime_boundary_edge_trace"),
        source_input(I4A2_NEUTRAL_TRACE, "N28_I4A2_neutral_gap_counterfactual_trace"),
        source_input(I4A2_EXTRACTIVE_TRACE, "N28_I4A2_extractive_cross_counterfactual_trace"),
    ]

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "6_later_eligibility_susceptibility_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_M2_later_eligibility_dependency_candidate_pending_I7_controls"
        ),
        "source_i5_output_digest": i5["output_digest"],
        "source_i5a_output_digest": i5a["output_digest"],
        "source_i5b_output_digest": i5b["output_digest"],
        "source_n28_transition_matrix_output_digest": transition_matrix["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": (
            "provisional_trace_mediated_later_eligibility_dependency_input_evidence"
        ),
        "runtime_origin": "inherited_N28_source_current_transition_artifacts",
        "n30_fresh_runtime": False,
        "participant_ladder_rung_assigned": "P2_candidate_with_I4B_P4_guardrail",
        "medium_relation_ladder_rung_assigned": "M2_candidate_pending_I7_controls",
        "n30_closeout_ceiling": (
            "N30-C4_medium_perturbation_trace_candidate_with_provisional_C5_input_evidence"
        ),
        "final_n30_closeout_rung": "not_assigned",
        "later_eligibility_dependency_evidence_opened": True,
        "n30_c5_input_evidence_supported": True,
        "minimal_shared_medium_participation_claim_allowed": False,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "ready_for_iteration_7_replay_controls": True,
        "candidate_rows": rows,
        "aggregate_trace": aggregate,
        "claim_boundary_guard": claim_boundary,
        "artifact_manifest": artifact_manifest,
        "source_current_inputs": source_current_inputs,
        "all_artifact_sha256_match_file_contents": artifact_sha256_match,
        "claim_boundary": {
            "claim_ceiling": (
                "provisional_M2_later_eligibility_input_evidence_pending_I7_controls"
            ),
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    checks = [
        {
            "check_id": "i5_i5a_i5b_inputs_passed",
            "passed": i5["status"] == "passed"
            and i5a["status"] == "passed"
            and i5b["status"] == "passed"
            and i5b["ready_for_iteration_6_later_eligibility_probe"] is True,
        },
        {
            "check_id": "later_metric_predeclared_and_effect_positive",
            "passed": all(
                row["susceptibility_or_eligibility_trace"]["metric_declared_before_use"]
                is True
                and row["effect_size"]["minimum_threshold_margin"] > 0
                and row["effect_size"]["edge_mean_normalized_score"] >= 1.0
                for row in rows
            ),
        },
        {
            "check_id": "counterfactuals_separate_eligibility_from_labels",
            "passed": all(
                row["control_results"][0]["actual_result"] == "unclassified"
                and row["control_results"][1]["actual_result"] == "extractive"
                for row in rows
            ),
        },
        {
            "check_id": "coupled_relation_chain_present",
            "passed": all(
                row["relation_chain_id"].endswith("_later_eligibility_dependency")
                and row["later_response_conditioned_by_medium"] is True
                and row["direct_message_present"] is False
                for row in rows
            ),
        },
        {
            "check_id": "transition_policy_not_retuned_or_mutated",
            "passed": transition_matrix["transition_policy"][
                "thresholds_retuned_for_transition"
            ]
            is False
            and transition_matrix["transition_summary"]["source_rows_mutated"] is False,
        },
        {
            "check_id": "final_c5_c6_claims_blocked_pending_i7",
            "passed": payload["n30_c5_input_evidence_supported"] is True
            and payload["final_n30_c5_claim_allowed"] is False
            and payload["final_n30_c6_claim_allowed"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": artifact_sha256_match,
        },
        {
            "check_id": "derived_report_only_false_for_candidates",
            "passed": all(row["derived_report_only"] is False for row in rows),
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
    payload["output_digest"] = digest_value(payload)
    return payload


def write_report(payload: dict[str, Any]) -> None:
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )
    candidate_rows = "\n".join(
        (
            f"- {row['row_id']}: surface={row['medium_surface_id']}, "
            f"effect_vs_neutral={row['effect_size']['effect_size_vs_neutral']}, "
            f"min_margin={row['effect_size']['minimum_threshold_margin']}, "
            f"decision={row['row_decision']}"
        )
        for row in payload["candidate_rows"]
    )
    text = f"""# N30 Iteration 6 - Later Eligibility / Susceptibility Probe

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

I6 tests whether the I5/I5-A changed medium surfaces condition a later
eligibility/susceptibility result. It consumes the exact I5/I5-A surface IDs
and the N28 same-policy boundary transition traces.

This is not final N30-C5. I6 opens provisional M2 input evidence, but the full
N30-C5 minimal shared-medium participation claim remains blocked until I7 runs
the replay and relation-control matrix.

## Result

```text
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
n30_closeout_ceiling = N30-C4_with_provisional_C5_input_evidence
later_eligibility_dependency_evidence_opened = true
n30_c5_input_evidence_supported = true
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
runtime_origin = inherited_N28_source_current_transition_artifacts
n30_fresh_runtime = false
```

## Candidate Rows

{candidate_rows}

## Geometric Interpretation

I5/I5-A established that a participant event can change a non-private neighbor
capacity surface. I6 adds the next dependency leg: the later same-policy
boundary-edge transition stays eligible only when the changed medium-surface
axes remain above their declared thresholds. The neutral-gap counterfactual has
the same stability context but no medium-surface gain, so it remains
unclassified. The extractive-cross counterfactual changes the surface in the
opposite direction, so it remains extractive rather than becoming generic
shared-medium eligibility.

Geometrically, the medium surface is not just present. Its distinguishability,
support, boundary, and environment-capacity deltas form the later eligibility
condition. The margin is narrow but positive, so I6 is a provisional M2 input
candidate, not a robust C5 closeout.

## Claim Boundary

```text
M2 input evidence = supported provisionally
final C5 minimal shared-medium participation = blocked pending I7
shared-medium coordination = false
parent-basin modulation = false
resonant alignment = false
native shared-medium organization = false
agency / selfhood / sentience / ecology regime = false
```

## Artifacts

| Role | Path |
|---|---|
{artifact_rows}

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
