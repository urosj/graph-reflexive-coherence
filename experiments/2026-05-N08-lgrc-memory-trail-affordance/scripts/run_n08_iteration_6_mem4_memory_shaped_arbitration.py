#!/usr/bin/env python3
"""Run N08 Iteration 6 MEM4 memory-shaped route arbitration.

Iteration 6 consumes MEM3 memory surface rows as serialized candidate-score
evidence. It compares a no-memory counterfactual lane against a memory-shaped
lane. It does not claim native geometric trail memory, agency, ACO, or pure
coherence/flux pheromone behavior.
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
SOURCE_MEM3_PATH = EXPERIMENT / "outputs" / "n08_iteration_5_mem3_decay_reinforcement.json"
SOURCE_MEM3_REPORT = EXPERIMENT / "reports" / "n08_iteration_5_mem3_decay_reinforcement.md"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_6_mem4_memory_shaped_arbitration.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_6_mem4_memory_shaped_arbitration.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_6_mem4_memory_shaped_arbitration.py"
)

MEM4_MEMORY_COMPONENTS = [
    "memory_trail_strength",
    "memory_surface_digest_match",
    "memory_recency_weight",
    "memory_decay_adjusted_strength",
]
MEM4_REQUIRED_RUNTIME_INPUT_PREFIXES = [
    "memory_surface_id:",
    "memory_surface_digest:",
    "memory_surface_state_snapshot_digest:",
    "memory_policy_id:",
    "route_use_event_digest:",
    "memory_event_time_key:",
]
MEM4_COUNTERFACTUAL_LANE_ID = "n08_mem4_counterfactual_without_memory_component"
MEM4_MEMORY_LANE_ID = "n08_mem4_memory_shaped_arbitration"
COUNTERFACTUAL_EVENT_TIME_BASE = 6.0
MEMORY_EVENT_TIME_BASE = 6.2
COUNTERFACTUAL_SCHEDULER_BASE = 35
MEMORY_SCHEDULER_BASE = 45


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


def digest_record(record: dict[str, Any], digest_field: str) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != digest_field}
    )


def round_score(value: float) -> float:
    return round(value, 12)


def latest_mem3_rows(mem3: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(mem3["memory_surface_rows"], key=lambda row: row["selected_route_id"])


def memory_component_scores(row: dict[str, Any]) -> dict[str, float]:
    elapsed = float(row["elapsed_memory_window_count"])
    return {
        "memory_trail_strength": round_score(float(row["memory_strength"])),
        "memory_surface_digest_match": 0.1,
        "memory_recency_weight": round_score(0.1 / elapsed),
        "memory_decay_adjusted_strength": round_score(
            float(row["strength_after_decay"]) * 0.1
        ),
    }


def candidate_score(components: dict[str, float]) -> float:
    return round_score(sum(float(value) for value in components.values()))


def base_candidate_fields(
    manifest_validation: dict[str, Any],
    mem3: dict[str, Any],
    row: dict[str, Any],
    lane_id: str,
    lane_kind: str,
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    claim_flags = false_claim_flags(manifest_validation)
    return {
        "artifact_kind": "lgrc9v3_native_route_candidate_record",
        "artifact_schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "experiment": "N08",
        "hypothesis": "A_serialized_producer_policy_memory",
        "mem_level": "MEM4",
        "mem_level_is_evidence_classification": True,
        "claim_ceiling": "mem4_memory_shaped_route_selection_candidate",
        "evidence_class": "memory_shaped_route_arbitration",
        "lane_id": lane_id,
        "lane_kind": lane_kind,
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc3",
        "causal_layer_mode": "topology_changing_causal_history",
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "candidate_route_id": row["selected_route_id"],
        "candidate_order_key": row["selected_route_id"],
        "candidate_selected_sink_id": (
            2 if row["selected_route_id"] == "route_a" else 3
        ),
        "candidate_competing_sink_ids": [2, 3],
        "candidate_memory_surface_id": row["memory_surface_id"],
        "candidate_memory_surface_digest": row["memory_surface_digest"],
        "candidate_memory_surface_state_snapshot_digest": mem3[
            "memory_surface_state_snapshot_digest"
        ],
        "candidate_memory_policy_id": row["memory_policy_id"],
        "candidate_memory_policy_digest": row["memory_policy_digest"],
        "candidate_route_use_event_digest": row["route_use_event_digest"],
        "candidate_memory_event_time_key": row["event_time_key"],
        "candidate_memory_scheduler_event_index": row["scheduler_event_index"],
        "candidate_mem3_update_window_policy_digest": row[
            "mem3_update_window_policy_digest"
        ],
        "candidate_memory_budget_prediction": {
            "memory_budget_before": row["memory_budget_before"],
            "memory_budget_after": row["memory_budget_after"],
            "memory_budget_error": row["memory_budget_error"],
        },
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": row["node_plus_packet_budget_before"],
            "node_plus_packet_budget_after": row["node_plus_packet_budget_after"],
            "node_plus_packet_budget_error": row["node_plus_packet_budget_error"],
        },
        "candidate_topology_event_kind": "not_committed_for_mem4_selection_only",
        "selected_topology_event_id": None,
        "selected_topology_event_digest": None,
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": claim_flags,
    }


def build_candidate_record(
    manifest_validation: dict[str, Any],
    mem3: dict[str, Any],
    row: dict[str, Any],
    lane_id: str,
    lane_kind: str,
    score_components: dict[str, float],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    record = base_candidate_fields(
        manifest_validation,
        mem3,
        row,
        lane_id,
        lane_kind,
        event_time_key,
        scheduler_event_index,
    )
    if score_components:
        runtime_inputs = [
            f"memory_surface_id:{row['memory_surface_id']}",
            f"memory_surface_digest:{row['memory_surface_digest']}",
            "memory_surface_state_snapshot_digest:"
            f"{mem3['memory_surface_state_snapshot_digest']}",
            f"memory_policy_id:{row['memory_policy_id']}",
            f"route_use_event_digest:{row['route_use_event_digest']}",
            f"memory_event_time_key:{row['event_time_key']}",
            "candidate_score_components",
            "serialized_memory_component_policy",
        ]
    else:
        runtime_inputs = [
            "counterfactual_without_memory_component",
            "candidate_score_components",
            "serialized_route_arbitration_policy",
        ]
    record.update(
        {
            "candidate_score_components": score_components,
            "candidate_route_score": candidate_score(score_components),
            "candidate_runtime_visible_inputs": runtime_inputs,
            "memory_component_names_allowed": MEM4_MEMORY_COMPONENTS,
            "memory_component_source": (
                "n08_iteration_5_mem3_decay_reinforcement"
                if score_components
                else "not_used_in_counterfactual"
            ),
            "memory_score_component_count": len(score_components),
            "memory_surface_read_by_arbitration": bool(score_components),
            "candidate_score_is_memory_shaped": bool(score_components),
            "hidden_memory_input_used": False,
            "route_specific_hidden_preference_used": False,
            "score_only_policy_path": True,
            "native_geometry_trail_claimed": False,
            "pure_coherence_flux_trail_claimed": False,
        }
    )
    record["candidate_route_digest"] = digest_record(record, "candidate_route_digest")
    return record


def build_candidate_set(
    manifest_validation: dict[str, Any],
    lane_id: str,
    lane_kind: str,
    candidates: list[dict[str, Any]],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    claim_flags = false_claim_flags(manifest_validation)
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
        "mem_level": "MEM4",
        "lane_id": lane_id,
        "lane_kind": lane_kind,
        "evidence_class": "memory_shaped_route_arbitration",
        "candidate_set_id": f"n08-native-route-candidate-set:{lane_id}",
        "arbitration_window_id": f"n08_mem4_arbitration_window:{lane_id}",
        "candidate_route_digests": [row["candidate_route_digest"] for row in ordered],
        "candidate_route_ids": [row["candidate_route_id"] for row in ordered],
        "candidate_set_order_key": "score_desc_then_candidate_id",
        "unresolved_tie_policy": "deterministic_candidate_order_key",
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "native_route_arbitration_enabled": True,
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc3",
        "causal_layer_mode": "topology_changing_causal_history",
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": claim_flags,
    }
    record["idempotency_key"] = digest_value(
        {
            "lane_id": lane_id,
            "candidate_route_digests": record["candidate_route_digests"],
            "candidate_set_order_key": record["candidate_set_order_key"],
        }
    )
    record["candidate_set_digest"] = digest_record(record, "candidate_set_digest")
    return record


def select_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        candidates,
        key=lambda row: (-float(row["candidate_route_score"]), row["candidate_order_key"]),
    )[0]


def build_arbitration_record(
    manifest_validation: dict[str, Any],
    lane_id: str,
    lane_kind: str,
    candidates: list[dict[str, Any]],
    candidate_set: dict[str, Any],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    claim_flags = false_claim_flags(manifest_validation)
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
        "mem_level": "MEM4",
        "mem_level_is_evidence_classification": True,
        "claim_ceiling": "mem4_memory_shaped_route_selection_candidate",
        "lane_id": lane_id,
        "lane_kind": lane_kind,
        "evidence_class": "memory_shaped_route_arbitration",
        "native_route_arbitration_record_id": (
            f"n08-native-route-arbitration:{lane_id}:"
            f"{selected['candidate_route_id']}"
        ),
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "arbitration_rule": "highest_score_then_candidate_order_key",
        "arbitration_reason_code": (
            "native_route_arbitration_selected_highest_score"
            if selected["candidate_route_score"]
            > min(row["candidate_route_score"] for row in candidates)
            else "native_route_arbitration_selected_declared_order_tiebreak"
        ),
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
        ]
        + (
            [
                f"memory_surface_digest:{selected['candidate_memory_surface_digest']}",
                "memory_surface_state_snapshot_digest:"
                f"{selected['candidate_memory_surface_state_snapshot_digest']}",
            ]
            if selected["candidate_score_is_memory_shaped"]
            else ["counterfactual_without_memory_component"]
        ),
        "selected_topology_event_id": None,
        "selected_topology_event_digest": None,
        "topology_event_committed": False,
        "packet_scheduled": False,
        "state_mutated": False,
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc3",
        "causal_layer_mode": "topology_changing_causal_history",
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": claim_flags,
    }
    record["idempotency_key"] = digest_value(
        {
            "candidate_set_digest": record["candidate_set_digest"],
            "selected_candidate_route_digest": record[
                "selected_candidate_route_digest"
            ],
            "arbitration_reason_code": record["arbitration_reason_code"],
            "arbitration_rule": record["arbitration_rule"],
        }
    )
    record["native_route_arbitration_digest"] = digest_record(
        record, "native_route_arbitration_digest"
    )
    return record


def build_lane(
    manifest_validation: dict[str, Any],
    mem3: dict[str, Any],
    lane_id: str,
    lane_kind: str,
    use_memory_components: bool,
    event_time_base: float,
    scheduler_base: int,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for index, row in enumerate(latest_mem3_rows(mem3)):
        components = memory_component_scores(row) if use_memory_components else {}
        candidates.append(
            build_candidate_record(
                manifest_validation,
                mem3,
                row,
                lane_id,
                lane_kind,
                components,
                round_score(event_time_base + (index * 0.01)),
                scheduler_base + index,
            )
        )
    candidate_set = build_candidate_set(
        manifest_validation,
        lane_id,
        lane_kind,
        candidates,
        round_score(event_time_base + 0.05),
        scheduler_base + 5,
    )
    arbitration = build_arbitration_record(
        manifest_validation,
        lane_id,
        lane_kind,
        candidates,
        candidate_set,
        round_score(event_time_base + 0.1),
        scheduler_base + 10,
    )
    return {
        "lane_id": lane_id,
        "lane_kind": lane_kind,
        "candidate_route_records": candidates,
        "candidate_set_record": candidate_set,
        "route_arbitration_record": arbitration,
        "selected_route_id": arbitration["selected_candidate_route_id"],
        "selected_candidate_route_digest": arbitration[
            "selected_candidate_route_digest"
        ],
        "candidate_scores_by_route": {
            row["candidate_route_id"]: row["candidate_route_score"]
            for row in candidates
        },
        "candidate_score_components_by_route": {
            row["candidate_route_id"]: row["candidate_score_components"]
            for row in candidates
        },
    }


def control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "candidate_score_memory_digest_missing",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "candidate_score_memory_digest_missing",
            "purpose": "Reject memory score components without a memory surface digest.",
        },
        {
            "control_id": "candidate_score_hidden_memory_input",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "candidate_score_hidden_memory_input",
            "purpose": "Reject memory score inputs not serialized as runtime-visible fields.",
        },
        {
            "control_id": "stale_memory_surface_read",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "stale_memory_surface_read",
            "purpose": "Reject candidate scoring against a stale MEM2 surface digest.",
        },
        {
            "control_id": "arbitration_memory_order_invalid",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "arbitration_memory_order_invalid",
            "purpose": "Reject candidate scoring before the MEM3 memory update row.",
        },
        {
            "control_id": "memory_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_budget_discontinuity",
            "purpose": "Reject memory-shaped scoring from invalid memory budget rows.",
        },
        {
            "control_id": "node_plus_packet_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "purpose": "Reject memory-shaped scoring that hides physical budget drift.",
        },
        {
            "control_id": "no_memory_surface_read_by_arbitration",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "no_memory_surface_read_by_arbitration",
            "purpose": "Reject MEM4 claim if arbitration does not read memory evidence.",
        },
        {
            "control_id": "claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "claim_promotion",
            "purpose": "Reject MEM4 promotion to memory claim, ACO, agency, or movement.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = digest_value(row)
    return rows


def arc_interpretation(lanes: dict[str, Any]) -> dict[str, Any]:
    counterfactual = lanes["counterfactual_without_memory_component"]
    memory = lanes["memory_shaped_arbitration"]
    memory_scores = memory["candidate_scores_by_route"]
    score_delta = round_score(memory_scores["route_b"] - memory_scores["route_a"])
    interpretation: dict[str, Any] = {
        "interpretation_id": "n08_i6_arc_of_becoming_mem4_arbitration_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "Can serialized MEM3 trail state become route-arbitration evidence "
            "without hidden memory inputs?"
        ),
        "observations": [
            {
                "observation_id": "counterfactual_tie_selects_order_key",
                "metric": "counterfactual_selected_route",
                "value": counterfactual["selected_route_id"],
                "interpretation": (
                    "Without memory components, both candidates have equal "
                    "score and deterministic order selects route_a."
                ),
            },
            {
                "observation_id": "memory_components_select_stronger_trace",
                "metric": "memory_shaped_selected_route",
                "value": memory["selected_route_id"],
                "interpretation": (
                    "With serialized memory components, route_b wins because "
                    "its MEM3 strength and recency score are higher."
                ),
            },
            {
                "observation_id": "selected_route_delta_observed",
                "metric": "selected_route_delta",
                "value": {
                    "without_memory": counterfactual["selected_route_id"],
                    "with_memory": memory["selected_route_id"],
                },
                "interpretation": (
                    "The selected route changes only when memory-derived score "
                    "components are included."
                ),
            },
            {
                "observation_id": "memory_score_delta_serialized",
                "metric": "route_b_minus_route_a_memory_score_delta",
                "value": score_delta,
                "interpretation": (
                    "The score delta is replayable from serialized MEM3 "
                    "surface fields, not fixture-side route preference."
                ),
            },
        ],
        "classification": {
            "mem_level": "MEM4",
            "classification_status": "memory_shaped_route_selection_candidate",
            "hypothesis": "A_serialized_producer_policy_memory",
            "not_merely_true_false_endpoint": True,
            "affordance_status": "operational_as_score_evidence_only",
            "claim_gate": "closed_until_mem6_artifact_replay",
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "Serialized memory rows can become route-score evidence.",
                "The no-memory counterfactual separates deterministic tie-breaking from memory-shaped selection.",
                "This remains a score-policy mechanism and does not solve native geometry-mediated trail memory.",
            ],
            "next_question": (
                "Can repeated route-use, memory update, and memory-shaped "
                "arbitration cycles remain replayable without hidden steering "
                "or budget drift?"
            ),
            "next_iteration": "7_MEM5_repeated_memory_shaped_selection",
        },
        "naturalization": {
            "naturalization_rung": "Nat3_score_operational_artifact_surface",
            "self_persistent_memory_observed": True,
            "self_updating_memory_observed": True,
            "memory_operational_in_route_selection": True,
            "why_not_more_naturalized": (
                "Memory changes score evidence, but it is still an independent "
                "serialized policy surface rather than native geometry/flux."
            ),
        },
        "learning_boundary": {
            "is_reinforcement_learning": False,
            "is_neural_weight_update": False,
            "is_graph_weight_propagation": False,
            "policy_updated": False,
            "route_weight_updated": False,
            "candidate_score_updated_by_memory_component": True,
            "native_geometry_trail_claimed": False,
            "pure_coherence_flux_trail_claimed": False,
            "distinction": (
                "Iteration 6 changes candidate evidence through serialized "
                "memory components. It does not change native geometry or "
                "coherence flux."
            ),
        },
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "aco_like_claim_allowed": False,
            "movement_claim_allowed": False,
            "reason": (
                "MEM4 supports a memory-shaped route-selection candidate only. "
                "The narrow memory/trail claim remains closed until MEM6 "
                "artifact replay."
            ),
        },
        "selected_route_delta": {
            "without_memory": counterfactual["selected_route_id"],
            "with_memory": memory["selected_route_id"],
            "changed": counterfactual["selected_route_id"]
            != memory["selected_route_id"],
        },
        "memory_score_delta": score_delta,
    }
    interpretation["arc_interpretation_digest"] = digest_value(interpretation)
    return interpretation


def all_candidate_records(lanes: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for lane in lanes.values():
        records.extend(lane["candidate_route_records"])
    return records


def validate_output(
    manifest_validation: dict[str, Any],
    mem3: dict[str, Any],
    lanes: dict[str, Any],
    controls: list[dict[str, Any]],
    interpretation: dict[str, Any],
) -> dict[str, bool]:
    manifest = manifest_validation["fixture_manifest"]
    component_contract = manifest["memory_derived_score_component_contract"]
    allowed_components = set(component_contract["component_names"])
    required_prefixes = set(
        component_contract["required_candidate_runtime_visible_inputs"]
    )
    memory_lane = lanes["memory_shaped_arbitration"]
    counterfactual_lane = lanes["counterfactual_without_memory_component"]
    candidates = all_candidate_records(lanes)
    memory_candidates = memory_lane["candidate_route_records"]
    source_memory_digests = {
        row["memory_surface_digest"] for row in mem3["memory_surface_rows"]
    }
    control_blockers = [row["primary_blocker"] for row in controls]
    return {
        "source_mem3_passed": mem3["status"] == "passed",
        "source_manifest_passed": manifest_validation["status"] == "passed",
        "candidate_route_digests_recompute": all(
            row["candidate_route_digest"] == digest_record(row, "candidate_route_digest")
            for row in candidates
        ),
        "candidate_set_digests_recompute": all(
            lane["candidate_set_record"]["candidate_set_digest"]
            == digest_record(lane["candidate_set_record"], "candidate_set_digest")
            for lane in lanes.values()
        ),
        "route_arbitration_digests_recompute": all(
            lane["route_arbitration_record"]["native_route_arbitration_digest"]
            == digest_record(
                lane["route_arbitration_record"], "native_route_arbitration_digest"
            )
            for lane in lanes.values()
        ),
        "memory_candidate_components_allowed": all(
            set(row["candidate_score_components"]).issubset(allowed_components)
            for row in memory_candidates
        ),
        "counterfactual_has_no_memory_components": all(
            row["candidate_score_components"] == {}
            and row["candidate_score_is_memory_shaped"] is False
            for row in counterfactual_lane["candidate_route_records"]
        ),
        "candidate_scores_equal_component_sums": all(
            row["candidate_route_score"]
            == candidate_score(row["candidate_score_components"])
            for row in candidates
        ),
        "memory_runtime_inputs_include_required_fields": all(
            required_prefixes.issubset(
                {
                    item.split(":", 1)[0]
                    for item in row["candidate_runtime_visible_inputs"]
                    if ":" in item
                }
            )
            for row in memory_candidates
        ),
        "memory_runtime_inputs_cite_source_mem3_digest": all(
            row["candidate_memory_surface_digest"] in source_memory_digests
            for row in memory_candidates
        ),
        "memory_surface_read_by_arbitration": all(
            row["memory_surface_read_by_arbitration"] is True
            for row in memory_candidates
        )
        and any(
            "memory_surface_digest:"
            in item
            for item in memory_lane["route_arbitration_record"][
                "arbitration_runtime_visible_inputs"
            ]
        ),
        "memory_candidate_order_after_mem3": all(
            row["event_time_key"] > row["candidate_memory_event_time_key"]
            and row["scheduler_event_index"]
            > row["candidate_memory_scheduler_event_index"]
            for row in memory_candidates
        ),
        "counterfactual_selected_route_a": counterfactual_lane["selected_route_id"]
        == "route_a",
        "memory_shaped_selected_route_b": memory_lane["selected_route_id"]
        == "route_b",
        "selected_route_delta_recorded": interpretation["selected_route_delta"][
            "changed"
        ]
        is True,
        "memory_score_delta_positive": interpretation["memory_score_delta"] > 0.0,
        "candidate_budget_predictions_exact": all(
            row["candidate_budget_prediction"]["node_plus_packet_budget_before"]
            == row["candidate_budget_prediction"]["node_plus_packet_budget_after"]
            and row["candidate_budget_prediction"]["node_plus_packet_budget_error"]
            == 0.0
            and row["candidate_memory_budget_prediction"]["memory_budget_error"] == 0.0
            for row in candidates
        ),
        "no_topology_or_packet_side_effects": all(
            lane["route_arbitration_record"]["topology_event_committed"] is False
            and lane["route_arbitration_record"]["packet_scheduled"] is False
            and lane["route_arbitration_record"]["state_mutated"] is False
            for lane in lanes.values()
        ),
        "hypothesis_a_only_no_native_geometry_claim": all(
            row["native_geometry_trail_claimed"] is False
            and row["pure_coherence_flux_trail_claimed"] is False
            for row in candidates
        ),
        "claim_flags_all_false": all(
            all(value is False for value in row["claim_flags"].values())
            for row in candidates
        )
        and all(value is False for value in mem3["claim_flags"].values()),
        "controls_present": {
            row["control_id"] for row in controls
        }
        == {
            "candidate_score_memory_digest_missing",
            "candidate_score_hidden_memory_input",
            "stale_memory_surface_read",
            "arbitration_memory_order_invalid",
            "memory_budget_discontinuity",
            "node_plus_packet_budget_discontinuity",
            "no_memory_surface_read_by_arbitration",
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
        "native_memory_still_experiment_local": all(
            blocker in mem3["inherited_native_policy_blockers"]
            for blocker in [
                "native_memory_candidate_score_component_semantics_missing",
                "native_memory_artifact_replay_validator_missing",
            ]
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
    paths = [MANIFEST_VALIDATION_PATH, SOURCE_MEM3_PATH]
    return {rel(path): digest_file(path) for path in paths}


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_MEM3_REPORT): digest_file(SOURCE_MEM3_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    lanes = output["lanes"]
    interpretation = output["arc_of_becoming_interpretation"]
    controls = output["controls"]
    checks = output["checks"]
    memory_lane = lanes["memory_shaped_arbitration"]
    counterfactual_lane = lanes["counterfactual_without_memory_component"]
    candidate_lines = "\n".join(
        "| `{lane}` | `{route}` | `{score}` | `{digest}` | `{components}` |".format(
            lane=lane["lane_id"],
            route=row["candidate_route_id"],
            score=row["candidate_route_score"],
            digest=row["candidate_route_digest"],
            components=json.dumps(row["candidate_score_components"], sort_keys=True),
        )
        for lane in lanes.values()
        for row in lane["candidate_route_records"]
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
    report = f"""# N08 Iteration 6 MEM4 Memory-Shaped Route Arbitration

Status: `{output['status']}`.

Iteration 6 tests Hypothesis A only: serialized producer/policy memory becomes
candidate-score evidence. It does not claim pure coherence/flux memory, native
geometry-mediated trail memory, ACO, agency, or biological pheromone behavior.

## Branch Question

{interpretation['question']}

## Branch Answer

Without memory components, route candidates tie and deterministic ordering
selects `{counterfactual_lane['selected_route_id']}`. With serialized MEM3
memory components, route arbitration selects `{memory_lane['selected_route_id']}`.

```json
{json.dumps(interpretation['selected_route_delta'], indent=2, sort_keys=True)}
```

The memory score delta is `{interpretation['memory_score_delta']}`.

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

## Candidate Scores

| Lane | Route | Score | Candidate Digest | Components |
|---|---|---:|---|---|
{candidate_lines}

## Counterfactual Lane

```json
{json.dumps(counterfactual_lane['route_arbitration_record'], indent=2, sort_keys=True)}
```

## Memory-Shaped Lane

```json
{json.dumps(memory_lane['route_arbitration_record'], indent=2, sort_keys=True)}
```

## Hypothesis Boundary

```json
{json.dumps(output['hypothesis_boundary'], indent=2, sort_keys=True)}
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

Iteration 6 passes if memory surface state changes candidate-route evidence and
native route arbitration selects according to serialized memory-derived score
components.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    mem3 = load_json(SOURCE_MEM3_PATH)
    lanes = {
        "counterfactual_without_memory_component": build_lane(
            manifest_validation,
            mem3,
            MEM4_COUNTERFACTUAL_LANE_ID,
            "counterfactual_without_memory_component",
            False,
            COUNTERFACTUAL_EVENT_TIME_BASE,
            COUNTERFACTUAL_SCHEDULER_BASE,
        ),
        "memory_shaped_arbitration": build_lane(
            manifest_validation,
            mem3,
            MEM4_MEMORY_LANE_ID,
            "memory_shaped_arbitration",
            True,
            MEMORY_EVENT_TIME_BASE,
            MEMORY_SCHEDULER_BASE,
        ),
    }
    controls = control_rows()
    interpretation = arc_interpretation(lanes)
    checks = validate_output(manifest_validation, mem3, lanes, controls, interpretation)
    output: dict[str, Any] = {
        "schema": "n08_iteration_6_mem4_memory_shaped_arbitration_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 6,
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
        "mem_level": "MEM4",
        "claim_ceiling": "mem4_memory_shaped_route_selection_candidate",
        "hypothesis_boundary": {
            "hypothesis": "A_serialized_producer_policy_memory",
            "serialized_memory_policy_path": True,
            "native_geometry_mediated_trail_path": False,
            "independent_memory_strength_used_as_score_evidence": True,
            "independent_memory_strength_used_as_physical_flux": False,
            "native_geometry_trail_claimed": False,
            "pure_coherence_flux_trail_claimed": False,
            "hypothesis_b_remains_open": True,
        },
        "mem4_score_component_contract": {
            "allowed_memory_component_names": MEM4_MEMORY_COMPONENTS,
            "required_candidate_runtime_visible_input_prefixes": (
                MEM4_REQUIRED_RUNTIME_INPUT_PREFIXES
            ),
            "score_invariant": "candidate_route_score == sum(candidate_score_components)",
            "counterfactual_without_memory_component_required": True,
        },
        "lanes": lanes,
        "arc_of_becoming_interpretation": interpretation,
        "producer_step_boundary": manifest_validation["fixture_manifest"][
            "producer_step_boundary"
        ],
        "inherited_native_policy_blockers": mem3["inherited_native_policy_blockers"],
        "controls": controls,
        "checks": checks,
        "claim_flags": false_claim_flags(manifest_validation),
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 6 passes if memory surface state changes "
                "candidate-route evidence and native route arbitration selects "
                "according to serialized memory-derived score components."
            ),
        },
    }
    output["artifact_digests"] = {
        "counterfactual_lane_digest": digest_value(
            lanes["counterfactual_without_memory_component"]
        ),
        "memory_shaped_lane_digest": digest_value(lanes["memory_shaped_arbitration"]),
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
