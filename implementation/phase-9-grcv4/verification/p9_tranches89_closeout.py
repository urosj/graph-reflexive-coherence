"""All-ten Tranches 8–9 reconciliation over accepted, unchanged evidence."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import subprocess

import p984b_runtime as b

BASE = '7083b989'
PREFIX = 'implementation/phase-9-grcv4/'
SIDE = 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
PATH = PREFIX + 'tranche-9/P9-Tranches8-9-AllTenAcceptance.json'
SELF = PREFIX + 'verification/p9_tranches89_closeout.py'
DIGEST = '3c198c83641fac16dc7de41086582c0b7824070e4144d3af11301ae5f0d8f8bc'
FIRST = {'C_OS', 'C_CI', 'A_CI', 'A_PC'}
LATER = {'A_OS': 'AOS', 'C_PC': 'CPC', 'C_CI_PC': 'CCIPC',
         'A_CI_PC': 'ACIPC', 'C_RG2b': 'CRG2b', 'A_RG2b': 'ARG2b'}
FAMILIES = FIRST | set(LATER)
STEPS = ('8.4d', '8.4e', '8.4f', '8.4g', '8.4h', '8.4i', '8.5', '8.6',
         'tranche8_end', '9.1b', '9.2', '9.3', '9.4a', '9.4b', '9.5', '9.6')
CHANGED = {
    *('implementation/Phase-9-GRCV4-' + n + '.md' for n in
      ('Handoff', 'ImplementationPlan', 'ImplementationChecklist')),
    *(SIDE + 'GRCV4ExploratorySideToolImplementation' + n + '.md'
      for n in ('Plan', 'Checklist')),
    SIDE + 'tool/src/grcv4_explorer/arg2b.py',
    SIDE + 'docs/ARG2bTenthRealization.md',
    PREFIX + 'verification/p9_arg2b_acceptance.py',
    PREFIX + 'verification/phase9_implementation_policy.py',
}
# These living documents and the maintenance roster may advance after closeout.
# Accepted scientific/runtime evidence and historical checker bytes stay frozen.
MAINTAINED_PRESENTATIONS = {
    *('implementation/Phase-9-GRCV4-' + n + '.md' for n in
      ('Handoff', 'ImplementationPlan', 'ImplementationChecklist')),
    *(SIDE + 'GRCV4ExploratorySideToolImplementation' + n + '.md'
      for n in ('Plan', 'Checklist')),
    PREFIX + 'verification/phase9_implementation_policy.py',
}
CLOSEOUT_COMMIT = '7ae0b128'
# Verification/presentation successors only; no scientific producer belongs here.
POST_CLOSEOUT_READERS = {
    PREFIX + 'verification/p9_crg2b_historical.py',
    *(SIDE + 'tool/' + n for n in ('scripts/serve_phase9.py',
      'src/grcv4_explorer/phase9_verification.py', 'phase9-web/index.html',
      'notebooks/phase9_verification.ipynb')),
}


def maintained_preimage(root, name, present):
    if name not in MAINTAINED_PRESENTATIONS | POST_CLOSEOUT_READERS:
        return present
    old = subprocess.check_output(['git', 'show', CLOSEOUT_COMMIT + ':' + name], cwd=root)
    live = b.sha((root / name).read_bytes())
    if live == b.sha(old):
        return present
    from phase9_implementation_policy import digest_record
    boundary = json.loads((root / PREFIX / 'verification/Phase9ImplementationBoundary.json').read_bytes())
    rows = {r['path']: r['sha256'] for r in boundary['artifact_bindings']}
    b.require(boundary['record_digest'] == digest_record(boundary) and rows.get(name) == live,
              'unbound post-closeout maintenance: ' + name)
    return b.sha(old) if present == live else present


@lru_cache(maxsize=64)
def original(root, name):
    return subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=root)


def record(root):
    value = json.loads((Path(root) / PATH).read_bytes())
    b.check_digest(value)
    b.require(value['record_digest'] == DIGEST and value['reviewed_commit'] == BASE
              and set(value['presentation_sources']) == CHANGED,
              'Tranches 8–9 closure identity or scope drift')
    return value


def peel_sha(root, name, present):
    root = Path(root).resolve()
    present = maintained_preimage(root, name, present)
    if name not in CHANGED or not (root / PATH).exists():
        return present
    row = record(root)['presentation_sources'][name]
    live = b.sha((root / name).read_bytes())
    if live != row['after_sha256'] and name in MAINTAINED_PRESENTATIONS:
        # Authenticate historical bytes at the committed closeout, and current
        # bytes through the existing maintenance boundary. Never rewrite the
        # acceptance or call the current document an old execution input.
        historical = subprocess.check_output(['git', 'show', CLOSEOUT_COMMIT + ':' + name], cwd=root)
        b.require(maintained_preimage(root, name, live) == row['after_sha256']
                  and b.sha(historical) == row['after_sha256'],
                  'maintained presentation or historical closeout drift: ' + name)
        if present == live:
            present = row['after_sha256']
        live = row['after_sha256']
    b.require(live == row['after_sha256']
              and b.sha(original(root, name)) == row['before_sha256'],
              'Tranches 8–9 closure source drift: ' + name)
    return row['before_sha256'] if present == row['after_sha256'] else present


def checked(root=b.ROOT):
    root = Path(root).resolve()
    value = record(root)
    for name, row in value['presentation_sources'].items():
        b.require(peel_sha(root, name, row['after_sha256']) == row['before_sha256'],
                  'Tranches 8–9 presentation binding')
    records = {}
    for ref in value['sources']:
        raw = (root / ref['path']).read_bytes()
        b.require(b.sha(raw) == ref['sha256'], 'Tranches 8–9 evidence drift: ' + ref['path'])
        retained = json.loads(raw)
        b.require(retained['record_digest'] == ref['record_digest'], 'closure source identity drift')
        records[ref['path']] = retained
    first = records[PREFIX + 'tranche-8/P9-Tranche8-FirstGroupAcceptance.json']
    b.require(first['user_accepted'] and first['first_group_closed']
              and set(first['families']) == FIRST, 'missing first-group Tranche 8 acceptance')
    for step in ('9.1b', '9.2', '9.3', '9.4a', '9.4b', '9.5', '9.6'):
        v = records[PREFIX + 'tranche-9/P9-' + step + '-Acceptance.json']
        b.require(v['user_accepted'] is True and v['bounded_leaf_closed'] is True,
                  'missing first-group Tranche 9 acceptance: ' + step)
    for family, code in LATER.items():
        v = records[PREFIX + 'tranche-9/P9-' + code + '-Acceptance.json']
        b.require(v['family'] == family and v['user_accepted'] is True
                  and v['bounded_scope_closed'] is True and v['checkpoints'] == list(STEPS),
                  'missing family checkpoint acceptance: ' + family)
        b.require(records[v['evidence']['path']]['record_digest'] == v['evidence']['record_digest'],
                  'accepted family evidence mismatch: ' + family)
    matrix = records[PREFIX + 'tranche-8/arg2b-native/9.3-Matrix.json']
    cells = deepcopy(matrix['cells'])
    pairs = {(v['family'], v['surface']) for v in cells}
    b.require(len(cells) == 40 and pairs == {(f, s) for f in FAMILIES
              for s in ('transition', 'state', 'observable', 'lifecycle')}, 'incomplete compatibility population')
    for cell in cells:
        if cell['family'] == 'A_RG2b':
            accepted = records[PREFIX + 'tranche-9/P9-ARG2b-Acceptance.json']
            b.require(cell['disposition'] == 'passed_pending_acceptance', 'original A_RG2b disposition drift')
            cell.update(disposition='bounded_accepted', acceptance=dict(
                path=PREFIX + 'tranche-9/P9-ARG2b-Acceptance.json', record_digest=accepted['record_digest']))
        b.require(cell['disposition'] == 'bounded_accepted' and cell['acceptance'] is not None,
                  'unaccepted compatibility subject')
    return dict(schema='phase9_tranches89_closeout_view_v1', record_digest=value['record_digest'],
                path=PATH, families=sorted(FAMILIES), user_accepted=True,
                tranche8_closed=True, tranche9_closed=True, aggregate_closed=True,
                compatibility_counts=dict(bounded_accepted=40, passed_pending_acceptance=0, unselected_not_executed=0),
                optional_completion='unselected_deferred_not_a_closure_blocker',
                full_GRC9V4_conformance=False, G4_accepted=False,
                limits=value['retained_limits'], check_level='retained_reconciliation_no_numerical_rerun',
                compatibility_cells=cells)


if __name__ == '__main__':
    value = checked()
    print('TRANCHES_8_9_CLOSED families=10 compatibility_cells=40 native_rerun=false full_conformance=false')
