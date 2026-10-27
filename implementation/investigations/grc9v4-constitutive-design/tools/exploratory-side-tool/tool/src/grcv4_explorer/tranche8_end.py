"""Read-only final-review evidence; no new runtime admission gate."""
from pathlib import Path
import sys

PINS = {'mechanisms': ('implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupMechanisms.json', '1760ea5359c49cc577d5240fb4c0d4d8fafb283a55b3a12d63a62078b779f694'), 'performance': ('implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupPerformance.json', '2fa86400134184bf4677d2666dcdb59364347b6d6eb36ead04f58361cab4a1f9')}
BASE = 'implementation/phase-9-grcv4/tranche-8/'
REPORT = BASE + 'P9-Tranche8-FirstGroupEndResults.md'
ACCEPTANCE = BASE + 'P9-Tranche8-FirstGroupAcceptance.json'
ACCEPTANCE_DIGEST = '9b177f90bc5c38deea9769aca98fc16d9f6c0c10dc6ccc3b92583a3faa8f697c'


def tranche8_end_reviews(repo_root):
    root=Path(repo_root).resolve()
    sys.path.insert(0,str(root/'implementation/phase-9-grcv4/verification'))
    import p986_first_group as h
    import p986_acceptance as acceptance
    records={};refs=[]
    for key,(path,pin) in PINS.items():
        value=h.load(root,path)
        h.require(value['record_digest']==pin,'changed final review: '+key)
        for ref in value['source_refs']:h.handoff.authenticate(root,ref)
        records[key]=value
        refs.extend(value['source_refs']);refs.append(h.handoff.reference(root,path))
    h.require(set(records)=={'mechanisms','performance'},'incomplete final review')
    a=h.load(root,acceptance.ACCEPTANCE)
    h.require(a['record_digest']==acceptance.ACCEPTANCE_DIGEST
        ==records['mechanisms']['acceptance_digest'],'unbound predecessor acceptance')
    h.require(h.sha((root/REPORT).read_bytes()) == '9a25215d4fe075983d3a31ccab904cdc65e0e70cfbdccd9668b1034ec5e754a0', 'changed final review narrative')
    closing=h.load(root,ACCEPTANCE)
    h.require(closing['record_digest']==ACCEPTANCE_DIGEST
        and closing['review_digests']=={k:v['record_digest'] for k,v in records.items()}
        and closing['conformance_acceptance_digest']==a['record_digest']
        and closing['families']==list(h.FAMILIES) and closing['limits']==h.LIMITS
        and closing['user_accepted'] and closing['first_group_closed']
        and not closing['aggregate_closed'],'unbound first-group closeout acceptance')
    refs.append(h.handoff.reference(root,ACCEPTANCE))
    return dict(schema='phase9_tranche8_end_reviews_v1',families=list(h.FAMILIES),
        records=records,scope='bounded first group; no numerical rerun or support extension',
        final_review_user_accepted=True,first_group_closed=True,aggregate_closed=False,acceptance=closing,
        source_refs=h.handoff.unique_refs(refs+[h.handoff.reference(root,REPORT)]))


def tranche8_end_source(repo_root,path):
    value=tranche8_end_reviews(repo_root)
    import p986_first_group as h
    refs={r['path']:r for r in value['source_refs']}
    if path not in refs:raise KeyError('source is not in the final review')
    ref=refs[path]
    return h.handoff.authenticate(Path(repo_root),ref),ref
