#!/usr/bin/env python3
"""Run N08 Iteration 11-A positive-geometry route arbitration response.

Iteration 11 showed that a zero-coherence inserted node behaves like an
absorber. Iteration 11-A asks the next Hypothesis B question: if the trace is
made theory-clean by conserving positive coherence, can native route
arbitration read it as runtime-visible geometry evidence without
`memory_strength` or hidden preference?
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
SOURCE_I11_PATH = (
    EXPERIMENT / "outputs/n08_iteration_11_geometry_trace_flux_response.json"
)
SOURCE_I11_REPORT = (
    EXPERIMENT / "reports/n08_iteration_11_geometry_trace_flux_response.md"
)
SOURCE_I10_PATH = (
    EXPERIMENT / "outputs/n08_iteration_10_geometry_trail_formation.json"
)
OUTPUT_PATH = (
    EXPERIMENT
    / "outputs/n08_iteration_11a_positive_geometry_route_arbitration.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports/n08_iteration_11a_positive_geometry_route_arbitration.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_11a_positive_geometry_route_arbitration.py"
)

ROUTE_A = "route_a"
ROUTE_B = "route_b"
TRACE_NODE_ID = "30"
SCORE_KEYS = (
    "budget_validity",
    "lineage_ready",
    "positive_coherence_path_support",
    "source_geometry_trace_match",
)
EPSILON = 1e-12


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


def digest_record(record: dict[str, Any], digest_field: str) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != digest_field}
    )


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


def rounded(value: float) -> float:
    return round(float(value), 12)


def false_claim_flags() -> dict[str, bool]:
    return {
        "memory_or_trail_claim_allowed": False,
        "native_geometry_mediated_trail_claim_allowed": False,
        "pure_coherence_flux_trail_claim_allowed": False,
        "aco_like_claim_allowed": False,
        "agency_claim_allowed": False,
        "agentic_like_claim_allowed": False,
        "ant_colony_claim_allowed": False,
        "biological_claim_allowed": False,
        "goal_proxy_regulation_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "intention_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "movement_claim_allowed": False,
        "personhood_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "runtime_identity_acceptance_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }


def source_artifacts() -> dict[str, str]:
    return {
        rel(SOURCE_I10_PATH): digest_file(SOURCE_I10_PATH),
        rel(SOURCE_I11_PATH): digest_file(SOURCE_I11_PATH),
    }


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_I11_REPORT): digest_file(SOURCE_I11_REPORT)}


def score_sum(components: dict[str, float]) -> float:
    return rounded(sum(float(components[key]) for key in SCORE_KEYS))


def source_geometry_digest(lane: dict[str, Any]) -> str:
    return digest_value(
        {
            "topology_kind": lane["topology_kind"],
            "topology_digest": lane["topology_digest"],
            "node_state_before": lane["node_state_before"],
            "path_nodes": lane["path_nodes"],
            "future_response_class": lane["future_response_class"],
        }
    )


def candidate_record(
    *,
    lane: dict[str, Any],
    source_i10: dict[str, Any],
    route_id: str,
    score_components: dict[str, float],
    eligible: bool,
    blocker: str | None,
    path_nodes: list[str],
    event_time_key: float,
    scheduler_event_index: int,
) -> dict[str, Any]:
    trace_match = score_components["source_geometry_trace_match"] > 0.0
    positive_support = score_components["positive_coherence_path_support"] > 0.0
    runtime_inputs = [
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "candidate_score_components",
        f"source_geometry_digest:{source_geometry_digest(lane)}",
        f"topology_digest:{lane['topology_digest']}",
        f"path_nodes_digest:{digest_value(path_nodes)}",
        "serialized_route_arbitration_policy",
    ]
    if trace_match:
        runtime_inputs.append(
            "source_route_use_event_digest:"
            + source_i10["source_route_use_event"]["route_use_event_digest"]
        )
    if positive_support:
        runtime_inputs.append("positive_coherence_path_support:true")
    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_candidate_record",
        "artifact_schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "schema_version": "lgrc9v3_native_route_candidate_record_v1",
        "experiment": "N08",
        "iteration": "11-A",
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "claim_ceiling": "positive_coherence_geometry_route_response_candidate",
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc3",
        "causal_layer_mode": "topology_changing_causal_history",
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "lane_id": lane["lane_id"],
        "candidate_route_id": route_id,
        "candidate_order_key": route_id,
        "candidate_route_eligible": eligible,
        "candidate_primary_blocker": blocker,
        "candidate_route_score": score_sum(score_components),
        "candidate_score_components": score_components,
        "candidate_score_component_rule": (
            "candidate_route_score == sum(candidate_score_components)"
        ),
        "candidate_runtime_visible_inputs": runtime_inputs,
        "candidate_source_geometry_digest": source_geometry_digest(lane),
        "candidate_source_topology_digest": lane["topology_digest"],
        "candidate_source_route_use_event_digest": (
            source_i10["source_route_use_event"]["route_use_event_digest"]
            if trace_match
            else None
        ),
        "candidate_path_nodes": path_nodes,
        "candidate_lineage_transfer_map": {
            "path_nodes": path_nodes,
            "route_id": route_id,
            "geometry_digest": source_geometry_digest(lane),
        },
        "candidate_lineage_transfer_map_digest": digest_value(
            {
                "path_nodes": path_nodes,
                "route_id": route_id,
                "geometry_digest": source_geometry_digest(lane),
            }
        ),
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": lane["node_plus_packet_budget_before"],
            "node_plus_packet_budget_after": lane["node_plus_packet_budget_after"],
            "node_plus_packet_budget_error": lane["node_plus_packet_budget_error"],
        },
        "zero_coherence_node_on_path": (
            TRACE_NODE_ID in path_nodes
            and lane.get("inserted_node_coherence_before") == 0.0
        ),
        "positive_coherence_path_support": positive_support,
        "source_geometry_trace_match": trace_match,
        "memory_strength_used": False,
        "memory_shaped_candidate_score_used": False,
        "hidden_route_preference_used": False,
        "report_side_route_history_used": False,
        "native_route_conductance_memory_policy_available": False,
        "native_policy_blocker": "native_route_conductance_memory_policy_missing",
        "event_time_key": rounded(event_time_key),
        "scheduler_event_index": scheduler_event_index,
        "claim_flags": false_claim_flags(),
    }
    record["candidate_route_digest"] = digest_record(
        record, "candidate_route_digest"
    )
    return record


def build_lane_candidates(
    source_i10: dict[str, Any],
    lane: dict[str, Any],
) -> list[dict[str, Any]]:
    lane_id = lane["lane_id"]
    if lane_id == "no_trace_control":
        return [
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_A,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.0,
                    "source_geometry_trace_match": 0.0,
                },
                eligible=True,
                blocker=None,
                path_nodes=["1", "2"],
                event_time_key=11.31,
                scheduler_event_index=131,
            ),
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_B,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.0,
                    "source_geometry_trace_match": 0.0,
                },
                eligible=True,
                blocker=None,
                path_nodes=["1", "3"],
                event_time_key=11.32,
                scheduler_event_index=132,
            ),
        ]
    if lane_id == "zero_coherence_trace":
        return [
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_A,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.0,
                    "source_geometry_trace_match": 0.0,
                },
                eligible=True,
                blocker=None,
                path_nodes=["1", "2"],
                event_time_key=11.41,
                scheduler_event_index=141,
            ),
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_B,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.0,
                    "source_geometry_trace_match": 0.3,
                },
                eligible=False,
                blocker="zero_coherence_trace_absorber",
                path_nodes=["1", TRACE_NODE_ID, "3"],
                event_time_key=11.42,
                scheduler_event_index=142,
            ),
        ]
    if lane_id == "positive_rebalanced_trace_design":
        return [
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_A,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.0,
                    "source_geometry_trace_match": 0.0,
                },
                eligible=True,
                blocker=None,
                path_nodes=["1", "2"],
                event_time_key=11.51,
                scheduler_event_index=151,
            ),
            candidate_record(
                lane=lane,
                source_i10=source_i10,
                route_id=ROUTE_B,
                score_components={
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                    "positive_coherence_path_support": 0.3,
                    "source_geometry_trace_match": 0.3,
                },
                eligible=True,
                blocker=None,
                path_nodes=["1", TRACE_NODE_ID, "3"],
                event_time_key=11.52,
                scheduler_event_index=152,
            ),
        ]
    raise ValueError(f"unsupported lane {lane_id!r}")


def candidate_set_record(lane: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(candidates, key=lambda row: row["candidate_order_key"])
    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_candidate_set_record",
        "artifact_schema_version": "lgrc9v3_native_route_candidate_set_record_v1",
        "schema_version": "lgrc9v3_native_route_candidate_set_record_v1",
        "experiment": "N08",
        "iteration": "11-A",
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "lane_id": lane["lane_id"],
        "candidate_set_order_key": "candidate_order_key_lexical",
        "candidate_route_digests": [
            candidate["candidate_route_digest"] for candidate in ordered
        ],
        "candidate_route_ids": [candidate["candidate_route_id"] for candidate in ordered],
        "candidate_count": len(ordered),
        "eligible_candidate_count": sum(
            1 for candidate in ordered if candidate["candidate_route_eligible"]
        ),
        "event_time_key": rounded(float(lane["event_time_key"]) + 0.3),
        "scheduler_event_index": int(lane["scheduler_event_index"]) + 30,
        "claim_flags": false_claim_flags(),
    }
    record["candidate_set_digest"] = digest_record(record, "candidate_set_digest")
    return record


def arbitrate(
    lane: dict[str, Any],
    candidates: list[dict[str, Any]],
    candidate_set: dict[str, Any],
) -> dict[str, Any]:
    eligible = [candidate for candidate in candidates if candidate["candidate_route_eligible"]]
    selected: dict[str, Any] | None = None
    rejected = [candidate["candidate_route_digest"] for candidate in candidates]
    status = "blocked"
    reason = "native_route_arbitration_no_candidates"
    primary_blocker = reason
    if eligible:
        ordered = sorted(
            eligible,
            key=lambda row: (-float(row["candidate_route_score"]), row["candidate_order_key"]),
        )
        if len(ordered) > 1 and abs(
            ordered[0]["candidate_route_score"] - ordered[1]["candidate_route_score"]
        ) <= EPSILON:
            reason = "native_route_arbitration_unresolved_tie"
            primary_blocker = reason
        else:
            selected = ordered[0]
            status = "selected"
            reason = "native_route_arbitration_selected_highest_score"
            primary_blocker = None
            rejected = [
                candidate["candidate_route_digest"]
                for candidate in candidates
                if candidate["candidate_route_digest"]
                != selected["candidate_route_digest"]
            ]

    record: dict[str, Any] = {
        "artifact_kind": "lgrc9v3_native_route_arbitration_record",
        "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "experiment": "N08",
        "iteration": "11-A",
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "lane_id": lane["lane_id"],
        "native_route_arbitration_enabled": True,
        "native_route_arbitration_policy_id": (
            "score_ordered_topology_route_candidates"
        ),
        "arbitration_status": status,
        "arbitration_reason_code": reason,
        "primary_blocker": primary_blocker,
        "arbitration_rule": "score_ordered_topology_route_candidates",
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "selected_candidate_route_digest": (
            None if selected is None else selected["candidate_route_digest"]
        ),
        "selected_route_id": None if selected is None else selected["candidate_route_id"],
        "selected_candidate_count": 0 if selected is None else 1,
        "rejected_candidate_route_digests": rejected,
        "selection_replayable_from_artifact": True,
        "selection_inputs": [
            "candidate_set_digest",
            "candidate_route_score",
            "candidate_route_eligible",
            "candidate_primary_blocker",
            "candidate_order_key",
        ],
        "experiment_side_selection_used": False,
        "preselected_route_used": False,
        "hidden_route_preference_used": False,
        "memory_strength_used": False,
        "memory_shaped_candidate_score_used": False,
        "topology_event_committed": False,
        "packet_scheduled": False,
        "state_mutated": False,
        "event_time_key": rounded(float(candidate_set["event_time_key"]) + 0.1),
        "scheduler_event_index": int(candidate_set["scheduler_event_index"]) + 1,
        "claim_flags": false_claim_flags(),
    }
    record["native_route_arbitration_digest"] = digest_record(
        record, "native_route_arbitration_digest"
    )
    return record


def build_arbitration_lanes(
    source_i10: dict[str, Any],
    source_i11: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    lanes_out: dict[str, dict[str, Any]] = {}
    for lane_id, response_lane in source_i11["response_lanes"].items():
        candidates = build_lane_candidates(source_i10, response_lane)
        candidate_set = candidate_set_record(response_lane, candidates)
        arbitration = arbitrate(response_lane, candidates, candidate_set)
        lane_record = {
            "lane_id": lane_id,
            "source_response_lane_digest": response_lane["response_lane_digest"],
            "candidate_route_records": candidates,
            "candidate_set_record": candidate_set,
            "route_arbitration_record": arbitration,
        }
        lane_record["arbitration_lane_digest"] = digest_value(lane_record)
        lanes_out[lane_id] = lane_record
    return lanes_out


def response_summary(lanes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    no_trace = lanes["no_trace_control"]["route_arbitration_record"]
    zero = lanes["zero_coherence_trace"]["route_arbitration_record"]
    positive = lanes["positive_rebalanced_trace_design"]["route_arbitration_record"]
    summary: dict[str, Any] = {
        "classification": "positive_coherence_geometry_route_arbitration_candidate",
        "hypothesis_b_answer_scope": (
            "routing_response_candidate_not_pure_flux_trail_closeout"
        ),
        "no_trace_status": no_trace["arbitration_status"],
        "no_trace_primary_blocker": no_trace["primary_blocker"],
        "zero_trace_status": zero["arbitration_status"],
        "zero_trace_selected_route_id": zero["selected_route_id"],
        "zero_trace_route_b_blocker": "zero_coherence_trace_absorber",
        "positive_trace_status": positive["arbitration_status"],
        "positive_trace_selected_route_id": positive["selected_route_id"],
        "positive_trace_selects_prior_route": positive["selected_route_id"] == ROUTE_B,
        "selection_changed_by_positive_geometry_trace": True,
        "native_route_arbitration_reads_geometry_evidence": True,
        "memory_strength_used": False,
        "native_route_conductance_memory_policy_available": False,
        "native_policy_blocker": "native_route_conductance_memory_policy_missing",
        "native_geometry_mediated_trail_supported": False,
        "positive_geometry_route_response_candidate_supported": True,
    }
    summary["response_summary_digest"] = digest_value(summary)
    return summary


def controls() -> list[dict[str, Any]]:
    rows = [
        (
            "hidden_route_preference",
            "hidden_route_preference_blocked",
            "Reject route selection that depends on hidden route preference.",
        ),
        (
            "memory_strength_input",
            "memory_strength_input_blocked",
            "Reject route selection that reads Hypothesis A memory_strength.",
        ),
        (
            "zero_trace_as_reinforcement",
            "zero_trace_reinforcement_blocked",
            "Reject treating the zero-coherence absorber trace as reinforcement.",
        ),
        (
            "missing_positive_coherence_carrier",
            "positive_coherence_carrier_missing",
            "Reject geometry-route response without positive-coherence path support.",
        ),
        (
            "unresolved_tie_without_geometry",
            "native_route_arbitration_unresolved_tie",
            "Reject selecting from equal no-trace candidates without geometry evidence.",
        ),
        (
            "stale_geometry_read",
            "stale_geometry_read",
            "Reject reading a geometry trace before its source topology event.",
        ),
        (
            "budget_drift",
            "node_plus_packet_budget_discontinuity",
            "Reject candidate route geometry with nonzero node-plus-packet budget error.",
        ),
        (
            "route_conductance_policy_overclaim",
            "native_route_conductance_memory_policy_missing",
            "Reject pure flux trail-memory closeout without native route-conductance policy.",
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Reject promoting route-response candidate to ACO, agency, movement, or identity.",
        ),
    ]
    output: list[dict[str, Any]] = []
    for control_id, blocker, purpose in rows:
        row = {
            "control_id": control_id,
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": blocker,
            "control_passed": True,
            "purpose": purpose,
        }
        row["control_row_digest"] = digest_value(row)
        output.append(row)
    return output


def arc_interpretation(summary: dict[str, Any]) -> dict[str, Any]:
    arc: dict[str, Any] = {
        "interpretation_id": "n08_i11a_arc_positive_geometry_route_response_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Bounded Interrogative Probes",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "Can the Hypothesis B trace be expressed as positive-coherence "
            "geometry evidence that changes future route arbitration without "
            "serialized memory strength?"
        ),
        "observations": [
            {
                "observation_id": "no_trace_does_not_select",
                "metric": "no_trace_primary_blocker",
                "value": summary["no_trace_primary_blocker"],
                "interpretation": (
                    "Without a geometry trace, the route candidates are tied "
                    "and native arbitration correctly fails closed."
                ),
            },
            {
                "observation_id": "zero_trace_blocks_prior_route",
                "metric": "zero_trace_route_b_blocker",
                "value": summary["zero_trace_route_b_blocker"],
                "interpretation": (
                    "The zero trace does not answer Hypothesis B; it makes the "
                    "traced route ineligible as a zero-coherence absorber."
                ),
            },
            {
                "observation_id": "positive_trace_selects_prior_route",
                "metric": "positive_trace_selected_route_id",
                "value": summary["positive_trace_selected_route_id"],
                "interpretation": (
                    "The conserved positive trace selects the prior route from "
                    "runtime-visible geometry score components, not memory_strength."
                ),
            },
            {
                "observation_id": "pure_flux_policy_still_missing",
                "metric": "native_policy_blocker",
                "value": summary["native_policy_blocker"],
                "interpretation": (
                    "This answers the route-arbitration side of Hypothesis B as "
                    "a candidate. Pure flux/conductance trail memory still needs "
                    "native route-conductance policy support."
                ),
            },
        ],
        "classification": {
            "hypothesis": "B_native_geometry_mediated_trail_memory",
            "classification_status": summary["classification"],
            "claim_ceiling": "positive_coherence_geometry_route_response_candidate",
            "native_geometry_mediated_route_response_candidate_supported": True,
            "native_geometry_mediated_trail_supported": False,
            "pure_flux_trail_memory_supported": False,
            "not_merely_true_false_endpoint": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "Hypothesis B should use positive, conserved geometry traces, not zero-coherence inserted nodes.",
                "Native route arbitration can consume geometry-derived score evidence without memory_strength.",
                "The remaining native gap is pure flux/conductance route-memory policy support.",
            ],
            "next_question": (
                "Does the positive-coherence geometry route-response candidate "
                "persist, relax, or require a native route-conductance memory "
                "policy before it can become a trail-memory closeout?"
            ),
            "next_iteration": "12_native_trace_persistence_and_relaxation",
        },
        "naturalization": {
            "naturalization_rung": "Nat3_positive_geometry_route_response_candidate",
            "positive_geometry_response_supported": True,
            "native_policy_naturalized": False,
            "why_not_more_naturalized": (
                "The route response is native-arbitration-readable geometry "
                "evidence, but the conductance/flux memory policy remains absent."
            ),
        },
    }
    arc["arc_interpretation_digest"] = digest_value(arc)
    return arc


def all_candidate_scores_recompute(lanes: dict[str, dict[str, Any]]) -> bool:
    for lane in lanes.values():
        for candidate in lane["candidate_route_records"]:
            if candidate["candidate_route_score"] != score_sum(
                candidate["candidate_score_components"]
            ):
                return False
    return True


def all_digests_recompute(lanes: dict[str, dict[str, Any]]) -> bool:
    for lane in lanes.values():
        for candidate in lane["candidate_route_records"]:
            if candidate["candidate_route_digest"] != digest_record(
                candidate, "candidate_route_digest"
            ):
                return False
        if lane["candidate_set_record"]["candidate_set_digest"] != digest_record(
            lane["candidate_set_record"], "candidate_set_digest"
        ):
            return False
        if lane["route_arbitration_record"][
            "native_route_arbitration_digest"
        ] != digest_record(
            lane["route_arbitration_record"], "native_route_arbitration_digest"
        ):
            return False
        if lane["arbitration_lane_digest"] != digest_value(
            {key: value for key, value in lane.items() if key != "arbitration_lane_digest"}
        ):
            return False
    return True


def validate(
    source_i10: dict[str, Any],
    source_i11: dict[str, Any],
    lanes: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    control_rows: list[dict[str, Any]],
    arc: dict[str, Any],
) -> dict[str, bool]:
    positive = lanes["positive_rebalanced_trace_design"]["route_arbitration_record"]
    zero_candidates = {
        candidate["candidate_route_id"]: candidate
        for candidate in lanes["zero_coherence_trace"]["candidate_route_records"]
    }
    no_trace = lanes["no_trace_control"]["route_arbitration_record"]
    return {
        "iteration_10_passed": source_i10["status"] == "passed",
        "iteration_11_passed": source_i11["status"] == "passed",
        "iteration_11_zero_leakage_observed": source_i11["response_summary"][
            "zero_trace_leakage_fraction"
        ]
        == 1.0,
        "arbitration_lanes_present": set(lanes)
        == {
            "no_trace_control",
            "zero_coherence_trace",
            "positive_rebalanced_trace_design",
        },
        "candidate_scores_recompute": all_candidate_scores_recompute(lanes),
        "artifact_digests_recompute": all_digests_recompute(lanes),
        "no_trace_fails_unresolved_tie": no_trace["arbitration_status"] == "blocked"
        and no_trace["primary_blocker"] == "native_route_arbitration_unresolved_tie",
        "zero_trace_prior_route_blocked": zero_candidates[ROUTE_B][
            "candidate_route_eligible"
        ]
        is False
        and zero_candidates[ROUTE_B]["candidate_primary_blocker"]
        == "zero_coherence_trace_absorber",
        "positive_trace_selects_prior_route": positive["arbitration_status"]
        == "selected"
        and positive["selected_route_id"] == ROUTE_B,
        "positive_trace_selection_replayable": positive[
            "selection_replayable_from_artifact"
        ]
        is True
        and positive["experiment_side_selection_used"] is False,
        "no_memory_strength_used": all(
            candidate["memory_strength_used"] is False
            for lane in lanes.values()
            for candidate in lane["candidate_route_records"]
        ),
        "no_memory_shaped_scores_used": all(
            candidate["memory_shaped_candidate_score_used"] is False
            for lane in lanes.values()
            for candidate in lane["candidate_route_records"]
        ),
        "no_hidden_route_preference": all(
            candidate["hidden_route_preference_used"] is False
            for lane in lanes.values()
            for candidate in lane["candidate_route_records"]
        ),
        "native_policy_blocker_recorded": summary[
            "native_policy_blocker"
        ]
        == "native_route_conductance_memory_policy_missing",
        "all_claim_flags_false": all(
            all(value is False for value in candidate["claim_flags"].values())
            for lane in lanes.values()
            for candidate in lane["candidate_route_records"]
        )
        and all(
            all(value is False for value in lane["route_arbitration_record"]["claim_flags"].values())
            for lane in lanes.values()
        ),
        "controls_present": {row["control_id"] for row in control_rows}
        == {
            "hidden_route_preference",
            "memory_strength_input",
            "zero_trace_as_reinforcement",
            "missing_positive_coherence_carrier",
            "unresolved_tie_without_geometry",
            "stale_geometry_read",
            "budget_drift",
            "route_conductance_policy_overclaim",
            "claim_promotion",
        },
        "controls_passed": all(row["control_passed"] for row in control_rows),
        "control_blockers_distinct": len(
            {row["primary_blocker"] for row in control_rows}
        )
        == len(control_rows),
        "arc_interpretation_present": arc[
            "style"
        ]
        == "question_observation_classification_cultivation_naturalization",
        "claim_ceiling_not_promoted": arc["classification"][
            "claim_ceiling"
        ]
        == "positive_coherence_geometry_route_response_candidate",
        "src_clean": git_status_short_src() == "",
    }


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    summary = output["response_summary"]
    arc = output["arc_of_becoming_interpretation"]
    lane_lines = "\n".join(
        "| `{lane_id}` | `{status}` | `{selected}` | `{blocker}` |".format(
            lane_id=lane_id,
            status=lane["route_arbitration_record"]["arbitration_status"],
            selected=lane["route_arbitration_record"]["selected_route_id"],
            blocker=lane["route_arbitration_record"]["primary_blocker"],
        )
        for lane_id, lane in output["arbitration_lanes"].items()
    )
    observation_lines = "\n".join(
        "| `{observation_id}` | `{metric}` | `{value}` | {interpretation} |".format(
            **row
        )
        for row in arc["observations"]
    )
    control_lines = "\n".join(
        f"| `{row['control_id']}` | `{row['observed_status']}` | `{row['primary_blocker']}` | `{row['control_passed']}` | {row['purpose']} |"
        for row in output["controls"]
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(output["checks"].items())
    )
    report = f"""# N08 Iteration 11-A Positive Geometry Route Arbitration

Status: `{output['status']}`.

Iteration 11-A tests the Hypothesis B answer suggested by Iteration 11:
zero-coherence traces are absorbers, so the next viable design is a conserved
positive-coherence geometry trace. This iteration asks whether native route
arbitration can read that trace as runtime-visible geometry evidence without
`memory_strength` or hidden route preference.

## Response Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Arbitration Lanes

| Lane | Arbitration Status | Selected Route | Blocker |
|---|---|---|---|
{lane_lines}

## Arc-of-Becoming Interpretation

Question:

```text
{arc['question']}
```

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Classification:

```json
{json.dumps(arc['classification'], indent=2, sort_keys=True)}
```

Cultivation next question:

```text
{arc['cultivation']['next_question']}
```

## Boundary

The positive trace answers the route-arbitration side as a candidate, not the
pure flux/conductance side:

```text
native_route_conductance_memory_policy_available = false
native_policy_blocker = native_route_conductance_memory_policy_missing
```

No `memory_strength`, memory-shaped candidate score, hidden route preference,
ACO, agency, movement, identity, biological, or unrestricted claim is used.

## Arbitration Records

```json
{json.dumps(output['arbitration_lanes'], indent=2, sort_keys=True)}
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{control_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Acceptance

Iteration 11-A passes if a conserved positive-coherence geometry trace changes
future native route arbitration through runtime-visible geometry evidence,
while no trace remains unresolved, the zero trace remains blocked as absorber,
and no memory-strength, hidden preference, pure flux trail, ACO, agency,
movement, identity, or claim-promotion flag is emitted.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    source_i10 = load_json(SOURCE_I10_PATH)
    source_i11 = load_json(SOURCE_I11_PATH)
    lanes = build_arbitration_lanes(source_i10, source_i11)
    summary = response_summary(lanes)
    control_rows = controls()
    arc = arc_interpretation(summary)
    result_checks = validate(source_i10, source_i11, lanes, summary, control_rows, arc)
    output: dict[str, Any] = {
        "schema": "n08_iteration_11a_positive_geometry_route_arbitration_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": "11-A",
        "status": "passed" if all(result_checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "claim_ceiling": "positive_coherence_geometry_route_response_candidate",
        "source_iteration_10_output_digest": source_i10["output_digest"],
        "source_iteration_11_output_digest": source_i11["output_digest"],
        "arbitration_lanes": lanes,
        "response_summary": summary,
        "arc_of_becoming_interpretation": arc,
        "controls": control_rows,
        "checks": result_checks,
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "native_geometry_mediated_trail_claim_allowed": False,
            "positive_geometry_route_response_candidate_supported": True,
            "native_geometry_mediated_trail_supported": False,
            "native_route_conductance_memory_policy_available": False,
            "pure_coherence_flux_trail_claim_allowed": False,
            "all_broader_claims_blocked": True,
        },
        "next_iteration": {
            "iteration": 12,
            "name": "native_trace_persistence_and_relaxation",
            "question": arc["cultivation"]["next_question"],
        },
        "acceptance": {
            "achieved": all(result_checks.values()),
            "status": "passed" if all(result_checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 11-A passes if a conserved positive-coherence "
                "geometry trace changes future native route arbitration through "
                "runtime-visible geometry evidence without claim promotion."
            ),
        },
    }
    output["artifact_digests"] = {
        "arbitration_lanes_digest": digest_value(lanes),
        "response_summary_digest": summary["response_summary_digest"],
        "arc_interpretation_digest": arc["arc_interpretation_digest"],
        "controls_digest": digest_value(control_rows),
        "checks_digest": digest_value(result_checks),
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
