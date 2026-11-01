"""Independent fixed-H equations and section/tube controls for C_RG2b."""
from pathlib import Path
import sys,unittest
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_c_rg2b import *
from spark_completion_c_rg2b_campaign import prepared_values,prepare_source,decode
from spark_completion_positive import fixture,propose_center

class CRG2bTests(unittest.TestCase):
    def setUp(self):
        self.precision=ctx.prec;ctx.prec=PRECISION;self.source,self.values,self.targets=fixture()
    def tearDown(self):ctx.prec=self.precision
    def test_independent_rational_equations_both_geometry_consumers(self):
        for graph in (self.source,self.targets['1']['graph']):
            m=CRG2bReference(graph);e=COSReference(graph,'rational')
            c=e.matrix([[e.q(1)+e.q(i,100)]for i in range(m.n)])
            H=e.matrix([[int(i==j)+e.q(1,2**18)*(int(i==j)+int(bool(m.overlap[i][j])))for j in range(m.m)]for i in range(m.m)])
            # Separate implementation solves the original equations directly.
            r=e.read(c,H,eta=e.q(1,1024));s=m.lag(arb_mat(c),m.operators(arb_mat(H)))
            for actual,expected in [(s['current'],r['current']),(s['causal_flat'],r['causal_flat']),
                (s['increment'],-e.q(8)*e.B*r['current']),(s['geometry'],e.geometry(r['causal_flat']))]:
                self.assertTrue(all(a.contains(arb(b)) for a,b in zip(actual.entries(),expected.entries())))
            self.assertNotEqual(r['current'],e.read(c,e.I,eta=e.q(1,1024))['current'])
    def test_global_quartic_bounds_nested_domains_and_caches(self):
        for graph in (self.source,self.targets['1']['graph']):
            m=CRG2bReference(graph);d=m.domain
            self.assertLess(F(d['base_lipschitz']),1);self.assertLess(F(d['section_value_radius']),RHO)
            self.assertLessEqual(F(d['image_lipschitz']),LIP);self.assertLess(F(d['graph_transform_contraction']),F(1,50))
            self.assertFalse(d['section_C1_claimed']);self.assertFalse(d['reference_zero_site_bounds_reused'])
            m.operators(m.I);builds=m.lag_operator_builds;m.operators(m.I);self.assertEqual(builds,m.lag_operator_builds)
            with ctx.workprec(PROPOSAL_BITS):m.operators(m.I)
            self.assertEqual(m.lag_operator_builds,builds+1);m.operators(m.I);self.assertEqual(m.lag_operator_builds,builds+1)
        self.assertGreater(graph_algebra.cache_info().hits,0)
    def test_completed_inverse_inside_and_outside_retraction(self):
        m=CRG2bReference(self.targets['1']['graph'])
        for base in (-2,1,6):
            target=arb_mat([[base+arb(fmpq(i,10))]for i in range(m.n)])
            with ctx.workprec(PROPOSAL_BITS):x,_=m.inverse_proposal(target,m.I,target)
            original=m.clip(x);independent=COSReference(m.graph,'arb').read(original,m.I,eta=ball(ETA))
            residual=x-ball(DT)*m.B*independent['current']-target
            self.assertLess(norm_upper(residual),arb(2)**-220)
    def test_finite_section_invariance_and_boundary(self):
        m=CRG2bReference(self.targets['1']['graph']);c=m.quantize(m.vector({n:str(x) for n,x in self.targets['1']['states']['current'].items()}))
        s=m.section(c,retain_chain=True);value=c+s['read']['increment'];nextc=m.quantize(value);nexts=m.section(nextc)
        shift=ball(LIP)*maxnorm(value-nextc)
        for i in range(m.m):
            for j in range(m.m):
                left=nexts['geometry'][i,j]+arb(0,shift.upper().fmpq());right=s['read']['geometry'][i,j]
                self.assertTrue(left.overlaps(right))
        self.assertEqual(len(s['chain']),DEPTH);self.assertLess(s['error'],arb(2)**-100)
        self.assertGreater(s['tail'],0);self.assertLess(s['residual_error'],s['tail'])
    def test_full_metric_trap_and_all_physical_directions(self):
        p,_=trap_certificate(self.targets);self.assertEqual(p['relative_dimension'],14)
        self.assertLess(F(p['contraction'][1]),1);self.assertGreater(F(p['strict_image_margin'][0]),0)
        m=CRG2bReference(self.targets['1']['graph']);c=m.vector(p['center']);r=arb(2)**-96
        s=m.section(c);nextc,nextr,_=m.advance_tube(c,r,s)
        for k in range(m.n-1):
            v=arb_mat([[int(i==k)-int(i==m.n-1)]for i in range(m.n)])*arb(2)**-104
            z=m.section(c+v);image=c+v+z['read']['increment'];delta=image-nextc
            self.assertLess(norm_upper(delta)*m.trace.sqrt(),nextr)
    def test_fresh_source_event_transfer_and_declared_reset(self):
        prepared=prepared_values()
        for role in ('current','reset'):
            m,c,r,s=prepare_source(self.source,self.targets,role,prepared)
            self.assertEqual(sum(c.entries()),21);self.assertGreater(F(s['spark_margin'][0]),0)
            self.assertFalse(s['reset_advanced']);self.assertFalse(s['geometry_history_transported'])
            self.assertTrue(s['target_section_rebuilt']);self.assertGreaterEqual(r,0)

if __name__=='__main__':unittest.main(verbosity=2)
