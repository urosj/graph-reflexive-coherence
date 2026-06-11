"""Column coarse-graining and Split tests for the Phase 6 GRC9 baseline."""

from __future__ import annotations

import unittest

from pygrc.core import GRCEvent
from pygrc.models import GRC9


def _coarse_config(**evolution_overrides: object) -> dict[str, object]:
    evolution: dict[str, object] = {
        "alpha": 1.0,
        "beta": 1.0,
        "gamma": 1.0,
        "delta": 1.0,
        "eta": 1.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.1,
        "rng_seed": 0,
        "w_bond": 1.0,
    }
    evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
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
    flux_uv: float = 0.0,
) -> dict[str, float | int]:
    return {
        "node_u": node_u,
        "port_u": port_u,
        "node_v": node_v,
        "port_v": port_v,
        "conductance": conductance,
        "flux_uv": flux_uv,
    }


class GRC9CoarseGrainingTest(unittest.TestCase):
    """Validate Iteration 7 exact column coarse-graining and invalidation."""

    def test_coarse_grain_columns_exactly_reconstructs_nonnegative_conductance(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 0, 1, 2, 0),
                        (2, 0, 3, 3, 0),
                        (3, 0, 4, 4, 0),
                    ]
                ),
                "node_coherence": {"0": 1.0, "1": 1.0, "2": 1.0, "3": 1.0, "4": 1.0},
                "port_edges": {
                    "0": _port_edge_payload(node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0),
                    "1": _port_edge_payload(node_u=0, port_u=2, node_v=2, port_v=1, conductance=1.0),
                    "2": _port_edge_payload(node_u=0, port_u=4, node_v=3, port_v=1, conductance=3.0),
                    "3": _port_edge_payload(node_u=0, port_u=5, node_v=4, port_v=1, conductance=6.0),
                },
            },
            params=_coarse_config(),
        )

        coarse_state = model.coarse_grain_columns("conductance")
        reconstructed = model.split_columns(coarse_state)

        self.assertEqual("exact_column_profile", coarse_state["mode"])
        self.assertEqual([5.0, 7.0, 0.0], coarse_state["by_node"]["0"]["column_totals"])
        self.assertEqual(
            [2.0 / 5.0, 3.0 / 5.0, 0.0],
            coarse_state["by_node"]["0"]["profiles"][0],
        )
        self.assertEqual(
            [1.0 / 7.0, 6.0 / 7.0, 0.0],
            coarse_state["by_node"]["0"]["profiles"][1],
        )
        self.assertEqual(
            {"1": 2.0, "2": 1.0, "3": 0.0, "4": 3.0, "5": 6.0, "6": 0.0, "7": 0.0, "8": 0.0, "9": 0.0},
            reconstructed["port_field"]["0"],
        )
        self.assertEqual(
            "conductance",
            reconstructed["field_name"],
        )

    def test_coarse_grain_columns_exactly_reconstructs_signed_flux_via_split(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 0, 1, 2, 0),
                    ]
                ),
                "node_coherence": {"0": 1.0, "1": 1.0, "2": 1.0},
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0, port_u=1, node_v=1, port_v=1, conductance=1.0, flux_uv=2.5
                    ),
                    "1": _port_edge_payload(
                        node_u=0, port_u=2, node_v=2, port_v=1, conductance=1.0, flux_uv=-1.5
                    ),
                },
            },
            params=_coarse_config(),
        )

        coarse_state = model.coarse_grain_columns("signed_flux")
        reconstructed = model.split_columns(coarse_state)

        self.assertEqual("signed_flux_split", coarse_state["mode"])
        self.assertEqual(
            {"1": 2.5, "2": -1.5, "3": 0.0, "4": 0.0, "5": 0.0, "6": 0.0, "7": 0.0, "8": 0.0, "9": 0.0},
            reconstructed["port_field"]["0"],
        )
        self.assertEqual(
            {"1": -2.5, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0, "6": 0.0, "7": 0.0, "8": 0.0, "9": 0.0},
            reconstructed["port_field"]["1"],
        )

    def test_coarse_cache_invalidates_after_metric_and_flux_recomputation(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 1.0, "1": 2.0},
                "potential": {"0": 0.0, "1": 1.0},
                "port_edges": {
                    "0": _port_edge_payload(node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0),
                },
            },
            params=_coarse_config(),
        )

        model.coarse_grain_columns("conductance")
        self.assertTrue(model.get_state().coarse_cache)

        model._compute_metric()
        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertEqual(
            "conductance_recomputation",
            model.get_state().cached_quantities["coarse_cache_invalidation_reason"],
        )

        model.coarse_grain_columns("signed_flux")
        self.assertTrue(model.get_state().coarse_cache)

        model._compute_flux()
        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertEqual(
            "flux_recomputation",
            model.get_state().cached_quantities["coarse_cache_invalidation_reason"],
        )

    def test_coarse_cache_invalidates_after_topology_mutation(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 4.0, "1": 1.0},
                "budget_target": 5.0,
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=3.0,
                    )
                },
            },
            params=_coarse_config(lambda_birth=1e9, alpha_seed=0.25),
        )

        model.coarse_grain_columns("conductance")
        self.assertTrue(model.get_state().coarse_cache)

        model._apply_growth()
        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertEqual(
            "topology_mutation",
            model.get_state().cached_quantities["coarse_cache_invalidation_reason"],
        )

    def test_coarse_cache_invalidates_after_expansion_rewiring(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 3.0, "1": 1.0},
                "budget_target": 4.0,
                "port_edges": {
                    "0": _port_edge_payload(node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0),
                },
                "sink_set": [0],
            },
            params=_coarse_config(),
        )

        model.coarse_grain_columns("conductance")
        self.assertTrue(model.get_state().coarse_cache)

        model._apply_topology_changes(
            [
                GRCEvent(
                    kind="spark",
                    step_index=0,
                    payload={"sink_node_id": 0},
                    source_family="GRC9",
                )
            ]
        )
        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertEqual(
            "topology_mutation",
            model.get_state().cached_quantities["coarse_cache_invalidation_reason"],
        )

