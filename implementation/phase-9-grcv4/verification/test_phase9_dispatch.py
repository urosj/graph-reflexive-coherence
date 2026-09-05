"""Focused P9-1.6 dispatch/authority smoke tests; not the P9-1.7 audit suite."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import audit_phase9 as audit

SCRIPTS = audit.ROOT / audit.SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from active_phase import phase9_present, verification_script  # noqa: E402


class DispatchTests(unittest.TestCase):
    def test_current_tree_selects_successor(self):
        self.assertEqual(
            verification_script(audit.ROOT), audit.ROOT / audit.HERE / "audit_phase9.py"
        )

    def test_deleted_marker_cannot_downgrade_history(self):
        with (
            patch.object(Path, "exists", return_value=False),
            patch(
                "active_phase.subprocess.run",
                return_value=subprocess.CompletedProcess([], 0),
            ),
        ):
            self.assertTrue(phase9_present(audit.ROOT))

    def test_pre_phase9_uses_historical_route(self):
        with (
            patch.object(Path, "exists", return_value=False),
            patch(
                "active_phase.subprocess.run",
                return_value=subprocess.CompletedProcess([], 1),
            ),
        ):
            self.assertEqual(
                verification_script(audit.ROOT),
                audit.ROOT
                / audit.INV
                / "scripts/audit_grcv4_post_d10_specifications.py",
            )

    def test_normal_alias_uses_shared_dispatch(self):
        spec = importlib.util.spec_from_file_location(
            "side_tool_runner", SCRIPTS / "run.py"
        )
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        with (
            patch.object(sys, "argv", ["run.py", "verify-post-d10-specifications"]),
            patch.object(
                runner, "verification_script", return_value=Path("/test/successor.py")
            ),
            patch.object(
                runner.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0),
            ) as invoked,
        ):
            self.assertEqual(runner.main(), 0)
            self.assertEqual(
                invoked.call_args.args[0], [sys.executable, "/test/successor.py"]
            )

    def test_success_marker_does_not_override_failed_command(self):
        result = subprocess.CompletedProcess(
            [], 1, "PHASE9_SUCCESSOR_VERIFICATION_PASS", "failure"
        )
        with patch.object(audit.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "failed"):
                audit.run_logged(["test"], audit.ROOT, "false_marker", [])

    def test_current_boundary_remains_planning_only(self):
        policy = audit.validate_policy(audit.ROOT)
        self.assertEqual(policy["authorization_effect"], audit.EFFECT)
        self.assertEqual(policy["accepted_generic_runtime_support"], [])

    def test_current_tree_is_admitted(self):
        self.assertGreater(
            audit.validate_tree(audit.ROOT)["protected_baseline_files"], 135
        )

    def reject_policy_mutation(self, change, message):
        original_read = audit.read
        value = deepcopy(original_read(audit.ROOT / audit.POLICY))
        change(value)
        value["record_digest"] = audit.sha(
            audit.canonical({k: v for k, v in value.items() if k != "record_digest"})
        )
        with patch.object(
            audit,
            "read",
            side_effect=lambda path: (
                value if path == audit.ROOT / audit.POLICY else original_read(path)
            ),
        ):
            with self.assertRaisesRegex(ValueError, message):
                audit.validate_policy(audit.ROOT)

    def test_rehashed_planning_flag_cannot_enable_runtime(self):
        self.reject_policy_mutation(
            lambda p: p["authorization_effect"].update(runtime_authorized=True),
            "cannot grant runtime",
        )

    def test_implementation_state_needs_separate_policy(self):
        self.reject_policy_mutation(
            lambda p: p.update(active_phase="implementation"), "separate accepted P9-G1"
        )

    def test_rehashed_allowlist_cannot_add_runtime_path(self):
        self.reject_policy_mutation(
            lambda p: p["exact_mutation_paths"].append("src/pygrc/models/grc_v4.py"),
            "scope widened",
        )

    def test_stale_opening_hash_rejects(self):
        self.reject_policy_mutation(
            lambda p: p["opening_binding"].update(sha256="0" * 64),
            "opening binding mismatch",
        )

    def test_planned_roster_cannot_advertise_support(self):
        self.reject_policy_mutation(
            lambda p: p["accepted_generic_runtime_support"].append("C_OS"),
            "cannot advertise support",
        )

    def test_untracked_runtime_path_is_rejected(self):
        original_git = audit.git

        def injected(root, *args):
            data = original_git(root, *args)
            return (
                data + b"src/pygrc/models/grc_v4.py\0"
                if args[:2] == ("ls-files", "--others")
                else data
            )

        with patch.object(audit, "git", side_effect=injected):
            with self.assertRaisesRegex(
                ValueError, "unauthorized planning-tree changes"
            ):
                audit.validate_tree(audit.ROOT)


if __name__ == "__main__":
    unittest.main()
