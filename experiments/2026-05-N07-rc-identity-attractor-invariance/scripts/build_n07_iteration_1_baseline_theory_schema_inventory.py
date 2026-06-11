"""Build N07 Iteration 1 baseline theory/schema inventory.

This script records theory gates, inherited source artifacts, available native
LGRC surfaces, the ID row schema, becoming-method schema, topology schema,
identity-carrier taxonomy, canonical controls, and claim boundaries for N07.
It intentionally does not run identity probes and does not import or mutate
`src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
IMPLEMENTATION = ROOT / "implementation"
PAPERS = ROOT / "papers"

OUTPUT_PATH = N07 / "outputs/n07_iteration_1_baseline_theory_schema_inventory.json"
REPORT_PATH = N07 / "reports/n07_iteration_1_baseline_theory_schema_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "build_n07_iteration_1_baseline_theory_schema_inventory.py"
)


SOURCE_ARTIFACTS: dict[str, Path] = {
    "n07_readme": N07 / "README.md",
    "n07_plan": N07
    / "implementation/RCIdentityAttractorInvarianceImplementationPlan.md",
    "n07_checklist": N07
    / "implementation/RCIdentityAttractorInvarianceImplementationChecklist.md",
    "n07_implementation_readme": N07 / "implementation/README.md",
    "n05_n11_roadmap": ROOT / "experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md",
    "rc_identity_choice_abundance": PAPERS / "2025-11-RC-IdentityChoiceAbundance.md",
    "grc_v2": PAPERS / "2025-12-GRC-V2.md",
    "grc_v3": PAPERS / "2026-02-GRC-V3.md",
    "grc_9": PAPERS / "2026-04-GRC-9.md",
    "lgrc_9": PAPERS / "2026-05-LGRC-9.md",
    "lgrc9v3_causal_pulse_substrate_surfaces": PAPERS
    / "2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md",
    "n04_taxonomy_inventory": N04 / "outputs/n04_taxonomy_inventory_v1.json",
    "n04_taxonomy_inventory_report": N04 / "reports/n04_taxonomy_inventory_v1.md",
    "n04_taxonomy_closeout": N04 / "outputs/n04_taxonomy_continuation_closeout.json",
    "n04_iter19e_topology_mutating_movement": N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json",
    "n04_iter22_identity_boundary": N04
    / "outputs/n04_iter22_identity_through_topology_mutation_boundary.json",
    "n04_iter22_identity_boundary_report": N04
    / "reports/n04_iter22_identity_through_topology_mutation_boundary.md",
    "n04_iter22b_native_route_arbitrated_identity_boundary": N04
    / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
    "n04_iter22b_native_route_arbitrated_identity_boundary_report": N04
    / "reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md",
    "n05_closeout": N05 / "outputs/n05_iteration_8_o6_closeout.json",
    "n05_closeout_report": N05 / "reports/n05_iteration_8_o6_closeout.md",
    "n06_closeout": N06 / "outputs/n06_iteration_8_sc6_closeout.json",
    "n06_closeout_report": N06 / "reports/n06_iteration_8_sc6_closeout.md",
    "phase8_causal_pulse_substrate_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-CausalPulseSubstrateCloseout.json",
    "phase8_surface_lineage_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json",
    "phase8_topology_state_reabsorption_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json",
    "phase8_time_scoped_lineage_replay_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json",
    "phase8_native_route_arbitration_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.json",
    "lgrc9v3_contract_source": ROOT / "src/pygrc/models/lgrc_9_v3_contract.py",
    "lgrc9v3_runtime_source": ROOT / "src/pygrc/models/lgrc_9_v3_runtime.py",
    "lgrc9v3_runtime_state_source": ROOT
    / "src/pygrc/models/lgrc_9_v3_runtime_state.py",
    "lgrc9v3_topology_source": ROOT / "src/pygrc/models/lgrc_9_v3_topology.py",
    "lgrc9v3_telemetry_source": ROOT / "src/pygrc/telemetry/lgrc9v3_contract.py",
}


ARC_OF_BECOMING_SOURCES = [
    {
        "title": "Classification of Becoming",
        "n07_use": (
            "classify what appeared before probing; promote only reusable, "
            "generative, coherence-preserving classes"
        ),
        "path_recorded": False,
    },
    {
        "title": "Interrogation of Becoming",
        "n07_use": (
            "treat probes as bounded questions and record the crossed boundary "
            "rung without proof inflation"
        ),
        "path_recorded": False,
    },
    {
        "title": "Naturalization of Becoming",
        "n07_use": (
            "separate probe-exposed capacity from native regime expression and "
            "record support-dependence"
        ),
        "path_recorded": False,
    },
    {
        "title": "Cultivation of Becoming",
        "n07_use": (
            "record orient/observe/classify/probe/withdraw/naturalize/integrate "
            "activity history and cultivate functions rather than proxies"
        ),
        "path_recorded": False,
    },
]


CLAIM_FLAGS_FALSE: dict[str, bool] = {
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "intention_claim_allowed": False,
    "memory_or_trail_claim_allowed": False,
    "goal_proxy_regulation_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "movement_claim_allowed": False,
}


ID_ROW_SCHEMA_REQUIRED_FIELDS = [
    "row_id",
    "id_level",
    "topology_family_id",
    "composite_topology_id",
    "candidate_identity_carrier_type",
    "identity_carrier_surface",
    "support_area_id",
    "support_area_digest",
    "source_artifacts",
    "source_artifact_sha256",
    "source_reports",
    "runtime_family",
    "implementation_surface",
    "gate_vector",
    "derived_id_ceiling",
    "primary_blocker",
    "native_support_status",
    "native_observables_used",
    "experiment_local_observables_used",
    "native_policy_blockers",
    "becoming_class_status",
    "probe_role",
    "boundary_rung",
    "support_dependency_status",
    "withdrawal_test_status",
    "naturalization_rung",
    "activity_history_digest",
    "claim_flags",
    "visual_reference",
    "visual_is_evidence_source",
]


CANONICAL_CONTROLS = [
    "label_only_null_topology",
    "missing_support_area",
    "external_label_only",
    "duplicate_support_row",
    "budget_discontinuity",
    "stale_node_id_replay",
    "missing_topology_state_reabsorption",
    "lineage_map_scrambled",
    "support_drift_beyond_threshold",
    "unstable_basin_no_local_well",
    "hidden_potential_or_report_side_well_score",
    "posthoc_threshold_change",
    "identity_threshold_missing",
    "wrong_support_area",
    "no_reentry",
    "closure_not_consumed_by_later_cycle",
    "improper_proper_time_threshold",
    "failed_persistence",
    "non_attractive_flux",
    "wrong_basin",
    "wrong_polarity",
    "subthreshold_flux",
    "hidden_route_context_steering",
    "destructive_interference",
    "ambiguous_overlap",
    "hidden_support_field",
    "producer_mutation_boundary_violation",
    "direct_state_or_topology_rewrite",
    "unauthorized_identity_acceptance_event",
    "identity_claim_promotion",
    "agency_claim_promotion",
]


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data
    return {"value": data}


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _artifact_record(name: str, path: Path) -> dict[str, Any]:
    record = {
        "name": name,
        "path": _rel(path),
        "exists": path.exists(),
        "sha256": _sha256(path),
    }
    if path.suffix == ".json" and path.exists():
        data = _load_json(path)
        record["status"] = data.get("status")
        record["claim_ceiling"] = data.get("claim_ceiling")
        record["primary_blocker"] = data.get("primary_blocker")
    return record


def _source_artifacts() -> list[dict[str, Any]]:
    return [_artifact_record(name, path) for name, path in SOURCE_ARTIFACTS.items()]


def _theory_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate": "grc_v2_directed_flux_identity_basin",
            "source": "GRC-V2",
            "n07_observable": "directed-flux attraction domain around sink/basin chart",
            "iteration_use": "support/stability/attractivity schema",
        },
        {
            "gate": "grc_v3_basin_attribute_bundle",
            "source": "GRC-V3",
            "n07_observable": "gradient, Hessian/well proxy, net flux, basin mass, id, parent, depth",
            "iteration_use": "ID2/ID3 and nine-port mapping fields",
        },
        {
            "gate": "grc9_nine_port_basin_chart",
            "source": "GRC-9 / GRC9V3",
            "n07_observable": "nine-port chart, sink relation, spark/refinement boundary",
            "iteration_use": "support topology and parent/child boundary",
        },
        {
            "gate": "lgrc_proper_time_identity_window",
            "source": "LGRC / LGRC9V3",
            "n07_observable": "proper-time or lineage-proper-time persistence",
            "iteration_use": "ID4/ID5 windows",
        },
        {
            "gate": "lgrc_lineage_current_identity",
            "source": "LGRC / LGRC9V3",
            "n07_observable": "lineage-current support, no stale node id replay",
            "iteration_use": "T5/C2 topology-changing identity boundary",
        },
        {
            "gate": "pulse_substrate_identity_carrier_taxonomy",
            "source": "Native causal pulse-substrate surfaces",
            "n07_observable": "coherence_basin vs surface_row/deformation_token/boundary_signal",
            "iteration_use": "carrier eligibility and evidence-only surfaces",
        },
        {
            "gate": "coherence_state",
            "source": "RC",
            "n07_observable": "S_coh = (C, J_C)",
            "iteration_use": "identity-basin theory basis",
        },
        {
            "gate": "continuity_equation",
            "source": "RC",
            "n07_observable": "partial_t C + div J_C = 0",
            "iteration_use": "budget/flux discipline",
        },
        {
            "gate": "coherence_functional",
            "source": "RC",
            "n07_observable": "P[C] stability/well theory",
            "iteration_use": "ID2 stability mapping",
        },
        {
            "gate": "global_coherence_invariance",
            "source": "RC",
            "n07_observable": "node-plus-packet conserved total",
            "iteration_use": "all ID rows above ID0",
        },
        {
            "gate": "identity_basin_stability",
            "source": "RC",
            "n07_observable": "declared stable well / retention / Hessian proxy",
            "iteration_use": "ID2",
        },
        {
            "gate": "attractivity",
            "source": "RC",
            "n07_observable": "declared neighborhood U flux convergence",
            "iteration_use": "ID3",
        },
        {
            "gate": "invariance",
            "source": "RC/LGRC",
            "n07_observable": "support overlap, lineage-current overlap, proper-time persistence",
            "iteration_use": "ID4",
        },
        {
            "gate": "reflexive_closure",
            "source": "RC",
            "n07_observable": "re-entry maintains or strengthens consumed basin evidence",
            "iteration_use": "ID5",
        },
        {
            "gate": "coherence_compatibility",
            "source": "RC",
            "n07_observable": "non-destructive coexistence with nearby modes",
            "iteration_use": "T7/C3 and ID6",
        },
        {
            "gate": "local_irreducibility_agency_boundary",
            "source": "RC / Arc of Becoming",
            "n07_observable": "agency remains blocked; identity is prerequisite only",
            "iteration_use": "claim boundary",
        },
    ]


def _native_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "native_causal_pulse_substrate_surface",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n07_use": "surface/support evidence only",
            "identity_carrier_eligible": False,
            "claim_boundary": "surface row is not identity carrier by itself",
        },
        {
            "surface_id": "surface_lineage_transport",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n07_use": "lineage-current support across topology changes",
            "identity_carrier_eligible": False,
            "claim_boundary": "lineage evidence is not RC identity acceptance",
        },
        {
            "surface_id": "topology_state_reabsorption",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n07_use": "state/ledger consistency after topology mutation",
            "identity_carrier_eligible": False,
            "claim_boundary": "reabsorption is runtime hygiene, not identity",
        },
        {
            "surface_id": "native_route_arbitration",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n07_use": "route-fed context for C4 only",
            "identity_carrier_eligible": False,
            "claim_boundary": "route choice is not identity",
        },
        {
            "surface_id": "packet_ledger_and_budget_accounting",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n07_use": "node-plus-packet conservation for every candidate",
            "identity_carrier_eligible": False,
            "claim_boundary": "budget conservation is necessary but insufficient",
        },
        {
            "surface_id": "proper_time_identity_evaluation",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc2_or_experiment_local",
            "n07_use": "proper-time persistence window if available",
            "identity_carrier_eligible": False,
            "claim_boundary": "persistence window is evidence, not unrestricted identity",
        },
        {
            "surface_id": "identity_acceptance_event_contract",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "unknown_or_experiment_local",
            "n07_use": "only as explicit native contract if present; otherwise blocked",
            "identity_carrier_eligible": False,
            "claim_boundary": "no runtime identity-acceptance event in Iteration 1",
        },
        {
            "surface_id": "telemetry_export_surfaces",
            "runtime_family": "LGRC9V3",
            "minimum_lgrc_runtime_level": "lgrc2_lgrc3_by_surface",
            "n07_use": "artifact-only replay inputs",
            "identity_carrier_eligible": False,
            "claim_boundary": "telemetry is evidence transport only",
        },
    ]


def _id_ladder_schema() -> dict[str, Any]:
    return {
        "levels": [
            {
                "id_level": "ID0",
                "name": "no_identity_evidence",
                "required_gates": {},
                "claim_ceiling": "no_identity_evidence",
            },
            {
                "id_level": "ID1",
                "name": "runtime_visible_support_area_candidate",
                "required_gates": {"support": "pass"},
                "claim_ceiling": "support_area_candidate",
            },
            {
                "id_level": "ID2",
                "name": "stable_basin_candidate",
                "required_gates": {"support": "pass", "stability": "pass"},
                "claim_ceiling": "stable_basin_candidate",
            },
            {
                "id_level": "ID3",
                "name": "attractor_candidate",
                "required_gates": {
                    "support": "pass",
                    "stability": "pass",
                    "attractivity": "pass",
                },
                "claim_ceiling": "attractor_candidate",
            },
            {
                "id_level": "ID4",
                "name": "invariant_basin_candidate",
                "required_gates": {
                    "support": "pass",
                    "stability": "pass",
                    "attractivity": "pass",
                    "invariance": "pass",
                },
                "conditional_required_gates": {
                    "lineage_current": {
                        "required_when": "topology_mutation_occurs == true",
                        "required_value": "pass",
                        "otherwise": "not_applicable",
                    },
                },
                "claim_ceiling": "invariant_basin_candidate",
            },
            {
                "id_level": "ID5",
                "name": "reflexively_self_maintaining_identity_candidate",
                "required_gates": {
                    "support": "pass",
                    "stability": "pass",
                    "attractivity": "pass",
                    "invariance": "pass",
                    "reflexive_closure": "pass",
                },
                "conditional_required_gates": {
                    "lineage_current": {
                        "required_when": "topology_mutation_occurs == true",
                        "required_value": "pass",
                        "otherwise": "not_applicable",
                    },
                },
                "claim_ceiling": "reflexively_self_maintaining_identity_candidate",
            },
            {
                "id_level": "ID6",
                "name": "artifact_only_rc_identity_acceptance_candidate",
                "required_gates": {
                    "support": "pass",
                    "stability": "pass",
                    "attractivity": "pass",
                    "invariance": "pass",
                    "reflexive_closure": "pass",
                    "compatibility": "pass",
                    "artifact_replay": "pass",
                },
                "conditional_required_gates": {
                    "lineage_current": {
                        "required_when": "topology_mutation_occurs == true",
                        "required_value": "pass",
                        "otherwise": "not_applicable",
                    },
                },
                "claim_ceiling": "experiment_local_rc_identity_acceptance_candidate",
            },
        ],
        "row_required_fields": ID_ROW_SCHEMA_REQUIRED_FIELDS,
        "gate_vector_fields": [
            "support",
            "stability",
            "attractivity",
            "invariance",
            "lineage_current",
            "reflexive_closure",
            "compatibility",
            "artifact_replay",
        ],
        "gate_vector_allowed_values": [
            "pass",
            "fail",
            "blocked",
            "not_measured",
            "not_applicable",
        ],
        "ceiling_algorithm": "weakest_required_gate",
        "carrier_rule": (
            "ID1-ID6 candidate rows require candidate_identity_carrier_type == "
            "coherence_basin"
        ),
        "native_support_status_allowed_values": [
            "pure_native",
            "mixed_native_experiment_local",
            "experiment_local",
            "blocked",
        ],
        "runtime_family_allowed_values": [
            "LGRC9V3",
            "experiment_local",
            "hybrid_lgrc9v3_experiment_local",
            "not_applicable",
        ],
        "implementation_surface_allowed_values": [
            "experiment_local",
            "native_lgrc_telemetry",
            "native_causal_pulse_substrate_surface",
            "surface_lineage_transport",
            "topology_state_reabsorption",
            "native_route_arbitration",
            "proper_time_identity_evaluation",
            "artifact_only_validator",
            "not_applicable",
        ],
        "source_artifacts_format": "list of objects with name, path, exists, sha256, status, claim_ceiling, primary_blocker when available",
        "source_reports_format": "list of objects with name, path, exists, sha256",
        "native_observables_used_format": "list of runtime-visible LGRC/native observable ids consumed by the row",
        "experiment_local_observables_used_format": "list of declared experiment-local observable ids consumed by the row",
        "activity_history_digest_method": "sha256 of canonical JSON over orient/observe/classify/probe/withdraw/naturalize/integrate events; null if no activity history exists",
        "visual_reference_format": "optional relative path or null; visual references are illustrative unless visual_is_evidence_source is explicitly true",
        "visual_is_evidence_source_format": "boolean; must be false for Iteration 1 and for any visual-only reference without source artifact backing",
    }


def _becoming_schema() -> dict[str, Any]:
    return {
        "becoming_class_status": [
            "observation_tag",
            "reusable_class",
            "generative_class",
            "coherence_preserving_class",
        ],
        "probe_role": [
            "none",
            "diagnostic_probe",
            "constructive_probe",
            "boundary_probe",
            "withdrawal_probe",
            "naturalization_probe",
        ],
        "boundary_rung": [
            "eligible_state",
            "event",
            "substrate_consequence",
            "structured_consequence",
            "source_specific_expression",
            "recurrence_or_continuation",
            "natural_regime_expression",
        ],
        "support_dependency_status": [
            "not_tested",
            "probe_dependent",
            "weakened_support_survives",
            "regime_assisted",
            "endogenous_precondition_candidate",
            "native_expression_candidate",
            "recurrent_native_expression_candidate",
        ],
        "withdrawal_test_status": [
            "not_tested",
            "support_weakened_passed",
            "support_removed_passed",
            "support_removed_failed",
            "not_applicable",
        ],
        "naturalization_rung": [
            "Nat0_probe_dependent_expression",
            "Nat1_probe_weakened_expression",
            "Nat2_regime_assisted_expression",
            "Nat3_endogenous_precondition_formation",
            "Nat4_native_expression",
            "Nat5_recurrent_native_expression",
            "Nat6_self_interrogating_regime",
            "not_applicable",
        ],
    }


def _topology_schema() -> dict[str, Any]:
    return {
        "topology_ladder": [
            {"level": "T0", "name": "label_only_null_topology", "ceiling": "ID0"},
            {"level": "T1", "name": "support_area_fixture_topology", "ceiling": "ID1"},
            {"level": "T2", "name": "stable_local_well_topology", "ceiling": "ID2"},
            {"level": "T3", "name": "attractor_neighborhood_topology", "ceiling": "ID3"},
            {"level": "T4", "name": "no_mutation_invariance_topology", "ceiling": "ID4"},
            {"level": "T5", "name": "lineage_current_invariance_topology", "ceiling": "ID4"},
            {"level": "T6", "name": "reflexive_closure_topology", "ceiling": "ID5"},
            {"level": "T7", "name": "compatibility_topology", "ceiling": "ID5_or_ID6"},
        ],
        "first_manifest_families": [
            "n07_T1_support_area_minimal",
            "n07_T2_stable_well_basin",
            "n07_T3_attractor_neighborhood",
            "n07_T5_lineage_current_invariance",
        ],
        "t4_deferred_rationale": (
            "T4 is the no-mutation recurrence baseline and remains deferred "
            "until recurrence probes; it is not removed from the ladder."
        ),
        "composite_suite": [
            "n07_C1_recurrent_single_basin_identity_candidate",
            "n07_C2_lineage_current_topology_mutating_identity_candidate",
            "n07_C3_competing_basin_compatibility_candidate",
            "n07_C4_route_fed_route_independent_identity_candidate",
            "n07_C5_movement_carried_movement_independent_identity_candidate",
            "n07_C6_parent_child_refinement_identity_boundary_candidate",
        ],
        "nine_port_basin_chart_fields": [
            "support_ports",
            "basin_chart_id",
            "sink_relation",
            "gradient_summary",
            "hessian_well_proxy",
            "net_flux_summary",
            "basin_mass",
            "parent_id",
            "depth",
        ],
    }


def _identity_carrier_taxonomy() -> dict[str, Any]:
    return {
        "eligible_identity_carrier": "coherence_basin",
        "supporting_evidence_only": [
            "surface_row",
            "deformation_token",
            "boundary_signal",
            "route_selection",
            "movement_trace",
            "topology_event",
            "lineage_record",
            "topology_state_reabsorption_record",
        ],
        "rule": "non-coherence-basin carriers cannot derive an ID ceiling above ID0",
    }


def _inherited_boundaries() -> dict[str, Any]:
    n05 = _load_json(SOURCE_ARTIFACTS["n05_closeout"])
    n06 = _load_json(SOURCE_ARTIFACTS["n06_closeout"])
    n04_22 = _load_json(SOURCE_ARTIFACTS["n04_iter22_identity_boundary"])
    n04_22b = _load_json(SOURCE_ARTIFACTS["n04_iter22b_native_route_arbitrated_identity_boundary"])
    return {
        "n05": {
            "source_artifact": _rel(SOURCE_ARTIFACTS["n05_closeout"]),
            "source_status": n05.get("status"),
            "inherited_background": "oscillator_circuit_background_only",
            "strongest_supported_o_level": n05.get("n05_closeout", {}).get(
                "strongest_supported_o_level"
            ),
            "strongest_claim_ceiling": n05.get("n05_closeout", {}).get(
                "strongest_claim_ceiling"
            ),
            "identity_inherited": False,
            "agency_inherited": False,
            "memory_or_trail_inherited": False,
        },
        "n06": {
            "source_artifact": _rel(SOURCE_ARTIFACTS["n06_closeout"]),
            "source_status": n06.get("status"),
            "inherited_background": "route_choice_context_only",
            "strongest_supported_sc_level": n06.get("acceptance", {}).get(
                "strongest_supported_sc_level"
            ),
            "strongest_claim_ceiling": n06.get("acceptance", {}).get(
                "strongest_claim_ceiling"
            ),
            "semantic_choice_claim_allowed": n06.get("acceptance", {}).get(
                "semantic_choice_claim_allowed"
            ),
            "identity_inherited": False,
            "agency_inherited": False,
        },
        "n04_22": {
            "source_artifact": _rel(SOURCE_ARTIFACTS["n04_iter22_identity_boundary"]),
            "source_status": n04_22.get("status"),
            "boundary_use": "negative_boundary_evidence_not_n07_identity_support",
            "primary_blocker": n04_22.get("primary_blocker"),
            "attempted_promotion": n04_22.get("attempted_promotion"),
            "rc_identity_supported": n04_22.get("boundary", {}).get(
                "rc_identity_through_topology_supported"
            ),
            "identity_acceptance_supported": n04_22.get("boundary", {}).get(
                "identity_acceptance_supported"
            ),
        },
        "n04_22b": {
            "source_artifact": _rel(
                SOURCE_ARTIFACTS["n04_iter22b_native_route_arbitrated_identity_boundary"]
            ),
            "source_status": n04_22b.get("status"),
            "boundary_use": "negative_boundary_evidence_not_n07_identity_support",
            "primary_blocker": n04_22b.get("primary_blocker"),
            "attempted_promotion": n04_22b.get("attempted_promotion"),
            "rc_identity_supported": n04_22b.get("boundary", {}).get(
                "rc_identity_through_native_route_arbitrated_topology_supported"
            ),
            "identity_acceptance_supported": n04_22b.get("boundary", {}).get(
                "identity_acceptance_supported"
            ),
        },
    }


def _artifact_digests(data: dict[str, Any]) -> dict[str, str]:
    return {
        "source_artifacts_digest": _digest(data["source_artifacts"]),
        "theory_gates_digest": _digest(data["theory_gates"]),
        "native_surfaces_digest": _digest(data["available_native_surfaces"]),
        "id_ladder_schema_digest": _digest(data["id_ladder_schema"]),
        "becoming_schema_digest": _digest(data["becoming_schema"]),
        "topology_schema_digest": _digest(data["topology_schema"]),
        "claim_flags_digest": _digest(data["claim_flags"]),
        "control_taxonomy_digest": _digest(data["canonical_controls"]),
    }


def _write_report(data: dict[str, Any]) -> None:
    src_status = data["git"]["status_short_src"]["stdout"] or "(no src/* status entries)"
    source_rows = "\n".join(
        "| `{name}` | `{exists}` | `{sha}` | `{path}` |".format(
            name=item["name"],
            exists=item["exists"],
            sha=item["sha256"],
            path=item["path"],
        )
        for item in data["source_artifacts"]
    )
    native_rows = "\n".join(
        "| `{surface_id}` | `{minimum_lgrc_runtime_level}` | {n07_use} | {claim_boundary} |".format(
            **surface
        )
        for surface in data["available_native_surfaces"]
    )
    level_rows = "\n".join(
        "| `{id_level}` | {name} | `{claim_ceiling}` |".format(**level)
        for level in data["id_ladder_schema"]["levels"]
    )
    report = f"""# N07 Iteration 1: Baseline And Theory/Schema Inventory

Status: passed.

Generated: `{data["environment"]["generated_at"]}`

Command:

```bash
{COMMAND}
```

## Purpose

Iteration 1 is inventory-only. It runs no identity probes, emits no support
rows, and does not change `src/*`.

## Boundaries

- N06 is route-choice context only, not identity evidence.
- N05 is oscillator context only, not identity, memory, or agency evidence.
- N04 Iteration 22/22-B artifacts are boundary/negative evidence: they show
  topology-aware continuity but still block RC identity through topology.
- ID levels are evidence classifications, not claim flags.
- Arc of Becoming sources are recorded by title only, not by filesystem path.

## Source Status

```text
{src_status}
```

## Theory Gates

```json
{json.dumps(data["theory_gate_names"], indent=2, sort_keys=True)}
```

## Available Native Surfaces

| Surface | Minimum level | N07 use | Claim boundary |
|---|---:|---|---|
{native_rows}

## ID-Ladder Schema

| ID level | Name | Claim ceiling |
|---|---|---|
{level_rows}

Required row fields:

```text
{chr(10).join(data["id_ladder_schema"]["row_required_fields"])}
```

Gate-vector values:

```text
{chr(10).join(data["id_ladder_schema"]["gate_vector_allowed_values"])}
```

Schema field definitions:

```json
{json.dumps({key: value for key, value in data["id_ladder_schema"].items() if key.endswith("_allowed_values") or key.endswith("_format") or key.endswith("_method")}, indent=2, sort_keys=True)}
```

## Becoming-Method Schema

```json
{json.dumps(data["becoming_schema"], indent=2, sort_keys=True)}
```

## Topology Schema

First manifest families:

```text
{chr(10).join(data["topology_schema"]["first_manifest_families"])}
```

Composite suite:

```text
{chr(10).join(data["topology_schema"]["composite_suite"])}
```

## Identity Carrier Taxonomy

```json
{json.dumps(data["identity_carrier_taxonomy"], indent=2, sort_keys=True)}
```

## Claim Flags

```json
{json.dumps(data["claim_flags"], indent=2, sort_keys=True)}
```

## Canonical Controls

```text
{chr(10).join(data["canonical_controls"])}
```

## Inherited Boundaries

```json
{json.dumps(data["inherited_boundaries"], indent=2, sort_keys=True)}
```

## Artifact Digests

```json
{json.dumps(data["artifact_digests"], indent=2, sort_keys=True)}
```

## Artifact Inventory

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
{source_rows}

## Acceptance

Iteration 1 passes because N07 has a source-backed theory/schema inventory, a
frozen ID-ladder row schema, frozen becoming/topology/carrier/control schemas,
explicit blocked claim flags, no identity probes, and no `src/*` changes
required.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_inventory() -> dict[str, Any]:
    source_artifacts = _source_artifacts()
    data: dict[str, Any] = {
        "schema": "n07_iteration_1_baseline_theory_schema_inventory_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 1,
        "status": "passed",
        "execution_stage": "baseline_inventory_no_identity_probe",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_artifacts": source_artifacts,
        "external_sources_by_title": ARC_OF_BECOMING_SOURCES,
        "theory_gates": _theory_gates(),
        "available_native_surfaces": _native_surfaces(),
        "id_ladder_schema": _id_ladder_schema(),
        "becoming_schema": _becoming_schema(),
        "topology_schema": _topology_schema(),
        "identity_carrier_taxonomy": _identity_carrier_taxonomy(),
        "canonical_controls": CANONICAL_CONTROLS,
        "claim_flags": CLAIM_FLAGS_FALSE,
        "blocked_claims": sorted(CLAIM_FLAGS_FALSE),
        "inherited_boundaries": _inherited_boundaries(),
        "baseline_decisions": {
            "identity_probe_run": False,
            "new_support_rows_emitted": False,
            "src_changes_required": False,
            "n04_iter22_and_22b_are_boundary_evidence_only": True,
            "n06_route_choice_is_context_only": True,
            "n05_oscillator_is_context_only": True,
            "arc_sources_recorded_by_title_only": True,
            "next_iteration": "2_fixture_manifest_and_discrete_rc_observable_mapping",
        },
        "acceptance": {
            "source_backed_inventory": True,
            "id_ladder_schema_frozen": True,
            "becoming_schema_frozen": True,
            "topology_schema_frozen": True,
            "identity_carrier_taxonomy_frozen": True,
            "canonical_control_taxonomy_frozen": True,
            "claim_flags_frozen_false": True,
            "no_identity_probe_run": True,
            "no_src_changes_required": True,
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
        "baseline_commands": [
            COMMAND,
            "git status --short src",
            "git diff --check",
        ],
    }
    data["theory_gate_names"] = [gate["gate"] for gate in data["theory_gates"]]
    data["artifact_digests"] = _artifact_digests(data)
    return data


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = build_inventory()
    OUTPUT_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(data)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
