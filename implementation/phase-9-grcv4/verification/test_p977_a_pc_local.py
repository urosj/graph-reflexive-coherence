"""Exact A_PC local product: old Z read, separate W and Z writes, no G2."""

from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_a import CandidateAStageError, CandidateAWriter
from pygrc.models import grc_v4_pc as pc, grc_v4_step as step
from pygrc.models.grc_v4_step import ResourceBoundaryError
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_lifecycle import _fresh_geometry
from tests.models import test_grc_v4 as catalog_helpers
from tests.models.test_grc_v4_generic_lifecycle import fixture, restore
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference, rehash_receipt_chain
from tests.models.test_grc_v4_ci import independent_point
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
from tests.models.test_grc_v4_pc import zoh_oracle

NOMINATED = 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75'


def old_h(inputs):
    ref = inputs.geometry.reference
    n = len(ref.graph.live_edge_ids)
    return np.asarray(ref.pairings.one_form.matrix) + ref.profile.params_resolved.geometry.kappa_H * np.asarray(inputs.current.Z_4).reshape(n, n)


def independent_beat(inputs, backend):
    """Dense current/source plus separate literal W/Z ODE solutions."""
    ref = inputs.geometry.reference
    h = old_h(inputs)
    j, source = independent_point(inputs, backend, h)
    b = np.asarray(ref.graph.incidence)
    c = tuple(float(F(v) - F(inputs.dt)*sum(F(float(b[i,k]))*F(float(j[k])) for k in range(len(j))))
              for i,v in enumerate(inputs.current.C))
    descriptors, target = scalar_oracle(ref, backend, c, tuple(j))
    w = log_writer_oracle(inputs.current.W_A, target, inputs.dt, ref.profile.params_resolved.candidate.tau_A)
    z = zoh_oracle(inputs.current.Z_4, tuple(source.flat), inputs.dt, ref.profile.params_resolved.realization.tau_PC)
    return dict(h=h.tolist(), current=j.tolist(), source=source.tolist(), final_C=list(c),
                writer_descriptors=[list(x) for x in descriptors], W_drv=list(target), written_W=list(w), written_Z=list(z))


class APCLocalProductTests(unittest.TestCase):
    obj = catalog_helpers.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects, cls.pressure = [], {}, []
        cls.inputs, cls.backend = fixture('A_PC')
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
                native_point = pc.CandidatePCRead
                def injected(inputs, backend):
                    if inputs.current == self.inputs.current:
                        raise CandidateAStageError(error, 'test-only consumed PC read fault')
                    return native_point(inputs, backend)
                with patch.object(pc, 'CandidatePCRead', side_effect=injected):
                    result = owner.step_v4_input(declared)
                self.assertFalse(result.committed)
                self.assertEqual(result.solver_disposition, error)
            else:
                result = owner.step_v4_input(declared)
                self.assertEqual(result.committed, dt >= 0)
                if dt > 0:
                    current = float(independent_point(self.inputs, self.backend, np.array(self.inputs.geometry.one_form_hodge.matrix))[0][0])
                    expected = tuple(float(F(c) + sign * F(dt)*F(current)) for c,sign in zip(self.inputs.current.C,(-1,1)))
                    np.testing.assert_allclose(owner.state.lifecycle.current.C, expected, rtol=0, atol=2e-13)
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
        with patch.object(pc, 'CandidatePCRead', wraps=pc.CandidatePCRead) as calls:
            result = owner.step_v4_input(declared)
        self.assertTrue(result.committed)
        predictor = next(call.args[0] for call in calls.call_args_list if call.args[0].current == current)
        self.assertEqual(predictor.current, current)
        self.assertEqual((predictor.dt,predictor.operation_id), (declared.dt,'fresh-second'))
        self.assertEqual(predictor.geometry, pc.carrier_geometry(predictor, current))
        self.assertEqual(predictor.receipt_ids, tuple(r['receipt_id'] for r in before['receipt_ledger']))
        self.assertNotEqual(current, self.inputs.current)
        self.assertTrue(all(call.args[0].current.W_A == current.W_A for call in calls.call_args_list if call.args[0].current == current))
        bad = declared.to_payload(); bad['cache'] = {'current':[999]}
        with self.assertRaises(ValueError): GRCV4StepRequestInput.from_payload(bad)
        self.emit('COMMON-STALE-CACHE',before,owner,result,request=declared,
                  observation=dict(postcondition='cache_rebuilt_before_consumer', stale_value_never_consumed=True,
                                   predictor_inputs_object=self.obj(predictor.to_payload()), cache_input_rejected=True))


    def test_candidate_and_PC_equations_with_distinct_control_ids(self):
        owner = self.model()
        before = owner.snapshot()
        stages = []
        # Same exact nomination, different authoritative histories. The signed
        # nonzero companion discriminates old-carrier geometry from H_ref.
        history = _fresh_geometry(replace(self.inputs,
            current=replace(self.inputs.current, Z_4=(-0.25,)),
            reset=replace(self.inputs.reset, Z_4=(0.125,))))
        for label, inputs in (('nomination_seed', self.inputs), ('signed_history_companion', history)):
            expected = independent_beat(inputs, self.backend)
            native_writer, native_zoh = pc.CandidateAWriter, pc.scalar_zoh
            with patch.object(pc, 'CandidateAWriter', wraps=native_writer) as writers, \
                 patch.object(pc, 'scalar_zoh', wraps=native_zoh) as carriers:
                value = pc.ProvisionalCandidatePCStep(inputs, self.backend)
            point, writer = value.read.point, value.writer
            self.assertEqual((writers.call_count, carriers.call_count), (1, 1))
            self.assertEqual(value.resource.continuity_evaluations, 1)
            self.assertEqual(value.carrier_writes, 1)
            self.assertEqual(point.inputs.stage, 'pc_old_history')
            self.assertEqual(point.inputs.current, inputs.current)
            self.assertEqual(writer.authority.state.Z_4, inputs.current.Z_4)
            self.assertEqual(value.reset_read.inputs.current, inputs.reset)
            self.assertEqual(value.next_inputs.reset, inputs.reset)
            self.assertEqual(value.restart.inputs.current, value.next_inputs.current)
            self.assertNotEqual(value.restart.inputs.geometry, point.inputs.geometry)
            self.assertNotEqual(value.reset_read.inputs.geometry, point.inputs.geometry)
            self.assertNotEqual(value.next_inputs.current.W_A, inputs.current.W_A)
            self.assertNotEqual(writer.descriptors, point.descriptors)
            self.assertNotEqual(value.next_inputs.current.Z_4, inputs.current.Z_4)
            observed = dict(h=[list(r) for r in point.inputs.geometry.one_form_hodge.matrix],
                current=list(point.current.values), source=[list(r) for r in value.read.structural_source.increment],
                final_C=list(value.next_inputs.current.C), writer_descriptors=[list(r) for r in writer.descriptors],
                W_drv=list(writer.W_drv_A), written_W=list(value.next_inputs.current.W_A),
                written_Z=list(value.next_inputs.current.Z_4))
            for key in observed:
                np.testing.assert_allclose(observed[key], expected[key], rtol=2e-12, atol=2e-14)
            desc, target = scalar_oracle(inputs.geometry.reference, self.backend, inputs.current.C, point.baseline.values)
            np.testing.assert_allclose(point.descriptors, desc, rtol=0, atol=2e-14)
            np.testing.assert_allclose(point.W_hat_A, target, rtol=0, atol=2e-14)
            self.assertEqual(carriers.call_args.args[0], inputs.current.Z_4)
            self.assertEqual(carriers.call_args.args[1], tuple(x for r in value.read.structural_source.increment for x in r))
            # Native readmissions on both reset and post-write current histories
            # have independent fixed-h current expectations, not just matching recipes.
            admissions = []
            for role, read in (('reset', value.reset_read), ('restart', value.restart)):
                hj = old_h(read.inputs)
                jj, _ = independent_point(read.inputs, self.backend, hj)
                np.testing.assert_allclose(read.point.current.values, jj, rtol=2e-12, atol=2e-14)
                np.testing.assert_allclose(read.inputs.geometry.one_form_hodge.matrix, hj, rtol=0, atol=2e-14)
                admissions.append(dict(role=role, inputs_object=self.obj(read.inputs.to_payload()),
                    current=list(read.point.current.values), h=hj.tolist()))
            stages.append(dict(label=label, inputs_object=self.obj(inputs.to_payload()),
                provisional_object=self.obj(value.to_payload()), observed=observed, independent_oracle=expected,
                pre_descriptors=[list(r) for r in point.descriptors], pre_W_hat=list(point.W_hat_A),
                pre_J0=list(point.baseline.values), writer_old_Z=list(writer.authority.state.Z_4),
                next_inputs_object=self.obj(value.next_inputs.to_payload()), admissions=admissions,
                certificate=dict(value.read.certificate.bounds), writer_count=writers.call_count,
                carrier_writes=carriers.call_count, continuity_evaluations=value.resource.continuity_evaluations))

        bad_weights = []
        for w in (0., -1., float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                self.model(replace(self.inputs, current=replace(self.inputs.current, W_A=(w,))))
            bad_weights.append('nan' if w != w else 'infinity' if w == float('inf') else str(w))
        self.assertEqual(owner.snapshot(), before)
        common = dict(stages=stages, supplied_W_is_not_formation=True, invalid_W_rejected=bad_weights,
            source_policy='held_old_prestate_source_not_post_continuity_refresh',
            scope='exact_profile_seed_and_same_profile_signed_history; no_matched_forcing_contraction_claim')
        for case in ('A-POSITIVE-W-ADMISSION', 'A-EXACT-PRE-READ-W-HAT', 'A-POST-CONTINUITY-REFRESH',
                     'A-LOG-WRITER', 'A-NO-SAME-BEAT-NEW-W-READ', 'A-INITIALIZATION-VS-FORMATION', 'PC-ZOH'):
            self.emit(case, before, owner, observation=common,
                layer='independent_equations_and_provisional_stage_not_public_commit')

        for field, case in (('chi_A', 'A-CHI-ZERO'), ('zeta_A', 'A-ZETA-ZERO')):
            ref = changed_reference(history.geometry.reference, 'candidate', **{field:0.})
            control = _fresh_geometry(replace(history, geometry=ref.geometry()))
            changed = self.model(control); control_before = changed.snapshot()
            value = pc.ProvisionalCandidatePCStep(control, self.backend)
            self.assertEqual(value.read.point.current, value.read.point.baseline)
            self.assertEqual(value.read.structural_source.increment, ((0.,),))
            self.assertEqual(value.read.inputs.geometry, control.geometry)
            expected_z = zoh_oracle(control.current.Z_4, (0.,), control.dt, ref.profile.params_resolved.realization.tau_PC)
            self.assertEqual(value.next_inputs.current.Z_4, expected_z)
            self.assertNotEqual(expected_z, control.current.Z_4)
            self.assertNotEqual(expected_z, (0.,))  # Native release is not reset/drop.
            declared = request(control.dt, case)
            result = changed.step_v4_input(declared)
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(changed.state.lifecycle.current, value.next_inputs.current)
            self.assertNotEqual(ref.profile.complete_profile_id, NOMINATED)
            self.emit(case, control_before, changed, result, request=declared,
                observation=dict(control_parameter=field, control_value=0,
                    control_profile_id=ref.profile.complete_profile_id, inputs_object=self.obj(control.to_payload()),
                    current=list(value.read.point.current.values), baseline=list(value.read.point.baseline.values),
                    source=[[0.]], written_Z=list(expected_z), zero_source_release_not_reset=True,
                    control_is_not_new_supported_profile=True))

    def test_late_readmission_and_reset_failure_keep_both_histories(self):
        for role in ('reset', 'restart'):
            owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
            declared = request(self.inputs.dt, 'injected-'+role)
            native = pc.CandidatePCRead
            def fail(inputs, backend):
                if (role == 'reset' and inputs.current == self.inputs.reset) or (
                        role == 'restart' and inputs.current != self.inputs.current and inputs.current != self.inputs.reset):
                    raise CandidateAStageError('no_admitted_root', 'test-only '+role+' readmission')
                return native(inputs, backend)
            with patch.object(pc, 'CandidatePCRead', side_effect=fail), \
                 patch.object(pc, 'scalar_zoh', wraps=pc.scalar_zoh) as writes:
                result = owner.step_v4_input(declared)
            self.assertFalse(result.committed)
            self.assertEqual(result.solver_disposition, None if role == 'reset' else 'valid_root')
            self.assertEqual(result.failure.code, 'no_admitted_root')
            self.assertEqual(result.failure.stage, 'pre_read_reconstruction' if role == 'reset' else 'final_reconstruction')
            self.assertEqual(writes.call_count, 0 if role == 'reset' else 1)
            self.assertEqual(owner.snapshot(), before)
            self.assertIs(owner._operation._owned, owned)
            self.pressure.append(dict(role=role, fault='test_only_native_readmission_fault',
                prestate_object=self.obj(before), poststate_object=self.obj(owner.snapshot()),
                request_object=self.obj(declared.to_payload()), result_object=self.obj(primitive(result)),
                carrier_writes_before_rejection=writes.call_count, whole_publication_unchanged=True))

    def test_fixed_profile_lifecycle_and_parent_ownership(self):
        owner=self.model()
        self.assertNotEqual(self.inputs.current,self.inputs.reset)
        first=owner.step_v4_input(request(self.inputs.dt,'lifecycle-first'))
        self.assertTrue(first.committed)
        before=owner.snapshot()
        clone=owner.duplicate()
        with TemporaryDirectory(prefix='a-pc-state-') as directory:
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
        exported['reset']['authoritative']['Z_4'][0]=999
        exported['scientific_state']['authoritative']['Z_4'][0]=999
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
