#!/usr/bin/env python3
"""Run I116 binding consumers, low-context replay, and closeout evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pygrc.causal_pathways import (
    BindingLock,
    BindingReceipt,
    CausalPathwayAuthority,
    PathwayBindingSession,
    UnbindableCompositionError,
    sha256_file,
)
from pygrc.core import GRCParams, PortGraphBackend
from pygrc.models import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC_RUNTIME_LEVEL_LGRC2,
    GRC9V3NodeState,
    GRC9V3State,
    PortEdge,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding/i116"
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
POLICY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-binding-conformance.json"
SUMMARY_PATH = EVIDENCE_DIR / "consumer-dry-run-summary.json"
REPLAY_SPEC_PATH = (
    ROOT / "implementation/evidence/causal-pathway-binding/"
    "i116-low-context-consumer-specification.json"
)
REPLAY_LOCK_PATH = EVIDENCE_DIR / "low-context-replay.lock.json"
REPLAY_RECEIPT_PATH = EVIDENCE_DIR / "low-context-replay.receipt.json"
REPLAY_RESULT_PATH = EVIDENCE_DIR / "low-context-replay.result.json"
REPLAY_ORACLE_PATH = EVIDENCE_DIR / "low-context-replay.oracle.json"
CANDIDATE_EVIDENCE_PATH = (
    ROOT / "tests/fixtures/causal_pathway_candidate_mechanism_evidence.json"
)


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _portable_command_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def _load_accepted_authority(
    acceptance_anchor: dict[str, Any],
    trusted_anchor_digest: str,
) -> CausalPathwayAuthority:
    return CausalPathwayAuthority.load(
        ROOT,
        acceptance_anchor=acceptance_anchor,
        trusted_anchor_digest=trusted_anchor_digest,
    )


def _two_node_state() -> GRC9V3State:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source"})
    target = graph.add_node({"label": "target"})
    edge = graph.connect_ports(source, 0, target, 0, {"kind": "route"})
    return GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=1.0),
            target: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge: PortEdge(
                source,
                1,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            )
        },
        base_conductance={edge: 1.0},
        geometric_length={edge: 1.0},
        temporal_delay={edge: 1.0},
        flux_coupling={edge: 0.0},
    )


def _two_node_runtime() -> LGRC9V3:
    return LGRC9V3.from_state(_two_node_state(), {"dt": 1.0})


def _feedback_ready_two_node_runtime() -> LGRC9V3:
    model = LGRC9V3.from_state(
        _two_node_state(),
        {
            "dt": 1.0,
            "causal_modes": {
                "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "explicit_event_time_key",
                "proper_time_accumulation_policy": "local_event_frontier",
                "causal_pulse_substrate_surface_enabled": True,
                "causal_pulse_substrate_surface_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                ),
                "causal_pulse_substrate_surface_validated": False,
            },
        },
    )
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(1,),
        rear_node_ids=(0,),
        feedback_threshold=0.0,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        threshold=0.0,
        packet_amount=0.1,
    )
    return model


def _packet_links(pathway: Any, model: LGRC9V3) -> tuple[Callable[..., Any], ...]:
    return (
        pathway.symbol("packet_schedule", instance=model),
        pathway.symbol("source_debit"),
        pathway.symbol("target_credit"),
    )


def _run_packet_lifecycle(
    model: LGRC9V3,
    links: tuple[Callable[..., Any], ...],
) -> Any:
    schedule, debit, credit = links
    schedule(source_node_id=0, target_node_id=1, edge_id=0, amount=0.25)
    runtime_state = model.get_state()
    ledger = runtime_state.packet_ledger
    if ledger is None or len(ledger.event_queue_records) != 1:
        raise RuntimeError("packet dry run expected one queued departure")
    departure = debit(
        runtime_state.base_state,
        ledger,
        queued_departure=ledger.event_queue_records[0],
    )
    return credit(
        runtime_state.base_state,
        departure.ledger,
        packet_id=departure.packet_record.packet_id,
    )


def _freeze_case(
    *,
    case_id: str,
    lock: BindingLock,
    receipt: BindingReceipt,
    assertions: dict[str, Any],
) -> dict[str, Any]:
    lock_path = EVIDENCE_DIR / f"{case_id}.lock.json"
    receipt_path = EVIDENCE_DIR / f"{case_id}.receipt.json"
    lock.write(lock_path)
    receipt.write(receipt_path)
    return {
        "case_id": case_id,
        "status": "passed",
        "lock_path": str(lock_path.relative_to(ROOT)),
        "lock_digest": lock.digest,
        "receipt_path": str(receipt_path.relative_to(ROOT)),
        "receipt_digest": receipt.digest,
        "assertions": assertions,
    }


def _simple_native(authority: CausalPathwayAuthority) -> dict[str, Any]:
    model = _two_node_runtime()
    session = PathwayBindingSession(authority)
    pathway = session.bind_pathway("lgrc9v3.explicit_packet_transport")
    links = _packet_links(pathway, model)
    lock = session.freeze_lock()
    _run_packet_lifecycle(model, links)
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _freeze_case(
        case_id="01-simple-native-pathway",
        lock=lock,
        receipt=receipt,
        assertions={
            "actual_pathway_ids": [
                item["pathway_id"] for item in record["actual_bound_pathways_used"]
            ],
            "composition_edge_count": 0,
            "claim_status": record["claim_envelope"]["overall_claim_status"],
        },
    )


def _cmp20(authority: CausalPathwayAuthority) -> dict[str, Any]:
    model = _feedback_ready_two_node_runtime()
    session = PathwayBindingSession(authority)
    composition = session.bind_composition("CMP-20")
    producer = composition.pathway("lgrc9v3.feedback_eligibility_producer")
    transport = composition.pathway("lgrc9v3.explicit_packet_transport")
    produce = producer.symbol("feedback_packet_schedule", instance=model)
    links = _packet_links(transport, model)
    lock = session.freeze_lock()
    with composition.evidence_scope():
        production = produce(
            policy="packet_departure_from_feedback_eligibility_policy"
        )
        schedule, debit, credit = links
        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=2.0,
            scheduler_event_index=10,
            packet_index=100,
        )
        runtime_state = model.get_state()
        ledger = runtime_state.packet_ledger
        if ledger is None:
            raise RuntimeError("feedback producer dry run lacks packet ledger")
        produced_event_id = production.production_records[0].scheduled_event_id
        queued_departure = next(
            event
            for event in ledger.event_queue_records
            if event.event_id == produced_event_id
        )
        departure = debit(
            runtime_state.base_state,
            ledger,
            queued_departure=queued_departure,
        )
        credit(
            runtime_state.base_state,
            departure.ledger,
            packet_id=departure.packet_record.packet_id,
        )
    receipt = session.build_receipt()
    record = receipt.to_record()
    flow_witness = record["composition_crossing_witnesses"][0][
        "dataflow_witness"
    ]
    return _freeze_case(
        case_id="02-producer-mediated-cmp20",
        lock=lock,
        receipt=receipt,
        assertions={
            "composition_ids": [
                item["composition_id"]
                for item in record["registered_compositions_exercised"]
            ],
            "dataflow_witness_kind": flow_witness["witness_kind"],
            "runtime_instance_binding_id": flow_witness[
                "runtime_instance_binding_id"
            ],
            "contains_producer_cut": record["claim_envelope"]["contains_producer_cut"],
            "lawful_native_blocked": "lawful_native" in record["blocked_claims"],
        },
    )


def _cmp26(authority: CausalPathwayAuthority) -> dict[str, Any]:
    source_runtime = _two_node_runtime()
    source_state = source_runtime.get_state().base_state
    source_state.nodes[0] = GRC9V3NodeState(coherence=4.0)
    edge = source_state.port_edges[0]
    source_state.port_edges[0] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=edge.conductance,
        flux_uv=2.0,
    )
    grc_model = GRC9V3(
        params=GRCParams.from_mapping(
            {
                "dt": 1.0,
                "evolution": {
                    "lambda_birth": 1.0,
                    "alpha_seed": 0.25,
                    "w_bond": 1.5,
                },
            }
        ),
        state=source_state,
    )
    grc_model.get_state().cached_quantities[
        "grcl9v3_growth_parent_capacity_sources"
    ] = {
        "0": {
            "construct_id": "I116-CMP26-front",
            "inactive_parent_port": 2,
            "propagate_child_front": True,
            "child_front_port": 2,
            "child_front_max_depth": 1,
            "front_generation_depth": 0,
        }
    }
    session = PathwayBindingSession(authority)
    composition = session.bind_composition("CMP-26")
    front = composition.pathway("grc9v3.front_capacity_growth")
    birth = composition.pathway("lgrc9v3.boundary_birth")
    eligible = front.symbol("front_capacity_growth_eligibility", instance=grc_model)
    propagate = front.symbol("front_propagation", instance=grc_model)
    crossing = composition.crossing(source_instance=grc_model)
    produce = birth.symbol(
        "birth_trial_production",
        instance=crossing.result_reference,
    )
    commit = birth.symbol(
        "birth_trial_commit",
        instance=crossing.result_reference,
    )
    lock = session.freeze_lock()
    with composition.evidence_scope():
        eligible()
        propagate(parent_node_id=0, parent_port_id=2, child_node_id=1)
        lgrc_model = crossing(grc_model)
        produce(policy="boundary_birth_trial_policy")
        commit(
            parent_node_id=0,
            parent_port_id=2,
            outward_flux_pressure=1.0,
            rng_sample=0.0,
        )
    receipt = session.build_receipt()
    record = receipt.to_record()
    edge = record["pathway_use_graph"]["edges"][0]
    return _freeze_case(
        case_id="03-explicit-adapter-cmp26",
        lock=lock,
        receipt=receipt,
        assertions={
            "composition_status": edge["composition_status"],
            "adapter_id": edge["adapter_id"],
            "adapter_owner": edge["adapter_owner"],
            "contains_adapter_cut": record["claim_envelope"]["contains_adapter_cut"],
            "adapter_result_is_target_instance": (
                crossing.result_reference.resolve() is lgrc_model
            ),
            "crossing_invocation_count": len(
                record["actual_composition_crossing_invocations"]
            ),
        },
    )


def _diagnostic(authority: CausalPathwayAuthority) -> dict[str, Any]:
    model = _two_node_runtime()
    diagnostic_model = GRC9V3(
        params=model.get_params(),
        state=model.get_state().base_state,
    )
    session = PathwayBindingSession(authority)
    composition = session.bind_composition("CMP-04")
    diagnostic = composition.pathway("lgrc9v3.diagnostic_grc_reconstruction")
    prepare = diagnostic.symbol("diagnostic_model_construction")
    rebuild = diagnostic.symbol("diagnostic_rebuild", instance=diagnostic_model)
    lock = session.freeze_lock()
    with composition.evidence_scope():
        prepare(model)
        rebuild()
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _freeze_case(
        case_id="04-diagnostic-only-cmp04",
        lock=lock,
        receipt=receipt,
        assertions={
            "contains_diagnostic_only_relation": record["claim_envelope"][
                "contains_diagnostic_only_relation"
            ],
            "claim_status": record["claim_envelope"]["overall_claim_status"],
            "blocked_claims": record["blocked_claims"],
            "composition_edge_count": len(record["pathway_use_graph"]["edges"]),
            "composition_witness_count": len(
                record["composition_crossing_witnesses"]
            ),
            "composition_declared_unused": composition.binding_id
            in record["declared_but_unused"]["composition_binding_ids"],
        },
    )


def _ambiguous(authority: CausalPathwayAuthority) -> dict[str, Any]:
    selector = _load_json(ROOT / "specs/grc-lgrc-causal-pathway-selection-guide.json")
    selected = next(
        case
        for case in selector["worked_cases"]
        if case["resolution_kind"] == "ambiguous_registered_crossing"
    )
    session = PathwayBindingSession(authority)
    for index, pathway_id in enumerate(selected["selected_pathway_ids"]):
        session.bind_pathway(pathway_id, binding_id=f"ambiguous-endpoint:{index}")
    lock = session.freeze_lock()
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _freeze_case(
        case_id="05-ambiguous-crossing-not-selected",
        lock=lock,
        receipt=receipt,
        assertions={
            "registered_alternatives_retained": selected["registered_alternatives"],
            "registered_compositions_exercised": [],
            "graph_edge_count": len(record["pathway_use_graph"]["edges"]),
            "claim_qualified": record["claim_qualified"],
        },
    )


def _expected_rejection(
    authority: CausalPathwayAuthority,
    *,
    case_id: str,
    composition_id: str,
    expected_status: str,
) -> dict[str, Any]:
    session = PathwayBindingSession(authority)
    try:
        session.bind_composition(composition_id)
    except UnbindableCompositionError as exc:
        return {
            "case_id": case_id,
            "status": "passed",
            "composition_id": composition_id,
            "matrix_status": expected_status,
            "rejection_type": type(exc).__name__,
            "rejection_message": str(exc),
            "accepted_as_admitted": False,
        }
    raise RuntimeError(f"{composition_id} unexpectedly bound as executable")


def _candidate(authority: CausalPathwayAuthority) -> dict[str, Any]:
    model = _two_node_runtime()
    session = PathwayBindingSession(authority)
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    restoration = session.bind_pathway(
        "pygrc.restoration_replay_identity",
        stage_ids=("snapshot_serialization",),
    )
    schedule = packet.symbol("packet_schedule", instance=model)
    snapshot = restoration.symbol("snapshot_serialization", instance=model)
    candidate = session.declare_candidate(
        candidate_id="experiment.i116.packet_to_snapshot_relation",
        candidate_kind="composition",
        purpose="Bounded I116 unregistered-candidate dry run.",
        owner="i116_fixture",
        consumed_pathway_ids=(packet.pathway_id, restoration.pathway_id),
        proposed_source_pathway_id=packet.pathway_id,
        proposed_target_pathway_id=restoration.pathway_id,
        proposed_relation="fixture-only post-packet snapshot relation",
        evidence_owner="i116_fixture",
        mechanism_evidence={
            "evidence_kind": "content_addressed_artifact",
            "mechanism_id": "fixture.packet_schedule_then_snapshot",
            "path": str(CANDIDATE_EVIDENCE_PATH.relative_to(ROOT)),
            "sha256": sha256_file(CANDIDATE_EVIDENCE_PATH),
        },
    )
    lock = session.freeze_lock()
    with candidate.evidence_scope():
        schedule(source_node_id=0, target_node_id=1, edge_id=0, amount=0.25)
        snapshot()
    session.record_candidate_use(candidate.candidate_id)
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _freeze_case(
        case_id="08-unregistered-candidate",
        lock=lock,
        receipt=receipt,
        assertions={
            "candidate_id": candidate.candidate_id,
            "experimental_unregistered": record["claim_envelope"][
                "experimental_unregistered"
            ],
            "promotion_status": candidate.promotion_status,
            "candidate_edge_kind": record["pathway_use_graph"]["edges"][0]["edge_kind"],
        },
    )


def _dynamic(authority: CausalPathwayAuthority) -> dict[str, Any]:
    model = _two_node_runtime()
    grc_model = GRC9V3(
        params=GRCParams.from_mapping({"dt": 1.0}),
        state=model.get_state().base_state,
    )
    session = PathwayBindingSession(authority)
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    restoration = session.bind_pathway(
        "pygrc.restoration_replay_identity",
        stage_ids=("snapshot_serialization",),
    )
    packet.symbol("packet_schedule", instance=model)
    snapshot = restoration.symbol("snapshot_serialization", instance=model)
    unrelated = session.bind_pathway(
        "grc9v3.synchronous_update_cycle",
        stage_ids=("continuity_and_invariants",),
    )
    continuity = unrelated.symbol(
        "continuity_and_invariants",
        instance=grc_model,
    )
    alternatives = session.declare_alternatives(
        alternative_set_id="i116.consumer-branch",
        pathway_ids=(packet.pathway_id, restoration.pathway_id),
        selection_authority="i116_consumer_boolean",
    )
    lock = session.freeze_lock()
    continuity()
    with alternatives.selection_scope():
        snapshot()
    receipt = session.build_receipt()
    record = receipt.to_record()
    actual = record["allowed_pathway_alternatives_actual_use"][0]
    return _freeze_case(
        case_id="09-dynamic-a-b-choice",
        lock=lock,
        receipt=receipt,
        assertions={
            "allowed_pathway_ids": actual["allowed_pathway_ids"],
            "actual_pathway_ids_used": actual["actual_pathway_ids_used"],
            "selected_pathway_ids": actual["selected_pathway_ids"],
            "selection_scope_count": len(actual["selection_scopes"]),
            "selection_authority": actual["selection_authority"],
            "unrelated_pathway_used_outside_scope": any(
                invocation["pathway_id"] == unrelated.pathway_id
                and invocation["alternative_selection_scope_id"] is None
                for invocation in record["actual_stage_symbol_invocations"]
            ),
            "binder_selected": record["semantic_selection_performed_by_binder"],
        },
    )


def _multi_edge(authority: CausalPathwayAuthority) -> dict[str, Any]:
    packet_model = _feedback_ready_two_node_runtime()
    diagnostic_runtime = _two_node_runtime()
    diagnostic_model = GRC9V3(
        params=diagnostic_runtime.get_params(),
        state=diagnostic_runtime.get_state().base_state,
    )
    session = PathwayBindingSession(authority)
    producer_composition = session.bind_composition("CMP-20")
    diagnostic_composition = session.bind_composition("CMP-04")
    producer = producer_composition.pathway("lgrc9v3.feedback_eligibility_producer")
    transport = producer_composition.pathway("lgrc9v3.explicit_packet_transport")
    produce = producer.symbol("feedback_packet_schedule", instance=packet_model)
    packet_links = _packet_links(transport, packet_model)
    diagnostic = diagnostic_composition.pathway("lgrc9v3.diagnostic_grc_reconstruction")
    prepare = diagnostic.symbol("diagnostic_model_construction")
    rebuild = diagnostic.symbol("diagnostic_rebuild", instance=diagnostic_model)
    lock = session.freeze_lock()
    with producer_composition.evidence_scope():
        production = produce(
            policy="packet_departure_from_feedback_eligibility_policy"
        )
        schedule, debit, credit = packet_links
        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
            departure_event_time_key=2.0,
            scheduler_event_index=10,
            packet_index=100,
        )
        runtime_state = packet_model.get_state()
        ledger = runtime_state.packet_ledger
        if ledger is None:
            raise RuntimeError("multi-edge producer dry run lacks packet ledger")
        produced_event_id = production.production_records[0].scheduled_event_id
        queued_departure = next(
            event
            for event in ledger.event_queue_records
            if event.event_id == produced_event_id
        )
        departure = debit(
            runtime_state.base_state,
            ledger,
            queued_departure=queued_departure,
        )
        credit(
            runtime_state.base_state,
            departure.ledger,
            packet_id=departure.packet_record.packet_id,
        )
    with diagnostic_composition.evidence_scope():
        prepare(diagnostic_runtime)
        rebuild()
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _freeze_case(
        case_id="10-multi-edge-use-graph",
        lock=lock,
        receipt=receipt,
        assertions={
            "edge_count": len(record["pathway_use_graph"]["edges"]),
            "composition_ids": sorted(
                edge["composition_id"] for edge in record["pathway_use_graph"]["edges"]
            ),
            "larger_chain_claim_synthesized": record["pathway_use_graph"][
                "larger_chain_claim_synthesized"
            ],
            "synthesized_chain_claim": record["claim_envelope"][
                "synthesized_chain_claim"
            ],
        },
    )


def _run_low_context_replay(
    checker: Any,
    policy: dict[str, Any],
    acceptance_anchor_path: Path,
    trusted_anchor_digest: str,
) -> dict[str, Any]:
    command = [
        ".venv/bin/python",
        "examples/causal_pathway_binding_low_context_consumer.py",
        "--specification",
        str(REPLAY_SPEC_PATH.relative_to(ROOT)),
        "--lock",
        str(REPLAY_LOCK_PATH.relative_to(ROOT)),
        "--receipt",
        str(REPLAY_RECEIPT_PATH.relative_to(ROOT)),
        "--result",
        str(REPLAY_RESULT_PATH.relative_to(ROOT)),
        "--acceptance-anchor",
        _portable_command_path(acceptance_anchor_path),
        "--trusted-anchor-digest",
        trusted_anchor_digest,
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout)
    result = _load_json(REPLAY_RESULT_PATH)
    receipt = _load_json(REPLAY_RECEIPT_PATH)
    selector = _load_json(ROOT / "specs/grc-lgrc-causal-pathway-selection-guide.json")
    specification = _load_json(REPLAY_SPEC_PATH)
    semantic_fields = (
        "demand",
        "required_temporal_semantics",
        "route_relation",
        "retained_relation",
    )
    oracle_case = next(
        case
        for case in selector["worked_cases"]
        if all(case[field] == specification[field] for field in semantic_fields)
    )
    actual_pathway = receipt["actual_bound_pathways_used"][0]
    oracle = {
        "artifact": "I116 low-context replay post-freeze identity oracle",
        "schema_version": "i116_low_context_replay_oracle_v1",
        "oracle_created_after_consumer_replay": True,
        "oracle_consumed_by_consumer": False,
        "expected_pathway_ids": oracle_case["selected_pathway_ids"],
        "expected_composition_ids": [],
        "expected_stage_ids": [
            stage["stage_id"]
            for stage in next(
                pathway
                for pathway in _load_json(
                    ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
                )["pathways"]
                if pathway["pathway_id"] == oracle_case["selected_pathway_ids"][0]
            )["stage_sequence"]
        ],
        "actual_pathway_ids": [actual_pathway["pathway_id"]],
        "actual_composition_ids": [
            item["composition_id"]
            for item in receipt["registered_compositions_exercised"]
        ],
        "actual_stage_ids": actual_pathway["actual_stage_ids"],
        "lock_digest": result["lock_digest"],
        "receipt_digest": result["receipt_digest"],
    }
    oracle["identity_match"] = (
        oracle["actual_pathway_ids"] == oracle["expected_pathway_ids"]
        and oracle["actual_composition_ids"] == oracle["expected_composition_ids"]
        and oracle["actual_stage_ids"] == oracle["expected_stage_ids"]
    )
    oracle["oracle_digest"] = checker.canonical_digest(oracle)
    _write_json(REPLAY_ORACLE_PATH, oracle)
    conformance = checker.validate_bundle(
        ROOT,
        checker.load_bundle(
            ROOT,
            lock_path=REPLAY_LOCK_PATH,
            receipt_path=REPLAY_RECEIPT_PATH,
        ),
        policy,
        acceptance_anchor=_load_json(acceptance_anchor_path),
        trusted_anchor_digest=trusted_anchor_digest,
    )
    if not oracle["identity_match"] or conformance["status"] != "passed":
        raise RuntimeError("low-context replay or post-freeze oracle failed")
    return {
        "status": "passed",
        "consumer_command": command,
        "consumer_input_contains_expected_ids": False,
        "consumer_result_path": str(REPLAY_RESULT_PATH.relative_to(ROOT)),
        "oracle_path": str(REPLAY_ORACLE_PATH.relative_to(ROOT)),
        "oracle_digest": oracle["oracle_digest"],
        "identity_match": oracle["identity_match"],
        "binding_conformance_passed": True,
    }


def main(
    *,
    acceptance_anchor_path: Path,
    trusted_anchor_digest: str,
) -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    acceptance_anchor = _load_json(acceptance_anchor_path)
    authority = _load_accepted_authority(
        acceptance_anchor,
        trusted_anchor_digest,
    )
    checker = _load_module("binding_conformance_i116", CHECKER_PATH)
    policy = _load_json(POLICY_PATH)
    cases = [
        _simple_native(authority),
        _cmp20(authority),
        _cmp26(authority),
        _diagnostic(authority),
        _ambiguous(authority),
        _expected_rejection(
            authority,
            case_id="06-unsupported-crossing-rejected",
            composition_id="CMP-06",
            expected_status="unsupported_missing_crossing",
        ),
        _expected_rejection(
            authority,
            case_id="07-invalid-relabel-rejected",
            composition_id="CMP-05",
            expected_status="invalid_relabel",
        ),
        _candidate(authority),
        _dynamic(authority),
        _multi_edge(authority),
    ]
    conformance_rows = []
    for case in cases:
        if "lock_path" not in case:
            continue
        outcome = checker.validate_bundle(
            ROOT,
            checker.load_bundle(
                ROOT,
                lock_path=ROOT / case["lock_path"],
                receipt_path=ROOT / case["receipt_path"],
            ),
            policy,
            acceptance_anchor=acceptance_anchor,
            trusted_anchor_digest=trusted_anchor_digest,
        )
        conformance_rows.append(
            {
                "case_id": case["case_id"],
                "status": outcome["status"],
                "issue_count": outcome["issue_count"],
            }
        )
    if any(row["status"] != "passed" for row in conformance_rows):
        raise RuntimeError(json.dumps(conformance_rows, indent=2))
    replay = _run_low_context_replay(
        checker,
        policy,
        acceptance_anchor_path,
        trusted_anchor_digest,
    )
    summary = {
        "artifact": "Phase 8 GRC/LGRC causal pathway binding I116 consumer dry runs",
        "schema_version": "phase8_grclgrc_causal_pathway_binding_i116_dry_runs_v1",
        "iteration": 116,
        "case_count": len(cases),
        "passed_case_count": sum(case["status"] == "passed" for case in cases),
        "cases": cases,
        "binding_conformance": conformance_rows,
        "low_context_replay": replay,
        "runtime_behavior_changed": False,
        "status": (
            "passed"
            if all(case["status"] == "passed" for case in cases)
            and replay["status"] == "passed"
            else "failed"
        ),
    }
    summary["summary_digest"] = checker.canonical_digest(summary)
    _write_json(SUMMARY_PATH, summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance-anchor", type=Path, required=True)
    parser.add_argument("--trusted-anchor-digest", required=True)
    arguments = parser.parse_args()
    raise SystemExit(
        main(
            acceptance_anchor_path=arguments.acceptance_anchor,
            trusted_anchor_digest=arguments.trusted_anchor_digest,
        )
    )
