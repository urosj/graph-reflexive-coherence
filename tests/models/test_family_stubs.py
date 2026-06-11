"""Contract tests for Phase 1 family stubs."""

from __future__ import annotations

from pathlib import Path
import random
import tempfile
import unittest

from pygrc.core import (
    GRCModel,
    GRCParams,
    GRCState,
    SnapshotCompatibilityError,
    load_snapshot,
)
from pygrc.models import GRC9, GRC9State, GRC9V3, GRCV2, GRCV3, GRCV3State


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
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class FamilyStubContractTest(unittest.TestCase):
    """Validate the non-executable family stubs against the common contract."""

    def test_family_stubs_import_and_inherit_contract(self) -> None:
        for cls in (GRCV2, GRCV3, GRC9, GRC9V3):
            with self.subTest(model=cls.__name__):
                self.assertTrue(issubclass(cls, GRCModel))

    def test_family_identifiers_and_capability_sets_are_correct(self) -> None:
        expectations = {
            GRCV2: "GRCV2",
            GRCV3: "GRCV3",
            GRC9: "GRC9",
            GRC9V3: "GRC9V3",
        }

        for cls, family in expectations.items():
            with self.subTest(model=cls.__name__):
                config = _valid_grcv2_config() if cls is GRCV2 else {"dt": 0.1}
                model = cls.from_config(config)
                self.assertEqual(family, model.MODEL_FAMILY)
                self.assertTrue(
                    set(model.CAPABILITY_PROFILE.required).issubset(
                        model.list_capabilities()
                    )
                )

    def test_family_stubs_bind_shared_params_and_state(self) -> None:
        model = GRCV3.from_config({"dt": 0.1})

        self.assertIsInstance(model.get_params(), GRCParams)
        self.assertIsInstance(model.get_state(), GRCState)
        self.assertIsInstance(model.get_state(), GRCV3State)

    def test_grc9_now_uses_a_real_typed_and_executable_surface(self) -> None:
        model = GRC9.from_config({"dt": 0.1})

        self.assertIsInstance(model.get_state(), GRC9State)
        result = model.step()

        self.assertEqual(1, result.step_index)

    def test_family_stubs_reject_non_state_objects_in_set_state(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        with self.assertRaises(SnapshotCompatibilityError):
            model.set_state({"step_index": 1})  # type: ignore[arg-type]

    def test_family_stub_snapshot_round_trip_via_save_and_load(self) -> None:
        rng = random.Random(17)
        model = GRC9V3.from_config(
            {
                "dt": 0.25,
                "state": {
                    "step_index": 3,
                    "time": 1.5,
                    "budget_target": 2.0,
                    "remainder": 1e-12,
                    "rng_state": rng.getstate(),
                    "params_identity": "params-17",
                    "observables": {"budget_current": 2.0},
                },
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "stub.json"
            model.save(str(path))
            saved_snapshot = load_snapshot(path)
            restored = GRC9V3.load(str(path))

        self.assertEqual(model.MODEL_FAMILY, restored.MODEL_FAMILY)
        self.assertEqual(model.get_state().step_index, restored.get_state().step_index)
        self.assertEqual(model.get_state().time, restored.get_state().time)
        self.assertEqual(model.get_state().remainder, restored.get_state().remainder)
        self.assertEqual(
            model.get_state().params_identity, restored.get_state().params_identity
        )
        self.assertEqual(
            "python_random", saved_snapshot["metadata"]["rng_state"]["engine"]
        )
        self.assertEqual(
            "python_random",
            saved_snapshot["dynamics"]["state"]["rng_state"]["engine"],
        )
        self.assertEqual(
            model.get_params().params_hash, saved_snapshot["metadata"]["params_hash"]
        )

    def test_family_stub_load_rejects_wrong_model_family(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "stub.json"
            model.save(str(path))

            with self.assertRaises(SnapshotCompatibilityError):
                GRC9.load(str(path))

    def test_family_stub_snapshot_uses_shared_contract_shape(self) -> None:
        model = GRCV3.from_config({"dt": 0.1, "state": {"step_index": 2}})

        snapshot = model.snapshot()

        self.assertEqual(
            [
                "metadata",
                "topology",
                "basin_attributes",
                "edge_labels",
                "dynamics",
                "observables",
                "events",
            ],
            list(snapshot.keys()),
        )
        self.assertEqual(
            {"nodes": [], "edges": [], "incidence": {}},
            snapshot["topology"],
        )
        self.assertEqual({}, snapshot["basin_attributes"]["nodes"])
        self.assertEqual(2, snapshot["dynamics"]["state"]["step_index"])
        self.assertEqual([], snapshot["events"])
