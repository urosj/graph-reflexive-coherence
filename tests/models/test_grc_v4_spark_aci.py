"""Bounded A_CI full-state mathematics, event history and atomic lifecycle."""

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
from pygrc.models.grc_v4_spark_aci import SparkACIKernel
from pygrc.models.grc_v4_spark_aci_math import ACIMath
from pygrc.models.grc_v4_spark_carrier import exact_state
from pygrc.models.grc_v4_spark_conductance import (
    ExactConductanceState,
    QuarticACIProfile,
)
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from aci_native_spark_oracle import Reference, audit_read, verify_step
from aci_native_spark_oracle import classify as independent_classify
from cos_native_spark_oracle import matrix, vector
from p991a6_aci_subjects import certificate_pair, configuration, profile, request


class NativeACITests(shared.NativeSparkCompletionTests):
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

    def test_independent_full_jacobian_at_exact_center(self):
        """Independent finite differences enclosed in every full tangent column."""
        c = self.certificates[0]
        S = matrix(c.operands["S"])
        U = matrix(c.operands["U"])
        n = len(self.center.C)
        d = S.ncols()
        eps = Q(1, 4096)
        values = list(c.operands["center"]) + list(c.operands["logW_center"])
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            point = arb_mat(vector(values))
            ref = Reference(self.center.graph.to_payload())
            math = ACIMath(self.center.graph)
            # Each segment has its own complete derivative enclosure. Both
            # resource and conductance output coordinates must agree.
            for axis in range(d):
                direction = arb_mat([[S[i, axis]] for i in range(S.nrows())])
                box = arb_mat(
                    [
                        [arb(Q(values[i]), abs(S[i, axis]) * eps)]
                        for i in range(S.nrows())
                    ]
                )
                J = math.jacobian(arb_mat(box.tolist()[:n]), arb_mat(box.tolist()[n:]))
                enclosed = arb_mat(U) * J * direction
                p = point + eps * direction
                m = point - eps * direction
                difference = (
                    arb_mat(U)
                    * (
                        ref.map(arb_mat(p.tolist()[:n]), arb_mat(p.tolist()[n:]))
                        - ref.map(arb_mat(m.tolist()[:n]), arb_mat(m.tolist()[n:]))
                    )
                    / (2 * eps)
                )
                self.assertTrue(
                    all(
                        a.contains(b)
                        for a, b in zip(enclosed.entries(), difference.entries())
                    ),
                    axis,
                )
            pointJ = math.jacobian(
                arb_mat(point.tolist()[:n]), arb_mat(point.tolist()[n:])
            )
            self.assertTrue(
                any(
                    not pointJ[i, j].contains(0)
                    for i in range(n)
                    for j in range(n, n + 16)
                )
            )
            self.assertTrue(
                any(
                    not pointJ[i, j].contains(0)
                    for i in range(n, n + 16)
                    for j in range(n)
                )
            )
        self.assertEqual(d, 30)

    def test_full_domain_mathematics_and_exact_membership(self):
        c = self.certificates[0]
        self.assertTrue(c.membership(self.center)[0])
        self.assertFalse(c.membership(self.event_model.configuration.current)[0])
        self.assertLess(Q(c.proof["q"]), 1)
        self.assertLess(Q(c.proof["full_step_error"]), Q(c.proof["image_margin"]))
        self.assertEqual(c.proof["relative_dimension"], 30)
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
        self.assertEqual(QuarticACIProfile.from_payload(p.to_payload()), p)
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
        payload["flat"][0][0] = ["0", "0"]
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
            native = r.selected(C, W)
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

    def test_exactly_two_full_reads_one_writer_one_atomic_write(self):
        k = owner.kernel(self.config)
        read = SparkACIKernel._admitted_read
        write = SparkACIKernel._writer
        commit = ExactConductanceState.advance_conductance
        reads = []
        writers = []
        writes = []

        def rs(k, state):
            reads.append(state)
            return read(k, state)

        def ws(k, state, after, value):
            writers.append(value)
            return write(k, state, after, value)

        def cs(state, *args):
            writes.append(state)
            return commit(state, *args)

        with (
            patch.object(SparkACIKernel, "_admitted_read", rs),
            patch.object(SparkACIKernel, "_writer", ws),
            patch.object(ExactConductanceState, "advance_conductance", cs),
        ):
            step = k.step(self.config.current)
        self.assertEqual(reads, [step.before, step.after])
        self.assertEqual(writes, [step.before])
        self.assertEqual(len(writers), 1)
        self.assertEqual(
            writers[0]["subject_digest"], step.consumed_read["subject_digest"]
        )

    def test_failed_incoming_writer_returned_and_publication_are_atomic(self):
        for phase in ("incoming", "writer", "returned", "write"):
            model = self.synthetic_window_fixture()
            model.step()
            before = model.snapshot()
            original = SparkACIKernel._admitted_read
            calls = []

            def read(k, state, calls=calls, phase=phase, original=original):
                calls.append(state)
                if (phase == "incoming" and len(calls) == 1) or (
                    phase == "returned" and len(calls) == 2
                ):
                    raise ValueError("injected " + phase)
                return original(k, state)

            target = SparkACIKernel if phase != "write" else ExactConductanceState
            name = (
                "_writer"
                if phase == "writer"
                else "advance_conductance"
                if phase == "write"
                else "_admitted_read"
            )
            replacement = (
                patch.object(target, name, side_effect=ValueError("injected"))
                if phase in ("writer", "write")
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
            self.event_model.support_status()["execution_families"], ["A_CI"]
        )
        self.assertFalse(self.event_model.support_status()["current_occurrence_completed"])
        self.assertFalse(self.event_model.support_status()["universal_entry_guarantee"])

    def test_nonstationary_full_map_and_root_coordinate_derivatives(self):
        """Every physical and flat axis at a heterogeneous, nonstationary state."""
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            graph = self.event_model.configuration.current.graph
            m = ACIMath(graph)
            r = Reference(graph.to_payload())
            n, e = m.n, m.m
            C = arb_mat([[Q(5, 4) + Q((i * 7) % 11, 32)] for i in range(n)])
            W = arb_mat([[1 + Q((i * 5) % 13 - 6, 2048)] for i in range(e)])
            L = arb_mat([[w.log()] for w in W.entries()])
            eps = Q(1, 2**100)
            x = arb_mat(C.tolist() + L.tolist())
            for k in range(n + e):
                box = arb_mat(
                    [
                        [arb(x[i, 0].mid().fmpq(), eps) if i == k else x[i, 0]]
                        for i in range(n + e)
                    ]
                )
                J = m.jacobian(arb_mat(box.tolist()[:n]), arb_mat(box.tolist()[n:]))
                plus = arb_mat(x)
                minus = arb_mat(x)
                plus[k, 0] += eps
                minus[k, 0] -= eps
                fd = (
                    r.map(arb_mat(plus.tolist()[:n]), arb_mat(plus.tolist()[n:]))
                    - r.map(arb_mat(minus.tolist()[:n]), arb_mat(minus.tolist()[n:]))
                ) / (2 * eps)
                self.assertTrue(
                    all(J[i, k].contains(fd[i, 0]) for i in range(n + e)), k
                )
            f = arb_mat([[Q(i + 1, 16384)] for i in range(e)])
            for k in range(e):
                box = arb_mat(f)
                box[k, 0] = arb(f[k, 0].fmpq(), eps)
                _, _, Ff, Jf = m.flat_partials(C, W, box)
                plus = arb_mat(f)
                minus = arb_mat(f)
                plus[k, 0] += eps
                minus[k, 0] -= eps
                a = r.read(C, W, r.geometry(plus))
                b = r.read(C, W, r.geometry(minus))
                for field, derivative in (("causal_flat", Ff), ("current", Jf)):
                    fd = (a[field] - b[field]) / (2 * eps)
                    self.assertTrue(
                        all(
                            derivative[i, k].overlaps(fd[i, 0])
                            and fd[i, 0].rad() < arb(2) ** -500
                            for i in range(e)
                        ),
                        (field, k),
                    )

    def test_selected_root_rejects_os_substitute_and_inadequate_solver(self):
        from aos_native_spark_oracle import Reference as OSReference

        from pygrc.models.grc_v4_spark_cpc import intervals

        k = owner.kernel(self.config)
        state = self.config.current
        payload = k.readmission(state).to_dict()
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            os = OSReference(state.graph.to_payload()).selected(C, W)
            payload["selected"] = {
                key: intervals(value) for key, value in os["corrector"].items()
            }
            payload["H"] = intervals(os["H"])
            with self.assertRaises(AssertionError):
                audit_read(Reference(state.graph.to_payload()), state, payload)
        # Explicit proposal exhaustion fails without an OS or precision fallback.
        short = SparkACIKernel(
            state.graph,
            profile(
                state.graph,
                realization={"iteration_limit": 1},
                solver={"iteration_limit": 1},
            ),
        )
        with self.assertRaisesRegex(RuntimeError, "iteration limit"):
            short.readmission(state)
        for field in ("root_error", "proposal_residual"):
            bad = k.readmission(state).to_dict()
            bad[field] = ["0", "0"]
            with (
                _ARB_CONTEXT_LOCK,
                ctx.workprec(768),
                self.assertRaises(AssertionError),
            ):
                audit_read(Reference(state.graph.to_payload()), state, bad)

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
