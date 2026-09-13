"""Check retained P9-7.5 evidence; --run emits a new execution, never writes."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
from verify_p972b_runtime import bindings as runtime_bindings

SCRIPT = p.HERE + 'verify_p975_failure_sequences.py'
TEST = p.HERE + 'test_p975_failure_sequences.py'
RECORD = p.PHASE + 'tranche-7/P9-7.5-FailureSequences.json'
CONTRACTS = ('D10.2-EC-EVENT-A-HISTORY', 'D10.2-EC-EVENT-K4-HISTORY',
             'D10.2-EC-EVENT-LIFECYCLE-TUPLE', 'D10.2-EC-EVENT-READMISSION-RECEIPT')


def bindings():
    names = {SCRIPT, TEST, 'specs/grc-v4-spec.md', 'specs/grc-v4-topology-event-spec.md',
             'specs/grc-v4-representation-transport-spec.md', p.INV + 'drafts/2026-09-GRC-V4.md'}
    return {**runtime_bindings(), **{n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}}


def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {n: contract_provenance(context, n) for n in CONTRACTS}


def predecessor():
    from verify_p974_acceptance import check
    value = check()
    p.require(value['user_accepted'] and value['aggregate_closed'], 'P9-7.4 is not accepted')
    return {n: value[n] for n in ('record_digest', 'acceptance_sha256')}


def roster():
    from test_p975_failure_sequences import FailureSequenceTests
    return ['test_p975_failure_sequences.FailureSequenceTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(FailureSequenceTests)]


def check():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_failure_sequence_execution_v1'
              and value['iteration_id'] == 'P9-7.5'
              and value['record_digest'] == p.digest_record(value), 'failure-sequence evidence drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'failure-sequence source drift')
    p.require(value['authority'] == authority() and value['predecessor'] == predecessor(),
              'failure-sequence authority or predecessor drift')
    p.require(value['test_ids'] == roster()
              and value['results'] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]),
              'failure-sequence execution incomplete')
    p.require(value['user_accepted'] is False and value['aggregate_closed'] is False
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'failure-sequence overclaim')
    cases = value['cases']
    p.require(set(cases) == {'reset_sequence', 'invalid_events', 'invalid_representations', 'mixed_readmission'},
              'failure-sequence case drift')
    p.require([r['operation'] for r in cases['reset_sequence']['operations']] == ['ordinary', 'migration', 'event']
              and [r['mutation'] for r in cases['reset_sequence']['missing_archives']] ==
              ['all_crossings', 'migration_crossing', 'event_crossing', 'source_reset_preimage', 'missing_receipt_member'],
              'reset/archive scope drift')
    p.require([r['case'] for r in cases['invalid_events']['rejections']] ==
              ['stale_state', 'source_order', 'target_order', 'charge_column', 'negative_output',
               'candidate_digest', 'carrier_digest', 'invented_preservation', 'missing_history', 'unregistered_target']
              and [r['case'] for r in cases['invalid_representations']['rejections']] ==
              ['missing_correspondence', 'missing_edge', 'wrong_orientation', 'duplicate_target']
              and [r['operation'] for r in cases['mixed_readmission']['rejections']] == ['migration', 'event'],
              'failure declaration roster drift')
    return dict(status='verified_pending_review', record_path=RECORD, record_digest=value['record_digest'],
                test_count=len(roster()), rejection_cases=21, reset_contexts=['ordinary', 'migration', 'event'],
                user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
                numerical_tests_rerun=0)


def run():
    from test_p975_failure_sequences import EVIDENCE
    sources, traces, prior, ids = bindings(), authority(), predecessor(), roster()
    EVIDENCE.clear()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'failure-sequence tests failed')
    p.require(sources == bindings(), 'sources changed during failure-sequence execution')
    value = dict(schema='phase9_failure_sequence_execution_v1', iteration_id='P9-7.5',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=sources,
        authority=traces, predecessor=prior, test_ids=ids,
        results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE,
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n)
                         for n in ('numpy', 'jsonschema', 'rfc8785')}),
        user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
        scope='Bounded mixed-prefix reset, missing crossing evidence, invalid map/history and readmission negatives. Not parent-DAG conformance, all profiles, graphs or parameters.')
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), indent=2))
