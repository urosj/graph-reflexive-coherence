"""Independent C_PC equation, writer, full-state derivative and cache pressure."""
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
from spark_completion_pc import CPCReference, global_domain, trap_certificate, graph_constants, _graph_constants
from spark_completion_positive import fixture, norm_upper
from spark_completion_ci_campaign import retained
from spark_completion_os_reference import COSReference


class PCScience(unittest.TestCase):
    def setUp(self):
        self.prec = ctx.workprec(512); self.prec.__enter__()
        self.source, _, self.targets = fixture()
        self.m = CPCReference(self.targets['1']['graph'])
        self.old = retained('SC2PositiveCandidate.json.xz')['checks']['trap']
        self.C = self.m.vector(self.old['center'])

    def tearDown(self):
        self.prec.__exit__(None, None, None)

    def test_signed_domain_exact_graph_cache_and_precision_boundary(self):
        for graph in (self.source, self.targets['1']['graph']):
            d = global_domain(graph)
            self.assertLess(F(d['source_norm_upper'][1]), F(d['carrier_radius']))
            self.assertTrue(d['signed_carriers'])
        before = _graph_constants.cache_info()
        a = graph_constants(self.targets['1']['graph'])
        self.assertEqual(graph_constants(deepcopy(self.targets['1']['graph'])), a)
        self.assertGreater(_graph_constants.cache_info().hits, before.hits)
        self.assertNotEqual(graph_constants(self.source), a)
        m = self.m
        for sign in (-1, 1):
            Z = m.zero(); Z[0, 0] = m.q(sign, 1024)
            m.pc_read(self.C, Z)
        bad = m.zero(); bad[0, 0] = m.q(1, 32)
        with self.assertRaises(ValueError): m.pc_read(self.C, bad)
        with ctx.workprec(256), self.assertRaises(ValueError): m.pc_read(self.C, m.zero())

    def test_literal_similarity_star_source_and_old_carrier_timing(self):
        m = self.m; Z = m.zero()
        for i in range(m.m): Z[i, i] = m.q((-1)**i, 2**16)
        C = m.vector({k:str(v) for k,v in self.targets['1']['states']['current'].items()})
        read = m.pc_read(C, Z)
        exact = COSReference(self.targets['1']['graph'], 'rational')
        exC = exact.vector({k:str(v) for k,v in self.targets['1']['states']['current'].items()})
        exZ = exact.matrix([[fmpq((-1)**i, 2**16) if i == j else 0
                            for j in range(m.m)] for i in range(m.m)])
        J, flat = exact.direct_similarity_read(exC, exact.I+exZ/2, eta=exact.q(1, 1024))
        for i in range(m.m):
            self.assertTrue(read['selected']['current'][i, 0].contains(arb(J[i, 0])))
            self.assertTrue(read['selected']['causal_flat'][i, 0].contains(arb(flat[i, 0])))
        S = exact.matrix(m.m, m.m)
        for v in m.nodes:
            for i,e in enumerate(m.edges):
                for j,f in enumerate(m.edges):
                    if v in e and v in f: S[i, j] += flat[i, 0]*flat[j, 0]/4
        for i in range(m.m):
            for j in range(m.m): self.assertTrue(read['source'][i,j].contains(arb(S[i,j])))
        C1, Z1 = m.advance(C, Z, read)
        actual = exC-32*exact.B*J
        self.assertTrue(all(C1[i,0].contains(arb(actual[i,0])) for i in range(m.n)))
        writer = m.decay*Z+(1-m.decay)*m.matrix(S)
        self.assertTrue(all(Z1[i,j].overlaps(writer[i,j]) for i in range(m.m) for j in range(m.m)))
        wrong = m.pc_read(C1, Z)['source']
        self.assertGreater(norm_upper(wrong-read['source']), 0)
        with self.assertRaises(ValueError): m.advance(C1, Z, read)

    def test_quiescent_zero_source_release_is_exponential(self):
        m = self.m; C = m.matrix([[1] for _ in m.nodes]); Z = m.zero()
        Z[0,0] = m.q(-1,1024)
        result = m.pc_step(C, Z)
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
        p = m.partials(box, Zbox); start = m.pc_step(C,Z)
        for k in range(m.n-1):
            direction = m.matrix([[int(i==k)-int(i==m.n-1)] for i in range(m.n)])
            end = m.pc_step(C+h*direction,Z)
            quotient = (end['after']-start['after'])/h
            dc = p['CC']*direction
            self.assertTrue(all(dc[i,0].contains(quotient[i,0]) for i in range(m.n)))
            source_diff = (end['read']['source']-start['read']['source'])/h
            expected = p['SC']*direction
            self.assertTrue(all(expected[k,0].contains(source_diff[i,j]*(1 if i==j else arb(2).sqrt()))
                                for k,(i,j) in enumerate(m.pairs)))
        for k,(i,j) in enumerate(m.pairs):
            direction = m.zero(); direction[i,j] = 1; direction[j,i] = 1
            end = m.pc_step(C,h*direction)
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
