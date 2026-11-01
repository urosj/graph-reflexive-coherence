"""A_CI selected joint root and full C/logW derivative, investigation only.

The shared A equations are unchanged. Geometry and both of its consumers use
one selected causal-flat root. Midpoints propose that root only; the returned
root and every physical advance enclose the actual input intervals.
"""
from functools import lru_cache
from fractions import Fraction as F
import json
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_a_os import AOSReference,graph_constants,PARAMETERS
from spark_completion_continuation import need,infnorm
from spark_completion_positive import norm_upper
from spark_completion_ci_campaign import exact_bounds

ROOT_RADIUS=F(1,32)
ROOT_NEWTON_LIMIT=12
FIRST_PROPOSAL_PRECISION=128


@lru_cache(maxsize=8)
def global_root_domain(key):
    """Rational uniform Banach bounds on C in [0,4], W in [99/100,101/100]."""
    B,_,_,_,overlap=graph_constants(key)
    ell=F(str(infnorm(B.transpose()*B)));S=F(max(map(sum,overlap)),8)
    r=ROOT_RADIUS;h=S*r*r;need(h<1,'root H inverse domain');u=1/(1-h)
    wl,wh=F(99,100),F(101,100)
    j0=wh*(12+ell*wh*4/64+ell*h*4/64)/1024
    exponent=(8+192+j0*j0)/65536;gl=1-exponent
    need(gl>F(1,2),'root floor-inactive branch')
    q=max(wh-gl,1-wl)/(wl+gl);den=1-q/4;J=j0/den;image=u*q*J/2
    jH=wh*ell*4/65536
    qj=4*wh*j0/(65536*(wl+gl)**2)
    Jj=1/den+j0*qj/(4*den*den)
    FH=u*((q*Jj+J*qj)*jH/2+image)
    rate=FH*2*S*r
    need(image<r and rate<1,'uniform joint-root contraction')
    return dict(schema='spark-completion-aci-root-domain-v1',C=['0','4'],W=['99/100','101/100'],
        causal_flat_radius=str(r),overlap_row_sum=str(S),edge_laplacian_norm=str(ell),
        H_deviation=str(h),H_inverse=str(u),baseline_current=str(j0),drive_lower=str(gl),
        q_absolute=str(q),closure_denominator_lower=str(den),selected_current=str(J),
        image_bound=str(image),baseline_H_lipschitz=str(jH),q_baseline_lipschitz=str(qj),
        current_baseline_lipschitz=str(Jj),flat_H_lipschitz=str(FH),contraction=str(rate),
        uniqueness='one root in the declared flat ball; no global root uniqueness claim')


class ACIReference(AOSReference):
    def __init__(self,graph):
        super().__init__(graph)
        self.domain=global_root_domain(json.dumps(graph,sort_keys=True))
        self.root_q=arb(fmpq(self.domain['contraction']));self.root_radius=arb(fmpq(str(ROOT_RADIUS)))
        self.root_calls=0;self.proposal_iterations=0

    def flat_partials(self,C,W,f,rows=None):
        """F_f and J_f at fixed C,W, with both H consumers differentiated."""
        H=self.geometry(f);selected=self.read(C,W,H,rows)
        dc=self.Bt*C
        dHs=[arb_mat([[self.overlap[i][j]*((f[j,0] if i==k else 0)+(f[i,0] if j==k else 0))/8
                       for j in range(self.m)] for i in range(self.m)]) for k in range(self.m)]
        pack=lambda cols:arb_mat([[cols[j][i,0] for j in range(self.m)] for i in range(self.m)])
        dj0=-self.diag(W)*self.Bt*self.B*pack([dH*dc for dH in dHs])/65536
        j0=selected['baseline'];G=selected['drive'];q=selected['q'];J=selected['current']
        dq=arb_mat([[4*W[i,0]*G[i,0]*j0[i,0]*dj0[i,j]/(65536*(W[i,0]+G[i,0])**2)
                     for j in range(self.m)] for i in range(self.m)])
        den=[1-q[i,0]/4 for i in range(self.m)]
        dJ=arb_mat([[dj0[i,j]/den[i]+j0[i,0]*dq[i,j]/(4*den[i]**2)
                    for j in range(self.m)] for i in range(self.m)])
        df=H.solve((self.diag(q)*dJ+self.diag(J)*dq)/2-pack([dH*selected['causal_flat'] for dH in dHs]))
        return selected,H,df,dJ

    def root(self,C,L):
        need(all(0<=x<=4 for x in C.entries()),'C outside root domain')
        W=self.exp(L);need(all(self.q(99,100)<=x<=self.q(101,100) for x in W.entries()),'W outside root domain')
        self.root_calls+=1
        cp=arb_mat([[x.mid()] for x in C.entries()]);lp=arb_mat([[x.mid()] for x in L.entries()])
        f=arb_mat(self.m,1);precision=ctx.prec;stages=[];p=min(FIRST_PROPOSAL_PRECISION,precision)
        while p<precision:stages.append(p);p=min(2*p,precision)
        stages.append(precision);iterations=0
        for p in stages:
            with ctx.workprec(p):
                wp=self.exp(lp);rows=self.rows(cp,wp);threshold=arb(2)**(-p+32)
                for iteration in range(ROOT_NEWTON_LIMIT):
                    selected,_,ff,_=self.flat_partials(cp,wp,f,rows);residual=selected['causal_flat']-f
                    if infnorm(residual)<threshold:break
                    delta=(self.I-ff).solve(residual)
                    f=arb_mat([[(f[i,0]+delta[i,0]).mid()] for i in range(self.m)])
                    need(infnorm(f)<self.root_radius,'root proposal outside selected domain')
                else:raise ValueError('explicit A_CI root proposal iteration limit')
                iterations+=iteration+1
        self.proposal_iterations+=iterations
        rows=self.rows(C,W);selected=self.read(C,W,self.geometry(f),rows)
        residual=infnorm(selected['causal_flat']-f);error=(residual/(1-self.root_q)).upper()
        need(infnorm(f)+error<self.root_radius,'selected root enclosure leaves domain')
        enclosed=arb_mat([[arb(f[i,0].fmpq(),error.fmpq())] for i in range(self.m)])
        H=self.geometry(enclosed);selected=self.read(C,W,H,rows)
        return dict(flat=enclosed,geometry=H,selected=selected,error=error,residual=residual,
            proposal=f,iterations=iterations,proposal_precision_stages=stages,_C=C,_L=L,_W=W)

    def advance(self,C,L,root):
        need(C is root['_C'] and L is root['_L'],'joint-root subject changed')
        J=root['selected']['current'];after=C-32*self.B*J
        exponent,_=self.exponent(after,root['_W'],J)
        self.writer_count+=1
        return after,self.decay*L+(1-self.decay)*exponent

    def step(self,C,L):
        root=self.root(C,L);after,lp=self.advance(C,L,root)
        return dict(root=root,after=after,logW_after=lp)

    def jacobian(self,C,L,root=None):
        root=self.root(C,L) if root is None else root
        need(C is root['_C'] and L is root['_L'],'derivative root subject changed')
        W=root['_W'];d=self.n+self.m
        dC=arb_mat([[int(i==j) for j in range(d)] for i in range(self.n)])
        dL=arb_mat([[int(self.n+i==j) for j in range(d)] for i in range(self.m)])
        dW=self.diag(W)*dL;rows=self.rows(C,W,dC,dW)
        selected,H,Ff,Jf=self.flat_partials(C,W,root['flat'],rows)
        need(infnorm(Ff)<self.root_q,'implicit derivative outside uniform root bound')
        zero=arb_mat(self.m,self.m)
        Jx,qx=self.read_derivative(C,W,H,selected,dC,dW,[zero]*d,rows)
        Fx=H.solve((self.diag(selected['q'])*Jx+self.diag(selected['current'])*qx)/2)
        df=(self.I-Ff).solve(Fx);dJ=Jx+Jf*df
        ca=C-32*self.B*selected['current'];dca=dC-32*self.B*dJ
        _,de=self.exponent(ca,W,selected['current'],None,dca,dW,dJ)
        return arb_mat(dca.tolist()+(self.decay*dL+(1-self.decay)*de).tolist())


def trap_certificate(targets):
    """Fresh implicit-map proof on the explicitly borrowed rational domain."""
    import spark_completion_a_os_earlier as old
    with ctx.workprec(512):
        runs=old.originals();proposal=old.read_json(old.EARLIER+'AOSAnisotropicDomain.json');old.need_seal(proposal)
        p=runs['current']['proof'];m=ACIReference(targets['1']['graph']);n=m.n;d=n-1+m.m
        E,R=old.charge_maps(m);T=fmpq_mat([[fmpq(x) for x in row] for row in proposal['basis']]);r=list(map(fmpq,proposal['axis_radii']))
        diag=lambda xs:fmpq_mat([[xs[i] if i==j else 0 for j in range(d)] for i in range(d)])
        S=E*T*diag(r);U=diag([1/x for x in r])*T.inv()*R
        need(U*S==fmpq_mat([[int(i==j) for j in range(d)] for i in range(d)]),'exact charge chart inverse')
        C=m.vector(p['center']);L=arb_mat([[arb(fmpq(x))] for x in p['logW_center']])
        widths=[sum(abs(S[i,j]) for j in range(d)) for i in range(n+m.m)]
        cb=arb_mat([[arb(fmpq(p['center'][x]),widths[i])] for i,x in enumerate(m.nodes)])
        lb=arb_mat([[arb(fmpq(x),widths[n+i])] for i,x in enumerate(p['logW_center'])])
        root=m.root(cb,lb);J=m.jacobian(cb,lb,root);D=arb_mat(U)*J*arb_mat(S)
        q=max(sum(abs(D[i,j]).upper() for j in range(d)) for i in range(d))
        step=m.step(C,L);defect=max(abs(x).upper() for x in (arb_mat(U)*old.stack(step['after']-C,step['logW_after']-L)).entries())
        margin=1-q-defect;need(q<1 and margin>0,'full implicit C/W trap unavailable')
        geometry={}
        for chi,t in targets.items():
            other=ACIReference(t['graph']);need(other.nodes==m.nodes and other.pairs==m.pairs and other.terms==m.terms,'chiral equation identity')
            geometry[chi]=old.uniform_geometry(other,cb,lb,p['center'],lambda i,j:arb(sum(abs(S[i,k]-S[j,k]) for k in range(d))))
            need(geometry[chi]['complete_basins']==p['complete_basins'][chi],'complete A_CI basin roster')
        return dict(schema='spark-completion-aci-full-return-v1',center=p['center'],logW_center=p['logW_center'],
            domain_record_digest=proposal['record_digest'],metric='||diag(r)^-1 T^-1 R (deltaC,delta logW)||_infinity',radius='1',
            relative_dimension=d,resource_dimension=n-1,conductance_dimension=m.m,
            contraction=exact_bounds(q),center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            geometry=geometry,complete_basins={chi:g['complete_basins'] for chi,g in geometry.items()},
            root_domain=m.domain,domain_root_error=exact_bounds(root['error']),
            implicit_geometry_derivative=True,stationary_writer_self_consistent=True,
            all_conductance_directions_included=True,OS_derivative_reused=False,OS_trajectory_reused=False,
            proof_precision_bits=512,native_completion=False,accepted_authority=False),U
