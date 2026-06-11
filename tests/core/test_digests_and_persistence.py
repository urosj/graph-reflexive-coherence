"""Tests for Phase 3 digest helpers and shared state persistence rules."""

from __future__ import annotations

import random
import unittest

from pygrc.core import (
    DIGEST_ALGORITHM,
    GRCEvent,
    GRCParams,
    GRCState,
    build_snapshot_metadata,
    build_standard_snapshot,
    build_state_payload,
    deserialize_rng_state,
    digest_canonical_data,
    digest_snapshot,
    digest_topology,
    export_weighted_topology,
    restore_state_payload,
    serialize_rng_state,
    serialize_runtime_rng_state,
    snapshot_from_json,
    snapshot_to_json,
)
from pygrc.core.storage import WeightedGraphBackend


class DigestAndPersistenceTest(unittest.TestCase):
    """Validate canonical digests and shared state persistence helpers."""

    def test_digest_helpers_use_sha256_and_ignore_mapping_order(self) -> None:
        left = {"b": 2, "a": [3, 4]}
        right = {"a": [3, 4], "b": 2}

        digest = digest_canonical_data(left)

        self.assertEqual("sha256", DIGEST_ALGORITHM)
        self.assertEqual(64, len(digest))
        self.assertEqual(digest, digest_canonical_data(right))

    def test_snapshot_and_topology_digests_are_stable_for_equivalent_content(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({"coherence": 1.0})
        right = graph.add_node({"coherence": 0.5})
        graph.add_edge(left, right, {"base_conductance": 0.25})
        topology = export_weighted_topology(graph)
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
            ),
            topology=topology,
        )

        self.assertEqual(digest_topology(topology), digest_topology(dict(topology)))
        self.assertEqual(digest_snapshot(snapshot), digest_snapshot(dict(snapshot)))

    def test_state_payload_roundtrip_preserves_remainder_and_python_rng_state(self) -> None:
        rng = random.Random(1234)
        original_rng_state = rng.getstate()
        state = GRCState(
            topology={"nodes": [0, 1]},
            node_values={"0": {"coherence": 1.0}},
            edge_values={"0": {"base_conductance": 0.25}},
            step_index=7,
            time=1.5,
            budget_target=2.5,
            remainder=1e-12,
            cached_quantities={"laplacian": {"0": 0.5}},
            event_log=[
                GRCEvent(
                    kind="spark",
                    step_index=7,
                    payload={"det_h": 0.0},
                    source_family="GRCV3",
                )
            ],
            observables={"budget_current": 2.5},
            rng_state=original_rng_state,
            params_identity="params-hash",
        )

        restored = restore_state_payload(build_state_payload(state))

        self.assertEqual(state.step_index, restored.step_index)
        self.assertEqual(state.time, restored.time)
        self.assertEqual(state.budget_target, restored.budget_target)
        self.assertEqual(state.remainder, restored.remainder)
        self.assertEqual(state.cached_quantities, restored.cached_quantities)
        self.assertEqual(state.event_log, restored.event_log)
        self.assertEqual(state.observables, restored.observables)
        self.assertEqual(state.params_identity, restored.params_identity)
        self.assertEqual(original_rng_state, restored.rng_state)

        replay = random.Random()
        replay.setstate(restored.rng_state)
        self.assertEqual(rng.random(), replay.random())

    def test_rng_helpers_tag_python_random_state(self) -> None:
        rng = random.Random(99)
        payload = serialize_runtime_rng_state(rng)

        self.assertEqual("python_random", payload["engine"])
        self.assertEqual(rng.getstate(), deserialize_rng_state(payload))
        self.assertEqual(rng.getstate(), deserialize_rng_state(serialize_rng_state(rng.getstate())))

    def test_snapshot_flow_preserves_raw_params_resolved_params_and_hash(self) -> None:
        params = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "evolution": {"alpha": 2.0},
                "constitutive_semantic_modes": {"frame_mode": "intrinsic_frame"},
            }
        )
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=3,
                params=params.raw_config,
                resolved_params=params.resolved_config,
                params_hash=params.params_hash,
                capabilities={"single_weight_edges"},
                rng_state=random.Random(7).getstate(),
            ),
            topology={"nodes": [], "edges": []},
        )

        restored = snapshot_from_json(snapshot_to_json(snapshot))

        self.assertEqual(
            {
                "dt": 0.1,
                "evolution": {"alpha": 2.0},
                "constitutive_semantic_modes": {"frame_mode": "intrinsic_frame"},
            },
            restored["metadata"]["params"],
        )
        self.assertEqual(
            {
                "dt": 0.1,
                "evolution": {"alpha": 2.0},
                "constitutive_semantic_modes": {"frame_mode": "intrinsic_frame"},
                "numerical_backend": {},
            },
            restored["metadata"]["resolved_params"],
        )
        self.assertEqual(params.params_hash, restored["metadata"]["params_hash"])
        self.assertEqual("python_random", restored["metadata"]["rng_state"]["engine"])

