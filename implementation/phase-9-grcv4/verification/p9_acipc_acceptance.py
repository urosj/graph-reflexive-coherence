"""Explicit A_CI_PC acceptance, preserving the reviewed implementation and runs."""
import json
from functools import lru_cache
from pathlib import Path
import subprocess

import p9_acipc_review as review

BASE = 'e3e7f91a'
PREFIX = 'implementation/phase-9-grcv4/'
PATH = PREFIX + 'tranche-9/P9-ACIPC-Acceptance.json'
EPOCHS = PREFIX + 'tranche-9/P9-ACIPC-AcceptanceSources.json'
SELF = PREFIX + 'verification/p9_acipc_acceptance.py'
TEST = PREFIX + 'verification/test_p9_acipc_acceptance.py'
VALIDATION = PREFIX + 'tranche-9/P9-ACIPC-AcceptanceValidation.json'
SIDE = review.historical.SIDE
CHANGED = {SIDE+'src/grcv4_explorer/acipc.py', review.SELF,
           PREFIX+'verification/test_p9_acipc_review.py', review.GUIDE, review.historical.SELF,
           PREFIX+'verification/phase9_implementation_policy.py',
           *(PREFIX+'tranche-8/P9-ACIPC-'+name+'.md' for name in ('Tranches8-9-Plan','ScientificReview')),
           *(SIDE.removesuffix('tool/')+'GRCV4ExploratorySideToolImplementation'+name+'.md' for name in ('Plan','Checklist')),
           *('implementation/Phase-9-GRCV4-'+name+'.md' for name in ('Handoff','ImplementationPlan','ImplementationChecklist'))}
DIGEST = '6d793202d07e1057cbc43297a9ae539e5475898fe6b5b060dae50c7770022c6f'


@lru_cache(maxsize=256)
def original(root, name):
    return subprocess.check_output(['git', 'show', BASE+':'+name], cwd=root)


def present_sha(root,name,present):
    from p9_crg2b_historical import peel_sha
    return peel_sha(root,name,present)


def record(root):
    value=json.loads((Path(root)/PATH).read_bytes())
    review.b.check_digest(value)
    review.b.require(value['record_digest']==DIGEST
        and value['schema']=='p9-acipc-acceptance-v1'
        and value['reviewed_commit']==BASE and value['family']=='A_CI_PC'
        and value['realization_number']==8 and value['accepted_date']=='2026-10-30'
        and value['checkpoints']==list(review.STEPS) and value['user_accepted'] is True
        and value['bounded_scope_closed'] is True
        and value['aggregate_closed'] is False and value['full_GRC9V4_conformance'] is False
        and value['original_large_target_roles_excluded']==['reset']
        and value['successful_companion_accepted'] is True
        and value['first_companion_event_credit'] is False
        and value['large_covariance_selected']==['combined','reflect','rotate']
        and value['large_covariance_deferred_unexecuted']==['edge_order','node_order','relabel','signed','rotate_twice']
        and value['compatibility_counts']==dict(bounded_accepted=32,
            passed_pending_acceptance=0,unselected_not_executed=8)
        and value['optional_completion']=='unselected' and value['tranche10']=='deferred',
        'A_CI_PC acceptance identity or scope drift')
    return value


def epochs(root):
    root=Path(root).resolve();accepted=record(root)
    raw=(root/EPOCHS).read_bytes()
    review.b.require(accepted['source_epochs']==dict(path=EPOCHS,sha256=review.b.sha(raw)),
                     'A_CI_PC acceptance source epochs drift')
    value=json.loads(raw);review.b.check_digest(value)
    review.b.require(value['schema']=='p9-acipc-acceptance-sources-v1'
        and value['base_commit']==BASE and set(value['sources'])==CHANGED
        and value['native_runtime_changed'] is False
        and value['original_execution_relabelled'] is False,'A_CI_PC acceptance source roster drift')
    for name,row in value['sources'].items():
        review.b.require(present_sha(root,name,review.b.sha((root/name).read_bytes()))==row['after_sha256']
            and review.b.sha(original(root,name))==row['before_sha256'],
            'A_CI_PC acceptance source drift: '+name)
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
                     'A_CI_PC acceptance review mismatch')
    for ref in [value['evidence'],*value['validation']]:
        raw=(root/ref['path']).read_bytes()
        review.b.require(review.b.sha(raw)==ref['sha256'] and raw==original(root,ref['path']),
                         'accepted A_CI_PC subject drift')
        retained=json.loads(raw);review.b.check_digest(retained)
        review.b.require(retained['record_digest']==ref['record_digest'],'accepted A_CI_PC digest drift')
        for source in retained['source_bindings']:
            review.b.require(matches(root,source['path'],source['sha256']),
                             'accepted A_CI_PC validation source drift: '+source['path'])
    return value


if __name__=='__main__':
    review.b.require(decision(review.b.ROOT) is not None,'A_CI_PC acceptance absent')
    print('A_CI_PC bounded Tranches 8–9 accepted; thirty-two compatibility cells accepted; full conformance held.')
