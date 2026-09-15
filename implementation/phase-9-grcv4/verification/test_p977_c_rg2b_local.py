"""Exact C_RG2b local product: frozen completion, not CI or persistent geometry."""

from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError, _c_condition
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection, ProvisionalCandidateRG2bStep, RG2bStageError
from pygrc.models import grc_v4_rg2b as rg, grc_v4_step as step
from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_generic_lifecycle import fixture
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference
from tests.models.test_grc_v4_rg2b_graph import independent_maps
from tests.models.test_grc_v4_candidate_c import dense_current_oracle, p943_direction, p943_centered, p943_fixture
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge, GRCV4Graph, OrientedEdge, PhysicalFlux
from pygrc.models.grc_v4_codec import canonical_json_bytes
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_migration import rehash_receipt_chain
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

NOMINATED = 'grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0'


def observed_chain(point):
    a=point.algebra
    return {k:np.asarray(v).tolist() for k,v in dict(projector=a.selector.projector,
        sector=a.selector.selected.values,hm=a.retained_hodge.matrix,phi=a.potential.values,
        j0=a.baseline.values,ident=a.identification,q=a.physical_identification,
        current=point.current.values,read=point.read.flux.values).items()}


def oracle(inputs, backend, h):
    delta, source, current = independent_maps(inputs, None, np.array(inputs.current.C), np.array(h))
    return dict(current=current.tolist(), source=source.tolist(), final_C=(np.array(inputs.current.C)+delta).tolist())


def inverse_oracle(inputs, backend):
    """Two literal transforms; check every inverse remains in cutoff-one K."""
    x = np.array(inputs.current.C)
    href = np.array(inputs.geometry.reference.geometry().one_form_hodge.matrix)
    d = RG2bGraphDomain.from_identity(inputs.geometry.reference.profile.params_resolved.realization.extension_evaluator_id)
    center = np.array([d.center_C]*len(inputs.current.C))
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


class CRG2bLocalProductTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects, cls.pressure = [], {}, []
        cls.inputs, cls.backend = fixture('C_RG2b')
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
                native = rg.CandidateCCurrent.__post_init__
                def fault(point):
                    inputs=point.inputs
                    if inputs.current == self.inputs.current:
                        raise CandidateCStageError(error, 'test-only consumed current fault')
                    return native(point)
                with patch.object(rg.CandidateCCurrent, '__post_init__', fault): result = owner.step_v4_input(declared)
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

    def test_candidate_and_section_equations_with_distinct_roles(self):
        owner=self.model(); before=owner.snapshot()
        with patch.object(rg,'CandidateAWriter',wraps=rg.CandidateAWriter) as writers:
            provisional=ProvisionalCandidateRG2bStep(self.inputs)
        self.assertEqual(writers.call_count,0); self.assertIsNone(provisional.writer)
        self.assertEqual(provisional.resource.continuity_evaluations,1)
        roles=[]
        for role,section,point in (('current',provisional.section,provisional.point),
                                  ('reset',provisional.reset_section,provisional.reset_point),
                                  ('restart',provisional.restart,provisional.restart_point)):
            h=np.array(section.geometry.one_form_hodge.matrix)
            expected=oracle(section.inputs,None,h); chain=observed_chain(point)
            dense=dense_current_oracle(point.inputs)
            for key in chain: np.testing.assert_allclose(chain[key],dense[key],rtol=0,atol=2e-13)
            independent_h=inverse_oracle(section.inputs,None); bounds=dict(section.certificate.bounds)
            self.assertLessEqual(np.linalg.norm(h-independent_h),float(F(section.error_upper)+F(bounds['section_radius'])*F(bounds['contraction_upper'])**2)+2e-15)
            np.testing.assert_allclose(point.current.values,expected['current'],rtol=0,atol=2e-13)
            self.assertEqual(point.inputs.stage,'rg2b_section')
            self.assertIsNone(point.inputs.current.W_A);self.assertIsNone(point.inputs.current.Z_4)
            with self.assertRaisesRegex(RG2bStageError,'Lipschitz-only'):section.classical_jacobian()
            roles.append(dict(role=role,inputs_object=self.obj(section.inputs.to_payload()),
                selected_inputs_object=self.obj(point.inputs.to_payload()),h=h.tolist(),inverse_oracle_h=independent_h.tolist(),
                current=list(point.current.values),chain=chain,certificate=bounds,error_upper=section.error_upper,
                levels=section.levels,evaluations=section.evaluations))
        expected=oracle(self.inputs,None,provisional.section.geometry.one_form_hodge.matrix)
        np.testing.assert_allclose(provisional.next_inputs.current.C,expected['final_C'],rtol=0,atol=2e-13)
        np.testing.assert_allclose(provisional.generated.one_form_hodge.matrix,np.array(self.inputs.geometry.one_form_hodge.matrix)+self.inputs.geometry.reference.profile.params_resolved.geometry.kappa_H*np.array(expected['source']),rtol=0,atol=2e-14)
        self.assertNotEqual(roles[0]['chain']['j0'],roles[1]['chain']['j0'])
        self.assertNotEqual(roles[0]['chain']['j0'],roles[2]['chain']['j0'])
        self.assertEqual(CandidateRG2bSection(self.inputs).geometry,provisional.section.geometry)
        declared=request(self.inputs.dt,'equation-beat');result=owner.step_v4_input(declared)
        self.assertTrue(result.committed,result.failure)
        self.assertEqual(owner.state.lifecycle.current,provisional.next_inputs.current)
        observation=dict(roles=roles,observed=dict(current=list(provisional.point.current.values),
            source=((np.array(provisional.generated.one_form_hodge.matrix)-np.array(self.inputs.geometry.one_form_hodge.matrix))/self.inputs.geometry.reference.profile.params_resolved.geometry.kappa_H).tolist(),
            final_C=list(provisional.next_inputs.current.C)),final_inputs_object=self.obj(provisional.next_inputs.to_payload()),
            generated_h=[list(v) for v in provisional.generated.one_form_hodge.matrix],diagnostics=dict(provisional.diagnostics),
            writer_count=0,deterministic_reconstruction=True,classical_derivative_rejected=True,
            section_scope='bounded_completion_relative_Lipschitz_only',global_base_invariance_claimed=False,CI_root_claimed=False)
        # The source is measured from the generated geometry in addition to the
        # independent dense pushforward; it is not an extra public execution.
        for case in ('RG2B-SECTION','C-POST-CONTINUITY-REDERIVATION'):
            self.emit(case,before,owner,result,request=declared,observation=observation)

    def test_candidate_fixed_stage_and_exact_controls(self):
        inputs=self.inputs;owner=self.model();before=owner.snapshot();point=CandidateCCurrent(inputs)
        a=point.algebra;observed=observed_chain(point);expected=dense_current_oracle(inputs)
        def row(case,**extra):
            self.emit(case,before,owner,layer='fixed_stage_no_operation',observation=dict(
                stage_inputs_object=self.obj(inputs.to_payload()),point_object=self.obj(point.to_payload()),**extra))
        for key in observed:np.testing.assert_allclose(observed[key],expected[key],rtol=0,atol=2e-13)
        row('C-BASELINE-EXACT',observed=observed,independent_oracle={k:expected[k].tolist() for k in observed})
        h=np.array(inputs.geometry.one_form_hodge.matrix);graph=inputs.geometry.reference.graph
        hcontrol=replace(inputs,geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(graph,tuple(map(tuple,h+np.eye(3)*.01)))))
        hp=CandidateCCurrent(hcontrol)
        self.assertEqual(a.transport.mobility.diagonal,hp.algebra.transport.mobility.diagonal)
        self.assertNotEqual(a.transport.mobility_constructor_identity,a.transport.structural_hodge_constructor_identity)
        self.assertNotEqual(a.baseline.values,hp.algebra.baseline.values)
        row('C-TR-REFERENCE-MAP',E_H=a.transport.structural_hodge_constructor_identity,E_M=a.transport.mobility_constructor_identity,
            mobility=list(a.transport.mobility.diagonal),changed_h_inputs_object=self.obj(hcontrol.to_payload()),mobility_unchanged=True)
        self.assertEqual(a.selector.rank,4)
        row('C-SELECTOR-STRICT-GAP',rank=a.selector.rank,certificate=dict(a.selector.certificate),
            spectrum=np.linalg.eigvalsh(np.array(graph.incidence)@h@np.array(graph.incidence).T).tolist(),cutoff=100.)
        boundary=replace(inputs,geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(graph,tuple(map(tuple,50*np.eye(3))))))
        with self.assertRaisesRegex(CandidateCStageError,'exact spectrum') as failure:CandidateCCurrent(boundary)
        row('C-SELECTOR-BOUNDARY',inputs_object=self.obj(boundary.to_payload()),diagnostic=failure.exception.disposition,
            scope='fixed_stage_selector_rejection_outside_completion_not_public_operation')
        np.testing.assert_allclose(a.physical_identification,np.array(a.identification)@a.flat_matrix,rtol=0,atol=1e-14)
        row('C-QC-TYPING',I_4M=a.identification,G_J=a.flat_matrix,Q_C=a.physical_identification)
        _c_condition(((.5,0),(0,1)),2,'retained')
        with self.assertRaisesRegex(ValueError,'conditioning'):_c_condition(((.5,5),(0,1)),2,'physical similarity')
        row('C-RETAINED-VS-PHYSICAL-CONDITIONING',certificates=[dict(c) for c in a.certificates],
            scope='nominated_matrix_certificates_plus_algebra_only_similarity_counterexample',
            counterexample=dict(retained=[[.5,0],[0,1]],physical=[[.5,5],[0,1]],limit=2,physical_rejected=True))
        for field in ('W_A','Z_4'):
            with self.assertRaises(ValueError):self.model(replace(inputs,current=replace(inputs.current,**{field:(1.,)*3})))
        row('C-C-ONLY-AUTHORITY',C=list(inputs.current.C),W_A=None,Z_4=None,invalid_history_rejected=['W_A','Z_4'])
        ref=changed_reference(inputs.geometry.reference,'candidate',kappa_M_C=0.)
        zero=replace(inputs,geometry=ref.geometry());zp=CandidateCCurrent(zero)
        self.assertEqual(zp.algebra.retained_hodge,zero.geometry.one_form_hodge)
        self.assertEqual(zp.algebra.transport.mobility.diagonal,a.transport.mobility.diagonal)
        row('C-KAPPA-M-ZERO',control_inputs_object=self.obj(zero.to_payload()),deformation=list(zp.algebra.deformation),
            retained_hodge=zp.algebra.retained_hodge.matrix,mobility=list(zp.algebra.transport.mobility.diagonal),control_is_nominated_support=False)
        derivatives=[]
        dc=(.2,-.1,.3,-.2);dh=((.1,.05,0),(.05,-.05,.02),(0,.02,.1))
        for subject,direction,geometry in ((inputs,dc,dh),(p943_fixture(),(.2,-.1,.3),((.1,.05),(.05,-.05)))):
            analytic=p943_direction(subject,direction,geometry);finite=p943_centered(subject,direction,geometry,2**-12)
            for key in ('projector','sector','deformation','hm','phi','j0'):
                np.testing.assert_allclose(analytic[key],finite[key],rtol=2e-6,atol=2e-7)
            derivatives.append(dict(inputs_object=self.obj(subject.to_payload()),dc=direction,dh=geometry,epsilon=2**-12,
                analytic={k:analytic[k].tolist() for k in ('projector','sector','deformation','hm','phi','j0')},
                finite={k:finite[k].tolist() for k in ('projector','sector','deformation','hm','phi','j0')}))
        signed_graph=GRCV4Graph(graph.live_node_ids,tuple(OrientedEdge(e.edge_id,e.head_node_id,e.tail_node_id) for e in graph.oriented_edges))
        signed=replace(inputs,geometry=replace(inputs.geometry.reference,graph=signed_graph).geometry())
        signed_point=CandidateCCurrent(signed);signed_d=p943_direction(signed,dc,dh)['j0']
        np.testing.assert_allclose(signed_point.algebra.baseline.values,-np.asarray(a.baseline.values),rtol=0,atol=1e-13)
        np.testing.assert_allclose(signed_d,-np.asarray(derivatives[0]['analytic']['j0']),rtol=0,atol=1e-13)
        row('C-BASELINE-DERIVATIVE-COVARIANCE',derivatives=derivatives,signed_inputs_object=self.obj(signed.to_payload()),
            signed_J0=list(signed_point.algebra.baseline.values),signed_delta_J0=signed_d.tolist(),
            scope='fixed_candidate_stratum_derivative_not_RG_section_derivative',partial_selector_control_not_nominated=True)
        for field,value,case in (('chi_C',0.,'C-CHI-ZERO'),('zeta_C',0.,'C-ZETA-ZERO'),('chi_C',.2,'C-ONE-CHI-GATE')):
            ref=changed_reference(inputs.geometry.reference,'candidate',**{field:value});control=replace(inputs,geometry=ref.geometry())
            cp=CandidateCCurrent(control);want=dense_current_oracle(control)
            for key,actual in observed_chain(cp).items():np.testing.assert_allclose(actual,want[key],rtol=0,atol=2e-13)
            step_control=None
            if value==0:
                step_control=ProvisionalCandidateRG2bStep(control)
                self.assertEqual(step_control.point.current,step_control.point.algebra.baseline)
                self.assertEqual(step_control.section.geometry,ref.geometry());self.assertEqual(step_control.generated,ref.geometry())
            else:
                fixed=PhysicalFlux(graph,point.current.values)
                np.testing.assert_allclose(cp.read_back(fixed).flux.values,2*np.array(point.read.flux.values),rtol=0,atol=2e-13)
            row(case,control_inputs_object=self.obj(control.to_payload()),control_complete_profile_id=ref.profile.complete_profile_id,
                control_J=list(cp.current.values),control_J0=list(cp.algebra.baseline.values),control_read=list(cp.read.flux.values),
                zero_section_h=None if step_control is None else step_control.section.geometry.one_form_hodge.matrix,
                zero_generated_h=None if step_control is None else step_control.generated.one_form_hodge.matrix,
                zero_next_inputs_object=None if step_control is None else self.obj(step_control.next_inputs.to_payload()),
                fixed_J_chi_ratio=2 if value else None,control_is_nominated_support=False)

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
            native = rg.CandidateCCurrent.__post_init__; hit=[]
            def fault(point):
                inputs = point.inputs
                if (label=='reset_native' and inputs.current==self.inputs.reset or
                    label=='restart_native' and inputs.step_index>self.inputs.step_index):
                    hit.append(inputs.stage)
                    raise CandidateCStageError('no_admitted_root', 'test-only readmission fault')
                return native(point)
            with patch.object(rg.CandidateCCurrent, '__post_init__', fault), \
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
            self.assertEqual(writers.call_count, 0)
            self.pressure.append(dict(case=label, scope='public_operation_test_fault' if label!='wrong_beat' else 'public_operation',
                prestate_object=self.obj(before), poststate_object=self.obj(owner.snapshot()),
                request_object=self.obj(declared.to_payload()), result_object=None if result is None else self.obj(primitive(result)),
                failure_stage=None if result is None else result.failure.stage, writer_count=writers.call_count,
                whole_publication_unchanged=True, fallback_used=False))


    def test_fixed_profile_lifecycle_and_parent_ownership(self):
        owner=self.model()
        self.assertNotEqual(self.inputs.current,self.inputs.reset)
        first=owner.step_v4_input(request(self.inputs.dt,'lifecycle-first'))
        self.assertTrue(first.committed)
        before=owner.snapshot()
        clone=owner.duplicate()
        with TemporaryDirectory(prefix='c-rg2b-state-') as directory:
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
        exported['reset']['authoritative']['C'][0]=999
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



if __name__ == '__main__': unittest.main()
