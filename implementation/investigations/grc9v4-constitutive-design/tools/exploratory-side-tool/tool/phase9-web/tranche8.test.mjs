import {test} from 'node:test';
import assert from 'node:assert/strict';
import {TRANCHE8_EVIDENCE as evidence} from './tranche8-evidence.js';
import {checkedTranche8, renderTranche8, sourceURL, tranche8Loader} from './tranche8.js';

const element = tag => ({tag, textContent:'', children:[], append(...nodes){this.children.push(...nodes);}, replaceChildren(...nodes){this.children=nodes;}});
const text = node => node.textContent + node.children.map(text).join(' ');

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
