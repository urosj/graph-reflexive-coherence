"""Native full C/Z numerics and bounded lifecycle; no source-to-entry campaign."""

import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_codec import CompletionPolicy
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_spark_carrier import (
    ExactCarrierState,
    carrier_pairs,
    exact_state,
)
from pygrc.models.grc_v4_spark_ccipc import SparkCCIPCKernel, intervals
from pygrc.models.grc_v4_spark_state import ExactResources, QuarticCCIPCProfile
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from ccipc_native_spark_oracle import (
    CCIPCReference,
    encloses,
    exact_matrix,
    verify_step,
)
from ccipc_native_spark_pressure_oracle import audit_root, audit_step
from cos_native_spark_oracle import matrix, vector
from p991a6_ccipc_subjects import certificate_pair, configuration, profile, request


class NativeCCIPCTests(shared.NativeSparkCompletionTests):
    @classmethod
    def setUpClass(cls):
        cls.config = configuration()
        cls.source_model = GRC9V4(cls.config)
        result = cls.source_model.step()
        assert result.committed, result.reason
        cls.event_model = cls.source_model.duplicate()
        result = cls.event_model.expand(request(cls.event_model))
        assert result.committed, result.reason
        cls.certificates, cls.center = certificate_pair(cls.event_model)

    def test_independent_full_jacobian_at_exact_center(self):

        k = owner.kernel(self.event_model.configuration)
        m = len(self.center.Z_4)
        Z = exact_matrix(self.center.Z_4)
        Z[0, 0] = Q(1, 10**10)
        i, j = next(p for p in k.pairs if p[0] != p[1])
        Z[i, j] = Z[j, i] = Q(-1, 10**11)
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            C = arb_mat([[Q(x)] for x in self.center.C])
            actual = k.partials(C, arb_mat(Z))
            saved = {name: intervals(actual[name]) for name in ("CC", "CZ", "SC", "SZ")}
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            ref = CCIPCReference(self.center.graph.to_payload())
            expected = ref.partials(
                arb_mat([[Q(x)] for x in self.center.C]), arb_mat(Z)
            )
            for name, value in saved.items():
                self.assertTrue(encloses(value, expected[name]), name)
        self.assertEqual(actual["CZ"].ncols(), 46)
        self.assertEqual(actual["SZ"].ncols(), 46)
        self.assertTrue(any(not x.contains(0) for x in actual["CZ"].entries()))
        self.assertEqual(m, 16)

    def test_certificate_tampering_full_coordinates_and_bindings(self):
        payload = self.certificates[0].to_payload()
        changes = [
            lambda x: x["proof"].update(q="0"),
            lambda x: x["operands"]["S"].pop(),
            lambda x: x["operands"]["U"][0].__setitem__(0, "0"),
            lambda x: x["operands"]["binding"].update(state_channels=["C"]),
            lambda x: x["operands"]["binding"].update(charge="22"),
            lambda x: x["operands"].update(carrier_radius="0"),
            lambda x: x["operands"]["carrier_pairs"].pop(),
            lambda x: x["operands"]["carrier_center"][0].__setitem__(0, "1/1024"),
        ]
        for change in changes:
            data = deepcopy(payload)
            change(data)
            with self.assertRaises((ValueError, RuntimeError, IndexError)):
                CompletionCertificate.from_payload(data)
        with self.assertRaises(ValueError):
            self.certificates[0].membership(
                ExactResources(self.center.graph, self.center.C, "21")
            )
        self.assertEqual(self.certificates[0].proof["full_dimension"], 60)
        self.assertTrue(self.certificates[0].proof["all_signed_carrier_directions"])

    def test_opposite_chiral_event_uses_actual_graph_certificate(self):
        model = self.source_model.duplicate()
        result = model.expand(request(model, -1))
        self.assertTrue(result.committed, result.reason)
        pair, center = certificate_pair(model)
        self.assertTrue(model.install_completion_certificates(*pair).committed)
        self.assertTrue(pair[0].membership(center)[0])
        self.assertNotEqual(pair[0].certificate_id, self.certificates[0].certificate_id)
        for i, role in enumerate(("current", "reset")):
            step = owner.kernel(model.configuration).step(
                getattr(model.configuration, role)
            )
            verify_step(step, pair[i], role)

    def test_exact_carrier_codec_signed_support_and_no_silent_resource_conversion(self):
        state = self.config.current
        self.assertEqual(exact_state(state.to_payload()), state)
        self.assertEqual(
            QuarticCCIPCProfile.from_payload(
                self.config.reference.profile.to_payload()
            ),
            self.config.reference.profile,
        )
        data = state.to_payload()
        for mutate in (
            lambda x: x["Z_4"].pop(),
            lambda x: x["Z_4"][0].__setitem__(1, "1/1024"),
            lambda x: x["Z_4"][0].__setitem__(0, "1"),
            lambda x: x["Z_4"][0].__setitem__(0, 0.5),
        ):
            bad = deepcopy(data)
            mutate(bad)
            with self.assertRaises((ValueError, TypeError)):
                exact_state(bad)
        support = set(carrier_pairs(state.graph))
        i, j = next(
            (i, j)
            for i in range(len(state.Z_4))
            for j in range(i + 1, len(state.Z_4))
            if (i, j) not in support
        )
        bad = deepcopy(data)
        bad["Z_4"][i][j] = bad["Z_4"][j][i] = "1/1024"
        with self.assertRaises(ValueError):
            exact_state(bad)
        self.assertLess(Q(self.config.reset.Z_4[0][0]), 0)
        with self.assertRaises(ValueError):
            replace(
                self.config, current=ExactResources(state.graph, state.C, state.charge)
            )
        with self.assertRaises(ValueError):
            state.advance(tuple("0" for _ in state.graph.live_edge_ids), "32")

    def test_old_carrier_same_read_writer_and_complete_independent_steps(self):
        source = owner.kernel(self.config).step(self.config.current)
        verify_step(source)
        model = self.event_model.configuration
        k = owner.kernel(model)
        for i, role in enumerate(("current", "reset")):
            state = getattr(model, role)
            for _ in range(3):
                step = k.step(state)
                verify_step(step, self.certificates[i], role)
                state = step.after
        zero = ExactCarrierState.zero(self.config.current)
        other = owner.kernel(self.config).step(zero)
        self.assertNotEqual(source.flux, other.flux)
        self.assertNotEqual(source.after.Z_4, other.after.Z_4)
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            k = owner.kernel(self.config)
            read = k._admitted_read(self.config.current)
            with self.assertRaises(RuntimeError):
                k._writer(self.config.reset, read)

    def test_source_event_archives_both_nonzero_histories_and_zeros_whole_target(self):
        event = self.event_model._operation._published.completion.event
        h = event["carrier_history"]
        self.assertFalse(h["native_release"])
        self.assertEqual(h["policy_id"], "event_loss_and_zero_target_carrier_v1")
        for role in ("current", "reset"):
            before = getattr(self.source_model.configuration, role)
            after = getattr(self.event_model.configuration, role)
            self.assertEqual(h["source_archive"][role].to_dict(), before.to_payload())
            self.assertTrue(any(Q(x) != 0 for row in before.Z_4 for x in row))
            self.assertTrue(all(Q(x) == 0 for row in after.Z_4 for x in row))
            self.assertEqual(
                h["fresh_source_reads"][role].to_dict(),
                owner.kernel(self.source_model.configuration)
                .readmission(before)
                .to_dict(),
            )
        self.assertEqual(self.source_model.configuration.reset, self.config.reset)
        self.assertEqual(len(h["target_carrier_pairs"]), 46)
        old = self.source_model.snapshot()
        bad = request(self.source_model).to_payload()
        bad["history_policy"]["carrier"]["source_history_digest"] = (
            "grcv4-history-content-sha256:" + "0" * 64
        )
        from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput

        self.assertFalse(
            self.source_model.expand(
                GRC9V4ExpansionRequestInput.from_payload(bad)
            ).committed
        )
        self.assertEqual(self.source_model.snapshot(), old)
        self.assertFalse(
            self.source_model.expand(shared.request(self.source_model)).committed
        )

    def test_full_carrier_membership_includes_every_signed_direction(self):
        radius = Q(self.certificates[0].operands["carrier_radius"])
        for i, j in carrier_pairs(self.center.graph):
            for sign in (-1, 1):
                z = [list(row) for row in self.center.Z_4]
                z[i][j] = z[j][i] = str(sign * radius / 4)
                point = replace(self.center, Z_4=z)
                inside, squared = self.certificates[0].membership(point)
                self.assertTrue(inside)
                self.assertGreater(Q(squared), 0)
        z = [list(row) for row in self.center.Z_4]
        z[0][0] = str(2 * radius)
        self.assertFalse(
            self.certificates[0].membership(replace(self.center, Z_4=z))[0]
        )

    def test_fresh_reads_writer_and_postwrite_failures_are_atomic(self):
        for phase in ("incoming", "writer", "after_write", "poststate"):
            model = self.event_model.duplicate()
            before = model.snapshot()
            root = model._operation._spark_scope.published
            if phase == "writer":
                target, attribute = SparkCCIPCKernel, "_writer"
                original = getattr(target, attribute)
            elif phase == "after_write":
                target, attribute = ExactCarrierState, "advance_carrier"
                original = getattr(target, attribute)
            else:
                target, attribute = SparkCCIPCKernel, "_admitted_read"
                original = getattr(target, attribute)
            calls = []

            def fail(*args, phase=phase, original=original, calls=calls, **kwargs):
                calls.append(1)
                if phase == "poststate" and len(calls) == 1:
                    return original(*args, **kwargs)
                if phase == "after_write":
                    original(*args, **kwargs)
                raise ValueError("injected " + phase)

            with patch.object(target, attribute, fail):
                result = model.step()
            self.assertFalse(result.committed, phase)
            self.assertEqual(model.snapshot(), before)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertTrue(model.step().committed)

    def test_policy_binding_and_explicit_profile_migration(self):
        with self.assertRaises(ValueError):
            replace(
                self.config,
                specialization=self.config.specialization.with_completion_policy(
                    CompletionPolicy()
                ),
            )
        with self.assertRaises(ValueError):
            owner.quartic_kernel(
                self.config.reference.graph,
                profile(self.config.reference.graph, realization={"tau_PC": 16}),
            )
        model = self.event_model.duplicate()
        config = model.configuration
        z = [list(row) for row in config.current.Z_4]
        z[0][0] = "1/1024"
        changed = replace(config, current=replace(config.current, Z_4=z))
        before = model.snapshot()
        self.assertFalse(model.migrate_spark_configuration(changed).committed)
        self.assertEqual(model.snapshot(), before)
        self.assertFalse(model.support_status()["native_endpoint_verified"])
        self.assertEqual(model.support_status()["execution_families"], ["C_CI_PC"])

    def test_graph_and_decay_cache_reuse_never_reuses_changing_reads(self):
        k = owner.kernel(self.event_model.configuration)
        before = k.domain_cache_info()
        owner.kernel(self.event_model.configuration)
        after = k.domain_cache_info()
        self.assertGreater(after["hits"], before["hits"])
        first = k.step(self.event_model.configuration.current)
        second = k.step(first.after)
        self.assertNotEqual(
            first.consumed_read["subject_digest"],
            second.consumed_read["subject_digest"],
        )
        self.assertNotEqual(first.writer, second.writer)
        self.assertGreater(k.decay_cache_info()["hits"], 0)
        source = owner.kernel(self.config)
        self.assertNotEqual(source.domain, k.domain)

    def test_composite_root_provenance_and_mutation_discriminators(self):
        k = owner.kernel(self.config)
        step = k.step(self.config.current)
        audit_step(step)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            variants = []
            for name in ("H", "J", "flat", "S"):
                p = step.consumed_read.to_dict()
                p[name][0][0] = ["0", "0"]
                variants.append((name, p))
            for name, value in (
                ("root_error", ["0", "0"]),
                ("proposal_residual", ["0", "0"]),
                ("residual_upper", "0"),
                ("conditioning_upper", "1"),
                ("subject_digest", "0" * 64),
            ):
                p = step.consumed_read.to_dict()
                p[name] = value
                variants.append((name, p))
            p = step.consumed_read.to_dict()
            p["root_domain"]["contraction"] = "0"
            variants.append(("domain", p))
            for name, p in variants:
                with self.assertRaises(AssertionError, msg=name):
                    if name == "S":
                        from pygrc.models.grc_v4_state import FrozenJSONMap

                        verify_step(replace(step, consumed_read=FrozenJSONMap(p)))
                    else:
                        audit_root(step.before, p)

    def test_every_signed_source_and_target_direction_admits_composite_root(self):
        for state in (self.config.current, self.event_model.configuration.current):
            k = owner.kernel(
                replace(
                    self.config
                    if state.graph == self.config.reference.graph
                    else self.event_model.configuration,
                    current=state,
                )
            )
            for i, j in k.pairs:
                for sign in (-1, 1):
                    z = [["0"] * len(state.Z_4) for _ in state.Z_4]
                    z[i][j] = z[j][i] = str(sign * Q(1, 1024))
                    point = replace(state, Z_4=z)
                    p = k.readmission(point)
                    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                        audit_root(point, p)

    def test_composite_domain_boundary_and_profile_mutations(self):
        k = owner.kernel(self.config)
        z = [["0"] * len(self.config.current.Z_4) for _ in self.config.current.Z_4]
        z[0][0] = "-1/128"
        state = replace(self.config.current, Z_4=z)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            audit_root(state, k.readmission(state))
        z[0][0] = "-65/8192"
        with self.assertRaises(RuntimeError):
            k.readmission(replace(state, Z_4=z))
        for change in (
            {"rho_inst": 2},
            {"radius": 1 / 64},
            {"tau_PC": 16},
            {"iteration_limit": 1},
            {"contraction_domain_id": "ci_quartic_flat_inf_ball_1_over_32_v1"},
        ):
            with self.assertRaises((ValueError, RuntimeError)):
                owner.quartic_kernel(
                    self.config.reference.graph,
                    profile(self.config.reference.graph, realization=change),
                ).step(self.config.current)

    def test_zero_carrier_is_CI_and_nonzero_carrier_is_not_PC(self):
        from p991a6_cci_subjects import profile as ci_profile
        from p991a6_cpc_subjects import profile as pc_profile

        from pygrc.models.grc_v4_spark_cci import SparkCCIKernel
        from pygrc.models.grc_v4_spark_cpc import SparkCPCKernel
        from pygrc.models.grc_v4_state import FrozenJSONMap

        k = owner.kernel(self.config)
        zero = ExactCarrierState.zero(self.config.current)
        actual = k.step(zero)
        ci = SparkCCIKernel(zero.graph, ci_profile(zero.graph)).step(
            ExactResources(zero.graph, zero.C, zero.charge)
        )
        self.assertEqual(actual.flux, ci.flux)
        self.assertEqual(actual.after.C, ci.after.C)
        good = k.step(self.config.current)
        pc = SparkCPCKernel(zero.graph, pc_profile(zero.graph)).step(
            self.config.current
        )
        self.assertNotEqual(good.flux, pc.flux)
        self.assertNotEqual(good.after.Z_4, pc.after.Z_4)
        for bad_read in (pc.consumed_read, actual.consumed_read):
            p = bad_read.to_dict()
            p["subject_digest"] = good.consumed_read["subject_digest"]
            with self.assertRaises(AssertionError):
                verify_step(replace(good, consumed_read=FrozenJSONMap(p)))
        for source in (good.restart_read["S"], pc.consumed_read["S"]):
            w = good.writer.to_dict()
            w["source"] = source
            with self.assertRaises(AssertionError):
                verify_step(replace(good, writer=FrozenJSONMap(w)))

    def test_exactly_two_full_roots_and_one_atomic_CZ_write(self):
        k = owner.kernel(self.event_model.configuration)
        root, write = SparkCCIPCKernel._admitted_read, ExactCarrierState.advance_carrier
        calls = []
        writes = []

        def read_spy(k, state):
            calls.append(state)
            return root(k, state)

        def write_spy(state, *args):
            writes.append(state)
            return write(state, *args)

        with (
            patch.object(SparkCCIPCKernel, "_admitted_read", read_spy),
            patch.object(ExactCarrierState, "advance_carrier", write_spy),
        ):
            step = k.step(self.event_model.configuration.current)
        self.assertEqual(calls, [step.before, step.after])
        self.assertEqual(writes, [step.before])

    def test_full_60_direction_finite_segments_and_cross_couplings(self):
        state = (
            owner.kernel(self.event_model.configuration)
            .step(self.event_model.configuration.current)
            .after
        )
        z = [list(row) for row in state.Z_4]
        z[0][0] = "1/16777216"
        state = replace(state, Z_4=z)
        k = owner.kernel(self.event_model.configuration)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            ref = CCIPCReference(state.graph.to_payload())
            C = arb_mat(vector(state.C))
            Z = arb_mat(matrix(state.Z_4))
            S = arb_mat(matrix(self.certificates[0].operands["S"]))
            eps = Q(1, 2**30)
            results = []
            for axis in range(60):
                dC = arb_mat(C.nrows(), 1)
                dZ = arb_mat(Z.nrows(), Z.ncols())
                if axis < 14:
                    for i in range(C.nrows()):
                        dC[i, 0] = S[i, axis]
                else:
                    i, j = ref.pairs[axis - 14]
                    dZ[i, j] = dZ[j, i] = arb(1) if i == j else 1 / arb(2).sqrt()

                def box(A, d):
                    return arb_mat(
                        [
                            [
                                arb(
                                    A[i, j].mid().fmpq(),
                                    (abs(d[i, j]) * eps).upper().fmpq(),
                                )
                                for j in range(A.ncols())
                            ]
                            for i in range(A.nrows())
                        ]
                    )

                with ctx.workprec(256):
                    p = k.partials(box(C, dC), box(Z, dZ))
                a = ref.pc_step(C - eps * dC, Z - eps * dZ)
                b = ref.pc_step(C + eps * dC, Z + eps * dZ)
                csec = (b["after"] - a["after"]) / (2 * eps)
                zsec = (b["carrier_after"] - a["carrier_after"]) / (2 * eps)
                basis = arb_mat([[0] for _ in ref.pairs])
                if axis >= 14:
                    basis[axis - 14, 0] = 1
                dc = p["CC"] * dC + p["CZ"] * basis
                dz = (1 - ref.decay) * (
                    p["SC"] * dC + p["SZ"] * basis
                ) + ref.decay * basis
                packed = arb_mat(
                    [
                        [(1 if i == j else arb(2).sqrt()) * zsec[i, j]]
                        for i, j in ref.pairs
                    ]
                )
                self.assertTrue(
                    all(
                        x.contains(y)
                        for x, y in zip(dc.entries(), csec.entries(), strict=True)
                    ),
                    ("C", axis),
                )
                self.assertTrue(
                    all(
                        x.contains(y)
                        for x, y in zip(dz.entries(), packed.entries(), strict=True)
                    ),
                    ("Z", axis),
                )
                results.append(
                    {
                        "axis": axis,
                        "kind": "charge" if axis < 14 else "carrier",
                        "contains_secant": True,
                    }
                )
            for name in ("CZ", "SC", "SZ"):
                self.assertTrue(any(not x.contains(0) for x in p[name].entries()), name)
        self.assertEqual(len(results), 60)
