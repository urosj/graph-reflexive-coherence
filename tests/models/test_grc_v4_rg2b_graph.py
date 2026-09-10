"""Graph RG2b: independent equations, finite section and ordinary-step pressure."""

from dataclasses import replace
from fractions import Fraction as F
import os
import unittest

import numpy as np

from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_rg2b import (
    RG2bCertificate,
    CandidateRG2bSection,
    ProvisionalCandidateRG2bStep,
)
from pygrc.models import grc_v4_rg2b_graph as general
from tests.models.test_grc_v4_rg2b import fixture as scalar_fixture


def graph_fixture(
    candidate="C",
    *,
    n=4,
    pairs=None,
    domain=None,
    gain=1e-3,
    tolerance=1e-11,
    changes=None,
    limit=4000,
    **kwargs,
):
    nodes = tuple(f"v{i:03}" for i in range(n))
    if pairs is None:
        pairs = [(i, i + 1) for i in range(n - 1)]
    graph = GRCV4Graph(
        nodes,
        tuple(
            OrientedEdge(f"e{i:03}", nodes[u], nodes[v])
            for i, (u, v) in enumerate(pairs)
        ),
    )
    domain = domain or general.RG2bGraphDomain(
        2.0,
        2.0 if candidate == "A" else 1.0,
        0.125,
        0.25,
        0.375,
        0.015625,
        0.125,
        2**-20,
    )
    candidate_changes = (
        dict(
            eta=0.05,
            kappa_c=0.1,
            kappa_Ah=0.1,
            alpha=0.02,
            beta=0.03,
            gamma=0.02,
            chi_A=0.1,
            zeta_A=0.1,
        )
        if candidate == "A"
        else dict(
            eta_C=0.05,
            kappa_Phi_C=0.1,
            kappa_M_C=0.1,
            tau_C=0.1,
            chi_C=0.1,
            zeta_C=0.1,
            Lambda_C=100.0,
        )
    )
    updates = dict(
        charge=dict(absolute_tolerance=1e-11),
        candidate=candidate_changes,
        realization=dict(
            approximation_policy_id=general.APPROXIMATION,
            error_norm_id=general.ERROR_NORM,
            containment_certificate_id=general.CONTAINMENT,
        ),
    )
    for group, values in (changes or {}).items():
        updates.setdefault(group, {}).update(values)
    return scalar_fixture(
        candidate,
        domain=domain,
        graph=graph,
        C=kwargs.pop(
            "C", tuple(2 + (-1 if i % 2 else 1) * (i % 3 + 1) / 32 for i in range(n))
        ),
        W=kwargs.pop("W", tuple(2 + (i % 3 - 1) / 32 for i in range(len(pairs)))),
        weights=kwargs.pop(
            "weights", {e: 1 + (i % 3) / 8 for i, e in enumerate(graph.live_edge_ids)}
        ),
        gain=gain,
        tolerance=tolerance,
        limit=limit,
        changes=updates,
        **kwargs,
    )


class GraphRG2bTests(unittest.TestCase):
    def test_first_matrix_sections_and_steps(self):
        for candidate in ("A", "C"):
            with self.subTest(candidate=candidate):
                before, backend = graph_fixture(candidate)
                step = ProvisionalCandidateRG2bStep(before, backend)
                self.assertGreater(
                    F(step.section.certificate.bounds["contraction_upper"]), 0
                )
                self.assertGreater(
                    np.linalg.norm(
                        np.array(step.section.geometry.one_form_hodge.matrix)
                        - np.array(before.geometry.one_form_hodge.matrix)
                    ),
                    1e-14,
                )
                self.assertEqual(step.resource.continuity_evaluations, 1)
                self.assertLessEqual(
                    F(step.diagnostics["invariance_residual"]),
                    F(step.diagnostics["invariance_error_bound"]),
                )


def independent_maps(before, backend, x, h):
    """Literal dense candidate maps and log writer, without RG certificate helpers."""
    import math
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
    from tests.models.test_grc_v4_ci import independent_point
    from tests.models.test_grc_v4_candidate_a import scalar_oracle

    graph = before.geometry.reference.graph
    n = len(graph.live_node_ids)
    state = GRCV4AuthoritativeState(
        tuple(map(float, x[:n])), tuple(map(float, x[n:])) if backend else None, None
    )
    selected = replace(before, current=state)
    j, source = independent_point(selected, backend, h)
    c = np.array(x[:n]) - before.dt * np.array(graph.incidence) @ j
    y = c
    if backend:
        _, target = scalar_oracle(
            before.geometry.reference, backend, tuple(c), tuple(j)
        )
        tau = before.geometry.reference.profile.params_resolved.candidate.tau_A
        fraction = -math.expm1(-before.dt / tau)
        w = np.array(
            [
                math.exp(math.log(old) + fraction * (math.log(new) - math.log(old)))
                for old, new in zip(x[n:], target, strict=True)
            ]
        )
        y = np.concatenate((c, w))
    return y - np.array(x), source, j


class GraphRG2bPressure(unittest.TestCase):
    def test_scalar_reference_sections_agree_with_matrix_completion(self):
        from tests.models.test_grc_v4_rg2b import strong_fixture
        from tests.models.test_grc_v4_profile import reidentify
        from pygrc.models.grc_v4_profile import resolve_profile
        from pygrc.models.grc_v4_rg2b import RG2bDomain

        for candidate in ("A", "C"):
            old, backend = strong_fixture(candidate)
            a = CandidateRG2bSection(old, backend)
            ref = old.geometry.reference
            params, identity = (
                ref.profile.params_resolved.to_payload(),
                ref.profile.identity_payload.to_payload(),
            )
            d = RG2bDomain.from_identity(
                params["realization"]["extension_evaluator_id"]
            )
            gd = general.RG2bGraphDomain(
                *(getattr(d, k) for k in d.__dataclass_fields__)
            )
            params["realization"].update(
                extension_evaluator_id=gd.identity,
                approximation_policy_id=general.APPROXIMATION,
                error_norm_id=general.ERROR_NORM,
                containment_certificate_id=general.CONTAINMENT,
            )
            reidentify(params, identity)
            converted = replace(
                old,
                geometry=replace(
                    ref, profile=resolve_profile(params, identity)
                ).geometry(),
            )
            b = CandidateRG2bSection(converted, backend)
            self.assertLessEqual(
                abs(
                    F(a.geometry.one_form_hodge.matrix[0][0])
                    - F(b.geometry.one_form_hodge.matrix[0][0])
                ),
                F(a.error_upper) + F(b.error_upper),
            )

    def test_nonzero_A_descriptor_and_C_noncommuting_response(self):
        from tests.models.test_grc_v4_candidate_c import dense_current_oracle
        from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
        from pygrc.models.grc_v4_ci import _a_descriptors_exact

        for candidate in ("A", "C"):
            before, backend = graph_fixture(
                candidate, pairs=[(0, 1), (1, 2), (2, 0), (2, 3)]
            )
            section = CandidateRG2bSection(before, backend)
            cert = section.certificate
            h = np.array(before.geometry.one_form_hodge.matrix)
            h[0, 1] = h[1, 0] = 0.003
            h[1, 2] = h[2, 1] = -0.002
            selected = replace(
                before,
                geometry=GRCV4Geometry(
                    before.geometry.reference,
                    OneFormHodge(before.geometry.reference.graph, tuple(map(tuple, h))),
                ),
                stage="rg2b_section",
            )
            if backend:
                from pygrc.models.grc_v4_candidate_a import CandidateACurrent

                point = CandidateACurrent(selected, backend)
                exact = _a_descriptors_exact(point)
                matrix = general.descriptor_operators(backend)
                evaluated = tuple(
                    tuple(
                        sum(
                            a * F(c) for a, c in zip(row, before.current.C, strict=True)
                        )
                        for row in op
                    )
                    for op in matrix
                )
                self.assertEqual(exact, evaluated)
                self.assertGreater(abs(float(exact[0][0] - exact[1][0])), 0.001)
            else:
                data = dense_current_oracle(selected)
                self.assertGreater(
                    np.linalg.norm(data["hm"] @ h - h @ data["hm"]), 1e-8
                )
                self.assertGreater(
                    np.linalg.norm(data["flux_response"] - data["response"]), 1e-5
                )
            x = np.array(general.coordinates(before.current), dtype=float)
            f, source, j = independent_maps(before, backend, x, h)
            fi, gi, je, ge = general.point_maps(
                cert, tuple(map(F, x)), tuple(map(tuple, h))
            )
            gain = before.geometry.reference.profile.params_resolved.geometry.kappa_H
            generated = np.array(before.geometry.one_form_hodge.matrix) + gain * source
            # The independent binary64 oracle has its own rounding. Tight
            # absolute allowances here are comparison tolerances, not certificates.
            self.assertLess(
                max(
                    abs(float((v.lo + v.hi) / 2) - a)
                    for v, a in zip(fi, f, strict=True)
                ),
                2e-15,
            )
            self.assertLess(
                np.linalg.norm(
                    np.array([[float((v.lo + v.hi) / 2) for v in row] for row in gi])
                    - generated
                ),
                2e-15,
            )
            self.assertLess(float(je), 1e-12)
            self.assertLess(float(ge), 1e-12)

    def test_whole_chart_bounds_against_independent_changes_in_every_axis(self):
        rng = np.random.default_rng(649)
        for candidate in ("A", "C"):
            before, backend = graph_fixture(
                candidate,
                pairs=[(0, 1), (1, 2), (2, 0), (2, 3)],
                changes={"candidate": {"Lambda_C": 1.5}} if candidate == "C" else {},
            )
            cert = RG2bCertificate(before, backend)
            d = cert.domain
            bounds = {k: float(F(v)) for k, v in cert.bounds.items()}
            center = np.array(general.centers(before, d))
            href = np.array(before.geometry.one_form_hodge.matrix)
            dim = len(center)
            for sample in range(4):
                x = center + rng.uniform(-d.outer, d.outer, dim)
                e = rng.normal(size=href.shape)
                e = (e + e.T) / 2
                h = href + e * (d.h_radius * 0.8 / np.linalg.norm(e))
                f, g, j = independent_maps(before, backend, x, h)
                self.assertLessEqual(
                    np.max(np.abs(f)), bounds["base_displacement_upper"]
                )
                self.assertLessEqual(np.linalg.norm(g), bounds["source_upper"])
                self.assertLessEqual(np.linalg.norm(j), bounds["current_upper"])
                for axis in range(dim):
                    xx = x.copy()
                    xx[axis] += 1e-5
                    ff, gg, _ = independent_maps(before, backend, xx, h)
                    self.assertLessEqual(
                        np.max(np.abs(ff - f)) / 1e-5,
                        bounds["base_X_lipschitz"] + 1e-10,
                    )
                    self.assertLessEqual(
                        np.linalg.norm(gg - g) / 1e-5,
                        bounds["source_X_lipschitz"] + 1e-10,
                    )
                for i in range(len(h)):
                    for k in range(i, len(h)):
                        hh = h.copy()
                        hh[i, k] += 1e-5
                        if k != i:
                            hh[k, i] += 1e-5
                        size = np.linalg.norm(hh - h)
                        ff, gg, _ = independent_maps(before, backend, x, hh)
                        self.assertLessEqual(
                            np.max(np.abs(ff - f)) / size,
                            bounds["base_h_lipschitz"] + 1e-10,
                        )
                        self.assertLessEqual(
                            np.linalg.norm(gg - g) / size,
                            bounds["source_h_lipschitz"] + 1e-10,
                        )

    def test_cycles_branches_parallel_loops_disconnected_and_isolates(self):
        pairs = [(0, 1), (1, 2), (2, 0), (1, 3), (0, 1), (2, 2), (4, 5)]
        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate, n=7, pairs=pairs)
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(step.next_inputs.current.C[6], before.current.C[6])
            self.assertEqual(step.point.current.values[5], 0.0)
            self.assertEqual(step.resource.continuity_evaluations, 1)
            self.assertGreater(np.linalg.norm(step.point.current.values), 0)

    def test_variable_graph_sizes_and_repeated_native_beats(self):
        for candidate in ("A", "C"):
            for n in (8, 16):
                before, backend = graph_fixture(candidate, n=n)
                for beat in range(2):
                    step = ProvisionalCandidateRG2bStep(before, backend)
                    self.assertEqual(step.next_inputs.step_index, before.step_index + 1)
                    self.assertGreater(
                        np.linalg.norm(
                            np.array(step.section.geometry.one_form_hodge.matrix)
                            - np.array(before.geometry.one_form_hodge.matrix)
                        ),
                        1e-13,
                    )
                    self.assertLessEqual(
                        F(step.diagnostics["invariance_residual"]),
                        F(step.diagnostics["invariance_error_bound"]),
                    )
                    before = step.next_inputs

    def test_finite_transform_against_independent_inverse_oracle(self):
        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate)
            actual = CandidateRG2bSection(before, backend)
            x = np.array(general.coordinates(before.current), dtype=float)
            href = np.array(before.geometry.one_form_hodge.matrix)
            gain = before.geometry.reference.profile.params_resolved.geometry.kappa_H

            # Two literal transforms, including inverse dependence on the prior
            # section. Fixture inverses stay in K, where the cutoff equals one.
            def oracle(level, target):
                if level == 0:
                    return href
                mid = target.copy()
                for _ in range(10):
                    h = oracle(level - 1, mid)
                    f, source, _ = independent_maps(before, backend, mid, h)
                    following = target - f
                    if np.max(np.abs(mid - following)) < 1e-15:
                        return href + gain * source
                    mid = following
                self.fail("independent inverse did not converge")

            expected = oracle(2, x)
            tail = float(
                F(actual.certificate.bounds["section_radius"])
                * F(actual.certificate.bounds["contraction_upper"]) ** 2
            )
            self.assertLessEqual(
                np.linalg.norm(
                    np.array(actual.geometry.one_form_hodge.matrix) - expected
                ),
                float(F(actual.error_upper)) + tail + 2e-15,
            )

    def test_parameter_and_numerical_failure_boundaries(self):
        from pygrc.models.grc_v4_rg2b import RG2bStageError

        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate)
            d = general.RG2bGraphDomain.from_identity(
                before.geometry.reference.profile.params_resolved.realization.extension_evaluator_id
            )
            cases = [
                dict(domain=replace(d, h_radius=2.0)),
                dict(domain=replace(d, beat_dt=1.0)),
                dict(domain=replace(d, inner=np.nextafter(d.core, 0).item())),
                dict(domain=replace(d, section_lipschitz=1e-30)),
                dict(tolerance=0.0),
                dict(limit=1),
            ]
            for case in cases:
                with self.subTest(candidate=candidate, case=case):
                    bad, b = graph_fixture(candidate, **case)
                    with self.assertRaises(RG2bStageError):
                        CandidateRG2bSection(bad, b)
            for name in (
                "approximation_policy_id",
                "error_norm_id",
                "containment_certificate_id",
            ):
                bad, b = graph_fixture(
                    candidate, changes={"realization": {name: "unimplemented"}}
                )
                with self.assertRaises(RG2bStageError):
                    CandidateRG2bSection(bad, b)
        bad, _ = graph_fixture("C", changes={"candidate": {"Lambda_C": 2.0}})
        # A separate exact cutoff graph removes reliance on approximate spectra.
        bad, _ = graph_fixture(
            "C", n=2, weights={"e000": 1.0}, changes={"candidate": {"Lambda_C": 2.0}}
        )
        from pygrc.models.grc_v4_candidate_c import CandidateCStageError

        with self.assertRaises((RG2bStageError, CandidateCStageError)):
            RG2bCertificate(bad)
        bad, b = graph_fixture("A", changes={"candidate": {"W_floor": 0.99}})
        with self.assertRaises(RG2bStageError):
            RG2bCertificate(bad, b)

    def test_recipes_zero_duration_and_no_classical_jacobian(self):
        from pygrc.models.grc_v4_rg2b import RG2bStageError

        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate)
            step = ProvisionalCandidateRG2bStep(replace(before, dt=0.0), backend)
            self.assertEqual(step.resource.continuity_evaluations, 0)
            self.assertIsNone(step.writer)
            replay = ProvisionalCandidateRG2bStep.from_payload(step.to_payload())
            self.assertEqual(replay.section, step.section)
            self.assertEqual(
                CandidateRG2bSection.from_payload(step.section.to_payload()),
                step.section,
            )
            with self.assertRaisesRegex(RG2bStageError, "Lipschitz"):
                step.section.classical_jacobian()
            bad = step.to_payload()
            bad["numerics"] = "different"
            with self.assertRaises(RG2bStageError):
                ProvisionalCandidateRG2bStep.from_payload(bad)


class GraphRG2bAdmissionAndCovariance(unittest.TestCase):
    def test_high_degree_graph_with_nonzero_feedback(self):
        for candidate in ("A", "C"):
            before, backend = graph_fixture(
                candidate,
                n=12,
                pairs=[(0, i) for i in range(1, 12)],
                gain=1e-3,
                tolerance=1e-13,
                changes={"candidate": {"eta": 0.01}}
                if candidate == "A"
                else {"candidate": {"eta_C": 0.01}},
            )
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertGreater(np.linalg.norm(step.point.current.values), 0.001)
            self.assertGreater(
                np.linalg.norm(
                    np.array(step.section.geometry.one_form_hodge.matrix)
                    - np.array(before.geometry.one_form_hodge.matrix)
                ),
                1e-13,
            )
            self.assertLessEqual(
                F(step.diagnostics["invariance_residual"]),
                F(step.diagnostics["invariance_error_bound"]),
            )

    def test_relabeling_reorientation_covariance_within_reported_errors(self):
        from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
        from pygrc.models.grc_v4_profile import resolve_profile
        from tests.models.test_grc_v4_profile import reidentify

        pairs = [(0, 1), (1, 2), (2, 0), (2, 3)]
        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate, pairs=pairs)
            old = CandidateRG2bSection(before, backend)
            graph = before.geometry.reference.graph
            names = {n: f"r{3 - i}" for i, n in enumerate(graph.live_node_ids)}
            signs = (-1, 1, -1, 1)
            edges = tuple(
                OrientedEdge(
                    e.edge_id,
                    names[e.head_node_id] if signs[i] < 0 else names[e.tail_node_id],
                    names[e.tail_node_id] if signs[i] < 0 else names[e.head_node_id],
                )
                for i, e in enumerate(graph.oriented_edges)
            )
            renamed = GRCV4Graph(tuple(sorted(names.values())), edges)
            order = [
                graph.node_index(next(k for k, v in names.items() if v == n))
                for n in renamed.live_node_ids
            ]
            ref = before.geometry.reference
            # Reconstruct the reference through its portable recipe, preserving
            # all measures, weights and profile semantics under the permutation.
            payload = ref.to_payload()
            payload["graph"] = renamed.to_payload()
            if backend:
                backend = CandidateADifferentialReference(
                    renamed,
                    backend.dimension,
                    tuple(backend.positions[i] for i in order),
                    backend.reference_weights,
                    backend.regularization,
                )
                params, identity = (
                    ref.profile.params_resolved.to_payload(),
                    ref.profile.identity_payload.to_payload(),
                )
                params["candidate"]["descriptor_backend_id"] = backend.identity
                reidentify(params, identity)
                payload["profile"] = resolve_profile(params, identity).to_payload()
            changed = type(ref).from_payload(payload)
            state = replace(before.current, C=tuple(before.current.C[i] for i in order))
            new = CandidateRG2bSection(
                replace(
                    before, current=state, reset=state, geometry=changed.geometry()
                ),
                backend,
            )
            sign = np.diag(signs)
            self.assertLessEqual(
                np.linalg.norm(
                    np.array(new.geometry.one_form_hodge.matrix)
                    - sign @ np.array(old.geometry.one_form_hodge.matrix) @ sign
                ),
                float(F(old.error_upper) + F(new.error_upper)),
            )

    def test_native_postconditions_and_failure_provenance_on_matrix_geometry(self):
        from unittest.mock import patch
        import pygrc.models.grc_v4_rg2b as rg
        from pygrc.models.grc_v4_candidate_a import CandidateAStageError
        from pygrc.models.grc_v4_candidate_c import CandidateCStageError
        from pygrc.models.grc_v4_step import ResourceBoundaryError

        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate)
            changed = replace(before.reset, C=tuple(reversed(before.reset.C)))
            before = replace(before, reset=changed)
            native = rg.CandidateACurrent if backend else rg.CandidateCCurrent
            original = native.__post_init__
            error = CandidateAStageError if backend else CandidateCStageError
            for final in (False, True):
                calls = []
                failure = error(
                    "no_admitted_root", "matrix postcondition injected failure"
                )

                def checked(point):
                    inputs = point.inputs
                    if inputs.stage == "rg2b_section":
                        calls.append(inputs)
                        if (
                            inputs.step_index > before.step_index
                            if final
                            else inputs.current == changed
                        ):
                            raise failure
                    return original(point)

                with patch.object(native, "__post_init__", checked):
                    with self.assertRaises(ResourceBoundaryError) as caught:
                        ProvisionalCandidateRG2bStep(before, backend)
                self.assertEqual(caught.exception.code, "no_admitted_root")
                self.assertEqual(
                    caught.exception.stage,
                    "final_reconstruction" if final else "pre_read_reconstruction",
                )
                self.assertIs(caught.exception.__cause__, failure)
                self.assertTrue(calls)

    def test_outer_cutoff_and_matrix_ball_error_are_not_point_fits(self):
        from pygrc.models.grc_v4_ci import _Interval
        from pygrc.models.grc_v4_rg2b import _cutoff

        d = graph_fixture()[
            0
        ].geometry.reference.profile.params_resolved.realization.extension_evaluator_id
        domain = general.RG2bGraphDomain.from_identity(d)
        for sign in (-1, 1):
            self.assertEqual(
                _cutoff(
                    F(domain.center_C) + sign * F(domain.core), domain.center_C, domain
                ),
                1,
            )
            self.assertEqual(
                _cutoff(
                    F(domain.center_C) + sign * F(domain.outer), domain.center_C, domain
                ),
                0,
            )
            self.assertEqual(
                _cutoff(
                    F(domain.center_C) + sign * F(domain.outer) * 2,
                    domain.center_C,
                    domain,
                ),
                0,
            )
        intervals = (
            (_Interval(F(1), F(1)), _Interval(F(-1, 100), F(1, 100))),
            (_Interval(F(-1, 100), F(1, 100)), _Interval(F(2), F(2))),
        )
        ball = general.matrix_ball(intervals)
        self.assertGreaterEqual(ball.error**2, F(2, 10000))
        self.assertEqual(ball.center[0][1], ball.center[1][0])


class GraphRG2bLargerExecution(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("GRCV4_RUN_SLOW_RG2B") == "1",
        "optional slow campaign; set GRCV4_RUN_SLOW_RG2B=1 explicitly",
    )
    def test_32_vertex_cycle_native_step_and_independent_current(self):
        from tests.models.test_grc_v4_ci import independent_point

        for candidate in ("A", "C"):
            with self.subTest(candidate=candidate):
                before, backend = graph_fixture(
                    candidate,
                    n=32,
                    pairs=[(i, (i + 1) % 32) for i in range(32)],
                    gain=1e-4,
                    changes={"candidate": {"eta": 0.01}}
                    if candidate == "A"
                    else {"candidate": {"eta_C": 0.01}},
                )
                step = ProvisionalCandidateRG2bStep(before, backend)
                expected, _ = independent_point(
                    before,
                    backend,
                    np.array(step.section.geometry.one_form_hodge.matrix),
                )
                self.assertLess(
                    np.linalg.norm(np.array(step.point.current.values) - expected),
                    1e-11,
                )
                self.assertGreater(np.linalg.norm(step.point.current.values), 0.001)
                self.assertGreater(
                    np.linalg.norm(
                        np.array(step.section.geometry.one_form_hodge.matrix)
                        - np.array(before.geometry.one_form_hodge.matrix)
                    ),
                    10 * float(F(step.section.error_upper)),
                )
                self.assertEqual(step.resource.continuity_evaluations, 1)
                self.assertLessEqual(
                    F(step.diagnostics["invariance_residual"]),
                    F(step.diagnostics["invariance_error_bound"]),
                )
                self.assertLess(
                    abs(sum(step.next_inputs.current.C) - before.Q_target), 1e-11
                )

    def test_loop_only_neutral_source_and_empty_space_rejection(self):
        for candidate in ("A", "C"):
            before, backend = graph_fixture(candidate, n=4, pairs=[(0, 0), (1, 1)])
            step = ProvisionalCandidateRG2bStep(before, backend)
            self.assertEqual(step.point.current.values, (0.0, 0.0))
            self.assertEqual(step.section.geometry, before.geometry)
            self.assertEqual(step.next_inputs.current.C, before.current.C)
            self.assertEqual(step.section.levels, 0)
            if backend:
                self.assertNotEqual(step.next_inputs.current.W_A, before.current.W_A)
            from pygrc.models.grc_v4_codec import V4SchemaError

            with self.assertRaisesRegex(V4SchemaError, "non-empty"):
                graph_fixture(candidate, n=4, pairs=[])


class GraphRG2bDescriptorDimensions(unittest.TestCase):
    def test_multidimensional_WLS_coefficients_and_unrepresented_query_rejection(self):
        from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
        from pygrc.models.grc_v4_profile import resolve_profile
        from tests.models.test_grc_v4_profile import reidentify
        from pygrc.models.grc_v4_rg2b import RG2bStageError

        before, _ = graph_fixture("A", pairs=[(0, 1), (1, 2), (2, 0), (2, 3)])
        ref = before.geometry.reference
        positions = ((0.0, 0.0), (1.0, 0.0), (1.0, 2.0), (-1.0, 3.0))
        backend = CandidateADifferentialReference(
            ref.graph, 2, positions, ref.edge_weights, 0.25
        )
        params, identity = (
            ref.profile.params_resolved.to_payload(),
            ref.profile.identity_payload.to_payload(),
        )
        params["candidate"]["descriptor_backend_id"] = backend.identity
        reidentify(params, identity)
        before = replace(
            before,
            geometry=replace(ref, profile=resolve_profile(params, identity)).geometry(),
        )
        cert = RG2bCertificate(before, backend)
        coefficients = general.descriptor_operators(backend)
        for i, node in enumerate(ref.graph.live_node_ids):
            normal = 0.25 * np.eye(2)
            rhs = np.zeros(2)
            for edge in ref.graph.oriented_edges:
                if node not in (edge.tail_node_id, edge.head_node_id):
                    continue
                j = ref.graph.node_index(
                    edge.head_node_id
                    if node == edge.tail_node_id
                    else edge.tail_node_id
                )
                delta = np.array(positions[j]) - np.array(positions[i])
                weight = ref.edge_weights[edge.edge_id]
                normal += weight * np.outer(delta, delta)
                rhs += weight * delta * (before.current.C[j] - before.current.C[i])
            self.assertLess(
                np.linalg.norm(
                    np.array(coefficients[i], dtype=float) @ np.array(before.current.C)
                    - np.linalg.solve(normal, rhs)
                ),
                1e-14,
            )
        x = list(general.coordinates(before.current))
        x[0] = F(7, 3)
        with self.assertRaisesRegex(RG2bStageError, "represented"):
            general.point_maps(cert, tuple(x), before.geometry.one_form_hodge.matrix)


class GraphRG2bPartialSelector(unittest.TestCase):
    def test_partial_selector_native_beats_with_both_geometry_gain_signs(self):
        from tests.models.test_grc_v4_ci import independent_point

        for gain in (-0.001, 0.001):
            before, _ = graph_fixture(
                "C",
                pairs=[(0, 1), (1, 2), (2, 0), (2, 3)],
                gain=gain,
                changes={"candidate": {"Lambda_C": 1.5}},
            )
            step = ProvisionalCandidateRG2bStep(before)
            self.assertEqual(step.point.algebra.selector.rank, 2)
            expected, _ = independent_point(
                before, None, np.array(step.section.geometry.one_form_hodge.matrix)
            )
            self.assertLess(
                np.linalg.norm(np.array(step.point.current.values) - expected), 1e-11
            )
            self.assertLessEqual(
                F(step.diagnostics["invariance_residual"]),
                F(step.diagnostics["invariance_error_bound"]),
            )
            self.assertGreater(
                abs(step.section.geometry.one_form_hodge.matrix[0][1]),
                float(F(step.section.error_upper)),
            )


# P9-6.4d: the auditor's three proposed methods, executed natively here.
from pygrc.models.grc_v4_rg2b import RG2bStageError  # noqa: E402
from pygrc.models.grc_v4_rg2b_graph import (  # noqa: E402
    RG2bGraphDomain,
    coordinates,
    point_maps,
    matrix_ball,
)
from pygrc.models.grc_v4_ci import _Interval  # noqa: E402
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge  # noqa: E402
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent  # noqa: E402


def mm(a, b):
    return tuple(
        tuple(sum((x * y for x, y in zip(row, col)), F()) for col in zip(*b))
        for row in a
    )


def tr(a):
    return tuple(zip(*a))


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def inv(a):
    n = len(a)
    work = [list(row) + list(e) for row, e in zip(a, eye(n))]
    for i in range(n):
        pivot = next(k for k in range(i, n) if work[k][i])
        work[i], work[pivot] = work[pivot], work[i]
        q = work[i][i]
        work[i] = [v / q for v in work[i]]
        for k in range(n):
            if k != i:
                q = work[k][i]
                work[k] = [x - q * y for x, y in zip(work[k], work[i])]
    return tuple(tuple(row[n:]) for row in work)


def exact(a):
    return tuple(tuple(F(x) for x in row) for row in a)


class GraphRG2bReconciliation(unittest.TestCase):
    def test_large_hodge_rounding_cannot_hide_section_error(self):
        h = 2.0**100
        d = RG2bGraphDomain(2.0, 1.0, 0.5, 1.25, 1.5, 2.0**63, 2.0**60, 2.0**-100)
        args = dict(
            n=4,
            pairs=[(0, 1), (2, 3)],
            domain=d,
            C=(3.0, 1.0, 3.0, 1.0),
            weights={"e000": h, "e001": h},
            tolerance=1e-10,
            changes={
                "candidate": {
                    "eta_C": 2.0**-100,
                    "kappa_Phi_C": 2.0**-101,
                    "kappa_M_C": 0.0,
                    "tau_C": 0.0,
                    "chi_C": 0.25,
                    "zeta_C": 2.0,
                    "Lambda_C": h,
                }
            },
        )
        for sign in (-1, 1):
            with self.subTest(geometry_gain_sign=sign):
                bad, _ = graph_fixture("C", gain=sign * 3 * 2.0**245, **args)
                RG2bCertificate(bad)  # Analytic completion is admitted.
                raw = F(3 * 2.0**245) * 2 / F(h) ** 2
                self.assertEqual(raw, 3 * F(2) ** 46)
                # These disjoint-edge fixed sections are diagonal. Exactly,
                # D_next = D * (1 + 4*dt*H/h). The inverse lies in the core;
                # the whole Hodge ball bounds its nonzero correction to D=2.
                lower = raw / (1 + 4 * F(d.beat_dt) * (1 + F(d.h_radius) / F(h))) ** 2
                upper = raw / (1 + 4 * F(d.beat_dt) * (1 - F(d.h_radius) / F(h))) ** 2
                lo, hi = (
                    (F(h) + lower, F(h) + upper)
                    if sign > 0
                    else (F(h) - upper, F(h) - lower)
                )
                nearest = F(float((lo + hi) / 2))
                # At 2**100 the binary64 spacing below is half the spacing
                # above. Both signs still miss the required absolute tolerance.
                self.assertGreater(max(lo - nearest, nearest - hi, F()), F(10**13))
                with self.assertRaisesRegex(
                    RG2bStageError, "approximation/error tolerance"
                ):
                    CandidateRG2bSection(bad)
                good, _ = graph_fixture("C", gain=sign * 2.0**247, **args)
                section = CandidateRG2bSection(good)
                self.assertEqual(
                    section.geometry.one_form_hodge.matrix,
                    ((h + sign * 2.0**48, 0.0), (0.0, h + sign * 2.0**48)),
                )
                self.assertLessEqual(F(section.error_upper), F(1e-10))
        neutral, _ = graph_fixture("C", gain=0.0, **args)
        section = CandidateRG2bSection(neutral)
        self.assertEqual(section.geometry, neutral.geometry)
        self.assertEqual(F(section.error_upper), 0)
        self.assertEqual(section.levels, 0)

    def test_rational_noncommuting_current_and_source_error_bridge(self):
        for tau in (0.0, 0.125):
            with self.subTest(tau=tau):
                before, _ = graph_fixture(
                    "C",
                    n=4,
                    pairs=[(0, 1), (1, 2), (2, 0), (2, 3)],
                    gain=-(2.0**-10),
                    changes={"candidate": {"kappa_M_C": 0.0, "tau_C": tau}},
                )
                cert = RG2bCertificate(before)
                ref = before.geometry.reference
                g = ref.graph
                h = [list(row) for row in ref.pairings.one_form.matrix]
                h[0][1] = h[1][0] = 2.0**-10
                h[1][2] = h[2][1] = -(2.0**-11)
                h = tuple(map(tuple, h))
                p = ref.profile.params_resolved.candidate
                m = len(h)
                selected = replace(
                    before,
                    geometry=GRCV4Geometry(ref, OneFormHodge(g, h)),
                    stage="rg2b_section",
                )
                point = CandidateCCurrent(selected)
                fi, gi, je, ge = point_maps(cert, coordinates(before.current), h, point)
                B = exact(g.incidence)
                H = exact(h)
                identity = eye(m)
                Q = inv(H)
                lap = mm(mm(tr(B), B), H)
                R = inv(
                    tuple(
                        tuple(identity[i][j] + F(tau) * lap[i][j] for j in range(m))
                        for i in range(m)
                    )
                )
                response = mm(mm(H, R), Q)
                self.assertEqual(
                    response, identity
                ) if tau == 0 else self.assertNotEqual(response, R)
                if tau:
                    self.assertNotEqual(mm(H, R), mm(R, H))
                C = tuple((F(x),) for x in before.current.C)
                raw = mm(mm(mm(mm(tr(B), B), H), tr(B)), C)
                J0 = tuple(
                    (-F(p.eta_C) * F(p.W_C_tr[e]) * F(p.kappa_Phi_C) * raw[i][0],)
                    for i, e in enumerate(g.live_edge_ids)
                )
                block = tuple(
                    tuple(
                        identity[i][j] - F(p.zeta_C) * F(p.chi_C) * response[i][j]
                        for j in range(m)
                    )
                    for i in range(m)
                )
                J = mm(inv(block), J0)
                self.assertLessEqual(
                    sum((F(a) - b[0]) ** 2 for a, b in zip(point.current.values, J)),
                    je**2,
                )
                flat = mm(mm(Q, response), J)
                flat = tuple(F(p.chi_C) * v[0] for v in flat)
                generated = []
                for i, e in enumerate(g.oriented_edges):
                    row = []
                    for j, f in enumerate(g.oriented_edges):
                        common = len(
                            {e.tail_node_id, e.head_node_id}
                            & {f.tail_node_id, f.head_node_id}
                        )
                        row.append(
                            F(ref.pairings.one_form.matrix[i][j])
                            + F(ref.profile.params_resolved.geometry.kappa_H)
                            * F(p.zeta_C)
                            * F(common, 2)
                            * flat[i]
                            * flat[j]
                        )
                    generated.append(row)
                distance2 = sum(
                    max(v.lo - x, F(), x - v.hi) ** 2
                    for row, ex in zip(gi, generated)
                    for v, x in zip(row, ex)
                )
                self.assertLessEqual(distance2, ge**2)
                dc = mm(B, J)
                for value, iv in zip(dc, fi):
                    f = -F(cert.domain.beat_dt) * value[0]
                    self.assertLessEqual(iv.lo, f)
                    self.assertLessEqual(f, iv.hi)

    def test_matrix_error_counts_both_offdiagonal_entries(self):
        for n in (2, 5, 9):
            with self.subTest(n=n):
                eps = F(1, 1024)
                extra = F(1, 128)
                intervals = tuple(
                    tuple(_Interval(F(i == j) - eps, F(i == j) + eps) for j in range(n))
                    for i in range(n)
                )
                ball = matrix_ball(intervals, extra)
                self.assertEqual(
                    ball.center,
                    tuple(tuple(float(i == j) for j in range(n)) for i in range(n)),
                )
                self.assertGreaterEqual(ball.error, n * eps + extra)
