#!/usr/bin/env python3
"""G1--G4 research certificates; exact rationals/outward intervals, no src writes.

Analytic state-domain bounds precede the embedded finite-domain proof. The
retained point/box kernels are imported unchanged. Prints JSON, never files.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import certify_atc_sector_readback_box as rb

p, I, GRID = rb.point, rb.I, rb.GRID
A, H, M, RREAD = F(19, 4), F(1, 8), F(24, 25), F(1, 783)
THETA = dict(chi=rb.span('1/32', '1/16'),
             gamma=rb.span('1/2048', '1/1024'),
             kh=rb.span('1/2', '1'), kah=rb.span('1/2', '1'))
ESOURCE = ((0, 4), (1, 4), (2, 4), (3, 4), (0, 5), (1, 6))
ETARGET = ((0, 4), (1, 4), (2, 5), (3, 5), (4, 5), (0, 6), (1, 7))
T = ((3, 2, 1), (2, 3, 0), (1, 0, 2))


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def mv(m, v):
    return tuple(sum((a*b for a, b in zip(row, v, strict=True)), F()) for row in m)


def mm(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(row, col, strict=True))
                       for col in zip(*b)) for row in a)


def source_cone():
    """G2: positive paired C, Q=9, x>=3, W in [24/25,1]."""
    baseline = F(11, 2)
    delta = F(225, 2)*(RREAD*baseline)**2
    fresh_baseline = baseline+delta
    selected = (1+RREAD)*fresh_baseline
    # Every reference/fresh target and writer target exceeds M; q<=1/49.
    target_lower = 1-selected**2/2048
    require(target_lower > M, 'source history interval invariant')
    error = delta+RREAD*fresh_baseline
    # Sum of bare baselines >= (19/250)x; x>=3 absorbs absolute error.
    growth = F(5, 16)*(F(19, 250)-2*error/3)
    residual = 4*((RREAD*baseline)**2+(RREAD*fresh_baseline)**2)
    require(growth > F(1, 50), 'uniform source contrast growth')
    require(residual < F(1, 512), 'uniform source OS admission')
    require(3*F(51, 50)**56 > 9, 'finite positive continuation impossible')
    return dict(baseline_bound=baseline, geometry_correction_bound=delta,
                selected_current_bound=selected, writer_lower=target_lower,
                OS_residual_upper=residual, relative_growth_lower=growth,
                certified_multiplier=F(51, 50), nonpositive_attempt_at_most=56,
                history_reset_only_also_in_cone=True)


def domain_entry():
    """G1: analytic target entry for a full-dimensional source/reset domain."""
    # Source baseline balance |bu-bv| <= (bu+bv)/64 and |chi*q| <= 1/784.
    rlo = F(63, 128)*F(783, 785)
    rhi = F(65, 128)*F(785, 783)
    halfbin = F(1, 131072)
    require(rlo-halfbin > F(31, 64) and rhi+halfbin < F(33, 64),
            'every rounded source outcome lies in declared share domain')
    # t=(2x-3)/10, e=(share-1/2)s; x in [3,7/2], |y|<=1/50.
    t, y, e = F(2, 5), F(1, 50), F(23, 320)
    # D=v-u may have either sign for reset, |D|<=1/25.
    # w(a-3w) in [7/4,1122/625], throughout w in [24/25,1].
    amin = F(7, 4)
    leaf = F(11, 32)*t+F(25, 32)*y+e/32
    parent = (2-F(3, 4)*(amin-F(1, 25)))*t
    parent += F(1, 4)*(2-amin)*y
    parent += F(7, 8)*e
    linear_X2 = 4*leaf**2+2*parent**2
    X2 = 12*t*t+4*y*y+2*e*e
    require(X2 < F(9, 4), 'initial target X<=3/2')
    base = F(6)  # ||b0|| <=4X.
    delta = F(125, 8)*F(3, 2)*(RREAD*base)**2
    jbound = (1+RREAD)*(base+delta)
    require(1-jbound*jbound/2048 > M, 'target read/writer contrast bound')
    correction = F(5, 16)*(delta+RREAD*(base+delta))
    require(linear_X2 < F(3, 5)**2, 'polynomial entry bound')
    require(F(3, 5)+correction < F(2, 3), 'both-role return radius')
    residual = (RREAD*base)**2+(RREAD*(base+delta))**2
    require(residual < F(1, 512), 'both-role entry OS residual')
    funding = F(31, 64)*F(21, 5)-F(61, 50)
    require(funding > 0, 'both-role positive funding')
    # Strict interior witness, not the definition or proof of the domain.
    x0,y0,u0,v0 = F(13,4),F(1,100),F(97,100),F(99,100)
    bu=u0*((3*u0+2*v0-A)*x0+(-3*u0+2*v0+A)*y0)
    bv=v0*((2*u0+3*v0-A)*x0+(-2*u0+3*v0-A)*y0)
    require(bu>0 and bv>0 and abs(bu-bv)<(bu+bv)/64,
            'nonempty full-dimensional event domain')
    return dict(unrounded_share_enclosure=[rlo,rhi],
                rounded_share_enclosure=[F(31,64),F(33,64)],
                funding_lower=funding, initial_X_squared_upper=X2,
                linear_first_X_squared_upper=linear_X2,
                nonlinear_first_X_error_upper=correction,
                first_X_upper=F(3,5)+correction, OS_residual_upper=residual,
                strict_interior_witness=[x0,y0,u0,v0],
                actual_reset_independent=True, arbitrary_reset_guarantee=False)


def polynomial_checks():
    """Exact matrix checks of G1 and G4 cancellation-preserving formulas."""
    count = 0
    for x,y,u,v,share in ((F(13,4),F(1,100),F(97,100),F(99,100),F(31,64)),
                         (F(3),-F(1,50),F(1),M,F(33,64)),
                         (F(7,2),F(1,50),M,F(1),F(1,2))):
        B=p.incidence(6,p.TARGET); W=(u,u,v,v,F(1));
        C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+(share*(9+4*x)/5,(1-share)*(9+4*x)/5)
        L=mm(tuple(tuple(b*w for b,w in zip(row,W)) for row in B),tuple(zip(*B)))
        lc=mv(L,C); linear=tuple(c-H*z for c,z in zip(C,mv(L,tuple(A*c-l for c,l in zip(C,lc)))))
        t=(2*x-3)/10; e=(share-F(1,2))*(9+4*x)/5
        au=u*(A-3*u); av=v*(A-3*v); d=v-u; s=u+v
        f1=t*(-1+3*H*au)+y*(1-H*au)+e*H*(au-2*u)
        f2=t*(-1+3*H*av)-y*(1-H*av)-e*H*(av-2*v)
        g1=t*(2-6*H*(au+d))+2*H*(au-s)*y+(1+2*H*(2*u-au-A+2+s))*e
        g2=t*(2-6*H*(av-d))+2*H*(s-av)*y-(1+2*H*(2*v-av-A+2+s))*e
        require(linear==tuple(F(3,2)+z for z in (f1,f1,f2,f2,g1,g2)), 'target polynomial identity')
        count += 1
    for C,W,f in (((1,1,1,1,2,1,1),(F(99,100),)*2+(F(1),)*4,(F(1,100),F(1,80),-F(1,60))),
                  ((2,2,1,1,3,4,4),(M,M,1,1,F(49,50),F(49,50)),(F(1,20),-F(1,70),F(1,30)))):
        B=p.incidence(7,ESOURCE); BT=tuple(zip(*B)); d=mv(BT,C)
        Lc=mv(B,tuple(w*z for w,z in zip(W,d)))
        bare=tuple(w*z for w,z in zip(W,mv(BT,tuple(A*c-l for c,l in zip(C,Lc)))))
        u,v,w=W[0],W[2],W[4]; du,dv,de=d[0],d[2],d[4]
        reduced=(u*((A-3*u)*du-2*v*dv-w*de),v*(-2*u*du+(A-3*v)*dv),w*(-u*du+(A-2*w)*de))
        require(bare==tuple(z for z in reduced for _ in range(2)), 'embedded baseline quotient')
        fu,fv,fe=f; full=tuple(z for z in f for _ in range(2))
        S=tuple(tuple(F(sum(bool(row[i] and row[j]) for row in B),2)*full[i]*full[j] for j in range(6)) for i in range(6))
        sr=(F(3,2)*fu*fu*du+fu*fv*dv+fu*fe*de/2,
            fu*fv*du+F(3,2)*fv*fv*dv,fu*fe*du/2+fe*fe*de)
        require(mv(S,d)==tuple(z for z in sr for _ in range(2)), 'embedded star quotient')
        Cn=tuple(c-H*z for c,z in zip(C,mv(B,bare)))
        dn=mv(BT,Cn)
        require(dn==tuple(z for z in tuple(a-H*b for a,b in zip((du,dv,de),mv(T,reduced))) for _ in range(2)),
                'embedded continuity quotient')
        count += 1
    return dict(exact_matrix_comparisons=count)


def positive_pivots(matrix):
    a=[list(map(F,row)) for row in matrix]; pivots=[]
    for k in range(len(a)):
        pivot=a[k][k]; require(pivot>0,'rational positive-definite certificate')
        pivots.append(pivot)
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                a[i][j]-=a[i][k]*a[k][j]/pivot
    return pivots


def embedded_return():
    B=p.incidence(8,ETARGET); L=mm(B,tuple(zip(*B)))
    # Columns e_i-e_7 span the entire mean-zero space, not just paired modes.
    Q=tuple(tuple(F(int(i==j)-int(i==7)) for j in range(7)) for i in range(8))
    QT=tuple(zip(*Q)); G=mm(QT,Q); K=mm(mm(QT,L),Q)
    low,high=F(3,10),F(47,10)
    lp=positive_pivots(tuple(tuple(k-low*g for k,g in zip(row,grow)) for row,grow in zip(K,G)))
    up=positive_pivots(tuple(tuple(high*g-k for k,g in zip(row,grow)) for row,grow in zip(K,G)))
    lo=M*low
    q0=max(1+H*lo*(lo-A),1+H*high*(high-A))
    require(q0==F(1553,1600),'embedded linear contraction')
    R=F(1,4); base=4*R
    delta_per_X=F(125,8)*(4*RREAD*R)**2
    read_error_per_X=delta_per_X+RREAD*(4+delta_per_X)
    q=q0+F(5,16)*read_error_per_X
    require(q<F(49,50),'embedded nonlinear contraction')
    jbound=R*(4+delta_per_X)*(1+RREAD)
    require(1-jbound*jbound/2048>M,'embedded history invariant')
    residual=(RREAD*base)**2+(RREAD*(4+delta_per_X)*R)**2
    require(residual<F(1,512),'embedded OS residual')
    return dict(nonzero_spectrum=[low,high], lower_pivots=lp,upper_pivots=up,
                weighted_spectrum=[lo,high], X_radius=R, W_lower=M,
                q0=q0, nonlinear_q_upper=q, certified_q=F(49,50),
                resource_floor=F(41,40)-R, OS_residual_upper=residual,
                full_mean_zero_space=True, history_limit=1)


def embedded_read(d,W):
    du,dv,de=d;u,v,w=W
    bare=(u*((A-3*u)*du-2*v*dv-w*de),
          v*(-2*u*du+(A-3*v)*dv),w*(-u*du+(A-2*w)*de))
    blocks=tuple(rb.read(b,z,THETA) for b,z in zip(bare,W))
    ref=tuple(z[0] for z in blocks);fu,fv,fe=(z[1] for z in blocks)
    star=(F(3,2)*fu.square()*du+fu*fv*dv+fu*fe*de/2,
          fu*fv*du+F(3,2)*fv.square()*dv,fu*fe*du/2+fe.square()*de)
    delta=tuple(-THETA['kh']*THETA['kah']*w*s for w,s in zip(W,mv(T,star)))
    fresh=tuple(rb.read(b+db,w,THETA) for b,db,w in zip(bare,delta,W))
    J=tuple(z[0] for z in fresh)
    err=tuple(db+z[1] for db,z in zip(delta,fresh))
    residual=2*THETA['kh']*(sum((z[1].square() for z in blocks),I(0))+sum((z[1].square() for z in fresh),I(0)))
    require(residual.hi<GRID*F(1,512),'embedded source OS residual')
    return dict(reference=ref, fresh=J, error=err, residual=residual)


def embedded_resources(d):
    du,dv,de=d; s=(F(41,5)-4*du-2*dv+2*de)/7
    return (s+du,s+du,s+dv,s+dv,s,s+du-de,s+du-de)


def embedded_step(d,W):
    read=embedded_read(d,W)
    TW=tuple(tuple(t*w for t,w in zip(row,W)) for row in T)
    TW2=mm(TW,TW)
    P=tuple(tuple(int(i==j)-H*A*TW[i][j]+H*TW2[i][j] for j in range(3)) for i in range(3))
    dn=tuple(z-H*e for z,e in zip(mv(P,d),mv(T,read['error'])))
    Cn=embedded_resources(dn)
    row=dict(minimum_C=p.minimum(Cn),OS_residual_upper=read['residual'])
    if row['minimum_C'].hi<0:
        return dn,None,row  # Rejected resource proposal: no history write.
    require(row['minimum_C'].lo>0,'embedded interval cannot certify resource sign')
    drives=tuple((-THETA['gamma']*j.square()/2).exp_nonpositive() for j in read['fresh'])
    require(all(d.lo>GRID//2 for d in drives),'embedded writer floor inactive')
    wn=tuple((w*drive).sqrt() for w,drive in zip(W,drives))
    require(all(w.lo>GRID//2 and w.hi<=GRID for w in wn),'embedded history/floor')
    return dn,wn,row


def embedded_domain():
    # A source domain, not a prepared ordinary trajectory. All coordinates
    # below vary independently except charge and structural pairing.
    eps=F(1,10000)
    r=rb.span(1-eps,1+eps); z=rb.span(1-eps,1+eps)
    s=rb.span(F(11,5)-6*eps,F(11,5)+6*eps)
    d=(r-s,r-s,r-z)
    W=(rb.span(F(99,100)-eps,F(99,100)+eps),rb.span(1-eps,1),rb.span(1-eps,1))
    read=embedded_read(d,W);ju,jv,je=read['reference']
    require(ju.lo>0 and jv.lo>0 and je.lo>0,'genuine selected inflow and external activity')
    share=I(1)/(1+jv/ju)  # Monotone ratio, avoiding repeated-ju wrapping.
    require(F(share.lo,GRID)-F(1,131072)>F(12,25) and F(share.hi,GRID)+F(1,131072)<F(13,25),'embedded prescribed share range')
    # Every actual reset independently belongs to the same source-coordinate
    # box; it need not generate the current role's share or have the same W.
    child_error=F(13,25)*(F(11,5)+6*eps)-F(41,40)
    leaf_error=F(1,40)+eps
    entry_X2=6*leaf_error**2+2*child_error**2
    require(entry_X2<F(1,16),'embedded both-role direct entry')
    funding=F(12,25)*(F(11,5)-6*eps)-(1+eps)
    require(funding>0,'embedded funding')
    controls={}
    for name,initial_W in (('no_split',W),('history_reset_only',(I(1),)*3)):
        dn,wn=d,initial_W;rows=[]
        for attempt in range(1,13):
            dn,wn,row=embedded_step(dn,wn);rows.append(dict(attempt=attempt,**row))
            if row['minimum_C'].hi<0:
                break
            require(row['minimum_C'].lo>0,'embedded interval cannot certify resource sign')
        require(rows[-1]['minimum_C'].hi<0,'embedded finite obstruction')
        controls[name]=dict(rejected_attempt=attempt,rows=rows)
    return dict(epsilon=eps,charge=F(41,5), source_edges=ESOURCE,target_edges=ETARGET,
                current_requires_ru_ge_rv=True,reset_requires_ru_ge_rv=False,
                external_reference_current=je,share_enclosure=share,
                rounded_share_hull=[F(12,25),F(13,25)],funding_lower=funding,
                both_role_entry_X_squared_upper=entry_X2,controls=controls,
                arbitrary_environment_claimed=False)


def embedding_counterexample():
    # Another unsplit parent shares all four leaves. Fission leaves enough
    # untouched obstruction to defeat a return claim, even at equilibrium.
    edges=((0,4),(1,4),(2,5),(3,5),(4,5),(0,6),(1,6),(2,6),(3,6))
    B=p.incidence(7,edges); v=(-1,-1,-1,-1,0,0,4)
    R=sum(z*z for z in mv(tuple(zip(*B)),v))/F(sum(z*z for z in v))
    require(sum(v)==0 and R==F(26,5) and R>A,'unaffected environmental obstruction')
    return dict(target_rayleigh=R, slope=A,return_impossible_near_uniform=True)


def evidence():
    return dict(G1=domain_entry(), G2=source_cone(), algebra=polynomial_checks(),
                G3='exact decorated automorphism/orbit theorem in companion note; not arbitrary equitable pooling',
                G4=dict(return_theorem=embedded_return(), domain=embedded_domain(),
                        excluded_environment=embedding_counterexample()))


def main():
    base=p.ROOT/p.INV
    predecessor=json.loads((base/'evidence/autonomous-topology-change/ATCSectorReadBackBoxAdjudication.json').read_text())
    body=dict(predecessor);digest=body.pop('record_digest')
    require(hashlib.sha256(p.canonical(body)).hexdigest()==digest,
            'accepted box adjudication digest')
    require(predecessor['scientific_acceptance'] and
            predecessor['accepted_scope']['whole_box_source_and_entry_accepted'],
            'box acceptance prerequisite')
    for binding in predecessor['source_bindings']:
        require(hashlib.sha256((p.ROOT/binding['path']).read_bytes()).hexdigest()==binding['sha256'],
                'reviewed predecessor content binding: '+binding['path'])
    result=evidence()
    record=dict(schema='grcv4_atc_state_domain_certificate_v1',
                status='G1_G4_mathematical_results_pending_review',
                interval_encoding='outward integer endpoints divided by 2**256',
                accepted=False,graph_admission=False,native_authority=False,
                ATC2_closed=False,G5_G7_completed=False,evidence=p.encode(result),
                source_bindings=[])
    for path in (Path(__file__).resolve(),base/'scripts/certify_atc_sector_readback_box.py',
                 base/'scripts/certify_atc_sector_readback_point.py',
                 base/'evidence/autonomous-topology-change/ATCSectorReadBackBoxAdjudication.json',
                 base/'decisions/ATCSectorStateDomain.md'):
        record['source_bindings'].append(dict(path=str(path.relative_to(p.ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    record['record_digest']=hashlib.sha256(p.canonical(record)).hexdigest()
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
