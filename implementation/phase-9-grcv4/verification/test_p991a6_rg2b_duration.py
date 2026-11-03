"""The common typed public transaction honors each admitted duration."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pygrc.models.grc_9_v4_api_lifecycle import GRC9V4PublicOperation
from pygrc.models import grc_9_v4_spark_owner as spark
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_state import FrozenJSONMap


class PolicyDurationTests(unittest.TestCase):
    def test_all_ten_typed_dispatches_use_policy_and_reject_wrong_duration(self):
        for candidate in ("C", "A"):
            for realization in ("OS", "CI", "PC", "CI_PC", "RG2b"):
                duration = (
                    (8 if candidate == "C" else 16) if realization == "RG2b" else 32
                )
                operation = SimpleNamespace(
                    _spark_scope=object(),
                    configuration=lambda d=duration: SimpleNamespace(
                        policy=SimpleNamespace(step_duration=str(d))
                    ),
                )
                request = GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1", "typed", duration, FrozenJSONMap({})
                )
                with (
                    self.subTest(candidate=candidate, realization=realization),
                    patch.object(spark, "transact", return_value="selected") as call,
                ):
                    self.assertEqual(
                        GRC9V4PublicOperation.step_enabled(operation, request),
                        "selected",
                    )
                    call.assert_called_once_with(
                        operation,
                        dict(kind="step", duration=str(duration), operation_id="typed"),
                    )
                    for wrong in (0, 8, 16, 32):
                        if wrong == duration:
                            continue
                        call.reset_mock()
                        r = GRC9V4PublicOperation.step_enabled(
                            operation,
                            GRCV4StepRequestInput(
                                "grcv4-step-request-input-v1",
                                "wrong",
                                wrong,
                                FrozenJSONMap({}),
                            ),
                        )
                        self.assertFalse(r.committed)
                        call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
