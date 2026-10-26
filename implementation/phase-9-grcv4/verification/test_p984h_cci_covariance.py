"""Focused map and full-joint covariance pressure, no native campaign."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import numpy as np
import p984h_cci_covariance as run


class CovarianceTests(unittest.TestCase):
    def test_baseline_geometry_representation(self):
        source, ev, _ = run.baseline()
        for index, inputs in enumerate((source['inputs'], ev['checkpoint']['state']['inputs'])):
            for role in run.ROLES:
                root = ev['admissions'][index][role]
                run.baseline_hodge(inputs, root)
                bad = deepcopy(inputs); bad['H1_form'][0][0] += 0.125
                with self.assertRaisesRegex(ValueError, 'baseline selected geometry'):
                    run.baseline_hodge(bad, root)
        for role in run.ROLES:
            record = run.cont.read(role, 1)
            for name, root in record['roots'].items():
                inputs = record['next_inputs'] if name == 'final' else ev['checkpoint']['state']['inputs']
                run.baseline_hodge(inputs, root)

    def test_comparison_and_scope(self):
        self.assertEqual(len(run.KINDS),8)
        for kind,seg in (('base','event'),('signed','final'),('reflect','source')):
            with self.assertRaises(ValueError):run.path(kind,seg)
        for wrong in ([float('nan')],[float('inf')],[1.001],[1.,2.]):
            with self.assertRaises(ValueError):run.compare(wrong,[1.],'pressure')
        self.assertEqual(run.compare([1.],[1.],'same'),0.)

    def test_all_maps_and_endpoint_pressure(self):
        with run.event.exact_backend(run.event.ExactBackend.FLINT), \
             run.event.numerical_policy(run.event.NumericalPolicy.CERTIFIED_ARB_256), \
             run.event.matrix_operation(), \
             patch.object(run.event.native,'GRC9V4CCIOperation',side_effect=AssertionError('native event')):
            for kind in run.KINDS:
                seed,request,identity,eid,target=run.subject(kind)
                self.assertEqual(len(target.current.C),107)
                self.assertEqual(len(target.geometry.reference.graph.live_edge_ids),407)
                self.assertNotEqual(seed.inputs.current,seed.inputs.reset)
                with run.transport():
                    old=run.baseline()[1]['checkpoint']['state']['inputs']['reference']['graph']
                    graph=target.to_payload()['reference']['graph'];d=run.maps.declaration(kind)
                    ni,ei,sign=run.maps.mapping(old,graph,d,run.baseline()[1]['event_id'],eid)
                    self.assertEqual(sorted(ni),list(range(107)));self.assertEqual(sorted(ei),list(range(407)))
                    bad=deepcopy(graph);bad['edges'][0]['tail']['port']=99
                    with self.assertRaises(ValueError):run.maps.mapping(old,bad,d,run.baseline()[1]['event_id'],eid)

    def test_retained_joint_pressure(self):
        if not (run.ROOT/run.path('combined','current')).exists():self.skipTest('not executed')
        with run.event.exact_backend(run.event.ExactBackend.FLINT), \
             run.event.numerical_policy(run.event.NumericalPolicy.CERTIFIED_ARB_256), \
             patch.object(run.cont,'ProvisionalCandidateCIStep',side_effect=AssertionError('native step')), \
             patch.object(run.event.native,'GRC9V4CCIOperation',side_effect=AssertionError('native event')):
            before,_=run.step_inputs('combined','current');value=run.read('combined','current')['execution']['roots']['current']
            run.check_joint(value,before)
            for field in ('H','generated','source'):
                bad=deepcopy(value);bad['joint'][field][0][0]+=0.125
                with self.assertRaises(ValueError):run.check_joint(bad,before)
            bad=deepcopy(value);bad['joint']['domain_id']='foreign'
            with self.assertRaises(ValueError):run.check_joint(bad,before)


if __name__=='__main__':unittest.main()
