"""Native F1/F2 regression and compatibility pressure for P9-7.2b.

Run from repository root:
  PYTHONPATH=src:. .venv/bin/python -m unittest tests.models.test_grc_v4_event_audit -v
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import (
    GRCV4, GRCV4MappedTopologyEventRequest, GRCV4RepresentationRequest,
)
from pygrc.models.grc_v4_codec import V4IdentityError, V4SchemaError
from pygrc.models.grc_v4_event_codec import representation_identity
from pygrc.models.grc_v4_geometry import GRCV4Graph, GraphCoordinateAction, OrientedEdge
from pygrc.models import grc_v4_events as events
from tests.models.test_grc_v4_events import event, representation
from tests.models.test_grc_v4_migration import fixture, changed_reference

ALIAS = "unregistered_legacy_alias"


def identity_action(reference):
    graph = reference.graph
    return GraphCoordinateAction(graph, graph,
        tuple(range(len(graph.live_node_ids))),
        tuple(range(len(graph.live_edge_ids))),
        (1,) * len(graph.live_edge_ids))


def legacy_event(owner, target, alias=ALIAS, operation="legacy"):
    payload = event(owner, target, operation=operation).to_payload()
    payload["history_policy"]["candidate"]["policy_id"] = alias
    return GRCV4MappedTopologyEventRequest.from_payload(payload)


def fresh_owner():
    inputs, _ = fixture("C_OS")
    reference = inputs.geometry.reference
    unusual = changed_reference(reference, "lifecycle", history_policy_id=ALIAS)
    return GRCV4(inputs, targets=(unusual,)), reference, unusual


def enter_joint(owner, reference, kind):
    if kind == "representation":
        return owner.transport_representation(
            representation(owner, reference, identity_action(reference), "joint-entry"))
    return owner.reconstruct_topology_event(event(owner, reference, operation="joint-entry"))


class RuntimeAuditRegressions(unittest.TestCase):
    def check_no_bad_append(self, entry):
        owner, reference, unusual = fresh_owner()
        result = enter_joint(owner, reference, entry)
        self.assertTrue(result.committed, result.failure)
        before = owner.snapshot()
        self.assertEqual(owner.duplicate().snapshot(), before)
        publication = owner._operation._owned
        result = owner.apply_topology_event(legacy_event(owner, unusual))
        self.assertFalse(result.committed,
            "A v1 operation must not append a declaration forbidden by the resulting joint snapshot contract")
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), before)
        self.assertEqual(owner.duplicate().snapshot(), before)

    def test_representation_then_legacy_alias_must_not_publish_unrestorable_state(self):
        self.check_no_bad_append("representation")

    def test_reconstruction_then_legacy_alias_must_not_publish_unrestorable_state(self):
        self.check_no_bad_append("reconstruction")

    def test_legacy_only_behavior_is_not_globally_restricted(self):
        owner, _, unusual = fresh_owner()
        result = owner.apply_topology_event(legacy_event(owner, unusual))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_old_alias_then_joint_entry_remains_an_atomic_rejection(self):
        for entry in ("representation", "reconstruction"):
            with self.subTest(entry=entry):
                owner, _, unusual = fresh_owner()
                self.assertTrue(owner.apply_topology_event(legacy_event(owner, unusual)).committed)
                before = owner.snapshot()
                result = enter_joint(owner, unusual, entry)
                self.assertFalse(result.committed)
                self.assertEqual(owner.snapshot(), before)

    def test_registered_legacy_aliases_remain_valid_after_joint_entry(self):
        for entry in ("representation", "reconstruction"):
            for alias in ("candidate_c_no_independent_history_v1", "candidate_c_rederive_no_history_v1"):
                with self.subTest(entry=entry, alias=alias):
                    owner, ref, _ = fresh_owner()
                    self.assertTrue(enter_joint(owner, ref, entry).committed)
                    result = owner.apply_topology_event(legacy_event(owner, ref, alias))
                    self.assertTrue(result.committed, result.failure)
                    self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())

    def test_internal_reference_errors_propagate_without_scientific_failure_receipts(self):
        for error_type in (ValueError, V4IdentityError, V4SchemaError, RuntimeError):
            with self.subTest(error_type=error_type.__name__):
                owner, ref, _ = fresh_owner()
                declared = representation(owner, ref, identity_action(ref))
                before = owner.snapshot()
                publication = owner._operation._owned
                error = error_type("programmer failure after valid correspondence declaration")
                with patch.object(events, "coordinate_reference", side_effect=error):
                    with self.assertRaises(error_type) as caught:
                        owner.transport_representation(declared)
                self.assertIs(caught.exception, error)
                self.assertIs(owner._operation._owned, publication)
                self.assertEqual(owner.snapshot(), before)

    def test_real_declaration_failures_still_return_typed_atomic_rejections(self):
        owner, ref, _ = fresh_owner()
        before = owner.snapshot()
        payload = representation(owner, ref, identity_action(ref)).to_payload()
        correspondence = payload["correspondence"]
        correspondence["payload"]["edge_map"][0]["orientation"] = -1
        # Hash valid bytes: the endpoint/orientation declaration is semantically wrong.
        correspondence["correspondence_id"] = representation_identity(
            "correspondence_payload", correspondence["payload"])
        result = owner.transport_representation(GRCV4RepresentationRequest.from_payload(payload))
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.code, "invalid_topology_event")
        self.assertEqual(owner.snapshot(), before)

    def test_changed_graph_a_target_uses_mapped_resource_in_both_initializer_roles(self):
        """Additional pressure, not a demonstrated implementation defect.

        Combines nonidentity affine resources, changed edge count and nonzero
        descriptor/current conductance channels at an A target.
        """
        from tests.models.test_grc_v4_candidate_a import fixture as a_reference
        from tests.models.test_grc_v4_initializer import oracle
        from pygrc.models.grc_v4_initializer import HISTORY_POLICY
        from pygrc.models.grc_v4_candidate_a import A_SITE_POTENTIAL

        graph = GRCV4Graph(("x", "y", "z"),
            (OrientedEdge("f", "x", "y"), OrientedEdge("g", "y", "z")))
        target, backend = a_reference(graph=graph, positions=((0.,), (1.,), (3.,)),
            weights={"f": 1., "g": 1.25}, eta=.125, kappa_c=.1,
            kappa_Ah=.1, alpha=.02, beta=.03, gamma=.02, chi_A=.125, zeta_A=.125,
            site_potential_id=A_SITE_POTENTIAL)
        target = changed_reference(target, "lifecycle", history_policy_id=HISTORY_POLICY)
        target = changed_reference(target, "realization", tolerance=1.)
        target = changed_reference(target, "charge", absolute_tolerance=1e-10)
        # The raw constructor fixture defaults to exact-zero solver residuals;
        # this non-dyadic native-current test declares binary64 tolerances.
        target = changed_reference(target, "solver", absolute_tolerance=1e-12, relative_tolerance=1e-12)
        source, _ = fixture("C_OS")
        owner = GRCV4(source, targets=(target,), target_differential_references=(backend,))
        matrix = (1., 0., 0., .5, 0., .5)
        increment = (.25, 0., 0.)
        result = owner.reconstruct_topology_event(event(owner, target, matrix, increment))
        self.assertTrue(result.committed, result.failure)
        for old, new in ((source.current, owner.state.lifecycle.current),
                         (source.reset, owner.state.lifecycle.reset.authoritative)):
            expected = tuple(float(Fraction(increment[i]) + sum(
                (Fraction(matrix[2*i+j])*Fraction(old.C[j]) for j in range(2)), Fraction()))
                for i in range(3))
            self.assertEqual(new.C, expected)
            self.assertEqual(new.W_A, tuple(oracle(target, backend, expected)[1]))
            self.assertIsNone(new.Z_4)
        self.assertNotEqual(owner.state.lifecycle.current.W_A,
                            owner.state.lifecycle.reset.authoritative.W_A)
        self.assertEqual(owner.state.lifecycle.Q_target, source.Q_target + .25)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current, owner.state.lifecycle.reset.authoritative)


if __name__ == "__main__":
    unittest.main(verbosity=2)
