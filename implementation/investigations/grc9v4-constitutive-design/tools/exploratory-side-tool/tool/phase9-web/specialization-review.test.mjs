import {test} from 'node:test';
import assert from 'node:assert/strict';
import {SPECIALIZATION_REVIEW} from './specialization-review.js';
import {checkedSpecialization} from './verification.js';

test('exact accepted consumed set closes tranche 7, not runtime conformance', () => {
  const value = {specialization_admission_review: structuredClone(SPECIALIZATION_REVIEW)};
  checkedSpecialization(value, true);
  assert.equal(value.specialization_admission_review.profile_count, 10);
  assert.equal(value.specialization_admission_review.disabled_cells, 40);
  assert.equal(value.specialization_admission_review.G3_accepted, true);
  assert.equal(value.specialization_admission_review.tranche_7_closed, true);
  const work=value.specialization_admission_review.a_expansion_work;
  assert.equal(work.oracle_owner,'P9-8.3A.1');
  assert.equal(work.runtime_owner,'P9-8.3A.2');
  assert.equal(work.oracle_requires_production_runtime,false);
  assert.ok(work.runtime_entry.includes('accepted_P9-8.3A.1_same_exact_scope'));
  checkedSpecialization({}, false);
});
test('missing, mutated, widened and held-boundary review rejected', () => {
  assert.throws(()=>checkedSpecialization({},true), /specialization admission/);
  assert.throws(()=>checkedSpecialization({specialization_admission_review:SPECIALIZATION_REVIEW},false), /specialization admission/);
  for (const edit of [v=>v.G3_accepted=false, v=>v.tranche_7_closed=false,
      v=>v.proposed_consumed_support.pop(), v=>v.pending_A_expansion_oracle=false,
      v=>v.specialization_runtime_conformance=true, v=>v.disabled_cells=39,
      v=>v.new_runtime_iterations_authorized.push('P9-8.1a'), v=>v.record_digest='0'.repeat(64),
      v=>v.a_expansion_work.oracle_owner=null, v=>v.a_expansion_work.runtime_entry.shift(),
      v=>v.a_expansion_work.generic_authority_gap_route='specialization_workaround']) {
    const v=structuredClone(SPECIALIZATION_REVIEW); edit(v);
    assert.throws(()=>checkedSpecialization({specialization_admission_review:v},true), /specialization admission/);
  }
});
