"""Missing C_PC crossings; reuse retained migrations without rerunning them."""

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
from pygrc.models.grc_v4_pc import CandidatePCRead
from tests.models import test_grc_v4 as recorder
from tests.models.test_grc_v4_migration import fixture, migration, changed_reference
from tests.models.test_grc_v4_events import event
from tests.models.test_grc_v4_pc import configure
from tests.models.test_grc_v4_candidate_c import dense_current_oracle
from tests.models.test_grc_v4_generic_lifecycle import restore
from tests.models.test_grc_v4_lifecycle import request
from test_p977_c_pc_local import NOMINATED, observed_chain
from test_p977_a_ci_crossings import ACICrossingTests


class CPCCrossingTests(unittest.TestCase):
    obj = recorder.CompleteProfileCatalogTests.obj
    reset_check = ACICrossingTests.reset_check

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.objects = [], {}

    def emit(self, case, before, owner, result, declared, **observation):
        recorder.CompleteProfileCatalogTests.emit(self, case, before, owner, result,
            request=declared, observation=observation)
        self.rows[-1]['nominated_complete_profile_id'] = NOMINATED

    def test_mapped_event_reference_rebuild_carrier_loss_and_independent_reset(self):
        inputs, _ = fixture('C_PC')
        self.assertEqual(inputs.geometry.reference.profile.complete_profile_id, NOMINATED)
        graph = GRCV4Graph(('x','y'), (OrientedEdge('target-e','x','y'),))
        action = GraphCoordinateAction(inputs.geometry.reference.graph, graph, (0,1), (0,), (1,))
        target, _ = coordinate_reference(inputs.geometry.reference, action, None)
        self.assertNotEqual(target.profile.complete_profile_id, NOMINATED)
        self.assertEqual(dict(target.profile.params_resolved.candidate.W_C_tr), {'target-e':2.})
        owner = GRCV4(inputs, targets=(target,))
        self.assertTrue(owner.step_v4_input(request(0,'event-seed')).committed)
        before, old, publication = owner.snapshot(), owner.state.lifecycle, owner._operation._owned
        declared = event(owner,target,matrix=(0,1,1,0),increment=(.125,0),operation='C_PC-mapped-event')
        expected_roles = {role:(float(F(a.C[1])+F(1,8)),a.C[0]) for role,a in
                          (('current',old.current),('reset',old.reset.authoritative))}
        seen = {}
        native, publish = CandidatePCRead.__post_init__, lifecycle._validate_publication
        def observe(read):
            native(read)
            if read.inputs.geometry.reference != target:return
            self.assertIs(owner._operation._owned, publication)
            self.assertIsNone(read.inputs.current.W_A)
            self.assertEqual(read.inputs.current.Z_4, (0.,))
            expected = dense_current_oracle(read.point.inputs)
            actual = observed_chain(read.point)
            for key in actual:np.testing.assert_allclose(actual[key], expected[key], rtol=2e-12, atol=2e-14)
            h = np.asarray(target.pairings.one_form.matrix)
            np.testing.assert_allclose(read.inputs.geometry.one_form_hodge.matrix, h, rtol=0, atol=2e-14)
            seen[tuple(read.inputs.current.C)] = dict(inputs_object=self.obj(read.point.inputs.to_payload()),
                observed=actual, independent_oracle={k:expected[k].tolist() for k in actual}, h=h.tolist())
        def validate_publication(*args, **kwargs):
            self.assertIs(owner._operation._owned, publication)
            for C in expected_roles.values():self.assertIn(C, seen)
            return publish(*args, **kwargs)
        with patch.object(CandidatePCRead,'__post_init__',observe), patch.object(lifecycle,'_validate_publication',validate_publication):
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
        self.assertEqual(owner.state.lifecycle.Q_target,float(F(old.Q_target)+F(1,8)))
        bad = deepcopy(after); bad['transition_records'] = []
        with self.assertRaises(ValueError):restore(bad)
        replay = restore(before)
        self.assertEqual(replay.reconstruct_topology_event(declared),result)
        self.assertEqual(replay.snapshot(),after)
        clone = owner.duplicate(); reset_object = self.reset_check(owner)
        self.assertEqual(clone.snapshot(),after)
        self.emit('mapped_event',before,restore(after),result,declared,
            expectations=expectations,target_reference_object=self.obj(target.to_payload()),
            expected_Q_target=float(F(old.Q_target)+F(1,8)),after_reset_object=reset_object,
            missing_archive_rejected=True,both_roles_admitted_before_publication=True,
            exact_replay=True,duplicate_unchanged_after_reset=True,
            expected_candidate='rederived',expected_carrier='whole_carrier_reset',expected_losses=['carrier_history_loss'],
            source_history_removal_is_not_native_release=True,
            map_scope='renamed_one_edge_C_PC_target; not_arbitrary_topology_or_parameter_sweep')

    def test_changed_carrier_contract_rejects_without_reset_fallback(self):
        inputs, _ = fixture('C_PC')
        original = fixture('C_CI_PC')[0].geometry.reference
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
        inputs, _ = fixture('C_PC')
        # Reconstruction explicitly resets Z. A preserving C-to-C migration
        # would instead reject the changed chart at exact-contract admission.
        target = configure(inputs, resource_radius=3).geometry.reference
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
