"""Quartic A_RG2b completion with the full fresh-resource conductance writer.

Only C and log W are state. A frozen bounded-increment completion on
X=(C,64 log W) defines a unique Lipschitz invariant section. Finite inverse
chains include the writer; interval residuals bound every proposal error.
No derivative of Gamma, native zero-site bound, or independent H history is used.
"""
from functools import lru_cache
from fractions import Fraction as F
import json
from flint import arb, arb_mat, fmpq, fmpq_mat, ctx
from spark_completion_a_os import AOSReference, graph_constants, PARAMETERS as A_PARAMETERS
from spark_completion_c_rg2b import ball, maxnorm, midpoint, ceil_dyadic
from spark_completion_ci_campaign import exact_bounds
from spark_completion_continuation import need, infnorm, spectral_domain

DT=F(16)
SCALE=F(64)
Y_RADIUS=F(1,16)
RHO=F(1,1024)
LIP=F(1,256)
DEPTH=16
SWEEPS=8
NEWTON_LIMIT=16
PRECISION=768
PROPOSAL_BITS=384
CENTER_BITS=320
PARAMETERS={**A_PARAMETERS,'duration':str(DT)}
SOURCE_CHART={
    'n1':('139/64','9/4'),'n2':('31/16','129/64'),'n3':('121/64','63/32'),
    'n4':('95/64','25/16'),'n5':('91/64','49/32'),'n6':('87/64','23/16'),
    'n7':('23/16','97/64'),'n8':('23/16','49/32'),'n9':('91/64','49/32'),
    'p':('185/64','191/64'),'v':('67/32','143/64'),'private':('57/64','31/32')}
TARGET_CHART={
    'n1':('17/16','9/4'),'n2':('69/64','133/64'),'n3':('69/64','63/32'),
    'n4':('65/64','25/16'),'n5':('57/64','97/64'),'n6':('63/64','23/16'),
    'n7':('1','97/64'),'n8':('57/64','97/64'),'n9':('63/64','97/64'),
    'p':('185/64','51/16'),'private':('57/64','37/32'),
    'sc2-positive-module/core':('-1/64','37/32'),
    'sc2-positive-module/satellite/1':('-1/64','19/16'),
    'sc2-positive-module/satellite/2':('115/64','205/64'),
    'sc2-positive-module/satellite/3':('-1/64','19/16')}


@lru_cache(maxsize=8)
def global_domain(key):
    """Exact rational global partial bounds in max(||C||inf,64||logW||inf)."""
    g=json.loads(key);B,_,_,_,overlap=graph_constants(key)
    source=len(g['live_node_ids'])==12
    need(source or len(g['live_node_ids'])==15,'declared graphs only')
    chart=SOURCE_CHART if source else TARGET_CHART
    need(set(chart)==set(g['live_node_ids']),'exact chart roster')
    intervals=[tuple(map(F,chart[v])) for v in g['live_node_ids']]
    lo=min(a for a,b in intervals);hi=max(b for a,b in intervals)
    u=max(abs(lo-2),abs(hi-2));span=hi-lo
    b=F(str(infnorm(B)));ell=F(str(infnorm(B.transpose()*B)))
    s=F(max(map(sum,overlap)),8)
    wl,wu=1-Y_RADIUS/SCALE,1/(1-Y_RADIUS/SCALE)
    site=max(u**3-u,F(1));curv=max(3*u*u-1,F(1))
    j0=wu*(2*site+ell*(wu+RHO)*span/64)/1024
    j0c=wu*(2*curv+2*ell*(wu+RHO)/64)/1024
    j0y=(j0+wu*wu*ell*span/65536)/SCALE
    j0x=j0c+j0y;j0h=wu*ell*span/65536
    emin=2*lo/65536;emax=(2*hi+12*span**2+j0*j0)/65536
    gl,gu=1-emax,1/(1+emin)
    need(gl>F(1,2) and 1+emin>0,'read floor/exp bound')
    qabs=max(abs((wl-gu)/(wl+gu)),abs((wu-gl)/(wu+gl)))
    rowx=2+2*span/SCALE
    ex=(2+24*span*rowx+2*j0*j0x)/65536;eh=2*j0*j0h/65536
    qx=(1/SCALE+ex)/2;qh=eh/2;den=1-qabs/4
    j=j0/den;jx=j0x/den+j0*qx/(4*den**2);jh=j0h/den+j0*qh/(4*den**2)
    # The exact vertex-specific reference derivative retains graph cancellation.
    lap=B*B.transpose();lap2=lap*lap;curvatures=[]
    for a,z in intervals:
        ends=[3*(a-2)**2-1,3*(z-2)**2-1]
        curvatures.append((F(-1) if a<=2<=z else min(ends),max(ends)))
    reference=max(sum(max(abs(F(str(lap2[i,k]))/64-F(str(lap[i,k]))*c)
        for c in curvatures[k]) for k in range(B.nrows())) for i in range(B.nrows()))*DT/1024
    wdelta=max(1-wl,wu-1);rdev=(wdelta+qabs/4)/den;rmax=wu/den
    ec=(2+48*span+2*j0*j0c)/65536
    ey=(48*span*span/SCALE+2*j0*j0y)/65536
    jy=j0y/den+j0*(1/SCALE+ey)/(8*den**2)
    perturb=DT*b*2*(rdev*(curv+2*b/64)+rmax*2*b*(wdelta+RHO)/64)/1024
    axc=reference+perturb+DT*b*j0*ec/(8*den**2)+DT*b*jy
    mc=DT*b*j;postx=1+axc;posth=DT*b*jh;postspan=span+2*mc
    writer_max=(2*(hi+mc)+12*postspan**2+j*j)/65536
    writer_min=2*(lo-mc)/65536
    need(1-writer_max>F(1,2),'writer floor bound')
    writer_x=(2*postx+24*postspan*(2*postx+2*postspan/SCALE)+2*j*jx)/65536
    writer_h=(2*posth+24*postspan*2*posth+2*j*jh)/65536
    # 1-exp(-DT/32) <= DT/32. The completed writer clips Y too.
    rate=DT/32
    ax=max(axc,rate*(1+SCALE*writer_x))
    ah=max(DT*b*jh,rate*SCALE*writer_h)
    my=rate*(Y_RADIUS+SCALE*max(writer_max,-writer_min))
    hinv=1/(1-RHO);flat=hinv*qabs*j/2
    fx=hinv*(qx*j+qabs*jx)/2
    fh=hinv*((qh*j+qabs*jh)/2+flat)
    gx=2*s*flat*fx;gh=2*s*flat*fh;value=s*flat*flat
    e=ax+ah*LIP
    need(e<1,'joint C/scaled-log-W base inverse unavailable')
    inverse=1/(1-e);image_lip=(gx+gh*LIP)*inverse
    q=gh+(gx+gh*LIP)*inverse*ah
    need(value<RHO and image_lip<=LIP and q<1,'coupled graph-transform premises')
    # Round outward once to keep finite-tail rational operands compact.
    q=F(-((-q.numerator*2**128)//q.denominator),2**128)
    selector=spectral_domain(g)
    need(wl*(1-RHO)*F(selector['nonconstant_eigenvalue_lower'])>F(1,64),'weighted H selector separation')
    return dict(schema='spark-completion-arg2b-domain-v1',
        completion='bounded_increment_joint_C_scaled_logW_argument_retraction_v1',
        resource_agreement={k:list(v) for k,v in chart.items()},
        scaled_logW_agreement=list(map(str,(-Y_RADIUS,Y_RADIUS))),logW_scale=str(SCALE),
        geometry_radius=str(RHO),section_lipschitz=str(LIP),section_value_radius=str(value),
        A_X=str(ax),A_H=str(ah),G_X=str(gx),G_H=str(gh),base_lipschitz=str(e),
        inverse_lipschitz=str(inverse),image_lipschitz=str(image_lip),graph_transform_contraction=str(q),
        section_tail=str(q**DEPTH*value),resource_displacement=str(mc),scaled_logW_displacement=str(my),
        read_exponent_upper=str(emax),writer_exponent_upper=str(writer_max),
        reference_increment_lipschitz=str(reference),resource_increment_lipschitz=str(axc),
        W_lower=str(wl),W_upper=str(wu),J_upper=str(j),J_X=str(jx),J_H=str(jh),
        selector=selector,section_C1_claimed=False,physical_state_clipped=False,
        whole_agreement_box_forward_invariance_claimed=False,reference_zero_site_bounds_reused=False,
        full_base_state=['C','64 log W_A'],writer_in_inverse=True)


class ARG2bReference(AOSReference):
    def __init__(self,graph):
        super().__init__(graph)
        self.key=json.dumps(graph,sort_keys=True,separators=(',',':'))
        self.domain=global_domain(self.key);self.precision=ctx.prec
        self.chart=[tuple(map(F,self.domain['resource_agreement'][v])) for v in self.nodes]
        self.decay=(-ball(DT/32)).exp()
        self.d=self.n+self.m
        self.state_identity=arb_mat([[int(i==j) for j in range(self.d)] for i in range(self.d)])
        self.zero=arb_mat(self.m,self.m)
        self.section_calls=0;self.newton_iterations=0;self.proposal_sweeps=0;self.section_reuses=0
        self.bounds={k:ball(self.domain[k]) for k in ('A_X','A_H','G_X','G_H',
            'inverse_lipschitz','graph_transform_contraction','section_value_radius','section_tail')}

    def pack(self,C,L):return arb_mat(C.tolist()+[[ball(SCALE)*x] for x in L.entries()])
    def unpack(self,X):
        return arb_mat([[X[i,0]] for i in range(self.n)]),arb_mat([[X[self.n+i,0]/ball(SCALE)] for i in range(self.m)])

    def clip(self,X):
        out=[]
        for i,x in enumerate(X.entries()):
            lo,hi=self.chart[i] if i<self.n else (-Y_RADIUS,Y_RADIUS)
            a=max(fmpq(str(lo)),min(fmpq(str(hi)),x.lower().fmpq()))
            b=max(fmpq(str(lo)),min(fmpq(str(hi)),x.upper().fmpq()))
            out.append([arb((a+b)/2,(b-a)/2)])
        return arb_mat(out)

    def lag(self,X,H,*,retract=False):
        x=self.clip(X) if retract else X;C,L=self.unpack(x);W=self.exp(L)
        selected=self.read(C,W,H);J=selected['current'];after=C-ball(DT)*self.B*J
        exponent,_=self.exponent(after,W,J)
        nextL=self.decay*L+(1-self.decay)*exponent
        self.writer_count+=1
        return dict(increment=self.pack(after-C,nextL-L),geometry=self.geometry(selected['causal_flat']),
            current=J,selected=selected,C=C,L=L,W=W,after=after,logW_after=nextL)

    def fixed_direction(self,X,H,directions,read=None):
        """Fixed-H partial applied to one or many directions; never D Gamma."""
        read=self.lag(X,H) if read is None else read
        C,L,W=read['C'],read['L'],read['W'];d=directions.ncols()
        dc=arb_mat([[directions[i,j] for j in range(d)] for i in range(self.n)])
        dl=arb_mat([[directions[self.n+i,j]/ball(SCALE) for j in range(d)] for i in range(self.m)])
        dw=self.diag(W)*dl;rows=self.rows(C,W,dc,dw)
        dj,_=self.read_derivative(C,W,H,read['selected'],dc,dw,[self.zero]*d,rows)
        dca=dc-ball(DT)*self.B*dj
        _,de=self.exponent(read['after'],W,read['current'],None,dca,dw,dj)
        dlp=self.decay*dl+(1-self.decay)*de
        return arb_mat(dca.tolist()+(ball(SCALE)*dlp).tolist())

    def fixed_jacobian(self,X,H,read=None):
        return self.fixed_direction(X,H,self.state_identity,read)

    def inverse_proposal(self,target,H,start):
        X=arb_mat(start);threshold=arb(2)**(-PROPOSAL_BITS+32)
        for _ in range(NEWTON_LIMIT):
            c=self.clip(X);r=self.lag(c,H);residual=X+r['increment']-target
            self.newton_iterations+=1
            if maxnorm(residual)<threshold:return X
            j=self.fixed_jacobian(c,H,r)-self.state_identity
            for k,x in enumerate(X.entries()):
                lo,hi=self.chart[k] if k<self.n else (-Y_RADIUS,Y_RADIUS)
                if not ball(lo)<x<ball(hi):
                    for i in range(self.d):j[i,k]=0
            X=midpoint(X-(self.state_identity+j).solve(residual))
        raise ValueError('declared joint inverse Newton limit')

    def section(self,X,*,retain_chain=False):
        need(ctx.prec==self.precision and X.nrows()==self.d and X.ncols()==1,'section precision/subject')
        need(all(x.rad()==0 for x in X.entries()),'exact proposed section center required')
        need(self.in_agreement(X),'query outside joint completion agreement')
        self.section_calls+=1
        with ctx.workprec(PROPOSAL_BITS):
            xs=[arb_mat(X) for _ in range(DEPTH+1)];hs=[arb_mat(self.I) for _ in range(DEPTH+1)]
            for _ in range(SWEEPS):
                self.proposal_sweeps+=1
                for i in range(1,DEPTH+1):xs[i]=self.inverse_proposal(xs[i-1],hs[i],xs[i])
                newhs=[midpoint(self.lag(xs[i],hs[i],retract=True)['geometry']) for i in range(1,DEPTH+1)]+[arb_mat(self.I)]
                change=max(maxnorm(a-b) for a,b in zip(hs,newhs));hs=newhs
                slope=self.bounds['G_H']+ball(LIP)*self.bounds['A_H']
                if slope*change/(1-self.bounds['graph_transform_contraction'])<max(
                    self.bounds['section_tail']/16,arb(2)**(-PROPOSAL_BITS+32)):break
        need(xs[0]==X and hs[-1]==self.I,'joint finite-chain boundary')
        rx=arb(0);rh=arb(0);levels=[]
        for i in range(1,DEPTH+1):
            H=hs[i];need(maxnorm(H-self.I)<=ball(RHO),'finite H ball')
            need(all(H[j,k]==H[k,j] for j in range(self.m) for k in range(self.m)),'finite H symmetry')
            need(all(H[j,k]==0 for j in range(self.m) for k in range(self.m) if not self.overlap[j][k]),'finite H support')
            r=self.lag(xs[i],H,retract=True)
            xr=maxnorm(xs[i]+r['increment']-xs[i-1]);hr=maxnorm(hs[i-1]-r['geometry'])
            rx=max(rx,xr);rh=max(rh,hr)
            if retain_chain:levels.append(dict(X=[str(x.fmpq()) for x in xs[i].entries()],
                H=[[str(x.fmpq()) for x in row] for row in H.tolist()],
                state_residual=exact_bounds(xr),geometry_residual=exact_bounds(hr)))
        error=((rh+ball(LIP)*rx)/(1-self.bounds['graph_transform_contraction'])+self.bounds['section_tail']).upper()
        out=self.enclose_section(X,hs[0],error)
        out.update(state_residual=rx,geometry_residual=rh,tail=self.bounds['section_tail'])
        if retain_chain:out['chain']=levels
        return out

    def enclose_section(self,X,proposal,error):
        need(maxnorm(proposal-self.I)+error<ball(RHO),'returned section outside ball')
        H=arb_mat(self.m,self.m)
        for i in range(self.m):
            for j in range(i,self.m):
                if self.overlap[i][j]:H[i,j]=arb(proposal[i,j].fmpq(),error.fmpq());H[j,i]=H[i,j]
        return dict(proposal=proposal,geometry=H,error=error,read=self.lag(X,H),subject=X)

    def in_agreement(self,X):
        return all((ball(self.chart[i][0])<x<ball(self.chart[i][1])) if i<self.n
            else (-ball(Y_RADIUS)<x<ball(Y_RADIUS)) for i,x in enumerate(X.entries()))

    def quantize(self,X,charge=21):
        scale=2**CENTER_BITS;values=[]
        for i,x in enumerate(X.entries()):
            if i==self.n-1:values.append(fmpq(charge)-sum(values));continue
            z=x.mid().fmpq();values.append(fmpq((z.numerator*scale)//z.denominator,scale))
        return arb_mat([[arb(x)] for x in values])

    def tube_box(self,X,r):return arb_mat([[arb(x.fmpq(),r.fmpq())] for x in X.entries()])

    def reuse(self,X,section,nextX):
        """Invariant-section identity with the FULL base-map center shift."""
        need(section['subject'] is X,'reuse subject mismatch')
        read=section['read'];proposal=midpoint(read['geometry'])
        error=(maxnorm(read['geometry']-proposal)+ball(LIP)*maxnorm(X+read['increment']-nextX)).upper()
        self.section_reuses+=1
        return self.enclose_section(nextX,proposal,error)

    def advance_tube(self,X,r,section):
        need(section['subject'] is X,'advance section subject mismatch')
        box=self.tube_box(X,r);need(self.in_agreement(box),'whole tube outside agreement')
        extra=ball(LIP)*r
        H=arb_mat([[arb(section['proposal'][i,j].fmpq(),(section['error']+extra).upper().fmpq())
            if self.overlap[i][j] else arb(0) for j in range(self.m)] for i in range(self.m)])
        # A_H is the global full-base partial, so includes writer sensitivity.
        q=(maxnorm(self.fixed_jacobian(box,H))+self.bounds['A_H']*ball(LIP)).upper()
        value=X+section['read']['increment'];center=self.quantize(value)
        defect=maxnorm(value-center);after=ball(ceil_dyadic(q*r+defect,256))
        need(after<arb(2)**-64,'validated full-state tube radius cap')
        return center,after,dict(lipschitz=q,center_defect=defect)
