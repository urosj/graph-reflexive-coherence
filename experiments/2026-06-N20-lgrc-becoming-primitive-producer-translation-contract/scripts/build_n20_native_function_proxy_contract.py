#!/usr/bin/env python3
"""Build N20 Iteration 4 continuation/proxy/scaffold contract."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-22T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
SOURCE_LEDGER = EXPERIMENT / "outputs" / "n20_producer_residue_ledger.json"
OUTPUT = EXPERIMENT / "outputs" / "n20_native_function_proxy_contract.json"
REPORT = EXPERIMENT / "reports" / "n20_native_function_proxy_contract.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_native_function_proxy_contract.py"
)

INVARIANTS = {
    "primitive_evidence_opened": False,
    "agency_claim_opened": False,
    "phase8_opened": False,
    "native_support_opened": False,
    "sentience_opened": False,
    "ant_ecology_spec_opened": False,
    "src_diff_empty_required": True,
}

BLOCKED_PROXY_TERMS = [
    "agency",
    "choice",
    "goal",
    "intention",
    "sentience",
    "identity",
    "native_support",
    "selfhood",
    "consciousness",
    "organism_life",
]

COMMON_SUPPORT_SCAFFOLD = {
    "support_source": "declared source-current or producer-mediated support surface",
    "support_surface": "support/coherence/boundary/flux contract surface",
    "hidden_support_allowed": False,
    "hidden_support_control": (
        "fail closed if support or scaffold is preserved by an undeclared "
        "producer surface"
    ),
    "producer_role": (
        "producer may declare, schedule, or expose the support/scaffold surface, "
        "but producer support cannot count as native support"
    ),
}

CONTRACT_DEFINITIONS: dict[str, dict[str, Any]] = {
    "withdrawal_resistance": {
        "continuation": {
            "basin_signature": [
                "basin_signature_trace",
                "boundary_integrity_trace",
                "support_coherence_floor_trace",
            ],
            "support_floor": "support remains above declared withdrawal floor",
            "coherence_floor": "coherence remains above declared withdrawal floor",
            "boundary_condition": "boundary remains distinguishable during support reduction",
            "flux_condition": "flux leakage does not explain apparent persistence",
            "continuation_condition": (
                "basin signature persists through declared support reduction"
            ),
            "withdrawal_condition": "declared support is weakened or removed in a bounded window",
            "transfer_condition": "not tested in N21 withdrawal row",
        },
        "proxy": {
            "measured_quantity": "support_coherence_survival_margin",
            "source_current_inputs": [
                "basin_signature_trace",
                "support_coherence_floor_trace",
                "boundary_integrity_trace",
                "withdrawal_window_trace",
            ],
            "producer_inputs": [
                "declared_withdrawal_schedule",
                "withdrawal_amount_policy",
                "pass_fail_threshold_label",
            ],
            "expected_relation_to_continuation_function": (
                "positive margin is only a sign of persistence if basin signature "
                "and boundary integrity remain source-visible"
            ),
            "divergence_condition": (
                "survival margin improves while basin signature or boundary "
                "integrity fails"
            ),
            "collapse_condition": (
                "hidden producer support keeps the margin above floor after "
                "withdrawal"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "support_coherence_floor_trace",
                "boundary_integrity_trace",
            ],
            "required_supports": [
                "support floor",
                "coherence floor",
                "boundary integrity floor",
            ],
            "optional_supports": ["withdrawal window telemetry"],
            "producer_supplied_scaffolds": [
                "declared_withdrawal_schedule",
                "withdrawal_amount_policy",
            ],
            "withdrawable_supports": ["declared support surface"],
            "withdrawal_condition": "support weakened or removed under bounded schedule",
            "naturalization_debt": [
                "source_current_support_withdrawal_surface",
                "producer_independent_withdrawal_replay",
            ],
        },
        "n21_handoff": {
            "probe_present_condition": "declared support/scaffold present before withdrawal",
            "probe_absent_condition": "declared support/scaffold weakened or absent after withdrawal",
        },
    },
    "naturalization_depth": {
        "continuation": {
            "basin_signature": [
                "post_probe_basin_signature_trace",
                "post_probe_support_floor_trace",
                "post_probe_coherence_floor_trace",
            ],
            "support_floor": "post-probe support remains above declared residual floor",
            "coherence_floor": "post-probe coherence remains above declared residual floor",
            "boundary_condition": "basin boundary remains distinguishable after probe removal",
            "flux_condition": "residual persistence is not explained by hidden support flux",
            "continuation_condition": (
                "basin signature persists after the original probe/scaffold is absent"
            ),
            "withdrawal_condition": "original probe/scaffold is removed or disabled",
            "transfer_condition": "not tested in N21 naturalization-depth row",
        },
        "proxy": {
            "measured_quantity": "post_probe_persistence_margin",
            "source_current_inputs": [
                "post_probe_basin_signature_trace",
                "post_probe_support_floor_trace",
                "post_probe_coherence_floor_trace",
                "multi_window_replay_trace",
            ],
            "producer_inputs": [
                "naturalization_depth_score_formula",
                "support_source_annotation",
                "depth_rank_label",
            ],
            "expected_relation_to_continuation_function": (
                "depth margin is a sign only when probe-absent basin state replays"
            ),
            "divergence_condition": (
                "depth score improves while post-probe basin signature does not persist"
            ),
            "collapse_condition": (
                "depth score depends on support annotation or probe residue"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "post_probe_support_floor_trace",
                "post_probe_coherence_floor_trace",
            ],
            "required_supports": [
                "post-probe support floor",
                "post-probe coherence floor",
                "multi-window replay trace",
            ],
            "optional_supports": ["support source annotation"],
            "producer_supplied_scaffolds": [
                "naturalization_depth_score_formula",
                "depth_rank_label",
            ],
            "withdrawable_supports": ["original probe/scaffold"],
            "withdrawal_condition": "probe absent while residual basin trace remains auditable",
            "naturalization_debt": [
                "source_current_producer_removal_observation",
                "multi_window_without_probe_replay",
            ],
        },
        "n21_handoff": {
            "probe_present_condition": "original probe/scaffold present",
            "probe_absent_condition": "original probe/scaffold absent with residual replay",
        },
    },
    "susceptibility_update": {
        "continuation": {
            "basin_signature": [
                "pre_interaction_geometry_trace",
                "post_interaction_geometry_trace",
                "susceptibility_delta_trace",
            ],
            "support_floor": "altered geometry stays above support floor",
            "coherence_floor": "altered geometry stays above coherence floor",
            "boundary_condition": "route or region boundary remains auditable after update",
            "flux_condition": "durable delta is not a flux-only transient",
            "continuation_condition": (
                "later route or boundary susceptibility differs because prior "
                "interaction altered replay-visible geometry"
            ),
            "withdrawal_condition": "prior interaction support can be removed without erasing replay trace",
            "transfer_condition": "not tested before N27",
        },
        "proxy": {
            "measured_quantity": "susceptibility_delta_replay_margin",
            "source_current_inputs": [
                "pre_interaction_geometry_trace",
                "post_interaction_geometry_trace",
                "susceptibility_delta_trace",
                "route_or_region_reentry_trace",
            ],
            "producer_inputs": [
                "route_update_rule",
                "reinforcement_schedule",
                "learning_label",
            ],
            "expected_relation_to_continuation_function": (
                "delta is a sign only if replay-visible geometry changes and "
                "later re-entry follows that altered geometry"
            ),
            "divergence_condition": (
                "delta label changes while source-current geometry and re-entry do not"
            ),
            "collapse_condition": (
                "replay loses the durable delta or depends on producer reinforcement"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "pre_interaction_geometry_trace",
                "post_interaction_geometry_trace",
            ],
            "required_supports": [
                "replay-visible geometry delta",
                "later re-entry trace",
            ],
            "optional_supports": ["peer-route comparison telemetry"],
            "producer_supplied_scaffolds": [
                "route_update_rule",
                "reinforcement_schedule",
            ],
            "withdrawable_supports": ["producer reinforcement schedule"],
            "withdrawal_condition": "delta replays after scheduled reinforcement is absent",
            "naturalization_debt": [
                "source_current_route_conditioned_state_mutation",
                "peer_route_same_budget_comparison",
            ],
        },
    },
    "live_continuation_collapse": {
        "continuation": {
            "basin_signature": [
                "live_branch_set_trace",
                "branch_support_coherence_traces",
                "collapsed_continuation_trace",
            ],
            "support_floor": "selected branch remains above support floor",
            "coherence_floor": "selected branch remains above coherence floor",
            "boundary_condition": "live alternatives are real and boundary-distinguishable",
            "flux_condition": "collapse is not leakage or merge pressure masquerading as selection",
            "continuation_condition": (
                "multiple live continuation branches resolve into one source-current "
                "continuation while alternatives remain auditable"
            ),
            "withdrawal_condition": "producer selected-branch label can be removed",
            "transfer_condition": "not tested before N27",
        },
        "proxy": {
            "measured_quantity": "branch_collapse_geometry_margin",
            "source_current_inputs": [
                "live_branch_set_trace",
                "branch_support_coherence_traces",
                "collapsed_continuation_trace",
                "counterfactual_branch_retention_trace",
            ],
            "producer_inputs": [
                "branch_enumeration_policy",
                "selected_branch_label",
                "tie_breaker_schedule",
            ],
            "expected_relation_to_continuation_function": (
                "branch margin is a sign only when alternatives are source-current "
                "and collapse is geometry-conditioned"
            ),
            "divergence_condition": (
                "selected branch score improves while alternatives are fake or post-hoc"
            ),
            "collapse_condition": (
                "collapse vanishes when producer preference or selected label is removed"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "live_branch_set_trace",
                "branch_support_coherence_traces",
            ],
            "required_supports": [
                "live continuation set",
                "counterfactual branch retention",
            ],
            "optional_supports": ["tie-break telemetry"],
            "producer_supplied_scaffolds": [
                "branch_enumeration_policy",
                "selected_branch_label",
            ],
            "withdrawable_supports": ["selected-branch label"],
            "withdrawal_condition": "collapse remains auditable without selected label",
            "naturalization_debt": [
                "source_current_counterfactual_branch_records",
                "route_conditioned_selection_policy",
            ],
        },
    },
    "surplus_supported_optionality": {
        "continuation": {
            "basin_signature": [
                "support_surplus_margin_trace",
                "optional_continuation_set_trace",
                "maintenance_floor_trace",
            ],
            "support_floor": "maintenance floor remains preserved",
            "coherence_floor": "coherence remains preserved while optionality opens",
            "boundary_condition": "boundary integrity remains above floor under optional branches",
            "flux_condition": "optional flux does not drain maintenance support",
            "continuation_condition": (
                "surplus above maintenance floor opens optional continuations without "
                "collapsing the basin"
            ),
            "withdrawal_condition": "surplus can be reduced back to maintenance floor",
            "transfer_condition": "not tested before N27",
        },
        "proxy": {
            "measured_quantity": "surplus_optional_branch_capacity",
            "source_current_inputs": [
                "support_surplus_margin_trace",
                "optional_continuation_set_trace",
                "maintenance_floor_trace",
                "boundary_integrity_under_optionality_trace",
            ],
            "producer_inputs": [
                "optionality_enumerator",
                "exploration_schedule",
                "reward_or_proxy_label",
            ],
            "expected_relation_to_continuation_function": (
                "option count is a sign only if surplus remains above maintenance "
                "floor and boundary integrity holds"
            ),
            "divergence_condition": (
                "optional branch count improves while maintenance floor or boundary fails"
            ),
            "collapse_condition": "optional branches disappear under hidden budget control",
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "support_surplus_margin_trace",
                "maintenance_floor_trace",
            ],
            "required_supports": [
                "surplus support condition",
                "maintenance floor",
                "boundary integrity",
            ],
            "optional_supports": ["optional branch telemetry"],
            "producer_supplied_scaffolds": [
                "optionality_enumerator",
                "exploration_schedule",
            ],
            "withdrawable_supports": ["surplus above maintenance floor"],
            "withdrawal_condition": "optional branches close while maintenance basin remains",
            "naturalization_debt": [
                "source_current_optional_branch_telemetry",
                "surplus_budget_owner",
            ],
        },
    },
    "spark_sub_basin_new_basin_formation": {
        "continuation": {
            "basin_signature": [
                "bifurcation_trace",
                "new_boundary_candidate_trace",
                "new_basin_support_coherence_trace",
            ],
            "support_floor": "new or sub-basin candidate has its own support floor",
            "coherence_floor": "new or sub-basin candidate has its own coherence floor",
            "boundary_condition": "new/sub-basin boundary is distinguishable from old basin thickening",
            "flux_condition": "candidate is not merge/leakage masquerading as formation",
            "continuation_condition": (
                "source-backed bifurcation or basin-creation candidate persists "
                "as a distinguishable replay state"
            ),
            "withdrawal_condition": "producer seed or label can be removed",
            "transfer_condition": "not tested before N27",
        },
        "proxy": {
            "measured_quantity": "basin_distinguishability_persistence_margin",
            "source_current_inputs": [
                "bifurcation_trace",
                "new_boundary_candidate_trace",
                "new_basin_support_coherence_trace",
                "replayable_distinction_trace",
            ],
            "producer_inputs": [
                "new_basin_label",
                "seed_insertion_policy",
                "split_threshold_schedule",
            ],
            "expected_relation_to_continuation_function": (
                "distinguishability margin is a sign only if the new/sub-basin "
                "replays without label support"
            ),
            "divergence_condition": (
                "distinguishability score improves while replay shows old-basin thickening"
            ),
            "collapse_condition": "candidate vanishes when seed insertion or label is removed",
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "new_basin_support_coherence_trace",
                "new_boundary_candidate_trace",
            ],
            "required_supports": [
                "bifurcation trace",
                "distinguishable boundary",
                "replayable distinction",
            ],
            "optional_supports": ["surplus precondition from N24"],
            "producer_supplied_scaffolds": [
                "new_basin_label",
                "seed_insertion_policy",
            ],
            "withdrawable_supports": ["seed insertion label"],
            "withdrawal_condition": "candidate persists after label/seed support is absent",
            "naturalization_debt": [
                "source_current_basin_birth_state_mutation",
                "distinguishability_replay",
            ],
        },
    },
    "proxy_divergence_proxy_collapse": {
        "continuation": {
            "basin_signature": [
                "basin_persistence_capacity_trace",
                "support_coherence_floor_trace",
                "basin_deepening_comparison_trace",
            ],
            "support_floor": "basin persistence capacity remains above floor",
            "coherence_floor": "basin deepening remains coherent under stress",
            "boundary_condition": "basin persistence remains distinguishable from proxy gain",
            "flux_condition": "proxy gain does not hide basin support leakage",
            "continuation_condition": (
                "basin persistence capacity remains coupled to the proxy under stress"
            ),
            "withdrawal_condition": "proxy target/policy can be removed or perturbed",
            "transfer_condition": "not tested before N27",
        },
        "proxy": {
            "measured_quantity": "proxy_basin_coupling_gap",
            "source_current_inputs": [
                "basin_persistence_capacity_trace",
                "support_coherence_floor_trace",
                "proxy_failure_under_perturbation_trace",
                "basin_deepening_comparison_trace",
            ],
            "producer_inputs": [
                "target_derivation_policy",
                "proxy_metric_formula",
                "ranking_policy",
            ],
            "expected_relation_to_continuation_function": (
                "proxy improvement is a sign only while basin persistence capacity "
                "also remains coupled and replay-visible"
            ),
            "divergence_condition": (
                "proxy improves while basin persistence stalls or degrades"
            ),
            "collapse_condition": (
                "proxy-optimized row fails under perturbation that basin-deepened "
                "row would survive"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "basin_persistence_capacity_trace",
                "support_coherence_floor_trace",
            ],
            "required_supports": [
                "proxy metric definition",
                "basin deepening comparison",
                "perturbation trace",
            ],
            "optional_supports": ["target digest telemetry"],
            "producer_supplied_scaffolds": [
                "target_derivation_policy",
                "proxy_metric_formula",
            ],
            "withdrawable_supports": ["proxy target derivation policy"],
            "withdrawal_condition": "basin persistence remains auditable when proxy policy is removed",
            "naturalization_debt": [
                "native_lower_stack_input_vector",
                "source_current_proxy_derivation_policy",
            ],
        },
    },
    "configuration_substrate_transfer": {
        "continuation": {
            "basin_signature": [
                "pre_transfer_basin_signature_trace",
                "post_transfer_basin_signature_trace",
                "boundary_mapping_trace",
            ],
            "support_floor": "post-transfer support remains above floor",
            "coherence_floor": "post-transfer coherence remains above floor",
            "boundary_condition": "mapped boundary preserves the declared basin signature",
            "flux_condition": "transfer is not support reconstruction through hidden flux",
            "continuation_condition": (
                "basin signature persists under declared configuration or substrate mapping"
            ),
            "withdrawal_condition": "original fixture support can be removed or changed",
            "transfer_condition": "declared fixture/topology/substrate mapping is source-backed",
        },
        "proxy": {
            "measured_quantity": "transfer_signature_preservation_margin",
            "source_current_inputs": [
                "pre_transfer_basin_signature_trace",
                "post_transfer_basin_signature_trace",
                "boundary_mapping_trace",
                "support_preservation_trace",
            ],
            "producer_inputs": [
                "configuration_mapping_policy",
                "fixture_equivalence_label",
                "support_reconstruction_schedule",
            ],
            "expected_relation_to_continuation_function": (
                "signature margin is a sign only when mapped boundary and support "
                "preservation are source-backed"
            ),
            "divergence_condition": (
                "signature score improves while mapping is only a fixture-equivalence label"
            ),
            "collapse_condition": (
                "transfer fails when original support reconstruction is blocked"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "pre_transfer_basin_signature_trace",
                "post_transfer_basin_signature_trace",
            ],
            "required_supports": [
                "transfer mapping declaration",
                "boundary mapping trace",
                "support preservation trace",
            ],
            "optional_supports": ["reconstructed support ledger"],
            "producer_supplied_scaffolds": [
                "configuration_mapping_policy",
                "fixture_equivalence_label",
            ],
            "withdrawable_supports": ["original fixture support"],
            "withdrawal_condition": "post-transfer signature remains after original support changes",
            "naturalization_debt": [
                "source_current_mapping_telemetry",
                "independent_substrate_replay",
            ],
        },
    },
    "generative_extractive_persistence": {
        "continuation": {
            "basin_signature": [
                "focal_basin_stability_trace",
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
            ],
            "support_floor": "focal and neighbor support floors remain visible",
            "coherence_floor": "focal and neighbor coherence remain distinguishable",
            "boundary_condition": "neighbor structures do not merge into focal basin",
            "flux_condition": "environment capacity gain is not focal extraction or leakage",
            "continuation_condition": (
                "focal basin persists while neighborhood basin-forming capacity "
                "increases or remains distinguishable"
            ),
            "withdrawal_condition": "producer generativity label can be removed",
            "transfer_condition": "ecology-specific transfer deferred until N29",
        },
        "proxy": {
            "measured_quantity": "generative_capacity_delta_margin",
            "source_current_inputs": [
                "focal_basin_stability_trace",
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "extraction_cost_trace",
            ],
            "producer_inputs": [
                "generativity_label",
                "neighbor_attribution_policy",
                "medium_segmentation_policy",
            ],
            "expected_relation_to_continuation_function": (
                "capacity delta is a sign only if focal persistence and neighbor "
                "distinguishability both remain source-visible"
            ),
            "divergence_condition": (
                "capacity score improves while neighbor support degrades or merge pressure rises"
            ),
            "collapse_condition": (
                "apparent generation is explained by extraction cost or medium segmentation"
            ),
            "proxy_only_success_blocker": (
                "proxy improves while basin continuation fails -> primitive not "
                "supported"
            ),
        },
        "scaffold": {
            "declared_supports": [
                "focal_basin_stability_trace",
                "neighbor_support_floor_trace",
            ],
            "required_supports": [
                "neighbor distinguishability",
                "environment basin-forming capacity",
                "extraction cost trace",
            ],
            "optional_supports": ["medium debt placeholder"],
            "producer_supplied_scaffolds": [
                "generativity_label",
                "neighbor_attribution_policy",
                "medium_segmentation_policy",
            ],
            "withdrawable_supports": ["generativity label"],
            "withdrawal_condition": "environment-side effects remain after label removal",
            "naturalization_debt": [
                "source_current_neighbor_basin_birth_telemetry",
                "medium_debt_deferred_to_n28_n29",
            ],
        },
    },
}


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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def source_ledger_reference(ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(SOURCE_LEDGER),
        "sha256": sha256_file(SOURCE_LEDGER),
        "output_digest": ledger["output_digest"],
        "status": ledger["status"],
        "acceptance_state": ledger["acceptance_state"],
        "row_count": ledger["row_count"],
        "variable_record_count": ledger["variable_record_count"],
    }


def no_absolute_paths(data: Any) -> bool:
    return not absolute_path_strings(data)


def absolute_path_strings(data: Any) -> list[str]:
    found: list[str] = []
    if isinstance(data, str):
        if data.startswith("/") or data.startswith("file://"):
            found.append(data)
        elif len(data) >= 3 and data[1] == ":" and data[2] in {"\\", "/"}:
            found.append(data)
        return found
    if isinstance(data, dict):
        for value in data.values():
            found.extend(absolute_path_strings(value))
    elif isinstance(data, list):
        for value in data:
            found.extend(absolute_path_strings(value))
    return found


def unsafe_claim_flags_from_i3(row: dict[str, Any]) -> dict[str, bool]:
    return dict(row["unsafe_claim_flags"])


def local_gap_dependencies(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ap_gap_dependencies": row["ap_gap_dependencies"],
        "conditional_gap_dependencies": row["conditional_gap_dependencies"],
        "carried_forward_from_i3": True,
    }


def continuation_descriptor(
    primitive_id: str, definition: dict[str, Any], i3_row: dict[str, Any]
) -> dict[str, Any]:
    continuation = definition["continuation"]
    proxy = definition["proxy"]
    return {
        "descriptor_id": f"n20_i4_{primitive_id}_continuation_function",
        "descriptor_kind": "bounded_geometric_continuation_condition",
        "native_function_descriptor_alias_allowed": True,
        "native_function_descriptor_alias_meaning": (
            "alias only; not purpose, goal, semantic function, biological "
            "function, intention, task success, or goal ownership"
        ),
        "basin_signature": continuation["basin_signature"],
        "support_floor": continuation["support_floor"],
        "coherence_floor": continuation["coherence_floor"],
        "boundary_condition": continuation["boundary_condition"],
        "flux_condition": continuation["flux_condition"],
        "continuation_condition": continuation["continuation_condition"],
        "withdrawal_condition": continuation["withdrawal_condition"],
        "transfer_condition": continuation["transfer_condition"],
        "proxy_metric": f"n20_i4_{primitive_id}_{proxy['measured_quantity']}",
        "proxy_divergence_blocker": (
            "primitive not supported when proxy improves while basin continuation "
            "or declared basin signature fails"
        ),
        "claim_ceiling": (
            "contract descriptor only; no primitive support, agency, Phase 8, "
            "native support, sentience, or semantic function"
        ),
        "source_ledger_row": i3_row["row_id"],
    }


def proxy_metric_definition(
    primitive_id: str, definition: dict[str, Any], i3_row: dict[str, Any]
) -> dict[str, Any]:
    proxy = definition["proxy"]
    return {
        "proxy_id": f"n20_i4_{primitive_id}_{proxy['measured_quantity']}",
        "proxy_kind": "bounded_indicator_not_replacement",
        "measured_quantity": proxy["measured_quantity"],
        "source_current_inputs": [
            f"{primitive_id}.{value}" for value in proxy["source_current_inputs"]
        ],
        "producer_inputs": [
            f"{primitive_id}.{value}" for value in proxy["producer_inputs"]
        ],
        "expected_relation_to_continuation_function": proxy[
            "expected_relation_to_continuation_function"
        ],
        "divergence_condition": proxy["divergence_condition"],
        "collapse_condition": proxy["collapse_condition"],
        "proxy_only_success_blocker": proxy["proxy_only_success_blocker"],
        "proxy_success_replaces_continuation": False,
        "blocked_relabels_as_proxy_metrics_allowed": False,
        "blocked_proxy_terms": BLOCKED_PROXY_TERMS,
        "source_ledger_row": i3_row["row_id"],
    }


def support_scaffold_declaration(
    primitive_id: str, definition: dict[str, Any], i3_row: dict[str, Any]
) -> dict[str, Any]:
    scaffold = definition["scaffold"]
    declared_supports = [f"{primitive_id}.{value}" for value in scaffold["declared_supports"]]
    producer_scaffolds = [
        f"{primitive_id}.{value}" for value in scaffold["producer_supplied_scaffolds"]
    ]
    debt_fields = [f"{primitive_id}.{value}" for value in scaffold["naturalization_debt"]]
    return {
        "support_id": f"n20_i4_{primitive_id}_support_scaffold",
        "declared_supports": declared_supports,
        "required_supports": scaffold["required_supports"],
        "optional_supports": scaffold["optional_supports"],
        "producer_supplied_scaffolds": producer_scaffolds,
        "withdrawable_supports": scaffold["withdrawable_supports"],
        "support_source": COMMON_SUPPORT_SCAFFOLD["support_source"],
        "support_surface": COMMON_SUPPORT_SCAFFOLD["support_surface"],
        "withdrawal_condition": scaffold["withdrawal_condition"],
        "producer_role": COMMON_SUPPORT_SCAFFOLD["producer_role"],
        "naturalization_debt": debt_fields,
        "hidden_support_allowed": COMMON_SUPPORT_SCAFFOLD["hidden_support_allowed"],
        "hidden_support_blocker": COMMON_SUPPORT_SCAFFOLD["hidden_support_control"],
        "hidden_support_control": COMMON_SUPPORT_SCAFFOLD["hidden_support_control"],
        "source_ledger_row": i3_row["row_id"],
    }


def native_function_descriptor_alias(primitive_id: str) -> dict[str, Any]:
    return {
        "alias_for": "continuation_function_descriptor",
        "descriptor_id": f"n20_i4_{primitive_id}_native_function_alias",
        "semantic_function_claim_allowed": False,
        "semantic_purpose_claim_allowed": False,
        "semantic_goal_claim_allowed": False,
        "semantic_intention_claim_allowed": False,
        "usage_rule": (
            "native_function_descriptor may be used only as shorthand for "
            "bounded geometric continuation condition"
        ),
    }


def same_basin_placeholder(primitive_id: str, i3_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": f"pending_n20_i5_{primitive_id}_same_basin_rule",
        "status": "deferred_to_iteration_5",
        "label_only_continuation_allowed": False,
        "reason": (
            "I4 defines continuation/proxy/scaffold only; I5 defines same-basin "
            "criteria and fail-closed controls"
        ),
        "source_ledger_row": i3_row["row_id"],
    }


def minimum_controls_placeholder(primitive_id: str, i3_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "deferred_to_iteration_5",
        "required_control_templates": i3_row["minimum_controls"][
            "required_control_templates"
        ],
        "reason": (
            "I4 names proxy-only and hidden-support blockers but does not freeze "
            "the full I5 control contract"
        ),
    }


def n21_handoff_inputs(row: dict[str, Any], definition: dict[str, Any]) -> dict[str, Any] | None:
    if row["expected_first_positive_experiment"] != "N21":
        return None
    scaffold = definition["scaffold"]
    continuation = definition["continuation"]
    proxy = definition["proxy"]
    handoff = definition["n21_handoff"]
    return {
        "primitive_id": row["primitive_id"],
        "withdrawal_condition": continuation["withdrawal_condition"],
        "declared_supports": scaffold["declared_supports"],
        "support_floor": continuation["support_floor"],
        "coherence_floor": continuation["coherence_floor"],
        "hidden_support_blocker": COMMON_SUPPORT_SCAFFOLD["hidden_support_control"],
        "probe_present_condition": handoff["probe_present_condition"],
        "probe_absent_condition": handoff["probe_absent_condition"],
        "proxy_only_success_blocker": proxy["proxy_only_success_blocker"],
    }


def build_rows(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i3_row in ledger["producer_residue_rows"]:
        primitive_id = i3_row["primitive_id"]
        definition = CONTRACT_DEFINITIONS[primitive_id]
        row = {
            "row_id": i3_row["row_id"].replace("n20_i3", "n20_i4"),
            "source_i3_row_id": i3_row["row_id"],
            "primitive_id": primitive_id,
            "primitive_name": i3_row["primitive_name"],
            "roadmap_target": i3_row["roadmap_target"],
            "expected_first_positive_experiment": i3_row[
                "expected_first_positive_experiment"
            ],
            "diagnostic_source_titles": i3_row["diagnostic_source_titles"],
            "source_inventory_row_ids": i3_row["source_inventory_row_ids"],
            "source_role_dependencies": i3_row["source_role_dependencies"],
            "LGRC_visible_fields": i3_row["LGRC_visible_fields"],
            "producer_mediated_fields": i3_row["producer_mediated_fields"],
            "naturalization_debt_fields": i3_row["naturalization_debt_fields"],
            "blocked_relabel_fields": i3_row["blocked_relabel_fields"],
            "primitive_specific_consumption_inputs": i3_row[
                "primitive_specific_consumption_inputs"
            ],
            "continuation_function_descriptor": continuation_descriptor(
                primitive_id, definition, i3_row
            ),
            "native_function_descriptor_alias": native_function_descriptor_alias(
                primitive_id
            ),
            "proxy_metric_definition": proxy_metric_definition(
                primitive_id, definition, i3_row
            ),
            "support_scaffold_declaration": support_scaffold_declaration(
                primitive_id, definition, i3_row
            ),
            "same_basin_continuation_rule": same_basin_placeholder(
                primitive_id, i3_row
            ),
            "contract_status": "incomplete_missing_same_basin_rule",
            "contract_complete_allowed": False,
            "missing_contract_objects": [
                "same_basin_continuation_rule",
                "minimum_controls",
            ],
            "row_decision": "supported",
            "contract_row_supported_as": (
                "continuation_proxy_scaffold_contract_defined"
            ),
            "primitive_supported": False,
            "primitive_evidence_opened": False,
            "minimum_controls": minimum_controls_placeholder(primitive_id, i3_row),
            "ap_gap_contract": local_gap_dependencies(i3_row),
            "claim_ceiling": (
                "continuation/proxy/scaffold contract row only; no primitive "
                "evidence, agency, Phase 8, native support, sentience, or "
                "semantic function"
            ),
            "unsafe_claim_flags": unsafe_claim_flags_from_i3(i3_row),
            "artifact_invariants": INVARIANTS,
            "downstream_consumption_status": "not_consumable_until_iteration5_contract_complete",
            "downstream_immutability_rule": i3_row["downstream_immutability_rule"],
            "source_consumption_rules": i3_row["source_consumption_rules"],
        }
        maybe_n21 = n21_handoff_inputs(i3_row, definition)
        if maybe_n21 is not None:
            row["n21_handoff_inputs"] = maybe_n21
        rows.append(row)
    return rows


def descriptor_signature(row: dict[str, Any]) -> tuple[str, ...]:
    descriptor = row["continuation_function_descriptor"]
    proxy = row["proxy_metric_definition"]
    scaffold = row["support_scaffold_declaration"]
    return (
        descriptor["continuation_condition"],
        descriptor["boundary_condition"],
        descriptor["flux_condition"],
        proxy["measured_quantity"],
        proxy["divergence_condition"],
        scaffold["withdrawal_condition"],
    )


def proxy_has_blocked_term(row: dict[str, Any]) -> bool:
    proxy = row["proxy_metric_definition"]
    text = " ".join(
        [
            proxy["proxy_id"],
            proxy["measured_quantity"],
            proxy["expected_relation_to_continuation_function"],
        ]
    ).lower()
    return any(term.lower() in text for term in BLOCKED_PROXY_TERMS)


def proxy_only_blocker_present(row: dict[str, Any]) -> bool:
    blocker = row["proxy_metric_definition"]["proxy_only_success_blocker"]
    return (
        "proxy improves while basin continuation fails" in blocker
        and "primitive not supported" in blocker
        and row["proxy_metric_definition"]["proxy_success_replaces_continuation"] is False
    )


def ap_gap_summary(rows: list[dict[str, Any]]) -> dict[str, bool]:
    by_id = {row["primitive_id"]: row for row in rows}

    def has_gap(row: dict[str, Any], ap_level: str, field: str) -> bool:
        return any(gap["ap_level"] == ap_level for gap in row["ap_gap_contract"][field])

    return {
        "susceptibility_update_has_ap4": has_gap(
            by_id["susceptibility_update"], "AP4", "ap_gap_dependencies"
        ),
        "susceptibility_update_has_conditional_ap5": has_gap(
            by_id["susceptibility_update"], "AP5", "conditional_gap_dependencies"
        ),
        "live_continuation_collapse_has_ap4": has_gap(
            by_id["live_continuation_collapse"], "AP4", "ap_gap_dependencies"
        ),
        "live_continuation_collapse_has_conditional_ap5": has_gap(
            by_id["live_continuation_collapse"], "AP5", "conditional_gap_dependencies"
        ),
        "proxy_divergence_proxy_collapse_has_ap5": has_gap(
            by_id["proxy_divergence_proxy_collapse"], "AP5", "ap_gap_dependencies"
        ),
        "configuration_substrate_transfer_has_conditional_ap4": has_gap(
            by_id["configuration_substrate_transfer"],
            "AP4",
            "conditional_gap_dependencies",
        ),
    }


def classification_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts[row["contract_status"]] += 1
    return dict(sorted(counts.items()))


def build_checks(artifact: dict[str, Any], ledger: dict[str, Any]) -> list[dict[str, Any]]:
    rows = artifact["contract_rows"]
    gap_summary = artifact["ap4_ap5_local_dependency_summary"]
    n21_rows = [
        row for row in rows if row["expected_first_positive_experiment"] == "N21"
    ]
    checks = [
        {
            "check_id": "source_ledger_passed_and_not_primitive_evidence",
            "passed": ledger["status"] == "passed"
            and ledger["primitive_evidence_opened"] is False
            and not ledger["failed_checks"],
            "detail": ledger["acceptance_state"],
        },
        {
            "check_id": "all_expected_primitives_have_contract_rows",
            "passed": len(rows) == 9
            and sorted(row["primitive_id"] for row in rows)
            == sorted(row["primitive_id"] for row in ledger["producer_residue_rows"]),
            "detail": [row["primitive_id"] for row in rows],
        },
        {
            "check_id": "continuation_descriptors_defined_geometric",
            "passed": all(
                row["continuation_function_descriptor"]["descriptor_kind"]
                == "bounded_geometric_continuation_condition"
                and row["continuation_function_descriptor"][
                    "native_function_descriptor_alias_meaning"
                ].startswith("alias only")
                for row in rows
            ),
            "detail": "native function is alias only, not semantic purpose or goal",
        },
        {
            "check_id": "proxy_metrics_defined_as_signs_not_replacements",
            "passed": all(
                row["proxy_metric_definition"]["proxy_kind"]
                == "bounded_indicator_not_replacement"
                and row["proxy_metric_definition"][
                    "proxy_success_replaces_continuation"
                ]
                is False
                for row in rows
            ),
            "detail": "proxy metrics cannot replace continuation function",
        },
        {
            "check_id": "proxy_only_success_blockers_defined",
            "passed": all(proxy_only_blocker_present(row) for row in rows),
            "detail": "proxy improves while basin continuation fails -> primitive not supported",
        },
        {
            "check_id": "blocked_relabels_not_used_as_proxy_metrics",
            "passed": all(not proxy_has_blocked_term(row) for row in rows)
            and all(
                row["proxy_metric_definition"][
                    "blocked_relabels_as_proxy_metrics_allowed"
                ]
                is False
                for row in rows
            ),
            "detail": BLOCKED_PROXY_TERMS,
        },
        {
            "check_id": "support_scaffold_declarations_defined",
            "passed": all(
                row["support_scaffold_declaration"]["declared_supports"]
                and row["support_scaffold_declaration"]["required_supports"]
                and row["support_scaffold_declaration"][
                    "producer_supplied_scaffolds"
                ]
                and row["support_scaffold_declaration"]["hidden_support_allowed"]
                is False
                for row in rows
            ),
            "detail": "declared, required, producer-supplied, and withdrawable supports present",
        },
        {
            "check_id": "ap4_ap5_dependencies_carried_forward_locally",
            "passed": all(gap_summary.values()),
            "detail": gap_summary,
        },
        {
            "check_id": "rows_remain_incomplete_until_iteration5",
            "passed": all(row["contract_status"] != "complete" for row in rows)
            and all(row["contract_complete_allowed"] is False for row in rows)
            and artifact["rows_marked_complete"] is False,
            "detail": artifact["contract_status_counts"],
        },
        {
            "check_id": "primitive_specific_descriptors_distinct",
            "passed": len({descriptor_signature(row) for row in rows}) == len(rows),
            "detail": "continuation/proxy/scaffold descriptor signatures are unique",
        },
        {
            "check_id": "n21_handoff_inputs_present",
            "passed": len(n21_rows) == 2
            and all("n21_handoff_inputs" in row for row in n21_rows)
            and all(
                all(
                    key in row["n21_handoff_inputs"]
                    for key in [
                        "withdrawal_condition",
                        "declared_supports",
                        "support_floor",
                        "coherence_floor",
                        "hidden_support_blocker",
                        "probe_present_condition",
                        "probe_absent_condition",
                        "proxy_only_success_blocker",
                    ]
                )
                for row in n21_rows
            ),
            "detail": [row["primitive_id"] for row in n21_rows],
        },
        {
            "check_id": "unsafe_claim_flags_false_per_row",
            "passed": all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "artifact_invariants_preserved",
            "passed": artifact["artifact_invariants"] == INVARIANTS
            and all(row["artifact_invariants"] == INVARIANTS for row in rows),
            "detail": artifact["artifact_invariants"],
        },
        {
            "check_id": "no_primitive_evidence_opened",
            "passed": artifact["primitive_evidence_opened"] is False
            and all(row["primitive_supported"] is False for row in rows)
            and all(row["primitive_evidence_opened"] is False for row in rows),
            "detail": {
                "primitive_evidence_opened": artifact["primitive_evidence_opened"],
                "native_support_opened": artifact["native_support_opened"],
            },
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(artifact),
            "detail": "contract paths are relative",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 4 - Continuation Function / Proxy / Scaffold Contract",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"row_count = {artifact['row_count']}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"native_function_descriptors_defined = {str(artifact['native_function_descriptors_defined']).lower()}",
        f"proxy_metric_definitions_defined = {str(artifact['proxy_metric_definitions_defined']).lower()}",
        f"support_scaffold_declarations_defined = {str(artifact['support_scaffold_declarations_defined']).lower()}",
        f"rows_marked_complete = {str(artifact['rows_marked_complete']).lower()}",
        "```",
        "",
        "Interpretation:",
        "",
        "Iteration 4 defines bounded continuation-function, proxy, and "
        "support/scaffold contracts. It does not test any primitive and does "
        "not mark any primitive complete; I5 still owns same-basin criteria and "
        "the full control contract.",
        "",
        "Primitive contracts:",
        "",
        "| Primitive | Contract Status | Proxy Metric | Support/Scaffold | AP Gaps |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in artifact["contract_rows"]:
        proxy = row["proxy_metric_definition"]["measured_quantity"]
        scaffold_count = len(row["support_scaffold_declaration"]["declared_supports"])
        gaps = [
            gap["ap_level"] for gap in row["ap_gap_contract"]["ap_gap_dependencies"]
        ] + [
            f"{gap['ap_level']} conditional"
            for gap in row["ap_gap_contract"]["conditional_gap_dependencies"]
        ]
        lines.append(
            f"| {row['primitive_id']} | {row['contract_status']} | {proxy} | "
            f"{scaffold_count} declared supports | {', '.join(gaps) if gaps else 'none'} |"
        )
    lines.extend(
        [
            "",
            "N21 handoff inputs:",
            "",
            "```json",
            json.dumps(artifact["n21_handoff_inputs"], indent=2, sort_keys=True),
            "```",
            "",
            "Proxy-only fail-closed rule:",
            "",
            "```text",
            artifact["proxy_only_fail_closed_rule"],
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.extend(
        [
            "",
            "Claim boundary:",
            "",
            "```text",
            artifact["claim_boundary"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ledger = load_json(SOURCE_LEDGER)
    rows = build_rows(ledger)
    artifact: dict[str, Any] = {
        "artifact_id": "n20_native_function_proxy_contract",
        "schema_version": "n20_native_function_proxy_contract_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 4,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Define bounded continuation-function, proxy metric, and support/"
            "scaffold contracts for each N20 becoming primitive without testing "
            "or supporting primitive evidence."
        ),
        "source_ledger": source_ledger_reference(ledger),
        "artifact_invariants": INVARIANTS,
        "native_function_descriptors_defined": True,
        "continuation_function_descriptors_defined": True,
        "proxy_metric_definitions_defined": True,
        "support_scaffold_declarations_defined": True,
        "proxy_only_success_blockers_defined": True,
        "primitive_evidence_opened": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_spec_opened": False,
        "contract_rows": rows,
        "row_count": len(rows),
        "contract_status_counts": classification_counts(rows),
        "rows_marked_complete": any(row["contract_status"] == "complete" for row in rows),
        "ap4_ap5_local_dependency_summary": ap_gap_summary(rows),
        "n21_handoff_inputs": [
            row["n21_handoff_inputs"]
            for row in rows
            if "n21_handoff_inputs" in row
        ],
        "proxy_only_fail_closed_rule": (
            "A proxy metric can be an indicator only. If the proxy improves while "
            "the continuation function, declared basin signature, support floor, "
            "coherence floor, boundary condition, or flux condition fails, the "
            "primitive is not supported."
        ),
        "iteration5_handoff": {
            "ready_for_iteration_5_same_basin_control_contract": True,
            "remaining_contract_status": "incomplete_missing_same_basin_rule",
            "remaining_contract_objects": [
                "same_basin_continuation_rule",
                "minimum_controls",
            ],
            "i5_must_define": [
                "same-basin continuation criteria",
                "allowed drift",
                "support/coherence floors",
                "boundary integrity and flux balance criteria",
                "replay requirements",
                "fail-closed controls",
            ],
        },
        "claim_boundary": (
            "N20 Iteration 4 defines contract objects only. It does not test or "
            "support withdrawal resistance, naturalization depth, susceptibility "
            "update, live-continuation collapse, optionality, spark/new-basin "
            "formation, proxy collapse, transfer, generative persistence, agency, "
            "Phase 8, native support, sentience, or semantic function."
        ),
        "output_digest": "pending",
    }
    checks = build_checks(artifact, ledger)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "accepted_native_function_proxy_scaffold_contract_no_primitive_evidence"
        if not failed_checks
        else "failed_native_function_proxy_scaffold_contract"
    )
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()
