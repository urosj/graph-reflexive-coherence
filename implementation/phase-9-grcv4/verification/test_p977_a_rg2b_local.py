"""Exact A_RG2b local product: frozen completion, not CI or persistent geometry."""

from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_a import CandidateAStageError
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection, ProvisionalCandidateRG2bStep, RG2bStageError
from pygrc.models import grc_v4_rg2b as rg, grc_v4_step as step
from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_generic_lifecycle import fixture
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference
from tests.models.test_grc_v4_rg2b_graph import independent_maps
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
from test_p977_a_os_local import AOSLocalProductTests

NOMINATED = 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'


def oracle(inputs, backend, h):
    """Dense candidate/continuity/log-writer equations, no RG evaluator calls."""
    x = np.array(inputs.current.C + inputs.current.W_A)
    delta, source, current = independent_maps(inputs, backend, x, np.array(h))
    n = len(inputs.current.C)
    descriptors, target = scalar_oracle(inputs.geometry.reference, backend, inputs.current.C,
                                      # Pre-read descriptors use baseline, not selected current.
                                      _baseline(inputs, h))
    final_c = tuple((x + delta)[:n])
    writer_desc, writer_target = scalar_oracle(inputs.geometry.reference, backend, final_c, tuple(current))
    return dict(current=current.tolist(), source=source.tolist(), final_C=list(final_c),
                W_hat=list(target), descriptors=[list(v) for v in descriptors],
                writer_descriptors=[list(v) for v in writer_desc], W_drv=list(writer_target),
                written_W=list(log_writer_oracle(inputs.current.W_A, writer_target, inputs.dt,
                    inputs.geometry.reference.profile.params_resolved.candidate.tau_A)))


def _baseline(inputs, h):
    # Literal Candidate A potential on this unit-vertex-pairing nomination.
    ref = inputs.geometry.reference
    b = np.array(ref.graph.incidence, dtype=float)
    c = np.array(inputs.current.C)
    h0 = np.array(ref.pairings.one_form.matrix, dtype=float)
    par = ref.profile.params_resolved.candidate
    w = np.array(inputs.current.W_A)
    potential = par.kappa_c*b@np.diag(w)@b.T@c + par.kappa_Ah*b@(np.array(h)-h0)@b.T@c
    return tuple(-par.eta*w*(b.T@potential))


def inverse_oracle(inputs, backend):
    """Two literal transforms; check every inverse remains in cutoff-one K."""
    x = np.array(inputs.current.C + inputs.current.W_A)
    href = np.array(inputs.geometry.reference.geometry().one_form_hodge.matrix)
    d = RG2bGraphDomain.from_identity(inputs.geometry.reference.profile.params_resolved.realization.extension_evaluator_id)
    center = np.array([d.center_C]*len(inputs.current.C)+[d.center_W]*len(inputs.current.W_A))
    gain = inputs.geometry.reference.profile.params_resolved.geometry.kappa_H
    def evaluate(level, target):
        if level == 0: return href
        mid = target.copy()
        for _ in range(10):
            if np.max(np.abs(mid-center)) > d.core: raise ValueError('oracle inverse left cutoff-one K')
            h = evaluate(level-1, mid)
            delta, source, _ = independent_maps(inputs, backend, mid, h)
            following = target-delta
            if np.max(np.abs(mid-following)) < 1e-15: return href+gain*source
            mid = following
        raise ValueError('independent inverse did not converge')
    return evaluate(2, x)


class ARG2bLocalProductTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj
    test_fixed_profile_lifecycle_and_parent_ownership = AOSLocalProductTests.test_fixed_profile_lifecycle_and_parent_ownership

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects, cls.pressure = [], {}, []
        cls.inputs, cls.backend = fixture('A_RG2b')
        assert cls.inputs.geometry.reference.profile.complete_profile_id == NOMINATED

    def model(self, inputs=None):
        return GRCV4(self.inputs if inputs is None else inputs, differential_reference=self.backend)

    def emit(self, *args, **kwargs):
        recorder.CompleteProfileCatalogTests.emit(self, *args, **kwargs)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_common_exact_profile_product(self):
        for case, dt, error in (
            ('COMMON-VALID-ORDINARY-STEP', self.inputs.dt, None),
            ('COMMON-INVALID-DOMAIN', self.inputs.dt, 'domain_failure'),
            ('COMMON-NONFINITE', self.inputs.dt, 'nonfinite'),
            ('COMMON-ZERO-DURATION', 0, None), ('COMMON-NEGATIVE-DURATION', -1, None)):
            owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
            declared = request(dt, case)
            if error:
                native = rg.CandidateACurrent
                def fault(inputs, backend):
                    if inputs.current == self.inputs.current:
                        raise CandidateAStageError(error, 'test-only consumed current fault')
                    return native(inputs, backend)
                with patch.object(rg, 'CandidateACurrent', side_effect=fault): result = owner.step_v4_input(declared)
                self.assertFalse(result.committed)
                self.assertEqual(result.failure.stage, 'candidate_solve')
            else:
                result = owner.step_v4_input(declared)
                self.assertEqual(result.committed, dt >= 0)
                if dt == 0:
                    self.assertEqual(owner.snapshot()['scientific_state'], before['scientific_state'])
                    self.assertEqual(result.observables['continuity_evaluations'], 0)
                elif dt < 0: self.assertEqual(result.failure.code, 'invalid_duration')
            if not result.committed:
                self.assertEqual(owner.snapshot(), before); self.assertIs(owner._operation._owned, owned)
            self.emit(case, before, owner, result, request=declared, fault=None if not error else 'test_only_'+error)
        owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
        native = step._resource_charge
        def charge(*args, **kwargs):
            if len(args)>2 and args[2]=='charge_admission':
                raise ResourceBoundaryError('charge_admission', 'charge_failure', 'test-only charge fault')
            return native(*args, **kwargs)
        declared = request(self.inputs.dt, 'charge-fault')
        with patch.object(step, '_resource_charge', side_effect=charge): result = owner.step_v4_input(declared)
        self.assertFalse(result.committed); self.assertEqual(result.failure.code, 'charge_failure')
        self.assertEqual(owner.snapshot(), before); self.assertIs(owner._operation._owned, owned)
        for case in ('COMMON-CHARGE-MISMATCH', 'COMMON-ATOMIC-FAILURE'):
            self.emit(case, before, owner, result, request=declared, fault='same_test_only_charge_execution')
        owner = self.model(); self.assertTrue(owner.step_v4_input(request(self.inputs.dt, 'first')).committed)
        before = owner.snapshot(); current = owner.state.lifecycle.current
        stale = owner.compute_observables(); stale['authoritative_current'] = {'values':[999]}
        declared = request(self.inputs.dt, 'fresh-second')  # Frozen beat, not dt/2.
        with patch.object(rg, 'CandidateRG2bSection', wraps=CandidateRG2bSection) as calls:
            result = owner.step_v4_input(declared)
        self.assertTrue(result.committed, result.failure)
        consumed = next(c.args[0] for c in calls.call_args_list if c.args[0].current == current)
        self.assertEqual(consumed.operation_id, 'fresh-second')
        self.assertEqual(consumed.geometry, consumed.geometry.reference.geometry())
        self.assertEqual(consumed.receipt_ids, tuple(r['receipt_id'] for r in before['receipt_ledger']))
        self.assertNotEqual(current, self.inputs.current)
        bad = declared.to_payload(); bad['cache'] = {'section':[999]}
        with self.assertRaises(ValueError): GRCV4StepRequestInput.from_payload(bad)
        self.emit('COMMON-STALE-CACHE', before, owner, result, request=declared,
                  observation=dict(postcondition='cache_rebuilt_before_consumer', stale_value_never_consumed=True,
                                   consumed_inputs_object=self.obj(consumed.to_payload()), cache_input_rejected=True))

    def test_candidate_and_section_equations_with_distinct_controls(self):
        owner = self.model(); before = owner.snapshot()
        with patch.object(rg, 'CandidateAWriter', wraps=rg.CandidateAWriter) as writers:
            provisional = ProvisionalCandidateRG2bStep(self.inputs, self.backend)
        self.assertEqual(writers.call_count, 1)
        self.assertEqual(provisional.resource.continuity_evaluations, 1)
        roles = []
        for role, section, point in (('current', provisional.section, provisional.point),
                                    ('reset', provisional.reset_section, provisional.reset_point),
                                    ('restart', provisional.restart, provisional.restart_point)):
            h = np.array(section.geometry.one_form_hodge.matrix)
            expected = oracle(section.inputs, self.backend, h)
            independent_h = inverse_oracle(section.inputs, self.backend)
            bounds = dict(section.certificate.bounds)
            tail = float(F(bounds['section_radius'])*F(bounds['contraction_upper'])**2)
            self.assertLessEqual(np.linalg.norm(h-independent_h), float(F(section.error_upper))+tail+2e-15)
            np.testing.assert_allclose(point.current.values, expected['current'], rtol=0, atol=2e-13)
            np.testing.assert_allclose(point.W_hat_A, expected['W_hat'], rtol=0, atol=2e-13)
            np.testing.assert_allclose(point.descriptors, expected['descriptors'], rtol=0, atol=2e-13)
            self.assertEqual(point.inputs.stage, 'rg2b_section')
            self.assertIsNone(point.inputs.current.Z_4)
            with self.assertRaisesRegex(RG2bStageError, 'Lipschitz-only'): section.classical_jacobian()
            roles.append(dict(role=role, inputs_object=self.obj(section.inputs.to_payload()),
                              selected_inputs_object=self.obj(point.inputs.to_payload()),
                              h=h.tolist(), inverse_oracle_h=independent_h.tolist(),
                              current=list(point.current.values), W_hat=list(point.W_hat_A),
                              descriptors=[list(v) for v in point.descriptors], certificate=bounds,
                              error_upper=section.error_upper, levels=section.levels, evaluations=section.evaluations))
        expected = oracle(self.inputs, self.backend, provisional.section.geometry.one_form_hodge.matrix)
        for key, actual in (('final_C', provisional.next_inputs.current.C), ('written_W', provisional.next_inputs.current.W_A),
                            ('writer_descriptors', provisional.writer.descriptors), ('W_drv', provisional.writer.W_drv_A)):
            np.testing.assert_allclose(actual, expected[key], rtol=0, atol=2e-13)
        np.testing.assert_allclose(provisional.generated.one_form_hodge.matrix,
            np.array(self.inputs.geometry.one_form_hodge.matrix)+self.inputs.geometry.reference.profile.params_resolved.geometry.kappa_H*np.array(expected['source']), rtol=0, atol=2e-14)
        self.assertNotEqual(provisional.writer.descriptors, provisional.point.descriptors)
        self.assertNotEqual(provisional.next_inputs.current.W_A, self.inputs.current.W_A)
        self.assertEqual(provisional.point.inputs.current, self.inputs.current)
        self.assertEqual(provisional.reset_point.inputs.current, self.inputs.reset)
        self.assertEqual(provisional.restart_point.inputs.current, provisional.next_inputs.current)
        self.assertEqual(CandidateRG2bSection(self.inputs, self.backend).geometry, provisional.section.geometry)
        for bad in (0., -1., float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                self.model(replace(self.inputs, current=replace(self.inputs.current, W_A=(bad,)*3)))
        declared = request(self.inputs.dt, 'equation-beat')
        result = owner.step_v4_input(declared)
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.lifecycle.current, provisional.next_inputs.current)
        observed = dict(expected, current=list(provisional.point.current.values),
            W_hat=list(provisional.point.W_hat_A), descriptors=[list(v) for v in provisional.point.descriptors],
            final_C=list(provisional.next_inputs.current.C), written_W=list(provisional.next_inputs.current.W_A),
            writer_descriptors=[list(v) for v in provisional.writer.descriptors], W_drv=list(provisional.writer.W_drv_A))
        observation = dict(roles=roles, observed=observed, final_inputs_object=self.obj(provisional.next_inputs.to_payload()),
            generated_h=[list(v) for v in provisional.generated.one_form_hodge.matrix],
            diagnostics=dict(provisional.diagnostics), writer_count=1, supplied_W_is_not_formation=True,
            invalid_W_rejected=['0.0','-1.0','infinity','nan'], deterministic_reconstruction=True,
            classical_derivative_rejected=True, section_scope='bounded_completion_relative_Lipschitz_only',
            global_base_invariance_claimed=False, CI_root_claimed=False)
        for case in ('A-POSITIVE-W-ADMISSION','A-EXACT-PRE-READ-W-HAT','A-POST-CONTINUITY-REFRESH',
                     'A-LOG-WRITER','A-NO-SAME-BEAT-NEW-W-READ','A-INITIALIZATION-VS-FORMATION','RG2B-SECTION'):
            self.emit(case, before, owner, result, request=declared, observation=observation)
        for field, case in (('chi_A','A-CHI-ZERO'), ('zeta_A','A-ZETA-ZERO')):
            ref = changed_reference(self.inputs.geometry.reference, 'candidate', **{field:0.})
            control = replace(self.inputs, geometry=ref.geometry())
            changed = self.model(control); control_before = changed.snapshot()
            point = ProvisionalCandidateRG2bStep(control, self.backend)
            self.assertEqual(point.point.current, point.point.baseline)
            self.assertEqual(point.section.geometry, ref.geometry())
            self.assertEqual(point.generated, ref.geometry())
            declared = request(control.dt, case); result = changed.step_v4_input(declared)
            self.assertTrue(result.committed, result.failure)
            self.assertEqual(changed.state.lifecycle.current, point.next_inputs.current)
            self.emit(case, control_before, changed, result, request=declared,
                observation=dict(control_parameter=field, control_profile_id=ref.profile.complete_profile_id,
                    current=list(point.point.current.values), baseline=list(point.point.baseline.values),
                    section_h=[list(v) for v in point.section.geometry.one_form_hodge.matrix], no_carrier=True))

    def test_completion_and_readmission_rejections_are_atomic(self):
        for label in ('wrong_beat', 'reset_outside_inner', 'budget', 'reset_native', 'restart_native', 'late_publication'):
            owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
            declared = request(self.inputs.dt, label)
            if label == 'wrong_beat': declared = request(2*self.inputs.dt, label)
            if label in ('reset_outside_inner', 'budget'):
                # Construction-only controls, not nomination lifecycle executions.
                inputs = self.inputs
                if label == 'budget':
                    ref = changed_reference(inputs.geometry.reference, 'realization', iteration_limit=1)
                    inputs = replace(inputs, geometry=ref.geometry())
                else:
                    c = list(inputs.reset.C); c[0]+=0.25; c[-1]-=0.25
                    inputs = replace(inputs, reset=replace(inputs.reset, C=tuple(c)))
                with self.assertRaises(ValueError): self.model(inputs)
                self.pressure.append(dict(case=label, scope='construction_control_not_public_operation',
                    inputs_object=self.obj(inputs.to_payload()), rejected=True, fallback_used=False))
                continue
            native = rg.CandidateACurrent.__post_init__; hit=[]
            def fault(point):
                inputs = point.inputs
                if (label=='reset_native' and inputs.current==self.inputs.reset or
                    label=='restart_native' and inputs.step_index>self.inputs.step_index):
                    hit.append(inputs.stage)
                    raise CandidateAStageError('no_admitted_root', 'test-only readmission fault')
                return native(point)
            with patch.object(rg.CandidateACurrent, '__post_init__', fault), \
                 patch.object(rg, 'CandidateAWriter', wraps=rg.CandidateAWriter) as writers:
                if label=='late_publication':
                    with patch('pygrc.models.grc_v4_lifecycle._validate_publication', side_effect=RuntimeError('late publication')):
                        with self.assertRaisesRegex(RuntimeError, 'late publication'): owner.step_v4_input(declared)
                    result=None
                else:
                    result=owner.step_v4_input(declared); self.assertFalse(result.committed)
            self.assertEqual(owner.snapshot(), before); self.assertIs(owner._operation._owned, owned)
            expected={'wrong_beat':'admission','reset_native':'pre_read_reconstruction','restart_native':'final_reconstruction'}
            if result is not None: self.assertEqual(result.failure.stage, expected[label])
            if label.endswith('_native'): self.assertTrue(hit)
            self.assertEqual(writers.call_count, int(label in ('restart_native','late_publication')))
            self.pressure.append(dict(case=label, scope='public_operation_test_fault' if label!='wrong_beat' else 'public_operation',
                prestate_object=self.obj(before), poststate_object=self.obj(owner.snapshot()),
                request_object=self.obj(declared.to_payload()), result_object=None if result is None else self.obj(primitive(result)),
                failure_stage=None if result is None else result.failure.stage, writer_count=writers.call_count,
                whole_publication_unchanged=True, fallback_used=False))


if __name__ == '__main__': unittest.main()
