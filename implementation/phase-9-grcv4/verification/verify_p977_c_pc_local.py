"""Retained exact C_PC local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_c_pc_local.py'
TEST=p.HERE+'test_p977_c_pc_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-C_PC-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_c_cases']
                  if r['id']!='C-LIFECYCLE-REFERENCE-MAP']+['PC-ZOH']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.2abc-AuditFollowup.json',
           p.PHASE+'tranche-6/P9-6.2ab-ExecutionRecord.json'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_c_pc_local import CPCLocalProductTests
    return ['test_p977_c_pc_local.CPCLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(CPCLocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-PARENT-REAL-PC', 'D10.2-EC-PC-ZOH-WRITER',
        'D10.2-EC-PC-RELEASE', 'D10.2-EC-PC-MATCHED-FORCING',
        'D11-C-EC-C-TR-REFERENCE-FIELD', 'D11-C-EC-C-M4-FACTORIZATION', 'D11-C-EC-C-J0-CURRENT',
        'D11-C-EC-C-J0-DERIVATIVE', 'D11-C-EC-C-J0-COVARIANCE', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_c_pc_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-C_PC-local'
              and value['record_digest']==p.digest_record(value),'C_PC local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'C_PC local execution source drift')
    p.require(value['authority'] == authority(), 'C_PC authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_PC']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'C_PC nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=5,failures=[],errors=[],skips=[]),
              'C_PC local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'C_PC evidence object changed')
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
    p.require(only['C']==list(subject.current.C) and only['W_A'] is None and only['Z_4']==list(subject.current.Z_4)
              and only['scope']=='no_T_C_or_mobility_state; persistent_Z_is_realization_authority'
              and only['invalid_A_history_rejected'] is True,'invented C history')
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
            p.require(control['zero_step_inputs_object'] in objects and control['fixed_J_chi_ratio'] is None
                      and control['zero_source_release_not_reset'] is True,'missing zero-source PC step')
            from tests.models.test_grc_v4_pc import zoh_oracle
            following=inputs(control['zero_step_inputs_object'])
            expected_z=zoh_oracle(declared.current.Z_4,(0.,),declared.dt,profile.params_resolved.realization.tau_PC)
            p.require(declared.current.Z_4==(-.25,) and following.current.Z_4==expected_z
                      and expected_z!=(0.,) and expected_z!=declared.current.Z_4
                      and following.current.W_A is None and following.reset==declared.reset
                      and following.geometry.reference==declared.geometry.reference,'native release confused with drop or foreign state')
        else:
            p.require(control['zero_step_inputs_object'] is None and control['fixed_J_chi_ratio']==2,'one-chi gate changed')
    validate_pc(value,seed)


def validate_pc(value,seed):
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from test_p977_c_pc_local import independent_beat,old_h
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle
    objects=value['objects'];nomination=value['nomination']
    rows={r['fixture_id']:r for r in value['fixture_results']}
    branch=rows['PC-ZOH']['observation']
    def inputs(key):return GeometryStageInputs.from_payload(objects[key])
    def close(a,b,name):
        p.require(np.shape(a)==np.shape(b) and np.allclose(a,b,rtol=2e-12,atol=2e-14),'PC equation drift: '+name)
    p.require(branch==rows['C-POST-CONTINUITY-REDERIVATION']['observation']
              and branch['source_policy']=='held_old_prestate_source_not_post_continuity_refresh'
              and branch['candidate_history_or_W_writer'] is False
              and branch['matched_forcing_contraction_claimed'] is False
              and branch['indefinite_base_chart_invariance_claimed'] is False
              and branch['scope']=='exact_profile_seed_and_same_profile_signed_history; separate_dense_fixed_stage_controls',
              'PC source/history/claim ceiling changed')
    p.require([r['label'] for r in branch['stages']]==['nomination_seed','signed_history_companion'],'missing PC state discrimination')
    for row in branch['stages']:
        subject=inputs(row['inputs_object']);following=inputs(row['next_inputs_object'])
        recipe=objects[row['provisional_object']]
        p.require(recipe['inputs']==subject.to_payload() and recipe['differential_reference'] is None
                  and subject.geometry.reference.profile.to_payload()==nomination
                  and following.geometry.reference==subject.geometry.reference,'PC nomination/backend drift')
        current,reset=deepcopy(seed['initial']['current']),deepcopy(seed['initial']['reset'])
        if row['label']=='signed_history_companion':current['Z_4']=[-.25];reset['Z_4']=[.125]
        p.require(subject.to_payload()['current']==current and subject.to_payload()['reset']==reset,'PC companion changed undeclared authority')
        expected=independent_beat(subject)
        p.require(set(row['observed'])==set(row['independent_oracle'])==set(expected),'missing PC equations')
        for key in expected:
            close(row['observed'][key],expected[key],key)
            close(row['independent_oracle'][key],expected[key],'oracle '+key)
        close(subject.geometry.one_form_hodge.matrix,old_h(subject),'old Z geometry')
        close(following.current.C,expected['final_C'],'written C')
        close(following.current.Z_4,expected['written_Z'],'written Z')
        p.require(following.current.W_A is None and following.reset==subject.reset
                  and following.current.Z_4!=subject.current.Z_4
                  and row['writer_count']==0 and row['carrier_writes']==row['continuity_evaluations']==1
                  and row['held_source_not_restart_source'] is True,'PC writer/readmission staging changed')
        p.require([r['role'] for r in row['chains']]==['consumed','reset','restart'],'missing C readmission chain')
        for chain in row['chains']:
            admitted=inputs(chain['inputs_object'])
            expected_state={'consumed':subject.current,'reset':subject.reset,'restart':following.current}[chain['role']]
            p.require(admitted.current==expected_state and admitted.geometry.reference==subject.geometry.reference
                      and admitted.reset==subject.reset and admitted.stage=='pre_read','borrowed C readmission inputs')
            close(admitted.geometry.one_form_hodge.matrix,old_h(admitted),'readmission geometry')
            oracle=dense_current_oracle(admitted)
            p.require(set(chain['observed'])==set(chain['independent_oracle'])=={'projector','sector','hm','phi','j0','ident','q','current','read'},'incomplete C chain')
            for key in chain['observed']:
                close(chain['observed'][key],oracle[key],chain['role']+' '+key)
                close(chain['independent_oracle'][key],oracle[key],'oracle '+chain['role']+' '+key)
        p.require(row['chains'][0]['observed']['j0']!=row['chains'][2]['observed']['j0']
                  and row['chains'][0]['observed']['current']!=row['chains'][1]['observed']['current'],'C readmissions collapsed')
        cert={k:F(v) for k,v in row['certificate'].items()}
        p.require(0<cert['hodge_lower']<=cert['hodge_upper']
                  and cert['source_norm_upper']<=cert['carrier_radius']==F(nomination['params_resolved']['realization']['radius'])
                  and cert['current_conditioning_upper']<=F(nomination['params_resolved']['solver']['conditioning_limit']),
                  'PC envelope/domain not admitted')
        p.require(float(np.linalg.norm(row['observed']['source']))<=float(cert['source_norm_upper']),'source outside certified envelope')
    pressure=value['readmission_pressure']
    p.require([r['role'] for r in pressure]==['reset','restart'],'missing both-role rejection pressure')
    for row in pressure:
        before,after=[objects[row[k]] for k in ('prestate_object','poststate_object')]
        result=objects[row['result_object']]
        p.require(before==after and before['reference']['profile']==nomination
                  and row['whole_publication_unchanged'] is True and row['fault']=='test_only_native_readmission_fault'
                  and result['committed'] is False
                  and row['carrier_writes_before_rejection']==(0 if row['role']=='reset' else 1)
                  and result['solver_disposition']==(None if row['role']=='reset' else 'valid_root')
                  and result['failure']['code']=='no_admitted_root'
                  and result['failure']['stage']==('pre_read_reconstruction' if row['role']=='reset' else 'final_reconstruction'),
                  'C_PC rejection/rollback changed')
    validate_lifecycle(value,seed)


def validate_lifecycle(value,seed):
    objects=value['objects'];rows={r['fixture_id']:r for r in value['fixture_results']}
    row=rows['RESET-AFTER-ORDINARY'];before=objects[row['prestate_object']];after=objects[row['poststate_object']]
    p.require(before['scientific_state']['authoritative']!=before['reset']['authoritative']
              and after['scientific_state']['authoritative']==before['reset']['authoritative']
              and before['reset']==after['reset']
              and row['observation']['independent_reset_authority']==seed['initial']['reset']
              and before['receipt_ledger']==after['receipt_ledger'][:-4],'reset carrier/resource authority changed')
    for key in ('time','step_index','Q_target'):
        p.require(before['scientific_state'][key]==after['scientific_state'][key],'reset clock/charge drift')
    replay=rows['SNAPSHOT-LOAD-REPLAY'];receipt=rows['RECEIPT-OWNERSHIP']
    p.require(replay['prestate_object']==receipt['prestate_object'] and replay['poststate_object']==receipt['poststate_object']
              and replay['observation']['saved_snapshot_object']==replay['prestate_object']
              and replay['observation']['exact_result_and_loaded_replay'] is True
              and receipt['observation']['coherent_missing_parent_rejected'] is True,'replay/parent evidence changed')
    result=objects[receipt['result_object']]
    for emitted in result['emitted_receipts']:
        p.require(emitted['identity_payload']['core']['parent_receipt_ids']==[receipt['observation']['previous_primary']],
                  'missing previous primary ownership')
    dup=rows['DUPLICATION-INDEPENDENCE']['observation']
    p.require(dup['exported_mutations_detached'] is True and dup['independently_rebased_clone'] is True
              and objects[dup['original_owner_snapshot_object']]['scientific_state']['authoritative']==seed['initial']['reset'],
              'duplicate aliasing altered original authority')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=5,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('C_PC'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_c_pc_local import CPCLocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'C_PC local product tests failed')
    p.require(bindings()==sources,'sources changed during C_PC capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_PC']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-C_PC-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=CPCLocalProductTests.rows,objects=CPCLocalProductTests.objects,
        readmission_pressure=CPCLocalProductTests.pressure,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='26 local C_PC catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
