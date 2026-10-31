"""P9-10.3 retained regression evidence; access never runs regression suites."""
from pathlib import Path
import sys


def checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / 'implementation/phase-9-grcv4/verification'))
    import p9103_regressions as c
    if c.ROOT != root:
        raise ValueError('regression repository mismatch')
    return root, c


def tranche10_regressions_status(root):
    root, c = checker(root)
    value = c.check()
    view = dict(schema='p9103-regression-view-v1',
        **{k: value[k] for k in ('status', 'families', 'tests_run', 'user_accepted',
             'P9_10_3_closed', 'all_ten_bounded_inputs_reconciled', 'G4_accepted',
             'full_GRC9V4_conformance', 'new_support', 'large_campaigns_rerun',
             'next_work', 'regressions', 'reconciliation')},
        release_id=value['preservation']['release_id'],
        unchanged_legacy_modules=value['preservation']['unchanged_legacy_modules'],
        execution_record_digest=value['record_digest'],
        evidence=[c.reference(root, c.PATH), c.reference(root, c.REVIEW)])
    import p9103_acceptance as acceptance
    accepted = acceptance.decision(root, value)
    ref = dict(**c.reference(root, acceptance.PATH), record_digest=accepted['record_digest'])
    view.update(status=accepted['status'], user_accepted=True, P9_10_3_closed=True,
                acceptance=ref, evidence=[*view['evidence'], ref], next_work=accepted['next_work'])
    return c.seal(view)


def tranche10_regressions_source(root, name):
    root, c = checker(root)
    value = c.check()
    import p9103_acceptance as acceptance
    acceptance.decision(root, value)
    refs = {r['path']: r for r in value['source_refs']}
    refs[acceptance.PATH] = c.reference(root, acceptance.PATH)
    for row in value['reconciliation']:
        refs.update((r['path'], r) for r in [*row['acceptances'], row['verification']])
    refs.update((p, c.historical_reference(root, p)) for p in (c.PATH, c.REVIEW, c.SELF))
    if name not in refs or Path(name).is_absolute() or '..' in Path(name).parts:
        raise KeyError('source is not indexed by P9-10.3')
    content = c.historical_bytes(root, name)
    if c.v.sha(content) != refs[name]['sha256']:
        raise ValueError('regression source drift')
    return content, refs[name]
