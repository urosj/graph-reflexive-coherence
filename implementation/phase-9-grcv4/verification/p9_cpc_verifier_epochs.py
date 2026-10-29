"""Exact, finite verification-only repairs during the unaccepted C_PC campaign.

Original executions and their digests remain immutable. This bridge permits only
the three named verifier successors, with original source bytes retained. It
never projects a runtime producer or confers new execution/acceptance credit.
"""
import hashlib
import json
from pathlib import Path
import p984b_runtime as b

SELF=b.HERE+'p9_cpc_verifier_epochs.py'
PATH=b.BASE+'P9-CPC-VerifierSourceEpochs.json'
NAMES={b.HERE+x+'.py' for x in ('p9_cpc_targets','p984h_cpc','p99_cpc')}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def check_bindings(refs):
    value=json.loads((b.ROOT/PATH).read_bytes());b.check_digest(value)
    b.require(value['schema']=='p9-cpc-verifier-epochs-v1' and set(value['sources'])==NAMES
        and value['checker_sha256']==sha((b.ROOT/SELF).read_bytes())
        and value['runtime_producer_changed'] is False and value['execution_relabelled'] is False,
        'verifier epoch scope drift')
    for name,row in value['sources'].items():
        b.require(sha(row['original_source'].encode())==row['before_sha256']
            and sha((b.ROOT/name).read_bytes())==row['after_sha256'], 'verifier successor drift: '+name)
    b.require(len({x['path'] for x in refs})==len(refs),'duplicate source binding')
    for ref in refs:
        name=Path(ref['path']).as_posix();present=sha((b.ROOT/name).read_bytes())
        b.require(ref['sha256']==present or (name in NAMES
            and ref['sha256']==value['sources'][name]['before_sha256']), 'source binding drift: '+name)
