"""C_OS full chart rotation/reflection with independent role normalization.

Exact frozen plans are separate from numerical native counterparts.
"""

import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

import p984d_cos as prior
import p984e_cos as ordering
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionPlan, GRC9ExpansionPolicy
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_9_v4_expansion import cos_profile_template

b, consumer = prior.b, prior.consumer
SELF = b.HERE + 'p984f_cos.py'
TEST = b.HERE + 'test_p984f_cos.py'
PLAN = b.BASE + 'P9-8.4f-COSPlan.md'
INPUTS = b.BASE + 'P9-8.4f-COSInputs.json'
RESULTS = b.BASE + 'P9-8.4f-COSResults.json'
REVIEW = b.BASE + 'P9-8.4f-COSReview.md'
KINDS = ('base', 'rotate', 'rotate_twice', 'reflect')
NORMALIZATION = 'grc9v4-event-namespace-and-role-covariance-normalization-v1'
ROLES = ('current', 'reset')


def declarations():
    values=[]
    for kind in KINDS:
        rotation={'base':0,'rotate':1,'rotate_twice':2,'reflect':0}[kind]
        branch=lambda x:4-x if kind=='reflect' else 1+(x-1+rotation)%3
        ports={str(p):branch(1+(p-1)%3)+3*(branch(1+(p-1)//3)-1) for p in range(1,10)}
        values.append(dict(kind=kind,ports=ports,branches={str(i):branch(i) for i in (1,2,3)},
            chirality_factor=-1 if kind=='reflect' else 1,normalization_policy_id=NORMALIZATION))
    frozen=b.read(b.VECTORS)['grc9_metamorphic_vectors'][1:]
    for d,v in zip((values[1],values[3]),frozen,strict=True):
        b.require(d['ports']==v['input']['port_permutation'] and d['branches']==v['input']['branch_permutation']
            and v['normalization_policy_id']==NORMALIZATION,'frozen full-chart generator drift')
    return values


def validate_transform(d):
    b.require(d in declarations(),'partial or foreign chart transformation')


def label(value,d,old_event=None,new_event=None):
    if isinstance(value,str) and old_event and value.startswith(old_event+'/'):
        parts=value[len(old_event)+1:].split('/')
        # Branch index, never an extra-node ordinal.
        offset=1 if parts[0] in ('satellite','extra') else (2 if parts[:2]==['internal','extra'] else 1)
        if parts[0]!='core':parts[offset]=str(d['branches'][parts[offset]])
        return new_event+'/'+ '/'.join(parts)
    if type(value) is int:return d['ports'][str(value)]
    if value in ('s','source-s'):return value
    if isinstance(value,str):
        if value.startswith('e') and value[1:].isdigit():return 'e'+str(d['ports'][value[1:]])
        for stem in ('old-','outside-'):
            if value.startswith(stem):return stem+str(d['ports'][value[len(stem):]])
    raise ValueError('unrecognized chart role')


def transported_graph(graph,d,old_event=None,new_event=None):
    validate_transform(d);g=deepcopy(graph)
    g['live_node_ids']=[label(n,d,old_event,new_event) for n in g['live_node_ids']]
    for e in g['edges']:
        e['edge_id']=label(e['edge_id'],d,old_event,new_event)
        for end in ('tail','head'):
            e[end]['node_id']=label(e[end]['node_id'],d,old_event,new_event)
            e[end]['port']=d['ports'][str(e[end]['port'])]
    g['live_node_ids'].sort(key=lambda n:(type(n)is str,b.canonical_json_bytes(n)))
    g['edges'].sort(key=lambda e:e['edge_id'].encode('utf-16-be'))
    return g


def frozen_pairs(*,execute=False):
    bundle=b.read(b.VECTORS);fixtures={x['fixture_id']:x for x in bundle['grc9_expansion_vectors']}
    rows=[];ds=declarations()
    for v,d in zip(bundle['grc9_metamorphic_vectors'][1:],(ds[1],ds[3]),strict=True):
        pair=[fixtures[v[k]] for k in ('base_vector_id','expected_target_vector_id')]
        graphs=[dict(schema_version='grc9v4-port-graph-v1',live_node_ids=f['expected']['target_live_node_ids'],
            edges=f['expected']['target_edges']) for f in pair]
        events=[f['expected']['event_id'] for f in pair]
        b.require(transported_graph(graphs[0],d,*events)==graphs[1],'frozen normalized graph mismatch')
        b.require(pair[1]['request']['module_chirality']==pair[0]['request']['module_chirality']*d['chirality_factor']
            and pair[1]['request']['growth_phase']==d['branches'][str(pair[0]['request']['growth_phase'])],
            'frozen phase/chirality mismatch')
        if execute:
            source=GRC9V4PortGraph.from_payload(bundle['port_graph_envelope_vectors'][0]['payload'])
            policy=GRC9ExpansionPolicy.from_payload(next(x['payload']['policy'] for x in bundle['subdigest_identity_vectors']
                if x['vector_id']=='SUBDIGEST-GRC9-EXPANSION-POLICY'))
            for f,g,event in zip(pair,graphs,events,strict=True):
                q=dict(f['request'],schema_version='grc9v4-expansion-event-request-input-v1',
                       expected_event_id=None,expected_target_graph_digest=None)
                request=b.GRC9V4ExpansionRequestInput.from_payload(q)
                actual=GRC9V4ExpansionPlan(source,request.source_state_digest,request,policy)
                b.require(actual.target_graph.to_payload()==g and actual.event_id==event,'frozen native plan mismatch')
        rows.append(dict(vector_id=v['vector_id'],base_vector_id=v['base_vector_id'],target_vector_id=v['expected_target_vector_id'],
            normalization_policy_id=NORMALIZATION,base_graph=graphs[0],target_graph=graphs[1],event_ids=events))
    return rows


def reidentify(reference):
    p=reference['profile']['params_resolved'];identity=reference['profile']['identity_payload']
    p['candidate']['W_C_tr_content_digest']=b.payload_identity('wctr_identity_payload',
        dict(schema_version='grcv4-wctr-identity-v1',W_C_tr=p['candidate']['W_C_tr']))
    p['geometry']['reference_hodge_digest']=b.payload_identity('reference_hodge_identity_payload',reference['reference_hodge'])
    p['geometry']['K4_base_digest']=b.payload_identity('k4_identity_payload',
        dict(schema_version='grcv4-k4-identity-v1',K4_base=reference['K4_base']))
    identity['params_hash']=b.payload_identity('resolved_params',p)
    reference['profile']=b.resolve_profile(p,identity).to_payload()


def transform(inputs,d):
    validate_transform(d)
    if d['kind']=='base':return deepcopy(inputs)
    p=deepcopy(inputs);old=p['reference']['graph'];g=transported_graph(old,d)
    # Keep the declared source-node-first convention, with sorted external labels.
    g['live_node_ids']=['s',*range(1,10)]
    ni,ei,_=mapping(old,g,d)
    for role in ROLES:
        b.require(p[role]['W_A'] is None and p[role]['Z_4'] is None,'not C_OS')
        p[role]['C']=[p[role]['C'][i] for i in ni]
    ref=p['reference'];ref['graph']=g
    for owner,key in ((ref,'K4_base'),(p,'H1_form')):
        h=owner[key];owner[key]=[[h[i][j] for j in ei] for i in ei]
    for weights in (ref['reference_hodge']['edge_weights'],ref['profile']['params_resolved']['candidate']['W_C_tr']):
        items=list(weights.items());weights.clear();weights.update({label(k,d):v for k,v in items})
    reidentify(ref)
    return materialize(inputs,p).to_payload()


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
    phase=b.read(consumer.INPUTS);old=b.read(b.INPUTS)
    for m in (phase,old):b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(phase['initial_inputs']==old['initial_inputs'],'predecessor source mismatch')
    cases=[next(c for c in old['cases'] if c['request']['target_effective_degree']==45 and c['request']['module_chirality']==ch)
        for ch in (1,-1)] + [next(c for c in phase['cases'] if c['request']['module_chirality']==ch) for ch in (1,-1)]
    traces=authority();paths={SELF,TEST,PLAN,ordering.SELF,ordering.REVIEW,b.INPUTS,consumer.INPUTS,b.VECTORS,
        consumer.SELF,b.SELF,prior.previous.SELF,'specs/grc-9-v4-spec.md'}
    paths|={r['path'] for m in (phase,old) for r in m['source_bindings']}
    paths|={r['source_ref']['path'] for t in traces.values() for r in t['rows']}
    return b.seal(dict(schema='p984f-cos-inputs-v1',family='C_OS',source_bindings=b.bind(paths),
        initial_inputs=phase['initial_inputs'],expected_source=phase['expected_source'],cases=cases,
        transforms=declarations(),frozen_pairs=frozen_pairs(),authority=traces,comparison=cases[0]['comparison'],
        scope=dict(layouts=4,transforms=3,required_history_cells=24,native_events=16,
            target_steps=64,steps_per_role=2,final_reads=32,source_steps=4,frozen_plan_executions=4,
            chart_symmetries=True,uniform_domain=False),user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m==make_manifest(),'covariance declaration drift')


def expected_event(source, case, declaration):
    inputs=b.GeometryStageInputs.from_payload(source['inputs']);ref=inputs.geometry.reference
    spec=source['specialization'];specialization=b.native.GRC9V4Specialization(b.FrozenJSONMap(spec['resolved']),b.FrozenJSONMap(spec['identity_payload']))
    seed=b.native.GRC9V4COSState(inputs,specialization)
    request=deepcopy(case['request']);branch=declaration['branches']
    shares=request['resource_distribution'];mapped=[0.]*3
    for i,x in enumerate(shares,1):mapped[branch[str(i)]-1]=x
    request.update(module_chirality=request['module_chirality']*declaration['chirality_factor'],
        growth_phase=None if request['growth_phase'] is None else branch[str(request['growth_phase'])],
        resource_distribution=mapped)
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id='s',target_profile_template_id=cos_profile_template(ref).profile_template_id,
        operation_id='p984f-'+case['fixture_id']+'-'+declaration['kind'])
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
            image[event+f'/satellite/{j}']=float(b.Fraction(old['s'])*b.Fraction(share))
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
    semantic=[]
    for field,bad_value in (('module_chirality',None),
            ('growth_phase',1 if request['growth_phase'] is None else None)):
        wrong=deepcopy(request);wrong[field]=bad_value
        result=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(wrong))
        b.require(not result.committed and owner.checkpoint()==before,'chart semantic rejection rollback')
        semantic.append(dict(field=field,value=bad_value,committed=False,rollback_exact=True,
            failure=result.failure.to_payload()))
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
                stale_request_control=dict(committed=False,rollback_exact=True,failure=rejected.failure.to_payload()),
                semantic_controls=semantic)


def mapping(base,other,d,old_event=None,new_event=None):
    validate_transform(d);rename=lambda x:label(x,d,old_event,new_event)
    bn,on=base['live_node_ids'],other['live_node_ids']
    b.require(set(map(rename,bn))==set(on) and len(bn)==len(on),'node bijection')
    ni=[bn.index(next(n for n in bn if rename(n)==x)) for x in on]
    by={rename(e['edge_id']):(i,e) for i,e in enumerate(base['edges'])}
    b.require(set(by)=={e['edge_id'] for e in other['edges']} and len(by)==len(other['edges']),'edge bijection')
    ei=[]
    for e in other['edges']:
        i,old=by[e['edge_id']];expected=deepcopy(old);expected['edge_id']=rename(old['edge_id'])
        for end in ('tail','head'):
            expected[end]=dict(node_id=rename(old[end]['node_id']),port=d['ports'][str(old[end]['port'])])
        b.require(e==expected,'partial chart/role/port transport');ei.append(i)
    return ni,ei,b.np.ones(len(ei))


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
    b.require(record['schema']=='p984f-cos-results-v1' and record['manifest_digest']==m['record_digest']
              and record['user_accepted'] is False and record['aggregate_closed'] is False
              and record['frozen_plan_execution']==dict(pairs=m['frozen_pairs'],plans_executed=4,numerical_events=0),'result scope')
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
            controls=row['semantic_controls']
            b.require([(x['field'],x['value']) for x in controls]==[('module_chirality',None),
                ('growth_phase',1 if request['growth_phase'] is None else None)]
                and all(x['committed'] is False and x['rollback_exact'] is True and bool(x['failure']) for x in controls),
                'missing phase/chirality rejection controls')
            for n,admission in enumerate(row['admission']):
                inp=seed.inputs if n<2 else target;role=ROLES[n%2]
                b.require(admission['published']==seed.scientific_digest
                          and admission['pass_capture']['inputs']==replace(inp,current=getattr(inp,role),dt=1).to_payload(),
                          'admission role/stage/atomicity')
                if numerics:consumer.check_pass(admission['pass_capture'],policy)
                max_error=max(max_error,numeric_pair(base['admission'][n]['pass_capture'],
                    admission['pass_capture'],d,policy,base['event_id'],row['event_id']))
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
    return dict(family='C_OS',status='executed_pending_review',required_cells=24,passing_pending_cells=24,
        accepted_cells=0,native_events=16,target_steps=64,source_steps=4,final_reads=32,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[45,52],chart_symmetries=True,normalization_policy_id=NORMALIZATION,frozen_plan_executions=4,
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
        frozen=frozen_pairs(execute=True)
        sources=[execute_source(m,d) for d in m['transforms']];rows=[]
        for case in m['cases']:
            for source,d in zip(sources,m['transforms'],strict=True):
                rows.append(execute_case(m,source,case,d));print(case['fixture_id'],d['kind'],'passed',flush=True)
    record=b.seal(dict(schema='p984f-cos-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),
        frozen_plan_execution=dict(pairs=frozen,plans_executed=4,numerical_events=0),user_accepted=False,aggregate_closed=False))
    summary=check(m,record,numerics=True);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
