"""Read-only C_RG2b research, without authority overlay or numerical refresh."""
from pathlib import Path
from .basin import _bound_file
from .spark_crg2b_sc3_metadata import HISTORICAL_HELPER,reviewed_source_bytes
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_crg2b_metadata import checked_epoch,need
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/'
REPORT=BASE+'CRG2bResearchProgress.json'
REPORT_DIGEST='c3d641283e60bdbce96252a07be8f39acb626a4ad8afd80f47703de65f15644c'


def spark_crg2b_research_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound C_RG2b report')
    need(r['family']=='C_RG2b' and r['status']=='demonstrated_bounded_pending_review' and
         not r['accepted_authority'] and not r['native_completion'] and not r['G4_accepted'] and
         r['full_state']==['C'] and r['ordinary_duration']=='8' and
         not r['duration_choice']['universal_impossibility_claimed'] and
         not r['duration_choice']['same_completion_uniform_Lipschitz_inverse_at_32'] and r['full_dimension']==14 and r['proof']['relative_dimension']==14 and
         r['proof']['completion_relative'] and r['proof']['full_return_difference_bound'] and
         not r['proof']['section_C1_claimed'] and not r['proof']['geometry_history_transported'] and
         not r['proof']['earlier_family_trajectory_reused'],'C_RG2b research scope')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate C_RG2b source')
    for ref in r['sources']:
        if ref['path']==HISTORICAL_HELPER:reviewed_source_bytes(root,ref['path'],ref['sha256'])
        else:_bound_file(root,ref['path'],ref['sha256'])
    baseline=load_json_object(root/r['accepted_baseline']['path'])
    need(baseline['record_digest']==record_digest(baseline,'record_digest')==r['accepted_baseline']['record_digest'] and
         baseline['scope']['scientific_families']==r['accepted_scientific_families']==['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC'],
         'accepted baseline changed or research promoted')
    history=load_json_object(root/(BASE+'CRG2bRunHistory.json'))
    need(history['record_digest']==record_digest(history,'record_digest')==r['historical_baseline']['record_digest'] and
         history['schema']=='spark-completion-crg2b-run-history-v1' and
         not history['numerical_payloads_retained'] and not history['historical_payloads_rechecked_by_inspection'],
         'historical C_RG2b retention scope')
    for ref in history['generator_sources']:_bound_file(root,ref['path'],ref['sha256'])
    active_sources={ref['path'] for ref in r['sources']}
    for role in ('current','reset'):
        run=history['runs'][role]
        need(run['evidence_status']=='historical_summary_only' and run['former_path'] not in active_sources and
             run['execution_record_digest']==r['execution_digests'][role] and
             run['decision']==r['decisions'][role] and run['proof_digest']==digest(r['proof']),
             'historical baseline summary differs')
        need(r['elapsed_from_event'][role]==dict(entry=str(8*r['decisions'][role]['first_certified_entry']),
             completion=str(8*r['decisions'][role]['target_completion_step'])),'C_RG2b elapsed-time projection')
    need(r['decisions']['current']['local_gain']==1 and r['decisions']['reset']['local_gain']==0 and
         r['debt']['status']=='open_pending_scientific_adjudication','C_RG2b accounting/debt')
    faster=r['faster'];certificate=load_json_object(root/(BASE+'CRG2bFasterCertificate.json'))
    need(certificate['record_digest']==record_digest(certificate,'record_digest')==faster['certificate_digest'] and
         {k:v for k,v in certificate.items() if k!='record_digest'}==faster['proof'],'faster certificate projection')
    need(faster['entry']==390 and faster['completion']==392 and faster['ordinary_duration']=='8' and
         not faster['uniform_duration_32_certified'] and not faster['accepted_authority'] and
         faster['proof']['relative_dimension']==14 and faster['proof']['original_SC1_contract_unchanged'] and
         faster['proof']['component_radius']=='1/32768' and
         faster['decisions']['current']['local_gain']==1 and faster['decisions']['reset']['local_gain']==0 and
         faster['complete_fresh_trajectory_replays']==2,'faster C_RG2b scope')
    historical=load_json_object(root/(BASE+'CRG2bFasterRunHistory.json'))
    need(historical['record_digest']==record_digest(historical,'record_digest')==faster['history_digest'] and
         faster['status']=='historical_summary_only' and not faster['numerical_payloads_retained'] and
         not historical['numerical_payloads_retained'] and not historical['historical_payloads_rechecked_by_inspection'],
         'superseded finite-union retention scope')
    for ref in historical['generator_sources']:_bound_file(root,ref['path'],ref['sha256'])
    for role,row in historical['runs'].items():
        need(row['former_path'] not in active_sources and row['execution_record_digest']==faster['execution_digests'][role],
             'superseded finite-union summary differs')
    direct=r['direct'];certificate=load_json_object(root/(BASE+'CRG2bDirectCertificate.json'))
    need(certificate['record_digest']==record_digest(certificate,'record_digest')==direct['certificate_digest'] and
         {k:v for k,v in certificate.items() if k!='record_digest'}==direct['proof'],'direct certificate projection')
    need(r['selected_proof']=='direct_continuous_domain' and direct['entry']==390 and direct['completion']==392 and
         direct['last_executed_step']==392 and direct['retained_states']==784 and
         direct['supporting_trajectory_steps_after_completion']==0 and not direct['future_trajectory_required'] and
         direct['proof']['trajectory_inputs_to_domain_checker']==0 and direct['proof']['relative_dimension']==14 and
         direct['proof']['radius']=='1/4096' and direct['proof']['original_SC1_contract_unchanged'] and
         direct['proof']['all_parameters_certified_continuously'] and direct['proof']['full_return_difference_bound'] and
         direct['proof']['common_contraction']['both_H_consumers'] and not direct['proof']['section_C1_claimed'] and
         direct['complete_fresh_trajectory_replays']==2 and direct['decisions']['current']['local_gain']==1 and
         direct['decisions']['reset']['local_gain']==0 and not direct['accepted_authority'] and
         direct['ordinary_duration']=='8' and not direct['uniform_duration_32_certified'],
         'direct C_RG2b domain, duration, tail or accounting scope')
    value=dict(schema='grc9v4_spark_crg2b_research_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_crg2b_research_source(root,side,path):
    value=spark_crg2b_research_status(root,side);ref=next((r for r in value['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed C_RG2b source')
    return reviewed_source_bytes(Path(root),path,ref['sha256']),ref
