"""Read-only A_RG2b research; retained evidence only, no numerical refresh."""
from pathlib import Path
import json,lzma
from .basin import _bound_file
from .spark_arg2b_sc3_metadata import HISTORICAL_HELPER,reviewed_source_bytes
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_arg2b_metadata import checked_epoch,need

BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/'
REPORT=BASE+'ARG2bResearchProgress.json'
REPORT_DIGEST='c4ecc07cb695391f6589d11e1d8508ddef3056d9fbce857e043eed5a40ed1a60'
FAMILIES=['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC','C_RG2b']


def spark_arg2b_research_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound A_RG2b report')
    need(r['family']=='A_RG2b' and r['status']=='demonstrated_bounded_pending_review' and
        not r['accepted_authority'] and not r['native_completion'] and not r['G4_accepted'], 'A_RG2b scope')
    need(r['full_state']==['C','W_A'] and r['full_dimension']==30 and r['resource_dimension']==14 and
        r['conductance_dimension']==16 and r['ordinary_duration']=='16', 'full physical dimensions/duration')
    need(r['entry']==300 and r['completion']==r['last_executed_step']==302 and r['retained_states']==604 and
        r['supporting_trajectory_steps_after_completion']==0 and not r['future_trajectory_required'], 'direct prefix scope')
    need(r['accepted_scientific_families']==FAMILIES and r['next_family_after_review'] is None and
        r['debt']['status']=='open_pending_scientific_adjudication', 'research promoted or accepted baseline changed')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate research source')
    for ref in r['sources']:
        if ref['path']==HISTORICAL_HELPER:reviewed_source_bytes(root,ref['path'],ref['sha256'])
        else:_bound_file(root,ref['path'],ref['sha256'])
    baseline=load_json_object(root/r['accepted_baseline']['path'])
    need(baseline['record_digest']==record_digest(baseline,'record_digest')==r['accepted_baseline']['record_digest'] and
        baseline['scope']['scientific_families']==FAMILIES,'accepted baseline scope')
    path=BASE+'ARG2bDirectCertificate.json.xz'
    cert=json.loads(lzma.decompress((root/path).read_bytes()))
    need(cert['record_digest']==record_digest(cert,'record_digest')==r['certificate_digest'],'direct certificate identity')
    proof=cert['checks'];need(proof==r['proof'] and cert['common_domain_for_both_roles'],'direct proof projection')
    need(proof['relative_dimension']==30 and proof['full_physical_state']==['C','W_A'] and
        proof['physical']['full_writer_included'] and proof['physical']['both_H_consumers'] and
        proof['physical']['all_independent_coordinates'] and not proof['section_C1_claimed'] and
        proof['trajectory_inputs_to_domain_checker']==0 and not proof['future_trajectory_required'], 'direct C/W proof scope')
    for role in ('current','reset'):
        need(r['decisions'][role]['local_gain']==int(role=='current') and
            not r['decisions'][role]['accepted_authority'] and not r['decisions'][role]['native_completion'], 'live gain/authority scope')
    need(r['verification']['complete_fresh_trajectory_replays']==2,'fresh replay evidence absent')
    value=dict(schema='grc9v4_spark_arg2b_research_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_arg2b_research_source(root,side,path):
    value=spark_arg2b_research_status(root,side)
    ref=next((r for r in value['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed A_RG2b source')
    return reviewed_source_bytes(Path(root),path,ref['sha256']),ref
