"""Missing C_CI_PC crossings; exact preserved PC pairs are reused, not rerun."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, GraphCoordinateAction
from pygrc.models.grc_v4_events import coordinate_reference
from pygrc.models.grc_v4_ci import CandidateCIRoot
from tests.models.test_grc_v4_cipc import independent_root as coupled_root
from tests.models.test_grc_v4_ci import independent_root as ci_root
from tests.models.test_grc_v4_initializer import target as initializer_target, oracle as initializer_oracle
from pygrc.models.grc_v4_pc import PCBaseChart
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_migration import fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_pc import configure
from tests.models.test_grc_v4_candidate_c import dense_current_oracle
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from test_p977_c_ci_pc_local import NOMINATED, observed_chain
from test_p977_a_ci_crossings import ACICrossingTests


class CCIPCCrossingTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj
    reset_check = ACICrossingTests.reset_check

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}

    def emit(self, case, before, owner, result, declared, **observation):
        recorder.CompleteProfileCatalogTests.emit(self, case, before, owner, result,
            request=declared, observation=observation)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_nonpersistent_and_candidate_crossings_on_exact_endpoints(self):
        for case,source_family,target_family in (
                ('nonpersistent_incoming','C_CI','C_CI_PC'),
                ('nonpersistent_outgoing','C_CI_PC','C_CI'),
                ('candidate_incoming','A_CI_PC','C_CI_PC'),
                ('initializer_outgoing','C_CI_PC','A_CI_PC')):
            inputs,backend=fixture(source_family)
            if case=='initializer_outgoing':target,other=initializer_target(target_family)
            else:
                target_inputs,other=fixture(target_family);target=target_inputs.geometry.reference
            extras=() if other is None or (backend is not None and other.identity==backend.identity) else (other,)
            owner=GRCV4(inputs,differential_reference=backend,targets=(target,),target_differential_references=extras)
            self.assertTrue(owner.step_v4_input(request(0,'seed-'+case)).committed)
            before,old,publication=owner.snapshot(),owner.state.lifecycle,owner._operation._owned
            declared=migration(owner,target,operation=case)
            observed=[];native=CandidateCIRoot.__post_init__;publish=lifecycle._validate_publication
            def observe(root):
                native(root)
                if root.inputs.geometry.reference==target:
                    self.assertIs(owner._operation._owned,publication)
                    observed.append(root)
            def publication_check(*args,**kwargs):
                self.assertIs(owner._operation._owned,publication)
                for a in (old.current,old.reset.authoritative):
                    self.assertTrue(any(root.inputs.current.C==a.C for root in observed))
                return publish(*args,**kwargs)
            with patch.object(CandidateCIRoot,'__post_init__',observe),patch.object(lifecycle,'_validate_publication',publication_check):
                result=owner.migrate_profile(declared)
            self.assertTrue(result.committed,result.failure)
            after=owner.snapshot();expectations={}
            for role,a,b in (('current',old.current,owner.state.lifecycle.current),
                              ('reset',old.reset.authoritative,owner.state.lifecycle.reset.authoritative)):
                init,W=initializer_oracle(target,other,a.C) if case=='initializer_outgoing' else (None,None)
                Z=None if case=='nonpersistent_outgoing' else [0.]
                self.assertEqual(dict(C=list(b.C),W_A=None if b.W_A is None else list(b.W_A),Z_4=None if b.Z_4 is None else list(b.Z_4)),dict(C=list(a.C),W_A=W,Z_4=Z))
                root=next(r for r in observed if r.inputs.current==b)
                if target.profile.identity_payload.realization=='CI+PC':h,j,source=coupled_root(root.inputs,other)
                else:
                    j,h=ci_root(root.inputs,other);source=None
                np.testing.assert_allclose(root.current.values,j,rtol=0,atol=2e-11)
                np.testing.assert_allclose(root.selected.inputs.geometry.one_form_hodge.matrix,h,rtol=0,atol=2e-11)
                chain=None
                if target.profile.identity_payload.candidate=='C':
                    native_chain=observed_chain(root.selected.point);oracle=dense_current_oracle(root.selected.inputs)
                    for k in native_chain:np.testing.assert_allclose(native_chain[k],oracle[k],rtol=0,atol=2e-12)
                    chain=dict(observed=native_chain,independent_oracle={k:oracle[k].tolist() for k in native_chain})
                expectations[role]=dict(C=list(b.C),W_A=W,Z_4=Z,reference_pass=init,
                    root_inputs_object=self.obj(root.inputs.to_payload()),selected_inputs_object=self.obj(root.selected.inputs.to_payload()),
                    current=list(root.current.values),h=[list(r) for r in root.selected.inputs.geometry.one_form_hodge.matrix],
                    source=None if source is None else [list(r) for r in root.selected.structural_source.increment],C_chain=chain)
            candidate={'nonpersistent_incoming':'rederived','nonpersistent_outgoing':'rederived',
                       'candidate_incoming':'explicit_loss','initializer_outgoing':'target_initializer'}[case]
            carrier={'nonpersistent_incoming':'target_initializer','nonpersistent_outgoing':'explicit_loss',
                     'candidate_incoming':'whole_carrier_reset','initializer_outgoing':'whole_carrier_reset'}[case]
            losses=[] if case=='nonpersistent_incoming' else ['candidate_history_loss','carrier_history_loss'] if case=='candidate_incoming' else ['carrier_history_loss']
            primary=result.emitted_receipts[0].identity_payload
            self.assertEqual(primary['history']['candidate']['disposition'],candidate)
            self.assertEqual(primary['history']['carrier']['disposition'],carrier)
            self.assertEqual(list(primary['core']['information_losses']),losses)
            if case=='initializer_outgoing':
                self.assertIsNotNone(after['transition_records'][-1]['initializer_pair'])
                self.assertNotEqual(target.profile.complete_profile_id,fixture('A_CI_PC')[0].geometry.reference.profile.complete_profile_id)
                self.assertNotEqual(expectations['current']['W_A'],expectations['reset']['W_A'])
            else:self.assertIsNone(after['transition_records'][-1].get('initializer_pair'))
            self.assertEqual((owner.state.lifecycle.time,owner.state.lifecycle.step_index,owner.state.lifecycle.Q_target),(old.time,old.step_index,old.Q_target))
            replay=restore(before)
            self.assertEqual(replay.migrate_profile(declared),result);self.assertEqual(replay.snapshot(),after)
            reset_object=self.reset_check(owner)
            self.emit(case,before,restore(after),result,declared,expectations=expectations,
                target_reference_object=self.obj(target.to_payload()),target_backend_object=None if other is None else self.obj(other.to_payload()),
                after_reset_object=reset_object,expected_candidate=candidate,expected_carrier=carrier,expected_losses=losses,
                both_roles_admitted_before_publication=True,exact_replay=True,
                initializer_is_separate_target=case=='initializer_outgoing')

    def test_mapped_event_reference_rebuild_carrier_loss_and_independent_reset(self):
        inputs, _ = fixture('C_CI_PC')
        self.assertEqual(inputs.geometry.reference.profile.complete_profile_id, NOMINATED)
        graph = GRCV4Graph(('x','y'), (OrientedEdge('target-e','x','y'),))
        action = GraphCoordinateAction(inputs.geometry.reference.graph, graph, (0,1), (0,), (1,))
        target, _ = coordinate_reference(inputs.geometry.reference, action, None)
        self.assertNotEqual(target.profile.complete_profile_id, NOMINATED)
        self.assertEqual(dict(target.profile.params_resolved.candidate.W_C_tr), {'target-e':2.})
        owner = GRCV4(inputs, targets=(target,))
        self.assertTrue(owner.step_v4_input(request(0,'event-seed')).committed)
        before, old, publication = owner.snapshot(), owner.state.lifecycle, owner._operation._owned
        declared = event(owner,target,matrix=(0,1,1,0),increment=(-.125,0),operation='C_CI_PC-mapped-event')
        expected_roles = {role:(float(F(a.C[1])-F(1,8)),a.C[0]) for role,a in
                          (('current',old.current),('reset',old.reset.authoritative))}
        seen = {}
        native, publish = CandidateCIRoot.__post_init__, lifecycle._validate_publication
        def observe(read):
            native(read)
            if read.inputs.geometry.reference != target:return
            self.assertIs(owner._operation._owned, publication)
            self.assertIsNone(read.inputs.current.W_A)
            self.assertEqual(read.inputs.current.Z_4, (0.,))
            expected = dense_current_oracle(read.selected.inputs)
            actual = observed_chain(read.selected.point)
            for key in actual:np.testing.assert_allclose(actual[key], expected[key], rtol=2e-12, atol=2e-14)
            h,j,source=coupled_root(read.inputs,None)
            np.testing.assert_allclose(read.current.values,j,rtol=0,atol=2e-11)
            np.testing.assert_allclose(read.selected.inputs.geometry.one_form_hodge.matrix,h,rtol=0,atol=2e-11)
            self.assertGreater(np.linalg.norm(h-np.asarray(target.pairings.one_form.matrix)),1e-8)
            self.assertGreater(np.linalg.norm(source),0.)
            seen[tuple(read.inputs.current.C)] = dict(inputs_object=self.obj(read.selected.inputs.to_payload()),
                root_inputs_object=self.obj(read.inputs.to_payload()),
                observed=actual, independent_oracle={k:expected[k].tolist() for k in actual},
                h=[list(r) for r in read.selected.inputs.geometry.one_form_hodge.matrix],
                source=[list(r) for r in read.selected.structural_source.increment])
        def validate_publication(*args, **kwargs):
            self.assertIs(owner._operation._owned, publication)
            for C in expected_roles.values():self.assertIn(C, seen)
            return publish(*args, **kwargs)
        with patch.object(CandidateCIRoot,'__post_init__',observe), patch.object(lifecycle,'_validate_publication',validate_publication):
            result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed,result.failure)
        after = owner.snapshot(); expectations = {}
        for role,key in (('current','scientific_state'),('reset','reset')):
            C = expected_roles[role]
            self.assertEqual(after[key]['authoritative'],dict(C=list(C),W_A=None,Z_4=[0.]))
            self.assertNotEqual(before[key]['authoritative']['Z_4'],[0.])
            expectations[role] = dict(C=list(C),W_A=None,Z_4=[0.],readmission=seen[C])
        self.assertNotEqual(old.current.Z_4,old.reset.authoritative.Z_4)
        self.assertNotEqual(expected_roles['current'],expected_roles['reset'])
        self.assertIsNone(after['transition_records'][-1]['initializer_pair'])
        history = result.emitted_receipts[0].identity_payload['history']
        self.assertEqual(history['candidate']['disposition'],'rederived')
        self.assertEqual(history['candidate']['information_loss'],'none')
        self.assertEqual(history['carrier']['disposition'],'whole_carrier_reset')
        self.assertEqual(list(result.emitted_receipts[0].identity_payload['core']['information_losses']),['carrier_history_loss'])
        self.assertEqual(owner.state.lifecycle.Q_target,float(F(old.Q_target)-F(1,8)))
        bad = deepcopy(after); bad['transition_records'] = []
        with self.assertRaises(ValueError):restore(bad)
        replay = restore(before)
        self.assertEqual(replay.reconstruct_topology_event(declared),result)
        self.assertEqual(replay.snapshot(),after)
        clone = owner.duplicate(); reset_object = self.reset_check(owner)
        self.assertEqual(clone.snapshot(),after)
        self.emit('mapped_event',before,restore(after),result,declared,
            expectations=expectations,target_reference_object=self.obj(target.to_payload()),
            expected_Q_target=float(F(old.Q_target)-F(1,8)),after_reset_object=reset_object,
            missing_archive_rejected=True,both_roles_admitted_before_publication=True,
            exact_replay=True,duplicate_unchanged_after_reset=True,
            expected_candidate='rederived',expected_carrier='whole_carrier_reset',expected_losses=['carrier_history_loss'],
            source_history_removal_is_not_native_release=True,
            zero_carrier_retains_immediate_geometry=True,
            map_scope='renamed_one_edge_C_CI_PC_target; not_arbitrary_topology_or_parameter_sweep')

    def test_changed_carrier_contract_rejects_without_reset_fallback(self):
        inputs, _ = fixture('C_CI_PC')
        original = fixture('C_PC')[0].geometry.reference
        target = changed_reference(original,'realization',tau_PC=1.)
        owner = GRCV4(inputs,targets=(target,))
        payload = migration(owner,original).to_payload(); payload['target_profile_id']=target.profile.complete_profile_id
        declared = GRCV4MigrationRequest.from_payload(payload)
        before, publication = owner.snapshot(), owner._operation._owned
        result = owner.migrate_profile(declared)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage,'admission')
        self.assertIn('exact carrier',result.failure.message)
        self.assertIs(owner._operation._owned,publication); self.assertEqual(owner.snapshot(),before)
        self.emit('carrier_contract_rejection',before,owner,result,declared,
            failure_stage='admission',target_reference_object=self.obj(target.to_payload()),
            preserved_target_reference_object=self.obj(original.to_payload()),changed_field='tau_PC',
            unchanged_history_not_silently_reset=True)

    def test_reset_only_target_chart_failure_and_passing_control(self):
        inputs, _ = fixture('C_CI_PC')
        # Reconstruction explicitly resets Z. A preserving C-to-C migration
        # would instead reject the changed chart at exact-contract admission.
        target = changed_reference(inputs.geometry.reference,'realization',source_envelope_id=PCBaseChart(3.,1.,1.).identity)
        for failing in (False,True):
            altered = replace(inputs,reset=replace(inputs.reset,C=(3.,1.))) if failing else replace(inputs,reset=inputs.current)
            owner = GRCV4(altered,targets=(target,))
            before, publication = owner.snapshot(), owner._operation._owned
            declared = event(owner,target,operation='reset-only' if failing else 'current-as-reset-control')
            with patch.object(lifecycle,'_validate_publication',wraps=lifecycle._validate_publication) as publish:
                result = owner.reconstruct_topology_event(declared)
            self.assertEqual(result.committed,not failing,result.failure)
            if failing:
                self.assertEqual(result.failure.stage,'target_readmission')
                self.assertIn('resource',result.failure.message)
                publish.assert_not_called(); self.assertIs(owner._operation._owned,publication)
                self.assertEqual(owner.snapshot(),before)
            else:
                for a,b in ((altered.current,owner.state.lifecycle.current),(altered.reset,owner.state.lifecycle.reset.authoritative)):
                    self.assertEqual(b.C,a.C); self.assertIsNone(b.W_A); self.assertEqual(b.Z_4,(0.,))
                history = result.emitted_receipts[0].identity_payload
                self.assertEqual(history['history']['carrier']['disposition'],'whole_carrier_reset')
                self.assertEqual(list(history['core']['information_losses']),['carrier_history_loss'])
            self.emit('readmission_rejection' if failing else 'readmission_control',before,owner,result,declared,
                failure_stage='target_readmission' if failing else None,target_reference_object=self.obj(target.to_payload()),
                source_resource_radius=4.,target_resource_radius=3.,
                source_current_norm_squared=sum(x*x for x in altered.current.C),
                source_reset_norm_squared=sum(x*x for x in altered.reset.C))


if __name__=='__main__':
    unittest.main()
