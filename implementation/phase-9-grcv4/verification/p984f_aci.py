"""A_CI full-chart covariance of full joint roots, not current-only agreement.

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

import p984f_cos as algebra
from p984f_cci import check_controls
import p984d_aci_runtime as prior
from pygrc.models.grc_9_v4_expansion import aci_profile_template

r, b = prior.r, prior.b
SELF=b.HERE+'p984f_aci.py'
TEST=b.HERE+'test_p984f_aci.py'
PLAN=b.BASE+'P9-8.4f-ACIPlan.md'
INPUTS=b.BASE+'P9-8.4f-ACIInputs.json'
RESULTS=b.BASE+'P9-8.4f-ACIResults.json'
REVIEW=b.BASE+'P9-8.4f-ACIReview.md'
ROLES, KINDS = algebra.ROLES, algebra.KINDS


def make_manifest():
    deep=b.read(prior.INPUTS);phase=b.read(r.INPUTS)
    for value in (deep,phase):
        b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(deep['initial_inputs']==phase['initial_inputs'],'different predecessor sources')
    cases=[next(c for c in phase['cases'] if c['request']['target_effective_degree']==degree
        and c['request']['module_chirality']==ch
        and c['request']['growth_phase']==(None if degree==45 else 1))
        for degree in (45,52) for ch in (1,-1)]
    frozen=b.read(algebra.RESULTS);b.check_digest(frozen)
    b.require(frozen['frozen_plan_execution']==dict(pairs=algebra.frozen_pairs(),plans_executed=4,numerical_events=0),
        'frozen mechanical predecessor')
    traces=algebra.authority()
    paths={SELF,TEST,PLAN,algebra.SELF,algebra.INPUTS,algebra.RESULTS,algebra.REVIEW,
           b.HERE+"p984f_cci.py",b.HERE+"p984e_aci.py",b.BASE+"P9-8.4e-ACIReview.md",prior.INPUTS,prior.REVIEW,r.INPUTS,r.REVIEW,
           prior.SELF,prior.previous.SELF,r.SELF}
    paths|={x['path'] for m in (deep,phase) for x in m['source_bindings']}
    paths|={x['source_ref']['path'] for t in traces.values() for x in t['rows']}
    return b.seal(dict(schema='p984f-aci-inputs-v1',family='A_CI',source_bindings=b.bind(paths),
        initial_inputs=deep['initial_inputs'],expected_source=deep['expected_source'],cases=cases,
        transforms=algebra.declarations(),authority=traces,
        frozen_plan_reuse=dict(path=algebra.RESULTS,record_digest=frozen['record_digest'],
            pairs=algebra.frozen_pairs(),plans_executed=4,numerical_events=0),
        comparison=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13),
        scope=dict(layouts=4,transforms=3,required_history_cells=24,native_events=16,
                   target_steps=64,steps_per_role=2,final_reads=32,source_steps=4,
                   frozen_plan_executions=0,reused_frozen_plan_executions=4,
                   chart_symmetries=True,uniform_domain=False,full_joint_roots=True),
        user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m==make_manifest(),'covariance declaration drift')


mapping=algebra.mapping
transported_graph=algebra.transported_graph


def transform(value,d):
    algebra.validate_transform(d)
    before=b.GeometryStageInputs.from_payload(value)
    original=value['reference']['graph']
    b.require(before.geometry.reference.to_payload()==r.oracle.reference(original).to_payload(),
        'outside declared A_CI fixed-reference chart')
    graph=transported_graph(original,d)
    ni,ei,signs=mapping(original,graph,d)
    ref=r.oracle.reference(graph);h=value['H1_form']
    h=tuple(tuple(h[i][j] for j in ei) for i in ei)
    states={role:b.GRCV4AuthoritativeState(tuple(value[role]['C'][i] for i in ni),
        tuple(value[role]['W_A'][i] for i in ei),None) for role in ROLES}
    b.require(all(value[role]['Z_4'] is None for role in ROLES),'unexpected carrier')
    return replace(before,geometry=b.GRCV4Geometry(ref,b.OneFormHodge(ref.graph,h)),**states).to_payload()


def backend(before):
    return r.native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph)


def check_root(before,value,*,numerics=False):
    return r.check_root(before,backend(before),value,numerics=numerics)


def check_step(before,value,*,numerics=False):
    return r.check_step(before,backend(before),value,numerics=numerics)


def expected_event(source,case,d):
    seed=r.state(source);ref=seed.inputs.geometry.reference
    request=deepcopy(case['request']);branch=d['branches'];mapped=[0.]*3
    for i,x in enumerate(request['resource_distribution'],1):mapped[branch[str(i)]-1]=x
    request.update(module_chirality=request['module_chirality']*d['chirality_factor'],
        growth_phase=None if request['growth_phase'] is None else branch[str(request['growth_phase'])],
        resource_distribution=mapped)
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id='source-s',target_profile_template_id=aci_profile_template(ref).profile_template_id,
        history_policy=r.oracle.history_policy(b.authority_payload(seed.inputs.current),b.authority_payload(seed.inputs.reset)),
        operation_id='p984f-aci-'+case['fixture_id']+'-'+d['kind'])
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
    semantic=[]
    for field,bad in (('module_chirality',None),
            ('growth_phase',1 if request['growth_phase'] is None else None)):
        wrong=deepcopy(request);wrong[field]=bad
        failed=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(wrong))
        b.require(not failed.committed and owner.checkpoint()==before,'semantic rollback')
        semantic.append(dict(field=field,value=bad,committed=False,rollback_exact=True,
            failure=failed.failure.to_payload()))
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
            failure=rejected.failure.to_payload()),semantic_controls=semantic)


def execute_variant(job):
    m,d=job
    with b.exact_backend(b.ExactBackend.FLINT):
        source=execute_source(m,d)
        cases=[]
        for c in m['cases']:
            cases.append(execute_case(m,source,c,d))
            print(c['fixture_id'],d['kind'],'passed',flush=True)
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
    b.require(record['schema']=='p984f-aci-results-v1' and record['manifest_digest']==m['record_digest']
              and record['user_accepted'] is False and record['aggregate_closed'] is False
              and record['frozen_plan_reuse']==m['frozen_plan_reuse'],'result scope')
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
                check_controls(row,seed)
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
    return dict(family='A_CI',status='executed_pending_review',required_cells=24,passing_pending_cells=24,
        accepted_cells=0,native_events=16,target_steps=64,source_steps=4,final_reads=32,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[45,52],full_joint_roots=True,chart_symmetries=True,
        normalization_policy_id=algebra.NORMALIZATION,frozen_plan_executions=0,reused_frozen_plan_executions=4,
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
    record=b.seal(dict(schema='p984f-aci-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),frozen_plan_reuse=m['frozen_plan_reuse'],user_accepted=False,aggregate_closed=False))
    summary=check(m,record);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
