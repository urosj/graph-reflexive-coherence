"""Bounded channel/charge verification; --run emits a new run, never writes."""

import argparse
from datetime import datetime, timezone
import json
import platform
import importlib.metadata
import sys
import unittest

import phase9_implementation_policy as p
from verify_p972b_runtime import bindings as runtime_bindings

SCRIPT = p.HERE + 'verify_p973_history_policy.py'
TEST = p.HERE + 'test_p973_history_policy.py'
RECORD = p.PHASE + 'tranche-7/P9-7.3-HistoryPolicy.json'
CONTRACTS = ['D10.2-EC-EVENT-A-HISTORY', 'D10.2-EC-EVENT-K4-HISTORY',
             'D10.2-EC-EVENT-LIFECYCLE-TUPLE', 'D10.2-EC-EVENT-RESOURCE',
             'D10.2-EC-EVENT-READMISSION-RECEIPT', 'P9-EC-A-INITIALIZER-REFERENCE-PASS']


def bindings():
    names = {SCRIPT, TEST, 'specs/grc-v4-spec.md', 'specs/grc-v4-topology-event-spec.md',
             'specs/grc-v4-representation-transport-spec.md',
             p.INV + 'drafts/2026-09-GRC-V4.md',
             p.PHASE + 'tranche-7/P9-7.2a-InitializerRuntimeReview.md',
             p.PHASE + 'tranche-7/P9-7.2b-RuntimeReview.md'}
    return {**runtime_bindings(), **{n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}}


def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {n: contract_provenance(context, n) for n in CONTRACTS}


def predecessors():
    from verify_p972a_initializer_runtime import check as migration
    from verify_p972b_acceptance import check as events
    values = {'P9-7.2a': migration(), 'P9-7.2b': events()}
    p.require(all(v['user_accepted'] and v['aggregate_closed'] for v in values.values()),
              'P9-7.3 requires accepted migration and event scopes')
    return {k: {n: v[n] for n in ('record_digest', 'acceptance_sha256')} for k, v in values.items()}


def roster():
    from test_p973_history_policy import HistoryPolicyTests
    return ['test_p973_history_policy.HistoryPolicyTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(HistoryPolicyTests)]


def check():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_history_policy_execution_v1'
              and value['iteration_id'] == 'P9-7.3'
              and value['record_digest'] == p.digest_record(value), 'history-policy evidence drift')
    p.require(value['source_bindings'] == bindings(), 'history-policy source drift')
    p.require(value['authority'] == authority() and value['predecessors'] == predecessors(),
              'history-policy authority or predecessor drift')
    p.require(value['test_ids'] == roster() and value['results'] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]),
              'history-policy execution incomplete')
    p.require(value['user_accepted'] is False and value['aggregate_closed'] is False
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'history-policy overclaim')
    cases = value['cases']
    p.require(set(cases) == {'policy_matrix', 'native_crossings', 'representation', 'rejected_channel_mutations',
                            'affine_charge', 'charge_rejections'}
              and len(cases['policy_matrix']) == 32 and len(cases['native_crossings']) == 5
              and cases['rejected_channel_mutations'] == 16 and len(cases['affine_charge']) == 2
              and cases['charge_rejections'] == ['reset_only_target_charge', 'exact_subnormal_column_excess'],
              'history-policy coverage drift')
    return dict(status='verified_pending_review', record_path=RECORD, record_digest=value['record_digest'],
                test_count=len(roster()), policy_cells=32, native_crossings=5,
                user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False)


def run():
    from test_p973_history_policy import EVIDENCE
    source, traces, prior, ids = bindings(), authority(), predecessors(), roster()
    EVIDENCE.clear()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'history-policy tests failed')
    p.require(source == bindings(), 'history-policy sources changed during execution')
    value = dict(schema='phase9_history_policy_execution_v1', iteration_id='P9-7.3',
                 captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=source,
                 authority=traces, predecessors=prior, test_ids=ids,
                 results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE,
                 environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n) for n in ('numpy', 'jsonschema', 'rfc8785')}),
                 user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
                 scope='Discrete policy tables plus bounded native witnesses; not all-graph/profile-pair admission or new transport authority.')
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), indent=2))
