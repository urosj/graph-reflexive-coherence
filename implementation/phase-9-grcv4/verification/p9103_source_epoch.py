"""Exact test-only successor; original accepted execution remains at its Git epoch."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = '98033204'
BASE = 'implementation/phase-9-grcv4/'
PATH = BASE + 'tranche-10/P9-10.3-TestSourceEpoch.json'
SELF = BASE + 'verification/p9103_source_epoch.py'
TESTS = {'tests/models/test_grc_9_v4_contracts.py', 'tests/models/test_grc_9_v4_architecture.py'}
CHANGED = {*TESTS, BASE+'verification/p910_family_basin.py', BASE+'verification/p910_arg2b_source_epoch.py'}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def seal(value):
    body={k:v for k,v in value.items() if k!='record_digest'}
    return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(',',':')).encode()))


def original(root,name):
    return subprocess.check_output(['git','show',BASELINE+':'+name],cwd=root)


def test_scope(root):
    allowed = {'test_known_unavailable_families_reject_before_execution',
               'test_known_target_declaration_is_not_runtime_support',
               'test_execution_selection_is_independent'}
    def unchanged(raw):
        tree = ast.parse(raw)
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            tree.body.pop(0)  # module scope explanation
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                node.body = [n for n in node.body if getattr(n, 'name', None) not in allowed]
        return ast.dump(tree)
    for name in TESTS:
        if unchanged(original(root,name)) != unchanged((root/name).read_bytes()):
            raise ValueError('test correction changed unrelated assertions')
    return True


def manifest(root):
    test_scope(root)
    return seal(dict(schema='p9103-test-source-epoch-v1',predecessor=BASELINE,
        checker_sha256=sha((root/SELF).read_bytes()),
        sources={n:dict(before_sha256=sha(original(root,n)),after_sha256=sha((root/n).read_bytes())) for n in sorted(CHANGED)},
        production_changed=False,accepted_execution_rewritten=False))


def previous_bytes(root,name):
    root=Path(root).resolve();raw=(root/name).read_bytes()
    if name not in CHANGED:return raw
    value=json.loads((root/PATH).read_bytes())
    if value!=manifest(root):raise ValueError('unbound regression test/source successor')
    return original(root,name)


def peel_sha(root,name,present):
    previous=previous_bytes(root,name)
    return sha(previous) if present==sha((root/name).read_bytes()) else present


def read_source(root,ref):
    old=previous_bytes(root,ref['path'])
    if sha(old)!=ref['sha256']:raise ValueError('unbound regression historical source')
    return old,dict(ref,revision=BASELINE,basis='historical_git')
