"""Bounded integrated C_CI_PC G2 proposal; no acceptance or registry mutation.

Default checks the retained proposal. --emit reconstructs the review, without
numerical reruns. --capture-interface emits one fresh zero-duration facade check.
"""

import argparse
from datetime import datetime, timezone
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_c_ci_pc_local as local
import verify_p977_c_ci_pc_crossings as crossing
import verify_p977_c_ci_pc_acceptance as acceptance

SCRIPT = p.HERE + 'verify_p977_c_ci_pc_g2.py'
TEST = p.HERE + 'test_p977_c_ci_pc_g2.py'
INTERFACE = p.PHASE + 'tranche-7/P9-7.7-C_CI_PC-G2Interface.json'
RECORD = p.PHASE + 'tranche-7/P9-7.7-C_CI_PC-G2Review.json'
NOMINATED = crossing.NOMINATED
INTERFACE_TEST = 'test_p977_c_ci_pc_g2.InterfaceTests.test_exact_profile_configuration_strict_run_and_missing_defaults'
OBLIGATIONS = ('G2-EXACT-PRODUCT', 'G2-ORDERED-ENDPOINTS', 'G2-INTEGRATED-REVIEW')


def interface_bindings():
    return {**crossing.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in (SCRIPT, TEST)}}


def validate_interface(value):
    p.require(value['schema'] == 'phase9_c_ci_pc_g2_interface_execution_v1'
              and value['record_digest'] == p.digest_record(value)
              and p.g2_bindings_match(value['source_bindings'], interface_bindings()), 'interface execution/source drift')
    p.require(value['test_ids'] == [INTERFACE_TEST]
              and value['results'] == dict(tests_run=1, failures=[], errors=[], skips=[])
              and value['G2_accepted'] is False, 'interface execution incomplete or promoted')
    e = value['evidence']
    before, after = e['initial_snapshot'], e['after_stream']
    p.require(before['reference']['profile'] == review.read(local.RECORD)['nomination']
              and before['scientific_state'] == after['scientific_state'], 'interface used different scientific subject')
    p.require(e['before_stream']['scientific_state']==before['scientific_state']
              and before['reset']==e['before_stream']['reset']==after['reset']
              and before['scientific_state']['authoritative']==e['source_config']['initial']['current']
              and before['reset']['authoritative']==e['source_config']['initial']['reset']
              and before['scientific_state']['authoritative']['Z_4']!=before['reset']['authoritative']['Z_4'],
              'facade carrier/current/reset authority drift')
    p.require(set(e['source_config'])=={'initial'}
              and before['scientific_state']['authoritative']['W_A'] is None
              and before['reset']['authoritative']['W_A'] is None, 'C facade acquired A-history/backend authority')
    p.require(e['strict_result']['committed'] is True and e['strict_result']['solver_disposition'] == 'valid_root'
              and e['strict_request']['dt'] == e['stream_request']['dt'] == 0, 'not the declared zero-duration probe')
    p.require(e['before_stream']['receipt_ledger'] == before['receipt_ledger'] + e['strict_result']['emitted_receipts']
              and after['receipt_ledger'][:-4] == e['before_stream']['receipt_ledger']
              and after['commit_records'][:-1] == e['before_stream']['commit_records'], 'partial iterator execution lost')
    expected = {'configuration_detached', 'immutable_parameters', 'unchanged_assignment', 'local_discovery_not_G2',
        'missing_default_rejected', 'invalid_run_inputs_rejected', 'wrong_request_layer_rejected',
        'extraneous_config_rejected', 'candidate_c_without_A_backend', 'strict_external_results_equal',
        'interrupted_iterator_keeps_prior_commit', 'carrier_configuration_detached', 'carrier_reset_preserved'}
    p.require(set(e['checks']) == expected and all(v is True for v in e['checks'].values()), 'missing facade assertion')
    p.require(e['operation_scope']=='zero_duration_interface_only; positive numerical step/replay remains in local product',
              'interface probe promoted to numerical campaign')


def capture_interface():
    from test_p977_c_ci_pc_g2 import InterfaceTests
    sources = interface_bindings()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(INTERFACE_TEST))
    p.require(result.wasSuccessful() and not result.skipped and interface_bindings() == sources, 'interface capture failed or source changed')
    value = dict(schema='phase9_c_ci_pc_g2_interface_execution_v1', captured_at=datetime.now(timezone.utc).isoformat(),
        source_bindings=sources, test_ids=[INTERFACE_TEST], results=dict(tests_run=1, failures=[], errors=[], skips=[]),
        evidence=InterfaceTests.evidence, python_version=platform.python_version(), G2_accepted=False)
    value['record_digest'] = p.digest_record(value)
    validate_interface(value)
    return value


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    contracts = ('D10.2-EC-PARENT-REAL-CI-PC', 'D10.2-EC-CI-PC-C-COMPOSITION', 'D10.2-EC-CI-C-CONTRACTION', 'D10.2-EC-CI-PC-ABLATIONS', 'D10.2-EC-PC-ZOH-WRITER', 'D10.2-EC-PC-RELEASE', 'D10.2-EC-PC-MATCHED-FORCING', 'P9-EC-A-INITIALIZER-REFERENCE-PASS', 'P9-EC-RECEIPT-PARENT-CHAIN',
        'P9-EC-RECEIPT-PARENT-ADMISSION', 'P9-EC-RECEIPT-PARENT-CEILING',
        'P9-EC-ABUNDANCE-INTERFACE', 'P9-EC-ABUNDANCE-OBSERVATION', 'P9-EC-ABUNDANCE-FAILURE-AND-CEILING',
        'D11-C-EC-C-TR-REFERENCE-FIELD', 'D11-C-EC-C-M4-FACTORIZATION', 'D11-C-EC-C-J0-CURRENT',
        'D11-C-EC-C-J0-DERIVATIVE', 'D11-C-EC-C-J0-COVARIANCE',
        'D10.2-EC-PARENT-L-ATOMICITY', 'D10.2-EC-PARENT-L-SNAPSHOT-RESET', 'D10.2-EC-PARENT-L-ORDERED-RECEIPTS')
    return dict(contracts={k: contract_provenance(context, k) for k in contracts},
        debts={k: debt_lifecycle(context, k) for k in ('P9-7.2a-DEBT-A-INITIALIZER-SOURCE',
                                                     'P9-4.9.2-DEBT-PARENTS', 'P9-4.9.1a-DEBT-ABUNDANCE', 'D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY')})


def build(bounded_acceptance=None):
    from profile_g2_registry import support_before, registry
    from pygrc.models.grc_v4_codec import RELEASE_ID, INITIALIZER_RELEASE_ID
    from pygrc.models.grc_v4_event_codec import EVENT_RELEASE_ID
    bounded = acceptance.check() if bounded_acceptance is None else bounded_acceptance
    p.require(bounded['user_accepted'] is True and bounded['record_digest'] == acceptance.EXECUTION_DIGEST
              and bounded['acceptance_sha256'] == acceptance.ACCEPTANCE_SHA256, 'bounded reconciliation not accepted')
    a, b, interface = [review.read(n) for n in (local.RECORD, crossing.RECORD, INTERFACE)]
    local.validate(a); crossing.validate(b); validate_interface(interface)
    product = []
    for case in sorted(review.required_cases('C_CI_PC')):
        matches = [(i, r) for i, r in enumerate(a['fixture_results']) if r['fixture_id'] == case]
        if matches:
            p.require(len(matches) == 1, 'duplicate local case')
            i, row = matches[0]
            product.append(dict(fixture_id=case, evidence=review.ref(local.RECORD, '/fixture_results/' + str(i)),
                source_complete_profile_id=row['complete_profile_id'], target_complete_profile_id=row['target_active_model_identity'],
                scope=row['evidence_layer'], disposition='satisfied_for_nomination_or_exact_declared_control'))
        else:
            product.append(dict(fixture_id=case, evidence=review.ref(crossing.RECORD, '/catalog_cells/' + case),
                linked_executions=b['catalog_cells'][case], scope='explicit_ordered_endpoint_dispositions_not_all_pairs',
                disposition='satisfied_for_declared_crossing_scope'))
    initializer_row=next(r for r in b['fixture_results'] if r['fixture_id']=='initializer_outgoing')
    initializer_target=b['objects'][initializer_row['observation']['target_reference_object']]['profile']['complete_profile_id']
    event_row = next(r for r in b['fixture_results'] if r['fixture_id']=='mapped_event')
    event_target = b['objects'][event_row['observation']['target_reference_object']]['profile']['complete_profile_id']
    p.require(initializer_row['complete_profile_id']==NOMINATED and event_target!=initializer_target
              and event_target!=NOMINATED and initializer_target!=NOMINATED,'separate crossing endpoints collapsed')
    p.git(p.ROOT,'merge-base','--is-ancestor','6ab241f','HEAD')
    for path in (local.RECORD,crossing.RECORD,acceptance.REVIEW):
        p.require(p.git(p.ROOT,'show','6ab241f:'+path)==(p.ROOT/path).read_bytes(),'bounded checkpoint changed')
    roster = registry(p.ROOT)['records']
    prior = support_before(p.ROOT,NOMINATED) if any(r['complete_profile_id']==NOMINATED for r in roster) else sorted(r['complete_profile_id'] for r in roster if r['state']=='accepted')
    sources = interface_bindings()
    sources.update({n: p.sha((p.ROOT/n).read_bytes()) for n in (INTERFACE, crossing.RECORD,
        acceptance.REVIEW, p.HERE+'verify_p977_c_ci_pc_acceptance.py', 'specs/grc-common-interface.md',
        'specs/grc-v4-a-initializer-spec.md', 'specs/grc-v4-topology-event-spec.md')})
    value = dict(schema='phase9_c_ci_pc_integrated_g2_review_v1', gate='P9-G2[C_CI_PC]', verdict='PASS_PROPOSAL',
        user_accepted=False, G2_accepted=False, G3_accepted=False, aggregate_closed=False, new_G2_support=[],
        source_bindings=sources, nomination=a['nomination'], proposed_additional_support=[NOMINATED],
        accepted_support_unchanged=prior, releases=dict(base=RELEASE_ID, initializer=INITIALIZER_RELEASE_ID, event=EVENT_RELEASE_ID),
        bounded_acceptance=dict(commit='6ab241f',path=acceptance.REVIEW, sha256=acceptance.ACCEPTANCE_SHA256, execution_digest=b['record_digest']),
        evidence_digests={local.RECORD:a['record_digest'], crossing.RECORD:b['record_digest'], INTERFACE:interface['record_digest']},
        catalog_product=product, interface_evidence=review.ref(INTERFACE, '/evidence'),
        ordered_scope=dict(matrix=b['ordered_migration_matrix'], C_to_A='exact_nomination_source_to_selected_initializer_target',
            C_to_A_candidate_history_loss=False, C_to_A_carrier_history_loss=True,
            event_target=event_target, event_target_is_proposed_support=False,
            initializer_target=initializer_target, initializer_target_is_proposed_support=False,
            all_ordered_pairs_verified=False, endpoint_support_does_not_prove_crossing_support=True,
            exact_PC_pairs_preserve_carrier_only_under_exact_carrier_contract=True,
            changed_carrier_contract_rejected_without_silent_reset=True,
            nonhistory_pair_is_separate_not_nomination_execution=True,
            initializer_event_target_is_not_proposed_support=True,
            event_policy='C_rederived_without_candidate_loss_and_whole_carrier_reset_not_native_release',
            CI_PC_scope='old_C_Z_joint_root_same_selected_source_for_immediate_geometry_and_one_ZOH_then_both_role_readmission',
            same_selected_root_source_drives_geometry_and_ZOH=True,
            trial_history_frozen=True, separate_post_continuity_W_writer=False,
            gain_two_is_constant_source_law_identity_not_settled_trajectory=True,
            global_root_uniqueness_claimed=False,
            unit_plus_unit_gain_is_not_amplitude_equivalence=True,
            zero_event_carrier_does_not_erase_immediate_geometry=True,
            A_to_C='exact_A_CI_PC_source_to_C_nomination_with_candidate_and_carrier_loss',
            A_to_C_candidate_history_loss=True, A_to_C_carrier_history_loss=True,
            native_release='zero_source_exponential_decay_not_reset_or_drop',
            matched_forcing_contraction_claimed=False, indefinite_base_chart_invariance_claimed=False,
            C_has_no_W_state_or_A_writer=True,
            full_C_baseline_rederived_at_each_role=True,
            reference_field_is_complete_target_edge_map=True,
            baseline_mobility_authority_is_not_structural_Hodge=True,
            zero_nominal_kappa_M_does_not_remove_baseline_geometry_dependence=True,
            dense_derivative_control_is_not_nomination_trajectory=True,
            zero_controls_are_separate_profiles=True,
            unreviewed_pairs='no new pair capability follows from accepting a profile; all other pairs remain unreviewed',
            event_evidence=review.ref(crossing.RECORD, '/catalog_cells/WHOLE-LIFECYCLE-TUPLE-MAP')),
        obligations={k:'satisfied_for_exact_declared_scope' for k in OBLIGATIONS}, authority=authority(),
        numerical_tests_rerun=0, reused_local_methods=5, reused_crossing_methods=4,
        supplemental_interface_methods=1,
        decision_required='Accept or return this exact G2 proposal; discovery/support and parent P9-7.7 remain unchanged until a separate decision.')
    value['record_digest'] = p.digest_record(value)
    return value


def validate(value, expected):
    p.require(value['record_digest'] == p.digest_record(value) and value == expected, 'integrated proposal differs from reviewed evidence')
    p.require([r['fixture_id'] for r in value['catalog_product']] == sorted(review.required_cases('C_CI_PC')),
              'incomplete or duplicated exact product')
    p.require(value['proposed_additional_support'] == [NOMINATED]
              and NOMINATED not in value['accepted_support_unchanged']
              and value['nomination']['complete_profile_id'] == NOMINATED
              and set(value['obligations']) == set(OBLIGATIONS), 'invalid proposal scope')
    for row in value['catalog_product']:
        p.require(review.resolve(row['evidence']) is not None, 'unresolved catalog evidence')


def check(bounded_acceptance=None):
    value = review.read(RECORD)
    validate(value, build(bounded_acceptance))
    return dict(status='pass_proposal_pending_G2_acceptance', record_path=RECORD, record_digest=value['record_digest'],
        gate=value['gate'], proposed_additional_support=value['proposed_additional_support'], catalog_cells=33,
        obligations=value['obligations'], accepted_support_unchanged=value['accepted_support_unchanged'],
        user_accepted=False, G2_accepted=False, G3_accepted=False, aggregate_closed=False, new_G2_support=[],
        all_ordered_pairs_verified=False, numerical_tests_rerun=0, supplemental_interface_methods=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--emit', action='store_true')
    mode.add_argument('--capture-interface', action='store_true')
    args = parser.parse_args()
    print(json.dumps(capture_interface() if args.capture_interface else build() if args.emit else check(), indent=2))
