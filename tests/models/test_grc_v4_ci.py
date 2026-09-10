"""Independent CI equations, domain boundaries, and candidate-specific pressure."""

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from fractions import Fraction
import math
from copy import copy
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4_codec import V4SchemaError

from pygrc.models.grc_v4_candidate_a import (
    CandidateACurrent,
    CandidateAStageError,
    CandidateAWriter,
)
from pygrc.models.grc_v4_candidate_c import CandidateCStageError, CandidateCCurrent
from pygrc.models.grc_v4_ci import (
    CIBoundedDomain,
    CIContractionCertificate,
    CIStageError,
    CITrial,
    CandidateCIRoot,
    ProvisionalCandidateCIStep,
    JOINT_NORM,
    SOLVER_ID,
    _exp_bounds,
    _sqrt_upper,
    _Interval,
    _iv,
    _itanh,
    _iinverse,
    _projector_enclosure,
)
from pygrc.models.grc_v4_geometry import (
    GRCV4Geometry,
    GRCV4Graph,
    OneFormHodge,
    OrientedEdge,
    PhysicalFlux,
)
from pygrc.models.grc_v4_profile import resolve_profile, list_supported_profiles
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import (
    ResourceBoundaryError,
    CurrentSelection,
    ProvisionalResourceStep,
)
from tests.models.test_grc_v4_candidate_a import (
    current_fixture as a_fixture,
    scalar_oracle,
    log_writer_oracle,
)
from tests.models.test_grc_v4_candidate_c import (
    current_fixture as c_fixture,
    dense_current_oracle,
)
from tests.models.test_grc_v4_profile import reidentify


def configure(
    before, *, radius=0.125, gain=1e-5, tolerance=1e-11, limit=60, changes=None
):
    ref = before.geometry.reference
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["realization"] = dict(
        schema_version="grcv4-ci-params-v1",
        contraction_domain_id=CIBoundedDomain(radius).identity,
        root_selector_id="unique_admitted_root_v1",
        iteration_limit=limit,
        residual_norm_id=JOINT_NORM,
        tolerance=tolerance,
    )
    params["solver"].update(
        solver_kind="fixed_point",
        iteration_limit=limit,
        absolute_tolerance=1e-11,
        relative_tolerance=1e-11,
        conditioning_limit=1e8,
    )
    params["geometry"]["kappa_H"] = gain
    params["charge"]["absolute_tolerance"] = 1e-11
    identity.update(
        realization="CI",
        profile_family_id=identity["candidate"] + "_CI",
        solver_id=SOLVER_ID,
    )
    for group, values in (changes or {}).items():
        (identity if group == "identity" else params[group]).update(values)
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(before, geometry=ref.geometry())


def fixture(
    candidate="C",
    *,
    radius=0.125,
    gain=1e-5,
    tolerance=1e-11,
    limit=60,
    graph=None,
    C=(3.0, 1.0),
    W=(2.0,),
    changes=None,
):
    graph = graph or GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))
    if candidate == "A":
        before, backend = a_fixture(
            graph=graph, C=C, W=W, dt=2**-14, kappa_Ah=0.25, gamma=0.1
        )
    else:
        before = c_fixture(
            graph=graph,
            resource=C,
            weights={e: 2.0 for e in graph.live_edge_ids},
            changes={
                "candidate": {
                    "kappa_M_C": 0.0,
                    "chi_C": 0.25,
                    "zeta_C": 0.25,
                    "tau_C": 0.25,
                    "eta_C": 0.5,
                }
            },
        )
        before, backend = replace(before, dt=2**-14), None
    return configure(
        before,
        radius=radius,
        gain=gain,
        tolerance=tolerance,
        limit=limit,
        changes=changes,
    ), backend


def independent_point(before, backend, h):
    """Literal candidate equations; no production current/root/geometry helper."""
    ref, graph = before.geometry.reference, before.geometry.reference.graph
    p = ref.profile.params_resolved.candidate
    if backend is None:
        inputs = replace(
            before,
            geometry=GRCV4Geometry(ref, OneFormHodge(graph, tuple(map(tuple, h)))),
        )
        value = dense_current_oracle(inputs)
        current, read = value["current"], value["read"]
    else:
        b, c, w = (
            np.array(graph.incidence),
            np.array(before.current.C),
            np.array(before.current.W_A),
        )
        href = np.array(ref.pairings.one_form.matrix)
        phi = (
            p.kappa_c * b @ np.diag(w) @ b.T @ c + p.kappa_Ah * b @ (h - href) @ b.T @ c
        )
        j0 = -p.eta * w * (b.T @ phi)
        _, target = scalar_oracle(ref, backend, tuple(c), tuple(j0))
        q = (w - np.array(target)) / (w + np.array(target))
        current = j0 / (1 - p.zeta_A * p.chi_A * q)
        read = p.chi_A * q * current
    flat = np.linalg.solve(h, read)
    zeta = p.zeta_A if backend is not None else p.zeta_C
    stars = [
        [
            i
            for i, e in enumerate(graph.oriented_edges)
            if v in (e.tail_node_id, e.head_node_id)
        ]
        for v in graph.live_node_ids
    ]
    counts = [sum(i in s for s in stars) for i in range(len(graph.live_edge_ids))]
    source = np.zeros_like(h)
    for star in stars:
        for i in star:
            for j in star:
                source[i, j] += (
                    zeta * (flat[i] * flat[j]) / math.sqrt(counts[i] * counts[j])
                )
    return current, source


def independent_root(before, backend):
    ref = before.geometry.reference
    href = np.array(ref.pairings.one_form.matrix)
    h = href.copy()
    for _ in range(200):
        j, source = independent_point(before, backend, h)
        updated = href + ref.profile.params_resolved.geometry.kappa_H * source
        if np.linalg.norm(updated - h) < 1e-14:
            return j, h
        h = updated
    raise AssertionError("independent root did not converge")


def scalar_c_bisection(before):
    """200-digit monotone scalar equation, independent of fixed-point iteration."""
    p = before.geometry.reference.profile.params_resolved.candidate
    assert p.kappa_M_C == 0
    with localcontext() as ctx:
        ctx.prec = 200

        def d(x):
            return Decimal.from_float(float(x))

        href = d(2)
        beta, tau = d(p.zeta_C) * d(p.chi_C), d(p.tau_C)
        k = (
            2
            * d(p.eta_C)
            * d(2)
            * d(p.kappa_Phi_C)
            * (d(before.current.C[1]) - d(before.current.C[0]))
        )
        gain = d(
            before.geometry.reference.profile.params_resolved.geometry.kappa_H
        ) * d(p.zeta_C)
        radius = d(
            CIBoundedDomain.from_identity(
                before.geometry.reference.profile.params_resolved.realization.contraction_domain_id
            ).radius
        )
        lo, hi = href - radius, href + radius

        def f(h):
            return h - href - gain * (d(p.chi_C) * k / (1 + 2 * tau * h - beta)) ** 2

        assert f(lo) < 0 < f(hi)
        for _ in range(180):
            mid = (lo + hi) / 2
            if f(mid) > 0:
                hi = mid
            else:
                lo = mid
        h = (lo + hi) / 2
        j = k * h * (1 + 2 * tau * h) / (1 + 2 * tau * h - beta)
        return float(j), float(h)


class CandidateCCITests(unittest.TestCase):
    def test_analytic_selector_deformation_and_residual_against_decimal(self):
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")),
        )
        before, _ = fixture(
            "C",
            graph=graph,
            C=(3.0, 1.0, 2.0),
            W=(2.0, 2.0),
            gain=1e-9,
            radius=0.01,
            changes={"candidate": {"kappa_M_C": 0.2, "Lambda_C": 3.0, "tau_C": 0.0}},
        )
        point = CandidateCCurrent(before)
        enclosure = _projector_enclosure(point)
        exact_p = (
            (Fraction(5, 6), Fraction(1, 3), Fraction(-1, 6)),
            (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
            (Fraction(-1, 6), Fraction(1, 3), Fraction(5, 6)),
        )
        for row, oracle in zip(enclosure, exact_p, strict=True):
            for interval, x in zip(row, oracle, strict=True):
                self.assertLessEqual(interval.lo, x)
                self.assertGreaterEqual(interval.hi, x)
        trial = CITrial(replace(before, stage="ci_trial", trial_current=point.current))
        with localcontext() as context:
            context.prec = 180
            d = Decimal.from_float
            p = before.geometry.reference.profile.params_resolved.candidate
            selected = [
                sum(
                    Decimal(x.numerator) / Decimal(x.denominator) * d(c)
                    for x, c in zip(row, before.current.C, strict=True)
                )
                for row in exact_p
            ]
            rho = [
                ((2 * x / d(p.C_ref)).exp() - 1) / ((2 * x / d(p.C_ref)).exp() + 1)
                for x in selected
            ]
            retained = [
                2 * (d(p.kappa_M_C) / 2 * (rho[i] + rho[i + 1])).exp() for i in range(2)
            ]
            # The declared tail-positive incidence gives Bt C=(2,-1).
            edge = (2 * retained[0], -retained[1])
            baseline = [
                -d(p.eta_C) * 2 * d(p.kappa_Phi_C) * (2 * edge[0] - edge[1]),
                -d(p.eta_C) * 2 * d(p.kappa_Phi_C) * (-edge[0] + 2 * edge[1]),
            ]
            flat = [d(p.chi_C) * d(j) / 2 for j in point.current.values]
            fj = [
                Fraction(d(j) - j0 - d(p.zeta_C) * d(p.chi_C) * d(j))
                for j, j0 in zip(point.current.values, baseline, strict=True)
            ]
            fh = [
                [
                    Fraction(
                        -d(
                            before.geometry.reference.profile.params_resolved.geometry.kappa_H
                        )
                        * d(p.zeta_C)
                        * flat[i]
                        * flat[k]
                        * (1 if i == k else Decimal(".5"))
                    )
                    for k in range(2)
                ]
                for i in range(2)
            ]
        for interval, x in zip(trial.analytic_current_residual, fj, strict=True):
            self.assertLessEqual(interval.lo, x)
            self.assertGreaterEqual(interval.hi, x)
        for row, oracle in zip(trial.analytic_geometry_residual, fh, strict=True):
            for interval, x in zip(row, oracle, strict=True):
                self.assertLessEqual(interval.lo, x)
                self.assertGreaterEqual(interval.hi, x)
        # A wrong subspace with the correct rank cannot be certified merely
        # because a numerical eigensolver produced it.
        forged = copy(point)
        algebra, selector = copy(point.algebra), copy(point.algebra.selector)
        object.__setattr__(
            selector, "projector", ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0))
        )
        object.__setattr__(algebra, "selector", selector)
        object.__setattr__(forged, "algebra", algebra)
        with self.assertRaises(CIStageError):
            _projector_enclosure(forged)

    def test_scalar_root_against_decimal_bisection(self):
        before, backend = fixture()
        root = CandidateCIRoot(before, backend)
        j, h = scalar_c_bisection(before)
        self.assertGreater(root.evaluations, 1)
        self.assertAlmostEqual(root.current.values[0], j, delta=2e-10)
        self.assertAlmostEqual(
            root.selected.inputs.geometry.one_form_hodge.matrix[0][0], h, delta=1e-11
        )
        self.assertLess(root.selected.residual_squared, Fraction(1e-11) ** 2)
        self.assertEqual(root.certificate.bounds["admitted_strata"], 1)

    def test_dense_selector_hodge_and_signed_multigraph(self):
        graph = GRCV4Graph(
            ("a", "b", "c", "isolated"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("ab2", "b", "a"),
                OrientedEdge("bc", "b", "c"),
            ),
        )
        before, backend = fixture(
            graph=graph,
            C=(2.0, 1.0, 3.0, 0.5),
            gain=1e-9,
            radius=0.01,
            changes={
                "candidate": {
                    "kappa_M_C": 0.2,
                    "Lambda_C": 3.0,
                    "chi_C": 0.05,
                    "zeta_C": 0.05,
                }
            },
        )
        root = CandidateCIRoot(before, backend)
        j, h = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, j, rtol=1e-10, atol=1e-11)
        np.testing.assert_allclose(
            root.selected.inputs.geometry.one_form_hodge.matrix,
            h,
            rtol=1e-12,
            atol=1e-11,
        )
        self.assertEqual(root.selected.point.algebra.selector.rank, 3)
        self.assertGreater(
            np.linalg.norm(h - np.array(before.geometry.one_form_hodge.matrix)), 0
        )

    def test_trial_refreshes_entire_chain_and_uses_trial_current(self):
        before, _ = fixture(changes={"candidate": {"kappa_M_C": 0.5}})
        graph = before.geometry.reference.graph
        values = []
        for h in (2.0, 2.05):
            geometry = GRCV4Geometry(
                before.geometry.reference, OneFormHodge(graph, ((h,),))
            )
            trial = CITrial(
                replace(
                    before,
                    geometry=geometry,
                    stage="ci_trial",
                    trial_current=PhysicalFlux(graph, (1.5,)),
                )
            )
            point = trial.point
            self.assertEqual(
                trial.current_residual[0],
                Fraction(1.5)
                - Fraction(point.algebra.baseline.values[0])
                - Fraction(0.25)
                * Fraction(point.read_back(trial.inputs.trial_current).flux.values[0]),
            )
            values.append(
                (
                    point.algebra.retained_hodge.matrix,
                    point.algebra.baseline.values,
                    point.algebra.response,
                )
            )
        for a, b in zip(*values, strict=True):
            self.assertNotEqual(a, b)

    def test_selector_boundary_and_singular_current_fail(self):
        before, _ = fixture(changes={"candidate": {"Lambda_C": 4.0}})
        with self.assertRaisesRegex(CandidateCStageError, "exact spectrum"):
            CandidateCIRoot(before)
        before, _ = fixture(
            changes={"candidate": {"tau_C": 0.0, "chi_C": 1.0, "zeta_C": 1.0}}
        )
        with self.assertRaises(CandidateCStageError):
            CandidateCIRoot(before)


class CandidateACITests(unittest.TestCase):
    def test_exact_descriptors_and_mobility_feed_the_analytic_residual(self):
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")),
        )
        before, backend = fixture(
            "A",
            graph=graph,
            C=(3.0, 1.0, 2.0),
            W=(1.1, 0.7),
            changes={
                "candidate": {
                    "eta": 0.1,
                    "alpha": 0.2,
                    "beta": 0.3,
                    "gamma": 0.1,
                    "kappa_Ah": 0.0,
                }
            },
        )
        point = CandidateACurrent(before, backend)
        trial = CITrial(
            replace(before, stage="ci_trial", trial_current=point.current), backend
        )
        with localcontext() as context:
            context.prec = 180
            d = Decimal.from_float
            p = before.geometry.reference.profile.params_resolved.candidate
            # Scalar WLS at the three nodes, including the middle 1/3 which
            # cannot be represented exactly in binary64.
            descriptors = (Decimal(-1), -Decimal(1) / 3, Decimal(1) / 2)
            w = tuple(d(x) for x in before.current.W_A)
            edge = (2 * w[0], -w[1])
            baseline = (
                -d(p.eta) * w[0] * d(p.kappa_c) * (2 * edge[0] - edge[1]),
                -d(p.eta) * w[1] * d(p.kappa_c) * (-edge[0] + 2 * edge[1]),
            )
            for i, j0 in enumerate(baseline):
                exponent = (
                    -(
                        d(p.alpha) * d(before.current.C[i] + before.current.C[i + 1])
                        + d(p.beta) * (descriptors[i] - descriptors[i + 1]) ** 2
                        + d(p.gamma) * j0 * j0
                    )
                    / 2
                )
                target = exponent.exp()
                q = (w[i] - target) / (w[i] + target)
                j = d(point.current.values[i])
                expected = Fraction(j - j0 - d(p.zeta_A) * d(p.chi_A) * q * j)
                interval = trial.analytic_current_residual[i]
                self.assertLessEqual(interval.lo, expected)
                self.assertGreaterEqual(interval.hi, expected)

    def test_nonneutral_root_matches_independent_equations(self):
        before, backend = fixture("A", gain=0.01)
        root = CandidateCIRoot(before, backend)
        j, h = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, j, rtol=1e-10, atol=1e-11)
        np.testing.assert_allclose(
            root.selected.inputs.geometry.one_form_hodge.matrix,
            h,
            rtol=1e-10,
            atol=1e-11,
        )
        self.assertGreater(root.evaluations, 1)
        self.assertNotEqual(
            root.selected.point.W_hat_A, CandidateACurrent(before, backend).W_hat_A
        )

    def test_each_trial_rebuilds_baseline_target_and_contrast(self):
        before, backend = fixture("A")
        graph = before.geometry.reference.graph
        values = []
        for h in (1.0, 1.05):
            trial = CITrial(
                replace(
                    before,
                    geometry=GRCV4Geometry(
                        before.geometry.reference, OneFormHodge(graph, ((h,),))
                    ),
                    stage="ci_trial",
                    trial_current=PhysicalFlux(graph, (0.3,)),
                ),
                backend,
            )
            point = trial.point
            values.append((point.baseline.values, point.W_hat_A, point.contrast_exact))
            self.assertEqual(
                trial.current_residual[0],
                Fraction(0.3)
                - Fraction(point.baseline.values[0])
                - Fraction(0.75)
                * Fraction(point.read_back(trial.inputs.trial_current).flux.values[0]),
            )
        for a, b in zip(*values, strict=True):
            self.assertNotEqual(a, b)

    def test_dense_noncommuting_geometry_and_unequal_retained_weights(self):
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("bc", "b", "c"),
                OrientedEdge("ca", "c", "a"),
            ),
        )
        before, backend = fixture(
            "A",
            graph=graph,
            C=(2.0, 1.0, 3.0),
            W=(2.0, 0.5, 1.5),
            gain=1e-5,
            radius=0.05,
        )
        root = CandidateCIRoot(before, backend)
        j, h = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, j, rtol=1e-9, atol=1e-10)
        np.testing.assert_allclose(
            root.selected.inputs.geometry.one_form_hodge.matrix,
            h,
            rtol=1e-10,
            atol=1e-11,
        )
        self.assertGreater(abs(h[0, 1]), 0)

    def test_exact_singular_diagonal_even_with_zero_right_hand_side(self):
        before, backend = fixture(
            "A",
            C=(0.0, 0.0),
            W=(2.0,),
            changes={"candidate": {"gamma": 0.0, "chi_A": 1.0, "zeta_A": 3.0}},
        )
        with self.assertRaisesRegex(CandidateAStageError, "singular"):
            CandidateCIRoot(before, backend)

    def test_floor_crossing_is_rejected_but_active_floor_is_admitted(self):
        before, backend = fixture(
            "A", changes={"candidate": {"W_floor": math.exp(-0.2)}}
        )
        with self.assertRaisesRegex(CIStageError, "floor chart"):
            CandidateCIRoot(before, backend)
        before, backend = fixture("A", changes={"candidate": {"W_floor": 2.0}})
        root = CandidateCIRoot(before, backend)
        self.assertEqual(root.certificate.bounds["floor_charts"], ("floor_active",))
        self.assertEqual(root.current, root.selected.point.baseline)

    def test_signed_exponential_coefficient_and_negative_geometry_gain(self):
        before, backend = fixture(
            "A", gain=-0.001, changes={"candidate": {"gamma": -0.1}}
        )
        root = CandidateCIRoot(before, backend)
        j, h = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, j, rtol=1e-10, atol=1e-11)
        self.assertLess(h[0, 0], 1.0)
        np.testing.assert_allclose(
            root.selected.inputs.geometry.one_form_hodge.matrix,
            h,
            rtol=1e-10,
            atol=1e-11,
        )


class CISharedTests(unittest.TestCase):
    def test_irrational_loop_edge_overlap_is_enclosed_before_source_rounding(self):
        graph = GRCV4Graph(
            ("u", "v"), (OrientedEdge("loop", "u", "u"), OrientedEdge("uv", "u", "v"))
        )
        before, _ = fixture("C", graph=graph, changes={"candidate": {"tau_C": 0.0}})
        trial = CITrial(
            replace(
                before, stage="ci_trial", trial_current=PhysicalFlux(graph, (1.0, 1.0))
            )
        )
        p = before.geometry.reference.profile.params_resolved
        with localcontext() as context:
            context.prec = 180
            d = Decimal.from_float
            expected = Fraction(
                -d(p.geometry.kappa_H)
                * d(p.candidate.zeta_C)
                * (d(p.candidate.chi_C) / 2) ** 2
                / Decimal(2).sqrt()
            )
        interval = trial.analytic_geometry_residual[0][1]
        self.assertLessEqual(interval.lo, expected)
        self.assertGreaterEqual(interval.hi, expected)
        self.assertNotEqual(trial.geometry_residual[0][1], expected)

    def test_large_rounded_fixed_points_must_meet_analytic_absolute_tolerance(self):
        graph = GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))
        href = 2.0**100
        h = math.nextafter(href, math.inf)
        for candidate in ("A", "C"):
            if candidate == "A":
                before, backend = a_fixture(
                    graph=graph,
                    weights={"e": href},
                    C=(29 / 8, 1.0),
                    W=(2.0,),
                    gamma=0.0,
                    kappa_Ah=0.0,
                )
                gain, j = 2.0**250, -3.0
                defect = (
                    Fraction(h)
                    - Fraction(href)
                    - Fraction(3, 16) * Fraction(gain) / Fraction(h) ** 2
                )
            else:
                before = c_fixture(
                    graph=graph,
                    weights={"e": href},
                    resource=(3.0, 1.0),
                    changes={
                        "candidate": {
                            "kappa_M_C": 0.0,
                            "eta_C": 2.0**-100,
                            "kappa_Phi_C": 2.0**-101,
                            "tau_C": 0.0,
                            "chi_C": 0.25,
                            "zeta_C": 2.0,
                            "Lambda_C": href,
                        }
                    },
                )
                backend, gain, j = None, 3 * 2.0**245, -4 * h / href
                defect = Fraction(2**46)
            before = configure(before, radius=2.0**60, gain=gain, limit=5)
            CIContractionCertificate(before, backend)
            trial = CITrial(
                replace(
                    before,
                    stage="ci_trial",
                    trial_current=PhysicalFlux(graph, (j,)),
                    geometry=GRCV4Geometry(
                        before.geometry.reference, OneFormHodge(graph, ((h,),))
                    ),
                ),
                backend,
            )
            self.assertEqual(trial.generated, trial.inputs.geometry)
            self.assertGreater(abs(trial.geometry_residual[0][0]), Fraction(2**45))
            interval = trial.analytic_geometry_residual[0][0]
            self.assertLessEqual(interval.lo, defect)
            self.assertGreaterEqual(interval.hi, defect)
            self.assertGreaterEqual(trial.residual_squared, defect**2)
            with self.assertRaises(CIStageError) as caught:
                CandidateCIRoot(before, backend)
            self.assertEqual(caught.exception.disposition, "no_admitted_root")
            if candidate == "C":
                # The exact defect is representable: equality passes; the next
                # smaller tolerance fails. No implicit scale or tolerance floor.
                for tolerance in (math.nextafter(2.0**46, 0.0), 2.0**46):
                    changed = configure(
                        before, radius=2.0**60, gain=gain, limit=5, tolerance=tolerance
                    )
                    if tolerance < 2.0**46:
                        with self.assertRaises(CIStageError):
                            CandidateCIRoot(changed)
                    else:
                        self.assertEqual(
                            CandidateCIRoot(changed).selected.residual_squared,
                            defect**2,
                        )

    def test_real_exponential_residual_includes_ordinary_rounding(self):
        before, backend = fixture("A", changes={"candidate": {"kappa_Ah": 0.0}})
        point = CandidateACurrent(before, backend)
        trial = CITrial(
            replace(before, stage="ci_trial", trial_current=point.current), backend
        )
        p = before.geometry.reference.profile.params_resolved.candidate
        with localcontext() as context:
            context.prec = 180
            d = Decimal.from_float
            target = (-d(p.gamma) * 4 / 2).exp()
            q = (2 - target) / (2 + target)
            j = d(point.current.values[0])
            exact_j = Fraction(j + 2 - d(p.zeta_A) * d(p.chi_A) * q * j)
            exact_h = Fraction(
                -d(before.geometry.reference.profile.params_resolved.geometry.kappa_H)
                * d(p.zeta_A)
                * (d(p.chi_A) * q * j) ** 2
            )
        for interval, oracle in (
            (trial.analytic_current_residual[0], exact_j),
            (trial.analytic_geometry_residual[0][0], exact_h),
        ):
            self.assertLessEqual(interval.lo, oracle)
            self.assertGreaterEqual(interval.hi, oracle)
        self.assertNotEqual(trial.current_residual[0], exact_j)

    def test_interval_inverse_and_saturation_enclose_independent_values(self):
        # Exact rational inverse samples challenge the whole interval matrix;
        # the production inverse never uses these sample values as its proof.
        box = (
            (_Interval(Fraction(2), Fraction(21, 10)), _iv(Fraction(1, 4))),
            (_iv(Fraction(1, 4)), _Interval(Fraction(3), Fraction(31, 10))),
        )
        inverse = _iinverse(box)
        for a in (Fraction(2), Fraction(41, 20), Fraction(21, 10)):
            for b in (Fraction(3), Fraction(61, 20), Fraction(31, 10)):
                det = a * b - Fraction(1, 16)
                expected = (
                    (b / det, -Fraction(1, 4) / det),
                    (-Fraction(1, 4) / det, a / det),
                )
                for row, other in zip(inverse, expected, strict=True):
                    for interval, x in zip(row, other, strict=True):
                        self.assertLessEqual(interval.lo, x)
                        self.assertGreaterEqual(interval.hi, x)
        with self.assertRaises(CIStageError):
            _iinverse(((_Interval(Fraction(-1), Fraction(1)),),))
        with localcontext() as context:
            context.prec = 520
            for q in (
                Fraction(-600),
                Fraction(-1, 10),
                Fraction(),
                Fraction(1, 10),
                Fraction(600),
            ):
                interval = _itanh(_iv(q))
                exp = (2 * Decimal(q.numerator) / Decimal(q.denominator)).exp()
                expected = Fraction((exp - 1) / (exp + 1))
                self.assertLessEqual(interval.lo, expected)
                self.assertGreaterEqual(interval.hi, expected)

    def test_two_positive_roots_selects_only_the_declared_reference_ball(self):
        before, backend = fixture(
            "A",
            gain=-147 / 2048,
            changes={"candidate": {"gamma": 0.0, "kappa_Ah": 0.0}},
        )
        with localcontext() as context:
            context.prec = 100

            def f(h):
                return h**3 - h**2 + Decimal(1) / 128

            roots = []
            for lo, hi in ((Decimal(0), Decimal(".5")), (Decimal(".5"), Decimal(1))):
                for _ in range(200):
                    mid = (lo + hi) / 2
                    if f(lo) * f(mid) <= 0:
                        hi = mid
                    else:
                        lo = mid
                roots.append(float((lo + hi) / 2))
        root = CandidateCIRoot(before, backend)
        self.assertAlmostEqual(
            root.selected.inputs.geometry.one_form_hodge.matrix[0][0],
            roots[1],
            delta=1e-11,
        )
        ref = before.geometry.reference
        with self.assertRaisesRegex(CIStageError, "outside"):
            CITrial(
                replace(
                    root.selected.inputs,
                    geometry=GRCV4Geometry(
                        ref, OneFormHodge(ref.graph, ((roots[0],),))
                    ),
                ),
                backend,
            )

    def test_exact_contraction_equality_and_adjacent_pass(self):
        # J=-16/7, q=1/3; on h in [1/2,3/2], R=16/21,
        # L_R=32/21, so L_T=(256/147)*kappa_H. At equality
        # the displacement bound is only 1/4: it is not the rejecting guard.
        threshold = 147 / 256
        for gain in (threshold, math.nextafter(threshold, math.inf)):
            before, backend = fixture(
                "A",
                radius=0.5,
                gain=gain,
                changes={"candidate": {"gamma": 0.0, "kappa_Ah": 0.0}},
            )
            with self.assertRaisesRegex(CIStageError, "strictly below"):
                CIContractionCertificate(before, backend)
        before, backend = fixture(
            "A",
            radius=0.5,
            gain=math.nextafter(threshold, 0.0),
            changes={"candidate": {"gamma": 0.0, "kappa_Ah": 0.0}},
        )
        certificate = CIContractionCertificate(before, backend)
        self.assertLess(Fraction(certificate.bounds["contraction_upper"]), 1)

    def test_joint_residual_keeps_subnormal_and_huge_defects(self):
        before, backend = fixture(
            "A", C=(0.0, 0.0), W=(1.0,), changes={"candidate": {"chi_A": 0.0}}
        )
        graph = before.geometry.reference.graph
        for j in (5e-324, 1e308):
            trial = CITrial(
                replace(
                    before, stage="ci_trial", trial_current=PhysicalFlux(graph, (j,))
                ),
                backend,
            )
            self.assertEqual(trial.residual_squared, Fraction(j) ** 2)
            self.assertGreater(trial.residual_squared, 0)

    def test_loops_and_isolates_and_explicit_empty_edge_rejection(self):
        loop = GRCV4Graph(("u", "isolated"), (OrientedEdge("loop", "u", "u"),))
        for candidate in ("C", "A"):
            before, backend = fixture(candidate, graph=loop, C=(1.0, 2.0))
            root = CandidateCIRoot(before, backend)
            self.assertEqual(root.current.values, (0.0,))
            self.assertEqual(root.selected.inputs.geometry, before.geometry)
            graph = GRCV4Graph(("isolated",), ())
            with self.assertRaisesRegex(V4SchemaError, "non-empty"):
                fixture(candidate, graph=graph, C=(1.0,), W=())

    def test_extreme_positive_A_history_is_never_clamped(self):
        for weight in (5e-324, 1e308):
            before, backend = fixture(
                "A",
                C=(0.0, 0.0),
                W=(weight,),
                changes={"candidate": {"eta": 1.0, "gamma": 0.0}},
            )
            root = CandidateCIRoot(before, backend)
            self.assertEqual(root.selected.point.authority.state.W_A, (weight,))
            self.assertEqual(root.current.values, (0.0,))

    def test_root_orientation_covariance_in_both_candidates(self):
        reversed_graph = GRCV4Graph(("u", "v"), (OrientedEdge("e", "v", "u"),))
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            reverse, other = fixture(candidate, graph=reversed_graph)
            original, flipped = (
                CandidateCIRoot(before, backend),
                CandidateCIRoot(reverse, other),
            )
            self.assertEqual(
                flipped.current.values, tuple(-x for x in original.current.values)
            )
            self.assertEqual(
                flipped.selected.inputs.geometry.one_form_hodge.matrix,
                original.selected.inputs.geometry.one_form_hodge.matrix,
            )

    def test_ball_certificate_is_stronger_than_a_reference_residual(self):
        before, backend = fixture("A", gain=100.0)
        with self.assertRaisesRegex(CIStageError, "self-map|contraction"):
            CIContractionCertificate(before, backend)
        # A perfect rounded residual must not bypass the certificate.
        with patch.object(CITrial, "residual_squared", new=Fraction()):
            with self.assertRaises(CIStageError):
                CandidateCIRoot(before, backend)

    def test_exact_enclosures_cover_independent_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 240
            for x in (-1000.0, -20.0, -0.01, 0.0, 0.01, 0.5, 1.0, 20.0, 700.0):
                lo, hi = _exp_bounds(Fraction(x))
                expected = Decimal.from_float(x).exp()
                self.assertLessEqual(
                    Decimal(lo.numerator) / Decimal(lo.denominator), expected
                )
                self.assertGreaterEqual(
                    Decimal(hi.numerator) / Decimal(hi.denominator), expected
                )
            for x in (Fraction(5e-324) ** 2, Fraction(2), Fraction(1e308) ** 2):
                self.assertGreaterEqual(_sqrt_upper(x) ** 2, x)

    def test_roundtrip_preserves_selected_root_and_has_no_workspace_authority(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            root = CandidateCIRoot(before, backend)
            restored = CandidateCIRoot.from_payload(root.to_payload())
            self.assertEqual(restored.identity, root.identity)
            self.assertEqual(restored.current, root.current)
            payload = root.to_payload()
            payload["previous_root"] = root.current.values
            with self.assertRaises(ValueError):
                CandidateCIRoot.from_payload(payload)
            with self.assertRaises(FrozenInstanceError):
                root.evaluations = 999

    def test_iteration_budget_is_failure_even_when_root_exists(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate, limit=1, tolerance=0.0)
            with self.assertRaisesRegex(CIStageError, "iteration limit") as caught:
                CandidateCIRoot(before, backend)
            self.assertEqual(caught.exception.disposition, "no_admitted_root")

    def test_domain_and_solver_ids_cannot_select_hidden_fallbacks(self):
        for changes in (
            {"realization": {"contraction_domain_id": "previous_root_branch"}},
            {"realization": {"residual_norm_id": "edge_l2_v1"}},
            {"solver": {"iteration_limit": 1}},
            {"identity": {"solver_id": "direct_unique_root_v1"}},
        ):
            before, backend = fixture(changes=changes)
            with self.assertRaises(CIStageError):
                CandidateCIRoot(before, backend)

    def test_spd_and_whole_ball_gap_are_checked_before_iteration(self):
        before, _ = fixture(radius=2.0)
        with self.assertRaisesRegex(CIStageError, "SPD"):
            CandidateCIRoot(before)
        before, _ = fixture(radius=0.125, changes={"candidate": {"Lambda_C": 3.9}})
        with self.assertRaisesRegex(CIStageError, "stratum"):
            CandidateCIRoot(before)

    def test_disconnected_seed_and_outside_trial_are_rejected(self):
        before, backend = fixture("A")
        graph = before.geometry.reference.graph
        foreign = replace(
            before,
            geometry=GRCV4Geometry(
                before.geometry.reference, OneFormHodge(graph, ((2.0,),))
            ),
        )
        with self.assertRaisesRegex(CIStageError, "reference pre-read"):
            CandidateCIRoot(foreign, backend)
        with self.assertRaisesRegex(CIStageError, "outside"):
            CITrial(
                replace(
                    foreign, stage="ci_trial", trial_current=PhysicalFlux(graph, (1.0,))
                ),
                backend,
            )

    def test_zero_source_controls_keep_reference_exact(self):
        for candidate in ("A", "C"):
            for control in ("chi", "zeta", "gain"):
                params = (
                    {}
                    if control == "gain"
                    else {"candidate": {control + "_" + candidate: 0.0}}
                )
                before, backend = fixture(
                    candidate,
                    gain=0.0 if control == "gain" else 1e-5,
                    changes=params,
                    tolerance=1e-11,
                )
                root = CandidateCIRoot(before, backend)
                self.assertEqual(root.selected.inputs.geometry, before.geometry)
                self.assertEqual(root.evaluations, 1)


class CIStepTests(unittest.TestCase):
    def test_consumed_root_failure_follows_successful_reset_admission(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, limit=1, tolerance=0.0)
            reset = GRCV4AuthoritativeState((2.0, 2.0), before.current.W_A, None)
            before = replace(before, reset=reset)
            original = before.to_payload()
            self.assertEqual(
                CandidateCIRoot(replace(before, current=reset), backend).evaluations, 1
            )
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(
                (caught.exception.stage, caught.exception.code),
                ("candidate_solve", "no_admitted_root"),
            )
            self.assertEqual(before.to_payload(), original)

    def test_writer_policy_is_admitted_before_any_zero_or_positive_root(self):
        from pygrc.models import grc_v4_ci as ci

        before, backend = fixture(
            "A", changes={"lifecycle": {"history_policy_id": "unknown_writer_v1"}}
        )
        # Root-only use has no transition responsibility.
        CandidateCIRoot(before, backend)
        for dt in (0.0, 2**-14):
            inputs = replace(before, dt=dt)
            original = inputs.to_payload()
            with patch.object(ci, "CandidateCIRoot", wraps=CandidateCIRoot) as roots:
                with self.assertRaisesRegex(ValueError, "writer policy"):
                    ProvisionalCandidateCIStep(inputs, backend)
                self.assertEqual(roots.call_count, 0)
            self.assertEqual(inputs.to_payload(), original)

    def test_final_regular_current_still_requires_CI_self_map_admission(self):
        before, backend = fixture(
            "A",
            W=(0.1,),
            gain=1000.0,
            changes={"candidate": {"gamma": 0.0, "kappa_Ah": 0.0}},
        )
        before = replace(before, dt=1.0)
        root = CandidateCIRoot(before, backend)
        selection = CurrentSelection(root.selected.inputs, "valid_root", root.current)
        resource = ProvisionalResourceStep(before, selection)
        writer = CandidateAWriter(root.selected.point, resource)
        after = replace(before, current=writer.authority.state, dt=0.0)
        # This succeeds: the rejecting postcondition is specifically CI's
        # bounded self-map, not a singular current or nonpositive history.
        CandidateACurrent(after, backend)
        with self.assertRaisesRegex(CIStageError, "self-map"):
            CIContractionCertificate(after, backend)
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(
            (caught.exception.stage, caught.exception.code),
            ("final_reconstruction", "domain_failure"),
        )
        self.assertEqual(before.to_payload(), original)

    def test_postwriter_current_failure_has_no_partial_result(self):
        before, backend = fixture(
            "A",
            C=(0.0, 0.0),
            W=(4.0,),
            changes={"candidate": {"gamma": 0.0, "chi_A": 1.0, "zeta_A": 3.0}},
        )
        before = replace(before, dt=math.log(2.0))
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(caught.exception.stage, "final_reconstruction")
        self.assertEqual(caught.exception.code, "singular_solver")
        self.assertEqual(before.to_payload(), original)

    def test_writer_runs_once_and_stale_trial_cannot_supply_it(self):
        before, backend = fixture("A")
        with patch(
            "pygrc.models.grc_v4_ci.CandidateAWriter", wraps=CandidateAWriter
        ) as writer:
            step = ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(writer.call_count, 1)
        point = step.root.selected.point
        bad = replace(
            point,
            inputs=replace(
                point.inputs, trial_current=PhysicalFlux(point.current.graph, (0.0,))
            ),
        )
        with self.assertRaisesRegex(ValueError, "selected root current"):
            CandidateAWriter(bad, step.resource)

    def test_clock_and_charge_fail_before_state_is_published(self):
        before, backend = fixture("A")
        for changes in (
            {"step_index": 2**53 - 1},
            {"time": 1e308, "dt": 1e308},
            {"Q_target": 1.0},
        ):
            bad = replace(before, **changes)
            original = bad.to_payload()
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateCIStep(bad, backend)
            self.assertEqual(caught.exception.stage, "admission")
            self.assertEqual(bad.to_payload(), original)

    def test_one_continuity_and_only_A_has_writer(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            step = ProvisionalCandidateCIStep(before, backend)
            expected = np.array(before.current.C) - before.dt * np.array(
                before.geometry.reference.graph.incidence
            ) @ np.array(step.root.current.values)
            np.testing.assert_allclose(
                step.next_inputs.current.C, expected, rtol=0, atol=2e-15
            )
            self.assertEqual(step.resource.continuity_evaluations, 1)
            self.assertEqual(step.next_inputs.step_index, before.step_index + 1)
            self.assertEqual(step.next_inputs.reset, before.reset)
            self.assertEqual(step.writer is None, candidate == "C")
            self.assertEqual(step.root.inputs.current, before.current)
            if step.writer is not None:
                expected = log_writer_oracle(
                    before.current.W_A,
                    step.writer.W_drv_A,
                    before.dt,
                    before.geometry.reference.profile.params_resolved.candidate.tau_A,
                )
                np.testing.assert_allclose(
                    step.next_inputs.current.W_A, expected, rtol=2e-15, atol=0
                )

    def test_zero_duration_is_temporal_identity(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            before = replace(before, dt=0.0)
            step = ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(step.next_inputs, before)
            self.assertIsNone(step.writer)
            self.assertIsNone(step.resource.selection)
            self.assertEqual(step.resource.continuity_evaluations, 0)

    def test_failed_root_and_reset_leave_complete_inputs_unchanged(self):
        before, backend = fixture("A", limit=1, tolerance=0.0)
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError):
            ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(before.to_payload(), original)
        before, backend = fixture(
            "A",
            C=(0.0, 0.0),
            W=(1.0,),
            changes={"candidate": {"gamma": 0.0, "chi_A": 1.0, "zeta_A": 3.0}},
        )
        before = replace(
            before, reset=GRCV4AuthoritativeState((0.0, 0.0), (2.0,), None)
        )
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
        self.assertEqual(before.to_payload(), original)

    def test_step_roundtrip_and_no_public_support_promotion(self):
        before, backend = fixture("A")
        step = ProvisionalCandidateCIStep(before, backend)
        restored = ProvisionalCandidateCIStep.from_payload(step.to_payload())
        self.assertEqual(restored.next_inputs, step.next_inputs)
        self.assertEqual(len(list_supported_profiles()), 1)
