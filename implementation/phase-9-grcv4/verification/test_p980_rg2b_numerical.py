"""Represented nine-port RG section research, independent of native backends.

Finite graph-transform iterates are evaluated as a backward chain. Complete
interval residuals certify the returned chain; accepted global bounds supply
its inverse error and the tail to the invariant section. No physical-tube
assumption is made about any backward state. See P9-8.0-RG2bNumericalFeasibility.md.
"""

import json
import math
import unittest
from dataclasses import dataclass
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import test_p980_rg2b_completion as rg
from test_p980_os_effect_witness import (
    HISTORY_OFFSET,
    IV,
    PARAMS,
    IntervalRows,
    bounds,
    endpoint,
    full_error,
    infinity,
    number,
    separation,
    staged_write,
    upper_abs,
    vector,
)
from test_p980_os_numerical_feasibility import StagedRows, product

DEPTH = {"A": 4, "C": 6}
SWEEPS = 18
SECTION_ERROR_LIMIT = Q(1, 2**48)
RESOURCE_ERROR_LIMIT = Q(1, 2**40)
HISTORY_ERROR_LIMIT = Q(1, 2**48)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_array(value, shape):
    a = np.asarray(value)
    require(
        a.shape == shape and a.dtype == np.dtype("float64") and np.all(np.isfinite(a)),
        "invalid represented shape/type/value",
    )
    return a


class RepresentedAuxiliary(StagedRows):
    def read(
        self, candidate, c, w, h, *, geometry=True, feedback=True, modulation=True
    ):
        """Binary64 NumPy linear algebra, certified a posteriori in full.

        This RG research arithmetic is separately selected; it does not change
        the OS checker's pure-Python binary64 LU recipe or inherit its margins.
        """
        chi = float(PARAMS.chi_a if candidate == "A" else PARAMS.chi_c)
        zeta = float(PARAMS.zeta_a if candidate == "A" else PARAMS.zeta_c)
        b = self.B.T @ c
        if candidate == "A":
            phi = self.B @ (w * b)
            if geometry:
                phi += float(bounds.KAPPA_AH) * (self.B @ ((h - self.I) @ b))
            baseline = -w * (self.B.T @ phi)
            drive = self.conductance(c, w, baseline)
            q = (w - drive) / (w + drive)
            j = baseline / (1 - zeta * chi * q) if feedback else baseline
            causal = chi * q * j if feedback else np.zeros_like(j)
        else:
            t = (
                math.exp(float(bounds.KAPPA_M) * math.tanh(math.fsum(c) / len(c)))
                if modulation
                else 1.0
            )
            baseline = -self.D @ (t * (h if geometry else self.I) @ b)
            response = np.linalg.solve(self.I + t * (h @ self.D), self.I)
            j = (
                np.linalg.solve(self.I - zeta * chi * response, baseline)
                if feedback
                else baseline
            )
            causal = chi * (response @ j) if feedback else np.zeros_like(j)
        flat = np.linalg.solve(h, causal)
        source = zeta * self.mask * np.outer(flat, flat)
        return {"J": j, "baseline": baseline, "source": source}

    def increment(self, candidate, x, h):
        """Argument-only global completion, in binary64 C/scaled-log-W."""
        n = len(self.nodes)
        c = np.clip(x[:n], float(rg.C_LOW), float(rg.C_HIGH))
        y = (
            np.clip(x[n:], float(rg.Y_LOW), float(rg.Y_HIGH))
            if candidate == "A"
            else None
        )
        w = np.array([math.exp(float(z) / 512) for z in y]) if y is not None else None
        read = self.read(candidate, c, w, h)
        dc = -float(bounds.DT) * product(self.B, read["J"])
        if y is None:
            return dc, read["source"]
        drive = self.conductance(c + dc, w, read["J"])
        decay = math.exp(-float(bounds.DT))
        dy = np.array(
            [
                (1 - decay) * (512 * math.log(float(g)) - float(z))
                for g, z in zip(drive, y, strict=True)
            ]
        )
        return np.concatenate((dc, dy)), read["source"]


@dataclass
class Chain:
    # x[0] is the query; h[-1]=I is the frozen Gamma_0 terminal section.
    x: list
    h: list


def solve_chain(model, candidate, query, depth):
    require(
        candidate in DEPTH and type(depth) is int and 1 <= depth <= 8,
        "invalid candidate/depth",
    )
    size = len(model.nodes) + (len(model.edges) if candidate == "A" else 0)
    query = finite_array(query, (size,))
    x = [query.copy() for _ in range(depth + 1)]
    h = [model.I.copy() for _ in range(depth + 1)]
    for _ in range(SWEEPS):
        for i in range(1, depth + 1):
            increment, _ = model.increment(candidate, x[i], h[i])
            x[i] = x[i - 1] - increment
        for i in range(depth, 0, -1):
            _, source = model.increment(candidate, x[i], h[i])
            h[i - 1] = model.I + float(bounds.KAPPA_H) * source
    return Chain(x, h)


def chain_error_bounds(candidate, depth, state_residual, geometry_residual):
    """Exact residual-to-chain bounds, including coupling at every depth."""
    require(
        candidate in DEPTH and type(depth) is int and 1 <= depth <= 8,
        "invalid candidate/depth",
    )
    rx, rh = Q(state_residual), Q(geometry_residual)
    require(rx >= 0 and rh >= 0, "negative residual bound")
    b = rg.global_bounds(candidate)
    kh = bounds.KAPPA_H
    amplification = sum((1 - b["A_X"]) ** (-i) for i in range(1, depth + 1))
    denominator = 1 - kh * b["B_H"] - kh * b["B_X"] * amplification * b["A_H"]
    require(denominator > 0, "chain residual coupling unresolved")
    eh = (rh + kh * b["B_X"] * amplification * rx) / denominator
    ex = amplification * (rx + b["A_H"] * eh)
    section = rg.section_budgets(b)
    tail = section["q_section"] ** depth * section["value_radius"]
    return {
        "state_error": ex,
        "geometry_error": eh,
        "truncation_error": tail,
        "propagation_error": kh * (b["B_X"] * ex + b["B_H"] * eh),
        "denominator": denominator,
    }


def certify_chain(model, candidate, chain, exact_query):
    """Recompute all residual coordinates; never trust producer error scalars.

    The frozen retraction is independently assembled here, rather than calling
    the represented increment or the interval producer's clipping helper.
    """
    require(
        candidate in DEPTH and model.params == PARAMS, "candidate/parameter binding"
    )
    n, m = len(model.nodes), len(model.edges)
    size = n + (m if candidate == "A" else 0)
    depth = len(chain.x) - 1
    require(1 <= depth <= 8 and len(chain.h) == depth + 1, "incomplete chain")
    require(exact_query.rows == size and exact_query.cols == 1, "incomplete query")
    # Local graph hypotheses of the accepted global estimates.
    require(
        n <= 17
        and m == n - 1
        and infinity(model.B) <= rg.DEGREE
        and infinity(model.D) <= rg.EDGE_GRAM
        and infinity(IV.matrix(model.mask.tolist())) <= rg.MASK_NORM,
        "graph bound hypotheses",
    )
    adjacency = {u: set() for u in model.nodes}
    for edge in model.edges:
        u, v = edge["tail"]["node_id"], edge["head"]["node_id"]
        adjacency[u].add(v)
        adjacency[v].add(u)
    reached = {model.nodes[0]}
    for _ in model.nodes:
        reached |= {v for u in tuple(reached) for v in adjacency[u]}
    require(len(reached) == n, "graph must be connected")
    for x in chain.x:
        finite_array(x, (size,))
    for h in chain.h:
        finite_array(h, (m, m))
        require(np.array_equal(h, h.T), "geometry must be symmetric")
        require(np.all(h[model.mask == 0] == 0), "geometry must be star-supported")
        require(
            infinity(IV.matrix(h.tolist()) - model.I) <= rg.RHO,
            "represented geometry outside global ball",
        )
    require(np.array_equal(chain.h[-1], np.eye(m)), "terminal section must be identity")
    query_error = full_error(chain.x[0], exact_query)
    rx, rh, first_image = Q(0), Q(0), None
    for i in range(1, depth + 1):
        # This explicit clipping is independent of both increment() methods.
        projected = [min(rg.C_HIGH, max(rg.C_LOW, Q(float(z)))) for z in chain.x[i][:n]]
        if candidate == "A":
            projected += [
                min(rg.Y_HIGH, max(rg.Y_LOW, Q(float(z)))) for z in chain.x[i][n:]
            ]
        increment, source = rg.literal_signed_increment(
            model, candidate, vector(projected), IV.matrix(chain.h[i].tolist())
        )
        rx = max(rx, infinity(vector(chain.x[i]) + increment - vector(chain.x[i - 1])))
        image = model.I + number(bounds.KAPPA_H) * source
        rh = max(rh, infinity(IV.matrix(chain.h[i - 1].tolist()) - image))
        if i == 1:
            first_image = image
    certificate = chain_error_bounds(candidate, depth, rx, rh)
    input_error = rg.SECTION_LIP * query_error
    total = (
        certificate["geometry_error"] + certificate["truncation_error"] + input_error
    )
    require(total < SECTION_ERROR_LIMIT, "section error budget unresolved")
    # Anchor on interval-evaluated G at the first predecessor. Publication
    # rounding in H0 is already measured by its residual; avoid turning it
    # into a fictitious independent rounding error on every off-diagonal.
    pad = (
        certificate["propagation_error"] + certificate["truncation_error"] + input_error
    )
    enclosure = IV.matrix(m, m)
    for i in range(m):
        for j in range(m):
            v = first_image[i, j]
            enclosure[i, j] = (
                IV.mpf([(v - number(pad)).a, (v + number(pad)).b])
                if model.mask[i, j]
                else number(0)
            )
    certificate.update(
        state_residual=rx,
        geometry_residual=rh,
        input_error=input_error,
        total_error=total,
        depth=depth,
    )
    return enclosure, certificate


def section(model, candidate, c, w=None, *, exact_c=None, exact_w=None, depth=None):
    n, m = len(model.nodes), len(model.edges)
    c = finite_array(c, (n,))
    require(candidate in DEPTH, "unknown candidate")
    if candidate == "A":
        w = finite_array(w, (m,))
        require(np.all(w > 0), "history must be positive")
    else:
        require(w is None and exact_w is None, "C has no history state")
    query = (
        np.concatenate((c, [512 * math.log(float(z)) for z in w]))
        if candidate == "A"
        else c.copy()
    )
    exact_c = vector(c) if exact_c is None else exact_c
    exact_w = vector(w) if candidate == "A" and exact_w is None else exact_w
    exact_query = rg.state(candidate, exact_c, exact_w)
    chain = solve_chain(
        model, candidate, query, DEPTH[candidate] if depth is None else depth
    )
    enclosure, certificate = certify_chain(
        rg.auxiliary(model), candidate, chain, exact_query
    )
    return chain.h[0], enclosure, certificate, chain


def ordinary(model, candidate, c, w=None, *, exact_c=None, exact_w=None):
    h, hi, certificate, chain = section(
        model, candidate, c, w, exact_c=exact_c, exact_w=exact_w
    )
    high = IntervalRows(model)
    ci = vector(c) if exact_c is None else exact_c
    wi = (vector(w) if exact_w is None else exact_w) if candidate == "A" else None
    require(
        all(0 <= endpoint(z, 0) <= endpoint(z, 1) < 4 for z in ci),
        "physical query outside resource agreement chart",
    )
    if wi is not None:
        require(
            all(
                Q(-5, 8)
                < endpoint(number(rg.SCALE) * IV.ln(z), 0)
                <= endpoint(number(rg.SCALE) * IV.ln(z), 1)
                < Q(5, 8)
                for z in wi
            ),
            "physical query outside history agreement chart",
        )
    read, exact_read = model.read(candidate, c, w, h), high.read(candidate, ci, wi, hi)
    after = c - float(bounds.DT) * product(model.B, read["J"])
    after_i = ci - number(bounds.DT) * high.B * exact_read["J"]
    wn = staged_write(model, after, w, read["J"]) if candidate == "A" else None
    wn_i = high.write(after_i, wi, exact_read["J"]) if candidate == "A" else None
    resource_error = full_error(after, after_i)
    history_error = full_error(wn, wn_i) if wn is not None else Q(0)
    require(resource_error < RESOURCE_ERROR_LIMIT, "full resource error unresolved")
    require(history_error < HISTORY_ERROR_LIMIT, "full history error unresolved")
    return (
        after,
        wn,
        {
            "H": h,
            "exact_H": hi,
            "read": read,
            "exact_read": exact_read,
            "exact_after": after_i,
            "exact_history": wn_i,
            "certificate": certificate,
            "chain": chain,
            "resource_error": resource_error,
            "history_error": history_error,
        },
    )


class RGNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rg.RGCompletionTests.setUpClass()
        cls.source, cls.target = [
            RepresentedAuxiliary(m.nodes, m.edges, PARAMS)
            for m in (rg.RGCompletionTests.source, rg.RGCompletionTests.target)
        ]

    def initial(self, candidate, role):
        center = Q(3) if role == "current" else Q(2)
        desired = {
            n: center if n == "source-s" else center + bounds.OUTSIDE_OFFSET
            for n in self.source.nodes
        }
        initial = (
            bounds.preimage(self.source.edges, desired)
            if role == "current"
            else desired
        )
        c = self.source.vector(initial)
        w = (
            np.full(len(self.source.edges), float(1 - HISTORY_OFFSET))
            if candidate == "A"
            else None
        )
        self.assertLess(
            max(
                abs(Q(float(c[i])) - initial[node])
                for i, node in enumerate(self.source.nodes)
            ),
            rg.RESOURCE_RADIUS,
        )
        return c, w

    def event(self, c, w):
        source, target = self.source, self.target
        ct = target.vector(
            {
                n: c[source.index[n]]
                if n.startswith("outside-")
                else c[source.index["source-s"]] / 3
                if n.startswith("satellite/")
                else 0
                for n in target.nodes
            }
        )
        lineage = (
            dict(zip((e["edge_id"] for e in source.edges), w, strict=True))
            if w is not None
            else {}
        )
        wt = (
            np.array([lineage.get(e["edge_id"], 1.0) for e in target.edges])
            if w is not None
            else None
        )
        exact = [
            Q(float(c[source.index[n]]))
            if n.startswith("outside-")
            else Q(float(c[source.index["source-s"]])) / 3
            if n.startswith("satellite/")
            else Q(0)
            for n in target.nodes
        ]
        self.assertLess(
            max(abs(Q(float(x)) - y) for x, y in zip(ct, exact, strict=True)),
            RESOURCE_ERROR_LIMIT,
        )
        return ct, wt

    def test_both_roles_source_and_ten_target_steps(self):
        report = {}
        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                c, w = self.initial(candidate, role)
                rows = []
                if role == "current":
                    c, w, stage = ordinary(self.source, candidate, c, w)
                    rows.append(self.summary("source", stage))
                    rows.append(
                        self.read_summary(
                            "source_poststate", self.source, candidate, c, w
                        )
                    )
                    row = IntervalRows(self.source).rows(
                        vector(c),
                        vector(w)
                        if w is not None
                        else vector([1] * len(self.source.edges)),
                    )[self.source.index["source-s"]]
                    self.assertTrue(all(endpoint(x, 0) > 0 for x in row))
                    self.assertLess(sum(upper_abs(x) ** 2 for x in row), Q(1, 4))
                else:
                    # Independently supplied reset is read, never advanced.
                    rows.append(
                        self.read_summary("source", self.source, candidate, c, w)
                    )
                c, w = self.event(c, w)
                self.assertEqual(c[self.target.index["core"]], 0)
                for k in range(bounds.HORIZON):
                    c, w, stage = ordinary(self.target, candidate, c, w)
                    if k == 0:
                        certificate = stage["certificate"]
                        b = rg.global_bounds(candidate)
                        sb = rg.section_budgets(b)
                        inverse_tail = (
                            sb["inverse_lip"]
                            * b["A_H"]
                            * sb["q_section"] ** (DEPTH[candidate] - 1)
                            * sb["value_radius"]
                        )
                        inverse_core = Q(
                            float(stage["chain"].x[1][self.target.index["core"]])
                        )
                        inverse_input_error = (
                            sb["inverse_lip"]
                            * certificate["input_error"]
                            / rg.SECTION_LIP
                        )
                        self.assertLess(
                            inverse_core
                            + certificate["state_error"]
                            + inverse_tail
                            + inverse_input_error,
                            0,
                        )
                    self.assertGreater(
                        min(endpoint(x, 0) for x in stage["exact_after"]), Q(1, 16384)
                    )
                    self.assertLess(
                        max(endpoint(x, 1) for x in stage["exact_after"]), 4
                    )
                    rows.append(self.summary(f"target_{k}", stage))
                # Include the last writer's reconstruction, without an extra beat.
                rows.append(
                    self.read_summary("target_10_read", self.target, candidate, c, w)
                )
                report[candidate + "_" + role] = rows
        type(self).continuation_report = report

    @staticmethod
    def summary(label, stage):
        return dict(
            stage=label,
            **{k: float(v) for k, v in stage["certificate"].items()},
            resource_error=float(stage["resource_error"]),
            history_error=float(stage["history_error"]),
        )

    @staticmethod
    def read_summary(label, model, candidate, c, w):
        _, hi, cert, _ = section(model, candidate, c, w)
        IntervalRows(model).read(
            candidate, vector(c), vector(w) if w is not None else None, hi
        )
        return dict(stage=label, **{k: float(v) for k, v in cert.items()})

    def test_defining_effects_invariance_and_history_consumers(self):
        report = {}
        for candidate in ("A", "C"):
            for role in ("current", "reset"):
                c, w = self.initial(candidate, role)
                after, wn, _ = ordinary(self.source, candidate, c, w)
                ct, wt = (
                    self.event(after, wn) if role == "current" else self.event(c, w)
                )
                cases = (
                    ("source", self.source, c, w),
                    ("target", self.target, ct, wt),
                )
                for label, model, c, w in cases:
                    high = IntervalRows(model)
                    ci, wi = vector(c), vector(w) if w is not None else None
                    after, wn, stage = ordinary(model, candidate, c, w)
                    h, hi = stage["H"], stage["exact_H"]
                    exact = stage["exact_read"]
                    key = candidate + "_" + role + "_" + label
                    for name, flags in (
                        ("geometry", {"geometry": False}),
                        ("readback", {"feedback": False}),
                        *(
                            (("modulation", {"modulation": False}),)
                            if candidate == "C"
                            else ()
                        ),
                    ):
                        control = model.read(candidate, c, w, h, **flags)
                        control_i = high.read(candidate, ci, wi, hi, **flags)
                        report[key + "_" + name] = separation(
                            stage["read"]["J"], control["J"], exact["J"], control_i["J"]
                        )
                    # Time-shifted RG geometry must not be an OS predictor or
                    # an instantaneous CI fixed point at the queried state.
                    os = model.ordinary_os(candidate, c, w)[2]
                    os_i = high.ordinary_os(candidate, ci, wi)[2]
                    report[key + "_versus_os_current"] = separation(
                        stage["read"]["J"],
                        os["read"]["J"],
                        exact["J"],
                        os_i["read"]["J"],
                    )
                    instantaneous = (
                        model.I + float(bounds.KAPPA_H) * stage["read"]["source"]
                    )
                    instantaneous_i = high.I + number(bounds.KAPPA_H) * exact["source"]
                    report[key + "_not_ci_root"] = separation(
                        h.ravel(),
                        instantaneous.ravel(),
                        IV.matrix(list(hi)),
                        IV.matrix(list(instantaneous_i)),
                    )
                    # The exact same-input ordinary output is enclosed, including
                    # its log-history conversion in the following section query.
                    _, next_hi, _, _ = section(
                        model,
                        candidate,
                        after,
                        wn,
                        exact_c=stage["exact_after"],
                        exact_w=stage["exact_history"],
                    )
                    for defect in next_hi - instantaneous_i:
                        self.assertLessEqual(endpoint(defect, 0), 0)
                        self.assertGreaterEqual(endpoint(defect, 1), 0)
                    if candidate == "A" and label == "target":
                        for name in ("baseline_current", "stale_resource"):
                            wc = staged_write(
                                model,
                                after if name == "baseline_current" else c,
                                w,
                                stage["read"]["baseline"]
                                if name == "baseline_current"
                                else stage["read"]["J"],
                            )
                            wci = high.write(
                                stage["exact_after"]
                                if name == "baseline_current"
                                else ci,
                                wi,
                                exact["baseline"]
                                if name == "baseline_current"
                                else exact["J"],
                            )
                            report[key + "_" + name + "_history"] = separation(
                                wn, wc, stage["exact_history"], wci
                            )
                            next_on = ordinary(
                                model,
                                candidate,
                                after,
                                wn,
                                exact_c=stage["exact_after"],
                                exact_w=stage["exact_history"],
                            )[2]
                            next_off = ordinary(
                                model,
                                candidate,
                                after,
                                wc,
                                exact_c=stage["exact_after"],
                                exact_w=wci,
                            )[2]
                            report[key + "_" + name + "_next_current"] = separation(
                                next_on["read"]["J"],
                                next_off["read"]["J"],
                                next_on["exact_read"]["J"],
                                next_off["exact_read"]["J"],
                            )
        type(self).effect_report = report

    def test_global_completion_at_every_depth_and_certificate_mutations(self):
        report = {}
        for candidate in ("A", "C"):
            model, n, m = self.target, len(self.target.nodes), len(self.target.edges)
            # Mixed exterior points force the frozen clamp at every depth;
            # they are auxiliary queries, never physical input resources.
            query = np.array(
                [-0.9 if i % 2 else 5.2 for i in range(n)]
                + ([(-1.0) ** i * 1.2 for i in range(m)] if candidate == "A" else [])
            )
            exact_query = vector(query)
            chain = solve_chain(model, candidate, query, DEPTH[candidate])
            high = rg.auxiliary(model)
            _, cert = certify_chain(high, candidate, chain, exact_query)
            self.assertTrue(all(np.any(x[:n] > 5) for x in chain.x[1:]))
            self.assertTrue(all(np.any(x[:n] < 0) for x in chain.x[1:]))
            if candidate == "A":
                self.assertTrue(all(np.any(np.abs(x[n:]) > 1) for x in chain.x[1:]))
            report[candidate + "_exterior"] = {k: float(v) for k, v in cert.items()}
            import copy

            for mode in (
                "identity_output",
                "stale_state",
                "last_coordinate",
                "terminal",
                "missing",
                "nonfinite",
                "asymmetric",
            ):
                bad = copy.deepcopy(chain)
                if mode == "identity_output":
                    bad.h[0] = model.I.copy()
                elif mode == "stale_state":
                    bad.x[1] = bad.x[0].copy()
                elif mode == "last_coordinate":
                    bad.x[-1][-1] += 0.01
                elif mode == "terminal":
                    bad.h[-1][0, 0] += 1e-6
                elif mode == "missing":
                    bad.h.pop()
                elif mode == "nonfinite":
                    bad.x[-1][-1] = math.nan
                else:
                    bad.h[1][0, 1] += 1e-6
                with (
                    self.subTest(candidate=candidate, mutation=mode),
                    self.assertRaises(ValueError),
                ):
                    certify_chain(high, candidate, bad, exact_query)
            for mode in (
                ("nonnegative_resource", "narrow_history")
                if candidate == "A"
                else ("nonnegative_resource",)
            ):
                original = RepresentedAuxiliary.increment

                def wrong_increment(
                    owner, family, x, h, mode=mode, n=n, original=original
                ):
                    altered = x.copy()
                    if mode == "nonnegative_resource":
                        altered[:n] = np.maximum(0, altered[:n])
                    else:
                        altered[n:] = np.clip(altered[n:], -0.625, 0.625)
                    return original(owner, family, altered, h)

                with patch.object(RepresentedAuxiliary, "increment", wrong_increment):
                    bad = solve_chain(model, candidate, query, DEPTH[candidate])
                with (
                    self.subTest(candidate=candidate, clamp=mode),
                    self.assertRaisesRegex(ValueError, "budget"),
                ):
                    certify_chain(high, candidate, bad, exact_query)
            shallow = solve_chain(model, candidate, query, 1)
            with self.assertRaisesRegex(ValueError, "budget"):
                certify_chain(high, candidate, shallow, exact_query)
        type(self).control_report = report

    def test_actual_consumer_rejects_substitutions_and_admits_equilibrium(self):
        import copy

        for candidate in ("A", "C"):
            model = self.target
            c = model.vector(bounds.resources(model.nodes, Q(3)))
            w = (
                np.array(
                    [
                        float(1 - HISTORY_OFFSET)
                        if e["edge_id"].startswith("old-")
                        else 1.0
                        for e in model.edges
                    ]
                )
                if candidate == "A"
                else None
            )
            _, _, _, chain = section(model, candidate, c, w)
            os_h = (
                model.I
                + float(bounds.KAPPA_H) * model.read(candidate, c, w, model.I)["source"]
            )
            ci_h = os_h.copy()
            for _ in range(8):
                ci_h = (
                    model.I
                    + float(bounds.KAPPA_H)
                    * model.read(candidate, c, w, ci_h)["source"]
                )
            for name, replacement in (
                ("identity", model.I),
                ("os", os_h),
                ("ci", ci_h),
            ):
                bad = copy.deepcopy(chain)
                bad.h[0] = replacement.copy()
                with (
                    patch(__name__ + ".solve_chain", return_value=bad),
                    self.subTest(candidate=candidate, mode=name),
                    self.assertRaisesRegex(ValueError, "budget"),
                ):
                    ordinary(model, candidate, c, w)
            bad = copy.deepcopy(chain)
            bad.x[-1][-1] += 0.01
            with (
                patch(__name__ + ".solve_chain", return_value=bad),
                self.assertRaisesRegex(ValueError, "budget"),
            ):
                ordinary(model, candidate, c, w)
            # Exact zero-current controls remain legal; effect witnesses are
            # assertions about named nondegenerate stages, not every state.
            flat_c = np.full(len(self.source.nodes), 3.0)
            flat_w = np.ones(len(self.source.edges)) if candidate == "A" else None
            h, _, _, _ = section(self.source, candidate, flat_c, flat_w)
            self.assertTrue(np.array_equal(h, self.source.I))
            self.assertTrue(
                np.all(self.source.read(candidate, flat_c, flat_w, h)["J"] == 0)
            )


if __name__ == "__main__":
    import sys

    reporting = "--report" in sys.argv
    if reporting:
        sys.argv.remove("--report")
    result = unittest.main(exit=False)
    if reporting and result.result.wasSuccessful():
        print(
            json.dumps(
                {
                    name: getattr(RGNumericalTests, name, None)
                    for name in (
                        "continuation_report",
                        "effect_report",
                        "control_report",
                    )
                },
                indent=2,
            )
        )
    sys.exit(not result.result.wasSuccessful())
