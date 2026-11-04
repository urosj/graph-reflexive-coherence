"""Cross-family public boundaries; no source-to-completion trajectory rerun."""

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_crossing import GRC9V4BranchRequest
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models import grc_9_v4_spark_owner as owner
from p991a7_support import ROOT, ROSTER, inputs


class NativeSparkIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = {
            family: GRC9V4SparkConfiguration.from_payload(
                inputs(ROOT, tag)["source_configuration"]
            )
            for family, tag, _ in ROSTER
        }

    def test_all_ten_public_wire_and_warm_cold_empty_journal_persistence(self):
        for family, config in self.configs.items():
            with (
                self.subTest(family=family),
                patch.object(
                    type(owner.kernel(config)),
                    "step",
                    side_effect=AssertionError("unexpected numerical step"),
                ),
            ):
                model = GRC9V4.from_config(config.to_payload())
                state, before = model.state, model.snapshot()
                self.assertEqual(
                    state.lifecycle.current.to_payload(), config.current.to_payload()
                )
                self.assertEqual(
                    state.lifecycle.reset.to_payload(), config.reset.to_payload()
                )
                self.assertNotEqual(config.current, config.reset)
                self.assertEqual(GRC9V4.from_state(state).snapshot(), before)
                self.assertEqual(model.duplicate().snapshot(), before)
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "native.json"
                    model.save(path)
                    self.assertEqual(GRC9V4.load(path).snapshot(), before)
                origin = before["owner"]["origin"]
                with owner._SCOPES_LOCK:
                    live = owner._SCOPES.pop(origin)
                try:
                    cold = GRC9V4.from_state(before)
                    self.assertEqual(cold.snapshot(), before)
                    self.assertEqual(cold.support_status(), model.support_status())
                finally:
                    with owner._SCOPES_LOCK:
                        owner._SCOPES[origin] = live
                self.assertEqual(model.snapshot(), before)

    def test_all_ten_reject_foreign_wire_identity_and_readable_role_substitution(self):
        profiles, models = set(), set()
        for family, config in self.configs.items():
            with self.subTest(family=family):
                model = GRC9V4(config)
                profiles.add(model.active_profile_id)
                models.add(model.active_model_identity)
                before = model.snapshot()
                for key in ("numerical_policy", "exact_backend"):
                    wrong = deepcopy(config.to_payload())
                    wrong["execution"][key] = "invented"
                    with self.assertRaises(ValueError):
                        GRC9V4.from_config(wrong)
                state = model.state
                forged = replace(
                    state,
                    lifecycle=replace(
                        state.lifecycle,
                        configuration=replace(config, current=config.reset),
                    ),
                )
                with self.assertRaises(ValueError):
                    model.set_state(forged)
                self.assertEqual(model.snapshot(), before)
                with self.assertRaises(ValueError):
                    model.snapshot(replay_mode="state_only")
        self.assertEqual(len(profiles), 10)
        self.assertEqual(len(models), 10)

    def test_all_ten_exact_resources_cannot_silently_enter_legacy_branch(self):
        for family, config in self.configs.items():
            with self.subTest(family=family):
                model = GRC9V4(config)
                before = model.snapshot()
                request = GRC9V4BranchRequest(
                    "disabled-native",
                    model.lifecycle_digest,
                    "disable",
                    {
                        "legacy_config": {},
                        "current_incoming_weights": [],
                        "reset_incoming_weights": [],
                        "current_incoming_flux": [],
                        "reset_incoming_flux": [],
                    },
                )
                result = model.migrate_branch(request)
                self.assertFalse(result.committed)
                self.assertIn("explicit lossless branch successor", result.reason)
                self.assertEqual(model.snapshot(), before)
                self.assertEqual(model.compatibility_branch, "enabled_spark_v4")
                self.assertFalse(model.support_status()["branch_crossing_available"])


if __name__ == "__main__":
    unittest.main()
