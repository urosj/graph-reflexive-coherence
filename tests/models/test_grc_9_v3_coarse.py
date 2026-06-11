"""Column coarse-graining operator tests for the Phase 7 GRC9V3 shell."""

from __future__ import annotations

import unittest

from pygrc.core import COLUMN_COARSE_GRAINING, InvalidStateTransitionError
from pygrc.models import GRC9V3


def _coarse_config(**modes: object) -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
            "eps_gradient": 0.5,
            "eps_hessian": 0.1,
        },
        "constitutive_semantic_modes": {
            "edge_label_selection": "all",
            **modes,
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


def _nodes(*node_ids: int) -> dict[str, dict[str, float]]:
    return {str(node_id): {"coherence": 1.0} for node_id in node_ids}


class GRC9V3CoarseGrainingTest(unittest.TestCase):
    """Validate the repaired GRC9V3 column coarse-graining operator surface."""

    def test_coarse_grain_columns_exactly_reconstructs_nonnegative_conductance(
        self,
    ) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 0, 1, 2, 0),
                        (2, 0, 3, 3, 0),
                        (3, 0, 4, 4, 0),
                    ]
                ),
                "nodes": _nodes(0, 1, 2, 3, 4),
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=2.0,
                    ),
                    "1": _port_edge_payload(
                        node_u=0,
                        port_u=2,
                        node_v=2,
                        port_v=1,
                        conductance=1.0,
                    ),
                    "2": _port_edge_payload(
                        node_u=0,
                        port_u=4,
                        node_v=3,
                        port_v=1,
                        conductance=3.0,
                    ),
                    "3": _port_edge_payload(
                        node_u=0,
                        port_u=5,
                        node_v=4,
                        port_v=1,
                        conductance=6.0,
                    ),
                },
            },
            params=_coarse_config(),
        )

        coarse_state = model.coarse_grain_columns("conductance")
        reconstructed = model.split_columns(coarse_state)
        state = model.get_state()

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
            {
                "1": 2.0,
                "2": 1.0,
                "3": 0.0,
                "4": 3.0,
                "5": 6.0,
                "6": 0.0,
                "7": 0.0,
                "8": 0.0,
                "9": 0.0,
            },
            reconstructed["port_field"]["0"],
        )
        self.assertEqual("conductance", reconstructed["field_name"])
        self.assertIn("exact_column_profile:conductance", state.coarse_cache)
        self.assertEqual(
            "operator_backed",
            state.cached_quantities["coarse_cache_refresh_mode"],
        )

    def test_coarse_grain_columns_exactly_reconstructs_signed_flux_via_split(
        self,
    ) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 0, 1, 2, 0),
                    ]
                ),
                "nodes": _nodes(0, 1, 2),
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=2.5,
                    ),
                    "1": _port_edge_payload(
                        node_u=0,
                        port_u=2,
                        node_v=2,
                        port_v=1,
                        conductance=1.0,
                        flux_uv=-1.5,
                    ),
                },
            },
            params=_coarse_config(),
        )

        coarse_state = model.coarse_grain_columns("signed_flux")
        reconstructed = model.split_columns(coarse_state)

        self.assertEqual("signed_flux_split", coarse_state["mode"])
        self.assertEqual(
            {
                "1": 2.5,
                "2": -1.5,
                "3": 0.0,
                "4": 0.0,
                "5": 0.0,
                "6": 0.0,
                "7": 0.0,
                "8": 0.0,
                "9": 0.0,
            },
            reconstructed["port_field"]["0"],
        )
        self.assertEqual(
            {
                "1": -2.5,
                "2": 0.0,
                "3": 0.0,
                "4": 0.0,
                "5": 0.0,
                "6": 0.0,
                "7": 0.0,
                "8": 0.0,
                "9": 0.0,
            },
            reconstructed["port_field"]["1"],
        )
        self.assertIn("signed_flux_split:signed_flux", model.get_state().coarse_cache)

    def test_nonnegative_edge_label_fields_reconstruct_after_transport(
        self,
    ) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "nodes": {
                    "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
                    "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
                },
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=0.5,
                    )
                },
            },
            params=_coarse_config(),
        )

        model.rebuild_differential_state()
        model.rebuild_transport_state()
        state = model.get_state()

        expected_by_field = {
            "geometric_length": state.geometric_length[0],
            "temporal_delay": state.temporal_delay[0],
            "flux_coupling": state.flux_coupling[0],
            "abs_flux": abs(state.port_edges[0].flux_uv),
        }
        for field_name, expected_value in expected_by_field.items():
            with self.subTest(field_name=field_name):
                coarse_state = model.coarse_grain_columns(field_name)
                reconstructed = model.split_columns(coarse_state)
                self.assertAlmostEqual(
                    expected_value,
                    reconstructed["port_field"]["0"]["1"],
                )
                self.assertAlmostEqual(
                    expected_value,
                    reconstructed["port_field"]["1"]["1"],
                )

    def test_coarse_cache_invalidates_after_transport_recomputation(self) -> None:
        model = GRC9V3.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "nodes": _nodes(0, 1),
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0,
                        port_u=1,
                        node_v=1,
                        port_v=1,
                        conductance=1.0,
                    )
                },
            },
            params=_coarse_config(),
        )

        model.coarse_grain_columns("conductance")
        self.assertTrue(model.get_state().coarse_cache)

        model.rebuild_differential_state()
        model.rebuild_transport_state()

        self.assertEqual({}, model.get_state().coarse_cache)
        self.assertEqual(
            "transport_recomputation",
            model.get_state().cached_quantities["coarse_cache_invalidation_reason"],
        )

    def test_required_capability_has_public_operator_surface(self) -> None:
        model = GRC9V3.from_state(state={"nodes": {}}, params=_coarse_config())

        self.assertIn(COLUMN_COARSE_GRAINING, model.list_capabilities())
        self.assertTrue(callable(model.coarse_grain_columns))
        self.assertTrue(callable(model.split_columns))

    def test_unsupported_coarse_field_or_split_mode_raises(self) -> None:
        model = GRC9V3.from_state(state={"nodes": {}}, params=_coarse_config())

        with self.assertRaises(InvalidStateTransitionError):
            model.coarse_grain_columns("unsupported")
        with self.assertRaises(InvalidStateTransitionError):
            model.split_columns({"mode": "unsupported", "field_name": "conductance"})


if __name__ == "__main__":
    unittest.main()
