"""Fixed-precision Arb proof pressure, not production admission."""

from dataclasses import replace
import hashlib
import math
import time
import unittest
import importlib.util

if importlib.util.find_spec("flint") is None:
    raise unittest.SkipTest("python-flint is required for this explicit policy suite")

from unittest.mock import patch

import flint
from tests.models._grc_v4_research_sources import research_source_digest
from scripts import benchmark_grcv4_arb_policy as probe
from tests.models.test_grc_v4_os_pass_probe import before, compare_point
from pygrc.models import grc_v4_realizations as real
from pygrc.models import grc_v4_numerics as numerics
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_profile import SolverPolicy


def waiting_worker(connection):
    time.sleep(30)


def failed_worker(connection):
    connection.send(("error", {"type": "certificate_inconclusive", "message": "pressure"}))
    connection.close()


class ArbPolicyTests(unittest.TestCase):
    def test_retained_stage_success_does_not_claim_complete_os_pass(self):
        folder = probe.base.ROOT / "implementation/evidence/grcv4-performance"
        r = probe.base.read(folder / "arb_policy_os_pass_probe.json")
        self.assertEqual(r["record_digest"], probe.base.digest({k: v for k, v in r.items() if k != "record_digest"}))
        for name, expected in r["source_bindings"].items():
            self.assertEqual(research_source_digest(probe.base.ROOT, name), expected, name)
        old = probe.base.read(folder / "exact_policy_hodge_positive_probe.json")
        self.assertEqual(r["predecessor_record_digest"], old["record_digest"])
        self.assertEqual((r["policy"], r["arb_algorithm"], r["arb_precision_bits"]), (probe.POLICY, "lu", 256))
        self.assertEqual(r["predictor_routes"], probe.PREDICTOR_ROUTES)
        self.assertEqual(r["corrector_routes"], probe.CORRECTOR_ROUTES)
        self.assertEqual(r["flint_threads"], 1)
        for flag in ("fallback_attempted", "production_admission", "src_changed"):
            self.assertFalse(r[flag])
        self.assertEqual((r["native_steps"], r["native_events"]), (0, 0))
        self.assertEqual(r["outcome"], "resource_limit")
        self.assertEqual(r["deadline_seconds"], 300)
        self.assertNotIn("result", r)
        events = r["events"]
        self.assertEqual([e["stage"] for e in events if e.get("operation") == "native_current_completed"],
                         ["os_predictor", "os_corrector"])
        self.assertTrue(any(e["stage"] == "native_selector_path" and e.get("operation") == "completed"
                            for e in events))
        self.assertEqual((events[-1]["stage"], events[-1]["operation"]), ("native_split_admission", "started"))
        solves = [e for e in events if e.get("operation") == "solve"]
        self.assertEqual(len(solves), 14)
        for stage, routes in (("os_predictor", probe.PREDICTOR_ROUTES), ("os_corrector", probe.CORRECTOR_ROUTES)):
            calls = [e for e in solves if e["native_stage"] == stage]
            self.assertEqual(len(calls), 7)
            self.assertEqual({e["stage"]: e["method"] for e in calls}, routes)
        self.assertEqual(sum(e["method"] == probe.METHOD for e in solves), 8)
        for event in solves:
            self.assertTrue(event["rounded_residual_pass"])
            if event["method"] == probe.METHOD:
                self.assertEqual((event["algorithm"], event["precision_bits"]), ("lu", 256))
                self.assertTrue(event["input_coefficients_exact"] and event["solution_enclosed"]
                                and event["all_entries_uniquely_rounded"])
                self.assertEqual(event["entries_certified"], 400*event["rhs_columns"])
                self.assertFalse(event["exact_solution_materialized"] or event["fallback_attempted"])
            else:
                self.assertTrue(event["exact_identity"])
        # Check the current digest against the separately retained exact Dixon solution.
        current = next(e for e in solves if e["native_stage"] == "os_predictor" and e["stage"] == "physical current solve")
        exact = probe.base.read(folder / "direct_source_predictor_dixon.json")["result"]
        self.assertEqual(current["rounded_solution_digest"], probe.base.digest(exact["rounded_solution"]))

    def test_retained_large_structural_flat_reproduces_without_current_trajectory(self):
        from pygrc.models import grc_v4_geometry as geometry
        folder = probe.base.ROOT / "implementation/evidence/grcv4-performance"
        record = probe.base.read(folder / "arb_policy_os_pass_probe.json")
        saved = probe.base.read(folder / "exact_policy_predictor_probe.json")
        with exact_backend(ExactBackend.FLINT):
            inputs = probe.prior.materialize()
            ref = inputs.geometry.reference
            causal = geometry.OneForm(ref.graph, tuple(saved["result"]["causal_flat"]))
            star = probe.base.matrix(geometry.StarAssembly(causal).matrix)
            increment = probe.base.rounded(probe.base.q(ref.profile.params_resolved.candidate.zeta_C)*star)
            scaled = probe.base.q(ref.profile.params_resolved.geometry.kappa_H)*increment
            h = probe.base.rounded(probe.base.matrix(ref.pairings.one_form.matrix)+probe.base.rounded(scaled))
            declared = next(e for e in record["events"] if e.get("operation") == "certificate"
                            and e.get("affine_call") == 1 and e.get("role") == "represented_affine_hodge")
            self.assertEqual(probe.hodge.certificate(h.tolist()), declared["certificate"])
            identity = probe.prior.eye(h.nrows())
            rounded, proof = probe.certified_solve(h, identity)
            recorded = next(e for e in record["events"] if e.get("operation") == "solve"
                            and e["native_stage"] == "os_corrector" and e["stage"] == "structural flat map")
            self.assertEqual(proof["rounded_solution_digest"], recorded["rounded_solution_digest"])
            residual = h*rounded-identity
            solver = ref.profile.params_resolved.solver
            for j in range(h.nrows()):
                self.assertTrue(numerics.residual_pass(tuple(residual[i, j] for i in range(h.nrows())),
                                                      tuple(identity[i, j] for i in range(h.nrows())), solver))

    def test_rounding_cells_ties_zero_subnormal_extremes(self):
        q = probe.base.q
        for x in (q(1), q(1)+q(2)**-53, q(1)+3*q(2)**-53,
                  q(2)**-1075, -q(2)**-1075, 3*q(2)**-1075,
                  -3*q(2)**-1075, q(float.fromhex('0x1.fffffffffffffp+1023'))):
            expected = float(x)
            expected = 0. if expected == 0 else expected
            self.assertEqual(probe.round_interval(x, x).hex(), expected.hex())
        self.assertEqual(probe.round_interval(-q(2)**-1075, q(2)**-1075).hex(), 0.0.hex())
        midpoint = q(1)+q(2)**-53
        with self.assertRaises(probe.Inconclusive):
            probe.round_interval(midpoint-q(2)**-200, midpoint+q(2)**-200)
        with self.assertRaises(probe.Inconclusive):
            probe.round_interval(q(2)**1024, q(2)**1024)
        with self.assertRaises(ValueError):
            probe.round_interval(2, 1)
        # A wrong floating conversion proposal cannot bypass the exact rounding cell.
        with patch.object(probe, "float", return_value=1., create=True):
            with self.assertRaises(probe.Inconclusive):
                probe.round_interval(q(1)+q(2)**-51, q(1)+q(2)**-51)

    def test_multiple_rhs_pivoting_nonsymmetric_and_nearly_singular(self):
        for rows in ([[0, 1], [1, 2]], [[2, 1], [0, 3]], [[1, 1], [1, 1+2**-50]],
                     [[2**-500, 0], [0, 2**500]], [[3, 1, 0], [1, 4, 1], [0, 1, 5]]):
            a = probe.base.matrix(rows)
            b = probe.base.matrix([[i+1, 1-i] for i in range(a.nrows())])
            expected = probe.base.rounded(a.inv()*b)
            with self.subTest(rows=rows):
                actual, proof = probe.certified_solve(a, b)
                self.assertEqual(actual, expected)
                self.assertEqual(proof["entries_certified"], a.nrows()*b.ncols())
                self.assertTrue(proof["all_entries_uniquely_rounded"])
                self.assertFalse(proof["exact_solution_materialized"])

    def test_fixed_input_precision_singular_nonfinite_and_context_restoration(self):
        old = flint.ctx.prec
        with flint.ctx.workprec(80):
            for a, b in (([[1, 1], [1, 1]], [[1], [1]]),
                         ([[probe.base.q(1)+probe.base.q(2)**-300]], [[1]]),
                         ([[1]], [[probe.base.q('1/3')]])):
                with self.assertRaises(probe.Inconclusive):
                    probe.certified_solve(probe.base.matrix(a), probe.base.matrix(b))
                self.assertEqual(flint.ctx.prec, 80)
        self.assertEqual(flint.ctx.prec, old)
        for ball in (flint.arb('nan'), flint.arb('0 +/- 1')):
            with self.assertRaises(probe.Inconclusive):
                probe.rounded_balls(flint.arb_mat([[ball]]))
        with self.assertRaises(ValueError):
            probe.certified_solve(probe.base.matrix([[1, 2]]), probe.base.matrix([[1]]))

    def test_complete_small_pass_preserves_matrices_readback_split_and_path(self):
        for tau in (0, 1):
            with self.subTest(tau=tau), exact_backend(ExactBackend.FLINT):
                b = before(tau)
                expected = real.CandidateCOSPass(b)
                with patch.object(probe.base, "direct", side_effect=AssertionError("hidden exact fallback")), probe.installed() as p:
                    actual = real.CandidateCOSPass(b)
                compare_point(self, actual.predictor, expected.predictor)
                compare_point(self, actual.corrector, expected.corrector)
                self.assertEqual(actual.residual, expected.residual)
                self.assertEqual(actual.selector_path_segments, expected.selector_path_segments)
                calls = [e for e in p.events if e.get("operation") == "solve" and e["method"] == probe.METHOD]
                self.assertTrue(calls)
                for event in calls:
                    self.assertTrue(event["all_entries_uniquely_rounded"])
                    self.assertTrue(event["rounded_residual_pass"])
                    self.assertFalse(event["exact_solution_materialized"])

    def test_independent_condition_and_residual_failures_not_waived(self):
        with exact_backend(ExactBackend.FLINT):
            p = probe.ArbPredictorPolicy(replace(before(), stage="os_predictor"))
            declared = p.inputs.geometry.reference.profile.params_resolved.solver
            payload = declared.to_payload()
            payload.update(absolute_tolerance=1e-20, relative_tolerance=1e-20)
            strict = SolverPolicy.from_payload(payload)
            with self.assertRaisesRegex(numerics.MatrixError, "residual tolerance"):
                p.solve(((1.5,),), ((1.,),), strict, "physical current solve", [])
            with patch.object(probe.prior.near_identity, "certify", return_value={"outcome": "inconclusive"}), \
                 patch.object(probe, "certified_solve", side_effect=AssertionError("solve after failed condition")):
                with self.assertRaises(probe.Inconclusive):
                    p.solve(((1.,),), ((1.,),), declared, "physical current solve", [])
            with patch.object(probe, "certified_solve", side_effect=probe.Inconclusive("unresolved rounding")), \
                 patch.object(probe.base, "direct", side_effect=AssertionError("hidden fallback")):
                with self.assertRaisesRegex(probe.Inconclusive, "unresolved rounding"):
                    p.solve(((1.,),), ((1.,),), declared, "physical current solve", [])
            with self.assertRaises(ValueError):
                p.solve(((1.,),), ((1.,),), declared, "unknown", [])

    def test_native_split_failure_and_hook_restoration(self):
        original = (probe.prior.PredictorPolicy, probe.previous.CorrectorPolicy, numerics.solve)
        with exact_backend(ExactBackend.FLINT):
            b = before(tolerance=0)
            with self.assertRaises(real.OSStageError) as legacy:
                real.CandidateCOSPass(b)
            with self.assertRaises(real.OSStageError) as updated:
                with probe.installed():
                    real.CandidateCOSPass(b)
            self.assertEqual(str(updated.exception), str(legacy.exception))
        self.assertEqual(original, (probe.prior.PredictorPolicy, probe.previous.CorrectorPolicy, numerics.solve))

    def test_deadline_and_worker_failure_do_not_retry(self):
        capped = probe.supervised(.1, target=waiting_worker)
        self.assertEqual(capped["outcome"], "resource_limit")
        self.assertFalse(capped["fallback_attempted"])
        failed = probe.supervised(5, target=failed_worker)
        self.assertEqual(failed["outcome"], "failed")
        self.assertEqual(failed["error"]["type"], "certificate_inconclusive")
        self.assertFalse(failed["fallback_attempted"])


if __name__ == "__main__":
    unittest.main()
