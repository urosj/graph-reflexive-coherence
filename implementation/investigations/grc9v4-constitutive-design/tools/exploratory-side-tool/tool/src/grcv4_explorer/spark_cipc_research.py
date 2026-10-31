"""Read-only, bounded research progress alongside the accepted applicability graph.

This surface adds no claim authority. It verifies retained source bindings and
never imports numerical campaign code or reruns a trajectory on refresh.
"""
from pathlib import Path
from .spark_pc import spark_pc_authority
from .basin import _bound_file
from .canonical import digest, load_json_object, record_digest, file_sha256
from .errors import SourceAdmissionError

INV = 'implementation/investigations/grc9v4-constitutive-design/'
REPORT = INV+'evidence/spark-completion/applicability/CCIPCResearchProgress.json'
REPORT_DIGEST = 'e6703c2c9dcbc1e25d611a0bdcef4c7646e3855f5c2015bdea81b50ac59f5c2d'


def need(condition, message):
    if not condition: raise SourceAdmissionError(message)


def spark_cipc_research_status(root, side):
    root = Path(root)
    prior = spark_pc_authority(root, side)
    report = load_json_object(root/REPORT)
    need(report.get('record_digest')==record_digest(report,'record_digest')==REPORT_DIGEST,
         'unbound spark-completion research report')
    need(report['schema']=='spark-completion-ccipc-research-progress-v1' and
         report['family']=='C_CI_PC' and report['status']=='demonstrated_bounded_pending_review' and
         report['accepted_authority'] is False and report['native_support_added']==[] and
         report['G4_accepted'] is False, 'research scope widened')
    need(report['predecessor_projection_digest']==prior['projection_digest'], 'accepted predecessor changed')
    need(report['full_physical_state']==['C','Z_4'] and report['full_dimension']==60 and
         report['carrier_dimension']==46 and report['nonzero_carrier_directions_included'] is True,
         'carrier obligation omitted')
    need(report['proof']['stationary_composite_gain']==2 and
         report['proof']['same_selected_source_for_geometry_and_writer'] is True,
         'composite same-source obligation omitted')
    refs = report['sources']
    need(len({r['path'] for r in refs})==len(refs), 'duplicate research source')
    for ref in refs: _bound_file(root,ref['path'],ref['sha256'])
    view = dict(schema='grc9v4_spark_cipc_research_surface_v1',report_record_digest=REPORT_DIGEST,
                accepted_scientific_families=prior['scope']['scientific_families'],
                report=report,check_mode='retained_source_integrity_no_numerical_rerun',
                source_refs=[dict(path=REPORT,sha256=file_sha256(root/REPORT)),*refs])
    view['projection_digest']=digest(view)
    return view


def spark_cipc_research_source(root, side, path):
    view=spark_cipc_research_status(root,side)
    ref=next((r for r in view['source_refs'] if r['path']==path),None)
    if ref is None: raise KeyError('not an indexed spark-completion research source')
    return _bound_file(Path(root),path,ref['sha256']).read_bytes(),ref
