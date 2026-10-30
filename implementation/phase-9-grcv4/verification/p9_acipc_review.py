"""Join source-bound A_CI_PC executions without widening numerical or acceptance scope."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os
from dataclasses import replace
from pathlib import Path
import json
import p984d_acipc as deep
import p984ef_acipc as covariance
import p984h_acipc as n
import p984h_acipc_covariance as cov
import p984h_acipc_actual as actual
import p9_acipc_large_charge as charge
import p985_acipc as life
import p99_acipc as integration
import p99_acipc_authority as authority
import p9_acipc_historical as historical
from p9_acipc_execution_scope import science_scope

b=deep.b
SELF=b.HERE+'p9_acipc_review.py'
PATH=b.BASE+'P9-ACIPC-Tranches8-9-Review.json'
STEPS=('8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end',
       '9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6')
GUIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/ACIPCEighthRealization.md'


def required_paths():
    helpers=('p984d_acipc','p984d_acipc_feasibility','p984ef_acipc','p984g_acipc','p984g_acipc_companion',
        'p984h_acipc','p984h_acipc_actual','p984h_acipc_covariance','p984h_acipc_math','p985_acipc','p99_acipc',
        'p99_acipc_authority','p9_acipc_campaign','p9_acipc_compute','p9_acipc_historical',
        'p9_acipc_integration_compute','p9_acipc_large_charge','p9_acipc_targets','p9_acipc_execution_scope','p9_acipc_review','test_p9_acipc_science','test_p9_acipc_review')
    return {SELF,GUIDE,historical.PATH,*historical.CHANGED,*historical.ADDITIONS,
        *(b.HERE+p+'.py' for p in helpers),historical.SIDE+'phase9-web/acipc.js',
        b.BASE+'P9-ACIPC-Tranches8-9-Plan.md',b.BASE+'P9-ACIPC-ScientificReview.md',
        'scripts/evidence_storage.py','artifact-storage.json',
        n.compute.PREFLIGHT,life.integration_compute.PREFLIGHT,
        deep.INPUTS,deep.PREFLIGHT,deep.RESULTS,deep.feasibility.SOURCE,
        *(p for k in ('e','f') for p in covariance.paths(k)),
        n.g.PREPARED,b.BASE+'P9-8.4g-ACIPCInvestigation.json',
        charge.ORIGINAL_INPUTS,charge.ORIGINAL_RESULTS,charge.ORIGINAL_NATIVE,charge.INPUTS,charge.RESULTS,charge.NATIVE,charge.ACTUAL,
        *(b.BASE+'P9-8.4h-ACIPC-prepared_target-'+r+'.json.xz' for r in n.ROLES),
        *(charge.filename(s,r) for s in ('source','prepared_target','final') for r in n.ROLES),charge.filename('event'),
        *(charge.filename('step',r,i) for r in n.ROLES for i in range(1,11)),cov.INPUTS,
        *(cov.path(k,s) for k in cov.KINDS for s in ('event',*n.ROLES)),life.INPUTS,life.path('small'),life.path('large'),
        *(integration.filename(k) for k in integration.GROUPS),integration.BASE+'P9-9.3-ACIPCMatrix.json',authority.PATH}


def science():
    original=deep.read(b.BASE+'P9-8.4g-ACIPCInvestigation.json')
    b.check_digest(original);b.check_bindings(original['source_bindings'])
    negative=[(r.get('graph',r.get('subject')),r['role']) for r in original['cases'] if r['negative_vertices']]
    b.require(negative==[('target','reset')],'original large exclusion changed')
    selected=deep.read(charge.INPUTS);proof=deep.read(charge.RESULTS)
    b.check_digest(selected);b.check_digest(proof);b.check_bindings(selected['source_bindings'])
    operands=list(map(n.q,selected['actual_source_split_operands']))
    b.require(selected['selection']==charge.select(selected['constraints'],operands)
        and selected['selection']['shares']==['7/32','13/32','3/8']
        and selected['original_evolved_split_charge_delta']==dict(current='1/18014398509481984',reset='0')
        and not selected['changed_tolerances'] and not selected['changed_step_size']
        and proof['manifest_digest']==selected['record_digest'] and proof['ready_for_native']
        and proof['native_steps']==proof['native_events']==0,'charge companion selection/proof scope')
    for row in proof['cases']:
        b.require(not row['negative_vertices'] and not row['unresolved_vertices'] and n.q(row['minimum_lower'])>0,'prepared positivity')
    actual.check()
    return dict(original_target_roles_excluded=['reset'],original_native_credit=False,
        source_reuse=selected['exact_source_reuse'],companion=selected['companion'],selection=selected['selection'],
        first_companion_evolved_charge_delta=selected['original_evolved_split_charge_delta'],
        pointwise_precision_bits=n.g.BITS,full_joint_root=True,uniform_trajectory_enclosure=False)


def segment_scope(value, manifest, segment, role, index=1):
    b.check_digest(value)
    wanted=manifest['source_manifest_digest'] if segment=='source' else manifest['record_digest']
    b.require(value['manifest_digest']==wanted and (value['segment'],value['role'],value['index'])==(segment,role,index)
        and value['outcome']=='completed' and not value['user_accepted'] and not value['aggregate_closed']
        and 0<value['elapsed_seconds']<=3600 and value['compute_policy']['exact_backend']=='flint'
        and value['compute_policy']['numerical_policy']=='certified_arb_256','native segment scope/policy')
    count=14 if segment=='event' else 1 if segment=='final' else 3
    b.require(len(value['native_root_timings'])==count,'fresh native root count')
    return dict(path=n.filename(segment,role,index),seconds=value['elapsed_seconds'])


def checked_native_segment(task):
    # A fresh spawned worker enters the same explicit scope as the serial
    # checker. Every predecessor is checked by content, never inferred from
    # worker order; all ten edges of each chain are mandatory in large().
    segment,role,index=task
    with n.compute_worker(),science_scope():
        manifest=deep.read(n.INPUTS);b.check_digest(manifest)
        value=n.read(segment,role,index)
        timing=segment_scope(value,manifest,segment,role,index)
        execution=value['execution'];errors=None
        if segment in ('source','prepared_target'):
            initial=n.prepared('source' if segment=='source' else 'target')
            b.require(execution['before']==n.r.role_input(initial.inputs,role,dt=n.DT).to_payload(),'prerequisite subject')
        else:
            event=n.read('event');b.check_digest(event)
            if segment=='step' and index==1:
                before=n.r.role_input(n.r.state(event['execution']['state']).inputs,role,dt=n.DT)
                predecessor=event
            else:
                predecessor=n.read('step',role,10 if segment=='final' else index-1)
                b.check_digest(predecessor)
                before=b.GeometryStageInputs.from_payload(predecessor['execution']['after'])
            if segment=='final':before=replace(before,dt=0)
            b.require(execution['before']==before.to_payload()
                and execution['event_record_digest']==event['record_digest']
                and execution['predecessor_digest']==predecessor['record_digest'],'continuation chain')
        if segment=='final':
            b.require(execution['read_only'],'final read scope')
            n.check_read(before,execution['read'])
        else:
            n.check_step(execution)
            cert=execution['pointwise_certificate']
            b.require(n.q(cert['resource_lower'])>=0 and cert['pointwise_at_saved_input']
                and not cert['uniform_trajectory_enclosure'],'pointwise update scope')
            errors=cert['errors']
            if segment=='source':
                b.require(manifest['exact_source_reuse'][role]==dict(path=n.filename(segment,role),record_digest=value['record_digest'])
                    and all(execution['trigger'][k] for k in ('small_gradient','strict_hessian_condition')),'source reuse/trigger')
        return dict(timing=timing,errors=errors)


def checked_covariance(kind):
    with n.compute_worker(),science_scope():
        manifest=deep.read(cov.INPUTS)
        b.require(manifest==cov.manifest(),'covariance manifest drift')
        maximum=0.;errors={}
        def leaves(value):
            if isinstance(value,dict):
                for child in value.values():yield from leaves(child)
            else:yield value
        for segment in ('event',*n.ROLES):
            value=cov.read(kind,segment);found=cov.check(value,kind,segment,manifest)
            b.require(found==value['covariance_errors'],'covariance errors drift')
            maximum=max(maximum,*leaves(found))
            if segment!='event':errors[cov.path(kind,segment)]=value['execution']['pointwise_certificate']['errors']
        return dict(kind=kind,maximum=maximum,errors=errors)


def large():
    manifest=deep.read(n.INPUTS);n.check_manifest(manifest)
    event=n.read('event');seed,source=n.source_state();execution=event['execution']
    target=n.check_event(seed,execution['case'],execution['event'])
    b.require(execution['case']==n.case_for(seed) and execution['state']==target.to_payload()
        and execution['source_record_digest']==source['record_digest'] and execution['rollback_exact'],'event/source lineage')
    timings=[segment_scope(event,manifest,'event','current')];errors={}
    tasks=[(segment,role,1) for role in n.ROLES for segment in ('source','prepared_target','final')]
    tasks += [('step',role,index) for role in n.ROLES for index in range(1,11)]
    workers=min(12,os.cpu_count() or 1)
    # Only retained checks run here; no new native trajectories or weakened
    # comparisons. Spawn avoids inheriting arithmetic contexts or cache state.
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        native=[pool.submit(checked_native_segment,task) for task in tasks]
        mapped=[pool.submit(checked_covariance,kind) for kind in cov.KINDS]
        for task,future in zip(tasks,native,strict=True):
            result=future.result();timings.append(result['timing'])
            if result['errors'] is not None:errors[result['timing']['path']]=result['errors']
            print('retained native check passed: '+str(task),flush=True)
        maximum=0.
        for kind,future in zip(cov.KINDS,mapped,strict=True):
            result=future.result();b.require(result['kind']==kind,'covariance job identity')
            maximum=max(maximum,result['maximum']);errors.update(result['errors'])
            print('retained covariance check passed: '+kind,flush=True)
    b.require(len(timings)==27 and len(errors)==30,'complete saved-input review roster')
    return dict(vertices=107,edges=407,native_events=4,prerequisite_steps=4,actual_target_steps=20,
        covariant_target_steps=6,final_reads=2,maximum_covariance_error=maximum,update_error_bounds=errors,
        large_covariance_selected=list(cov.KINDS),large_covariance_deferred_unexecuted=list(cov.DEFERRED),
        uniform_trajectory_enclosure=False,timings=timings,retained_check_workers=workers)


def build():
    with n.compute_worker(),science_scope():
        statuses={'8.4d':deep.check(deep.read(deep.INPUTS),deep.read(deep.RESULTS))}
        for k in ('e','f'):
            ip,rp=covariance.paths(k);statuses['8.4'+k]=covariance.check(deep.read(ip),deep.read(rp))[0]
        statuses['8.4g']=science();statuses['8.4h']=large()
        lm=deep.read(life.INPUTS)
        for s in ('small','large'):life.check(lm,deep.read(life.path(s)))
    records={k:integration.check(k) for k in integration.GROUPS}
    matrix=deep.read(integration.BASE+'P9-9.3-ACIPCMatrix.json');b.require(matrix==integration.matrix(),'compatibility matrix')
    statuses.update({'8.4i':dict(handoff='exact_retained_records',new_acceptance=False),
        '8.5':dict(small_tests=6,large_replay=True,readmissions=3,both_roles=True),
        '8.6':dict(conformance='bounded_A_CI_PC',optional_completion='unselected',universal_graph_claim=False),
        'tranche8_end':dict(bounded_execution='passed',user_acceptance='pending'),
        '9.3':dict(counts=matrix['counts'])})
    for k,v in records.items():statuses[k]=dict(tests=v['tests_run'],execution_digest=v['record_digest'])
    snapshot=records['9.1b']['evidence']['mixed_snapshot']
    def subject(v):return dict(model_identity=v['model_identity'],scientific_digest=v['scientific_digest'],complete_profile_id=v['inputs']['reference']['profile']['complete_profile_id'])
    proven=authority.check()
    statuses['9.6']=dict(source=subject(snapshot['initial']),enabled_target=subject(snapshot['state']),
        compatibility_source_model=records['9.2']['evidence']['transition']['model_identity'],
        expanded_target_four_surface_compatibility='not_transferred_from_source',A_CI_PC_basin_policy='unselected',
        umbrella_compatibility='held_eight_unselected_cells',authority=[dict(contract_id=k,trace_digest=t['trace_digest'],
        support_disposition=t['rows'][0]['payload']['support_disposition']) for k,t in proven['traces'].items()])
    names=required_paths()
    for name in tuple(names):
        if name.endswith(('.json','.json.xz')):
            refs=deep.read(name).get('source_bindings',[]);names.update(refs if isinstance(refs,dict) else (r['path'] for r in refs))
    return b.seal(dict(schema='p9-acipc-review-v1',family='A_CI_PC',realization_number=8,
        checkpoints=[dict(checkpoint=k,state='passed_pending_acceptance',user_accepted=False,execution=statuses[k]) for k in STEPS],
        source_bindings=b.bind(names),accepted_predecessor_families=['C_OS','C_CI','A_CI','A_PC','A_OS','C_PC','C_CI_PC'],
        remaining_families=['C_RG2b','A_RG2b'],optional_completion='unselected',tranche10='deferred',
        numerical_scope='pointwise_joint_root_and_staged_updates_at_saved_inputs_not_uniform_trajectory',
        user_accepted=False,aggregate_closed=False,full_GRC9V4_conformance=False))


def checked(root=b.ROOT,value=None):
    root=Path(root).resolve();value=json.loads((root/PATH).read_bytes()) if value is None else value
    b.check_digest(value)
    b.require(value['schema']=='p9-acipc-review-v1' and value['family']=='A_CI_PC' and value['realization_number']==8
        and [r['checkpoint'] for r in value['checkpoints']]==list(STEPS)
        and all(r['state']=='passed_pending_acceptance' and r['user_accepted'] is False for r in value['checkpoints'])
        and all(value[k] is False for k in ('user_accepted','aggregate_closed','full_GRC9V4_conformance'))
        and value['remaining_families']==['C_RG2b','A_RG2b'] and value['tranche10']=='deferred','bounded review scope')
    refs=value['source_bindings'];b.require(len(refs)==len({r['path'] for r in refs}) and required_paths()<={r['path'] for r in refs},'review source roster')
    from scripts.evidence_storage import entries, restore
    stored={row['path'] for row in entries(root)}
    for ref in refs:
        if ref['path'] in stored and not (root/ref['path']).exists():restore(root,prefix=ref['path'])
    from p9_acipc_acceptance import matches
    for ref in refs:
        path=(root/ref['path']).resolve()
        b.require(path.is_relative_to(root) and matches(root,ref['path'],ref['sha256']),
                  'review source drift: '+ref['path'])
    rows={r['checkpoint']:r['execution'] for r in value['checkpoints']}
    b.require(rows['8.4g']['original_target_roles_excluded']==['reset']
        and rows['8.4g']['selection']['shares']==['7/32','13/32','3/8']
        and rows['8.4h']['large_covariance_selected']==['combined','reflect','rotate']
        and rows['8.4h']['large_covariance_deferred_unexecuted']==['edge_order','node_order','relabel','signed','rotate_twice'], 'scientific exclusion/selected covariance')
    b.require(rows['8.4d']['cases_passed']==20 and rows['8.4d']['source_witnesses']==2
        and rows['8.4e']['required_history_cells']==20 and rows['8.4f']['required_history_cells']==24
        and rows['8.4h']['actual_target_steps']==20 and rows['8.4h']['covariant_target_steps']==6
        and len(rows['8.4h']['update_error_bounds'])==30 and rows['8.5']['small_tests']==6
        and rows['9.3']['counts']==dict(bounded_accepted=28,passed_pending_acceptance=4,unselected_not_executed=8)
        and all(rows[k]['tests']==count for k,count in integration.COUNTS.items()),'bounded coverage')
    b.require({r['contract_id'] for r in rows['9.6']['authority']}==set(authority.IDS)
        and all(r['support_disposition']=='indeterminate_requires_review' for r in rows['9.6']['authority']),'authority promotion')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('build','check'));args=parser.parse_args()
    if args.action=='build':
        value=build();checked(value=value);b.write_new(PATH,value)
    else:checked()
    print('A_CI_PC bounded retained review passed; user acceptance pending')
