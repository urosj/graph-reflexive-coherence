"""Small diagnostic-parity checks; these do not replace the large read check."""
import json
import lzma
import unittest

import p984h_cos_kernel_profile as probe


class KernelInstrumentation(unittest.TestCase):
    def test_retained_read_binding_and_parity_not_campaign_credit(self):
        record = json.loads(lzma.decompress((probe.run.ROOT / probe.OUTPUT).read_bytes()))
        baseline = json.loads(lzma.decompress((probe.run.ROOT / probe.probe.OUTPUT).read_bytes()))
        self.assertEqual(record, probe.run.seal(record))
        self.assertEqual(baseline, probe.run.seal(baseline))
        self.assertEqual(record['baseline_record_digest'], baseline['record_digest'])
        self.assertEqual(record['input_digest'], baseline['input_digest'])
        self.assertEqual(record['scientific_view_digest'], probe.run.digest(
            {k: baseline[k] for k in probe.previous.FIELDS}))
        self.assertTrue(record['baseline_parity'])
        self.assertEqual((record['native_events'], record['native_steps']), (0, 0))
        for path, digest in record['source_bindings'].items():
            with self.subTest(path=path):
                from p984h_pre_solve_reuse_sources import historical_binding
                self.assertTrue(historical_binding(path, digest, (probe.run.ROOT / path).read_bytes()))
        attributed = sum(row['exclusive_seconds'] for row in record['counters'].values())
        self.assertAlmostEqual(attributed + record['uninstrumented_seconds'], record['elapsed_seconds'])

    def test_installed_solve_expressions_and_failure_behavior(self):
        cert = probe.probe.cert
        with probe.run.oracle.exact_backend(probe.run.oracle.ExactBackend.FLINT), cert.numerical_policy(cert.NumericalPolicy.CERTIFIED_ARB_256):
            timers = probe.Timers()
            timed = probe.instrument(cert.rounded_solve, timers, precision_body=True)
            cases = [
                (((2., 0.), (0., 4.)), ((1.,), (2.,))),
                (((2., 1.), (1., 3.)), ((1., 0.), (0., 1.))),
                (((0.,),), ((1.,),)),
                (((1., 2.), (2., 4.)), ((1.,), (0.,))),
                (((1.,),), ((1.,), (2.,))),
            ]
            def outcome(fn, a, b):
                try:
                    return 'ok', fn(a, b)
                except Exception as exc:
                    return type(exc).__name__, str(exc)
            for a, b in cases:
                with self.subTest(matrix=a, rhs=b):
                    self.assertEqual(outcome(cert.rounded_solve, a, b), outcome(timed, a, b))
                    self.assertEqual(timers.stack, [])
            self.assertTrue(timers.counters)

    def test_patches_restore_even_on_failure(self):
        original = probe.probe.cert.rounded_solve
        algebra = probe.probe.candidate._CandidateCAlgebra.__post_init__
        with self.assertRaisesRegex(RuntimeError, 'injected'):
            with probe.timing(probe.Timers()):
                self.assertIsNot(original, probe.probe.cert.rounded_solve)
                raise RuntimeError('injected')
        self.assertIs(original, probe.probe.cert.rounded_solve)
        self.assertIs(algebra, probe.probe.candidate._CandidateCAlgebra.__post_init__)


if __name__ == '__main__':
    unittest.main()
