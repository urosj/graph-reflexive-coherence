import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import {readFileSync} from 'node:fs';
import {G2_REGISTRY} from './g2-registry.js';
import {AGGREGATE_REVIEW} from './aggregate-review.js';
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

test('parent successor cannot promote support or substitute an authority identity', async () => {
  const {verifiedParents} = await import('./verification.js');
  for (const value of [null, {}, {authority_extension_digest:'0'.repeat(64)}, {
    authority_extension_digest:'3715d198eb15564ea459fcd0fdf9d7f185ddce4800cc9b66c31fed41b3f129a0',
    schema:'grcv4_p9492_parent_surface_v1', policy_id:'grcv4-previous-successful-primary-v1',
    G2_accepted:true, runtime_conformance_inferred:false, contracts:[],
  }]) await assert.rejects(verifiedParents(value));
});

const acceptedProfile = "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d";
// Synthetic browser-validation inputs, not a recorded API run or new evidence.
// Build current profile views from the pinned roster, not checker internals.
const acceptedSupport = G2_REGISTRY.records.filter(r=>r.state==='accepted').map(r=>r.complete_profile_id).sort();
const retained = name => JSON.parse(readFileSync(new URL('../../../../../../../implementation/phase-9-grcv4/tranche-7/'+name, import.meta.url), 'utf8'));
function profileFixture() {
  const value = structuredClone(G2_REGISTRY.reconciliation_views);
  value.profile_g2 = G2_REGISTRY.records.map(r=>({
    ...Object.fromEntries(['profile_family_id','complete_profile_id','gate','state','review','acceptance'].map(k=>[k,r[k]])),
    G2_accepted:r.state==='accepted', G3_accepted:false, aggregate_closed:false,
    all_ordered_pairs_verified:false, new_runtime_iterations_authorized:[], admitted_specialization_support_sets:[]
  }));
  const preceding = [];
  for (const row of G2_REGISTRY.records) {
    if (row.adapter !== 'historical_c_os') {
      const accepted = row.state === 'accepted';
      value[row.view_key] = {
        ...row.review_metrics, gate:row.gate, record_path:row.review.path, record_digest:row.review.record_digest,
        status:accepted ? 'accepted' : 'pass_proposal_pending_G2_acceptance',
        user_accepted:accepted, G2_accepted:accepted, G3_accepted:false, aggregate_closed:false,
        all_ordered_pairs_verified:false, new_G2_support:accepted ? [row.complete_profile_id] : [],
        proposed_additional_support:[row.complete_profile_id], accepted_support_unchanged:[...preceding].sort(),
        obligations:Object.fromEntries(['G2-EXACT-PRODUCT','G2-ORDERED-ENDPOINTS','G2-INTEGRATED-REVIEW'].map(k=>[k,'satisfied_for_exact_declared_scope'])),
        ...(accepted ? {acceptance_path:row.acceptance.path, acceptance_digest:row.acceptance.record_digest,
          accepted_generic_runtime_support:[...acceptedSupport]} : {})
      };
    }
    if(row.state==='accepted') preceding.push(row.complete_profile_id);
  }
  value.profile_aggregate_reconciliation = structuredClone(AGGREGATE_REVIEW);
  return structuredClone(value);
}
function accepted(extra={}) {
  return fixture({schema:'phase9_governance_status_v2',runtime_authorized:true,P9_G1_accepted:true,
    ...profileFixture(),
    accepted_generic_runtime_support:[...acceptedSupport],
    g2_acceptance:{record_digest:'e7165dc2f4cfe159d397c7aa61ccfbc89a30909db888e6638ef1ffe5905ec6dd',gate:'P9-G2[C_OS]',alias:'P9-7.7-C_OS',G2_accepted:true,G3_accepted:false,tranche_4_status:'closed',accepted_generic_runtime_support:[acceptedProfile],new_runtime_iterations_authorized:[]},
    initializer_runtime:{
      status:'accepted', user_accepted:true, aggregate_closed:true,
      producer_implemented:true, payload_specification_complete:true, positive_migration_verified:true,
      release_id:'grcv4-spec-release-sha256:e44dcd77a78a752c0e62f559243b88faff0bf90af1ee11a587f25d27e8a8abc7',
      record_path:'implementation/phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntime.json',
      record_digest:retained('P9-7.2a-InitializerRuntime.json').record_digest,
      acceptance_path:'implementation/phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md',
      acceptance_sha256:'a64bfe5e90e331495b7351d0b010c73b1de01f44332232b6b4d7b23046d23191',
      tests_run:25, numerical_tests_rerun:0, G3_accepted:false, new_G2_support:[],
      accepted_migration_classes:['nonhistory_to_nonhistory','nonhistory_to_persistent','persistent_to_nonhistory','PC_to_CI_PC','CI_PC_to_PC','A_to_C','C_to_A'],
      positive_target_families:['A_OS','A_CI','A_PC','A_CI_PC','A_RG2b']
    },
    event_runtime:{
      status:'accepted', user_accepted:true, aggregate_closed:true,
      acceptance_path:'implementation/phase-9-grcv4/tranche-7/P9-7.2b-RuntimeReview.md',
      acceptance_sha256:'9ac06f87275fe656a2650334517be319b9eb7c98c2b9710dae263a349237120d',
      record_digest:retained('P9-7.2b-RuntimeAuditCorrection.json').record_digest,
      test_count:18, case_count:27, numerical_tests_rerun:0, G3_accepted:false, new_G2_support:[]
    },
    handoff_evidence:{status:'verified'},
    abundance_interface_authority:{record_digest:'d9488700be9624da8500c1e533aa65d33b4f36a3307748ad12fd66449d8fe053',policy_id:'grcv4-family-abundance-diagnostic-v1',release_id:'grcv4-spec-release-sha256:e2acd9df0cc02c5fd4bbed4989ff5d7da3a819adeb2950d922b8a6ef4bf35f24',G2_accepted:false,numeric_definition_admitted:false},
    runtime_authority_state:'accepted_P9_G1_bounded_implementation_not_conformance',
    approval_digest:'cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2',
    resource_acceptance:{record_digest:'3e71b580090ba1712dbec4a1718653c2057e4062200f3367ba0c1ed7adeae6fa',accepted_iterations:['P9-3.3']},
    numerical_pressure_acceptance:{record_digest:'0626df41be15fdb2d5a5a7b4fa6f8be52693f8d3ba40297ae98acbe334f480c1',accepted_iterations:['P9-3.4']},
    preservation_acceptance:{record_digest:'b866b4b5d9b8b7ecdf087fd6f2a6d879810ec19464a9d3368ddddaf4d2edf43b',accepted_iterations:['P9-3.5']},
    reference_transport_acceptance:{record_digest:'ff07f5d71ad094d4c28f3fafdd0c0ca1d74f9f34f18678c8ff6909029b24358a',accepted_iterations:['P9-4.1']},
    c_controls_acceptance:{record_digest:'b2834e343fc50fa447ca430475a064157d27b431e27eb64ee721ff52e66a6f15',accepted_iterations:['P9-4.3']},c_current_acceptance:{record_digest:'5ce39f22e2999ee6f375648263a5902f883866420b497822cbf7daaa6e043b43',accepted_iterations:['P9-4.2']},
    os_pass_acceptance:{record_digest:'37d61d733bf90b794e4c68f0b2d078f7d38b41aa3f4c0679457c24a3161ad074',accepted_iterations:['P9-4.4']},
    os_operations_acceptance:{record_digest:'b37b037f0baa0fe5e291c96deba0520933070077b8d5a6a64995fbca21b5e274',accepted_iterations:['P9-4.5']},
    specification_correction:{record_digest:'56f1d4378eb8273d261b76aff3b128c526fb5064fa3bceace5c73fbb1f9f9903',release_id:'grcv4-spec-release-sha256:7b8b4d4e32e48fd35f70421cce7f547eebb21dd81389764061efe6e1a8c19886'},
    receipt_parent_authority:{record_digest:'ba7d69189c527153828b02c2bb3311899b036a634446de9ad8f36af6592c28f8',policy_id:'grcv4-previous-successful-primary-v1',release_id:'grcv4-spec-release-sha256:f777519824f86c3e9382bcf9b45cba28554351506f354d3f778746e2aaff5c6b',G2_accepted:false},
    lifecycle_batch_authorization:{record_digest:'fe11cfd2db36a9e1a74301aeaf89e316a3e93e7d3f5ea9d5f1197e199ee27d6b',execution_order:['P9-4.7a','P9-4.7b'],audit_status:'findings_closed_after_correction',combined_audit_scope:['P9-4.6','P9-4.7a','P9-4.7b']},
    implementation_scope:Array.from({length:62},(_,i)=>({path:`synthetic/${i}`})),
    foundation_acceptance:{record_digest:'1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4',accepted_iterations:['P9-2.1','P9-2.2']},
    request_acceptance:{record_digest:'ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f',accepted_iterations:['P9-2.3']},
    result_acceptance:{record_digest:'9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0',accepted_iterations:['P9-2.4']},
    harness_acceptance:{record_digest:'e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896',accepted_iterations:['P9-2.5']},
    integration_acceptance:{record_digest:'e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2',accepted_iterations:['P9-2.6']},
    geometry_acceptance:{record_digest:'f119e1361500e72f58297bc8186f868954b4065c853fcdd089280a5d28f88618',accepted_iterations:['P9-3.1']},
    stage_acceptance:{record_digest:'425cd05eb85213185a4b531a09c16cefec4be992ac4755d404b5f263e09ebd0a',accepted_iterations:['P9-3.2']},
    dependency_ready_leaves:["P9-2.1","P9-2.2","P9-2.3","P9-2.4","P9-2.5","P9-2.6","P9-3.1","P9-3.2","P9-3.3","P9-3.4","P9-3.5","P9-4.1","P9-4.2","P9-4.3","P9-4.4","P9-4.5","P9-4.6","P9-4.7a","P9-4.7b","P9-4.9.1","P9-4.9.1a","P9-4.9.2","P9-4.9.3","P9-5.1","P9-5.2","P9-5.3","P9-5.4","P9-6.1a","P9-6.1b","P9-6.1c","P9-6.2a","P9-6.2b","P9-6.2c","P9-6.3a","P9-6.3b","P9-6.3c","P9-6.4a","P9-6.4b","P9-6.4c","P9-6.4d","P9-6.5","P9-7.1","P9-7.1-A_CI","P9-7.1-A_CI_PC","P9-7.1-A_OS","P9-7.1-A_PC","P9-7.1-A_RG2b","P9-7.1-C_CI","P9-7.1-C_CI_PC","P9-7.1-C_OS","P9-7.1-C_PC","P9-7.1-C_RG2b","P9-7.2a","P9-7.2a-A_CIPC_PC","P9-7.2a-A_C_DROP","P9-7.2a-A_C_NH","P9-7.2a-A_C_PC","P9-7.2a-A_NH_NH","P9-7.2a-A_NH_PC","P9-7.2a-A_PC_CIPC","P9-7.2a-A_PC_NH","P9-7.2a-C_CIPC_PC","P9-7.2a-C_NH_NH","P9-7.2a-C_NH_PC","P9-7.2a-C_OS-NH-NH","P9-7.2a-C_OS-UNSUPPORTED","P9-7.2a-C_PC_CIPC","P9-7.2a-C_PC_NH","P9-7.2a-C_TO_A_UNRESOLVED","P9-7.2b","P9-7.2b-C_OS-MAPPED","P9-7.3-C_OS","P9-7.4-C_OS","P9-7.5-C_OS","P9-7.6-C_OS"],permitted_runtime_paths:[...Array.from({length:15},(_,i)=>`synthetic/${i}`),'pyproject.toml','tests/models/grcv4_conformance_harness.py','tests/models/grcv4_reference_oracles.py','src/pygrc/models/__init__.py',"src/pygrc/models/grc_v4_geometry.py","src/pygrc/models/grc_v4_transport.py","tests/models/test_grc_v4_geometry.py","tests/models/test_grc_v4_transport.py","src/pygrc/models/grc_v4_candidate_c.py","tests/models/test_grc_v4_candidate_c.py","src/pygrc/models/grc_v4_realizations.py","tests/models/test_grc_v4_realizations.py","src/pygrc/models/grc_v4_lifecycle.py","tests/models/test_grc_v4_lifecycle.py","src/pygrc/models/grc_v4_candidate_a.py","tests/models/test_grc_v4_candidate_a.py","src/pygrc/models/grc_v4_ci.py","tests/models/test_grc_v4_ci.py","src/pygrc/models/grc_v4_pc.py","tests/models/test_grc_v4_pc.py","tests/models/test_grc_v4_cipc.py","src/pygrc/models/grc_v4_rg2b.py","tests/models/test_grc_v4_rg2b.py","src/pygrc/models/grc_v4_rg2b_graph.py","tests/models/test_grc_v4_rg2b_graph.py","tests/models/test_grc_v4_generic_lifecycle.py","src/pygrc/models/grc_v4_migration.py","tests/models/test_grc_v4_migration.py","src/pygrc/models/grc_v4_initializer.py","tests/models/test_grc_v4_initializer.py","src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-release.json","src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json","src/pygrc/models/grc_v4_events.py","tests/models/test_grc_v4_events.py","tests/models/test_grc_v4_event_audit.py"],
    iterations:[4,5,6,7,8,9].map(i=>({iteration_id:`P9-1.${i}`,status:'implemented_and_verified',reviewer_decision:'accepted_by_user'})),...extra});
}

function held(extra={}) {
  const value=accepted();
  for (const key of [...Object.keys(profileFixture()), 'g2_acceptance','initializer_runtime','event_runtime',
    'implementation_scope','dependency_ready_leaves','permitted_runtime_paths','foundation_acceptance','request_acceptance',
    'result_acceptance','harness_acceptance','integration_acceptance','geometry_acceptance','stage_acceptance',
    'resource_acceptance','numerical_pressure_acceptance','preservation_acceptance','reference_transport_acceptance',
    'c_current_acceptance','c_controls_acceptance','os_pass_acceptance','os_operations_acceptance',
    'lifecycle_batch_authorization','specification_correction','receipt_parent_authority','abundance_interface_authority',
    'status_digest']) delete value[key];
  return fixture({...value,current_boundary:'failed_closed',runtime_authorized:false,
    accepted_generic_runtime_support:[],runtime_authority_state:'accepted_P9_G1_current_work_held',...extra});
}
test('accepted G1 permission does not independently grant profile support',async()=>{
  assert.equal((await verifiedStatus(accepted())).P9_G1_accepted,true);
  const missingPackage=accepted({permitted_runtime_paths:Array.from({length:43},(_,i)=>`synthetic/${i}`)});
  assert.throws(()=>checkedStatus(missingPackage),/dependency-ready/);
  const missingExport=accepted();
  missingExport.permitted_runtime_paths[18]='synthetic/no-export-owner';
  assert.throws(()=>checkedStatus(missingExport),/dependency-ready/);
  for(const extra of [{approval_digest:'0'.repeat(64)},{runtime_authorized:false},{accepted_generic_runtime_support:['C_OS']},{admitted_specialization_support_sets:[['C_OS']]},{implementation_scope:[]},{dependency_ready_leaves:['P9-8.2']}]) assert.throws(()=>checkedStatus(accepted(extra)));
});

test('current fixtures are detached from each other and the trusted browser roster', () => {
  const first=accepted(), second=accepted();
  const registryBefore=canonical(G2_REGISTRY), aggregateBefore=canonical(AGGREGATE_REVIEW);
  first.profile_g2[1].review.record_digest='0'.repeat(64);
  first.profile_g2[1].acceptance.record_digest='0'.repeat(64);
  first.profile_aggregate_reconciliation.accepted_generic_runtime_support.pop();
  first.a_os_crossings.user_accepted=false;
  first.a_os_g2_review.accepted_generic_runtime_support.pop();
  assert.equal(canonical(G2_REGISTRY),registryBefore);
  assert.equal(canonical(AGGREGATE_REVIEW),aggregateBefore);
  checkedStatus(second);
  checkedStatus(accepted());
  assert.throws(()=>checkedStatus(first),/registry projection/);
});

test('valid current status reaches each targeted registry and aggregate rejection', () => {
  const reject=(edit,reason)=>{
    const value=accepted();
    checkedStatus(value); // An invalid starting fixture must never mask the target assertion.
    edit(value);
    const rehashed=fixture(value);
    assert.throws(()=>checkedStatus(rehashed),reason);
  };
  reject(v=>v.profile_g2.pop(),/registry projection/);
  reject(v=>v.accepted_generic_runtime_support.pop(),/support/);
  reject(v=>{v.accepted_generic_runtime_support=[acceptedProfile];},/support/);
  for(const row of G2_REGISTRY.records.filter(r=>r.adapter!=='historical_c_os')) {
    reject(v=>delete v[row.view_key],/Missing registered G2 view/);
    reject(v=>{v[row.view_key].acceptance_digest='0'.repeat(64);},/G2 acceptance/);
    reject(v=>{v[row.view_key].catalog_cells-=1;},/registered G2 review/);
  }
  reject(v=>delete v.a_os_local_product,/bounded reconciliation view/);
  reject(v=>delete v.profile_aggregate_reconciliation,/aggregate reconciliation/);
  reject(v=>{v.profile_aggregate_reconciliation.aggregate_closed=true;},/aggregate reconciliation/);
});

test('held projection removes every current profile view without erasing historical G1 acceptance', () => {
  const value=held();
  checkedStatus(value);
  assert.equal(value.P9_G1_accepted,true);
  assert.equal(value.runtime_authorized,false);
  for(const [key,projection] of Object.entries(profileFixture())) {
    assert.equal(value[key],undefined,key);
    assert.throws(()=>checkedStatus(fixture({...value,[key]:projection})),key);
  }
  for(const key of ['initializer_runtime','event_runtime'])
    assert.throws(()=>checkedStatus(fixture({...value,[key]:accepted()[key]})),key);
});
test('failed G1 boundary cannot retain permission even with a recomputed digest',async()=>{
  assert.throws(()=>checkedStatus(accepted({current_boundary:'failed_closed'})));
  const value=held({P9_G1_accepted:false});
  assert.equal((await verifiedStatus(value)).runtime_authorized,false);
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
  const value=held();
  assert.equal((await verifiedStatus(value)).P9_G1_accepted,true);
  assert.equal(value.runtime_authorized,false);
  assert.throws(()=>checkedStatus({...value,approval_digest:'0'.repeat(64)}));
});

test('committed foundation acceptance does not accept request work or conformance',()=>{
  for(const foundation_acceptance of [undefined,{},
    {record_digest:'0'.repeat(64),accepted_iterations:['P9-2.1','P9-2.2']},
    {record_digest:'1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4',accepted_iterations:['P9-2.1','P9-2.2','P9-2.3']}])
    assert.throws(()=>checkedStatus(accepted({foundation_acceptance})),/foundation/);
  assert.throws(()=>checkedStatus(accepted({dependency_ready_leaves:['P9-2.1','P9-2.2','P9-2.3','P9-2.4','P9-2.5','P9-2.6','P9-3.1','P9-3.2','P9-3.3','P9-3.4','P9-3.5','P9-4.2']})),/dependency-ready/);
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

test('geometry acceptance cannot be missing, forged or accept stage work',()=>{
  for(const geometry_acceptance of [undefined,{},
    {record_digest:'0'.repeat(64),accepted_iterations:['P9-3.1']},
    {record_digest:'f119e1361500e72f58297bc8186f868954b4065c853fcdd089280a5d28f88618',accepted_iterations:['P9-3.1','P9-3.2']}])
    assert.throws(()=>checkedStatus(accepted({geometry_acceptance})),/accepted geometry/);
});

test('stage acceptance cannot be missing, forged or accept stage work',()=>{
  for(const stage_acceptance of [undefined,{},
    {record_digest:'0'.repeat(64),accepted_iterations:['P9-3.2']},
    {record_digest:'425cd05eb85213185a4b531a09c16cefec4be992ac4755d404b5f263e09ebd0a',accepted_iterations:['P9-3.2','P9-3.3']}])
    assert.throws(()=>checkedStatus(accepted({stage_acceptance})),/accepted stages/);
});

test('resource acceptance cannot be omitted or expanded', () => {
  for (const resource_acceptance of [undefined, {}, {record_digest:'0'.repeat(64),accepted_iterations:['P9-3.3']},
    {record_digest:'3e71b580090ba1712dbec4a1718653c2057e4062200f3367ba0c1ed7adeae6fa',accepted_iterations:['P9-3.3','P9-3.4']}])
    assert.throws(() => checkedStatus(accepted({resource_acceptance})), /accepted resources/);
});

test('numerical pressure acceptance cannot be omitted or expanded', () => {
  for (const numerical_pressure_acceptance of [undefined, {}, {record_digest:'0'.repeat(64),accepted_iterations:['P9-3.4']},
    {record_digest:'0626df41be15fdb2d5a5a7b4fa6f8be52693f8d3ba40297ae98acbe334f480c1',accepted_iterations:['P9-3.4','P9-3.5']}])
    assert.throws(() => checkedStatus(accepted({numerical_pressure_acceptance})), /accepted numerical pressure/);
});

test("prestate acceptance is authenticated", () => {
  for (const preservation_acceptance of [undefined, {}, {record_digest:"0".repeat(64),accepted_iterations:["P9-3.5"]},
    {record_digest:"b866b4b5d9b8b7ecdf087fd6f2a6d879810ec19464a9d3368ddddaf4d2edf43b",accepted_iterations:["P9-3.5","P9-4.1"]}])
    assert.throws(() => checkedStatus(accepted({preservation_acceptance})), /accepted prestate preservation/);
});

test("C reference transport requires its own acceptance", () => {
  for (const reference_transport_acceptance of [undefined, {}, {record_digest:"0".repeat(64),accepted_iterations:["P9-4.1"]}, {record_digest:"ff07f5d71ad094d4c28f3fafdd0c0ca1d74f9f34f18678c8ff6909029b24358a",accepted_iterations:["P9-4.1","P9-4.2"]}])
    assert.throws(() => checkedStatus(accepted({reference_transport_acceptance})), /accepted C reference transport/);
});

test("C stage current requires its own acceptance", () => {
  for (const c_current_acceptance of [undefined, {}, {record_digest:"0".repeat(64),accepted_iterations:["P9-4.2"]}, {record_digest:"5ce39f22e2999ee6f375648263a5902f883866420b497822cbf7daaa6e043b43",accepted_iterations:["P9-4.2","P9-4.3"]}])
    assert.throws(() => checkedStatus(accepted({c_current_acceptance})), /accepted C stage current/);
});

test("C controls require their own acceptance", () => {
  for (const c_controls_acceptance of [undefined, {}, {record_digest:"0".repeat(64),accepted_iterations:["P9-4.3"]}, {record_digest:"b2834e343fc50fa447ca430475a064157d27b431e27eb64ee721ff52e66a6f15",accepted_iterations:["P9-4.3","P9-4.4"]}])
    assert.throws(() => checkedStatus(accepted({c_controls_acceptance})), /accepted C control derivative/);
});

test('OS pass acceptance cannot be missing, forged or promote ordinary vectors',()=>{
  for (const os_pass_acceptance of [undefined, {record_digest:'0'.repeat(64),accepted_iterations:['P9-4.4']}, {...accepted().os_pass_acceptance,accepted_iterations:['P9-4.4','P9-4.5']}]) assert.throws(()=>checkedStatus(accepted({os_pass_acceptance})), /OS pass/);
});

test('OS operation acceptance cannot open lifecycle without accepted source',()=>{
  for (const os_operations_acceptance of [undefined, {}, {record_digest:'0'.repeat(64),accepted_iterations:['P9-4.5']}, {...accepted().os_operations_acceptance,accepted_iterations:['P9-4.5','P9-4.6']}]) assert.throws(()=>checkedStatus(accepted({os_operations_acceptance})), /OS operations/);
});

test('ordered lifecycle batch cannot imply audit closure or open G2', () => {
  const valid = accepted();
  checkedStatus(valid);
  for (const changed of [undefined, {...valid.lifecycle_batch_authorization, audit_status:'pending'}, {...valid.lifecycle_batch_authorization, audit_status:'complete'}, {...valid.lifecycle_batch_authorization, execution_order:['P9-4.7b','P9-4.7a']}, {...valid.lifecycle_batch_authorization, combined_audit_scope:['P9-4.7a','P9-4.7b']}, {...valid.lifecycle_batch_authorization, record_digest:'0'.repeat(64)}]) assert.throws(()=>checkedStatus(accepted({lifecycle_batch_authorization:changed})));
  assert.throws(()=>checkedStatus(accepted({dependency_ready_leaves:[...valid.dependency_ready_leaves,'P9-4.8']})));
});

test('successor specification authority cannot be omitted or forged', () => {
  const valid = accepted();
  for (const changed of [undefined, {...valid.specification_correction, record_digest:'0'.repeat(64)}, {...valid.specification_correction, release_id:'predecessor'}]) assert.throws(()=>checkedStatus(accepted({specification_correction:changed})));
});

test('accepted fixture readiness cannot imply a detector or open the final review', () => {
  const valid = accepted();
  checkedStatus(valid);
  assert.equal(valid.dependency_ready_leaves.length, 75);
  assert.throws(()=>checkedStatus(accepted({dependency_ready_leaves:valid.dependency_ready_leaves.filter(leaf=>leaf!=='P9-4.9.3')})), /dependency-ready/);
  for (const changed of [undefined, {...valid.abundance_interface_authority, record_digest:'0'.repeat(64)}, {...valid.abundance_interface_authority, release_id:'predecessor'}, {...valid.abundance_interface_authority, numeric_definition_admitted:true}, {...valid.abundance_interface_authority, G2_accepted:true}]) assert.throws(()=>checkedStatus(accepted({abundance_interface_authority:changed})));
  // Duplicate fixture permission and premature review permission both reject.
  for (const leaf of ['P9-4.9.3','P9-4.8B']) assert.throws(()=>checkedStatus(accepted({dependency_ready_leaves:[...valid.dependency_ready_leaves,leaf]})));
});

test('G2 acceptance is an exact registry; the historical C_OS decision stays a singleton', async () => {
  const value = await verifiedStatus(accepted());
  assert.deepEqual(value.accepted_generic_runtime_support, acceptedSupport);
  assert.equal(acceptedSupport.length, 10);
  assert.deepEqual(value.g2_acceptance.accepted_generic_runtime_support, [acceptedProfile]);
  for (const support of [[], ['C_OS'], [acceptedProfile, 'A_OS'], [acceptedProfile, acceptedProfile]])
    assert.throws(() => checkedStatus(accepted({accepted_generic_runtime_support:support})), /support/);
  for (const g2 of [undefined, {...value.g2_acceptance,record_digest:'0'.repeat(64)}, {...value.g2_acceptance,G3_accepted:true}, {...value.g2_acceptance,accepted_generic_runtime_support:['C_OS']}, {...value.g2_acceptance,new_runtime_iterations_authorized:['P9-8.1']}, {...value.g2_acceptance,tranche_4_status:'pending'}])
    assert.throws(() => checkedStatus(accepted({g2_acceptance:g2})), /G2/);
});

test('A current/writer permission cannot imply later A work or A conformance', () => {
  const valid = accepted();
  checkedStatus(valid);
  for (const leaves of [valid.dependency_ready_leaves.filter(x => x !== 'P9-5.1'), valid.dependency_ready_leaves.filter(x => x !== 'P9-5.4'), [...valid.dependency_ready_leaves, 'P9-7.2a-A_OS']])
    assert.throws(() => checkedStatus(accepted({dependency_ready_leaves: leaves})), /dependency-ready/);
  const paths = valid.permitted_runtime_paths.filter(x => x !== 'src/pygrc/models/grc_v4_candidate_a.py');
  paths.push('synthetic/replacement');
  assert.throws(() => checkedStatus(accepted({permitted_runtime_paths:paths})), /dependency-ready/);
  assert.throws(() => checkedStatus(accepted({accepted_generic_runtime_support:[acceptedProfile, 'A_OS']})), /support/);
});

test('full 7.1 permission requires every child without inventing event leaves or G2 support', () => {
  const valid = accepted();
  for (const candidate of ['A', 'C']) for (const realization of ['OS', 'CI', 'RG2b', 'PC', 'CI_PC']) {
    const id = `P9-7.1-${candidate}_${realization}`;
    assert.ok(valid.dependency_ready_leaves.includes(id));
    assert.throws(() => checkedStatus(accepted({dependency_ready_leaves: valid.dependency_ready_leaves.filter(x => x !== id)})), /dependency-ready/);
  }
  assert.throws(() => checkedStatus(accepted({dependency_ready_leaves: [...valid.dependency_ready_leaves, 'P9-7.2b-A_PC']})), /dependency-ready/);
  assert.throws(() => checkedStatus(accepted({accepted_generic_runtime_support: [acceptedProfile, 'C_PC']})), /support/);
  const paths = valid.permitted_runtime_paths.filter(x => x !== 'tests/models/test_grc_v4_generic_lifecycle.py');
  paths.push('synthetic/replacement');
  assert.throws(() => checkedStatus(accepted({permitted_runtime_paths: paths})), /dependency-ready/);
});

test('scoped 7.2a permission retains historical leaf IDs without promoting support', () => {
  const valid = accepted();
  const leaves = valid.dependency_ready_leaves.filter(x => x.startsWith('P9-7.2a'));
  assert.equal(leaves.length, 17); // 15 new scoped leaves plus two historical C_OS children.
  assert.ok(leaves.includes('P9-7.2a-C_TO_A_UNRESOLVED')); // Historical leaf ID, not the current initializer disposition.
  assert.equal(valid.initializer_runtime.positive_migration_verified,true);
  for (const id of leaves)
    assert.throws(() => checkedStatus(accepted({dependency_ready_leaves: valid.dependency_ready_leaves.filter(x => x !== id)})), /dependency-ready/);
  for (const path of ['src/pygrc/models/grc_v4_migration.py', 'tests/models/test_grc_v4_migration.py']) {
    const paths = valid.permitted_runtime_paths.map(x => x === path ? 'synthetic/missing-migration-owner' : x);
    assert.throws(() => checkedStatus(accepted({permitted_runtime_paths: paths})), /dependency-ready/);
  }
  assert.throws(() => checkedStatus(accepted({accepted_generic_runtime_support: [acceptedProfile, 'A_CI']})), /support/);
});
