"""Bounded pressure for C_RG2b .1–.4; no source-to-completion campaign."""

import unittest
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch

import crg2b_native_spark_pressure_oracle as audit
from crg2b_native_spark_oracle import encoded, norm, verify_step
from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M
from p991a6_crg2b_preflight import transition
from p991a6_crg2b_subjects import request

from pygrc.models import grc_9_v4_completion_crg2b as curve
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import CertificationInconclusive
from pygrc.models.grc_v4_spark_crg2b import SparkCRG2bKernel, _section_witness
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_crg2b as baseline


class CRG2bPressureTests(unittest.TestCase):
    synthetic_window_fixture = baseline.NativeCRG2bTests.synthetic_window_fixture

    @classmethod
    def setUpClass(cls):
        baseline.NativeCRG2bTests.setUpClass()
        for name in ("config", "source_model", "event_model", "certificates", "center"):
            setattr(cls, name, getattr(baseline.NativeCRG2bTests, name))
        cls.target = cls.event_model.configuration
        cls.k = owner.kernel(cls.target)
        cls.steps = {
            role: cls.k.step(getattr(cls.target, role)) for role in ("current", "reset")
        }
        cls.evidence = {
            "steps": {role: transition(step) for role, step in cls.steps.items()},
            "subject": cls.target.to_payload(),
            "manufactured": {},
            "certificate": cls.certificates[0].to_payload(),
        }
        cls.measurements = {"mutations": [], "full_trajectory_runs": 0}

    def reject(self, label, action):
        with self.assertRaises(
            (
                AssertionError,
                ValueError,
                TypeError,
                IndexError,
                CertificationInconclusive,
            )
        ):
            action()
        self.measurements["mutations"].append(label)

    def read(self, witness, state=None):
        return audit.audit_read(
            self.target.reference.graph.to_payload(),
            self.target.reference.profile.to_payload(),
            state or self.target.current,
            witness,
        )

    def test_exact_manufactured_one_and_two_inverse_levels(self):
        from pygrc.models import grc_v4_spark_crg2b_math as section_math

        graph = self.config.reference.graph.to_payload()
        with ctx.workprec(256):
            native = owner.kernel(self.config).section_math()
            for depth in (1, 2):
                rows = audit.manufactured(graph, depth)
                self.evidence["manufactured"][str(depth)] = rows
                result = audit.exact_chain(graph, rows)
                self.assertFalse(result["infinite_section_claimed"])
                for i in range(1, len(rows)):
                    X, H, target = M(rows[i]["X"]), M(rows[i]["H"]), M(rows[i - 1]["X"])
                    proposed, _ = native.inverse_proposal(
                        arb_mat(target), arb_mat(H), arb_mat(X)
                    )
                    self.assertLess(norm(proposed - arb_mat(X)), arb(2) ** -180)
                    actual = native.lag(
                        arb_mat(X), native.operators(arb_mat(H)), retract=True
                    )
                    exact = audit.fixed(graph, X, H)
                    for key, name in (
                        ("current", "J"),
                        ("causal_flat", "flat"),
                        ("baseline", "j0"),
                        ("geometry", "H"),
                    ):
                        self.assertTrue(
                            all(
                                a.overlaps(b)
                                for a, b in zip(
                                    actual[key].entries(),
                                    arb_mat(exact[name]).entries(),
                                    strict=True,
                                )
                            )
                        )
                self.assertNotEqual(rows[0]["H"], rows[1]["H"])
                # Exercise the actual finite-chain loop at N=1,2. Its policy
                # and tail are test-local; production remains fixed at N=32.
                X0 = M(rows[0]["X"])
                point = arb_mat([[arb(x).mid()] for x in X0.entries()])
                original_tail = native.bounds["section_tail"]
                try:
                    native.bounds["section_tail"] = (
                        native.bounds["graph_transform_contraction"] ** depth
                        * native.bounds["section_value_radius"]
                    )
                    with patch.object(section_math, "DEPTH", depth):
                        finite = native.section(point, retain_chain=True)
                    finite_error = finite["residual_error"] + arb(Q(1, 256)) * norm(
                        point - arb_mat(X0)
                    )
                    self.assertTrue(
                        all(
                            abs(x - y) < finite_error
                            for x, y in zip(
                                finite["proposal"].entries(),
                                arb_mat(M(rows[0]["H"])).entries(),
                                strict=True,
                            )
                        )
                    )
                    self.assertEqual(len(finite["chain"]), depth)
                finally:
                    native.bounds["section_tail"] = original_tail
                wrong = deepcopy(rows)
                wrong[0]["H"] = wrong[1]["H"]
                self.reject(
                    f"depth{depth}_wrong_output_level",
                    lambda wrong=wrong: audit.exact_chain(graph, wrong),
                )
                wrong = deepcopy(rows)
                wrong[-1]["X"][0][0] = "2"
                self.reject(
                    f"depth{depth}_deepest_inverse",
                    lambda wrong=wrong: audit.exact_chain(graph, wrong),
                )
                X0 = M(rows[0]["X"])
                self.assertNotEqual(
                    audit.fixed(graph, X0, M(rows[1]["H"]))["H"], M(rows[0]["H"])
                )
                if depth == 2:
                    wrong = deepcopy(rows)
                    wrong[1]["H"] = rows[-1]["H"]
                    self.reject(
                        "reference_H_at_all_inverse_levels",
                        lambda wrong=wrong: audit.exact_chain(graph, wrong),
                    )

    def test_argument_only_clipping_signed_auxiliary_and_overlap_multiplicity(self):
        graph = self.target.reference.graph.to_payload()
        B, I, O, _, _ = audit.algebra(graph)
        X = M([[Q(-1, 8) if i == 0 else Q(2)] for i in range(B.nrows())])
        Y = M(X)
        Y[0, 0] -= Q(1, 4)
        a, b = audit.fixed(graph, X, I), audit.fixed(graph, Y, I)
        self.assertEqual(a["H"], b["H"])
        self.assertEqual(a["J"], b["J"])
        self.assertEqual(b["X"] - a["X"], Y - X)
        self.assertEqual(sum(a["X"].entries()), sum(X.entries()))
        with ctx.workprec(256):
            native = self.k.section_math()
            for C, exact in ((X, a), (Y, b)):
                read = native.lag(arb_mat(C), native.operators(native.I), retract=True)
                self.assertTrue(
                    all(
                        x.overlaps(y)
                        for x, y in zip(
                            (arb_mat(C) + read["increment"]).entries(),
                            arb_mat(exact["X"]).entries(),
                            strict=True,
                        )
                    )
                )
            self.assertNotEqual(
                sum(native.clip(arb_mat(X)).entries()), sum(X.entries())
            )
        self.assertTrue(all(O[i, i] == 2 for i in range(O.nrows())))
        self.assertTrue(
            any(a["H"][i, i] != 1 + a["flat"][i, 0] ** 2 / 8 for i in range(I.nrows()))
        )
        self.reject(
            "signed_auxiliary_is_not_physical_readmission",
            lambda: ExactResources(
                self.center.graph, tuple(map(str, X.entries())), str(sum(X.entries()))
            ),
        )

    def test_all_chain_levels_and_separate_error_terms(self):
        w = self.steps["current"].section
        with ctx.workprec(768):
            self.assertTrue(self.read(w)["checks"]["level_weighted_residuals"])
            changes = {
                "deepest_X": lambda d: d["chain"][-1]["X"].__setitem__(0, "2"),
                "interior_H": lambda d: d["chain"][16]["H"].__setitem__(0, "1"),
                "missing_level": lambda d: d["chain"].pop(16),
                "reordered_levels": lambda d: d["chain"].reverse(),
                "terminal_nonidentity": lambda d: d["chain"][-1]["H"].__setitem__(
                    0, "1025/1024"
                ),
                "wrong_output_H1": lambda d: d.update(
                    proposal=encoded(self.k.section_math().I)
                ),
                "zero_tail": lambda d: d.update(section_tail=["0", "0"]),
                "zero_residual": lambda d: d.update(residual_error=["0", "0"]),
                "zero_reported_maximum": lambda d: d.update(state_residual=["0", "0"]),
                "X0_binding": lambda d: d["query_proposal"].__setitem__(0, "2"),
                "query_nonsymmetric": lambda d: d["proposal"][0].__setitem__(
                    1, ["1/1000000"] * 2
                ),
            }
            for name, change in changes.items():
                bad = w.to_dict()
                change(bad)
                self.reject(name, lambda bad=bad: self.read(FrozenJSONMap(bad)))

    def test_corrected_charts_duration_and_complete_external_binding(self):
        with ctx.workprec(768):
            w = self.steps["current"].section
            self.read(w)
            for key, value in {
                "resource_agreement": ["1/2", "7/2"],
                "K_minus": ["7/8", "25/8"],
                "K": ["9/16", "55/16"],
                "geometry_radius": "1/512",
                "section_lipschitz": "1/128",
                "section_tail": "0",
            }.items():
                bad = w.to_dict()
                bad["completion"][key] = value
                self.reject(
                    "target_wrong_" + key, lambda bad=bad: self.read(FrozenJSONMap(bad))
                )
            for key in ("graph", "profile", "state"):
                bad = w.to_dict()
                source = (
                    owner.kernel(self.config).readmission(self.config.current).to_dict()
                )
                bad[key] = source[key]
                self.reject(
                    "external_" + key, lambda bad=bad: self.read(FrozenJSONMap(bad))
                )
            bad = w.to_dict()
            bad["numerical_policy_id"] = "duration32_section"
            self.reject(
                "duration32_section", lambda bad=bad: self.read(FrozenJSONMap(bad))
            )
            self.reject(
                "other_role_section", lambda: self.read(self.steps["reset"].section)
            )
        for duration in ("0", "32"):
            self.reject(
                "public_duration_" + duration,
                lambda duration=duration: self.k.step(self.target.current, duration),
            )

    def test_time_shift_on_unrounded_image_not_same_state_root(self):
        with ctx.workprec(768):
            self.evidence["time_shift"] = audit.time_shift(
                self.target.reference.graph.to_payload(),
                self.target.reference.profile.to_payload(),
                self.target.current,
                self.steps["current"].section,
            )
        self.assertTrue(self.evidence["time_shift"]["same_state_identity_rejected"])

    def test_wrong_CI_and_OS_geometry_substitutions(self):
        with ctx.workprec(768):
            m = audit.model(self.target.reference.graph.to_payload())
            C = audit.vector(self.target.current.C)
            H = m.I
            # A converged same-state proposal remains a different equation.
            for _ in range(14):
                _, flat = m.direct_similarity_read(C, H, m.q(1, 1024))
                H = arb_mat(
                    [[x.mid() for x in row] for row in m.geometry(flat).tolist()]
                )
            _, f = m.direct_similarity_read(C, H, m.q(1, 1024))
            self.assertLess(norm(H - m.geometry(f)), arb(2) ** -160)
            for label, candidate in (("CI_same_state", H), ("OS_identity", m.I)):
                bad = self.steps["current"].section.to_dict()
                bad["proposal"] = encoded(candidate)
                self.reject(label, lambda bad=bad: self.read(FrozenJSONMap(bad)))
            self.measurements["CI_same_state_residual_upper"] = str(
                norm(H - m.geometry(f)).fmpq()
            )

    def test_cold_warm_cleared_state_only_reconstruction(self):
        with ctx.workprec(768):
            for role in ("current", "reset"):
                state = getattr(self.target, role)
                for _ in range(2):
                    _section_witness.cache_clear()
                    cold = self.k.step(state)
                    warm = self.k.step(state)
                    self.assertEqual(cold, warm)
                    _section_witness.cache_clear()
                    rebuilt = ExactResources.from_canonical_bytes(
                        state.to_canonical_bytes()
                    )
                    self.assertEqual(self.k.step(rebuilt), cold)
                    self.assertTrue(verify_step(cold, fresh=False)["full_step_error"])
                    state = cold.after
        self.measurements["cold_warm_state_only_checkpoints"] = 4

    def test_cache_poison_is_detached_and_cross_subject_reuse_rejected(self):
        a = self.k.readmission(self.target.current)
        poisoned = a.to_dict()
        poisoned["geometry"][0][0] = ["1", "1"]
        self.assertEqual(self.k.readmission(self.target.current), a)
        other = self.k.readmission(self.target.reset)
        self.assertNotEqual(other, a)
        with ctx.workprec(768):
            self.reject("other_state_valid_shape_cache_value", lambda: self.read(other))
            self.reject(
                "unchanged_geometry_for_shifted_state",
                lambda: self.read(a, self.steps["current"].after),
            )
            opposite = self.source_model.duplicate()
            self.assertTrue(opposite.expand(request(opposite, -1)).committed)
            wrong = owner.kernel(opposite.configuration).readmission(
                opposite.configuration.current
            )
            self.reject("same_size_other_graph_cache_value", lambda: self.read(wrong))
        self.measurements["forward_section_propagation_used"] = False
        self.assertEqual(self.k.cache_info()["section"]["maxsize"], 8)

    def test_full_represented_error_and_exact_charge_are_separate(self):
        with ctx.workprec(768):
            for role, step in self.steps.items():
                self.assertTrue(verify_step(step, fresh=False)["full_step_error"])
                self.assertEqual(sum(map(Q, step.after.C)), Q(21))
                self.assertEqual(step.after, step.before.advance(step.flux, "8"))
                self.reject(
                    role + "_zero_incidence_error",
                    lambda step=step: verify_step(
                        replace(step, componentwise_error_bounds=("0",) * 15),
                        fresh=False,
                    ),
                )
                bad = step.section.to_dict()
                bad["baseline"][0][0] = ["0", "0"]
                self.reject(
                    role + "_missing_H_potential_consumer",
                    lambda bad=bad, step=step: self.read(
                        FrozenJSONMap(bad), step.before
                    ),
                )
        proof = self.certificates[0].proof
        self.assertLess(Q(proof["full_step_error"]), Q(proof["image_margin"]))
        local = proof["local_section"]
        physical = proof["physical_difference_bound"]
        self.assertGreater(Q(physical["section_difference_correction"][0]), 0)
        self.assertNotEqual(
            local["inverse_increment_lipschitz"], physical["contraction"]
        )
        self.assertFalse(proof["section_C1_claimed"])

    def test_exact_chebyshev_composition_and_degree120_residual(self):
        with ctx.workprec(256):
            m = self.k.section_math()
            rho = Q(999, 1000)
            Qc = M(self.certificates[0].operands["curve"])
            _, R = curve.reference_residual(m, Qc, rho)
            self.assertEqual(R.ncols(), 121)
            self.assertTrue(any(R[i, k] for i in range(15) for k in range(41, 121)))
            for s in (Q(0), Q(1, 7), Q(1)):
                C = curve.curve_at(Qc, s)
                fixed = audit.fixed(
                    self.target.reference.graph.to_payload(),
                    C,
                    audit.algebra(self.target.reference.graph.to_payload())[1],
                    retract=False,
                )
                self.assertEqual(
                    curve.curve_at(R, s), fixed["X"] - curve.curve_at(Qc, rho * s)
                )
            small = M([[Q(i + j + 1, 100) for j in range(3)] for i in range(15)])
            # Constant total charge is necessary for the residual metric.
            for j in (1, 2):
                small[14, j] = -sum(small[i, j] for i in range(14))
            _, residual = curve.reference_residual(m, small, rho)
            s = Q(2, 5)
            C = curve.curve_at(small, s)
            expected = audit.fixed(
                self.target.reference.graph.to_payload(),
                C,
                audit.algebra(self.target.reference.graph.to_payload())[1],
                retract=False,
            )["X"] - curve.curve_at(small, rho * s)
            self.assertEqual(curve.curve_at(residual, s), expected)
            wrong = M([[small[i, j] * rho**j for j in range(3)] for i in range(15)])
            self.assertNotEqual(
                curve.curve_at(wrong, s), curve.curve_at(small, rho * s)
            )
        self.measurements["continuous_residual_degree"] = 120

    def test_all_tangent_directions_boundary_parameters_and_charge(self):
        c = self.certificates[0]
        graph = self.target.reference.graph.to_payload()
        Qc = M(c.operands["curve"])
        P = audit.algebra(graph)[4]
        R = Q(1, 4096)
        count = 0
        with ctx.workprec(256):
            for s in (Q(0), Q(1, 7), Q(1)):
                center = curve.curve_at(Qc, s)
                for i in range(14):
                    d = M([[int(j == i) - int(j == 14)] for j in range(15)])
                    limit = arb(R) / arb((d.transpose() * P * d)[0, 0]).sqrt()
                    # Two exact rational distances strictly bracket the tube at this s.
                    for factor, inside in (
                        (Q(999, 1000), True),
                        (Q(1001, 1000), False),
                    ):
                        X = center + d * (limit.mid().fmpq() * factor)
                        values = tuple(map(str, X.entries()))
                        if inside:
                            audit.membership(graph, Qc, values, s)
                        else:
                            self.reject(
                                f"outside_witness_{s}_{i}",
                                lambda values=values, s=s: audit.membership(
                                    graph, Qc, values, s
                                ),
                            )
                        count += 1
            center = tuple(map(str, curve.curve_at(Qc, Q(1, 2)).entries()))
            for s in ("-1/1000", "1001/1000"):
                self.reject(
                    "out_of_range_parameter_" + s,
                    lambda s=s: audit.membership(graph, Qc, center, s),
                )
            off = list(center)
            off[-1] = str(Q(off[-1]) + Q(1, 2**30))
            self.reject(
                "offcharge_last_coordinate",
                lambda: audit.membership(graph, Qc, off, Q(1, 2)),
            )
            for s in (Q(1, 2), Q(1, 2) + Q(1, 2**30)):
                audit.membership(graph, Qc, center, s)
        self.measurements["exact_tube_boundary_witness_checks"] = count

    def test_certificate_rejects_sampled_truncated_and_reference_only_proofs(self):
        original = self.certificates[0].to_payload()
        changes = {
            "truncated_residual_degree": lambda d: d["proof"].update(
                residual_degree=40
            ),
            "sampled_parameters_only": lambda d: d["proof"].update(
                all_parameters_certified_continuously=False
            ),
            "per_ball_only_contraction": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(all_independent_coordinates=False),
            "omitted_section_difference": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(section_difference_correction=["0", "0"]),
            "omitted_section_value": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(geometry_value_correction=["0", "0"]),
            "old_future_tail": lambda d: d["proof"].update(
                future_trajectory_required=True,
                supporting_trajectory_steps_after_completion=2089,
            ),
            "curve_coefficient_charge": lambda d: d["operands"]["curve"][
                -1
            ].__setitem__(40, "1"),
            "transported_history": lambda d: d["operands"]["binding"].update(
                state_channels=["C", "Z_4"]
            ),
            "duration32_domain": lambda d: d["operands"]["binding"].update(
                duration="32"
            ),
        }
        for label, change in changes.items():
            bad = deepcopy(original)
            change(bad)
            self.reject(label, lambda bad=bad: CompletionCertificate.from_payload(bad))
        with ctx.workprec(256):
            # The native bound uses the common convex hull, hence also pairs in
            # different balls of the nonconvex union. Compare separated centres.
            c = self.certificates[0]
            Qc = M(c.operands["curve"])
            P = audit.algebra(self.target.reference.graph.to_payload())[4]
            states = [
                replace(self.center, C=tuple(map(str, curve.curve_at(Qc, s).entries())))
                for s in (Q(0), Q(1))
            ]
            steps = [self.k.step(s) for s in states]
            d = M(
                [[Q(a) - Q(b)] for a, b in zip(states[0].C, states[1].C, strict=True)]
            )
            y = M(
                [
                    [Q(a) - Q(b)]
                    for a, b in zip(steps[0].after.C, steps[1].after.C, strict=True)
                ]
            )
            self.assertLess(
                arb((y.transpose() * P * y)[0, 0]).sqrt(),
                arb(Q(c.proof["q"])) * arb((d.transpose() * P * d)[0, 0]).sqrt()
                + 2 * arb(Q(c.proof["full_step_error"])),
            )

    def test_actual_event_preserves_both_source_allocations_and_reset(self):
        event = self.event_model._operation._published.completion.event
        self.assertEqual(self.source_model.configuration.reset, self.config.reset)
        self.assertNotEqual(
            self.source_model.configuration.current, self.config.current
        )
        self.assertEqual(self.source_model.configuration.time, "8")
        T = M(event["transfer"])
        for role in ("current", "reset"):
            source = getattr(self.source_model.configuration, role)
            target = getattr(self.target, role)
            self.assertEqual(
                T * M([[Q(x)] for x in source.C]), M([[Q(x)] for x in target.C])
            )
            values = dict(
                zip(target.graph.live_node_ids, map(Q, target.C), strict=True)
            )
            parent = Q(source.C[source.graph.live_node_ids.index("v")])
            self.assertEqual(values[event["module"][0]], 0)
            for node, share in zip(
                event["module"][1:],
                (Q(5, 2048), Q(1021, 1024), Q(1, 2048)),
                strict=True,
            ):
                self.assertEqual(values[node], parent * share)
            self.assertEqual(self.k.readmission(target)["physical_state"], ("C",))

    def test_deepest_inverse_fixed_solve_and_returned_failures_retry_atomically(self):
        from pygrc.models.grc_v4_spark_crg2b_math import SectionMath

        for fault in ("deepest_inverse", "fixed_solve", "returned_section"):
            m = self.event_model.duplicate()
            before = m.snapshot()
            ledger = m.receipt_ledger
            _section_witness.cache_clear()
            calls = []
            if fault == "deepest_inverse":
                original = SectionMath.inverse_proposal

                def fail(self, *args, calls=calls, original=original):
                    calls.append(1)
                    if len(calls) == 32:
                        raise CertificationInconclusive("injected deepest inverse")
                    return original(self, *args)

                context = patch.object(SectionMath, "inverse_proposal", fail)
            elif fault == "fixed_solve":
                # Admit and cache the incoming section before failing the
                # held-H poststate operator solve (after exact continuity).
                self.k.readmission(m.configuration.current)
                original = SectionMath.operators

                def fail(self, H, calls=calls, original=original):
                    calls.append(1)
                    if len(calls) == 2:
                        raise CertificationInconclusive("injected fixed-H solve")
                    return original(self, H)

                context = patch.object(SectionMath, "operators", fail)
            else:
                original = SparkCRG2bKernel._admitted_section

                def fail(self, state, calls=calls, original=original):
                    calls.append(1)
                    result = original(self, state)
                    if len(calls) == 2:
                        raise CertificationInconclusive(
                            "injected post-section solve/read"
                        )
                    return result

                context = patch.object(SparkCRG2bKernel, "_admitted_section", fail)
            with context:
                self.assertFalse(m.step().committed)
            self.assertEqual(m.snapshot(), before)
            self.assertEqual(m.receipt_ledger, ledger)
            self.assertTrue(m.step().committed)
            self.assertEqual(m.configuration.current, self.steps["current"].after)
            self.assertEqual(m.configuration.time, "16")

    def test_reset_only_event_readmission_failure_and_observer_purity(self):
        m = self.source_model.duplicate()
        before = m.snapshot()
        ledger = m.receipt_ledger
        original = SparkCRG2bKernel.readmission
        calls = []

        def fail(k, state):
            if len(state.C) == 15:
                calls.append(state)
                if len(calls) == 2:
                    raise CertificationInconclusive("injected target reset readmission")
            return original(k, state)

        with patch.object(SparkCRG2bKernel, "readmission", fail):
            self.assertFalse(m.expand(request(m)).committed)
        self.assertEqual(len(calls), 2)
        self.assertEqual(m.snapshot(), before)
        self.assertEqual(m.receipt_ledger, ledger)
        self.assertTrue(m.expand(request(m)).committed)
        a = m.duplicate()
        b = m.duplicate()
        before = a.snapshot()
        with patch.object(
            SparkCRG2bKernel,
            "step",
            side_effect=AssertionError("observation advanced time"),
        ):
            for _ in range(3):
                a.compute_observables()
        self.assertEqual(a.snapshot(), before)
        _section_witness.cache_clear()
        self.assertTrue(a.step().committed)
        for _ in range(2):
            b.compute_observables()
        self.assertTrue(b.step().committed)
        self.assertEqual(a.configuration.current, b.configuration.current)
        self.assertEqual(a.configuration.reset, b.configuration.reset)
        self.assertEqual(a.configuration.time, b.configuration.time)


if __name__ == "__main__":
    unittest.main()
