"""Focused independent-equation, completion, whole-domain and scope controls."""
import copy,unittest
from check_spark_completion_a_rg2b import *
from spark_completion_a_rg2b_direct import (curve_jets,reference_jets,bernstein_cells,
    composition,physical_bounds)
from spark_completion_a_os import PARAMETERS as A_PARAMETERS


class ARG2bScience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx.prec=PRECISION
        cls.declaration,cls.domain=inputs();cls.source,_,cls.targets=fixture()
        cls.m=ARG2bReference(cls.targets['1']['graph']);metric(cls.m)
        cls.Q=fmpq_mat([[fmpq(x) for x in row] for row in cls.domain['curves']['current']])

    def test_fresh_full_base_global_bounds(self):
        self.assertEqual({k:v for k,v in PARAMETERS.items() if k!='duration'},
            {k:v for k,v in A_PARAMETERS.items() if k!='duration'})
        for graph in (self.source,self.targets['1']['graph']):
            m=ARG2bReference(graph);v=m.domain
            self.assertLess(F(v['base_lipschitz']),1)
            self.assertLess(F(v['graph_transform_contraction']),1)
            self.assertLess(F(v['image_lipschitz']),LIP)
            self.assertTrue(v['writer_in_inverse']);self.assertFalse(v['reference_zero_site_bounds_reused'])
            for sign in (-1,0,1):
                X=arb_mat([[ball((a+b)/2+sign*(b-a)*F(49,100))] for a,b in m.chart]+
                    [[ball(sign*Y_RADIUS*F(49,50))] for _ in range(m.m)])
                derivative=m.fixed_jacobian(X,m.I)-m.state_identity
                self.assertLess(maxnorm(derivative),ball(v['A_X']))

    def test_independent_series_equations_and_directional_derivative(self):
        m=self.m;cells=bernstein_cells(self.Q,6)
        for index in (0,31,63):
            jets=curve_jets(cells[index],fmpq(1,64),at_midpoint=True)
            direct=reference_jets(m,jets)
            X=arb_mat([[v[0]] for v in jets]);dX=arb_mat([[v[1]] for v in jets])
            read=m.lag(X,m.I);derivative=m.fixed_direction(X,m.I,dX,read)
            self.assertTrue(all(a[0].overlaps(b) for a,b in zip(direct,(X+read['increment']).entries())))
            self.assertTrue(all(a[1].overlaps(b) for a,b in zip(direct,derivative.entries())))

    def test_both_geometry_consumers_are_live(self):
        m=self.m;X=arb_mat(curve_at(self.Q,1));C,L=m.unpack(X);W=m.exp(L)
        H=m.I+arb(2)**-20*m.I
        a=m.read(C,W,m.I);b=m.read(C,W,H)
        self.assertGreater(maxnorm(a['current']-b['current']),arb(2)**-100)
        expected=H.solve(arb_mat([[b['q'][i,0]*b['current'][i,0]/2] for i in range(m.m)]))
        self.assertTrue(all(x.overlaps(y) for x,y in zip(expected.entries(),b['causal_flat'].entries())))
        self.assertGreater(maxnorm(expected-arb_mat([[b['q'][i,0]*b['current'][i,0]/2] for i in range(m.m)])),arb(2)**-100)

    def test_joint_section_reuse_and_query_guard(self):
        m=self.m;X=m.quantize(arb_mat(curve_at(self.Q,1)))
        section=m.section(X);self.assertLess(section['error'],arb(2)**-100)
        after,r,_=m.advance_tube(X,arb(2)**-256,section)
        reused=m.reuse(X,section,after);fresh=m.section(after)
        self.assertTrue(all(a.overlaps(b) for a,b in zip(reused['geometry'].entries(),fresh['geometry'].entries())))
        with self.assertRaisesRegex(ValueError,'subject'):m.reuse(arb_mat(X),section,after)
        with self.assertRaisesRegex(ValueError,'exact proposed'):m.section(m.tube_box(X,arb(2)**-200))

    def test_full_continuous_domain_and_mutations(self):
        proof=curve_certificate(self.domain,'current')
        self.assertEqual(proof['relative_dimension'],30)
        self.assertLess(F(proof['physical']['contraction'][1]),1)
        self.assertGreater(F(proof['strict_image_margin'][0]),0)
        self.assertFalse(proof['future_trajectory_required'])
        self.assertEqual(proof['trajectory_inputs_to_domain_checker'],0)
        self.assertEqual(proof['geometry']['1']['complete_basins'],EXPECTED)
        for key,value in [('radius','0'),('relative_dimension',14),('coordinate_system','C_only'),('entry',301)]:
            bad=copy.deepcopy(self.domain);bad[key]=value
            with self.assertRaises(ValueError):curve_certificate(bad,'current')
        bad=copy.deepcopy(self.domain)
        for role in ('current','reset'):bad['curves'][role][0][0]='0'
        with self.assertRaisesRegex(ValueError,'charge'):curve_certificate(bad,'current')

    def test_no_later_trajectory_or_unknown_role(self):
        with self.assertRaisesRegex(ValueError,'subsequent supporting'):
            campaign('current',self.declaration,self.domain,maximum_steps=ENTRY+WINDOW+1)
        with self.assertRaisesRegex(ValueError,'history role'):
            prepare('unrecognized',self.declaration)


if __name__=='__main__':unittest.main(verbosity=2)
