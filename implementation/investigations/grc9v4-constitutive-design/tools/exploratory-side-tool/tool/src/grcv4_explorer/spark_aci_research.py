"""Read-only A_CI research, without authority overlay or numerical refresh."""
from pathlib import Path
import json,lzma
from .basin import _bound_file
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_aci_metadata import checked_epoch,need
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/'
REPORT=BASE+'ACIResearchProgress.json'
REPORT_DIGEST='706f60b3852e0913694724ccc08acb4c5e5d63cc5805d9482f530f337792fbd5'


def spark_aci_research_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound A_CI report')
    need(r['family']=='A_CI' and r['status']=='demonstrated_bounded_pending_review' and
         not r['accepted_authority'] and not r['native_completion'] and not r['G4_accepted'] and
         r['full_state']==['C','W_A'] and r['full_dimension']==30 and r['conductance_dimension']==16 and
         r['proof']['implicit_geometry_derivative'] and r['proof']['stationary_writer_self_consistent'] and
         not r['proof']['OS_derivative_reused'] and not r['proof']['OS_trajectory_reused'],'A_CI research scope')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate A_CI source')
    for ref in r['sources']:_bound_file(root,ref['path'],ref['sha256'])
    baseline=load_json_object(root/r['accepted_baseline']['path'])
    need(baseline['record_digest']==record_digest(baseline,'record_digest')==r['accepted_baseline']['record_digest'] and
         baseline['scope']['scientific_families']==r['accepted_scientific_families']==['C_OS','C_CI','C_PC','C_CI_PC','A_OS'],
         'accepted baseline changed or research promoted')
    for role in ('current','reset'):
        execution=json.loads(lzma.decompress((root/(BASE+'ACI-'+role+'.json.xz')).read_bytes()))
        need(execution['record_digest']==record_digest(execution,'record_digest')==r['execution_digests'][role],'A_CI execution identity')
        need(execution['checks']['proof']==r['proof'] and execution['checks']['decision']==r['decisions'][role],'A_CI proof/decision projection')
    need(r['decisions']['current']['local_gain']==1 and r['decisions']['reset']['local_gain']==0 and
         r['debt']['status']=='open_pending_scientific_adjudication','A_CI accounting/debt')
    value=dict(schema='grc9v4_spark_aci_research_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_aci_research_source(root,side,path):
    value=spark_aci_research_status(root,side);ref=next((r for r in value['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed A_CI source')
    return _bound_file(Path(root),path,ref['sha256']).read_bytes(),ref
