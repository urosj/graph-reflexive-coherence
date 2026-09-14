"""Exact C_CI_PC crossing reconciliation. --run emits a fresh record to stdout."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review
import verify_p977_c_ci_pc_local as local

SCRIPT = p.HERE + 'verify_p977_c_ci_pc_crossings.py'
TEST = p.HERE + 'test_p977_c_ci_pc_crossings.py'
RECORD = p.PHASE + 'tranche-7/P9-7.7-C_CI_PC-Crossings.json'
NOMINATED = 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b'
MIGRATIONS = {
    'nonpersistent_incoming': ('C_CI','C_CI_PC','rederived','target_initializer',[]),
    'nonpersistent_outgoing': ('C_CI_PC','C_CI','rederived','explicit_loss',['carrier_history_loss']),
    'candidate_incoming': ('A_CI_PC','C_CI_PC','explicit_loss','whole_carrier_reset',['candidate_history_loss','carrier_history_loss']),
    'initializer_outgoing': ('C_CI_PC','A_CI_PC','target_initializer','whole_carrier_reset',['carrier_history_loss']),
}
CASES = sorted([*MIGRATIONS, 'carrier_contract_rejection', 'mapped_event',
                'readmission_control', 'readmission_rejection'])


def bindings():
    return {**local.bindings(), **{n: p.sha((p.ROOT/n).read_bytes()) for n in
        (SCRIPT, TEST, local.RECORD, review.SOURCES['migration'], review.SOURCES['initializer'], p.HERE+'test_p977_a_ci_crossings.py')}}


def roster():
    from test_p977_c_ci_pc_crossings import CCIPCCrossingTests
    return ['test_p977_c_ci_pc_crossings.CCIPCCrossingTests.' + n
            for n in unittest.TestLoader().getTestCaseNames(CCIPCCrossingTests)]


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
    for origin, key in [('migration', k) for k in ('C_NH_NH', 'C_PC_CIPC', 'C_CIPC_PC')]:
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
        dict(migration_class='same_candidate_nonhistory_to_nonhistory', disposition='separate_endpoints_not_C_CI_PC; no positive nomination credit', evidence='migration/C_NH_NH'),
        dict(migration_class='same_candidate_nonhistory_to_history', disposition='positive_exact_nomination_target', evidence='nonpersistent_incoming'),
        dict(migration_class='same_candidate_history_to_nonhistory', disposition='positive_exact_nomination_source', evidence='nonpersistent_outgoing'),
        dict(migration_class='PC_to_CI_PC', disposition='positive_exact_nomination_target; exact_carrier_contract_only', evidence='migration/C_PC_CIPC'),
        dict(migration_class='CI_PC_to_PC', disposition='positive_exact_nomination_source; exact_carrier_contract_only', evidence='migration/C_CIPC_PC', negative='carrier_contract_rejection'),
        dict(migration_class='A_to_C', disposition='positive_exact_nomination_target; separate_candidate_loss_and_whole_carrier_reset', evidence='candidate_incoming'),
        dict(migration_class='C_to_A', disposition='positive_exact_nomination_source; separate_initializer_target; carrier_loss_not_candidate_loss', evidence='initializer_outgoing'),
    ]


def cells():
    return {
        'C-LIFECYCLE-REFERENCE-MAP': ['nonpersistent_incoming','migration/C_PC_CIPC','candidate_incoming','mapped_event'],
        'RESET-AFTER-MIGRATION': [*MIGRATIONS,'migration/C_PC_CIPC','migration/C_CIPC_PC'],
        'RESET-AFTER-EVENT': ['mapped_event'],
        'WHOLE-LIFECYCLE-TUPLE-MAP': ['mapped_event'],
        'ALL-MIGRATION-CLASSES': ['ordered_migration_matrix'],
        'HISTORY-DISPOSITION': [*MIGRATIONS,'migration/C_PC_CIPC','migration/C_CIPC_PC','mapped_event','carrier_contract_rejection'],
        'TARGET-READMISSION-FAILURE': ['readmission_control','readmission_rejection'],
    }


def validate_retained_maps():
    """Preserved PC pairs only; do not infer missing historical solver evidence."""
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry as Reference
    from pygrc.models.grc_v4_migration import carrier_contract
    cases = review.read(review.SOURCES['migration'])['cases']
    for key in ('C_PC_CIPC','C_CIPC_PC'):
        row=cases[key];before,after=row['before'],row['after']
        source=Reference.from_payload(row['initial']['reference'])
        target=Reference.from_payload(row['target_reference'])
        endpoint=target if key=='C_PC_CIPC' else source
        p.require(endpoint.profile.complete_profile_id==NOMINATED, 'retained nomination substituted')
        receipt=row['receipts'][0]['identity_payload']
        p.require(receipt['core']['information_losses']==[]
                  and receipt['history']['candidate']['disposition']=='rederived'
                  and receipt['history']['carrier']['disposition']=='exact_transport'
                  and carrier_contract(source)==carrier_contract(target), 'retained carrier authority drift')
        for role in ('scientific_state','reset'):
            a,b=before[role]['authoritative'],after[role]['authoritative']
            p.require(a==b and a['W_A'] is None and a['Z_4'] not in (None,[0.]), 'retained role transport drift')
        p.require(before['scientific_state']['authoritative']['Z_4']!=before['reset']['authoritative']['Z_4'],
                  'vacuous retained carrier contrast')
        for name in ('time','step_index','Q_target'):
            p.require(before['scientific_state'][name]==after['scientific_state'][name]
                      ==row['reset']['scientific_state'][name], 'retained clock/charge drift')


def validate_reset(obs,objects,after):
    reset=objects[obs['after_reset_object']]
    p.require(reset['scientific_state']['authoritative']==after['reset']['authoritative']
              and reset['reset']==after['reset'] and reset['reference']==after['reference']
              and reset['transition_records']==after['transition_records']
              and len(reset['receipt_ledger'])==len(after['receipt_ledger'])+4
              and reset['receipt_ledger'][:-4]==after['receipt_ledger']
              and len(reset['commit_records'])==len(after['commit_records'])+1
              and reset['commit_records'][:-1]==after['commit_records'], 'reset/ledger drift')
    for name in ('time','step_index','Q_target'):
        p.require(reset['scientific_state'][name]==after['scientific_state'][name], 'reset clock/charge drift')


def validate_migration(case,before,after,request,result,obs,objects):
    import numpy as np
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry as Reference, GeometryStageInputs
    from tests.models.test_grc_v4_migration import fixture
    from tests.models.test_grc_v4_initializer import target as initializer_target, oracle as initializer_oracle
    from tests.models.test_grc_v4_cipc import independent_root as coupled_root
    from tests.models.test_grc_v4_ci import independent_root as ci_root
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle
    def close(a,b,message):
        p.require(np.shape(a)==np.shape(b) and np.allclose(a,b,rtol=0,atol=2e-11),message)
    sf,tf,candidate,carrier,losses=MIGRATIONS[case]
    source=fixture(sf)[0].geometry.reference
    if case=='initializer_outgoing':target,backend=initializer_target(tf)
    else:target,backend=fixture(tf)[0].geometry.reference,None
    p.require(before['reference']==source.to_payload()
              and objects[obs['target_reference_object']]==target.to_payload()==after['reference']
              and request['target_profile_id']==target.profile.complete_profile_id
              and NOMINATED in (source.profile.complete_profile_id,target.profile.complete_profile_id),
              'native migration exact endpoints changed')
    p.require((obs['target_backend_object'] is None if backend is None else
              objects[obs['target_backend_object']]==backend.to_payload()), 'target backend drift')
    primary=result['emitted_receipts'][0]['identity_payload'];history=primary['history']
    p.require(obs['expected_candidate']==history['candidate']['disposition']==candidate
              and obs['expected_carrier']==history['carrier']['disposition']==carrier
              and obs['expected_losses']==primary['core']['information_losses']==losses,
              'native migration two-channel history changed')
    p.require(obs['both_roles_admitted_before_publication'] is True and obs['exact_replay'] is True
              and obs['initializer_is_separate_target']==(case=='initializer_outgoing'), 'migration evidence scope drift')
    if case=='initializer_outgoing':
        p.require(after['transition_records'][-1]['initializer_pair'] is not None
                  and target.profile.complete_profile_id!=fixture('A_CI_PC')[0].geometry.reference.profile.complete_profile_id,
                  'initializer borrowed nominal A support')
    else:p.require(after['transition_records'][-1].get('initializer_pair') is None, 'unexpected A initializer')
    for role,key in (('current','scientific_state'),('reset','reset')):
        a,b=before[key]['authoritative'],after[key]['authoritative'];expected=obs['expectations'][role]
        init,W=initializer_oracle(target,backend,a['C']) if case=='initializer_outgoing' else (None,None)
        Z=None if case=='nonpersistent_outgoing' else [0.]
        p.require(b==dict(C=a['C'],W_A=W,Z_4=Z)=={k:expected[k] for k in ('C','W_A','Z_4')}
                  and expected['reference_pass']==init, 'migration role/initializer equations drift')
        p.require((a['Z_4'] is None if case=='nonpersistent_incoming' else a['Z_4'] not in (None,[0.]))
                  and (a['W_A'] not in (None,[0.]) if case=='candidate_incoming' else a['W_A'] is None),
                  'vacuous source-history control')
        root=GeometryStageInputs.from_payload(objects[expected['root_inputs_object']])
        selected=GeometryStageInputs.from_payload(objects[expected['selected_inputs_object']])
        p.require(root.geometry.reference==selected.geometry.reference==target
                  and root.current==selected.current
                  and dict(C=list(root.current.C),W_A=None if root.current.W_A is None else list(root.current.W_A),
                           Z_4=None if root.current.Z_4 is None else list(root.current.Z_4))==b
                  and root.stage=='pre_read'
                  and selected.stage==('cipc_trial' if target.profile.identity_payload.realization=='CI+PC' else 'ci_trial'),
                  'migration role/root selection drift')
        if target.profile.identity_payload.realization=='CI+PC':
            h,j,source_term=coupled_root(root,backend)
            close(expected['source'],source_term,'coupled source drift')
        else:
            j,h=ci_root(root,backend)
            p.require(expected['source'] is None,'plain CI misclassified as coupled')
        close(expected['h'],h,'migration selected H drift')
        close(selected.geometry.one_form_hodge.matrix,h,'migration root input H drift')
        close(expected['current'],j,'migration root current drift')
        chain=expected['C_chain']
        if target.profile.identity_payload.candidate=='C':
            oracle=dense_current_oracle(selected)
            p.require(set(chain['observed'])==set(chain['independent_oracle'])==
                      {'projector','sector','hm','phi','j0','ident','q','current','read'}, 'incomplete migration C chain')
            for name in chain['observed']:
                close(chain['observed'][name],oracle[name],'migration C equation drift: '+name)
                close(chain['independent_oracle'][name],oracle[name],'migration C oracle drift: '+name)
        else:p.require(chain is None, 'C equations attributed to A target')
    p.require(before['scientific_state']['authoritative']['C']!=before['reset']['authoritative']['C'],
              'migration roles collapsed')
    if case=='initializer_outgoing':
        p.require(after['scientific_state']['authoritative']['W_A']!=after['reset']['authoritative']['W_A'],
                  'initializer roles collapsed')
    for name in ('time','step_index','Q_target'):
        p.require(before['scientific_state'][name]==after['scientific_state'][name], 'migration clock/charge drift')
    validate_reset(obs,objects,after)


def validate_case(case,row,before,after,request,result,obs,objects):
    from fractions import Fraction as F
    import numpy as np
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry as Reference, GeometryStageInputs
    from pygrc.models.grc_v4_migration import carrier_contract
    from pygrc.models.grc_v4_pc import PCBaseChart
    from tests.models.test_grc_v4_candidate_c import dense_current_oracle
    def close(a,b,message):
        p.require(np.shape(a)==np.shape(b) and np.allclose(a,b,rtol=2e-12,atol=2e-14),message)
    if case in MIGRATIONS:
        validate_migration(case,before,after,request,result,obs,objects)
        return
    p.require(row['complete_profile_id']==NOMINATED, 'wrong nominated source')
    if not row['committed']:
        p.require(row['failure_code']==result['failure']['code'], 'failure code differs')
    target=Reference.from_payload(objects[obs['target_reference_object']])
    p.require(target.profile.complete_profile_id==request['target_profile_id'], 'target reference drift')
    if row['committed']:
        p.require(after['reference']==target.to_payload(), 'published target reference differs')
    if case=='carrier_contract_rejection':
        source=Reference.from_payload(before['reference'])
        original=Reference.from_payload(objects[obs['preserved_target_reference_object']])
        left,right=carrier_contract(original),carrier_contract(target)
        p.require(carrier_contract(source)==left and left!=right and obs['changed_field']=='tau_PC'
                  and obs['unchanged_history_not_silently_reset'] is True
                  and result['failure']['stage']=='admission' and 'exact carrier' in result['failure']['message'],
                  'changed carrier contract boundary lost')
        from tests.models.test_grc_v4_migration import changed_reference
        p.require(target==changed_reference(original,'realization',tau_PC=1.)
                  and original.profile.params_resolved.realization.tau_PC!=1., 'carrier contrast changed')
        return
    if case=='mapped_event':
        p.require(target.profile.identity_payload.candidate=='C'
                  and target.profile.identity_payload.realization=='CI+PC' and target.profile.complete_profile_id!=NOMINATED
                  and dict(target.profile.params_resolved.candidate.W_C_tr)=={'target-e':2.}
                  and target.graph.live_edge_ids==('target-e',)
                  and request['target_graph']==target.graph.to_payload()
                  and target.graph.graph_digest!=before['scientific_state']['graph_digest'],
                  'C target/reference map replaced')
        from pygrc.models.grc_v4_geometry import GraphCoordinateAction
        from pygrc.models.grc_v4_events import coordinate_reference
        source=Reference.from_payload(before['reference'])
        expected_target,_=coordinate_reference(source,GraphCoordinateAction(source.graph,target.graph,(0,1),(0,),(1,)))
        p.require(target==expected_target, 'renamed target borrows undeclared parameters')
        p.require(request['resource_transform']['row_major_coefficients']==[0,1,1,0]
                  and request['resource_transform']['target_increment']==[-.125,0], 'affine event map drift')
        for role,key in (('current','scientific_state'),('reset','reset')):
            old,actual=before[key]['authoritative'],after[key]['authoritative']
            C=[float(F(old['C'][1])-F(1,8)),old['C'][0]]
            expected=obs['expectations'][role]
            p.require(actual==dict(C=C,W_A=None,Z_4=[0.])
                      and actual=={k:expected[k] for k in ('C','W_A','Z_4')}
                      and old['W_A'] is None and old['Z_4'] not in (None,[0.]), 'event role/loss map mismatch')
            chain=expected['readmission']
            inputs=GeometryStageInputs.from_payload(objects[chain['inputs_object']])
            p.require(inputs.geometry.reference==target and list(inputs.current.C)==C
                      and inputs.current.W_A is None and list(inputs.current.Z_4)==[0.]
                      and inputs.stage=='cipc_trial', 'C readmission role/stage drift')
            from tests.models.test_grc_v4_cipc import independent_root as coupled_root
            root=GeometryStageInputs.from_payload(objects[chain['root_inputs_object']])
            p.require(root.geometry.reference==target and root.current==inputs.current and root.stage=='pre_read',
                      'event root/selected role drift')
            h,j,source_term=coupled_root(root,None)
            p.require(np.allclose(chain['h'],h,rtol=0,atol=2e-11),'coupled event geometry drift')
            p.require(np.allclose(chain['source'],source_term,rtol=0,atol=2e-11),'coupled event source drift')
            p.require(np.allclose(inputs.geometry.one_form_hodge.matrix,h,rtol=0,atol=2e-11),'readmission geometry drift')
            p.require(np.linalg.norm(h-np.asarray(target.pairings.one_form.matrix))>1e-8
                      and np.linalg.norm(source_term)>0 and obs['zero_carrier_retains_immediate_geometry'] is True,
                      'zero carrier flattened immediate geometry')
            oracle=dense_current_oracle(inputs)
            p.require(set(chain['observed'])==set(chain['independent_oracle'])==
                      {'projector','sector','hm','phi','j0','ident','q','current','read'}, 'incomplete C reconstruction')
            for key in chain['observed']:
                close(chain['observed'][key],oracle[key],'event C equation drift: '+key)
                close(chain['independent_oracle'][key],oracle[key],'independent event equation drift: '+key)
        p.require(before['scientific_state']['authoritative']['Z_4']!=before['reset']['authoritative']['Z_4']
                  and obs['expectations']['current']['C']!=obs['expectations']['reset']['C']
                  and obs['expectations']['current']['readmission']['observed']['j0']!=obs['expectations']['reset']['readmission']['observed']['j0'],
                  'event roles collapsed')
        primary=result['emitted_receipts'][0]['identity_payload'];history=primary['history']
        p.require(obs['expected_losses']==primary['core']['information_losses']==['carrier_history_loss']
                  and obs['expected_candidate']==history['candidate']['disposition']=='rederived'
                  and history['candidate']['information_loss']=='none'
                  and history['candidate']['source_history_digest'] is None
                  and obs['expected_carrier']==history['carrier']['disposition']=='whole_carrier_reset'
                  and history['carrier']['information_loss']=='carrier_history_loss'
                  and obs['source_history_removal_is_not_native_release'] is True,
                  'event two-channel losses erased or invented')
        p.require(obs['expected_Q_target']==after['scientific_state']['Q_target']==float(F(before['scientific_state']['Q_target'])-F(1,8))
                  and obs['missing_archive_rejected'] is True and obs['both_roles_admitted_before_publication'] is True
                  and obs['exact_replay'] is True and obs['duplicate_unchanged_after_reset'] is True
                  and obs['map_scope']=='renamed_one_edge_C_CI_PC_target; not_arbitrary_topology_or_parameter_sweep'
                  and after['transition_records'][-1]['initializer_pair'] is None, 'event ownership/scope drift')
        reset=objects[obs['after_reset_object']]
        p.require(reset['scientific_state']['authoritative']==after['reset']['authoritative']
                  and reset['reset']==after['reset'] and reset['reference']==after['reference']
                  and reset['transition_records']==after['transition_records']
                  and reset['receipt_ledger'][:-4]==after['receipt_ledger']
                  and reset['commit_records'][:-1]==after['commit_records'], 'reset/ledger drift')
        for name in ('time','step_index','Q_target'):
            p.require(reset['scientific_state'][name]==after['scientific_state'][name], 'reset clock/charge drift')
        for name in ('time','step_index'):
            p.require(before['scientific_state'][name]==after['scientific_state'][name], 'event clock drift')
        return
    p.require(target.profile.identity_payload.candidate=='C' and target.profile.identity_payload.realization=='CI+PC'
              and target.profile.params_resolved.realization.source_envelope_id==PCBaseChart(3.,1.,1.).identity
              and obs['source_resource_radius']==4. and obs['target_resource_radius']==3.
              and request['resource_transform']['row_major_coefficients']==[1,0,0,1]
              and request['resource_transform']['target_increment']==[0,0], 'reset-only target/event chart drift')
    norms={key:sum(x*x for x in before[key]['authoritative']['C']) for key in ('scientific_state','reset')}
    p.require(obs['source_current_norm_squared']==norms['scientific_state']<=9
              and obs['source_reset_norm_squared']==norms['reset']<=16, 'resource contrast changed')
    if case=='readmission_rejection':
        p.require(norms['reset']>9 and result['failure']['stage']=='target_readmission'
                  and 'resource' in result['failure']['message'], 'not a reset-only resource rejection')
    else:
        p.require(norms['reset']<=9, 'control reset not admissible')
        for key in ('scientific_state','reset'):
            p.require(after[key]['authoritative']==dict(C=before[key]['authoritative']['C'],W_A=None,Z_4=[0.]), 'control role map mismatch')
        primary=result['emitted_receipts'][0]['identity_payload']
        p.require(primary['core']['information_losses']==['carrier_history_loss']
                  and primary['history']['carrier']['disposition']=='whole_carrier_reset'
                  and primary['history']['candidate']['disposition']=='rederived', 'control loss channels drift')


def validate(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    p.require(value['schema'] == 'phase9_exact_profile_crossing_reconciliation_v1'
              and value['iteration_id'] == 'P9-7.7-C_CI_PC-crossings'
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
    p.require(set(cells()) == set(review.required_cases('C_CI_PC')) - set(local.required()), 'crossing catalog drift')
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
        p.require(row['committed'] == (case in (*MIGRATIONS,'mapped_event','readmission_control')), 'positive/negative crossing relabeled')
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
        complete_profile_id=NOMINATED, test_count=4, new_execution_cases=8, retained_alias_count=3,
        reconciled_crossing_cells=7, local_cells=26, ordered_migration_classes=7,
        matrix_scope='exact_PC_pairs_and_two_channel_losses; separate_nonhistory_and_initializer_target; not_all_pairs',
        user_accepted=False, aggregate_closed=False, G2_accepted=False, G3_accepted=False,
        new_G2_support=[], all_ordered_pairs_verified=False, numerical_tests_rerun=0)


def run(local_product=None):
    from test_p977_c_ci_pc_crossings import CCIPCCrossingTests
    predecessor = local.check() if local_product is None else local_product
    before = bindings()
    ids = roster()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(result.wasSuccessful() and not result.skipped, 'crossing execution failed')
    p.require(before == bindings(), 'sources changed during crossing capture')
    value = dict(schema='phase9_exact_profile_crossing_reconciliation_v1', iteration_id='P9-7.7-C_CI_PC-crossings',
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=before,
        nomination=review.read(local.RECORD)['nomination'], local_record_digest=predecessor['record_digest'],
        test_ids=ids, results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        fixture_results=CCIPCCrossingTests.rows, objects=CCIPCCrossingTests.objects,
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
