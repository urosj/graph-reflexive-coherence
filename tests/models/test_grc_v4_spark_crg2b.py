"""Bounded native C_RG2b section, continuous-domain and atomic lifecycle checks."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, ctx, fmpq, fmpq_mat

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_crg2b import curve_at
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_spark_cos import _matrix
from pygrc.models.grc_v4_spark_crg2b import SparkCRG2bKernel, _section_witness
from pygrc.models.grc_v4_spark_state import ExactResources, QuarticCRG2bProfile
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_9_v4_spark_completion as shared

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from crg2b_native_spark_oracle import audit_read, verify_step
from p991a2_native_spark_numerics import row_oracle
from p991a6_crg2b_subjects import certificate_pair, configuration, profile, request


class NativeCRG2bTests(unittest.TestCase):
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

    def test_full_continuous_domain_and_exact_membership(self):
        c = self.certificates[0]
        self.assertEqual(CompletionCertificate.from_payload(c.to_payload()), c)
        self.assertLess(fmpq(c.proof["q"]), 1)
        self.assertLess(fmpq(c.proof["full_step_error"]), fmpq(c.proof["image_margin"]))
        self.assertGreater(fmpq(c.proof["represented_image_margin"]), 0)
        self.assertEqual(c.proof["relative_dimension"], 14)
        self.assertFalse(c.proof["section_C1_claimed"])
        self.assertFalse(c.proof["future_trajectory_required"])
        self.assertEqual(c.proof["residual_degree"], 120)
        self.assertTrue(c.proof["all_parameters_certified_continuously"])
        Q = _matrix(c.operands["curve"])
        for parameter in ("0", "1", "1/2", "1/7", "999/1000", "998001/1000000"):
            values = tuple(str(x) for x in curve_at(Q, fmpq(parameter)).entries())
            state = ExactResources(self.center.graph, values, "21")
            self.assertTrue(c.membership(state)[0], parameter)
            self.assertEqual(
                sorted(
                    len(v) for v in row_oracle(state)["complete_basins_oracle"].values()
                ),
                [2, 3],
            )
        self.assertFalse(c.membership(self.event_model.configuration.current)[0])

    def test_certificate_rejects_coordinate_curve_and_binding_mutations(self):
        original = self.certificates[0].to_payload()
        for mutate in (
            lambda d: d["proof"].update(q="0"),
            lambda d: d["operands"]["curve"].pop(),
            lambda d: d["operands"]["curve"][0].__setitem__(2, "1"),
            lambda d: d["operands"].update(radius="1/1000"),
            lambda d: d["operands"].update(parameter_decay="1"),
            lambda d: d["operands"].update(subdivision_depth=0),
            lambda d: d["operands"]["binding"].update(state_channels=["C", "Z_4"]),
            lambda d: d["operands"]["binding"].update(duration="32"),
            lambda d: d["operands"]["binding"].update(charge="22"),
            lambda d: d["operands"]["binding"].update(
                context={"evaluator": "other", "parameters": {}}
            ),
        ):
            bad = deepcopy(original)
            mutate(bad)
            with self.assertRaises(
                (ValueError, TypeError, IndexError, CertificationInconclusive)
            ):
                CompletionCertificate.from_payload(bad)
        with self.assertRaises(ValueError):
            self.certificates[0].require_binding(
                owner.kernel(self.event_model.configuration),
                self.config.policy,
                "reset",
                "21",
            )

    def test_real_source_event_and_both_exact_allocations(self):
        event = self.event_model._operation._published.completion.event
        config = self.event_model.configuration
        self.assertEqual(self.source_model.configuration.time, "8")
        self.assertEqual(self.event_model.configuration.time, "8")
        self.assertEqual(len(config.current.C), 15)
        self.assertEqual(config.current.charge, config.reset.charge)
        self.assertEqual(
            event["source_receipt"]["receipt_id"],
            self.source_model.receipt_ledger[-1].receipt_id,
        )
        self.assertEqual(
            self.event_model.compute_observables()["completion"]["children"], []
        )
        T = _matrix(event["transfer"])
        for role in ("current", "reset"):
            before = getattr(self.source_model.configuration, role)
            after = getattr(config, role)
            expected = T * fmpq_mat([[fmpq(x)] for x in before.C])
            self.assertEqual(tuple(map(str, expected.entries())), after.C)
            module = event["module"]
            values = dict(zip(after.graph.live_node_ids, after.C, strict=True))
            parent = fmpq(before.C[before.graph.live_node_ids.index("v")])
            self.assertEqual(values[module[0]], "0")
            for node, share in zip(
                module[1:], ("5/2048", "1021/1024", "1/2048"), strict=True
            ):
                self.assertEqual(fmpq(values[node]), parent * fmpq(share))
            witness = owner.kernel(config).readmission(after)
            self.assertEqual(witness["state"].to_dict(), after.to_payload())
            self.assertEqual(witness["physical_state"], ("C",))
        old = request(self.source_model).to_payload()
        old["resource_distribution"] = [1 / 64, 31 / 32, 1 / 64]
        from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput

        before = self.source_model.snapshot()
        self.assertFalse(
            self.source_model.expand(
                GRC9V4ExpansionRequestInput.from_payload(old)
            ).committed
        )
        self.assertEqual(before, self.source_model.snapshot())

    def test_opposite_chiral_event_and_own_section(self):
        m = self.source_model.duplicate()
        r = m.expand(request(m, -1))
        self.assertTrue(r.committed, r.reason)
        pair, center = certificate_pair(m)
        self.assertTrue(m.install_completion_certificates(*pair).committed)
        self.assertTrue(pair[0].membership(center)[0])
        self.assertNotEqual(pair[0].certificate_id, self.certificates[0].certificate_id)
        verify_step(owner.kernel(m.configuration).step(m.configuration.current))

    def test_both_roles_source_target_and_poststate_against_independent_sections(self):
        for config in (self.config, self.event_model.configuration):
            for role in ("current", "reset"):
                result = owner.kernel(config).step(getattr(config, role))
                self.assertTrue(verify_step(result)["full_step_error"])
                row_oracle(result.after)

    def test_all_fourteen_resource_differences_in_full_physical_map(self):
        cert = self.certificates[0]
        k = owner.kernel(self.event_model.configuration)
        Q = _matrix(cert.operands["curve"])
        for parameter in ("0", "1"):
            center = replace(
                self.center, C=tuple(map(str, curve_at(Q, fmpq(parameter)).entries()))
            )
            baseline = k.step(center)
            P = k.section_math().algebra["P"]
            for j in range(14):
                values = list(map(fmpq, center.C))
                values[j] += fmpq(1, 2**24)
                values[-1] -= fmpq(1, 2**24)
                state = replace(center, C=tuple(map(str, values)))
                self.assertTrue(cert.membership(state)[0])
                shifted = k.step(state)
                dc = fmpq_mat(
                    [
                        [fmpq(a) - fmpq(b)]
                        for a, b in zip(state.C, center.C, strict=True)
                    ]
                )
                dy = fmpq_mat(
                    [
                        [fmpq(a) - fmpq(b)]
                        for a, b in zip(shifted.after.C, baseline.after.C, strict=True)
                    ]
                )
                with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                    distance = arb((dc.transpose() * P * dc)[0, 0]).sqrt()
                    result = arb((dy.transpose() * P * dy)[0, 0]).sqrt()
                    self.assertLess(
                        result,
                        arb(fmpq(cert.proof["q"])) * distance
                        + 2 * arb(fmpq(cert.proof["full_step_error"])),
                    )

    def test_two_positive_duration8_beats_and_complete_curve_evidence(self):
        m = self.synthetic_window_fixture()
        gains = []
        for _ in range(3):
            r = m.step()
            self.assertTrue(r.committed, r.reason)
            gains.append(r.local_gain)
        self.assertEqual(gains, [0, 0, 1])
        v = m.compute_observables()["completion"]
        self.assertEqual(len(v["children"]), 1)
        evidence = v["evidence"]
        obs = evidence["observations"]
        self.assertEqual(fmpq(obs[-1]["time"]) - fmpq(obs[0]["time"]), 16)
        proof = evidence["proof"]
        self.assertEqual(proof["norm_id"], "full_charge_tangent_curve_P_metric_v1")
        domain = m.completion_evidence_object(proof["domain"])
        self.assertEqual(
            domain["curve"],
            [list(row) for row in self.certificates[0].operands["curve"]],
        )
        for row in obs:
            diagnostic = m.completion_evidence_object(row["diagnostic_certificate"])
            self.assertIn("curve_parameter", diagnostic)
            self.assertLessEqual(fmpq(diagnostic["membership_norm"]), 1)

    def test_section_witness_mutations_are_detected_independently(self):
        c = self.event_model.configuration
        k = owner.kernel(c)
        state = c.current
        good = k.readmission(state)
        for change in (
            lambda d: d["chain"].pop(),
            lambda d: d["chain"][0]["X"].__setitem__(0, "0"),
            lambda d: d["chain"][0]["H"].__setitem__(0, "2"),
            lambda d: d.update(section_tail=["0", "0"]),
            lambda d: d.update(residual_error=["0", "0"]),
            lambda d: d.update(section_error=["0", "0"]),
            lambda d: d["current"][0].__setitem__(0, ["1", "1"]),
            lambda d: d["baseline"][0].__setitem__(0, ["1", "1"]),
            lambda d: d["flat"][0].__setitem__(0, ["1", "1"]),
            lambda d: d["query_proposal"].__setitem__(
                0, str(fmpq(d["query_proposal"][0]) + 1)
            ),
        ):
            bad = good.to_dict()
            change(bad)
            with (
                _ARB_CONTEXT_LOCK,
                ctx.workprec(768),
                self.assertRaises((AssertionError, ValueError)),
            ):
                audit_read(
                    c.reference.graph.to_payload(),
                    c.reference.profile.to_payload(),
                    state,
                    FrozenJSONMap(bad),
                    fresh=False,
                )

    def test_fixed_precision_comparison_and_unique_flux(self):
        c = self.event_model.configuration
        k = owner.kernel(c)
        for role in ("current", "reset"):
            state = getattr(c, role)
            low = k.step(state)
            with patch.object(
                SparkCRG2bKernel, "precision_bits", property(lambda self: 512)
            ):
                high = owner.kernel(c).step(state)
            self.assertEqual(low.after, high.after)
            self.assertEqual(low.flux, high.flux)

    def test_complete_subject_cache_and_policy_invalidations(self):
        c = self.event_model.configuration
        k = owner.kernel(c)
        state = c.current
        _section_witness.cache_clear()
        first = k.readmission(state)
        info = _section_witness.cache_info()
        self.assertEqual(k.readmission(state), first)
        self.assertGreater(_section_witness.cache_info().hits, info.hits)
        values = list(map(fmpq, state.C))
        values[0] += fmpq(1, 2**180)
        values[1] -= fmpq(1, 2**180)
        changed = replace(state, C=tuple(map(str, values)))
        other = k.readmission(changed)
        self.assertNotEqual(other["state"], first["state"])
        self.assertEqual(_section_witness.cache_info().misses, info.misses + 1)
        self.assertEqual(_section_witness.cache_info().maxsize, 8)
        private_matrix = k.section_math().algebra["B"]
        private_matrix[0, 0] = 999
        self.assertNotEqual(k.section_math().algebra["B"][0, 0], 999)
        altered = first.to_dict()
        altered["current"][0][0] = ["9", "9"]
        self.assertEqual(k.readmission(state), first)
        p = c.reference.profile
        self.assertEqual(QuarticCRG2bProfile.from_payload(p.to_payload()), p)
        for changes in (
            {"realization": {"iteration_limit": 11}},
            {"realization": {"error_tolerance": 1e-8}},
            {"candidate": {"eta_C": 1 / 512}},
            {"realization": {"extension_evaluator_id": "different"}},
        ):
            with self.assertRaises((ValueError, TypeError)):
                SparkCRG2bKernel(state.graph, profile(state.graph, **changes))
        with self.assertRaises(ValueError):
            k.step(state, "32")

    def test_incoming_returned_and_postnumerics_failures_are_atomic(self):
        for failed in (1, 2):
            m = self.synthetic_window_fixture()
            before = m.snapshot()
            original = SparkCRG2bKernel._admitted_section
            calls = []

            def read(k, state, calls=calls, failed=failed, original=original):
                calls.append(1)
                if len(calls) == failed:
                    raise CertificationInconclusive("injected section failure")
                return original(k, state)

            with patch.object(SparkCRG2bKernel, "_admitted_section", read):
                self.assertFalse(m.step().committed)
            self.assertEqual(m.snapshot(), before)
        for phase in ("progress", "publish"):
            m = self.synthetic_window_fixture()
            before = m.snapshot()
            with patch.object(
                owner, phase, side_effect=ValueError("injected late failure")
            ):
                self.assertFalse(m.step().committed)
            self.assertEqual(m.snapshot(), before)

    def test_complete_proof_audit_needs_no_second_section_solve(self):
        import crg2b_native_spark_oracle as oracle

        c = self.event_model.configuration
        step = owner.kernel(c).step(c.current)
        oracle._audited_read.cache_clear()
        with patch.object(
            oracle, "selected", side_effect=AssertionError("unexpected second solve")
        ):
            first = verify_step(step, fresh=False)
            self.assertTrue(first["incoming"]["proof_derived_section"])
            self.assertFalse(first["incoming"]["fresh_depth40"])
            hits = oracle._audited_read.cache_info().hits
            self.assertEqual(verify_step(step, fresh=False), first)
            self.assertGreater(oracle._audited_read.cache_info().hits, hits)
            bad = step.restart_section.to_dict()
            bad["section_tail"] = ["0", "0"]
            with self.assertRaises(AssertionError):
                verify_step(
                    replace(step, restart_section=FrozenJSONMap(bad)), fresh=False
                )

    def test_optimized_clipping_and_geometry_preserve_outward_arithmetic(self):
        from flint import arb_mat

        c = self.event_model.configuration
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            m = owner.kernel(c).section_math()
            raw = [
                arb(m.lo - 1),
                arb(m.lo),
                arb(m.lo, fmpq(1, 100)),
                arb(fmpq(1, 3)),
                arb(2),
                arb(m.hi, fmpq(1, 100)),
                arb(m.hi),
                arb(m.hi + 1),
            ]
            C = arb_mat([[raw[i % len(raw)]] for i in range(m.n)])
            expected = []
            for x in C.entries():
                a = max(m.lo, min(m.hi, x.lower().fmpq()))
                b = max(m.lo, min(m.hi, x.upper().fmpq()))
                expected.append(arb((a + b) / 2, (b - a) / 2))
            for x, y in zip(m.clip(C).entries(), expected, strict=True):
                self.assertEqual(
                    (x.lower().fmpq(), x.upper().fmpq()),
                    (y.lower().fmpq(), y.upper().fmpq()),
                )
            f = arb_mat([[arb(fmpq(i - 8, 1000), fmpq(1, 2**200))] for i in range(m.m)])
            expected_H = m.I + arb_mat(
                [
                    [m.overlap[i][j] * f[i, 0] * f[j, 0] / 8 for j in range(m.m)]
                    for i in range(m.m)
                ]
            )
            result = m.geometry(f)
            for i in range(m.m):
                for j in range(m.m):
                    self.assertTrue(result[i, j].overlaps(expected_H[i, j]))
                    left = f[i, 0].mid().fmpq() - f[i, 0].rad().fmpq()
                    right = f[i, 0].mid().fmpq() + f[i, 0].rad().fmpq()
                    if i == j:
                        products = [left * left, right * right]
                        if left <= 0 <= right:
                            products.append(fmpq(0))
                    else:
                        low = f[j, 0].mid().fmpq() - f[j, 0].rad().fmpq()
                        high = f[j, 0].mid().fmpq() + f[j, 0].rad().fmpq()
                        products = [a * b for a in (left, right) for b in (low, high)]
                    corners = [x * m.overlap[i][j] / 8 + int(i == j) for x in products]
                    with self.subTest(i=i, j=j):
                        for enclosure in (result[i, j], expected_H[i, j]):
                            lower = enclosure.mid().fmpq() - enclosure.rad().fmpq()
                            upper = enclosure.mid().fmpq() + enclosure.rad().fmpq()
                            self.assertTrue(all(lower <= x <= upper for x in corners))

    def test_inverse_exhaustion_and_domain_escape_fail_closed(self):
        import pygrc.models.grc_v4_spark_crg2b_math as math

        c = self.event_model.configuration
        k = owner.kernel(c)
        _section_witness.cache_clear()
        with (
            patch.object(math, "NEWTON_LIMIT", 0),
            self.assertRaises(CertificationInconclusive),
        ):
            k.readmission(c.current)
        values = list(c.current.C)
        values[0] = "5"
        values[-1] = str(fmpq(values[-1]) + fmpq(c.current.C[0]) - 5)
        with self.assertRaises((ValueError, CertificationInconclusive)):
            k.readmission(ExactResources(c.current.graph, tuple(values), "21"))


if __name__ == "__main__":
    unittest.main()
