"""Cross-family reset-baseline persistence and identity-v2 tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from pygrc.core import SnapshotCompatibilityError, load_snapshot, save_snapshot
from pygrc.models import (
    GRC9,
    GRC9V3,
    GRCV2,
    GRCV3,
    LGRC9V3,
    LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION,
    LGRC9V3_RESTORATION_IDENTITY_V2_SCHEMA_VERSION,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
    lgrc9v3_restoration_identity_v2,
)


MODEL_FAMILIES = (GRCV2, GRCV3, GRC9, GRC9V3, LGRC9V3)


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
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _model(model_type: type[object]) -> object:
    config = _valid_grcv2_config() if model_type is GRCV2 else {"dt": 0.1}
    return model_type.from_config(config)  # type: ignore[attr-defined,no-any-return]


def _index(model: object) -> int:
    state = model.get_state()  # type: ignore[attr-defined]
    if isinstance(model, LGRC9V3):
        return int(state.scheduler_event_index)
    return int(state.step_index)


def _set_index(model: object, value: int) -> None:
    state = deepcopy(model.get_state())  # type: ignore[attr-defined]
    if isinstance(model, LGRC9V3):
        state.scheduler_event_index = value
    else:
        state.step_index = value
    model.set_state(state)  # type: ignore[attr-defined]


class ResetBaselinePersistenceTests(unittest.TestCase):
    def test_all_concrete_families_preserve_construction_baseline(self) -> None:
        for model_type in MODEL_FAMILIES:
            with self.subTest(model_family=model_type.__name__):
                model = _model(model_type)
                _set_index(model, 7)
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = Path(tmp_dir) / "model.json"
                    model.save(str(path))  # type: ignore[attr-defined]
                    restored = model_type.load(str(path))

                self.assertEqual(7, _index(restored))
                model.reset()  # type: ignore[attr-defined]
                restored.reset()
                self.assertEqual(0, _index(model))
                self.assertEqual(0, _index(restored))

    def test_set_state_preserves_baseline_and_rebase_is_explicit(self) -> None:
        for model_type in MODEL_FAMILIES:
            with self.subTest(model_family=model_type.__name__):
                model = _model(model_type)
                _set_index(model, 4)
                model.reset()  # type: ignore[attr-defined]
                self.assertEqual(0, _index(model))

                _set_index(model, 5)
                model.rebase_reset_baseline()  # type: ignore[attr-defined]
                _set_index(model, 9)
                model.reset()  # type: ignore[attr-defined]
                self.assertEqual(5, _index(model))

    def test_repeated_save_load_preserves_baseline(self) -> None:
        for model_type in MODEL_FAMILIES:
            with self.subTest(model_family=model_type.__name__):
                model = _model(model_type)
                _set_index(model, 6)
                with tempfile.TemporaryDirectory() as tmp_dir:
                    current = model
                    for cycle in range(3):
                        path = Path(tmp_dir) / f"model-{cycle}.json"
                        current.save(str(path))  # type: ignore[attr-defined]
                        current = model_type.load(str(path))
                current.reset()
                self.assertEqual(0, _index(current))

    def test_legacy_snapshot_loads_but_reset_requires_explicit_rebase(self) -> None:
        for model_type in MODEL_FAMILIES:
            with self.subTest(model_family=model_type.__name__):
                model = _model(model_type)
                _set_index(model, 3)
                legacy_snapshot = model.snapshot()  # type: ignore[attr-defined]
                legacy_snapshot.pop("reset_baseline")
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = Path(tmp_dir) / "legacy.json"
                    save_snapshot(path, legacy_snapshot)
                    restored = model_type.load(str(path))

                with self.assertRaises(SnapshotCompatibilityError):
                    restored.reset()
                with tempfile.TemporaryDirectory() as tmp_dir:
                    unavailable_path = Path(tmp_dir) / "unavailable.json"
                    restored.save(str(unavailable_path))
                    unavailable_snapshot = load_snapshot(unavailable_path)
                    self.assertEqual(
                        "unavailable",
                        unavailable_snapshot["reset_baseline"]["status"],
                    )
                    restored = model_type.load(str(unavailable_path))
                with self.assertRaises(SnapshotCompatibilityError):
                    restored.reset()
                restored.rebase_reset_baseline()
                _set_index(restored, 8)
                restored.reset()
                self.assertEqual(3, _index(restored))

    def test_lgrc_identity_v2_includes_reset_baseline_without_changing_v1(self) -> None:
        first = LGRC9V3.from_config({"dt": 0.1})
        second = LGRC9V3.from_config({"dt": 0.1})
        _set_index(second, 2)
        second.rebase_reset_baseline()
        _set_index(first, 7)
        _set_index(second, 7)

        self.assertEqual(
            digest_lgrc9v3_restoration_identity_v1(first),
            digest_lgrc9v3_restoration_identity_v1(second),
        )
        self.assertNotEqual(
            digest_lgrc9v3_restoration_identity_v2(first),
            digest_lgrc9v3_restoration_identity_v2(second),
        )
        artifact = lgrc9v3_restoration_identity_v2(first)
        self.assertEqual(
            LGRC9V3_RESTORATION_IDENTITY_V2_SCHEMA_VERSION,
            artifact["artifact_schema_version"],
        )
        self.assertEqual(
            LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION,
            artifact["current_state_restoration_identity"]["artifact_schema_version"],
        )

    def test_lgrc_identity_v2_rejects_legacy_missing_baseline(self) -> None:
        snapshot = LGRC9V3.from_config({"dt": 0.1}).snapshot()
        snapshot.pop("reset_baseline")

        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v2(snapshot)

    def test_lgrc_identity_v2_is_stable_across_save_load(self) -> None:
        model = LGRC9V3.from_config({"dt": 0.1})
        _set_index(model, 5)
        before = digest_lgrc9v3_restoration_identity_v2(model)

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc.json"
            model.save(str(path))
            restored = LGRC9V3.load(str(path))

        self.assertEqual(
            before,
            digest_lgrc9v3_restoration_identity_v2(restored),
        )

    def test_malformed_or_cross_family_baseline_fails_closed(self) -> None:
        snapshot = LGRC9V3.from_config({"dt": 0.1}).snapshot()
        malformed = deepcopy(snapshot)
        malformed["reset_baseline"]["snapshot"] = "not-a-snapshot"
        wrong_family = deepcopy(snapshot)
        wrong_family["reset_baseline"]["model_family"] = "GRC9V3"
        wrong_params = deepcopy(snapshot)
        wrong_params["reset_baseline"]["snapshot"]["metadata"]["params_hash"] = (
            "different-params"
        )
        recursive = deepcopy(snapshot)
        recursive["reset_baseline"]["snapshot"]["reset_baseline"] = deepcopy(
            snapshot["reset_baseline"]
        )

        for candidate in (malformed, wrong_family, wrong_params, recursive):
            with self.subTest(candidate=candidate["reset_baseline"]):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = Path(tmp_dir) / "malformed.json"
                    with self.assertRaises(SnapshotCompatibilityError):
                        save_snapshot(path, candidate)


if __name__ == "__main__":
    unittest.main()
