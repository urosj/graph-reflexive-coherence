"""Focused pressure for the new A_OS oracle scope, not a native campaign."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984b_aos_oracle as oracle

common, aos = oracle.common, oracle.aos


class DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = oracle.make_manifest()

    def test_exact_all_layouts_and_both_history_cells(self):
        cases = self.manifest["cases"]
        expected = common.read(common.COVERAGE)
        cells = {
            r["id"]
            for r in expected["coverage_cells"]
            if r["owner"] == "P9-8.4b" and r["family"] == "A_OS" and r["applicable"]
        }
        self.assertEqual(len(cases), 16)
        self.assertEqual(len(cells), 32)
        self.assertEqual(
            {v for c in cases for v in c["coverage_binding"]["cell_ids"]}, cells
        )
        self.assertFalse(self.manifest["native_runtime_executed"])
        self.assertFalse(self.manifest["user_accepted"])

    def test_baseline_remains_identical_and_only_phase_one_changes_shares(self):
        old = oracle.predecessor()
        for case in self.manifest["cases"]:
            request = case["request"]
            phase_one = (
                request["target_effective_degree"],
                request["growth_phase"],
            ) == (52, 1)
            self.assertEqual(
                request["resource_distribution"],
                [0.25, 0.5, 0.25] if phase_one else [0.5, 0.25, 0.25],
            )
            self.assertEqual(
                request["history_policy"], old["request"]["history_policy"]
            )
            if case["fixture_id"] == common.PINNED:
                self.assertEqual(case["target"], old["target"])
                self.assertEqual(case["event_id"], old["event_id"])
        self.assertEqual(self.manifest["shared"]["initial"], old["initial"])

    def test_all_exact_role_maps_preserve_old_history_charge_and_reference_types(self):
        source = self.manifest["shared"]["source"]
        old_ids = [e["edge_id"] for e in source["port_graph"]["edges"]]
        for case in self.manifest["cases"]:
            new_ids = [e["edge_id"] for e in case["target"]["port_graph"]["edges"]]
            self.assertEqual(
                len(case["target"]["port_graph"]["live_node_ids"]),
                9 + case["event_identity_payload"]["canonical_module_node_count"],
            )
            self.assertEqual(
                case["target"]["descriptor"]["descriptor_version"],
                "grc9v4-candidate-a-fixed-row-v1",
            )
            for role in oracle.ROLES:
                with self.subTest(case=case["case_id"], role=role):
                    target = case["target"]["roles"][role]
                    w = dict(zip(new_ids, target["authoritative"]["W_A"], strict=True))
                    j = dict(
                        zip(new_ids, target["incoming_reference_current"], strict=True)
                    )
                    self.assertEqual([w[e] for e in old_ids], source[role]["W_A"])
                    self.assertEqual(
                        [j[e] for e in old_ids],
                        self.manifest["shared"]["source_reference_reads"][role][
                            "current"
                        ],
                    )
                    self.assertTrue(
                        all(
                            w[e] == 1 and j[e] == 0 for e in new_ids if e not in old_ids
                        )
                    )
                    self.assertEqual(
                        sum(map(Q, target["authoritative"]["C"])),
                        sum(map(Q, source[role]["C"])),
                    )
                    self.assertIsNone(target["authoritative"]["Z_4"])

    def test_rehashed_missing_case_changed_request_or_budget_rejected(self):
        for field in ("case", "request", "budget", "history"):
            value = deepcopy(self.manifest)
            if field == "case":
                value["cases"].pop()
            elif field == "request":
                value["cases"][0]["request"]["module_chirality"] *= -1
            elif field == "budget":
                value["cases"][0]["comparison"]["budgets"]["W_A"] = "1"
            else:
                value["cases"][0]["target"]["roles"]["reset"]["authoritative"]["W_A"][
                    0
                ] += 0.1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "drift"):
                oracle.check_manifest(common.seal(value))

    def test_expectations_do_not_call_production_numerical_or_event_producers(self):
        with (
            patch(
                "pygrc.models.grc_v4_candidate_a.CandidateACurrent",
                side_effect=AssertionError("native current"),
            ),
            patch(
                "pygrc.models.grc_v4_realizations.CandidateAOSPass",
                side_effect=AssertionError("native OS"),
            ),
            patch(
                "pygrc.models.grc_v4_step.ProvisionalCandidateAOSStep",
                side_effect=AssertionError("native step"),
            ),
            patch(
                "pygrc.models.grc_9_v4_expansion.GRC9V4ExpansionPlan",
                side_effect=AssertionError("native allocation"),
            ),
            patch(
                "pygrc.models.grc_9_v4_lifecycle.GRC9V4AOSOperation",
                side_effect=AssertionError("native event"),
            ),
        ):
            manifest = oracle.make_manifest()
            case = manifest["cases"][0]
            graph = case["target"]["port_graph"]
            row = oracle.evaluate(
                aos.PaperAOS(graph),
                case["target"]["roles"]["current"]["authoritative"],
                "target_continuation",
                "current",
                1,
            )
            self.assertGreater(Q(row["certificate"]["C_lower"]), 0)


class NumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        case = oracle.make_manifest()["cases"][0]
        cls.graph = case["target"]["port_graph"]
        cls.state = case["target"]["roles"]["current"]["authoritative"]
        cls.row = oracle.evaluate(
            aos.PaperAOS(cls.graph), cls.state, "target_continuation", "current", 1
        )

    def test_point_errors_are_below_frozen_budgets(self):
        oracle.check_certificate(self.row["certificate"])
        self.assertEqual(
            oracle.interval_certificate(
                self.graph, self.state["C"], self.state["W_A"], self.row["output"]
            ),
            self.row["certificate"],
        )

    def test_current_history_geometry_and_nonfinite_shape_pressure(self):
        for field in oracle.LIMITS:
            output = deepcopy(self.row["output"])
            if field in ("H", "regenerated"):
                output[field][0][0] += 2**-20
            else:
                output[field][0] += 2**-20
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(ValueError, "full formula error"),
            ):
                oracle.interval_certificate(
                    self.graph, self.state["C"], self.state["W_A"], output
                )
        for value in ([float("nan")] * len(self.state["C"]), [[0]]):
            output = deepcopy(self.row["output"])
            output["C"] = value
            with self.assertRaisesRegex(ValueError, "shape/value"):
                oracle.interval_certificate(
                    self.graph, self.state["C"], self.state["W_A"], output
                )

    def test_saved_entry_cannot_be_redefined_by_faulty_producer(self):
        paper = aos.PaperAOS(self.graph)
        original = deepcopy(self.state)
        wrong = deepcopy(self.row["output"])
        wrong["W_A"][0] += 2**-20
        with (
            patch.object(paper, "step", return_value=wrong),
            self.assertRaisesRegex(ValueError, "full formula error"),
        ):
            oracle.evaluate(paper, self.state, "target_continuation", "current", 1)
        self.assertEqual(self.state, original)

    def test_rehashed_output_and_self_consistent_digest_fail_interval_recheck(self):
        changed = deepcopy(self.row)
        changed["output"]["current"][0] += 2**-20
        changed["certificate"]["output_digest"] = common.digest(changed["output"])
        with self.assertRaisesRegex(ValueError, "full formula error"):
            oracle.check_observation(
                self.graph, self.state, changed, recheck_numerics=True
            )


class RetainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = common.read(oracle.INPUTS)
        cls.results = common.read(oracle.RESULTS)

    def test_retained_all_sixteen_oracles_are_not_runtime_passes(self):
        oracle.check_manifest(self.manifest)
        summary = oracle.validate(self.manifest, self.results)
        self.assertEqual(summary["oracle_cases_passed"], 16)
        self.assertEqual(summary["runtime_cells_closed"], 0)
        self.assertFalse(summary["native_runtime_executed"])
        self.assertFalse(summary["interval_equations_recomputed"])
        self.assertEqual(
            sum(len(r["expectations"]) for r in self.results["cases"]), 352
        )

    def test_missing_roles_stages_and_false_execution_acceptance_fail(self):
        for mutation in (
            "case",
            "stage",
            "admission",
            "runtime",
            "acceptance",
            "entry",
        ):
            value = deepcopy(self.results)
            row = value["cases"][0]
            if mutation == "case":
                value["cases"].pop()
            elif mutation == "stage":
                row["expectations"].pop()
            elif mutation == "admission":
                row["target_admission_expectation_indices"]["reset"] = 0
            elif mutation == "runtime":
                row["native_event_committed"] = True
            elif mutation == "acceptance":
                value["user_accepted"] = True
            else:
                row["expectations"][2]["entry"]["W_A"][0] += 1e-5
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                oracle.validate(self.manifest, common.seal(value))


if __name__ == "__main__":
    unittest.main()
