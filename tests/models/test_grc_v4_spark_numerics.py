"""Exact representation, independent equations and fail-closed spark bridge tests."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
import p991a2_native_spark_numerics as evidence

from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_profile import GRCV4Profile
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from pygrc.models.grc_v4_certification import CertificationInconclusive
from pygrc.models.grc_v4_spark_state import (
    ExactResources, QuarticCOSProfile, QuarticSite, rational, round_flux, FLUX_BITS,
)
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel, _reference_facts


class SparkRepresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared, cls.graph, cls.states, cls.domain = evidence.subjects()

    def test_site_exact_polynomial_derivatives_and_units(self):
        site = QuarticSite(c0="5/2", a="3/2", mu="7/3")
        x, c, a, mu = map(Fraction, ("9/4", site.c0, site.a, site.mu))
        z = x-c
        self.assertEqual(tuple(map(str, site.evaluate(str(x)))), tuple(map(str, (
            mu*(z*z-a*a)**2/4, mu*(z*z*z-a*a*z), mu*(3*z*z-a*a)))))
        for change in (dict(a="0"), dict(c0="1"), dict(mu="-1"), dict(units_id="foreign")):
            with self.subTest(change=change), self.assertRaises(ValueError):
                QuarticSite(**change)
        with self.assertRaises(ValueError):
            site.evaluate("-1")

    def test_rational_wire_never_coerces_or_loses_precision(self):
        for bad in (1, 1.0, True, "1.0", "1/1", "2/4", "-0", "01", " 1", "1/0", "1e-20"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                rational(bad)
        q = "1208925819614629174706177/1208925819614629174706176"
        self.assertEqual(str(rational(q)), q)
        self.assertNotEqual(Fraction(float(rational(q))), Fraction(q))

    def test_closed_profile_successor_identity_and_old_decoder(self):
        p = evidence.profile(self.graph)
        self.assertNotEqual(p.complete_profile_id, p.baseline.complete_profile_id)
        self.assertNotEqual(replace(p, site=QuarticSite(mu="2")).complete_profile_id, p.complete_profile_id)
        restored = QuarticCOSProfile.from_canonical_bytes(p.to_canonical_bytes())
        self.assertEqual(restored, p); self.assertEqual(hash(restored), hash(p))
        old = p.baseline.to_canonical_bytes()
        self.assertEqual(GRCV4Profile.from_canonical_bytes(old).to_canonical_bytes(), old)
        with self.assertRaises(ValueError):
            GRCV4Profile.from_canonical_bytes(p.to_canonical_bytes())
        for path, value in ((["extra"], 1), (["complete_profile_id"], p.baseline.complete_profile_id),
                            (["params_resolved", "charge", "repair_policy"], "adjust_last_node"),
                            (["params_resolved", "candidate", "site_binding", "mu"], "2"),
                            (["params_resolved", "candidate", "site_binding", "unknown"], "1")):
            data = p.to_payload(); dest = data
            for key in path[:-1]: dest = dest[key]
            dest[path[-1]] = value
            with self.subTest(path=path), self.assertRaises((ValueError, KeyError)):
                QuarticCOSProfile.from_payload(data)

    def test_exact_state_roundtrip_and_charge_counterexample(self):
        state = self.states["current"]
        self.assertEqual(ExactResources.from_canonical_bytes(state.to_canonical_bytes()), state)
        self.assertEqual(sum(map(Fraction, state.C)), 21)
        with self.assertRaises(ValueError):
            replace(state, C=tuple(str(Fraction(float(Fraction(x)))) for x in state.C))
        data = state.to_payload(); data["C"][0] = "0"
        self.assertEqual(state, self.states["current"])
        with self.assertRaises(FrozenInstanceError):
            state.charge = "20"
        with self.assertRaises(ValueError):
            ExactResources.from_canonical_bytes(canonical_json_bytes(dict(state.to_payload(), extra=1)))
        g = GRCV4Graph(("a", "b"), (OrientedEdge("e", "a", "b"),))
        small = ExactResources(g, ("1", "2"), "3")
        malformed = small.to_payload(); malformed["C"] = "12"
        with self.assertRaises(ValueError):
            ExactResources.from_canonical_bytes(canonical_json_bytes(malformed))
        with self.assertRaises(TypeError): ExactResources(g, "12", "3")
        with self.assertRaises(TypeError): small.advance("0", "1")
        with self.assertRaises(TypeError): small.transfer(g, ("10", "01"))
        after = small.advance((str(Fraction(1, 2**53)),), "1")
        self.assertEqual(tuple(map(Fraction, after.C)), (1-Fraction(1,2**53), 2+Fraction(1,2**53)))

    def test_flux_nearest_even_signed_ties_and_fraction_oracle(self):
        from flint import fmpq
        scale = 1 << FLUX_BITS
        for value in [Fraction(n, 2*scale) for n in range(-9, 10)] + [Fraction(17,31), Fraction(-71,199)]:
            actual = round_flux(fmpq(str(value)))
            self.assertEqual(Fraction(str(actual)), Fraction(round(value*scale), scale))
            self.assertLessEqual(abs(Fraction(str(actual))-value), Fraction(1,2*scale))
            self.assertEqual(round_flux(-fmpq(str(value))), -actual)
        with self.assertRaises(TypeError): round_flux(0.5)

    def test_exact_allocation_rejects_nonconservative_and_negative_maps(self):
        target, matrix = evidence.transfer(self.states["reset"], 1)
        self.assertEqual(sum(map(Fraction, target.C)), 21)
        for value in ("-1", "1/2"):
            broken = [list(row) for row in matrix]; broken[0][0] = value
            with self.assertRaises(ValueError): self.states["reset"].transfer(target.graph, broken)
        with self.assertRaises(ValueError): self.states["reset"].transfer(target.graph, matrix[:-1])

    def test_exact_diagnostics_and_strict_ties(self):
        evidence.row_oracle(self.states["current"])
        uniform = replace(self.states["current"], C=("7/4",)*12)
        rows = uniform.spatial_diagnostics(sign=-1, gradient="4", hessian="1/4", contrast="1/2", core_resource="1/2")
        self.assertTrue(all(not r["seed"] and not r["anchor"] and r["evaluation_error"] == "0" for r in rows))
        self.assertEqual(uniform.edge_orders(-1), (0,)*13)
        with self.assertRaises(ValueError): uniform.spatial_diagnostics(sign=True, gradient="4", hessian="1/4", contrast="1/2", core_resource="1/2")


class SparkNativeMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.graph, cls.states, cls.domain = evidence.subjects()
        cls.kernel = SparkCOSKernel(cls.graph, evidence.profile(cls.graph))
        cls.source = cls.kernel.step(cls.states["current"])

    def test_literal_full_similarity_and_arb_source_equations(self):
        evidence.oracle(self.source, literal=True)

    def test_declared_policy_stays_flint_and_restores_outer_context(self):
        from pygrc.models import grc_v4_numerics as numerics
        original = numerics.inverse; observed = []
        def inverse(a):
            observed.append(current_exact_backend())
            return original(a)
        with exact_backend(ExactBackend.PYTHON), patch.object(numerics, "inverse", inverse):
            self.kernel.step(self.states["current"])
            self.assertIs(current_exact_backend(), ExactBackend.PYTHON)
        self.assertTrue(observed and all(x is ExactBackend.FLINT for x in observed))

    def test_reference_cache_fresh_changing_states_and_immutable_keys(self):
        target, _ = evidence.transfer(self.source.after, 1)
        warm = SparkCOSKernel(target.graph, evidence.profile(target.graph))
        a = warm.step(target); b = warm.step(a.after)
        self.assertNotEqual(a.exact_current, b.exact_current)
        hits = warm.cache_info()["hits"]
        same = SparkCOSKernel(target.graph, evidence.profile(target.graph))
        self.assertGreater(same.cache_info()["hits"], hits)
        _reference_facts.cache_clear()
        cold = SparkCOSKernel(target.graph, evidence.profile(target.graph))
        self.assertEqual(cold.step(a.after), b)
        with self.assertRaises(FrozenInstanceError): warm.graph = self.graph
        with self.assertRaises(ValueError): warm.step(self.states["current"])

    def test_unsupported_bindings_and_inconclusive_bounds(self):
        for changes in (dict(candidate=dict(eta_C=1/512)), dict(identity=dict(solver_id="unknown")),
                        dict(geometry=dict(star_cover_id="unknown")), dict(realization=dict(split_residual_norm_id="unknown")),
                        dict(common=dict(normalization_id="unknown"))):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                SparkCOSKernel(self.graph, evidence.profile(self.graph, **changes))
        weak = SparkCOSKernel(self.graph, evidence.profile(self.graph, solver=dict(conditioning_limit=1)))
        with self.assertRaises(CertificationInconclusive): weak.step(self.states["current"])
        with self.assertRaises(ValueError): self.kernel.step(self.states["current"], "8")

    def test_generated_geometry_cannot_be_dropped(self):
        from pygrc.models.grc_v4_spark_cos import _matrix
        with patch.object(SparkCOSKernel, "_geometry", lambda owner, flat: _matrix(owner._I)):
            wrong = self.kernel.step(self.states["current"])
        self.assertNotEqual(wrong.exact_current, self.source.exact_current)
        self.assertNotEqual(wrong.after, self.source.after)

    def test_orientation_covariance_including_quantized_flux(self):
        data = self.graph.to_payload()
        for edge in data["edges"]:
            edge["tail"], edge["head"] = edge["head"], edge["tail"]
        reversed_graph = GRCV4Graph.from_payload(data)
        kernel = SparkCOSKernel(reversed_graph, evidence.profile(reversed_graph))
        reverse = kernel.step(replace(self.states["current"], graph=reversed_graph))
        self.assertEqual(reverse.after.C, self.source.after.C)
        self.assertEqual(tuple(map(rational, reverse.flux)), tuple(-rational(x) for x in self.source.flux))

    def test_uniform_full_map_budget_below_real_margin(self):
        result = evidence.domain_budget(self.domain)
        self.assertLess(Fraction(result["full_step_error"]), Fraction(result["image_margin"]))
        self.assertEqual(result["spatial_evaluation_error"], "0")
        self.assertFalse(result["completion_admitted"])
        altered = deepcopy(self.domain); altered["axis_radii"][0] = "0"
        with self.assertRaises(ValueError): evidence.domain_budget(altered)


if __name__ == "__main__": unittest.main()
