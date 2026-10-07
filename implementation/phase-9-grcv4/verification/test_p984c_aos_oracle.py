"""Focused boundary A_OS oracle tests, with no native numerical producers."""

from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984c_aos_oracle as oracle


class BoundaryOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = oracle.make_manifest()

    def test_complete_population_lineage_and_both_roles(self):
        m = self.manifest
        self.assertEqual(len(m["cases"]), 32)
        self.assertEqual(len(m["exact_reuse"]), 2)
        self.assertFalse(m["native_runtime_executed"])
        source = m["shared"]["source"]
        edges = [e["edge_id"] for e in source["port_graph"]["edges"]]
        for case in m["cases"]:
            target = case["target"]
            self.assertNotEqual(target["roles"]["current"], target["roles"]["reset"])
            self.assertEqual(case["request"]["resource_distribution"], [0.5, 0.25, 0.25])
            ids = [e["edge_id"] for e in target["port_graph"]["edges"]]
            for role in oracle.previous.ROLES:
                state = target["roles"][role]["authoritative"]
                weights = dict(zip(ids, state["W_A"], strict=True))
                currents = dict(zip(ids, target["roles"][role]["incoming_reference_current"], strict=True))
                self.assertEqual([weights[e] for e in edges], source[role]["W_A"])
                self.assertEqual([currents[e] for e in edges], m["shared"]["source_reference_reads"][role]["current"])
                self.assertTrue(all(weights[e] == 1 and currents[e] == 0 for e in ids if e not in edges))
                self.assertEqual(sum(map(Q, state["C"])), sum(map(Q, source[role]["C"])))
                self.assertIsNone(state["Z_4"])

    def test_resealed_scope_request_history_and_budget_rejected(self):
        for kind in ("case", "phase", "history", "budget", "reuse"):
            value = deepcopy(self.manifest)
            if kind == "case":
                value["cases"].pop()
            elif kind == "phase":
                value["cases"][0]["request"]["growth_phase"] = 3
            elif kind == "history":
                value["cases"][0]["target"]["roles"]["reset"]["authoritative"]["W_A"][0] += 0.25
            elif kind == "budget":
                value["cases"][0]["comparison"]["budgets"]["H"] = "1"
            else:
                value["exact_reuse"][0]["previous_case_id"] = "foreign"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                oracle.check_manifest(oracle.base.seal(value))

    def test_new_two_remainder_equations_with_native_producers_disabled(self):
        with ExitStack() as stack:
            for name in oracle.PRODUCERS:
                stack.enter_context(patch(name, side_effect=AssertionError("native producer")))
            m = oracle.make_manifest()
            for case in m["cases"]:
                if case["request"]["target_effective_degree"] != 38:
                    continue
                paper = oracle.aos.PaperAOS(case["target"]["port_graph"])
                for role in oracle.previous.ROLES:
                    row = oracle.previous.evaluate(paper, case["target"]["roles"][role]["authoritative"], "target_continuation", role, 1)
                    self.assertGreater(Q(row["certificate"]["C_lower"]), 0)
                    self.assertGreater(Q(row["certificate"]["W_lower"]), 0)

    def test_wrong_stage_and_writer_fail_full_formula_certificate(self):
        case = next(c for c in self.manifest["cases"] if "D38-E1-P1" in c["case_id"])
        graph = case["target"]["port_graph"]
        for role in oracle.previous.ROLES:
            state = case["target"]["roles"][role]["authoritative"]
            row = oracle.previous.evaluate(oracle.aos.PaperAOS(graph), state, "target_continuation", role, 1)
            for field in ("current", "W_A", "H", "corrector_readback"):
                output = deepcopy(row["output"])
                if field == "current":
                    output[field] = output["predictor_current"]
                elif field == "W_A":
                    output[field] = list(state["W_A"])
                elif field == "H":
                    n = len(graph["edges"])
                    output[field] = [[float(i == j) for j in range(n)] for i in range(n)]
                else:
                    output[field] = [0.0] * len(output[field])
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    oracle.previous.interval_certificate(graph, state["C"], state["W_A"], output)

    def test_retained_roster_and_flags_fail_closed(self):
        if not (oracle.base.ROOT / oracle.RESULTS).exists():
            self.skipTest("oracle result not yet retained")
        record = oracle.base.read(oracle.RESULTS)
        summary = oracle.validate(self.manifest, record)
        self.assertEqual(summary["oracle_cases_passed"], 32)
        self.assertEqual(summary["runtime_cells_closed"], 0)
        for kind in ("runtime", "acceptance", "case", "reuse"):
            value = deepcopy(record)
            if kind == "runtime":
                value["native_runtime_executed"] = True
            elif kind == "acceptance":
                value["user_accepted"] = True
            elif kind == "case":
                value["cases"].pop()
            else:
                value["reuse"][0]["previous_row_digest"] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                oracle.validate(self.manifest, oracle.base.seal(value))


if __name__ == "__main__":
    unittest.main()
