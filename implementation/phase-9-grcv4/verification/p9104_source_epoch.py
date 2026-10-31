"""Finite documentation successor for accepted P9-10.3 evidence.

Only two old example guides change. Original checked code/docs remain readable
at their accepted Git revision. No production, spec, test or result is replaced.
"""
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = '32ba54dd'
BASE = 'implementation/phase-9-grcv4/'
PATH = BASE+'tranche-10/P9-10.4-DocumentationSourceEpoch.json'
SELF = BASE+'verification/p9104_source_epoch.py'
DOCS = {'examples/grcv4/README.md', 'examples/grcv4/grc9v4_api.md'}
CHANGED = DOCS | {BASE+'verification/p9103_regressions.py', BASE+'verification/p9103_acceptance.py'}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def original(root, name):
    return subprocess.check_output(['git', 'show', BASELINE+':'+name], cwd=root)


def manifest(root):
    root = Path(root)
    return dict(schema='p9104-documentation-successor-v1', predecessor=BASELINE,
        checker_sha256=sha((root/SELF).read_bytes()), production_changed=False,
        original_results_unchanged=True,
        sources={n:dict(before_sha256=sha(original(root,n)),
            after_sha256=sha((root/n).read_bytes())) for n in sorted(CHANGED)})


def previous_bytes(root, name):
    root = Path(root)
    if name not in CHANGED:
        return (root/name).read_bytes()
    if json.loads((root/PATH).read_bytes()) != manifest(root):
        raise ValueError('unbound P9-10.4 documentation/checker successor')
    return original(root, name)


def reference(root, name):
    return dict(path=name, sha256=sha(previous_bytes(root, name)))
