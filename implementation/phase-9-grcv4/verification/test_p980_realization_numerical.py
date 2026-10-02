"""Bounded CI/PC/CI+PC represented research; no native/event admission.

Reuses A's fixed-H binary64 read kernel from the RG numerical owner; C uses
an equivalent compensated correction solve with its own error certificates.
Every root, current and same-source writer is independently enclosed here.
Source and target carriers are separately supplied, not an event-transfer law.
"""

import copy
import json
import math
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import test_p980_revised_realization_bounds as exact
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
from test_p980_rg2b_numerical import RepresentedAuxiliary, finite_array

REALIZATIONS = ("CI", "PC", "CI_PC")
GEOMETRY_ERROR_LIMIT = Q(1, 2**48)
RESOURCE_ERROR_LIMIT = CURRENT_ERROR_LIMIT = Q(1, 2**40)
HISTORY_ERROR_LIMIT = Q(1, 2**48)
SOURCE_ERROR_LIMIT = CARRIER_ERROR_LIMIT = Q(1, 2**64)


class RepresentedRows(StagedRows):
    def read(
        self, candidate, c, w, h, *, geometry=True, feedback=True, modulation=True
    ):
        if candidate == "A":
            return RepresentedAuxiliary.read(
                self,
                candidate,
                c,
                w,
                h,
                geometry=geometry,
                feedback=feedback,
                modulation=modulation,
            )
        # Solve for R J directly, then add the small feedback correction to J0:
        # (I+t H D-p I) u=J0; J=J0+p u; u=R J. This identity requires no
        # commutation of D and H. Compensated dot products reduce baseline loss.
        t = (
            math.exp(float(bounds.KAPPA_M) * math.tanh(math.fsum(c) / len(c)))
            if modulation
            else 1.0
        )
        b = product(self.B.T, c)
        baseline = -t * product(self.D, product(h if geometry else self.I, b))
        chi, zeta = float(PARAMS.chi_c), float(PARAMS.zeta_c)
        p = chi * zeta
        if feedback:
            u = np.linalg.solve((1 - p) * self.I + t * product(h, self.D), baseline)
            j, causal = baseline + p * u, chi * u
        else:
            j, causal = baseline, np.zeros_like(baseline)
        flat = np.linalg.solve(h, causal)
        return {
            "J": j,
            "baseline": baseline,
            "source": zeta * self.mask * np.outer(flat, flat),
        }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_separation(label, *operands):
    try:
        return separation(*operands)
    except AssertionError as exc:
        raise AssertionError(f"{label}: {exc}") from exc


def matrix_error(represented, enclosure):
    a = finite_array(represented, (enclosure.rows, enclosure.cols))
    return full_error(a.ravel(), IV.matrix(list(enclosure)))


def frobenius_squared(a):
    return sum(upper_abs(a[i, j]) ** 2 for i in range(a.rows) for j in range(a.cols))


def carrier_input(model, z, zi=None):
    m = len(model.edges)
    z = finite_array(z, (m, m))
    require(
        exact.carrier_admitted(model, z.tolist()), "represented carrier outside domain"
    )
    zi = IV.matrix(z.tolist()) if zi is None else zi
    require(zi.rows == m and zi.cols == m, "incomplete carrier enclosure")
    for i in range(m):
        for j in range(m):
            endpoints = (endpoint(zi[i, j], 0), endpoint(zi[i, j], 1))
            require(
                endpoints == (endpoint(zi[j, i], 0), endpoint(zi[j, i], 1)),
                "asymmetric carrier enclosure",
            )
            require(model.mask[i, j] or endpoints == (0, 0), "disjoint carrier entry")
    require(
        frobenius_squared(zi) <= exact.CARRIER_RADIUS**2,
        "carrier enclosure outside ball",
    )
    return zi


def seed_carrier(model, role):
    """Distinct nonzero dyadic inputs on EACH graph; no source/target transfer."""
    sign = 1 if role == "current" else -1
    m = len(model.edges)
    return np.array(
        [
            [
                sign
                * float(exact.CARRIER_RADIUS / 16)
                * float(model.mask[i, j])
                * (-1.0) ** (i + j)
                for j in range(m)
            ]
            for i in range(m)
        ]
    )


def solve_geometry(model, candidate, realization, c, w, z):
    base = model.I if realization == "CI" else model.I + float(bounds.KAPPA_H) * z
    h = base.copy()
    if realization != "PC":
        for _ in range(4):
            h = base + float(bounds.KAPPA_H) * model.read(candidate, c, w, h)["source"]
    return h


def produce_step(model, candidate, realization, c, w, z):
    h = solve_geometry(model, candidate, realization, c, w, z)
    read = model.read(candidate, c, w, h)
    after = c - float(bounds.DT) * product(model.B, read["J"])
    wn = staged_write(model, after, w, read["J"]) if candidate == "A" else None
    decay = math.exp(-float(bounds.DT))
    zn = decay * z + (1 - decay) * read["source"] if z is not None else None
    return {"H": h, "read": read, "after": after, "history": wn, "carrier": zn}


def certify_read(
    model, candidate, realization, c, w, z, h, read, *, ci=None, wi=None, zi=None
):
    require(
        candidate in ("A", "C") and realization in REALIZATIONS,
        "unknown research profile",
    )
    n, m = len(model.nodes), len(model.edges)
    finite_array(c, (n,))
    ci = vector(c) if ci is None else ci
    if candidate == "A":
        finite_array(w, (m,))
        wi = vector(w) if wi is None else wi
    else:
        require(w is None and wi is None, "C has no W history")
    high = IntervalRows(model)
    if realization == "CI":
        require(z is None and zi is None, "CI has no persistent carrier")
        base = high.I
    else:
        zi = carrier_input(model, z, zi)
        base = high.I + number(bounds.KAPPA_H) * zi
    # Recheck the actual state box, not a surrounding rectangular chart claim.
    whole_read, budget = exact.read_bounds(high, candidate, ci, wi)
    exact.assert_current_frobenius_aggregation(
        whole_read["source"], budget["source_frobenius_squared"]
    )
    exact.realization_budgets(budget)
    finite_array(h, (m, m))
    require(
        np.array_equal(h, h.T) and np.all(h[model.mask == 0] == 0),
        "geometry structure mismatch",
    )
    hi_point = IV.matrix(h.tolist())
    require(
        infinity(hi_point - high.I) <= exact.GEOMETRY_RADIUS,
        "geometry outside root ball",
    )
    q = budget["contraction"] if realization != "PC" else Q(0)
    image = base
    if realization != "PC":
        image += (
            number(bounds.KAPPA_H) * high.read(candidate, ci, wi, hi_point)["source"]
        )
    residual = infinity(hi_point - image)
    root_error = residual / (1 - q)
    require(root_error < GEOMETRY_ERROR_LIMIT, "geometry error budget unresolved")
    # One exact image contracts the root error, keeping diagonal publication
    # rounding separate from the uncertainty in the underlying exact root.
    padding = q * root_error
    hi = IV.matrix(
        [
            [
                IV.mpf(
                    [
                        (image[i, j] - number(padding)).a,
                        (image[i, j] + number(padding)).b,
                    ]
                )
                if model.mask[i, j]
                else number(0)
                for j in range(m)
            ]
            for i in range(m)
        ]
    )
    truth = high.read(candidate, ci, wi, hi)
    current_error = full_error(read["J"], truth["J"])
    source_error = matrix_error(read["source"], truth["source"])
    baseline_error = full_error(read["baseline"], truth["baseline"])
    require(
        max(current_error, baseline_error) < CURRENT_ERROR_LIMIT,
        "full current error unresolved",
    )
    require(source_error < SOURCE_ERROR_LIMIT, "incoming source binding unresolved")
    require(
        frobenius_squared(truth["source"]) < exact.CARRIER_RADIUS**2,
        "source leaves carrier ball",
    )
    return {
        "high": high,
        "H": hi,
        "read": truth,
        "c": ci,
        "w": wi,
        "z": zi,
        "certificate": {
            "contraction": q,
            "residual": residual,
            "root_error": root_error,
            "current_error": current_error,
            "source_error": source_error,
            "regularity": budget["regularity"],
        },
    }


def evaluate(
    model, candidate, realization, c, w=None, z=None, *, ci=None, wi=None, zi=None
):
    require(
        candidate in ("A", "C") and realization in REALIZATIONS,
        "unknown research profile",
    )
    if realization == "CI":
        require(z is None, "CI has no persistent carrier")
    else:
        carrier_input(model, z, zi)
    # RN-F1: certification owns the entry operands, independently of producer
    # work storage. Exact-input enclosures need not contain rounded points.
    finite_array(c, (len(model.nodes),))
    if candidate == "A":
        finite_array(w, (len(model.edges),))
    else:
        require(w is None and wi is None, "C has no W history")
    c = c.copy()
    w = None if w is None else w.copy()
    z = None if z is None else z.copy()
    output = produce_step(
        model,
        candidate,
        realization,
        c.copy(),
        None if w is None else w.copy(),
        None if z is None else z.copy(),
    )
    truth = certify_read(
        model,
        candidate,
        realization,
        c,
        w,
        z,
        output["H"],
        output["read"],
        ci=ci,
        wi=wi,
        zi=zi,
    )
    high = truth["high"]
    after = truth["c"] - number(bounds.DT) * high.B * truth["read"]["J"]
    history = (
        high.write(after, truth["w"], truth["read"]["J"]) if candidate == "A" else None
    )
    if candidate == "C":
        require(output["history"] is None, "C history output must be absent")
    resource_error = full_error(output["after"], after)
    history_error = (
        full_error(output["history"], history) if history is not None else Q(0)
    )
    require(resource_error < RESOURCE_ERROR_LIMIT, "full resource error unresolved")
    require(history_error < HISTORY_ERROR_LIMIT, "full history error unresolved")
    if z is None:
        require(output["carrier"] is None, "CI carrier output must be absent")
        carrier, carrier_error = None, Q(0)
    else:
        decay = IV.exp(-number(bounds.DT))
        carrier = decay * truth["z"] + (1 - decay) * truth["read"]["source"]
        carrier_error = matrix_error(output["carrier"], carrier)
        require(
            carrier_error < CARRIER_ERROR_LIMIT, "same-source carrier writer unresolved"
        )
        carrier_input(model, output["carrier"], carrier)
    truth.update(after=after, history=history, carrier=carrier)
    truth["certificate"].update(
        resource_error=resource_error,
        history_error=history_error,
        carrier_error=carrier_error,
    )
    return output, truth


class RealizationNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exact.RevisedRealizationBoundTests.setUpClass()
        cls.source, cls.target = [
            RepresentedRows(m.nodes, m.edges, PARAMS)
            for m in (
                exact.RevisedRealizationBoundTests.source,
                exact.RevisedRealizationBoundTests.target,
            )
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
        self.assertLess(
            max(
                abs(Q(float(c[i])) - initial[n])
                for i, n in enumerate(self.source.nodes)
            ),
            exact.RESOURCE_RADIUS,
        )
        w = (
            np.full(len(self.source.edges), float(1 - HISTORY_OFFSET))
            if candidate == "A"
            else None
        )
        return c, w

    def target_inputs(self, c, w, realization, role):
        source, target = self.source, self.target
        exact_c = [
            Q(float(c[source.index[n]]))
            if n.startswith("outside-")
            else Q(float(c[source.index["source-s"]])) / 3
            if n.startswith("satellite/")
            else Q(0)
            for n in target.nodes
        ]
        ct = np.array([float(x) for x in exact_c])
        self.assertLess(full_error(ct, vector(exact_c)), RESOURCE_ERROR_LIMIT)
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
        # Explicit independently supplied target input, NOT a carrier event map.
        zt = seed_carrier(target, role) if realization != "CI" else None
        return ct, wt, zt

    def read_stage(self, model, candidate, realization, c, w, z):
        h = solve_geometry(model, candidate, realization, c, w, z)
        read = model.read(candidate, c, w, h)
        return certify_read(model, candidate, realization, c, w, z, h, read)

    def test_six_profiles_both_roles_ten_target_steps(self):
        report = {}
        for candidate in ("A", "C"):
            for realization in REALIZATIONS:
                for role in ("current", "reset"):
                    c, w = self.initial(candidate, role)
                    z = seed_carrier(self.source, role) if realization != "CI" else None
                    rows = []

                    def record(stage, truth, rows=rows):
                        rows.append(
                            dict(
                                stage=stage,
                                **{
                                    k: float(v) for k, v in truth["certificate"].items()
                                },
                            )
                        )

                    if role == "current":
                        out, truth = evaluate(
                            self.source, candidate, realization, c, w, z
                        )
                        record("source", truth)
                        c, w, z = out["after"], out["history"], out["carrier"]
                        record(
                            "source_poststate",
                            self.read_stage(
                                self.source, candidate, realization, c, w, z
                            ),
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
                        record(
                            "source",
                            self.read_stage(
                                self.source, candidate, realization, c, w, z
                            ),
                        )
                    c, w, z = self.target_inputs(c, w, realization, role)
                    for i, n in enumerate(self.target.nodes):
                        if n == "core" or n.startswith("extra/"):
                            self.assertEqual(c[i], 0)
                    for k in range(bounds.HORIZON):
                        out, truth = evaluate(
                            self.target, candidate, realization, c, w, z
                        )
                        self.assertGreater(
                            min(endpoint(x, 0) for x in truth["after"]), Q(1, 16384)
                        )
                        self.assertLess(max(endpoint(x, 1) for x in truth["after"]), 4)
                        c, w, z = out["after"], out["history"], out["carrier"]
                        record(f"target_{k}", truth)
                    record(
                        "target_10_read",
                        self.read_stage(self.target, candidate, realization, c, w, z),
                    )
                    report[candidate + "_" + realization + "_" + role] = rows
        type(self).continuation_report = report

    def test_defining_effects_and_next_history_carrier_consumers(self):
        report = {}
        for candidate in ("A", "C"):
            for realization in REALIZATIONS:
                for role in ("current", "reset"):
                    cs, ws = self.initial(candidate, role)
                    zs = (
                        seed_carrier(self.source, role) if realization != "CI" else None
                    )
                    source_out, _ = evaluate(
                        self.source, candidate, realization, cs, ws, zs
                    )
                    ct, wt, zt = (
                        self.target_inputs(
                            source_out["after"],
                            source_out["history"],
                            realization,
                            role,
                        )
                        if role == "current"
                        else self.target_inputs(cs, ws, realization, role)
                    )
                    for label, model, c, w, z in (
                        ("source", self.source, cs, ws, zs),
                        ("target", self.target, ct, wt, zt),
                    ):
                        out, truth = evaluate(model, candidate, realization, c, w, z)
                        key = candidate + "_" + realization + "_" + role + "_" + label
                        high, hi = truth["high"], truth["H"]
                        ci, wi = truth["c"], truth["w"]
                        controls = [
                            ("geometry", {"geometry": False}),
                            ("readback", {"feedback": False}),
                        ]
                        if candidate == "C":
                            controls.append(("modulation", {"modulation": False}))
                        for name, flags in controls:
                            low_off = model.read(candidate, c, w, out["H"], **flags)
                            high_off = high.read(candidate, ci, wi, hi, **flags)
                            report[key + "_" + name] = checked_separation(
                                key + "_" + name,
                                out["read"]["J"],
                                low_off["J"],
                                truth["read"]["J"],
                                high_off["J"],
                            )
                        if realization != "CI":
                            off, off_i = evaluate(
                                model, candidate, realization, c, w, np.zeros_like(z)
                            )
                            report[key + "_old_carrier"] = checked_separation(
                                key + "_old_carrier",
                                out["read"]["J"],
                                off["read"]["J"],
                                truth["read"]["J"],
                                off_i["read"]["J"],
                            )
                        if realization == "CI_PC":
                            off, off_i = evaluate(model, candidate, "PC", c, w, z)
                            report[key + "_instantaneous_source"] = checked_separation(
                                key + "_instantaneous_source",
                                out["read"]["J"],
                                off["read"]["J"],
                                truth["read"]["J"],
                                off_i["read"]["J"],
                            )
                        if label != "target":
                            continue
                        if realization != "CI":
                            # Wrong writer source: re-read post-continuity C/W at
                            # the old selected H, instead of the incoming read.
                            wrong_source = model.read(
                                candidate, out["after"], out["history"], out["H"]
                            )["source"]
                            wrong_source_i = high.read(
                                candidate, truth["after"], truth["history"], hi
                            )["source"]
                            a, ai = (
                                math.exp(-float(bounds.DT)),
                                IV.exp(-number(bounds.DT)),
                            )
                            wrong_z = a * z + (1 - a) * wrong_source
                            wrong_zi = ai * truth["z"] + (1 - ai) * wrong_source_i
                            report[key + "_same_source_carrier"] = checked_separation(
                                key + "_same_source_carrier",
                                out["carrier"].ravel(),
                                wrong_z.ravel(),
                                IV.matrix(list(truth["carrier"])),
                                IV.matrix(list(wrong_zi)),
                            )
                            next_on, next_oni = evaluate(
                                model,
                                candidate,
                                realization,
                                out["after"],
                                out["history"],
                                out["carrier"],
                                ci=truth["after"],
                                wi=truth["history"],
                                zi=truth["carrier"],
                            )
                            next_off, next_offi = evaluate(
                                model,
                                candidate,
                                realization,
                                out["after"],
                                out["history"],
                                wrong_z,
                                ci=truth["after"],
                                wi=truth["history"],
                                zi=wrong_zi,
                            )
                            report[key + "_same_source_next_current"] = (
                                checked_separation(
                                    key + "_same_source_next_current",
                                    next_on["read"]["J"],
                                    next_off["read"]["J"],
                                    next_oni["read"]["J"],
                                    next_offi["read"]["J"],
                                )
                            )
                        if candidate == "A":
                            for name in ("baseline_current", "stale_resource"):
                                wc = staged_write(
                                    model,
                                    out["after"] if name == "baseline_current" else c,
                                    w,
                                    out["read"]["baseline"]
                                    if name == "baseline_current"
                                    else out["read"]["J"],
                                )
                                wci = high.write(
                                    truth["after"]
                                    if name == "baseline_current"
                                    else ci,
                                    wi,
                                    truth["read"]["baseline"]
                                    if name == "baseline_current"
                                    else truth["read"]["J"],
                                )
                                report[key + "_" + name + "_history"] = (
                                    checked_separation(
                                        key + "_" + name + "_history",
                                        out["history"],
                                        wc,
                                        truth["history"],
                                        wci,
                                    )
                                )
                                next_on, next_oni = evaluate(
                                    model,
                                    candidate,
                                    realization,
                                    out["after"],
                                    out["history"],
                                    out["carrier"],
                                    ci=truth["after"],
                                    wi=truth["history"],
                                    zi=truth["carrier"],
                                )
                                next_off, next_offi = evaluate(
                                    model,
                                    candidate,
                                    realization,
                                    out["after"],
                                    wc,
                                    out["carrier"],
                                    ci=truth["after"],
                                    wi=wci,
                                    zi=truth["carrier"],
                                )
                                report[key + "_" + name + "_next_current"] = (
                                    checked_separation(
                                        key + "_" + name + "_next_current",
                                        next_on["read"]["J"],
                                        next_off["read"]["J"],
                                        next_oni["read"]["J"],
                                        next_offi["read"]["J"],
                                    )
                                )
        type(self).effect_report = report

    def test_actual_consumer_rejects_wrong_roots_sources_and_writers(self):
        for candidate in ("A", "C"):
            for realization in REALIZATIONS:
                cs, ws = self.initial(candidate, "current")
                c, w, z = self.target_inputs(cs, ws, realization, "current")
                good = produce_step(self.target, candidate, realization, c, w, z)
                modes = [
                    "identity_geometry",
                    "last_current",
                    "incomplete_current",
                    "nonfinite_source",
                ]
                if realization != "CI":
                    modes += [
                        "updated_carrier_read",
                        "poststate_source",
                        "wrong_carrier_write",
                    ]
                if realization == "CI_PC":
                    modes += ["omit_instantaneous", "omit_old_carrier"]
                for mode in modes:
                    bad = copy.deepcopy(good)
                    if mode == "identity_geometry":
                        bad["H"] = self.target.I.copy()
                    elif mode == "last_current":
                        bad["read"]["J"][-1] += 1e-6
                    elif mode == "incomplete_current":
                        bad["read"]["J"] = bad["read"]["J"][:-1]
                    elif mode == "nonfinite_source":
                        bad["read"]["source"][-1, -1] = math.nan
                    elif mode == "updated_carrier_read":
                        bad["H"] = solve_geometry(
                            self.target, candidate, realization, c, w, bad["carrier"]
                        )
                    elif mode == "poststate_source":
                        bad["read"]["source"] = self.target.read(
                            candidate, bad["after"], bad["history"], bad["H"]
                        )["source"]
                        a = math.exp(-float(bounds.DT))
                        bad["carrier"] = a * z + (1 - a) * bad["read"]["source"]
                    elif mode == "wrong_carrier_write":
                        bad["carrier"] = z.copy()
                    elif mode == "omit_instantaneous":
                        bad["H"] = solve_geometry(self.target, candidate, "PC", c, w, z)
                    else:
                        bad["H"] = solve_geometry(
                            self.target, candidate, "CI", c, w, None
                        )
                    with (
                        self.subTest(
                            candidate=candidate, realization=realization, mode=mode
                        ),
                        patch(__name__ + ".produce_step", return_value=bad),
                        self.assertRaises(ValueError),
                    ):
                        evaluate(self.target, candidate, realization, c, w, z)

    def test_producer_work_storage_cannot_move_entry_reference(self):
        producer = produce_step
        mutation_count = 0
        for candidate in ("A", "C"):
            for realization in REALIZATIONS:
                cs, ws = self.initial(candidate, "current")
                zs = (
                    seed_carrier(self.source, "current")
                    if realization != "CI"
                    else None
                )
                source, _ = evaluate(self.source, candidate, realization, cs, ws, zs)
                inputs = self.target_inputs(
                    source["after"], source["history"], realization, "current"
                )
                snapshots = [None if x is None else x.copy() for x in inputs]

                def assert_unchanged(inputs=inputs, snapshots=snapshots):
                    for original, saved in zip(inputs, snapshots, strict=True):
                        if saved is not None:
                            np.testing.assert_array_equal(original, saved)

                # In-place scratch work is lawful when outputs still describe
                # the entry state; the caller must retain its own operands.
                def valid_work(m, a, r, c, w, z):
                    output = producer(m, a, r, c, w, z)
                    for work in (c, w, z):
                        if work is not None:
                            work.fill(0)
                    return output

                with patch(__name__ + ".produce_step", side_effect=valid_work):
                    evaluate(self.target, candidate, realization, *inputs)
                assert_unchanged()
                operands = ["C"] + (["W"] if candidate == "A" else [])
                if realization != "CI":
                    operands.append("Z")
                for operand in operands:

                    def corrupt(m, a, r, c, w, z, operand=operand):
                        if operand == "C":
                            c[m.index["core"]] += 2.0**-16
                        elif operand == "W":
                            w[-1] += 2.0**-20
                        else:
                            z[0, 0] += float(exact.CARRIER_RADIUS / 64)
                        return producer(m, a, r, c, w, z)

                    with (
                        self.subTest(
                            candidate=candidate,
                            realization=realization,
                            operand=operand,
                        ),
                        patch(__name__ + ".produce_step", side_effect=corrupt),
                        self.assertRaises(ValueError),
                    ):
                        evaluate(self.target, candidate, realization, *inputs)
                    assert_unchanged()
                    mutation_count += 1
        self.assertEqual(mutation_count, 13)

        # Exact equilibrium counterexample: old code certified 3.125 against
        # the mutated reference with zero error, although entry C was 3.
        c = np.full(len(self.source.nodes), 3.0)

        def shift_equilibrium(m, a, r, c, w, z):
            c += 0.125
            return producer(m, a, r, c, w, z)

        with (
            patch(__name__ + ".produce_step", side_effect=shift_equilibrium),
            self.assertRaisesRegex(ValueError, "full resource error unresolved"),
        ):
            evaluate(self.source, "C", "CI", c)
        np.testing.assert_array_equal(c, np.full_like(c, 3.0))

    def test_exact_input_enclosures_can_exclude_rounded_operands(self):
        model = self.source
        c, w, z = (
            np.full(len(model.nodes), 3.0),
            np.ones(len(model.edges)),
            np.zeros_like(model.I),
        )
        ci = vector([Q(3) + Q(1, 2**48)] * len(c))
        wi = vector([Q(1) - Q(1, 2**60)] * len(w))
        zi = number(Q(1, 2**80)) * IntervalRows(model).I
        self.assertGreater(endpoint(ci[0], False), Q(float(c[0])))
        self.assertLess(endpoint(wi[0], True), Q(float(w[0])))
        self.assertGreater(endpoint(zi[0, 0], False), Q(float(z[0, 0])))
        _, truth = evaluate(model, "A", "PC", c, w, z, ci=ci, wi=wi, zi=zi)
        self.assertGreater(truth["certificate"]["resource_error"], 0)
        self.assertGreater(truth["certificate"]["carrier_error"], 0)

    def test_c_noncommuting_response_order_rejected_by_source_certificate(self):
        original_product = product
        rejections = 0
        for realization in REALIZATIONS:
            for role in ("current", "reset"):
                c, w = self.initial("C", role)
                if role == "current":
                    z = seed_carrier(self.source, role) if realization != "CI" else None
                    source, _ = evaluate(self.source, "C", realization, c, w, z)
                    c, w = source["after"], source["history"]
                inputs = self.target_inputs(c, w, realization, role)

                def swapped(left, right):
                    # Mutate only the H D response solve; the baseline D H
                    # and the independent interval evaluator are untouched.
                    if right is self.target.D:
                        return original_product(right, left)
                    return original_product(left, right)

                with (
                    self.subTest(realization=realization, role=role),
                    patch(__name__ + ".product", side_effect=swapped),
                    self.assertRaisesRegex(ValueError, "source"),
                ):
                    evaluate(self.target, "C", realization, *inputs)
                rejections += 1
        self.assertEqual(rejections, 6)

    def test_naive_old_edge_carrier_copy_violates_target_support(self):
        source_ids = {e["edge_id"]: i for i, e in enumerate(self.source.edges)}
        target_ids = {e["edge_id"]: i for i, e in enumerate(self.target.edges)}
        cases = 0
        for candidate in ("A", "C"):
            for realization in ("PC", "CI_PC"):
                for role in ("current", "reset"):
                    z = seed_carrier(self.source, role)
                    if role == "current":
                        c, w = self.initial(candidate, role)
                        source, _ = evaluate(
                            self.source, candidate, realization, c, w, z
                        )
                        z = source["carrier"]
                    copied = np.zeros_like(self.target.I)
                    for edge_i, i in source_ids.items():
                        for edge_j, j in source_ids.items():
                            copied[target_ids[edge_i], target_ids[edge_j]] = z[i, j]
                    unsupported = [
                        (i, j)
                        for i in range(len(copied))
                        for j in range(i + 1, len(copied))
                        if not self.target.mask[i, j] and copied[i, j] != 0
                    ]
                    with self.subTest(
                        candidate=candidate, realization=realization, role=role
                    ):
                        self.assertEqual(len(unsupported), 27)
                        pair = sorted((target_ids["old-1"], target_ids["old-2"]))
                        self.assertIn(tuple(pair), unsupported)
                        self.assertFalse(
                            exact.carrier_admitted(self.target, copied.tolist())
                        )
                        with self.assertRaises(ValueError):
                            carrier_input(self.target, copied)
                    cases += 1
        self.assertEqual(cases, 8)

    def test_carrier_domains_and_legitimate_zero_equilibrium(self):
        model = self.target
        z = seed_carrier(model, "current")
        self.assertFalse(np.array_equal(z, seed_carrier(model, "reset")))
        carrier_input(model, z)
        malformed = [None, z[:-1], z * 32]
        bad = z.copy()
        bad[0, 0] = math.inf
        malformed.append(bad)
        bad = z.copy()
        bad[0, 1] += 1e-9
        malformed.append(bad)
        i, j = next(
            (i, j) for i in range(len(z)) for j in range(len(z)) if not model.mask[i, j]
        )
        bad = z.copy()
        bad[i, j] = bad[j, i] = 1e-10
        malformed.append(bad)
        for bad in malformed:
            with self.assertRaises(ValueError):
                carrier_input(model, bad)
        for candidate in ("A", "C"):
            for realization in REALIZATIONS:
                c = np.full(len(self.source.nodes), 3.0)
                w = np.ones(len(self.source.edges)) if candidate == "A" else None
                z = np.zeros_like(self.source.I) if realization != "CI" else None
                out, truth = evaluate(self.source, candidate, realization, c, w, z)
                self.assertTrue(np.array_equal(out["H"], self.source.I))
                self.assertTrue(np.all(out["read"]["J"] == 0))
                self.assertEqual(truth["certificate"]["residual"], 0)

    def test_c_reset_legacy_margin_and_compensated_correction(self):
        # Retain the actual too-small full-error margin, rather than changing
        # gains, the nominal input, or the strict 4*error+8*ULP criterion.
        cs, ws = self.initial("C", "reset")
        c, w, z = self.target_inputs(cs, ws, "PC", "reset")

        def operands():
            out, truth = evaluate(self.target, "C", "PC", c, w, z)
            wrong = self.target.read("C", out["after"], None, out["H"])["source"]
            wrong_i = truth["high"].read("C", truth["after"], None, truth["H"])[
                "source"
            ]
            a, ai = math.exp(-float(bounds.DT)), IV.exp(-number(bounds.DT))
            zc, zci = a * z + (1 - a) * wrong, ai * truth["z"] + (1 - ai) * wrong_i
            on, oni = evaluate(
                self.target,
                "C",
                "PC",
                out["after"],
                None,
                out["carrier"],
                ci=truth["after"],
                zi=truth["carrier"],
            )
            off, offi = evaluate(
                self.target,
                "C",
                "PC",
                out["after"],
                None,
                zc,
                ci=truth["after"],
                zi=zci,
            )
            return (
                on["read"]["J"],
                off["read"]["J"],
                oni["read"]["J"],
                offi["read"]["J"],
            )

        with patch.object(RepresentedRows, "read", RepresentedAuxiliary.read):
            legacy = operands()
        with self.assertRaisesRegex(AssertionError, "full effect margin unresolved"):
            separation(*legacy)
        result = separation(*operands())
        self.assertGreater(result["minimum_margin_ratio"], 1)
        # The corrected response identity is checked in the noncommuting case.
        h = self.target.I + float(bounds.KAPPA_H) * z
        self.assertGreater(np.max(np.abs(h @ self.target.D - self.target.D @ h)), 0)


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
                    key: getattr(RealizationNumericalTests, key, None)
                    for key in ("continuation_report", "effect_report")
                },
                indent=2,
            )
        )
    sys.exit(not result.result.wasSuccessful())
