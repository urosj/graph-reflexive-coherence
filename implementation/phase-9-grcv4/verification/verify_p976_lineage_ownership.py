"""Check retained P9-7.6 evidence; --run emits a new execution, never writes."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
from verify_p972b_runtime import bindings as runtime_bindings

SCRIPT = p.HERE + 'verify_p976_lineage_ownership.py'
TEST = p.HERE + 'test_p976_lineage_ownership.py'
RECORD = p.PHASE + 'tranche-7/P9-7.6-LineageOwnership.json'
CONTRACTS = ('P9-EC-RECEIPT-PARENT-CHAIN', 'P9-EC-RECEIPT-PARENT-ADMISSION',
             'P9-EC-RECEIPT-PARENT-CEILING')


def bindings():
    names = {SCRIPT, TEST, p.HERE + 'check_p9492_parent_proposal.py',
             'specs/grc-common-interface-v4-ext.md', 'specs/grc-v4-spec.md',
             'specs/grc-v4-topology-event-spec.md', 'specs/grc-v4-representation-transport-spec.md',
             p.INV + 'drafts/2026-09-GRC-V4.md', p.INV + 'decisions/P9ReceiptParentAuthority.json'}
    return {**runtime_bindings(), **{n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}}


def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {n: contract_provenance(context, n) for n in CONTRACTS}


def predecessor():
    from verify_p975_acceptance import check
    value = check()
    p.require(value['user_accepted'] and value['aggregate_closed'], 'P9-7.5 is not accepted')
    return {n: value[n] for n in ('record_digest', 'acceptance_sha256')}


def roster():
    from test_p976_lineage_ownership import LineageOwnershipTests
    return ['test_p976_lineage_ownership.LineageOwnershipTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(LineageOwnershipTests)]


def check():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_lineage_ownership_execution_v1'
              and value['iteration_id'] == 'P9-7.6'
              and value['record_digest'] == p.digest_record(value), 'lineage evidence drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'lineage source drift')
    p.require(value['authority'] == authority() and value['predecessor'] == predecessor(),
              'lineage authority or predecessor drift')
    p.require(value['test_ids'] == roster()
              and value['results'] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]),
              'lineage execution incomplete')
    p.require(value['user_accepted'] is False and value['aggregate_closed'] is False
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'lineage overclaim')
    cases = value['cases']
    p.require(set(cases) == {'native_chain', 'coherent_negatives', 'forks', 'symbolic'}, 'lineage case drift')
    p.require([r['group_size'] for r in cases['native_chain']['groups']] == [4, 4, 4, 4, 4, 1, 4],
              'native mixed-arity chain drift')
    p.require([r['mutation'] for r in cases['coherent_negatives']['restores']] ==
              ['missing', 'skipped', 'foreign', 'nonprimary', 'extra', 'reordered_extra',
               'duplicate_parent', 'intra_commit', 'auxiliary_disagrees', 'forward_acyclic']
              and [r['operation'] for r in cases['coherent_negatives']['publications']] ==
              ['migration', 'event', 'representation'], 'coherent negative roster drift')
    p.require([r['mutation'] for r in cases['coherent_negatives']['partitions']] ==
              ['duplicate_group', 'reordered_groups', 'uncovered_ledger'], 'partition scope drift')
    p.require(cases['forks']['exported_mutation_did_not_publish'] is True
              and cases['forks']['save_load_equal'] is True
              and len(cases['forks']['root_groups']) == 1
              and cases['forks']['root_groups'][0]['group_size'] == 1
              and cases['forks']['root_groups'][0]['parent'] is None, 'fork ownership evidence incomplete')
    p.require(cases['symbolic']['runtime_executions'] == 0
              and cases['symbolic']['symbolic_valid_cases'] == 9
              and len(cases['symbolic']['symbolic_mutations_rejected']) == 16,
              'symbolic controls relabeled or incomplete')
    return dict(status='verified_pending_review', record_path=RECORD, record_digest=value['record_digest'],
                test_count=len(roster()), coherent_parent_rejections=10, publication_rejections=3,
                partition_rejections=3, symbolic_rejections=16, user_accepted=False, aggregate_closed=False,
                new_G2_support=[], G3_accepted=False, numerical_tests_rerun=0)


def run():
    from test_p976_lineage_ownership import EVIDENCE
    sources, traces, prior, ids = bindings(), authority(), predecessor(), roster()
    EVIDENCE.clear()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'lineage tests failed')
    p.require(sources == bindings(), 'sources changed during lineage execution')
    value = dict(schema='phase9_lineage_ownership_execution_v1', iteration_id='P9-7.6',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=sources,
        authority=traces, predecessor=prior, test_ids=ids,
        results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE,
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n)
                         for n in ('numpy', 'jsonschema', 'rfc8785')}),
        user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
        scope='Bounded generic parent-rule and mutable fork ownership verification; symbolic cycles are not coherently hashed runtime cycles. No authenticated history, all-profile/graph claim or new G2/G3.')
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), indent=2))
