"""Bounded exact-direct benchmark pressure, not production solver admission."""

from copy import deepcopy
import hashlib
import math
import time
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from tests.models._grc_v4_research_sources import research_source_digest

from flint import fmpq, fmpq_mat
from scripts import benchmark_grcv4_exact_direct as probe
from scripts import benchmark_grcv4_identity_condition as identity
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_profile import SolverPolicy


def waiting_worker(connection, job, algorithm, path):
    connection.send(("progress", {"stage": "test_waiting"}))
    time.sleep(30)


def failing_worker(connection, job, algorithm, path):
    connection.send(("error", {"type": "TestFailure", "message": "no retry"}))
    connection.close()


class ExactDirectProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = probe.read(probe.ROOT / probe.DECLARATION)["source"]["profile"]["params_resolved"]

    def test_exact_and_rounded_equality_multiple_rhs_and_pivoting(self):
        matrices = (
            [[0, 1], [1, 2]],  # indefinite, requires pivoting
            [[2, 1], [0, 3]],  # nonsymmetric
            [[1, 1], [1, 1 + 2**-50]],  # nearly singular, not singular
            [[2**-500, 0], [0, 2**500]],  # large scale separation
            [[3, 1, 0], [1, 4, 1], [0, 1, 5]],
        )
        for rows in matrices:
            a = probe.matrix(rows)
            b = probe.matrix([[i + 1, 1 - i] for i in range(a.nrows())])
            # Historical path, independently exercised only on small matrices.
            old = a.inv() * b
            for algorithm in probe.ALGORITHMS:
                with self.subTest(rows=rows, algorithm=algorithm):
                    x = probe.direct(a, b, algorithm)
                    probe.verify_exact(a, b, x)
                    self.assertEqual(x, old)
                    self.assertEqual(probe.rounded(x), probe.rounded(old))
                    corrupted = fmpq_mat(x)
                    corrupted[0, 0] += 1
                    with self.assertRaisesRegex(ValueError, "exact solve identity"):
                        probe.verify_exact(a, b, corrupted)

    def test_rounding_ties_subnormal_and_overflow(self):
        # Rational RHS can be exact dyadics beyond binary64 precision.
        a = probe.matrix([[2**53]])
        b = probe.matrix([[2**53 + 1, 2**53 + 3]])
        for algorithm in probe.ALGORITHMS:
            x = probe.rounded(probe.direct(a, b, algorithm))
            self.assertEqual(float(x[0, 0]), 1.0)
            self.assertEqual(float(x[0, 1]), 1.0 + 2**-51)
            tiny = probe.direct(probe.matrix([[2**500]]), probe.matrix([[2**-575]]), algorithm)
            self.assertEqual(tiny[0, 0], fmpq(1, 2**1075))
            self.assertEqual(float(probe.rounded(tiny)[0, 0]), 0.0)
        with self.assertRaises((ValueError, OverflowError)):
            probe.rounded(probe.matrix([[2**1024]]))

    def test_singular_invalid_and_missing_algorithm_fail_explicitly(self):
        for algorithm in probe.ALGORITHMS:
            with self.assertRaises(ZeroDivisionError):
                probe.direct(probe.matrix([[1, 1], [1, 1]]), probe.matrix([[1], [1]]), algorithm)
            with self.assertRaises(ValueError):
                probe.direct(probe.matrix([[1, 2]]), probe.matrix([[1]]), algorithm)
            with self.assertRaises(ValueError):
                probe.direct(probe.matrix([[1]]), fmpq_mat(1, 0), algorithm)
        for algorithm in (None, "auto", "inverse", "approx"):
            with self.assertRaises(ValueError):
                probe.direct(probe.matrix([[1]]), probe.matrix([[1]]), algorithm)

    def test_condition_boundary_separate_from_solve_success(self):
        with exact_backend(ExactBackend.FLINT):
            for value, admitted in ((2.0, True), (math.nextafter(2.0, math.inf), False)):
                a, b = probe.matrix([[1, 0], [0, value]]), probe.matrix([[1], [1]])
                probe.verify_exact(a, b, probe.direct(a, b, "dixon"))
                if admitted:
                    numerics.condition(((1., 0.), (0., value)), 2, "pressure")
                else:
                    with self.assertRaises(numerics.MatrixError):
                        numerics.condition(((1., 0.), (0., value)), 2, "pressure")

    def test_rounded_residual_can_fail_after_exact_solve(self):
        policy = deepcopy(self.params["solver"])
        policy.update(absolute_tolerance=1e-20, relative_tolerance=1e-20)
        policy = SolverPolicy.from_payload(policy)
        a, b = probe.matrix([[3]]), probe.matrix([[1]])
        x = probe.direct(a, b, "dixon")
        probe.verify_exact(a, b, x)
        r = a * probe.rounded(x) - b
        with exact_backend(ExactBackend.FLINT):
            self.assertFalse(numerics.residual_pass((r[0, 0],), (b[0, 0],), policy))

    def test_reconstruction_matches_native_block_and_baseline(self):
        from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
        from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
        from tests.models.test_grc_v4_candidate_c import current_fixture
        graph = GRCV4Graph(("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c"), OrientedEdge("ca", "c", "a")))
        resources = (2.015625, 2.0, 1.984375)
        params = {k: v for k, v in self.params["candidate"].items()
                  if k not in ("W_C_tr", "W_C_tr_content_digest")}
        for tau in (0, 1):
            params["tau_C"] = tau
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                inputs = current_fixture(graph=graph, weights={e.edge_id: 1 for e in graph.oriented_edges},
                                         resource=resources, changes={"candidate": params})
                native = CandidateCCurrent(inputs)
                block, rhs, _ = probe.predictor_block(probe.matrix(graph.incidence), resources, params, "dixon")
                self.assertEqual(block, probe.matrix(native.algebra.current_block))
                self.assertEqual(rhs, probe.matrix([[x] for x in native.algebra.baseline.values]))
                self.assertEqual(probe.rounded(probe.direct(block, rhs, "dixon")),
                                 probe.matrix([[x] for x in native.current.values]))

    def test_deadline_and_worker_failure_do_not_switch_methods(self):
        result = probe.supervised("solve", "dixon", None, .75, target=waiting_worker)
        self.assertEqual(result["outcome"], "resource_limit")
        self.assertFalse(result["fallback_attempted"])
        self.assertNotEqual(result["worker_exitcode"], 0)
        result = probe.supervised("solve", "dixon", None, 5, target=failing_worker)
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["error"]["type"], "TestFailure")
        self.assertFalse(result["fallback_attempted"])

    def test_identity_certificate_is_sufficient_not_a_rejection_oracle(self):
        for rows in ([[1, .125], [0, 1]], [[1, 0], [0, 1.5]]):
            a = probe.matrix(rows)
            result = identity.certify(a, 1, 3)
            self.assertEqual(result["outcome"], "certified")
            # Independent exact PSD checks of the asserted singular-value bounds.
            with exact_backend(ExactBackend.FLINT):
                gram = a.transpose() * a
                lo = probe.q(result["singular_value_lower"]) ** 2
                hi = probe.q(result["singular_value_upper"]) ** 2
                eye = probe.matrix([[1, 0], [0, 1]])
                for bound in (gram - lo * eye, hi * eye - gram):
                    negative, _, _ = numerics.inertia(tuple(tuple(r) for r in bound.tolist()))
                    self.assertEqual(negative, 0)
            moved = identity.certify(-7 * a, -7, 3)
            self.assertEqual(result["condition_upper_squared"], moved["condition_upper_squared"])
        at_limit = identity.certify(probe.matrix([[1, 0], [0, 1.5]]), 1, 3)
        self.assertEqual(at_limit["condition_upper_squared"], "9")
        below = identity.certify(probe.matrix([[1, 0], [0, 1.5]]), 1, math.nextafter(3., 0.))
        self.assertEqual(below["outcome"], "inconclusive")
        for rows in ([[0, 0], [0, 1]], [[0, 1], [1, 0]]):
            # Singular and perfectly conditioned matrices can both be outside this certificate domain.
            self.assertEqual(identity.certify(probe.matrix(rows), 1, 100)["outcome"], "inconclusive")
        with self.assertRaises(ValueError):
            identity.certify(probe.matrix([[1]]), 0, 1)

    def test_retained_probe_bindings_and_certificate_without_resolving(self):
        base = probe.ROOT / "implementation/evidence/grcv4-performance"
        value, a, b = probe.load_block(base / "direct_source_predictor_block.json.xz")
        reports = {}
        for name in ("prepare", "dixon", "condition", "identity_condition"):
            r = probe.read(base / f"direct_source_predictor_{name}.json")
            self.assertEqual(r["record_digest"], probe.digest({k: v for k, v in r.items() if k != "record_digest"}))
            for path, expected in r["source_bindings"].items():
                self.assertEqual(research_source_digest(probe.ROOT, path), expected, path)
            self.assertFalse(r["production_admission"])
            self.assertFalse(r["fallback_attempted"])
            if r["outcome"] == "completed":
                self.assertEqual(r["result"]["block_digest"], value["block_digest"])
            reports[name] = r
        saved = reports["dixon"]["result"]
        self.assertTrue(saved["exact_identity"])
        self.assertTrue(saved["rounded_residual_pass"])
        r = a * probe.matrix(saved["rounded_solution"]) - b
        with exact_backend(ExactBackend.FLINT):
            self.assertTrue(numerics.residual_pass(tuple(r[i, 0] for i in range(r.nrows())),
                tuple(b[i, 0] for i in range(b.nrows())), SolverPolicy.from_payload(value["policy"])))
        cert = reports["identity_condition"]["result"]["certificate"]
        self.assertEqual(cert, identity.certify(a, 1, value["policy"]["conditioning_limit"]))
        self.assertEqual(cert["outcome"], "certified")
        self.assertEqual(reports["condition"]["outcome"], "resource_limit")


if __name__ == "__main__":
    unittest.main()
