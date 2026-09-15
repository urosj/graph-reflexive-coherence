"""Retained exact C_RG2b local product; --run emits a new run without writing."""

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

SCRIPT=p.HERE+'verify_p977_c_rg2b_local.py'
TEST=p.HERE+'test_p977_c_rg2b_local.py'
RECORD=p.PHASE+'tranche-7/P9-7.7-C_RG2b-LocalProduct.json'
LOCAL_LIFECYCLE={'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RECEIPT-OWNERSHIP','DUPLICATION-INDEPENDENCE'}


def required():
    catalog=review.read(review.CATALOG)
    return sorted([r['id'] for r in catalog['common_cases']]+[r['id'] for r in catalog['candidate_c_cases']
                  if r['id']!='C-LIFECYCLE-REFERENCE-MAP']+['RG2B-SECTION']+sorted(LOCAL_LIFECYCLE))


def bindings():
    names={SCRIPT,TEST,review.RECORD,review.SCRIPT,review.CATALOG,
           'specs/grc-v4-spec.md','specs/grc-common-interface-v4-ext.md',
           p.INV+'drafts/2026-09-GRC-V4.md',review.SOURCES['lifecycle'],
           p.PHASE+'tranche-6/P9-6.4c-ExecutionRecord.json',
           'tests/models/test_grc_v4_rg2b_graph.py','tests/models/test_grc_v4_candidate_c.py',
           'tests/models/test_grc_v4_ci.py',
           p.HERE+'verify_p977_c_ci_pc_local.py'}
    return {**runtime_bindings(),**{n:p.sha((p.ROOT/n).read_bytes()) for n in sorted(names)}}


def roster():
    from test_p977_c_rg2b_local import CRG2bLocalProductTests
    return ['test_p977_c_rg2b_local.CRG2bLocalProductTests.'+n
            for n in unittest.TestLoader().getTestCaseNames(CRG2bLocalProductTests)]


def authority():
    sys.path.insert(0, str(p.ROOT/p.SIDE/'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        'D10.2-EC-PARENT-REAL-RG2B', 'D10.2-EC-RG-INVARIANCE',
        'D10.2-EC-RG-LIPSCHITZ-CONTRACTION', 'D10.2-EC-RG-DETERMINISM',
        'D10.2-EC-RG-CLAIM-CEILING', 'P9-EC-RECEIPT-PARENT-CEILING',
        'D11-C-EC-C-TR-REFERENCE-FIELD', 'D11-C-EC-C-M4-FACTORIZATION', 'D11-C-EC-C-J0-CURRENT',
        'D11-C-EC-C-J0-DERIVATIVE', 'D11-C-EC-C-J0-COVARIANCE')}


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile
    from test_p977_c_rg2b_local import NOMINATED
    p.require(value['schema']=='phase9_exact_profile_local_product_v1'
              and value['iteration_id']=='P9-7.7-C_RG2b-local'
              and value['record_digest']==p.digest_record(value),'C_RG2b local record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()),'C_RG2b local execution source drift')
    p.require(value['authority'] == authority(), 'C_RG2b authority drift or support promotion')
    original=review.read(review.RECORD)
    p.require(value['initial_review_digest']==original['record_digest']==p.digest_record(original),
              'initial reconciliation changed')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_RG2b']
    nomination=seed['initial']['reference']['profile']
    p.require(value['nomination']==nomination and nomination['complete_profile_id']==NOMINATED,'C_RG2b nomination replaced')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=5,failures=[],errors=[],skips=[]),
              'C_RG2b local execution incomplete')
    p.require(value['user_accepted'] is False and value['G2_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support']==[]
              and value['G3_accepted'] is False,'local product overclaim')
    rows=value['fixture_results']; objects=value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==required(),'missing/duplicate local fixture row')
    for key,obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj))==key,'C_RG2b evidence object changed')
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
        if row['result_object'] is not None:
            result=objects[row['result_object']]
            p.require(all(result[k]==row[k] for k in ('committed','operation_disposition','solver_disposition','active_model_identity'))
                      and [r['receipt_id'] for r in result['emitted_receipts']]==row['emitted_receipt_ids']
                      and (None if result['failure'] is None else result['failure']['code'])==row['failure_code'],
                      'result preimage disagrees with coverage row')
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from pygrc.models.grc_v4_rg2b import RG2bCertificate
    from tests.models.test_grc_v4_lifecycle import primitive
    from test_p977_c_rg2b_local import oracle, inverse_oracle
    backend=None
    branch=next(r for r in rows if r['fixture_id']=='RG2B-SECTION')['observation']
    def close(actual,want,label):
        p.require(np.asarray(actual).shape==np.asarray(want).shape and np.allclose(actual,want,rtol=0,atol=2e-13),'RG independent mismatch: '+label)
    def row(case):
        return next(r for r in rows if r['fixture_id']==case)
    p.require(branch['writer_count']==0
              and branch['deterministic_reconstruction'] is True and branch['classical_derivative_rejected'] is True
              and branch['section_scope']=='bounded_completion_relative_Lipschitz_only'
              and branch['global_base_invariance_claimed'] is False and branch['CI_root_claimed'] is False,'RG scope/ownership drift')
    p.require([r['role'] for r in branch['roles']]==['current','reset','restart'],'missing/reordered RG roles')
    endpoint=GeometryStageInputs.from_payload(objects[branch['final_inputs_object']])
    initial=GeometryStageInputs.from_payload(seed['initial'])
    p.require(endpoint.current.Z_4 is None and endpoint.current.W_A is None and endpoint.reset==initial.reset
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
        close(item['current'],expected['current'],'current')
        from tests.models.test_grc_v4_candidate_c import dense_current_oracle
        dense=dense_current_oracle(selected)
        p.require(set(item['chain'])=={'projector','sector','hm','phi','j0','ident','q','current','read'},'missing C chain')
        for name in item['chain']:close(item['chain'][name],dense[name],name)
    current=branch['roles'][0]
    expected=oracle(initial,backend,current['h'])
    for name,want in expected.items(): close(branch['observed'][name],want,name)
    close(endpoint.current.C,expected['final_C'],'endpoint C')
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
    science=('C-POST-CONTINUITY-REDERIVATION','RG2B-SECTION')
    for case in science:
        r=row(case)
        p.require(r['observation']==branch and r['committed'] is True,'shared RG execution inconsistent')
        before,after=(objects[r[k]] for k in ('prestate_object','poststate_object'))
        p.require(before['scientific_state']['authoritative']==primitive(initial.current)
                  and after['scientific_state']['authoritative']==primitive(endpoint.current),'RG measured endpoint replaced')
    validate_candidate(value,initial)
    from verify_p977_c_ci_pc_local import validate_lifecycle
    validate_lifecycle(value,seed)
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
                      and item['writer_count']==0,'RG rollback/write drift')
            stages={'wrong_beat':'admission','reset_native':'pre_read_reconstruction','restart_native':'final_reconstruction','late_publication':None}
            p.require(item['failure_stage']==stages[case],'wrong RG failure stage')
            p.require(item['scope']==('public_operation' if case=='wrong_beat' else 'public_operation_test_fault'),
                      'fault relabeled as native domain pressure')
            request=objects[item['request_object']]
            p.require(request['dt']==initial.dt*(2 if case=='wrong_beat' else 1),'pressure beat changed')
            if case=='late_publication':p.require(item['result_object'] is None,'unexpected exception relabeled as a returned failure')
            else:
                result=objects[item['result_object']]
                p.require(result['committed'] is False
                          and result['emitted_receipts']==[result['failure']['failure_receipt']]
                          and result['failure']['stage']==stages[case],'failure result preimage mismatch')


def validate_candidate(value, initial):
    """Recalculate fixed-stratum C evidence; never differentiate an RG section."""
    from dataclasses import replace
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError, _c_condition
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle, p943_direction, p943_centered
    objects=value['objects'];rows={r['fixture_id']:r for r in value['fixture_results']}
    obs=lambda case:rows[case]['observation']
    inputs=lambda key:GeometryStageInputs.from_payload(objects[key])
    def close(actual,want,label,atol=2e-13,rtol=0):
        p.require(np.asarray(actual).shape==np.asarray(want).shape and np.allclose(actual,want,rtol=rtol,atol=atol),'C retained equation mismatch: '+label)
    base=obs('C-BASELINE-EXACT');subject=inputs(base['stage_inputs_object'])
    p.require(subject==initial,'fixed C stage borrowed')
    point=CandidateCCurrent(subject);a=point.algebra;expected=dense_current_oracle(subject)
    p.require(objects[base['point_object']]==point.to_payload(),'fixed C point changed')
    keys={'projector','sector','hm','phi','j0','ident','q','current','read'}
    p.require(set(base['observed'])==set(base['independent_oracle'])==keys,'incomplete baseline chain')
    for key in keys:
        close(base['observed'][key],expected[key],key);close(base['independent_oracle'][key],expected[key],'oracle '+key)
    for case,row in rows.items():
        if case.startswith('C-') and case!='C-POST-CONTINUITY-REDERIVATION':
            o=row['observation']
            p.require(o['stage_inputs_object']==base['stage_inputs_object'] and o['point_object']==base['point_object']
                      and row['evidence_layer']=='fixed_stage_no_operation','C fixed-stage relabeled')
    o=obs('C-TR-REFERENCE-MAP');changed=inputs(o['changed_h_inputs_object']);cp=CandidateCCurrent(changed)
    p.require(changed.current==subject.current and changed.reset==subject.reset and changed.geometry.reference==subject.geometry.reference
              and o['E_H']==a.transport.structural_hodge_constructor_identity!=o['E_M']==a.transport.mobility_constructor_identity
              and o['mobility_unchanged'] is True and cp.algebra.transport.mobility.diagonal==a.transport.mobility.diagonal
              and cp.algebra.baseline.values!=a.baseline.values,'mobility/Hodge authority transfer')
    close(o['mobility'],np.array(list(subject.geometry.reference.profile.params_resolved.candidate.W_C_tr.values()))*.05,'mobility')
    o=obs('C-SELECTOR-STRICT-GAP');b=np.array(subject.geometry.reference.graph.incidence)
    p.require(o['rank']==a.selector.rank==4 and o['certificate']==dict(a.selector.certificate) and o['cutoff']==100.,'selector changed')
    close(o['spectrum'],np.linalg.eigvalsh(b@np.array(subject.geometry.one_form_hodge.matrix)@b.T),'spectrum')
    o=obs('C-SELECTOR-BOUNDARY');boundary=inputs(o['inputs_object'])
    p.require(boundary.geometry.reference==subject.geometry.reference and boundary.current==subject.current
              and o['scope']=='fixed_stage_selector_rejection_outside_completion_not_public_operation'
              and o['diagnostic']=='domain_failure','boundary scope changed')
    close(boundary.geometry.one_form_hodge.matrix,50*np.eye(3),'boundary H')
    try: CandidateCCurrent(boundary)
    except CandidateCStageError as exc:p.require(exc.disposition=='domain_failure','wrong boundary failure')
    else:raise ValueError('selector boundary admitted')
    o=obs('C-QC-TYPING')
    for key,want in (('I_4M',a.identification),('G_J',a.flat_matrix),('Q_C',a.physical_identification)):close(o[key],want,key)
    o=obs('C-RETAINED-VS-PHYSICAL-CONDITIONING')
    p.require(o['certificates']==[dict(c) for c in a.certificates]
              and o['scope']=='nominated_matrix_certificates_plus_algebra_only_similarity_counterexample'
              and o['counterexample']==dict(retained=[[.5,0],[0,1]],physical=[[.5,5],[0,1]],limit=2,physical_rejected=True),'conditioning scope changed')
    _c_condition(((.5,0),(0,1)),2,'retained')
    try:_c_condition(((.5,5),(0,1)),2,'physical similarity')
    except ValueError:pass
    else:raise ValueError('conditioning counterexample no longer discriminates')
    p.require(obs('C-C-ONLY-AUTHORITY')==dict(stage_inputs_object=base['stage_inputs_object'],point_object=base['point_object'],
        C=list(subject.current.C),W_A=None,Z_4=None,invalid_history_rejected=['W_A','Z_4']),'invented C history')
    def control(case,field,target):
        o=obs(case);c=inputs(o['control_inputs_object']);original=subject.to_payload();modified=c.to_payload()
        wanted=deepcopy(value['nomination']['params_resolved']);wanted['candidate'][field]=target
        p.require(c.geometry.reference.profile.complete_profile_id!=value['nomination']['complete_profile_id']
                  and canonical_json_bytes(c.geometry.reference.profile.params_resolved.to_payload())==canonical_json_bytes(wanted)
                  and o['control_is_nominated_support'] is False,'control nomination/scope changed')
        modified['reference']['profile']=original['reference']['profile']
        p.require(canonical_json_bytes(modified['reference'])==canonical_json_bytes(original['reference']),
                  'control changes reference outside profile')
        # Profile changes rederive the scientific/reset/lifecycle identities.
        p.require(canonical_json_bytes(c.to_payload())==canonical_json_bytes(replace(subject,geometry=c.geometry).to_payload()),
                  'control changes unrelated inputs')
        return o,c
    o,c=control('C-KAPPA-M-ZERO','kappa_M_C',0.)
    close(o['deformation'],np.ones(3),'zero deformation');close(o['retained_hodge'],c.geometry.one_form_hodge.matrix,'zero H')
    close(o['mobility'],a.transport.mobility.diagonal,'zero mobility authority')
    o=obs('C-BASELINE-DERIVATIVE-COVARIANCE');derivatives=o['derivatives']
    p.require(o['scope']=='fixed_candidate_stratum_derivative_not_RG_section_derivative'
              and o['partial_selector_control_not_nominated'] is True and len(derivatives)==2
              and inputs(derivatives[0]['inputs_object'])==subject,'derivative scope drift')
    p.require(CandidateCCurrent(inputs(derivatives[1]['inputs_object'])).algebra.selector.rank==2,'partial-selector control missing')
    for d in derivatives:
        c=inputs(d['inputs_object']);analytic=p943_direction(c,d['dc'],d['dh']);finite=p943_centered(c,d['dc'],d['dh'],d['epsilon'])
        p.require(d['epsilon']==2**-12 and set(d['analytic'])==set(d['finite'])=={'projector','sector','deformation','hm','phi','j0'},'derivative channels missing')
        for key in d['analytic']:
            close(d['analytic'][key],analytic[key],'analytic '+key)
            close(d['finite'][key],finite[key],'finite '+key)
            close(d['analytic'][key],d['finite'][key],'derivative '+key,2e-7,2e-6)
    signed=inputs(o['signed_inputs_object']);d=derivatives[0]
    p.require(signed.current==subject.current and signed.reset==subject.reset
              and signed.geometry.reference.profile==subject.geometry.reference.profile,'signed control authority changed')
    for old,new in zip(subject.geometry.reference.graph.oriented_edges,signed.geometry.reference.graph.oriented_edges,strict=True):
        p.require((old.edge_id,old.tail_node_id,old.head_node_id)==(new.edge_id,new.head_node_id,new.tail_node_id),'not the declared orientation reversal')
    close(o['signed_J0'],dense_current_oracle(signed)['j0'],'signed J0');close(o['signed_J0'],-expected['j0'],'covariant J0')
    close(o['signed_delta_J0'],p943_direction(signed,d['dc'],d['dh'])['j0'],'signed derivative')
    close(o['signed_delta_J0'],-np.array(d['analytic']['j0']),'covariant derivative')
    for case,field,target in (('C-CHI-ZERO','chi_C',0.),('C-ZETA-ZERO','zeta_C',0.),('C-ONE-CHI-GATE','chi_C',.2)):
        o,c=control(case,field,target);want=dense_current_oracle(c)
        p.require(o['control_complete_profile_id']==c.geometry.reference.profile.complete_profile_id,'control identity drift')
        for key,name in (('control_J','current'),('control_J0','j0'),('control_read','read')):close(o[key],want[name],key)
        if target==0:
            close(o['control_J'],o['control_J0'],'zero baseline')
            close(o['zero_section_h'],c.geometry.one_form_hodge.matrix,'zero section')
            close(o['zero_generated_h'],c.geometry.one_form_hodge.matrix,'zero generated')
            endpoint=inputs(o['zero_next_inputs_object'])
            p.require(endpoint.geometry.reference==c.geometry.reference and endpoint.reset==c.reset
                      and endpoint.current.W_A is None and endpoint.current.Z_4 is None
                      and endpoint.step_index==c.step_index+1 and o['fixed_J_chi_ratio'] is None,'zero control endpoint drift')
            close(endpoint.current.C,np.array(c.current.C)-c.dt*b@want['current'],'zero continuity')
        else:
            p.require(o['fixed_J_chi_ratio']==2 and o['zero_next_inputs_object'] is None
                      and o['zero_section_h'] is None and o['zero_generated_h'] is None,'chi gate execution promoted')
            fixed=c.geometry.reference.profile.params_resolved.candidate.chi_C*want['flux_response']@expected['current']
            close(fixed,2*expected['read'],'one external chi')


def initial_predecessor():
    # Reuse the already checked, pinned historical review. Validate its current
    # execution sources; do not rerun the unchanged P9-7.1--7.6 chain.
    from profile_g2_registry import registry, bound_record
    view=registry(p.ROOT)['reconciliation_views']['a_rg2b_local_product']
    prior=bound_record(p.ROOT,dict(path=view['record_path'],record_digest=view['record_digest']))
    original=review.read(review.RECORD)
    p.require(original['record_digest']==p.digest_record(original)==prior['initial_review_digest'],
              'original reconciliation identity changed')
    p.require(p.g2_bindings_match(original['source_bindings'],review.bindings()),'original reconciliation source drift')
    return original


def check(initial_review=None):
    if initial_review is None: initial_review=initial_predecessor()
    value=review.read(RECORD)
    p.require(initial_review['record_digest']==value['initial_review_digest'],'different initial profile review')
    validate(value)
    return dict(status='local_product_verified_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=value['nomination']['complete_profile_id'],test_count=5,verified_local_cells=len(required()),
        remaining_catalog_cases=sorted(set(review.required_cases('C_RG2b'))-set(required())),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,numerical_tests_rerun=0)


def run():
    from test_p977_c_rg2b_local import CRG2bLocalProductTests
    original=initial_predecessor()
    sources=bindings()
    ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'C_RG2b local product tests failed')
    p.require(bindings()==sources,'sources changed during C_RG2b capture')
    seed=review.read(review.SOURCES['lifecycle'])['families']['C_RG2b']
    value=dict(schema='phase9_exact_profile_local_product_v1',iteration_id='P9-7.7-C_RG2b-local',
        captured_at=datetime.now(timezone.utc).isoformat(),initial_review_digest=original['record_digest'],
        source_bindings=sources,nomination=seed['initial']['reference']['profile'],authority=authority(),
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=CRG2bLocalProductTests.rows,objects=CRG2bLocalProductTests.objects,readmission_pressure=CRG2bLocalProductTests.pressure,
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,new_G2_support=[],G3_accepted=False,
        scope='26 local C_RG2b catalog cells; seven crossing cells remain. Control profiles and provisional stages are not additional supported profiles or committed operations; shared executions are not added together.')
    value['record_digest']=p.digest_record(value)
    validate(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
