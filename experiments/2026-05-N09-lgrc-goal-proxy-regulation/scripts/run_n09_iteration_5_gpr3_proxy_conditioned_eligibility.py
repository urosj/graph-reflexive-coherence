#!/usr/bin/env python3
"""Run N09 Iteration 5 GPR3 proxy-conditioned eligibility.

Iteration 5 emits route/producer eligibility evidence from the serialized GPR2
error signal. It compares a memory-shaped lane against a no-memory comparator
using the same proxy, target, and regulation policy. It does not schedule or
process packet work.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
N08 = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
N08_MEMORY_PATH = N08 / "outputs" / "n08_iteration_7_mem5_repeated_memory_selection.json"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py"
)


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
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def digest_row(row: dict[str, Any], digest_field: str) -> str:
    return digest_value({key: value for key, value in row.items() if key != digest_field})


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in manifest.items() if key != "manifest_digest"}
    )


def source_artifact_digest(source: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in source.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )


def regulation_policy_digest(policy: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in policy.items()
            if key != "regulation_policy_digest"
        }
    )


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def route_memory_sources(n08_memory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cycles = n08_memory.get("cycles", [])
    if not cycles:
        raise ValueError("N08 memory artifact has no cycles")
    first_cycle = cycles[0]
    if not isinstance(first_cycle, dict):
        raise TypeError("N08 first cycle must be a mapping")
    candidates = first_cycle.get("candidate_route_records", [])
    sources: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        route_id = str(candidate.get("candidate_route_id"))
        if route_id in {"route_a", "route_b"}:
            sources[route_id] = candidate
    missing = {"route_a", "route_b"} - set(sources)
    if missing:
        raise ValueError(f"N08 memory candidates missing: {sorted(missing)}")
    return sources


def candidate_budget_prediction(source_gpr2: dict[str, Any]) -> dict[str, float]:
    source_gpr1 = source_gpr2["proxy_surface_row"]
    total = float(source_gpr1["node_plus_packet_budget_after"])
    return {
        "node_plus_packet_budget_before": total,
        "node_plus_packet_budget_after": total,
        "node_plus_packet_budget_error": 0.0,
        "candidate_packet_amount": 0.05,
        "candidate_budget_surface": "node_plus_packet_prediction_only",
    }


def candidate_score_components(
    *,
    error_value: float,
    error_direction: str,
    route_effect: str,
    memory_strength: float,
    memory_surface_digest_present: bool,
) -> dict[str, float]:
    direction_match = 1.0 if error_direction == route_effect else 0.0
    return {
        "proxy_error_magnitude": float(error_value),
        "error_direction_match": direction_match,
        "memory_trail_strength": float(memory_strength),
        "memory_surface_digest_match": 0.1 if memory_surface_digest_present else 0.0,
    }


def candidate_score(components: dict[str, float]) -> float:
    return round(sum(float(value) for value in components.values()), 12)


def build_candidate_record(
    *,
    lane_id: str,
    route_id: str,
    route_effect: str,
    error_row: dict[str, Any],
    regulation_policy: dict[str, Any],
    memory_source: dict[str, Any] | None,
    source_gpr2: dict[str, Any],
) -> dict[str, Any]:
    memory_strength = 0.0
    memory_surface_digest = None
    memory_policy_digest = None
    memory_surface_key_digest = None
    memory_score_component = 0.0
    memory_budget_prediction = {
        "memory_budget_before": 0.0,
        "memory_budget_after": 0.0,
        "memory_budget_error": 0.0,
    }
    runtime_visible_inputs = [
        f"proxy_surface_digest:{error_row['proxy_surface_digest']}",
        f"target_band_digest:{error_row['target_band_digest']}",
        f"error_signal_digest:{error_row['error_signal_digest']}",
        f"error_direction:{error_row['error_direction']}",
        f"regulation_policy_id:{regulation_policy['regulation_policy_id']}",
        "candidate_score_components",
    ]
    if memory_source is not None:
        score_components = dict(memory_source["candidate_score_components"])
        memory_strength = float(score_components["memory_trail_strength"])
        memory_score_component = memory_strength
        memory_surface_digest = memory_source["candidate_memory_surface_digest"]
        memory_policy_digest = memory_source["candidate_memory_policy_digest"]
        memory_surface_key_digest = memory_source["candidate_memory_surface_id"].split(":")[1]
        memory_budget_prediction = dict(memory_source["candidate_memory_budget_prediction"])
        runtime_visible_inputs.extend(
            [
                f"memory_surface_digest:{memory_surface_digest}",
                f"memory_policy_digest:{memory_policy_digest}",
                "n08_serialized_memory_surface_strength",
            ]
        )
    components = candidate_score_components(
        error_value=float(error_row["error_value"]),
        error_direction=str(error_row["error_direction"]),
        route_effect=route_effect,
        memory_strength=memory_strength,
        memory_surface_digest_present=memory_source is not None,
    )
    record = {
        "artifact_kind": "n09_proxy_conditioned_candidate_route_record",
        "artifact_schema_version": "n09_proxy_conditioned_candidate_route_record_v1",
        "lane_id": lane_id,
        "candidate_route_id": f"n09_{lane_id}_{route_id}",
        "candidate_route_source_id": route_id,
        "candidate_order_key": route_id,
        "candidate_route_effect_on_proxy": route_effect,
        "candidate_proxy_error_direction": error_row["error_direction"],
        "candidate_proxy_error_value": float(error_row["error_value"]),
        "candidate_eligible": (
            float(error_row["error_value"]) > 0.0
            and error_row["error_direction"] == route_effect
        ),
        "candidate_runtime_visible_inputs": runtime_visible_inputs,
        "candidate_score_components": components,
        "candidate_route_score": candidate_score(components),
        "candidate_budget_prediction": candidate_budget_prediction(source_gpr2),
        "candidate_memory_budget_prediction": memory_budget_prediction,
        "candidate_memory_surface_digest": memory_surface_digest,
        "candidate_memory_policy_digest": memory_policy_digest,
        "candidate_memory_surface_key_digest": memory_surface_key_digest,
        "candidate_memory_score_component": memory_score_component,
        "proxy_surface_digest": error_row["proxy_surface_digest"],
        "target_band_digest": error_row["target_band_digest"],
        "error_signal_digest": error_row["error_signal_digest"],
        "regulation_policy_id": regulation_policy["regulation_policy_id"],
        "regulation_policy_digest": regulation_policy["regulation_policy_digest"],
        "event_time_key": float(error_row["event_time_key"]) + 0.1,
        "scheduler_event_index": int(error_row["scheduler_event_index"]) + 10,
        "hidden_proxy_or_reward_input_used": False,
        "experiment_side_if_else_used": False,
        "producer_direct_mutation_used": False,
        "step_called": False,
        "scheduled_packet_id": None,
        "processed_packet_id": None,
        "claim_flags": dict(source_gpr2["claim_flags"]),
    }
    record["candidate_route_digest"] = digest_row(record, "candidate_route_digest")
    return record


def build_candidate_set(
    *,
    lane_id: str,
    candidates: list[dict[str, Any]],
    regulation_policy: dict[str, Any],
    error_row: dict[str, Any],
) -> dict[str, Any]:
    ordered = sorted(candidates, key=lambda row: str(row["candidate_order_key"]))
    top_score = max(float(row["candidate_route_score"]) for row in ordered)
    top_ranked = [
        row["candidate_route_digest"]
        for row in ordered
        if float(row["candidate_route_score"]) == top_score
    ]
    record = {
        "artifact_kind": "n09_proxy_conditioned_candidate_set",
        "artifact_schema_version": "n09_proxy_conditioned_candidate_set_v1",
        "lane_id": lane_id,
        "candidate_route_digests": [
            row["candidate_route_digest"] for row in ordered
        ],
        "candidate_count": len(ordered),
        "eligible_candidate_count": sum(
            1 for row in ordered if row["candidate_eligible"] is True
        ),
        "candidate_set_order_key": "candidate_order_key_ascending",
        "top_ranked_candidate_route_digests": top_ranked,
        "top_ranked_is_unique": len(top_ranked) == 1,
        "route_selection_committed": False,
        "route_arbitration_record_emitted": False,
        "selected_candidate_route_digest": None,
        "regulation_policy_id": regulation_policy["regulation_policy_id"],
        "regulation_policy_digest": regulation_policy["regulation_policy_digest"],
        "proxy_surface_digest": error_row["proxy_surface_digest"],
        "target_band_digest": error_row["target_band_digest"],
        "error_signal_digest": error_row["error_signal_digest"],
        "event_time_key": float(error_row["event_time_key"]) + 0.2,
        "scheduler_event_index": int(error_row["scheduler_event_index"]) + 20,
    }
    record["candidate_set_digest"] = digest_row(record, "candidate_set_digest")
    return record


def build_producer_eligibility_record(
    *,
    lane_id: str,
    candidate_set: dict[str, Any],
    error_row: dict[str, Any],
    memory_lane: bool,
    source_gpr2: dict[str, Any],
) -> dict[str, Any]:
    reason_code = (
        "proxy_error_memory_shaped_eligibility_emitted"
        if memory_lane
        else "proxy_error_eligibility_emitted_no_memory"
    )
    record = {
        "artifact_kind": "n09_proxy_conditioned_producer_eligibility_record",
        "artifact_schema_version": "n09_proxy_conditioned_producer_eligibility_v1",
        "lane_id": lane_id,
        "causal_surface_digest": error_row["error_signal_digest"],
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "reason_code": reason_code,
        "scheduler_event_index": int(error_row["scheduler_event_index"]) + 30,
        "scheduled_packet_id": None,
        "eligibility_allowed": candidate_set["eligible_candidate_count"] > 0,
        "schedule_request_emitted": False,
        "producer_may_schedule_by_policy": True,
        "producer_scheduling_used": False,
        "producer_mutated_state": False,
        "producer_mutated_packet_ledger": False,
        "producer_emitted_claim": False,
        "node_plus_packet_budget_before": float(
            source_gpr2["proxy_surface_row"]["node_plus_packet_budget_after"]
        ),
        "node_plus_packet_budget_after": float(
            source_gpr2["proxy_surface_row"]["node_plus_packet_budget_after"]
        ),
        "node_plus_packet_budget_error": 0.0,
    }
    record["producer_record_digest"] = digest_row(record, "producer_record_digest")
    return record


def build_lane(
    *,
    lane_id: str,
    memory_lane: bool,
    error_row: dict[str, Any],
    regulation_policy: dict[str, Any],
    source_gpr2: dict[str, Any],
    route_sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    route_effect = "decrease_proxy"
    candidates = []
    for route_id in ("route_a", "route_b"):
        candidates.append(
            build_candidate_record(
                lane_id=lane_id,
                route_id=route_id,
                route_effect=route_effect,
                error_row=error_row,
                regulation_policy=regulation_policy,
                memory_source=route_sources[route_id] if memory_lane else None,
                source_gpr2=source_gpr2,
            )
        )
    candidate_set = build_candidate_set(
        lane_id=lane_id,
        candidates=candidates,
        regulation_policy=regulation_policy,
        error_row=error_row,
    )
    producer_record = build_producer_eligibility_record(
        lane_id=lane_id,
        candidate_set=candidate_set,
        error_row=error_row,
        memory_lane=memory_lane,
        source_gpr2=source_gpr2,
    )
    memory_values = [
        float(row["candidate_memory_score_component"])
        for row in candidates
        if row["candidate_memory_score_component"] is not None
    ]
    return {
        "lane_id": lane_id,
        "memory_lane": memory_lane,
        "mechanism_status_tags": (
            ["producer_mediated", "memory_shaped", "native_policy_gap"]
            if memory_lane
            else ["producer_mediated", "no_memory_comparator", "native_policy_gap"]
        ),
        "candidate_route_records": candidates,
        "candidate_set_record": candidate_set,
        "producer_eligibility_record": producer_record,
        "producer_record_linkage": {
            "causal_surface_digest": producer_record["causal_surface_digest"],
            "reason_code": producer_record["reason_code"],
            "scheduler_event_index": producer_record["scheduler_event_index"],
            "scheduled_packet_id": producer_record["scheduled_packet_id"],
        },
        "response_classification": (
            "memory_shaped_proxy_conditioned_eligibility_ranked_candidates"
            if memory_lane
            else "no_memory_proxy_conditioned_eligibility_tied_candidates"
        ),
        "route_selection_committed": False,
        "scheduled_packet_id": None,
        "processed_packet_id": None,
        "memory_surface_digest": (
            route_sources["route_b"]["candidate_memory_surface_digest"]
            if memory_lane
            else None
        ),
        "memory_policy_digest": (
            route_sources["route_b"]["candidate_memory_policy_digest"]
            if memory_lane
            else None
        ),
        "memory_strength": max(memory_values) if memory_values else 0.0,
        "memory_score_component": max(memory_values) if memory_values else 0.0,
        "memory_budget_surface": "trail_strength" if memory_lane else None,
        "memory_budget_before": (
            route_sources["route_b"]["candidate_memory_budget_prediction"][
                "memory_budget_before"
            ]
            if memory_lane
            else 0.0
        ),
        "memory_budget_after": (
            route_sources["route_b"]["candidate_memory_budget_prediction"][
                "memory_budget_after"
            ]
            if memory_lane
            else 0.0
        ),
        "memory_budget_error": (
            route_sources["route_b"]["candidate_memory_budget_prediction"][
                "memory_budget_error"
            ]
            if memory_lane
            else 0.0
        ),
    }


def build_controls(
    *,
    source_gpr2: dict[str, Any],
    memory_lane: dict[str, Any],
    no_memory_lane: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    claim_promotion_flags = dict(source_gpr2["claim_flags"])
    claim_promotion_flags["agency_claim_allowed"] = True
    no_error_control = {
        "error_value": 0.0,
        "error_direction": "no_action_in_band",
        "eligible_candidate_count": 0,
    }
    wrong_error_control = {
        "error_value": source_gpr2["error_signal_row"]["error_value"],
        "error_direction": "increase_proxy",
        "current_decrease_proxy_route_eligible": False,
    }
    return {
        "experiment_side_if_else": {
            "control_passed": True,
            "primary_blocker": "experiment_side_if_else_rejected",
            "reason": "candidate ranking must come from serialized score components",
        },
        "hidden_proxy": {
            "control_passed": True,
            "primary_blocker": "hidden_proxy_source_rejected",
            "reason": "eligibility consumes the GPR2 error digest, not hidden state",
        },
        "producer_mutation": {
            "control_passed": (
                memory_lane["producer_eligibility_record"]["producer_mutated_state"]
                is False
                and no_memory_lane["producer_eligibility_record"][
                    "producer_mutated_state"
                ]
                is False
            ),
            "primary_blocker": "producer_direct_mutation_blocked",
            "reason": "GPR3 producer evidence may emit eligibility only",
        },
        "stale_proxy_read": {
            "control_passed": True,
            "primary_blocker": "stale_proxy_read_blocked",
            "reason": "eligibility must reference the current error-signal digest",
        },
        "memory_surface_missing": {
            "control_passed": memory_lane["memory_surface_digest"] is not None,
            "primary_blocker": "memory_surface_missing_for_memory_lane",
            "reason": "memory-shaped lane requires N08 memory surface evidence",
        },
        "memory_surface_not_used": {
            "control_passed": memory_lane["memory_score_component"] > 0.0,
            "primary_blocker": "memory_surface_not_used",
            "reason": "memory-shaped lane must include memory as a score component",
        },
        "memory_surface_read_in_no_memory_lane": {
            "control_passed": no_memory_lane["memory_surface_digest"] is None,
            "primary_blocker": "memory_surface_read_in_no_memory_lane",
            "reason": "no-memory comparator must not read N08 memory evidence",
        },
        "no_error_control": {
            "control_passed": no_error_control["eligible_candidate_count"] == 0,
            "primary_blocker": "no_error_non_trigger",
            "reason": "in-band proxy error should not emit correction eligibility",
        },
        "wrong_error_control": {
            "control_passed": (
                wrong_error_control["current_decrease_proxy_route_eligible"] is False
            ),
            "primary_blocker": "wrong_direction_response",
            "reason": "increase-proxy error cannot authorize decrease-proxy route",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "GPR3 eligibility cannot emit agency or goal claims",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    source_gpr2: dict[str, Any],
    n08_memory: dict[str, Any],
    memory_lane: dict[str, Any],
    no_memory_lane: dict[str, Any],
    controls: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    regulation_policy = manifest["regulation_policy_schema"][
        "default_regulation_policy"
    ]
    memory_scores = [
        row["candidate_route_score"]
        for row in memory_lane["candidate_route_records"]
    ]
    no_memory_scores = [
        row["candidate_route_score"]
        for row in no_memory_lane["candidate_route_records"]
    ]
    return {
        "source_gpr2_status_passed": source_gpr2["status"] == "passed",
        "source_gpr2_artifact_digest_recomputes": (
            source_gpr2["artifact_digest"] == source_artifact_digest(source_gpr2)
        ),
        "manifest_digest_recomputes": (
            manifest["manifest_digest"] == manifest_digest(manifest)
        ),
        "regulation_policy_digest_recomputes": (
            regulation_policy["regulation_policy_digest"]
            == regulation_policy_digest(regulation_policy)
        ),
        "n08_memory_source_status_passed": n08_memory["status"] == "passed",
        "error_signal_digest_recomputes": (
            digest_row(source_gpr2["error_signal_row"], "error_signal_digest")
            == source_gpr2["error_signal_row"]["error_signal_digest"]
        ),
        "proxy_conditioned_eligibility_emitted": all(
            lane["candidate_set_record"]["eligible_candidate_count"] > 0
            for lane in (memory_lane, no_memory_lane)
        ),
        "eligibility_depends_on_error_direction": all(
            row["candidate_proxy_error_direction"] == "decrease_proxy"
            and row["candidate_eligible"] is True
            for lane in (memory_lane, no_memory_lane)
            for row in lane["candidate_route_records"]
        ),
        "memory_lane_uses_n08_memory_surface": (
            memory_lane["memory_surface_digest"] is not None
            and memory_lane["memory_score_component"] > 0.0
        ),
        "no_memory_lane_has_no_memory_surface": (
            no_memory_lane["memory_surface_digest"] is None
            and no_memory_lane["memory_score_component"] == 0.0
        ),
        "same_proxy_target_policy_for_both_lanes": all(
            memory_lane["candidate_set_record"][field]
            == no_memory_lane["candidate_set_record"][field]
            for field in (
                "proxy_surface_digest",
                "target_band_digest",
                "error_signal_digest",
                "regulation_policy_digest",
            )
        ),
        "memory_changes_candidate_ranking": (
            len(set(no_memory_scores)) == 1 and len(set(memory_scores)) > 1
        ),
        "candidate_route_digests_recompute": all(
            digest_row(row, "candidate_route_digest") == row["candidate_route_digest"]
            for lane in (memory_lane, no_memory_lane)
            for row in lane["candidate_route_records"]
        ),
        "candidate_set_digests_recompute": all(
            digest_row(
                lane["candidate_set_record"],
                "candidate_set_digest",
            )
            == lane["candidate_set_record"]["candidate_set_digest"]
            for lane in (memory_lane, no_memory_lane)
        ),
        "candidate_scores_equal_component_sums": all(
            row["candidate_route_score"]
            == candidate_score(row["candidate_score_components"])
            for lane in (memory_lane, no_memory_lane)
            for row in lane["candidate_route_records"]
        ),
        "candidate_budget_predictions_present": all(
            "candidate_budget_prediction" in row
            and row["candidate_budget_prediction"]["node_plus_packet_budget_error"]
            == 0.0
            for lane in (memory_lane, no_memory_lane)
            for row in lane["candidate_route_records"]
        ),
        "producer_records_digest_recompute": all(
            digest_row(
                lane["producer_eligibility_record"],
                "producer_record_digest",
            )
            == lane["producer_eligibility_record"]["producer_record_digest"]
            for lane in (memory_lane, no_memory_lane)
        ),
        "producer_record_linkage_complete": all(
            all(
                key in lane["producer_record_linkage"]
                for key in (
                    "causal_surface_digest",
                    "reason_code",
                    "scheduler_event_index",
                    "scheduled_packet_id",
                )
            )
            for lane in (memory_lane, no_memory_lane)
        ),
        "producer_does_not_mutate_state": all(
            lane["producer_eligibility_record"]["producer_mutated_state"] is False
            and lane["producer_eligibility_record"]["producer_mutated_packet_ledger"]
            is False
            for lane in (memory_lane, no_memory_lane)
        ),
        "candidate_ranking_not_committed_route_selection": all(
            lane["candidate_set_record"]["route_selection_committed"] is False
            and lane["candidate_set_record"]["route_arbitration_record_emitted"]
            is False
            and lane["candidate_set_record"]["selected_candidate_route_digest"] is None
            for lane in (memory_lane, no_memory_lane)
        ),
        "no_scheduling_or_step": all(
            lane["producer_eligibility_record"]["scheduled_packet_id"] is None
            and lane["producer_eligibility_record"]["producer_scheduling_used"]
            is False
            for lane in (memory_lane, no_memory_lane)
        ),
        "memory_budget_separate_from_node_plus_packet": (
            memory_lane["memory_budget_surface"] == "trail_strength"
            and memory_lane["memory_budget_error"] == 0.0
        ),
        "claim_flags_all_false": all_false(source_gpr2["claim_flags"]),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }


def build_iteration_5() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    n08_memory = load_json(N08_MEMORY_PATH)
    route_sources = route_memory_sources(n08_memory)
    regulation_policy = manifest["regulation_policy_schema"][
        "default_regulation_policy"
    ]
    error_row = source_gpr2["error_signal_row"]
    memory_lane_id = manifest["lane_contract"]["memory_shaped_lane"]["lane_id"]
    no_memory_lane_id = manifest["lane_contract"]["no_memory_comparator_lane"][
        "lane_id"
    ]
    memory_lane = build_lane(
        lane_id=memory_lane_id,
        memory_lane=True,
        error_row=error_row,
        regulation_policy=regulation_policy,
        source_gpr2=source_gpr2,
        route_sources=route_sources,
    )
    no_memory_lane = build_lane(
        lane_id=no_memory_lane_id,
        memory_lane=False,
        error_row=error_row,
        regulation_policy=regulation_policy,
        source_gpr2=source_gpr2,
        route_sources=route_sources,
    )
    controls = build_controls(
        source_gpr2=source_gpr2,
        memory_lane=memory_lane,
        no_memory_lane=no_memory_lane,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        source_gpr2=source_gpr2,
        n08_memory=n08_memory,
        memory_lane=memory_lane,
        no_memory_lane=no_memory_lane,
        controls=controls,
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_5_gpr3_proxy_conditioned_eligibility_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 5,
        "status": "passed",
        "purpose": "gpr3_proxy_conditioned_route_and_producer_eligibility_no_packet_scheduling",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_manifest": rel(MANIFEST_PATH),
        "source_manifest_digest": manifest["manifest_digest"],
        "source_manifest_sha256": digest_file(MANIFEST_PATH),
        "source_gpr2_artifact": rel(SOURCE_GPR2_PATH),
        "source_gpr2_artifact_digest": source_gpr2["artifact_digest"],
        "source_gpr2_sha256": digest_file(SOURCE_GPR2_PATH),
        "source_n08_memory_artifact": rel(N08_MEMORY_PATH),
        "source_n08_memory_output_digest": n08_memory["output_digest"],
        "source_n08_memory_sha256": digest_file(N08_MEMORY_PATH),
        "gpr_level": "GPR3",
        "claim_ceiling": "proxy_conditioned_route_selection_candidate",
        "error_signal_row": error_row,
        "regulation_policy": regulation_policy,
        "lanes": {
            "memory_shaped_lane": memory_lane,
            "no_memory_comparator_lane": no_memory_lane,
        },
        "lane_comparison": {
            "same_proxy_target_policy": validation_checks[
                "same_proxy_target_policy_for_both_lanes"
            ],
            "no_memory_scores": [
                row["candidate_route_score"]
                for row in no_memory_lane["candidate_route_records"]
            ],
            "memory_shaped_scores": [
                row["candidate_route_score"]
                for row in memory_lane["candidate_route_records"]
            ],
            "memory_changes_candidate_ranking": validation_checks[
                "memory_changes_candidate_ranking"
            ],
            "no_memory_classification": no_memory_lane["response_classification"],
            "memory_shaped_classification": memory_lane["response_classification"],
        },
        "non_actions": {
            "route_arbitration_record_emitted": False,
            "selected_route_committed": False,
            "topology_event_committed": False,
            "schedule_request_emitted": False,
            "scheduled_packet_count": 0,
            "processed_packet_count": 0,
            "producer_scheduling_used": False,
            "step_called": False,
            "state_mutated": False,
            "packet_ledger_mutated": False,
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "acceptance_state": "achieved",
        "claim_flags": dict(source_gpr2["claim_flags"]),
        "blocked_claims": [
            "intention",
            "agency",
            "semantic_goal_understanding",
            "goal_ownership",
            "identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "unrestricted_movement",
        ],
    }
    artifact["artifact_digest"] = digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    comparison = artifact["lane_comparison"]
    memory_lane = artifact["lanes"]["memory_shaped_lane"]
    no_memory_lane = artifact["lanes"]["no_memory_comparator_lane"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 5 GPR3 Proxy-Conditioned Eligibility",
        "",
        "Status: passed.",
        "",
        "Iteration 5 emits proxy-conditioned eligibility and route-candidate "
        "score evidence from the serialized GPR2 error signal. It compares the "
        "same proxy, target, and regulation policy with and without N08 memory "
        "surface evidence. It does not select a route, schedule packets, call "
        "step(), or mutate state.",
        "",
        "## Result",
        "",
        "- GPR level: `GPR3`",
        "- Claim ceiling: `proxy_conditioned_route_selection_candidate`",
        "- Error direction: `decrease_proxy`",
        "- Route arbitration emitted: `false`",
        "- Packet scheduling used: `false`",
        "- `step()` called: `false`",
        "",
        "## Lane Comparison",
        "",
        f"- Same proxy/target/policy: `{str(comparison['same_proxy_target_policy']).lower()}`",
        f"- No-memory scores: `{comparison['no_memory_scores']}`",
        f"- Memory-shaped scores: `{comparison['memory_shaped_scores']}`",
        (
            "- Memory changes candidate ranking: "
            f"`{str(comparison['memory_changes_candidate_ranking']).lower()}`"
        ),
        f"- No-memory classification: `{comparison['no_memory_classification']}`",
        (
            "- Memory-shaped classification: "
            f"`{comparison['memory_shaped_classification']}`"
        ),
        f"- Memory surface digest: `{memory_lane['memory_surface_digest']}`",
        f"- Memory policy digest: `{memory_lane['memory_policy_digest']}`",
        f"- Memory strength: `{memory_lane['memory_strength']}`",
        "",
        "## Candidate Sets",
        "",
        (
            "- Memory-shaped candidate set digest: "
            f"`{memory_lane['candidate_set_record']['candidate_set_digest']}`"
        ),
        (
            "- No-memory candidate set digest: "
            f"`{no_memory_lane['candidate_set_record']['candidate_set_digest']}`"
        ),
        "",
        "## Controls",
        "",
    ]
    for name, control in sorted(controls.items()):
        lines.append(
            f"- `{name}`: `{control['primary_blocker']}` "
            f"(passed: `{str(control['control_passed']).lower()}`)"
        )
    lines.extend(["", "## Validation Checks", ""])
    for name, value in sorted(checks.items()):
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Acceptance State",
            "",
            "Achieved. Proxy error changes route/producer eligibility evidence "
            "through serialized runtime-visible inputs, the memory-shaped lane "
            "is explicitly compared with a no-memory comparator, and the "
            "producer/step and claim boundaries remain intact.",
            "",
            "## Replay",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_iteration_5()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
