"""Independent C_CI_PC equation, writer, full-state derivative and cache pressure."""
from pathlib import Path
import sys
import unittest
from fractions import Fraction as F
from copy import deepcopy
from flint import arb, fmpq, ctx

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0] = [str(ROOT/'src'), str(INV/'research'),
               str(INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_ci_pc import CCIPCReference, global_domain, trap_certificate, graph_constants, _graph_constants
from spark_completion_positive import fixture, norm_upper
from spark_completion_ci_campaign import retained
from spark_completion_os_reference import COSReference


class PCScience(unittest.TestCase):
    def setUp(self):
        self.prec = ctx.workprec(512); self.prec.__enter__()
        self.source, _, self.targets = fixture()
        self.m = CCIPCReference(self.targets['1']['graph'])
        self.old = retained('SC2PositiveCandidate.json.xz')['checks']['trap']
        self.C = self.m.vector(self.old['center'])

    def tearDown(self):
        self.prec.__exit__(None, None, None)

    def test_signed_domain_exact_graph_cache_and_precision_boundary(self):
        for graph in (self.source, self.targets['1']['graph']):
            d = global_domain(graph)
            self.assertLess(F(d['source_norm_upper']), F(d['carrier_radius']))
            self.assertTrue(d['signed_carriers'])
        before = _graph_constants.cache_info()
        a = graph_constants(self.targets['1']['graph'])
        self.assertEqual(graph_constants(deepcopy(self.targets['1']['graph'])), a)
        self.assertGreater(_graph_constants.cache_info().hits, before.hits)
        self.assertNotEqual(graph_constants(self.source), a)
        m = self.m
        for sign in (-1, 1):
            Z = m.zero(); Z[0, 0] = m.q(sign, 1024)
            m.ccipc_read(self.C, Z)
        bad = m.zero(); bad[0, 0] = m.q(1, 32)
        with self.assertRaises(ValueError): m.ccipc_read(self.C, bad)
        with ctx.workprec(256), self.assertRaises(ValueError): m.ccipc_read(self.C, m.zero())

    def test_independent_picard_literal_root_and_same_source_gain_two(self):
        from spark_completion_continuation import infnorm
        m=self.m;C=m.matrix([[m.q(1)+m.q(i,32)]for i in range(m.n)]);Z=m.zero()
        for i,j in m.pairs: Z[i,j]=m.q((-1)**(i+j),2**16);Z[j,i]=Z[i,j]
        root=m.ccipc_read(C,Z);f=m.matrix(m.m,1)
        for _ in range(40): f=m.read(C,m.geometry_with_history(f,Z),eta=m.q(1,1024))['causal_flat']
        residual=infnorm(m.read(C,m.geometry_with_history(f,Z),eta=m.q(1,1024))['causal_flat']-f)
        error=(residual/(1-m.root_q)).upper()
        independent=m.matrix([[arb(f[i,0].mid().fmpq(),(f[i,0].rad()+error).upper().fmpq())]for i in range(m.m)])
        self.assertTrue(all(x.overlaps(y)for x,y in zip(independent.entries(),root['flat'].entries())))
        J,flat=m.direct_similarity_read(C,root['geometry'],eta=m.q(1,1024))
        self.assertTrue(all(x.overlaps(y)for x,y in zip(J.entries(),root['selected']['current'].entries())))
        self.assertTrue(all(x.overlaps(y)for x,y in zip(flat.entries(),root['flat'].entries())))
        self.assertTrue(all(x.contains(0)for x in (root['geometry']-m.I-(Z+root['source'])/2).entries()))
        # At a stationary writer Z=S, the composite contribution is exactly S.
        fixedH=m.geometry_with_history(root['proposal'],m.source(root['proposal']))
        self.assertTrue(all(x.contains(0)for x in (fixedH-m.I-m.source(root['proposal'])).entries()))
        C1,Z1=m.advance(C,Z,root)
        expected=m.decay*Z+(1-m.decay)*root['source']
        self.assertTrue(all(x.overlaps(y)for x,y in zip(Z1.entries(),expected.entries())))
        with self.assertRaises(ValueError): m.advance(C1,Z,root)

    def test_quiescent_zero_source_release_is_exponential(self):
        m = self.m; C = m.matrix([[1] for _ in m.nodes]); Z = m.zero()
        Z[0,0] = m.q(-1,1024)
        result = m.ccipc_step(C, Z)
        self.assertEqual(result['after'], C)
        self.assertTrue(all(x == 0 for x in result['read']['source'].entries()))
        self.assertTrue(result['carrier_after'][0,0].contains(-(-arb(1)).exp()/1024))
        self.assertLess(result['carrier_after'][0,0], 0)
        self.assertNotEqual(result['carrier_after'][0,0], 0)

    def test_full_derivative_on_all_independent_charge_and_carrier_directions(self):
        m = self.m; C = self.C; Z = m.zero(); h = m.q(1,2**35)
        R = fmpq(self.old['coordinate_radius'])
        box = m.matrix([[arb(C[i,0].fmpq(), R)] for i in range(m.n)])
        Zbox = m.zero()
        for i,j in m.pairs:
            Zbox[i,j] = arb(0,fmpq(1,2**30)); Zbox[j,i] = Zbox[i,j]
        p = m.partials(box, Zbox); start = m.ccipc_step(C,Z)
        for k in range(m.n-1):
            direction = m.matrix([[int(i==k)-int(i==m.n-1)] for i in range(m.n)])
            end = m.ccipc_step(C+h*direction,Z)
            quotient = (end['after']-start['after'])/h
            dc = p['CC']*direction
            self.assertTrue(all(dc[i,0].contains(quotient[i,0]) for i in range(m.n)))
            source_diff = (end['read']['source']-start['read']['source'])/h
            expected = p['SC']*direction
            self.assertTrue(all(expected[k,0].contains(source_diff[i,j]*(1 if i==j else arb(2).sqrt()))
                                for k,(i,j) in enumerate(m.pairs)))
        for k,(i,j) in enumerate(m.pairs):
            direction = m.zero(); direction[i,j] = 1; direction[j,i] = 1
            end = m.ccipc_step(C,h*direction)
            quotient = (end['after']-start['after'])/h
            scale = 1 if i==j else arb(2).sqrt()
            self.assertTrue(all((p['CZ'][r,k]*scale).contains(quotient[r,0]) for r in range(m.n)))
            source_diff = (end['read']['source']-start['read']['source'])/h
            self.assertTrue(all((p['SZ'][r,k]*scale).contains(source_diff[a,b]*(1 if a==b else arb(2).sqrt()))
                                for r,(a,b) in enumerate(m.pairs)))

    def test_full_trap_covers_carriers_and_separates_reference_stationarity(self):
        proof,_ = trap_certificate({**self.targets['1'],'charts':self.targets}, self.old)
        self.assertEqual(proof['full_dimension'], 60)
        self.assertEqual(proof['carrier_dimension'], 46)
        self.assertLess(F(proof['full_contraction'][1]), 1)
        self.assertGreater(F(proof['strict_image_margin'][0]), 0)
        self.assertGreater(F(proof['reference_submap_margin'][0]), 0)
        self.assertGreater(F(proof['derivative_blocks']['CZ'][0]), 0)
        self.assertGreater(F(proof['derivative_blocks']['ZC'][0]), 0)
        self.assertTrue(proof['nonzero_carrier_directions_included'])


if __name__ == '__main__': unittest.main()
