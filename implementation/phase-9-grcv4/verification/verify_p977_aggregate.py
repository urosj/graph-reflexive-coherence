"""Reconcile accepted child decisions, not rerun or broaden their science.

The original HOLD and all accepted executions remain immutable. Current runtime
conformance stays with the existing child checkers; this successor checks their
accepted record identities, catalog coverage and preserved scope boundaries.
"""

import argparse
from functools import lru_cache
import json

import phase9_implementation_policy as p
import profile_g2_registry as g
import verify_p977_profile_review as original

BASE = 'ffbcabf'
REVIEW_CHECKPOINT = '1863ab8b8a24edbb811024e4afeecfca161a9928'
ACCEPTANCE = p.PHASE + 'tranche-7/P9-7.7-AggregateAcceptance.json'
ACCEPTANCE_DIGEST = 'd3a220a82a8c6c15a77f064d6ae45b9bf4978f5bd247e32d871c2220acae91e1'
RECORD = p.PHASE + 'tranche-7/P9-7.7-AggregateReconciliation.json'
SCRIPT = p.HERE + 'verify_p977_aggregate.py'
TEST = p.HERE + 'test_p977_aggregate.py'
BROWSER = p.SIDE + 'tool/phase9-web/aggregate-review.js'
OBLIGATIONS = ('G2-EXACT-PRODUCT', 'G2-ORDERED-ENDPOINTS', 'G2-INTEGRATED-REVIEW')


def build():
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    inputs = {}

    @lru_cache(None)
    def read(name):
        content = p.safe_path(p.ROOT, name).read_bytes()
        p.require(content == p.git(p.ROOT, 'show', BASE + ':' + name),
                  'accepted aggregate input changed: ' + name)
        value = json.loads(content)
        if 'record_digest' in value:
            p.require(value['record_digest'] == p.digest_record(value), 'input digest drift: ' + name)
        inputs[name] = p.sha(content)
        return value

    def resolve(ref):
        value = read(ref['path'])
        for part in ref['json_pointer'].strip('/').split('/'):
            if part:
                part = part.replace('~1', '/').replace('~0', '~')
                value = value[int(part)] if isinstance(value, list) else value[part]
        p.require(value is not None, 'missing aggregate evidence pointer')
        return value

    initial = read(original.RECORD)
    catalog = read(original.CATALOG)
    register = read(original.REGISTER)
    read(g.REGISTRY)
    roster = g.registry(p.ROOT)
    normalized = g.checked(p.ROOT)  # Existing trusted historical/common adapters.
    expected_families = [r['profile_family'] for r in initial['profiles']]
    rows = {r['profile_family_id']: r for r in roster['records']}
    p.require(len(rows) == len(roster['records']) == 10 and set(rows) == set(expected_families),
              'aggregate family population changed')
    p.require(all(r['state'] == 'accepted' for r in rows.values()), 'unaccepted aggregate child')
    classes = [r['migration_class'] for r in register['migration_classes']]
    result = []
    for index, old in enumerate(initial['profiles']):
        family = old['profile_family']
        row = rows[family]
        accepted = read(row['acceptance']['path'])
        reviewed = read(row['review']['path'])
        nomination = accepted['accepted_profile']
        p.require(nomination == old['nomination'] and nomination['complete_profile_id'] == row['complete_profile_id'],
                  'nomination replaced or joined only by family')
        ids = original.required_cases(family)
        p.require(ids == next(r['required_catalog_case_ids'] for r in register['profiles']
                             if r['profile_family'] == family), 'catalog/register drift')
        p.require(sorted(ids) == sorted(c['fixture_id'] for c in old['cells']), 'initial applicability drift')
        cells = []
        if family == 'C_OS':
            for old_cell in old['cells']:
                refs = old_cell['evidence']
                p.require(len(refs) == 1, 'C_OS alias must resolve one original result')
                execution = resolve(refs[0])
                p.require(execution['fixture_id'] == old_cell['fixture_id']
                          and execution['complete_profile_id'] == row['complete_profile_id']
                          and set(catalog['execution_contract']['required_result_fields']) <= set(execution),
                          'C_OS alias scope or result fields changed')
                cells.append(dict(fixture_id=old_cell['fixture_id'], disposition='accepted_historical_alias',
                                  evidence=refs[0]))
            obligations = dict.fromkeys(OBLIGATIONS, 'accepted_P9_4_8B_alias_no_new_credit')
            scope = dict(acceptance_scope=accepted['scope'], source_debt_policy=accepted['source_debt_policy'],
                         original_review_obligations=reviewed['obligations'])
            authority = original.ref(row['acceptance']['path'], '/source_debt_policy')
            interface = original.ref(row['review']['path'], '/obligations')
        else:
            p.require(reviewed['obligations'] == dict.fromkeys(OBLIGATIONS, 'satisfied_for_exact_declared_scope'),
                      'unresolved child obligation')
            p.require(reviewed['nomination'] == nomination, 'child review differs from accepted nomination')
            product = reviewed['catalog_product']
            p.require(len(product) == len(ids) and sorted(c['fixture_id'] for c in product) == sorted(ids),
                      'missing/duplicate/foreign child catalog cell')
            for path, digest in reviewed['evidence_digests'].items():
                p.require(read(path)['record_digest'] == digest, 'child evidence identity changed')
            for i, cell in enumerate(product):
                execution = resolve(cell['evidence'])
                if 'linked_executions' in cell:
                    p.require(execution == cell['linked_executions'], 'crossing links changed')
                else:
                    p.require(execution['fixture_id'] == cell['fixture_id']
                              and execution['complete_profile_id'] == cell['source_complete_profile_id']
                              and execution['target_active_model_identity'] == cell['target_complete_profile_id'],
                              'control or endpoint relabeled as nomination')
                cells.append(dict(fixture_id=cell['fixture_id'], disposition='accepted_child_scope',
                    reviewed_cell=original.ref(row['review']['path'], '/catalog_product/' + str(i))))
            matrix = reviewed['ordered_scope']['matrix']
            p.require(len(matrix) == 7 and sorted(r['migration_class'] for r in matrix) == sorted(classes),
                      'missing/duplicate migration class disposition')
            p.require(reviewed['ordered_scope']['all_ordered_pairs_verified'] is False,
                      'aggregate must not manufacture all-pairs coverage')
            obligations = reviewed['obligations']
            scope = reviewed['ordered_scope']
            authority = original.ref(row['review']['path'], '/authority')
            interface = reviewed['interface_evidence']
            resolve(authority)
            resolve(interface)
        result.append(dict(profile_family=family, complete_profile_id=row['complete_profile_id'],
            initial_nomination=original.ref(original.RECORD, '/profiles/' + str(index)),
            review=row['review'], acceptance=row['acceptance'], obligations=obligations,
            cells=sorted(cells, key=lambda c: c['fixture_id']), ordered_scope=scope,
            authority_and_debt=authority, interface_evidence=interface,
            new_execution_credit=0))
    count = sum(len(r['cells']) for r in result)
    p.require(count == 305, 'aggregate catalog count drift')
    value = dict(schema='phase9_profile_aggregate_reconciliation_v1', iteration_id='P9-7.7',
        status='reconciled_pending_independent_review', user_accepted=False, aggregate_closed=False,
        G3_accepted=False, all_ordered_pairs_verified=False, new_G2_support=[],
        new_runtime_iterations_authorized=[], admitted_specialization_support_sets=[],
        accepted_checkpoint=BASE, initial_review=original.ref(original.RECORD, ''),
        accepted_generic_runtime_support=normalized['accepted_generic_runtime_support'],
        profiles=result, input_bindings=inputs,
        # Preserve the accepted review's original checker identities. Current
        # acceptance/projection code is separately bound by the maintenance
        # manifest and checked import path; this is not a live-source waiver.
        checker_bindings={n: p.sha(p.git(p.ROOT, 'show', REVIEW_CHECKPOINT + ':' + n)) for n in (SCRIPT, TEST)},
        summary=dict(profile_count=10, required_cells=count, reconciled_cells=count,
            accepted_alias_cells=33, accepted_child_cells=272, unresolved_cells=0,
            unresolved_child_obligations=[], numerical_tests_rerun=0, new_execution_credit=0,
            pending_aggregate_review=True),
        scope='Accepted exact catalog obligations and retained endpoint dispositions only; no all-pairs, arbitrary parameters, formation authentication, stronger RG2b regularity or specialization admission. Current scientific replay remains with the existing child checkers; this record reconciles their accepted evidence, not a new numerical run.')
    value['record_digest'] = p.digest_record(value)
    return value


def validate(value, expected):
    p.require(value['record_digest'] == p.digest_record(value), 'aggregate digest drift')
    p.require(value == expected, 'aggregate differs from accepted child evidence or widens scope')


def acceptance(value):
    decision = p.read(p.ROOT / ACCEPTANCE)
    p.require(decision['record_digest'] == p.digest_record(decision) == ACCEPTANCE_DIGEST
              and decision['reviewed_commit'] == REVIEW_CHECKPOINT, 'aggregate acceptance identity drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', REVIEW_CHECKPOINT, 'HEAD')
    for ref in (decision['review'], decision['review_text']):
        current = p.safe_path(p.ROOT, ref['path']).read_bytes()
        p.require(current == p.git(p.ROOT, 'show', REVIEW_CHECKPOINT + ':' + ref['path'])
                  and p.sha(current) == ref['sha256'], 'accepted aggregate subject changed')
    p.require(value['record_digest'] == decision['review']['record_digest']
              and value['accepted_generic_runtime_support'] == decision['accepted_generic_runtime_support'],
              'aggregate acceptance differs from reviewed scope')
    return decision


def view(value):
    result = {k: value[k] for k in ('status', 'user_accepted', 'aggregate_closed', 'G3_accepted',
        'all_ordered_pairs_verified', 'new_G2_support', 'new_runtime_iterations_authorized',
        'admitted_specialization_support_sets', 'accepted_generic_runtime_support')} | dict(
        record_path=RECORD, record_digest=value['record_digest'], **value['summary'])
    decision = acceptance(value)
    result.update(status='accepted', user_accepted=True, aggregate_closed=True,
                  pending_aggregate_review=False, acceptance_path=ACCEPTANCE,
                  acceptance_digest=decision['record_digest'])
    return result


def browser_source(value):
    return '// Generated from the checked P9-7.7 aggregate record. No acceptance authority.\nexport const AGGREGATE_REVIEW = ' + json.dumps(view(value), indent=2) + ';\n'


def check(profile_views=None):
    value = p.read(p.ROOT / RECORD)
    validate(value, build())
    p.require((p.ROOT/BROWSER).read_text() == browser_source(value), 'aggregate browser projection drift')
    if profile_views is not None:
        roster = g.registry(p.ROOT)
        p.require(profile_views['profile_g2'] == [g.view(r) for r in roster['records']],
                  'aggregate/status support disagreement')
        for row in roster['records']:
            if row['adapter'] != 'historical_c_os':
                actual = profile_views[row['view_key']]
                p.require(actual['status'] == 'accepted' and actual['G2_accepted'] is True
                          and actual['record_digest'] == row['review']['record_digest']
                          and actual['acceptance_digest'] == row['acceptance']['record_digest'],
                          'aggregate materialized child is not accepted')
    return view(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    p.current_boundary(p.ROOT)
    print(json.dumps(build() if args.emit else check(), indent=2))
