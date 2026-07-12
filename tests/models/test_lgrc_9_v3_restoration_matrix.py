"""Iteration 93 replay, sensitivity, and compatibility matrix."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
from typing import Any, Callable, cast
import unittest

from pygrc.core import (
    SnapshotCompatibilityError,
    digest_canonical_data,
    digest_snapshot,
    save_snapshot,
)
from pygrc.models import (
    GRC9V3,
    LGRC9V3,
    digest_lgrc9v3_restoration_identity_v1,
    lgrc9v3_restoration_identity_v1,
)

from tests.models.test_lgrc_9_v3_restoration import _active_model, _model, _state


_OPTIONAL_LEGACY_RUNTIME_FIELDS = (
    "causal_pulse_substrate_surface_log",
    "causal_pulse_substrate_surface_lineage_log",
    "child_basin_state_log",
    "post_refinement_flow_window_log",
    "merge_leakage_control_matrix_log",
    "multi_basin_replay_validation_log",
    "native_route_candidate_log",
    "native_route_candidate_set_log",
    "native_route_arbitration_log",
)


JsonObject = dict[str, Any]


def _base_snapshot(snapshot: JsonObject) -> JsonObject:
    return cast(JsonObject, snapshot["caches"]["base_grc9v3_snapshot"])


def _base_state(snapshot: JsonObject) -> JsonObject:
    return cast(JsonObject, _base_snapshot(snapshot)["dynamics"]["state"])


def _runtime(snapshot: JsonObject) -> JsonObject:
    return cast(JsonObject, snapshot["dynamics"]["lgrc9v3_runtime"])


def _reverse_mapping(mapping: JsonObject) -> JsonObject:
    return dict(reversed(tuple(mapping.items())))


class LGRC9V3RestorationReplayMatrixTests(unittest.TestCase):
    def test_composite_fixed_point_and_raw_digest_cycle_across_three_loads(
        self,
    ) -> None:
        current = _active_model()
        snapshots = [current.snapshot()]
        identities = [lgrc9v3_restoration_identity_v1(snapshots[0])]
        with tempfile.TemporaryDirectory() as tmp_dir:
            for cycle in range(3):
                path = Path(tmp_dir) / f"cycle-{cycle}.json"
                current.save(str(path))
                current = LGRC9V3.load(str(path))
                snapshots.append(current.snapshot())
                identities.append(lgrc9v3_restoration_identity_v1(snapshots[-1]))

        self.assertTrue(all(identity == identities[0] for identity in identities))
        raw_digests = [digest_snapshot(snapshot) for snapshot in snapshots]
        self.assertGreater(len(set(raw_digests)), 1)
        self.assertEqual(raw_digests[1], raw_digests[3])
        self.assertNotEqual(raw_digests[1], raw_digests[2])

    def test_equal_input_continuation_twins_remain_equivalent(self) -> None:
        original = _active_model()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "continuation.json"
            original.save(str(path))
            restored = LGRC9V3.load(str(path))

        self.assertEqual(
            lgrc9v3_restoration_identity_v1(original),
            lgrc9v3_restoration_identity_v1(restored),
        )
        original_result = original.step()
        restored_result = restored.step()
        self.assertEqual(original_result, restored_result)
        self.assertEqual(
            lgrc9v3_restoration_identity_v1(original),
            lgrc9v3_restoration_identity_v1(restored),
        )

    def test_current_runtime_events_and_observables_remain_exact(self) -> None:
        model = _active_model()
        before = model.snapshot()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "exact-groups.json"
            model.save(str(path))
            restored = LGRC9V3.load(str(path))
        after = restored.snapshot()
        self.assertEqual(
            before["dynamics"]["lgrc9v3_runtime"],
            after["dynamics"]["lgrc9v3_runtime"],
        )
        self.assertEqual(before["events"], after["events"])
        self.assertEqual(before["observables"], after["observables"])


class LGRC9V3RestorationSensitivityMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot: JsonObject = _active_model().snapshot()
        self.original_digest = digest_lgrc9v3_restoration_identity_v1(self.snapshot)

    def assertMutationChangesIdentity(self, changed: JsonObject) -> None:
        self.assertNotEqual(
            self.original_digest,
            digest_lgrc9v3_restoration_identity_v1(changed),
        )

    def test_embedded_topology_and_allocation_sensitivity(self) -> None:
        topology_changed = deepcopy(self.snapshot)
        _base_snapshot(topology_changed)["topology"]["nodes"][0]["payload"]["label"] = (
            "changed-topology-label"
        )
        self.assertMutationChangesIdentity(topology_changed)

        allocation_changed = deepcopy(self.snapshot)
        _base_snapshot(allocation_changed)["metadata"]["next_node_id"] += 1
        self.assertMutationChangesIdentity(allocation_changed)

    def test_embedded_node_basin_and_edge_label_sensitivity(self) -> None:
        node_changed = deepcopy(self.snapshot)
        _base_state(node_changed)["nodes"]["0"]["basin_id"] = "changed-basin"
        self.assertMutationChangesIdentity(node_changed)

        edge_label_changed = deepcopy(self.snapshot)
        _base_state(edge_label_changed)["base_conductance"]["1"] = 0.5
        self.assertMutationChangesIdentity(edge_label_changed)

        mode_changed = deepcopy(self.snapshot)
        _base_state(mode_changed)["edge_label_computation_mode"]["geometric_length"] = (
            "changed-mode"
        )
        self.assertMutationChangesIdentity(mode_changed)

    def test_potential_sink_basin_budget_and_remainder_sensitivity(self) -> None:
        mutations: tuple[tuple[str, Callable[[JsonObject], None]], ...] = (
            ("potential", lambda state: state["potential"].__setitem__("0", 0.5)),
            ("sink_set", lambda state: state.__setitem__("sink_set", [2])),
            ("basins", lambda state: state["basins"].__setitem__("0", [0])),
            ("budget_target", lambda state: state.__setitem__("budget_target", 3.5)),
            ("remainder", lambda state: state.__setitem__("remainder", 0.125)),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                changed = deepcopy(self.snapshot)
                mutate(_base_state(changed))
                self.assertMutationChangesIdentity(changed)

    def test_rng_and_hidden_cache_sensitivity(self) -> None:
        rng_changed = deepcopy(self.snapshot)
        _base_state(rng_changed)["rng_state"] = {
            "engine": "identity_matrix_rng",
            "state": [1, 2, 3],
        }
        self.assertMutationChangesIdentity(rng_changed)

        cache_changed = deepcopy(self.snapshot)
        _base_state(cache_changed)["cached_quantities"]["evidence_surface"]["value"] = (
            0.75
        )
        self.assertMutationChangesIdentity(cache_changed)

    def test_state_owned_event_and_observable_sensitivity(self) -> None:
        event_changed = deepcopy(self.snapshot)
        _base_state(event_changed)["event_log"] = [
            {
                "kind": "identity_matrix_event",
                "step_index": 3,
                "payload": {"value": 1},
                "source_family": "GRC9V3",
            }
        ]
        self.assertMutationChangesIdentity(event_changed)

        observable_changed = deepcopy(self.snapshot)
        _base_state(observable_changed)["observables"]["fixture_observable"] = 4.0
        self.assertMutationChangesIdentity(observable_changed)

    def test_lgrc_queue_clock_ledger_route_topology_and_producer_sensitivity(
        self,
    ) -> None:
        queue_changed = deepcopy(self.snapshot)
        _runtime(queue_changed)["packet_ledger"]["event_queue_records"][0][
            "event_time_key"
        ] = 2.5
        self.assertMutationChangesIdentity(queue_changed)

        clock_changed = deepcopy(self.snapshot)
        _runtime(clock_changed)["scheduler_event_index"] = 2
        self.assertMutationChangesIdentity(clock_changed)

        ledger_changed = deepcopy(self.snapshot)
        _runtime(ledger_changed)["packet_ledger"]["budget_error"] = 0.01
        self.assertMutationChangesIdentity(ledger_changed)

        route_changed = deepcopy(self.snapshot)
        _runtime(route_changed)["causal_flux_routes"] = {
            "0": [{"target_node_id": 2, "edge_id": 1, "amount": 0.1}]
        }
        self.assertMutationChangesIdentity(route_changed)

        topology_history_changed = deepcopy(self.snapshot)
        _runtime(topology_history_changed)["topology_event_log"] = [
            {
                "kind": "identity_matrix_topology_event",
                "step_index": 1,
                "payload": {"topology_mutated": False},
                "source_family": "LGRC9V3",
            }
        ]
        self.assertMutationChangesIdentity(topology_history_changed)

        producer_changed = deepcopy(self.snapshot)
        _runtime(producer_changed)["cached_quantities"][
            "identity_matrix_producer_record"
        ] = {"policy": "bounded-test", "enabled": False}
        self.assertMutationChangesIdentity(producer_changed)

    def test_source_current_surface_mutation_changes_identity(self) -> None:
        model = LGRC9V3.from_state(
            _state(),
            {
                "dt": 1.0,
                "causal_modes": {
                    "causal_layer_mode": "packetized_fixed_topology",
                    "lgrc_runtime_level": "lgrc2",
                    "lapse_policy": "unit",
                    "edge_delay_policy": "constant_delay",
                    "event_time_policy": "explicit_event_time_key",
                    "proper_time_accumulation_policy": "local_event_frontier",
                    "causal_pulse_substrate_surface_enabled": True,
                    "causal_pulse_substrate_surface_policy": (
                        "emit_committed_packet_contact_rows"
                    ),
                    "causal_pulse_substrate_surface_validated": True,
                },
            },
        )
        model.schedule_packet_departure(
            source_node_id=2,
            target_node_id=0,
            edge_id=1,
            amount=0.25,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        model.step()
        before = digest_lgrc9v3_restoration_identity_v1(model)
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=[2],
            rear_node_ids=[0],
            reference_delta=0.0,
            feedback_threshold=0.0,
            expected_next_route_id="identity-matrix-route",
            expected_next_channel_id="identity-matrix-channel",
        )
        self.assertNotEqual(
            before,
            digest_lgrc9v3_restoration_identity_v1(model),
        )


class LGRC9V3RestorationNormalizationMatrixTests(unittest.TestCase):
    def test_endpoint_and_nonzero_signed_flux_reversal_is_invariant(self) -> None:
        left = _model().snapshot()
        right = deepcopy(left)
        left_base = _base_snapshot(left)
        right_base = _base_snapshot(right)
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
        topology_edge = right_base["topology"]["edges"][0]
        topology_edge["endpoint_a"], topology_edge["endpoint_b"] = (
            topology_edge["endpoint_b"],
            topology_edge["endpoint_a"],
        )
        self.assertEqual(
            lgrc9v3_restoration_identity_v1(left),
            lgrc9v3_restoration_identity_v1(right),
        )

    def test_deterministic_default_materialization_is_invariant(self) -> None:
        baseline = _model().snapshot()
        baseline_identity = lgrc9v3_restoration_identity_v1(baseline)

        params_absent = deepcopy(baseline)
        _base_state(params_absent)["params_identity"] = None
        self.assertEqual(
            baseline_identity,
            lgrc9v3_restoration_identity_v1(params_absent),
        )

        rng_absent = deepcopy(baseline)
        _base_state(rng_absent)["rng_state"] = None
        _base_snapshot(rng_absent)["metadata"].pop("rng_state", None)
        self.assertEqual(
            baseline_identity,
            lgrc9v3_restoration_identity_v1(rng_absent),
        )

        budget_source_materialized = deepcopy(baseline)
        _base_state(budget_source_materialized)["cached_quantities"][
            "budget_target_source"
        ] = "explicit_state"
        self.assertEqual(
            baseline_identity,
            lgrc9v3_restoration_identity_v1(budget_source_materialized),
        )

    def test_mapping_and_set_order_are_invariant(self) -> None:
        baseline = _active_model().snapshot()
        reordered = deepcopy(baseline)
        reordered["metadata"] = _reverse_mapping(reordered["metadata"])
        state = _base_state(reordered)
        state["nodes"] = _reverse_mapping(state["nodes"])
        state["basins"]["0"] = list(reversed(state["basins"]["0"]))
        _runtime(reordered)["cached_quantities"] = _reverse_mapping(
            _runtime(reordered)["cached_quantities"]
        )
        self.assertEqual(
            lgrc9v3_restoration_identity_v1(baseline),
            lgrc9v3_restoration_identity_v1(reordered),
        )

    def test_signed_zero_outside_port_flux_remains_exact(self) -> None:
        positive = _model().snapshot()
        negative = deepcopy(positive)
        _base_state(positive)["potential"]["0"] = 0.0
        _base_state(negative)["potential"]["0"] = -0.0
        self.assertNotEqual(
            digest_lgrc9v3_restoration_identity_v1(positive),
            digest_lgrc9v3_restoration_identity_v1(negative),
        )

    def test_raw_duplicate_base_event_and_observable_views_normalize_away(
        self,
    ) -> None:
        baseline = _model().snapshot()
        duplicate_changed = deepcopy(baseline)
        _base_snapshot(duplicate_changed)["events"] = [
            {
                "kind": "ignored-duplicate-view",
                "step_index": 99,
                "payload": {},
                "source_family": "GRC9V3",
            }
        ]
        _base_snapshot(duplicate_changed)["observables"] = {"ignored_duplicate": 99.0}
        self.assertEqual(
            lgrc9v3_restoration_identity_v1(baseline),
            lgrc9v3_restoration_identity_v1(duplicate_changed),
        )


class LGRC9V3RestorationCompatibilityAndControlTests(unittest.TestCase):
    def test_legacy_supported_grc9v3_snapshot_remains_loadable(self) -> None:
        base_snapshot = deepcopy(_base_snapshot(_model().snapshot()))
        state = base_snapshot["dynamics"]["state"]
        for optional in ("choice_registry", "collapse_registry", "coarse_cache"):
            state.pop(optional, None)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "legacy-grc9v3.json"
            save_snapshot(path, base_snapshot)
            restored = GRC9V3.load(str(path))
        self.assertEqual("GRC9V3", restored.snapshot()["metadata"]["model_family"])

    def test_legacy_supported_lgrc9v3_snapshot_reaches_same_identity(self) -> None:
        current = _active_model().snapshot()
        legacy = deepcopy(current)
        runtime = _runtime(legacy)
        for field in _OPTIONAL_LEGACY_RUNTIME_FIELDS:
            runtime.pop(field, None)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "legacy-lgrc9v3.json"
            save_snapshot(path, legacy)
            restored = LGRC9V3.load(str(path))
        self.assertEqual(
            lgrc9v3_restoration_identity_v1(legacy),
            lgrc9v3_restoration_identity_v1(restored),
        )

    def test_missing_wrong_family_and_malformed_runtime_fail_closed(self) -> None:
        snapshot = _active_model().snapshot()

        missing = deepcopy(snapshot)
        del missing["caches"]["base_grc9v3_snapshot"]
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(missing)

        wrong_family = deepcopy(snapshot)
        wrong_family["metadata"]["model_family"] = "GRC9V3"
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(wrong_family)

        malformed_runtime = deepcopy(snapshot)
        _runtime(malformed_runtime)["artifact_kind"] = "not-lgrc9v3-runtime"
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(malformed_runtime)

    def test_relabel_controls_fail_closed(self) -> None:
        raw_digest = digest_snapshot(_active_model().snapshot())
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(raw_digest)  # type: ignore[arg-type]

        experiment_projection = {
            "artifact_kind": "rcae_restoration_projection",
            "projection": {},
        }
        with self.assertRaises(SnapshotCompatibilityError):
            lgrc9v3_restoration_identity_v1(experiment_projection)

        identity = lgrc9v3_restoration_identity_v1(_active_model())
        forbidden_claim_keys = {
            "unrestricted_behavioral_equivalence",
            "rc_identity_supported",
            "selfhood_supported",
            "agency_supported",
            "native_shared_medium_supported",
        }
        self.assertTrue(forbidden_claim_keys.isdisjoint(identity))
        self.assertEqual(
            digest_canonical_data(identity),
            digest_lgrc9v3_restoration_identity_v1(_active_model()),
        )
