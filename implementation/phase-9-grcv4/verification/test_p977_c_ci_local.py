"""Exact C_CI local product; controls and fixed stages are not new support."""

from copy import deepcopy
from dataclasses import replace, fields
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError, _c_condition
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_ci import CandidateCIRoot, ProvisionalCandidateCIStep
from pygrc.models import grc_v4_ci as ci, grc_v4_step as step
from pygrc.models.grc_v4_step import ResourceBoundaryError
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge, GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_lifecycle import _fresh_geometry
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from tests.models import test_grc_v4 as catalog_helpers
from tests.models.test_grc_v4_generic_lifecycle import fixture, restore
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference, rehash_receipt_chain
from tests.models.test_grc_v4_ci import independent_root, scalar_c_bisection, configure
from tests.models.test_grc_v4_candidate_c import dense_current_oracle, p943_direction, p943_centered, current_fixture

NOMINATED = 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e'


class CCILocalProductTests(unittest.TestCase):
    obj = catalog_helpers.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}
        cls.inputs, cls.backend = fixture('C_CI')
        assert cls.inputs.geometry.reference.profile.complete_profile_id == NOMINATED
        assert cls.backend is None

    def model(self, inputs=None):
        return GRCV4(self.inputs if inputs is None else inputs)

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
                        raise CandidateCStageError(error, 'test-only consumed C CI solve fault')
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
                      fault=None if error is None else 'test_only_C_solve_' + error)

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

    def test_fixed_profile_lifecycle_and_parent_ownership(self):
        owner=self.model()
        self.assertNotEqual(self.inputs.current,self.inputs.reset)
        first=owner.step_v4_input(request(self.inputs.dt,'lifecycle-first'))
        self.assertTrue(first.committed)
        before=owner.snapshot()
        clone=owner.duplicate()
        with TemporaryDirectory(prefix='c-ci-state-') as directory:
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

    def test_candidate_fixed_stage_and_exact_controls(self):
        owner=self.model(); before=owner.snapshot(); inputs=self.inputs
        point=CandidateCCurrent(inputs); a=point.algebra; params=a.transport.params
        oracle=dense_current_oracle(inputs)
        observed=dict(projector=a.selector.projector, sector=a.selector.selected.values,
                      hm=a.retained_hodge.matrix, phi=a.potential.values, j0=a.baseline.values,
                      ident=a.identification, q=a.physical_identification,
                      current=point.current.values, read=point.read.flux.values)
        for key,actual in observed.items():
            np.testing.assert_allclose(actual,oracle[key],rtol=0,atol=2e-13)
        def row(name, **extra):
            self.emit(name,before,owner,layer='fixed_stage_no_operation',observation=dict(
                stage_inputs_object=self.obj(inputs.to_payload()),
                point_object=self.obj(point.to_payload()),**extra))
        self.assertEqual(dict(params.W_C_tr),{'e':2.})
        self.assertEqual(a.transport.mobility.diagonal,(1.,))
        self.assertNotEqual(a.transport.mobility_constructor_identity,a.transport.structural_hodge_constructor_identity)
        # H changes are not mobility inputs, even though both constructors use W_C_tr.
        hcontrol=replace(inputs,geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(inputs.geometry.reference.graph,((2.125,),))))
        hp=CandidateCCurrent(hcontrol)
        self.assertEqual(hp.algebra.transport.mobility_constructor_identity,a.transport.mobility_constructor_identity)
        self.assertEqual(hp.algebra.transport.mobility.diagonal,a.transport.mobility.diagonal)
        row('C-TR-REFERENCE-MAP',E_H=a.transport.structural_hodge_constructor_identity,
            E_M=a.transport.mobility_constructor_identity,mobility=list(a.transport.mobility.diagonal),
            changed_h_inputs_object=self.obj(hcontrol.to_payload()),mobility_unchanged=True)
        row('C-BASELINE-EXACT',observed={k:np.asarray(v).tolist() for k,v in observed.items()},
            independent_oracle={k:oracle[k].tolist() for k in observed})
        self.assertEqual(a.selector.rank,1)
        row('C-SELECTOR-STRICT-GAP',rank=1,spectrum=[0,4],cutoff=params.Lambda_C)
        boundary=replace(inputs,geometry=GRCV4Geometry(inputs.geometry.reference,OneFormHodge(inputs.geometry.reference.graph,((0.5,),))))
        with self.assertRaises(CandidateCStageError) as rejected: CandidateCCurrent(boundary)
        self.assertEqual(rejected.exception.disposition,'domain_failure')
        row('C-SELECTOR-BOUNDARY',inputs_object=self.obj(boundary.to_payload()),
            diagnostic=rejected.exception.disposition,scope='fixed_stage_selector_rejection_not_public_operation')
        np.testing.assert_allclose(a.physical_identification,np.asarray(a.identification)@np.asarray(a.flat_matrix),rtol=0,atol=1e-14)
        row('C-QC-TYPING',I_4M=a.identification,G_J=a.flat_matrix,Q_C=a.physical_identification)
        self.assertTrue(all(c['condition_upper_squared']=='1' for c in a.certificates))
        _c_condition(((0.5,0),(0,1)),2,'retained')
        with self.assertRaisesRegex(ValueError,'conditioning'):
            _c_condition(((0.5,5),(0,1)),2,'physical similarity')
        row('C-RETAINED-VS-PHYSICAL-CONDITIONING',certificates=[c.to_dict() for c in a.certificates],
            scope='one_dimensional_nomination_plus_explicit_algebra_only_similarity_counterexample',
            counterexample=dict(retained=[[0.5,0],[0,1]],physical=[[0.5,5],[0,1]],limit=2,physical_rejected=True))
        self.assertEqual([f.name for f in fields(inputs.current)],['C','W_A','Z_4'])
        self.assertIsNone(inputs.current.W_A);self.assertIsNone(inputs.current.Z_4)
        row('C-C-ONLY-AUTHORITY',C=list(inputs.current.C),W_A=None,Z_4=None)
        self.assertEqual(a.deformation,(1.,));self.assertEqual(a.retained_hodge,inputs.geometry.one_form_hodge)
        row('C-KAPPA-M-ZERO',deformation=list(a.deformation),retained_hodge=a.retained_hodge.matrix,
            mobility=list(a.transport.mobility.diagonal),scope='nomination_has_kappa_M_C_zero')
        # Baseline derivative: nominal and separately declared nonzero-deformation,
        # noncommuting three-node stratum. No control earns nomination execution.
        graph=GRCV4Graph(('a','b','c'),(OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c')))
        dense=configure(current_fixture(graph=graph,weights={'ab':2.,'bc':3.},resource=(3.,1.,2.),
            changes={'candidate':{'Lambda_C':3.,'kappa_M_C':0.2,'chi_C':0.05,'zeta_C':0.05}}))
        dense=replace(dense,geometry=GRCV4Geometry(dense.geometry.reference,OneFormHodge(graph,((2.2,0.1),(0.1,3.1)))))
        derivatives=[]
        for subject,dc,dh in ((inputs,(.25,-.125),((.25,),)),(dense,(.2,-.1,.3),((.1,.05),(.05,-.05)))):
            analytic=p943_direction(subject,dc,dh);finite=p943_centered(subject,dc,dh,2**-12)
            self.assertEqual(analytic['representation'],[])
            for key in ('projector','sector','deformation','hm','phi','j0'):
                np.testing.assert_allclose(analytic[key],finite[key],rtol=2e-6,atol=2e-7)
            derivatives.append(dict(inputs_object=self.obj(subject.to_payload()),dc=dc,dh=dh,epsilon=2**-12,
                analytic={k:analytic[k].tolist() for k in ('projector','sector','deformation','hm','phi','j0')},
                finite={k:finite[k].tolist() for k in ('projector','sector','deformation','hm','phi','j0')},
                complete_profile_id=subject.geometry.reference.profile.complete_profile_id))
        moved_graph=GRCV4Graph(('v','u'),(OrientedEdge('e','v','u'),))
        ref=replace(inputs.geometry.reference,graph=moved_graph)
        moved=replace(inputs,geometry=ref.geometry(),current=GRCV4AuthoritativeState(tuple(reversed(inputs.current.C)),None,None),
                      reset=GRCV4AuthoritativeState(tuple(reversed(inputs.reset.C)),None,None))
        moved_point=CandidateCCurrent(moved)
        np.testing.assert_allclose(moved_point.algebra.baseline.values,-np.asarray(a.baseline.values),rtol=0,atol=1e-13)
        signed=p943_direction(moved,(-.125,.25),((.25,),))['j0']
        np.testing.assert_allclose(signed,-np.asarray(derivatives[0]['analytic']['j0']),rtol=0,atol=1e-13)
        row('C-BASELINE-DERIVATIVE-COVARIANCE',derivatives=derivatives,
            signed_inputs_object=self.obj(moved.to_payload()),signed_delta_J0=signed.tolist(),
            dense_control_not_nominated=True)
        for field,value,name in (('chi_C',0.,'C-CHI-ZERO'),('zeta_C',0.,'C-ZETA-ZERO'),('chi_C',.5,'C-ONE-CHI-GATE')):
            ref=changed_reference(inputs.geometry.reference,'candidate',**{field:value})
            control=replace(inputs,geometry=ref.geometry()); cp=CandidateCCurrent(control)
            expected=dense_current_oracle(control)
            np.testing.assert_allclose(cp.current.values,expected['current'],rtol=0,atol=2e-13)
            np.testing.assert_allclose(cp.read.flux.values,expected['read'],rtol=0,atol=2e-13)
            root=None
            if value==0:
                root=CandidateCIRoot(control)
                self.assertEqual(root.current,root.selected.point.algebra.baseline)
                self.assertEqual(root.selected.inputs.geometry,control.geometry)
                self.assertEqual(root.evaluations,1)
            else:
                # Hold the input J fixed when checking that chi occurs once.
                from pygrc.models.grc_v4_geometry import PhysicalFlux
                j=PhysicalFlux(inputs.geometry.reference.graph,point.current.values)
                read=cp.read_back(j)
                np.testing.assert_allclose(read.flux.values,2*np.asarray(point.read.flux.values),rtol=0,atol=2e-13)
            row(name,control_inputs_object=self.obj(control.to_payload()),control_complete_profile_id=ref.profile.complete_profile_id,
                control_J=list(cp.current.values),control_J0=list(cp.algebra.baseline.values),control_read=list(cp.read.flux.values),
                independent_J=expected['current'].tolist(),independent_read=expected['read'].tolist(),
                zero_root_object=None if root is None else self.obj(root.to_payload()),
                fixed_J_chi_ratio=None if value==0 else 2,control_is_nominated_support=False)

    def test_CI_root_and_postcontinuity_rederivation(self):
        owner=self.model();before=owner.snapshot()
        expected_j,expected_h=scalar_c_bisection(self.inputs)
        trials=[];native=ci._point
        def observe(inputs,backend):
            point=native(inputs,backend);trials.append(point);return point
        with patch.object(ci,'_point',side_effect=observe):
            provisional=ProvisionalCandidateCIStep(self.inputs)
        root=provisional.root; selected=root.selected; bounds=dict(root.certificate.bounds)
        np.testing.assert_allclose(root.current.values,[expected_j],rtol=0,atol=2e-11)
        np.testing.assert_allclose(selected.inputs.geometry.one_form_hodge.matrix,[[expected_h]],rtol=0,atol=2e-11)
        self.assertLess(F(bounds['contraction_upper']),1)
        self.assertLessEqual(F(bounds['displacement_upper']),F(bounds['radius']))
        self.assertLessEqual(selected.residual_squared,F(self.inputs.geometry.reference.profile.params_resolved.realization.tolerance)**2)
        seen=[]
        for point in trials:
            if point.inputs.current!=self.inputs.current or point.inputs.stage!='ci_trial':continue
            oracle=dense_current_oracle(point.inputs)
            for actual,key in ((point.algebra.selector.selected.values,'sector'),(point.algebra.retained_hodge.matrix,'hm'),
                (point.algebra.potential.values,'phi'),(point.algebra.baseline.values,'j0'),(point.current.values,'current')):
                np.testing.assert_allclose(actual,oracle[key],rtol=0,atol=2e-12)
            seen.append(dict(inputs_object=self.obj(point.inputs.to_payload()),J0=list(point.algebra.baseline.values),
                current=list(point.current.values),sector=list(point.algebra.selector.selected.values)))
        self.assertGreater(len(seen),1)
        self.assertIsNone(provisional.writer);self.assertEqual(provisional.carrier_writes,0)
        self.assertEqual(provisional.resource.continuity_evaluations,1)
        expected_C=[float(F(c)+sign*F(self.inputs.dt)*F(expected_j)) for c,sign in zip(self.inputs.current.C,(-1,1))]
        np.testing.assert_allclose(provisional.next_inputs.current.C,expected_C,rtol=0,atol=2e-13)
        self.assertIsNone(provisional.next_inputs.current.W_A);self.assertIsNone(provisional.next_inputs.current.Z_4)
        self.assertEqual(provisional.reset_root.inputs.current,self.inputs.reset)
        self.assertEqual(provisional.restart.inputs.current,provisional.next_inputs.current)
        reset_j,reset_h=scalar_c_bisection(replace(self.inputs,current=self.inputs.reset))
        restart_j,restart_h=scalar_c_bisection(provisional.next_inputs)
        np.testing.assert_allclose(provisional.reset_root.current.values,[reset_j],rtol=0,atol=2e-11)
        np.testing.assert_allclose(provisional.restart.current.values,[restart_j],rtol=0,atol=2e-11)
        self.assertNotEqual(root.current,provisional.restart.current)
        limited=configure(self.inputs,limit=1,tolerance=0.)
        with self.assertRaises(ci.CIStageError) as exhausted:CandidateCIRoot(limited)
        self.assertEqual(exhausted.exception.disposition,'no_admitted_root')
        observation=dict(provisional_object=self.obj(provisional.to_payload()),certificate=bounds,
            selected_inputs_object=self.obj(selected.inputs.to_payload()),residual_squared=str(selected.residual_squared),
            root_evaluations=root.evaluations,trial_points=seen,writer_count=0,carrier_writes=0,continuity_evaluations=1,
            independent_oracle=dict(current=[expected_j],hodge=[[expected_h]],final_C=expected_C,reset_current=[reset_j],restart_current=[restart_j]),
            observed=dict(current=list(root.current.values),hodge=selected.inputs.geometry.one_form_hodge.matrix,
                final_C=list(provisional.next_inputs.current.C),reset_current=list(provisional.reset_root.current.values),restart_current=list(provisional.restart.current.values)),
            budget_control=dict(inputs_object=self.obj(limited.to_payload()),disposition='no_admitted_root',fallback_used=False,
                scope='root_construction_rejection_not_public_operation'),
            branch_scope='analytic_local_reference_ball_not_global_uniqueness',
            reset_and_restart_are_independent_admissions=True)
        for name in ('CI-BRANCH','C-POST-CONTINUITY-REDERIVATION'):
            self.emit(name,before,owner,layer='independent_equations_and_provisional_stage_not_public_commit',observation=observation)


if __name__=='__main__':
    unittest.main()
