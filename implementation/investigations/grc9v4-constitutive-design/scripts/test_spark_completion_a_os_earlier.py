"""Pressure tests for oblique full-state trapping and its claimed early entry."""
from copy import deepcopy
import unittest
import check_spark_completion_a_os_earlier as check
e=check.e


class EarlierDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs=e.originals();cls.domain=e.read_json(e.EARLIER+'AOSAnisotropicDomain.json')
        cls.proof,cls.o=e.anisotropic_certificate(cls.runs,cls.domain)
        cls.evidence=e.read_json(e.EARLIER+'AOSEarlierChecks.json.xz')

    def test_complete_interval_recomputation(self):
        self.assertEqual(check.check()['retained_states'],2065)
        for role,entry,end in [('current',375,377),('reset',372,374)]:
            r=self.evidence['runs'][role]
            self.assertEqual((r['anisotropic_entry'],r['anisotropic_window_end']),(entry,end))
            self.assertEqual(r['additional_event_gain'],0)
            self.assertFalse(r['reset_earns_live_gain'])
            self.assertGreater(e.F(r['interval_checks'][entry-2]['anisotropic_distance'][0]),1)
            self.assertLess(e.F(r['interval_checks'][entry-1]['anisotropic_distance'][1]),1)

    def test_full_map_secants_in_all_thirty_oblique_directions(self):
        with e.ctx.workprec(e.PRECISION):
            o=self.o;m=o['model'];S=e.arb_mat(o['S']);U=e.arb_mat(o['U'])
            C,L=o['center_C'],o['center_L'];h=e.arb(e.fmpq(1,256))
            base=m.step(C,L);base=e.stack(base['after'],base['logW_after'])
            for k in range(30):
                for sign in (-1,1):
                    dc=e.arb_mat([[S[i,k]*sign] for i in range(m.n)])
                    dl=e.arb_mat([[S[m.n+i,k]*sign] for i in range(m.m)])
                    s=m.step(C+h*dc,L+h*dl);diff=U*(e.stack(s['after'],s['logW_after'])-base)/h
                    self.assertTrue(all((o['derivative'][i,k]*sign).contains(diff[i,0]) for i in range(30)),(k,sign))
            self.assertTrue(all(sum(o['S'][i,j] for i in range(m.n))==0 for j in range(30)))
            self.assertGreater(e.F(self.proof['positive_relative_neighborhood_lower']),0)

    def test_rank_missing_history_radius_and_source_controls(self):
        for defect in ('rank','missing_history','radius','source','promotion'):
            p=deepcopy(self.domain)
            if defect=='rank':
                for row in p['basis']:row[-1]=row[-2]
            if defect=='missing_history':p['basis']=p['basis'][:14]
            if defect=='radius':p['axis_radii'][0]='0'
            if defect=='source':p['sources'][0]['sha256']='0'*64
            if defect=='promotion':p['accepted_authority']=True
            p=e.sealed({k:v for k,v in p.items() if k!='record_digest'})
            with self.subTest(defect=defect),self.assertRaises(ValueError):e.anisotropic_certificate(self.runs,p)

    def test_actual_domain_support_and_edge_crossing_rejection(self):
        o=self.o;m=o['model'];S=o['S'];center=self.runs['current']['proof']['center']
        self.assertLess(e.F(self.proof['enclosing_coordinate_box_minimum_edge_margin']),0)
        self.assertGreater(e.F(self.proof['geometry']['1']['minimum_order_margin'][0]),0)
        # The exact support is attained by a sign corner of the unit cube.
        for i,j in m.pairs:
            a=[S[i,k]-S[j,k] for k in range(30)];corner=[1 if x>=0 else -1 for x in a]
            self.assertEqual(sum(x*s for x,s in zip(a,corner)),sum(map(abs,a)))
        with e.ctx.workprec(e.PRECISION),self.assertRaisesRegex(ValueError,'edge-order'):
            e.uniform_geometry(m,o['Cbox'],o['Lbox'],center,lambda i,j:e.arb(100))

    def test_exact_spectral_inequalities_and_observed_obstruction(self):
        ball,P=e.enlarged_ball_certificate(self.runs)
        self.assertEqual(ball,self.evidence['enlarged_ball'])
        self.assertEqual([len(x) for x in ball['positive_definite_pivots'].values()],[14,14])
        with self.assertRaisesRegex(ValueError,'positive definite'):e.positive_definite_exact(e.fmpq_mat([[1,2],[2,1]]))
        for role,before in [('current',364),('reset',352)]:
            r=self.evidence['runs'][role];flip=r['last_order_reversal']
            self.assertEqual((flip['before_step'],flip['after_step']),(before,before+1))
            with e.ctx.workprec(e.PRECISION):
                m=self.o['model'];k=m.edge_ids.index(flip['edge_id']);i,j=m.pairs[k]
                for step,sign in [(before,-1),(before+1,1)]:
                    C,L=e.decode(m,r['checkpoints'][str(step)]['original_state'])
                    self.assertGreater((C[i,0]-C[j,0])*sign,0)


if __name__=='__main__':unittest.main()
