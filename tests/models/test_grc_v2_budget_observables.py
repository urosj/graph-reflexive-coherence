"""Continuity, budget, and observable tests for Phase 4 Iteration 7."""

from __future__ import annotations

import unittest

from pygrc.core import InvalidStateTransitionError
from pygrc.models import GRCV2


def _valid_grcv2_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "eta": 1.0,
            "kappa_c": 1.0,
            "lambda_c": 1.0,
            "xi_c": 1.0,
            "zeta_c": 1.0,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0},
            "eps_spark": 0.01,
            "tau_split": 2.0,
            "lambda_birth": 0.25,
            "alpha_seed": 0.5,
            "eps_prune": 0.001,
            "rng_seed": 0,
            "spark_backend": "cheeger_proxy",
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRCV2BudgetObservablesTest(unittest.TestCase):
    """Validate continuity update, budget closure, and observables."""

    def test_apply_continuity_updates_node_coherence_from_flux(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "flux": {"0:0": 2.0, "0:1": -2.0},
        }
        model = GRCV2.from_config(config)

        model._apply_continuity()

        state = model.get_state()
        self.assertAlmostEqual(1.8, state.nodes[0])
        self.assertAlmostEqual(1.2, state.nodes[1])
        self.assertEqual({0: -0.2, 1: 0.2}, state.cached_quantities["last_continuity_delta"])

    def test_enforce_budget_corrects_drift_and_clears_remainder(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [],
                "incidence": {"0": [], "1": []},
            },
            "nodes": {"0": 1.4, "1": 1.5},
            "budget_target": 3.0,
        }
        model = GRCV2.from_config(config)

        model._enforce_budget()

        state = model.get_state()
        self.assertAlmostEqual(3.0, sum(state.nodes.values()))
        self.assertEqual(0.0, state.remainder)

    def test_enforce_budget_clips_negative_coherence_and_tracks_correction(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}],
                "edges": [],
                "incidence": {"0": []},
            },
            "nodes": {"0": 0.1},
            "budget_target": 0.1,
        }
        model = GRCV2.from_config(config)
        model.get_state().nodes[0] = -0.1
        model.get_state().budget_target = -0.1

        model._enforce_budget()

        state = model.get_state()
        self.assertEqual(0.0, state.nodes[0])
        self.assertEqual(-0.1, state.remainder)
        self.assertEqual(0.1, state.cached_quantities["negative_mass_correction"])

    def test_step_observables_reflect_post_step_topology_and_budget(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["h_thr"] = 0.0
        config["evolution"]["lambda_birth"] = 1e9
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 1.0},
        }
        model = GRCV2.from_config(config)

        result = model.step()
        state = model.get_state()

        self.assertEqual(3, result.observables["num_nodes"])
        self.assertEqual(2, result.observables["num_edges"])
        self.assertEqual(1, result.observables["birth_count"])
        self.assertEqual(0, result.observables["spark_count"])
        self.assertAlmostEqual(sum(state.nodes.values()), result.observables["budget_current"])
        self.assertEqual(0.0, result.observables["budget_error"])

    def test_observables_use_paper_abundance_semantics(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())
        state = model.get_state()
        state.sink_set = {1, 3}
        state.basins = {1: {0, 1}, 3: {2, 3, 4}}
        state.nodes = {0: 1.0, 1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}

        observables = model.compute_observables()

        self.assertEqual(2.0, observables["abundance"])
        self.assertEqual(5.0, observables["weighted_abundance"])
        self.assertEqual(2, observables["sink_count"])
        self.assertEqual(11.0, observables["budget_current"])
