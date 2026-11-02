"""Campaign verifier rejection and pending-window fault controls, bounded only."""

import unittest
from copy import deepcopy

from p991a6_acipc_campaign import delivery, fail_before_completion
from p991a6_acipc_campaign_cost import forecast
from p991a6_acipc_campaign_verify import Capture, compact, expand, verify

from tests.models import test_grc_v4_spark_acipc as fixtures


class ACIPCCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeACIPCTests.setUpClass()
        cls.fixture = fixtures.NativeACIPCTests()

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
            lambda x: x["carrier_writer"]["midpoint"][0].__setitem__(0, "1"),
            lambda x: x["writer_inputs"][1].update(same_read_object=False),
            lambda x: x["sequence"].reverse(),
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

        from pygrc.models.grc_v4_spark_acipc import SparkACIPCKernel

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
                SparkACIPCKernel, "step", side_effect=AssertionError("native reuse")
            ),
            patch.object(
                SparkACIPCKernel,
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
            lambda d: d["after"]["Z_4"][0].__setitem__(0, "1/65536"),
            lambda d: d["carrier_writer"]["midpoint"][0].__setitem__(0, "1"),
            lambda d: d["consumed_read"]["current_midpoint"].__setitem__(0, "1"),
        ):
            bad = deepcopy(rebuilt)
            change(bad)
            with self.assertRaises((ValueError, AssertionError)):
                verify(model.configuration, bad, cert, compact=True)

    def test_seven_faults_at_pending_window_and_once_only_retry(self):
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
        self.assertEqual(len(pressure), 7)

    def test_read_witness_reuse_requires_full_equality_and_connected_predecessor(self):
        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        with cap.installed():
            self.assertTrue(model.step().committed)
            first = compact(cap.payload())
            self.assertTrue(model.step().committed)
        full = cap.payload()
        encoded = compact(full, first["restart_read"])
        self.assertEqual(encoded["consumed_read"], {"previous_restart": True})
        with self.assertRaisesRegex(ValueError, "missing preceding read witness"):
            expand(encoded, full["before"])
        rebuilt = expand(encoded, full["before"], first["restart_read"])
        verify(model.configuration, rebuilt, self.fixture.certificates[0], compact=True)
        wrong = deepcopy(first["restart_read"])
        wrong["subject_digest"] = "wrong"
        self.assertNotEqual(
            compact(full, wrong)["consumed_read"], {"previous_restart": True}
        )
        with self.assertRaises((ValueError, AssertionError)):
            verify(
                model.configuration,
                expand(encoded, full["before"], wrong),
                self.fixture.certificates[0],
                compact=True,
            )

    def test_forecast_reports_profiling_target_overrun(self):
        samples = {
            r: [
                {
                    "seconds": 6,
                    "native_seconds": 4,
                    "resource_bits": 144,
                    "conductance_bits": 193,
                    "carrier_bits": 193,
                }
            ]
            * 20
            for r in ("current", "reset")
        }
        _, estimate = forecast(samples, 10, 1)
        self.assertFalse(estimate["within_budget"])
        self.assertEqual(estimate["campaign_cap_seconds"], 1800)

    def test_independent_root_cache_preserves_checks_and_uncached_results(self):
        import acipc_native_spark_campaign_cache as cache
        from p991a6_acipc_campaign_verify import _verify_uncached

        model = self.fixture.synthetic_window_fixture()
        cap = Capture()
        cert = self.fixture.certificates[0]
        with cap.installed():
            self.assertTrue(model.step().committed)
        data = cap.payload()
        cache.clear()
        expected = _verify_uncached(model.configuration, data, cert)
        self.assertEqual(verify(model.configuration, data, cert), expected)
        first = cache.info()
        self.assertEqual(verify(model.configuration, data, cert), expected)
        self.assertEqual(cache.info()["misses"], first["misses"])
        self.assertGreater(cache.info()["hits"], first["hits"])
        bad = deepcopy(data)
        bad["consumed_read"]["proposal_residual"] = ["0", "0"]
        with self.assertRaisesRegex(AssertionError, "actual full-input root residual"):
            verify(model.configuration, bad, cert, compact=True)
        import acipc_native_spark_oracle as original

        self.assertIs(original.Reference, cache._Reference)

    def test_independent_root_cache_binds_both_histories_precision_and_exact_balls(
        self,
    ):
        import acipc_native_spark_campaign_cache as cache
        from cos_native_spark_oracle import matrix, vector
        from flint import arb, arb_mat, ctx
        from flint import fmpq as Q

        from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

        state = self.fixture.event_model.configuration.current
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            ref = cache.CachedReference(state.graph.to_payload())
            C, W, Z = (
                arb_mat(vector(state.C)),
                arb_mat(vector(state.W_A)),
                arb_mat(matrix(state.Z_4)),
            )
            cache.clear()
            first = ref.selected(C, W, Z)
            expected = arb_mat(first["source"])
            first["source"][0, 0] = 7
            self.assertEqual(
                cache._ball_key(ref.selected(C, W, Z)["source"]),
                cache._ball_key(expected),
            )
            misses = cache.info()["misses"]
            changedW = arb_mat(W)
            changedW[0, 0] += Q(1, 2**100)
            ref.selected(C, changedW, Z)
            changedZ = arb_mat(Z)
            changedZ[0, 0] += Q(1, 2**100)
            ref.selected(C, W, changedZ)
            changedC = arb_mat(C)
            changedC[0, 0] += Q(1, 2**100)
            ref.selected(changedC, W, Z)
            widened = arb_mat(C)
            widened[0, 0] += arb(0, Q(1, 2**200))
            ref.selected(widened, W, Z)
            self.assertEqual(cache.info()["misses"], misses + 4)
            with ctx.workprec(1024):
                ref.selected(C, W, Z)
            self.assertEqual(cache.info()["misses"], misses + 5)
            for k in range(12):
                z = arb_mat(Z)
                z[0, 0] += Q(k + 1, 2**110)
                ref.selected(C, W, z)
            self.assertEqual(cache.info()["entries"], cache.LIMIT)
