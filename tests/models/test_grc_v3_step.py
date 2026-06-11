"""Theory-facing direct tests for GRCV3 semantic update helpers."""

from __future__ import annotations

import unittest

from pygrc.core import WeightedGraphBackend
from pygrc.models import GRCV3


def _node_attributes(
    *,
    coherence: float,
    gradient: list[float],
    hessian: list[list[float]],
    basin_id: str | int,
    parent_id: str | int | None = None,
    depth: int = 0,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": gradient,
        "hessian": hessian,
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": parent_id,
        "depth": depth,
    }


class GRCV3TheoryFacingStepTest(unittest.TestCase):
    def test_signed_hessian_basin_criterion_requires_small_gradient_and_positive_curvature(self) -> None:
        graph = WeightedGraphBackend()
        candidate = graph.add_node({})
        weak_curvature = graph.add_node({})
        strong_gradient = graph.add_node({})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(candidate): _node_attributes(
                        coherence=1.0,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.0]],
                        basin_id="candidate",
                    ),
                    str(weak_curvature): _node_attributes(
                        coherence=1.0,
                        gradient=[0.0, 0.0],
                        hessian=[[5e-4, 0.0], [0.0, 1.0]],
                        basin_id="weak",
                    ),
                    str(strong_gradient): _node_attributes(
                        coherence=1.0,
                        gradient=[1e-2, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.0]],
                        basin_id="gradient",
                    ),
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph

        model.rebuild_identity_state()

        geometric_identity = model.get_state().cached_quantities["geometric_identity"]
        self.assertEqual([candidate], geometric_identity["seed_nodes"])
        self.assertEqual([candidate], geometric_identity["validated_basin_ids"])
        self.assertEqual(
            {
                str(candidate): candidate,
                str(weak_curvature): weak_curvature,
                str(strong_gradient): strong_gradient,
            },
            geometric_identity["basin_id_by_node"],
        )

    def test_split_completion_confirms_spark_when_geometric_basin_count_increases(self) -> None:
        graph = WeightedGraphBackend()
        node_id = graph.add_node({})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(node_id): _node_attributes(
                        coherence=1.0,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.0]],
                        basin_id=node_id,
                    )
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()
        model.get_state().cached_quantities["split_registry"] = {
            "split:0:0:0": {
                "parent_node_id": node_id,
                "parent_basin_id": node_id,
                "pre_metrics": {"sink_count": 0, "validated_basin_count": 0},
                "min_child_basins": 1,
                "candidate_rank": 0,
                "spark_confirmed": False,
            }
        }

        events = model._evaluate_split_completion()

        self.assertEqual(["spark"], [event.kind for event in events])
        self.assertEqual(1, events[0].payload["geometric_delta"])
        self.assertEqual(0, events[0].payload["sink_delta"])
        self.assertTrue(
            model.get_state().cached_quantities["split_registry"]["split:0:0:0"][
                "spark_confirmed"
            ]
        )

    def test_split_completion_stays_pending_without_required_attractor_gain(self) -> None:
        graph = WeightedGraphBackend()
        node_id = graph.add_node({})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(node_id): _node_attributes(
                        coherence=1.0,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.0]],
                        basin_id=node_id,
                    )
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()
        model.get_state().cached_quantities["split_registry"] = {
            "split:0:0:0": {
                "parent_node_id": node_id,
                "parent_basin_id": node_id,
                "pre_metrics": {"sink_count": 0, "validated_basin_count": 1},
                "min_child_basins": 2,
                "candidate_rank": 0,
                "spark_confirmed": False,
            }
        }

        events = model._evaluate_split_completion()

        self.assertEqual(["spark_pending"], [event.kind for event in events])
        self.assertEqual(0, events[0].payload["geometric_delta"])
        self.assertEqual(0, events[0].payload["sink_delta"])
        self.assertFalse(
            model.get_state().cached_quantities["split_registry"]["split:0:0:0"][
                "spark_confirmed"
            ]
        )
