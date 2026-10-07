"""A_CI boundary oracle pressure without production numerical execution."""

from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import p984c_aci_oracle as p

b = p.b


class ACIOracleTests(unittest.TestCase):
    def test_layouts_history_lineage_shares_and_scope(self):
        manifest = p.make_manifest()
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 64)
        source = p.previous.state(manifest["expected_source"])
        with ExitStack() as stack:
            for name in p.PRODUCERS:
                stack.enter_context(patch(name, side_effect=AssertionError("native producer forbidden")))
            for case in manifest["cases"]:
                target = p.target_for(manifest, case)
                for role in p.previous.ROLES:
                    old, new = getattr(source.inputs, role), getattr(target.inputs, role)
                    self.assertEqual(sum(map(Q, old.C)), sum(map(Q, new.C)))
                    self.assertIsNone(new.Z_4)
        for kind in ("shares", "budget", "reuse"):
            changed = deepcopy(manifest)
            if kind == "shares":
                changed["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                changed["cases"][0]["comparison"]["budgets"]["root_error"] = "1"
            else:
                changed["exact_reuse"].pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.check_manifest(b.seal(changed))

    def test_actual_joint_root_readback_history_and_domain_pressure(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        case = next(c for c in manifest["cases"] if "D38-E1-P1" in c["case_id"])
        row = next(v for v in record["cases"] if v["case_id"] == case["case_id"])
        graph = case["oracle"]["target_graph"]
        paper = p.oracle.PaperACI(graph)
        for role in p.previous.ROLES:
            value = next(v for v in row["observations"] if v["role"] == role and v["index"] == 1)
            p.check_observation(graph, value["entry"], value, numerics=True)
            for kind in ("geometry", "readback", "flat", "frozen_W", "nonfinite"):
                wrong = deepcopy(value["output"])
                if kind == "geometry":
                    wrong["H"][0][0] += 2**-18
                elif kind in ("readback", "flat"):
                    wrong[kind][0] += 1e-5
                elif kind == "frozen_W":
                    wrong["W_A"] = value["entry"]["W_A"]
                else:
                    wrong["current"][0] = float("nan")
                with self.subTest(role=role, kind=kind), self.assertRaises((ValueError, OverflowError)):
                    p.certificate(graph, value["entry"], wrong)
            # Valid alternative current, but with the defining feedback disabled.
            _, alternative = paper.root(value["entry"]["C"], value["entry"]["W_A"], feedback=False)
            wrong = deepcopy(value["output"])
            wrong["current"] = list(map(float, alternative["current"]))
            with self.assertRaises(ValueError):
                p.certificate(graph, value["entry"], wrong)
            for field, bad in (("contraction_upper", "1"), ("radius", "1/2"), ("displacement_upper", "1")):
                cert = deepcopy(value["certificate"])
                cert["domain"][field] = bad
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    p.check_certificate(cert)

    def test_resealed_native_promotion_schedule_and_reuse_rejected(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        for kind in ("native", "role", "stage", "reuse"):
            changed = deepcopy(record)
            if kind == "native":
                changed["cases"][0]["native_steps"] = 10
            elif kind == "role":
                changed["cases"][0]["observations"][0]["role"] = "reset"
            elif kind == "stage":
                changed["cases"][0]["observations"][-1]["stage"] = "nominal_update"
            else:
                changed["reuse"][0]["previous_row_digest"] = "wrong"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.check(manifest, b.seal(changed))


if __name__ == "__main__":
    unittest.main()
