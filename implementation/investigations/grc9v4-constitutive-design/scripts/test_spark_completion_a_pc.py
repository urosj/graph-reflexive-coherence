"""Independent A_PC equations, every physical derivative axis and history controls."""
from pathlib import Path
import sys,json,unittest
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from mpmath.ctx_mp import MPContext
from spark_completion_a_pc import APCReference,global_domain,trap_certificate
from spark_completion_a_pc_campaign import prepare_source
from spark_completion_a_os import graph_constants
from spark_completion_positive import fixture,norm_upper


def independent_step(m,C,L,Z):
    """110-digit scalar/matrix equations; no APC read, writer or derivative."""
    mp=MPContext();mp.dps=110
    def number(x):
        q=x.mid().fmpq();return mp.mpf(int(q.numerator))/int(q.denominator)
    c=mp.matrix([number(x) for x in C.entries()]);l=[number(x) for x in L.entries()];w=[mp.exp(x) for x in l]
    z=mp.matrix([[number(Z[i,j]) for j in range(m.m)] for i in range(m.m)])
    B=mp.matrix([[int(x) for x in row] for row in graph_constants(json.dumps(m.graph,sort_keys=True))[0].tolist()]);I=mp.eye(m.m);H=I+z/2
    def drive(c,j):
        rows=[[sum(w[k]*(c[v]-c[i]) for k,v in row)/sum(w[k] for k,v in row) if row else mp.mpf(0)
               for row in terms] for i,terms in enumerate(m.terms)]
        return [max(mp.mpf('.5'),mp.exp(-(c[i]+c[v]+sum((rows[i][r]-rows[v][r])**2 for r in range(3))+j[k]**2)/65536)) for k,(i,v) in enumerate(m.pairs)]
    phi=B*mp.diag(w)*B.T*c/64-mp.matrix([(x-2)**3-(x-2) for x in c])+B*(H-I)*B.T*c/64
    j0=-mp.diag(w)*B.T*phi/1024;g=drive(c,j0);q=[(x-y)/(x+y) for x,y in zip(w,g)]
    j=mp.matrix([x/(1-y/4) for x,y in zip(j0,q)]);f=mp.lu_solve(H,mp.matrix([x*y/2 for x,y in zip(q,j)]))
    source=mp.matrix([[m.overlap[i][k]*f[i]*f[k]/4 for k in range(m.m)] for i in range(m.m)])
    ca=c-32*B*j;g=drive(ca,j);decay=mp.exp(-1)
    la=[decay*x+(1-decay)*mp.log(y) for x,y in zip(l,g)];za=decay*z+(1-decay)*source
    return mp,list(ca)+la+[(1 if i==k else mp.sqrt(2))*za[i,k] for i,k in m.carrier_pairs]


def point(m):
    C=arb_mat([[m.q(33+i,32)] for i in range(m.n)]);L=arb_mat([[m.q((-1)**i*(i+1),4096)] for i in range(m.m)]);Z=m.zero()
    for k,(i,j) in enumerate(m.carrier_pairs):Z[i,j]=m.q((-1)**k*(k+1),2**24);Z[j,i]=Z[i,j]
    return C,L,Z


def packed(m,s):return arb_mat(s['after'].tolist()+s['logW_after'].tolist()+m.coordinates(s['carrier_after']).tolist())


class APCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,_,cls.targets=fixture()

    def test_independent_equations_on_both_graphs(self):
        with ctx.workprec(512):
            for graph in (self.source,self.targets['1']['graph']):
                m=APCReference(graph);C,L,Z=point(m);s=packed(m,m.step(C,L,Z));mp,expected=independent_step(m,C,L,Z)
                for x,y in zip(s.entries(),expected):
                    q=x.mid().fmpq();observed=mp.mpf(int(q.numerator))/int(q.denominator)
                    self.assertLess(abs(observed-y),mp.mpf('1e-95'))

    def test_all_76_charge_conductance_and_carrier_directions(self):
        with ctx.workprec(512):
            m=APCReference(self.targets['1']['graph']);C,L,Z=point(m);h=m.q(1,2**150)
            cb=arb_mat([[arb(x.mid(),2*h)] for x in C.entries()]);lb=arb_mat([[arb(x.mid(),2*h)] for x in L.entries()]);zb=m.zero()
            for i,j in m.carrier_pairs:zb[i,j]=arb(Z[i,j].mid(),2*h);zb[j,i]=zb[i,j]
            J=m.jacobian(cb,lb,zb);base=packed(m,m.step(C,L,Z));nx=m.n-1+m.m
            self.assertEqual(nx+m.carrier_dimension,76)
            for k in range(nx+m.carrier_dimension):
                dc=arb_mat([[int(i==k)-int(i==m.n-1) if k<m.n-1 else 0] for i in range(m.n)])
                dl=arb_mat([[int(i==k-(m.n-1))] for i in range(m.m)]);dz=m.zero()
                if k>=nx:
                    i,j=m.carrier_pairs[k-nx];dz[i,j]=1 if i==j else 1/arb(2).sqrt();dz[j,i]=dz[i,j]
                v=arb_mat(dc.tolist()+dl.tolist()+m.coordinates(dz).tolist())
                quotient=(packed(m,m.step(C+h*dc,L+h*dl,Z+h*dz))-base)/h;pred=J*v
                self.assertTrue(all(quotient[i,0].contains(0) if pred[i,0]==0 else pred[i,0].contains(quotient[i,0]) for i in range(J.nrows())),k)

    def test_signed_domain_support_and_full_product_trap(self):
        with ctx.workprec(512):
            for graph in (self.source,self.targets['1']['graph']):
                m=APCReference(graph);d=m.domain;C,L,Z=point(m)
                self.assertLess(fmpq(d['source_norm_upper']),fmpq(d['carrier_radius']));self.assertGreater(fmpq(d['writer_drive_lower']),fmpq(99,100))
                for bad in (-1,5):
                    broken=arb_mat(C);broken[0,0]=bad
                    with self.assertRaisesRegex(ValueError,'declared domain'):m.pc_read(broken,L,Z)
                broken=arb_mat(Z);broken[0,0]=1
                with self.assertRaisesRegex(ValueError,'norm domain'):m.pc_read(C,L,broken)
                i,j=next((i,j) for i,j in m.carrier_pairs if i!=j);broken=arb_mat(Z);broken[i,j]+=m.q(1,1024)
                with self.assertRaisesRegex(ValueError,'symmetric'):m.pc_read(C,L,broken)
                i,j=next((i,j) for i in range(m.m) for j in range(m.m) if not m.overlap[i][j]);broken=arb_mat(Z);broken[i,j]=broken[j,i]=m.q(1,1024)
                with self.assertRaisesRegex(ValueError,'star support'):m.pc_read(C,L,broken)
            p,U=trap_certificate(self.targets)
            self.assertEqual((p['relative_dimension'],p['conductance_dimension'],p['carrier_dimension']),(76,16,46))
            self.assertLess(fmpq(p['contraction'][1]),1);self.assertGreater(fmpq(p['strict_image_margin'][0]),0)
            self.assertTrue(p['all_carrier_directions_included']);self.assertFalse(p['OS_derivative_reused'])

    def test_distinct_history_writers_and_incoming_carrier(self):
        with ctx.workprec(512):
            m=APCReference(self.targets['1']['graph']);C,L,Z=point(m);s=m.step(C,L,Z);r=s['read'];J=r['selected']['current'];W=m.exp(L)
            distinct=lambda a,b:any(abs(x-y).lower()>0 for x,y in zip(a.entries(),b.entries()))
            ex,_=m.exponent(C,W,J);self.assertTrue(distinct(s['logW_after'],m.decay*L+(1-m.decay)*ex))
            ex,_=m.exponent(s['after'],m.exp(s['logW_after']),J);self.assertTrue(distinct(s['logW_after'],m.decay*L+(1-m.decay)*ex))
            fresh=m.pc_read(s['after'],L,Z);wrong=m.decay*Z+(1-m.decay)*fresh['source'];self.assertTrue(distinct(wrong,s['carrier_after']))
            without=m.step(C,L,m.zero());self.assertTrue(distinct(without['after'],s['after']));self.assertTrue(distinct(without['logW_after'],s['logW_after']))
            changed=m.step(C,arb_mat(m.m,1),Z);self.assertTrue(distinct(changed['carrier_after'],s['carrier_after']))
            for args in ((arb_mat(C),L,Z),(C,arb_mat(L),Z),(C,L,arb_mat(Z))):
                with self.assertRaisesRegex(ValueError,'subject'):m.advance(*args,r)

    def test_actual_source_two_channel_transfer_and_cache(self):
        with ctx.workprec(512):
            for role in ('current','reset'):
                m,C,L,Z,s=prepare_source(self.source,self.targets,role)
                self.assertFalse(s['reset_advanced']);self.assertFalse(s['W_transfer']['old_history_discarded'])
                self.assertEqual(s['carrier_history']['information_loss'],'carrier_history_loss')
                self.assertTrue(all(x==0 for x in Z.entries()))
                for edge in s['W_transfer']['new_edge_ids']:self.assertEqual(L[m.edge_ids.index(edge),0],0)
                self.assertTrue(any(x!=['0','0'] for x in s['reset_state']['Z']))
                self.assertNotEqual(s['consumed_current_read'],s['fresh_event_read'])
            before=global_domain.cache_info();APCReference(self.source);after=global_domain.cache_info()
            self.assertEqual(before.misses,after.misses);self.assertGreater(after.hits,before.hits)


if __name__=='__main__':unittest.main()
