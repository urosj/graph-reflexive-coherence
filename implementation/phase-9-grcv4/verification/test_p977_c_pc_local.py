"""Exact C_PC local product: complete baseline at old Z, no W writer, one held-source Z write, no G2."""

from dataclasses import replace, fields
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError, _c_condition
from pygrc.models import grc_v4_pc as pc, grc_v4_step as step
from pygrc.models.grc_v4_step import ResourceBoundaryError
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_lifecycle import _fresh_geometry
from tests.models import test_grc_v4 as catalog_helpers
from tests.models.test_grc_v4_generic_lifecycle import fixture, restore
from tests.models.test_grc_v4_lifecycle import request, primitive
from tests.models.test_grc_v4_migration import changed_reference, rehash_receipt_chain
from tests.models.test_grc_v4_ci import independent_point
from tests.models.test_grc_v4_candidate_c import dense_current_oracle, p943_direction, p943_centered, current_fixture
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge, GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from tests.models.test_grc_v4_pc import zoh_oracle, configure

NOMINATED = 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f'


def old_h(inputs):
    ref = inputs.geometry.reference
    n = len(ref.graph.live_edge_ids)
    return np.asarray(ref.pairings.one_form.matrix) + ref.profile.params_resolved.geometry.kappa_H * np.asarray(inputs.current.Z_4).reshape(n, n)


def independent_beat(inputs):
    h=old_h(inputs)
    j,source=independent_point(inputs,None,h)
    b=np.asarray(inputs.geometry.reference.graph.incidence)
    c=[float(F(v)-F(inputs.dt)*sum(F(float(b[i,k]))*F(float(j[k])) for k in range(len(j))))
       for i,v in enumerate(inputs.current.C)]
    z=zoh_oracle(inputs.current.Z_4,tuple(source.flat),inputs.dt,inputs.geometry.reference.profile.params_resolved.realization.tau_PC)
    return dict(h=h.tolist(),current=j.tolist(),source=source.tolist(),final_C=c,written_Z=list(z))


def observed_chain(point):
    a=point.algebra
    return {k:np.asarray(v).tolist() for k,v in dict(projector=a.selector.projector,
        sector=a.selector.selected.values,hm=a.retained_hodge.matrix,phi=a.potential.values,
        j0=a.baseline.values,ident=a.identification,q=a.physical_identification,
        current=point.current.values,read=point.read.flux.values).items()}




class CPCLocalProductTests(unittest.TestCase):
    obj = catalog_helpers.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects, cls.pressure = [], {}, []
        cls.inputs, cls.backend = fixture('C_PC')
        assert cls.inputs.geometry.reference.profile.complete_profile_id == NOMINATED

    def model(self, inputs=None):
        return GRCV4(self.inputs if inputs is None else inputs, differential_reference=self.backend)

    def emit(self, *args, **kwargs):
        catalog_helpers.CompleteProfileCatalogTests.emit(self, *args, **kwargs)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_PC_old_history_and_complete_C_readmissions(self):
        owner=self.model();before=owner.snapshot();stages=[]
        history=_fresh_geometry(replace(self.inputs,current=replace(self.inputs.current,Z_4=(-.25,)),
                                        reset=replace(self.inputs.reset,Z_4=(.125,))))
        for label,inputs in (('nomination_seed',self.inputs),('signed_history_companion',history)):
            expected=independent_beat(inputs)
            with patch.object(pc,'CandidateAWriter',wraps=pc.CandidateAWriter) as writers, \
                 patch.object(pc,'scalar_zoh',wraps=pc.scalar_zoh) as carriers:
                value=pc.ProvisionalCandidatePCStep(inputs)
            self.assertEqual((writers.call_count,carriers.call_count),(0,1))
            self.assertIsNone(value.writer)
            self.assertEqual((value.carrier_writes,value.resource.continuity_evaluations),(1,1))
            self.assertEqual(value.read.point.inputs.stage,'pc_old_history')
            self.assertEqual(value.read.inputs.current,inputs.current)
            self.assertEqual(value.reset_read.inputs.current,inputs.reset)
            self.assertEqual(value.next_inputs.reset,inputs.reset)
            self.assertEqual(value.restart.inputs.current,value.next_inputs.current)
            self.assertIsNone(value.next_inputs.current.W_A)
            self.assertNotEqual(value.next_inputs.current.Z_4,inputs.current.Z_4)
            self.assertNotEqual(value.restart.point.algebra.baseline.values,value.read.point.algebra.baseline.values)
            self.assertNotEqual(value.restart.structural_source.increment,value.read.structural_source.increment)
            observed=dict(h=np.asarray(value.read.inputs.geometry.one_form_hodge.matrix).tolist(),
                current=list(value.read.point.current.values),source=np.asarray(value.read.structural_source.increment).tolist(),
                final_C=list(value.next_inputs.current.C),written_Z=list(value.next_inputs.current.Z_4))
            for key in observed:np.testing.assert_allclose(observed[key],expected[key],rtol=2e-12,atol=2e-14)
            self.assertEqual(carriers.call_args.args[0],inputs.current.Z_4)
            self.assertEqual(carriers.call_args.args[1],tuple(x for r in value.read.structural_source.increment for x in r))
            chains=[]
            for role,read in (('consumed',value.read),('reset',value.reset_read),('restart',value.restart)):
                native=observed_chain(read.point);oracle=dense_current_oracle(read.point.inputs)
                for key in native:np.testing.assert_allclose(native[key],oracle[key],rtol=2e-12,atol=2e-14)
                np.testing.assert_allclose(read.inputs.geometry.one_form_hodge.matrix,old_h(read.inputs),rtol=0,atol=2e-14)
                chains.append(dict(role=role,inputs_object=self.obj(read.inputs.to_payload()),observed=native,
                    independent_oracle={k:oracle[k].tolist() for k in native}))
            self.assertNotEqual(chains[0]['observed']['current'],chains[1]['observed']['current'])
            stages.append(dict(label=label,inputs_object=self.obj(inputs.to_payload()),
                provisional_object=self.obj(value.to_payload()),next_inputs_object=self.obj(value.next_inputs.to_payload()),
                observed=observed,independent_oracle=expected,chains=chains,
                certificate=dict(value.read.certificate.bounds),writer_count=writers.call_count,
                carrier_writes=carriers.call_count,continuity_evaluations=value.resource.continuity_evaluations,
                held_source_not_restart_source=True))
        obs=dict(stages=stages,source_policy='held_old_prestate_source_not_post_continuity_refresh',
            candidate_history_or_W_writer=False,matched_forcing_contraction_claimed=False,
            indefinite_base_chart_invariance_claimed=False,
            scope='exact_profile_seed_and_same_profile_signed_history; separate_dense_fixed_stage_controls')
        for name in ('PC-ZOH','C-POST-CONTINUITY-REDERIVATION'):
            self.emit(name,before,owner,observation=obs,layer='independent_equations_and_provisional_stage_not_public_commit')

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
                        raise CandidateCStageError(error, 'test-only consumed PC read fault')
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


    def test_late_readmission_and_reset_failure_keep_both_histories(self):
        for role in ('reset', 'restart'):
            owner = self.model(); before, owned = owner.snapshot(), owner._operation._owned
            declared = request(self.inputs.dt, 'injected-'+role)
            native = pc.CandidatePCRead
            def fail(inputs, backend):
                if (role == 'reset' and inputs.current == self.inputs.reset) or (
                        role == 'restart' and inputs.current != self.inputs.current and inputs.current != self.inputs.reset):
                    raise CandidateCStageError('no_admitted_root', 'test-only '+role+' readmission')
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
        with TemporaryDirectory(prefix='c-pc-state-') as directory:
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
        self.assertIsNone(inputs.current.W_A);self.assertEqual(inputs.current.Z_4,(0.,))
        with self.assertRaises(ValueError):self.model(replace(inputs,current=replace(inputs.current,W_A=(1.,))))
        row('C-C-ONLY-AUTHORITY',C=list(inputs.current.C),W_A=None,Z_4=list(inputs.current.Z_4),
            scope='no_T_C_or_mobility_state; persistent_Z_is_realization_authority',invalid_A_history_rejected=True)
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
        moved=replace(inputs,geometry=ref.geometry(),current=GRCV4AuthoritativeState(tuple(reversed(inputs.current.C)),None,inputs.current.Z_4),
                      reset=GRCV4AuthoritativeState(tuple(reversed(inputs.reset.C)),None,inputs.reset.Z_4))
        moved_point=CandidateCCurrent(moved)
        np.testing.assert_allclose(moved_point.algebra.baseline.values,-np.asarray(a.baseline.values),rtol=0,atol=1e-13)
        signed=p943_direction(moved,(-.125,.25),((.25,),))['j0']
        np.testing.assert_allclose(signed,-np.asarray(derivatives[0]['analytic']['j0']),rtol=0,atol=1e-13)
        row('C-BASELINE-DERIVATIVE-COVARIANCE',derivatives=derivatives,
            signed_inputs_object=self.obj(moved.to_payload()),signed_delta_J0=signed.tolist(),
            dense_control_not_nominated=True)
        for field,value,name in (('chi_C',0.,'C-CHI-ZERO'),('zeta_C',0.,'C-ZETA-ZERO'),('chi_C',.5,'C-ONE-CHI-GATE')):
            ref=changed_reference(inputs.geometry.reference,'candidate',**{field:value})
            control=_fresh_geometry(replace(inputs,geometry=ref.geometry(),current=replace(inputs.current,Z_4=(-.25,)))) if value==0 else replace(inputs,geometry=ref.geometry())
            cp=CandidateCCurrent(control)
            expected=dense_current_oracle(control)
            np.testing.assert_allclose(cp.current.values,expected['current'],rtol=0,atol=2e-13)
            np.testing.assert_allclose(cp.read.flux.values,expected['read'],rtol=0,atol=2e-13)
            root=None
            if value==0:
                root=pc.ProvisionalCandidatePCStep(control)
                self.assertEqual(root.read.point.current,root.read.point.algebra.baseline)
                self.assertEqual(root.read.structural_source.increment,((0.,),))
                self.assertEqual(root.next_inputs.current.Z_4,zoh_oracle(control.current.Z_4,(0.,),control.dt,ref.profile.params_resolved.realization.tau_PC))
                self.assertNotEqual(root.next_inputs.current.Z_4,(0.,))
                self.assertNotEqual(root.next_inputs.current.Z_4,control.current.Z_4)
            else:
                # Hold the input J fixed when checking that chi occurs once.
                from pygrc.models.grc_v4_geometry import PhysicalFlux
                j=PhysicalFlux(inputs.geometry.reference.graph,point.current.values)
                read=cp.read_back(j)
                np.testing.assert_allclose(read.flux.values,2*np.asarray(point.read.flux.values),rtol=0,atol=2e-13)
            row(name,control_inputs_object=self.obj(control.to_payload()),control_complete_profile_id=ref.profile.complete_profile_id,
                control_J=list(cp.current.values),control_J0=list(cp.algebra.baseline.values),control_read=list(cp.read.flux.values),
                independent_J=expected['current'].tolist(),independent_read=expected['read'].tolist(),
                zero_step_inputs_object=None if root is None else self.obj(root.next_inputs.to_payload()),
                zero_source_release_not_reset=None if root is None else True,
                fixed_J_chi_ratio=None if value==0 else 2,control_is_nominated_support=False)


if __name__=="__main__":
    unittest.main()
