"""Independent exact algebra and boundary pressure for the research extension."""
from copy import deepcopy
import unittest

from flint import fmpq as Q, fmpq_mat
import p9_crg2b_completion as c


def graph(n, pairs):
    ports = [0]*n
    edges = []
    for k, (u,v) in enumerate(pairs):
        ports[u] += 1; ports[v] += 1
        edges.append(dict(edge_id=str(k), tail=dict(node_id=u,port=ports[u]),
                          head=dict(node_id=v,port=ports[v])))
    return dict(live_node_ids=list(range(n)), edges=edges)


class CompletionPressure(unittest.TestCase):
    def test_vertex_reduction_matches_unreduced_edge_inverse_on_cycles(self):
        for n,pairs in [(4,[(0,1),(1,2),(2,3)]),
                        (4,[(0,1),(1,2),(2,3),(3,0),(0,2)])]:
            b,d,_,_ = c.graph_algebra(graph(n,pairs))
            reduced = c.eye(len(pairs))-b.transpose()*(c.eye(n)+b*b.transpose()).solve(b)
            self.assertEqual(reduced,(c.eye(len(pairs))+d).inv())
            self.assertEqual((c.eye(len(pairs))+d)*reduced,c.eye(len(pairs)))

    def test_noncommuting_full_chart_enclosures_and_current_identity(self):
        g=graph(4,[(0,1),(1,2),(2,3),(3,0),(0,2)])
        b,d,mask,_=c.graph_algebra(g);m=b.ncols(); ident=c.eye(m)
        r0=(ident+d).inv();bound=c.response_bounds(c.norm(r0),c.norm(ident-r0))
        values,checks=c.global_bounds(c.norm(b),c.norm(d),c.norm(mask),bound)
        self.assertTrue(all(checks.values()))
        # Star-supported indefinite perturbation, not only generated PSD sources.
        e=fmpq_mat([[0]*m for _ in range(m)])
        e[0,0]=c.RHO/2;e[1,1]=-c.RHO/2;e[0,1]=e[1,0]=c.RHO/2
        h=ident+e
        self.assertNotEqual(d*h,h*d)
        self.assertEqual(c.norm(e),c.RHO)
        for t in (1-c.KM,Q(1),1/(1-c.KM)):
            r=(ident+t*h*d).inv()
            self.assertLessEqual(c.norm(r),bound['response_upper'])
            self.assertLessEqual(c.norm(ident-r),bound['complement_upper'])
            x=fmpq_mat([[-1],[5],[-1],[5]])
            gradient=b.transpose()*x;j0=-t*d*h*gradient
            p=c.CHI*c.ZETA
            j=(ident-p*r).solve(j0)
            u=(ident+t*h*d-p*ident).solve(j0)
            self.assertEqual(j,j0+p*u)
            self.assertEqual(r*j,u)
            self.assertEqual(r*j0,(r-ident)*gradient-r*t*(d*h-h*d)*gradient)
            self.assertLessEqual(c.norm(j),values['current_upper'])
            v=h.solve(c.CHI*r*j)
            s=fmpq_mat([[c.ZETA*mask[i,k]*v[i,0]*v[k,0] for k in range(m)] for i in range(m)])
            self.assertLessEqual(c.norm(s),values['M_S'])

    def test_neumann_boundary_rejects_equality_and_beyond(self):
        # km=0 leaves delta=rho*s0, so equality is exact and independently chosen.
        for s in (Q(4),Q(4)+Q(1,100)):
            with self.assertRaisesRegex(ValueError,'inconclusive'):
                c.response_bounds(Q(1),s,rho=Q(1,4),km=Q(0))
        self.assertLess(c.response_bounds(Q(1),Q(4)-Q(1,100),rho=Q(1,4),km=Q(0))['perturbation'],1)

    def test_failed_sufficient_bound_is_not_claimed_physical_nonexistence(self):
        # The old sqrt(m)-style majorant fails; this says nothing about a root's existence.
        wide=c.response_bounds(Q(21),Q(21))
        _,checks=c.global_bounds(Q(9),Q(18),Q(9),wide)
        self.assertFalse(checks['graph_transform'])
        self.assertFalse(checks['lipschitz_class'])

    def test_graph_hypotheses_fail_closed(self):
        cases=[graph(4,[(0,1),(2,3)]),graph(3,[(0,1),(1,1),(1,2)]),
               graph(3,[(0,1),(1,0),(1,2)])]
        collision=graph(3,[(0,1),(1,2)])
        collision['edges'][1]['tail']['port']=1;cases.append(collision)
        invalid=graph(2,[(0,1)]);invalid['edges'][0]['tail']['port']=10;cases.append(invalid)
        duplicate=graph(3,[(0,1),(1,2)]);duplicate['edges'][1]['edge_id']='0';cases.append(duplicate)
        for g in cases:
            with self.subTest(graph=g),self.assertRaises(ValueError):c.graph_algebra(g)

    def test_order_and_orientation_preserve_exact_certificate(self):
        g=graph(5,[(0,1),(1,2),(2,3),(3,4),(4,0),(1,3)])
        other=deepcopy(g);other['live_node_ids'].reverse();other['edges'].reverse()
        other['edges'][0]['tail'],other['edges'][0]['head']=other['edges'][0]['head'],other['edges'][0]['tail']
        a,b=c.graph_certificate(g),c.graph_certificate(other)
        for name in ('bounds','response','checks','reference_response_norm','reference_complement_norm','selector_lower'):
            self.assertEqual(a[name],b[name])

    def test_long_path_does_not_gain_selector_credit_from_connectivity(self):
        g=graph(50,[(i,i+1) for i in range(49)])
        result=c.graph_certificate(g)
        self.assertFalse(result['checks']['constant_selector'])
        self.assertLess(Q(result['selector_lower']),c.CUTOFF)

    def test_changed_physical_parameters_cannot_inherit_certificate(self):
        source=c.read(c.INPUTS[1])
        c.validate_large_recipe(source)
        source['target']['profile']['params_resolved']['candidate']['zeta_C']*=2
        with self.assertRaisesRegex(ValueError,'parameter changed'):c.validate_large_recipe(source)


if __name__ == '__main__':unittest.main()
