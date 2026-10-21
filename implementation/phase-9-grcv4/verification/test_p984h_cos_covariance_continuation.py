"""Exercise the comparison before expensive native execution, without solves."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984h_cos_covariance_continuation as successor

c=successor.parent


class ComparisonTests(unittest.TestCase):
    def test_full_comparison_control_and_bad_geometry(self):
        with c.native.oracle.exact_backend(c.native.oracle.ExactBackend.FLINT),c.native.oracle.numerical_policy(c.native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
            _,_,_,eid,expected=c.subject('combined')
            before=c.continuation.initial('current');baseline=c.continuation.read('current',1)
            ni,ei,sign=c.mapping(before.to_payload()['reference']['graph'],expected.to_payload()['reference']['graph'],c.declaration('combined'),c.base()[1]['event_id'],eid)
            np=c.native.np
            b,params=c.native.oracle.old.graph_data(dict(graph=before.geometry.reference.graph.port_graph.to_payload(),profile=before.geometry.reference.profile.to_payload()))
            h=c.native.oracle.old.generated_h(b,np.array(baseline['observation']['predictor']['causal_flat']),params)
            h=(h[np.ix_(ei,ei)]*np.outer(sign,sign)).tolist()
            geometry=dict(predictor=expected.to_payload()['H1_form'],corrector=h,final=h)
            row=deepcopy(baseline['observation'])
            for stage in ('predictor','corrector','final'):
                for field in ('current','baseline','read_flux','causal_flat'):
                    row[stage][field]=(np.asarray(row[stage][field])[ei]*np.asarray(sign)).tolist()
                row[stage]['input_hodge_digest']=c.digest(geometry[stage])
            after=replace(expected,current=replace(expected.current,C=tuple(np.array(baseline['next_inputs']['current']['C'])[ni])))
            with patch.object(c.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native run forbidden')):
                result=successor.compare_step('combined','current',row,after,geometry)
                self.assertEqual(result['resources'],0.);self.assertEqual(result['generated_geometry'],0.)
                bad=deepcopy(geometry);bad['corrector'][0][0]=123.
                with self.assertRaises(ValueError):successor.compare_step('combined','current',row,after,bad)
                bad=deepcopy(row);bad['final']['input_hodge_digest']='stale'
                with self.assertRaises(ValueError):successor.compare_step('combined','current',bad,after,geometry)


if __name__=='__main__':unittest.main()
