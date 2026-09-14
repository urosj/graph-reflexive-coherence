"""Exact A_CI+PC crossing reconciliation. --run emits a fresh record to stdout."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_a_ci_pc_local as local

SCRIPT = p.HERE + 'verify_p977_a_ci_pc_crossings.py'
TEST = p.HERE + 'test_p977_a_ci_pc_crossings.py'
RECORD = p.PHASE + 'tranche-7/P9-7.7-A_CI_PC-Crossings.json'
NOMINATED = 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689'
CASES = ['carrier_contract_rejection', 'incoming_C_rejection', 'mapped_event',
         'nonpersistent_incoming', 'nonpersistent_outgoing', 'readmission_control', 'readmission_rejection']


def bindings():
    return {**local.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in
        (SCRIPT, TEST, local.RECORD, review.SOURCES['migration'], review.SOURCES['initializer'], p.HERE+'test_p977_a_ci_crossings.py')}}


def roster():
    from test_p977_a_ci_pc_crossings import ACIPCCrossingTests
    return ['test_p977_a_ci_pc_crossings.ACIPCCrossingTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(ACIPCCrossingTests)]


def authority():
    traces = local.authority()
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT/p.SIDE)
    key = 'P9-EC-A-INITIALIZER-REFERENCE-PASS'
    traces[key] = contract_provenance(context, key)
    return traces


def retained():
    """Project only fields actually present in the old receipt/endpoints."""
    aliases = []
    for origin, key in [('migration', k) for k in ('A_NH_NH', 'A_PC_CIPC', 'A_CIPC_PC', 'A_C_DROP')] + [('initializer', 'A_CI_PC')]:
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
        dict(migration_class='same_candidate_nonhistory_to_nonhistory', disposition='separate_endpoints_not_A_CI_PC; no positive nomination credit', evidence='migration/A_NH_NH'),
        dict(migration_class='same_candidate_nonhistory_to_history', disposition='positive_exact_nomination_target', evidence='nonpersistent_incoming'),
        dict(migration_class='same_candidate_history_to_nonhistory', disposition='positive_exact_nomination_source', evidence='nonpersistent_outgoing'),
        dict(migration_class='PC_to_CI_PC', disposition='positive_exact_nomination_target; exact_carrier_contract_only', evidence='migration/A_PC_CIPC'),
        dict(migration_class='CI_PC_to_PC', disposition='positive_exact_nomination_source; exact_carrier_contract_only', evidence='migration/A_CIPC_PC', negative='carrier_contract_rejection'),
        dict(migration_class='A_to_C', disposition='positive_exact_nomination_source; candidate_and_carrier_explicit_loss', evidence='migration/A_C_DROP'),
        dict(migration_class='C_to_A', disposition='negative_exact_nomination_target; positive initializer target remains a different profile',
             evidence='incoming_C_rejection', separate_positive='initializer/A_CI_PC'),
    ]


def cells():
    maps=['nonpersistent_incoming','nonpersistent_outgoing','migration/A_PC_CIPC','migration/A_CIPC_PC','migration/A_C_DROP']
    return {
        'A-MIGRATION-HISTORY-RECEIPT':maps,
        'RESET-AFTER-MIGRATION':maps,
        'RESET-AFTER-EVENT':['mapped_event'],
        'WHOLE-LIFECYCLE-TUPLE-MAP':['mapped_event'],
        'ALL-MIGRATION-CLASSES':['ordered_migration_matrix'],
        'HISTORY-DISPOSITION':maps+['mapped_event','carrier_contract_rejection'],
        'TARGET-READMISSION-FAILURE':['readmission_control','readmission_rejection'],
    }


def validate_retained_maps():
    """Check literal two-role maps in retained evidence, without rerunning it."""
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry as Reference
    from pygrc.models.grc_v4_migration import carrier_contract
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    cases = review.read(review.SOURCES['migration'])['cases']
    for key in ('A_PC_CIPC','A_CIPC_PC','A_C_DROP'):
        row=cases[key];before,after=row['before'],row['after']
        source=Reference.from_payload(row['initial']['reference'])
        target=Reference.from_payload(row['target_reference'])
        endpoint=target if key=='A_PC_CIPC' else source
        p.require(endpoint.profile.complete_profile_id==NOMINATED,'retained coupled nomination substituted')
        receipt=row['receipts'][0]['identity_payload'];history=receipt['history']
        drop=key=='A_C_DROP'
        p.require(receipt['core']['information_losses']==(['candidate_history_loss','carrier_history_loss'] if drop else [])
                  and history['candidate']['disposition']==('explicit_loss' if drop else 'exact_transport')
                  and history['carrier']['disposition']==('explicit_loss' if drop else 'exact_transport'),'retained history channels changed')
        if not drop:
            p.require(canonical_json_bytes(carrier_contract(source))==canonical_json_bytes(carrier_contract(target)),'carrier contract changed')
        for role in ('scientific_state','reset'):
            a,z=before[role]['authoritative'],after[role]['authoritative']
            p.require(z==dict(C=a['C'],W_A=None if drop else a['W_A'],Z_4=None if drop else a['Z_4']),'retained two-role map changed')
        a,z=before['scientific_state']['authoritative'],before['reset']['authoritative']
        p.require(a['Z_4']!=z['Z_4'] and a['Z_4']!=[0.] and z['Z_4']!=[0.],'vacuous retained history')
        for field in ('time','step_index','Q_target'):
            p.require(before['scientific_state'][field]==after['scientific_state'][field]
                      ==row['reset']['scientific_state'][field],'retained clock/charge changed')


def validate_case(case,row,before,after,request,result,obs,objects):
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry as Reference, GeometryStageInputs
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from pygrc.models.grc_v4_migration import carrier_contract
    from pygrc.models.grc_v4_pc import PCBaseChart
    from tests.models.test_grc_v4_initializer import oracle, target as initializer_target
    from tests.models.test_grc_v4_cipc import independent_root
    def close(a,b,message):
        p.require(np.shape(a)==np.shape(b) and np.allclose(a,b,rtol=0,atol=2e-11),message)
    if not row['committed']:
        p.require(row['failure_code']==result['failure']['code'], 'failure code mismatch')
    if case=='incoming_C_rejection':
        p.require(request['target_profile_id']==obs['failed_target_profile_id']==NOMINATED
                  and before['reference']['profile']['identity_payload']['candidate']=='C'
                  and obs['selected_initializer_profile_id']==initializer_target('A_CI_PC')[0].profile.complete_profile_id
                  and obs['selected_initializer_profile_id']!=NOMINATED
                  and result['failure']['stage']=='admission'
                  and 'initializer source' in result['failure']['message'], 'unselected initializer boundary lost')
        return
    if case in ('nonpersistent_incoming','nonpersistent_outgoing'):
        validate_nonpersistent(case,row,before,after,request,result,obs,objects)
        return
    p.require(row['complete_profile_id']==NOMINATED, 'wrong nominated source')
    target=Reference.from_payload(objects[obs['target_reference_object']])
    p.require(target.profile.complete_profile_id==request['target_profile_id'], 'target reference mismatch')
    if case=='carrier_contract_rejection':
        source=Reference.from_payload(before['reference'])
        original=Reference.from_payload(objects[obs['preserved_target_reference_object']])
        left,right=carrier_contract(original),carrier_contract(target)
        p.require(carrier_contract(source)==left and left!=right and obs['changed_field']=='tau_PC'
                  and obs['unchanged_history_not_silently_reset'] is True
                  and result['failure']['stage']=='admission' and 'exact carrier' in result['failure']['message'],
                  'changed carrier contract boundary lost')
        p.require(original.profile.params_resolved.realization.tau_PC!=target.profile.params_resolved.realization.tau_PC,
                  'carrier contrast missing')
        return
    if case=='mapped_event':
        backend=CandidateADifferentialReference.from_payload(objects[obs['target_backend_object']])
        from test_p977_a_ci_pc_crossings import event_target
        selected,selected_backend=event_target()
        p.require(target==selected and backend==selected_backend and request['target_profile_id']!=NOMINATED,
                  'event initializer declaration substituted')
        p.require(request['resource_transform']['row_major_coefficients']==[0,1,1,0]
                  and request['resource_transform']['target_increment']==[-.125,0], 'event affine map changed')
        for role,key in (('current','scientific_state'),('reset','reset')):
            old,actual=before[key]['authoritative'],after[key]['authoritative']
            expected_C=[float(F(old['C'][1])-F(1,8)),old['C'][0]]
            derived,W=oracle(target,backend,expected_C)
            expect=obs['expectations'][role]
            p.require(actual==dict(C=expected_C,W_A=W,Z_4=[0.]) and old['Z_4']!=[0.]
                      and expect['reference_pass']==derived
                      and actual=={k:expect[k] for k in ('C','W_A','Z_4')}, 'independent event role map mismatch')
            inputs=GeometryStageInputs.from_payload(objects[expect['readmission_inputs_object']])
            p.require(inputs.geometry.reference==target and list(inputs.current.C)==expected_C
                      and list(inputs.current.W_A)==W and list(inputs.current.Z_4)==[0.], 'readmission role substituted')
            h,current,source=independent_root(inputs,backend)
            close(expect['h'],h,'event coupled geometry mismatch')
            close(expect['source'],source,'event same-root source mismatch')
            p.require(expect['source']!=[[0.]] and expect['h']!=[list(v) for v in target.pairings.one_form.matrix], 'zero Z incorrectly erased immediate geometry')
            close(expect['independent_current'],current,'independent event current changed')
            close(expect['current'],current,'event native current mismatch')
        p.require(obs['expectations']['current']['W_A']!=obs['expectations']['reset']['W_A']
                  and before['scientific_state']['authoritative']['Z_4']!=before['reset']['authoritative']['Z_4'],
                  'event reset role collapsed')
        losses=['candidate_history_loss','carrier_history_loss']
        history=result['emitted_receipts'][0]['identity_payload']['history']
        p.require(obs['expected_losses']==losses==result['emitted_receipts'][0]['identity_payload']['core']['information_losses']
                  and history['candidate']['information_loss']==losses[0] and history['carrier']['information_loss']==losses[1]
                  and history['candidate']['disposition']==obs['expected_candidate']=='explicit_loss'
                  and history['carrier']['disposition']==obs['expected_carrier']=='whole_carrier_reset'
                  and obs['source_history_removal_is_not_native_release'] is True, 'event history loss erased/relabelled')
        p.require(after['scientific_state']['Q_target']==obs['expected_Q_target']==float(F(before['scientific_state']['Q_target'])-F(1,8))
                  and obs['missing_archive_rejected'] is True, 'event charge/archive mismatch')
        reset=objects[obs['after_reset_object']]
        p.require(reset['scientific_state']['authoritative']==after['reset']['authoritative']
                  and reset['reset']==after['reset'] and reset['reference']==after['reference']
                  and reset['transition_records']==after['transition_records']
                  and reset['receipt_ledger'][:-4]==after['receipt_ledger']
                  and reset['commit_records'][:-1]==after['commit_records'], 'event reset/ledger mismatch')
        for name in ('time','step_index','Q_target'):
            p.require(reset['scientific_state'][name]==after['scientific_state'][name], 'reset changed time/charge')
        for name in ('time','step_index'):
            p.require(before['scientific_state'][name]==after['scientific_state'][name], 'event changed clock')
        return
    p.require(target.profile.identity_payload.candidate=='C' and target.profile.identity_payload.realization=='CI+PC'
              and target.profile.params_resolved.realization.source_envelope_id==PCBaseChart(3.,1.,1.).identity
              and obs['source_resource_radius']==4. and obs['target_resource_radius']==3., 'reset-only target chart changed')
    norms={key:sum(x*x for x in before[key]['authoritative']['C']) for key in ('scientific_state','reset')}
    p.require(obs['source_current_norm_squared']==norms['scientific_state']<=9
              and obs['source_reset_norm_squared']==norms['reset']<=16, 'source resource contrast changed')
    if case=='readmission_rejection':
        p.require(norms['reset']>9 and result['failure']['stage']=='target_readmission', 'not reset-only readmission rejection')
    else:
        p.require(norms['reset']<=9, 'control reset not admissible')
        for key in ('scientific_state','reset'):
            p.require(after[key]['authoritative']==dict(C=before[key]['authoritative']['C'],W_A=None,Z_4=[0.]), 'control role map mismatch')
        receipt=result['emitted_receipts'][0]['identity_payload']
        p.require(receipt['core']['information_losses']==['candidate_history_loss','carrier_history_loss']
                  and receipt['history']['carrier']['disposition']=='whole_carrier_reset', 'control loss channels changed')


def validate_nonpersistent(case,row,before,after,request,result,obs,objects):
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from tests.models.test_grc_v4_migration import fixture
    from tests.models.test_grc_v4_ci import independent_root as ci_root
    from tests.models.test_grc_v4_cipc import independent_root as coupled_root
    incoming=case=='nonpersistent_incoming'
    source_family,target_family=('A_CI','A_CI_PC') if incoming else ('A_CI_PC','A_CI')
    source,_=fixture(source_family);target_inputs,backend=fixture(target_family)
    target=GRCV4ReferenceGeometry.from_payload(objects[obs['target_reference_object']])
    p.require(before['reference']==source.geometry.reference.to_payload()
              and target==target_inputs.geometry.reference
              and after['reference']==target.to_payload()
              and request['target_profile_id']==target.profile.complete_profile_id
              and CandidateADifferentialReference.from_payload(objects[obs['target_backend_object']])==backend,
              'nonpersistent ordered endpoint substituted')
    p.require((row['target_active_model_identity'] if incoming else row['complete_profile_id'])==NOMINATED,
              'nonpersistent crossing does not involve nomination')
    losses=[] if incoming else ['carrier_history_loss']
    receipt=result['emitted_receipts'][0]['identity_payload'];history=receipt['history']
    p.require(obs['expected_losses']==receipt['core']['information_losses']==losses
              and history['candidate']['disposition']=='exact_transport'
              and history['carrier']['disposition']==('target_initializer' if incoming else 'explicit_loss')
              and obs['exact_replay'] is True,'nonpersistent history/reset semantics changed')
    for role,key in (('current','scientific_state'),('reset','reset')):
        old,actual=before[key]['authoritative'],after[key]['authoritative'];expected=obs['expectations'][role]
        p.require(actual==dict(C=old['C'],W_A=old['W_A'],Z_4=[0.] if incoming else None)
                  and actual=={k:expected[k] for k in ('C','W_A','Z_4')}
                  and (old['Z_4'] is None if incoming else old['Z_4'] not in (None,[0.])),
                  'nonpersistent two-role map changed')
        inputs=GeometryStageInputs.from_payload(objects[expected['readmission_inputs_object']])
        p.require(inputs.geometry.reference==target and inputs.to_payload()['current']==actual,
                  'nonpersistent readmission role borrowed')
        if incoming:h,j,_=coupled_root(inputs,backend)
        else:j,h=ci_root(inputs,backend)
        for field,value in (('h',h),('current',j)):
            p.require(np.shape(expected[field])==np.shape(value)
                      and np.allclose(expected[field],value,rtol=0,atol=2e-11),'nonpersistent independent '+field)
    p.require(before['scientific_state']['authoritative']!=before['reset']['authoritative'],
              'nonpersistent reset role collapsed')
    reset=objects[obs['after_reset_object']]
    p.require(reset['scientific_state']['authoritative']==after['reset']['authoritative']
              and reset['reset']==after['reset'] and reset['reference']==after['reference']
              and reset['transition_records']==after['transition_records']
              and reset['receipt_ledger'][:-4]==after['receipt_ledger']
              and reset['commit_records'][:-1]==after['commit_records'],'nonpersistent reset ownership changed')
    for field in ('time','step_index','Q_target'):
        p.require(before['scientific_state'][field]==after['scientific_state'][field]
                  ==reset['scientific_state'][field],'nonpersistent clock/charge changed')


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    p.require(value['schema'] == 'phase9_exact_profile_crossing_reconciliation_v1'
              and value['iteration_id'] == 'P9-7.7-A_CI_PC-crossings'
              and value['record_digest'] == p.digest_record(value), 'crossing record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'crossing source drift')
    p.require(value['authority'] == authority(), 'crossing authority drift or promotion')
    p.require(value['nomination'] == review.read(local.RECORD)['nomination']
              and value['local_record_digest'] == review.read(local.RECORD)['record_digest'], 'nomination/local record drift')
    p.require(value['results'] == dict(tests_run=4, failures=[], errors=[], skips=[])
              and value['test_ids'] == roster(), 'crossing execution incomplete')
    for name in ('user_accepted', 'aggregate_closed', 'G2_accepted', 'G3_accepted', 'all_ordered_pairs_verified'):
        p.require(value[name] is False, 'crossing scope or acceptance promoted')
    p.require(value['new_G2_support'] == [] and value['retained_aliases'] == retained()
              and value['ordered_migration_matrix'] == matrix() and value['catalog_cells'] == cells(), 'crossing reconciliation changed')
    p.require(set(cells()) == set(review.required_cases('A_CI_PC')) - set(local.required()), 'crossing catalog drift')
    rows, objects = value['fixture_results'], value['objects']
    p.require(sorted(r['fixture_id'] for r in rows) == CASES, 'missing/duplicate crossing row')
    for key, obj in objects.items():
        p.require(p.sha(canonical_json_bytes(obj)) == key, 'crossing preimage drift')
    required = set(review.read(review.CATALOG)['execution_contract']['required_result_fields'])
    for row in rows:
        p.require(required <= set(row) and row['nominated_complete_profile_id'] == NOMINATED, 'missing result/nomination fields')
        before, after = [objects[row[k]] for k in ('prestate_object', 'poststate_object')]
        profile = before['reference']['profile']
        request, result = [objects[row[k]] for k in ('request_object', 'result_object')]
        p.require(row['complete_profile_id'] == row['active_model_identity'] == profile['complete_profile_id']
                  == before['scientific_state']['active_model_identity']
                  and row['resolved_params_id'] == profile['identity_payload']['params_hash'], 'borrowed source identity')
        p.require(row['prestate_digest'] == before['scientific_state_digest'] == request['source_state_digest']
                  and row['poststate_digest'] == after['scientific_state_digest']
                  and row['target_active_model_identity'] == after['scientific_state']['active_model_identity'], 'incorrect operation endpoints')
        for name in ('committed', 'operation_disposition', 'solver_disposition'):
            p.require(row[name] == result.get(name), 'result disposition differs from preimage')
        p.require(row['emitted_receipt_ids'] == [r['receipt_id'] for r in result['emitted_receipts']], 'result receipt delta drift')
        obs = row['observation']
        if row['committed']:
            p.require(request['target_profile_id'] == row['target_active_model_identity'], 'target identity substituted')
            p.require(after['receipt_ledger'] == before['receipt_ledger'] + result['emitted_receipts'], 'persistent ledger is not emitted delta')
        else:
            p.require(before == after and result['commit_id'] is None and len(result['emitted_receipts']) == 1
                      and result['failure']['stage'] == obs['failure_stage'], 'failed crossing changed publication')
        case = row['fixture_id']
        p.require(row['committed'] == (case in ('mapped_event','readmission_control','nonpersistent_incoming','nonpersistent_outgoing')), 'positive/negative crossing relabeled')
        validate_case(case,row,before,after,request,result,obs,objects)
    validate_retained_maps()
    by_id = {r['fixture_id']:r for r in rows}
    good,bad = [objects[by_id[k]['prestate_object']] for k in ('readmission_control','readmission_rejection')]
    p.require(good['reference']==bad['reference'] and good['scientific_state']['authoritative']==bad['scientific_state']['authoritative']
              and good['reset']['authoritative']==good['scientific_state']['authoritative']
              and bad['reset']['authoritative']!=bad['scientific_state']['authoritative'], 'not a reset-only contrast')
    p.require(objects[by_id['readmission_control']['request_object']]['target_profile_id']
              ==objects[by_id['readmission_rejection']['request_object']]['target_profile_id'], 'readmission targets differ')


def check(local_product=None):
    local_product = local.check() if local_product is None else local_product
    value = review.read(RECORD)
    p.require(local_product['record_digest'] == value['local_record_digest'], 'wrong local predecessor')
    validate(value)
    return dict(status='crossings_reconciled_pending_review', record_path=RECORD, record_digest=value['record_digest'],
        complete_profile_id=NOMINATED, test_count=4, new_execution_cases=7, retained_alias_count=5,
        reconciled_crossing_cells=7, local_cells=21, ordered_migration_classes=7,
        matrix_scope='exact_CI_PC_nonpersistent_pairs_and_retained_PC_pairs; separate_initializer_target; not_all_pairs',
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        new_G2_support=[], all_ordered_pairs_verified=False, numerical_tests_rerun=0)


def run():
    from test_p977_a_ci_pc_crossings import ACIPCCrossingTests
    # The shared status path checks full ancestry once; capture checks the
    # exact local preimages/equations without replaying the old review chain.
    predecessor = local.check(initial_review={'record_digest':review.read(review.RECORD)['record_digest']})
    before = bindings()
    ids = roster()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'crossing execution failed')
    p.require(before == bindings(), 'sources changed during crossing capture')
    value = dict(schema='phase9_exact_profile_crossing_reconciliation_v1', iteration_id='P9-7.7-A_CI_PC-crossings',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=before,
        nomination=review.read(local.RECORD)['nomination'], local_record_digest=predecessor['record_digest'],
        test_ids=ids, results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        fixture_results=ACIPCCrossingTests.rows, objects=ACIPCCrossingTests.objects,
        retained_aliases=retained(), ordered_migration_matrix=matrix(), catalog_cells=cells(), authority=authority(),
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n) for n in ('numpy', 'jsonschema', 'rfc8785')}),
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        all_ordered_pairs_verified=False, new_G2_support=[])
    value['record_digest'] = p.digest_record(value)
    validate(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), separators=(',', ':')))
