"""Tests for LGRC9V3 restoration-identity projections."""

from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    PortGraphBackend,
    SnapshotCompatibilityError,
    digest_canonical_data,
)
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3_RESTORATION_IDENTITY_KIND,
    LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION,
    PortEdge,
    digest_lgrc9v3_restoration_identity_v1,
    lgrc9v3_restoration_identity_v1,
)
from pygrc.models.lgrc_9_v3_restoration import (
    LGRC9V3_EMBEDDED_GRC9V3_STATE_KIND,
    LGRC9V3_EMBEDDED_GRC9V3_STATE_SCHEMA_VERSION,
    build_lgrc9v3_embedded_grc9v3_state_v1,
    digest_lgrc9v3_embedded_grc9v3_state_v1,
)


def _state() -> GRC9V3State:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "left"})
    removed = graph.add_node({"label": "removed"})
    node_2 = graph.add_node({"label": "right"})
    graph.remove_node(removed)
    removed_edge = graph.connect_ports(
        node_0,
        1,
        node_2,
        1,
        {"kind": "removed"},
    )
    graph.remove_edge(removed_edge)
    edge_id = graph.connect_ports(
        node_2,
        0,
        node_0,
        0,
        {"kind": "restoration_fixture"},
    )
    return GRC9V3State(
        topology=graph,
        nodes={
            node_0: GRC9V3NodeState(
                coherence=1.25,
                basin_mass=1.0,
                basin_id="left-basin",
            ),
            node_2: GRC9V3NodeState(
                coherence=1.75,
                basin_mass=2.0,
                basin_id="right-basin",
                parent_id="left-basin",
                depth=1,
            ),
        },
        port_edges={
            edge_id: PortEdge(
                node_u=node_2,
                port_u=1,
                node_v=node_0,
                port_v=1,
                conductance=0.75,
                flux_uv=-0.0,
            )
        },
        base_conductance={edge_id: 0.75},
        geometric_length={edge_id: 2.0},
        temporal_delay={edge_id: 1.5},
        flux_coupling={edge_id: 0.25},
        potential={node_0: 0.25, node_2: -0.25},
        sink_set={node_0},
        basins={node_0: {node_0, node_2}},
        hierarchy={"left-basin": ["right-basin"]},
        choice_registry={"choice-1": {"selected": node_0}},
        collapse_registry={"collapse-1": {"sink": node_0}},
        coarse_cache={"coarse": {"members": [node_0, node_2]}},
        step_index=3,
        time=2.5,
        budget_target=3.0,
        remainder=0.0,
        cached_quantities={"evidence_surface": {"value": 0.5}},
        observables={"fixture_observable": 3.0},
    )


def _model() -> LGRC9V3:
    return LGRC9V3.from_state(
        _state(),
        {
            "dt": 1.0,
            "evolution": {"rng_seed": 17},
        },
    )


def _active_model() -> LGRC9V3:
    model = _model()
    model.schedule_packet_departure(
        source_node_id=2,
        target_node_id=0,
        edge_id=1,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    return model


def _mapping_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            key for child in value.values() for key in _mapping_keys(child)
        }
    if isinstance(value, list):
        return {key for child in value for key in _mapping_keys(child)}
    return set()


class LGRC9V3EmbeddedRestorationStateTests(unittest.TestCase):
    def test_component_is_deterministic_complete_and_non_mutating(self) -> None:
        snapshot = _model().snapshot()
        original = deepcopy(snapshot)

        first = build_lgrc9v3_embedded_grc9v3_state_v1(snapshot)
        second = build_lgrc9v3_embedded_grc9v3_state_v1(snapshot)

        self.assertEqual(original, snapshot)
        self.assertEqual(first, second)
        self.assertEqual(
            LGRC9V3_EMBEDDED_GRC9V3_STATE_KIND,
            first["component_kind"],
        )
        self.assertEqual(
            LGRC9V3_EMBEDDED_GRC9V3_STATE_SCHEMA_VERSION,
            first["component_schema_version"],
        )
        self.assertEqual(3, first["stable_allocation"]["next_node_id"])
        self.assertEqual(
            ["live", "tombstone", "live"],
            first["stable_allocation"]["node_slot_status"],
        )
        self.assertEqual(2, first["stable_allocation"]["next_edge_id"])
        self.assertEqual(
            ["tombstone", "live"],
            first["stable_allocation"]["edge_slot_status"],
        )
        self.assertIn("choice_registry", first["state"])
        self.assertIn("collapse_registry", first["state"])
        self.assertIn("expansion_registry", first["state"])
        self.assertIn("coarse_cache", first["state"])
        self.assertIn("cached_quantities", first["state"])
        self.assertIn("rng_state", first["state"])
        self.assertIsInstance(first["base_events"], list)
        self.assertIn("node_count", first["base_observables"])
        self.assertEqual(
            digest_lgrc9v3_embedded_grc9v3_state_v1(snapshot),
            digest_lgrc9v3_embedded_grc9v3_state_v1(snapshot),
        )

    def test_component_is_stable_across_native_load(self) -> None:
        model = _model()
        components = [build_lgrc9v3_embedded_grc9v3_state_v1(model.snapshot())]
        with tempfile.TemporaryDirectory() as tmp_dir:
            current = model
            for cycle in range(3):
                path = Path(tmp_dir) / f"lgrc9v3-{cycle}.json"
                current.save(str(path))
                current = LGRC9V3.load(str(path))
                components.append(
                    build_lgrc9v3_embedded_grc9v3_state_v1(current.snapshot())
                )
        self.assertTrue(all(component == components[0] for component in components))

    def test_zero_flux_has_canonical_positive_sign(self) -> None:
        component = build_lgrc9v3_embedded_grc9v3_state_v1(_model().snapshot())
        edge = component["state"]["port_edges"]["1"]
        self.assertLess(
            (edge["node_u"], edge["port_u"]), (edge["node_v"], edge["port_v"])
        )
        self.assertEqual(0.0, edge["flux_uv"])
        self.assertEqual(1.0, math.copysign(1.0, edge["flux_uv"]))

    def test_opposite_raw_orientation_preserves_nonzero_signed_flux(self) -> None:
        left = _model().snapshot()
        right = deepcopy(left)
        left_base = left["caches"]["base_grc9v3_snapshot"]
        right_base = right["caches"]["base_grc9v3_snapshot"]
        left_edge = left_base["dynamics"]["state"]["port_edges"]["1"]
        right_edge = right_base["dynamics"]["state"]["port_edges"]["1"]
        left_edge["flux_uv"] = -0.5
        right_edge["node_u"], right_edge["node_v"] = (
            right_edge["node_v"],
            right_edge["node_u"],
        )
        right_edge["port_u"], right_edge["port_v"] = (
            right_edge["port_v"],
            right_edge["port_u"],
        )
        right_edge["flux_uv"] = 0.5
        right_topology_edge = right_base["topology"]["edges"][0]
        (
            right_topology_edge["endpoint_a"],
            right_topology_edge["endpoint_b"],
        ) = (
            right_topology_edge["endpoint_b"],
            right_topology_edge["endpoint_a"],
        )

        left_component = build_lgrc9v3_embedded_grc9v3_state_v1(left)
        right_component = build_lgrc9v3_embedded_grc9v3_state_v1(right)
        self.assertEqual(left_component, right_component)
        self.assertEqual(
            0.5,
            left_component["state"]["port_edges"]["1"]["flux_uv"],
        )

    def test_included_state_mutation_changes_digest(self) -> None:
        snapshot = _model().snapshot()
        changed = deepcopy(snapshot)
        changed["caches"]["base_grc9v3_snapshot"]["dynamics"]["state"]["nodes"]["0"][
            "coherence"
        ] = 1.5
        self.assertNotEqual(
            digest_lgrc9v3_embedded_grc9v3_state_v1(snapshot),
            digest_lgrc9v3_embedded_grc9v3_state_v1(changed),
        )

    def test_nonzero_flux_mutation_changes_digest(self) -> None:
        snapshot = _model().snapshot()
        changed = deepcopy(snapshot)
        changed["caches"]["base_grc9v3_snapshot"]["dynamics"]["state"]["port_edges"][
            "1"
        ]["flux_uv"] = 0.5
        self.assertNotEqual(
            digest_lgrc9v3_embedded_grc9v3_state_v1(snapshot),
            digest_lgrc9v3_embedded_grc9v3_state_v1(changed),
        )

    def test_non_mapping_input_fails_closed(self) -> None:
        for malformed in (None, [], "not-a-snapshot"):
            with self.subTest(malformed=malformed):
                with self.assertRaises(SnapshotCompatibilityError):
                    build_lgrc9v3_embedded_grc9v3_state_v1(malformed)  # type: ignore[arg-type]

    def test_wrong_family_and_malformed_inputs_fail_closed(self) -> None:
        snapshot = _model().snapshot()
        wrong_family = deepcopy(snapshot)
        wrong_family["metadata"]["model_family"] = "GRC9V3"
        with self.assertRaises(SnapshotCompatibilityError):
            build_lgrc9v3_embedded_grc9v3_state_v1(wrong_family)

        malformed = deepcopy(snapshot)
        del malformed["caches"]["base_grc9v3_snapshot"]
        with self.assertRaises(SnapshotCompatibilityError):
            build_lgrc9v3_embedded_grc9v3_state_v1(malformed)

        invalid_conductance = deepcopy(snapshot)
        invalid_conductance["caches"]["base_grc9v3_snapshot"]["dynamics"]["state"][
            "port_edges"
        ]["1"]["conductance"] = None
        with self.assertRaises(SnapshotCompatibilityError):
            build_lgrc9v3_embedded_grc9v3_state_v1(invalid_conductance)

        missing_edge_id = deepcopy(snapshot)
        del missing_edge_id["caches"]["base_grc9v3_snapshot"]["topology"]["edges"][0][
            "edge_id"
        ]
        with self.assertRaises(SnapshotCompatibilityError):
            build_lgrc9v3_embedded_grc9v3_state_v1(missing_edge_id)


class LGRC9V3CompositeRestorationIdentityTests(unittest.TestCase):
    def test_public_artifact_composes_exact_native_groups(self) -> None:
        model = _active_model()
        snapshot = model.snapshot()
        original = deepcopy(snapshot)

        from_model = lgrc9v3_restoration_identity_v1(model)
        from_snapshot = lgrc9v3_restoration_identity_v1(snapshot)

        self.assertEqual(original, snapshot)
        self.assertEqual(from_model, from_snapshot)
        self.assertEqual(
            LGRC9V3_RESTORATION_IDENTITY_KIND,
            from_snapshot["artifact_kind"],
        )
        self.assertEqual(
            LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION,
            from_snapshot["artifact_schema_version"],
        )
        self.assertEqual("LGRC9V3", from_snapshot["model_family"])
        self.assertEqual("pygrc.snapshot", from_snapshot["source_snapshot_schema"])
        self.assertEqual(1, from_snapshot["source_snapshot_version"])
        self.assertIn(
            "embedded_grc9v3_state",
            from_snapshot["included_state_groups"],
        )
        self.assertIn(
            "exact_lgrc9v3_runtime_artifact",
            from_snapshot["included_state_groups"],
        )
        self.assertIn(
            "raw_full_snapshot_digest",
            from_snapshot["excluded_representation_fields"],
        )
        self.assertEqual(
            snapshot["dynamics"]["lgrc9v3_runtime"],
            from_snapshot["lgrc9v3_runtime_artifact"],
        )
        self.assertEqual(snapshot["events"], from_snapshot["events"])
        self.assertEqual(snapshot["observables"], from_snapshot["observables"])
        artifact_keys = _mapping_keys(from_snapshot)
        self.assertNotIn("raw_snapshot_digest", artifact_keys)
        self.assertNotIn("raw_full_snapshot_digest", artifact_keys)
        self.assertNotIn("raw_snapshot", artifact_keys)

    def test_public_artifact_and_digest_are_deterministic(self) -> None:
        snapshot = _active_model().snapshot()
        first = lgrc9v3_restoration_identity_v1(snapshot)
        second = lgrc9v3_restoration_identity_v1(snapshot)
        self.assertEqual(first, second)
        self.assertEqual(
            digest_canonical_data(first),
            digest_lgrc9v3_restoration_identity_v1(snapshot),
        )

    def test_public_identity_is_stable_across_native_load(self) -> None:
        model = _active_model()
        before = lgrc9v3_restoration_identity_v1(model)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "lgrc9v3-composite.json"
            model.save(str(path))
            loaded = LGRC9V3.load(str(path))
        self.assertEqual(before, lgrc9v3_restoration_identity_v1(loaded))

    def test_runtime_event_and_observable_mutations_change_digest(self) -> None:
        snapshot = _active_model().snapshot()
        original_digest = digest_lgrc9v3_restoration_identity_v1(snapshot)

        runtime_changed = deepcopy(snapshot)
        runtime_changed["dynamics"]["lgrc9v3_runtime"]["scheduler_event_index"] += 1
        self.assertNotEqual(
            original_digest,
            digest_lgrc9v3_restoration_identity_v1(runtime_changed),
        )

        event_changed = deepcopy(snapshot)
        event_changed["events"][0]["payload"]["identity_test_marker"] = True
        self.assertNotEqual(
            original_digest,
            digest_lgrc9v3_restoration_identity_v1(event_changed),
        )

        observable_changed = deepcopy(snapshot)
        observable_key = next(iter(observable_changed["observables"]))
        observable_changed["observables"][observable_key] += 1.0
        self.assertNotEqual(
            original_digest,
            digest_lgrc9v3_restoration_identity_v1(observable_changed),
        )

    def test_public_identity_rejects_unsupported_or_malformed_sources(self) -> None:
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(object())  # type: ignore[arg-type]

        snapshot = _active_model().snapshot()
        missing_runtime = deepcopy(snapshot)
        del missing_runtime["dynamics"]["lgrc9v3_runtime"]
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(missing_runtime)

        malformed_events = deepcopy(snapshot)
        malformed_events["events"] = {}
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(malformed_events)

        missing_events = deepcopy(snapshot)
        del missing_events["events"]
        with self.assertRaisesRegex(SnapshotCompatibilityError, "events are required"):
            lgrc9v3_restoration_identity_v1(missing_events)

        malformed_observables = deepcopy(snapshot)
        malformed_observables["observables"] = []
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(malformed_observables)


if __name__ == "__main__":
    unittest.main()
