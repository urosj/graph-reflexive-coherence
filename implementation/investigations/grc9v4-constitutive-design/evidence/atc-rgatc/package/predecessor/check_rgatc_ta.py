#!/usr/bin/env python3
"""RGATC-T/A: rational theorem budgets and whole-section-envelope certificate.

This is NOT an RG2b section evaluator, native step, trajectory search, or
source-admission tool. It checks an explicit completion's sufficient analytic
majorants and interval implications valid for EVERY section value in its
proved ball. Stdlib plus one retained, unchanged outward-arithmetic kernel.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'deps/retained/arithmetic'))
import certify_atc_sector_readback_point as p
I, GRID = p.I, p.GRID

H = F(1, 2**25)
KH = F(1, 2**32)
RHO = F(1,4096)
LSECTION = F(1,2)
M = F(24,25)
PARAMS = dict(alpha=F(3,8192), beta=F(3,8192), gamma=F(3,4096),
              chi=F(3,64), kah=F(3,4), a=F(19,4), nu=F(1,65536))
GRAPHS = {
 'source': (5, p.SOURCE, (1,1,1,1,0)),
 'target': (6, p.TARGET, (1,1,1,1,0,0)),
}

def require(value, message):
    if not value:
        raise AssertionError(message)


def enc(x):
    if isinstance(x,I): return dict(lo=str(F(x.lo,GRID)),hi=str(F(x.hi,GRID)))
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [enc(v) for v in x]
    return x


def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def span(a,b): return I.bounds(I(a).lo,I(b).hi)


def absupper(x): return F(max(abs(x.lo),abs(x.hi)),GRID)


def log_nonpositive(w):
    """Retained atanh log enclosure, on [1/2,1], 96 terms."""
    require(GRID//2 <= w.lo <= w.hi <= GRID,'log input domain')
    z=(1-w)/(1+w); z2=z.square(); term=z; total=I(0)
    for k in range(96):
        total += term/(2*k+1); term=term*z2
    tail=F(1,3)**193/(193*(1-F(1,9)))
    return -2*(total+span(F(0),tail))


def decay(h): return (8*I(h)*log_nonpositive(I(F(1,2)))).exp_nonpositive()


def completion_certificate():
    # Norms: coordinate sup for (C,W), Frobenius for H. The table uses the
    # entire old positive alpha/beta/gamma/chi/kah box, not just PARAMS.
    # Outer support: C in [-2,11], W in [1/2,3/2]. The auxiliary raw formula PRESERVES the conductance floor.
    # Effective exponent min(E,log(2)) is 1-Lipschitz; all bounds below
    # remain valid across its kink. The physical domains are floor-inactive.
    Cmax=F(11); wmax=F(3,2); chi=F(1,16); margin=1-chi
    alpha=beta=F(1,2048); gamma=F(1,1024)
    require(H <= F(1,2**22),'small-beat envelope')
    require(F(1)/(1-RHO) < 2,'H inverse bound')
    # Source/target maximum degree 4, <=5 edges, ridge-one WLS row l1 <=2.
    for name,(n,edges,pos) in GRAPHS.items():
        require(n<=6 and len(edges)<=5,'finite graph counts')
        for i in range(n):
            nbr=[v if u==i else u for u,v in edges if i in (u,v)]
            require(len(nbr)<=4,'degree bound')
            require(all(abs(pos[j]-pos[i])<=1 for j in nbr),'host increments')
    # All entries below are upper bounds, with intentionally large slack.
    require((F(19,4)+F(1,4096))*Cmax+F(1,65536)*Cmax*Cmax/2 < 53,'polynomial value bound')
    require(F(19,4)+F(1,4096)+11*F(1,65536)<5,'polynomial slope bound')
    require(100+5+10*RHO<106,'potential state Lipschitz budget')
    phi = 4*wmax*2*Cmax + 53 + 100*RHO
    require(phi < 186,'potential/stiffness/geometry value bound')
    b, bX, bH = F(600),F(1024),F(512)
    require(2*wmax*phi < b,'baseline value')
    require(2*186+2*wmax*106 < bX,'baseline state Lipschitz')
    require(2*wmax*100 < bH,'baseline H Lipschitz')
    EX=alpha+beta*44*4+gamma*b*bX
    EH=gamma*b*bH
    E=alpha*Cmax+beta*44**2/2+gamma*b*b/2
    require(E<256 and EX<1024 and EH<512,'read exponent majorants')
    qX,qH=F(1024),F(256)
    require((2+1024)/F(2)<qX and F(512)/2<=qH,'response Lipschitz')
    J,JX,JH=F(2**10),F(2**16),F(2**14)
    require(b/margin<J,'current value')
    require(bX/margin+b*chi*qX/margin**2<JX,'current state Lipschitz')
    require(bH/margin+b*chi*qH/margin**2<JH,'current H Lipschitz')
    V,VX,VH=F(2**9),F(2**19),F(2**17)
    require(2*chi*3*J<V,'flat value')
    require(2*chi*3*(qX*J+JX)<VX,'flat state Lipschitz')
    require(4*chi*3*J+2*chi*3*(qH*J+JH)<VH,'flat H Lipschitz')
    MS,SX,SH=F(2**18),F(2**29),F(2**27)
    require(V*V<=MS and 2*V*VX<=SX and 2*V*VH<=SH,'normalized Star bounds')
    # Post-C is bounded by 12, derivative <=2, and H derivative <=2**16*h.
    require(Cmax+4*H*J < 12 and 1+4*H*JX<2,'post-C value and derivative')
    EV=alpha*12+beta*48**2/2+gamma*J*J/2
    EVX=2*(alpha+beta*48*4)+gamma*J*JX
    EVH=(alpha+beta*48*4)*4*H*JH+gamma*J*JH
    require(EV<2**10 and EVX<2**17 and EVH<2**15,'refreshed writer exponent')
    # theta=1-exp(-h/tau)<8h, tau=1/(8log2), |log W|<1.
    require(8*(2**10+1)<2**14,'writer log increment')
    require(F(2**14)*H < F(1,2),'writer exponential <=2 regime')
    require(wmax*2*2**14 < 2**16,'writer increment bound / h')
    require(F(2**15)+3*8*(2**17+2)<2**22,'writer state derivative / h')
    require(3*8*2**15 < 2**20,'writer H derivative / h')
    # Product cubic cutoff has state-sup Lipschitz <=1.5*n+6*m<=39<64.
    cutoff=F(64)
    require(F(3,2)*6+6*5<cutoff,'cutoff product bound')
    Mf=F(2**16)*H
    FX=F(2**23)*H # raw 2**22 + cutoff 64 * raw Mf/h =2**23
    FH=F(2**20)*H
    GX=F(2**30); GH=SH
    require(SX+cutoff*MS<GX,'completed structural state derivative')
    ell=FX+FH*LSECTION
    inv=1/(1-ell)
    lipschitz_image=KH*(GX+GH*LSECTION)*inv
    q=KH*(GH+(GX+GH*LSECTION)*inv*FH)
    radius=KH*MS
    require(ell<F(1,2) and inv<2,'global inverse')
    require(Mf<F(1,5),'physical set to analytic core buffer')
    require(radius<RHO,'section value self-map')
    require(lipschitz_image<LSECTION,'section Lipschitz self-map')
    require(q<F(1,16),'section C0 contraction')
    return dict(beat=H,kappa_H=KH,geometry_ball=RHO,section_lipschitz=LSECTION,
        raw_majorants=dict(b=b,b_X=bX,b_H=bH,J=J,J_X=JX,J_H=JH,V=V,V_X=VX,V_H=VH,
                           S=MS,S_X=SX,S_H=SH,f=Mf,f_X=F(2**22)*H,f_H=FH),
        completed_majorants=dict(cutoff_lipschitz=cutoff,f_X=FX,f_H=FH,G_X=GX,G_H=GH),
        inverse_lipschitz=inv,base_increment_lipschitz=ell,
        section_value_bound=radius,section_lipschitz_image=lipschitz_image,
        graph_transform_contraction=q,
        completion='rgatc_paired_floor_preserving_completion_v1_proposed',
        physical_agreement='source positive Q9 x>=2.9 and target positive Q9 X<=1.5; W in [24/25,1]',
        analytic_core=dict(C=['-1','10'],W=['3/4','5/4']),
        outer_support=dict(C=['-2','11'],W=['1/2','3/2']),
        global_regularities='bounded Lipschitz; C1 of the auxiliary floor surface or section not required',
        native_completion_admitted=False)


def fixed_geometry_bounds():
    K,rr=F(1,2048),F(1,783)
    E=90*RHO+rr*(F(11,2)+90*RHO)
    mu=F(5,2)*(F(19,250)-6*K-F(2,3)*E)
    lo,hi=M*F(7,16),F(73,16)
    bare=min(z*(F(19,4)-z) for z in (lo,hi))
    bcoef=4+F(5,2)*K+F(125,8)*RHO
    err=F(5,2)*(F(5,2)*K+F(125,8)*RHO+rr*bcoef)
    delta=bare-err
    require(mu>F(1,8),'positive source growth rate')
    require(delta>F(3,4),'positive target decay rate')
    require(1-F(1,8)*F(19,4)**2/4>0,'bare spectral multiplier sign')
    # Neither 65/64 nor the old 71-beat horizon is imported at the new h.
    N=16/H
    require(N.denominator==1 and N>1 and N*(H/8)==2,'finite positivity contradiction, strict Bernoulli')
    transfer2=12*F(2,5)**2+4*F(1,50)**2+2*F(23,320)**2
    funding=F(31,64)*F(21,5)-F(61,50)
    require(transfer2<F(9,4) and funding>0,'both-role transfer')
    require(F(5,6)<F(11,12)**2,'charge-hyperplane coordinate norm inequality')
    require(F(3,2)-F(11,12)*F(3,2)==F(1,8),'positive target floor without first-entry claim')
    return dict(source_rate=mu,source_multiplier=1+H/8,positive_source_horizon=int(N),
        target_rate=delta,target_factor=1-F(3,4)*H,target_floor=F(1,8),
        target_first_step_below_two_thirds_claimed=False,
        transfer_X_squared_upper=transfer2,funding_lower=funding,
        source_support_gap=5*M-F(19,4),target_support_gap=F(19,4)-hi,
        fixed_geometry_source_error=E,target_error_rate=err,
        statement='new h-dependent inequalities from inherited fixed-H algebra, not imported request certificate')


def descriptor(graph,C):
    n,edges,pos=GRAPHS[graph];out=[]
    for i in range(n):
        num=I(0);den=1
        for u,v in edges:
            if i not in (u,v):continue
            j=v if u==i else u;dx=pos[j]-pos[i]
            num += dx*(C[j]-C[i]);den += dx*dx
        out.append(num/den)
    return tuple(out)


def drive(graph,C,D,J):
    out=[]
    for (u,v),j in zip(GRAPHS[graph][1],J):
        E=PARAMS['alpha']*(C[u]+C[v])/2+PARAMS['beta']*(D[u]-D[v]).square()/2+PARAMS['gamma']*j.square()/2
        require(E.lo>=0,'physical exponent nonnegative')
        g=(-E).exp_nonpositive();require(g.lo>M*GRID,'physical floor inactive and W invariant')
        out.append(g)
    return tuple(out)


def geometry_envelope(graph,radius):
    m=len(GRAPHS[graph][1])
    # This entrywise box is a conservative SUPERSET of the proven F-ball.
    return tuple(tuple(I(int(i==j))+span(-radius,radius) for j in range(m)) for i in range(m))


def read_envelope(graph,C,W,radius):
    n,edges,_=GRAPHS[graph];B=p.incidence(n,edges);BT=tuple(zip(*B));HH=geometry_envelope(graph,radius)
    diff=p.mv(BT,C)
    lap=p.mv(B,tuple(w*d for w,d in zip(W,diff)))
    inc=tuple(tuple(v-int(i==j) for j,v in enumerate(row)) for i,row in enumerate(HH))
    geo=p.mv(B,p.mv(inc,diff))
    pot=tuple(PARAMS['a']*c+PARAMS['nu']*c.square()/2 for c in C)
    phi=tuple(l-v+PARAMS['kah']*g for l,v,g in zip(lap,pot,geo))
    b=tuple(-w*d for w,d in zip(W,p.mv(BT,phi)))
    D=descriptor(graph,C);g=drive(graph,C,D,b)
    q=tuple((w-v)/(w+v) for w,v in zip(W,g))
    denom=tuple(1-PARAMS['chi']*v for v in q)
    require(all(x.lo>0 for x in denom),'regular current block')
    J=tuple(v/d for v,d in zip(b,denom))
    rb=tuple(PARAMS['chi']*v*j for v,j in zip(q,J))
    flat=p.solve(HH,rb);S=p.star(flat,B)
    return dict(current=J,baseline=b,q=q,readback=rb,flat=flat,source=S,descriptor=D)


def one_envelope(graph,C,W,radius):
    rd=read_envelope(graph,C,W,radius);B=p.incidence(GRAPHS[graph][0],GRAPHS[graph][1])
    newC=tuple(c-H*v for c,v in zip(C,p.mv(B,rd['current'])))
    require(all(v.lo>0 for v in newC),'positive envelope resource step')
    D=descriptor(graph,newC);g=drive(graph,newC,D,rd['current']);d=decay(H)
    newW=tuple((d*log_nonpositive(w)+(1-d)*log_nonpositive(v)).exp_nonpositive() for w,v in zip(W,g))
    require(all(M*GRID<=v.lo<=v.hi<=GRID for v in newW),'history envelope admitted')
    return newC,newW,rd


def paired_source(x,y,u,v):
    C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,)
    require(sum(C)==9 and C[0]==C[1] and C[2]==C[3],'exact source charge and pairing')
    return tuple(map(I,C)),tuple(map(I,(u,u,v,v)))


def anchor_envelope(radius):
    eps=F(1,2**30);x0=3-H;y0=F(1,2**24);w=F(99,100)
    C,W=paired_source(x0,y0,w-eps,w+eps)
    postC,postW,used=one_envelope('source',C,W,radius)
    x=postC[4]-(postC[0]+postC[2])/2;y=(postC[0]-postC[2])/2
    require(x0<3 and x.lo>3*GRID and x.hi<F(7,2)*GRID,'inactive to active x for entire section ball')
    require(y.lo>0 and y.hi<F(1,50)*GRID,'event y')
    require(postW[0].hi<postW[2].lo,'exact paired sectors remain strictly ordered')
    # Lagged invariance gives a tighter EVENT geometry bound than the
    # global section envelope: Gamma(post)-I = KH*S(pre,Gamma(pre)).
    fresh_radius=KH*F(p.norm2(used['flat']).hi,GRID)
    require(0<fresh_radius<radius,'lagged event geometry bound')
    require(all(v.hi<0 for v in used['flat']),'nonzero same-sign source flat')
    require(all((c-postC[4]).hi<0 for c in postC[:4]),'nonzero source incidence difference')
    fresh=read_envelope('source',postC,postW,fresh_radius)
    ju=fresh['current'][0]+fresh['current'][1];jv=fresh['current'][2]+fresh['current'][3]
    require(ju.lo>0 and jv.lo>0,'positive source sector inflows')
    raw=65536*ju/(ju+jv)
    require(raw.lo>F(65535,2)*GRID and raw.hi<F(65537,2)*GRID,'unique central round-even cell')
    k=32768
    # RG invariance turns the nonzero generated source into nonneutral event H.
    require(used['source'][0][0].lo>0,'active source geometry at poststate by invariance')
    rc,rw=paired_source(F(13,4),-F(1,100),F(97,100),F(99,100))
    roles={}
    for label,cc,ww in (('current',postC,postW),('reset',rc,rw)):
        targetC=cc[:4]+(cc[4]/2,cc[4]/2);targetW=ww+(I(1),)
        X2=p.norm2(tuple(c-F(3,2) for c in targetC))
        require(X2.hi<F(9,4)*GRID,'both-role target domain by conservative interval')
        nxtC,nxtW,rd=one_envelope('target',targetC,targetW,radius)
        require(rd['source'][0][0].lo>0,'active target section at following state by invariance')
        roles[label]=dict(target_X_squared=X2,minimum_C=min(F(x.lo,GRID) for x in targetC),
                          target_readback=rd['readback'],nonzero_target_S_diagonal=rd['source'][0][0],
                          source_selected_share=F(1,2),old_W_lineage=True,bridge_W=1)
    return dict(kind='uniform interval implication for unknown exact invariant-section values, not an RG numerical trajectory',
        prestate=dict(x=x0,y=y0,u=w-eps,v=w+eps),post_x=x,post_y=y,post_W=postW,
        event_geometry_radius=fresh_radius,raw_dyadic_index=raw,k=k,source_S00_lower=F(used['source'][0][0].lo,GRID),
        event_H00_minus_one_lower=KH*F(used['source'][0][0].lo,GRID),
        roles=roles,section_evaluations=0,CI_roots=0,OS_passes=0,PC_carriers=0)


def run():
    T=completion_certificate()
    A=fixed_geometry_bounds()
    envelope=anchor_envelope(T['section_value_bound'])
    record=enc(dict(schema='rgatc_ta_theory_certificate_v1',status='proposed_theorems_with_local_exact_checks_not_independently_reviewed',
        T=T,A=A,profile=PARAMS,anchor=envelope,
        qualifications=dict(new_research_completion=True,analytic_auxiliary_negative_C=True,
          negative_physical_resources_admitted=False,old_request_interval_reused=False,
          native_admission=False,native_RG_step_executed=False,section_solver_implemented=False,
          source_debt_discharge=False,aggregate_ATC2_closed=False),
        source_files=[dict(name=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                      for path in (Path(__file__).resolve(),ROOT/'deps/retained/arithmetic/certify_atc_sector_readback_point.py')]))
    record['record_digest']=digest(record)
    return record

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
