"""Bounded A_RG2b joint-section, full C/W domain and atomic lifecycle checks."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_arg2b import (
    metric,
    metric_norm,
)
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_crg2b import curve_at
from pygrc.models.grc_v4_certification import CertificationInconclusive
from pygrc.models.grc_v4_spark_arg2b import SparkARG2bKernel, _section_witness, vector
from pygrc.models.grc_v4_spark_arg2b_math import ARG2bMath
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
import itertools

from arg2b_native_spark_oracle import model as independent_model
from arg2b_native_spark_oracle import proof_read, verify_step
from p991a6_arg2b_subjects import certificate_pair, configuration, profile, request


class NativeARG2bTests(unittest.TestCase):
    synthetic_window_fixture = (
        shared.NativeSparkCompletionTests.synthetic_window_fixture
    )
    test_optional_schema_static_v3_and_round_trip = (
        shared.NativeSparkCompletionTests.test_optional_schema_static_v3_and_round_trip
    )
    test_concurrent_duplicate_completion_is_one_atomic_claim = shared.NativeSparkCompletionTests.test_concurrent_duplicate_completion_is_one_atomic_claim
    test_wrong_role_pair_and_forced_requests_cannot_advance = shared.NativeSparkCompletionTests.test_wrong_role_pair_and_forced_requests_cannot_advance
    test_all_terminal_paths_excluded_anchors_and_ties = shared.NativeSparkCompletionTests.test_all_terminal_paths_excluded_anchors_and_ties
    test_duplicate_before_completion_single_shared_credit = shared.NativeSparkCompletionTests.test_duplicate_before_completion_single_shared_credit
    test_late_failure_rolls_back_state_window_consumption_and_children = shared.NativeSparkCompletionTests.test_late_failure_rolls_back_state_window_consumption_and_children
    test_zero_inspection_failure_reset_rebase_and_policy_replacement = shared.NativeSparkCompletionTests.test_zero_inspection_failure_reset_rebase_and_policy_replacement
    test_save_load_replay_and_stale_import_reconcile_occurrence = shared.NativeSparkCompletionTests.test_save_load_replay_and_stale_import_reconcile_occurrence
    test_cold_checkpoint_replay_actual_source_and_event = shared.NativeSparkCompletionTests.test_cold_checkpoint_replay_actual_source_and_event

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

    def test_declared_joint_domain_full_continuous_proof(self):
        c = self.certificates[0]
        p = c.proof
        self.assertEqual(CompletionCertificate.from_payload(c.to_payload()), c)
        self.assertEqual(p["relative_dimension"], 30)
        self.assertEqual(p["full_physical_state"], ("C", "W_A"))
        self.assertFalse(p["section_C1_claimed"])
        self.assertFalse(p["future_trajectory_required"])
        self.assertLess(fmpq(p["q"]), 1)
        self.assertLess(fmpq(p["full_step_error"]), fmpq(p["image_margin"]))
        cells = p["residual_partition"]["cells"]
        self.assertEqual(cells[0]["interval"][0], "0")
        self.assertEqual(cells[-1]["interval"][1], "1")
        self.assertTrue(
            all(
                a["interval"][1] == b["interval"][0]
                for a, b in itertools.pairwise(cells)
            )
        )
        self.assertTrue(p["physical_difference_bound"]["full_writer_included"])
        self.assertFalse(c.membership(self.event_model.configuration.current)[0])
        with ctx.workprec(256):
            Q = fmpq_mat(c.operands["curve"])
            for s in ("0", "1/7", "1/2", "999/1000", "1"):
                x = curve_at(Q, s)
                state = ExactConductanceState(
                    self.center.graph,
                    tuple(map(str, x.entries()[:15])),
                    "21",
                    tuple(
                        str(arb(v / 64).exp().mid().fmpq()) for v in x.entries()[15:]
                    ),
                )
                self.assertTrue(c.membership(state)[0], s)

    def test_all_thirty_physical_tangent_directions(self):
        k = owner.kernel(self.event_model.configuration)
        c = self.certificates[0]
        baseline = k.step(self.center)
        with ctx.workprec(768):
            m = ARG2bMath(self.center.graph)
            metric(m)
            X = m.pack(
                vector(self.center.C),
                arb_mat([[arb(fmpq(w)).log()] for w in self.center.W_A]),
            )
            Y = m.pack(
                vector(baseline.after.C),
                arb_mat([[arb(fmpq(w)).log()] for w in baseline.after.W_A]),
            )
            for direction in range(30):
                C = list(map(fmpq, self.center.C))
                W = list(map(fmpq, self.center.W_A))
                if direction < 14:
                    C[direction] += fmpq(1, 2**24)
                    C[-1] -= fmpq(1, 2**24)
                else:
                    W[direction - 14] *= 1 + fmpq(1, 2**24)
                state = replace(
                    self.center, C=tuple(map(str, C)), W_A=tuple(map(str, W))
                )
                self.assertTrue(c.membership(state)[0])
                step = k.step(state)
                dx = (
                    m.pack(
                        vector(state.C),
                        arb_mat([[arb(fmpq(w)).log()] for w in state.W_A]),
                    )
                    - X
                )
                dy = (
                    m.pack(
                        vector(step.after.C),
                        arb_mat([[arb(fmpq(w)).log()] for w in step.after.W_A]),
                    )
                    - Y
                )
                self.assertLess(
                    metric_norm(m, dy),
                    arb(fmpq(c.proof["q"])) * metric_norm(m, dx)
                    + 2 * arb(fmpq(c.proof["full_step_error"])),
                )

    def test_fixed_H_derivatives_all_directions_against_independent_scalar_rows(self):
        with ctx.workprec(256):
            m = ARG2bMath(self.center.graph)
            other = independent_model(self.center.graph.to_payload())
            C = vector(self.center.C)
            W = vector(self.center.W_A)
            L = arb_mat([[x.log()] for x in W.entries()])
            X = m.pack(C, L)
            for width in (fmpq(0), fmpq(1, 2**24)):
                box = arb_mat([[arb(x.mid().fmpq(), width)] for x in X.entries()])
                H = arb_mat(m.I)
                H[0, 0] += arb(fmpq(1, 2**22))
                a = m.fixed_jacobian(box, H)
                b = other.fixed_jacobian(box, H)
                self.assertTrue(
                    all(
                        x.overlaps(y)
                        for x, y in zip(a.entries(), b.entries(), strict=True)
                    )
                )
                for j in range(m.d):
                    self.assertTrue(
                        sum(a[i, j] for i in range(m.n)).contains(int(j < m.n))
                    )

    def test_full_sections_source_target_and_both_roles(self):
        for config in (self.config, self.event_model.configuration):
            k = owner.kernel(config)
            for role in ("current", "reset"):
                state = getattr(config, role)
                step = k.step(state)
                self.assertTrue(verify_step(config, state, step)["full_C_logW_error"])
                self.assertEqual(step.after.charge, "21")
                self.assertEqual(step.section["physical_state"], ("C", "W_A"))

    def test_chain_full_writer_tail_and_binding_mutations(self):
        c = self.event_model.configuration
        state = c.current
        w = owner.kernel(c).readmission(state)
        changes = [
            lambda d: d["chain"].pop(),
            lambda d: d["chain"][-1]["X"].__setitem__(-1, "0"),
            lambda d: d["chain"][7]["X"].__setitem__(0, "2"),
            lambda d: d["chain"][7]["H"].__setitem__(0, "1"),
            lambda d: d.update(section_tail=["0", "0"]),
            lambda d: d.update(residual_error=["0", "0"]),
            lambda d: d.update(section_error=["0", "0"]),
            lambda d: d.update(writer_in_inverse=False),
            lambda d: d["state"]["W_A"].__setitem__(
                0, str(fmpq(d["state"]["W_A"][0]) + fmpq(1, 2**40))
            ),
            lambda d: d["selected"]["current"][0].__setitem__(0, ["1", "1"]),
        ]
        for change in changes:
            bad = w.to_dict()
            change(bad)
            with self.assertRaises(
                (AssertionError, ValueError, CertificationInconclusive)
            ):
                proof_read(
                    c.reference.graph.to_payload(),
                    c.reference.profile.to_payload(),
                    state,
                    FrozenJSONMap(bad),
                )

    def test_cold_warm_state_only_reconstruction_and_W_cache_key(self):
        c = self.event_model.configuration
        k = owner.kernel(c)
        state = c.current
        _section_witness.cache_clear()
        cold = k.step(state)
        self.assertEqual(cold, k.step(state))
        self.assertGreater(k.cache_info()["section"]["hits"], 0)
        _section_witness.cache_clear()
        restored = ExactConductanceState.from_canonical_bytes(
            state.to_canonical_bytes()
        )
        self.assertEqual(k.step(restored), cold)
        weights = list(state.W_A)
        weights[0] = str(fmpq(weights[0]) * (1 + fmpq(1, 2**180)))
        changed = replace(state, W_A=tuple(weights))
        w = k.readmission(changed)
        self.assertNotEqual(w["state"], cold.section["state"])
        self.assertEqual(w["state"]["W_A"], changed.W_A)
        copy = w.to_dict()
        copy["selected"]["current"][0][0] = ["9", "9"]
        self.assertEqual(k.readmission(changed), w)

    def test_exact_event_allocations_and_retained_edge_history_both_chiralities(self):
        for chi in (-1, 1):
            m = self.source_model.duplicate()
            r = m.expand(request(m, chi))
            self.assertTrue(r.committed, r.reason)
            event = m._operation._published.completion.event
            T = fmpq_mat(event["transfer"])
            for role in ("current", "reset"):
                a = getattr(self.source_model.configuration, role)
                b = getattr(m.configuration, role)
                self.assertEqual(
                    T * fmpq_mat([[fmpq(x)] for x in a.C]),
                    fmpq_mat([[fmpq(x)] for x in b.C]),
                )
                old = dict(zip(a.graph.live_edge_ids, a.W_A, strict=True))
                new = dict(zip(b.graph.live_edge_ids, b.W_A, strict=True))
                self.assertTrue(all(new[e] == v for e, v in old.items()))
                self.assertEqual([new[e] for e in new if e not in old], ["1"] * 3)
            self.assertEqual(m.configuration.time, "16")
            self.assertEqual(self.source_model.configuration.reset, self.config.reset)

    def test_duration16_two_beat_window_and_joint_public_evidence(self):
        m = self.synthetic_window_fixture()
        gains = []
        for _ in range(3):
            r = m.step()
            self.assertTrue(r.committed, r.reason)
            gains.append(r.local_gain)
        self.assertEqual(gains, [0, 0, 1])
        e = m.compute_observables()["completion"]["evidence"]
        self.assertEqual(
            fmpq(e["observations"][-1]["time"]) - fmpq(e["observations"][0]["time"]), 32
        )
        self.assertEqual(
            e["proof"]["norm_id"], "full_C_64logW_curve_P_Euclidean_product_v1"
        )
        self.assertEqual(e["proof"]["state_channels"], ["C", "W_A"])
        for row in e["observations"]:
            d = m.completion_evidence_object(row["diagnostic_certificate"])
            self.assertIn("curve_parameter", d)

    def test_current256_vs512_unique_flux_and_conductance(self):
        c = self.event_model.configuration
        k = owner.kernel(c)
        low = k.step(c.current)
        with patch.object(
            SparkARG2bKernel, "precision_bits", property(lambda self: 512)
        ):
            high = owner.kernel(c).step(c.current)
        self.assertEqual(low.after, high.after)
        self.assertEqual(low.flux, high.flux)

    def test_complete_certificate_scope_and_coordinate_mutations(self):
        original = self.certificates[0].to_payload()
        for change in (
            lambda d: d["operands"]["curve"].pop(),
            lambda d: d["operands"]["curve"][-1].pop(),
            lambda d: d["operands"]["curve"][14].__setitem__(2, "1"),
            lambda d: d["proof"].update(q="0"),
            lambda d: d["proof"]["physical_difference_bound"].update(
                full_writer_included=False
            ),
            lambda d: d["operands"]["binding"].update(duration="32"),
            lambda d: d["operands"]["binding"].update(state_channels=["C"]),
            lambda d: d["proof"].update(future_trajectory_required=True),
        ):
            bad = deepcopy(original)
            change(bad)
            with self.assertRaises(
                (ValueError, TypeError, IndexError, CertificationInconclusive)
            ):
                CompletionCertificate.from_payload(bad)
        weights = list(self.center.W_A)
        weights[-1] = "1001/1000"
        self.assertFalse(
            self.certificates[0].membership(replace(self.center, W_A=tuple(weights)))[0]
        )

    def test_completion_clipping_full_base_and_frozen_duration(self):
        k = owner.kernel(self.event_model.configuration)
        with ctx.workprec(256):
            m = k.section_math()
            C = vector(self.center.C)
            L = arb_mat([[arb(fmpq(w)).log()] for w in self.center.W_A])
            X = m.pack(C, L)
            X[0, 0] = arb(m.chart[0][0] - 1)
            X[m.d - 1, 0] = arb(1)
            Y = arb_mat(X)
            Y[0, 0] -= 1
            Y[m.d - 1, 0] += 1
            a, b = m.lag(X, m.I, retract=True), m.lag(Y, m.I, retract=True)
            self.assertEqual(
                [
                    [str(x.mid().fmpq()), str(x.rad().fmpq())]
                    for x in a["increment"].entries()
                ],
                [
                    [str(x.mid().fmpq()), str(x.rad().fmpq())]
                    for x in b["increment"].entries()
                ],
            )
            self.assertTrue(
                all(
                    x.overlaps(y)
                    for x, y in zip(
                        ((Y + b["increment"]) - (X + a["increment"])).entries(),
                        (Y - X).entries(),
                        strict=True,
                    )
                )
            )
        for dt in ("0", "8", "32"):
            with self.assertRaises(ValueError):
                k.step(self.center, dt)
        for change in (
            {"realization": {"iteration_limit": 15}},
            {"candidate": {"tau_A": 16}},
            {"candidate": {"eta": 1 / 512}},
        ):
            with self.assertRaises((ValueError, TypeError)):
                SparkARG2bKernel(k.graph, profile(k.graph, **change))

    def test_incoming_writer_returned_and_publication_failures_atomic(self):
        for phase in ("incoming", "writer", "returned", "publish"):
            m = self.synthetic_window_fixture()
            before = m.snapshot()
            ledger = m.receipt_ledger
            calls = []
            original = SparkARG2bKernel._admitted_section

            def read(k, state, calls=calls, original=original, phase=phase):
                calls.append(1)
                if len(calls) == (1 if phase == "incoming" else 2):
                    raise CertificationInconclusive("injected joint read")
                return original(k, state)

            context = (
                patch.object(
                    SparkARG2bKernel,
                    "_writer",
                    side_effect=CertificationInconclusive("writer"),
                )
                if phase == "writer"
                else patch.object(owner, "publish", side_effect=ValueError("publish"))
                if phase == "publish"
                else patch.object(SparkARG2bKernel, "_admitted_section", read)
            )
            with context:
                self.assertFalse(m.step().committed)
            self.assertEqual(before, m.snapshot())
            self.assertEqual(ledger, m.receipt_ledger)
            self.assertTrue(m.step().committed)


if __name__ == "__main__":
    unittest.main()
