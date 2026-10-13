"""Bounded native C_OS covariance; retained check never executes producers."""

import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

import p984d_cos as prior
from pygrc.models.grc_9_v4_expansion import cos_profile_template

b, consumer = prior.b, prior.consumer
SELF = b.HERE + 'p984e_cos.py'
TEST = b.HERE + 'test_p984e_cos.py'
PLAN = b.BASE + 'P9-8.4e-COSPlan.md'
INPUTS = b.BASE + 'P9-8.4e-COSInputs.json'
RESULTS = b.BASE + 'P9-8.4e-COSResults.json'
REVIEW = b.BASE + 'P9-8.4e-COSReview.md'
KINDS = ('base', 'edge_order', 'node_order', 'relabel', 'signed', 'combined')
ROLES = ('current', 'reset')


def declarations():
    frozen = b.read(b.VECTORS)['grc9_metamorphic_vectors'][0]
    b.require(frozen['kind'] == 'source_edge_input_order_permutation', 'frozen vector kind')
    order = [int(e['edge_id'].split('-')[1])-1 for e in frozen['input']['permuted_source_graph']['edges']]
    return [dict(kind=k, node_order=list(reversed(range(10))) if k in ('node_order','combined') else list(range(10)),
                 edge_order=order if k in ('edge_order','combined') else list(range(9)),
                 signs=[-1 if k in ('signed','combined') and i % 2 == 0 else 1 for i in range(9)],
                 relabel=k in ('relabel','combined')) for k in KINDS]


def labels(declaration):
    nodes=['s',*range(1,10)]
    return ({n: f'node-{9-i:02d}' if declaration['relabel'] else n for i,n in enumerate(nodes)},
            {f'e{i}': f'bond-{10-i:02d}' if declaration['relabel'] else f'e{i}' for i in range(1,10)})


def reidentify(reference):
    p=reference['profile']['params_resolved'];identity=reference['profile']['identity_payload']
    p['candidate']['W_C_tr_content_digest']=b.payload_identity('wctr_identity_payload',
        dict(schema_version='grcv4-wctr-identity-v1',W_C_tr=p['candidate']['W_C_tr']))
    p['geometry']['reference_hodge_digest']=b.payload_identity('reference_hodge_identity_payload',reference['reference_hodge'])
    p['geometry']['K4_base_digest']=b.payload_identity('k4_identity_payload',
        dict(schema_version='grcv4-k4-identity-v1',K4_base=reference['K4_base']))
    identity['params_hash']=b.payload_identity('resolved_params',p)
    reference['profile']=b.resolve_profile(p,identity).to_payload()


def transform(inputs, declaration):
    """Declared P/S transport, independent of production graph/OS algorithms."""
    value=deepcopy(inputs);ref=value['reference'];graph=ref['graph'];nodes,edges=labels(declaration)
    ni,ei=declaration['node_order'],declaration['edge_order'];signs=declaration['signs']
    b.require(sorted(ni)==list(range(10)) and sorted(ei)==list(range(9))
              and len(signs)==9 and all(s in (-1,1) for s in signs),'nonbijective transform')
    graph['live_node_ids']=[nodes[graph['live_node_ids'][i]] for i in ni]
    old=graph['edges'];graph['edges']=[]
    for i in ei:
        e=deepcopy(old[i]);e['edge_id']=edges[e['edge_id']]
        for end in ('tail','head'):e[end]['node_id']=nodes[e[end]['node_id']]
        if signs[i]<0:e['tail'],e['head']=e['head'],e['tail']
        graph['edges'].append(e)
    for role in ROLES:
        state=value[role];state['C']=[state['C'][i] for i in ni]
        b.require(state['W_A'] is None and state['Z_4'] is None,'not C_OS')
    for field in ('K4_base',):
        a=ref[field];ref[field]=[[a[i][j]*signs[i]*signs[j] if a[i][j] else 0.0 for j in ei] for i in ei]
    a=value['H1_form'];value['H1_form']=[[a[i][j]*signs[i]*signs[j] if a[i][j] else 0.0 for j in ei] for i in ei]
    for mapping in (ref['reference_hodge']['edge_weights'],ref['profile']['params_resolved']['candidate']['W_C_tr']):
        items=list(mapping.items());mapping.clear();mapping.update({edges[k]:v for k,v in items})
    reidentify(ref)
    return materialize(inputs,value).to_payload()


def materialize(original,value):
    ref=b.GRCV4ReferenceGeometry.from_payload(value['reference'])
    original=deepcopy(original)
    # Original wire authority remains strict; changed authority is constructed
    # explicitly and receives fresh derived identities, never patched digests.
    prototype=b.GeometryStageInputs.from_payload(original)
    return replace(prototype,geometry=b.GRCV4Geometry(ref,b.OneFormHodge(ref.graph,tuple(map(tuple,value['H1_form'])))),
        current=b.GRCV4AuthoritativeState(tuple(value['current']['C']),None,None),
        reset=b.GRCV4AuthoritativeState(tuple(value['reset']['C']),None,None),
        operation_id=value['operation_id'],dt=value['dt'])


def authority():
    side=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool'
    if str(side/'tool/src') not in b.sys.path:b.sys.path.insert(0,str(side/'tool/src'))
    from grcv4_explorer.successor import load_successor_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    ctx=load_successor_forensic_context(b.ROOT,side)
    return {k:contract_provenance(ctx,k) for k in ('D11-G9-EC-PORT-PLAN-DETERMINISM',
        'D11-G9-EC-EXACT-OLD-PORT-MAP','D11-G9-EC-LIFECYCLE-READMISSION')}


def make_manifest():
    deep=b.read(prior.INPUTS);phase=b.read(consumer.INPUTS)
    b.check_digest(deep);b.check_bindings(deep['source_bindings'])
    b.check_digest(phase);b.check_bindings(phase['source_bindings'])
    b.require(deep['initial_inputs']==phase['initial_inputs'],'different predecessor sources')
    cases=[next(c for c in phase['cases'] if c['request']['module_chirality']==1),
           next(c for c in deep['cases'] if c['request']['target_effective_degree']==94
                and c['request']['module_chirality']==-1 and c['request']['growth_phase']==3)]
    traces=authority()
    paths={SELF,TEST,PLAN,prior.INPUTS,prior.REVIEW,consumer.INPUTS,b.VECTORS,
           consumer.SELF,b.SELF,prior.previous.SELF,
           'src/pygrc/models/grc_9_v4_lifecycle.py','src/pygrc/models/grc_9_v4_expansion.py'}
    paths|={r['path'] for r in deep['source_bindings']}|{r['path'] for r in phase['source_bindings']}
    paths|={r['source_ref']['path'] for t in traces.values() for r in t['rows']}
    return b.seal(dict(schema='p984e-cos-inputs-v1',family='C_OS',source_bindings=b.bind(paths),
        initial_inputs=deep['initial_inputs'],expected_source=deep['expected_source'],cases=cases,
        transforms=declarations(),authority=traces,comparison=deep['cases'][0]['comparison'],
        scope=dict(layouts=2,transforms=5,required_history_cells=20,native_events=12,
                   target_steps=48,steps_per_role=2,final_reads=24,source_steps=6,
                   chart_symmetries=False,uniform_domain=False),user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m==make_manifest(),'covariance declaration drift')


def renamed(value, nodes, edges, old_event=None, new_event=None):
    if isinstance(value,str) and old_event and value.startswith(old_event+'/'):
        return new_event+value[len(old_event):]
    return nodes.get(value,edges.get(value,value))


def transported_graph(graph, declaration, old_event, new_event):
    nodes,edges=labels(declaration);g=deepcopy(graph)
    rename=lambda x:renamed(x,nodes,edges,old_event,new_event)
    g['live_node_ids']=[rename(n) for n in g['live_node_ids']]
    for e in g['edges']:
        old=e['edge_id'];e['edge_id']=rename(old)
        for end in ('tail','head'):e[end]['node_id']=rename(e[end]['node_id'])
        if old in edges and declaration['signs'][int(old[1:])-1]<0:e['tail'],e['head']=e['head'],e['tail']
    g['live_node_ids'].sort(key=lambda n:(type(n)is str,b.canonical_json_bytes(n)))
    g['edges'].sort(key=lambda e:e['edge_id'].encode('utf-16-be'))
    return g


def expected_event(source, case, declaration):
    inputs=b.GeometryStageInputs.from_payload(source['inputs']);ref=inputs.geometry.reference
    spec=source['specialization'];specialization=b.native.GRC9V4Specialization(b.FrozenJSONMap(spec['resolved']),b.FrozenJSONMap(spec['identity_payload']))
    seed=b.native.GRC9V4COSState(inputs,specialization)
    nodes,_=labels(declaration);request=deepcopy(case['request'])
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id=nodes['s'],target_profile_template_id=cos_profile_template(ref).profile_template_id,
        operation_id='p984e-'+str(request['target_effective_degree'])+'-'+declaration['kind'])
    identity=deepcopy(case['oracle']['event_identity'])
    for key in identity:
        if key in request and key!='schema_version':identity[key]=request[key]
    event='grc-event-sha256:'+b.digest(identity)
    graph=transported_graph(case['oracle']['target_graph'],declaration,case['oracle']['event_id'],event)
    # Independent target construction uses the declared graph, not the allocator result.
    p=deepcopy(source['inputs']);r=p['reference'];r['graph']=graph
    weights={e['edge_id']:1 for e in graph['edges']};size=len(weights)
    r['K4_base']=[[0.0]*size for _ in range(size)]
    r['reference_hodge']['edge_weights']=weights.copy()
    r['profile']['params_resolved']['candidate']['W_C_tr']=weights.copy();reidentify(r)
    p['H1_form']=[[float(i==j) for j in range(size)] for i in range(size)]
    for role in ROLES:
        old=dict(zip(ref.graph.live_node_ids,p[role]['C'],strict=True));image={n:old.get(n,0.) for n in graph['live_node_ids']}
        for j,share in enumerate(request['resource_distribution'],1):
            image[event+f'/satellite/{j}']=float(b.Fraction(old[nodes['s']])*b.Fraction(share))
        p[role]['C']=[image[n] for n in graph['live_node_ids']]
    p.update(dt=0,operation_id=request['operation_id'])
    return request,identity,materialize(source['inputs'],p)


def execute_source(m, declaration):
    before=b.GeometryStageInputs.from_payload(transform(m['initial_inputs'],declaration))
    step=b.ProvisionalCandidateCOSStep(before)
    spec=m['expected_source']['specialization']
    specialization=b.native.GRC9V4Specialization(b.FrozenJSONMap(spec['resolved']),b.FrozenJSONMap(spec['identity_payload']))
    seed=b.native.GRC9V4COSState(replace(step.next_inputs,dt=0),specialization)
    return dict(kind=declaration['kind'],step=consumer.step_capture(step),state=seed.to_payload())


def state_from_payload(value):
    spec=value['specialization']
    return b.native.GRC9V4COSState(b.GeometryStageInputs.from_payload(value['inputs']),
        b.native.GRC9V4Specialization(b.FrozenJSONMap(spec['resolved']),b.FrozenJSONMap(spec['identity_payload'])))


def execute_case(m,source,case,declaration):
    request,identity,expected=expected_event(source['state'],case,declaration)
    seed=state_from_payload(source['state'])
    owner=b.native.GRC9V4COSOperation(seed);before=owner.checkpoint();reads=[]
    stale=deepcopy(request);stale['source_state_digest']='grcv4-state-sha256:'+'0'*64
    rejected=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejected.committed and owner.checkpoint()==before,'stale request failed rollback')
    def observe(operand):
        passed=b.CandidateCOSPass(operand)
        reads.append(dict(pass_capture=consumer.pass_capture(passed),published=owner.state.scientific_digest))
        return passed
    with patch.object(b.native,'CandidateCOSPass',observe):
        outcome=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(request))
    b.require(outcome.committed,'native event rejected: '+str(outcome.failure))
    actual=owner.state.inputs
    b.require(actual.geometry.reference.to_payload()==expected.geometry.reference.to_payload() and actual.current==expected.current
              and actual.reset==expected.reset,'independent target mismatch')
    b.require(b.native.GRC9V4COSOperation.replay(owner.checkpoint()).checkpoint()==owner.checkpoint(),'event replay')
    roles={}
    for role in ROLES:
        incoming=replace(actual,current=getattr(actual,role),dt=b.DT);steps=[]
        for _ in range(m['scope']['steps_per_role']):
            step=b.ProvisionalCandidateCOSStep(incoming);steps.append(consumer.step_capture(step));incoming=step.next_inputs
        roles[role]=dict(steps=steps,final=consumer.pass_capture(b.CandidateCOSPass(incoming)))
    return dict(layout=case['fixture_id'],kind=declaration['kind'],request=request,event_identity=identity,
                event_id='grc-event-sha256:'+b.digest(identity),event_committed=True,case_passed=True,
                source_digest=seed.scientific_digest,target=owner.state.to_payload(),admission=reads,
                roles=roles,replay_exact=True,prestate_checkpoint_digest=b.sha(before),
                stale_request_control=dict(committed=False,rollback_exact=True,failure=rejected.failure.to_payload()))


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
        expected_sign=declaration['signs'][int(old['edge_id'][1:])-1] if old['edge_id'] in edges else 1
        b.require(s==expected_sign,'unrequested orientation')
        ei.append(i);sign.append(s)
    return ni,ei,b.np.array(sign)


def numeric_pair(base,other,declaration,policy,old_event=None,new_event=None):
    ni,ei,s=mapping(base['inputs']['reference']['graph'],other['inputs']['reference']['graph'],declaration,old_event,new_event)
    errors=[]
    def cmp(a,e,name):errors.append(b.comparison(a,e,policy,name)['maximum_error'])
    for role in ROLES:cmp(other['inputs'][role]['C'],b.np.array(base['inputs'][role]['C'])[ni],'covariance_'+role+'_C')
    for stage in ('predictor','corrector'):
        for field in ('current','read_flux','causal_flat'):
            cmp(other[stage][field],b.np.array(base[stage][field])[ei]*s,'covariance_'+stage+'_'+field)
        h=b.np.array(base[stage]['descriptor']['inputs']['H1_form'])
        cmp(other[stage]['descriptor']['inputs']['H1_form'],h[b.np.ix_(ei,ei)]*b.np.outer(s,s),'covariance_'+stage+'_H')
    return max(errors)


def check(m,record,*,numerics=False):
    check_manifest(m);b.check_digest(record)
    b.require(record['schema']=='p984e-cos-results-v1' and record['manifest_digest']==m['record_digest']
              and record['user_accepted'] is False and record['aggregate_closed'] is False,'result scope')
    data=prior.previous.expand(record['execution']);sources=data['sources'];rows=data['cases'];policy=m['comparison']
    b.require([s['kind'] for s in sources]==list(KINDS),'source roster')
    b.require([(r['layout'],r['kind']) for r in rows]==[(c['fixture_id'],d['kind']) for c in m['cases'] for d in m['transforms']], 'case roster')
    for source,d in zip(sources,m['transforms'],strict=True):
        b.require(source['step']['pass']['inputs']==transform(m['initial_inputs'],d),'source transform')
        after=deepcopy(source['step']['poststate']);after['dt']=0
        b.require(after==source['state']['inputs'],'source poststate substitution')
        if numerics:consumer.check_step(source['step'],policy)
    max_error=0.
    for case in m['cases']:
        base=next(r for r in rows if r['layout']==case['fixture_id'] and r['kind']=='base')
        for d,source in zip(m['transforms'],sources,strict=True):
            row=next(r for r in rows if r['layout']==case['fixture_id'] and r['kind']==d['kind'])
            request,identity,expected=expected_event(source['state'],case,d)
            b.require(row['request']==request and row['event_identity']==identity
                      and row['event_id']=='grc-event-sha256:'+b.digest(identity),'event/request binding')
            target=b.GeometryStageInputs.from_payload(row['target']['inputs'])
            b.require(target.geometry.reference.to_payload()==expected.geometry.reference.to_payload() and target.current==expected.current
                      and target.reset==expected.reset,'independent transferred state')
            b.require(row['event_committed'] is True and row['case_passed'] is True and row['replay_exact'] is True,'incomplete event')
            g=transported_graph(base['target']['inputs']['reference']['graph'],d,base['event_id'],row['event_id'])
            b.require(g==row['target']['inputs']['reference']['graph'],'exact normalized target graph')
            b.require(set(row['roles'])==set(ROLES) and len(row['admission'])==4,'both-role coverage')
            seed=state_from_payload(source['state'])
            b.require(row['source_digest']==seed.scientific_digest,'source identity')
            control=row['stale_request_control']
            b.require(control['committed'] is False and control['rollback_exact'] is True and bool(control['failure']),'missing stale request control')
            for n,admission in enumerate(row['admission']):
                inp=seed.inputs if n<2 else target;role=ROLES[n%2]
                b.require(admission['published']==seed.scientific_digest
                          and admission['pass_capture']['inputs']==replace(inp,current=getattr(inp,role),dt=1).to_payload(),
                          'admission role/stage/atomicity')
                if numerics:consumer.check_pass(admission['pass_capture'],policy)
            for role in ROLES:
                rr=row['roles'][role];br=base['roles'][role]
                b.require(len(rr['steps'])==2,'continuation horizon')
                incoming=replace(target,current=getattr(target,role),dt=b.DT)
                oracle=replace(expected,current=getattr(expected,role),dt=b.DT)
                for k,step in enumerate(rr['steps']):
                    b.require(step['pass']['inputs']==incoming.to_payload(),'continuation chain')
                    if numerics:
                        _,post=consumer.check_step(step,policy);dense=b.dense_os(oracle)
                        b.comparison(post.current.C,dense['C'],policy,'independent_trajectory_C')
                        oracle=replace(oracle,current=b.GRCV4AuthoritativeState(tuple(dense['C']),None,None),time=oracle.time+b.DT,step_index=oracle.step_index+1)
                    incoming=b.GeometryStageInputs.from_payload(step['poststate'])
                    b.require(incoming.reset==target.reset and incoming.current.W_A is None and incoming.current.Z_4 is None,'history leakage')
                    max_error=max(max_error,numeric_pair(br['steps'][k]['pass'],step['pass'],d,policy,base['event_id'],row['event_id']))
                b.require(rr['final']['inputs']==incoming.to_payload(),'fresh final operand')
                if numerics:consumer.check_pass(rr['final'],policy)
                max_error=max(max_error,numeric_pair(br['final'],rr['final'],d,policy,base['event_id'],row['event_id']))
    for source,d in zip(sources,m['transforms'],strict=True):
        max_error=max(max_error,numeric_pair(sources[0]['step']['pass'],source['step']['pass'],d,policy))
    return dict(family='C_OS',status='executed_pending_review',required_cells=20,passing_pending_cells=20,
        accepted_cells=0,native_events=12,target_steps=48,source_steps=6,final_reads=24,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[52,94],
        native_trajectories_rerun=False,dense_comparisons_rerun=numerics,uniform_domain=False,
        aggregate_closed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':b.write_new(INPUTS,make_manifest());return
    m=b.read(INPUTS);check_manifest(m)
    if args.mode=='check':
        with ExitStack() as stack:
            for module,name in ((b,'ProvisionalCandidateCOSStep'),(b,'CandidateCOSPass'),(b.native,'GRC9V4COSOperation')):
                stack.enter_context(patch.object(module,name,side_effect=AssertionError('native producer forbidden')))
            print(json.dumps(check(m,b.read(RESULTS),numerics=args.recheck_numerics),indent=2))
        return
    b.require(not (b.ROOT/RESULTS).exists(),'refuse overwrite')
    with b.exact_backend(b.ExactBackend.FLINT):
        sources=[execute_source(m,d) for d in m['transforms']];rows=[]
        for case in m['cases']:
            for source,d in zip(sources,m['transforms'],strict=True):
                rows.append(execute_case(m,source,case,d));print(case['fixture_id'],d['kind'],'passed',flush=True)
    record=b.seal(dict(schema='p984e-cos-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),user_accepted=False,aggregate_closed=False))
    summary=check(m,record,numerics=True);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
