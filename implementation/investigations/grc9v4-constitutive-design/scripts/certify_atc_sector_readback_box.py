#!/usr/bin/env python3
"""Original CAN-LSF box: source/entry enclosures and separate kernel hardening.

Reuse the immutable reviewed interval kernel, not the point's trajectories.
Use exact paired-source coordinates to avoid spurious cancellation/wrapping.
No target search, parameter shrinking, native calls or output-file writes.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import certify_atc_sector_readback_point as point

I, GRID = point.I, point.GRID
ROOT, INV, REFS = point.ROOT, point.INV, point.REFS


def span(a, b):
    return I.bounds(I(F(a)).lo, I(F(b)).hi)


class Uncertified(Exception):
    def __init__(self, stage, data):
        self.stage, self.data = stage, data


def require(condition, stage, data):
    if not condition:
        raise Uncertified(stage, data)


def exponential_probes():
    """Independent positive-series reciprocal brackets, no libm/Decimal oracle."""
    rows = []
    for t in (F(1, 2048), F(1, 8), F(3, 2), F(10), F(100)):
        n = 64+8*point.ceil_div(t.numerator, t.denominator)
        term, total = F(1), F(1)
        for k in range(1, n+1):
            term *= t/k
            total += term
        next_term = term*t/(n+1)
        assert t < n+2
        upper_positive = total+next_term/(1-t/(n+2))
        # Positive terms; subsequent ratios <= t/(n+2) give a geometric tail.
        lower, upper = 1/upper_positive, 1/total
        tested = I(-t).exp_nonpositive()
        assert F(tested.lo, GRID) <= lower <= upper <= F(tested.hi, GRID)
        rows.append(dict(argument=str(-t), positive_series_order=n, enclosure=tested,
                         independent_rational_bracket_contained=True))
    return dict(status='PASS',method='positive Taylor series + geometric tail + reciprocal',
                reviewed_kernel_unchanged=True, probes=rows)


def read(b, w, theta):
    hat = (-theta['gamma']*b.square()/2).exp_nonpositive()
    require(hat.lo > GRID//2, 'pre_read_floor', dict(target=hat))
    q = (w-hat)/(w+hat)
    den = 1-theta['chi']*q
    require(den.lo > 0, 'read_denominator', dict(denominator=den))
    j = b/den
    return j, theta['chi']*q*j


def source_read(x, y, u, v, theta):
    a = F(19, 4)
    bu = u*((3*u+2*v-a)*x+(-3*u+2*v+a)*y)
    bv = v*((2*u+3*v-a)*x+(-2*u+3*v-a)*y)
    ju, fu = read(bu, u, theta)
    jv, fv = read(bv, v, theta)
    du, dv = y-x, -y-x
    su = F(3, 2)*fu.square()*du+fu*fv*dv
    sv = fu*fv*du+F(3, 2)*fv.square()*dv
    product = theta['kh']*theta['kah']
    delta_u = -product*u*(3*su+2*sv)
    delta_v = -product*v*(2*su+3*sv)
    fresh_u, ru = read(bu+delta_u, u, theta)
    fresh_v, rv = read(bv+delta_v, v, theta)
    # H>=I, so ||H^-1 r||<=||r||. Star trace bounds its Frobenius norm.
    residual = theta['kh']*2*(fu.square()+fv.square()+ru.square()+rv.square())
    require(residual.hi < GRID*F(1, 512), 'source_OS_residual', dict(upper=residual))
    return dict(reference=(ju, jv), fresh=(fresh_u, fresh_v), source_forms=(fu, fv),
                fresh_baseline_changes=(delta_u, delta_v), star_d=(su, sv),
                residual_upper=residual)


def source_resources(x, y):
    mean = (9-x)/5
    return (mean+y, mean+y, mean-y, mean-y, (9+4*x)/5)


def source_step(state, theta):
    x, y, u, v = state
    readout = source_read(x, y, u, v, theta)
    ju, jv = readout['fresh']
    xn, yn = x+F(5, 16)*(ju+jv), y+F(1, 16)*(jv-ju)
    Cn = source_resources(xn, yn)
    minimum = point.minimum(Cn)
    if minimum.hi < 0:
        return dict(status='negative_resource', minimum_C=minimum, C_next=Cn,
                    residual_upper=readout['residual_upper'], next_state=None)
    require(minimum.lo > 0, 'source_resource_sign', dict(minimum=minimum))
    drivers = tuple((-theta['gamma']*j.square()/2).exp_nonpositive() for j in (ju, jv))
    require(all(d.lo > GRID//2 for d in drivers), 'source_writer_floor', dict(drivers=drivers))
    un, vn = ((w*d).sqrt() for w, d in zip((u, v), drivers, strict=True))
    require(all(w.lo >= GRID//2 and w.hi <= GRID for w in (un, vn)), 'source_W_domain', dict(W=(un,vn)))
    return dict(status='admitted_positive', minimum_C=minimum, C_next=Cn,
                residual_upper=readout['residual_upper'], next_state=(xn, yn, un, vn),
                drivers=drivers, readout=readout)


def algebra_checks():
    """Exact matrix/reduced-form comparisons, without a trajectory rerun."""
    B = point.incidence(5, point.SOURCE); BT = tuple(zip(*B))
    mv = lambda m,v: tuple(sum((a*b for a,b in zip(row,v,strict=True)),F()) for row in m)
    for x,y,u,v in ((F(4),F(0),F(361,400),F(5929,6400)),
                    (F(4),F(1,64),F(19,20),F(77,80)),
                    (F(7),F(1,4),F(9,10),F(99,100))):
        C = ((9-x)/5+y,)*2+((9-x)/5-y,)*2+((9+4*x)/5,)
        W=(u,u,v,v); d=mv(BT,C); lap=mv(B,tuple(w*z for w,z in zip(W,d,strict=True)))
        b=tuple(w*z for w,z in zip(W,mv(BT,tuple(F(19,4)*c-l for c,l in zip(C,lap,strict=True))),strict=True))
        bu=u*((3*u+2*v-F(19,4))*x+(-3*u+2*v+F(19,4))*y)
        bv=v*((2*u+3*v-F(19,4))*x+(-2*u+3*v-F(19,4))*y)
        assert b == (bu,bu,bv,bv)
        fu,fv=F(1,256),F(1,384); f=(fu,fu,fv,fv)
        S=tuple(tuple(F(sum(bool(r[i] and r[j]) for r in B),2)*f[i]*f[j] for j in range(4)) for i in range(4))
        su=F(3,2)*fu*fu*(y-x)+fu*fv*(-y-x)
        sv=fu*fv*(y-x)+F(3,2)*fv*fv*(-y-x)
        assert mv(S,d)==(su,su,sv,sv)
        assert mv(BT,mv(B,mv(S,d))) == (3*su+2*sv,)*2+(2*su+3*sv,)*2
    return dict(exact_matrix_comparisons=3, charge='9, eliminated algebraically', symmetry='reviewed invariant paired subspace')


def full_stage(C,W,H,B,theta):
    d=point.mv(tuple(zip(*B)),C)
    lap=point.mv(B,tuple(w*z for w,z in zip(W,d,strict=True)))
    delta=tuple(tuple(h-int(i==j) for j,h in enumerate(row)) for i,row in enumerate(H))
    geometry=tuple(theta['kah']*v for v in point.mv(B,point.mv(delta,d)))
    phi=tuple(l-F(19,4)*c+g for l,c,g in zip(lap,C,geometry,strict=True))
    baseline=tuple(-w*z for w,z in zip(W,point.mv(tuple(zip(*B)),phi),strict=True))
    blocks=tuple(read(b,w,theta) for b,w in zip(baseline,W,strict=True))
    return tuple(b[0] for b in blocks),point.solve(H,tuple(b[1] for b in blocks))


def target_entry(C,W,theta):
    B=point.incidence(6,point.TARGET)
    identity=tuple(tuple(I(int(i==j)) for j in range(5)) for i in range(5))
    _,f0=full_stage(C,W,identity,B,theta); S=point.star(f0,B)
    H=tuple(tuple(a+theta['kh']*b for a,b in zip(row,other,strict=True)) for row,other in zip(identity,S,strict=True))
    J,f1=full_stage(C,W,H,B,theta)
    residual=theta['kh']*(point.norm2(f0)+point.norm2(f1))
    require(residual.hi < GRID*F(1,512), 'target_OS_residual', dict(residual=residual))
    Cn=tuple(c-v/8 for c,v in zip(C,point.mv(B,J),strict=True))
    require(point.minimum(Cn).lo>0,'target_positivity',dict(C=Cn))
    drivers=tuple((-theta['gamma']*j.square()/2).exp_nonpositive() for j in J)
    require(all(d.lo>GRID//2 for d in drivers),'target_writer_floor',dict(drivers=drivers))
    Wn=tuple((w*d).sqrt() for w,d in zip(W,drivers,strict=True))
    X2=point.norm2(tuple(c-F(3,2) for c in Cn))
    lower=I(F(-1,8)).exp_nonpositive()
    require(X2.hi < GRID*F(4,9),'target_return_radius',dict(X2=X2))
    require(all(w.lo>lower.hi and w.hi<=GRID for w in Wn),'target_log_history',dict(W=Wn))
    return dict(C_after=Cn,W_after=Wn,X_squared=X2,minimum_C=point.minimum(Cn),
                split_residual_upper=residual,all_entry_hypotheses_certified=True)


def box_evidence():
    theta=dict(chi=span('1/32','1/16'),gamma=span('1/2048','1/1024'),kh=span('1/2','1'),kah=span('1/2','1'))
    initial=(I(4),I(0),I(F(361,400)),I(F(5929,6400)))
    initial_guard=F(5,2)*(initial[2]+initial[3])-F(19,4)
    assert initial_guard.hi<0
    first=source_step(initial,theta); state=first['next_state']; assert state is not None
    x,y,u,v=state
    now=source_read(*state,theta); ju,jv=now['reference']
    margins=dict(sector_separation=v-u,old_source_spectral_guard=F(5,2)*(u+v)-F(19,4),
                 inward=point.minimum((ju,jv)),x=x,y=y)
    require(all(v.lo>0 for v in margins.values()),'source_guard',margins)
    ratio=65536*ju/(ju+jv)
    # A conservative closed hull of every round-even output; ties included.
    kmin=(ratio.lo+GRID//2)//GRID
    if ratio.lo+GRID//2 == kmin*GRID: kmin-=1
    kmax=(ratio.hi+GRID//2)//GRID
    assert 0<kmin<=kmax<65536
    share=span(F(kmin,65536),F(kmax,65536)); complement=1-share
    C1=source_resources(x,y)
    funding=(share*C1[4]-C1[0],complement*C1[4]-C1[2])
    require(all(f.lo>0 for f in funding),'funding',dict(margins=funding,k_range=[kmin,kmax]))
    progress=dict(source_margins=margins,grid_coordinate=ratio,k_hull=[kmin,kmax],funding=funding)
    controls={}
    try:
        for name,start_state,start,expected in (
                ('no_split',state,2,10),('history_reset_without_split',(x,y,I(1),I(1)),1,7)):
            rows=[dict(attempt=1,minimum_C=first['minimum_C'],residual_upper=first['residual_upper'])] if name=='no_split' else []
            cur=start_state
            for attempt in range(start,17):
                row=source_step(cur,theta)
                rows.append(dict(attempt=attempt,status=row['status'],minimum_C=row['minimum_C'],residual_upper=row['residual_upper']))
                if row['next_state'] is None: break
                cur=row['next_state']
            require(row['next_state'] is None,'source_failure_horizon',dict(rows=rows))
            controls[name]=dict(rows=rows,failed_attempt=attempt,point_comparator_attempt=expected)
        progress['controls']=controls
        # Cover ALL integer outcomes with eight consecutive proof cells.
        # These are universal enclosures, not alternative targets to choose.
        width=point.ceil_div(kmax-kmin+1,8)
        cells=[]
        for lo in range(kmin,kmax+1,width):
            hi=min(lo+width-1,kmax)
            cell_share=span(F(lo,65536),F(hi,65536))
            cell=dict(k_range=[lo,hi],target_roles={})
            for name,C,W in (('current',C1,(u,u,v,v)),
                             ('reset',(I(1),)*4+(I(5),),(initial[2],initial[2],initial[3],initial[3]))):
                cell['target_roles'][name]=target_entry(C[:4]+(cell_share*C[4],(1-cell_share)*C[4]),W+(I(1),),theta)
            cells.append(cell)
        assert [k for cell in cells for k in range(cell['k_range'][0],cell['k_range'][1]+1)]==list(range(kmin,kmax+1))
        progress['target_entry_cells']=cells
    except Uncertified as exc:
        exc.data=dict(partial=progress,failing_bounds=exc.data)
        raise
    # Uniform nonvacuity at the initial beat, without subtracting correlated
    # wide selected-current intervals. F'(b)>=1/(1+chi_max) for gamma>=0.
    initial_read=first['readout']; fu,fv=initial_read['source_forms']
    require(min(fu.lo,fv.lo)>0,'uniform_nonvacuity',dict(source_forms=(fu,fv)))
    deltas=initial_read['fresh_baseline_changes']
    require(all(d.lo>0 for d in deltas),'uniform_geometry_consumption',dict(deltas=deltas))
    current_gap_lower=I.bounds(min(d.lo for d in deltas),min(d.lo for d in deltas))/F(17,16)
    require(all(d.hi<GRID for d in first['drivers']),'uniform_history_consumption',dict(drivers=first['drivers']))
    progress.update(initial_guard=initial_guard,first_source=first,parameters=theta,
                    nonvacuity=dict(reference_read_flux=(fu,fv),fresh_current_gap_lower=current_gap_lower,
                                    geometry_baseline_changes=deltas,writer_targets=first['drivers']),
                    all_parameter_points_covered=True,parameter_subdivision=False,parameter_shrinking=False,
                    target_selection=False,actual_reachable_k_set_claimed=False,
                    bin_coverage='every integer in conservative k hull covered by consecutive closed share cells; every cell must pass both roles',
                    source_prescription_changed=False,share_proof_cells=len(cells),physical_target_count_per_source=1)
    return progress


def main():
    names=('ATCSectorReadBackPointCertificate.json','ATCSectorReadBackPointAdjudication.json')
    prior=[]
    for name in names:
        value=json.loads((ROOT/REFS/name).read_text()); body=dict(value); digest=body.pop('record_digest')
        assert hashlib.sha256(point.canonical(body)).hexdigest()==digest
        for b in value['source_bindings']:
            assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],b['path']
        prior.append(digest)
    result=dict(schema='grcv4_atc_sector_readback_box_pressure_v1',predecessor_digests=prior,
                arithmetic='reviewed 256-bit outward dyadic kernel',kernel_hardening=exponential_probes(),
                reduced_algebra=algebra_checks(),scientific_acceptance=False,graph_admission=False,ATC2_closed=False)
    try:
        result.update(status='box_enclosure_certificate_pending_review',box=box_evidence())
    except Uncertified as exc:
        result.update(status='enclosure_inconclusive_not_a_physical_counterexample',failed_stage=exc.stage,details=exc.data)
    paths=[Path(__file__).relative_to(ROOT),INV/'scripts/certify_atc_sector_readback_point.py',
           *[REFS/name for name in names],INV/'decisions/ATCSectorReadBackLiftProposal.md',
           INV/'decisions/ATCSectorReadBackBoxCertification.md']
    result['source_bindings']=[dict(path=str(p),sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]
    result=point.encode(result);result['record_digest']=hashlib.sha256(point.canonical(result)).hexdigest()
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
