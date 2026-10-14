"""Exact weighted OS admission pressure; not an all-profile runtime campaign."""

import hashlib
import math
import random
import time
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from tests.models._grc_v4_research_sources import research_source_digest
from unittest.mock import patch

from scripts import benchmark_grcv4_split_certificate as probe
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models import grc_v4_realizations as real
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Geometry, GRCV4Graph, OneFormHodge, OrientedEdge
from tests.models.test_grc_v4_candidate_c import current_fixture
from tests.models.test_grc_v4_os_pass_probe import before, compare_point


def native_decision(r, d, t):
    r, d, t = probe.base.matrix(r), probe.base.matrix(d), probe.base.q(t)
    return all(numerics.inertia(tuple(tuple(row) for row in (t*d+sign*r).tolist()))[0] == 0
               for sign in (-1, 1))


def pair(h1, h2, weights, tolerance=1.):
    graph = GRCV4Graph(("a", "b", "c"), (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")))
    ref = current_fixture(graph=graph, weights=dict(zip(("ab", "bc"), weights)),
                          changes={"realization": {"tolerance": tolerance}}).geometry.reference
    return tuple(GRCV4Geometry(ref, OneFormHodge(graph, h)) for h in (h1, h2))


def result_then_linger(connection):
    connection.send(("result", {"test_payload": "returned_before_teardown"}))
    time.sleep(10)


class WeightedSplitTests(unittest.TestCase):
    def test_retained_complete_pass_bindings_and_reconstructed_split_not_trajectory_rerun(self):
        from pygrc.models.grc_v4_geometry import OneForm, StarAssembly
        folder = probe.base.ROOT / "implementation/evidence/grcv4-performance"
        record = probe.base.read(folder / "weighted_split_os_pass_probe.json")
        self.assertEqual(record["record_digest"], probe.base.digest({k: v for k, v in record.items() if k != "record_digest"}))
        for name, expected in record["source_bindings"].items():
            self.assertEqual(research_source_digest(probe.base.ROOT, name), expected, name)
        old = probe.base.read(folder / "arb_policy_os_pass_probe.json")
        self.assertEqual(record["predecessor_record_digest"], old["record_digest"])
        self.assertEqual((record["policy"], record["split_method"]), (probe.POLICY, probe.METHOD))
        self.assertEqual((record["arb_precision_bits"], record["arb_algorithm"], record["flint_threads"]), (256, "lu", 1))
        self.assertEqual(record["outcome"], "completed")
        # The inherited supervisor permits only .1 s teardown after receiving
        # the complete result, then terminates the child. Do not misreport this
        # retained numerical completion as a clean process exit.
        self.assertEqual(record["worker_exitcode"], -15)
        self.assertLess(record["worker_wall_seconds"], record["deadline_seconds"])
        for flag in ("production_admission", "src_changed", "fallback_attempted"):
            self.assertFalse(record[flag])
        self.assertEqual((record["native_steps"], record["native_events"]), (0, 0))
        result = record["result"]
        for flag in ("complete_os_pass", "instrumented_numerical_policy", "split_admitted", "predictor_matches_prior_exact"):
            self.assertTrue(result[flag])
        self.assertGreater(result["selector_path_segments"], 0)
        operations = [{k: v for k, v in e.items() if k != "elapsed_seconds"} for e in record["events"]]
        self.assertEqual(operations, result["operations"])
        self.assertEqual((operations[-1]["stage"], operations[-1]["operation"]), ("weighted_split_admission", "completed"))
        self.assertFalse(any(e["stage"] == "native_split_admission" for e in operations))
        solves = [e for e in operations if e.get("operation") == "solve"]
        self.assertEqual(len(solves), 14)
        self.assertTrue(all(e["rounded_residual_pass"] for e in solves))
        for stage, routes in (("os_predictor", probe.arb.PREDICTOR_ROUTES), ("os_corrector", probe.arb.CORRECTOR_ROUTES)):
            self.assertEqual({e["stage"]: e["method"] for e in solves if e["native_stage"] == stage}, routes)
        def outputs(events):
            return {(e["native_stage"], e["stage"]): e["rounded_solution_digest"] for e in events
                    if e.get("operation") == "solve" and e["method"] == probe.arb.METHOD}
        self.assertEqual(outputs(operations), outputs(old["events"]))
        exact = probe.base.read(folder / "exact_policy_predictor_probe.json")["result"]
        for key in ("current", "baseline", "read_flux", "causal_flat", "current_block_digest", "closure_residual_squared"):
            self.assertEqual(result["predictor"][key], exact[key])
        # Reconstruct actual operands from retained stage output, not a rerun of
        # the costly current/selector trajectory or a reuse of the claimed bound.
        with exact_backend(ExactBackend.FLINT):
            ref = probe.arb.prior.materialize().geometry.reference
            reference = probe.base.matrix(ref.pairings.one_form.matrix)
            h = []
            for point in (result["predictor"], result["corrector"]):
                star = probe.base.matrix(StarAssembly(OneForm(ref.graph, tuple(point["causal_flat"]))).matrix)
                increment = probe.base.rounded(probe.base.q(ref.profile.params_resolved.candidate.zeta_C)*star)
                scaled = probe.base.rounded(probe.base.q(ref.profile.params_resolved.geometry.kappa_H)*increment)
                h.append(probe.base.rounded(reference+scaled))
            self.assertEqual(probe.base.digest([[float(x) for x in row] for row in h[0].tolist()]),
                             result["corrector"]["input_hodge_digest"])
            residual = h[0]-h[1]
            certified = probe.certificate(residual.tolist(), reference.tolist(), ref.profile.params_resolved.realization.tolerance)
        self.assertEqual(certified, operations[-1]["certificate"])
        self.assertEqual(certified["residual_digest"], result["split_exact_values_digest"])
        self.assertEqual(certified["outcome"], "certified")
        self.assertFalse(certified["inertia_computed"] or certified["fallback_attempted"])

    def test_completed_payload_is_distinct_from_clean_child_exit(self):
        r = probe.arb.supervised(5, target=result_then_linger)
        self.assertEqual(r["outcome"], "completed")
        self.assertEqual(r["result"], {"test_payload": "returned_before_teardown"})
        self.assertNotEqual(r["worker_exitcode"], 0)
        self.assertFalse(r["fallback_attempted"])

    def test_equality_adjacent_zero_subnormal_and_extreme_scales(self):
        q = probe.base.q
        with exact_backend(ExactBackend.FLINT):
            for scale in (q(1), q(2)**-1074, q(2)**1024):
                d = ((scale, 0), (0, 4*scale))
                for amount, expected in ((math.nextafter(.5, 0.), "certified"), (.5, "certified"),
                                         (math.nextafter(.5, math.inf), "inconclusive")):
                    r = ((q(amount)*scale, 0), (0, -4*q(amount)*scale))
                    proof = probe.certificate(r, d, .5)
                    self.assertEqual(proof["outcome"], expected)
                    self.assertEqual(native_decision(r, d, .5), expected == "certified")
            self.assertEqual(probe.certificate(((0,),), ((1,),), 0)["outcome"], "certified")
            tiny = q(2)**-1075
            self.assertEqual(float(tiny), 0.)
            self.assertEqual(probe.certificate(((tiny,),), ((1,),), 0)["outcome"], "inconclusive")
            self.assertFalse(native_decision(((tiny,),), ((1,),), 0))
            self.assertEqual(probe.certificate((), (), 0)["outcome"], "certified")

    def test_conservative_weighted_boundary_is_inconclusive_not_rejection(self):
        # True normalized norm is 1/2; row bound is 1. No silent inertia fallback.
        r, d = ((0, 1), (1, 0)), ((1, 0), (0, 4))
        with exact_backend(ExactBackend.FLINT):
            self.assertTrue(native_decision(r, d, .5))
        with patch.object(numerics, "inertia", side_effect=AssertionError("hidden inertia")):
            proof = probe.certificate(r, d, .5)
        self.assertEqual(proof["outcome"], "inconclusive")
        self.assertEqual(proof["weighted_row_bound"], "1")

    def test_weight_normalization_and_coordinate_covariance(self):
        r = ((2, .25, 0), (.25, -1, .5), (0, .5, .125))
        d = ((4, 0, 0), (0, 2, 0), (0, 0, .5))
        proof = probe.certificate(r, d, 2)
        self.assertEqual(proof["weighted_row_bound"], "5/4")
        self.assertEqual(proof["outcome"], "certified")
        permutation, signs = (2, 0, 1), (-1, 1, -1)
        rr = tuple(tuple(signs[i]*signs[j]*r[p][q] for j, q in enumerate(permutation))
                   for i, p in enumerate(permutation))
        dd = tuple(tuple(d[p][q] for q in permutation) for p in permutation)
        transformed = probe.certificate(rr, dd, 2)
        self.assertEqual(transformed["weighted_row_bound"], proof["weighted_row_bound"])
        # Raw ||R|| is too large, but the declared reference normalization admits it.
        self.assertEqual(probe.certificate(((2.,),), ((4.,),), .5)["outcome"], "certified")
        self.assertEqual(probe.certificate(((2.,),), ((1.,),), .5)["outcome"], "inconclusive")

    def test_seeded_symmetric_cases_against_exact_inertia(self):
        rng = random.Random(741)
        with exact_backend(ExactBackend.FLINT):
            for n in range(1, 7):
                for _ in range(5):
                    r = [[rng.randint(-16, 16)/16 for j in range(n)] for i in range(n)]
                    r = [[r[min(i,j)][max(i,j)] for j in range(n)] for i in range(n)]
                    weights = [2.**rng.randint(-3, 3) for _ in range(n)]
                    d = [[weights[i]*int(i == j) for j in range(n)] for i in range(n)]
                    bound = probe.base.q(probe.certificate(r, d, 0)["weighted_row_bound"])
                    for t in (bound, 2*bound):
                        self.assertEqual(probe.certificate(r, d, t)["outcome"], "certified")
                        self.assertTrue(native_decision(r, d, t))

    def test_malformed_and_wrong_reference_assumptions_fail(self):
        for r, d, t in ((((1, 2),), ((1,),), 1), (((1, 1), (0, 1)), ((1, 0), (0, 1)), 1),
                        (((1,),), ((0,),), 1), (((1,),), ((-1,),), 1),
                        (((1, 0), (0, 1)), ((2, 1), (1, 2)), 1),
                        (((float('nan'),),), ((1,),), 1), (((float('inf'),),), ((1,),), 1),
                        (((1,),), ((1,),), -1), (((1,),), ((1,),), float('nan')),
                        (((probe.base.q('1/3'),),), ((1,),), 1)):
            with self.subTest(r=r, d=d, t=t), self.assertRaises((ValueError, OverflowError)):
                probe.certificate(r, d, t)

    def test_typed_result_matches_native_including_overflow_display(self):
        with exact_backend(ExactBackend.FLINT):
            for h1, h2, weights, t in ((((2., .125), (.125, 3.)), ((1., 0.), (0., 2.)), (1, 4), 2),
                                      (((1., 0.), (0., 2.)), ((1., 0.), (0., 2.)), (2, 4), 0)):
                g, h = pair(h1, h2, weights, t)
                native = probe.NativeSplitResidual(g, h)
                with patch.object(numerics, "inertia", side_effect=AssertionError("hidden inertia")):
                    updated = probe.CertifiedSplitResidual(g, h)
                for name in ("geometry", "regenerated", "values", "exact_values", "admitted"):
                    self.assertEqual(getattr(updated, name), getattr(native, name))
            large = float.fromhex('0x1.fffffffffffffp+1023')
            g, h = pair(((large, .75*large), (.75*large, large)),
                        ((large, -.75*large), (-.75*large, large)), (2, 2), large)
            native, updated = probe.NativeSplitResidual(g, h), probe.CertifiedSplitResidual(g, h)
            self.assertTrue(native.admitted and updated.admitted)
            self.assertIsNone(updated.values)
            self.assertEqual(updated.exact_values, native.exact_values)

    def test_typed_domain_guards_and_inconclusive_no_fallback(self):
        with exact_backend(ExactBackend.FLINT):
            g, h = pair(((8., 1.), (1., 8.)), ((8., 0.), (0., 8.)), (1, 4), .5)
            self.assertTrue(probe.NativeSplitResidual(g, h).admitted)
            with patch.object(numerics, "inertia", side_effect=AssertionError("hidden inertia")):
                with self.assertRaises(probe.arb.Inconclusive):
                    probe.CertifiedSplitResidual(g, h)
            with self.assertRaises(TypeError):
                probe.CertifiedSplitResidual(object(), h)
            other = pair(((8., 0.), (0., 8.)), ((8., 0.), (0., 8.)), (2, 4), .5)[0]
            with self.assertRaisesRegex(ValueError, "foreign reference"):
                probe.CertifiedSplitResidual(g, other)
            b = current_fixture(realization="CI")
            with self.assertRaisesRegex(ValueError, "unimplemented OS split norm"):
                probe.CertifiedSplitResidual(b.geometry, b.geometry)

    def test_small_complete_pass_and_inconclusive_restore_hooks(self):
        original = (real.OSSplitResidual, probe.arb.hodge.HodgePositivePolicy, numerics.inertia)
        with exact_backend(ExactBackend.FLINT):
            for tau in (0, 1):
                b = before(tau)
                native = real.CandidateCOSPass(b)
                with probe.installed() as p:
                    updated = real.CandidateCOSPass(b)
                compare_point(self, updated.predictor, native.predictor)
                compare_point(self, updated.corrector, native.corrector)
                self.assertEqual(updated.selector_path_segments, native.selector_path_segments)
                for name in ("values", "exact_values", "admitted"):
                    self.assertEqual(getattr(updated.residual, name), getattr(native.residual, name))
                calls = [e for e in p.events if e["stage"] == "weighted_split_admission" and e["operation"] == "completed"]
                self.assertEqual(len(calls), 1)
            with self.assertRaises(probe.arb.Inconclusive), probe.installed():
                real.CandidateCOSPass(before(tolerance=0))
        self.assertEqual(original, (real.OSSplitResidual, probe.arb.hodge.HodgePositivePolicy, numerics.inertia))


if __name__ == "__main__":
    unittest.main()
