"""Pressure release scope and publication without repeating scientific campaigns."""

from copy import deepcopy
import io
import json
import sys
import unittest
from unittest.mock import patch

import p9106_release as c


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = c.checked()

    def test_resealed_scope_widening_and_lost_residual_reject(self):
        mutations = [
            lambda v: v.update(G4_accepted=True),
            lambda v: v.update(full_GRC9V4_conformance=True),
            lambda v: v.update(Phase9_closed=True),
            lambda v: v["families"].pop(),
            lambda v: v["residuals"].update(hierarchy_obligation=None),
            lambda v: v["residuals"].update(inherited_D10_transformations_preserved=0),
            lambda v: v["support_sets"]["native_spark_completion"].update(scope="all profiles"),
            lambda v: v["source_refs"][0].update(sha256="0" * 64),
            lambda v: v["acceptance_chain"].update(native_debt_reconciliation="wrong.json"),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                bad = deepcopy(self.value)
                mutate(bad)
                with self.assertRaises(ValueError):
                    c.validate(c.seal(bad), self.value)

    def test_changed_accepted_source_rejects(self):
        with patch.object(c.subprocess, "check_output", return_value=b"wrong accepted bytes"):
            with self.assertRaisesRegex(ValueError, "accepted release source changed"):
                c.build()

    def test_http_browser_and_notebook_publish_checked_disposition(self):
        side = c.ROOT / (c.INV + "tools/exploratory-side-tool/tool")
        sys.path.insert(0, str(side / "src"))
        sys.path.insert(0, str(side / "scripts"))
        import serve_phase9 as server

        def request(url):
            handler = object.__new__(server.Handler)
            handler.path = url
            handler.wfile = io.BytesIO()
            status = []
            handler.send_response = status.append
            handler.send_header = lambda *args: None
            handler.end_headers = lambda: None
            handler.do_GET()
            return status[0], handler.wfile.getvalue()

        code, raw = request("/api/phase9/release")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw), self.value)
        self.assertEqual(request("/api/phase9/release?run=1")[0], 503)
        with patch.object(c, "checked", side_effect=ValueError("source drift")):
            code, raw = request("/api/phase9/release")
            self.assertEqual(code, 503)
            self.assertNotIn("source_refs", json.loads(raw))
        html = (side / "phase9-web/index.html").read_text()
        self.assertIn('href="/api/phase9/release"', html)
        self.assertIn("G4 is a separate pending decision", html)
        book = json.loads((side / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(row for row in book["cells"] if row.get("id") == "p9106-release")
        self.assertEqual(cell["outputs"], [])
        ns = dict(repo_root=c.ROOT, display=lambda value: None)
        exec("".join(cell["source"]), ns)
        self.assertEqual(ns["release_disposition"], self.value)
        with patch.object(c, "checked", side_effect=ValueError("source drift")):
            with self.assertRaises(ValueError):
                exec("".join(cell["source"]), ns)
        self.assertIsNone(ns["release_disposition"])


if __name__ == "__main__":
    unittest.main()
