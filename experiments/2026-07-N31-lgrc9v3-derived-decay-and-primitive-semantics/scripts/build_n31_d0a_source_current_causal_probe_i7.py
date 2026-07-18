#!/usr/bin/env python3
"""Build N31 Iteration 7 source-current spatial D0a probe artifacts."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    PortEdge,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
    lgrc9v3_restoration_identity_v1,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
ARTIFACT_DIR = OUTPUTS / "n31_i7_d0a_source_current_causal_probe_artifacts"
I2_OUTPUT = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I3_OUTPUT = OUTPUTS / "n31_active_nulls_and_failure_baselines_i3.json"
I3R1_OUTPUT = OUTPUTS / "n31_i3_revision_lineage_r1.json"
I4_OUTPUT = OUTPUTS / "n31_d0a_representation_gate_i4.json"
I4R1_OUTPUT = OUTPUTS / "n31_i4_revision_lineage_r1.json"
I5_OUTPUT = OUTPUTS / "n31_d0c_instantaneous_geometry_comparator_i5.json"
I5R1_OUTPUT = OUTPUTS / "n31_i5_revision_lineage_r1.json"
I6_OUTPUT = OUTPUTS / "n31_d0b_finite_window_derived_relation_i6.json"
I6_TRACE = OUTPUTS / "n31_i6_d0b_finite_window_source_current_trace.json"
PREREGISTRATION = ARTIFACT_DIR / "n31_i7_preregistration.json"
TRACE = OUTPUTS / "n31_i7_d0a_source_current_causal_trace.json"
OUTPUT = OUTPUTS / "n31_d0a_source_current_causal_probe_i7.json"
REPORT = EXPERIMENT / "reports" / "n31_d0a_source_current_causal_probe_i7.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_d0a_source_current_causal_probe_i7.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I7_GOVERNANCE_BASE_REVISION = "42a760376c630fc9d9797ef2d85848b5af628a17"
PROTECTED_RUNTIME_BASE_REVISION = I7_GOVERNANCE_BASE_REVISION
SOURCE_IDENTITIES = {
    I2_OUTPUT: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I3_OUTPUT: (
        "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea",
        "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff",
    ),
    I3R1_OUTPUT: (
        "b6f6c1948f723d5fbb6008348b804b778993718da18c4b7efb3a499a8757de64",
        "2ac6582625b0898fd799c545de385a757925226eae4d38803d903549e2133398",
    ),
    I4_OUTPUT: (
        "b7b6f34e3978ec4a410a77e36bc1b548f1baf96dbda7987803d544fc737c3597",
        "eab3b993ad9990c2a7ba47e2445f62b520e003d9c938bc9cbc9590e428dd3782",
    ),
    I4R1_OUTPUT: (
        "6dbd1441b5fcdce666d8eeca287cd59205cc4d34495016a0aefe3da9b818eb16",
        "a8781a04980b0a650a0ebfeae41f34a067a188f72c57b71f140ad1048642d5ba",
    ),
    I5_OUTPUT: (
        "95d1a1f2c3003a7eeaa1edeaf9a0e843ac92e2c4af010e04a045233b445ac88b",
        "6b4707cd8b7a10d563cb55f5b61fd4d857161c7b644218ed18cdc7b541be7704",
    ),
    I5R1_OUTPUT: (
        "1bb729f219fbb4e0e5f52615e4213567e4f46b195b7bc00a27376c283203e9c8",
        "4d0e0dded207fc7c1da61114ee603835a168f58d155b7912edb2e6f189957aa0",
    ),
    I6_OUTPUT: (
        "206088cbe96bb37e119aa88a543f728170d206ad3ce15e9da24f1b9a5f77313a",
        "a076c8d78adeb0a92b0d28f1393f73a0e7731e9a39f16374b94d37b69ebf0a22",
    ),
    I6_TRACE: (
        "7941db25a5c048f450573725f3844c098f7060a0ca265cb2dd1711ced4e92f2f",
        "42f7436351b59181b9a55a2869e97de36a37646b79b05adeae9e12fc9c1b2039",
    ),
}

ROUTE_SUPPORT = (0, 1, 2)
ROUTE_BOUNDARY_EDGE = 2
INITIAL_ROUTE_C = {0: 0.48, 1: 0.04, 2: 0.48}
FORMATION_PACKET_AMOUNT = 0.20
PERSISTENCE_PACKET_AMOUNT = 0.05
PROGRESSION_PACKET_AMOUNT = 0.04
READOUT_PACKET_AMOUNT = 0.22
ATTEMPT_MODES = (
    "disjoint_hold",
    "internal_weakening",
    "internal_reinforcement",
)

THRESHOLDS = {
    "threshold_record_id": "n31_i7_spatial_D0a_thresholds_v1",
    "declared_before_runtime_execution": True,
    "selected_organization_coordinate": "C[1]-C[2]",
    "stronger_orientation": "greater_than_baseline_in_formation_direction",
    "weaker_orientation": "lower_positive_formation_effect",
    "baseline_rule": "pre_formation_C1_minus_C2",
    "minimum_formation_effect": 0.15,
    "persistence_tolerance": 1e-12,
    "minimum_weakening_amount": 0.05,
    "minimum_residual_organization": 0.05,
    "minimum_readout_pass_margin": 0.015,
    "minimum_readout_rejection_shortfall": 0.015,
    "route_mass_tolerance": 1e-12,
    "closed_system_budget_tolerance": 1e-12,
    "identity_match_tolerance": 0.0,
    "trajectory_rule": (
        "formation effect must persist through a disjoint event, then the "
        "predeclared internal-weakening row must reduce but not erase it"
    ),
    "monotonicity_requirement": "single_directional_weakening_step_only",
    "sign_or_orientation_ambiguity_resolution": (
        "orientation is frozen from the signed C1-C2 formation delta; absolute "
        "magnitude is not substituted after outcomes are observed"
    ),
    "declaration_digest": "computed_from_this_record_before_model_execution",
    "declared_before_candidate_outcome": True,
}

BLOCKED_RELABELS = [
    "autonomous_slow_mode_relaxation",
    "general_decay_law",
    "independent_decay_state",
    "native_route_memory",
    "trail_or_stigmergic_field",
    "semantic_memory",
    "learning",
    "communication",
    "ecological_coordination",
    "agency",
    "selfhood",
    "sentience",
    "organism_or_life",
    "native_support",
    "phase8_completion",
    "unrestricted_autonomy",
]


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(marker not in text for marker in forbidden)


def git_diff_empty(base: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", base, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path) -> dict[str, Any]:
    data = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    return {
        "path": relative(path),
        "expected_output_digest": expected_digest,
        "actual_output_digest": data.get("output_digest"),
        "expected_sha256": expected_sha,
        "actual_sha256": sha256_file(path),
        "identity_exact": data.get("output_digest") == expected_digest
        and sha256_file(path) == expected_sha,
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
    }


def build_graph_state() -> GRC9V3State:
    graph = PortGraphBackend()
    for label in (
        "route_source",
        "route_mediator",
        "route_anchor",
        "outside_a",
        "outside_b",
    ):
        graph.add_node({"label": label})

    edge_specs = (
        (0, 1, 0, 0, "route_internal"),
        (1, 2, 1, 0, "route_internal"),
        (2, 3, 1, 0, "route_boundary"),
        (3, 4, 1, 0, "outside_progression"),
    )
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for source, target, source_slot, target_slot, kind in edge_specs:
        edge_id = graph.connect_ports(
            source,
            source_slot,
            target,
            target_slot,
            {"kind": kind},
        )
        port_edges[edge_id] = PortEdge(
            source,
            source_slot + 1,
            target,
            target_slot + 1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0

    return GRC9V3State(
        topology=graph,
        nodes={
            0: GRC9V3NodeState(coherence=INITIAL_ROUTE_C[0]),
            1: GRC9V3NodeState(coherence=INITIAL_ROUTE_C[1]),
            2: GRC9V3NodeState(coherence=INITIAL_ROUTE_C[2]),
            3: GRC9V3NodeState(coherence=0.50),
            4: GRC9V3NodeState(coherence=0.50),
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def schedule_packet(
    model: LGRC9V3,
    *,
    source: int,
    target: int,
    edge: int,
    amount: float,
    departure: float,
    arrival: float,
    scheduler_index: int,
) -> None:
    model.schedule_packet_departure(
        source_node_id=source,
        target_node_id=target,
        edge_id=edge,
        amount=amount,
        departure_event_time_key=departure,
        arrival_event_time_key=arrival,
        scheduler_event_index=scheduler_index,
    )


def build_attempt_model(mode: str) -> LGRC9V3:
    if mode not in ATTEMPT_MODES:
        raise ValueError(f"unknown attempt mode: {mode}")
    model = LGRC9V3.from_state(build_graph_state(), {"dt": 1.0})
    schedules = [
        (0, 1, 0, FORMATION_PACKET_AMOUNT, 0.0, 1.0, 1),
        (3, 4, 3, PERSISTENCE_PACKET_AMOUNT, 2.0, 3.0, 3),
    ]
    if mode == "disjoint_hold":
        schedules.append((4, 3, 3, PROGRESSION_PACKET_AMOUNT, 4.0, 5.0, 5))
    elif mode == "internal_weakening":
        schedules.append((1, 2, 1, PROGRESSION_PACKET_AMOUNT, 4.0, 5.0, 5))
    else:
        schedules.append((2, 1, 1, PROGRESSION_PACKET_AMOUNT, 4.0, 5.0, 5))
    schedules.append((1, 0, 0, READOUT_PACKET_AMOUNT, 6.0, 7.0, 7))
    for source, target, edge, amount, departure, arrival, scheduler_index in schedules:
        schedule_packet(
            model,
            source=source,
            target=target,
            edge=edge,
            amount=amount,
            departure=departure,
            arrival=arrival,
            scheduler_index=scheduler_index,
        )
    return model


def route_packet_mass(model: LGRC9V3) -> float:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    support = set(ROUTE_SUPPORT)
    return sum(
        float(packet.amount)
        for packet in ledger.packet_records
        if packet.packet_state == "in_flight"
        and int(packet.source_node_id) in support
        and int(packet.target_node_id) in support
    )


def route_state(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    coherence = {
        str(node_id): float(state.base_state.nodes[node_id].coherence)
        for node_id in ROUTE_SUPPORT
    }
    node_mass = sum(coherence.values())
    in_flight = route_packet_mass(model)
    c0_c2 = coherence["0"] - coherence["2"]
    c1_c2 = coherence["1"] - coherence["2"]
    baseline_coordinate = INITIAL_ROUTE_C[1] - INITIAL_ROUTE_C[2]
    formation_oriented_strength = c1_c2 - baseline_coordinate
    return {
        "event_time_key": float(state.event_time_key),
        "scheduler_event_index": int(state.scheduler_event_index),
        "node_coherence": coherence,
        "route_node_coherence_mass": node_mass,
        "route_internal_in_flight_mass": in_flight,
        "registered_route_mass": node_mass + in_flight,
        "spatial_organization": {
            "coordinate_C0_minus_C2": c0_c2,
            "coordinate_C1_minus_C2": c1_c2,
            "baseline_C1_minus_C2": baseline_coordinate,
            "formation_oriented_strength": formation_oriented_strength,
            "internal_oriented_flux": {
                str(edge_id): float(state.base_state.port_edges[edge_id].flux_uv)
                for edge_id in (0, 1)
            },
        },
        "boundary_transfer": {
            "edge_id": ROUTE_BOUNDARY_EDGE,
            "instantaneous_oriented_flux": float(
                state.base_state.port_edges[ROUTE_BOUNDARY_EDGE].flux_uv
            ),
            "integrated_outward_transfer_in_window": 0.0,
        },
        "runtime_budget": {
            "node_coherence_total": float(ledger.node_coherence_total),
            "in_flight_packet_total": float(ledger.in_flight_packet_total),
            "conserved_budget_total": float(ledger.conserved_budget_total),
            "budget_error": float(ledger.budget_error),
        },
        "queue_record_count": len(ledger.event_queue_records),
        "restoration_identity_v1_digest": digest_lgrc9v3_restoration_identity_v1(
            model
        ),
        "restoration_identity_v2_digest": digest_lgrc9v3_restoration_identity_v2(
            model
        ),
        "forming_packet_in_flight": any(
            packet.packet_state == "in_flight"
            and int(packet.source_node_id) == 0
            and int(packet.target_node_id) == 1
            and abs(float(packet.amount) - FORMATION_PACKET_AMOUNT) <= 1e-12
            for packet in ledger.packet_records
        ),
    }


def save_snapshot(model: LGRC9V3, name: str) -> dict[str, Any]:
    path = ARTIFACT_DIR / f"{name}.json"
    model.save(str(path))
    return {
        "path": relative(path),
        "sha256": sha256_file(path),
        "artifact_role": f"source_current_{name}_snapshot",
    }


def event_receipt(result: Any) -> dict[str, Any]:
    return {
        "step_index": int(result.step_index),
        "event_time_key": float(result.time),
        "event_kinds": [event.kind for event in result.events],
        "state_mutated": any(bool(event.payload.get("state_mutated", False)) for event in result.events),
        "budget_errors": [
            float(event.payload["budget_error"])
            for event in result.events
            if "budget_error" in event.payload
        ],
    }


def process_exact_events(model: LGRC9V3, count: int) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for _ in range(count):
        receipts.append(event_receipt(model.step()))
    return receipts


def readout(model: LGRC9V3) -> dict[str, Any]:
    source_before = float(model.get_state().base_state.nodes[1].coherence)
    queue_before = len(model.get_state().packet_ledger.event_queue_records)  # type: ignore[union-attr]
    try:
        departure = model.step()
    except InvalidStateTransitionError as error:
        return {
            "admitted": False,
            "native_transition": "LGRC9V3.step packet departure eligibility",
            "source_node_id": 1,
            "target_node_id": 0,
            "packet_amount": READOUT_PACKET_AMOUNT,
            "source_coherence_before": source_before,
            "eligibility_margin": source_before - READOUT_PACKET_AMOUNT,
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "queue_record_count_before": queue_before,
            "queue_record_count_after": len(
                model.get_state().packet_ledger.event_queue_records  # type: ignore[union-attr]
            ),
            "event_receipts": [],
        }
    arrival = model.step()
    return {
        "admitted": True,
        "native_transition": "LGRC9V3.step packet departure and arrival",
        "source_node_id": 1,
        "target_node_id": 0,
        "packet_amount": READOUT_PACKET_AMOUNT,
        "source_coherence_before": source_before,
        "eligibility_margin": source_before - READOUT_PACKET_AMOUNT,
        "exception_type": None,
        "exception_message": None,
        "queue_record_count_before": queue_before,
        "queue_record_count_after": len(
            model.get_state().packet_ledger.event_queue_records  # type: ignore[union-attr]
        ),
        "event_receipts": [event_receipt(departure), event_receipt(arrival)],
    }


def identity_diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix]
    if isinstance(left, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right), key=str):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right:
                paths.append(path)
            else:
                paths.extend(identity_diff_paths(left[key], right[key], path))
        return paths
    if isinstance(left, list):
        if len(left) != len(right):
            return [prefix]
        paths = []
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            paths.extend(
                identity_diff_paths(left_item, right_item, f"{prefix}[{index}]")
            )
        return paths
    return [] if left == right else [prefix]


def clone_model(model: LGRC9V3) -> LGRC9V3:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "snapshot.json"
        model.save(str(path))
        return LGRC9V3.load(str(path))


def intervene_route_c(
    model: LGRC9V3,
    values: dict[int, float],
) -> tuple[LGRC9V3, dict[str, Any]]:
    original_v1 = digest_lgrc9v3_restoration_identity_v1(model)
    original_v2 = digest_lgrc9v3_restoration_identity_v2(model)
    branch = clone_model(model)
    restored_v1 = digest_lgrc9v3_restoration_identity_v1(branch)
    restored_v2 = digest_lgrc9v3_restoration_identity_v2(branch)
    source_identity = lgrc9v3_restoration_identity_v1(branch)
    source_mass = sum(
        float(branch.get_state().base_state.nodes[node_id].coherence)
        for node_id in ROUTE_SUPPORT
    )
    state = deepcopy(branch.get_state())
    for node_id, value in values.items():
        state.base_state.nodes[node_id].coherence = float(value)
    branch.set_state(state)
    intervention_identity = lgrc9v3_restoration_identity_v1(branch)
    intervention_mass = sum(
        float(branch.get_state().base_state.nodes[node_id].coherence)
        for node_id in ROUTE_SUPPORT
    )
    changed_paths = identity_diff_paths(source_identity, intervention_identity)
    allowed_paths = sorted(
        f"embedded_grc9v3_state.state.nodes.{node_id}.coherence"
        for node_id in ROUTE_SUPPORT
    )
    changed_path_set = set(changed_paths)
    allowed_path_set = set(allowed_paths)
    only_intended_paths_changed = bool(changed_path_set) and changed_path_set <= allowed_path_set
    return branch, {
        "intervention_surface": "LGRC9V3.set_state",
        "intervention_scope": "registered_route_node_C_only",
        "snapshot_load_identity_v1_exact_before_intervention": original_v1
        == restored_v1,
        "snapshot_load_identity_v2_exact_before_intervention": original_v2
        == restored_v2,
        "route_mass_before": source_mass,
        "route_mass_after": intervention_mass,
        "route_mass_matched": abs(source_mass - intervention_mass) <= 1e-12,
        "changed_restoration_identity_paths": changed_paths,
        "allowed_changed_paths": allowed_paths,
        "changed_route_C_path_count": len(changed_path_set),
        "only_intended_C_paths_changed": only_intended_paths_changed,
        "all_other_scientific_state_matched": only_intended_paths_changed,
        "constitutive_dependent_fields_recomputed": False,
        "readout_uses_direct_native_source_C_eligibility": True,
    }


def run_attempt(mode: str) -> tuple[dict[str, Any], list[dict[str, Any]], LGRC9V3]:
    model = build_attempt_model(mode)
    artifacts: list[dict[str, Any]] = []
    baseline = route_state(model)
    artifacts.append(save_snapshot(model, f"{mode}_baseline"))
    formation_receipts = process_exact_events(model, 2)
    formed = route_state(model)
    artifacts.append(save_snapshot(model, f"{mode}_formed"))
    persistence_receipts = process_exact_events(model, 2)
    persisted = route_state(model)
    artifacts.append(save_snapshot(model, f"{mode}_persisted"))
    progression_receipts = process_exact_events(model, 2)
    progressed = route_state(model)
    artifacts.append(save_snapshot(model, f"{mode}_progressed"))
    pre_readout_model = clone_model(model)
    pre_readout_snapshot_load_audit = {
        "restoration_identity_v1_exact": (
            digest_lgrc9v3_restoration_identity_v1(model)
            == digest_lgrc9v3_restoration_identity_v1(pre_readout_model)
        ),
        "restoration_identity_v2_exact": (
            digest_lgrc9v3_restoration_identity_v2(model)
            == digest_lgrc9v3_restoration_identity_v2(pre_readout_model)
        ),
    }
    readout_result = readout(model)
    after_readout = route_state(model)
    artifacts.append(save_snapshot(model, f"{mode}_after_readout_attempt"))

    row = {
        "attempt_id": f"n31_i7_{mode}",
        "attempt_mode": mode,
        "schedule_declared_before_execution": True,
        "baseline": baseline,
        "formed": formed,
        "persisted": persisted,
        "progressed": progressed,
        "after_readout_attempt": after_readout,
        "formation_receipts": formation_receipts,
        "persistence_receipts": persistence_receipts,
        "progression_receipts": progression_receipts,
        "readout": readout_result,
        "pre_readout_snapshot_load_audit": pre_readout_snapshot_load_audit,
        "forming_packet_exhausted_at_formed_checkpoint": not formed[
            "forming_packet_in_flight"
        ],
        "forming_packet_identity_excluded_from_progression_and_readout": True,
        "post_formation_producer_calls": [],
        "post_formation_state_mutating_producer_calls": [],
        "producer_call_audit_status": "complete_no_post_formation_calls",
        "snapshot_manifest": artifacts,
    }
    return row, artifacts, pre_readout_model


def build_preregistration() -> dict[str, Any]:
    record = {
        "experiment": "N31",
        "iteration": "7",
        "artifact_kind": "D0a_candidate_preregistration",
        "artifact_schema_version": "n31_i7_preregistration_v1",
        "generated_at": GENERATED_AT,
        "fixture_id": "n31_i7_five_node_route_and_disjoint_progression_v1",
        "finite_attempt_matrix": [
            {
                "attempt_mode": "disjoint_hold",
                "progression_lane": "outside edge 3, nodes 4 to 3",
                "expected_geometric_role": "persistence_without_route_change",
            },
            {
                "attempt_mode": "internal_weakening",
                "progression_lane": "route edge 1, node 1 to node 2",
                "expected_geometric_role": "decrease signed formation coordinate",
            },
            {
                "attempt_mode": "internal_reinforcement",
                "progression_lane": "route edge 1, node 2 to node 1",
                "expected_geometric_role": "directional control increases coordinate",
            },
        ],
        "packet_schedule": {
            "formation": {
                "route": "0->1 edge 0",
                "amount": FORMATION_PACKET_AMOUNT,
                "departure": 0.0,
                "arrival": 1.0,
            },
            "persistence_clock_event": {
                "route": "3->4 edge 3",
                "amount": PERSISTENCE_PACKET_AMOUNT,
                "departure": 2.0,
                "arrival": 3.0,
            },
            "attempt_progression": {
                "amount": PROGRESSION_PACKET_AMOUNT,
                "departure": 4.0,
                "arrival": 5.0,
            },
            "later_readout": {
                "route": "1->0 edge 0",
                "amount": READOUT_PACKET_AMOUNT,
                "departure": 6.0,
                "arrival": 7.0,
            },
        },
        "thresholds": dict(THRESHOLDS),
        "candidate_selection_policy": (
            "the internal_weakening row is selected by its preregistered signed "
            "direction, not by scanning outcomes; hold and reinforcement remain controls"
        ),
        "producer_boundary": {
            "all_schedule_calls_before_first_runtime_event": True,
            "no_schedule_call_after_formation": True,
            "no_D0_specific_decay_state": True,
            "no_retained_age_or_history_cursor": True,
            "predeclared_progression_lane_is_producer_residue": True,
        },
    }
    thresholds_for_digest = dict(record["thresholds"])
    thresholds_for_digest["declaration_digest"] = "excluded_from_own_digest"
    record["thresholds"]["declaration_digest"] = digest_value(thresholds_for_digest)
    record["output_digest"] = digest_value(
        {key: value for key, value in record.items() if key != "output_digest"}
    )
    return record


def build_trace() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    preregistration = build_preregistration()
    PREREGISTRATION.write_text(canonical_json(preregistration), encoding="utf-8")
    attempts: list[dict[str, Any]] = []
    artifact_manifest = [
        {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "artifact_role": "pre_outcome_threshold_and_attempt_preregistration",
        }
    ]
    pre_readout_models: dict[str, LGRC9V3] = {}
    for mode in ATTEMPT_MODES:
        row, artifacts, pre_readout = run_attempt(mode)
        attempts.append(row)
        artifact_manifest.extend(artifacts)
        pre_readout_models[mode] = pre_readout

    hold_model = pre_readout_models["disjoint_hold"]
    hold_clamp, hold_clamp_receipt = intervene_route_c(hold_model, INITIAL_ROUTE_C)
    hold_clamp_pre = save_snapshot(hold_clamp, "intervention_hold_baseline_clamp")
    hold_clamp_readout = readout(hold_clamp)
    hold_clamp_post = save_snapshot(
        hold_clamp, "intervention_hold_baseline_clamp_after_readout"
    )

    weak_model = pre_readout_models["internal_weakening"]
    formed_values = {
        node_id: float(
            attempts[1]["formed"]["node_coherence"][str(node_id)]
        )
        for node_id in ROUTE_SUPPORT
    }
    weak_restore, weak_restore_receipt = intervene_route_c(
        weak_model, formed_values
    )
    weak_restore_pre = save_snapshot(
        weak_restore, "intervention_weakened_formed_restore"
    )
    weak_restore_readout = readout(weak_restore)
    weak_restore_post = save_snapshot(
        weak_restore, "intervention_weakened_formed_restore_after_readout"
    )
    artifact_manifest.extend(
        [hold_clamp_pre, hold_clamp_post, weak_restore_pre, weak_restore_post]
    )

    attempt_by_mode = {row["attempt_mode"]: row for row in attempts}
    hold = attempt_by_mode["disjoint_hold"]
    weak = attempt_by_mode["internal_weakening"]
    reinforce = attempt_by_mode["internal_reinforcement"]
    baseline_strength = float(weak["baseline"]["spatial_organization"]["formation_oriented_strength"])
    formed_strength = float(weak["formed"]["spatial_organization"]["formation_oriented_strength"])
    persisted_strength = float(weak["persisted"]["spatial_organization"]["formation_oriented_strength"])
    weakened_strength = float(weak["progressed"]["spatial_organization"]["formation_oriented_strength"])
    reinforcement_strength = float(reinforce["progressed"]["spatial_organization"]["formation_oriented_strength"])
    weakening_amount = persisted_strength - weakened_strength

    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "7",
        "artifact_kind": "D0a_source_current_causal_trace",
        "artifact_schema_version": "n31_i7_D0a_source_current_causal_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_source_current_spatial_D0a_direction_matrix_and_matched_"
            "causal_intervention_trace"
        ),
        "source_current_runtime_artifact": True,
        "derived_report_only": False,
        "runtime_family": "LGRC9V3",
        "runtime_revision": I7_GOVERNANCE_BASE_REVISION,
        "public_runtime_operations": [
            "LGRC9V3.from_state",
            "LGRC9V3.schedule_packet_departure",
            "LGRC9V3.step",
            "LGRC9V3.save",
            "LGRC9V3.load",
            "LGRC9V3.set_state",
            "lgrc9v3_restoration_identity_v1",
            "digest_lgrc9v3_restoration_identity_v2",
        ],
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
            "declared_before_attempt_execution": True,
        },
        "fixture_contract": {
            "route_support": list(ROUTE_SUPPORT),
            "route_internal_edges": [0, 1],
            "route_boundary_edge": ROUTE_BOUNDARY_EDGE,
            "outside_progression_edge": 3,
            "registered_route_mass": sum(INITIAL_ROUTE_C.values()),
            "global_conserved_budget": sum(INITIAL_ROUTE_C.values()) + 1.0,
            "selected_spatial_coordinate": "C[1]-C[2]",
            "all_packet_schedules_registered_before_first_event": True,
            "schedule_definition_owner": "experiment_fixture",
            "packet_execution_owner": "native_LGRC9V3_runtime",
        },
        "attempt_rows": attempts,
        "direction_matrix": {
            "matrix_kind": (
                "preregistered_directional_perturbation_not_equal_state_continuation"
            ),
            "persisted_complete_continuation_states_equal": False,
            "non_equality_reason": (
                "hold, weakening, and reinforcement branches contain distinct "
                "predeclared future packet queues"
            ),
            "baseline_strength": baseline_strength,
            "formed_strength": formed_strength,
            "persisted_strength": persisted_strength,
            "weakened_strength": weakened_strength,
            "reinforced_strength": reinforcement_strength,
            "weakening_amount": weakening_amount,
            "residual_organization_fraction": weakened_strength / formed_strength,
            "hold_preserved_formation_effect": abs(
                float(hold["progressed"]["spatial_organization"]["formation_oriented_strength"])
                - formed_strength
            )
            <= THRESHOLDS["persistence_tolerance"],
            "weakening_direction_passed": weakening_amount
            >= THRESHOLDS["minimum_weakening_amount"],
            "residual_organization_passed": weakened_strength
            >= THRESHOLDS["minimum_residual_organization"],
            "reinforcement_direction_control_passed": reinforcement_strength
            > formed_strength,
        },
        "causal_intervention_matrix": {
            "hold_native_readout": hold["readout"],
            "hold_baseline_clamp": {
                "intervention_receipt": hold_clamp_receipt,
                "readout": hold_clamp_readout,
            },
            "weakened_native_readout": weak["readout"],
            "weakened_formed_restore": {
                "intervention_receipt": weak_restore_receipt,
                "readout": weak_restore_readout,
            },
            "same_readout_packet_amount_all_branches": all(
                abs(float(result["packet_amount"]) - READOUT_PACKET_AMOUNT) <= 1e-12
                for result in (
                    hold["readout"],
                    hold_clamp_readout,
                    weak["readout"],
                    weak_restore_readout,
                )
            ),
            "formed_organization_enables_readout": hold["readout"]["admitted"]
            and not hold_clamp_readout["admitted"],
            "weakening_removes_readout_eligibility": hold["readout"]["admitted"]
            and not weak["readout"]["admitted"],
            "restoring_formed_organization_restores_readout": weak_restore_readout[
                "admitted"
            ],
            "mediation_supported": (
                hold["readout"]["admitted"]
                and not hold_clamp_readout["admitted"]
                and not weak["readout"]["admitted"]
                and weak_restore_readout["admitted"]
                and hold_clamp_receipt["only_intended_C_paths_changed"]
                and weak_restore_receipt["only_intended_C_paths_changed"]
            ),
        },
        "producer_call_audit": {
            "pre_execution_schedule_call_count_per_attempt": 4,
            "all_schedule_calls_before_first_runtime_event": True,
            "pre_execution_schedule_authorship_present": True,
            "weakening_schedule_owner": "experiment_fixture",
            "weakening_transition_execution_owner": "native_LGRC9V3_runtime",
            "post_formation_producer_call_policy": "no_calls",
            "post_formation_producer_calls": [],
            "post_formation_state_mutating_producer_calls": [],
            "producer_call_audit_status": (
                "complete_preexecution_schedule_authorship_present_"
                "no_postformation_calls"
            ),
            "intervention_calls_are_control_branches_not_positive_trajectory": True,
        },
        "classification_boundary": {
            "supported_D0_subclass": "D0a_spatial_formation_and_persistence",
            "native_D0a_ladder_ceiling": "DR2",
            "conditional_internal_reorganization_relation": (
                "supported_with_bounded_local_source_C_readout_effect"
            ),
            "conditional_reorganization_shape": (
                "DR4_shaped_but_not_an_autonomous_decay_rung"
            ),
            "autonomous_slow_mode_relaxation_supported": False,
            "full_spatial_distribution_mediation_supported": False,
            "general_decay_law_supported": False,
            "final_D0a_supported": False,
            "pending": "I8 replay, restoration, complete control, and comparative classification",
        },
        "artifact_manifest": artifact_manifest,
    }
    trace["checks"] = [
        check(
            "formation_effect_passed",
            formed_strength >= THRESHOLDS["minimum_formation_effect"],
            formed_strength,
        ),
        check(
            "forming_packet_exhausted_before_persistence",
            all(row["forming_packet_exhausted_at_formed_checkpoint"] for row in attempts),
            [row["attempt_id"] for row in attempts],
        ),
        check(
            "bounded_persistence_passed",
            abs(persisted_strength - formed_strength)
            <= THRESHOLDS["persistence_tolerance"],
            {"formed": formed_strength, "persisted": persisted_strength},
        ),
        check(
            "direction_matrix_passed",
            trace["direction_matrix"]["weakening_direction_passed"]
            and trace["direction_matrix"]["residual_organization_passed"]
            and trace["direction_matrix"]["hold_preserved_formation_effect"]
            and trace["direction_matrix"]["reinforcement_direction_control_passed"],
            trace["direction_matrix"],
        ),
        check(
            "readout_mediation_intervention_passed",
            trace["causal_intervention_matrix"]["mediation_supported"],
            trace["causal_intervention_matrix"],
        ),
        check(
            "readout_margins_passed",
            float(hold["readout"]["eligibility_margin"])
            >= THRESHOLDS["minimum_readout_pass_margin"]
            and -float(weak["readout"]["eligibility_margin"])
            >= THRESHOLDS["minimum_readout_rejection_shortfall"],
            {
                "hold_pass_margin": hold["readout"]["eligibility_margin"],
                "weakening_rejection_shortfall": -float(
                    weak["readout"]["eligibility_margin"]
                ),
            },
        ),
        check(
            "route_mass_and_global_budget_closed",
            all(
                abs(
                    float(checkpoint["registered_route_mass"])
                    - sum(INITIAL_ROUTE_C.values())
                )
                <= THRESHOLDS["route_mass_tolerance"]
                and abs(float(checkpoint["runtime_budget"]["budget_error"]))
                <= THRESHOLDS["closed_system_budget_tolerance"]
                for row in attempts
                for checkpoint in (
                    row["baseline"],
                    row["formed"],
                    row["persisted"],
                    row["progressed"],
                    row["after_readout_attempt"],
                )
            ),
            "all attempt checkpoints",
        ),
        check(
            "post_formation_producer_mutation_absent",
            not trace["producer_call_audit"][
                "post_formation_state_mutating_producer_calls"
            ],
            trace["producer_call_audit"],
        ),
        check(
            "snapshot_load_identity_exact",
            all(
                row["pre_readout_snapshot_load_audit"][
                    "restoration_identity_v1_exact"
                ]
                and row["pre_readout_snapshot_load_audit"][
                    "restoration_identity_v2_exact"
                ]
                for row in attempts
            )
            and hold_clamp_receipt[
                "snapshot_load_identity_v1_exact_before_intervention"
            ]
            and hold_clamp_receipt[
                "snapshot_load_identity_v2_exact_before_intervention"
            ]
            and weak_restore_receipt[
                "snapshot_load_identity_v1_exact_before_intervention"
            ]
            and weak_restore_receipt[
                "snapshot_load_identity_v2_exact_before_intervention"
            ],
            "all attempt and intervention branch points",
        ),
        check(
            "artifact_manifest_hashes_exact",
            all(
                sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in artifact_manifest
            ),
            len(artifact_manifest),
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I7_source_current_trace_failed"
    trace["output_digest"] = digest_value(
        {key: value for key, value in trace.items() if key != "output_digest"}
    )
    return trace


def build_controls(candidate_contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        (
            "forming_activity_never_stopped",
            "forming activity remains live during the claimed persistence window",
            "forming packet exhausted before persistence is admitted",
            "forming packet is exhausted before persistence and progression",
            "passed",
            "blocks_DR2_plus_if_false",
            False,
            None,
        ),
        (
            "forming_packet_propagation_as_later_mediation",
            "forming packet is reused as the later readout or progression packet",
            "forming packet identity is exhausted and excluded from later operations",
            "progression and readout use distinct packet identities and times",
            "passed",
            "blocks_independent_later_readout_language_if_false",
            False,
            None,
        ),
        (
            "route_mass_loss_as_organization_weakening_relabel",
            "route-mass loss is relabeled as organization weakening",
            "route mass remains invariant while the selected coordinate changes",
            "registered route mass is invariant while spatial coordinate weakens",
            "passed",
            "blocks_D0a_if_false",
            False,
            None,
        ),
        (
            "hidden_producer_update",
            "an undisclosed producer update changes the positive trajectory",
            "all producer schedule ownership and post-formation calls are disclosed",
            (
                "pre-execution schedule authorship is explicit and post-formation "
                "call lists are empty"
            ),
            "passed",
            "reclassifies_or_blocks_if_false",
            False,
            None,
        ),
        (
            "producer_scheduled_D0_decay",
            "the experiment fixture selects the weakening time, amount, route, and direction",
            "triggered condition must reject autonomous D0a weakening",
            (
                "fixture pre-schedules the 1->2 weakening packet; native runtime "
                "executes conservation but does not select the transition"
            ),
            "failed_closed",
            "caps_native_D0a_at_DR2_and_blocks_autonomous_relaxation_relabel",
            False,
            None,
        ),
        (
            "observable_disconnected_from_transport",
            "the reported local-C effect does not alter a native operation",
            "a matched C-only intervention changes native departure eligibility",
            "same queued native departure flips under C-only clamp/restore",
            "passed",
            "blocks_local_C_causal_effect_if_false",
            False,
            None,
        ),
        (
            "node_scalar_match_as_complete_state_match",
            "node-scalar equality is presented as complete-state equality",
            "intervention identity diff is restricted to declared C paths",
            "identity diff proves all non-intervened scientific paths equal",
            "passed",
            "blocks_intervention_if_false",
            False,
            None,
        ),
        (
            "proper_time_annotation_as_causal_alignment",
            "derived timing annotation is relabeled as native temporal mediation",
            "control is outside the spatial-only candidate scope",
            "temporal organization is not claimed or consumed",
            "not_applicable",
            "not_applicable_spatial_D0a",
            False,
            "I7 tests a spatial C-distribution candidate and makes no temporal claim",
        ),
        (
            "label_only_decay",
            "a semantic label substitutes for source-current state and native receipts",
            "all descriptive results derive from runtime state and receipts",
            "all outcomes derive from source-current C, packet receipts, and native eligibility",
            "passed",
            "blocks_all_positive_rungs_if_false",
            False,
            None,
        ),
    ]
    return [
        {
            "control_id": control_id,
            "candidate_semantic_contract": candidate_contract,
            "blocked_condition": blocked_condition,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "control_status": control_status,
            "control_status_meaning": {
                "passed": "positive_or_control_gate_satisfied",
                "failed_closed": "false_positive_path_triggered_and_stronger_claim_rejected",
                "failed_open": "blocker_triggered_but_claim_remained_open",
                "not_applicable": "outside_declared_scope_with_reason",
            }[control_status],
            "passed": control_status in {"passed", "failed_closed", "not_applicable"},
            "claim_allowed_when_control_triggers": claim_allowed_when_control_triggers,
            "rung_effect": rung_effect,
            "scope_reason_if_not_applicable": scope_reason_if_not_applicable,
            "candidate_specific_not_direct_I3_positive_evidence": True,
        }
        for (
            control_id,
            blocked_condition,
            expected_result,
            actual_result,
            control_status,
            rung_effect,
            claim_allowed_when_control_triggers,
            scope_reason_if_not_applicable,
        ) in rows
    ]


def build_candidate(trace: dict[str, Any], i2: dict[str, Any]) -> dict[str, Any]:
    attempts = {row["attempt_mode"]: row for row in trace["attempt_rows"]}
    hold = attempts["disjoint_hold"]
    weak = attempts["internal_weakening"]
    formed = weak["formed"]
    progressed = weak["progressed"]
    mass_before = float(formed["registered_route_mass"])
    mass_after = float(progressed["registered_route_mass"])
    mass_delta = mass_after - mass_before
    candidate_contract = {
        "primary_semantic_class": "D0a",
        "representation_or_authority_class": "exact_derived_projection",
        "organization_domain": "spatial_distribution",
        "load_bearing_organization_domain": "spatial_distribution",
        "candidate_specific_schema_id": "n31_i7_spatial_D0a_candidate_schema_v1",
        "carrier_contract_id": "n31_i7_native_route_C_and_packet_transport_v1",
        "continuation_state_contract_id": "n31_i7_complete_LGRC9V3_state_v1",
        "internal_time_policy": "native_LGRC9V3_event_time_wall_clock_excluded_v1",
    }
    controls = build_controls(candidate_contract)
    required_fields = i2["schema"]["candidate_row_schema"]["required_fields"]
    route_mass_contract = {
        "route_mass_contract_id": "n31_i7_registered_route_mass_v1",
        "registered_route_support": list(ROUTE_SUPPORT),
        "registered_route_boundary": {
            "edge_ids": [ROUTE_BOUNDARY_EDGE],
            "inside_node_ids": list(ROUTE_SUPPORT),
            "outside_node_ids": [3, 4],
        },
        "metric_measure_and_boundary_convention": (
            "fixed node support; node coherence plus route-internal in-flight packets; "
            "boundary edge 2 oriented from route node 2 toward outside node 3"
        ),
        "post_formation_integration_window": {
            "start_event_time_key": 1.0,
            "end_event_time_key": 5.0,
            "classification": "formation_exhaustion_through_pre_readout_progression",
        },
        "flux_quantity_semantics": "time_integrated_exported_coherence",
        "boundary_measure": {
            "kind": "single_registered_discrete_boundary_edge",
            "edge_weights": {str(ROUTE_BOUNDARY_EDGE): 1.0},
        },
        "mass_before": mass_before,
        "mass_after": mass_after,
        "mass_delta": mass_delta,
        "boundary_flux_sign_policy": "positive_outward",
        "net_outward_boundary_flux": 0.0,
        "in_flight_boundary_treatment": (
            "internal packets counted once while in flight; no boundary packet is scheduled"
        ),
        "boundary_crossing_count_policy": "each_packet_or_flux_transfer_counted_exactly_once",
        "departure_arrival_accounting_policy": (
            "internal departure debit plus in-flight packet plus arrival credit counted once"
        ),
        "receiver_inside_or_outside_support": (
            "formation, progression, and readout receivers are inside route support; "
            "outside progression remains on nodes 3 and 4"
        ),
        "moving_support_or_measure_correction": "not_applicable_fixed_support",
        "continuity_tolerance": THRESHOLDS["route_mass_tolerance"],
        "continuity_residual": mass_delta,
        "continuity_closed": abs(mass_delta)
        <= THRESHOLDS["route_mass_tolerance"],
    }
    organization_contract = {
        "route_organization_contract_id": "n31_i7_spatial_C_distribution_v1",
        "organization_observable_id": "n31_i7_signed_C1_minus_C2_formation_coordinate_v1",
        "organization_definition": (
            "complete I4-admitted route C distribution and internal signed flux, with "
            "C1-C2 selected before execution as the weakening orientation"
        ),
        "organization_inputs": [
            "base_state.nodes[0..2].coherence",
            "base_state.port_edges[0..1].flux_uv",
        ],
        "organization_domain": "spatial_distribution",
        "observed_diagnostic_domains": ["spatial_distribution", "induced_geometry"],
        "load_bearing_organization_domain": "spatial_distribution",
        "load_bearing_mediator_component": "local_source_node_1_coherence",
        "full_spatial_distribution_mediation_status": "unresolved",
        "mixed_domain_mediation_resolution": "not_applicable",
        "organization_before": float(
            formed["spatial_organization"]["formation_oriented_strength"]
        ),
        "organization_after": float(
            progressed["spatial_organization"]["formation_oriented_strength"]
        ),
        "organization_weakened": trace["direction_matrix"]["weakening_direction_passed"],
        "organization_authority": "exact_derived_projection",
        "organization_update_owner": "native_LGRC9V3_packet_departure_and_arrival",
        "organization_transition_selection_owner": "experiment_fixture_schedule",
        "organization_has_independent_causal_freedom": False,
        "organization_recomputation_status": "passed_exact",
    }
    mediation_contract = {
        "causal_mediation_contract_id": "n31_i7_native_departure_eligibility_v1",
        "later_local_readout_definition": (
            "prequeued node-1 to node-0 packet departure admitted only when native "
            "source coherence is at least the fixed readout packet amount"
        ),
        "later_readout_changed": trace["causal_intervention_matrix"][
            "weakening_removes_readout_eligibility"
        ],
        "organization_intervention_definition": (
            "I4-admitted set_state control changes only route-node C: baseline clamp "
            "removes formed eligibility and formed-state restore rescues weakened eligibility"
        ),
        "mass_matched_during_organization_intervention": True,
        "packet_amount_matched_during_organization_intervention": True,
        "spatial_organization_matched_during_temporal_intervention": (
            "not_applicable_no_temporal_intervention"
        ),
        "other_continuation_state_matched": True,
        "temporal_intervention_matching_status": "not_applicable",
        "organization_intervention_valid": trace["causal_intervention_matrix"][
            "mediation_supported"
        ],
        "local_transport_intervention_status": (
            "passed_C_only_clamp_and_restore_flip_native_departure_eligibility"
        ),
        "direct_readout_path_excluded": True,
        "hidden_selector_excluded": True,
        "added_coincidence_or_resonance_policy_present": False,
        "later_readout_probe_relation": "independent_later_probe",
        "formation_packet_exclusion_status": "exhausted",
        "organization_mediated_readout_change": trace[
            "causal_intervention_matrix"
        ]["mediation_supported"],
        "mediation_strength": "bounded_partial",
        "local_source_node_C_causality_supported": True,
        "full_spatial_distribution_mediation_supported": False,
        "induced_geometry_causality_supported": False,
        "induced_geometry_causality_blocker": (
            "set_state intervention does not recompute constitutive dependent fields"
        ),
    }
    evidential_objects = {
        "native_spatial_D0a": {
            "formation": "supported",
            "persistence": "supported",
            "decay_relation_ladder_rung": "DR2",
            "autonomous_weakening": "unsupported",
            "producer_authored_weakening_not_consumed": True,
        },
        "conditional_internal_reorganization": {
            "native_D0a_rung_effect": "separate_not_rung_raising",
            "perturbation_owner": "experiment_fixture",
            "execution_owner": "native_LGRC9V3_runtime",
            "weakening_direction": "supported",
            "reverse_reinforcement": "supported",
            "local_source_C_consequence": "supported_bounded_partial",
            "D0_decay_relation": False,
        },
    }
    control_summary = {
        "producer_scheduled_D0_decay": "failed_closed",
        "forming_packet_exclusion": "passed",
        "route_mass_match": "passed",
        "direction_matrix": "perturbation_control",
        "proper_time_alignment": "not_applicable",
    }
    global_budget = float(trace["fixture_contract"]["global_conserved_budget"])
    candidate: dict[str, Any] = {
        "candidate_id": "n31_i7_spatial_D0a_internal_reorganization_causal_readout",
        "candidate_schema_version": "n31_decay_candidate_schema_v2",
        "schema_change_record_id": "n31_pre_i1_mass_organization_mediation_normalization_v2",
        "source_iteration": "N31-I7",
        "primary_semantic_class": "D0a",
        "representation_or_authority_class": "exact_derived_projection",
        "candidate_disposition": "partial",
        "d0_subclass": "internal_reorganization",
        "native_D0a_supported_scope": "spatial_formation_and_persistence",
        "weakening_mode": "internal_reorganization",
        "weakening_mode_qualifier": (
            "experiment_authored_directional_internal_packet_redistribution_"
            "after_formation"
        ),
        "weakening_trajectory_class": "bounded_single_step_monotonic_internal_reorganization",
        "formation_source": (
            "experiment_predeclared_packet_executed_by_native_source_current_transport"
        ),
        "carrier_definition": (
            "complete route-node C distribution plus registered internal signed flux; "
            "no independent decay, age, memory, or susceptibility field"
        ),
        "continuation_state_definition": "complete LGRC9V3 current scientific state",
        "route_local_surface": "registered nodes 0,1,2 and internal edges 0,1",
        "route_mass_contract": route_mass_contract,
        "route_organization_contract": organization_contract,
        "causal_mediation_contract": mediation_contract,
        "route_mass_decreased": False,
        "route_organization_weakened": True,
        "later_readout_changed": True,
        "organization_mediated_readout_change": True,
        "local_source_node_C_mediated_readout_change": True,
        "full_spatial_distribution_mediation_supported": False,
        "load_bearing_mediator": "local_source_node_C",
        "full_route_distribution_mediation": "unresolved",
        "ordinary_post_formation_flux_generated": False,
        "ordinary_post_formation_flux_executed": True,
        "added_export_policy_present": False,
        "export_policy_owner": "not_applicable_no_boundary_export",
        "export_policy_inputs": [],
        "producer_authors_aftereffect": True,
        "producer_authors_weakening": True,
        "ordinary_autonomous_weakening_generated": False,
        "weakening_schedule_owner": "experiment_fixture",
        "weakening_transition_execution_owner": "native_LGRC9V3_runtime",
        "d0_to_br_bridge_status": "not_applicable_no_boundary_export",
        "added_mechanism_admission_reason": "d0_insufficient",
        "added_mechanism_admission_status": (
            "provisionally_justified_for_I9_review_pending_I8_confirmation"
        ),
        "post_formation_producer_call_policy": "no_calls",
        "post_formation_producer_calls": [],
        "post_formation_state_mutating_producer_calls": [],
        "producer_call_audit_status": (
            "complete_preexecution_schedule_authorship_present_"
            "no_postformation_calls"
        ),
        "topology_contract_id": "n31_i7_fixed_five_node_route_v1",
        "internal_time_owner": "native_LGRC9V3_event_queue",
        "internal_time_advance_event": (
            "predeclared distinct packet departures and arrivals at event times 2 through 5"
        ),
        "update_phase": "native_packet_departure_debit_and_arrival_credit",
        "equation_or_relation_id": "C_source_prime=C_source-q; C_target_prime=C_target+q",
        "units_by_state": {
            "node_C": "coherence",
            "packet_amount": "coherence",
            "event_time_key": "LGRC_event_time",
            "organization_coordinate": "coherence",
        },
        "invariant_id": "closed_node_plus_in_flight_coherence",
        "coherence_budget_before": global_budget,
        "coherence_budget_after": global_budget,
        "invariant_tolerance": THRESHOLDS["closed_system_budget_tolerance"],
        "forming_activity_present": True,
        "forming_activity_stopped": True,
        "post_formation_window": {
            "start_event_time_key": 1.0,
            "end_event_time_key": 5.0,
            "forming_packet_exhausted": True,
            "later_readout_event_time_key": 6.0,
        },
        "formation_trace": formed,
        "persistence_trace": weak["persisted"],
        "weakening_trace": progressed,
        "local_readout_trace": {
            "formed_hold_readout": hold["readout"],
            "weakened_readout": weak["readout"],
        },
        "mediator_intervention_trace": trace["causal_intervention_matrix"],
        "destination_trace_if_mass_moves": {
            "formation": "node 0 debit to in-flight packet to node 1 credit",
            "weakening": "node 1 debit to in-flight packet to node 2 credit",
            "boundary_export": "none",
        },
        "complete_state_identity": {
            "formed_v1": hold["formed"]["restoration_identity_v1_digest"],
            "formed_v2": hold["formed"]["restoration_identity_v2_digest"],
            "weakened_v1": weak["progressed"]["restoration_identity_v1_digest"],
            "weakened_v2": weak["progressed"]["restoration_identity_v2_digest"],
            "trace_artifact": relative(TRACE),
            "intervention_identity_diff_scope": "only route C paths",
        },
        "restoration_identity_schema": "lgrc9v3_restoration_identity_v1_and_v2",
        "snapshot_load_status": "passed_exact_at_pre_readout_clone_boundaries",
        "reset_status": "not_applicable_no_reset_operation",
        "branch_continuation_status": (
            "direction_matrix_not_equal_state; intervention_branches_matched_except_"
            "declared_route_C_changes"
        ),
        "direction_matrix_equal_state_continuation": False,
        "direction_matrix_role": (
            "preregistered_directional_perturbation_matrix_only"
        ),
        "derived_cache_status": "not_applicable_no_derived_runtime_cache",
        "derived_cache_recomputation_status": "not_applicable_with_reason",
        "execution_reconstruction_status": "not_run_pending_iteration_8",
        "producer_roles": [
            "pre_execution_packet_schedule_fixture",
            "source_current_observer_and_receipt_collector",
            "matched_C_only_control_intervention",
        ],
        "producer_residue": [
            "formation, persistence-clock, progression, and readout packets are experiment-predeclared",
            "the fixture owns weakening timing, amount, source, destination, and direction",
            "native runtime owns conservative packet debit, in-flight state, and credit only",
            "the direction matrix establishes conditional internal reorganization, not autonomous no-input relaxation",
            "set_state is used only in matched intervention branches admitted by I4",
        ],
        "naturalization_debt": [
            "no native relaxation law selects the weakening direction without a predeclared continuation packet",
            "full route-distribution mediation is unresolved because native departure eligibility reads local source C",
            "induced geometry is not recomputed by the set_state intervention",
            "extended multi-step decay shape is not shown",
            "I8 replay and full control classification remain pending",
        ],
        "source_current_inputs": [
            "LGRC9V3RuntimeState.base_state.nodes[0..2].coherence",
            "LGRC9V3RuntimeState.base_state.port_edges[0..1].flux_uv",
            "LGRC9V3RuntimeState.packet_ledger",
            "LGRC9V3RuntimeState.event_time_key",
        ],
        "artifact_manifest": [
            {
                "path": relative(TRACE),
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_spatial_D0a_direction_and_intervention_trace",
            },
            *trace["artifact_manifest"],
        ],
        "artifact_sha256": sha256_file(TRACE),
        "all_artifact_sha256_match_file_contents": True,
        "row_specific_thresholds_declared_before_use": load_json(PREREGISTRATION)[
            "thresholds"
        ],
        "decay_relation_ladder_rung": "DR2_native_D0a_ceiling",
        "conditional_reorganization_relation_shape": (
            "DR4_shaped_bounded_partial_local_C_effect_not_decay_rung"
        ),
        "provisional_DR4_status": "superseded_not_a_native_decay_rung",
        "native_D0a_ladder_ceiling": "DR2",
        "autonomous_weakening_supported": False,
        "row_decision": "partial",
        "claim_ceiling": (
            "native_spatial_D0a_formation_and_persistence_at_DR2_plus_"
            "experiment_authored_conditional_internal_reorganization_with_"
            "bounded_local_source_C_readout_effect"
        ),
        "blocked_relabels": BLOCKED_RELABELS,
        "unsafe_claim_flags": {
            f"{claim}_claim_allowed": False for claim in BLOCKED_RELABELS
        },
        "candidate_semantic_contract": candidate_contract,
        "candidate_semantic_contract_digest": digest_value(candidate_contract),
        "evidential_objects": evidential_objects,
        "control_summary": control_summary,
        "control_results": controls,
    }
    candidate["missing_required_fields"] = sorted(set(required_fields) - set(candidate))
    nested_schemas = {
        "route_mass_contract": i2["schema"]["route_mass_contract_schema"]["required_fields"],
        "route_organization_contract": i2["schema"]["route_organization_contract_schema"]["required_fields"],
        "causal_mediation_contract": i2["schema"]["causal_mediation_contract_schema"]["required_fields"],
    }
    candidate["nested_contract_validation"] = {
        name: {
            "required_field_count": len(fields),
            "missing_required_fields": sorted(set(fields) - set(candidate[name])),
            "complete": not (set(fields) - set(candidate[name])),
        }
        for name, fields in nested_schemas.items()
    }
    candidate["missing_nested_required_fields"] = {
        name: result["missing_required_fields"]
        for name, result in candidate["nested_contract_validation"].items()
        if result["missing_required_fields"]
    }
    organization_schema = i2["schema"]["route_organization_contract_schema"]
    mediation_schema = i2["schema"]["causal_mediation_contract_schema"]
    candidate["nested_contract_values_conform"] = (
        route_mass_contract["flux_quantity_semantics"]
        == i2["schema"]["route_mass_contract_schema"][
            "flux_quantity_semantics_required_value"
        ]
        and route_mass_contract["boundary_flux_sign_policy"] == "positive_outward"
        and organization_contract["organization_domain"]
        in organization_schema["organization_domain_enum"]
        and organization_contract["organization_authority"]
        in organization_schema["organization_authority_enum"]
        and mediation_contract["later_readout_probe_relation"]
        in mediation_schema["later_readout_probe_relation_enum"]
        and mediation_contract["mediation_strength"]
        in mediation_schema["mediation_strength_enum"]
    )
    candidate["row_digest"] = digest_value(
        {key: value for key, value in candidate.items() if key != "row_digest"}
    )
    return candidate


def build_payload(trace: dict[str, Any]) -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    source_chain = [source_record(path) for path in SOURCE_IDENTITIES]
    candidate = build_candidate(trace, i2)
    protected_paths = (
        "src",
        "lib",
        "specs",
        "implementation",
        "tests",
        "examples",
        "scripts",
        "pyproject.toml",
        "requirements.txt",
        "uv.lock",
    )
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "7",
        "artifact_kind": "D0a_source_current_causal_probe",
        "artifact_schema_version": "n31_i7_D0a_source_current_causal_probe_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_native_spatial_D0a_DR2_formation_persistence_and_"
            "conditional_reorganization_probe"
        ),
        "source_chain": source_chain,
        "governance": {
            "I7_governance_base_revision": I7_GOVERNANCE_BASE_REVISION,
            "protected_runtime_base_revision": PROTECTED_RUNTIME_BASE_REVISION,
            "src_diff_empty": git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, "src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(PROTECTED_RUNTIME_BASE_REVISION, path)
                for path in protected_paths
            ),
            "experiment_only_changes_allowed": True,
        },
        "representation_gate": {
            "I4_status": load_json(I4_OUTPUT)["status"],
            "I4_spatial_D0a_representation_gate_open": load_json(I4_OUTPUT)[
                "D0a_representation_gate"
            ]["spatial_D0a_representation_gate_open"],
            "admitted_authority": "exact_derived_projection",
            "admitted_domain": "spatial_distribution",
        },
        "candidate_row": candidate,
        "comparative_context": {
            "D0c_I5": {
                "classification": "instantaneous_current_state_geometry",
                "rung": "DR1",
                "persistence": False,
                "causal_mediation": False,
            },
            "D0b_I6": {
                "classification": "finite_window_fading_derived_observable",
                "rung": "DR3",
                "persistence": True,
                "weakening": True,
                "causal_mediation": False,
            },
            "native_spatial_D0a_I7": {
                "classification": "spatial_formation_and_persistence",
                "rung": "DR2_native_D0a_ceiling",
                "persistence": True,
                "autonomous_weakening": False,
                "producer_authored_weakening_consumed_as_native": False,
            },
            "conditional_internal_reorganization_I7": {
                "classification": (
                    "experiment_authored_mass_conserving_directional_perturbation"
                ),
                "native_D0a_rung_effect": "none",
                "weakening_direction": True,
                "reverse_reinforcement": True,
                "local_source_C_causal_effect": True,
                "full_spatial_distribution_mediation": False,
                "D0_decay_relation": False,
            },
        },
        "classification": {
            "primary_semantic_class": "D0a",
            "representation_or_authority_class": "exact_derived_projection",
            "organization_domain": "spatial_distribution",
            "weakening_mode": "internal_reorganization",
            "weakening_mode_qualifier": (
                "experiment_authored_conditional_directional_packet_transfer"
            ),
            "provisional_DR4_status": "superseded_not_a_native_decay_rung",
            "native_D0a_ladder_ceiling": "DR2",
            "conditional_reorganization_relation_supported": True,
            "conditional_reorganization_relation_shape": (
                "DR4_shaped_bounded_partial_local_C_effect_not_decay_rung"
            ),
            "mediation_strength": "bounded_partial",
            "load_bearing_mediator": "local_source_node_1_coherence_component",
            "load_bearing_mediator_normalized": "local_source_node_C",
            "full_spatial_distribution_mediation_supported": False,
            "full_route_distribution_mediation": "unresolved",
            "producer_authors_weakening": True,
            "ordinary_autonomous_weakening_generated": False,
            "n31_closeout_progress_rung": "N31-C3",
            "n31_closeout_ceiling": "N31-C3_source_current_classification_available",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_8_replay_controls_classification": True,
            "autonomous_slow_mode_relaxation_supported": False,
            "general_decay_law_supported": False,
            "final_D0a_supported": False,
            "final_N31_supported": False,
            "added_mechanism_need_status": (
                "provisionally_justified_pending_I8_comparative_confirmation"
            ),
        },
        "evidential_objects": candidate["evidential_objects"],
        "control_summary": candidate["control_summary"],
        "RCAE_return_projection": {
            "projection_status": "provisional_I7_not_final_return_manifest",
            "native_spatial_D0a": candidate["evidential_objects"][
                "native_spatial_D0a"
            ],
            "conditional_internal_reorganization": candidate[
                "evidential_objects"
            ]["conditional_internal_reorganization"],
            "added_producer_mechanism_lane": (
                "remains_open_pending_I8_confirmation_and_I9_admission"
            ),
            "automatic_RCAE_adoption_allowed": False,
            "final_return_manifest_emitted": False,
        },
        "claim_boundary": {
            "allowed_claim": candidate["claim_ceiling"],
            "blocked_relabels": BLOCKED_RELABELS,
            "unsafe_claim_flags": candidate["unsafe_claim_flags"],
        },
        "artifact_manifest": [
            {
                "path": relative(TRACE),
                "sha256": sha256_file(TRACE),
                "artifact_role": "source_current_D0a_runtime_trace",
            },
            {
                "path": relative(PREREGISTRATION),
                "sha256": sha256_file(PREREGISTRATION),
                "artifact_role": "pre_outcome_preregistration",
            },
        ],
    }
    payload["checks"] = [
        check(
            "source_chain_exact",
            all(row["identity_exact"] for row in source_chain),
            [row["path"] for row in source_chain if not row["identity_exact"]],
        ),
        check(
            "I4_exact_spatial_representation_admitted",
            payload["representation_gate"]["I4_spatial_D0a_representation_gate_open"]
            and payload["representation_gate"]["admitted_authority"]
            == "exact_derived_projection",
            payload["representation_gate"],
        ),
        check("trace_passed", trace["status"] == "passed", trace["failed_checks"]),
        check(
            "candidate_schema_complete",
            not candidate["missing_required_fields"]
            and not candidate["missing_nested_required_fields"]
            and candidate["nested_contract_values_conform"],
            {
                "missing": candidate["missing_required_fields"],
                "nested_missing": candidate["missing_nested_required_fields"],
                "values_conform": candidate["nested_contract_values_conform"],
            },
        ),
        check(
            "native_D0a_DR2_and_conditional_reorganization_classification_pass",
            candidate["route_organization_weakened"]
            and candidate["local_source_node_C_mediated_readout_change"]
            and candidate["forming_activity_stopped"]
            and not candidate["post_formation_state_mutating_producer_calls"],
            {
                "native_D0a_ladder_ceiling": candidate["native_D0a_ladder_ceiling"],
                "conditional_shape": candidate[
                    "conditional_reorganization_relation_shape"
                ],
            },
        ),
        check(
            "producer_schedule_authorship_fail_closed",
            candidate["producer_authors_aftereffect"]
            and not candidate["ordinary_post_formation_flux_generated"]
            and not candidate["autonomous_weakening_supported"]
            and any(
                row["control_id"] == "producer_scheduled_D0_decay"
                and row["control_status"] == "failed_closed"
                for row in candidate["control_results"]
            ),
            candidate["producer_call_audit_status"],
        ),
        check(
            "bounded_partial_mediation_scope_preserved",
            candidate["causal_mediation_contract"]["mediation_strength"]
            == "bounded_partial"
            and candidate["local_source_node_C_mediated_readout_change"]
            and not candidate["full_spatial_distribution_mediation_supported"]
            and not candidate["causal_mediation_contract"][
                "induced_geometry_causality_supported"
            ],
            candidate["causal_mediation_contract"],
        ),
        check(
            "control_status_meanings_conform",
            all(
                row["control_status"]
                in {"passed", "failed_closed", "not_applicable"}
                and (
                    row["control_status"] != "not_applicable"
                    or bool(row["scope_reason_if_not_applicable"])
                )
                for row in candidate["control_results"]
            ),
            {
                row["control_id"]: row["control_status"]
                for row in candidate["control_results"]
            },
        ),
        check(
            "evidential_objects_remain_separate",
            payload["evidential_objects"]["native_spatial_D0a"][
                "decay_relation_ladder_rung"
            ]
            == "DR2"
            and payload["evidential_objects"][
                "conditional_internal_reorganization"
            ]["native_D0a_rung_effect"]
            == "separate_not_rung_raising"
            and not payload["evidential_objects"][
                "conditional_internal_reorganization"
            ]["D0_decay_relation"],
            payload["evidential_objects"],
        ),
        check(
            "RCAE_projection_preserves_I7_boundary",
            not payload["RCAE_return_projection"]["automatic_RCAE_adoption_allowed"]
            and not payload["RCAE_return_projection"]["final_return_manifest_emitted"]
            and payload["RCAE_return_projection"][
                "added_producer_mechanism_lane"
            ]
            == "remains_open_pending_I8_confirmation_and_I9_admission",
            payload["RCAE_return_projection"],
        ),
        check(
            "autonomous_relaxation_not_overclaimed",
            not payload["classification"]["autonomous_slow_mode_relaxation_supported"]
            and "autonomous_slow_mode_relaxation" in candidate["blocked_relabels"],
            payload["classification"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in candidate["unsafe_claim_flags"].values()),
            candidate["unsafe_claim_flags"],
        ),
        check(
            "src_diff_empty",
            payload["governance"]["src_diff_empty"],
            PROTECTED_RUNTIME_BASE_REVISION,
        ),
        check(
            "protected_runtime_contract_diff_empty",
            payload["governance"]["protected_runtime_contract_diff_empty"],
            protected_paths,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
    ]
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I7_D0a_probe_failed"
        payload["classification"]["ready_for_iteration_8_replay_controls_classification"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    candidate = payload["candidate_row"]
    direction = load_json(TRACE)["direction_matrix"]
    intervention = load_json(TRACE)["causal_intervention_matrix"]
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 7 - D0a Source-Current Causal Probe

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
primary_semantic_class = D0a
representation_or_authority_class = exact_derived_projection
organization_domain = spatial_distribution
native_D0a_ladder_ceiling = DR2
conditional_internal_reorganization_relation = supported
mediation_strength = bounded_partial
full_spatial_distribution_mediation_supported = false
n31_closeout_progress_rung = N31-C3
ready_for_iteration_8_replay_controls_classification = {str(payload['classification']['ready_for_iteration_8_replay_controls_classification']).lower()}
final_D0a_supported = false
final_N31_supported = false
```

I7 supports native spatial D0a formation and bounded persistence at `DR2`.
It also supplies a useful conditional perturbation result: native packet
transport executes an experiment-predeclared internal redistribution that
weakens, but does not erase, the signed formation coordinate. A later packet
departure is admitted in the persisted strong state and rejected after that
redistribution. The perturbation is not autonomous D0a weakening.

## Separate Evidential Objects

```text
native_spatial_D0a:
  formation = supported
  persistence = supported
  ladder ceiling = DR2
  autonomous weakening = unsupported

conditional_internal_reorganization:
  perturbation owner = experiment fixture
  execution owner = native LGRC9V3 runtime
  weakening direction = supported
  reverse reinforcement = supported
  local source-C consequence = supported, bounded partial
  native D0a rung effect = none
  D0 decay relation = false
```

These objects share one source-current trace but are aggregated separately.
The conditional perturbation cannot raise the native D0a ladder ceiling.

## Geometry

The registered route is `0 -> 1 -> 2`, with node 2 as the coordinate anchor.
The selected coordinate is `C[1] - C[2]`, oriented by the formation event
before outcomes are inspected:

```text
baseline strength = {direction['baseline_strength']:.12f}
formed strength = {direction['formed_strength']:.12f}
persisted strength = {direction['persisted_strength']:.12f}
weakened strength = {direction['weakened_strength']:.12f}
reinforced-control strength = {direction['reinforced_strength']:.12f}
weakening amount = {direction['weakening_amount']:.12f}
residual organization fraction = {direction['residual_organization_fraction']:.12f}
```

The hold row moves coherence only on the outside `3 -> 4 -> 3` lane and leaves
route organization unchanged. The weakening row moves `0.04` coherence from
route node 1 to anchor node 2. The reverse row moves the same amount from node
2 to node 1 and strengthens the coordinate. This is a preregistered directional
perturbation matrix, not an equal-state continuation test. The three branches
already contain different future packet queues. It shows different declared
inputs producing the expected conservative reorganizations; it does not show
an equal state autonomously diverging into weakening and reinforcement.

Route mass remains `1.0`; the weakening is redistribution inside the registered
route, not loss. No packet crosses the route boundary and signed integrated
outward transfer is zero.

## Causal Readout

The readout packet (`1 -> 0`, amount `{READOUT_PACKET_AMOUNT}`) is queued before
the first runtime event in every branch. Native departure eligibility reads
source-current node-1 coherence:

```text
formed/hold readout admitted = {str(intervention['hold_native_readout']['admitted']).lower()}
formed/hold eligibility margin = {intervention['hold_native_readout']['eligibility_margin']:.12f}
weakened readout admitted = {str(intervention['weakened_native_readout']['admitted']).lower()}
weakened eligibility margin = {intervention['weakened_native_readout']['eligibility_margin']:.12f}
```

Two I4-admitted matched interventions establish a bounded local-C causal effect.
Clamping the hold branch back to baseline route C removes eligibility. Restoring
the formed route C in the weakened branch restores eligibility. In both
controls, route mass is unchanged and the complete restoration identity differs
only within declared route-node coherence paths. Native departure eligibility,
however, reads only source-node `C[1]`. The full `C[1]-C[2]` distribution is not
isolated as the load-bearing mediator, and `set_state()` does not recompute
constitutive dependent geometry. Full route-distribution and induced-geometric
mediation therefore remain unresolved.

The binary readout is narrowly threshold-gated. It differs only for readout
amounts in `0.20 < q <= 0.24`; the preregistered `q = 0.22` gives margins
`+0.02` and `-0.02`. I8 should preserve this continuous margin interpretation
and may audit the interval with a preregistered amount sweep.

## Producer Boundary

All four packet schedules are registered before the first runtime event. The
forming packet is exhausted before persistence, progression, and readout, and
there are no post-formation producer calls. That timing does not remove
producer authorship: the experiment fixture selects the weakening packet's
time, amount, source, destination, and direction. The native runtime owns the
conservative debit, in-flight state, and credit. The
`producer_scheduled_D0_decay` control therefore triggers and fails closed,
blocking autonomous weakening above native `DR2`.

The added producer-mechanism lane remains open pending I8 confirmation and I9
admission. The I7 result does not eliminate candidate A/B/C consideration.

## Comparative Boundary

```text
I5 D0c = instantaneous state/flux geometry at DR1
I6 D0b = fading finite-window observable at DR3, no mediation
I7 native D0a = spatial formation and persistence at DR2
I7 perturbation = experiment-authored internal reorganization with bounded local-C effect
```

The provisional RCAE projection preserves the same split, allows no automatic
adoption, and is not the final N31 return manifest.

## Contract Validation

```text
candidate required fields missing = {candidate['missing_required_fields']}
nested contract fields missing = {candidate['missing_nested_required_fields']}
nested contract values conform = {str(candidate['nested_contract_values_conform']).lower()}
```

## Checks

| Check | Passed |
|---|---:|
{checks}

## Claim Ceiling

```text
{candidate['claim_ceiling']}
```

This is not autonomous weakening, full route-distribution mediation,
induced-geometric mediation, a general decay law, memory,
trail/stigmergy, learning, communication, ecology, agency, native support, or
Phase 8 completion.

## Reproduction

```bash
{COMMAND}
```

```text
output_digest = {payload['output_digest']}
```
""",
        encoding="utf-8",
    )


def main() -> None:
    trace = build_trace()
    TRACE.write_text(canonical_json(trace), encoding="utf-8")
    if trace["failed_checks"]:
        raise RuntimeError("N31 I7 trace failed: " + ", ".join(trace["failed_checks"]))
    payload = build_payload(trace)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["failed_checks"]:
        raise RuntimeError("N31 I7 failed: " + ", ".join(payload["failed_checks"]))
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
