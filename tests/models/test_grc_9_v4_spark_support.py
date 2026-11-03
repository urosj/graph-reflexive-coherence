"""Public declaration support never substitutes for an occurrence's evidence."""

import json
import lzma
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models.grc_9_v4_spark_owner import CompletionPublication
from pygrc.models import grc_9_v4_spark_support as support
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
from p991a7_support import ROSTER, inputs  # noqa: E402


class NativeSparkSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = {
            (family, role): GRC9V4SparkConfiguration.from_payload(
                value[role + "_configuration"]
            )
            for family, tag, _ in ROSTER
            for value in [inputs(ROOT, tag)]
            for role in ("source", "target")
        }

    def test_all_twenty_public_declarations_are_specific_and_read_only(self):
        for (family, role), config in self.configs.items():
            with self.subTest(family=family, role=role):
                model = GRC9V4(config)
                before = model.snapshot()
                status = model.support_status()
                caps = model.list_capabilities()
                self.assertTrue(status["optional_completion"])
                self.assertTrue(status["native_endpoint_verified"])
                self.assertEqual(status["matched_subject"], role)
                self.assertFalse(status["current_occurrence_completed"])
                self.assertFalse(status["full_GRC9V4_conformance"])
                self.assertFalse(status["hierarchy_tracking"])
                self.assertFalse(status["branch_crossing_available"])
                self.assertIn("completed_spark", caps)
                self.assertNotIn("hierarchy_tracking", caps)
                realization = config.reference.profile.identity_payload.realization.lower().replace(
                    "+", "_"
                )
                self.assertEqual(
                    {c for c in caps if c.startswith("v4_realization_")},
                    {"v4_realization_" + realization},
                )
                self.assertEqual(
                    model.list_supported_profiles(),
                    {config.reference.profile.complete_profile_id},
                )
                self.assertEqual(
                    model.list_supported_model_identities(), {config.model_identity}
                )
                self.assertEqual(model.snapshot(), before)

    def test_changed_policy_charge_and_no_policy_do_not_inherit_support(self):
        for (family, role), config in self.configs.items():
            if role != "source":
                continue
            for key, value in [
                ("step_duration", "1"),
                ("minimum_beats", 3),
                ("contrast", "1/4"),
            ]:
                policy = replace(config.policy, **{key: value})
                variant = replace(
                    config,
                    specialization=config.specialization.with_completion_policy(policy),
                )
                self.assertIsNone(support.match(variant), (family, key))
            variant = replace(
                config,
                current=replace(
                    config.current,
                    C=tuple("2" for _ in config.current.C),
                    charge=str(2 * len(config.current.C)),
                ),
                reset=replace(
                    config.reset,
                    C=tuple("2" for _ in config.reset.C),
                    charge=str(2 * len(config.reset.C)),
                ),
            )
            self.assertIsNone(support.match(variant), family)
            variant = replace(
                config,
                specialization=config.specialization.with_completion_policy(None),
            )
            self.assertIsNone(support.match(variant), family)
            model = GRC9V4(variant)
            self.assertNotIn("completed_spark", model.list_capabilities())
            self.assertFalse(model.support_status()["native_endpoint_verified"])

    def test_occurrence_and_declaration_are_independent(self):
        config = self.configs["C_OS", "target"]
        empty = CompletionPublication()
        completed = replace(
            empty,
            event=FrozenJSONMap({"occurrence": "accepted-event"}),
            evidence=FrozenJSONMap({"decision": "completed"}),
        )
        self.assertFalse(support.status(config, empty)["current_occurrence_completed"])
        self.assertTrue(
            support.status(config, completed)["current_occurrence_completed"]
        )
        self.assertFalse(
            support.status(config, replace(completed, event=None))[
                "current_occurrence_completed"
            ]
        )
        self.assertTrue(support.status(config, empty)["native_endpoint_verified"])
        self.assertFalse(
            support.status(config, completed)["cross_process_global_uniqueness"]
        )

    def test_real_completed_and_reset_publications_report_separately(self):
        # Inspect retained native completion metadata; do not replay old journals.
        path = (
            ROOT
            / "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-ARG2b.5-checkpoints.jsonl.xz"
        )
        with lzma.open(path, "rt") as stream:
            rows = [json.loads(line) for line in stream]
        self.assertEqual(len(rows), 8)

        # Every exact checkpoint remains bound by the campaign reader; locate its
        # saved completion record recursively, independently of reporter code.
        def find(value):
            if isinstance(value, dict):
                if "configuration" in value and "completion" in value:
                    yield value
                for v in value.values():
                    yield from find(v)
            elif isinstance(value, list):
                for v in value:
                    yield from find(v)

        completed = 0
        for row in rows:
            for publication in find(row):
                cp = publication["completion"]
                if (
                    not cp.get("evidence")
                    or cp["evidence"].get("decision") != "completed"
                ):
                    continue
                config = GRC9V4SparkConfiguration.from_payload(
                    publication["configuration"]
                )
                state = CompletionPublication(
                    event=None if cp["event"] is None else FrozenJSONMap(cp["event"]),
                    evidence=FrozenJSONMap(cp["evidence"]),
                )
                self.assertEqual(
                    support.status(config, state)["current_occurrence_completed"],
                    cp["event"] is not None,
                )
                completed += 1
        self.assertGreater(completed, 0)

    def test_roster_tampering_rejected_without_cached_acceptance(self):
        support.registry()
        original = Path.read_bytes

        def changed(path):
            raw = original(path)
            return raw + b" " if path.name == support.ASSET else raw

        with (
            patch.object(Path, "read_bytes", changed),
            self.assertRaisesRegex(ValueError, "support roster"),
        ):
            support.registry()


if __name__ == "__main__":
    unittest.main()
