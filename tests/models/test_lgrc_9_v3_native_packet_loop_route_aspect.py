"""Tests for native LGRC9V3 packet-loop route-aspect contracts."""

from __future__ import annotations

import json
import unittest

from pygrc.core import InvalidStateTransitionError, PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    PortEdge,
    compile_lgrc9v3_route_aspect_to_causal_flux_routes,
    restore_lgrc9v3_route_aspect_artifact,
    validate_lgrc9v3_route_aspect,
)


def _ring_state() -> GRC9V3State:
    graph = PortGraphBackend()
    nodes = [graph.add_node({"label": f"node_{index}"}) for index in range(12)]
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}
    for edge_index, source_node_id in enumerate(nodes):
        target_node_id = nodes[(edge_index + 1) % len(nodes)]
        edge_id = graph.connect_ports(
            source_node_id,
            5,
            target_node_id,
            3,
            {"kind": "route_aspect_ring"},
        )
        port_edges[edge_id] = PortEdge(
            source_node_id,
            6,
            target_node_id,
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
        nodes={node_id: GRC9V3NodeState(coherence=1.0) for node_id in nodes},
        port_edges=port_edges,
        base_conductance=base_conductance,
        geometric_length=geometric_length,
        temporal_delay=temporal_delay,
        flux_coupling=flux_coupling,
    )


def _channel(
    channel_id: str,
    source_pole_id: str,
    target_pole_id: str,
    hops: list[tuple[int, int, int]],
    *,
    expected_next_channel_id: str | None = None,
) -> LGRC9V3RouteAspectChannel:
    return LGRC9V3RouteAspectChannel(
        channel_id=channel_id,
        source_pole_id=source_pole_id,
        target_pole_id=target_pole_id,
        expected_next_channel_id=expected_next_channel_id,
        route_hops=tuple(
            LGRC9V3RouteAspectHop(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                edge_id=edge_id,
            )
            for source_node_id, target_node_id, edge_id in hops
        ),
    )


def _route_aspect(
    *,
    direction: str = "clockwise",
    pole_regions: dict[str, tuple[int, ...]] | None = None,
    channel_sequence: tuple[str, ...] = (
        "S1_to_K2",
        "K2_to_S2",
        "S2_to_K1",
        "K1_to_S1",
    ),
) -> LGRC9V3RouteAspect:
    channels = (
        _channel(
            "S1_to_K2",
            "S1",
            "K2",
            [(1, 2, 1), (2, 3, 2)],
            expected_next_channel_id="K2_to_S2",
        ),
        _channel(
            "K2_to_S2",
            "K2",
            "S2",
            [(4, 5, 4), (5, 6, 5)],
            expected_next_channel_id="S2_to_K1",
        ),
        _channel(
            "S2_to_K1",
            "S2",
            "K1",
            [(7, 8, 7), (8, 9, 8)],
            expected_next_channel_id="K1_to_S1",
        ),
        _channel(
            "K1_to_S1",
            "K1",
            "S1",
            [(10, 11, 10), (11, 0, 11)],
            expected_next_channel_id="S1_to_K2",
        ),
    )
    return LGRC9V3RouteAspect(
        route_aspect_id="d2_3_cw_closed_loop",
        direction=direction,
        pole_regions=pole_regions
        or {
            "S1": (0, 1),
            "K2": (3, 4),
            "S2": (6, 7),
            "K1": (9, 10),
        },
        channels=channels,
        channel_sequence=channel_sequence,
    )


class LGRC9V3RouteAspectContractTest(unittest.TestCase):
    """Validate Iteration 44 route-aspect contracts."""

    def test_route_aspect_json_round_trips_with_stable_digests(self) -> None:
        route_aspect = _route_aspect()
        artifact = json.loads(json.dumps(route_aspect.to_artifact(), sort_keys=True))
        restored = restore_lgrc9v3_route_aspect_artifact(artifact)

        self.assertEqual(artifact, restored.to_artifact())
        self.assertEqual(
            route_aspect.route_aspect_digest,
            restored.route_aspect_digest,
        )
        self.assertEqual(
            route_aspect.pole_region_digest,
            restored.pole_region_digest,
        )
        self.assertEqual(
            route_aspect.channel_sequence_digest,
            restored.channel_sequence_digest,
        )

    def test_route_aspect_validates_against_state_and_compiles_to_routes(self) -> None:
        route_aspect = validate_lgrc9v3_route_aspect(_route_aspect(), state=_ring_state())

        routes = compile_lgrc9v3_route_aspect_to_causal_flux_routes(
            route_aspect,
            amount=0.006,
        )

        self.assertEqual(
            {
                1: [{"target_node_id": 2, "edge_id": 1}],
                2: [{"target_node_id": 3, "edge_id": 2}],
                4: [{"target_node_id": 5, "edge_id": 4}],
                5: [{"target_node_id": 6, "edge_id": 5}],
                7: [{"target_node_id": 8, "edge_id": 7}],
                8: [{"target_node_id": 9, "edge_id": 8}],
                10: [{"target_node_id": 11, "edge_id": 10}],
                11: [{"target_node_id": 0, "edge_id": 11}],
            },
            {
                source_node_id: [
                    {
                        "target_node_id": route["target_node_id"],
                        "edge_id": route["edge_id"],
                    }
                    for route in source_routes
                ]
                for source_node_id, source_routes in routes.items()
            },
        )
        for source_routes in routes.values():
            for route in source_routes:
                self.assertEqual("d2_3_cw_closed_loop", route["route_aspect_id"])
                self.assertEqual(route_aspect.route_aspect_digest, route["route_aspect_digest"])
                self.assertAlmostEqual(0.006, route["amount"])

    def test_route_aspect_digest_changes_with_pole_mask(self) -> None:
        original = _route_aspect()
        changed = _route_aspect(
            pole_regions={
                "S1": (0, 1, 2),
                "K2": (3, 4),
                "S2": (6, 7),
                "K1": (9, 10),
            }
        )

        self.assertNotEqual(original.pole_region_digest, changed.pole_region_digest)
        self.assertNotEqual(original.route_aspect_digest, changed.route_aspect_digest)

    def test_route_aspect_digest_changes_with_direction(self) -> None:
        original = _route_aspect(direction="clockwise")
        changed = _route_aspect(direction="counter_clockwise")

        self.assertNotEqual(original.route_aspect_digest, changed.route_aspect_digest)

    def test_route_aspect_digest_changes_with_channel_order(self) -> None:
        original = _route_aspect()
        rotated = _route_aspect(
            channel_sequence=(
                "K2_to_S2",
                "S2_to_K1",
                "K1_to_S1",
                "S1_to_K2",
            )
        )

        self.assertNotEqual(
            original.channel_sequence_digest,
            rotated.channel_sequence_digest,
        )
        self.assertNotEqual(original.route_aspect_digest, rotated.route_aspect_digest)

    def test_overlapping_pole_regions_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _route_aspect(
                pole_regions={
                    "S1": (0, 1),
                    "K2": (1, 4),
                    "S2": (6, 7),
                    "K1": (9, 10),
                }
            )

    def test_scrambled_channel_sequence_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _route_aspect(
                channel_sequence=(
                    "S1_to_K2",
                    "S2_to_K1",
                    "K2_to_S2",
                    "K1_to_S1",
                )
            )

    def test_broken_return_route_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            LGRC9V3RouteAspect(
                route_aspect_id="broken_return",
                direction="clockwise",
                pole_regions={
                    "S1": (0, 1),
                    "K2": (3, 4),
                    "S2": (6, 7),
                    "K1": (9, 10),
                    "X": (11,),
                },
                channels=(
                    _channel("S1_to_K2", "S1", "K2", [(1, 2, 1)]),
                    _channel("K2_to_S2", "K2", "S2", [(4, 5, 4)]),
                    _channel("S2_to_K1", "S2", "K1", [(7, 8, 7)]),
                    _channel("K1_to_X", "K1", "X", [(10, 11, 10)]),
                ),
                channel_sequence=(
                    "S1_to_K2",
                    "K2_to_S2",
                    "S2_to_K1",
                    "K1_to_X",
                ),
            )

    def test_route_aspect_state_validation_rejects_bad_edge(self) -> None:
        route_aspect = LGRC9V3RouteAspect(
            route_aspect_id="bad_edge",
            direction="clockwise",
            pole_regions={
                "S1": (0, 1),
                "K2": (3, 4),
                "S2": (6, 7),
                "K1": (9, 10),
            },
            channels=(
                _channel("S1_to_K2", "S1", "K2", [(1, 2, 0)]),
                _channel("K2_to_S2", "K2", "S2", [(4, 5, 4)]),
                _channel("S2_to_K1", "S2", "K1", [(7, 8, 7)]),
                _channel("K1_to_S1", "K1", "S1", [(10, 11, 10)]),
            ),
            channel_sequence=(
                "S1_to_K2",
                "K2_to_S2",
                "S2_to_K1",
                "K1_to_S1",
            ),
        )

        with self.assertRaises(InvalidStateTransitionError):
            validate_lgrc9v3_route_aspect(route_aspect, state=_ring_state())

    def test_route_aspect_state_validation_rejects_missing_pole_node(self) -> None:
        route_aspect = _route_aspect(
            pole_regions={
                "S1": (0, 99),
                "K2": (3, 4),
                "S2": (6, 7),
                "K1": (9, 10),
            }
        )

        with self.assertRaises(InvalidStateTransitionError):
            validate_lgrc9v3_route_aspect(route_aspect, state=_ring_state())

    def test_route_aspect_state_validation_rejects_reversed_edge_direction(
        self,
    ) -> None:
        route_aspect = LGRC9V3RouteAspect(
            route_aspect_id="reversed_edge",
            direction="clockwise",
            pole_regions={
                "S1": (0, 1),
                "K2": (3, 4),
                "S2": (6, 7),
                "K1": (9, 10),
            },
            channels=(
                _channel("S1_to_K2", "S1", "K2", [(2, 1, 1)]),
                _channel("K2_to_S2", "K2", "S2", [(4, 5, 4)]),
                _channel("S2_to_K1", "S2", "K1", [(7, 8, 7)]),
                _channel("K1_to_S1", "K1", "S1", [(10, 11, 10)]),
            ),
            channel_sequence=(
                "S1_to_K2",
                "K2_to_S2",
                "S2_to_K1",
                "K1_to_S1",
            ),
        )

        with self.assertRaises(InvalidStateTransitionError):
            validate_lgrc9v3_route_aspect(route_aspect, state=_ring_state())


if __name__ == "__main__":
    unittest.main()
