"""Bounded seventh-realization reconciliation from immutable native execution records."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

import p984d_ccipc as deep
import p984ef_ccipc as covariance
import p984h_ccipc as large
import p984h_ccipc_covariance as large_covariance
import p985_ccipc as lifecycle
import p99_ccipc as integration
import p99_ccipc_authority as authority
import p9_ccipc_historical as historical
import p9_ccipc_execution_epoch as epoch
import p9_ccipc_large_charge as charge
import p9_ccipc_evidence as evidence
import p9_ccipc_event_reuse as event_reuse
import p9_ccipc_raw_store as raw_store
import p9_ccipc_pointwise as pointwise
import p9_ccipc_compute as compute
import p9_ccipc_integration_compute as integration_compute
import p984h_ccipc_actual as actual
from p9_cpc_covariance_compute import wire_reuse

b=deep.b
SELF=b.HERE+'p9_ccipc_review.py'
TEST=b.HERE+'test_p9_ccipc_review.py'
CORE_TEST=b.HERE+'test_p9_ccipc_science.py'
GUIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/CCIPCSeventhRealization.md'
PATH=b.BASE+'P9-CCIPC-Tranches8-9-Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end',
       '9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')


def large_paths():
    return [*(charge.filename(s,r) for s in ('source','prepared_target') for r in large.ROLES),
        charge.filename('event'),*(charge.filename('step',r,i) for r in large.ROLES for i in range(1,11)),
        *(charge.filename('final',r) for r in large.ROLES)]


def required_paths():
    helpers=('p984d_ccipc','p984ef_ccipc','p984g_ccipc','p984g_ccipc_companion',
        'p984h_ccipc','p984h_ccipc_actual','p984h_ccipc_covariance','p984h_ccipc_math',
        'p985_ccipc','p99_ccipc','p99_ccipc_authority','p9_ccipc_campaign','p9_ccipc_capture',
        'p9_ccipc_compute','p9_ccipc_evidence','p9_ccipc_execution_epoch','p9_ccipc_historical',
        'p9_ccipc_integration_compute','p9_ccipc_large_charge','p9_ccipc_large_profile',
        'p9_ccipc_pointwise','p9_ccipc_targets','p9_ccipc_event_reuse','p9_ccipc_raw_store')
    return {SELF,TEST,CORE_TEST,GUIDE,authority.PATH,authority.SELF,historical.PATH,historical.SELF,
        epoch.PATH,epoch.SELF,*historical.CHANGED,*historical.ADDITIONS,
        historical.SIDE+'phase9-web/ccipc.js',b.BASE+'P9-CCIPC-Tranches8-9-Plan.md',
        'artifact-storage.json','scripts/evidence_storage.py',
        *(b.HERE+name+'.py' for name in helpers),
        *(b.HERE+name+'.py' for name in ('test_p984g_ccipc','test_p984h_ccipc',
            'test_p984h_ccipc_math','test_p9_ccipc_capture','test_p9_ccipc_event_reuse')),
        b.BASE+'P9-CCIPC-ScientificReview.md',compute.PREFLIGHT,integration_compute.PREFLIGHT,event_reuse.PREFLIGHT,
        raw_store.TEST,raw_store.PREFLIGHT,raw_store.FAILURE,
        b.BASE+'P9-CCIPC-LargeRootProfile-Incomplete.json.xz',pointwise.PATH,pointwise.PILOT,
        deep.INPUTS,deep.RESULTS,deep.PREFLIGHT,deep.PREFLIGHT+'.xz',large.g.PREPARED,large.g.RESULTS,
        charge.ORIGINAL_INPUTS,charge.ORIGINAL_RESULTS,charge.ORIGINAL_NATIVE,
        charge.INPUTS,charge.RESULTS,charge.NATIVE,charge.ACTUAL,
        *(b.BASE+'P9-8.4h-CCIPC-prepared_target-'+role+'.json.xz' for role in large.ROLES),
        large_covariance.INPUTS,lifecycle.INPUTS,
        integration.BASE+'P9-9.3-CCIPCMatrix.json',*large_paths(),
        *(p for k in ('e','f') for p in covariance.paths(k)),
        *(large_covariance.path(k,s) for k in large_covariance.KINDS for s in ('event',*large.ROLES)),
        *(lifecycle.path(s) for s in ('small','large')),*(integration.filename(k) for k in integration.GROUPS)}


def check_large():
    m=deep.read(large.INPUTS);large.check_manifest(m)
    b.require(m['schema']=='p984h-ccipc-inputs-v1' and m['family']=='C_CI_PC'
        and m['numerical_policy']=='certified_arb_256' and m['independent_precision_bits']==large.g.BITS
        and m['scope']==dict(source_steps=2,prepared_target_steps=2,events=1,target_steps=20,final_reads=2),
        'large manifest scope')
    event=large.read('event');seed,source=large.source_state();e=event['execution']
    target=large.check_event(seed,e['case'],e['event'])
    b.require(e['case']==large.case_for(seed) and e['state']==target.to_payload()
        and e['checkpoint']==e['event']['checkpoint'] and e['source_record_digest']==source['record_digest']
        and e['rollback_exact'] and e['stale_failure'] and e['native_events']==1 and e['native_steps']==0,'actual event binding')
    reference_lineage=evidence.reference_lineage(seed,e['case'],e['event'])
    ledger=pointwise.check()
    errors={row['native_path']:row['errors'] for row in ledger['cases']};timings=[]
    def scope(v,segment,role,index=1):
        b.check_digest(v)
        expected_manifest=m['source_manifest_digest'] if segment=='source' else m['record_digest']
        if segment=='source':
            b.require(m['exact_source_reuse'][role]==dict(path=charge.filename(segment,role),
                record_digest=v['record_digest']),'source reuse identity')
        else:
            b.require(v['source_equivalence']==dict(path=epoch.PATH,record_digest=epoch.checked()['record_digest']),
                'numerical execution source equivalence')
        b.require(v['schema']=='p984h-ccipc-segment-v1' and v['manifest_digest']==expected_manifest
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
        before=large.r.role_input(target.inputs,role,dt=large.DT);previous=event['record_digest']
        for index in range(1,11):
            v=large.read('step',role,index);scope(v,'step',role,index);step=v['execution']
            b.require(step['before']==before.to_payload() and step['event_record_digest']==event['record_digest']
                and step['predecessor_digest']==previous,'complete target continuation lineage')
            before=large.check_step(step);previous=v['record_digest']
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
            if segment=='event':
                transformed,case,_=large_covariance.subject(kind)
                evidence.reference_lineage(transformed,case,v['execution']['event'])
            timings.append(dict(path=large_covariance.path(kind,segment),seconds=v['seconds'],native_seconds=v['execution'].get('native_seconds')))
    graph=target.inputs.geometry.reference.graph
    b.require((len(graph.live_node_ids),len(graph.live_edge_ids))==(107,407),'larger graph size')
    return dict(vertices=107,edges=407,native_events=4,prerequisite_steps=4,actual_target_steps=20,
        covariant_target_steps=6,successful_history_cells=8,final_reads=2,maximum_covariance_error=maximum,
        update_error_bounds=errors,pointwise_record_digest=ledger['record_digest'],
        reference_lineage=reference_lineage,large_covariance_selected=list(large_covariance.KINDS),
        large_covariance_deferred_unexecuted=list(large_covariance.DEFERRED),
        large_covariance_scope='user_prioritized_subset',timings=timings)


def science():
    g=large.g
    original=deep.read(g.PREPARED);exclusion=deep.read(g.RESULTS)
    b.check_digest(exclusion);b.check_bindings(exclusion['source_bindings'])
    b.require(exclusion['schema']=='p984g-ccipc-original-feasibility-v1'
        and exclusion['ready_for_native'] is False and exclusion['native_steps']==exclusion['native_events']==0,
        'original exclusion scope')
    first=deep.read(charge.ORIGINAL_INPUTS);first_result=deep.read(charge.ORIGINAL_RESULTS)
    selected=deep.read(charge.INPUTS);result=deep.read(charge.RESULTS)
    for manifest,record in ((first,first_result),(selected,result)):
        b.check_digest(manifest);b.check_digest(record);b.check_bindings(manifest['source_bindings'])
        b.require(record['manifest_digest']==manifest['record_digest'] and record['ready_for_native']
            and record['native_steps']==record['native_events']==0
            and not manifest['changed_tolerances'] and not manifest['changed_step_size'],
            'separate companion scientific scope')
    for declaration,record in ((original,exclusion),(first['adjusted'],first_result),(selected['adjusted'],result)):
        b.require([(row['graph'],row['role']) for row in record['cases']]==
            [(graph,role) for graph in ('source','target') for role in large.ROLES], 'oracle case roster')
        for row in record['cases']:
            b.require(row['subject_digest']==b.digest(declaration[row['graph']])
                and row['dt']==large.DT and 1<=row['iterations']<=12,'oracle saved operands')
            if record is exclusion and row['graph']=='target':
                b.require(not row['first_step_nonnegative'] and row['negative_resources']
                    and all(g.q(x['upper'])<0 for x in row['negative_resources']),'strict original target exclusion')
            else:b.require(row['first_step_nonnegative'] and not row['negative_resources']
                and not row['unresolved_resources'],'positive companion oracle')
    operands=list(map(g.q,selected['actual_source_split_operands']))
    b.require(selected['selection']==charge.select(first['constraints'],operands)
        and selected['selection']['shares']==['5/16','5/16','3/8']
        and selected['adjusted']['source']==first['adjusted']['source']
        and selected['original_prepared_target_reused'] is False
        and selected['original_evolved_split_charge_delta']==dict(current='-1/9007199254740992',reset='0'),
        'exact evolved-source allocation selection')
    adjusted,identity=large.companion.companion(selected['selection']['shares'],True)
    b.require(adjusted==selected['adjusted'] and identity==selected['companion'],'selected companion construction')
    for i,role in enumerate(large.ROLES):
        old=operands[i]
        b.require(sum((g.q(float(old*g.q(w))) for w in selected['selection']['shares']),g.q(0))==old,
            'selected represented split charge')
        reuse=selected['exact_source_reuse'][role]
        b.require(reuse==dict(path=charge.filename('source',role),record_digest=large.read('source',role)['record_digest']),
            'source native record reuse')
    b.require(result['source_oracle_exact_reuse']==first_result['record_digest']
        and result['cases'][:2]==first_result['cases'][:2],'source oracle reuse')
    actual.check()
    return dict(original_target_roles_excluded=list(large.ROLES),original_native_credit=False,
        first_companion_evolved_charge_delta=selected['original_evolved_split_charge_delta'],
        first_companion_event_credit=False,companion=selected['companion'],
        exact_source_reuse=selected['exact_source_reuse'],selection=selected['selection'],
        ready_for_8_4h=True,pointwise_precision_bits=g.BITS,
        independent_equations='vertex_reduced_Arb_joint_CI_PC_fixed_old_carrier_with_whole_chart_bounds')


def restore_inputs(root):
    from scripts.evidence_storage import restore
    restore(Path(root),prefix=b.BASE+'P9-8.4d-CCIPC')


def build():
    restore_inputs(b.ROOT)
    diagnostic_store=raw_store.checked()
    with epoch.numerical_campaign(),charge.context(),large.compute_worker():
        statuses={'8.4d':deep.check(deep.read(deep.INPUTS),deep.read(deep.RESULTS))}
        for k in ('e','f'):
            ip,rp=covariance.paths(k);statuses['8.4'+k]=covariance.check(deep.read(ip),deep.read(rp))[0]
        statuses['8.4g']=science();statuses['8.4h']=check_large()
        lm=deep.read(lifecycle.INPUTS)
        for segment in ('small','large'):lifecycle.check(lm,deep.read(lifecycle.path(segment)))
    records={k:integration.check(k) for k in integration.GROUPS}
    matrix=deep.read(integration.BASE+'P9-9.3-CCIPCMatrix.json')
    b.require(matrix==integration.matrix(),'compatibility matrix drift')
    statuses.update({'8.4i':dict(handoff='exact_retained_records',predecessor_accepted=True,new_acceptance=False),
        '8.5':dict(small_tests=6,large_replay=True,readmissions=3,both_roles=True),
        '8.6':dict(conformance='bounded_C_CI_PC',optional_completion='unselected',universal_graph_claim=False),
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
        expanded_target_four_surface_compatibility='not_transferred_from_source',C_CI_PC_basin_policy='unselected',
        umbrella_compatibility='held_twelve_unselected_cells',authority=[dict(contract_id=k,trace_digest=t['trace_digest'],
        support_disposition=t['rows'][0]['payload']['support_disposition']) for k,t in provenance['traces'].items()])
    names=required_paths()
    for name in tuple(names):
        if name.endswith(('.json','.json.xz')):
            refs=deep.read(name).get('source_bindings',[])
            names.update(refs if isinstance(refs,dict) else (r['path'] for r in refs))
    return b.seal(dict(schema='p9-ccipc-review-v1',family='C_CI_PC',realization_number=7,
        checkpoints=[dict(checkpoint=k,state='passed_pending_acceptance',user_accepted=False,execution=statuses[k]) for k in STEPS],
        source_bindings=b.bind(names),original_large_target_roles_excluded=['current','reset'],
        numerical_scope='pointwise_joint_CI_PC_at_saved_inputs_with_staged_update_bounds_not_uniform_trajectory',
        performance=dict(exact_backend='flint',large_policy='certified_arb_256',caps_seconds=3600,
            root_warm_start=False,unchanged_tolerances=True,
            selected_covariance_harness_roots=12,baseline_harness_roots=14,
            event_harness_parity_digest=event_reuse.checked()['record_digest'],
            diagnostic_save_preflight_digest=diagnostic_store['record_digest'],
            serialization_reuse='bounded_success_only_exact_JCS_bytes',
            matrix_cache='operation_scoped_exact_operands',schema_memo='bounded_success_only_exact_content',
            independent_math='vertex_Woodbury_reduction',source_pilot_seconds=large.read('source')['elapsed_seconds'],
            observed_cache=large.read('source')['execution']['cache_observations']),
        accepted_predecessor_families=['C_OS','C_CI','A_CI','A_PC','A_OS','C_PC'],
        remaining_families=['A_CI_PC','C_RG2b','A_RG2b'],optional_completion='unselected',tranche10='deferred',
        user_accepted=False,aggregate_closed=False,full_GRC9V4_conformance=False))


def checked(root=b.ROOT,value=None):
    root=Path(root).resolve();restore_inputs(root)
    value=json.loads((root/PATH).read_bytes()) if value is None else value
    b.check_digest(value)
    b.require(value['schema']=='p9-ccipc-review-v1' and value['family']=='C_CI_PC' and value['realization_number']==7
        and [r['checkpoint'] for r in value['checkpoints']]==list(STEPS)
        and all(r['state']=='passed_pending_acceptance' and r['user_accepted'] is False for r in value['checkpoints'])
        and all(value[k] is False for k in ('user_accepted','aggregate_closed','full_GRC9V4_conformance'))
        and value['original_large_target_roles_excluded']==['current','reset']
        and value['accepted_predecessor_families']==['C_OS','C_CI','A_CI','A_PC','A_OS','C_PC']
        and value['remaining_families']==['A_CI_PC','C_RG2b','A_RG2b']
        and value['optional_completion']=='unselected' and value['tranche10']=='deferred','C_CI_PC review scope')
    refs=value['source_bindings']
    b.require(len({r['path'] for r in refs})==len(refs) and required_paths()<={r['path'] for r in refs},'review source roster')
    for ref in refs:
        p=(root/ref['path']).resolve()
        from p9_ccipc_acceptance import matches
        b.require(p.is_relative_to(root) and matches(root,ref['path'],ref['sha256']),'review source drift: '+ref['path'])
    rows={r['checkpoint']:r['execution'] for r in value['checkpoints']}
    diagnostic_store=json.loads((root/raw_store.PREFLIGHT).read_bytes());b.check_digest(diagnostic_store)
    b.require(value['performance']['diagnostic_save_preflight_digest']==diagnostic_store['record_digest']
        and diagnostic_store['outcome']=='passed' and diagnostic_store['tests']==4
        and diagnostic_store['native_roots_reused'] is False
        and diagnostic_store['numerical_behavior_changed'] is False,'private diagnostic save scope')
    b.require(rows['8.4g']['original_target_roles_excluded']==['current','reset']
        and rows['8.4g']['original_native_credit'] is False
        and value['performance']['exact_backend']=='flint' and value['performance']['caps_seconds']==3600
        and value['performance']['observed_cache']['solve_hits']>0
        and rows['8.4g']['selection']['shares']==['5/16','5/16','3/8']
        and rows['8.4g']['first_companion_event_credit'] is False
        and rows['8.4h']['reference_lineage']==dict(current=True,reset=True,fresh_root_source=True,exact_represented_charge=True),'scientific exclusion/compute scope')
    b.require(rows['8.4d']['successful_history_cells']==40 and rows['8.4e']['required_history_cells']==20
        and rows['8.4f']['required_history_cells']==24 and rows['8.4h']['actual_target_steps']==20
        and rows['8.4h']['covariant_target_steps']==6 and rows['8.4h']['native_events']==4
        and rows['8.4h']['large_covariance_selected']==['combined','reflect','rotate']
        and rows['8.4h']['large_covariance_deferred_unexecuted']==['edge_order','node_order','relabel','signed','rotate_twice']
        and rows['8.4h']['large_covariance_scope']=='user_prioritized_subset'
        and len(rows['8.4h']['update_error_bounds'])==30 and rows['8.5']['small_tests']==6
        and rows['8.5']['readmissions']==3 and rows['9.3']['counts']==dict(bounded_accepted=24,passed_pending_acceptance=4,unselected_not_executed=12)
        and all(rows[k]['tests']==v for k,v in integration.COUNTS.items()),'review coverage')
    b.require({r['contract_id'] for r in rows['9.6']['authority']}==set(authority.IDS)
        and all(r['support_disposition']=='indeterminate_requires_review' for r in rows['9.6']['authority']),'authority promotion')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('build','check'));args=parser.parse_args()
    if args.action=='build':
        value=build();checked(value=value);b.write_new(PATH,value)
    else:checked()
    print('C_CI_PC bounded review passed; user acceptance pending')
