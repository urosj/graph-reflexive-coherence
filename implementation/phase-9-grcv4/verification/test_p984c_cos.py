"""Focused C_OS boundary construction, retention and scientific mutations."""

from copy import deepcopy
import unittest

import p984c_cos as run
from pygrc.models import grc_9_v4_expansion as expansion
from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph


class COSBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = run.make_manifest()

    def test_exact_subjects_targets_and_both_resource_roles(self):
        manifest = self.manifest
        graph = GRC9V4PortGraph.from_payload(manifest["initial_inputs"]["reference"]["graph"])
        policy = expansion.GRC9ExpansionPolicy.from_payload(manifest["expected_source"]["specialization"]["resolved"]["expansion"])
        self.assertEqual(len(manifest["cases"]), 32)
        self.assertEqual(len(manifest["exact_reuse"]), 2)
        for case in manifest["cases"]:
            with self.subTest(case=case["case_id"]):
                request = expansion.GRC9V4ExpansionRequestInput.from_payload(case["request"])
                actual = expansion.GRC9V4ExpansionPlan(graph, request.source_state_digest, request, policy)
                self.assertEqual(actual.event_identity_payload(), case["oracle"]["event_identity"])
                self.assertEqual(actual.target_graph.to_payload(), case["oracle"]["target_graph"])
                target = run.base.independent_target(manifest, case)
                self.assertNotEqual(target.current, target.reset)
                for role in run.boundary.ROLES:
                    self.assertGreaterEqual(min(getattr(target, role).C), 0)
                    self.assertIsNone(getattr(target, role).W_A)
                    self.assertIsNone(getattr(target, role).Z_4)

    def test_reference_compaction_is_exact_and_fail_closed(self):
        target = run.base.independent_target(self.manifest, self.manifest["cases"][0]).to_payload()
        original = [target, target]
        packed = run.compact(original)
        self.assertEqual(run.expand(packed), original)
        bad = deepcopy(packed)
        bad["contexts"][next(iter(bad["contexts"]))] = []
        with self.assertRaises(ValueError):
            run.expand(bad)
        bad = deepcopy(packed)
        bad["payload"][0]["reference"] = {"p984c_context": "missing"}
        with self.assertRaises(ValueError):
            run.expand(bad)
        bad = deepcopy(packed)
        bad["contexts"][run.base.digest([42])] = [42]
        with self.assertRaises(ValueError):
            run.expand(bad)

    def test_retained_consumption_and_wrong_stage_mutations(self):
        if not (run.base.ROOT / run.RESULTS).exists():
            self.skipTest("completed native run not yet retained")
        record = run.base.read(run.RESULTS)
        run.status(self.manifest, record)
        rows = run.expand(record["execution"])["cases"]
        # One new two-remainder layout: independent dense oracle must
        # distinguish predictor substitution, omitted geometry, and each role.
        row = next(r for r in rows if "D38-E1-P1" in r["case_id"])
        self.assertTrue(row["case_passed"])
        case = next(c for c in self.manifest["cases"] if c["case_id"] == row["case_id"])
        for role in run.boundary.ROLES:
            index = next(i for i, o in enumerate(row["observations"]) if o["stage"] == "target_continuation" and o["role"] == role)
            capture = row["consumption_evidence"][index]["value"]
            run.consumer.check_step(capture, case["comparison"])
            bad = deepcopy(capture)
            bad["pass"]["corrector"]["current"] = bad["pass"]["predictor"]["current"]
            with self.assertRaises(ValueError):
                run.consumer.check_step(bad, case["comparison"])
            bad = deepcopy(capture)
            bad["pass"]["corrector"]["descriptor"]["inputs"]["H1_form"] = bad["pass"]["predictor"]["descriptor"]["inputs"]["H1_form"]
            with self.assertRaises(ValueError):
                run.consumer.check_step(bad, case["comparison"])
        bad = deepcopy(record)
        bad["user_accepted"] = True
        with self.assertRaises(ValueError):
            run.status(self.manifest, run.base.seal(bad))


if __name__ == "__main__":
    unittest.main()
