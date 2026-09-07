"""Pressure path presentation fidelity, original retrieval, and portable export."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import evidence_paths as p


ROOT = Path(__file__).resolve().parents[3]


class EvidencePathTests(unittest.TestCase):
    def test_retained_phase9_text_has_no_machine_specific_locations(self):
        names = subprocess.check_output(
            ["git", "ls-files", p.PHASE, "implementation/Phase-9-GRCV4*"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        for name in names:
            if Path(name).suffix in {".json", ".md", ".txt"}:
                with self.subTest(path=name):
                    self.assertIsNone(
                        re.search(
                            r"/(?:home|Users)/[^/\s\"'\\]+/|/tmp/|/mnt/data/",
                            (ROOT / name).read_text(),
                        )
                    )

    def test_locations_preserve_values_and_distinct_temporary_roots(self):
        checkout = "/home/example/work/graph-reflexive-coherence"
        source = json.dumps(
            {
                "module": checkout + "/src/pygrc/models/grc_v4_step.py",
                "cwd": checkout,
                "python": checkout + "/.venv/bin/python",
                "other_project": checkout + "-other/src/model.py",
                "first": "/tmp/run-one/repository/src/model.py",
                "second": "/tmp/run-two/repository/src/model.py",
                "status": "failed",
                "count": 25,
                "value": -0.0,
                "sha256": "0" * 64,
            }
        )
        result = json.loads(p.normalize_text(source))
        self.assertEqual(result["module"], "src/pygrc/models/grc_v4_step.py")
        self.assertEqual(result["cwd"], ".")
        self.assertEqual(result["python"], ".venv/bin/python")
        self.assertEqual(result["other_project"], checkout + "-other/src/model.py")
        self.assertEqual(
            result["first"], p.SCRATCH + "/temporary/run-one/repository/src/model.py"
        )
        self.assertEqual(
            result["second"], p.SCRATCH + "/temporary/run-two/repository/src/model.py"
        )
        for key in ("status", "count", "value", "sha256"):
            self.assertEqual(
                json.dumps(result[key]), json.dumps(json.loads(source)[key])
            )
        self.assertEqual(
            p.normalize_text(p.normalize_text(source)), p.normalize_text(source)
        )
        self.assertEqual(
            p.normalize_text(
                "/Users/example/work/graph-reflexive-coherence/tests/a.py"
            ),
            "tests/a.py",
        )

    def test_external_environment_is_not_misidentified_as_project_source(self):
        self.assertEqual(
            p.normalize_text("/home/example/.cache/pip"), "<user-cache>/pip"
        )
        self.assertEqual(
            p.normalize_text("/usr/share/fonts/example.ttf"),
            "<system-fonts>/example.ttf",
        )
        self.assertEqual(
            p.normalize_text("#!/usr/bin/env python3"), "#!/usr/bin/env python3"
        )
        self.assertEqual(
            p.normalize_text("/opt/_internal/cpython-3.12/lib/x"),
            "<numpy-build-environment>/lib/x",
        )
        locator = p.normalize_text("/mnt/data/p931_audit/stress.py")
        path, pointer = locator.split("#")
        value = json.loads((ROOT / path).read_bytes())
        for key in pointer.split("/")[1:]:
            value = value[int(key)] if isinstance(value, list) else value[key]
        self.assertIn("def ", value)

    def test_all_presentations_retrieve_exact_git_preimages(self):
        manifest = p.load_manifest(ROOT)
        self.assertEqual(p.verify(ROOT)["files"], 18)
        for row in manifest["files"]:
            with self.subTest(path=row["path"]):
                original = p.original_bytes(ROOT, manifest, row)
                current = (ROOT / row["path"]).read_bytes()
                self.assertEqual(p.present(original), current)
                self.assertTrue(
                    p.permits(
                        manifest,
                        row["path"],
                        row["original_blob"],
                        row["presented_blob"],
                    )
                )
                for item in row.get("embedded_presentations", []):
                    for raw, key in (
                        (original, "original_sha256"),
                        (current, "presented_sha256"),
                    ):
                        value = json.loads(raw)
                        for part in item["pointer"].split("/")[1:]:
                            part = part.replace("~1", "/").replace("~0", "~")
                            value = (
                                value[int(part)]
                                if isinstance(value, list)
                                else value[part]
                            )
                        self.assertEqual(
                            hashlib.sha256(value.encode()).hexdigest(), item[key]
                        )

    def test_changed_outcome_hash_or_roster_cannot_self_authorize(self):
        manifest = p.load_manifest(ROOT)
        row = manifest["files"][0]
        self.assertFalse(
            p.permits(manifest, row["path"], row["original_blob"], "f" * 40)
        )
        self.assertFalse(
            p.permits(
                manifest, "unlisted.json", row["original_blob"], row["presented_blob"]
            )
        )
        with self.assertRaisesRegex(ValueError, "presented evidence binding"):
            with patch.object(Path, "read_bytes", return_value=b'{"status":"passed"}'):
                p.verify(ROOT, manifest)
        for field, replacement in (("files", []), ("source_revision", "f" * 40)):
            forged = deepcopy(manifest)
            forged[field] = replacement
            with self.assertRaisesRegex(ValueError, "untrusted path presentation"):
                p.verify(ROOT, forged)
        with self.assertRaisesRegex(ValueError, "location change"):
            p.present(b'{"status":"passed"}')

    def test_safe_paths_reject_traversal_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "repository"
            root.mkdir()
            (root / "escape").symlink_to(Path(scratch), target_is_directory=True)
            for name in ("../elsewhere", "/absolute", "a/../b", "escape/file.json"):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    p.safe_path(root, name)

    def test_export_uses_ignored_repository_output_without_recursion(self):
        from tests.models import test_grc_v4_step as step

        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / ".gitignore").write_text("/scratch/\n")
            (root / "src").mkdir()
            (root / "src/control.py").write_text("answer = 42\n")
            (root / "scratch").mkdir()
            (root / "scratch/old.zip").write_bytes(b"must not be exported")
            check_output = subprocess.check_output

            def fixture_command(command, **kwargs):
                if command == ["git", "rev-parse", "HEAD"]:
                    return "fixture-revision\n"
                return check_output(command, **kwargs)

            with (
                patch.object(
                    step, "__file__", str(root / "tests/models/test_grc_v4_step.py")
                ),
                patch.object(subprocess, "check_output", side_effect=fixture_command),
            ):
                with self.assertRaisesRegex(ValueError, "ignored storage"):
                    step.export_p933_audit(root / "bad.zip")
                self.assertFalse((root / "bad.zip").exists())
                output = root / "scratch/review.zip"
                step.export_p933_audit(output)
                before = output.read_bytes()
                with self.assertRaises(FileExistsError):
                    step.export_p933_audit(output)
                self.assertEqual(output.read_bytes(), before)
                with zipfile.ZipFile(output) as archive:
                    self.assertEqual(
                        set(archive.namelist()),
                        {"src/control.py", "BUNDLE-MANIFEST.json"},
                    )
                    manifest = json.loads(archive.read("BUNDLE-MANIFEST.json"))
                    self.assertEqual(
                        manifest["files"][0]["sha256"],
                        hashlib.sha256(archive.read("src/control.py")).hexdigest(),
                    )


if __name__ == "__main__":
    unittest.main()
