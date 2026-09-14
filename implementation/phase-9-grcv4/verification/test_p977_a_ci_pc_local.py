"""Exact A_CI_PC local product; implicit-root authority is not OS evidence."""

from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_a import CandidateAStageError, CandidateAWriter
from pygrc.models.grc_v4_ci import CandidateCIRoot, ProvisionalCandidateCIStep
from pygrc.models import grc_v4_ci as ci, grc_v4_step as step
from pygrc.models.grc_v4_step import ResourceBoundaryError
from pygrc.models.grc_v4_geometry import PhysicalFlux
from pygrc.models.grc_v4_lifecycle import _fresh_geometry
from tests.models import test_grc_v4 as catalog_helpers
from tests.models.test_grc_v4_generic_lifecycle import fixture
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference
from tests.models.test_grc_v4_cipc import independent_root as coupled_root, configure
from tests.models.test_grc_v4_ci import independent_point
from tests.models.test_grc_v4_pc import zoh_oracle
from pygrc.models import grc_v4_pc as pc

def independent_root(inputs, backend):
    h, j, source = coupled_root(inputs, backend)
    return j, h
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
import test_p977_a_pc_local as lifecycle_helpers

NOMINATED = 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689'


class ACIPCLocalProductTests(unittest.TestCase):
    obj = catalog_helpers.CompleteProfileCatalogTests.obj
    # Execute the same lifecycle assertions on A_CI_PC, not borrow A_OS outputs.
    test_fixed_profile_lifecycle_and_parent_ownership = lifecycle_helpers.APCLocalProductTests.test_fixed_profile_lifecycle_and_parent_ownership

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects, cls.pressure, cls.companions = [], {}, [], []
        cls.inputs, cls.backend = fixture('A_CI_PC')
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
                native_point = ci._point
                def injected(inputs, backend):
                    if inputs.current == self.inputs.current:
                        raise CandidateAStageError(error, 'test-only consumed CI solve fault')
                    return native_point(inputs, backend)
                with patch.object(ci, '_point', side_effect=injected):
                    result = owner.step_v4_input(declared)
                self.assertFalse(result.committed)
                self.assertEqual(result.solver_disposition, error)
            else:
                result = owner.step_v4_input(declared)
                self.assertEqual(result.committed, dt >= 0)
                if dt > 0:
                    current = float(independent_root(self.inputs, self.backend)[0][0])
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
        with patch.object(ci, '_point', wraps=ci._point) as calls:
            result = owner.step_v4_input(declared)
        self.assertTrue(result.committed)
        predictor = next(call.args[0] for call in calls.call_args_list if call.args[0].current == current)
        self.assertEqual(predictor.current, current)
        self.assertEqual((predictor.dt,predictor.operation_id), (declared.dt,'fresh-second'))
        self.assertEqual(predictor.geometry, predictor.geometry.reference.geometry())
        self.assertEqual(predictor.receipt_ids, tuple(r['receipt_id'] for r in before['receipt_ledger']))
        self.assertNotEqual(current, self.inputs.current)
        self.assertTrue(all(call.args[0].current.W_A == current.W_A for call in calls.call_args_list if call.args[0].current == current))
        bad = declared.to_payload(); bad['cache'] = {'current':[999]}
        with self.assertRaises(ValueError): GRCV4StepRequestInput.from_payload(bad)
        self.emit('COMMON-STALE-CACHE',before,owner,result,request=declared,
                  observation=dict(postcondition='cache_rebuilt_before_consumer', stale_value_never_consumed=True,
                                   predictor_inputs_object=self.obj(predictor.to_payload()), cache_input_rejected=True))

    def test_candidate_and_coupled_equations_with_distinct_control_ids(self):
        owner = self.model()
        before = owner.snapshot()
        oracle_j, oracle_h = independent_root(self.inputs, self.backend)
        points = []
        native = ci._point

        def observe(inputs, backend):
            point = native(inputs, backend)
            points.append(point)
            return point

        with patch.object(ci, '_point', side_effect=observe), \
             patch.object(ci, 'CandidateAWriter', wraps=CandidateAWriter) as writers, \
             patch.object(pc, 'scalar_zoh', wraps=pc.scalar_zoh) as zwriters:
            provisional = ProvisionalCandidateCIStep(self.inputs, self.backend)
        root, selected = provisional.root, provisional.root.selected
        self.assertEqual(writers.call_count, 1)
        self.assertEqual(provisional.resource.continuity_evaluations, 1)
        self.assertEqual(provisional.carrier_writes, 1)
        self.assertEqual(zwriters.call_count, 1)
        source = np.asarray(selected.structural_source.increment)
        np.testing.assert_allclose(source, coupled_root(self.inputs, self.backend)[2], rtol=0, atol=2e-11)
        self.assertEqual(zwriters.call_args.args[1], tuple(source.flat))
        expected_Z = zoh_oracle(self.inputs.current.Z_4, tuple(source.flat), self.inputs.dt, self.inputs.geometry.reference.profile.params_resolved.realization.tau_PC)
        np.testing.assert_allclose(provisional.next_inputs.current.Z_4, expected_Z, rtol=0, atol=2e-14)
        np.testing.assert_allclose(root.current.values, oracle_j, rtol=0, atol=2e-11)
        np.testing.assert_allclose(selected.inputs.geometry.one_form_hodge.matrix, oracle_h, rtol=0, atol=2e-11)
        bounds = primitive(root.certificate.bounds)
        self.assertLess(F(bounds['contraction_upper']), 1)
        self.assertLessEqual(F(bounds['displacement_upper']), F(bounds['radius']))
        self.assertLessEqual(selected.residual_squared, F(self.inputs.geometry.reference.profile.params_resolved.realization.tolerance)**2)
        trial_points = [p for p in points if p.inputs.current == self.inputs.current and p.inputs.stage == 'cipc_trial']
        self.assertGreater(len(trial_points), 1)
        for point in trial_points:
            self.assertEqual(point.inputs.current, self.inputs.current)
            desc, target = scalar_oracle(point.inputs.geometry.reference, self.backend,
                                         point.inputs.current.C, point.baseline.values)
            np.testing.assert_allclose(point.descriptors, desc, rtol=0, atol=2e-14)
            np.testing.assert_allclose(point.W_hat_A, target, rtol=0, atol=2e-14)
        # Nonzero gamma distinguishes W-hat evaluated at different trial J0.
        self.assertNotEqual(trial_points[0].W_hat_A, selected.point.W_hat_A)
        final_C = tuple(float(F(c) + sign*F(self.inputs.dt)*F(float(oracle_j[0])))
                        for c, sign in zip(self.inputs.current.C, (-1, 1)))
        np.testing.assert_allclose(provisional.next_inputs.current.C, final_C, rtol=0, atol=2e-13)
        writer = provisional.writer
        desc, target = scalar_oracle(self.inputs.geometry.reference, self.backend,
                                     provisional.resource.provisional_state.C, root.current.values)
        np.testing.assert_allclose(writer.descriptors, desc, rtol=0, atol=2e-14)
        np.testing.assert_allclose(writer.W_drv_A, target, rtol=0, atol=2e-14)
        expected_W = log_writer_oracle(self.inputs.current.W_A, target, self.inputs.dt, 1.)
        np.testing.assert_allclose(provisional.next_inputs.current.W_A, expected_W, rtol=0, atol=2e-14)
        self.assertNotEqual(writer.descriptors, selected.point.descriptors)
        self.assertNotEqual(provisional.next_inputs.current.W_A, self.inputs.current.W_A)
        self.assertEqual(provisional.restart.inputs.current, provisional.next_inputs.current)
        self.assertEqual(provisional.reset_root.inputs.current, self.inputs.reset)
        self.assertNotEqual(root.current, provisional.reset_root.current)
        bad_point = replace(selected.point, inputs=replace(selected.inputs,
            trial_current=PhysicalFlux(selected.inputs.geometry.reference.graph, (0.,))))
        with self.assertRaisesRegex(ValueError, 'selected root current'):
            CandidateAWriter(bad_point, provisional.resource)
        for w in (0., -1., float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                self.model(replace(self.inputs, current=replace(self.inputs.current, W_A=(w,))))
        self.assertEqual(owner.snapshot(), before)
        limited = configure(self.inputs, limit=1, tolerance=0.)
        with self.assertRaises(ci.CIStageError) as exhausted:
            CandidateCIRoot(limited, self.backend)
        self.assertEqual(exhausted.exception.disposition, 'no_admitted_root')
        common = dict(
            provisional_object=self.obj(provisional.to_payload()),
            selected_inputs_object=self.obj(selected.inputs.to_payload()),
            certificate=bounds, residual_squared=str(selected.residual_squared),
            root_evaluations=root.evaluations, writer_count=1, continuity_evaluations=1,
            carrier_writes=zwriters.call_count, source_policy='selected_root_source_held_once',
            composition_gain=2, rho_inst=1, source=source.tolist(),
            written_Z=list(provisional.next_inputs.current.Z_4),
            next_inputs_object=self.obj(provisional.next_inputs.to_payload()),
            reset_inputs_object=self.obj(provisional.reset_root.inputs.to_payload()),
            source_inputs_object=self.obj(self.inputs.to_payload()),
            current_stage_roster=sorted({p.inputs.stage for p in trial_points}),
            independent_oracle=dict(current=oracle_j.tolist(), hodge=oracle_h.tolist(),
                final_C=list(final_C), writer_descriptors=[list(x) for x in desc],
                W_drv=list(target), written_W=list(expected_W)),
            observed=dict(current=list(root.current.values),
                hodge=[list(x) for x in selected.inputs.geometry.one_form_hodge.matrix],
                selected_W_hat=list(selected.point.W_hat_A),
                writer_descriptors=[list(x) for x in writer.descriptors],
                W_drv=list(writer.W_drv_A), final_C=list(provisional.next_inputs.current.C),
                written_W=list(provisional.next_inputs.current.W_A),
                reset_current=list(provisional.reset_root.current.values),
                restart_current=list(provisional.restart.current.values)),
            trial_points=[dict(inputs_object=self.obj(p.inputs.to_payload()),
                J0=list(p.baseline.values), W_hat=list(p.W_hat_A),
                current=list(p.current.values)) for p in trial_points],
            stale_writer_trial_rejected=True, supplied_W_is_not_formation=True,
            invalid_W_rejected=['0.0', '-1.0', 'infinity', 'nan'],
            budget_control=dict(inputs_object=self.obj(limited.to_payload()),
                disposition=exhausted.exception.disposition,
                scope='root_construction_rejection_not_public_operation', fallback_used=False),
            branch_scope='analytic_local_reference_ball_not_global_uniqueness')
        for case in ('A-POSITIVE-W-ADMISSION', 'A-EXACT-PRE-READ-W-HAT',
                     'A-POST-CONTINUITY-REFRESH', 'A-LOG-WRITER',
                     'A-NO-SAME-BEAT-NEW-W-READ', 'A-INITIALIZATION-VS-FORMATION', 'CI-PC-SAME-SOURCE'):
            self.emit(case, before, owner, observation=common,
                layer='independent_equations_and_provisional_stage_not_public_commit')

        for field, case in (('chi_A','A-CHI-ZERO'), ('zeta_A','A-ZETA-ZERO')):
            ref = changed_reference(self.inputs.geometry.reference, 'candidate', **{field: 0.})
            control = _fresh_geometry(replace(self.inputs, geometry=ref.geometry()))
            changed = self.model(control)
            control_before = changed.snapshot()
            point = ProvisionalCandidateCIStep(control, self.backend)
            self.assertEqual(point.root.current, point.root.selected.point.baseline)
            self.assertEqual(point.root.selected.inputs.geometry, control.geometry)
            self.assertEqual(point.root.selected.structural_source.increment, ((0.,),))
            self.assertEqual(point.carrier_writes, 1)
            self.assertEqual(point.root.evaluations, 1)
            declared = request(control.dt, case)
            result = changed.step_v4_input(declared)
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(changed.state.lifecycle.current, point.next_inputs.current)
            self.assertNotEqual(ref.profile.complete_profile_id, NOMINATED)
            self.emit(case, control_before, changed, result, request=declared,
                observation=dict(control_parameter=field, control_value=0,
                    control_profile_id=ref.profile.complete_profile_id,
                    provisional_object=self.obj(point.to_payload()),
                    current=list(point.root.current.values),
                    baseline=list(point.root.selected.point.baseline.values),
                    control_is_not_new_supported_profile=True))


    def test_nonzero_history_same_source_and_release(self):
        subject = _fresh_geometry(replace(self.inputs,
            current=replace(self.inputs.current, Z_4=(-.25,)),
            reset=replace(self.inputs.reset, Z_4=(.125,))))
        for field in (None, 'chi_A', 'zeta_A'):
            inputs = subject
            if field:
                ref = changed_reference(subject.geometry.reference, 'candidate', **{field: 0.})
                inputs = _fresh_geometry(replace(subject, geometry=ref.geometry()))
            with patch.object(ci, 'CandidateAWriter', wraps=CandidateAWriter) as w, \
                 patch.object(pc, 'scalar_zoh', wraps=pc.scalar_zoh) as z:
                provisional = ProvisionalCandidateCIStep(inputs, self.backend)
            root = provisional.root
            h, current, source = coupled_root(inputs, self.backend)
            np.testing.assert_allclose(root.current.values, current, rtol=0, atol=2e-11)
            np.testing.assert_allclose(root.selected.inputs.geometry.one_form_hodge.matrix, h, rtol=0, atol=2e-11)
            expected = zoh_oracle(inputs.current.Z_4, tuple(source.flat), inputs.dt,
                                 inputs.geometry.reference.profile.params_resolved.realization.tau_PC)
            np.testing.assert_allclose(provisional.next_inputs.current.Z_4, expected, rtol=0, atol=2e-14)
            self.assertEqual((w.call_count,z.call_count,provisional.resource.continuity_evaluations),(1,1,1))
            np.testing.assert_allclose(z.call_args.args[1], tuple(source.flat), rtol=0, atol=2e-11)
            if field:
                self.assertEqual(root.current, root.selected.point.baseline)
                self.assertEqual(tuple(source.flat), (0.,))
                self.assertLess(inputs.current.Z_4[0], expected[0]); self.assertLess(expected[0], 0.)
                self.assertNotEqual(h.tolist(), [[1.]])
            else:
                post_source=coupled_root(provisional.next_inputs,self.backend)[2]
                self.assertFalse(np.allclose(source, post_source, rtol=0, atol=1e-10))
            roles=[]
            for role, admitted in (('reset',provisional.reset_root),('restart',provisional.restart)):
                rh,rj,rs=coupled_root(admitted.inputs,self.backend)
                np.testing.assert_allclose(admitted.current.values,rj,rtol=0,atol=2e-11)
                np.testing.assert_allclose(admitted.selected.inputs.geometry.one_form_hodge.matrix,rh,rtol=0,atol=2e-11)
                roles.append(dict(role=role,inputs_object=self.obj(admitted.inputs.to_payload()),
                    current=list(admitted.current.values),hodge=[list(v) for v in admitted.selected.inputs.geometry.one_form_hodge.matrix]))
            self.companions.append(dict(control_parameter=field,inputs_object=self.obj(inputs.to_payload()),
                next_inputs_object=self.obj(provisional.next_inputs.to_payload()),
                current=list(root.current.values),hodge=[list(v) for v in root.selected.inputs.geometry.one_form_hodge.matrix],
                source=[list(v) for v in root.selected.structural_source.increment],written_Z=list(provisional.next_inputs.current.Z_4),
                writer_count=w.call_count,carrier_writes=z.call_count,continuity_evaluations=1,roles=roles,
                scope='same_nomination_history_companion' if field is None else 'distinct_zero_gate_control_not_support'))

    def test_late_readmission_and_reset_failure_keep_both_histories(self):
        for role in ('reset', 'restart'):
            owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
            declared = request(self.inputs.dt, 'injected-'+role)
            native = ci.CandidateCIRoot
            def fail(inputs, backend):
                if (role == 'reset' and inputs.current == self.inputs.reset) or (
                        role == 'restart' and inputs.current != self.inputs.current and inputs.current != self.inputs.reset):
                    raise CandidateAStageError('no_admitted_root', 'test-only '+role+' readmission')
                return native(inputs, backend)
            with patch.object(ci, 'CandidateCIRoot', side_effect=fail), \
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


if __name__ == '__main__':
    unittest.main()
