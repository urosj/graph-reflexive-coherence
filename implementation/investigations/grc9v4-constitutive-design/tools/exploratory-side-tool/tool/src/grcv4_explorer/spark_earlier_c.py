"""Read-only earlier C-family comparison; authenticate retained evidence only."""
from pathlib import Path
import json,lzma
from .basin import _bound_file
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_earlier_c_metadata import checked_epoch,need
from .spark_earlier_sc3_metadata import reviewed_source_bytes
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/earlier-closure/'
REPORT=BASE+'CEarlierResearch.json'
REPORT_DIGEST='38b6966aad65350055c3452b1d20094fc0701f44564bd0f758ea210563bd2373'
FAMILIES=['C_OS','C_CI','C_PC','C_CI_PC']


def spark_earlier_c_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound earlier C-family report')
    need(r['status']=='demonstrated_bounded_pending_review' and not r['accepted_authority'] and
         not r['native_completion'] and not r['G4_accepted'] and r['additional_event_gain']==0,'earlier witness scope')
    need(r['families']==FAMILIES and r['ordinary_duration']=='32' and r['window_elapsed']=='64', 'family or duration changed')
    need(len({x['path']for x in r['sources']})==len(r['sources']),'duplicate source')
    for ref in r['sources']:reviewed_source_bytes(root,ref['path'],ref['sha256'])
    proofs=load_json_object(root/(BASE+'CEarlierProofs.json'))
    need(proofs['record_digest']==record_digest(proofs,'record_digest')==r['proofs_digest'],'whole-domain proof identity')
    for family in FAMILIES:
        p=proofs['proofs'][family]
        need(p['full_dimension']==(60 if family in ('C_PC','C_CI_PC')else 14) and
             p['trajectory_inputs_to_domain_checker']==0 and p['supporting_trajectory_steps_after_completion']==0 and
             not p['accepted_authority'] and not p['native_completion'],'full physical proof scope')
        for role in ('current','reset'):
            ref=proofs['prefixes'][family+'/'+role];v=json.loads(lzma.decompress((root/ref['path']).read_bytes()))
            need(v['record_digest']==record_digest(v,'record_digest')==ref['record_digest'],'selected prefix identity')
            end=376 if role=='current' else 377
            need(v['completion']==v['last_retained_step']==v['last_required_execution_step']==end and
                 v['entry']==end-2 and len(v['observations'])==end and
                 v['supporting_trajectory_steps_after_completion']==0 and v['additional_event_gain']==0 and
                 v['local_gain']==int(role=='current') and not v['reset_earns_live_gain'] and
                 not v['accepted_authority'] and not v['native_completion'],'short-prefix or gain scope')
            if family=='C_OS':need(v['last_executed_step']==end,'fresh OS endpoint')
            else:need(v['last_executed_step']==v['origin']['original_last_executed_step']==(851 if role=='current'else 819),'original execution relabelled')
    need(r['existing_A_OS']['current_completion']==377 and r['existing_A_OS']['reset_completion']==374 and
         not r['existing_A_OS']['rerun'],'existing A_OS result changed')
    value=dict(schema='grc9v4_spark_earlier_c_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_earlier_c_source(root,side,path):
    value=spark_earlier_c_status(root,side)
    ref=next((r for r in value['source_refs']if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed earlier-closure source')
    return reviewed_source_bytes(root,path,ref['sha256']),ref
