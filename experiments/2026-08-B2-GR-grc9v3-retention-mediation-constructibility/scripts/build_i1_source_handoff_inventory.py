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


def graph_source_record(contract: dict[str, Any]) -> dict[str, Any]:
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
            }
        )
    record = {
        **contract,
        "repository": "github.com/urosj/graph-reflexive-coherence",
        "repository_relative_path": repository_relative,
        "exists": True,
        "tracked": True,
        "git_blob": git_blob(repository_relative),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "payload_sha256": payload_sha256,
        "consumed_values": consumed,
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


def build_payload() -> dict[str, Any]:
    contract = source_contract()
    graph_records = [graph_source_record(row) for row in contract["graph_sources"]]
    theory_records = [theory_source_record(row) for row in contract["theory_sources"]]
    by_id = {row["source_id"]: row for row in graph_records}

    closeout = read_json(B1_ROOT / "outputs/gates/grv8_closeout_acceptance_anchor.json")
    bundle = read_json(B1_ROOT / "outputs/evidence_bundle_manifest.json")
    handoff = read_json(B1_ROOT / "outputs/continuation_readback_next_route_handoff.json")
    causal = read_json(B1_ROOT / "outputs/final_causal_role_classification.json")
    claims = read_json(B1_ROOT / "outputs/final_claim_classification.json")
    extension = read_json(B1_ROOT / "outputs/extension_decision.json")
    retention = read_json(B1_ROOT / "outputs/conductance_retention_probe.json")

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
        "source_precedence": contract["source_precedence"],
        "source_precedence_resolution": {
            "embedded_handoff_status": handoff["payload"]["handoff_status"],
            "embedded_handoff_grv_c6_assigned": handoff["payload"]["grv_c6_assigned"],
            "authoritative_closeout_status": closeout["acceptance_status"],
            "authoritative_closeout_rung": closeout["assigned_closeout_rung"],
            "resolution": "closeout_acceptance_anchor_supersedes_preacceptance_embedded_handoff_lifecycle_fields_without_mutating_the_handoff",
        },
        "graph_source_records": graph_records,
        "theory_source_records": theory_records,
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
    payload = build_payload()
    payload["input_execution_revision"] = input_revision
    payload["substrate_base_revision"] = substrate_revision
    payload["input_experiment_tree_sha256"] = tree["tree_sha256"]
    payload["source_contract_path"] = CONFIG_RELATIVE
    payload["source_contract_sha256"] = sha256_file(REPO_ROOT / CONFIG_RELATIVE)
    artifact = envelope(payload, "b2_i1_source_handoff_inventory_v1", COMMAND)
    protected = protected_manifest(input_revision, substrate_revision)

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
