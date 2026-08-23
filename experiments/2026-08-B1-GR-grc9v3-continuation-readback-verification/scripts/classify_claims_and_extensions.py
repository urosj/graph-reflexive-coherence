"""Generate the GRV8 scientific classification without closing GRV-C6."""

from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    artifact_envelope,
    assert_payload_digest,
    file_manifest,
    find_machine_local_path,
    git,
    read_json,
    semantic_digest,
    sha256_file,
    tracked_files,
    write_json,
)
from gate_receipts import (
    finalize_receipt,
    validate_acceptance_anchor,
    validate_receipt,
)
from route_contradictions_and_theory_reopening import (
    ALLOWED_CONTRADICTION_ROUTES,
    contradiction_entries,
    extension_decisions,
    superseded_exploratory_claims,
    theory_reopening_decision,
)


EXPERIMENT_RELATIVE = EXPERIMENT_ROOT.relative_to(REPO_ROOT).as_posix()
COMMAND = f".venv/bin/python {EXPERIMENT_RELATIVE}/scripts/run_all.py --gate GRV8"
IMPLEMENTATION_STATUSES = {
    "already_implemented_exactly",
    "implemented_as_declared_simplifying_limit",
    "implemented_only_analogically",
    "measurable_from_existing_state_but_not_constitutive",
    "absent_from_substrate",
    "theoretically_underdetermined_open",
}
CORRESPONDENCE_LEVELS = {
    "L0_analogy",
    "L1_representability",
    "L2_operational_signature",
    "L3_constitutive_realization",
    "L4_derived_reduced_limit",
    "L5_robust_realization",
}
CORRESPONDENCE_LEVEL_DEFINITIONS = {
    "L0_analogy": "The substrate contains a suggestive resemblance.",
    "L1_representability": "The substrate state can carry a correctly typed candidate object.",
    "L2_operational_signature": "Controlled evidence distinguishes the candidate from some rival mechanisms.",
    "L3_constitutive_realization": "Interventions establish the required causal factorization.",
    "L4_derived_reduced_limit": "A declared mathematical reduction connects the core and graph equations.",
    "L5_robust_realization": "The mapping survives parameter, relabeling, branch, and held-out stress within scope.",
}
ASSUMPTION_STATUSES = {
    "satisfied",
    "failed",
    "not_identifiable",
    "not_applicable",
    "deferred",
}
DECISION_ROUTES = {
    "unchanged_grc_interpretation",
    "analysis_only_measurement",
    "selectable_grc_extension",
    "lgrc_specific_investigation",
    "theory_revision_or_reopening",
    "blocked_by_identifiability",
}
REQUIRED_OBJECT_IDS = {
    "formed_zero_current_branches",
    "bounded_runtime_causal_state",
    "fixed_W_constrained_continuation_comparator",
    "complete_step_temporal_spectrum",
    "stable_neutral_unstable_temporal_subspaces",
    "post_activity_joint_state_persistence",
    "native_carrier_mediated_read_effect",
    "activity_conditioned_write_effect",
    "distinct_directional_read_current",
    "j_equals_J_C_limit",
    "current_magnitude_inscription",
    "historical_orientation_retention",
    "field_current_full_equivalence_hierarchy",
    "K_hybrid_node_tensor",
    "geometry_mobility_separation",
    "active_stationary_circulation",
    "recurrent_transport_orbits",
    "moving_retained_slow_bundle",
    "runtime_row_signed_Hessian_relation_to_continuation",
    "native_transport_conductance",
    "native_current_recurrence",
    "independent_current_temporal_state",
    "geometry_conditioned_baseline_transport",
    "frozen_W_carrier_conditioned_susceptibility",
    "durable_native_retained_carrier",
    "joint_state_mediated_later_response",
    "current_axis_or_channel_inscription",
    "present_current_directional_response",
    "cycle_space_orientation",
    "typed_graph_one_form_bridge",
    "active_joint_C_J_continuation",
}
SOURCE_IDS = {
    "SRC-CONTINUATION": "core/2026-08-TheContinuationSpectrum.md",
    "SRC-READBACK": "core/2026-08-ReadBack.md",
}


def scope_policy() -> dict[str, Any]:
    return read_json(EXPERIMENT_ROOT / "configs/grv8_scope_and_role_policy.json")


def source_id_map() -> dict[str, dict[str, str]]:
    manifest = envelope_payload("theory_source_manifest")
    records_by_path = {row["path"]: row for row in manifest["sources"]}
    if set(records_by_path) != set(SOURCE_IDS.values()):
        raise ValueError("theory source manifest does not match the GRV8 source IDs")
    return {
        source_id: {
            "path": relative,
            "sha256": records_by_path[relative]["sha256"],
            "git_blob": records_by_path[relative]["git_blob"],
            "source_role": records_by_path[relative]["source_role"],
        }
        for source_id, relative in sorted(SOURCE_IDS.items())
    }


def envelope_payload(name: str) -> dict[str, Any]:
    artifact = read_json(EXPERIMENT_ROOT / f"outputs/{name}.json")
    assert_payload_digest(artifact)
    return artifact["payload"]


def ids_in(value: str, prefix: str) -> list[str]:
    return sorted(
        set(re.findall(rf"(?<![A-Z0-9-]){prefix}-[A-Z0-9]+(?:-[A-Z0-9]+)*", value))
    )


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv7_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv7_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if anchor["acceptance_status"] != "accepted":
        raise ValueError("GRV7 is not scientifically accepted")
    if anchor["receipt_payload_sha256"] != receipt["receipt_payload_sha256"]:
        raise ValueError("GRV7 anchor does not bind the current result receipt")
    package = read_json(EXPERIMENT_ROOT / "configs/p8_manifest.json")
    if package["prerequisite"]["verification_closeout_rung"] != "GRV-C5":
        raise ValueError("GRV8 requires the explicit GRV-C5 prerequisite assignment")
    if package["prerequisite"]["grv8_authorized"] is not True:
        raise ValueError("GRV8 is not authorized by the P8 package")
    return receipt, anchor


def validate_accepted_chain() -> list[dict[str, Any]]:
    rows = []
    for index in range(8):
        receipt_path = EXPERIMENT_ROOT / f"outputs/gates/grv{index}_result_receipt.json"
        anchor_path = EXPERIMENT_ROOT / f"outputs/gates/grv{index}_acceptance_anchor.json"
        receipt = read_json(receipt_path)
        anchor = read_json(anchor_path)
        validate_receipt(receipt)
        validate_acceptance_anchor(anchor)
        if anchor["acceptance_status"] != "accepted":
            raise ValueError(f"GRV{index} acceptance status is not accepted")
        if anchor["receipt_payload_sha256"] != receipt["receipt_payload_sha256"]:
            raise ValueError(f"GRV{index} anchor/receipt mismatch")
        git("cat-file", "-e", f"{anchor['result_revision']}^{{commit}}")
        rows.append(
            {
                "gate_id": f"GRV{index}",
                "result_revision": anchor["result_revision"],
                "receipt_payload_sha256": receipt["receipt_payload_sha256"],
                "acceptance_anchor_path": anchor_path.relative_to(EXPERIMENT_ROOT).as_posix(),
                "acceptance_anchor_sha256": sha256_file(anchor_path),
                "acceptance_anchor_semantic_sha256": semantic_digest(anchor),
            }
        )
    return rows


def accepted_evidence_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for gate_index in range(8):
        gate_id = f"GRV{gate_index}"
        receipt_path = EXPERIMENT_ROOT / f"outputs/gates/grv{gate_index}_result_receipt.json"
        anchor_path = EXPERIMENT_ROOT / f"outputs/gates/grv{gate_index}_acceptance_anchor.json"
        receipt = read_json(receipt_path)
        anchor = read_json(anchor_path)
        validate_receipt(receipt)
        validate_acceptance_anchor(anchor)
        for relative, expected_sha256 in receipt["output_artifact_digests"].items():
            artifact_path = EXPERIMENT_ROOT / relative
            if sha256_file(artifact_path) != expected_sha256:
                raise ValueError(f"accepted evidence changed after {gate_id}: {relative}")
            if relative in index:
                raise ValueError(f"accepted artifact has multiple owning gates: {relative}")
            payload_sha256 = None
            if artifact_path.suffix == ".json":
                artifact = read_json(artifact_path)
                if "payload" in artifact and "payload_sha256" in artifact:
                    assert_payload_digest(artifact)
                    payload_sha256 = artifact["payload_sha256"]
            index[relative] = {
                "source_gate": gate_id,
                "result_revision": anchor["result_revision"],
                "acceptance_anchor_path": anchor_path.relative_to(EXPERIMENT_ROOT).as_posix(),
                "acceptance_anchor_sha256": sha256_file(anchor_path),
                "acceptance_anchor_semantic_sha256": semantic_digest(anchor),
                "artifact_path": relative,
                "artifact_sha256": expected_sha256,
                "artifact_payload_sha256": payload_sha256,
            }
    return index


def json_pointer_value(document: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {pointer}")
    current = document
    for raw_token in pointer.removeprefix("/").split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        else:
            current = current[token]
    return current


def bind_evidence(
    pointers: list[str], evidence_index: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    records = []
    for qualified_pointer in pointers:
        relative, separator, pointer = qualified_pointer.partition("#")
        if not separator or not pointer:
            raise ValueError(f"evidence pointer must bind an exact JSON field: {qualified_pointer}")
        if relative not in evidence_index:
            raise ValueError(f"evidence artifact is not bound by an accepted gate: {relative}")
        document = read_json(EXPERIMENT_ROOT / relative)
        value = json_pointer_value(document, pointer)
        records.append(
            {
                **evidence_index[relative],
                "exact_field_or_row": pointer,
                "consumed_value_semantic_sha256": semantic_digest(value),
            }
        )
    return records


def evidence_pointers_for_ids(
    policy: dict[str, Any],
    scope: dict[str, Any],
    *,
    claim_ids: list[str] | None = None,
    debt_ids: list[str] | None = None,
) -> list[str]:
    claims = set(claim_ids or [])
    debts = set(debt_ids or [])
    return sorted(
        {
            pointer
            for obj in policy["object_classifications"]
            if claims.intersection(obj["claim_ids"]) or debts.intersection(obj["debt_ids"])
            for pointer in scope["object_scope_policy"][obj["object_id"]][
                "evidence_pointers"
            ]
        }
    )


def resolved_object_scope(
    object_id: str, scope: dict[str, Any], evidence_index: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    object_policy = scope["object_scope_policy"][object_id]
    profile = scope["scope_profiles"][object_policy["profile_id"]]
    qualifiers = sorted(
        set(profile["secondary_qualifiers"] + object_policy.get("secondary_qualifiers", []))
    )
    return {
        "fixture_branch_envelope": object_policy.get(
            "fixture_branch_envelope", profile["fixture_branch_envelope"]
        ),
        "runtime_stage": object_policy.get("runtime_stage", profile["runtime_stage"]),
        "continuous_stratum": object_policy.get(
            "continuous_stratum", profile["continuous_stratum"]
        ),
        "secondary_qualifiers": qualifiers,
        "unknown_outside_envelope": "unknown_outside_envelope" in qualifiers,
        "accepted_evidence_records": bind_evidence(
            object_policy["evidence_pointers"], evidence_index
        ),
    }


def validate_policy(policy: dict[str, Any]) -> dict[str, Any]:
    assumption_source = envelope_payload("theory_assumption_registry")
    claim_source = envelope_payload("theory_claim_ledger")
    debt_source = envelope_payload("theory_debt_register")
    assumption_ids = {row["Assumption ID"] for row in assumption_source["records"]}
    claim_ids = {row["Claim ID"] for row in claim_source["records"]}
    debt_ids = {row["Debt ID"] for row in debt_source["records"]}
    if set(policy["assumption_statuses"]) != assumption_ids:
        raise ValueError("GRV8 policy must classify every and only source assumption")
    if any(row["status"] not in ASSUMPTION_STATUSES for row in policy["assumption_statuses"].values()):
        raise ValueError("invalid assumption status")
    grouped_claim_ids = [
        claim_id
        for group in policy["claim_disposition_groups"].values()
        for claim_id in group
    ]
    if set(grouped_claim_ids) != claim_ids or len(grouped_claim_ids) != len(claim_ids):
        raise ValueError("claim disposition groups must partition all source claims")
    object_rows = policy["object_classifications"]
    object_ids = {row["object_id"] for row in object_rows}
    if object_ids != REQUIRED_OBJECT_IDS or len(object_rows) != len(object_ids):
        raise ValueError("GRV8 object classification coverage mismatch")
    if {row["implementation_status"] for row in object_rows} != IMPLEMENTATION_STATUSES:
        raise ValueError("all six implementation statuses must be instantiated")
    if any(row["correspondence_level"] not in CORRESPONDENCE_LEVELS for row in object_rows):
        raise ValueError("invalid correspondence level")
    scope = scope_policy()
    if set(scope["object_scope_policy"]) != object_ids:
        raise ValueError("GRV8 scope policy must cover every and only classified object")
    if len({row["role_id"] for row in scope["causal_role_classifications"]}) != len(
        scope["causal_role_classifications"]
    ):
        raise ValueError("duplicate GRV8 causal-role classification")
    for object_id, object_scope in scope["object_scope_policy"].items():
        if object_scope["profile_id"] not in scope["scope_profiles"]:
            raise ValueError(f"unknown scope profile for {object_id}")
        if not object_scope["evidence_pointers"]:
            raise ValueError(f"missing exact evidence pointers for {object_id}")
    if set(policy["debt_routes"]) != debt_ids:
        raise ValueError("every theory debt must receive one primary route")
    if any(route not in DECISION_ROUTES for route in policy["debt_routes"].values()):
        raise ValueError("invalid debt route")
    for row in object_rows:
        if not set(row["claim_ids"]).issubset(claim_ids):
            raise ValueError(f"unknown claim in object {row['object_id']}")
        if not set(row["debt_ids"]).issubset(debt_ids):
            raise ValueError(f"unknown debt in object {row['object_id']}")
        for relative in row["evidence_refs"]:
            if not (EXPERIMENT_ROOT / relative).is_file():
                raise ValueError(f"missing evidence ref: {relative}")
    local_paths = find_machine_local_path(policy)
    if local_paths:
        raise ValueError(f"machine-local paths in GRV8 policy: {local_paths}")
    return {
        "assumption_source": assumption_source,
        "claim_source": claim_source,
        "debt_source": debt_source,
        "scope_policy": scope,
    }


def assumption_matrix(policy: dict[str, Any], claim_records: list[dict[str, Any]]) -> dict[str, Any]:
    affected: dict[str, list[str]] = {key: [] for key in policy["assumption_statuses"]}
    for claim in claim_records:
        for assumption_id in ids_in(claim["Required assumptions and limits"], "A"):
            affected[assumption_id].append(claim["Claim ID"])
    rows = []
    for assumption_id, decision in sorted(policy["assumption_statuses"].items()):
        rows.append(
            {
                "assumption_id": assumption_id,
                **decision,
                "affected_claim_ids": sorted(affected[assumption_id]),
                "maximum_supported_use": decision["scope"],
                "blocked_use": "outside_declared_scope_or_as_unrecorded_assumption",
            }
        )
    return {
        "gate_id": "GRV8",
        "source_id_map": source_id_map(),
        "rows": rows,
        "summary": dict(sorted(Counter(row["status"] for row in rows).items())),
        "highest_supported_claim": "bounded_assumption_status_assignment_for_unchanged_GRC9V3",
        "blocked_claims": ["assumption_status_is_global_theorem", "GRC_status_automatically_applies_to_LGRC"],
    }


def disposition_index(policy: dict[str, Any]) -> dict[str, str]:
    return {
        claim_id: disposition
        for disposition, claim_ids in policy["claim_disposition_groups"].items()
        for claim_id in claim_ids
    }


def claim_classification(
    policy: dict[str, Any],
    source_claims: list[dict[str, Any]],
    proof_note_ids: set[str],
    scope: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    dispositions = disposition_index(policy)
    assumption_decisions = policy["assumption_statuses"]
    object_rows = policy["object_classifications"]
    rows = []
    for source in source_claims:
        claim_id = source["Claim ID"]
        required = ids_in(source["Required assumptions and limits"], "A")
        statuses = {key: assumption_decisions[key]["status"] for key in required}
        disposition = dispositions[claim_id]
        if disposition == "bounded_supported_distinction" and any(
            status in {"failed", "not_identifiable"} for status in statuses.values()
        ):
            raise ValueError(f"positive claim {claim_id} has a failed/unidentifiable assumption")
        evidence_refs = sorted(
            {
                ref
                for obj in object_rows
                if claim_id in obj["claim_ids"]
                for ref in obj["evidence_refs"]
            }
        )
        if not evidence_refs:
            evidence_refs = ["outputs/theory_source_manifest.json"]
        evidence_pointers = sorted(
            {
                pointer
                for obj in object_rows
                if claim_id in obj["claim_ids"]
                for pointer in scope["object_scope_policy"][obj["object_id"]][
                    "evidence_pointers"
                ]
            }
        )
        object_correspondences = sorted(
            [
                {
                    "object_id": obj["object_id"],
                    "implementation_status": obj["implementation_status"],
                    "correspondence_level": obj["correspondence_level"],
                }
                for obj in object_rows
                if claim_id in obj["claim_ids"]
            ],
            key=lambda row: row["object_id"],
        )
        proof_id = f"PN-{claim_id.removeprefix('T-')}"
        rows.append(
            {
                "claim_id": claim_id,
                "statement": source["Statement"],
                "provenance": source["Provenance"],
                "disposition": disposition,
                "required_assumption_ids": required,
                "assumption_statuses": statuses,
                "evidence_refs": evidence_refs,
                "accepted_evidence_records": (
                    bind_evidence(evidence_pointers, evidence_index)
                    if evidence_pointers
                    else []
                ),
                "object_correspondences": object_correspondences,
                "classification_scope": "bounded_B1_GR_unchanged_GRC9V3_evidence_envelope",
                "source_ids": sorted(SOURCE_IDS),
                "proof_note_ids": [proof_id] if proof_id in proof_note_ids else [],
                "debt_ids": policy["claim_debt_map"].get(claim_id, []),
                "maximum_supported_claim": {
                    "bounded_supported_distinction": "source_backed_distinction_supported_within_the_bounded_GRC9V3_evidence_envelope",
                    "source_backed_boundary_not_runtime_admission": "source_backed_boundary_preserved_without_native_runtime_realization_claim",
                    "not_admitted_under_tested_assumptions": "theory_statement_retained_but_native_GRC9V3_claim_not_admitted",
                    "not_tested_fixed_topology_scope": "no_fixed_topology_GRC_result",
                    "theory_open_no_native_realization": "open_theory_role_with_no_native_GRC9V3_realization_identified",
                }[disposition],
                "blocked_claims": [
                    "unbounded_generalization",
                    "automatic_LGRC_inheritance",
                    "memory_learning_agency_or_life",
                ],
                "primary_decision_route": (
                    policy["debt_routes"][policy["claim_debt_map"][claim_id][0]]
                    if policy["claim_debt_map"].get(claim_id)
                    else "unchanged_grc_interpretation"
                ),
            }
        )
    return {
        "gate_id": "GRV8",
        "source_id_map": source_id_map(),
        "rows": rows,
        "summary": dict(sorted(Counter(row["disposition"] for row in rows).items())),
        "all_source_claim_ids_classified": True,
        "highest_supported_claim": "bounded_claim_by_claim_GRC9V3_realization_and_boundary_classification",
        "blocked_claims": ["full_core_Read_Back", "unique_retained_projector", "unified_spectrum"],
    }


def equivalence_classification(
    policy: dict[str, Any],
    claim_rows: list[dict[str, Any]],
    scope: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    assumption_by_claim = {
        row["claim_id"]: row["required_assumption_ids"] for row in claim_rows
    }
    proof_by_claim = {row["claim_id"]: row["proof_note_ids"] for row in claim_rows}
    rows = []
    for source in policy["object_classifications"]:
        scoped = resolved_object_scope(source["object_id"], scope, evidence_index)
        rows.append(
            {
                **source,
                "classification_scope": "bounded_B1_GR_unchanged_GRC9V3_evidence_envelope",
                **scoped,
                "assumption_ids": sorted(
                    {
                        assumption_id
                        for claim_id in source["claim_ids"]
                        for assumption_id in assumption_by_claim[claim_id]
                    }
                ),
                "proof_note_ids": sorted(
                    {
                        proof_id
                        for claim_id in source["claim_ids"]
                        for proof_id in proof_by_claim[claim_id]
                    }
                ),
                "source_ids": sorted(SOURCE_IDS),
                "primary_decision_route": (
                    policy["debt_routes"][source["debt_ids"][0]]
                    if source["debt_ids"]
                    else "unchanged_grc_interpretation"
                ),
            }
        )
    return {
        "gate_id": "GRV8",
        "source_id_map": source_id_map(),
        "implementation_status_enum": sorted(IMPLEMENTATION_STATUSES),
        "correspondence_level_enum": sorted(CORRESPONDENCE_LEVELS),
        "correspondence_level_definitions": CORRESPONDENCE_LEVEL_DEFINITIONS,
        "rows": rows,
        "summary": {
            "object_count": len(rows),
            "implementation_status_counts": dict(
                sorted(Counter(row["implementation_status"] for row in rows).items())
            ),
            "correspondence_level_counts": dict(
                sorted(Counter(row["correspondence_level"] for row in rows).items())
            ),
            "native_readback_supported": False,
            "native_writeback_supported": False,
            "closed_read_write_loop_supported": False,
            "geometry_mobility_extension_opened": False,
            "retained_carrier_extension_opened": False,
            "oriented_current_extension_selected": False,
            "K_decision": "remains_explicitly_diagnostic",
            "current_recurrence_classification": "exact_native_mechanism_distinct_from_core_readback",
            "j_equals_J_C_runtime_mapping": "analogy_only_candidate_mapping_rejected",
            "reduced_spatial_continuation_non_equivalence_supported": True,
            "reduced_structural_discrete_threshold_non_equivalence_supported": True,
            "runtime_spatial_vs_full_temporal_non_equivalence_supported": False,
            "full_map_non_equivalence_supported": False,
        },
        "highest_supported_claim": "evidence_grounded_unchanged_GRC9V3_correspondence_atlas_pending_human_review",
        "blocked_claims": [
            "full_core_Read_Back",
            "unique_retained_projector",
            "unified_alpha_gamma_beta_spectrum",
            "LGRC_retention_or_readback",
            "memory_learning_agency_organism_or_life",
        ],
    }


def final_causal_role_classification(
    scope: dict[str, Any], evidence_index: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    rows = []
    for source in scope["causal_role_classifications"]:
        rows.append(
            {
                **source,
                "classification_scope": "bounded_GRV5_synthetic_valid_formation_and_native_continuation_envelope",
                "accepted_evidence_records": bind_evidence(
                    source["evidence_pointers"], evidence_index
                ),
            }
        )
    return {
        "gate_id": "GRV8",
        "rows": rows,
        "summary": {
            "role_count": len(rows),
            "maximum_retention_ladder_rung": "GRR2",
            "native_mediation_supported": False,
            "native_readback_supported": False,
            "native_writeback_supported": False,
            "closed_loop_supported": False,
            "synthetic_input_provenance_preserved": True,
            "branch_relocation_rival_unresolved": True,
            "cross_gate_synthesis_creates_positive_arrow": False,
        },
        "highest_supported_claim": "arrow_by_arrow_GRR2_bounded_role_classification_without_partial_readback_relabel",
        "blocked_claims": [
            "partial_readback",
            "GRR3_or_stronger",
            "native_retained_carrier",
            "closed_read_write_loop",
        ],
    }


def final_debt_register(
    policy: dict[str, Any],
    source_debts: list[dict[str, Any]],
    scope: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    objects = policy["object_classifications"]
    rows = []
    for source in source_debts:
        debt_id = source["Debt ID"]
        evidence_refs = sorted(
            {
                ref
                for obj in objects
                if debt_id in obj["debt_ids"]
                for ref in obj["evidence_refs"]
            }
        )
        evidence_pointers = sorted(
            {
                pointer
                for obj in objects
                if debt_id in obj["debt_ids"]
                for pointer in scope["object_scope_policy"][obj["object_id"]][
                    "evidence_pointers"
                ]
            }
        )
        rows.append(
            {
                **source,
                "GRV8_status": "open_with_bounded_route",
                "GRV8_primary_route": policy["debt_routes"][debt_id],
                "evidence_refs": evidence_refs or ["outputs/theory_source_manifest.json"],
                "accepted_evidence_records": bind_evidence(
                    evidence_pointers, evidence_index
                ),
                "debt_closed": False,
            }
        )
    return {
        "gate_id": "GRV8",
        "rows": rows,
        "all_source_debt_ids_routed": True,
        "highest_supported_claim": "all_open_theory_and_realization_debts_have_one_primary_route",
        "blocked_claims": ["open_debt_is_extension_requirement", "open_debt_is_theory_falsification"],
    }


def completed_traceability(
    source_rows: list[dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    rows = []
    for index, source in enumerate(source_rows, start=1):
        combined = " ".join(str(value) for value in source.values())
        claim_ids = ids_in(combined, "T")
        debt_ids = ids_in(combined, "D")
        rows.append(
            {
                "traceability_row_id": f"TR-{index:02d}",
                "source_row": source,
                "claim_ids": claim_ids,
                "debt_ids": debt_ids,
                "assumption_statuses": {
                    assumption_id: policy["assumption_statuses"][assumption_id]["status"]
                    for claim_id in claim_ids
                    for assumption_id in claims[claim_id]["required_assumption_ids"]
                },
                "result_dispositions": {
                    claim_id: claims[claim_id]["disposition"] for claim_id in claim_ids
                },
                "primary_routes": sorted(
                    {policy["debt_routes"][debt_id] for debt_id in debt_ids}
                    or {"unchanged_grc_interpretation"}
                ),
                "evidence_refs": sorted(
                    {
                        ref
                        for claim_id in claim_ids
                        for ref in claims[claim_id]["evidence_refs"]
                    }
                ),
                "accepted_evidence_records": [
                    record
                    for claim_id in claim_ids
                    for record in claims[claim_id]["accepted_evidence_records"]
                ],
            }
        )
    return {
        "gate_id": "GRV8",
        "rows": rows,
        "results_pending": False,
        "highest_supported_claim": "completed_claim_assumption_result_and_route_traceability",
        "blocked_claims": ["traceability_row_is_independent_evidence"],
    }


def protected_manifest_v8() -> dict[str, Any]:
    predecessor = read_json(EXPERIMENT_ROOT / "outputs/protected_path_manifest_v7.json")
    assert_payload_digest(predecessor)
    expected_files = predecessor["payload"]["files"]
    current = file_manifest([row["path"] for row in expected_files])
    if current["files"] != expected_files:
        raise ValueError("GRV8 protected source/spec/root-test paths changed")
    payload = {
        **predecessor["payload"],
        "manifest_id": "b1_grv8_protected_paths_v8",
        "predecessor_path": f"{EXPERIMENT_RELATIVE}/outputs/protected_path_manifest_v7.json",
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "predecessor_tree_sha256": predecessor["payload"]["tree_sha256"],
        "unchanged_successor": True,
        "newly_discovered_load_bearing_paths": [],
    }
    return artifact_envelope(
        payload,
        schema_version="b1_grv8_protected_path_manifest_v8",
        generating_command=COMMAND,
    )


def run_existing_suite() -> tuple[dict[str, Any], Path]:
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]
    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path = EXPERIMENT_ROOT / "outputs/logs/grv8_existing_tests.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout, encoding="utf-8")
    match = re.search(r"Ran (\d+) tests", result.stdout)
    run_count = int(match.group(1)) if match else None
    passed = result.returncode == 0 and "\nOK" in result.stdout
    if not passed:
        raise RuntimeError("GRV8 complete existing-suite run failed")
    payload = {
        "command": "PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p test_*.py",
        "status": "passed",
        "tests_run": run_count,
        "failed_or_error": 0,
        "log_path": log_path.relative_to(EXPERIMENT_ROOT).as_posix(),
        "log_sha256": sha256_file(log_path),
        "highest_supported_claim": "protected_repository_suite_passes_at_GRV8_input_revision",
        "blocked_claims": ["test_pass_is_scientific_acceptance"],
    }
    return payload, log_path


def write_report(
    assumptions: dict[str, Any],
    claims: dict[str, Any],
    equivalence: dict[str, Any],
    causal_roles: dict[str, Any],
    contradictions: dict[str, Any],
    extensions: dict[str, Any],
    reopening: dict[str, Any],
    test_result: dict[str, Any],
    accepted_chain: list[dict[str, Any]],
) -> Path:
    report = EXPERIMENT_ROOT / "reports/b1_grc9v3_verification_report.md"
    lines = [
        "# B1-GR Verification Report",
        "",
        "## GRV8 Classification Result",
        "",
        "```text",
        "mechanical_status = passed",
        "scientific_acceptance = awaiting_human_review",
        "accepted_prerequisite_gate_count = 8",
        f"classified_assumption_count = {len(assumptions['rows'])}",
        f"classified_claim_count = {len(claims['rows'])}",
        f"classified_object_count = {len(equivalence['rows'])}",
        f"classified_causal_role_count = {len(causal_roles['rows'])}",
        f"contradiction_route_count = {len(contradictions['entries'])}",
        f"extension_decision_count = {len(extensions['decisions'])}",
        "theory_reopening_required = false",
        "GRV_C6_assigned = false",
        "B1_L_execution_authorized = false",
        "```",
        "",
        "GRV8 classifies the accepted unchanged-`GRC9V3` evidence. It does not",
        "retroactively upgrade reduced, synthetic, diagnostic, or blocked rows.",
        "The classification result must be accepted before the evidence bundle,",
        "evidence-grounded successor, LGRC handoff, or `GRV-C6` closeout can exist.",
        "This P8.1 result supersedes the unaccepted P8 candidate at revision",
        "`1448757`; it does not alter any accepted GRV0-GRV7 result.",
        "",
        "## Main Classification",
        "",
        "- Formed fixed-topology branches are exact bounded runtime results.",
        "- The synchronous causal closure is a bounded simplifying limit with `C`",
        "  independent and `W/J` reconstructed or stage-dependent.",
        "- Native current recurrence is an exact stage sequence: old `J` informs a",
        "  sign-even `J^2 -> W` write, then potential flow reconstructs current and",
        "  advances `C`. This is a real reflexive mechanism, not core Read-Back.",
        "- The `j = J_C` runtime mapping is rejected as a declared simplifying limit.",
        "  Reuse of one current variable does not satisfy the passive-null or",
        "  carrier-sensitive reduced read closure; the correspondence is analogical.",
        "- The fixed-`W` continuation construction and complete-step spectra are",
        "  analysis surfaces, not native retained-sector or Read-Back objects.",
        "- GRV5 supports only synthetic, `C`-dominated neutral persistence; native",
        "  transient-`W` mediation, Read-Back, write-back, and closure remain blocked.",
        "- GRV6 provides bounded negative short-period recurrence evidence without a",
        "  global orbit-nonexistence claim.",
        "- GRV7 supports reduced clamped-`W` non-equivalence, not runtime/full-map",
        "  non-equivalence or an informative nontrivial complete-step `+1` threshold.",
        "",
        "## Arrow-By-Arrow Causal Roles",
        "",
    ]
    for row in causal_roles["rows"]:
        lines.append(
            f"- `{row['role_id']}`: `{row['status']}`; ceiling `{row['maximum_supported_claim']}`."
        )
    lines.extend(
        [
        "",
        "The GRR2 persistence row remains synthetic-input, `C`-dominated, and",
        "compatible with branch relocation. It is not partial Read-Back, a durable",
        "native carrier, or later carrier mediation.",
        "",
        "## Extension And Theory Routes",
        "",
        ]
    )
    for row in extensions["decisions"]:
        lines.append(f"- `{row['decision_id']}`: `{row['route']}`.")
    lines.extend(
        [
            f"- Theory reopening: `{reopening['decision']['route']}`.",
            "",
            "`K` remains diagnostic. Geometry/mobility and retained-carrier",
            "extensions are not opened because their preregistered triggers were not",
            "met. GRR3-GRR5 constructibility under unchanged GRC remains unresolved",
            "and is routed to a revision-distinct witness search before extension",
            "selection. Current temporalization is conditionally selectable only for",
            "a target requiring independent current relaxation. Oriented current is",
            "conditionally selectable only for directional Read-Back or active",
            "circulation. B1-GR selects neither target.",
            "",
            "## Assumption And Contradiction Discipline",
            "",
            f"Assumption statuses: `{assumptions['summary']}`.",
            "A failed or unidentifiable required assumption cannot become a positive",
            "runtime claim. The native Read-Back passive null remains unidentifiable",
            "because no distinct native read operator was admitted. Fixed-topology",
            "transport is not applicable rather than silently generalized to LGRC.",
            "",
        ]
    )
    for row in contradictions["entries"]:
        lines.append(
            f"- `{row['contradiction_id']}` routes `{row['subject']}` to `{row['route']}`; theory contradiction = `{str(row['theory_contradicted']).lower()}`."
        )
    lines.extend(
        [
            "",
            "## Verification",
            "",
            f"- Complete existing suite: `{test_result['status']}` ({test_result['tests_run']} tests).",
            "- Protected source/spec/root-test tree: unchanged from GRV7.",
            f"- Accepted prerequisite gates: `{', '.join(row['gate_id'] for row in accepted_chain)}`.",
            "",
            "## LGRC Handoff Boundary Candidate",
            "",
            "B1-L over legacy GRC9V3 and a future LGRC-N over a revised GRC kernel",
            "are separate investigations. Neither is authorized by this unaccepted",
            "classification. Packet ledgers, queues, proper time, pulse surfaces,",
            "lineage, and producer-read history must not be relabeled as retained",
            "continuation, memory, relaxation spectrum, Read-Back, canonical mode",
            "transport, or native constitutive reading.",
            "",
            "## Claim Boundary",
            "",
            "The result does not establish full core Read-Back, a unique retained",
            "projector, a unified spectrum, active stationary circulation, native LGRC",
            "retention, memory, learning, agency, organism, or life. It does not select",
            "N32, L04, or substantive B1-L execution.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv8() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV8 requires a clean committed P8 input revision")
    receipt7, anchor7 = validate_prerequisite()
    accepted_chain = validate_accepted_chain()
    policy = read_json(EXPERIMENT_ROOT / "configs/grv8_classification_policy.json")
    source = validate_policy(policy)
    scope = source["scope_policy"]
    evidence_index = accepted_evidence_index()
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))

    proof_notes = envelope_payload("proof_note_registry")
    assumptions_payload = assumption_matrix(policy, source["claim_source"]["records"])
    claims_payload = claim_classification(
        policy,
        source["claim_source"]["records"],
        {row["proof_note_id"] for row in proof_notes["records"]},
        scope,
        evidence_index,
    )
    claims_by_id = {row["claim_id"]: row for row in claims_payload["rows"]}
    equivalence_payload = equivalence_classification(
        policy, claims_payload["rows"], scope, evidence_index
    )
    causal_roles_payload = final_causal_role_classification(scope, evidence_index)
    debts_payload = final_debt_register(
        policy, source["debt_source"]["records"], scope, evidence_index
    )
    traceability_source = envelope_payload("theory_test_traceability")
    traceability_payload = completed_traceability(
        traceability_source["records"], claims_by_id, policy
    )
    contradiction_rows = contradiction_entries()
    for row in contradiction_rows:
        row["accepted_evidence_records"] = bind_evidence(
            evidence_pointers_for_ids(
                policy, scope, claim_ids=row["claim_ids"]
            ),
            evidence_index,
        )
    contradictions_payload = {
        "gate_id": "GRV8",
        "allowed_routes": sorted(ALLOWED_CONTRADICTION_ROUTES),
        "entries": contradiction_rows,
        "theory_contradiction_count": 0,
        "highest_supported_claim": "all_material_mismatches_have_one_primary_non_theory_reopening_route",
        "blocked_claims": ["substrate_nonrealization_is_theory_falsification"],
    }
    extension_rows = extension_decisions(policy)
    for row in extension_rows:
        row["accepted_evidence_records"] = bind_evidence(
            evidence_pointers_for_ids(policy, scope, debt_ids=row["debt_ids"]),
            evidence_index,
        )
    extensions_payload = {
        "gate_id": "GRV8",
        "decisions": extension_rows,
        "lgrc_route_partition": scope["lgrc_route_partition"],
        "lgrc_boundary_candidate": scope["lgrc_boundary_candidate"],
        "forbidden_lgrc_relabels": scope["forbidden_lgrc_relabels"],
        "runtime_implementation_opened": False,
        "highest_supported_claim": "bounded_selectable_extension_routing_without_implementation",
        "blocked_claims": ["extension_selected_by_missing_symbol", "runtime_change_authorized"],
    }
    reopening_payload = {
        "gate_id": "GRV8",
        "decision": theory_reopening_decision(policy),
        "highest_supported_claim": "no_theory_reopening_required_after_bounded_routing",
        "blocked_claims": ["theory_globally_confirmed", "future_reopening_forbidden"],
    }
    superseded_payload = {
        "gate_id": "GRV8",
        "records": superseded_exploratory_claims(),
        "historical_artifacts_mutated": False,
        "highest_supported_claim": "exploratory_overclaims_superseded_by_accepted_bounded_results",
        "blocked_claims": ["history_deleted", "superseded_claim_remains_consumable"],
    }
    test_payload, test_log_path = run_existing_suite()
    protected = protected_manifest_v8()

    payloads = {
        "assumption_status_matrix.json": (assumptions_payload, "b1_grv8_assumption_status_matrix_v1"),
        "final_claim_classification.json": (claims_payload, "b1_grv8_final_claim_classification_v2"),
        "equivalence_classification.json": (equivalence_payload, "b1_grv8_equivalence_classification_v2"),
        "final_causal_role_classification.json": (causal_roles_payload, "b1_grv8_final_causal_role_classification_v1"),
        "final_theory_debt_register.json": (debts_payload, "b1_grv8_final_theory_debt_register_v2"),
        "final_theory_test_traceability.json": (traceability_payload, "b1_grv8_final_theory_test_traceability_v2"),
        "final_contradiction_routing.json": (contradictions_payload, "b1_grv8_final_contradiction_routing_v2"),
        "extension_decision.json": (extensions_payload, "b1_grv8_extension_decision_v2"),
        "theory_reopening_decision.json": (reopening_payload, "b1_grv8_theory_reopening_decision_v1"),
        "superseded_exploratory_claims.json": (superseded_payload, "b1_grv8_superseded_exploratory_claims_v2"),
        "grv8_existing_test_result.json": (test_payload, "b1_grv8_existing_test_result_v1"),
    }
    output_paths: list[Path] = []
    for name, (payload, schema_version) in payloads.items():
        path = EXPERIMENT_ROOT / "outputs" / name
        write_json(
            path,
            artifact_envelope(payload, schema_version=schema_version, generating_command=COMMAND),
        )
        output_paths.append(path)
    protected_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v8.json"
    write_json(protected_path, protected)
    output_paths.extend([protected_path, test_log_path])
    report_path = write_report(
        assumptions_payload,
        claims_payload,
        equivalence_payload,
        causal_roles_payload,
        contradictions_payload,
        extensions_payload,
        reopening_payload,
        test_payload,
        accepted_chain,
    )
    output_paths.append(report_path)

    receipt = finalize_receipt(
        {
            "gate_id": "GRV8",
            "input_execution_revision": input_revision,
            "substrate_base_revision": protected["payload"]["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [receipt7["receipt_payload_sha256"]],
            "prerequisite_acceptance_status": "accepted",
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV7",
                    "immutable_ref": "git:3d11154abbf4b84f5f3199b54ed83237a9fa7630",
                    "anchor_payload_sha256": semantic_digest(anchor7),
                }
            ],
            "accepted_gate_chain": accepted_chain,
            "superseded_unaccepted_result": {
                "result_revision": "144875709359d477c05ef7d47382bc76342223f5",
                "receipt_payload_sha256": "0f974b0bb44623494424f5ebc50a2cabbf5c48deba7de6998956c6ce6882c714",
                "acceptance_anchor_existed": False,
                "reason": "P8_1_object_envelope_role_and_provenance_hardening",
            },
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(output_paths)
            },
            "grv8_summary": {
                "assumption_count": len(assumptions_payload["rows"]),
                "claim_count": len(claims_payload["rows"]),
                "object_count": len(equivalence_payload["rows"]),
                "causal_role_count": len(causal_roles_payload["rows"]),
                "contradiction_route_count": len(contradictions_payload["entries"]),
                "extension_decision_count": len(extensions_payload["decisions"]),
                "theory_reopening_required": False,
                "existing_tests_run": test_payload["tests_run"],
                "protected_paths_unchanged": True,
                "classification_complete_candidate": True,
                "evidence_bundle_frozen": False,
                "successor_generated": False,
                "GRV_C6_assigned": False,
                "B1_L_execution_authorized": False,
                "unaccepted_P8_candidate_superseded": True,
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": ["GRV8_bundle_and_closeout", "B1-L"],
            "claim_ceiling": "bounded_unchanged_GRC9V3_classification_and_route_decision_pending_human_review_without_GRV_C6_or_LGRC_execution",
        }
    )
    validate_receipt(receipt)
    write_json(EXPERIMENT_ROOT / "outputs/gates/grv8_result_receipt.json", receipt)
    print("GRV8 classification mechanically validated; scientific acceptance is pending.")


def main() -> None:
    run_grv8()


if __name__ == "__main__":
    main()
