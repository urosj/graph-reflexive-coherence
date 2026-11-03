"""Actual beat-205 rational-distance regression and joint-history pressure."""

import json
import lzma
import unittest
from dataclasses import replace

from flint import ctx, fmpq as Q
from p991a6_arg2b_campaign import FIXTURE, metric_bounds
from p991a6_rg2b_campaign import ROOT
from arg2b_native_spark_pressure_oracle import joint_distances, state_X
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK


class ExactJointMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = json.loads(lzma.decompress((ROOT / FIXTURE).read_bytes()))
        cls.state = ExactConductanceState.from_canonical_bytes(
            canonical_json_bytes(cls.v["state"])
        )

    def metric(self, state=None, parameter=None):
        return metric_bounds(
            self.state.graph.to_payload(),
            self.v["curve"],
            state or self.state,
            parameter
            if parameter is not None
            else self.v["native_membership"]["parameter"],
            self.v["radius"],
        )

    def test_actual_outside_state_exactly_matches_native_upper(self):
        lo, hi = self.metric()
        self.assertEqual(lo, hi)
        self.assertEqual(hi, Q(self.v["native_membership"]["squared_norm"]))
        self.assertGreater(lo, 1)
        self.assertFalse(self.v["native_membership"]["inside"])

    def test_old_arb_conversion_introduces_spurious_positive_radius(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            c, y = joint_distances(
                self.state.graph.to_payload(),
                self.v["curve"],
                state_X(self.state),
                self.v["native_membership"]["parameter"],
            )
            old_hi = max(c.upper().fmpq(), y.upper().fmpq()) / Q(self.v["radius"]) ** 2
        self.assertGreater(old_hi, self.metric()[1])
        self.assertLess(old_hi - self.metric()[1], Q(1, 10**220))

    def test_history_and_shared_parameter_remain_consequential(self):
        w = list(self.state.W_A)
        w[0] = str(Q(w[0]) * 2)
        self.assertGreater(
            self.metric(replace(self.state, W_A=tuple(w)))[0], self.metric()[1]
        )
        self.assertNotEqual(self.metric(parameter="0"), self.metric())

    def test_invalid_parameter_rejects(self):
        for parameter in ("-1/100", "101/100"):
            with self.assertRaises(ValueError):
                self.metric(parameter=parameter)


if __name__ == "__main__":
    unittest.main()
