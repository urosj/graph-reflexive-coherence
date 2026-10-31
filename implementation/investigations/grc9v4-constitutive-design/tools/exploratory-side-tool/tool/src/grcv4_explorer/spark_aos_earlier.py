"""Read-only earlier A_OS certificate; no authority overlay or numerical refresh."""
from pathlib import Path
import json,lzma
from .basin import _bound_file
from .canonical import digest,load_json_object,record_digest,file_sha256
from .spark_aos_earlier_metadata import checked_epoch,need
from .spark_aci_metadata import reviewed_source_bytes
BASE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/earlier-closure/'
REPORT=BASE+'AOSEarlierResearch.json'
REPORT_DIGEST='dec3d7189532bd937d7d3cf65084bb01f78107ea0e18dd325c2a713649e0f5a3'
CHECKS=BASE+'AOSEarlierChecks.json.xz'


def spark_aos_earlier_status(root,side):
    root=Path(root);checked_epoch(root);r=load_json_object(root/REPORT)
    need(r.get('record_digest')==record_digest(r,'record_digest')==REPORT_DIGEST,'unbound earlier A_OS report')
    need(r['family']=='A_OS' and r['status']=='demonstrated_bounded_pending_review' and
         not r['accepted_authority'] and not r['native_completion'] and not r['G4_accepted'] and
         r['relative_dimension']==30 and r['conductance_dimension']==16 and
         r['additional_event_gain']==0 and r['trajectory_reruns']==0,'earlier A_OS scope')
    need(len({x['path'] for x in r['sources']})==len(r['sources']),'duplicate earlier source')
    for ref in r['sources']:reviewed_source_bytes(root,ref['path'],ref['sha256'])
    c=json.loads(lzma.decompress((root/CHECKS).read_bytes()))
    need(c['record_digest']==record_digest(c,'record_digest')==r['checks_record_digest'],'earlier check identity')
    for role,summary in r['decisions'].items():
        need(summary=={k:v for k,v in c['runs'][role].items() if k not in ('interval_checks','checkpoints')},'earlier entry/accounting projection')
    need(r['anisotropic']==c['anisotropic'] and r['enlarged_ball']==c['enlarged_ball'],'earlier proof projection')
    value=dict(schema='grc9v4_spark_aos_earlier_surface_v1',report_record_digest=REPORT_DIGEST,report=r,
        check_mode='retained_source_integrity_no_numerical_rerun',
        source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*r['sources']])
    value['projection_digest']=digest(value);return value


def spark_aos_earlier_source(root,side,path):
    value=spark_aos_earlier_status(root,side)
    ref=next((r for r in value['source_refs'] if r['path']==path),None)
    if ref is None:raise KeyError('not an indexed earlier A_OS source')
    return reviewed_source_bytes(Path(root),path,ref['sha256']),ref
