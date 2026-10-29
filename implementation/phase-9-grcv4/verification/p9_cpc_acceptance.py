"""Explicit C_PC acceptance, preserving the reviewed implementation and runs."""
import json
from functools import lru_cache
from pathlib import Path
import subprocess

import p9_cpc_review as review

BASE = '1e720983'
PREFIX = 'implementation/phase-9-grcv4/'
PATH = PREFIX + 'tranche-9/P9-CPC-Acceptance.json'
EPOCHS = PREFIX + 'tranche-9/P9-CPC-AcceptanceSources.json'
SELF = PREFIX + 'verification/p9_cpc_acceptance.py'
TEST = PREFIX + 'verification/test_p9_cpc_acceptance.py'
VALIDATION = PREFIX + 'tranche-9/P9-CPC-AcceptanceValidation.json'
SIDE = review.historical.SIDE
CHANGED = {SIDE+'src/grcv4_explorer/cpc.py', SIDE+'phase9-web/cpc.js',
           review.SELF, review.TEST, review.GUIDE, review.historical.SELF,
           PREFIX+'verification/phase9_implementation_policy.py'}
DIGEST = 'd12f3587c98c3692dcbde8b71643d07bb377f8bfbf132258f2922665f7a855d5'


@lru_cache(maxsize=256)
def original(root, name):
    return subprocess.check_output(['git', 'show', BASE+':'+name], cwd=root)


def present_sha(root,name,present):
    from p9_ccipc_historical import project_sha
    return project_sha(root,name,present)


def record(root):
    value=json.loads((Path(root)/PATH).read_bytes())
    review.b.check_digest(value)
    review.b.require(value['record_digest']==DIGEST
        and value['schema']=='p9-cpc-acceptance-v1'
        and value['reviewed_commit']==BASE and value['family']=='C_PC'
        and value['realization_number']==6 and value['accepted_date']=='2026-10-29'
        and value['checkpoints']==list(review.STEPS) and value['user_accepted'] is True
        and value['bounded_scope_closed'] is True
        and value['aggregate_closed'] is False and value['full_GRC9V4_conformance'] is False
        and value['original_large_target_roles_excluded']==['current','reset']
        and value['successful_companion_accepted'] is True
        and value['compatibility_counts']==dict(bounded_accepted=24,
            passed_pending_acceptance=0,unselected_not_executed=16)
        and value['optional_completion']=='unselected' and value['tranche10']=='deferred',
        'C_PC acceptance identity or scope drift')
    return value


def epochs(root):
    root=Path(root).resolve();accepted=record(root)
    raw=(root/EPOCHS).read_bytes()
    review.b.require(accepted['source_epochs']==dict(path=EPOCHS,sha256=review.b.sha(raw)),
                     'C_PC acceptance source epochs drift')
    value=json.loads(raw);review.b.check_digest(value)
    review.b.require(value['schema']=='p9-cpc-acceptance-sources-v1'
        and value['base_commit']==BASE and set(value['sources'])==CHANGED
        and value['native_runtime_changed'] is False
        and value['original_execution_relabelled'] is False,'C_PC acceptance source roster drift')
    for name,row in value['sources'].items():
        review.b.require(present_sha(root,name,review.b.sha((root/name).read_bytes()))==row['after_sha256']
            and review.b.sha(original(root,name))==row['before_sha256'],
            'C_PC acceptance source drift: '+name)
    return value['sources']


def previous_sha(root,name,present):
    if name not in CHANGED or not (Path(root)/PATH).exists():return None
    present=present_sha(root,name,present)
    row=epochs(root)[name]
    return row['before_sha256'] if present==row['after_sha256'] else None


def matches(root,name,expected):
    present=review.b.sha((Path(root)/name).read_bytes())
    return present==expected or present_sha(root,name,present)==expected or previous_sha(root,name,present)==expected


def decision(root):
    root=Path(root).resolve()
    if not (root/PATH).exists():return None
    value=record(root);epochs(root)
    evidence=review.checked(root)
    review.b.require(evidence['record_digest']==value['evidence']['record_digest'],
                     'C_PC acceptance review mismatch')
    for ref in [value['evidence'],*value['validation']]:
        raw=(root/ref['path']).read_bytes()
        review.b.require(review.b.sha(raw)==ref['sha256'] and raw==original(root,ref['path']),
                         'accepted C_PC subject drift')
        retained=json.loads(raw);review.b.check_digest(retained)
        review.b.require(retained['record_digest']==ref['record_digest'],'accepted C_PC digest drift')
        for source in retained['source_bindings']:
            review.b.require(matches(root,source['path'],source['sha256']),
                             'accepted C_PC validation source drift: '+source['path'])
    return value


if __name__=='__main__':
    review.b.require(decision(review.b.ROOT) is not None,'C_PC acceptance absent')
    print('C_PC bounded Tranches 8–9 accepted; twenty-four compatibility cells accepted; full conformance held.')
