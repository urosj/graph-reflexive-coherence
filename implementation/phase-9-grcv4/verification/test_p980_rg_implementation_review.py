"""Pressure the actual RG numerical owner; independent of native runtime gates."""

import copy
import json
import math
import unittest
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import test_p980_rg2b_numerical as rn
from mpmath.ctx_mp import MPContext
from test_p980_os_effect_witness import IV, endpoint, full_error, number, vector


class RGImplementationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rn.RGNumericalTests.setUpClass()
        cls.owner = rn.RGNumericalTests()
        cls.source, cls.target = cls.owner.source, cls.owner.target
        cls.cases = {}
        cls.report = {}
        for candidate in ("A", "C"):
            c, w = cls.owner.initial(candidate, "reset")
            c, w = cls.owner.event(c, w)
            chain = rn.section(cls.target, candidate, c, w)[3]
            cls.cases[candidate] = (c, w, chain)

    def operands(self, candidate):
        c, w, chain = self.cases[candidate]
        return c.copy(), None if w is None else w.copy(), copy.deepcopy(chain)

    def test_full_read_output_corruption_rejected(self):
        for candidate in ("A", "C"):
            for field, mode in (
                ("J", "small_error"),
                ("baseline", "wrong_value"),
                ("baseline", "short"),
                ("source", "wrong_value"),
                ("source", "nan"),
                ("source", "short"),
            ):
                c, w, chain = self.operands(candidate)
                original = self.target.read

                def bad_read(
                    *args, field=field, mode=mode, original=original, **kwargs
                ):
                    result = original(*args, **kwargs)
                    if mode == "short":
                        result[field] = result[field][:-1]
                    else:
                        result[field].flat[-1] += (
                            2**-35
                            if mode == "small_error"
                            else math.nan
                            if mode == "nan"
                            else 1
                        )
                    return result

                with (
                    self.subTest(candidate=candidate, field=field, mode=mode),
                    patch.object(rn, "solve_chain", return_value=chain),
                    patch.object(self.target, "read", side_effect=bad_read),
                    self.assertRaises(ValueError),
                ):
                    rn.ordinary(self.target, candidate, c, w)

    def test_read_private_scratch_preserves_entry_and_geometry(self):
        for candidate in ("A", "C"):
            c, w, chain = self.operands(candidate)
            saved_c, saved_w = c.copy(), None if w is None else w.copy()
            original = self.target.read

            def scratch(family, cc, ww, hh, original=original):
                result = original(family, cc, ww, hh)
                cc[:] = 0
                if ww is not None:
                    ww[:] = 0
                hh[:] = 0
                return result

            with (
                self.subTest(candidate=candidate),
                patch.object(rn, "solve_chain", return_value=chain),
                patch.object(self.target, "read", side_effect=scratch),
            ):
                _, _, stage = rn.ordinary(self.target, candidate, c, w)
                self.assertTrue(np.array_equal(c, saved_c))
                if w is not None:
                    self.assertTrue(np.array_equal(w, saved_w))
                self.assertTrue(np.array_equal(stage["H"], chain.h[0]))
                self.assertTrue(np.all(np.diag(stage["H"]) > 0.99))

    def test_writer_private_scratch_preserves_entry_and_outputs(self):
        c, w, chain = self.operands("A")
        saved = w.copy()
        original = rn.staged_write

        def scratch(model, cc, ww, jj):
            result = original(model, cc, ww, jj)
            ww[:] = 0
            jj[:] = 100
            return result

        with (
            patch.object(rn, "solve_chain", return_value=chain),
            patch.object(rn, "staged_write", side_effect=scratch),
        ):
            _, _, stage = rn.ordinary(self.target, "A", c, w)
        self.assertTrue(np.array_equal(w, saved))
        self.assertLess(
            full_error(stage["read"]["J"], stage["exact_read"]["J"]), Q(1, 2**40)
        )

    def test_requested_depth_cannot_be_substituted(self):
        for candidate in ("A", "C"):
            c, w, _ = self.operands(candidate)
            deeper = rn.section(
                self.target, candidate, c, w, depth=rn.DEPTH[candidate] + 1
            )[3]
            with (
                self.subTest(candidate=candidate),
                patch.object(rn, "solve_chain", return_value=deeper),
                self.assertRaisesRegex(ValueError, "depth"),
            ):
                rn.section(self.target, candidate, c, w)

    def test_intended_input_cannot_admit_invalid_represented_resource(self):
        for candidate in ("A", "C"):
            c, w, _ = self.operands(candidate)
            ci, wi = vector(c), None if w is None else vector(w)
            c[self.target.index["core"]] = -(2**-45)
            with (
                self.subTest(candidate=candidate),
                self.assertRaisesRegex(ValueError, "physical.*resource"),
            ):
                rn.ordinary(self.target, candidate, c, w, exact_c=ci, exact_w=wi)

    def test_every_chain_depth_and_malformed_certificate(self):
        checked = 0
        for candidate in ("A", "C"):
            c, w, good = self.operands(candidate)
            query = rn.rg.state(candidate, vector(c), None if w is None else vector(w))
            high = rn.rg.auxiliary(self.target)
            for i in range(len(good.x)):
                for field in ("x", "h"):
                    chain = copy.deepcopy(good)
                    getattr(chain, field)[i].flat[-1] += 2**-15
                    with self.subTest(candidate=candidate, field=field, depth=i), self.assertRaises(ValueError):
                        rn.certify_chain(high, candidate, chain, query)
                    checked += 1
            for mode in (
                "empty",
                "too_long",
                "nonfinite",
                "wrong_shape",
                "unsupported_H",
            ):
                chain = copy.deepcopy(good)
                if mode == "empty":
                    chain.x = []
                elif mode == "too_long":
                    chain.x += [chain.x[-1]] * 9
                elif mode == "nonfinite":
                    chain.x[1][-1] = math.inf
                elif mode == "wrong_shape":
                    chain.x[1] = chain.x[1].reshape(-1, 1)
                else:
                    i, j = np.argwhere(self.target.mask == 0)[0]
                    chain.h[0][i, j] = chain.h[0][j, i] = np.nextafter(0.0, 1.0)
                with self.subTest(candidate=candidate, mode=mode), self.assertRaises(ValueError):
                    rn.certify_chain(high, candidate, chain, query)
                checked += 1
        self.report["chain_rejections"] = checked

    def test_input_shapes_domains_and_consumed_model_binding(self):
        checked = 0
        for candidate in ("A", "C"):
            c, w, _ = self.operands(candidate)
            for mode in ("nan", "inf", "shape", "dtype", "negative", "upper_face"):
                cc = c.copy()
                if mode in ("nan", "inf"):
                    cc[-1] = math.nan if mode == "nan" else math.inf
                elif mode == "shape":
                    cc = cc.reshape(-1, 1)
                elif mode == "dtype":
                    cc = cc.astype(np.float32)
                elif mode == "negative":
                    cc[0] = -np.nextafter(0.0, 1.0)
                else:
                    cc[-1] = 4
                with self.subTest(candidate=candidate, mode=mode), self.assertRaises(ValueError):
                    rn.ordinary(self.target, candidate, cc, w)
                checked += 1
            for mode in ("shape", "infinite"):
                ci = vector(c[:-1]) if mode == "shape" else vector(c)
                if mode == "infinite":
                    ci[0] = IV.mpf([0, "inf"])
                with self.subTest(candidate=candidate, exact=mode), self.assertRaises(ValueError):
                    rn.section(self.target, candidate, c, w, exact_c=ci)
                checked += 1
            for field in ("B", "D", "I", "mask", "index", "params"):
                model = copy.deepcopy(self.target)
                if field == "index":
                    model.index[model.nodes[0]] = 1
                elif field == "params":
                    model.params = replace(model.params, chi_a=2 * model.params.chi_a)
                else:
                    getattr(model, field).flat[-1] += 0.25
                with self.subTest(candidate=candidate, field=field), self.assertRaisesRegex(ValueError, "binding"):
                    rn.section(model, candidate, c, w)
                checked += 1
        c, w, _ = self.operands("A")
        for value in (0, -1, math.nan, math.inf, math.exp(1 / 512)):
            bad = w.copy()
            bad[-1] = value
            with self.subTest(history=value), self.assertRaises(ValueError):
                rn.ordinary(self.target, "A", c, bad)
            checked += 1
        self.report["input_and_model_rejections"] = checked

    def test_point_and_intended_certificates_are_separate(self):
        for candidate in ("A", "C"):
            c, w, chain = self.operands(candidate)
            ci = vector(c)
            ci[self.target.index["outside-9"]] += number(Q(1, 2**48))
            wi = None if w is None else vector(w)
            # A point operand deliberately lies outside this intended interval.
            self.assertLess(
                Q(float(c[self.target.index["outside-9"]])),
                endpoint(ci[self.target.index["outside-9"]], 0),
            )
            with patch.object(rn, "solve_chain", return_value=chain):
                after, wn, stage = rn.ordinary(
                    self.target, candidate, c, w, exact_c=ci, exact_w=wi
                )
            self.assertLess(stage["resource_error"], rn.RESOURCE_ERROR_LIMIT)
            self.assertGreater(
                stage["certificate"]["input_error"],
                stage["point_certificate"]["input_error"],
            )
            exact = rn.rg.state(candidate, ci, wi)
            self.assertEqual(
                stage["certificate"]["input_error"],
                rn.rg.SECTION_LIP * full_error(chain.x[0], exact),
            )
            self.assertLess(full_error(after, stage["exact_after"]), Q(1, 2**38))
            if wn is not None:
                self.assertLess(full_error(wn, stage["exact_history"]), Q(1, 2**46))
        self.report["intended_exact_excludes_point_controls"] = 2

    def test_equilibria_clamp_faces_and_outliers(self):
        cases = []
        for candidate in ("A", "C"):
            for model_name, model in (("source", self.source), ("target", self.target)):
                for level in (0.0, 3.0):
                    c = np.full(len(model.nodes), level)
                    w = np.ones(len(model.edges)) if candidate == "A" else None
                    after, _, stage = rn.ordinary(model, candidate, c, w)
                    self.assertTrue(np.array_equal(stage["H"], model.I))
                    self.assertTrue(np.all(stage["read"]["J"] == 0))
                    self.assertTrue(np.array_equal(after, c))
                    cases.append(f"{candidate}_{model_name}_equilibrium_{level}")
            for level in (-1.0, 5.0):
                n, m = len(self.target.nodes), len(self.target.edges)
                query = np.array(
                    [level] * n
                    + (
                        [1.0 if i % 2 else -1.0 for i in range(m)]
                        if candidate == "A"
                        else []
                    )
                )
                chain = rn.solve_chain(
                    self.target, candidate, query, rn.DEPTH[candidate]
                )
                rn.certify_chain(
                    rn.rg.auxiliary(self.target), candidate, chain, vector(query)
                )
                cases.append(f"{candidate}_clamp_face_{level}")
            n, m = len(self.target.nodes), len(self.target.edges)
            for magnitude in (1e16, 1e100, np.finfo(float).max):
                query = np.array(
                    [
                        magnitude if i % 2 else -magnitude
                        for i in range(n + (m if candidate == "A" else 0))
                    ]
                )
                with np.errstate(over="ignore", invalid="ignore"):
                    chain = rn.solve_chain(
                        self.target, candidate, query, rn.DEPTH[candidate]
                    )
                    with self.assertRaises(ValueError):
                        rn.certify_chain(
                            rn.rg.auxiliary(self.target),
                            candidate,
                            chain,
                            vector(query),
                        )
                cases.append(f"{candidate}_outlier_rejected_{magnitude}")
        self.report["equilibria_boundary_outlier_controls"] = cases

    def test_independent_90_digit_equations_and_refinement(self):
        reports = {}
        for candidate in ("A", "C"):
            for kind in ("physical", "exterior"):
                c, w, chain = self.operands(candidate)
                if kind == "physical":
                    query_i = rn.rg.state(
                        candidate, vector(c), None if w is None else vector(w)
                    )
                else:
                    n, m = len(self.target.nodes), len(self.target.edges)
                    query = np.array(
                        [-0.9 if i % 2 else 5.2 for i in range(n)]
                        + (
                            [1.2 if i % 2 else -1.2 for i in range(m)]
                            if candidate == "A"
                            else []
                        )
                    )
                    query_i = vector(query)
                    chain = rn.solve_chain(
                        self.target, candidate, query, rn.DEPTH[candidate]
                    )
                high = rn.rg.auxiliary(self.target)
                hi, cert = rn.certify_chain(high, candidate, chain, query_i)
                oracle = DecimalEquations(self.target)
                mp = oracle.mp
                exact_query = mp.matrix(
                    [oracle.q((endpoint(v, 0) + endpoint(v, 1)) / 2) for v in query_i]
                )
                x = [mp.matrix(list(v)) for v in chain.x]
                h = [mp.matrix(v.tolist()) for v in chain.h]
                checked = 0
                rx = rh = mp.mpf(0)
                for i in range(1, len(x)):
                    inc, source = oracle.increment(candidate, x[i], h[i])
                    literal_inc, literal_source = high.increment(
                        candidate, vector(chain.x[i]), IV.matrix(chain.h[i].tolist())
                    )
                    checked += oracle.enclosed(self, inc, literal_inc)
                    checked += oracle.enclosed(self, source, literal_source)
                    rx = max(rx, oracle.norm(x[i] + inc - x[i - 1]))
                    rh = max(rh, oracle.norm(h[i - 1] - oracle.eye - source / 2))
                self.assertLessEqual(rx, oracle.q(cert["state_residual"]))
                self.assertLessEqual(rh, oracle.q(cert["geometry_residual"]))
                # Refine the actual returned chain with a separately written law.
                x[0] = exact_query
                for _ in range(16):
                    for i in range(1, len(x)):
                        inc, _ = oracle.increment(candidate, x[i], h[i])
                        x[i] = x[i - 1] - inc
                    for i in range(len(x) - 1, 0, -1):
                        _, source = oracle.increment(candidate, x[i], h[i])
                        h[i - 1] = oracle.eye + source / 2
                residual = mp.mpf(0)
                for i in range(1, len(x)):
                    inc, source = oracle.increment(candidate, x[i], h[i])
                    residual = max(
                        residual,
                        oracle.norm(x[i] + inc - x[i - 1]),
                        oracle.norm(h[i - 1] - oracle.eye - source / 2),
                    )
                self.assertLess(residual, mp.mpf("1e-28"))
                checked += oracle.enclosed(self, h[0], hi)
                if kind == "physical":
                    cc = mp.matrix(list(c))
                    ww = None if w is None else mp.matrix(list(w))
                    j, baseline, source = oracle.read(candidate, cc, ww, h[0])
                    literal = high.read(
                        candidate, vector(c), None if w is None else vector(w), hi
                    )
                    for actual, key in (
                        (j, "J"),
                        (baseline, "baseline"),
                        (source, "source"),
                    ):
                        checked += oracle.enclosed(self, actual, literal[key])
                reports[candidate + "_" + kind] = {
                    "enclosed_entries": checked,
                    "original_state_residual": float(rx),
                    "original_geometry_residual": float(rh),
                    "refined_max_residual": float(residual),
                }
        self.report["independent_90_digit"] = reports


class DecimalEquations:
    """Separate matrix/row/constitutive assembly; no production or interval calls."""

    def __init__(self, model):
        self.mp = MPContext()
        self.mp.dps = 90
        mp = self.mp
        self.nodes, self.edges = model.nodes, copy.deepcopy(model.edges)
        self.index = {v: i for i, v in enumerate(self.nodes)}
        n, m = len(self.nodes), len(self.edges)
        self.B, self.mask, self.eye = mp.matrix(n, m), mp.matrix(m, m), mp.eye(m)
        ends = [{e["tail"]["node_id"], e["head"]["node_id"]} for e in self.edges]
        for k, e in enumerate(self.edges):
            self.B[self.index[e["tail"]["node_id"]], k] = 1
            self.B[self.index[e["head"]["node_id"]], k] = -1
            for j in range(m):
                self.mask[k, j] = (
                    1 if j == k else mp.mpf("0.5") if ends[k] & ends[j] else 0
                )
        self.D = self.B.T * self.B
        self.d = mp.mpf(1) / 4096

    def q(self, value):
        return self.mp.mpf(value.numerator) / value.denominator

    def norm(self, matrix):
        return max(
            sum(abs(matrix[i, j]) for j in range(matrix.cols))
            for i in range(matrix.rows)
        )

    def enclosed(self, test, values, intervals):
        test.assertEqual((values.rows, values.cols), (intervals.rows, intervals.cols))
        for i in range(values.rows):
            for j in range(values.cols):
                test.assertGreaterEqual(
                    values[i, j], self.q(endpoint(intervals[i, j], 0))
                )
                test.assertLessEqual(values[i, j], self.q(endpoint(intervals[i, j], 1)))
        return values.rows * values.cols

    def conductance(self, c, w, j):
        mp = self.mp
        rows = [[mp.mpf(0) for _ in range(3)] for _ in self.nodes]
        for node in self.nodes:
            for row in range(3):
                numerator = denominator = mp.mpf(0)
                for k, e in enumerate(self.edges):
                    for side, other in (("tail", "head"), ("head", "tail")):
                        if (
                            e[side]["node_id"] == node
                            and (e[side]["port"] - 1) // 3 == row
                        ):
                            numerator += w[k] * (
                                c[self.index[e[other]["node_id"]]] - c[self.index[node]]
                            )
                            denominator += w[k]
                rows[self.index[node]][row] = (
                    numerator / denominator if denominator else mp.mpf(0)
                )
        out = []
        for k, e in enumerate(self.edges):
            u, v = self.index[e["tail"]["node_id"]], self.index[e["head"]["node_id"]]
            contrast = sum((rows[u][a] - rows[v][a]) ** 2 for a in range(3))
            out.append(mp.exp(-(c[u] + c[v] + contrast + j[k] ** 2) / 2**25))
        return mp.matrix(out)

    def read(self, candidate, c, w, h):
        mp = self.mp
        b = self.B.T * c
        if candidate == "A":
            mobility = mp.diag(list(w))
            baseline = (
                -mobility
                * self.B.T
                * (self.B * mobility * b + self.B * (h - self.eye) * b / 2)
            )
            drive = self.conductance(c, w, baseline)
            q = mp.matrix([(x - y) / (x + y) for x, y in zip(w, drive)])
            j = mp.matrix([baseline[i] / (1 - q[i] / 32) for i in range(len(w))])
            causal = mp.matrix([q[i] * j[i] / 16 for i in range(len(w))])
            zeta = mp.mpf("0.5")
        else:
            t = mp.exp(mp.tanh(sum(c) / len(c)) / 2**24)
            baseline = -self.D * t * h * b
            # Full physical/retained similarity: Q=H^-1 on the constant sector.
            q = h**-1
            retained = (self.eye + t * self.D * h) ** -1
            response = (q**-1) * retained * q
            j = (self.eye - response / 2**33) ** -1 * baseline
            causal = 16 * response * j
            zeta = mp.mpf(1) / 2**37
        flat = (h**-1) * causal
        source = mp.matrix(
            [
                [zeta * self.mask[i, k] * flat[i] * flat[k] for k in range(len(flat))]
                for i in range(len(flat))
            ]
        )
        return j, baseline, source

    def increment(self, candidate, x, h):
        mp = self.mp
        n = len(self.nodes)
        c = mp.matrix([max(mp.mpf(-1), min(mp.mpf(5), v)) for v in list(x)[:n]])
        y = (
            mp.matrix([max(mp.mpf(-1), min(mp.mpf(1), v)) for v in list(x)[n:]])
            if candidate == "A"
            else None
        )
        w = mp.matrix([mp.exp(v / 512) for v in y]) if y is not None else None
        j, _, source = self.read(candidate, c, w, h)
        dc = -self.d * self.B * j
        if w is None:
            return dc, source
        drive = self.conductance(c + dc, w, j)
        dy = [-mp.expm1(-self.d) * (512 * mp.log(g) - v) for g, v in zip(drive, y)]
        return mp.matrix(list(dc) + dy), source


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(json.dumps(RGImplementationReviewTests.report, indent=2))
    sys.exit(not result.result.wasSuccessful())
