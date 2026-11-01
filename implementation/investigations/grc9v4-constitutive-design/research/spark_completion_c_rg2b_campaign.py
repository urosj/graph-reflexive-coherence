"""Declared C_RG2b metric-tube campaigns; all physical uncertainty is propagated."""
from fractions import Fraction as F
import time
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_c_rg2b import (CRG2bReference,trap_certificate,ball,ceil_dyadic,PRECISION,DT,ETA,DEPTH,SWEEPS,
    PROPOSAL_BITS,CENTER_BITS,LIP,graph_algebra,global_domain,PARAMETERS)
from spark_completion_positive import fixture,norm_upper
from spark_completion_ci_campaign import exact_bounds,box_payload,matrix_payload
from spark_completion_continuation import need,geometric_roster
import spark_completion_basins as basins
HORIZON=8192
TIME_LIMIT=3600
WINDOW=2


def exact_vector(m,C):return {n:str(C[i,0].fmpq()) for i,n in enumerate(m.nodes)}
def state_payload(m,C,r):return dict(center=exact_vector(m,C),radius=str(r.fmpq()),C=box_payload(m,m.box(C,r)))
def decode(m,s):return m.vector(s['center']),ball(s['radius'])
def interval(bounds):
    a,b=map(F,bounds);need(a<=b,'reversed interval');return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
def section_payload(s,m,C,r):
    out=dict(proposal=matrix_payload(s['proposal']),H=matrix_payload(s['geometry']),J=matrix_payload(s['read']['current']),
        flat=matrix_payload(s['read']['causal_flat']),error=exact_bounds(s['error'],160),tail=exact_bounds(s['tail'],160),
        state_residual=exact_bounds(s['state_residual'],256),geometry_residual=exact_bounds(s['geometry_residual'],256))
    # Section chain certifies its center. This additional read encloses the
    # entire physical tube, including its independent section variation.
    error=(s['error']+ball(LIP)*m.sqrtamax*r).upper()
    H=arb_mat(m.m,m.m)
    for i in range(m.m):
        for j in range(i,m.m):
            if m.overlap[i][j]:H[i,j]=arb(s['proposal'][i,j].fmpq(),error.fmpq());H[j,i]=H[i,j]
    physical=m.lag(m.box(C,r),m.operators(H))
    out['physical_read']=dict(H=matrix_payload(H),J=matrix_payload(physical['current']),flat=matrix_payload(physical['causal_flat']),
        section_error=exact_bounds(error,160),physical_tube_radius=str(r.fmpq()))
    if 'chain' in s:out['chain']=s['chain']
    return out

def prepared_values():
    """A new exact declared prestate for duration eight; no old trajectory input."""
    source,values,_=fixture()
    with ctx.workprec(PRECISION):
        m=CRG2bReference(source);target=m.vector({n:str(x) for n,x in values['current'].items()})
        with ctx.workprec(PROPOSAL_BITS):X,_=m.inverse_proposal(target,m.I,target)
        C=m.quantize(X)
        return dict(current=exact_vector(m,C),reset={n:str(x) for n,x in values['reset'].items()})

def prepare_source(source,targets,role,prepared):
    m=CRG2bReference(source);C=m.vector(prepared['current']);need(sum(C.entries())==21,'exact source charge')
    s=m.section(C,retain_chain=True);post,pr,diag=m.advance_tube(C,arb(0),s)
    fresh=m.section(post,retain_chain=True);box=m.box(post,pr)
    need(all(0<x<4 for x in box.entries()),'source positivity');roster=geometric_roster(source,box,m.nodes)
    need(roster=={'p':sorted(m.nodes)},'fresh complete source parent')
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1)) for e in source['edges']]
    bounds={n:tuple(map(F,exact_bounds(box[i,0]))) for i,n in enumerate(m.nodes)}
    rows=basins.row_intervals(m.nodes,edges,{n:v[0]for n,v in bounds.items()},{n:v[1]for n,v in bounds.items()})
    gv=[interval([str(a),str(b)]) for a,b in rows['v']]
    gradient=16-sum(x*x for x in gv);spark=arb(fmpq(1,8))-min(-x for x in gv)
    need(gradient>0 and spark>0,'actual RG postbeat trigger not eligible')
    ports=[e[end]['port']for e in source['edges']for end in ('tail','head')if e[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'unsaturated source')
    reset=m.quantize(m.vector(prepared['reset']))
    # The declared reset values are rational, so retain them exactly as fmpq
    # before dyadic proposal conversion and include its conversion defect.
    reset_exact=m.vector(prepared['reset']);rr=ball(ceil_dyadic(norm_upper(reset_exact-reset)*m.trace.sqrt()))
    need(sum(F(v)for v in prepared['reset'].values())==21,'exact reset charge')
    reset_section=m.section(reset,retain_chain=True)
    operand,rad=(post,pr) if role=='current' else (reset,rr)
    t=CRG2bReference(targets['1']['graph']);module=targets['1']['module'];shares=['1/64','31/32','1/64']
    T=arb_mat(t.n,m.n)
    for i,n in enumerate(t.nodes):
        if n in m.nodes and n!='v':T[i,m.nodes.index(n)]=1
        elif n in module[1:]:T[i,m.nodes.index('v')]=ball(shares[module[1:].index(n)])
    need(all(sum(T[i,j]for i in range(t.n))==1 for j in range(m.n)),'allocation charge identity')
    target_value=T*operand;after=t.quantize(target_value)
    transport=(t.trace.sqrt()*norm_upper(T)*m.sqrtamax).upper()
    tr=ball(ceil_dyadic(transport*rad+t.trace.sqrt()*norm_upper(target_value-after)))
    need(set(geometric_roster(t.graph,t.box(after,tr),t.nodes))=={'p'},'allocation itself counted as gain')
    record=dict(prepared=prepared,initial=state_payload(m,C,arb(0)),consumed_section=section_payload(s,m,C,arb(0)),
        actual_poststate=state_payload(m,post,pr),fresh_event_section=section_payload(fresh,m,post,pr),
        reset=state_payload(m,reset,rr),reset_section=section_payload(reset_section,m,reset,rr),
        complete_parent=roster,gradient_squared_margin=exact_bounds(gradient),spark_margin=exact_bounds(spark),
        domain=m.domain,source_steps=1,reset_advanced=False,allocation_shares=shares,charge='21',
        geometry_history_transported=False,target_section_rebuilt=True,transport_factor=exact_bounds(transport),
        ordinary_tube=dict(lipschitz=exact_bounds(diag['lipschitz']),defect=exact_bounds(diag['defect'],160)),
        charge_argument='exact incidence and column-stochastic allocation; dyadic centers retain charge and all conversion defects enter the radius')
    return t,after,tr,record

def distance(m,C,r,proof):
    d=C-m.vector(proof['center']);sq=(d.transpose()*m.P*d)[0,0]
    return (max(arb(0),sq.upper()).sqrt()+r).upper()

def campaign(role,prepared,steps=HORIZON,complete=True):
    need(role in ('current','reset'),'unknown role');start=time.monotonic();source,_,targets=fixture()
    proof,_=trap_certificate(targets)
    with ctx.workprec(PRECISION):
        m,C,r,record=prepare_source(source,targets,role,prepared);initial=state_payload(m,C,r)
        rows=[];entry=None;gain=None;checkpoints={}
        s=m.section(C,retain_chain=True);checkpoints['event']={**initial,'section':section_payload(s,m,C,r)}
        target_calls=m.section_calls;target_builds=m.lag_operator_builds;target_newtons=m.newton_iterations;target_sweeps=m.proposal_sweeps
        for step in range(1,steps+1):
            need(time.monotonic()-start<TIME_LIMIT,'declared one-hour research cap reached')
            C,r,diag=m.advance_tube(C,r,s);cb=m.box(C,r);km=list(map(ball,m.domain['K_minus']))
            need(all(km[0]<x<km[1] for x in cb.entries()),'physical trajectory leaves agreement chart')
            need(all(x>0 for x in cb.entries()),'postbeat nonpositive resource')
            need(sum(C.entries())==21,'tube center lost exact charge')
            d=distance(m,C,r,proof);rosters={chi:geometric_roster(t['graph'],cb,m.nodes) for chi,t in targets.items()}
            if gain is None and rosters==proof['complete_basins']:gain=step
            entering=entry is None and d<ball(proof['radius'])
            if entering:need(rosters==proof['complete_basins'],'entry lacks complete basins');entry=step
            if entry is not None:need(d<ball(proof['radius']) and rosters==proof['complete_basins'],'positive window left trap')
            finishing=entry is not None and step==entry+WINDOW
            s=m.section(C,retain_chain=entering or finishing)
            row=dict(step=step,**state_payload(m,C,r),trap_distance_upper=exact_bounds(d)[1],complete_basins=rosters,
                tube=dict(lipschitz=exact_bounds(diag['lipschitz']),defect=exact_bounds(diag['defect'],160)),
                section_error=exact_bounds(s['error'],160))
            rows.append(row)
            if entering:checkpoints['entry']={**state_payload(m,C,r),'section':section_payload(s,m,C,r)}
            if finishing:checkpoints['completion']={**state_payload(m,C,r),'section':section_payload(s,m,C,r)}
            if step%100==0 or entering or finishing:print(role,step,'seconds',round(time.monotonic()-start,1),'distance',d.str(6),'tube',r.str(3),flush=True)
            if finishing:break
        success=entry is not None and len(rows)==entry+WINDOW
        if complete:need(success,'no complete positive window in declared horizon')
        return dict(role=role,source_graph=source,targets=targets,source=record,proof=proof,section_domain=m.domain,
            initial_target=initial,observations=rows,checkpoints=checkpoints,
            decision=dict(role=role,scientific_completion=success and role=='current',local_gain=int(success and role=='current'),
                reset_probe_earns_live_gain=False,first_spatial_gain=gain,first_certified_entry=entry,
                target_completion_step=len(rows) if success else None,window_beats=WINDOW,window_elapsed=str(DT*WINDOW),
                full_state=['C'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False),
            arithmetic=dict(precision_bits=PRECISION,proposal_bits=PROPOSAL_BITS,center_bits=CENTER_BITS,section_depth=DEPTH,
                proposal_sweeps_limit=SWEEPS,maximum_target_steps=HORIZON,time_limit_seconds=TIME_LIMIT,automatic_fallback=False,
                physical_enclosure='charge-tangent metric tubes with full propagated rounding and finite-section error',
                midpoint_only_evolution=False,storage_bits=112,radius_storage='exact dyadic'),
            optimization=dict(target_ordinary_steps=len(rows),target_section_calls=m.section_calls-target_calls,
                target_lag_operator_builds=m.lag_operator_builds-target_builds,target_newton_iterations=m.newton_iterations-target_newtons,
                target_proposal_sweeps=m.proposal_sweeps-target_sweeps,
                graph_cache_hits=graph_algebra.cache_info().hits,domain_cache_hits=global_domain.cache_info().hits,
                immutable_exact_graph_cache=True,precision_keyed_identity_cache=True,per_inverse_operator_reuse=True,
                certified_proposal_early_stop=True,validated_metric_tubes=True,identical_subject_read_reuse=True,
                chiral_incidence_identity=True,trajectory_results_cached=False),
            earlier_family_trajectory_reused=False,native_steps=0,elapsed_seconds=time.monotonic()-start)
