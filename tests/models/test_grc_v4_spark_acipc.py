"""Bounded A_CI_PC full-state mathematics, event history and atomic lifecycle."""

import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_spark_acipc import SparkACIPCKernel
from pygrc.models.grc_v4_spark_acipc_math import ACIPCMath
from pygrc.models.grc_v4_spark_adaptive_carrier import (
    ExactAdaptiveCarrierState,
    QuarticACIPCProfile,
)
from pygrc.models.grc_v4_spark_carrier import exact_state
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from acipc_native_spark_oracle import Reference, audit_read, verify_step
from acipc_native_spark_oracle import classify as independent_classify
from cos_native_spark_oracle import matrix, vector
from p991a6_acipc_subjects import certificate_pair, configuration, profile, request


class NativeACIPCTests(shared.NativeSparkCompletionTests):
    @classmethod
    def setUpClass(cls):
        cls.config = configuration()
        cls.source_model = GRC9V4(cls.config)
        r = cls.source_model.step()
        assert r.committed, r.reason
        cls.event_model = cls.source_model.duplicate()
        r = cls.event_model.expand(request(cls.event_model))
        assert r.committed, r.reason
        cls.certificates, cls.center = certificate_pair(cls.event_model)

    def test_full_domain_mathematics_and_exact_membership(self):
        c = self.certificates[0]
        self.assertTrue(c.membership(self.center)[0])
        self.assertFalse(c.membership(self.event_model.configuration.current)[0])
        self.assertLess(Q(c.proof["q"]), 1)
        self.assertLess(Q(c.proof["full_step_error"]), Q(c.proof["image_margin"]))
        self.assertEqual(c.proof["relative_dimension"], 76)
        self.assertEqual(c.proof["conductance_dimension"], 16)
        self.assertTrue(
            c.proof["numerical_bound"]["writer_resource_propagation_included"]
        )
        self.assertEqual(CompletionCertificate.from_payload(c.to_payload()), c)
        self.assert_rows(self.center)

    def assert_rows(self, state):
        policy = self.config.policy
        expected = independent_classify(
            state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
        )
        actual = classify(state, policy)
        self.assertEqual(
            (actual.basins, actual.terminals, [x.to_dict() for x in actual.rows]),
            expected,
        )

    def test_opposite_chiral_event_uses_actual_graph_certificate(self):
        model = self.source_model.duplicate()
        r = model.expand(request(model, -1))
        self.assertTrue(r.committed, r.reason)
        pair, center = certificate_pair(model)
        self.assertTrue(model.install_completion_certificates(*pair).committed)
        self.assertTrue(pair[0].membership(center)[0])
        self.assertNotEqual(pair[0].certificate_id, self.certificates[0].certificate_id)
        for role, c in zip(("current", "reset"), pair):
            verify_step(
                owner.kernel(model.configuration).step(
                    getattr(model.configuration, role)
                ),
                c,
                role,
            )
        self.assert_rows(center)

    def test_exact_conductance_codec_and_explicit_profile(self):
        state = self.config.current
        self.assertEqual(exact_state(state.to_payload()), state)
        p = self.config.reference.profile
        self.assertEqual(QuarticACIPCProfile.from_payload(p.to_payload()), p)
        for edit in (
            lambda v: v["W_A"].pop(),
            lambda v: v["W_A"].__setitem__(0, "0"),
            lambda v: v["W_A"].__setitem__(0, "2/2"),
            lambda v: v["W_A"].__setitem__(0, 1.0),
            lambda v: v.update(extra=0),
        ):
            bad = deepcopy(state.to_payload())
            edit(bad)
            with self.assertRaises((ValueError, TypeError)):
                exact_state(bad)
        with self.assertRaises(ValueError):
            replace(
                self.config, current=ExactResources(state.graph, state.C, state.charge)
            )
        with self.assertRaises(ValueError):
            state.advance(("0",) * 13, "32")
        with self.assertRaises(ValueError):
            state.transfer(state.graph, [])

    def test_all_conductance_directions_and_nonuniform_weighted_rows(self):
        for config in (self.config, self.event_model.configuration):
            k = owner.kernel(config)
            state = config.current
            for i in range(len(state.W_A)):
                for sign in (-1, 1):
                    weights = list(state.W_A)
                    weights[i] = str(Q(weights[i]) + sign * Q(1, 4096))
                    value = replace(state, W_A=weights)
                    payload = k.readmission(value)
                    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                        audit_read(Reference(state.graph.to_payload()), value, payload)
                    self.assert_rows(value)

    def test_certificate_rejects_omitted_or_wrong_history(self):
        payload = self.certificates[0].to_payload()
        for mutate in (
            lambda v: v["operands"]["logW_center"].pop(),
            lambda v: v["operands"]["S"].pop(),
            lambda v: v["operands"]["binding"].update(state_channels=["C"]),
            lambda v: v["proof"].update(full_step_error="0"),
            lambda v: v["operands"]["carrier_pairs"].pop(),
            lambda v: v["operands"].update(carrier_radius="1/1000"),
            lambda v: v["operands"]["carrier_center"][0].__setitem__(0, "1/1000"),
        ):
            bad = deepcopy(payload)
            mutate(bad)
            with self.assertRaises((ValueError, RuntimeError)):
                CompletionCertificate.from_payload(bad)
        with self.assertRaises(ValueError):
            self.certificates[0].membership(
                ExactResources(self.center.graph, self.center.C, "21")
            )
        for i in range(16):
            W = list(self.center.W_A)
            W[i] = str(Q(W[i]) + Q(1, 100000))
            self.assertFalse(
                self.certificates[0].membership(replace(self.center, W_A=W))[0], i
            )

    def test_actual_source_and_both_edge_histories(self):
        event = self.event_model._operation._published.completion.event
        h = event["conductance_history"]
        source = self.source_model.configuration
        self.assertEqual(h["information_loss"], "none")
        self.assertEqual(len(h["new_edge_ids"]), 3)
        for role in ("current", "reset"):
            before = getattr(source, role)
            after = getattr(self.event_model.configuration, role)
            self.assertEqual(h["source_archive"][role].to_dict(), before.to_payload())
            old = dict(zip(before.graph.live_edge_ids, before.W_A))
            self.assertEqual(
                after.W_A,
                tuple(old.get(edge, "1") for edge in after.graph.live_edge_ids),
            )
            values = dict(zip(before.graph.live_node_ids, before.C))
            new = dict(zip(after.graph.live_node_ids, map(Q, after.C)))
            for node, share in zip(event["module"], ("0", "1/128", "63/64", "1/128")):
                self.assertEqual(new[node], Q(values["v"]) * Q(share))
            with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                audit_read(
                    Reference(before.graph.to_payload()),
                    before,
                    h["fresh_source_reads"][role],
                )
        z = event["carrier_history"]
        self.assertEqual(z["information_loss"], "carrier_history_loss")
        self.assertTrue(z["target_all_dense_entries_zero"])
        for role in ("current", "reset"):
            before, after = (
                getattr(source, role),
                getattr(self.event_model.configuration, role),
            )
            self.assertEqual(z["source_archive"][role].to_dict(), before.to_payload())
            self.assertTrue(any(Q(x) != 0 for row in before.Z_4 for x in row))
            self.assertTrue(all(x == "0" for row in after.Z_4 for x in row))
        self.assertEqual(source.reset, self.config.reset)
        self.assertNotEqual(source.current.W_A, self.config.current.W_A)
        bad = request(self.source_model).to_payload()
        bad["history_policy"]["candidate"]["source_history_digest"] = (
            "grcv4-history-content-sha256:" + "0" * 64
        )
        from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput

        before = self.source_model.snapshot()
        try:
            r = self.source_model.expand(GRC9V4ExpansionRequestInput.from_payload(bad))
        except ValueError:
            r = None
        self.assertTrue(r is None or not r.committed)
        self.assertEqual(before, self.source_model.snapshot())

    def test_complete_steps_include_final_resource_writer_error(self):
        for config in (self.config, self.event_model.configuration):
            k = owner.kernel(config)
            for role in ("current", "reset"):
                state = getattr(config, role)
                for _ in range(2):
                    step = k.step(state)
                    verify_step(step)
                    state = step.after
        k = owner.kernel(self.event_model.configuration)
        step = k.step(self.center)
        report = verify_step(step, self.certificates[0])
        self.assertLessEqual(
            Q(report["full_chart_error_upper"]),
            Q(self.certificates[0].proof["full_step_error"]),
        )
        _, bound = k.coordinate_error_bounds()
        self.assertGreater(bound, Q(100, 99) * (Q(1, 2**193) + Q(1, 2**224)))

    def test_semantic_read_and_writer_substitutions_reject(self):
        k = owner.kernel(self.config)
        step = k.step(self.config.current)
        variants = []
        for stage in ("selected",):
            for name in (
                "potential",
                "baseline",
                "drive",
                "q",
                "current",
                "causal_flat",
            ):
                payload = step.consumed_read.to_dict()
                payload[stage][name][0][0] = ["0", "0"]
                variants.append(replace(step, consumed_read=FrozenJSONMap(payload)))
        payload = step.consumed_read.to_dict()
        payload["source"][0][0] = ["0", "0"]
        variants.append(replace(step, consumed_read=FrozenJSONMap(payload)))
        for key in ("exponent", "ideal", "selected_current"):
            writer = step.writer.to_dict()
            writer[key][0][0] = ["0", "0"]
            variants.append(replace(step, writer=FrozenJSONMap(writer)))
        # Rebinding the correct subject does not make a unit-W substitute true.
        other = k.step(replace(step.before, W_A=("1",) * 13)).consumed_read.to_dict()
        other["subject_digest"] = step.consumed_read["subject_digest"]
        variants.append(replace(step, consumed_read=FrozenJSONMap(other)))
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(step.before.graph.to_payload())
            C, W = arb_mat(vector(step.before.C)), arb_mat(vector(step.before.W_A))
            native = r.selected(C, W, arb_mat(matrix(step.before.Z_4)))
            J = native["selected"]["current"]
            C1 = arb_mat(vector(step.after.C))
            wrong = [
                r.log_drive(C, W, J),
                r.log_drive(C1, arb_mat(vector(step.after.W_A)), J),
                r.log_drive(C1, W, native["selected"]["baseline"]),
            ]
            for value in wrong:
                writer = step.writer.to_dict()
                writer["exponent"] = [
                    [[str(x.lower().fmpq()), str(x.upper().fmpq())]]
                    for x in value.entries()
                ]
                variants.append(replace(step, writer=FrozenJSONMap(writer)))
        for i, bad in enumerate(variants):
            with self.subTest(i=i), self.assertRaises(AssertionError):
                verify_step(bad)

    def test_failed_incoming_writer_returned_and_publication_are_atomic(self):
        for phase in ("incoming", "writer", "carrier_writer", "returned", "write"):
            model = self.synthetic_window_fixture()
            model.step()
            before = model.snapshot()
            original = SparkACIPCKernel._admitted_read
            calls = []

            def read(k, state, calls=calls, phase=phase, original=original):
                calls.append(state)
                if (phase == "incoming" and len(calls) == 1) or (
                    phase == "returned" and len(calls) == 2
                ):
                    raise ValueError("injected " + phase)
                return original(k, state)

            target = SparkACIPCKernel if phase != "write" else ExactAdaptiveCarrierState
            name = (
                "_conductance_writer"
                if phase == "writer"
                else "_carrier_writer"
                if phase == "carrier_writer"
                else "advance_histories"
                if phase == "write"
                else "_admitted_read"
            )
            replacement = (
                patch.object(target, name, side_effect=ValueError("injected"))
                if phase in ("writer", "carrier_writer", "write")
                else patch.object(target, name, new=read)
            )
            with replacement:
                result = model.step()
            self.assertFalse(result.committed)
            self.assertEqual(model.snapshot(), before)
            self.assertTrue(model.step().committed)

    def test_failure_after_numerics_and_window_preparation_is_atomic(self):
        for name in ("prepare", "progress"):
            model = self.synthetic_window_fixture()
            model.step()
            model.step()
            before = model.snapshot()
            original = getattr(owner, name)

            def failure(*args, original=original, name=name, **kwargs):
                original(*args, **kwargs)
                raise ValueError("failed after " + name)

            with patch.object(owner, name, new=failure):
                result = model.step()
            self.assertFalse(result.committed)
            self.assertEqual(model.snapshot(), before)
            self.assertEqual(model.step().local_gain, 1)

    def test_cache_reuse_changed_operands_and_policy_guards(self):
        k = owner.kernel(self.config)
        before = k.cache_info()
        owner.kernel(self.config)
        self.assertGreater(k.cache_info()["graph"]["hits"], before["graph"]["hits"])
        one = k.step(self.config.current)
        two = k.step(one.after)
        self.assertNotEqual(
            one.consumed_read["subject_digest"], two.consumed_read["subject_digest"]
        )
        self.assertGreater(k.cache_info()["decay"]["hits"], 0)
        for change in ({"tau_A": 16}, {"alpha": 0}, {"kappa_Ah": 0}):
            with self.assertRaises(ValueError):
                owner.quartic_kernel(
                    self.config.reference.graph,
                    profile(self.config.reference.graph, candidate=change),
                )
        for value in ("99/100", "101/100", "1/2"):
            with self.assertRaises(RuntimeError):
                k.readmission(replace(self.config.current, W_A=(value,) * 13))
        self.assertEqual(
            self.event_model.support_status()["execution_families"], ["A_CI_PC"]
        )
        self.assertFalse(self.event_model.support_status()["native_endpoint_verified"])

    def test_checkpoint_hash_once_and_identical_warm_cold_accounting(self):
        model = GRC9V4(self.config)
        for _ in range(6):
            self.assertTrue(model.step().committed)
        snapshot = model.snapshot()
        calls = []
        digest = owner.digest

        def counted(value):
            if value == snapshot["owner"]["publication"]:
                calls.append(True)
            return digest(value)

        with patch.object(owner, "digest", counted):
            warm = GRC9V4.from_state(snapshot)
        self.assertEqual(len(calls), 1)
        self.assertEqual(warm.snapshot(), snapshot)
        with patch.object(owner, "_SCOPES", {}):
            cold = GRC9V4.from_state(snapshot)
            self.assertEqual(cold.snapshot(), snapshot)
        self.assertTrue(warm.step().committed)
        self.assertEqual(model.snapshot(), snapshot)

    def test_all_signed_carrier_coordinates_and_partial_writes_reject(self):
        for config in (self.config, self.event_model.configuration):
            k = owner.kernel(config)
            for i, j in k.pairs:
                for sign in (-1, 1):
                    z = [list(row) for row in config.current.Z_4]
                    z[i][j] = z[j][i] = str(Q(z[i][j]) + sign * Q(1, 65536))
                    value = replace(config.current, Z_4=z)
                    payload = k.readmission(value)
                    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                        audit_read(Reference(value.graph.to_payload()), value, payload)
            with self.assertRaises(ValueError):
                config.current.advance_conductance(
                    ("0",) * len(config.current.W_A), "32", config.current.W_A
                )
            with self.assertRaises(ValueError):
                config.current.advance_carrier(
                    ("0",) * len(config.current.W_A), "32", config.current.Z_4
                )
        raw = self.config.current.to_payload()
        for change in (
            lambda v: v.pop("Z_4"),
            lambda v: v["Z_4"].pop(),
            lambda v: v["Z_4"][0].__setitem__(1, "1/65536"),
            lambda v: v["Z_4"][0].__setitem__(0, "1"),
            lambda v: v["Z_4"][0].__setitem__(0, 0.0),
        ):
            bad = deepcopy(raw)
            change(bad)
            with self.assertRaises((ValueError, TypeError)):
                exact_state(bad)

    def test_two_fresh_reads_two_same_read_writers_one_atomic_publication(self):
        k = owner.kernel(self.config)
        read = SparkACIPCKernel._admitted_read
        wwrite = SparkACIPCKernel._conductance_writer
        zwrite = SparkACIPCKernel._carrier_writer
        commit = ExactAdaptiveCarrierState.advance_histories
        reads = []
        writers = []
        writes = []
        selected = []

        def rs(k, state):
            reads.append(state)
            v = read(k, state)
            selected.append(v)
            return v

        def ws(k, state, after, value):
            writers.append(value)
            return wwrite(k, state, after, value)

        def zs(k, state, value):
            writers.append(value)
            return zwrite(k, state, value)

        def cs(state, *args):
            writes.append(state)
            return commit(state, *args)

        with (
            patch.object(SparkACIPCKernel, "_admitted_read", rs),
            patch.object(SparkACIPCKernel, "_conductance_writer", ws),
            patch.object(SparkACIPCKernel, "_carrier_writer", zs),
            patch.object(ExactAdaptiveCarrierState, "advance_histories", cs),
        ):
            step = k.step(self.config.current)
        self.assertEqual(reads, [step.before, step.after])
        self.assertEqual(writes, [step.before])
        self.assertEqual(len(writers), 2)
        self.assertIs(writers[0], selected[0])
        self.assertIs(writers[1], selected[0])

    def test_wrong_carrier_source_rebound_geometry_and_writer_reject(self):
        k = owner.kernel(self.config)
        step = k.step(self.config.current)
        wrongs = []
        for key in ("source", "ideal", "midpoint"):
            writer = step.carrier_writer.to_dict()
            writer[key][0][0] = "0" if key == "midpoint" else ["0", "0"]
            wrongs.append(replace(step, carrier_writer=FrozenJSONMap(writer)))
        zero = replace(step.before, Z_4=tuple(("0",) * 13 for _ in range(13)))
        payload = k.readmission(zero).to_dict()
        payload["subject_digest"] = step.consumed_read["subject_digest"]
        wrongs.append(replace(step, consumed_read=FrozenJSONMap(payload)))
        for bad in wrongs:
            with self.assertRaises(AssertionError):
                verify_step(bad)

    def _finite_directions(self, nonstationary=False):
        graph = self.center.graph
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            m = ACIPCMath(graph)
            r = Reference(graph.to_payload())
            n, e = m.n, m.m
            nx = n + e
            cert = self.certificates[0]
            S = matrix(cert.operands["S"])
            C = arb_mat(vector(cert.operands["center"]))
            L = arb_mat(vector(cert.operands["logW_center"]))
            Z = arb_mat(e, e)
            if nonstationary:
                C = arb_mat([[Q(5, 4) + Q((i * 7) % 11, 32)] for i in range(n)])
                L = arb_mat(
                    [[arb(1 + Q((i * 5) % 13 - 6, 2048)).log()] for i in range(e)]
                )
                for k, (i, j) in enumerate(m.carrier_pairs):
                    Z[i, j] = Z[j, i] = Q((-1) ** k * (k + 1), 2**24)
            eps = Q(1, 2**100)
            for axis in range(S.ncols() + len(m.carrier_pairs)):
                dc, dl, dz = arb_mat(n, 1), arb_mat(e, 1), arb_mat(e, e)
                direction = arb_mat(nx + len(m.carrier_pairs), 1)
                if axis < S.ncols():
                    for i in range(nx):
                        direction[i, 0] = S[i, axis]
                    dc = arb_mat(direction.tolist()[:n])
                    dl = arb_mat(direction.tolist()[n:nx])
                else:
                    k = axis - S.ncols()
                    i, j = m.carrier_pairs[k]
                    dz[i, j] = dz[j, i] = 1 if i == j else 1 / arb(2).sqrt()
                    direction[nx + k, 0] = 1
                cbox = arb_mat(
                    [
                        [C[i, 0] + arb(0, abs(dc[i, 0]).upper().fmpq() * eps)]
                        for i in range(n)
                    ]
                )
                lbox = arb_mat(
                    [
                        [L[i, 0] + arb(0, abs(dl[i, 0]).upper().fmpq() * eps)]
                        for i in range(e)
                    ]
                )
                zbox = arb_mat(
                    [
                        [
                            Z[i, j] + arb(0, abs(dz[i, j]).upper().fmpq() * eps)
                            for j in range(e)
                        ]
                        for i in range(e)
                    ]
                )
                derivative = m.jacobian(cbox, lbox, zbox) * direction
                secant = (
                    r.map(C + eps * dc, L + eps * dl, Z + eps * dz)
                    - r.map(C - eps * dc, L - eps * dl, Z - eps * dz)
                ) / (2 * eps)
                for i in range(derivative.nrows()):
                    # A structural zero derivative and a rounded independent
                    # secant can both enclose zero without strict containment.
                    a, b = derivative[i, 0], secant[i, 0]
                    self.assertTrue(
                        a.contains(b) or (a.is_zero() and b.contains(0)),
                        (nonstationary, axis, i),
                    )
            self.assertEqual(S.ncols() + len(m.carrier_pairs), 76)

    def test_independent_full_jacobian_at_exact_center(self):
        self._finite_directions()

    def test_nonstationary_all_76_physical_directions(self):
        self._finite_directions(True)

    def test_all_flat_root_directions_include_both_geometry_consumers(self):
        graph = self.center.graph
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            m, r = ACIPCMath(graph), Reference(graph.to_payload())
            C = arb_mat([[Q(5, 4) + Q((i * 7) % 11, 32)] for i in range(m.n)])
            W = arb_mat([[1 + Q((i * 5) % 13 - 6, 2048)] for i in range(m.m)])
            Z = arb_mat(m.m, m.m)
            for k, (i, j) in enumerate(m.carrier_pairs):
                Z[i, j] = Z[j, i] = Q((-1) ** k * (k + 1), 2**24)
            flat = arb_mat([[Q((-1) ** i * (i + 1), 4096)] for i in range(m.m)])
            eps = Q(1, 2**100)
            for axis in range(m.m):
                direction = arb_mat([[int(i == axis)] for i in range(m.m)])
                box = arb_mat(
                    [[flat[i, 0] + arb(0, eps if i == axis else 0)] for i in range(m.m)]
                )
                _, _, Ff, Jf = m.flat_partials(C, W, Z, box)
                plus = r.read(C, W, r.composite_geometry(flat + eps * direction, Z))
                minus = r.read(C, W, r.composite_geometry(flat - eps * direction, Z))
                for key, derivative in (("causal_flat", Ff), ("current", Jf)):
                    secant = (plus[key] - minus[key]) / (2 * eps)
                    for i in range(m.m):
                        a, b = derivative[i, axis], secant[i, 0]
                        self.assertTrue(
                            a.contains(b) or (a.is_zero() and b.contains(0)),
                            (key, axis, i),
                        )

    def test_composite_cannot_drop_incoming_carrier_or_immediate_source(self):
        state = self.config.current
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C, W, Z = (
                arb_mat(vector(state.C)),
                arb_mat(vector(state.W_A)),
                arb_mat(matrix(state.Z_4)),
            )
            actual = r.selected(C, W, Z)
            for drop in ("carrier", "immediate"):

                def geometry(flat, z, drop=drop):
                    return (
                        r.I
                        + (
                            (z if drop != "carrier" else arb_mat(r.m, r.m))
                            + (
                                r.source(flat)
                                if drop != "immediate"
                                else arb_mat(r.m, r.m)
                            )
                        )
                        / 2
                    )

                with patch.object(r, "composite_geometry", geometry):
                    other = r.selected(C, W, Z)
                for key in ("current", "causal_flat"):
                    lower = max(
                        abs(x).lower().fmpq()
                        for x in (
                            actual["selected"][key] - other["selected"][key]
                        ).entries()
                    )
                    self.assertGreater(lower, 0, (drop, key))

    def test_root_witness_and_composite_policy_mutations_reject(self):
        k = owner.kernel(self.config)
        step = k.step(self.config.current)
        for mutate in (
            lambda v: v["domain"].update(contraction="0"),
            lambda v: v["domain"].update(carrier_radius="1/128"),
            lambda v: v["domain"].update(stationary_composite_gain=1),
            lambda v: v.update(root_error=["0", "0"]),
            lambda v: v.update(proposal_residual=["0", "0"]),
            lambda v: v.update(joint_residual_upper="0"),
            lambda v: v["proposal"][0].__setitem__(0, ["0", "0"]),
        ):
            value = step.consumed_read.to_dict()
            mutate(value)
            with self.assertRaises((ValueError, AssertionError)):
                verify_step(replace(step, consumed_read=FrozenJSONMap(value)))
        for updates in (
            {"rho_inst": 0},
            {"contraction_domain_id": "wrong"},
            {"radius": 1 / 128},
            {"tau_PC": 16},
            {"tolerance": 1e-9},
        ):
            with self.assertRaises(ValueError):
                owner.quartic_kernel(
                    self.config.reference.graph,
                    profile(self.config.reference.graph, realization=updates),
                )
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            C, W, Z = (
                arb_mat(vector(step.before.C)),
                arb_mat(vector(step.before.W_A)),
                arb_mat(matrix(step.before.Z_4)),
            )
            L = arb_mat([[x.log()] for x in W.entries()])
            math = ACIPCMath(step.before.graph)
            root = math.root(C, L, Z, W)
            with self.assertRaises(RuntimeError):
                math.jacobian(C, L, arb_mat(Z), root)
            with self.assertRaises(RuntimeError):
                math.advance(C, L, arb_mat(Z), root)

    def test_actual_root_iteration_exhaustion_rolls_back_without_fallback(self):
        model = GRC9V4(self.config)
        snapshot = model.snapshot()
        published = model._operation._spark_scope.published
        original = ACIPCMath.root
        precisions = []

        def limited(math, C, L, Z, W=None, limit=60):
            precisions.append(ctx.prec)
            return original(math, C, L, Z, W, limit=1)

        with patch.object(ACIPCMath, "root", limited):
            result = model.step()
        self.assertFalse(result.committed)
        self.assertEqual(precisions, [256])
        self.assertEqual(model.snapshot(), snapshot)
        self.assertIs(model._operation._spark_scope.published, published)
        self.assertTrue(model.step().committed)
