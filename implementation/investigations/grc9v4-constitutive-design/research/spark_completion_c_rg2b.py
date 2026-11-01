"""Quartic C_RG2b: frozen argument completion, Lipschitz section and metric tubes.

No derivative of the invariant section is used. Midpoints propose finite chains
and charge-21 tube centers; residuals and full propagated radii enclose the
exact physical trajectory. Immutable FLINT graph algebra alone is cached.
"""
from functools import lru_cache
from fractions import Fraction as F
import json
from flint import arb,arb_mat,fmpq,fmpq_mat,ctx
from spark_completion_os_reference import COSReference
from spark_completion_positive import norm_upper,content_id
from spark_completion_continuation import need,infnorm,spectral_domain,geometric_roster
from spark_completion_ci_campaign import exact_bounds

ETA=F(1,1024)
DT=F(8)
RHO=F(1,1024)
LIP=F(1,256)
DEPTH=16
SWEEPS=8
NEWTON_LIMIT=12
PROPOSAL_BITS=256
PRECISION=512
CENTER_BITS=240
TRAP_RADIUS=F(1,8192)
PARAMETERS=dict(eta=str(ETA),duration=str(DT),kappa_Phi='1/64',kappa_M='0',tau='1',
    chi='1/2',zeta='1/2',kappa_H='1/2',site='(C-2)^3-(C-2)')


def fraction(x):return F(str(x))
def ball(x):return arb(fmpq(str(x)))
def upper(x):return x.upper().fmpq()
def midpoint(M):return arb_mat([[x.mid() for x in row] for row in M.tolist()])
def maxnorm(M):return max(sum(abs(M[i,j]).upper() for j in range(M.ncols())) for i in range(M.nrows())).upper()
def ceil_dyadic(x,bits=160):
    q=fraction(x.upper().fmpq());scale=2**bits
    return F(-((-q.numerator*scale)//q.denominator),scale)


@lru_cache(maxsize=8)
def graph_algebra(encoded):
    m=COSReference(json.loads(encoded),'rational');B=m.B;D=m.Le;M=(m.q(3,4)*m.I+D).inv()
    A=B*(m.I+M/4)*B.transpose();L=B*B.transpose();pi=m.matrix([[m.q(1,m.n) for _ in range(m.n)]for _ in range(m.n)])
    P=(A+pi).inv();trace=sum(P[i,i] for i in range(m.n))-1
    need(trace>0,'charge metric trace')
    return dict(B=B,D=D,I=m.I,M=M,A=A,L=L,P=P,trace=trace,overlap=m.overlap,
        a0=fraction(infnorm(M)),amax=fraction(infnorm(A)),AL=fraction(infnorm(A*L)),
        b=fraction(infnorm(B)),ell=fraction(infnorm(D)),s=F(max(map(sum,m.overlap)),8))


def polynomial_image(algebra,lo,hi):
    """Exact separable cubic map at H=I; interval extrema include critical roots."""
    A,L=algebra['A'],algebra['L'];AL=A*L;n=A.nrows();h=ETA*DT
    out=[]
    for i in range(n):
        lows=[];highs=[]
        for j in range(n):
            a=-h*fraction(A[i,j]);b=F(i==j)+h*fraction(A[i,j])+h*fraction(AL[i,j])/64
            xs=[ball(lo-2),ball(hi-2)]
            if a and -b/(3*a)>0:
                r=ball(-b/(3*a)).sqrt()
                for x in (r,-r):
                    if not (x.upper()<ball(lo-2) or x.lower()>ball(hi-2)):xs.append(x)
            vals=[ball(a)*x**3+ball(b)*x for x in xs]
            lows.append(min(x.lower() for x in vals));highs.append(max(x.upper() for x in vals))
        out.append((2+sum(lows),2+sum(highs)))
    return min(x[0] for x in out),max(x[1] for x in out)


@lru_cache(maxsize=8)
def global_domain(encoded):
    """Fresh quartic bounds; physical agreement and nested domains are explicit."""
    g=json.loads(encoded);a=graph_algebra(encoded);source=len(g['live_node_ids'])==12
    need(source or len(g['live_node_ids'])==15,'only declared source/target graphs')
    u=F(3,2) if source else F(33,16);lo,hi=2-u,2+u
    b,ell,a0,an,al,s=(a[k] for k in ('b','ell','a0','amax','AL','s'))
    need(a0*RHO*ell<1,'uniform current inverse')
    inverse=a0/(1-a0*RHO*ell);hinv=1/(1-RHO);h=ETA*DT
    site=max(u**3-u,F(1));curv=max(3*u*u-1,F(1));span=2*u
    j0=ETA*(2*site+ell*(1+RHO)*span/64);j0x=ETA*(2*curv+ell*(1+RHO)*2/64);j0h=ETA*ell*span/64
    y=inverse*j0;flat=hinv*y/2;fx=hinv*inverse*j0x/2;fh=hinv*(inverse*(j0h+ell*y)/2+flat)
    gx=2*s*flat*fx;gh=2*s*flat*fh;V=s*flat**2
    jh=j0h*(1+inverse/4)+inverse*ell*y/4;ah=DT*b*jh
    qdiff=inverse*RHO*ell*a0/4
    perturb=h*b*2*(qdiff*(curv+2*b/64)+(1+inverse/4)*2*b*RHO/64)
    ax=h*(an*curv+al/64)+perturb;mf=h*(an*site+al*u/64)+ah*RHO
    ellbase=ax+ah*LIP;inv=1/(1-ellbase)
    image_lip=(gx+gh*LIP)*inv;q=gh+(gx+gh*LIP)*inv*ah
    need(ellbase<1 and V<RHO and image_lip<=LIP and q<1,'quartic graph-transform premises')
    with ctx.workprec(PRECISION):
        if source:
            km=(F(7,8),F(25,8));k=(F(9,16),F(55,16));image=(ball(km[0]-mf),ball(km[1]+mf))
        else:
            km=(F(-1,32),F(129,32));k=(F(-3,64),F(259,64))
            left,right=polynomial_image(a,*km);image=(left-ball(ah*RHO),right+ball(ah*RHO))
        need(lo<k[0]<km[0]<km[1]<k[1]<hi,'strict nested signed charts')
        need(image[0]>ball(k[0]) and image[1]<ball(k[1]),'whole K_minus image containment')
        spectrum=spectral_domain(g)
        need((1-RHO)*F(spectrum['nonconstant_eigenvalue_lower'])>F(1,64),'uniform H selector separation')
        return dict(schema='spark-completion-crg2b-domain-v1',completion='bounded_increment_argument_retraction_v1',
            resource_agreement=[str(lo),str(hi)],K_minus=list(map(str,km)),K=list(map(str,k)),
            contained_image=[exact_bounds(image[0])[0],exact_bounds(image[1])[1]],
            geometry_radius=str(RHO),geometry_norm='induced_infinity_symmetric_star',
            section_lipschitz=str(LIP),section_value_radius=str(V),image_lipschitz=str(image_lip),
            A_X=str(ax),A_H=str(ah),G_X=str(gx),G_H=str(gh),base_lipschitz=str(ellbase),
            inverse_lipschitz=str(inv),graph_transform_contraction=str(q),section_tail=str(q**DEPTH*V),
            current_inverse_norm=str(inverse),hodge_inverse_norm=str(hinv),reference_inverse_norm=str(a0),
            incidence_norm=str(b),edge_laplacian_norm=str(ell),overlap_sum_over_8=str(s),
            reference_resource_operator_norm=str(an),reference_AL_norm=str(al),global_displacement=str(mf),
            selector=spectrum,global_resource_box_invariance_claimed=False,section_C1_claimed=False,
            reference_zero_site_bounds_reused=False)


class CRG2bReference(COSReference):
    def __init__(self,graph):
        super().__init__(graph,'arb');self.graph=graph;self.precision=ctx.prec
        self.key=json.dumps(graph,sort_keys=True,separators=(',',':'));self.algebra=graph_algebra(self.key)
        self.domain=global_domain(self.key);self.P=arb_mat(self.algebra['P']);self.A=arb_mat(self.algebra['A'])
        self.trace=arb(self.algebra['trace']);self.amax=ball(self.algebra['amax']);self.sqrtamax=self.amax.sqrt().upper()
        self.bounds={k:ball(self.domain[k]) for k in ('A_X','A_H','G_X','G_H','inverse_lipschitz','graph_transform_contraction','section_value_radius','section_tail','current_inverse_norm')}
        self.lo,self.hi=map(F,self.domain['resource_agreement']);self.section_calls=0;self.lag_operator_builds=0
        self.newton_iterations=0;self.read_count=0
        self.identity_operators={};self.proposal_sweeps=0

    def clip(self,C):
        rows=[]
        for x in C.entries():
            lo=max(fmpq(str(self.lo)),min(fmpq(str(self.hi)),x.lower().fmpq()))
            hi=max(fmpq(str(self.lo)),min(fmpq(str(self.hi)),x.upper().fmpq()))
            rows.append([arb((lo+hi)/2,(hi-lo)/2)])
        return arb_mat(rows)

    def operators(self,H):
        if H==self.I:
            # Precision belongs to the cache key; no lower-precision operator reuse.
            if ctx.prec in self.identity_operators:return self.identity_operators[ctx.prec]
        M=(self.q(3,4)*self.I+H*self.Le).inv();hi=H.inv();lh=self.B*H*self.Bt
        A=self.B*(self.I+M/4)*self.Bt;self.lag_operator_builds+=1
        out=dict(H=H,M=M,Hi=hi,L=lh,A=A)
        if H==self.I:self.identity_operators[ctx.prec]=out
        return out

    def lag(self,C,ops,*,retract=False):
        c=self.clip(C) if retract else C;phi=ops['L']*c/64-self.site(c)
        j0=-ball(ETA)*self.Bt*phi;y=ops['M']*j0;J=j0+y/4;flat=ops['Hi']*y/2
        H=self.geometry(flat);self.read_count+=1
        return dict(increment=-ball(DT)*self.B*J,geometry=H,current=J,causal_flat=flat,baseline=j0)

    def inverse_proposal(self,target,H,start):
        ops=self.operators(H);X=arb_mat(start);identity=arb_mat([[int(i==j)for j in range(self.n)]for i in range(self.n)])
        threshold=arb(2)**(-PROPOSAL_BITS+32)
        for iteration in range(NEWTON_LIMIT):
            c=self.clip(X);phi=ops['L']*c/64-self.site(c);f=ball(ETA*DT)*ops['A']*phi
            residual=X+f-target;self.newton_iterations+=1
            if maxnorm(residual)<threshold:break
            mask=[int(self.lo<fraction(x.mid().fmpq())<self.hi) for x in X.entries()]
            D=ops['L']/64-arb_mat([[(3*(c[i,0]-2)**2-1) if i==j else 0 for j in range(self.n)]for i in range(self.n)])
            DP=arb_mat([[D[i,j]*mask[j]for j in range(self.n)]for i in range(self.n)])
            jac=identity+ball(ETA*DT)*ops['A']*DP
            X=midpoint(X-jac.solve(residual))
        else:raise ValueError('declared inverse proposal iteration cap')
        return X,ops

    def section(self,C,*,retain_chain=False):
        need(ctx.prec==self.precision and C.nrows()==self.n and C.ncols()==1,'section precision/subject')
        need(all(x.rad()==0 for x in C.entries()),'section query must be an exact proposed tube center')
        need(all(ball(self.lo)<x<ball(self.hi) for x in C.entries()),'physical query outside completion agreement chart')
        self.section_calls+=1
        with ctx.workprec(PROPOSAL_BITS):
            xs=[arb_mat(C) for _ in range(DEPTH+1)];hs=[arb_mat(self.I) for _ in range(DEPTH+1)]
            for _ in range(SWEEPS):
                self.proposal_sweeps+=1
                ops=[]
                for i in range(1,DEPTH+1):
                    xs[i],op=self.inverse_proposal(xs[i-1],hs[i],xs[i]);ops.append(op)
                generated=[midpoint(self.lag(xs[i],ops[i-1],retract=True)['geometry']) for i in range(1,DEPTH+1)]
                newhs=generated+[arb_mat(self.I)]
                change=max(maxnorm(a-b) for a,b in zip(hs,newhs));hs=newhs
                # Proposal-only early stop. Every level is subsequently
                # certified afresh at PRECISION, including both residuals.
                slope=self.bounds['G_H']+ball(LIP)*self.bounds['A_H']
                if slope*change/(1-self.bounds['graph_transform_contraction'])<self.bounds['section_tail']/16:break
        need(xs[0]==C and hs[-1]==self.I,'finite section boundaries')
        rx=arb(0);rh=arb(0);levels=[]
        for i in range(1,DEPTH+1):
            H=hs[i];need(maxnorm(H-self.I)<=ball(RHO),'finite geometry ball')
            need(all(H[j,k]==H[k,j] for j in range(self.m)for k in range(self.m)),'finite geometry symmetry')
            need(all(H[j,k]==0 for j in range(self.m)for k in range(self.m)if not self.overlap[j][k]),'finite geometry support')
            r=self.lag(xs[i],self.operators(H),retract=True)
            xr=maxnorm(xs[i]+r['increment']-xs[i-1]);hr=maxnorm(hs[i-1]-r['geometry']);rx=max(rx,xr);rh=max(rh,hr)
            if retain_chain:levels.append(dict(X=[str(x.fmpq()) for x in xs[i].entries()],
                H=[str(H[j,k].fmpq())for j in range(self.m)for k in range(j,self.m)if self.overlap[j][k]],
                state_residual=exact_bounds(xr),geometry_residual=exact_bounds(hr)))
        # Backward elimination of the coupled residual inequalities. Each exact
        # finite-level section stays in the proved global Lipschitz class.
        L=ball(LIP);q=self.bounds['graph_transform_contraction']
        residual_error=((rh+L*rx)/(1-q)).upper();tail=self.bounds['section_tail'];error=(residual_error+tail).upper()
        need(maxnorm(hs[0]-self.I)+error<ball(RHO),'returned section ball')
        H=arb_mat(self.m,self.m)
        for i in range(self.m):
            for j in range(i,self.m):
                if self.overlap[i][j]:H[i,j]=arb(hs[0][i,j].fmpq(),error.fmpq());H[j,i]=H[i,j]
        out=dict(proposal=hs[0],geometry=H,error=error,residual_error=residual_error,tail=tail,
            state_residual=rx,geometry_residual=rh,read=self.lag(C,self.operators(H)),subject=C)
        if retain_chain:out['chain']=levels
        return out

    def quantize(self,C,charge=21):
        scale=2**CENTER_BITS;values=[]
        for x in C.entries()[:-1]:
            q=x.mid().fmpq();values.append(fmpq((q.numerator*scale)//q.denominator,scale))
        values.append(fmpq(charge)-sum(values));return arb_mat([[arb(x)] for x in values])

    def box(self,C,radius):
        width=(self.sqrtamax*radius).upper()
        return arb_mat([[arb(x.fmpq(),width.fmpq())]for x in C.entries()])

    def section_local_lipschitz(self,C,radius,section):
        """Difference bounds through the inverse footprint; no D Gamma."""
        a=self.algebra;b=ball(a['b']);ell=ball(a['ell']);s=ball(a['s']);inv=self.bounds['inverse_lipschitz']
        width=(self.sqrtamax*radius).upper();f0=maxnorm(section['read']['increment'])
        R=(inv*(width+f0)).upper();V=min(self.bounds['section_value_radius'].upper(),
            (maxnorm(section['proposal']-self.I)+section['error']+ball(LIP)*R).upper())
        cb=self.clip(arb_mat([[arb(x.fmpq(),R.fmpq())]for x in C.entries()]))
        curvature=max(abs(3*(x-2)**2-1).upper() for x in cb.entries())
        span=max(x.upper() for x in cb.entries())-min(x.lower() for x in cb.entries())
        inverse=ball(a['a0'])/(1-ball(a['a0'])*V*ell);hinv=1/(1-V)
        j0x=ball(ETA)*(2*curvature+ell*(1+V)*2/64);j0h=ball(ETA)*ell*span/64
        reference=self.lag(C,self.operators(self.I));j0=maxnorm(reference['baseline'])+j0x*R+j0h*V
        y=inverse*j0;flat=hinv*y/2;fx=hinv*inverse*j0x/2;fh=hinv*(inverse*(j0h+ell*y)/2+flat)
        gx=2*s*flat*fx;gh=2*s*flat*fh
        local=((gx+gh*ball(LIP))*inv).upper()
        return min(ball(LIP),local),dict(inverse_footprint_radius=R,geometry_deviation=V,G_X=gx,G_H=gh)

    def return_lipschitz(self,C,radius,section):
        """P-metric differences: reference self-adjoint map plus H perturbations."""
        a=self.algebra;ell=ball(a['ell']);h=ball(ETA*DT);cb=self.box(C,radius)
        need(all(ball(self.lo)<x<ball(self.hi) for x in cb.entries()),'whole physical tube outside agreement chart')
        curv=[3*(x-2)**2-1 for x in cb.entries()]
        dmin=min(x.lower() for x in curv)-ell/64;dmax=max(x.upper() for x in curv)
        # ||BB^T||_2 <= ||B^T B||_infinity. A0 has positive charge-tangent
        # eigenvalues in [1/trace,amax]; P=A0^-1 on that exact tangent.
        low=dmin/self.trace if dmin>=0 else self.amax*dmin
        high=self.amax*max(arb(0),dmax)
        reference=max(abs(1-h*low).upper(),abs(1-h*high).upper())
        L,foot=self.section_local_lipschitz(C,radius,section)
        V=(maxnorm(section['proposal']-self.I)+section['error']+ball(LIP)*self.sqrtamax*radius).upper()
        need(V<ball(RHO),'local section geometry domain')
        a2=(1+V)/(1-V)*self.q(4,3);q2=1+a2/4
        D0=max(abs(x).upper() for x in curv)+ell/64
        qdiff=a2*V*ell/3
        partial=h*ell*(qdiff*D0+q2*ell*V/64)
        z=norm_upper(self.Bt*cb);phi=self.B*self.Bt*cb/64-self.site(cb)
        j0=ball(ETA)*norm_upper(self.Bt*phi)+ball(ETA)*ell*V*z/64
        y=a2*j0
        Hslope=ball(DT)*ell.sqrt()*(ball(ETA)*ell*z*q2/64+a2*ell*y/4)
        convert=(self.amax*self.trace).sqrt()
        correction=(partial+Hslope*L)*convert;q=(reference+correction).upper()
        return q,dict(reference=reference,H_partial_correction=partial*convert,
            section_difference_correction=Hslope*L*convert,section_lipschitz=L,**foot)

    def advance_tube(self,C,radius,section=None):
        section=self.section(C) if section is None else section
        need(section['subject'] is C,'section subject changed')
        q,parts=self.return_lipschitz(C,radius,section)
        value=C+section['read']['increment'];center=self.quantize(value)
        defect=(norm_upper(value-center)*self.trace.sqrt()).upper()
        after=ball(ceil_dyadic(q*radius+defect))
        need(after<arb(2)**-64,'declared validated-tube radius cap')
        return center,after,dict(lipschitz=q,defect=defect,parts=parts,section=section)


def trap_certificate(targets):
    """Full physical C return on a charge-tangent ball, using only differences."""
    from spark_completion_positive import propose_center
    with ctx.workprec(PRECISION):
        m=CRG2bReference(targets['1']['graph']);center=propose_center(m);C=m.vector(center);r=ball(TRAP_RADIUS)
        s=m.section(C);q,parts=m.return_lipschitz(C,r,s)
        defect=(norm_upper(s['read']['increment'])*m.trace.sqrt()).upper();margin=(1-q)*r-defect
        need(q<1 and margin>0,'strict full C_RG2b invariant metric ball')
        box=m.box(C,r);km=list(map(ball,m.domain['K_minus']))
        need(all(km[0]<x<km[1] for x in box.entries()),'trap inside physical agreement chart')
        expected={'p':['p','private'],'sc2-positive-module/satellite/2':['n2','n8','sc2-positive-module/satellite/2']}
        rosters={}
        for chi,t in targets.items():
            need([(e['tail']['node_id'],e['head']['node_id']) for e in t['graph']['edges']]==m.edges,'chiral incidence changed')
            rosters[chi]=geometric_roster(t['graph'],box,m.nodes)
            need(rosters[chi]==expected,'whole trapping ball lacks complete descendant basins')
        return dict(center=center,radius=str(TRAP_RADIUS),coordinate_radius=exact_bounds(m.sqrtamax*r)[1],
            metric='(A0 + 11^T/n)^-1 on exact charge-21 tangent space',relative_dimension=m.n-1,
            A_max=str(m.algebra['amax']),inverse_trace=str(m.algebra['trace']),
            contraction=exact_bounds(q),center_defect=exact_bounds(defect),strict_image_margin=exact_bounds(margin),
            difference_bounds={k:exact_bounds(v) for k,v in parts.items()},complete_basins=rosters,
            section_domain=m.domain,full_physical_state=['C'],section_C1_claimed=False,
            full_return_difference_bound=True,completion_relative=True,geometry_history_transported=False,
            earlier_family_trajectory_reused=False,native_conformance=False),m.algebra['P']
