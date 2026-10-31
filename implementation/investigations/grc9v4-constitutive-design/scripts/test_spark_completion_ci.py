"""Focused CI science pressure; no duplicate long continuation campaign."""
from pathlib import Path
import sys,json,lzma,unittest
from flint import arb,fmpq,ctx
ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_ci import CCIReference,global_root_domain,trap_certificate
from spark_completion_positive import fixture,norm_upper
from spark_completion_continuation import infnorm,geometric_roster
from spark_completion_ci_campaign import retained,exact_bounds
from fractions import Fraction as F


class CIScience(unittest.TestCase):
    def setUp(self):
        self.prec=ctx.workprec(512);self.prec.__enter__()
        self.source,_,self.targets=fixture();self.m=CCIReference(self.targets['1']['graph'])
        self.C=self.m.vector({k:str(v)for k,v in self.targets['1']['states']['current'].items()})
    def tearDown(self):self.prec.__exit__(None,None,None)

    def test_uniform_domains_and_exact_quiescent_control(self):
        for graph in (self.source,self.targets['1']['graph']):
            d=global_root_domain(graph)
            self.assertLess(F(d['image_bound']),F(d['causal_flat_radius']))
            self.assertLess(F(d['contraction']),1)
            self.assertLess(F(d['hodge_deviation']),1)
        m=self.m;C=m.matrix([[1]for _ in m.nodes]);r=m.root(C)
        self.assertTrue(all(x==0 for x in r['selected']['current'].entries()))
        self.assertEqual(r['geometry'],m.I)
        self.assertEqual(m.ci_step(C)['after'],C)
        for bad in ('-1/100','401/100'):
            C[0,0]=m.q(fmpq(bad))
            with self.assertRaises(ValueError):m.root(C)

    def test_independent_picard_and_literal_physical_read(self):
        m=self.m;r=m.root(self.C)
        f=m.matrix([[0]for _ in range(m.m)])
        for _ in range(32):f=m.read(self.C,m.geometry(f),eta=m.q(1,1024))['causal_flat']
        residual=infnorm(m.read(self.C,m.geometry(f),eta=m.q(1,1024))['causal_flat']-f)
        radius=(residual/(1-m.root_q)).upper()
        independent=m.matrix([[arb(f[i,0].mid().fmpq(),(f[i,0].rad()+radius).upper().fmpq())]for i in range(m.m)])
        self.assertTrue(all(independent[i,0].overlaps(r['flat'][i,0])for i in range(m.m)))
        J,flat=m.direct_similarity_read(self.C,r['geometry'],eta=m.q(1,1024))
        self.assertTrue(all(J[i,0].overlaps(r['selected']['current'][i,0]) and flat[i,0].overlaps(r['flat'][i,0])for i in range(m.m)))
        regenerated=m.geometry(r['selected']['causal_flat'])
        self.assertTrue(all((regenerated-r['geometry'])[i,j].contains(0)for i in range(m.m)for j in range(m.m)))
        os=m.step(self.C,eta=m.q(1,1024),dt=m.q(32))
        self.assertGreater(max(abs((os['corrector']['current']-r['selected']['current'])[i,0]).lower()for i in range(m.m)),0)
        self.assertGreater(max(abs((os['geometry']-m.geometry(os['corrector']['causal_flat']))[i,j]).lower()for i in range(m.m)for j in range(m.m)),0)

    def test_partial_and_implicit_derivatives_on_finite_segments(self):
        m=self.m;r=m.root(self.C);f=r['proposal'];h=m.q(1,2**30)
        # Independent coordinate directions check both H uses and same-source root feedback.
        for k in (0,4,9):
            dc=m.matrix([[int(i==k)-int(i==m.n-1)]for i in range(m.n)])
            C0=self.C+dc*h  # also move the event's zero core into the positive domain if needed
            box=m.matrix([[arb(C0[i,0].mid().fmpq(),fmpq(1,2**29))]for i in range(m.n)])
            # Partial formula is smooth beyond the physical domain; the implicit
            # root comparison below uses a positive translated state instead.
            _,Ff,FC,Jf,JC=m.partials(box,f)
            actual=m.read(C0+h*dc,m.geometry(f),eta=m.q(1,1024))['causal_flat']-m.read(C0,m.geometry(f),eta=m.q(1,1024))['causal_flat']
            enclosure=FC*dc
            self.assertTrue(all(enclosure[i,0].contains(actual[i,0]/h)for i in range(m.m)))
            df=m.matrix([[int(i==k)]for i in range(m.m)])
            fbox=m.matrix([[arb(f[i,0].mid().fmpq(),fmpq(1,2**29))]for i in range(m.m)])
            _,Ff,_,_,_=m.partials(C0,fbox)
            actual=(m.read(C0,m.geometry(f+h*df),eta=m.q(1,1024))['causal_flat']-m.read(C0,m.geometry(f),eta=m.q(1,1024))['causal_flat'])/h
            enclosure=Ff*df
            self.assertTrue(all(enclosure[i,0].contains(actual[i,0])for i in range(m.m)))
        old=retained('SC2PositiveCandidate.json.xz')['checks']['trap'];C=m.vector(old['center'])
        R=m.q(fmpq(old['coordinate_radius']));box=m.matrix([[arb(C[i,0].fmpq(),R.fmpq())]for i in range(m.n)])
        J,_=m.full_jacobian(box)
        for k in (0,4,9):
            v=m.matrix([[int(i==k)-int(i==m.n-1)]for i in range(m.n)])
            quotient=(m.ci_step(C+h*v)['after']-m.ci_step(C)['after'])/h
            enclosure=J*v
            self.assertTrue(all(enclosure[i,0].contains(quotient[i,0])for i in range(m.n)))

    def test_full_physical_trap_is_separate_from_root_contraction(self):
        old=retained('SC2PositiveCandidate.json.xz')['checks']['trap']
        proof,_=trap_certificate({**self.targets['1'],'charts':self.targets},old)
        self.assertEqual(proof['relative_dimension'],14)
        self.assertLess(F(proof['full_CI_contraction'][1]),1)
        self.assertGreater(F(proof['strict_image_margin'][0]),0)
        self.assertGreater(F(proof['full_CI_contraction'][0]),F(proof['root_domain']['contraction']))
        self.assertFalse(proof['OS_trajectory_entry_reused'])
        self.assertEqual(set(proof['complete_basins']),{'1','-1'})


if __name__=='__main__':unittest.main()
