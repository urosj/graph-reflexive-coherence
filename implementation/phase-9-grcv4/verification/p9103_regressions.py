"""P9-10.3: reconcile bounded acceptances, run focused regressions, preserve sources.

--run performs four independent regression jobs. --check authenticates retained
results and rechecks identities; it never reruns trajectories or the test suites.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import platform
import subprocess
import time
import unittest

import p9102_verification as v
import p9102_acceptance as first_acceptance
import p910_family_basin as families
import p910_family_acceptance as family_acceptance

ROOT = v.ROOT
BASELINE = '98033204'
BASE = v.BASE
SELF = BASE + 'verification/p9103_regressions.py'
PATH = BASE + 'tranche-10/P9-10.3-Regressions.json'
REVIEW = BASE + 'tranche-10/P9-10.3-Review.md'
FAMILIES = tuple(sorted((*v.FAMILIES, *families.FAMILIES)))
GROUPS = {
    'legacy_generic': (
        'tests.core.test_import_smoke', 'tests.core.test_module_imports',
        'tests.models.test_grc_v2_construction',
        'tests.models.test_grc_v2_runtime_persistence',
        'tests.models.test_grc_v2_step_skeleton',
        'tests.models.test_grc_v3_state', 'tests.models.test_grc_v3_step',
        'tests.models.test_grc_v3_serialization'),
    'legacy_nine_port': (
        'tests.models.test_grc_9_v3_state', 'tests.models.test_grc_9_v3_step',
        'tests.models.test_grc_9_v3_differential',
        'tests.models.test_grc_9_v3_transport', 'tests.models.test_grc_9_v3_sparks',
        'tests.models.test_grc_9_v3_hessian_readiness'),
    'shared_public_contracts': (
        'tests.models.test_grc_9_v4_contracts',
        'tests.models.test_grc_9_v4_basin.BasinGraphTests'),
    'shared_lifecycle_boundaries': (
        'tests.models.test_grc_9_v4_architecture',
        'tests.models.test_grc_9_v4_legacy.DelegateBoundaryTests'),
}
require, seal, reference = v.require, v.seal, v.reference
from p9104_source_epoch import previous_bytes as historical_bytes, reference as historical_reference


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def source_bindings():
    """Exact production/spec preservation at entry, plus the regression inputs."""
    names = git('ls-tree', '-r', '--name-only', BASELINE, 'src', 'specs',
                'tests', 'examples/grcv4').decode().splitlines()
    names = [n for n in names if Path(n).suffix in ('.py', '.json', '.sha256', '.md', '.xz')]
    import p9103_source_epoch as correction
    import p9104_source_epoch as publication
    changed = set(git('diff', '--name-only', BASELINE, '--', 'src', 'specs', 'tests', 'examples/grcv4').decode().splitlines())
    require(changed <= correction.TESTS | publication.DOCS, 'P9-10.3 production/spec/test input drift; review affected reruns')
    for name in correction.TESTS:
        correction.previous_bytes(ROOT, name)
    require(not git('ls-files', '--others', '--exclude-standard', '--',
                    'src', 'specs', 'tests', 'examples/grcv4').strip(),
            'untracked regression input')
    return [historical_reference(ROOT, n) if n in publication.DOCS else reference(ROOT, n) for n in sorted(names)]


def preservation():
    import phase9_implementation_policy as p
    from p9_tranches89_closeout import checked
    legacy = git('ls-tree', '-r', '--name-only', p.BASELINE, 'src/pygrc').decode().splitlines()
    # The models package initializer gained lazy V4 exports; its accepted
    # current bytes and the regression import tests are checked separately.
    legacy = [n for n in legacy if n.endswith('.py') and n != 'src/pygrc/models/__init__.py']
    for name in legacy:
        require((ROOT / name).read_bytes() == git('show', p.BASELINE + ':' + name),
                'pre-V4 production changed: ' + name)
    release = p.current_abundance_release(ROOT)
    packaged = ROOT / 'src/pygrc/models/grc_v4_assets'
    releases = []
    for path in sorted((ROOT / 'specs').glob('*release*')):
        if path.suffix not in ('.json', '.sha256'):
            continue
        other = packaged / path.name
        if other.exists():
            require(path.read_bytes() == other.read_bytes(), 'packaged release differs: ' + path.name)
            releases.extend(reference(ROOT, q.relative_to(ROOT).as_posix()) for q in (path, other))
    prior = checked(ROOT)
    require(prior['families'] == list(FAMILIES) and prior['tranche8_closed'] and prior['tranche9_closed'],
            'missing accepted Tranches 8-9 population')
    return dict(legacy_epoch=p.BASELINE, unchanged_legacy_modules=len(legacy),
                legacy_sources=[reference(ROOT, n) for n in legacy],
                models_initializer='accepted_additive_V4_exports_bound_at_entry_and_import_tested',
                release_id=release, packaged_release_pairs=releases,
                regression_test_correction=reference(ROOT, BASE+'tranche-10/P9-10.3-TestSourceEpoch.json'),
                tranches89_acceptance=reference(ROOT, 'implementation/phase-9-grcv4/tranche-9/P9-Tranches8-9-AllTenAcceptance.json'))


def reconcile_one(family):
    with v.no_native_runs():
        value = families.check(family)
        decision = family_acceptance.decision(ROOT, value)
        require(decision is not None, 'missing family acceptance')
        return dict(family=family,
            acceptances=[reference(ROOT, family_acceptance.path(family))],
            verification=families.load(family)[1],
            subjects={k: value['target_compatibility'][k]['subject'] for k in ('v1', 'v2')},
            saved_charge_checks=len(value['verification']['charges']),
            receipts=sum(x['receipts'] for x in value['verification']['ledgers'].values()),
            commit_groups=sum(x['commit_groups'] for x in value['verification']['ledgers'].values()),
            limits=decision['scope'])


def reconciliation(workers=1):
    with v.no_native_runs():
        value = v.check()
        first_acceptance.decision(ROOT, value)
    first = []
    for row in value['families_checked']:
        first.append(dict(family=row['family'],
            acceptances=[reference(ROOT, first_acceptance.PATH),
                         *[reference(ROOT, m.PATH) for m in _first_modules()]],
            verification=reference(ROOT, v.PATH),
            subjects={x['version']: x['subject'] for x in row['versions']},
            saved_charge_checks=len(row['independent_charge_checks']),
            receipts=sum(x['ledger']['receipts'] for x in row['versions']),
            commit_groups=sum(x['ledger']['commit_groups'] for x in row['versions']),
            limits='Exact accepted first-four subjects; represented-flow diagnostic; fixed-H bounds do not prove exact CI-root signs; no G4 or full conformance.'))
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            later = list(pool.map(reconcile_one, families.FAMILIES))
    else:
        later = [reconcile_one(f) for f in families.FAMILIES]
    rows = sorted([*first, *later], key=lambda x: x['family'])
    require([r['family'] for r in rows] == list(FAMILIES), 'family coverage mismatch')
    require(all(set(r['subjects']) == {'v1', 'v2'} and r['saved_charge_checks'] == 4 for r in rows),
            'missing exact target/role coverage')
    return rows


def _first_modules():
    import p9101a_acceptance as a
    import p9101b_acceptance as b
    import p9101c_acceptance as c
    return a, b, c


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def roster(group):
    suite = unittest.defaultTestLoader.loadTestsFromNames(GROUPS[group])
    return suite, [t.id() for t in flatten(suite)]


def run_group(group):
    import flint
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    start = time.monotonic()
    suite, ids = roster(group)
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output), exact_backend(ExactBackend.FLINT):
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    require(result.wasSuccessful() and not result.skipped and not result.expectedFailures
            and result.testsRun == len(ids) and len(ids) > 0,
            group + ' failed:\n' + output.getvalue())
    return dict(group=group, tests=ids, tests_run=result.testsRun,
                failures=0, errors=0, skips=0, expected_failures=0,
                status='passed', elapsed_seconds=round(time.monotonic()-start, 3),
                python=platform.python_version(), python_flint=flint.__version__, exact_backend='flint')


def validate(value):
    require(value == seal(value) and value['schema'] == 'p9103-regressions-v1', 'record identity')
    require(value['status'] == 'passed_pending_acceptance' and value['families'] == list(FAMILIES)
            and value['all_ten_bounded_inputs_reconciled'] is True
            and all(value[k] is False for k in ('user_accepted', 'P9_10_3_closed',
                'full_GRC9V4_conformance', 'G4_accepted')) and value['new_support'] == []
            and value['large_campaigns_rerun'] == 0, 'regression scope changed')
    require(value['source_epoch'] == git('rev-parse', BASELINE).decode().strip()
            and value['source_refs'] == source_bindings()
            and value['checker'] == historical_reference(ROOT, SELF), 'regression source/checker drift')
    require(value['reconciliation'] == reconciliation() and value['preservation'] == preservation(),
            'accepted inputs or release preservation changed')
    require([r['group'] for r in value['regressions']] == list(GROUPS), 'regression groups changed')
    for row in value['regressions']:
        _, ids = roster(row['group'])
        require(row['tests'] == ids and row['tests_run'] == len(ids) > 0
                and row['status'] == 'passed'
                and all(row[k] == 0 for k in ('failures', 'errors', 'skips', 'expected_failures')),
                'regression roster/outcome mismatch')
    require(value['tests_run'] == sum(r['tests_run'] for r in value['regressions']), 'test count mismatch')
    return value


def run(workers=4):
    require(not (ROOT / PATH).exists(), 'refuse to overwrite regression evidence')
    before = source_bindings()
    preserved = preservation()
    rows = reconciliation(workers)
    print('Accepted inputs and release identities reconciled; starting four regression jobs.', flush=True)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_group, name): name for name in GROUPS}
        completed = {}
        for future in as_completed(futures):
            row = future.result()
            completed[row['group']] = row
            print(f"{row['group']}: {row['tests_run']} passed in {row['elapsed_seconds']} s", flush=True)
        runs = [completed[name] for name in GROUPS]
    require(before == source_bindings(), 'input sources changed during execution')
    value = seal(dict(schema='p9103-regressions-v1', status='passed_pending_acceptance',
        families=list(FAMILIES), source_epoch=git('rev-parse', BASELINE).decode().strip(),
        checker=reference(ROOT, SELF), source_refs=before, preservation=preserved,
        reconciliation=rows, all_ten_bounded_inputs_reconciled=True,
        regressions=runs, tests_run=sum(r['tests_run'] for r in runs), workers=workers,
        user_accepted=False, P9_10_3_closed=False, full_GRC9V4_conformance=False,
        G4_accepted=False, new_support=[], large_campaigns_rerun=0,
        execution_scope='Fresh focused old-family/shared-interface regressions; accepted numerical, compatibility and replay campaigns reused by exact identity.',
        next_work='Review bounded P9-10.3; then P9-10.4 capability/example publication, P9-10.5 debt reconciliation and P9-10.6 G4/handoff.'))
    # No duplicate numeric payloads; original records are referenced by hash.
    raw = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n'
    require(len(raw.encode()) <= 1_000_000, 'record requires compressed storage')
    with (ROOT / PATH).open('x') as stream:
        stream.write(raw)
    return value


def check():
    return validate(json.loads((ROOT / PATH).read_bytes()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--workers', type=int, choices=range(1, 13), default=4)
    args = parser.parse_args()
    value = run(args.workers) if args.run else check()
    print(json.dumps({k: value[k] for k in ('status', 'tests_run', 'families', 'record_digest')}))
