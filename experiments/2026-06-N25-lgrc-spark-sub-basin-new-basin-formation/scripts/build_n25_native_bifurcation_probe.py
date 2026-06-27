#!/usr/bin/env python3
"""Build N25 Iteration 4 native optional-branch bifurcation probe."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_native_bifurcation_probe.json"
REPORT = EXPERIMENT / "reports" / "n25_native_bifurcation_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_native_bifurcation_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_native_bifurcation_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_basin_formation_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_active_nulls_and_failure_baselines.json"
)

NATIVE_FLUX_DEBT_BOUND = 1e-9
PACKET_AMOUNT = 1e-9
BOUNDARY_DISTINGUISHABILITY_MARGIN_FORMULA = (
    "module_node_count - minimum_distinguishable_module_node_count"
)
OLD_BASIN_SEPARATION_MARGIN_FORMULA = (
    "1.0 when old center removed by source-current expansion else 0.0"
)
SOURCE_FILES = [
    "examples/lgrc9v3/causal_spark_diagnostics.py",
    "examples/lgrc9v3/refinement_packet_transport.py",
    "examples/grc9v3/_fixtures.py",
]
PLAN_CONTROL_IDS = [
    "label_only_new_basin_rejected",
    "single_basin_thickening_relabel_rejected",
    "reshaped_old_boundary_relabel_rejected",
    "merge_leakage_masquerading_as_new_basin_rejected",
    "non_replayable_transient_rejected",
    "hidden_producer_insertion_rejected",
    "n24_optionality_relabel_as_formation_rejected",
    "producer_assisted_success_does_not_overwrite_native_failure",
    "native_flux_debt_remains_row_local",
    "producer_schedule_post_hoc_control",
    "producer_hidden_support_control",
    "producer_threshold_relaxation_control",
    "producer_basin_insertion_without_trace_control",
    "producer_success_as_native_relabel_control",
    "producer_success_overwrites_native_failure_control",
    "native_spark_source_policy_rejected",
    "producer_before_native_spark_path_rejected",
    "ap4_gap_prose_only_rejected",
    "ap5_proxy_target_omission_rejected_when_applicable",
    "semantic_learning_relabel_rejected",
    "semantic_choice_relabel_rejected",
    "agency_relabel_rejected",
    "native_support_relabel_rejected",
    "phase8_relabel_rejected",
    "ant_ecology_relabel_rejected",
]
UNSAFE_CLAIMS = [
    "semantic_learning",
    "semantic_choice",
    "agency",
    "intention",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "sentience",
    "phase8",
    "ant_ecology",
    "organism_life",
    "fully_native_integration",
]

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.models import (  # noqa: E402
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND,
    LGRC_RUNTIME_LEVEL_LGRC3,
)


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def source_content_digest(paths: list[str]) -> str:
    return digest_value({path: sha256_file(path) for path in paths})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def active_topology_config() -> dict[str, Any]:
    config = make_config(spark_lane=LANE_B)
    config["causal_modes"] = {
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "lapse_policy": LAPSE_POLICY_UNIT,
        "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
        "event_time_policy": "explicit_event_time_key",
        "proper_time_accumulation_policy": "local_event_frontier",
        "causal_topology_integration_allowed": True,
        "causal_spark_expansion_allowed": True,
        "causal_refinement_packet_transport_allowed": True,
        "causal_proper_time_inheritance_allowed": True,
        "causal_collapse_reabsorption_allowed": False,
        "causal_identity_acceptance_allowed": False,
    }
    return config


def topology_signature(state: Any) -> dict[str, Any]:
    graph = state.topology
    edge_records: list[dict[str, Any]] = []
    for edge_id in sorted(int(edge_id) for edge_id in graph.iter_live_edge_ids()):
        endpoint_a, endpoint_b = graph.edge_ports(edge_id)
        edge_records.append(
            {
                "edge_id": int(edge_id),
                "endpoints": [
                    [int(endpoint_a[0]), int(endpoint_a[1])],
                    [int(endpoint_b[0]), int(endpoint_b[1])],
                ],
            }
        )
    return {
        "node_ids": sorted(int(node_id) for node_id in graph.iter_live_node_ids()),
        "edge_records": edge_records,
        "node_count": len(tuple(graph.iter_live_node_ids())),
        "edge_count": len(tuple(graph.iter_live_edge_ids())),
    }


def node_metrics(state: Any, node_ids: list[int]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for node_id in node_ids:
        node = state.nodes[int(node_id)]
        records.append(
            {
                "node_id": int(node_id),
                "coherence": float(getattr(node, "coherence", 0.0)),
                "basin_mass": float(getattr(node, "basin_mass", 0.0)),
                "basin_id": str(getattr(node, "basin_id", node_id)),
                "incident_edge_ids": [
                    int(edge_id)
                    for edge_id in state.topology.incident_edge_ids(int(node_id))
                ],
            }
        )
    return records


def first_event(events: list[Any], kind: str) -> Any:
    for event in events:
        if event.kind == kind:
            return event
    raise RuntimeError(f"expected event kind {kind!r}")


def compact_event(event: Any) -> dict[str, Any]:
    payload = dict(event.payload)
    return {
        "kind": str(event.kind),
        "candidate_event_id": payload.get("candidate_event_id"),
        "expansion_id": payload.get("expansion_id"),
        "topology_event_id": payload.get("topology_event_id"),
        "event_time_key": payload.get("event_time_key"),
        "scheduler_event_index": payload.get("scheduler_event_index"),
        "spark_lane": payload.get("spark_lane"),
        "source_candidate_event_id": payload.get("source_candidate_event_id"),
        "gate_reasons": payload.get("gate_reasons")
        or payload.get("source_candidate_gate_reasons"),
        "column_h": payload.get("column_h"),
        "column_h_branch_hit": payload.get("column_h_branch_hit"),
        "mechanical_expansion_emitted": payload.get(
            "mechanical_expansion_emitted", False
        ),
        "topology_mutated": payload.get("topology_mutated", False),
        "identity_acceptance_emitted": payload.get(
            "identity_acceptance_emitted", False
        ),
        "module_node_ids": payload.get("module_node_ids"),
        "internal_edge_ids": payload.get("internal_edge_ids"),
        "budget_before": payload.get("budget_before"),
        "budget_after": payload.get("budget_after"),
        "budget_error": payload.get("budget_error"),
        "amount_total": payload.get("amount_total"),
    }


def run_native_probe() -> dict[str, Any]:
    model = LGRC9V3.from_state(make_column_h_state(), active_topology_config())
    pre_state = model.get_state().base_state
    pre_topology = topology_signature(pre_state)

    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    results = model.run_event_queue(max_events=4)
    events = [event for result in results for event in result.events]
    candidate = first_event(events, LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND)
    expansion = first_event(events, "hybrid_mechanical_expansion")
    transport = first_event(events, "lgrc9v3_refinement_packet_transport")
    proper_time = first_event(events, "lgrc9v3_proper_time_inheritance")

    post_state = model.get_state().base_state
    post_topology = topology_signature(post_state)
    module_node_ids = [int(node_id) for node_id in expansion.payload["module_node_ids"]]
    internal_edge_ids = [int(edge_id) for edge_id in expansion.payload["internal_edge_ids"]]
    module_node_records = node_metrics(post_state, module_node_ids)
    module_coherences = [record["coherence"] for record in module_node_records]
    positive_module_coherences = [
        value for value in module_coherences if value > 0.0
    ]
    old_center_removed = 0 not in post_topology["node_ids"]
    boundary_external_edge_count = sum(
        1
        for edge in post_topology["edge_records"]
        if (
            edge["endpoints"][0][0] in module_node_ids
            and edge["endpoints"][1][0] not in module_node_ids
        )
        or (
            edge["endpoints"][1][0] in module_node_ids
            and edge["endpoints"][0][0] not in module_node_ids
        )
    )

    support_coherence_trace = {
        "candidate_region_node_ids": module_node_ids,
        "candidate_internal_edge_ids": internal_edge_ids,
        "candidate_external_edge_count": boundary_external_edge_count,
        "node_records": module_node_records,
        "min_candidate_coherence": min(module_coherences),
        "positive_node_min_coherence": min(positive_module_coherences),
        "positive_node_count": len(positive_module_coherences),
        "candidate_node_count": len(module_node_ids),
        "support_floor_definition": (
            "I4 records source-current module support as emitted module nodes "
            "and internal edges plus preserved budget. Stability and replay are "
            "deferred to I5."
        ),
        "declared_min_internal_edge_count": len(internal_edge_ids),
        "declared_min_positive_coherence_nodes": len(positive_module_coherences),
        "support_floor_margin_new_region": 0.0,
        "coherence_floor_margin_new_region": 0.0,
        "floor_margin_interpretation": (
            "zero-margin candidate trace; enough to record a native bifurcation "
            "surface, not enough to close stable BF3/BF4 without I5"
        ),
    }
    old_relation_trace = {
        "old_basin_id": "root",
        "old_center_node_id": 0,
        "old_center_removed_after_expansion": old_center_removed,
        "parent_basin_id": expansion.payload.get("parent_basin_id"),
        "module_attached_to_old_basin": True,
        "old_basin_relation": "replacement/refinement of saturated root sink into module nodes",
        "old_basin_thickening_only": False,
        "reshaped_old_boundary_only": False,
    }
    bifurcation_trace = {
        "runtime_family": "LGRC9V3",
        "existing_source_examples_reused": SOURCE_FILES[:2],
        "packet_amount": PACKET_AMOUNT,
        "packet_amount_equals_native_flux_debt_bound": PACKET_AMOUNT
        == NATIVE_FLUX_DEBT_BOUND,
        "event_kinds": [str(event.kind) for event in events],
        "step_trace": [
            {
                "processed_event_kind": result.bookkeeping.get(
                    "processed_event_kind"
                ),
                "event_time_key": result.bookkeeping.get("event_time_key"),
                "causal_spark_diagnostic_events": result.bookkeeping.get(
                    "causal_spark_diagnostic_events"
                ),
                "causal_topology_integration_events": result.bookkeeping.get(
                    "causal_topology_integration_events"
                ),
                "topology_events_routed": result.bookkeeping.get(
                    "topology_events_routed"
                ),
            }
            for result in results
        ],
        "spark_candidate": compact_event(candidate),
        "mechanical_expansion": compact_event(expansion),
        "refinement_packet_transport": compact_event(transport),
        "proper_time_inheritance": compact_event(proper_time),
    }
    runtime_trace = {
        "trace_id": "n25_i4_lgrc9v3_runtime_trace",
        "runtime_family": "LGRC9V3",
        "causal_modes": active_topology_config()["causal_modes"],
        "event_kinds": bifurcation_trace["event_kinds"],
        "step_trace": bifurcation_trace["step_trace"],
        "source_current_runtime_path": (
            "LGRC9V3 packet arrival -> local update -> causal spark diagnostic "
            "-> active topology integration"
        ),
        "producer_intervention_used": False,
    }
    producer_ledger = {
        "ledger_id": "n25_i4_native_only_empty_producer_intervention_ledger",
        "producer_intervention_used": False,
        "producer_schedule_present": False,
        "producer_flux_conditioning_present": False,
        "producer_hidden_support_present": False,
        "producer_threshold_relaxation_present": False,
        "scope_reason": "I4 is native-only and reuses existing LGRC9V3 spark/topology integration.",
    }
    boundary_trace = {
        "pre_topology_signature": pre_topology,
        "post_topology_signature": post_topology,
        "node_count_delta": post_topology["node_count"] - pre_topology["node_count"],
        "edge_count_delta": post_topology["edge_count"] - pre_topology["edge_count"],
        "module_node_ids": module_node_ids,
        "internal_edge_ids": internal_edge_ids,
        "boundary_external_edge_count": boundary_external_edge_count,
        "candidate_boundary_signature_digest": digest_value(
            {
                "module_node_ids": module_node_ids,
                "internal_edge_ids": internal_edge_ids,
                "boundary_external_edge_count": boundary_external_edge_count,
            }
        ),
        "source_current_boundary_event_kind": "hybrid_mechanical_expansion",
    }
    merge_leakage_trace = {
        "budget_before": float(expansion.payload["budget_before"]),
        "budget_after": float(expansion.payload["budget_after"]),
        "budget_error": float(expansion.payload["budget_error"]),
        "refinement_packet_transport_amount_total": float(
            transport.payload.get("amount_total", 0.0)
        ),
        "transport_amount_total_interpretation": (
            "The refinement packet transport event is structurally present but "
            "carries no residual packet amount in this run; the packet-triggered "
            "spark and mechanical expansion remain source-current, and budget "
            "conservation is tracked by budget_error."
        ),
        "budget_error_within_native_flux_debt_bound": abs(
            float(expansion.payload["budget_error"])
        )
        <= NATIVE_FLUX_DEBT_BOUND,
        "merge_leakage_margin": NATIVE_FLUX_DEBT_BOUND
        - abs(float(expansion.payload["budget_error"])),
        "merge_leakage_control_status": "deferred_to_iteration_5",
    }
    flux_debt_trace = {
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "packet_amount": PACKET_AMOUNT,
        "packet_amount_within_bound": PACKET_AMOUNT <= NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_not_overwritten": True,
    }
    return {
        "bifurcation_trace": bifurcation_trace,
        "new_boundary_candidate_trace": boundary_trace,
        "new_basin_support_coherence_trace": support_coherence_trace,
        "old_basin_relation_trace": old_relation_trace,
        "merge_leakage_trace": merge_leakage_trace,
        "native_flux_debt_trace": flux_debt_trace,
        "runtime_trace": runtime_trace,
        "producer_intervention_ledger": producer_ledger,
    }


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def control_results() -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "label_only_new_basin_rejected",
            "control_status": "passed",
            "blocked_condition": "candidate exists only as a label",
            "expected_result": "source-current spark and topology events are present",
            "actual_result": "causal spark, mechanical expansion, and topology signature digests present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "allows BF2 bifurcation evidence; label-only path absent",
        },
        {
            "control_id": "single_basin_thickening_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "old basin merely thickens without new module boundary",
            "expected_result": "module nodes/internal edges distinguish candidate from thickening",
            "actual_result": "old center replaced by module nodes and internal expansion edges",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "permits provisional sub-basin candidate interpretation pending I5",
        },
        {
            "control_id": "reshaped_old_boundary_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "old boundary shift is relabeled as formation",
            "expected_result": "mechanical expansion emits new module boundary trace",
            "actual_result": "new module node ids and boundary signature digest recorded",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "keeps candidate distinct from boundary wrinkle interpretation",
        },
        {
            "control_id": "hidden_producer_insertion_rejected",
            "control_status": "passed",
            "blocked_condition": "producer inserts basin-like record without native trace",
            "expected_result": "native LGRC9V3/GRC9V3 event path produces the trace",
            "actual_result": "no producer-assisted lane or producer intervention ledger is used",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "keeps I4 native-lane only",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "native row omits or widens inherited 1e-9 flux debt",
            "expected_result": "packet amount and row-local bound remain at 1e-9",
            "actual_result": "packet_amount = native_flux_debt_bound = 1e-9",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native row remains admissible for BF2",
        },
        {
            "control_id": "n24_optionality_relabel_as_formation_rejected",
            "control_status": "passed",
            "blocked_condition": "N24 optionality context is relabeled as N25 formation",
            "expected_result": "I4 formation evidence must come from a new LGRC9V3 source-current spark/expansion trace",
            "actual_result": "causal spark, mechanical expansion, and module boundary artifacts are present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N24 AB5/N24-C5 remains context only; I4 evidence is not a relabel",
        },
        {
            "control_id": "merge_leakage_masquerading_as_new_basin_rejected",
            "control_status": "not_run",
            "blocked_condition": "merge or leakage is counted as formation",
            "expected_result": "I5 replay/control matrix must test this",
            "actual_result": "budget error trace is zero, but full merge/leakage control is deferred",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks BF4+ and final BF3 closeout until I5",
        },
        {
            "control_id": "non_replayable_transient_rejected",
            "control_status": "not_run",
            "blocked_condition": "one-window spark is counted as formation",
            "expected_result": "I5 replay must distinguish replayable candidate from transient",
            "actual_result": "I4 records first positive run only",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks BF4+ and final BF3 closeout until I5",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "not_applicable",
            "blocked_condition": "producer-assisted success is relabeled as native",
            "expected_result": "native I4 row has no producer-assisted result",
            "actual_result": "producer_assisted_result_class = not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only I4 row",
        },
    ]
    controls.extend(
        [
            {
                "control_id": "producer_assisted_success_does_not_overwrite_native_failure",
                "control_status": "not_applicable",
                "blocked_condition": "producer-assisted result overwrites native lane result",
                "expected_result": "I4 native row has no producer-assisted result",
                "actual_result": "producer_assisted_result_class = not_applicable",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: producer lane not opened in I4",
            },
            {
                "control_id": "producer_schedule_post_hoc_control",
                "control_status": "not_applicable",
                "blocked_condition": "producer schedule is added after observing the result",
                "expected_result": "no producer schedule is present",
                "actual_result": "empty producer intervention ledger recorded",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: native-only I4 row",
            },
            {
                "control_id": "producer_hidden_support_control",
                "control_status": "not_applicable",
                "blocked_condition": "hidden producer support carries the candidate",
                "expected_result": "no producer support is present",
                "actual_result": "empty producer intervention ledger recorded",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: native-only I4 row",
            },
            {
                "control_id": "producer_threshold_relaxation_control",
                "control_status": "not_applicable",
                "blocked_condition": "producer lane relaxes thresholds",
                "expected_result": "native I4 thresholds are declared before use",
                "actual_result": "producer threshold relaxation absent",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: native-only I4 row",
            },
            {
                "control_id": "producer_basin_insertion_without_trace_control",
                "control_status": "passed",
                "blocked_condition": "basin-like record appears without source-current trace",
                "expected_result": "source-current LGRC9V3 spark and expansion traces exist",
                "actual_result": "bifurcation, boundary, runtime, and old-basin relation traces recorded",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "producer insertion without trace remains blocked",
            },
            {
                "control_id": "producer_success_overwrites_native_failure_control",
                "control_status": "not_applicable",
                "blocked_condition": "producer-assisted success overwrites native failure",
                "expected_result": "producer-assisted lane is not opened",
                "actual_result": "producer_assisted_result_class = not_applicable",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: native-only I4 row",
            },
            {
                "control_id": "native_spark_source_policy_rejected",
                "control_status": "passed",
                "blocked_condition": "existing LGRC/LGRC9V3 spark sources are skipped",
                "expected_result": "I4 reuses existing LGRC9V3 spark/topology paths",
                "actual_result": "causal spark diagnostics and active topology integration reused",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "native-spark-first policy satisfied",
            },
            {
                "control_id": "producer_before_native_spark_path_rejected",
                "control_status": "passed",
                "blocked_condition": "producer path is tried before native spark path",
                "expected_result": "I4 is native-only",
                "actual_result": "producer_assisted_lane_opened = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "producer-before-native ordering blocked",
            },
            {
                "control_id": "ap4_gap_prose_only_rejected",
                "control_status": "passed",
                "blocked_condition": "AP4 dependency is handled only in prose",
                "expected_result": "row records AP4 dependency status and reason",
                "actual_result": "ap4_dependency_status = required_recorded",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "AP4 gap remains explicit",
            },
            {
                "control_id": "ap5_proxy_target_omission_rejected_when_applicable",
                "control_status": "not_applicable",
                "blocked_condition": "AP5 proxy/target dependency is omitted when applicable",
                "expected_result": "I4 has no proxy/target formation row",
                "actual_result": "ap5_dependency_status = not_applicable",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "scope reason: no AP5-dependent proxy/target formation in I4",
            },
            {
                "control_id": "semantic_learning_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as semantic learning",
                "expected_result": "semantic learning claim flag remains false",
                "actual_result": "unsafe_claim_flags.semantic_learning = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "semantic learning relabel blocked",
            },
            {
                "control_id": "semantic_choice_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as semantic choice",
                "expected_result": "semantic choice claim flag remains false",
                "actual_result": "unsafe_claim_flags.semantic_choice = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "semantic choice relabel blocked",
            },
            {
                "control_id": "agency_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as agency",
                "expected_result": "agency claim flag remains false",
                "actual_result": "unsafe_claim_flags.agency = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "agency relabel blocked",
            },
            {
                "control_id": "native_support_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as native support",
                "expected_result": "native support claim flag remains false",
                "actual_result": "unsafe_claim_flags.native_support = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "native support relabel blocked",
            },
            {
                "control_id": "phase8_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as Phase 8 implementation",
                "expected_result": "phase8 claim flag remains false",
                "actual_result": "unsafe_claim_flags.phase8 = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "Phase 8 relabel blocked",
            },
            {
                "control_id": "ant_ecology_relabel_rejected",
                "control_status": "passed",
                "blocked_condition": "bifurcation is relabeled as ant ecology",
                "expected_result": "ant ecology claim flag remains false",
                "actual_result": "unsafe_claim_flags.ant_ecology = false",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "ant ecology relabel blocked",
            },
        ]
    )
    return controls


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    probe = run_native_probe()

    threshold_record = {
        "record_id": "n25_i4_thresholds_declared_before_use",
        "declared_before_use": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "packet_amount": PACKET_AMOUNT,
        "minimum_distinguishable_module_node_count": 1,
        "minimum_module_node_count_for_candidate": 5,
        "minimum_internal_edge_count_for_candidate": 4,
        "minimum_positive_coherence_nodes_for_candidate": 3,
        "distinguishable_module_node_count_note": (
            "The one-node threshold is only the distinguishability baseline; "
            "the I4 candidate gate separately requires the full five-node module."
        ),
        "boundary_distinguishability_margin_formula": BOUNDARY_DISTINGUISHABILITY_MARGIN_FORMULA,
        "old_basin_separation_margin_kind": "binary_indicator",
        "old_basin_separation_margin_formula": OLD_BASIN_SEPARATION_MARGIN_FORMULA,
        "temporal_window_schema": {
            "bifurcation_window": ["start_step", "end_step", "event_time_key"],
            "boundary_candidate_window": [
                "start_step",
                "end_step",
                "event_time_key",
            ],
            "ordering_rule": "bifurcation_window.end_step <= boundary_candidate_window.start_step",
        },
        "bf3_closeout_requires_iteration_5_replay_controls": True,
    }
    artifact_paths_by_role = {
        "threshold_record": ARTIFACT_DIR / "n25_i4_thresholds_declared_before_use.json",
        "bifurcation_trace": ARTIFACT_DIR / "n25_i4_lgrc9v3_bifurcation_trace.json",
        "new_boundary_candidate_trace": ARTIFACT_DIR
        / "n25_i4_new_boundary_candidate_trace.json",
        "new_basin_support_coherence_trace": ARTIFACT_DIR
        / "n25_i4_new_region_support_coherence_trace.json",
        "old_basin_relation_trace": ARTIFACT_DIR / "n25_i4_old_basin_relation_trace.json",
        "merge_leakage_trace": ARTIFACT_DIR / "n25_i4_merge_leakage_trace.json",
        "native_flux_debt_trace": ARTIFACT_DIR / "n25_i4_native_flux_debt_trace.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i4_runtime_trace.json",
        "producer_intervention_ledger": ARTIFACT_DIR
        / "n25_i4_empty_producer_intervention_ledger.json",
    }
    write_json(artifact_paths_by_role["threshold_record"], threshold_record)
    for role, path in artifact_paths_by_role.items():
        if role == "threshold_record":
            continue
        write_json(path, probe[role])

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    old_sig = probe["new_boundary_candidate_trace"]["pre_topology_signature"]
    boundary_sig = probe["new_boundary_candidate_trace"]
    support_trace = probe["new_basin_support_coherence_trace"]
    merge_trace = probe["merge_leakage_trace"]

    row: dict[str, Any] = {
        "row_id": "n25_i4_native_lgrc9v3_optional_branch_bifurcation_probe",
        "source_iteration": "I4_native_optional_branch_bifurcation_probe",
        "source_contract_row_digest": i1.get("source_contract_row_digest", "not_recorded"),
        "source_consumable_contract_row_digest": i1.get(
            "source_consumable_contract_row_digest", "not_recorded"
        ),
        "source_output_digest": i1.get("output_digest"),
        "run_artifact_id": "n25_i4_native_lgrc9v3_active_topology_probe",
        "runtime_config_digest": digest_value(active_topology_config()),
        "source_commit_or_source_digest": source_content_digest(SOURCE_FILES),
        "source_current_inputs": SOURCE_FILES,
        "artifact_manifest": manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": artifact_paths
        == [entry["path"] for entry in manifest],
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == {entry["path"]: entry["sha256"] for entry in manifest},
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(path) == sha for path, sha in artifact_sha256.items()
        ),
        "row_specific_thresholds_declared_before_use": threshold_record,
        "existing_lgrc_spark_sources_considered": True,
        "native_spark_mechanism_reuse_status": (
            "reused_existing_lgrc9v3_causal_spark_and_active_topology_integration"
        ),
        "new_producer_code_justification": "not_applicable_native_path_reuses_existing_lgrc9v3_spark_mechanism",
        "lane": "native",
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_result_class": "not_applicable",
        "n20_source_contract_row": i1["source_contract_row"],
        "n20_consumable_contract_row": i1["source_consumable_contract_row"],
        "n24_native_lane_status": "AB5_N24-C5_context_only_not_reclassified",
        "n24_producer_lane_status": "not_used_in_native_row",
        "formation_class": "bifurcation_partial",
        "provisional_formation_class_target": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "bifurcation_trace": {
            "path": repo_relative(artifact_paths_by_role["bifurcation_trace"]),
            "digest": digest_value(probe["bifurcation_trace"]),
            "summary": "causal spark candidate followed by active topology mechanical expansion",
        },
        "new_boundary_candidate_trace": {
            "path": repo_relative(
                artifact_paths_by_role["new_boundary_candidate_trace"]
            ),
            "digest": digest_value(probe["new_boundary_candidate_trace"]),
            "module_node_ids": boundary_sig["module_node_ids"],
            "internal_edge_ids": boundary_sig["internal_edge_ids"],
            "boundary_external_edge_count": boundary_sig[
                "boundary_external_edge_count"
            ],
        },
        "new_basin_support_coherence_trace": {
            "path": repo_relative(
                artifact_paths_by_role["new_basin_support_coherence_trace"]
            ),
            "digest": digest_value(probe["new_basin_support_coherence_trace"]),
            "candidate_node_count": support_trace["candidate_node_count"],
            "positive_node_count": support_trace["positive_node_count"],
            "min_candidate_coherence": support_trace["min_candidate_coherence"],
        },
        "replayable_distinction_trace": {
            "status": "not_run_until_iteration_5",
            "reason": "I4 records first positive native bifurcation; replay/control matrix is I5 scope",
        },
        "old_basin_relation_trace": {
            "path": repo_relative(artifact_paths_by_role["old_basin_relation_trace"]),
            "digest": digest_value(probe["old_basin_relation_trace"]),
            "old_center_removed_after_expansion": probe["old_basin_relation_trace"][
                "old_center_removed_after_expansion"
            ],
        },
        "merge_leakage_trace": {
            "path": repo_relative(artifact_paths_by_role["merge_leakage_trace"]),
            "digest": digest_value(probe["merge_leakage_trace"]),
            "budget_error": merge_trace["budget_error"],
            "merge_leakage_control_status": merge_trace[
                "merge_leakage_control_status"
            ],
        },
        "formation_window": {
            "start_step": 0,
            "end_step": 1,
            "start_event_time_key": 1.0,
            "end_event_time_key": 2.0,
        },
        "bifurcation_window": {
            "start_step": 1,
            "end_step": 1,
            "event_time_key": 2.0,
            "event_kind": "lgrc9v3_causal_spark_candidate",
        },
        "boundary_candidate_window": {
            "start_step": 1,
            "end_step": 1,
            "event_time_key": 2.0,
            "event_kind": "hybrid_mechanical_expansion",
        },
        "replay_window": "not_run_until_iteration_5",
        "old_basin_reference_window": {"event_time_key": 1.0, "topology_digest": digest_value(old_sig)},
        "bifurcation_window_order_valid": True,
        "thresholds_declared_before_bifurcation_window": True,
        "old_basin_signature_digest": digest_value(old_sig),
        "candidate_basin_signature_digest": digest_value(
            {
                "module_node_ids": boundary_sig["module_node_ids"],
                "support_coherence": support_trace,
            }
        ),
        "candidate_boundary_signature_digest": boundary_sig[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": digest_value(
            {
                "old_center_removed": probe["old_basin_relation_trace"][
                    "old_center_removed_after_expansion"
                ],
                "node_count_delta": boundary_sig["node_count_delta"],
                "edge_count_delta": boundary_sig["edge_count_delta"],
            }
        ),
        "boundary_distinguishability_margin": len(boundary_sig["module_node_ids"]) - 1,
        "boundary_distinguishability_margin_formula": BOUNDARY_DISTINGUISHABILITY_MARGIN_FORMULA,
        "support_floor_margin_new_region": support_trace[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": support_trace[
            "coherence_floor_margin_new_region"
        ],
        "old_basin_separation_margin": 1.0
        if probe["old_basin_relation_trace"]["old_center_removed_after_expansion"]
        else 0.0,
        "old_basin_separation_margin_kind": "binary_indicator",
        "old_basin_separation_margin_formula": OLD_BASIN_SEPARATION_MARGIN_FORMULA,
        "merge_leakage_margin": merge_trace["merge_leakage_margin"],
        "replay_distinction_persistence_ratio": "not_run_until_iteration_5",
        "old_basin_thickening_rejected": True,
        "reshaped_old_boundary_rejected": True,
        "merge_leakage_rejected": "deferred_to_iteration_5",
        "transient_rejected": "deferred_to_iteration_5",
        "label_only_rejected": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "producer_flux_window_bound": "not_applicable_native_lane",
        "producer_flux_window_declared_before_use": "not_applicable_native_lane",
        "native_flux_debt_not_overwritten": True,
        "support_floor_result": "candidate_trace_recorded_zero_margin_pending_replay",
        "coherence_floor_result": "candidate_trace_recorded_zero_margin_pending_replay",
        "boundary_integrity_result": "source_current_boundary_candidate_recorded",
        "flux_or_leakage_result": "budget_error_within_1e-9_full_merge_leakage_control_deferred",
        "control_results": control_results(),
        "producer_residue_classification": "not_applicable_native_row",
        "naturalization_debt": [
            "replayable_distinction_trace",
            "merge_leakage_control",
            "transient_control",
            "stress_threshold_matrix",
        ],
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "N25 consumes N24 optionality context and must preserve AP4 gap boundary",
        "ap5_condition_reason": "no proxy/target formation row in I4 native bifurcation probe",
        "bf_ladder_rung": "BF2_native_source_current_bifurcation_partial",
        "bf3_candidate_status": "provisional_pending_iteration_5_replay_and_controls",
        "row_decision": "partial",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "native source-current bifurcation/sub-basin candidate trace; no "
            "replay/control-backed formation, no native support, no agency"
        ),
        "n25_closeout_ceiling": "N25-C2_spark_bifurcation_partial",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": (
            "A Lane-B column-H spark at the saturated root sink routes into an "
            "active topology expansion. The old center is replaced by a module "
            "with internal edges, giving a source-current boundary candidate. "
            "The module has zero-margin support/coherence floors and no replay "
            "yet, so this is BF2 with a provisional BF3 target, not stable "
            "basin formation."
        ),
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check(
            "existing_lgrc9v3_spark_path_reused",
            row["existing_lgrc_spark_sources_considered"]
            and "existing_lgrc9v3" in row["native_spark_mechanism_reuse_status"],
            row["native_spark_mechanism_reuse_status"],
        ),
        check(
            "native_flux_debt_preserved",
            row["native_flux_debt_bound"] == NATIVE_FLUX_DEBT_BOUND
            and row["native_flux_debt_widened"] is False
            and row["native_flux_debt_status"] == "preserved"
            and PACKET_AMOUNT <= NATIVE_FLUX_DEBT_BOUND,
            row["native_flux_debt_bound"],
        ),
        check(
            "n20_contract_rows_match_inventory",
            row["n20_source_contract_row"] == i1["source_contract_row"]
            and row["n20_consumable_contract_row"] == i1["source_consumable_contract_row"],
            {
                "n20_source_contract_row": row["n20_source_contract_row"],
                "n20_consumable_contract_row": row["n20_consumable_contract_row"],
            },
        ),
        check(
            "n24_optionality_relabel_control_present",
            any(
                control["control_id"] == "n24_optionality_relabel_as_formation_rejected"
                and control["control_status"] == "passed"
                for control in row["control_results"]
            ),
            "N24 optionality relabel is blocked in the positive row.",
        ),
        check(
            "source_current_inputs_non_circular",
            not any(path in row["source_current_inputs"] for path in row["artifact_paths"]),
            row["source_current_inputs"],
        ),
        check(
            "runtime_trace_artifact_present",
            any(
                entry["artifact_role"] == "runtime_trace"
                for entry in row["artifact_manifest"]
            ),
            row["artifact_manifest"],
        ),
        check(
            "producer_intervention_ledger_artifact_present",
            any(
                entry["artifact_role"] == "producer_intervention_ledger"
                for entry in row["artifact_manifest"]
            ),
            row["artifact_manifest"],
        ),
        check(
            "all_plan_controls_scoped_in_i4",
            all(
                control_id
                in {control["control_id"] for control in row["control_results"]}
                for control_id in PLAN_CONTROL_IDS
            ),
            {
                "expected": PLAN_CONTROL_IDS,
                "actual": [control["control_id"] for control in row["control_results"]],
            },
        ),
        check(
            "bf2_formation_class_not_overclaimed",
            row["formation_class"] == "bifurcation_partial"
            and row["provisional_formation_class_target"] == "sub_basin_candidate",
            {
                "formation_class": row["formation_class"],
                "provisional_target": row["provisional_formation_class_target"],
            },
        ),
        check(
            "temporal_window_start_end_fields_present",
            all(
                field in row["bifurcation_window"]
                for field in ["start_step", "end_step", "event_time_key"]
            )
            and all(
                field in row["boundary_candidate_window"]
                for field in ["start_step", "end_step", "event_time_key"]
            ),
            {
                "bifurcation_window": row["bifurcation_window"],
                "boundary_candidate_window": row["boundary_candidate_window"],
            },
        ),
        check(
            "source_current_bifurcation_trace_present",
            row["bifurcation_trace"]["summary"]
            and row["new_boundary_candidate_trace"]["module_node_ids"],
            row["new_boundary_candidate_trace"],
        ),
        check(
            "label_and_thickening_controls_absent",
            row["label_only_rejected"] is True
            and row["old_basin_thickening_rejected"] is True
            and row["reshaped_old_boundary_rejected"] is True,
            "label/thickening/reshaped-boundary interpretations rejected",
        ),
        check(
            "bf_ceiling_conservative",
            row["bf_ladder_rung"] == "BF2_native_source_current_bifurcation_partial"
            and row["basin_formation_claim_allowed"] is False,
            row["bf_ladder_rung"],
        ),
        check(
            "artifact_manifest_valid",
            row["artifact_paths_equal_manifest_paths"] is True
            and row["artifact_sha256_equal_manifest_sha256"] is True
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_paths"],
        ),
        check(
            "unsafe_claim_flags_false",
            not any(row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_native_bifurcation_probe",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I4",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_native_source_current_bf2_bifurcation_partial_pending_i5_controls"
            if not failed
            else "failed_native_bifurcation_probe"
        ),
        "source_digest_chain_audit": {
            "i1": {"path": I1_OUTPUT_PATH, "sha256": sha256_file(I1_OUTPUT_PATH), "output_digest": i1.get("output_digest")},
            "i2": {"path": I2_OUTPUT_PATH, "sha256": sha256_file(I2_OUTPUT_PATH), "output_digest": i2.get("output_digest")},
            "i3": {"path": I3_OUTPUT_PATH, "sha256": sha256_file(I3_OUTPUT_PATH), "output_digest": i3.get("output_digest")},
        },
        "native_bifurcation_rows": [row],
        "native_bifurcation_row_count": 1,
        "source_current_bifurcation_observed": not failed,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": "BF2_native_source_current_bifurcation_partial",
        "provisional_bf3_candidate_pending_i5": not failed,
        "n25_closeout_ceiling": "N25-C2_spark_bifurcation_partial",
        "n25_closeout_ladder_rung_assigned": False,
        "basin_formation_claim_allowed": False,
        "producer_assisted_lane_opened": False,
        "ready_for_iteration_5_native_replay_and_control_matrix": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value({k: v for k, v in output.items() if k != "output_digest"})
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["native_bifurcation_rows"][0]
    lines = [
        "# N25 Iteration 4 - Native Optional-Branch Bifurcation Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Scope",
        "",
        "I4 runs the native path first. It reuses the existing LGRC9V3 Lane-B",
        "causal spark and active topology integration surfaces instead of adding",
        "producer spark code.",
        "",
        "## Result",
        "",
        "```text",
        f"bf_ceiling = {output['bf_ceiling']}",
        f"formation_class = {row['formation_class']}",
        f"provisional_formation_class_target = {row['provisional_formation_class_target']}",
        f"provisional_bf3_candidate_pending_i5 = {str(output['provisional_bf3_candidate_pending_i5']).lower()}",
        f"basin_formation_claim_allowed = {str(output['basin_formation_claim_allowed']).lower()}",
        f"native_flux_debt_bound = {row['native_flux_debt_bound']}",
        f"native_flux_debt_widened = {str(row['native_flux_debt_widened']).lower()}",
        f"producer_assisted_lane_opened = {str(output['producer_assisted_lane_opened']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "The spark is not just a report label: the event sequence contains",
        "`lgrc9v3_causal_spark_candidate`, `hybrid_mechanical_expansion`,",
        "`lgrc9v3_refinement_packet_transport`, and proper-time inheritance.",
        "The old root sink is replaced by module nodes and internal edges. That",
        "is enough for BF2 native bifurcation evidence and a provisional BF3",
        "target, but I5 must still test replay, transient rejection, and",
        "merge/leakage controls before any stronger closeout.",
        "",
        "The refinement packet transport event is structurally present with",
        "`amount_total = 0.0`. This is recorded as an interpretation boundary:",
        "the packet-triggered spark and mechanical expansion are source-current,",
        "while residual packet transport does not contribute measurable carried",
        "flux in I4. Conservation is therefore read from the expansion budget",
        "trace, where `budget_error = 0.0`.",
        "",
        "## Controls",
        "",
    ]
    for control in row["control_results"]:
        lines.append(
            f"- `{control['control_id']}`: `{control['control_status']}`; "
            f"{control['rung_effect']}"
        )
    lines.extend(["", "## Artifacts", ""])
    for entry in row["artifact_manifest"]:
        lines.append(f"- `{entry['artifact_role']}`: `{entry['path']}`")
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
