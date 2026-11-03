"""Bounded A_RG2b pressure: joint inverse/history/continuous domain, never .5."""

import unittest
from copy import deepcopy
from dataclasses import replace
from math import comb
from unittest.mock import patch

import arg2b_native_spark_pressure_oracle as audit
from arg2b_native_spark_oracle import verify_step
from crg2b_native_spark_oracle import decoded, encoded, norm
from flint import arb, arb_mat, arb_series, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M
from p991a6_arg2b_preflight import transition
from p991a6_arg2b_subjects import profile, request

from pygrc.models import grc_9_v4_completion_arg2b as curve
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_arg2b_math as maths
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import CertificationInconclusive
from pygrc.models.grc_v4_spark_arg2b import SparkARG2bKernel, _section_witness
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_arg2b as baseline


class ARG2bPressureTests(unittest.TestCase):
    synthetic_window_fixture = baseline.NativeARG2bTests.synthetic_window_fixture

    @classmethod
    def setUpClass(cls):
        baseline.NativeARG2bTests.setUpClass()
        for name in ("config", "source_model", "event_model", "certificates", "center"):
            setattr(cls, name, getattr(baseline.NativeARG2bTests, name))
        cls.target = cls.event_model.configuration
        cls.k = owner.kernel(cls.target)
        cls.graph = cls.target.reference.graph.to_payload()
        cls.steps = {
            r: cls.k.step(getattr(cls.target, r)) for r in ("current", "reset")
        }
        cls.evidence = {
            "subject": cls.target.to_payload(),
            "steps": {r: transition(s) for r, s in cls.steps.items()},
            "manufactured": {},
            "certificate": cls.certificates[0].to_payload(),
        }
        cls.measurements = {"mutations": [], "full_trajectory_runs": 0}

    def reject(self, label, action, reason=None):
        with self.assertRaises(
            (
                AssertionError,
                ValueError,
                TypeError,
                IndexError,
                CertificationInconclusive,
            )
        ) as error:
            action()
        message = str(error.exception)
        if reason:
            self.assertIn(reason, message)
        self.measurements["mutations"].append({"label": label, "detected_by": message})

    def read(self, witness, state=None):
        return audit.audit_read(
            self.graph,
            self.target.reference.profile.to_payload(),
            state or self.target.current,
            witness,
        )

    def test_manufactured_joint_chains_and_history_only_counterfeit(self):
        graph = self.graph
        with ctx.workprec(768):
            for depth in (1, 2):
                fixture = audit.manufactured(graph, depth)
                self.evidence["manufactured"][str(depth)] = fixture
                report = audit.manufactured_check(graph, fixture)
                self.assertFalse(report["infinite_section_claimed"])
                bad = deepcopy(fixture)
                X = decoded(bad["rows"][0]["X"])
                X[X.nrows() - 1, 0] += arb(Q(1, 2**24))
                bad["rows"][0]["X"] = encoded(X)
                bad = audit.sealed(bad)
                rc, ry, rh, _ = audit.chain_residuals(graph, bad["rows"])
                self.assertLess(rc, arb(2) ** -650)
                self.assertLess(rh, arb(2) ** -650)
                self.assertGreater(ry, arb(2) ** -25)
                self.reject(
                    f"manufactured_depth{depth}_history_only_rehashed",
                    lambda bad=bad: audit.manufactured_check(graph, bad),
                    "history residual",
                )
                # Native proposals see exact dyadic centres; fixture widths and
                # centre conversion enter the finite comparison explicitly.
                X0 = decoded(fixture["rows"][0]["X"])
                H0 = decoded(fixture["rows"][0]["H"])
                with ctx.workprec(256):
                    native = self.k.section_math()
                    point = arb_mat([[x.mid()] for x in X0.entries()])
                    oldtail = native.bounds["section_tail"]
                    native.bounds["section_tail"] = (
                        native.bounds["graph_transform_contraction"] ** depth
                        * native.bounds["section_value_radius"]
                    )
                    try:
                        with patch.object(maths, "DEPTH", depth):
                            result = native.section(point, retain_chain=True)
                    finally:
                        native.bounds["section_tail"] = oldtail
                    error = result["residual_error"] + arb(Q(1, 256)) * norm(X0 - point)
                    self.assertLess(
                        norm(result["proposal"] - H0),
                        error
                        + norm(
                            arb_mat([[x.rad() for x in row] for row in H0.tolist()])
                        ),
                    )
                    self.assertEqual(len(result["chain"]), depth)
                    for row in fixture["rows"][1:]:
                        X, H = decoded(row["X"]), decoded(row["H"])
                        a = native.lag(X, H, retract=True)
                        b = audit.fixed(graph, X, H)
                        self.assertTrue(audit.overlaps(X + a["increment"], b["X"]))
                        self.assertTrue(audit.overlaps(a["geometry"], b["H"]))
        self.measurements["manufactured_exact_solution_claimed"] = False

    def test_every_inverse_history_coordinate_and_separate_tail(self):
        with ctx.workprec(768):
            w = self.steps["current"].section
            _, details = self.read(w)
            self.measurements["joint_inverse"] = details
            for level in range(16):
                for edge in range(16):
                    bad = w.to_dict()
                    bad["chain"][level]["X"][15 + edge] = str(
                        Q(bad["chain"][level]["X"][15 + edge]) + Q(1, 2**24)
                    )
                    self.reject(
                        f"inverse_history_{level}_{edge}",
                        lambda bad=bad: self.read(FrozenJSONMap(bad)),
                        "C/Y inverse residual",
                    )
            changes = {
                "freeze_all_inverse_history": lambda d: [
                    r["X"].__setitem__(slice(15, None), d["query_proposal"][15:])
                    for r in d["chain"]
                ],
                "deepest_resource": lambda d: d["chain"][-1]["X"].__setitem__(0, "2"),
                "zero_tail": lambda d: d.update(section_tail=["0", "0"]),
                "zero_residual": lambda d: d.update(residual_error=["0", "0"]),
                "zero_joint_maximum": lambda d: d.update(state_residual=["0", "0"]),
                "zero_log_query_displacement": lambda d: d.update(
                    query_shift=["0", "0"]
                ),
                "missing_level": lambda d: d["chain"].pop(),
                "wrong_depth_tail": lambda d: d["completion"].update(section_tail="0"),
                "wrong_output_H": lambda d: d.update(
                    proposal=encoded(self.k.section_math().I)
                ),
                "terminal_nonidentity": lambda d: d["chain"][-1]["H"].__setitem__(
                    0, "1025/1024"
                ),
                "scaled512": lambda d: d["completion"].update(logW_scale="512"),
                "writer_not_in_inverse": lambda d: d.update(writer_in_inverse=False),
            }
            for label, change in changes.items():
                bad = w.to_dict()
                change(bad)
                self.reject(label, lambda bad=bad: self.read(FrozenJSONMap(bad)))

    def test_fixed_H_map_duration_decay_and_writer_stage_discriminators(self):
        with ctx.workprec(768):
            X = audit.state_X(self.target.current)
            H = decoded(self.steps["current"].section["geometry"])
            true = audit.fixed(self.graph, X, H, retract=False)
            native = self.k.section_math().lag(X, H)
            self.assertTrue(audit.overlaps(X + native["increment"], true["X"]))
            for label, kw in (
                ("duration32_base", {"duration": 32}),
                ("inherited_exp_minus_one", {"decay": (-arb(1)).exp()}),
                ("inverse_frozen_history", {"freeze_history": True}),
                ("baseline_in_post_writer", {"writer_baseline": True}),
                ("omit_H_potential", {"potential_H": False}),
                ("omit_H_lowering", {"lowering_H": False}),
            ):
                wrong = audit.fixed(self.graph, X, H, retract=False, **kw)
                self.assertFalse(
                    audit.overlaps(wrong["H"], true["H"])
                    and audit.overlaps(wrong["X"], true["X"]),
                    label,
                )
                self.measurements["mutations"].append(
                    {
                        "label": label,
                        "detected_by": "resolved independent fixed-H map/geometry difference",
                    }
                )
            self.assertFalse(
                audit.overlaps(true["read_exponent"], true["writer_exponent"])
            )
            for step in self.steps.values():
                self.assertTrue(
                    verify_step(self.target, step.before, step)["full_C_logW_error"]
                )
        for d in ("8", "32"):
            self.reject(
                "ordinary_duration_" + d,
                lambda d=d: self.k.step(self.target.current, d),
            )
        self.reject(
            "tau16_changes_section",
            lambda: SparkARG2bKernel(
                self.k.graph, profile(self.k.graph, candidate={"tau_A": 16})
            ),
        )

    def test_scaled_history_clipping_and_exterior_base_identity(self):
        with ctx.workprec(768):
            m = self.k.section_math()
            X = audit.state_X(self.target.current)
            X[30, 0] = arb(1)
            Y = arb_mat(X)
            Y[30, 0] += 3
            a, b = audit.fixed(self.graph, X, m.I), audit.fixed(self.graph, Y, m.I)
            self.assertTrue(audit.overlaps(a["increment"], b["increment"]))
            self.assertTrue(audit.overlaps(a["H"], b["H"]))
            self.assertTrue(audit.overlaps(b["X"] - a["X"], Y - X))
            for x in (X, Y):
                got = m.lag(x, m.I, retract=True)
                self.assertTrue(
                    audit.overlaps(
                        x + got["increment"], audit.fixed(self.graph, x, m.I)["X"]
                    )
                )
            wrong = (-arb(Q(1, 2))).exp() * arb(3)
            self.assertFalse((b["X"] - a["X"])[30, 0].overlaps(wrong))
            huge = arb_mat(X)
            huge[30, 0] = arb(2) ** 100000
            got = m.lag(huge, m.I, retract=True)
            self.assertTrue(all(x.is_finite() for x in got["increment"].entries()))
            self.assertTrue(audit.overlaps(got["increment"], a["increment"]))
            self.assertTrue(audit.overlaps(m.clip(X), audit.clip(self.graph, X)))
            weights = list(self.target.current.W_A)
            weights[-1] = "513/512"
            state = replace(self.target.current, W_A=tuple(weights))
            self.reject(
                "positive_W_outside_scaled_chart", lambda: self.k.readmission(state)
            )
            self.assertGreater(64 * arb(Q(513, 512)).log(), arb(Q(1, 16)))
        self.measurements["unbounded_auxiliary_exponentiation_avoided"] = True

    def test_final_C_writer_is_not_retracted_again(self):
        with ctx.workprec(768):
            m = self.k.section_math()
            X = audit.state_X(self.target.current)
            found = None
            for i in range(m.n):
                for face in m.chart[i]:
                    probe = arb_mat(X)
                    probe[i, 0] = arb(face)
                    good = audit.fixed(self.graph, probe, m.I)
                    wrong = audit.fixed(self.graph, probe, m.I, post_clip=True)
                    if not audit.overlaps(good["writer_C"], wrong["writer_C"]):
                        found = (probe, good, wrong)
                        break
                if found:
                    break
            self.assertIsNotNone(found, "need a final-C chart-crossing discriminator")
            probe, good, wrong = found
            self.assertFalse(audit.overlaps(good["X"], wrong["X"]))
            observed = []
            original = m.exponent

            def capture(C, W, J, *args, **kwargs):
                observed.append((arb_mat(C), arb_mat(W), arb_mat(J)))
                return original(C, W, J, *args, **kwargs)

            with patch.object(m, "exponent", capture):
                actual = m.lag(probe, m.I, retract=True)
            self.assertTrue(audit.overlaps(observed[-1][0], good["writer_C"]))
            self.assertTrue(audit.overlaps(observed[-1][1], good["writer_W"]))
            self.assertTrue(audit.overlaps(probe + actual["increment"], good["X"]))
            self.evidence["post_continuity_chart_probe"] = encoded(probe)

    def test_vertex_chart_transport_and_wrong_source_chart(self):
        with ctx.workprec(768):
            graph = deepcopy(self.graph)
            graph["live_node_ids"] = list(reversed(graph["live_node_ids"]))
            X = audit.state_X(self.target.current)
            n = 15
            permuted = arb_mat(list(reversed(X.tolist()[:n])) + X.tolist()[n:])
            H = decoded(self.steps["current"].section["geometry"])
            a = audit.fixed(self.graph, X, H)
            b = audit.fixed(graph, permuted, H)
            self.assertTrue(
                audit.overlaps(
                    a["X"],
                    arb_mat(list(reversed(b["X"].tolist()[:n])) + b["X"].tolist()[n:]),
                )
            )
            self.assertTrue(audit.overlaps(a["H"], b["H"]))
            m = self.k.section_math()
            chart = audit.model(self.graph).domain["resource_agreement"]
            self.assertEqual(m.chart, [tuple(map(Q, chart[v])) for v in m.nodes])
            bad = self.steps["current"].section.to_dict()
            bad["completion"]["resource_agreement"] = audit.model(
                self.config.reference.graph.to_payload()
            ).domain["resource_agreement"]
            self.reject("source_chart_at_target", lambda: self.read(FrozenJSONMap(bad)))
            bad = self.steps["current"].section.to_dict()
            keys = list(bad["completion"]["resource_agreement"])
            a, b = keys[0], keys[-1]
            (
                bad["completion"]["resource_agreement"][a],
                bad["completion"]["resource_agreement"][b],
            ) = (
                bad["completion"]["resource_agreement"][b],
                bad["completion"]["resource_agreement"][a],
            )
            self.reject(
                "positional_chart_after_reordering",
                lambda: self.read(FrozenJSONMap(bad)),
            )

    def test_unrounded_time_shift_and_two_W_routes(self):
        with ctx.workprec(768):
            value = audit.time_shift(
                self.graph,
                self.target.reference.profile.to_payload(),
                self.target.current,
                self.steps["current"].section,
            )
            self.evidence["time_shift"] = value
            newH, oldH = (
                decoded(value["fresh_next_H"]),
                decoded(value["stale_history_H"]),
            )
            X = decoded(value["unrounded_X"])
            oldX = arb_mat(
                X.tolist()[:15] + audit.state_X(self.target.current).tolist()[15:]
            )
            controls = {
                (w, h): audit.fixed(self.graph, x, H, retract=False)["J"]
                for w, x in (("newW", X), ("oldW", oldX))
                for h, H in (("newH", newH), ("oldH", oldH))
            }
            self.assertFalse(
                audit.overlaps(controls["newW", "newH"], controls["oldW", "newH"])
            )
            self.assertFalse(
                audit.overlaps(controls["newW", "newH"], controls["newW", "oldH"])
            )
            self.measurements["W_direct_current_difference_upper"] = str(
                norm(controls["newW", "newH"] - controls["oldW", "newH"]).upper().fmpq()
            )
            self.measurements["W_section_current_difference_upper"] = str(
                norm(controls["newW", "newH"] - controls["newW", "oldH"]).upper().fmpq()
            )
            self.assertEqual(value["duration"], "16")

    def test_cache_full_history_displacement_state_only_and_detached_values(self):
        state = self.steps["current"].after
        base = self.k.readmission(state)
        for i in range(3):
            W = list(state.W_A)
            W[-1] = str(Q(W[-1]) * (1 + Q(i + 1, 2**70)))
            changed = replace(state, W_A=tuple(W))
            _section_witness.cache_clear()
            cold = self.k.readmission(changed)
            self.assertEqual(cold, self.k.readmission(changed))
            rebuilt = ExactConductanceState.from_canonical_bytes(
                changed.to_canonical_bytes()
            )
            _section_witness.cache_clear()
            self.assertEqual(cold, self.k.readmission(rebuilt))
            self.assertEqual(changed.C, state.C)
            self.assertNotEqual(cold["state"], base["state"])
            exported = cold.to_dict()
            exported["geometry"][0][0] = ["9", "9"]
            self.assertEqual(cold, self.k.readmission(changed))
            with ctx.workprec(768):
                self.reject(
                    f"C_only_cache_history_perturbation_{i}",
                    lambda changed=changed: self.read(base, changed),
                    "external full C/W binding",
                )
                self.read(cold, changed)
        self.measurements["history_only_cold_warm_state_only_cases"] = 3
        self.measurements["forward_geometry_reuse_used"] = False
        self.assertEqual(self.k.cache_info()["section"]["maxsize"], 8)

    def test_full_physical_error_independent_writer_and_charge(self):
        with ctx.workprec(768):
            results = {}
            for role, step in self.steps.items():
                proof, _ = self.read(step.section, step.before)
                c, y, exact = audit.step_error(
                    self.graph, step.before, step, decoded(proof["H"])
                )
                bound = arb(Q(self.certificates[0].proof["full_step_error"]))
                self.assertLess(max(c, y), bound)
                self.assertEqual(sum(map(Q, step.after.C)), 21)
                self.assertNotEqual(
                    sum(map(Q, step.after.W_A)), sum(map(Q, step.before.W_A))
                )
                writer = step.writer
                from hashlib import sha256

                from pygrc.models.grc_v4_spark_state import ExactResources

                self.assertEqual(
                    writer["consumed_state_digest"],
                    sha256(step.before.to_canonical_bytes()).hexdigest(),
                )
                resources = ExactResources.advance(step.before, step.flux, "16")
                self.assertEqual(
                    writer["final_resource_digest"],
                    sha256(resources.to_canonical_bytes()).hexdigest(),
                )
                self.assertTrue(
                    decoded([[writer["decay"]]])[0, 0].contains((-arb(Q(1, 2))).exp())
                )
                represented = audit.state_X(step.after)
                delta = represented - exact["X"]
                logs = arb_mat(delta.tolist()[15:])
                maximum = max(abs(x).upper() for x in logs.entries())
                self.assertGreater(y, maximum)
                results[role] = {
                    "C_metric_error_upper": str(c.upper().fmpq()),
                    "scaled_logW_l2_error_upper": str(y.upper().fmpq()),
                }
                self.reject(
                    role + "_zero_log_error",
                    lambda step=step: verify_step(
                        self.target,
                        step.before,
                        replace(step, log_conductance_component_error="0"),
                    ),
                )
            self.measurements["full_step_error"] = results
            P = audit.algebra(self.graph)[3]
            from crg2b_native_spark_pressure_oracle import algebra as C_algebra

            self.assertNotEqual(P, C_algebra(self.graph)[4])
            self.assertFalse(self.certificates[0].proof["section_C1_claimed"])

    def test_scaled_logW_derivatives_and_unfrozen_weighted_rows(self):
        with ctx.workprec(768):
            X = audit.state_X(self.target.current)
            H = decoded(self.steps["current"].section["geometry"])
            # Fixed point H prevents section differentiation from entering this check.
            H = arb_mat([[v.mid() for v in row] for row in H.tolist()])
            native = self.k.section_math()
            J = native.fixed_jacobian(X, H)
            delta = arb(2) ** -100
            for edge in range(16):
                a, b = arb_mat(X), arb_mat(X)
                a[15 + edge, 0] += delta
                b[15 + edge, 0] -= delta
                f, g = (
                    audit.fixed(self.graph, a, H, retract=False),
                    audit.fixed(self.graph, b, H, retract=False),
                )
                fd = (f["X"] - g["X"]) / (2 * delta)
                self.assertLess(
                    norm(fd - arb_mat([[J[i, 15 + edge]] for i in range(31)])),
                    arb(2) ** -170,
                )
                dw = (f["W"][edge, 0] - g["W"][edge, 0]) / (2 * delta)
                self.assertLess(
                    abs(dw - (X[15 + edge, 0] / 64).exp() / 64), arb(2) ** -170
                )
                self.assertFalse(dw.overlaps((X[15 + edge, 0] / 64).exp()))
            self.measurements["independent_history_derivative_columns"] = 16

    def test_shared_parameter_membership_not_separate_projections(self):
        with ctx.workprec(768):
            c = self.certificates[0]
            Qcurve = M(c.operands["curve"])
            for s in (Q(0), Q(1, 7), Q(1)):
                X = arb_mat(curve.curve_at(Qcurve, s))
                state = self.curve_state(X)
                detail = curve.membership_details(c, state)
                self.assertTrue(detail["inside"])
                audit.joint_membership(
                    self.graph, Qcurve, audit.state_X(state), detail["parameter"]
                )
            # Private membership-logic fixture, never a public spark certificate.
            # p_C(s)=base+s(e0-e1), p_Y(s)=s e0. Separate projections fit at 0 and 1.
            Qsmall = M(31, 2)
            for i, x in enumerate(self.center.C):
                Qsmall[i, 0] = Q(x)
            for i, sign in ((0, 1), (1, -1)):
                Qsmall[i, 0] += Q(sign, 2)
                Qsmall[i, 1] = Q(sign, 2)
            Qsmall[15, 0] = Qsmall[15, 1] = Q(1, 2)
            X = arb_mat(
                [[Q(x)] for x in self.center.C] + [[int(i == 0)] for i in range(16)]
            )
            a0, b0 = audit.joint_distances(self.graph, Qsmall, X, 0)
            a1, b1 = audit.joint_distances(self.graph, Qsmall, X, 1)
            self.assertTrue(a0.contains(0))
            self.assertTrue(b1.contains(0))
            self.assertGreater(b0, arb(Q(1, 2)))
            self.assertGreater(a1, arb(Q(1, 100)))
            fake = type("MembershipLogicFixture", (), {})()
            fake.operands = FrozenJSONMap(
                {
                    "binding": c.operands["binding"],
                    "curve": [[str(v) for v in row] for row in Qsmall.tolist()],
                    "radius": "1/1000",
                }
            )
            fake.proof = FrozenJSONMap({"precision_bits": 256})
            self.assertFalse(
                curve.membership_details(fake, self.curve_state(X))["inside"]
            )
            self.measurements[
                "shared_parameter_synthetic_separate_projections_rejected"
            ] = True

    def curve_state(self, X):
        # Restore exact charge after converting a nondyadic curve evaluation.
        C = [x.mid().fmpq() for x in X.entries()[:15]]
        C[-1] = Q(21) - sum(C[:-1])
        return ExactConductanceState(
            self.center.graph,
            tuple(map(str, C)),
            "21",
            tuple(str((x / 64).exp().mid().fmpq()) for x in X.entries()[15:]),
        )

    def test_all_thirty_tube_directions_and_history_scale(self):
        with ctx.workprec(768):
            Qc = M(self.certificates[0].operands["curve"])
            P = audit.algebra(self.graph)[3]
            R = Q(1, 4096)
            count = 0
            for s in (Q(0), Q(1, 7), Q(1)):
                origin = arb_mat(curve.curve_at(Qc, s))
                for direction in range(30):
                    d = M(31, 1)
                    if direction < 14:
                        d[direction, 0] = 1
                        d[14, 0] = -1
                        dc = M(d.tolist()[:15])
                        scale = arb(R) / arb((dc.transpose() * P * dc)[0, 0]).sqrt()
                    else:
                        d[15 + direction - 14, 0] = 1
                        scale = arb(R)
                    for factor, inside in (
                        (Q(999, 1000), True),
                        (Q(1001, 1000), False),
                    ):
                        X = origin + arb_mat(d) * scale.mid() * arb(factor)
                        if inside:
                            audit.joint_membership(self.graph, Qc, X, s)
                        else:
                            self.reject(
                                f"outside_shared_witness_{s}_{direction}",
                                lambda X=X, s=s: audit.joint_membership(
                                    self.graph, Qc, X, s
                                ),
                                "product norm",
                            )
                        count += 1
            self.measurements["tube_boundary_witness_checks"] = count
            X = arb_mat(curve.curve_at(Qc, Q(1, 2)))
            X[30, 0] += arb(2 * R)
            _c, y = audit.joint_distances(self.graph, Qc, X, Q(1, 2))
            self.assertLess(y / 64**2, arb(R**2))
            self.assertGreater(y, arb(R**2))
            self.reject(
                "unscaled_logW_would_accept",
                lambda: audit.joint_membership(self.graph, Qc, X, Q(1, 2)),
            )
            for s in ("-1/1000", "1001/1000"):
                self.reject(
                    "out_of_range_s_" + s,
                    lambda s=s: audit.joint_membership(self.graph, Qc, X, s),
                )

    def test_Taylor_factorials_cell_scaling_and_full_writer_series(self):
        with ctx.workprec(768):
            width = Q(1, 8)
            cell = [[Q(0), Q(0), Q(0), Q(0), Q(1)]]
            jets = curve.curve_jets(cell, width, at_midpoint=True)[0]
            whole = curve.curve_jets(cell, width, at_midpoint=False)[0]
            for k in range(5):
                expected = Q(comb(4, k)) * Q(1, 2) ** (4 - k) / width**k
                self.assertTrue(jets[k].contains(expected))
                for u in (Q(0), Q(1, 3), Q(1)):
                    self.assertTrue(
                        whole[k].contains(Q(comb(4, k)) * u ** (4 - k) / width**k)
                    )
            self.assertFalse(jets[4].contains(1))
            self.assertFalse(jets[4].contains(24 / width**4))
            m = self.k.section_math()
            Qcurve = M(self.certificates[0].operands["curve"])
            for s in (Q(0), Q(1, 7), Q(1)):
                X = arb_mat(curve.curve_at(Qcurve, s))
                series = [arb_series([x], prec=5) for x in X.entries()]
                native = curve.reference_jets(m, series)
                expected = audit.fixed(self.graph, X, m.I, retract=False)["X"]
                self.assertTrue(
                    audit.overlaps(arb_mat([[v[0]] for v in native]), expected)
                )
                shift = curve.composition(Qcurve, Q(999, 1000))
                self.assertEqual(
                    curve.curve_at(shift, s), curve.curve_at(Qcurve, Q(999, 1000) * s)
                )
            # Nonconstant history series must differentiate weighted rows and
            # the final-C writer, not just the explicit exponential mobility.
            X = arb_mat(curve.curve_at(Qcurve, Q(1, 7)))
            delta = arb(2) ** -100
            for edge in (0, 15):
                series = [
                    arb_series([x, int(i == 15 + edge)], prec=5)
                    for i, x in enumerate(X.entries())
                ]
                jets = curve.reference_jets(m, series)
                plus, minus = arb_mat(X), arb_mat(X)
                plus[15 + edge, 0] += delta
                minus[15 + edge, 0] -= delta
                difference = (
                    audit.fixed(self.graph, plus, m.I, retract=False)["X"]
                    - audit.fixed(self.graph, minus, m.I, retract=False)["X"]
                ) / (2 * delta)
                self.assertLess(
                    norm(arb_mat([[v[1]] for v in jets]) - difference), arb(2) ** -170
                )
            self.measurements["continuous_residual_cells"] = len(
                self.certificates[0].proof["residual_partition"]["cells"]
            )

    def test_continuous_certificate_rehashed_corruptions_and_common_hull(self):
        original = self.certificates[0].to_payload()
        changes = {
            "missing_narrow_cell": lambda d: d["proof"]["residual_partition"][
                "cells"
            ].pop(33),
            "coverage_gap_same_count": lambda d: d["proof"]["residual_partition"][
                "cells"
            ][10]["interval"].__setitem__(1, "0"),
            "omit_history_dimension": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(conductance_dimension=0),
            "sampled_remainder": lambda d: d["proof"]["residual_partition"].update(
                continuous_parameter=False
            ),
            "omit_section_correction": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(section_difference_correction=["0", "0"]),
            "omit_geometry_value": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(geometry_value_correction=["0", "0"]),
            "per_ball_not_pairwise": lambda d: d["proof"][
                "physical_difference_bound"
            ].update(all_independent_coordinates=False),
            "wrong_coordinate_W": lambda d: d["proof"].update(
                coordinate_system="C_then_W"
            ),
            "claim_section_C1": lambda d: d["proof"].update(section_C1_claimed=True),
            "future_tail": lambda d: d["proof"].update(
                supporting_trajectory_steps_after_completion=1600
            ),
        }
        for label, change in changes.items():
            bad = deepcopy(original)
            change(bad)
            envelope = audit.sealed({"certificate": bad})
            self.assertEqual(envelope, audit.sealed(envelope))
            self.reject(label, lambda bad=bad: CompletionCertificate.from_payload(bad))
        with ctx.workprec(768):
            Qc = M(self.certificates[0].operands["curve"])
            states = [self.curve_state(arb_mat(curve.curve_at(Qc, s))) for s in (0, 1)]
            steps = [self.k.step(s) for s in states]

            def distance(a, b):
                d = audit.state_X(a) - audit.state_X(b)
                C = arb_mat(d.tolist()[:15])
                Y = d.entries()[15:]
                return max(
                    (C.transpose() * arb_mat(audit.algebra(self.graph)[3]) * C)[0, 0]
                    .nonnegative_part()
                    .sqrt(),
                    sum(x * x for x in Y).nonnegative_part().sqrt(),
                )

            self.assertLess(
                distance(steps[0].after, steps[1].after),
                arb(Q(self.certificates[0].proof["q"])) * distance(*states)
                + 2 * arb(Q(self.certificates[0].proof["full_step_error"])),
            )

    def test_actual_event_lineage_and_committed_W_classifier(self):
        from pygrc.models.grc_9_v4_completion import classify
        from pygrc.models.grc_9_v4_spark_conductance_event import target

        event = self.event_model._operation._published.completion.event
        self.assertEqual(self.source_model.configuration.reset, self.config.reset)
        self.assertEqual(self.source_model.configuration.time, "16")
        self.assertNotEqual(
            self.source_model.configuration.current.W_A, self.config.current.W_A
        )
        T = M(event["transfer"])
        for role in ("current", "reset"):
            source = getattr(self.source_model.configuration, role)
            actual = getattr(self.target, role)
            expected = target(source, actual.graph, event["transfer"])
            self.assertEqual(actual, expected)
            self.assertEqual(
                T * M([[Q(x)] for x in source.C]), M([[Q(x)] for x in actual.C])
            )
            old = dict(zip(source.graph.live_edge_ids, source.W_A, strict=True))
            new = dict(zip(actual.graph.live_edge_ids, actual.W_A, strict=True))
            self.assertTrue(all(new[e] == w for e, w in old.items()))
            self.assertEqual([new[e] for e in new if e not in old], ["1"] * 3)
            self.assertEqual(self.k.readmission(actual)["physical_state"], ("C", "W_A"))
            self.assertNotIn("Z_4", actual.to_payload())
            if role == "current":
                before_writer = target(
                    self.config.current, actual.graph, event["transfer"]
                )
                self.assertNotEqual(actual.W_A, before_writer.W_A)
                with ctx.workprec(768):
                    self.reject(
                        "prewriter_W_at_target",
                        lambda before_writer=before_writer, actual=actual: self.read(
                            self.k.readmission(before_writer), actual
                        ),
                        "external full C/W binding",
                    )
                W = list(actual.W_A)
                indices = [
                    i for i, e in enumerate(actual.graph.live_edge_ids) if e in old
                ]
                a = indices[0]
                b = next(i for i in indices if W[i] != W[a])
                W[a], W[b] = W[b], W[a]
                permuted = replace(actual, W_A=tuple(W))
                self.assertNotEqual(permuted, expected)
                with ctx.workprec(768):
                    self.reject(
                        "old_edge_W_permutation",
                        lambda permuted=permuted, actual=actual: self.read(
                            self.k.readmission(permuted), actual
                        ),
                        "external full C/W binding",
                    )
            reported = classify(actual, self.target.policy)
            self.assertEqual(
                tuple(reported.rows),
                actual.spatial_diagnostics(
                    sign=self.target.policy.landscape_sign,
                    gradient=self.target.policy.epsilon_gradient,
                    hessian=self.target.policy.epsilon_Hessian,
                    contrast=self.target.policy.contrast,
                    core_resource=self.target.policy.minimum_resource,
                ),
            )
            with ctx.workprec(768):
                exact = audit.fixed(
                    self.graph, audit.state_X(actual), self.k.section_math().I
                )
                for row, expected_row in zip(reported.rows, exact["rows"], strict=True):
                    self.assertTrue(
                        all(
                            x.contains(Q(y))
                            for x, y in zip(expected_row, row["gradient"], strict=True)
                        )
                    )
            controlled = replace(
                actual, W_A=tuple(str(1 + Q(i + 1, 2**14)) for i in range(16))
            )
            uniform = replace(actual, W_A=("1",) * 16)
            self.assertNotEqual(
                classify(controlled, self.target.policy).rows,
                classify(uniform, self.target.policy).rows,
            )
        with ctx.workprec(768):
            unit = replace(self.target.current, W_A=("1",) * 16)
            bad = self.k.readmission(unit).to_dict()
            bad["state"] = self.target.current.to_payload()
            self.reject(
                "unit_W_section_relabelled_as_transported_W",
                lambda: self.read(FrozenJSONMap(bad)),
            )
            source = self.source_model.configuration
            oldH = decoded(owner.kernel(source).readmission(source.current)["geometry"])
            H = self.k.section_math().I
            positions = [
                self.target.current.graph.live_edge_ids.index(e)
                for e in source.current.graph.live_edge_ids
            ]
            for i, ii in enumerate(positions):
                for j, jj in enumerate(positions):
                    H[ii, jj] = oldH[i, j].mid()
            bad = self.steps["current"].section.to_dict()
            bad["proposal"] = encoded(H)
            self.reject(
                "transported_source_H_as_target_authority",
                lambda: self.read(FrozenJSONMap(bad)),
            )
        self.measurements["actual_event_old_W_lineage_and_seed"] = True

    def test_deep_history_auxiliary_writer_and_postwriter_failures_atomic(self):
        for fault in (
            "deep_history_residual",
            "inverse_final_C_writer",
            "postwriter_returned_section",
        ):
            m = self.event_model.duplicate()
            before = m.snapshot()
            ledger = m.receipt_ledger
            _section_witness.cache_clear()
            calls = []
            if fault == "deep_history_residual":
                original = maths.ARG2bMath.lag

                def fail(obj, *args, calls=calls, original=original, **kwargs):
                    result = original(obj, *args, **kwargs)
                    if ctx.prec == 256 and obj.proposal_sweeps:
                        calls.append(1)
                        if len(calls) == 16:
                            increment = arb_mat(result["increment"])
                            increment[obj.d - 1, 0] += arb(Q(1, 10000))
                            result = dict(result, increment=increment)
                    return result

                context = patch.object(maths.ARG2bMath, "lag", fail)
            elif fault == "inverse_final_C_writer":
                original = maths.ARG2bMath.exponent

                def fail(obj, *args, calls=calls, original=original, **kwargs):
                    if ctx.prec == 224:
                        calls.append(1)
                        if len(calls) == 2:
                            raise CertificationInconclusive(
                                "injected auxiliary final-C writer"
                            )
                    return original(obj, *args, **kwargs)

                context = patch.object(maths.ARG2bMath, "exponent", fail)
            else:
                original = SparkARG2bKernel._admitted_section

                def fail(obj, state, calls=calls, original=original):
                    calls.append(1)
                    result = original(obj, state)
                    if len(calls) == 2:
                        raise CertificationInconclusive(
                            "injected prospective C+/W+ section"
                        )
                    return result

                context = patch.object(SparkARG2bKernel, "_admitted_section", fail)
            with context:
                result = m.step()
                self.assertFalse(result.committed, fault)
            self.assertTrue(calls)
            self.assertEqual(m.snapshot(), before)
            self.assertEqual(m.receipt_ledger, ledger)
            self.assertTrue(m.step().committed)
            self.assertEqual(m.configuration.current, self.steps["current"].after)
            self.measurements["mutations"].append(
                {"label": fault, "detected_by": str(result.reason)}
            )

    def test_reset_only_event_failure_equal_C_different_W_and_observation_purity(self):
        sameC = replace(self.target.current, W_A=self.target.reset.W_A)
        self.assertEqual(sameC.C, self.target.current.C)
        self.assertNotEqual(sameC.W_A, self.target.current.W_A)
        other = self.k.readmission(sameC)
        with ctx.workprec(768):
            self.reject(
                "equal_C_different_role_W",
                lambda: self.read(other),
                "external full C/W binding",
            )
        m = self.source_model.duplicate()
        before = m.snapshot()
        ledger = m.receipt_ledger
        original = SparkARG2bKernel.readmission
        seen = []

        def fail(k, state):
            if len(state.C) == 15:
                seen.append(state)
                if len(seen) == 2:
                    raise CertificationInconclusive(
                        "target reset C/W admission after transfer"
                    )
            return original(k, state)

        with patch.object(SparkARG2bKernel, "readmission", fail):
            self.assertFalse(m.expand(request(m)).committed)
        self.assertEqual(len(seen), 2)
        self.assertEqual(m.snapshot(), before)
        self.assertEqual(m.receipt_ledger, ledger)
        self.assertTrue(m.expand(request(m)).committed)
        before = m.snapshot()
        with patch.object(
            SparkARG2bKernel, "step", side_effect=AssertionError("observation aged W")
        ):
            for _ in range(3):
                m.compute_observables()
                m.snapshot()
        self.assertEqual(m.snapshot(), before)
        a, b = m.duplicate(), m.duplicate()
        _section_witness.cache_clear()
        self.assertTrue(a.step().committed)
        b.compute_observables()
        self.assertTrue(b.step().committed)
        self.assertEqual(a.configuration.current, b.configuration.current)
        self.assertEqual(a.configuration.reset, b.configuration.reset)

    test_bounded_completion_window_no_source_endpoint_claim = baseline.NativeARG2bTests.test_duration16_two_beat_window_and_joint_public_evidence


if __name__ == "__main__":
    unittest.main()
