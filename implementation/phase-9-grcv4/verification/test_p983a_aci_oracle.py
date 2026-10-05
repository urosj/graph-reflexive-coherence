"""Pressure the A.1 expectations before any native A.2 implementation exists."""

import json
import unittest
from copy import deepcopy
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import verify_p983a_aci_oracle as oracle

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


class ACIOracleTests(unittest.TestCase):
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
                oracle.common.descriptor_id(part["port_graph"]),
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

    def test_declared_domain_and_profile_are_exact_and_not_OS_or_carrier(self):
        r = self.record
        for name in ("source", "target"):
            ref = GRCV4ReferenceGeometry.from_payload(r[name]["reference"])
            self.assertEqual(ref.profile.identity_payload.profile_family_id, "A_CI")
            params = ref.profile.params_resolved.to_payload()["realization"]
            self.assertEqual(
                params["contraction_domain_id"],
                "ci_reference_frobenius_ball_v1:" + float(2**-20).hex(),
            )
            self.assertEqual(params["tolerance"], 2**-44)
            for cert in r["domain_certificates"][name].values():
                self.assertLess(Q(cert["displacement_upper"]), Q(oracle.RADIUS))
                self.assertLess(Q(cert["contraction_upper"]), 1)
                self.assertGreater(Q(cert["current_margin_lower"]), Q(1, 2))
                self.assertEqual(cert["floor_chart"], "inactive")
        self.assertNotIn("regenerated", r["source_step"])

    def test_domain_outliers_do_not_turn_a_failed_bound_into_admission(self):
        graph = self.record["target"]["port_graph"]
        state = self.record["target"]["roles"]["current"]["authoritative"]
        c, w = state["C"], state["W_A"]
        for radius in (Q(0), Q(-1), Q(1), Q(2), Q(1, 2**50)):
            with self.subTest(radius=radius), self.assertRaises(ValueError):
                oracle.frobenius_domain(graph, c, w, radius)
        for weights in ([0] * len(w), [-1] * len(w), w[:-1]):
            with self.assertRaises(ValueError):
                oracle.frobenius_domain(graph, c, weights)
        with self.assertRaisesRegex(ValueError, "floor"):
            oracle.frobenius_domain(graph, [10**6 * x for x in c], w)

    def test_negative_proves_image_exit_with_regular_current_and_admitted_source(self):
        cert = oracle.check_negative(self.record)
        self.assertGreater(
            Q(cert["image_frobenius_squared_lower"]), Q(cert["radius_squared"])
        )
        self.assertGreater(Q(cert["current_regularity_lower"]), Q(1, 2))
        negative = deepcopy(self.record)
        fixture = negative["rejection_expectations"]["target_domain"]
        fixture["mapped_target_role"] = negative["target"]["roles"]["current"][
            "authoritative"
        ]
        with self.assertRaisesRegex(ValueError, "map mismatch"):
            oracle.check_negative(negative)
        fixture["source_role"] = negative["source"]["current"]
        with self.assertRaisesRegex(ValueError, "exit not certified"):
            oracle.check_negative(negative)

    def test_point_oracle_detaches_graph_and_preserves_operand_arrays(self):
        graph = deepcopy(self.record["source"]["port_graph"])
        state = deepcopy(self.record["source"]["current"])
        saved = deepcopy(state)
        paper = oracle.PaperACI(graph)
        expected = paper.step(state["C"], state["W_A"])
        graph["live_node_ids"][0] = "changed"
        graph["edges"][0]["tail"]["port"] = 9
        self.assertEqual(paper.step(state["C"], state["W_A"]), expected)
        self.assertEqual(state, saved)

    def test_wls_cannot_replace_the_declared_fixed_row_backend(self):
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

    def test_rehashed_identity_stage_history_domain_and_provenance_tampering(self):
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
            ("domain_certificates", "target", "reset", "radius"),
            ("side_tool_provenance", 5, "support_disposition"),
        ]
        for path in paths:
            changed = deepcopy(self.record)
            item = changed
            for key in path[:-1]:
                item = item[key]
            value = item[path[-1]]
            item[path[-1]] = value + 2**-20 if type(value) in (int, float) else "forged"
            changed.pop("record_digest")
            changed["record_digest"] = oracle.digest(changed)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "drift"):
                oracle.validate(
                    changed, self.expected, numerical_checks=False, gates=False
                )

    def test_corrupt_producer_outputs_are_rejected_against_saved_operands(self):
        r = self.record
        graph = r["target"]["port_graph"]
        for role in ("current", "reset"):
            state = r["target"]["roles"][role]["authoritative"]
            saved_c, saved_w = tuple(state["C"]), tuple(state["W_A"])
            good = oracle.PaperACI(graph).step(saved_c, saved_w)
            for field in ("C", "W_A", "current", "baseline", "H", "source"):
                result = deepcopy(good)
                if field in ("H", "source"):
                    result[field][0][0] += 2**-20
                else:
                    result[field][0] += 2**-20
                with (
                    self.subTest(role=role, field=field),
                    self.assertRaises(ValueError),
                ):
                    oracle.check_step(graph, saved_c, saved_w, result)
            self.assertEqual(tuple(state["C"]), saved_c)
            self.assertEqual(tuple(state["W_A"]), saved_w)
        old = oracle.PaperACI.write

        def corrupt(writer, c, w, j):
            result = old(writer, c, w, j)
            result[0] += writer.mp.mpf(2) ** -20
            return result

        with patch.object(oracle.PaperACI, "write", corrupt):
            result = oracle.PaperACI(graph).step(saved_c, saved_w)
        with self.assertRaisesRegex(ValueError, "entry-referenced W_A"):
            oracle.check_step(graph, saved_c, saved_w, result)

    def test_wrong_entry_current_and_reference_geometry_cannot_supply_CI_root(self):
        r = self.record
        state = r["source"]["current"]
        stale = deepcopy(r["source_reference_reads"]["current"])
        stale["current"] = r["source_step"]["current"]
        with self.assertRaisesRegex(ValueError, "joint residual"):
            oracle.check_step(
                r["source"]["port_graph"], state["C"], state["W_A"], stale
            )
        graph = r["target"]["port_graph"]
        for role in ("current", "reset"):
            state = r["target"]["roles"][role]["authoritative"]
            wrong = deepcopy(r["continuation"][role][0])
            wrong["H"] = np.eye(len(state["W_A"])).tolist()
            with self.assertRaisesRegex(ValueError, "joint residual"):
                oracle.check_step(graph, state["C"], state["W_A"], wrong)

    def test_joint_residual_gate_is_stricter_than_output_comparison_allowance(self):
        r = self.record
        graph = r["target"]["port_graph"]
        state = r["target"]["roles"]["current"]["authoritative"]
        altered = deepcopy(r["continuation"]["current"][0])
        altered["current"][0] += 2**-42
        # This perturbation fits the 2^-40 oracle current-comparison allowance,
        # but is too large for the independently checked 2^-44 joint root norm.
        with self.assertRaisesRegex(ValueError, "joint residual"):
            oracle.check_step(graph, state["C"], state["W_A"], altered)

    def test_signed_reordering_covaries_vectors_and_both_geometry_tensors(self):
        r = self.record
        for label in ("source", "target"):
            graph = r[label]["port_graph"]
            state = (
                r["source"]["current"]
                if label == "source"
                else r["target"]["roles"]["current"]["authoritative"]
            )
            expected = oracle.PaperACI(graph).step(state["C"], state["W_A"])
            size = len(graph["edges"])
            for offset in (0, 1, 3):
                order = list(range(offset, size)) + list(range(offset))
                changed = deepcopy(graph)
                changed["edges"] = [deepcopy(graph["edges"][i]) for i in order]
                signs = [-1 if i % 2 else 1 for i in order]
                for edge, sign in zip(changed["edges"], signs):
                    if sign == -1:
                        edge["tail"], edge["head"] = edge["head"], edge["tail"]
                actual = oracle.PaperACI(changed).step(
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
                for field in ("current", "baseline"):
                    np.testing.assert_allclose(
                        actual[field],
                        [s * expected[field][i] for s, i in zip(signs, order)],
                        rtol=0,
                        atol=2**-40,
                    )
                for field in ("H", "source"):
                    tensor = [
                        [s * t * expected[field][i][j] for t, j in zip(signs, order)]
                        for s, i in zip(signs, order)
                    ]
                    np.testing.assert_allclose(
                        actual[field], tensor, rtol=0, atol=2**-48
                    )

    def test_all_effect_controls_exceed_actual_full_error_and_ULP(self):
        controls = oracle.effects(self.record)
        self.assertEqual(len(controls), 18)
        self.assertGreater(min(c["minimum_margin_ratio"] for c in controls), 1)
        self.assertEqual(
            {c["effect"] for c in controls},
            {
                "geometry",
                "feedback",
                "entire_root_source_off",
                "stale_resource_writer",
                "baseline_current_writer",
                "next_root_consumes_written_W",
            },
        )

    def test_G2_G3_and_native_numerical_independence(self):
        with (
            patch.object(
                oracle.admission, "accepted", side_effect=ValueError("G3 missing")
            ),
            self.assertRaisesRegex(ValueError, "G3 missing"),
        ):
            oracle.validate(self.record, self.expected, numerical_checks=False)
        with (
            patch.object(
                oracle.admission,
                "accepted",
                return_value={"accepted_generic_runtime_support": []},
            ),
            self.assertRaisesRegex(ValueError, "A_CI G2 absent"),
        ):
            oracle.validate(self.record, self.expected, numerical_checks=False)
        from contextlib import ExitStack

        names = [
            "grc_v4_candidate_a.CandidateACurrent",
            "grc_v4_candidate_a.CandidateAWriter",
            "grc_v4_realizations.CandidateAOSPass",
            "grc_v4_ci.CandidateCIRoot",
            "grc_v4_ci.ProvisionalCandidateCIStep",
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
