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
    handoff_evidence:{status:'verified'},
    runtime_authority_state:'accepted_P9_G1_bounded_implementation_not_conformance',
    approval_digest:'cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2',
    implementation_scope:Array.from({length:43},(_,i)=>({path:`synthetic/${i}`})),
    foundation_acceptance:{record_digest:'1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4',accepted_iterations:['P9-2.1','P9-2.2']},
    request_acceptance:{record_digest:'ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f',accepted_iterations:['P9-2.3']},
    result_acceptance:{record_digest:'9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0',accepted_iterations:['P9-2.4']},
    harness_acceptance:{record_digest:'e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896',accepted_iterations:['P9-2.5']},
    integration_acceptance:{record_digest:'e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2',accepted_iterations:['P9-2.6']},
    dependency_ready_leaves:['P9-2.1','P9-2.2','P9-2.3','P9-2.4','P9-2.5','P9-2.6','P9-3.1'],permitted_runtime_paths:[...Array.from({length:15},(_,i)=>`synthetic/${i}`),'pyproject.toml','tests/models/grcv4_conformance_harness.py','tests/models/grcv4_reference_oracles.py','src/pygrc/models/__init__.py',"src/pygrc/models/grc_v4_geometry.py","src/pygrc/models/grc_v4_transport.py","tests/models/test_grc_v4_geometry.py","tests/models/test_grc_v4_transport.py"],
    iterations:[4,5,6,7,8,9].map(i=>({iteration_id:`P9-1.${i}`,status:'implemented_and_verified',reviewer_decision:'accepted_by_user'})),...extra});
}
test('accepted G1 permission does not imply accepted profile support',async()=>{
  assert.equal((await verifiedStatus(accepted())).P9_G1_accepted,true);
  const missingPackage=accepted({permitted_runtime_paths:Array.from({length:23},(_,i)=>`synthetic/${i}`)});
  assert.throws(()=>checkedStatus(missingPackage),/dependency-ready/);
  const missingExport=accepted();
  missingExport.permitted_runtime_paths[18]='synthetic/no-export-owner';
  assert.throws(()=>checkedStatus(missingExport),/dependency-ready/);
  for(const extra of [{approval_digest:'0'.repeat(64)},{runtime_authorized:false},{accepted_generic_runtime_support:['C_OS']},{admitted_specialization_support_sets:[['C_OS']]},{implementation_scope:[]},{dependency_ready_leaves:['P9-8.2']}]) assert.throws(()=>checkedStatus(accepted(extra)));
});
test('failed G1 boundary cannot retain permission even with a recomputed digest',async()=>{
  assert.throws(()=>checkedStatus(accepted({current_boundary:'failed_closed'})));
  const held=accepted({current_boundary:'failed_closed',runtime_authorized:false,P9_G1_accepted:false});
  assert.equal((await verifiedStatus(held)).runtime_authorized,false);
});

test('missing and invalid handoff evidence do not change accepted permission',async()=>{
  for(const status of ['unavailable','invalid']) {
    const value=await verifiedStatus(accepted({handoff_evidence:{status}}));
    assert.equal(value.P9_G1_accepted,true);
    assert.equal(value.runtime_authorized,true);
  }
  assert.throws(()=>checkedStatus(accepted({handoff_evidence:{status:'green'}})));
});

test('current work can be held while historical acceptance remains verified',async()=>{
  const value=accepted({current_boundary:'failed_closed',runtime_authorized:false,runtime_authority_state:'accepted_P9_G1_current_work_held'});
  for(const key of ['implementation_scope','dependency_ready_leaves','permitted_runtime_paths','foundation_acceptance','request_acceptance','result_acceptance','harness_acceptance','integration_acceptance','status_digest']) delete value[key];
  value.status_digest=createHash('sha256').update(canonical(value)).digest('hex');
  assert.equal((await verifiedStatus(value)).P9_G1_accepted,true);
  assert.equal(value.runtime_authorized,false);
  assert.throws(()=>checkedStatus({...value,approval_digest:'0'.repeat(64)}));
});

test('committed foundation acceptance does not accept request work or conformance',()=>{
  for(const foundation_acceptance of [undefined,{},
    {record_digest:'0'.repeat(64),accepted_iterations:['P9-2.1','P9-2.2']},
    {record_digest:'1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4',accepted_iterations:['P9-2.1','P9-2.2','P9-2.3']}])
    assert.throws(()=>checkedStatus(accepted({foundation_acceptance})),/foundation/);
  assert.throws(()=>checkedStatus(accepted({dependency_ready_leaves:['P9-2.1','P9-2.2','P9-2.3','P9-2.4','P9-2.5','P9-2.6','P9-3.1','P9-3.2']})),/dependency-ready/);
});

 test('request acceptance cannot be missing or promote result work',()=>{
   for (const request_acceptance of [undefined,{}, {record_digest:'ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f',accepted_iterations:['P9-2.3','P9-2.4']}])
     assert.throws(()=>checkedStatus(accepted({request_acceptance})),/accepted requests/);
 });

test('result acceptance cannot be missing or accept harness work',()=>{
  for(const result_acceptance of [undefined,{}, {record_digest:'9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0',accepted_iterations:['P9-2.4','P9-2.5']}])
    assert.throws(()=>checkedStatus(accepted({result_acceptance})),/accepted results/);
  const missingHarness=accepted();
  missingHarness.permitted_runtime_paths[16]='synthetic/no-harness';
  assert.throws(()=>checkedStatus(missingHarness),/dependency-ready/);
});

test('harness acceptance cannot be missing or accept integration work',()=>{
  for(const harness_acceptance of [undefined,{}, {record_digest:'e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896',accepted_iterations:['P9-2.5','P9-2.6']}])
    assert.throws(()=>checkedStatus(accepted({harness_acceptance})),/accepted harness/);
});


test('integration acceptance cannot be missing, forged or accept geometry work',()=>{
  for(const integration_acceptance of [undefined,{},
    {record_digest:'0'.repeat(64),accepted_iterations:['P9-2.6']},
    {record_digest:'e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2',accepted_iterations:['P9-2.6','P9-3.1']}])
    assert.throws(()=>checkedStatus(accepted({integration_acceptance})),/accepted integration/);
  for(const path of ['src/pygrc/models/grc_v4_geometry.py','src/pygrc/models/grc_v4_transport.py','tests/models/test_grc_v4_geometry.py','tests/models/test_grc_v4_transport.py']) {
    const value=accepted();
    value.permitted_runtime_paths[value.permitted_runtime_paths.indexOf(path)]='synthetic/missing-owner';
    assert.throws(()=>checkedStatus(value),/dependency-ready/);
  }
});
