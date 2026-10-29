"""Composite whole-ball rejection and independent dense/vertex equation parity."""
from copy import deepcopy
import math
import unittest
from unittest.mock import patch
import p984g_ccipc as g
import p984b_ccipc_runtime as r
from p9_ccipc_compute import worker


class CompositeOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with worker():
            before=r.b.GeometryStageInputs.from_payload(r.b.read(r.INPUTS)['initial_inputs'])
            ref=before.geometry.reference
            cls.subject=dict(graph=ref.graph.port_graph.to_envelope(),profile=ref.profile.to_payload(),
                roles={role:r.b.authority_payload(getattr(before,role)) for role in r.ROLES})

    def test_composite_scope_and_strict_chart_boundaries(self):
        g.whole_chart(self.subject)
        for kind in ('family','gain','domain','resource','rho'):
            value=deepcopy(self.subject);p=value['profile']['params_resolved']
            if kind=='family':value['profile']['identity_payload']['profile_family_id']='C_PC'
            elif kind=='gain':value['profile']['identity_payload']['composition_gain']=1
            elif kind=='rho':p['realization']['rho_inst']=2
            elif kind=='domain':
                below=math.nextafter(2*p['geometry']['kappa_H']*p['realization']['radius'],0)
                p['realization']['contraction_domain_id']='ci_reference_frobenius_ball_v1:'+below.hex()
            else:p['realization']['source_envelope_id']='pc_compact_base_chart_v1:'+float(2**20).hex()+':'+float(1).hex()+':'+float(1).hex()
            with self.subTest(kind=kind),self.assertRaises(ValueError):g.whole_chart(value)

    def test_vertex_reduction_matches_direct_edge_equations(self):
        with g.ctx.workprec(g.BITS):
            bv,params,_=g.whole_chart(self.subject);p=params['candidate']
            b=g.iv.matrix(bv);bt=b.transpose();m=b.ncols();identity=g.iv.eye(m)
            old=g.pc.carrier(self.subject,'current',m)
            h=identity+g.a(params['geometry']['kappa_H'])*g.iv.matrix(old)
            cs=list(map(g.q,self.subject['roles']['current']['C']));c=g.iv.matrix([[x] for x in cs])
            t=(g.a(p['kappa_M_C'])*(g.a(sum(cs,g.q(0))/len(cs))/g.a(p['C_ref'])).tanh()).exp()
            actual=g.iv.real_read(b,c,h,p,t)[:3]
            baseline=-g.a(p['eta_C'])*g.a(p['kappa_Phi_C'])*bt*b*(t*h)*bt*c
            response=(identity+g.a(p['tau_C'])*t*h*bt*b).inv()
            j=(identity-g.a(p['zeta_C'])*g.a(p['chi_C'])*response).solve(baseline)
            readback=g.a(p['chi_C'])*response*j
            for left,right in zip(actual,(j,readback,h.solve(readback)),strict=True):
                for i in range(m):
                    self.assertTrue(left[i,0].overlaps(right[i,0]))
                    self.assertLess(g.iv.magnitude(left[i,0]-right[i,0]),g.q('1/1000000000000000000000000000000000000000000'))

    def test_root_enclosure_overlaps_existing_independent_oracle(self):
        with patch.object(r,'CandidateCIRoot',side_effect=AssertionError('native root forbidden')), \
                g.ctx.workprec(g.BITS):
            result=g.root(self.subject,'current')
            source=self.subject;role=source['roles']['current'];graph=source['graph']
            old=r.oracle.independent_root(graph,role['C'],role['Z_4'])
            certified=r.oracle.certify(graph,role['C'],role['Z_4'],old)
            for i,value in enumerate(result['J']):
                previous=certified['read']['J'][i]
                self.assertGreaterEqual(g.hi(value),g.q(str(r.oracle.endpoint(previous,0))))
                self.assertLessEqual(g.lo(value),g.q(str(r.oracle.endpoint(previous,1))))
        self.assertLess(result['geometry_error'],g.q('1/1000000000000000000000000000000'))

    def test_old_carrier_and_resource_domain_reject(self):
        for kind in ('negative','asymmetry','radius'):
            value=deepcopy(self.subject);role=value['roles']['current']
            if kind=='negative':role['C'][0]=-1
            elif kind=='asymmetry':role['Z_4'][1]+=0.25
            else:role['Z_4'][0]=2
            with self.subTest(kind=kind),self.assertRaises(ValueError),g.ctx.workprec(g.BITS):g.root(value,'current')


if __name__=='__main__':unittest.main()
