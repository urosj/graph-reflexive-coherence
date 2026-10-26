"""Mapping/comparator preflight; no event/root/trajectory producers."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
import p984h_aci_covariance as m


def mapping_pressure(kind):
    with patch.object(m.c.p.native,'GRC9V4ACIOperation',side_effect=AssertionError('no event')):
        seed,request,identity,eid,target=m.subject(kind)
        m.require(request['history_policy']==m.c.p.aos_history_policy(seed.inputs.current,seed.inputs.reset),'both role policy')
        m.require(len(target.current.W_A)==407,'target history width')
        with m.transport():
            orders=m.maps.mapping(m.baseline()[0]['inputs']['reference']['graph'],seed.inputs.to_payload()['reference']['graph'],m.maps.declaration(kind))
        for role in m.ROLES:
            m.require(list(getattr(seed.inputs,role).W_A)==[m.baseline()[0]['inputs'][role]['W_A'][i] for i in orders[1]],'unsigned history')
        m.require(all(x>0 for x in target.current.W_A) and target.time==seed.inputs.time and target.current!=target.reset,'target authority/clock')
    print(kind,'mechanical mapping passed',flush=True)
    return kind


class CovarianceTests(unittest.TestCase):
    def test_eight_complete_mappings_and_unsigned_history(self):
        with ProcessPoolExecutor(max_workers=8,mp_context=mp.get_context('spawn')) as pool:
            self.assertEqual(list(pool.map(mapping_pressure,m.KINDS)),list(m.KINDS))

    def test_full_joint_comparator_not_just_current(self):
        old=dict(actual=dict(current=[1.,2.],baseline=[3.,4.],flux=[5.,6.],flat=[7.,8.],drive=[9.,10.],potential=[11.,12.]),
            joint=dict(H=[[1.,.1],[.1,1.]],source=[[2.,.2],[.2,3.]],generated=[[4.,.3],[.3,5.]],recipe='a',domain_id='d'))
        orders=([1,0],[1,0],[-1,1]);new=deepcopy(old)
        for k in ('current','baseline','flux','flat'):new['actual'][k]=(m.np.asarray(old['actual'][k])[orders[1]]*orders[2]).tolist()
        new['actual']['potential']=[12.,11.];new['actual']['drive']=[10.,9.]
        for k in ('H','source','generated'):new['joint'][k]=(m.np.asarray(old['joint'][k])[m.np.ix_(orders[1],orders[1])]*m.np.outer(orders[2],orders[2])).tolist()
        self.assertTrue(all(x==0 for x in m.root_pair(old,new,orders).values()))
        for k in ('H','source','generated'):
            with self.subTest(k=k):
                bad=deepcopy(new);bad['joint'][k][0][0]+=.01
                with self.assertRaisesRegex(ValueError,'covariance'):m.root_pair(old,bad,orders)
        bad=deepcopy(new);bad['actual']['drive'][0]*=-1
        with self.assertRaisesRegex(ValueError,'unsigned drive'):m.root_pair(old,bad,orders)


if __name__=='__main__':unittest.main()
