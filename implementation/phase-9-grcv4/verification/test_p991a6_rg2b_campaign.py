"""Bounded campaign pressure; no long trajectories."""

import unittest
import json
from copy import deepcopy
from dataclasses import replace

from p991a6_rg2b_campaign import (
    Adapter,
    Capture,
    compact_step,
    digest,
    fail_pending,
    observation,
    setup,
)
from pygrc.models.grc_9_v4 import GRC9V4


class CampaignTests:
    @classmethod
    def setUpClass(cls):
        cls.a = Adapter(cls.family)
        cls.cap = Capture(cls.a)
        with cls.cap.installed():
            cls.models, cls.certs, cls.center, cls.inputs = setup(
                cls.a, cls.cap, deep=False
            )

    def synthetic(self):
        # Same private seam as accepted native lifecycle tests; never a primary.
        from tests.models.test_grc_9_v4_spark_completion import (
            NativeSparkCompletionTests,
        )

        class Fixture:
            event_model = self.models["current"]
            center = self.center
            certificates = tuple(self.certs.values())

        return NativeSparkCompletionTests.synthetic_window_fixture(Fixture())

    def test_full_transition_audit_and_mutations(self):
        model = self.synthetic()
        before = model.configuration
        with self.cap.installed():
            self.assertTrue(model.step().committed)
        step = self.cap.step
        report = self.a.audit(before, step)
        obs = observation(self.a, step.after, before.policy, self.certs["current"])
        self.assertTrue(obs["inside"])
        raw = json.loads(json.dumps(self.a.preflight.transition(step)))
        compact = compact_step(self.a, raw, report, obs)
        self.assertEqual(compact["full_transition_digest"], digest(raw))
        for mutate in (
            lambda d: d["flux"].__setitem__(0, "1"),
            lambda d: d["after"]["C"].__setitem__(0, "2"),
            lambda d: d["section"]["chain"].pop(),
            lambda d: d["restart_section"]["chain"].pop(),
            lambda d: d["final_current"].__setitem__(0, ["1", "1"]),
        ):
            bad = deepcopy(raw)
            mutate(bad)
            with self.assertRaises((ValueError, AssertionError)):
                self.a.audit(before, self.a.preflight.decoded(bad))

    def test_pending_rollback_and_once_only_retry(self):
        model = self.synthetic()
        pressure = []
        with self.cap.installed():
            for beat in (1, 2):
                self.assertTrue(
                    model.step_v4_input(self.a.delivery("synthetic", beat)).committed
                )
            self.assertEqual(
                len(model._operation._published.completion.observations), 2
            )
            forks = fail_pending(self.a, model, 2, pressure)
            self.assertEqual(
                model.step_v4_input(self.a.delivery("synthetic", 3)).local_gain, 1
            )
            for fork, req in forks:
                result = fork.step_v4_input(req)
                self.assertTrue(result.committed)
                self.assertEqual(result.local_gain, 0)
                self.assertEqual(
                    fork.configuration.current, model.configuration.current
                )
        self.assertEqual(len(pressure), 6 if self.family == "A_RG2b" else 5)

    def test_full_diagnostic_reconstruction(self):
        model = GRC9V4(
            replace(
                self.models["current"].configuration,
                current=self.center,
                reset=self.center,
            )
        )
        before = model.configuration
        with self.cap.installed():
            self.assertTrue(model.step().committed)
        raw = self.a.preflight.transition(self.cap.step)
        self.a.native._section_witness.cache_clear()
        rebuilt = self.a.kernel(before.reference.graph, before.reference.profile).step(
            before.current, str(self.a.duration)
        )
        self.assertEqual(digest(raw), digest(self.a.preflight.transition(rebuilt)))

    def test_typed_duration_matches_ordinary_and_wrong_duration_rolls_back(self):
        from pygrc.models.grc_v4 import GRCV4StepRequestInput
        from pygrc.models.grc_v4_state import FrozenJSONMap

        config = replace(
            self.models["current"].configuration, current=self.center, reset=self.center
        )
        ordinary, typed = GRC9V4(config), GRC9V4(config)
        self.assertTrue(ordinary.step().committed)
        self.assertTrue(
            typed.step_v4_input(self.a.delivery("typed-duration", 1)).committed
        )
        self.assertEqual(ordinary.configuration.current, typed.configuration.current)
        before = typed.snapshot()
        for wrong in (0, 32, 16 if self.a.duration == 8 else 8):
            result = typed.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1",
                    "wrong-" + str(wrong),
                    wrong,
                    FrozenJSONMap({}),
                )
            )
            self.assertFalse(result.committed)
            self.assertEqual(typed.snapshot(), before)


class CRG2bCampaignTests(CampaignTests, unittest.TestCase):
    family = "C_RG2b"


class ARG2bCampaignTests(CampaignTests, unittest.TestCase):
    family = "A_RG2b"


if __name__ == "__main__":
    unittest.main()
