"""Focused native segment input/retained pressure; no numerical campaign."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984h_cos_native as run


class NativeBaseline(unittest.TestCase):
    def test_declaration_and_roundtrip(self):
        with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT), run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
            _, source = run.oracle.second_source_input()
            self.assertEqual(run.state(source.to_payload()).to_payload(), source.to_payload())
            m = run.manifest()
            self.assertEqual(m['target_steps_per_role'], 1)
            self.assertEqual(m['planned_total_steps_per_role'], 10)
            self.assertFalse(m['covariance_executed'])
            self.assertEqual(m['numerical_policy'], 'certified_arb_256_weighted_v1')

    def test_retained_prefix_pressure(self):
        if not (run.ROOT/run.path('prefix')).exists(): self.skipTest('native prefix not run')
        with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT), run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
            value=run.checked('prefix'); m=run.manifest()
            with patch.object(run,'manifest',return_value=m), patch.object(run,'ProvisionalCandidateCOSStep',side_effect=AssertionError('numerics')):
                for mutate in (
                    lambda v:v.update(covariance_executed=True),
                    lambda v:v['execution'].update(native_events=1),
                    lambda v:v['execution']['steps'][1]['after_C'].__setitem__(0,-1.),
                    lambda v:v['execution']['steps'][1].update(after_index=99),
                    lambda v:v['execution']['steps'][1]['final'].update(input_hodge_digest='stale'),
                ):
                    bad=deepcopy(value);mutate(bad)
                    with patch.object(run,'read',return_value=run.seal(bad)),self.assertRaises(ValueError): run.checked('prefix')


if __name__ == '__main__': unittest.main()
