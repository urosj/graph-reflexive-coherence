"""Pressure the A.1 expectations before any native A.2 implementation exists."""

import json
import math
import unittest
from copy import deepcopy
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import verify_p983a_aos_oracle as oracle

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


class AOSOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = oracle.build()
        cls.record = json.loads((oracle.ROOT / oracle.RECORD).read_text())

    def test_full_interval_comparison_and_both_role_continuation(self):
        r = self.record
        oracle.validate(r, self.expected)
        for role in ("current", "reset"):
            self.assertEqual(len(r["continuation"][role]), 11)
            source = r["source"][role]
            self.assertLess(abs(sum(map(Q, source["C"])) - Q(30.140625)), Q(1, 2**40))
            self.assertEqual(len(set(source["W_A"])), 9)
            self.assertEqual(r["target"]["roles"][role]["authoritative"]["Z_4"], None)
            for row in r["continuation"][role][:10]:
                self.assertGreater(min(row["C"]), 0)
                self.assertLess(max(row["C"]), 4)
                self.assertGreater(min(row["W_A"]), 0.99)
                self.assertLess(max(row["W_A"]), 1.001)
                self.assertLess(abs(sum(map(Q, row["C"])) - Q(30.140625)), Q(1, 2**40))
        self.assertNotEqual(r["source"]["current"]["W_A"], r["source"]["reset"]["W_A"])
        self.assertEqual(r["source"]["reset"], r["initial"]["reset"])

    def test_native_identity_and_independent_d52_topology_match_accepted_mechanics(
        self,
    ):
        r = self.record
        for name in ("source", "target"):
            part = r[name]
            ref = GRCV4ReferenceGeometry.from_payload(part["reference"])
            self.assertEqual(
                ref.profile.params_resolved.candidate.descriptor_backend_id,
                oracle.descriptor_id(part["port_graph"]),
            )
            self.assertEqual(part["descriptor"], oracle.descriptor(part["port_graph"]))
            self.assertEqual(ref.graph.port_graph.to_payload(), part["port_graph"])
            for field, schema in [
                ("scientific", "scientific_state_payload"),
                ("reset", "grc9v4_reset_payload"),
            ]:
                self.assertEqual(
                    payload_identity(schema, part[field + "_payload"]),
                    part[field + "_digest"],
                )
        graph = GRC9V4PortGraph.from_payload(r["source"]["port_graph"])
        request = GRC9V4ExpansionRequestInput.from_payload(r["request"])
        policy = GRC9ExpansionPolicy.from_payload(
            r["specialization"]["resolved"]["expansion"]
        )
        plan = GRC9V4ExpansionPlan(
            graph, r["source"]["scientific_digest"], request, policy
        )
        self.assertEqual(plan.event_id, r["event_id"])
        self.assertEqual(plan.target_graph.to_payload(), r["target"]["port_graph"])
        self.assertEqual(len(plan.target_graph.live_node_ids), 17)
        self.assertEqual(len(plan.target_graph.edges), 16)
        ref = GRCV4ReferenceGeometry.from_payload(r["source"]["reference"])
        state = r["source"]["current"]
        rows = GRC9V4PostbeatRows(
            graph,
            ref.profile,
            GRCV4AuthoritativeState(state["C"], state["W_A"], None),
            tuple(r["source_reference_reads"]["current"]["current"]),
            1,
            -1,
        )
        source = rows.evaluate()[-1]
        self.assertEqual(
            list(source.gradient), r["candidate_detection"]["source_gradient"]
        )
        self.assertEqual(
            [source.signed_hessian[i][i] for i in range(3)],
            r["candidate_detection"]["source_signed_hessian_diagonal"],
        )
        detection = GRC9V4CandidateDetection(
            rows, GRC9SparkPolicy.from_payload(r["specialization"]["resolved"]["spark"])
        )
        self.assertEqual(
            list(detection.candidate_node_ids()),
            r["candidate_detection"]["candidate_node_ids"],
        )
        self.assertFalse(r["numerical_scope"]["native_runtime_executed"])
        self.assertNotEqual(
            r["source"]["reference"]["profile"]["complete_profile_id"], oracle.A_G2
        )

    def test_exact_history_left_inverse_and_resource_charge_map(self):
        from pygrc.models.grc_v4_geometry import VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation

        r = self.record
        source, target = r["source"]["port_graph"], r["target"]["port_graph"]
        old = [e["edge_id"] for e in source["edges"]]
        new = [e["edge_id"] for e in target["edges"]]
        embedding = [[int(e == s) for s in old] for e in new]
        projection = [[int(e == s) for e in new] for s in old]
        product = [
            [sum(x * y for x, y in zip(row, col)) for col in zip(*embedding)]
            for row in projection
        ]
        self.assertEqual(product, [[int(i == j) for j in range(9)] for i in range(9)])
        for role in ("current", "reset"):
            before = r["source"][role]
            after = r["target"]["roles"][role]
            ws = dict(zip(new, after["authoritative"]["W_A"]))
            self.assertEqual([ws[e] for e in old], before["W_A"])
            self.assertEqual([ws[e] for e in new if e not in old], [1.0] * 7)
            refs = dict(zip(new, after["incoming_reference_current"]))
            self.assertEqual(
                [refs[e] for e in old], r["source_reference_reads"][role]["current"]
            )
            self.assertEqual([refs[e] for e in new if e not in old], [0.0] * 7)
            currents = dict(zip(new, r["continuation"][role][0]["current"]))
            self.assertTrue(all(currents[e] != 0 for e in new if e not in old))
            cb, ca = before["C"], after["authoritative"]["C"]
            self.assertEqual(sum(map(Q, ca)), sum(map(Q, cb)))
        receipts = r["receipt_expectations"]
        self.assertEqual(receipts["information_losses"], [])
        self.assertEqual(receipts["candidate"]["disposition"], "exact_transport")
        self.assertIsNone(receipts["carrier"]["source_history_digest"])
        self.assertIsNone(receipts["carrier"]["target_history_digest"])
        ref = GRCV4ReferenceGeometry.from_payload(r["target"]["reference"])
        for role in ("current", "reset"):
            result = ChargeEvaluation(
                VertexScalar(
                    ref.graph, tuple(r["target"]["roles"][role]["authoritative"]["C"])
                ),
                30.140625,
                ref.profile,
            )
            self.assertEqual(result.receipt_values(), receipts["role_charge"][role])
            self.assertTrue(result.admitted)

    def test_point_oracle_detaches_graph_and_preserves_operand_arrays(self):
        graph = deepcopy(self.record["source"]["port_graph"])
        state = deepcopy(self.record["source"]["current"])
        saved = deepcopy(state)
        paper = oracle.PaperAOS(graph)
        expected = paper.step(state["C"], state["W_A"])
        graph["live_node_ids"][0] = "changed"
        graph["edges"][0]["tail"]["port"] = 9
        self.assertEqual(paper.step(state["C"], state["W_A"]), expected)
        self.assertEqual(state, saved)

    def test_real_target_split_failure_has_a_lower_bound_and_admitted_source(self):
        self.assertGreater(oracle.check_negative(self.record), Q(oracle.SPLIT))
        negative = deepcopy(self.record)
        negative["rejection_expectations"]["target_split"]["mapped_target_role"] = (
            negative["target"]["roles"]["current"]["authoritative"]
        )
        with self.assertRaisesRegex(ValueError, "failure not certified"):
            oracle.check_negative(negative)

    def test_wls_descriptor_cannot_silently_stand_in_for_native_fixed_rows(self):
        from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
        from pygrc.models.grc_v4_profile import list_supported_profiles

        supported = list_supported_profiles()
        self.assertIn(oracle.A_G2, supported)
        for name in ("source", "target"):
            part = self.record[name]
            with self.assertRaises(ValueError):
                CandidateADifferentialReference.from_payload(part["descriptor"])
            self.assertNotIn(
                part["reference"]["profile"]["complete_profile_id"], supported
            )

    def test_rehashed_policy_graph_role_reference_and_stage_tampering_rejects(self):
        r = self.record
        paths = [
            ("source", "current", "W_A", 0),
            ("source", "reset", "W_A", 0),
            ("source_reference_reads", "current", "current", 0),
            ("target", "roles", "current", "incoming_reference_current", 0),
            ("target", "roles", "reset", "authoritative", "W_A", 0),
            ("target", "roles", "current", "authoritative", "C", 0),
            ("continuation", "reset", 0, "W_A", 0),
            ("target", "descriptor", "read_weights"),
            ("request", "history_policy", "candidate", "disposition"),
            ("request", "history_policy", "candidate", "information_loss"),
            ("receipt_expectations", "carrier", "source_history_digest"),
            ("numerical_scope", "native_runtime_executed"),
        ]
        for path in paths:
            changed = deepcopy(r)
            item = changed
            for key in path[:-1]:
                item = item[key]
            value = item[path[-1]]
            item[path[-1]] = value + 2**-20 if type(value) in (int, float) else "forged"
            changed.pop("record_digest")
            changed["record_digest"] = oracle.digest(changed)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "drift"):
                oracle.validate(changed, self.expected, numerical=False, gates=False)
        for role in ("current", "reset"):
            changed = deepcopy(r)
            w = changed["target"]["roles"][role]["authoritative"]["W_A"]
            w[-1], w[-2] = w[-2], w[-1]
            with self.assertRaisesRegex(ValueError, "drift"):
                oracle.validate(changed, self.expected, numerical=False, gates=False)

    def test_point_producer_mutations_are_checked_against_saved_entry_operands(self):
        r = self.record
        graph = r["target"]["port_graph"]
        for role in ("current", "reset"):
            original = r["target"]["roles"][role]["authoritative"]
            for key in ("C", "W_A", "current", "baseline", "H", "regenerated"):
                state = deepcopy(original)
                snapshot = deepcopy(state)
                result = oracle.PaperAOS(graph).step(state["C"], state["W_A"])
                if key in ("H", "regenerated"):
                    result[key][0][0] += 2**-20
                else:
                    result[key][0] += 2**-20
                with (
                    self.subTest(role=role, key=key),
                    self.assertRaisesRegex(ValueError, "entry-referenced"),
                ):
                    oracle.check_step(
                        graph, tuple(snapshot["C"]), tuple(snapshot["W_A"]), result
                    )
                self.assertEqual(state, original)
        old = oracle.PaperAOS.write

        def corrupt(writer, c, w, j):
            result = old(writer, c, w, j)
            result[0] += writer.mp.mpf(2) ** -20
            return result

        original = r["target"]["roles"]["current"]["authoritative"]
        with patch.object(oracle.PaperAOS, "write", corrupt):
            result = oracle.PaperAOS(graph).step(original["C"], original["W_A"])
        with self.assertRaisesRegex(ValueError, "entry-referenced W_A"):
            oracle.check_step(graph, original["C"], original["W_A"], result)

    def test_wrong_reference_stage_and_writer_operands_are_detectable(self):
        r = self.record
        # Source reference must be freshly reconstructed at event-entry C/W.
        stale = deepcopy(r["source_reference_reads"]["current"])
        stale["current"] = r["source_step"]["current"]
        state = r["source"]["current"]
        with self.assertRaisesRegex(ValueError, "entry-referenced current"):
            oracle.check_step(
                r["source"]["port_graph"], state["C"], state["W_A"], stale
            )
        graph = r["target"]["port_graph"]
        paper = oracle.PaperAOS(graph)
        for role in ("current", "reset"):
            state = r["target"]["roles"][role]["authoritative"]
            c, w = state["C"], state["W_A"]
            pred = paper.read(c, w)
            correct = paper.read(c, w, paper.I + pred["source"] / 2)
            fresh = (
                paper.mp.matrix(c)
                - paper.mp.mpf(oracle.DT) * paper.B * correct["current"]
            )
            expected = paper.write(fresh, w, correct["current"])
            high = oracle.IntervalRows(
                oracle.StagedRows(graph["live_node_ids"], graph["edges"], oracle.PARAMS)
            )
            cn, wn, stages = high.ordinary_os("A", oracle.vector(c), oracle.vector(w))
            good = np.array(list(map(float, expected)))
            good_error = oracle.full_error(good, wn)
            for wrong, truth in (
                (
                    paper.write(c, w, correct["current"]),
                    high.write(oracle.vector(c), oracle.vector(w), stages["read"]["J"]),
                ),
                (
                    paper.write(fresh, w, correct["baseline"]),
                    high.write(cn, oracle.vector(w), stages["read"]["baseline"]),
                ),
            ):
                wrong = np.array(list(map(float, wrong)))
                error = max(abs(Q(float(x)) - Q(float(y))) for x, y in zip(good, wrong))
                allowance = 4 * (
                    good_error + oracle.full_error(wrong, truth)
                ) + 8 * max(Q(math.ulp(float(x))) for x in (*good, *wrong))
                self.assertGreater(error, allowance)

    def test_oracle_equations_covary_under_edge_reordering_and_reversal(self):
        r = self.record
        for label in ("source", "target"):
            graph = r[label]["port_graph"]
            state = (
                r["source"]["current"]
                if label == "source"
                else r["target"]["roles"]["current"]["authoritative"]
            )
            expected = oracle.PaperAOS(graph).step(state["C"], state["W_A"])
            size = len(graph["edges"])
            for offset in (0, 1, 3):
                order = list(range(offset, size)) + list(range(offset))
                changed = deepcopy(graph)
                changed["edges"] = [deepcopy(graph["edges"][i]) for i in order]
                signs = [-1 if i % 2 else 1 for i in order]
                for edge, sign in zip(changed["edges"], signs):
                    if sign == -1:
                        edge["tail"], edge["head"] = edge["head"], edge["tail"]
                actual = oracle.PaperAOS(changed).step(
                    state["C"], [state["W_A"][i] for i in order]
                )
                np.testing.assert_allclose(
                    actual["C"], expected["C"], rtol=0, atol=2**-48
                )
                np.testing.assert_allclose(
                    actual["W_A"],
                    [expected["W_A"][i] for i in order],
                    rtol=0,
                    atol=2**-48,
                )
                np.testing.assert_allclose(
                    actual["current"],
                    [s * expected["current"][i] for s, i in zip(signs, order)],
                    rtol=0,
                    atol=2**-40,
                )

    def test_geometry_readback_and_written_history_effects_exceed_full_error(self):
        from test_p980_os_effect_witness import separation

        r = self.record
        for label in ("source", "target"):
            graph = r[label]["port_graph"]
            paper = oracle.PaperAOS(graph)
            high = oracle.IntervalRows(
                oracle.StagedRows(graph["live_node_ids"], graph["edges"], oracle.PARAMS)
            )
            for role in ("current", "reset"):
                state = (
                    r["source"][role]
                    if label == "source"
                    else r["target"]["roles"][role]["authoritative"]
                )
                c, w = state["C"], state["W_A"]
                pred = paper.read(c, w)
                h = paper.I + pred["source"] / 2
                enabled = paper.read(c, w, h)
                ci, wi = oracle.vector(c), oracle.vector(w)
                hi = high.I + high.read("A", ci, wi, high.I)["source"] / 2
                truth = high.read("A", ci, wi, hi)
                for control in ({"geometry": False}, {"feedback": False}):
                    comparison = paper.read(c, w, h, **control)
                    alternate = high.read("A", ci, wi, hi, **control)
                    result = separation(
                        list(map(float, enabled["current"])),
                        list(map(float, comparison["current"])),
                        truth["J"],
                        alternate["J"],
                    )
                    self.assertGreater(result["minimum_margin_ratio"], 1)
                if label == "target":
                    step = paper.step(c, w)
                    new = paper.step(step["C"], step["W_A"])
                    held = paper.step(step["C"], w)
                    # Match final C and compare only retained-W consumption.
                    ci = oracle.vector(step["C"])
                    a = high.ordinary_os("A", ci, oracle.vector(step["W_A"]))[2][
                        "read"
                    ]["J"]
                    b = high.ordinary_os("A", ci, wi)[2]["read"]["J"]
                    result = separation(new["current"], held["current"], a, b)
                    self.assertGreater(result["minimum_margin_ratio"], 1)

    def test_g2_g3_scope_and_no_native_numerical_producer_dependencies(self):
        with (
            patch.object(
                oracle.admission, "accepted", side_effect=ValueError("G3 missing")
            ),
            self.assertRaisesRegex(ValueError, "G3 missing"),
        ):
            oracle.validate(self.record, self.expected, numerical=False)
        with (
            patch.object(
                oracle.admission,
                "accepted",
                return_value={"accepted_generic_runtime_support": []},
            ),
            self.assertRaisesRegex(ValueError, "A_OS G2 absent"),
        ):
            oracle.validate(self.record, self.expected, numerical=False)
        # Fail if an independent expectation starts using a production evaluator.
        with (
            patch(
                "pygrc.models.grc_v4_candidate_a.CandidateACurrent",
                side_effect=AssertionError("runtime A read"),
            ),
            patch(
                "pygrc.models.grc_v4_realizations.CandidateAOSPass",
                side_effect=AssertionError("runtime OS pass"),
            ),
            patch(
                "pygrc.models.grc_9_v4_expansion.GRC9V4ExpansionPlan",
                side_effect=AssertionError("runtime plan"),
            ),
            patch(
                "pygrc.models.grc_9_v4_topology.GRC9V4RowDifferential.evaluate",
                side_effect=AssertionError("runtime rows"),
            ),
        ):
            self.assertEqual(
                canonical_json_bytes(oracle.build()),
                canonical_json_bytes(self.expected),
            )


if __name__ == "__main__":
    unittest.main()
