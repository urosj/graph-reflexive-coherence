"""Campaign verifier rejection and pending-window fault controls, bounded only."""

import unittest
from copy import deepcopy

from p991a6_aos_campaign import delivery, fail_before_completion
from p991a6_aos_campaign_cost import forecast
from p991a6_aos_campaign_verify import Capture, compact, expand, verify

from tests.models import test_grc_v4_spark_aos as fixtures


class AOSCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeAOSTests.setUpClass()
        cls.fixture = fixtures.NativeAOSTests()

    def test_final_verifier_and_rejections_at_synthetic_near_domain_state(self):
        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        with cap.installed():
            self.assertTrue(
                model.step_v4_input(delivery("synthetic-audit", 1)).committed
            )
        data = cap.payload()
        cert = self.fixture.certificates[0]
        self.assertEqual(verify(model.configuration, data, cert)["exact_charge"], True)
        for mutate in (
            lambda x: x.update(physical_writes=2),
            lambda x: x["read_inputs"].__setitem__(0, "wrong"),
            lambda x: x["writer_inputs"][0].update(same_read_object=False),
            lambda x: x["writer"]["midpoint"].__setitem__(0, "1"),
            lambda x: x["restart_read"]["H"][0].__setitem__(0, ["2", "2"]),
            lambda x: x["flux"].__setitem__(0, "1"),
            lambda x: x["consumed_read"]["current_midpoint"].__setitem__(0, "1"),
        ):
            bad = deepcopy(data)
            mutate(bad)
            with self.assertRaises((ValueError, AssertionError)):
                verify(model.configuration, bad, cert)

    def test_compact_roundtrip_and_independent_recheck_without_native_calls(self):
        from unittest.mock import patch

        from pygrc.models.grc_v4_spark_aos import SparkAOSKernel

        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        with cap.installed():
            self.assertTrue(model.step().committed)
        full = cap.payload()
        encoded = compact(full)
        rebuilt = expand(encoded, full["before"])
        cert = self.fixture.certificates[0]
        with (
            patch.object(
                SparkAOSKernel, "step", side_effect=AssertionError("native reuse")
            ),
            patch.object(
                SparkAOSKernel,
                "_admitted_read",
                side_effect=AssertionError("native reuse"),
            ),
        ):
            actual = verify(model.configuration, rebuilt, cert, compact=True)
        expected = verify(model.configuration, full, cert)
        self.assertEqual(
            actual["full_step_error_upper"], expected["full_step_error_upper"]
        )
        for change in (
            lambda d: d["after"]["W_A"].__setitem__(-1, "1"),
            lambda d: d["writer"]["midpoint"].__setitem__(0, "1"),
            lambda d: d["consumed_read"]["current_midpoint"].__setitem__(0, "1"),
        ):
            bad = deepcopy(rebuilt)
            change(bad)
            with self.assertRaises((ValueError, AssertionError)):
                verify(model.configuration, bad, cert, compact=True)

    def test_six_faults_at_pending_window_and_once_only_retry(self):
        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        pressure = []
        with cap.installed():
            for beat in (1, 2):
                self.assertTrue(
                    model.step_v4_input(delivery("synthetic-pending", beat)).committed
                )
            self.assertEqual(
                len(model._operation._published.completion.observations), 2
            )
            forks = fail_before_completion(model, "current", 2, pressure)
            result = model.step_v4_input(delivery("synthetic-complete", 3))
            self.assertEqual(result.local_gain, 1)
            for fork, req in forks:
                result = fork.step_v4_input(req)
                self.assertTrue(result.committed)
                self.assertEqual(result.local_gain, 0)
                self.assertEqual(
                    fork.configuration.current, model.configuration.current
                )
        self.assertEqual(len(pressure), 6)

    def test_forecast_reports_profiling_target_overrun(self):
        samples = {
            r: [
                {
                    "seconds": 6,
                    "native_seconds": 4,
                    "resource_bits": 144,
                    "conductance_bits": 193,
                }
            ]
            * 20
            for r in ("current", "reset")
        }
        _, estimate = forecast(samples, 10, 1)
        self.assertFalse(estimate["within_budget"])
        self.assertEqual(estimate["campaign_cap_seconds"], 1800)
