"""Campaign verifier rejection and pending-window fault controls, bounded only."""

import unittest
from copy import deepcopy

from p991a6_cci_campaign import delivery, fail_before_completion
from p991a6_cci_campaign_cost import forecast
from p991a6_cci_campaign_verify import Capture, verify

from tests.models import test_grc_v4_spark_cci as fixtures


class CCICampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeCCITests.setUpClass()
        cls.fixture = fixtures.NativeCCITests()

    def test_final_verifier_and_rejections_at_synthetic_near_domain_state(self):
        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        with cap.installed():
            self.assertTrue(
                model.step_v4_input(delivery("synthetic-audit", 1)).committed
            )
        data = cap.payload()
        cert = self.fixture.certificates[0]
        self.assertEqual(verify(model.configuration, data, cert)["exact_charge"], "21")
        for mutate in (
            lambda x: x.update(physical_writes=2),
            lambda x: x["root_inputs"][0]["C"].__setitem__(0, "0"),
            lambda x: x["flux"].__setitem__(0, "1"),
            lambda x: x["root_inputs"][0]["current_midpoint"].__setitem__(0, "1"),
        ):
            bad = deepcopy(data)
            mutate(bad)
            with self.assertRaises((ValueError, AssertionError)):
                verify(model.configuration, bad, cert)

    def test_five_faults_at_pending_window_and_once_only_retry(self):
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
        self.assertEqual(len(pressure), 5)

    def test_retained_counterexample_checks_both_independent_bounds(self):
        import json
        import lzma

        from flint import fmpq as Q
        from p991a6_cci_campaign import BASE, ROOT, seal

        from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
        from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

        with lzma.open(
            ROOT / BASE / "P9-9.1a.6-CCI.5-FailedAudit.json.xz", "rt"
        ) as stream:
            value = json.load(stream)
        self.assertEqual(value, seal(value))
        import base64
        from hashlib import sha256

        files = {}
        for ref in value["files"]:
            raw = base64.b64decode(ref["base64"], validate=True)
            self.assertEqual(sha256(raw).hexdigest(), ref["sha256"])
            files[ref["path"]] = raw
        from p991a6_cci_campaign import FILES

        prefix = [
            json.loads(line)
            for line in lzma.decompress(files[FILES["current"]]).splitlines()
        ]
        previous = None
        for row in prefix:
            self.assertEqual(row, seal(row))
            self.assertEqual(row["previous_record_digest"], previous)
            previous = row["record_digest"]
        self.assertEqual(len(prefix), 181)
        self.assertEqual(
            prefix[-1]["stage"]["after"], value["diagnostic"]["stage"]["before"]
        )
        d = value["diagnostic"]
        report = verify(
            GRC9V4SparkConfiguration.from_payload(d["config"]),
            d["stage"],
            CompletionCertificate.from_payload(d["certificate"]),
        )
        self.assertEqual(report, d["report"])
        self.assertGreater(
            Q(report["direct_error_upper"]), Q(report["full_step_error_upper"])
        )
        self.assertLess(Q(report["direct_error_upper"]), Q(d["certificate_budget"]))

    def test_forecast_refuses_costlier_campaign(self):
        samples = {
            r: [{"seconds": 3, "native_seconds": 2, "resource_bits": 144}] * 20
            for r in ("current", "reset")
        }
        _, estimate = forecast(samples, 10, 1)
        self.assertFalse(estimate["within_budget"])
        self.assertEqual(estimate["campaign_cap_seconds"], 1800)
