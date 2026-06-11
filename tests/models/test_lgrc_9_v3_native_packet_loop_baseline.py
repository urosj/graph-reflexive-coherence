"""Baseline tests for Phase 8 native LGRC9V3 packet-loop continuation."""

from __future__ import annotations

import unittest

from pygrc.core import InvalidParamsError, PortGraphBackend
from pygrc.models import GRC9V3NodeState, GRC9V3State, LGRC9V3, PortEdge
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
)
from pygrc.models.lgrc_9_v3_packets import (
    LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
)


_PARAMS = {"dt": 1.0}
_PACKET_AMOUNT = 0.006
_SURPLUS_TRIGGER_POLICY_CANDIDATE = "source_pole_surplus_threshold"


def _e2_route_manifest() -> dict[str, object]:
    """Return a compact in-test copy of the E2 route fixture."""

    return {
        "schema": "n03_e2_lgrc9v3_route_manifest_v1",
        "fixture": "e2_lgrc9v3_ported_ring_v1",
        "node_count": 12,
        "edge_count": 12,
        "poles": {
            "S1": [0, 1],
            "K2": [3, 4],
            "S2": [6, 7],
            "K1": [9, 10],
        },
        "declared_routes": {
            "d2_3_cw_closed_loop": [
                "S1_to_K2",
                "K2_to_S2",
                "S2_to_K1",
                "K1_to_S1",
            ]
        },
        "channels": {
            "S1_to_K2": {
                "source_pole": "S1",
                "target_pole": "K2",
                "route_hops": [
                    {"source_node_id": 1, "target_node_id": 2, "edge_id": 1},
                    {"source_node_id": 2, "target_node_id": 3, "edge_id": 2},
                ],
            },
            "K2_to_S2": {
                "source_pole": "K2",
                "target_pole": "S2",
                "route_hops": [
                    {"source_node_id": 4, "target_node_id": 5, "edge_id": 4},
                    {"source_node_id": 5, "target_node_id": 6, "edge_id": 5},
                ],
            },
            "S2_to_K1": {
                "source_pole": "S2",
                "target_pole": "K1",
                "route_hops": [
                    {"source_node_id": 7, "target_node_id": 8, "edge_id": 7},
                    {"source_node_id": 8, "target_node_id": 9, "edge_id": 8},
                ],
            },
            "K1_to_S1": {
                "source_pole": "K1",
                "target_pole": "S1",
                "route_hops": [
                    {"source_node_id": 10, "target_node_id": 11, "edge_id": 10},
                    {"source_node_id": 11, "target_node_id": 0, "edge_id": 11},
                ],
            },
        },
    }


def _e2_route_hops(manifest: dict[str, object]) -> list[dict[str, int]]:
    channels = manifest["channels"]
    assert isinstance(channels, dict)
    declared_routes = manifest["declared_routes"]
    assert isinstance(declared_routes, dict)
    route_order = declared_routes["d2_3_cw_closed_loop"]
    assert isinstance(route_order, list)
    hops: list[dict[str, int]] = []
    for channel_id in route_order:
        channel = channels[str(channel_id)]
        assert isinstance(channel, dict)
        route_hops = channel["route_hops"]
        assert isinstance(route_hops, list)
        hops.extend(
            {
                "source_node_id": int(hop["source_node_id"]),
                "target_node_id": int(hop["target_node_id"]),
                "edge_id": int(hop["edge_id"]),
            }
            for hop in route_hops
            if isinstance(hop, dict)
        )
    return hops


def _e2_routes_by_source() -> dict[int, list[dict[str, float | int]]]:
    return {
        hop["source_node_id"]: [
            {
                "target_node_id": hop["target_node_id"],
                "edge_id": hop["edge_id"],
                "amount": _PACKET_AMOUNT,
            }
        ]
        for hop in _e2_route_hops(_e2_route_manifest())
    }


def _e2_ring_state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_ids = [graph.add_node({"label": f"node_{index}"}) for index in range(12)]
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for edge_index, source_id in enumerate(node_ids):
        target_id = node_ids[(edge_index + 1) % len(node_ids)]
        edge_id = graph.connect_ports(
            source_id,
            5,
            target_id,
            3,
            {"kind": "e2_clockwise_ring"},
        )
        port_edges[edge_id] = PortEdge(
            source_id,
            6,
            target_id,
            4,
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
            node_id: GRC9V3NodeState(coherence=1.0)
            for node_id in node_ids
        },
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def _runtime_budget_surface(model: LGRC9V3) -> float:
    state = model.get_state()
    node_total = sum(
        float(node.coherence) for node in state.base_state.nodes.values()
    )
    return node_total + float(state.packet_ledger.in_flight_packet_total)


class LGRC9V3NativePacketLoopBaselineTest(unittest.TestCase):
    """Freeze current E2 packet-loop runtime boundary before new primitives."""

    def test_e2_route_fixture_is_imported_as_compact_test_contract(self) -> None:
        manifest = _e2_route_manifest()
        hops = _e2_route_hops(manifest)

        self.assertEqual("n03_e2_lgrc9v3_route_manifest_v1", manifest["schema"])
        self.assertEqual("e2_lgrc9v3_ported_ring_v1", manifest["fixture"])
        self.assertEqual(12, manifest["node_count"])
        self.assertEqual(12, manifest["edge_count"])
        self.assertEqual(
            ["S1_to_K2", "K2_to_S2", "S2_to_K1", "K1_to_S1"],
            manifest["declared_routes"]["d2_3_cw_closed_loop"],  # type: ignore[index]
        )
        self.assertEqual(
            [
                {"source_node_id": 1, "target_node_id": 2, "edge_id": 1},
                {"source_node_id": 2, "target_node_id": 3, "edge_id": 2},
                {"source_node_id": 4, "target_node_id": 5, "edge_id": 4},
                {"source_node_id": 5, "target_node_id": 6, "edge_id": 5},
                {"source_node_id": 7, "target_node_id": 8, "edge_id": 7},
                {"source_node_id": 8, "target_node_id": 9, "edge_id": 8},
                {"source_node_id": 10, "target_node_id": 11, "edge_id": 10},
                {"source_node_id": 11, "target_node_id": 0, "edge_id": 11},
            ],
            hops,
        )

    def test_existing_scheduled_packet_route_replay_baseline(self) -> None:
        model = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)
        budget_before = _runtime_budget_surface(model)
        hops = _e2_route_hops(_e2_route_manifest())

        for packet_index, hop in enumerate(hops):
            model.schedule_packet_departure(
                source_node_id=hop["source_node_id"],
                target_node_id=hop["target_node_id"],
                edge_id=hop["edge_id"],
                amount=_PACKET_AMOUNT,
                departure_event_time_key=0.0,
                scheduler_event_index=packet_index + 1,
                packet_index=packet_index,
            )

        results = model.run_event_queue(max_events=2 * len(hops))
        event_kinds = [
            event.kind
            for result in results
            for event in result.events
            if event.kind
            in {
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            }
        ]

        self.assertEqual(
            [LGRC9V3_PACKET_EVENT_KIND_DEPARTURE] * len(hops)
            + [LGRC9V3_PACKET_EVENT_KIND_ARRIVAL] * len(hops),
            event_kinds,
        )
        packet_events = [
            event
            for result in results
            for event in result.events
            if event.kind
            in {
                LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
                LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
            }
        ]
        for event in packet_events:
            self.assertIn("scheduler_event_index", event.payload)
            self.assertIn("checkpoint_index", event.payload)
            self.assertIn("event_time_key", event.payload)
            self.assertIn("processed_event", event.payload)
            self.assertIn("packet_record", event.payload)
            self.assertIn("proper_time_update", event.payload)
        self.assertTrue(
            all(
                event.payload["proper_time_update"] is not None
                for event in packet_events
                if event.kind == LGRC9V3_PACKET_EVENT_KIND_ARRIVAL
            )
        )
        self.assertAlmostEqual(budget_before, _runtime_budget_surface(model))
        self.assertEqual((), model.get_state().packet_ledger.event_queue_records)
        self.assertFalse(model.get_state().topology_event_log)

    def test_existing_static_route_autonomy_is_not_d2_3_equivalent(self) -> None:
        model = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)
        model.set_causal_flux_routes(_e2_routes_by_source())

        results = model.run_autonomous(
            max_events=4,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )
        summary = model.get_state().cached_quantities[
            "last_lgrc9v3_autonomous_run"
        ]
        production_records = [
            record
            for production_result in summary["production_results"]
            for record in production_result["production_records"]
        ]

        self.assertEqual(8, summary["producer_scheduled_event_count"])
        self.assertEqual(4, summary["consumed_step_count"])
        self.assertEqual("max_events_reached", summary["stop_condition"])
        self.assertTrue(results)
        self.assertTrue(
            all(
                record["producer_policy"]
                == LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
                for record in production_records
            )
        )
        self.assertTrue(
            all("source_pole_surplus" not in record["observed_evidence"] for record in production_records)
        )
        self.assertTrue(
            all("self_rearm" not in record["observed_evidence"] for record in production_records)
        )
        self.assertFalse(hasattr(model.get_state(), "route_aspects"))
        self.assertFalse(hasattr(model.get_state(), "self_rearm_evidence_log"))

    def test_disabled_policy_does_not_change_static_route_autonomy(self) -> None:
        control = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)
        probed = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)
        control.set_causal_flux_routes(_e2_routes_by_source())
        probed.set_causal_flux_routes(_e2_routes_by_source())

        disabled = probed.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED
        )
        control_results = control.run_autonomous(
            max_events=4,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )
        probed_results = probed.run_autonomous(
            max_events=4,
            producer_policies=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
            ),
        )

        self.assertEqual(0, disabled.scheduled_event_count)
        self.assertFalse(disabled.state_mutated)
        self.assertEqual(
            [[event.kind for event in result.events] for result in control_results],
            [[event.kind for event in result.events] for result in probed_results],
        )
        self.assertEqual(
            control.get_state().cached_quantities["last_lgrc9v3_autonomous_run"][
                "producer_scheduled_event_count"
            ],
            probed.get_state().cached_quantities["last_lgrc9v3_autonomous_run"][
                "producer_scheduled_event_count"
            ],
        )

    def test_disabled_policy_preserves_default_off_boundary(self) -> None:
        model = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)
        before_runtime = model.snapshot()["dynamics"]["lgrc9v3_runtime"]

        result = model.produce_events(policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED)

        self.assertEqual(0, result.scheduled_event_count)
        self.assertFalse(result.state_mutated)
        self.assertEqual(
            before_runtime,
            model.snapshot()["dynamics"]["lgrc9v3_runtime"],
        )

    def test_native_surplus_trigger_policy_is_not_claimed_yet(self) -> None:
        model = LGRC9V3.from_state(_e2_ring_state(), _PARAMS)

        with self.assertRaises(InvalidParamsError):
            model.produce_events(policy=_SURPLUS_TRIGGER_POLICY_CANDIDATE)


if __name__ == "__main__":
    unittest.main()
