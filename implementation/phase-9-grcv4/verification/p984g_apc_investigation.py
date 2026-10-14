"""Independent A_PC whole-chart and diagonal-prestate first-step research.

FLINT/Arb only; no production current, carrier certificate, writer or step.
Reuse fixed-row operand assembly, not A_CI's joint-root theorem or witness.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from flint import arb, ctx
import p984g_aci_investigation as rows
import p984g_aci_feasibility as scalar

ROOT,BASE,HERE=rows.ROOT,rows.BASE,rows.HERE
SELF=HERE+'p984g_apc_investigation.py'
TEST=HERE+'test_p984g_apc_investigation.py'
PLAN=BASE+'P9-8.4g-APCInvestigationPlan.md'
NOTE=BASE+'P9-8.4g-APCInvestigation.md'
RESULTS=BASE+'P9-8.4g-APCInvestigationResults.json'
PREPARED=BASE+'larger-graph-examples/A_PC.json'
PREPARED_SHA='2a6d5ed6614dd009622d9860100e41499b6116dcd5c120fd9569e53b8e76e367'
BITS=192
q,a,lo,hi=rows.q,scalar.a,scalar.lo,scalar.hi
require,seal,read=rows.require,rows.seal,rows.read


def operands(subject,role):
    # The shared assembler only needs C/W. Strip its nonpersistent assertion
    # on a private copy, then separately validate the actual PC carrier below.
    copy=deepcopy(subject);copy['roles'][role]['Z_4']=None
    return rows.operands(copy,role)


def chart(subject):
    profile=subject['profile'];p=profile['params_resolved'];pc=p['realization'];g=p['geometry']
    require(profile['identity_payload']['profile_family_id']=='A_PC','A_PC only')
    require(pc['schema_version']=='grcv4-pc-params-v1' and
        pc['carrier_norm_id']=='symmetric_star_frobenius_v1' and
        pc['writer_id']=='zero_order_hold_exponential_v1','PC declaration')
    prefix='pc_compact_base_chart_v1:';name=pc['source_envelope_id']
    require(name.startswith(prefix),'compact chart required')
    values=[float.fromhex(s) for s in name[len(prefix):].split(':')]
    require(len(values)==3 and name==prefix+':'.join(x.hex() for x in values),'canonical chart')
    M,wl,wu=map(q,values);R,tau=q(pc['radius']),q(pc['tau_PC'])
    require(M>0 and 0<wl<=wu and R>0 and tau>0,'positive chart')
    cp=p['candidate']
    require(cp['site_potential_id']=='quadratic_site_potential_zero_derivative_v1' and
        cp['conductance_evaluator_id']=='curvature_disabled_G_W_v1','fixed A recipe')
    require(g['star_cover_id']=='vertex_star_exact_overlap_v1' and
        g['overlap_normalization_id']=='edge_multiplicity_inverse_sqrt_v1' and
        g['candidate_adapter_id']=='candidate_a_exact_star_adapter_v1','star recipe')
    require(q(cp['W_floor'])>0 and q(cp['tau_A'])>0 and q(cp['eta'])>0,'positive A parameters')
    return M,wl,wu,R,tau


def carrier(subject,role,m):
    z=subject['roles'][role]['Z_4']
    if z=={'recipe':'zero_v1'}:return [q(0)]*m
    require(set(z)=={'recipe','scale'} and z['recipe']=='alternating_diagonal_v1','diagonal carrier recipe only')
    scale=q(z['scale']);return [scale*(-1)**i for i in range(m)]


def admit_state(c,w,z,bounds):
    M,wl,wu,R,_=bounds
    require(all(x>=0 for x in c) and sum((x*x for x in c),q(0))<=M*M,'resource chart')
    require(all(wl<=x<=wu for x in w),'history chart')
    require(sum((x*x for x in z),q(0))<=R*R,'carrier chart')


def opnorm(matrix):
    r=max(sum(abs(q(int(x))) for x in row) for row in matrix)
    c=max(sum(abs(q(int(x))) for x in col) for col in matrix.T)
    return hi(a(r*c).sqrt())


def whole_chart(subject):
    M,wl,wu,R,_=chart(subject);b,*_=operands(subject,'current')
    p=subject['profile']['params_resolved'];cp=p['candidate'];kh=abs(q(p['geometry']['kappa_H']))
    r=kh*R;lower,upper=1-r,1+r;limit=q(p['solver']['conditioning_limit'])
    require(lower>0 and upper/lower<=limit,'whole-ball Hodge conditioning')
    b2=opnorm(b.T@b);dc=opnorm(b.T)*M
    baseline=q(cp['eta'])*wu*b2*(abs(q(cp['kappa_c']))*wu+abs(q(cp['kappa_Ah']))*r)*dc
    feedback=abs(q(cp['zeta_A'])*q(cp['chi_A']));margin=1-feedback
    require(margin>0 and (1+feedback)/margin<=limit,'whole-chart current conditioning')
    J=baseline/margin;F=abs(q(cp['chi_A']))*J/lower
    source=abs(q(cp['zeta_A']))*F*F
    descriptor=hi(a(6).sqrt())*M
    exponent=(abs(q(cp['alpha']))*hi(a(2).sqrt())*M+
        abs(q(cp['beta']))*(2*descriptor)**2+abs(q(cp['gamma']))*J*J)/2
    require(exponent<=700,'finite conductance chart')
    require(source<=R,'uniform source envelope exceeds carrier radius')
    return dict(hodge_lower=str(lower),hodge_upper=str(upper),current_margin_lower=str(margin),
        current_condition_upper=str((1+feedback)/margin),baseline_upper=str(baseline),
        current_upper=str(J),flat_upper=str(F),source_upper=str(source),
        carrier_radius=str(R),source_slack=str(R-source),conductance_exponent_upper=str(exponent))


def floored_drive(p,ends,c,descriptors,j0):
    floor=q(p['W_floor']);out=[]
    for k,(u,v) in enumerate(ends):
        exponent=-(a(p['alpha'])*(c[u]+c[v])+a(p['beta'])*sum(
            (scalar.square(x-y) for x,y in zip(descriptors[u],descriptors[v])),arb(0))+
            a(p['gamma'])*scalar.square(j0[k]))/2
        value=exponent.exp()
        out.append(a(max(floor,lo(value))).union(a(max(floor,hi(value)))))
    return out


def point(subject,role,*,zero_carrier=False,zero_readback=False):
    b,ends,c,w,desc=operands(subject,role);p=subject['profile']['params_resolved'];cp=p['candidate']
    z=carrier(subject,role,len(w));admit_state(c,w,z,chart(subject))
    if zero_carrier:z=[q(0)]*len(w)
    h=[1+q(p['geometry']['kappa_H'])*x for x in z];require(min(h)>0,'point Hodge')
    d=[c[u]-c[v] for u,v in ends];gram=b.T@b
    potential=[(q(cp['kappa_c'])*wi+q(cp['kappa_Ah'])*(he-1))*di for wi,he,di in zip(w,h,d)]
    baseline=[-q(cp['eta'])*wi*sum((q(int(x))*y for x,y in zip(row,potential)),q(0)) for wi,row in zip(w,gram)]
    drive=floored_drive(cp,ends,list(map(a,c)),[[a(x) for x in row] for row in desc],list(map(a,baseline)))
    contrast=[(a(wi)-gi)/(a(wi)+gi) for wi,gi in zip(w,drive)]
    gain=q(0) if zero_readback else q(cp['zeta_A'])
    blocks=[1-a(gain*q(cp['chi_A']))*x for x in contrast]
    require(all(lo(x)>0 for x in blocks),'point current margin')
    current=[a(x)/be for x,be in zip(baseline,blocks)]
    flat=[a(cp['chi_A'])*qe*je/a(he) for qe,je,he in zip(contrast,current,h)]
    return dict(b=b,ends=ends,c=c,w=w,z=z,h=h,J=current,flat=flat,baseline=baseline,drive=drive)


def case(subject,role,dt):
    bounds=whole_chart(subject);md=point(subject,role);p=subject['profile']['params_resolved'];cp=p['candidate']
    b,c,w,J,flat=md['b'],md['c'],md['w'],md['J'],md['flat'];dt=q(dt);require(dt>0,'positive step')
    after=[a(ci)-a(dt)*sum((int(x)*je for x,je in zip(row,J)),arb(0)) for ci,row in zip(c,b)]
    negative=[dict(vertex=subject['graph']['live_node_ids'][i],lower=str(lo(x)),upper=str(hi(x))) for i,x in enumerate(after) if hi(x)<0]
    unresolved=[subject['graph']['live_node_ids'][i] for i,x in enumerate(after) if lo(x)<0<=hi(x)]
    desc=scalar.descriptors(subject,after,list(map(a,w))) if not negative and not unresolved else None
    # The same weighted-row formula remains algebraically meaningful outside
    # the nonnegative chart, but we do not certify/readmit an excluded poststate.
    writer=None
    if desc is not None:
        target=floored_drive(cp,md['ends'],after,desc,J)
        decay=(-a(dt)/a(cp['tau_A'])).exp()
        updated=[(decay*a(wi).log()+(1-decay)*gi.log()).exp() for wi,gi in zip(w,target)]
        M,wl,wu,_,_=chart(subject)
        writer=dict(weight_lower=str(min(lo(x) for x in updated)),weight_upper=str(max(hi(x) for x in updated)),
            history_in_chart=all(lo(x)>=wl and hi(x)<=wu for x in updated),
            resources_in_chart=hi(sum((scalar.square(x) for x in after),arb(0)))<=M*M,
            timing='postcontinuity_C_incoming_W_selected_current')
    mask=abs(b).T@abs(b)
    source2=sum((scalar.square(a(cp['zeta_A'])*a(q(int(mask[i,j]))/2)*flat[i]*flat[j])
        for i in range(len(w)) for j in range(len(w)) if mask[i,j]),arb(0))
    source_norm=hi(source2.sqrt());oldnorm=rows.norm(md['z']);decay=(-a(dt)/a(p['realization']['tau_PC'])).exp()
    zupper=hi(decay*a(oldnorm)+(1-decay)*a(source_norm))
    zoff=point(subject,role,zero_carrier=True)['J'];off=point(subject,role,zero_readback=True)['J']
    effect=lambda control:dict(maximum_lower=str(max(lo(abs(x-y)) for x,y in zip(J,control))),
        maximum_upper=str(max(hi(abs(x-y)) for x,y in zip(J,control))))
    constraints=[]
    if not any(md['z']):
        # Exact leading rate eta*(B W B^T)^2 C at the zero-carrier target.
        # This reuses only linear coefficient assembly, not CI closure or its
        # selected shares. Nonlinear readback corrections are retained below.
        copy=deepcopy(subject);copy['roles'][role]['Z_4']=None
        for row in scalar.leading_constraints(copy,role):
            row.pop('selected_rate');constraints.append(row)
        rates=[-sum((int(x)*j for x,j in zip(row,J)),arb(0)) for row in b]
        for row in constraints:
            i=next(i for i,n in enumerate(subject['graph']['live_node_ids']) if isinstance(n,str) and n.endswith('/'+row['node']))
            baseline_rate=-sum((q(int(x))*j for x,j in zip(b[i],md['baseline'])),q(0))
            correction=rates[i]-a(baseline_rate)
            row.update(eta=str(q(cp['eta'])),original_rate_lower=str(lo(rates[i])),
                original_rate_upper=str(hi(rates[i])),original_readback_correction_lower=str(lo(correction)),
                original_readback_correction_upper=str(hi(correction)))
    return dict(vertices=len(c),edges=len(w),whole_chart=bounds,
        first_resource_minimum_lower=str(min(lo(x) for x in after)),
        first_resource_minimum_upper=str(min(hi(x) for x in after)),
        negative_vertices=negative,unresolved_vertices=unresolved,
        resource_sign='excluded' if negative else 'inconclusive' if unresolved else 'nonnegative',
        history_writer=writer,carrier_source_norm_upper=str(source_norm),
        carrier_next_norm_upper=str(zupper),carrier_next_in_ball=zupper<=q(p['realization']['radius']),
        carrier_effect=effect(zoff),readback_effect=effect(off),native_admission=False,
        leading_empty_node_constraints=constraints,
        constraint_scope='affine_baseline_in_simplex_shares; correction_bound_only_at_original_state')


def bindings():
    paths=[SELF,TEST,PLAN,PREPARED,rows.SELF,scalar.SELF,rows.shared.SELF,
        'specs/grc-v4-spec.md','specs/grc-9-v4-spec.md','src/pygrc/models/grc_v4_pc.py',
        'src/pygrc/models/grc_v4_candidate_a.py']
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}


def calculate():
    require(hashlib.sha256((ROOT/PREPARED).read_bytes()).hexdigest()==PREPARED_SHA,'frozen declaration drift')
    v=read(PREPARED)
    require(v['reference_recipe']==dict(unit_vertex_measures=True,unit_edge_weights=True,
        K4_base='exact zero m by m in each graph edge order',context=dict(contract_id='constant_zero_context_v1',values={})),
        'unit zero-base reference required')
    with ctx.workprec(BITS):
        cases=[dict(graph=g,role=r,**case(v[g],r,v['selected_configuration']['ordinary_dt'])) for g,r in rows.shared.CASES]
    return seal(dict(schema='p984g-apc-investigation-v1',family='A_PC',cases=cases,source_bindings=bindings(),
        precision_bits=BITS,scope='exact_real_whole_chart_and_diagonal_prestate_not_native_or_staged',
        native_steps=0,native_events=0,user_accepted=False,ready_for_8_4h=False,aggregate_closed=False,
        open_obligations=['both-role feasibility if excluded; derive before selecting a companion',
            'represented current/two-writer/final-read oracle and numerical-error separation',
            'review oracle before native prerequisite conformance','8.4h actual postbeat event and continuation']))


def check(value=None):
    value=read(RESULTS) if value is None else value
    require(value==calculate(),'A_PC research/source/scope drift');return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['run','check']);args=parser.parse_args()
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite')
        raw=json.dumps(calculate(),indent=2)+'\n';require(len(raw.encode())<=250000,'compact evidence budget')
        (ROOT/RESULTS).write_text(raw)
    else:check()
