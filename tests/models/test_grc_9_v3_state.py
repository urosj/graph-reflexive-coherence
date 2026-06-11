"""State and parameter contract tests for the Phase 7 GRC9V3 surface."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    BOUNDARY_BARRIER,
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    InvalidParamsError,
    SnapshotCompatibilityError,
    load_snapshot,
)
from pygrc.models import GRC9, GRC9V3, GRC9V3NodeState, GRC9V3State, GRCV3, PortEdge


def _two_node_port_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {"label": "root"}},
                {"node_id": 1, "payload": {"label": "child"}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 4},
                    "payload": {"kind": "occupied"},
                }
            ],
            "incidence": {"0": [0], "1": [0]},
            "port_structure": {},
        },
        "nodes": {
            "0": {
                "coherence": 2.0,
                "gradient_row_basis": [0.1, 0.0, -0.1],
                "signed_hessian_row_basis": [1.0, -0.5, 0.25],
                "net_flux_summary": [0.0, 0.2, -0.2],
                "basin_mass": 2.0,
                "basin_id": "root",
                "parent_id": None,
                "depth": 0,
            },
            "1": {
                "coherence": 1.0,
                "basin_mass": 1.0,
                "basin_id": "child",
                "parent_id": "root",
                "depth": 1,
            },
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 5,
                "conductance": 0.75,
                "flux_uv": 0.125,
            }
        },
        "base_conductance": {"0": 0.75},
        "geometric_length": {"0": 1.25},
        "temporal_delay": {"0": 2.5},
        "flux_coupling": {"0": 0.125},
        "potential": {"0": 2.0, "1": 1.0},
        "sink_set": [1],
        "basins": {"1": [0, 1]},
        "hierarchy": {"root": ["child"]},
        "choice_registry": {"0": {"backend": "disabled"}},
        "collapse_registry": {"1": {"kind": "collapsed"}},
        "coarse_cache": {"column:conductance": {"mode": "full"}},
        "edge_label_computation_mode": {"geometric_length": "fixed_port_chart"},
        "edge_label_params": {"selection": "all", "hessian_backend": "row_basis_diagonal"},
        "step_index": 2,
    }


class GRC9V3StateContractTest(unittest.TestCase):
    """Validate the Iteration 1 GRC9V3 state and params surface."""

    def test_minimal_config_resolves_defaults_and_constructs_hybrid_state(self) -> None:
        model = GRC9V3.from_config({"dt": 0.1})

        params = model.get_params()
        modes = dict(params.constitutive_semantic_modes)
        backend_payload = modes[BACKEND_SELECTIONS_KEY]
        state = model.get_state()

        self.assertEqual("fixed_port_chart", modes["frame_mode"])
        self.assertEqual("prune", modes["boundary_mode"])
        self.assertEqual("equal", modes["expansion_distribution_mode"])
        self.assertEqual("all", modes["edge_label_selection"])
        self.assertEqual("none", modes["curvature_backend"])
        self.assertEqual("row_basis_diagonal", modes["hessian_backend"])
        self.assertEqual("sink_compatibility", modes["choice_backend"])
        self.assertEqual("simplex_projection", modes["budget_correction_method"])
        self.assertEqual("row_basis_diagonal", backend_payload["hessian"]["name"])
        self.assertIsInstance(state, GRC9V3State)
        self.assertEqual({}, state.nodes)
        self.assertEqual({}, state.port_edges)
        self.assertEqual({}, state.hierarchy)
        self.assertEqual({}, state.choice_registry)
        self.assertEqual(params.params_hash, state.params_identity)
        self.assertIsNotNone(state.rng_state)

    def test_weighted_least_squares_hessian_backend_is_allowed_for_comparison(self) -> None:
        model = GRC9V3.from_config(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "hessian_backend": "weighted_least_squares",
                    "budget_correction_method": "uniform_shift",
                },
            }
        )

        modes = dict(model.get_params().constitutive_semantic_modes)
        self.assertEqual("weighted_least_squares", modes["hessian_backend"])
        self.assertEqual(
            "weighted_least_squares",
            modes[BACKEND_SELECTIONS_KEY]["hessian"]["name"],
        )
        self.assertEqual("uniform_shift", modes["budget_correction_method"])

    def test_defaults_are_parent_derived_not_ad_hoc_thresholds(self) -> None:
        grc9 = GRC9.from_config({"dt": 0.1})
        grcv3 = GRCV3.from_config({"dt": 0.1})
        grc9v3 = GRC9V3.from_config({"dt": 0.1})

        grc9_evolution = grc9.get_params().evolution
        grcv3_evolution = grcv3.get_params().evolution
        grc9v3_params = grc9v3.get_params()
        grc9v3_evolution = grc9v3_params.evolution
        provenance = grc9v3_params.constitutive_semantic_modes[
            "default_evolution_provenance"
        ]

        for key in (
            "alpha",
            "beta",
            "gamma",
            "delta",
            "eta",
            "kappa_c",
            "lambda_c",
            "xi_c",
            "zeta_c",
            "eps_gradient",
            "eps_hessian",
            "eps_spark",
            "compatibility_score_params",
            "site_potential_selection",
            "site_potential_params",
        ):
            self.assertEqual(grcv3_evolution[key], grc9v3_evolution[key])

        for key in (
            "tau_instability",
            "D_eff_target",
            "w_bond",
            "lambda_birth",
            "alpha_seed",
        ):
            self.assertEqual(grc9_evolution[key], grc9v3_evolution[key])

        self.assertEqual("GRCV3 signed-Hessian spark threshold", provenance["eps_spark"])
        self.assertEqual("GRC9 mechanical expansion default", provenance["D_eff_target"])

    def test_capabilities_claim_required_hybrid_surface_without_optional_claims(self) -> None:
        model = GRC9V3.from_config({"dt": 0.1})
        claims = model.list_capabilities()

        self.assertIn(INTRINSIC_FRAME, claims)
        self.assertNotIn(HOST_EMBEDDING_FRAME, claims)
        self.assertNotIn(BOUNDARY_BARRIER, claims)

    def test_invalid_mode_values_are_rejected_early(self) -> None:
        invalid_modes = (
            {"frame_mode": "host_embedding"},
            {"boundary_mode": "ghost"},
            {"boundary_mode": "barrier"},
            {"expansion_distribution_mode": "biased"},
            {"curvature_backend": "ricci"},
            {"hessian_backend": "full_matrix"},
            {"choice_backend": "roulette"},
            {"quadrature_mode": "host_measure"},
            {"budget_correction_method": "clip"},
            {"spark_signed_crossing": "yes"},
        )

        for modes in invalid_modes:
            with self.subTest(modes=modes):
                with self.assertRaises(InvalidParamsError):
                    GRC9V3.from_config(
                        {"dt": 0.1, "constitutive_semantic_modes": modes}
                    )

    def test_invalid_threshold_values_are_rejected_early(self) -> None:
        invalid_evolution = (
            {"eps_gradient": 0.0},
            {"eps_hessian": -1.0},
            {"eps_spark": -1.0},
            {"eps_tau": 0.0},
            {"alpha_seed": 1.1},
            {"lambda_birth": -0.1},
            {"compatibility_score_params": "loose"},
        )

        for evolution in invalid_evolution:
            with self.subTest(evolution=evolution):
                with self.assertRaises(InvalidParamsError):
                    GRC9V3.from_config({"dt": 0.1, "evolution": evolution})

    def test_from_state_restores_port_topology_and_hybrid_fields(self) -> None:
        model = GRC9V3.from_state(state=_two_node_port_state(), params={"dt": 0.1})
        restored = model.get_state()

        self.assertEqual((0, 1), tuple(restored.topology.iter_live_node_ids()))
        self.assertEqual((0,), tuple(restored.topology.iter_live_edge_ids()))
        self.assertIsInstance(restored.nodes[0], GRC9V3NodeState)
        self.assertEqual([0.1, 0.0, -0.1], restored.nodes[0].gradient_row_basis)
        self.assertEqual([1.0, -0.5, 0.25], restored.nodes[0].signed_hessian_row_basis)
        self.assertEqual("child", restored.nodes[1].basin_id)
        self.assertIsInstance(restored.port_edges[0], PortEdge)
        self.assertEqual(0.75, restored.port_edges[0].conductance)
        self.assertEqual({1}, restored.sink_set)
        self.assertEqual({1: {0, 1}}, restored.basins)
        self.assertEqual({"root": ["child"]}, restored.hierarchy)
        self.assertEqual({"1": {"kind": "collapsed"}}, restored.collapse_registry)
        self.assertEqual(3.0, restored.budget_target)
        self.assertEqual("initial_state_sum", restored.cached_quantities["budget_target_source"])

    def test_set_state_rejects_incompatible_objects_and_invalid_references(self) -> None:
        model = GRC9V3.from_config({"dt": 0.1})

        with self.assertRaises(SnapshotCompatibilityError):
            model.set_state(object())  # type: ignore[arg-type]

        with self.assertRaises(SnapshotCompatibilityError):
            model.set_state(GRC9V3State(nodes={99: GRC9V3NodeState(coherence=1.0)}))

    def test_snapshot_save_load_preserves_hybrid_groups(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_port_state(),
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "hessian_backend": "weighted_least_squares"
                },
            },
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9v3.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRC9V3.load(str(path))

        self.assertEqual("GRC9V3", snapshot["metadata"]["model_family"])
        self.assertEqual(
            "weighted_least_squares",
            snapshot["metadata"]["params"]["constitutive_semantic_modes"]["hessian_backend"],
        )
        self.assertEqual(
            "root",
            snapshot["basin_attributes"]["nodes"]["0"]["basin_id"],
        )
        self.assertEqual(
            {"root": ["child"]},
            snapshot["basin_attributes"]["hierarchy"],
        )
        self.assertEqual(0.75, snapshot["edge_labels"]["base_conductance"]["0"])
        self.assertEqual(
            "weighted_least_squares",
            restored.get_params().constitutive_semantic_modes["hessian_backend"],
        )
        self.assertEqual(0.125, restored.get_state().port_edges[0].flux_uv)
        self.assertEqual(2, restored.get_state().step_index)

    def test_budget_target_is_fixed_at_initialization_when_not_provided(self) -> None:
        model = GRC9V3.from_state(state=_two_node_port_state(), params={"dt": 0.1})
        state = model.get_state()
        state.nodes[0] = GRC9V3NodeState(coherence=10.0)
        model.set_state(state)

        summary = model.enforce_quadrature_budget()

        self.assertEqual(3.0, summary["budget_target"])
        self.assertAlmostEqual(3.0, summary["budget_after"])

    def test_explicit_zero_budget_target_is_preserved(self) -> None:
        state = _two_node_port_state()
        state["budget_target"] = 0.0
        model = GRC9V3.from_state(state=state, params={"dt": 0.1})

        self.assertEqual(0.0, model.get_state().budget_target)
        self.assertEqual(
            "explicit_state",
            model.get_state().cached_quantities["budget_target_source"],
        )

        summary = model.enforce_quadrature_budget()

        self.assertEqual(0.0, summary["budget_target"])
        self.assertAlmostEqual(0.0, summary["budget_after"])
        self.assertAlmostEqual(0.0, sum(node.coherence for node in model.get_state().nodes.values()))


if __name__ == "__main__":
    unittest.main()
