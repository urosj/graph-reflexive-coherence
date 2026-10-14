"""Exact positivity proof pressure, including represented-number boundaries."""

import hashlib
import math
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from tests.models._grc_v4_research_sources import research_source_digest
from unittest.mock import patch

from scripts import benchmark_grcv4_hodge_positive as probe
from tests.models.test_grc_v4_os_pass_probe import before, compare_point
from pygrc.models import grc_v4_geometry as geometry
from pygrc.models import grc_v4_realizations as real
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend


class PositiveCertificateTests(unittest.TestCase):
    def test_retained_integrity_keeps_completion_distinct_from_successful_subchecks(self):
        folder = probe.base.ROOT / "implementation/evidence/grcv4-performance"
        r = probe.base.read(folder / "exact_policy_hodge_positive_probe.json")
        self.assertEqual(r["record_digest"], probe.base.digest({k: v for k, v in r.items() if k != "record_digest"}))
        for name, expected in r["source_bindings"].items():
            self.assertEqual(research_source_digest(probe.base.ROOT, name), expected, name)
        old = probe.base.read(folder / "exact_policy_os_pass_probe.json")
        self.assertEqual(r["predecessor_record_digest"], old["record_digest"])
        self.assertEqual(r["policy"], probe.POLICY)
        self.assertEqual(r["positivity_method"], probe.METHOD)
        self.assertEqual(r["positivity_scale"], 1)
        self.assertEqual(r["predictor_routes"], probe.previous.prior.ROUTES)
        self.assertEqual(r["corrector_routes"], probe.previous.CORRECTOR_ROUTES)
        self.assertEqual(r["flint_threads"], 1)
        for flag in ("fallback_attempted", "production_admission", "src_changed"):
            self.assertFalse(r[flag])
        self.assertEqual((r["native_steps"], r["native_events"]), (0, 0))
        self.assertIn(r["outcome"], ("completed", "resource_limit"))
        if r["outcome"] == "completed":
            self.assertTrue(r["result"]["complete_os_pass"])
            self.assertTrue(r["result"]["split_admitted"])
        else:
            self.assertNotIn("result", r)
            self.assertEqual(r["deadline_seconds"], 300)
        self.assertTrue(any(e["stage"] == "native_source_geometry" and e.get("operation") == "completed"
                            for e in r["events"]))
        self.assertTrue(any(e["stage"] == "os_corrector" and e.get("operation") == "policy_setup_completed"
                            for e in r["events"]))

    def test_retained_affine_certificates_reconstruct_without_rerunning_currents(self):
        folder = probe.base.ROOT / "implementation/evidence/grcv4-performance"
        r = probe.base.read(folder / "exact_policy_hodge_positive_probe.json")
        saved = probe.base.read(folder / "exact_policy_predictor_probe.json")
        with exact_backend(ExactBackend.FLINT):
            inputs = probe.previous.prior.materialize()
            ref = inputs.geometry.reference
            causal = geometry.OneForm(ref.graph, tuple(saved["result"]["causal_flat"]))
            star = probe.base.matrix(geometry.StarAssembly(causal).matrix)
            increment = probe.base.rounded(probe.base.q(ref.profile.params_resolved.candidate.zeta_C)*star)
            scaled = probe.base.q(ref.profile.params_resolved.geometry.kappa_H)*increment
            reference = probe.base.matrix(ref.pairings.one_form.matrix)
            exact = reference+scaled
            represented = probe.base.rounded(reference+probe.base.rounded(scaled))
            certificates = [e for e in r["events"] if e.get("affine_call") == 1
                            and e.get("operation") == "certificate"
                            and e["role"] in ("unrounded_affine_hodge", "represented_affine_hodge")]
            self.assertEqual([e["role"] for e in certificates], ["unrounded_affine_hodge", "represented_affine_hodge"])
            for event, matrix in zip(certificates, (exact, represented), strict=True):
                self.assertEqual(event["certificate"], probe.certificate(matrix.tolist()))
            # This witness has genuinely different exact and represented matrices.
            self.assertNotEqual(certificates[0]["certificate"]["matrix_digest"], certificates[1]["certificate"]["matrix_digest"])

    def test_exact_bounds_against_native_elimination_and_independent_inertia(self):
        for rows in (((1.,),), ((1.125, -.0625), (-.0625, .875)),
                     ((1., -.125, .0625), (-.125, 1.25, 0.), (.0625, 0., .875))):
            for scale in (probe.base.q(1), probe.base.q(2)**-1074, probe.base.q(2)**1024):
                with self.subTest(rows=rows, scale=str(scale)), exact_backend(ExactBackend.FLINT):
                    a = scale*probe.base.matrix(rows)
                    r = probe.certificate(a.tolist(), scale)
                    self.assertEqual(r["outcome"], "certified")
                    self.assertEqual(r["arithmetic"], "flint_fmpq")
                    geometry._require_positive_definite(a.tolist())
                    lo, hi = map(probe.base.q, (r["eigenvalue_lower_bound"], r["eigenvalue_upper_bound"]))
                    for bound in (a-lo*probe.previous.prior.eye(a.nrows()), hi*probe.previous.prior.eye(a.nrows())-a):
                        self.assertEqual(numerics.inertia(tuple(tuple(row) for row in bound.tolist()))[0], 0)

    def test_strict_boundary_singular_indefinite_nonsymmetric_and_invalid(self):
        for off, outcome in ((math.nextafter(1., 0.), "certified"), (1., "inconclusive"),
                             (math.nextafter(1., math.inf), "inconclusive")):
            self.assertEqual(probe.certificate(((1., off), (off, 1.)))["outcome"], outcome)
        self.assertEqual(probe.certificate(((0.,),))["outcome"], "inconclusive")
        self.assertEqual(probe.certificate(((-1.,),))["outcome"], "inconclusive")
        with self.assertRaisesRegex(ValueError, "symmetry"):
            probe.certificate(((1., .125), (0., 1.)))
        for rows in (((1., 0.),), ((float("nan"),),), ((float("inf"),),), ((probe.base.q("1/3"),),)):
            with self.assertRaises((ValueError, OverflowError)):
                probe.certificate(rows)
        for scale in (0, -1):
            with self.assertRaises(ValueError):
                probe.certificate(((1.,),), scale)
        self.assertTrue(probe.certificate(())["empty_space"])

    def test_exact_and_represented_boundary_are_separate_and_no_fallback(self):
        # Positive exact dyadic matrix rounds to a singular binary64 matrix.
        off = 1-probe.base.q(2)**-55
        exact = ((probe.base.q(1), off), (off, probe.base.q(1)))
        self.assertEqual(probe.certificate(exact)["outcome"], "certified")
        rounded = tuple(tuple(float(x) for x in row) for row in exact)
        self.assertEqual(probe.certificate(rounded)["outcome"], "inconclusive")
        with self.assertRaises(geometry.GeometryDomainError):
            geometry._require_positive_definite(rounded)
        # This SPD matrix is outside the chosen scale=1 certificate. No elimination retry.
        geometry._require_positive_definite(((3.,),))
        p = probe.HodgePositivePolicy()
        with patch.object(geometry, "_require_positive_definite", side_effect=AssertionError("hidden elimination")):
            with self.assertRaises(probe.previous.prior.CertificateInconclusive):
                p.positive(((3.,),))

    def test_full_small_pass_matches_original_with_both_affine_roles(self):
        for tau in (0, 1):
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                b = before(tau)
                expected = real.CandidateCOSPass(b)
                p = probe.HodgePositivePolicy()
                with p.installed():
                    actual = real.CandidateCOSPass(b)
                compare_point(self, actual.predictor, expected.predictor)
                compare_point(self, actual.corrector, expected.corrector)
                self.assertEqual(actual.residual, expected.residual)
                self.assertEqual(actual.selector_path_segments, expected.selector_path_segments)
                for ordinal in (1, 2):
                    calls = [e for e in p.events if e.get("affine_call") == ordinal
                             and e.get("operation") == "certificate" and e["role"] != "reconstructed_or_retained_hodge"]
                    self.assertEqual([e["role"] for e in calls], ["unrounded_affine_hodge", "represented_affine_hodge"])
                    self.assertTrue(all(e["certificate"]["outcome"] == "certified" for e in calls))

    def test_failure_restores_hooks_and_does_not_relax_split_admission(self):
        original = (geometry.H_profile, geometry._require_positive_definite, real.H_profile, numerics.solve)
        with exact_backend(ExactBackend.FLINT):
            b = before(tolerance=0)
            with self.assertRaises(real.OSStageError) as legacy:
                real.CandidateCOSPass(b)
            with self.assertRaises(real.OSStageError) as updated:
                with probe.HodgePositivePolicy().installed():
                    real.CandidateCOSPass(b)
            self.assertEqual(str(updated.exception), str(legacy.exception))
        self.assertEqual(original, (geometry.H_profile, geometry._require_positive_definite, real.H_profile, numerics.solve))


if __name__ == "__main__":
    unittest.main()
