"""Regularity equivalence, singular boundaries and actual small native staging."""
from copy import deepcopy
from dataclasses import replace
import unittest
from flint import fmpq_mat
import p984g_cos_bounds as p


class BoundsScience(unittest.TestCase):
    def test_regularity_equivalence_including_cycle_and_exact_zero(self):
        graphs=[[[1],[-1]],[[1,0],[-1,1],[0,-1]],
                [[1,0,-1],[-1,1,0],[0,-1,1]],[[0],[0]],[[1,0],[-1,0],[0,1],[0,-1]]]
        for rows in graphs:
            n,m=len(rows),len(rows[0]);b=fmpq_mat(rows)
            h0=[[int(i==j)*(i+1) for j in range(n)] for i in range(n)]
            hm=[[int(i==j)*(i+1)+(p.q('1/8') if abs(i-j)==1 else 0) for j in range(m)] for i in range(m)]
            for beta in (p.q('0'),p.q('1/2'),p.q('1'),p.q('3/2'),p.q('3')):
                for tau in (p.q('0'),p.q('1/4'),p.q('1')):
                    with self.subTest(rows=rows,beta=str(beta),tau=str(tau)):
                        direct=fmpq_mat([[int(i==j)*(1-beta) for j in range(m)] for i in range(m)])+tau*b.transpose()*fmpq_mat(h0).inv()*b*fmpq_mat(hm)
                        result=p.regularity(rows,h0,hm,beta,tau)
                        self.assertEqual(result['nonsingular'],direct.det()!=0)
                        self.assertFalse(result['inverse_constructed'])
        # Exact singularity with beta>1 must not be hidden by a rounded inverse.
        self.assertFalse(p.regularity([[1],[-1]],[[1,0],[0,1]],[[1]],3,1)['nonsingular'])
        for hm in ([[0]], [[-1]]):
            with self.assertRaises(ValueError):p.regularity([[1],[-1]],[[1,0],[0,1]],hm,0,1)
        with self.assertRaises(ValueError):p.regularity([[1],[-1]],[[1,1],[0,1]],[[1]],0,1)
        with self.assertRaises(ValueError):p.regularity([[1],[-1]],[[1,0],[0,1]],[[1]],0,-1)

    def test_rounding_boundaries_and_ambiguous_current_fail_closed(self):
        with p.ctx.workprec(p.BITS):
            half=p.a(p.q(1)+p.q('1/9007199254740992'))
            self.assertEqual(p.lo(p.rounded(half)),1)  # ties-to-even
            uncertain=p.a(1).union(p.a(1+2**-52))
            self.assertLess(p.lo(p.rounded(uncertain)),p.hi(p.rounded(uncertain)))
            with self.assertRaisesRegex(ValueError,'uniquely enclosed'):
                p.represented_continuity(p.matrix([[1],[-1]]),[1,1],p.arb_mat([[uncertain]]),.1)
            with self.assertRaises(ValueError):p.rounded(p.arb('nan'))

    def test_small_native_predictor_corrector_read_and_continuity(self):
        from pygrc.models.grc_v4_exact import exact_backend,ExactBackend
        from pygrc.models.grc_v4_geometry import GRCV4Graph,OrientedEdge,GRCV4Differential,VertexScalar
        from pygrc.models.grc_v4_realizations import CandidateCOSPass
        from pygrc.models.grc_v4_transport import provisional_continuity
        from tests.models.test_grc_v4_candidate_c import current_fixture
        graph=GRCV4Graph(('a','b','c'),(OrientedEdge('ab','a','b'),OrientedEdge('bc','b','c'),OrientedEdge('ca','c','a')))
        params=p.prior.read(p.prior.PREPARED)['source']['profile']['params_resolved']
        weights={e.edge_id:1 for e in graph.oriented_edges}
        for tau in (0,1):
            with self.subTest(tau=tau),exact_backend(ExactBackend.FLINT),p.ctx.workprec(p.BITS):
                candidate={k:v for k,v in params['candidate'].items() if k not in ('W_C_tr','W_C_tr_content_digest')}
                candidate['tau_C']=tau
                inputs=current_fixture(graph=graph,weights=weights,resource=(2.015625,2.,1.984375),
                    changes={'candidate':candidate,'geometry':{'kappa_H':.5},'realization':{'tolerance':1e-8}})
                inputs=replace(inputs,dt=2**-12)
                native=CandidateCOSPass(inputs)
                b=p.matrix(graph.incidence);c=p.matrix([[x] for x in inputs.current.C]);h=p.eye(3)
                for point in (native.predictor,native.corrector):
                    j,flux,flat,domain=p.staged_read(b,c,h,candidate,point.algebra.deformation[0])
                    for interval,actual in ((j,point.current.values),(flux,point.read.flux.values),(flat,point.read.causal_flat.values)):
                        for i,x in enumerate(actual):self.assertTrue(p.lo(interval[i,0])<=p.q(x)<=p.hi(interval[i,0]))
                    h=p.generated(b,flat,params,staged=True)
                    if point is native.predictor:
                        for i in range(3):
                            for k in range(3):self.assertTrue(p.lo(h[i,k])<=p.q(native.corrector.inputs.geometry.one_form_hodge.matrix[i][k])<=p.hi(h[i,k]))
                after,_=p.represented_continuity(b,inputs.current.C,j,inputs.dt)
                actual=provisional_continuity(VertexScalar(graph,inputs.current.C),native.corrector.current,inputs.dt,
                    differential=GRCV4Differential(graph,inputs.geometry.reference.profile.params_resolved.common))
                self.assertEqual([p.lo(after[i,0]) for i in range(3)],[p.q(x) for x in actual.values])
                # Compare reduced real equation against literal full-edge solves.
                t=(p.a(candidate['kappa_M_C'])*(p.a(2)/p.a(candidate['C_ref'])).tanh()).exp()
                hr=p.matrix([[1.02,.001,0],[.001,1.01,.002],[0,.002,1.03]])
                reduced,_,_,_=p.real_read(b,c,hr,candidate,t)
                baseline=-p.a(candidate['eta_C'])*p.a(candidate['kappa_Phi_C'])*b.transpose()*b*(t*hr)*b.transpose()*c
                response=(p.eye(3)+p.a(tau)*t*hr*b.transpose()*b).inv()
                literal=(p.eye(3)-p.a(candidate['zeta_C'])*p.a(candidate['chi_C'])*response).solve(baseline)
                for i in range(3):self.assertTrue(reduced[i,0].overlaps(literal[i,0]))


class RetainedBounds(unittest.TestCase):
    def test_retained_scope_and_semantic_mutations(self):
        m,r=p.prior.read(p.INPUTS),p.prior.read(p.RESULTS)
        summary=p.check(m,r)
        self.assertEqual(summary['staged_positive'],4)
        for change in ('scope','count','width','error','current','selector','sign'):
            altered=deepcopy(r);case=altered['cases'][2]['staged']
            if change=='scope':altered['native_admission']=True
            if change=='count':altered['cases'].pop()
            if change=='width':case['maximum_width']='1'
            if change=='error':case['oracle_coordinate_error_upper']='0'
            if change=='current':case['uniquely_enclosed_current'][0]+=1
            if change=='selector':case['corrector_domain']['selector_gap_lower']='0'
            if change=='sign':case['positive']=False
            with self.subTest(change=change),self.assertRaises(ValueError):p.check(m,p.prior.seal(altered))


if __name__=='__main__':unittest.main()
