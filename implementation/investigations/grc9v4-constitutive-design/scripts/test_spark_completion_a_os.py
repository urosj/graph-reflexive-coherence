"""Independent equations, all tangent directions, and stage/cache controls."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from mpmath.ctx_mp import MPContext
from spark_completion_a_os import AOSReference,trap_certificate,graph_constants
from spark_completion_a_os_campaign import prepare_source,campaign
from spark_completion_positive import fixture,norm_upper


def independent_step(m,C,L):
    """Separate scalar/matrix mpmath spelling, no AOSReference read or writer."""
    mp=MPContext();mp.dps=110
    def number(x):
        q=x.mid().fmpq();return mp.mpf(int(q.numerator))/int(q.denominator)
    c=mp.matrix([number(x) for x in C.entries()]);l=[number(x) for x in L.entries()]
    w=[mp.exp(x) for x in l];B=mp.matrix([[int(x) for x in row] for row in graph_constants(__import__('json').dumps(m.graph,sort_keys=True))[0].tolist()]);I=mp.eye(m.m)
    def drive(c,j):
        rows=[]
        for i,terms in enumerate(m.terms):
            rows.append([sum(w[k]*(c[v]-c[i]) for k,v in row)/sum(w[k] for k,v in row) if row else mp.mpf(0) for row in terms])
        return [max(mp.mpf('.5'),mp.exp(-(c[i]+c[v]+sum((rows[i][r]-rows[v][r])**2 for r in range(3))+j[k]**2)/65536)) for k,(i,v) in enumerate(m.pairs)]
    def read(h):
        phi=B*mp.diag(w)*B.T*c/64-mp.matrix([(x-2)**3-(x-2) for x in c])+B*(h-I)*B.T*c/64
        j0=-mp.diag(w)*B.T*phi/1024;g=drive(c,j0);q=[(x-y)/(x+y) for x,y in zip(w,g)]
        j=mp.matrix([x/(1-y/4) for x,y in zip(j0,q)])
        f=mp.lu_solve(h,mp.matrix([x*y/2 for x,y in zip(q,j)]));return j,f
    jp,fp=read(I);H=I+mp.matrix([[m.overlap[i][j]*fp[i]*fp[j]/8 for j in range(m.m)] for i in range(m.m)])
    j,f=read(H);ca=c-32*B*j;g=drive(ca,j);a=mp.exp(-1)
    la=[a*x+(1-a)*mp.log(y) for x,y in zip(l,g)]
    return mp,list(ca)+la


class AOSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,_,cls.targets=fixture()

    def test_independent_equations(self):
        with ctx.workprec(512):
            for graph in (self.source,self.targets['1']['graph']):
                m=AOSReference(graph);C=arb_mat([[m.q(33+i,32)] for i in range(m.n)])
                L=arb_mat([[m.q((-1)**i*(i+1),4096)] for i in range(m.m)])
                s=m.step(C,L);mp,expected=independent_step(m,C,L)
                for x,y in zip(s['after'].entries()+s['logW_after'].entries(),expected):
                    q=x.mid().fmpq();observed=mp.mpf(int(q.numerator))/int(q.denominator)
                    self.assertLess(abs(observed-y),mp.mpf('1e-95'))

    def test_full_return_and_every_independent_direction(self):
        proof,P=trap_certificate(self.targets)
        self.assertEqual((proof['relative_dimension'],proof['conductance_dimension']),(30,16))
        with ctx.workprec(512):
            m=AOSReference(self.targets['1']['graph']);C=m.vector(proof['center']);L=arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])
            cb=arb_mat([[arb(x.mid(),arb(fmpq(proof['coordinate_radius'])))] for x in C.entries()]);lb=arb_mat([[arb(x.mid(),arb(fmpq(proof['logW_coordinate_radius'])))] for x in L.entries()])
            J=m.jacobian(cb,lb);s=m.step(C,L);base=arb_mat(s['after'].tolist()+s['logW_after'].tolist());h=m.q(1,2**48)
            for k in range(m.n-1+m.m):
                vc=arb_mat([[int(i==k)-int(i==m.n-1) if k<m.n-1 else 0] for i in range(m.n)])
                vl=arb_mat([[int(i==k-(m.n-1))] for i in range(m.m)])
                v=arb_mat(vc.tolist()+vl.tolist());sn=m.step(C+h*vc,L+h*vl)
                delta=(arb_mat(sn['after'].tolist()+sn['logW_after'].tolist())-base)/h;enclosure=J*v
                self.assertTrue(all(enclosure[i,0].contains(delta[i,0]) for i in range(m.n+m.m)),k)
            self.assertLess(float(fmpq(proof['contraction'][1])),1)
            self.assertGreater(float(fmpq(proof['strict_image_margin'][0])),0)

    def test_writer_and_os_stage_controls(self):
        with ctx.workprec(512):
            m,C,L,_=prepare_source(self.source,self.targets,'current');s=m.step(C,L);W=m.exp(L);j=s['corrector']['current']
            wrong={}
            ex,_=m.exponent(C,W,j);wrong['incoming_C_writer']=m.decay*L+(1-m.decay)*ex
            ex,_=m.exponent(s['after'],m.exp(s['logW_after']),j);wrong['updated_W_writer']=m.decay*L+(1-m.decay)*ex
            ex,_=m.exponent(s['after'],W,s['predictor']['current']);wrong['predictor_current_writer']=m.decay*L+(1-m.decay)*ex
            wrong['frozen_W']=L
            for name,value in wrong.items():self.assertTrue(any(abs(a-b).lower()>0 for a,b in zip(value.entries(),s['logW_after'].entries())),name)
            self.assertTrue(any(abs(a-b).lower()>0 for a,b in zip((C-32*m.B*s['predictor']['current']).entries(),s['after'].entries())))
            with self.assertRaisesRegex(ValueError,'subject'):m.advance(arb_mat(C),L,s)

    def test_source_transfer_and_chiral_cache(self):
        with ctx.workprec(512):
            for role in ('current','reset'):
                m,C,L,s=prepare_source(self.source,self.targets,role)
                self.assertFalse(s['reset_advanced']);self.assertFalse(s['W_transfer']['old_history_discarded'])
                for t in self.targets.values():
                    other=AOSReference(t['graph']);self.assertEqual(m.terms,other.terms);self.assertEqual(m.pairs,other.pairs)
                for e in s['W_transfer']['new_edge_ids']:self.assertEqual(L[m.edge_ids.index(e),0],0)
                self.assertTrue(all(L[m.edge_ids.index(e),0]!=0 for e in s['W_transfer']['retained_edge_ids']))
            before=graph_constants.cache_info();AOSReference(self.source);after=graph_constants.cache_info()
            self.assertEqual(before.misses,after.misses);self.assertGreater(after.hits,before.hits)

    def test_floor_and_invalid_conductance_rejected(self):
        with ctx.workprec(512):
            m=AOSReference(self.source);C=arb_mat([[100000] for _ in range(m.n)]);W=arb_mat([[1] for _ in range(m.m)])
            with self.assertRaisesRegex(ValueError,'floor'):m.exponent(C,W,arb_mat(m.m,1))
            with self.assertRaisesRegex(ValueError,'positive'):m.rows(C,-W)


if __name__=='__main__':unittest.main()
