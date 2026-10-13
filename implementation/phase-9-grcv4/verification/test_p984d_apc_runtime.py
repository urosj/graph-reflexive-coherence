"""A_PC deep-layout pressure at actual saved operands; no duplicate native campaign."""

from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

import p984d_apc_runtime as runtime

r, b = runtime.r, runtime.b


class APCDeepTests(unittest.TestCase):
    def test_contract_targets_and_whole_chart(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 40)
        seed = r.state(manifest["expected_source"])
        self.assertNotEqual(seed.inputs.current.Z_4, seed.inputs.reset.Z_4)
        self.assertNotEqual(seed.inputs.current.W_A, seed.inputs.reset.W_A)
        with ExitStack() as stack:
            for module, name in ((r, "CandidatePCRead"), (r, "ProvisionalCandidatePCStep"), (r.native, "GRC9V4APCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))
            for case in manifest["cases"]:
                runtime.previous.bind_case(seed, case, manifest)
                target = r.independent_target(seed, case)
                self.assertEqual(case["independent_whole_chart"], r.oracle.whole_chart(case["oracle"]["target_graph"]))
                for role in r.ROLES:
                    old, new = getattr(seed.inputs, role), getattr(target.inputs, role)
                    histories = dict(zip(seed.inputs.geometry.reference.graph.live_edge_ids, old.W_A, strict=True))
                    expected = tuple(histories.get(e, seed.specialization.resolved["expansion"]["bond_seed"])
                        for e in target.inputs.geometry.reference.graph.live_edge_ids)
                    self.assertEqual(new.W_A, expected)
                    self.assertFalse(any(new.Z_4))
                    self.assertTrue(r.charge_record(seed.inputs, new))
                    self.assertGreaterEqual(min(new.C), 0)
        with patch.object(runtime, "ACCEPTANCE_SHA", "unaccepted"), self.assertRaises(ValueError):
            runtime.predecessor()
        self.assertEqual(sorted({len(c["oracle"]["target_graph"]["live_node_ids"]) for c in manifest["cases"]}), [18,19,20,23])
        for kind in ("population", "shares", "budget", "source"):
            changed = deepcopy(manifest)
            if kind == "population":
                changed["cases"].pop()
            elif kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["execution_budget_seconds"] += 1
            else:
                changed["expected_source"]["inputs"]["current"]["W_A"][0] += 0.01
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_manifest(b.seal(changed))

    def test_failed_pilot_has_no_native_credit(self):
        manifest, record = b.read(runtime.INPUTS), b.read(runtime.RESULTS)
        with ExitStack() as stack:
            for module, name in ((r, "CandidatePCRead"), (r, "ProvisionalCandidatePCStep"),
                    (r.native, "GRC9V4APCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))
            summary = runtime.check(manifest, record, numerics=True)
        self.assertEqual((summary["attempted_cases"], summary["unattempted_cases"]), (1,19))
        self.assertEqual((summary["native_cases"],summary["target_steps"],summary["accepted_cells"]), (0,0,0))
        raw = runtime.previous.expand(record["execution"])
        self.assertEqual(runtime.previous.expand(runtime.previous.compact(raw)), raw)
        for kind in ("roster", "scope", "event", "false_pass", "native_flag", "failure"):
            value = deepcopy(raw)
            row = value["cases"][0]
            if kind == "roster":
                value["cases"].append(deepcopy(row))
            elif kind == "scope":
                row["user_accepted"] = True
            elif kind == "event":
                row["event_committed"] = True
            elif kind == "false_pass":
                row.update(case_passed=True, outcome="passed_named_case", first_failure=None)
            elif kind == "native_flag":
                value["native_runtime_executed"] = True
            else:
                row["first_failure"]["message"] = "different failure"
            changed = dict(record, execution=runtime.previous.compact(b.seal(value)))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check(manifest, b.seal(changed))

    def test_full_enabled_interval_exclusions_and_second_step_control(self):
        manifest, record = b.read(runtime.INPUTS), b.read(runtime.PRESSURE)
        with ExitStack() as stack:
            for module, name in ((r, "CandidatePCRead"), (r, "ProvisionalCandidatePCStep"),
                    (r.native, "GRC9V4APCOperation")):
                stack.enter_context(patch.object(module, name, side_effect=AssertionError("native producer forbidden")))
            summary = runtime.check_pressure(manifest, record, numerics=True)
        self.assertEqual(summary["certified_exclusions"], 2)
        first, _, _, balanced, second, _, _ = record["samples"]
        self.assertLess(min(r.Q(z) for a,z in first["resource_intervals"]), r.Q(-7e-5))
        self.assertEqual(min(r.Q(a) for a,z in balanced["resource_intervals"]), 0)
        self.assertLess(min(r.Q(z) for a,z in second["resource_intervals"]), r.Q(-1e-7))
        self.assertNotEqual(balanced["entry"]["W_A"], second["entry"]["W_A"])
        self.assertFalse(any(balanced["entry"]["Z_4"]))
        self.assertTrue(any(second["entry"]["Z_4"]))
        for kind in ("role", "schedule", "sign", "scope", "bound"):
            wrong = deepcopy(record)
            if kind == "role":
                wrong["samples"][0]["role"] = "reset"
            elif kind == "schedule":
                wrong["samples"].pop()
            elif kind == "sign":
                wrong["samples"][0]["excluded_nodes"] = []
            elif kind == "scope":
                wrong["general_infeasibility_proved"] = True
            else:
                wrong["samples"][0]["resource_intervals"][0] = ["1", "0"]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.check_pressure(manifest,b.seal(wrong))
        # A hash-consistent wrong input must also fail equation recomputation.
        wrong = deepcopy(record)
        wrong["samples"][0]["entry"]["W_A"][0] += 1/16
        with self.assertRaisesRegex(ValueError, "operand drift"):
            runtime.check_pressure(manifest,b.seal(wrong),numerics=True)


if __name__ == "__main__":
    unittest.main()
