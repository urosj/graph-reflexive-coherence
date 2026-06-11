"""Build N06 Iteration 1 baseline and schema inventory.

This script records N05 inheritance, native LGRC9V3 route-arbitration contract
surfaces, context/affordance mapping options, SC row schema, and claim
boundaries for N06. It intentionally does not run route-choice probes and does
not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
IMPLEMENTATION = ROOT / "implementation"
CONTRACT_PATH = ROOT / "src/pygrc/models/lgrc_9_v3_contract.py"
RUNTIME_PATH = ROOT / "src/pygrc/models/lgrc_9_v3_runtime.py"
TELEMETRY_PATH = ROOT / "src/pygrc/telemetry/lgrc9v3_contract.py"

OUTPUT_PATH = N06 / "outputs/n06_iteration_1_baseline_inventory.json"
REPORT_PATH = N06 / "reports/n06_iteration_1_baseline_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "build_n06_iteration_1_baseline_inventory.py"
)


SOURCE_ARTIFACTS: dict[str, Path] = {
    "n06_readme": N06 / "README.md",
    "n06_plan": N06 / "implementation/SemanticRouteChoiceImplementationPlan.md",
    "n06_checklist": N06
    / "implementation/SemanticRouteChoiceImplementationChecklist.md",
    "n06_implementation_readme": N06 / "implementation/README.md",
    "n05_n11_roadmap": ROOT / "experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md",
    "n05_closeout": N05 / "outputs/n05_iteration_8_o6_closeout.json",
    "n05_closeout_report": N05 / "reports/n05_iteration_8_o6_closeout.md",
    "n04_native_route_arbitration_rerun": N04
    / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json",
    "n04_native_route_arbitration_rerun_report": N04
    / "reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md",
    "n04_identity_native_route_arbitrated_topology": N04
    / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
    "phase8_native_route_arbitration_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.md",
    "phase8_native_route_arbitration_closeout_json": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.json",
    "lgrc9v3_contract_source": CONTRACT_PATH,
    "lgrc9v3_runtime_source": RUNTIME_PATH,
    "lgrc9v3_telemetry_source": TELEMETRY_PATH,
}


CLAIM_FLAGS_FALSE: dict[str, bool] = {
    "semantic_choice_claim_allowed": False,
    "memory_or_trail_claim_allowed": False,
    "movement_claim_allowed": False,
    "agency_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "goal_proxy_regulation_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
}


SC_ROW_SCHEMA_REQUIRED_FIELDS: list[str] = [
    "run_id",
    "sc_level",
    "sc_level_is_evidence_classification",
    "claim_ceiling",
    "claim_flags",
    "runtime_family",
    "lgrc_runtime_level",
    "source_native_surfaces",
    "fixture_id",
    "source_node_id",
    "candidate_route_records",
    "candidate_route_digests",
    "candidate_set_record",
    "candidate_set_digest",
    "native_route_arbitration_record",
    "native_route_arbitration_digest",
    "selected_candidate_route_digest",
    "rejected_candidate_route_digests",
    "context_surface",
    "context_surface_digest",
    "context_relation",
    "context_runtime_visible",
    "selection_rule",
    "selection_reason_code",
    "score_components",
    "compatibility_gate_components",
    "arbitration_window_id",
    "candidate_source_surface_digest",
    "candidate_source_producer_record_id",
    "candidate_source_topology_state_reabsorption_digest",
    "route_intent",
    "selected_topology_event_id",
    "event_time_key",
    "scheduler_event_index",
    "causal_epoch",
    "node_proper_time",
    "scheduled_packet_id",
    "processed_packet_id",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "producer_records",
    "producer_boundary",
    "artifact_only_replay",
    "controls",
    "blocked_claims",
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
    return record


def _source_artifacts() -> list[dict[str, Any]]:
    return [_artifact_record(name, path) for name, path in SOURCE_ARTIFACTS.items()]


def _n05_inheritance() -> dict[str, Any]:
    n05 = _load_json(SOURCE_ARTIFACTS["n05_closeout"])
    closeout = dict(n05.get("n05_closeout", {}))
    o6 = dict(n05.get("o6_boundary", {}))
    return {
        "source_artifact": _rel(SOURCE_ARTIFACTS["n05_closeout"]),
        "source_status": n05.get("status"),
        "inherited_background": "oscillator_circuit_background_only",
        "strongest_supported_o_level": closeout.get("strongest_supported_o_level"),
        "strongest_claim_ceiling": closeout.get("strongest_claim_ceiling"),
        "o6_route_coupled_oscillator_supported": o6.get(
            "o6_route_coupled_oscillator_supported"
        ),
        "o6_primary_blocker": o6.get("trail_memory_blocker"),
        "n06_ready": bool(n05.get("n06_handoff_recommendation", {}).get("ready")),
        "claim_flags": n05.get("claim_flags", {}),
        "n06_inheritance_claims": {
            "memory_or_trail_inherited": False,
            "semantic_choice_inherited": False,
            "agency_inherited": False,
            "identity_acceptance_inherited": False,
            "locomotion_inherited": False,
        },
    }


def _native_route_arbitration_surfaces() -> dict[str, Any]:
    return {
        "native_route_arbitration_contract": {
            "contract_file": _rel(CONTRACT_PATH),
            "runtime_file": _rel(RUNTIME_PATH),
            "telemetry_file": _rel(TELEMETRY_PATH),
            "candidate_record_class": "LGRC9V3NativeRouteCandidateRecord",
            "candidate_set_record_class": "LGRC9V3NativeRouteCandidateSetRecord",
            "arbitration_record_class": "LGRC9V3NativeRouteArbitrationRecord",
            "validator": "validate_lgrc9v3_native_route_arbitration_artifacts",
            "validator_signature": {
                "required": [
                    "events",
                    "candidate_route_records",
                    "candidate_set_records",
                    "route_arbitration_records",
                ],
                "optional": [
                    "surface_rows",
                    "surface_lineage_records",
                    "topology_events",
                    "topology_state_reabsorption_records",
                    "production_results",
                    "budget_tolerance",
                ],
            },
            "validator_scope": (
                "artifact-only replay of candidate routes, candidate sets, "
                "arbitration records, selected topology event, lineage, "
                "topology-state reabsorption, and producer scheduling"
            ),
            "validator_failure_modes": {
                "disabled_policy": "native_route_arbitration_policy_disabled",
                "no_candidates": "native_route_arbitration_no_candidates",
                "unresolved_tie": "native_route_arbitration_unresolved_tie",
                "hidden_input": "native_route_arbitration_hidden_input_rejected",
                "budget_invalid": "native_route_arbitration_budget_invalid",
                "budget_mismatch": "native_route_candidate_budget_mismatch",
                "order_invalid": "native_route_arbitration_order_invalid",
                "candidate_order_inversion": (
                    "native_route_arbitration_order_invalid:"
                    "candidate_set_before_candidate"
                ),
                "candidate_digest_mismatch": "candidate_route_digest_mismatch",
                "candidate_set_digest_mismatch": "candidate_set_digest_mismatch",
                "candidate_source_surface_missing": (
                    "native_route_candidate_unknown_source_surface"
                ),
                "candidate_set_missing_candidate": "candidate_set_missing_candidate",
                "duplicate_candidate": "duplicate_native_route_candidate",
                "duplicate_candidate_set": "duplicate_native_route_candidate_set",
                "duplicate_arbitration": "duplicate_native_route_arbitration",
                "claim_promotion": (
                    "native_route_arbitration_claim_promotion_blocked"
                ),
                "selected_candidate_outside_set": (
                    "native_route_arbitration_selected_candidate_outside_set"
                ),
            },
        },
        "native_runtime_gate": {
            "lgrc_runtime_level": "lgrc3",
            "causal_layer_mode": "topology_changing_causal_history",
            "causal_topology_integration_allowed": True,
            "causal_pulse_substrate_surface_lineage_transport_supported": True,
            "causal_topology_state_reabsorption_supported": True,
            "native_lgrc_route_arbitration_enabled": True,
            "native_lgrc_route_arbitration_policy_gate": "policy != disabled",
            "n06_default_native_lgrc_route_arbitration_policy": (
                "score_ordered_topology_route_candidates"
            ),
            "disabled_policy_requires_enabled_false": True,
            "lgrc2_native_route_arbitration_allowed": False,
        },
        "candidate_record_fields": {
            "source_linkage": [
                "candidate_source_surface_digest",
                "candidate_source_producer_record_id",
                "candidate_source_topology_state_reabsorption_digest",
            ],
            "route_fields": [
                "route_intent",
                "candidate_topology_event_kind",
                "candidate_competing_sink_ids",
                "candidate_selected_sink_id",
                "candidate_losing_sink_ids",
                "candidate_transferred_node_ids",
                "candidate_lineage_transfer_map",
                "candidate_source_node_ids",
                "candidate_target_node_ids",
                "candidate_retired_node_ids",
                "candidate_source_edge_ids",
                "candidate_target_edge_ids",
                "candidate_retired_edge_ids",
            ],
            "score_and_context_fields": [
                "candidate_route_score",
                "candidate_score_components",
                "candidate_runtime_visible_inputs",
                "candidate_order_key",
            ],
            "score_component_invariant": {
                "owner": "native_lgrc9v3_candidate_record_contract",
                "rule": "candidate_route_score == sum(candidate_score_components)",
                "enforced_by": "LGRC9V3NativeRouteCandidateRecord.__post_init__",
                "tolerance": "1e-12",
            },
            "budget_fields": ["candidate_budget_prediction"],
            "ordering_fields": ["event_time_key", "scheduler_event_index"],
            "digest_field": "candidate_route_digest",
        },
        "candidate_set_fields": {
            "required": [
                "candidate_set_id",
                "arbitration_window_id",
                "candidate_route_digests",
                "candidate_set_order_key",
                "unresolved_tie_policy",
                "event_time_key",
                "scheduler_event_index",
                "idempotency_key",
                "candidate_set_digest",
            ]
        },
        "candidate_set_ordering": {
            "default_for_n06": "score_desc_then_candidate_id",
            "policy_configurable_values": [
                "score_desc_then_candidate_id",
                "digest_ascending",
            ],
            "score_desc_then_candidate_id_order": [
                "candidate_route_score descending",
                "candidate_order_key ascending",
                "candidate_route_id ascending",
            ],
            "digest_ascending_order": ["candidate_route_digest ascending"],
            "iteration_2_requirement": (
                "fixture manifest must declare the order key before candidate "
                "emission; list order alone is not native evidence"
            ),
        },
        "declared_tiebreaker_serialization": {
            "policy": "declared_runtime_visible_tiebreaker",
            "serialized_fields": [
                "candidate_set.unresolved_tie_policy",
                "candidate_set.candidate_set_order_key",
                "candidate.candidate_order_key",
                "candidate.candidate_route_digest",
                "arbitration_record.arbitration_runtime_visible_inputs",
            ],
            "blocked_sources": [
                "fixture hidden order",
                "experiment if/else",
                "Python/list order unless declared by candidate_set_order_key",
                "report-side selected route",
            ],
        },
        "arbitration_record_fields": {
            "required": [
                "native_route_arbitration_record_id",
                "candidate_set_id",
                "candidate_set_digest",
                "selected_candidate_route_digest",
                "rejected_candidate_route_digests",
                "arbitration_reason_code",
                "arbitration_score",
                "arbitration_rule",
                "arbitration_runtime_visible_inputs",
                "event_time_key",
                "scheduler_event_index",
                "idempotency_key",
                "native_route_arbitration_digest",
            ],
            "selected_topology_linkage": [
                "selected_topology_event_id",
                "selected_topology_event_digest",
            ],
        },
        "policies": {
            "disabled": "disabled",
            "score_ordered_candidates": "score_ordered_topology_route_candidates",
        },
        "reason_codes": [
            "native_route_arbitration_selected_highest_score",
            "native_route_arbitration_selected_declared_local_preference",
            "native_route_arbitration_no_candidates",
            "native_route_arbitration_unresolved_tie",
            "native_route_arbitration_policy_disabled",
            "native_route_arbitration_budget_invalid",
            "native_route_arbitration_order_invalid",
            "native_route_arbitration_hidden_input_rejected",
        ],
        "route_intents": ["collapse", "reabsorb", "split", "merge", "redirect"],
        "route_intent_classes": {
            "topology_mutating_native_intents": [
                "collapse",
                "reabsorb",
                "split",
                "merge",
            ],
            "redirect_policy": (
                "redirect is a native route-intent value, but N06 must declare "
                "whether it is used as a fixed-route/control scaffold or with "
                "an explicit topology-event kind; redirect alone must not be "
                "read as topology-mutating movement evidence"
            ),
        },
        "candidate_set_order_keys": [
            "score_desc_then_candidate_id",
            "digest_ascending",
        ],
        "unresolved_tie_policies": [
            "fail_closed",
            "declared_runtime_visible_tiebreaker",
        ],
        "forbidden_inputs": [
            "hidden_fixture_array",
            "hidden_fixture_state",
            "experiment_if_else",
            "preselected_sink_id",
            "posthoc_threshold",
            "report_code",
        ],
        "source_digest_pin_policy": (
            "Iteration 1 records current SHA-256 digests for native contract, "
            "runtime, and telemetry sources. Later iterations should compare "
            "against these source_artifacts records if source drift matters."
        ),
    }


def _context_affordance_inventory() -> dict[str, Any]:
    return {
        "dedicated_native_context_surface_exists": False,
        "required_iteration_2_decision": (
            "map context states A/B to native score/runtime-visible input "
            "fields or explicitly label an experiment-local gate"
        ),
        "preferred_default_native_mapping_for_iteration_2": {
            "score_surface": "candidate_score_components",
            "candidate_context_sources": "candidate_runtime_visible_inputs",
            "arbitration_context_sources": "arbitration_runtime_visible_inputs",
            "default_compatibility_gate": (
                "native_score_components_with_threshold_interpretation"
            ),
            "surface_row_inputs": (
                "optional source evidence when context is derived from native "
                "causal pulse-substrate rows"
            ),
            "fallback_only": "experiment_local_compatibility_gate_record",
        },
        "mapping_elimination_criteria": [
            "reject if context state is not serialized in runtime-visible fields",
            "reject if compatibility is decided by fixture/report code",
            "reject if the mapping requires hidden context arrays",
            "reject if the mapping cannot reconstruct A/B selection from artifacts",
            "label as experiment-local if it cannot be expressed by native fields",
        ],
        "allowed_native_field_mappings": [
            {
                "field": "candidate_score_components",
                "use": (
                    "numeric context/affordance contribution; route score must "
                    "equal the component sum"
                ),
                "native": True,
            },
            {
                "field": "candidate_runtime_visible_inputs",
                "use": "serialized names of context inputs consumed by a candidate",
                "native": True,
            },
            {
                "field": "arbitration_runtime_visible_inputs",
                "use": "serialized names of inputs consumed by arbitration",
                "native": True,
            },
            {
                "field": "causal_pulse_substrate_surface_rows",
                "use": (
                    "context from local_support_mass, boundary_polarity_score, "
                    "proper_time_phase, surface_deformation, route_local_pulse_contact, "
                    "or feedback_eligibility"
                ),
                "native": True,
            },
            {
                "field": "route_aspect_mass_polarity_channel_fields",
                "use": "route aspect context from serialized route semantics",
                "native": True,
            },
            {
                "field": "experiment_local_compatibility_gate_record",
                "use": "exploratory scaffold only; not native route-arbitration context",
                "native": False,
            },
        ],
        "compatibility_gate_options": [
            "native_score_components_with_threshold_interpretation",
            "experiment_local_gate_records",
        ],
        "blocked_context_sources": [
            "hidden_fixture_array",
            "hidden_fixture_state",
            "experiment_if_else",
            "preselected_sink_id",
            "posthoc_threshold",
            "report_code",
        ],
    }


def _sc_ladder_schema() -> dict[str, Any]:
    return {
        "schema_name": "semantic_route_choice_report_v1",
        "row_required_fields": SC_ROW_SCHEMA_REQUIRED_FIELDS,
        "sc_levels": {
            "SC0": "no_choice_fixed_route",
            "SC1": "alternatives_exposed",
            "SC2": "native_arbitration_selection",
            "SC3": "context_conditioned_selection",
            "SC4": "bidirectional_or_context_swap_selection",
            "SC5": "repeated_context_conditioned_selection",
            "SC6": "artifact_only_semantic_route_choice_candidate",
        },
        "sc_level_is_evidence_classification": True,
        "claim_flags_are_separate_from_sc_level": True,
        "minimum_runtime_level_scope": (
            "native route-arbitration evidence is LGRC-3-only; overall SC1 may "
            "also include LGRC-2 experiment-local scaffold/control rows when "
            "explicitly labeled non-native"
        ),
        "minimum_runtime_level_by_sc": {
            "SC0": {
                "native": "not_applicable_fixed_route_control",
                "experiment_local_or_control": "lgrc0_lgrc1_lgrc2",
            },
            "SC1": {
                "native": "lgrc3_for_candidate_route_and_candidate_set_records",
                "experiment_local_or_control": (
                    "lgrc2_allowed_only_as_non_native_scaffold_or_control"
                ),
            },
            "SC2": {
                "native": "lgrc3_topology_changing_causal_history",
                "experiment_local_or_control": "does_not_satisfy_native_sc2",
            },
            "SC3": {
                "native": "lgrc3_for_context_conditioned_route_arbitration",
                "experiment_local_or_control": "does_not_satisfy_native_sc3",
            },
            "SC4": {
                "native": "lgrc3_for_context_swap_route_arbitration",
                "experiment_local_or_control": "does_not_satisfy_native_sc4",
            },
            "SC5": {
                "native": "lgrc3_for_repeated_context_conditioned_arbitration",
                "experiment_local_or_control": "does_not_satisfy_native_sc5",
            },
            "SC6": {
                "native": "lgrc3_for_native_artifact_replay",
                "experiment_local_or_control": "does_not_satisfy_native_sc6",
            },
        },
        "minimum_native_runtime_level_by_sc": {
            "SC0": "lgrc0_lgrc1_lgrc2_fixed_route_control",
            "SC1": "lgrc3_for_native_candidate_emission",
            "SC2": "lgrc3_topology_changing_causal_history",
            "SC3": "lgrc3_for_native_route_arbitrated_rows",
            "SC4": "lgrc3_for_native_route_arbitrated_rows",
            "SC5": "lgrc3_for_native_route_arbitrated_rows",
            "SC6": "lgrc3_for_native_artifact_replay",
        },
        "experiment_local_lgrc2_rows": (
            "allowed only as non-native scaffolds or controls; they do not "
            "satisfy native route-arbitration evidence"
        ),
    }


def _claim_boundary() -> dict[str, Any]:
    return {
        "claim_flags": CLAIM_FLAGS_FALSE,
        "semantic_choice_claim_policy": (
            "semantic_route_choice_candidate may be claimed only after "
            "context-conditioned native arbitration and artifact replay pass; "
            "Iteration 1 sets no such claim"
        ),
        "semantic_choice_claim_allowed": False,
        "route_arbitration_alone_is_semantic_choice": False,
        "oscillator_inheritance_promotes_choice": False,
        "memory_trail_deferred_to": "N08",
        "blocked_claims": [
            "memory_or_trail",
            "agency",
            "agentic_like_behavior",
            "rc_identity_collapse",
            "identity_acceptance",
            "goal_proxy_regulation",
            "locomotion_like_behavior",
            "biological_behavior",
            "ant_colony_behavior",
            "unrestricted_movement",
        ],
    }


def _baseline_decisions() -> dict[str, Any]:
    return {
        "route_choice_probe_run": False,
        "oscillator_claim_inherited": False,
        "memory_trail_claim_inherited": False,
        "native_lane_runtime_decision": (
            "native N06 route-arbitration rows must run at LGRC-3; any LGRC-2 "
            "early lanes are experiment-local scaffolds or controls"
        ),
        "context_mapping_decision_status": "deferred_to_iteration_2_fixture_manifest",
        "selected_context_mapping": None,
        "recommended_iteration_2_context_mapping": (
            "candidate_score_components plus candidate_runtime_visible_inputs "
            "and arbitration_runtime_visible_inputs"
        ),
        "recommended_iteration_2_compatibility_gate": (
            "native_score_components_with_threshold_interpretation"
        ),
        "selected_compatibility_gate_representation": None,
        "selected_arbitration_window_boundary": None,
        "arbitration_window_boundary_deferred_to_iteration_2": True,
        "selected_candidate_source_fields": None,
        "native_route_arbitration_policy_gate": "policy != disabled",
        "recommended_iteration_2_native_policy": (
            "score_ordered_topology_route_candidates"
        ),
        "n04_phase8_artifacts_are_precedent_not_n06_evidence": True,
    }


def _write_report(result: Mapping[str, Any]) -> None:
    source_lines = "\n".join(
        (
            f"| `{record['name']}` | `{record['exists']}` | "
            f"`{record.get('sha256')}` | `{record['path']}` |"
        )
        for record in result["source_artifacts"]
    )
    surface = result["native_route_arbitration_surfaces"]
    context = result["context_affordance_inventory"]
    claim_flags = "\n".join(
        f"- `{key}` = `{value}`"
        for key, value in sorted(result["claim_boundary"]["claim_flags"].items())
    )
    required_fields = "\n".join(
        f"- `{field}`" for field in result["sc_ladder_schema"]["row_required_fields"]
    )
    REPORT_PATH.write_text(
        f"""# N06 Iteration 1: Baseline And Schema Inventory

Status: {result['status']}.

## Purpose

Iteration 1 is inventory-only. It runs no route-choice probes and does not
change `src/*`.

## N05 Inheritance

```json
{json.dumps(result['n05_inheritance'], indent=2, sort_keys=True)}
```

N06 inherits only oscillator/circuit background from N05. It does not inherit
semantic choice, memory/trail, agency, identity, ACO, locomotion, or unrestricted
movement claims.

## Native Route-Arbitration Contract

Native route arbitration is LGRC-3/topology-changing-causal-history gated:

```json
{json.dumps(surface['native_runtime_gate'], indent=2, sort_keys=True)}
```

Validator:

```json
{json.dumps(surface['native_route_arbitration_contract']['validator_signature'], indent=2, sort_keys=True)}
```

Validator failure modes:

```json
{json.dumps(surface['native_route_arbitration_contract']['validator_failure_modes'], indent=2, sort_keys=True)}
```

Reason codes:

```json
{json.dumps(surface['reason_codes'], indent=2, sort_keys=True)}
```

Score invariant:

```json
{json.dumps(surface['candidate_record_fields']['score_component_invariant'], indent=2, sort_keys=True)}
```

Candidate-set ordering and ties:

```json
{json.dumps({'candidate_set_ordering': surface['candidate_set_ordering'], 'declared_tiebreaker_serialization': surface['declared_tiebreaker_serialization']}, indent=2, sort_keys=True)}
```

## Context/Affordance Mapping

```json
{json.dumps(context, indent=2, sort_keys=True)}
```

N06 has no dedicated native `context_surface` record type at baseline. Iteration
2 must choose the concrete mapping before fixture probes run.

## SC Row Schema

Required fields:

{required_fields}

## Claim Boundary

{claim_flags}

## Source Artifacts

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
{source_lines}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance Result

Achieved. N06 has a source-backed baseline inventory, frozen SC-ladder row
schema, explicit blocked claim flags, native LGRC-3 route-arbitration gate
record, context/affordance mapping inventory, and no route-choice probe
evidence or claim promotion.
""",
        encoding="utf-8",
    )


def main() -> None:
    source_artifacts = _source_artifacts()
    result: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "run_id": "n06_iteration_1_baseline_inventory_v1",
        "iteration": 1,
        "status": "passed",
        "command": COMMAND,
        "runtime_family": "LGRC9V3",
        "execution_stage": "baseline_inventory_no_route_choice_probe",
        "route_choice_probe_run": False,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
        "source_artifacts": source_artifacts,
        "n05_inheritance": _n05_inheritance(),
        "native_route_arbitration_surfaces": _native_route_arbitration_surfaces(),
        "context_affordance_inventory": _context_affordance_inventory(),
        "sc_ladder_schema": _sc_ladder_schema(),
        "claim_boundary": _claim_boundary(),
        "baseline_decisions": _baseline_decisions(),
        "controls_inventory": {
            "negative_controls_required_from_iteration_2": [
                "policy_disabled",
                "no_candidates",
                "unresolved_tie",
                "hidden_context",
                "hidden_route_preference",
                "preselected_sink",
                "experiment_side_if_else",
                "report_side_selection",
                "posthoc_threshold_change",
                "budget_mismatch",
                "order_inversion",
                "stale_candidate",
                "stale_context",
                "duplicate_arbitration",
                "producer_mutation",
                "claim_promotion",
            ],
            "distinct_primary_blockers_required": True,
        },
        "acceptance": {
            "source_backed_inventory": all(
                record["exists"]
                for record in source_artifacts
                if record["name"]
                in {
                    "n06_readme",
                    "n06_plan",
                    "n06_checklist",
                    "n05_closeout",
                    "lgrc9v3_contract_source",
                    "lgrc9v3_runtime_source",
                }
            ),
            "sc_schema_frozen": True,
            "claim_flags_frozen_false": all(
                value is False for value in CLAIM_FLAGS_FALSE.values()
            ),
            "no_route_choice_probe_run": True,
            "no_src_changes_required": True,
        },
    }
    result["artifact_digests"] = {
        "source_artifacts_digest": _digest(result["source_artifacts"]),
        "native_route_arbitration_surfaces_digest": _digest(
            result["native_route_arbitration_surfaces"]
        ),
        "context_affordance_inventory_digest": _digest(
            result["context_affordance_inventory"]
        ),
        "sc_ladder_schema_digest": _digest(result["sc_ladder_schema"]),
        "claim_boundary_digest": _digest(result["claim_boundary"]),
    }
    if not all(result["acceptance"].values()):
        result["status"] = "failed"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "route_choice_probe_run": result["route_choice_probe_run"],
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "native_runtime_level": result[
                    "native_route_arbitration_surfaces"
                ]["native_runtime_gate"]["lgrc_runtime_level"],
                "context_surface_dedicated_native_type": result[
                    "context_affordance_inventory"
                ]["dedicated_native_context_surface_exists"],
                "claim_flags_frozen_false": result["acceptance"][
                    "claim_flags_frozen_false"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
