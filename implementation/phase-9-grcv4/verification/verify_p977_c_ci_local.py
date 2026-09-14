"""Retained exact C_CI local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_c_ci_local.py'
TEST=p.HERE+'test_p977_c_ci_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-C_CI-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_c_cases']
                  if r['id']!='C-LIFECYCLE-REFERENCE-MAP']+['CI-BRANCH']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.1ab-AuditFollowup.json',
           p.PHASE+'tranche-6/P9-6.1c-ExecutionRecord.json'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_c_ci_local import CCILocalProductTests
    return ['test_p977_c_ci_local.CCILocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(CCILocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-CI-C-ROOT', 'D10.2-EC-CI-C-CONTRACTION',
        'D10.2-EC-CI-C-ROOT-SELECTION', 'D11-C-EC-C-J0-CURRENT',
        'D11-C-EC-C-J0-DERIVATIVE', 'D11-C-EC-C-J0-COVARIANCE', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_c_ci_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-C_CI-local'
              and value['record_digest']==p.digest_record(value),'C_CI local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'C_CI local execution source drift')
    p.require(value['authority'] == authority(), 'C_CI authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_CI']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'C_CI nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=4,failures=[],errors=[],skips=[]),
              'C_CI local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'C_CI evidence object changed')
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
            p.require(row['evidence_layer'] in ('independent_equations_and_provisional_stage_not_public_commit','fixed_stage_no_operation')
                      and row['result_object'] is None and row['solver_disposition'] is None,
                      'provisional stage relabeled as committed execution')
        for name in ('request_object','result_object'):
            p.require(row[name] is None or row[name] in objects,'missing operation preimage')
    validate_science(value, seed)


def validate_science(value, seed):
    """Inspect retained preimages against independent equations; no runtime rerun."""
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle, p943_direction
    nomination=value['nomination']; objects=value['objects']
    rows={r['fixture_id']:r for r in value['fixture_results']}
    obs=lambda name: rows[name]['observation']
    def close(actual, expected, message, rtol=0, atol=2e-12):
        p.require(np.asarray(actual).shape==np.asarray(expected).shape
                  and np.allclose(actual,expected,rtol=rtol,atol=atol),message)
    def inputs(key):
        return GeometryStageInputs.from_payload(objects[key])
    baseline=obs('C-BASELINE-EXACT')
    subject=inputs(baseline['stage_inputs_object'])
    expected=dense_current_oracle(subject)
    for key in baseline['observed']:
        close(baseline['observed'][key],expected[key],'C baseline equation mismatch: '+key)
        close(baseline['independent_oracle'][key],expected[key],'C oracle changed: '+key)
    p.require(set(baseline['observed'])=={'projector','sector','hm','phi','j0','ident','q','current','read'},
              'missing baseline observable')
    candidate=nomination['params_resolved']['candidate']
    p.require(candidate['kappa_M_C']==0 and candidate['W_C_tr']=={'e':2.0},'different baseline nomination')
    for name,row in rows.items():
        if name.startswith('C-') and name!='C-POST-CONTINUITY-REDERIVATION':
            point=obs(name)
            p.require(point['stage_inputs_object']==baseline['stage_inputs_object']
                      and point['point_object']==baseline['point_object']
                      and row['evidence_layer']=='fixed_stage_no_operation','borrowed fixed stage')
    p.require(subject.to_payload()['reference']['profile']==nomination
              and subject.to_payload()['current']==seed['initial']['current'],'wrong C prestate')
    reference=obs('C-TR-REFERENCE-MAP')
    p.require(reference['E_H']!=reference['E_M'] and reference['mobility']==[1.0]
              and reference['mobility_unchanged'] is True,'mobility/Hodge authority transfer')
    changed=objects[reference['changed_h_inputs_object']]
    p.require(changed['reference']==subject.to_payload()['reference']
              and changed['current']==subject.to_payload()['current'],'Hodge control changes authority')
    selector=obs('C-SELECTOR-STRICT-GAP')
    p.require(selector['rank']==1 and selector['spectrum']==[0,4] and selector['cutoff']==1,'selector gap changed')
    boundary=obs('C-SELECTOR-BOUNDARY')
    p.require(boundary['diagnostic']=='domain_failure'
              and boundary['scope']=='fixed_stage_selector_rejection_not_public_operation'
              and boundary['inputs_object'] in objects,'selector boundary mislabeled')
    q=obs('C-QC-TYPING'); close(q['Q_C'],np.asarray(q['I_4M'])@q['G_J'],'Q_C typing changed')
    cond=obs('C-RETAINED-VS-PHYSICAL-CONDITIONING')
    p.require(cond['scope']=='one_dimensional_nomination_plus_explicit_algebra_only_similarity_counterexample'
              and cond['counterexample']==dict(retained=[[.5,0],[0,1]],physical=[[.5,5],[0,1]],limit=2,physical_rejected=True)
              and cond['certificates'] and all(c['condition_upper_squared']=='1' for c in cond['certificates']),
              'conditioning control scope changed')
    only=obs('C-C-ONLY-AUTHORITY')
    p.require(only['C']==list(subject.current.C) and only['W_A'] is None and only['Z_4'] is None,'invented C history')
    zero=obs('C-KAPPA-M-ZERO')
    p.require(zero['deformation']==[1.] and zero['mobility']==[1.]
              and zero['scope']=='nomination_has_kappa_M_C_zero','zero mobility-deformation control changed')
    close(zero['retained_hodge'],subject.geometry.one_form_hodge.matrix,'zero deformation retained H changed')
    derivative=obs('C-BASELINE-DERIVATIVE-COVARIANCE')
    p.require(derivative['dense_control_not_nominated'] is True and len(derivative['derivatives'])==2,
              'missing separately scoped derivative control')
    for index,entry in enumerate(derivative['derivatives']):
        declared=inputs(entry['inputs_object'])
        profile=declared.geometry.reference.profile
        p.require(entry['complete_profile_id']==profile.complete_profile_id
                  and (profile.complete_profile_id==nomination['complete_profile_id'])==(index==0)
                  and entry['epsilon']==2**-12,'derivative control identity changed')
        analytic=p943_direction(declared,entry['dc'],entry['dh'])
        p.require(set(entry['analytic'])==set(entry['finite'])=={'projector','sector','deformation','hm','phi','j0'},
                  'incomplete derivative evidence')
        for key in entry['analytic']:
            close(entry['analytic'][key],analytic[key],'analytical derivative drift: '+key)
            close(entry['finite'][key],analytic[key],'finite derivative mismatch: '+key,rtol=2e-6,atol=2e-7)
    signed=inputs(derivative['signed_inputs_object'])
    close(dense_current_oracle(signed)['j0'],-expected['j0'],'signed baseline covariance changed')
    close(derivative['signed_delta_J0'],-np.asarray(derivative['derivatives'][0]['analytic']['j0']),
          'signed derivative covariance changed')
    for name,field,target in (('C-CHI-ZERO','chi_C',0.),('C-ZETA-ZERO','zeta_C',0.),('C-ONE-CHI-GATE','chi_C',.5)):
        control=obs(name); declared=inputs(control['control_inputs_object']); profile=declared.geometry.reference.profile
        params=deepcopy(nomination['params_resolved']); params['candidate'][field]=target
        p.require(profile.to_payload()['params_resolved']==params
                  and control['control_complete_profile_id']==profile.complete_profile_id!=nomination['complete_profile_id']
                  and control['control_is_nominated_support'] is False,'control relabeled as nomination support')
        oracle=dense_current_oracle(declared)
        for actual,key in (('control_J','current'),('independent_J','current'),('control_read','read'),('independent_read','read'),('control_J0','j0')):
            close(control[actual],oracle[key],'zero/chi control mismatch: '+actual)
        if target==0:
            close(control['control_J'],control['control_J0'],'zero control not baseline')
            p.require(control['zero_root_object'] in objects and control['fixed_J_chi_ratio'] is None,'missing zero root')
        else:
            p.require(control['zero_root_object'] is None and control['fixed_J_chi_ratio']==2,'one-chi gate changed')
    branch=obs('CI-BRANCH'); cert=branch['certificate']
    p.require(branch==obs('C-POST-CONTINUITY-REDERIVATION'),'shared CI evidence differs')
    p.require(cert['scope']=='analytic_local_reference_ball'
              and branch['branch_scope']=='analytic_local_reference_ball_not_global_uniqueness'
              and F(cert['contraction_upper'])<1 and F(cert['displacement_upper'])<=F(cert['radius']),
              'CI branch not locally certified')
    realization=nomination['params_resolved']['realization']
    p.require(F(branch['residual_squared'])<=F(realization['tolerance'])**2
              and 1<=branch['root_evaluations']<=realization['iteration_limit']
              and branch['writer_count']==branch['carrier_writes']==0 and branch['continuity_evaluations']==1
              and branch['reset_and_restart_are_independent_admissions'] is True,'CI lifecycle staging changed')
    p.require(set(branch['observed'])==set(branch['independent_oracle'])=={'current','hodge','final_C','reset_current','restart_current'},
              'missing CI oracle observation')
    for key in branch['observed']:
        close(branch['observed'][key],branch['independent_oracle'][key],'CI oracle mismatch: '+key,atol=2e-11 if key!='final_C' else 2e-13)
    p.require(branch['observed']['current']!=branch['observed']['restart_current']
              and branch['observed']['current']!=branch['observed']['reset_current'],'reused live/root history')
    selected=inputs(branch['selected_inputs_object'])
    p.require(selected.to_payload()['reference']['profile']==nomination
              and selected.current==subject.current and selected.stage=='ci_trial','borrowed CI trial')
    p.require(len(branch['trial_points'])>1,'missing C rederivation trials')
    for point in branch['trial_points']:
        trial=inputs(point['inputs_object'])
        p.require(trial.current==subject.current and trial.stage=='ci_trial'
                  and trial.geometry.reference==subject.geometry.reference,'borrowed C trial authority')
        oracle=dense_current_oracle(trial)
        for field,key in (('J0','j0'),('current','current'),('sector','sector')):
            close(point[field],oracle[key],'C trial not rederived: '+field)
    budget=branch['budget_control']; limited=inputs(budget['inputs_object']).geometry.reference.profile
    p.require(budget['disposition']=='no_admitted_root' and budget['fallback_used'] is False
              and budget['scope']=='root_construction_rejection_not_public_operation'
              and limited.complete_profile_id!=nomination['complete_profile_id']
              and limited.params_resolved.realization.iteration_limit==1
              and limited.params_resolved.realization.tolerance==0,'budget failure scope changed')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=4,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('C_CI'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_c_ci_local import CCILocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'C_CI local product tests failed')
    p.require(bindings()==sources,'sources changed during C_CI capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_CI']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-C_CI-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=CCILocalProductTests.rows,objects=CCILocalProductTests.objects,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='26 local C_CI catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
