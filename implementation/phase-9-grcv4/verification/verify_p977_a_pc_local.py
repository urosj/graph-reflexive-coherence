"""Retained exact A_PC local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_a_pc_local.py'
TEST=p.HERE+'test_p977_a_pc_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-A_PC-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_a_cases']
                  if r['id']!='A-MIGRATION-HISTORY-RECEIPT']+['PC-ZOH']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.2abc-AuditFollowup.json',
           p.PHASE+'tranche-6/P9-6.2ab-ExecutionRecord.json',
           p.HERE+'test_p977_a_os_local.py'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_a_pc_local import APCLocalProductTests
    return ['test_p977_a_pc_local.APCLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(APCLocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-PARENT-REAL-PC', 'D10.2-EC-PC-ZOH-WRITER', 'D10.2-EC-PC-RELEASE', 'D10.2-EC-PC-MATCHED-FORCING', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_a_pc_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-A_PC-local'
              and value['record_digest']==p.digest_record(value),'A_PC local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'A_PC local execution source drift')
    p.require(value['authority'] == authority(), 'A_PC authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_PC']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'A_PC nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=4,failures=[],errors=[],skips=[]),
              'A_PC local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'A_PC evidence object changed')
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
    validate_science(value, seed)


def validate_science(value, seed):
    """Recompute literal equations from retained operands, never rerun the model."""
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from tests.models.test_grc_v4_candidate_a import scalar_oracle
    from tests.models.test_grc_v4_ci import independent_point
    from test_p977_a_pc_local import independent_beat, old_h
    from tests.models.test_grc_v4_pc import zoh_oracle
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    rows = {r['fixture_id']:r for r in value['fixture_results']}
    objects = value['objects']; nomination = value['nomination']
    branch = rows['PC-ZOH']['observation']
    def close(a, b, label):
        p.require(np.allclose(a, b, rtol=2e-12, atol=2e-14), 'PC equation mismatch: '+label)
    def inputs(key):
        return GeometryStageInputs.from_payload(objects[key])
    p.require(branch['source_policy']=='held_old_prestate_source_not_post_continuity_refresh'
              and branch['scope']=='exact_profile_seed_and_same_profile_signed_history; no_matched_forcing_contraction_claim'
              and branch['supplied_W_is_not_formation'] is True
              and branch['invalid_W_rejected']==['0.0','-1.0','infinity','nan'], 'PC history/formation ceiling changed')
    p.require([r['label'] for r in branch['stages']]==['nomination_seed','signed_history_companion'], 'missing PC state discrimination')
    for row in branch['stages']:
        subject = inputs(row['inputs_object']); following = inputs(row['next_inputs_object'])
        recipe = objects[row['provisional_object']]
        backend = CandidateADifferentialReference.from_payload(recipe['differential_reference'])
        p.require(recipe['inputs']==subject.to_payload()
                  and subject.geometry.reference.profile.to_payload()==nomination
                  and following.geometry.reference.profile.to_payload()==nomination, 'PC source/target nomination changed')
        current, reset = deepcopy(seed['initial']['current']), deepcopy(seed['initial']['reset'])
        if row['label']=='signed_history_companion':
            current['Z_4']=[-0.25]; reset['Z_4']=[0.125]
        p.require(subject.to_payload()['current']==current and subject.to_payload()['reset']==reset,
                  'PC companion changed more than declared carrier history')
        expected = independent_beat(subject, backend)
        p.require(set(row['observed'])==set(row['independent_oracle'])==set(expected), 'incomplete PC equation evidence')
        for key in expected:
            close(row['observed'][key], expected[key], key)
            close(row['independent_oracle'][key], expected[key], 'oracle '+key)
        close(subject.geometry.one_form_hodge.matrix, old_h(subject), 'old Z geometry')
        close(following.current.C, expected['final_C'], 'published C')
        close(following.current.W_A, expected['written_W'], 'published W')
        close(following.current.Z_4, expected['written_Z'], 'published Z')
        # Pre-read W-hat consumes baseline J0, while the writer uses total J
        # and the post-continuity resource; neither consumes prospective Z.
        ref = subject.geometry.reference; candidate = ref.profile.params_resolved.candidate
        b = np.asarray(ref.graph.incidence); c = np.asarray(subject.current.C); w = np.asarray(subject.current.W_A)
        phi = candidate.kappa_c*b@np.diag(w)@b.T@c + candidate.kappa_Ah*b@(old_h(subject)-np.asarray(ref.pairings.one_form.matrix))@b.T@c
        j0 = -candidate.eta*w*(b.T@phi)
        desc, target = scalar_oracle(ref, backend, tuple(c), tuple(j0))
        close(row['pre_J0'], j0, 'baseline')
        close(row['pre_descriptors'], desc, 'pre descriptors')
        close(row['pre_W_hat'], target, 'pre W hat')
        p.require(row['writer_old_Z']==list(subject.current.Z_4)
                  and row['writer_count']==row['carrier_writes']==row['continuity_evaluations']==1
                  and following.reset==subject.reset and following.current.Z_4!=subject.current.Z_4
                  and following.current.W_A!=subject.current.W_A, 'PC writer count/history source changed')
        p.require([r['role'] for r in row['admissions']]==['reset','restart'], 'missing PC both-role readmission')
        for admission in row['admissions']:
            admitted = inputs(admission['inputs_object'])
            p.require(admitted.geometry.reference==subject.geometry.reference
                      and admitted.current==(subject.reset if admission['role']=='reset' else following.current), 'borrowed readmission state')
            j, _ = independent_point(admitted, backend, old_h(admitted))
            close(admission['h'], old_h(admitted), 'readmission geometry')
            close(admission['current'], j, 'readmission current')
        cert = {k:F(v) for k,v in row['certificate'].items()}
        p.require(0 < cert['hodge_lower'] <= cert['hodge_upper']
                  and cert['source_norm_upper'] <= cert['carrier_radius'] == F(ref.profile.params_resolved.realization.radius)
                  and cert['current_conditioning_upper'] <= F(ref.profile.params_resolved.solver.conditioning_limit), 'PC envelope/domain not admitted')
        p.require(float(np.linalg.norm(np.asarray(row['observed']['source']))) <= float(cert['source_norm_upper']), 'PC source exceeds envelope')
    for key in ('A-POSITIVE-W-ADMISSION','A-EXACT-PRE-READ-W-HAT','A-POST-CONTINUITY-REFRESH',
                'A-LOG-WRITER','A-NO-SAME-BEAT-NEW-W-READ','A-INITIALIZATION-VS-FORMATION'):
        p.require(rows[key]['observation']==branch, 'candidate cell borrowed a different PC stage')
    for key in ('A-CHI-ZERO','A-ZETA-ZERO'):
        control = rows[key]['observation']; subject = inputs(control['inputs_object'])
        p.require(subject.geometry.reference.profile.complete_profile_id==rows[key]['complete_profile_id']
                  and subject.current.Z_4==(-0.25,) and control['source']==[[0.]]
                  and control['zero_source_release_not_reset'] is True, 'control old-carrier/source changed')
        expected_z = zoh_oracle(subject.current.Z_4,(0.,),subject.dt,subject.geometry.reference.profile.params_resolved.realization.tau_PC)
        p.require(control['written_Z']==list(expected_z) and expected_z!=(0.,) and expected_z!=subject.current.Z_4,
                  'native release replaced by reset/drop')
        close(objects[rows[key]['poststate_object']]['scientific_state']['authoritative']['Z_4'], expected_z, 'control published Z')
    pressure = value['readmission_pressure']
    p.require([r['role'] for r in pressure]==['reset','restart'], 'missing PC readmission rejection')
    for row in pressure:
        before, after = [objects[row[k]] for k in ('prestate_object','poststate_object')]
        result = objects[row['result_object']]
        p.require(before==after and before['reference']['profile']==nomination
                  and row['whole_publication_unchanged'] is True
                  and row['fault']=='test_only_native_readmission_fault'
                  and row['carrier_writes_before_rejection']==(0 if row['role']=='reset' else 1)
                  and result['committed'] is False
                  and result['solver_disposition']==(None if row['role']=='reset' else 'valid_root')
                  and result['failure']['code']=='no_admitted_root'
                  and result['failure']['stage']==('pre_read_reconstruction' if row['role']=='reset' else 'final_reconstruction'),
                  'PC late rollback evidence changed')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=4,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('A_PC'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_pc_local import APCLocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'A_PC local product tests failed')
    p.require(bindings()==sources,'sources changed during A_PC capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_PC']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-A_PC-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=APCLocalProductTests.rows,objects=APCLocalProductTests.objects,
        readmission_pressure=APCLocalProductTests.pressure,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='21 local A_PC catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
