"""Read-only lifecycle evidence and actual API/browser route pressure."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import tranche9  # noqa: E402


class Surfaces(unittest.TestCase):
    def test_checked_results_and_indexed_sources_without_numerics(self):
        from pygrc.models.grc_9_v4_owner import GRC9V4EnabledOperation

        with patch.object(
            GRC9V4EnabledOperation,
            "__init__",
            side_effect=AssertionError("status must not run kernels"),
        ):
            value = tranche9.tranche9_status(ROOT)
            self.assertEqual(value["families"], ["C_OS", "C_CI", "A_CI", "A_PC"])
            self.assertTrue(value["user_accepted"])
            self.assertFalse(value["full_GRC9V4_conformance"])
            self.assertEqual(sum(r["tests"] for r in value["records"]), 24)
            raw, ref = tranche9.tranche9_source(ROOT, value["source_refs"][0]["path"])
            self.assertEqual(tranche9.hashlib.sha256(raw).hexdigest(), ref["sha256"])
            for path in (
                "../outside",
                "src/pygrc/models/grc_9_v4_owner.py",
                "/absolute/path",
            ):
                with self.assertRaises(KeyError):
                    tranche9.tranche9_source(ROOT, path)

    def test_actual_http_dispatch_rejects_widening_and_missing_results(self):
        spec = importlib.util.spec_from_file_location(
            "p991b_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            handler = object.__new__(server.Handler)
            handler.path, handler.wfile = path, io.BytesIO()
            statuses, headers = [], {}
            handler.send_response = statuses.append
            handler.send_header = lambda k, v: headers.update({k: v})
            handler.end_headers = lambda: None
            handler.do_GET()
            return statuses[-1], handler.wfile.getvalue(), headers

        code, raw, headers = get("/api/tranche9")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["iteration"], "P9-9.1b")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(get("/api/tranche9?family=A_OS")[0], 404)
        self.assertEqual(get("/api/tranche9/source?path=../secret")[0], 404)
        with patch.object(
            server, "tranche9_status", side_effect=ValueError("source drift")
        ):
            code, raw, _ = get("/api/tranche9")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )

    def test_browser_and_notebook_are_wired(self):
        html = (TOOL / "phase9-web/index.html").read_text()
        self.assertIn('id="tranche9-refresh"', html)
        self.assertIn('src="/tranche9.js"', html)
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        self.assertTrue(
            any(
                "tranche9_status(repo_root)" in "".join(c.get("source", []))
                for c in notebook["cells"]
            )
        )


if __name__ == "__main__":
    unittest.main()
