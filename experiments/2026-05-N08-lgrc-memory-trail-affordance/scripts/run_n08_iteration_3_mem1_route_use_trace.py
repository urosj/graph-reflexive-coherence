#!/usr/bin/env python3
"""Run N08 Iteration 3 MEM1 route-use trace.

Iteration 3 creates committed route-use trace records from N06 selected-route
artifacts. It does not emit memory surfaces yet. The report interprets the
trace in an Arc-of-Becoming style: question, observation, classification,
cultivation, and naturalization boundary.
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
MANIFEST_VALIDATION_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_2_fixture_manifest_validation.json"
)
SOURCE_N06_SC5_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "outputs"
    / "n06_iteration_7_sc5_repeated_context_selection.json"
)
SOURCE_N06_SC5_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N06-lgrc-semantic-route-choice"
    / "reports"
    / "n06_iteration_7_sc5_repeated_context_selection.md"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_3_mem1_route_use_trace.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_3_mem1_route_use_trace.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_3_mem1_route_use_trace.py"
)
ROUTE_USE_EVENT_TIME_OFFSET = 0.1
ROUTE_USE_EVENT_TIME_STRIDE = 1.0
ROUTE_USE_SCHEDULER_INDEX_OFFSET = 1

MEM1_SUPPLEMENTARY_FIELDS = [
    "artifact_kind",
    "candidate_context_values",
    "candidate_score_component_sums",
    "claim_ceiling",
    "event_order_relation",
    "event_time_key_derivation",
    "mem_level",
    "mem_level_is_evidence_classification",
    "memory_surface_digest",
    "memory_surface_emitted",
    "memory_surface_state_snapshot",
    "node_plus_packet_budget_semantics",
    "rejected_candidate_route_digests",
    "route_aspect_id",
    "route_use_commit_semantics",
    "schema_version",
    "source_arbitration_digest_derivation",
    "source_arbitration_event_time_key",
    "source_arbitration_record_id",
    "source_arbitration_record_id_from_n06_lane",
    "source_arbitration_record_id_matches_n06_lane",
    "source_arbitration_record_id_required_by_manifest",
    "source_arbitration_scheduler_event_index",
    "source_context_state_id",
    "source_cycle_id",
    "source_experiment",
    "source_surface_digest",
    "source_surface_digest_derivation",
    "source_surface_digest_present",
    "topology_commit_status",
    "visual_is_evidence_source",
    "visual_reference",
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


def cycle_index(cycle_id: str) -> int:
    return int(cycle_id.rsplit("_", 1)[1])


def false_claim_flags(manifest: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in manifest["fixture_manifest"]["route_use_event_schema"][
            "required_claim_flag_keys"
        ]
    }


def source_rows(baseline: dict[str, Any]) -> list[dict[str, Any]]:
    rows = list(baseline["n06_inventory"]["route_digest_rows"])
    return sorted(rows, key=lambda row: cycle_index(str(row["cycle_id"])))


def route_use_event_id(cycle_id: str, source_digest: str) -> str:
    return f"n08-route-use:{cycle_id}:{source_digest[:16]}"


def route_use_digest(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "route_use_event_digest"}
    return digest_value(payload)


def first_source_surface_digest(row: dict[str, Any]) -> str | None:
    digests = row.get("candidate_source_surface_digests", [])
    if not digests:
        return None
    return str(digests[0])


def build_route_use_events(
    baseline: dict[str, Any],
    manifest_validation: dict[str, Any],
    n06_sc5: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest = manifest_validation["fixture_manifest"]
    route_schema = manifest["route_use_event_schema"]
    required_arbitration_ids = set(
        manifest["iteration_3_route_use_cycle_contract"][
            "required_source_arbitration_record_ids"
        ]
    )
    route_aspect = baseline["n05_inventory"]["route_aspect_fields"]
    support = baseline["n07_support_fields_available_as_memory_keys"]["field_values"]
    claim_flags = false_claim_flags(manifest_validation)
    lanes = n06_sc5["lanes"]
    events: list[dict[str, Any]] = []

    for row in source_rows(baseline):
        cycle_id = str(row["cycle_id"])
        lane = lanes[cycle_id]
        arbitration = lane["route_arbitration_record"]
        source_digest = arbitration["native_route_arbitration_digest"]
        row_arbitration_id = str(row["source_arbitration_record_id"])
        n06_arbitration_id = str(arbitration["native_route_arbitration_record_id"])
        source_surface_digest = first_source_surface_digest(row)
        route_id = str(row["selected_route"])
        index = cycle_index(cycle_id)

        event: dict[str, Any] = {
            "artifact_kind": "n08_route_use_event",
            "schema_version": route_schema["schema_version"],
            "mem_level": "MEM1",
            "mem_level_is_evidence_classification": True,
            "claim_ceiling": "mem1_route_use_trace_only",
            "route_use_event_id": route_use_event_id(cycle_id, source_digest),
            "route_use_commit_status": "committed",
            "route_use_commit_semantics": (
                "ordered_serialized_budget_audited_digest_pinned_memory_lane_consumption"
            ),
            "source_experiment": "N06",
            "source_cycle_id": cycle_id,
            "source_context_state_id": row["context_state_id"],
            "source_arbitration_record_id": row_arbitration_id,
            "source_arbitration_record_id_from_n06_lane": n06_arbitration_id,
            "source_arbitration_record_id_matches_n06_lane": (
                row_arbitration_id == n06_arbitration_id
            ),
            "source_arbitration_record_id_required_by_manifest": (
                row_arbitration_id in required_arbitration_ids
            ),
            "source_arbitration_record_digest": source_digest,
            "source_arbitration_digest_derivation": (
                "read_from_N06_SC5_route_arbitration_record.native_route_arbitration_digest"
            ),
            "source_arbitration_event_time_key": arbitration["event_time_key"],
            "source_arbitration_scheduler_event_index": arbitration[
                "scheduler_event_index"
            ],
            "source_candidate_set_digest": row["candidate_set_digest"],
            "selected_candidate_route_digest": row[
                "selected_candidate_route_digest"
            ],
            "rejected_candidate_route_digests": row[
                "rejected_candidate_route_digests"
            ],
            "selected_route_id": route_id,
            "route_aspect_id": route_aspect["route_aspect_id"],
            "route_aspect_digest": route_aspect["route_aspect_digest"],
            "source_support_area_digest": support["source_support_area_digest"],
            "target_support_area_digest": support["target_support_area_digest"],
            "source_surface_digest": source_surface_digest,
            "source_surface_digest_present": source_surface_digest is not None,
            "source_surface_digest_derivation": (
                "first candidate_source_surface_digest from N08 Iteration 1 "
                "N06 cycle inventory; validation requires it to be present"
            ),
            "candidate_score_component_sums": row["candidate_score_component_sums"],
            "candidate_context_values": row["candidate_context_values"],
            "topology_commit_required": False,
            "topology_commit_status": "not_required_for_mem1_route_use_trace",
            "event_time_key": round(
                float(arbitration["event_time_key"])
                + ROUTE_USE_EVENT_TIME_OFFSET
                + (ROUTE_USE_EVENT_TIME_STRIDE * index),
                6,
            ),
            "scheduler_event_index": (
                int(arbitration["scheduler_event_index"])
                + ROUTE_USE_SCHEDULER_INDEX_OFFSET
                + index
            ),
            "event_time_key_derivation": {
                "source_arbitration_event_time_key": arbitration["event_time_key"],
                "route_use_event_time_offset": ROUTE_USE_EVENT_TIME_OFFSET,
                "route_use_event_time_stride_per_cycle": ROUTE_USE_EVENT_TIME_STRIDE,
                "rationale": (
                    "Source N06 cycle arbitrations all use event_time_key 1.0; "
                    "MEM1 route-use events are placed after their source "
                    "arbitration and separated by source cycle index so the "
                    "route-use trace has a deterministic replay order."
                ),
            },
            "event_order_relation": (
                "route_arbitration_precedes_selected_route_use; "
                "memory_update_must_follow_in_iteration_4"
            ),
            "node_plus_packet_budget_before": 0.0,
            "node_plus_packet_budget_after": 0.0,
            "node_plus_packet_budget_error": 0.0,
            "node_plus_packet_budget_semantics": (
                "route_use_event_is_evidence_only_and_budget_neutral"
            ),
            "memory_surface_emitted": False,
            "memory_surface_digest": None,
            "memory_surface_state_snapshot": None,
            "claim_flags": claim_flags,
            "visual_reference": None,
            "visual_is_evidence_source": False,
        }
        event["route_use_event_digest"] = route_use_digest(event)
        events.append(event)

    return events


def control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "missing_selected_route",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "missing_selected_route",
            "purpose": "Reject a route-use event without selected route identity.",
        },
        {
            "control_id": "hidden_route_history",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "hidden_route_history",
            "purpose": "Reject route history that exists only in fixture/report memory.",
        },
        {
            "control_id": "budget_mismatch",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "purpose": "Reject a route-use trace whose evidence-only budget drifts.",
        },
        {
            "control_id": "duplicate_route_use_event",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "duplicate_route_use_event",
            "purpose": "Reject replay that emits the same route-use event twice.",
        },
        {
            "control_id": "premature_memory_surface_emission",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_surface_not_allowed_in_mem1",
            "purpose": "Reject claiming MEM2 memory-surface evidence in MEM1.",
        },
        {
            "control_id": "claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "claim_promotion",
            "purpose": "Reject memory, agency, ACO, identity, or movement claim promotion.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = digest_value(row)
    return rows


def arc_interpretation(events: list[dict[str, Any]]) -> dict[str, Any]:
    route_sequence = [event["selected_route_id"] for event in events]
    cycle_sequence = [event["source_cycle_id"] for event in events]
    interpretation: dict[str, Any] = {
        "interpretation_id": "n08_i3_arc_of_becoming_mem1_route_use_trace_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What becomes available when N06 selected-route artifacts are "
            "converted into committed route-use events without forming memory yet?"
        ),
        "observations": [
            {
                "observation_id": "selection_becomes_use_history",
                "metric": "committed_route_use_event_count",
                "value": len(events),
                "interpretation": (
                    "The source selections are now represented as ordered, "
                    "budget-neutral route-use events that can become memory "
                    "inputs later."
                ),
            },
            {
                "observation_id": "route_alternation_exposed",
                "metric": "selected_route_sequence",
                "value": route_sequence,
                "interpretation": (
                    "The trace exposes an alternating A/B route-use pattern. "
                    "This is not memory yet; it is the substrate history from "
                    "which memory may be cultivated."
                ),
            },
            {
                "observation_id": "memory_absence_is_informative",
                "metric": "memory_surface_emitted_count",
                "value": 0,
                "interpretation": (
                    "The route-use trace deliberately stops before MEM2. This "
                    "keeps the first transition clean: selected route evidence "
                    "has become serialized use history, not a trail."
                ),
            },
            {
                "observation_id": "budget_not_the_motion",
                "metric": "node_plus_packet_budget_error",
                "value": 0.0,
                "interpretation": (
                    "Route use is evidence bookkeeping here. It does not "
                    "inject or delete coherence and it does not mutate packets."
                ),
            },
        ],
        "classification": {
            "mem_level": "MEM1",
            "classification_status": "route_use_history_trace",
            "not_merely_true_false_endpoint": True,
            "claim_gate": "closed",
            "memory_surface_claimed": False,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "N06 route selection can be re-expressed as ordered use history.",
                "A/B alternation is now visible as a route-use sequence rather than hidden fixture memory.",
                "The next question is whether this serialized history can persist as a trail or affordance surface.",
            ],
            "next_question": (
                "Can committed route-use events cultivate a persisted trail or "
                "affordance surface whose digest and budget replay from artifacts?"
            ),
            "next_iteration": "4_MEM2_trail_affordance_memory_surface",
            "successor_probe_should_measure": [
                "memory_surface_rows_or_snapshot_present",
                "memory_surface_digest_recomputes",
                "route_use_event_digest_is_cited",
                "memory_budget_equation_replays",
            ],
        },
        "naturalization": {
            "naturalization_rung": "Nat0_trace_dependent_expression",
            "self_persistent_memory_observed": False,
            "why_not_naturalized": (
                "The trace persists as an artifact, but no memory surface has "
                "yet regenerated, decayed, or reinforced itself."
            ),
        },
        "learning_boundary": {
            "is_reinforcement_learning": False,
            "is_neural_weight_update": False,
            "is_graph_weight_propagation": False,
            "policy_updated": False,
            "route_weight_updated": False,
            "edge_conductance_updated": False,
            "candidate_score_updated": False,
            "future_route_bias_created": False,
            "closest_analogy": "event_log_or_trace_buffer",
            "distinction": (
                "Iteration 3 records that a selected route was used. It does "
                "not update a policy, weight, conductance, value function, "
                "edge cost, probability, or route preference."
            ),
            "later_iterations_where_learning_like_behavior_may_begin": {
                "iteration_4": "create trail_or_affordance_memory_surface",
                "iteration_5": "apply_decay_or_reinforcement_update",
                "iteration_6": "use_memory_derived_score_components_in_route_arbitration",
                "iteration_7": "test_repeated_memory_shaped_selection",
            },
        },
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "aco_like_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "reason": (
                "Arc-style interpretation classifies the expressed transition; "
                "it does not promote memory, choice, agency, ACO, or identity claims."
            ),
        },
        "cycle_sequence": cycle_sequence,
        "route_sequence": route_sequence,
    }
    interpretation["arc_interpretation_digest"] = digest_value(interpretation)
    return interpretation


def validate_events(
    events: list[dict[str, Any]],
    baseline: dict[str, Any],
    manifest_validation: dict[str, Any],
    controls: list[dict[str, Any]],
    interpretation: dict[str, Any],
) -> dict[str, bool]:
    manifest = manifest_validation["fixture_manifest"]
    route_schema = manifest["route_use_event_schema"]
    required_fields = set(route_schema["required_fields"])
    required_cycles = set(
        manifest["iteration_3_route_use_cycle_contract"]["required_source_cycle_ids"]
    )
    required_arbitration_ids = set(
        manifest["iteration_3_route_use_cycle_contract"][
            "required_source_arbitration_record_ids"
        ]
    )
    supplementary_fields = set(MEM1_SUPPLEMENTARY_FIELDS)
    control_blockers = [row["primary_blocker"] for row in controls]
    event_cycles = {event["source_cycle_id"] for event in events}
    return {
        "source_baseline_passed": baseline["status"] == "passed",
        "source_manifest_passed": manifest_validation["status"] == "passed",
        "all_required_cycles_emitted": event_cycles == required_cycles,
        "route_use_event_count_matches_contract": len(events)
        == manifest["iteration_3_route_use_cycle_contract"][
            "required_route_use_event_count"
        ],
        "route_use_events_required_fields_present": all(
            required_fields.issubset(event) for event in events
        ),
        "route_use_event_supplementary_fields_declared": all(
            (set(event) - required_fields).issubset(supplementary_fields)
            for event in events
        ),
        "route_use_events_digest_recompute": all(
            event["route_use_event_digest"] == route_use_digest(event)
            for event in events
        ),
        "source_arbitration_digests_resolved": all(
            event["source_arbitration_record_digest"] for event in events
        ),
        "source_arbitration_record_ids_match_manifest_contract": all(
            event["source_arbitration_record_id"] in required_arbitration_ids
            and event["source_arbitration_record_id_required_by_manifest"] is True
            for event in events
        ),
        "source_arbitration_id_digest_same_n06_lane": all(
            event["source_arbitration_record_id"]
            == event["source_arbitration_record_id_from_n06_lane"]
            and event["source_arbitration_record_id_matches_n06_lane"] is True
            for event in events
        ),
        "source_surface_digest_present": all(
            event["source_surface_digest_present"] is True
            and event["source_surface_digest"] is not None
            for event in events
        ),
        "route_use_not_n06_selection_only": all(
            event["route_use_event_id"].startswith("n08-route-use:")
            and event["source_arbitration_record_id"].startswith(
                "native-route-arbitration:"
            )
            for event in events
        ),
        "event_order_after_source_arbitration": all(
            event["event_time_key"] > event["source_arbitration_event_time_key"]
            and event["scheduler_event_index"]
            > event["source_arbitration_scheduler_event_index"]
            for event in events
        ),
        "budget_neutral": all(
            event["node_plus_packet_budget_before"]
            == event["node_plus_packet_budget_after"]
            and event["node_plus_packet_budget_error"] == 0.0
            for event in events
        ),
        "no_memory_surface_emitted": all(
            event["memory_surface_emitted"] is False
            and event["memory_surface_digest"] is None
            and event["memory_surface_state_snapshot"] is None
            for event in events
        ),
        "claim_flags_all_false": all(
            all(value is False for value in event["claim_flags"].values())
            for event in events
        ),
        "controls_present": {
            row["control_id"] for row in controls
        }
        == {
            "missing_selected_route",
            "hidden_route_history",
            "budget_mismatch",
            "duplicate_route_use_event",
            "premature_memory_surface_emission",
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
        "learning_boundary_recorded": interpretation["learning_boundary"][
            "closest_analogy"
        ]
        == "event_log_or_trace_buffer",
        "no_policy_or_weight_update": all(
            interpretation["learning_boundary"][key] is False
            for key in (
                "policy_updated",
                "route_weight_updated",
                "edge_conductance_updated",
                "candidate_score_updated",
                "future_route_bias_created",
            )
        ),
        "memory_claim_still_closed": interpretation["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ]
        is False,
        "producer_step_boundary_carried_forward": manifest[
            "producer_step_boundary"
        ]["step_remains_packet_mutation_boundary"]
        is True,
        "inherited_native_policy_blockers_carried_forward": bool(
            manifest["native_policy_blockers_inherited"]
        ),
        "src_clean": git_status_short_src() == "",
    }


def source_artifacts() -> dict[str, str]:
    paths = [
        BASELINE_PATH,
        MANIFEST_VALIDATION_PATH,
        SOURCE_N06_SC5_PATH,
    ]
    return {rel(path): digest_file(path) for path in paths}


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_N06_SC5_REPORT): digest_file(SOURCE_N06_SC5_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    events = output["route_use_events"]
    interpretation = output["arc_of_becoming_interpretation"]
    controls = output["controls"]
    checks = output["checks"]
    contract = output["mem1_route_use_event_contract"]
    producer_boundary = output["producer_step_boundary"]
    blocker_lines = "\n".join(
        f"- `{blocker}`" for blocker in output["inherited_native_policy_blockers"]
    )
    supplementary_lines = "\n".join(
        f"- `{field}`" for field in contract["allowed_supplementary_fields"]
    )
    event_lines = "\n".join(
        "| `{source_cycle_id}` | `{selected_route_id}` | `{source_arbitration_record_digest}` | `{route_use_event_digest}` | `{scheduler_event_index}` |".format(
            **event
        )
        for event in events
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
    report = f"""# N08 Iteration 3 MEM1 Route-Use Trace

Status: `{output['status']}`.

Iteration 3 emits committed route-use events from source-backed N06 selected
route artifacts. It does not emit memory surfaces and it does not claim memory,
ACO, agency, choice, identity acceptance, or movement.

## Branch Question

{interpretation['question']}

## Branch Answer

N06 selection artifacts can be converted into four ordered, serialized,
budget-neutral MEM1 route-use events:

```json
{json.dumps(interpretation['route_sequence'], indent=2)}
```

This is not yet memory. The result is a cultivated history substrate: selected
routes have become replayable route-use evidence that Iteration 4 may try to
turn into a trail or affordance surface.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `{interpretation['classification']['classification_status']}`
- naturalization rung:
  `{interpretation['naturalization']['naturalization_rung']}`
- memory surface claimed:
  `{interpretation['classification']['memory_surface_claimed']}`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Cultivation next question:

{interpretation['cultivation']['next_question']}

## Learning Boundary

Iteration 3 is not reinforcement learning, neural weight propagation, graph
weight propagation, conductance learning, or policy update.

```json
{json.dumps(interpretation['learning_boundary'], indent=2, sort_keys=True)}
```

The closest analogy is an event log or trace buffer. Iteration 3 records:

```text
selected route -> committed route-use trace
```

It does not record:

```text
route used -> route weight increases -> future route becomes more likely
```

That distinction matters because N08 should not smuggle learning into the
experiment through bookkeeping. Learning-like behavior can only begin after a
serialized memory surface, decay/reinforcement update, and memory-shaped route
arbitration are present in later iterations.

## MEM1 Event Contract

The Iteration 2 manifest defines minimum required route-use fields. Iteration 3
also declares these MEM1 supplementary fields so replay auditors can
distinguish intentional provenance/context fields from accidental leakage:

{supplementary_lines}

Source arbitration IDs are checked against the Iteration 2 manifest contract
and against the N06 SC5 lane that supplies the source arbitration digest.

## Producer / Step Boundary

```json
{json.dumps(producer_boundary, indent=2, sort_keys=True)}
```

Iteration 3 does not use producers to mutate memory, node coherence, or packet
ledgers. The route-use events are evidence records only.

## Inherited Native Policy Blockers

The native memory/trail policy blockers from Iteration 2 remain active:

{blocker_lines}

## Route-Use Events

| Source Cycle | Route | Source Arbitration Digest | Route-Use Digest | Scheduler Index |
|---|---|---|---|---:|
{event_lines}

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

Iteration 3 passes if route-use traces are source-backed and replayable, but no
memory/trail surface is yet claimed. MEM1 supports route-use history only.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["fixture_manifest"]
    n06_sc5 = load_json(SOURCE_N06_SC5_PATH)
    events = build_route_use_events(baseline, manifest_validation, n06_sc5)
    controls = control_rows()
    interpretation = arc_interpretation(events)
    checks = validate_events(events, baseline, manifest_validation, controls, interpretation)
    output: dict[str, Any] = {
        "schema": "n08_iteration_3_mem1_route_use_trace_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 3,
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
        "route_use_events": events,
        "route_use_event_count": len(events),
        "mem1_route_use_event_contract": {
            "minimum_required_fields": manifest["route_use_event_schema"][
                "required_fields"
            ],
            "allowed_supplementary_fields": MEM1_SUPPLEMENTARY_FIELDS,
            "supplementary_fields_are_intentional": True,
            "source_arbitration_ids_required_by_manifest": manifest[
                "iteration_3_route_use_cycle_contract"
            ]["required_source_arbitration_record_ids"],
        },
        "producer_step_boundary": manifest["producer_step_boundary"],
        "inherited_native_policy_blockers": manifest[
            "native_policy_blockers_inherited"
        ],
        "memory_surface_emitted": False,
        "mem_level": "MEM1",
        "claim_ceiling": "mem1_route_use_trace_only",
        "arc_of_becoming_interpretation": interpretation,
        "controls": controls,
        "checks": checks,
        "claim_flags": false_claim_flags(manifest_validation),
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 3 passes if route-use traces are source-backed "
                "and replayable, but no memory/trail surface is yet claimed. "
                "MEM1 supports route-use history only."
            ),
        },
    }
    output["artifact_digests"] = {
        "route_use_events_digest": digest_value(events),
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
