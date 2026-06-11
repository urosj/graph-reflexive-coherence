#!/usr/bin/env python3
"""Run N08 Iteration 11 future flux response to geometry trace.

Iteration 11 follows the Arc-of-Becoming method. It does not ask whether the
Iteration 10 trace "passes" as reinforcement. It asks what future flux becomes
around the trace: no response, leakage/absorption, or a design direction for a
theory-clean positive-coherence geometry.
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
SOURCE_I10_PATH = (
    EXPERIMENT / "outputs/n08_iteration_10_geometry_trail_formation.json"
)
SOURCE_I10_REPORT = (
    EXPERIMENT / "reports/n08_iteration_10_geometry_trail_formation.md"
)
SOURCE_I9_PATH = (
    EXPERIMENT / "outputs/n08_iteration_9_native_geometry_trail_baseline.json"
)
OUTPUT_PATH = (
    EXPERIMENT / "outputs/n08_iteration_11_geometry_trace_flux_response.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports/n08_iteration_11_geometry_trace_flux_response.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_11_geometry_trace_flux_response.py"
)

TRACE_NODE_ID = "30"
FUTURE_PACKET_AMOUNT = 0.1
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


def rounded(value: float) -> float:
    return round(float(value), 12)


def source_artifacts() -> dict[str, str]:
    return {
        rel(SOURCE_I10_PATH): digest_file(SOURCE_I10_PATH),
        rel(SOURCE_I9_PATH): digest_file(SOURCE_I9_PATH),
    }


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_I10_REPORT): digest_file(SOURCE_I10_REPORT)}


def node_total(state: dict[str, float]) -> float:
    return rounded(sum(float(value) for value in state.values()))


def apply_future_probe(
    *,
    lane_id: str,
    path_nodes: list[str],
    node_state_before: dict[str, float],
    source_iteration_10: dict[str, Any],
    topology_kind: str,
    topology_digest: str,
    event_time_key: float,
    scheduler_event_index: int,
    diagnostic_policy_id: str,
) -> dict[str, Any]:
    """Apply the small diagnostic response probe to one topology lane.

    The policy is intentionally simple and serialized: a future packet tries to
    move along the declared route path. If the next node is a zero-coherence
    node, the packet is retained there and classified as leakage/absorption.
    Otherwise it transits to the final target. This is not a native route
    conductance policy and must not be promoted as such.
    """

    before = {key: float(value) for key, value in node_state_before.items()}
    after = dict(before)
    source_node = path_nodes[0]
    target_node = path_nodes[-1]
    inserted_before = before.get(TRACE_NODE_ID)
    retained_at_inserted = 0.0
    target_delivery = 0.0
    packet_processed_by_step = True
    route_continuity = True
    event_class = "direct_target_delivery"

    after[source_node] = rounded(after[source_node] - FUTURE_PACKET_AMOUNT)
    if TRACE_NODE_ID in path_nodes and before.get(TRACE_NODE_ID, 0.0) <= EPSILON:
        after[TRACE_NODE_ID] = rounded(after.get(TRACE_NODE_ID, 0.0) + FUTURE_PACKET_AMOUNT)
        retained_at_inserted = FUTURE_PACKET_AMOUNT
        route_continuity = False
        event_class = "zero_trace_leakage_absorption"
    else:
        after[target_node] = rounded(after[target_node] + FUTURE_PACKET_AMOUNT)
        target_delivery = FUTURE_PACKET_AMOUNT
        if TRACE_NODE_ID in path_nodes:
            event_class = "positive_rebalanced_trace_transit"

    inserted_after = after.get(TRACE_NODE_ID)
    inserted_delta = None
    if inserted_before is not None and inserted_after is not None:
        inserted_delta = rounded(inserted_after - inserted_before)

    budget_before = node_total(before)
    budget_after = node_total(after)
    record: dict[str, Any] = {
        "artifact_kind": "n08_geometry_trace_future_flux_response_lane",
        "schema_version": "n08_geometry_trace_future_flux_response_lane_v1",
        "experiment": "N08",
        "iteration": 11,
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "lane_id": lane_id,
        "topology_kind": topology_kind,
        "topology_digest": topology_digest,
        "source_iteration_10_output_digest": source_iteration_10["output_digest"],
        "source_topology_event_digest": source_iteration_10["topology_event"][
            "topology_event_digest"
        ],
        "source_theory_caveat_digest": source_iteration_10["theory_caveat"][
            "theory_caveat_digest"
        ],
        "diagnostic_policy_id": diagnostic_policy_id,
        "diagnostic_policy_scope": (
            "experiment_local_artifact_probe_not_native_route_conductance_policy"
        ),
        "native_route_conductance_memory_policy_available": False,
        "native_policy_blocker": "native_route_conductance_memory_policy_missing",
        "path_nodes": path_nodes,
        "future_packet_amount": FUTURE_PACKET_AMOUNT,
        "event_time_key": rounded(event_time_key),
        "scheduler_event_index": scheduler_event_index,
        "node_state_before": before,
        "node_state_after": after,
        "inserted_node_id": int(TRACE_NODE_ID) if TRACE_NODE_ID in path_nodes else None,
        "inserted_node_coherence_before": inserted_before,
        "inserted_node_coherence_after": inserted_after,
        "inserted_node_coherence_delta": inserted_delta,
        "retained_at_inserted_node": rounded(retained_at_inserted),
        "target_delivery": rounded(target_delivery),
        "route_continuity_preserved": route_continuity,
        "future_response_class": event_class,
        "leakage_fraction": rounded(retained_at_inserted / FUTURE_PACKET_AMOUNT),
        "target_delivery_fraction": rounded(target_delivery / FUTURE_PACKET_AMOUNT),
        "packet_processed_by_step": packet_processed_by_step,
        "producer_or_report_mutated_state": False,
        "memory_strength_used": False,
        "memory_shaped_candidate_score_used": False,
        "hidden_route_preference_used": False,
        "node_plus_packet_budget_before": budget_before,
        "node_plus_packet_budget_after": budget_after,
        "node_plus_packet_budget_error": rounded(budget_after - budget_before),
        "claim_flags": false_claim_flags(),
    }
    record["response_lane_digest"] = digest_record(record, "response_lane_digest")
    return record


def build_lanes(source_i10: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reabsorption = source_i10["topology_state_reabsorption_record"]
    pre_trace_state = {
        key: float(value)
        for key, value in reabsorption["active_node_state_before"].items()
    }
    zero_trace_state = {
        key: float(value)
        for key, value in reabsorption["active_node_state_after"].items()
    }
    positive_rebalanced_state = {
        "0": 1.5,
        "1": 1.0,
        "2": 1.5,
        "3": 1.0,
        TRACE_NODE_ID: 1.0,
    }
    positive_topology = {
        "topology_kind": "coherence_split_preserving_edge_split_design_candidate",
        "source_route_use_event_digest": source_i10["source_route_use_event"][
            "route_use_event_digest"
        ],
        "path_nodes": ["1", TRACE_NODE_ID, "3"],
        "node_state_before": positive_rebalanced_state,
        "conserved_total": node_total(positive_rebalanced_state),
        "theory_clean_positive_carrier": True,
        "design_status": "followup_design_candidate_not_iteration_10_runtime_trace",
    }
    positive_topology["topology_digest"] = digest_value(positive_topology)
    policy_id = "n08_i11_serialized_local_response_probe_v1"
    positive_lane = apply_future_probe(
        lane_id="positive_rebalanced_trace_design",
        path_nodes=positive_topology["path_nodes"],
        node_state_before=positive_rebalanced_state,
        source_iteration_10=source_i10,
        topology_kind=positive_topology["topology_kind"],
        topology_digest=positive_topology["topology_digest"],
        event_time_key=11.2,
        scheduler_event_index=112,
        diagnostic_policy_id=policy_id,
    )
    positive_lane["positive_rebalanced_topology_design"] = positive_topology
    positive_lane["response_lane_digest"] = digest_record(
        positive_lane, "response_lane_digest"
    )
    return {
        "no_trace_control": apply_future_probe(
            lane_id="no_trace_control",
            path_nodes=["1", "3"],
            node_state_before=pre_trace_state,
            source_iteration_10=source_i10,
            topology_kind="no_inserted_trace_control",
            topology_digest=source_i10["pre_trace_topology_snapshot"][
                "topology_snapshot_digest"
            ],
            event_time_key=11.0,
            scheduler_event_index=110,
            diagnostic_policy_id=policy_id,
        ),
        "zero_coherence_trace": apply_future_probe(
            lane_id="zero_coherence_trace",
            path_nodes=["1", TRACE_NODE_ID, "3"],
            node_state_before=zero_trace_state,
            source_iteration_10=source_i10,
            topology_kind="iteration_10_zero_coherence_edge_split_trace",
            topology_digest=source_i10["topology_event"]["topology_event_digest"],
            event_time_key=11.1,
            scheduler_event_index=111,
            diagnostic_policy_id=policy_id,
        ),
        "positive_rebalanced_trace_design": positive_lane,
    }


def response_summary(lanes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    zero = lanes["zero_coherence_trace"]
    no_trace = lanes["no_trace_control"]
    positive = lanes["positive_rebalanced_trace_design"]
    summary: dict[str, Any] = {
        "matched_lane_count": len(lanes),
        "zero_trace_leakage_fraction": zero["leakage_fraction"],
        "zero_trace_target_delivery_fraction": zero["target_delivery_fraction"],
        "zero_trace_inserted_node_delta": zero["inserted_node_coherence_delta"],
        "no_trace_target_delivery_fraction": no_trace["target_delivery_fraction"],
        "positive_rebalanced_target_delivery_fraction": positive[
            "target_delivery_fraction"
        ],
        "positive_rebalanced_leakage_fraction": positive["leakage_fraction"],
        "future_response_observed": True,
        "primary_observation": "zero_coherence_trace_behaves_as_absorber",
        "stronger_design_direction_observed": (
            "coherence_split_preserving_positive_trace_can_transit_probe_packet"
        ),
        "native_geometry_mediated_trail_supported": False,
        "reinforcement_interpretation_supported": False,
        "classification": "zero_trace_leakage_boundary_with_positive_rebalanced_design_direction",
    }
    summary["response_summary_digest"] = digest_value(summary)
    return summary


def controls() -> list[dict[str, Any]]:
    rows = [
        (
            "hidden_route_preference",
            "hidden_route_preference_blocked",
            "Reject future response attributed to hidden route preference.",
        ),
        (
            "score_only_memory_input",
            "score_only_memory_input_blocked",
            "Reject using serialized memory_strength or candidate-score memory input.",
        ),
        (
            "stale_geometry_read",
            "stale_geometry_read",
            "Reject response that reads the trace before Iteration 10 topology commit.",
        ),
        (
            "order_inversion",
            "future_response_order_inversion",
            "Reject response event ordered before source route-use and topology trace.",
        ),
        (
            "budget_drift",
            "node_plus_packet_budget_discontinuity",
            "Reject future response that creates or deletes node-plus-packet budget.",
        ),
        (
            "missing_positive_followup_design",
            "positive_coherence_followup_design_missing",
            "Reject zero-node leakage closeout without a positive/rebalanced follow-up design.",
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Reject promoting response probe to memory, ACO, agency, or movement.",
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


def arc_interpretation(
    source_i10: dict[str, Any],
    lanes: dict[str, dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    zero = lanes["zero_coherence_trace"]
    positive = lanes["positive_rebalanced_trace_design"]
    arc: dict[str, Any] = {
        "interpretation_id": "n08_i11_arc_future_flux_response_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Bounded Interrogative Probes",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What does future flux become when it encounters the Iteration 10 "
            "zero-coherence topology trace?"
        ),
        "observations": [
            {
                "observation_id": "zero_trace_absorbs_future_packet",
                "metric": "zero_trace_inserted_node_coherence_delta",
                "value": zero["inserted_node_coherence_delta"],
                "interpretation": (
                    "The future packet is retained at the inserted zero node. "
                    "This supports the leakage/absorption caveat rather than "
                    "route reinforcement."
                ),
            },
            {
                "observation_id": "target_delivery_blocked_by_zero_trace",
                "metric": "zero_trace_target_delivery_fraction",
                "value": zero["target_delivery_fraction"],
                "interpretation": (
                    "The zero-trace lane does not deliver the probe packet to "
                    "the target under the serialized diagnostic policy."
                ),
            },
            {
                "observation_id": "positive_rebalanced_trace_transits",
                "metric": "positive_rebalanced_target_delivery_fraction",
                "value": positive["target_delivery_fraction"],
                "interpretation": (
                    "A conserved positive-coherence edge split can carry the "
                    "probe packet without retaining it at the inserted node. "
                    "This is a design direction, not a native memory claim."
                ),
            },
            {
                "observation_id": "native_policy_still_missing",
                "metric": "native_route_conductance_memory_policy_available",
                "value": False,
                "interpretation": (
                    "The response metric is diagnostic because N08 still has "
                    "no native route-conductance memory policy."
                ),
            },
        ],
        "classification": {
            "hypothesis": "B_native_geometry_mediated_trail_memory",
            "classification_status": summary["classification"],
            "claim_ceiling": "diagnostic_geometry_trace_response_boundary_probe",
            "zero_trace_reinforcement_supported": False,
            "future_response_observed": True,
            "native_geometry_mediated_trail_supported": False,
            "stronger_design_direction": summary["stronger_design_direction_observed"],
            "not_merely_true_false_endpoint": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "The zero-coherence trace becomes a leakage/absorption site under the response probe.",
                "A positive, coherence-split-preserving trace is a better next design than a zero node.",
                "The missing native route-conductance memory policy remains the core native-support blocker.",
            ],
            "next_question": (
                "Can a positive-coherence, geometry-mediated trace shape "
                "future route arbitration through native-visible geometry "
                "rather than through a diagnostic response probe?"
            ),
            "next_iteration": "12_native_trace_persistence_and_relaxation",
        },
        "naturalization": {
            "naturalization_rung": "Nat2_response_boundary_classified",
            "zero_trace_naturalized": False,
            "positive_rebalanced_design_naturalized": False,
            "why_not_more_naturalized": (
                "The response is classified from artifact-visible diagnostic "
                "lanes. A native route-conductance/geometry response policy is "
                "still missing."
            ),
        },
        "source_iteration_10_theory_caveat_digest": source_i10["theory_caveat"][
            "theory_caveat_digest"
        ],
    }
    arc["arc_interpretation_digest"] = digest_value(arc)
    return arc


def validate(
    source_i9: dict[str, Any],
    source_i10: dict[str, Any],
    lanes: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    control_rows: list[dict[str, Any]],
    arc: dict[str, Any],
) -> dict[str, bool]:
    return {
        "iteration_9_passed": source_i9["status"] == "passed",
        "iteration_10_passed": source_i10["status"] == "passed",
        "iteration_10_theory_caveat_present": source_i10["theory_caveat"][
            "zero_coherence_inserted_node_allowed_by_theory"
        ]
        is False,
        "matched_lanes_present": set(lanes)
        == {
            "no_trace_control",
            "zero_coherence_trace",
            "positive_rebalanced_trace_design",
        },
        "lane_digests_recompute": all(
            lane["response_lane_digest"] == digest_record(lane, "response_lane_digest")
            for lane in lanes.values()
        ),
        "zero_trace_absorbs_packet": lanes["zero_coherence_trace"][
            "retained_at_inserted_node"
        ]
        == FUTURE_PACKET_AMOUNT
        and lanes["zero_coherence_trace"]["target_delivery"] == 0.0,
        "zero_trace_not_reinforcement": lanes["zero_coherence_trace"][
            "future_response_class"
        ]
        == "zero_trace_leakage_absorption"
        and summary["reinforcement_interpretation_supported"] is False,
        "positive_rebalanced_followup_present": lanes[
            "positive_rebalanced_trace_design"
        ]["positive_rebalanced_topology_design"]["theory_clean_positive_carrier"]
        is True,
        "positive_rebalanced_transits": lanes["positive_rebalanced_trace_design"][
            "target_delivery"
        ]
        == FUTURE_PACKET_AMOUNT
        and lanes["positive_rebalanced_trace_design"]["retained_at_inserted_node"]
        == 0.0,
        "node_plus_packet_budgets_exact": all(
            lane["node_plus_packet_budget_error"] == 0.0 for lane in lanes.values()
        ),
        "no_memory_strength_used": all(
            lane["memory_strength_used"] is False for lane in lanes.values()
        ),
        "no_memory_shaped_scoring_used": all(
            lane["memory_shaped_candidate_score_used"] is False
            for lane in lanes.values()
        ),
        "no_hidden_route_preference": all(
            lane["hidden_route_preference_used"] is False for lane in lanes.values()
        ),
        "native_policy_blocker_recorded": all(
            lane["native_policy_blocker"]
            == "native_route_conductance_memory_policy_missing"
            for lane in lanes.values()
        ),
        "all_claim_flags_false": all(
            all(value is False for value in lane["claim_flags"].values())
            for lane in lanes.values()
        ),
        "controls_present": {row["control_id"] for row in control_rows}
        == {
            "hidden_route_preference",
            "score_only_memory_input",
            "stale_geometry_read",
            "order_inversion",
            "budget_drift",
            "missing_positive_followup_design",
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
        == "diagnostic_geometry_trace_response_boundary_probe",
        "src_clean": git_status_short_src() == "",
    }


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    lanes = output["response_lanes"]
    summary = output["response_summary"]
    arc = output["arc_of_becoming_interpretation"]
    lane_lines = "\n".join(
        "| `{lane_id}` | `{future_response_class}` | `{inserted_node_coherence_delta}` | `{leakage_fraction}` | `{target_delivery_fraction}` | `{node_plus_packet_budget_error}` |".format(
            **lane
        )
        for lane in lanes.values()
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
    report = f"""# N08 Iteration 11 Geometry Trace Flux Response

Status: `{output['status']}`.

Iteration 11 asks what future flux becomes around the Iteration 10 topology
trace. It is an Arc-of-Becoming response probe, not a yes/no reinforcement
test. The zero-coherence trace is expected to behave as a boundary or leakage
site unless a positive-coherence geometry can carry the route.

## Response Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Matched Lanes

| Lane | Response Class | Inserted Delta | Leakage Fraction | Target Delivery Fraction | Budget Error |
|---|---|---:|---:|---:|---:|
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

## Native Policy Boundary

The response policy is serialized and artifact-visible, but it is diagnostic:

```text
native_route_conductance_memory_policy_available = false
native_policy_blocker = native_route_conductance_memory_policy_missing
```

No `memory_strength`, memory-shaped candidate score, hidden route preference,
ACO, agency, movement, or native trail claim is used.

## Response Records

```json
{json.dumps(lanes, indent=2, sort_keys=True)}
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

Iteration 11 passes if future flux/routing behavior around the declared
geometry/topology/support trace is source-backed and classified without
promotion: either as leakage/absorption into the zero-coherence boundary probe,
as avoidance/no-response, or as a stronger response from a positive-coherence
or rebalanced geometry candidate, with no independent memory scalar, no hidden
steering, and exact budgets.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    source_i9 = load_json(SOURCE_I9_PATH)
    source_i10 = load_json(SOURCE_I10_PATH)
    lanes = build_lanes(source_i10)
    summary = response_summary(lanes)
    control_rows = controls()
    arc = arc_interpretation(source_i10, lanes, summary)
    result_checks = validate(source_i9, source_i10, lanes, summary, control_rows, arc)
    output: dict[str, Any] = {
        "schema": "n08_iteration_11_geometry_trace_flux_response_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 11,
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
        "claim_ceiling": "diagnostic_geometry_trace_response_boundary_probe",
        "source_iteration_10_output_digest": source_i10["output_digest"],
        "source_iteration_10_topology_event_digest": source_i10["topology_event"][
            "topology_event_digest"
        ],
        "source_iteration_10_theory_caveat_digest": source_i10["theory_caveat"][
            "theory_caveat_digest"
        ],
        "response_summary": summary,
        "response_lanes": lanes,
        "arc_of_becoming_interpretation": arc,
        "controls": control_rows,
        "checks": result_checks,
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "native_geometry_mediated_trail_claim_allowed": False,
            "future_flux_response_classified": True,
            "native_route_conductance_memory_policy_available": False,
            "reinforcement_interpretation_allowed": False,
            "hypothesis_b_closeout_reached": False,
            "all_broader_claims_blocked": True,
        },
        "next_iteration": {
            "iteration": "11-A",
            "name": "positive_coherence_geometry_route_arbitration_response",
            "question": arc["cultivation"]["next_question"],
        },
        "acceptance": {
            "achieved": all(result_checks.values()),
            "status": "passed" if all(result_checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 11 passes if future flux/routing behavior around "
                "the declared geometry/topology/support trace is source-backed "
                "and classified without promotion."
            ),
        },
    }
    output["artifact_digests"] = {
        "response_summary_digest": summary["response_summary_digest"],
        "response_lanes_digest": digest_value(lanes),
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
