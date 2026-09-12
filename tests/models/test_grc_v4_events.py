"""P9-7.2b executed crossings; literal resource/history and archive pressure."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4, GRCV4MappedTopologyEventRequest, GRCV4RepresentationRequest
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_event_codec import representation_identity, EVENT_LAYOUT, REPRESENTATION_LAYOUT, POLICY_ID
from pygrc.models.grc_v4_events import reconstruction_history_policy, coordinate_reference
from pygrc.models.grc_v4_geometry import GRCV4Graph, GraphCoordinateAction, OrientedEdge
from pygrc.models.grc_v4_lifecycle import _state_inputs
from tests.models.test_grc_v4_migration import fixture, changed_reference, migration
from tests.models.test_grc_v4_initializer import target as initializer_target, oracle
from tests.models.test_grc_v4_lifecycle import request as step_request

EVIDENCE = {}


def capture(name, inputs, owner, declared, result):
    state = _state_inputs(owner._operation.reference, owner.state.lifecycle)
    def endpoint(value):
        authoritative = lambda s: dict(C=list(s.C), W_A=None if s.W_A is None else list(s.W_A),
                                       Z_4=None if s.Z_4 is None else list(s.Z_4))
        return dict(scientific_state_id=value.scientific_state_id, reset_id=value.reset_id,
                    reference_id=value.geometry.reference.identity,
                    current=authoritative(value.current), reset=authoritative(value.reset),
                    Q_target=value.Q_target, step_index=value.step_index, time=value.time)
    EVIDENCE[name] = dict(source=endpoint(inputs), target=endpoint(state), request=declared.to_payload(),
        primary=result.emitted_receipts[0].to_payload(), commit_id=result.commit_id,
        emitted_receipt_ids=[r.receipt_id for r in result.emitted_receipts])


def event(owner, target, matrix=(1, 0, 0, 1), increment=(0, 0), operation="event"):
    before = _state_inputs(owner._operation.reference, owner.state.lifecycle)
    return GRCV4MappedTopologyEventRequest.from_payload(dict(
        schema_version="grcv4-mapped-topology-event-request-v1", operation_id=operation,
        source_state_digest=before.scientific_state_id, source_graph_digest=before.geometry.reference.graph.graph_digest,
        target_graph=target.graph.to_payload(), target_profile_id=target.profile.complete_profile_id,
        resource_transform=dict(schema_version="grcv4-resource-event-transform-v1", policy_id="caller_affine_resource_transport_v1", source_vertex_ids=list(before.geometry.reference.graph.live_node_ids),
            target_vertex_ids=list(target.graph.live_node_ids), row_major_coefficients=list(matrix), target_increment=list(increment)),
        history_policy=reconstruction_history_policy(before, target).to_payload(), metadata={}))


def representation(owner, target, action, operation="coordinate"):
    source = action.source
    vertex_rows = [None] * len(source.live_node_ids)
    edge_rows = [None] * len(source.live_edge_ids)
    for i, a in enumerate(action.vertex_permutation):
        vertex_rows[a] = dict(source_vertex_id=source.live_node_ids[a], target_vertex_id=action.target.live_node_ids[i])
    for i, a in enumerate(action.edge_permutation):
        edge_rows[a] = dict(source_edge_id=source.live_edge_ids[a], target_edge_id=action.target.live_edge_ids[i], orientation=action.edge_signs[i])
    payload = dict(schema_version="grcv4-coordinate-map-v1", policy_id=POLICY_ID, source_graph_digest=source.graph_digest,
        target_graph_digest=target.graph.graph_digest, vertex_map=vertex_rows, edge_map=edge_rows)
    return GRCV4RepresentationRequest.from_payload(dict(schema_version="grcv4-representation-transport-request-v1",
        operation_id=operation, source_state_digest=owner.state.lifecycle.scientific_state_digest,
        source_graph_digest=source.graph_digest, target_graph=target.graph.to_payload(), target_profile_id=target.profile.complete_profile_id,
        correspondence=dict(correspondence_id=representation_identity("correspondence_payload", payload), payload=payload), metadata={}))


def reversed_target(inputs, backend):
    source = inputs.geometry.reference
    graph = GRCV4Graph(("renamed-v", "renamed-u"), (OrientedEdge("renamed-e", "renamed-v", "renamed-u"),))
    action = GraphCoordinateAction(source.graph, graph, (1, 0), (0,), (-1,))
    ref, other = coordinate_reference(source, action, backend)
    return ref, other, action


class EventRuntimeTests(unittest.TestCase):
    def test_legacy_event_initializer_migration_and_new_archive_tampering(self):
        from tests.models.test_grc_v4_lifecycle import event_request
        from tests.models.test_grc_v4_migration import rehash_receipt_chain
        from pygrc.models.grc_v4_lifecycle import GRCV4Operation
        inputs, _ = fixture("C_OS")
        target, backend = initializer_target("A_OS")
        owner = GRCV4(inputs, targets=(target,), target_differential_references=(backend,))
        legacy = owner.apply_topology_event(event_request(owner._operation, inputs.geometry.reference, [1, 0, 0, 1], [0, 0]))
        self.assertTrue(legacy.committed, legacy.failure)
        self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
        declared = event(owner, target, operation="new-A-event")
        event_inputs = _state_inputs(owner._operation.reference, owner.state.lifecycle)
        result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        snapshot = owner.snapshot()
        self.assertEqual(owner.duplicate().snapshot(), snapshot)
        for mutation in ("pair", "legacy_version", "alias"):
            bad = deepcopy(snapshot)
            if mutation == "pair":
                bad["transition_records"][-1]["initializer_pair"] = None
            elif mutation == "legacy_version":
                primary = bad["receipt_ledger"][-4]["identity_payload"]
                primary["schema_version"] = "grcv4-topology-event-receipt-v1"
                primary.pop("initializer_pair_id")
                bad["transition_records"][-1]["initializer_pair"] = None
                rehash_receipt_chain(bad)
            else:
                bad["transition_records"][-1]["request"]["history_policy"]["candidate"]["policy_id"] = "identity_candidate_history_v1"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): GRCV4Operation.from_state(bad)
        capture("legacy_migration_event", event_inputs, owner, declared, result)

    def test_representation_signed_parallel_loop_carrier_and_rehashed_charge_tamper(self):
        from tests.models.test_grc_v4_candidate_c import current_fixture
        from tests.models.test_grc_v4_pc import configure
        from tests.models.test_grc_v4_migration import rehash_receipt_chain
        from pygrc.models.grc_v4_lifecycle import GRCV4Operation
        graph = GRCV4Graph(("a", "b"), (OrientedEdge("e", "a", "b"), OrientedEdge("f", "a", "b"), OrientedEdge("loop", "a", "a")))
        inputs = current_fixture(graph=graph, resource=(2, 2), weights={"e": 1, "f": 1, "loop": 1},
                                 changes={"candidate": dict(Lambda_C=.5, eta_C=.125, kappa_M_C=.125, tau_C=.125, chi_C=.125, zeta_C=.125)})
        z = (.125, .03125, 0, .03125, -.0625, 0, 0, 0, .125)
        inputs = configure(inputs, z=z, reset_z=tuple(-x if x else 0.0 for x in z))
        graph2 = GRCV4Graph(("y", "x"), (OrientedEdge("l2", "x", "x"), OrientedEdge("f2", "y", "x"), OrientedEdge("e2", "x", "y")))
        action = GraphCoordinateAction(graph, graph2, (1, 0), (2, 1, 0), (-1, -1, 1))
        target, _ = coordinate_reference(inputs.geometry.reference, action)
        owner = GRCV4(inputs, targets=(target,))
        declared = representation(owner, target, action)
        result = owner.transport_representation(declared)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.lifecycle.current.Z_4,
                         (.125, 0, 0, 0, -.0625, -.03125, 0, -.03125, .125))
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        import subprocess, sys
        replay = subprocess.run([sys.executable, "-c",
            "import sys; from pygrc.models.grc_v4_codec import decode_canonical_json, canonical_json_bytes; "
            "from pygrc.models.grc_v4_lifecycle import GRCV4Operation; "
            "sys.stdout.buffer.write(canonical_json_bytes(GRCV4Operation.from_state(decode_canonical_json(sys.stdin.buffer.read())).snapshot()))"],
            input=canonical_json_bytes(owner.snapshot()), capture_output=True, check=True)
        self.assertEqual(replay.stdout, canonical_json_bytes(owner.snapshot()))
        bad = owner.snapshot()
        bad["receipt_ledger"][0]["identity_payload"]["charge"]["reset"]["target"]["admitted_charge"] = 3
        rehash_receipt_chain(bad)
        with self.assertRaises(ValueError): GRCV4Operation.from_state(bad)
        capture("signed_parallel_loop", inputs, owner, declared, result)
    def test_identity_transport_is_not_identity_reconstruction_and_mixed_replay(self):
        inputs, backend = fixture("A_PC")
        target, _ = initializer_target("A_PC")
        from pygrc.models.grc_v4_lifecycle import _fresh_geometry
        inputs = _fresh_geometry(replace(inputs, geometry=target.geometry()))
        owner = GRCV4(inputs, differential_reference=backend)
        # A preserving migration supplies a four-receipt predecessor.
        self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
        action = GraphCoordinateAction(target.graph, target.graph, (0, 1), (0,), (1,))
        preserved = owner.transport_representation(representation(owner, target, action))
        self.assertTrue(preserved.committed, preserved.failure)
        self.assertEqual(owner.state.lifecycle.current.W_A, inputs.current.W_A)
        self.assertEqual(owner.state.lifecycle.current.Z_4, inputs.current.Z_4)
        # Positive evolution must not later be mistaken for old initializer output.
        self.assertTrue(owner.step_v4_input(step_request(2**-12, "evolve")).committed)
        rebuilt = owner.reconstruct_topology_event(event(owner, target, operation="rebuild"))
        self.assertTrue(rebuilt.committed, rebuilt.failure)
        self.assertEqual(tuple(rebuilt.emitted_receipts[0].identity_payload["core"]["information_losses"]),
                         ("candidate_history_loss", "carrier_history_loss"))
        self.assertEqual(owner.state.lifecycle.current.Z_4, (0.0,))
        self.assertTrue(owner.step_v4_input(step_request(2**-12, "after-rebuild")).committed)
        clone = owner.duplicate()
        self.assertEqual(clone.snapshot(), owner.snapshot())
        clone.reset()
        self.assertEqual(clone.state.lifecycle.current, clone.state.lifecycle.reset.authoritative)
        self.assertNotEqual(clone.snapshot(), owner.snapshot())

    def test_declaration_and_late_publication_failures_are_atomic(self):
        from pygrc.models import grc_v4_lifecycle as lifecycle
        inputs, _ = fixture("C_OS")
        target, _, action = reversed_target(inputs, None)
        incompatible = changed_reference(target, "candidate", eta_C=0.375)
        owner = GRCV4(inputs, targets=(target, incompatible))
        before = owner.snapshot()
        bad = representation(owner, incompatible, action)
        result = owner.transport_representation(bad)
        self.assertFalse(result.committed)
        self.assertEqual(owner.snapshot(), before)
        declared = representation(owner, target, action)
        with patch.object(lifecycle, "_validate_publication", side_effect=RuntimeError("late failure")):
            with self.assertRaisesRegex(RuntimeError, "late failure"):
                owner.transport_representation(declared)
        self.assertEqual(owner.snapshot(), before)
        invalid = event(owner, target, matrix=(1, 1, 0, 1))
        self.assertFalse(owner.reconstruct_topology_event(invalid).committed)
        self.assertEqual(owner.snapshot(), before)
        with self.assertRaises(TypeError): owner.transport_representation(declared.to_payload())
        overflow, backend = initializer_target("A_OS", alpha=-1e308)
        other = GRCV4(inputs, targets=(overflow,), target_differential_references=(backend,))
        original = other.snapshot()
        result = other.reconstruct_topology_event(event(other, overflow))
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, "target_construction")
        self.assertEqual(other.snapshot(), original)
        # Legacy admission must not produce an unrestorable new-layout archive.
        unusual = changed_reference(inputs.geometry.reference, "lifecycle", history_policy_id="unregistered_legacy_alias")
        old_inputs = replace(inputs, geometry=unusual.geometry())
        shifted, _, move = reversed_target(old_inputs, None)
        old_owner = GRCV4(old_inputs, targets=(shifted,))
        payload = event(old_owner, unusual).to_payload()
        payload["history_policy"]["candidate"]["policy_id"] = "unregistered_legacy_alias"
        self.assertTrue(old_owner.apply_topology_event(GRCV4MappedTopologyEventRequest.from_payload(payload)).committed)
        original = old_owner.snapshot()
        held = old_owner.transport_representation(representation(old_owner, shifted, move))
        self.assertFalse(held.committed)
        self.assertEqual(old_owner.snapshot(), original)

    def test_charge_order_witness_and_reset_only_rejection(self):
        from tests.models.test_grc_v4_candidate_c import current_fixture
        from pygrc.models.grc_v4_lifecycle import _fresh_geometry
        graph = GRCV4Graph(("a", "b", "c"), (OrientedEdge("e", "a", "b"),))
        inputs = current_fixture(graph=graph, resource=(1, 2**-53, 2**-53), weights={"e": 1},
                                 changes={"charge": dict(absolute_tolerance=2**-52, relative_tolerance=0)})
        inputs = replace(inputs, Q_target=1)
        graph2 = GRCV4Graph(("b", "c", "a"), graph.oriented_edges)
        action = GraphCoordinateAction(graph, graph2, (1, 2, 0), (0,), (1,))
        target, _ = coordinate_reference(inputs.geometry.reference, action)
        owner = GRCV4(inputs, targets=(target,))
        result = owner.transport_representation(representation(owner, target, action))
        self.assertTrue(result.committed, result.failure)
        receipt = result.emitted_receipts[0].identity_payload
        self.assertEqual(receipt["core"]["actual_charge_delta"], 0)
        self.assertEqual(receipt["charge"]["current"]["target"]["admitted_charge"] -
                         receipt["charge"]["current"]["source"]["admitted_charge"], 2**-52)
        strict = changed_reference(inputs.geometry.reference, "charge", absolute_tolerance=0, relative_tolerance=0)
        inputs = _fresh_geometry(replace(inputs, geometry=strict.geometry(),
            current=replace(inputs.current, C=(0, 1, 0)), reset=replace(inputs.reset, C=(1, 2**-53, 2**-53))))
        target, _ = coordinate_reference(strict, action)
        owner = GRCV4(inputs, targets=(target,))
        before = owner.snapshot()
        result = owner.transport_representation(representation(owner, target, action))
        self.assertFalse(result.committed)
        self.assertEqual(owner.snapshot(), before)

    def test_topology_edge_count_change_affine_increment_and_carrier_size(self):
        from tests.models.test_grc_v4_candidate_c import current_fixture
        inputs, backend = fixture("A_PC")
        graph = GRCV4Graph(("x", "y", "z"),
            (OrientedEdge("f", "x", "y"), OrientedEdge("g", "y", "z")))
        raw = current_fixture(graph=graph, resource=(1, 2, 1), weights={"f": 1, "g": 1},
                              changes={"candidate": dict(Lambda_C=.5, eta_C=.125, kappa_M_C=.125, tau_C=.125, chi_C=.125, zeta_C=.125)})
        from tests.models.test_grc_v4_pc import configure
        target = configure(raw).geometry.reference
        owner = GRCV4(inputs, targets=(target,), differential_reference=backend)
        matrix, increment = (1, 0, 0, .5, 0, .5), (.25, 0, 0)
        result = owner.reconstruct_topology_event(event(owner, target, matrix, increment))
        self.assertTrue(result.committed, result.failure)
        for old, new in ((inputs.current, owner.state.lifecycle.current), (inputs.reset, owner.state.lifecycle.reset.authoritative)):
            expected = tuple(float(Fraction(increment[i]) + sum((Fraction(matrix[2*i+j])*Fraction(old.C[j]) for j in range(2)), Fraction())) for i in range(3))
            self.assertEqual(new.C, expected)
            self.assertIsNone(new.W_A); self.assertEqual(new.Z_4, (0.0,) * 4)
        self.assertEqual(owner.state.lifecycle.Q_target, inputs.Q_target + .25)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_c_reconstruction_and_representation_smoke(self):
        inputs, _ = fixture("C_OS")
        target, _, action = reversed_target(inputs, None)
        owner = GRCV4(inputs, targets=(target,))
        result = owner.reconstruct_topology_event(event(owner, target, (0, 1, 1, 0)))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.lifecycle.current.C, inputs.current.C[::-1])
        self.assertEqual(owner.snapshot()["implementation_layout_id"], EVENT_LAYOUT)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        owner = GRCV4(inputs, targets=(target,))
        result = owner.transport_representation(representation(owner, target, action))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertEqual(owner.snapshot()["implementation_layout_id"], REPRESENTATION_LAYOUT)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        self.assertTrue(owner.step_v4_input(step_request(0, "after-coordinate")).committed)
        self.assertEqual(owner.snapshot()["receipt_ledger"][1]["identity_payload"]["core"]["parent_receipt_ids"],
                         [result.emitted_receipts[0].receipt_id])
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current, owner.state.lifecycle.reset.authoritative)

    def test_all_ten_reconstruction_targets_and_independent_roles(self):
        for candidate in ("C", "A"):
            for realization in ("OS", "CI", "RG2b", "PC", "CI_PC"):
                family = candidate + "_" + realization
                with self.subTest(target=family):
                    source_persistent = realization not in ("CI", "PC")
                    inputs, source_backend = fixture(("A" if candidate == "C" else "C") + ("_PC" if source_persistent else "_OS"))
                    if candidate == "A":
                        target, backend = initializer_target(family)
                    else:
                        other, backend = fixture(family); target = other.geometry.reference
                    owner = GRCV4(inputs, targets=(target,), differential_reference=source_backend,
                                  target_differential_references=() if backend is None else (backend,))
                    declared = event(owner, target)
                    result = owner.reconstruct_topology_event(declared)
                    self.assertTrue(result.committed, result.failure)
                    state = owner.state.lifecycle
                    self.assertEqual(state.current.C, inputs.current.C)
                    self.assertEqual(state.reset.authoritative.C, inputs.reset.C)
                    self.assertEqual(state.Q_target, inputs.Q_target)
                    for role, old, new in (("current", inputs.current, state.current),
                                           ("reset", inputs.reset, state.reset.authoritative)):
                        if candidate == "A":
                            self.assertEqual(new.W_A, tuple(oracle(target, backend, old.C)[1]))
                        else:
                            self.assertIsNone(new.W_A)
                        self.assertEqual(new.Z_4, (0.0,) if realization in ("PC", "CI_PC") else None)
                    history = result.emitted_receipts[0].identity_payload["history"]
                    self.assertEqual(history["candidate"]["information_loss"], "candidate_history_loss" if candidate == "C" else "none")
                    self.assertEqual(history["carrier"]["information_loss"], "carrier_history_loss" if source_persistent else "none")
                    capture("reconstruction_" + family, inputs, owner, declared, result)

    def test_a_source_loss_to_each_a_target_and_discarded_history_independence(self):
        for realization in ("OS", "CI", "RG2b", "PC", "CI_PC"):
            with self.subTest(target=realization):
                inputs, backend = fixture("A_PC" if realization in ("RG2b", "CI_PC") else "A_OS")
                target, target_backend = initializer_target("A_" + realization)
                owner = GRCV4(inputs, targets=(target,), differential_reference=backend,
                              target_differential_references=() if backend == target_backend else (target_backend,))
                declared = event(owner, target)
                result = owner.reconstruct_topology_event(declared)
                self.assertTrue(result.committed, result.failure)
                self.assertEqual(result.emitted_receipts[0].identity_payload["history"]["candidate"]["information_loss"], "candidate_history_loss")
                self.assertEqual(owner.state.lifecycle.current.W_A, tuple(oracle(target, target_backend, inputs.current.C)[1]))
                capture("A_loss_" + realization, inputs, owner, declared, result)
                if realization == "OS":
                    changed = replace(inputs, current=replace(inputs.current, W_A=(1.875,)), reset=replace(inputs.reset, W_A=(1.8125,)))
                    second = GRCV4(changed, targets=(target,), differential_reference=backend)
                    other = second.reconstruct_topology_event(event(second, target))
                    self.assertTrue(other.committed, other.failure)
                    self.assertEqual(owner.state.lifecycle.current, second.state.lifecycle.current)
                    self.assertEqual(owner.state.lifecycle.reset.authoritative, second.state.lifecycle.reset.authoritative)
                    self.assertNotEqual(result.emitted_receipts[0].receipt_id, other.emitted_receipts[0].receipt_id)

    def test_all_ten_representation_targets_inverse_preserves_science_not_ledger(self):
        for candidate in ("C", "A"):
            for realization in ("OS", "CI", "RG2b", "PC", "CI_PC"):
                with self.subTest(family=candidate + realization):
                    inputs, backend = fixture(candidate + "_" + realization)
                    target, other, action = reversed_target(inputs, backend)
                    owner = GRCV4(inputs, targets=(target,), differential_reference=backend,
                                  target_differential_references=() if other is None else (other,))
                    before = owner.snapshot()
                    declared = representation(owner, target, action)
                    result = owner.transport_representation(declared)
                    self.assertTrue(result.committed, result.failure)
                    self.assertEqual(owner.state.lifecycle.current.C, inputs.current.C[::-1])
                    self.assertEqual(owner.state.lifecycle.reset.authoritative.C, inputs.reset.C[::-1])
                    self.assertEqual(owner.state.lifecycle.current.W_A, inputs.current.W_A)
                    self.assertEqual(owner.state.lifecycle.current.Z_4, inputs.current.Z_4)
                    capture("representation_" + candidate + "_" + realization, inputs, owner, declared, result)
                    inverse = GraphCoordinateAction(target.graph, action.source, (1, 0), (0,), (-1,))
                    result2 = owner.transport_representation(representation(owner, inputs.geometry.reference, inverse, "inverse"))
                    self.assertTrue(result2.committed, result2.failure)
                    after = owner.snapshot()
                    for key in ("scientific_state", "scientific_state_digest", "reset", "reference"):
                        self.assertEqual(before[key], after[key])
                    self.assertNotEqual(before["lifecycle_digest"], after["lifecycle_digest"])
                    self.assertEqual(len(after["commit_records"]), 2)
                    self.assertEqual(result2.emitted_receipts[0].identity_payload["core"]["parent_receipt_ids"],
                                     (result.emitted_receipts[0].receipt_id,))


if __name__ == "__main__":
    unittest.main()
