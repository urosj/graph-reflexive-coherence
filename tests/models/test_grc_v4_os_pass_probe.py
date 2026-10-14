"""Bounded generated-geometry correctness and explicit-failure pressure."""

from dataclasses import replace
import hashlib
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from tests.models._grc_v4_research_sources import research_source_digest
from unittest.mock import patch

from scripts import benchmark_grcv4_os_pass as probe
from tests.models.test_grc_v4_resolvent_predictor_probe import inputs
from tests.models.test_grc_v4_candidate_c import current_fixture
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models import grc_v4_realizations as real
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend


def before(tau=1, *, tolerance=1e-8):
    seed = inputs(tau)
    p = seed.geometry.reference.profile.params_resolved.candidate.to_payload()
    p = {k: v for k, v in p.items() if k not in ("W_C_tr", "W_C_tr_content_digest")}
    graph = seed.geometry.reference.graph
    return current_fixture(graph=graph, weights={e.edge_id: 1 for e in graph.oriented_edges},
                           resource=seed.current.C,
                           changes={"candidate": p, "realization": {"tolerance": tolerance}})


def compare_point(test, actual, expected):
    test.assertEqual(actual.current, expected.current)
    test.assertEqual(actual.read, expected.read)
    test.assertEqual(actual.closure_residual_squared, expected.closure_residual_squared)
    for field in ("baseline", "retained_hodge", "potential", "generated_potential", "selector",
                  "identification", "inverse_identification", "flat_matrix", "physical_identification",
                  "laplacian", "response", "flux_response", "current_block"):
        test.assertEqual(getattr(actual.algebra, field), getattr(expected.algebra, field), field)


class OSPassPolicyTests(unittest.TestCase):
    def test_retained_bounded_attempt_integrity_not_native_reexecution(self):
        r = probe.base.read(probe.base.ROOT / "implementation/evidence/grcv4-performance/exact_policy_os_pass_probe.json")
        self.assertEqual(r["record_digest"], probe.base.digest({k: v for k, v in r.items() if k != "record_digest"}))
        for path, expected in r["source_bindings"].items():
            self.assertEqual(research_source_digest(probe.base.ROOT, path), expected, path)
        self.assertEqual(r["policy"], probe.POLICY)
        self.assertEqual(r["predictor_routes"], probe.prior.ROUTES)
        self.assertEqual(r["corrector_routes"], probe.CORRECTOR_ROUTES)
        self.assertFalse(r["fallback_attempted"])
        self.assertFalse(r["production_admission"])
        self.assertFalse(r["src_changed"])
        self.assertEqual((r["native_steps"], r["native_events"]), (0, 0))
        # This record preserves the capped attempt, not a synthetic successful pass.
        self.assertEqual(r["outcome"], "resource_limit")
        self.assertNotIn("result", r)
        self.assertEqual(r["deadline_seconds"], 300)
        events = r["events"]
        self.assertEqual([e["stage"] for e in events if e.get("operation") == "native_current_completed"], ["os_predictor"])
        self.assertEqual((events[-1]["stage"], events[-1]["operation"]), ("native_source_geometry", "started"))
        solves = [e for e in events if e.get("operation") == "solve"]
        self.assertEqual({e["stage"] for e in solves}, set(probe.prior.ROUTES))
        self.assertTrue(all(e["exact_identity"] and e["rounded_residual_pass"] for e in solves))

    def test_complete_pass_bitwise_equivalence_including_native_split_and_path(self):
        for tau in (0, 1):
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                b = before(tau)
                native = real.CandidateCOSPass(b)
                policy = probe.OSPassPolicy()
                with policy.installed():
                    actual = real.CandidateCOSPass(b)
                compare_point(self, actual.predictor, native.predictor)
                compare_point(self, actual.corrector, native.corrector)
                self.assertEqual(actual.residual, native.residual)
                self.assertEqual(actual.selector_path_segments, native.selector_path_segments)
                self.assertEqual(policy.stages, ["os_predictor", "os_corrector"])
                h = actual.corrector.inputs.geometry.one_form_hodge.matrix
                self.assertTrue(any(x for i, row in enumerate(h) for j, x in enumerate(row) if i != j))
                certificates = [r["certificate"] for r in policy.events if r.get("native_stage") == "os_corrector"
                                and r["stage"] == "retained resolvent" and r.get("operation") == "condition"]
                self.assertEqual(len(certificates), 1)
                if tau:
                    self.assertGreater(probe.base.q(certificates[0]["represented_error_norm2_upper"]), 0)

    def test_materially_nondiagonal_corrector_exact_legacy_equivalence_without_inverse_fallback(self):
        from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
        for tau in (0, 1):
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                b = before(tau)
                ref = b.geometry.reference
                h = ((1.125, -.0625, 0.), (-.0625, 1.0625, -.03125), (0., -.03125, 1.))
                b = replace(b, geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, h)), stage="os_corrector")
                expected = CandidateCCurrent(b)
                policy = probe.CorrectorPolicy(b)
                with patch("pygrc.models._grc_v4_matrix.inverse", side_effect=AssertionError("hidden inverse")), \
                     patch("pygrc.models._grc_v4_matrix.condition_bound", side_effect=AssertionError("hidden condition")), \
                     policy.installed():
                    actual = CandidateCCurrent(b)
                compare_point(self, actual, expected)
                self.assertTrue(any(r.get("method") == "positive_hodge_similarity" for r in policy.events))
                # Independently verify the nonsymmetric regularity block has no kernel.
                self.assertNotEqual(policy.regularity.det(), 0)

    def test_valid_native_geometry_can_exceed_sufficient_certificate_domain(self):
        from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
        with exact_backend(ExactBackend.FLINT):
            b = before()
            ref = b.geometry.reference
            h = ((1.25, -.125, 0.), (-.125, 1.125, -.0625), (0., -.0625, 1.))
            b = replace(b, geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, h)), stage="os_corrector")
            CandidateCCurrent(b)  # Native acceptance does not imply our sufficient bound will resolve.
            with self.assertRaisesRegex(probe.prior.CertificateInconclusive, "retained resolvent"):
                with probe.CorrectorPolicy(b).installed():
                    CandidateCCurrent(b)

    def test_native_split_failure_preserved_and_hooks_restored(self):
        with exact_backend(ExactBackend.FLINT):
            b = before(tolerance=0)
            with self.assertRaises(real.OSStageError) as legacy:
                real.CandidateCOSPass(b)
            original = (real.CandidateCCurrent, real.OSSplitResidual, numerics.solve, numerics.inverse, numerics.condition)
            with self.assertRaises(real.OSStageError) as actual:
                with probe.OSPassPolicy().installed():
                    real.CandidateCOSPass(b)
            self.assertEqual(str(actual.exception), str(legacy.exception))
            self.assertEqual(original, (real.CandidateCCurrent, real.OSSplitResidual, numerics.solve,
                                       numerics.inverse, numerics.condition))

    def test_wrong_stage_matrix_unknown_role_and_no_fallback(self):
        with exact_backend(ExactBackend.FLINT):
            b = before()
            with self.assertRaises(ValueError):
                probe.CorrectorPolicy(b)
            p = probe.CorrectorPolicy(replace(b, stage="os_corrector"))
            solver = b.geometry.reference.profile.params_resolved.solver
            with self.assertRaises(probe.prior.CertificateInconclusive):
                p.inverse(((2., 0.), (0., 3.)))
            with self.assertRaises(probe.prior.CertificateInconclusive):
                p.condition(((1.,),), 100, "unknown")
            with self.assertRaises(ValueError):
                p.solve(((1.,),), ((1.,),), solver, "unknown", [])
            with patch.object(probe.base, "direct", side_effect=ZeroDivisionError("injected exact solve failure")):
                with self.assertRaisesRegex(ZeroDivisionError, "injected"):
                    p.solve(((1.,),), ((1.,),), solver, "physical current solve", [])
            with patch.object(probe.prior.near_identity, "certify", return_value={"outcome": "inconclusive"}), \
                 patch.object(probe.base, "direct", side_effect=AssertionError("solve after failed proof")):
                with self.assertRaises(probe.prior.CertificateInconclusive):
                    p.solve(((1.,),), ((1.,),), solver, "physical current solve", [])


if __name__ == "__main__":
    unittest.main()
