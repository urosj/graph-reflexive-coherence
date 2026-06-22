#!/usr/bin/env python3
"""Build N20 Iteration 5 same-basin continuation and control contract."""

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
SOURCE_CONTRACT = EXPERIMENT / "outputs" / "n20_native_function_proxy_contract.json"
OUTPUT = EXPERIMENT / "outputs" / "n20_same_basin_continuation_contract.json"
REPORT = EXPERIMENT / "reports" / "n20_same_basin_continuation_contract.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_same_basin_continuation_contract.py"
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

SHARED_CONTROL_IDS = [
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
]

SHARED_CONTROL_DEFINITIONS = {
    "label_only_success_control": {
        "control_kind": "label_relabel_blocker",
        "blocked_condition": (
            "continuation label changes or persists while basin signature, support, "
            "coherence, boundary, flux, or replay criteria fail"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "proxy_only_success_control": {
        "control_kind": "proxy_replacement_blocker",
        "blocked_condition": (
            "proxy metric improves while same-basin continuation criteria fail"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "hidden_producer_support_control": {
        "control_kind": "hidden_support_blocker",
        "blocked_condition": (
            "undeclared producer support preserves the row after declared support "
            "or scaffold is withdrawn"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "post_hoc_trace_construction_control": {
        "control_kind": "trace_order_blocker",
        "blocked_condition": (
            "continuation trace is assembled after the fact instead of replaying "
            "from declared source-current fields"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "semantic_relabel_control": {
        "control_kind": "semantic_overclaim_blocker",
        "blocked_condition": (
            "agency, choice, goal, intention, sentience, selfhood, identity, or "
            "life labels are used as evidence"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "native_support_relabel_control": {
        "control_kind": "native_support_overclaim_blocker",
        "blocked_condition": (
            "producer-mediated or naturalization-debt state is relabeled as native "
            "support"
        ),
        "expected_result": "rejected_fail_closed",
    },
    "phase8_relabel_control": {
        "control_kind": "phase8_overclaim_blocker",
        "blocked_condition": (
            "contract artifact is relabeled as Phase 8 implementation or source "
            "mutation support"
        ),
        "expected_result": "rejected_fail_closed",
    },
}

SAME_BASIN_RULES = {
    "withdrawal_resistance": {
        "basin_signature_fields": [
            "basin_signature_trace",
            "boundary_integrity_trace",
            "support_coherence_floor_trace",
        ],
        "allowed_drift": "bounded support reduction may lower margin but may not change declared basin signature",
        "required_support_floor": "support remains above declared withdrawal floor",
        "required_coherence_floor": "coherence remains above declared withdrawal floor",
        "boundary_integrity_floor": "boundary remains distinguishable during withdrawal",
        "flux_balance_bounds": "leakage cannot explain apparent persistence under support reduction",
        "replay_requirement": "withdrawal run replays from declared support schedule without hidden producer support",
        "failure_modes": [
            "basin signature changes",
            "support floor crosses below declared floor",
            "coherence floor crosses below declared floor",
            "hidden support preserves margin",
            "label-only resistance",
        ],
        "primitive_specific_controls": [
            "withdrawal_schedule_removed_control",
            "hidden_support_margin_control",
            "support_floor_crossing_control",
        ],
    },
    "naturalization_depth": {
        "basin_signature_fields": [
            "post_probe_basin_signature_trace",
            "post_probe_support_floor_trace",
            "post_probe_coherence_floor_trace",
        ],
        "allowed_drift": "probe removal may reduce margin but not erase post-probe basin signature",
        "required_support_floor": "post-probe support remains above residual floor",
        "required_coherence_floor": "post-probe coherence remains above residual floor",
        "boundary_integrity_floor": "post-probe boundary remains distinguishable",
        "flux_balance_bounds": "residual persistence cannot be imported by hidden support flux",
        "replay_requirement": "multi-window replay without original probe/scaffold",
        "failure_modes": [
            "probe residue preserves row",
            "post-probe signature absent",
            "support annotation replaces source-current support",
            "depth score without replay",
        ],
        "primitive_specific_controls": [
            "probe_present_only_control",
            "probe_residue_control",
            "support_source_annotation_relabel_control",
        ],
    },
    "susceptibility_update": {
        "basin_signature_fields": [
            "pre_interaction_geometry_trace",
            "post_interaction_geometry_trace",
            "susceptibility_delta_trace",
        ],
        "allowed_drift": "durable geometry delta must remain within declared route or region boundary",
        "required_support_floor": "altered geometry stays above support floor",
        "required_coherence_floor": "altered geometry stays above coherence floor",
        "boundary_integrity_floor": "route or region boundary remains auditable after update",
        "flux_balance_bounds": "durable delta cannot be a one-window flux transient",
        "replay_requirement": "later replay preserves susceptibility delta without producer reinforcement",
        "failure_modes": [
            "route label changed without geometry change",
            "delta vanishes on replay",
            "reinforcement schedule supplies hidden support",
            "AP4 gap omitted when base route-conditioned susceptibility participates",
            "AP5 gap omitted when proxy-conditioned susceptibility participates",
        ],
        "primitive_specific_controls": [
            "durable_geometry_modification_control",
            "route_label_only_control",
            "reinforcement_schedule_removed_control",
            "AP4_gap_dependency_if_route_conditioned",
            "AP5_gap_dependency_if_proxy_conditioned",
        ],
    },
    "live_continuation_collapse": {
        "basin_signature_fields": [
            "live_branch_set_trace",
            "branch_support_coherence_traces",
            "collapsed_continuation_trace",
        ],
        "allowed_drift": "branch collapse may select one branch but alternatives must remain auditable",
        "required_support_floor": "selected branch support remains above floor",
        "required_coherence_floor": "selected branch coherence remains above floor",
        "boundary_integrity_floor": "live branches are boundary-distinguishable before collapse",
        "flux_balance_bounds": "selection cannot be explained by merge, leakage, or external flux",
        "replay_requirement": "branch set and collapse replay without selected-branch label",
        "failure_modes": [
            "fake alternatives",
            "single branch relabeled as choice",
            "post-hoc selected branch",
            "producer preference injection",
            "random tie masquerading as collapse",
        ],
        "primitive_specific_controls": [
            "fake_alternative_control",
            "single_branch_relabel_control",
            "producer_preference_injection_control",
            "post_hoc_selected_branch_control",
        ],
    },
    "surplus_supported_optionality": {
        "basin_signature_fields": [
            "support_surplus_margin_trace",
            "optional_continuation_set_trace",
            "maintenance_floor_trace",
        ],
        "allowed_drift": "optional branches may open only while maintenance basin remains above floor",
        "required_support_floor": "maintenance support floor preserved",
        "required_coherence_floor": "maintenance coherence floor preserved",
        "boundary_integrity_floor": "boundary remains coherent while optional branches are open",
        "flux_balance_bounds": "optional branch flux cannot drain maintenance support below floor",
        "replay_requirement": "surplus and optional branch set replay under same budget surface",
        "failure_modes": [
            "hidden budget relief",
            "maintenance floor crossing",
            "optional branch label without geometry",
            "reward/proxy gain mistaken for abundance",
        ],
        "primitive_specific_controls": [
            "floor_crossing_control",
            "hidden_budget_relief_control",
            "optional_branch_label_only_control",
        ],
    },
    "spark_sub_basin_new_basin_formation": {
        "basin_signature_fields": [
            "bifurcation_trace",
            "new_boundary_candidate_trace",
            "new_basin_support_coherence_trace",
        ],
        "allowed_drift": "new/sub-basin candidate may diverge from old basin only within declared bifurcation rule",
        "required_support_floor": "new/sub-basin support floor present",
        "required_coherence_floor": "new/sub-basin coherence floor present",
        "boundary_integrity_floor": "new/sub-basin boundary distinguishable from thickened old basin",
        "flux_balance_bounds": "merge or leakage cannot masquerade as new basin formation",
        "replay_requirement": "bifurcation and distinguishable boundary replay without seed label",
        "failure_modes": [
            "label-only new basin",
            "single-basin thickening relabel",
            "transient fluctuation misread as basin",
            "hidden producer insertion",
        ],
        "primitive_specific_controls": [
            "label_only_new_basin_control",
            "single_basin_thickening_relabel_control",
            "hidden_producer_insertion_control",
            "transient_replay_failure_control",
        ],
    },
    "proxy_divergence_proxy_collapse": {
        "basin_signature_fields": [
            "basin_persistence_capacity_trace",
            "support_coherence_floor_trace",
            "basin_deepening_comparison_trace",
        ],
        "allowed_drift": "proxy value may vary only while basin persistence capacity remains coupled",
        "required_support_floor": "basin persistence support floor preserved",
        "required_coherence_floor": "basin deepening coherence floor preserved",
        "boundary_integrity_floor": "proxy gain remains distinguishable from basin support",
        "flux_balance_bounds": "proxy gain cannot hide support leakage or target-policy flux",
        "replay_requirement": "proxy and basin traces replay with target digest recorded before use",
        "failure_modes": [
            "proxy-only improvement",
            "post-hoc target derivation",
            "hidden proxy policy",
            "basin persistence stalls while proxy improves",
            "AP5 gap omitted",
        ],
        "primitive_specific_controls": [
            "proxy_only_improvement_control",
            "post_hoc_target_derivation_control",
            "hidden_proxy_policy_control",
            "AP5_gap_dependency",
        ],
    },
    "configuration_substrate_transfer": {
        "basin_signature_fields": [
            "pre_transfer_basin_signature_trace",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
        ],
        "allowed_drift": "mapped fixture/topology may change but declared basin signature must remain within mapping tolerance",
        "required_support_floor": "post-transfer support floor preserved",
        "required_coherence_floor": "post-transfer coherence floor preserved",
        "boundary_integrity_floor": "mapped boundary preserves distinguishability",
        "flux_balance_bounds": "transfer cannot be support reconstruction through hidden flux",
        "replay_requirement": "transfer replays under structurally distinct fixture or mapping",
        "failure_modes": [
            "same label on different basin",
            "fixture equivalence label without mapping",
            "hidden support reconstruction",
            "AP4 gap omitted when route-conditioned selection participates",
            "cross-substrate transfer claimed without declared source-backed substrate mapping",
        ],
        "primitive_specific_controls": [
            "transfer_mapping_declaration_control",
            "reconstructed_support_ledger_control",
            "fixture_equivalence_label_control",
            "AP4_gap_dependency_if_route_conditioned",
            "cross_substrate_mapping_declaration_control",
        ],
    },
    "generative_extractive_persistence": {
        "basin_signature_fields": [
            "focal_basin_stability_trace",
            "neighbor_basin_distinguishability_trace",
            "neighbor_support_floor_trace",
        ],
        "allowed_drift": "focal persistence may affect neighborhood only without reducing neighbor distinguishability below floor",
        "required_support_floor": "focal and neighbor support floors visible",
        "required_coherence_floor": "focal and neighbor coherence distinguishable",
        "boundary_integrity_floor": "neighbor structures do not merge into focal basin",
        "flux_balance_bounds": "environment capacity gain cannot be extraction, leakage, or merge pressure",
        "replay_requirement": "focal and environment-side traces replay under same medium-debt boundary",
        "failure_modes": [
            "generativity label only",
            "neighbor support degraded while focal persists",
            "merge/leakage masquerading as support",
            "medium debt relabeled as ecology proof",
        ],
        "primitive_specific_controls": [
            "generativity_label_control",
            "extractive_persistence_control",
            "merge_leakage_as_generation_control",
            "medium_debt_placeholder_control",
            "medium_debt_as_success_control",
            "direct_message_scaffold_as_native_medium_control",
            "shared_medium_label_only_control",
        ],
    },
}

PRIMITIVE_DEPENDENCY_MAP = {
    "N21": [
        "withdrawal_condition",
        "support_scaffold_declaration",
        "support_floor",
        "coherence_floor",
        "same_basin_continuation_rule",
        "hidden_producer_support_control",
        "proxy_only_success_control",
    ],
    "N22": [
        "susceptibility_fields",
        "replay_requirement",
        "durable_geometry_modification_controls",
        "AP4_gap_dependency_if_route_conditioned",
        "AP5_gap_dependency_if_proxy_conditioned",
    ],
    "N23": [
        "live_continuation_set",
        "fake_alternative_controls",
        "producer_preference_injection_blockers",
        "AP4_gap_dependency",
    ],
    "N24": [
        "surplus_support_condition",
        "optional_continuation_space",
        "floor_crossing_controls",
        "hidden_budget_relief_control",
    ],
    "N25": [
        "basin_signature",
        "sub_basin_distinguishability_rule",
        "new_basin_replay_requirement",
        "hidden_producer_insertion_control",
    ],
    "N26": [
        "proxy_metric_definition",
        "continuation_function_descriptor",
        "proxy_divergence_condition",
        "proxy_collapse_condition",
        "AP5_gap_dependency",
    ],
    "N27": [
        "basin_signature",
        "transfer_mapping_declaration",
        "reconstructed_support_ledger",
        "producer_residue_ledger",
        "source_backed_substrate_mapping_if_cross_substrate",
    ],
    "N28": [
        "generative_persistence_fields",
        "extractive_persistence_fields",
        "environment_basin_forming_capacity_fields",
        "medium_debt_placeholder",
        "medium_debt_as_success_control",
        "direct_message_scaffold_as_native_medium_control",
        "shared_medium_label_only_control",
    ],
}

DEFINITION_COMPONENT_VALIDATION = [
    {
        "component_id": "basin_signature_fields",
        "definition_role": "identity_of_the_geometric_object_under_test",
        "source_basis": [
            "I3 substrate-carried field ledger",
            "I4 bounded continuation-function descriptors",
            "Arc of Becoming classification method",
        ],
        "source_role": "ledger_and_method_backed_contract_requirement",
        "correctness_status": "valid_as_required_contract_gate_not_as_evidence",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "label, proxy, or output could replace the basin itself",
        "downstream_revision_policy": (
            "N21-N28 may refine the field list only by recording source-backed "
            "geometry showing that the declared signature is over- or under-specific"
        ),
    },
    {
        "component_id": "allowed_drift",
        "definition_role": "bounded_change_permitted_without_identity_language",
        "source_basis": [
            "N16 boundary-state maturity and drift controls",
            "N18 limited h4/L5 horizon and bottleneck constraints",
            "Arc of Becoming interrogation method",
        ],
        "source_role": "conservative_admissibility_assumption",
        "correctness_status": "valid_as_fail_closed_bound_pending_primitive_tests",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "any change could be relabeled as same basin or no change could be allowed",
        "downstream_revision_policy": (
            "N21-N28 must treat drift bounds as test targets; changes require "
            "source-backed pass/fail evidence, not semantic preference"
        ),
    },
    {
        "component_id": "support_and_coherence_floors",
        "definition_role": "minimum internal viability of the continuing basin",
        "source_basis": [
            "N13 support/regulation evidence",
            "N16 boundary requirements",
            "N18 long-horizon support/proxy stress",
            "N19 Phase-8 readiness telemetry classification",
        ],
        "source_role": "prior_experiment_backed_contract_requirement",
        "correctness_status": "valid_as_required_contract_gate_not_fixed_numeric_threshold",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "a basin could count as continuing after losing its support/coherence basis",
        "downstream_revision_policy": (
            "N21-N28 must instantiate numeric floors per primitive and record "
            "floor-crossing controls"
        ),
    },
    {
        "component_id": "boundary_integrity_floor",
        "definition_role": "separability_of_the_continuing_basin",
        "source_basis": [
            "N16 AP6 artifact-level self/environment boundary classification",
            "N16 leakage/separability requirements",
            "N19 AP6 native-readiness classification",
        ],
        "source_role": "direct_prior_boundary_evidence",
        "correctness_status": "valid_as_required_contract_gate",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "merge, leakage, or external structure could be misread as continuation",
        "downstream_revision_policy": (
            "N21-N28 may refine boundary criteria only by preserving N16/N19 "
            "separability and unsafe-claim blockers"
        ),
    },
    {
        "component_id": "flux_balance_bounds",
        "definition_role": "prevents flow/leakage/extraction from masquerading as persistence",
        "source_basis": [
            "N16 directional-flux challenge and boundary-state sweep",
            "N17 resource/support and shared-medium loop controls",
            "N18 shared-medium and cross-axis bottleneck stress",
        ],
        "source_role": "prior_experiment_backed_contract_requirement",
        "correctness_status": "valid_as_required_contract_gate_with_primitive_specific_thresholds_pending",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "support transfer, leakage, merge pressure, or extraction could look like same-basin persistence",
        "downstream_revision_policy": (
            "N21-N28 must make flux bounds operational in their own geometry and "
            "fail closed when leakage/merge/extraction explains success"
        ),
    },
    {
        "component_id": "replay_requirement",
        "definition_role": "artifact-level reproducibility and hidden-state blocker",
        "source_basis": [
            "N15 replay/digest discipline",
            "N16 artifact/duplicate/order/snapshot replay controls",
            "N17 loop replay and order controls",
            "N18 long-horizon replay and stale-axis controls",
            "N19 NAT readiness schema",
        ],
        "source_role": "direct_prior_control_evidence",
        "correctness_status": "valid_as_required_contract_gate",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "hidden runtime state or post-hoc construction could define continuity",
        "downstream_revision_policy": (
            "N21-N28 must include replay/digest inputs sufficient to reconstruct "
            "the claimed primitive row"
        ),
    },
    {
        "component_id": "failure_modes",
        "definition_role": "named ways the row must fail closed",
        "source_basis": [
            "N12-N19 claim-boundary and negative-control discipline",
            "I3 producer-residue and naturalization-debt ledger",
            "I4 proxy-only fail-closed rule",
        ],
        "source_role": "prior_control_pattern_and_row_specific_contract",
        "correctness_status": "valid_as_initial_fail_closed_taxonomy",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "later rows could pass by exploiting unnamed failure channels",
        "downstream_revision_policy": (
            "N21-N28 may add failure modes when source-backed tests expose new "
            "ways to fake continuation; they may not remove existing blockers "
            "without evidence"
        ),
    },
    {
        "component_id": "blocked_relabels",
        "definition_role": "unsafe semantic and native-support claim boundary",
        "source_basis": [
            "N12-N19 unsafe claim blockers",
            "N19 AP4/AP5 NAT4 gap preservation",
            "I3 blocked_relabel variable classification",
        ],
        "source_role": "direct_claim_boundary_evidence",
        "correctness_status": "valid_as_required_claim_boundary",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "agency, choice, goal, selfhood, native support, or sentience labels could become evidence",
        "downstream_revision_policy": (
            "Blocked relabels are non-converting labels; they cannot become "
            "proxy metrics or substrate-carried evidence in N21-N28"
        ),
    },
    {
        "component_id": "minimum_controls",
        "definition_role": "shared fail-closed control surface for every primitive",
        "source_basis": [
            "N16 negative control matrix",
            "N17 replay/order/hidden-state controls",
            "N18 stale-axis and replay controls",
            "N19 naturalization review controls",
        ],
        "source_role": "direct_prior_control_evidence",
        "correctness_status": "valid_as_minimum_control_template",
        "necessity_status": "necessary_not_sufficient",
        "risk_if_omitted": "later primitive evidence could pass through label-only, proxy-only, hidden support, or native-support relabel paths",
        "downstream_revision_policy": (
            "N21-N28 can add primitive-specific controls but cannot remove the "
            "minimum shared template"
        ),
    },
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
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def source_contract_reference(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(SOURCE_CONTRACT),
        "sha256": sha256_file(SOURCE_CONTRACT),
        "output_digest": contract["output_digest"],
        "status": contract["status"],
        "acceptance_state": contract["acceptance_state"],
        "row_count": contract["row_count"],
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


def control_record(control_id: str, row: dict[str, Any]) -> dict[str, Any]:
    template = SHARED_CONTROL_DEFINITIONS[control_id]
    return {
        "control_id": control_id,
        "control_kind": template["control_kind"],
        "blocked_condition": template["blocked_condition"],
        "expected_result": template["expected_result"],
        "fail_closed": True,
        "claim_allowed_when_control_triggers": False,
        "source_contract_row": row["row_id"],
    }


def primitive_control_record(control_id: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_kind": "primitive_specific_fail_closed_control",
        "blocked_condition": f"{control_id} blocks primitive-specific relabel or hidden support path",
        "expected_result": "rejected_or_blocked_fail_closed",
        "fail_closed": True,
        "claim_allowed_when_control_triggers": False,
        "source_contract_row": row["row_id"],
    }


def same_basin_rule(row: dict[str, Any]) -> dict[str, Any]:
    primitive_id = row["primitive_id"]
    rule = SAME_BASIN_RULES[primitive_id]
    return {
        "rule_id": f"n20_i5_{primitive_id}_same_basin_rule",
        "basin_signature_fields": [
            f"{primitive_id}.{field}" for field in rule["basin_signature_fields"]
        ],
        "allowed_drift": rule["allowed_drift"],
        "required_support_floor": rule["required_support_floor"],
        "required_coherence_floor": rule["required_coherence_floor"],
        "boundary_integrity_floor": rule["boundary_integrity_floor"],
        "flux_balance_bounds": rule["flux_balance_bounds"],
        "replay_requirement": rule["replay_requirement"],
        "failure_modes": rule["failure_modes"],
        "blocked_relabels": row["blocked_relabel_fields"],
        "label_only_continuation_allowed": False,
        "proxy_only_success_allowed": False,
        "hidden_producer_support_allowed": False,
        "source_contract_row": row["row_id"],
    }


def minimum_controls(row: dict[str, Any]) -> dict[str, Any]:
    primitive_ids = SAME_BASIN_RULES[row["primitive_id"]]["primitive_specific_controls"]
    shared = [control_record(control_id, row) for control_id in SHARED_CONTROL_IDS]
    primitive_specific = [
        primitive_control_record(control_id, row) for control_id in primitive_ids
    ]
    return {
        "status": "defined",
        "shared_control_template_ids": SHARED_CONTROL_IDS,
        "shared_controls": shared,
        "primitive_specific_controls": primitive_specific,
        "all_controls_fail_closed": True,
        "source_contract_row": row["row_id"],
    }


def build_rows(i4_contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i4_row in i4_contract["contract_rows"]:
        primitive_id = i4_row["primitive_id"]
        controls = minimum_controls(i4_row)
        row = {
            "row_id": i4_row["row_id"].replace("n20_i4", "n20_i5"),
            "source_i4_row_id": i4_row["row_id"],
            "primitive_id": primitive_id,
            "primitive_name": i4_row["primitive_name"],
            "roadmap_target": i4_row["roadmap_target"],
            "expected_first_positive_experiment": i4_row[
                "expected_first_positive_experiment"
            ],
            "diagnostic_source_titles": i4_row["diagnostic_source_titles"],
            "source_inventory_row_ids": i4_row["source_inventory_row_ids"],
            "source_role_dependencies": i4_row["source_role_dependencies"],
            "LGRC_visible_fields": i4_row["LGRC_visible_fields"],
            "producer_mediated_fields": i4_row["producer_mediated_fields"],
            "naturalization_debt_fields": i4_row["naturalization_debt_fields"],
            "blocked_relabel_fields": i4_row["blocked_relabel_fields"],
            "primitive_specific_consumption_inputs": PRIMITIVE_DEPENDENCY_MAP[
                i4_row["expected_first_positive_experiment"]
            ],
            "continuation_function_descriptor": i4_row[
                "continuation_function_descriptor"
            ],
            "native_function_descriptor_alias": i4_row[
                "native_function_descriptor_alias"
            ],
            "proxy_metric_definition": i4_row["proxy_metric_definition"],
            "support_scaffold_declaration": i4_row["support_scaffold_declaration"],
            "same_basin_continuation_rule": same_basin_rule(i4_row),
            "minimum_controls": controls,
            "contract_status": "complete",
            "contract_complete_allowed": True,
            "contract_complete_scope": "N20_contract_row_complete_not_primitive_evidence",
            "missing_contract_objects": [],
            "row_decision": "supported",
            "contract_row_supported_as": (
                "same_basin_continuation_and_control_contract_defined"
            ),
            "primitive_supported": False,
            "primitive_evidence_opened": False,
            "ap_gap_contract": i4_row["ap_gap_contract"],
            "claim_ceiling": (
                "complete N20 contract row only; no primitive evidence, agency, "
                "Phase 8, native support, sentience, or semantic function"
            ),
            "unsafe_claim_flags": i4_row["unsafe_claim_flags"],
            "artifact_invariants": INVARIANTS,
            "downstream_consumption_status": (
                "contract_complete_pending_iteration6_closeout"
            ),
            "downstream_immutability_rule": i4_row["downstream_immutability_rule"],
            "source_consumption_rules": i4_row["source_consumption_rules"],
        }
        if primitive_id == "susceptibility_update":
            row["ap5_dependency_split"] = {
                "status": "explicit_split_not_gap_removal",
                "base_susceptibility_update": {
                    "ap4_gap_dependency": "required_if_route_conditioned",
                    "ap5_gap_dependency": "not_required_when_proxy_target_formation_absent",
                },
                "proxy_conditioned_susceptibility_update": {
                    "ap5_gap_dependency": "required_when_proxy_or_target_formation_participates",
                    "source": "N19/N15",
                },
                "i2_source_map_relation": (
                    "I2 required AP5 propagation for direct proxy/target "
                    "primitives and a general rule for any later primitive that "
                    "depends on proxy derivation or target formation. I5 makes "
                    "that general rule row-local for susceptibility_update."
                ),
            }
        if primitive_id == "configuration_substrate_transfer":
            row["transfer_scope_contract"] = {
                "primary_scope": "configuration_or_topology_transfer_inside_LGRC",
                "cross_substrate_transfer_status": "optional_conditional_extension",
                "cross_substrate_requirement": (
                    "cross-substrate transfer requires a declared source-backed "
                    "substrate mapping before it can be counted"
                ),
            }
        if primitive_id == "generative_extractive_persistence":
            row["medium_debt_control_scope"] = {
                "medium_debt_as_success_allowed": False,
                "direct_message_scaffold_as_native_medium_allowed": False,
                "shared_medium_label_only_success_allowed": False,
            }
        if "n21_handoff_inputs" in i4_row:
            row["n21_handoff_inputs"] = i4_row["n21_handoff_inputs"]
        rows.append(row)
    return rows


def contract_status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(row["contract_status"] for row in rows)
    return dict(sorted(counts.items()))


def definition_component_counts() -> dict[str, int]:
    counts: Counter[str] = Counter(
        component["source_role"] for component in DEFINITION_COMPONENT_VALIDATION
    )
    return dict(sorted(counts.items()))


def definition_components_have_source_basis() -> bool:
    required_fields = {
        "component_id",
        "definition_role",
        "source_basis",
        "source_role",
        "correctness_status",
        "necessity_status",
        "risk_if_omitted",
        "downstream_revision_policy",
    }
    return all(
        set(component) >= required_fields
        and isinstance(component["source_basis"], list)
        and bool(component["source_basis"])
        and all(isinstance(source, str) and source for source in component["source_basis"])
        for component in DEFINITION_COMPONENT_VALIDATION
    )


def definition_components_are_necessary_not_sufficient() -> bool:
    return all(
        component["necessity_status"] == "necessary_not_sufficient"
        for component in DEFINITION_COMPONENT_VALIDATION
    )


def definition_revision_policies_present() -> bool:
    return all(
        bool(component["downstream_revision_policy"])
        for component in DEFINITION_COMPONENT_VALIDATION
    )


def definition_validation_has_expected_roles() -> bool:
    roles = {component["source_role"] for component in DEFINITION_COMPONENT_VALIDATION}
    expected_roles = {
        "ledger_and_method_backed_contract_requirement",
        "conservative_admissibility_assumption",
        "prior_experiment_backed_contract_requirement",
        "direct_prior_boundary_evidence",
        "direct_prior_control_evidence",
        "prior_control_pattern_and_row_specific_contract",
        "direct_claim_boundary_evidence",
    }
    return expected_roles <= roles


def all_same_basin_fields_present(row: dict[str, Any]) -> bool:
    required = [
        "basin_signature_fields",
        "allowed_drift",
        "required_support_floor",
        "required_coherence_floor",
        "boundary_integrity_floor",
        "flux_balance_bounds",
        "replay_requirement",
        "failure_modes",
        "blocked_relabels",
    ]
    rule = row["same_basin_continuation_rule"]
    return all(rule.get(field) for field in required)


def all_shared_controls_present(row: dict[str, Any]) -> bool:
    ids = {
        control["control_id"] for control in row["minimum_controls"]["shared_controls"]
    }
    return ids == set(SHARED_CONTROL_IDS)


def all_controls_fail_closed(row: dict[str, Any]) -> bool:
    controls = (
        row["minimum_controls"]["shared_controls"]
        + row["minimum_controls"]["primitive_specific_controls"]
    )
    return all(
        control["fail_closed"] is True
        and control["claim_allowed_when_control_triggers"] is False
        and "fail_closed" in control["expected_result"]
        for control in controls
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


def primitive_dependency_map_matches_rows(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        target = row["expected_first_positive_experiment"]
        if target == "N21":
            expected = PRIMITIVE_DEPENDENCY_MAP["N21"]
        else:
            expected = PRIMITIVE_DEPENDENCY_MAP[target]
        if row["primitive_specific_consumption_inputs"] != expected:
            return False
    return True


def susceptibility_ap5_split_is_explicit(rows: list[dict[str, Any]]) -> bool:
    row = next(row for row in rows if row["primitive_id"] == "susceptibility_update")
    control_ids = {
        control["control_id"]
        for control in row["minimum_controls"]["primitive_specific_controls"]
    }
    conditional_ap5 = any(
        gap["ap_level"] == "AP5"
        for gap in row["ap_gap_contract"]["conditional_gap_dependencies"]
    )
    return (
        row.get("ap5_dependency_split", {}).get("status")
        == "explicit_split_not_gap_removal"
        and conditional_ap5
        and "AP5_gap_dependency_if_proxy_conditioned" in control_ids
        and "AP5_gap_dependency_if_proxy_conditioned"
        in row["primitive_specific_consumption_inputs"]
    )


def configuration_transfer_scope_is_explicit(rows: list[dict[str, Any]]) -> bool:
    row = next(
        row for row in rows if row["primitive_id"] == "configuration_substrate_transfer"
    )
    control_ids = {
        control["control_id"]
        for control in row["minimum_controls"]["primitive_specific_controls"]
    }
    return (
        row.get("transfer_scope_contract", {}).get("primary_scope")
        == "configuration_or_topology_transfer_inside_LGRC"
        and row["transfer_scope_contract"]["cross_substrate_transfer_status"]
        == "optional_conditional_extension"
        and "cross_substrate_mapping_declaration_control" in control_ids
        and "source_backed_substrate_mapping_if_cross_substrate"
        in row["primitive_specific_consumption_inputs"]
    )


def n28_medium_debt_controls_are_explicit(rows: list[dict[str, Any]]) -> bool:
    row = next(row for row in rows if row["primitive_id"] == "generative_extractive_persistence")
    control_ids = {
        control["control_id"]
        for control in row["minimum_controls"]["primitive_specific_controls"]
    }
    required = {
        "medium_debt_as_success_control",
        "direct_message_scaffold_as_native_medium_control",
        "shared_medium_label_only_control",
    }
    return (
        required <= control_ids
        and required <= set(row["primitive_specific_consumption_inputs"])
        and row.get("medium_debt_control_scope", {}).get("medium_debt_as_success_allowed")
        is False
    )


def build_checks(artifact: dict[str, Any], i4_contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = artifact["contract_rows"]
    gap_summary = artifact["ap4_ap5_local_dependency_summary"]
    checks = [
        {
            "check_id": "source_i4_contract_passed_and_ready",
            "passed": i4_contract["status"] == "passed"
            and i4_contract["iteration5_handoff"][
                "ready_for_iteration_5_same_basin_control_contract"
            ]
            is True
            and not i4_contract["failed_checks"],
            "detail": i4_contract["acceptance_state"],
        },
        {
            "check_id": "all_expected_primitives_have_i5_rows",
            "passed": len(rows) == 9
            and sorted(row["primitive_id"] for row in rows)
            == sorted(row["primitive_id"] for row in i4_contract["contract_rows"]),
            "detail": [row["primitive_id"] for row in rows],
        },
        {
            "check_id": "same_basin_required_fields_present",
            "passed": all(all_same_basin_fields_present(row) for row in rows),
            "detail": "basin signature, drift, floors, boundary, flux, replay, failures, blockers",
        },
        {
            "check_id": "support_coherence_boundary_flux_replay_defined",
            "passed": all(
                row["same_basin_continuation_rule"]["required_support_floor"]
                and row["same_basin_continuation_rule"]["required_coherence_floor"]
                and row["same_basin_continuation_rule"]["boundary_integrity_floor"]
                and row["same_basin_continuation_rule"]["flux_balance_bounds"]
                and row["same_basin_continuation_rule"]["replay_requirement"]
                for row in rows
            ),
            "detail": "floors, boundary, flux, and replay present in every row",
        },
        {
            "check_id": "minimum_shared_control_template_present",
            "passed": all(all_shared_controls_present(row) for row in rows),
            "detail": SHARED_CONTROL_IDS,
        },
        {
            "check_id": "primitive_specific_controls_present",
            "passed": all(
                row["minimum_controls"]["primitive_specific_controls"] for row in rows
            ),
            "detail": "primitive-specific controls are non-empty per row",
        },
        {
            "check_id": "all_controls_fail_closed",
            "passed": all(all_controls_fail_closed(row) for row in rows),
            "detail": "controls reject or block claim when triggered",
        },
        {
            "check_id": "proxy_only_success_rejected",
            "passed": all(
                row["same_basin_continuation_rule"]["proxy_only_success_allowed"]
                is False
                and any(
                    control["control_id"] == "proxy_only_success_control"
                    for control in row["minimum_controls"]["shared_controls"]
                )
                for row in rows
            ),
            "detail": "proxy-only success cannot satisfy same-basin continuation",
        },
        {
            "check_id": "label_only_continuation_rejected",
            "passed": all(
                row["same_basin_continuation_rule"][
                    "label_only_continuation_allowed"
                ]
                is False
                and any(
                    control["control_id"] == "label_only_success_control"
                    for control in row["minimum_controls"]["shared_controls"]
                )
                for row in rows
            ),
            "detail": "label-only continuation cannot satisfy same-basin continuation",
        },
        {
            "check_id": "hidden_producer_support_rejected",
            "passed": all(
                row["same_basin_continuation_rule"][
                    "hidden_producer_support_allowed"
                ]
                is False
                and any(
                    control["control_id"] == "hidden_producer_support_control"
                    for control in row["minimum_controls"]["shared_controls"]
                )
                for row in rows
            ),
            "detail": "hidden producer support cannot satisfy same-basin continuation",
        },
        {
            "check_id": "ap4_ap5_dependencies_carried_forward_locally",
            "passed": all(gap_summary.values()),
            "detail": gap_summary,
        },
        {
            "check_id": "primitive_dependency_map_frozen",
            "passed": primitive_dependency_map_matches_rows(rows)
            and artifact["primitive_dependency_map"] == PRIMITIVE_DEPENDENCY_MAP,
            "detail": artifact["primitive_dependency_map"],
        },
        {
            "check_id": "susceptibility_ap5_dependency_split_explicit",
            "passed": susceptibility_ap5_split_is_explicit(rows)
            and artifact["ap5_dependency_refinement"][
                "susceptibility_update_split_status"
            ]
            == "explicit_split_not_gap_removal",
            "detail": artifact["ap5_dependency_refinement"],
        },
        {
            "check_id": "configuration_transfer_scope_primary",
            "passed": configuration_transfer_scope_is_explicit(rows)
            and artifact["configuration_transfer_scope"][
                "configuration_transfer_is_primary"
            ]
            is True
            and artifact["configuration_transfer_scope"][
                "cross_substrate_transfer_requires_source_backed_mapping"
            ]
            is True,
            "detail": artifact["configuration_transfer_scope"],
        },
        {
            "check_id": "n28_medium_debt_relation_controls_present",
            "passed": n28_medium_debt_controls_are_explicit(rows)
            and artifact["n28_medium_debt_control_requirements"][
                "medium_debt_as_success_allowed"
            ]
            is False,
            "detail": artifact["n28_medium_debt_control_requirements"],
        },
        {
            "check_id": "medium_debt_deferred_until_n28_n29",
            "passed": artifact["medium_debt"]["medium_debt_status"]
            == "deferred_until_N28_N29"
            and artifact["medium_debt"]["medium_debt_not_applicable_before_N28"]
            is True
            and "medium_debt_placeholder"
            in PRIMITIVE_DEPENDENCY_MAP["N28"],
            "detail": artifact["medium_debt"],
        },
        {
            "check_id": "definition_components_have_source_basis",
            "passed": definition_components_have_source_basis()
            and len(artifact["definition_component_validation"]) == 9,
            "detail": [
                component["component_id"]
                for component in artifact["definition_component_validation"]
            ],
        },
        {
            "check_id": "definition_components_are_necessary_not_sufficient",
            "passed": definition_components_are_necessary_not_sufficient()
            and artifact["definition_sufficiency_status"]
            == "necessary_contract_gates_not_sufficient_primitive_evidence",
            "detail": artifact["definition_sufficiency_status"],
        },
        {
            "check_id": "definition_revision_policy_present",
            "passed": definition_revision_policies_present()
            and bool(artifact["definition_revision_policy"]),
            "detail": artifact["definition_revision_policy"],
        },
        {
            "check_id": "definition_validation_source_roles_explicit",
            "passed": definition_validation_has_expected_roles(),
            "detail": artifact["definition_component_counts"],
        },
        {
            "check_id": "future_outcomes_not_pre_decided_by_contract",
            "passed": artifact["definition_outcome_guard"][
                "future_rows_must_supply_source_backed_pass_fail_evidence"
            ]
            is True
            and artifact["definition_outcome_guard"][
                "ad_hoc_redefinition_to_pass_allowed"
            ]
            is False
            and artifact["definition_outcome_guard"][
                "contract_definitions_are_primitive_evidence"
            ]
            is False,
            "detail": artifact["definition_outcome_guard"],
        },
        {
            "check_id": "contract_rows_complete_but_not_primitive_evidence",
            "passed": all(row["contract_status"] == "complete" for row in rows)
            and all(row["primitive_supported"] is False for row in rows)
            and all(row["primitive_evidence_opened"] is False for row in rows)
            and artifact["primitive_evidence_opened"] is False
            and artifact["contract_completion_alias"]["contract_complete"] is True
            and artifact["contract_completion_alias"]["primitive_supported"] is False,
            "detail": {
                "contract_status_counts": artifact["contract_status_counts"],
                "contract_completion_alias": artifact["contract_completion_alias"],
            },
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
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(artifact),
            "detail": "contract paths are relative",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 5 - Same-Basin Continuation And Control Contract",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"row_count = {artifact['row_count']}",
        f"contract_rows_complete = {str(artifact['contract_rows_complete']).lower()}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"same_basin_rules_defined = {str(artifact['same_basin_rules_defined']).lower()}",
        f"minimum_controls_defined = {str(artifact['minimum_controls_defined']).lower()}",
        "```",
        "",
        "Interpretation:",
        "",
        "Iteration 5 completes the N20 contract rows by defining same-basin "
        "continuation rules and fail-closed controls. Complete means the contract "
        "surface is complete, not that any primitive is supported.",
        "",
        "Primitive rows:",
        "",
        "| Primitive | Contract Status | Same-Basin Signature Fields | Shared Controls | Specific Controls |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in artifact["contract_rows"]:
        lines.append(
            f"| {row['primitive_id']} | {row['contract_status']} | "
            f"{len(row['same_basin_continuation_rule']['basin_signature_fields'])} | "
            f"{len(row['minimum_controls']['shared_controls'])} | "
            f"{len(row['minimum_controls']['primitive_specific_controls'])} |"
        )
    lines.extend(
        [
            "",
            "Shared controls:",
            "",
            "```json",
            json.dumps(artifact["minimum_shared_control_template"], indent=2),
            "```",
            "",
            "AP5 dependency refinement:",
            "",
            "```json",
            json.dumps(artifact["ap5_dependency_refinement"], indent=2, sort_keys=True),
            "```",
            "",
            "Transfer and medium-debt scope:",
            "",
            "```json",
            json.dumps(
                {
                    "configuration_transfer_scope": artifact[
                        "configuration_transfer_scope"
                    ],
                    "n28_medium_debt_control_requirements": artifact[
                        "n28_medium_debt_control_requirements"
                    ],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Medium debt:",
            "",
            "```json",
            json.dumps(artifact["medium_debt"], indent=2, sort_keys=True),
            "```",
            "",
            "Definition validation:",
            "",
            "These definitions are evidence-informed contract gates. They are not "
            "primitive evidence and they do not pre-decide N21-N28 outcomes.",
            "",
            f"Definition sufficiency status: `{artifact['definition_sufficiency_status']}`",
            "",
            "| Component | Source Role | Correctness Status | Necessity |",
            "| --- | --- | --- | --- |",
        ]
    )
    for component in artifact["definition_component_validation"]:
        lines.append(
            f"| {component['component_id']} | {component['source_role']} | "
            f"{component['correctness_status']} | {component['necessity_status']} |"
        )
    lines.extend(
        [
            "",
            "Definition revision policy:",
            "",
            "```text",
            artifact["definition_revision_policy"],
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
    i4_contract = load_json(SOURCE_CONTRACT)
    rows = build_rows(i4_contract)
    artifact: dict[str, Any] = {
        "artifact_id": "n20_same_basin_continuation_contract",
        "schema_version": "n20_same_basin_continuation_contract_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 5,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Define same-basin continuation criteria, replay requirements, and "
            "fail-closed controls for all N20 becoming-primitive contract rows."
        ),
        "source_contract": source_contract_reference(i4_contract),
        "artifact_invariants": INVARIANTS,
        "same_basin_rules_defined": True,
        "minimum_controls_defined": True,
        "primitive_dependency_map_defined": True,
        "contract_rows_complete": True,
        "primitive_evidence_opened": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_spec_opened": False,
        "contract_rows": rows,
        "row_count": len(rows),
        "contract_status_counts": contract_status_counts(rows),
        "contract_completion_alias": {
            "contract_complete": True,
            "contract_complete_means": "N20_contract_surface_complete",
            "primitive_supported": False,
            "primitive_evidence_opened": False,
            "all_primitives_complete_language_allowed": False,
        },
        "minimum_shared_control_template": SHARED_CONTROL_IDS,
        "primitive_dependency_map": PRIMITIVE_DEPENDENCY_MAP,
        "ap4_ap5_local_dependency_summary": ap_gap_summary(rows),
        "ap5_dependency_refinement": {
            "susceptibility_update_split_status": "explicit_split_not_gap_removal",
            "base_susceptibility_update": (
                "AP4 is required when route-conditioned selection participates; "
                "AP5 is not required for proxy-free susceptibility update"
            ),
            "proxy_conditioned_susceptibility_update": (
                "AP5 is required when proxy derivation or target formation "
                "participates in susceptibility update"
            ),
            "i2_relation": (
                "I2 required AP5 for the direct proxy-collapse primitive and "
                "froze the general rule that any primitive depending on proxy "
                "derivation or target formation must carry AP5. I5 makes that "
                "general rule explicit for susceptibility_update instead of "
                "treating all susceptibility updates as AP5-dependent."
            ),
            "n19_ap5_gap_removed": False,
        },
        "configuration_transfer_scope": {
            "configuration_transfer_is_primary": True,
            "primary_scope": "configuration_or_topology_transfer_inside_LGRC",
            "cross_substrate_transfer_status": "optional_conditional_extension",
            "cross_substrate_transfer_requires_source_backed_mapping": True,
            "full_substrate_transfer_supported_by_n20": False,
        },
        "n28_medium_debt_control_requirements": {
            "medium_debt_as_success_allowed": False,
            "direct_message_scaffold_as_native_medium_allowed": False,
            "shared_medium_label_only_success_allowed": False,
            "required_additional_controls": [
                "medium_debt_as_success_control",
                "direct_message_scaffold_as_native_medium_control",
                "shared_medium_label_only_control",
            ],
        },
        "definition_validation_status": (
            "validated_as_evidence_informed_conservative_contract_not_as_primitive_evidence"
        ),
        "definition_sufficiency_status": (
            "necessary_contract_gates_not_sufficient_primitive_evidence"
        ),
        "definition_component_validation": DEFINITION_COMPONENT_VALIDATION,
        "definition_component_counts": definition_component_counts(),
        "definition_correctness_boundary": (
            "I5 definitions are correctness constraints for future primitive tests. "
            "They are necessary contract gates derived from prior artifacts and "
            "method sources, not direct proof that any primitive is supported."
        ),
        "definition_revision_policy": (
            "N21-N28 cannot redefine basin signature, continuation condition, "
            "proxy-only success, or producer-residue classification ad hoc in "
            "order to pass. A later experiment may only revise an I5 definition "
            "by recording source-backed evidence that the definition is over- or "
            "under-constraining, while preserving N19 AP4/AP5 gap propagation and "
            "unsafe claim blockers."
        ),
        "definition_outcome_guard": {
            "contract_definitions_are_primitive_evidence": False,
            "future_rows_must_supply_source_backed_pass_fail_evidence": True,
            "ad_hoc_redefinition_to_pass_allowed": False,
            "row_specific_thresholds_must_be_declared_before_use": True,
            "claim_boundary_must_be_preserved": True,
        },
        "medium_debt": {
            "medium_debt_status": "deferred_until_N28_N29",
            "medium_debt_not_applicable_before_N28": True,
            "medium_debt_first_contract_owner": "N28",
            "first_formal_agentic_ecology_bridge": "N29",
            "claim_boundary": (
                "medium debt is a placeholder for later graph-substrate and "
                "agentic-ecology work, not ant-ecology implementation in N20"
            ),
        },
        "iteration6_handoff": {
            "ready_for_iteration_6_closeout": True,
            "n20_contract_rows_complete": True,
            "primitive_evidence_opened": False,
            "remaining_closeout_tasks": [
                "confirm primitive evidence remains unopened",
                "confirm agency/native/Phase8/sentience remain unopened",
                "record final N21 withdrawal-resistance handoff",
                "record final N21 naturalization-depth handoff",
                "confirm src_diff_empty",
            ],
        },
        "claim_boundary": (
            "N20 Iteration 5 completes contract rows only. It does not test or "
            "support withdrawal resistance, naturalization depth, susceptibility "
            "update, live-continuation collapse, optionality, spark/new-basin "
            "formation, proxy collapse, transfer, generative persistence, agency, "
            "Phase 8, native support, sentience, ant ecology, or semantic function."
        ),
        "output_digest": "pending",
    }
    checks = build_checks(artifact, i4_contract)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "accepted_same_basin_control_contract_complete_no_primitive_evidence"
        if not failed_checks
        else "failed_same_basin_control_contract"
    )
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()
