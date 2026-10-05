"""Independent A_PC oracle pressure before its separately accepted runtime leaf."""

import json
import math
import unittest
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import verify_p983a_apc_oracle as oracle

from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9SparkPolicy, GRC9V4CandidateDetection
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph, GRC9V4PostbeatRows
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState


class APCOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = oracle.build()
        cls.record = json.loads((oracle.ROOT / oracle.RECORD).read_text())

    def test_full_independent_intervals_and_both_role_continuations(self):
        r = self.record
        certs = oracle.validate(r, self.expected)
        self.assertEqual(len(certs), 25)
        for role in ("current", "reset"):
            self.assertEqual(len(r["continuation"][role]), 11)
            for row in r["continuation"][role][:10]:
                self.assertGreater(min(row["C"]), 0)
                self.assertLess(max(row["C"]), 4)
                self.assertLess(abs(sum(map(Q, row["C"])) - Q(30.140625)), Q(1, 2**40))
                self.assertTrue(
                    all(oracle.W_MIN <= x <= oracle.W_MAX for x in row["W_A"])
                )
                oracle.carrier_admitted(r["target"]["port_graph"], row["Z_4"])
        self.assertEqual(r["source"]["reset"], r["initial"]["reset"])
        self.assertNotEqual(r["source"]["current"]["W_A"], r["source"]["reset"]["W_A"])

    def test_native_identity_d52_allocator_and_candidate_match_mechanics(self):
        r = self.record
        for name in ("source", "target"):
            part = r[name]
            ref = GRCV4ReferenceGeometry.from_payload(part["reference"])
            self.assertEqual(ref.graph.port_graph.to_payload(), part["port_graph"])
            self.assertEqual(ref.profile.identity_payload.profile_family_id, "A_PC")
            self.assertEqual(
                ref.profile.params_resolved.candidate.descriptor_backend_id,
                oracle.common.descriptor_id(part["port_graph"]),
            )
            self.assertEqual(
                ref.profile.params_resolved.geometry.kappa_H, oracle.KAPPA_H
            )
            for field, schema in [
                ("scientific", "scientific_state_payload"),
                ("reset", "grc9v4_reset_payload"),
            ]:
                self.assertEqual(
                    payload_identity(schema, part[field + "_payload"]),
                    part[field + "_digest"],
                )
        graph = GRC9V4PortGraph.from_payload(r["source"]["port_graph"])
        plan = GRC9V4ExpansionPlan(
            graph,
            r["source"]["scientific_digest"],
            GRC9V4ExpansionRequestInput.from_payload(r["request"]),
            GRC9ExpansionPolicy.from_payload(
                r["specialization"]["resolved"]["expansion"]
            ),
        )
        self.assertEqual(plan.event_id, r["event_id"])
        self.assertEqual(plan.target_graph.to_payload(), r["target"]["port_graph"])
        ref = GRCV4ReferenceGeometry.from_payload(r["source"]["reference"])
        state = r["source"]["current"]
        rows = GRC9V4PostbeatRows(
            graph,
            ref.profile,
            GRCV4AuthoritativeState(state["C"], state["W_A"], state["Z_4"]),
            tuple(r["source_reference_reads"]["current"]["current"]),
            1,
            -1,
        )
        source = rows.evaluate()[-1]
        np.testing.assert_allclose(
            source.gradient,
            r["candidate_detection"]["source_gradient"],
            rtol=0,
            atol=2**-48,
        )
        detection = GRC9V4CandidateDetection(
            rows, GRC9SparkPolicy.from_payload(r["specialization"]["resolved"]["spark"])
        )
        self.assertEqual(list(detection.candidate_node_ids()), ["source-s"])

    def test_exact_W_lineage_carrier_archive_loss_and_reference_maps(self):
        r = self.record
        source, target = r["source"]["port_graph"], r["target"]["port_graph"]
        old, new = (
            [e["edge_id"] for e in source["edges"]],
            [e["edge_id"] for e in target["edges"]],
        )
        for role in ("current", "reset"):
            before = r["source"][role]
            after = r["target"]["roles"][role]
            wm = dict(zip(new, after["authoritative"]["W_A"], strict=True))
            self.assertEqual([wm[e] for e in old], before["W_A"])
            self.assertEqual([wm[e] for e in new if e not in old], [1.0] * 7)
            self.assertEqual(after["authoritative"]["Z_4"], [0.0] * 256)
            refs = dict(zip(new, after["incoming_reference_current"], strict=True))
            self.assertEqual(
                [refs[e] for e in old], r["source_reference_reads"][role]["current"]
            )
            self.assertEqual([refs[e] for e in new if e not in old], [0.0] * 7)
            physical = dict(
                zip(new, r["continuation"][role][0]["current"], strict=True)
            )
            self.assertTrue(all(physical[e] != 0 for e in new if e not in old))
            self.assertLessEqual(
                abs(
                    sum(map(Q, after["authoritative"]["C"])) - sum(map(Q, before["C"]))
                ),
                Q(1, 2**48),
            )
        archive = r["carrier_archive"]
        self.assertEqual(archive["source_edge_ids"], old)
        self.assertEqual(
            archive["history_content"],
            oracle.carrier_content(r["source"]["current"], r["source"]["reset"]),
        )
        self.assertEqual(
            archive["history_digest"],
            payload_identity(
                "history_content_identity_payload", archive["history_content"]
            ),
        )
        receipts = r["receipt_expectations"]
        self.assertEqual(receipts["information_losses"], ["carrier_history_loss"])
        self.assertEqual(receipts["candidate"]["information_loss"], "none")
        self.assertEqual(receipts["carrier"]["disposition"], "whole_carrier_reset")
        self.assertNotEqual(
            receipts["carrier"]["source_history_digest"],
            receipts["carrier"]["target_history_digest"],
        )
        self.assertEqual(receipts["time"], oracle.DT)
        self.assertEqual(receipts["step_index"], 1)

    def test_rational_resource_columns_and_history_left_inverse(self):
        r = self.record
        source, target = r["source"]["port_graph"], r["target"]["port_graph"]
        ns, nt = source["live_node_ids"], target["live_node_ids"]
        shares = {
            r["event_id"] + "/satellite/" + str(i): q
            for i, q in enumerate((Q(1, 4), Q(3, 8), Q(3, 8)), 1)
        }
        p = [
            [Q(int(n == s)) if s != "source-s" else shares.get(n, Q(0)) for s in ns]
            for n in nt
        ]
        self.assertEqual([sum(column) for column in zip(*p, strict=True)], [1] * 10)
        old, new = (
            [e["edge_id"] for e in source["edges"]],
            [e["edge_id"] for e in target["edges"]],
        )
        e = [[int(a == b) for b in old] for a in new]
        projection = list(zip(*e, strict=True))
        self.assertEqual(
            [
                [
                    sum(a * b for a, b in zip(row, col, strict=True))
                    for col in zip(*e, strict=True)
                ]
                for row in projection
            ],
            np.eye(9, dtype=int).tolist(),
        )
        seed = [int(a not in old) for a in new]
        self.assertEqual(
            [sum(a * b for a, b in zip(row, seed, strict=True)) for row in projection],
            [0] * 9,
        )
        for role in ("current", "reset"):
            exact = [
                sum(a * Q(b) for a, b in zip(row, r["source"][role]["C"], strict=True))
                for row in p
            ]
            represented = r["target"]["roles"][role]["authoritative"]["C"]
            self.assertLess(
                max(abs(a - Q(b)) for a, b in zip(exact, represented, strict=True)),
                Q(1, 2**48),
            )

    def test_whole_chart_extreme_points_fit_the_proved_bound(self):
        for name in ("source", "target"):
            g = self.record[name]["port_graph"]
            m = len(g["edges"])
            n = len(g["live_node_ids"])
            p = oracle.PaperAPC(g)
            high = oracle.IntervalRows(oracle.model_for(g))
            limit = Q(
                self.record["domain_certificates"][name]["source_frobenius_upper"]
            )
            for coordinate in (0, n - 1):
                c = [0.0] * n
                c[coordinate] = oracle.RESOURCE_RADIUS
                for w in (
                    [oracle.W_MIN] * m,
                    [oracle.W_MAX] * m,
                    [oracle.W_MIN if i % 2 else oracle.W_MAX for i in range(m)],
                ):
                    for sign in (-1, 1):
                        z = np.zeros((m, m))
                        z[0, 0] = sign * oracle.RADIUS
                        oracle.carrier_admitted(g, z)
                        h = high.I + oracle.number(oracle.KAPPA_H) * oracle.IV.matrix(
                            z.tolist()
                        )
                        read = high.read("A", oracle.vector(c), oracle.vector(w), h)
                        squared = sum(oracle.upper_abs(x) ** 2 for x in read["source"])
                        self.assertLessEqual(squared, limit**2)
                        point = p.read(
                            c,
                            w,
                            p.I + p.mp.mpf(oracle.KAPPA_H) * p.mp.matrix(z.tolist()),
                        )
                        self.assertGreaterEqual(point["regularity"], p.mp.mpf(31) / 32)
                        self.assertLess(
                            oracle.full_error(
                                list(map(float, point["current"])), read["J"]
                            ),
                            oracle.CURRENT_ERROR,
                        )

    def test_carrier_seed_every_coordinate_and_exact_ball_bound(self):
        r = self.record
        g = r["source"]["port_graph"]
        for role in ("current", "reset"):
            z = r["initial"][role]["Z_4"]
            self.assertEqual(
                oracle.carrier_admitted(g, z), Q(27, 256) * oracle.RADIUS**2
            )
            for i in range(9):
                for j in range(9):
                    self.assertEqual(
                        z[i * 9 + j],
                        (1 if role == "current" else -1)
                        * Q(oracle.RADIUS, 16)
                        * (1 if i == j else Q(1, 2))
                        * (-1) ** (i + j),
                    )

    def test_uniform_chart_not_sampled_trajectory_and_separate_research_domain(self):
        for name in ("source", "target"):
            c = self.record["domain_certificates"][name]
            self.assertLess(Q(c["source_frobenius_upper"]), oracle.RADIUS)
            self.assertEqual(Q(c["geometry_radius"]), Q(1, 8))
            self.assertEqual(Q(c["hodge_lower"]), Q(7, 8))
            self.assertEqual(Q(c["current_margin_lower"]), Q(31, 32))
            self.assertLess(Q(c["conductance_exponent_absolute_upper"]), 1)
        witness = oracle.boundary_witnesses(self.record)[
            "small_research_radius_on_full_chart"
        ]
        self.assertGreater(
            Q(witness["source_diagonal_lower"]), Q(witness["rejected_radius"])
        )
        self.assertEqual(sum(Q(x) ** 2 for x in witness["C"]), 256)
        self.assertEqual(witness["Z_4"], [0.0] * 81)

    def test_whole_chart_extremes_reject_without_repair(self):
        graph = self.record["source"]["port_graph"]
        for kw in (
            {"radius": Q(0)},
            {"radius": Q(-1)},
            {"radius": Q(1, 2**22)},
            {"kappa": Q(1)},
            {"low": Q(0)},
            {"high": Q(1, 4)},
            {"resource": Q(0)},
            {"resource": Q(10**9)},
        ):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                oracle.whole_chart(graph, **kw)

    def test_carrier_boundary_symmetry_support_and_shape(self):
        g = self.record["target"]["port_graph"]
        m = len(g["edges"])
        good = np.zeros((m, m))
        good[0, 0] = oracle.RADIUS
        self.assertEqual(oracle.carrier_admitted(g, good), oracle.RADIUS**2)
        bad = good.copy()
        bad[0, 0] = math.nextafter(oracle.RADIUS, math.inf)
        with self.assertRaisesRegex(ValueError, "ball"):
            oracle.carrier_admitted(g, bad)
        for value in (math.nan, math.inf, -math.inf):
            bad = good.copy()
            bad[0, 0] = value
            with self.assertRaisesRegex(ValueError, "finite"):
                oracle.carrier_admitted(g, bad)
        bad = good.copy()
        bad[0, 1] = 1
        with self.assertRaisesRegex(ValueError, "symmetry"):
            oracle.carrier_admitted(g, bad)
        ends = [{e[k]["node_id"] for k in ("tail", "head")} for e in g["edges"]]
        i, j = next(
            (i, j) for i, a in enumerate(ends) for j, b in enumerate(ends) if not a & b
        )
        bad = np.zeros((m, m))
        bad[i, j] = bad[j, i] = 2**-100
        with self.assertRaisesRegex(ValueError, "support"):
            oracle.carrier_admitted(g, bad)
        with self.assertRaisesRegex(ValueError, "shape"):
            oracle.carrier_admitted(g, [0.0] * (m * m - 1))

    def test_event_admission_does_not_imply_next_resource_positivity(self):
        neg = oracle.boundary_witnesses(self.record)[
            "admitted_event_negative_next_step"
        ]
        self.assertLess(Q(neg["next_resource_upper"]), 0)
        s = neg["mapped_target_role"]
        g = self.record["target"]["port_graph"]
        self.assertGreaterEqual(min(s["C"]), 0)
        self.assertEqual(s["Z_4"], [0.0] * 256)
        oracle.whole_chart(g)
        step = oracle.PaperAPC(g).step(s["C"], s["W_A"], s["Z_4"])
        with self.assertRaisesRegex(ValueError, "negative next resource"):
            oracle.check_step(g, s["C"], s["W_A"], s["Z_4"], step)

    def test_source_archive_stage_is_exact_even_below_numeric_error_budget(self):
        oracle.check_event_stage(self.record)
        for role in ("current", "reset"):
            changed = deepcopy(self.record)
            changed["source"][role]["Z_4"] = changed["source_reference_reads"][role][
                "Z_4"
            ]
            changed["carrier_archive"]["history_content"] = oracle.carrier_content(
                changed["source"]["current"], changed["source"]["reset"]
            )
            with self.assertRaisesRegex(ValueError, "physical stage"):
                oracle.check_event_stage(changed)
            changed = deepcopy(self.record)
            z = changed["carrier_archive"]["history_content"]["content"]
            z[0] = math.nextafter(z[0], math.inf)
            self.assertLess(
                abs(
                    z[0]
                    - self.record["carrier_archive"]["history_content"]["content"][0]
                ),
                float(oracle.CARRIER_ERROR),
            )
            with self.assertRaisesRegex(ValueError, "archive physical stage"):
                oracle.check_event_stage(changed)
        changed = deepcopy(self.record)
        changed["source"]["current"]["Z_4"] = changed["initial"]["current"]["Z_4"]
        with self.assertRaisesRegex(ValueError, "physical stage"):
            oracle.check_event_stage(changed)

    def test_each_numerical_output_has_an_independent_interval_guard(self):
        g = self.record["target"]["port_graph"]
        for role in ("current", "reset"):
            s = deepcopy(self.record["target"]["roles"][role]["authoritative"])
            good = self.record["continuation"][role][0]
            for field in ("C", "W_A", "Z_4", "current", "baseline", "H", "source"):
                changed = deepcopy(good)
                if field in ("H", "source"):
                    changed[field][0][0] += 2**-20
                else:
                    changed[field][0] += 2**-20
                with (
                    self.subTest(role=role, field=field),
                    self.assertRaises(ValueError),
                ):
                    oracle.check_step(g, s["C"], s["W_A"], s["Z_4"], changed)
            self.assertEqual(s, self.record["target"]["roles"][role]["authoritative"])

    def test_entry_resource_W_and_carrier_domain_guards(self):
        g = self.record["source"]["port_graph"]
        s = self.record["source"]["current"]
        out = self.record["source_reference_reads"]["current"]
        for key, value in [
            ("C", -1.0),
            ("C", math.inf),
            ("C", 17.0),
            ("W_A", 0.0),
            ("W_A", math.nan),
            ("W_A", 0.49),
            ("W_A", 2.0),
        ]:
            changed = deepcopy(s)
            changed[key][0] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                oracle.check_step(g, changed["C"], changed["W_A"], changed["Z_4"], out)

    def test_read_uses_old_carrier_not_current_source_or_new_writer(self):
        g = self.record["target"]["port_graph"]
        s = self.record["target"]["roles"]["current"]["authoritative"]
        p = oracle.PaperAPC(g)
        good = p.step(s["C"], s["W_A"], s["Z_4"])
        self.assertEqual(good["H"], np.eye(16).tolist())
        for bad_z in (np.asarray(good["source"]).reshape(-1).tolist(), good["Z_4"]):
            changed = p.step(s["C"], s["W_A"], bad_z)
            with self.assertRaisesRegex(ValueError, "full error budget"):
                oracle.check_step(g, s["C"], s["W_A"], s["Z_4"], changed)

    def test_zero_source_native_release_is_exponential_not_event_reset(self):
        g = self.record["source"]["port_graph"]
        p = oracle.PaperAPC(g)
        c = [1.0] * 10
        w = [0.9] * 9
        z = np.asarray(oracle.seed(g, "current"))
        result = p.step(c, w, z)
        self.assertTrue(all(x == 0 for row in result["source"] for x in row))
        decay = p.mp.exp(-p.mp.mpf(oracle.DT))
        self.assertEqual(
            result["Z_4"], [float(decay * p.mp.mpf(float(x))) for x in z.flat]
        )
        self.assertTrue(any(result["Z_4"]))
        oracle.check_step(g, c, w, z, result)
        self.assertEqual(
            self.record["receipt_expectations"]["carrier"]["information_loss"],
            "carrier_history_loss",
        )

    def test_producer_owns_inputs_and_point_writer_corruption_is_detected(self):
        g = deepcopy(self.record["target"]["port_graph"])
        s = deepcopy(self.record["target"]["roles"]["current"]["authoritative"])
        saved = deepcopy(s)
        p = oracle.PaperAPC(g)
        expected = p.step(s["C"], s["W_A"], s["Z_4"])
        g["edges"][0]["tail"]["port"] = 9
        self.assertEqual(p.step(s["C"], s["W_A"], s["Z_4"]), expected)
        self.assertEqual(s, saved)
        old = oracle.PaperAPC.write

        def wrong(p, c, w, j):
            out = old(p, c, w, j)
            out[0] += p.mp.mpf(2) ** -20
            return out

        with patch.object(oracle.PaperAPC, "write", wrong):
            bad = p.step(s["C"], s["W_A"], s["Z_4"])
        with self.assertRaisesRegex(ValueError, "W_A full error"):
            oracle.check_step(p.graph, s["C"], s["W_A"], s["Z_4"], bad)

    def test_signed_reorder_covaries_both_histories_geometry_and_source(self):
        for name in ("source", "target"):
            g = self.record[name]["port_graph"]
            s = (
                self.record["source"]["current"]
                if name == "source"
                else self.record["target"]["roles"]["current"]["authoritative"]
            )
            base = oracle.PaperAPC(g).step(s["C"], s["W_A"], s["Z_4"])
            m = len(g["edges"])
            for offset in (0, 1, 3):
                order = list(range(offset, m)) + list(range(offset))
                sign = np.array([-1 if i % 2 else 1 for i in order])
                moved = deepcopy(g)
                moved["edges"] = [deepcopy(g["edges"][i]) for i in order]
                for edge, sigma in zip(moved["edges"], sign, strict=True):
                    if sigma < 0:
                        edge["tail"], edge["head"] = edge["head"], edge["tail"]

                def tensor(values, m=m, order=order, sign=sign):
                    return (
                        np.asarray(values).reshape(m, m)[np.ix_(order, order)]
                        * sign[:, None]
                        * sign[None, :]
                    )

                z = tensor(s["Z_4"])
                w = [s["W_A"][i] for i in order]
                out = oracle.PaperAPC(moved).step(s["C"], w, z)
                oracle.check_step(moved, s["C"], w, z, out)
                np.testing.assert_allclose(out["C"], base["C"], rtol=0, atol=2**-48)
                np.testing.assert_allclose(
                    out["W_A"], np.asarray(base["W_A"])[order], rtol=0, atol=2**-48
                )
                for field in ("current", "baseline"):
                    np.testing.assert_allclose(
                        out[field],
                        np.asarray(base[field])[order] * sign,
                        rtol=0,
                        atol=2**-44,
                    )
                for field in ("H", "source", "Z_4"):
                    np.testing.assert_allclose(
                        np.asarray(out[field]).reshape(m, m),
                        tensor(base[field]),
                        rtol=0,
                        atol=2**-44,
                    )

    def test_rehashed_history_archive_profile_outputs_and_claims_cannot_drift(self):
        paths = [
            ("source", "current", "W_A", 0),
            ("source", "reset", "Z_4", 0),
            ("target", "roles", "current", "authoritative", "Z_4", 0),
            ("source_reference_reads", "reset", "current", 0),
            ("carrier_archive", "source_edge_ids", 0),
            ("carrier_archive", "history_content", "content", 0),
            ("request", "history_policy", "candidate", "information_loss"),
            ("request", "history_policy", "carrier", "information_loss"),
            ("target", "descriptor", "read_weights"),
            ("receipt_expectations", "carrier", "target_history_digest"),
            ("receipt_expectations", "time"),
            ("numerical_scope", "native_runtime_executed"),
            ("side_tool_provenance", 5, "support_disposition"),
            ("domain_certificates", "target", "source_frobenius_upper"),
        ]
        for path in paths:
            changed = deepcopy(self.record)
            item = changed
            for key in path[:-1]:
                item = item[key]
            v = item[path[-1]]
            item[path[-1]] = v + 2**-20 if type(v) in (int, float) else "forged"
            changed.pop("record_digest")
            changed["record_digest"] = oracle.digest(changed)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "drift"):
                oracle.validate(
                    changed, self.expected, numerical_checks=False, gates=False
                )

    def test_all_named_effects_exceed_composed_errors_and_ULPs(self):
        controls = oracle.effects(self.record)
        self.assertEqual(len(controls), 24)
        self.assertGreater(min(c["minimum_margin_ratio"] for c in controls), 1)
        self.assertEqual(
            {c["effect"] for c in controls},
            {
                "geometry",
                "feedback",
                "written_carrier_next_current",
                "next_geometry",
                "same_source_carrier",
                "same_source_next_current",
                "stale_resource_writer_W",
                "stale_resource_writer_next_current",
                "baseline_current_writer_W",
                "baseline_current_writer_next_current",
                "next_current_consumes_written_W",
            },
        )
        self.assertEqual(
            sum(c["effect"] == "geometry" for c in controls), 2
        )  # source only; zero target Z has no geometry effect

    def test_exact_G2_G3_required_without_new_public_support(self):
        from pygrc.models.grc_v4_profile import list_supported_profiles

        supported = list_supported_profiles()
        self.assertIn(oracle.A_G2, supported)
        for name in ("source", "target"):
            self.assertNotIn(
                self.record[name]["reference"]["profile"]["complete_profile_id"],
                supported,
            )
        with (
            patch.object(
                oracle.admission,
                "accepted",
                return_value={"accepted_generic_runtime_support": []},
            ),
            self.assertRaisesRegex(ValueError, "A_PC G2 absent"),
        ):
            oracle.validate(self.record, self.expected, numerical_checks=False)

    def test_producer_is_independent_of_native_numerics_and_event_allocation(self):
        names = [
            "grc_v4_candidate_a.CandidateACurrent",
            "grc_v4_candidate_a.CandidateAWriter",
            "grc_v4_realizations.CandidateAOSPass",
            "grc_v4_ci.CandidateCIRoot",
            "grc_v4_pc.CandidatePCRead",
            "grc_v4_pc.PCEnvelopeCertificate",
            "grc_v4_pc.scalar_zoh",
            "grc_v4_pc.ProvisionalCandidatePCStep",
            "grc_9_v4_expansion.GRC9V4ExpansionPlan",
            "grc_9_v4_topology.GRC9V4RowDifferential.evaluate",
        ]
        with ExitStack() as stack:
            for name in names:
                stack.enter_context(
                    patch(
                        "pygrc.models." + name,
                        side_effect=AssertionError("native numerical dependency"),
                    )
                )
            self.assertEqual(
                canonical_json_bytes(oracle.build()),
                canonical_json_bytes(self.expected),
            )


if __name__ == "__main__":
    unittest.main()
