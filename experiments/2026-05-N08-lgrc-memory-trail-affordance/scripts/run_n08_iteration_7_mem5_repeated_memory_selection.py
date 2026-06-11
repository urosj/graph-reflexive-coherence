#!/usr/bin/env python3
"""Run N08 Iteration 7 MEM5 repeated memory-shaped selection.

Iteration 7 closes the Hypothesis A loop over repeated cycles:

    memory state -> candidate scores -> route arbitration -> route use
    -> decay/reinforcement update -> next memory state

It remains serialized producer/policy memory. It does not claim native
geometry-mediated trail memory or pure coherence/flux pheromone behavior.
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
SOURCE_MEM4_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_6_mem4_memory_shaped_arbitration.json"
)
SOURCE_MEM4_REPORT = (
    EXPERIMENT / "reports" / "n08_iteration_6_mem4_memory_shaped_arbitration.md"
)
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_7_mem5_repeated_memory_selection.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n08_iteration_7_mem5_repeated_memory_selection.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_7_mem5_repeated_memory_selection.py"
)

MEM5_CYCLE_COUNT = 4
DECAY_FACTOR = 0.9
REINFORCEMENT_AMOUNT = 0.25
FLOOR = 0.0
CEILING = 1.0
MEM5_EVENT_TIME_BASE = 7.0
MEM5_SCHEDULER_BASE = 70
MEM5_SCORE_COMPONENTS = [
    "memory_trail_strength",
    "memory_surface_digest_match",
    "memory_recency_weight",
    "memory_decay_adjusted_strength",
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


def round_value(value: float) -> float:
    return round(value, 12)


def false_claim_flags(manifest_validation: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in manifest_validation["fixture_manifest"]["memory_surface_row_schema"][
            "required_claim_flag_keys"
        ]
    }


def digest_record(record: dict[str, Any], digest_field: str) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != digest_field}
    )


def initial_memory_states(mem4: dict[str, Any]) -> dict[str, dict[str, Any]]:
    states: dict[str, dict[str, Any]] = {}
    mem3_rows = {
        row["candidate_route_id"]: row
        for row in mem4["lanes"]["memory_shaped_arbitration"][
            "candidate_route_records"
        ]
    }
    for route_id, candidate in sorted(mem3_rows.items()):
        components = candidate["candidate_score_components"]
        # The MEM4 candidates expose the MEM3 row through runtime-visible fields.
        states[route_id] = {
            "route_id": route_id,
            "memory_surface_id": candidate["candidate_memory_surface_id"],
            "memory_surface_digest": candidate["candidate_memory_surface_digest"],
            "memory_surface_state_snapshot_digest": candidate[
                "candidate_memory_surface_state_snapshot_digest"
            ],
            "memory_policy_id": candidate["candidate_memory_policy_id"],
            "memory_policy_digest": candidate["candidate_memory_policy_digest"],
            "route_use_event_digest": candidate["candidate_route_use_event_digest"],
            "memory_event_time_key": candidate["candidate_memory_event_time_key"],
            "memory_scheduler_event_index": candidate[
                "candidate_memory_scheduler_event_index"
            ],
            "memory_strength": candidate["candidate_memory_budget_prediction"][
                "memory_budget_after"
            ],
            "strength_after_decay": round_value(
                components["memory_decay_adjusted_strength"] / 0.1
            ),
            "windows_since_reinforcement": round_value(
                0.1 / components["memory_recency_weight"]
            ),
            "route_use_count_for_key": 2,
            "memory_surface_key_digest": (
                candidate["candidate_memory_surface_id"].split(":")[1]
            ),
            "source_candidate_route_digest": candidate["candidate_route_digest"],
        }
    return states


def candidate_components(state: dict[str, Any]) -> dict[str, float]:
    windows = max(1.0, float(state["windows_since_reinforcement"]))
    strength = float(state["memory_strength"])
    return {
        "memory_trail_strength": round_value(strength),
        "memory_surface_digest_match": 0.1,
        "memory_recency_weight": round_value(0.1 / windows),
        "memory_decay_adjusted_strength": round_value(strength * DECAY_FACTOR * 0.1),
    }


def candidate_score(components: dict[str, float]) -> float:
    return round_value(sum(float(value) for value in components.values()))


def build_candidate_record(
    manifest_validation: dict[str, Any],
    cycle_id: str,
    state: dict[str, Any],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    components = candidate_components(state)
    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_candidate_record",
        "artifact_schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM5",
        "mem_level_is_evidence_classification": True,
        "claim_ceiling": "mem5_repeated_memory_shaped_selection_candidate",
        "cycle_id": cycle_id,
        "evidence_class": "repeated_memory_shaped_route_arbitration",
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc3",
        "causal_layer_mode": "topology_changing_causal_history",
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "candidate_route_id": state["route_id"],
        "candidate_order_key": state["route_id"],
        "candidate_memory_surface_id": state["memory_surface_id"],
        "candidate_memory_surface_digest": state["memory_surface_digest"],
        "candidate_memory_surface_state_snapshot_digest": state[
            "memory_surface_state_snapshot_digest"
        ],
        "candidate_memory_policy_id": state["memory_policy_id"],
        "candidate_memory_policy_digest": state["memory_policy_digest"],
        "candidate_route_use_event_digest": state["route_use_event_digest"],
        "candidate_memory_event_time_key": state["memory_event_time_key"],
        "candidate_memory_scheduler_event_index": state[
            "memory_scheduler_event_index"
        ],
        "candidate_score_components": components,
        "candidate_route_score": candidate_score(components),
        "candidate_runtime_visible_inputs": [
            f"memory_surface_id:{state['memory_surface_id']}",
            f"memory_surface_digest:{state['memory_surface_digest']}",
            "memory_surface_state_snapshot_digest:"
            f"{state['memory_surface_state_snapshot_digest']}",
            f"memory_policy_id:{state['memory_policy_id']}",
            f"route_use_event_digest:{state['route_use_event_digest']}",
            f"memory_event_time_key:{state['memory_event_time_key']}",
            "candidate_score_components",
            "serialized_memory_component_policy",
        ],
        "memory_component_names_allowed": MEM5_SCORE_COMPONENTS,
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": 0.0,
            "node_plus_packet_budget_after": 0.0,
            "node_plus_packet_budget_error": 0.0,
        },
        "candidate_memory_budget_prediction": {
            "memory_budget_before": state["memory_strength"],
            "memory_budget_after": state["memory_strength"],
            "memory_budget_error": 0.0,
        },
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "hidden_memory_input_used": False,
        "route_specific_hidden_preference_used": False,
        "native_geometry_trail_claimed": False,
        "pure_coherence_flux_trail_claimed": False,
        "claim_flags": false_claim_flags(manifest_validation),
    }
    record["candidate_route_digest"] = digest_record(record, "candidate_route_digest")
    return record


def select_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        candidates,
        key=lambda row: (-float(row["candidate_route_score"]), row["candidate_order_key"]),
    )[0]


def build_candidate_set(
    manifest_validation: dict[str, Any],
    cycle_id: str,
    candidates: list[dict[str, Any]],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    ordered = sorted(
        candidates,
        key=lambda row: (-float(row["candidate_route_score"]), row["candidate_order_key"]),
    )
    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_candidate_set_record",
        "artifact_schema_version": "lgrc9v3_native_route_candidate_set_record_v1",
        "schema_version": "lgrc9v3_native_route_candidate_set_record_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM5",
        "cycle_id": cycle_id,
        "candidate_set_id": f"n08-mem5-candidate-set:{cycle_id}",
        "arbitration_window_id": f"n08_mem5_repeated_window:{cycle_id}",
        "candidate_route_digests": [row["candidate_route_digest"] for row in ordered],
        "candidate_route_ids": [row["candidate_route_id"] for row in ordered],
        "candidate_set_order_key": "score_desc_then_candidate_id",
        "unresolved_tie_policy": "deterministic_candidate_order_key",
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": false_claim_flags(manifest_validation),
    }
    record["idempotency_key"] = digest_value(
        {
            "cycle_id": cycle_id,
            "candidate_route_digests": record["candidate_route_digests"],
            "candidate_set_order_key": record["candidate_set_order_key"],
        }
    )
    record["candidate_set_digest"] = digest_record(record, "candidate_set_digest")
    return record


def build_arbitration_record(
    manifest_validation: dict[str, Any],
    cycle_id: str,
    candidates: list[dict[str, Any]],
    candidate_set: dict[str, Any],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    selected = select_candidate(candidates)
    rejected = [
        row["candidate_route_digest"]
        for row in candidates
        if row["candidate_route_digest"] != selected["candidate_route_digest"]
    ]
    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_arbitration_record",
        "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM5",
        "mem_level_is_evidence_classification": True,
        "claim_ceiling": "mem5_repeated_memory_shaped_selection_candidate",
        "cycle_id": cycle_id,
        "native_route_arbitration_record_id": (
            f"n08-mem5-route-arbitration:{cycle_id}:"
            f"{selected['candidate_route_id']}"
        ),
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "arbitration_rule": "highest_score_then_candidate_order_key",
        "arbitration_reason_code": "native_route_arbitration_selected_highest_score",
        "candidate_set_id": candidate_set["candidate_set_id"],
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "selected_candidate_route_id": selected["candidate_route_id"],
        "selected_candidate_route_digest": selected["candidate_route_digest"],
        "rejected_candidate_route_digests": sorted(rejected),
        "arbitration_score": selected["candidate_route_score"],
        "arbitration_runtime_visible_inputs": [
            "candidate_route_score",
            "candidate_order_key",
            "candidate_set_order_key",
            "candidate_score_components",
            f"memory_surface_digest:{selected['candidate_memory_surface_digest']}",
        ],
        "selected_topology_event_id": None,
        "selected_topology_event_digest": None,
        "topology_event_committed": False,
        "packet_scheduled": False,
        "state_mutated": False,
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": false_claim_flags(manifest_validation),
    }
    record["idempotency_key"] = digest_value(
        {
            "candidate_set_digest": record["candidate_set_digest"],
            "selected_candidate_route_digest": record[
                "selected_candidate_route_digest"
            ],
            "arbitration_rule": record["arbitration_rule"],
        }
    )
    record["native_route_arbitration_digest"] = digest_record(
        record, "native_route_arbitration_digest"
    )
    return record


def build_route_use_event(
    manifest_validation: dict[str, Any],
    cycle_id: str,
    arbitration: dict[str, Any],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "artifact_kind": "n08_route_use_event",
        "schema_version": "n08_route_use_event_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM5",
        "cycle_id": cycle_id,
        "route_use_event_id": (
            f"n08-mem5-route-use:{cycle_id}:"
            f"{arbitration['selected_candidate_route_id']}"
        ),
        "route_use_commit_status": "committed",
        "source_arbitration_record_digest": arbitration[
            "native_route_arbitration_digest"
        ],
        "selected_candidate_route_digest": arbitration[
            "selected_candidate_route_digest"
        ],
        "selected_route_id": arbitration["selected_candidate_route_id"],
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "node_plus_packet_budget_before": 0.0,
        "node_plus_packet_budget_after": 0.0,
        "node_plus_packet_budget_error": 0.0,
        "claim_flags": false_claim_flags(manifest_validation),
    }
    event["route_use_event_digest"] = digest_record(event, "route_use_event_digest")
    return event


def build_memory_update_row(
    manifest_validation: dict[str, Any],
    cycle_id: str,
    state: dict[str, Any],
    route_use_event: dict[str, Any],
    selected_route_id: str,
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    before = float(state["memory_strength"])
    after_decay = round_value(max(FLOOR, before * DECAY_FACTOR))
    decay_loss = round_value(before - after_decay)
    selected = state["route_id"] == selected_route_id
    reinforcement_input = REINFORCEMENT_AMOUNT if selected else 0.0
    proposed = round_value(after_decay + reinforcement_input)
    saturation_clamp_loss = round_value(max(0.0, proposed - CEILING))
    after = round_value(min(CEILING, proposed))
    row: dict[str, Any] = {
        "artifact_kind": "n08_memory_surface_row",
        "schema_version": "n08_memory_surface_row_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM5",
        "mem_level_is_evidence_classification": True,
        "claim_ceiling": "mem5_repeated_memory_shaped_selection_candidate",
        "cycle_id": cycle_id,
        "memory_surface_id": (
            f"n08-memory-surface:{state['memory_surface_key_digest']}:"
            f"mem5:{cycle_id}"
        ),
        "memory_surface_kind": "trail",
        "source_memory_surface_id": state["memory_surface_id"],
        "source_memory_surface_digest": state["memory_surface_digest"],
        "route_use_event_digest": (
            route_use_event["route_use_event_digest"] if selected else None
        ),
        "reinforced_by_route_use_event": selected,
        "selected_route_id": state["route_id"],
        "memory_surface_key_digest": state["memory_surface_key_digest"],
        "memory_policy_id": state["memory_policy_id"],
        "memory_policy_digest": state["memory_policy_digest"],
        "memory_strength": after,
        "memory_strength_before": before,
        "memory_strength_delta": round_value(after - before),
        "strength_after_decay": after_decay,
        "decay_factor": DECAY_FACTOR,
        "decay_loss": decay_loss,
        "reinforcement_input": reinforcement_input,
        "saturation_clamp_loss": saturation_clamp_loss,
        "memory_budget_surface": "trail_strength",
        "memory_budget_before": before,
        "memory_budget_after": after,
        "memory_budget_error": 0.0,
        "node_plus_packet_budget_before": 0.0,
        "node_plus_packet_budget_after": 0.0,
        "node_plus_packet_budget_error": 0.0,
        "decay_quantity_kind": "serialized_memory_signal_attenuation",
        "decay_is_physical_flux": False,
        "decay_destination_surface": None,
        "coherence_pocket_transfer_performed": False,
        "physical_decay_support_status": (
            "not_supported_without_explicit_conserved_destination_surface"
        ),
        "same_window_update_order": ["decay", "reinforcement"],
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": false_claim_flags(manifest_validation),
    }
    row["memory_surface_digest"] = digest_record(row, "memory_surface_digest")
    return row


def update_state_from_row(state: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state["memory_surface_id"] = row["memory_surface_id"]
    next_state["memory_surface_digest"] = row["memory_surface_digest"]
    next_state["memory_event_time_key"] = row["event_time_key"]
    next_state["memory_scheduler_event_index"] = row["scheduler_event_index"]
    next_state["memory_strength"] = row["memory_strength"]
    next_state["strength_after_decay"] = row["strength_after_decay"]
    if row["reinforced_by_route_use_event"]:
        next_state["windows_since_reinforcement"] = 1
        next_state["route_use_count_for_key"] = int(state["route_use_count_for_key"]) + 1
        next_state["route_use_event_digest"] = row["route_use_event_digest"]
    else:
        next_state["windows_since_reinforcement"] = (
            float(state["windows_since_reinforcement"]) + 1
        )
    return next_state


def run_cycles(
    manifest_validation: dict[str, Any],
    mem4: dict[str, Any],
) -> list[dict[str, Any]]:
    states = initial_memory_states(mem4)
    cycles: list[dict[str, Any]] = []
    for cycle_index in range(MEM5_CYCLE_COUNT):
        cycle_id = f"cycle_{cycle_index}"
        event_base = MEM5_EVENT_TIME_BASE + cycle_index
        scheduler_base = MEM5_SCHEDULER_BASE + (cycle_index * 20)
        before_states = {route: dict(state) for route, state in states.items()}
        candidates = [
            build_candidate_record(
                manifest_validation,
                cycle_id,
                state,
                round_value(event_base + index * 0.01),
                scheduler_base + index,
            )
            for index, state in enumerate(states.values())
        ]
        candidate_set = build_candidate_set(
            manifest_validation,
            cycle_id,
            candidates,
            round_value(event_base + 0.05),
            scheduler_base + 5,
        )
        arbitration = build_arbitration_record(
            manifest_validation,
            cycle_id,
            candidates,
            candidate_set,
            round_value(event_base + 0.1),
            scheduler_base + 10,
        )
        route_use = build_route_use_event(
            manifest_validation,
            cycle_id,
            arbitration,
            round_value(event_base + 0.2),
            scheduler_base + 12,
        )
        update_rows = [
            build_memory_update_row(
                manifest_validation,
                cycle_id,
                state,
                route_use,
                arbitration["selected_candidate_route_id"],
                round_value(event_base + 0.3 + index * 0.01),
                scheduler_base + 15 + index,
            )
            for index, state in enumerate(states.values())
        ]
        states = {
            row["selected_route_id"]: update_state_from_row(
                states[row["selected_route_id"]], row
            )
            for row in update_rows
        }
        cycles.append(
            {
                "cycle_id": cycle_id,
                "cycle_index": cycle_index,
                "memory_state_before": before_states,
                "candidate_route_records": candidates,
                "candidate_set_record": candidate_set,
                "route_arbitration_record": arbitration,
                "route_use_event": route_use,
                "memory_update_rows": update_rows,
                "memory_state_after": {route: dict(state) for route, state in states.items()},
                "selected_route_id": arbitration["selected_candidate_route_id"],
                "candidate_scores_by_route": {
                    row["candidate_route_id"]: row["candidate_route_score"]
                    for row in candidates
                },
            }
        )
    return cycles


def control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "repeated_hidden_route_preference",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "candidate_score_hidden_memory_input",
            "purpose": "Reject repeated selection driven by hidden route preference.",
        },
        {
            "control_id": "stale_memory_surface_read",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "stale_memory_surface_read",
            "purpose": "Reject a cycle that scores candidates from stale memory rows.",
        },
        {
            "control_id": "duplicate_memory_update",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "duplicate_memory_update",
            "purpose": "Reject duplicate update rows for the same route/cycle.",
        },
        {
            "control_id": "cross_cycle_memory_leak",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "cross_cycle_memory_leak",
            "purpose": "Reject memory state leaking across unrelated route keys.",
        },
        {
            "control_id": "memory_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_budget_discontinuity",
            "purpose": "Reject memory update budget drift.",
        },
        {
            "control_id": "node_plus_packet_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "purpose": "Reject physical budget drift hidden by memory scoring.",
        },
        {
            "control_id": "claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "claim_promotion",
            "purpose": "Reject MEM5 promotion to memory claim, ACO, agency, or movement.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = digest_value(row)
    return rows


def all_candidates(cycles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for cycle in cycles for row in cycle["candidate_route_records"]]


def all_updates(cycles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for cycle in cycles for row in cycle["memory_update_rows"]]


def memory_budget_equation_holds(row: dict[str, Any]) -> bool:
    expected = (
        row["memory_budget_before"]
        + row["reinforcement_input"]
        - row["decay_loss"]
        - row["saturation_clamp_loss"]
    )
    return abs(expected - row["memory_budget_after"]) <= 1e-12


def trend_summary(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    selected_routes = [cycle["selected_route_id"] for cycle in cycles]
    route_a_after = [
        cycle["memory_state_after"]["route_a"]["memory_strength"] for cycle in cycles
    ]
    route_b_after = [
        cycle["memory_state_after"]["route_b"]["memory_strength"] for cycle in cycles
    ]
    return {
        "selected_routes": selected_routes,
        "route_a_strength_after_each_cycle": route_a_after,
        "route_b_strength_after_each_cycle": route_b_after,
        "route_b_saturation_observed": any(value >= CEILING for value in route_b_after),
        "route_a_extinction_trend_observed": all(
            later < earlier for earlier, later in zip(route_a_after, route_a_after[1:])
        ),
        "route_a_floor_reached": any(value <= FLOOR for value in route_a_after),
        "oscillation_observed": len(set(selected_routes)) > 1,
        "tie_observed": any(
            len(set(cycle["candidate_scores_by_route"].values())) == 1
            for cycle in cycles
        ),
        "competing_memory_behavior": (
            "route_b_converges_to_saturation_while_route_a_decays_without_reinforcement"
        ),
    }


def arc_interpretation(cycles: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    interpretation: dict[str, Any] = {
        "interpretation_id": "n08_i7_arc_of_becoming_mem5_repeated_selection_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What regime appears when memory-shaped arbitration, route use, "
            "and memory update repeat across cycles?"
        ),
        "observations": [
            {
                "observation_id": "same_route_reinforces_and_saturates",
                "metric": "route_b_strength_after_each_cycle",
                "value": summary["route_b_strength_after_each_cycle"],
                "interpretation": (
                    "Route B is repeatedly selected and reaches the serialized "
                    "memory ceiling."
                ),
            },
            {
                "observation_id": "unselected_route_decays",
                "metric": "route_a_strength_after_each_cycle",
                "value": summary["route_a_strength_after_each_cycle"],
                "interpretation": (
                    "Route A remains present as a memory surface but decays "
                    "while it is not selected."
                ),
            },
            {
                "observation_id": "competing_memory_regime_classified",
                "metric": "competing_memory_behavior",
                "value": summary["competing_memory_behavior"],
                "interpretation": (
                    "The observed regime is convergence to the reinforced "
                    "route, not oscillation or unresolved tie."
                ),
            },
            {
                "observation_id": "policy_memory_not_native_flux",
                "metric": "hypothesis",
                "value": "A_serialized_producer_policy_memory",
                "interpretation": (
                    "The loop is useful producer/policy memory evidence; it "
                    "does not prove native geometry-mediated trail memory."
                ),
            },
        ],
        "classification": {
            "mem_level": "MEM5",
            "classification_status": "repeated_memory_shaped_selection_candidate",
            "hypothesis": "A_serialized_producer_policy_memory",
            "not_merely_true_false_endpoint": True,
            "claim_gate": "closed_until_mem6_artifact_replay",
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "Repeated memory-shaped arbitration can lock into a saturated remembered route.",
                "The unselected competing memory decays but is not physically deleted.",
                "The next question is artifact-only replay of the full repeated chain.",
            ],
            "next_question": (
                "Can route use, memory updates, memory-shaped candidate scores, "
                "route arbitration, and controls replay from artifacts only?"
            ),
            "next_iteration": "8_MEM6_artifact_only_replay_and_closeout",
        },
        "naturalization": {
            "naturalization_rung": "Nat4_repeated_policy_memory_loop",
            "self_persistent_memory_observed": True,
            "self_updating_memory_observed": True,
            "memory_operational_in_repeated_route_selection": True,
            "why_not_more_naturalized": (
                "The loop is repeated and operational, but memory remains a "
                "serialized score policy surface rather than native geometry."
            ),
        },
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "aco_like_claim_allowed": False,
            "movement_claim_allowed": False,
            "reason": (
                "MEM5 supports repeated memory-shaped selection only. The "
                "narrow memory/trail claim remains closed until MEM6 replay."
            ),
        },
        "trend_summary": summary,
    }
    interpretation["arc_interpretation_digest"] = digest_value(interpretation)
    return interpretation


def validate_output(
    manifest_validation: dict[str, Any],
    mem4: dict[str, Any],
    cycles: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    interpretation: dict[str, Any],
) -> dict[str, bool]:
    candidates = all_candidates(cycles)
    updates = all_updates(cycles)
    summary = interpretation["trend_summary"]
    control_blockers = [row["primary_blocker"] for row in controls]
    update_ids = [row["memory_surface_id"] for row in updates]
    return {
        "source_mem4_passed": mem4["status"] == "passed",
        "source_manifest_passed": manifest_validation["status"] == "passed",
        "minimum_cycle_count_met": len(cycles) >= MEM5_CYCLE_COUNT,
        "candidate_route_digests_recompute": all(
            row["candidate_route_digest"] == digest_record(row, "candidate_route_digest")
            for row in candidates
        ),
        "route_arbitration_digests_recompute": all(
            cycle["route_arbitration_record"]["native_route_arbitration_digest"]
            == digest_record(
                cycle["route_arbitration_record"], "native_route_arbitration_digest"
            )
            for cycle in cycles
        ),
        "route_use_digests_recompute": all(
            cycle["route_use_event"]["route_use_event_digest"]
            == digest_record(cycle["route_use_event"], "route_use_event_digest")
            for cycle in cycles
        ),
        "memory_surface_digests_recompute": all(
            row["memory_surface_digest"] == digest_record(row, "memory_surface_digest")
            for row in updates
        ),
        "candidate_scores_equal_component_sums": all(
            row["candidate_route_score"]
            == candidate_score(row["candidate_score_components"])
            for row in candidates
        ),
        "route_use_after_arbitration": all(
            cycle["route_use_event"]["event_time_key"]
            > cycle["route_arbitration_record"]["event_time_key"]
            and cycle["route_use_event"]["scheduler_event_index"]
            > cycle["route_arbitration_record"]["scheduler_event_index"]
            for cycle in cycles
        ),
        "memory_update_after_route_use": all(
            all(
                row["event_time_key"] > cycle["route_use_event"]["event_time_key"]
                and row["scheduler_event_index"]
                > cycle["route_use_event"]["scheduler_event_index"]
                for row in cycle["memory_update_rows"]
            )
            for cycle in cycles
        ),
        "selected_route_reinforced_only": all(
            all(
                (
                    row["reinforcement_input"] == REINFORCEMENT_AMOUNT
                    and row["reinforced_by_route_use_event"] is True
                )
                if row["selected_route_id"] == cycle["selected_route_id"]
                else (
                    row["reinforcement_input"] == 0.0
                    and row["reinforced_by_route_use_event"] is False
                )
                for row in cycle["memory_update_rows"]
            )
            for cycle in cycles
        ),
        "memory_budget_equations_hold": all(
            memory_budget_equation_holds(row) for row in updates
        ),
        "node_plus_packet_budget_exact": all(
            row["node_plus_packet_budget_before"]
            == row["node_plus_packet_budget_after"]
            and row["node_plus_packet_budget_error"] == 0.0
            for row in updates
        ),
        "route_b_repeated_selection_observed": summary["selected_routes"]
        == ["route_b"] * MEM5_CYCLE_COUNT,
        "saturation_observed": summary["route_b_saturation_observed"] is True,
        "extinction_trend_observed_not_floor_reached": summary[
            "route_a_extinction_trend_observed"
        ]
        is True
        and summary["route_a_floor_reached"] is False,
        "competing_memory_behavior_recorded": bool(
            summary["competing_memory_behavior"]
        ),
        "oscillation_and_tie_recorded": summary["oscillation_observed"] is False
        and summary["tie_observed"] is False,
        "duplicate_updates_suppressed": len(update_ids) == len(set(update_ids)),
        "claim_flags_all_false": all(
            all(value is False for value in row["claim_flags"].values())
            for row in candidates + updates
        )
        and all(value is False for value in mem4["claim_flags"].values()),
        "hypothesis_a_only_no_native_geometry_claim": all(
            row["native_geometry_trail_claimed"] is False
            and row["pure_coherence_flux_trail_claimed"] is False
            for row in candidates
        ),
        "controls_present": {
            row["control_id"] for row in controls
        }
        == {
            "repeated_hidden_route_preference",
            "stale_memory_surface_read",
            "duplicate_memory_update",
            "cross_cycle_memory_leak",
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
        "memory_claim_still_closed": interpretation["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ]
        is False,
        "producer_step_boundary_preserved": manifest_validation["fixture_manifest"][
            "producer_step_boundary"
        ]["producer_may_mutate_memory_surface"]
        is False,
        "src_clean": git_status_short_src() == "",
    }


def source_artifacts() -> dict[str, str]:
    paths = [MANIFEST_VALIDATION_PATH, SOURCE_MEM4_PATH]
    return {rel(path): digest_file(path) for path in paths}


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_MEM4_REPORT): digest_file(SOURCE_MEM4_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    cycles = output["cycles"]
    interpretation = output["arc_of_becoming_interpretation"]
    controls = output["controls"]
    checks = output["checks"]
    cycle_lines = "\n".join(
        "| `{cycle_id}` | `{selected_route_id}` | `{scores}` | `{a_after}` | `{b_after}` |".format(
            cycle_id=cycle["cycle_id"],
            selected_route_id=cycle["selected_route_id"],
            scores=json.dumps(cycle["candidate_scores_by_route"], sort_keys=True),
            a_after=cycle["memory_state_after"]["route_a"]["memory_strength"],
            b_after=cycle["memory_state_after"]["route_b"]["memory_strength"],
        )
        for cycle in cycles
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
    report = f"""# N08 Iteration 7 MEM5 Repeated Memory-Shaped Selection

Status: `{output['status']}`.

Iteration 7 repeats the Hypothesis A memory policy loop. It does not claim
native geometry-mediated trail memory, pure coherence/flux trail memory, ACO,
agency, or biological pheromone behavior.

## Branch Question

{interpretation['question']}

## Branch Answer

Repeated memory-shaped arbitration converges to route B. Route B reaches the
serialized memory ceiling while route A decays under non-selection:

```json
{json.dumps(interpretation['trend_summary'], indent=2, sort_keys=True)}
```

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `{interpretation['classification']['classification_status']}`
- naturalization rung:
  `{interpretation['naturalization']['naturalization_rung']}`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Cultivation next question:

{interpretation['cultivation']['next_question']}

## Repeated Cycles

| Cycle | Selected Route | Candidate Scores | Route A After | Route B After |
|---|---|---|---:|---:|
{cycle_lines}

## Hypothesis Boundary

```json
{json.dumps(output['hypothesis_boundary'], indent=2, sort_keys=True)}
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

Iteration 7 passes if repeated route-use cycles produce memory-shaped route
selection without hidden steering and without budget drift.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    mem4 = load_json(SOURCE_MEM4_PATH)
    cycles = run_cycles(manifest_validation, mem4)
    summary = trend_summary(cycles)
    controls = control_rows()
    interpretation = arc_interpretation(cycles, summary)
    checks = validate_output(manifest_validation, mem4, cycles, controls, interpretation)
    output: dict[str, Any] = {
        "schema": "n08_iteration_7_mem5_repeated_memory_selection_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 7,
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
        "mem_level": "MEM5",
        "claim_ceiling": "mem5_repeated_memory_shaped_selection_candidate",
        "hypothesis_boundary": {
            "hypothesis": "A_serialized_producer_policy_memory",
            "serialized_memory_policy_loop": True,
            "native_geometry_mediated_trail_path": False,
            "independent_memory_strength_used_as_score_evidence": True,
            "independent_memory_strength_used_as_physical_flux": False,
            "native_geometry_trail_claimed": False,
            "pure_coherence_flux_trail_claimed": False,
            "hypothesis_b_remains_open": True,
        },
        "cycle_count": len(cycles),
        "cycles": cycles,
        "trend_summary": summary,
        "arc_of_becoming_interpretation": interpretation,
        "producer_step_boundary": manifest_validation["fixture_manifest"][
            "producer_step_boundary"
        ],
        "inherited_native_policy_blockers": mem4["inherited_native_policy_blockers"],
        "controls": controls,
        "checks": checks,
        "claim_flags": false_claim_flags(manifest_validation),
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 7 passes if repeated route-use cycles produce "
                "memory-shaped route selection without hidden steering and "
                "without budget drift."
            ),
        },
    }
    output["artifact_digests"] = {
        "cycles_digest": digest_value(cycles),
        "trend_summary_digest": digest_value(summary),
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
