"""Bounded continuation pressure without repeated native trajectories."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_cci_continuation as run


class ContinuationTests(unittest.TestCase):
    def test_paths(self):
        for role, step in (('foreign', 1), ('current', 0), ('reset', 11), ('current', True)):
            with self.assertRaises(ValueError): run.path(role, step)
        self.assertTrue(run.path('reset', 'final').endswith('.json.xz'))

    def test_joint_root_pressure(self):
        # Already executed event operand: no new solve required for these controls.
        source = run.event.read('source')['execution']
        before = run.event.state(source['state']).inputs
        value = run.event.read('event')['execution']['admissions'][0]['current']
        run.check_root(value, before)
        for mutate in (
            lambda r: r['point'].update(input_hodge_digest='stale'),
            lambda r: r.update(resource_digest='stale'),
            lambda r: r.update(independent_geometry_residual_upper='1'),
            lambda r: r['certificate'].update(contraction_upper='1'),
            lambda r: r['joint_root_error'].update(current_error_upper='0'),
        ):
            bad = deepcopy(value); mutate(bad)
            with self.assertRaises(ValueError): run.check_root(bad, before)

    def test_retained_chains_and_mutations(self):
        if not (run.ROOT/run.path('current', 1)).exists(): self.skipTest('not executed')
        with patch.object(run, 'CandidateCIRoot', side_effect=AssertionError('native rerun')), \
             patch.object(run, 'ProvisionalCandidateCIStep', side_effect=AssertionError('native rerun')):
            m = run.prior.read(run.INPUTS); self.assertEqual(m, run.manifest())
            before = run.initial('current'); value = run.read('current', 1)
            run.validate(value, m, 'current', 1, before, m['event_record_digest'])
            for mutate in (
                lambda r: r.update(role='reset'), lambda r: r.update(predecessor_digest='foreign'),
                lambda r: r.update(native_events=1), lambda r: r.update(user_accepted=True),
                lambda r: r.update(elapsed_seconds=601), lambda r: r.update(step=2),
                lambda r: r['next_inputs']['reset']['C'].__setitem__(0, 123.),
                lambda r: r['roots']['final']['point'].update(input_hodge_digest='stale'),
                lambda r: r['resource_bounds'].update(minimum_exact_root_lower='1'),
            ):
                bad = deepcopy(value); mutate(bad)
                with self.assertRaises(ValueError):
                    run.validate(run.seal(bad), m, 'current', 1, before, m['event_record_digest'])


if __name__ == '__main__': unittest.main()
