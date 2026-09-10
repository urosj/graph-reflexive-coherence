"""Independent PC equations, whole-chart bounds, history and outlier pressure."""

from dataclasses import FrozenInstanceError, replace
from decimal import Context, Decimal, localcontext
from fractions import Fraction
import math
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4_pc import (
    CandidatePCRead,
    PCBaseChart,
    PCEnvelopeCertificate,
    PCStageError,
    ProvisionalCandidatePCStep,
    NORM_ID,
    carrier_geometry,
    scalar_zoh,
)
from pygrc.models.grc_v4_candidate_a import CandidateAWriter
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_profile import resolve_profile, list_supported_profiles
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_ci import fixture as ci_fixture, independent_point
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle
from tests.models.test_grc_v4_candidate_c import dense_current_oracle


def configure(
    before,
    *,
    radius=64.0,
    resource_radius=4.0,
    weight_lower=0.1,
    weight_upper=2.0,
    tau=0.5,
    gain=1e-5,
    z=None,
    reset_z=None,
    changes=None,
):
    ref = before.geometry.reference
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    candidate = identity["candidate"]
    chart = PCBaseChart(
        resource_radius,
        weight_lower if candidate == "A" else 1.0,
        weight_upper if candidate == "A" else 1.0,
    )
    params["realization"] = dict(
        schema_version="grcv4-pc-params-v1",
        tau_PC=tau,
        radius=radius,
        carrier_norm_id=NORM_ID,
        source_envelope_id=chart.identity,
        writer_id="zero_order_hold_exponential_v1",
    )
    params["solver"].update(solver_kind="direct", conditioning_limit=1e8)
    params["geometry"]["kappa_H"] = gain
    identity.update(
        realization="PC",
        profile_family_id=candidate + "_PC",
        solver_id="direct_unique_root_v1",
    )
    for group, values in (changes or {}).items():
        (identity if group == "identity" else params[group]).update(values)
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    n = len(ref.graph.live_edge_ids)
    z = tuple(z) if z is not None else (0.0,) * (n * n)
    reset_z = tuple(reset_z) if reset_z is not None else z
    current = GRCV4AuthoritativeState(before.current.C, before.current.W_A, z)
    reset = GRCV4AuthoritativeState(before.reset.C, before.reset.W_A, reset_z)
    inputs = replace(before, geometry=ref.geometry(), current=current, reset=reset)
    return replace(inputs, geometry=carrier_geometry(inputs, current))


def fixture(candidate="C", **kwargs):
    graph = kwargs.pop("graph", None)
    C, W = kwargs.pop("C", (3.0, 1.0)), kwargs.pop("W", (2.0,))
    before, backend = ci_fixture(candidate, graph=graph, C=C, W=W)
    return configure(before, **kwargs), backend


def zoh_oracle(z, s, dt, tau):
    # Literal scalar ODE solution at 2000 digits, no production writer/utilities.
    with localcontext(Context(prec=2000, Emin=-999999, Emax=999999)):
        d = Decimal.from_float
        ratio = d(dt) / d(tau)
        if ratio > 10000:
            return tuple(s)
        a = (-ratio).exp()
        return tuple(
            float(a * d(x) + (1 - a) * d(y)) for x, y in zip(z, s, strict=True)
        )


class PCWriterTests(unittest.TestCase):
    def test_formation_hold_release_and_equal_endpoint(self):
        for z, s in [
            ((0.0,), (2.0,)),
            ((2.0,), (0.0,)),
            ((2.0,), (2.0,)),
            ((-2.0,), (3.0,)),
        ]:
            for dt in (0.0, 0.125, 1.0, 1000.0):
                with self.subTest(z=z, s=s, dt=dt):
                    self.assertEqual(
                        scalar_zoh(z, s, dt, 2.0), zoh_oracle(z, s, dt, 2.0)
                    )
        self.assertGreater(scalar_zoh((0.0,), (2.0,), 0.125, 2.0)[0], 0)
        self.assertGreater(scalar_zoh((2.0,), (0.0,), 0.125, 2.0)[0], 0)

    def test_extreme_ratio_keeps_representable_formation_and_release(self):
        tiny, large = math.ulp(0.0), float.fromhex("0x1.fffffffffffffp+1023")
        cases = [
            ((0.0,), (large,), tiny, 1.0),
            ((0.0,), (large,), tiny, large),
            ((large,), (0.0,), 1000.0, 1.0),
            ((large,), (-large,), math.log(2.0), 1.0),
            ((tiny,), (-tiny,), 0.125, 1.0),
            ((large,), (tiny,), large, tiny),
        ]
        for z, s, dt, tau in cases:
            with self.subTest(case=(z, s, dt, tau)):
                self.assertEqual(scalar_zoh(z, s, dt, tau), zoh_oracle(z, s, dt, tau))
        self.assertNotEqual(scalar_zoh((0.0,), (large,), tiny, 1.0), (0.0,))
        self.assertNotEqual(scalar_zoh((large,), (0.0,), 1000.0, 1.0), (0.0,))

    def test_variable_duration_zero_source_matches_exponential_up_to_storage_rounding(
        self,
    ):
        z = (3.0, -2.0, 1e-200)
        durations = (0.125, 0.25, 0.5, 1.0)
        actual = z
        for dt in durations:
            actual = scalar_zoh(actual, (0.0,) * 3, dt, 2.0)
        expected = zoh_oracle(z, (0.0,) * 3, sum(durations), 2.0)
        np.testing.assert_allclose(actual, expected, rtol=5e-16, atol=0.0)

    def test_writer_rejects_invalid_types_shapes_and_times(self):
        for z, s, dt, tau in [
            ((1.0,), (), 1.0, 1.0),
            ((math.inf,), (0.0,), 1.0, 1.0),
            ((True,), (0.0,), 1.0, 1.0),
            ((1.0,), (0.0,), -1.0, 1.0),
            ((1.0,), (0.0,), 1.0, 0.0),
            ((1.0,), (0.0,), math.inf, 1.0),
            ((1.0,), (0.0,), 1.0, True),
        ]:
            with self.assertRaises((ValueError, TypeError)):
                scalar_zoh(z, s, dt, tau)

    def test_decimal_context_does_not_change_writer(self):
        from decimal import DefaultContext, Inexact, ROUND_DOWN

        expected = scalar_zoh((2.0,), (-3.0,), 0.125, 2.0)
        saved = DefaultContext.copy()
        try:
            DefaultContext.prec = 7
            DefaultContext.rounding = ROUND_DOWN
            DefaultContext.traps[Inexact] = True
            with localcontext() as ctx:
                ctx.prec = 4
                ctx.traps[Inexact] = True
                self.assertEqual(scalar_zoh((2.0,), (-3.0,), 0.125, 2.0), expected)
        finally:
            DefaultContext.prec = saved.prec
            DefaultContext.rounding = saved.rounding
            DefaultContext.traps = saved.traps.copy()


class CandidateCPCTests(unittest.TestCase):
    def test_old_carrier_full_c_chain_and_single_writer(self):
        before, _ = fixture(z=(0.5,), reset_z=(-0.25,))
        step = ProvisionalCandidatePCStep(before)
        expected = dense_current_oracle(step.read.point.inputs)
        np.testing.assert_allclose(
            step.read.point.current.values, expected["current"], rtol=1e-12
        )
        source = tuple(x for row in step.read.structural_source.increment for x in row)
        self.assertEqual(
            step.next_inputs.current.Z_4,
            zoh_oracle(before.current.Z_4, source, before.dt, 0.5),
        )
        self.assertEqual(step.carrier_writes, 1)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertIsNone(step.writer)
        self.assertEqual(step.reset_read.inputs.current.Z_4, (-0.25,))
        self.assertEqual(step.next_inputs.reset, before.reset)
        self.assertEqual(step.read.point.inputs.stage, "pc_old_history")
        self.assertEqual(step.read.point.inputs.geometry, before.geometry)
        self.assertNotEqual(step.restart.point.inputs.geometry, before.geometry)

    def test_dense_noncommuting_signed_carrier_and_nonuniform_deformation(self):
        graph = GRCV4Graph(
            ("u", "v", "w"), (OrientedEdge("a", "u", "v"), OrientedEdge("b", "v", "w"))
        )
        before, _ = fixture(
            graph=graph,
            C=(2.0, 1.0, 0.5),
            z=(0.2, -0.125, -0.125, -0.1),
            changes={"candidate": {"kappa_M_C": 0.1, "Lambda_C": 3.0}},
        )
        read = CandidatePCRead(before)
        expected = dense_current_oracle(read.point.inputs)
        np.testing.assert_allclose(
            read.point.current.values, expected["current"], rtol=2e-11, atol=1e-12
        )
        _, source = independent_point(
            before, None, np.array(before.geometry.one_form_hodge.matrix)
        )
        np.testing.assert_allclose(
            read.structural_source.increment, source, rtol=2e-11, atol=1e-12
        )
        self.assertNotEqual(read.point.algebra.selector.rank, 0)
        ProvisionalCandidatePCStep(before)

    def test_orientation_covariance_including_carrier(self):
        graph = GRCV4Graph(("u", "v"), (OrientedEdge("e", "v", "u"),))
        forward, _ = fixture(z=(0.25,))
        backward, _ = fixture(graph=graph, z=(0.25,))
        a, b = ProvisionalCandidatePCStep(forward), ProvisionalCandidatePCStep(backward)
        np.testing.assert_allclose(
            a.read.point.current.values,
            -np.array(b.read.point.current.values),
            rtol=1e-12,
        )
        self.assertEqual(a.next_inputs.current, b.next_inputs.current)

    def test_selector_boundary_and_physical_margin_reject(self):
        for changes in (
            {"candidate": {"Lambda_C": 4.0}},
            {"candidate": {"chi_C": 1.0, "zeta_C": 2.0}},
        ):
            before, _ = fixture(changes=changes)
            with self.assertRaises((PCStageError, ValueError)):
                CandidatePCRead(before)


class CandidateAPCTests(unittest.TestCase):
    def test_a_current_and_refreshed_writer_preserve_old_z_until_carrier_write(self):
        before, backend = fixture("A", z=(0.5,))
        step = ProvisionalCandidatePCStep(before, backend)
        expected_j, expected_source = independent_point(
            before, backend, np.array(before.geometry.one_form_hodge.matrix)
        )
        np.testing.assert_allclose(
            step.read.point.current.values, expected_j, rtol=1e-12
        )
        np.testing.assert_allclose(
            step.read.structural_source.increment, expected_source, rtol=1e-12
        )
        self.assertIsInstance(step.writer, CandidateAWriter)
        self.assertEqual(step.writer.authority.state.Z_4, before.current.Z_4)
        _, target = scalar_oracle(
            before.geometry.reference,
            backend,
            step.next_inputs.current.C,
            step.read.point.current.values,
        )
        expected_w = log_writer_oracle(
            before.current.W_A,
            target,
            before.dt,
            before.geometry.reference.profile.params_resolved.candidate.tau_A,
        )
        np.testing.assert_allclose(step.next_inputs.current.W_A, expected_w, rtol=1e-12)
        self.assertEqual(step.next_inputs.reset, before.reset)
        self.assertNotEqual(step.next_inputs.current.W_A, before.current.W_A)
        self.assertNotEqual(step.next_inputs.current.Z_4, before.current.Z_4)

    def test_a_differential_and_mobility_chart_are_not_c_inputs(self):
        before, backend = fixture("A")
        for bad in (None, replace(backend, regularization=2.0)):
            with self.assertRaises((PCStageError, TypeError)):
                CandidatePCRead(before, bad)
        changed = replace(before, current=replace(before.current, W_A=(2.01,)))
        with self.assertRaisesRegex(PCStageError, "base chart"):
            CandidatePCRead(changed, backend)
        c, _ = fixture()
        with self.assertRaises(TypeError):
            CandidatePCRead(c, backend)

    def test_below_floor_history_is_not_clamped(self):
        before, backend = fixture(
            "A", W=(1e-14,), weight_lower=1e-15, changes={"candidate": {"gamma": 0.0}}
        )
        read = CandidatePCRead(before, backend)
        self.assertEqual(read.point.authority.state.W_A, (1e-14,))
        self.assertLess(
            read.point.authority.state.W_A[0],
            before.geometry.reference.profile.params_resolved.candidate.W_floor,
        )

    def test_unknown_history_policy_rejects_zero_and_positive_duration(self):
        before, backend = fixture(
            "A", changes={"lifecycle": {"history_policy_id": "unimplemented"}}
        )
        for dt in (0.0, before.dt):
            with self.assertRaisesRegex(ValueError, "history"):
                ProvisionalCandidatePCStep(replace(before, dt=dt), backend)


class PCSharedTests(unittest.TestCase):
    def test_profile_domain_roundtrip_and_identity(self):
        chart = PCBaseChart(4.0, 0.1, 2.0)
        self.assertEqual(PCBaseChart.from_identity(chart.identity), chart)
        for name in (
            "missing",
            chart.identity.replace("0x1.0000000000000p+2", "4"),
            chart.identity + ":x",
        ):
            with self.assertRaises(PCStageError):
                PCBaseChart.from_identity(name)
        before, _ = fixture()
        for kwargs in ({"tau": 1.0}, {"radius": 63.0}, {"resource_radius": 3.9}):
            changed = configure(before, **kwargs)
            self.assertNotEqual(
                changed.geometry.reference.profile.complete_profile_id,
                before.geometry.reference.profile.complete_profile_id,
            )

    def test_uniform_source_bound_is_independent_of_submitted_resource_point(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate)
            first = PCEnvelopeCertificate(before, backend).bounds
            zero = replace(before, current=replace(before.current, C=(0.0, 0.0)))
            self.assertEqual(PCEnvelopeCertificate(zero, backend).bounds, first)
            # An attractive zero-source point cannot rescue a too-small ball.
            narrow = configure(zero, radius=1e-12)
            with self.assertRaisesRegex(PCStageError, "source envelope"):
                PCEnvelopeCertificate(narrow, backend)

    def test_pressure_whole_chart_corners_and_stored_source(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate)
            certificate = PCEnvelopeCertificate(before, backend)
            bound = float(Fraction(certificate.bounds["source_norm_upper"]))
            for C in ((0.0, 0.0), (4.0, 0.0), (0.0, 4.0), (2.0, 2.0)):
                for z in (-64.0, 0.0, 64.0):
                    state = replace(before.current, C=C, Z_4=(z,))
                    inputs = replace(
                        before, current=state, geometry=carrier_geometry(before, state)
                    )
                    read = CandidatePCRead(inputs, backend)
                    self.assertLessEqual(
                        abs(read.structural_source.increment[0][0]), bound
                    )

    def test_zero_duration_admits_both_states_and_advances_nothing(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(0.25,), reset_z=(-0.5,))
            before = replace(before, dt=0.0)
            with patch(
                "pygrc.models.grc_v4_pc.scalar_zoh",
                side_effect=AssertionError("writer called"),
            ):
                step = ProvisionalCandidatePCStep(before, backend)
            self.assertEqual(step.next_inputs, before)
            self.assertEqual(step.carrier_writes, 0)
            self.assertEqual(step.resource.continuity_evaluations, 0)
            self.assertIsNone(step.writer)
            self.assertNotEqual(
                step.read.inputs.geometry, step.reset_read.inputs.geometry
            )

    def test_invalid_reset_is_not_hidden_by_valid_current(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate)
            reset = replace(before.reset, Z_4=(math.nextafter(64.0, math.inf),))
            for dt in (0.0, before.dt):
                with self.assertRaises(ResourceBoundaryError) as raised:
                    ProvisionalCandidatePCStep(
                        replace(before, reset=reset, dt=dt), backend
                    )
                self.assertEqual(raised.exception.stage, "pre_read_reconstruction")

    def test_ball_geometry_domain_and_stale_old_history_are_rejected(self):
        before, _ = fixture(z=(0.5,))
        for changed in (
            replace(before, geometry=before.geometry.reference.geometry()),
            configure(before, gain=1.0, radius=64.0),
            configure(
                before, changes={"realization": {"carrier_norm_id": "undeclared"}}
            ),
        ):
            with self.assertRaises((PCStageError, ValueError)):
                CandidatePCRead(changed)
        state = replace(before.current, Z_4=(math.nextafter(64.0, math.inf),))
        changed = replace(
            before, current=state, geometry=carrier_geometry(before, state)
        )
        with self.assertRaisesRegex(PCStageError, "carrier"):
            CandidatePCRead(changed)

    def test_final_chart_failure_preserves_input_and_never_reuses_new_z(self):
        before, backend = fixture("A", weight_lower=2.0, weight_upper=2.0)
        original = before.to_payload()
        with self.assertRaises(ResourceBoundaryError) as raised:
            ProvisionalCandidatePCStep(before, backend)
        self.assertEqual(raised.exception.stage, "final_reconstruction")
        self.assertEqual(before.to_payload(), original)
        self.assertEqual(before.current.Z_4, (0.0,))

    def test_recipe_roundtrip_detaches_and_recomputes_current_reset_and_final(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(0.25,), reset_z=(-0.5,))
            step = ProvisionalCandidatePCStep(before, backend)
            payload = step.to_payload()
            rebuilt = ProvisionalCandidatePCStep.from_payload(payload)
            self.assertEqual(rebuilt.identity, step.identity)
            self.assertEqual(rebuilt.next_inputs, step.next_inputs)
            payload["inputs"]["current"]["Z_4"][0] = 19.0
            self.assertEqual(step.inputs.current.Z_4, (0.25,))
            with self.assertRaises(FrozenInstanceError):
                step.carrier_writes = 2
            bad = step.to_payload()
            bad["numerics"] = "unknown"
            with self.assertRaises(PCStageError):
                ProvisionalCandidatePCStep.from_payload(bad)

    def test_clock_index_and_charge_fail_without_history_mutation(self):
        before, _ = fixture()
        cases = [
            dict(step_index=2**53 - 1),
            dict(time=1e308, dt=1e308),
            dict(Q_target=5.0),
        ]
        for change in cases:
            altered = replace(before, **change)
            original = altered.to_payload()
            with self.assertRaises(ResourceBoundaryError):
                ProvisionalCandidatePCStep(altered)
            self.assertEqual(altered.to_payload(), original)

    def test_public_support_remains_c_os_only(self):
        self.assertEqual(len(list_supported_profiles()), 1)


class PCOutlierTests(unittest.TestCase):
    def test_once_gated_signed_source_and_no_instantaneous_feedback(self):
        for candidate in ("A", "C"):
            for zeta in (-0.125, 0.125):
                before, backend = fixture(
                    candidate,
                    z=(0.5,),
                    changes={
                        "candidate": {
                            "zeta_" + candidate: zeta,
                            "chi_" + candidate: 0.25,
                        }
                    },
                )
                step = ProvisionalCandidatePCStep(before, backend)
                j, source = independent_point(
                    before, backend, np.array(before.geometry.one_form_hodge.matrix)
                )
                np.testing.assert_allclose(
                    step.read.point.current.values, j, rtol=1e-12
                )
                np.testing.assert_allclose(
                    step.read.structural_source.increment, source, rtol=1e-12
                )
                expected = zoh_oracle(
                    before.current.Z_4, tuple(source.flat), before.dt, 0.5
                )
                np.testing.assert_allclose(
                    step.next_inputs.current.Z_4, expected, rtol=1e-14
                )
                self.assertEqual(step.read.point.inputs.current.Z_4, (0.5,))
                self.assertNotEqual(
                    step.restart.structural_source, step.read.structural_source
                )

    def test_zero_read_source_releases_history_without_clearing_it(self):
        for candidate in ("A", "C"):
            for control in ("chi_", "zeta_"):
                before, backend = fixture(
                    candidate,
                    z=(0.5,),
                    changes={"candidate": {control + candidate: 0.0}},
                )
                step = ProvisionalCandidatePCStep(before, backend)
                self.assertEqual(step.read.structural_source.increment, ((0.0,),))
                self.assertEqual(
                    step.next_inputs.current.Z_4,
                    zoh_oracle((0.5,), (0.0,), before.dt, 0.5),
                )
                self.assertGreater(step.next_inputs.current.Z_4[0], 0.0)
                self.assertNotEqual(
                    step.read.point.inputs.geometry,
                    before.geometry.reference.geometry(),
                )

    def test_one_of_each_writer_and_precontinuity_source_is_held(self):
        before, backend = fixture("A", z=(0.25,))
        with (
            patch("pygrc.models.grc_v4_pc.scalar_zoh", wraps=scalar_zoh) as z_writer,
            patch(
                "pygrc.models.grc_v4_pc.CandidateAWriter", wraps=CandidateAWriter
            ) as w_writer,
        ):
            step = ProvisionalCandidatePCStep(before, backend)
        self.assertEqual(z_writer.call_count, 1)
        self.assertEqual(w_writer.call_count, 1)
        self.assertEqual(
            z_writer.call_args.args,
            (
                before.current.Z_4,
                tuple(x for row in step.read.structural_source.increment for x in row),
                before.dt,
                0.5,
            ),
        )
        self.assertEqual(w_writer.call_args.args[0], step.read.point)

    def test_disconnected_and_isolated_components_with_signed_history(self):
        graph = GRCV4Graph(
            ("a", "b", "c", "d", "isolated"),
            (OrientedEdge("left", "a", "b"), OrientedEdge("right", "c", "d")),
        )
        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate,
                graph=graph,
                C=(1.5, 1.0, 1.0, 0.5, 0.5),
                W=(1.5, 1.0),
                z=(0.125, 0.0, 0.0, -0.125),
                changes={"candidate": {"zeta_" + candidate: 0.05}},
            )
            step = ProvisionalCandidatePCStep(before, backend)
            j, source = independent_point(
                before, backend, np.array(before.geometry.one_form_hodge.matrix)
            )
            np.testing.assert_allclose(
                step.read.point.current.values, j, rtol=1e-12, atol=1e-13
            )
            np.testing.assert_allclose(
                step.read.structural_source.increment, source, rtol=1e-12, atol=1e-13
            )
            for indices in ((0, 1), (2, 3), (4,)):
                self.assertAlmostEqual(
                    sum(step.next_inputs.current.C[i] for i in indices),
                    sum(before.current.C[i] for i in indices),
                    places=13,
                )
            self.assertEqual(step.next_inputs.current.Z_4[1:3], (0.0, 0.0))

    def test_carrier_outside_star_support_and_asymmetry_reject(self):
        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (OrientedEdge("left", "a", "b"), OrientedEdge("right", "c", "d")),
        )
        for z in ((0.0, 0.1, 0.1, 0.0), (0.0, 0.1, 0.0, 0.0)):
            with self.assertRaises(ValueError):
                fixture(graph=graph, C=(1.0, 1.0, 1.0, 1.0), z=z)

    def test_tau_extremes_and_zero_index_boundary(self):
        for candidate in ("A", "C"):
            for tau in (math.ulp(0.0), 1e308):
                before, backend = fixture(candidate, tau=tau, z=(0.5,))
                step = ProvisionalCandidatePCStep(before, backend)
                source = tuple(
                    x for row in step.read.structural_source.increment for x in row
                )
                self.assertEqual(
                    step.next_inputs.current.Z_4,
                    zoh_oracle((0.5,), source, before.dt, tau),
                )
            before, backend = fixture(candidate)
            before = replace(before, dt=0.0, step_index=2**53 - 1)
            self.assertEqual(
                ProvisionalCandidatePCStep(before, backend).next_inputs, before
            )

    def test_failed_a_writer_prevents_carrier_write(self):
        from pygrc.models.grc_v4_candidate_a import CandidateAStageError

        before, backend = fixture("A")
        original = before.to_payload()
        with (
            patch(
                "pygrc.models.grc_v4_pc.CandidateAWriter",
                side_effect=CandidateAStageError("nonfinite", "injected"),
            ),
            patch(
                "pygrc.models.grc_v4_pc.scalar_zoh",
                side_effect=AssertionError("unreached Z writer"),
            ),
        ):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidatePCStep(before, backend)
        self.assertEqual(caught.exception.stage, "history_write")
        self.assertEqual(before.to_payload(), original)

    def test_negative_geometry_gain_still_reads_old_carrier(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, gain=-1e-5, z=(0.25,))
            step = ProvisionalCandidatePCStep(before, backend)
            ref = before.geometry.reference
            self.assertLess(
                step.read.point.inputs.geometry.one_form_hodge.matrix[0][0],
                ref.pairings.one_form.matrix[0][0],
            )
            j, source = independent_point(
                before, backend, np.array(before.geometry.one_form_hodge.matrix)
            )
            np.testing.assert_allclose(step.read.point.current.values, j, rtol=1e-12)
            np.testing.assert_allclose(
                step.read.structural_source.increment, source, rtol=1e-12
            )

    def test_a_finite_exponential_chart_and_dense_nonuniform_history(self):
        graph = GRCV4Graph(
            ("a", "b", "c"), (OrientedEdge("x", "a", "b"), OrientedEdge("y", "b", "c"))
        )
        before, backend = fixture(
            "A",
            graph=graph,
            C=(1.0, 2.0, 0.5),
            W=(1.5, 0.5),
            z=(0.2, 0.125, 0.125, -0.1),
            changes={
                "candidate": {
                    "alpha": 0.1,
                    "beta": 0.05,
                    "gamma": 0.05,
                    "zeta_A": -0.05,
                }
            },
        )
        read = CandidatePCRead(before, backend)
        j, source = independent_point(
            before, backend, np.array(before.geometry.one_form_hodge.matrix)
        )
        np.testing.assert_allclose(read.point.current.values, j, rtol=1e-12)
        np.testing.assert_allclose(read.structural_source.increment, source, rtol=1e-12)
        ProvisionalCandidatePCStep(before, backend)
        excessive = configure(before, changes={"candidate": {"gamma": 1e308}})
        with self.assertRaisesRegex(PCStageError, "finite-certified"):
            CandidatePCRead(excessive, backend)


# External audit regression proposal; executed here against the actual repository.
TINY = math.ulp(0.0)


class PCAuditRegressionTests(unittest.TestCase):
    def assert_canonical_zero(self, values):
        for value in values:
            self.assertEqual(value, 0.0)
            self.assertEqual(math.copysign(1.0, value), 1.0)

    def test_scalar_signed_underflow_returns_reusable_canonical_zero(self):
        for old, source, dt, tau in (
            (-TINY, 0.0, 1.0, 1.0),
            (0.0, -TINY, 0.125, 1.0),
            (-TINY, 0.0, 1000.0, 1.0),
            (TINY, -TINY, 1.0, 1.0),
        ):
            with self.subTest(old=old, source=source, dt=dt):
                value = scalar_zoh((old,), (source,), dt, tau)
                self.assert_canonical_zero(value)
                # The writer's result must inhabit its own input domain.
                scalar_zoh(value, (source,), dt, tau)
                GRCV4AuthoritativeState((0.0,), None, value)

    def test_C_source_underflow_is_canonical_for_both_gain_signs(self):
        for zeta in (-TINY, TINY):
            with self.subTest(zeta=zeta):
                before, _ = fixture(
                    changes={
                        "candidate": {
                            "tau_C": 0.0,
                            "chi_C": 0.125,
                            "zeta_C": zeta,
                            "eta_C": 0.125,
                            "kappa_Phi_C": 0.25,
                        }
                    }
                )
                read = CandidatePCRead(before)
                self.assert_canonical_zero(
                    tuple(x for row in read.structural_source.increment for x in row)
                )

    def test_signed_release_returns_a_complete_PC_step_for_A_and_C(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, C=(0.0, 0.0), W=(1.0,), z=(-TINY,))
            before = replace(before, dt=1.0)
            snapshot = before.to_payload()
            with self.subTest(candidate=candidate):
                step = ProvisionalCandidatePCStep(before, backend)
                self.assert_canonical_zero(step.next_inputs.current.Z_4)
                self.assertEqual(step.next_inputs.current.C, before.current.C)
                self.assertEqual(step.next_inputs.reset, before.reset)
                self.assertEqual(step.carrier_writes, 1)
                self.assertEqual(before.to_payload(), snapshot)
                again = ProvisionalCandidatePCStep(step.next_inputs, backend)
                self.assert_canonical_zero(again.next_inputs.current.Z_4)

    def test_signed_edge_covariance_survives_carrier_underflow(self):
        for candidate in ("A", "C"):
            outputs = []
            for sign in (-1, 1):
                graph = GRCV4Graph(
                    ("u", "v", "w"),
                    (
                        OrientedEdge("a", "u", "v"),
                        OrientedEdge("b", "v", "w")
                        if sign < 0
                        else OrientedEdge("b", "w", "v"),
                    ),
                )
                changes = (
                    {"chi_A": 0.0}
                    if candidate == "A"
                    else {
                        "chi_C": 0.0,
                        "Lambda_C": 10.0,
                    }
                )
                before, backend = fixture(
                    candidate,
                    graph=graph,
                    C=(0.0, 0.0, 0.0),
                    W=(1.0, 1.0),
                    z=(0.0, sign * TINY, sign * TINY, 0.0),
                    changes={"candidate": changes},
                )
                step = ProvisionalCandidatePCStep(replace(before, dt=1.0), backend)
                self.assert_canonical_zero(step.next_inputs.current.Z_4)
                outputs.append(step.next_inputs.current.C)
            self.assertEqual(outputs[0], outputs[1])

    def loop_fixture(self, alpha, resource=1.0):
        graph = GRCV4Graph(("u",), (OrientedEdge("loop", "u", "u"),))
        return fixture(
            "A",
            graph=graph,
            C=(resource,),
            W=(1.0,),
            z=(0.0,),
            resource_radius=1.0,
            radius=1.0,
            gain=0.0,
            weight_lower=1.0,
            weight_upper=1.0,
            changes={"candidate": {"alpha": alpha, "beta": 0.0, "gamma": 0.0}},
        )

    def test_loop_exponent_bound_dominates_actual_finite_exponent(self):
        before, backend = self.loop_fixture(-600.0)
        certificate = PCEnvelopeCertificate(before, backend)
        bound = Fraction(certificate.bounds["conductance_exponent_absolute_upper"])
        self.assertGreaterEqual(bound, 600)
        self.assertLessEqual(bound, 700)
        read = CandidatePCRead(before, backend)
        self.assertGreater(read.point.W_hat_A[0], 0.0)
        self.assertTrue(math.isfinite(read.point.W_hat_A[0]))

    def test_loop_range_fails_whole_chart_even_at_zero_resource(self):
        # A valid zero point cannot certify a chart containing E=800.
        for resource in (0.0, 1.0):
            before, backend = self.loop_fixture(-800.0, resource)
            with self.subTest(resource=resource), self.assertRaises(PCStageError):
                PCEnvelopeCertificate(before, backend)

    def test_loopless_chart_keeps_its_tighter_endpoint_bound(self):
        before, backend = fixture(
            "A",
            C=(1.0, 0.0),
            W=(1.0,),
            z=(0.0,),
            resource_radius=1.0,
            radius=1.0,
            gain=0.0,
            weight_lower=1.0,
            weight_upper=1.0,
            changes={
                "candidate": {
                    "alpha": -800.0,
                    "beta": 0.0,
                    "gamma": 0.0,
                    "chi_A": 0.0,
                }
            },
        )
        cert = PCEnvelopeCertificate(before, backend)
        self.assertLessEqual(
            Fraction(cert.bounds["conductance_exponent_absolute_upper"]), 700
        )
        CandidatePCRead(before, backend)

    def test_half_subnormal_formation_requires_correct_rounding(self):
        # First-order formation is exactly half the smallest subnormal;
        # the higher-order exponential term puts the true answer below it.
        self.assert_canonical_zero(scalar_zoh((0.0,), (2.0**1022,), TINY, 2.0**1023))
        # Large zero-source release at ratio 1000 is still representable.
        value = scalar_zoh(
            (float.fromhex("0x1.fffffffffffffp+1023"),), (0.0,), 1000.0, 1.0
        )[0]
        self.assertGreater(value, 0.0)


class PCReconciliationTests(unittest.TestCase):
    def test_negative_zero_input_remains_forbidden_at_every_writer_branch(self):
        for dt in (0.0, 1.0, 1600.0):
            for old, source in (
                ((-0.0,), (0.0,)),
                ((0.0,), (-0.0,)),
                ((-0.0,), (-0.0,)),
            ):
                with (
                    self.subTest(dt=dt, old=old, source=source),
                    self.assertRaises(ValueError),
                ):
                    scalar_zoh(old, source, dt, 1.0)
        with self.assertRaises(ValueError):
            GRCV4AuthoritativeState((0.0,), None, (-0.0,))

    def test_mixed_graph_loop_endpoint_bound_and_exact_range_boundary(self):
        graph = GRCV4Graph(
            ("a", "b", "loop-only"),
            (
                OrientedEdge("edge", "a", "b"),
                OrientedEdge("loop", "loop-only", "loop-only"),
            ),
        )
        for alpha in (-700.0, 700.0):
            before, backend = fixture(
                "A",
                graph=graph,
                C=(0.0, 0.0, 1.0),
                W=(1.0, 1.0),
                resource_radius=1.0,
                radius=1.0,
                gain=0.0,
                changes={
                    "candidate": {
                        "alpha": alpha,
                        "beta": 0.0,
                        "gamma": 0.0,
                        "chi_A": 0.0,
                    }
                },
            )
            cert = PCEnvelopeCertificate(before, backend)
            self.assertEqual(
                Fraction(cert.bounds["conductance_exponent_absolute_upper"]), 700
            )
            read = CandidatePCRead(before, backend)
            # Independent local law: zero loop incidence/gradient/current
            # leaves exp(-alpha*C_loop), with its declared conductance floor.
            p = before.geometry.reference.profile.params_resolved.candidate
            expected = max(p.W_floor, math.exp(-alpha))
            np.testing.assert_allclose(read.point.W_hat_A[1], expected, rtol=2e-14)
            outside = configure(
                before,
                resource_radius=1.0,
                radius=1.0,
                gain=0.0,
                changes={
                    "candidate": {
                        "alpha": math.nextafter(alpha, math.copysign(math.inf, alpha))
                    }
                },
            )
            zero = replace(outside, current=replace(outside.current, C=(0.0, 0.0, 0.0)))
            with self.assertRaisesRegex(PCStageError, "finite-certified"):
                PCEnvelopeCertificate(zero, backend)

    def test_weight_chart_corners_share_one_source_envelope(self):
        before, backend = fixture("A")
        bounds = PCEnvelopeCertificate(before, backend).bounds
        upper = Fraction(bounds["source_norm_upper"])
        for w in (0.1, 2.0):
            for C in ((4.0, 0.0), (0.0, 4.0)):
                state = replace(before.current, C=C, W_A=(w,))
                sample = replace(before, current=state)
                read = CandidatePCRead(sample, backend)
                self.assertEqual(read.certificate.bounds, bounds)
                self.assertLessEqual(
                    abs(Fraction(read.structural_source.increment[0][0])), upper
                )
                j, source = independent_point(
                    sample, backend, np.array(sample.geometry.one_form_hodge.matrix)
                )
                np.testing.assert_allclose(read.point.current.values, j, rtol=1e-12)
                np.testing.assert_allclose(
                    read.structural_source.increment, source, rtol=1e-12
                )

    def test_midpoint_refines_and_signed_underflow_rounds_to_canonical_zero(self):
        precisions = []

        def observed_context(**kwargs):
            precisions.append(kwargs["prec"])
            return Context(**kwargs)

        for sign in (-1, 1):
            precisions.clear()
            with patch("pygrc.models.grc_v4_pc.Context", side_effect=observed_context):
                actual = scalar_zoh((0.0,), (sign * 2.0**1022,), TINY, 2.0**1023)
            self.assertEqual(precisions, [800, 1600])
            self.assertEqual(actual, (0.0,))
            self.assertEqual(math.copysign(1.0, actual[0]), 1.0)
            # Ordinary neighbours of a cancellation midpoint are also
            # checked against the independent 2000-digit real-law oracle.
        for dt in (
            math.nextafter(math.log(2.0), 0.0),
            math.log(2.0),
            math.nextafter(math.log(2.0), math.inf),
        ):
            expected = zoh_oracle((TINY,), (-TINY,), dt, 1.0)
            result = scalar_zoh((TINY,), (-TINY,), dt, 1.0)
            self.assertEqual(result, expected)
            self.assertEqual(math.copysign(1.0, result[0]), 1.0)

    def test_selector_cutoff_is_domain_failure_before_any_current_solve(self):
        before, _ = fixture(changes={"candidate": {"Lambda_C": 4.0}}, gain=0.0)
        with patch(
            "pygrc.models.grc_v4_pc.CandidateCCurrent",
            side_effect=AssertionError("current must not run"),
        ):
            with self.assertRaisesRegex(PCStageError, "selector cutoff") as direct:
                PCEnvelopeCertificate(before)
            self.assertEqual(direct.exception.disposition, "domain_failure")
            for dt in (0.0, before.dt):
                with self.assertRaises(ResourceBoundaryError) as error:
                    ProvisionalCandidatePCStep(replace(before, dt=dt))
                self.assertEqual(error.exception.stage, "pre_read_reconstruction")
                self.assertEqual(error.exception.code, "domain_failure")
        # Exact adjacent cutoffs have positive gap; the failure is neither
        # a numerical cutoff tolerance nor a statement about physical J.
        for cutoff in (math.nextafter(4.0, 0.0), math.nextafter(4.0, math.inf)):
            adjacent = configure(
                before, gain=0.0, changes={"candidate": {"Lambda_C": cutoff}}
            )
            self.assertGreater(
                Fraction(PCEnvelopeCertificate(adjacent).bounds["selector_gap_lower"]),
                0,
            )

    def test_matched_forcing_does_not_mean_identical_held_sources(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, gain=1e-3, z=(0.25,))
            other = replace(before.current, Z_4=(-0.25,))
            alternate = replace(
                before, current=other, geometry=carrier_geometry(before, other)
            )
            first, second = (
                CandidatePCRead(before, backend),
                CandidatePCRead(alternate, backend),
            )
            s1, s2 = (
                first.structural_source.increment[0][0],
                second.structural_source.increment[0][0],
            )
            self.assertNotEqual(s1, s2)
            z1 = scalar_zoh((0.25,), (s1,), 1.0, 0.5)[0]
            z2 = scalar_zoh((-0.25,), (s2,), 1.0, 0.5)[0]
            with localcontext(Context(prec=2000)):
                a = Decimal(-2).exp()
                expected = a * Decimal(0.5) + (1 - a) * (
                    Decimal.from_float(s1) - Decimal.from_float(s2)
                )
                held_only = float(a * Decimal(0.5))
            self.assertAlmostEqual(
                z1 - z2, float(expected), delta=4 * math.ulp(float(expected))
            )
            self.assertGreater(abs((z1 - z2) - held_only), 8 * math.ulp(held_only))

    def test_reset_resource_and_a_weight_have_independent_chart_admission(self):
        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate, resource_radius=3.2, z=(0.25,), reset_z=(-0.5,)
            )
            reset = replace(
                before.reset, C=(1.0, 3.0), W_A=(1.2,) if candidate == "A" else None
            )
            valid = replace(before, reset=reset, dt=0.0)
            step = ProvisionalCandidatePCStep(valid, backend)
            self.assertEqual(step.reset_read.point.inputs.current, reset)
            self.assertNotEqual(
                step.reset_read.point.inputs.geometry, step.read.point.inputs.geometry
            )
            self.assertEqual(step.next_inputs, valid)
            invalid = [replace(reset, C=(4.0, 0.0))]
            if candidate == "A":
                invalid.append(replace(reset, W_A=(0.05,)))
            for state in invalid:
                for dt in (0.0, before.dt):
                    current = replace(before, reset=state, dt=dt)
                    snapshot = current.to_payload()
                    with self.assertRaises(ResourceBoundaryError) as error:
                        ProvisionalCandidatePCStep(current, backend)
                    self.assertEqual(error.exception.stage, "pre_read_reconstruction")
                    self.assertEqual(error.exception.code, "domain_failure")
                    self.assertEqual(current.to_payload(), snapshot)

    def test_c_offdiagonal_source_underflow_with_positive_gain(self):
        for reversed_edge in (False, True):
            graph = GRCV4Graph(
                ("u", "v", "w"),
                (
                    OrientedEdge("a", "u", "v"),
                    OrientedEdge("b", "w", "v")
                    if reversed_edge
                    else OrientedEdge("b", "v", "w"),
                ),
            )
            before, _ = fixture(
                graph=graph,
                C=(0.0, 1.0, 0.0),
                changes={
                    "candidate": {
                        "zeta_C": TINY,
                        "chi_C": 0.125,
                        "eta_C": 0.125,
                        "kappa_Phi_C": 0.125,
                        "tau_C": 0.0,
                        "Lambda_C": 10.0,
                    }
                },
            )
            read = CandidatePCRead(before)
            flat = read.point.read.causal_flat.values
            self.assertEqual(flat[0] * flat[1] > 0, reversed_edge)
            for row in read.structural_source.increment:
                for x in row:
                    self.assertEqual(x, 0.0)
                    self.assertEqual(math.copysign(1.0, x), 1.0)
