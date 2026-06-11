"""Validation-matrix tests for Phase 4 Iteration 9."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pygrc.core import (
    InvalidParamsError,
    SnapshotCompatibilityError,
    UnsupportedCapabilityError,
)
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


class GRCV2ValidationMatrixTest(unittest.TestCase):
    """Cover the remaining Phase 4 validation/error matrix."""

    def test_invalid_parameter_ranges_are_rejected(self) -> None:
        negative_dt = _valid_grcv2_config()
        negative_dt["dt"] = 0.0
        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(negative_dt)

        negative_eta = _valid_grcv2_config()
        negative_eta["evolution"]["eta"] = -1.0
        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(negative_eta)

        negative_tau_split = _valid_grcv2_config()
        negative_tau_split["evolution"]["tau_split"] = 0.0
        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(negative_tau_split)

    def test_unsupported_capability_requests_are_rejected(self) -> None:
        with self.assertRaises(UnsupportedCapabilityError):
            GRCV2.CAPABILITY_PROFILE.validate_claims(
                set(GRCV2.CAPABILITY_PROFILE.required) | {"port_graph"}
            )

    def test_incompatible_state_deserialization_is_rejected(self) -> None:
        bad_state = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}],
                "edges": [],
                "incidence": {"0": []},
            },
            "nodes": {"0": 1.0},
            "event_log": {"not": "a-list"},
        }
        with self.assertRaises(SnapshotCompatibilityError):
            GRCV2.from_state(bad_state, _valid_grcv2_config())

    def test_multi_step_save_load_replay_remains_deterministic(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["h_thr"] = 0.0
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 1.0},
        }
        model_a = GRCV2.from_config(config)
        model_b = GRCV2.from_config(config)

        first_a = [model_a.step() for _ in range(3)]
        first_b = [model_b.step() for _ in range(3)]
        self.assertEqual(
            [result.observables for result in first_a],
            [result.observables for result in first_b],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "replay.json"
            model_a.save(str(path))
            restored = GRCV2.load(str(path))

        next_original = [model_a.step() for _ in range(2)]
        next_restored = [restored.step() for _ in range(2)]
        self.assertEqual(
            [result.observables for result in next_original],
            [result.observables for result in next_restored],
        )
        self.assertEqual(
            [
                [(event.kind, event.payload) for event in result.events]
                for result in next_original
            ],
            [
                [(event.kind, event.payload) for event in result.events]
                for result in next_restored
            ],
        )
