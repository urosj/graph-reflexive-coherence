"""Bounded A_CI_PC two-history pressure; no source-to-completion trajectory."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from acipc_native_spark_audit import (
    audit_event,
    audit_step,
    audit_trace,
    digest,
    separation,
)
from acipc_native_spark_pressure_oracle import (
    Reference,
    admit_proposal,
    audit_manufactured,
    contains,
    frobenius,
    frozen_reference_root,
    manufacture,
    upper,
    verify_step,
)
from cos_native_spark_oracle import matrix, vector
from cpc_native_spark_pressure_oracle import decode, intervals
from p991a6_acipc_preflight import decoded, transition
from p991a6_acipc_subjects import profile, request

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_acipc as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_acipc_math import ACIPCMath
from pygrc.models.grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from pygrc.models.grc_v4_spark_carrier import carrier_pairs
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_acipc as fixtures


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


def observed(model):
    initial, publication = model.configuration, model._operation._spark_scope.published
    records, steps = [], []
    kernel = native.SparkACIPCKernel
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


class ACIPCNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeACIPCTests.setUpClass()
        cls.fixture = fixtures.NativeACIPCTests()
        cls.config = cls.fixture.config
        cls.event = cls.fixture.event_model
        cls.certs = cls.fixture.certificates
        cls.state = sentinel(cls.event.configuration.current, resources=True)
        cls.kernel = owner.kernel(cls.event.configuration)
        cls.good = cls.kernel.step(cls.state)
        cls.measurements = {"mutations": []}
        caches = cls.kernel.cache_info()
        if not all(
            caches[key]["hits"] > 0 for key in ("graph", "rows", "domain", "decay")
        ):
            raise AssertionError(
                "static caches must be active before pressure sampling"
            )
        cls.measurements["caches_before_pressure"] = caches
        cls.evidence = {
            "actual_steps": [],
            "events": [],
            "probes": {},
            "manufactured": {},
            "counterfeit": {},
        }

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
        separation(ref.selected(c, w, z)["H"], ref.selected(cc, ww, z)["H"])
        a = ACIPCMath(state.graph)
        rows = a.rows(c, w)[0]
        a.root(c, arb_mat([[x.log()] for x in w.entries()]), zz, w)
        self.assertEqual(intervals(arb_mat(rows)), intervals(arb_mat(a.rows(c, w)[0])))
        self.measurements["writer_independence"] = {
            "detached_orders_equal": True,
            "held_S_unchanged": True,
            "new_Z_irrelevant_to_held_W": True,
            "new_C_W_irrelevant_to_held_Z": True,
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
                lambda section=section, name=name, value=value: native.SparkACIPCKernel(
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
        b = native.SparkACIPCKernel(graph, profile(graph)).step(moved)
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
                native.SparkACIPCKernel(graph, profile(graph)).readmission(wrong)[
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
        math = ACIPCMath(s.graph)
        self.reject(
            "smooth_floor_crossing", lambda: math.exponent(c, w, arb_mat([[1000]] * m))
        )
        self.assertTrue(
            any(Q(x) < 0 for row in self.kernel.step(s).after.Z_4 for x in row)
        )

    def test_all_76_directions_mixed_segments_and_nine_jacobian_blocks(self):
        state = self.state
        ref = Reference(state.graph.to_payload())
        math = ACIPCMath(state.graph)
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
            # One enclosing box contains every axis and mixed segment at this
            # scale. Reuse its full implicit Jacobian, not a point derivative.
            enlarge = lambda A, eps=eps: arb_mat(
                [[x + arb(0, eps) for x in row] for row in A.tolist()]
            )
            Zbox = arb_mat(Z)
            for i, j in math.carrier_pairs:
                Zbox[i, j] = Zbox[j, i] = Z[i, j] + arb(0, eps)
            full = math.jacobian(enlarge(C), enlarge(L), Zbox)
            for index, d in enumerate(directions):
                dc = arb_mat(d.tolist()[:n])
                dl = arb_mat(d.tolist()[n:nx])
                dz = arb_mat(m, m)
                for k, (i, j) in enumerate(math.carrier_pairs):
                    dz[i, j] = dz[j, i] = d[nx + k, 0] / (
                        1 if i == j else arb(2).sqrt()
                    )
                self.assertTrue(all(abs(x).upper() <= 1 for x in d.entries()))
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
            "full_implicit_box_evaluations": 3,
            "shared_boxes_cover_all_segments": True,
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
            kernel = native.SparkACIPCKernel
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
                original = native.SparkACIPCKernel.readmission

                def fail(k, state, original=original):
                    if len(state.C) == 15 and any(
                        Q(w) == Q(8191, 8192) for w in state.W_A
                    ):
                        raise RuntimeError("injected reset")
                    return original(k, state)

                context = patch.object(native.SparkACIPCKernel, "readmission", fail)
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
                native.SparkACIPCKernel,
                "_conductance_writer",
                side_effect=AssertionError("observation wrote W"),
            ),
            patch.object(
                native.SparkACIPCKernel,
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

    def test_manufactured_reference_H_and_equal_current_twin(self):
        from acipc_native_spark_pressure_oracle import audit_read

        base = replace(self.state, C=("3/2",) * 12 + ("1",) * 3)
        ref = Reference(base.graph.to_payload())
        C, W, _ = operands(base)
        a, record_a = manufacture(base, ref.I)
        first = ref.read(C, W, ref.I)
        v = ref.B.transpose() * C
        # Two incident edges with u^T B^T C = 0, but u^T f != 0.
        choices = []
        for i, j in ref.carrier_pairs:
            if i == j:
                continue
            u = arb_mat(ref.m, 1)
            u[i, 0], u[j, 0] = v[j, 0], -v[i, 0]
            score = abs((u.transpose() * first["causal_flat"])[0, 0]).lower().fmpq()
            choices.append((score, i, j, u))
        score, i, j, u = max(choices, key=lambda x: x[0])
        self.assertGreater(score, 0)
        self.assertTrue((u.transpose() * v)[0, 0].is_zero())
        E = u * u.transpose() / 1024
        b, record_b = manufacture(base, ref.I + E / 2)
        second = ref.read(C, W, ref.I + E / 2)
        self.assertTrue(
            all(
                x.contains(0)
                for x in (second["potential"] - first["potential"]).entries()
            )
        )
        for key in ("baseline", "drive", "q", "current"):
            self.assertLess(upper(second[key] - first[key]), Q(1, 2**700))
        Sf, Sg = ref.source(first["causal_flat"]), ref.source(second["causal_flat"])
        flat_gap = separation(first["causal_flat"], second["causal_flat"])
        source_gap = separation(Sf, Sg)
        self.assertGreater(Q(source_gap), Q(1, 2**192))
        one, two = self.kernel.step(a), self.kernel.step(b)
        verify_step(one)
        verify_step(two)
        self.assertEqual(one.after.C, two.after.C)
        self.assertEqual(one.after.W_A, two.after.W_A)
        self.assertNotEqual(one.after.Z_4, two.after.Z_4)
        decay = (-arb(1)).exp()
        expected_a = (1 - 2 * decay) * Sf
        expected_difference = decay * E + (1 - 2 * decay) * (Sg - Sf)
        # Bounds include the exact-real to rational bridge and the native writer lattice.
        budget = 2 * (
            Q(one.carrier_component_error)
            + Q(record_a["bridge_radius"])
            + Q(record_b["bridge_radius"])
            + Q(record_a["conversion_error"])
            + Q(record_b["conversion_error"])
        )
        self.assertLess(upper(arb_mat(matrix(one.after.Z_4)) - expected_a), budget)
        self.assertLess(
            upper(
                arb_mat(matrix(two.after.Z_4))
                - arb_mat(matrix(one.after.Z_4))
                - expected_difference
            ),
            budget,
        )
        self.assertGreater(frobenius(expected_a), 0)
        self.assertNotEqual(one.after.W_A, a.W_A)
        for label, step in (
            ("reference_cancellation", one),
            ("equal_current_twin", two),
        ):
            self.evidence["manufactured"][label] = (
                record_a if step is one else record_b
            ) | {"step": transition(step)}
            audit_manufactured(self.evidence["manufactured"][label])
        # Rebind an otherwise valid role to defeat a trivial digest-only rejection.
        bad = one.consumed_read.to_dict()
        bad["subject_digest"] = digest(b.to_payload())
        with self.assertRaisesRegex(
            AssertionError, "incoming-carrier geometry|selected|root"
        ):
            audit_read(ref, b, bad)
        self.measurements["mutations"].append("equal_J_C_W_root_role_swap_after_rehash")
        for label, source in [
            ("net_Z_plus_S", arb_mat(ref.m, ref.m)),
            ("geometry_factor_twice", Sf / 2),
        ]:
            changed = self.changed(one, "carrier_writer", "source", intervals(source))
            with self.assertRaisesRegex(AssertionError, "old-state carrier source"):
                verify_step(changed)
            self.measurements["mutations"].append(label)
        self.measurements["manufactured"] = {
            "incident_edges": [i, j],
            "same_represented_C_W": True,
            "distinct_Z": True,
            "flat_gap": flat_gap,
            "source_gap": source_gap,
            "conversion_bits": 600,
            "reference_H_nonzero_histories": True,
            "cross_writer_identity": True,
        }

    def test_frozen_reference_counterfeit_converges_and_is_rejected(self):
        from acipc_native_spark_pressure_oracle import audit_read

        ref = Reference(self.state.graph.to_payload())
        C, W, Z = operands(self.state)
        wrong = frozen_reference_root(ref, C, W, Z)
        payload = self.good.consumed_read.to_dict()
        payload["proposal"] = intervals(wrong["flat"])
        payload["proposal_residual"] = ["0", str(wrong["wrong_residual"])]
        payload["root_error"] = ["0", str(wrong["wrong_residual"] / (1 - ref.rate))]
        # Skip expanded diagnostics only so the intended full-input residual detector fires first.
        with self.assertRaisesRegex(AssertionError, "actual full-input root residual"):
            audit_read(ref, self.state, payload, compact=True)
        self.measurements["mutations"].append("converged_frozen_G_wrong_equation")
        self.evidence["counterfeit"] = {
            "state": self.state.to_payload(),
            "payload": payload,
            "wrong_residual": str(wrong["wrong_residual"]),
            "actual_residual": str(wrong["actual_residual"]),
            "iterations": wrong["iterations"],
        }
        original = ACIPCMath.read
        frozen = []

        def mutated(math, C, W, H, rows=None):
            result = original(math, C, W, H, rows)
            if not frozen:
                frozen.append(result["drive"])
            G = frozen[0]
            theta = arb_mat(
                [[(W[i, 0] - G[i, 0]) / (W[i, 0] + G[i, 0])] for i in range(math.m)]
            )
            J = arb_mat(
                [
                    [result["baseline"][i, 0] / (1 - theta[i, 0] / 4)]
                    for i in range(math.m)
                ]
            )
            flat = H.solve(
                arb_mat([[theta[i, 0] * J[i, 0] / 2] for i in range(math.m)])
            )
            return result | {"drive": G, "q": theta, "current": J, "causal_flat": flat}

        with patch.object(ACIPCMath, "read", mutated):
            counterfeit = self.kernel.readmission(self.state)
        with self.assertRaisesRegex(
            AssertionError, "incoming-carrier geometry|selected|root"
        ):
            audit_read(ref, self.state, counterfeit)
        self.measurements["mutations"].append(
            "production_frozen_G_self_consistent_residual"
        )
        self.measurements["frozen_reference"] = {
            "wrong_residual": str(wrong["wrong_residual"]),
            "true_residual": str(wrong["actual_residual"]),
            "budget": str(Q(1, 2**192)),
            "production_counterfeit_completed": True,
        }

    def test_trial_chain_derivative_reference_and_residual_purity(self):
        ref = Reference(self.state.graph.to_payload())
        C, W, Z = operands(self.state)
        math = ACIPCMath(self.state.graph)
        f = arb_mat([[Q((-1) ** i, 256)] for i in range(ref.m)])
        g = f / 2
        first = math.read(C, W, math.composite_geometry(f, Z))
        math.read(C, W, math.composite_geometry(g, Z))
        again = math.read(C, W, math.composite_geometry(f, Z))
        self.assertEqual(
            {k: intervals(v) for k, v in first.items()},
            {k: intervals(v) for k, v in again.items()},
        )
        independent = ref.read(C, W, ref.composite_geometry(f, Z))
        for key in independent:
            self.assertLess(upper(first[key] - independent[key]), Q(1, 2**700))
        second = ref.read(C, W, ref.composite_geometry(g, Z))
        for key in ("potential", "baseline", "drive", "q", "current", "causal_flat"):
            separation(independent[key], second[key])
        # Finite H-direction pressure on dG and dtheta at a nonstationary root.
        root = ref.selected(C, W, Z)
        H = root["H"]
        eps = Q(1, 2**100)
        E = arb_mat(ref.m, ref.m)
        E[0, 0] = 1
        a = ref.read(C, W, H - eps * E)
        b = ref.read(C, W, H + eps * E)
        dj = (b["baseline"] - a["baseline"]) / (2 * eps)
        mid = ref.read(C, W, H)
        dG = arb_mat(
            [
                [-mid["drive"][i, 0] * mid["baseline"][i, 0] * dj[i, 0] / 32768]
                for i in range(ref.m)
            ]
        )
        dq = arb_mat(
            [
                [-2 * W[i, 0] * dG[i, 0] / (W[i, 0] + mid["drive"][i, 0]) ** 2]
                for i in range(ref.m)
            ]
        )
        self.assertLess(upper(dG - (b["drive"] - a["drive"]) / (2 * eps)), Q(1, 2**180))
        self.assertLess(upper(dq - (b["q"] - a["q"]) / (2 * eps)), Q(1, 2**180))
        self.assertGreater(
            max(abs(x).lower().fmpq() for x in dG.entries()), Q(1, 2**100)
        )
        self.assertGreater(
            max(abs(x).lower().fmpq() for x in dq.entries()), Q(1, 2**100)
        )
        flat = root["flat"]
        _, _, Ff, Jf = math.flat_partials(C, W, Z, flat)
        omitted_reference_detected = False
        for index in range(ref.m):
            direction = arb_mat(ref.m, 1)
            direction[index, 0] = 1
            left = ref.read(C, W, ref.composite_geometry(flat - eps * direction, Z))
            right = ref.read(C, W, ref.composite_geometry(flat + eps * direction, Z))
            for key, derivative in (("causal_flat", Ff), ("current", Jf)):
                self.assertLess(
                    upper(
                        derivative * direction - (right[key] - left[key]) / (2 * eps)
                    ),
                    Q(1, 2**180),
                )
            # Deliberately omit geometry -> G -> theta from the J derivative.
            dj0 = (right["baseline"] - left["baseline"]) / (2 * eps)
            wrong = arb_mat(
                [
                    [dj0[i, 0] / (1 - root["selected"]["q"][i, 0] / 4)]
                    for i in range(ref.m)
                ]
            )
            omitted_reference_detected |= max(
                abs(x).lower().fmpq() for x in (wrong - Jf * direction).entries()
            ) > Q(1, 2**192)
        self.assertTrue(omitted_reference_detected)
        self.measurements["mutations"].append(
            "omit_geometry_to_read_reference_derivative"
        )
        self.measurements["trial_chain"] = {
            "all_geometry_dependent_fields_resolved": True,
            "dG_dtheta_identities": True,
            "native_Ff_Jf_directions": 16,
            "omitted_reference_derivative_detected": True,
            "residual_path_independent": True,
            "fixed_input_weighted_rows_reusable": True,
        }

    def test_zero_carrier_target_requires_composite_readmission(self):
        from aci_native_spark_oracle import Reference as CIReference

        state = self.event.configuration.current
        self.assertTrue(all(Q(x) == 0 for row in state.Z_4 for x in row))
        before = state.to_payload()
        with (
            patch.object(
                native.SparkACIPCKernel,
                "_carrier_writer",
                side_effect=AssertionError("read wrote Z"),
            ),
            patch.object(
                native.SparkACIPCKernel,
                "_conductance_writer",
                side_effect=AssertionError("read wrote W"),
            ),
        ):
            admitted = self.kernel.readmission(state)
        self.assertEqual(state.to_payload(), before)
        ref = Reference(state.graph.to_payload())
        C, W, Z = operands(state)
        r = ref.selected(C, W, Z)
        ci = CIReference(state.graph.to_payload()).selected(C, W)
        self.assertGreater(Q(separation(r["H"], ref.I)), Q(1, 2**192))
        self.assertLess(upper(r["H"] - ci["H"]), Q(1, 2**600))
        one = self.kernel.step(state)
        two = self.kernel.step(one.after)
        verify_step(one)
        verify_step(two)
        self.assertEqual(one.consumed_read, admitted)
        self.assertTrue(any(Q(x) != 0 for row in one.after.Z_4 for x in row))
        separation(decode(two.consumed_read["H"]), decode(one.consumed_read["H"]))
        with self.assertRaisesRegex(AssertionError, "incoming-carrier geometry"):
            verify_step(self.changed(one, "consumed_read", "H", intervals(ref.I)))
        self.measurements["mutations"].append(
            "zero_carrier_target_reference_H_shortcut"
        )
        self.measurements["event_composite"] = {
            "zero_Z_nonreference_H": True,
            "matches_A_CI_read_at_transferred_C_W": True,
            "first_beat_writes_Z": True,
            "second_beat_consumes_W_Z": True,
            "event_read_writes_neither": True,
        }

    def test_complete_root_tuple_sign_and_cross_writer_identity(self):
        from acipc_native_spark_pressure_oracle import audit_read

        step = self.good
        ref = Reference(step.before.graph.to_payload())
        C, W, Z = operands(step.before)
        r = ref.selected(C, W, Z)
        a = (-arb(1)).exp()
        identity = (2 * a - 1) * Z + 2 * (1 - a) * (r["H"] - ref.I)
        self.assertLess(
            upper(arb_mat(matrix(step.after.Z_4)) - identity),
            Q(step.carrier_component_error),
        )
        # Quadratic geometry is insensitive to sign; the flat equation is not.
        f = r["flat"]
        self.assertLess(upper(ref.source(-f) - ref.source(f)), Q(1, 2**700))
        wrong = step.consumed_read.to_dict()
        wrong["flat"] = intervals(-decode(wrong["flat"]))
        with self.assertRaisesRegex(AssertionError, "independent selected root"):
            audit_read(ref, step.before, wrong)
        self.measurements["mutations"].append("flat_sign_invisible_to_source_geometry")
        self.assertGreater(
            upper(
                2 * r["H"] * (-f)
                - arb_mat(
                    [
                        [r["selected"]["q"][i, 0] * r["selected"]["current"][i, 0]]
                        for i in range(ref.m)
                    ]
                )
            ),
            Q(1, 2**192),
        )
        for name, value in [
            ("potential", r["selected"]["potential"] * 2),
            ("baseline", r["selected"]["baseline"] * 2),
            ("drive", r["selected"]["drive"] + arb_mat([[Q(1, 2**100)]] * ref.m)),
            ("q", r["selected"]["q"] * 2),
        ]:
            bad = step.consumed_read.to_dict()
            bad["selected"][name] = intervals(value)
            with self.assertRaisesRegex(AssertionError, "selected " + name):
                audit_read(ref, step.before, bad)
            self.measurements["mutations"].append("complete_root_" + name)
        S = ref.source(r["flat"])
        math = ACIPCMath(step.before.graph)
        self.assertLess(
            upper(math.composite_geometry(r["flat"], S) - (ref.I + S)), Q(1, 2**700)
        )
        held = a * S + (1 - a) * S
        self.assertLess(upper(held - S), Q(1, 2**700))
        separation(ref.I + S, ref.I + S / 2)
        self.measurements["composition"] = {
            "stationary_gain": 2,
            "source_sign_requires_flat_equation": True,
            "cross_writer_identity": True,
        }

    def test_proposals_stagnation_and_trial_work_do_not_acquire_authority(self):
        from acipc_native_spark_pressure_oracle import audit_read, midpoint

        ref = Reference(self.state.graph.to_payload())
        C, W, Z = operands(self.state)
        selected = ref.selected(C, W, Z)
        starts = [
            arb_mat(ref.m, 1),
            midpoint(ref.read(C, W, ref.I + Z / 2)["causal_flat"]),
            midpoint(selected["flat"]),
        ]
        # Under-relaxation is only proposal work; the full residual admits it.
        for start in starts:
            f = start
            for _ in range(90):
                next_f = ref.read(C, W, ref.composite_geometry(f, Z))["causal_flat"]
                if upper(next_f - f) < Q(1, 2**80):
                    break
                f = midpoint((f + next_f) / 2)
            residual, radius = admit_proposal(ref, C, W, Z, f)
            self.assertLess(radius, Q(1, 2**79))
            self.assertLessEqual(upper(f - selected["flat"]), radius + Q(1, 2**630))
        pc = starts[1]
        residual, radius = admit_proposal(ref, C, W, Z, pc)
        self.assertLess(upper(pc) + radius, Q(1, 32))
        bad = self.good.consumed_read.to_dict()
        # Quantized stagnation is only an iterate property, not an error estimate.
        stagnant = arb_mat([[Q(0)]] * ref.m)
        from cpc_native_spark_pressure_oracle import round_even

        exact_update = ref.read(C, W, ref.composite_geometry(stagnant, Z))[
            "causal_flat"
        ]
        quantized_update = arb_mat(
            [[round_even(x.mid().fmpq(), 8)] for x in exact_update.entries()]
        )
        self.assertEqual(stagnant, quantized_update)
        self.assertGreater(
            max(abs(x).lower().fmpq() for x in exact_update.entries()), Q(1, 2**192)
        )
        bad["proposal"] = intervals(stagnant)
        bad["proposal_residual"] = ["0", "0"]
        bad["root_error"] = ["0", "0"]
        with self.assertRaisesRegex(AssertionError, "actual full-input root residual"):
            audit_read(ref, self.state, bad, compact=True)
        self.measurements["mutations"].append(
            "represented_stagnation_zero_residual_claim"
        )
        with self.assertRaisesRegex(AssertionError, "outside declared root ball"):
            admit_proposal(ref, C, W, Z, arb_mat([[Q(1, 16)]] * ref.m))
        original = self.state.to_payload()
        payload = self.kernel.readmission(self.state).to_dict()
        payload["source"][0][0] = ["1", "1"]
        payload["H"][0][0] = ["7", "7"]
        payload["flat"][0][0] = ["1", "1"]
        self.assertEqual(self.state.to_payload(), original)
        with ctx.workprec(256):
            trial = self.kernel._admitted_read(self.state)
            trial["geometry"][0, 0] = 7
            trial["S"][0, 0] = 1
            trial["flat"][0, 0] = 1
        self.assertEqual(self.state.to_payload(), original)
        self.assertEqual(self.kernel.step(self.state), self.good)
        self.measurements["proposals"] = {
            "cold_PC_warm_starts": 3,
            "under_relaxed_work_only": True,
            "PC_proposal_may_be_admitted": True,
            "PC_residual": str(residual),
            "PC_radius": str(radius),
            "detached_trial_aliasing": True,
        }

    def test_every_native_trial_refreshes_A_chain_on_frozen_inputs(self):
        model = GRC9V4(replace(self.event.configuration, current=self.state))
        initial = model.snapshot()
        roots = []
        active = []
        geometry = []
        root_impl, read_impl, geometry_impl = (
            ACIPCMath.root,
            ACIPCMath.read,
            ACIPCMath.composite_geometry,
        )

        def root(math, C, L, Z, W=None, limit=60):
            frozen = {
                key: intervals(value)
                for key, value in [("C", C), ("L", L), ("W", W), ("Z", Z)]
            }
            row = {"entry": frozen, "trials": []}
            roots.append(row)
            active.append(row)
            try:
                result = root_impl(math, C, L, Z, W, limit)
                self.assertEqual(
                    frozen,
                    {
                        key: intervals(value)
                        for key, value in [("C", C), ("L", L), ("W", W), ("Z", Z)]
                    },
                )
                self.assertEqual(model.snapshot(), initial)
                return result
            finally:
                active.pop()

        def geom(math, f, Z):
            H = geometry_impl(math, f, Z)
            if active:
                geometry[:] = [intervals(f), intervals(Z)]
            return H

        def read(math, C, W, H, rows=None):
            result = read_impl(math, C, W, H, rows)
            if active:
                active[-1]["trials"].append(
                    {
                        "C": intervals(C),
                        "W": intervals(W),
                        "Z": geometry[1],
                        "flat": geometry[0],
                        "H": intervals(H),
                        "read": {
                            key: intervals(value) for key, value in result.items()
                        },
                    }
                )
                self.assertEqual(model.snapshot(), initial)
            return result

        with (
            patch.object(ACIPCMath, "root", root),
            patch.object(ACIPCMath, "read", read),
            patch.object(ACIPCMath, "composite_geometry", geom),
        ):
            step, _trace = observed(model)
        self.assertEqual(len(roots), 2)
        from acipc_native_spark_audit import audit_trials

        result = audit_trials(step, roots)
        self.evidence["root_trials"] = {
            "step": transition(step),
            "roots": roots,
            "audit": result,
        }
        self.measurements["root_trial_ownership"] = result
        self.assertEqual(self.kernel.step(self.state), step)
