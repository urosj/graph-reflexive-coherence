"""Bounded sixth-realization reconciliation from immutable native execution records."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import p984d_cpc as deep
import p984ef_cpc as covariance
import p984h_cpc as large
import p984h_cpc_covariance as large_covariance
import p985_cpc as lifecycle
import p99_cpc as integration
import p99_cpc_authority as authority
import p9_cpc_historical as historical
import p9_cpc_verifier_epochs as repairs
import p9_cpc_large_runner as optimized
from p9_cpc_wire_reuse import wire_reuse

b=deep.b
SELF=b.HERE+'p9_cpc_review.py'
TEST=b.HERE+'test_p9_cpc_review.py'
CORE_TEST=b.HERE+'test_p9_cpc_science.py'
GUIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/CPCSixthRealization.md'
PATH=b.BASE+'P9-CPC-Tranches8-9-Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end',
       '9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')


def large_paths():
    return [*(large.filename(s,r) for s in ('source','prepared_target') for r in large.ROLES),
        large.filename('event'),*(large.filename('step',r,i) for r in large.ROLES for i in range(1,11)),
        *(large.filename('final',r) for r in large.ROLES)]


def required_paths():
    return {SELF,TEST,CORE_TEST,GUIDE,authority.PATH,authority.SELF,historical.PATH,historical.SELF,
        repairs.PATH,repairs.SELF,*historical.CHANGED,*historical.ADDITIONS,
        historical.SIDE+'phase9-web/cpc.js',b.BASE+'P9-CPC-Tranches8-9-Plan.md',
        'artifact-storage.json','scripts/evidence_storage.py',large.g.RESULTS+'.xz',large.companion.RESULTS+'.xz',
        optimized.SELF,optimized.CACHE,optimized.TEST,optimized.PREFLIGHT,
        large_covariance.compute.SELF,large_covariance.compute.PREFLIGHT,
        b.BASE+'P9-8.4h-CPCCovarianceCapInputs.json',
        b.BASE+'P9-CPC-CovarianceCapAttempt.json',
        b.BASE+'P9-CPC-EventCapAttempt.json',
        b.BASE+'P9-CPC-ScientificReview.md',b.BASE+'P9-CPC-ComputePreflight.json',
        deep.INPUTS,deep.RESULTS,deep.PREFLIGHT,large.g.INPUTS,large.g.RESULTS,
        large.companion.INPUTS,large.companion.RESULTS,large.INPUTS,large_covariance.INPUTS,lifecycle.INPUTS,
        integration.BASE+'P9-9.3-CPCMatrix.json',*large_paths(),
        *(p for k in ('e','f') for p in covariance.paths(k)),
        *(large_covariance.path(k,s) for k in large_covariance.KINDS for s in ('event',*large.ROLES)),
        *(lifecycle.path(s) for s in ('small','large')),*(integration.filename(k) for k in integration.GROUPS)}


def step_error_bounds(value):
    """Independent componentwise one-step error, including binary64 rounding.

    This is evaluated at each saved input, never presented as an enclosure of
    a ten-step exact trajectory. Current/source errors come from signed Arb
    equations, not from native residuals or a comparison of magnitudes.
    """
    g=large.g;q,a,hi=g.q,g.a,g.hi
    before=b.GeometryStageInputs.from_payload(value['before'])
    after=b.GeometryStageInputs.from_payload(value['after'])
    bv,_=g.graph_math.graph_data(large.subject(before));dt=q(before.dt)
    current=list(map(q,value['read']['current']));error=q(value['read']['certificate']['errors']['current'])
    resource=q(0)
    for i,old in enumerate(before.current.C):
        exact=q(old)-dt*sum((int(x)*y for x,y in zip(bv[i],current,strict=True)),q(0))
        bound=abs(q(after.current.C[i])-exact)+dt*sum(abs(int(x)) for x in bv[i])*error
        resource=max(resource,bound)
    with g.ctx.workprec(g.BITS):
        decay=(-a(before.dt)/a(before.geometry.reference.profile.params_resolved.realization.tau_PC)).exp()
        alpha=1-decay;source=[x for row in value['read']['source'] for x in row]
        rounding=max(hi(abs(a(out)-(decay*a(old)+alpha*a(src))))
            for out,old,src in zip(after.current.Z_4,before.current.Z_4,source,strict=True))
        carrier=rounding+hi(abs(alpha))*q(value['read']['certificate']['errors']['source'])
    b.require(0<=resource<q(large.LIMITS['resource']) and 0<=carrier<q(large.LIMITS['carrier']),
        'independent staged update error exceeds declared bound')
    return dict(resource_error=str(resource),carrier_error=str(carrier),uniform_trajectory_enclosure=False)


def check_large():
    m=deep.read(large.INPUTS);large.check_manifest(m)
    b.require(m['schema']=='p984h-cpc-inputs-v1' and m['family']=='C_PC'
        and m['numerical_policy']=='certified_arb_256' and m['independent_precision_bits']==large.g.BITS
        and m['scope']==dict(source_steps=2,prepared_target_steps=2,events=1,target_steps=20,final_reads=2),
        'large manifest scope')
    event=large.read('event');seed,source=large.source_state();e=event['execution']
    target=large.check_event(seed,e['case'],e['event'])
    b.require(e['case']==large.case_for(seed) and e['state']==target.to_payload()
        and e['checkpoint']==e['event']['checkpoint'] and e['source_record_digest']==source['record_digest']
        and e['rollback_exact'] and e['stale_failure'] and e['native_events']==1 and e['native_steps']==0,'actual event binding')
    errors={};timings=[]
    def scope(v,segment,role,index=1):
        b.check_digest(v)
        if 'serialization_reuse' in v:
            b.require(v['compute_bindings']==optimized.bindings() and v['serialization_reuse']['hits']>0
                and v['serialization_reuse']['retained_bytes']==0,'serialization compute binding/reuse')
        b.require(v['schema']=='p984h-cpc-segment-v1' and v['manifest_digest']==m['record_digest']
            and (v['segment'],v['role'],v['index'])==(segment,role,index) and v['outcome']=='completed'
            and not v['user_accepted'] and not v['aggregate_closed']
            and 0<v['elapsed_seconds']<=m['caps']['event' if segment=='event' else 'final' if segment=='final' else 'step']
            and v['compute_policy']['exact_backend']=='flint' and v['compute_policy']['matrix_reuse']=='automatic_exact_operands',
            'large segment identity/policy/cap')
        timings.append(dict(path=large.filename(segment,role,index),seconds=v['elapsed_seconds'],native_seconds=v['execution'].get('native_seconds')))
    scope(event,'event','current')
    for role in large.ROLES:
        for segment in ('source','prepared_target'):
            v=large.read(segment,role);scope(v,segment,role)
            initial=large.prepared('source' if segment=='source' else 'target')
            wanted=large.r.role_input(initial.inputs,role,dt=large.DT)
            b.require(v['execution']['before']==wanted.to_payload(),'prerequisite operand')
            after=large.check_step(v['execution'])
            b.require(v['execution']['state']==replace(initial,inputs=replace(after,dt=0)).to_payload(),'prerequisite state')
            if segment=='source':b.require(all(v['execution']['trigger'][k] for k in ('small_gradient','strict_hessian_condition')),'source trigger')
            errors[large.filename(segment,role)]=step_error_bounds(v['execution'])
        before=large.r.role_input(target.inputs,role,dt=large.DT);previous=event['record_digest']
        for index in range(1,11):
            v=large.read('step',role,index);scope(v,'step',role,index);step=v['execution']
            b.require(step['before']==before.to_payload() and step['event_record_digest']==event['record_digest']
                and step['predecessor_digest']==previous,'complete target continuation lineage')
            before=large.check_step(step);previous=v['record_digest']
            errors[large.filename('step',role,index)]=step_error_bounds(step)
        v=large.read('final',role);scope(v,'final',role);final=v['execution'];before=replace(before,dt=0)
        b.require(final['before']==before.to_payload() and final['event_record_digest']==event['record_digest']
            and final['predecessor_digest']==previous and final['read_only'],'final read lineage')
        large.check_read(before,final['read'])
    cm=deep.read(large_covariance.INPUTS);maximum=0.0
    b.require(cm==large_covariance.manifest(),'covariance manifest scope')
    def leaves(value):
        if isinstance(value,dict):
            for x in value.values():yield from leaves(x)
        else:yield value
    for kind in large_covariance.KINDS:
        for segment in ('event',*large.ROLES):
            v=large_covariance.read(kind,segment);actual=large_covariance.check(v,kind,segment,cm)
            b.require(actual==v['covariance_errors'],'counterpart covariance error drift')
            maximum=max(maximum,*leaves(actual))
            if segment!='event':errors[large_covariance.path(kind,segment)]=step_error_bounds(v['execution'])
            timings.append(dict(path=large_covariance.path(kind,segment),seconds=v['seconds'],native_seconds=v['execution'].get('native_seconds')))
    graph=target.inputs.geometry.reference.graph
    b.require((len(graph.live_node_ids),len(graph.live_edge_ids))==(107,407),'larger graph size')
    return dict(vertices=107,edges=407,native_events=9,prerequisite_steps=4,actual_target_steps=20,
        covariant_target_steps=16,successful_history_cells=18,final_reads=2,maximum_covariance_error=maximum,
        update_error_bounds=errors,timings=timings)


def science():
    g=large.g
    m=deep.read(g.INPUTS);v=deep.read(g.RESULTS);b.check_digest(m);b.check_digest(v);b.check_bindings(m['source_bindings'])
    b.require(m==g.make_manifest(),'original declared scientific subject')
    b.require(v['schema']=='p984g-cpc-results-v1' and v['user_accepted'] is False and v['aggregate_closed'] is False
        and v['manifest_digest']==m['record_digest'] and v['cases']==g.calculate(m['original'])
        and v['ready_for_native'] is False and v['native_steps']==v['native_events']==0,'original oracle integrity')
    for role in large.ROLES:
        row=next(x for x in v['cases'] if (x['graph'],x['role'])==('target',role))
        b.require(not row['first_step_nonnegative'] and row['negative_resources'],'both original target roles excluded')
    cm=deep.read(large.companion.INPUTS);cv=deep.read(large.companion.RESULTS)
    b.require(cm==large.companion.manifest() and cv==large.companion.calculate(cm)
        and cv['ready_for_native'] is True and not cm['changed_tolerances'] and not cm['changed_step_size'],'independent companion')
    return dict(original_target_roles_excluded=list(large.ROLES),original_native_credit=False,
        companion=cm['companion'],ready_for_8_4h=True,pointwise_precision_bits=g.BITS,
        independent_equations='vertex_reduced_Arb_PC_with_whole_chart_bounds')


def build():
    with wire_reuse(),large.compute_worker():
        statuses={'8.4d':deep.check(deep.read(deep.INPUTS),deep.read(deep.RESULTS))}
        for k in ('e','f'):
            ip,rp=covariance.paths(k);statuses['8.4'+k]=covariance.check(deep.read(ip),deep.read(rp))[0]
        statuses['8.4g']=science();statuses['8.4h']=check_large()
        lm=deep.read(lifecycle.INPUTS)
        for segment in ('small','large'):lifecycle.check(lm,deep.read(lifecycle.path(segment)))
    records={k:integration.check(k) for k in integration.GROUPS}
    matrix=deep.read(integration.BASE+'P9-9.3-CPCMatrix.json')
    b.require(matrix==integration.matrix(),'compatibility matrix drift')
    statuses.update({'8.4i':dict(handoff='exact_retained_records',predecessor_accepted=True,new_acceptance=False),
        '8.5':dict(small_tests=6,large_replay=True,readmissions=3,both_roles=True),
        '8.6':dict(conformance='bounded_C_PC',optional_completion='unselected',universal_graph_claim=False),
        'tranche8_end':dict(bounded_execution='passed',user_acceptance='pending'),
        '9.3':dict(counts=matrix['counts'])})
    for k,v in records.items():statuses[k]=dict(tests=v['tests_run'],execution_digest=v['record_digest'])
    snapshot=records['9.1b']['evidence']['mixed_snapshot']
    def subject(value):
        return {k:value[k] for k in ('model_identity','scientific_digest','reset_digest') if k in value}|{
            'complete_profile_id':value['inputs']['reference']['profile']['complete_profile_id']}
    provenance=authority.check()
    statuses['9.6']=dict(source=subject(snapshot['initial']),enabled_target=subject(snapshot['state']),
        compatibility_source_model=records['9.2']['evidence']['transition']['model_identity'],
        expanded_target_four_surface_compatibility='not_transferred_from_source',C_PC_basin_policy='unselected',
        umbrella_compatibility='held_sixteen_unselected_cells',authority=[dict(contract_id=k,trace_digest=t['trace_digest'],
        support_disposition=t['rows'][0]['payload']['support_disposition']) for k,t in provenance['traces'].items()])
    names=required_paths()
    for name in tuple(names):
        if name.endswith(('.json','.json.xz')):
            refs=deep.read(name).get('source_bindings',[])
            names.update(refs if isinstance(refs,dict) else (r['path'] for r in refs))
    return b.seal(dict(schema='p9-cpc-review-v1',family='C_PC',realization_number=6,
        checkpoints=[dict(checkpoint=k,state='passed_pending_acceptance',user_accepted=False,execution=statuses[k]) for k in STEPS],
        source_bindings=b.bind(names),original_large_target_roles_excluded=['current','reset'],
        numerical_scope='pointwise_exact_PC_at_saved_inputs_with_staged_update_bounds_not_uniform_trajectory',
        performance=dict(exact_backend='flint',large_policy='certified_arb_256',caps_seconds=1800,
            original_event_attempt='incomplete_at_1800_seconds_no_native_credit',
            serialization_reuse='bounded_success_only_exact_JCS_bytes',
            matrix_cache='operation_scoped_exact_operands',schema_memo='bounded_success_only_exact_content',
            independent_math='vertex_Woodbury_reduction',source_pilot_seconds=large.read('source')['elapsed_seconds'],
            observed_cache=large.read('source')['execution']['cache_observations']),
        accepted_predecessor_families=['C_OS','C_CI','A_CI','A_PC','A_OS'],
        remaining_families=['C_CI_PC','A_CI_PC','C_RG2b','A_RG2b'],optional_completion='unselected',tranche10='deferred',
        user_accepted=False,aggregate_closed=False,full_GRC9V4_conformance=False))


def checked(root=b.ROOT,value=None):
    root=Path(root).resolve();value=json.loads((root/PATH).read_bytes()) if value is None else value
    b.check_digest(value)
    b.require(value['schema']=='p9-cpc-review-v1' and value['family']=='C_PC' and value['realization_number']==6
        and [r['checkpoint'] for r in value['checkpoints']]==list(STEPS)
        and all(r['state']=='passed_pending_acceptance' and r['user_accepted'] is False for r in value['checkpoints'])
        and all(value[k] is False for k in ('user_accepted','aggregate_closed','full_GRC9V4_conformance'))
        and value['original_large_target_roles_excluded']==['current','reset']
        and value['accepted_predecessor_families']==['C_OS','C_CI','A_CI','A_PC','A_OS']
        and value['remaining_families']==['C_CI_PC','A_CI_PC','C_RG2b','A_RG2b']
        and value['optional_completion']=='unselected' and value['tranche10']=='deferred','C_PC review scope')
    refs=value['source_bindings']
    b.require(len({r['path'] for r in refs})==len(refs) and required_paths()<={r['path'] for r in refs},'review source roster')
    for ref in refs:
        p=(root/ref['path']).resolve()
        from p9_cpc_acceptance import matches
        b.require(p.is_relative_to(root) and matches(root,ref['path'],ref['sha256']),'review source drift: '+ref['path'])
    rows={r['checkpoint']:r['execution'] for r in value['checkpoints']}
    b.require(rows['8.4g']['original_target_roles_excluded']==['current','reset']
        and rows['8.4g']['original_native_credit'] is False
        and value['performance']['exact_backend']=='flint' and value['performance']['caps_seconds']==1800
        and value['performance']['observed_cache']['solve_hits']>0,'scientific exclusion/compute scope')
    b.require(rows['8.4d']['successful_history_cells']==40 and rows['8.4e']['required_history_cells']==20
        and rows['8.4f']['required_history_cells']==24 and rows['8.4h']['actual_target_steps']==20
        and rows['8.4h']['covariant_target_steps']==16 and rows['8.4h']['native_events']==9
        and len(rows['8.4h']['update_error_bounds'])==40 and rows['8.5']['small_tests']==6
        and rows['8.5']['readmissions']==3 and rows['9.3']['counts']==dict(bounded_accepted=20,passed_pending_acceptance=4,unselected_not_executed=16)
        and all(rows[k]['tests']==v for k,v in integration.COUNTS.items()),'review coverage')
    b.require({r['contract_id'] for r in rows['9.6']['authority']}==set(authority.IDS)
        and all(r['support_disposition']=='indeterminate_requires_review' for r in rows['9.6']['authority']),'authority promotion')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('build','check'));args=parser.parse_args()
    if args.action=='build':
        value=build();checked(value=value);b.write_new(PATH,value)
    else:checked()
    print('C_PC bounded review passed; user acceptance pending')
