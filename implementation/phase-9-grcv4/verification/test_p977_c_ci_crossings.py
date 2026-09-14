"""Exact C_CI crossing gaps; retained migrations are projected, not rerun."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import unittest
import numpy as np
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, GraphCoordinateAction
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_events import coordinate_reference
from tests.models.test_grc_v4_candidate_c import dense_current_oracle
from tests.models.test_grc_v4_ci import scalar_c_bisection
from tests.models.test_grc_v4_pc import configure
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models import grc_v4_lifecycle as lifecycle
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_migration import fixture, migration
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_initializer import target as initializer_target, oracle
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from test_p977_c_ci_local import NOMINATED


class CCICrossingTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}

    def emit(self, case, before, owner, result, declared, **observation):
        recorder.CompleteProfileCatalogTests.emit(self, case, before, owner, result,
            request=declared, observation=observation)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def reset_check(self, owner):
        before, state = owner.snapshot(), owner.state.lifecycle
        self.assertNotEqual(state.current, state.reset.authoritative)
        owner.reset()
        after = owner.snapshot()
        self.assertEqual(owner.state.lifecycle.current, state.reset.authoritative)
        self.assertEqual(owner.state.lifecycle.reset, state.reset)
        self.assertEqual((owner.state.lifecycle.time, owner.state.lifecycle.step_index, owner.state.lifecycle.Q_target),
                         (state.time, state.step_index, state.Q_target))
        for key in ('reference', 'transition_records'):
            self.assertEqual(after[key], before[key])
        self.assertEqual(after['receipt_ledger'][:-4], before['receipt_ledger'])
        self.assertEqual(after['commit_records'][:-1], before['commit_records'])
        self.assertEqual(restore(after).snapshot(), after)
        return self.obj(after)

    def test_returning_carrier_and_outgoing_initializer(self):
        for case in ('persistent_C_PC','C_to_A'):
            inputs,backend=fixture('C_PC' if case=='persistent_C_PC' else 'C_CI')
            target,other=(fixture('C_CI')[0].geometry.reference,None) if case=='persistent_C_PC' else initializer_target('A_OS')
            self.assertIn(NOMINATED,(inputs.geometry.reference.profile.complete_profile_id,target.profile.complete_profile_id))
            owner=GRCV4(inputs,targets=(target,),target_differential_references=() if other is None else (other,))
            self.assertTrue(owner.step_v4_input(request(0,'seed-'+case)).committed)
            before,old=owner.snapshot(),owner.state.lifecycle
            declared=migration(owner,target,operation=case)
            result=owner.migrate_profile(declared)
            self.assertTrue(result.committed,result.failure)
            after,new=owner.snapshot(),owner.state.lifecycle
            expectations={}
            for role,a,b in (('current',old.current,new.current),('reset',old.reset.authoritative,new.reset.authoritative)):
                self.assertEqual(b.C,a.C);self.assertIsNone(b.Z_4)
                if other is None:
                    self.assertIsNone(b.W_A)
                    expectations[role]=dict(C=list(a.C),W_A=None,Z_4=None)
                else:
                    derived,W=oracle(target,other,a.C)
                    self.assertEqual(list(b.W_A),W)
                    expectations[role]=dict(C=list(a.C),W_A=W,Z_4=None,reference_pass=derived)
            self.assertEqual((new.time,new.step_index,new.Q_target),(old.time,old.step_index,old.Q_target))
            if case=='persistent_C_PC':
                self.assertNotEqual(old.current.Z_4,old.reset.authoritative.Z_4)
                self.assertNotEqual(old.current.Z_4,(0.,));self.assertNotEqual(old.reset.authoritative.Z_4,(0.,))
            else:
                self.assertNotEqual(expectations['current']['W_A'],expectations['reset']['W_A'])
            history=result.emitted_receipts[0].identity_payload['history']
            candidate='rederived' if other is None else 'target_initializer'
            carrier='explicit_loss' if other is None else 'not_applicable'
            losses=['carrier_history_loss'] if other is None else []
            self.assertEqual(history['candidate']['disposition'],candidate)
            self.assertEqual(history['carrier']['disposition'],carrier)
            self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']),losses)
            replay=restore(before)
            self.assertEqual(replay.migrate_profile(declared),result);self.assertEqual(replay.snapshot(),after)
            reset_object=self.reset_check(owner)
            self.emit(case,before,restore(after),result,declared,after_reset_object=reset_object,
                expected_candidate=candidate,expected_carrier=carrier,expected_losses=losses,
                expectations=expectations,target_reference_object=self.obj(target.to_payload()),
                target_backend_object=None if other is None else self.obj(other.to_payload()),exact_replay=True)

    def test_mapped_event_reference_rederivation_and_distinct_reset(self):
        inputs,_=fixture('C_CI');self.assertEqual(inputs.geometry.reference.profile.complete_profile_id,NOMINATED)
        graph=GRCV4Graph(('x','y'),(OrientedEdge('target-e','x','y'),))
        action=GraphCoordinateAction(inputs.geometry.reference.graph,graph,(0,1),(0,),(1,))
        target,_=coordinate_reference(inputs.geometry.reference,action,None)
        self.assertNotEqual(target.profile.complete_profile_id,NOMINATED)
        self.assertEqual(dict(target.profile.params_resolved.candidate.W_C_tr),{'target-e':2.})
        owner=GRCV4(inputs,targets=(target,))
        self.assertTrue(owner.step_v4_input(request(0,'event-seed')).committed)
        before,old=owner.snapshot(),owner.state.lifecycle
        declared=event(owner,target,matrix=(0,1,1,0),increment=(.125,0),operation='C_CI-mapped-event')
        expected_roles={role:(float(F(a.C[1])+F(1,8)),a.C[0]) for role,a in
                        (('current',old.current),('reset',old.reset.authoritative))}
        original=owner._operation._owned;seen={};trials=[]
        native=CandidateCCurrent.__post_init__;publish=lifecycle._validate_publication
        def observe(point):
            native(point)
            if point.inputs.geometry.reference.identity!=target.identity:return
            self.assertIs(owner._operation._owned,original)
            self.assertEqual(dict(point.inputs.geometry.reference.profile.params_resolved.candidate.W_C_tr),{'target-e':2.})
            expected=dense_current_oracle(point.inputs)
            a=point.algebra
            actual=dict(projector=a.selector.projector,sector=a.selector.selected.values,hm=a.retained_hodge.matrix,
                phi=a.potential.values,j0=a.baseline.values,current=point.current.values,read=point.read.flux.values)
            for key,value in actual.items():np.testing.assert_allclose(value,expected[key],rtol=0,atol=2e-12)
            row=dict(inputs_object=self.obj(point.inputs.to_payload()),observed={k:np.asarray(v).tolist() for k,v in actual.items()})
            trials.append(row)
            if point.inputs.stage=='ci_trial':seen[tuple(point.inputs.current.C)]=row
        def publication(*args,**kwargs):
            self.assertIs(owner._operation._owned,original)
            for C in expected_roles.values():self.assertIn(C,seen)
            return publish(*args,**kwargs)
        with patch.object(CandidateCCurrent,'__post_init__',observe),patch.object(lifecycle,'_validate_publication',publication):
            result=owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed,result.failure)
        after=owner.snapshot();expectations={}
        from pygrc.models.grc_v4_geometry import GeometryStageInputs
        for role,C in expected_roles.items():
            actual=after['scientific_state']['authoritative'] if role=='current' else after['reset']['authoritative']
            self.assertEqual(actual,dict(C=list(C),W_A=None,Z_4=None))
            point=seen[C];stage=GeometryStageInputs.from_payload(self.objects[point['inputs_object']])
            j,h=scalar_c_bisection(stage)
            np.testing.assert_allclose(point['observed']['current'],[j],rtol=0,atol=2e-11)
            np.testing.assert_allclose(stage.geometry.one_form_hodge.matrix,[[h]],rtol=0,atol=2e-11)
            expectations[role]=dict(C=list(C),W_A=None,Z_4=None,root_current=[j],root_hodge=[[h]],selected_point=point)
        self.assertIsNone(after['transition_records'][-1]['initializer_pair'])
        self.assertEqual(owner.state.lifecycle.Q_target,float(F(old.Q_target)+F(1,8)))
        bad=deepcopy(after);bad['transition_records']=[]
        with self.assertRaises(ValueError):restore(bad)
        replay=restore(before);self.assertEqual(replay.reconstruct_topology_event(declared),result)
        self.assertEqual(replay.snapshot(),after)
        history=result.emitted_receipts[0].identity_payload['history']
        self.assertEqual(history['candidate']['disposition'],'rederived')
        self.assertEqual(history['carrier']['disposition'],'not_applicable')
        self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']),[])
        reset_object=self.reset_check(owner)
        self.emit('mapped_event',before,restore(after),result,declared,expectations=expectations,
            expected_Q_target=float(F(old.Q_target)+F(1,8)),after_reset_object=reset_object,
            missing_archive_rejected=True,expected_candidate='rederived',expected_carrier='not_applicable',expected_losses=[],
            target_reference_object=self.obj(target.to_payload()),target_readmission_points=trials,
            both_roles_admitted_before_publication=True,exact_replay=True,
            map_scope='renamed_one_edge_C_CI_target; not_arbitrary_topology_or_parameter_sweep')

    def test_reset_only_target_readmission_failure(self):
        inputs,_=fixture('C_CI')
        target=configure(inputs,resource_radius=3).geometry.reference
        for failing in (False,True):
            altered=replace(inputs,reset=replace(inputs.reset,C=(0.,4.))) if failing else replace(inputs,reset=inputs.current)
            owner=GRCV4(altered,targets=(target,));before,publication=owner.snapshot(),owner._operation._owned
            declared=migration(owner,target,operation='reset-only' if failing else 'current-as-reset-control')
            with patch.object(lifecycle,'_validate_publication',wraps=lifecycle._validate_publication) as publish:
                result=owner.migrate_profile(declared)
            self.assertEqual(result.committed,not failing)
            if failing:
                self.assertEqual(result.failure.stage,'target_readmission');self.assertIn('resource',result.failure.message)
                publish.assert_not_called();self.assertIs(owner._operation._owned,publication)
                self.assertEqual(owner.snapshot(),before)
            self.emit('readmission_rejection' if failing else 'readmission_control',before,owner,result,declared,
                failure_stage=result.failure.stage if failing else None,target_reference_object=self.obj(target.to_payload()))


if __name__=='__main__':
    unittest.main()
