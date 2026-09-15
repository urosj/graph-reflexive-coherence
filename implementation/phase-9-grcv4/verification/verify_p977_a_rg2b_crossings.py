"""Exact A_RG2b crossing reconciliation. --run emits a fresh record to stdout."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_a_rg2b_local as local

SCRIPT = p.HERE + 'verify_p977_a_rg2b_crossings.py'
TEST = p.HERE + 'test_p977_a_rg2b_crossings.py'
RECORD = p.PHASE + 'tranche-7/P9-7.7-A_RG2b-Crossings.json'
NOMINATED = 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'
from test_p977_a_rg2b_crossings import MIGRATIONS
CASES = sorted([*MIGRATIONS,'mapped_event','readmission_control','readmission_rejection',
                'core_only_admission','incoming_C_rejection'])


def bindings():
    return {**local.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in
        (SCRIPT, TEST, local.RECORD, review.SOURCES['migration'], review.SOURCES['initializer'],
         p.HERE+'test_p977_a_ci_crossings.py',p.HERE+'verify_p977_c_ci_pc_crossings.py',
         'specs/grc-v4-a-initializer-spec.md','specs/grc-v4-topology-event-spec.md')}}


def roster():
    from test_p977_a_rg2b_crossings import ARG2bCrossingTests
    return ['test_p977_a_rg2b_crossings.ARG2bCrossingTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(ARG2bCrossingTests)]


def authority():
    traces = local.authority()
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    for key in ('P9-EC-A-INITIALIZER-REFERENCE-PASS','D11-C-EC-C-J0-CURRENT'):
        traces[key] = contract_provenance(context, key)
    return traces


def retained():
    """Project only fields actually present in the old receipt/endpoints."""
    aliases = []
    for origin, key in [('migration', k) for k in ('A_PC_NH', 'A_PC_CIPC', 'A_CIPC_PC')] + [('initializer', 'A_RG2b')]:
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
        dict(migration_class='same_candidate_nonhistory_to_nonhistory',disposition='positive_exact_nomination_target',evidence='nonpersistent_incoming'),
        dict(migration_class='same_candidate_nonhistory_to_history',disposition='positive_exact_nomination_source',evidence='persistent_outgoing'),
        dict(migration_class='same_candidate_history_to_nonhistory',disposition='positive_exact_nomination_target',evidence='persistent_incoming'),
        dict(migration_class='PC_to_CI_PC',disposition='separate_PC_pair_not_nomination_execution',evidence='migration/A_PC_CIPC'),
        dict(migration_class='CI_PC_to_PC',disposition='separate_PC_pair_not_nomination_execution',evidence='migration/A_CIPC_PC'),
        dict(migration_class='A_to_C',disposition='positive_exact_nomination_source',evidence='candidate_outgoing'),
        dict(migration_class='C_to_A',disposition='negative_exact_nomination_target; positive_initializer_is_separate_scalar_target',
             evidence='incoming_C_rejection',separate_positive='initializer/A_RG2b'),
    ]


def cells():
    return {
        'A-MIGRATION-HISTORY-RECEIPT':list(MIGRATIONS),
        'RESET-AFTER-MIGRATION':[*MIGRATIONS,'core_only_admission'],
        'RESET-AFTER-EVENT':['mapped_event'],
        'WHOLE-LIFECYCLE-TUPLE-MAP':['mapped_event'],
        'ALL-MIGRATION-CLASSES':['ordered_migration_matrix'],
        'HISTORY-DISPOSITION':[*MIGRATIONS,'mapped_event'],
        'TARGET-READMISSION-FAILURE':['readmission_control','readmission_rejection','core_only_admission'],
    }


def local_predecessor():
    # The local product already pinned and checked the original predecessor
    # chain. Verify its current record, equations and source bindings, without
    # replaying the entire unchanged chain for each crossing invocation.
    from profile_g2_registry import registry, bound_record
    view=registry(p.ROOT)['reconciliation_views']['a_rg2b_local_product']
    value=bound_record(p.ROOT,dict(path=local.RECORD,record_digest=view['record_digest']))
    return local.check(initial_review={'record_digest':value['initial_review_digest']})


def validate(value):
    from fractions import Fraction as F
    from dataclasses import replace
    import numpy as np
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_rg2b import RG2bCertificate
    from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
    from tests.models.test_grc_v4_ci import independent_point
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle
    from tests.models.test_grc_v4_initializer import oracle as initializer_oracle
    from tests.models.test_grc_v4_lifecycle import primitive
    from test_p977_a_rg2b_local import inverse_oracle
    from test_p977_a_rg2b_crossings import companion, event_target
    from verify_p977_c_ci_pc_crossings import validate_reset
    p.require(value['schema']=='phase9_exact_profile_crossing_reconciliation_v1'
              and value['iteration_id']=='P9-7.7-A_RG2b-crossings'
              and value['record_digest']==p.digest_record(value),'crossing record drift')
    p.require(p.g2_bindings_match(value['source_bindings'],bindings()),'crossing source drift')
    p.require(value['authority']==authority(),'crossing authority promotion/drift')
    local_record=review.read(local.RECORD)
    p.require(value['nomination']==local_record['nomination'] and value['local_record_digest']==local_record['record_digest']
              ==p.digest_record(local_record),'local nomination drift')
    p.require(value['test_ids']==roster() and value['results']==dict(tests_run=3,failures=[],errors=[],skips=[]),'crossing run incomplete')
    for name in ('user_accepted','aggregate_closed','G2_accepted','G3_accepted','all_ordered_pairs_verified'):
        p.require(value[name] is False,'crossing scope promoted')
    p.require(value['new_G2_support']==[] and value['retained_aliases']==retained()
              and value['ordered_migration_matrix']==matrix() and value['catalog_cells']==cells(),'crossing applicability drift')
    p.require(all(a['evidence_scope']=='separate_ordered_endpoints_not_nomination_execution' for a in value['retained_aliases']),
              'old scalar endpoints borrowed graph nomination credit')
    p.require(set(cells())==set(review.required_cases('A_RG2b'))-set(local.required()),'crossing cells mismatch')
    rows,objects=value['fixture_results'],value['objects']
    p.require(sorted(r['fixture_id'] for r in rows)==CASES,'missing/duplicate crossing case')
    for key,obj in objects.items(): p.require(key==p.sha(canonical_json_bytes(obj)),'crossing object drift')
    required=set(review.read(review.CATALOG)['execution_contract']['required_result_fields'])
    def close(actual,expected,label):
        p.require(np.allclose(actual,expected,rtol=0,atol=2e-12),'independent crossing mismatch: '+label)
    for row in rows:
        p.require(required<=set(row) and row['nominated_complete_profile_id']==NOMINATED,'crossing fields/nomination')
        case=row['fixture_id'];obs=row['observation']
        before,after=[objects[row[k]] for k in ('prestate_object','poststate_object')]
        request,result=[objects[row[k]] for k in ('request_object','result_object')]
        profile=before['reference']['profile']
        p.require(row['active_model_identity']==row['complete_profile_id']==profile['complete_profile_id']
                  ==before['scientific_state']['active_model_identity']
                  and row['resolved_params_id']==profile['identity_payload']['params_hash'],'borrowed source')
        p.require(row['prestate_digest']==before['scientific_state_digest']==request['source_state_digest']
                  and row['poststate_digest']==after['scientific_state_digest']
                  and row['target_active_model_identity']==after['scientific_state']['active_model_identity'],'endpoint drift')
        for name in ('committed','operation_disposition','solver_disposition'):
            p.require(row[name]==result.get(name),'result preimage mismatch')
        p.require(row['emitted_receipt_ids']==[r['receipt_id'] for r in result['emitted_receipts']],'receipt delta changed')
        p.require(row['committed']==(case not in ('readmission_rejection','incoming_C_rejection')),'positive/negative relabel')
        if row['committed']:
            p.require(request['target_profile_id']==row['target_active_model_identity']
                      and after['receipt_ledger']==before['receipt_ledger']+result['emitted_receipts'],'target/ledger drift')
        else:
            p.require(before==after and result['commit_id'] is None and len(result['emitted_receipts'])==1
                      and result['failure']['stage']==obs['failure_stage'],'failure publication drift')
        if case in MIGRATIONS or case=='mapped_event':
            target=GRCV4ReferenceGeometry.from_payload(objects[obs['target_reference_object']])
            backend=None if obs['target_backend_object'] is None else CandidateADifferentialReference.from_payload(objects[obs['target_backend_object']])
            p.require(target.to_payload()==after['reference'],'target reference replaced')
            p.require(obs['both_roles_admitted_before_publication'] is True and obs['ordinary_writer_count']==0,'crossing admission/writer drift')
            history=result['emitted_receipts'][0]['identity_payload']
            if case in MIGRATIONS:
                source_family,target_family,candidate,carrier,losses=MIGRATIONS[case]
                p.require(profile['complete_profile_id']==companion(source_family)[0].geometry.reference.profile.complete_profile_id
                          and target==companion(target_family)[0].geometry.reference,'wrong concrete migration endpoints')
                p.require(obs['exact_replay'] is True,'migration replay missing')
            else:
                p.require(profile['complete_profile_id']==NOMINATED and target==event_target()[0]
                          and target.profile.complete_profile_id!=NOMINATED,'event target replaced')
                candidate,carrier,losses='explicit_loss','not_applicable',['candidate_history_loss']
                p.require(obs['initializer_is_separate_target'] is True and obs['missing_archive_rejected'] is True
                          and obs['duplicate_unchanged_after_reset'] is True
                          and obs['map_scope']=='one_affine_renamed_graph_not_GRC9','event scope/archive drift')
                transform=request['resource_transform']
                p.require(transform['row_major_coefficients']==[int(j==3-i) for i in range(4) for j in range(4)]
                          and transform['target_increment']==[1/128,0,0,0],'wrong graph affine map')
            p.require(obs['expected_candidate']==history['history']['candidate']['disposition']==candidate
                      and obs['expected_carrier']==history['history']['carrier']['disposition']==carrier
                      and obs['expected_losses']==history['core']['information_losses']==losses,'history/loss drift')
            for role,key in (('current','scientific_state'),('reset','reset')):
                old=before[key]['authoritative'];actual=after[key]['authoritative'];expected=obs['expectations'][role]
                if case in MIGRATIONS:
                    C=old['C'];W=old['W_A'] if target.profile.identity_payload.candidate=='A' else None
                    Z=[0.]*9 if case=='persistent_outgoing' else None
                else:
                    C=[float(F(old['C'][3-i])+(F(1,128) if i==0 else 0)) for i in range(4)]
                    reference,W=initializer_oracle(target,backend,C);Z=None
                    p.require(expected['reference_pass']==reference,'initializer reference pass drift')
                p.require(actual==dict(C=C,W_A=W,Z_4=Z)=={k:expected[k] for k in ('C','W_A','Z_4')},'literal history/resource map drift')
                evidence=expected['readmission']
                inputs=GeometryStageInputs.from_payload(objects[evidence['inputs_object']])
                p.require(inputs.geometry.reference==target and primitive(inputs.current)==actual
                          and primitive(inputs.reset)==after['reset']['authoritative'] and inputs.dt==0,'readmission role/duration drift')
                close(evidence['h'],inputs.geometry.one_form_hodge.matrix,'selected h')
                current,_=independent_point(inputs,backend,np.array(evidence['h']))
                close(evidence['current'],current,'current')
                if backend is None:close(evidence['baseline'],dense_current_oracle(inputs)['j0'],'C baseline')
                if target.profile.identity_payload.realization=='RG2b':
                    section=GeometryStageInputs.from_payload(objects[evidence['section_inputs_object']])
                    p.require(section.geometry.reference==target and section.current==inputs.current
                              and section.reset==inputs.reset and section.dt==0 and inputs.stage=='rg2b_section','section role drift')
                    d=RG2bGraphDomain.from_identity(target.profile.params_resolved.realization.extension_evaluator_id)
                    p.require(evidence['frozen_beat']==d.beat_dt and evidence['regularity']=='Lipschitz_only','completion or C1 promotion')
                    cert=RG2bCertificate(section,backend)
                    p.require(evidence['certificate']==dict(cert.bounds),'section certificate drift')
                    b={k:F(v) for k,v in evidence['certificate'].items()}
                    p.require(0<=b['contraction_upper']<1 and 0<=F(evidence['error_upper'])<=F(target.profile.params_resolved.realization.error_tolerance)
                              and 1<=evidence['evaluations']<=target.profile.params_resolved.realization.iteration_limit,'uncertified section')
                    oracle_h=inverse_oracle(replace(section,dt=d.beat_dt),backend)
                    close(evidence['inverse_oracle_h'],oracle_h,'independent inverse')
                    allowance=float(F(evidence['error_upper'])+b['section_radius']*b['contraction_upper']**2)+2e-15
                    p.require(np.linalg.norm(np.array(evidence['h'])-oracle_h)<=allowance,'section outside inverse error')
            for name in ('time','step_index'):p.require(before['scientific_state'][name]==after['scientific_state'][name],'crossing clock change')
            q=float(F(before['scientific_state']['Q_target'])+(F(1,128) if case=='mapped_event' else 0))
            p.require(after['scientific_state']['Q_target']==q,'crossing charge change')
            if case=='mapped_event':p.require(obs['expected_Q_target']==q,'event charge claim drift')
            if case=='persistent_incoming':
                a,b=before['scientific_state']['authoritative'],before['reset']['authoritative']
                p.require(a['Z_4']!=b['Z_4'] and any(a['Z_4']) and any(b['Z_4']),'vacuous carrier loss')
            validate_reset(obs,objects,after)
        elif case=='incoming_C_rejection':
            p.require(request['target_profile_id']==NOMINATED and obs['selected_initializer_profile_id']!=NOMINATED
                      and obs['failure_stage']=='admission' and 'initializer source' in result['failure']['message']
                      and obs['scope']=='negative_nomination_target_not_positive_C_to_A','incoming initializer relabel')
        else:
            p.require(request['target_profile_id']==NOMINATED and profile['complete_profile_id']==companion('A_OS')[0].geometry.reference.profile.complete_profile_id,
                      'reset-only endpoints changed')
            if case=='readmission_rejection':
                p.require(obs['reset_W']==2.3125 and result['failure']['stage']=='target_readmission'
                          and 'outside K' in result['failure']['message'],'not native target K rejection')
            elif case=='core_only_admission':
                p.require(obs['reset_W']==2.1875 and obs['state_readmission_is_not_ordinary_entry'] is True
                          and obs['ordinary_entry_rejected_durations']==[0.,companion('A_RG2b')[0].dt]
                          and after['reset']['authoritative']['W_A']==[2.1875]*3,'K versus K_minus boundary collapsed')
                validate_reset(obs,objects,after)
            else:p.require(obs['reset_W'] is None,'readmission control changed')
    by_id={r['fixture_id']:r for r in rows}
    good,bad=[objects[by_id[k]['prestate_object']] for k in ('readmission_control','readmission_rejection')]
    p.require(good['reference']==bad['reference'] and good['scientific_state']['authoritative']==bad['scientific_state']['authoritative']
              and good['reset']['authoritative']==good['scientific_state']['authoritative']
              and bad['reset']['authoritative']['W_A']==[2.3125]*3,'not a reset-only contrast')


def check(local_product=None):
    local_product=local_predecessor() if local_product is None else local_product
    value=review.read(RECORD)
    p.require(local_product['record_digest']==value['local_record_digest'],'wrong local predecessor')
    validate(value)
    return dict(status='crossings_reconciled_pending_review',record_path=RECORD,record_digest=value['record_digest'],
        complete_profile_id=NOMINATED,test_count=3,new_execution_cases=9,retained_alias_count=4,
        reconciled_crossing_cells=7,local_cells=21,ordered_migration_classes=7,
        matrix_scope='exact_graph_positive_and_negative_endpoints; scalar_PC_pairs_and_initializer_separate; not_all_pairs',
        user_accepted=False,aggregate_closed=False,G2_accepted=False,G3_accepted=False,
        new_G2_support=[],all_ordered_pairs_verified=False,numerical_tests_rerun=0)


def run():
    from test_p977_a_rg2b_crossings import ARG2bCrossingTests
    predecessor=local_predecessor();before=bindings();ids=roster()
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped,'crossing execution failed')
    p.require(before==bindings(),'sources changed during crossing capture')
    value=dict(schema='phase9_exact_profile_crossing_reconciliation_v1',iteration_id='P9-7.7-A_RG2b-crossings',
        captured_at=datetime.now(timezone.utc).isoformat(),source_bindings=before,
        nomination=review.read(local.RECORD)['nomination'],local_record_digest=predecessor['record_digest'],
        test_ids=ids,results=dict(tests_run=result.testsRun,failures=[],errors=[],skips=[]),
        fixture_results=ARG2bCrossingTests.rows,objects=ARG2bCrossingTests.objects,
        retained_aliases=retained(),ordered_migration_matrix=matrix(),catalog_cells=cells(),authority=authority(),
        environment=dict(python=platform.python_version(),dependencies={n:importlib.metadata.version(n) for n in ('numpy','jsonschema','rfc8785')}),
        user_accepted=False,aggregate_closed=False,G2_accepted=False,G3_accepted=False,all_ordered_pairs_verified=False,new_G2_support=[])
    value['record_digest']=p.digest_record(value);validate(value);return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(),indent=2))
