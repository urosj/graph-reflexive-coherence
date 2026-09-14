"""Exact A_CI crossing reconciliation. --run emits a fresh record to stdout."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_a_ci_local as local

SCRIPT = p.HERE + 'verify_p977_a_ci_crossings.py'
TEST = p.HERE + 'test_p977_a_ci_crossings.py'
RECORD = p.PHASE + 'tranche-7/P9-7.7-A_CI-Crossings.json'
NOMINATED = 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'
CASES = ['A_to_C', 'incoming_C_rejection', 'mapped_event', 'persistent_A_PC',
         'readmission_control', 'readmission_rejection']


def bindings():
    return {**local.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in
        (SCRIPT, TEST, local.RECORD, review.SOURCES['migration'], review.SOURCES['initializer'])}}


def roster():
    from test_p977_a_ci_crossings import ACICrossingTests
    return ['test_p977_a_ci_crossings.ACICrossingTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(ACICrossingTests)]


def authority():
    traces = local.authority()
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    key = 'P9-EC-A-INITIALIZER-REFERENCE-PASS'
    traces[key] = contract_provenance(context, key)
    return traces


def retained():
    """Project only fields actually present in the old receipt/endpoints."""
    aliases = []
    for origin, key in [('migration', k) for k in ('A_NH_NH', 'A_NH_PC', 'A_PC_CIPC', 'A_CIPC_PC')] + [('initializer', 'A_CI')]:
        source = review.SOURCES[origin]
        run = review.read(source)
        p.require(run['record_digest'] == p.digest_record(run), 'retained crossing run drift')
        row = run['cases'][key]
        before, after = row['before'], row['after']
        receipt = row['receipts'][0]['identity_payload']
        core = receipt['core']
        profile = row['initial']['reference']['profile']
        p.require(core['disposition'] == 'committed'
                  and core['source_state_digest'] == before['scientific_state_digest']
                  and core['target_state_digest'] == after['scientific_state_digest']
                  and core['source_model_identity'] == profile['complete_profile_id']
                  and core['target_model_identity'] == row['target_reference']['profile']['complete_profile_id'],
                  'retained ordered endpoint mismatch')
        ids = [r['receipt_id'] for r in row['receipts']]
        p.require(after['receipt_ids'] == before['receipt_ids'] + ids, 'retained delta mismatch')
        p.require(row['reset']['scientific_state']['authoritative'] == after['reset']['authoritative'],
                  'retained reset mismatch')
        aliases.append(dict(key=origin + '/' + key, evidence=review.ref(source, '/cases/' + key),
            original_record_digest=run['record_digest'],
            complete_profile_id=profile['complete_profile_id'], active_model_identity=core['source_model_identity'],
            resolved_params_id=profile['identity_payload']['params_hash'],
            target_active_model_identity=core['target_model_identity'],
            prestate_digest=core['source_state_digest'], poststate_digest=core['target_state_digest'],
            operation_disposition=core['disposition'], committed=True, emitted_receipt_ids=ids,
            solver_disposition=None, solver_evidence='not_recorded_in_retained_migration_receipt; no solver outcome inferred',
            history=receipt['history'], information_losses=core['information_losses'],
            evidence_scope='exact_nomination_source' if core['source_model_identity'] == NOMINATED else
                'exact_nomination_target' if core['target_model_identity'] == NOMINATED else
                'separate_ordered_endpoints_not_nomination_execution'))
    return aliases


def matrix():
    return [
        dict(migration_class='same_candidate_nonhistory_to_nonhistory', disposition='positive_exact_nomination_target', evidence='migration/A_NH_NH'),
        dict(migration_class='same_candidate_nonhistory_to_history', disposition='positive_exact_nomination_source', evidence='migration/A_NH_PC'),
        dict(migration_class='same_candidate_history_to_nonhistory', disposition='positive_exact_nomination_target', evidence='persistent_A_PC'),
        dict(migration_class='PC_to_CI_PC', disposition='separate_endpoints_not_A_CI; no positive nomination credit', evidence='migration/A_PC_CIPC'),
        dict(migration_class='CI_PC_to_PC', disposition='separate_endpoints_not_A_CI; no positive nomination credit', evidence='migration/A_CIPC_PC'),
        dict(migration_class='A_to_C', disposition='positive_exact_nomination_source', evidence='A_to_C'),
        dict(migration_class='C_to_A', disposition='negative_exact_nomination_target; positive initializer target remains a different profile',
             evidence='incoming_C_rejection', separate_positive='initializer/A_CI'),
    ]


def cells():
    return {
        'A-MIGRATION-HISTORY-RECEIPT': ['migration/A_NH_NH', 'A_to_C', 'migration/A_NH_PC', 'persistent_A_PC'],
        'RESET-AFTER-MIGRATION': ['migration/A_NH_NH', 'A_to_C', 'migration/A_NH_PC', 'persistent_A_PC'],
        'RESET-AFTER-EVENT': ['mapped_event'],
        'WHOLE-LIFECYCLE-TUPLE-MAP': ['mapped_event'],
        'ALL-MIGRATION-CLASSES': ['ordered_migration_matrix'],
        'HISTORY-DISPOSITION': ['A_to_C', 'migration/A_NH_PC', 'persistent_A_PC', 'mapped_event'],
        'TARGET-READMISSION-FAILURE': ['readmission_control', 'readmission_rejection'],
    }


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    p.require(value['schema'] == 'phase9_exact_profile_crossing_reconciliation_v1'
              and value['iteration_id'] == 'P9-7.7-A_CI-crossings'
              and value['record_digest'] == p.digest_record(value), 'crossing record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'crossing source drift')
    p.require(value['authority'] == authority(), 'crossing authority drift or promotion')
    p.require(value['nomination'] == review.read(local.RECORD)['nomination']
              and value['local_record_digest'] == review.read(local.RECORD)['record_digest'], 'nomination/local record drift')
    p.require(value['results'] == dict(tests_run=3, failures=[], errors=[], skips=[])
              and value['test_ids'] == roster(), 'crossing execution incomplete')
    for name in ('user_accepted', 'aggregate_closed', 'G2_accepted', 'G3_accepted', 'all_ordered_pairs_verified'):
        p.require(value[name] is False, 'crossing scope or acceptance promoted')
    p.require(value['new_G2_support'] == [] and value['retained_aliases'] == retained()
              and value['ordered_migration_matrix'] == matrix() and value['catalog_cells'] == cells(), 'crossing reconciliation changed')
    p.require(set(cells()) == set(review.required_cases('A_CI')) - set(local.required()), 'crossing catalog drift')
    rows, objects = value['fixture_results'], value['objects']
    p.require(sorted(r['fixture_id'] for r in rows) == CASES, 'missing/duplicate crossing row')
    for key, obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj)) == key, 'crossing preimage drift')
    required = set(review.read(review.CATALOG)['execution_contract']['required_result_fields'])
    for row in rows:
        p.require(required <= set(row) and row['nominated_complete_profile_id'] == NOMINATED, 'missing result/nomination fields')
        before, after = [objects[row[k]] for k in ('prestate_object', 'poststate_object')]
        profile = before['reference']['profile']
        request, result = [objects[row[k]] for k in ('request_object', 'result_object')]
        p.require(row['complete_profile_id'] == row['active_model_identity'] == profile['complete_profile_id']
                  == before['scientific_state']['active_model_identity']
                  and row['resolved_params_id'] == profile['identity_payload']['params_hash'], 'borrowed source identity')
        p.require(row['prestate_digest'] == before['scientific_state_digest'] == request['source_state_digest']
                  and row['poststate_digest'] == after['scientific_state_digest']
                  and row['target_active_model_identity'] == after['scientific_state']['active_model_identity'], 'incorrect operation endpoints')
        for name in ('committed', 'operation_disposition', 'solver_disposition'):
            p.require(row[name] == result.get(name), 'result disposition differs from preimage')
        p.require(row['emitted_receipt_ids'] == [r['receipt_id'] for r in result['emitted_receipts']], 'result receipt delta drift')
        obs = row['observation']
        if row['committed']:
            p.require(request['target_profile_id'] == row['target_active_model_identity'], 'target identity substituted')
            p.require(after['receipt_ledger'] == before['receipt_ledger'] + result['emitted_receipts'], 'persistent ledger is not emitted delta')
        else:
            p.require(before == after and result['commit_id'] is None and len(result['emitted_receipts']) == 1
                      and result['failure']['stage'] == obs['failure_stage'], 'failed crossing changed publication')
        case = row['fixture_id']
        p.require(row['committed'] == (case not in ('incoming_C_rejection', 'readmission_rejection')),
                  'positive/negative crossing relabeled')
        if case in ('A_to_C', 'persistent_A_PC', 'mapped_event'):
            history = result['emitted_receipts'][0]['identity_payload']['history']
            for subject in ('candidate', 'carrier'):
                p.require(history[subject]['disposition'] == obs['expected_' + subject], 'history channel mismatch')
            p.require(result['emitted_receipts'][0]['identity_payload']['core']['information_losses'] == obs['expected_losses'], 'loss mismatch')
            expected_loss = ['carrier_history_loss'] if case == 'persistent_A_PC' else ['candidate_history_loss']
            p.require(obs['expected_losses'] == expected_loss, 'required history loss erased')
            p.require(history['carrier']['disposition'] == ('explicit_loss' if case == 'persistent_A_PC' else 'not_applicable'),
                      'carrier history borrowed from another crossing')
            reset = objects[obs['after_reset_object']]
            p.require(reset['scientific_state']['authoritative'] == after['reset']['authoritative']
                      and reset['reset'] == after['reset'] and reset['reference'] == after['reference']
                      and reset['transition_records'] == after['transition_records']
                      and reset['receipt_ledger'][:-4] == after['receipt_ledger']
                      and reset['commit_records'][:-1] == after['commit_records'], 'reset/ledger authority mismatch')
            for name in ('time', 'step_index', 'Q_target'):
                p.require(reset['scientific_state'][name] == after['scientific_state'][name], 'reset clock/charge drift')
        if case in ('persistent_A_PC', 'A_to_C'):
            p.require(NOMINATED == (request['target_profile_id'] if case == 'persistent_A_PC' else row['complete_profile_id']), 'wrong migration endpoint')
            for left, right in ((before['scientific_state']['authoritative'], after['scientific_state']['authoritative']),
                                (before['reset']['authoritative'], after['reset']['authoritative'])):
                p.require(left['C'] == right['C'] and right['W_A'] == (left['W_A'] if case == 'persistent_A_PC' else None)
                          and right['Z_4'] is None, 'wrong literal migration map')
            for name in ('time', 'step_index', 'Q_target'):
                p.require(before['scientific_state'][name] == after['scientific_state'][name], 'migration clock/charge drift')
            p.require(history['candidate']['disposition'] == ('exact_transport' if case == 'persistent_A_PC' else 'explicit_loss'),
                      'candidate history borrowed from another crossing')
            if case == 'persistent_A_PC':
                old, baseline = before['scientific_state']['authoritative'], before['reset']['authoritative']
                p.require(old['Z_4'] != baseline['Z_4'] and old['Z_4'] != [0] and baseline['Z_4'] != [0],
                          'vacuous carrier-loss control')
        elif case == 'mapped_event':
            p.require(row['complete_profile_id'] == NOMINATED and request['target_profile_id'] != NOMINATED, 'initializer target conflated')
            from fractions import Fraction as F
            transform = request['resource_transform']
            p.require(transform['row_major_coefficients'] == [0, 1, 1, 0]
                      and transform['target_increment'] == [.125, 0], 'different affine event map')
            for role, actual in (('current', after['scientific_state']['authoritative']), ('reset', after['reset']['authoritative'])):
                p.require(actual == {k: obs['expectations'][role][k] for k in ('C', 'W_A', 'Z_4')}, 'event oracle mismatch')
                old = before['scientific_state']['authoritative'] if role == 'current' else before['reset']['authoritative']
                p.require(actual['C'] == [float(F(old['C'][1]) + F(1, 8)), old['C'][0]], 'independent resource map mismatch')
            p.require(after['scientific_state']['Q_target'] == obs['expected_Q_target'] and obs['missing_archive_rejected'] is True, 'whole lifecycle map missing')
            p.require(obs['expected_Q_target'] == float(F(before['scientific_state']['Q_target']) + F(1, 8)), 'charge map mismatch')
            for name in ('time', 'step_index'):
                p.require(before['scientific_state'][name] == after['scientific_state'][name], 'event changed clock')
        elif case == 'incoming_C_rejection':
            p.require(not row['committed'] and request['target_profile_id'] == NOMINATED
                      and obs['selected_initializer_profile_id'] != NOMINATED
                      and result['failure']['stage'] == 'admission'
                      and 'initializer source' in result['failure']['message'], 'incoming negative mislabeled')
        else:
            p.require(row['complete_profile_id'] == NOMINATED and row['committed'] == (case == 'readmission_control'), 'reset-only control lost')
            if case == 'readmission_rejection':
                p.require(result['failure']['stage'] == 'target_readmission', 'failure was not target readmission')
    by_id = {r['fixture_id']: r for r in rows}
    good, bad = [objects[by_id[k]['prestate_object']] for k in ('readmission_control', 'readmission_rejection')]
    p.require(good['reference'] == bad['reference'] and good['scientific_state']['authoritative'] == bad['scientific_state']['authoritative']
              and good['reset']['authoritative'] == good['scientific_state']['authoritative']
              and bad['reset']['authoritative'] != bad['scientific_state']['authoritative'], 'not a reset-only contrast')
    p.require(objects[by_id['readmission_control']['request_object']]['target_profile_id']
              == objects[by_id['readmission_rejection']['request_object']]['target_profile_id'], 'readmission targets differ')


def check(local_product=None):
    local_product = local.check() if local_product is None else local_product
    value = review.read(RECORD)
    p.require(local_product['record_digest'] == value['local_record_digest'], 'wrong local predecessor')
    validate(value)
    return dict(status='crossings_reconciled_pending_review', record_path=RECORD, record_digest=value['record_digest'],
        complete_profile_id=NOMINATED, test_count=3, new_execution_cases=6, retained_alias_count=5,
        reconciled_crossing_cells=7, local_cells=21, ordered_migration_classes=7,
        matrix_scope='exact_positive_and_negative_endpoints; separate_PC_pairs; not_all_pairs',
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        new_G2_support=[], all_ordered_pairs_verified=False, numerical_tests_rerun=0)


def run():
    from test_p977_a_ci_crossings import ACICrossingTests
    predecessor = local.check()
    before = bindings()
    ids = roster()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'crossing execution failed')
    p.require(before == bindings(), 'sources changed during crossing capture')
    value = dict(schema='phase9_exact_profile_crossing_reconciliation_v1', iteration_id='P9-7.7-A_CI-crossings',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=before,
        nomination=review.read(local.RECORD)['nomination'], local_record_digest=predecessor['record_digest'],
        test_ids=ids, results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        fixture_results=ACICrossingTests.rows, objects=ACICrossingTests.objects,
        retained_aliases=retained(), ordered_migration_matrix=matrix(), catalog_cells=cells(), authority=authority(),
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n) for n in ('numpy', 'jsonschema', 'rfc8785')}),
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        all_ordered_pairs_verified=False, new_G2_support=[])
    value['record_digest'] = p.digest_record(value)
    validate(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), separators=(',', ':')))
