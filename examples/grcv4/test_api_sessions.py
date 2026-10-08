"""Focused workflow guard tests; the six CLI scenarios provide numerical smoke checks."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from examples.grcv4 import api_sessions as api
from examples.grcv4.session_support import Session, differences, transfer
from pygrc.models.grc_v4_migration import (
    MigrationAdmissionError,
    map_migration,
    migration_history_policy,
)


class SessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        cls.states, cls.backend = cls.session.fixtures("A")
        cls.before = cls.states["CI"]

    def test_conserving_fork_and_original_reset_are_separate(self):
        before = self.before
        old = before.to_payload()
        edited = transfer(before, 0.05)
        self.assertAlmostEqual(sum(edited.current.C), before.Q_target, places=14)
        self.assertEqual(edited.reset, before.reset)
        self.assertEqual(edited.current.W_A, before.current.W_A)
        self.assertNotEqual(edited.scientific_state_id, before.scientific_state_id)
        self.assertEqual(before.to_payload(), old)
        self.assertEqual(
            transfer(before, 0).scientific_state_id, before.scientific_state_id
        )

    def test_comparison_rejects_unequal_horizon_and_unaligned_graph(self):
        for after in (replace(self.before, step_index=1), replace(self.before, time=1)):
            with self.assertRaisesRegex(AssertionError, "equal physical"):
                differences(self.before, after)
        ref = self.before.geometry.reference
        reordered = replace(
            ref.graph, live_node_ids=tuple(reversed(ref.graph.live_node_ids))
        )
        after = replace(self.before, geometry=replace(ref, graph=reordered).geometry())
        with self.assertRaisesRegex(AssertionError, "same graph"):
            differences(self.before, after)
        with self.assertRaisesRegex(AssertionError, "shape mismatch"):
            api.read_difference({"J": [1, 2]}, {"J": [[1, 2]]})

    def test_reset_only_history_change_invalidates_migration_policy(self):
        target = self.states["PC"].geometry.reference
        bound = migration_history_policy(self.before, target)
        modified = replace(
            self.before,
            reset=replace(
                self.before.reset, W_A=tuple(w + 0.01 for w in self.before.reset.W_A)
            ),
        )
        with self.assertRaises(MigrationAdmissionError):
            map_migration(modified, target, bound)

    def test_migration_maps_both_roles_and_records_carrier_loss(self):
        before = replace(
            self.before, reset=replace(self.before.reset, W_A=(1.9, 2.0, 2.1))
        )
        mapped, record = self.session.migrate(
            before, self.states["PC"].geometry.reference
        )
        for role in ("current", "reset"):
            self.assertEqual(getattr(mapped, role).W_A, getattr(before, role).W_A)
            self.assertEqual(getattr(mapped, role).Z_4, (0.0,) * 9)
        self.assertEqual(
            record["policy"]["carrier"]["disposition"], "target_initializer"
        )
        back, record = self.session.migrate(mapped, self.before.geometry.reference)
        self.assertEqual(back.current, before.current)
        self.assertEqual(back.reset, before.reset)
        self.assertEqual(record["policy"]["carrier"]["disposition"], "explicit_loss")
        c = differences(before, mapped)
        self.assertEqual(c["Z_4"], {"before_present": False, "after_present": True})

    def test_expected_rejection_cannot_silently_pass(self):
        with self.assertRaisesRegex(AssertionError, "was admitted"):
            api.rejected(lambda: None, MigrationAdmissionError)
        for steps in (0, -1, True, 1.5):
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                api.run("debug", steps=steps)

    def test_listing_rendering_and_output_guard_do_not_execute(self):
        with patch.object(
            api, "report", side_effect=AssertionError("unwanted execution")
        ):
            out = io.StringIO()
            with patch("sys.argv", ["api_sessions.py", "--list"]), redirect_stdout(out):
                api.main()
            self.assertIn("lifecycle", out.getvalue())
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "saved.json"
                saved = {
                    "schema": "grcv4-api-example-v1",
                    "scenario": "debug",
                    "description": "saved fixture",
                    "result": {},
                }
                path.write_text(json.dumps(saved))
                original = path.read_bytes()
                with (
                    patch(
                        "sys.argv",
                        ["api_sessions.py", "--render-from", str(path), "--json"],
                    ),
                    redirect_stdout(io.StringIO()) as out,
                ):
                    api.main()
                self.assertEqual(json.loads(out.getvalue()), saved)
                with (
                    patch("sys.argv", ["api_sessions.py", "--output", str(path)]),
                    patch("sys.stderr", io.StringIO()),
                    self.assertRaises(SystemExit) as failure,
                ):
                    api.main()
                self.assertEqual(failure.exception.code, 2)
                self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
