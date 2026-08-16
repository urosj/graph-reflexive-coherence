#!/usr/bin/env python3
"""Run the prospectively frozen Phase 8 C0/C1 matrix exactly once."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "implementation"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_freeze(freeze: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    verified: list[dict[str, str]] = []
    for item in freeze["files"]:
        path = ROOT / str(item["path"])
        actual = sha256_file(path) if path.is_file() else "missing"
        record = {
            "path": str(item["path"]),
            "expected": str(item["sha256"]),
            "actual": actual,
        }
        (verified if actual == item["sha256"] else failures).append(record)
    if failures:
        raise RuntimeError(f"execution freeze verification failed: {failures}")
    return {
        "passed": True,
        "verified_count": len(verified),
        "failure_count": 0,
        "failures": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite claim-bearing output: {output}")

    registration_path = IMPLEMENTATION / (
        "Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Reregistration.json"
    )
    freeze_path = IMPLEMENTATION / (
        "Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1ExecutionFreeze002.json"
    )
    registration = load_json(registration_path)
    freeze = load_json(freeze_path)
    freeze_result = verify_freeze(freeze)

    sys.path.insert(0, str(ROOT / "src"))
    from pygrc.core import PortGraphBackend
    from pygrc.models import (
        GRC9V3,
        GRC9V3NodeState,
        GRC9V3State,
        LGRC9V3,
        PortEdge,
    )

    fixture = registration["fixture"]
    tolerances = registration["tolerances"]
    params = fixture["params"]
    float_tol = float(tolerances["float_equality"])
    funding_tol = float(tolerances["funding"])
    flux_zero = float(tolerances["flux_zero"])

    def build_state(labels: tuple[str, str, str] = ("centre", "left", "right")) -> Any:
        coherence = tuple(float(x) for x in fixture["initial_coherence"])
        conductance = tuple(float(x) for x in fixture["base_conductance"])
        prior_flux = tuple(float(x) for x in fixture["prior_flux"])
        graph = PortGraphBackend()
        node_0 = graph.add_node({"label": labels[0]})
        node_1 = graph.add_node({"label": labels[1]})
        node_2 = graph.add_node({"label": labels[2]})
        edge_01 = graph.connect_ports(node_0, 0, node_1, 0, {"kind": "left"})
        edge_02 = graph.connect_ports(node_0, 1, node_2, 0, {"kind": "right"})
        return GRC9V3State(
            topology=graph,
            nodes={
                node_0: GRC9V3NodeState(
                    coherence=coherence[0], basin_mass=coherence[0], basin_id=0
                ),
                node_1: GRC9V3NodeState(
                    coherence=coherence[1], basin_mass=coherence[1], basin_id=1
                ),
                node_2: GRC9V3NodeState(
                    coherence=coherence[2], basin_mass=coherence[2], basin_id=2
                ),
            },
            port_edges={
                edge_01: PortEdge(node_0, 1, node_1, 1, conductance[0], prior_flux[0]),
                edge_02: PortEdge(node_0, 2, node_2, 1, conductance[1], prior_flux[1]),
            },
            base_conductance={edge_01: conductance[0], edge_02: conductance[1]},
            geometric_length={edge_01: 1.0, edge_02: 1.0},
            temporal_delay={edge_01: 1.0, edge_02: 1.0},
            flux_coupling={edge_01: abs(prior_flux[0]), edge_02: abs(prior_flux[1])},
            budget_target=float(fixture["budget_target"]),
        )

    def coherence_map(model: Any) -> dict[str, float]:
        state = model.get_state().base_state
        return {
            str(node_id): float(state.nodes[node_id].coherence)
            for node_id in sorted(state.nodes)
        }

    def source_state_record(model: Any) -> dict[str, Any]:
        state = model.get_state().base_state
        record = {
            "coherence": coherence_map(model),
            "base_conductance": {
                str(edge_id): float(value)
                for edge_id, value in sorted(state.base_conductance.items())
            },
            "topology_nodes": sorted(int(x) for x in state.topology.iter_live_node_ids()),
            "topology_edges": sorted(int(x) for x in state.topology.iter_live_edge_ids()),
            "basin_ids": {
                str(node_id): state.nodes[node_id].basin_id
                for node_id in sorted(state.nodes)
            },
        }
        record["digest"] = digest_json(record)
        return record

    def reconstruct(model: Any) -> tuple[Any, dict[str, Any]]:
        grc = GRC9V3(
            params=model.get_params(), state=deepcopy(model.get_state().base_state)
        )
        grc.rebuild_differential_state()
        grc.rebuild_transport_state()
        grc.rebuild_differential_state()
        grc.rebuild_identity_state()
        grc.rebuild_choice_state()
        state = grc.get_state()
        record = {
            "coherence": {
                str(node_id): float(state.nodes[node_id].coherence)
                for node_id in sorted(state.nodes)
            },
            "potential": {
                str(node_id): float(state.potential.get(node_id, 0.0))
                for node_id in sorted(state.nodes)
            },
            "flux": {
                str(edge_id): float(state.port_edges[edge_id].flux_uv)
                for edge_id in sorted(state.port_edges)
            },
            "sink_set": sorted(int(x) for x in state.sink_set),
            "choice_state": deepcopy(state.cached_quantities.get("choice_state", {})),
            "reconstruction_count": 1,
        }
        record["digest"] = digest_json(record)
        return state, record

    def build_proposal(
        model: Any,
        *,
        trigger_node_id: int,
        integration_scale: float = 1.0,
        reverse_direction: bool = False,
        forced_action_node: int | None = None,
        stale_source_digest: str | None = None,
    ) -> dict[str, Any]:
        source = source_state_record(model)
        if stale_source_digest is not None and stale_source_digest != source["digest"]:
            return {
                "status": "rejected_stale_proposal",
                "source_state_digest": source["digest"],
                "proposal_source_state_digest": stale_source_digest,
                "packets": [],
            }
        action_node = trigger_node_id if forced_action_node is None else forced_action_node
        if int(action_node) != int(trigger_node_id):
            return {
                "status": "rejected_scope_leak",
                "trigger_node_id": int(trigger_node_id),
                "action_node_id": int(action_node),
                "source_state_digest": source["digest"],
                "packets": [],
            }
        grc_state, geometry = reconstruct(model)
        packets: list[dict[str, Any]] = []
        for edge_id, edge in sorted(grc_state.port_edges.items()):
            flux = float(edge.flux_uv)
            if abs(flux) <= flux_zero:
                continue
            source_node, target_node = (
                (int(edge.node_u), int(edge.node_v))
                if flux > 0.0
                else (int(edge.node_v), int(edge.node_u))
            )
            if reverse_direction:
                source_node, target_node = target_node, source_node
            if source_node != int(action_node):
                continue
            amount = (
                float(fixture["integration_amount"])
                * float(integration_scale)
                * abs(flux)
            )
            if amount > flux_zero:
                packets.append(
                    {
                        "edge_id": int(edge_id),
                        "source_node_id": source_node,
                        "target_node_id": target_node,
                        "amount": amount,
                        "flux_uv": flux,
                    }
                )
        required = sum(row["amount"] for row in packets)
        available = float(grc_state.nodes[action_node].coherence)
        funded = required <= available + funding_tol
        proposal = {
            "status": "eligible" if funded else "rejected_underfunded",
            "trigger_node_id": int(trigger_node_id),
            "action_node_id": int(action_node),
            "source_state_digest": source["digest"],
            "geometry": geometry,
            "integration_scale": float(integration_scale),
            "reverse_direction": bool(reverse_direction),
            "packets": packets if funded else [],
            "proposed_packets_before_funding": packets,
            "required_funding": required,
            "available_funding": available,
            "direct_funding_passed": funded,
        }
        proposal["digest"] = digest_json(proposal)
        return proposal

    def schedule_proposal(model: Any, proposal: Mapping[str, Any], counter: list[int]) -> int:
        if proposal.get("status") != "eligible":
            return 0
        scheduled = 0
        now = float(model.get_state().event_time_key)
        for packet in proposal["packets"]:
            counter[0] += 1
            model.schedule_packet_departure(
                source_node_id=int(packet["source_node_id"]),
                target_node_id=int(packet["target_node_id"]),
                edge_id=int(packet["edge_id"]),
                amount=float(packet["amount"]),
                departure_event_time_key=now
                + float(fixture["generated_departure_offset"]),
                arrival_event_time_key=now
                + float(fixture["generated_arrival_offset"]),
                scheduler_event_index=1000 + counter[0] * 10,
                packet_index=1000 + counter[0],
                source_lineage_id="c1-geometry-generated",
                target_lineage_id="c1-geometry-generated",
            )
            scheduled += 1
        return scheduled

    def schedule_exogenous(model: Any, history: str) -> None:
        amount = float(fixture["exogenous_packet_amount"])
        same_frontier = history.startswith("F")
        order = [1, 2] if history.endswith("12") else [2, 1]
        arrivals = (
            [float(fixture["same_frontier_arrival_time"])] * 2
            if same_frontier
            else [float(x) for x in fixture["non_tied_arrival_times"]]
        )
        for index, (source_node, arrival) in enumerate(zip(order, arrivals, strict=True)):
            model.schedule_packet_departure(
                source_node_id=source_node,
                target_node_id=0,
                edge_id=0 if source_node == 1 else 1,
                amount=amount,
                departure_event_time_key=float(fixture["exogenous_departure_time"]),
                arrival_event_time_key=arrival,
                scheduler_event_index=10 + index * 10,
                packet_index=index,
                source_lineage_id=f"c1-exogenous-{history}-{index}",
                target_lineage_id="c1-centre",
            )

    def event_record(model: Any, result: Any) -> dict[str, Any]:
        state = model.get_state()
        processing = state.packet_processing_log[-1]
        record = {
            "step_index": int(result.step_index),
            "time": float(result.time),
            "processed_event": processing.processed_event.to_record(),
            "packet_record": processing.packet_record.to_record(),
            "budget_before": float(processing.budget_before),
            "budget_after": float(processing.budget_after),
            "budget_error": float(processing.budget_error),
            "coherence": coherence_map(model),
            "queue_length": len(state.packet_ledger.event_queue_records),
            "in_flight_packet_total": float(state.packet_ledger.in_flight_packet_total),
        }
        record["digest"] = digest_json(record)
        return record

    def run_arm(
        arm_id: str,
        *,
        history: str,
        mode: str,
        labels: tuple[str, str, str] = ("centre", "left", "right"),
        integration_scale: float = 1.0,
        reverse_direction: bool = False,
        restore_after_first_trigger: bool = False,
    ) -> dict[str, Any]:
        base = build_state(labels)
        base_model = GRC9V3.from_state(base, params)
        model = LGRC9V3.from_state(base_model.get_state(), base_model.get_params())
        initial = source_state_record(model)
        schedule_exogenous(model, history)
        events: list[dict[str, Any]] = []
        proposals: list[dict[str, Any]] = []
        trigger_count = 0
        generated_counter = [0]
        restored = False
        snapshot_sha256: str | None = None
        limit = int(registration["execution_policy"]["runtime_event_limit_per_arm"])

        def trigger() -> None:
            nonlocal model, trigger_count, restored, snapshot_sha256
            trigger_count += 1
            if mode == "geometry_off":
                proposals.append({"status": "geometry_off", "packets": []})
                return
            proposal = build_proposal(
                model,
                trigger_node_id=0,
                integration_scale=integration_scale,
                reverse_direction=reverse_direction,
            )
            if mode == "packetization_off":
                proposal = dict(proposal)
                proposal["status_before_packetization_off"] = proposal["status"]
                proposal["status"] = "packetization_off"
                proposal["packets"] = []
            proposals.append(proposal)
            schedule_proposal(model, proposal, generated_counter)
            if restore_after_first_trigger and trigger_count == 1:
                with tempfile.TemporaryDirectory(prefix="phase8-elgi-c1-") as directory:
                    snapshot = Path(directory) / "checkpoint.json"
                    model.save(str(snapshot))
                    snapshot_sha256 = sha256_file(snapshot)
                    model = LGRC9V3.load(str(snapshot))
                restored = True

        processed = 0
        while model.get_state().packet_ledger.event_queue_records:
            if processed >= limit:
                raise RuntimeError(f"event limit exceeded in {arm_id}")
            result = model.step()
            processed += 1
            record = event_record(model, result)
            events.append(record)
            packet = model.get_state().packet_processing_log[-1].packet_record
            event = model.get_state().packet_processing_log[-1].processed_event
            is_exogenous_arrival = (
                event.event_kind == "lgrc9v3_packet_arrival"
                and str(packet.source_lineage_id or "").startswith("c1-exogenous-")
            )
            if mode != "c0_full_drain" and is_exogenous_arrival:
                queue = model.get_state().packet_ledger.event_queue_records
                same_frontier_pending = bool(
                    queue
                    and abs(float(queue[0].event_time_key) - float(event.event_time_key))
                    <= float_tol
                )
                if not same_frontier_pending:
                    trigger()

        if mode == "c0_full_drain":
            trigger()
            while model.get_state().packet_ledger.event_queue_records:
                if processed >= limit:
                    raise RuntimeError(f"event limit exceeded in {arm_id}")
                result = model.step()
                processed += 1
                events.append(event_record(model, result))

        final_source = source_state_record(model)
        _, independent = reconstruct(model)
        final_state = model.get_state().base_state
        semantic = {
            "final_coherence": final_source["coherence"],
            "independent_later_effect": independent,
            "proposal_statuses": [row["status"] for row in proposals],
            "proposal_packet_amounts": [
                [float(packet["amount"]) for packet in row.get("packets", [])]
                for row in proposals
            ],
            "trigger_count": trigger_count,
            "topology_nodes": sorted(int(x) for x in final_state.topology.iter_live_node_ids()),
            "topology_edges": sorted(int(x) for x in final_state.topology.iter_live_edge_ids()),
            "basin_ids": {
                str(node_id): final_state.nodes[node_id].basin_id
                for node_id in sorted(final_state.nodes)
            },
        }
        semantic["digest"] = digest_json(semantic)
        budget_errors = [abs(float(row["budget_error"])) for row in events]
        return {
            "arm_id": arm_id,
            "history": history,
            "mode": mode,
            "initial_source": initial,
            "events": events,
            "proposals": proposals,
            "trigger_count": trigger_count,
            "restored_after_first_trigger": restored,
            "snapshot_sha256": snapshot_sha256,
            "final_source": final_source,
            "independent_later_effect": independent,
            "semantic_result": semantic,
            "maximum_absolute_budget_error": max(budget_errors, default=0.0),
            "budget_conservation_passed": max(budget_errors, default=0.0)
            <= float(tolerances["budget"]),
        }

    started = datetime.now(timezone.utc).isoformat()
    arms = [
        run_arm("C0_H12", history="H12", mode="c0_full_drain"),
        run_arm("C0_H21", history="H21", mode="c0_full_drain"),
        run_arm("C1_H12", history="H12", mode="c1"),
        run_arm("C1_H21", history="H21", mode="c1"),
        run_arm("C1_F12", history="F12", mode="c1"),
        run_arm("C1_F21", history="F21", mode="c1"),
        run_arm("C1_GEOMETRY_OFF_H12", history="H12", mode="geometry_off"),
        run_arm("C1_GEOMETRY_OFF_H21", history="H21", mode="geometry_off"),
        run_arm("C1_PACKETIZATION_OFF_H12", history="H12", mode="packetization_off"),
        run_arm("C1_PACKETIZATION_OFF_H21", history="H21", mode="packetization_off"),
        run_arm(
            "C1_LABEL_ONLY_H12",
            history="H12",
            mode="c1",
            labels=("renamed-centre", "renamed-left", "renamed-right"),
        ),
        run_arm("C1_HALF_SCALE_H12", history="H12", mode="c1", integration_scale=0.5),
        run_arm(
            "C1_WRONG_DIRECTION_H12",
            history="H12",
            mode="c1",
            reverse_direction=True,
        ),
        run_arm(
            "C1_RESTORATION_H12",
            history="H12",
            mode="c1",
            restore_after_first_trigger=True,
        ),
        run_arm("C1_REPLAY_H12", history="H12", mode="c1"),
        run_arm("C1_OVERDRAW_H12", history="H12", mode="c1", integration_scale=1000.0),
    ]

    control_model_base = GRC9V3.from_state(build_state(), params)
    control_model = LGRC9V3.from_state(
        control_model_base.get_state(), control_model_base.get_params()
    )
    stale_digest = source_state_record(control_model)["digest"]
    schedule_exogenous(control_model, "H12")
    control_model.step()
    stale_control = build_proposal(
        control_model,
        trigger_node_id=0,
        stale_source_digest=stale_digest,
    )
    scope_control = build_proposal(
        control_model,
        trigger_node_id=0,
        forced_action_node=1,
    )

    raw = {
        "artifact": "Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1RawEvidence",
        "schema_version": "phase8_lgrc9_event_local_geometry_integration_c0_c1_raw_v1",
        "experiment_id": registration["experiment_id"],
        "attempt": 1,
        "source_commit": registration["source_authority"]["commit"],
        "registration_sha256": sha256_file(registration_path),
        "execution_freeze_sha256": sha256_file(freeze_path),
        "freeze_id": freeze["freeze_id"],
        "freeze_verification": freeze_result,
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "arms": arms,
        "static_controls": {
            "stale_proposal": stale_control,
            "scope_leak": scope_control,
        },
        "runtime_source_modified": False,
        "claim_boundary": registration["maximum_claim"],
        "blocked_claims": registration["blocked_claims"],
    }
    raw["evidence_digest"] = digest_json(raw)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(raw, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
