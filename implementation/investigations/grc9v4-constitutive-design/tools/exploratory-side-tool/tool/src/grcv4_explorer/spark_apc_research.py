"""Read-only A_PC research, without authority overlay or numerical refresh."""
from pathlib import Path
import json,lzma
from .basin import _bound_file
from .spark_apc_sc3_metadata import HISTORICAL_HELPER,reviewed_source_bytes
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_apc_metadata import checked_epoch,need
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/'
REPORT=BASE+'APCResearchProgress.json'
REPORT_DIGEST='a8a819ea8757720323a22eb46c553051024517b4913e5417ac87aa5352f7e68a'


def spark_apc_research_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound A_PC report')
    need(r['family']=='A_PC' and r['status']=='demonstrated_bounded_pending_review' and
         not r['accepted_authority'] and not r['native_completion'] and not r['G4_accepted'] and
         r['full_state']==['C','W_A','Z_4'] and r['full_dimension']==76 and r['conductance_dimension']==16 and
         r['carrier_dimension']==46 and r['proof']['incoming_carrier_geometry'] and r['proof']['both_independent_writers'] and
         r['proof']['all_carrier_directions_included'] and r['proof']['stationary_writer_self_consistent'] and
         not r['proof']['OS_derivative_reused'] and not r['proof']['earlier_family_trajectory_reused'],'A_PC research scope')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate A_PC source')
    for ref in r['sources']:
        if ref['path']==HISTORICAL_HELPER:reviewed_source_bytes(root,ref['path'],ref['sha256'])
        else:_bound_file(root,ref['path'],ref['sha256'])
    baseline=load_json_object(root/r['accepted_baseline']['path'])
    need(baseline['record_digest']==record_digest(baseline,'record_digest')==r['accepted_baseline']['record_digest'] and
         baseline['scope']['scientific_families']==r['accepted_scientific_families']==['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI'],
         'accepted baseline changed or research promoted')
    for role in ('current','reset'):
        execution=json.loads(lzma.decompress((root/(BASE+'APC-'+role+'.json.xz')).read_bytes()))
        need(execution['record_digest']==record_digest(execution,'record_digest')==r['execution_digests'][role],'A_PC execution identity')
        need(execution['checks']['proof']==r['proof'] and execution['checks']['decision']==r['decisions'][role],'A_PC proof/decision projection')
    need(r['decisions']['current']['local_gain']==1 and r['decisions']['reset']['local_gain']==0 and
         r['debt']['status']=='open_pending_scientific_adjudication','A_PC accounting/debt')
    value=dict(schema='grc9v4_spark_apc_research_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_apc_research_source(root,side,path):
    value=spark_apc_research_status(root,side);ref=next((r for r in value['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed A_PC source')
    return reviewed_source_bytes(Path(root),path,ref['sha256']),ref
