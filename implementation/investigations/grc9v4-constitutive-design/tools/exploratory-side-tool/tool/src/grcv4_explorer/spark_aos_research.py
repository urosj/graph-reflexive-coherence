"""Read-only A_OS research; no authority overlay and no numerical refresh."""
from pathlib import Path
from .spark_cipc import spark_cipc_authority
from .basin import _bound_file
from .spark_aos_sc3_metadata import HISTORICAL_HELPER,reviewed_source_bytes
from .canonical import digest,load_json_object,record_digest,file_sha256
from .errors import SourceAdmissionError
REPORT='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/AOSResearchProgress.json'
REPORT_DIGEST='6d8fdba74099052d7cedb3b102e3bb031b46f28f2754da8de54bb97430cfed62'

def need(ok,message):
    if not ok:raise SourceAdmissionError(message)

def spark_aos_research_status(root,side):
    root=Path(root);prior=spark_cipc_authority(root,side);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound A_OS report')
    need(r['family']=='A_OS' and r['status']=='demonstrated_bounded_pending_review' and not r['accepted_authority'] and
         r['native_support_added']==[] and not r['G4_accepted'],'A_OS research scope')
    need(r['predecessor_projection_digest']==prior['projection_digest'],'accepted predecessor changed')
    need(r['full_physical_state']==['C','W_A'] and r['full_dimension']==30 and r['conductance_dimension']==16 and
         r['proof']['all_conductance_directions_included'] and r['proof']['stationary_writer_self_consistent'],'A_OS full writer obligation')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate A_OS source')
    for ref in r['sources']:
        if ref['path']==HISTORICAL_HELPER:reviewed_source_bytes(root,ref['path'],ref['sha256'])
        else:_bound_file(root,ref['path'],ref['sha256'])
    v=dict(schema='grc9v4_spark_aos_research_surface_v1',report_record_digest=REPORT_DIGEST,
        accepted_scientific_families=prior['scope']['scientific_families'],report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    v['projection_digest']=digest(v);return v

def spark_aos_research_source(root,side,path):
    v=spark_aos_research_status(root,side);ref=next((r for r in v['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed A_OS source')
    return reviewed_source_bytes(Path(root),path,ref['sha256']),ref
