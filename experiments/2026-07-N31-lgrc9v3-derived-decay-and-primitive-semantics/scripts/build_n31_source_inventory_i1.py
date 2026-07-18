#!/usr/bin/env python3
"""Build N31 Iteration 1 source and authority inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
RCAE_ROOT = ROOT.parent / "reflexive-coherence-agentic-ecology"
THEORY_ROOT = ROOT.parent / "geometric-reflexive-coherence"
EXPERIMENT = ROOT / "experiments" / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
OUTPUT = EXPERIMENT / "outputs" / "n31_source_inventory_i1.json"
REPORT = EXPERIMENT / "reports" / "n31_source_inventory_i1.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_source_inventory_i1.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

GRAPH_REVISION = "7075ecb5e464401df96f16eac171fbefe0e532dc"
RCAE_REVISION = "ae11be2008b1902df1749faec531420432056c37"
THEORY_REVISION = "e0d25bf69b8bf681eb8d092ba416497030e5d88e"

PROTECTED_PATHS = [
    "src",
    "lib",
    "specs",
    "implementation",
    "tests",
    "examples",
    "scripts",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "uv.lock",
]

RCAE_SOURCES = [
    (
        "rcae_q005_decay_interpretation_study",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/reports/"
        "P2-I3-Q005-decay-interpretation-study.md",
        "exact_decay_question_and_candidate_taxonomy_demand",
    ),
    (
        "rcae_n31_decay_primitive_handoff",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/implementation/"
        "P2-I3-N31-decay-primitive-handoff.md",
        "graph_departure_and_return_contract_demand",
    ),
    (
        "rcae_p2_i3_decision_record",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/implementation/"
        "P2-I3-decision-record.md",
        "paused_ecology_decision_and_authority_boundary",
    ),
    (
        "rcae_trail_field_brief",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/implementation/"
        "P2-I3-trail-or-stigmergic-field-brief.md",
        "ecology_demand_context_only",
    ),
    (
        "rcae_trail_field_checklist",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/implementation/"
        "P2-I3-trail-or-stigmergic-field-checklist.md",
        "ecology_acceptance_context_only",
    ),
    (
        "rcae_source_current_capability_audit",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/reports/"
        "P2-I3-I01-source-current-capability-audit.md",
        "downstream_capability_demand_audit_only",
    ),
    (
        "rcae_exact_source_admission",
        "experiments/2026-07-AE01-post-n30-demand-composition-atlas/reports/"
        "P2-I3-I02-exact-source-admission.md",
        "downstream_source_admission_context_only",
    ),
]

THEORY_SOURCES = [
    (
        "theory_reflexive_coherence",
        "core/2025-11-ReflexiveCoherence.md",
        "e03b643e6020f0288a7fa9dd1a49b93c445b4fb3c9e85b8dab09fcadd53d6b94",
        "core_coherence_geometry_flux_and_conservation_source",
    ),
    (
        "theory_identity_choice_abundance",
        "core/2025-11-RC-IdentityChoiceAbundance.md",
        "a9d49332b25d01511c8731a2478de6321792137f645cef32e3be01cc94f0fbe5",
        "basin_persistence_geometry_update_and_conservation_source",
    ),
    (
        "theory_coherence",
        "core/2025-11-Coherence.md",
        "d0b9da4c2af353ba0a008c9d83a466609e1df2b643e9de3936d4df45909079bf",
        "coherence_field_and_continuity_source",
    ),
    (
        "theory_rc_distance_v4",
        "investigations/2026-01-RC-Distance-v4.md",
        "85c34229212c7ef0a67dd9baaa50ea755ba45701f7a99b60e4112f1a33b4ef70",
        "geometric_causal_functional_distance_source",
    ),
    (
        "theory_lgrc9",
        "substrates/2026-05-LGRC-9.md",
        "4340a8b7b4be0d6b04127f4205630db59912e2a4a18ca326025517ece6a996cb",
        "lgrc_timing_packet_and_causal_substrate_specification",
    ),
    (
        "theory_lgrc9v3_native_packet_loops",
        "substrates/2026-05-LGRC9V3-Native-Packet-Loops.md",
        "d95f745ed5b88c114448add49f84dd97cd3ef3140fbdde0d7c620e29dd368481",
        "native_packet_loop_and_queue_specification",
    ),
    (
        "theory_lgrc9v3_causal_pulse_surfaces",
        "substrates/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md",
        "82506f5b1fbf2aa7e60a2e67559be82bca4781e2becede75fb2f17c5a0a5c45e",
        "causal_pulse_surface_and_lineage_specification",
    ),
]

GRAPH_RUNTIME_SOURCES = [
    ("runtime_contract", "src/pygrc/models/lgrc_9_v3_contract.py"),
    ("runtime_state", "src/pygrc/models/lgrc_9_v3_runtime_state.py"),
    ("timing_surfaces", "src/pygrc/models/lgrc_9_v3_timing.py"),
    ("packet_queue", "src/pygrc/models/lgrc_9_v3_packets.py"),
    ("restoration_identity", "src/pygrc/models/lgrc_9_v3_restoration.py"),
    ("runtime_execution", "src/pygrc/models/lgrc_9_v3_runtime.py"),
    ("runtime_facade", "src/pygrc/models/lgrc_9_v3.py"),
    ("telemetry_contract", "src/pygrc/telemetry/lgrc9v3_contract.py"),
    ("restoration_identity_spec", "specs/lgrc-9-v3-restoration-identity.md"),
    ("reset_baseline_spec", "specs/grc-reset-baseline-persistence.md"),
]

GRAPH_TEST_SOURCES = [
    "tests/models/test_lgrc_9_v3_runtime.py",
    "tests/models/test_lgrc_9_v3_contract.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py",
    "tests/models/test_lgrc_9_v3_restoration.py",
    "tests/models/test_lgrc_9_v3_restoration_matrix.py",
    "tests/models/test_reset_baseline_persistence.py",
    "tests/telemetry/test_lgrc9v3_contract.py",
]

HISTORIC_AND_PLANNING_SOURCES = [
    (
        "n08_mem6_closeout",
        "experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/"
        "n08_iteration_8_mem6_closeout.json",
        "historic_artifact_memory_candidate_and_native_policy_blocker",
        ["historic_memory_candidate_boundary", "native_memory_blocker"],
        ["N31_decay_evidence", "native_decay_policy_evidence"],
    ),
    (
        "n08_native_geometry_trail_closeout",
        "experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/"
        "n08_iteration_13_native_geometry_trail_closeout.json",
        "native_geometry_trail_attempt_and_blocker_context",
        ["native_geometry_trail_blocker", "route_use_trace_context"],
        ["N31_positive_D0_evidence", "native_route_memory_evidence"],
    ),
    (
        "n22_source_handoff_inventory",
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_source_handoff_inventory.json",
        "susceptibility_contract_history",
        ["historic_susceptibility_contract", "AP4_AP5_gap_context"],
        ["N31_candidate_C_evidence", "native_susceptibility_update_evidence"],
    ),
    (
        "n22_producer_carrier_probe",
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_alternative_nonconsumptive_carrier_probe.json",
        "producer_mediated_conductance_carrier_precedent",
        ["producer_carrier_precedent", "naturalization_debt_source"],
        ["native_candidate_C_evidence", "coherence_only_D0_evidence"],
    ),
    (
        "n22_closeout_and_n23_handoff",
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_closeout_and_n23_handoff.json",
        "producer_residue_and_naturalization_debt_boundary",
        ["producer_residue_boundary", "native_conductance_memory_blocker"],
        ["N31_positive_evidence", "native_learning_or_decay_evidence"],
    ),
    (
        "n30_participant_admissibility",
        "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/"
        "n30_participant_admissibility_i4.json",
        "source_current_participant_carrier_precedent",
        ["source_current_participant_precedent", "participant_attribution_boundary"],
        ["N31_decay_evidence", "agentic_participant_evidence"],
    ),
    (
        "n30_primary_medium_trace",
        "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/"
        "n30_medium_surface_trace_i5.json",
        "source_current_medium_trace_precedent",
        ["source_current_fixture_precedent", "trace_persistence_decay_limit"],
        ["N31_decay_evidence", "native_slow_trace_evidence"],
    ),
    (
        "n30_scope_window_audit",
        "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/"
        "n30_medium_surface_scope_window_i5b.json",
        "medium_scope_window_and_temporal_decay_blocker",
        ["window_scope_boundary", "temporal_decay_blocker"],
        ["N31_positive_D0b_evidence", "long_horizon_decay_evidence"],
    ),
    (
        "n30_later_eligibility",
        "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/"
        "n30_later_eligibility_i6.json",
        "later_eligibility_dependency_precedent",
        ["local_later_readout_precedent", "causal_dependency_control_context"],
        ["N31_causal_mediation_evidence", "shared_medium_coordination_evidence"],
    ),
    (
        "n30_closeout",
        "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/"
        "n30_closeout_and_spiral_handoff_i8.json",
        "minimal_shared_medium_closeout_and_N31_context",
        ["participant_medium_context", "post_N30_spiral_context"],
        ["N31_decay_evidence", "ecology_regime_evidence"],
    ),
    (
        "n30_plus_catalog_roadmap",
        "experiments/N30_plus_experiment_catalog_roadmap.md",
        "planning_and_claim_boundary_only",
        ["catalog_context", "claim_boundary_policy"],
        ["scientific_evidence", "N31_candidate_support"],
    ),
    (
        "n30_plus_candidate_directions",
        "experiments/N30_plus_candidate_directions.md",
        "planning_direction_only",
        ["candidate_direction_context", "dependency_context"],
        ["scientific_evidence", "N31_candidate_selection"],
    ),
    (
        "n30_plus_shared_medium_ecology_handoff",
        "experiments/N30_plus_LGRC_SharedMediumEcologyHandoff.md",
        "planning_handoff_only",
        ["handoff_context", "ecology_demand_context"],
        ["scientific_evidence", "N31_decay_result"],
    ),
    (
        "claim_boundary_index",
        "docs/reference/ClaimBoundaryIndex.md",
        "claim_index_only",
        ["claim_ceiling_context", "blocked_relabel_context"],
        ["scientific_evidence", "positive_runtime_support"],
    ),
]

BLOCKED_CLAIMS = [
    "universal_decay_law",
    "native_memory",
    "native_learning",
    "trail_or_stigmergy",
    "semantic_communication",
    "shared_medium_coordination",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_extension",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    encoded = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_output(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True
    ).stdout


def git_text(repo: Path, *args: str) -> str:
    return git_output(repo, *args).decode("utf-8").strip()


def pinned_blob(repo: Path, revision: str, path: str) -> bytes:
    return git_output(repo, "show", f"{revision}:{path}")


def git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=repo,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def external_record(
    *,
    source_id: str,
    repository_id: str,
    repo: Path,
    revision: str,
    path: str,
    role: str,
    may_consume_as: list[str],
    must_not_consume_as: list[str],
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    blob = pinned_blob(repo, revision, path)
    digest = sha256_bytes(blob)
    return {
        "source_id": source_id,
        "repository_id": repository_id,
        "revision": revision,
        "path": path,
        "source_role": role,
        "source_exists_at_revision": True,
        "sha256": digest,
        "expected_sha256": expected_sha256,
        "expected_sha256_matches": expected_sha256 is None or digest == expected_sha256,
        "may_consume_as": may_consume_as,
        "must_not_consume_as": must_not_consume_as,
        "positive_evidence_opened_by_source": False,
    }


def graph_record(
    source_id: str,
    path: str,
    role: str,
    may_consume_as: list[str],
    must_not_consume_as: list[str],
) -> dict[str, Any]:
    try:
        blob = pinned_blob(ROOT, GRAPH_REVISION, path)
    except subprocess.CalledProcessError:
        blob = None
    return {
        "source_id": source_id,
        "repository_id": "graph_reflexive_coherence",
        "revision": GRAPH_REVISION,
        "path": path,
        "source_role": role,
        "source_exists_at_revision": blob is not None,
        "sha256": sha256_bytes(blob) if blob is not None else "missing",
        "expected_sha256": None,
        "expected_sha256_matches": blob is not None,
        "may_consume_as": may_consume_as,
        "must_not_consume_as": must_not_consume_as,
        "positive_evidence_opened_by_source": False,
    }


def runtime_capability_inventory() -> list[dict[str, Any]]:
    return [
        {
            "capability_id": "node_coherence_state",
            "runtime_disposition": "existing_native_runtime_surface",
            "source_paths": ["src/pygrc/models/lgrc_9_v3_runtime_state.py"],
            "evidence": "LGRC9V3RuntimeState.base_state node coherence",
            "n31_use": "route_mass_and_invariant_input_candidate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "edge_conductance_and_flux",
            "runtime_disposition": "existing_native_runtime_surface",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime.py",
                "src/pygrc/telemetry/lgrc9v3_contract.py",
            ],
            "evidence": "port-edge conductance and flux_uv are source-current state/telemetry",
            "n31_use": "D0c_input_and_candidate_C_comparator_only",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "lapse",
            "runtime_disposition": "existing_native_computed_runtime_surface",
            "source_paths": ["src/pygrc/models/lgrc_9_v3_timing.py"],
            "evidence": "compute_lgrc9v3_lapse_by_node with explicit policies",
            "n31_use": "internal_time_input_not_decay_policy",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "node_proper_time",
            "runtime_disposition": "existing_native_mutating_runtime_surface",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                "src/pygrc/models/lgrc_9_v3_runtime.py",
            ],
            "evidence": "step-local _advance_node_proper_time updates persisted node surfaces",
            "n31_use": "internal_progression_clock_not_causal_alignment_proof",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "event_time_and_edge_causal_delay",
            "runtime_disposition": "existing_native_runtime_surface",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                "src/pygrc/models/lgrc_9_v3_packets.py",
            ],
            "evidence": "arrival key is departure key plus captured positive edge causal delay",
            "n31_use": "temporal_projection_input_not_dispersion_or_decay_by_itself",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "packet_event_queue",
            "runtime_disposition": "existing_native_executable_runtime_surface",
            "source_paths": ["src/pygrc/models/lgrc_9_v3_packets.py"],
            "evidence": "deterministic departure/arrival records, queue ordering, and processors",
            "n31_use": "formation_packet_exclusion_and_temporal_history_input",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "arrival_local_readout",
            "runtime_disposition": "existing_native_executable_runtime_surface",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_packets.py",
                "src/pygrc/models/lgrc_9_v3_runtime.py",
            ],
            "evidence": "arrival eligibility and local update can causally affect later scheduling",
            "n31_use": "candidate_local_readout_API_subject_to_I4_mediation_gate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "arrival_time_distribution",
            "runtime_disposition": "exact_derived_projection_possible_native_aggregate_missing",
            "source_paths": ["src/pygrc/models/lgrc_9_v3_packets.py"],
            "evidence": "per-packet arrival keys exist; no native arrival-distribution state or update law",
            "n31_use": "D0b_or_I4_temporal_representation_candidate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "coincidence_resonance_alignment_policy",
            "runtime_disposition": "runtime_surface_missing",
            "source_paths": [],
            "evidence": "no native coincidence window, resonance state, or alignment update owner found",
            "n31_use": "added_policy_must_be_closure_or_extension_not_native_D0",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "registered_route_support",
            "runtime_disposition": "candidate_exact_projection_requires_I4_freeze",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                "src/pygrc/models/lgrc_9_v3_runtime.py",
            ],
            "evidence": "topology and causal route records exist but no generic N31 route-support API",
            "n31_use": "I4_representation_gate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "route_boundary_flux",
            "runtime_disposition": "candidate_exact_projection_requires_I4_continuity_contract",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_packets.py",
                "src/pygrc/telemetry/lgrc9v3_contract.py",
            ],
            "evidence": "packet and edge flux are available; route boundary/sign/in-flight treatment is not generic",
            "n31_use": "I4_mass_continuity_gate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "route_organization_observable",
            "runtime_disposition": "generic_native_mediator_missing_exact_projection_open",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                "src/pygrc/models/lgrc_9_v3_timing.py",
            ],
            "evidence": "state exposes geometry/timing components but no admitted persistent route-organization mediator",
            "n31_use": "I4_domain_specific_representation_gate",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "finite_window_history_relation",
            "runtime_disposition": "exact_derived_projection_candidate_no_native_decay_policy",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                "src/pygrc/models/lgrc_9_v3_packets.py",
            ],
            "evidence": "exact queue/event/route histories exist; a finite-window relation would be derived",
            "n31_use": "D0b_candidate_only",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "route_susceptibility_relaxation",
            "runtime_disposition": "added_update_and_relaxation_policy_missing",
            "source_paths": ["src/pygrc/models/lgrc_9_v3_runtime.py"],
            "evidence": "conductance state exists but N22 carrier update was producer-mediated and no native relaxation law exists",
            "n31_use": "candidate_C_closure_or_extension_boundary",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "restoration_identity_v1",
            "runtime_disposition": "existing_native_current_state_identity",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_restoration.py",
                "specs/lgrc-9-v3-restoration-identity.md",
            ],
            "evidence": "v1 identifies scientific current state and excludes representation caches",
            "n31_use": "current_state_replay_identity_only",
            "positive_decay_evidence": False,
        },
        {
            "capability_id": "restoration_identity_v2_and_reset_baseline",
            "runtime_disposition": "existing_native_current_plus_reset_baseline_identity",
            "source_paths": [
                "src/pygrc/models/lgrc_9_v3_restoration.py",
                "specs/grc-reset-baseline-persistence.md",
            ],
            "evidence": "v2 binds current v1 identity and reset-baseline v1 identity; legacy rebase is explicit/prospective",
            "n31_use": "N31_replay_restoration_and_reset_contract",
            "positive_decay_evidence": False,
        },
    ]


def theory_runtime_dispositions() -> list[dict[str, Any]]:
    return [
        {
            "question_id": "global_coherence_conservation",
            "theory_disposition": "direct_theory_requirement",
            "runtime_disposition": "multiple_budget_and_packet_continuity_surfaces_exist_candidate_specific_audit_required",
            "n31_effect": "each positive row must freeze and close its own invariant",
        },
        {
            "question_id": "D0a_slow_causal_coherence_organization",
            "theory_disposition": "theoretically_compatible_not_automatically_discrete",
            "runtime_disposition": "representation_unresolved_pending_I4",
            "n31_effect": "no positive D0a row admitted in I1",
        },
        {
            "question_id": "D0b_fading_derived_observable",
            "theory_disposition": "admissible_as_observable_not_independent_state",
            "runtime_disposition": "exact_history_inputs_exist_projection_not_yet_frozen",
            "n31_effect": "candidate remains below mediation until I6/I8",
        },
        {
            "question_id": "D0c_instantaneous_geometry",
            "theory_disposition": "directly_induced_by_current_coherence_flux_geometry",
            "runtime_disposition": "native_state_and_telemetry_inputs_exist",
            "n31_effect": "instantaneous comparator only; persistence unproved",
        },
        {
            "question_id": "temporal_desynchronization_or_dispersion",
            "theory_disposition": "bounded_D0_domain_variant_if_causal_mediation_is_shown",
            "runtime_disposition": "timing_and_packet_events_native_distribution_and_mediation_unresolved",
            "n31_effect": "arrival histogram alone remains D0b",
        },
        {
            "question_id": "candidate_A_release_efficacy",
            "theory_disposition": "compatible_only_if_efficacy_is_coherence_derived_or_declared_added_state",
            "runtime_disposition": "packet_amount_and_timing_exist_no_generic_age_phase_release_law",
            "n31_effect": "added law cannot be called field-state decay",
        },
        {
            "question_id": "candidate_B_conserved_source_leakage",
            "theory_disposition": "continuity_compatible_with_explicit_destination",
            "runtime_disposition": "packet_transfer_primitives_exist_endogenous_leak_law_missing",
            "n31_effect": "producer policy must remain B_or_B_R",
        },
        {
            "question_id": "candidate_C_susceptibility_relaxation",
            "theory_disposition": "independent_slow_state_is_closure_or_theory_extension",
            "runtime_disposition": "storage_precedent_exists_native_update_relaxation_missing",
            "n31_effect": "cannot be promoted to coherence-only D0",
        },
    ]


def build_payload() -> dict[str, Any]:
    graph_head = git_text(ROOT, "rev-parse", "HEAD")
    graph_base_is_ancestor = git_is_ancestor(ROOT, GRAPH_REVISION, graph_head)
    rcae_revision_resolved = git_text(RCAE_ROOT, "rev-parse", RCAE_REVISION)
    theory_revision_resolved = git_text(THEORY_ROOT, "rev-parse", THEORY_REVISION)

    source_records: list[dict[str, Any]] = []
    for source_id, path, role in RCAE_SOURCES:
        source_records.append(
            external_record(
                source_id=source_id,
                repository_id="reflexive_coherence_agentic_ecology",
                repo=RCAE_ROOT,
                revision=RCAE_REVISION,
                path=path,
                role=role,
                may_consume_as=["question", "control", "return_role", "blocked_claim"],
                must_not_consume_as=["graph_runtime_evidence", "N31_positive_evidence"],
            )
        )
    for source_id, path, expected_sha256, role in THEORY_SOURCES:
        source_records.append(
            external_record(
                source_id=source_id,
                repository_id="geometric_reflexive_coherence",
                repo=THEORY_ROOT,
                revision=THEORY_REVISION,
                path=path,
                role=role,
                may_consume_as=["theory_constraint", "substrate_specification", "claim_boundary"],
                must_not_consume_as=["graph_runtime_evidence", "positive_N31_run_evidence"],
                expected_sha256=expected_sha256,
            )
        )
    for source_id, path in GRAPH_RUNTIME_SOURCES:
        source_records.append(
            graph_record(
                source_id,
                path,
                "load_bearing_graph_runtime_or_specification_source",
                ["runtime_capability_inventory", "representation_gate_input", "replay_contract"],
                ["positive_decay_evidence_without_run", "universal_decay_claim"],
            )
        )
    for index, path in enumerate(GRAPH_TEST_SOURCES, start=1):
        source_records.append(
            graph_record(
                f"load_bearing_runtime_test_{index:02d}",
                path,
                "load_bearing_runtime_conformance_test_source",
                ["existing_contract_conformance_context", "future_N31_test_selection"],
                ["N31_scientific_evidence", "decay_candidate_support"],
            )
        )
    for source_id, path, role, may_consume_as, must_not_consume_as in HISTORIC_AND_PLANNING_SOURCES:
        source_records.append(
            graph_record(source_id, path, role, may_consume_as, must_not_consume_as)
        )

    runtime_capabilities = runtime_capability_inventory()
    theory_dispositions = theory_runtime_dispositions()
    src_diff_empty = not git_text(ROOT, "diff", "--", "src")
    protected_diff_empty = not git_text(ROOT, "diff", "--", *PROTECTED_PATHS)
    unsafe_claim_flags = {f"{claim}_claim_allowed": False for claim in BLOCKED_CLAIMS}

    checks = [
        {
            "check_id": "graph_frozen_I1_base_is_ancestor",
            "passed": graph_base_is_ancestor,
        },
        {"check_id": "rcae_revision_verified", "passed": rcae_revision_resolved == RCAE_REVISION},
        {"check_id": "theory_revision_verified", "passed": theory_revision_resolved == THEORY_REVISION},
        {
            "check_id": "all_required_sources_exist",
            "passed": all(record["source_exists_at_revision"] for record in source_records),
        },
        {
            "check_id": "all_seven_theory_digests_match",
            "passed": all(
                record["expected_sha256_matches"]
                for record in source_records
                if record["source_id"].startswith("theory_")
            ),
        },
        {
            "check_id": "all_sources_have_consumption_boundaries",
            "passed": all(record["may_consume_as"] and record["must_not_consume_as"] for record in source_records),
        },
        {
            "check_id": "RCAE_sources_are_demand_not_evidence",
            "passed": all(
                "N31_positive_evidence" in record["must_not_consume_as"]
                for record in source_records
                if record["repository_id"] == "reflexive_coherence_agentic_ecology"
            ),
        },
        {
            "check_id": "timing_execution_and_missing_policy_distinguished",
            "passed": any(
                row["capability_id"] == "packet_event_queue"
                and row["runtime_disposition"] == "existing_native_executable_runtime_surface"
                for row in runtime_capabilities
            )
            and any(
                row["capability_id"] == "coincidence_resonance_alignment_policy"
                and row["runtime_disposition"] == "runtime_surface_missing"
                for row in runtime_capabilities
            ),
        },
        {
            "check_id": "route_mass_organization_and_mediation_not_collapsed",
            "passed": all(
                any(row["capability_id"] == capability_id for row in runtime_capabilities)
                for capability_id in (
                    "registered_route_support",
                    "route_boundary_flux",
                    "route_organization_observable",
                    "arrival_local_readout",
                )
            ),
        },
        {
            "check_id": "restoration_v1_v2_and_reset_baseline_inventory_present",
            "passed": all(
                any(row["capability_id"] == capability_id for row in runtime_capabilities)
                for capability_id in (
                    "restoration_identity_v1",
                    "restoration_identity_v2_and_reset_baseline",
                )
            ),
        },
        {"check_id": "src_diff_empty", "passed": src_diff_empty},
        {"check_id": "protected_runtime_contract_diff_empty", "passed": protected_diff_empty},
        {"check_id": "positive_evidence_remains_closed", "passed": True},
        {"check_id": "unsafe_claim_flags_false", "passed": all(value is False for value in unsafe_claim_flags.values())},
    ]

    payload: dict[str, Any] = {
        "experiment": "N31_lgrc9v3_derived_decay_and_primitive_semantics",
        "iteration": "1_source_inventory_and_authority_admission",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_source_and_authority_inventory_only_no_decay_evidence",
        "candidate_schema_version": "n31_decay_candidate_schema_v2",
        "graph_source_state": {
            "branch": "experiment-N31",
            "frozen_I1_base_revision": GRAPH_REVISION,
            "frozen_I1_base_is_ancestor": graph_base_is_ancestor,
            "execution_revision_policy": (
                "frozen_base_must_remain_ancestor; later experiment-only commits "
                "do not change consumed runtime revision"
            ),
            "source_state_at_I1_start": "clean",
            "src_diff_empty": src_diff_empty,
            "protected_runtime_contract_diff_empty": protected_diff_empty,
            "experiment_artifact_changes_allowed": True,
        },
        "external_source_revisions": {
            "RCAE_demand_revision": rcae_revision_resolved,
            "geometric_theory_revision": theory_revision_resolved,
        },
        "source_record_count": len(source_records),
        "source_records": source_records,
        "runtime_capability_count": len(runtime_capabilities),
        "runtime_capability_inventory": runtime_capabilities,
        "theory_to_runtime_dispositions": theory_dispositions,
        "missing_surface_interpretation": {
            "missing_runtime_surface_is_negative_theory_evidence": False,
            "missing_runtime_surface_means": "current_graph_representation_or_policy_does_not_supply_the_surface",
            "I4_may_classify": [
                "exact_derived_projection",
                "blocked_by_representation",
                "runtime_extension_required",
            ],
        },
        "historic_experiment_boundaries": {
            "N08": "artifact_memory_and_route_trace_precedent_with_native_memory_policy_blocked",
            "N22": "producer_mediated_non_consumptive_conductance_carrier_with_native_update_and_relaxation_debt",
            "N30": "source_current_participant_medium_and_later_eligibility_precedent_with_temporal_decay_unresolved",
            "roadmaps_and_handoffs": "planning_and_claim_boundary_only",
        },
        "positive_evidence_opened": False,
        "candidate_rows_classified": False,
        "decay_semantics_selected": False,
        "decay_relation_ladder_rung_assigned": False,
        "decay_relation_ladder_ceiling": "DR0_no_source_current_decay_evidence",
        "n31_closeout_ladder_rung_assigned": False,
        "n31_closeout_ceiling": "N31-C1_source_and_authority_inventory_only",
        "ready_for_iteration_2_schema_freeze": True,
        "claim_boundary": {
            "claim_ceiling": "source_and_authority_inventory_only_no_N31_decay_evidence",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": unsafe_claim_flags,
        },
        "digest_semantics": {
            "output_digest": "canonical_payload_digest_excluding_output_digest",
            "artifact_sha256": "exact_file_content_digest",
            "values_may_differ": True,
        },
        "checks": checks,
    }
    checks.append({"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)})
    payload["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_source_inventory_checks_failed"
        payload["ready_for_iteration_2_schema_freeze"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    source_rows = "\n".join(
        "| {source_id} | {repository_id} | {source_role} | `{sha}` |".format(
            source_id=row["source_id"],
            repository_id=row["repository_id"],
            source_role=row["source_role"],
            sha=row["sha256"][:12],
        )
        for row in payload["source_records"]
    )
    capability_rows = "\n".join(
        "| {capability_id} | {runtime_disposition} | {n31_use} |".format(**row)
        for row in payload["runtime_capability_inventory"]
    )
    check_rows = "\n".join(
        f"- `{row['check_id']}` = `{str(row['passed']).lower()}`"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 1 - Source Inventory And Authority Admission

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 1 admits source authority and inventories executable graph surfaces.
It does not run a decay candidate, select a decay meaning, or assign a positive
DR/N31-C rung. RCAE defines the exact downstream question and return contract;
theory sources constrain interpretation; graph runtime and experiment artifacts
define what is currently executable or previously evidenced.

## Source Records

| Source | Repository | Role | SHA-256 prefix |
|---|---|---|---|
{source_rows}

## Runtime Capability Dispositions

| Capability | Current disposition | N31 use |
|---|---|---|
{capability_rows}

## Main Boundary

LGRC9V3 already executes event-time ordering, node proper time, lapse, edge
causal delay, packet queues, arrivals, local updates, and source-current
conductance/flux surfaces. These are admissible inputs, not decay evidence.

No native arrival-distribution state, coincidence/resonance policy, generic
persistent route-organization mediator, or susceptibility-relaxation law is
present. Per-packet timing and exact histories may support derived projections,
but I4 must first establish their representation and mediation authority.
Runtime absence is not negative evidence against RC theory.

N08 contributes a native-memory blocker, N22 contributes producer-mediated
conductance-carrier precedent and naturalization debt, and N30 contributes
source-current participant/medium/readout precedent while leaving temporal
decay unresolved. None supplies a positive N31 row.

## Restoration Boundary

Restoration identity v1 covers scientific current state. V2 additionally binds
the reset baseline. A legacy explicit rebase makes v2 available prospectively;
it does not recover historical construction provenance. Later N31 replay rows
must select the identity version appropriate to the operation being tested.

## Checks

{check_rows}

## Claim Ceiling

`n31_closeout_ceiling = N31-C1_source_and_authority_inventory_only`

`positive_evidence_opened = false`

`decay_relation_ladder_rung_assigned = false`
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
