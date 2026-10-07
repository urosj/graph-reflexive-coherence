"""Boundary native pressure using retained operands, without another campaign."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984c_aos_runtime as runtime

base, previous = runtime.base, runtime.previous


class BoundaryNativeTests(unittest.TestCase):
    def test_prepared_population_acceptance_and_subjects(self):
        manifest = runtime.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        with patch.object(runtime, "ACCEPTANCE_SHA", "unaccepted"), self.assertRaisesRegex(ValueError, "review changed"):
            runtime.accepted_oracle()
        for field in ("cases", "exact_reuse", "oracle_results_digest"):
            changed = deepcopy(manifest)
            if isinstance(changed[field], list):
                changed[field].pop()
            else:
                changed[field] = "wrong"
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.check_manifest(base.seal(changed))

    @classmethod
    def retained(cls):
        manifest, record = base.read(runtime.INPUTS), base.read(runtime.RESULTS)
        execution = runtime.materialize(manifest, record)
        return manifest, record, execution

    def test_compact_evidence_is_exact_and_fail_closed(self):
        _, record, _ = self.retained()
        value = runtime.expand(record["execution"])
        self.assertEqual(runtime.expand(runtime.compact(value)), value)
        broken = deepcopy(record["execution"])
        key = next(iter(broken["contexts"]))
        broken["contexts"][key] = []
        with self.assertRaisesRegex(ValueError, "context digest"):
            runtime.expand(broken)

    def test_resealed_roster_scope_and_reuse_changes_rejected(self):
        manifest, record, _ = self.retained()
        for kind in ("missing", "scope", "event_vs_case", "reuse"):
            changed = deepcopy(record)
            execution = runtime.expand(changed["execution"])
            if kind == "missing":
                execution["cases"].pop()
            elif kind == "scope":
                execution["cases"][0]["user_accepted"] = True
            elif kind == "event_vs_case":
                execution["cases"][0]["case_passed"] = False
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            changed["execution"] = runtime.compact(base.seal(execution))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                runtime.status(manifest, base.seal(changed))

    def test_actual_source_history_and_both_role_stage_pressure(self):
        _, _, execution = self.retained()
        accepted, expected = runtime.accepted_oracle()
        seed = previous.seed_from_payload(execution["shared"]["actual_source"])
        # D38: two remainders; phase 1, positive chirality. Both distinct roles.
        index = next(i for i, c in enumerate(accepted["cases"]) if
            (c["request"]["target_effective_degree"], c["request"]["growth_phase"], c["request"]["module_chirality"]) == (38, 1, 1))
        row, oracle_case, nominal = execution["cases"][index], accepted["cases"][index], expected["cases"][index]
        request = previous.fresh_request(seed, oracle_case)
        target = previous.check_event(row["event"], seed, request, oracle_case)
        for role in runtime.oracle.previous.ROLES:
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=previous.aos.DT)
            step = next(r["step"] for r in row["continuation"] if r["role"] == role and r["index"] == 1)
            # Independent interval equations at the actual native operand,
            # including fresh written-state/restart reads, not nominal state.
            previous.check_step_record(before, step, target.differential_reference,
                nominal["expectations"][0 if role == "current" else 11]["output"], numerics=True)
            for wrong in ("predictor_writer", "frozen_history", "wrong_regeneration", "stale_final"):
                changed = deepcopy(step)
                if wrong == "predictor_writer":
                    changed["pass"]["trace"]["writer_targets"][0]["point_identity"] = changed["pass"]["predictor"]["identity"]
                elif wrong == "frozen_history":
                    changed["poststate"]["W_A"] = list(before.current.W_A)
                elif wrong == "wrong_regeneration":
                    changed["pass"]["regenerated"] = changed["pass"]["H"]
                    changed["pass"]["trace"]["geometry"][1]["H"] = changed["pass"]["H"]
                else:
                    changed["final"] = changed["pass"]["corrector"]
                with self.subTest(role=role, wrong=wrong), self.assertRaises(ValueError):
                    previous.capture.check_step(changed, before, target.differential_reference)
        for wrong in ("history", "reference_current", "early_publication"):
            changed = deepcopy(row["event"])
            if wrong == "history":
                changed["actual_target"]["inputs"]["reset"]["W_A"][0] += 0.01
            elif wrong == "reference_current":
                changed["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][0] += 1
            else:
                changed["publication_observations"][0]["admission_reads_before_receipts"] = 3
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                previous.check_event(changed, seed, request, oracle_case)


if __name__ == "__main__":
    unittest.main()
