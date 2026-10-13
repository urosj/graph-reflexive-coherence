"""Focused transform algebra, partial-transport and retained-coverage pressure."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import p984e_cos as e


class CovarianceTests(unittest.TestCase):
    def test_transform_bijections_incidence_resources_and_reference(self):
        p=e.b.read(e.prior.INPUTS)['initial_inputs']
        before=e.b.GeometryStageInputs.from_payload(p)
        for d in e.declarations():
            q=e.transform(p,d);after=e.b.GeometryStageInputs.from_payload(q)
            ni,ei,s=e.mapping(p['reference']['graph'],q['reference']['graph'],d)
            self.assertTrue(e.b.np.array_equal(e.b.np.array(after.geometry.reference.graph.incidence),
                e.b.np.array(before.geometry.reference.graph.incidence)[e.b.np.ix_(ni,ei)]*s))
            for role in e.ROLES:self.assertEqual(q[role]['C'],[p[role]['C'][i] for i in ni])
            self.assertEqual(len(after.geometry.reference.profile.params_resolved.candidate.W_C_tr),9)
        bad=deepcopy(e.declarations()[1]);bad['edge_order'][0]=bad['edge_order'][1]
        with self.assertRaisesRegex(ValueError,'nonbijective'):e.transform(p,bad)
        changed=e.transform(p,e.declarations()[3]);changed['reference']['profile']=p['reference']['profile']
        with self.assertRaises(ValueError):e.b.GeometryStageInputs.from_payload(changed)

    def test_nontrivial_signed_geometry_algebra_and_partial_transport(self):
        p=e.b.read(e.prior.INPUTS)['initial_inputs'];d=e.declarations()[-1]
        # A nontrivial SPD algebra probe, not a new admitted C_OS trajectory.
        x=e.b.np.arange(1.,10.)/16;h=e.b.np.eye(9)+e.b.np.outer(x,x)
        p['H1_form']=h.tolist();q=e.transform(p,d)
        _,ei,s=e.mapping(p['reference']['graph'],q['reference']['graph'],d)
        expected=h[e.b.np.ix_(ei,ei)]*e.b.np.outer(s,s)
        self.assertTrue(e.b.np.array_equal(q['H1_form'],expected))
        with self.assertRaisesRegex(ValueError,'independent comparison failed'):
            e.b.comparison(h[e.b.np.ix_(ei,ei)]*s[:,None],expected,
                dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13),'one_sided_H')
        bad=deepcopy(q['reference']['graph']);bad['edges'][0]['head']['port']=1
        with self.assertRaisesRegex(ValueError,'partial endpoint'):e.mapping(p['reference']['graph'],bad,d)

    def test_retained_scope_chain_and_signed_current_mutations(self):
        if not (e.b.ROOT/e.RESULTS).exists():self.skipTest('run campaign before retained pressure')
        m=e.b.read(e.INPUTS);record=e.b.read(e.RESULTS)
        e.check_manifest(m)
        with patch.object(e,'check_manifest'),patch.object(e.b,'ProvisionalCandidateCOSStep',side_effect=AssertionError('native rerun')):
            self.assertEqual(e.check(m,record)['passing_pending_cells'],20)
            for mutation in ('roster','acceptance','source_C','current_sign','final_chain','event_graph'):
                bad=deepcopy(record);data=e.prior.previous.expand(bad['execution'])
                if mutation=='roster':data['cases'].pop()
                elif mutation=='acceptance':bad['user_accepted']=True
                elif mutation=='source_C':data['sources'][2]['step']['pass']['inputs']['current']['C'].reverse()
                elif mutation=='current_sign':
                    row=next(r for r in data['cases'] if r['kind']=='signed')
                    j=row['roles']['current']['steps'][0]['pass']['corrector']['current'];j[0]+=0.01
                elif mutation=='final_chain':data['cases'][0]['roles']['reset']['final']['inputs']['time']+=1
                else:data['cases'][0]['target']['inputs']['reference']['graph']['edges'][0]['kind']='tree'
                bad['execution']=e.prior.previous.compact(data);bad=e.b.seal(bad)
                with self.subTest(mutation=mutation),self.assertRaises((ValueError,TypeError)):
                    e.check(m,bad)


if __name__=='__main__':unittest.main()
