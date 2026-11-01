"""Bounded A_CI_PC: selected joint root and full C/logW/symmetric-star Z map.

The same root source enters immediate geometry and the separate carrier writer.
Only proposals use midpoints; physical evolution encloses full input intervals.
"""
from functools import lru_cache
from fractions import Fraction as F
from math import isqrt
import json
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_a_pc import APCReference,PARAMETERS,CARRIER_RADIUS,TRAP_CARRIER_RADIUS
from spark_completion_a_os import graph_constants
from spark_completion_continuation import need,infnorm
from spark_completion_positive import norm_upper
from spark_completion_ci_campaign import exact_bounds

ROOT_RADIUS=F(1,32)
ROOT_NEWTON_LIMIT=12
FIRST_PROPOSAL_PRECISION=128

@lru_cache(maxsize=8)
def global_domain(key):
    """Uniform rational Banach bounds with signed incoming carrier held fixed."""
    B,_,_,_,overlap=graph_constants(key);m=B.ncols()
    ell=F(str(infnorm(B.transpose()*B)));s=F(max(map(sum,overlap)),8)
    R=CARRIER_RADIUS;r=ROOT_RADIUS
    z=F(isqrt(m-1)+1)*R/2;h=z+s*r*r;need(h<1,'root H inverse domain');u=1/(1-h)
    wl,wh=F(99,100),F(101,100)
    j=wh*(12+4*ell*wh/64+4*ell*h/64)/1024
    g=1-(8+192+j*j)/65536;need(g>F(1,2),'uniform floor-inactive branch')
    a=max(wh-g,1-wl)/(wl+g);den=1-a/4;J=j/den;image=u*a*J/2
    jH=4*wh*ell/65536;qj=4*wh*j/(65536*(wl+g)**2)
    Jj=1/den+j*qj/(4*den**2);FH=u*((a*Jj+J*qj)*jH/2+image);rate=2*s*r*FH
    source=F(m,2)*image**2;writer_lower=1-(200+J*J)/65536
    need(image<r and rate<1 and source<R and writer_lower>wl,'uniform composite root/writer envelopes')
    return dict(schema='spark-completion-acipc-domain-v1',C=['0','4'],W=['99/100','101/100'],
        carrier_radius=str(R),carrier_norm='symmetric_star_frobenius',signed_carriers=True,
        causal_flat_radius=str(r),overlap_row_sum=str(s),edge_laplacian_norm=str(ell),
        incoming_H_deviation_infinity=str(z),H_deviation=str(h),H_inverse=str(u),
        H_eigenvalue_lower=str(1-R/2),H_eigenvalue_upper=str(1+R/2+F(m,4)*r*r),
        baseline_current=str(j),drive_lower=str(g),q_absolute=str(a),closure_denominator_lower=str(den),
        selected_current=str(J),image_bound=str(image),baseline_H_lipschitz=str(jH),
        q_baseline_lipschitz=str(qj),current_baseline_lipschitz=str(Jj),flat_H_lipschitz=str(FH),contraction=str(rate),
        source_norm_upper=str(source),writer_drive_lower=str(writer_lower),invariant_carrier_ball=True,
        W_invariance_conditional_on_next_C_box=True,resource_box_invariance_claimed=False,
        uniqueness='one root in the declared flat ball; no global root uniqueness claim')

class ACIPCReference(APCReference):
    def __init__(self,graph):
        super().__init__(graph)
        self.domain=global_domain(json.dumps(graph,sort_keys=True))
        self.root_q=arb(fmpq(self.domain['contraction']));self.root_radius=arb(fmpq(str(ROOT_RADIUS)))
        self.root_calls=0;self.proposal_iterations=0

    def composite_geometry(self,Z,f):return self.I+(Z+self.source(f))/2

    def flat_partials(self,C,W,Z,f,rows=None):
        """F_f and J_f at fixed C,W,Z, with both H consumers differentiated."""
        H=self.composite_geometry(Z,f);selected=self.read(C,W,H,rows)
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

    def root(self,C,L,Z):
        self.validate(C,L,Z);W=self.exp(L)
        self.root_calls+=1
        cp=arb_mat([[x.mid()] for x in C.entries()]);lp=arb_mat([[x.mid()] for x in L.entries()])
        zp=arb_mat([[Z[i,j].mid() for j in range(self.m)] for i in range(self.m)])
        f=arb_mat(self.m,1);precision=ctx.prec;stages=[];p=min(FIRST_PROPOSAL_PRECISION,precision)
        while p<precision:stages.append(p);p=min(2*p,precision)
        stages.append(precision);iterations=0
        for p in stages:
            with ctx.workprec(p):
                wp=self.exp(lp);rows=self.rows(cp,wp);threshold=arb(2)**(-p+32)
                for iteration in range(ROOT_NEWTON_LIMIT):
                    selected,_,ff,_=self.flat_partials(cp,wp,zp,f,rows);residual=selected['causal_flat']-f
                    if infnorm(residual)<threshold:break
                    delta=(self.I-ff).solve(residual)
                    f=arb_mat([[(f[i,0]+delta[i,0]).mid()] for i in range(self.m)])
                    need(infnorm(f)<self.root_radius,'root proposal outside selected domain')
                else:raise ValueError('explicit A_CI_PC root proposal iteration limit')
                iterations+=iteration+1
        self.proposal_iterations+=iterations
        rows=self.rows(C,W);selected=self.read(C,W,self.composite_geometry(Z,f),rows)
        residual=infnorm(selected['causal_flat']-f);error=(residual/(1-self.root_q)).upper()
        need(infnorm(f)+error<self.root_radius,'selected root enclosure leaves domain')
        enclosed=arb_mat([[arb(f[i,0].fmpq(),error.fmpq())] for i in range(self.m)])
        source=self.source(enclosed);H=self.I+(Z+source)/2;selected=self.read(C,W,H,rows)
        need(norm_upper(source)<=self.q(1,64),'selected source domain')
        self.selected_read_count+=1
        return dict(flat=enclosed,source=source,geometry=H,selected=selected,error=error,residual=residual,
            proposal=f,iterations=iterations,proposal_precision_stages=stages,_C=C,_L=L,_Z=Z,_W=W)

    pc_read=root

    def jacobian(self,C,L,Z):
        """All C/W/Z columns; orthonormal symmetric carrier coordinates.

        Every carrier off-diagonal basis has entries 1/sqrt(2). H inverse and
        implicit root derivatives each share one multiple-right-hand-side solve.
        """
        read=self.pc_read(C,L,Z);W=read['_W'];H=read['geometry'];sel=read['selected']
        nx=self.n+self.m;d=nx+self.carrier_dimension;zero=self.zero()
        dC=arb_mat([[int(i==j) for j in range(d)] for i in range(self.n)])
        dL=arb_mat([[int(self.n+i==j) for j in range(d)] for i in range(self.m)])
        dW=self.diag(W)*dL;dHs=[zero]*nx
        for i,j in self.carrier_pairs:
            basis=self.zero();basis[i,j]=self.q(1,2) if i==j else 1/(2*arb(2).sqrt());basis[j,i]=basis[i,j];dHs.append(basis)
        rows=self.rows(C,W,dC,dW)
        sel,H,Ff,Jf=self.flat_partials(C,W,Z,read['flat'],rows)
        need(infnorm(Ff)<self.root_q,'implicit derivative outside uniform root bound')
        dJ,dq=self.read_derivative(C,W,H,sel,dC,dW,dHs,rows)
        selected_flat=sel['causal_flat'];hf=arb_mat([[sum(dHs[k][i,j]*selected_flat[j,0] for j in range(self.m)) for k in range(d)] for i in range(self.m)])
        Fx=H.solve((self.diag(sel['q'])*dJ+self.diag(sel['current'])*dq)/2-hf)
        df=(self.I-Ff).solve(Fx);dJ=dJ+Jf*df;f=read['flat']
        dsource=arb_mat([[(1 if i==j else arb(2).sqrt())*self.q(self.overlap[i][j],4)*
            (df[i,k]*f[j,0]+f[i,0]*df[j,k]) for k in range(d)] for i,j in self.carrier_pairs])
        ca=C-32*self.B*sel['current'];dca=dC-32*self.B*dJ
        _,de=self.exponent(ca,W,sel['current'],None,dca,dW,dJ)
        dla=self.decay*dL+(1-self.decay)*de
        dz=arb_mat([[int(nx+i==j) for j in range(d)] for i in range(self.carrier_dimension)])
        return arb_mat(dca.tolist()+dla.tolist()+(self.decay*dz+(1-self.decay)*dsource).tolist())


def trap_certificate(targets):
    """Fresh full-map product proof using only the earlier rational C/W shape."""
    import spark_completion_a_os_earlier as old
    with ctx.workprec(512):
        runs=old.originals();proposal=old.read_json(old.EARLIER+'AOSAnisotropicDomain.json');old.need_seal(proposal)
        p=runs['current']['proof'];m=ACIPCReference(targets['1']['graph']);n=m.n;nx=n+m.m;d=nx-1;k=m.carrier_dimension
        E,R=old.charge_maps(m);T=fmpq_mat([[fmpq(x) for x in row] for row in proposal['basis']]);r=list(map(fmpq,proposal['axis_radii']))
        need(len(r)==d and all(x>0 for x in r),'positive full C/W radii')
        diag=lambda xs:fmpq_mat([[xs[i] if i==j else 0 for j in range(d)] for i in range(d)])
        S=E*T*diag(r);U=diag([1/x for x in r])*T.inv()*R
        need(U*S==fmpq_mat([[int(i==j) for j in range(d)] for i in range(d)]),'exact full C/W domain inverse')
        need(sum(fmpq(x) for x in p['center'].values())==21,'charge-21 center')
        C=m.vector(p['center']);L=arb_mat([[arb(fmpq(x))] for x in p['logW_center']]);rho=arb(fmpq(str(TRAP_CARRIER_RADIUS)))
        widths=[sum(abs(S[i,j]) for j in range(d)) for i in range(nx)]
        cb=arb_mat([[arb(fmpq(p['center'][x]),widths[i])] for i,x in enumerate(m.nodes)])
        lb=arb_mat([[arb(fmpq(x),widths[n+i])] for i,x in enumerate(p['logW_center'])]);zb=m.zero()
        for i,j in m.carrier_pairs:
            radius=rho if i==j else (rho/arb(2).sqrt()).upper()
            zb[i,j]=arb(0,radius);zb[j,i]=zb[i,j]
        J=m.jacobian(cb,lb,zb)
        block=lambda a,b,c,e:arb_mat([[J[i,j] for j in range(c,e)] for i in range(a,b)])
        XX=arb_mat(U)*block(0,nx,0,nx)*arb_mat(S)
        XZ=arb_mat(U)*block(0,nx,nx,nx+k)
        ZX=block(nx,nx+k,0,nx)*arb_mat(S)
        ZZ=block(nx,nx+k,nx,nx+k)-m.decay*arb_mat([[int(i==j) for j in range(k)] for i in range(k)])
        xx=max(sum(abs(XX[i,j]).upper() for j in range(d)) for i in range(d))
        xz=max(sum(XZ[i,j]**2 for j in range(k)).upper().sqrt().upper() for i in range(d))*rho
        zx=norm_upper(ZX)*arb(d).sqrt()/rho;zz=m.decay+norm_upper(ZZ)
        q=max((xx+xz).upper(),(zx+zz).upper())
        step=m.step(C,L,m.zero());defx=max(abs(x).upper() for x in (arb_mat(U)*old.stack(step['after']-C,step['logW_after']-L)).entries())
        defz=norm_upper(step['carrier_after'])/rho;defect=max(defx,defz.upper());margin=1-q-defect
        need(q<1 and margin>0,f'full C/W/Z product trap unavailable: xx={xx}, xz={xz}, zx={zx}, zz={zz}')
        geometry={}
        for chi,t in targets.items():
            other=ACIPCReference(t['graph']);need(other.nodes==m.nodes and other.pairs==m.pairs and other.terms==m.terms and other.carrier_pairs==m.carrier_pairs,'chiral equation identity')
            geometry[chi]=old.uniform_geometry(other,cb,lb,p['center'],lambda i,j:arb(sum(abs(S[i,jj]-S[j,jj]) for jj in range(d))))
            lower=F(geometry[chi]['weighted_selector_lower'])*(1-TRAP_CARRIER_RADIUS/2)
            need(lower>F(1,64),'carrier-adjusted selector separation');geometry[chi]['carrier_adjusted_selector_lower']=str(lower)
            need(geometry[chi]['complete_basins']==p['complete_basins'][chi],'complete A_CI_PC basin roster')
        return dict(schema='spark-completion-acipc-full-return-v1',center=p['center'],logW_center=p['logW_center'],carrier_center='zero',
            domain_record_digest=proposal['record_digest'],metric='max(||U(deltaC,delta logW)||_infinity,||Z||_F/rho)',radius='1',
            carrier_radius=str(TRAP_CARRIER_RADIUS),relative_dimension=d+k,resource_dimension=n-1,conductance_dimension=m.m,
            carrier_dimension=k,independent_carrier_pairs=m.carrier_pairs,
            derivative_blocks={name:exact_bounds(x) for name,x in dict(XX=xx,XZ=xz,ZX=zx,ZZ=zz).items()},
            contraction=exact_bounds(q),center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            geometry=geometry,complete_basins={chi:g['complete_basins'] for chi,g in geometry.items()},domain=m.domain,
            incoming_carrier_geometry=True,implicit_geometry_derivative=True,
            same_selected_source_for_geometry_and_writer=True,stationary_composite_gain=2,PC_derivative_reused=False,CI_derivative_reused=False,both_independent_writers=True,stationary_writer_self_consistent=True,
            stationary_carrier_argument='BJ=0 and positive diagonal closure imply J=f=S=0; stationary carrier decay gives Z=0, hence H=I and W=G(C,W,0).',
            all_conductance_directions_included=True,all_carrier_directions_included=True,
            OS_derivative_reused=False,earlier_family_trajectory_reused=False,proof_precision_bits=512,native_completion=False,accepted_authority=False),U
