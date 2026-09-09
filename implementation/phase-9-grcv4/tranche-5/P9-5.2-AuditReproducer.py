#!/usr/bin/env python3
"""Targeted P9-5.2 regression proposals, using the real repository fixtures.

Run with the submitted source overlay and its dependencies:
  PYTHONPATH=src:. .venv/bin/python implementation/phase-9-grcv4/tranche-5/P9-5.2-AuditReproducer.py

The first two tests encode recommended post-correction behavior. They are
expected to expose the submitted implementation's two findings; they are NOT
expected-failure or skipped tests. The third is a forward-readmission boundary
characterization, not a request to make the provisional writer a lifecycle owner.

Audit note: this repository-integrated file was compiled, but not executed in
this audit environment (no runnable dependency-complete checkout). Findings
were reproduced with the unchanged relevant uploaded function/class bodies in
an explicitly isolated harness. See P9-5.2-AuditPressure.json for those results.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import DefaultContext, Inexact, Rounded
from fractions import Fraction
import math
import unittest

from pygrc.models.grc_v4_candidate_a import (
    CandidateACurrent, CandidateAStageError, CandidateAWriter,
    candidate_a_log_interpolation,
)
from pygrc.models.grc_v4_geometry import H_profile
from tests.models.test_grc_v4_candidate_a import current_fixture, write_fixture


class P952AuditRegressionTests(unittest.TestCase):
    def test_finite_corrector_not_rejected_by_decomposition_diagnostic_overflow(self):
        """Reference succeeds; real predictor source generates the corrected h=4."""
        s = math.ldexp(1.0, 1023)
        before, backend = current_fixture(
            C=(1.0, 0.0), W=(2.0,),
            eta=math.ldexp(1.0, -1024),
            kappa_c=math.ldexp(1.0, 1022),
            kappa_Ah=-3 * math.ldexp(1.0, 1021),
            chi_A=1.0, zeta_A=1.5,
            changes={"geometry": {"kappa_H": 1.125}},
        )
        ref = before.geometry.reference
        predictor = CandidateACurrent(replace(before, stage="os_predictor"), backend)
        self.assertEqual(predictor.baseline.values, (-2.0,))
        self.assertEqual(predictor.current.values, (-4.0,))
        geometry = H_profile(
            predictor.structural_source(),
            reference=ref, context=ref.context, profile=ref.profile,
        )
        self.assertEqual(geometry.one_form_hodge.matrix, ((4.0,),))
        corrected = CandidateACurrent(
            replace(before, stage="os_corrector", geometry=geometry), backend
        )
        self.assertEqual(corrected.potential.values, (-1.25 * s, 1.25 * s))
        self.assertEqual(corrected.baseline.values, (2.5,))
        self.assertEqual(corrected.denominator_exact, (Fraction(1, 2),))
        self.assertEqual(corrected.current.values, (5.0,))

    def test_log_writer_pins_traps_not_just_precision(self):
        """DefaultContext is ordinary caller-configurable library state."""
        expected = candidate_a_log_interpolation((0.125,), (7.0,), 0.125, 0.7)
        saved_traps = dict(DefaultContext.traps)
        try:
            DefaultContext.traps[Inexact] = True
            DefaultContext.traps[Rounded] = True
            self.assertEqual(
                candidate_a_log_interpolation((0.125,), (7.0,), 0.125, 0.7),
                expected,
            )
        finally:
            DefaultContext.traps = saved_traps

    def test_positive_writer_output_is_not_complete_poststate_readmission(self):
        """Local writer legitimately returns W=2; the new state's current is singular.

        Carry this case to P9-5.3/full lifecycle integration as an atomic-negative
        post-writer target, keeping the already selected beat current distinct
        from a read-only poststate admission calculation.
        """
        point, resource = write_fixture(
            C=(0.0, 0.0), W=(4.0,), kappa_c=0.0,
            alpha=0.0, beta=0.0, gamma=0.0,
            chi_A=1.0, zeta_A=3.0, tau_A=1.0, dt=math.log(2.0),
        )
        self.assertEqual(point.denominator_exact, (Fraction(-4, 5),))
        self.assertEqual(point.current.values, (0.0,))
        writer = CandidateAWriter(point, resource)
        self.assertEqual(writer.W_drv_A, (1.0,))
        self.assertEqual(writer.authority.state.W_A, (2.0,))
        with self.assertRaises(CandidateAStageError) as caught:
            CandidateACurrent(
                replace(point.inputs, current=writer.authority.state),
                point.differential_reference,
            )
        self.assertEqual(caught.exception.disposition, "singular")


if __name__ == "__main__":
    unittest.main(verbosity=2)
