"""Focused joint-root and lifecycle covariance pressure; no broad rerun."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import p984e_cci as e


class JointCovarianceTests(unittest.TestCase):
    def test_root_matrix_transport_is_two_sided_and_independent_of_current(self):
        d=e.algebra.declarations()[-1]
        p=e.b.read(e.prior.INPUTS)['initial_inputs'];q=e.algebra.transform(p,d)
        indices=e.algebra.mapping(p['reference']['graph'],q['reference']['graph'],d)
        _,ei,s=indices;n=len(ei);x=e.b.np.arange(1.,n+1)/16
        root=dict(domain_id='same',recipe='same')
        for key in ('J','read_current','baseline','readback','flat'):root[key]=x.tolist()
        for key in ('H','source','generated'):root[key]=(e.b.np.eye(n)+e.b.np.outer(x,x)).tolist()
        target=deepcopy(root)
        for key in ('J','read_current','baseline','readback','flat'):target[key]=(x[ei]*s).tolist()
        for key in ('H','source','generated'):
            target[key]=(e.b.np.array(root[key])[e.b.np.ix_(ei,ei)]*e.b.np.outer(s,s)).tolist()
        policy=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13)
        self.assertEqual(e.root_pair(root,target,indices,policy),0)
        for key in ('H','source','generated'):
            bad=deepcopy(target);bad[key][0][1]*=-1
            with self.subTest(field=key),self.assertRaises(ValueError):e.root_pair(root,bad,indices,policy)
        bad=deepcopy(target);bad['domain_id']='different'
        with self.assertRaises(ValueError):e.root_pair(root,bad,indices,policy)

    def test_transformed_inputs_preserve_roles_and_bind_reference(self):
        p=e.b.read(e.prior.INPUTS)['initial_inputs']
        for d in e.algebra.declarations():
            q=e.algebra.transform(p,d);e.b.GeometryStageInputs.from_payload(q)
            for role in e.ROLES:self.assertEqual(q[role]['C'],[p[role]['C'][i] for i in d['node_order']])
            self.assertNotEqual(q['current']['C'],q['reset']['C'])
        q=e.algebra.transform(p,e.algebra.declarations()[3]);q['reference']['profile']=p['reference']['profile']
        with self.assertRaises(ValueError):e.b.GeometryStageInputs.from_payload(q)

    def test_retained_rejects_joint_root_and_lifecycle_mutations_without_native(self):
        if not (e.b.ROOT/e.RESULTS).exists():self.skipTest('campaign not captured')
        m=e.b.read(e.INPUTS);record=e.b.read(e.RESULTS);e.check_manifest(m)
        with patch.object(e,'check_manifest'),patch.object(e.r,'CandidateCIRoot',side_effect=AssertionError('native rerun')):
            self.assertEqual(e.check(m,record)['passing_pending_cells'],20)
            for mutation in ('H_only','domain','recipe','source_C','missing_role','short_horizon','reference_current','acceptance'):
                bad=deepcopy(record);data=e.prior.previous.expand(bad['execution']);row=data['cases'][0]
                if mutation in ('H_only','domain','recipe'):
                    root=row['roles']['current']['final']
                    if mutation=='H_only':root['H'][0][1]+=0.001
                    elif mutation=='domain':root['domain_id']='wrong'
                    else:root['recipe']='wrong'
                    cert=root.pop('independent_certificate');root=e.b.seal(root)
                    cert['selected_root_digest']=root['record_digest'];root['independent_certificate']=cert
                    row['roles']['current']['final']=root
                elif mutation=='source_C':data['sources'][2]['state']['inputs']['current']['C'].reverse()
                elif mutation=='missing_role':del row['roles']['reset']
                elif mutation=='short_horizon':row['roles']['current']['steps'].pop()
                elif mutation=='reference_current':row['event']['checkpoint']['reference_currents'][0]['roles']['reset']['target'][0]+=1
                else:bad['user_accepted']=True
                bad['execution']=e.prior.previous.compact(data);bad=e.b.seal(bad)
                with self.subTest(mutation=mutation),self.assertRaises((ValueError,TypeError)):
                    e.check(m,bad)


if __name__=='__main__':unittest.main()
