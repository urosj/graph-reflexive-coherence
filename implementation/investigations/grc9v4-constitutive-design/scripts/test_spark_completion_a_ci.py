"""Independent A_CI equations, implicit derivatives and physical-stage controls."""
from pathlib import Path
import sys,json,unittest
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from mpmath.ctx_mp import MPContext
from spark_completion_a_ci import ACIReference,global_root_domain,trap_certificate
from spark_completion_a_ci_campaign import prepare_source
from spark_completion_a_os import AOSReference,graph_constants
from spark_completion_positive import fixture,norm_upper
from spark_completion_continuation import infnorm


def independent_step(m,C,L):
    """110-digit scalar/matrix law and Picard root; no ACI read or derivative."""
    mp=MPContext();mp.dps=110
    def number(x):
        q=x.mid().fmpq();return mp.mpf(int(q.numerator))/int(q.denominator)
    c=mp.matrix([number(x) for x in C.entries()]);l=[number(x) for x in L.entries()];w=[mp.exp(x) for x in l]
    B=mp.matrix([[int(x) for x in row] for row in graph_constants(json.dumps(m.graph,sort_keys=True))[0].tolist()]);I=mp.eye(m.m)
    def drive(c,j):
        rows=[[sum(w[k]*(c[v]-c[i]) for k,v in row)/sum(w[k] for k,v in row) if row else mp.mpf(0)
               for row in terms] for i,terms in enumerate(m.terms)]
        return [max(mp.mpf('.5'),mp.exp(-(c[i]+c[v]+sum((rows[i][r]-rows[v][r])**2 for r in range(3))+j[k]**2)/65536)) for k,(i,v) in enumerate(m.pairs)]
    def read(f):
        H=I+mp.matrix([[m.overlap[i][j]*f[i]*f[j]/8 for j in range(m.m)] for i in range(m.m)])
        phi=B*mp.diag(w)*B.T*c/64-mp.matrix([(x-2)**3-(x-2) for x in c])+B*(H-I)*B.T*c/64
        j0=-mp.diag(w)*B.T*phi/1024;g=drive(c,j0);q=[(x-y)/(x+y) for x,y in zip(w,g)]
        j=mp.matrix([x/(1-y/4) for x,y in zip(j0,q)])
        return j,mp.lu_solve(H,mp.matrix([x*y/2 for x,y in zip(q,j)]))
    f=mp.matrix(m.m,1)
    for _ in range(32):
        j,new=read(f)
        if max(abs(a-b) for a,b in zip(new,f))<mp.mpf('1e-105'):f=new;break
        f=new
    else:raise AssertionError('independent Picard root failed')
    j,_=read(f);ca=c-32*B*j;g=drive(ca,j);decay=mp.exp(-1)
    la=[decay*x+(1-decay)*mp.log(y) for x,y in zip(l,g)]
    return mp,list(ca)+la,list(f)


class ACITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,_,cls.targets=fixture()

    def test_independent_joint_root_and_writer_equations(self):
        with ctx.workprec(512):
            for graph in (self.source,self.targets['1']['graph']):
                m=ACIReference(graph);C=arb_mat([[m.q(33+i,32)] for i in range(m.n)])
                L=arb_mat([[m.q((-1)**i*(i+1),4096)] for i in range(m.m)])
                s=m.step(C,L);mp,expected,flat=independent_step(m,C,L)
                for x,y in zip(s['after'].entries()+s['logW_after'].entries()+s['root']['flat'].entries(),expected+flat):
                    q=x.mid().fmpq();observed=mp.mpf(int(q.numerator))/int(q.denominator)
                    self.assertLess(abs(observed-y),mp.mpf('1e-95'))

    def test_all_implicit_charge_and_history_directions(self):
        with ctx.workprec(512):
            m=ACIReference(self.targets['1']['graph']);h=m.q(1,2**180)
            C=arb_mat([[m.q(7,5)+m.q(i-7,128)] for i in range(m.n)])
            L=arb_mat([[m.q((-1)**i*(i+1),4096)] for i in range(m.m)])
            cb=arb_mat([[arb(x.mid(),2*h)] for x in C.entries()]);lb=arb_mat([[arb(x.mid(),2*h)] for x in L.entries()])
            J=m.jacobian(cb,lb);base=m.step(C,L);base=arb_mat(base['after'].tolist()+base['logW_after'].tolist())
            for k in range(30):
                dc=arb_mat([[int(i==k)-int(i==m.n-1) if k<m.n-1 else 0] for i in range(m.n)])
                dl=arb_mat([[int(i==k-(m.n-1))] for i in range(m.m)]);v=arb_mat(dc.tolist()+dl.tolist())
                s=m.step(C+h*dc,L+h*dl);quotient=(arb_mat(s['after'].tolist()+s['logW_after'].tolist())-base)/h
                self.assertTrue(all((J*v)[i,0].contains(quotient[i,0]) for i in range(m.n+m.m)),k)

    def test_flat_partials_both_geometry_consumers(self):
        with ctx.workprec(512):
            m=ACIReference(self.targets['1']['graph']);C=arb_mat([[m.q(33+i,32)] for i in range(m.n)])
            W=arb_mat([[m.q(4097,4096)] for _ in range(m.m)]);h=m.q(1,2**100)
            f=arb_mat([[m.q((-1)**i,128)] for i in range(m.m)])
            box=arb_mat([[arb(x.mid(),2*h)] for x in f.entries()]);_,_,Ff,Jf=m.flat_partials(C,W,box)
            base=m.read(C,W,m.geometry(f))
            for k in range(m.m):
                v=arb_mat([[int(i==k)] for i in range(m.m)]);new=m.read(C,W,m.geometry(f+h*v))
                for field,D in [('causal_flat',Ff),('current',Jf)]:
                    q=(new[field]-base[field])/h
                    # Structurally zero partials have no interval width; the
                    # separately evaluated zero secant still has roundoff.
                    self.assertTrue(all(q[i,0].contains(0) if D[i,k]==0 else D[i,k].contains(q[i,0])
                                        for i in range(m.m)),(field,k))

    def test_uniform_root_domain_and_fresh_full_state_trap(self):
        with ctx.workprec(512):
            for graph in (self.source,self.targets['1']['graph']):
                m=ACIReference(graph);d=m.domain
                self.assertLess(fmpq(d['image_bound']),fmpq(d['causal_flat_radius']))
                self.assertLess(fmpq(d['contraction']),1);self.assertGreater(fmpq(d['drive_lower']),fmpq(1,2))
                C=arb_mat([[1] for _ in m.nodes]);L=arb_mat(m.m,1);r=m.root(C,L)
                self.assertTrue(all(x==0 for x in r['selected']['current'].entries()));self.assertEqual(r['geometry'],m.I)
                for bad in (-1,5):
                    broken=arb_mat(C);broken[0,0]=bad
                    with self.assertRaisesRegex(ValueError,'root domain'):m.root(broken,L)
                badL=arb_mat(L);badL[0,0]=1
                with self.assertRaisesRegex(ValueError,'root domain'):m.root(C,badL)
            proof,U=trap_certificate(self.targets)
            self.assertEqual((proof['relative_dimension'],proof['conductance_dimension']),(30,16))
            self.assertLess(fmpq(proof['contraction'][1]),1);self.assertGreater(fmpq(proof['strict_image_margin'][0]),0)
            self.assertFalse(proof['OS_derivative_reused']);self.assertFalse(proof['OS_trajectory_reused'])

    def test_stage_lineage_subject_and_cache_controls(self):
        with ctx.workprec(512):
            m,C,L,s=prepare_source(self.source,self.targets,'current');r=m.root(C,L);step=m.step(C,L)
            os=AOSReference(m.graph).step(C,L)
            self.assertTrue(any(abs(a-b).lower()>0 for a,b in zip(os['corrector']['current'].entries(),r['selected']['current'].entries())))
            self.assertTrue(all(x.contains(0) for x in (r['geometry']-m.geometry(r['selected']['causal_flat'])).entries()))
            W=m.exp(L);J=r['selected']['current'];wrong={}
            ex,_=m.exponent(C,W,J);wrong['incoming_C']=m.decay*L+(1-m.decay)*ex
            ex,_=m.exponent(step['after'],m.exp(step['logW_after']),J);wrong['updated_W']=m.decay*L+(1-m.decay)*ex
            wrong['frozen_W']=L
            for name,value in wrong.items():self.assertTrue(any(abs(a-b).lower()>0 for a,b in zip(value.entries(),step['logW_after'].entries())),name)
            with self.assertRaisesRegex(ValueError,'subject'):m.advance(arb_mat(C),L,r)
            for role in ('current','reset'):
                t,c,l,source=prepare_source(self.source,self.targets,role)
                self.assertFalse(source['reset_advanced']);self.assertFalse(source['W_transfer']['old_history_discarded'])
                for edge in source['W_transfer']['new_edge_ids']:self.assertEqual(l[t.edge_ids.index(edge),0],0)
            before=global_root_domain.cache_info();ACIReference(self.source);after=global_root_domain.cache_info()
            self.assertEqual(before.misses,after.misses);self.assertGreater(after.hits,before.hits)


if __name__=='__main__':unittest.main()
