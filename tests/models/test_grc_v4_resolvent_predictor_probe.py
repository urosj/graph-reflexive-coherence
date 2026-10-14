"""Scientific and boundary pressure for the explicit predictor research policy."""

from dataclasses import replace
import hashlib
import math
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from tests.models._grc_v4_research_sources import research_source_digest
from unittest.mock import patch

from scripts import benchmark_grcv4_resolvent_predictor as probe
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from tests.models.test_grc_v4_candidate_c import current_fixture


def inputs(tau=1):
    graph = GRCV4Graph(("a", "b", "c"), (OrientedEdge("ab", "a", "b"),
                      OrientedEdge("bc", "b", "c"), OrientedEdge("ca", "c", "a")))
    p = probe.base.read(probe.base.ROOT / probe.base.DECLARATION)["source"]["profile"]["params_resolved"]["candidate"]
    p = {k: v for k, v in p.items() if k not in ("W_C_tr", "W_C_tr_content_digest")}
    p["tau_C"] = tau
    return replace(current_fixture(graph=graph, weights={e.edge_id: 1 for e in graph.oriented_edges},
        resource=(2.015625, 2., 1.984375), changes={"candidate": p}), stage="os_predictor")


class ResolventCertificateTests(unittest.TestCase):
    def test_actual_rounded_and_nonsymmetric_bounds_against_exact_gram_inertia(self):
        for b in (probe.base.matrix([[1, 0], [-1, 1], [0, -1]]),
                  probe.base.matrix([[1, 1, 0], [-1, -1, 0]])):
            for tau in (0, probe.base.q("1/10"), 16):
                h = probe.base.q("10000000000000003/10000000000000000")
                ideal = probe.eye(b.ncols()) + tau * h * b.transpose() * b
                for asymmetry in (0, probe.base.q("1/64")):
                    actual = probe.base.rounded(ideal)
                    actual[0, 1] += asymmetry
                    result = probe.resolvent_certificate(actual, b, tau, h, 10000)
                    self.assertEqual(result["outcome"], "certified")
                    lower, upper = map(probe.base.q, (result["singular_value_lower"], result["singular_value_upper"]))
                    gram = actual.transpose() * actual
                    with exact_backend(ExactBackend.FLINT):
                        for bound in (gram - lower**2 * probe.eye(b.ncols()), upper**2 * probe.eye(b.ncols()) - gram):
                            negative, _, _ = numerics.inertia(tuple(tuple(row) for row in bound.tolist()))
                            self.assertEqual(negative, 0)
                    if asymmetry:
                        self.assertGreater(probe.base.q(result["represented_error_norm2_upper"]), 0)

    def test_boundary_equality_inconclusive_and_invalid_inputs(self):
        b = probe.base.matrix([[1, 0], [0, 1]])
        exact = 2 * probe.eye(2)
        self.assertEqual(probe.resolvent_certificate(exact, b, 1, 1, 2)["outcome"], "certified")
        # Actual kappa=1, but the sufficient bound is 2: inability to certify is NOT rejection.
        below = probe.resolvent_certificate(exact, b, 1, 1, math.nextafter(2., 0.))
        self.assertEqual(below["outcome"], "inconclusive")
        self.assertEqual(probe.resolvent_certificate(probe.eye(2), b, 1, 1, 100)["outcome"], "inconclusive")
        self.assertEqual(probe.resolvent_certificate(probe.eye(2) * 0, b, 1, 1, 100)["outcome"], "inconclusive")
        for tau, h, limit in ((-1, 1, 10), (0, 0, 10), (0, -1, 10), (0, 1, .5)):
            with self.assertRaises(ValueError):
                probe.resolvent_certificate(exact, b, tau, h, limit)
        with self.assertRaises(ValueError):
            probe.resolvent_certificate(probe.eye(3), b, 1, 1, 10)

    def test_witness_and_rounding_perturbations_are_not_ignored(self):
        b = probe.base.matrix([[1, -1], [0, 1]])
        represented = probe.base.rounded(probe.eye(2) + probe.base.q("1/10") * b.transpose() * b)
        original = probe.resolvent_certificate(represented, b, 1, probe.base.q("1/10"), 100)
        self.assertGreater(probe.base.q(original["represented_error_norm2_upper"]), 0)
        # A false ideal witness cannot silently retain the original tight lower bound.
        wrong = probe.resolvent_certificate(represented, b, 1, 10, 100)
        self.assertEqual(wrong["outcome"], "inconclusive")


class PredictorPolicyTests(unittest.TestCase):
    def test_complete_small_predictor_equivalence_and_no_legacy_inverse(self):
        for tau in (0, 1):
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                before = inputs(tau)
                native = CandidateCCurrent(before)
                policy = probe.PredictorPolicy(before)
                with patch("pygrc.models._grc_v4_matrix.inverse", side_effect=AssertionError("hidden inverse")), \
                     patch("pygrc.models._grc_v4_matrix.condition_bound", side_effect=AssertionError("hidden legacy condition")), \
                     policy.installed():
                    actual = CandidateCCurrent(before)
                self.assertEqual(actual.current, native.current)
                self.assertEqual(actual.read, native.read)
                self.assertEqual(actual.closure_residual_squared, native.closure_residual_squared)
                for field in ("baseline", "retained_hodge", "potential", "generated_potential", "selector",
                              "response", "flux_response", "current_block", "flat_matrix", "inverse_identification"):
                    self.assertEqual(getattr(actual.algebra, field), getattr(native.algebra, field), field)
                self.assertTrue(any(r["stage"] == "discarded_regularity_inverse_guard" for r in policy.events))

    def test_unknown_roles_wrong_coefficients_and_solver_errors_do_not_fallback(self):
        with exact_backend(ExactBackend.FLINT):
            before = inputs()
            policy = probe.PredictorPolicy(before)
            declared = before.geometry.reference.profile.params_resolved.solver
            with self.assertRaises(probe.CertificateInconclusive):
                policy.inverse(((2., 0.), (0., 3.)))
            with self.assertRaises(ValueError):
                policy.solve(((1.,),), ((1.,),), declared, "unknown role", [])
            with self.assertRaises(ValueError):
                policy.solve(((1., 1.), (0., 1.)), ((1.,), (1.,)), declared, "structural flat map", [])
            with patch.object(probe.base, "direct", side_effect=ZeroDivisionError("injected direct failure")):
                with self.assertRaisesRegex(ZeroDivisionError, "injected"):
                    policy.solve(((1.,),), ((1.,),), declared, "physical current solve", [])
            with patch.object(probe.near_identity, "certify", return_value={"method": "pressure", "outcome": "inconclusive"}), \
                 patch.object(probe.base, "direct", side_effect=AssertionError("solve after failed certificate")):
                with self.assertRaises(probe.CertificateInconclusive):
                    policy.solve(((1.,),), ((1.,),), declared, "physical current solve", [])

    def test_instrumentation_is_restored_after_failure(self):
        original = (numerics.solve, numerics.inverse, numerics.condition)
        with exact_backend(ExactBackend.FLINT):
            policy = probe.PredictorPolicy(inputs())
            with self.assertRaises(RuntimeError):
                with policy.installed():
                    raise RuntimeError("pressure")
        self.assertEqual(original, (numerics.solve, numerics.inverse, numerics.condition))

    def test_retained_predictor_and_certificate_without_reexecuting_predictor(self):
        root = probe.base.ROOT
        folder = root / "implementation/evidence/grcv4-performance"
        records = []
        for name in ("resolvent_condition_probe.json", "exact_policy_predictor_probe.json"):
            r = probe.base.read(folder / name)
            self.assertEqual(r["record_digest"], probe.base.digest({k: v for k, v in r.items() if k != "record_digest"}))
            for path, expected in r["source_bindings"].items():
                self.assertEqual(research_source_digest(root, path), expected, path)
            self.assertEqual(r["outcome"], "completed")
            self.assertEqual(r["policy"], probe.POLICY)
            self.assertEqual(r["solve_routes"], probe.ROUTES)
            for flag in ("fallback_attempted", "production_admission", "src_changed", "complete_os_pass"):
                self.assertFalse(r[flag])
            self.assertEqual((r["native_steps"], r["native_events"]), (0, 0))
            records.append(r)
        result = records[1]["result"]
        self.assertTrue(result["predictor_completed"])
        self.assertTrue(result["instrumented_numerical_policy"])
        self.assertTrue(result["prior_block_baseline_and_rounded_current_match"])
        earlier = probe.base.read(folder / "direct_source_predictor_dixon.json")
        block, _, _ = probe.base.load_block(folder / "direct_source_predictor_block.json.xz")
        self.assertEqual(result["current"], [row[0] for row in earlier["result"]["rounded_solution"]])
        self.assertEqual(result["baseline"], [row[0] for row in block["rhs"]])
        self.assertEqual(result["current_block_digest"], probe.base.digest(block["matrix"]))
        params = probe.base.read(root / probe.base.DECLARATION)["source"]["profile"]["params_resolved"]
        residual = tuple(probe.base.q(j) - probe.base.q(j0) - probe.base.q(params["candidate"]["zeta_C"]) * probe.base.q(r)
            for j, j0, r in zip(result["current"], result["baseline"], result["read_flux"], strict=True))
        self.assertEqual(str(sum((x*x for x in residual), probe.base.q(0))), result["closure_residual_squared"])
        from pygrc.models.grc_v4_profile import SolverPolicy
        with exact_backend(ExactBackend.FLINT):
            self.assertTrue(numerics.residual_pass(residual, tuple(probe.base.q(x) for x in result["baseline"]),
                                                   SolverPolicy.from_payload(params["solver"])))
        solves = [r for r in result["operations"] if r.get("operation") == "solve"]
        self.assertEqual({r["stage"] for r in solves}, set(probe.ROUTES))
        for row in solves:
            self.assertTrue(row["exact_identity"])
            self.assertTrue(row["rounded_residual_pass"])
        resolvent = next(r["certificate"] for r in result["operations"]
                         if r["stage"] == "retained resolvent" and r.get("operation") == "condition")
        self.assertEqual(resolvent, records[0]["result"]["certificate"])


if __name__ == "__main__":
    unittest.main()
