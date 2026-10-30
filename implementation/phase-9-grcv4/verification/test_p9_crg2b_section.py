from copy import deepcopy
import unittest

import numpy as np
from flint import ctx
import p9_crg2b_completion as c
import p9_crg2b_section as s
from test_p9_crg2b_completion import graph


class SectionPressure(unittest.TestCase):
    def setUp(self):
        self.graph=graph(4,[(0,1),(1,2),(2,3),(3,0),(0,2)])
        self.b,self.d,self.mask,_=c.graph_algebra(self.graph)
        self.cert=c.graph_certificate(self.graph)
        self.query=[3.,1.,2.,0.]
        self.x,self.h=s.proposal(np.array(self.b.tolist(),dtype=float),np.array(self.mask.tolist(),dtype=float),self.query)

    def test_full_edge_equations_overlap_vertex_reduced_intervals(self):
        with ctx.workprec(s.BITS):
            b=s.matrix(self.b.tolist());h=s.matrix(self.h[0]);x=s.matrix([[v] for v in self.query])
            t=(s.ball(c.KM)*(sum((x[i,0] for i in range(4)),s.arb(0))/4).tanh()).exp()
            d=b.transpose()*b; ident=s.eye(d.nrows());p=s.ball(c.CHI*c.ZETA)
            j0=-t*d*h*b.transpose()*x
            response=(ident+t*h*d).inv();expected=(ident-p*response).solve(j0)
            _,_,actual=s.literal(b,self.mask,self.query,h)
            for i in range(len(self.mask.tolist())):self.assertTrue(expected[i,0].overlaps(actual[i,0]))

    def test_chain_meets_budget_and_sparse_encoding_is_lossless(self):
        result=s.certify(self.graph,self.query,self.x,self.h,self.cert)
        self.assertTrue(result['section_tolerance_passes'])
        xs,hs=s.decode(s.encode(self.x,self.h))
        for a,b in zip(self.x+self.h,xs+hs,strict=True):np.testing.assert_array_equal(a,b)

    def test_stale_intermediate_geometry_is_seen_by_full_residual(self):
        hs=[h.copy() for h in self.h];hs[2][0,0]+=2**-20
        result=s.certify(self.graph,self.query,self.x,hs,self.cert)
        self.assertFalse(result['section_tolerance_passes'])

    def test_wrong_query_terminal_and_nonfinite_work_are_rejected(self):
        xs=[v.copy() for v in self.x];xs[0][0]+=1
        with self.assertRaisesRegex(ValueError,'query/terminal'):s.certify(self.graph,self.query,xs,self.h,self.cert)
        hs=[v.copy() for v in self.h];hs[-1][0,0]+=2**-20
        with self.assertRaisesRegex(ValueError,'query/terminal'):s.certify(self.graph,self.query,self.x,hs,self.cert)
        xs=[v.copy() for v in self.x];xs[3][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'operands'):s.certify(self.graph,self.query,xs,self.h,self.cert)

    def test_sparse_duplicate_cannot_hide_stale_coordinate(self):
        packed=s.encode(self.x,self.h);packed['h_upper_nonzero'][0].append(packed['h_upper_nonzero'][0][0])
        with self.assertRaisesRegex(ValueError,'coordinate'):s.decode(packed)


if __name__=='__main__':unittest.main()
