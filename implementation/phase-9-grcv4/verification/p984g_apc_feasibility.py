"""A_PC-specific allocation and old-carrier interval-input feasibility."""
import argparse
from copy import deepcopy
import hashlib
import json
import lzma
import signal
from flint import arb, ctx
import p984g_apc_investigation as prior
import prepare_p983_all_realizations as mechanical

ROOT,BASE,HERE=prior.ROOT,prior.BASE,prior.HERE
SELF=HERE+'p984g_apc_feasibility.py'
TEST=HERE+'test_p984g_apc_feasibility.py'
PLAN=BASE+'P9-8.4g-APCFeasibilityPlan.md'
NOTE=BASE+'P9-8.4g-APCFeasibility.md'
RESULTS=BASE+'P9-8.4g-APCFeasibilityResults.json.xz'
q,a,lo,hi,require=prior.q,prior.a,prior.lo,prior.hi,prior.require
BITS=192


def select(constraints):
    equations=[row for rows in constraints.values() for row in rows]
    require(len(equations)==10,'two-history five-node constraint roster')
    for den in (2,4,8,16,32,64):
        choices=[]
        for i in range(1,den):
            for j in range(1,den-i):
                shares=(q(i)/den,q(j)/den,q(den-i-j)/den)
                margin=min(q(row['offset'])+sum((q(x)*s for x,s in zip(row['coefficients'],shares)),q(0)) for row in equations)
                if margin>0:choices.append((margin,shares))
        if choices:
            margin,shares=sorted(choices,key=lambda c:(-c[0],c[1]))[0]
            return dict(shares=list(map(str,shares)),denominator=den,leading_margin=str(margin),
                rule='first_dyadic_grid_positive_then_max_min_leading_rate_lexicographic')
    raise ValueError('no candidate in declared dyadic grids; no target-fit fallback')


def compensation_node(graph,source):
    adjacency={n:set() for n in graph['live_node_ids']}
    for e in graph['edges']:
        u,v=e['tail']['node_id'],e['head']['node_id'];adjacency[u].add(v);adjacency[v].add(u)
    distances={source:0};todo=[source]
    for n in todo:
        for other in sorted(adjacency[n]):
            if other not in distances:distances[other]=distances[n]+1;todo.append(other)
    require(len(distances)==len(adjacency),'connected source required')
    distance=max(distances.values());require(distance>2,'no remote compensation site')
    return min(n for n,d in distances.items() if d==distance),distance


def companion(shares,*,perturb):
    with mechanical.exact_backend(mechanical.ExactBackend.FLINT):
        return _companion(shares,perturb=perturb)


def _companion(shares,*,perturb):
    old=prior.read(prior.PREPARED);shares=list(map(q,shares))
    require(len(shares)==3 and min(shares)>0 and sum(shares,q(0))==1,'strict simplex')
    require(all(q(float(s))==s for s in shares),'exact binary64 shares')
    graph=mechanical.GRC9V4PortGraph.from_envelope(old['source']['graph'])
    source=old['event_request']['source_node_id'];remote,distance=compensation_node(old['source']['graph'],source)
    delta=4*q(old['selected_configuration']['ordinary_dt']) if perturb else q(0)
    require(0<=delta<q('1/4'),'bounded source perturbation')
    for state in old['source']['roles'].values():
        for node,change in ((source,-delta),(remote,delta)):
            i=graph.live_node_ids.index(node);value=q(state['C'][i])+change
            require(value>=0 and q(float(value))==value,'exact resource shift')
            state['C'][i]=float(value)
    profile=mechanical.GRCV4Profile.from_canonical_bytes(mechanical.canonical_json_bytes(old['source']['profile']))
    spec=mechanical.native.GRC9V4Specialization(mechanical.FrozenJSONMap(old['specialization']['resolved']),
        mechanical.FrozenJSONMap(old['specialization']['identity_payload']))
    roles={r:mechanical.authority(s,len(graph.edges)) for r,s in old['source']['roles'].items()}
    state=mechanical.make_state(graph,profile,spec,roles,'A_PC')
    old['source'].update(mechanical.identities(state))
    request=deepcopy(old['event_request'])
    request.update(operation_id='p984g-apc-source-allocation-v1' if perturb else 'p984g-apc-allocation-only-v1',
        source_state_digest=state.scientific_digest,resource_distribution=list(map(float,shares)),
        history_policy=mechanical.expansion.apc_history_policy(roles['current'],roles['reset']))
    plan=mechanical.expansion.GRC9V4ExpansionPlan(graph,state.scientific_digest,
        mechanical.expansion.GRC9V4ExpansionRequestInput.from_payload(request),
        mechanical.expansion.GRC9ExpansionPolicy.from_payload(old['specialization']['resolved']['expansion']))
    target=dict(graph=plan.target_graph.to_envelope(),
        profile=mechanical.profile_for(plan.target_graph,'A_PC',old['selected_configuration']).to_payload(),roles={})
    mapping={plan.event_id+f'/satellite/{i+1}':s for i,s in enumerate(shares)}
    matrix=[[mapping.get(n,q(0)) if v==source else q(int(n==v)) for v in graph.live_node_ids]
        for n in plan.target_graph.live_node_ids]
    require(all(sum(col,q(0))==1 for col in zip(*matrix)),'charge-preserving resource map')
    actual=mechanical.expansion._resource_transform(plan)
    require([q(x) for x in actual['row_major_coefficients']]==[x for row in matrix for x in row]
        and all(x==0 for x in actual['target_increment']),'mechanical map mismatch')
    for role,s in old['source']['roles'].items():
        c=[sum((x*q(y) for x,y in zip(row,s['C'])),q(0)) for row in matrix]
        require(all(q(float(x))==x for x in c),'exact target resources')
        weights=dict(zip((e.edge_id for e in graph.edges),s['W_A']))
        target['roles'][role]=dict(C=list(map(float,c)),
            W_A=[weights.get(e.edge_id,plan.policy.bond_seed) for e in plan.target_graph.edges],Z_4={'recipe':'zero_v1'})
    identity=dict(request=request,event_id=plan.event_id,target_graph_digest=plan.target_graph.graph_digest,
        target_profile_id=mechanical.profile_for(plan.target_graph,'A_PC',old['selected_configuration']).complete_profile_id,
        source_scientific_digest=state.scientific_digest,shares=list(map(str,shares)),
        source_deficit=str(delta),compensation_node=remote,compensation_distance=distance,
        history_policy_unchanged=True,carrier_policy='whole_carrier_reset_with_loss_receipt_v1',
        identity_scope='prebeat_mechanical_declaration_not_postbeat_event_receipt')
    return old,target,matrix,identity


def state_box(subject,role,c=None,w=None):
    bv,ends,cs,ws,_=prior.operands(subject,role)
    c=list(map(a,cs)) if c is None else c;w=list(map(a,ws)) if w is None else w
    require(len(c)==len(cs) and len(w)==len(ws),'box coordinate coverage')
    M,wl,wu,R,_=prior.chart(subject)
    require(all(lo(x)>=0 for x in c) and hi(sum((prior.scalar.square(x) for x in c),arb(0)))<=M*M,'resource box chart')
    require(all(lo(x)>=wl and hi(x)<=wu for x in w),'history box chart')
    z=prior.carrier(subject,role,len(w));require(sum((x*x for x in z),q(0))<=R*R,'carrier box chart')
    p=subject['profile']['params_resolved'];cp=p['candidate']
    h=[1+q(p['geometry']['kappa_H'])*x for x in z];require(min(h)>0,'diagonal Hodge')
    descriptors=prior.scalar.descriptors(subject,c,w)
    phi=[arb(0) for _ in c]
    for i,(u,v) in enumerate(ends):
        term=(a(cp['kappa_c'])*w[i]+a(cp['kappa_Ah'])*a(h[i]-1))*(c[u]-c[v])
        phi[u]+=term;phi[v]-=term
    baseline=[-a(cp['eta'])*we*(phi[u]-phi[v]) for we,(u,v) in zip(w,ends)]
    drives=prior.floored_drive(cp,ends,c,descriptors,baseline)
    contrast=[(we-ge)/(we+ge) for we,ge in zip(w,drives)]
    blocks=[1-a(cp['zeta_A'])*a(cp['chi_A'])*qe for qe in contrast]
    require(min(lo(x) for x in blocks)>0,'interval physical current margin')
    J=[j/be for j,be in zip(baseline,blocks)]
    flat=[a(cp['chi_A'])*qe*je/a(he) for qe,je,he in zip(contrast,J,h)]
    return dict(b=bv,ends=ends,c=c,w=w,z=z,J=J,flat=flat,baseline=baseline)


def step(subject,role,dt,c=None,w=None):
    md=state_box(subject,role,c,w);p=subject['profile']['params_resolved'];cp=p['candidate'];dt=q(dt)
    require(dt>0,'positive dt')
    after=[ci-a(dt)*sum((int(x)*j for x,j in zip(row,md['J'])),arb(0)) for ci,row in zip(md['c'],md['b'])]
    require(min(lo(x) for x in after)>0,'positive continuation not established')
    desc=prior.scalar.descriptors(subject,after,md['w'])
    drive=prior.floored_drive(cp,md['ends'],after,desc,md['J'])
    weights=prior.scalar.log_writer(md['w'],drive,dt,cp['tau_A'])
    M,wl,wu,R,_=prior.chart(subject)
    resource_norm=hi(sum((prior.scalar.square(x) for x in after),arb(0)).sqrt())
    require(resource_norm<=M and all(lo(x)>=wl and hi(x)<=wu for x in weights),'post-C/W chart not established')
    # S generally has off-diagonals. Use its full Frobenius bound, never feed
    # a fictitious diagonal Z' into a second read.
    flatnorm=prior.scalar.norm(md['flat']);source=abs(q(cp['zeta_A']))*flatnorm**2
    decay=(-a(dt)/a(p['realization']['tau_PC'])).exp()
    zupper=hi(decay*a(prior.rows.norm(md['z']))+(1-decay)*a(source))
    require(zupper<=R,'next carrier chart not established')
    return dict(all_positive=True,minimum_resource_lower=str(min(lo(x) for x in after)),
        resource_norm_upper=str(resource_norm),history_lower=str(min(lo(x) for x in weights)),
        history_upper=str(max(hi(x) for x in weights)),history_chart=True,
        held_source_norm_upper=str(source),next_carrier_norm_upper=str(zupper),carrier_chart=True,
        history_writer_stage='postcontinuity_C_incoming_W_selected_current',
        carrier_writer_stage='incoming_PC_read_held_source',poststate_read_executed=False),after,weights


def transfer(old,target,matrix,c,w):
    values=[sum((a(x)*y for x,y in zip(row,c)),arb(0)) for row in matrix]
    lineage={e['edge_id']:x for e,x in zip(old['source']['graph']['edges'],w)}
    weights=[lineage.get(e['edge_id'],a(old['specialization']['resolved']['expansion']['bond_seed'])) for e in target['graph']['edges']]
    return values,weights


def bindings():
    paths=[SELF,TEST,PLAN,prior.SELF,prior.RESULTS,prior.PREPARED,prior.rows.SELF,prior.scalar.SELF,
        HERE+'prepare_p983_all_realizations.py','src/pygrc/models/grc_9_v4_expansion.py',
        'src/pygrc/models/grc_9_v4_topology.py','src/pygrc/models/grc_v4_pc.py',
        'src/pygrc/models/grc_v4_candidate_a.py']
    return {s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}


def calculate():
    original=prior.read(prior.RESULTS)
    require(original==prior.seal(original) and original['source_bindings']==prior.bindings(),'prior research drift')
    constraints={c['role']:c['leading_empty_node_constraints'] for c in original['cases'] if c['graph']=='target'}
    selection=select(constraints)
    print('selected allocation',selection['shares'],'mechanical FLINT construction',flush=True)
    old,target,matrix,identity=companion(selection['shares'],perturb=True)
    print('source companion declaration complete',flush=True)
    allocation,atarget,amatrix,aid=companion(selection['shares'],perturb=False)
    print('allocation-only declaration complete; interval equations',flush=True)
    dt=old['selected_configuration']['ordinary_dt'];cases=[];diagnostics=[]
    with ctx.workprec(BITS):
        charts={g:prior.whole_chart(s) for g,s in (('source',old['source']),('target',target))}
        for role in ('current','reset'):
            initial,_,_=step(atarget,role,dt)
            src,c,w=step(allocation['source'],role,dt)
            diagnostics.append(dict(role=role,initial_target=initial,source_postbeat=src,
                source_trigger=prior.scalar.trigger(allocation,c,w)))
            print('allocation-only',role,'complete',flush=True)
        for role in ('current','reset'):
            initial,_,_=step(target,role,dt)
            source,c,w=step(old['source'],role,dt)
            signal=prior.scalar.trigger(old,c,w)
            require(signal['small_gradient'] and q(signal['minimum_signed_hessian_upper'])<-q(identity['source_deficit'])/2,'robust postbeat trigger not established')
            tc,tw=transfer(old,target,matrix,c,w)
            fresh,_,_=step(target,role,dt,tc,tw)
            cases.append(dict(role=role,initial_target=initial,source_postbeat=source,
                source_trigger=signal,postbeat_transfer_target=fresh,
                postbeat_role_use='live_current' if role=='current' else 'reset_as_current_diagnostic_not_event_reset'))
            print('full companion',role,'complete',flush=True)
    return prior.seal(dict(schema='p984g-apc-feasibility-v1',family='A_PC',precision_bits=BITS,
        source_bindings=bindings(),source=old['source'],target=target,companion=identity,selection=selection,
        leading_constraints=constraints,whole_charts=charts,cases=cases,
        allocation_only=dict(companion=aid,cases=diagnostics),
        original_research_digest=original['record_digest'],original_reset_exclusion_preserved=True,
        event_pair=dict(current='postbeat_transfer_target/current',reset='initial_target/reset',reset_evolves=False,
            candidate_history='exact_old_edge_lineage_plus_positive_seed',carrier='whole_history_loss_zero_target'),
        scope='exact_real_PC_interval_input_resource_history_carrier_trigger_not_native_or_final_read',
        native_steps=0,native_events=0,ready_for_8_4h=False,user_accepted=False,aggregate_closed=False,
        open_obligations=['represented current and both writers with mechanism/error discrimination',
            'fresh final-C/W/Z readmission; poststep source Z is not diagonal',
            'native prerequisite conformance after oracle review',
            '8.4h fresh actual postbeat identity/archive/event and continuation']))


def read():return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def check_retained(value=None):
    v=read() if value is None else value
    require(v==prior.seal(v) and v['source_bindings']==bindings(),'feasibility identity/source drift')
    require(v['schema']=='p984g-apc-feasibility-v1' and v['family']=='A_PC' and v['precision_bits']==BITS,'feasibility schema')
    require(v['selection']==select(v['leading_constraints']) and v['companion']['shares']==v['selection']['shares'],'selection drift')
    require(v['original_research_digest']==prior.read(prior.RESULTS)['record_digest'] and v['original_reset_exclusion_preserved'],'lost original exclusion')
    require(v['companion']['source_deficit']=='1/1024' and v['companion']['compensation_node']==29
        and v['companion']['compensation_distance']==8,'source fixture drift')
    require(v['event_pair']==dict(current='postbeat_transfer_target/current',reset='initial_target/reset',reset_evolves=False,
        candidate_history='exact_old_edge_lineage_plus_positive_seed',carrier='whole_history_loss_zero_target'),'event chronology')
    require([c['role'] for c in v['cases']]==['current','reset'],'role roster')
    for c in v['cases']:
        require(c['source_trigger']['small_gradient'] and q(c['source_trigger']['minimum_signed_hessian_upper'])<-q('1/2048'),'trigger margin')
        for stage in ('initial_target','source_postbeat','postbeat_transfer_target'):
            s=c[stage]
            require(s['all_positive'] and q(s['minimum_resource_lower'])>0 and s['history_chart'] and s['carrier_chart']
                and not s['poststate_read_executed'],'continuation scope')
    require(v['native_steps']==v['native_events']==0 and not v['ready_for_8_4h'] and not v['user_accepted']
        and not v['aggregate_closed'],'research promotion')
    return v


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['run','check','recompute']);args=parser.parse_args()
    def timeout(*_):raise TimeoutError('300-second research cap; no fallback')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(300)
    if args.mode=='run':
        require(not (ROOT/RESULTS).exists(),'no overwrite');value=calculate();check_retained(value)
        raw=(json.dumps(value,indent=2)+'\n').encode();require(len(raw)<=3000000,'raw evidence budget')
        (ROOT/RESULTS).write_bytes(lzma.compress(raw,preset=6))
    elif args.mode=='recompute':require(read()==calculate(),'full interval recomputation drift')
    else:check_retained()
