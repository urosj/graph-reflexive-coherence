"""Explicit bounded C_RG2b acceptance without relabelling execution evidence."""
import hashlib
import json
from pathlib import Path

import p9_crg2b_native_review as native

PATH = 'implementation/phase-9-grcv4/tranche-9/P9-CRG2b-Acceptance.json'
SELF = 'implementation/phase-9-grcv4/verification/p9_crg2b_acceptance.py'
DIGEST = 'b4c76c8c0cfd206e1951c833276df50aaae93dfb639772d86697079ff4a81a98'


def decision(root):
    root = Path(root).resolve()
    if not (root / PATH).exists():
        return None
    value = json.loads((root / PATH).read_bytes())
    native.b.check_digest(value)
    native.b.require(value['record_digest'] == DIGEST,
                     'C_RG2b acceptance identity or scope drift')
    execution = native.checked(root)
    native.b.require(execution['record_digest'] == value['evidence']['record_digest']
                     and set(execution['checkpoints']) == set(value['checkpoints'])
                     and execution['user_accepted'] is False,
                     'C_RG2b accepted execution mismatch')
    for key in ('evidence', 'support', 'matrix', 'completion_release', 'storage'):
        ref = value[key]
        raw = (root / ref['path']).read_bytes()
        native.b.require(hashlib.sha256(raw).hexdigest() == ref['sha256'],
                         'C_RG2b accepted subject drift: ' + ref['path'])
        if 'record_digest' in ref:
            record = json.loads(raw)
            native.b.check_digest(record)
            native.b.require(record['record_digest'] == ref['record_digest'],
                             'C_RG2b accepted record digest drift')
    return value
