"""Focused A_CI boundary pressure; retained operands, not another campaign."""

from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch
import unittest

import p984c_aci_runtime as runtime

r, b = runtime.r, runtime.b


class ACIBoundaryTests(unittest.TestCase):
    def test_accepted_scope_source_population_and_freeze(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        with patch.object(runtime, "ACCEPTANCE_SHA", "unaccepted"), self.assertRaises(ValueError):
            runtime.accepted_oracle()
        for kind in ("roster", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "roster":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["W_A"][0] += 1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))
        ready, _ = runtime.accepted_oracle()
        seed = r.state(ready["expected_source"])
        case = manifest["cases"][0]
        self.assertEqual(runtime.bind_case(seed, case, ready), case)
        changed = replace(seed, inputs=replace(seed.inputs, current=seed.inputs.reset))
        with self.assertRaisesRegex(ValueError, "source/history"):
            runtime.bind_case(changed, case, ready)

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

    def test_actual_joint_root_history_and_lifecycle_pressure(self):
        manifest, _, execution = self.retained()
        index = next(i for i, c in enumerate(manifest["cases"]) if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        row, case = execution["cases"][index], manifest["cases"][index]
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        for role in r.ROLES:
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=b.DT)
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            r.check_step(before, target.differential_reference, step, numerics=True)
            for kind in ("geometry", "read", "domain", "source", "restart", "continuity", "stale_writer", "frozen_history"):
                changed = deepcopy(step)
                if kind == "geometry":
                    changed["root"]["H"][0][0] += 2**-20
                elif kind == "read":
                    changed["root"]["read_current"][0] += 1
                elif kind == "domain":
                    changed["root"]["bounds"]["contraction_upper"] = "1"
                elif kind == "source":
                    changed["root"]["source"][0][0] += 2**-50
                elif kind == "restart":
                    changed["restart"] = changed["root"]
                elif kind == "continuity":
                    changed["poststate"]["current"]["C"][0] += 1
                elif kind == "stale_writer":
                    changed["writer_targets"][0]["C"] = list(before.current.C)
                else:
                    changed["poststate"]["current"]["W_A"] = list(before.current.W_A)
                if kind in ("geometry", "read", "domain", "source"):
                    raw = {k: v for k, v in changed["root"].items() if k != "independent_certificate"}
                    changed["root"]["record_digest"] = b.seal(raw)["record_digest"]
                    changed["root"]["independent_certificate"]["selected_root_digest"] = changed["root"]["record_digest"]
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_step(before, target.differential_reference, changed)
            raw = {k: v for k, v in step["root"].items() if k != "independent_certificate"}
            for kind in ("geometry", "readback", "nonfinite"):
                changed = deepcopy(raw)
                if kind == "geometry":
                    changed["H"][0][0] += 2**-20
                elif kind == "readback":
                    changed["readback"][0] += 2**-20
                else:
                    changed["J"][0] = float("nan")
                with self.subTest(role=role, equation=kind), self.assertRaises((ValueError, AssertionError)):
                    r.independent_certificate(before, changed)
        for kind in ("reset_W", "reference_current", "early_publication", "missing_read", "replay"):
            changed = deepcopy(row["event"])
            if kind == "reset_W":
                changed["actual_target"]["inputs"]["reset"]["W_A"][0] += 1
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
