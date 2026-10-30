"""Bounded A_RG2b user decision over unchanged implementation evidence."""
from functools import lru_cache
import json
from pathlib import Path
import subprocess

import p9_arg2b_native_review as native

b = native.b
BASE = 'fd23970b'
PREFIX = 'implementation/phase-9-grcv4/'
SIDE = 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
PATH = PREFIX + 'tranche-9/P9-ARG2b-Acceptance.json'
SELF = PREFIX + 'verification/p9_arg2b_acceptance.py'
DIGEST = '254cdc1d64fba737b2c3e4cc659c3ea44271eed7f21e48167899738434dd4c14'
CHANGED = {
    *('implementation/Phase-9-GRCV4-' + name + '.md'
      for name in ('Handoff', 'ImplementationPlan', 'ImplementationChecklist')),
    *(SIDE + 'GRCV4ExploratorySideToolImplementation' + name + '.md'
      for name in ('Plan', 'Checklist')),
    SIDE + 'docs/ARG2bTenthRealization.md',
    PREFIX + 'tranche-8/P9-ARG2b-NativeContinuation.md',
    SIDE + 'tool/src/grcv4_explorer/arg2b.py',
    *(PREFIX + 'verification/' + name + '.py' for name in
      ('p9_arg2b_historical', 'test_p9_arg2b_review', 'phase9_implementation_policy')),
}


@lru_cache(maxsize=64)
def original(root, name):
    return subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=root)


def record(root):
    value = json.loads((Path(root) / PATH).read_bytes())
    b.check_digest(value)
    b.require(value['record_digest'] == DIGEST and value['reviewed_commit'] == BASE
              and set(value['acceptance_sources']) == CHANGED,
              'A_RG2b acceptance identity or scope drift')
    return value


def peel_sha(root, name, present):
    """Authenticate only the finite acceptance-only presentation successor."""
    root = Path(root).resolve()
    if name not in CHANGED or not (root / PATH).exists():
        return present
    row = record(root)['acceptance_sources'][name]
    b.require(b.sha((root / name).read_bytes()) == row['after_sha256']
              and b.sha(original(root, name)) == row['before_sha256'],
              'A_RG2b acceptance source drift: ' + name)
    return row['before_sha256'] if present == row['after_sha256'] else present


def decision(root):
    root = Path(root).resolve()
    if not (root / PATH).exists():
        return None
    value = record(root)
    for name, row in value['acceptance_sources'].items():
        b.require(peel_sha(root, name, row['after_sha256']) == row['before_sha256'],
                  'A_RG2b acceptance source projection')
    execution = native.checked(root)
    b.require(execution['record_digest'] == value['evidence']['record_digest']
              and list(native.STEPS) == value['checkpoints']
              and execution['user_accepted'] is False,
              'A_RG2b accepted execution mismatch')
    for key in ('evidence', 'support', 'matrix', 'completion_release', 'storage'):
        ref = value[key]
        raw = (root / ref['path']).read_bytes()
        b.require(b.sha(raw) == ref['sha256'] and raw == original(root, ref['path']),
                  'A_RG2b accepted subject drift: ' + ref['path'])
        if 'record_digest' in ref:
            retained = json.loads(raw)
            b.check_digest(retained)
            b.require(retained['record_digest'] == ref['record_digest'],
                      'A_RG2b accepted record digest drift')
    return value
