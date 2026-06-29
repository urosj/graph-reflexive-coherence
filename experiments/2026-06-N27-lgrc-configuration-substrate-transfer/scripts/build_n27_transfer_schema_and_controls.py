#!/usr/bin/env python3
"""Build N27 Iteration 2 transfer schema and control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n27_transfer_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_transfer_schema_and_controls.py"
)

N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N26_CLOSEOUT_PATH = (
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
    "outputs/n26_closeout_and_n27_handoff.json"
)

DESCRIPTOR_CONTRACT_ROW = "n20_i4_row_08_configuration_substrate_transfer"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_08_configuration_substrate_transfer"

CT_LADDER = [
    {
        "rung": "CT0",
        "definition": "no source-current transfer evidence",
        "positive_transfer_support_allowed": False,
    },
    {
        "rung": "CT1",
        "definition": "declared mapping and pre-transfer basin signature present",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
        ],
        "transfer_claim_allowed": False,
    },
    {
        "rung": "CT2",
        "definition": "source-current post-transfer signature and boundary mapping observed",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
            "support_preservation_trace",
            "coherence_preservation_trace",
            "flux_balance_trace",
        ],
        "transfer_claim_allowed": False,
    },
    {
        "rung": "CT3",
        "definition": "replay-backed same-basin transfer candidate",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
            "support_preservation_trace",
            "coherence_preservation_trace",
            "flux_balance_trace",
            "replay_trace",
        ],
    },
    {
        "rung": "CT4",
        "definition": "control-backed configuration/topology transfer candidate",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
            "support_preservation_trace",
            "coherence_preservation_trace",
            "flux_balance_trace",
            "replay_trace",
            "control_trace",
        ],
    },
    {
        "rung": "CT5",
        "definition": "stress/variant-backed transfer candidate across multiple declared mappings",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
            "support_preservation_trace",
            "coherence_preservation_trace",
            "flux_balance_trace",
            "replay_trace",
            "control_trace",
            "stress_variant_trace",
        ],
    },
    {
        "rung": "CT6",
        "definition": "N28-ready bounded transfer evidence with claim-clean handoff",
        "required_artifact_roles": [
            "transfer_mapping_trace",
            "pre_transfer_basin_signature_trace",
            "threshold_record",
            "post_transfer_basin_signature_trace",
            "boundary_mapping_trace",
            "support_preservation_trace",
            "coherence_preservation_trace",
            "flux_balance_trace",
            "replay_trace",
            "control_trace",
            "stress_variant_trace",
            "closeout",
            "N28_handoff_record",
        ],
        "handoff_rung_only": True,
        "semantic_identity_claim_allowed": False,
        "agency_claim_allowed": False,
    },
]

N27_CLOSEOUT_LADDER = [
    {"rung": "N27-C0", "definition": "initialized contract only"},
    {"rung": "N27-C1", "definition": "source inventory and transfer contract admission passed"},
    {"rung": "N27-C2", "definition": "transfer schema and controls frozen"},
    {"rung": "N27-C3", "definition": "active nulls fail closed"},
    {"rung": "N27-C4", "definition": "source-current transfer candidate supported"},
    {
        "rung": "N27-C5",
        "definition": "replay/control/stress-backed transfer candidate supported",
    },
    {"rung": "N27-C6", "definition": "N28-ready bounded transfer closeout"},
]

REQUIRED_CANDIDATE_FIELDS = [
    "row_id",
    "iteration",
    "row_decision",
    "ct_ladder_rung",
    "n27_closeout_ceiling",
    "source_current_inputs",
    "source_inventory_output_digest",
    "source_contract_row_digest",
    "source_output_digest",
    "descriptor_contract_row_digest",
    "consumable_contract_row_digest",
    "n26_closeout_output_digest",
    "run_artifact_id",
    "runtime_config_digest",
    "artifact_manifest",
    "all_artifact_sha256_match_file_contents",
    "derived_report_only",
    "row_specific_thresholds_declared_before_use",
    "transfer_scope",
    "transfer_core",
    "transfer_core_digest",
    "transfer_mapping_id",
    "transfer_mapping_digest",
    "mapping_declared_before_use",
    "mapping_source_backed",
    "pre_transfer_basin_signature_trace",
    "post_transfer_basin_signature_trace",
    "boundary_mapping_trace",
    "support_preservation_trace",
    "coherence_preservation_trace",
    "flux_balance_trace",
    "original_fixture_support_change_trace",
    "reconstructed_support_ledger",
    "hidden_support_reconstruction_absent",
    "same_basin_signature_preserved_under_mapping",
    "same_label_different_basin_rejected",
    "proxy_score_relabel_rejected",
    "configuration_label_only_rejected",
    "support_reconstruction_as_transfer_rejected",
    "n25_2_direct_transfer_consumption_used",
    "n25_2_consumed_only_through_n26_context",
    "signature_preservation_margin_formula",
    "boundary_mapping_tolerance_formula",
    "support_floor_margin_formula",
    "coherence_floor_margin_formula",
    "flux_balance_bound_formula",
    "threshold_record_digest",
    "replay_result",
    "control_results",
    "ap4_dependency_status",
    "ap4_condition_reason",
    "ap5_dependency_status",
    "ap5_condition_reason",
    "claim_ceiling",
    "unsafe_claim_flags",
]

TRANSFER_CORE_FIELDS = [
    "transfer_scope",
    "transfer_mapping_id",
    "transfer_mapping_digest",
    "mapping_declared_before_use",
    "mapping_source_backed",
    "pre_signature_digest",
    "post_signature_digest",
    "boundary_mapping_digest",
    "support_preservation_digest",
    "coherence_preservation_digest",
    "flux_balance_digest",
]

CONTROL_ROWS = [
    {
        "control_id": "same_label_different_basin_control",
        "blocked_condition": "same label appears after mapping but basin signature or boundary differs",
        "expected_result": "failed_closed",
        "rung_effect": "CT1_or_stronger_blocked",
        "orthogonal_role": "rejects label identity",
    },
    {
        "control_id": "fixture_equivalence_label_only_control",
        "blocked_condition": "fixture or topology is declared equivalent without source-current mapping",
        "expected_result": "failed_closed",
        "rung_effect": "CT1_or_stronger_blocked",
        "orthogonal_role": "rejects mapping-free fixture similarity",
    },
    {
        "control_id": "mapping_declared_after_outcome_control",
        "blocked_condition": "transfer mapping is declared after seeing the post-transfer result",
        "expected_result": "failed_closed",
        "rung_effect": "CT1_or_stronger_blocked",
        "orthogonal_role": "rejects post-hoc mapping",
    },
    {
        "control_id": "proxy_score_relabel_as_transfer_control",
        "blocked_condition": "proxy score is preserved while basin signature or boundary mapping fails",
        "expected_result": "failed_closed",
        "rung_effect": "CT2_or_stronger_blocked",
        "orthogonal_role": "rejects proxy preservation",
    },
    {
        "control_id": "hidden_support_reconstruction_control",
        "blocked_condition": "undeclared producer support rebuilds the post-transfer basin",
        "expected_result": "failed_closed",
        "rung_effect": "CT2_or_stronger_blocked",
        "orthogonal_role": "rejects hidden rebuilding",
    },
    {
        "control_id": "support_reconstruction_as_transfer_control",
        "blocked_condition": "reconstructed support ledger is counted as preserved support",
        "expected_result": "failed_closed",
        "rung_effect": "CT2_or_stronger_blocked",
        "orthogonal_role": "rejects post-hoc reconstruction",
    },
    {
        "control_id": "boundary_mapping_missing_control",
        "blocked_condition": "post-transfer boundary is not mapped from the pre-transfer boundary",
        "expected_result": "failed_closed",
        "rung_effect": "CT2_or_stronger_blocked",
        "orthogonal_role": "rejects unmapped boundary",
    },
    {
        "control_id": "post_transfer_signature_missing_control",
        "blocked_condition": "post-transfer basin signature is missing",
        "expected_result": "failed_closed",
        "rung_effect": "CT2_or_stronger_blocked",
        "orthogonal_role": "rejects missing post-transfer state",
    },
    {
        "control_id": "source_current_inputs_missing_control",
        "blocked_condition": "row is derived from report labels rather than source-current runtime inputs",
        "expected_result": "failed_closed",
        "rung_effect": "CT1_or_stronger_blocked",
        "orthogonal_role": "rejects report-only evidence",
    },
    {
        "control_id": "cross_substrate_mapping_missing_control",
        "blocked_condition": "substrate transfer is claimed without source-backed substrate mapping",
        "expected_result": "failed_closed",
        "rung_effect": "substrate_transfer_claim_blocked",
        "orthogonal_role": "rejects unmapped substrate claims",
    },
    {
        "control_id": "artifact_manifest_failure_control",
        "blocked_condition": "artifact path, role, or SHA-256 validation fails",
        "expected_result": "failed_closed",
        "rung_effect": "positive_transfer_support_blocked",
        "orthogonal_role": "rejects unverifiable artifacts",
    },
    {
        "control_id": "replay_failure_control",
        "blocked_condition": "artifact, snapshot/load, duplicate, or mapping-order replay fails",
        "expected_result": "failed_closed",
        "rung_effect": "CT3_or_stronger_blocked",
        "orthogonal_role": "rejects non-replayable transfer",
    },
    {
        "control_id": "stress_variant_failure_control",
        "blocked_condition": "mapping tolerance, support, coherence, or flux stress fails",
        "expected_result": "failed_closed",
        "rung_effect": "CT5_or_stronger_blocked",
        "orthogonal_role": "rejects overbroad robustness",
    },
    {
        "control_id": "AP4_dependency_omitted_control",
        "blocked_condition": "route-conditioned selection participates but AP4 dependency is omitted",
        "expected_result": "failed_closed",
        "rung_effect": "row_blocks_at_AP4_gate",
        "orthogonal_role": "rejects prose-only AP4 handling",
    },
    {
        "control_id": "AP5_dependency_omitted_control",
        "blocked_condition": "proxy/target formation participates but AP5 dependency is omitted",
        "expected_result": "failed_closed",
        "rung_effect": "row_blocks_at_AP5_gate",
        "orthogonal_role": "rejects prose-only AP5 handling",
    },
    {
        "control_id": "n26_proxy_as_transfer_evidence_control",
        "blocked_condition": "N26 PD6 proxy result is counted as N27 transfer evidence",
        "expected_result": "failed_closed",
        "rung_effect": "positive_transfer_support_blocked",
        "orthogonal_role": "rejects proxy-to-transfer relabel",
    },
    {
        "control_id": "n26_scoped_ap5_as_native_ap5_control",
        "blocked_condition": "N26 scoped artifact AP5 bridge is promoted to native AP5",
        "expected_result": "failed_closed",
        "rung_effect": "AP5_NAT4_gap_resolution_blocked",
        "orthogonal_role": "rejects native AP5 relabel",
    },
    {
        "control_id": "n25_2_direct_transfer_consumption_control",
        "blocked_condition": "N25.2 is consumed directly as N27 substrate transfer evidence",
        "expected_result": "failed_closed",
        "rung_effect": "positive_transfer_support_blocked",
        "orthogonal_role": "rejects direct N25.2 backfill",
    },
    {
        "control_id": "semantic_identity_relabel_control",
        "blocked_condition": "semantic identity or selfhood is used as transfer evidence",
        "expected_result": "failed_closed",
        "rung_effect": "unsafe_claim_blocked",
        "orthogonal_role": "rejects identity overclaim",
    },
    {
        "control_id": "semantic_choice_goal_relabel_control",
        "blocked_condition": "semantic choice, goal, or intention is used as transfer evidence",
        "expected_result": "failed_closed",
        "rung_effect": "unsafe_claim_blocked",
        "orthogonal_role": "rejects semantic agency language",
    },
    {
        "control_id": "native_support_relabel_control",
        "blocked_condition": "producer-mediated or transfer-preserved support is relabeled native support",
        "expected_result": "failed_closed",
        "rung_effect": "unsafe_claim_blocked",
        "orthogonal_role": "rejects native support overclaim",
    },
    {
        "control_id": "phase8_ant_ecology_relabel_control",
        "blocked_condition": "N27 transfer evidence is relabeled Phase 8 completion or ant ecology",
        "expected_result": "failed_closed",
        "rung_effect": "unsafe_claim_blocked",
        "orthogonal_role": "rejects downstream project overclaim",
    },
]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json_path(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def load_json(relative_path: str) -> dict[str, Any]:
    return load_json_path(ROOT / relative_path)


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def find_contract_row(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in data.get("contract_rows", []):
        if isinstance(row, dict) and row.get("row_id") == row_id:
            return row
    raise ValueError(f"missing contract row {row_id}")


def source_record(path: str, source_id: str, role: str) -> dict[str, Any]:
    record = {
        "source_id": source_id,
        "path": path,
        "source_role": role,
        "exists": (ROOT / path).exists(),
        "sha256": sha256_file(path),
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["artifact_id"] = data.get("artifact_id", "not_recorded")
        record["status"] = data.get("status", "not_recorded")
        record["acceptance_state"] = data.get("acceptance_state", "not_recorded")
        record["output_digest"] = data.get("output_digest", "not_recorded")
    else:
        record["artifact_id"] = "markdown_source"
        record["status"] = "context_only"
        record["acceptance_state"] = "not_applicable_markdown_context"
        record["output_digest"] = "not_applicable_markdown_context"
    return record


def build_source_digest_pins(
    i1: dict[str, Any], descriptor_row: dict[str, Any], consumable_row: dict[str, Any]
) -> dict[str, Any]:
    n26_record = next(row for row in i1["source_records"] if row["source_id"] == "n26_closeout")
    return {
        "source_inventory_output_digest": i1["output_digest"],
        "descriptor_contract_row": DESCRIPTOR_CONTRACT_ROW,
        "descriptor_contract_row_digest": digest_value(descriptor_row),
        "consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
        "consumable_contract_row_digest": digest_value(consumable_row),
        "n20_native_function_artifact_sha256": sha256_file(N20_NATIVE_FUNCTION_PATH),
        "n20_same_basin_artifact_sha256": sha256_file(N20_SAME_BASIN_PATH),
        "n26_closeout_output_digest": n26_record["output_digest"],
        "n26_closeout_artifact_sha256": n26_record["sha256"],
    }


def build_candidate_row_schema(source_digest_pins: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_candidate_transfer_row_schema_v1",
        "required_fields": REQUIRED_CANDIDATE_FIELDS,
        "required_source_digests": source_digest_pins,
        "required_values_for_positive_rows": {
            "all_artifact_sha256_match_file_contents": True,
            "derived_report_only": False,
            "mapping_declared_before_use": True,
            "mapping_source_backed": True,
            "hidden_support_reconstruction_absent": True,
            "same_label_different_basin_rejected": True,
            "proxy_score_relabel_rejected": True,
            "configuration_label_only_rejected": True,
            "support_reconstruction_as_transfer_rejected": True,
            "n25_2_direct_transfer_consumption_used": False,
            "n25_2_consumed_only_through_n26_context": True,
        },
        "row_specific_thresholds_declared_before_use_required": True,
        "source_current_inputs_required_non_empty": True,
        "artifact_manifest_required_non_empty": True,
        "absolute_paths_allowed": False,
        "positive_row_cannot_use": [
            "same_label_only",
            "nearby_basin_movement_only",
            "visual_topological_similarity_only",
            "proxy_score_preservation_only",
            "hidden_support_reconstruction",
            "N26_PD6_as_transfer_evidence",
            "direct_N25_2_transfer_consumption",
        ],
    }


def build_transfer_core_schema() -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_transfer_core_schema_v1",
        "required_fields": TRANSFER_CORE_FIELDS,
        "required_values": {
            "mapping_declared_before_use": True,
            "mapping_source_backed": True,
        },
        "canonicalization": {
            "canonical_form": "json_sort_keys_no_runtime_timestamp",
            "digest_field": "transfer_core_digest",
            "positive_rows_reference_core_by_digest": True,
            "duplicated_top_level_fields_must_match_transfer_core": True,
        },
        "fail_closed_if_only": [
            "same_label_after_mapping",
            "nearby_basin_shift_inside_same_frame",
            "visual_or_topological_similarity",
            "proxy_score_preservation",
            "hidden_support_reconstruction",
            "support_reconstruction_as_transfer",
        ],
    }


def build_transfer_scope_schema() -> dict[str, Any]:
    return {
        "allowed_transfer_scopes": ["configuration", "fixture", "topology", "substrate"],
        "primary_scope": "configuration_or_topology_transfer_inside_LGRC",
        "substrate_scope_requirements": [
            "declared_source_backed_substrate_mapping",
            "mapping_source_artifact_digest",
            "boundary_side_assignment_mapping",
            "support_coherence_interpretation_mapping",
        ],
        "substrate_scope_missing_requirement_effect": "substrate_transfer_claim_blocked_or_demoted_to_configuration_only",
        "basin_movement_is_transfer": False,
        "movement_vs_transfer_rule": {
            "movement": "same-frame basin center or boundary shift in existing geometry",
            "transfer": "declared cross-frame mapping with pre/post signature, boundary mapping, support/coherence preservation, and flux discipline",
        },
    }


def build_artifact_role_schema() -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_rung_specific_artifact_role_schema_v1",
        "per_artifact_required_fields": ["path", "sha256", "artifact_role"],
        "artifact_roles_by_ct_rung": {
            row["rung"]: row["required_artifact_roles"]
            for row in CT_LADDER
            if "required_artifact_roles" in row
        },
        "positive_support_blockers": [
            "artifact_missing",
            "sha256_mismatch",
            "artifact_role_missing",
            "derived_report_only_true",
            "absolute_path_present",
            "rung_required_artifact_role_missing",
        ],
    }


def build_support_reconstruction_schema() -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_support_preservation_reconstruction_split_v1",
        "required_fields": [
            "support_preservation_trace",
            "original_fixture_support_change_trace",
            "reconstructed_support_ledger",
            "hidden_support_reconstruction_absent",
            "support_reconstruction_as_transfer_rejected",
        ],
        "support_preservation_required_for_ct2_or_stronger": True,
        "hidden_support_reconstruction_allowed": False,
        "reconstructed_support_may_be_recorded_as": "producer_residue_or_negative_control_context",
        "reconstructed_support_must_not_be_counted_as": "support_preservation_trace",
        "failure_effects": {
            "hidden_support_reconstruction_present": "CT2_or_stronger_blocked",
            "reconstructed_support_counted_as_preserved_support": "CT2_or_stronger_blocked",
            "original_fixture_support_change_trace_missing": "support_reconstruction_control_inconclusive_blocks_CT4_or_stronger",
        },
    }


def build_replay_schema() -> dict[str, Any]:
    return {
        "ct3_required_replay_modes": [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "mapping_order_replay",
        ],
        "ct3_if_any_required_replay_fails": "CT3_or_stronger_blocked",
        "ct4_or_stronger_requires_controls_fail_closed": True,
        "ct5_or_stronger_requires_stress_variant_replay": True,
        "duplicate_replay_semantics": "stable digest and no duplicate positive row creation",
        "order_replay_semantics": "mapping declaration must precede post-transfer signature",
    }


def build_threshold_formula_schema() -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_threshold_formula_schema_v1",
        "required_formula_fields": [
            "signature_preservation_margin_formula",
            "boundary_mapping_tolerance_formula",
            "support_floor_margin_formula",
            "coherence_floor_margin_formula",
            "flux_balance_bound_formula",
        ],
        "required_threshold_fields": [
            "threshold_record_digest",
            "row_specific_thresholds_declared_before_use",
        ],
        "declared_before_use_required": True,
        "formula_records_must_be_source_current_or_schema_backed": True,
        "missing_formula_effect": "same_basin_under_mapping_metric_incomplete_blocks_CT3_or_stronger",
        "threshold_declared_after_outcome_effect": "positive_transfer_support_blocked",
        "interpretation": (
            "same basin under mapping must be measured by declared formulas and "
            "thresholds, not interpreted after seeing the outcome"
        ),
    }


def build_ap_dependency_schema() -> dict[str, Any]:
    allowed = ["required_recorded", "missing_blocks_row", "not_applicable"]
    return {
        "ap4_dependency_status_enum": allowed,
        "ap5_dependency_status_enum": allowed,
        "ap4_condition_reason_required": True,
        "ap5_condition_reason_required": True,
        "not_applicable_requires_reason": True,
        "ap4_required_when": ["route_conditioned_selection_participates"],
        "ap5_required_when": ["proxy_or_target_formation_participates"],
        "prose_only_dependency_handling_allowed": False,
        "n26_scoped_ap5_context_counts_as_native_ap5": False,
        "n26_scoped_ap5_context_resolves_ap5_nat4_gap": False,
        "missing_dependency_effect": "row_blocks_at_AP_gate",
    }


def build_control_schema() -> dict[str, Any]:
    return {
        "schema_id": "n27_i2_transfer_control_schema_v1",
        "required_control_ids": [row["control_id"] for row in CONTROL_ROWS],
        "control_rows": CONTROL_ROWS,
        "control_result_required_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
            "orthogonal_role",
            "control_satisfied_for_positive_row",
            "control_applicability_reason",
        ],
        "allowed_control_statuses": [
            "passed",
            "failed_closed",
            "failed_open",
            "not_run",
            "not_applicable",
        ],
        "failed_open_effect": "positive_transfer_support_invalidated",
        "not_run_required_control_effect": "dependent_CT_rung_blocked",
        "not_applicable_requires_control_applicability_reason": True,
        "active_null_acceptance": {
            "expected_status": "failed_closed",
            "failed_closed_meaning": "blocker triggered and claim was rejected",
            "failed_open_meaning": "blocker triggered but claim still passed",
        },
    }


def build_claim_boundary() -> dict[str, Any]:
    return {
        "claim_ceiling": "schema/control freeze only; no transfer evidence or CT rung assigned",
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "blocked_claims": [
            "semantic identity",
            "semantic choice",
            "semantic goal ownership",
            "semantic learning",
            "agency",
            "native support",
            "selfhood",
            "identity acceptance",
            "sentience",
            "organism/life",
            "ant ecology implementation",
            "Phase 8 completion",
            "unscoped multi-basin substrate",
            "native AP5",
            "AP5 NAT4 gap resolution",
        ],
    }


def build_checks(output: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        check(
            "i1_source_inventory_passed",
            output["source_inventory"]["status"] == "passed"
            and output["source_inventory"]["acceptance_state"]
            == "accepted_source_inventory_transfer_contract_admission_no_positive_evidence",
            {
                "status": output["source_inventory"]["status"],
                "acceptance_state": output["source_inventory"]["acceptance_state"],
            },
        ),
        check(
            "source_inventory_digest_pinned",
            output["source_digest_pins"]["source_inventory_output_digest"]
            == output["source_inventory"]["output_digest"],
            {
                "source_inventory_output_digest": output["source_inventory"]["output_digest"],
            },
        ),
        check(
            "n20_i5_normative_i4_context_only",
            output["source_precedence"]["normative_contract_row"] == CONSUMABLE_CONTRACT_ROW
            and output["source_precedence"]["descriptor_context_row"] == DESCRIPTOR_CONTRACT_ROW
            and output["source_precedence"]["deferred_i4_fields_can_weaken_transfer_gates"]
            is False,
            output["source_precedence"],
        ),
        check(
            "ct_ladder_frozen",
            [row["rung"] for row in output["ct_ladder"]]
            == ["CT0", "CT1", "CT2", "CT3", "CT4", "CT5", "CT6"],
            {"rungs": [row["rung"] for row in output["ct_ladder"]]},
        ),
        check(
            "n27_closeout_ladder_frozen",
            [row["rung"] for row in output["n27_closeout_ladder"]]
            == ["N27-C0", "N27-C1", "N27-C2", "N27-C3", "N27-C4", "N27-C5", "N27-C6"],
            {"rungs": [row["rung"] for row in output["n27_closeout_ladder"]]},
        ),
        check(
            "candidate_row_required_fields_present",
            set(REQUIRED_CANDIDATE_FIELDS).issubset(
                set(output["candidate_row_schema"]["required_fields"])
            ),
            {"field_count": len(output["candidate_row_schema"]["required_fields"])},
        ),
        check(
            "transfer_core_schema_frozen",
            output["transfer_core_schema"]["required_fields"] == TRANSFER_CORE_FIELDS
            and output["transfer_core_schema"]["required_values"]["mapping_declared_before_use"]
            is True,
            output["transfer_core_schema"],
        ),
        check(
            "transfer_scope_schema_frozen",
            output["transfer_scope_schema"]["allowed_transfer_scopes"]
            == ["configuration", "fixture", "topology", "substrate"]
            and output["transfer_scope_schema"]["basin_movement_is_transfer"] is False,
            output["transfer_scope_schema"],
        ),
        check(
            "substrate_scope_requires_source_backed_mapping",
            set(output["transfer_scope_schema"]["substrate_scope_requirements"])
            == {
                "declared_source_backed_substrate_mapping",
                "mapping_source_artifact_digest",
                "boundary_side_assignment_mapping",
                "support_coherence_interpretation_mapping",
            },
            output["transfer_scope_schema"]["substrate_scope_requirements"],
        ),
        check(
            "rung_specific_artifact_roles_frozen",
            "closeout"
            not in output["artifact_role_schema"]["artifact_roles_by_ct_rung"]["CT4"]
            and "stress_variant_trace"
            in output["artifact_role_schema"]["artifact_roles_by_ct_rung"]["CT5"]
            and "N28_handoff_record"
            in output["artifact_role_schema"]["artifact_roles_by_ct_rung"]["CT6"],
            output["artifact_role_schema"]["artifact_roles_by_ct_rung"],
        ),
        check(
            "source_current_mapping_telemetry_required",
            {
                "transfer_mapping_digest",
                "pre_signature_digest",
                "post_signature_digest",
                "boundary_mapping_digest",
                "support_preservation_digest",
                "coherence_preservation_digest",
                "flux_balance_digest",
            }.issubset(set(output["transfer_core_schema"]["required_fields"])),
            output["transfer_core_schema"]["required_fields"],
        ),
        check(
            "transfer_core_canonicalization_frozen",
            output["transfer_core_schema"]["canonicalization"]["digest_field"]
            == "transfer_core_digest"
            and output["transfer_core_schema"]["canonicalization"][
                "positive_rows_reference_core_by_digest"
            ]
            is True,
            output["transfer_core_schema"]["canonicalization"],
        ),
        check(
            "threshold_formula_schema_frozen",
            {
                "signature_preservation_margin_formula",
                "boundary_mapping_tolerance_formula",
                "support_floor_margin_formula",
                "coherence_floor_margin_formula",
                "flux_balance_bound_formula",
            }.issubset(set(output["threshold_formula_schema"]["required_formula_fields"]))
            and output["threshold_formula_schema"]["declared_before_use_required"] is True,
            output["threshold_formula_schema"],
        ),
        check(
            "support_preservation_reconstruction_split_frozen",
            output["support_reconstruction_schema"]["hidden_support_reconstruction_allowed"]
            is False
            and output["support_reconstruction_schema"]["reconstructed_support_must_not_be_counted_as"]
            == "support_preservation_trace",
            output["support_reconstruction_schema"],
        ),
        check(
            "replay_requirements_frozen",
            output["replay_schema"]["ct3_required_replay_modes"]
            == [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "mapping_order_replay",
            ]
            and output["replay_schema"]["ct3_if_any_required_replay_fails"]
            == "CT3_or_stronger_blocked",
            output["replay_schema"],
        ),
        check(
            "ap4_ap5_dependency_statuses_frozen",
            output["ap_dependency_schema"]["ap4_dependency_status_enum"]
            == ["required_recorded", "missing_blocks_row", "not_applicable"]
            and output["ap_dependency_schema"]["ap5_dependency_status_enum"]
            == ["required_recorded", "missing_blocks_row", "not_applicable"],
            output["ap_dependency_schema"],
        ),
        check(
            "ap_not_applicable_requires_reason",
            output["ap_dependency_schema"]["not_applicable_requires_reason"] is True
            and output["ap_dependency_schema"]["prose_only_dependency_handling_allowed"]
            is False,
            output["ap_dependency_schema"],
        ),
        check(
            "control_families_frozen",
            set(output["control_schema"]["required_control_ids"])
            == {row["control_id"] for row in CONTROL_ROWS},
            {"control_count": len(output["control_schema"]["required_control_ids"])},
        ),
        check(
            "orthogonal_control_roles_recorded",
            all(row.get("orthogonal_role") for row in output["control_schema"]["control_rows"])
            and len({row["orthogonal_role"] for row in output["control_schema"]["control_rows"]})
            == len(output["control_schema"]["control_rows"]),
            {
                "orthogonal_roles": [
                    row["orthogonal_role"] for row in output["control_schema"]["control_rows"]
                ]
            },
        ),
        check(
            "positive_row_control_audit_fields_frozen",
            {
                "control_satisfied_for_positive_row",
                "control_applicability_reason",
            }.issubset(set(output["control_schema"]["control_result_required_fields"]))
            and output["control_schema"][
                "not_applicable_requires_control_applicability_reason"
            ]
            is True,
            output["control_schema"]["control_result_required_fields"],
        ),
        check(
            "no_direct_n25_2_consumption_invariant_frozen",
            output["n25_2_consumption_schema"]["n25_2_direct_transfer_consumption_used_required_value"]
            is False
            and output["n25_2_consumption_schema"][
                "n25_2_consumed_only_through_n26_context_required_value"
            ]
            is True,
            output["n25_2_consumption_schema"],
        ),
        check(
            "n26_context_not_transfer_or_native_ap5",
            output["n26_context_schema"]["n26_consumed_as_transfer_evidence_allowed"]
            is False
            and output["n26_context_schema"]["n26_scoped_ap5_context_counts_as_native_ap5"]
            is False
            and output["n26_context_schema"]["n26_ap5_nat4_gap_resolution_allowed"]
            is False,
            output["n26_context_schema"],
        ),
        check(
            "no_positive_transfer_evidence_opened",
            output["positive_transfer_evidence_opened"] is False
            and output["ct_ladder_rung_assigned"] is False
            and output["candidate_rows_classified"] is False,
            {
                "positive_transfer_evidence_opened": output[
                    "positive_transfer_evidence_opened"
                ],
                "ct_ladder_rung_assigned": output["ct_ladder_rung_assigned"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in output["claim_boundary"]["unsafe_claim_flags"].values()),
            output["claim_boundary"]["unsafe_claim_flags"],
        ),
    ]
    return checks


def build_output() -> dict[str, Any]:
    i1 = load_json_path(I1_OUTPUT)
    native_function = load_json(N20_NATIVE_FUNCTION_PATH)
    same_basin = load_json(N20_SAME_BASIN_PATH)
    descriptor_row = find_contract_row(native_function, DESCRIPTOR_CONTRACT_ROW)
    consumable_row = find_contract_row(same_basin, CONSUMABLE_CONTRACT_ROW)
    source_digest_pins = build_source_digest_pins(i1, descriptor_row, consumable_row)

    output: dict[str, Any] = {
        "artifact_id": "n27_transfer_schema_and_controls",
        "schema_version": "n27_i2_transfer_schema_and_controls_v1",
        "experiment": "N27_configuration_substrate_transfer",
        "iteration": "2",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "freeze transfer schema, ladder, digest pins, and fail-closed controls",
        "status": "passed",
        "acceptance_state": "accepted_transfer_schema_and_controls_frozen_no_positive_evidence",
        "source_inventory_path": (
            "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
            "outputs/n27_source_inventory_and_transfer_contract_admission.json"
        ),
        "source_inventory": {
            "status": i1.get("status"),
            "acceptance_state": i1.get("acceptance_state"),
            "output_digest": i1.get("output_digest"),
            "ready_for_iteration_2": i1.get("ready_for_iteration_2"),
        },
        "source_records": [
            source_record(
                "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
                "outputs/n27_source_inventory_and_transfer_contract_admission.json",
                "n27_i1_source_inventory",
                "source_inventory_and_transfer_contract_admission",
            ),
            source_record(
                N20_NATIVE_FUNCTION_PATH,
                "n20_native_function_proxy_contract",
                "descriptor_context_only",
            ),
            source_record(
                N20_SAME_BASIN_PATH,
                "n20_same_basin_continuation_contract",
                "normative_consumable_transfer_contract",
            ),
            source_record(N26_CLOSEOUT_PATH, "n26_closeout", "bounded_context_not_transfer_evidence"),
        ],
        "source_precedence": {
            "normative_contract_row": CONSUMABLE_CONTRACT_ROW,
            "descriptor_context_row": DESCRIPTOR_CONTRACT_ROW,
            "n20_i5_consumable_contract_is_normative": True,
            "n20_i4_descriptor_is_context_only": True,
            "deferred_i4_fields_can_weaken_transfer_gates": False,
        },
        "source_digest_pins": source_digest_pins,
        "ct_ladder": CT_LADDER,
        "n27_closeout_ladder": N27_CLOSEOUT_LADDER,
        "candidate_row_schema": build_candidate_row_schema(source_digest_pins),
        "transfer_core_schema": build_transfer_core_schema(),
        "transfer_scope_schema": build_transfer_scope_schema(),
        "artifact_role_schema": build_artifact_role_schema(),
        "support_reconstruction_schema": build_support_reconstruction_schema(),
        "replay_schema": build_replay_schema(),
        "threshold_formula_schema": build_threshold_formula_schema(),
        "ap_dependency_schema": build_ap_dependency_schema(),
        "control_schema": build_control_schema(),
        "n25_2_consumption_schema": {
            "n25_2_direct_transfer_consumption_used_required_value": False,
            "n25_2_consumed_only_through_n26_context_required_value": True,
            "direct_n25_2_transfer_consumption_effect": "positive_transfer_support_blocked",
            "unscoped_multi_basin_substrate_consumption_effect": "positive_transfer_support_blocked",
        },
        "n26_context_schema": {
            "n26_consumed_as_transfer_evidence_allowed": False,
            "n26_scoped_ap5_context_counts_as_native_ap5": False,
            "n26_ap5_nat4_gap_resolution_allowed": False,
            "allowed_n26_roles": [
                "bounded_PD6_proxy_divergence_collapse_evidence",
                "scoped_artifact_AP5_bridge_candidate_context",
                "proxy_pressure_control_context",
                "source_current_proxy_basin_contrast_context",
            ],
        },
        "claim_boundary": build_claim_boundary(),
        "positive_transfer_evidence_opened": False,
        "candidate_rows_classified": False,
        "ct_ladder_rung_assigned": False,
        "n27_closeout_ceiling": "N27-C2_transfer_schema_and_controls_frozen",
        "n27_closeout_ladder_rung_assigned": False,
        "ready_for_iteration_3": True,
        "notes": [
            "I2 is schema/control freeze only.",
            "N20 I5 is the normative transfer contract; N20 I4 is descriptor context.",
            "Same label, movement, proxy preservation, and support reconstruction are not transfer.",
        ],
    }
    checks = build_checks(output)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_transfer_schema_and_controls_frozen_no_positive_evidence"
        if output["status"] == "passed"
        else "blocked_transfer_schema_and_controls"
    )
    output["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in value
                for value in collect_strings(output)
                for marker in ABSOLUTE_PATH_MARKERS
            ),
            "all record paths are repository-relative",
        )
    )
    output["failed_checks"] = [item["check_id"] for item in output["checks"] if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_transfer_schema_and_controls_frozen_no_positive_evidence"
        if output["status"] == "passed"
        else "blocked_transfer_schema_and_controls"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 2 - Transfer Schema And Controls

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 2 freezes N27 schema and controls only. It opens no positive transfer
evidence, assigns no CT rung, and does not classify a transfer candidate.

## Source Precedence

```text
normative_contract_row = {output['source_precedence']['normative_contract_row']}
descriptor_context_row = {output['source_precedence']['descriptor_context_row']}
n20_i5_consumable_contract_is_normative = {str(output['source_precedence']['n20_i5_consumable_contract_is_normative']).lower()}
n20_i4_descriptor_is_context_only = {str(output['source_precedence']['n20_i4_descriptor_is_context_only']).lower()}
```

Deferred I4 descriptor fields cannot weaken transfer gates.

## Digest Pins

```text
source_inventory_output_digest = {output['source_digest_pins']['source_inventory_output_digest']}
descriptor_contract_row_digest = {output['source_digest_pins']['descriptor_contract_row_digest']}
consumable_contract_row_digest = {output['source_digest_pins']['consumable_contract_row_digest']}
n26_closeout_output_digest = {output['source_digest_pins']['n26_closeout_output_digest']}
```

## Frozen Ladders

| Ladder | Rungs |
| --- | --- |
| `CT` | `{', '.join(row['rung'] for row in output['ct_ladder'])}` |
| `N27-C` | `{', '.join(row['rung'] for row in output['n27_closeout_ladder'])}` |

## Transfer Core

Every positive row must record:

```text
{chr(10).join(output['transfer_core_schema']['required_fields'])}
```

Canonicalization:

```text
canonical_form = {output['transfer_core_schema']['canonicalization']['canonical_form']}
digest_field = {output['transfer_core_schema']['canonicalization']['digest_field']}
positive_rows_reference_core_by_digest = {str(output['transfer_core_schema']['canonicalization']['positive_rows_reference_core_by_digest']).lower()}
```

The transfer core fails closed for same-label-only, movement-only,
visual-similarity-only, proxy-score-only, hidden support reconstruction, or
support reconstruction counted as transfer.

## Scope Rules

Allowed scopes:

```text
{chr(10).join(output['transfer_scope_schema']['allowed_transfer_scopes'])}
```

Substrate transfer requires:

```text
{chr(10).join(output['transfer_scope_schema']['substrate_scope_requirements'])}
```

## Rung-Specific Artifact Roles

| CT rung | Required roles |
| --- | --- |
"""
    for rung, roles in output["artifact_role_schema"]["artifact_roles_by_ct_rung"].items():
        report += f"| `{rung}` | `{', '.join(roles)}` |\n"

    report += f"""

## Support Preservation Vs Reconstruction

```text
hidden_support_reconstruction_allowed = {str(output['support_reconstruction_schema']['hidden_support_reconstruction_allowed']).lower()}
reconstructed_support_must_not_be_counted_as = {output['support_reconstruction_schema']['reconstructed_support_must_not_be_counted_as']}
support_preservation_required_for_ct2_or_stronger = {str(output['support_reconstruction_schema']['support_preservation_required_for_ct2_or_stronger']).lower()}
```

## Threshold And Formula Records

Required formula fields:

```text
{chr(10).join(output['threshold_formula_schema']['required_formula_fields'])}
```

Required threshold fields:

```text
{chr(10).join(output['threshold_formula_schema']['required_threshold_fields'])}
```

## Replay And AP Gates

Required CT3 replay modes:

```text
{chr(10).join(output['replay_schema']['ct3_required_replay_modes'])}
```

AP dependency statuses:

```text
ap4 = {' | '.join(output['ap_dependency_schema']['ap4_dependency_status_enum'])}
ap5 = {' | '.join(output['ap_dependency_schema']['ap5_dependency_status_enum'])}
not_applicable_requires_reason = {str(output['ap_dependency_schema']['not_applicable_requires_reason']).lower()}
```

## Controls

Required control count: `{len(output['control_schema']['required_control_ids'])}`

```text
{chr(10).join(output['control_schema']['required_control_ids'])}
```

Positive-row control audit fields include:

```text
control_satisfied_for_positive_row
control_applicability_reason
```

## Claim Boundary

```text
positive_transfer_evidence_opened = {str(output['positive_transfer_evidence_opened']).lower()}
ct_ladder_rung_assigned = {str(output['ct_ladder_rung_assigned']).lower()}
n27_closeout_ceiling = {output['n27_closeout_ceiling']}
n26_consumed_as_transfer_evidence_allowed = {str(output['n26_context_schema']['n26_consumed_as_transfer_evidence_allowed']).lower()}
n25_2_direct_transfer_consumption_used_required_value = {str(output['n25_2_consumption_schema']['n25_2_direct_transfer_consumption_used_required_value']).lower()}
```

Blocked claims:

```text
{chr(10).join(output['claim_boundary']['blocked_claims'])}
```

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Interpretation

I2 makes N27 fail closed before positive probes. A later row cannot pass by
movement, same-label continuity, proxy preservation, N26 proxy/AP5 relabeling,
direct N25.2 backfill, hidden support reconstruction, support reconstruction
as preservation, or AP4/AP5 prose-only handling.

Output digest: `{output['output_digest']}`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
