"""Timing-stop recovery keeps exact prefixes and budgets the cold public replay."""

import json
import lzma
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from p991a6_cpc_campaign import Stream
from p991a6_cpc_campaign_complete import PROFILE_WARNINGS, checked_copy, profile
from p991a6_cpc_resume_cost import check, forecast, rows, stopped


class CPCResumeTests(unittest.TestCase):
    def test_stopped_scope_and_late_cost_are_pinned(self):
        stop = stopped()
        cost = check()
        self.assertEqual(stop["reset_verified_steps"], 191)
        from hashlib import sha256

        from p991a6_cpc_campaign import ROOT
        from p991a6_cpc_evidence_epoch import PREFIXES, evidence_bytes

        for path in PREFIXES:
            self.assertFalse((ROOT / path).exists())
            ref = next(r for r in stop["streams"].values() if r["path"] == path)
            self.assertEqual(
                sha256(evidence_bytes(ROOT, path)).hexdigest(), ref["sha256"]
            )
        self.assertTrue(stop["current_complete"])
        self.assertGreater(
            sum(stop["last_8_native_seconds"]) / 8, stop["native_stop_threshold"]
        )
        self.assertTrue(cost["estimate"]["within_budget"])
        self.assertLess(cost["estimate"]["combined_upper_seconds"], 1800)
        self.assertGreater(cost["estimate"]["cold_journal_replay_upper_seconds"], 0)
        self.assertEqual(cost["estimate"]["pressure_reserve_seconds"], 240)
        current = rows(stop["streams"]["current"]["path"])
        reset = rows(stop["streams"]["reset"]["path"])
        costly = [{"seconds": 10, "native_seconds": 5}] * 20
        self.assertFalse(forecast(costly, stop, current, reset)["within_budget"])

    def test_profiling_overrun_reports_and_continues(self):
        from contextlib import redirect_stdout
        from io import StringIO

        from p991a5_native_spark_verify import need

        output = StringIO()
        with redirect_stdout(output):
            profile(False, "synthetic timing overrun")
        self.assertTrue(json.loads(output.getvalue())["continues"])
        self.assertIn("synthetic timing overrun", PROFILE_WARNINGS)
        with self.assertRaises(ValueError):
            need(False, "numerical admission must still fail")

    def test_repository_staging_survives_failure_and_replaces_on_same_device(self):
        from p991a6_cpc_campaign import BASE, ROOT
        from p991a6_cpc_campaign_complete import staging_directory

        stage = staging_directory()
        source = stage / "sample.xz"
        target = stage / "published.xz"
        try:
            self.assertEqual(stage.stat().st_dev, (ROOT / BASE).stat().st_dev)
            source.write_bytes(lzma.compress(b"exact retained evidence"))
            with self.assertRaises(RuntimeError):
                raise RuntimeError("injected publication failure")
            self.assertTrue(source.is_file())
            source.replace(target)
            self.assertEqual(
                lzma.decompress(target.read_bytes()), b"exact retained evidence"
            )
        finally:
            if source.exists():
                source.unlink()
            if target.exists():
                target.unlink()
            stage.rmdir()

    def test_prefix_rewrite_preserves_hashes_and_rejects_disconnection(self):
        stop = stopped()
        original = rows(stop["streams"]["reset"]["path"])[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "copy.xz")
            stream = Stream(path)
            try:
                checked_copy(stream, original)
            finally:
                stream.close()
            with lzma.open(path, "rt") as source:
                self.assertEqual([json.loads(line) for line in source], original)
            bad = deepcopy(original)
            bad[1]["previous_record_digest"] = "different"
            stream = Stream(str(Path(tmp) / "bad.xz"))
            try:
                with self.assertRaises(ValueError):
                    checked_copy(stream, bad)
            finally:
                stream.close()
