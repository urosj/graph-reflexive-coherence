"""Independent arithmetic and mutation pressure for the unexecuted .c contract."""

from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import prepare_p984c_boundaries as contract


class BoundaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = contract.build()

    def test_capacity_endpoints_by_independent_enumeration(self):
        expected = {36: (5, 37, 1), 37: (5, 37, 1), 38: (6, 44, 2),
                    43: (6, 44, 2), 44: (6, 44, 2), 45: (7, 51, 0)}
        for row in self.value["layouts"]:
            degree, e = row["degree"], row["expected"]
            # Count free ports on a tree, rather than repeat the ceil formula.
            minimum = next(n for n in range(4, 20) if 9*n - 2*(n-1) >= degree)
            self.assertEqual((e["module_nodes"], e["capacity"], e["remainder"]), expected[degree])
            self.assertEqual(e["module_nodes"], minimum)
            self.assertEqual(e["internal_edges"], minimum - 1)
            self.assertEqual(e["unused_capacity"], e["capacity"] - degree)
            self.assertEqual((e["target_vertices"], e["target_edges"]), (9+minimum, 8+minimum))

    def test_chiral_remainder_distribution(self):
        cycles = {1: (1, 2, 3), -1: (1, 3, 2)}
        for row in self.value["layouts"]:
            e, phase = row["expected"], row["phase"]
            extras = [0, 0, 0]
            if phase is None:
                extras = [1, 1, 1]
            else:
                cycle = cycles[row["chirality"]]
                offset = cycle.index(phase)
                for i in range(e["remainder"]):
                    extras[cycle[(offset+i) % 3] - 1] += 1
            self.assertEqual(e["branch_extras"], extras)
            self.assertEqual(sum(extras), e["module_nodes"] - 4)

    def test_exact_ten_family_both_role_population(self):
        v = self.value
        families = {f"{a}_{r}" for a, r in itertools.product(("A", "C"), ("OS", "CI", "PC", "CI_PC", "RG2b"))}
        self.assertEqual({r["family"] for r in v["families"]}, families)
        expected = set(itertools.product((r["id"] for r in v["layouts"]), families, ("current", "reset")))
        self.assertEqual({(r["layout"], r["family"], r["role"]) for r in v["cells"]}, expected)
        self.assertEqual(len(v["cells"]), 640)
        self.assertEqual(len(v["cases"]), 320)
        self.assertEqual(len({r["id"] for r in v["cells"]}), 640)
        self.assertEqual(v["counts"]["reuse_candidates"], 40)
        self.assertEqual(v["counts"]["new_history_cells"], 600)
        self.assertTrue(all(not r["runtime_executed"] and not r["user_accepted"] for r in v["cells"]))
        cases = {r["id"]: r for r in v["cases"]}
        for cell in v["cells"]:
            case = cases[cell["case_id"]]
            self.assertEqual((case["layout"], case["family"]), (cell["layout"], cell["family"]))
            self.assertEqual(case["reuse_case_id"], cell["reuse_case_id"])

    def test_wire_and_semantic_failures_are_distinct_obligations(self):
        rows = self.value["negative_recipes"]
        self.assertEqual(sum(r["expected_stage"] == "wire_decode" for r in rows), 14)
        self.assertEqual(sum(r["expected_stage"] == "typed_request_admission" for r in rows), 17)
        self.assertEqual({r["expected_code"] for r in rows if r["expected_stage"] == "typed_request_admission"},
                         {"module_chirality_required", "module_growth_phase_required", "reject_noncanonical_inactive_growth_phase"})
        self.assertTrue(all(r["expected_stage"] == "wire_decode" for r in rows if r["operation"] == "remove"))
        self.assertEqual(self.value["common_pressure"]["integer_valued_float_control"], 37.0)
        for degree in (True, 37.0, 8):
            with self.assertRaises(ValueError):
                contract.geometry(degree, 1, 1)
        for degree, chirality, phase in ((37, True, 1), (37, 1, None), (45, 1, 1), (37, 1, True)):
            with self.assertRaises(ValueError):
                contract.geometry(degree, chirality, phase)

    def test_schedule_budgets_and_reuse_are_not_success(self):
        v = self.value
        self.assertEqual(v["schedule"]["target_beats_per_role"], 10)
        self.assertEqual(v["schedule"]["dt"], 1/4096)
        self.assertEqual((v["schedule"]["source_current_beats"], v["schedule"]["source_reset_beats"]), (1, 0))
        self.assertEqual((v["counts"]["accepted_cells"], v["counts"]["executed_cells"]), (0, 0))
        for case in v["cases"]:
            d = case["request_recipe"]["overrides"]["target_effective_degree"]
            self.assertEqual(case["reuse_case_id"] is not None, d == 45)
            self.assertIn(case["disposition"], ("pending_exact_reuse_check", "pending_new_target_prerequisites"))
        for family in v["families"]:
            self.assertEqual(family["budget_status"], "frozen_required_ceiling_not_new_target_certificate")
            self.assertIn("pending", family["readiness"])
            self.assertEqual(family["new_A_oracle_review_required"], family["family"].startswith("A_"))

    def test_all_operand_references_resolve_and_are_bound(self):
        v = self.value
        bindings = {r["path"] for r in v["source_bindings"]}

        def visit(value):
            if isinstance(value, dict):
                if "payload_digest" in value:
                    self.assertIn(value["path"], bindings)
                    target = json.loads((contract.ROOT / value["path"]).read_bytes())
                    for key in value["pointer"].strip("/").split("/"):
                        target = target[int(key)] if isinstance(target, list) else target[key]
                    self.assertEqual(contract.digest(target), value["payload_digest"])
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        visit(v)
        self.assertTrue(all(not Path(p).is_absolute() and ".." not in Path(p).parts for p in bindings))
        self.assertLess(len(json.dumps(v, indent=2).encode()), v["retention"]["max_contract_bytes"])
        self.assertFalse(v["retention"]["operational_or_incomplete_runs_retained"])

    def test_resealed_mutations_do_not_create_authority(self):
        def mutate(v, path, replacement):
            cursor = v
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = replacement

        mutations = [(("layouts", 0, "expected", "capacity"), 38),
                     (("layouts", 0, "expected", "branch_extras"), [0, 0, 0]),
                     (("cells", 0, "role"), "reset"),
                     (("families",), self.value["families"][:-1]),
                     (("families", 0, "comparison"), {}),
                     (("source_bindings", 0, "sha256"), "0"*64),
                     (("user_accepted",), True), (("counts", "executed_cells"), 640)]
        # The frozen expected value is reconstructed once; no solver needed.
        with patch.object(contract, "build", return_value=self.value):
            for path, replacement in mutations:
                with self.subTest(path=path):
                    bad = deepcopy(self.value)
                    mutate(bad, path, replacement)
                    with self.assertRaisesRegex(ValueError, "source-bound reconstruction"):
                        contract.validate(contract.seal(bad))

    def test_retained_record_and_source_drift(self):
        retained = json.loads((contract.ROOT / contract.OUTPUT).read_bytes())
        self.assertEqual(contract.validate(retained)["contract_integrity"], "passed")
        path = contract.ROOT / "docs/reference/EvidenceStorage.md"
        original = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda p: original(p) + b"\n" if p == path else original(p)):
            with self.assertRaisesRegex(ValueError, "source-bound reconstruction"):
                contract.validate(retained)


if __name__ == "__main__":
    unittest.main()
