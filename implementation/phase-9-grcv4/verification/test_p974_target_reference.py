"""P9-7.4: complete C target authority and pre-publication numerical admission."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_codec import decode_canonical_json, payload_identity
from pygrc.models.grc_v4_geometry import GRCV4Graph, GRCV4ReferenceGeometry, OrientedEdge
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models import grc_v4_lifecycle as lifecycle
from tests.models.test_grc_v4_migration import fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_candidate_c import current_fixture, dense_current_oracle
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_pc import configure

EVIDENCE = {}
FAMILIES = ('C_OS', 'C_CI', 'C_RG2b', 'C_PC', 'C_CI_PC')


def summary(point):
    a = point.algebra
    return dict(reference_id=point.inputs.geometry.reference.identity,
                C=list(point.inputs.current.C), hodge=point.inputs.geometry.one_form_hodge.matrix,
                selector=a.selector.projector, sector=a.selector.selected.values, retained_hodge=a.retained_hodge.matrix,
                potential=a.potential.values, baseline=a.baseline.values,
                current=point.current.values, read_back=point.read.flux.values)


class TargetReferenceTests(unittest.TestCase):
    def test_reference_map_rejections_at_public_construction_boundary(self):
        rows = []
        for family in FAMILIES:
            ref = fixture(family)[0].geometry.reference
            edge = ref.graph.live_edge_ids[0]
            variants = {'missing': {}, 'extra': {edge: 2, 'foreign': 3},
                        'unmatched_same_dimension': {'foreign': 2}, 'zero': {edge: 0},
                        'negative': {edge: -1}, 'nan': {edge: float('nan')},
                        'infinity': {edge: float('inf')}}
            for kind, weights in variants.items():
                with self.subTest(family=family, kind=kind):
                    raw = deepcopy(ref.to_payload())
                    params = raw['profile']['params_resolved']
                    params['candidate']['W_C_tr'] = weights
                    # Rehash finite declarations so edge-coverage failures are
                    # not merely stale-digest failures. Nonfinite wire values
                    # are rejected before any valid content identity exists.
                    try:
                        params['candidate']['W_C_tr_content_digest'] = payload_identity(
                            'wctr_identity_payload', dict(schema_version='grcv4-wctr-identity-v1', W_C_tr=weights))
                        reidentify(params, raw['profile']['identity_payload'])
                        raw['profile'] = resolve_profile(params, raw['profile']['identity_payload']).to_payload()
                    except ValueError:
                        self.assertIn(kind, ('missing', 'zero', 'negative', 'nan', 'infinity'))
                    with self.assertRaises(ValueError) as caught:
                        GRCV4ReferenceGeometry.from_payload(raw)
                    if kind in ('extra', 'unmatched_same_dimension'):
                        self.assertIn('target_W_C_tr_matches_live_edges', str(caught.exception))
                    rows.append(dict(family=family, mutation=kind, boundary='reference_construction',
                                     error_type=type(caught.exception).__name__, message=str(caught.exception)))
            # Duplicate object keys cannot survive as a Python mapping: test
            # the actual JSON decoder, not an already-collapsed dict.
            with self.assertRaises(ValueError):
                decode_canonical_json('{"W_C_tr":{"' + edge + '":2,"' + edge + '":3}}')
            rows.append(dict(family=family, mutation='duplicate', boundary='wire_decode'))
        EVIDENCE['reference_rejections'] = rows

    def test_all_five_c_targets_read_both_roles_before_publication(self):
        rows = []
        for family in FAMILIES:
            with self.subTest(family=family):
                inputs, _ = fixture('C_OS')
                target = fixture(family)[0].geometry.reference
                if family == 'C_OS':
                    target = changed_reference(target, 'candidate', eta_C=.25)
                owner = GRCV4(inputs, targets=(target,))
                original = owner._operation._owned
                seen = []
                native = CandidateCCurrent.__post_init__
                validate = lifecycle._validate_publication

                def observe(point):
                    native(point)
                    if point.inputs.geometry.reference.identity == target.identity:
                        self.assertIs(owner._operation._owned, original)
                        seen.append(tuple(point.inputs.current.C))

                def publication(*args, **kwargs):
                    self.assertIs(owner._operation._owned, original)
                    self.assertIn(inputs.current.C, seen)
                    self.assertIn(inputs.reset.C, seen)
                    return validate(*args, **kwargs)

                declared = event(owner, target)
                with patch.object(CandidateCCurrent, '__post_init__', observe), patch.object(
                        lifecycle, '_validate_publication', publication):
                    result = owner.reconstruct_topology_event(declared)
                self.assertTrue(result.committed, result.failure)
                self.assertIsNot(owner._operation._owned, original)
                self.assertIsNone(owner.state.lifecycle.current.W_A)
                self.assertIsNone(owner.state.lifecycle.reset.authoritative.W_A)
                self.assertIsNone(owner.snapshot()['transition_records'][-1]['initializer_pair'])
                self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
                rows.append(dict(family=family, source=inputs.to_payload(), target=target.to_payload(),
                                 request=declared.to_payload(), observed_resources=seen,
                                 receipts=[r.to_payload() for r in result.emitted_receipts]))
        EVIDENCE['five_targets'] = rows

    def test_changed_graph_target_rederives_all_c_surfaces(self):
        inputs, _ = fixture('C_OS')
        graph = GRCV4Graph(('x', 'y', 'z'), (OrientedEdge('b', 'y', 'z'),
            OrientedEdge('a', 'x', 'y'), OrientedEdge('parallel', 'x', 'y')))
        target_inputs = current_fixture(graph=graph, weights={'parallel': 3, 'a': 2, 'b': 1},
            resource=(2, 1, 1), changes={'candidate': dict(Lambda_C=.5, eta_C=.125,
                kappa_M_C=.125, tau_C=.125, chi_C=.125, zeta_C=.125)})
        target = target_inputs.geometry.reference
        owner = GRCV4(inputs, targets=(target,))
        declared = event(owner, target, matrix=(1, 0, 0, .5, 0, .5), increment=(0, 0, 0))
        native = CandidateCCurrent.__post_init__
        seen = {}

        def observe(point):
            native(point)
            if point.inputs.geometry.reference.identity != target.identity:
                return
            oracle = dense_current_oracle(point.inputs)
            for actual, expected in ((point.algebra.selector.projector, oracle['projector']),
                    (point.algebra.selector.selected.values, oracle['sector']),
                    (point.algebra.retained_hodge.matrix, oracle['hm']),
                    (point.algebra.potential.values, oracle['phi']),
                    (point.algebra.baseline.values, oracle['j0']),
                    (point.current.values, oracle['current']), (point.read.flux.values, oracle['read'])):
                np.testing.assert_allclose(actual, expected, rtol=1e-10, atol=1e-12)
            np.testing.assert_array_equal(point.algebra.transport.structural_hodge.matrix, np.diag([1, 2, 3]))
            np.testing.assert_array_equal(point.algebra.transport.mobility.matrix, np.diag([.125, .25, .375]))
            seen[tuple(point.inputs.current.C)] = summary(point)

        with patch.object(CandidateCCurrent, '__post_init__', observe):
            result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        current, reset = (2.125, .9375, .9375), (2.0625, .96875, .96875)
        self.assertEqual(owner.state.lifecycle.current.C, current)
        self.assertEqual(owner.state.lifecycle.reset.authoritative.C, reset)
        self.assertEqual(set(seen), {current, reset})
        self.assertNotEqual(seen[current]['baseline'], seen[reset]['baseline'])
        self.assertTrue(any(seen[current]['read_back']))
        snapshot = owner.snapshot()
        self.assertEqual(owner.duplicate().snapshot(), snapshot)
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current.C, reset)
        EVIDENCE['changed_graph'] = dict(source=inputs.to_payload(), target=target.to_payload(),
            request=declared.to_payload(), numerical_roles=[seen[current], seen[reset]],
            receipts=[r.to_payload() for r in result.emitted_receipts])

    def test_reset_only_numerical_rejection_and_late_failure_keep_whole_publication(self):
        inputs, _ = fixture('C_OS')
        inputs = replace(inputs, reset=replace(inputs.reset, C=(0, 4)))
        target = configure(inputs, resource_radius=3).geometry.reference
        rows = []
        for kind in ('event', 'migration'):
            owner = GRCV4(inputs, targets=(target,))
            original, snapshot = owner._operation._owned, owner.snapshot()
            declaration = event(owner, target) if kind == 'event' else migration(owner, target)
            call = owner.reconstruct_topology_event if kind == 'event' else owner.migrate_profile
            # Control: exactly this target admits current as both roles.
            good = replace(inputs, reset=inputs.current)
            control = GRCV4(good, targets=(target,))
            good_request = event(control, target) if kind == 'event' else migration(control, target)
            success = (control.reconstruct_topology_event(good_request) if kind == 'event'
                       else control.migrate_profile(good_request))
            self.assertTrue(success.committed, success.failure)
            with patch.object(lifecycle, '_validate_publication', wraps=lifecycle._validate_publication) as publish:
                result = call(declaration)
                publish.assert_not_called()
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, 'target_readmission')
            self.assertIn('resource', result.failure.message)
            self.assertIs(owner._operation._owned, original)
            self.assertEqual(owner.snapshot(), snapshot)
            rows.append(dict(operation=kind, source=inputs.to_payload(), target=target.to_payload(),
                request=declaration.to_payload(), failure_stage=result.failure.stage,
                failure_message=result.failure.message, receipt=result.emitted_receipts[0].to_payload()))
        inputs, _ = fixture('C_OS')
        owner = GRCV4(inputs)
        original, snapshot = owner._operation._owned, owner.snapshot()
        declared = event(owner, inputs.geometry.reference)
        with patch.object(lifecycle, '_validate_publication', side_effect=RuntimeError('late target publication')):
            with self.assertRaisesRegex(RuntimeError, 'late target publication'):
                owner.reconstruct_topology_event(declared)
        self.assertIs(owner._operation._owned, original)
        self.assertEqual(owner.snapshot(), snapshot)
        EVIDENCE['atomic_rejections'] = rows
        EVIDENCE['late_failure'] = 'unexpected_error_propagates_with_original_whole_publication'


if __name__ == '__main__':
    unittest.main()
