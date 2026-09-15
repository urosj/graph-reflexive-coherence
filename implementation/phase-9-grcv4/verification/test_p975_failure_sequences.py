"""Bounded mixed-prefix failure/reset pressure, not parent-DAG conformance."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import unittest

from pygrc.models.grc_v4 import GRCV4, GRCV4MappedTopologyEventRequest, GRCV4RepresentationRequest
from pygrc.models.grc_v4_event_codec import representation_identity
from pygrc.models.grc_v4_lifecycle import _state_inputs
from tests.models.test_grc_v4_migration import fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event, representation, reversed_target
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_generic_lifecycle import endpoint, restore
from tests.models.test_grc_v4_pc import configure

EVIDENCE = {}


class FailureSequenceTests(unittest.TestCase):
    def commit_check(self, owner, call, declaration):
        ledger = owner.snapshot()['receipt_ledger']
        result = call(declaration)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.snapshot()['receipt_ledger'],
                         ledger + [r.to_payload() for r in result.emitted_receipts])
        return result

    def reset_check(self, owner):
        before = owner.snapshot()
        old = owner.state.lifecycle
        self.assertNotEqual(old.current, old.reset.authoritative,
                            'reset pressure must not start from an already reset state')
        owner.reset()
        after = owner.snapshot()
        state = owner.state.lifecycle
        self.assertEqual(state.current, old.reset.authoritative)
        self.assertEqual(state.reset, old.reset)
        self.assertEqual((state.time, state.step_index, state.Q_target),
                         (old.time, old.step_index, old.Q_target))
        self.assertEqual(after['reference'], before['reference'])
        self.assertEqual(after['transition_records'], before['transition_records'])
        self.assertEqual(after['receipt_ledger'][:len(before['receipt_ledger'])], before['receipt_ledger'])
        self.assertEqual(after['commit_records'][:-1], before['commit_records'])
        self.assertEqual(after['receipt_ledger'][len(before['receipt_ledger'])]['identity_payload']['schema_version'],
                         'grcv4-reset-receipt-v1')
        self.assertEqual(restore(after).snapshot(), after)
        return dict(before=endpoint(before), after=endpoint(after),
                    reset_receipts=after['receipt_ledger'][len(before['receipt_ledger']):])

    def rejection(self, owner, declaration, call, stage):
        before, publication = owner.snapshot(), owner._operation._owned
        result = call(declaration)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, stage)
        self.assertIsNone(result.commit_id)
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), before)
        receipt = result.emitted_receipts[0].to_payload()
        self.assertEqual(receipt['identity_payload']['source_state_digest'],
                         receipt['identity_payload']['observed_poststate_digest'])
        return dict(request=declaration.to_payload(), stage=stage, message=result.failure.message,
                    receipt=receipt, unchanged=endpoint(before))

    def test_reset_after_step_migration_event_and_missing_archives(self):
        inputs, backend = fixture('A_PC')
        target = fixture('A_CI_PC')[0].geometry.reference
        c_target = fixture('C_PC')[0].geometry.reference
        owner = GRCV4(inputs, differential_reference=backend, targets=(target, c_target))
        step = request(2**-12, 'positive-step')
        result = self.commit_check(owner, owner.step_v4_input, step)
        self.assertNotEqual(owner.state.lifecycle.current, inputs.current)
        rows = [dict(operation='ordinary', request=step.to_payload(), reset=self.reset_check(owner))]
        self.assertTrue(owner.step_v4_input(request(2**-12, 'before-migration')).committed)
        declared = migration(owner, target)
        old = owner.state.lifecycle
        result = self.commit_check(owner, owner.migrate_profile, declared)
        self.assertEqual(owner.state.lifecycle.current, old.current)
        self.assertEqual(owner.state.lifecycle.reset.authoritative, old.reset.authoritative)
        rows.append(dict(operation='migration', request=declared.to_payload(), reset=self.reset_check(owner)))
        self.assertTrue(owner.step_v4_input(request(2**-12, 'before-event')).committed)
        old = owner.state.lifecycle
        declared = event(owner, c_target, matrix=(0, 1, 1, 0), increment=(.25, 0))
        result = self.commit_check(owner, owner.reconstruct_topology_event, declared)
        for source, target_state in ((old.current, owner.state.lifecycle.current),
                                     (old.reset.authoritative, owner.state.lifecycle.reset.authoritative)):
            expected = (float(Fraction(source.C[1]) + Fraction(1, 4)), source.C[0])
            self.assertEqual(target_state.C, expected)
            self.assertIsNone(target_state.W_A)
            self.assertEqual(target_state.Z_4, (0.,))
        self.assertEqual(owner.state.lifecycle.reset.authoritative.C, (2.1875, 2.0625))
        self.assertIsNone(owner.state.lifecycle.reset.authoritative.W_A)
        self.assertEqual(owner.state.lifecycle.reset.authoritative.Z_4, (0.,))
        self.assertEqual(owner.state.lifecycle.Q_target, 4.25)
        rows.append(dict(operation='event', request=declared.to_payload(), reset=self.reset_check(owner)))
        valid = owner.snapshot()
        self.assertEqual(restore(valid).snapshot(), valid)
        rejected = []
        for kind in ('all_crossings', 'migration_crossing', 'event_crossing', 'source_reset_preimage', 'missing_receipt_member'):
            bad = deepcopy(valid)
            if kind == 'all_crossings':
                bad['transition_records'] = []
            elif kind == 'migration_crossing':
                bad['transition_records'].pop(0)
            elif kind == 'event_crossing':
                bad['transition_records'].pop(-1)
            elif kind == 'source_reset_preimage':
                bad['transition_records'][-1].pop('source_reset')
            else:
                bad['receipt_ledger'].pop(0)
            with self.subTest(kind=kind), self.assertRaises(ValueError) as caught:
                restore(bad)
            self.assertEqual(owner.snapshot(), valid)
            rejected.append(dict(mutation=kind, error_type=type(caught.exception).__name__, message=str(caught.exception)))
        EVIDENCE['reset_sequence'] = dict(source=inputs.to_payload(), backend=backend.to_payload(),
            targets=[target.to_payload(), c_target.to_payload()], operations=rows, missing_archives=rejected)

    def test_invalid_event_maps_and_history_after_positive_step(self):
        inputs, backend = fixture('A_PC')
        target = fixture('C_PC')[0].geometry.reference
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,))
        stale = event(owner, target)
        self.assertTrue(owner.step_v4_input(request(2**-12, 'map-prefix')).committed)
        rows = [dict(case='stale_state', **self.rejection(owner, stale, owner.reconstruct_topology_event, 'admission'))]
        base = event(owner, target).to_payload()
        for kind in ('source_order', 'target_order', 'charge_column', 'negative_output',
                     'candidate_digest', 'carrier_digest', 'invented_preservation', 'missing_history',
                     'unregistered_target'):
            bad = deepcopy(base)
            stage = 'admission'
            if kind in ('source_order', 'target_order'):
                bad['resource_transform'][kind.replace('_order', '_vertex_ids')].reverse()
            elif kind == 'charge_column':
                bad['resource_transform']['row_major_coefficients'] = [1, 1, 0, 1]
            elif kind == 'negative_output':
                bad['resource_transform']['target_increment'] = [-10, 0]
                stage = 'target_construction'
            elif kind in ('candidate_digest', 'carrier_digest'):
                bad['history_policy'][kind.split('_')[0]]['source_history_digest'] = 'grcv4-history-content-sha256:' + '0'*64
            elif kind == 'invented_preservation':
                bad['history_policy']['carrier'].update(policy_id='identity_carrier_history_v1',
                    disposition='exact_transport', information_loss='none', target_initializer_id=None)
            elif kind == 'missing_history':
                bad.pop('history_policy')
            else:
                bad['target_profile_id'] = 'grcv4-profile-sha256:' + '0'*64
            before, publication = owner.snapshot(), owner._operation._owned
            if kind == 'missing_history':
                with self.assertRaises(ValueError) as caught:
                    GRCV4MappedTopologyEventRequest.from_payload(bad)
                rows.append(dict(case=kind, boundary='wire_decode', error_type=type(caught.exception).__name__))
            elif kind == 'invented_preservation':
                typed = GRCV4MappedTopologyEventRequest.from_payload(bad)
                with self.assertRaises(ValueError) as caught:
                    owner.reconstruct_topology_event(typed)
                rows.append(dict(case=kind, boundary='event_wire_admission', request=bad,
                                 error_type=type(caught.exception).__name__))
            else:
                typed = GRCV4MappedTopologyEventRequest.from_payload(bad)
                rows.append(dict(case=kind, **self.rejection(owner, typed, owner.reconstruct_topology_event, stage)))
            self.assertIs(owner._operation._owned, publication)
            self.assertEqual(owner.snapshot(), before)
        # No failure receipt was appended; a corrected event still succeeds.
        result = owner.reconstruct_topology_event(event(owner, target, operation='corrected'))
        self.assertTrue(result.committed, result.failure)
        EVIDENCE['invalid_events'] = dict(source=inputs.to_payload(), backend=backend.to_payload(),
            target=target.to_payload(), rejections=rows, reset=self.reset_check(owner))

    def test_missing_or_invalid_representation_never_falls_back(self):
        inputs, backend = fixture('A_PC')
        target, target_backend, action = reversed_target(inputs, backend)
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,),
                      target_differential_references=(target_backend,))
        self.assertTrue(owner.step_v4_input(request(2**-12, 'coordinate-prefix')).committed)
        base = representation(owner, target, action).to_payload()
        rows = []
        for kind in ('missing_correspondence', 'missing_edge', 'wrong_orientation', 'duplicate_target'):
            bad = deepcopy(base)
            before, publication = owner.snapshot(), owner._operation._owned
            if kind == 'missing_correspondence':
                bad.pop('correspondence')
            else:
                mapping = bad['correspondence']['payload']
                if kind == 'missing_edge':
                    mapping['edge_map'] = []
                elif kind == 'wrong_orientation':
                    mapping['edge_map'][0]['orientation'] *= -1
                else:
                    mapping['vertex_map'][1]['target_vertex_id'] = mapping['vertex_map'][0]['target_vertex_id']
                # Schema-valid defects are reidentified to reach semantic map
                # checks, not fail on an accidentally stale correspondence ID.
                try:
                    bad['correspondence']['correspondence_id'] = representation_identity('correspondence_payload', mapping)
                except ValueError:
                    self.assertEqual(kind, 'missing_edge')
            if kind == 'missing_correspondence':
                with self.assertRaises(ValueError):
                    GRCV4RepresentationRequest.from_payload(bad)
                rows.append(dict(case=kind, boundary='wire_decode'))
            else:
                typed = GRCV4RepresentationRequest.from_payload(bad)
                rows.append(dict(case=kind, **self.rejection(owner, typed, owner.transport_representation, 'admission')))
            self.assertIs(owner._operation._owned, publication)
            self.assertEqual(owner.snapshot(), before)
        old = owner.state.lifecycle
        result = owner.transport_representation(representation(owner, target, action))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']), [])
        for source, target_state in ((old.current, owner.state.lifecycle.current),
                                     (old.reset.authoritative, owner.state.lifecycle.reset.authoritative)):
            self.assertEqual(target_state.C, source.C[::-1])
            self.assertEqual(target_state.W_A, source.W_A)
            self.assertEqual(target_state.Z_4, source.Z_4)
        EVIDENCE['invalid_representations'] = dict(source=inputs.to_payload(), backend=backend.to_payload(),
            target=target.to_payload(), target_backend=target_backend.to_payload(), rejections=rows,
            reset=self.reset_check(owner))

    def test_target_readmission_failure_after_mixed_prefix(self):
        inputs, _ = fixture('C_OS')
        inputs = replace(inputs, reset=replace(inputs.reset, C=(0, 4)))
        target = changed_reference(inputs.geometry.reference, 'candidate', eta_C=.25)
        strict = configure(inputs, resource_radius=3).geometry.reference
        owner = GRCV4(inputs, targets=(target, strict))
        self.assertTrue(owner.step_v4_input(request(2**-12, 'readmission-prefix')).committed)
        self.assertTrue(owner.migrate_profile(migration(owner, target)).committed)
        self.assertTrue(owner.reconstruct_topology_event(event(owner, target)).committed)
        before = owner.snapshot()
        # Positive control admits exactly the live resource as both roles.
        good = _state_inputs(target, owner.state.lifecycle)
        good = replace(good, reset=good.current, receipt_ids=())
        control = GRCV4(good, targets=(strict,))
        result = control.reconstruct_topology_event(event(control, strict))
        self.assertTrue(result.committed, result.failure)
        rows = []
        for kind in ('migration', 'event'):
            declaration = migration(owner, strict) if kind == 'migration' else event(owner, strict)
            call = owner.migrate_profile if kind == 'migration' else owner.reconstruct_topology_event
            row = self.rejection(owner, declaration, call, 'target_readmission')
            self.assertIn('resource', row['message'])
            rows.append(dict(operation=kind, **row))
        self.assertEqual(owner.snapshot(), before)
        reset = self.reset_check(owner)
        self.assertEqual(owner.state.lifecycle.current.C, (0, 4))
        EVIDENCE['mixed_readmission'] = dict(source=inputs.to_payload(), target=target.to_payload(),
            strict_target=strict.to_payload(), prefix=endpoint(before), rejections=rows, reset=reset)


if __name__ == '__main__':
    unittest.main()
