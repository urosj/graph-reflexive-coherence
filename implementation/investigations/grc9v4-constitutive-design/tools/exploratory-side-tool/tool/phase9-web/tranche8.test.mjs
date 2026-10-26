import {test} from 'node:test';
import assert from 'node:assert/strict';
import {TRANCHE8_EVIDENCE as evidence} from './tranche8-evidence.js';
import {checkedTranche8, renderTranche8, sourceURL, tranche8Loader, checkedSelectedRuntime, selectedRuntimeLoader} from './tranche8.js';

const element = tag => ({tag, textContent:'', children:[], append(...nodes){this.children.push(...nodes);}, replaceChildren(...nodes){this.children=nodes;}});
const text = node => node.textContent + node.children.map(text).join(' ');

test('full historical index distinguishes provenance from current conformance',()=>{
  assert.equal(evidence.verification.historical_8_4b_source_bindings_authenticated,true);
  assert.equal(evidence.verification.current_runtime_conformance_inferred,false);
  assert.equal(evidence.verification.native_trajectories_rerun,false);
  assert.match(evidence.runtime_scope_note,/Historical display roster only/);
  assert.match(evidence.verification.boundary_source_revision,/^[a-f0-9]{40}$/);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/current-code conformance or execution authorization is inferred/);
  const bad=structuredClone(evidence);bad.verification.current_runtime_conformance_inferred=true;
  assert.throws(()=>checkedTranche8(bad));
});

const selectedACI=()=>({schema:'phase9_tranche8_family_status_v1',family:'A_CI',checkpoint:'8.4h',
  runtime:structuredClone(evidence.coverage.larger_runtime.find(r=>r.family==='A_CI')),
  source_refs:evidence.source_refs.filter(r=>r.basis==='pinned_A_CI_8_4h_not_acceptance'),
  other_families_checked:false,native_trajectories_rerun:false});

test('selected A_CI browser loads its scoped route and clears unavailable evidence',async()=>{
  const out=element('div'),status=element('p');let fail=false;const urls=[];
  const load=selectedRuntimeLoader('A_CI',out,status,async url=>{
    urls.push(url);return {ok:!fail,json:async()=>selectedACI()};
  },element);
  await load();assert.deepEqual(urls,['/api/tranche8?family=A_CI&checkpoint=8.4h']);
  assert.match(text(out),/9 events; 36 target steps; 2 final roots/);
  assert.match(text(out),/Accepted: true/);assert.match(status.textContent,/unrelated checks remain separate/);
  const links=out.children.at(-1).children.filter(e=>e.tag==='a');
  assert.ok(links.length>0);assert.ok(links.every(e=>e.href.includes('family=A_CI&checkpoint=8.4h&path=')));
  fail=true;await load();assert.equal(out.children.length,0);assert.match(status.textContent,/Unavailable/);
});

test('selected A_CI rejects widened scope, altered rows and missing evidence links',()=>{
  assert.doesNotThrow(()=>checkedSelectedRuntime(selectedACI(),'A_CI'));
  for(const mutate of [v=>v.other_families_checked=true,v=>v.runtime.user_accepted=false,
      v=>v.source_refs=[],v=>v.source_refs[0].sha256='forged']) {
    const bad=structuredClone(selectedACI());mutate(bad);assert.throws(()=>checkedSelectedRuntime(bad,'A_CI'));
  }
});

test('A_CI 8.4h exposes scoped acceptance with unchanged execution flags', () => {
  const row=evidence.coverage.larger_runtime.find(r=>r.family==='A_CI');
  assert.equal(row.native_steps,1);assert.equal(row.total_native_events,9);
  assert.equal(row.total_target_steps,36);assert.equal(row.final_reads,2);
  assert.equal(row.continuation.baseline_complete,true);assert.equal(row.covariance.covariance_complete,true);
  assert.equal(row.unsigned_candidate_history,true);assert.equal(row.full_joint_roots,true);
  assert.equal(row.user_accepted,true);assert.equal(row.accepted_on,'2026-10-26');
  assert.equal(row.original_execution_flags_unchanged,true);assert.equal(row.aggregate_closed,false);
  assert.equal(row.native_numerics_rerun,false);assert.equal(row.uniform_trajectory_enclosure,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/8.4h A_CI — bounded joint-root event integration/);
  assert.match(text(out),/A_CI preserves unsigned candidate history/);
  assert.match(text(out),/A_CI larger covariance: 8\/8 transformed events and 16\/16 one-step histories/);
  for (const [key,value] of [['user_accepted',false],['aggregate_closed',true],['total_native_events',10],['total_target_steps',40],['unsigned_candidate_history',false]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime.find(r=>r.family==='A_CI')[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
});

test('C_CI 8.4h records scoped acceptance without changing execution flags', () => {
  const row=evidence.coverage.larger_runtime.find(r=>r.family==='C_CI');
  assert.equal(row.native_steps,1);assert.equal(row.target_steps,20);assert.equal(row.final_reads,2);
  assert.equal(row.native_events,1);
  assert.equal(row.status,'baseline_and_covariance_accepted');
  assert.equal(row.original_execution_flags_unchanged,true);
  assert.equal(row.accepted_on,'2026-10-21');
  assert.equal(row.covariance.covariance_complete,true);
  assert.equal(row.covariance.native_events,8);assert.equal(row.covariance.target_steps,16);
  assert.equal(row.total_native_events,9);assert.equal(row.total_target_steps,36);
  assert.equal(row.continuation.baseline_complete,true);
  assert.equal(row.continuation.uniform_trajectory_enclosure,false);
  assert.equal(row.source_full_joint_parity,true);assert.equal(row.fresh_trigger.eligible,true);
  assert.equal(row.user_accepted,true);assert.equal(row.aggregate_closed,false);
  assert.equal(row.native_numerics_rerun,false);assert.equal(row.covariance_executed,true);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/C_CI — bounded joint-root event integration/);
  assert.match(text(out),/local exact-root resource enclosures/);
  assert.match(text(out),/8\/8 transformed events and 16\/16 one-step histories/);
  for(const [key,value] of [['native_steps',2],['target_steps',36],['user_accepted',false],['covariance_executed',false]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime.find(r=>r.family==='C_CI')[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
});

test('C_OS 8.4h distinguishes completed bounded coverage from acceptance', () => {
  const row=evidence.coverage.larger_runtime[0];
  assert.equal(row.family,'C_OS');assert.equal(row.original_trigger.eligible,false);
  assert.equal(row.fresh_trigger.eligible,true);assert.equal(row.oracle_steps,2);
  assert.equal(row.source_beats_before_request,2);assert.equal(row.initial_conditions_unchanged,true);
  assert.equal(row.dense_screen_steps,20);assert.equal(row.exact_reused_reset_cases,1);
  assert.equal(row.native_steps,38);assert.equal(row.native_events,9);
  assert.equal(row.status,'native_baseline_and_covariance_accepted');
  assert.equal(row.original_execution_flags_unchanged,true);
  assert.equal(row.aggregate_closed,false);
  assert.equal(row.native.native_events,0);
  assert.equal(row.event_successor.outcome,'completed');assert.equal(row.event_successor.native_events,1);
  assert.equal(row.event_successor.both_role_admission_checked,true);
  assert.equal(row.event_successor.failed_attempt_artifact_retained,false);
  assert.equal(row.event_successor.native_numerics_rerun,false);
  assert.deepEqual(row.event_successor.target_steps_by_role,{current:0,reset:0});
  assert.deepEqual(row.native.failures,[]);
  assert.match(row.native.timeout_note,/artifact removed at user request/);
  assert.equal(row.performance.full_read_parity,true);
  assert.equal(row.performance.event_execution,false);
  assert.equal(row.continuation.target_steps,20);assert.equal(row.continuation.final_reads,2);
  assert.equal(row.continuation.baseline_complete,true);assert.equal(row.continuation.native_numerics_rerun,false);
  assert.equal(row.continuation.uniform_trajectory_enclosure,false);
  assert.equal(row.continuation.first_steps_match_certified_oracle,true);
  assert.equal(row.covariance_executed,true);assert.equal(row.user_accepted,true);
  assert.equal(row.covariance.mechanical_transforms.length,8);
  assert.equal(row.covariance.native_events,8);assert.equal(row.covariance.target_steps,16);
  assert.deepEqual(row.covariance.completed_numerical_transforms,row.covariance.required_transforms);
  assert.deepEqual(row.covariance.pending_numerical_transforms,[]);
  assert.equal(row.covariance.transformed_horizon,1);assert.equal(row.covariance.covariance_complete,true);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Oracle success is not native runtime acceptance/);
  assert.match(text(out),/No success credit/);
  assert.match(text(out),/Measured single OS read/);
  assert.match(text(out),/Separately bound event successor: completed/);
  assert.match(text(out),/20\/20 native steps and 2\/2 fresh final reads/);
  assert.match(text(out),/Completed numerical counterparts: edge_order, node_order, relabel, signed, combined, rotate, rotate_twice, reflect/);
  for(const [key,value] of [['native_events',0],['native_steps',20],['user_accepted',false],['aggregate_closed',true],['covariance_executed',false]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime[0][key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const [key,value] of [['native_events',9],['target_steps',20],['transformed_horizon',10],['covariance_complete',false],['source_prefix_rerun',true],['pending_numerical_transforms',['rotate_twice']],['user_accepted',true]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime[0].covariance[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const [key,value] of [['native_events',0],['both_role_admission_checked',false],['user_accepted',true],['native_numerics_rerun',true]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime[0].event_successor[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const [key,value] of [['target_steps',18],['final_reads',0],['user_accepted',true],['native_numerics_rerun',true],['uniform_trajectory_enclosure',true],['covariance_executed',true]]) {
    const bad=structuredClone(evidence);bad.coverage.larger_runtime[0].continuation[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
});

test('A_PC larger chart research retains exclusions and separates native successor credit', () => {
  const row=evidence.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC');
  assert.equal(row.pc_whole_chart,true);
  assert.deepEqual(row.cases.map(c=>c.resource_sign),['nonnegative','nonnegative','nonnegative','excluded']);
  assert.equal(row.native_steps,4);assert.equal(row.ready_for_8_4h,true);
  assert.equal(row.pc_native.native_reads,12);assert.equal(row.pc_native.native_prerequisites_complete,true);
  assert.equal(row.pc_native.committed_steps,0);assert.equal(row.pc_native.user_accepted,true);
  assert.equal(row.pc_native.original_execution_flags_unchanged,true);
  assert.equal(row.pc_native.historical_target_attempts.length,2);
  assert.ok(row.pc_native.historical_target_attempts.every(c=>c.native_steps===0 && c.outcome==='incomplete'));
  assert.equal(row.scalar_certificates_recomputed,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Carrier admission is not resource continuation/);
  assert.deepEqual(row.feasibility.shares,['1/4','3/8','3/8']);
  assert.equal(row.feasibility.event_pair.reset_evolves,false);
  assert.equal(row.feasibility.poststate_read_executed,false);
  assert.equal(row.feasibility.interval_research_recomputed,false);
  assert.match(text(out),/A_PC separately derived feasibility companion/);
  assert.match(text(out),/Updated source Z is not diagonal/);
  assert.match(text(out),/Target first-step carrier-to-current response is not resolved/);
  assert.equal(row.pc_staged.native_steps,0);assert.equal(row.pc_staged.ready_for_8_4h,false);
  assert.ok(row.pc_staged.cases.every(c=>c.final_read_executed && c.nonzero_offdiagonal_carrier_entries>0));
  assert.deepEqual(row.pc_staged.cases.filter(c=>c.graph==='target').map(c=>c.stale_Z_final_current_changed_coordinates),[0,0]);
  assert.equal(row.pc_hardening.scale,'7/8');assert.equal(row.pc_hardening.native_steps,0);
  assert.ok(row.pc_hardening.cases.every(c=>c.separated_coordinates>0 && c.effect_lower_display>c.combined_error_upper_display));
  assert.match(text(out),/Separate carrier-sensitive history companion/);
  assert.match(text(out),/A_PC native prerequisites: 4 detached prepared steps/);
  for(const key of ['ready_for_8_4h','user_accepted','native_events','committed_steps']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC').pc_native[key]=['ready_for_8_4h','user_accepted'].includes(key)?false:true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const key of ['ready_for_8_4h','native_steps','numerical_recomputed']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC').pc_hardening[key]=true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const key of ['ready_for_8_4h','native_steps']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC').pc_staged[key]=true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const key of ['ready_for_8_4h','user_accepted','native_steps','poststate_read_executed']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC').feasibility[key]=true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const key of ['ready_for_8_4h','user_accepted','native_steps']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_PC')[key]=['ready_for_8_4h','user_accepted'].includes(key)?false:true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
});

test('A_CI larger joint roots retain reset exclusion without native credit', () => {
  const row=evidence.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_CI');
  assert.equal(row.cases.length,4);
  assert.deepEqual(row.cases.map(c=>c.exact_real_first_step_resources_nonnegative),[true,true,true,false]);
  assert.equal(row.native_roots,0);assert.equal(row.ready_for_8_4h,false);assert.equal(row.user_accepted,false);
  assert.deepEqual(row.feasibility.shares,['5/16','5/16','3/8']);
  assert.equal(row.feasibility.event_pair.reset_evolves,false);
  assert.equal(row.feasibility.interval_research_recomputed,false);
  assert.equal(row.feasibility.ready_for_8_4h,false);
  assert.equal(row.staged_oracle.native_roots,0);
  assert.equal(row.native_attempt.native_steps,0);
  assert.equal(row.native_attempt.native_prerequisites_complete,false);
  assert.deepEqual(row.native_attempt.cases.map(c=>c.outcome),['incomplete','not_run','not_run','not_run']);
  assert.equal(row.native_attempt.known_implementation_holds.length,2);
  assert.equal(row.native_successor.native_steps,4);assert.equal(row.native_successor.native_roots,12);
  assert.equal(row.native_successor.native_prerequisites_complete,true);
  assert.equal(row.native_successor.user_accepted,true);assert.equal(row.native_successor.ready_for_8_4h,true);
  assert.equal(row.native_successor.original_execution_flags_unchanged,true);
  assert.equal(row.native_successor.full_retained_checker_rerun,false);
  assert.equal(row.staged_oracle.ready_for_8_4h,false);
  assert.equal(row.staged_oracle.interval_research_recomputed,false);
  assert.equal(row.staged_oracle.cases.length,4);
  assert.ok(row.staged_oracle.cases.every(c=>c.two_consecutive_independent_residual_passes && !c.native_stopping_outcome_verified && c.feedback_coordinates_above_selected_error>0));
  assert.ok(row.feasibility.cases.every(c=>c.fresh_transfer_target_minimum_lower_display>0));
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/A unique joint root is not a successful continuation/);
  assert.match(text(out),/successor keeps both W histories unchanged/);
  assert.match(text(out),/independent staged joint-root oracle/);
  assert.match(text(out),/Source diagonal changes round away/);
  assert.match(text(out),/native prerequisite HOLD/);
  assert.match(text(out),/expected-failure test is not a conformance PASS/);
  assert.match(text(out),/corrected native successor/);
  assert.match(text(out),/Scoped A_CI prerequisite acceptance/);
  assert.match(text(out),/not exact conservation/);
  for(const [key,value] of [['ready_for_8_4h',false],['user_accepted',false],['native_events',1]]) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_CI').native_successor[key]=value;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  const promoted=structuredClone(evidence);
  promoted.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_CI').native_attempt.native_prerequisites_complete=true;
  assert.throws(()=>checkedTranche8(promoted),/stale or widened/);
  for(const key of ['ready_for_8_4h','user_accepted','native_roots']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_CI').staged_oracle[key]=true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
  for(const key of ['ready_for_8_4h','user_accepted','native_roots']) {
    const bad=structuredClone(evidence);
    bad.coverage.larger_prerequisites.investigations.find(r=>r.family==='A_CI')[key]=true;
    assert.throws(()=>checkedTranche8(bad),/stale or widened/);
  }
});

test('larger C_CI investigation does not promote exact-real roots to native admission', () => {
  const row=evidence.coverage.larger_prerequisites.investigations[0];
  assert.equal(row.family,'C_CI');assert.equal(row.cases.length,4);
  assert.equal(row.native_roots,0);assert.equal(row.ready_for_8_4h,false);
  assert.ok(row.cases.every(c=>c.reference_pair_already_within_exact_real_residual_tolerance));
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/C_CI — research and separately bound native prerequisites/);
  assert.match(text(out),/does not establish feedback discrimination/);
  assert.equal(row.staged_bridge.cases.length,4);
  assert.equal(row.staged_bridge.native_stopping_outcome_verified,false);
  assert.match(text(out),/includes analytic current defect/);
  assert.equal(row.staged_bridge.continuation.excluded_target_roles,2);
  assert.match(text(out),/certified negative exact-root first-step resources/);
  const bad=structuredClone(evidence);bad.coverage.larger_prerequisites.investigations[0].staged_bridge.native_stopping_outcome_verified=true;
  assert.throws(()=>checkedTranche8(bad));
  for(const key of ['native_roots','native_steps','ready_for_8_4h','user_accepted']) {
    const forged=structuredClone(evidence);forged.coverage.larger_prerequisites.investigations[0][key]=1;
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('larger equation preflight confers no native admission or readiness', () => {
  const row=evidence.coverage.larger_prerequisites.family_results[0];
  assert.equal(row.family,'C_OS'); assert.equal(row.cases,4);
  assert.equal(row.user_accepted,true);
  assert.equal(row.pointwise_bounds.user_accepted,true);
  assert.equal(row.acceptance_scope,'bounded_research_checkpoint_not_native_admission');
  for(const key of ['native_admission','ready_for_8_4h','full_error_enclosure','aggregate_closed']) {
    assert.equal(row[key],false);
    const forged=structuredClone(evidence);
    forged.coverage.larger_prerequisites.family_results[0][key]=true;
    assert.throws(()=>checkedTranche8(forged));
  }
  const container=element('div'); renderTranche8(evidence,container,element);
  assert.match(text(container),/8.4g C_OS — historical bounds and native prerequisites/);
  assert.match(text(container),/authorized 8.4h readiness: true/);
  assert.match(text(container),/Bounded research checkpoint accepted/);
  assert.equal(row.pointwise_bounds.staged_positive,4);
  assert.equal(row.pointwise_bounds.exact_real_positive,4);
  assert.match(text(container),/Explicit certified FLINT\/Arb policy integrated/);
  assert.equal(row.native_prerequisites.numerical_steps,4);
  assert.equal(row.native_prerequisites.committed_steps,0);
  assert.equal(row.native_prerequisites.native_events,0);
  assert.equal(row.native_prerequisites.user_accepted,true);
  for(const [key,value] of [['numerical_steps',5],['native_events',1],['user_accepted',false],['ready_for_8_4h',false]]) {
    const forged=structuredClone(evidence);
    forged.coverage.larger_prerequisites.family_results[0].native_prerequisites[key]=value;
    assert.throws(()=>checkedTranche8(forged));
  }
  for(const key of ['native_admission','ready_for_8_4h','production_shortcut_integrated','uniform_domain']) {
    const forged=structuredClone(evidence);
    forged.coverage.larger_prerequisites.family_results[0].pointwise_bounds[key]=true;
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_OS chart covariance separates exact plans from accepted native cells', () => {
  const view=evidence.coverage.chart_covariance,row=view.family_results[0];
  assert.equal(row.family,'C_OS');assert.equal(row.passing_pending_cells,0);
  assert.equal(row.accepted_cells,24);assert.ok(row.acceptance);
  assert.equal(row.frozen_plan_executions,4);assert.equal(row.native_events,16);
  assert.equal(row.target_steps,64);assert.equal(row.final_reads,32);
  assert.equal(row.chart_symmetries,true);assert.equal(view.aggregate_closed,false);
  assert.equal(view.families_not_executed.length,6);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/4 exact frozen mechanical-plan executions are separate/);
  assert.match(text(out),/Reflection is not edge reversal/);
  for(const mutate of [r=>r.accepted_cells=0,r=>r.native_events=20,
      r=>r.normalization_policy_id='column_only',r=>r.uniform_domain=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.chart_covariance.family_results[0]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_CI chart covariance binds full roots and separately reused frozen plans', () => {
  const row=evidence.coverage.chart_covariance.family_results.find(r=>r.family==='C_CI');
  assert.equal(row.full_joint_roots,true);assert.equal(row.chart_symmetries,true);
  assert.equal(row.accepted_cells,24);assert.equal(row.passing_pending_cells,0);
  assert.equal(row.native_events,16);assert.equal(row.target_steps,64);assert.equal(row.final_reads,32);
  assert.equal(row.frozen_plan_executions,0);assert.equal(row.reused_frozen_plan_executions,4);
  assert.equal(row.interval_certificates_rerun,false);assert.ok(row.acceptance);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Complete joint-root covariance with pointwise independent interval certificates/);
  assert.match(text(out),/4 frozen mechanical plans are reused/);
  for(const mutate of [r=>r.accepted_cells=0,r=>r.full_joint_roots=false,
      r=>r.frozen_plan_executions=4,r=>r.interval_certificates_rerun=true]) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.chart_covariance.family_results.find(r=>r.family==='C_CI'));
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_CI chart covariance keeps unsigned history and scoped acceptance explicit', () => {
  const row=evidence.coverage.chart_covariance.family_results.find(r=>r.family==='A_CI');
  assert.equal(row.full_joint_roots,true);assert.equal(row.unsigned_candidate_history,true);
  assert.equal(row.accepted_cells,24);assert.equal(row.passing_pending_cells,0);
  assert.equal(row.native_events,16);assert.equal(row.target_steps,64);assert.equal(row.final_reads,32);
  assert.equal(row.frozen_plan_executions,0);assert.equal(row.reused_frozen_plan_executions,4);
  assert.ok(row.acceptance);assert.equal(row.interval_certificates_rerun,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Unsigned W_A and effective conductance/);
  assert.match(text(out),/not new A_CI executions/);
  for(const mutate of [r=>r.accepted_cells=0,r=>r.unsigned_candidate_history=false,
      r=>r.full_joint_roots=false,r=>r.native_events=20]) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.chart_covariance.family_results.find(r=>r.family==='A_CI'));
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_PC full-chart covariance keeps carrier loss and scoped acceptance explicit', () => {
  const group=evidence.coverage.chart_covariance;
  const row=group.family_results.find(r=>r.family==='A_PC');
  assert.equal(row.accepted_cells,24);assert.equal(row.passing_pending_cells,0);
  assert.equal(row.native_events,16);assert.equal(row.target_steps,64);assert.equal(row.final_reads,32);
  assert.equal(row.full_joint_roots,false);assert.equal(row.persistent_carrier,true);
  assert.equal(row.unsigned_candidate_history,true);assert.equal(row.chart_symmetries,true);
  assert.equal(row.frozen_plan_executions,0);assert.equal(row.reused_frozen_plan_executions,4);
  assert.ok(row.acceptance);assert.equal(row.interval_certificates_rerun,false);
  assert.equal(group.family_results.reduce((n,r)=>n+r.accepted_cells,0),96);
  assert.equal(group.first_group_closed,true);assert.equal(group.first_group_accepted_cells,96);
  assert.equal(group.family_results.reduce((n,r)=>n+r.passing_pending_cells,0),0);
  assert.equal(group.families_not_executed.length,6);assert.equal(group.aggregate_closed,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/whole-carrier archive, explicit loss, zero target initialization/);
  assert.match(text(out),/Both declared layouts have active phase/);
  for(const mutate of [r=>r.accepted_cells=0,r=>r.persistent_carrier=false,
      r=>r.full_joint_roots=true,r=>r.native_events=20,r=>r.interval_certificates_rerun=true]) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.chart_covariance.family_results.find(r=>r.family==='A_PC'));
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_OS ordering covariance projects scoped acceptance without sibling credit', () => {
  const view=evidence.coverage.ordering_covariance,row=view.family_results[0];
  assert.equal(row.family,'C_OS'); assert.equal(row.passing_pending_cells,0);
  assert.equal(row.accepted_cells,20); assert.equal(row.native_events,12);
  assert.equal(row.target_steps,48); assert.equal(row.final_reads,24);
  assert.equal(view.families_not_executed.length,6);assert.equal(view.aggregate_closed,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/C_OS: 0\/20 covariance history cells passing pending acceptance, 20 accepted/);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [v=>v.aggregate_closed=true,v=>v.family_results[0].accepted_cells=0,
      v=>v.family_results[0].uniform_domain=true,v=>v.families_not_executed.pop(),
      v=>v.family_results[0].results.sha256='forged']) {
    const forged=structuredClone(evidence);mutate(forged.coverage.ordering_covariance);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_CI ordering covariance retains full-root scope and scoped acceptance', () => {
  const row=evidence.coverage.ordering_covariance.family_results.find(r=>r.family==='C_CI');
  assert.equal(row.passing_pending_cells,0);assert.equal(row.accepted_cells,20);
  assert.ok(row.acceptance);assert.equal(row.full_joint_roots,true);
  assert.equal(row.interval_certificates_rerun,false);assert.equal(row.native_trajectories_rerun,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Full joint CI roots/);
  for(const field of ['full_joint_roots','interval_certificates_rerun','native_trajectories_rerun']) {
    const forged=structuredClone(evidence);
    const changed=forged.coverage.ordering_covariance.family_results.find(r=>r.family==='C_CI');
    changed[field]=!changed[field];assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_CI covariance keeps unsigned history and scoped acceptance visible', () => {
  const row=evidence.coverage.ordering_covariance.family_results.find(r=>r.family==='A_CI');
  assert.equal(row.passing_pending_cells,0);assert.equal(row.accepted_cells,20);
  assert.equal(row.unsigned_candidate_history,true);assert.equal(row.full_joint_roots,true);
  assert.notEqual(row.acceptance,null);assert.equal(row.interval_certificates_rerun,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Unsigned Candidate-A history/);
  for(const key of ['unsigned_candidate_history','full_joint_roots','interval_certificates_rerun']) {
    const forged=structuredClone(evidence);
    const changed=forged.coverage.ordering_covariance.family_results.find(r=>r.family==='A_CI');
    changed[key]=!changed[key];assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_PC covariance keeps persistent carrier loss and scoped acceptance visible', () => {
  const row=evidence.coverage.ordering_covariance.family_results.find(r=>r.family==='A_PC');
  assert.equal(row.passing_pending_cells,0);assert.equal(row.accepted_cells,20);
  assert.equal(row.persistent_carrier,true);assert.equal(row.full_joint_roots,false);
  assert.equal(row.unsigned_candidate_history,true);assert.ok(row.acceptance);
  assert.deepEqual(row.degrees,[59,94]);
  const group=evidence.coverage.ordering_covariance;
  assert.deepEqual(group.family_results.map(r=>r.family),['C_OS','C_CI','A_CI','A_PC']);
  assert.equal(group.family_results.reduce((n,r)=>n+r.accepted_cells,0),80);
  assert.equal(group.family_results.reduce((n,r)=>n+r.passing_pending_cells,0),0);
  assert.equal(group.families_not_executed.length,6);assert.equal(group.aggregate_closed,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Persistent carrier: two-sided signed Z transport/);
  for(const key of ['persistent_carrier','full_joint_roots','interval_certificates_rerun']) {
    const forged=structuredClone(evidence);
    const changed=forged.coverage.ordering_covariance.family_results.find(r=>r.family==='A_PC');
    changed[key]=!changed[key];assert.throws(()=>checkedTranche8(forged));
  }
});

test('deep A_CI oracle is visible without native or acceptance promotion', () => {
  const deep=evidence.coverage.deep_expansion;
  const row=deep.oracle_preparations.find(r=>r.family==='A_CI');
  assert.equal(row.passed_cases,20);
  assert.equal(row.independent_observations,440);
  assert.equal(row.runtime_cells_closed,0);
  assert.equal(row.native_steps,0);
  assert.equal(row.oracle_scope_accepted,true);
  assert.ok(!deep.families_not_executed.includes('A_CI'));
  const native=deep.family_results.find(r=>r.family==='A_CI');
  assert.equal(native.passing_pending_cells,0);
  assert.equal(native.accepted_cells,40);
  assert.equal(native.target_steps,400);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/A_CI independent deep oracle: 20\/20 cases, 440 joint-root observations; oracle scope accepted/);
  assert.match(text(out),/A_CI: 20 single-event cases; 40\/40 accepted history cells, 0 passing pending acceptance/);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.runtime_cells_closed=40,r=>r.oracle_scope_accepted=false,r=>r.review.sha256='forged']) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.deep_expansion.oracle_preparations[0]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('deep C_OS evidence is partial and not acceptance or an event sequence', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/8.4d deeper expansion/);
  assert.match(text(out),/24 pointwise sign enclosures; 18\/18 positive finite-probe histories/);
  assert.match(text(out),/Bounded C_CI hardening: 9 finite target probes, 18 histories, 36 native steps/);
  assert.match(text(out),/3 are rounded-transfer controls, not exact-conserving event evidence/);
  assert.match(text(out),/40\/40 accepted history cells, 0 passing pending acceptance/);
  const deep=evidence.coverage.deep_expansion;
  assert.equal(deep.family_results.length,4);
  assert.equal(deep.family_results[0].maximum_core_depth,4);
  assert.equal(deep.families_not_executed.length,6);
  const hardened=structuredClone(evidence);
  hardened.coverage.deep_expansion.family_results[0].hardening.uniform_tube=true;
  assert.throws(()=>checkedTranche8(hardened));
  assert.ok(sourceURL(deep.family_results[0].results).startsWith('/api/tranche8/source?'));
  for (const mutate of [d=>d.aggregate_closed=true,d=>d.family_results[0].accepted_cells=0,d=>d.family_results[0].successive_events=true,d=>d.families_not_executed.pop()]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.deep_expansion);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('deep A_PC distinguishes accepted exclusion from trigger-rejected companion', () => {
  const deep=evidence.coverage.deep_expansion;
  const row=deep.family_results.find(r=>r.family==='A_PC');
  assert.equal(row.native_cases,20);assert.equal(row.target_steps,400);
  assert.equal(row.committed_events,20);
  assert.equal(row.source_companion.native.source_steps,1);
  assert.equal(row.history_companion.source_eligible,true);
  assert.equal(row.history_companion.native_cases,0);
  assert.equal(row.history_companion.pressure.neighbor_probes,0);
  assert.equal(row.accepted_cells,40);assert.equal(row.passing_pending_cells,0);
  assert.equal(deep.first_group_closed,true);
  assert.equal(deep.first_group_accepted_cells,160);
  assert.equal(deep.aggregate_closed,false);
  assert.equal(row.full_campaign.newly_executed_cases,19);
  assert.equal(row.full_campaign.reused_cases,1);
  assert.equal(row.full_campaign.reused_target_steps,20);
  assert.equal(row.full_campaign.final_reads,40);
  assert.equal(row.full_campaign.uniform_native_domain,false);
  assert.equal(row.joint_witness.passed_cases,0);
  assert.equal(row.joint_witness.target_steps,1);
  assert.equal(row.joint_successor.passed_cases,1);
  assert.equal(row.joint_successor.uniform_native_domain,false);
  assert.equal(row.attempted_cases,20);assert.equal(row.unattempted_cases,0);
  assert.equal(row.preflight_pressure.certified_exclusions,2);
  assert.equal(row.allocation_feasibility.D94_cases,6);
  assert.equal(row.allocation_feasibility.runtime_cells_closed,0);
  assert.ok(!deep.families_not_executed.includes('A_PC'));
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/A_PC frozen-source PREFLIGHT HOLD: 1 case attempted, 19 not attempted; 0 native events and 0 native continuation steps/);
  assert.match(text(out),/1 native source step; 1 event attempt, 0 commits, 0 native target steps/);
  assert.match(text(out),/A_PC allocation exclusion: 6 declared D94 layouts, entire closed simplex/);
  assert.match(text(out),/A_PC history companion: fresh source eligible; current-role target preflight fails at step 1/);
  assert.match(text(out),/A_PC coupled successor: 1 D94 case, 20 native target steps, 2 final reads/);
  assert.match(text(out),/A_PC full coupled campaign: 20\/20 cases, 400 native continuation steps, 40 final reads/);
  assert.ok(sourceURL(row.preflight_pressure.evidence).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.committed_events=2,r=>r.accepted_cells=0,r=>r.unattempted_cases=1,r=>r.full_campaign.uniform_native_domain=true,r=>r.full_campaign.reused_cases=0,r=>r.joint_successor.uniform_native_domain=true,r=>r.joint_witness.passed_cases=1,r=>r.source_companion.native.uniform_neighborhood_proved=true,r=>r.preflight_pressure.general_infeasibility_proved=true]) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.deep_expansion.family_results.find(r=>r.family==='A_PC'));
    assert.throws(()=>checkedTranche8(forged));
  }
  for(const mutate of [f=>f.claim_scope='all_sources',f=>f.runtime_cells_closed=40,f=>f.D94_cases=10,f=>f.evidence.sha256='forged']) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.deep_expansion.family_results.find(r=>r.family==='A_PC').allocation_feasibility);
    assert.throws(()=>checkedTranche8(forged));
  }
  for(const mutate of [h=>h.source_eligible=false,h=>h.native_cases=1,h=>h.pressure.neighbor_probes=2,h=>h.accepted_cells=40]) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.deep_expansion.family_results.find(r=>r.family==='A_PC').history_companion);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_PC boundary execution binds scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c C_PC — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='C_PC');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=640,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('deep C_CI binds complete joint-root evidence without acceptance widening', () => {
  const deep=evidence.coverage.deep_expansion;
  const row=deep.family_results.find(r=>r.family==='C_CI');
  assert.equal(row.passed_cases,20);
  assert.equal(row.target_steps,400);
  assert.equal(row.accepted_cells,40);
  assert.equal(row.passing_pending_cells,0);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');
  assert.match(row.comparison_scope,/CI_only_tree23_pointwise_full_joint_root/);
  assert.ok(sourceURL(row.review).startsWith('/api/tranche8/source?'));
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/C_CI: 20 single-event cases; 40\/40 accepted history cells/);
  for(const mutate of [r=>r.accepted_cells=0,r=>r.final_reads=0,r=>r.interval_equations_recomputed=true,r=>r.review.sha256='forged']) {
    const forged=structuredClone(evidence);
    mutate(forged.coverage.deep_expansion.family_results.find(r=>r.family==='C_CI'));
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_PC boundary execution binds scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c A_PC — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='A_PC');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=640,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_CI_PC boundary execution binds scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c C_CI_PC — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='C_CI_PC');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=640,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_CI_PC boundary execution binds separate scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c A_CI_PC — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='A_CI_PC');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.equal(row.passing_pending_cells,0);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=64,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_RG2b boundary execution records separate scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c C_RG2b — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='C_RG2b');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.match(row.comparison_scope,/six_level_inverse_chain/);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=64,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_RG2b boundary execution records separate scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c A_RG2b — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const i=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='A_RG2b');
  const row=evidence.coverage.boundary_contract.family_results[i];
  assert.equal(row.passed_cases,30);assert.equal(row.exact_reuse_cases,2);
  assert.equal(row.acceptance.anchor,'scoped-user-acceptance');assert.equal(row.accepted_cells,64);
  assert.match(row.comparison_scope,/four_level_CY_chain/);
  assert.ok(sourceURL(row.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=0,r=>r.acceptance=null,r=>r.passing_pending_cells=64,r=>r.native_trajectories_rerun=true]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[i]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_OS oracle scope is not native boundary acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /32\/32 independent oracle expectations pass/);
  assert.match(text(out), /0 native steps and 0 runtime cells closed/);
  const r=evidence.coverage.boundary_contract.oracle_preparations[0];
  assert.equal(r.oracle_scope_accepted, true);
  assert.equal(r.user_accepted, false);
  assert.equal(r.status, 'accepted_oracle_scope');
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.native_runtime_executed=true,r=>r.runtime_cells_closed=64,r=>r.user_accepted=true]) {
    const forged=structuredClone(evidence); mutate(forged.coverage.boundary_contract.oracle_preparations[0]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_CI joint-root oracle scope cannot become native evidence or acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c A_CI oracle — accepted_oracle_scope/);
  assert.match(text(out), /30 new independent oracle cases; 2 exact accepted native target reuses, not new oracle executions/);
  const index=evidence.coverage.boundary_contract.oracle_preparations.findIndex(r=>r.family==='A_CI');
  const r=evidence.coverage.boundary_contract.oracle_preparations[index];
  assert.equal(r.native_steps,0);assert.equal(r.native_roots,0);
  assert.equal(r.oracle_scope_accepted,true);assert.equal(r.acceptance.anchor,'scoped-user-acceptance');
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.native_steps=600,r=>r.acceptance=null,r=>r.runtime_cells_closed=64,r=>r.exact_accepted_target_reuses=0]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.oracle_preparations[index]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_CI native boundary results bind separate scoped acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c A_CI — accepted_bounded/);
  const index=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='A_CI');
  const r=evidence.coverage.boundary_contract.family_results[index];
  assert.equal(r.successful_history_cells,64);assert.equal(r.accepted_cells,64);
  assert.equal(r.passing_pending_cells,0);assert.equal(r.acceptance.anchor,'scoped-user-acceptance');
  for(const mutate of [r=>r.acceptance=null,r=>r.native_trajectories_rerun=true,r=>r.passed_cases=32]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[index]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('A_OS native results bind separate scoped acceptance', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const index=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='A_OS');
  const r=evidence.coverage.boundary_contract.family_results[index];
  assert.equal(r.status, 'accepted_bounded');
  assert.equal(r.acceptance.anchor, 'scoped-user-acceptance');
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=640,r=>r.native_trajectories_rerun=true,r=>r.interval_equations_recomputed=true]) {
    const forged=structuredClone(evidence); mutate(forged.coverage.boundary_contract.family_results[index]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_CI native boundary evidence is distinct from preparation and acceptance', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /8.4c C_CI — accepted_bounded/);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const index=evidence.coverage.boundary_contract.family_results.findIndex(r=>r.family==='C_CI');
  const r=evidence.coverage.boundary_contract.family_results[index];
  assert.equal(r.passed_cases,30);assert.equal(r.exact_reuse_cases,2);
  assert.equal(r.acceptance.anchor,'scoped-user-acceptance');
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.accepted_cells=640,r=>r.native_trajectories_rerun=true,r=>r.passing_pending_cells=640,r=>r.acceptance=null]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.family_results[index]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_CI preparation displays native root reads without event or runtime credit', () => {
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /60 new read-only native joint-root proposals/);
  assert.match(text(out), /0 topology events, 0 native steps and 0 runtime cells closed/);
  const r=evidence.coverage.boundary_contract.target_preparations[0];
  assert.equal(r.family,'C_CI');assert.equal(r.passed_cases,30);
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for(const mutate of [r=>r.native_steps=600,r=>r.runtime_cells_closed=64,r=>r.topology_events=30,r=>r.new_native_root_reads=0]) {
    const forged=structuredClone(evidence);mutate(forged.coverage.boundary_contract.target_preparations[0]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('C_OS boundary execution cannot confer acceptance or native rerun', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  assert.match(text(out), /64\/64 accepted history cells; 0 passing cells pending acceptance/);
  const r=evidence.coverage.boundary_contract.family_results[0];
  assert.equal(r.family, 'C_OS');
  assert.ok(sourceURL(r.results).startsWith('/api/tranche8/source?'));
  for (const mutate of [r=>r.accepted_cells=640, r=>r.native_trajectories_rerun=true, r=>r.exact_reuse_cases=32]) {
    const forged=structuredClone(evidence); mutate(forged.coverage.boundary_contract.family_results[0]);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('shared mechanics cannot become numerical coverage or lose mock labels', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  assert.match(text(out), /mocked numerical reads, detection and target construction/);
  assert.match(text(out), /No numerical admission or continuation credit/);
  const mechanical=evidence.coverage.boundary_contract.mechanics;
  assert.equal(mechanical.status, 'accepted_shared_mechanics');
  assert.equal(mechanical.test_methods, 6);
  assert.ok(sourceURL(mechanical.record).startsWith('/api/tranche8/source?'));
  for (const mutate of [m=>m.numerical_history_credit=640, m=>m.status='accepted',
      m=>m.observations.receiver_probes[0].numerical_reads_mocked=false]) {
    const forged=structuredClone(evidence); mutate(forged.coverage.boundary_contract.mechanics);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('boundary contract renders separately and rejects false runtime credit', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  for (const phrase of ['640 current/reset obligations', '600 new, 40 exact-reuse candidates', '0 executed; 0 accepted', 'not new target certificates'])
    assert.ok(text(out).includes(phrase), phrase);
  assert.ok(sourceURL(evidence.coverage.boundary_contract.record).startsWith('/api/tranche8/source?'));
  for (const mutate of [b=>b.counts.accepted_cells=640, b=>b.native_runtime_executed=true, b=>b.families.pop()]) {
    const forged=structuredClone(evidence); mutate(forged.coverage.boundary_contract);
    assert.throws(()=>checkedTranche8(forged));
  }
});

test('all ten accepted 8.3 profiles and partial 8.4 coverage actually render', () => {
  const out=element('div'); renderTranche8(evidence,out,element);
  const content=text(out);
  for(const row of evidence.profiles) assert.ok(content.includes(row.family));
  for(const s of ['322/322','0 pending','INCOMPLETE CASE','event committed=true','No native trajectory rerun','not runtime acceptance']) assert.ok(content.includes(s),s);
  assert.ok(out.children.length > 20);
});

test('mutated counts, scope, input identities and failures cannot be promoted', () => {
  for(const mutate of [v=>v.coverage.accepted_cells=323, v=>v.coverage.aggregate_closed=true,
    v=>v.profiles.pop(),v=>v.configuration.families[0].runtime_accepted=true,
    v=>v.coverage.runs[0].cases.find(r=>!r.case_passed).case_passed=true,
    v=>v.verification.native_trajectories_rerun=true,v=>v.source_refs[0].sha256='0'.repeat(64),
    v=>v.dependency_ready_snapshot.push('P9-8.5')]) {
    const value=structuredClone(evidence);mutate(value);assert.throws(()=>checkedTranche8(value));
  }
});

test('C_CI scoped acceptance preserves original incomplete evidence', () => {
  const run = evidence.coverage.runs.find(r => r.family === 'C_CI');
  assert.equal(run.acceptance.anchor, 'scoped-user-acceptance');
  assert.equal(evidence.coverage.families.find(r => r.family === 'C_CI').accepted_cells, 32);
  const out=element('div'); renderTranche8(evidence,out,element);
  assert.match(text(out), /Original execution and timeout/);
  const forged = structuredClone(evidence);
  forged.coverage.runs.find(r => r.family === 'C_CI').acceptance=null;
  assert.throws(() => checkedTranche8(forged));
});

test('only exact indexed source links are exposed', () => {
  const ref=evidence.source_refs[0];assert.ok(sourceURL(ref).startsWith('/api/tranche8/source?path='));
  assert.throws(()=>sourceURL({...ref,path:'../../secret'}));
  assert.throws(()=>sourceURL({...ref,sha256:'0'.repeat(64)}));
});

test('A_CI acceptance is separately bound without widening scope', () => {
  const run = evidence.coverage.runs.find(r => r.family === 'A_CI');
  assert.equal(run.acceptance.anchor, 'scoped-user-acceptance');
  assert.equal(run.status, 'accepted_bounded');
  assert.equal(run.passed_cases, 16);
  assert.equal(evidence.coverage.families.find(r => r.family === 'A_CI').accepted_cells, 32);
  assert.equal(evidence.coverage.executed_pending_cells, 0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out), /322\/322/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r => r.family === 'A_CI').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});

test('failed refresh clears previous success and ignores delayed old response', async () => {
  const out=element('div'), status=element('p');let fail=false;
  const load=tranche8Loader(out,status,async()=>({ok:!fail,json:async()=>evidence}),element);
  await load();assert.ok(out.children.length);fail=true;await load();assert.equal(out.children.length,0);
  assert.match(status.textContent,/Unavailable/);
  let resolve;let n=0;
  const reload=tranche8Loader(out,status,async()=>++n===1 ? new Promise(r=>resolve=r) : {ok:false},element);
  const first=reload();await reload();resolve({ok:true,json:async()=>evidence});await first;
  assert.equal(out.children.length,0);assert.match(status.textContent,/Unavailable/);
});

test('C_PC binds scoped acceptance for all 17 subjects', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='C_PC');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.passed_cases,17);
  assert.equal(run.status,'accepted_bounded');
  const row=evidence.coverage.families.find(r=>r.family==='C_PC');
  assert.equal(row.accepted_cells,34);assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Separate scoped acceptance/);
  assert.match(text(out),/G9-EXPAND-C-PC-CARRIER-RESET/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='C_PC').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});


test('A_PC binds scoped acceptance with both histories and W/Z evidence', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='A_PC');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.status,'accepted_bounded');
  assert.equal(run.passed_cases,16);
  const row=evidence.coverage.families.find(r=>r.family==='A_PC');
  assert.equal(row.accepted_cells,32);assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Separate scoped acceptance/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='A_PC').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});


test('C_CI_PC keeps composite execution separate from acceptance', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='C_CI_PC');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.status,'accepted_bounded');
  assert.equal(run.passed_cases,16);
  assert.equal(run.stage_evidence.signed_read_certificates,1059);
  assert.equal(run.stage_evidence.same_root_writer_effects,32);
  assert.equal(run.stage_evidence.final_root_effects,160);
  const row=evidence.coverage.families.find(r=>r.family==='C_CI_PC');
  assert.equal(row.accepted_cells,32);assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Separate scoped acceptance/);
  assert.match(text(out),/Signed reads, composite roots and carrier effects/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='C_CI_PC').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});


test('A_CI_PC binds separate acceptance with both writer channels', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='A_CI_PC');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.status,'accepted_bounded');
  assert.equal(run.passed_cases,16);
  assert.equal(run.stage_evidence.signed_read_certificates,1059);
  assert.equal(run.stage_evidence.entry_W_Z_effects,288);
  assert.equal(run.stage_evidence.final_root_effects,96);
  assert.equal(run.stage_evidence.source_old_Z_effects,4);
  const row=evidence.coverage.families.find(r=>r.family==='A_CI_PC');
  assert.equal(row.accepted_cells,32);assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Separate scoped acceptance/);
  assert.match(text(out),/Signed joint roots and separate W\/Z consumers/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='A_CI_PC').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});


test('C_RG2b exposes complete chains and claim limits with separate scoped acceptance', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='C_RG2b');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.status,'accepted_bounded');
  assert.equal(run.passed_cases,16);
  assert.equal(run.stage_evidence.signed_read_certificates,1061);
  assert.equal(run.stage_evidence.inverse_level_residuals,6366);
  assert.equal(run.stage_evidence.source_controls,12);
  assert.equal(run.stage_evidence.entry_controls,192);
  assert.equal(run.stage_evidence.final_controls,192);
  assert.equal(run.execution_recovery,undefined);
  assert.equal(run.operational_retry,undefined);
  const row=evidence.coverage.families.find(r=>r.family==='C_RG2b');
  assert.equal(row.accepted_cells,32);assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Separate scoped acceptance/);
  assert.match(text(out),/Signed inverse chains, complete section errors and lagged invariance/);
  assert.match(text(out),/RG completion and C1 claim restrictions/);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='C_RG2b').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});


test('A_RG2b binds separate acceptance without closing later 8.4 work', () => {
  const run=evidence.coverage.runs.find(r=>r.family==='A_RG2b');
  assert.equal(run.acceptance.anchor,'scoped-user-acceptance');
  assert.equal(run.status,'accepted_bounded');
  assert.equal(run.passed_cases,16);
  assert.equal(run.stage_evidence.signed_read_certificates,1061);
  assert.equal(run.stage_evidence.inverse_level_residuals,4244);
  assert.equal(run.stage_evidence.writer_controls,192);
  const row=evidence.coverage.families.find(r=>r.family==='A_RG2b');
  assert.equal(row.accepted_cells,32); assert.equal(row.executed_pending_cells,0);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/Signed C\/Y chains, W lineage and composed writer controls/);
  assert.match(text(out),/Separate scoped acceptance/);
  assert.match(text(out),/P9-8.4 remains open/);
  assert.equal(evidence.coverage.children.find(r=>r.work_id==='P9-8.4b').accepted,true);
  assert.equal(evidence.coverage.aggregate_closed,false);
  const forged=structuredClone(evidence);
  forged.coverage.runs.find(r=>r.family==='A_RG2b').acceptance=null;
  assert.throws(()=>checkedTranche8(forged));
});

test('C_CI feasibility preserves exclusions and reset chronology without native credit', () => {
  const r=evidence.coverage.larger_prerequisites.investigations.find(x=>x.family==='C_CI');
  assert.equal(r.staged_bridge.continuation.excluded_target_roles,2);
  assert.deepEqual(r.feasibility.shares,['5/16','5/16','3/8']);
  assert.equal(r.feasibility.source_deficit,'1/1024');
  assert.equal(r.feasibility.event_pair.reset_evolves,false);
  assert.equal(r.feasibility.ready_for_8_4h,false);
  assert.equal(r.feasibility.interval_solves_rerun,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/stored reset does not evolve/);
  for(const mutate of [x=>x.ready_for_8_4h=true,x=>x.event_pair.reset_evolves=true,
      x=>x.shares=['1/2','1/4','1/4']]) {
    const v=structuredClone(evidence);
    mutate(v.coverage.larger_prerequisites.investigations.find(x=>x.family==='C_CI').feasibility);
    assert.throws(()=>checkedTranche8(v));
  }
});

test('C_CI native successor binds scoped acceptance without event credit', () => {
  const n=evidence.coverage.larger_prerequisites.investigations[0].native_prerequisites;
  assert.equal(n.native_steps,4);assert.equal(n.native_roots,12);
  assert.equal(n.native_events,0);assert.equal(n.user_accepted,true);
  assert.equal(n.ready_for_8_4h,true);assert.ok(n.acceptance);
  assert.equal(n.numerical_trajectories_rerun,false);
  assert.ok(n.cases.every(c=>c.minimum_resource>0 && c.root_evaluations.every(v=>v===1)));
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/12 full joint roots/);
  for(const key of ['native_events','user_accepted','ready_for_8_4h']) {
    const bad=structuredClone(evidence);bad.coverage.larger_prerequisites.investigations[0].native_prerequisites[key]=key==='native_events'?1:false;
    assert.throws(()=>checkedTranche8(bad));
  }
});

test('8.4c aggregate closes exact accepted scope while later work stays open', () => {
  const closure=evidence.coverage.boundary_contract.closeout;
  assert.equal(closure.accepted_cells,640);
  assert.equal(closure.pending_cells,0);
  assert.equal(closure.aggregate_closed,true);
  assert.equal(evidence.coverage.children.find(r=>r.work_id==='P9-8.4c').accepted,true);
  assert.equal(evidence.coverage.aggregate_closed,false);
  const out=element('div');renderTranche8(evidence,out,element);
  assert.match(text(out),/8.4c closed/);
  assert.match(text(out),/640\/640 accepted history cells across all ten families/);
  assert.match(text(out),/8.4d–i and 8.5\/8.6 remain open/);
  for (const mutate of [v=>v.coverage.boundary_contract.closeout.accepted_cells--,
      v=>v.coverage.boundary_contract.closeout.families.pop(),
      v=>v.coverage.aggregate_closed=true]) {
    const v=structuredClone(evidence);mutate(v);assert.throws(()=>checkedTranche8(v));
  }
});
