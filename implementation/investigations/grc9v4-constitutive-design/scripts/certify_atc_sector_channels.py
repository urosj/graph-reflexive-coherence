#!/usr/bin/env python3
"""G5 channels/potential and G6 request-domain research, never native ATC.

Exact rational bounds plus the immutable reviewed outward interval kernel.
Only prints a certificate; does not write files or alter production profiles.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import certify_atc_sector_state_domain as prior

p, rb = prior.p, prior.rb
I, GRID = p.I, p.GRID
A, M, RREAD = F(19,4), F(24,25), F(1,783)
K = F(1,2048)  # |p'(c)-19/4| on [0,9], common site law.
ALPHA_MAX = BETA_MAX = F(1,2048)
ALPHA_MIN = BETA_MIN = F(1,4096)
THETA = dict(prior.THETA, alpha=rb.span(ALPHA_MIN,ALPHA_MAX),
             beta=rb.span(BETA_MIN,BETA_MAX))
GRAPHS = {
    'paired_source': (5,p.SOURCE,(1,1,1,1,0)),
    'paired_target': (6,p.TARGET,(1,1,1,1,0,0)),
    'embedded_source': (7,prior.ESOURCE,(1,1,1,1,0,2,2)),
    'embedded_target': (8,prior.ETARGET,(1,1,1,1,0,0,2,2)),
}
require = prior.require


def wls_matrix(n, edges, positions):
    """Unit weights, dimension one, ridge one; exact native WLS formula."""
    rows=[]
    for i in range(n):
        row=[F(0)]*n; denominator=F(1)
        for u,v in edges:
            if i not in (u,v):
                continue
            j=v if i==u else u
            dx=F(positions[j]-positions[i]);denominator+=dx*dx
            row[j]+=dx;row[i]-=dx
        rows.append(tuple(c/denominator for c in row))
    return tuple(rows)


def descriptor_checks():
    rows={}
    for name,(n,edges,positions) in GRAPHS.items():
        D=wls_matrix(n,edges,positions)
        require(all(sum(row)==0 for row in D),'descriptor annihilates constants')
        contrasts=tuple(tuple(a-b for a,b in zip(D[u],D[v])) for u,v in edges)
        norms=[sum(c*c for c in row) for row in contrasts]
        require(max(norms)<=4,'edge descriptor contrast <=2X')
        # Decorated pair swaps, including corresponding environment vertices.
        perms=[list(range(n)),list(range(n))]
        perms[0][0],perms[0][1]=1,0;perms[1][2],perms[1][3]=3,2
        if name=='embedded_source':perms[0][5],perms[0][6]=6,5
        if name=='embedded_target':perms[0][6],perms[0][7]=7,6
        for perm in perms:
            require(all(positions[perm[i]]==positions[i] for i in range(n)), 'host symmetry')
            require(all(D[perm[i]][perm[j]]==D[i][j] for i in range(n) for j in range(n)), 'descriptor equivariance')
        rows[name]=dict(positions=positions,dimension=1,ridge=1,reference_weights=1,
                       matrix=D,edge_contrast_squared_norm_max=max(norms),
                       exact_pair_covariance=True)
    return rows


def algebra_checks():
    """Full-space spectral certificates and symbolic linear descriptor checks."""
    spectra={}
    for name,lo,hi in (('paired_target',F(7,16),F(73,16)),
                       ('embedded_target',F(3,10),F(47,10))):
        n,edges,_=GRAPHS[name];B=p.incidence(n,edges)
        L=prior.mm(B,tuple(zip(*B)))
        Q=tuple(tuple(F(int(i==j)-int(i==n-1)) for j in range(n-1)) for i in range(n))
        QT=tuple(zip(*Q));G=prior.mm(QT,Q);Lr=prior.mm(prior.mm(QT,L),Q)
        lower=prior.positive_pivots(tuple(tuple(k-lo*g for k,g in zip(row,gr)) for row,gr in zip(Lr,G)))
        upper=prior.positive_pivots(tuple(tuple(hi*g-k for k,g in zip(row,gr)) for row,gr in zip(Lr,G)))
        spectra[name]=dict(unweighted_nonzero_spectrum=[lo,hi],
                           lower_pivots=lower,upper_pivots=upper,full_mean_zero_space=True)
    # Check linear identities on a basis, not merely a sampled trajectory.
    D=wls_matrix(*GRAPHS['embedded_source'])
    for d in ((0,0,0),(1,0,0),(0,1,0),(0,0,1)):
        full=prior.mv(D,prior.embedded_resources(tuple(map(F,d))))
        du,dv,ds,dz=embedded_descriptor(tuple(map(F,d)))
        require(full==(du,du,dv,dv,ds,dz,dz),'embedded WLS quotient identity')
    Dp=wls_matrix(*GRAPHS['paired_source'])
    for x,y in ((F(0),F(0)),(F(1),F(0)),(F(0),F(1))):
        C=((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,)
        d=prior.mv(Dp,C)
        require(d[0]-d[4]==3*x/10+y/2 and d[2]-d[4]==3*x/10-y/2,
                'paired WLS edge-contrast identity')
    # Positive charge-preserving post-state: stale source descriptors must
    # not be interchangeable with the writer's rebuilt post-state operand.
    before=(F(1),)*4+(F(11,5),F(1),F(1))
    after=(F(99,100),)*2+(F(1),)*2+(F(111,50),F(1),F(1))
    old,new=prior.mv(D,before),prior.mv(D,after)
    require(sum(before)==sum(after) and (old[0]-old[4])**2!=(new[0]-new[4])**2,
            'stale writer descriptor is discriminated')
    return dict(target_spectra=spectra,exact_descriptor_reductions=True,
                writer_stage_pressure=dict(old_contrast_squared=(old[0]-old[4])**2,
                    rebuilt_contrast_squared=(new[0]-new[4])**2,interchangeable=False))


def analytic_bounds(hmin,hmax):
    require(0<hmin<=hmax<=F(1,8),'request domain')
    B=F(11,2);delta=F(225,2)*(RREAD*B)**2
    require(F(2697,500)+9*K < B,'source perturbed baseline bound')
    current=(1+RREAD)*(B+delta)
    source_budget=ALPHA_MAX*F(9,2)+BETA_MAX*F(27,10)**2/2+current**2/2048
    require(1-source_budget>M,'source read and post-resource writer invariant')
    error=delta+RREAD*(B+delta)
    growth=F(5,2)*hmin*(F(19,250)-6*K-2*error/3)
    multiplier=F(51,50) if hmin==F(1,8) else F(61,60)
    horizon=56 if hmin==F(1,8) else 67
    require(growth>multiplier-1,'full-channel source growth')
    require(3*multiplier**horizon>9,'finite source obstruction')
    source_residual=4*((RREAD*B)**2+(RREAD*(B+delta))**2)
    require(source_residual<F(1,512),'source OS admission')
    # Event E_p uses the actual p-baseline balance, not a0's surrogate current.
    witness=prior.domain_entry()['strict_interior_witness'];x,y,u,v=witness
    bu=u*((3*u+2*v-A)*x+(-3*u+2*v+A)*y)
    bv=v*((2*u+3*v-A)*x+(-2*u+3*v-A)*y)
    require(min(bu,bv)>9*K and abs(bu-bv)+18*K<(bu+bv-18*K)/64,
            'common strict interior for every admitted potential')
    # Polynomial target entry at a0, remainder handles the potential class.
    t,yy,e=F(2,5),F(1,50),F(23,320)
    leaf=(1-3*hmin*F(7,4))*t+(1-hmin*F(7,4))*yy+hmax*e/4
    parent=(2-6*hmin*(F(7,4)-F(1,25)))*t+hmax*yy/2+(1-hmin)*e
    lin2=4*leaf*leaf+2*parent*parent
    lin=F(3,5) if hmin==F(1,8) else F(5,8)
    require(lin2<lin*lin,'both-role polynomial entry')
    effective=4+F(5,2)*K
    X=F(3,2);base=effective*X;dg=F(125,8)*X*(RREAD*base)**2
    correction=hmax*F(5,2)*(F(5,2)*K*X+dg+RREAD*(base+dg))
    entry=lin+correction
    require(entry<F(2,3),'both-role full-channel entry')
    j=(1+RREAD)*(base+dg)
    entry_budget=ALPHA_MAX*(F(3,2)+X)+2*BETA_MAX*X*X+j*j/2048
    require(1-entry_budget>M,'entry read/writer history interval')
    entry_residual=(RREAD*base)**2+(RREAD*(base+dg))**2
    require(entry_residual<F(1,512),'entry OS admission')
    returns={}
    for name,lo,hi,R,c,limit in (
        ('paired',M*F(7,16),F(73,16),F(2,3),F(3,2),F(9,10)),
        ('embedded',M*F(3,10),F(47,10),F(1,4),F(41,40),F(49,50))):
        # P(lambda) is positive on the whole spectral interval; its maximum
        # is at an endpoint, and the worst step for contraction is hmin.
        require(1-hmax*A*A/4>0,'positive bare spectral multiplier')
        q0=max(1+hmin*lo*(lo-A),1+hmin*hi*(hi-A))
        dg_per_X=F(125,8)*(RREAD*effective*R)**2
        correction_per_X=hmax*F(5,2)*(F(5,2)*K+dg_per_X+RREAD*(effective+dg_per_X))
        q=q0+correction_per_X
        require(q<limit,'full-channel uniform target contraction '+name)
        j=(1+RREAD)*(effective+dg_per_X)*R
        budget=ALPHA_MAX*(c+R)+2*BETA_MAX*R*R+j*j/2048
        require(1-budget>M,'return read and rebuilt writer target '+name)
        residual=(RREAD*effective*R)**2+(RREAD*(effective+dg_per_X)*R)**2
        require(residual<F(1,512),'return OS admission '+name)
        require(1-ALPHA_MAX*c>M,'shifted equilibrium inside history interval')
        returns[name]=dict(q0=q0,q_upper=q,certified_q=limit,R=R,c=c,
                          resource_floor=c-R,exponent_budget=budget,
                          OS_residual_upper=residual,W_limit='exp(-alpha*c)')
    require(M*F(26,5)>A+K,'second-parent obstruction persists at shifted equilibrium')
    # Concrete nonlinear subclass, not just an affine relabelling.
    require(F(1,4096)+9*F(1,65536)<K,'nonlinear quadratic subclass slope bound')
    return dict(h=[hmin,hmax],source_growth_lower=growth,source_multiplier=multiplier,
                source_failure_by=horizon,source_exponent_budget=source_budget,
                source_OS_residual_upper=source_residual,
                entry_linear_X_squared_upper=lin2,entry_X_upper=entry,
                entry_exponent_budget=entry_budget,entry_OS_residual_upper=entry_residual,
                returns=returns,common_event_interior=witness,
                alpha_source_exponent_lower=ALPHA_MIN*F(269,100),
                beta_source_exponent_lower=BETA_MIN*F(89,100)**2/2,
                second_parent_weighted_rayleigh_lower=M*F(26,5))


def log_nonpositive(w):
    """Outward log on [1/2,1], via -2 atanh((1-w)/(1+w))."""
    require(GRID//2<=w.lo<=w.hi<=GRID,'log interval domain')
    z=(1-w)/(1+w);z2=z.square();term=z;total=I(0)
    for k in range(96):
        total+=term/(2*k+1);term=term*z2
    tail=F(1,3)**193/(193*(1-F(1,9)))
    return -2*(total+I.bounds(0,I(tail).hi))


def decay(h):
    # tau remains 1/(8 log 2); h changes, tau does not.
    log2=-log_nonpositive(I(F(1,2)))
    return (-8*h*log2).exp_nonpositive()


def kernel_checks():
    rows=[]
    for w in (F(1,2),M,F(99,100),F(1)):
        lw=log_nonpositive(I(w));roundtrip=lw.exp_nonpositive()
        require(roundtrip.contains(w),'log/exp rational roundtrip')
        rows.append(dict(w=w,log=lw,roundtrip_contains_input=True))
    half=decay(I(F(1,8)));require(half.contains(F(1,2)),'original half writer')
    lower_step=decay(I(F(3,25)));require(lower_step.lo>GRID//2,'changed step not square-root writer')
    # rho <= 25/37 follows log(2)>1/2 and exp(t)>=1+t.
    require(lower_step.hi<GRID*F(25,37),'uniform variable-request writer decay')
    return dict(log_probes=rows,h0_decay=half,hmin_decay=lower_step,
                rho_upper=F(25,37),log_terms=96)


def abstract_p_delta(d,w):
    bound=max(abs(d.lo),abs(d.hi))
    return w*I.bounds(-bound,bound)*K


def embedded_descriptor(d):
    du,dv,de=d
    return ((du-de)/3,dv/2,2*(du+dv)/5,-de/2)  # u,v,parent,external


def edge_operands(C,d):
    du,dv,ds,dz=embedded_descriptor(d)
    return ((C[0]+C[4])/2,(C[2]+C[4])/2,(C[0]+C[5])/2),((du-ds).square(),(dv-ds).square(),(du-dz).square())


def target_exponent(avg,contrast,b):
    return THETA['alpha']*avg+THETA['beta']*contrast/2+THETA['gamma']*b.square()/2


def read(b,w,avg,contrast):
    exponent=target_exponent(avg,contrast,b)
    require(exponent.lo>=0,'nonnegative conductance exponent')
    target=(-exponent).exp_nonpositive()
    require(target.lo>GRID//2,'read floor inactive')
    q=(w-target)/(w+target);den=1-THETA['chi']*q
    require(den.lo>0,'read denominator')
    j=b/den
    return j,THETA['chi']*q*j


def embedded_read(d,W):
    du,dv,de=d;u,v,w=W
    C=prior.embedded_resources(d);avg,contrast=edge_operands(C,d)
    bare=(u*((A-3*u)*du-2*v*dv-w*de),v*(-2*u*du+(A-3*v)*dv),w*(-u*du+(A-2*w)*de))
    dp=tuple(abstract_p_delta(di,wi) for di,wi in zip(d,W))
    blocks=tuple(read(b+e,wi,a,c) for b,e,wi,a,c in zip(bare,dp,W,avg,contrast))
    ref=tuple(z[0] for z in blocks);fu,fv,fe=(z[1] for z in blocks)
    star=(F(3,2)*fu.square()*du+fu*fv*dv+fu*fe*de/2,
          fu*fv*du+F(3,2)*fv.square()*dv,fu*fe*du/2+fe.square()*de)
    dg=tuple(-THETA['kh']*THETA['kah']*wi*s for wi,s in zip(W,prior.mv(prior.T,star)))
    fresh=tuple(read(b+e+g,wi,a,c) for b,e,g,wi,a,c in zip(bare,dp,dg,W,avg,contrast))
    error=tuple(e+g+z[1] for e,g,z in zip(dp,dg,fresh))
    residual=2*THETA['kh']*(sum((z[1].square() for z in blocks),I(0))+sum((z[1].square() for z in fresh),I(0)))
    require(residual.hi<GRID*F(1,512),'embedded OS admission')
    return dict(reference=ref,fresh=tuple(z[0] for z in fresh),error=error,
                residual=residual,alpha_exponents=tuple(THETA['alpha']*a for a in avg),
                beta_exponents=tuple(THETA['beta']*c/2 for c in contrast))


def intersection(a,b):
    require(max(a.lo,b.lo)<=min(a.hi,b.hi),'nonempty survivor enclosure')
    return I.bounds(max(a.lo,b.lo),min(a.hi,b.hi))


def embedded_step(d,W,h,rho):
    rd=embedded_read(d,W)
    TW=tuple(tuple(t*w for t,w in zip(row,W)) for row in prior.T)
    TW2=prior.mm(TW,TW)
    # Group h once: I+h Q(Q-aI), not independently expanded h terms.
    P=tuple(tuple(int(i==j)+h*(TW2[i][j]-A*TW[i][j]) for j in range(3)) for i in range(3))
    dn=tuple(z-h*e for z,e in zip(prior.mv(P,d),prior.mv(prior.T,rd['error'])))
    C=prior.embedded_resources(dn);minimum=p.minimum(C)
    row=dict(minimum_C=minimum,OS_residual_upper=rd['residual'])
    if minimum.hi<0:
        return None,None,dict(row,disposition='all_survivors_reject_resources',writer_executed=False)
    # Conditional reachability enclosure: discard already rejected members.
    # This is a proof operation, not a physical clamp or a committed step.
    for i,c in enumerate(C):
        if c.lo>I(F(41,5)).hi:
            return None,None,dict(row,disposition='all_survivors_reject_resources_by_charge',
                                  writer_executed=False,over_charge_coordinate=i)
    C=tuple(I.bounds(max(0,c.lo),min(I(F(41,5)).hi,c.hi)) for c in C)
    differences=(C[0]-C[4],C[2]-C[4],C[0]-C[5])
    for i,(a,b) in enumerate(zip(dn,differences)):
        if max(a.lo,b.lo)>min(a.hi,b.hi):
            # A surviving state must satisfy both exact descriptions of d_i.
            # Disjoint intervals prove the nonnegative survivor set empty.
            return None,None,dict(row,disposition='all_survivors_reject_resources_by_empty_intersection',
                writer_executed=False,empty_intersection=dict(coordinate=i,raw=a,nonnegative_difference=b))
    dn=tuple(intersection(a,b) for a,b in zip(dn,differences))
    # Rebuild the descriptor from the admitted post-resource state. Use the
    # full WLS linear map to avoid treating source read descriptors as writer inputs.
    D=wls_matrix(*GRAPHS['embedded_source'])
    descriptors=prior.mv(D,C)
    avg=((C[0]+C[4])/2,(C[2]+C[4])/2,(C[0]+C[5])/2)
    con=((descriptors[0]-descriptors[4]).square(),(descriptors[2]-descriptors[4]).square(),(descriptors[0]-descriptors[5]).square())
    exponents=tuple(target_exponent(a,c,j) for a,c,j in zip(avg,con,rd['fresh']))
    require(all(e.lo>=0 for e in exponents),'writer exponent at surviving resources')
    drives=tuple((-e).exp_nonpositive() for e in exponents)
    require(all(t.lo>GRID//2 for t in drives),'writer floor inactive')
    wn=tuple((rho*log_nonpositive(w)-(1-rho)*e).exp_nonpositive() for w,e in zip(W,exponents))
    require(all(w.lo>=GRID//2 and w.hi<=GRID for w in wn),'history domain')
    row.update(disposition='all_admitted' if minimum.lo>0 else 'conditional_nonnegative_survivors_only',
               writer_executed='surviving_nonnegative_states_only',writer_descriptors='rebuilt_from_C_next')
    return dn,wn,row


def embedded_domain(hmin,hmax):
    eps=F(1,10000);r=rb.span(1-eps,1+eps);s=rb.span(F(11,5)-6*eps,F(11,5)+6*eps)
    d=(r-s,r-s,r-r)
    W=(rb.span(F(99,100)-eps,F(99,100)+eps),rb.span(1-eps,1),rb.span(1-eps,1))
    rd=embedded_read(d,W);ju,jv,je=rd['reference']
    require(min(j.lo for j in rd['reference'])>0,'parent inflows and active environment')
    require(all(x.lo>0 for x in rd['alpha_exponents']+rd['beta_exponents']), 'both new channels genuinely active')
    share=I(1)/(1+jv/ju);low,high=F(15,32),F(17,32)
    require(F(share.lo,GRID)-F(1,131072)>low and F(share.hi,GRID)+F(1,131072)<high,'all prescribed shares enclosed')
    funding=low*(F(11,5)-6*eps)-(1+eps)
    child_error=high*(F(11,5)+6*eps)-F(41,40)
    X2=6*(F(1,40)+eps)**2+2*child_error**2
    require(funding>0 and X2<F(1,16),'both-role direct entry, no target selection')
    h=rb.span(hmin,hmax);rho=decay(h);controls={}
    for name,initial in (('no_split',W),('history_reset_to_one_only',(I(1),)*3)):
        dn,wn=d,initial;rows=[]
        for attempt in range(1,11):
            dn,wn,row=embedded_step(dn,wn,h,rho);rows.append(dict(attempt=attempt,**row))
            if dn is None:break
        require(dn is None,'uniform embedded source failure horizon')
        controls[name]=dict(all_trajectories_reject_by=attempt,rows=rows)
    return dict(h=[hmin,hmax],share=share,conservative_share_hull=[low,high],
                funding_lower=funding,both_role_entry_X_squared_upper=X2,
                external_reference_current=je,alpha_exponents=rd['alpha_exponents'],
                beta_exponents=rd['beta_exponents'],controls=controls,
                current_requires_ru_ge_rv=True,reset_requires_ru_ge_rv=False,
                predecessor_source_state_domain_unchanged=True,arbitrary_environment=False)


def evidence():
    return dict(descriptor=descriptor_checks(),algebra=algebra_checks(),kernel=kernel_checks(),
                G5=dict(analytic=analytic_bounds(F(1,8),F(1,8)),embedded=embedded_domain(F(1,8),F(1,8))),
                G6=dict(analytic=analytic_bounds(F(3,25),F(1,8)),embedded=embedded_domain(F(3,25),F(1,8))))


def main():
    base=p.ROOT/p.INV
    predecessor_path=base/'evidence/autonomous-topology-change/ATCSectorStateDomainAdjudication.json'
    predecessor=json.loads(predecessor_path.read_text())
    body=dict(predecessor);digest=body.pop('record_digest')
    require(hashlib.sha256(p.canonical(body)).hexdigest()==digest,'G1-G4 adjudication digest')
    require(digest=='d577ff86b44b76ca6748c930f8bfbab2758aedc077d0c5625fcb640bf139a23e',
            'exact accepted G1-G4 predecessor')
    for binding in predecessor['source_bindings']:
        require(hashlib.sha256((p.ROOT/binding['path']).read_bytes()).hexdigest()==binding['sha256'],
                'reviewed predecessor binding: '+binding['path'])
    record=dict(schema='grcv4_atc_sector_channels_requests_certificate_v1',
        status='G5_G6_bounded_mathematics_pending_independent_review',
        accepted=False,graph_admission=False,native_authority=False,native_ATC_executed=False,
        G7_closed=False,ATC2_closed=False,ATC3_closed=False,
        predecessor_digest=digest,
        interval_encoding='outward integer endpoints divided by 2**256',
        potential_class=dict(domain=['0','9'],center_slope=str(A),slope_deviation=str(K),
            regularity='C1',same_fixed_law_at_every_vertex=True,
            concrete_nonlinear_subclass=dict(form='a*c + nu*c**2/2',
                a=[str(A-F(1,4096)),str(A+F(1,4096))],nu=['1/131072','1/65536'])),
        parameters=p.encode(THETA),tau_A='1/(8*log(2))',
        G6_request_policy='each requested h in [3/25,1/8]; fixed tau and constitutive parameters; no subdivision invariance',
        evidence=p.encode(evidence()),source_bindings=[])
    for path in (Path(__file__).resolve(),base/'scripts/certify_atc_sector_state_domain.py',
                 base/'scripts/certify_atc_sector_readback_box.py',
                 base/'scripts/certify_atc_sector_readback_point.py',predecessor_path,
                 base/'decisions/ATCSectorChannelsAndRequests.md'):
        record['source_bindings'].append(dict(path=str(path.relative_to(p.ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    record['record_digest']=hashlib.sha256(p.canonical(record)).hexdigest()
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
