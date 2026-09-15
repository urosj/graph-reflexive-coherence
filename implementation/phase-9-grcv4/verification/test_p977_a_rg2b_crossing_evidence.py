"""A_RG2b crossing evidence and generic projection; no native campaign rerun."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_a_rg2b_crossings as audit


class ARG2bCrossingEvidenceTests(unittest.TestCase):
    def test_rehashed_endpoint_history_completion_and_scope_pressure(self):
        value=audit.review.read(audit.RECORD);audit.validate(value)
        def row(v,k):return next(r for r in v['fixture_results'] if r['fixture_id']==k)
        def obs(v,k='mapped_event'):return row(v,k)['observation']
        def read(v,role='current'):return obs(v)['expectations'][role]['readmission']
        def object_edit(v,key,edit):
            # Rehash the changed object and its references, not merely the top
            # record. Semantic controls must reject after hash consistency.
            obj=v['objects'].pop(key);edit(obj)
            new=audit.p.sha(audit.p.canonical(obj));v['objects'][new]=obj
            def rewrite(x):
                if isinstance(x,dict):return {k:rewrite(a) for k,a in x.items()}
                if isinstance(x,list):return [rewrite(a) for a in x]
                return new if x==key else x
            v['fixture_results']=rewrite(v['fixture_results'])
        mutations={
            'missing_case':lambda v:v['fixture_results'].pop(),
            'duplicate_case':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'authority':lambda v:v.update(authority={}),
            'borrowed_source':lambda v:row(v,'mapped_event').update(complete_profile_id='A_RG2b'),
            'missing_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'invented_solver':lambda v:v['fixture_results'][0].update(solver_disposition='valid_root'),
            'lost_receipt_delta':lambda v:v['fixture_results'][0]['emitted_receipt_ids'].pop(),
            'missing_class':lambda v:v['ordered_migration_matrix'].pop(),
            'scalar_as_nomination':lambda v:v['retained_aliases'][0].update(evidence_scope='exact_nomination_target'),
            'borrowed_PC_pair':lambda v:v['ordered_migration_matrix'][3].update(disposition='positive_exact_nomination_target'),
            'positive_nominal_initializer':lambda v:v['ordered_migration_matrix'][-1].update(disposition='positive_exact_nomination_target'),
            'G2':lambda v:v.update(G2_accepted=True),
            'G3':lambda v:v.update(G3_accepted=True),
            'acceptance':lambda v:v.update(user_accepted=True),
            'aggregate':lambda v:v.update(aggregate_closed=True),
            'all_pairs':lambda v:v.update(all_ordered_pairs_verified=True),
            'support':lambda v:v.update(new_G2_support=[audit.NOMINATED]),
            'missing_cell':lambda v:v['catalog_cells'].pop('HISTORY-DISPOSITION'),
            'loss_erased':lambda v:obs(v).update(expected_losses=[]),
            'false_carrier_loss':lambda v:obs(v).update(expected_losses=['candidate_history_loss','carrier_history_loss']),
            'fresh_PC_as_loss':lambda v:obs(v,'persistent_outgoing').update(expected_losses=['carrier_history_loss']),
            'drop_PC_without_loss':lambda v:obs(v,'persistent_incoming').update(expected_losses=[]),
            'ordinary_writer':lambda v:obs(v).update(ordinary_writer_count=1),
            'late_readmission':lambda v:obs(v).update(both_roles_admitted_before_publication=False),
            'initializer_reference':lambda v:obs(v)['expectations']['reset'].update(reference_pass={}),
            'event_W':lambda v:obs(v)['expectations']['current'].update(W_A=[2.]*3),
            'event_Z':lambda v:obs(v)['expectations']['reset'].update(Z_4=[0.]*9),
            'event_charge':lambda v:obs(v).update(expected_Q_target=8.),
            'event_archive':lambda v:obs(v).update(missing_archive_rejected=False),
            'event_duplicate':lambda v:obs(v).update(duplicate_unchanged_after_reset=False),
            'all_graphs':lambda v:obs(v).update(map_scope='all_graphs'),
            'initializer_nomination':lambda v:obs(v).update(initializer_is_separate_target=False),
            'current':lambda v:read(v).update(current=[999.]*3),
            'h':lambda v:read(v).update(h=[[999.]*3]*3),
            'inverse':lambda v:read(v).update(inverse_oracle_h=[[999.]*3]*3),
            'reset_role':lambda v:read(v,'reset').update(inputs_object=read(v)['inputs_object']),
            'section_role':lambda v:read(v,'reset').update(section_inputs_object=read(v)['section_inputs_object']),
            'zero_beat_completion':lambda v:read(v).update(frozen_beat=0.),
            'C1':lambda v:read(v).update(regularity='C1'),
            'noncontraction':lambda v:read(v)['certificate'].update(contraction_upper='1'),
            'uncertified':lambda v:read(v).update(error_upper='1'),
            'unbounded_budget':lambda v:read(v).update(evaluations=999999),
            'migration_replay':lambda v:obs(v,'nonpersistent_incoming').update(exact_replay=False),
            'wrong_reset_after':lambda v:obs(v).update(after_reset_object=row(v,'mapped_event')['poststate_object']),
            'K_is_K_minus':lambda v:obs(v,'core_only_admission').update(state_readmission_is_not_ordinary_entry=False),
            'K_ordinary_unchecked':lambda v:obs(v,'core_only_admission').update(ordinary_entry_rejected_durations=[]),
            'not_reset_only':lambda v:obs(v,'readmission_rejection').update(reset_W=2.),
            'wrong_failure':lambda v:obs(v,'readmission_rejection').update(failure_stage='admission'),
            'rehash_affine_map':lambda v:object_edit(v,row(v,'mapped_event')['request_object'],
                lambda o:o['resource_transform'].update(target_increment=[0.]*4)),
            'rehash_target_C':lambda v:object_edit(v,row(v,'mapped_event')['poststate_object'],
                lambda o:o['scientific_state']['authoritative'].update(C=[2.]*4)),
            'rehash_reset_W':lambda v:object_edit(v,row(v,'persistent_incoming')['poststate_object'],
                lambda o:o['reset']['authoritative'].update(W_A=[2.]*3)),
        }
        with patch.object(audit,'authority',return_value=value['authority']):
            for name,edit in mutations.items():
                bad=deepcopy(value);edit(bad);bad['record_digest']=audit.p.digest_record(bad)
                with self.subTest(name=name),self.assertRaises((ValueError,KeyError,TypeError)):
                    audit.validate(bad)

    def test_registered_crossing_checker_and_browser_projection(self):
        import json,subprocess,sys
        import profile_g2_registry as registry
        root=audit.p.ROOT;record=audit.review.read(audit.RECORD)
        checked=registry._checker(root,'verify_p977_a_rg2b_acceptance')(
            local_product={'record_digest':record['local_record_digest']})
        roster=registry.registry(root)
        self.assertIn(dict(view_key='a_rg2b_crossings',module='verify_p977_a_rg2b_acceptance',kind='crossing',
                           dependency='a_rg2b_local_product'),roster['materializers'])
        views=dict(roster['reconciliation_views'],a_rg2b_crossings=checked)
        registry.checked_reconciliation(root,views)
        self.assertEqual((checked['reconciled_crossing_cells'],checked['new_execution_cases']),(7,9))
        self.assertFalse(checked['G2_accepted'])
        tool=root/audit.p.SIDE/'tool';sys.path.insert(0,str(tool/'src'))
        from grcv4_explorer.tooling import managed_node,tool_environment
        code="""
import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {checkedReconciliation,renderReconciliation} from './verification.js';
const v=JSON.parse(readFileSync(0,'utf8'));checkedReconciliation(v,true);
const body={rows:[],replaceChildren(){this.rows=[];},append(r){this.rows.push(r);}};
renderReconciliation(v,body,()=>({children:[],append(c){this.children.push(c);}}));
const r=body.rows.find(r=>r.children[0].textContent==='a_rg2b_crossings');assert.ok(r);
assert.equal(r.children[1].textContent,'7');assert.equal(r.children[2].textContent,'Bounded reconciliation accepted');
for(const field of ['G2_accepted','G3_accepted','user_accepted','aggregate_closed','all_ordered_pairs_verified']) {
 const bad=structuredClone(v);bad.a_rg2b_crossings[field]=!bad.a_rg2b_crossings[field];assert.throws(()=>checkedReconciliation(bad,true));
}
for(const field of ['reconciled_crossing_cells','new_execution_cases','retained_alias_count','numerical_tests_rerun']) {
 const bad=structuredClone(v);bad.a_rg2b_crossings[field]++;assert.throws(()=>checkedReconciliation(bad,true));
}
const bad=structuredClone(v);delete bad.a_rg2b_crossings;assert.throws(()=>checkedReconciliation(bad,true));
checkedReconciliation({},false);assert.throws(()=>checkedReconciliation(v,false));
console.log('A_RG2B_CROSSING_PROJECTION_PASS');
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',code],cwd=tool/'phase9-web',
            input=json.dumps(views),capture_output=True,text=True,env=tool_environment(),timeout=30)
        self.assertEqual(result.returncode,0,result.stderr);self.assertIn('A_RG2B_CROSSING_PROJECTION_PASS',result.stdout)


if __name__=='__main__':unittest.main()
