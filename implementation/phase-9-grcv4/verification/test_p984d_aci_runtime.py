"""Deep native A_CI scientific, lifecycle and evidence pressure; no campaign rerun."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import unittest
from unittest.mock import patch
from pygrc.models.grc_v4_geometry import VertexScalar
from pygrc.models.grc_v4_transport import ChargeEvaluation

import p984d_aci_runtime as p

r, b = p.r, p.b


class DeepACITests(unittest.TestCase):
    def test_accepted_scope_and_source_freeze(self):
        m = p.make_manifest()
        self.assertEqual(len(m["cases"]), 20)
        self.assertEqual(len({v for c in m["cases"] for v in c["coverage_binding"]["cell_ids"]}), 40)
        with patch.object(p, "ACCEPTANCE_SHA", "unaccepted"), self.assertRaises(ValueError):
            p.accepted_oracle()
        for key in ("cases", "expected_source", "scope"):
            wrong = deepcopy(m)
            if key == "cases":
                wrong[key][0]["request"]["resource_distribution"] = [0.25,0.5,0.25]
            elif key == "expected_source":
                wrong[key]["inputs"]["reset"]["W_A"][0] += 1
            else:
                wrong[key]["arbitrary_depth"] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                p.check_manifest(b.seal(wrong))

    def test_deep_joint_root_writer_and_event_pressure(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        execution = p.previous.expand(record["execution"])
        case = next(c for c in manifest["cases"] if "D94-E-1-P3" in c["case_id"])
        row = next(v for v in execution["cases"] if v["case_id"] == case["case_id"])
        self.assertTrue(row["case_passed"], row["first_failure"])
        seed = r.state(execution["shared"]["actual_source"])
        target = r.check_event(seed, case, row["event"])
        for role in r.ROLES:
            before = replace(target.inputs, current=getattr(target.inputs, role), dt=b.DT)
            step = next(v["step"] for v in row["continuation"] if v["role"] == role and v["index"] == 1)
            after = r.check_step(before, target.differential_reference, step, numerics=True)
            self.assertGreater(min(after.current.C), 0)
            # The frozen binary64 reduction/tolerance is not exact coordinate conservation.
            charge = ChargeEvaluation(VertexScalar(after.geometry.reference.graph, after.current.C),
                after.Q_target, after.geometry.reference.profile)
            self.assertTrue(charge.admitted)
            self.assertLessEqual(abs(Q(charge.actual)-Q(after.Q_target)), Q(1e-11))
            for kind in ("root", "restart", "continuity", "stale_writer", "frozen_history"):
                wrong = deepcopy(step)
                if kind == "root":
                    wrong["root"]["H"][0][0] += 2**-20
                elif kind == "restart":
                    wrong["restart"] = wrong["root"]
                elif kind == "continuity":
                    wrong["poststate"]["current"]["C"][0] += 1
                elif kind == "stale_writer":
                    wrong["writer_targets"][0]["C"] = list(before.current.C)
                else:
                    wrong["poststate"]["current"]["W_A"] = list(before.current.W_A)
                with self.subTest(role=role, kind=kind), self.assertRaises(ValueError):
                    r.check_step(before, target.differential_reference, wrong)
            raw = {k:v for k,v in step["root"].items() if k != "independent_certificate"}
            for kind in ("geometry", "readback", "nonfinite"):
                wrong = deepcopy(raw)
                if kind == "geometry":
                    wrong["H"][0][0] += 2**-20
                elif kind == "readback":
                    wrong["readback"][0] += 2**-20
                else:
                    wrong["J"][0] = float("nan")
                with self.subTest(role=role, equation=kind), self.assertRaises((ValueError,AssertionError)):
                    r.independent_certificate(before, wrong)
        for kind in ("reset_W", "reference", "early_publication", "missing_read", "replay"):
            wrong = deepcopy(row["event"])
            if kind == "reset_W":
                wrong["actual_target"]["inputs"]["reset"]["W_A"][0] += 1
            elif kind == "reference":
                wrong["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][0] += 1
            elif kind == "early_publication":
                wrong["publication"][0]["admission_pairs"] = 1
            elif kind == "missing_read":
                wrong["admission_reads"].pop()
            else:
                wrong["replay_identical"] = False
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                r.check_event(seed, case, wrong)

    def test_lossless_capture_and_no_false_completion(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        self.assertEqual(p.status(manifest, record)["passed_cases"], 20)
        execution = p.previous.expand(record["execution"])
        self.assertEqual(p.previous.expand(p.previous.compact(execution)), execution)
        for kind in ("roster", "scope", "event_vs_case", "schedule", "false_pass"):
            wrong = deepcopy(execution)
            row = wrong["cases"][0]
            if kind == "roster":
                wrong["cases"].pop()
            elif kind == "scope":
                row["user_accepted"] = True
            elif kind == "event_vs_case":
                row["case_passed"] = False
            elif kind == "schedule":
                row["continuation"].pop()
            else:
                row["first_failure"] = dict(stage="final_read", message="failure")
            changed = dict(record, execution=p.previous.compact(b.seal(wrong)))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.status(manifest, b.seal(changed))


if __name__ == "__main__":
    unittest.main()
