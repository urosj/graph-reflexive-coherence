"""Mechanical spark-trigger tests for the Phase 6 GRC9 baseline."""

from __future__ import annotations

import unittest

from pygrc.models import GRC9, SparkKind


def _spark_config(*, enable_sign_crossing: bool = False) -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "tau_instability": 0.5,
            "eps_spark": 0.01,
            "enable_sign_crossing_spark": enable_sign_crossing,
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _topology_from_connections(
    connections: list[tuple[int, int, int, int, int]],
) -> dict[str, object]:
    node_ids: set[int] = set()
    incidence: dict[str, list[int]] = {}
    edges: list[dict[str, object]] = []
    for edge_id, node_a, slot_a, node_b, slot_b in connections:
        node_ids.update({node_a, node_b})
        incidence.setdefault(str(node_a), []).append(edge_id)
        incidence.setdefault(str(node_b), []).append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": slot_a},
                "endpoint_b": {"node_id": node_b, "slot": slot_b},
                "payload": {},
            }
        )
    return {
        "nodes": [{"node_id": node_id, "payload": {}} for node_id in sorted(node_ids)],
        "edges": sorted(edges, key=lambda edge: int(edge["edge_id"])),
        "incidence": {
            node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
        },
        "port_structure": {},
    }


def _port_edge_payload(
    *,
    node_u: int,
    port_u: int,
    node_v: int,
    port_v: int,
    conductance: float,
) -> dict[str, float | int]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": 0.0,
    }


class GRC9MechanicalSparkTest(unittest.TestCase):
    """Validate the deterministic Phase 6 spark trigger branches."""

    def test_detect_events_emits_instability_branch_for_saturated_sink(self) -> None:
        connections = [
            (edge_id, 0, edge_id, edge_id + 1, 0)
            for edge_id in range(9)
        ] + [(9, 1, 1, 10, 0)]
        port_edges = {
            str(edge_id): _port_edge_payload(
                node_u=0,
                port_u=edge_id + 1,
                node_v=edge_id + 1,
                port_v=1,
                conductance=0.01,
            )
            for edge_id in range(9)
        }
        port_edges["9"] = _port_edge_payload(
            node_u=1,
            port_u=2,
            node_v=10,
            port_v=1,
            conductance=1.0,
        )

        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(connections),
                "node_coherence": {"0": 1.0, **{str(node_id): 100.0 for node_id in range(1, 10)}, "10": 0.0},
                "port_edges": port_edges,
                "sink_set": [0],
            },
            params=_spark_config(),
        )

        events = model._detect_events()

        self.assertEqual(1, len(events))
        self.assertEqual("spark", events[0].kind)
        self.assertEqual(SparkKind.SATURATION_INSTABILITY.value, events[0].payload["spark_kind"])
        self.assertGreater(events[0].payload["instability"], 0.5)
        self.assertEqual((0,), model.get_state().cached_quantities["spark_trigger_order"])

    def test_detect_events_emits_column_proxy_branch_with_correct_column_grouping(self) -> None:
        connections = [(edge_id, 0, edge_id, edge_id + 1, 0) for edge_id in range(9)]

        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(connections),
                "node_coherence": {
                    "0": 10.0,
                    "1": 11.0,
                    "2": 20.0,
                    "3": 30.0,
                    "4": 10.0,
                    "5": 20.0,
                    "6": 30.0,
                    "7": 9.0,
                    "8": 20.0,
                    "9": 30.0,
                },
                "sink_set": [0],
            },
            params=_spark_config(),
        )

        events = model._detect_events()

        self.assertEqual(1, len(events))
        self.assertEqual(SparkKind.SATURATION_COLUMN_PROXY.value, events[0].payload["spark_kind"])
        self.assertAlmostEqual(0.0, events[0].payload["instability"])
        self.assertAlmostEqual(0.0, events[0].payload["min_abs_column"])
        self.assertEqual([0.0, 30.0, 60.0], events[0].payload["column_diagnostic"])

    def test_detect_events_defers_near_saturation_relaxation(self) -> None:
        connections = [(edge_id, 0, edge_id, edge_id + 1, 0) for edge_id in range(8)]

        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(connections),
                "node_coherence": {"0": 10.0, **{str(node_id): 10.0 for node_id in range(1, 9)}},
                "sink_set": [0],
            },
            params=_spark_config(),
        )

        events = model._detect_events()
        diagnostics = model.get_state().cached_quantities["spark_diagnostics"]["0"]

        self.assertEqual([], events)
        self.assertEqual(8, diagnostics["active_degree"])
        self.assertEqual("deferred", diagnostics["near_saturation_extension"])
        self.assertIsNone(diagnostics["spark_kind"])

    def test_detect_events_can_emit_sign_crossing_branch_when_enabled(self) -> None:
        connections = [(edge_id, 0, edge_id, edge_id + 1, 0) for edge_id in range(9)]

        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(connections),
                "node_coherence": {
                    "0": 10.0,
                    "1": 9.0,
                    "2": 11.0,
                    "3": 12.0,
                    "4": 9.0,
                    "5": 11.0,
                    "6": 12.0,
                    "7": 9.0,
                    "8": 11.0,
                    "9": 12.0,
                },
                "sink_set": [0],
                "prev_column_diagnostic": {"0": [1.0, 1.0, 1.0]},
            },
            params=_spark_config(enable_sign_crossing=True),
        )

        events = model._detect_events()

        self.assertEqual(1, len(events))
        self.assertEqual(
            SparkKind.SATURATION_SIGN_CROSSING.value,
            events[0].payload["spark_kind"],
        )
        self.assertEqual([-3.0, 3.0, 6.0], events[0].payload["column_diagnostic"])
        self.assertEqual(
            [-3.0, 3.0, 6.0],
            model.get_state().prev_column_diagnostic[0],
        )

    def test_detect_events_orders_multiple_sinks_by_ascending_node_id(self) -> None:
        left_connections = [(edge_id, 0, edge_id, edge_id + 1, 0) for edge_id in range(9)]
        right_connections = [
            (edge_id + 9, 20, edge_id, edge_id + 21, 0)
            for edge_id in range(9)
        ]

        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(left_connections + right_connections),
                "node_coherence": {
                    "0": 10.0,
                    **{str(node_id): 10.0 + ((node_id - 1) % 3) for node_id in range(1, 10)},
                    "20": 5.0,
                    **{
                        str(node_id): 5.0 + ((node_id - 21) % 3)
                        for node_id in range(21, 30)
                    },
                },
                "sink_set": [20, 0],
            },
            params=_spark_config(),
        )

        events = model._detect_events()

        self.assertEqual([0, 20], [event.payload["sink_node_id"] for event in events])
        self.assertEqual(
            (0, 20),
            model.get_state().cached_quantities["spark_trigger_order"],
        )

