"""C_CI boundary pressure on actual retained operands, not another campaign."""

from copy import deepcopy
from dataclasses import replace
import unittest

import p984c_cci_runtime as runtime

r, b = runtime.r, runtime.b


class CCIBoundaryTests(unittest.TestCase):
    def test_preparation_population_and_scientific_freeze(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        for kind in ("roster", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "roster":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.5, 0.5]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["C"][0] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    @classmethod
    def retained(cls):
        manifest, record = b.read(runtime.INPUTS), b.read(runtime.RESULTS)
        return manifest, record, runtime.materialize(manifest, record)

    def test_compaction_roster_scope_and_reuse_pressure(self):
        manifest, record, _ = self.retained()
        raw = runtime.expand(record["execution"])
        self.assertEqual(runtime.expand(runtime.compact(raw)), raw)
        corrupt = deepcopy(record["execution"])
        corrupt["contexts"][next(iter(corrupt["contexts"]))] = []
        with self.assertRaisesRegex(ValueError, "context digest"):
            runtime.expand(corrupt)
        for kind in ("roster", "scope", "event_vs_case", "reuse", "schedule"):
            changed = deepcopy(record)
            execution = runtime.expand(changed["execution"])
            if kind == "roster":
                execution["cases"].pop()
            elif kind == "scope":
                execution["cases"][0]["user_accepted"] = True
            elif kind == "event_vs_case":
                execution["cases"][0]["case_passed"] = False
            elif kind == "schedule":
                execution["cases"][0]["continuation"].pop()
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            changed["execution"] = runtime.compact(b.seal(execution))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.status(manifest, b.seal(changed))

    def test_actual_joint_root_step_and_lifecycle_pressure(self):
        manifest, _, execution = self.retained()
        index = next(i for i, c in enumerate(manifest["cases"]) if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        row, case = execution["cases"][index], manifest["cases"][index]
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        for role in r.ROLES:
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=b.DT)
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            r.check_step(before, step, numerics=True)
            for kind in ("wrong_geometry", "wrong_read", "wrong_domain", "source", "stale_restart", "continuity"):
                changed = deepcopy(step)
                if kind == "wrong_geometry":
                    changed["root"]["H"][0][0] += 2**-20
                elif kind == "wrong_read":
                    changed["root"]["read_current"][0] += 1
                elif kind == "wrong_domain":
                    changed["root"]["bounds"]["contraction_upper"] = "1"
                elif kind == "source":
                    changed["root"]["source"][0][0] += 2**-50
                elif kind == "stale_restart":
                    changed["restart"] = changed["root"]
                else:
                    changed["poststate"]["current"]["C"][0] += 1
                if kind in ("wrong_geometry", "wrong_read", "wrong_domain", "source"):
                    raw = {k: v for k, v in changed["root"].items() if k != "independent_certificate"}
                    changed["root"]["record_digest"] = b.seal(raw)["record_digest"]
                    changed["root"]["independent_certificate"]["selected_root_digest"] = changed["root"]["record_digest"]
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_step(before, changed)
        for kind in ("reset", "reference_current", "early_publication", "missing_read", "replay"):
            changed = deepcopy(row["event"])
            if kind == "reset":
                changed["actual_target"]["inputs"]["reset"]["C"][0] += 1
            elif kind == "reference_current":
                changed["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][0] += 1
            elif kind == "early_publication":
                changed["publication"][0]["admission_pairs"] = 1
            elif kind == "missing_read":
                changed["admission_reads"].pop()
            else:
                changed["replay_identical"] = False
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                r.check_event(seed, case, changed)


if __name__ == "__main__":
    unittest.main()
