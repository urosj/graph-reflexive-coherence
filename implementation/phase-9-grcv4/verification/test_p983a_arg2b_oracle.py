"""A_RG2b oracle pressure: full chains, W stages, bounds and independent laws."""

from __future__ import annotations

import json
import math
import sys
import unittest
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import verify_p983a_arg2b_oracle as o
from test_p980_rg_implementation_review import DecimalEquations

from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9SparkPolicy, GRC9V4CandidateDetection
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph, GRC9V4PostbeatRows
from pygrc.models.grc_v4_codec import payload_identity
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_profile import list_supported_profiles
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState


class ARGOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((o.ROOT / o.RECORD).read_text())
        cls.report = {}

    def operands(self, role="reset"):
        r = self.record
        return (
            r["target"]["port_graph"],
            deepcopy(r["target"]["roles"][role]["authoritative"]),
            deepcopy(r["continuation"][role][0]),
        )

    def test_rebuild_independent_of_native_numerics_and_event_allocator(self):
        before = list_supported_profiles()
        with ExitStack() as stack:
            for name in (
                "pygrc.models.grc_v4_candidate_a.CandidateACurrent",
                "pygrc.models.grc_v4_rg2b.CandidateRG2bSection",
                "pygrc.models.grc_v4_rg2b.ProvisionalCandidateRG2bStep",
                "pygrc.models.grc_9_v4_rg2b.section",
                "pygrc.models.grc_9_v4_topology.GRC9V4PostbeatRows.evaluate",
                "pygrc.models.grc_9_v4_expansion.GRC9V4ExpansionPlan.__post_init__",
            ):
                stack.enter_context(
                    patch(
                        name,
                        side_effect=AssertionError(
                            "native numerical/allocator oracle dependency"
                        ),
                    )
                )
            rebuilt = o.build()
        o.validate(self.record, rebuilt, numerical_checks=False)
        self.assertEqual(list_supported_profiles(), before)

    def test_all_25_intervals_and_continuations(self):
        certs = o.validate(self.record, self.record)
        self.assertEqual(len(certs), 25)
        for role in ("current", "reset"):
            rows = self.record["continuation"][role]
            self.assertEqual(len(rows), 11)
            for row in rows[:10]:
                self.assertGreater(min(row["C"]), 0)
                self.assertLess(max(row["C"]), 4)
                self.assertLess(abs(sum(map(Q, row["C"])) - Q(30.140625)), Q(1, 2**40))
                o.numerical.physical_input(o.vector(row["C"]), o.vector(row["W_A"]))
        self.assertEqual(
            self.record["source"]["reset"], self.record["initial"]["reset"]
        )

    def test_identity_allocator_and_candidate_match(self):
        r = self.record
        for key in ("source", "target"):
            p = r[key]
            ref = GRCV4ReferenceGeometry.from_payload(p["reference"])
            self.assertEqual(ref.graph.port_graph.to_payload(), p["port_graph"])
            self.assertEqual(ref.profile.identity_payload.profile_family_id, "A_RG2b")
            self.assertEqual(
                ref.profile.params_resolved.candidate.descriptor_backend_id,
                o.common.descriptor_id(p["port_graph"]),
            )
            self.assertEqual(
                ref.profile.params_resolved.realization.extension_evaluator_id,
                o.EXTENSION,
            )
            for field, schema in (
                ("scientific", "scientific_state_payload"),
                ("reset", "grc9v4_reset_payload"),
            ):
                self.assertEqual(
                    payload_identity(schema, p[field + "_payload"]),
                    p[field + "_digest"],
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
        s = r["source"]["current"]
        rows = GRC9V4PostbeatRows(
            graph,
            GRCV4ReferenceGeometry.from_payload(r["source"]["reference"]).profile,
            GRCV4AuthoritativeState(s["C"], s["W_A"], None),
            tuple(r["source_reference_reads"]["current"]["current"]),
            1,
            -1,
        )
        np.testing.assert_allclose(
            rows.evaluate()[-1].gradient,
            r["candidate_detection"]["source_gradient"],
            rtol=0,
            atol=2**-48,
        )
        detection = GRC9V4CandidateDetection(
            rows, GRC9SparkPolicy.from_payload(r["specialization"]["resolved"]["spark"])
        )
        self.assertEqual(list(detection.candidate_node_ids()), ["source-s"])

    def test_exact_resource_columns_W_lineage_and_absent_carrier(self):
        r = self.record
        old = [e["edge_id"] for e in r["source"]["port_graph"]["edges"]]
        new = [e["edge_id"] for e in r["target"]["port_graph"]["edges"]]
        nodes = r["target"]["port_graph"]["live_node_ids"]
        for role in ("current", "reset"):
            src = r["source"][role]
            target = r["target"]["roles"][role]
            wm = dict(zip(new, target["authoritative"]["W_A"], strict=True))
            self.assertEqual([wm[k] for k in old], src["W_A"])
            self.assertEqual([wm[k] for k in new if k not in old], [1.0] * 7)
            jm = dict(zip(new, target["incoming_reference_current"], strict=True))
            self.assertEqual(
                [jm[k] for k in old], r["source_reference_reads"][role]["current"]
            )
            self.assertEqual([jm[k] for k in new if k not in old], [0.0] * 7)
            cm = dict(zip(nodes, target["authoritative"]["C"], strict=True))
            center = Q(src["C"][-1])
            for i, f in enumerate((Q(1, 2), Q(1, 4), Q(1, 4)), 1):
                self.assertEqual(Q(cm[r["event_id"] + f"/satellite/{i}"]), center * f)
            self.assertEqual(
                sum(map(Q, target["authoritative"]["C"])), sum(map(Q, src["C"]))
            )
            self.assertIsNone(target["authoritative"]["Z_4"])
        rec = r["receipt_expectations"]
        self.assertEqual(rec["information_losses"], [])
        self.assertEqual(rec["candidate"]["disposition"], "exact_transport")
        self.assertEqual(rec["carrier"]["disposition"], "not_applicable")
        self.assertEqual(rec["time"], o.DT)
        self.assertEqual(rec["step_index"], 1)

    def test_source_stage_and_reference_history_are_not_interchangeable(self):
        r = self.record
        cur = r["source"]["current"]
        self.assertEqual(
            cur, o.authority(r["source_step"]["C"], r["source_step"]["W_A"])
        )
        self.assertNotEqual(cur["W_A"], r["initial"]["current"]["W_A"])
        for key in ("current", "reset"):
            self.assertNotEqual(
                r["source_reference_reads"][key]["W_A"], r["source"][key]["W_A"]
            )
        changed = deepcopy(r)
        changed["source"]["current"]["W_A"] = r["initial"]["current"]["W_A"]
        changed["record_digest"] = o.digest(
            {k: v for k, v in changed.items() if k != "record_digest"}
        )
        with self.assertRaisesRegex(ValueError, "drift"):
            o.validate(changed, r, numerical_checks=False, gates=False)

    def test_rehashed_identity_history_and_policy_corruption(self):
        r = self.record
        for branch, key, value in (
            ("numerical_scope", "depth", 5),
            ("template", "profile_family_id", "C_RG2b"),
            ("candidate_detection", "weight_source", "initial_W"),
            ("receipt_expectations", "information_losses", ["candidate_history_loss"]),
            ("completion_proof", "K_Y", [-1, 1]),
        ):
            bad = deepcopy(r)
            bad[branch][key] = value
            bad["record_digest"] = o.digest(
                {k: v for k, v in bad.items() if k != "record_digest"}
            )
            with (
                self.subTest(branch=branch),
                self.assertRaisesRegex(ValueError, "drift"),
            ):
                o.validate(bad, r, numerical_checks=False, gates=False)

    def test_uniform_global_section_and_containment_proof(self):
        p = o.proof_record()
        self.assertEqual(p, self.record["completion_proof"])
        b, s = (
            o.proof.global_bounds("A"),
            o.proof.section_budgets(o.proof.global_bounds("A")),
        )
        self.assertLess(b["M_C"], Q(1, 4))
        self.assertLess(b["M_Y"], Q(1, 8))
        self.assertLess(s["value_radius"], o.proof.RHO)
        self.assertLess(s["image_lip"], o.proof.SECTION_LIP)
        self.assertLess(s["q_section"], 1)
        for field, value in (("A_X", Q(1)), ("M_S", Q(1)), ("B_H", Q(3))):
            with self.subTest(field=field), self.assertRaises(ValueError):
                o.proof.section_budgets(dict(b, **{field: value}))

    def test_all_returned_chain_depths_and_last_W_coordinate_reject_corruption(self):
        graph, x, out = self.operands()
        for i in range(o.DEPTH + 1):
            for field in ("x", "h"):
                bad = deepcopy(out)
                if field == "x":
                    bad["chain"][field][i][-1] += 2**-10
                else:
                    bad["chain"][field][i][-1][-1] += 2**-10
                with self.subTest(depth=i, field=field), self.assertRaises(ValueError):
                    o.check_step(graph, x["C"], x["W_A"], bad)
        for field in ("x", "h"):
            bad = deepcopy(out)
            bad["chain"][field].pop()
            with self.assertRaisesRegex(ValueError, "depth"):
                o.check_step(graph, x["C"], x["W_A"], bad)

    def test_full_output_corruption_at_the_consumer(self):
        graph, x, out = self.operands()
        for field in ("current", "baseline", "source", "H", "C", "W_A"):
            bad = deepcopy(out)
            if field in ("source", "H"):
                bad[field][-1][-1] += 2**-25
            else:
                bad[field][-1] += 2**-25
            with self.subTest(field=field), self.assertRaises(ValueError):
                o.check_step(graph, x["C"], x["W_A"], bad)

    def test_malformed_nonfinite_and_point_intended_domain_admission(self):
        graph, x, out = self.operands()
        for value in (0, -1, math.nan, math.inf):
            w = x["W_A"].copy()
            w[-1] = value
            with (
                self.subTest(value=value),
                self.assertRaises((ValueError, OverflowError)),
            ):
                o.check_step(graph, x["C"], w, out)
        c = x["C"].copy()
        c[0] = -(2**-45)
        with self.assertRaisesRegex(ValueError, "physical"):
            o.check_step(
                graph, c, x["W_A"], out, ci=o.vector(x["C"]), wi=o.vector(x["W_A"])
            )
        for field in ("current", "source", "W_A"):
            bad = deepcopy(out)
            bad[field] = bad[field][:-1]
            with self.subTest(field=field), self.assertRaises(ValueError):
                o.check_step(graph, x["C"], x["W_A"], bad)

    def test_signed_inverse_uses_the_predecessor_tail(self):
        report = o.signed_inverse(self.record)
        self.report["signed_inverse"] = report
        for row in report.values():
            self.assertLess(Q(row["first_predecessor_upper"]), 0)
        b = o.proof.global_bounds("A")
        s = o.proof.section_budgets(b)
        correct = s["inverse_lip"] * b["A_H"] * s["q_section"] ** 3 * s["value_radius"]
        self.assertEqual(Q(report["reset"]["inverse_section_tail"]), correct)

    def test_graph_specific_reconstruction_and_no_transported_section(self):
        graph, x, out = self.operands()
        bad = deepcopy(out)
        bad["chain"] = deepcopy(self.record["source_reference_reads"]["reset"]["chain"])
        with self.assertRaises(ValueError):
            o.check_step(graph, x["C"], x["W_A"], bad)
        bad = deepcopy(out)
        for i in range(1, o.DEPTH + 1):
            bad["chain"]["x"][i][-1] = 0.0
        with self.assertRaises(ValueError):
            o.check_step(graph, x["C"], x["W_A"], bad)

    def test_effects_and_complete_poststate_invariance(self):
        effects = o.effects(self.record)
        self.assertEqual(len(effects), 30)
        self.assertGreater(min(v["minimum_margin_ratio"] for v in effects), 1)
        self.report["effects"] = effects

    def test_signed_edge_reordering_and_orientation_covariance(self):
        graph, x, out = self.operands()
        m = o.model_for(graph)
        for reverse, flip in ((True, False), (False, True), (True, True)):
            order = (
                list(range(len(m.edges)))[::-1]
                if reverse
                else list(range(len(m.edges)))
            )
            new = deepcopy(graph)
            new["edges"] = [deepcopy(m.edges[i]) for i in order]
            signs = np.array(
                [-1.0 if flip and k % 2 else 1.0 for k in range(len(order))]
            )
            for k, e in enumerate(new["edges"]):
                if signs[k] < 0:
                    e["tail"], e["head"] = e["head"], e["tail"]
            w = np.array(x["W_A"])[order]
            observed = o.PaperARG(new).step(x["C"], w)
            o.check_step(new, x["C"], w, observed)
            np.testing.assert_allclose(
                observed["current"],
                np.array(out["current"])[order] * signs,
                rtol=0,
                atol=2**-40,
            )
            np.testing.assert_allclose(observed["C"], out["C"], rtol=0, atol=2**-40)
            np.testing.assert_allclose(
                observed["W_A"], np.array(out["W_A"])[order], rtol=0, atol=2**-48
            )
            np.testing.assert_allclose(
                observed["H"],
                np.array(out["H"])[np.ix_(order, order)] * np.outer(signs, signs),
                rtol=0,
                atol=2**-48,
            )

    def test_argument_only_signed_faces_and_equilibria(self):
        graph, _, _ = self.operands()
        m = o.model_for(graph)
        high = o.proof.auxiliary(m)
        n, sz = len(m.nodes), len(m.nodes) + len(m.edges)
        for level in (0.0, 3.0):
            out = o.PaperARG(graph).step(np.full(n, level), np.ones(len(m.edges)))
            self.assertEqual(out["H"], m.I.tolist())
            self.assertTrue(all(j == 0 for j in out["current"]))
            self.assertEqual(out["C"], [level] * n)
        for magnitude in (1.0, 1.2):
            query = np.array(
                [(-1.0 if i % 2 else 5.0) for i in range(n)]
                + [magnitude * (-1 if i % 2 else 1) for i in range(len(m.edges))]
            )
            chain = o.numerical.solve_chain(m, "A", query, o.DEPTH)
            o.numerical.certify_chain(high, "A", chain, o.vector(query))
            inc, src = high.increment("A", o.vector(query), high.I)
            clipped = o.vector(
                [min(5, max(-1, Q(z))) for z in query[:n]]
                + [min(1, max(-1, Q(z))) for z in query[n:]]
            )
            di, si = o.proof.literal_signed_increment(high, "A", clipped, high.I)
            for a, b in ((inc, di), (src, si)):
                self.assertTrue(
                    all(o.endpoint(v, 0) <= 0 <= o.endpoint(v, 1) for v in a - b)
                )
            self.assertEqual(query.shape, (sz,))
        # Signed C admits G > 1; clipping the exponent would change the completion.
        g = high.conductance(
            o.vector([-1] * n),
            o.vector([1] * len(m.edges)),
            o.vector([0] * len(m.edges)),
        )
        self.assertTrue(all(o.endpoint(v, 0) > 1 for v in g))

    def test_float_outliers_fail_certification_without_physical_repair(self):
        graph, _, _ = self.operands()
        m = o.model_for(graph)
        for mag in (1e16, 1e100, np.finfo(float).max):
            q = np.array(
                [mag * (-1 if i % 2 else 1) for i in range(len(m.nodes) + len(m.edges))]
            )
            with np.errstate(over="ignore", invalid="ignore"):
                chain = o.numerical.solve_chain(m, "A", q, o.DEPTH)
                with self.assertRaises(ValueError):
                    o.numerical.certify_chain(
                        o.proof.auxiliary(m), "A", chain, o.vector(q)
                    )

    def test_simplex_vertex_resource_map_can_fail_next_physical_step(self):
        r = self.record
        reports = {}
        for role in ("current", "reset"):
            graph, x, _ = self.operands(role)
            for chosen in (1, 2, 3):
                c = x["C"].copy()
                for satellite in (1, 2, 3):
                    i = graph["live_node_ids"].index(
                        r["event_id"] + f"/satellite/{satellite}"
                    )
                    c[i] = r["source"][role]["C"][-1] if satellite == chosen else 0.0
                self.assertEqual(sum(map(Q, c)), sum(map(Q, r["source"][role]["C"])))
                out = o.PaperARG(graph).step(c, x["W_A"])
                t = o.check_step(graph, c, x["W_A"], out, require_positive=False)
                negative = min(o.endpoint(z, 1) for z in t["truth"]["C"])
                self.assertLess(negative, 0)
                with self.assertRaisesRegex(ValueError, "negativity"):
                    o.check_step(graph, c, x["W_A"], out)
                reports[f"{role}_{chosen}"] = str(negative)
        self.report["simplex_vertex_negative_next_resource"] = reports

    def test_graph_corners_and_induced_matrix_norm(self):
        for n in (2, 17, 18):
            graph = o.graph_payload(
                list(range(n)),
                [
                    {
                        "edge_id": f"e{i}",
                        "kind": "boundary",
                        "tail": {"node_id": i, "port": 2},
                        "head": {"node_id": i + 1, "port": 1},
                    }
                    for i in range(n - 1)
                ],
            )
            m = o.model_for(graph)
            query = np.array(
                [4.25 if i % 2 else 0.0 for i in range(n)]
                + [0.625 if i % 2 else -0.625 for i in range(n - 1)]
            )
            chain = o.numerical.solve_chain(m, "A", query, o.DEPTH)
            if n == 18:
                with self.assertRaisesRegex(ValueError, "graph bound"):
                    o.numerical.certify_chain(
                        o.proof.auxiliary(m), "A", chain, o.vector(query)
                    )
            else:
                o.numerical.certify_chain(
                    o.proof.auxiliary(m), "A", chain, o.vector(query)
                )
        graph, x, out = self.operands()
        m = o.model_for(graph)
        bad = deepcopy(out)
        # Each allowed entry is small, but one absolute row sum exceeds rho.
        row = max(range(len(m.edges)), key=lambda i: np.count_nonzero(m.mask[i]))
        h = m.I.copy()
        for j in np.flatnonzero(m.mask[row]):
            h[row, j] += float(o.proof.RHO) / 2
            if j != row:
                h[j, row] += float(o.proof.RHO) / 2
        bad["chain"]["h"][1] = h.tolist()
        with self.assertRaisesRegex(ValueError, "global ball"):
            o.check_step(graph, x["C"], x["W_A"], bad)

    def test_K_readmission_is_not_K_minus_ordinary_entry(self):
        for ordinary, cmax, yr in ((True, 4.25, 0.625), (False, 4.5, 0.75)):
            o.chart_admitted([0, cmax], [1], ordinary=ordinary)
            with self.assertRaises(ValueError):
                o.chart_admitted(
                    [0, np.nextafter(cmax, math.inf)], [1], ordinary=ordinary
                )
            for sign in (-1, 1):
                mid = math.exp(sign * yr / 512)
                inward = np.nextafter(mid, 1.0)
                outward = np.nextafter(mid, 0.0 if sign < 0 else math.inf)
                o.chart_admitted([0, 1], [inward], ordinary=ordinary)
                with self.assertRaisesRegex(ValueError, "scaled-log"):
                    o.chart_admitted([0, 1], [outward], ordinary=ordinary)
        for c, w in (([0, 4.4], [1]), ([0, 1], [math.exp(0.7 / 512)])):
            o.chart_admitted(c, w, ordinary=False)
            with self.assertRaises(ValueError):
                o.chart_admitted(c, w, ordinary=True)
        graph = o.graph_payload(
            [0, 1],
            [
                {
                    "edge_id": "e",
                    "kind": "boundary",
                    "tail": {"node_id": 0, "port": 1},
                    "head": {"node_id": 1, "port": 1},
                }
            ],
        )
        out = o.PaperARG(graph).step([1.0, 1.0], [1.0])
        o.check_step(graph, [1.0, 1.0], [1.0], out)

    def test_independent_90_digit_complete_equations(self):
        reports = {}
        for role in ("current", "reset"):
            graph, x, out = self.operands(role)
            t = o.check_step(graph, x["C"], x["W_A"], out)
            dec = DecimalEquations(t["model"])
            mp = dec.mp
            high = o.proof.auxiliary(t["model"])
            xx = [mp.matrix(v) for v in out["chain"]["x"]]
            hh = [mp.matrix(v) for v in out["chain"]["h"]]
            count = 0
            for i in range(1, len(xx)):
                inc, source = dec.increment("A", xx[i], hh[i])
                ii, si = high.increment(
                    "A",
                    o.vector(out["chain"]["x"][i]),
                    o.IV.matrix(out["chain"]["h"][i]),
                )
                count += dec.enclosed(self, inc, ii) + dec.enclosed(self, source, si)
            xx[0] = mp.matrix(list(x["C"]) + [512 * mp.log(z) for z in x["W_A"]])
            for _ in range(16):
                for i in range(1, len(xx)):
                    inc, _ = dec.increment("A", xx[i], hh[i])
                    xx[i] = xx[i - 1] - inc
                for i in range(len(xx) - 1, 0, -1):
                    _, src = dec.increment("A", xx[i], hh[i])
                    hh[i - 1] = dec.eye + src / 2
            residual = mp.mpf(0)
            for i in range(1, len(xx)):
                inc, src = dec.increment("A", xx[i], hh[i])
                residual = max(
                    residual,
                    dec.norm(xx[i] + inc - xx[i - 1]),
                    dec.norm(hh[i - 1] - dec.eye - src / 2),
                )
            self.assertLess(residual, mp.mpf("1e-28"))
            count += dec.enclosed(self, hh[0], t["truth"]["H"])
            c, w = mp.matrix(x["C"]), mp.matrix(x["W_A"])
            j, j0, src = dec.read("A", c, w, hh[0])
            cn = c - dec.d * dec.B * j
            drive = dec.conductance(cn, w, j)
            wn = mp.matrix(
                [
                    mp.exp(
                        mp.exp(-dec.d) * mp.log(v) + (1 - mp.exp(-dec.d)) * mp.log(g)
                    )
                    for v, g in zip(w, drive)
                ]
            )
            for key, actual in (
                ("current", j),
                ("baseline", j0),
                ("source", src),
                ("C", cn),
                ("W_A", wn),
            ):
                count += dec.enclosed(self, actual, t["truth"][key])
            reports[role] = {
                "enclosed_entries": count,
                "refined_residual": float(residual),
            }
        self.report["independent_90_digit"] = reports


if __name__ == "__main__":
    if "--report" in sys.argv:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ARGOracleTests)
        )
        print(
            json.dumps(
                {
                    "tests_run": result.testsRun,
                    "failures": len(result.failures),
                    "errors": len(result.errors),
                    "observations": ARGOracleTests.report,
                },
                indent=2,
            )
        )
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main()
