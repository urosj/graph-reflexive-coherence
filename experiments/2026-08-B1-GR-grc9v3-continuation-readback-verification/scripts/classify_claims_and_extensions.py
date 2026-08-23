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
    "conductance_mediated_retention",
    "native_read_effect",
    "activity_conditioned_write_effect",
    "distinct_directional_read_current",
    "j_equals_J_C_limit",
    "magnitude_and_axis_inscription",
    "orientation_retention",
    "field_current_full_equivalence_hierarchy",
    "K_hybrid_node_tensor",
    "geometry_mobility_separation",
    "active_stationary_circulation",
    "recurrent_transport_orbits",
    "moving_retained_slow_bundle",
    "runtime_row_signed_Hessian_relation_to_continuation",
}
SOURCE_IDS = {
    "SRC-CONTINUATION": "core/2026-08-TheContinuationSpectrum.md",
    "SRC-READBACK": "core/2026-08-ReadBack.md",
}


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


def equivalence_classification(policy: dict[str, Any], claim_rows: list[dict[str, Any]]) -> dict[str, Any]:
    assumption_by_claim = {
        row["claim_id"]: row["required_assumption_ids"] for row in claim_rows
    }
    proof_by_claim = {row["claim_id"]: row["proof_note_ids"] for row in claim_rows}
    rows = []
    for source in policy["object_classifications"]:
        rows.append(
            {
                **source,
                "classification_scope": "bounded_B1_GR_unchanged_GRC9V3_evidence_envelope",
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


def final_debt_register(policy: dict[str, Any], source_debts: list[dict[str, Any]]) -> dict[str, Any]:
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
        rows.append(
            {
                **source,
                "GRV8_status": "open_with_bounded_route",
                "GRV8_primary_route": policy["debt_routes"][debt_id],
                "evidence_refs": evidence_refs or ["outputs/theory_source_manifest.json"],
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
        "",
        "## Main Classification",
        "",
        "- Formed fixed-topology branches are exact bounded runtime results.",
        "- The synchronous causal closure is a bounded simplifying limit with `C`",
        "  independent and `W/J` reconstructed or stage-dependent.",
        "- The fixed-`W` continuation construction and complete-step spectra are",
        "  analysis surfaces, not native retained-sector or Read-Back objects.",
        "- GRV5 supports only synthetic, `C`-dominated neutral persistence; native",
        "  transient-`W` mediation, Read-Back, write-back, and closure remain blocked.",
        "- GRV6 provides bounded negative short-period recurrence evidence without a",
        "  global orbit-nonexistence claim.",
        "- GRV7 supports reduced clamped-`W` non-equivalence, not runtime/full-map",
        "  non-equivalence or an informative nontrivial complete-step `+1` threshold.",
        "",
        "## Extension And Theory Routes",
        "",
    ]
    for row in extensions["decisions"]:
        lines.append(f"- `{row['decision_id']}`: `{row['route']}`.")
    lines.extend(
        [
            f"- Theory reopening: `{reopening['decision']['route']}`.",
            "",
            "`K` remains diagnostic. Geometry/mobility and retained-carrier",
            "extensions are not opened because their preregistered triggers were not",
            "met. An oriented-current extension is conditionally selectable only if a",
            "future target explicitly requires directional Read-Back or active",
            "circulation; B1-GR does not select that target.",
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
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))

    proof_notes = envelope_payload("proof_note_registry")
    assumptions_payload = assumption_matrix(policy, source["claim_source"]["records"])
    claims_payload = claim_classification(
        policy,
        source["claim_source"]["records"],
        {row["proof_note_id"] for row in proof_notes["records"]},
    )
    claims_by_id = {row["claim_id"]: row for row in claims_payload["rows"]}
    equivalence_payload = equivalence_classification(policy, claims_payload["rows"])
    debts_payload = final_debt_register(policy, source["debt_source"]["records"])
    traceability_source = envelope_payload("theory_test_traceability")
    traceability_payload = completed_traceability(
        traceability_source["records"], claims_by_id, policy
    )
    contradictions_payload = {
        "gate_id": "GRV8",
        "allowed_routes": sorted(ALLOWED_CONTRADICTION_ROUTES),
        "entries": contradiction_entries(),
        "theory_contradiction_count": 0,
        "highest_supported_claim": "all_material_mismatches_have_one_primary_non_theory_reopening_route",
        "blocked_claims": ["substrate_nonrealization_is_theory_falsification"],
    }
    extensions_payload = {
        "gate_id": "GRV8",
        "decisions": extension_decisions(policy),
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
        "final_claim_classification.json": (claims_payload, "b1_grv8_final_claim_classification_v1"),
        "equivalence_classification.json": (equivalence_payload, "b1_grv8_equivalence_classification_v1"),
        "final_theory_debt_register.json": (debts_payload, "b1_grv8_final_theory_debt_register_v1"),
        "final_theory_test_traceability.json": (traceability_payload, "b1_grv8_final_theory_test_traceability_v1"),
        "final_contradiction_routing.json": (contradictions_payload, "b1_grv8_final_contradiction_routing_v1"),
        "extension_decision.json": (extensions_payload, "b1_grv8_extension_decision_v1"),
        "theory_reopening_decision.json": (reopening_payload, "b1_grv8_theory_reopening_decision_v1"),
        "superseded_exploratory_claims.json": (superseded_payload, "b1_grv8_superseded_exploratory_claims_v1"),
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
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(output_paths)
            },
            "grv8_summary": {
                "assumption_count": len(assumptions_payload["rows"]),
                "claim_count": len(claims_payload["rows"]),
                "object_count": len(equivalence_payload["rows"]),
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
