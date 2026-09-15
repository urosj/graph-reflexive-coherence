"""Rehashed C_RG2b evidence pressure, without another numerical campaign."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_c_rg2b_local as audit


class CRG2bLocalEvidenceTests(unittest.TestCase):
    def test_registered_checker_and_shared_browser_projection(self):
        """Actual new checker + generic view; not a full status-chain rerun."""
        import json
        import subprocess
        import sys
        import profile_g2_registry as registry
        root=audit.p.ROOT
        record=audit.review.read(audit.RECORD)
        check=registry._checker(root,'verify_p977_c_rg2b_local')
        view=check(initial_review={'record_digest':record['initial_review_digest']})
        roster=registry.registry(root)
        self.assertIn(dict(view_key='c_rg2b_local_product',module='verify_p977_c_rg2b_local',
                           kind='local',dependency='profile_conformance_review'),roster['materializers'])
        values=dict(roster['reconciliation_views'],c_rg2b_local_product=view)
        registry.checked_reconciliation(root,values)
        self.assertEqual(view['verified_local_cells'],26)
        self.assertEqual(len(view['remaining_catalog_cases']),7)
        self.assertFalse(view['G2_accepted'])
        tool=root/audit.p.SIDE/'tool';sys.path.insert(0,str(tool/'src'))
        from grcv4_explorer.tooling import managed_node,tool_environment
        code="""
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkedReconciliation,renderReconciliation} from './verification.js';
const v=JSON.parse(readFileSync(0,'utf8'));
checkedReconciliation(v,true);
const body={rows:[],replaceChildren(){this.rows=[];},append(r){this.rows.push(r);}};
const create=()=>({children:[],append(c){this.children.push(c);}});
renderReconciliation(v,body,create);
const r=body.rows.find(r=>r.children[0].textContent==='c_rg2b_local_product');
assert.ok(r); assert.equal(r.children[1].textContent,'26');
assert.equal(r.children[2].textContent,'Local evidence pending review');
for(const field of ['G2_accepted','user_accepted','aggregate_closed','G3_accepted']) {
 const bad=structuredClone(v);bad.c_rg2b_local_product[field]=true;
 assert.throws(()=>checkedReconciliation(bad,true));
}
for(const field of ['verified_local_cells','test_count','numerical_tests_rerun']) {
 const bad=structuredClone(v);bad.c_rg2b_local_product[field]++;
 assert.throws(()=>checkedReconciliation(bad,true));
}
const missing=structuredClone(v);delete missing.c_rg2b_local_product;
assert.throws(()=>checkedReconciliation(missing,true));
checkedReconciliation({},false);assert.throws(()=>checkedReconciliation(v,false));
console.log('C_RG2B_SHARED_PROJECTION_PASS');
"""
        result=subprocess.run([str(managed_node()),'--input-type=module','-e',code],cwd=tool/'phase9-web',
                              input=json.dumps(values),text=True,capture_output=True,env=tool_environment(),timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('C_RG2B_SHARED_PROJECTION_PASS',result.stdout)

    def test_retained_product_and_rehashed_mutations(self):
        original=audit.review.read(audit.RECORD)
        audit.validate(original)
        def obs(value,case): return next(r for r in value['fixture_results'] if r['fixture_id']==case)['observation']
        def science(value,edit):
            for r in value['fixture_results']:
                if isinstance(r['observation'],dict) and 'roles' in r['observation']: edit(r['observation'])
        changes={
            'missing_cell':lambda v:v['fixture_results'].pop(),
            'duplicate_cell':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'missing_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'source_drift':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'authority_promotion':lambda v:v.update(authority={}),
            'G2_promotion':lambda v:v.update(G2_accepted=True),
            'acceptance':lambda v:v.update(user_accepted=True),
            'new_support':lambda v:v.update(new_G2_support=['C_RG2b']),
            'G3':lambda v:v.update(G3_accepted=True),
            'aggregate':lambda v:v.update(aggregate_closed=True),
            'C1_overclaim':lambda v:science(v,lambda b:b.update(section_scope='C1_classical_section')),
            'CI_overclaim':lambda v:science(v,lambda b:b.update(CI_root_claimed=True)),
            'base_invariance':lambda v:science(v,lambda b:b.update(global_base_invariance_claimed=True)),
            'double_writer':lambda v:science(v,lambda b:b.update(writer_count=2)),
            'carrier':lambda v:science(v,lambda b:b['diagnostics'].update(carrier_writes=1)),
            'double_continuity':lambda v:science(v,lambda b:b['diagnostics'].update(continuity_evaluations=2)),
            'noncontraction':lambda v:science(v,lambda b:b['roles'][0]['certificate'].update(contraction_upper='1')),
            'missing_reset':lambda v:science(v,lambda b:b['roles'].pop(1)),
            'wrong_current':lambda v:science(v,lambda b:b['roles'][0].update(current=[999]*3)),
            'wrong_baseline':lambda v:science(v,lambda b:b['roles'][0]['chain'].update(j0=[999]*3)),
            'wrong_inverse':lambda v:science(v,lambda b:b['roles'][0].update(inverse_oracle_h=[[999]*3]*3)),
            'wrong_section':lambda v:science(v,lambda b:b['roles'][0].update(h=[[999]*3]*3)),
            'stale_reset':lambda v:science(v,lambda b:b['roles'][1].update(inputs_object=b['roles'][0]['inputs_object'])),
            'stale_restart':lambda v:science(v,lambda b:b['roles'][2].update(inputs_object=b['roles'][0]['inputs_object'])),
            'error_exceeded':lambda v:science(v,lambda b:b['roles'][0].update(error_upper='1')),
            'budget_exceeded':lambda v:science(v,lambda b:b['roles'][0].update(evaluations=999999)),
            'source_refresh':lambda v:science(v,lambda b:b.update(generated_h=[[999]*3]*3)),
            'wrong_continuity':lambda v:science(v,lambda b:b['observed'].update(final_C=[999]*4)),
            'wrong_potential':lambda v:science(v,lambda b:b['roles'][2]['chain'].update(phi=[999]*4)),
            'wrong_invariance':lambda v:science(v,lambda b:b['diagnostics'].update(invariance_residual='1')),
            'control_identity':lambda v:obs(v,'C-CHI-ZERO').update(control_complete_profile_id=v['nomination']['complete_profile_id']),
            'control_source':lambda v:obs(v,'C-ZETA-ZERO').update(zero_section_h=[[999]*3]*3),
            'missing_chain':lambda v:science(v,lambda b:b['roles'][0]['chain'].pop('q')),
            'mobility_transfer':lambda v:obs(v,'C-TR-REFERENCE-MAP').update(E_M=obs(v,'C-TR-REFERENCE-MAP')['E_H']),
            'selector':lambda v:obs(v,'C-SELECTOR-STRICT-GAP').update(rank=3),
            'boundary_promotion':lambda v:obs(v,'C-SELECTOR-BOUNDARY').update(scope='public_operation'),
            'physical_condition':lambda v:obs(v,'C-RETAINED-VS-PHYSICAL-CONDITIONING')['counterexample'].update(physical_rejected=False),
            'invented_history':lambda v:obs(v,'C-C-ONLY-AUTHORITY').update(W_A=[1]*3),
            'zero_mobility':lambda v:obs(v,'C-KAPPA-M-ZERO').update(mobility=[0]*3),
            'C1_derivative':lambda v:obs(v,'C-BASELINE-DERIVATIVE-COVARIANCE').update(scope='RG_section_derivative'),
            'missing_partial_stratum':lambda v:obs(v,'C-BASELINE-DERIVATIVE-COVARIANCE')['derivatives'].pop(),
            'double_chi':lambda v:obs(v,'C-ONE-CHI-GATE').update(fixed_J_chi_ratio=4),
            'control_support':lambda v:obs(v,'C-ZETA-ZERO').update(control_is_nominated_support=True),
            'missing_pressure':lambda v:v['readmission_pressure'].pop(),
            'fallback':lambda v:v['readmission_pressure'][2].update(fallback_used=True),
            'reset_writer':lambda v:v['readmission_pressure'][3].update(writer_count=1),
            'wrong_failure_stage':lambda v:v['readmission_pressure'][4].update(failure_stage='admission'),
            'rollback':lambda v:v['readmission_pressure'][4].update(whole_publication_unchanged=False),
            'reset_authority':lambda v:obs(v,'RESET-AFTER-ORDINARY').update(independent_reset_authority={}),
            'missing_parent':lambda v:obs(v,'RECEIPT-OWNERSHIP').update(coherent_missing_parent_rejected=False),
            'duplicate_alias':lambda v:obs(v,'DUPLICATION-INDEPENDENCE').update(exported_mutations_detached=False),
        }
        # The valid current authority/source checks above run once. Mutations
        # below exercise retained semantics, not repeated forensic rebuilds.
        with patch.object(audit,'authority',return_value=original['authority']):
            for name,edit in changes.items():
                value=deepcopy(original);edit(value);value['record_digest']=audit.p.digest_record(value)
                with self.subTest(name=name),self.assertRaises((ValueError,KeyError,TypeError)):
                    audit.validate(value)


if __name__=='__main__': unittest.main()
