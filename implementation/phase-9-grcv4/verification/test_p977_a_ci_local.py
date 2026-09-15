"""Exact A_CI local product; implicit-root authority is not OS evidence."""

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
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_migration import changed_reference
from tests.models.test_grc_v4_ci import independent_root, configure
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
import test_p977_a_os_local as lifecycle_helpers

NOMINATED = 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'


class ACILocalProductTests(unittest.TestCase):
    obj = catalog_helpers.CompleteProfileCatalogTests.obj
    # Execute the same lifecycle assertions on A_CI, not borrow A_OS outputs.
    test_fixed_profile_lifecycle_and_parent_ownership = lifecycle_helpers.AOSLocalProductTests.test_fixed_profile_lifecycle_and_parent_ownership

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}
        cls.inputs, cls.backend = fixture('A_CI')
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

    def test_candidate_and_CI_equations_with_distinct_control_ids(self):
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
             patch.object(ci, 'CandidateAWriter', wraps=CandidateAWriter) as writers:
            provisional = ProvisionalCandidateCIStep(self.inputs, self.backend)
        root, selected = provisional.root, provisional.root.selected
        self.assertEqual(writers.call_count, 1)
        self.assertEqual(provisional.resource.continuity_evaluations, 1)
        self.assertEqual(provisional.carrier_writes, 0)
        np.testing.assert_allclose(root.current.values, oracle_j, rtol=0, atol=2e-11)
        np.testing.assert_allclose(selected.inputs.geometry.one_form_hodge.matrix, oracle_h, rtol=0, atol=2e-11)
        bounds = dict(root.certificate.bounds)
        self.assertLess(F(bounds['contraction_upper']), 1)
        self.assertLessEqual(F(bounds['displacement_upper']), F(bounds['radius']))
        self.assertLessEqual(selected.residual_squared, F(self.inputs.geometry.reference.profile.params_resolved.realization.tolerance)**2)
        trial_points = [p for p in points if p.inputs.current == self.inputs.current and p.inputs.stage == 'ci_trial']
        self.assertGreater(len(trial_points), 1)
        for point in trial_points:
            self.assertEqual(point.inputs.current.W_A, self.inputs.current.W_A)
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
                     'A-NO-SAME-BEAT-NEW-W-READ', 'A-INITIALIZATION-VS-FORMATION', 'CI-BRANCH'):
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


if __name__ == '__main__':
    unittest.main()
