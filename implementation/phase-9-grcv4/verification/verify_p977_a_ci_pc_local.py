"""Retained exact A_CI_PC local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_a_ci_pc_local.py'
TEST=p.HERE+'test_p977_a_ci_pc_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-A_CI_PC-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_a_cases']
                  if r['id']!='A-MIGRATION-HISTORY-RECEIPT']+['CI-PC-SAME-SOURCE']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.1ab-AuditFollowup.json',
           p.PHASE+'tranche-6/P9-6.1c-ExecutionRecord.json',
           p.HERE+'test_p977_a_pc_local.py',
           'tests/models/test_grc_v4_cipc.py','tests/models/test_grc_v4_ci.py',
           'tests/models/test_grc_v4_pc.py','tests/models/test_grc_v4_candidate_a.py'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_a_ci_pc_local import ACIPCLocalProductTests
    return ['test_p977_a_ci_pc_local.ACIPCLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(ACIPCLocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-CI-PC-A-COMPOSITION', 'D10.2-EC-CI-PC-A-ROOT',
        'D10.2-EC-PARENT-REAL-CI-PC', 'D10.2-EC-PC-ZOH-WRITER',
        'D10.2-EC-PC-RELEASE', 'D10.2-EC-CI-PC-ABLATIONS', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_a_ci_pc_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-A_CI_PC-local'
              and value['record_digest']==p.digest_record(value),'A_CI_PC local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'A_CI_PC local execution source drift')
    p.require(value['authority'] == authority(), 'A_CI_PC authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_CI_PC']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'A_CI_PC nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=5,failures=[],errors=[],skips=[]),
              'A_CI_PC local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'A_CI_PC evidence object changed')
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
    branch = next(r for r in rows if r['fixture_id'] == 'CI-PC-SAME-SOURCE')['observation']
    cert = branch['certificate']
    p.require(cert['scope'] == 'analytic_local_reference_ball'
              and branch['branch_scope'] == 'analytic_local_reference_ball_not_global_uniqueness'
              and Fraction(cert['contraction_upper']) < 1
              and Fraction(cert['displacement_upper']) <= Fraction(cert['radius']), 'CI branch not certified')
    params = nomination['params_resolved']['realization']
    p.require(Fraction(branch['residual_squared']) <= Fraction(params['tolerance'])**2
              and 1 <= branch['root_evaluations'] <= params['iteration_limit']
              and branch['writer_count'] == branch['continuity_evaluations'] == 1
              and branch['current_stage_roster'] == ['cipc_trial']
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
        p.require(inputs['current'] == seed['initial']['current'] and inputs['stage'] == 'cipc_trial',
                  'CI trial borrowed new history or another prestate')

    validate_coupling(value, seed, branch)

def validate_coupling(value, seed, branch):
    """Recompute literal equations from retained preimages, not production roots."""
    from dataclasses import replace
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from tests.models.test_grc_v4_generic_lifecycle import fixture
    from tests.models.test_grc_v4_cipc import independent_root
    from tests.models.test_grc_v4_ci import independent_point
    from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
    from tests.models.test_grc_v4_pc import zoh_oracle
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    objects=value['objects']; nomination=value['nomination']
    _,backend=fixture('A_CI_PC')
    rows={r['fixture_id']:r for r in value['fixture_results']}
    def close(actual,expected,message,atol=2e-11):
        p.require(np.asarray(actual).shape==np.asarray(expected).shape and
                  np.allclose(actual,expected,rtol=0,atol=atol),message)
    def inputs(key):return GeometryStageInputs.from_payload(objects[key])
    source=inputs(branch['source_inputs_object'])
    following=inputs(branch['next_inputs_object'])
    reset=inputs(branch['reset_inputs_object'])
    p.require(source.to_payload()['current']==seed['initial']['current']
              and source.to_payload()['reset']==seed['initial']['reset']
              and source.to_payload()['reference']['profile']==nomination,'wrong coupled prestate')
    p.require(branch['carrier_writes']==branch['writer_count']==branch['continuity_evaluations']==1
              and branch['source_policy']=='selected_root_source_held_once'
              and branch['composition_gain']==nomination['identity_payload']['composition_gain']==2
              and branch['rho_inst']==nomination['params_resolved']['realization']['rho_inst']==1,
              'coupled source/writer/identity changed')
    h,j,s=independent_root(source,backend)
    close(branch['observed']['current'],j,'coupled current equation')
    close(branch['observed']['hodge'],h,'coupled geometry equation')
    close(branch['source'],s,'same-root structural source')
    ref=source.geometry.reference; params=ref.profile.params_resolved
    close(h,np.asarray(ref.pairings.one_form.matrix)+params.geometry.kappa_H*(np.asarray(source.current.Z_4).reshape(h.shape)+s),'literal unit-plus-unit geometry')
    # The writer consumes the admitted numerical root, not the oracle's more
    # tightly converged root. First compare roots above, then check the exact
    # consumed-current path without silently tightening the declared solver.
    consumed=branch['observed']['current']
    c=tuple(float(F(v)+sign*F(source.dt)*F(float(consumed[0]))) for v,sign in zip(source.current.C,(-1,1)))
    desc,target=scalar_oracle(ref,backend,c,tuple(consumed))
    w=log_writer_oracle(source.current.W_A,target,source.dt,params.candidate.tau_A)
    z=zoh_oracle(source.current.Z_4,tuple(s.flat),source.dt,params.realization.tau_PC)
    for key,expected in [('final_C',c),('writer_descriptors',desc),('W_drv',target),('written_W',w)]:
        close(branch['observed'][key],expected,'post-continuity '+key,2e-13)
    close(branch['written_Z'],z,'held source ZOH',2e-14)
    close(following.current.C,c,'next C',2e-13);close(following.current.W_A,w,'next W',2e-13)
    close(following.current.Z_4,z,'next Z',2e-14)
    p.require(following.reset==source.reset and reset.current==source.reset
              and following.geometry.reference==reset.geometry.reference==ref,'readmission authority changed')
    for role,subject in [('reset',reset),('restart',following)]:
        close(branch['observed'][role+'_current'],independent_root(subject,backend)[1],role+' independent root')
    for trial in branch['trial_points']:
        subject=inputs(trial['inputs_object'])
        h=np.asarray(subject.geometry.one_form_hodge.matrix)
        b=np.asarray(ref.graph.incidence);w=np.asarray(subject.current.W_A);c=np.asarray(subject.current.C)
        phi=params.candidate.kappa_c*b@np.diag(w)@b.T@c+params.candidate.kappa_Ah*b@(h-np.asarray(ref.pairings.one_form.matrix))@b.T@c
        j0=-params.candidate.eta*w*(b.T@phi)
        close(trial['J0'],j0,'trial baseline')
        close(trial['W_hat'],scalar_oracle(ref,backend,subject.current.C,tuple(j0))[1],'fresh trial W-hat')
        close(trial['current'],independent_point(subject,backend,h)[0],'trial current')
    cert=branch['certificate']
    p.require(F(cert['uniform_source_upper'])<=F(cert['carrier_radius'])
              and F(cert['uniform_source_slack'])==F(cert['carrier_radius'])-F(cert['uniform_source_upper'])
              and cert['rho_inst']==1,'composite envelope changed')
    for name in ('A-POSITIVE-W-ADMISSION','A-EXACT-PRE-READ-W-HAT','A-POST-CONTINUITY-REFRESH',
                 'A-LOG-WRITER','A-NO-SAME-BEAT-NEW-W-READ','A-INITIALIZATION-VS-FORMATION'):
        p.require(rows[name]['observation']==branch,'shared scientific execution changed')
    companions=value['companions']
    p.require([r['control_parameter'] for r in companions]==[None,'chi_A','zeta_A'],'missing companion/release control')
    for row in companions:
        subject=inputs(row['inputs_object']); nxt=inputs(row['next_inputs_object'])
        field=row['control_parameter']; expected=deepcopy(nomination['params_resolved'])
        if field:expected['candidate'][field]=0
        p.require(canonical_json_bytes(subject.geometry.reference.profile.params_resolved.to_payload())==canonical_json_bytes(expected)
                  and subject.current==replace(source.current,Z_4=(-.25,))
                  and subject.reset==replace(source.reset,Z_4=(.125,)),'companion identity or history changed')
        p.require(row['scope']==('same_nomination_history_companion' if field is None else 'distinct_zero_gate_control_not_support')
                  and row['writer_count']==row['carrier_writes']==row['continuity_evaluations']==1,'companion scope or writer changed')
        h,j,s=independent_root(subject,backend)
        for key,expected in [('hodge',h),('current',j),('source',s)]:close(row[key],expected,'companion '+key)
        z=zoh_oracle(subject.current.Z_4,tuple(s.flat),subject.dt,params.realization.tau_PC)
        close(row['written_Z'],z,'companion release',2e-14);close(nxt.current.Z_4,z,'companion endpoint',2e-14)
        c=tuple(float(F(v)+sign*F(subject.dt)*F(float(row['current'][0]))) for v,sign in zip(subject.current.C,(-1,1)))
        target=scalar_oracle(subject.geometry.reference,backend,c,tuple(row['current']))[1]
        close(nxt.current.C,c,'companion continuity',2e-13)
        close(nxt.current.W_A,log_writer_oracle(subject.current.W_A,target,subject.dt,params.candidate.tau_A),'companion W',2e-13)
        if field:p.require(tuple(s.flat)==(0.,) and -.25<z[0]<0,'zero-source release is not reset/drop')
        else:p.require(not np.allclose(s,independent_root(nxt,backend)[2],rtol=0,atol=1e-10),'post-continuity source not distinguished')
        p.require([r['role'] for r in row['roles']]==['reset','restart'],'missing companion readmission')
        for role in row['roles']:
            admitted=inputs(role['inputs_object'])
            p.require(admitted.current==(subject.reset if role['role']=='reset' else nxt.current)
                      and admitted.geometry.reference==subject.geometry.reference,'borrowed readmission role')
            h,j,_=independent_root(admitted,backend)
            close(role['current'],j,'companion readmission current');close(role['hodge'],h,'companion readmission geometry')
    pressure=value['readmission_pressure']
    p.require([r['role'] for r in pressure]==['reset','restart'],'missing rejection role')
    for row in pressure:
        result=objects[row['result_object']];is_reset=row['role']=='reset'
        p.require(objects[row['prestate_object']]==objects[row['poststate_object']]
                  and row['whole_publication_unchanged'] is True
                  and row['carrier_writes_before_rejection']==(0 if is_reset else 1)
                  and result['committed'] is False
                  and result['solver_disposition']==(None if is_reset else 'valid_root')
                  and result['failure']['code']=='no_admitted_root'
                  and result['failure']['stage']==('pre_read_reconstruction' if is_reset else 'final_reconstruction'),
                  'readmission rollback/writer boundary changed')
    p.require(rows['RESET-AFTER-ORDINARY']['observation']['independent_reset_authority']==seed['initial']['reset']
              and rows['RECEIPT-OWNERSHIP']['observation']['coherent_missing_parent_rejected'] is True
              and rows['DUPLICATION-INDEPENDENCE']['observation']['exported_mutations_detached'] is True,
              'lifecycle ownership changed')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=5,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('A_CI_PC'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_ci_pc_local import ACIPCLocalProductTests
    # Check exact retained input identity here; the normal status/check path
    # verifies the full predecessor chain once, outside the native capture.
    original=review.read(review.RECORD)
    p.require(original['record_digest']==p.digest_record(original)
              and p.g2_bindings_match(original['source_bindings'],review.bindings()),
              'initial review source identity changed')
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'A_CI_PC local product tests failed')
    p.require(bindings()==sources,'sources changed during A_CI_PC capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_CI_PC']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-A_CI_PC-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=ACIPCLocalProductTests.rows,objects=ACIPCLocalProductTests.objects,
        companions=ACIPCLocalProductTests.companions,readmission_pressure=ACIPCLocalProductTests.pressure,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='21 local A_CI_PC catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
