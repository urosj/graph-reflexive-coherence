"""Investigation-only A_OS equations and full C/log(W) interval return proof.

Fixed-row descriptors use incoming W in both reads and in the final-C writer.
All coefficients of the A feedback, geometry and writer are strictly positive.
FLINT/Arb enclosures evolve without midpoint replacement or tolerance widening.
"""
from functools import lru_cache
from fractions import Fraction as F
from math import floor, ceil
import json
from flint import arb, arb_mat, fmpq, fmpq_mat, ctx
from spark_completion_positive import norm_upper, NAMESPACE
from spark_completion_continuation import need, infnorm, POLICY
from spark_completion_ci_campaign import exact_bounds
import spark_completion_basins as basins

PARAMETERS = dict(eta='1/1024',duration='32',kappa_c='1/64',kappa_Ah='1/64',
    chi='1/2',zeta='1/2',kappa_H='1/2',alpha='1/32768',beta='1/32768',
    gamma='1/32768',W_floor='1/2',tau_A='32',site='(C-2)^3-(C-2)')


@lru_cache(maxsize=8)
def graph_constants(key):
    g=json.loads(key); nodes=g['live_node_ids']; n=len(nodes); edges=g['edges']; m=len(edges)
    pairs=[(nodes.index(e['tail']['node_id']),nodes.index(e['head']['node_id'])) for e in edges]
    need(all(i!=j for i,j in pairs),'loop-free declared fixture required')
    B=fmpq_mat([[(k==i)-(k==j) for i,j in pairs] for k in range(n)])
    I=fmpq_mat([[int(i==j) for j in range(m)] for i in range(m)])
    rows=[[[] for _ in range(3)] for _ in nodes]
    for k,e in enumerate(edges):
        for end,other in [('tail','head'),('head','tail')]:
            rows[nodes.index(e[end]['node_id'])][(e[end]['port']-1)//3].append((k,nodes.index(e[other]['node_id'])))
    overlap=[[sum(v in e and v in f for v in range(n)) for f in pairs] for e in pairs]
    return B,I,pairs,rows,overlap


class AOSReference:
    def __init__(self,graph):
        self.graph=graph; self.nodes=graph['live_node_ids'];self.edge_ids=[e['edge_id'] for e in graph['edges']]
        B,I,self.pairs,self.terms,self.overlap=graph_constants(json.dumps(graph,sort_keys=True))
        self.B=arb_mat(B);self.Bt=self.B.transpose();self.I=arb_mat(I)
        self.n,self.m=len(self.nodes),len(self.edge_ids);self.matrix=arb_mat
        self.decay=(-arb(1)).exp();self.floor_log=-arb(2).log();self.read_count=0;self.writer_count=0

    def q(self,n,d=1):return arb(fmpq(n,d))
    def vector(self,values):return arb_mat([[arb(fmpq(values[n]))] for n in self.nodes])
    def diag(self,v):return arb_mat([[v[i,0] if i==j else 0 for j in range(v.nrows())] for i in range(v.nrows())])
    def exp(self,L):return arb_mat([[L[i,0].exp()] for i in range(self.m)])
    def site(self,C):return arb_mat([[(C[i,0]-2)*(C[i,0]-2)*(C[i,0]-2)-(C[i,0]-2)] for i in range(self.n)])

    def rows(self,C,W,dC=None,dW=None):
        values=[];derivatives=[];d=dC.ncols() if dC is not None else 0
        for i,terms in enumerate(self.terms):
            vr=[];dr=[]
            for row in terms:
                den=sum((W[k,0] for k,j in row),arb(0))
                if not row:v=arb(0);dv=[arb(0)]*d
                else:
                    need(den>0,'positive fixed-row denominator')
                    v=sum((W[k,0]*(C[j,0]-C[i,0]) for k,j in row),arb(0))/den
                    dv=[sum((dW[k,l]*(C[j,0]-C[i,0]-v)+W[k,0]*(dC[j,l]-dC[i,l]) for k,j in row),arb(0))/den for l in range(d)]
                vr.append(v);dr.append(dv)
            values.append(vr);derivatives.append(dr)
        return values,derivatives

    def exponent(self,C,W,J,rows=None,dC=None,dW=None,dJ=None):
        rv,rd=self.rows(C,W,dC,dW) if rows is None else rows
        out=[];der=[];d=dC.ncols() if dC is not None else 0
        for k,(i,j) in enumerate(self.pairs):
            v=-(C[i,0]+C[j,0]+sum((rv[i][r]-rv[j][r])*(rv[i][r]-rv[j][r]) for r in range(3))+J[k,0]*J[k,0])/65536
            # This bounded certificate uses the smooth, strictly floor-inactive branch.
            need(v>self.floor_log,'conductance floor not strictly inactive')
            out.append([v])
            der.append([-(dC[i,l]+dC[j,l]+sum(2*(rv[i][r]-rv[j][r])*(rd[i][r][l]-rd[j][r][l]) for r in range(3))+2*J[k,0]*dJ[k,l])/65536 for l in range(d)])
        return arb_mat(out),arb_mat(der) if d else None

    def read(self,C,W,H,rows=None):
        self.read_count+=1
        phi=self.B*self.diag(W)*self.Bt*C/64-self.site(C)+self.B*(H-self.I)*self.Bt*C/64
        j0=-self.diag(W)*self.Bt*phi/1024
        exponent,_=self.exponent(C,W,j0,rows)
        G=self.exp(exponent);q=arb_mat([[(W[k,0]-G[k,0])/(W[k,0]+G[k,0])] for k in range(self.m)])
        den=[1-q[k,0]/4 for k in range(self.m)];need(all(x>self.q(3,4) for x in den),'positive physical closure')
        J=arb_mat([[j0[k,0]/den[k]] for k in range(self.m)])
        causal=arb_mat([[q[k,0]*J[k,0]/2] for k in range(self.m)])
        flat=causal if H is self.I else H.solve(causal)
        return dict(potential=phi,baseline=j0,drive=G,q=q,current=J,causal_flat=flat)

    def geometry(self,f):
        return self.I+arb_mat([[self.overlap[i][j]*f[i,0]*f[j,0]/8 for j in range(self.m)] for i in range(self.m)])

    def os_read(self,C,L):
        W=self.exp(L);need(all(x>0 for x in W.entries()),'positive conductance')
        rows=self.rows(C,W);pred=self.read(C,W,self.I,rows)
        H=self.geometry(pred['causal_flat']);corr=self.read(C,W,H,rows)
        defect=norm_upper(H-self.geometry(corr['causal_flat']))
        need(defect<self.q(1,10**11),'OS split tolerance exceeded')
        return dict(predictor=pred,geometry=H,corrector=corr,split_upper=defect,_C=C,_L=L,_W=W)

    def advance(self,C,L,read):
        need(C is read['_C'] and L is read['_L'],'read subject changed')
        W=read['_W'];J=read['corrector']['current'];after=C-32*self.B*J
        exponent,_=self.exponent(after,W,J)
        self.writer_count+=1
        return after,self.decay*L+(1-self.decay)*exponent

    def step(self,C,L):
        read=self.os_read(C,L);after,ln=self.advance(C,L,read)
        return dict(**read,after=after,logW_after=ln)

    def read_derivative(self,C,W,H,read,dC,dW,dHs,rows):
        d=dC.ncols();dc=self.Bt*C;phi=read['potential'];j0=read['baseline'];G=read['drive'];q=read['q']
        extra=arb_mat([[sum(dHs[l][i,j]*dc[j,0] for j in range(self.m)) for l in range(d)] for i in range(self.m)])
        curvature=self.diag(arb_mat([[3*(C[i,0]-2)**2-1] for i in range(self.n)]))
        dp=self.B*(self.diag(W)*self.Bt*dC+self.diag(dc)*dW+(H-self.I)*self.Bt*dC+extra)/64-curvature*dC
        dj=-((self.diag(W)*self.Bt*dp)+(self.diag(self.Bt*phi)*dW))/1024
        _,de=self.exponent(C,W,j0,rows,dC,dW,dj);dg=self.diag(G)*de
        dq=arb_mat([[2*(G[k,0]*dW[k,l]-W[k,0]*dg[k,l])/(W[k,0]+G[k,0])**2 for l in range(d)] for k in range(self.m)])
        dJ=arb_mat([[dj[k,l]/(1-q[k,0]/4)+j0[k,0]*dq[k,l]/(4*(1-q[k,0]/4)**2) for l in range(d)] for k in range(self.m)])
        return dJ,dq

    def jacobian(self,C,L):
        d=self.n+self.m;W=self.exp(L)
        dC=arb_mat([[int(i==j) for j in range(d)] for i in range(self.n)])
        dL=arb_mat([[int(self.n+i==j) for j in range(d)] for i in range(self.m)])
        dW=self.diag(W)*dL;rows=self.rows(C,W,dC,dW)
        s=self.os_read(C,L);p=s['predictor'];c=s['corrector'];zero=arb_mat(self.m,self.m)
        dj,dq=self.read_derivative(C,W,self.I,p,dC,dW,[zero]*d,rows)
        df=(self.diag(p['q'])*dj+self.diag(p['current'])*dq)/2
        f=p['causal_flat']
        dHs=[arb_mat([[self.overlap[i][j]*(df[i,l]*f[j,0]+f[i,0]*df[j,l])/8 for j in range(self.m)] for i in range(self.m)]) for l in range(d)]
        dj,_=self.read_derivative(C,W,s['geometry'],c,dC,dW,dHs,rows)
        ca=C-32*self.B*c['current'];dca=dC-32*self.B*dj
        _,de=self.exponent(ca,W,c['current'],None,dca,dW,dj)
        dl=self.decay*dL+(1-self.decay)*de
        return arb_mat(dca.tolist()+dl.tolist())


def geometric_roster(m,C,L):
    """Complete fixed-row predicates with committed W, over arbitrary boxes."""
    W=m.exp(L);rv,_=m.rows(C,W)
    rows={n:[tuple(map(F,exact_bounds(x))) for x in rv[i]] for i,n in enumerate(m.nodes)}
    low={n:F(str(C[i,0].lower().fmpq())) for i,n in enumerate(m.nodes)}
    high={n:F(str(C[i,0].upper().fmpq())) for i,n in enumerate(m.nodes)}
    adj={n:set() for n in m.nodes}
    for i,j in m.pairs:adj[m.nodes[i]].add(m.nodes[j]);adj[m.nodes[j]].add(m.nodes[i])
    seeds={n for n in m.nodes if basins.seed_status(rows[n],POLICY)};anchors=set()
    for n in seeds:
        if low[n]>POLICY['core_resource'] and all(low[n]-high[v]>POLICY['contrast'] for v in adj[n]):anchors.add(n)
        else:need(high[n]<=POLICY['core_resource'] or any(high[n]-low[v]<=POLICY['contrast'] for v in adj[n]),'unresolved anchor')
    down={n:set() for n in m.nodes}
    for n in m.nodes:
        for v in adj[n]:
            if low[v]>high[n]:down[n].add(v)
            else:need(low[n]>high[v],'unresolved edge order')
    destinations={}
    def visit(n):
        if n not in destinations:destinations[n]=set().union(*(visit(v) for v in down[n])) if down[n] else {n}
        return destinations[n]
    for n in m.nodes:visit(n)
    out={a:sorted(n for n in m.nodes if destinations[n]=={a}) for a in sorted(anchors)}
    return {a:b for a,b in out.items() if len(b)>1}


def propose_center(m):
    n,mx=m.n,m.m;d=n+mx
    C=arb_mat([[arb(3 if x in ('p',NAMESPACE+'/satellite/2') else 1)+arb(fmpq(2,15))] for x in m.nodes])
    L=arb_mat(mx,1);lam=arb(0)
    dc=arb_mat([[int(i==j) for j in range(d)] for i in range(n)])
    dl=arb_mat([[int(n+i==j) for j in range(d)] for i in range(mx)]);J=arb_mat(mx,1);dj=arb_mat(mx,d)
    for _ in range(12):
        W=m.exp(L);dw=m.diag(W)*dl;ex,de=m.exponent(C,W,J,None,dc,dw,dj)
        R=m.site(C)-m.B*m.diag(W)*m.Bt*C/64
        dr=m.diag(arb_mat([[3*(C[i,0]-2)**2-1] for i in range(n)]))*dc-m.B*(m.diag(W)*m.Bt*dc+m.diag(m.Bt*C)*dw)/64
        M=arb_mat([dr.tolist()[i]+[-1] for i in range(n)]+[(dl-de).tolist()[i]+[0] for i in range(mx)]+[[1]*n+[0]*(mx+1)])
        residual=arb_mat([[R[i,0]-lam] for i in range(n)]+[[L[i,0]-ex[i,0]] for i in range(mx)]+[[sum(C.entries())-21]])
        delta=M.solve(residual)
        C=arb_mat([[(C[i,0]-delta[i,0]).mid()] for i in range(n)])
        L=arb_mat([[(L[i,0]-delta[n+i,0]).mid()] for i in range(mx)]);lam=(lam-delta[d,0]).mid()
    dyadic=lambda x:str(F(floor(F(str(x.mid().fmpq()))*2**160),2**160))
    cv=[dyadic(C[i,0]) for i in range(n-1)];cv.append(str(21-sum(map(F,cv))))
    return dict(zip(m.nodes,cv)),[dyadic(L[i,0]) for i in range(mx)]


def trap_certificate(targets):
    with ctx.workprec(512):
        m=AOSReference(targets['1']['graph']);n=m.n
        center,logs=propose_center(m);C=m.vector(center);L=arb_mat([[arb(fmpq(x))] for x in logs])
        B=graph_constants(json.dumps(m.graph,sort_keys=True))[0]
        weights=[fmpq(str(F(floor(F(str(x.mid().fmpq()))*2**160),2**160))) for x in m.exp(L).entries()]
        A=B*fmpq_mat([[weights[i] if i==j else 0 for j in range(m.m)] for i in range(m.m)])*B.transpose()
        pi=fmpq_mat([[fmpq(1,n) for j in range(n)] for i in range(n)]);P=(A+pi).inv()
        trace=sum(P[i,i] for i in range(n))-1;amax=infnorm(A);amin=1/trace
        curvature=[3*(fmpq(center[x])-2)**2-1 for x in m.nodes]
        D=fmpq_mat([[curvature[i] if i==j else 0 for j in range(n)] for i in range(n)])-A/64
        dmin=min(curvature)-infnorm(A)/64;dmax=max(curvature)
        need(dmin>0 and amax*dmax/32<2,'reference spectral interval')
        q0=max(1-amin*dmin/32,amax*dmax/32-1)
        J0=arb_mat(fmpq_mat([[int(i==j) for j in range(n)] for i in range(n)])-A*D/32)
        radius=m.q(1,2**20);weight=arb(64)
        cr=F(ceil(F(str((arb(amax).sqrt()*radius).upper().fmpq()))*2**100),2**100)
        lr=F(1,2**26)
        box=arb_mat([[arb(fmpq(center[x]),fmpq(str(cr)))] for x in m.nodes])
        lb=arb_mat([[arb(fmpq(x),fmpq(str(lr)))] for x in logs])
        J=m.jacobian(box,lb)
        block=lambda a,b,c,d:arb_mat([[J[i,j] for j in range(c,d)] for i in range(a,b)])
        cc=arb(q0)+norm_upper(block(0,n,0,n)-J0)*(arb(amax)*arb(trace)).sqrt()
        cw=norm_upper(block(0,n,n,n+m.m))*arb(trace).sqrt()/weight
        wc=norm_upper(block(n,n+m.m,0,n))*arb(amax).sqrt()*weight
        # Writer has diagonal decay; bound its perturbation in Frobenius norm.
        ww=m.decay+norm_upper(block(n,n+m.m,n,n+m.m)-m.decay*m.I)
        q=max((cc+cw).upper(),(wc+ww).upper())
        need(q<1,f'full C/W contraction unproved: cc={cc}, cw={cw}, wc={wc}, ww={ww}')
        step=m.step(C,L);defect=max((norm_upper(step['after']-C)*arb(trace).sqrt()).upper(),(weight*norm_upper(step['logW_after']-L)).upper())
        margin=(1-q)*radius-defect;need(margin>0,'full C/W invariant ball unproved')
        expected={'p':['p','private'],NAMESPACE+'/satellite/2':['n2','n8',NAMESPACE+'/satellite/2']}
        rosters={chi:geometric_roster(AOSReference(t['graph']),box,lb) for chi,t in targets.items()}
        need(all(v==expected for v in rosters.values()),'full C/W trap basin roster')
        need(all(m.terms==AOSReference(t['graph']).terms and m.pairs==AOSReference(t['graph']).pairs for t in targets.values()),'chiral equations differ')
        return dict(center=center,logW_center=logs,radius='1/1048576',weight=64,
            coordinate_radius=str(cr),logW_coordinate_radius=str(lr),inverse_trace=str(trace),A_max=str(amax),reference_W=list(map(str,weights)),
            metric='max(sqrt(deltaC^T (B diag(W0) B^T+11^T/n)^-1 deltaC),64*||delta logW||_2), sum C=21',
            q_reference=str(q0),block_bounds={k:exact_bounds(v) for k,v in dict(CC=cc,CW=cw,WC=wc,WW=ww).items()},
            contraction=exact_bounds(q),center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            complete_basins=rosters,relative_dimension=n-1+m.m,resource_dimension=n-1,conductance_dimension=m.m,
            stationary_writer_self_consistent=True,all_conductance_directions_included=True,
            stationary_argument='Full-map Banach fixed point; positive diagonal closure and BJ=0 imply J=0, hence H=I and logW=logG(C,W,0).',
            actual_full_map_trapping=True,native_completion=False),P
