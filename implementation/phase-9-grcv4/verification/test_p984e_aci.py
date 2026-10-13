"""A_CI unsigned-history versus signed-root covariance pressure."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984e_aci as e


class AHistoryCovarianceTests(unittest.TestCase):
    def test_transform_incidence_and_unsigned_distinct_histories(self):
        p=e.b.read(e.prior.INPUTS)['initial_inputs'];old=e.b.GeometryStageInputs.from_payload(p)
        self.assertEqual(e.transform(p,e.algebra.declarations()[0]),p)
        for d in e.algebra.declarations():
            q=e.transform(p,d);new=e.b.GeometryStageInputs.from_payload(q)
            ni,ei,s=e.mapping(p['reference']['graph'],q['reference']['graph'],d)
            self.assertTrue(e.b.np.array_equal(new.geometry.reference.graph.incidence,
                e.b.np.array(old.geometry.reference.graph.incidence)[e.b.np.ix_(ni,ei)]*s))
            for role in e.ROLES:
                self.assertEqual(q[role]['W_A'],[p[role]['W_A'][i] for i in ei])
                self.assertEqual(q[role]['C'],[p[role]['C'][i] for i in ni])
            self.assertNotEqual(q['current']['W_A'],q['reset']['W_A'])
        bad=deepcopy(e.algebra.declarations()[0]);bad['edge_order'][0]=bad['edge_order'][1]
        with self.assertRaisesRegex(ValueError,'nonbijective'):e.transform(p,bad)

    def test_root_signed_geometry_unsigned_conductance(self):
        p=e.b.read(e.prior.INPUTS)['initial_inputs'];d=e.algebra.declarations()[-1];q=e.transform(p,d)
        ids=e.mapping(p['reference']['graph'],q['reference']['graph'],d);_,ei,s=ids
        x=e.b.np.arange(1.,10.)/16;h=e.b.np.eye(9)+e.b.np.outer(x,x)
        a=dict(domain_id='same',recipe='same',W_hat_A=x.tolist());c=deepcopy(a)
        for k in ('J','read_current','baseline','readback','flat'):a[k]=x.tolist();c[k]=(x[ei]*s).tolist()
        for k in ('H','source','generated'):a[k]=h.tolist();c[k]=(h[e.b.np.ix_(ei,ei)]*e.b.np.outer(s,s)).tolist()
        c['W_hat_A']=x[ei].tolist();policy=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13)
        self.assertEqual(e.root_pair(a,c,ids,policy),0)
        for k in ('H','W_hat_A'):
            wrong=deepcopy(c)
            if k=='H':wrong[k][0][1]*=-1
            else:wrong[k]=(x[ei]*s).tolist()
            with self.subTest(field=k),self.assertRaises(ValueError):e.root_pair(a,wrong,ids,policy)

    def test_retained_history_writer_root_and_scope_pressure(self):
        if not (e.b.ROOT/e.RESULTS).exists():self.skipTest('campaign not captured')
        m=e.b.read(e.INPUTS);record=e.b.read(e.RESULTS);e.check_manifest(m)
        with patch.object(e,'check_manifest'),patch.object(e.r,'CandidateCIRoot',side_effect=AssertionError('native rerun')):
            self.assertEqual(e.check(m,record)['passing_pending_cells'],20)
            for mutation in ('signed_W','reset_W','writer','H_only','history_policy','missing_role','scope'):
                bad=deepcopy(record);data=e.prior.previous.expand(bad['execution']);row=data['cases'][0]
                if mutation=='signed_W':data['sources'][4]['state']['inputs']['current']['W_A'][0]*=-1
                elif mutation=='reset_W':row['roles']['reset']['steps'][0]['poststate']['reset']['W_A'][0]+=0.01
                elif mutation=='writer':row['roles']['current']['steps'][0]['writer_targets'][0]['J'][0]+=0.01
                elif mutation=='H_only':
                    root=row['roles']['current']['final'];root['H'][0][1]+=0.001
                    cert=root.pop('independent_certificate');root=e.b.seal(root)
                    cert['selected_root_digest']=root['record_digest'];root['independent_certificate']=cert
                    row['roles']['current']['final']=root
                elif mutation=='history_policy':row['request']['history_policy']['candidate_history_policy_digest']='forged'
                elif mutation=='missing_role':del row['roles']['reset']
                else:bad['user_accepted']=True
                bad['execution']=e.prior.previous.compact(data);bad=e.b.seal(bad)
                with self.subTest(mutation=mutation),self.assertRaises((ValueError,TypeError)):
                    e.check(m,bad)


if __name__=='__main__':unittest.main()
