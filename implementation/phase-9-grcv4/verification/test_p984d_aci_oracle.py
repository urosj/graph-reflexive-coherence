"""Deep A_CI transfer, joint-root and false-credit pressure; no native campaign."""

from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

import p984d_aci_oracle as p

b = p.b


class DeepACIOracleTests(unittest.TestCase):
    def test_population_transfer_and_dimension_scope(self):
        manifest = p.make_manifest()
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(len({v for c in manifest["cases"] for v in c["coverage_binding"]["cell_ids"]}), 40)
        sizes = set()
        with ExitStack() as stack:
            for name in p.previous.PRODUCERS:
                stack.enter_context(patch(name, side_effect=AssertionError("native producer forbidden")))
            for case in manifest["cases"]:
                # Includes exact charge, old-edge lineage/new-edge seeding and distinct roles.
                target = p.previous.target_for(manifest, case)
                sizes.add(len(target.inputs.current.C))
        self.assertEqual(sizes, {18, 19, 20, 23})
        for kind in ("shares", "budget", "depth"):
            wrong = deepcopy(manifest)
            if kind == "shares":
                wrong["cases"][0]["request"]["resource_distribution"] = [0.25, 0.5, 0.25]
            elif kind == "budget":
                wrong["cases"][0]["comparison"]["budgets"]["root_error"] = "1"
            else:
                wrong["scope"]["arbitrary_depth"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.check_manifest(b.seal(wrong))

    def test_largest_joint_root_mechanism_pressure(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        case = next(c for c in manifest["cases"] if "D94-E1-P1" in c["case_id"])
        row = next(v for v in record["cases"] if v["case_id"] == case["case_id"])
        graph = case["oracle"]["target_graph"]
        paper = p.previous.oracle.PaperACI(graph)
        for role in p.ROLES:
            value = next(v for v in row["observations"] if v["role"] == role and v["index"] == 1)
            p.previous.check_observation(graph, value["entry"], value, numerics=True)
            for kind in ("geometry", "readback", "flat", "frozen_W", "nonfinite", "feedback_off"):
                wrong = deepcopy(value["output"])
                if kind == "geometry":
                    wrong["H"][0][0] += 2**-18
                elif kind in ("readback", "flat"):
                    wrong[kind][0] += 1e-5
                elif kind == "frozen_W":
                    wrong["W_A"] = value["entry"]["W_A"]
                elif kind == "nonfinite":
                    wrong["current"][0] = float("nan")
                else:
                    _, alternative = paper.root(value["entry"]["C"], value["entry"]["W_A"], feedback=False)
                    wrong["current"] = list(map(float, alternative["current"]))
                with self.subTest(role=role, kind=kind), self.assertRaises((ValueError, OverflowError)):
                    p.previous.certificate(graph, value["entry"], wrong)
            for field, bad in (("contraction_upper", "1"), ("radius", "1/2"), ("displacement_upper", "1")):
                cert = deepcopy(value["certificate"])
                cert["domain"][field] = bad
                with self.subTest(role=role, field=field), self.assertRaises(ValueError):
                    p.previous.check_certificate(cert)

    def test_resealed_schedule_stage_and_native_promotion(self):
        manifest, record = b.read(p.INPUTS), b.read(p.RESULTS)
        self.assertEqual(p.check(manifest, record)["independent_observations"], 440)
        for kind in ("native", "role", "stage", "missing_case", "history", "joint_digest"):
            wrong = deepcopy(record)
            row = wrong["cases"][0]
            if kind == "native":
                row["native_steps"] = 10
            elif kind == "role":
                row["observations"][0]["role"] = "reset"
            elif kind == "stage":
                row["observations"][-1]["stage"] = "nominal_update"
            elif kind == "missing_case":
                wrong["cases"].pop()
            elif kind == "history":
                row["observations"][1]["entry"] = row["observations"][0]["entry"]
            else:
                row["observations"][0]["certificate"]["selected_joint_point_digest"] = "wrong"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                p.check(manifest, b.seal(wrong))


if __name__ == "__main__":
    unittest.main()
