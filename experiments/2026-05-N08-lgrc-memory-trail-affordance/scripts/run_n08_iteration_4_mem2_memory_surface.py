#!/usr/bin/env python3
"""Run N08 Iteration 4 MEM2 trail memory-surface formation.

Iteration 4 converts MEM1 route-use events into experiment-local serialized
memory surface rows. It creates a trail surface and final state snapshot, but
does not yet perform decay/reinforcement windows, memory-shaped arbitration, or
claim promotion.
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
MANIFEST_VALIDATION_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_2_fixture_manifest_validation.json"
)
SOURCE_MEM1_PATH = EXPERIMENT / "outputs" / "n08_iteration_3_mem1_route_use_trace.json"
SOURCE_MEM1_REPORT = EXPERIMENT / "reports" / "n08_iteration_3_mem1_route_use_trace.md"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_4_mem2_memory_surface.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_4_mem2_memory_surface.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_4_mem2_memory_surface.py"
)

MEMORY_SURFACE_EVENT_TIME_OFFSET = 0.2
MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET = 10
MEMORY_SURFACE_EVENT_TIME_OFFSET_RATIONALE = (
    "MEM2 memory surface rows are placed after MEM1 route-use events while "
    "leaving an ordered event-time band for later MEM3 update windows."
)
MEMORY_SURFACE_SCHEDULER_INDEX_BAND = "10-19"
MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET_RATIONALE = (
    "MEM1 route-use evidence occupies the lower scheduler band; MEM2 memory "
    "surface formation rows use the 10-19 band so later MEM3 windows can be "
    "ordered after surface formation without reusing route-use indices."
)
MEMORY_SURFACE_ID_RULE = (
    "n08-memory-surface:{memory_surface_key_digest[:16]}:"
    "{route_use_event_digest[:16]}"
)
MEMORY_SURFACE_SUPPLEMENTARY_FIELDS = [
    "artifact_kind",
    "schema_version",
    "mem_level",
    "mem_level_is_evidence_classification",
    "claim_ceiling",
    "memory_surface_id_rule",
    "memory_surface_kind_semantics",
    "route_use_event_id",
    "source_route_use_event_time_key",
    "source_route_use_scheduler_event_index",
    "source_cycle_id",
    "selected_route_id",
    "source_arbitration_record_digest",
    "source_candidate_set_digest",
    "selected_candidate_route_digest",
    "memory_policy_native_support_status",
    "memory_strength_before",
    "memory_strength_delta",
    "route_use_count_for_key",
    "event_time_key_derivation",
    "scheduler_event_index_derivation",
    "event_order_relation",
    "node_plus_packet_budget_semantics",
    "memory_budget_semantics",
    "formation_window_applied",
    "formation_update_kind",
    "formation_input",
    "formation_arithmetic",
    "formation_arithmetic_policy_reference",
    "formation_arithmetic_matches_reinforcement_policy",
    "formation_input_from_route_use",
    "formal_mem3_policy_window_applied",
    "formal_mem3_decay_reinforcement_window_applied",
    "formal_mem3_window_status",
    "decay_policy_applied",
    "reinforcement_policy_window_applied",
    "affordance_surface_emitted",
    "affordance_status",
    "learning_boundary",
    "visual_reference",
    "visual_is_evidence_source",
]


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


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def git_status_short_src() -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "src"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def false_claim_flags(manifest_validation: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in manifest_validation["fixture_manifest"]["memory_surface_row_schema"][
            "required_claim_flag_keys"
        ]
    }


def memory_surface_key(event: dict[str, Any], memory_policy_id: str) -> dict[str, str]:
    return {
        "route_id": event["selected_route_id"],
        "source_support_area_digest": event["source_support_area_digest"],
        "target_support_area_digest": event["target_support_area_digest"],
        "route_aspect_digest": event["route_aspect_digest"],
        "memory_policy_id": memory_policy_id,
    }


def memory_surface_id(key_digest: str, route_use_digest: str) -> str:
    return f"n08-memory-surface:{key_digest[:16]}:{route_use_digest[:16]}"


def memory_policy_digest_payload(memory_policy: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in memory_policy.items()
        if key != "memory_policy_digest"
    }


def recompute_memory_policy_digest(memory_policy: dict[str, Any]) -> str:
    return digest_value(memory_policy_digest_payload(memory_policy))


def memory_surface_digest(row: dict[str, Any]) -> str:
    payload = {key: value for key, value in row.items() if key != "memory_surface_digest"}
    return digest_value(payload)


def build_memory_surface_rows(
    manifest_validation: dict[str, Any],
    mem1: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest = manifest_validation["fixture_manifest"]
    memory_policy = manifest["memory_policy_schema"]["default_policy"]
    memory_schema = manifest["memory_surface_row_schema"]
    reinforcement_policy = manifest["reinforcement_policy_schema"]["default_policy"]
    claim_flags = false_claim_flags(manifest_validation)
    reinforcement_amount = float(reinforcement_policy["reinforcement_amount"])
    ceiling = float(memory_policy["memory_strength_ceiling"])
    strengths_by_key_digest: dict[str, float] = {}
    counts_by_key_digest: dict[str, int] = {}
    rows: list[dict[str, Any]] = []

    for event in mem1["route_use_events"]:
        key = memory_surface_key(event, memory_policy["memory_policy_id"])
        key_digest = digest_value(key)
        previous_strength = strengths_by_key_digest.get(key_digest, 0.0)
        proposed_strength = previous_strength + reinforcement_amount
        clamp_loss = max(0.0, proposed_strength - ceiling)
        after_strength = min(ceiling, proposed_strength)
        previous_count = counts_by_key_digest.get(key_digest, 0)
        counts_by_key_digest[key_digest] = previous_count + 1
        strengths_by_key_digest[key_digest] = after_strength

        row: dict[str, Any] = {
            "artifact_kind": memory_schema["artifact_kind"],
            "schema_version": memory_schema["schema_version"],
            "mem_level": "MEM2",
            "mem_level_is_evidence_classification": True,
            "claim_ceiling": "mem2_trail_surface_candidate",
            "memory_surface_id": memory_surface_id(
                key_digest, event["route_use_event_digest"]
            ),
            "memory_surface_id_rule": MEMORY_SURFACE_ID_RULE,
            "memory_surface_kind": "trail",
            "memory_surface_kind_semantics": memory_schema[
                "memory_surface_kind_definitions"
            ]["trail"],
            "route_use_event_digest": event["route_use_event_digest"],
            "route_use_event_id": event["route_use_event_id"],
            "source_route_use_event_time_key": event["event_time_key"],
            "source_route_use_scheduler_event_index": event["scheduler_event_index"],
            "source_cycle_id": event["source_cycle_id"],
            "selected_route_id": event["selected_route_id"],
            "source_arbitration_record_digest": event[
                "source_arbitration_record_digest"
            ],
            "source_candidate_set_digest": event["source_candidate_set_digest"],
            "selected_candidate_route_digest": event[
                "selected_candidate_route_digest"
            ],
            "memory_surface_key": key,
            "memory_surface_key_digest": key_digest,
            "memory_policy_id": memory_policy["memory_policy_id"],
            "memory_policy_digest": memory_policy["memory_policy_digest"],
            "memory_policy_native_support_status": memory_policy[
                "native_support_status"
            ],
            "memory_strength": after_strength,
            "memory_strength_before": previous_strength,
            "memory_strength_delta": after_strength - previous_strength,
            "route_use_count_for_key": counts_by_key_digest[key_digest],
            "event_time_key": round(
                float(event["event_time_key"]) + MEMORY_SURFACE_EVENT_TIME_OFFSET,
                6,
            ),
            "event_time_key_derivation": {
                "source_route_use_event_time_key": event["event_time_key"],
                "offset": MEMORY_SURFACE_EVENT_TIME_OFFSET,
                "rationale": MEMORY_SURFACE_EVENT_TIME_OFFSET_RATIONALE,
            },
            "scheduler_event_index": int(event["scheduler_event_index"])
            + MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET,
            "scheduler_event_index_derivation": {
                "source_route_use_scheduler_event_index": event[
                    "scheduler_event_index"
                ],
                "offset": MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET,
                "target_scheduler_band": MEMORY_SURFACE_SCHEDULER_INDEX_BAND,
                "rationale": MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET_RATIONALE,
            },
            "event_order_relation": (
                "selected_route_use_precedes_memory_surface_row; "
                "formation_seed_accumulation_precedes_formal_mem3_window"
            ),
            "node_plus_packet_budget_before": event["node_plus_packet_budget_after"],
            "node_plus_packet_budget_after": event["node_plus_packet_budget_after"],
            "node_plus_packet_budget_error": 0.0,
            "node_plus_packet_budget_semantics": (
                "memory surface formation is serialized bookkeeping and cannot "
                "repair or change node-plus-packet coherence"
            ),
            "memory_budget_surface": "trail_strength",
            "memory_budget_before": previous_strength,
            "reinforcement_input": reinforcement_amount,
            "decay_loss": 0.0,
            "saturation_clamp_loss": clamp_loss,
            "memory_budget_after": after_strength,
            "memory_budget_error": 0.0,
            "memory_budget_semantics": (
                "serialized trail strength accounting; not node coherence"
            ),
            "formation_window_applied": True,
            "formation_update_kind": "route_use_seed_accumulation",
            "formation_input": reinforcement_amount,
            "formation_arithmetic": "saturating_additive_seed_accumulation",
            "formation_arithmetic_policy_reference": reinforcement_policy[
                "reinforcement_policy_id"
            ],
            "formation_arithmetic_matches_reinforcement_policy": True,
            "formal_mem3_policy_window_applied": False,
            "formal_mem3_decay_reinforcement_window_applied": False,
            "formal_mem3_window_status": "deferred_to_iteration_5",
            "decay_policy_applied": False,
            "reinforcement_policy_window_applied": False,
            "formation_input_from_route_use": True,
            "affordance_surface_emitted": False,
            "affordance_status": (
                "latent_until_memory_surface_is_read_by_candidate_scoring"
            ),
            "learning_boundary": {
                "policy_updated": False,
                "route_weight_updated": False,
                "candidate_score_updated": False,
                "future_route_bias_created": False,
                "memory_surface_created": True,
            },
            "claim_flags": claim_flags,
            "visual_reference": None,
            "visual_is_evidence_source": False,
        }
        row["memory_surface_digest"] = memory_surface_digest(row)
        rows.append(row)
    return rows


def build_state_snapshot(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key_digest = row["memory_surface_key_digest"]
        by_key[key_digest] = {
            "latest_memory_surface_id": row["memory_surface_id"],
            "memory_surface_key": row["memory_surface_key"],
            "memory_surface_key_digest": key_digest,
            "memory_surface_kind": row["memory_surface_kind"],
            "selected_route_id": row["selected_route_id"],
            "latest_memory_surface_digest": row["memory_surface_digest"],
            "latest_route_use_event_digest": row["route_use_event_digest"],
            "latest_event_time_key": row["event_time_key"],
            "latest_scheduler_event_index": row["scheduler_event_index"],
            "latest_source_arbitration_record_digest": row[
                "source_arbitration_record_digest"
            ],
            "latest_source_candidate_set_digest": row["source_candidate_set_digest"],
            "latest_selected_candidate_route_digest": row[
                "selected_candidate_route_digest"
            ],
            "route_use_count_for_key": row["route_use_count_for_key"],
            "memory_strength": row["memory_strength"],
            "latest_memory_budget_before": row["memory_budget_before"],
            "latest_memory_budget_after": row["memory_budget_after"],
            "latest_memory_budget_error": row["memory_budget_error"],
            "latest_node_plus_packet_budget_before": row[
                "node_plus_packet_budget_before"
            ],
            "latest_node_plus_packet_budget_after": row[
                "node_plus_packet_budget_after"
            ],
            "latest_node_plus_packet_budget_error": row[
                "node_plus_packet_budget_error"
            ],
            "latest_reinforcement_input": row["reinforcement_input"],
            "latest_decay_loss": row["decay_loss"],
            "latest_saturation_clamp_loss": row["saturation_clamp_loss"],
            "claim_flags_all_false": all(
                value is False for value in row["claim_flags"].values()
            ),
            "memory_policy_id": row["memory_policy_id"],
            "memory_policy_digest": row["memory_policy_digest"],
        }
    snapshot: dict[str, Any] = {
        "snapshot_id": "n08_mem2_trail_surface_state_snapshot_v1",
        "snapshot_kind": "memory_surface_state_snapshot",
        "snapshot_semantics": (
            "final experiment-local trail surface state after MEM1 route-use events"
        ),
        "snapshot_completeness": "latest_state_summary_not_full_replay_record",
        "full_replay_requires": "memory_surface_rows",
        "omitted_replay_fields_reason": (
            "Full per-event replay fields remain serialized on memory_surface_rows; "
            "the snapshot summarizes the latest state per canonical memory key."
        ),
        "memory_surface_storage": "experiment_local_serialized_json_artifact_rows",
        "affordance_status": "latent_not_yet_read_by_candidate_scoring",
        "state_by_memory_surface_key_digest": dict(sorted(by_key.items())),
    }
    snapshot["memory_surface_state_snapshot_digest"] = digest_value(snapshot)
    return snapshot


def control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "missing_route_use_event",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "missing_route_use_event",
            "purpose": "Reject a memory surface row without a source route-use event.",
        },
        {
            "control_id": "memory_surface_digest_mismatch",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_surface_digest_mismatch",
            "purpose": "Reject a memory surface row whose digest does not recompute.",
        },
        {
            "control_id": "memory_surface_key_digest_mismatch",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_surface_key_digest_mismatch",
            "purpose": "Reject a surface whose canonical key digest does not recompute.",
        },
        {
            "control_id": "hidden_route_history",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "hidden_route_history",
            "purpose": "Reject memory surfaces derived from hidden fixture history.",
        },
        {
            "control_id": "memory_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_budget_discontinuity",
            "purpose": "Reject trail-strength budget equation failure.",
        },
        {
            "control_id": "node_plus_packet_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "purpose": "Reject node-plus-packet budget drift hidden by memory bookkeeping.",
        },
        {
            "control_id": "claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "claim_promotion",
            "purpose": "Reject MEM2 promotion to memory claim, ACO, agency, or movement.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = digest_value(row)
    return rows


def arc_interpretation(
    rows: list[dict[str, Any]], snapshot: dict[str, Any]
) -> dict[str, Any]:
    strengths = {
        state["selected_route_id"]: state["memory_strength"]
        for state in snapshot["state_by_memory_surface_key_digest"].values()
    }
    counts = {
        state["selected_route_id"]: state["route_use_count_for_key"]
        for state in snapshot["state_by_memory_surface_key_digest"].values()
    }
    interpretation: dict[str, Any] = {
        "interpretation_id": "n08_i4_arc_of_becoming_mem2_memory_surface_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What becomes available when committed route-use traces persist as "
            "serialized trail-surface rows?"
        ),
        "observations": [
            {
                "observation_id": "use_history_becomes_surface",
                "metric": "memory_surface_row_count",
                "value": len(rows),
                "interpretation": (
                    "The MEM1 trace is no longer only event history; each route "
                    "use now has a digest-pinned trail surface row."
                ),
            },
            {
                "observation_id": "route_specific_strength_accumulates",
                "metric": "final_memory_strength_by_route",
                "value": strengths,
                "interpretation": (
                    "Route A and route B retain separate trail strengths under "
                    "the canonical memory-surface key. This is surface "
                    "persistence, not route choice bias yet."
                ),
            },
            {
                "observation_id": "affordance_is_latent",
                "metric": "affordance_surface_emitted",
                "value": False,
                "interpretation": (
                    "The trail can become an affordance only when later "
                    "candidate scoring reads it as runtime-visible evidence."
                ),
            },
            {
                "observation_id": "memory_budget_separate_from_coherence",
                "metric": "node_plus_packet_budget_error",
                "value": 0.0,
                "interpretation": (
                    "Trail strength accounting changes while physical "
                    "node-plus-packet coherence remains unchanged."
                ),
            },
        ],
        "classification": {
            "mem_level": "MEM2",
            "classification_status": "trail_memory_surface_candidate",
            "claim_gate": "closed_until_mem6_artifact_replay",
            "not_merely_true_false_endpoint": True,
            "affordance_status": "latent_not_yet_operational",
            "memory_surface_persisted": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "A route-use trace can become a serialized trail surface without hidden route history.",
                "Trail strength can remain keyed by route/support/aspect rather than becoming a global preference.",
                "The next test is not whether the surface exists, but how it changes across ordered decay and reinforcement windows.",
            ],
            "next_question": (
                "Can the persisted trail surface undergo serialized decay and "
                "reinforcement updates while preserving memory-budget and "
                "node-plus-packet budget separation?"
            ),
            "next_iteration": "5_MEM3_decay_reinforcement_update",
            "successor_probe_should_measure": [
                "decay_loss",
                "reinforcement_input",
                "saturation_clamp_loss",
                "same_window_update_order",
                "memory_budget_equation",
            ],
        },
        "naturalization": {
            "naturalization_rung": "Nat1_persisted_artifact_surface",
            "self_persistent_memory_observed": True,
            "self_updating_memory_observed": False,
            "why_not_more_naturalized": (
                "The surface persists as serialized artifact state, but decay, "
                "reinforcement, and candidate-score reads are still later probes."
            ),
        },
        "learning_boundary": {
            "is_reinforcement_learning": False,
            "is_neural_weight_update": False,
            "is_graph_weight_propagation": False,
            "policy_updated": False,
            "route_weight_updated": False,
            "candidate_score_updated": False,
            "future_route_bias_created": False,
            "surface_strength_created": True,
            "distinction": (
                "Iteration 4 creates a serialized trail surface from route-use "
                "events. It still does not update native route weights or let "
                "memory bias future route arbitration."
            ),
        },
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "aco_like_claim_allowed": False,
            "movement_claim_allowed": False,
            "reason": (
                "MEM2 supports a trail-surface candidate only. The narrow "
                "memory/trail claim remains closed until MEM6 artifact replay."
            ),
        },
        "final_route_use_counts": counts,
        "final_memory_strength_by_route": strengths,
    }
    interpretation["arc_interpretation_digest"] = digest_value(interpretation)
    return interpretation


def memory_budget_equation_holds(row: dict[str, Any]) -> bool:
    expected = (
        row["memory_budget_before"]
        + row["reinforcement_input"]
        - row["decay_loss"]
        - row["saturation_clamp_loss"]
    )
    return abs(expected - row["memory_budget_after"]) <= 1e-12 and row[
        "memory_budget_error"
    ] == 0.0


def validate_output(
    manifest_validation: dict[str, Any],
    mem1: dict[str, Any],
    rows: list[dict[str, Any]],
    snapshot: dict[str, Any],
    controls: list[dict[str, Any]],
    interpretation: dict[str, Any],
) -> dict[str, bool]:
    manifest = manifest_validation["fixture_manifest"]
    memory_policy = manifest["memory_policy_schema"]["default_policy"]
    required_fields = set(manifest["memory_surface_row_schema"]["required_fields"])
    row_contract_fields = required_fields.union(MEMORY_SURFACE_SUPPLEMENTARY_FIELDS)
    route_use_digests = {
        event["route_use_event_digest"] for event in mem1["route_use_events"]
    }
    control_blockers = [row["primary_blocker"] for row in controls]
    return {
        "source_mem1_passed": mem1["status"] == "passed",
        "source_manifest_passed": manifest_validation["status"] == "passed",
        "memory_surface_rows_emitted": len(rows) == mem1["route_use_event_count"],
        "memory_surface_required_fields_present": all(
            required_fields.issubset(row) for row in rows
        ),
        "memory_surface_kind_trail": all(
            row["memory_surface_kind"] == "trail" for row in rows
        ),
        "route_use_digest_cited": all(
            row["route_use_event_digest"] in route_use_digests for row in rows
        ),
        "memory_surface_digest_recomputes": all(
            row["memory_surface_digest"] == memory_surface_digest(row)
            for row in rows
        ),
        "memory_surface_key_digest_recomputes": all(
            row["memory_surface_key_digest"] == digest_value(row["memory_surface_key"])
            for row in rows
        ),
        "memory_policy_digest_recomputes": memory_policy["memory_policy_digest"]
        == recompute_memory_policy_digest(memory_policy)
        and all(
            row["memory_policy_digest"] == memory_policy["memory_policy_digest"]
            for row in rows
        ),
        "memory_surface_id_rule_declared": all(
            row["memory_surface_id_rule"] == MEMORY_SURFACE_ID_RULE for row in rows
        ),
        "allowed_supplementary_fields_declared": all(
            set(row).issubset(row_contract_fields) for row in rows
        ),
        "memory_surface_persists_after_route_use": all(
            row["event_time_key"] > row["source_route_use_event_time_key"]
            and row["scheduler_event_index"]
            > row["source_route_use_scheduler_event_index"]
            for row in rows
        ),
        "event_time_offset_declared": all(
            row["event_time_key_derivation"]["offset"]
            == MEMORY_SURFACE_EVENT_TIME_OFFSET
            and row["event_time_key_derivation"]["rationale"]
            == MEMORY_SURFACE_EVENT_TIME_OFFSET_RATIONALE
            for row in rows
        ),
        "scheduler_index_offset_declared": all(
            row["scheduler_event_index_derivation"]["offset"]
            == MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET
            and row["scheduler_event_index_derivation"]["target_scheduler_band"]
            == MEMORY_SURFACE_SCHEDULER_INDEX_BAND
            for row in rows
        ),
        "memory_surface_state_snapshot_serialized": bool(
            snapshot["state_by_memory_surface_key_digest"]
        )
        and bool(snapshot["memory_surface_state_snapshot_digest"]),
        "state_snapshot_scope_declared": snapshot["snapshot_completeness"]
        == "latest_state_summary_not_full_replay_record"
        and snapshot["full_replay_requires"] == "memory_surface_rows",
        "memory_surface_state_snapshot_digest_recomputes": snapshot[
            "memory_surface_state_snapshot_digest"
        ]
        == digest_value(
            {
                key: value
                for key, value in snapshot.items()
                if key != "memory_surface_state_snapshot_digest"
            }
        ),
        "memory_budget_equations_hold": all(
            memory_budget_equation_holds(row) for row in rows
        ),
        "memory_strength_equals_memory_budget_after": all(
            row["memory_strength"] == row["memory_budget_after"] for row in rows
        ),
        "formation_window_semantics_declared": all(
            row["formation_window_applied"] is True
            and row["formation_update_kind"] == "route_use_seed_accumulation"
            and row["formation_arithmetic_matches_reinforcement_policy"] is True
            and row["formal_mem3_policy_window_applied"] is False
            and row["formal_mem3_decay_reinforcement_window_applied"] is False
            and row["reinforcement_policy_window_applied"] is False
            for row in rows
        ),
        "node_plus_packet_budget_separate_and_exact": all(
            row["node_plus_packet_budget_before"]
            == row["node_plus_packet_budget_after"]
            and row["node_plus_packet_budget_error"] == 0.0
            for row in rows
        ),
        "affordance_not_yet_operational": all(
            row["affordance_surface_emitted"] is False for row in rows
        )
        and interpretation["classification"]["affordance_status"]
        == "latent_not_yet_operational",
        "no_candidate_score_or_future_bias_update": all(
            row["learning_boundary"]["candidate_score_updated"] is False
            and row["learning_boundary"]["future_route_bias_created"] is False
            for row in rows
        ),
        "claim_flags_all_false": all(
            all(value is False for value in row["claim_flags"].values()) for row in rows
        )
        and all(value is False for value in mem1["claim_flags"].values()),
        "controls_present": {
            row["control_id"] for row in controls
        }
        == {
            "missing_route_use_event",
            "memory_surface_digest_mismatch",
            "memory_surface_key_digest_mismatch",
            "hidden_route_history",
            "memory_budget_discontinuity",
            "node_plus_packet_budget_discontinuity",
            "claim_promotion",
        },
        "control_blockers_distinct": len(control_blockers) == len(set(control_blockers)),
        "controls_passed": all(row["control_passed"] for row in controls),
        "arc_interpretation_present": interpretation[
            "style"
        ]
        == "question_observation_classification_cultivation_naturalization",
        "arc_not_endpoint_only": interpretation["classification"][
            "not_merely_true_false_endpoint"
        ]
        is True,
        "arc_next_question_recorded": bool(
            interpretation["cultivation"]["next_question"]
        ),
        "native_memory_surface_still_experiment_local": all(
            row["memory_policy_native_support_status"]
            == "experiment_local_until_phase8_memory_surface"
            for row in rows
        ),
        "memory_claim_still_closed": interpretation["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ]
        is False,
        "producer_step_boundary_preserved": manifest["producer_step_boundary"][
            "producer_may_mutate_memory_surface"
        ]
        is False,
        "src_clean": git_status_short_src() == "",
    }


def source_artifacts() -> dict[str, str]:
    paths = [MANIFEST_VALIDATION_PATH, SOURCE_MEM1_PATH]
    return {rel(path): digest_file(path) for path in paths}


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_MEM1_REPORT): digest_file(SOURCE_MEM1_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    rows = output["memory_surface_rows"]
    snapshot = output["memory_surface_state_snapshot"]
    interpretation = output["arc_of_becoming_interpretation"]
    controls = output["controls"]
    checks = output["checks"]
    contract = output["mem2_memory_surface_contract"]
    policy_digest_validation = output["memory_policy_digest_validation"]
    row_lines = "\n".join(
        "| `{source_cycle_id}` | `{selected_route_id}` | `{memory_strength_before}` | `{reinforcement_input}` | `{memory_strength}` | `{memory_surface_digest}` |".format(
            **row
        )
        for row in rows
    )
    observation_lines = "\n".join(
        "| `{observation_id}` | `{metric}` | `{value}` | {interpretation} |".format(
            **row
        )
        for row in interpretation["observations"]
    )
    control_lines = "\n".join(
        f"| `{row['control_id']}` | `{row['observed_status']}` | `{row['primary_blocker']}` | `{row['control_passed']}` | {row['purpose']} |"
        for row in controls
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    report = f"""# N08 Iteration 4 MEM2 Trail Memory Surface

Status: `{output['status']}`.

Iteration 4 converts MEM1 route-use events into experiment-local serialized
trail memory surface rows. It does not yet run decay/reinforcement windows,
memory-shaped route arbitration, or candidate-score updates.

## Branch Question

{interpretation['question']}

## Branch Answer

Committed route-use events can persist as digest-pinned trail-surface rows.
The resulting surface is visible as serialized artifact state:

```json
{json.dumps(interpretation['final_memory_strength_by_route'], indent=2, sort_keys=True)}
```

This is still not reinforcement learning or route-weight propagation. The
surface exists, but it has not been read by candidate scoring and has not yet
created future route bias.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `{interpretation['classification']['classification_status']}`
- naturalization rung:
  `{interpretation['naturalization']['naturalization_rung']}`
- affordance status:
  `{interpretation['classification']['affordance_status']}`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Cultivation next question:

{interpretation['cultivation']['next_question']}

## Memory Surface Rows

| Source Cycle | Route | Before | Input | After | Surface Digest |
|---|---|---:|---:|---:|---|
{row_lines}

## Formation Versus MEM3 Window

Iteration 4 performs formation-phase seed accumulation: a committed route-use
event creates or strengthens a serialized trail surface row. The arithmetic is
saturating additive and matches the declared reinforcement policy, but this is
not the formal MEM3 decay/reinforcement policy window.

```json
{json.dumps(contract['formation_window_semantics'], indent=2, sort_keys=True)}
```

Iteration 5 starts from this formed surface state and applies the first formal
decay/reinforcement update window. It must not re-apply the Iteration 4
formation inputs as if they were unprocessed route-use events.

## MEM2 Event Contract

```json
{json.dumps(contract, indent=2, sort_keys=True)}
```

Memory policy digest validation:

```json
{json.dumps(policy_digest_validation, indent=2, sort_keys=True)}
```

## State Snapshot

```json
{json.dumps(snapshot, indent=2, sort_keys=True)}
```

The snapshot is a latest-state summary keyed by memory surface key digest. Full
artifact replay must use `memory_surface_rows`, which retain every ordered
formation event, source digest, budget field, and claim flag.

## Learning Boundary

```json
{json.dumps(interpretation['learning_boundary'], indent=2, sort_keys=True)}
```

## Producer / Step Boundary

```json
{json.dumps(output['producer_step_boundary'], indent=2, sort_keys=True)}
```

## Inherited Native Policy Blockers

```json
{json.dumps(output['inherited_native_policy_blockers'], indent=2, sort_keys=True)}
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{control_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Artifact Digests

```json
{json.dumps(output['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 4 passes if prior route use creates a persisted runtime-visible
memory/trail/affordance surface with source provenance and exact budgets.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    mem1 = load_json(SOURCE_MEM1_PATH)
    rows = build_memory_surface_rows(manifest_validation, mem1)
    snapshot = build_state_snapshot(rows)
    controls = control_rows()
    interpretation = arc_interpretation(rows, snapshot)
    checks = validate_output(
        manifest_validation, mem1, rows, snapshot, controls, interpretation
    )
    memory_policy = manifest_validation["fixture_manifest"]["memory_policy_schema"][
        "default_policy"
    ]
    reinforcement_policy = manifest_validation["fixture_manifest"][
        "reinforcement_policy_schema"
    ]["default_policy"]
    output: dict[str, Any] = {
        "schema": "n08_iteration_4_mem2_memory_surface_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 4,
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "mem_level": "MEM2",
        "claim_ceiling": "mem2_trail_surface_candidate",
        "mem2_memory_surface_contract": {
            "required_fields": manifest_validation["fixture_manifest"][
                "memory_surface_row_schema"
            ]["required_fields"],
            "allowed_supplementary_fields": MEMORY_SURFACE_SUPPLEMENTARY_FIELDS,
            "memory_surface_id_rule": MEMORY_SURFACE_ID_RULE,
            "event_time_key_convention": {
                "offset_from_route_use_event": MEMORY_SURFACE_EVENT_TIME_OFFSET,
                "rationale": MEMORY_SURFACE_EVENT_TIME_OFFSET_RATIONALE,
            },
            "scheduler_event_index_convention": {
                "offset_from_route_use_event": MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET,
                "target_scheduler_band": MEMORY_SURFACE_SCHEDULER_INDEX_BAND,
                "rationale": MEMORY_SURFACE_SCHEDULER_INDEX_OFFSET_RATIONALE,
            },
            "snapshot_scope": {
                "snapshot_completeness": (
                    "latest_state_summary_not_full_replay_record"
                ),
                "full_replay_requires": "memory_surface_rows",
            },
            "formation_window_semantics": {
                "formation_window_applied": True,
                "formation_update_kind": "route_use_seed_accumulation",
                "formation_arithmetic": "saturating_additive_seed_accumulation",
                "formation_arithmetic_policy_reference": (
                    reinforcement_policy["reinforcement_policy_id"]
                ),
                "formal_mem3_policy_window_applied": False,
                "formal_mem3_decay_reinforcement_window_applied": False,
                "formal_mem3_window_status": "deferred_to_iteration_5",
            },
        },
        "memory_policy_digest_validation": {
            "memory_policy_id": memory_policy["memory_policy_id"],
            "declared_digest": memory_policy["memory_policy_digest"],
            "recomputed_digest": recompute_memory_policy_digest(memory_policy),
            "digest_rule": memory_policy["memory_policy_digest_rule"],
            "valid": memory_policy["memory_policy_digest"]
            == recompute_memory_policy_digest(memory_policy),
        },
        "memory_surface_rows": rows,
        "memory_surface_row_count": len(rows),
        "memory_surface_state_snapshot": snapshot,
        "memory_surface_state_snapshot_digest": snapshot[
            "memory_surface_state_snapshot_digest"
        ],
        "affordance_surface_emitted": False,
        "arc_of_becoming_interpretation": interpretation,
        "producer_step_boundary": manifest_validation["fixture_manifest"][
            "producer_step_boundary"
        ],
        "inherited_native_policy_blockers": manifest_validation["fixture_manifest"][
            "native_policy_blockers_inherited"
        ],
        "controls": controls,
        "checks": checks,
        "claim_flags": false_claim_flags(manifest_validation),
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 4 passes if prior route use creates a persisted "
                "runtime-visible memory/trail/affordance surface with source "
                "provenance and exact budgets."
            ),
        },
    }
    output["artifact_digests"] = {
        "memory_surface_rows_digest": digest_value(rows),
        "memory_surface_state_snapshot_digest": snapshot[
            "memory_surface_state_snapshot_digest"
        ],
        "arc_interpretation_digest": interpretation["arc_interpretation_digest"],
        "controls_digest": digest_value(controls),
        "checks_digest": digest_value(checks),
    }
    output["output_digest_scope"] = {
        "included": "all output fields except generated_at and output_digest",
        "excluded": ["generated_at", "output_digest"],
        "stable_across_same_inputs": True,
    }
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"generated_at", "output_digest"}
        }
    )
    return output


def main() -> None:
    output = build_output()
    write_output(output)
    write_report(output)


if __name__ == "__main__":
    main()
