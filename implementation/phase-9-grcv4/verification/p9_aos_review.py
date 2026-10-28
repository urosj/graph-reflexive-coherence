"""Bounded fifth-realization reconciliation; execution never grants acceptance."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import p984d_aos_runtime as deep
import p984ef_aos as covariance
import p984gh_aos_native as large
import p984h_aos_covariance as large_covariance
import p985_aos as lifecycle
import p99_aos as integration
import p99_aos_authority as authority
import p9_aos_historical as historical

b=deep.b
SELF=b.HERE+'p9_aos_review.py'
TEST=b.HERE+'test_p9_aos_review.py'
GUIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/AOSFifthRealization.md'
PATH=b.BASE+'P9-AOS-Tranches8-9-Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end',
       '9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')


def large_paths():
    return [*(large.filename(s,r) for s in ('source','prepared_target') for r in large.ROLES),
        large.filename('event'),*(large.filename('step',r,i) for r in large.ROLES for i in range(1,11)),
        *(large.filename('final',r) for r in large.ROLES)]


def required_paths():
    paths={SELF,TEST,GUIDE,authority.PATH,authority.SELF,historical.PATH,historical.SELF,
        *historical.CHANGED,deep.INPUTS,deep.RESULTS,deep.oracle.INPUTS,deep.oracle.RESULTS,
        large.g.INPUTS,large.g.RESULTS,large.INPUTS,large_covariance.INPUTS,lifecycle.INPUTS,
        integration.BASE+'P9-9.3-AOSMatrix.json',*large_paths(),
        *(p for checkpoint in ('e','f') for p in covariance.paths(checkpoint)),
        *(large_covariance.path(k,s) for k in large_covariance.KINDS for s in ('event',*large.ROLES)),
        *(lifecycle.path(s) for s in ('small','large')),
        *(integration.filename(c) for c in integration.GROUPS)}
    return paths


def check_step_metadata(value):
    """Independent tree-charge and complete saved-state/geometry consumption."""
    before,after=value['before'],value['after'];q=large.q
    wanted=dict(before,current=after['current'],step_index=before['step_index']+1,
        time=float(q(before['time'])+q(before['dt'])),
        scientific_state_id=after['scientific_state_id'],source_lifecycle_id=after['source_lifecycle_id'])
    # The two derived identities are authenticated by GeometryStageInputs in
    # check_step; all remaining metadata must be retained literally.
    b.require(after==wanted,'step changed unowned metadata')
    values=list(after['current']['C'])
    while len(values)>1:
        values=[float(q(values[i])+q(values[i+1])) if i+1<len(values) else values[i]
            for i in range(0,len(values),2)]
    actual=values[0] if values else 0.;target=before['Q_target'];delta=q(actual)-q(target)
    b.require(value['charge']==dict(target_charge=target,admitted_charge=actual,residual=float(delta)),
        'saved charge differs from independent binary64 tree')
    policy=before['reference']['profile']['params_resolved']['charge']
    bound=q(policy['absolute_tolerance'])+q(policy['relative_tolerance'])*max(abs(q(target)),q(1))
    b.require(abs(delta)<=bound and q(value['exact_resource_sum_delta'])==
        sum(map(q,after['current']['C']),q(0))-sum(map(q,before['current']['C']),q(0)), 'charge bound/exact sum drift')
    b.require(value['final']['H_digest']==b.digest(value['H'])
        and value['restart']['H_digest']==b.digest(before['H1_form']),'read geometry binding')
    # Consume both generated matrices from the saved selected currents' flats.
    # No native solver, continuity update or writer runs in this check.
    scalar=large.scalar;params=before['reference']['profile']['params_resolved']
    graph=before['reference']['graph'];nodes={v:i for i,v in enumerate(graph['live_node_ids'])}
    incidence=b.np.zeros((len(nodes),len(graph['edges'])),dtype=int)
    for i,edge in enumerate(graph['edges']):
        incidence[nodes[edge['head']['node_id']],i]+=1
        incidence[nodes[edge['tail']['node_id']],i]-=1
    b.require(not any(x for row in before['reference']['K4_base'] for x in row),'undeclared nonzero reference K4')
    md=dict(w=before['current']['W_A'],p=params['candidate'],params=params,
        mask=abs(incidence).T@abs(incidence)/2)
    with scalar.ctx.workprec(scalar.BITS):
        for stage,key in (('predictor','H'),('corrector','regenerated_digest')):
            h=scalar.image(md,value[stage]['flat'],staged=True)
            rows=[[scalar.unique(h[i,j]) for j in range(h.ncols())] for i in range(h.nrows())]
            expected=b.digest(value['H']) if key=='H' else value['oracle'][key]
            b.require(b.digest(rows)==expected,'OS geometry regeneration consumption')


def check_large():
    m=deep.oracle.read(large.INPUTS);large.check_manifest(m)
    timings=[];event=large.read('event');b.check_digest(event)
    b.require(event['manifest_digest']==m['record_digest'] and event['outcome']=='completed'
        and event['segment']=='event' and not event['user_accepted'] and not event['aggregate_closed'],'event scope')
    source,source_record=large.source_state();target=large.state(event['execution']['state'])
    e=event['execution']
    b.require(e['source_record_digest']==source_record['record_digest'] and e['stale_rollback_exact']
        and e['exact_replay'] and e['native_events']==1 and e['checkpoint']['state']==e['state']
        and e['request']['source_state_digest']==source.scientific_digest
        and e['request']['history_policy']==large.aos_history_policy(source.inputs.current,source.inputs.reset), 'actual event binding')
    # Recompute transfer from actual source resources, not prepared-target data.
    old=source.inputs.geometry.reference.graph.port_graph;new=target.inputs.geometry.reference.graph.port_graph
    shares={e['event_id']+f'/satellite/{i+1}':large.q(x) for i,x in enumerate(e['request']['resource_distribution'])}
    for role in large.ROLES:
        incoming=getattr(source.inputs,role);actual=getattr(target.inputs,role)
        cs=dict(zip(old.live_node_ids,incoming.C,strict=True));ws=dict(zip((x.edge_id for x in old.edges),incoming.W_A,strict=True))
        expected=[cs[v] if v in cs else float(large.q(cs[e['request']['source_node_id']])*shares.get(v,large.q(0))) for v in new.live_node_ids]
        b.require(list(actual.C)==expected and list(actual.W_A)==[ws.get(x.edge_id,1.) for x in new.edges],'actual both-role transfer')
        for segment in ('source','prepared_target'):
            v=large.read(segment,role);b.check_digest(v)
            b.require(v['manifest_digest']==m['record_digest'] and (v['segment'],v['role'])==(segment,role),'prerequisite binding')
            initial=large.prepared('source' if segment=='source' else 'target').inputs
            b.require(v['execution']['before']==replace(initial,current=getattr(initial,role),dt=large.DT).to_payload(),'prerequisite operand')
            large.check_step(v['execution'])
            check_step_metadata(v['execution'])
            if segment=='source':b.require(all(v['execution']['trigger'][k] for k in ('small_gradient','strict_hessian_condition')),'source trigger')
        before=replace(target.inputs,current=getattr(target.inputs,role),dt=large.DT)
        for i in range(1,11):
            v=large.read('step',role,i);b.check_digest(v)
            b.require(v['manifest_digest']==m['record_digest'] and (v['segment'],v['role'],v['index'])==('step',role,i)
                and v['execution']['before']==before.to_payload() and v['execution']['event_record_digest']==event['record_digest']
                and v['outcome']=='completed' and not v['user_accepted'] and not v['aggregate_closed'],'actual continuation chain')
            before=large.check_step(v['execution'])
            check_step_metadata(v['execution'])
        v=large.read('final',role);b.check_digest(v);f=v['execution']
        b.require(v['manifest_digest']==m['record_digest'] and (v['segment'],v['role'])==('final',role)
            and f['before']==before.to_payload() and f['read_only'] and f['event_record_digest']==event['record_digest']
            and f['oracle']['subject_digest']==b.digest(large.subject(before)),'final read binding')
        for key in ('predictor','corrector'):large.compare_point(f[key],f['oracle'][key])
    for path in large_paths():
        v=deep.oracle.read(path)
        b.require(0<v['elapsed_seconds']<=m['caps']['event' if v['segment']=='event' else 'final' if v['segment']=='final' else 'step'],'execution cap')
        timings.append(dict(path=path,seconds=v['elapsed_seconds'],native_seconds=v['execution'].get('native_seconds')))
    cm=deep.oracle.read(large_covariance.INPUTS);b.check_digest(cm);b.check_bindings(cm['source_bindings'])
    maximum=0.
    def leaves(value):
        if isinstance(value,dict):
            for v in value.values():yield from leaves(v)
        else:yield value
    for kind in large_covariance.KINDS:
        for segment in ('event',*large.ROLES):
            v=large_covariance.read(kind,segment);errors=large_covariance.check(v,kind,segment,cm)
            b.require(v['covariance_errors']==errors,'retained covariance error drift')
            if segment!='event':check_step_metadata(v['execution'])
            maximum=max(maximum,*leaves(errors)) if errors else maximum
            timings.append(dict(path=large_covariance.path(kind,segment),seconds=v['seconds'],native_seconds=v['execution'].get('native_seconds')))
    return dict(vertices=len(new.live_node_ids),edges=len(new.edges),native_events=9,
        prerequisite_steps=4,actual_target_steps=20,covariant_target_steps=16,
        successful_history_cells=18,final_reads=2,maximum_covariance_error=maximum,timings=timings)


def build():
    # Saved-input geometry validation also uses exact algebra. Honor the
    # selected FLINT backend without sharing matrix facts across policies.
    with b.exact_backend(b.ExactBackend.FLINT):
        return _build()


def _build():
    statuses={}
    statuses['8.4d']=deep.check(deep.oracle.read(deep.INPUTS),deep.oracle.read(deep.RESULTS))
    for checkpoint in ('e','f'):
        ip,rp=covariance.paths(checkpoint)
        statuses['8.4'+checkpoint]=covariance.check(deep.oracle.read(ip),deep.oracle.read(rp))
    statuses['8.4g']=large.g.check(deep.oracle.read(large.g.INPUTS),deep.oracle.read(large.g.RESULTS))
    with large.policy():
        statuses['8.4h']=check_large()
        lm=deep.oracle.read(lifecycle.INPUTS)
        for segment in ('small','large'):lifecycle.check(lm,deep.oracle.read(lifecycle.path(segment)))
    records={k:integration.check(k) for k in integration.GROUPS}
    matrix=deep.oracle.read(integration.BASE+'P9-9.3-AOSMatrix.json')
    b.require(matrix==integration.matrix(),'compatibility matrix drift')
    oracle_status=statuses['8.4g']
    statuses['8.4g']=dict(oracle=oracle_status,original_reset_excluded=True,
        companion=oracle_status['companion'],native_prerequisite_steps=4,ready_for_8_4h=True)
    statuses['8.4i']=dict(handoff='exact_retained_records',historical_boundary_accepted=True,new_acceptance=False)
    statuses['8.5']=dict(small_tests=6,large_replay=True,readmissions=3,both_roles=True)
    statuses['8.6']=dict(conformance='bounded_A_OS',optional_completion='unselected',universal_graph_claim=False)
    statuses['tranche8_end']=dict(bounded_execution='passed',user_acceptance='pending')
    for k,v in records.items():statuses[k]=dict(tests=v['tests_run'],execution_digest=v['record_digest'])
    statuses['9.3']=dict(counts=matrix['counts'])
    snapshot=records['9.1b']['evidence']['mixed_snapshot']
    def subject(value):
        return {k:value[k] for k in ('model_identity','scientific_digest','reset_digest') if k in value} | {
            'complete_profile_id':value['inputs']['reference']['profile']['complete_profile_id']}
    statuses['9.6']=dict(source=subject(snapshot['initial']),enabled_target=subject(snapshot['state']),
        compatibility_source_model=records['9.2']['evidence']['transition']['model_identity'],
        expanded_target_four_surface_compatibility='not_transferred_from_source',
        A_OS_basin_policy='unselected',umbrella_compatibility='held_twenty_unselected_cells')
    provenance=authority.check()
    statuses['9.6']['authority']=[dict(contract_id=key,trace_digest=trace['trace_digest'],
        support_disposition=trace['rows'][0]['payload']['support_disposition'])
        for key,trace in provenance['traces'].items()]
    names=required_paths()
    for name in tuple(names):
        if name.endswith(('.json','.json.xz')):
            record=deep.oracle.read(name)
            refs=record.get('source_bindings',[])
            names.update(refs if isinstance(refs,dict) else (r['path'] for r in refs))
    rows=[dict(checkpoint=k,state='passed_pending_acceptance',user_accepted=False,execution=statuses[k]) for k in STEPS]
    return b.seal(dict(schema='p9-aos-review-v1',family='A_OS',realization_number=5,checkpoints=rows,
        source_bindings=b.bind(names),original_large_reset_excluded=True,
        numerical_scope='pointwise_exact_OS_composition_at_saved_inputs_not_uniform_trajectory',
        performance=dict(exact_backend='flint',large_policy='certified_arb_256_weighted_v1',
            validation_memo=large.VALIDATION_POLICY,matrix_cache='operation_scoped_exact_content',
            profiled_source_seconds=large.read('source')['elapsed_seconds'],
            bottleneck='serialization_and_validation',further_kernel_change_required=False),
        accepted_first_group=['C_OS','C_CI','A_CI','A_PC'],
        remaining_families=['C_PC','C_CI_PC','A_CI_PC','C_RG2b','A_RG2b'],
        optional_completion='unselected',tranche10='deferred',user_accepted=False,
        aggregate_closed=False,full_GRC9V4_conformance=False))


def checked(root=b.ROOT,value=None):
    root=Path(root).resolve()
    value=json.loads((root/PATH).read_bytes()) if value is None else value
    b.check_digest(value)
    b.require(value['schema']=='p9-aos-review-v1' and value['family']=='A_OS' and value['realization_number']==5
        and [r['checkpoint'] for r in value['checkpoints']]==list(STEPS)
        and all(r['state']=='passed_pending_acceptance' and r['user_accepted'] is False for r in value['checkpoints'])
        and all(value[k] is False for k in ('user_accepted','aggregate_closed','full_GRC9V4_conformance'))
        and value['original_large_reset_excluded'] and value['optional_completion']=='unselected'
        and value['tranche10']=='deferred','A_OS review scope')
    refs=value['source_bindings']
    b.require(len({r['path'] for r in refs})==len(refs) and required_paths()<={r['path'] for r in refs},'review source roster')
    for ref in refs:
        p=(root/ref['path']).resolve()
        b.require(p.is_relative_to(root) and b.sha(p.read_bytes())==ref['sha256'],'review source drift: '+ref['path'])
    rows={r['checkpoint']:r['execution'] for r in value['checkpoints']}
    b.require(rows['8.4d']['successful_history_cells']==40 and rows['8.4e']['successful_history_cells']==20
        and rows['8.4f']['successful_history_cells']==24 and rows['8.4h']['actual_target_steps']==20
        and rows['8.4h']['covariant_target_steps']==16 and rows['8.4h']['native_events']==9
        and rows['9.3']['counts']==dict(bounded_accepted=16,passed_pending_acceptance=4,unselected_not_executed=20), 'review coverage')
    b.require({r['contract_id'] for r in rows['9.6']['authority']}==set(authority.IDS)
        and all(r['support_disposition']=='indeterminate_requires_review' for r in rows['9.6']['authority']),
        'inherited authority limits changed')
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('build','check'));args=p.parse_args()
    if args.action=='build':
        value=build();checked(value=value);b.write_new(PATH,value)
    else:checked()
    print('A_OS bounded review passed; user acceptance pending')
