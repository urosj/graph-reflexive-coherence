"""Independent RG2b completion, section error and native candidate pressure."""

from dataclasses import replace
from fractions import Fraction
import math
from decimal import Decimal, localcontext
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4_rg2b import (
    RG2bDomain,
    RG2bCertificate,
    CandidateRG2bSection,
    APPROXIMATION,
    ERROR_NORM,
    CONTAINMENT,
    RG2bStageError,
    ProvisionalCandidateRG2bStep,
)
import pygrc.models.grc_v4_rg2b as rg
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from tests.models.test_grc_v4_candidate_a import current_fixture as a_fixture
from tests.models.test_grc_v4_candidate_c import current_fixture as c_fixture
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_ci import configure as ci_configure, independent_point
from pygrc.models.grc_v4_ci import CandidateCIRoot
from pygrc.models.grc_v4_step import ResourceBoundaryError
from pygrc.models.grc_v4_candidate_a import CandidateACurrent, CandidateAStageError
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from pygrc.models.grc_v4_step import CurrentSelection, ProvisionalResourceStep


def fixture(
    candidate="C",
    *,
    domain=None,
    C=(2.125, 1.875),
    W=(2.125,),
    gain=2**-20,
    tolerance=2**-36,
    limit=4000,
    changes=None,
    graph=None,
    weights=None,
):
    d = domain or RG2bDomain(
        2.0, 2.0 if candidate == "A" else 1.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-16
    )
    graph = graph or GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))
    if candidate == "A":
        raw, backend = a_fixture(
            graph=graph,
            C=C,
            W=W,
            weights=weights,
            dt=d.beat_dt,
            eta=0.125,
            kappa_c=0.25,
            kappa_Ah=0.125,
            alpha=0.125,
            beta=0.25,
            gamma=0.0625,
            chi_A=0.125,
            zeta_A=0.125,
        )
    else:
        raw = c_fixture(
            graph=graph,
            resource=C,
            weights=weights,
            changes={
                "candidate": {
                    "eta_C": 0.125,
                    "kappa_Phi_C": 0.25,
                    "kappa_M_C": 0.125,
                    "tau_C": 0.125,
                    "chi_C": 0.125,
                    "zeta_C": 0.125,
                    "Lambda_C": 0.5,
                }
            },
        )
        raw, backend = replace(raw, dt=d.beat_dt), None
    ref = raw.geometry.reference
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["realization"] = dict(
        schema_version="grcv4-rg2b-params-v1",
        extension_evaluator_id=d.identity,
        approximation_policy_id=APPROXIMATION,
        error_norm_id=ERROR_NORM,
        error_tolerance=tolerance,
        containment_certificate_id=CONTAINMENT,
        iteration_limit=limit,
        failure_policy_id="fail_closed_on_uncertified_section_v1",
    )
    params["geometry"]["kappa_H"] = gain
    params["solver"].update(solver_kind="direct", conditioning_limit=1e8)
    identity.update(
        realization="RG2b",
        profile_family_id=candidate + "_RG2b",
        solver_id="direct_unique_root_v1",
    )
    for group, values in (changes or {}).items():
        params[group].update(values)
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(raw, geometry=ref.geometry()), backend


class RG2bCertificateTests(unittest.TestCase):
    def test_candidate_specific_nonzero_coupling_certificates(self):
        for candidate in ("C", "A"):
            with self.subTest(candidate=candidate):
                before, backend = fixture(candidate)
                cert = RG2bCertificate(before, backend)
                self.assertGreater(Fraction(cert.bounds["contraction_upper"]), 0)
                self.assertLess(Fraction(cert.bounds["contraction_upper"]), 1)
                section = CandidateRG2bSection(before, backend)
                self.assertLessEqual(
                    Fraction(section.error_upper),
                    Fraction(
                        before.geometry.reference.profile.params_resolved.realization.error_tolerance
                    ),
                )
                self.assertNotEqual(section.geometry, before.geometry)

    def test_nested_charts_and_canonical_identity(self):
        d = RG2bDomain(2.0, 2.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-16)
        self.assertEqual(RG2bDomain.from_identity(d.identity), d)
        for changes in (
            {"inner": 0.5},
            {"outer": 2.0},
            {"beat_dt": 0.0},
            {"section_lipschitz": 0.0},
        ):
            with self.assertRaises(RG2bStageError):
                replace(d, **changes)
        for value in (True, math.nan, math.inf, -0.0):
            with self.assertRaises((TypeError, ValueError)):
                replace(d, inner=value)
        with self.assertRaises(RG2bStageError):
            RG2bDomain.from_identity(
                d.identity.replace("0x1.0000000000000p+1", "0x1p+1")
            )

    def test_evaluator_norm_containment_and_failure_ids_are_bound(self):
        for candidate in ("C", "A"):
            for key in (
                "extension_evaluator_id",
                "approximation_policy_id",
                "error_norm_id",
                "containment_certificate_id",
            ):
                before, backend = fixture(
                    candidate, changes={"realization": {key: "unimplemented"}}
                )
                with self.assertRaises(RG2bStageError):
                    CandidateRG2bSection(before, backend)

    def test_declared_positive_beat_cannot_change_between_queries(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            bad = replace(before, dt=math.nextafter(before.dt, math.inf))
            with self.assertRaisesRegex(RG2bStageError, "beat differs"):
                CandidateRG2bSection(bad, backend)
            zero = CandidateRG2bSection(replace(before, dt=0), backend)
            self.assertEqual(
                zero.geometry, CandidateRG2bSection(before, backend).geometry
            )

    def test_uniform_inverse_containment_value_and_lipschitz_failures(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            d = RG2bDomain.from_identity(
                before.geometry.reference.profile.params_resolved.realization.extension_evaluator_id
            )
            cases = [
                (replace(d, beat_dt=0.25), "invertible"),
                (replace(d, inner=math.nextafter(d.core, 0)), "containment"),
                (replace(d, h_radius=1e-30), "value radius"),
                (replace(d, section_lipschitz=1e-30), "Lipschitz self-map"),
            ]
            for domain, reason in cases:
                with self.subTest(candidate=candidate, reason=reason):
                    inputs, backend = fixture(candidate, domain=domain)
                    with self.assertRaisesRegex(RG2bStageError, reason):
                        RG2bCertificate(inputs, backend)

    def test_source_bounds_are_whole_chart_not_submitted_equilibrium(self):
        for candidate in ("C", "A"):
            d = RG2bDomain(
                2.0,
                2.0 if candidate == "A" else 1.0,
                0.25,
                0.5,
                0.75,
                1e-30,
                0.0625,
                2**-16,
            )
            before, backend = fixture(candidate, domain=d, C=(2.0, 2.0))
            with self.assertRaisesRegex(RG2bStageError, "value radius"):
                RG2bCertificate(before, backend)

    def test_selector_cutoff_and_hodge_boundaries(self):
        before, _ = fixture("C")
        href = before.geometry.one_form_hodge.matrix[0][0]
        for cutoff in (0.0, 2 * href):
            before, _ = fixture("C", changes={"candidate": {"Lambda_C": cutoff}})
            with self.assertRaises((RG2bStageError, ValueError)):
                RG2bCertificate(before)
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            d = RG2bDomain.from_identity(
                before.geometry.reference.profile.params_resolved.realization.extension_evaluator_id
            )
            d = replace(d, h_radius=before.geometry.one_form_hodge.matrix[0][0])
            before, backend = fixture(candidate, domain=d)
            with self.assertRaisesRegex(RG2bStageError, "Hodge ball"):
                RG2bCertificate(before, backend)

    def test_A_floor_is_not_a_permitted_nonsmooth_candidate_chart(self):
        before, backend = fixture("A", changes={"candidate": {"W_floor": 0.9}})
        with self.assertRaisesRegex(RG2bStageError, "floor chart"):
            RG2bCertificate(before, backend)

    def test_extended_maps_are_identity_and_reference_outside_compact_support(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            cert = RG2bCertificate(before, backend)
            x = rg._coordinates(before, before.current)
            for sign in (-1, 1):
                outside = (
                    Fraction(cert.domain.center_C) + sign * Fraction(cert.domain.outer),
                    *x[1:],
                )
                f, g = rg._extended(
                    cert, outside, rg._iv(before.geometry.one_form_hodge.matrix[0][0])
                )
                self.assertTrue(all(v.lo == v.hi == 0 for v in f))
                self.assertEqual((g.lo, g.hi), (0, 0))
            inside = (Fraction(2),) * 2 + ((Fraction(2),) if candidate == "A" else ())
            h = rg._iv(before.geometry.one_form_hodge.matrix[0][0])
            f, g = rg._extended(cert, inside, h)
            raw_f, raw_g, _ = rg._raw(
                before,
                cert.domain,
                cert.selector_rank,
                [rg._Jet(rg._iv(v)) for v in (*inside, h)],
            )
            self.assertEqual(f, [v.value for v in raw_f])
            self.assertEqual(g, raw_g.value)

    def test_cutoff_joins_and_exact_adjacent_boundary(self):
        d = RG2bDomain(2.0, 2.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-16)
        self.assertEqual(rg._cutoff(Fraction(2.5), 2.0, d), 1)
        self.assertEqual(rg._cutoff(Fraction(2.75), 2.0, d), 0)
        self.assertGreater(rg._cutoff(Fraction(math.nextafter(2.75, 0)), 2.0, d), 0)
        self.assertLess(rg._cutoff(Fraction(math.nextafter(2.5, math.inf)), 2.0, d), 1)
        for value in (2.55, 2.625, 2.7):
            self.assertEqual(
                rg._cutoff(Fraction(value), 2.0, d),
                rg._cutoff(4 - Fraction(value), 2.0, d),
            )

    def test_log_enclosure_against_independent_high_precision_decimal(self):
        with localcontext() as ctx:
            ctx.prec = 150
            for value in (math.ulp(0.0), 0.125, 0.7, 1.0, 2.0, 17.0, 1e100):
                q = Fraction(value)
                bound = rg._log_point(q)
                expected = Fraction(Decimal.from_float(value).ln())
                self.assertLessEqual(bound.lo, expected)
                self.assertGreaterEqual(bound.hi, expected)

    def test_whole_chart_bounds_against_independent_map_differences(self):
        import numpy as np

        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            cert = RG2bCertificate(before, backend)
            bounds = {k: float(Fraction(v)) for k, v in cert.bounds.items()}
            p = before.geometry.reference.profile.params_resolved.candidate
            href = before.geometry.one_form_hodge.matrix[0][0]

            def maps(x, h):
                current = replace(
                    before.current,
                    C=tuple(x[:2]),
                    W_A=(x[2],) if candidate == "A" else None,
                )
                inputs = replace(before, current=current)
                j, source = independent_point(inputs, backend, np.array([[h]]))
                f = [-before.dt * j[0], before.dt * j[0]]
                if candidate == "A":
                    target = math.exp(-(p.alpha * sum(x[:2]) + p.gamma * j[0] ** 2) / 2)
                    a = math.exp(-before.dt / p.tau_A)
                    f.append(x[2] ** a * target ** (1 - a) - x[2])
                return np.array(f), source[0, 0]

            for sign in (-1, 1):
                x = np.array(
                    [2 + sign * 0.7, 2 - sign * 0.7]
                    + ([2 + sign * 0.7] if candidate == "A" else [])
                )
                h = href + sign * 0.025
                f, g = maps(x, h)
                self.assertLessEqual(np.max(abs(f)), bounds["base_displacement_upper"])
                self.assertLessEqual(abs(g), bounds["source_upper"])
                eps = 2**-16
                df, dg = [], []
                for axis in range(len(x)):
                    delta = np.eye(len(x))[axis] * eps
                    a, b = maps(x + delta, h), maps(x - delta, h)
                    df.append((a[0] - b[0]) / (2 * eps))
                    dg.append((a[1] - b[1]) / (2 * eps))
                self.assertLessEqual(
                    np.max(np.sum(abs(np.array(df)), axis=0)),
                    bounds["base_X_lipschitz"],
                )
                self.assertLessEqual(
                    sum(abs(v) for v in dg), bounds["source_X_lipschitz"]
                )
                a, b = maps(x, h + eps), maps(x, h - eps)
                self.assertLessEqual(
                    np.max(abs(a[0] - b[0])) / (2 * eps),
                    bounds["base_h_lipschitz"] + 1e-10,
                )
                self.assertLessEqual(
                    abs(a[1] - b[1]) / (2 * eps), bounds["source_h_lipschitz"] + 1e-10
                )

    def test_A_zero_descriptor_contrast_is_structural_not_a_beta_ablation(self):
        results = []
        for beta in (0.0, 1e250):
            before, backend = fixture("A", changes={"candidate": {"beta": beta}})
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(step.point.descriptors[0], step.point.descriptors[1])
            results.append(
                (step.section.geometry.one_form_hodge.matrix, step.next_inputs.current)
            )
        self.assertEqual(results[0], results[1])


def strong_fixture(candidate, **kwargs):
    d = RG2bDomain(
        2.0, 2.0 if candidate == "A" else 1.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-10
    )
    return fixture(
        candidate, domain=d, C=(2.25, 1.75), gain=2**-10, tolerance=2**-45, **kwargs
    )


class RG2bSectionTests(unittest.TestCase):
    def test_C_section_against_independent_cubic_preimage_oracle(self):
        before, backend = strong_fixture(
            "C", changes={"candidate": {"tau_C": 0.0, "kappa_M_C": 0.0}}
        )
        section = CandidateRG2bSection(before, backend)
        p = before.geometry.reference.profile.params_resolved.candidate
        with localcontext() as ctx:
            ctx.prec = 100

            def d(x):
                return Decimal.from_float(float(x))

            href = d(before.geometry.one_form_hodge.matrix[0][0])
            kh = d(before.geometry.reference.profile.params_resolved.geometry.kappa_H)
            c = (
                2
                * d(p.eta_C)
                * d(p.W_C_tr["e"])
                * d(p.kappa_Phi_C)
                / (1 - d(p.zeta_C) * d(p.chi_C))
            )
            rate = 2 * d(before.dt) * c
            source = d(p.zeta_C) * (d(p.chi_C) * c) ** 2
            difference = d(before.current.C[0]) - d(before.current.C[1])

            # Gamma_1 is an explicit quadratic. The Gamma_2 preimage solves
            # this monotone cubic, independently of the production inverse.
            def gamma1(x):
                return href + kh * source * (x / (1 + rate * href)) ** 2

            lo, hi = Decimal(0), difference
            for _ in range(220):
                mid = (lo + hi) / 2
                if (1 + rate * gamma1(mid)) * mid < difference:
                    lo = mid
                else:
                    hi = mid
            gamma2 = href + kh * source * ((lo + hi) / 2) ** 2
            tail = (
                Fraction(section.certificate.bounds["section_radius"])
                * Fraction(section.certificate.bounds["contraction_upper"]) ** 2
            )
            actual = Fraction(section.geometry.one_form_hodge.matrix[0][0])
            self.assertLessEqual(
                abs(actual - Fraction(gamma2)),
                Fraction(section.error_upper) + tail + Fraction(1, 10**60),
            )

    def test_A_section_against_independent_explicit_inverse_oracle(self):
        before, backend = strong_fixture(
            "A", changes={"candidate": {"kappa_Ah": 0.0, "alpha": 0.0, "gamma": 0.0}}
        )
        section = CandidateRG2bSection(before, backend)
        p = before.geometry.reference.profile.params_resolved.candidate
        with localcontext() as ctx:
            ctx.prec = 100

            def d(x):
                return Decimal.from_float(float(x))

            href = d(before.geometry.one_form_hodge.matrix[0][0])
            kh = d(before.geometry.reference.profile.params_resolved.geometry.kappa_H)
            a = (-d(before.dt) / d(p.tau_A)).exp()

            def oracle(depth, difference, weight):
                if depth == 0:
                    return href
                old_w = weight ** (1 / a)
                self.assertLess(abs(old_w - 2), Decimal(".5"))
                contrast = (old_w - 1) / (old_w + 1)
                c = (
                    2
                    * d(p.eta)
                    * d(p.kappa_c)
                    * old_w**2
                    / (1 - d(p.zeta_A) * d(p.chi_A) * contrast)
                )
                old_d = difference / (1 + 2 * d(before.dt) * c)
                old_h = oracle(depth - 1, old_d, old_w)
                return (
                    href
                    + kh
                    * d(p.zeta_A)
                    * (d(p.chi_A) * contrast * c * old_d / old_h) ** 2
                )

            depth = section.levels + 1
            expected = oracle(
                depth,
                d(before.current.C[0]) - d(before.current.C[1]),
                d(before.current.W_A[0]),
            )
            tail = (
                Fraction(section.certificate.bounds["section_radius"])
                * Fraction(section.certificate.bounds["contraction_upper"]) ** depth
            )
            actual = Fraction(section.geometry.one_form_hodge.matrix[0][0])
            self.assertLessEqual(
                abs(actual - Fraction(expected)),
                Fraction(section.error_upper) + tail + Fraction(1, 10**60),
            )

    def test_lagged_section_is_distinct_from_same_beat_CI_root(self):
        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate)
            section = CandidateRG2bSection(before, backend)
            ci = ci_configure(before, radius=0.03125, gain=2**-10, tolerance=2**-47)
            root = CandidateCIRoot(ci, backend)
            difference = abs(
                section.geometry.one_form_hodge.matrix[0][0]
                - root.selected.inputs.geometry.one_form_hodge.matrix[0][0]
            )
            self.assertGreater(
                difference, 10 * (float(Fraction(section.error_upper)) + 2**-47)
            )

    def test_precision_refinement_encloses_consistent_section(self):
        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate)
            fine = CandidateRG2bSection(before, backend)
            coarse_before, coarse_backend = fixture(
                candidate,
                gain=2**-10,
                tolerance=2**-28,
                C=before.current.C,
                domain=fine.certificate.domain,
            )
            coarse = CandidateRG2bSection(coarse_before, coarse_backend)
            self.assertLessEqual(
                Fraction(fine.error_upper), Fraction(coarse.error_upper)
            )
            self.assertLessEqual(
                abs(
                    Fraction(fine.geometry.one_form_hodge.matrix[0][0])
                    - Fraction(coarse.geometry.one_form_hodge.matrix[0][0])
                ),
                Fraction(fine.error_upper) + Fraction(coarse.error_upper),
            )

    def test_budget_and_zero_tolerance_fail_without_neutral_fallback(self):
        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate, limit=1)
            with self.assertRaisesRegex(RG2bStageError, "budget"):
                CandidateRG2bSection(before, backend)
            before, backend = fixture(candidate, tolerance=0.0)
            with self.assertRaisesRegex(RG2bStageError, "depth budget"):
                CandidateRG2bSection(before, backend)
            neutral, backend = fixture(candidate, gain=0.0, tolerance=0.0)
            section = CandidateRG2bSection(neutral, backend)
            self.assertEqual(section.geometry, neutral.geometry)
            self.assertEqual(Fraction(section.error_upper), 0)

    def test_reconstruction_has_no_persisted_geometry_or_solver_values(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            section = CandidateRG2bSection(before, backend)
            payload = section.to_payload()
            self.assertEqual(
                set(payload), {"numerics", "inputs", "differential_reference"}
            )
            restored = CandidateRG2bSection.from_payload(payload)
            self.assertEqual(restored.geometry, section.geometry)
            later = replace(
                before,
                time=123.0,
                step_index=99,
                reset=replace(before.reset, C=(2.0, 2.0)),
            )
            self.assertEqual(
                CandidateRG2bSection(later, backend).geometry, section.geometry
            )
            with self.assertRaisesRegex(RG2bStageError, "Lipschitz-only"):
                section.classical_jacobian()

    def test_signed_gains_and_full_C_retained_filter_controls(self):
        for candidate in ("C", "A"):
            suffix = "_A" if candidate == "A" else "_C"
            before, backend = fixture(
                candidate,
                gain=-(2**-16),
                changes={
                    "candidate": {"zeta" + suffix: -0.125, "chi" + suffix: -0.125}
                },
            )
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertLessEqual(
                Fraction(step.diagnostics["invariance_residual"]),
                Fraction(step.diagnostics["invariance_error_bound"]),
            )
        values = []
        for change in ({}, {"kappa_M_C": 0.0}, {"tau_C": 0.0}, {"Lambda_C": 100.0}):
            before, _ = fixture("C", gain=2**-10, changes={"candidate": change})
            step = ProvisionalCandidateRG2bStep(before)
            values.append(step.point.current.values[0])
        self.assertEqual(len(set(values)), 4)

    def test_relabeling_and_reorientation_covariance(self):
        for candidate in ("C", "A"):
            graph = GRCV4Graph(
                ("renamed_u", "renamed_v"),
                (OrientedEdge("e", "renamed_v", "renamed_u"),),
            )
            left, backend = fixture(candidate)
            right, other_backend = fixture(candidate, graph=graph)
            a, b = (
                ProvisionalCandidateRG2bStep(left, backend),
                ProvisionalCandidateRG2bStep(right, other_backend),
            )
            self.assertEqual(
                a.section.geometry.one_form_hodge.matrix,
                b.section.geometry.one_form_hodge.matrix,
            )
            self.assertAlmostEqual(
                a.point.current.values[0], -b.point.current.values[0], places=14
            )
            self.assertEqual(a.next_inputs.current, b.next_inputs.current)

    def test_unsupported_graphs_reject_explicitly(self):
        graphs = [
            GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "u"),)),
            GRCV4Graph(
                ("u", "v"), (OrientedEdge("e", "u", "v"), OrientedEdge("f", "u", "v"))
            ),
            GRCV4Graph(("u", "v", "isolated"), (OrientedEdge("e", "u", "v"),)),
        ]
        for candidate in ("C", "A"):
            for graph in graphs:
                c = (2.0,) * len(graph.live_node_ids)
                before, backend = fixture(
                    candidate, graph=graph, C=c, W=(2.0,) * len(graph.live_edge_ids)
                )
                with self.assertRaisesRegex(RG2bStageError, "two vertices"):
                    CandidateRG2bSection(before, backend)


class RG2bStepTests(unittest.TestCase):
    def test_native_current_and_generated_source_match_independent_equations(self):
        import numpy as np

        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate)
            step = ProvisionalCandidateRG2bStep(before, backend)
            j, s = independent_point(
                before, backend, np.array(step.section.geometry.one_form_hodge.matrix)
            )
            self.assertAlmostEqual(j[0], step.point.current.values[0], delta=1e-13)
            generated = before.geometry.one_form_hodge.matrix[0][0] + 2**-10 * s[0, 0]
            self.assertAlmostEqual(
                generated, step.generated.one_form_hodge.matrix[0][0], delta=1e-14
            )
            self.assertEqual(step.resource.continuity_evaluations, 1)
            self.assertIsNone(step.next_inputs.current.Z_4)
            self.assertEqual(step.diagnostics["carrier_writes"], 0)
            self.assertLessEqual(
                Fraction(step.diagnostics["invariance_residual"]),
                Fraction(step.diagnostics["invariance_error_bound"]),
            )

    def test_A_writer_uses_selected_current_and_changes_mobility_once(self):
        from tests.models.test_grc_v4_candidate_a import log_writer_oracle

        before, backend = strong_fixture("A")
        step = ProvisionalCandidateRG2bStep(before, backend)
        expected = log_writer_oracle(
            before.current.W_A,
            step.writer.W_drv_A,
            before.dt,
            before.geometry.reference.profile.params_resolved.candidate.tau_A,
        )
        self.assertEqual(step.next_inputs.current.W_A, expected)
        self.assertNotEqual(step.next_inputs.current.W_A, before.current.W_A)
        self.assertEqual(step.point.inputs.current, before.current)

    def test_zero_duration_is_identity_not_a_positive_beat_invariance_claim(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            before = replace(before, dt=0.0)
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(step.next_inputs, before)
            self.assertEqual(step.resource.continuity_evaluations, 0)
            self.assertIsNone(step.writer)
            self.assertIsNone(step.generated)
            self.assertNotIn("invariance_residual", step.diagnostics)

    def test_reset_and_current_inner_charts_are_independently_required(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            original = before.to_payload()
            for field in ("current", "reset"):
                bad = replace(
                    before, **{field: replace(getattr(before, field), C=(2.375, 1.625))}
                )
                for dt in (0.0, before.dt):
                    with self.assertRaisesRegex(ResourceBoundaryError, "K_minus"):
                        ProvisionalCandidateRG2bStep(replace(bad, dt=dt), backend)
            self.assertEqual(before.to_payload(), original)

    def test_final_containment_does_not_claim_next_beat_inner_invariance(self):
        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate)
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertGreater(step.next_inputs.current.C[0], 2.25)
            self.assertLess(step.next_inputs.current.C[0], 2.5)
            with self.assertRaisesRegex(ResourceBoundaryError, "K_minus"):
                ProvisionalCandidateRG2bStep(step.next_inputs, backend)

    def test_replay_and_programmer_errors(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(
                ProvisionalCandidateRG2bStep.from_payload(
                    step.to_payload()
                ).next_inputs,
                step.next_inputs,
            )
            with patch.object(
                rg, "CandidateRG2bSection", side_effect=RuntimeError("section bug")
            ):
                with self.assertRaisesRegex(RuntimeError, "section bug"):
                    ProvisionalCandidateRG2bStep(before, backend)

    def test_current_sign_error_cannot_hide_behind_even_source(self):
        actual = rg._raw

        def wrong_current(*args):
            f, g, j = actual(*args)
            return f, g, -j

        for candidate in ("C", "A"):
            before, backend = fixture(candidate)
            with patch.object(rg, "_raw", side_effect=wrong_current):
                with self.assertRaisesRegex(ResourceBoundaryError, "arithmetic bridge"):
                    ProvisionalCandidateRG2bStep(before, backend)


# Seven auditor-proposed native regressions; isolated audit results are separate.


def native(inputs, backend):
    return (
        CandidateCCurrent(inputs)
        if backend is None
        else CandidateACurrent(inputs, backend)
    )


def reset_case(candidate):
    """Equal-charge reset with dyadic reference admission but failed section read."""
    if candidate == "C":
        before, backend = fixture(
            "C",
            C=(2.0, 2.0),
            gain=2**-10,
            changes={
                "candidate": {
                    "kappa_M_C": 0.0,
                    "tau_C": 0.0,
                    "chi_C": 0.5,
                    "zeta_C": 0.25,
                },
                "solver": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0},
            },
        )
        reset = replace(before.reset, C=(2 + 7 / 32, 2 - 7 / 32))
    else:
        domain = RG2bDomain(2.0, 3.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-16)
        before, backend = fixture(
            "A",
            domain=domain,
            C=(2.0, 2.0),
            W=(3.0,),
            gain=2**-10,
            changes={
                "candidate": {
                    "alpha": 0.0,
                    "beta": 0.0,
                    "gamma": 0.0,
                    "chi_A": 0.5,
                    "zeta_A": 0.5,
                    "kappa_Ah": 0.0,
                },
                "solver": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0},
            },
        )
        reset = replace(before.reset, C=(2 + 7 / 64, 2 - 7 / 64))
    return replace(before, reset=reset), backend


def final_case():
    domain = RG2bDomain(2.0, 1.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 2**-10)
    return fixture(
        "C",
        domain=domain,
        C=(2.091796875, 1.908203125),
        gain=2**-10,
        tolerance=2**-45,
        changes={
            "candidate": {
                "kappa_M_C": 0.0,
                "tau_C": 0.125,
                "chi_C": 0.125,
                "zeta_C": 0.25,
                "kappa_Phi_C": 0.125,
            },
            "solver": {"absolute_tolerance": 9 * 2**-57, "relative_tolerance": 0.0},
        },
    )


class RG2bAuditRegressions(unittest.TestCase):
    def check_reset(self, candidate):
        before, backend = reset_case(candidate)
        reset_inputs = replace(before, current=before.reset)
        # Positive controls: reference numerical current and section evaluator.
        native(reset_inputs, backend)
        section = CandidateRG2bSection(reset_inputs, backend)
        error_type = CandidateCStageError if candidate == "C" else CandidateAStageError
        with self.assertRaises(error_type) as cause:
            native(
                replace(reset_inputs, geometry=section.geometry, stage="rg2b_section"),
                backend,
            )
        self.assertEqual(cause.exception.disposition, "no_admitted_root")
        original = before.to_payload()
        for dt in (0.0, before.dt):
            with self.subTest(candidate=candidate, dt=dt):
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ProvisionalCandidateRG2bStep(replace(before, dt=dt), backend)
                self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
        self.assertEqual(before.to_payload(), original)

    def test_C_reset_admission_uses_its_section_geometry(self):
        self.check_reset("C")

    def test_A_reset_admission_uses_its_section_geometry(self):
        self.check_reset("A")

    def test_C_native_final_readmission_at_positive_tolerance(self):
        before, _ = final_case()
        section = CandidateRG2bSection(before)
        chosen = replace(before, geometry=section.geometry, stage="rg2b_section")
        point = CandidateCCurrent(chosen)
        selection = CurrentSelection(chosen, "valid_root", point.current)
        resource = ProvisionalResourceStep(before, selection)
        final = resource.consume(expected_prestate=before, expected_selection=selection)
        after = replace(
            before,
            current=final,
            time=float(Fraction(before.time) + Fraction(before.dt)),
            step_index=before.step_index + 1,
        )
        CandidateCCurrent(after)  # Reference-only final admission succeeds.
        restart = CandidateRG2bSection(after)
        with self.assertRaises(CandidateCStageError) as native_error:
            CandidateCCurrent(
                replace(after, geometry=restart.geometry, stage="rg2b_section")
            )
        self.assertEqual(native_error.exception.disposition, "no_admitted_root")
        self.assertIn("retained resolvent", str(native_error.exception))
        # Isolate the exact scalar failure independently of current construction.
        h = Fraction(restart.geometry.one_form_hodge.matrix[0][0])
        block = 1 + h / 4
        inverse = Fraction(float(1 / block))
        self.assertGreater(abs(block * inverse - 1), Fraction(9 * 2**-57))
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateRG2bStep(before)
        self.assertEqual(caught.exception.stage, "final_reconstruction")
        self.assertEqual(before.to_payload(), original)

    def test_consumed_native_no_admitted_root_keeps_its_code(self):
        for candidate in ("C", "A"):
            before, backend = reset_case(candidate)
            before = replace(before, current=before.reset, reset=before.current)
            with self.subTest(candidate=candidate):
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ProvisionalCandidateRG2bStep(before, backend)
                self.assertEqual(caught.exception.stage, "candidate_solve")
                self.assertEqual(caught.exception.code, "no_admitted_root")

    def test_safe_index_is_admitted_before_numerical_work(self):
        for candidate in ("C", "A"):
            before, backend = fixture(candidate, C=(2.0, 2.0))
            maximum = replace(before, step_index=2**53 - 1)
            with self.subTest(candidate=candidate):
                with patch.object(
                    rg,
                    "CandidateRG2bSection",
                    side_effect=AssertionError(
                        "section attempted before index rejection"
                    ),
                ):
                    with self.assertRaises(ResourceBoundaryError) as caught:
                        ProvisionalCandidateRG2bStep(maximum, backend)
                self.assertEqual(caught.exception.stage, "admission")
                self.assertEqual(caught.exception.code, "domain_failure")
                zero = ProvisionalCandidateRG2bStep(replace(maximum, dt=0.0), backend)
                self.assertEqual(zero.next_inputs, replace(maximum, dt=0.0))

    def test_clock_overflow_is_admitted_before_numerical_work(self):
        domain = RG2bDomain(2.0, 1.0, 0.25, 0.5, 0.75, 0.03125, 0.0625, 1e308)
        before, _ = fixture(
            "C",
            domain=domain,
            C=(2.0, 2.0),
            gain=0.0,
            changes={"candidate": {"kappa_Phi_C": 0.0, "kappa_M_C": 0.0, "tau_C": 0.0}},
        )
        with patch.object(
            rg,
            "CandidateRG2bSection",
            side_effect=AssertionError("section attempted before clock rejection"),
        ):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateRG2bStep(replace(before, time=1e308))
        self.assertEqual(caught.exception.stage, "admission")
        self.assertEqual(caught.exception.code, "nonfinite_value")

    def test_poststate_native_current_control_is_actually_reached(self):
        # Explicit fault control, separate from the native numerical witness above.
        for candidate in ("C", "A"):
            before, backend = strong_fixture(candidate)
            cls = CandidateCCurrent if candidate == "C" else CandidateACurrent
            error_type = (
                CandidateCStageError if candidate == "C" else CandidateAStageError
            )
            original = cls.__post_init__
            triggered = []

            def control(obj):
                inputs = obj.inputs
                if (
                    inputs.current != before.current
                    and inputs.geometry != inputs.geometry.reference.geometry()
                ):
                    triggered.append(inputs.stage)
                    raise error_type(
                        "no_admitted_root", "injected poststate-only current failure"
                    )
                return original(obj)

            with self.subTest(candidate=candidate):
                with patch.object(cls, "__post_init__", new=control):
                    with self.assertRaises(ResourceBoundaryError) as caught:
                        ProvisionalCandidateRG2bStep(before, backend)
                self.assertEqual(caught.exception.stage, "final_reconstruction")
                self.assertTrue(triggered)


class RG2bBoundaryPressure(unittest.TestCase):
    def test_reset_rejection_preserves_typed_cause_and_prevents_continuity(self):
        for candidate in ("A", "C"):
            before, backend = reset_case(candidate)
            with patch("pygrc.models.grc_v4_step.ProvisionalResourceStep") as resource:
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ProvisionalCandidateRG2bStep(before, backend)
            resource.assert_not_called()
            self.assertEqual(caught.exception.code, "no_admitted_root")
            self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
            self.assertEqual(caught.exception.__cause__.disposition, "no_admitted_root")

    def test_readmission_currents_are_postconditions_not_extra_writes(self):
        for candidate in ("A", "C"):
            before, backend = strong_fixture(candidate)
            calls = []
            original_resource = ProvisionalResourceStep.__post_init__
            original_writer = rg.CandidateAWriter.__post_init__

            def resource(value):
                calls.append("continuity")
                original_resource(value)

            def writer(value):
                calls.append("writer")
                original_writer(value)

            with patch.object(ProvisionalResourceStep, "__post_init__", resource):
                with patch.object(rg.CandidateAWriter, "__post_init__", writer):
                    step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(
                calls, ["continuity", "writer"] if candidate == "A" else ["continuity"]
            )
            self.assertEqual(step.reset_point.inputs.current, before.reset)
            self.assertEqual(
                step.reset_point.inputs.geometry, step.reset_section.geometry
            )
            self.assertEqual(
                step.restart_point.inputs.current, step.next_inputs.current
            )
            self.assertEqual(step.restart_point.inputs.geometry, step.restart.geometry)
            self.assertEqual(step.resource.continuity_evaluations, 1)

    def test_final_readmission_preserves_failure_code_and_programmer_errors(self):
        for candidate in ("A", "C"):
            before, backend = strong_fixture(candidate)
            cls = CandidateACurrent if candidate == "A" else CandidateCCurrent
            original = cls.__post_init__
            error_type = (
                CandidateAStageError if candidate == "A" else CandidateCStageError
            )
            for error in (
                error_type("no_admitted_root", "final native failure"),
                RuntimeError("native defect"),
            ):

                def control(obj):
                    if (
                        obj.inputs.step_index != before.step_index
                        and obj.inputs.geometry
                        != obj.inputs.geometry.reference.geometry()
                    ):
                        raise error
                    return original(obj)

                with patch.object(cls, "__post_init__", control):
                    with self.assertRaises(
                        ResourceBoundaryError
                        if isinstance(error, error_type)
                        else RuntimeError
                    ) as caught:
                        ProvisionalCandidateRG2bStep(before, backend)
                if isinstance(error, error_type):
                    self.assertEqual(caught.exception.stage, "final_reconstruction")
                    self.assertEqual(caught.exception.code, "no_admitted_root")
                    self.assertIs(caught.exception.__cause__, error)
