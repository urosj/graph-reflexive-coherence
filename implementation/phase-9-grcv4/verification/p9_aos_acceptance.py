"""Explicit bounded A_OS acceptance, separate from original execution records."""
from pathlib import Path
import json
import subprocess

import p9_aos_review as review
from p9_cpc_historical import project_sha

BASE = 'b4339d8f'
PREFIX = 'implementation/phase-9-grcv4/'
PATH = PREFIX + 'tranche-9/P9-AOS-Acceptance.json'
EPOCHS = PREFIX + 'tranche-9/P9-AOS-AcceptanceSources.json'
SELF = PREFIX + 'verification/p9_aos_acceptance.py'
TEST = PREFIX + 'verification/test_p9_aos_acceptance.py'
VALIDATION = PREFIX + 'tranche-9/P9-AOS-AcceptanceValidation.json'
SIDE = 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/'
CHANGED = {SIDE+'src/grcv4_explorer/aos.py', SIDE+'phase9-web/aos.js',
           PREFIX+'verification/p9_aos_g2_sources.py',
           PREFIX+'verification/phase9_implementation_policy.py'}
DIGEST = 'df3860ed9c90095da5cb03c988a7a65db7efdfdfc442b195ba069d79efb9e5cf'


def original(root, name):
    return subprocess.check_output(['git', 'show', BASE+':'+name], cwd=root)


def record(root):
    value=json.loads((Path(root)/PATH).read_bytes())
    review.b.check_digest(value)
    review.b.require(value['record_digest']==DIGEST
        and value['schema']=='p9-aos-acceptance-v1'
        and value['reviewed_commit']==BASE and value['family']=='A_OS'
        and value['checkpoints']==list(review.STEPS) and value['user_accepted'] is True
        and value['bounded_scope_closed'] is True
        and value['aggregate_closed'] is False and value['full_GRC9V4_conformance'] is False
        and value['original_large_reset_excluded'] is True
        and value['optional_completion']=='unselected' and value['tranche10']=='deferred',
        'A_OS acceptance identity or scope drift')
    return value


def epochs(root):
    root=Path(root).resolve(); accepted=record(root)
    raw=(root/EPOCHS).read_bytes()
    review.b.require(accepted['source_epochs']==dict(path=EPOCHS,sha256=review.b.sha(raw)),
                     'A_OS acceptance source epochs drift')
    value=json.loads(raw);review.b.check_digest(value)
    review.b.require(value['base_commit']==BASE and set(value['sources'])==CHANGED,
                     'A_OS acceptance source roster drift')
    for name,row in value['sources'].items():
        review.b.require(project_sha(root,name,review.b.sha((root/name).read_bytes()))==row['after_sha256']
            and review.b.sha(original(root,name))==row['before_sha256'],
            'A_OS acceptance source drift: '+name)
    return value['sources']


def previous_sha(root, name, present):
    if name not in CHANGED:return None
    row=epochs(root)[name]
    present=project_sha(root,name,present)
    return row['before_sha256'] if present==row['after_sha256'] else None


def decision(root):
    root=Path(root).resolve()
    if not (root/PATH).exists():return None
    value=record(root);changes=epochs(root)
    evidence=review.checked(root)
    review.b.require(evidence['record_digest']==value['evidence']['record_digest'],
                     'A_OS acceptance review mismatch')
    for ref in [value['evidence'], *value['validation']]:
        raw=(root/ref['path']).read_bytes()
        review.b.require(review.b.sha(raw)==ref['sha256'],'accepted A_OS subject drift')
        retained=json.loads(raw);review.b.check_digest(retained)
        review.b.require(retained['record_digest']==ref['record_digest'],'accepted A_OS digest drift')
        for source in retained['source_bindings']:
            name=source['path'];present=project_sha(root,name,review.b.sha((root/name).read_bytes()))
            if present==source['sha256']:continue
            row=changes.get(name)
            review.b.require(row is not None and row['before_sha256']==source['sha256']
                and row['after_sha256']==present,'accepted A_OS validation source drift: '+name)
    return value


if __name__=='__main__':
    value=decision(review.b.ROOT)
    review.b.require(value is not None,'A_OS acceptance absent')
    print('A_OS bounded Tranches 8–9 accepted; twenty compatibility cells accepted; full conformance held.')
