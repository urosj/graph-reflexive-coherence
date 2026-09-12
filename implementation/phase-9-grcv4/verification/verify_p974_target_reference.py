"""Inspect bounded P9-7.4 evidence; --run emits a new execution without writing."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
from verify_p972b_runtime import bindings as runtime_bindings

SCRIPT = p.HERE + 'verify_p974_target_reference.py'
TEST = p.HERE + 'test_p974_target_reference.py'
RECORD = p.PHASE + 'tranche-7/P9-7.4-TargetReference.json'
CONTRACTS = ('D10.2-EC-EVENT-C-DERIVED', 'D10.2-EC-EVENT-READMISSION-RECEIPT',
             'D11-C-EC-C-TR-REFERENCE-FIELD', 'D11-C-EC-C-J0-LIFECYCLE',
             'D11-C-EC-C-J0-REALIZATION-COVERAGE')


def bindings():
    names = {SCRIPT, TEST, 'specs/grc-v4-spec.md', 'specs/grc-v4-topology-event-spec.md',
             p.INV + 'drafts/2026-09-GRC-V4.md'}
    return {**runtime_bindings(), **{n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}}


def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {n: contract_provenance(context, n) for n in CONTRACTS}


def predecessor():
    from verify_p973_acceptance import check
    value = check()
    p.require(value['user_accepted'] and value['aggregate_closed'], 'P9-7.3 is not accepted')
    return {n: value[n] for n in ('record_digest', 'regression_record_digest', 'acceptance_sha256')}


def roster():
    from test_p974_target_reference import TargetReferenceTests
    return ['test_p974_target_reference.TargetReferenceTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(TargetReferenceTests)]


def check():
    from test_p974_target_reference import FAMILIES
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_target_reference_execution_v1'
              and value['iteration_id'] == 'P9-7.4'
              and value['record_digest'] == p.digest_record(value), 'target-reference evidence drift')
    p.require(value['source_bindings'] == bindings(), 'target-reference source drift')
    p.require(value['authority'] == authority() and value['predecessor'] == predecessor(),
              'target-reference authority or predecessor drift')
    p.require(value['test_ids'] == roster()
              and value['results'] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]),
              'target-reference execution incomplete')
    p.require(value['user_accepted'] is False and value['aggregate_closed'] is False
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'target-reference overclaim')
    cases = value['cases']
    p.require(set(cases) == {'reference_rejections', 'five_targets', 'changed_graph',
                            'atomic_rejections', 'late_failure'}, 'target-reference case drift')
    expected = {(f, m) for f in FAMILIES for m in ('missing', 'extra', 'unmatched_same_dimension',
                'zero', 'negative', 'nan', 'infinity', 'duplicate')}
    p.require(len(cases['reference_rejections']) == 40
              and {(r['family'], r['mutation']) for r in cases['reference_rejections']} == expected,
              'target-reference negative roster drift')
    p.require([r['family'] for r in cases['five_targets']] == list(FAMILIES)
              and len(cases['changed_graph']['numerical_roles']) == 2
              and [r['operation'] for r in cases['atomic_rejections']] == ['event', 'migration']
              and cases['late_failure'] == 'unexpected_error_propagates_with_original_whole_publication',
              'target-reference native scope drift')
    return dict(status='verified_pending_review', record_path=RECORD, record_digest=value['record_digest'],
                test_count=len(roster()), c_target_families=list(FAMILIES), reference_rejections=40,
                user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
                numerical_tests_rerun=0)


def run():
    from test_p974_target_reference import EVIDENCE
    sources, traces, prior, ids = bindings(), authority(), predecessor(), roster()
    EVIDENCE.clear()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'target-reference tests failed')
    p.require(sources == bindings(), 'sources changed during target-reference execution')
    value = dict(schema='phase9_target_reference_execution_v1', iteration_id='P9-7.4',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=sources,
        authority=traces, predecessor=prior, test_ids=ids,
        results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE,
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n)
                         for n in ('numpy', 'jsonschema', 'rfc8785')}),
        user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
        scope='Five C target witnesses, changed-graph dense-oracle discrimination, reference construction and atomic failure pressure; not all graphs, parameters or profile pairs.')
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), indent=2))
