"""Three audit-suggested native discriminators; --run emits separate evidence."""

import argparse
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as F
import json
import sys
import unittest

import phase9_implementation_policy as p
import verify_p973_history_policy as baseline
from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, GraphCoordinateAction
from pygrc.models.grc_v4_lifecycle import _fresh_geometry, _state_inputs
from pygrc.models.grc_v4_events import coordinate_reference
from tests.models.test_grc_v4_migration import fixture, changed_reference
from tests.models.test_grc_v4_events import event, representation
from test_p973_history_policy import history

SCRIPT = p.HERE + 'test_p973_sharp_regressions.py'
RECORD = p.PHASE + 'tranche-7/P9-7.3-SharpRegressions.json'
EVIDENCE = {}


class SharpRegressions(unittest.TestCase):
    def test_subnormal_products_must_accumulate_before_rounding(self):
        epsilon = 5e-324
        inputs, _ = fixture('C_OS')
        ref = changed_reference(inputs.geometry.reference, 'charge', absolute_tolerance=0., relative_tolerance=0.)
        inputs = _fresh_geometry(replace(inputs, geometry=ref.geometry(), Q_target=2*epsilon,
            current=replace(inputs.current, C=(epsilon, epsilon)), reset=replace(inputs.reset, C=(0., 2*epsilon))))
        owner = GRCV4(inputs)
        declared = event(owner, ref, (.5, .5, .5, .5))
        result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        correct = float(F(.5)*F(epsilon) + F(.5)*F(epsilon))
        premature = float(F(.5)*F(epsilon)) + float(F(.5)*F(epsilon))
        self.assertEqual(correct, epsilon)
        self.assertEqual(premature, 0.)
        state = owner.state.lifecycle
        self.assertEqual(state.current.C, (epsilon, epsilon))
        self.assertEqual(state.reset.authoritative.C, (epsilon, epsilon))
        self.assertEqual(state.Q_target, 2*epsilon)
        self.assertEqual(result.emitted_receipts[0].identity_payload['core']['actual_charge_delta'], 0.)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        EVIDENCE['round_once'] = dict(source_current=list(inputs.current.C), source_reset=list(inputs.reset.C),
            target_current=list(state.current.C), target_reset=list(state.reset.authoritative.C),
            correct_component=correct, premature_component=premature, Q_target=state.Q_target,
            request=declared.to_payload(), receipts=[r.to_payload() for r in result.emitted_receipts])

    def test_admitted_charge_offset_is_not_silently_repaired(self):
        delta = 2**-42
        inputs, _ = fixture('C_OS')
        inputs = replace(inputs, Q_target=4. + delta)
        owner = GRCV4(inputs)
        declared = event(owner, inputs.geometry.reference, increment=(.25, 0.))
        result = owner.reconstruct_topology_event(declared)
        self.assertTrue(result.committed, result.failure)
        state = owner.state.lifecycle
        actual = sum(map(F, state.current.C))
        self.assertEqual(actual, F(4.25))
        self.assertEqual(F(state.Q_target), F(4.25) + F(delta))
        self.assertNotEqual(F(state.Q_target), actual)
        charge = result.emitted_receipts[1].identity_payload
        self.assertEqual(charge['target_charge'], state.Q_target)
        self.assertEqual(charge['admitted_charge'], 4.25)
        self.assertEqual(charge['residual'], -delta)
        self.assertEqual(result.emitted_receipts[0].identity_payload['core']['actual_charge_delta'], .25)
        self.assertEqual(sum(map(F, state.reset.authoritative.C)), F(4.25))
        restored = owner.duplicate()
        self.assertEqual(restored.snapshot(), owner.snapshot())
        restored.reset()
        self.assertEqual(restored.state.lifecycle.Q_target, state.Q_target)
        EVIDENCE['charge_offset'] = dict(source_Q=inputs.Q_target, source_actual=4., target_Q=state.Q_target,
            target_actual=float(actual), residual=charge['residual'], request=declared.to_payload(),
            receipts=[r.to_payload() for r in result.emitted_receipts])

    def test_lossless_two_edge_transport_changes_both_history_hashes(self):
        from tests.models.test_grc_v4_pc import fixture as pc_fixture
        graph = GRCV4Graph(('u', 'v'), (OrientedEdge('e0', 'u', 'v'), OrientedEdge('e1', 'u', 'v')))
        inputs, backend = pc_fixture('A', graph=graph, C=(2.125, 1.875), W=(1.25, 1.75),
            z=(.125, .0625, .0625, -.25), reset_z=(.25, -.03125, -.03125, .125),
            changes={'candidate': {'chi_A': .125, 'zeta_A': .125, 'kappa_Ah': .125}})
        inputs = _fresh_geometry(replace(inputs, reset=replace(inputs.reset, C=(2.0625, 1.9375), W_A=(1.5, 1.625))))
        target_graph = GRCV4Graph(('u', 'v'), (OrientedEdge('f0', 'v', 'u'), OrientedEdge('f1', 'u', 'v')))
        action = GraphCoordinateAction(graph, target_graph, (0, 1), (1, 0), (-1, 1))
        target, target_backend = coordinate_reference(inputs.geometry.reference, action, backend)
        owner = GRCV4(inputs, differential_reference=backend, targets=(target,), target_differential_references=(target_backend,))
        declared = representation(owner, target, action)
        result = owner.transport_representation(declared)
        self.assertTrue(result.committed, result.failure)
        after = _state_inputs(owner._operation.reference, owner.state.lifecycle)
        for old, new in ((inputs.current, after.current), (inputs.reset, after.reset)):
            self.assertEqual(new.C, old.C)
            self.assertEqual(new.W_A, old.W_A[::-1])
            # Literal U Z U^T for U=((0,-1),(1,0)), independent of runtime action.
            z = old.Z_4
            self.assertEqual(new.Z_4, (z[3], -z[2], -z[1], z[0]))
            self.assertEqual(sum(F(x)**2 for x in new.Z_4), sum(F(x)**2 for x in z))
        primary = result.emitted_receipts[0].identity_payload
        for subject in ('candidate', 'carrier'):
            old, new = history(inputs, subject), history(after, subject)
            self.assertNotEqual(old, new)
            self.assertEqual(primary['history'][subject]['source_history_digest'], old)
            self.assertEqual(primary['history'][subject]['target_history_digest'], new)
            self.assertEqual(primary['history'][subject]['disposition'], 'exact_transport')
            self.assertEqual(primary['history'][subject]['information_loss'], 'none')
        self.assertEqual(list(primary['core']['information_losses']), [])
        self.assertEqual(len(result.emitted_receipts), 1)
        self.assertEqual(after.Q_target, inputs.Q_target)
        self.assertEqual(owner.duplicate().snapshot(), owner.snapshot())
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current, after.reset)
        def state(s): return dict(C=list(s.C), W_A=list(s.W_A), Z_4=list(s.Z_4))
        EVIDENCE['changed_hashes_without_loss'] = dict(source_current=state(inputs.current), source_reset=state(inputs.reset),
            target_current=state(after.current), target_reset=state(after.reset),
            request=declared.to_payload(), receipt=result.emitted_receipts[0].to_payload())


def bindings():
    return {**baseline.bindings(), SCRIPT: p.sha((p.ROOT/SCRIPT).read_bytes())}


def roster():
    return ['test_p973_sharp_regressions.SharpRegressions.' + n for n in unittest.TestLoader().getTestCaseNames(SharpRegressions)]


def check():
    value = p.read(p.ROOT/RECORD)
    prior = baseline.check()
    p.require(value['record_digest'] == p.digest_record(value) and value['source_bindings'] == bindings(), 'sharp regression evidence/source drift')
    p.require(value['baseline_record_digest'] == prior['record_digest']
              and value['test_ids'] == roster() and value['results'] == dict(tests_run=3, failures=[], errors=[], skips=[]), 'sharp regression execution incomplete')
    p.require(set(value['cases']) == {'round_once', 'charge_offset', 'changed_hashes_without_loss'}
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'sharp regression scope drift')
    return dict(record_path=RECORD, record_digest=value['record_digest'], test_count=3, numerical_tests_rerun=0)


def run():
    import test_p973_sharp_regressions as module
    source, prior = bindings(), baseline.check()
    module.EVIDENCE.clear()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(roster()))
    p.require(result.wasSuccessful() and not result.skipped, 'sharp regressions failed')
    p.require(source == bindings(), 'sharp regression sources changed during execution')
    value = dict(schema='phase9_history_policy_sharp_regressions_v1', iteration_id='P9-7.3',
        captured_at=datetime.now(timezone.utc).isoformat(), baseline_record_digest=prior['record_digest'],
        source_bindings=source, test_ids=roster(), results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        cases=module.EVIDENCE, new_G2_support=[], G3_accepted=False)
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    print(json.dumps(run() if parser.parse_args().run else check(), indent=2))
