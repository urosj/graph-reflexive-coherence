"""Bounded compatibility projection, source integrity and real HTTP dispatch."""

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
import p992_compatibility as checker  # noqa: E402


class Surfaces(unittest.TestCase):
    def test_matrix_and_source_without_native_execution(self):
        from pygrc.models.grc_9_v4_legacy import GRC9V4LegacyDelegate

        with patch.object(
            GRC9V4LegacyDelegate,
            "step",
            side_effect=AssertionError("status executed numerics"),
        ):
            v = tranche9.tranche9_compatibility_status(ROOT)
            self.assertEqual(len(v["cells"]), 40)
            self.assertEqual(
                sum(r["state"] == "bounded_accepted" for r in v["cells"]), 16
            )
            self.assertTrue(v["user_accepted"])
            self.assertFalse(v["crossings_executed"])
            raw, ref = tranche9.tranche9_compatibility_source(
                ROOT, v["source_refs"][0]["path"]
            )
            self.assertEqual(checker.sha(raw), ref["sha256"])
            with self.assertRaises(KeyError):
                tranche9.tranche9_compatibility_source(ROOT, "../secret")

    def test_bound_source_drift_and_status_promotion_reject(self):
        original = checker.read(ROOT, "C_OS")
        for kind in ("input", "promotion", "cell"):
            altered = json.loads(json.dumps(original))
            if kind == "input":
                altered["source_refs"][0]["sha256"] = "0" * 64
            elif kind == "promotion":
                altered["user_accepted"] = True
            else:
                altered["cells"]["state"]["contract_id"] = (
                    "D10.2-EC-DISABLED-A_OS-STATE"
                )
            altered = checker.seal(altered)
            with patch.object(checker, "read", return_value=altered):
                with self.assertRaises(ValueError):
                    checker.check(ROOT, "C_OS")

    def test_http_dispatch_and_fail_closed(self):
        spec = importlib.util.spec_from_file_location(
            "p992_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            handler = object.__new__(server.Handler)
            handler.path = path
            handler.wfile = io.BytesIO()
            codes = []
            headers = {}
            handler.send_response = codes.append
            handler.send_header = lambda k, v: headers.update({k: v})
            handler.end_headers = lambda: None
            handler.do_GET()
            return codes[-1], handler.wfile.getvalue(), headers

        code, raw, headers = get("/api/tranche9/compatibility")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["selected_cells"], 16)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(get("/api/tranche9/compatibility?family=A_OS")[0], 404)
        self.assertEqual(
            get("/api/tranche9/compatibility/source?path=../secret")[0], 404
        )
        with patch.object(
            server, "tranche9_compatibility_status", side_effect=ValueError("drift")
        ):
            code, raw, _ = get("/api/tranche9/compatibility")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )

    def test_browser_and_notebook_wired(self):
        self.assertIn(
            'id="tranche9-compatibility-refresh"',
            (TOOL / "phase9-web/index.html").read_text(),
        )
        v = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        self.assertTrue(
            any(
                "tranche9_compatibility_status(repo_root)"
                in "".join(c.get("source", []))
                for c in v["cells"]
            )
        )


if __name__ == "__main__":
    unittest.main()
