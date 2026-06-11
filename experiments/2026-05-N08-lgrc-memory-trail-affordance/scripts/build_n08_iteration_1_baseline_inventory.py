#!/usr/bin/env python3
"""Build N08 Iteration 1 baseline and schema inventory artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_1_baseline_inventory.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_1_baseline_inventory.md"

N05_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N05-lgrc-coherence-waves-oscillators"
    / "outputs"
    / "n05_iteration_8_o6_closeout.json"
)
N05_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N05-lgrc-coherence-waves-oscillators"
    / "reports"
    / "n05_iteration_8_o6_closeout.md"
)
N06_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "outputs"
    / "n06_iteration_8_sc6_closeout.json"
)
N06_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "reports"
    / "n06_iteration_8_sc6_closeout.md"
)
N07_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "outputs"
    / "n07_iteration_12_long_horizon_compatibility_closeout.json"
)
N07_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "reports"
    / "n07_iteration_12_long_horizon_compatibility_closeout.md"
)
N07_11B_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "outputs"
    / "n07_iteration_11b_neutral_absorber_reservoir.json"
)
N07_11B_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N07-rc-identity-attractor-invariance"
    / "reports"
    / "n07_iteration_11b_neutral_absorber_reservoir.md"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def inventory_stable_digest(inventory: dict[str, Any]) -> str:
    """Digest deterministic inventory sections, excluding run-local metadata."""
    excluded_keys = {"generated_at", "inventory_digest"}
    digest_input = {
        key: value for key, value in inventory.items() if key not in excluded_keys
    }
    return canonical_digest(digest_input)


def git_status_short_src() -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "src"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def import_native_route_contract() -> tuple[list[str], list[str]]:
    sys.path.insert(0, str(ROOT / "src"))
    from pygrc.models.lgrc_9_v3_contract import (  # noqa: WPS433
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS,
    )

    return (
        sorted(LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS),
        sorted(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS),
    )


def n06_cycles(n06: dict[str, Any]) -> list[dict[str, Any]]:
    closeout = n06.get("artifact_only_closeout", {})
    cycles = closeout.get("per_cycle", [])
    if not isinstance(cycles, list):
        return []
    return [cycle for cycle in cycles if isinstance(cycle, dict)]


def n06_source_arbitration_record_id(cycle: dict[str, Any]) -> str | None:
    for reason in cycle.get("expected_incomplete_reasons", []):
        parts = str(reason).split(":")
        if len(parts) >= 3 and parts[1] == "native-route-arbitration":
            return f"{parts[1]}:{parts[2]}"
    return None


def n06_cycle_structure_valid(cycles: list[dict[str, Any]]) -> bool:
    required_cycle_keys = {
        "cycle_id",
        "candidate_set_digest",
        "selected_candidate_route_digest",
        "rejected_candidate_route_digests",
        "candidate_score_component_sums",
        "candidate_context_values",
    }
    return bool(cycles) and all(required_cycle_keys.issubset(cycle) for cycle in cycles)


def build_inventory() -> dict[str, Any]:
    n05 = load_json(N05_OUTPUT)
    n06 = load_json(N06_OUTPUT)
    n07 = load_json(N07_OUTPUT)
    n07_11b = load_json(N07_11B_OUTPUT)
    route_forbidden, surface_forbidden = import_native_route_contract()

    proposed_memory_components = [
        "memory_trail_strength",
        "memory_surface_digest_match",
        "memory_recency_weight",
        "memory_decay_adjusted_strength",
    ]
    required_runtime_visible_inputs = [
        "memory_surface_id",
        "memory_surface_digest",
        "memory_surface_state_snapshot_digest",
        "memory_policy_id",
        "route_use_event_digest",
        "memory_event_time_key",
    ]

    n05_route_fields = n05["o6_boundary"]["route_coupling_fields"]
    n06_cycle_rows = n06_cycles(n06)
    n07_row = n07["long_horizon_closeout_row"]
    n07_11b_row = n07_11b["long_horizon_candidate_row"]

    n06_route_digest_rows = []
    for cycle in n06_cycle_rows:
        n06_route_digest_rows.append(
            {
                "cycle_id": cycle.get("cycle_id"),
                "context_state_id": cycle.get("context_state_id"),
                "candidate_set_digest": cycle.get("candidate_set_digest"),
                "selected_route": cycle.get("selected_route"),
                "selected_candidate_route_digest": cycle.get(
                    "selected_candidate_route_digest"
                ),
                "rejected_candidate_route_digests": cycle.get(
                    "rejected_candidate_route_digests", []
                ),
                "candidate_source_surface_digests": cycle.get(
                    "candidate_source_surface_digests", []
                ),
                "candidate_score_component_sums": cycle.get(
                    "candidate_score_component_sums", {}
                ),
                "candidate_context_values": cycle.get("candidate_context_values", {}),
                "source_surface_provenance": cycle.get("source_surface_provenance", {}),
                "scheduled_processed_packet_evidence": cycle.get(
                    "scheduled_processed_packet_evidence", {}
                ),
                "expected_incomplete_reasons": cycle.get(
                    "expected_incomplete_reasons", []
                ),
                "source_arbitration_record_id": n06_source_arbitration_record_id(cycle),
            }
        )

    native_component_rows = []
    for component in proposed_memory_components:
        in_route_forbidden = component in route_forbidden
        in_surface_forbidden = component in surface_forbidden
        native_component_rows.append(
            {
                "component_name": component,
                "route_candidate_score_key_allowed_by_current_native_contract": (
                    not in_route_forbidden
                ),
                "component_name_is_forbidden_route_input": in_route_forbidden,
                "component_name_is_forbidden_surface_key": in_surface_forbidden,
                "native_memory_semantics_exist": False,
                "required_runtime_visible_inputs": required_runtime_visible_inputs,
                "blocker_if_used_without_memory_surface": (
                    "native_memory_candidate_score_component_semantics_missing"
                ),
            }
        )

    claim_flags = {
        "memory_or_trail_claim_allowed": False,
        "aco_like_claim_allowed": False,
        "agency_claim_allowed": False,
        "agentic_like_claim_allowed": False,
        "ant_colony_claim_allowed": False,
        "intention_claim_allowed": False,
        "goal_proxy_regulation_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "runtime_identity_acceptance_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "biological_claim_allowed": False,
        "personhood_claim_allowed": False,
        "movement_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }

    mem_ladder = {
        "MEM0": "external_or_label_only_memory_no_runtime_visible_route_use_event",
        "MEM1": "route_use_event_trace_recorded_with_digest_and_budget",
        "MEM2": "persisted_trail_or_affordance_memory_surface_after_route_use",
        "MEM3": "serialized_decay_or_reinforcement_update_with_budget",
        "MEM4": "memory_surface_digest_shapes_candidate_route_score",
        "MEM5": "repeated_memory_shaped_selection_over_multiple_cycles",
        "MEM6": "artifact_only_replay_of_route_use_memory_update_arbitration_controls",
    }

    frozen_row_schema = [
        "row_id",
        "mem_level",
        "mem_level_is_evidence_classification",
        "claim_ceiling",
        "claim_flags",
        "source_artifacts",
        "source_reports",
        "route_use_event_id",
        "route_use_event_digest",
        "route_use_commit_status",
        "route_id",
        "selected_route_id",
        "route_aspect_digest",
        "source_arbitration_record_digest",
        "selected_candidate_route_digest",
        "rejected_candidate_route_digests",
        "memory_surface_id",
        "memory_surface_digest",
        "memory_surface_key",
        "memory_surface_key_digest",
        "source_support_area_digest",
        "target_support_area_digest",
        "support_area_id",
        "support_area_digest",
        "memory_policy_id",
        "memory_policy_digest",
        "decay_policy_id",
        "reinforcement_policy_id",
        "memory_surface_state_snapshot",
        "memory_surface_state_snapshot_digest",
        "candidate_route_digests",
        "candidate_set_digest",
        "native_route_arbitration_record_digest",
        "event_time_key",
        "scheduler_event_index",
        "node_plus_packet_budget_before",
        "node_plus_packet_budget_after",
        "node_plus_packet_budget_error",
        "memory_budget_surface",
        "memory_budget_before",
        "memory_budget_after",
        "memory_budget_error",
        "native_support_status",
        "native_policy_blockers",
        "visual_reference",
        "visual_is_evidence_source",
    ]

    native_policy_blockers = [
        "native_route_conductance_memory_policy_missing",
        "native_trail_memory_surface_missing",
        "native_memory_surface_serialization_policy_missing",
        "native_memory_surface_keying_policy_missing",
        "native_memory_budget_accounting_policy_missing",
        "native_memory_cross_cycle_persistence_policy_missing",
        "native_memory_decay_policy_missing",
        "native_memory_reinforcement_policy_missing",
        "native_memory_candidate_score_component_semantics_missing",
        "native_memory_artifact_replay_validator_missing",
    ]

    memory_surface_key_contract = {
        "field_type": "canonical_json_object",
        "field_name": "memory_surface_key",
        "required_fields": [
            "route_id",
            "source_support_area_digest",
            "target_support_area_digest",
            "route_aspect_digest",
            "memory_policy_id",
        ],
        "digest_field_name": "memory_surface_key_digest",
        "digest_rule": "sha256(canonical_json(memory_surface_key))",
        "not_a_scalar_string": True,
        "not_hidden_process_memory": True,
    }

    required_gates = [
        "MEM6 required",
        "artifact-only replay passes",
        "route-use events replay",
        "memory surface state reconstructs",
        "decay/reinforcement policies replay",
        "memory-derived candidate scores recompute exactly",
        "controls fail with distinct blockers",
        "node-plus-packet budget passes",
        "memory budget passes",
        "does not promote ACO, agency, identity, or locomotion claims",
    ]

    inventory: dict[str, Any] = {
        "schema": "n08_iteration_1_baseline_inventory_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 1,
        "status": "passed",
        "purpose": "baseline_schema_inventory_no_memory_probe",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": (
            ".venv/bin/python "
            "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
            "build_n08_iteration_1_baseline_inventory.py"
        ),
        "source_artifacts": {
            rel(N05_OUTPUT): sha256_file(N05_OUTPUT),
            rel(N06_OUTPUT): sha256_file(N06_OUTPUT),
            rel(N07_OUTPUT): sha256_file(N07_OUTPUT),
            rel(N07_11B_OUTPUT): sha256_file(N07_11B_OUTPUT),
        },
        "source_reports": {
            rel(N05_REPORT): sha256_file(N05_REPORT),
            rel(N06_REPORT): sha256_file(N06_REPORT),
            rel(N07_REPORT): sha256_file(N07_REPORT),
            rel(N07_11B_REPORT): sha256_file(N07_11B_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "memory_probe_run": False,
        "n05_inventory": {
            "source_artifact": rel(N05_OUTPUT),
            "status": n05.get("status"),
            "strongest_supported_o_level": n05["n05_closeout"][
                "strongest_supported_o_level"
            ],
            "strongest_claim_ceiling": n05["n05_closeout"][
                "strongest_claim_ceiling"
            ],
            "o6_supported": n05["n05_closeout"]["o6_supported"],
            "o6_primary_blocker": n05["n05_closeout"]["o6_primary_blocker"],
            "route_aspect_serialized": bool(n05_route_fields.get("route_aspect_digest")),
            "route_aspect_fields": n05_route_fields,
            "route_memory_absent_fields": {
                "route_conductance_memory_digest": n05_route_fields.get(
                    "route_conductance_memory_digest"
                ),
                "route_conductance_memory_policy_id": n05_route_fields.get(
                    "route_conductance_memory_policy_id"
                ),
                "trail_reinforcement_surface_digest": n05_route_fields.get(
                    "trail_reinforcement_surface_digest"
                ),
                "route_memory_runtime_visible": n05["o6_boundary"][
                    "route_memory_runtime_visible"
                ],
                "trail_memory_blocker": n05["o6_boundary"]["trail_memory_blocker"],
            },
            "phase3_native_policy_blockers": n05[
                "phase3_native_policy_support_audit"
            ]["native_policy_blockers"],
        },
        "n06_inventory": {
            "source_artifact": rel(N06_OUTPUT),
            "status": n06.get("status"),
            "strongest_supported_sc_level": n06["closeout"][
                "strongest_supported_sc_level"
            ],
            "strongest_claim_ceiling": n06["closeout"]["strongest_claim_ceiling"],
            "selection_scope": n06["closeout"][
                "scheduled_processed_packet_evidence_applicability"
            ],
            "candidate_route_records_present": all(
                cycle.get("checks", {}).get("candidate_route_records_replayed")
                for cycle in n06_cycle_rows
            ),
            "candidate_set_records_present": all(
                cycle.get("checks", {}).get("candidate_set_record_replayed")
                for cycle in n06_cycle_rows
            ),
            "native_route_arbitration_records_present": all(
                cycle.get("checks", {}).get("native_route_arbitration_record_replayed")
                for cycle in n06_cycle_rows
            ),
            "candidate_score_components_present": all(
                bool(cycle.get("candidate_score_component_sums"))
                for cycle in n06_cycle_rows
            ),
            "context_surfaces_present": all(
                bool(cycle.get("candidate_context_values", {}).get("context_surface_digest"))
                for cycle in n06_cycle_rows
            ),
            "selected_and_rejected_route_digests_present": all(
                bool(cycle.get("selected_candidate_route_digest"))
                and isinstance(cycle.get("rejected_candidate_route_digests"), list)
                for cycle in n06_cycle_rows
            ),
            "cycle_count": len(n06_cycle_rows),
            "route_digest_rows": n06_route_digest_rows,
            "route_use_boundary_for_n08": {
                "n06_selection_is_committed_route_use": False,
                "reason": (
                    "N06 SC6 is selection-only and pre-topology; N08 MEM1 "
                    "requires a new ordered route-use event."
                ),
                "required_next_record": "n08_route_use_event",
            },
        },
        "n07_inventory": {
            "source_artifact": rel(N07_OUTPUT),
            "source_11b_artifact": rel(N07_11B_OUTPUT),
            "status": n07.get("status"),
            "frozen_n07_ceiling": n07["closeout_decision"]["frozen_n07_ceiling"],
            "frozen_long_horizon_c3_class": n07["closeout_decision"][
                "frozen_long_horizon_c3_class"
            ],
            "runtime_identity_acceptance_claim_allowed": n07["closeout_decision"][
                "runtime_identity_acceptance_claim_allowed"
            ],
            "support_area_id": n07_row.get("support_area_id"),
            "support_area_digest": n07_row.get("support_area_digest"),
            "source_specific_support_anchor": {
                "candidate_identity_carrier_type": n07_row.get(
                    "candidate_identity_carrier_type"
                ),
                "identity_carrier_surface": n07_row.get("identity_carrier_surface"),
                "source_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "A_support_area_digest"
                ),
                "target_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "B_support_area_digest"
                ),
                "reservoir_runtime_visible_inputs": n07_11b.get(
                    "reservoir_policy", {}
                ).get("runtime_visible_inputs", {}),
            },
            "claim_boundary_fields": {
                key: value
                for key, value in n07["claim_flags"].items()
                if key.endswith("_claim_allowed")
            },
            "n07_11b_candidate_row": {
                "row_id": n07_11b_row.get("row_id"),
                "claim_ceiling": n07_11b_row.get("claim_ceiling"),
                "trajectory_regime": n07_11b_row.get("trajectory_regime"),
                "support_area_id": n07_11b_row.get("support_area_id"),
                "support_area_digest": n07_11b_row.get("support_area_digest"),
                "candidate_row_digest": n07_11b_row.get("candidate_row_digest"),
                "native_support_status": n07_11b_row.get("native_support_status"),
            },
        },
        "available_native_memory_like_surfaces": {
            "route_aspect_surface_from_n05": {
                "available": True,
                "native_memory_surface": False,
                "route_aspect_digest": n05_route_fields.get("route_aspect_digest"),
                "limitation": (
                    "route aspect is replayable carrier/circuit evidence, "
                    "not route conductance memory"
                ),
            },
            "native_route_candidate_score_components": {
                "available": True,
                "native_memory_surface": False,
                "semantics": (
                    "arbitrary finite non-forbidden component keys can be "
                    "serialized, but memory/trail semantics must be supplied "
                    "by N08 artifact rows until Phase 8 adds native memory"
                ),
            },
            "native_route_candidate_runtime_visible_inputs": {
                "available": True,
                "native_memory_surface": False,
                "semantics": (
                    "runtime-visible input names can cite memory artifact "
                    "digests later, but current core has no memory surface "
                    "validator"
                ),
            },
            "n07_support_area_anchors": {
                "available": True,
                "native_memory_surface": False,
                "support_area_id": n07_row.get("support_area_id"),
                "support_area_digest": n07_row.get("support_area_digest"),
                "source_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "A_support_area_digest"
                ),
                "target_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "B_support_area_digest"
                ),
            },
        },
        "missing_native_memory_policy_surfaces": native_policy_blockers,
        "native_route_arbitration_contract_inventory": {
            "forbidden_input_keys": route_forbidden,
            "forbidden_surface_keys_relevant_to_claims": [
                key
                for key in surface_forbidden
                if key.endswith("_claim_allowed") or "claim" in key
            ],
            "candidate_score_component_contract": {
                "score_components_must_not_be_empty": True,
                "score_components_must_be_finite": True,
                "candidate_route_score_equals_sum_components": True,
                "candidate_runtime_visible_inputs_must_not_be_empty": True,
                "candidate_budget_prediction_required": True,
                "candidate_lineage_transfer_map_required": True,
            },
            "proposed_memory_components": native_component_rows,
            "all_proposed_memory_components_allowed_as_component_names": all(
                row["route_candidate_score_key_allowed_by_current_native_contract"]
                for row in native_component_rows
            ),
            "memory_semantics_native_supported": False,
        },
        "n07_support_fields_available_as_memory_keys": {
            "support_area_id": n07_row.get("support_area_id") is not None,
            "support_area_digest": n07_row.get("support_area_digest") is not None,
            "source_support_area_digest": n07_11b.get("source_metrics", {}).get(
                "A_support_area_digest"
            )
            is not None,
            "target_support_area_digest": n07_11b.get("source_metrics", {}).get(
                "B_support_area_digest"
            )
            is not None,
            "field_values": {
                "support_area_id": n07_row.get("support_area_id"),
                "support_area_digest": n07_row.get("support_area_digest"),
                "source_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "A_support_area_digest"
                ),
                "target_support_area_digest": n07_11b.get("source_metrics", {}).get(
                    "B_support_area_digest"
                ),
            },
        },
        "mem_ladder": mem_ladder,
        "frozen_mem_row_schema": frozen_row_schema,
        "memory_surface_key_contract": memory_surface_key_contract,
        "claim_flags": claim_flags,
        "memory_or_trail_promotion_criteria": {
            "memory_or_trail_claim_allowed_initial": False,
            "status": "criteria_defined_not_satisfied_iteration_1",
            "blocked_until": "MEM6",
            "required_gates": required_gates,
        },
        "baseline_json_report_schema": {
            "json_required_sections": [
                "n05_inventory",
                "n06_inventory",
                "n07_inventory",
                "available_native_memory_like_surfaces",
                "missing_native_memory_policy_surfaces",
                "native_route_arbitration_contract_inventory",
                "n07_support_fields_available_as_memory_keys",
                "mem_ladder",
                "frozen_mem_row_schema",
                "memory_surface_key_contract",
                "claim_flags",
                "memory_or_trail_promotion_criteria",
                "checks",
            ],
            "report_required_sections": [
                "Result",
                "Inherited Evidence Inventory",
                "Native Contract Inventory",
                "Frozen MEM Schema",
                "Memory Surface Key Contract",
                "Claim Boundary",
                "Source Report Digests",
                "Acceptance Result",
            ],
        },
    }

    checks = {
        "n05_status_passed": inventory["n05_inventory"]["status"] == "passed",
        "n05_o5_inventory_present": inventory["n05_inventory"][
            "strongest_supported_o_level"
        ]
        == "O5",
        "n05_o6_blocker_recorded": inventory["n05_inventory"]["o6_primary_blocker"]
        == "missing_route_conductance_memory_policy",
        "n05_route_memory_absent": inventory["n05_inventory"][
            "route_memory_absent_fields"
        ]["route_memory_runtime_visible"]
        is False,
        "n06_status_passed": inventory["n06_inventory"]["status"] == "passed",
        "n06_sc6_inventory_present": inventory["n06_inventory"][
            "strongest_supported_sc_level"
        ]
        == "SC6",
        "n06_candidate_route_records_present": inventory["n06_inventory"][
            "candidate_route_records_present"
        ],
        "n06_candidate_set_records_present": inventory["n06_inventory"][
            "candidate_set_records_present"
        ],
        "n06_native_route_arbitration_records_present": inventory["n06_inventory"][
            "native_route_arbitration_records_present"
        ],
        "n06_candidate_score_components_present": inventory["n06_inventory"][
            "candidate_score_components_present"
        ],
        "n06_cycle_structure_valid": n06_cycle_structure_valid(n06_cycle_rows),
        "n06_selection_not_route_use": inventory["n06_inventory"][
            "route_use_boundary_for_n08"
        ]["n06_selection_is_committed_route_use"]
        is False,
        "n07_status_passed": inventory["n07_inventory"]["status"] == "passed",
        "n07_bounded_exchange_inventory_present": inventory["n07_inventory"][
            "frozen_long_horizon_c3_class"
        ]
        == "bounded_non_destructive_exchange",
        "n07_support_fields_present": all(
            inventory["n07_support_fields_available_as_memory_keys"][key]
            for key in (
                "support_area_id",
                "support_area_digest",
                "source_support_area_digest",
                "target_support_area_digest",
            )
        ),
        "forbidden_inputs_inventoried": bool(route_forbidden),
        "proposed_memory_score_components_not_forbidden": inventory[
            "native_route_arbitration_contract_inventory"
        ]["all_proposed_memory_components_allowed_as_component_names"],
        "native_candidate_score_components_can_carry_memory_keys_by_name": all(
            row["route_candidate_score_key_allowed_by_current_native_contract"]
            for row in native_component_rows
        ),
        "native_memory_semantics_missing_recorded": inventory[
            "native_route_arbitration_contract_inventory"
        ]["memory_semantics_native_supported"]
        is False,
        "missing_native_memory_policy_surfaces_recorded": len(native_policy_blockers)
        >= 8,
        "mem_ladder_complete": sorted(mem_ladder) == [
            "MEM0",
            "MEM1",
            "MEM2",
            "MEM3",
            "MEM4",
            "MEM5",
            "MEM6",
        ],
        "frozen_row_schema_has_memory_snapshot": (
            "memory_surface_state_snapshot" in frozen_row_schema
            and "memory_surface_state_snapshot_digest" in frozen_row_schema
        ),
        "memory_surface_key_contract_explicit": (
            inventory["memory_surface_key_contract"]["field_type"]
            == "canonical_json_object"
            and "memory_surface_key_digest" in frozen_row_schema
        ),
        "frozen_row_schema_has_budget_split": (
            "node_plus_packet_budget_error" in frozen_row_schema
            and "memory_budget_error" in frozen_row_schema
        ),
        "claim_flags_all_false": all(value is False for value in claim_flags.values()),
        "memory_or_trail_requires_mem6": inventory[
            "memory_or_trail_promotion_criteria"
        ]["blocked_until"]
        == "MEM6",
        "promotion_criteria_encoded_as_required_gates": bool(
            inventory["memory_or_trail_promotion_criteria"]["required_gates"]
        ),
        "baseline_json_schema_self_validates": all(
            key in inventory or key == "checks"
            for key in inventory["baseline_json_report_schema"][
                "json_required_sections"
            ]
        ),
        "n07_11b_report_digest_recorded": rel(N07_11B_REPORT)
        in inventory["source_reports"],
        "memory_probe_not_run": inventory["memory_probe_run"] is False,
        "src_clean_for_iteration_1": inventory["git"]["src_clean"],
    }
    inventory["checks"] = checks
    inventory["acceptance"] = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 1 passes if N08 has a source-backed baseline inventory "
            "of inherited N05/N06/N07 artifacts, a frozen MEM ladder and row "
            "schema, a recorded native memory/trail policy gap inventory, "
            "clean claim boundaries, and no memory probe execution."
        ),
    }
    inventory["inventory_digest_scope"] = {
        "included": "all inventory fields except generated_at and inventory_digest",
        "excluded": ["generated_at", "inventory_digest"],
        "stable_across_same_inputs": True,
    }
    inventory["inventory_digest"] = inventory_stable_digest(inventory)
    inventory["status"] = inventory["acceptance"]["status"]
    return inventory


def write_report(inventory: dict[str, Any]) -> None:
    n05 = inventory["n05_inventory"]
    n06 = inventory["n06_inventory"]
    n07 = inventory["n07_inventory"]
    checks = inventory["checks"]
    blocker_lines = "\n".join(
        f"- `{blocker}`"
        for blocker in inventory["missing_native_memory_policy_surfaces"]
    )
    component_lines = "\n".join(
        "- `{component_name}`: allowed as route-score key = `{allowed}`, "
        "native memory semantics = `{semantics}`".format(
            component_name=row["component_name"],
            allowed=row["route_candidate_score_key_allowed_by_current_native_contract"],
            semantics=row["native_memory_semantics_exist"],
        )
        for row in inventory["native_route_arbitration_contract_inventory"][
            "proposed_memory_components"
        ]
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    schema_lines = "\n".join(
        f"- `{field}`" for field in inventory["frozen_mem_row_schema"]
    )
    key_contract = inventory["memory_surface_key_contract"]
    key_contract_lines = "\n".join(
        f"- `{field}`" for field in key_contract["required_fields"]
    )
    promotion_gate_lines = "\n".join(
        f"- {gate}"
        for gate in inventory["memory_or_trail_promotion_criteria"][
            "required_gates"
        ]
    )
    report = f"""# N08 Iteration 1 Baseline And Schema Inventory

Status: `{inventory['status']}`.

## Result

Iteration 1 built a source-backed baseline inventory from existing N05, N06,
and N07 closeout artifacts only. No N08 memory probe was run.

The current N08 starting boundary is:

```text
MEM evidence = not yet produced
native memory/trail surface = missing
route-score component carrier = available for non-forbidden serialized keys
memory/trail semantics = experiment-local until a later Phase 8 task exists
memory_or_trail_claim_allowed = false
```

## Inherited Evidence Inventory

N05:

- strongest O-level: `{n05['strongest_supported_o_level']}`
- claim ceiling: `{n05['strongest_claim_ceiling']}`
- O6 supported: `{n05['o6_supported']}`
- O6 blocker: `{n05['o6_primary_blocker']}`
- route-aspect digest: `{n05['route_aspect_fields']['route_aspect_digest']}`
- route conductance memory digest: `{n05['route_memory_absent_fields']['route_conductance_memory_digest']}`
- Phase 3 native policy blockers:
  `{n05['phase3_native_policy_blockers']}`

N06:

- strongest SC-level: `{n06['strongest_supported_sc_level']}`
- claim ceiling: `{n06['strongest_claim_ceiling']}`
- cycle count: `{n06['cycle_count']}`
- candidate route records present: `{n06['candidate_route_records_present']}`
- candidate set records present: `{n06['candidate_set_records_present']}`
- native route-arbitration records present: `{n06['native_route_arbitration_records_present']}`
- N06 selection counts as N08 route use: `{n06['route_use_boundary_for_n08']['n06_selection_is_committed_route_use']}`

N07:

- frozen ceiling: `{n07['frozen_n07_ceiling']}`
- C3 class: `{n07['frozen_long_horizon_c3_class']}`
- support area id: `{n07['support_area_id']}`
- support area digest: `{n07['support_area_digest']}`
- runtime identity acceptance allowed: `{n07['runtime_identity_acceptance_claim_allowed']}`

## Native Contract Inventory

Native route-arbitration forbidden input keys:

```json
{json.dumps(inventory['native_route_arbitration_contract_inventory']['forbidden_input_keys'], indent=2)}
```

Proposed N08 memory score components:

{component_lines}

This means the current native candidate-score contract can carry these names as
serialized score-component keys, but it does not supply memory/trail semantics
by itself. N08 must serialize route-use events, memory surfaces, memory policy,
and memory state snapshots as experiment-local artifacts unless a Phase 8 task
adds native memory support.

Missing native memory/trail policy surfaces:

{blocker_lines}

## Frozen MEM Schema

The MEM0-MEM6 ladder is frozen as evidence classification only. Claim flags are
separate from MEM levels.

Frozen row fields:

{schema_lines}

## Memory Surface Key Contract

`memory_surface_key` is frozen as a canonical JSON object, not a scalar string.
It must contain exactly the replay-relevant route/support/policy identity
fields needed by later memory rows:

{key_contract_lines}

Digest rule:

```text
{key_contract['digest_field_name']} = {key_contract['digest_rule']}
```

The row schema therefore also includes `{key_contract['digest_field_name']}`.
Iteration 2 must instantiate this contract in the fixture manifest before
positive memory probes run.

## Claim Boundary

All claim flags remain false. The narrow
`memory_or_trail_claim_allowed` flag requires MEM6 artifact-only replay and
does not promote ACO, agency, intention, goal regulation, RC identity collapse,
identity acceptance, locomotion-like behavior, biological behavior, personhood,
unrestricted identity, or unrestricted movement.

Promotion criteria are required gates, not achieved Iteration 1 results:

{promotion_gate_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Artifact Digests

```json
{json.dumps(inventory['source_artifacts'], indent=2, sort_keys=True)}
```

## Source Report Digests

```json
{json.dumps(inventory['source_reports'], indent=2, sort_keys=True)}
```

## Acceptance Result

Achieved: `{inventory['acceptance']['achieved']}`.

Inventory digest scope:

```json
{json.dumps(inventory['inventory_digest_scope'], indent=2, sort_keys=True)}
```

Inventory digest: `{inventory['inventory_digest']}`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(inventory)


if __name__ == "__main__":
    main()
