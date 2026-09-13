"""Retained exact A_OS local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_a_os_local.py'
TEST=p.HERE+'test_p977_a_os_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-A_OS-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_a_cases']
                  if r['id']!='A-MIGRATION-HISTORY-RECEIPT']+['OS-ONE-PASS']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-5/P9-5.3-AuditFollowup.json'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_a_os_local import AOSLocalProductTests
    return ['test_p977_a_os_local.AOSLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(AOSLocalProductTests)]


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_a_os_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-A_OS-local'
              and value['record_digest']==p.digest_record(value),'A_OS local record drift')
    p.require(value['source_bindings']==bindings(),'A_OS local execution source drift')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_OS']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'A_OS nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=3,failures=[],errors=[],skips=[]),
              'A_OS local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'A_OS evidence object changed')
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


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=3,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('A_OS'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_os_local import AOSLocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'A_OS local product tests failed')
    p.require(bindings()==sources,'sources changed during A_OS capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_OS']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-A_OS-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=AOSLocalProductTests.rows,objects=AOSLocalProductTests.objects,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='21 local A_OS catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
