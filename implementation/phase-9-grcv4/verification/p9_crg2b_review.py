"""Read-only scoped research view; numerical certification is an explicit command."""
import hashlib
import json
import lzma
from pathlib import Path

import p9_crg2b_completion as c
import p9_crg2b_section as s

AUTHORITY=c.BASE+'tranche-8/P9-CRG2b-Authority.json'
IDENTITIES=c.BASE+'tranche-8/P9-CRG2b-ResearchBindings.json'
SELF=c.BASE+'verification/p9_crg2b_review.py'


def checked(root=c.ROOT):
    root=Path(root).resolve()
    identities=json.loads((root/IDENTITIES).read_bytes())
    c.require(identities==c.seal(identities),'research identities digest drift')
    c.require(set(identities['artifacts'])=={c.RESULT,s.RESULT,AUTHORITY},'research identity roster drift')
    for name,expected in identities['artifacts'].items():
        c.require(hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,'research artifact drift: '+name)
    completion=c.check(json.loads((root/c.RESULT).read_bytes()))
    with lzma.open(root/s.RESULT,'rt',encoding='utf-8') as stream:sections=s.check(json.load(stream))
    authority=json.loads((root/AUTHORITY).read_bytes())
    c.require(len(authority['contracts'])==8 and list(authority['debts'])==['GTRS-RG-DEBT-C1-SECTION-REGULARITY'],
              'authority/debt roster drift')
    names={c.RESULT,s.RESULT,AUTHORITY,IDENTITIES,SELF,
           *(r['path'] for v in (completion,sections) for r in v['source_bindings'])}
    for trace in (*authority['contracts'].values(),*authority['debts'].values()):
        names|={row['source_ref']['path'] for row in trace['rows']}
    for row in identities['authority_sources']:
        c.require(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],'authority source drift')
    c.require({r['path'] for r in identities['authority_sources']}=={
        row['source_ref']['path'] for t in (*authority['contracts'].values(),*authority['debts'].values()) for row in t['rows']},
        'authority source roster drift')
    import p9_crg2b_native_review as native
    execution=native.checked(root)
    names|={native.PATH,native.SELF}
    names|={r['path'] for r in execution['source_bindings']}
    release=c.BASE+'tranche-8/P9-CRG2b-ConnectedCompletionRelease.json'
    adopted=json.loads((root/release).read_bytes())
    c.require(adopted==c.seal(adopted),'connected release binding')
    for row in adopted['source_bindings']:
        c.require(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],'connected release source drift')
        names.add(row['path'])
    names.add(release)
    return dict(schema='phase9_crg2b_work_v2',family='C_RG2b',realization_number=9,
        branch='work/p9-acipc-tranches-8-9',stage=execution['stage'],
        graph_certificates=len(completion['graphs']),completion_passed=completion['completion_theorem_passes'],
        prepared_sections=[dict(graph=r['graph'],role=r['role'],
            section_passed=r['certificate']['section_tolerance_passes'],
            section_error_upper=float(s.Q(r['certificate']['section_error_upper'])),
            exact_real_first_step_positive=r['certificate']['exact_real_first_step_positive'],
            exact_real_resource_lower=float(s.Q(r['certificate']['exact_real_next_resource_lower']))) for r in sections['cases']],
        native_execution=execution['checkpoints'],native_review_digest=execution['record_digest'],
        large_covariance_selected=execution['large_covariance_selected'],
        large_covariance_deferred=execution['large_covariance_deferred'],
        remaining_family='A_RG2b',tranche10='deferred',uniform_trajectory_enclosure=False,
        research_native_steps=0,research_native_events=0,user_accepted=False,aggregate_closed=False,G3_support_added=[],
        debt_status='C1 regularity remains narrowed and unresolved',
        check_level='retained_integrity_only_no_numerical_rerun',
        next_work=execution['next_work'],
        source_refs=[dict(path=p,sha256=hashlib.sha256((root/p).read_bytes()).hexdigest()) for p in sorted(names)])
