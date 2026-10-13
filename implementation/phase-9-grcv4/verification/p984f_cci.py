"""C_CI full chart covariance of complete joint roots and both histories.

Reuses accepted transformation algebra and CI interval equations. Only run
executes native operations; retained checking never reconstructs native roots.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

from concurrent.futures import ProcessPoolExecutor
import p984f_cos as algebra
from p984e_cci import check_event, root_pair
import p984d_cci as prior
from pygrc.models.grc_9_v4_expansion import cci_profile_template

r, b, certificate = prior.r, prior.b, prior.certificate
SELF=b.HERE+'p984f_cci.py'
TEST=b.HERE+'test_p984f_cci.py'
PLAN=b.BASE+'P9-8.4f-CCIPlan.md'
INPUTS=b.BASE+'P9-8.4f-CCIInputs.json'
RESULTS=b.BASE+'P9-8.4f-CCIResults.json'
REVIEW=b.BASE+'P9-8.4f-CCIReview.md'
ROLES, KINDS = algebra.ROLES, algebra.KINDS


def make_manifest():
    phase=b.read(r.INPUTS)
    b.check_digest(phase);b.check_bindings(phase['source_bindings'])
    cases=[next(c for c in phase['cases'] if c['request']['target_effective_degree']==degree
        and c['request']['module_chirality']==ch
        and c['request']['growth_phase']==(None if degree==45 else 1))
        for degree in (45,52) for ch in (1,-1)]
    frozen=b.read(algebra.RESULTS);b.check_digest(frozen)
    b.require(frozen['frozen_plan_execution']==dict(pairs=algebra.frozen_pairs(),plans_executed=4,numerical_events=0),
        'frozen mechanical predecessor')
    traces=algebra.authority()
    paths={SELF,TEST,PLAN,algebra.SELF,algebra.INPUTS,algebra.RESULTS,algebra.REVIEW,
        b.HERE+'p984e_cci.py',b.BASE+'P9-8.4e-CCIReview.md',r.INPUTS,r.REVIEW,
        prior.SELF,prior.previous.SELF,b.HERE+'p984d_cci_certificate.py'}
    paths|={x['path'] for x in phase['source_bindings']}
    paths|={x['source_ref']['path'] for t in traces.values() for x in t['rows']}
    return b.seal(dict(schema='p984f-cci-inputs-v1',family='C_CI',source_bindings=b.bind(paths),
        initial_inputs=phase['initial_inputs'],expected_source=phase['expected_source'],cases=cases,
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


def expected_event(source,case,declaration):
    seed=r.state(source);ref=seed.inputs.geometry.reference
    nodes={'s':'s'};request=deepcopy(case['request']);branch=declaration['branches']
    mapped=[0.]*3
    for i,x in enumerate(request['resource_distribution'],1):mapped[branch[str(i)]-1]=x
    request.update(module_chirality=request['module_chirality']*declaration['chirality_factor'],
        growth_phase=None if request['growth_phase'] is None else branch[str(request['growth_phase'])],
        resource_distribution=mapped)
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id=nodes['s'],target_profile_template_id=cci_profile_template(ref).profile_template_id,
        operation_id='p984f-cci-'+case['fixture_id']+'-'+declaration['kind'])
    identity=deepcopy(case['oracle']['event_identity'])
    for key in identity:
        if key in request and key!='schema_version':identity[key]=request[key]
    event='grc-event-sha256:'+b.digest(identity)
    graph=algebra.transported_graph(case['oracle']['target_graph'],declaration,case['oracle']['event_id'],event)
    p=deepcopy(source['inputs']);reference=p['reference'];reference['graph']=graph
    weights={e['edge_id']:1 for e in graph['edges']};size=len(weights)
    reference['K4_base']=[[0.0]*size for _ in range(size)]
    reference['reference_hodge']['edge_weights']=weights.copy()
    reference['profile']['params_resolved']['candidate']['W_C_tr']=weights.copy()
    algebra.reidentify(reference)
    p['H1_form']=[[float(i==j) for j in range(size)] for i in range(size)]
    for role in ROLES:
        old=dict(zip(ref.graph.live_node_ids,p[role]['C'],strict=True))
        image={n:old.get(n,0.) for n in graph['live_node_ids']}
        for j,share in enumerate(request['resource_distribution'],1):
            image[event+f'/satellite/{j}']=float(b.Fraction(old[nodes['s']])*b.Fraction(share))
        p[role]['C']=[image[n] for n in graph['live_node_ids']]
    p.update(dt=0,operation_id=request['operation_id'])
    return request,identity,algebra.materialize(source['inputs'],p)


def execute_source(m,d):
    before=b.GeometryStageInputs.from_payload(algebra.transform(m['initial_inputs'],d))
    step=r.ProvisionalCandidateCIStep(before)
    seed=replace(r.state(m['expected_source']),inputs=replace(step.next_inputs,dt=0))
    return dict(kind=d['kind'],step=r.capture_step(step),state=seed.to_payload())


def execute_case(m,source,case,d):
    request,identity,expected=expected_event(source['state'],case,d)
    seed=r.state(source['state']);owner=r.native.GRC9V4CCIOperation(seed);before=owner.checkpoint()
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
            step=r.ProvisionalCandidateCIStep(incoming);steps.append(r.capture_step(step));incoming=step.next_inputs
        roles[role]=dict(steps=steps,final=r.certified_root(r.CandidateCIRoot(replace(incoming,dt=0))))
    return dict(layout=case['fixture_id'],kind=d['kind'],request=request,event_identity=identity,
        event_id='grc-event-sha256:'+b.digest(identity),event_committed=True,case_passed=True,
        event=event,roles=roles,stale_request_control=dict(committed=False,rollback_exact=True,
            failure=rejected.failure.to_payload()),semantic_controls=semantic)


def check(m,record,*,numerics=False):
    check_manifest(m);b.check_digest(record)
    b.require(record['schema']=='p984f-cci-results-v1' and record['manifest_digest']==m['record_digest']
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
            b.require(c[role]['W_A'] is None and c[role]['Z_4'] is None,'history leakage')
    def roots_pair(a,c,indices):
        nonlocal max_error
        max_error=max(max_error,root_pair(a,c,indices,policy))
    with certificate.checker():
        for source,d in zip(sources,m['transforms'],strict=True):
            before=b.GeometryStageInputs.from_payload(algebra.transform(m['initial_inputs'],d))
            after=r.check_step(before,source['step'],numerics=numerics)
            b.require(replace(after,dt=0).to_payload()==source['state']['inputs'],'source poststate substitution')
            indices=algebra.mapping(m['initial_inputs']['reference']['graph'],before.geometry.reference.graph.to_payload(),d)
            states_pair(sources[0]['state']['inputs'],source['state']['inputs'],indices)
            for key in ('root','reset_root','restart'):roots_pair(sources[0]['step'][key],source['step'][key],indices)
        for case in m['cases']:
            base=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']=='base')
            for d,source in zip(m['transforms'],sources,strict=True):
                row=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']==d['kind'])
                request,identity,expected=expected_event(source['state'],case,d)
                b.require(row['request']==request and row['event_identity']==identity
                    and row['event_id']=='grc-event-sha256:'+b.digest(identity),'event/request binding')
                b.require(row['event_committed'] is True and row['case_passed'] is True,'incomplete event')
                seed=r.state(source['state'])
                target=check_event(seed,dict(request=request,oracle=dict(event_id=row['event_id'])),row['event'],expected,numerics=numerics)
                control=row['stale_request_control']
                b.require(control['committed'] is False and control['rollback_exact'] is True and bool(control['failure']),'missing stale request control')
                check_controls(row,seed)
                b.require(set(row['roles'])==set(ROLES),'role coverage')
                bg=base['event']['actual_target']['inputs']['reference']['graph'];tg=target.inputs.geometry.reference.graph.to_payload()
                b.require(algebra.transported_graph(bg,d,base['event_id'],row['event_id'])==tg,'normalized target graph')
                indices=algebra.mapping(bg,tg,d,base['event_id'],row['event_id'])
                states_pair(base['event']['actual_target']['inputs'],target.inputs.to_payload(),indices)
                source_indices=algebra.mapping(sources[0]['state']['inputs']['reference']['graph'],
                    source['state']['inputs']['reference']['graph'],d)
                for admission_index,admission_indices in ((0,source_indices),(1,indices)):
                    for key in ('root','reset_root'):
                        roots_pair(base['event']['admission_reads'][admission_index][key],
                            row['event']['admission_reads'][admission_index][key],admission_indices)
                for role in ROLES:
                    rr=row['roles'][role];br=base['roles'][role];incoming=replace(target.inputs,current=getattr(target.inputs,role),dt=b.DT)
                    b.require(len(rr['steps'])==2,'continuation horizon')
                    for k,step in enumerate(rr['steps']):
                        incoming=r.check_step(incoming,step,numerics=numerics)
                        states_pair(br['steps'][k]['poststate'],step['poststate'],indices)
                        for key in ('root','reset_root','restart'):roots_pair(br['steps'][k][key],step[key],indices)
                    r.check_root(replace(incoming,dt=0),rr['final'],numerics=numerics)
                    roots_pair(br['final'],rr['final'],indices)
    return dict(family='C_CI',status='executed_pending_review',required_cells=24,passing_pending_cells=24,
        accepted_cells=0,native_events=16,target_steps=64,source_steps=4,final_reads=32,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[45,52],full_joint_roots=True,chart_symmetries=True,
        normalization_policy_id=algebra.NORMALIZATION,frozen_plan_executions=0,reused_frozen_plan_executions=4,
        native_trajectories_rerun=False,interval_certificates_rerun=numerics,uniform_domain=False,aggregate_closed=False)


def check_controls(row,seed):
    controls=row['semantic_controls']
    expected=[('module_chirality',None,'module_chirality_required'),
        ('growth_phase',1 if row['request']['growth_phase'] is None else None,
         'reject_noncanonical_inactive_growth_phase' if row['request']['growth_phase'] is None else 'module_growth_phase_required')]
    b.require(len(controls)==len(expected),'semantic roster')
    for control,(field,value,code) in zip(controls,expected,strict=True):
        failure=control['failure']
        b.require(control['field']==field and control['value']==value
            and control['committed'] is False and control['rollback_exact'] is True
            and failure['code']==code and failure['stage']=='admission'
            and failure['prestate_digest']==failure['poststate_digest']==seed.scientific_digest
            and failure['pre_lifecycle_digest']==failure['post_lifecycle_digest']==seed.lifecycle_digest(()),
            'semantic failure identity/rollback drift')


def execute_variant(job):
    m,d=job
    with b.exact_backend(b.ExactBackend.FLINT),certificate.checker():
        source=execute_source(m,d);rows=[]
        for case in m['cases']:
            rows.append(execute_case(m,source,case,d))
            print(case['fixture_id'],d['kind'],'passed',flush=True)
        return source,rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':b.write_new(INPUTS,make_manifest());return
    m=b.read(INPUTS);check_manifest(m)
    if args.mode=='check':
        with ExitStack() as stack:
            for module,name in ((r,'ProvisionalCandidateCIStep'),(r,'CandidateCIRoot'),(r.native,'GRC9V4CCIOperation')):
                stack.enter_context(patch.object(module,name,side_effect=AssertionError('native producer forbidden')))
            print(json.dumps(check(m,b.read(RESULTS),numerics=args.recheck_numerics),indent=2))
        return
    b.require(not (b.ROOT/RESULTS).exists(),'refuse overwrite')
    with ProcessPoolExecutor(max_workers=4) as pool:
        captured=list(pool.map(execute_variant,[(m,d) for d in m['transforms']]))
    sources=[x[0] for x in captured]
    by={(row['layout'],row['kind']):row for _,rows in captured for row in rows}
    rows=[by[(case['fixture_id'],d['kind'])] for case in m['cases'] for d in m['transforms']]
    record=b.seal(dict(schema='p984f-cci-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),frozen_plan_reuse=m['frozen_plan_reuse'],user_accepted=False,aggregate_closed=False))
    summary=check(m,record,numerics=False);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
