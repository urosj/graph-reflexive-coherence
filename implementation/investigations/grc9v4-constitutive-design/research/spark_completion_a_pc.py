"""Investigation-only A_PC: full C/logW/symmetric-star Z return in FLINT/Arb.

Incoming Z selects H=I+Z/2; one selected read drives continuity and both
separate writers. The product domain includes every independent carrier axis.
"""
from functools import lru_cache
from fractions import Fraction as F
import json
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_a_os import AOSReference,graph_constants,PARAMETERS as A_PARAMETERS
from spark_completion_positive import norm_upper
from spark_completion_continuation import need,infnorm
from spark_completion_ci_campaign import exact_bounds

PARAMETERS={**A_PARAMETERS,'tau_PC':'32'}
CARRIER_RADIUS=F(1,64)
TRAP_CARRIER_RADIUS=F(1,2**30)


@lru_cache(maxsize=8)
def global_domain(key):
    """Exact uniform bounds; signed Frobenius ball, conditional resource box."""
    B,_,_,_,overlap=graph_constants(key);m=B.ncols()
    ell=F(str(infnorm(B.transpose()*B)));R=CARRIER_RADIUS
    h=F(m)*R/2;hmin=1-R/2;wl,wh=F(99,100),F(101,100)
    j=wh*(12+ell*wh*4/64+ell*h*4/64)/1024
    g=1-(8+192+j*j)/65536;need(g>F(1,2),'uniform read floor branch')
    a=max(wh-g,1-wl)/(wl+g);den=1-a/4;J=j/den
    flat_squared=m*(a*J/(2*hmin))**2;source=flat_squared/2
    writer_lower=1-(8+192+J*J)/65536
    need(source<R and writer_lower>wl,'both conditional writer envelopes')
    return dict(schema='spark-completion-apc-domain-v1',C=['0','4'],W=['99/100','101/100'],
        carrier_radius=str(R),carrier_norm='symmetric_star_frobenius',signed_carriers=True,
        H_eigenvalue_lower=str(hmin),H_eigenvalue_upper=str(1+R/2),H_deviation_infinity=str(h),
        edge_laplacian_norm=str(ell),baseline_current_upper=str(j),drive_lower=str(g),q_absolute=str(a),
        closure_denominator_lower=str(den),selected_current_upper=str(J),flat_norm_squared_upper=str(flat_squared),
        source_norm_upper=str(source),writer_drive_lower=str(writer_lower),invariant_carrier_ball=True,
        W_invariance_conditional_on_next_C_box=True,resource_box_invariance_claimed=False)


class APCReference(AOSReference):
    def __init__(self,graph):
        super().__init__(graph);self.precision=ctx.prec
        self.domain=global_domain(json.dumps(graph,sort_keys=True))
        self.carrier_pairs=[(i,j) for i in range(self.m) for j in range(i,self.m) if self.overlap[i][j]]
        self.carrier_dimension=len(self.carrier_pairs);self.carrier_writer_count=0;self.selected_read_count=0

    def zero(self):return arb_mat(self.m,self.m)

    def source(self,f):
        Z=self.zero()
        for i,j in self.carrier_pairs:
            Z[i,j]=self.q(self.overlap[i][j],4)*f[i,0]*f[j,0];Z[j,i]=Z[i,j]
        return Z

    def coordinates(self,Z):
        return arb_mat([[(1 if i==j else arb(2).sqrt())*Z[i,j]] for i,j in self.carrier_pairs])

    def validate(self,C,L,Z):
        need(ctx.prec==self.precision,'construct model at actual precision')
        need(C.nrows()==self.n and C.ncols()==1 and L.nrows()==self.m and L.ncols()==1 and
             Z.nrows()==Z.ncols()==self.m,'full C/W/Z dimensions')
        need(all(0<=x<=4 for x in C.entries()),'C outside declared domain')
        need(all(self.q(99,100)<=x<=self.q(101,100) for x in self.exp(L).entries()),'W outside declared domain')
        need(all(Z[i,j].mid()==Z[j,i].mid() and Z[i,j].rad()==Z[j,i].rad() for i,j in self.carrier_pairs),'symmetric carrier enclosure')
        need(all(Z[i,j]==0 for i in range(self.m) for j in range(self.m) if not self.overlap[i][j]),'carrier star support')
        need(norm_upper(Z)<=self.q(1,64),'carrier norm domain')

    def pc_read(self,C,L,Z):
        self.validate(C,L,Z);W=self.exp(L);H=self.I+Z/2
        selected=self.read(C,W,H,self.rows(C,W));source=self.source(selected['causal_flat'])
        need(norm_upper(source)<=self.q(1,64),'carrier source domain')
        self.selected_read_count+=1
        return dict(geometry=H,selected=selected,source=source,_C=C,_L=L,_Z=Z,_W=W)

    def advance(self,C,L,Z,read):
        need(C is read['_C'] and L is read['_L'] and Z is read['_Z'],'selected full-state read subject changed')
        J=read['selected']['current'];ca=C-32*self.B*J
        exponent,_=self.exponent(ca,read['_W'],J)
        la=self.decay*L+(1-self.decay)*exponent
        za=self.decay*Z+(1-self.decay)*read['source']
        self.writer_count+=1;self.carrier_writer_count+=1
        return ca,la,za

    def step(self,C,L,Z):
        read=self.pc_read(C,L,Z);ca,la,za=self.advance(C,L,Z,read)
        return dict(read=read,after=ca,logW_after=la,carrier_after=za)

    def jacobian(self,C,L,Z):
        """All C/W/Z columns; orthonormal symmetric carrier coordinates.

        Every carrier off-diagonal basis has entries 1/sqrt(2). H^{-1}
        derivatives share one multiple-right-hand-side solve.
        """
        read=self.pc_read(C,L,Z);W=read['_W'];H=read['geometry'];sel=read['selected']
        nx=self.n+self.m;d=nx+self.carrier_dimension;zero=self.zero()
        dC=arb_mat([[int(i==j) for j in range(d)] for i in range(self.n)])
        dL=arb_mat([[int(self.n+i==j) for j in range(d)] for i in range(self.m)])
        dW=self.diag(W)*dL;dHs=[zero]*nx
        for i,j in self.carrier_pairs:
            basis=self.zero();basis[i,j]=self.q(1,2) if i==j else 1/(2*arb(2).sqrt());basis[j,i]=basis[i,j];dHs.append(basis)
        rows=self.rows(C,W,dC,dW)
        dJ,dq=self.read_derivative(C,W,H,sel,dC,dW,dHs,rows)
        f=sel['causal_flat'];hf=arb_mat([[sum(dHs[k][i,j]*f[j,0] for j in range(self.m)) for k in range(d)] for i in range(self.m)])
        df=H.solve((self.diag(sel['q'])*dJ+self.diag(sel['current'])*dq)/2-hf)
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
        p=runs['current']['proof'];m=APCReference(targets['1']['graph']);n=m.n;nx=n+m.m;d=nx-1;k=m.carrier_dimension
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
            other=APCReference(t['graph']);need(other.nodes==m.nodes and other.pairs==m.pairs and other.terms==m.terms and other.carrier_pairs==m.carrier_pairs,'chiral equation identity')
            geometry[chi]=old.uniform_geometry(other,cb,lb,p['center'],lambda i,j:arb(sum(abs(S[i,jj]-S[j,jj]) for jj in range(d))))
            lower=F(geometry[chi]['weighted_selector_lower'])*(1-TRAP_CARRIER_RADIUS/2)
            need(lower>F(1,64),'carrier-adjusted selector separation');geometry[chi]['carrier_adjusted_selector_lower']=str(lower)
            need(geometry[chi]['complete_basins']==p['complete_basins'][chi],'complete A_PC basin roster')
        return dict(schema='spark-completion-apc-full-return-v1',center=p['center'],logW_center=p['logW_center'],carrier_center='zero',
            domain_record_digest=proposal['record_digest'],metric='max(||U(deltaC,delta logW)||_infinity,||Z||_F/rho)',radius='1',
            carrier_radius=str(TRAP_CARRIER_RADIUS),relative_dimension=d+k,resource_dimension=n-1,conductance_dimension=m.m,
            carrier_dimension=k,independent_carrier_pairs=m.carrier_pairs,
            derivative_blocks={name:exact_bounds(x) for name,x in dict(XX=xx,XZ=xz,ZX=zx,ZZ=zz).items()},
            contraction=exact_bounds(q),center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            geometry=geometry,complete_basins={chi:g['complete_basins'] for chi,g in geometry.items()},domain=m.domain,
            incoming_carrier_geometry=True,both_independent_writers=True,stationary_writer_self_consistent=True,
            stationary_carrier_argument='BJ=0 and positive diagonal closure imply J=f=S=0; stationary carrier decay gives Z=0, hence H=I and W=G(C,W,0).',
            all_conductance_directions_included=True,all_carrier_directions_included=True,
            OS_derivative_reused=False,earlier_family_trajectory_reused=False,proof_precision_bits=512,native_completion=False,accepted_authority=False),U
