import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { canonical, checkedStatus, verifiedStatus, verifiedProbe } from './verification.js';

function fixture(extra = {}) {
  const value = {schema: 'phase9_governance_status_v1', output_class: 'implementation_verification_status_not_forensic_trace', runtime_authorized: false, P9_G1_accepted: false, accepted_generic_runtime_support: [], admitted_specialization_support_sets: [], current_boundary: 'passed', recorded_full_verification: 'not_current', policy_digest: '1'.repeat(64), source_refs: [{path: 'synthetic/fixture.json', sha256: '2'.repeat(64)}], iterations: ['P9-1.7', 'P9-1.8'].map(iteration_id => ({iteration_id, status: 'in_progress', reviewer_decision: 'pending_user_review'})), ...extra};
  value.status_digest = createHash('sha256').update(canonical(value)).digest('hex');
  return value;
}
test('planning is not runtime and lacks a recorded pass', async () => { const value = fixture(); assert.equal(await verifiedStatus(value), value); });
test('runtime/support promotion rejected', () => {
  for (const extra of [{runtime_authorized: true}, {P9_G1_accepted: true}, {accepted_generic_runtime_support: ['C_OS']}, {admitted_specialization_support_sets: [['C_OS']]}, {accepted_generic_runtime_support: ''}, {source_refs: []}, {iterations: []}]) assert.throws(() => checkedStatus(fixture(extra)));
});
test('unrecognized and contradictory status rejected', () => {
  for (const extra of [{schema: 'forensic_trace'}, {current_boundary: 'green'}, {current_boundary: 'failed_closed', recorded_full_verification: 'recorded_pass_matching_current_inputs'}]) assert.throws(() => checkedStatus(fixture(extra)));
});
test('modified payload with stale digest rejected', async () => { const value = fixture(); value.current_boundary = 'failed_closed'; await assert.rejects(verifiedStatus(value), /digest/); });
test('explicit failed-closed result is valid but never a pass', async () => { assert.equal((await verifiedStatus(fixture({current_boundary: 'failed_closed'}))).current_boundary, 'failed_closed'); });
test('canonical planning JSON is key-order independent', () => { assert.equal(canonical({b: ['α', false], a: {z: null, a: 4}}), '{"a":{"a":4,"z":null},"b":["α",false]}'); });

test('full probe IDs sharing a prefix cannot collide and assertion never changes candidate', async () => {
  const a='same-displayed-prefix-0000000000000001', b='same-displayed-prefix-0000000000000002';
  const value={schema:'phase9_pressure_projection_v1',output_class:'isolated_probe_not_current_tree_admission',case_id:a,candidate_decision:'rejected',assertion_result:'passed',project_effect:{runtime_authorized:false,P9_G1_accepted:false,scientific_promotion:false}};
  value.projection_digest=createHash('sha256').update(canonical(value)).digest('hex');
  assert.equal((await verifiedProbe(value,a)).candidate_decision,'rejected');
  await assert.rejects(verifiedProbe(value,b),/exact subject/);
  await assert.rejects(verifiedProbe({...value,candidate_decision:'admitted'},a),/digest/);
});

test('missing null and unrecognized permission cannot substitute for false', () => {
  for(const runtime_authorized of [undefined,null,'unknown','false']) assert.throws(()=>checkedStatus(fixture({runtime_authorized})));
});

function accepted(extra={}) {
  return fixture({schema:'phase9_governance_status_v2',runtime_authorized:true,P9_G1_accepted:true,
    runtime_authority_state:'accepted_P9_G1_bounded_implementation_not_conformance',
    approval_digest:'cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2',
    implementation_scope:Array.from({length:43},(_,i)=>({path:`synthetic/${i}`})),
    dependency_ready_leaves:['P9-2.1','P9-2.2'],permitted_runtime_paths:Array.from({length:11},(_,i)=>`synthetic/${i}`),
    iterations:[4,5,6,7,8,9].map(i=>({iteration_id:`P9-1.${i}`,status:'implemented_and_verified',reviewer_decision:'accepted_by_user'})),...extra});
}
test('accepted G1 permission does not imply accepted profile support',async()=>{
  assert.equal((await verifiedStatus(accepted())).P9_G1_accepted,true);
  for(const extra of [{approval_digest:'0'.repeat(64)},{runtime_authorized:false},{accepted_generic_runtime_support:['C_OS']},{admitted_specialization_support_sets:[['C_OS']]},{implementation_scope:[]},{dependency_ready_leaves:['P9-8.2']}]) assert.throws(()=>checkedStatus(accepted(extra)));
});
test('failed G1 boundary cannot retain permission even with a recomputed digest',async()=>{
  assert.throws(()=>checkedStatus(accepted({current_boundary:'failed_closed'})));
  const held=accepted({current_boundary:'failed_closed',runtime_authorized:false,P9_G1_accepted:false});
  assert.equal((await verifiedStatus(held)).runtime_authorized,false);
});
