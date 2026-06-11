"""Expansion, rewiring, and growth tests for the Phase 6 GRC9 baseline."""

from __future__ import annotations

import math
import unittest

from pygrc.core import GRCEvent, InvalidParamsError
from pygrc.models import GRC9


def _expansion_config(
    *,
    mode_overrides: dict[str, object] | None = None,
    **evolution_overrides: object,
) -> dict[str, object]:
    evolution: dict[str, object] = {
        "D_eff_target": 30,
        "w_bond": 1.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.1,
        "rng_seed": 0,
        "adiabatic_expansion_substeps": 1,
    }
    evolution.update(evolution_overrides)
    modes: dict[str, object] = {
        "frame_mode": "fixed_port_chart",
        "curvature_backend": "none",
        "boundary_mode": "prune",
        "expansion_distribution_mode": "equal",
        "edge_label_selection": "all",
    }
    if mode_overrides:
        modes.update(mode_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": modes,
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


class GRC9ExpansionGrowthTest(unittest.TestCase):
    """Validate the deterministic Iteration 6 topology-event mechanics."""

    def test_apply_topology_changes_builds_canonical_module_and_rewires_by_column(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 0, 1, 2, 0),
                        (2, 0, 8, 3, 0),
                    ]
                ),
                "node_coherence": {"0": 9.0, "1": 1.0, "2": 1.0, "3": 1.0},
                "budget_target": 12.0,
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0, port_u=1, node_v=1, port_v=1, conductance=4.0
                    ),
                    "1": _port_edge_payload(
                        node_u=0, port_u=2, node_v=2, port_v=1, conductance=9.0
                    ),
                    "2": _port_edge_payload(
                        node_u=0, port_u=9, node_v=3, port_v=1, conductance=16.0
                    ),
                },
                "sink_set": [0],
            },
            params=_expansion_config(),
        )

        spark_event = GRCEvent(
            kind="spark",
            step_index=0,
            payload={"sink_node_id": 0, "spark_kind": "saturation_column_proxy"},
            source_family="GRC9",
        )

        model._apply_topology_changes([spark_event])

        state = model.get_state()
        expansion_event = next(event for event in state.event_log if event.kind == "expansion")
        module_node_ids = expansion_event.payload["module_node_ids"]
        core_node_id, satellite_1, satellite_2, satellite_3 = module_node_ids[:4]

        self.assertFalse(state.topology.has_node(0))
        self.assertEqual(0.0, state.node_coherence[core_node_id])
        self.assertAlmostEqual(3.0, state.node_coherence[satellite_1])
        self.assertAlmostEqual(3.0, state.node_coherence[satellite_2])
        self.assertAlmostEqual(3.0, state.node_coherence[satellite_3])
        self.assertEqual((0,), state.cached_quantities["topology_event_order"])

        edge_0_ports = state.topology.edge_ports(0)
        edge_1_ports = state.topology.edge_ports(1)
        edge_2_ports = state.topology.edge_ports(2)
        self.assertEqual((satellite_1, 0), edge_0_ports[0])
        self.assertEqual((satellite_2, 1), edge_1_ports[0])
        self.assertEqual((satellite_3, 8), edge_2_ports[0])

        spine_edge_ids = expansion_event.payload["internal_edge_ids"][:3]
        self.assertEqual(
            ((core_node_id, 1), (satellite_1, 4)),
            state.topology.edge_ports(spine_edge_ids[0]),
        )
        self.assertEqual(
            ((core_node_id, 4), (satellite_2, 4)),
            state.topology.edge_ports(spine_edge_ids[1]),
        )
        self.assertEqual(
            ((core_node_id, 7), (satellite_3, 4)),
            state.topology.edge_ports(spine_edge_ids[2]),
        )
        self.assertAlmostEqual(4.0, state.port_edges[spine_edge_ids[0]].conductance)
        self.assertAlmostEqual(9.0, state.port_edges[spine_edge_ids[1]].conductance)
        self.assertAlmostEqual(16.0, state.port_edges[spine_edge_ids[2]].conductance)
        self.assertEqual(tuple(module_node_ids), state.expansion_registry["spark-0-0"].module_node_ids)
        self.assertAlmostEqual(0.0, state.cached_quantities["expansion_budget_check"]["budget_error"])

    def test_apply_topology_changes_uses_w_bond_fallback_for_empty_columns(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 3.0, "1": 1.0},
                "budget_target": 4.0,
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0
                    )
                },
            },
            params=_expansion_config(w_bond=0.75),
        )

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

        state = model.get_state()
        expansion_event = next(event for event in state.event_log if event.kind == "expansion")
        core_node_id, _, satellite_2, satellite_3 = expansion_event.payload["module_node_ids"][:4]
        spine_edge_ids = expansion_event.payload["internal_edge_ids"][:3]

        edge_to_satellite_2 = next(
            edge_id
            for edge_id in spine_edge_ids
            if satellite_2 in {endpoint[0] for endpoint in state.topology.edge_ports(edge_id)}
        )
        edge_to_satellite_3 = next(
            edge_id
            for edge_id in spine_edge_ids
            if satellite_3 in {endpoint[0] for endpoint in state.topology.edge_ports(edge_id)}
        )

        self.assertEqual((core_node_id, 4), state.topology.edge_ports(edge_to_satellite_2)[0])
        self.assertAlmostEqual(0.75, state.port_edges[edge_to_satellite_2].conductance)
        self.assertAlmostEqual(0.75, state.port_edges[edge_to_satellite_3].conductance)

    def test_expansion_size_over_four_adds_round_robin_tree_node(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                "node_coherence": {"0": 3.0, "1": 1.0},
                "budget_target": 4.0,
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0
                    )
                },
            },
            params=_expansion_config(D_eff_target=31),
        )

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

        state = model.get_state()
        expansion_event = next(event for event in state.event_log if event.kind == "expansion")
        core_node_id, satellite_1, _, _, extra_node_id = expansion_event.payload["module_node_ids"]
        extra_edge_id = next(
            edge_id
            for edge_id in expansion_event.payload["internal_edge_ids"]
            if extra_node_id in {endpoint[0] for endpoint in state.topology.edge_ports(edge_id)}
        )
        endpoints = state.topology.edge_ports(extra_edge_id)

        self.assertEqual(5, len(expansion_event.payload["module_node_ids"]))
        self.assertIn((extra_node_id, 4), endpoints)
        self.assertIn((satellite_1, 1), endpoints)
        self.assertIn((core_node_id, 1), state.topology.edge_ports(expansion_event.payload["internal_edge_ids"][0]))

    def test_apply_topology_changes_handles_multiple_sparks_sequentially(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": _topology_from_connections(
                    [
                        (0, 0, 0, 1, 0),
                        (1, 2, 0, 3, 0),
                    ]
                ),
                "node_coherence": {"0": 3.0, "1": 1.0, "2": 3.0, "3": 1.0},
                "budget_target": 8.0,
                "port_edges": {
                    "0": _port_edge_payload(
                        node_u=0, port_u=1, node_v=1, port_v=1, conductance=2.0
                    ),
                    "1": _port_edge_payload(
                        node_u=2, port_u=1, node_v=3, port_v=1, conductance=2.0
                    ),
                },
            },
            params=_expansion_config(),
        )

        model._apply_topology_changes(
            [
                GRCEvent(kind="spark", step_index=0, payload={"sink_node_id": 2}, source_family="GRC9"),
                GRCEvent(kind="spark", step_index=0, payload={"sink_node_id": 0}, source_family="GRC9"),
            ]
        )

        state = model.get_state()
        self.assertEqual((0, 2), state.cached_quantities["topology_event_order"])
        self.assertEqual(2, len(state.expansion_registry))
        self.assertEqual(2, sum(1 for event in state.event_log if event.kind == "expansion"))

    def test_apply_growth_uses_lowest_inactive_parent_port_and_preserves_budget(self) -> None:
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
            params=_expansion_config(lambda_birth=1e9, alpha_seed=0.25),
        )

        model._apply_growth()

        state = model.get_state()
        growth_event = next(event for event in state.event_log if event.kind == "growth")
        child_node_id = growth_event.payload["child_node_id"]
        new_edge_id = max(state.topology.iter_live_edge_ids())
        endpoints = state.topology.edge_ports(new_edge_id)

        self.assertEqual(2, growth_event.payload["parent_port_id"])
        self.assertIn((0, 1), endpoints)
        self.assertIn((child_node_id, 0), endpoints)
        self.assertAlmostEqual(3.0, state.node_coherence[0])
        self.assertAlmostEqual(1.0, state.node_coherence[child_node_id])
        self.assertAlmostEqual(0.0, state.cached_quantities["growth_budget_check"]["budget_error"])
        self.assertEqual("bernoulli_probability", state.cached_quantities["birth_rule_mode"])

    def test_apply_growth_records_seeded_birth_probability_and_rng_sample(self) -> None:
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
            params=_expansion_config(lambda_birth=1.0, alpha_seed=0.25, rng_seed=0),
        )

        model._apply_growth()

        growth_event = next(event for event in model.get_state().event_log if event.kind == "growth")
        expected_probability = 1.0 - math.exp(-3.0)

        self.assertAlmostEqual(expected_probability, growth_event.payload["birth_probability"])
        self.assertAlmostEqual(0.8444218515250481, growth_event.payload["rng_sample"])

    def test_apply_growth_front_capacity_mode_requires_eligible_port_metadata(self) -> None:
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
            params=_expansion_config(
                lambda_birth=1e9,
                alpha_seed=0.25,
                mode_overrides={"growth_parent_eligibility": "grc9_front_capacity"},
            ),
        )

        model._apply_growth()

        state = model.get_state()
        self.assertEqual([], state.cached_quantities["last_growth_events"])
        self.assertEqual(
            "grc9_front_capacity",
            state.cached_quantities["birth_parent_eligibility_mode"],
        )
        self.assertFalse(any(event.kind == "growth" for event in state.event_log))

    def test_apply_growth_front_capacity_mode_uses_lowest_eligible_port(self) -> None:
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
                "cached_quantities": {
                    "grc9_front_growth_eligible_ports": {"0": [4, 3]},
                    "grc9_growth_parent_capacity_sources": {
                        "0": {
                            "front_capacity_source": "spark_refinement_front",
                            "inactive_parent_port": 3,
                        }
                    },
                },
            },
            params=_expansion_config(
                lambda_birth=1e9,
                alpha_seed=0.25,
                mode_overrides={"growth_parent_eligibility": "grc9_front_capacity"},
            ),
        )

        model._apply_growth()

        state = model.get_state()
        growth_event = next(event for event in state.event_log if event.kind == "growth")
        child_node_id = growth_event.payload["child_node_id"]
        endpoints = state.topology.edge_ports(max(state.topology.iter_live_edge_ids()))

        self.assertEqual(3, growth_event.payload["parent_port_id"])
        self.assertEqual(
            "grc9_front_capacity",
            growth_event.payload["growth_parent_eligibility_mode"],
        )
        self.assertEqual(
            "spark_refinement_front",
            growth_event.payload["growth_parent_capacity_source"],
        )
        self.assertIn((0, 2), endpoints)
        self.assertIn((child_node_id, 0), endpoints)

    def test_apply_growth_accepts_pressure_boundary_capacity_source(self) -> None:
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
                "cached_quantities": {
                    "grc9_front_growth_eligible_ports": {"0": [4]},
                    "grc9_growth_parent_capacity_sources": {
                        "0": {
                            "front_capacity_source": "pressure_boundary",
                            "inactive_parent_port": 4,
                        }
                    },
                },
            },
            params=_expansion_config(
                lambda_birth=1e9,
                alpha_seed=0.25,
                mode_overrides={"growth_parent_eligibility": "grc9_front_capacity"},
            ),
        )

        model._apply_growth()

        state = model.get_state()
        growth_event = next(event for event in state.event_log if event.kind == "growth")
        self.assertEqual(4, growth_event.payload["parent_port_id"])
        self.assertEqual(
            "pressure_boundary",
            growth_event.payload["growth_parent_capacity_source"],
        )

    def test_pressure_boundary_growth_requires_positive_outward_pressure(self) -> None:
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
                        flux_uv=0.0,
                    )
                },
                "cached_quantities": {
                    "grc9_front_growth_eligible_ports": {"0": [4]},
                    "grc9_growth_parent_capacity_sources": {
                        "0": {
                            "front_capacity_source": "pressure_boundary",
                            "inactive_parent_port": 4,
                        }
                    },
                },
            },
            params=_expansion_config(
                lambda_birth=1e9,
                mode_overrides={"growth_parent_eligibility": "grc9_front_capacity"},
            ),
        )

        model._apply_growth()

        state = model.get_state()
        self.assertEqual([], state.cached_quantities["last_growth_events"])
        self.assertFalse(any(event.kind == "growth" for event in state.event_log))

    def test_invalid_growth_parent_eligibility_mode_raises(self) -> None:
        with self.assertRaises(InvalidParamsError):
            GRC9.from_state(
                state={
                    "topology": _topology_from_connections([(0, 0, 0, 1, 0)]),
                    "node_coherence": {"0": 1.0, "1": 1.0},
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
                params=_expansion_config(
                    mode_overrides={"growth_parent_eligibility": "unsupported"}
                ),
            )
