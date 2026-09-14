"""Retained exact A_CI local product; --run emits a new run without writing."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
from verify_p972b_runtime import bindings as runtime_bindings

SCRIPT=p.HERE+'verify_p977_a_ci_local.py'
TEST=p.HERE+'test_p977_a_ci_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-A_CI-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_a_cases']
                  if r['id']!='A-MIGRATION-HISTORY-RECEIPT']+['CI-BRANCH']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.1ab-AuditFollowup.json',
           p.PHASE+'tranche-6/P9-6.1c-ExecutionRecord.json',
           p.HERE+'test_p977_a_os_local.py'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_a_ci_local import ACILocalProductTests
    return ['test_p977_a_ci_local.ACILocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(ACILocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-CI-A-ROOT', 'D10.2-EC-CI-A-CONTRACTION', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_a_ci_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-A_CI-local'
              and value['record_digest']==p.digest_record(value),'A_CI local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'A_CI local execution source drift')
    p.require(value['authority'] == authority(), 'A_CI authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_CI']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'A_CI nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=3,failures=[],errors=[],skips=[]),
              'A_CI local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'A_CI evidence object changed')
    fields=set(review.read(review.CATALOG)['execution_contract']['required_result_fields'])
    commons={r['id']:r for r in review.read(review.CATALOG)['common_cases']}
    for row in rows:
        p.require(fields<=set(row) and row['nominated_complete_profile_id']==NOMINATED,'missing result fields or nomination')
        before,after=[objects[row[k]] for k in ('prestate_object','poststate_object')]
        profile=before['reference']['profile']
        resolved=resolve_profile(profile['params_resolved'],profile['identity_payload'])
        p.require(row['complete_profile_id']==row['active_model_identity']==resolved.complete_profile_id
                  ==before['scientific_state']['active_model_identity']
                  and row['resolved_params_id']==profile['identity_payload']['params_hash'],'borrowed profile result')
        if row['fixture_id'] in ('A-CHI-ZERO','A-ZETA-ZERO'):
            field='chi_A' if row['fixture_id']=='A-CHI-ZERO' else 'zeta_A'
            expected=deepcopy(nomination['params_resolved']); expected['candidate'][field]=0
            p.require(canonical_json_bytes(profile['params_resolved'])==canonical_json_bytes(expected)
                      and resolved.complete_profile_id!=NOMINATED,'invalid control relationship')
            p.require(row['observation']['current']==row['observation']['baseline'],'zero control lost baseline')
        else:
            p.require(resolved.complete_profile_id==NOMINATED,'unlisted control profile')
        p.require(row['prestate_digest']==before['scientific_state_digest']
                  and row['poststate_digest']==after['scientific_state_digest']
                  and row['target_active_model_identity']==after['scientific_state']['active_model_identity'],
                  'result endpoint mismatch')
        old=[r['receipt_id'] for r in before['receipt_ledger']]
        new=[r['receipt_id'] for r in after['receipt_ledger']]
        if row['committed']:
            p.require(row['operation_disposition']=='committed' and row['emitted_receipt_ids']
                      and new==old+row['emitted_receipt_ids'],'receipt delta mismatch')
        else:
            p.require(before==after,'uncommitted operation changed publication')
        if row['fixture_id'] in commons:
            contract=commons[row['fixture_id']]
            for name in ('operation_disposition','solver_disposition','committed','failure_code'):
                key='required_'+name
                if key in contract: p.require(row[name]==contract[key],'common disposition mismatch: '+row['fixture_id'])
            if row['fixture_id']=='COMMON-STALE-CACHE':
                p.require(row['observation']['postcondition']=='cache_rebuilt_before_consumer'
                          and row['observation']['stale_value_never_consumed'] is True,'stale cache not covered')
        if row['operation_disposition']=='not_invoked':
            p.require(row['evidence_layer']=='independent_equations_and_provisional_stage_not_public_commit'
                      and row['result_object'] is None and row['solver_disposition'] is None,
                      'provisional stage relabeled as committed execution')
        for name in ('request_object','result_object'):
            p.require(row[name] is None or row[name] in objects,'missing operation preimage')
    from fractions import Fraction
    import numpy as np
    branch = next(r for r in rows if r['fixture_id'] == 'CI-BRANCH')['observation']
    cert = branch['certificate']
    p.require(cert['scope'] == 'analytic_local_reference_ball'
              and branch['branch_scope'] == 'analytic_local_reference_ball_not_global_uniqueness'
              and Fraction(cert['contraction_upper']) < 1
              and Fraction(cert['displacement_upper']) <= Fraction(cert['radius']), 'CI branch not certified')
    params = nomination['params_resolved']['realization']
    p.require(Fraction(branch['residual_squared']) <= Fraction(params['tolerance'])**2
              and 1 <= branch['root_evaluations'] <= params['iteration_limit']
              and branch['writer_count'] == branch['continuity_evaluations'] == 1
              and branch['current_stage_roster'] == ['ci_trial']
              and branch['stale_writer_trial_rejected'] is True
              and branch['supplied_W_is_not_formation'] is True, 'CI stage/branch boundary changed')
    for key in ('current','hodge','final_C','writer_descriptors','W_drv','written_W'):
        p.require(np.allclose(branch['observed'][key], branch['independent_oracle'][key], rtol=0,
                             atol=2e-11 if key in ('current','hodge') else 2e-13), 'CI independent oracle mismatch: '+key)
    selected = objects[branch['selected_inputs_object']]
    p.require(selected['reference']['profile'] == nomination,
              'CI selected trial has a different profile')
    budget = branch['budget_control']
    limited = objects[budget['inputs_object']]['reference']['profile']
    p.require(budget['disposition'] == 'no_admitted_root' and budget['fallback_used'] is False
              and budget['scope'] == 'root_construction_rejection_not_public_operation'
              and limited['complete_profile_id'] != NOMINATED
              and limited['params_resolved']['realization']['iteration_limit'] == 1
              and limited['params_resolved']['realization']['tolerance'] == 0, 'CI budget control relabeled')
    for row in branch['trial_points']:
        inputs = objects[row['inputs_object']]
        p.require(inputs['current'] == seed['initial']['current'] and inputs['stage'] == 'ci_trial',
                  'CI trial borrowed new history or another prestate')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=3,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('A_CI'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_ci_local import ACILocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'A_CI local product tests failed')
    p.require(bindings()==sources,'sources changed during A_CI capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_CI']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-A_CI-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=ACILocalProductTests.rows,objects=ACILocalProductTests.objects,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='21 local A_CI catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
