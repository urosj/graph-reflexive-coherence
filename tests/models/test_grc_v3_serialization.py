"""Serialization and replay contract tests for the GRCV3 family surface."""

from __future__ import annotations

from pathlib import Path
import random
import tempfile
import unittest

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    SnapshotCompatibilityError,
    build_backend_selection,
    build_backend_selection_payload,
    digest_snapshot,
    load_snapshot,
    save_snapshot,
)
from pygrc.models import GRCV3


def _node_attributes(*, coherence: float, basin_id: str | int, depth: int = 0) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": depth,
    }


class GRCV3SerializationContractTest(unittest.TestCase):
    def test_snapshot_roundtrip_preserves_backend_selections_choice_state_events_and_rng(self) -> None:
        rng = random.Random(17)
        model = GRCV3.from_state(
            state={
                "nodes": {
                    "0": _node_attributes(coherence=1.5, basin_id="root"),
                    "1": _node_attributes(coherence=0.5, basin_id=1, depth=1),
                },
                "base_conductance": {"0": 1.25},
                "geometric_length": {"0": 0.75},
                "temporal_delay": {"0": 0.5},
                "flux_coupling": {"0": 0.25},
                "flux": {"0:0": 0.2, "0:1": -0.2},
                "potential": {"0": 1.0, "1": 0.5},
                "sink_set": [1],
                "basins": {"1": [0, 1]},
                "hierarchy": {"root": [1], "1": []},
                "choice_registry": {
                    "0": {
                        "backend": "sink_compatibility",
                        "viable_sink_ids": ["1", "2"],
                        "winner_sink_id": "1",
                    }
                },
                "collapse_registry": {
                    "0": {
                        "backend": "sink_compatibility",
                        "collapsed_sink_id": "1",
                        "persistence_mode": "registry_only",
                    }
                },
                "cached_quantities": {
                    "hessian_sign": 1,
                    "successor_map": {"0": 1, "1": None},
                },
                "event_log": [
                    {
                        "kind": "choice_detected",
                        "step_index": 2,
                        "payload": {"node_id": 0},
                        "source_family": "GRCV3",
                    },
                    {
                        "kind": "collapse",
                        "step_index": 3,
                        "payload": {"node_id": 0, "collapsed_sink_id": "1"},
                        "source_family": "GRCV3",
                    },
                ],
                "observables": {"choice_regime_count": 1.0},
                "rng_state": rng.getstate(),
                "step_index": 3,
                "time": 0.3,
                "budget_target": 2.0,
                "remainder": 1e-12,
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="choice",
                                name="sink_compatibility",
                                params={
                                    "epsilon_choice": 0.1,
                                    "epsilon_collapse": 0.2,
                                },
                            )
                        ]
                    )
                },
            },
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-serialization.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRCV3.load(str(path))

        restored_state = restored.get_state()
        backend_payload = restored.get_params().constitutive_semantic_modes[BACKEND_SELECTIONS_KEY]

        self.assertIn(BACKEND_SELECTIONS_KEY, snapshot["metadata"]["resolved_params"]["constitutive_semantic_modes"])
        self.assertEqual("sink_compatibility", backend_payload["choice"]["name"])
        self.assertEqual(
            {"epsilon_choice": 0.1, "epsilon_collapse": 0.2},
            backend_payload["choice"]["params"],
        )
        self.assertEqual(1, snapshot["metadata"]["hessian_sign"])
        self.assertEqual({"root": [1], 1: []}, restored_state.hierarchy)
        self.assertEqual(model.get_state().choice_registry, restored_state.choice_registry)
        self.assertEqual(model.get_state().collapse_registry, restored_state.collapse_registry)
        self.assertEqual(tuple(model.get_state().event_log), tuple(restored_state.event_log))
        self.assertEqual(model.get_state().rng_state, restored_state.rng_state)
        replay = random.Random()
        replay.setstate(restored_state.rng_state)
        self.assertEqual(rng.random(), replay.random())

    def test_snapshot_digest_is_stable_across_save_load_roundtrip(self) -> None:
        model = GRCV3.from_state(
            state={
                "nodes": {"0": _node_attributes(coherence=1.0, basin_id="seed")},
                "cached_quantities": {"hessian_sign": 1},
                "event_log": [
                    {
                        "kind": "spark_pending",
                        "step_index": 1,
                        "payload": {"registry_key": "split:1:0:0"},
                        "source_family": "GRCV3",
                    }
                ],
                "step_index": 1,
            },
            params={"dt": 0.1},
        )

        initial_digest = digest_snapshot(model.snapshot())

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-digest.json"
            model.save(str(path))
            restored = GRCV3.load(str(path))

        restored_digest = digest_snapshot(restored.snapshot())

        self.assertEqual(initial_digest, restored_digest)

    def test_load_can_restore_event_log_from_top_level_events_fallback(self) -> None:
        model = GRCV3.from_state(
            state={
                "nodes": {"0": _node_attributes(coherence=1.0, basin_id="seed")},
                "cached_quantities": {"hessian_sign": 1},
                "event_log": [
                    {
                        "kind": "choice_detected",
                        "step_index": 1,
                        "payload": {"node_id": 0},
                        "source_family": "GRCV3",
                    }
                ],
                "step_index": 1,
            },
            params={"dt": 0.1},
        )
        snapshot = model.snapshot()
        del snapshot["dynamics"]["state"]["event_log"]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-events-fallback.json"
            save_snapshot(path, snapshot)
            restored = GRCV3.load(str(path))

        self.assertEqual(["choice_detected"], [event.kind for event in restored.get_state().event_log])

    def test_load_rejects_invalid_event_log_shape(self) -> None:
        model = GRCV3.from_state(
            state={"nodes": {"0": _node_attributes(coherence=1.0, basin_id="seed")}},
            params={"dt": 0.1},
        )
        snapshot = model.snapshot()
        snapshot["dynamics"]["state"]["event_log"] = ["not-a-mapping"]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-invalid-events.json"
            save_snapshot(path, snapshot)
            with self.assertRaises(SnapshotCompatibilityError):
                GRCV3.load(str(path))
