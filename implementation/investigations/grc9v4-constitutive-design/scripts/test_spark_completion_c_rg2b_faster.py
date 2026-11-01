"""Section reuse errors, independent physical directions and finite-union controls."""
from check_spark_completion_c_rg2b_faster import *
import unittest,copy

class FasterTests(unittest.TestCase):
    def setUp(self):self.old=ctx.prec;ctx.prec=PRECISION
    def tearDown(self):ctx.prec=self.old
    def test_reuse_center_shift_and_independent_reconstruction(self):
        d=load(DECLARATION);m,C,r,_,_=prepare('current',d);s=m.section(C)
        nextC=m.quantize(C+s['read']['increment'])
        # A nontrivial exact-charge shift makes omission of the Lipschitz
        # displacement visible; quantization alone would be too small a test.
        moved=nextC+arb_mat([[arb(2)**-30*(int(i==0)-int(i==1))]for i in range(m.n)])
        cached=section_reuse(m,C,s,moved);fresh=m.section(moved)
        self.assertGreater(F(cached['reuse']['center_shift'][0]),F(1,2**31))
        self.assertGreater(cached['error'],ball(LIP)*arb(2)**-31)
        self.assertTrue(all(a.overlaps(b)for a,b in zip(cached['geometry'].entries(),fresh['geometry'].entries())))
        with self.assertRaisesRegex(ValueError,'subject'):section_reuse(m,arb_mat(C),s,moved)
    def test_reuse_encloses_both_signs_of_all_tangent_directions(self):
        _,_,targets=fixture();m=CRG2bReference(targets['1']['graph']);proof,_=trap_certificate(targets);C=m.vector(proof['center'])
        for k in range(m.n-1):
            for sign in (-1,1):
                x=C+arb_mat([[ball(F(sign,2**18))*(int(i==k)-int(i==m.n-1))]for i in range(m.n)])
                s=m.section(x);y=m.quantize(x+s['read']['increment']);cached=section_reuse(m,x,s,y);fresh=m.section(y)
                self.assertTrue(all(a.overlaps(b)for a,b in zip(cached['geometry'].entries(),fresh['geometry'].entries())))
    def test_finite_union_rejects_boundary_and_omitted_directions(self):
        _,runs=checked_inputs();p=union_certificate(runs);self.assertLess(F(p['common_contraction']['contraction'][1]),1)
        self.assertEqual(p['relative_dimension'],14);self.assertLess(p['completion_step'],400)
        for alteration,message in [('zero','zero-dimensional'),('order','edge direction'),('roster','basin roster'),('image','non-strict')]:
            bad=copy.deepcopy(runs);row=bad['current']['observations'][ENTRY-1]
            if alteration=='zero':row['radius']='0'
            elif alteration=='order':
                row['center']['n3']='3';row['center']['n4']=str(F(row['center']['n4'])+F(runs['current']['observations'][ENTRY-1]['center']['n3'])-3)
            elif alteration=='roster':row['complete_basins']={}
            else:bad['current']['observations'][ENTRY]['tube']['defect']=['1','1']
            with self.assertRaises(ValueError):union_certificate(bad)
    def test_full_direction_finite_difference_bound(self):
        _,runs=checked_inputs();p=load(BASE+'CRG2bFasterCertificate.json');m=CRG2bReference(runs['current']['targets']['1']['graph'])
        C=m.quantize((m.vector(runs['current']['observations'][ENTRY-1]['center'])+m.vector(runs['current']['terminal_proof']['center']))/2);s=m.section(C);image=C+s['read']['increment'];q=ball(F(p['common_contraction']['contraction'][1]))
        for k in range(m.n-1):
            for sign in (-1,1):
                delta=arb_mat([[ball(F(sign,2**18))*(int(i==k)-int(i==m.n-1))]for i in range(m.n)])
                z=C+delta;fresh=m.section(z);out=z+fresh['read']['increment']-image
                before=(delta.transpose()*m.P*delta)[0,0];after=(out.transpose()*m.P*out)[0,0]
                self.assertLess(after,q*q*before)

if __name__=='__main__':unittest.main(verbosity=2)
