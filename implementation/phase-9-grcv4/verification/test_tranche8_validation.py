"""Validation reuse must preserve rejection, isolation and selected scope."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import tranche8_validation as v
import tranche8_evidence as index
import tranche8_retained as retained


class SnapshotTests(unittest.TestCase):
    def test_snapshot_drift_isolation_paths_and_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "input.json"
            file.write_text('{"value":[1]}')
            snapshot = v.Snapshot(root)
            bindings = snapshot.bind(["input.json"])
            snapshot.check_bindings(bindings)
            value = snapshot.read("input.json")
            value["value"].append(2)
            self.assertEqual(snapshot.read("input.json"), {"value": [1]})
            with self.assertRaisesRegex(ValueError, "duplicate"):
                snapshot.check_bindings(bindings * 2)
            with self.assertRaisesRegex(ValueError, "source drift"):
                snapshot.check_bindings([dict(path="input.json", sha256="wrong")])
            with self.assertRaisesRegex(ValueError, "nonportable"):
                snapshot.raw("../input.json")
            file.write_text('{"value":[2]}')
            self.assertEqual(snapshot.read("input.json"), {"value": [1]})
            with self.assertRaisesRegex(ValueError, "changed during"):
                snapshot.unchanged()
            self.assertEqual(v.Snapshot(root).read("input.json"), {"value": [2]})
            file.unlink()
            with self.assertRaises(FileNotFoundError):
                snapshot.unchanged()

    def test_cache_is_operation_local_copies_and_config_sensitive(self):
        module = SimpleNamespace(__name__="fixture", ACCEPTANCE="accepted")
        calls = []
        def make():
            calls.append(1)
            if module.ACCEPTANCE != "accepted":
                raise ValueError("not accepted")
            return dict(values=[1])
        wrapped = v.memoized(make)
        first = v.Snapshot(v.ROOT)
        first.modules = [module]
        token = v.ACTIVE.set(first)
        try:
            wrapped()["values"].append(2)
            self.assertEqual(wrapped(), dict(values=[1]))
            self.assertEqual(len(calls), 1)
            module.ACCEPTANCE = "rejected"
            with self.assertRaisesRegex(ValueError, "not accepted"):
                wrapped()
            # A different thread must call the original, not this session cache.
            module.ACCEPTANCE = "accepted"
            with ThreadPoolExecutor(max_workers=1) as pool:
                self.assertEqual(pool.submit(wrapped).result(), dict(values=[1]))
            self.assertEqual(len(calls), 3)
        finally:
            v.ACTIVE.reset(token)
        wrapped()
        self.assertEqual(len(calls), 4)

    def test_hooks_restore_and_do_not_cache_checks(self):
        import p984b_runtime as b
        original = b.read
        with v.validation_session(("p984c_aci_runtime",)) as snapshot:
            self.assertIsNot(b.read, original)
            with self.assertRaisesRegex(ValueError, "nested"):
                with v.validation_session():
                    pass
            rows = b.bind(["pyproject.toml"])
            b.check_bindings(rows)
            rows[0]["sha256"] = "wrong"
            with self.assertRaisesRegex(ValueError, "source drift"):
                b.check_bindings(rows)
            self.assertIn("pyproject.toml", snapshot._bytes)
        self.assertIs(b.read, original)
        self.assertIsNone(v.ACTIVE.get())
        with self.assertRaisesRegex(ValueError, "snapshot root mismatch"):
            with v.validation_session(("p984c_aci_runtime",)):
                with patch.object(b, "ROOT", v.ROOT.parent):
                    b.read("pyproject.toml")
        self.assertIs(b.read, original)
        self.assertIsNone(v.ACTIVE.get())


class ScopeTests(unittest.TestCase):
    def test_selected_dispatch_does_not_build_unrelated_status(self):
        argv = ["index", "verify-retained", "--family", "A_CI", "--checkpoint", "8.4c"]
        with patch.object(sys, "argv", argv), patch.object(index, "checked", side_effect=AssertionError("global check forbidden")), patch.object(index.subprocess, "run") as run:
            index.main()
            command = run.call_args.args[0]
            self.assertTrue(command[1].endswith("tranche8_retained.py"))
            self.assertTrue(command[-2].endswith("p984c_aci_runtime.py"))
            self.assertEqual(command[-1], "--check-retained")
        argv = ["index", "status", "--family", "A_CI", "--checkpoint", "8.4c"]
        with patch.object(sys, "argv", argv), patch.object(index, "checked", side_effect=AssertionError("global check forbidden")), patch.object(index, "family_status", return_value={}) as selected:
            index.main()
            selected.assert_called_once_with(index.ROOT, "A_CI")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            index.family_status(index.ROOT, "A_CI_PC")

    def test_retained_launcher_refuses_execution_and_unindexed_input(self):
        for name, option in (("p984c_aci_runtime.py", "--run"), ("p984c_aci_oracle.py", "--run-oracle"), ("unregistered.py", "--check-retained")):
            with patch.object(sys, "argv", ["retained", str(index.ROOT / index.HERE / name), option]), self.assertRaises(ValueError):
                retained.main()
        from contextlib import nullcontext
        module = SimpleNamespace(INPUTS="foreign.json", RESULTS="foreign-result.json", REVIEW="foreign.md", main=lambda: self.fail("must reject before dispatch"))
        argv = ["retained", str(index.ROOT / index.HERE / "p984c_aci_runtime.py"), "--check-retained"]
        import phase9_implementation_policy as policy
        with ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", argv))
            stack.enter_context(patch.object(retained.importlib, "import_module", return_value=module))
            stack.enter_context(patch.object(retained, "validation_session", return_value=nullcontext()))
            stack.enter_context(patch.object(policy, "restore_packed_evidence"))
            stack.enter_context(patch.object(index.Sources, "raw", side_effect=ValueError("unindexed source")))
            with self.assertRaisesRegex(ValueError, "unindexed"):
                retained.main()

    def test_frozen_producers_and_evidence_were_not_rewritten(self):
        manifest = json.loads((index.ROOT / index.BASE / "P9-8.4c-ACICases.json").read_text())
        for binding in manifest["source_bindings"]:
            if binding["path"].endswith(("p984c_aci_runtime.py", "p984c_aci_oracle.py", "test_p984c_aci_runtime.py")):
                self.assertEqual(hashlib.sha256((index.ROOT / binding["path"]).read_bytes()).hexdigest(), binding["sha256"])
        for name, expected in index.BOUNDARY_ACI_SOURCES.items():
            self.assertEqual(hashlib.sha256((index.ROOT / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
