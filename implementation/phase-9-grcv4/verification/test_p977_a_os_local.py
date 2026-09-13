"""Exact A_OS local catalog product; crossings are a separate reconciliation."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_a import CandidateACurrent, CandidateAStageError, CandidateAWriter
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep, ResourceBoundaryError
from pygrc.models import grc_v4_realizations as realization, grc_v4_step as step
from pygrc.models.grc_v4_lifecycle import _fresh_geometry
from tests.models import test_grc_v4 as catalog_helpers
from tests.models.test_grc_v4_generic_lifecycle import fixture, restore
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference, rehash_receipt_chain
from tests.models.test_grc_v4_realizations import a_scalar_pass
from tests.models.test_grc_v4_candidate_a import log_writer_oracle

NOMINATED = 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4'


class AOSLocalProductTests(unittest.TestCase):
    # Reuse the existing exact-input/result recorder, without inheriting its C tests.
    obj = catalog_helpers.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}
        cls.inputs, cls.backend = fixture('A_OS')
        assert cls.inputs.geometry.reference.profile.complete_profile_id == NOMINATED

    def model(self, inputs=None):
        return GRCV4(self.inputs if inputs is None else inputs, differential_reference=self.backend)

    def emit(self, *args, **kwargs):
        catalog_helpers.CompleteProfileCatalogTests.emit(self, *args, **kwargs)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_common_exact_profile_product(self):
        for case, dt, error in (
            ('COMMON-VALID-ORDINARY-STEP', self.inputs.dt, None),
            ('COMMON-INVALID-DOMAIN', self.inputs.dt, 'domain_failure'),
            ('COMMON-NONFINITE', self.inputs.dt, 'nonfinite'),
            ('COMMON-ZERO-DURATION', 0, None),
            ('COMMON-NEGATIVE-DURATION', -1, None),
        ):
            owner = self.model()
            before, owned = owner.snapshot(), owner._operation._owned
            declared = request(dt, case)
            if error:
                with patch.object(realization, 'CandidateACurrent', side_effect=CandidateAStageError(error, 'test-only typed solver fault')):
                    result = owner.step_v4_input(declared)
                self.assertFalse(result.committed)
                self.assertEqual(result.solver_disposition, error)
            else:
                result = owner.step_v4_input(declared)
                self.assertEqual(result.committed, dt >= 0)
                if dt > 0:
                    current = float(a_scalar_pass(self.inputs)['corrector'][1])
                    expected = tuple(float(F(c) + sign * F(dt)*F(current)) for c,sign in zip(self.inputs.current.C,(-1,1)))
                    self.assertEqual(owner.state.lifecycle.current.C, expected)
                    self.assertEqual(result.solver_disposition, 'valid_root')
                elif dt == 0:
                    self.assertEqual(owner.snapshot()['scientific_state'], before['scientific_state'])
                    self.assertEqual(owner.state.lifecycle.current, self.inputs.current)
                    self.assertEqual(result.observables['continuity_evaluations'], 0)
                else:
                    self.assertEqual(result.failure.code, 'invalid_duration')
                    self.assertIsNone(result.solver_disposition)
            if not result.committed:
                self.assertEqual(owner.snapshot(), before)
                self.assertIs(owner._operation._owned, owned)
            self.emit(case, before, owner, result, request=declared,
                      fault=None if error is None else 'test_only_A_solve_' + error)

        owner = self.model()
        before, owned = owner.snapshot(), owner._operation._owned
        declared = request(self.inputs.dt, 'charge-fault')
        native = step._resource_charge

        def charge(*args, **kwargs):
            if len(args) > 2 and args[2] == 'charge_admission':
                raise ResourceBoundaryError('charge_admission', 'charge_failure', 'test-only postsolve charge fault')
            return native(*args, **kwargs)

        with patch.object(step, '_resource_charge', side_effect=charge):
            result = owner.step_v4_input(declared)
        self.assertFalse(result.committed)
        self.assertEqual((result.solver_disposition, result.failure.code), ('valid_root','charge_failure'))
        self.assertEqual(owner.snapshot(), before)
        self.assertIs(owner._operation._owned, owned)
        for case in ('COMMON-CHARGE-MISMATCH','COMMON-ATOMIC-FAILURE'):
            self.emit(case,before,owner,result,request=declared,
                      fault='same_test_only_postsolve_charge_execution',
                      observation=dict(shared_execution='charge-fault', full_publication_unchanged=True))

        owner = self.model()
        first = owner.step_v4_input(request(self.inputs.dt, 'first'))
        self.assertTrue(first.committed)
        before = owner.snapshot()
        current = owner.state.lifecycle.current
        stale = owner.compute_observables()
        stale['authoritative_current'] = {'values': [999]}
        declared = request(self.inputs.dt/2, 'fresh-second')
        with patch.object(realization, 'CandidateACurrent', wraps=CandidateACurrent) as calls:
            result = owner.step_v4_input(declared)
        self.assertTrue(result.committed)
        predictor = calls.call_args_list[0].args[0]
        self.assertEqual(predictor.current, current)
        self.assertEqual((predictor.dt,predictor.operation_id), (declared.dt,'fresh-second'))
        self.assertEqual(predictor.geometry, predictor.geometry.reference.geometry())
        self.assertEqual(predictor.receipt_ids, tuple(r['receipt_id'] for r in before['receipt_ledger']))
        self.assertNotEqual(result.observables['os']['current'], first.observables['os']['current'])
        bad = declared.to_payload(); bad['cache'] = {'current':[999]}
        with self.assertRaises(ValueError): GRCV4StepRequestInput.from_payload(bad)
        self.emit('COMMON-STALE-CACHE',before,owner,result,request=declared,
                  observation=dict(postcondition='cache_rebuilt_before_consumer', stale_value_never_consumed=True,
                                   predictor_inputs_object=self.obj(predictor.to_payload()), cache_input_rejected=True))

    def test_candidate_and_OS_equations_with_distinct_control_ids(self):
        owner = self.model()
        before = owner.snapshot()
        expected = a_scalar_pass(self.inputs)
        with patch.object(realization, 'CandidateACurrent', wraps=CandidateACurrent) as currents, \
             patch.object(step, 'CandidateAWriter', wraps=CandidateAWriter) as writers:
            provisional = ProvisionalCandidateAOSStep(self.inputs, self.backend)
        self.assertEqual([x.args[0].stage for x in currents.call_args_list], ['os_predictor','os_corrector'])
        self.assertEqual(writers.call_count, 1)
        passed = provisional.os_pass
        for actual,want in ((passed.predictor.current.values[0],expected['predictor'][1]),
                            (passed.corrector.current.values[0],expected['corrector'][1]),
                            (passed.corrector.inputs.geometry.one_form_hodge.matrix[0][0],expected['h']),
                            (passed.residual.values[0][0],expected['residual'])):
            self.assertAlmostEqual(actual,float(want),delta=2e-14)
        self.assertEqual(provisional.resource.continuity_evaluations,1)
        self.assertEqual(provisional.next_inputs.current.W_A,log_writer_oracle(self.inputs.current.W_A,(1.,),self.inputs.dt,1.))
        self.assertNotEqual(provisional.next_inputs.current.W_A,self.inputs.current.W_A)
        self.assertNotEqual(provisional.writer.descriptors,passed.corrector.descriptors)
        self.assertEqual(provisional.final.inputs.current,provisional.next_inputs.current)
        self.assertEqual(provisional.restart.inputs.current,provisional.next_inputs.current)
        for point in (passed.predictor,passed.corrector):
            self.assertEqual(point.inputs.current.W_A,self.inputs.current.W_A)
            self.assertEqual(point.W_hat_A,(1.,))
        bad_weights=[]
        for w in (0.,-1.,float('inf'),float('nan')):
            with self.assertRaises(ValueError):
                self.model(replace(self.inputs,current=replace(self.inputs.current,W_A=(w,))))
            bad_weights.append('nan' if w!=w else 'infinity' if w==float('inf') else str(w))
        self.assertEqual(owner.snapshot(),before)
        common=dict(provisional_object=self.obj(provisional.to_payload()),
                    scalar_oracle={k:[str(x) for x in v] if isinstance(v,tuple) else str(v) for k,v in expected.items()},
                    observed=dict(predictor_J=list(passed.predictor.current.values),
                                  corrector_J=list(passed.corrector.current.values),
                                  predictor_W_hat=list(passed.predictor.W_hat_A),
                                  corrector_W_hat=list(passed.corrector.W_hat_A),
                                  consumed_H=[list(x) for x in passed.corrector.inputs.geometry.one_form_hodge.matrix],
                                  split_residual=[list(x) for x in passed.residual.values],
                                  corrector_descriptors=[list(x) for x in passed.corrector.descriptors],
                                  writer_descriptors=[list(x) for x in provisional.writer.descriptors],
                                  W_drv=list(provisional.writer.W_drv_A),
                                  final_C=list(provisional.next_inputs.current.C),
                                  written_W=list(provisional.next_inputs.current.W_A),
                                  final_J=list(provisional.final.current.values),
                                  restart_J=list(provisional.restart.current.values)),
                    current_stage_roster=['os_predictor','os_corrector'], writer_count=1,
                    supplied_W_is_not_formation=True, invalid_W_rejected=bad_weights)
        for case in ('A-POSITIVE-W-ADMISSION','A-EXACT-PRE-READ-W-HAT','A-POST-CONTINUITY-REFRESH',
                     'A-LOG-WRITER','A-NO-SAME-BEAT-NEW-W-READ','A-INITIALIZATION-VS-FORMATION','OS-ONE-PASS'):
            self.emit(case,before,owner,observation=common,layer='independent_equations_and_provisional_stage_not_public_commit')

        for field,case in (('chi_A','A-CHI-ZERO'),('zeta_A','A-ZETA-ZERO')):
            ref=changed_reference(self.inputs.geometry.reference,'candidate',**{field:0.})
            control=_fresh_geometry(replace(self.inputs,geometry=ref.geometry()))
            changed=self.model(control)
            control_before=changed.snapshot()
            point=ProvisionalCandidateAOSStep(control,self.backend)
            self.assertEqual(point.os_pass.corrector.current,point.os_pass.corrector.baseline)
            self.assertEqual(point.os_pass.corrector.inputs.geometry,control.geometry)
            self.assertEqual(point.os_pass.residual.values,((0.,),))
            declared=request(control.dt,case)
            result=changed.step_v4_input(declared)
            self.assertTrue(result.committed)
            self.assertEqual(changed.state.lifecycle.current,point.next_inputs.current)
            self.assertNotEqual(ref.profile.complete_profile_id,NOMINATED)
            self.emit(case,control_before,changed,result,request=declared,
                      observation=dict(control_parameter=field,control_value=0,
                                       control_profile_id=ref.profile.complete_profile_id,
                                       provisional_object=self.obj(point.to_payload()),
                                       current=list(point.os_pass.corrector.current.values),
                                       baseline=list(point.os_pass.corrector.baseline.values),
                                       control_is_not_new_supported_profile=True))

    def test_fixed_profile_lifecycle_and_parent_ownership(self):
        owner=self.model()
        self.assertNotEqual(self.inputs.current,self.inputs.reset)
        first=owner.step_v4_input(request(self.inputs.dt,'lifecycle-first'))
        self.assertTrue(first.committed)
        before=owner.snapshot()
        clone=owner.duplicate()
        with TemporaryDirectory(prefix='a-os-state-') as directory:
            path=Path(directory)/'state.json'
            owner.save(str(path)); self.assertEqual(path.read_bytes(),canonical_json_bytes(before))
            loaded=GRCV4.load(str(path))
        self.assertEqual(loaded.snapshot(),before)
        declared=request(self.inputs.dt,'replay')
        result=owner.step_v4_input(declared)
        self.assertTrue(result.committed)
        self.assertEqual(loaded.step_v4_input(declared),result)
        self.assertEqual(loaded.snapshot(),owner.snapshot())
        self.assertEqual(clone.snapshot(),before)
        self.emit('SNAPSHOT-LOAD-REPLAY',before,owner,result,request=declared,
                  observation=dict(saved_snapshot_object=self.obj(before), exact_result_and_loaded_replay=True))
        for receipt in result.emitted_receipts:
            self.assertEqual(tuple(receipt.identity_payload['core']['parent_receipt_ids']),(first.emitted_receipts[0].receipt_id,))
        hostile=owner.snapshot()
        for receipt in hostile['receipt_ledger'][-4:]:
            receipt['identity_payload']['core']['parent_receipt_ids']=[]
        rehash_receipt_chain(hostile)
        with self.assertRaisesRegex(ValueError,'previous-successful-primary'):
            restore(hostile)
        self.emit('RECEIPT-OWNERSHIP',before,owner,result,request=declared,
                  observation=dict(shared_execution='replay', previous_primary=first.emitted_receipts[0].receipt_id,
                                   coherent_missing_parent_rejected=True))
        before_reset=owner.snapshot(); state=owner.state.lifecycle
        self.assertNotEqual(state.current,state.reset.authoritative)
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current,state.reset.authoritative)
        self.assertEqual((owner.state.lifecycle.time,owner.state.lifecycle.step_index),(state.time,state.step_index))
        self.assertEqual(owner.snapshot()['receipt_ledger'][:-4],before_reset['receipt_ledger'])
        self.emit('RESET-AFTER-ORDINARY',before_reset,owner,
                  observation=dict(independent_reset_authority=primitive(self.inputs.reset)))
        stable=clone.snapshot(); exported=clone.snapshot()
        exported['reset']['authoritative']['W_A'][0]=999
        exported['scientific_state']['authoritative']['C'][0]=999
        exported['receipt_ledger'].clear(); exported['commit_records'].clear()
        self.assertEqual(clone.snapshot(),stable)
        clone.rebase_reset_baseline()
        self.assertEqual(owner.state.lifecycle.current,self.inputs.reset)
        self.assertEqual(restore(owner.snapshot()).snapshot(),owner.snapshot())
        self.assertEqual(restore(clone.snapshot()).snapshot(),clone.snapshot())
        self.emit('DUPLICATION-INDEPENDENCE',stable,clone,
                  observation=dict(original_owner_snapshot_object=self.obj(owner.snapshot()),
                                   exported_mutations_detached=True, independently_rebased_clone=True))


if __name__ == '__main__':
    unittest.main()
