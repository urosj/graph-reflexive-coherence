"""Focused C_CI boundary preparation and whole-joint-root pressure."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import unittest

import p984c_cci_preparation as p

b, r = p.b, p.r


class PreparationTests(unittest.TestCase):
    def test_population_reference_and_exact_resource_maps(self):
        manifest = p.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
        for case in manifest["cases"]:
            target = p.target_for(manifest, case)
            for role in r.ROLES:
                old, new = getattr(source, role), getattr(target, role)
                self.assertEqual(sum(map(Q, old.C)), sum(map(Q, new.C)))
                self.assertIsNone(new.W_A)
                self.assertIsNone(new.Z_4)
        for field in ("comparison", "request"):
            changed = deepcopy(manifest)
            if field == "request":
                changed["cases"][0][field]["resource_distribution"] = [0.25, 0.25, 0.5]
            else:
                changed["cases"][0][field]["budgets"]["root_error"] = "1/2"
            with self.subTest(field=field), self.assertRaises(ValueError):
                p.check_manifest(b.seal(changed))

    def test_target_joint_roots_cannot_be_reduced_to_current_or_swapped_roles(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        case = next(c for c in manifest["cases"] if "D38-E1-P1" in c["case_id"])
        row = next(v for v in record["cases"] if v["case_id"] == case["case_id"])
        target = p.target_for(manifest, case)
        for role in r.ROLES:
            before = replace(target, current=getattr(target, role))
            root = row["roles"][role]
            r.check_root(before, root, numerics=True)
            for field in ("H", "generated", "source", "bounds", "domain_id"):
                changed = deepcopy(root)
                if field == "bounds":
                    changed[field]["contraction_upper"] = "1"
                elif field == "domain_id":
                    changed[field] = "foreign-domain"
                else:
                    changed[field][0][0] += 1e-6
                cert = changed.pop("independent_certificate")
                changed = b.seal(changed)
                cert["selected_root_digest"] = changed["record_digest"]
                changed["independent_certificate"] = cert
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    r.check_root(before, changed)
            with self.subTest(role=role), self.assertRaises(ValueError):
                r.check_root(before, row["roles"]["reset" if role == "current" else "current"])

    def test_prediction_scope_and_invalid_states_fail_closed(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        case, row = manifest["cases"][0], record["cases"][0]
        target = p.target_for(manifest, case)
        p.check_predictions(target, row["predictions"])
        for value in (-1, float("nan"), float("inf")):
            changed = deepcopy(row["predictions"])
            changed["reset"][0]["C"][0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                p.check_predictions(target, changed)
        changed = deepcopy(row["predictions"])
        changed["current"][0]["J"][0] += 1
        with self.assertRaisesRegex(ValueError, "continuity"):
            p.check_predictions(target, changed)
        changed = deepcopy(record)
        changed["cases"][0]["runtime_cells_closed"] = 2
        with self.assertRaisesRegex(ValueError, "runtime credit"):
            p.status(manifest, b.seal(changed))
        changed = deepcopy(record)
        changed["reuse"][0]["previous_row_digest"] = "wrong"
        with self.assertRaisesRegex(ValueError, "reuse"):
            p.status(manifest, b.seal(changed))


if __name__ == "__main__":
    unittest.main()
