#!/usr/bin/env python3
"""Run N06 Iteration 3: SC1 candidate alternatives exposed.

This is an experiment-local probe over the native LGRC9V3 route-candidate
contract. It emits competing candidate route records and one candidate set from
committed runtime-visible surface evidence, then stops before arbitration,
topology commitment, producer scheduling, or claim promotion.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygrc.core import PortGraphBackend  # noqa: E402
from pygrc.models import (  # noqa: E402
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    PortEdge,
    build_lgrc9v3_native_route_candidate_set_idempotency_key,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_3_sc1_candidate_alternatives.json"
REPORT_PATH = N06 / "reports/n06_iteration_3_sc1_candidate_alternatives.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_3_sc1_candidate_alternatives.py"
)

CLAIM_FLAGS = (
    "semantic_choice_claim_allowed",
    "memory_or_trail_claim_allowed",
    "movement_claim_allowed",
    "agency_claim_allowed",
    "agentic_like_claim_allowed",
    "rc_identity_collapse_claim_allowed",
    "identity_acceptance_claim_allowed",
    "goal_proxy_regulation_claim_allowed",
    "locomotion_like_claim_allowed",
    "biological_claim_allowed",
    "ant_colony_claim_allowed",
    "unrestricted_movement_claim_allowed",
)

EDGE_PORTS = {
    0: (0, 0, 1, 0),
    1: (1, 1, 2, 0),
    2: (1, 2, 3, 0),
    3: (4, 0, 1, 3),
    4: (5, 0, 1, 4),
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _state_from_manifest(manifest: Mapping[str, Any]) -> GRC9V3State:
    graph = PortGraphBackend()
    node_ids: dict[int, int] = {}
    for node in manifest["fixture"]["nodes"]:
        manifest_node_id = int(node["node_id"])
        created_id = graph.add_node({"label": str(node["role"])})
        if created_id != manifest_node_id:
            raise RuntimeError(
                "N06 fixture requires manifest node ids to match native node ids"
            )
        node_ids[manifest_node_id] = created_id

    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}

    for edge in manifest["fixture"]["edges"]:
        edge_id = int(edge["edge_id"])
        node_u, port_u, node_v, port_v = EDGE_PORTS[edge_id]
        created_edge_id = graph.connect_ports(
            node_ids[node_u],
            port_u,
            node_ids[node_v],
            port_v,
            {"role": str(edge["role"])},
        )
        if created_edge_id != edge_id:
            raise RuntimeError(
                "N06 fixture requires manifest edge ids to match native edge ids"
            )
        conductance = float(edge["base_conductance"])
        delay = float(edge["temporal_delay"])
        port_edges[edge_id] = PortEdge(
            node_u,
            port_u,
            node_v,
            port_v,
            conductance=conductance,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = conductance
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = delay
        flux_coupling[edge_id] = 0.0

    return GRC9V3State(
        topology=graph,
        nodes={
            int(node["node_id"]): GRC9V3NodeState(coherence=1.0)
            for node in manifest["fixture"]["nodes"]
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def _params(*, native_route_arbitration_enabled: bool) -> dict[str, Any]:
    route_policy = (
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
        if native_route_arbitration_enabled
        else LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
    )
    return {
        "dt": 1.0,
        "causal_modes": {
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
            "causal_collapse_reabsorption_allowed": True,
            "causal_identity_acceptance_allowed": False,
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_enabled": True,
            "causal_pulse_substrate_surface_lineage_transport_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE
            ),
            "causal_pulse_substrate_surface_lineage_transport_validated": True,
            "causal_pulse_substrate_surface_lineage_transport_supported": True,
            "causal_topology_state_reabsorption_enabled": True,
            "causal_topology_state_reabsorption_policy": (
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE
            ),
            "causal_topology_state_reabsorption_validated": True,
            "causal_topology_state_reabsorption_supported": True,
            "native_lgrc_route_arbitration_enabled": native_route_arbitration_enabled,
            "native_lgrc_route_arbitration_policy": route_policy,
            "native_lgrc_route_arbitration_validated": (
                native_route_arbitration_enabled
            ),
            "native_lgrc_route_arbitration_supported": (
                native_route_arbitration_enabled
            ),
        },
    }


def _seed_model(
    manifest: Mapping[str, Any],
    *,
    native_route_arbitration_enabled: bool,
) -> tuple[LGRC9V3, Any]:
    model = LGRC9V3.from_state(
        _state_from_manifest(manifest),
        _params(native_route_arbitration_enabled=native_route_arbitration_enabled),
    )
    model.schedule_packet_departure(
        source_node_id=int(manifest["fixture"]["source_node_id"]),
        target_node_id=int(manifest["fixture"]["branch_node_id"]),
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    return model, source_row


def _numeric_budget_prediction(template: Mapping[str, Any]) -> dict[str, float]:
    prediction = template["candidate_budget_prediction"]
    return {
        "node_plus_packet_budget_before": float(
            prediction["node_plus_packet_budget_before"]
        ),
        "node_plus_packet_budget_after": float(
            prediction["node_plus_packet_budget_after"]
        ),
        "node_plus_packet_budget_error": float(
            prediction["node_plus_packet_budget_error"]
        ),
    }


def _candidate_templates(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(template["route_id"]): template
        for template in manifest["candidate_route_templates"]
    }


def _candidate_spec(
    manifest: Mapping[str, Any],
    *,
    route_id: str,
    source_surface_digest: str,
    context_state_id: str,
) -> dict[str, Any]:
    template = _candidate_templates(manifest)[route_id]
    context_state = manifest["context_affordance_surface"]["context_states"][
        context_state_id
    ]
    score_template = context_state["candidate_score_templates"][route_id]
    score_components = {
        str(key): float(value)
        for key, value in score_template["candidate_score_components"].items()
    }
    candidate_route_score = float(score_template["candidate_route_score"])
    return {
        "candidate_route_id": route_id,
        "candidate_source_surface_digest": source_surface_digest,
        "route_intent": LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        "candidate_topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "candidate_competing_sink_ids": [
            int(value) for value in template["candidate_competing_sink_ids"]
        ],
        "candidate_losing_sink_ids": [
            int(value) for value in template["candidate_losing_sink_ids"]
        ],
        "candidate_selected_sink_id": int(template["candidate_selected_sink_id"]),
        "candidate_transferred_node_ids": [
            int(value) for value in template["candidate_transferred_node_ids"]
        ],
        "candidate_lineage_transfer_map": {
            str(key): str(value)
            for key, value in template["candidate_lineage_transfer_map"].items()
        },
        "candidate_source_node_ids": [
            int(value) for value in template["candidate_source_node_ids"]
        ],
        "candidate_target_node_ids": [
            int(value) for value in template["candidate_target_node_ids"]
        ],
        "candidate_retired_node_ids": [
            int(value) for value in template["candidate_retired_node_ids"]
        ],
        "candidate_source_edge_ids": [
            int(value) for value in template["candidate_source_edge_ids"]
        ],
        "candidate_target_edge_ids": [
            int(value) for value in template["candidate_target_edge_ids"]
        ],
        "candidate_retired_edge_ids": [
            int(value) for value in template["candidate_retired_edge_ids"]
        ],
        "candidate_route_score": candidate_route_score,
        "candidate_score_components": score_components,
        "candidate_budget_prediction": _numeric_budget_prediction(template),
        "candidate_order_key": str(
            manifest["routes"][route_id]["candidate_order_key"]
        ),
        "candidate_runtime_visible_inputs": [
            "candidate_source_surface_digest",
            f"context_surface_digest:{source_surface_digest}",
            f"active_context_node_id:{context_state['active_context_node_id']}",
            f"candidate_route_id:{route_id}",
            f"compatible_route_id:{context_state['compatible_route_id']}",
            "candidate_score_components",
            "candidate_budget_prediction",
            "candidate_lineage_transfer_map",
            "serialized_route_arbitration_policy",
        ],
    }


def _candidate_specs(
    manifest: Mapping[str, Any],
    *,
    source_surface_digest: str,
    context_state_id: str = "context_a",
) -> list[dict[str, Any]]:
    return [
        _candidate_spec(
            manifest,
            route_id="route_a",
            source_surface_digest=source_surface_digest,
            context_state_id=context_state_id,
        ),
        _candidate_spec(
            manifest,
            route_id="route_b",
            source_surface_digest=source_surface_digest,
            context_state_id=context_state_id,
        ),
    ]


def _runtime_artifacts(model: LGRC9V3) -> dict[str, Any]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "candidate_route_records": runtime["native_route_candidate_log"],
        "candidate_set_records": runtime["native_route_candidate_set_log"],
        "route_arbitration_records": runtime["native_route_arbitration_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_events": [
            event["payload"] for event in runtime["topology_event_log"]
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
        "production_results": runtime["cached_quantities"].get(
            "lgrc9v3_autonomous_production_log",
            [],
        ),
    }


def _runtime_counts(model: LGRC9V3) -> dict[str, int]:
    artifacts = _runtime_artifacts(model)
    return {
        "event_count": len(artifacts["events"]),
        "surface_row_count": len(artifacts["surface_rows"]),
        "candidate_route_count": len(artifacts["candidate_route_records"]),
        "candidate_set_count": len(artifacts["candidate_set_records"]),
        "route_arbitration_count": len(artifacts["route_arbitration_records"]),
        "surface_lineage_count": len(artifacts["surface_lineage_records"]),
        "topology_event_count": len(artifacts["topology_events"]),
        "topology_state_reabsorption_count": len(
            artifacts["topology_state_reabsorption_records"]
        ),
        "production_result_count": len(artifacts["production_results"]),
    }


def _candidate_only_validation(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=artifacts["events"],
        candidate_route_records=artifacts["candidate_route_records"],
        candidate_set_records=artifacts["candidate_set_records"],
        route_arbitration_records=artifacts["route_arbitration_records"],
        surface_rows=artifacts["surface_rows"],
        surface_lineage_records=artifacts["surface_lineage_records"],
        topology_events=artifacts["topology_events"],
        topology_state_reabsorption_records=artifacts[
            "topology_state_reabsorption_records"
        ],
        production_results=artifacts["production_results"],
    )
    expected_incomplete = {"no_native_route_arbitration_records"}
    failures = set(str(reason) for reason in validation["failure_reasons"])
    unexpected_failures = sorted(failures - expected_incomplete)
    return {
        **validation,
        "validator_scope": "candidate_set_only_pre_arbitration",
        "expected_incomplete_reasons": sorted(expected_incomplete & failures),
        "unexpected_failure_reasons": unexpected_failures,
        "candidate_set_contract_valid": not unexpected_failures
        and validation["candidate_route_count"] > 0
        and validation["candidate_set_count"] == 1,
    }


def _context_derivation_checks(
    manifest: Mapping[str, Any],
    candidate_records: Sequence[Mapping[str, Any]],
    *,
    context_state_id: str,
    source_surface_digest: str,
) -> dict[str, Any]:
    tolerance = float(manifest["arbitration_policy"]["budget_tolerance"])
    mapping = manifest["context_affordance_surface"][
        "context_to_score_component_mapping"
    ]
    declared_context_fields = set(
        mapping["context_match"]["runtime_visible_input_fields"]
    )
    allowed_support_fields = {
        "candidate_source_surface_digest",
        "candidate_score_components",
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "serialized_route_arbitration_policy",
    }
    context_state = manifest["context_affordance_surface"]["context_states"][
        context_state_id
    ]
    compatible_route_id = str(context_state["compatible_route_id"])
    active_context_node_id = int(context_state["active_context_node_id"])
    per_candidate: dict[str, Any] = {}
    all_reconstructable = True
    for record in candidate_records:
        route_id = str(record["candidate_route_id"])
        components = record["candidate_score_components"]
        expected_context_match = (
            float(mapping["context_match"]["value_if_context_route_matches"])
            if route_id == compatible_route_id
            else float(mapping["context_match"]["value_if_context_route_mismatches"])
        )
        expected_budget = float(mapping["budget_validity"]["value_if_valid"])
        expected_lineage = float(mapping["lineage_ready"]["value_if_valid"])
        runtime_inputs = set(str(value) for value in record["candidate_runtime_visible_inputs"])
        component_checks = {
            "context_match": abs(
                float(components["context_match"]) - expected_context_match
            )
            <= tolerance,
            "budget_validity": abs(
                float(components["budget_validity"]) - expected_budget
            )
            <= tolerance,
            "lineage_ready": abs(
                float(components["lineage_ready"]) - expected_lineage
            )
            <= tolerance,
        }
        input_checks = {
            "active_context_node_id_serialized": (
                f"active_context_node_id:{active_context_node_id}" in runtime_inputs
            ),
            "candidate_route_id_serialized": (
                f"candidate_route_id:{route_id}" in runtime_inputs
            ),
            "compatible_route_id_serialized": (
                f"compatible_route_id:{compatible_route_id}" in runtime_inputs
            ),
            "context_surface_digest_serialized": (
                f"context_surface_digest:{source_surface_digest}" in runtime_inputs
            ),
        }
        runtime_visible_field_names = {
            value.split(":", 1)[0] for value in runtime_inputs
        }
        undeclared_field_names = sorted(
            runtime_visible_field_names - declared_context_fields - allowed_support_fields
        )
        input_checks["declared_context_fields_present"] = (
            declared_context_fields.issubset(runtime_visible_field_names)
        )
        input_checks["no_undeclared_runtime_visible_fields"] = not undeclared_field_names
        row_ok = all(component_checks.values()) and all(input_checks.values())
        all_reconstructable = all_reconstructable and row_ok
        per_candidate[route_id] = {
            "component_checks": component_checks,
            "runtime_visible_input_checks": input_checks,
            "runtime_visible_field_names": sorted(runtime_visible_field_names),
            "undeclared_runtime_visible_field_names": undeclared_field_names,
            "reconstructable": row_ok,
        }
    return {
        "context_state_id": context_state_id,
        "active_context_node_id": active_context_node_id,
        "compatible_route_id": compatible_route_id,
        "source_surface_digest": source_surface_digest,
        "comparison_tolerance": tolerance,
        "declared_context_fields": sorted(declared_context_fields),
        "allowed_support_fields": sorted(allowed_support_fields),
        "per_candidate": per_candidate,
        "context_to_score_reconstructable": all_reconstructable,
    }


def _budget_prediction_checks(
    manifest: Mapping[str, Any],
    candidate_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    tolerance = float(manifest["arbitration_policy"]["budget_tolerance"])
    templates = _candidate_templates(manifest)
    per_candidate: dict[str, Any] = {}
    all_match = True
    for record in candidate_records:
        route_id = str(record["candidate_route_id"])
        expected = _numeric_budget_prediction(templates[route_id])
        actual = {
            str(key): float(value)
            for key, value in record["candidate_budget_prediction"].items()
        }
        field_checks = {
            key: abs(float(actual.get(key, float("nan"))) - expected_value) <= tolerance
            for key, expected_value in expected.items()
        }
        error_within_tolerance = (
            abs(float(actual.get("node_plus_packet_budget_error", float("nan"))))
            <= tolerance
        )
        candidate_ok = all(field_checks.values()) and error_within_tolerance
        all_match = all_match and candidate_ok
        per_candidate[route_id] = {
            "expected": expected,
            "actual": actual,
            "field_checks": field_checks,
            "node_plus_packet_budget_error_within_tolerance": error_within_tolerance,
            "matches_manifest": candidate_ok,
        }
    return {
        "comparison_tolerance": tolerance,
        "per_candidate": per_candidate,
        "budget_predictions_match_manifest": all_match,
    }


def _candidate_set_idempotency_check(candidate_set: Mapping[str, Any]) -> dict[str, Any]:
    reconstructed = build_lgrc9v3_native_route_candidate_set_idempotency_key(
        native_route_arbitration_policy_id=str(
            candidate_set["native_route_arbitration_policy_id"]
        ),
        arbitration_window_id=str(candidate_set["arbitration_window_id"]),
        event_time_key=float(candidate_set["event_time_key"]),
        candidate_route_digests=[
            str(value) for value in candidate_set["candidate_route_digests"]
        ],
        candidate_set_order_key=str(candidate_set["candidate_set_order_key"]),
    )
    return {
        "recorded_idempotency_key": candidate_set["idempotency_key"],
        "reconstructed_idempotency_key": reconstructed,
        "reconstructable": reconstructed == candidate_set["idempotency_key"],
    }


def _claim_flags_false_in_records(records: Sequence[Mapping[str, Any]]) -> bool:
    for record in records:
        flags = record.get("claim_flags", {})
        if not isinstance(flags, Mapping):
            return False
        if any(bool(flags.get(flag, False)) for flag in CLAIM_FLAGS):
            return False
    return True


def _emit_candidate_set(
    model: LGRC9V3,
    manifest: Mapping[str, Any],
    *,
    source_surface_digest: str,
    candidate_specs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return model.emit_native_route_candidate_set(
        arbitration_window_id=str(
            manifest["arbitration_window"]["arbitration_window_id"]
        ),
        source_surface_digest=source_surface_digest,
        candidate_routes=candidate_specs,
        candidate_set_order_key=(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        unresolved_tie_policy=LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    )


def _run_default_off_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model, source_row = _seed_model(
        manifest,
        native_route_arbitration_enabled=False,
    )
    source_surface_digest = str(source_row.surface_digest)
    specs = _candidate_specs(
        manifest,
        source_surface_digest=source_surface_digest,
        context_state_id="context_a",
    )
    before_counts = _runtime_counts(model)
    result = _emit_candidate_set(
        model,
        manifest,
        source_surface_digest=source_surface_digest,
        candidate_specs=specs,
    )
    after_counts = _runtime_counts(model)
    return {
        "lane_id": "default_off_no_candidate_emission",
        "native_lgrc_route_arbitration_enabled": False,
        "source_surface_digest": source_surface_digest,
        "emit_result": {
            "emitted": bool(result["emitted"]),
            "reason_code": result["reason_code"],
            "candidate_record_count": len(result["candidate_records"]),
            "candidate_set_record_present": result["candidate_set_record"] is not None,
        },
        "before_counts": before_counts,
        "after_counts": after_counts,
        "passed": (
            result["emitted"] is False
            and result["reason_code"]
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED
            and after_counts["candidate_route_count"] == 0
            and after_counts["candidate_set_count"] == 0
            and after_counts["route_arbitration_count"] == 0
            and after_counts["topology_event_count"] == 0
            and after_counts["production_result_count"] == 0
        ),
    }


def _run_enabled_sc1_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    model, source_row = _seed_model(
        manifest,
        native_route_arbitration_enabled=True,
    )
    source_surface_digest = str(source_row.surface_digest)
    specs = _candidate_specs(
        manifest,
        source_surface_digest=source_surface_digest,
        context_state_id="context_a",
    )
    before_counts = _runtime_counts(model)
    result = _emit_candidate_set(
        model,
        manifest,
        source_surface_digest=source_surface_digest,
        candidate_specs=specs,
    )
    after_counts = _runtime_counts(model)
    artifacts = _runtime_artifacts(model)
    candidate_records = artifacts["candidate_route_records"]
    candidate_set_records = artifacts["candidate_set_records"]
    candidate_set = candidate_set_records[0]
    budget_checks = _budget_prediction_checks(manifest, candidate_records)
    idempotency_check = _candidate_set_idempotency_check(candidate_set)
    committed_surface_digests = {
        str(row["surface_digest"]) for row in artifacts["surface_rows"]
    }
    candidate_order = [record["candidate_route_id"] for record in candidate_records]
    expected_order = [
        record["candidate_route_id"]
        for record in sorted(
            candidate_records,
            key=lambda record: (
                -float(record["candidate_route_score"]),
                str(record["candidate_order_key"]),
                str(record["candidate_route_id"]),
            ),
        )
    ]
    candidate_digests = {
        str(record["candidate_route_digest"]) for record in candidate_records
    }
    candidate_only_validation = _candidate_only_validation(artifacts)
    context_checks = _context_derivation_checks(
        manifest,
        candidate_records,
        context_state_id="context_a",
        source_surface_digest=source_surface_digest,
    )
    timing = manifest["arbitration_window"]["timing"]
    checks = {
        "candidate_route_count_is_two": len(candidate_records) == 2,
        "candidate_set_count_is_one": len(candidate_set_records) == 1,
        "candidate_sources_non_null": all(
            bool(record["candidate_source_surface_digest"])
            for record in candidate_records
        ),
        "candidate_sources_committed": all(
            record["candidate_source_surface_digest"] in committed_surface_digests
            for record in candidate_records
        ),
        "sc1_reabsorption_digest_absent": all(
            record["candidate_source_topology_state_reabsorption_digest"] is None
            for record in candidate_records
        ),
        "source_producer_record_id_null_when_not_producer_backed": all(
            record["candidate_source_producer_record_id"] is None
            for record in candidate_records
        ),
        "context_to_score_reconstructable": context_checks[
            "context_to_score_reconstructable"
        ],
        "event_time_and_scheduler_order_present": all(
            "event_time_key" in record and "scheduler_event_index" in record
            for record in candidate_records
        )
        and "event_time_key" in candidate_set
        and "scheduler_event_index" in candidate_set,
        "causal_epoch_and_checkpoint_recorded_in_report": bool(
            timing["causal_epoch"]
        )
        and int(timing["checkpoint_index"]) == 0,
        "candidate_set_includes_all_window_candidates": set(
            candidate_set["candidate_route_digests"]
        )
        == candidate_digests,
        "deterministic_candidate_order": candidate_order == expected_order
        and candidate_set["candidate_route_digests"]
        == [record["candidate_route_digest"] for record in candidate_records],
        "candidate_route_digests_recorded": all(
            bool(record["candidate_route_digest"]) for record in candidate_records
        ),
        "candidate_budget_predictions_present": all(
            bool(record["candidate_budget_prediction"])
            for record in candidate_records
        ),
        "candidate_budget_predictions_match_manifest": budget_checks[
            "budget_predictions_match_manifest"
        ],
        "candidate_set_idempotency_key_reconstructable": idempotency_check[
            "reconstructable"
        ],
        "candidate_set_contract_valid_pre_arbitration": candidate_only_validation[
            "candidate_set_contract_valid"
        ],
        "no_route_arbitration_record": after_counts["route_arbitration_count"] == 0,
        "no_selected_topology_event_committed": (
            after_counts["topology_event_count"] == 0
        ),
        "no_packet_scheduled_by_candidate_emission": (
            after_counts["event_count"] == before_counts["event_count"]
            and after_counts["production_result_count"]
            == before_counts["production_result_count"]
        ),
        "claim_flags_remain_false": _claim_flags_false_in_records(
            [*candidate_records, *candidate_set_records]
        ),
    }
    return {
        "lane_id": "enabled_sc1_candidate_alternatives",
        "native_lgrc_route_arbitration_enabled": True,
        "source_surface_id": source_row.surface_id,
        "source_surface_digest": source_surface_digest,
        "source_surface_kind": source_row.surface_kind,
        "candidate_route_count": len(candidate_records),
        "candidate_set_count": len(candidate_set_records),
        "candidate_order": candidate_order,
        "expected_candidate_order": expected_order,
        "candidate_route_digests": sorted(candidate_digests),
        "candidate_set_digest": candidate_set["candidate_set_digest"],
        "candidate_set_idempotency_key": candidate_set["idempotency_key"],
        "arbitration_window": {
            "arbitration_window_id": manifest["arbitration_window"][
                "arbitration_window_id"
            ],
            "causal_epoch": timing["causal_epoch"],
            "checkpoint_index": timing["checkpoint_index"],
            "candidate_set_order_key": candidate_set["candidate_set_order_key"],
            "unresolved_tie_policy": candidate_set["unresolved_tie_policy"],
        },
        "before_counts": before_counts,
        "after_counts": after_counts,
        "context_derivation": context_checks,
        "context_scope": {
            "checked_context_state_ids": ["context_a"],
            "deferred_context_state_ids": ["context_b"],
            "deferred_to_iteration": "Iteration 5 / SC3 context-conditioned route selection",
            "reason": "SC1 exposes alternatives from one committed context surface and does not yet prove context switching.",
        },
        "budget_prediction_checks": budget_checks,
        "candidate_set_idempotency_check": idempotency_check,
        "candidate_only_artifact_validation": candidate_only_validation,
        "checks": checks,
        "candidate_records": candidate_records,
        "candidate_set_record": candidate_set,
        "passed": all(checks.values()),
    }


def _control_result(
    control_id: str,
    *,
    passed: bool,
    primary_blocker: str,
    detail: Any = None,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "passed": bool(passed),
        "primary_blocker": primary_blocker,
        "detail": detail,
    }


def _exception_control(
    manifest: Mapping[str, Any],
    *,
    control_id: str,
    expected_blocker: str,
    spec_mutator: Any,
    require_detail_match: bool = True,
) -> dict[str, Any]:
    model, source_row = _seed_model(
        manifest,
        native_route_arbitration_enabled=True,
    )
    source_surface_digest = str(source_row.surface_digest)
    specs = _candidate_specs(
        manifest,
        source_surface_digest=source_surface_digest,
        context_state_id="context_a",
    )
    mutated_specs = spec_mutator(specs, source_surface_digest)
    try:
        _emit_candidate_set(
            model,
            manifest,
            source_surface_digest=source_surface_digest,
            candidate_specs=mutated_specs,
        )
    except Exception as exc:  # noqa: BLE001 - controls record native blockers.
        detail = str(exc)
        return _control_result(
            control_id,
            passed=(expected_blocker in detail) if require_detail_match else True,
            primary_blocker=expected_blocker,
            detail=detail,
        )
    return _control_result(
        control_id,
        passed=False,
        primary_blocker=expected_blocker,
        detail="control did not raise",
    )


def _run_controls(manifest: Mapping[str, Any], enabled_lane: Mapping[str, Any]) -> dict[str, Any]:
    controls: dict[str, dict[str, Any]] = {}
    controls["hidden_route"] = _exception_control(
        manifest,
        control_id="hidden_route",
        expected_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        spec_mutator=lambda specs, _digest: [
            {**specs[0], "candidate_hidden_inputs": ["experiment_if_else"]},
            specs[1],
        ],
    )
    controls["hidden_context"] = _exception_control(
        manifest,
        control_id="hidden_context",
        expected_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        spec_mutator=lambda specs, _digest: [
            {
                **specs[0],
                "candidate_score_components": {
                    "hidden_fixture_state": 0.6,
                    "budget_validity": 0.2,
                    "lineage_ready": 0.2,
                },
                "candidate_route_score": 1.0,
            },
            specs[1],
        ],
    )
    controls["missing_budget_prediction"] = _exception_control(
        manifest,
        control_id="missing_budget_prediction",
        expected_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        spec_mutator=lambda specs, _digest: [
            {key: value for key, value in specs[0].items() if key != "candidate_budget_prediction"},
            specs[1],
        ],
    )
    controls["malformed_candidate"] = _exception_control(
        manifest,
        control_id="malformed_candidate",
        expected_blocker="native_route_candidate_schema_rejected_malformed_candidate",
        spec_mutator=lambda specs, _digest: [
            {**specs[0], "candidate_selected_sink_id": 99},
            specs[1],
        ],
        require_detail_match=False,
    )
    controls["unknown_source_surface_digest"] = _exception_control(
        manifest,
        control_id="unknown_source_surface_digest",
        expected_blocker="native_route_candidate_committed_source_surface_required",
        spec_mutator=lambda specs, _digest: [
            {
                **specs[0],
                "candidate_source_surface_digest": "sha256:not-committed",
            },
            {
                **specs[1],
                "candidate_source_surface_digest": "sha256:not-committed",
            },
        ],
        require_detail_match=False,
    )

    duplicate_model, duplicate_source_row = _seed_model(
        manifest,
        native_route_arbitration_enabled=True,
    )
    duplicate_digest = str(duplicate_source_row.surface_digest)
    duplicate_spec = _candidate_spec(
        manifest,
        route_id="route_a",
        source_surface_digest=duplicate_digest,
        context_state_id="context_a",
    )
    duplicate_result = _emit_candidate_set(
        duplicate_model,
        manifest,
        source_surface_digest=duplicate_digest,
        candidate_specs=[duplicate_spec, copy.deepcopy(duplicate_spec)],
    )
    duplicate_artifacts = _runtime_artifacts(duplicate_model)
    duplicate_route_count = len(duplicate_artifacts["candidate_route_records"])
    duplicate_set = duplicate_artifacts["candidate_set_records"][0]
    controls["duplicate_candidate"] = _control_result(
        "duplicate_candidate",
        passed=duplicate_route_count == 1
        and len(duplicate_set["candidate_route_digests"]) == 1
        and duplicate_result["emitted"] is True,
        primary_blocker="duplicate_native_route_candidate_suppressed",
        detail={
            "candidate_route_count_after_duplicate_input": duplicate_route_count,
            "candidate_set_route_digest_count": len(
                duplicate_set["candidate_route_digests"]
            ),
        },
    )

    corrupted_records = copy.deepcopy(enabled_lane["candidate_records"])
    corrupted_records[0]["claim_flags"]["semantic_choice_claim_allowed"] = True
    claim_validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=[],
        candidate_route_records=corrupted_records,
        candidate_set_records=[enabled_lane["candidate_set_record"]],
        route_arbitration_records=[],
        surface_rows=[],
    )
    controls["claim_promotion"] = _control_result(
        "claim_promotion",
        passed=any(
            "native_route_arbitration_claim_promotion_blocked" in reason
            for reason in claim_validation["failure_reasons"]
        ),
        primary_blocker="native_route_arbitration_claim_promotion_blocked",
        detail={
            "specific_claim_promotion_blocker_present": any(
                "native_route_arbitration_claim_promotion_blocked" in reason
                for reason in claim_validation["failure_reasons"]
            ),
            "failure_reasons": claim_validation["failure_reasons"],
            "side_effect_failures_allowed": [
                "corrupted record digest mismatch",
                "candidate set missing corrupted candidate digest",
                "no_native_route_arbitration_records at SC1 scope",
            ],
        },
    )
    return controls


def _build_report(data: Mapping[str, Any]) -> str:
    acceptance = data["acceptance"]
    enabled = data["lanes"]["enabled_sc1"]
    controls = data["controls"]
    lines = [
        "# N06 Iteration 3 SC1 Candidate Alternatives",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- source surface digest: `{enabled['source_surface_digest']}`",
        f"- candidate route count: `{enabled['candidate_route_count']}`",
        f"- candidate set digest: `{enabled['candidate_set_digest']}`",
        f"- candidate order: `{enabled['candidate_order']}`",
        "",
        "## Boundary",
        "",
        "- SC1 emits native candidate route records and one candidate set.",
        "- It does not emit a route-arbitration record.",
        "- It does not commit a selected topology event.",
        "- It does not schedule packets or mutate state from candidate emission.",
        "- It does not promote semantic choice, memory, agency, identity, movement, or ACO claims.",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(acceptance, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate-Only Replay Scope",
        "",
        "The full native route-arbitration validator is intentionally incomplete at SC1 because no arbitration record exists yet. Iteration 3 treats `no_native_route_arbitration_records` as the expected pre-arbitration limitation and fails on any other candidate/candidate-set replay issue.",
        "",
        "```json",
        json.dumps(
            enabled["candidate_only_artifact_validation"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Context Derivation",
        "",
        "```json",
        json.dumps(enabled["context_derivation"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(controls, indent=2, sort_keys=True),
        "```",
        "",
        "## Artifact Digests",
        "",
        "```json",
        json.dumps(data["artifact_digests"], indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    manifest = _load_manifest()
    default_off = _run_default_off_lane(manifest)
    enabled_sc1 = _run_enabled_sc1_lane(manifest)
    controls = _run_controls(manifest, enabled_sc1)
    checks = {
        "default_off_noop_passed": default_off["passed"],
        "enabled_sc1_lane_passed": enabled_sc1["passed"],
        "controls_passed": all(control["passed"] for control in controls.values()),
        "no_route_arbitration_record_emitted": enabled_sc1["checks"][
            "no_route_arbitration_record"
        ],
        "no_selected_topology_event_committed": enabled_sc1["checks"][
            "no_selected_topology_event_committed"
        ],
        "no_packet_scheduled_by_candidate_emission": enabled_sc1["checks"][
            "no_packet_scheduled_by_candidate_emission"
        ],
        "claim_flags_remain_false": enabled_sc1["checks"][
            "claim_flags_remain_false"
        ],
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "sc_level": "SC1",
        "claim_ceiling": "candidate_alternatives_exposed_no_selection",
        "candidate_alternatives_exposed": enabled_sc1["passed"],
        "default_off_no_candidates": default_off["passed"],
        "context_to_score_reconstructable": enabled_sc1["checks"][
            "context_to_score_reconstructable"
        ],
        "candidate_set_contract_valid_pre_arbitration": enabled_sc1["checks"][
            "candidate_set_contract_valid_pre_arbitration"
        ],
        "route_selected": False,
        "topology_event_committed": False,
        "packet_scheduled_by_candidate_emission": False,
        "semantic_choice_claim_allowed": False,
        "all_claim_flags_false": enabled_sc1["checks"]["claim_flags_remain_false"],
        "status": status,
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 3,
        "iteration_name": "SC1 Alternatives Exposed",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest": _artifact_record(MANIFEST_PATH),
        "lanes": {
            "default_off": default_off,
            "enabled_sc1": enabled_sc1,
        },
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "claim_flags": {flag: False for flag in CLAIM_FLAGS},
        "artifact_digests": {},
        "git": {
            "status_src": _git(["status", "--short", "src"]),
            "diff_check_experiment": _git(
                ["diff", "--check", "--", _rel(N06)]
            ),
        },
    }
    data["artifact_digests"] = {
        "enabled_lane_digest": _digest(enabled_sc1),
        "controls_digest": _digest(controls),
        "acceptance_digest": _digest(acceptance),
        "claim_flags_digest": _digest(data["claim_flags"]),
    }
    OUTPUT_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(_build_report(data), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "candidate_route_count": enabled_sc1["candidate_route_count"],
                "candidate_set_count": enabled_sc1["candidate_set_count"],
                "default_off_passed": default_off["passed"],
                "controls_passed": checks["controls_passed"],
                "route_selected": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
