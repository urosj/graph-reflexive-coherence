"""Crossing status stays bounded and never runs numerical kernels."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p994a_crossings as c

ROOT = Path(__file__).resolve().parents[3]
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import tranche9  # noqa:E402


class Surfaces(unittest.TestCase):
    def test_integrity_and_rejection(self):
        from pygrc.models.grc_9_v4_crossing import GRC9V4BranchOperation

        with patch.object(
            GRC9V4BranchOperation,
            "migrate",
            side_effect=AssertionError("status executed migration"),
        ):
            v = tranche9.tranche9_crossing_status(ROOT)
            self.assertEqual(len(v["records"]), 4)
            self.assertTrue(v["user_accepted"])
            self.assertFalse(v["public_api"])
            raw, ref = tranche9.tranche9_crossing_source(
                ROOT, v["source_refs"][0]["path"]
            )
            self.assertEqual(c.sha(raw), ref["sha256"])
            with self.assertRaises(KeyError):
                tranche9.tranche9_crossing_source(ROOT, "../secret")
        original = c.read(ROOT, "C_OS")
        for kind in ("input", "promotion", "scope", "role"):
            v = json.loads(json.dumps(original))
            if kind == "input":
                v["source_refs"][0]["sha256"] = "0" * 64
            elif kind == "promotion":
                v["public_api"] = True
            elif kind == "scope":
                v["family"] = "A_OS"
            else:
                v["evidence"]["roundtrip"]["current_reset_independently_admitted"] = (
                    False
                )
            with patch.object(c, "read", return_value=c.seal(v)):
                with self.assertRaises(ValueError):
                    c.check(ROOT, "C_OS")

    def test_http_and_actual_wiring(self):
        spec = importlib.util.spec_from_file_location(
            "p994a_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            h = object.__new__(server.Handler)
            h.path = path
            h.wfile = io.BytesIO()
            codes = []
            headers = {}
            h.send_response = codes.append
            h.send_header = lambda k, v: headers.update({k: v})
            h.end_headers = lambda: None
            h.do_GET()
            return codes[-1], h.wfile.getvalue(), headers

        code, raw, headers = get("/api/tranche9/crossings")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["iteration"], "P9-9.4a")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(get("/api/tranche9/crossings?family=A_OS")[0], 404)
        self.assertEqual(get("/api/tranche9/crossings/source?path=../secret")[0], 404)
        with patch.object(
            server, "tranche9_crossing_status", side_effect=ValueError("drift")
        ):
            code, raw, _ = get("/api/tranche9/crossings")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )
        self.assertIn(
            'id="tranche9-crossings-refresh"',
            (TOOL / "phase9-web/index.html").read_text(),
        )
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        self.assertTrue(
            any(
                "tranche9_crossing_status(repo_root)" in "".join(x.get("source", []))
                for x in notebook["cells"]
            )
        )

    def test_owner_successor_is_narrow(self):
        import p994a_owner_successor as s

        self.assertEqual(s.check(ROOT, "C_OS")["family"], "C_OS")
        original = Path.read_bytes

        def altered(path):
            raw = original(path)
            return (
                raw + b"\n# drift\n"
                if path == ROOT / "src/pygrc/models/grc_9_v4_owner.py"
                else raw
            )

        with patch.object(Path, "read_bytes", altered):
            with self.assertRaises(ValueError):
                s.check(ROOT, "C_OS")


if __name__ == "__main__":
    unittest.main()
