"""Exact polynomial oracle, whole-domain failures, full-state and tail isolation."""
import copy,unittest
from unittest.mock import patch
import check_spark_completion_c_rg2b_direct as checker
from check_spark_completion_c_rg2b_direct import *
import spark_completion_c_rg2b_direct as direct


class DirectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ctx.prec;ctx.prec=PRECISION
        cls.d,cls.domain=inputs();_,_,t=fixture();cls.m=CRG2bReference(t['1']['graph'])
        cls.Q=fmpq_mat([[fmpq(v) for v in row] for row in cls.domain['chebyshev_coefficients']])
        cls.cert=direct_certificate(cls.domain)

    @classmethod
    def tearDownClass(cls):ctx.prec=cls.old

    def test_exact_polynomial_against_direct_physical_identity_map(self):
        bound,residual=reference_residual(self.m,self.Q,fmpq(str(DECAY)))
        a=self.m.algebra
        for s in (F(0),F(1,13),F(1,2),F(7,8),F(1)):
            C=curve_at(self.Q,s)
            site=fmpq_mat([[(v-2)**3-(v-2)] for v in C.entries()])
            physical=C+fmpq(str(ETA*DT))*a['A']*(a['L']*C/64-site)
            actual=physical-curve_at(self.Q,s*DECAY)
            self.assertEqual(actual,curve_at(residual,s))
            squared=(actual.transpose()*a['P']*actual)[0,0]
            self.assertLessEqual(arb(squared).sqrt(),bound)
            self.assertEqual(sum(C.entries()),21)

    def test_full_domain_not_a_sampled_or_flat_geometry_claim(self):
        p=self.cert
        self.assertEqual(p['relative_dimension'],14)
        self.assertTrue(p['all_parameters_certified_continuously'])
        self.assertFalse(p['future_trajectory_required'])
        self.assertEqual(p['trajectory_inputs_to_domain_checker'],0)
        self.assertGreater(F(p['strict_image_margin'][0]),F(6,10**7))
        self.assertLess(F(p['common_contraction']['contraction'][1]),F(998,1000))
        self.assertGreater(F(p['common_contraction']['section_difference_correction'][0]),0)
        self.assertGreater(F(p['common_contraction']['geometry_value_correction'][0]),0)
        self.assertGreater(F(p['local_section']['inverse_cube_margin'][0]),0)
        self.assertFalse(p['local_section']['section_C1_claimed'])
        for chi in ('-1','1'):
            self.assertEqual(p['geometry'][chi]['complete_basins'],EXPECTED)
            self.assertEqual(len(p['geometry'][chi]['edge_directions']),self.m.m)
            self.assertGreater(F(p['geometry'][chi]['minimum_edge_margin'][0]),0)

    def test_bad_domain_rejected_after_rehash(self):
        for kind in ('zero_radius','lost_direction','charge','curve','wrong_completion'):
            d=copy.deepcopy(self.domain)
            if kind=='zero_radius':d['radius']='0'
            elif kind=='lost_direction':d['relative_dimension']=13
            elif kind=='charge':d['chebyshev_coefficients'][0][1]='0'
            elif kind=='wrong_completion':d['parameters']['duration']='32'
            else:
                # Preserve charge AND the curve origin while spoiling its image.
                for i,sign in ((0,1),(self.m.n-1,-1)):
                    for k in (0,1):d['chebyshev_coefficients'][i][k]=str(F(d['chebyshev_coefficients'][i][k])+F(sign,8))
            d=seal({k:v for k,v in d.items() if k!='record_digest'})
            with self.subTest(kind=kind),self.assertRaises(ValueError):direct_certificate(d)

    def test_local_inverse_and_whole_order_controls(self):
        bounds=CurveBounds(self.m,self.Q,RADIUS,SUBDIVISIONS)
        with patch.object(direct,'INVERSE_RADIUS',F(1,100)),self.assertRaisesRegex(ValueError,'inverse cube'):
            local_section(self.m,self.domain['center'],bounds.box())
        # Radius small enough for physical admission but too wide for edge order.
        wide=CurveBounds(self.m,self.Q,F(1,1024),SUBDIVISIONS)
        with self.assertRaises(ValueError):uniform_roster(self.m,self.m.graph,wide)

    def test_actual_section_in_all_fourteen_directions(self):
        m=self.m;C=m.quantize(arb_mat(curve_at(self.Q,F(1,2))))
        s=m.section(C);image=C+s['read']['increment']
        q=ball(F(self.cert['common_contraction']['contraction'][1]))
        local=self.cert['local_section'];L=ball(F(local['section_lipschitz'][1]));V=ball(F(local['section_value_radius'][1]))
        for k in range(m.n-1):
            for sign in (-1,1):
                delta=arb_mat([[ball(F(sign,2**18))*(int(i==k)-int(i==m.n-1))] for i in range(m.n)])
                z=C+delta;t=m.section(z);out=z+t['read']['increment']-image
                self.assertLess((out.transpose()*m.P*out)[0,0],q*q*(delta.transpose()*m.P*delta)[0,0])
                self.assertLess(maxnorm(t['geometry']-m.I),V)
                self.assertLess(maxnorm(t['geometry']-s['geometry']),L*maxnorm(delta))

    def test_no_old_tail_reads_and_window_membership_controls(self):
        original=Path.open;opened=[]
        def guarded(path,*args,**kwargs):
            opened.append(str(path))
            self.assertFalse(path.name in ('CRG2bFaster-current.json.xz','CRG2bFaster-reset.json.xz','CRG2b-current.json.xz','CRG2b-reset.json.xz'))
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):result=checker.check()
        self.assertEqual(result['retained_states'],784)
        self.assertEqual(result['supporting_trajectory_steps_after_completion'],0)
        for role in ('current','reset'):
            run=load(PREFIX+role+'.json.xz')['checks'];row=copy.deepcopy(run['observations'][ENTRY-1])
            membership(self.m,self.Q,row)
            row['radius']='0'
            with self.assertRaises(ValueError):membership(self.m,self.Q,row)
            row['radius']='1'
            with self.assertRaises(ValueError):membership(self.m,self.Q,row)
            row['step']=393
            with self.assertRaises(ValueError):membership(self.m,self.Q,row)


if __name__=='__main__':unittest.main(verbosity=2)
