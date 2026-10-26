"""Bounded transform and retained-record pressure; no native campaign replay."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_cos_covariance as c


class CovarianceTests(unittest.TestCase):
    def test_declarations_and_full_graph_mapping(self):
        graph=c.base()[0]['inputs']['reference']['graph']
        for kind in c.KINDS:
            d=c.declaration(kind);image=c.graph_image(graph,d,source=True)
            ni,ei,sign=c.mapping(graph,image,d)
            self.assertEqual(sorted(ni),list(range(100)))
            self.assertEqual(sorted(ei),list(range(400)))
            self.assertEqual(set(sign),{-1,1} if kind in ('signed','combined') else {1})
            bad=deepcopy(image);bad['edges'][0]['head']['port']=1+bad['edges'][0]['head']['port']%9
            with self.assertRaises(ValueError):c.mapping(graph,bad,d)
            bad=deepcopy(image);bad['edges'][0]['edge_id']='foreign'
            with self.assertRaises(ValueError):c.mapping(graph,bad,d)
        d=c.declaration('reflect')
        self.assertEqual(c.rename('old/extra/1/0007',d,'old','new'),'new/extra/3/0007')
        self.assertEqual(c.rename('old/internal/extra/1/0007',d,'old','new'),'new/internal/extra/3/0007')
        for kind,segment in (('foreign','event'),('all','event'),('combined','mechanical')):
            with self.assertRaises(ValueError):c.path(kind,segment)

    def test_signed_values_and_rank_pressure(self):
        old=dict(current=[1.,2.],baseline=[3.,4.],read_flux=[5.,6.],causal_flat=[7.,8.],selector_rank=1)
        new={k:[v[1],-v[0]] if isinstance(v,list) else v for k,v in old.items()}
        self.assertEqual(set(c.compare_point(old,new,[1,0],[1,-1]).values()),{0.})
        for key in ('current','baseline','read_flux','causal_flat','selector_rank'):
            bad=deepcopy(new)
            if key=='selector_rank':bad[key]=2
            else:bad[key][1]*=-1
            with self.assertRaises(ValueError):c.compare_point(old,bad,[1,0],[1,-1])

    def test_retained_native_records(self):
        if not (c.ROOT/c.path('combined','event')).exists():self.skipTest('not yet executed')
        with c.native.oracle.exact_backend(c.native.oracle.ExactBackend.FLINT),c.native.oracle.numerical_policy(c.native.oracle.NumericalPolicy.CERTIFIED_ARB_256),patch.object(c.native,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')),patch.object(c.native.native,'GRC9V4COSOperation',side_effect=AssertionError('native rerun')):
            m=c.native.oracle.old.read(c.INPUTS)
            for segment in ('event','current','reset'):
                if not (c.ROOT/c.path('combined',segment)).exists():continue
                r=c.read('combined',segment);c.check_record(r,m,'combined',segment)
                for mutate in (lambda x:x.update(user_accepted=True),lambda x:x.update(kind='signed'),lambda x:x.update(elapsed_seconds=1201),lambda x:x['execution'].update(native_steps=99)):
                    bad=deepcopy(r);mutate(bad)
                    with self.assertRaises(ValueError):c.check_record(c.seal(bad),m,'combined',segment)


if __name__=='__main__':unittest.main()
