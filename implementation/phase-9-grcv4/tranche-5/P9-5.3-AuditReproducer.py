#!/usr/bin/env python3
"""P9-5.3 audit regressions for the real repository.

From the repository root, with its locked environment:
    PYTHONPATH=src:. .venv/bin/python implementation/phase-9-grcv4/tranche-5/P9-5.3-AuditReproducer.py

This file is compiled but NOT executed in the audit environment. Equivalent
numerical/control-flow findings were executed in the isolated harness described
in P9-5.3-AuditPressure.json. These tests encode the recommended corrected
behavior; do not mark them expected failures or claim their execution here.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import math
import sys
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4_candidate_a import CandidateACurrent
from pygrc.models.grc_v4_candidate_c import CandidateCStageError
from pygrc.models.grc_v4_geometry import GRCV4Graph, H_profile, OrientedEdge
from pygrc.models.grc_v4_realizations import CandidateAOSPass, OSStageError
from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep
from tests.models.test_grc_v4_realizations import a_os_fixture


def extreme_fixture(tolerance: float = 64.0):
    s = math.ldexp(1.0, 1023)
    graph = GRCV4Graph(
        ("u", "v"),
        (OrientedEdge("a", "u", "v"), OrientedEdge("b", "u", "v")),
    )
    # Multiplication order matters when preparing this fixture: 3*s overflows,
    # whereas 3*(s/8) is the intended finite reference value.
    return a_os_fixture(
        graph=graph,
        weights={"a": s / 8, "b": 3 * (s / 8)},
        C=(1.0, 2.0), W=(2.0, 3.0),
        eta=1.0, kappa_c=s / 64, kappa_Ah=1 / 256,
        alpha=0.0, beta=0.0, gamma=0.0,
        chi_A=1.0, zeta_A=1.0,
        dt=math.ldexp(1.0, -1030),
        changes={
            "geometry": {"kappa_H": s},
            "realization": {"tolerance": tolerance},
            "solver": {"conditioning_limit": 1e12},
            "charge": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0},
        },
    )


def source_geometry(point):
    ref = point.inputs.geometry.reference
    return H_profile(
        point.structural_source(), reference=ref,
        context=ref.context, profile=ref.profile,
    )


def exact_residual(geometry, regenerated):
    return tuple(
        tuple(Fraction(a) - Fraction(b) for a, b in zip(left, right, strict=True))
        for left, right in zip(
            geometry.one_form_hodge.matrix,
            regenerated.one_form_hodge.matrix, strict=True,
        )
    )


def positive_definite_two_by_two(matrix) -> bool:
    """Independent exact Sylvester test, not the production inertia helper."""
    return (
        matrix[0][1] == matrix[1][0]
        and matrix[0][0] > 0
        and matrix[0][0] * matrix[1][1] > matrix[0][1] ** 2
    )


class P953AuditRegressions(unittest.TestCase):
    def test_finite_whitened_split_does_not_require_finite_raw_display_entries(self):
        before, backend = extreme_fixture()
        pred = CandidateACurrent(replace(before, stage="os_predictor"), backend)
        geometry = source_geometry(pred)
        corr = CandidateACurrent(
            replace(before, geometry=geometry, stage="os_corrector"), backend,
        )
        regenerated = source_geometry(corr)
        residual = exact_residual(geometry, regenerated)
        self.assertGreater(abs(residual[0][1]), Fraction(sys.float_info.max))
        href = before.geometry.one_form_hodge.matrix
        for sign in (-1, 1):
            bound_matrix = tuple(
                tuple(64 * Fraction(h) + sign * r for h, r in zip(hr, rr, strict=True))
                for hr, rr in zip(href, residual, strict=True)
            )
            self.assertTrue(positive_definite_two_by_two(bound_matrix))
        # This is the behavior requiring correction on the reviewed source.
        passed = CandidateAOSPass(before, backend)
        self.assertTrue(passed.residual.admitted)
        self.assertEqual(
            tuple(tuple(Fraction(x) for x in row) for row in passed.residual.exact_values),
            residual,
        )
        step = ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(step.next_inputs.current.C, (64591 / 65536, 132017 / 65536))
        self.assertEqual(step.next_inputs.current.W_A, (2.0, 3.0))
        self.assertEqual(step.next_inputs.reset, before.reset)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertTrue(all(math.isfinite(v) for v in step.final.current.values))
        self.assertTrue(all(math.isfinite(v) for v in step.restart.current.values))

    def test_exceeded_exact_split_keeps_its_real_failure_reason(self):
        before, backend = extreme_fixture(tolerance=0.0)
        with self.assertRaises(OSStageError) as raised:
            CandidateAOSPass(before, backend)
        self.assertEqual(raised.exception.substage, "split_residual")
        self.assertEqual(raised.exception.__cause__.disposition, "domain_failure")

    def test_shared_numerical_failure_is_classified_at_the_A_OS_boundary(self):
        # Applicable while A reuses C-typed numerical utilities. If the shared
        # utility adopts a candidate-neutral error type, update this type only.
        before, backend = a_os_fixture()
        fault = CandidateCStageError("nonfinite", "explicit shared-helper fault")
        with patch(
            "pygrc.models.grc_v4_realizations.OSSplitResidual", side_effect=fault,
        ):
            with self.assertRaises(OSStageError) as raised:
                CandidateAOSPass(before, backend)
        self.assertEqual(raised.exception.substage, "split_residual")
        cause = raised.exception.__cause__
        self.assertEqual(cause.disposition, "nonfinite")
        # Either retain the numerical cause directly or translate it to the
        # A stage exception and retain the original cause below that adapter.
        self.assertTrue(cause is fault or cause.__cause__ is fault)

    def test_programmer_errors_are_not_scientific_split_failures(self):
        before, backend = a_os_fixture()
        fault = ValueError("explicit programmer fault, not numerical admission")
        with patch(
            "pygrc.models.grc_v4_realizations.OSSplitResidual", side_effect=fault,
        ):
            with self.assertRaises(ValueError) as raised:
                CandidateAOSPass(before, backend)
        self.assertIs(raised.exception, fault)


if __name__ == "__main__":
    unittest.main(verbosity=2)
