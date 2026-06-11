"""State and parameter contract tests for the GRCV3 family surface."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    BOUNDARY_BARRIER,
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    SnapshotCompatibilityError,
    load_snapshot,
)
from pygrc.models import BasinAttributes, GRCV3, GRCV3State


class GRCV3StateContractTest(unittest.TestCase):
    """Validate the Phase 5 Iteration 2 GRCV3 state and params surface."""

    def test_minimal_config_resolves_defaults_and_backend_selections(self) -> None:
        model = GRCV3.from_config({"dt": 0.1})

        params = model.get_params()
        modes = dict(params.constitutive_semantic_modes)
        backend_payload = modes[BACKEND_SELECTIONS_KEY]

        self.assertEqual("induced_local_frame", modes["frame_mode"])
        self.assertEqual("prune", modes["boundary_mode"])
        self.assertEqual("equal", modes["split_distribution_mode"])
        self.assertEqual("all", modes["edge_label_selection"])
        self.assertEqual("none", modes["curvature_backend"])
        self.assertEqual("measure_absorbed", modes["budget_measure_mode"])
        self.assertEqual("quadratic", params.evolution["site_potential_selection"])
        self.assertEqual(
            {"mu": 0.0, "scale": 1.0},
            params.evolution["site_potential_params"],
        )
        self.assertEqual("induced_local_frame", backend_payload["geometry"]["name"])
        self.assertEqual("weighted_least_squares", backend_payload["differential_summary"]["name"])
        self.assertEqual("tensor_exponential", backend_payload["metric"]["name"])
        self.assertEqual("none", backend_payload["curvature"]["name"])
        self.assertEqual(
            "signed_hessian_plus_attractor_delta",
            backend_payload["spark"]["name"],
        )
        self.assertEqual("basin_parent_child", backend_payload["hierarchy_update"]["name"])
        self.assertEqual("disabled", backend_payload["choice"]["name"])

    def test_minimal_family_surface_uses_grcv3_state(self) -> None:
        model = GRCV3.from_config({"dt": 0.1})

        self.assertIsInstance(model.get_state(), GRCV3State)
        self.assertEqual({}, model.get_state().nodes)
        self.assertEqual({}, model.get_state().base_conductance)
        self.assertEqual({}, model.get_state().hierarchy)
        self.assertEqual({}, model.get_state().choice_registry)
        self.assertEqual({}, model.get_state().collapse_registry)

    def test_capabilities_reflect_frame_and_boundary_modes(self) -> None:
        intrinsic_model = GRCV3.from_config({"dt": 0.1})
        intrinsic_claims = intrinsic_model.list_capabilities()
        self.assertIn(INTRINSIC_FRAME, intrinsic_claims)
        self.assertNotIn(HOST_EMBEDDING_FRAME, intrinsic_claims)
        self.assertNotIn(BOUNDARY_BARRIER, intrinsic_claims)

        host_model = GRCV3.from_config(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "frame_mode": "host_embedding",
                    "host_geometry_fields": ["chart_center_hint"],
                    "boundary_mode": "ghost",
                },
            }
        )
        host_claims = host_model.list_capabilities()
        self.assertIn(HOST_EMBEDDING_FRAME, host_claims)
        self.assertNotIn(INTRINSIC_FRAME, host_claims)
        self.assertIn(BOUNDARY_BARRIER, host_claims)

    def test_host_embedding_requires_host_geometry_fields(self) -> None:
        with self.assertRaises(Exception):
            GRCV3.from_config(
                {
                    "dt": 0.1,
                    "constitutive_semantic_modes": {"frame_mode": "host_embedding"},
                }
            )

    def test_from_state_restores_basin_attribute_nodes(self) -> None:
        model = GRCV3.from_state(
            state={
                "nodes": {
                    "0": {
                        "coherence": 1.5,
                        "gradient": [0.1, -0.2],
                        "hessian": [[2.0, 0.0], [0.0, 1.0]],
                        "net_flux": [0.5, -0.5],
                        "basin_mass": 3.0,
                        "basin_id": "root",
                        "parent_id": None,
                        "depth": 0,
                    }
                },
                "hierarchy": {"root": ["child_a", "child_b"]},
                "choice_registry": {"n0": {"kind": "ambiguous"}},
                "collapse_registry": {"n1": {"kind": "collapsed"}},
                "edge_label_computation_mode": {
                    "geometric_length": "induced_intrinsic"
                },
            },
            params={"dt": 0.1},
        )

        state = model.get_state()
        self.assertEqual((0,), tuple(state.nodes))
        self.assertIsInstance(state.nodes[0], BasinAttributes)
        self.assertEqual(1.5, state.nodes[0].coherence)
        self.assertEqual([0.1, -0.2], state.nodes[0].gradient)
        self.assertEqual("root", state.nodes[0].basin_id)
        self.assertEqual({"root": ["child_a", "child_b"]}, state.hierarchy)
        self.assertEqual({"n0": {"kind": "ambiguous"}}, state.choice_registry)
        self.assertEqual({"n1": {"kind": "collapsed"}}, state.collapse_registry)

    def test_snapshot_roundtrip_preserves_grcv3_groups(self) -> None:
        model = GRCV3.from_state(
            state={
                "nodes": {
                    "0": {
                        "coherence": 2.0,
                        "gradient": [0.0, 0.0],
                        "hessian": [[1.0, 0.0], [0.0, 1.0]],
                        "net_flux": [0.0, 0.0],
                        "basin_mass": 2.0,
                        "basin_id": "seed-0",
                        "parent_id": None,
                        "depth": 0,
                    }
                },
                "base_conductance": {"0": 1.25},
                "geometric_length": {"0": 0.75},
                "temporal_delay": {"0": 0.5},
                "flux_coupling": {"0": 0.25},
                "edge_label_computation_mode": {
                    "geometric_length": "induced_intrinsic",
                    "temporal_delay": "transport_ratio",
                    "flux_coupling": "absolute_flux",
                },
                "edge_label_params": {"temporal_delay": {"v0": 1.0}},
                "hessian_sign": 1,
                "step_index": 2,
            },
            params={"dt": 0.1},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRCV3.load(str(path))

        self.assertIn("basin_attributes", snapshot)
        self.assertIn("edge_labels", snapshot)
        self.assertEqual(1, snapshot["metadata"]["hessian_sign"])
        self.assertEqual(
            "seed-0",
            snapshot["basin_attributes"]["nodes"]["0"]["basin_id"],
        )
        self.assertEqual(
            1.25,
            snapshot["edge_labels"]["base_conductance"]["0"],
        )
        self.assertEqual(2, restored.get_state().step_index)
        self.assertEqual("seed-0", restored.get_state().nodes[0].basin_id)
        self.assertEqual(1.25, restored.get_state().base_conductance[0])

    def test_set_state_rejects_non_grcv3_state_objects(self) -> None:
        model = GRCV3.from_config({"dt": 0.1})
        with self.assertRaises(SnapshotCompatibilityError):
            model.set_state(object())  # type: ignore[arg-type]
