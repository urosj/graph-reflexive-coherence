"""Bounded A_PC two-history pressure; no source-to-completion trajectory."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from apc_native_spark_audit import (
    audit_event,
    audit_step,
    audit_trace,
    digest,
    separation,
)
from apc_native_spark_pressure_oracle import Reference, contains, frobenius, verify_step
from cos_native_spark_oracle import incidence, matrix, vector
from cpc_native_spark_pressure_oracle import decode, intervals
from p991a6_apc_preflight import decoded, transition
from p991a6_apc_subjects import profile, request

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_apc as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from pygrc.models.grc_v4_spark_apc_math import APCMath
from pygrc.models.grc_v4_spark_carrier import carrier_pairs
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_apc as fixtures


def sentinel(state, sign=1, resources=False):
    n, m = len(state.C), len(state.W_A)
    z = [["0"] * m for _ in range(m)]
    for k, (i, j) in enumerate(carrier_pairs(state.graph)):
        z[i][j] = z[j][i] = str(sign * (-1) ** k * Q(k + 1, 2**24))
    changes = {
        "W_A": tuple(str(1 + sign * Q((i * 5) % 13 - 6, 2048)) for i in range(m)),
        "Z_4": tuple(map(tuple, z)),
    }
    if resources:
        delta = [Q((i * 7) % 11, 32) for i in range(n)]
        mean = sum(delta) / n
        changes["C"] = tuple(str(Q(state.charge) / n + x - mean) for x in delta)
    return replace(state, **changes)


def operands(state):
    return (
        arb_mat(vector(state.C)),
        arb_mat(vector(state.W_A)),
        arb_mat(matrix(state.Z_4)),
    )


def exact_potential(state):
    B = incidence(state.graph.to_payload())
    C, W, Z = vector(state.C), vector(state.W_A), matrix(state.Z_4)
    D = M(
        [[W[i, 0] if i == j else 0 for j in range(W.nrows())] for i in range(W.nrows())]
    )
    site = M([[(c - 2) ** 3 - (c - 2)] for c in map(Q, state.C)])
    return B * (D + Z / 2) * B.transpose() * C / 64 - site


def observed(model):
    initial, publication = model.configuration, model._operation._spark_scope.published
    records, steps = [], []
    kernel = native.SparkAPCKernel
    read, ww, zw, write, step = (
        kernel._admitted_read,
        kernel._conductance_writer,
        kernel._carrier_writer,
        ExactAdaptiveCarrierState.advance_histories,
        kernel.step,
    )

    def frozen():
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not publication
        ):
            raise AssertionError("provisional three-coordinate publication")

    def capture_read(k, state):
        frozen()
        result = read(k, state)
        records.append(
            {
                "stage": "incoming" if not records else "returned",
                "state": state.to_payload(),
                "read": k.read_payload(result).to_dict(),
            }
        )
        return result

    def capture_w(k, state, after, consumed):
        frozen()
        held = intervals(consumed["S"])
        result = ww(k, state, after, consumed)
        records.append(
            {
                "stage": "W_writer",
                "state": state.to_payload(),
                "final_C": list(after.C),
                "held_source_before": held,
                "held_source_after": intervals(consumed["S"]),
                "writer": result[1].to_dict(),
            }
        )
        return result

    def capture_z(k, state, consumed):
        frozen()
        result = zw(k, state, consumed)
        records.append(
            {
                "stage": "Z_writer",
                "state": state.to_payload(),
                "source": intervals(consumed["S"]),
                "writer": result[1].to_dict(),
            }
        )
        return result

    def capture_write(state, *args):
        frozen()
        result = write(state, *args)
        records.append(
            {
                "stage": "write",
                "state": state.to_payload(),
                "after": result.to_payload(),
            }
        )
        return result

    def capture_step(k, *args, **kw):
        result = step(k, *args, **kw)
        steps.append(result)
        return result

    with (
        patch.object(kernel, "_admitted_read", capture_read),
        patch.object(kernel, "_conductance_writer", capture_w),
        patch.object(kernel, "_carrier_writer", capture_z),
        patch.object(ExactAdaptiveCarrierState, "advance_histories", capture_write),
        patch.object(kernel, "step", capture_step),
    ):
        result = model.step()
    if not result.committed or len(steps) != 1:
        raise AssertionError(result.reason)
    return steps[0], records


class APCNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeAPCTests.setUpClass()
        cls.fixture = fixtures.NativeAPCTests()
        cls.config = cls.fixture.config
        cls.event = cls.fixture.event_model
        cls.certs = cls.fixture.certificates
        cls.state = sentinel(cls.event.configuration.current, resources=True)
        cls.kernel = owner.kernel(cls.event.configuration)
        cls.good = cls.kernel.step(cls.state)
        cls.measurements = {"mutations": []}
        cls.evidence = {"actual_steps": [], "events": [], "probes": {}}

    def setUp(self):
        self.enterContext(exact_backend(ExactBackend.FLINT))
        self.enterContext(_ARB_CONTEXT_LOCK)
        self.enterContext(ctx.workprec(768))

    def reject(self, name, call):
        with (
            self.subTest(mutation=name),
            self.assertRaises((AssertionError, ValueError, RuntimeError)),
        ):
            call()
        self.measurements["mutations"].append(name)

    def changed(self, step, field, key, value):
        data = getattr(step, field).to_dict()
        data[key] = value
        changed = replace(step, **{field: FrozenJSONMap(data)})
        envelope = {"transition": transition(changed)}
        envelope["content_digest"] = digest(envelope)
        self.assertEqual(
            envelope["content_digest"], digest({"transition": envelope["transition"]})
        )
        return decoded(envelope["transition"])

    def test_frozen_public_two_writer_stages_and_complete_map(self):
        source = GRC9V4(self.config)
        step, trace = observed(source)
        self.evidence["source_step"] = {
            "subject": self.config.to_payload(),
            "step": transition(step),
            "role": "current",
            "audit": audit_step(self.config, self.config.current, step),
        }
        self.assertTrue(source.expand(request(source)).committed)
        self.assertTrue(source.install_completion_certificates(*self.certs).committed)
        reset = source.duplicate()
        self.assertTrue(reset.reset().committed)
        for role, model, cert in (
            ("current", source, self.certs[0]),
            ("reset", reset, self.certs[1]),
        ):
            for index in range(2):
                initial = model.configuration
                step, trace = observed(model)
                report = audit_step(initial, initial.current, step, cert, role)
                result = audit_trace(step, trace)
                row = {
                    "subject": initial.to_payload(),
                    "step": transition(step),
                    "role": role,
                    "certificate": cert.to_payload(),
                    "audit": report,
                }
                self.evidence["actual_steps"].append(row)
                if role == "current" and index == 0:
                    self.evidence["operand_trace"] = trace
                    self.evidence["operand_trace_audit"] = result
        self.measurements["two_writer_staging"] = {
            "actual_target_steps": 4,
            "fresh_reads": 2,
            "physical_writers": 2,
            "atomic_writes": 1,
            "frozen_source": True,
        }

    def test_detached_writer_order_and_conditional_independences(self):
        state = self.state
        k = self.kernel
        with ctx.workprec(256):
            read = k._admitted_read(state)
            C = ExactResources(
                self.good.after.graph, self.good.after.C, self.good.after.charge
            )
            before = intervals(read["S"])
            w1 = k._conductance_writer(state, C, read)
            z1 = k._carrier_writer(state, read)
            z2 = k._carrier_writer(state, read)
            w2 = k._conductance_writer(state, C, read)
            self.assertEqual(w1, w2)
            self.assertEqual(z1, z2)
            self.assertEqual(before, intervals(read["S"]))
            # Holding the consumed current fixed, an unrelated new Z is irrelevant to W.
            unrelated = dict(read)
            unrelated["_Z"] = arb_mat(len(state.W_A), len(state.W_A))
            unrelated["source"] = arb_mat(len(state.W_A), len(state.W_A))
            self.assertEqual(k._conductance_writer(state, C, unrelated), w1)
            # The carrier helper consumes old Z and held S, never new C/W arrays.
            unrelated = dict(read)
            unrelated["_C"] = arb_mat(len(state.C), 1)
            unrelated["_W"] = arb_mat(len(state.W_A), 1)
            self.assertEqual(k._carrier_writer(state, unrelated), z1)
        ref = Reference(state.graph.to_payload())
        c, w, z = operands(state)
        shifted = sentinel(state, -1, resources=True)
        cc, ww, zz = operands(shifted)
        self.assertEqual(ref.selected(c, w, z)["H"], ref.selected(cc, ww, z)["H"])
        a = APCMath(state.graph)
        rows = a.rows(c, w)[0]
        a.pc_read(c, arb_mat([[x.log()] for x in w.entries()]), zz, w)
        self.assertEqual(intervals(arb_mat(rows)), intervals(arb_mat(a.rows(c, w)[0])))
        self.measurements["writer_independence"] = {
            "detached_orders_equal": True,
            "held_S_unchanged": True,
            "new_Z_irrelevant_to_held_W": True,
            "new_C_W_irrelevant_to_held_Z": True,
        }

    def test_identical_potential_different_mobility_probe(self):
        state = self.state
        phi = exact_potential(state)
        B = incidence(state.graph.to_payload())
        gradient = B.transpose() * phi
        edge = next(i for i in range(gradient.nrows()) if gradient[i, 0] != 0)
        d = Q(1, 2**20)
        w = list(map(Q, state.W_A))
        z = matrix(state.Z_4)
        w[edge] += d
        z[edge, edge] -= 2 * d
        other = replace(
            state,
            W_A=tuple(map(str, w)),
            Z_4=tuple(
                tuple(str(z[i, j]) for j in range(z.ncols())) for i in range(z.nrows())
            ),
        )
        self.assertEqual(phi, exact_potential(other))
        self.assertEqual(
            matrix(state.Z_4) / 2
            + M(
                [
                    [Q(state.W_A[i]) if i == j else 0 for j in range(len(w))]
                    for i in range(len(w))
                ]
            ),
            z / 2
            + M(
                [[w[i] if i == j else 0 for j in range(len(w))] for i in range(len(w))]
            ),
        )
        ref = Reference(state.graph.to_payload())
        a = ref.selected(*operands(state))
        b = ref.selected(*operands(other))
        delta = b["selected"]["baseline"] - a["selected"]["baseline"]
        expected = -d * gradient[edge, 0] / 1024
        self.assertTrue(delta[edge, 0].contains(expected))
        self.assertNotEqual(expected, 0)
        steps = [self.kernel.step(x) for x in (state, other)]
        for s in steps:
            verify_step(s)
        self.assertNotEqual(steps[0].after.W_A, steps[1].after.W_A)
        self.reject(
            "collapse_W_Z_to_effective_stiffness",
            lambda: verify_step(
                replace(
                    steps[1],
                    consumed_read=FrozenJSONMap(
                        dict(
                            steps[0].consumed_read.to_dict(),
                            subject_digest=digest(other.to_payload()),
                        )
                    ),
                )
            ),
        )
        self.evidence["probes"]["equal_potential"] = [
            state.to_payload(),
            other.to_payload(),
        ]
        self.measurements["equal_potential"] = {
            "edge": edge,
            "exact_potential_equal": True,
            "baseline_difference": str(expected),
            "current_separation": separation(
                a["selected"]["current"], b["selected"]["current"]
            ),
        }

    def test_identical_current_different_inverse_flat_and_source_probe(self):
        state = self.state
        ref = Reference(state.graph.to_payload())
        c, w, z = operands(state)
        a = ref.selected(c, w, z)
        v = incidence(state.graph.to_payload()).transpose() * vector(state.C)
        for i, j in carrier_pairs(state.graph):
            if i == j:
                continue
            u = M(len(state.W_A), 1)
            u[i, 0] = v[j, 0]
            u[j, 0] = -v[i, 0]
            if (
                abs(
                    (arb_mat(u).transpose() * a["selected"]["causal_flat"])[0, 0]
                ).lower()
                > 0
            ):
                break
        else:
            self.fail("rank-one source discriminator is degenerate")
        E = Q(1, 2**18) * u * u.transpose()
        self.assertEqual(E * v, M(len(state.W_A), 1))
        Z = matrix(state.Z_4) + E
        other = replace(
            state,
            Z_4=tuple(
                tuple(str(Z[i, j]) for j in range(Z.ncols())) for i in range(Z.nrows())
            ),
        )
        self.assertEqual(exact_potential(other), exact_potential(state))
        b = ref.selected(*operands(other))
        sa, sb = [self.kernel.step(x) for x in (state, other)]
        for s in (sa, sb):
            verify_step(s)
        self.assertEqual(sa.flux, sb.flux)
        self.assertEqual(sa.after.C, sb.after.C)
        self.assertEqual(sa.after.W_A, sb.after.W_A)
        self.assertNotEqual(sa.after.Z_4, sb.after.Z_4)
        for key in ("baseline", "drive", "q", "current"):
            self.assertTrue(
                all(
                    x.contains(0)
                    for x in (a["selected"][key] - b["selected"][key]).entries()
                )
            )
        for field, key, bad in [
            (
                "consumed_read",
                "selected",
                dict(
                    sb.consumed_read["selected"].to_dict(),
                    causal_flat=sa.consumed_read.to_dict()["selected"]["causal_flat"],
                ),
            ),
            ("consumed_read", "source", sa.consumed_read.to_dict()["source"]),
            ("carrier_writer", "source", sa.carrier_writer.to_dict()["source"]),
        ]:
            self.reject(
                "equal_current_wrong_" + field + "_" + key,
                lambda field=field, key=key, bad=bad: verify_step(
                    self.changed(sb, field, key, bad)
                ),
            )
        self.evidence["probes"]["equal_current"] = [
            state.to_payload(),
            other.to_payload(),
        ]
        self.measurements["equal_current"] = {
            "incident_edges": [i, j],
            "exact_potential_equal": True,
            "represented_C_W_equal": True,
            "flat_separation": separation(
                a["selected"]["causal_flat"], b["selected"]["causal_flat"]
            ),
            "source_separation": separation(a["source"], b["source"]),
        }

    def test_four_cross_history_inputs_and_four_returned_consumers(self):
        s = self.state
        t = sentinel(s, -1)
        states = [
            s,
            replace(s, W_A=t.W_A),
            replace(s, Z_4=t.Z_4),
            replace(s, W_A=t.W_A, Z_4=t.Z_4),
        ]
        steps = [self.kernel.step(x) for x in states]
        for step in steps:
            verify_step(step)
        self.measurements["cross_history"] = {
            "W_to_S": separation(
                decode(steps[0].consumed_read["source"]),
                decode(steps[1].consumed_read["source"]),
            ),
            "Z_to_J": separation(
                decode(steps[0].consumed_read["selected"]["current"]),
                decode(steps[2].consumed_read["selected"]["current"]),
            ),
            "Z_to_W": separation(
                arb_mat(vector(steps[0].after.W_A)), arb_mat(vector(steps[2].after.W_A))
            ),
            "W_to_Z": separation(
                arb_mat(matrix(steps[0].after.Z_4)), arb_mat(matrix(steps[1].after.Z_4))
            ),
        }
        step = steps[0]
        after = step.after
        for label, state in [
            ("old_W", replace(after, W_A=s.W_A)),
            ("old_Z", replace(after, Z_4=s.Z_4)),
            ("both_old", replace(after, W_A=s.W_A, Z_4=s.Z_4)),
        ]:
            read = self.kernel.readmission(state).to_dict()
            read["subject_digest"] = digest(after.to_payload())
            separation(
                decode(read["selected"]["current"]),
                decode(step.restart_read["selected"]["current"]),
            )
            self.reject(
                "returned_" + label,
                lambda read=read: verify_step(
                    replace(step, restart_read=FrozenJSONMap(read))
                ),
            )
        self.measurements["cross_history"]["next_read_controls"] = 4

    def test_wrong_writer_time_stages_reject_after_rehash(self):
        s = self.good
        ref = Reference(s.before.graph.to_payload())
        c, w, z = operands(s.before)
        after = arb_mat(vector(s.after.C))
        neww = arb_mat(vector(s.after.W_A))
        r = ref.selected(c, w, z)
        alternatives = {
            "source_final_C": ref.selected(after, w, z)["source"],
            "source_new_W": ref.selected(c, neww, z)["source"],
            "source_final_C_new_W": ref.selected(after, neww, z)["source"],
        }
        for label, bad in alternatives.items():
            separation(r["source"], bad)
            self.reject(
                label,
                lambda bad=bad: verify_step(
                    self.changed(s, "carrier_writer", "source", intervals(bad))
                ),
            )
        for label, bad in [
            ("W_old_C", ref.log_drive(c, w, r["selected"]["current"])),
            ("W_new_W", ref.log_drive(after, neww, r["selected"]["current"])),
            ("W_baseline", ref.log_drive(after, w, r["selected"]["baseline"])),
        ]:
            separation(decode(s.writer["exponent"]), bad)
            self.reject(
                label,
                lambda bad=bad: verify_step(
                    self.changed(s, "writer", "exponent", intervals(bad))
                ),
            )
        newZ = arb_mat(matrix(s.after.Z_4))
        bad = ref.selected(c, w, newZ)
        self.reject(
            "new_Z_in_consumed_geometry",
            lambda: verify_step(
                self.changed(s, "consumed_read", "H", intervals(bad["H"]))
            ),
        )

    def test_zero_carrier_event_two_beat_causality(self):
        state = self.event.configuration.current
        self.assertTrue(all(Q(x) == 0 for row in state.Z_4 for x in row))
        one = self.kernel.step(state)
        two = self.kernel.step(one.after)
        verify_step(one)
        verify_step(two)
        ref = Reference(state.graph.to_payload())
        r = ref.selected(*operands(state))
        self.assertTrue(contains(one.consumed_read["H"], ref.I))
        self.assertGreater(frobenius(r["source"]), 0)
        self.assertTrue(any(Q(x) != 0 for row in one.after.Z_4 for x in row))
        separation(decode(two.consumed_read["H"]), ref.I)
        for label, H in [
            ("instantaneous_PC", ref.I + r["source"] / 2),
            ("OS_source_geometry", ref.I + r["source"] / 2),
        ]:
            self.reject(
                label,
                lambda H=H: verify_step(
                    self.changed(one, "consumed_read", "H", intervals(H))
                ),
            )
        self.assertEqual(two.before, one.after)
        self.measurements["two_beat_causality"] = {
            "first_H_identity": True,
            "first_source_nonzero": True,
            "second_uses_written_W_Z": True,
        }

    def test_uniform_resource_simultaneous_history_relaxation(self):
        initial = replace(
            self.state,
            C=(str(Q(self.state.charge) / len(self.state.C)),) * len(self.state.C),
        )
        state = initial
        c = Q(initial.C[0])
        d = (-arb(1)).exp()
        g0 = -arb(c) / 32768
        z0 = arb_mat(matrix(initial.Z_4))
        l0 = arb_mat([[arb(Q(w)).log()] for w in initial.W_A])
        for index in range(1, 4):
            step = self.kernel.step(state)
            verify_step(step)
            self.assertEqual(step.after.C, initial.C)
            self.assertTrue(all(Q(x) == 0 for x in step.flux))
            self.assertNotEqual(step.after.W_A, state.W_A)
            self.assertNotEqual(step.after.Z_4, state.Z_4)
            for k, w in enumerate(step.after.W_A):
                expected = d**index * l0[k, 0] + (1 - d**index) * g0
                self.assertLess(
                    abs(arb(Q(w)).log() - expected).upper().fmpq(), Q(index, 2**187)
                )
            self.assertLess(
                frobenius(arb_mat(matrix(step.after.Z_4)) - d**index * z0),
                Q(index * len(state.W_A), 2**190),
            )
            state = step.after
        self.measurements["relaxation"] = {
            "beats": 3,
            "exact_charge": initial.charge,
            "uniform_C": str(c),
            "flow_zero": True,
            "both_histories_change": True,
        }
        self.reject(
            "skip_histories_on_zero_flow",
            lambda: verify_step(replace(step, after=step.before)),
        )
        self.reject(
            "arithmetic_W_interpolation",
            lambda: self.assertTrue(
                all(
                    abs(arb(Q(w)) - (d * arb(Q(old)) + (1 - d) * g0.exp())).upper()
                    < Q(1, 2**180)
                    for old, w in zip(step.before.W_A, step.after.W_A, strict=True)
                )
            ),
        )

    def test_unequal_time_constants_only_at_configurable_primitives(self):
        from pygrc.models.grc_v4_candidate_a import candidate_a_log_interpolation
        from pygrc.models.grc_v4_pc import scalar_zoh

        oldw, targetw = 1.005, 0.995
        oldz, targetz = -1 / 1024, 1 / 2048
        w = candidate_a_log_interpolation((oldw,), (targetw,), 32, 16)[0]
        z = scalar_zoh((oldz,), (targetz,), 32, 64)[0]
        aw, az = (-arb(2)).exp(), (-arb(Q(1, 2))).exp()
        qw = lambda x: arb(Q(*x.as_integer_ratio()))
        ew = (aw * qw(oldw).log() + (1 - aw) * qw(targetw).log()).exp()
        ez = az * qw(oldz) + (1 - az) * qw(targetz)
        self.assertLess(abs(qw(w) - ew).upper(), arb(Q(1, 2**51)))
        self.assertLess(abs(qw(z) - ez).upper(), arb(Q(1, 2**62)))
        self.assertNotEqual(
            w, candidate_a_log_interpolation((oldw,), (targetw,), 32, 64)[0]
        )
        self.assertNotEqual(z, scalar_zoh((oldz,), (targetz,), 32, 16)[0])
        for fn, old, target, tau in (
            (candidate_a_log_interpolation, oldw, targetw, 16),
            (scalar_zoh, oldz, targetz, 64),
        ):
            two = fn(fn((old,), (target,), 16, tau), (target,), 16, tau)[0]
            one = fn((old,), (target,), 32, tau)[0]
            self.assertLessEqual(abs(qw(two) - qw(one)).upper(), arb(Q(1, 2**51)))
        for section, name, value in [
            ("candidate", "tau_A", 16),
            ("realization", "tau_PC", 64),
        ]:
            self.reject(
                "named_profile_changed_" + name,
                lambda section=section, name=name, value=value: native.SparkAPCKernel(
                    self.state.graph,
                    profile(self.state.graph, **{section: {name: value}}),
                ),
            )
        self.measurements["unequal_tau"] = {
            "scope": "existing configurable binary64 primitives with exact input interpretation; native binding unchanged",
            "tau_A": 16,
            "tau_PC": 64,
            "held_target_composition": True,
            "whole_map_semigroup_claimed": False,
        }

    def test_nonuniform_event_lineage_and_complete_carrier_loss_both_chiralities(self):
        for chi in (-1, 1):
            config = replace(
                self.config,
                current=sentinel(self.config.current),
                reset=sentinel(self.config.reset, -1),
            )
            model = GRC9V4(config)
            self.assertTrue(model.step().committed)
            source = model.configuration
            self.assertNotEqual(source.current.W_A, config.current.W_A)
            self.assertNotEqual(source.current.Z_4, config.current.Z_4)
            self.assertEqual(source.reset, config.reset)
            self.assertTrue(model.expand(request(model, chi)).committed)
            event = model._operation._published.completion.event.to_dict()
            report = audit_event(source, model.configuration, event)
            self.evidence["events"].append(
                {
                    "source": source.to_payload(),
                    "target": model.configuration.to_payload(),
                    "event": event,
                    "audit": report,
                }
            )
        self.measurements["event_history"] = {
            "chiralities": 2,
            "old_edges": 13,
            "unit_seeded_edges": 3,
            "whole_Z_reset": True,
            "complete_actual_both_role_archives": True,
        }

    def test_rehashed_event_history_and_allocation_mutations(self):
        model = GRC9V4(
            replace(
                self.config,
                current=sentinel(self.config.current),
                reset=sentinel(self.config.reset, -1),
            )
        )
        self.assertTrue(model.step().committed)
        source = model.configuration
        self.assertTrue(model.expand(request(model)).committed)
        target = model.configuration
        event = model._operation._published.completion.event.to_dict()
        for channel, key in [("conductance", "W_A"), ("carrier", "Z_4")]:
            bad = deepcopy(event)
            h = bad[channel + "_history"]
            a = h["source_archive"]["current"]
            if key == "W_A":
                a[key][0] = "1"
            else:
                a[key][0][0] = "0"
            schema = "conductance" if channel == "conductance" else "carrier"
            subject = "candidate" if channel == "conductance" else "carrier"
            h["history_policy"][subject]["source_history_digest"] = (
                "grcv4-history-content-sha256:"
                + digest(
                    {
                        "schema_version": "grcv4-exact-" + schema + "-history-v1",
                        "subject": subject,
                        "content": h["source_archive"],
                    }
                )
            )
            bad["rehash"] = digest(bad)
            self.reject(
                "rehashed_false_" + channel + "_archive",
                lambda bad=bad: audit_event(source, target, bad),
            )
        for label, changed in [
            ("reset_W", replace(target.current, W_A=("1",) * 16)),
            ("retain_Z", sentinel(target.current)),
            (
                "permute_W",
                replace(target.current, W_A=tuple(reversed(target.current.W_A))),
            ),
        ]:
            self.reject(
                "event_" + label,
                lambda changed=changed: audit_event(
                    source, replace(target, current=changed), event
                ),
            )
        bad = deepcopy(event)
        bad["carrier_history"]["information_loss"] = "none"
        self.reject("hidden_carrier_loss", lambda: audit_event(source, target, bad))
        vals = dict(
            zip(
                target.current.graph.live_node_ids,
                map(Q, target.current.C),
                strict=True,
            )
        )
        charge = Q(source.current.C[source.current.graph.node_index(event["expanded"])])
        for node, share in zip(
            event["module"], map(Q, ("0", "1/64", "31/32", "1/64")), strict=True
        ):
            vals[node] = charge * share
        changed = replace(
            target.current,
            C=tuple(str(vals[n]) for n in target.current.graph.live_node_ids),
        )
        self.reject(
            "event_C_family_allocation",
            lambda: audit_event(source, replace(target, current=changed), event),
        )

    def test_source_Z_effect_survives_event_in_transferred_C_W(self):
        configs = [
            replace(self.config, current=sentinel(self.config.current)),
            replace(
                self.config,
                current=replace(
                    sentinel(self.config.current),
                    Z_4=sentinel(self.config.current, -1).Z_4,
                ),
            ),
        ]
        targets = []
        sources = []
        for config in configs:
            model = GRC9V4(config)
            step, _ = observed(model)
            audit_step(config, config.current, step)
            source = model.configuration
            sources.append(source.current)
            self.assertTrue(model.expand(request(model)).committed)
            audit_event(
                source,
                model.configuration,
                model._operation._published.completion.event.to_dict(),
            )
            targets.append(model.configuration.current)
        self.assertNotEqual(sources[0].C, sources[1].C)
        self.assertNotEqual(sources[0].W_A, sources[1].W_A)
        self.assertTrue(all(Q(x) == 0 for s in targets for row in s.Z_4 for x in row))
        self.assertNotEqual(targets[0].C, targets[1].C)
        self.assertNotEqual(targets[0].W_A, targets[1].W_A)
        self.measurements["event_intervention"] = {
            "explicit_target_Z_zero": True,
            "earlier_Z_effects_survive_in_C_W": True,
        }

    def test_signed_reindexing_permutes_W_and_conjugates_Z(self):
        state = self.state
        payload = state.graph.to_payload()
        m = len(state.W_A)
        perm = list(reversed(range(m)))
        sign = [-1 if i % 3 == 0 else 1 for i in range(m)]
        payload["edges"] = [deepcopy(payload["edges"][i]) for i in perm]
        for i, e in enumerate(payload["edges"]):
            if sign[i] < 0:
                e["tail"], e["head"] = e["head"], e["tail"]
        graph = GRCV4Graph.from_payload(payload)
        moved = replace(
            state,
            graph=graph,
            W_A=tuple(state.W_A[i] for i in perm),
            Z_4=tuple(
                tuple(
                    str(sign[i] * sign[j] * Q(state.Z_4[perm[i]][perm[j]]))
                    for j in range(m)
                )
                for i in range(m)
            ),
        )
        a = self.good
        b = native.SparkAPCKernel(graph, profile(graph)).step(moved)
        verify_step(b)
        self.assertEqual(a.after.C, b.after.C)
        self.assertEqual(b.after.W_A, tuple(a.after.W_A[i] for i in perm))
        self.assertEqual(
            b.after.Z_4,
            tuple(
                tuple(
                    str(sign[i] * sign[j] * Q(a.after.Z_4[perm[i]][perm[j]]))
                    for j in range(m)
                )
                for i in range(m)
            ),
        )
        P = arb_mat(
            [[sign[i] if j == perm[i] else 0 for j in range(m)] for i in range(m)]
        )
        ref = Reference(state.graph.to_payload()).selected(*operands(state))
        for key in ("current", "causal_flat"):
            self.assertTrue(
                contains(b.consumed_read["selected"][key], P * ref["selected"][key])
            )
        self.assertTrue(
            contains(b.consumed_read["source"], P * ref["source"] * P.transpose())
        )
        self.reject(
            "sign_W_like_carrier",
            lambda: replace(
                moved, W_A=tuple(str(sign[i] * Q(moved.W_A[i])) for i in range(m))
            ),
        )
        wrong = replace(
            moved,
            Z_4=tuple(
                tuple(str(Q(state.Z_4[perm[i]][perm[j]])) for j in range(m))
                for i in range(m)
            ),
        )
        separation(
            decode(
                native.SparkAPCKernel(graph, profile(graph)).readmission(wrong)[
                    "source"
                ]
            ),
            decode(b.consumed_read["source"]),
        )
        self.measurements["covariance"] = {
            "permutation": perm,
            "signs": sign,
            "W_unsigned_permutation": True,
            "Z_signed_conjugation": True,
            "exact_outputs": True,
        }

    def test_full_state_admission_and_last_off_diagonal_frobenius_weight(self):
        c = self.fixture.center
        cert = self.certs[0]
        rho = Q(1, 2**30)
        m = len(c.W_A)
        i, j = next((i, j) for i, j in reversed(carrier_pairs(c.graph)) if i != j)

        def state(value):
            z = [["0"] * m for _ in range(m)]
            z[i][j] = z[j][i] = str(value)
            return replace(c, Z_4=tuple(map(tuple, z)))

        inside, outside = state(7 * rho / 10), state(3 * rho / 4)
        self.assertTrue(cert.membership(inside)[0])
        self.assertFalse(cert.membership(outside)[0])
        self.assertEqual(
            classify(c, self.config.policy), classify(outside, self.config.policy)
        )
        self.assertGreater(Q(cert.membership(outside)[1]), 1)
        # A much larger but read-admissible signed carrier stays outside the trap
        # through these bounded physical steps despite the qualifying C/W roster.
        far = state(Q(1, 2**15))
        with patch.object(self.fixture, "center", far):
            model = self.fixture.synthetic_window_fixture()
        for _ in range(3):
            result = model.step()
            self.assertTrue(result.committed)
            self.assertEqual(result.local_gain, 0)
            self.assertFalse(cert.membership(model.configuration.current)[0])
            self.assertEqual(
                model._operation._published.completion.reason,
                "outside certificate domain",
            )
            self.assertEqual(
                classify(model.configuration.current, self.config.policy).basins,
                classify(c, self.config.policy).basins,
            )
        self.measurements["membership"] = {
            "last_off_diagonal": [i, j],
            "inside_squared": "49/50",
            "outside_squared": "9/8",
            "same_roster": True,
            "Z_required": True,
        }

    def test_tiny_authoritative_Z_is_not_recovered_from_H(self):
        initial = replace(
            self.state,
            C=(str(Q(self.state.charge) / len(self.state.C)),) * len(self.state.C),
        )
        m = len(initial.W_A)
        z = [["0"] * m for _ in range(m)]
        z[0][0] = str(Q(1, 2**300))
        initial = replace(initial, Z_4=tuple(map(tuple, z)))
        step = self.kernel.step(initial)
        verify_step(step)
        self.assertEqual(step.before.Z_4[0][0], str(Q(1, 2**300)))
        H = decode(step.consumed_read["H"])
        self.assertTrue(H[0, 0].contains(1))
        ideal = decode(step.carrier_writer["ideal"])
        expected = (-arb(1)).exp() * Q(1, 2**300)
        self.assertTrue(ideal[0, 0].contains(expected))
        self.assertGreater(ideal[0, 0].lower(), 0)
        bad = step.carrier_writer.to_dict()
        bad["ideal"][0][0] = ["0", "0"]
        self.reject(
            "recover_Z_from_rounded_H",
            lambda step=step, bad=bad: verify_step(
                replace(step, carrier_writer=FrozenJSONMap(bad))
            ),
        )
        self.measurements["tiny_Z"] = {
            "exact_old_Z": str(Q(1, 2**300)),
            "H_interval_contains_reference": True,
            "writer_ideal_nonzero": True,
            "represented_zero_allowed_by_192_bit_policy": True,
        }

    def test_signed_carrier_cancellation_encloses_without_projection(self):
        s = self.state
        m = len(s.W_A)
        ref = Reference(s.graph.to_payload())
        c, w, _z = operands(s)
        d = (-arb(1)).exp()
        base = replace(s, Z_4=tuple(("0",) * m for _ in range(m)))
        src = ref.selected(*operands(base))["source"]
        edge = max(range(m), key=lambda i: abs(src[i, i]).upper())
        root = Q(0)
        for _ in range(6):
            zz = arb_mat(m, m)
            zz[edge, edge] = root
            value = -(1 - d) / d * ref.selected(c, w, zz)["source"][edge, edge]
            root = value.mid().fmpq()
        signs = []
        for factor in (Q(1023, 1024), Q(1025, 1024)):
            zz = [["0"] * m for _ in range(m)]
            zz[edge][edge] = str(root * factor)
            state = replace(s, Z_4=tuple(map(tuple, zz)))
            step = self.kernel.step(state)
            verify_step(step)
            signs.append(Q(step.after.Z_4[edge][edge]) > 0)
            self.assertLess(abs(Q(step.after.Z_4[edge][edge])), abs(root) / 100)
            if not signs[-1]:
                bad = step.carrier_writer.to_dict()
                bad["ideal"][edge][edge] = ["0", "0"]
                self.reject(
                    "clip_signed_Z_after_cancellation",
                    lambda step=step, bad=bad: verify_step(
                        replace(step, carrier_writer=FrozenJSONMap(bad))
                    ),
                )
        self.assertEqual(signs, [True, False])
        self.measurements["cancellation"] = {
            "edge": edge,
            "positive_and_negative_results": True,
            "clipping_rejected": True,
        }

    def test_floor_and_carrier_boundaries_are_independent(self):
        s = self.state
        m = len(s.W_A)
        self.reject("negative_W", lambda: replace(s, W_A=("-1",) + s.W_A[1:]))
        self.reject(
            "positive_W_outside_native_box",
            lambda: self.kernel.readmission(replace(s, W_A=("1/2",) * m)),
        )
        z = [["0"] * m for _ in range(m)]
        z[0][0] = "-1/32"
        self.reject(
            "carrier_outside_ball", lambda: replace(s, Z_4=tuple(map(tuple, z)))
        )
        c, w, z = operands(s)
        math = APCMath(s.graph)
        self.reject(
            "smooth_floor_crossing", lambda: math.exponent(c, w, arb_mat([[1000]] * m))
        )
        self.assertTrue(
            any(Q(x) < 0 for row in self.kernel.step(s).after.Z_4 for x in row)
        )

    def test_all_76_directions_mixed_segments_and_nine_jacobian_blocks(self):
        state = self.state
        ref = Reference(state.graph.to_payload())
        math = APCMath(state.graph)
        C, W, Z = operands(state)
        L = arb_mat([[x.log()] for x in W.entries()])
        n, m = math.n, math.m
        nx = n + m
        p = len(math.carrier_pairs)
        directions = []
        for k in range(n - 1):
            d = arb_mat(nx + p, 1)
            d[k, 0] = 1
            d[n - 1, 0] = -1
            directions.append(d)
        for k in range(m + p):
            d = arb_mat(nx + p, 1)
            d[n + k, 0] = 1
            directions.append(d)
        self.assertEqual(len(directions), 76)
        for i in range(4):
            directions.append(
                directions[i]
                + directions[n - 1 + i] / 2
                - directions[n - 1 + m + i] / 3
            )
        splits = [range(n), range(n, nx), range(nx, nx + p)]
        resolved = set()
        inverse_detected = False
        segments = 0
        # Every physical axis at three scales; mixed directions couple all histories.
        for bits in (36, 52, 80):
            eps = Q(1, 2**bits)
            for index, d in enumerate(directions):
                dc = arb_mat(d.tolist()[:n])
                dl = arb_mat(d.tolist()[n:nx])
                dz = arb_mat(m, m)
                for k, (i, j) in enumerate(math.carrier_pairs):
                    dz[i, j] = dz[j, i] = d[nx + k, 0] / (
                        1 if i == j else arb(2).sqrt()
                    )
                box = lambda a, b, eps=eps: arb_mat(
                    [
                        [
                            a[i, j] + arb(0, (abs(b[i, j]) * eps).upper().fmpq())
                            for j in range(a.ncols())
                        ]
                        for i in range(a.nrows())
                    ]
                )
                full = math.jacobian(box(C, dc), box(L, dl), box(Z, dz))
                derivative = full * d
                secant = (
                    ref.map(C + eps * dc, L + eps * dl, Z + eps * dz)
                    - ref.map(C - eps * dc, L - eps * dl, Z - eps * dz)
                ) / (2 * eps)
                for i in range(derivative.nrows()):
                    a, b = derivative[i, 0], secant[i, 0]
                    self.assertTrue(
                        a.contains(b) or (a.is_zero() and b.contains(0)),
                        (bits, index, i),
                    )
                segments += 1
                if bits == 80 and index < 76:
                    group = 0 if index < n - 1 else 1 if index < n - 1 + m else 2
                    for out, rows in enumerate(splits):
                        mutant = arb_mat(full)
                        for i in rows:
                            for j in splits[group]:
                                mutant[i, j] = 0
                        wrong = mutant * d
                        if any(not wrong[i, 0].overlaps(secant[i, 0]) for i in rows):
                            resolved.add((out, group))
                    if group == 2:
                        selected = ref.selected(C, W, Z)
                        flat = selected["selected"]["causal_flat"]
                        wrong_df = selected["H"].inv() * (dz / 2) * flat
                        correction = (1 - (-arb(1)).exp()) * arb_mat(
                            [
                                [
                                    (1 if i == j else arb(2).sqrt())
                                    * sum(
                                        int(
                                            i
                                            in [
                                                k
                                                for k, pair in enumerate(ref.pairs)
                                                if node in pair
                                            ]
                                            and j
                                            in [
                                                k
                                                for k, pair in enumerate(ref.pairs)
                                                if node in pair
                                            ]
                                        )
                                        for node in range(n)
                                    )
                                    / 4
                                    * (
                                        flat[i, 0] * wrong_df[j, 0]
                                        + flat[j, 0] * wrong_df[i, 0]
                                    )
                                ]
                                for i, j in math.carrier_pairs
                            ]
                        )
                        wrong = arb_mat(derivative)
                        for k in range(p):
                            wrong[nx + k, 0] += correction[k, 0]
                        inverse_detected |= any(
                            not wrong[nx + k, 0].overlaps(secant[nx + k, 0])
                            for k in range(p)
                        )
        self.assertEqual(resolved, {(i, j) for i in range(3) for j in range(3)})
        self.assertTrue(inverse_detected)
        self.measurements["mutations"] += [
            "drop_jacobian_" + a + "_from_" + b
            for a in ("C", "logW", "Z")
            for b in ("C", "logW", "Z")
        ] + ["omit_inverse_H_derivative"]
        self.measurements["derivatives"] = {
            "independent_axes": 76,
            "mixed_directions": 4,
            "step_bits": [36, 52, 80],
            "segments": segments,
            "all_nine_blocks_resolved": True,
            "inverse_H_term_discriminated": True,
            "center_checks_retained": True,
        }

    def test_tiny_contrast_does_not_hide_conductance_writer_activity(self):
        s = self.state
        ref = Reference(s.graph.to_payload())
        c, w, z = operands(s)
        for _ in range(20):
            r = ref.selected(c, w, z)
            w = arb_mat(
                [[arb(x.mid().fmpq())] for x in r["selected"]["drive"].entries()]
            )
        w = arb_mat([[x * (1 + arb(Q(1, 2**120)))] for x in w.entries()])
        state = replace(s, W_A=tuple(str(x.mid().fmpq()) for x in w.entries()))
        step = self.kernel.step(state)
        verify_step(step)
        r = ref.selected(*operands(state))
        J = max(abs(x).lower().fmpq() for x in r["selected"]["current"].entries())
        source = frobenius(r["source"])
        self.assertGreater(J, Q(1, 10**6))
        self.assertLess(source, Q(1, 10**60))
        self.assertNotEqual(state.W_A, step.after.W_A)
        self.measurements["tiny_contrast"] = {
            "current_lower": str(J),
            "source_upper": str(source),
            "W_writer_active": True,
        }

    def test_late_three_coordinate_failures_roll_back_and_retry_once(self):
        for phase in (
            "W_prepared",
            "Z_prepared",
            "bad_W_after_Z",
            "bad_Z_after_W",
            "returned",
            "window",
            "publication",
        ):
            model = self.fixture.synthetic_window_fixture()
            self.assertTrue(model.step().committed)
            self.assertTrue(model.step().committed)
            before = model.snapshot()
            publication = model._operation._spark_scope.published
            calls = []
            kernel = native.SparkAPCKernel
            if phase in ("W_prepared", "Z_prepared"):
                name = (
                    "_conductance_writer"
                    if phase == "W_prepared"
                    else "_carrier_writer"
                )
                original = getattr(kernel, name)

                def fail(*args, original=original):
                    original(*args)
                    raise RuntimeError("injected prepared history")

                context = patch.object(kernel, name, fail)
            elif phase in ("bad_W_after_Z", "bad_Z_after_W"):
                original = ExactAdaptiveCarrierState.advance_histories

                def fail(state, flux, duration, W, Z, original=original, phase=phase):
                    if phase == "bad_W_after_Z":
                        W = ("0",) + W[1:]
                    else:
                        Z = [list(row) for row in Z]
                        Z[0][0] = "1"
                    return original(state, flux, duration, W, Z)

                context = patch.object(
                    ExactAdaptiveCarrierState, "advance_histories", fail
                )
            elif phase == "returned":
                original = kernel._admitted_read

                def fail(*args, original=original, calls=calls):
                    result = original(*args)
                    calls.append(1)
                    if len(calls) == 2:
                        raise RuntimeError("injected returned read")
                    return result

                context = patch.object(kernel, "_admitted_read", fail)
            else:
                name = "progress" if phase == "window" else "prepare"
                original = getattr(owner, name)

                def fail(*args, original=original, **kw):
                    original(*args, **kw)
                    raise RuntimeError("injected late publication")

                context = patch.object(owner, name, fail)
            with context:
                result = model.step()
            self.assertFalse(result.committed, phase)
            self.assertEqual(model.snapshot(), before, phase)
            self.assertIs(model._operation._spark_scope.published, publication)
            self.assertEqual(model.step().local_gain, 1)
            self.assertEqual(model.step().local_gain, 0)
        self.measurements["rollback"] = {
            "ordinary_phases": 7,
            "full_snapshot_equal": True,
            "publication_identity_equal": True,
            "retry_once_only": True,
        }

    def test_reset_only_and_event_archive_failures_are_atomic(self):
        import pygrc.models.grc_9_v4_spark_apc_event as event_module

        for phase in ("reset_read", "carrier_archive", "carrier_target"):
            model = GRC9V4(self.config)
            self.assertTrue(model.step().committed)
            before = model.snapshot()
            publication = model._operation._spark_scope.published
            if phase == "reset_read":
                original = native.SparkAPCKernel.readmission

                def fail(k, state, original=original):
                    if len(state.C) == 15 and any(
                        Q(w) == Q(8191, 8192) for w in state.W_A
                    ):
                        raise RuntimeError("injected reset")
                    return original(k, state)

                context = patch.object(native.SparkAPCKernel, "readmission", fail)
            elif phase == "carrier_archive":
                original = event_module.capture

                def fail(*args, original=original):
                    original(*args)
                    raise RuntimeError("injected archives prepared")

                context = patch.object(event_module, "capture", fail)
            else:
                original = event_module.target
                count = []

                def fail(*args, original=original, count=count):
                    result = original(*args)
                    count.append(1)
                    if len(count) == 2:
                        raise RuntimeError("injected reset target")
                    return result

                context = patch.object(event_module, "target", fail)
            with context:
                result = model.expand(request(model))
            self.assertFalse(result.committed, phase)
            self.assertEqual(model.snapshot(), before)
            self.assertIs(model._operation._spark_scope.published, publication)
            source = model.configuration
            self.assertTrue(model.expand(request(model)).committed)
            audit_event(
                source,
                model.configuration,
                model._operation._published.completion.event.to_dict(),
            )
        self.measurements["event_rollback"] = {
            "phases": 3,
            "whole_publication_unchanged": True,
            "retries": 3,
        }

    def test_observers_and_archives_do_not_alias_or_advance_either_history(self):
        model = GRC9V4(
            replace(
                self.config,
                current=sentinel(self.config.current),
                reset=sentinel(self.config.reset, -1),
            )
        )
        self.assertTrue(model.step().committed)
        self.assertTrue(model.expand(request(model)).committed)
        before = model.snapshot()
        with (
            patch.object(
                native.SparkAPCKernel,
                "_conductance_writer",
                side_effect=AssertionError("observation wrote W"),
            ),
            patch.object(
                native.SparkAPCKernel,
                "_carrier_writer",
                side_effect=AssertionError("observation wrote Z"),
            ),
        ):
            model.compute_observables()
            snapshot = model.snapshot()
            restored = GRC9V4.from_state(snapshot)

        def poison(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "W_A":
                        child[0] = "0"
                    elif key == "Z_4":
                        child[0][0] = "1"
                    else:
                        poison(child)
            elif isinstance(value, list):
                for child in value:
                    poison(child)

        poison(snapshot)
        self.assertEqual(model.snapshot(), before)
        self.assertEqual(restored.configuration, model.configuration)
        self.assertTrue(model.step().committed and restored.step().committed)
        self.assertEqual(model.configuration, restored.configuration)
        self.assertTrue(model.reset().committed)
        self.assertEqual(model.configuration.current.W_A, model.configuration.reset.W_A)
        self.assertEqual(model.configuration.current.Z_4, model.configuration.reset.Z_4)


if __name__ == "__main__":
    unittest.main()
