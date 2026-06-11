#!/usr/bin/env python3
"""Build and validate the N08 Iteration 2 fixture manifest.

Iteration 2 is contract-only. It defines route-use and memory-surface schemas,
ordering, budgets, policies, and controls before any positive memory probe runs.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
BASELINE_PATH = EXPERIMENT / "outputs" / "n08_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n08_fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "build_n08_iteration_2_fixture_manifest.py"
)

ROUTE_USE_REQUIRED_FIELDS = [
    "route_use_event_id",
    "route_use_commit_status",
    "source_arbitration_record_digest",
    "source_candidate_set_digest",
    "selected_candidate_route_digest",
    "selected_route_id",
    "route_aspect_digest",
    "source_support_area_digest",
    "target_support_area_digest",
    "topology_commit_required",
    "event_time_key",
    "scheduler_event_index",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "claim_flags",
    "route_use_event_digest",
]

MEMORY_SURFACE_REQUIRED_FIELDS = [
    "memory_surface_id",
    "memory_surface_kind",
    "route_use_event_digest",
    "memory_surface_key",
    "memory_surface_key_digest",
    "memory_policy_id",
    "memory_policy_digest",
    "memory_strength",
    "event_time_key",
    "scheduler_event_index",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "memory_budget_surface",
    "memory_budget_before",
    "reinforcement_input",
    "decay_loss",
    "saturation_clamp_loss",
    "memory_budget_after",
    "memory_budget_error",
    "claim_flags",
    "memory_surface_digest",
]

MEMORY_KEY_FIELDS = [
    "route_id",
    "source_support_area_digest",
    "target_support_area_digest",
    "route_aspect_digest",
    "memory_policy_id",
]

REQUIRED_MEMORY_SCORE_COMPONENTS = [
    "memory_trail_strength",
    "memory_surface_digest_match",
    "memory_recency_weight",
    "memory_decay_adjusted_strength",
]

REQUIRED_RUNTIME_VISIBLE_INPUTS = [
    "memory_surface_id",
    "memory_surface_digest",
    "memory_surface_state_snapshot_digest",
    "memory_policy_id",
    "route_use_event_digest",
    "memory_event_time_key",
]

REQUIRED_CONTROL_BLOCKERS = {
    "hidden_route_history": "hidden_route_history",
    "missing_route_use_event": "missing_route_use_event",
    "memory_surface_missing": "memory_surface_missing",
    "memory_surface_digest_mismatch": "memory_surface_digest_mismatch",
    "memory_surface_poisoned": "memory_surface_poisoned",
    "memory_policy_missing": "memory_policy_missing",
    "memory_policy_hidden_preference": "memory_policy_hidden_preference",
    "decay_policy_missing": "decay_policy_missing",
    "reinforcement_policy_missing": "reinforcement_policy_missing",
    "candidate_score_memory_digest_missing": (
        "candidate_score_memory_digest_missing"
    ),
    "candidate_score_hidden_memory_input": "candidate_score_hidden_memory_input",
    "arbitration_memory_order_invalid": "arbitration_memory_order_invalid",
    "memory_budget_discontinuity": "memory_budget_discontinuity",
    "node_plus_packet_budget_discontinuity": (
        "node_plus_packet_budget_discontinuity"
    ),
    "stale_memory_surface_read": "stale_memory_surface_read",
    "cross_cycle_memory_leak": "cross_cycle_memory_leak",
    "duplicate_memory_update": "duplicate_memory_update",
    "policy_disabled": "policy_disabled",
    "producer_mutation_boundary_violation": (
        "producer_mutation_boundary_violation"
    ),
    "no_memory_surface_read_by_arbitration": (
        "no_memory_surface_read_by_arbitration"
    ),
    "posthoc_memory_threshold_change": "posthoc_memory_threshold_change",
    "claim_promotion": "claim_promotion",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


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


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["claim_flags"])}


def source_arbitration_record_id(row: dict[str, Any]) -> str:
    # Fallback only. Iteration 1 now preserves this field directly; parsing
    # blocker strings remains here for compatibility with older baseline rows.
    for reason in row.get("expected_incomplete_reasons", []):
        parts = str(reason).split(":")
        if len(parts) >= 3 and parts[1] == "native-route-arbitration":
            return f"{parts[1]}:{parts[2]}"
    return f"native-route-arbitration:unresolved:{row['cycle_id']}"


def build_route_use_templates(baseline: dict[str, Any]) -> list[dict[str, Any]]:
    route_aspect = baseline["n05_inventory"]["route_aspect_fields"]
    support = baseline["n07_support_fields_available_as_memory_keys"]["field_values"]
    templates: list[dict[str, Any]] = []
    seen_routes: set[str] = set()
    for row in baseline["n06_inventory"]["route_digest_rows"]:
        route_id = str(row["selected_route"])
        if route_id in seen_routes:
            continue
        seen_routes.add(route_id)
        templates.append(
            {
                "template_id": f"n08_mem1_route_use_template_{route_id}",
                "source_experiment": "N06",
                "source_cycle_id": row["cycle_id"],
                "source_context_state_id": row["context_state_id"],
                "source_selection_scope": (
                    "selection_only_pre_topology_not_committed_route_use"
                ),
                "route_use_event_commits_memory_lane_consumption": True,
                "topology_commit_required": False,
                "topology_commit_requirement_rationale": (
                    "Early N08 route-use events are ordered, serialized, "
                    "budget-audited, and digest-pinned memory-lane "
                    "consumption records. They do not require topology "
                    "commit unless a later fixture explicitly uses a "
                    "topology-committing route."
                ),
                "selected_route_id": route_id,
                "source_candidate_set_digest": row["candidate_set_digest"],
                "source_arbitration_record_id": (
                    row.get("source_arbitration_record_id")
                    or source_arbitration_record_id(row)
                ),
                "source_arbitration_record_digest_required_for_route_use_event": True,
                "source_arbitration_record_digest_resolution": (
                    "must_be_resolved_by_iteration_3_from_source_artifact; "
                    "N06 SC6 closeout per-cycle rows replay native arbitration "
                    "records but do not serialize the positive arbitration "
                    "digest directly in the row"
                ),
                "selected_candidate_route_digest": row[
                    "selected_candidate_route_digest"
                ],
                "rejected_candidate_route_digests": row[
                    "rejected_candidate_route_digests"
                ],
                "source_surface_digest": row["candidate_source_surface_digests"][0],
                "route_aspect_digest": route_aspect["route_aspect_digest"],
                "route_aspect_id": route_aspect["route_aspect_id"],
                "source_support_area_digest": support["source_support_area_digest"],
                "target_support_area_digest": support["target_support_area_digest"],
                "node_plus_packet_budget_semantics": (
                    "route_use_event_is_evidence_only_and_must_be_budget_neutral"
                ),
            }
        )
    return templates


def build_iteration_3_cycle_contract(
    baseline: dict[str, Any], templates: list[dict[str, Any]]
) -> dict[str, Any]:
    rows = baseline["n06_inventory"]["route_digest_rows"]
    template_cycle_ids = {template["source_cycle_id"] for template in templates}
    return {
        "template_scope": "unique_selected_routes_only",
        "template_scope_rationale": (
            "Iteration 2 templates define reusable route-use shapes for route_a "
            "and route_b; they do not exhaust the source N06 cycle evidence."
        ),
        "iteration_3_route_use_event_scope": "all_source_n06_sc6_cycles",
        "source_cycle_count": len(rows),
        "required_route_use_event_count": len(rows),
        "required_source_cycle_ids": [row["cycle_id"] for row in rows],
        "template_source_cycle_ids": sorted(template_cycle_ids),
        "non_template_source_cycle_ids_to_emit_in_iteration_3": [
            row["cycle_id"] for row in rows if row["cycle_id"] not in template_cycle_ids
        ],
        "required_source_arbitration_record_ids": [
            row.get("source_arbitration_record_id") or source_arbitration_record_id(row)
            for row in rows
        ],
    }


def build_manifest(baseline: dict[str, Any]) -> dict[str, Any]:
    claim_flags = false_claim_flags(baseline)
    frozen_claim_flag_keys = sorted(claim_flags)
    route_use_templates = build_route_use_templates(baseline)
    memory_policy = {
        "memory_policy_id": "n08_memory_policy_v1",
        "policy_surface": "experiment_local_serialized_json_rows",
        "native_support_status": "experiment_local_until_phase8_memory_surface",
        "hidden_preference_allowed": False,
        "route_preference_source": "committed_route_use_events_only",
        "memory_strength_floor": 0.0,
        "memory_strength_ceiling": 1.0,
        "memory_policy_digest_rule": (
            "sha256(canonical_json(memory_policy_without_memory_policy_digest))"
        ),
    }
    memory_policy["memory_policy_digest"] = digest_value(
        {key: value for key, value in memory_policy.items() if key != "memory_policy_digest"}
    )

    decay_policy = {
        "decay_policy_id": "n08_exponential_decay_v1",
        "decay_function": "exponential_per_memory_window",
        "decay_factor": 0.9,
        "floor": 0.0,
        "decay_can_only_reduce_strength": True,
        "records_decay_loss": True,
        "hidden_decay_allowed": False,
    }
    reinforcement_policy = {
        "reinforcement_policy_id": "n08_saturating_additive_reinforcement_v1",
        "reinforcement_function": "saturating_additive",
        "reinforcement_amount": 0.25,
        "floor": 0.0,
        "ceiling": 1.0,
        "records_reinforcement_input": True,
        "records_saturation_clamp_loss": True,
        "hidden_reinforcement_allowed": False,
    }

    manifest: dict[str, Any] = {
        "schema": "n08_fixture_manifest_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 2,
        "purpose": "fixture_manifest_and_route_use_memory_contract",
        "source_baseline_inventory": rel(BASELINE_PATH),
        "source_baseline_inventory_digest": baseline["inventory_digest"],
        "memory_probe_run": False,
        "route_use_event_schema": {
            "artifact_kind": "n08_route_use_event",
            "schema_version": "n08_route_use_event_v1",
            "required_fields": ROUTE_USE_REQUIRED_FIELDS,
            "commit_status_values": ["committed"],
            "committed_semantics": {
                "route_arbitration_record_exists": True,
                "selected_candidate_digest_exists": True,
                "route_consumption_for_memory_formation_recorded": True,
                "ordered": True,
                "serialized": True,
                "budget_audited": True,
                "digest_pinned": True,
                "topology_commit_required_by_default": False,
            },
            "digest_field": "route_use_event_digest",
            "digest_rule": (
                "sha256(canonical_json(route_use_event_without_route_use_event_digest))"
            ),
            "claim_flags_must_remain_false": True,
            "claim_flags_reference": (
                "must match Iteration 1 frozen claim flag keys with all values false"
            ),
            "required_claim_flag_keys": frozen_claim_flag_keys,
        },
        "route_use_fixture_templates": route_use_templates,
        "iteration_3_route_use_cycle_contract": build_iteration_3_cycle_contract(
            baseline, route_use_templates
        ),
        "memory_surface_row_schema": {
            "artifact_kind": "n08_memory_surface_row",
            "schema_version": "n08_memory_surface_row_v1",
            "required_fields": MEMORY_SURFACE_REQUIRED_FIELDS,
            "storage_format": "experiment_local_serialized_json_artifact_rows",
            "native_memory_surface": False,
            "phase8_required_for_native_memory_surface": True,
            "memory_surface_kind_values": ["trail", "affordance"],
            "memory_surface_kind_definitions": {
                "trail": (
                    "serialized persistence of prior committed route use on a "
                    "route/support/aspect key"
                ),
                "affordance": (
                    "serialized prospective route capability signal derived "
                    "from trail/support/aspect evidence, not a hidden preference"
                ),
            },
            "digest_field": "memory_surface_digest",
            "digest_rule": (
                "sha256(canonical_json(memory_surface_record_without_memory_surface_digest))"
            ),
            "mem2_plus_requires_one_of": [
                "memory_surface_state_snapshot",
                "memory_surface_rows",
            ],
            "digest_without_serialized_state_is_insufficient_for_mem6": True,
            "claim_flags_must_remain_false": True,
            "claim_flags_reference": (
                "must match Iteration 1 frozen claim flag keys with all values false"
            ),
            "required_claim_flag_keys": frozen_claim_flag_keys,
            "mem_evidence_mapping": {
                "memory_strength_source": (
                    "MEM2+ evidence rows read memory_strength from serialized "
                    "memory_surface_state_snapshot or memory_surface_rows"
                ),
                "memory_surface_digest_source": "memory_surface_digest",
                "memory_surface_policy_source": "memory_policy_id",
            },
        },
        "memory_surface_key_contract": {
            "field_name": "memory_surface_key",
            "field_type": "canonical_json_object",
            "required_fields": MEMORY_KEY_FIELDS,
            "digest_field": "memory_surface_key_digest",
            "digest_rule": "sha256(canonical_json(memory_surface_key))",
            "not_a_scalar_string": True,
            "not_hidden_process_memory": True,
        },
        "memory_policy_schema": {
            "required_fields": [
                "memory_policy_id",
                "policy_surface",
                "route_preference_source",
                "memory_strength_floor",
                "memory_strength_ceiling",
                "memory_policy_digest",
            ],
            "default_policy": memory_policy,
        },
        "decay_policy_schema": {
            "required_fields": [
                "decay_policy_id",
                "decay_function",
                "decay_factor",
                "floor",
                "decay_can_only_reduce_strength",
                "records_decay_loss",
            ],
            "default_policy": decay_policy,
        },
        "reinforcement_policy_schema": {
            "required_fields": [
                "reinforcement_policy_id",
                "reinforcement_function",
                "reinforcement_amount",
                "floor",
                "ceiling",
                "records_reinforcement_input",
                "records_saturation_clamp_loss",
            ],
            "default_policy": reinforcement_policy,
        },
        "same_window_update_order": {
            "serialized_order_required": True,
            "default_order": ["decay", "reinforcement"],
        },
        "budget_contract": {
            "node_plus_packet_budget": {
                "fields": [
                    "node_plus_packet_budget_before",
                    "node_plus_packet_budget_after",
                    "node_plus_packet_budget_error",
                ],
                "semantics": (
                    "physical coherence accounting; memory bookkeeping cannot "
                    "repair node-plus-packet drift"
                ),
                "must_remain_exact": True,
            },
            "memory_budget": {
                "fields": [
                    "memory_budget_surface",
                    "memory_budget_before",
                    "reinforcement_input",
                    "decay_loss",
                    "saturation_clamp_loss",
                    "memory_budget_after",
                    "memory_budget_error",
                ],
                "semantics": (
                    "serialized trail/affordance strength accounting, not node coherence"
                ),
                "equation": (
                    "memory_budget_before + reinforcement_input - decay_loss "
                    "- saturation_clamp_loss == memory_budget_after"
                ),
            },
        },
        "memory_derived_score_component_contract": {
            "component_names": REQUIRED_MEMORY_SCORE_COMPONENTS,
            "required_candidate_runtime_visible_inputs": REQUIRED_RUNTIME_VISIBLE_INPUTS,
            "candidate_route_score_invariant": (
                "candidate_route_score == sum(candidate_score_components)"
            ),
            "hidden_memory_input_allowed": False,
            "component_names_not_native_forbidden_inputs": True,
        },
        "event_ordering_contract": {
            "ordered_chain": [
                "route_arbitration",
                "selected_route_use",
                "memory_update",
                "later_candidate_scoring",
                "native_route_arbitration",
            ],
            "strict_scheduler_order_required": True,
            "strict_event_time_order_required": True,
            "order_inversion_blocker": "arbitration_memory_order_invalid",
        },
        "control_contract": [
            {
                "control_id": control_id,
                "expected_status": "blocked",
                "primary_blocker": blocker,
                "distinct_primary_blocker_required": True,
            }
            for control_id, blocker in REQUIRED_CONTROL_BLOCKERS.items()
        ],
        "control_distinctions": {
            "hidden_route_history": (
                "route history exists only in fixture/report code and is not serialized"
            ),
            "memory_policy_hidden_preference": (
                "serialized memory policy contains undeclared route preference "
                "not derived from route-use evidence"
            ),
        },
        "producer_step_boundary": {
            "producer_scheduling_allowed": True,
            "producer_may_mutate_memory_surface": False,
            "producer_may_mutate_node_coherence": False,
            "producer_may_mutate_packet_ledger": False,
            "step_remains_packet_mutation_boundary": True,
            "primary_blocker": "producer_mutation_boundary_violation",
        },
        "claim_boundary": {
            "claim_flags": claim_flags,
            "claim_flags_must_remain_false_until_mem6": True,
            "memory_or_trail_claim_allowed_requires_mem6": True,
            "aco_agency_identity_locomotion_claims_blocked": True,
        },
        "native_policy_blockers_inherited": baseline[
            "missing_native_memory_policy_surfaces"
        ],
    }
    manifest["manifest_digest_scope"] = {
        "included": "manifest fields except manifest_digest",
        "excluded": ["manifest_digest"],
        "stable_across_same_inputs": True,
    }
    manifest["manifest_digest"] = digest_value(
        {key: value for key, value in manifest.items() if key != "manifest_digest"}
    )
    return manifest


def validate_manifest(manifest: dict[str, Any], baseline: dict[str, Any]) -> dict[str, bool]:
    route_schema = manifest["route_use_event_schema"]
    memory_schema = manifest["memory_surface_row_schema"]
    key_contract = manifest["memory_surface_key_contract"]
    decay = manifest["decay_policy_schema"]["default_policy"]
    reinforcement = manifest["reinforcement_policy_schema"]["default_policy"]
    budget = manifest["budget_contract"]
    score = manifest["memory_derived_score_component_contract"]
    controls = manifest["control_contract"]
    control_map = {row["control_id"]: row["primary_blocker"] for row in controls}
    event_order = manifest["event_ordering_contract"]["ordered_chain"]
    claim_flags = manifest["claim_boundary"]["claim_flags"]
    frozen_claim_flag_keys = sorted(claim_flags)
    route_templates = manifest["route_use_fixture_templates"]
    cycle_contract = manifest["iteration_3_route_use_cycle_contract"]
    native_components = baseline["native_route_arbitration_contract_inventory"][
        "proposed_memory_components"
    ]
    native_component_names = [row["component_name"] for row in native_components]
    source_support = baseline["n07_support_fields_available_as_memory_keys"][
        "field_values"
    ]
    return {
        "source_baseline_passed": baseline["status"] == "passed",
        "source_baseline_digest_matches": manifest["source_baseline_inventory_digest"]
        == baseline["inventory_digest"],
        "manifest_digest_stable_scope_declared": manifest["manifest_digest_scope"][
            "stable_across_same_inputs"
        ],
        "route_use_event_schema_required_fields_present": set(
            ROUTE_USE_REQUIRED_FIELDS
        ).issubset(route_schema["required_fields"]),
        "committed_route_use_semantics_complete": all(
            route_schema["committed_semantics"][key]
            for key in (
                "route_arbitration_record_exists",
                "selected_candidate_digest_exists",
                "route_consumption_for_memory_formation_recorded",
                "ordered",
                "serialized",
                "budget_audited",
                "digest_pinned",
            )
        ),
        "topology_commit_requirement_explicit": route_schema[
            "committed_semantics"
        ]["topology_commit_required_by_default"]
        is False
        and all(template["topology_commit_required"] is False for template in route_templates),
        "route_use_templates_source_backed": all(
            template["selected_candidate_route_digest"]
            and template["source_candidate_set_digest"]
            and template["source_surface_digest"]
            and template["source_arbitration_record_id"].startswith(
                "native-route-arbitration:"
            )
            for template in route_templates
        ),
        "route_use_event_schema_requires_arbitration_digest": (
            "source_arbitration_record_digest" in route_schema["required_fields"]
        ),
        "route_use_template_arbitration_digest_resolution_explicit": all(
            template["source_arbitration_record_digest_required_for_route_use_event"]
            is True
            and template["source_arbitration_record_digest_resolution"].startswith(
                "must_be_resolved_by_iteration_3"
            )
            for template in route_templates
        ),
        "route_use_templates_cover_two_routes": {template["selected_route_id"] for template in route_templates}
        == {"route_a", "route_b"},
        "iteration_3_requires_all_n06_cycles": (
            cycle_contract["iteration_3_route_use_event_scope"]
            == "all_source_n06_sc6_cycles"
            and cycle_contract["required_route_use_event_count"]
            == len(baseline["n06_inventory"]["route_digest_rows"])
            and set(cycle_contract["required_source_cycle_ids"])
            == {row["cycle_id"] for row in baseline["n06_inventory"]["route_digest_rows"]}
        ),
        "memory_surface_schema_required_fields_present": set(
            MEMORY_SURFACE_REQUIRED_FIELDS
        ).issubset(memory_schema["required_fields"]),
        "memory_surface_budget_equation_terms_serialized": set(
            (
                "reinforcement_input",
                "decay_loss",
                "saturation_clamp_loss",
            )
        ).issubset(memory_schema["required_fields"]),
        "memory_surface_kind_definitions_declared": set(
            memory_schema["memory_surface_kind_definitions"]
        )
        == {"trail", "affordance"},
        "memory_strength_mapping_declared": (
            "memory_surface_state_snapshot"
            in memory_schema["mem_evidence_mapping"]["memory_strength_source"]
            and memory_schema["mem_evidence_mapping"]["memory_surface_digest_source"]
            == "memory_surface_digest"
        ),
        "memory_surface_storage_experiment_local": memory_schema["storage_format"]
        == "experiment_local_serialized_json_artifact_rows",
        "memory_surface_key_contract_complete": key_contract["field_type"]
        == "canonical_json_object"
        and key_contract["required_fields"] == MEMORY_KEY_FIELDS
        and key_contract["digest_rule"] == "sha256(canonical_json(memory_surface_key))",
        "memory_surface_digest_algorithm_declared": memory_schema["digest_rule"]
        == "sha256(canonical_json(memory_surface_record_without_memory_surface_digest))",
        "mem2_plus_requires_snapshot_or_rows": set(
            memory_schema["mem2_plus_requires_one_of"]
        )
        == {"memory_surface_state_snapshot", "memory_surface_rows"},
        "decay_policy_schema_complete": decay["decay_function"]
        == "exponential_per_memory_window"
        and decay["records_decay_loss"] is True
        and decay["floor"] == 0.0,
        "decay_policy_can_only_reduce_strength": decay[
            "decay_can_only_reduce_strength"
        ]
        is True,
        "reinforcement_policy_schema_complete": reinforcement["reinforcement_function"]
        == "saturating_additive"
        and reinforcement["floor"] == 0.0
        and reinforcement["ceiling"] == 1.0
        and reinforcement["records_saturation_clamp_loss"] is True,
        "same_window_update_order_serialized": manifest["same_window_update_order"][
            "default_order"
        ]
        == ["decay", "reinforcement"],
        "memory_budget_equation_declared": "memory_budget_before + reinforcement_input"
        in budget["memory_budget"]["equation"],
        "node_plus_packet_budget_separate": budget["node_plus_packet_budget"][
            "must_remain_exact"
        ]
        is True
        and "memory_budget_error" in budget["memory_budget"]["fields"],
        "score_component_names_match_baseline": score["component_names"]
        == native_component_names
        == REQUIRED_MEMORY_SCORE_COMPONENTS,
        "runtime_visible_inputs_declared": score[
            "required_candidate_runtime_visible_inputs"
        ]
        == REQUIRED_RUNTIME_VISIBLE_INPUTS,
        "event_ordering_contract_declared": event_order
        == [
            "route_arbitration",
            "selected_route_use",
            "memory_update",
            "later_candidate_scoring",
            "native_route_arbitration",
        ],
        "controls_include_required_blockers": all(
            control_map.get(control_id) == blocker
            for control_id, blocker in REQUIRED_CONTROL_BLOCKERS.items()
        ),
        "control_blockers_distinct": len(set(control_map.values())) == len(control_map),
        "special_controls_present": all(
            control_id in control_map
            for control_id in (
                "producer_mutation_boundary_violation",
                "policy_disabled",
                "no_memory_surface_read_by_arbitration",
                "memory_surface_poisoned",
                "cross_cycle_memory_leak",
            )
        ),
        "hidden_route_history_and_hidden_preference_distinct": control_map[
            "hidden_route_history"
        ]
        != control_map["memory_policy_hidden_preference"],
        "claim_flags_all_false": all(value is False for value in claim_flags.values()),
        "route_use_claim_flags_reference_frozen_set": (
            route_schema["required_claim_flag_keys"] == frozen_claim_flag_keys
            and route_schema["claim_flags_must_remain_false"] is True
        ),
        "memory_surface_claim_flags_reference_frozen_set": (
            memory_schema["required_claim_flag_keys"] == frozen_claim_flag_keys
            and memory_schema["claim_flags_must_remain_false"] is True
        ),
        "producer_step_boundary_declared": (
            manifest["producer_step_boundary"]["producer_scheduling_allowed"] is True
            and manifest["producer_step_boundary"]["producer_may_mutate_memory_surface"]
            is False
            and manifest["producer_step_boundary"]["step_remains_packet_mutation_boundary"]
            is True
        ),
        "native_policy_blockers_inherited": bool(
            manifest["native_policy_blockers_inherited"]
        ),
        "memory_probe_not_run": manifest["memory_probe_run"] is False,
        "support_anchors_present_in_templates": all(
            template["source_support_area_digest"]
            == source_support["source_support_area_digest"]
            and template["target_support_area_digest"]
            == source_support["target_support_area_digest"]
            for template in route_templates
        ),
    }


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    manifest = output["fixture_manifest"]
    checks = output["checks"]
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    control_lines = "\n".join(
        f"| `{row['control_id']}` | `{row['primary_blocker']}` |"
        for row in manifest["control_contract"]
    )
    route_schema_lines = "\n".join(
        f"- `{field}`" for field in manifest["route_use_event_schema"]["required_fields"]
    )
    memory_schema_lines = "\n".join(
        f"- `{field}`" for field in manifest["memory_surface_row_schema"]["required_fields"]
    )
    memory_kind_lines = "\n".join(
        f"- `{kind}`: {definition}"
        for kind, definition in manifest["memory_surface_row_schema"][
            "memory_surface_kind_definitions"
        ].items()
    )
    memory_budget_field_lines = "\n".join(
        f"- `{field}`" for field in manifest["budget_contract"]["memory_budget"]["fields"]
    )
    cycle_contract = manifest["iteration_3_route_use_cycle_contract"]
    inherited_blocker_lines = "\n".join(
        f"- `{blocker}`" for blocker in manifest["native_policy_blockers_inherited"]
    )
    producer_boundary = manifest["producer_step_boundary"]
    report = f"""# N08 Iteration 2 Fixture Manifest And Route-Use Trace Contract

Status: `{output['status']}`.

## Result

Iteration 2 defines the route-use and memory/trail fixture contract before any
positive memory probe. It does not emit route-use events or memory surfaces.

Key boundary:

```text
N06 route selection artifact != N08 route-use event
N08 route-use event = ordered, serialized, budget-audited consumption record
memory surface = experiment-local JSON artifact rows until native Phase 8 support
memory_or_trail_claim_allowed = false
```

## Route-Use Event Schema

Required fields:

{route_schema_lines}

Default topology commit requirement:
`{manifest['route_use_event_schema']['committed_semantics']['topology_commit_required_by_default']}`.

The early N08 fixture explicitly does not require topology commit. Its route-use
event is a memory-lane consumption record, not topology mutation evidence.

Template provenance note: route-use events require
`source_arbitration_record_digest`, but the N06 SC6 closeout per-cycle rows
serialize native arbitration replay status and record IDs rather than the
positive arbitration digest directly. Iteration 3 must resolve and pin the
actual source arbitration digest when it emits MEM1 route-use events.

Template coverage note: Iteration 2 templates are deduplicated by selected
route and cover route A and route B shapes. Iteration 3 must emit route-use
events for all `{cycle_contract['required_route_use_event_count']}` N06 SC6
source cycles:

```json
{json.dumps(cycle_contract['required_source_cycle_ids'], indent=2)}
```

## Memory Surface Schema

Storage format:
`{manifest['memory_surface_row_schema']['storage_format']}`.

Required fields:

{memory_schema_lines}

Memory surface kind definitions:

{memory_kind_lines}

`memory_surface_key` is a canonical JSON object with fields:

```json
{json.dumps(manifest['memory_surface_key_contract']['required_fields'], indent=2)}
```

Digest rules:

```text
route_use_event_digest =
  {manifest['route_use_event_schema']['digest_rule']}

memory_surface_key_digest =
  {manifest['memory_surface_key_contract']['digest_rule']}

memory_surface_digest =
  {manifest['memory_surface_row_schema']['digest_rule']}
```

MEM2+ requires one of:
`{manifest['memory_surface_row_schema']['mem2_plus_requires_one_of']}`.

MEM2+ evidence-row mapping:

```json
{json.dumps(manifest['memory_surface_row_schema']['mem_evidence_mapping'], indent=2, sort_keys=True)}
```

## Policies And Budgets

Default decay policy:
`{manifest['decay_policy_schema']['default_policy']['decay_function']}`
with factor `{manifest['decay_policy_schema']['default_policy']['decay_factor']}`.
Decay can only reduce memory strength:
`{manifest['decay_policy_schema']['default_policy']['decay_can_only_reduce_strength']}`.

Default reinforcement policy:
`{manifest['reinforcement_policy_schema']['default_policy']['reinforcement_function']}`
with amount
`{manifest['reinforcement_policy_schema']['default_policy']['reinforcement_amount']}`.

Same-window order:
`{manifest['same_window_update_order']['default_order']}`.

Memory budget equation:

```text
{manifest['budget_contract']['memory_budget']['equation']}
```

Memory-budget row fields:

{memory_budget_field_lines}

Node-plus-packet budget remains a separate exact coherence accounting surface.

## Score Components

Memory-derived candidate score components:

```json
{json.dumps(manifest['memory_derived_score_component_contract']['component_names'], indent=2)}
```

Required `candidate_runtime_visible_inputs`:

```json
{json.dumps(manifest['memory_derived_score_component_contract']['required_candidate_runtime_visible_inputs'], indent=2)}
```

## Event Ordering

```json
{json.dumps(manifest['event_ordering_contract']['ordered_chain'], indent=2)}
```

## Producer / Step Boundary

```json
{json.dumps(producer_boundary, indent=2, sort_keys=True)}
```

Producers may schedule and record evidence only. They may not mutate memory
surfaces, node coherence, or packet ledgers; `step()` remains the packet
mutation boundary.

## Inherited Native Policy Blockers

The Iteration 1 native memory/trail policy blockers are carried forward:

{inherited_blocker_lines}

## Controls

| Control | Primary Blocker |
|---|---|
{control_lines}

`hidden_route_history` and `memory_policy_hidden_preference` are distinct
failure modes.

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Artifact Digests

```json
{json.dumps(output['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance Result

Achieved: `{output['acceptance']['achieved']}`.

Manifest digest: `{manifest['manifest_digest']}`.
Validation digest: `{output['validation_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output(manifest: dict[str, Any], checks: dict[str, bool]) -> dict[str, Any]:
    output: dict[str, Any] = {
        "schema": "n08_iteration_2_fixture_manifest_validation_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 2,
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_artifacts": {
            rel(BASELINE_PATH): digest_file(BASELINE_PATH),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "fixture_manifest_path": rel(MANIFEST_PATH),
        "fixture_manifest": manifest,
        "checks": checks,
        "memory_probe_run": False,
        "claim_flags": manifest["claim_boundary"]["claim_flags"],
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 2 passes if the fixture manifest and "
                "route-use/memory contracts are defined before positive "
                "memory probes. The manifest must make route-use events, "
                "memory surfaces, decay/reinforcement policies, budget "
                "surfaces, event ordering, and controls replayable from "
                "artifacts."
            ),
        },
    }
    output["artifact_digests"] = {
        rel(MANIFEST_PATH): digest_file(MANIFEST_PATH),
        rel(BASELINE_PATH): digest_file(BASELINE_PATH),
    }
    output["validation_digest_scope"] = {
        "included": "all validation fields except generated_at and validation_digest",
        "excluded": ["generated_at", "validation_digest"],
        "stable_across_same_inputs": True,
        "artifact_digest_dependency": (
            "validation_digest includes artifact_digests; generated artifacts are "
            "written with sorted keys and fixed indentation for stable file hashes"
        ),
    }
    output["validation_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"generated_at", "validation_digest"}
        }
    )
    return output


def main() -> None:
    baseline = load_json(BASELINE_PATH)
    manifest = build_manifest(baseline)
    write_manifest(manifest)
    checks = validate_manifest(manifest, baseline)
    output = build_output(manifest, checks)
    write_output(output)
    write_report(output)


if __name__ == "__main__":
    main()
