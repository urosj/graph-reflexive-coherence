"""Retained exact A_RG2b local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_a_rg2b_local.py'
TEST=p.HERE+'test_p977_a_rg2b_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-A_RG2b-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_a_cases']
                  if r['id']!='A-MIGRATION-HISTORY-RECEIPT']+['RG2B-SECTION']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.4c-ExecutionRecord.json',
           'tests/models/test_grc_v4_rg2b_graph.py','tests/models/test_grc_v4_candidate_a.py',
           'tests/models/test_grc_v4_ci.py',
           p.HERE+'test_p977_a_os_local.py'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_a_rg2b_local import ARG2bLocalProductTests
    return ['test_p977_a_rg2b_local.ARG2bLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(ARG2bLocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-PARENT-REAL-RG2B', 'D10.2-EC-RG-INVARIANCE',
        'D10.2-EC-RG-LIPSCHITZ-CONTRACTION', 'D10.2-EC-RG-DETERMINISM',
        'D10.2-EC-RG-CLAIM-CEILING', 'P9-EC-RECEIPT-PARENT-CEILING')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_a_rg2b_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-A_RG2b-local'
              and value['record_digest']==p.digest_record(value),'A_RG2b local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'A_RG2b local execution source drift')
    p.require(value['authority'] == authority(), 'A_RG2b authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_RG2b']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'A_RG2b nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=4,failures=[],errors=[],skips=[]),
              'A_RG2b local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'A_RG2b evidence object changed')
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
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_rg2b import RG2bCertificate
    from tests.models.test_grc_v4_lifecycle import primitive
    from test_p977_a_rg2b_local import oracle, inverse_oracle
    backend=CandidateADifferentialReference.from_payload(seed['differential_reference'])
    branch=next(r for r in rows if r['fixture_id']=='RG2B-SECTION')['observation']
    def close(actual,want,label):
        p.require(np.allclose(actual,want,rtol=0,atol=2e-13),'RG independent mismatch: '+label)
    def row(case):
        return next(r for r in rows if r['fixture_id']==case)
    p.require(branch['writer_count']==1 and branch['supplied_W_is_not_formation'] is True
              and branch['deterministic_reconstruction'] is True and branch['classical_derivative_rejected'] is True
              and branch['section_scope']=='bounded_completion_relative_Lipschitz_only'
              and branch['global_base_invariance_claimed'] is False and branch['CI_root_claimed'] is False
              and branch['invalid_W_rejected']==['0.0','-1.0','infinity','nan'],'RG scope/ownership drift')
    p.require([r['role'] for r in branch['roles']]==['current','reset','restart'],'missing/reordered RG roles')
    endpoint=GeometryStageInputs.from_payload(objects[branch['final_inputs_object']])
    initial=GeometryStageInputs.from_payload(seed['initial'])
    p.require(endpoint.current.Z_4 is None and endpoint.reset==initial.reset
              and endpoint.geometry.reference==initial.geometry.reference
              and endpoint.time==float(F(initial.time)+F(initial.dt))
              and endpoint.step_index==initial.step_index+1,'RG endpoint identity/history drift')
    for item,state in zip(branch['roles'],(initial.current,initial.reset,endpoint.current),strict=True):
        inputs=GeometryStageInputs.from_payload(objects[item['inputs_object']])
        selected=GeometryStageInputs.from_payload(objects[item['selected_inputs_object']])
        p.require(inputs.current==state and inputs.reset==initial.reset and inputs.geometry.reference==initial.geometry.reference
                  and inputs.dt==initial.dt and inputs.stage==initial.stage,'RG role borrowed authority')
        p.require(selected.current==state and selected.stage=='rg2b_section'
                  and selected.geometry.reference==inputs.geometry.reference
                  and selected.geometry.one_form_hodge.matrix==tuple(map(tuple,item['h'])),'RG selected stage drift')
        cert=RG2bCertificate(inputs,backend)
        p.require(item['certificate']==dict(cert.bounds),'RG certificate changed')
        b={k:F(v) for k,v in item['certificate'].items()}
        p.require(0<=b['contraction_upper']<1 and 0<=F(item['error_upper'])<=F(nomination['params_resolved']['realization']['error_tolerance'])
                  and 0<=item['levels'] and 1<=item['evaluations']<=nomination['params_resolved']['realization']['iteration_limit'],
                  'RG finite section not certified')
        independent=inverse_oracle(inputs,backend)
        close(item['inverse_oracle_h'],independent,'inverse')
        p.require(np.linalg.norm(np.array(item['h'])-independent)<=float(F(item['error_upper'])+b['section_radius']*b['contraction_upper']**2)+2e-15,
                  'RG section differs from independent transforms')
        expected=oracle(inputs,backend,item['h'])
        for name in ('current','W_hat','descriptors'): close(item[name],expected[name],name)
    current=branch['roles'][0]
    expected=oracle(initial,backend,current['h'])
    for name,want in expected.items(): close(branch['observed'][name],want,name)
    close(endpoint.current.C,expected['final_C'],'endpoint C')
    close(endpoint.current.W_A,expected['written_W'],'endpoint W')
    close(branch['generated_h'],np.array(initial.geometry.one_form_hodge.matrix)+
          initial.geometry.reference.profile.params_resolved.geometry.kappa_H*np.array(expected['source']),'source pushforward')
    diagnostics=branch['diagnostics']
    p.require(diagnostics['regularity']=='Lipschitz_only' and diagnostics['continuity_evaluations']==1
              and diagnostics['carrier_writes']==0 and diagnostics['section_error_upper']==current['error_upper'],
              'RG step regularity/writer mismatch')
    bound=F(diagnostics['invariance_error_bound'])
    p.require(0<=F(diagnostics['invariance_residual'])<=bound< F(1e-10),'RG invariance bound failed')
    # Binary64 comparison is a discriminator, not a replacement for the rational certificate.
    residual=np.linalg.norm(np.array(branch['roles'][2]['h'])-np.array(branch['generated_h']))
    p.require(residual<=float(bound)+2e-15,'RG restart not invariant within bound')
    science=('A-POSITIVE-W-ADMISSION','A-EXACT-PRE-READ-W-HAT','A-POST-CONTINUITY-REFRESH',
             'A-LOG-WRITER','A-NO-SAME-BEAT-NEW-W-READ','A-INITIALIZATION-VS-FORMATION','RG2B-SECTION')
    for case in science:
        r=row(case)
        p.require(r['observation']==branch and r['committed'] is True,'shared RG execution inconsistent')
        before,after=(objects[r[k]] for k in ('prestate_object','poststate_object'))
        p.require(before['scientific_state']['authoritative']==primitive(initial.current)
                  and after['scientific_state']['authoritative']==primitive(endpoint.current),'RG measured endpoint replaced')
    for case in ('A-CHI-ZERO','A-ZETA-ZERO'):
        r=row(case);o=r['observation'];profile=objects[r['prestate_object']]['reference']['profile']
        p.require(o['control_profile_id']==profile['complete_profile_id']!=NOMINATED
                  and o['control_parameter']==('chi_A' if case=='A-CHI-ZERO' else 'zeta_A')
                  and o['no_carrier'] is True,'control identity or carrier drift')
        close(o['section_h'],initial.geometry.one_form_hodge.matrix,'zero source section')
    o=row('RESET-AFTER-ORDINARY')['observation']
    p.require(o['independent_reset_authority']==primitive(initial.reset),'independent reset changed')
    r=row('RESET-AFTER-ORDINARY');before,after=(objects[r[k]] for k in ('prestate_object','poststate_object'))
    p.require(after['scientific_state']['authoritative']==primitive(initial.reset)
              and before['scientific_state']['authoritative']!=primitive(initial.reset),'reset not distinct/consumed')
    p.require(row('RECEIPT-OWNERSHIP')['observation']['coherent_missing_parent_rejected'] is True
              and row('SNAPSHOT-LOAD-REPLAY')['observation']['exact_result_and_loaded_replay'] is True
              and row('DUPLICATION-INDEPENDENCE')['observation']['exported_mutations_detached'] is True,
              'lifecycle pressure omitted')
    pressure=value['readmission_pressure']
    p.require([r['case'] for r in pressure]==['wrong_beat','reset_outside_inner','budget','reset_native','restart_native','late_publication'],
              'missing RG pressure')
    for item in pressure:
        p.require(item['fallback_used'] is False,'RG fallback claimed')
        case=item['case']
        if case in ('budget','reset_outside_inner'):
            inputs=GeometryStageInputs.from_payload(objects[item['inputs_object']])
            p.require(item['scope']=='construction_control_not_public_operation' and item['rejected'] is True,'construction relabeled')
            if case=='budget':
                p.require(inputs.geometry.reference.profile.complete_profile_id!=NOMINATED
                          and inputs.geometry.reference.profile.params_resolved.realization.iteration_limit==1,'budget control borrowed nomination')
            else:
                p.require(inputs.geometry.reference.profile.complete_profile_id==NOMINATED
                          and max(abs(c-2) for c in inputs.reset.C)>0.125,'reset control is admitted')
        else:
            p.require(objects[item['prestate_object']]==objects[item['poststate_object']]
                      and item['whole_publication_unchanged'] is True
                      and item['writer_count']==int(case in ('restart_native','late_publication')),'RG rollback/write drift')
            stages={'wrong_beat':'admission','reset_native':'pre_read_reconstruction','restart_native':'final_reconstruction','late_publication':None}
            p.require(item['failure_stage']==stages[case],'wrong RG failure stage')


def check(initial_review=None):
    if initial_review is None: initial_review=review.check()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=4,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('A_RG2b'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_rg2b_local import ARG2bLocalProductTests
    original=review.check()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'A_RG2b local product tests failed')
    p.require(bindings()==sources,'sources changed during A_RG2b capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['A_RG2b']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-A_RG2b-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=ARG2bLocalProductTests.rows,objects=ARG2bLocalProductTests.objects,readmission_pressure=ARG2bLocalProductTests.pressure,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='21 local A_RG2b catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
