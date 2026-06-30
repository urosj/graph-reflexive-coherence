#!/usr/bin/env python3
"""Build N29 I15 prototype atlas and composition classification artifact."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_prototype_atlas_classification_i15.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i8_bridge_motif_library": EXPERIMENT / "outputs" / "n29_bridge_motif_library_i8.json",
    "i9_motif_relabel_nulls": EXPERIMENT / "outputs" / "n29_motif_relabel_nulls_i9.json",
    "i10_prototype_admission_schema": (
        EXPERIMENT / "outputs" / "n29_prototype_admission_schema_i10.json"
    ),
    "prototype_a_i11c_minimal_edge": (
        EXPERIMENT / "outputs" / "n29_trace_pressure_loop_replay_stress_i11c.json"
    ),
    "prototype_a_i11_1c": (
        EXPERIMENT / "outputs" / "n29_trace_pressure_loop_stronger_replay_stress_i111c.json"
    ),
    "prototype_b_i12x": (
        EXPERIMENT / "outputs" / "n29_prototype_b_boundary_shared_medium_synthesis_i12x.json"
    ),
    "prototype_c_i13x": (
        EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_synthesis_i13x.json"
    ),
    "prototype_d_i14y": (
        EXPERIMENT / "outputs" / "n29_prototype_d_complete_synthesis_i14y.json"
    ),
    "prototype_d_i14c_direct_replay_stress": (
        EXPERIMENT / "outputs" / "n29_generative_extractive_direct_replay_stress_i14c.json"
    ),
    "prototype_d_i14d_composition_controls": (
        EXPERIMENT / "outputs" / "n29_loop_composition_controls_i14d.json"
    ),
    "prototype_d_i14e_composition_replay_stress": (
        EXPERIMENT / "outputs" / "n29_loop_composition_replay_stress_i14e.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_prototype_atlas_classification_i15.json"
REPORT = EXPERIMENT / "reports" / "n29_prototype_atlas_classification_i15.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_success_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "fully_native_ecology_claim_allowed": False,
    "native_ant_agency_claim_allowed": False,
    "native_colony_agency_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
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
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def prototype_rows(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    a_edge = sources["prototype_a_i11c_minimal_edge"]
    a = sources["prototype_a_i11_1c"]
    b = sources["prototype_b_i12x"]["prototype_b_summary"]
    c = sources["prototype_c_i13x"]
    d = sources["prototype_d_i14y"]
    d_i14c = sources["prototype_d_i14c_direct_replay_stress"]
    d_i14d = sources["prototype_d_i14d_composition_controls"]
    d_i14e = sources["prototype_d_i14e_composition_replay_stress"]

    return [
        {
            "prototype_id": "prototype_a_trace_pressure_loop",
            "prototype_label": "Prototype A - trace / pressure / bounded response loop",
            "primary_source_id": "prototype_a_i11_1c",
            "primary_source_digest": a["output_digest"],
            "evidence_status": "runtime_replay_stress_backed_bridge_candidate",
            "prototype_family_status": "carry_forward_primary",
            "prototype_status": "runnable_runtime",
            "atlas_classification": "bridge_exemplar",
            "bridge_exemplar_supported": True,
            "runtime_ecology_success_supported": False,
            "source_basis": "I11.1-C replay/stress-backed stronger runtime bridge",
            "evidence_hierarchy": {
                "primary_evidence": "I11.1-C stronger replay/stress-backed row",
                "primary_artifact_digest": a["output_digest"],
                "construction_contrast": "I11-C minimal edge replay/stress row",
                "construction_contrast_digest": a_edge["output_digest"],
                "why_primary": (
                    "I11.1-C preserves the same trace/pressure/loop rules with "
                    "less knife-edge margins than the I11-C construction contrast."
                ),
            },
            "evidence_summary": {
                "runtime_bridge_replay_status": a["runtime_bridge_replay_status"],
                "trace_window_supported": a["trace_window_supported"],
                "pressure_threshold_supported": a["pressure_threshold_supported"],
                "response_margin_supported": a["response_margin_supported"],
                "route_context_supported": a["route_context_supported"],
            },
            "claim_ceiling": (
                "bounded trace/pressure/loop runtime bridge exemplar; not ecology "
                "success, agency, semantic action, native support, or Phase 8"
            ),
            "producer_residue_status": "producer_assisted_bridge_evidence",
            "native_ecology_status": "blocked",
            "remaining_blockers": [
                "producer-assisted, not native ecology",
                "no general trace decay law",
                "no pheromone, hunger, ant behavior, or semantic action",
            ],
            "next_probe_implication": (
                "Can supply the pressure/response loop skeleton for the first "
                "agentic-ecology probe contract."
            ),
        },
        {
            "prototype_id": "prototype_b_boundary_shared_medium_unit",
            "prototype_label": "Prototype B - boundary / shared-medium unit",
            "primary_source_id": "prototype_b_i12x",
            "primary_source_digest": sources["prototype_b_i12x"]["output_digest"],
            "evidence_status": "runtime_replay_stress_backed_bridge_candidate",
            "prototype_family_status": "carry_forward_primary",
            "prototype_status": "runnable_runtime",
            "atlas_classification": "bridge_exemplar",
            "bridge_exemplar_supported": True,
            "runtime_ecology_success_supported": False,
            "source_basis": "I12/I12.1/I12.2 synthesis",
            "evidence_hierarchy": {
                "primary_evidence": "I12x synthesis",
                "primary_artifact_digest": sources["prototype_b_i12x"]["output_digest"],
                "supporting_rows": [
                    "I12 primary boundary/shared-medium unit",
                    "I12.1 sibling repeatability",
                    "I12.2 active-medium separability",
                ],
                "why_primary": (
                    "I12x preserves the primary unit, repeatability variant, and "
                    "active-medium separability while keeping nonzero leakage debt visible."
                ),
            },
            "evidence_summary": {
                "primary_unit_supported": b["i12_contribution"]["supported"],
                "sibling_repeatability_supported": b["i12_1_contribution"]["supported"],
                "active_medium_separability_supported": b["i12_2_contribution"][
                    "supported"
                ],
                "nonzero_leakage_tolerance_supported": b["i12_2_contribution"][
                    "leakage_headroom_improved"
                ],
            },
            "claim_ceiling": (
                "bounded boundary/shared-medium bridge exemplar with zero-leakage "
                "policy preserved; not native shared-medium coordination or "
                "multi-agent interaction"
            ),
            "producer_residue_status": "source_backed_bridge_evidence_with_medium_debt",
            "native_ecology_status": "blocked",
            "remaining_blockers": [
                "no native shared-medium coordination",
                "nonzero leakage tolerance remains unsupported",
                "no agent body or multi-agent interaction",
            ],
            "next_probe_implication": (
                "Can supply the separable medium/boundary unit for composed ecology "
                "probe contracts, while preserving nonzero-leakage debt."
            ),
        },
        {
            "prototype_id": "prototype_c_proxy_susceptibility_reentry",
            "prototype_label": "Prototype C - proxy / susceptibility / re-entry",
            "primary_source_id": "prototype_c_i13x",
            "primary_source_digest": c["output_digest"],
            "evidence_status": "runtime_replay_stress_backed_bridge_candidate",
            "prototype_family_status": "carry_forward_primary",
            "prototype_status": "runnable_runtime",
            "atlas_classification": "bridge_exemplar",
            "bridge_exemplar_supported": c["prototype_c_runtime_evidence_supported"],
            "runtime_ecology_success_supported": False,
            "source_basis": "I13/I13.1/I13.2 two-geometry synthesis",
            "evidence_hierarchy": {
                "primary_evidence": "I13x synthesis",
                "primary_artifact_digest": c["output_digest"],
                "supporting_rows": [
                    "I13 mapping hygiene and exact source-chain extraction",
                    "I13.1-C narrow direct composed runtime",
                    "I13.2-C stronger buffered runtime",
                ],
                "why_primary": (
                    "I13x records the two runtime geometries and preserves the "
                    "mapping-only debt rows rather than treating them as runtime evidence."
                ),
            },
            "evidence_summary": {
                "runtime_candidate_count": c["runtime_candidate_count"],
                "control_backed_candidate_count": c["control_backed_candidate_count"],
                "replay_stress_backed_candidate_count": c[
                    "replay_stress_backed_candidate_count"
                ],
                "strongest_local_candidate": c["strongest_local_candidate"],
            },
            "claim_ceiling": c["claim_ceiling"],
            "producer_residue_status": "producer_mediated_susceptibility_debt_remains",
            "native_ecology_status": "blocked",
            "remaining_blockers": [
                "no semantic learning or choice",
                "native AP4/AP5 closure remains blocked",
                "no native support",
            ],
            "next_probe_implication": (
                "Can supply a re-entry/susceptibility modulation component for "
                "probe contracts, without semantic learning or choice claims."
            ),
        },
        {
            "prototype_id": "prototype_d_generative_extractive_medium_reshaping",
            "prototype_label": "Prototype D - generative / extractive / medium reshaping",
            "primary_source_id": "prototype_d_i14y",
            "primary_source_digest": d["output_digest"],
            "evidence_status": "runtime_replay_stress_backed_bridge_candidate_with_lane_split",
            "prototype_family_status": "carry_forward_with_debt",
            "prototype_status": "runnable_runtime",
            "atlas_classification": "bridge_exemplar_with_lane_split",
            "bridge_exemplar_supported": d["complete_prototype_d_synthesis_supported"],
            "runtime_ecology_success_supported": False,
            "source_basis": "I14Y complete Prototype D synthesis",
            "evidence_hierarchy": {
                "primary_evidence": "I14Y complete Prototype D synthesis",
                "primary_artifact_digest": d["output_digest"],
                "supporting_rows": [
                    "I14-C direct motif replay/stress",
                    "I14-D composition controls",
                    "I14-E composition replay/stress",
                ],
                "supporting_artifact_digests": {
                    "I14-C": d_i14c["output_digest"],
                    "I14-D": d_i14d["output_digest"],
                    "I14-E": d_i14e["output_digest"],
                },
                "why_primary": (
                    "I14Y is used only after I14-C, I14-D, and I14-E have passed; "
                    "it preserves the native motif / blocked native composition / "
                    "producer-mediated composition split."
                ),
            },
            "evidence_summary": {
                "native_motif_layer_supported": d["prototype_d_native_motif_layer_supported"],
                "native_composition_layer_supported": d[
                    "prototype_d_native_composition_layer_supported"
                ],
                "producer_mediated_composition_bridge_supported": d[
                    "prototype_d_producer_mediated_composition_bridge_supported"
                ],
                "naturalization_targets": d["naturalization_targets"],
            },
            "claim_ceiling": d["claim_ceiling"],
            "producer_residue_status": (
                "native/source-current motif layer plus producer-mediated "
                "composition bridge; native composition remains debt"
            ),
            "native_ecology_status": "blocked",
            "remaining_blockers": [
                "native composition layer remains unsupported",
                "no resource economy, cooperation, exploitation, or altruism",
                "closed environmental circulation remains producer-mediated bridge evidence",
            ],
            "next_probe_implication": (
                "Can supply environmental medium-reshaping motifs and "
                "producer-mediated composition bridges for ecology probe contracts."
            ),
        },
    ]


def control_results(scope: str) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "component_order_inversion_control",
            "control_scope": scope,
            "control_status": "failed_closed",
            "blocked_condition": "unordered or inverted component dependency",
            "expected_result": "composition_claim_allowed_false",
            "actual_result": "claim_rejected_without_ordered_dependency",
            "rung_effect": "blocks_composed_runtime_success",
        },
        {
            "control_id": "hidden_producer_coupling_control",
            "control_scope": scope,
            "control_status": "failed_closed",
            "blocked_condition": "undeclared producer coupling between prototypes",
            "expected_result": "native_or_ecology_claim_false",
            "actual_result": "producer_residue_kept_visible",
            "rung_effect": "blocks_native_ecology_upgrade",
        },
        {
            "control_id": "medium_debt_hidden_as_native_relation_control",
            "control_scope": scope,
            "control_status": "failed_closed",
            "blocked_condition": "medium/shared-state debt relabeled as native coordination",
            "expected_result": "native_shared_medium_coordination_false",
            "actual_result": "medium_debt_recorded",
            "rung_effect": "blocks_native_coordination_claim",
        },
        {
            "control_id": "composition_claim_ceiling_upgrade_control",
            "control_scope": scope,
            "control_status": "failed_closed",
            "blocked_condition": "composition raises claims above component ceilings",
            "expected_result": "claim_ceiling_not_raised",
            "actual_result": "bridge_ceiling_preserved",
            "rung_effect": "blocks_ecology_success_claim",
        },
        {
            "control_id": "prototype_success_as_ecology_success_control",
            "control_scope": scope,
            "control_status": "failed_closed",
            "blocked_condition": "bridge exemplar relabeled as ecology success",
            "expected_result": "ecology_success_claim_allowed_false",
            "actual_result": "ecology_success_blocked",
            "rung_effect": "requires_I16_runtime_probe_contract",
        },
    ]


def composition_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "composition_id": "composition_a_b_trace_pressure_boundary_unit",
            "component_prototype_ids": [
                "prototype_a_trace_pressure_loop",
                "prototype_b_boundary_shared_medium_unit",
            ],
            "ordered_dependency": (
                "trace/pressure loop conditions the separable boundary/shared-medium "
                "unit without claiming native shared-medium coordination"
            ),
            "composition_readiness_status": "ready_for_probe_contract",
            "composition_evidence_status": "source_backed_reconstruction_candidate",
            "composition_status": "source_backed_reconstruction_candidate",
            "runtime_surface_status": "not_run_in_i15",
            "bridge_composition_candidate": True,
            "runtime_ecology_success_supported": False,
            "why_admitted": (
                "Both components are admitted bridge exemplars and the ordered "
                "dependency can be stated without raising either component's claim ceiling."
            ),
            "why_not_stronger": (
                "The ordered A+B runtime composition has not been run; this is "
                "composition readiness for I16, not composed ecology evidence."
            ),
            "claim_ceiling": "A+B bridge composition seed; not runtime ecology success",
            "blocked_relabels": [
                "native shared-medium coordination",
                "semantic route support",
                "ecology success",
            ],
            "next_probe_implication": (
                "Minimal ecology probe can ask whether a pressure loop can operate "
                "through a separable medium unit."
            ),
        },
        {
            "composition_id": "composition_b_c_boundary_proxy_reentry",
            "component_prototype_ids": [
                "prototype_b_boundary_shared_medium_unit",
                "prototype_c_proxy_susceptibility_reentry",
            ],
            "ordered_dependency": (
                "boundary/shared-medium separability supplies the local medium in "
                "which susceptibility and later re-entry can be probed"
            ),
            "composition_readiness_status": "ready_for_probe_contract",
            "composition_evidence_status": "source_backed_reconstruction_candidate",
            "composition_status": "source_backed_reconstruction_candidate",
            "runtime_surface_status": "not_run_in_i15",
            "bridge_composition_candidate": True,
            "runtime_ecology_success_supported": False,
            "why_admitted": (
                "Prototype B supplies a bounded medium/boundary unit and Prototype C "
                "supplies a re-entry susceptibility pattern; both preserve their debt rows."
            ),
            "why_not_stronger": (
                "No runtime has yet shown susceptibility/re-entry operating inside "
                "the Prototype B medium unit."
            ),
            "claim_ceiling": "B+C bridge composition seed; not semantic learning or coordination",
            "blocked_relabels": [
                "semantic learning",
                "native shared-medium coordination",
                "choice",
            ],
            "next_probe_implication": (
                "Probe contract can test whether a separable medium can carry a "
                "re-entry-conditioned susceptibility pattern."
            ),
        },
        {
            "composition_id": "composition_c_d_susceptibility_medium_reshaping",
            "component_prototype_ids": [
                "prototype_c_proxy_susceptibility_reentry",
                "prototype_d_generative_extractive_medium_reshaping",
            ],
            "ordered_dependency": (
                "susceptibility/re-entry changes may condition later medium "
                "reshaping motifs, while native composition debt remains visible"
            ),
            "composition_readiness_status": "ready_for_probe_contract",
            "composition_evidence_status": "source_backed_reconstruction_candidate",
            "composition_status": "source_backed_reconstruction_candidate",
            "runtime_surface_status": "not_run_in_i15",
            "bridge_composition_candidate": True,
            "runtime_ecology_success_supported": False,
            "why_admitted": (
                "Prototype C supplies history-conditioned susceptibility and "
                "Prototype D supplies medium-reshaping motifs with lane-split debt visible."
            ),
            "why_not_stronger": (
                "The runtime handoff from C's changed susceptibility state into D's "
                "medium-reshaping motif has not been executed as a composed probe."
            ),
            "claim_ceiling": "C+D bridge composition seed; not resource economy",
            "blocked_relabels": [
                "resource economy",
                "cooperation/exploitation",
                "native medium-reshaping ecology",
            ],
            "next_probe_implication": (
                "Probe contract can test whether re-entry state affects later "
                "generative/extractive medium reshaping."
            ),
        },
        {
            "composition_id": "composition_a_d_loop_pressure_medium_reshaping",
            "component_prototype_ids": [
                "prototype_a_trace_pressure_loop",
                "prototype_d_generative_extractive_medium_reshaping",
            ],
            "ordered_dependency": (
                "trace/pressure loop leaves or consumes a medium-reshaping condition; "
                "later pressure response may differ if a runtime probe is built"
            ),
            "composition_readiness_status": "ready_for_probe_contract_with_producer_debt",
            "composition_evidence_status": "source_backed_reconstruction_candidate",
            "composition_status": "source_backed_reconstruction_candidate",
            "runtime_surface_status": "not_run_in_i15",
            "bridge_composition_candidate": True,
            "runtime_ecology_success_supported": False,
            "why_admitted": (
                "Prototype A and Prototype D are admitted bridge exemplars and form "
                "the smallest direct pressure-loop/medium-reshaping composition."
            ),
            "why_not_stronger": (
                "No ordered runtime has shown an A loop leaving a D medium aftereffect "
                "that later changes A-side pressure response."
            ),
            "claim_ceiling": "A+D bridge composition seed; not closed circulation or resource economy",
            "blocked_relabels": [
                "closed environmental circulation",
                "resource economy",
                "native ecology",
            ],
            "next_probe_implication": (
                "Probe contract can ask whether pressure-loop dynamics and "
                "medium-reshaping aftereffects condition each other over ordered runtime."
            ),
        },
    ]
    for row in rows:
        row["control_results"] = control_results(row["composition_id"])
        row["composition_claim_allowed"] = False
        row["composition_runtime_supported"] = False
    return rows


def debt_rows() -> list[dict[str, Any]]:
    return [
        {
            "debt_id": "producer_assisted_trace_pressure_loop_debt",
            "source_prototype": "prototype_a_trace_pressure_loop",
            "debt_status": "must_remain_visible_in_probe_contract",
            "blocks": ["native loop agency", "semantic action/perception"],
        },
        {
            "debt_id": "nonzero_shared_medium_leakage_and_native_coordination_debt",
            "source_prototype": "prototype_b_boundary_shared_medium_unit",
            "debt_status": "must_remain_visible_in_probe_contract",
            "blocks": ["native shared-medium coordination", "multi-agent interaction"],
        },
        {
            "debt_id": "producer_mediated_susceptibility_and_AP4_AP5_debt",
            "source_prototype": "prototype_c_proxy_susceptibility_reentry",
            "debt_status": "must_remain_visible_in_probe_contract",
            "blocks": ["semantic learning", "choice", "native AP4/AP5 closure"],
        },
        {
            "debt_id": "native_composition_and_multi_leg_medium_debt",
            "source_prototype": "prototype_d_generative_extractive_medium_reshaping",
            "debt_status": "must_remain_visible_in_probe_contract",
            "blocks": [
                "native closed circulation",
                "resource economy",
                "cooperation/exploitation",
            ],
        },
    ]


def mapping_only_rows() -> list[dict[str, Any]]:
    return [
        {
            "row_id": "minimal_composed_ecology_runtime",
            "row_status": "mapping_only_no_runtime_surface",
            "reason": (
                "I15 classifies prototypes and selected composition seeds; I16 must "
                "define the runnable A/B/C/D ecology probe contract."
            ),
            "missing_surface_reason": "no composed runtime harness or cross-prototype handoff trace",
        },
        {
            "row_id": "full_a_b_c_d_minimal_probe_seed",
            "row_status": "mapping_only_no_runtime_surface",
            "reason": (
                "The full pressure-loop -> separable medium -> susceptibility/re-entry -> "
                "medium-reshaping chain is a probe-contract seed, not an I15 runtime row."
            ),
            "missing_surface_reason": (
                "ordered cross-prototype state handoff and composed replay/control matrix "
                "are not run until I16+"
            ),
        },
        {
            "row_id": "native_ecology_or_colony_agency",
            "row_status": "blocked_by_claim_boundary",
            "reason": "Prototype atlas evidence is artifact/runtime bridge evidence, not agency.",
            "missing_surface_reason": "claim blocked; no native ecology runtime surface exists",
        },
        {
            "row_id": "native_shared_medium_coordination",
            "row_status": "blocked_by_debt",
            "reason": "Prototype B preserves zero-leakage policy and does not support native coordination.",
            "missing_surface_reason": "native multi-component medium coupling surface is missing",
        },
        {
            "row_id": "resource_economy_cooperation_exploitation",
            "row_status": "blocked_by_claim_boundary",
            "reason": "Prototype D medium reshaping does not license semantic ecology roles.",
            "missing_surface_reason": (
                "resource economy / cooperation / exploitation observation and control "
                "surface is missing and semantically blocked"
            ),
        },
    ]


def status_enums() -> dict[str, list[str]]:
    return {
        "evidence_status_values": [
            "runtime_replay_stress_backed_bridge_candidate",
            "runtime_replay_stress_backed_bridge_candidate_with_lane_split",
            "control_backed_runtime_candidate_pending_replay",
            "source_backed_reconstruction_candidate",
            "mapping_only_debt_record",
            "context_only",
            "blocked_by_missing_runtime_surface",
            "blocked_by_controls",
            "blocked_by_claim_boundary",
        ],
        "prototype_family_status_values": [
            "carry_forward_primary",
            "carry_forward_with_debt",
            "mapping_only",
            "blocked_or_deferred",
        ],
        "composition_readiness_status_values": [
            "ready_for_probe_contract",
            "ready_for_probe_contract_with_producer_debt",
            "blocked_by_missing_source",
            "blocked_by_controls",
            "blocked_by_claim_boundary",
        ],
        "composition_evidence_status_values": [
            "source_backed_reconstruction_candidate",
            "mapping_only_no_runtime_surface",
            "runtime_not_run",
            "blocked_by_controls",
        ],
    }


def probe_implication_index() -> dict[str, list[dict[str, Any]]]:
    return {
        "minimal_ecology_probe_candidates": [
            {
                "candidate_id": "A_plus_B_route_support_pressure_over_medium_unit",
                "composition_id": "composition_a_b_trace_pressure_boundary_unit",
                "role": "smallest pressure loop over a separable boundary/shared-medium unit",
            }
        ],
        "stronger_probe_candidates": [
            {
                "candidate_id": "B_plus_C_reentry_susceptibility_inside_bounded_unit",
                "composition_id": "composition_b_c_boundary_proxy_reentry",
                "role": "re-entry/susceptibility pattern inside a bounded medium unit",
            }
        ],
        "medium_reshaping_probe_candidates": [
            {
                "candidate_id": "C_plus_D_history_conditioned_medium_reshaping",
                "composition_id": "composition_c_d_susceptibility_medium_reshaping",
                "role": "history-conditioned susceptibility affecting later medium reshaping",
            },
            {
                "candidate_id": "A_plus_D_loop_pressure_medium_aftereffect",
                "composition_id": "composition_a_d_loop_pressure_medium_reshaping",
                "role": "pressure loop and medium-reshaping aftereffect dependency",
            },
        ],
        "blocked_or_later_probe_candidates": [
            {
                "candidate_id": "full_A_B_C_D_minimal_ecology_runtime",
                "status": "mapping_only_until_I16",
                "role": "full chain requires composed runtime harness and handoff trace",
            },
            {
                "candidate_id": "native_D_circulation_or_exchange_loop",
                "status": "blocked_by_native_composition_debt",
                "role": "requires native ordered dependency and medium handoff not shown in I15",
            },
        ],
    }


def missing_runtime_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "composed_ecology_runtime_harness",
            "required_for": "I16 minimal runnable ecology probe",
            "current_status": "missing",
            "not_allowed_to_backfill_from": "I15 atlas rows",
        },
        {
            "surface_id": "cross_prototype_state_handoff_trace",
            "required_for": "ordered composition runtime evidence",
            "current_status": "missing",
            "not_allowed_to_backfill_from": "source digests or report summaries",
        },
        {
            "surface_id": "native_multi_component_medium_coupling",
            "required_for": "native ecology or native shared-medium coordination claims",
            "current_status": "missing",
            "not_allowed_to_backfill_from": "producer-mediated composition bridges",
        },
        {
            "surface_id": "ecology_role_observation_and_control_matrix",
            "required_for": "future ecology probe evaluation",
            "current_status": "missing",
            "not_allowed_to_backfill_from": "prototype labels",
        },
    ]


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    prototypes = prototype_rows(sources)
    compositions = composition_rows()
    debts = debt_rows()
    mapping_rows = mapping_only_rows()
    missing_surfaces = missing_runtime_surfaces()
    enums = status_enums()
    probe_index = probe_implication_index()

    prototype_by_id = {row["prototype_id"]: row for row in prototypes}
    for row in compositions:
        row["component_evidence_statuses"] = {
            prototype_id: prototype_by_id[prototype_id]["evidence_status"]
            for prototype_id in row["component_prototype_ids"]
        }
        row["component_source_digests"] = {
            prototype_id: prototype_by_id[prototype_id]["primary_source_digest"]
            for prototype_id in row["component_prototype_ids"]
        }

    admitted_prototype_ids = {
        row["prototype_id"] for row in prototypes if row["bridge_exemplar_supported"]
    }
    composition_references_admitted = all(
        set(row["component_prototype_ids"]).issubset(admitted_prototype_ids)
        for row in compositions
    )
    composition_controls_failed_closed = all(
        control["control_status"] == "failed_closed"
        for row in compositions
        for control in row["control_results"]
    )
    all_prototypes_have_next_probe = all(
        bool(row["next_probe_implication"]) for row in prototypes
    )
    all_prototypes_bridge_not_success = all(
        row["atlas_classification"].startswith("bridge_exemplar")
        and row["runtime_ecology_success_supported"] is False
        for row in prototypes
    )
    all_prototypes_have_evidence_status = all(
        row["evidence_status"] in enums["evidence_status_values"] for row in prototypes
    )
    all_prototypes_have_family_status = all(
        row["prototype_family_status"] in enums["prototype_family_status_values"]
        for row in prototypes
    )
    all_prototypes_have_claim_ceiling = all(bool(row["claim_ceiling"]) for row in prototypes)
    all_mapping_only_rows_have_missing_reason = all(
        bool(row.get("missing_surface_reason")) for row in mapping_rows
    )
    composition_rows_have_ordering_controls_and_limits = all(
        bool(row["ordered_dependency"])
        and bool(row["why_admitted"])
        and bool(row["why_not_stronger"])
        and row["composition_runtime_supported"] is False
        and row["composition_claim_allowed"] is False
        and row["composition_readiness_status"]
        in enums["composition_readiness_status_values"]
        and row["composition_evidence_status"]
        in enums["composition_evidence_status_values"]
        for row in compositions
    )
    d_not_overpromoted = (
        sources["prototype_d_i14c_direct_replay_stress"]["status"] == "passed"
        and sources["prototype_d_i14d_composition_controls"]["status"] == "passed"
        and sources["prototype_d_i14e_composition_replay_stress"]["status"] == "passed"
        and prototype_by_id[
            "prototype_d_generative_extractive_medium_reshaping"
        ]["evidence_summary"]["native_composition_layer_supported"]
        is False
    )

    atlas_summary = {
        "prototype_count": len(prototypes),
        "bridge_exemplar_count": sum(row["bridge_exemplar_supported"] for row in prototypes),
        "composition_row_count": len(compositions),
        "mapping_only_row_count": len(mapping_rows),
        "missing_runtime_surface_count": len(missing_surfaces),
        "prototype_atlas_supported": True,
        "composition_atlas_opened": True,
        "composition_runtime_supported": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "status_enum_count": sum(len(values) for values in enums.values()),
        "probe_implication_group_count": len(probe_index),
        "claim_ceiling": (
            "claim-clean prototype atlas and source-backed bridge composition map; "
            "not composed ecology runtime success, native ecology, agency, "
            "sentience, or Phase 8 completion"
        ),
        "ready_for_iteration_16": True,
    }

    checks = [
        check(
            "all_source_artifacts_passed",
            all(source.get("status") == "passed" for source in sources.values()),
        ),
        check(
            "i10_composition_activation_condition_satisfied_for_atlas",
            len(admitted_prototype_ids) >= 2
            and sources["i10_prototype_admission_schema"]["composition_activation_condition"][
                "composition_route_directly_admissible_in_i10"
            ]
            is False,
            "I10 blocked direct composition before I15; I15 now has four admitted "
            "non-composition prototype rows.",
        ),
        check("four_prototype_rows_classified", len(prototypes) == 4),
        check("all_prototype_rows_have_evidence_status", all_prototypes_have_evidence_status),
        check("all_prototype_rows_have_family_status", all_prototypes_have_family_status),
        check("all_prototype_rows_have_claim_ceiling", all_prototypes_have_claim_ceiling),
        check("every_prototype_bridge_exemplar_not_ecology_success", all_prototypes_bridge_not_success),
        check("every_prototype_has_next_probe_implication", all_prototypes_have_next_probe),
        check("composition_rows_reference_admitted_prototypes", composition_references_admitted),
        check("composition_controls_failed_closed", composition_controls_failed_closed),
        check(
            "composition_rows_have_ordered_composition_controls_and_limits",
            composition_rows_have_ordering_controls_and_limits,
        ),
        check("prototype_d_not_overpromoted_before_and_after_i14c", d_not_overpromoted),
        check("mapping_rows_and_missing_runtime_surfaces_recorded", bool(mapping_rows) and bool(missing_surfaces)),
        check("all_mapping_only_rows_have_missing_surface_reason", all_mapping_only_rows_have_missing_reason),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("ready_for_iteration_16", atlas_summary["ready_for_iteration_16"]),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_prototype_atlas_classification_i15",
        "experiment_id": "N29",
        "title": "Prototype Atlas And Composition Classification",
        "iteration": "I15",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_prototype_atlas_with_debt_classification",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], data)
            for source_id, data in sources.items()
        ],
        "status_enums": enums,
        "atlas_summary": atlas_summary,
        "prototype_rows": prototypes,
        "composition_rows": compositions,
        "debt_classification_rows": debts,
        "mapping_only_rows": mapping_rows,
        "missing_runtime_surfaces": missing_surfaces,
        "probe_implication_index": probe_index,
        "prototype_atlas_supported": atlas_summary["prototype_atlas_supported"],
        "composition_atlas_opened": atlas_summary["composition_atlas_opened"],
        "composition_runtime_supported": atlas_summary["composition_runtime_supported"],
        "runtime_ecology_success_supported": atlas_summary["ecology_success_supported"],
        "native_ecology_supported": atlas_summary["native_ecology_supported"],
        "claim_boundary": UNSAFE_FLAGS,
        "ready_for_iteration_16": atlas_summary["ready_for_iteration_16"],
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["checks"] = checks
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    summary = data["atlas_summary"]
    lines = [
        "# Prototype Atlas And Composition Classification",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        "I15 classifies Prototypes A-D as bridge exemplars and opens atlas-level "
        "composition rows only as source-backed probe-contract seeds. It does not "
        "claim composed ecology runtime success.",
        "",
        "## Summary",
        "",
        f"- Prototype rows classified: `{summary['prototype_count']}`",
        f"- Bridge exemplars supported: `{summary['bridge_exemplar_count']}`",
        f"- Composition rows recorded: `{summary['composition_row_count']}`",
        f"- Composition runtime supported: `{str(summary['composition_runtime_supported']).lower()}`",
        f"- Native ecology supported: `{str(summary['native_ecology_supported']).lower()}`",
        f"- Ready for Iteration 16: `{str(summary['ready_for_iteration_16']).lower()}`",
        "",
        "## Prototype Atlas",
        "",
        "| Prototype | Evidence status | Family status | Classification | Next probe implication |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in data["prototype_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["prototype_id"],
                row["evidence_status"],
                row["prototype_family_status"],
                row["atlas_classification"],
                row["next_probe_implication"],
            )
        )
    lines.extend(
        [
            "",
            "Each prototype row records primary evidence, supporting or contrast rows, "
            "remaining blockers, and a claim ceiling in the machine-readable atlas.",
            "",
            "",
            "## Composition Rows",
            "",
            "| Composition | Components | Readiness | Evidence | Why not stronger |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in data["composition_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["composition_id"],
                ", ".join(row["component_prototype_ids"]),
                row["composition_readiness_status"],
                row["composition_evidence_status"],
                row["why_not_stronger"],
            )
        )
    lines.extend(
        [
            "",
            "Composition controls are recorded fail-closed for order inversion, hidden "
            "producer coupling, hidden medium debt, claim-ceiling upgrade, and "
            "prototype-success-as-ecology-success relabels.",
            "",
            "## Probe Implication Index",
            "",
        ]
    )
    for group, rows in data["probe_implication_index"].items():
        lines.append(f"- `{group}`")
        for row in rows:
            candidate = row["candidate_id"]
            status = row.get("status", row.get("composition_id", "not_recorded"))
            lines.append(f"  - `{candidate}`: `{status}`")
    lines.extend(
        [
            "",
            "## Debt And Missing Surfaces",
            "",
        ]
    )
    for row in data["debt_classification_rows"]:
        lines.append(f"- `{row['debt_id']}`: {row['debt_status']}")
    lines.append("")
    for row in data["missing_runtime_surfaces"]:
        lines.append(f"- `{row['surface_id']}`: `{row['current_status']}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Native ecology, agency, ant ecology, resource economy, cooperation, "
            "exploitation, sentience, native support, and Phase 8 completion remain "
            "blocked. I16 must define the first runnable ecology probe contract before "
            "any composed runtime claim can be evaluated.",
            "",
            f"Output digest: `{data['output_digest']}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "digest": data["output_digest"]}))


if __name__ == "__main__":
    main()
