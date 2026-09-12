"""P9-7.6: actual parent chains, coherent negatives and independent forks."""

from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_state import GRCV4State
from pygrc.models.grc_v4_geometry import GraphCoordinateAction
from pygrc.models.grc_v4_codec import canonical_json_bytes, V4IdentityError
from pygrc.models import grc_v4_lifecycle as lifecycle
from tests.models.test_grc_v4_migration import fixture, migration, rehash_receipt_chain, audit_identity
from tests.models.test_grc_v4_events import event, representation, reversed_target
from tests.models.test_grc_v4_lifecycle import request
from tests.models.test_grc_v4_generic_lifecycle import endpoint, restore

EVIDENCE = {}


def groups(snapshot):
    result, offset = [], 0
    for record in snapshot['commit_records']:
        ids = record['payload']['emitted_receipt_ids']
        group = snapshot['receipt_ledger'][offset:offset+len(ids)]
        assert ids and [r['receipt_id'] for r in group] == ids
        result.append(group)
        offset += len(ids)
    assert offset == len(snapshot['receipt_ledger'])
    return result


def independent_chain(snapshot):
    """Literal ordered-rank rule, not the production parent validator."""
    previous, seen, rows = None, set(), []
    for rank, group in enumerate(groups(snapshot)):
        for row in group:
            assert row['receipt_id'] not in seen
            seen.add(row['receipt_id'])
            assert row['identity_payload']['core']['parent_receipt_ids'] == ([] if previous is None else [previous])
        rows.append(dict(rank=rank, primary=group[0]['receipt_id'],
                         kind=group[0]['identity_payload']['schema_version'],
                         parent=previous, group_size=len(group)))
        previous = group[0]['receipt_id']
    return rows


class LineageOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inputs, backend = fixture('A_PC')
        a_target = fixture('A_CI_PC')[0].geometry.reference
        c_inputs, _ = fixture('C_PC')
        c_target = c_inputs.geometry.reference
        coordinate_target, _, action = reversed_target(c_inputs, None)
        owner = GRCV4(inputs, differential_reference=backend, targets=(a_target, c_target, coordinate_target))
        declarations = []

        def execute(call, declared):
            before = owner.snapshot()
            result = call(declared)
            assert result.committed, result.failure
            assert owner.snapshot()['receipt_ledger'] == before['receipt_ledger'] + [r.to_payload() for r in result.emitted_receipts]
            declarations.append(declared.to_payload())

        execute(owner.step_v4_input, request(2**-12, 'initial-step'))
        owner.reset()
        owner.rebase_reset_baseline()
        cls.parent_snapshot = owner.snapshot()
        execute(owner.migrate_profile, migration(owner, a_target))
        execute(owner.reconstruct_topology_event, event(owner, c_target))
        execute(owner.transport_representation, representation(owner, coordinate_target, action))
        execute(owner.step_v4_input, request(0, 'after-representation'))
        cls.snapshot = owner.snapshot()
        cls.witness = dict(source=inputs.to_payload(), backend=backend.to_payload(),
            targets=[r.to_payload() for r in (a_target, c_target, coordinate_target)],
            requests=declarations, snapshot=cls.snapshot)

    def test_native_chain_nonwriters_and_unreceipted_assignment(self):
        owner = restore(deepcopy(self.snapshot))
        rows = independent_chain(owner.snapshot())
        self.assertEqual([r['group_size'] for r in rows], [4, 4, 4, 4, 4, 1, 4])
        self.assertEqual([r['kind'] for r in rows], ['grcv4-step-commit-receipt-v1',
            'grcv4-reset-receipt-v1', 'grcv4-rebase-receipt-v1', 'grcv4-profile-migration-receipt-v1',
            'grcv4-topology-event-receipt-v2', 'grcv4-representation-transport-receipt-v1',
            'grcv4-step-commit-receipt-v1'])
        before = owner.snapshot()
        owner.get_state()
        owner.compute_observables()
        self.assertFalse(owner.step_v4_input(request(-1, 'failed')).committed)
        with self.assertRaises(TypeError):
            owner.reconstruct_topology_event({})
        self.assertEqual(owner.snapshot(), before)
        inputs = lifecycle._state_inputs(owner._operation.reference, owner.state.lifecycle)
        assigned = replace(inputs, current=replace(inputs.current, C=inputs.current.C[::-1]))
        state = lifecycle._lifecycle_state(assigned, lifecycle._ledger(before['receipt_ledger']))
        owner.set_state(GRCV4State(state))
        after_assignment = owner.snapshot()
        self.assertNotEqual(after_assignment['scientific_state_digest'], before['scientific_state_digest'])
        self.assertEqual(after_assignment['receipt_ledger'], before['receipt_ledger'])
        self.assertEqual(after_assignment['commit_records'], before['commit_records'])
        result = owner.step_v4_input(request(0, 'after-assignment'))
        self.assertTrue(result.committed, result.failure)
        head = rows[-1]['primary']
        for receipt in result.emitted_receipts:
            self.assertEqual(list(receipt.identity_payload['core']['parent_receipt_ids']), [head])
        independent_chain(owner.snapshot())
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
        EVIDENCE['native_chain'] = dict(self.witness, groups=rows,
            assigned=endpoint(after_assignment), following=endpoint(owner.snapshot()))

    def test_coherent_wrong_parents_reject_restore_and_crossing_publication(self):
        # Parent mutations need a nonempty generic history, not repeated
        # numerical replay of every crossing in the separate mixed witness.
        owner = restore(deepcopy(self.parent_snapshot))
        base_groups = groups(self.parent_snapshot)
        first, previous = base_groups[0][0]['receipt_id'], base_groups[-2][0]['receipt_id']
        rows = []
        for kind in ('missing', 'skipped', 'foreign', 'nonprimary', 'extra', 'reordered_extra',
                     'duplicate_parent', 'intra_commit', 'auxiliary_disagrees', 'forward_acyclic'):
            bad = deepcopy(self.parent_snapshot)
            group = groups(bad)[-1]
            choices = {'missing': [], 'skipped': [first], 'foreign': ['grc-receipt-sha256:'+'0'*64],
                       'nonprimary': [base_groups[0][1]['receipt_id']], 'extra': [previous, first],
                       'reordered_extra': [first, previous], 'duplicate_parent': [previous, previous]}
            if kind == 'intra_commit':
                group[-1]['identity_payload']['core']['parent_receipt_ids'] = [group[0]['receipt_id']]
            elif kind == 'auxiliary_disagrees':
                group[-1]['identity_payload']['core']['parent_receipt_ids'] = [first]
            elif kind == 'forward_acyclic':
                # Break the later group's dependency on the middle group,
                # then point the middle group at the actual later content ID.
                # This admits coherent hashes without a cycle/fixed point.
                for row in group:
                    row['identity_payload']['core']['parent_receipt_ids'] = [first]
                rehash_receipt_chain(bad)
                later = groups(bad)[-1][0]['receipt_id']
                for row in groups(bad)[-2]:
                    row['identity_payload']['core']['parent_receipt_ids'] = [later]
            else:
                for row in group:
                    row['identity_payload']['core']['parent_receipt_ids'] = choices[kind]
            rehash_receipt_chain(bad)
            if kind == 'forward_acyclic':
                self.assertEqual(groups(bad)[-2][0]['identity_payload']['core']['parent_receipt_ids'],
                                 [groups(bad)[-1][0]['receipt_id']])
            # Establish content/commit coherence independently before asking
            # the lifecycle owner to reject the actual parent convention.
            for row in bad['receipt_ledger']:
                self.assertEqual(row['receipt_id'], audit_identity('grc-receipt-sha256', row['identity_payload']))
            for record, group in zip(bad['commit_records'], groups(bad), strict=True):
                self.assertEqual(record['commit_id'], audit_identity('grc-commit-sha256', record['payload']))
                self.assertTrue(all(r['commit_id'] == record['commit_id'] for r in group))
            with self.subTest(kind=kind), self.assertRaises(ValueError) as caught:
                restore(bad)
            self.assertEqual(owner.snapshot(), self.parent_snapshot)
            rows.append(dict(mutation=kind, target_group=groups(bad)[-1],
                             parent_projection=[dict(receipt=r['receipt_id'], parents=r['identity_payload']['core']['parent_receipt_ids'])
                                                for r in bad['receipt_ledger']],
                             error_type=type(caught.exception).__name__, message=str(caught.exception)))
        partitions = []
        for kind in ('duplicate_group', 'reordered_groups', 'uncovered_ledger'):
            bad = deepcopy(self.parent_snapshot)
            if kind == 'duplicate_group':
                bad['receipt_ledger'].extend(deepcopy(groups(bad)[-1]))
                bad['commit_records'].append(deepcopy(bad['commit_records'][-1]))
                bad['lifecycle']['receipt_ids'] = [r['receipt_id'] for r in bad['receipt_ledger']]
                bad['lifecycle_digest'] = audit_identity('grcv4-lifecycle-sha256', bad['lifecycle'])
            elif kind == 'reordered_groups':
                bad['commit_records'][-2:] = bad['commit_records'][-2:][::-1]
            else:
                bad['commit_records'].pop()
            with self.assertRaises(ValueError) as caught:
                restore(bad)
            self.assertEqual(owner.snapshot(), self.parent_snapshot)
            partitions.append(dict(mutation=kind, message=str(caught.exception)))
        owner = restore(deepcopy(self.snapshot))
        original = owner._operation._owned
        native = lifecycle.make_commit_receipts
        target = owner._operation.reference
        action = GraphCoordinateAction(target.graph, target.graph, (0, 1), (0,), (1,))
        rejected = []
        for kind in ('migration', 'event', 'representation'):
            def corrupt(payloads, **kwargs):
                values = deepcopy(payloads)
                for row in values:
                    row['core']['parent_receipt_ids'] = [first]
                return native(values, **kwargs)
            declaration = (migration(owner, target) if kind == 'migration' else
                           event(owner, target) if kind == 'event' else representation(owner, target, action))
            call = {'migration': owner.migrate_profile, 'event': owner.reconstruct_topology_event,
                    'representation': owner.transport_representation}[kind]
            with patch.object(lifecycle, 'make_commit_receipts', side_effect=corrupt):
                with self.assertRaises(V4IdentityError) as caught:
                    call(declaration)
            self.assertIs(owner._operation._owned, original)
            self.assertEqual(owner.snapshot(), self.snapshot)
            rejected.append(dict(operation=kind, request=declaration.to_payload(), message=str(caught.exception)))
        EVIDENCE['coherent_negatives'] = dict(source_snapshot=self.parent_snapshot,
            restores=rows, publications=rejected, partitions=partitions)

    def test_duplicate_forks_detach_mutability_and_allow_shared_content_ids(self):
        # A short persistent representation history exercises a nonempty
        # transition archive and the new singleton root without replaying
        # unrelated CI crossings for each duplicate/loader check.
        inputs, _ = fixture('C_PC')
        target, _, action = reversed_target(inputs, None)
        owner = GRCV4(inputs, targets=(target,))
        result = owner.transport_representation(representation(owner, target, action))
        self.assertTrue(result.committed, result.failure)
        prefix = owner.snapshot()
        root = independent_chain(prefix)
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0]['group_size'], 1)
        self.assertIsNone(root[0]['parent'])
        left, right = owner.duplicate(), owner.duplicate()
        self.assertIsNot(owner._operation._owned, left._operation._owned)
        self.assertIsNot(left._operation._lock, right._operation._lock)
        with TemporaryDirectory(prefix='p976-data-') as directory:
            path = Path(directory) / 'state.json'
            owner.save(str(path))
            self.assertEqual(path.read_bytes(), canonical_json_bytes(prefix))
            loaded = GRCV4.load(str(path))
            self.assertEqual(loaded.snapshot(), prefix)
        exported = left.snapshot()
        exported['scientific_state']['authoritative']['C'][0] = 123
        exported['receipt_ledger'][0]['identity_payload']['core']['parent_receipt_ids'].append('foreign')
        exported['commit_records'].clear()
        exported['transition_records'].clear()
        exported['reference_registry'].clear()
        for value in (owner, left, right, loaded):
            self.assertEqual(value.snapshot(), prefix)
        for value in (left, right):
            self.assertTrue(value.step_v4_input(request(0, 'shared-fork')).committed)
        shared = left.snapshot()
        self.assertEqual(right.snapshot(), shared)
        self.assertEqual(owner.snapshot(), prefix)
        left.reset()
        self.assertEqual(right.snapshot(), shared)
        right.rebase_reset_baseline()
        self.assertNotEqual(left.snapshot()['lifecycle_digest'], right.snapshot()['lifecycle_digest'])
        for value in (left, right):
            independent_chain(value.snapshot())
            self.assertEqual(restore(value.snapshot()).snapshot(), value.snapshot())
        self.assertEqual(owner.snapshot(), prefix)
        self.assertEqual(loaded.snapshot(), prefix)
        EVIDENCE['forks'] = dict(source=inputs.to_payload(), target=target.to_payload(),
                               root_groups=root, prefix=endpoint(prefix), shared=endpoint(shared),
                               left=endpoint(left.snapshot()), right=endpoint(right.snapshot()),
                               exported_mutation_did_not_publish=True, save_load_equal=True)

    def test_symbolic_self_forward_cycles_and_duplicate_partition(self):
        from check_p9492_parent_proposal import main, validate_parent_projection
        output = StringIO()
        with redirect_stdout(output):
            main()
        result = json.loads(output.getvalue())
        self.assertEqual(result['symbolic_valid_cases'], 9)
        self.assertEqual(len(result['symbolic_mutations_rejected']), 16)
        self.assertTrue({'self_parent', 'forward_parent', 'two_commit_cycle', 'duplicate_receipt_id',
                         'intra_commit_auxiliary_parent', 'reordered_commit_groups'}.issubset(result['symbolic_mutations_rejected']))
        # The newer representation group is a singleton, not four receipts.
        projection = [[('root', ())], [('step', ('root',)), ('aux', ('root',))]]
        validate_parent_projection(projection)
        self.assertEqual(result['runtime_executions'], 0)
        EVIDENCE['symbolic'] = dict(result, additional_mixed_arity_control=projection)


if __name__ == '__main__':
    unittest.main()
