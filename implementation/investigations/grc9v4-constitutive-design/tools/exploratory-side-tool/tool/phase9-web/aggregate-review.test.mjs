import {test} from 'node:test';
import assert from 'node:assert/strict';
import {AGGREGATE_REVIEW} from './aggregate-review.js';
import {checkedAggregate} from './verification.js';

test('aggregate successor projects reconciled cells, not acceptance or G3', () => {
  checkedAggregate({profile_aggregate_reconciliation: structuredClone(AGGREGATE_REVIEW)}, true);
  assert.equal(AGGREGATE_REVIEW.reconciled_cells, 305);
  assert.equal(AGGREGATE_REVIEW.accepted_generic_runtime_support.length, 10);
  assert.equal(AGGREGATE_REVIEW.aggregate_closed, false);
  checkedAggregate({}, false);
});

test('aggregate rejects omitted, widened, stale and failed-boundary projections', () => {
  assert.throws(() => checkedAggregate({}, true));
  assert.throws(() => checkedAggregate({profile_aggregate_reconciliation: AGGREGATE_REVIEW}, false));
  for (const [key, value] of Object.entries({aggregate_closed:true, user_accepted:true,
    G3_accepted:true, all_ordered_pairs_verified:true, reconciled_cells:304,
    unresolved_cells:1, numerical_tests_rerun:305, new_execution_credit:305,
    new_G2_support:['A_CI'], new_runtime_iterations_authorized:['P9-8.1a'],
    record_digest:'0'.repeat(64), accepted_generic_runtime_support:[]})) {
    const bad = {...structuredClone(AGGREGATE_REVIEW), [key]:value};
    assert.throws(() => checkedAggregate({profile_aggregate_reconciliation:bad}, true), key);
  }
});
