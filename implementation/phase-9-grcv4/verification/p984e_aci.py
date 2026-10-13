"""A_CI ordering covariance of full joint roots, not current-only agreement.

Reuses accepted transformation algebra and CI interval equations. Only run
executes native operations; retained checking never reconstructs native roots.
"""
import argparse
from contextlib import ExitStack, nullcontext
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

import p984e_cos as algebra
import p984d_aci_runtime as prior
from pygrc.models.grc_9_v4_expansion import aci_profile_template

r, b = prior.r, prior.b
SELF=b.HERE+'p984e_aci.py'
TEST=b.HERE+'test_p984e_aci.py'
PLAN=b.BASE+'P9-8.4e-ACIPlan.md'
INPUTS=b.BASE+'P9-8.4e-ACIInputs.json'
RESULTS=b.BASE+'P9-8.4e-ACIResults.json'
REVIEW=b.BASE+'P9-8.4e-ACIReview.md'
ROLES, KINDS = algebra.ROLES, algebra.KINDS


def make_manifest():
    deep=b.read(prior.INPUTS);phase=b.read(r.INPUTS)
    for value in (deep,phase):
        b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(deep['initial_inputs']==phase['initial_inputs'],'different predecessor sources')
    cases=[next(c for c in phase['cases'] if c['request']['target_effective_degree']==52
                and c['request']['module_chirality']==1 and c['request']['growth_phase']==1),
           next(c for c in deep['cases'] if c['request']['target_effective_degree']==94
                and c['request']['module_chirality']==-1 and c['request']['growth_phase']==3)]
    traces=algebra.authority()
    paths={SELF,TEST,PLAN,algebra.SELF,prior.INPUTS,prior.REVIEW,r.INPUTS,r.REVIEW,
           prior.SELF,prior.previous.SELF,r.SELF}
    paths|={x['path'] for m in (deep,phase) for x in m['source_bindings']}
    paths|={x['source_ref']['path'] for t in traces.values() for x in t['rows']}
    return b.seal(dict(schema='p984e-aci-inputs-v1',family='A_CI',source_bindings=b.bind(paths),
        initial_inputs=deep['initial_inputs'],expected_source=deep['expected_source'],cases=cases,
        transforms=algebra.declarations(),authority=traces,
        comparison=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13),
        scope=dict(layouts=2,transforms=5,required_history_cells=20,native_events=12,
                   target_steps=48,steps_per_role=2,final_reads=24,source_steps=6,
                   chart_symmetries=False,uniform_domain=False,full_joint_roots=True),
        user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m==make_manifest(),'covariance declaration drift')


renamed=algebra.renamed


def labels(d):
    nodes=[*(f'outside-{i}' for i in range(1,10)),'source-s']
    return ({n:f'node-{9-i:02d}' if d['relabel'] else n for i,n in enumerate(nodes)},
            {f'old-{i}':f'bond-{10-i:02d}' if d['relabel'] else f'old-{i}' for i in range(1,10)})


def transform(value,d):
    before=b.GeometryStageInputs.from_payload(value);graph=deepcopy(value['reference']['graph'])
    nodes,edges=labels(d);ni,ei,signs=d['node_order'],d['edge_order'],d['signs']
    b.require(sorted(ni)==list(range(10)) and sorted(ei)==list(range(9))
        and len(signs)==9 and all(x in (-1,1) for x in signs),'nonbijective transform')
    graph['live_node_ids']=[nodes[graph['live_node_ids'][i]] for i in ni]
    old=graph['edges'];graph['edges']=[]
    for i in ei:
        e=deepcopy(old[i]);e['edge_id']=edges[e['edge_id']]
        for end in ('tail','head'):e[end]['node_id']=nodes[e[end]['node_id']]
        if signs[i]<0:e['tail'],e['head']=e['head'],e['tail']
        graph['edges'].append(e)
    ref=r.oracle.reference(graph);h=value['H1_form']
    h=tuple(tuple(h[i][j]*signs[i]*signs[j] if h[i][j] else 0.0 for j in ei) for i in ei)
    states={role:b.GRCV4AuthoritativeState(tuple(value[role]['C'][i] for i in ni),
        tuple(value[role]['W_A'][i] for i in ei),None) for role in ROLES}
    return replace(before,geometry=b.GRCV4Geometry(ref,b.OneFormHodge(ref.graph,h)),**states).to_payload()


def transported_graph(graph, declaration, old_event, new_event):
    nodes,edges=labels(declaration);g=deepcopy(graph)
    rename=lambda x:renamed(x,nodes,edges,old_event,new_event)
    g['live_node_ids']=[rename(n) for n in g['live_node_ids']]
    for e in g['edges']:
        old=e['edge_id'];e['edge_id']=rename(old)
        for end in ('tail','head'):e[end]['node_id']=rename(e[end]['node_id'])
        if old in edges and declaration['signs'][int(old[4:])-1]<0:e['tail'],e['head']=e['head'],e['tail']
    g['live_node_ids'].sort(key=lambda n:(type(n)is str,b.canonical_json_bytes(n)))
    g['edges'].sort(key=lambda e:e['edge_id'].encode('utf-16-be'))
    return g


def mapping(base,other,declaration,old_event=None,new_event=None):
    """Explicit bijection plus endpoint-derived signs; partial transforms fail."""
    nodes,edges=labels(declaration);rename=lambda x:renamed(x,nodes,edges,old_event,new_event)
    bn,on=base['live_node_ids'],other['live_node_ids']
    b.require(set(map(rename,bn))==set(on) and len(bn)==len(on),'node bijection')
    ni=[bn.index(next(n for n in bn if rename(n)==x)) for x in on]
    be=base['edges'];by={rename(e['edge_id']):(i,e) for i,e in enumerate(be)}
    b.require(set(by)=={e['edge_id'] for e in other['edges']} and len(be)==len(other['edges']),'edge bijection')
    ei=[];sign=[]
    for e in other['edges']:
        i,old=by[e['edge_id']];ends=[dict(x,node_id=rename(x['node_id'])) for x in (old['tail'],old['head'])]
        b.require(e['kind']==old['kind'],'edge kind drift')
        if [e['tail'],e['head']]==ends:s=1
        elif [e['head'],e['tail']]==ends:s=-1
        else:raise ValueError('partial endpoint/port transform')
        expected_sign=declaration['signs'][int(old['edge_id'][4:])-1] if old['edge_id'] in edges else 1
        b.require(s==expected_sign,'unrequested orientation')
        ei.append(i);sign.append(s)
    return ni,ei,b.np.array(sign)


def backend(before):
    return r.native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph)


def check_root(before,value,*,numerics=False):
    return r.check_root(before,backend(before),value,numerics=numerics)


def check_step(before,value,*,numerics=False):
    return r.check_step(before,backend(before),value,numerics=numerics)


def expected_event(source,case,d):
    seed=r.state(source);ref=seed.inputs.geometry.reference
    nodes,_=labels(d);request=deepcopy(case['request'])
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id=nodes['source-s'],target_profile_template_id=aci_profile_template(ref).profile_template_id,
        history_policy=r.oracle.history_policy(b.authority_payload(seed.inputs.current),b.authority_payload(seed.inputs.reset)),
        operation_id='p984e-aci-'+str(request['target_effective_degree'])+'-'+d['kind'])
    identity=deepcopy(case['oracle']['event_identity'])
    for key in identity:
        if key in request and key!='schema_version':identity[key]=request[key]
    for channel in ('candidate','carrier'):
        key=channel+'_history_policy_digest';identity[key]=request['history_policy'][key]
    event='grc-event-sha256:'+b.digest(identity)
    graph=transported_graph(case['oracle']['target_graph'],d,case['oracle']['event_id'],event)
    target=r.independent_target(seed,dict(request=request,oracle=dict(event_id=event,target_graph=graph)))
    return request,identity,target.inputs


def execute_source(m,d):
    before=b.GeometryStageInputs.from_payload(transform(m['initial_inputs'],d))
    step,after=r.checked_step(before,backend(before))
    seed=replace(r.state(m['expected_source']),inputs=replace(after,dt=0))
    return dict(kind=d['kind'],step=step,state=seed.to_payload())


def execute_case(m,source,case,d):
    request,identity,expected=expected_event(source['state'],case,d)
    seed=r.state(source['state']);owner=r.native.GRC9V4ACIOperation(seed);before=owner.checkpoint()
    stale=deepcopy(request);stale['source_state_digest']='grcv4-state-sha256:'+'0'*64
    rejected=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejected.committed and owner.checkpoint()==before,'stale request rollback')
    owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(request))
    b.require(outcome.committed,'native event rejected: '+str(outcome.failure))
    b.require(owner.state.to_payload()==replace(seed,inputs=expected).to_payload(),'independent target mismatch')
    roles={}
    for role in ROLES:
        incoming=replace(owner.state.inputs,current=getattr(owner.state.inputs,role),dt=b.DT);steps=[]
        for _ in range(m['scope']['steps_per_role']):
            step,incoming=r.checked_step(incoming,backend(incoming));steps.append(step)
        roles[role]=dict(steps=steps,final=r.certified_root(r.CandidateCIRoot(replace(incoming,dt=0),backend(incoming))))
    return dict(layout=case['fixture_id'],kind=d['kind'],request=request,event_identity=identity,
        event_id='grc-event-sha256:'+b.digest(identity),event_committed=True,case_passed=True,
        event=event,roles=roles,stale_request_control=dict(committed=False,rollback_exact=True,
            failure=rejected.failure.to_payload()))


def execute_variant(job):
    m,d=job
    with b.exact_backend(b.ExactBackend.FLINT):
        source=execute_source(m,d)
        cases=[execute_case(m,source,c,d) for c in m['cases']]
    print(d['kind']+': both layouts passed',flush=True)
    return source,cases


def root_pair(base,other,indices,policy):
    _,ei,s=indices;errors=[]
    b.require(base['domain_id']==other['domain_id'] and base['recipe']==other['recipe'],'root contract covariance')
    for field in ('J','read_current','baseline','readback','flat','H','source','generated'):
        a=b.np.array(base[field]);expected=a[b.np.ix_(ei,ei)]*b.np.outer(s,s) if a.ndim==2 else a[ei]*s
        errors.append(b.comparison(other[field],expected,policy,'joint_covariance_'+field)['maximum_error'])
    errors.append(b.comparison(other['W_hat_A'],b.np.array(base['W_hat_A'])[ei],policy,'unsigned_W_hat_A')['maximum_error'])
    return max(errors)


def check(m,record,*,numerics=False):
    check_manifest(m);b.check_digest(record)
    b.require(record['schema']=='p984e-aci-results-v1' and record['manifest_digest']==m['record_digest']
              and record['user_accepted'] is False and record['aggregate_closed'] is False,'result scope')
    data=prior.previous.expand(record['execution']);sources=data['sources'];rows=data['cases'];policy=m['comparison']
    b.require([s['kind'] for s in sources]==list(KINDS),'source roster')
    b.require([(x['layout'],x['kind']) for x in rows]==[(c['fixture_id'],d['kind']) for c in m['cases'] for d in m['transforms']],'case roster')
    max_error=0.
    def states_pair(a,c,indices):
        nonlocal max_error
        for role in ROLES:
            max_error=max(max_error,b.comparison(c[role]['C'],b.np.array(a[role]['C'])[indices[0]],policy,'covariance_'+role+'_C')['maximum_error'])
            max_error=max(max_error,b.comparison(c[role]['W_A'],b.np.array(a[role]['W_A'])[indices[1]],policy,'unsigned_W_A')['maximum_error'])
            b.require(c[role]['Z_4'] is None,'carrier leakage')
    def roots_pair(a,c,indices):
        nonlocal max_error
        max_error=max(max_error,root_pair(a,c,indices,policy))
    def writer_pair(a,c,indices):
        nonlocal max_error
        ni,ei,sign=indices
        for key,order,multiplier in (('C',ni,1),('W_A',ei,1),('J',ei,sign),('target',ei,1)):
            max_error=max(max_error,b.comparison(c[key],b.np.array(a[key])[order]*multiplier,
                policy,'writer_covariance_'+key)['maximum_error'])
    with nullcontext():
        for source,d in zip(sources,m['transforms'],strict=True):
            before=b.GeometryStageInputs.from_payload(transform(m['initial_inputs'],d))
            after=check_step(before,source['step'],numerics=numerics)
            b.require(replace(r.state(m['expected_source']),inputs=replace(after,dt=0)).to_payload()==source['state'],'source/poststate/specialization substitution')
            indices=mapping(m['initial_inputs']['reference']['graph'],before.geometry.reference.graph.to_payload(),d)
            states_pair(sources[0]['state']['inputs'],source['state']['inputs'],indices)
            for key in ('root','reset_root','restart'):roots_pair(sources[0]['step'][key],source['step'][key],indices)
            writer_pair(sources[0]['step']['writer_targets'][0],source['step']['writer_targets'][0],indices)
        for case in m['cases']:
            base=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']=='base')
            for d,source in zip(m['transforms'],sources,strict=True):
                row=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']==d['kind'])
                request,identity,expected=expected_event(source['state'],case,d)
                b.require(row['request']==request and row['event_identity']==identity
                    and row['event_id']=='grc-event-sha256:'+b.digest(identity),'event/request binding')
                b.require(row['event_committed'] is True and row['case_passed'] is True,'incomplete event')
                seed=r.state(source['state'])
                bound=dict(request=request,oracle=dict(event_id=row['event_id'],target_graph=expected.geometry.reference.graph.to_payload()))
                target=r.check_event(seed,bound,row['event'],numerics=numerics)
                control=row['stale_request_control']
                b.require(control['committed'] is False and control['rollback_exact'] is True and bool(control['failure']),'missing stale request control')
                b.require(set(row['roles'])==set(ROLES),'role coverage')
                bg=base['event']['actual_target']['inputs']['reference']['graph'];tg=target.inputs.geometry.reference.graph.to_payload()
                b.require(transported_graph(bg,d,base['event_id'],row['event_id'])==tg,'normalized target graph')
                indices=mapping(bg,tg,d,base['event_id'],row['event_id'])
                states_pair(base['event']['actual_target']['inputs'],target.inputs.to_payload(),indices)
                source_indices=mapping(m['initial_inputs']['reference']['graph'],seed.inputs.geometry.reference.graph.to_payload(),d)
                for key in ('root','reset_root'):
                    roots_pair(base['event']['admission_reads'][0][key],row['event']['admission_reads'][0][key],source_indices)
                for k in range(4):
                    writer_pair(base['event']['writer_surfaces'][k],row['event']['writer_surfaces'][k],
                        source_indices if k<2 else indices)
                for key in ('root','reset_root'):
                    roots_pair(base['event']['admission_reads'][1][key],row['event']['admission_reads'][1][key],indices)
                for role in ROLES:
                    rr=row['roles'][role];br=base['roles'][role];incoming=replace(target.inputs,current=getattr(target.inputs,role),dt=b.DT)
                    b.require(len(rr['steps'])==2,'continuation horizon')
                    for k,step in enumerate(rr['steps']):
                        incoming=check_step(incoming,step,numerics=numerics)
                        states_pair(br['steps'][k]['poststate'],step['poststate'],indices)
                        writer_pair(br['steps'][k]['writer_targets'][0],step['writer_targets'][0],indices)
                        for key in ('root','reset_root','restart'):roots_pair(br['steps'][k][key],step[key],indices)
                    check_root(replace(incoming,dt=0),rr['final'],numerics=numerics)
                    roots_pair(br['final'],rr['final'],indices)
    return dict(family='A_CI',status='executed_pending_review',required_cells=20,passing_pending_cells=20,
        accepted_cells=0,native_events=12,target_steps=48,source_steps=6,final_reads=24,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[52,94],full_joint_roots=True,
        unsigned_candidate_history=True,
        native_trajectories_rerun=False,interval_certificates_rerun=numerics,uniform_domain=False,aggregate_closed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':b.write_new(INPUTS,make_manifest());return
    m=b.read(INPUTS);check_manifest(m)
    if args.mode=='check':
        with ExitStack() as stack:
            for module,name in ((r,'ProvisionalCandidateCIStep'),(r,'CandidateCIRoot'),(r.native,'GRC9V4ACIOperation')):
                stack.enter_context(patch.object(module,name,side_effect=AssertionError('native producer forbidden')))
            print(json.dumps(check(m,b.read(RESULTS),numerics=args.recheck_numerics),indent=2))
        return
    b.require(not (b.ROOT/RESULTS).exists(),'refuse overwrite')
    with ProcessPoolExecutor(max_workers=4) as pool:
        outputs=list(pool.map(execute_variant,[(m,d) for d in m['transforms']]))
    sources=[v[0] for v in outputs]
    rows=[v[1][i] for i in range(len(m['cases'])) for v in outputs]
    record=b.seal(dict(schema='p984e-aci-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),user_accepted=False,aggregate_closed=False))
    summary=check(m,record);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
