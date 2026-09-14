"""Exact C_CI crossing reconciliation. --run emits a fresh record to stdout."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_c_ci_local as local

SCRIPT = p.HERE + 'verify_p977_c_ci_crossings.py'
TEST = p.HERE + 'test_p977_c_ci_crossings.py'
RECORD = p.PHASE + 'tranche-7/P9-7.7-C_CI-Crossings.json'
NOMINATED = 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e'
CASES = ['C_to_A', 'mapped_event', 'persistent_C_PC', 'readmission_control', 'readmission_rejection']


def bindings():
    return {**local.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in
        (SCRIPT, TEST, local.RECORD, review.SOURCES['migration'], review.SOURCES['initializer'])}}


def roster():
    from test_p977_c_ci_crossings import CCICrossingTests
    return ['test_p977_c_ci_crossings.CCICrossingTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(CCICrossingTests)]


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
    for origin, key in [('migration', k) for k in ('C_NH_NH', 'C_NH_PC', 'C_PC_CIPC', 'C_CIPC_PC', 'A_C_DROP')]:
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
        dict(migration_class='same_candidate_nonhistory_to_nonhistory', disposition='positive_exact_nomination_target', evidence='migration/C_NH_NH'),
        dict(migration_class='same_candidate_nonhistory_to_history', disposition='positive_exact_nomination_source', evidence='migration/C_NH_PC'),
        dict(migration_class='same_candidate_history_to_nonhistory', disposition='positive_exact_nomination_target', evidence='persistent_C_PC'),
        dict(migration_class='PC_to_CI_PC', disposition='separate_endpoints_not_C_CI; no positive nomination credit', evidence='migration/C_PC_CIPC'),
        dict(migration_class='CI_PC_to_PC', disposition='separate_endpoints_not_C_CI; no positive nomination credit', evidence='migration/C_CIPC_PC'),
        dict(migration_class='A_to_C', disposition='positive_exact_nomination_target; candidate_and_carrier_loss', evidence='migration/A_C_DROP'),
        dict(migration_class='C_to_A', disposition='positive_exact_nomination_source; separately_declared_initializer_target', evidence='C_to_A'),
    ]


def cells():
    return {
        'C-LIFECYCLE-REFERENCE-MAP': ['migration/C_NH_NH', 'migration/A_C_DROP', 'persistent_C_PC', 'mapped_event'],
        'RESET-AFTER-MIGRATION': ['migration/C_NH_NH', 'migration/C_NH_PC', 'persistent_C_PC', 'C_to_A', 'migration/A_C_DROP'],
        'RESET-AFTER-EVENT': ['mapped_event'],
        'WHOLE-LIFECYCLE-TUPLE-MAP': ['mapped_event'],
        'ALL-MIGRATION-CLASSES': ['ordered_migration_matrix'],
        'HISTORY-DISPOSITION': ['migration/A_C_DROP', 'migration/C_NH_PC', 'persistent_C_PC', 'C_to_A', 'mapped_event'],
        'TARGET-READMISSION-FAILURE': ['readmission_control', 'readmission_rejection'],
    }


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    p.require(value['schema'] == 'phase9_exact_profile_crossing_reconciliation_v1'
              and value['iteration_id'] == 'P9-7.7-C_CI-crossings'
              and value['record_digest'] == p.digest_record(value), 'crossing record drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'crossing source drift')
    p.require(value['authority'] == authority(), 'crossing authority drift or promotion')
    p.require(value['nomination'] == review.read(local.RECORD)['nomination']
              and value['local_record_digest'] == review.read(local.RECORD)['record_digest'], 'nomination/local record drift')
    p.require(value['results'] == dict(tests_run=3, failures=[], errors=[], skips=[])
              and value['test_ids'] == roster(), 'crossing execution incomplete')
    for name in ('user_accepted', 'aggregate_closed', 'G2_accepted', 'G3_accepted', 'all_ordered_pairs_verified'):
        p.require(value[name] is False, 'crossing scope or acceptance promoted')
    p.require(value['new_G2_support'] == [] and value['retained_aliases'] == retained()
              and value['ordered_migration_matrix'] == matrix() and value['catalog_cells'] == cells(), 'crossing reconciliation changed')
    p.require(set(cells()) == set(review.required_cases('C_CI')) - set(local.required()), 'crossing catalog drift')
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
        p.require(row['committed'] == (case != 'readmission_rejection'), 'positive/negative crossing relabeled')
        validate_case(case,row,before,after,request,result,obs,objects)

    by_id = {r['fixture_id']: r for r in rows}
    good, bad = [objects[by_id[k]['prestate_object']] for k in ('readmission_control', 'readmission_rejection')]
    p.require(good['reference'] == bad['reference'] and good['scientific_state']['authoritative'] == bad['scientific_state']['authoritative']
              and good['reset']['authoritative'] == good['scientific_state']['authoritative']
              and bad['reset']['authoritative'] != bad['scientific_state']['authoritative'], 'not a reset-only contrast')
    p.require(objects[by_id['readmission_control']['request_object']]['target_profile_id']
              == objects[by_id['readmission_rejection']['request_object']]['target_profile_id'], 'readmission targets differ')


def validate_case(case,row,before,after,request,result,obs,objects):
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GeometryStageInputs,GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle
    from tests.models.test_grc_v4_initializer import oracle as initializer_oracle
    target=GRCV4ReferenceGeometry.from_payload(objects[obs['target_reference_object']])
    p.require(target.profile.complete_profile_id==request['target_profile_id'],'target preimage drift')
    if row['committed']:
        p.require(after['reference']==target.to_payload(),'published target reference differs')
    if case in ('readmission_control','readmission_rejection'):
        p.require(row['complete_profile_id']==NOMINATED,'borrowed failure source')
        if case=='readmission_rejection':
            p.require(result['failure']['stage']=='target_readmission' and 'resource' in result['failure']['message'],
                      'not a numerical resource readmission failure')
        return
    history=result['emitted_receipts'][0]['identity_payload']['history']
    candidate,carrier,losses={
        'persistent_C_PC':('rederived','explicit_loss',['carrier_history_loss']),
        'C_to_A':('target_initializer','not_applicable',[]),
        'mapped_event':('rederived','not_applicable',[]),
    }[case]
    p.require(obs['expected_candidate']==history['candidate']['disposition']==candidate
              and obs['expected_carrier']==history['carrier']['disposition']==carrier
              and obs['expected_losses']==result['emitted_receipts'][0]['identity_payload']['core']['information_losses']==losses,
              'history channels/loss changed')
    reset=objects[obs['after_reset_object']]
    p.require(reset['scientific_state']['authoritative']==after['reset']['authoritative']
              and reset['reset']==after['reset'] and reset['reference']==after['reference']
              and reset['transition_records']==after['transition_records']
              and reset['receipt_ledger'][:-4]==after['receipt_ledger']
              and reset['commit_records'][:-1]==after['commit_records'] and obs['exact_replay'] is True,
              'reset/archive/replay scope changed')
    for name in ('time','step_index','Q_target'):
        p.require(reset['scientific_state'][name]==after['scientific_state'][name],'reset clock/charge changed')
    for name in ('time','step_index'):
        p.require(before['scientific_state'][name]==after['scientific_state'][name],'crossing changed clock')
    p.require(NOMINATED==(request['target_profile_id'] if case=='persistent_C_PC' else row['complete_profile_id']),
              'wrong exact nomination endpoint')
    backend=None if obs.get('target_backend_object') is None else CandidateADifferentialReference.from_payload(objects[obs['target_backend_object']])
    for role,old,actual in (('current',before['scientific_state']['authoritative'],after['scientific_state']['authoritative']),
                            ('reset',before['reset']['authoritative'],after['reset']['authoritative'])):
        expected=obs['expectations'][role]
        p.require(actual=={k:expected[k] for k in ('C','W_A','Z_4')} and actual['Z_4'] is None,'role/oracle mismatch')
        if case=='mapped_event':
            p.require(actual['C']==[float(F(old['C'][1])+F(1,8)),old['C'][0]] and actual['W_A'] is None,'affine C map mismatch')
            selected=expected['selected_point'];stage=GeometryStageInputs.from_payload(objects[selected['inputs_object']])
            p.require(list(stage.current.C)==actual['C'] and stage.stage=='ci_trial','wrong root role')
            from tests.models.test_grc_v4_ci import scalar_c_bisection
            j,h=scalar_c_bisection(stage)
            p.require(expected['root_current']==[j] and expected['root_hodge']==[[h]],'changed independent root oracle')
            p.require(np.allclose(selected['observed']['current'],expected['root_current'],rtol=0,atol=2e-11)
                      and np.allclose(stage.geometry.one_form_hodge.matrix,expected['root_hodge'],rtol=0,atol=2e-11),
                      'independent CI oracle mismatch')
        else:
            p.require(actual['C']==old['C'] and before['scientific_state']['Q_target']==after['scientific_state']['Q_target'],
                      'migration resource/charge drift')
            if case=='persistent_C_PC':
                p.require(actual['W_A'] is None and old['Z_4'] not in (None,[0]),'vacuous carrier loss')
            else:
                p.require(backend is not None and old['W_A'] is None,'wrong initializer authority')
                derived,W=initializer_oracle(target,backend,old['C'])
                p.require(actual['W_A']==W and expected['reference_pass']==derived,'initializer equations mismatch')
    if case=='persistent_C_PC':
        p.require(before['scientific_state']['authoritative']['Z_4']!=before['reset']['authoritative']['Z_4'],
                  'borrowed current/reset carrier')
    elif case=='C_to_A':
        p.require(target.profile.complete_profile_id!=NOMINATED
                  and after['scientific_state']['authoritative']['W_A']!=after['reset']['authoritative']['W_A'],
                  'initializer roles collapsed')
    else:
        p.require(request['resource_transform']['row_major_coefficients']==[0,1,1,0]
                  and request['resource_transform']['target_increment']==[.125,0]
                  and obs['expected_Q_target']==after['scientific_state']['Q_target']==float(F(before['scientific_state']['Q_target'])+F(1,8))
                  and obs['missing_archive_rejected'] is True and obs['both_roles_admitted_before_publication'] is True
                  and obs['map_scope']=='renamed_one_edge_C_CI_target; not_arbitrary_topology_or_parameter_sweep',
                  'event map/publication boundary changed')
        p.require(dict(target.profile.params_resolved.candidate.W_C_tr)=={'target-e':2.}
                  and request['target_graph']==target.graph.to_payload()
                  and target.graph.live_edge_ids==('target-e',)
                  and target.graph.graph_digest!=before['scientific_state']['graph_digest']
                  and after['transition_records'][-1]['initializer_pair'] is None,'C target reference/initializer drift')
        roles=set()
        for point in obs['target_readmission_points']:
            stage=GeometryStageInputs.from_payload(objects[point['inputs_object']])
            p.require(stage.geometry.reference==target and stage.current.W_A is None and stage.current.Z_4 is None,
                      'borrowed target reconstruction authority')
            roles.add(tuple(stage.current.C));expected=dense_current_oracle(stage)
            p.require(set(point['observed'])=={'projector','sector','hm','phi','j0','current','read'},'missing C reconstruction surface')
            for key,actual in point['observed'].items():
                p.require(np.asarray(actual).shape==np.asarray(expected[key]).shape
                          and np.allclose(actual,expected[key],rtol=0,atol=2e-12),'C target equation mismatch: '+key)
        p.require(roles=={tuple(obs['expectations'][role]['C']) for role in ('current','reset')},'target roles not separately rederived')


def check(local_product=None):
    local_product = local.check() if local_product is None else local_product
    value = review.read(RECORD)
    p.require(local_product['record_digest'] == value['local_record_digest'], 'wrong local predecessor')
    validate(value)
    return dict(status='crossings_reconciled_pending_review', record_path=RECORD, record_digest=value['record_digest'],
        complete_profile_id=NOMINATED, test_count=3, new_execution_cases=5, retained_alias_count=5,
        reconciled_crossing_cells=7, local_cells=26, ordered_migration_classes=7,
        matrix_scope='exact_declared_endpoints_and_reset_failure; separate_PC_pairs; not_all_pairs',
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        new_G2_support=[], all_ordered_pairs_verified=False, numerical_tests_rerun=0)


def run():
    from test_p977_c_ci_crossings import CCICrossingTests
    predecessor = local.check()
    aliases, traces = retained(), authority()
    before = bindings()
    ids = roster()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'crossing execution failed')
    p.require(before == bindings(), 'sources changed during crossing capture')
    value = dict(schema='phase9_exact_profile_crossing_reconciliation_v1', iteration_id='P9-7.7-C_CI-crossings',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=before,
        nomination=review.read(local.RECORD)['nomination'], local_record_digest=predecessor['record_digest'],
        test_ids=ids, results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        fixture_results=CCICrossingTests.rows, objects=CCICrossingTests.objects,
        retained_aliases=aliases, ordered_migration_matrix=matrix(), catalog_cells=cells(), authority=traces,
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
