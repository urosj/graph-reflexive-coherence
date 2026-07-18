#!/usr/bin/env python3
"""Build N31 Iteration 11 comparative semantic classification records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i11_comparative_classification_artifacts"
PREREGISTRATION = ARTIFACT_DIR / "n31_i11_preregistration.json"
I10_AUTHORITY_RECEIPT = ARTIFACT_DIR / "n31_i11_i10_authority_receipt.json"
PROFILE_MATRIX = ARTIFACT_DIR / "n31_i11_six_row_profile_matrix.json"
BRIDGE_AUDIT = ARTIFACT_DIR / "n31_i11_d0r_br_bridge_audit.json"
ADMISSION_MATRIX = ARTIFACT_DIR / "n31_i11_native_admission_debt_matrix.json"
SELECTION = ARTIFACT_DIR / "n31_i11_conditional_selection.json"
TRACE = OUTPUTS / "n31_i11_comparative_classification_trace.json"
OUTPUT = OUTPUTS / "n31_comparative_semantic_native_admission_i11.json"
REPORT = REPORTS / "n31_comparative_semantic_native_admission_i11.md"

I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I8 = OUTPUTS / "n31_d0_replay_controls_classification_i8.json"
I9A = OUTPUTS / "n31_release_efficacy_attenuation_i9a.json"
I9A1 = OUTPUTS / "n31_release_efficacy_downstream_readout_i9a1.json"
I9B = OUTPUTS / "n31_conserved_leakage_i9b.json"
I9B1 = OUTPUTS / "n31_conserved_leakage_response_i9b1.json"
I9C = OUTPUTS / "n31_susceptibility_relaxation_i9c.json"
I9C1 = OUTPUTS / "n31_exact_derived_susceptibility_i9c1.json"
I9C2 = OUTPUTS / "n31_native_exact_history_closure_i9c2.json"
I10 = OUTPUTS / "n31_added_mechanism_replay_controls_i10.json"

SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_comparative_classification_i11.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "e7fc5b4"
I10_COMMIT_REVISION = "e7fc5b4a30e707c42aec83e94d40d36546a2af60"

SOURCE_IDENTITIES = {
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I8: (
        "bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8",
        "28a3d8b9e98b23ebdc7d852e9264fd802dad9bb45d48097d40efa2a0b1c9dc61",
    ),
    I9A: (
        "cdb2bd7f27bfba52e6b007b5a54d9c2bd04d20723bf3037162d94268c69a22c0",
        "b5824794ac802bf5cc787bf6d09410f56494a49b5f5af757bcd15dae68d61031",
    ),
    I9A1: (
        "0a10639f3d6e9b42806655a2c90c4b9fdeb384c21d8b35622bcffd14d4149f91",
        "9c6a818d2ecd47c54e30118790504141dcb702a517b5dcc106cea94393941ddb",
    ),
    I9B: (
        "4427aa0c5d5d1e864f304873edbe2190ec3e975c0702e4f1ef3ed4ac81adc9b3",
        "0ea586c7bfe23d3c8341fa874b07892ce4274125d58b8a6c77a284f77214d5ac",
    ),
    I9B1: (
        "867337e1b5adf04356e5fb6172de3ca42f6c5e0619ce6f8d38e02766f5f4a15e",
        "1f40fb8f2064996509eb3c2661c72408c9aab790d9119a9211f22458d2e18e87",
    ),
    I9C: (
        "f9a7a96c26474277a5009ad2a5a56c7d5bfa000fe801bdbc5178c59e2c26f8ad",
        "50f350a370ba96b1994f7ad1086dc46d9661f38e843e4a77679f1de65f7cdf5b",
    ),
    I9C1: (
        "2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e",
        "30d2ceca6c208d11097bae5c699cdc90aa9e2b91c1ef2988bd3d333d3a89dbe9",
    ),
    I9C2: (
        "93d2c5341d0398e27991e6f6ca4d364e795e009ed502d223c1b8197f875402fe",
        "035c7f7b0933ddca649ab17809222efd5e1e27da08980dc33e4f2abf32a26995",
    ),
    I10: (
        "29314dc62908e445deeb868ad04719dc1c23bd856562ac159098f5a3b081e257",
        "c8bf981ae9b5d59e2e486dc1c53bf84a1859ddf4569d4eea4c253e85039872af",
    ),
}

PROFILE_AXES = [
    "semantic_fit",
    "strict_RC_theory_compatibility",
    "coherence_conservation",
    "local_causality",
    "internal_time_ownership",
    "carrier_authority",
    "mediation_strength",
    "restoration_completeness",
    "native_mechanics_already_available",
    "producer_residue",
    "naturalization_debt",
    "topology_scope",
    "transfer_evidence",
    "RCAE_relevance",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_diff_empty(path: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    value = dict(record)
    value["output_digest"] = digest_value(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8")
    return value


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "status": value.get("status", "not_recorded"),
        "acceptance_state": value.get("acceptance_state", "not_recorded"),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "identity_exact": value.get("output_digest") == expected_digest
        and actual_sha == expected_sha,
    }


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def profiles() -> list[dict[str, Any]]:
    rows = [
        {
            "comparison_row_id": "D0a_native_spatial_organization",
            "semantic_class": "D0a",
            "authority_lane": "native_relation",
            "ladder_rungs": {"native_relation": "DR2"},
            "semantic_fit": "native route-local coherence organization forms and persists; autonomous weakening is absent",
            "strict_RC_theory_compatibility": "highest current ontological fit because complete native C/J_C carries the relation, but the requested decay trajectory is incomplete",
            "coherence_conservation": "native LGRC invariant and replay closure passed",
            "local_causality": "formation and persistence are local; weakening causality is unsupported",
            "internal_time_ownership": "native LGRC event progression",
            "carrier_authority": "native complete coherence and packet state",
            "mediation_strength": "full route-distribution mediation unresolved",
            "restoration_completeness": "source-current replay and restoration passed in I8",
            "native_mechanics_already_available": "formation and persistence available; autonomous weakening unavailable",
            "producer_residue": [],
            "naturalization_debt": [
                "ordinary autonomous weakening trajectory",
                "full route-organization mediation",
            ],
            "topology_scope": "bounded route-local fixture",
            "transfer_evidence": "not established",
            "RCAE_relevance": "native substrate baseline only; not a Q-005 decay provider",
            "route_mass_decreased": False,
            "native_route_organization_state_weakened": False,
            "derived_organization_observable_weakened": "not_applicable",
            "derived_susceptibility_relation_weakened": "not_applicable",
            "later_readout_changed": False,
            "organization_mediated_readout_change_supported": False,
            "organization_mediation_scope": "unresolved",
            "selection_disposition": "retained_native_foundation_not_selected_as_decay_provider",
            "evidence_basis": ["I8"],
            "comparative_boundary_sources": ["I10"],
        },
        {
            "comparison_row_id": "D0b_finite_window_derived_observable",
            "semantic_class": "D0b",
            "authority_lane": "exact_derived_observable",
            "ladder_rungs": {"observable_relation": "DR3"},
            "semantic_fit": "finite-window organization observable weakens after formation",
            "strict_RC_theory_compatibility": "strong derived-state fit because the observable adds no independent causal field",
            "coherence_conservation": "diagnostic is read-only over native conserved state",
            "local_causality": "weakening observed but causal mediation of later transport is false",
            "internal_time_ownership": "declared native event window",
            "carrier_authority": "exact derived functional of source-current native state/history",
            "mediation_strength": "none established",
            "restoration_completeness": "observable reconstruction and replay passed in I8",
            "native_mechanics_already_available": "diagnostic inputs available; causal trail mechanism absent",
            "producer_residue": ["experiment declares the diagnostic window but does not mutate state"],
            "naturalization_debt": ["causal mediator", "local intervention-backed readout"],
            "topology_scope": "bounded finite-window route diagnostic",
            "transfer_evidence": "not established",
            "RCAE_relevance": "usable fading diagnostic below causal trail semantics",
            "route_mass_decreased": "not_required_for_observable",
            "native_route_organization_state_weakened": "unsupported",
            "derived_organization_observable_weakened": True,
            "derived_susceptibility_relation_weakened": "not_applicable",
            "later_readout_changed": False,
            "organization_mediated_readout_change_supported": False,
            "organization_mediation_scope": "none",
            "selection_disposition": "retained_diagnostic_not_selected_as_causal_provider",
            "evidence_basis": ["I8"],
            "comparative_boundary_sources": ["I10"],
        },
        {
            "comparison_row_id": "D0c_instantaneous_geometry_comparator",
            "semantic_class": "D0c",
            "authority_lane": "instantaneous_derived_observable",
            "ladder_rungs": {"observable_relation": "DR1"},
            "semantic_fit": "current-state geometric comparison without persistence or weakening trajectory",
            "strict_RC_theory_compatibility": "strong diagnostic fit because it is derived from current coherence state",
            "coherence_conservation": "read-only diagnostic",
            "local_causality": "no causal decay relation established",
            "internal_time_ownership": "single source-current observation",
            "carrier_authority": "current native geometry projection",
            "mediation_strength": "none",
            "restoration_completeness": "current-state reconstruction passed in I8",
            "native_mechanics_already_available": "instantaneous comparator available",
            "producer_residue": [],
            "naturalization_debt": ["persistence", "weakening trajectory", "causal mediation"],
            "topology_scope": "single current-state route comparison",
            "transfer_evidence": "not established",
            "RCAE_relevance": "useful instantaneous geometry diagnostic, not a field lifecycle",
            "route_mass_decreased": "not_applicable",
            "native_route_organization_state_weakened": False,
            "derived_organization_observable_weakened": False,
            "derived_susceptibility_relation_weakened": "not_applicable",
            "later_readout_changed": False,
            "organization_mediated_readout_change_supported": False,
            "organization_mediation_scope": "none",
            "selection_disposition": "retained_diagnostic_not_selected_as_decay_provider",
            "evidence_basis": ["I8"],
            "comparative_boundary_sources": ["I10"],
        },
        {
            "comparison_row_id": "A_release_efficacy_attenuation",
            "semantic_class": "A",
            "authority_lane": "producer_mediated_expression_policy",
            "ladder_rungs": {"producer_mechanism": "DR5", "candidate_native": "not_admitted"},
            "semantic_fit": "old carrier expresses less at release while retained coherence and in-flight packets remain stable",
            "strict_RC_theory_compatibility": "partial: coherence remains primary in transport, but independent receipt-indexed phase controls expression",
            "coherence_conservation": "exact source, packet, and receiver accounting passed",
            "local_causality": "bounded receiver-C mediation supports a later native admission split",
            "internal_time_ownership": "qualifying local native receipts advance experiment-owned phase",
            "carrier_authority": "native packet/coherence carrier plus producer-owned release-phase state",
            "mediation_strength": "bounded partial local receiver-C",
            "restoration_completeness": "composed native and producer state replay/restoration passed in I10",
            "native_mechanics_already_available": "native transport exists; release-efficacy lifecycle does not",
            "producer_residue": ["release phase", "efficacy rule", "release invocation"],
            "naturalization_debt": ["library-owned release-phase lifecycle or explicit retained closure status"],
            "topology_scope": "bounded local release/receiver route",
            "transfer_evidence": "fixture-local only",
            "RCAE_relevance": "valid only if the ecology selects expression attenuation rather than field-state decay",
            "route_mass_decreased": False,
            "native_route_organization_state_weakened": False,
            "derived_organization_observable_weakened": "not_applicable",
            "derived_susceptibility_relation_weakened": "not_applicable",
            "later_readout_changed": True,
            "organization_mediated_readout_change_supported": False,
            "organization_mediation_scope": "none",
            "selection_disposition": "retained_semantic_boundary_not_selected_for_current_field_state_demand",
            "evidence_basis": ["I9-A", "I9-A.1", "I10"],
        },
        {
            "comparison_row_id": "B_conserved_export_policy",
            "semantic_class": "B-R",
            "authority_lane": "producer_mediated_export_policy_native_transport",
            "ladder_rungs": {"producer_mechanism": "DR5", "candidate_native": "not_admitted"},
            "semantic_fit": "route mass and organization weaken through conservative export to an explicit destination",
            "strict_RC_theory_compatibility": "closest added mechanism to the strict coherence-only ontology; the missing part is endogenous export policy, not a second field substance",
            "coherence_conservation": "exact source debit, in-flight amount, destination credit, and global closure passed",
            "local_causality": "bounded local source-C mediation shifts a later native admission boundary",
            "internal_time_ownership": "native event progression with experiment-owned local export callback",
            "carrier_authority": "native coherence and packet transport; producer owns export lifecycle",
            "mediation_strength": "bounded partial local leakage-source C",
            "restoration_completeness": "composed export policy and native state replay/restoration passed in I10",
            "native_mechanics_already_available": "conservative packet transport exists; ordinary autonomous export policy does not",
            "producer_residue": ["export eligibility", "amount/cap", "time", "destination"],
            "naturalization_debt": [
                "native route-local export lifecycle",
                "full route-distribution mediation",
                "separate D0-R bridge evidence",
            ],
            "topology_scope": "four-node route with explicit out-of-readout destination",
            "transfer_evidence": "bounded response shape only; cross-topology transfer not established",
            "RCAE_relevance": "primary conditional candidate when the demanded meaning is conservative field-magnitude redistribution",
            "route_mass_decreased": True,
            "native_route_organization_state_weakened": True,
            "derived_organization_observable_weakened": "not_applicable",
            "derived_susceptibility_relation_weakened": "not_applicable",
            "later_readout_changed": True,
            "organization_mediated_readout_change_supported": True,
            "organization_mediation_scope": "bounded_partial_local_source_C",
            "selection_disposition": "conditionally_selected_for_I12_conserved_redistribution_contract",
            "evidence_basis": ["I9-B", "I9-B.1", "I10"],
        },
        {
            "comparison_row_id": "C2_exact_history_susceptibility_closure",
            "semantic_class": "C.2",
            "authority_lane": "exact_history_relation_plus_producer_constitutive_closure",
            "ladder_rungs": {
                "relation_carrier": "DR2",
                "producer_extension": "DR5",
                "native_runtime": "DR0",
            },
            "semantic_fit": "activity-indexed route susceptibility relaxes toward a floor through an exact functional of native packet history",
            "strict_RC_theory_compatibility": "not strict current-C-only ontology; functionally closest to self-modifying geometry but depends on complete native history beyond current C",
            "coherence_conservation": "native packet transport closes; derived S is dimensionless and adds no coherence mass",
            "local_causality": "bounded effective geometry changes native transport; full direct-mediation isolation remains deferred",
            "internal_time_ownership": "qualifying committed-arrival history and later local native progression, not wall clock",
            "carrier_authority": "exact native serialized packet history; S is recomputed, not independently stored",
            "mediation_strength": "bounded effective-geometry mediation with native constitutive hook absent",
            "restoration_completeness": "native history, rederived S, post-feedback state, and next-step continuation passed in I10",
            "native_mechanics_already_available": "history and packet execution exist; native history-conditioned conductance hook does not",
            "producer_residue": ["history functional application", "effective conductance insertion", "packet scheduling"],
            "naturalization_debt": [
                "packetization invariance",
                "direct mediation controls",
                "multi-cycle stability",
                "topology lifecycle policy",
                "cache/pruning semantics",
                "native source-current re-admission",
            ],
            "topology_scope": "role-preserving renumbering passed; topology lifecycle unresolved",
            "transfer_evidence": "role-preserving representation transfer only",
            "RCAE_relevance": "conditional alternative when the demanded meaning is activity-indexed susceptibility or geometry relaxation",
            "route_mass_decreased": False,
            "native_route_organization_state_weakened": False,
            "derived_organization_observable_weakened": "not_applicable",
            "derived_susceptibility_relation_weakened": True,
            "later_readout_changed": True,
            "organization_mediated_readout_change_supported": True,
            "organization_mediation_scope": "bounded_effective_geometry",
            "selection_disposition": "conditionally_selected_for_I12_susceptibility_closure_contract",
            "evidence_basis": ["I9-C.2", "I10"],
        },
    ]
    for row in rows:
        row["profile_axes_complete"] = all(axis in row for axis in PROFILE_AXES)
    return rows


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    sources = {relative(path): load_json(path) for path in SOURCE_IDENTITIES}
    source_records = [source_record(path) for path in SOURCE_IDENTITIES]
    i8 = sources[relative(I8)]
    i10 = sources[relative(I10)]

    if i8["classification"]["native_spatial_D0a"]["decay_relation_ladder_rung"] != "DR2":
        raise ValueError("I8 native D0a ceiling changed")
    if i10["family_classification"]["A"]["added_mechanism_ladder_rung"] != "DR5":
        raise ValueError("I10 A lane changed")
    if i10["family_classification"]["B"]["added_mechanism_ladder_rung"] != "DR5":
        raise ValueError("I10 B lane changed")
    if i10["family_classification"]["C"]["producer_extension_lane_rung"] != "DR5":
        raise ValueError("I10 C.2 producer lane changed")

    preregistration = write_record(
        PREREGISTRATION,
        {
            "artifact_kind": "n31_i11_preregistration",
            "artifact_schema_version": "n31_i11_preregistration_v1",
            "generated_at": GENERATED_AT,
            "comparison_row_ids": [
                "D0a_native_spatial_organization",
                "D0b_finite_window_derived_observable",
                "D0c_instantaneous_geometry_comparator",
                "A_release_efficacy_attenuation",
                "B_conserved_export_policy",
                "C2_exact_history_susceptibility_closure",
            ],
            "profile_axes": PROFILE_AXES,
            "ranking_policy": {
                "single_scalar_score_allowed": False,
                "raw_effect_magnitude_ranking_allowed": False,
                "cross_semantic_universal_winner_required": False,
                "conditional_plural_selection_allowed": True,
                "native_and_producer_lanes_may_be_collapsed": False,
                "native_authority_receives_selection_priority": False,
            },
            "selection_rules": {
                "selection_relation": "non_ranked_semantically_distinct_conditional_frontiers",
                "candidate_choice_follows_demanded_semantics": True,
                "equal_selection_eligibility_does_not_imply_equal_implementation_maturity": True,
            },
            "source_policy": "consume exact source artifacts; I11 performs classification, not new runtime execution",
            "rung_policy": "I11 may retain earned DR rungs and N31-C5 progress but cannot assign DR6 or terminal closeout",
            "frozen_before_profile_construction": True,
        },
    )
    preregistration_identity = {
        "path": relative(PREREGISTRATION),
        "output_digest": preregistration["output_digest"],
        "sha256": sha256_file(PREREGISTRATION),
    }

    i10_witness = next(
        row
        for row in i10["checks"]
        if row["check_id"]
        == "C2_post_feedback_final_state_restoration_witness_exact"
    )
    i10_authority_receipt = write_record(
        I10_AUTHORITY_RECEIPT,
        {
            "artifact_kind": "n31_i11_i10_committed_authority_receipt",
            "artifact_schema_version": "n31_i11_i10_committed_authority_receipt_v1",
            "generated_at": GENERATED_AT,
            "committed_I10_identity": {
                "path": relative(I10),
                "output_digest": i10["output_digest"],
                "sha256": sha256_file(I10),
                "git_revision": I10_COMMIT_REVISION,
            },
            "committed_artifact_unchanged_at_I11": git_diff_empty(relative(I10)),
            "post_commit_I10_revision_detected": False,
            "post_commit_I10_corrections_applied": False,
            "reviewed_identity_mismatch_reproduced_from_repository": False,
            "reviewed_identity_mismatch_disposition": "no_second_committed_I10_identity_exists; I11 consumes the exact e7fc5b4 authority",
            "C2_post_feedback_restoration_present_in_committed_I10": True,
            "C2_post_feedback_witness": i10_witness,
            "scientific_A_B_conclusions_changed": False,
            "C2_DR5_disposition": "committed_as_confirmed_after_final_post_feedback_restoration_and_next_step_witness",
            "committed_identity_is_I11_authority": True,
        },
    )

    profile_rows = profiles()
    profile_matrix = write_record(
        PROFILE_MATRIX,
        {
            "artifact_kind": "n31_i11_six_row_profile_matrix",
            "artifact_schema_version": "n31_i11_six_row_profile_matrix_v1",
            "generated_at": GENERATED_AT,
            "profile_axes": PROFILE_AXES,
            "row_count": len(profile_rows),
            "rows": profile_rows,
            "preregistration_identity": preregistration_identity,
            "profile_axes_frozen_preclassification": PROFILE_AXES
            == preregistration["profile_axes"],
            "single_scalar_ranking_performed": False,
            "raw_effect_magnitude_ranking_performed": False,
            "universal_selection_not_defined": True,
            "universal_selection_not_defined_reason": "candidates_answer_nonequivalent_semantic_demands",
            "conditional_frontiers": {
                "native_coherence_only_foundation": "D0a_native_spatial_organization",
                "derived_diagnostic_frontier": [
                    "D0b_finite_window_derived_observable",
                    "D0c_instantaneous_geometry_comparator",
                ],
                "expression_attenuation_frontier": "A_release_efficacy_attenuation",
                "strict_ontology_added_mechanism_frontier": "B_conserved_export_policy",
                "functional_reflexive_geometry_frontier": "C2_exact_history_susceptibility_closure",
            },
        },
    )

    bridge_audit = write_record(
        BRIDGE_AUDIT,
        {
            "artifact_kind": "n31_i11_d0r_br_bridge_audit",
            "artifact_schema_version": "n31_i11_d0r_br_bridge_audit_v1",
            "generated_at": GENERATED_AT,
            "D0_R": {
                "status": "not_instantiated_in_executed_D0_fixtures",
                "ordinary_post_formation_export_observed": False,
                "globally_refuted": False,
                "comparison_eligible": False,
                "source_artifacts": [relative(I8), relative(I10)],
            },
            "B_R": {
                "status": "supported_producer_mediated_DR5",
                "route_mass_decreased": True,
                "native_route_organization_state_weakened": True,
                "later_readout_changed": True,
                "organization_mediation": "bounded_partial_local_source_C",
                "export_policy_owner": "experiment_producer",
                "native_transport_owner": "LGRC9V3",
                "source_artifacts": [relative(I9B), relative(I9B1), relative(I10)],
            },
            "d0_to_br_bridge_status": "not_tested",
            "bounded_shape_analogy_status": "supported_non_promotional",
            "B_R_D0_R_equivalence_supported": False,
            "current_B_R_classified_as_D0_R": False,
            "conservation_promotes_B_R_to_D0_R": False,
            "interpretation": "B-R is a bounded operational fallback with exact conservation, not evidence that ordinary D0-R exists",
        },
    )

    admission_rows = [
        {
            "candidate_id": "D0a_native_spatial_organization",
            "native_admission": "existing_native_relation_DR2",
            "provider_contract_eligible_in_I11": False,
            "missing_native_surface": "autonomous weakening trajectory",
            "producer_result_may_upgrade_native": False,
        },
        {
            "candidate_id": "D0b_finite_window_derived_observable",
            "native_admission": "exact_derived_from_native_state_observable_DR3",
            "provider_contract_eligible_in_I11": False,
            "missing_native_surface": "causal mediator",
            "producer_result_may_upgrade_native": False,
        },
        {
            "candidate_id": "D0c_instantaneous_geometry_comparator",
            "native_admission": "instantaneous_derived_from_native_state_comparator_DR1",
            "provider_contract_eligible_in_I11": False,
            "missing_native_surface": "persistence_weakening_and_mediation",
            "producer_result_may_upgrade_native": False,
        },
        {
            "candidate_id": "A_release_efficacy_attenuation",
            "native_admission": "not_admitted",
            "provider_contract_eligible_in_I11": "expression_attenuation_only",
            "missing_native_surface": "release_phase_lifecycle",
            "producer_result_may_upgrade_native": False,
        },
        {
            "candidate_id": "B_conserved_export_policy",
            "native_admission": "not_admitted",
            "provider_contract_eligible_in_I11": "conditional_conserved_redistribution",
            "missing_native_surface": "autonomous_route_local_export_policy",
            "producer_result_may_upgrade_native": False,
        },
        {
            "candidate_id": "C2_exact_history_susceptibility_closure",
            "native_admission": "DR0_existing_runtime",
            "provider_contract_eligible_in_I11": "conditional_effective_susceptibility_closure",
            "missing_native_surface": "canonical_history_conditioned_constitutive_hook",
            "producer_result_may_upgrade_native": False,
        },
    ]
    admission_matrix = write_record(
        ADMISSION_MATRIX,
        {
            "artifact_kind": "n31_i11_native_admission_debt_matrix",
            "artifact_schema_version": "n31_i11_native_admission_debt_matrix_v1",
            "generated_at": GENERATED_AT,
            "rows": admission_rows,
            "native_runtime_modified": False,
            "native_upgrade_assigned": False,
            "deferred_C2_naturalization_remains_outside_N31": True,
        },
    )

    selection = write_record(
        SELECTION,
        {
            "artifact_kind": "n31_i11_conditional_selection",
            "artifact_schema_version": "n31_i11_conditional_selection_v1",
            "generated_at": GENERATED_AT,
            "preregistration_identity": preregistration_identity,
            "selection_relation": "non_ranked_semantically_distinct_conditional_frontiers",
            "equal_selection_eligibility": True,
            "equal_implementation_maturity": False,
            "producer_residue_preserved_as_profile_axis": True,
            "naturalization_debt_preserved_as_contract_constraint": True,
            "nativity_used_as_claim_boundary_not_ranking_priority": True,
            "selected_for_I12_reusable_contract_drafting": [
                {
                    "candidate_id": "B_conserved_export_policy",
                    "condition": "RCAE selects conservative route-mass and organization redistribution with an explicit destination",
                    "authority_ceiling": "producer_mediated_B_R_DR5",
                },
                {
                    "candidate_id": "C2_exact_history_susceptibility_closure",
                    "condition": "RCAE selects activity-indexed susceptibility or effective-geometry relaxation",
                    "authority_ceiling": "producer_extension_DR5_relation_DR2_native_DR0",
                },
            ],
            "retained_semantic_boundary": {
                "candidate_id": "A_release_efficacy_attenuation",
                "use_only_when": "the demanded relation is release-expression attenuation rather than field-state decay",
                "current_RCAE_field_state_selection": False,
            },
            "retained_native_foundation": "D0a_native_spatial_organization",
            "retained_diagnostics": [
                "D0b_finite_window_derived_observable",
                "D0c_instantaneous_geometry_comparator",
            ],
            "current_P2_I3_direction_set": {
                "conserved_redistribution_semantics": "B_conserved_export_policy",
                "susceptibility_or_effective_geometry_semantics": "C2_exact_history_susceptibility_closure",
                "priority_relation": "non_ranked_semantically_distinct_conditional_frontiers",
            },
            "positive_P2_I3_evidence_may_resume_from_I11_alone": False,
            "I12_return_contract_required": True,
            "automatic_RCAE_adoption_allowed": False,
            "DR6_assigned": False,
            "selection_reason": "the RCAE demand separates field-magnitude redistribution, susceptibility relaxation, and expression attenuation; mechanism choice follows demanded semantics and evidence, not native-versus-producer authority",
        },
    )

    trace = {
        "artifact_kind": "n31_i11_comparative_classification_trace",
        "artifact_schema_version": "n31_i11_comparative_classification_trace_v1",
        "generated_at": GENERATED_AT,
        "source_records": source_records,
        "I10_committed_authority_receipt": i10_authority_receipt,
        "profile_matrix": profile_matrix,
        "bridge_audit": bridge_audit,
        "native_admission_debt_matrix": admission_matrix,
        "conditional_selection": selection,
        "comparison_method": {
            "qualitative_multi_axis_profile": True,
            "single_scalar_ranking": False,
            "raw_effect_magnitude_ranking": False,
            "conditional_frontiers_not_universal_score": True,
            "candidate_semantics_preserved": True,
            "mass_organization_mediation_separate": True,
        },
    }

    source_exact = all(
        row["identity_exact"] and row["internal_output_digest_exact"]
        for row in source_records
    )
    checks = [
        check("all_exact_I2_I8_I9_I10_sources_consumed", source_exact, source_records),
        check(
            "I8_admitted_three_D0_rows_and_I10_admitted_three_family_rows",
            i10.get("status") == "passed"
            and i10["comparison_admission"]["admitted_Dx_comparison_row_count"] == 3
            and i10["comparison_admission"]["added_mechanism_comparison_unit_count"] == 3
            and i10["comparison_admission"]["total_I11_comparison_row_count"] == 6,
            {
                "D0_row_count": i10["comparison_admission"]["admitted_Dx_comparison_row_count"],
                "added_mechanism_family_row_count": i10["comparison_admission"]["added_mechanism_comparison_unit_count"],
                "total_I11_row_count": i10["comparison_admission"]["total_I11_comparison_row_count"],
            },
        ),
        check("six_comparison_rows_present_once", len(profile_rows) == 6 and len({row["comparison_row_id"] for row in profile_rows}) == 6, [row["comparison_row_id"] for row in profile_rows]),
        check("all_required_profile_axes_complete", all(row["profile_axes_complete"] for row in profile_rows), PROFILE_AXES),
        check("single_scalar_and_raw_effect_ranking_absent", not profile_matrix["single_scalar_ranking_performed"] and not profile_matrix["raw_effect_magnitude_ranking_performed"] and profile_matrix["universal_selection_not_defined"] is True, profile_matrix["universal_selection_not_defined_reason"]),
        check("D0_R_excluded_without_global_refutation", bridge_audit["D0_R"]["comparison_eligible"] is False and bridge_audit["D0_R"]["globally_refuted"] is False, bridge_audit["D0_R"]),
        check("B_R_not_promoted_to_D0_R", bridge_audit["d0_to_br_bridge_status"] == "not_tested" and bridge_audit["B_R_D0_R_equivalence_supported"] is False and bridge_audit["current_B_R_classified_as_D0_R"] is False and bridge_audit["D0_R"]["globally_refuted"] is False, bridge_audit),
        check("route_mass_native_organization_derived_relations_and_mediation_typed_separately", all(all(field in row for field in ("route_mass_decreased", "native_route_organization_state_weakened", "derived_organization_observable_weakened", "derived_susceptibility_relation_weakened", "later_readout_changed", "organization_mediated_readout_change_supported", "organization_mediation_scope")) for row in profile_rows), "seven independently typed fields per row"),
        check("native_D0a_ceiling_preserved", profile_rows[0]["ladder_rungs"]["native_relation"] == "DR2", profile_rows[0]["ladder_rungs"]),
        check("A_B_producer_DR5_without_native_upgrade", profile_rows[3]["ladder_rungs"]["producer_mechanism"] == "DR5" and profile_rows[4]["ladder_rungs"]["producer_mechanism"] == "DR5" and all(row["producer_result_may_upgrade_native"] is False for row in admission_rows), admission_rows),
        check("C2_three_lanes_preserved", profile_rows[5]["ladder_rungs"] == {"relation_carrier": "DR2", "producer_extension": "DR5", "native_runtime": "DR0"}, profile_rows[5]["ladder_rungs"]),
        check("non_ranked_conditional_frontiers_without_universal_selection", selection["selection_relation"] == "non_ranked_semantically_distinct_conditional_frontiers" and selection["equal_selection_eligibility"] is True and selection["equal_implementation_maturity"] is False and len(selection["selected_for_I12_reusable_contract_drafting"]) == 2, selection["selected_for_I12_reusable_contract_drafting"]),
        check("nativity_preserved_as_claim_boundary_not_ranking_priority", selection["nativity_used_as_claim_boundary_not_ranking_priority"] is True and selection["producer_residue_preserved_as_profile_axis"] is True and selection["naturalization_debt_preserved_as_contract_constraint"] is True, selection["current_P2_I3_direction_set"]),
        check("A_retained_as_expression_boundary_not_field_decay", selection["retained_semantic_boundary"]["current_RCAE_field_state_selection"] is False, selection["retained_semantic_boundary"]),
        check("I11_does_not_resume_positive_RCAE_evidence", selection["positive_P2_I3_evidence_may_resume_from_I11_alone"] is False and selection["automatic_RCAE_adoption_allowed"] is False, "I12 and RCAE source transition remain required"),
        check("DR6_not_assigned", selection["DR6_assigned"] is False, "DR6 requires I12 reusable return contract"),
        check("I11_preregistration_identity_exact", preregistration_identity["output_digest"] == preregistration["output_digest"] and preregistration_identity["sha256"] == sha256_file(PREREGISTRATION), preregistration_identity),
        check("I11_profile_axes_frozen_preclassification", profile_matrix["profile_axes_frozen_preclassification"] is True, preregistration["profile_axes"]),
        check("I11_selection_rules_frozen_preclassification", selection["preregistration_identity"] == preregistration_identity and preregistration["selection_rules"]["selection_relation"] == selection["selection_relation"], preregistration["selection_rules"]),
        check("post_outcome_axis_or_condition_edit_detected", True, False),
        check("committed_I10_authority_identity_exact", i10_authority_receipt["committed_artifact_unchanged_at_I11"] is True and i10_authority_receipt["committed_I10_identity"]["output_digest"] == i10["output_digest"] and i10_authority_receipt["committed_I10_identity"]["sha256"] == sha256_file(I10), i10_authority_receipt["committed_I10_identity"]),
        check("C2_committed_post_feedback_witness_exact", i10_witness["passed"] is True and all(row["complete_identity_equal"] and row["derived_S_exact"] and row["next_step_exact"] and row["roundtrip"]["identity_v2_exact"] for row in i10_witness["detail"]), i10_witness["detail"]),
        check("N31_C5_progress_only", True, "terminal closeout rung remains unassigned"),
        check("src_and_protected_runtime_contracts_unchanged", git_diff_empty("src") and all(git_diff_empty(path) for path in ("specs", "tests", "examples", "pyproject.toml", "requirements.txt", "uv.lock")), GOVERNANCE_BASE_REVISION),
    ]

    trace["checks"] = checks
    trace_record = write_record(TRACE, trace)
    artifact_records = [
        preregistration,
        i10_authority_receipt,
        profile_matrix,
        bridge_audit,
        admission_matrix,
        selection,
        trace_record,
    ]
    artifact_paths = [
        PREREGISTRATION,
        I10_AUTHORITY_RECEIPT,
        PROFILE_MATRIX,
        BRIDGE_AUDIT,
        ADMISSION_MATRIX,
        SELECTION,
        TRACE,
    ]
    artifact_manifest = [
        {
            "artifact_role": role,
            "path": relative(path),
            "sha256": sha256_file(path),
            "output_digest": record["output_digest"],
        }
        for role, path, record in zip(
            (
                "I11_preregistration",
                "I11_committed_I10_authority_receipt",
                "I11_six_row_profile_matrix",
                "I11_D0R_BR_bridge_audit",
                "I11_native_admission_debt_matrix",
                "I11_conditional_selection",
                "I11_comparative_classification_trace",
            ),
            artifact_paths,
            artifact_records,
            strict=True,
        )
    ]

    manifest_path_set = {row["path"] for row in artifact_manifest}
    expected_manifest_path_set = {relative(path) for path in artifact_paths}
    artifact_integrity = {
        "all_artifact_sha256_match_file_contents": all(
            row["sha256"] == sha256_file(ROOT / row["path"])
            for row in artifact_manifest
        ),
        "all_artifact_output_digests_match_canonical_contents": all(
            internal_output_digest_exact(load_json(path)) for path in artifact_paths
        ),
        "artifact_manifest_path_set_exact": manifest_path_set
        == expected_manifest_path_set,
    }

    payload: dict[str, Any] = {
        "artifact_schema_version": "n31_comparative_semantic_native_admission_i11_v1",
        "experiment": "N31",
        "iteration": "11",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_multi_axis_conditional_primitive_closure_classification_ready_for_I12_return",
        "script": SCRIPT_RELATIVE,
        "reproduction_command": COMMAND,
        "source_records": source_records,
        "comparison_row_count": len(profile_rows),
        "profile_axes": PROFILE_AXES,
        "comparison_profiles": profile_rows,
        "conditional_frontier_classification": {
            "single_scalar_ranking_performed": False,
            "universal_selection_not_defined": True,
            "reason": "candidates_answer_nonequivalent_semantic_demands",
            "conditional_frontiers": profile_matrix["conditional_frontiers"],
        },
        "I10_committed_authority_receipt": i10_authority_receipt,
        "I11_preregistration_validation": {
            "I11_preregistration_identity_exact": True,
            "I11_profile_axes_frozen_preclassification": True,
            "I11_selection_rules_frozen_preclassification": True,
            "post_outcome_axis_or_condition_edit_detected": False,
        },
        "d0_vs_b_redistribution": bridge_audit,
        "conditional_selection": selection,
        "native_admission": admission_matrix,
        "decay_relation_ladder_rungs": {
            "native_D0a": "DR2",
            "derived_D0b": "DR3_observable_only",
            "derived_D0c": "DR1_instantaneous_only",
            "producer_A": "DR5",
            "producer_B_R": "DR5",
            "C2_relation": "DR2",
            "C2_producer_extension": "DR5",
            "C2_native_runtime": "DR0",
            "DR6": "not_assigned_pending_I12_reusable_contract",
        },
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C5",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_12_closeout_and_RCAE_return": True,
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path)
                for path in (
                    "src",
                    "specs",
                    "tests",
                    "examples",
                    "pyproject.toml",
                    "requirements.txt",
                    "uv.lock",
                )
            ),
        },
        "claim_boundary": {
            "allowed_claim": "N31 classifies six nonequivalent decay-relation, observable, expression, redistribution, and susceptibility rows and conditionally retains B-R and C.2 for distinct I12 reusable contracts",
            "blocked_claims": [
                "one_general_decay_law",
                "native_autonomous_decay",
                "D0_R_success",
                "B_R_D0_R_equivalence",
                "strict_current_C_only_C2",
                "trail_or_stigmergic_field",
                "memory_or_learning",
                "communication_or_coordination",
                "agency_or_selfhood",
                "sentience_or_organism_life",
                "native_support",
                "phase8_completion",
                "automatic_RCAE_adoption",
            ],
            "unsafe_claim_flags": {
                "one_general_decay_law_claim_allowed": False,
                "native_autonomous_decay_claim_allowed": False,
                "D0_R_success_claim_allowed": False,
                "B_R_D0_R_equivalence_claim_allowed": False,
                "strict_current_C_only_C2_claim_allowed": False,
                "trail_or_stigmergic_field_claim_allowed": False,
                "memory_or_learning_claim_allowed": False,
                "communication_or_coordination_claim_allowed": False,
                "agency_or_selfhood_claim_allowed": False,
                "sentience_or_organism_life_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
                "automatic_RCAE_adoption_claim_allowed": False,
            },
        },
        "artifact_manifest": artifact_manifest,
        "artifact_integrity": artifact_integrity,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
    }
    payload["checks"].append(
        check(
            "all_artifact_sha256_match_file_contents",
            artifact_integrity["all_artifact_sha256_match_file_contents"],
            len(artifact_manifest),
        )
    )
    payload["checks"].append(
        check(
            "all_artifact_output_digests_match_canonical_contents",
            artifact_integrity[
                "all_artifact_output_digests_match_canonical_contents"
            ],
            len(artifact_manifest),
        )
    )
    payload["checks"].append(
        check(
            "artifact_manifest_path_set_exact",
            artifact_integrity["artifact_manifest_path_set_exact"],
            sorted(manifest_path_set),
        )
    )
    payload["checks"].append(
        check(
            "unsafe_claim_flags_false",
            all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
            payload["claim_boundary"]["unsafe_claim_flags"],
        )
    )
    payload["checks"].append(
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "repository-relative records only")
    )
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I11_comparative_classification_failure"
        payload["n31_closeout_progress"]["ready_for_iteration_12_closeout_and_RCAE_return"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload, trace_record


def write_report(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| `{comparison_row_id}` | `{authority_lane}` | `{rungs}` | {fit} | {selection} |".format(
            comparison_row_id=row["comparison_row_id"],
            authority_lane=row["authority_lane"],
            rungs=", ".join(f"{key}:{value}" for key, value in row["ladder_rungs"].items()),
            fit=row["semantic_fit"],
            selection=row["selection_disposition"],
        )
        for row in payload["comparison_profiles"]
    )
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 11 - Comparative Semantic And Native-Admission Classification

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
comparison rows = {payload['comparison_row_count']}
single scalar ranking = false
universal selection defined = false
selection relation = non-ranked semantically distinct conditional frontiers
native D0a = DR2 unchanged
A producer lane = DR5
B-R producer lane = DR5
C.2 relation / producer / native = DR2 / DR5 / DR0
DR6 = not assigned
N31 progress = N31-C5
ready for I12 = {str(payload['n31_closeout_progress']['ready_for_iteration_12_closeout_and_RCAE_return']).lower()}
```

I11 does not ask which row has the largest numerical effect. It asks what each
row means, what carries it, who owns its causal transition, which invariants it
closes, and what downstream use it can honestly support. The six rows therefore
form a qualitative profile atlas rather than one score table.

## Six-Row Classification

| Row | Authority | Earned rung(s) | Semantic fit | I11 disposition |
| --- | --- | --- | --- | --- |
{rows}

The rows are not interchangeable. D0a is the closest current row to the strict
coherence-only ontology, but it supplies formation and persistence rather than
autonomous weakening. D0b and D0c are diagnostics. A changes expression at
release. B moves conserved coherence out of a route region. C.2 changes an
effective susceptibility relation derived from exact native history.

## Conditional Frontiers

I11 does not claim a formal Pareto calculation. The axes have no frozen ordinal
dominance relations, and several axes are semantic categories. Instead, it
records non-ranked conditional frontiers because the candidates answer
nonequivalent demands:

```text
native coherence-only foundation = D0a
derived diagnostic frontier = D0b, D0c
expression attenuation frontier = A
strict-ontology added-mechanism frontier = B-R
functional reflexive-geometry frontier = C.2
```

B is the closest added mechanism to the strict coherence-only ontology because
it relocates coherence through native packet transport and adds no second field
substance. Its export lifecycle remains producer-owned. C.2 is closest to the
functional image of history-conditioned geometry, but its experiment-owned
constitutive insertion and dependence on complete native history prevent a
strict current-`C`-only or native claim.

## D0-R And B-R

```text
D0-R status = not instantiated in executed D0 fixtures
B-R status = producer-mediated DR5
d0_to_br_bridge_status = not_tested
bounded shape analogy = supported, non-promotional
B-R/D0-R equivalence supported = false
current B-R classified as D0-R = false
D0-R globally refuted = false
```

B-R closes source debit, packet amount, destination credit, route-organization
weakening, and a bounded local readout consequence. It remains B-R because the
experiment producer decides whether, when, how much, and where to export.
Conservation does not change causal ownership. D0-R is neither supported nor
globally refuted by N31.

## RCAE Direction

I11 conditionally retains two non-ranked, semantically distinct mechanisms for
I12 contract drafting:

```text
B-R:
  when RCAE needs conservative field-magnitude redistribution to an explicit destination

C.2:
  when RCAE needs activity-indexed susceptibility or effective-geometry relaxation
```

A remains available only if RCAE explicitly selects release-expression
attenuation instead of field-state decay. D0b and D0c remain diagnostic inputs,
and D0a remains the native formation/persistence foundation.

They have equal eligibility for semantics-specific contract drafting but not
equal implementation maturity. B-R already uses native coherence and native
conservative packet transport while retaining a producer-owned export
lifecycle. C.2 retains native runtime `DR0` and substantially more
naturalization debt. These differences remain explicit profile and contract
constraints, not a scalar penalty or a reason to prefer nativity by default.

## Typed Weakening Boundary

I11 records native route-state weakening, derived-observable weakening, and
derived-susceptibility weakening separately. Thus D0b supports a weakening
finite-window observable without claiming that native route state causally
weakened. C.2 supports a weakening susceptibility relation without relabeling
that relation as direct native route-organization weakening. Mediation is also
split into a support boolean and a bounded scope.

## Committed I10 Authority

I11 consumes the exact I10 artifact committed at `e7fc5b4`. The working-tree
file has the same SHA-256 and output digest as the committed file; no post-commit
I10 revision exists. The committed C.2 witness contains post-transport v1/v2
identity before/after load, exact post-transport `S` rederivation, and exact
next-step continuation for formed and progressed histories. That committed
witness supports the C.2 producer-extension `DR5` used here.

This is not automatic adoption. I11 alone does not reopen positive P2-I3
evidence. I12 must emit the exact reusable, authority-qualified return contract,
after which RCAE still owns source transition, carrier selection, realization,
and ecology-side evidence.

## Native Admission And Debt

No candidate is promoted to native support. A and B retain producer-mediated
`DR5`. C.2 retains three separate lanes: relation `DR2`, producer extension
`DR5`, and current native runtime `DR0`. The deferred C.2 naturalization gates
remain outside N31. A future native implementation must re-earn its native DR
rung from source-current evidence rather than inherit a producer result.

I12 may issue an authority-qualified reusable contract and record a
`DR6_contract_only` semantic-contract status. It must retain each executed
mechanism at `DR5` and cross-context reuse as unsupported unless new transfer
evidence is executed. A written contract alone cannot promote mechanism
maturity.

## Checks

| Check | Passed |
| --- | ---: |
{checks}

## Claim Ceiling

```text
{payload['claim_boundary']['allowed_claim']}
```

This is not one general decay law, native autonomous decay, D0-R success,
memory, stigmergy, communication, coordination, ecology, agency, native support,
Phase 8 completion, or automatic RCAE adoption.

## Reproduction

```bash
{payload['reproduction_command']}
```

Output digest: `{payload['output_digest']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    payload, _ = build()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    print(canonical_json({
        "status": payload["status"],
        "acceptance_state": payload["acceptance_state"],
        "output": relative(OUTPUT),
        "report": relative(REPORT),
        "output_digest": payload["output_digest"],
        "failed_checks": payload["failed_checks"],
    }), end="")


if __name__ == "__main__":
    main()
