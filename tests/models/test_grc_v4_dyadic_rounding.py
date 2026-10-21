"""Independent exact-rational pressure of the dense-output proof kernel."""
from fractions import Fraction
import math
import random
import unittest
from unittest.mock import patch

import flint
from pygrc.models import grc_v4_certification as cert
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend


def fraction_value(m, e):
    return Fraction(m << e) if e >= 0 else Fraction(m, 1 << -e)


def rational_ball(ball):
    if not ball.is_finite():
        raise cert.CertificationInconclusive('nonfinite Arb enclosure')
    return cert.round_interval(ball.lower().fmpq(), ball.upper().fmpq())


class DyadicRoundingTests(unittest.TestCase):
    def assert_fraction_round(self, m, e):
        try:
            expected = float(fraction_value(m, e))
        except OverflowError:
            with self.assertRaises(cert.CertificationInconclusive):
                cert._round_dyadic(m, e)
        else:
            actual = cert._round_dyadic(m, e)
            self.assertEqual(actual, expected)
            if not expected:
                self.assertEqual(math.copysign(1., actual), 1.)

    def test_seeded_exact_fraction_comparison(self):
        rng = random.Random(984)
        for _ in range(2500):
            m = rng.getrandbits(rng.randrange(1, 513)) * rng.choice((-1, 1))
            self.assert_fraction_round(m, rng.randrange(-1800, 1100))

    def test_ties_powers_subnormal_transition_and_overflow(self):
        values = (0., 2**-1074, -2**-1074, 2**-1022, -2**-1022,
                  math.nextafter(2**-1022, 0.), 1., -1.,
                  math.nextafter(1., 2.), math.nextafter(1., 0.),
                  float.fromhex('0x1.fffffffffffffp+1023'))
        with exact_backend(ExactBackend.PYTHON):
            for v in values:
                lo, hi, _ = cert._rounding_cell(v)
                for endpoint in (lo, hi):
                    n, d = endpoint.as_integer_ratio()
                    e = -(d.bit_length()-1)
                    # Exactly at and strictly on both sides of every cell boundary.
                    for offset in (-1, 0, 1):
                        self.assert_fraction_round((n << 300)+offset, e-300)
        for m in (1, -1, 3, -3):
            self.assert_fraction_round(m, -1075)
        self.assertEqual(cert._round_dyadic(1, -10**9), 0.)
        with self.assertRaises(cert.CertificationInconclusive):
            cert._round_dyadic(1, 10**9)

    def test_whole_ball_matches_original_rational_cell_check(self):
        rng = random.Random(83)
        with exact_backend(ExactBackend.FLINT), flint.ctx.workprec(256):
            balls = [flint.arb(flint.fmpq(rng.randrange(-10**9, 10**9), rng.randrange(1, 10**9)))
                     for _ in range(500)]
            balls += [flint.arb('0 +/- 1e-1000'), flint.arb('1 +/- 1e-10'),
                      flint.arb('+inf'), flint.arb('nan')]
            for ball in balls:
                try:
                    expected = rational_ball(ball)
                except cert.CertificationInconclusive:
                    with self.assertRaises(cert.CertificationInconclusive):
                        cert._round_ball(ball)
                else:
                    self.assertEqual(cert._round_ball(ball), expected)

    def test_two_changing_native_steps_preserve_full_stages(self):
        from tests.models.test_grc_v4_os_pass_probe import before, compare_point
        from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
        from pygrc.models.grc_v4_numerics import matrix_operation
        with exact_backend(ExactBackend.FLINT), cert.numerical_policy(cert.NumericalPolicy.CERTIFIED_ARB_256):
            old_before = new_before = before()
            for _ in range(2):
                with patch.object(cert, '_round_ball', rational_ball), matrix_operation():
                    old = ProvisionalCandidateCOSStep(old_before)
                with matrix_operation():
                    new = ProvisionalCandidateCOSStep(new_before)
                self.assertEqual(old.next_inputs, new.next_inputs)
                self.assertNotEqual(new_before.current.C, new.next_inputs.current.C)
                for stage in ('predictor', 'corrector'):
                    compare_point(self, getattr(new.os_pass, stage), getattr(old.os_pass, stage))
                compare_point(self, new.final, old.final)
                self.assertEqual(new.os_pass.residual, old.os_pass.residual)
                old_before, new_before = old.next_inputs, new.next_inputs


if __name__ == '__main__':
    unittest.main()
