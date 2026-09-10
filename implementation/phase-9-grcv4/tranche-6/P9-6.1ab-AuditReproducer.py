"""Proposed repository-integrated regressions for the P9-6.1a/b audit.

Compiled, NOT executed in the audit environment (the pinned full checkout was
unavailable). Run from repository root with PYTHONPATH=src:. and the reviewed
source subject. These are desired-behavior tests: submitted source is expected
to fail them. The isolated executed numerical harness is separately packaged.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction as F
import unittest
from unittest.mock import patch

from pygrc.models import grc_v4_ci as ci
from pygrc.models.grc_v4_candidate_a import CandidateAStageError
from pygrc.models.grc_v4_candidate_c import CandidateCStageError
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_candidate_a import current_fixture as a_fixture
from tests.models.test_grc_v4_candidate_c import current_fixture as c_fixture
from tests.models.test_grc_v4_ci import configure, fixture


def large_case(candidate: str):
    graph = GRCV4Graph(('u', 'v'), (OrientedEdge('e', 'u', 'v'),))
    h0 = 2.0 ** 100
    if candidate == 'A':
        before, backend = a_fixture(
            graph=graph, weights={'e': h0}, C=(29 / 8, 1.0), W=(2.0,),
            gamma=0.0, kappa_Ah=0.0,
        )
        gain = 2.0 ** 250
    else:
        before = c_fixture(
            graph=graph, weights={'e': h0}, resource=(3.0, 1.0),
            changes={'candidate': {
                'kappa_M_C': 0.0, 'eta_C': 2.0 ** -100,
                'kappa_Phi_C': 2.0 ** -101, 'tau_C': 0.0,
                'chi_C': 0.25, 'zeta_C': 2.0, 'Lambda_C': h0,
            }},
        )
        backend, gain = None, 3 * 2.0 ** 245
    return configure(before, radius=2.0 ** 60, gain=gain, tolerance=1e-11, limit=5), backend


def independent_geometry_residual(candidate: str, h: float) -> F:
    hq, href = F(h), F(2.0 ** 100)
    if candidate == 'A':
        # J=-3, causal flux=-1/2, zeta=3/4, so T(h)=h0+(3/16)k/h^2.
        return hq - href - F(3, 16) * F(2.0 ** 250) / hq**2
    # J=-4 h/h0, causal flat=-1/h0, zeta=2: exact reduced map is constant.
    return hq - href - 2 * F(3 * 2.0 ** 245) / href**2


class CIAdditionalAuditTests(unittest.TestCase):
    def test_A_rounded_fixed_point_is_not_a_certified_small_analytic_residual(self):
        self._check_large('A')

    def test_C_rounded_fixed_point_is_not_a_certified_small_analytic_residual(self):
        self._check_large('C')

    def _check_large(self, candidate: str):
        before, backend = large_case(candidate)
        # The analytic existence certificate should not be confused with
        # availability of a binary64 point satisfying the absolute residual.
        certificate = ci.CIContractionCertificate(before, backend)
        self.assertLess(F(certificate.bounds['contraction_upper']), 1)
        try:
            root = ci.CandidateCIRoot(before, backend)
        except (ci.CIStageError, CandidateAStageError, CandidateCStageError) as exc:
            self.assertEqual(exc.disposition, 'no_admitted_root')
            return
        h = root.selected.inputs.geometry.one_form_hodge.matrix[0][0]
        exact = independent_geometry_residual(candidate, h)
        self.assertLessEqual(exact * exact, F(1e-11) ** 2)

    def test_consumed_root_exhaustion_is_candidate_solve_not_reset_admission(self):
        for candidate in ('C', 'A'):
            before, backend = fixture(candidate, limit=1, tolerance=0.0)
            reset = GRCV4AuthoritativeState((2.0, 2.0), before.current.W_A, None)
            before = replace(before, reset=reset)
            # A legitimate, equally charged reset root succeeds in one evaluation.
            reset_root = ci.CandidateCIRoot(replace(before, current=reset), backend)
            self.assertEqual(reset_root.evaluations, 1)
            with self.subTest(candidate=candidate):
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ci.ProvisionalCandidateCIStep(before, backend)
                self.assertEqual(caught.exception.stage, 'candidate_solve')
                self.assertEqual(caught.exception.code, 'no_admitted_root')

    def test_A_unknown_writer_policy_rejects_before_zero_or_positive_root(self):
        for dt in (0.0, 2.0 ** -14):
            before, backend = fixture('A', changes={
                'lifecycle': {'history_policy_id': 'audit_unknown_writer_policy_v1'},
            })
            before = replace(before, dt=dt)
            original = before.to_payload()
            with self.subTest(dt=dt), patch.object(
                ci, 'CandidateCIRoot', wraps=ci.CandidateCIRoot
            ) as calls:
                with self.assertRaises(ValueError):
                    ci.ProvisionalCandidateCIStep(before, backend)
                self.assertEqual(calls.call_count, 0)
            self.assertEqual(before.to_payload(), original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
