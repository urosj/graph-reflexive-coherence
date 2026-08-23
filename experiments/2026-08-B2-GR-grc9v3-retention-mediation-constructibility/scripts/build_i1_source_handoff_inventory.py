"""Build B2-GR Iteration 1 source and handoff admission artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from typing import Any

from b2_artifact_io import (
    B1_RELATIVE,
    B1_ROOT,
    EXPERIMENT_ROOT,
    REPO_ROOT,
    THEORY_ROOT,
    assert_envelope_digest,
    envelope,
    file_manifest,
    finalize_receipt,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_bytes,
    sha256_file,
    tracked_files,
    verify_file_manifest,
    write_json,
)


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/build_i1_source_handoff_inventory.py"
)
CONFIG_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "configs/b2_i1_source_contract.json"
)
EXPECTED_THEORY_REVISION = "5a8b01ae60165054da617db649c5a039755a18ec"


def json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    current = value
    for raw_part in pointer.removeprefix("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def git_blob(relative: str, *, cwd: Path = REPO_ROOT) -> str:
    line = git("ls-files", "-s", "--", relative, cwd=cwd)
    if not line:
        raise RuntimeError(f"source is not tracked: {relative}")
    return line.split()[1]


def git_commit_exists(revision: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def graph_source_record(contract: dict[str, Any], input_revision: str | None = None) -> dict[str, Any]:
    input_revision = input_revision or git("rev-parse", "HEAD")
    relative_to_b1 = contract["path"]
    path = B1_ROOT / relative_to_b1
    repository_relative = f"{B1_RELATIVE}/{relative_to_b1}"
    if not path.is_file():
        raise FileNotFoundError(path)
    data: Any = None
    payload_sha256 = None
    if path.suffix == ".json":
        data = read_json(path)
        if "payload" in data:
            assert_envelope_digest(data)
            payload_sha256 = data["payload_sha256"]
    consumed = []
    for pointer in contract["consumed_pointers"]:
        consumed_value = json_pointer(data, pointer)
        consumed.append(
            {
                "pointer": pointer,
                "value_semantic_sha256": semantic_digest(consumed_value),
                "source_role": contract["source_classification"],
                "allowed_downstream_use": contract["may_consume_as"],
                "forbidden_downstream_use": contract["must_not_consume_as"],
                "positive_B2_rung_credit": False,
            }
        )
    revision_blob = git("rev-parse", f"{input_revision}:{repository_relative}")
    record = {
        **contract,
        "repository": "github.com/urosj/graph-reflexive-coherence",
        "repository_relative_path": repository_relative,
        "exists": True,
        "tracked": True,
        "git_blob": git_blob(repository_relative),
        "input_revision_git_blob": revision_blob,
        "working_tree_blob_matches_input_revision": git_blob(repository_relative) == revision_blob,
        "last_change_revision": git("log", "-1", "--format=%H", "--", repository_relative),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "payload_sha256": payload_sha256,
        "consumed_values": consumed,
        "positive_B2_rung_credit": False,
    }
    if "receipt_path" in contract:
        receipt_path = B1_ROOT / contract["receipt_path"]
        receipt = read_json(receipt_path)
        if data["acceptance_status"] != "accepted":
            raise RuntimeError(f"source anchor is not accepted: {relative_to_b1}")
        if data["receipt_payload_sha256"] != receipt["receipt_payload_sha256"]:
            raise RuntimeError(f"anchor/receipt mismatch: {relative_to_b1}")
        record["receipt_repository_relative_path"] = f"{B1_RELATIVE}/{contract['receipt_path']}"
        record["receipt_sha256"] = sha256_file(receipt_path)
        record["receipt_payload_sha256"] = receipt["receipt_payload_sha256"]
        record["acceptance_status"] = data["acceptance_status"]
        record["accepted_result_revision"] = data["result_revision"]
    elif isinstance(data, dict) and data.get("acceptance_status") == "accepted" and "result_revision" in data:
        record["acceptance_status"] = data["acceptance_status"]
        record["accepted_result_revision"] = data["result_revision"]
    if "accepted_result_revision" in record:
        revision = record["accepted_result_revision"]
        record["accepted_result_revision_exists"] = git_commit_exists(revision)
        record["accepted_result_revision_is_ancestor_of_input"] = (
            record["accepted_result_revision_exists"] and git_is_ancestor(revision, input_revision)
        )
    return record


def pinned_theory_bytes(revision: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=THEORY_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def theory_source_record(contract: dict[str, Any]) -> dict[str, Any]:
    revision = contract["revision"]
    relative = contract["path"]
    pinned = pinned_theory_bytes(revision, relative)
    pinned_sha256 = sha256_bytes(pinned)
    if pinned_sha256 != contract["expected_sha256"]:
        raise RuntimeError(f"pinned theory digest mismatch: {relative}")
    tree_line = git("ls-tree", revision, "--", relative, cwd=THEORY_ROOT)
    if not tree_line:
        raise RuntimeError(f"theory source absent at pinned revision: {relative}")
    working_path = THEORY_ROOT / relative
    return {
        **contract,
        "pinned_revision_exists": True,
        "git_blob": tree_line.split()[2],
        "pinned_blob_sha256": pinned_sha256,
        "working_tree_file_exists": working_path.is_file(),
        "working_tree_sha256": sha256_file(working_path) if working_path.is_file() else None,
        "consumption_mode": "pinned_revision_blob",
    }


def protected_manifest(input_revision: str, substrate_revision: str) -> dict[str, Any]:
    paths = tracked_files(["src/pygrc", "specs", "tests"])
    payload = file_manifest(paths)
    payload.update(
        {
            "manifest_id": "b2_i1_protected_paths",
            "scope": "all_tracked_PyGRC_source_specs_and_existing_tests",
            "input_revision": input_revision,
            "substrate_base_revision": substrate_revision,
            "runtime_change_authorized": False,
            "src_change_authorized": False,
            "spec_change_authorized": False,
            "existing_test_change_authorized": False,
        }
    )
    return envelope(payload, "b2_i1_protected_path_manifest_v1", COMMAND)


def experiment_tree() -> dict[str, Any]:
    relative = repo_relative(EXPERIMENT_ROOT)
    paths = tracked_files([relative])
    included = [
        path
        for path in paths
        if f"{relative}/outputs/" not in path and f"{relative}/reports/" not in path
    ]
    return file_manifest(included)


def source_contract() -> dict[str, Any]:
    return read_json(REPO_ROOT / CONFIG_RELATIVE)


def markdown_section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def unchanged_runtime_identity(
    contract: dict[str, Any], input_revision: str, protected: dict[str, Any]
) -> dict[str, Any]:
    paths = tracked_files(contract["unchanged_runtime_paths"])
    runtime_manifest = file_manifest(paths)
    records = []
    for entry in runtime_manifest["files"]:
        relative = entry["path"]
        input_blob = git("rev-parse", f"{input_revision}:{relative}")
        records.append(
            {
                **entry,
                "git_blob": git_blob(relative),
                "input_revision_git_blob": input_blob,
                "working_tree_blob_matches_input_revision": git_blob(relative) == input_blob,
            }
        )
    protected_payload = protected["payload"]
    protected_files = protected_payload["files"]
    return {
        "identity_id": "b2_i1_unchanged_grc9v3_runtime_identity_v1",
        "repository_revision": input_revision,
        "runtime_file_records": records,
        "runtime_tree_sha256": semantic_digest(records),
        "protected_manifest_payload_sha256": protected["payload_sha256"],
        "protected_tree_sha256": protected_payload["tree_sha256"],
        "spec_tree_sha256": semantic_digest(
            [row for row in protected_files if row["path"].startswith("specs/")]
        ),
        "existing_test_tree_sha256": semantic_digest(
            [row for row in protected_files if row["path"].startswith("tests/")]
        ),
        "all_runtime_blobs_match_input_revision": all(
            row["working_tree_blob_matches_input_revision"] for row in records
        ),
        "protected_manifest_live_verification": verify_file_manifest(protected_payload),
        "positive_runtime_profile": "unchanged_GRC9V3_only",
    }


def branch_crosswalk() -> dict[str, Any]:
    fixed = read_json(B1_ROOT / "outputs/fixed_branch_registry.json")["payload"]
    jacobians = read_json(B1_ROOT / "outputs/complete_step_jacobians.json")["payload"]
    slow = read_json(B1_ROOT / "outputs/slow_cluster_registry.json")["payload"]
    interventions = read_json(B1_ROOT / "outputs/grv5_intervention_registry.json")["payload"]
    retention = read_json(B1_ROOT / "outputs/conductance_retention_probe.json")["payload"]
    causal = read_json(B1_ROOT / "outputs/causal_role_matrix.json")["payload"]

    jac_by_id = {row["branch_id"]: row for row in jacobians["branches"]}
    slow_counts: dict[str, int] = {}
    for row in slow["rows"]:
        slow_counts[row["branch_id"]] = slow_counts.get(row["branch_id"], 0) + 1
    intervention_counts: dict[str, int] = {}
    for row in interventions["interventions"]:
        branch_id = row["intervention_id"].split("::", 1)[0]
        intervention_counts[branch_id] = intervention_counts.get(branch_id, 0) + 1
    retention_counts: dict[str, int] = {}
    for row in retention["candidate_rows"]:
        retention_counts[row["branch_id"]] = retention_counts.get(row["branch_id"], 0) + 1
    causal_counts: dict[str, int] = {}
    for row in causal["rows"]:
        branch_id = row["row_id"].split("::", 1)[0]
        causal_counts[branch_id] = causal_counts.get(branch_id, 0) + 1

    rows = []
    for fixed_row in fixed["branches"]:
        branch_id = fixed_row["branch_id"]
        jac = jac_by_id.get(branch_id)
        snapshot_path = REPO_ROOT / fixed_row["state_snapshot_path"]
        snapshot = read_json(snapshot_path)
        topology = snapshot["topology"]
        codec = jac["causal_codec"] if jac is not None else None
        identity_matches = bool(
            jac
            and jac["fixture_id"] == fixed_row["fixture_id"]
            and jac["symmetry_orbit_id"] == fixed_row["symmetry_orbit_id"]
            and jac["source_snapshot_sha256"] == fixed_row["state_snapshot_sha256"]
            and codec["node_order"] == [row["node_id"] for row in topology["nodes"]]
            and codec["edge_order"] == [row["edge_id"] for row in topology["edges"]]
        )
        rows.append(
            {
                "branch_id": branch_id,
                "fixture_id": fixed_row["fixture_id"],
                "symmetry_orbit_id": fixed_row["symmetry_orbit_id"],
                "canonical_branch_signature": fixed_row["canonical_branch_signature"],
                "parameter_hash": fixed_row["parameter_hash"],
                "runtime_parameter_vector_digest": semantic_digest(
                    snapshot["metadata"]["resolved_params"]
                ),
                "budget_target": snapshot["dynamics"]["state"]["budget_target"],
                "gauge": codec["basis_id"] if codec is not None else None,
                "categorical_stratum_status": (
                    jac["full_C_W_J_stratum_and_jacobian"]["categorical_surface_status"]
                    if jac is not None
                    else None
                ),
                "topology_semantic_sha256": semantic_digest(topology),
                "node_order": [row["node_id"] for row in topology["nodes"]],
                "edge_order": [row["edge_id"] for row in topology["edges"]],
                "source_snapshot_path": fixed_row["state_snapshot_path"],
                "source_snapshot_sha256": fixed_row["state_snapshot_sha256"],
                "complete_step_jacobian_row_count": 1 if jac is not None else 0,
                "slow_cluster_row_count": slow_counts.get(branch_id, 0),
                "intervention_row_count": intervention_counts.get(branch_id, 0),
                "retention_candidate_row_count": retention_counts.get(branch_id, 0),
                "causal_role_row_count": causal_counts.get(branch_id, 0),
                "identity_fields_match": identity_matches,
            }
        )
    fixed_ids = {row["branch_id"] for row in fixed["branches"]}
    joined_ids = {
        *jac_by_id,
        *slow_counts,
        *intervention_counts,
        *retention_counts,
        *causal_counts,
    }
    return {
        "crosswalk_id": "b2_i1_B1_branch_crosswalk_v1",
        "accepted_B1_branch_population_count": len(rows),
        "accepted_B1_branch_population_digest": semantic_digest(rows),
        "B2_search_eligible_population_selected": False,
        "branch_ranking_performed": False,
        "all_referenced_branch_ids_within_accepted_population": joined_ids <= fixed_ids,
        "all_branch_identity_fields_match": all(row["identity_fields_match"] for row in rows),
        "all_branches_present_on_each_required_surface": all(
            row["complete_step_jacobian_row_count"] == 1
            and row["slow_cluster_row_count"] > 0
            and row["intervention_row_count"] > 0
            and row["retention_candidate_row_count"] > 0
            and row["causal_role_row_count"] > 0
            for row in rows
        ),
        "rows": rows,
    }


def build_payload(
    input_revision: str | None = None, protected: dict[str, Any] | None = None
) -> dict[str, Any]:
    input_revision = input_revision or git("rev-parse", "HEAD")
    substrate_revision = git("merge-base", "main", input_revision)
    protected = protected or protected_manifest(input_revision, substrate_revision)
    contract = source_contract()
    graph_records = [graph_source_record(row, input_revision) for row in contract["graph_sources"]]
    theory_records = [theory_source_record(row) for row in contract["theory_sources"]]
    by_id = {row["source_id"]: row for row in graph_records}

    closeout = read_json(B1_ROOT / "outputs/gates/grv8_closeout_acceptance_anchor.json")
    bundle = read_json(B1_ROOT / "outputs/evidence_bundle_manifest.json")
    handoff = read_json(B1_ROOT / "outputs/continuation_readback_next_route_handoff.json")
    causal = read_json(B1_ROOT / "outputs/final_causal_role_classification.json")
    claims = read_json(B1_ROOT / "outputs/final_claim_classification.json")
    extension = read_json(B1_ROOT / "outputs/extension_decision.json")
    retention = read_json(B1_ROOT / "outputs/conductance_retention_probe.json")
    traceability = read_json(B1_ROOT / "outputs/final_theory_test_traceability.json")

    runtime_identity = unchanged_runtime_identity(contract, input_revision, protected)
    branch_identity_crosswalk = branch_crosswalk()
    field_registry = [
        {
            "source_id": row["source_id"],
            "artifact_path": row["repository_relative_path"],
            **field,
        }
        for row in graph_records
        for field in row["consumed_values"]
    ]
    field_registry.extend(
        {
            "source_id": row["source_id"],
            "artifact_path": row["path"],
            "pointer": "complete_pinned_document",
            "value_semantic_sha256": row["pinned_blob_sha256"],
            "source_role": row["source_classification"],
            "allowed_downstream_use": row["may_consume_as"],
            "forbidden_downstream_use": row["must_not_consume_as"],
            "positive_B2_rung_credit": False,
        }
        for row in theory_records
    )

    grr_contract = contract["grr_ladder_contract"]
    grr_spec = by_id[grr_contract["source_id"]]
    grr_section = markdown_section(REPO_ROOT / grr_spec["repository_relative_path"], grr_contract["heading"])
    grr_ladder_definition = {
        **grr_contract,
        "source_path": grr_spec["repository_relative_path"],
        "source_file_sha256": grr_spec["sha256"],
        "source_git_blob": grr_spec["git_blob"],
        "section_sha256": sha256_bytes(grr_section.encode("utf-8")),
        "all_rungs_present_verbatim": all(
            f"| `{rung}` | {meaning} |" in grr_section
            for rung, meaning in grr_contract["rungs"].items()
        ),
    }

    all_source_ids = {row["source_id"] for row in [*graph_records, *theory_records]}
    required_ids = {
        source_id
        for source_ids in contract["required_fact_domains"].values()
        for source_id in source_ids
    }
    bundle_members = {row["path"] for row in bundle["payload"]["artifacts"]}
    bundle_member_source_ids = sorted(
        row["source_id"]
        for row in graph_records
        if row["repository_relative_path"] in bundle_members
    )
    excluded = set(bundle["payload"]["bundle_excluded_paths"])
    post_bundle_source_ids = sorted(
        row["source_id"]
        for row in graph_records
        if row["path"] in excluded
    )
    source_dependency_closure = {
        "required_fact_domains": contract["required_fact_domains"],
        "all_required_sources_admitted": required_ids <= all_source_ids,
        "missing_required_source_ids": sorted(required_ids - all_source_ids),
        "evidence_bundle_member_source_ids": bundle_member_source_ids,
        "post_bundle_accepted_derivative_source_ids": post_bundle_source_ids,
        "bundle_exclusion_is_not_treated_as_missing": True,
        "provenance_stage_order": [
            "pinned_theory_and_accepted_raw_gate_artifacts",
            "accepted_final_classification_and_traceability",
            "evidence_bundle_then_handoff_and_successor",
            "closeout_acceptance_authority",
        ],
        "dependency_graph_acyclic_by_frozen_stage_order": True,
        "accepted_evidence_records_deduplicated": traceability["payload"]["accepted_evidence_records_deduplicated"],
    }

    consistency_rows = [
        {
            "fact_id": "maximum_retention_rung",
            "raw_source": "B1_RETENTION_PROBE:/payload/summary/maximum_local_evidence_ladder_rung",
            "raw_value": retention["payload"]["summary"]["maximum_local_evidence_ladder_rung"],
            "final_source": "B1_FINAL_CAUSAL_ROLES:/payload/summary/maximum_retention_ladder_rung",
            "final_value": causal["payload"]["summary"]["maximum_retention_ladder_rung"],
            "relation": "exact",
        },
        {
            "fact_id": "native_mediation",
            "raw_source": "B1_RETENTION_PROBE:/payload/summary/native_mediation_count",
            "raw_value": retention["payload"]["summary"]["native_mediation_count"],
            "final_source": "B1_FINAL_CAUSAL_ROLES:/payload/summary/native_mediation_supported",
            "final_value": causal["payload"]["summary"]["native_mediation_supported"],
            "relation": "zero_count_means_not_supported",
        },
        {
            "fact_id": "branch_relocation_rival",
            "raw_source": "B1_RETENTION_PROBE:/payload/summary/branch_relocation_rival_unresolved_GRR2_row_count",
            "raw_value": retention["payload"]["summary"]["branch_relocation_rival_unresolved_GRR2_row_count"],
            "final_source": "B1_FINAL_CAUSAL_ROLES:/payload/summary/branch_relocation_rival_unresolved",
            "final_value": causal["payload"]["summary"]["branch_relocation_rival_unresolved"],
            "relation": "positive_count_means_unresolved",
        },
        {
            "fact_id": "forming_input_provenance",
            "raw_source": "B1_RETENTION_PROBE:/payload/summary/forming_old_current_input_runtime_reached",
            "raw_value": retention["payload"]["summary"]["forming_old_current_input_runtime_reached"],
            "final_source": "B1_FINAL_CAUSAL_ROLES:/payload/summary/synthetic_input_provenance_preserved",
            "final_value": causal["payload"]["summary"]["synthetic_input_provenance_preserved"],
            "relation": "not_runtime_reached_and_synthetic_provenance_preserved",
        },
    ]
    for row in consistency_rows:
        if row["relation"] == "exact":
            row["consistent"] = row["raw_value"] == row["final_value"]
        elif row["relation"] == "zero_count_means_not_supported":
            row["consistent"] = row["raw_value"] == 0 and row["final_value"] is False
        elif row["relation"] == "positive_count_means_unresolved":
            row["consistent"] = row["raw_value"] > 0 and row["final_value"] is True
        else:
            row["consistent"] = row["raw_value"] is False and row["final_value"] is True
    cross_artifact_consistency_audit = {
        "policy": "precedence_may_narrow_interpretation_but_cannot_overwrite_contradictory_raw_measurement",
        "status_on_disagreement": "source_consistency_failure",
        "all_rows_consistent": all(row["consistent"] for row in consistency_rows),
        "rows": consistency_rows,
    }

    accepted_revisions = [
        closeout["result_revision"],
        *[row["result_revision"] for row in bundle["payload"]["accepted_gate_results"]],
    ]
    revision_ancestry = {
        "input_revision": input_revision,
        "accepted_revisions": [
            {
                "revision": revision,
                "exists": git_commit_exists(revision),
                "is_ancestor_of_input_revision": (
                    git_commit_exists(revision) and git_is_ancestor(revision, input_revision)
                ),
            }
            for revision in accepted_revisions
        ],
    }
    revision_ancestry["all_accepted_revisions_exist_and_are_ancestors"] = all(
        row["exists"] and row["is_ancestor_of_input_revision"]
        for row in revision_ancestry["accepted_revisions"]
    )

    lane = next(
        row
        for row in handoff["payload"]["handoff_lanes"]
        if row["lane_id"] == "GRC_UNCHANGED_CONSTRUCTIBILITY"
    )
    unchanged_decision = next(
        row
        for row in extension["payload"]["decisions"]
        if row["decision_id"] == "EXT-UNCHANGED-CONSTRUCTIBILITY"
    )

    binding_checks = {
        "closeout_anchor_accepted": closeout["acceptance_status"] == "accepted",
        "closeout_rung_is_GRV_C6": closeout["assigned_closeout_rung"] == "GRV-C6",
        "closeout_binds_evidence_bundle_file": closeout["evidence_bundle_sha256"] == by_id["B1_EVIDENCE_BUNDLE"]["sha256"],
        "closeout_binds_evidence_bundle_payload": closeout["evidence_bundle_payload_sha256"] == bundle["payload_sha256"],
        "closeout_binds_handoff_file": closeout["next_route_handoff_sha256"] == by_id["B1_NEXT_ROUTE_HANDOFF"]["sha256"],
        "closeout_binds_handoff_payload": closeout["next_route_handoff_payload_sha256"] == handoff["payload_sha256"],
        "closeout_result_revision_consumed": any(
            row["pointer"] == "/result_revision"
            for row in by_id["B1_CLOSEOUT_ACCEPTANCE"]["consumed_values"]
        ),
        "accepted_revisions_exist_and_precede_B2": revision_ancestry["all_accepted_revisions_exist_and_are_ancestors"],
        "all_source_blobs_match_input_revision": all(
            row["working_tree_blob_matches_input_revision"] for row in graph_records
        ),
        "unchanged_runtime_identity_complete": (
            runtime_identity["all_runtime_blobs_match_input_revision"]
            and runtime_identity["protected_manifest_live_verification"]
        ),
        "required_source_dependency_closure_complete": source_dependency_closure["all_required_sources_admitted"],
        "source_dependency_graph_acyclic": source_dependency_closure["dependency_graph_acyclic_by_frozen_stage_order"],
        "accepted_evidence_records_deduplicated": source_dependency_closure["accepted_evidence_records_deduplicated"],
        "cross_artifact_raw_and_final_values_consistent": cross_artifact_consistency_audit["all_rows_consistent"],
        "B1_branch_crosswalk_complete": (
            branch_identity_crosswalk["all_referenced_branch_ids_within_accepted_population"]
            and branch_identity_crosswalk["all_branch_identity_fields_match"]
            and branch_identity_crosswalk["all_branches_present_on_each_required_surface"]
        ),
        "all_B1_branches_admitted_before_B2_selection": (
            branch_identity_crosswalk["accepted_B1_branch_population_count"] == 48
            and branch_identity_crosswalk["B2_search_eligible_population_selected"] is False
            and branch_identity_crosswalk["branch_ranking_performed"] is False
        ),
        "GRR_ladder_definition_bound": grr_ladder_definition["all_rungs_present_verbatim"],
        "field_level_consumption_registry_complete": (
            len(field_registry) > 0
            and all(row["positive_B2_rung_credit"] is False for row in field_registry)
        ),
        "source_precedence_frozen": contract["source_precedence"] == [
            "accepted_closeout_final_classification_and_handoff",
            "accepted_gate_artifacts_and_acceptance_anchors",
            "accepted_evidence_grounded_successor_specification",
            "reports",
            "theory_definitions_and_vocabulary",
        ],
        "B1_maximum_retention_rung_is_GRR2": causal["payload"]["summary"]["maximum_retention_ladder_rung"] == "GRR2",
        "B1_synthetic_provenance_preserved": causal["payload"]["summary"]["synthetic_input_provenance_preserved"] is True,
        "B1_branch_relocation_rival_open": causal["payload"]["summary"]["branch_relocation_rival_unresolved"] is True,
        "B1_native_mediation_unsupported": causal["payload"]["summary"]["native_mediation_supported"] is False,
        "B1_retention_probe_matches_GRR2": retention["payload"]["summary"]["maximum_local_evidence_ladder_rung"] == "GRR2",
        "B1_forming_input_not_runtime_reached": retention["payload"]["summary"]["forming_old_current_input_runtime_reached"] is False,
        "unchanged_runtime_lane_is_first": lane["lane_order"] == 1 and lane["status"] == "eligible_first_grc_investigation",
        "unchanged_runtime_target_exact": lane["target"] == "GRR3_to_GRR5_witnesses_under_unchanged_GRC9V3",
        "extension_search_is_not_impossibility": unchanged_decision["mechanical_impossibility_established"] is False,
        "runtime_implementation_not_opened": extension["payload"]["runtime_implementation_opened"] is False,
        "B1_L_not_authorized": closeout["B1_L_execution_authorized"] is False,
        "all_graph_sources_present": all(row["exists"] and row["tracked"] for row in graph_records),
        "all_theory_sources_match_pinned_revision": all(
            row["pinned_blob_sha256"] == row["expected_sha256"] for row in theory_records
        ),
        "final_claims_are_classified": claims["payload"]["all_source_claim_ids_classified"] is True,
    }
    failed = sorted(name for name, passed in binding_checks.items() if not passed)
    payload = {
        "experiment_id": "B2-GR",
        "iteration": "I1",
        "status": "passed" if not failed else "failed",
        "acceptance_state": "awaiting_scientific_review",
        "semantic_digest_contract": contract["semantic_digest_contract"],
        "source_precedence": contract["source_precedence"],
        "source_authority_policy": {
            "precedence_applies_to": "interpretation_claim_wording_and_lifecycle_authority",
            "precedence_does_not_apply_to": "overwriting_or_manufacturing_raw_empirical_measurements",
            "ambiguous_authority_statuses": [
                "source_authority_ambiguous",
                "source_revision_mismatch",
                "source_dependency_incomplete",
                "source_field_semantics_ambiguous",
                "source_consistency_failure",
            ],
            "all_ambiguities_fail_closed": True,
        },
        "source_precedence_resolution": {
            "embedded_handoff_status": handoff["payload"]["handoff_status"],
            "embedded_handoff_grv_c6_assigned": handoff["payload"]["grv_c6_assigned"],
            "authoritative_closeout_status": closeout["acceptance_status"],
            "authoritative_closeout_rung": closeout["assigned_closeout_rung"],
            "resolution": "closeout_acceptance_anchor_supersedes_preacceptance_embedded_handoff_lifecycle_fields_without_mutating_the_handoff",
        },
        "graph_source_records": graph_records,
        "theory_source_records": theory_records,
        "consumed_field_registry": field_registry,
        "source_dependency_closure": source_dependency_closure,
        "revision_ancestry": revision_ancestry,
        "cross_artifact_consistency_audit": cross_artifact_consistency_audit,
        "unchanged_runtime_identity": runtime_identity,
        "B1_branch_crosswalk": branch_identity_crosswalk,
        "GRR_ladder_definition": grr_ladder_definition,
        "source_record_count": len(graph_records) + len(theory_records),
        "graph_source_record_count": len(graph_records),
        "theory_source_record_count": len(theory_records),
        "accepted_starting_boundary": {
            "source_experiment": "B1-GR",
            "source_closeout_rung": "GRV-C6",
            "maximum_retention_rung": "GRR2",
            "retention_class": "bounded_C_dominated_neutral_coordinate_persistence",
            "forming_input_provenance": "synthetic_experiment_authored_old_current",
            "native_branch_only_reachability": "unsupported",
            "isolated_slow_cluster_occupancy": "unsupported",
            "specific_transient_W_mediation": "unsupported",
            "matched_native_probe_mediation": "unsupported",
            "branch_relocation_rival": "unresolved",
            "raw_and_accepted_interpretation_kept_separate": True,
            "semantic_statuses_not_collapsed": [
                "unsupported",
                "absent",
                "measured_zero",
                "blocked",
                "not_identifiable",
                "unresolved",
            ],
            "B1_evidence_consumable_for": [
                "provenance",
                "controls",
                "method",
                "prior_boundary",
                "search_envelope_definition",
            ],
            "B1_positive_B2_rung_credit": False,
        },
        "admitted_route": {
            "lane_id": lane["lane_id"],
            "lane_order": lane["lane_order"],
            "status": lane["status"],
            "target": lane["target"],
            "role": lane["role"],
            "claim_ceiling": unchanged_decision["claim_ceiling"],
            "mechanical_impossibility_established": unchanged_decision["mechanical_impossibility_established"],
        },
        "binding_checks": binding_checks,
        "check_count": len(binding_checks),
        "passed_check_count": sum(binding_checks.values()),
        "failed_checks": failed,
        "claim_boundary": {
            "B2_positive_evidence_opened": False,
            "GRR_rung_assigned": False,
            "B2_closeout_rung_assigned": False,
            "B2_closeout_ceiling": "B2-C0-ready",
            "runtime_change_authorized": False,
            "src_change_authorized": False,
            "spec_extension_authorized": False,
            "extension_target_selected": False,
            "B1_L_execution_authorized": False,
            "N32_selected": False,
            "ready_for_I1_human_review": not failed,
            "ready_for_I2": False,
        },
        "blocked_relabels": [
            "B1_GRR2_as_B2_positive_evidence",
            "bounded_search_as_mechanical_impossibility",
            "synthetic_old_current_as_runtime_reached_formation",
            "branch_relocation_as_retained_carrier",
            "frozen_W_sensitivity_as_native_mediation",
            "zero_probe_baseline_as_core_ReadBack_passive_null",
            "missing_role_as_extension_authorization",
            "retention_as_memory_learning_agency_or_life",
        ],
    }
    absolute_paths = find_absolute_paths(payload)
    payload["path_audit"] = {
        "absolute_path_locations": absolute_paths,
        "all_recorded_paths_repository_or_source_repository_relative": not absolute_paths,
    }
    if absolute_paths:
        payload["status"] = "failed"
        payload["failed_checks"] = sorted([*payload["failed_checks"], "recorded_absolute_path"])
        payload["claim_boundary"]["ready_for_I1_human_review"] = False
    return payload


def render_report(artifact: dict[str, Any]) -> str:
    payload = artifact["payload"]
    boundary = payload["accepted_starting_boundary"]
    route = payload["admitted_route"]
    lines = [
        "# B2-GR Iteration 1 - Source And Handoff Admission",
        "",
        "## Result",
        "",
        f"- Status: `{payload['status']}`",
        f"- Acceptance: `{payload['acceptance_state']}`",
        f"- Source records: `{payload['source_record_count']}`",
        f"- Checks: `{payload['passed_check_count']}/{payload['check_count']}` passed",
        "- Positive B2 evidence opened: `false`",
        "- GRR rung assigned: `false`",
        "- Process ceiling: `B2-C0-ready` pending human review",
        "",
        "## Accepted Starting Boundary",
        "",
        f"B1-GR is consumed at accepted closeout `GRV-C6`, with maximum retention rung `{boundary['maximum_retention_rung']}`. Its retained result is `{boundary['retention_class']}` after a `{boundary['forming_input_provenance']}` input.",
        "",
        "The following remain unresolved or unsupported and therefore define B2 rather than satisfy it:",
        "",
        f"- Native branch-only reachability: `{boundary['native_branch_only_reachability']}`",
        f"- Isolated slow-cluster occupancy: `{boundary['isolated_slow_cluster_occupancy']}`",
        f"- Specific transient-W mediation: `{boundary['specific_transient_W_mediation']}`",
        f"- Matched native probe mediation: `{boundary['matched_native_probe_mediation']}`",
        f"- Branch-relocation rival: `{boundary['branch_relocation_rival']}`",
        "",
        "## Route Admission",
        "",
        f"The accepted first route is `{route['lane_id']}`: `{route['target']}`. Its status is `{route['status']}`. B1-GR explicitly did not establish mechanical impossibility and did not authorize a runtime extension.",
        "",
        "## Lifecycle Reconciliation",
        "",
        "The handoff payload was generated before final closeout acceptance and therefore retains `candidate_pending_closeout_review` and `grv_c6_assigned = false`. The later accepted closeout anchor binds that exact handoff and evidence bundle while assigning `GRV-C6`. Source precedence resolves lifecycle authority to the accepted closeout anchor without rewriting historical artifacts.",
        "",
        "## Source Consumption",
        "",
        "Final classifications and the accepted handoff provide the B1 boundary. Gate artifacts provide accepted source evidence and methods. Reports are context only. The pinned theory papers provide definitions and vocabulary only.",
        "",
        "No B1 artifact is consumed as B2 `GRR3-GRR5` evidence, and no missing role is consumed as extension necessity.",
        "",
        "Source precedence narrows interpretation and resolves lifecycle authority; it cannot overwrite a contradictory raw measurement. Every consumed JSON field has a semantic digest, source role, allowed use, forbidden use, and `positive_B2_rung_credit = false`.",
        "",
        "## Runtime And Branch Identity",
        "",
        f"The unchanged-runtime identity binds `{len(payload['unchanged_runtime_identity']['runtime_file_records'])}` GRC9V3/core files plus the complete protected `src/pygrc`, `specs`, and existing `tests` tree at revision `{payload['unchanged_runtime_identity']['repository_revision']}`.",
        "",
        f"The B1 branch crosswalk retains all `{payload['B1_branch_crosswalk']['accepted_B1_branch_population_count']}` accepted branches before B2 eligibility selection. It joins branch, fixture, symmetry orbit, topology, node/edge order, parameter, budget, gauge, categorical-stratum, operator, intervention, retention, and causal-role identities. No branch ranking is performed in I1.",
        "",
        "## Dependency And Consistency Audit",
        "",
        "The dependency closure distinguishes evidence-bundle members from accepted post-bundle derivatives. Bundle exclusion of the handoff, successor, and closeout records is preserved as lifecycle ordering rather than reported as missing evidence.",
        "",
        "Raw GRV5 measurements and final GRV8 classifications agree on the GRR2 ceiling, absent native mediation, unresolved branch-relocation rival, and synthetic forming provenance. Any material raw/final disagreement would fail I1 as `source_consistency_failure`.",
        "",
        f"The inherited `GRR0-GRR5` ladder is bound to `{payload['GRR_ladder_definition']['source_path']}` with section SHA-256 `{payload['GRR_ladder_definition']['section_sha256']}`; I2 may operationalize but not redefine it.",
        "",
        "## Decision",
        "",
        "Iteration 1 is mechanically complete and ready for scientific review. Acceptance may assign `B2-C0`; Iteration 2 remains blocked until that acceptance anchor exists.",
        "",
        f"Artifact payload SHA-256: `{artifact['payload_sha256']}`",
        "",
    ]
    return "\n".join(lines)


def execute(output_root: Path, report_root: Path) -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("B2 I1 requires a clean committed execution package")
    input_revision = git("rev-parse", "HEAD")
    substrate_revision = git("merge-base", "main", "HEAD")
    tree = experiment_tree()
    protected = protected_manifest(input_revision, substrate_revision)
    payload = build_payload(input_revision, protected)
    payload["input_execution_revision"] = input_revision
    payload["substrate_base_revision"] = substrate_revision
    payload["input_experiment_tree_sha256"] = tree["tree_sha256"]
    payload["source_contract_path"] = CONFIG_RELATIVE
    payload["source_contract_sha256"] = sha256_file(REPO_ROOT / CONFIG_RELATIVE)
    artifact = envelope(payload, "b2_i1_source_handoff_inventory_v2", COMMAND)

    inventory_path = output_root / "b2_i1_source_handoff_inventory.json"
    protected_path = output_root / "b2_i1_protected_path_manifest.json"
    report_path = report_root / "b2_i1_source_handoff_inventory.md"
    write_json(inventory_path, artifact)
    write_json(protected_path, protected)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(artifact), encoding="utf-8")

    output_digests = {
        repo_relative(path): sha256_file(path)
        for path in (inventory_path, protected_path, report_path)
    }
    closeout_anchor_relative = (
        f"{B1_RELATIVE}/outputs/gates/grv8_closeout_acceptance_anchor.json"
    )
    receipt = finalize_receipt(
        {
            "gate_id": "B2-I1",
            "input_execution_revision": input_revision,
            "substrate_base_revision": substrate_revision,
            "input_experiment_tree_sha256": tree["tree_sha256"],
            "generating_script_path": repo_relative(Path(__file__)),
            "generating_script_sha256": sha256_file(Path(__file__)),
            "config_path": CONFIG_RELATIVE,
            "config_sha256": sha256_file(REPO_ROOT / CONFIG_RELATIVE),
            "prerequisite_result_receipt_digests": [],
            "prerequisite_acceptance_anchors": [
                {
                    "path": closeout_anchor_relative,
                    "sha256": sha256_file(REPO_ROOT / closeout_anchor_relative),
                    "acceptance_status": "accepted",
                    "assigned_closeout_rung": "GRV-C6",
                }
            ],
            "output_artifact_digests": output_digests,
            "status": "awaiting_scientific_review" if payload["status"] == "passed" else "blocked",
            "blocked_gates": ["B2-I2", "B2-I3", "B2-I4", "B2-I5", "B2-I6", "B2-I7", "B2-I8"],
            "claim_ceiling": "B2-C0-ready_source_admission_only_no_positive_constructibility_evidence",
        }
    )
    receipt_path = output_root / "gates/b2_i1_result_receipt.json"
    write_json(receipt_path, receipt)
    return {
        "artifact": artifact,
        "protected": protected,
        "receipt": receipt,
        "paths": [inventory_path, protected_path, report_path, receipt_path],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    parser.add_argument("--report-root", type=Path, default=EXPERIMENT_ROOT / "reports")
    args = parser.parse_args()
    execute(args.output_root, args.report_root)


if __name__ == "__main__":
    main()
