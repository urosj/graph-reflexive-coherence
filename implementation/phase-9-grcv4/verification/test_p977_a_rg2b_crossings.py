"""Graph-nominated A_RG2b crossings; scalar historical targets are not aliases."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from functools import lru_cache
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models.grc_v4_candidate_a import CandidateACurrent, CandidateAWriter
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection
from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, GraphCoordinateAction
from pygrc.models.grc_v4_events import coordinate_reference
from pygrc.models.grc_v4_initializer import HISTORY_POLICY
from pygrc.models.grc_v4_profile import resolve_profile
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_generic_lifecycle import fixture as nominal_fixture, restore
from tests.models.test_grc_v4_migration import fixture as scalar_fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_initializer import oracle as initializer_oracle
from tests.models.test_grc_v4_rg2b_graph import graph_fixture
from tests.models.test_grc_v4_pc import configure
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_ci import independent_point
from tests.models.test_grc_v4_candidate_c import dense_current_oracle
from tests.models.test_grc_v4_lifecycle import request, primitive
import test_p977_a_ci_crossings as common
from test_p977_a_rg2b_local import NOMINATED, inverse_oracle

MIGRATIONS = {
    'nonpersistent_incoming': ('A_OS','A_RG2b','exact_transport','not_applicable',[]),
    'persistent_outgoing': ('A_RG2b','A_PC','exact_transport','target_initializer',[]),
    'persistent_incoming': ('A_PC','A_RG2b','exact_transport','explicit_loss',['carrier_history_loss']),
    'candidate_outgoing': ('A_RG2b','C_OS','explicit_loss','not_applicable',['candidate_history_loss']),
}


@lru_cache(maxsize=4)
def companion(family):
    inputs,backend=nominal_fixture('A_RG2b')
    if family=='A_RG2b': return inputs,backend
    if family=='A_PC':
        z=tuple(1/32 if i==j else 0. for i in range(3) for j in range(3))
        return configure(inputs,resource_radius=8.,weight_upper=3.,gain=.001,z=z,
                         reset_z=tuple(-v if v else 0. for v in z)),backend
    if family=='C_OS':
        c,_=graph_fixture('C')
        inputs=replace(c,current=replace(c.current,C=inputs.current.C),
                       reset=replace(c.reset,C=inputs.reset.C),Q_target=inputs.Q_target,receipt_ids=())
        backend=None
    ref=inputs.geometry.reference
    params,identity=ref.profile.params_resolved.to_payload(),ref.profile.identity_payload.to_payload()
    params['realization']=scalar_fixture(family)[0].geometry.reference.profile.params_resolved.realization.to_payload()
    identity.update(realization='OS',profile_family_id=family)
    reidentify(params,identity)
    return replace(inputs,geometry=replace(ref,profile=resolve_profile(params,identity)).geometry()),backend


def event_target():
    inputs,backend=companion('A_RG2b');source=inputs.geometry.reference
    graph=GRCV4Graph(tuple('target-'+n for n in source.graph.live_node_ids),
        tuple(OrientedEdge('target-'+e.edge_id,'target-'+e.tail_node_id,'target-'+e.head_node_id)
              for e in source.graph.oriented_edges))
    target,other=coordinate_reference(source,GraphCoordinateAction(source.graph,graph,(0,1,2,3),(0,1,2),(1,1,1)),backend)
    target=changed_reference(target,'lifecycle',history_policy_id=HISTORY_POLICY)
    # The selected initializer produces W near one, not the nomination's
    # supplied-W chart centred on two. This is a distinct complete target.
    domain=RG2bGraphDomain.from_identity(target.profile.params_resolved.realization.extension_evaluator_id)
    target=changed_reference(target,'realization',extension_evaluator_id=replace(domain,center_W=1.).identity)
    return target,other


class ARG2bCrossingTests(unittest.TestCase):
    obj=recorder.CompleteProfileCatalogTests.obj
    reset_check=common.ACICrossingTests.reset_check

    @classmethod
    def setUpClass(cls): cls.rows,cls.objects=[],{}

    def emit(self,case,before,owner,result,declared,**observation):
        recorder.CompleteProfileCatalogTests.emit(self,case,before,owner,result,request=declared,observation=observation)
        self.rows[-1]['nominated_complete_profile_id']=NOMINATED

    def owner(self,inputs,backend,target,other):
        extras=() if other is None or (backend is not None and backend.identity==other.identity) else (other,)
        return GRCV4(inputs,differential_reference=backend,targets=(target,),target_differential_references=extras)

    def execute(self,owner,target,other,declared,expected,*,mapped=False):
        publication=owner._operation._owned; points=[];sections=[]
        a_native,c_native,s_native=CandidateACurrent.__post_init__,CandidateCCurrent.__post_init__,CandidateRG2bSection.__post_init__
        publish=lifecycle._validate_publication
        def observe(point,native):
            native(point)
            if point.inputs.geometry.reference==target:
                self.assertIs(owner._operation._owned,publication);points.append(point)
        def section(s):
            s_native(s)
            if s.inputs.geometry.reference==target:
                self.assertIs(owner._operation._owned,publication);sections.append(s)
        def publication_check(*args,**kwargs):
            for state in expected.values():
                self.assertTrue(any(primitive(p.inputs.current)==state for p in points))
            self.assertIs(owner._operation._owned,publication)
            return publish(*args,**kwargs)
        with patch.object(CandidateACurrent,'__post_init__',lambda p:observe(p,a_native)), \
             patch.object(CandidateCCurrent,'__post_init__',lambda p:observe(p,c_native)), \
             patch.object(CandidateRG2bSection,'__post_init__',section), \
             patch.object(lifecycle,'_validate_publication',publication_check), \
             patch.object(CandidateAWriter,'__post_init__',side_effect=AssertionError('crossing used ordinary W writer')):
            result=owner.reconstruct_topology_event(declared) if mapped else owner.migrate_profile(declared)
        self.assertTrue(result.committed,result.failure)
        observations={}
        for role,state in expected.items():
            point=next(p for p in reversed(points) if primitive(p.inputs.current)==state)
            h=np.array(point.inputs.geometry.one_form_hodge.matrix)
            current,_=independent_point(point.inputs,other,h)
            np.testing.assert_allclose(point.current.values,current,rtol=0,atol=2e-12)
            obs=dict(inputs_object=self.obj(point.inputs.to_payload()),h=h.tolist(),current=list(point.current.values))
            if other is None:
                dense=dense_current_oracle(point.inputs)
                np.testing.assert_allclose(point.algebra.baseline.values,dense['j0'],rtol=0,atol=2e-12)
                obs['baseline']=list(point.algebra.baseline.values)
            if target.profile.identity_payload.realization=='RG2b':
                section=next(s for s in reversed(sections) if primitive(s.inputs.current)==state)
                # Readmission carries dt=0; the graph-transform itself uses the
                # target's frozen positive beat. The independent oracle must too.
                domain=RG2bGraphDomain.from_identity(target.profile.params_resolved.realization.extension_evaluator_id)
                oracle_inputs=replace(section.inputs,dt=domain.beat_dt)
                oracle_h=inverse_oracle(oracle_inputs,other)
                b=dict(section.certificate.bounds)
                allowance=float(F(section.error_upper)+F(b['section_radius'])*F(b['contraction_upper'])**2)+2e-15
                self.assertLessEqual(np.linalg.norm(h-oracle_h),allowance)
                obs.update(section_inputs_object=self.obj(section.inputs.to_payload()),inverse_oracle_h=oracle_h.tolist(),
                    certificate=b,error_upper=section.error_upper,levels=section.levels,evaluations=section.evaluations,
                    frozen_beat=domain.beat_dt,regularity='Lipschitz_only')
            observations[role]=dict(**state,readmission=obs)
        return result,observations

    def test_graph_nomination_migration_channels_and_reset(self):
        for case,(source,family,candidate,carrier,losses) in MIGRATIONS.items():
            inputs,backend=companion(source);target_inputs,other=companion(family);target=target_inputs.geometry.reference
            self.assertIn(NOMINATED,(inputs.geometry.reference.profile.complete_profile_id,target.profile.complete_profile_id))
            owner=self.owner(inputs,backend,target,other)
            before=owner.snapshot();old=owner.state.lifecycle
            expected={role:dict(C=list(s.C),W_A=list(s.W_A) if family.startswith('A') else None,
                               Z_4=[0.]*9 if family=='A_PC' else None)
                      for role,s in (('current',old.current),('reset',old.reset.authoritative))}
            declared=migration(owner,target,operation=case)
            result,expectations=self.execute(owner,target,other,declared,expected)
            after=owner.snapshot();primary=result.emitted_receipts[0].identity_payload
            for role,key in (('current','scientific_state'),('reset','reset')):self.assertEqual(after[key]['authoritative'],expected[role])
            self.assertEqual(primary['history']['candidate']['disposition'],candidate)
            self.assertEqual(primary['history']['carrier']['disposition'],carrier)
            self.assertEqual(list(primary['core']['information_losses']),losses)
            self.assertEqual((owner.state.lifecycle.time,owner.state.lifecycle.step_index,owner.state.lifecycle.Q_target),
                             (old.time,old.step_index,old.Q_target))
            # One exact replay, then independent reset/restore. No prior scalar campaign reruns.
            replay=restore(before);self.assertEqual(replay.migrate_profile(declared),result);self.assertEqual(replay.snapshot(),after)
            reset_object=self.reset_check(owner)
            self.emit(case,before,restore(after),result,declared,expectations=expectations,
                target_reference_object=self.obj(target.to_payload()),target_backend_object=None if other is None else self.obj(other.to_payload()),
                after_reset_object=reset_object,expected_candidate=candidate,expected_carrier=carrier,expected_losses=losses,
                both_roles_admitted_before_publication=True,ordinary_writer_count=0,exact_replay=True)

    def test_changed_graph_event_frozen_completion_initializer_and_reset(self):
        inputs,backend=companion('A_RG2b');target,other=event_target()
        owner=self.owner(inputs,backend,target,other);before=owner.snapshot();old=owner.state.lifecycle
        matrix=tuple(int(j==3-i) for i in range(4) for j in range(4));increment=(1/128,0,0,0)
        declared=event(owner,target,matrix=matrix,increment=increment,operation='A_RG2b-mapped-event')
        expected={};references={}
        for role,s in (('current',old.current),('reset',old.reset.authoritative)):
            C=tuple(float(F(s.C[3-i])+(F(1,128) if i==0 else 0)) for i in range(4))
            reference,W=initializer_oracle(target,other,C)
            expected[role]=dict(C=list(C),W_A=W,Z_4=None);references[role]=reference
        result,expectations=self.execute(owner,target,other,declared,expected,mapped=True)
        after=owner.snapshot()
        for role,key in (('current','scientific_state'),('reset','reset')):
            self.assertEqual(after[key]['authoritative'],expected[role]);expectations[role]['reference_pass']=references[role]
        self.assertNotEqual(expected['current']['W_A'],expected['reset']['W_A'])
        primary=result.emitted_receipts[0].identity_payload
        self.assertEqual(list(primary['core']['information_losses']),['candidate_history_loss'])
        self.assertEqual(primary['history']['carrier']['disposition'],'not_applicable')
        self.assertEqual(owner.state.lifecycle.Q_target,float(F(old.Q_target)+F(1,128)))
        self.assertEqual((owner.state.lifecycle.time,owner.state.lifecycle.step_index),(old.time,old.step_index))
        hostile=deepcopy(after);hostile['transition_records']=[]
        with self.assertRaises(ValueError):restore(hostile)
        clone=owner.duplicate();reset_object=self.reset_check(owner);self.assertEqual(clone.snapshot(),after)
        self.emit('mapped_event',before,clone,result,declared,expectations=expectations,
            target_reference_object=self.obj(target.to_payload()),target_backend_object=self.obj(other.to_payload()),
            after_reset_object=reset_object,expected_candidate=primary['history']['candidate']['disposition'],
            expected_carrier='not_applicable',expected_losses=['candidate_history_loss'],expected_Q_target=float(F(old.Q_target)+F(1,128)),
            both_roles_admitted_before_publication=True,ordinary_writer_count=0,missing_archive_rejected=True,
            duplicate_unchanged_after_reset=True,map_scope='one_affine_renamed_graph_not_GRC9',initializer_is_separate_target=True)

    def test_target_core_readmission_failure_controls_and_incoming_initializer_boundary(self):
        inputs,backend=companion('A_OS');nominal,_=companion('A_RG2b');target=nominal.geometry.reference
        for case,w in (('readmission_control',None),('readmission_rejection',2.3125),('core_only_admission',2.1875)):
            reset=inputs.current if w is None else replace(inputs.reset,W_A=(w,)*3)
            altered=replace(inputs,reset=reset);owner=self.owner(altered,backend,target,backend)
            before,publication=owner.snapshot(),owner._operation._owned;declared=migration(owner,target,operation=case)
            with patch.object(lifecycle,'_validate_publication',wraps=lifecycle._validate_publication) as publish:
                result=owner.migrate_profile(declared)
            self.assertEqual(result.committed,case!='readmission_rejection')
            if not result.committed:
                self.assertEqual(result.failure.stage,'target_readmission');self.assertIn('outside K',result.failure.message)
                publish.assert_not_called();self.assertEqual(owner.snapshot(),before);self.assertIs(owner._operation._owned,publication)
            after=owner.snapshot();extra={}
            if case=='core_only_admission':
                self.assertEqual(owner.state.lifecycle.reset.authoritative.W_A,(w,)*3)
                for dt in (0.,nominal.dt):
                    rejected=owner.step_v4_input(request(dt,'core-not-inner-'+str(dt)))
                    self.assertFalse(rejected.committed);self.assertIn('K_minus',rejected.failure.message)
                    self.assertEqual(owner.snapshot(),after)
                reset_object=self.reset_check(owner)
                extra=dict(after_reset_object=reset_object,ordinary_entry_rejected_durations=[0.,nominal.dt],
                           state_readmission_is_not_ordinary_entry=True)
            self.emit(case,before,restore(after),result,declared,failure_stage=None if result.committed else result.failure.stage,
                reset_W=None if w is None else w,target_reference_object=self.obj(target.to_payload()),**extra)
        c_inputs,_=companion('C_OS');owner=self.owner(c_inputs,None,target,backend)
        selected=changed_reference(target,'lifecycle',history_policy_id=HISTORY_POLICY)
        payload=migration(owner,selected).to_payload();payload['target_profile_id']=NOMINATED
        declared=GRCV4MigrationRequest.from_payload(payload);before,publication=owner.snapshot(),owner._operation._owned
        result=owner.migrate_profile(declared)
        self.assertFalse(result.committed);self.assertEqual(result.failure.stage,'admission')
        self.assertIn('initializer source',result.failure.message)
        self.assertEqual(owner.snapshot(),before);self.assertIs(owner._operation._owned,publication)
        self.emit('incoming_C_rejection',before,owner,result,declared,failure_stage='admission',
            selected_initializer_profile_id=selected.profile.complete_profile_id,
            scope='negative_nomination_target_not_positive_C_to_A')


if __name__=='__main__':unittest.main()
