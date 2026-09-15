"""A_PC missing crossings; existing exact migration witnesses are not rerun."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models.grc_v4_pc import PCBaseChart
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_migration import fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_initializer import target as initializer_target, oracle
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_ci import independent_point
from test_p977_a_pc_local import NOMINATED
from test_p977_a_ci_crossings import ACICrossingTests


class APCCrossingTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj
    reset_check = ACICrossingTests.reset_check

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}

    def emit(self, case, before, owner, result, declared, **observation):
        recorder.CompleteProfileCatalogTests.emit(self, case, before, owner, result,
            request=declared, observation=observation)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_mapped_event_two_history_losses_initializer_and_reset(self):
        inputs, backend = fixture('A_PC')
        target, other = initializer_target('A_PC')
        self.assertEqual(inputs.geometry.reference.profile.complete_profile_id, NOMINATED)
        self.assertNotEqual(target.profile.complete_profile_id, NOMINATED)
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,),
            target_differential_references=() if other.identity==backend.identity else (other,))
        self.assertTrue(owner.step_v4_input(request(0, 'event-seed')).committed)
        before, old = owner.snapshot(), owner.state.lifecycle
        # Negative increment keeps the fixed initializer target inside its
        # admitted W chart. This is an explicit affine reconstruction, not a
        # representation change, native release, or preserving migration.
        declared = event(owner, target, matrix=(0,1,1,0), increment=(-.125,0), operation='A_PC-mapped-event')
        observed = []
        from pygrc.models.grc_v4_pc import CandidatePCRead
        native = CandidatePCRead.__post_init__
        def observe(read):
            native(read)
            if read.inputs.geometry.reference==target:
                observed.append(read)
        with patch.object(CandidatePCRead, '__post_init__', observe):
            result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        after = owner.snapshot(); expectations = {}
        for role, a, b in (('current',old.current,owner.state.lifecycle.current),
                           ('reset',old.reset.authoritative,owner.state.lifecycle.reset.authoritative)):
            C = (float(F(a.C[1])-F(1,8)), a.C[0])
            derived, W = oracle(target, other, C)
            self.assertEqual(b.C, C); self.assertEqual(list(b.W_A), W)
            self.assertEqual(b.Z_4, (0.,))
            self.assertNotEqual(a.Z_4, (0.,))
            read = next(r for r in observed if r.inputs.current==b)
            h = np.asarray(target.pairings.one_form.matrix)  # zero target carrier
            j, _ = independent_point(read.inputs, other, h)
            np.testing.assert_allclose(read.point.current.values, j, rtol=2e-12, atol=2e-14)
            np.testing.assert_allclose(read.inputs.geometry.one_form_hodge.matrix, h, rtol=0, atol=2e-14)
            expectations[role] = dict(C=list(C), W_A=W, Z_4=[0.], reference_pass=derived,
                readmission_inputs_object=self.obj(read.inputs.to_payload()), current=list(read.point.current.values),
                independent_current=j.tolist(), h=h.tolist())
        self.assertNotEqual(expectations['current']['W_A'], expectations['reset']['W_A'])
        self.assertEqual(owner.state.lifecycle.Q_target, float(F(old.Q_target)-F(1,8)))
        self.assertEqual((owner.state.lifecycle.time,owner.state.lifecycle.step_index),(old.time,old.step_index))
        history = result.emitted_receipts[0].identity_payload['history']
        losses = ['candidate_history_loss','carrier_history_loss']
        self.assertEqual(history['candidate']['information_loss'], losses[0])
        self.assertEqual(history['carrier']['information_loss'], losses[1])
        self.assertEqual(history['carrier']['disposition'], 'whole_carrier_reset')
        self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']), losses)
        bad = deepcopy(after); bad['transition_records'] = []
        with self.assertRaises(ValueError): restore(bad)
        reset_object = self.reset_check(owner)
        self.emit('mapped_event',before,restore(after),result,declared,
            expectations=expectations, target_reference_object=self.obj(target.to_payload()),
            target_backend_object=self.obj(other.to_payload()), expected_Q_target=float(F(old.Q_target)-F(1,8)),
            after_reset_object=reset_object, missing_archive_rejected=True,
            expected_candidate=history['candidate']['disposition'], expected_carrier='whole_carrier_reset',
            expected_losses=losses, source_history_removal_is_not_native_release=True)

    def test_reset_only_target_chart_failure_and_passing_control(self):
        inputs, backend = fixture('A_PC')
        target = changed_reference(fixture('C_PC')[0].geometry.reference,'realization',
            source_envelope_id=PCBaseChart(3.,1.,1.).identity)
        for failing in (False,True):
            # Both source states fit the source radius 4. Only the reset role
            # exceeds the target resource radius 3; W/Z removal is explicit.
            altered = replace(inputs,reset=replace(inputs.reset,C=(3.,1.))) if failing else replace(inputs,reset=inputs.current)
            owner = GRCV4(altered,differential_reference=backend,targets=(target,))
            before, publication = owner.snapshot(), owner._operation._owned
            declared = migration(owner,target,operation='reset-only' if failing else 'current-as-reset-control')
            with patch.object(lifecycle,'_validate_publication',wraps=lifecycle._validate_publication) as publish:
                result = owner.migrate_profile(declared)
            self.assertEqual(result.committed,not failing,result.failure)
            if failing:
                self.assertEqual(result.failure.stage,'target_readmission')
                publish.assert_not_called()
                self.assertIs(owner._operation._owned,publication)
                self.assertEqual(owner.snapshot(),before)
            else:
                for a,b in ((altered.current,owner.state.lifecycle.current),(altered.reset,owner.state.lifecycle.reset.authoritative)):
                    self.assertEqual(b.C,a.C); self.assertIsNone(b.W_A); self.assertEqual(b.Z_4,(0.,))
            self.emit('readmission_rejection' if failing else 'readmission_control',before,owner,result,declared,
                failure_stage='target_readmission' if failing else None,
                target_reference_object=self.obj(target.to_payload()),
                source_resource_radius=4.,target_resource_radius=3.,
                source_current_norm_squared=sum(float(x*x) for x in altered.current.C),
                source_reset_norm_squared=sum(float(x*x) for x in altered.reset.C))

    def test_unselected_incoming_initializer_and_changed_carrier_contract_reject(self):
        inputs, backend = fixture('A_PC'); ref = inputs.geometry.reference
        c_inputs, _ = fixture('C_PC')
        owner = GRCV4(c_inputs,targets=(ref,),target_differential_references=(backend,))
        selected, _ = initializer_target('A_PC')
        payload = migration(owner,selected).to_payload(); payload['target_profile_id']=NOMINATED
        declared = GRCV4MigrationRequest.from_payload(payload)
        before, publication = owner.snapshot(), owner._operation._owned
        result = owner.migrate_profile(declared)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage,'admission')
        self.assertIn('initializer source',result.failure.message)
        self.assertIs(owner._operation._owned,publication); self.assertEqual(owner.snapshot(),before)
        self.emit('incoming_C_rejection',before,owner,result,declared,
            selected_initializer_profile_id=selected.profile.complete_profile_id,
            failed_target_profile_id=NOMINATED,failure_stage='admission',
            scope='negative exact target boundary; separate positive initializer target is not nominated support')

        original = fixture('A_CI_PC')[0].geometry.reference
        target = changed_reference(original,'realization',tau_PC=1.)
        owner = GRCV4(inputs,differential_reference=backend,targets=(target,))
        payload = migration(owner,original).to_payload(); payload['target_profile_id']=target.profile.complete_profile_id
        declared = GRCV4MigrationRequest.from_payload(payload)
        before, publication = owner.snapshot(), owner._operation._owned
        result = owner.migrate_profile(declared)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage,'admission')
        self.assertIn('exact carrier',result.failure.message)
        self.assertIs(owner._operation._owned,publication); self.assertEqual(owner.snapshot(),before)
        self.emit('carrier_contract_rejection',before,owner,result,declared,
            failure_stage='admission',target_reference_object=self.obj(target.to_payload()),
            preserved_target_reference_object=self.obj(original.to_payload()),
            changed_field='tau_PC',unchanged_history_not_silently_reset=True)


if __name__=='__main__':
    unittest.main()
