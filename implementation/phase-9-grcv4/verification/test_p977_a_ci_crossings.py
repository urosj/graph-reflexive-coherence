"""Exact A_CI crossing gaps; retained migrations are projected, not rerun."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models import grc_v4_lifecycle as lifecycle
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_migration import fixture, migration
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_initializer import target as initializer_target, oracle
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from test_p977_a_ci_local import NOMINATED


class ACICrossingTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}

    def emit(self, case, before, owner, result, declared, **observation):
        recorder.CompleteProfileCatalogTests.emit(self, case, before, owner, result,
            request=declared, observation=observation)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def reset_check(self, owner):
        before, state = owner.snapshot(), owner.state.lifecycle
        self.assertNotEqual(state.current, state.reset.authoritative)
        owner.reset()
        after = owner.snapshot()
        self.assertEqual(owner.state.lifecycle.current, state.reset.authoritative)
        self.assertEqual(owner.state.lifecycle.reset, state.reset)
        self.assertEqual((owner.state.lifecycle.time, owner.state.lifecycle.step_index, owner.state.lifecycle.Q_target),
                         (state.time, state.step_index, state.Q_target))
        for key in ('reference', 'transition_records'):
            self.assertEqual(after[key], before[key])
        self.assertEqual(after['receipt_ledger'][:-4], before['receipt_ledger'])
        self.assertEqual(after['commit_records'][:-1], before['commit_records'])
        self.assertEqual(restore(after).snapshot(), after)
        return self.obj(after)

    def test_returning_carrier_and_outgoing_candidate_loss(self):
        for case, source, target_family in (('persistent_A_PC', 'A_PC', 'A_CI'),
                                            ('A_to_C', 'A_CI', 'C_OS')):
            inputs, backend = fixture(source)
            target_inputs, other = fixture(target_family)
            target = target_inputs.geometry.reference
            self.assertIn(NOMINATED, (inputs.geometry.reference.profile.complete_profile_id, target.profile.complete_profile_id))
            extras = () if other is None or other.identity == backend.identity else (other,)
            owner = GRCV4(inputs, differential_reference=backend, targets=(target,), target_differential_references=extras)
            self.assertTrue(owner.step_v4_input(request(0, 'seed-' + source)).committed)
            before, old = owner.snapshot(), owner.state.lifecycle
            declared = migration(owner, target, operation=source + '-to-' + target_family)
            result = owner.migrate_profile(declared)
            self.assertTrue(result.committed, result.failure)
            after, new = owner.snapshot(), owner.state.lifecycle
            for a, b in ((old.current, new.current), (old.reset.authoritative, new.reset.authoritative)):
                self.assertEqual(b.C, a.C)
                self.assertEqual(b.W_A, a.W_A if target_family == 'A_CI' else None)
                self.assertIsNone(b.Z_4)
            self.assertEqual((new.time, new.step_index, new.Q_target), (old.time, old.step_index, old.Q_target))
            if source == 'A_PC':
                self.assertNotEqual(old.current.Z_4, old.reset.authoritative.Z_4)
                self.assertNotEqual(old.current.Z_4, (0.,))
                self.assertNotEqual(old.reset.authoritative.Z_4, (0.,))
            history = result.emitted_receipts[0].identity_payload['history']
            candidate = 'exact_transport' if source == 'A_PC' else 'explicit_loss'
            carrier = 'explicit_loss' if source == 'A_PC' else 'not_applicable'
            losses = ['carrier_history_loss'] if source == 'A_PC' else ['candidate_history_loss']
            self.assertEqual(history['candidate']['disposition'], candidate)
            self.assertEqual(history['carrier']['disposition'], carrier)
            self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']), losses)
            reset_object = self.reset_check(owner)
            self.emit(case, before, restore(after), result, declared,
                after_reset_object=reset_object, expected_losses=losses,
                expected_candidate=candidate, expected_carrier=carrier)

    def test_mapped_event_distinct_roles_initializer_oracle_and_reset(self):
        inputs, backend = fixture('A_CI')
        target, other = initializer_target('A_CI')
        self.assertEqual(inputs.geometry.reference.profile.complete_profile_id, NOMINATED)
        self.assertNotEqual(target.profile.complete_profile_id, NOMINATED)
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,),
                      target_differential_references=() if other.identity == backend.identity else (other,))
        self.assertTrue(owner.step_v4_input(request(0, 'event-seed')).committed)
        before, old = owner.snapshot(), owner.state.lifecycle
        declared = event(owner, target, matrix=(0, 1, 1, 0), increment=(.125, 0), operation='A_CI-mapped-event')
        result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        after = owner.snapshot()
        expectations = {}
        for role, a, b in (('current', old.current, owner.state.lifecycle.current),
                           ('reset', old.reset.authoritative, owner.state.lifecycle.reset.authoritative)):
            C = (float(F(a.C[1]) + F(1, 8)), a.C[0])
            derived, W = oracle(target, other, C)
            self.assertEqual(b.C, C)
            self.assertEqual(list(b.W_A), W)
            self.assertIsNone(b.Z_4)
            expectations[role] = dict(C=list(C), W_A=W, Z_4=None, reference_pass=derived)
        self.assertNotEqual(expectations['current']['W_A'], expectations['reset']['W_A'])
        self.assertEqual(owner.state.lifecycle.Q_target, float(F(old.Q_target) + F(1, 8)))
        self.assertEqual((owner.state.lifecycle.time, owner.state.lifecycle.step_index), (old.time, old.step_index))
        history = result.emitted_receipts[0].identity_payload['history']
        self.assertEqual(history['candidate']['information_loss'], 'candidate_history_loss')
        self.assertEqual(history['carrier']['disposition'], 'not_applicable')
        self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']), ['candidate_history_loss'])
        # A missing crossing preimage cannot be reconstructed from the final state.
        bad = deepcopy(after); bad['transition_records'] = []
        with self.assertRaises(ValueError): restore(bad)
        reset_object = self.reset_check(owner)
        self.emit('mapped_event', before, restore(after), result, declared,
            expectations=expectations, expected_Q_target=float(F(old.Q_target) + F(1, 8)),
            after_reset_object=reset_object, missing_archive_rejected=True,
            expected_candidate=history['candidate']['disposition'], expected_carrier='not_applicable',
            expected_losses=['candidate_history_loss'])

    def test_reset_only_readmission_and_unavailable_incoming_initializer(self):
        inputs, backend = fixture('A_CI')
        target = fixture('A_PC')[0].geometry.reference
        for failing in (False, True):
            altered = replace(inputs, reset=replace(inputs.reset, W_A=(3.,))) if failing else replace(inputs, reset=inputs.current)
            owner = GRCV4(altered, differential_reference=backend, targets=(target,))
            before, publication = owner.snapshot(), owner._operation._owned
            declared = migration(owner, target, operation='reset-only' if failing else 'current-as-reset-control')
            with patch.object(lifecycle, '_validate_publication', wraps=lifecycle._validate_publication) as publish:
                result = owner.migrate_profile(declared)
            self.assertEqual(result.committed, not failing)
            if failing:
                self.assertEqual(result.failure.stage, 'target_readmission')
                publish.assert_not_called()
                self.assertIs(owner._operation._owned, publication)
                self.assertEqual(owner.snapshot(), before)
            self.emit('readmission_rejection' if failing else 'readmission_control', before, owner, result, declared,
                      failure_stage=None if not failing else result.failure.stage)

        c_inputs, _ = fixture('C_OS')
        ref = inputs.geometry.reference
        owner = GRCV4(c_inputs, targets=(ref,), target_differential_references=(backend,))
        # Send a well-formed declaration claiming the accepted initializer, but
        # keep the exact nominated target that does not select that producer.
        selected, _ = initializer_target('A_CI')
        payload = migration(owner, selected).to_payload()
        payload['target_profile_id'] = NOMINATED
        declared = GRCV4MigrationRequest.from_payload(payload)
        before, publication = owner.snapshot(), owner._operation._owned
        result = owner.migrate_profile(declared)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, 'admission')
        self.assertIn('initializer source', result.failure.message)
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), before)
        self.emit('incoming_C_rejection', before, owner, result, declared,
                  selected_initializer_profile_id=selected.profile.complete_profile_id,
                  failed_target_profile_id=NOMINATED, failure_stage='admission',
                  scope='negative endpoint boundary, not positive C-to-nominated-A execution')


if __name__ == '__main__':
    unittest.main()
