"""Independent P9-7.3 channel/charge assertions over accepted runtime owners."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
import unittest

from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest, GRCV4MappedTopologyEventRequest
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_events import reconstruction_history_policy
from pygrc.models.grc_v4_migration import migration_history_policy
from pygrc.models.grc_v4_lifecycle import _state_inputs, _fresh_geometry
from pygrc.models.grc_v4_initializer import HISTORY_POLICY
from tests.models.test_grc_v4_migration import fixture, owner_for, migration, changed_reference
from tests.models.test_grc_v4_initializer import target as initializer_target
from tests.models.test_grc_v4_events import event, representation, reversed_target

EVIDENCE = {}


def history(inputs, subject):
    """Literal current-then-reset identity; not the runtime history helper."""
    field = 'W_A' if subject == 'candidate' else 'Z_4'
    current, reset = getattr(inputs.current, field), getattr(inputs.reset, field)
    if current is None and reset is None:
        return None
    assert current is not None and reset is not None
    payload = dict(schema_version='grcv4-history-content-identity-v1', subject=subject,
                   content=list(current) + list(reset))
    return 'grcv4-history-content-sha256:' + sha256(canonical_json_bytes(payload)).hexdigest()


def expected(kind, a, b, old, new):
    """Spec tables, independently of runtime policy factories and receipts."""
    candidate = {
        ('C', 'C'): ('candidate_c_rederive_no_history_v1', 'rederived', 'none', None),
        ('C', 'A'): (HISTORY_POLICY, 'target_initializer', 'none', 'grcv4-a-target-reference-pass-v1'),
        ('A', 'C'): ('archive_drop_candidate_history_v1', 'explicit_loss', 'candidate_history_loss', None),
        ('A', 'A'): ('identity_candidate_history_v1', 'exact_transport', 'none', None),
    }[a, b]
    if kind == 'event' and a == b == 'A':
        candidate = ('candidate_a_event_loss_reference_pass_v1', 'explicit_loss',
                     'candidate_history_loss', 'grcv4-a-target-reference-pass-v1')
    if not old and not new:
        carrier = ('no_persistent_carrier_v1', 'not_applicable', 'none', None)
    elif not old:
        carrier = ('canonical_zero_carrier_initialization_v1', 'target_initializer', 'none', 'canonical_zero_carrier_v1')
    elif not new:
        carrier = ('archive_drop_carrier_history_v1', 'explicit_loss', 'carrier_history_loss', None)
    elif kind == 'migration' and a == b:
        carrier = ('identity_carrier_history_v1', 'exact_transport', 'none', None)
    else:
        carrier = ('event_loss_and_zero_target_carrier_v1' if kind == 'event' else 'loss_and_zero_target_carrier_v1',
                   'whole_carrier_reset', 'carrier_history_loss', 'canonical_zero_carrier_v1')
    return dict(candidate=candidate, carrier=carrier)


class HistoryPolicyTests(unittest.TestCase):
    def assert_receipts(self, before, owner, result, channels):
        self.assertTrue(result.committed, result.failure)
        after = _state_inputs(owner._operation.reference, owner.state.lifecycle)
        primary = result.emitted_receipts[0].identity_payload
        losses = [channels[s][2] for s in ('candidate', 'carrier') if channels[s][2] != 'none']
        for subject in ('candidate', 'carrier'):
            row = primary['history'][subject]
            self.assertEqual(row['source_history_digest'], history(before, subject))
            self.assertEqual(row['target_history_digest'], history(after, subject))
            self.assertEqual(row['disposition'], channels[subject][1])
            self.assertEqual(row['information_loss'], channels[subject][2])
        for receipt in result.emitted_receipts:
            self.assertEqual(list(receipt.identity_payload['core']['information_losses']), losses)
        self.assertEqual((after.time, after.step_index), (before.time, before.step_index))
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        return after

    def test_complete_discrete_policy_matrix(self):
        rows = []
        for kind, factory in (('migration', migration_history_policy), ('event', reconstruction_history_policy)):
            for a in ('A', 'C'):
                for b in ('A', 'C'):
                    for old in (False, True):
                        for new in (False, True):
                            inputs, _ = fixture(a + ('_PC' if old else '_OS'))
                            target = fixture(b + ('_PC' if new else '_OS'))[0].geometry.reference
                            if b == 'A':
                                target = changed_reference(target, 'lifecycle', history_policy_id=HISTORY_POLICY)
                            policy = factory(inputs, target)
                            channels = expected(kind, a, b, old, new)
                            for subject, values in channels.items():
                                row = getattr(policy, subject)
                                self.assertEqual((row.policy_id, row.disposition, row.information_loss, row.target_initializer_id), values)
                                self.assertEqual(row.source_history_digest, history(inputs, subject))
                            rows.append(dict(operation=kind, source=a, target=b, source_persistent=old,
                                             target_persistent=new, policy=policy.to_payload()))
        self.assertEqual(len(rows), 32)
        EVIDENCE['policy_matrix'] = rows

    def test_native_migration_and_event_channel_combinations(self):
        cases = [('migration', 'A_PC', 'C_PC'), ('migration', 'C_PC', 'A_PC'),
                 ('migration', 'A_PC', 'A_CI_PC'), ('event', 'A_PC', 'A_PC'),
                 ('event', 'C_OS', 'A_PC')]
        rows = []
        for kind, source, target_family in cases:
            with self.subTest(kind=kind, source=source, target=target_family):
                target = initializer_target(target_family)[0] if target_family[0] == 'A' and (source[0] == 'C' or kind == 'event') else None
                owner, target = owner_for(source, target_family, target_ref=target)
                before = _state_inputs(owner._operation.reference, owner.state.lifecycle)
                if kind == 'event' and source == 'A_PC':
                    # Present but zero is not absent, nor loss-free reconstruction.
                    inputs = _fresh_geometry(replace(before, current=replace(before.current, Z_4=(0.,)), reset=replace(before.reset, Z_4=(0.,))))
                    owner, target = owner_for(source, target_family, source_inputs=inputs, target_ref=target)
                    before = _state_inputs(owner._operation.reference, owner.state.lifecycle)
                declared = migration(owner, target) if kind == 'migration' else event(owner, target)
                result = owner.migrate_profile(declared) if kind == 'migration' else owner.reconstruct_topology_event(declared)
                channels = expected(kind, source[0], target_family[0], source.endswith('_PC'), True)
                after = self.assert_receipts(before, owner, result, channels)
                self.assertEqual(after.current.C, before.current.C)
                self.assertEqual(after.reset.C, before.reset.C)
                self.assertEqual(after.Q_target, before.Q_target)
                self.assertEqual(result.emitted_receipts[0].identity_payload['core']['actual_charge_delta'], 0)
                if channels['carrier'][1] == 'exact_transport':
                    self.assertEqual((after.current.Z_4, after.reset.Z_4), (before.current.Z_4, before.reset.Z_4))
                else:
                    self.assertEqual((after.current.Z_4, after.reset.Z_4), ((0.,), (0.,)))
                rows.append(dict(operation=kind, source=source, target=target_family,
                                 request=declared.to_payload(),
                                 source_current=dict(C=list(before.current.C), W_A=before.current.W_A, Z_4=before.current.Z_4),
                                 source_reset=dict(C=list(before.reset.C), W_A=before.reset.W_A, Z_4=before.reset.Z_4),
                                 current=dict(C=list(after.current.C), W_A=after.current.W_A, Z_4=after.current.Z_4),
                                 reset=dict(C=list(after.reset.C), W_A=after.reset.W_A, Z_4=after.reset.Z_4),
                                 receipts=[r.to_payload() for r in result.emitted_receipts]))
        EVIDENCE['native_crossings'] = rows

    def test_representation_is_not_reconstruction_loss(self):
        inputs, backend = fixture('A_PC')
        target, mapped_backend, action = reversed_target(inputs, backend)
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,), target_differential_references=(mapped_backend,))
        result = owner.transport_representation(representation(owner, target, action))
        channels = {s: ('coordinate', 'exact_transport', 'none', None) for s in ('candidate', 'carrier')}
        self.assert_receipts(inputs, owner, result, channels)
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertEqual(result.emitted_receipts[0].identity_payload['charge']['delta_semantics'], 'exact_coordinate_action')
        EVIDENCE['representation'] = result.emitted_receipts[0].to_payload()

    def test_current_reset_digests_and_channel_loss_tampering_reject(self):
        owner, target = owner_for('A_PC', 'C_PC')
        before = owner.snapshot()
        publication = owner._operation._owned
        for kind in ('migration', 'event'):
            good = (migration(owner, target) if kind == 'migration' else event(owner, target)).to_payload()
            mutations = []
            for subject in ('candidate', 'carrier'):
                for field, value in (('information_loss', 'none'), ('source_history_digest', None),
                                     ('disposition', 'exact_transport')):
                    bad = deepcopy(good); bad['history_policy'][subject][field] = value; mutations.append(bad)
                bad = deepcopy(good)
                actual = _state_inputs(owner._operation.reference, owner.state.lifecycle)
                wrong_reset = replace(actual, reset=actual.current)
                bad['history_policy'][subject]['source_history_digest'] = history(wrong_reset, subject)
                mutations.append(bad)
            for bad in mutations:
                declared = (GRCV4MigrationRequest if kind == 'migration' else GRCV4MappedTopologyEventRequest).from_payload(bad)
                # New event wire restrictions can reject before lifecycle entry.
                from pygrc.models.grc_v4_codec import V4SchemaError
                try:
                    result = owner.migrate_profile(declared) if kind == 'migration' else owner.reconstruct_topology_event(declared)
                except V4SchemaError:
                    self.assertEqual(kind, 'event')
                else:
                    self.assertFalse(result.committed)
                    self.assertEqual(len(result.emitted_receipts), 1)
                self.assertIs(owner._operation._owned, publication)
                self.assertEqual(owner.snapshot(), before)
        EVIDENCE['rejected_channel_mutations'] = 16

    def test_affine_charge_uses_rounded_resources_not_declared_increment(self):
        inputs, _ = fixture('C_OS'); owner = GRCV4(inputs)
        rows = []
        for matrix, delta in (((1., 0., 0., 1.), (5e-324, 0.)), ((.5, 0., .5, 1.), (.25, 0.))):
            before = _state_inputs(owner._operation.reference, owner.state.lifecycle)
            declared = event(owner, before.geometry.reference, matrix, delta)
            result = owner.reconstruct_topology_event(declared)
            after = self.assert_receipts(before, owner, result, expected('event', 'C', 'C', False, False))
            for old, new in ((before.current, after.current), (before.reset, after.reset)):
                expected_C = tuple(float(F(delta[i]) + sum((F(matrix[2*i+j])*F(old.C[j]) for j in range(2)), F())) for i in range(2))
                self.assertEqual(new.C, expected_C)
            actual = sum(map(F, after.current.C)) - sum(map(F, before.current.C))
            self.assertEqual(F(after.Q_target), F(before.Q_target) + actual)
            self.assertEqual(F(result.emitted_receipts[0].identity_payload['core']['actual_charge_delta']), actual)
            if delta[0] == 5e-324:
                self.assertEqual(actual, 0)
                self.assertNotEqual(actual, F(delta[0]))
            rows.append(dict(transform=declared.resource_transform.to_payload(), current=list(after.current.C),
                             reset=list(after.reset.C), Q_target=after.Q_target, primary=result.emitted_receipts[0].to_payload()))
        EVIDENCE['affine_charge'] = rows

    def test_exact_charge_form_and_reset_only_target_mismatch_reject(self):
        inputs, _ = fixture('C_OS')
        target = inputs.geometry.reference
        source = changed_reference(target, 'charge', absolute_tolerance=.25)
        inputs = replace(inputs, geometry=source.geometry(), reset=replace(inputs.reset, C=(2.125, 2.)))
        owner = GRCV4(inputs, targets=(target,))
        before, publication = owner.snapshot(), owner._operation._owned
        result = owner.reconstruct_topology_event(event(owner, target))
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, 'target_readmission')
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), before)
        # Binary64 addition hides this nonconservative column; exact input
        # arithmetic must still reject it before any target publication.
        self.assertEqual(1. + 5e-324, 1.)
        declared = event(owner, source, (1., 5e-324, 0., 1.))
        result = owner.reconstruct_topology_event(declared)
        self.assertFalse(result.committed)
        self.assertEqual(result.failure.stage, 'admission')
        self.assertIs(owner._operation._owned, publication)
        self.assertEqual(owner.snapshot(), before)
        EVIDENCE['charge_rejections'] = ['reset_only_target_charge', 'exact_subnormal_column_excess']


if __name__ == '__main__':
    unittest.main(verbosity=2)
