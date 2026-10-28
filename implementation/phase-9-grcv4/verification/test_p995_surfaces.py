"""Retained conflict evidence must not execute runtime or imply acceptance."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import p995_public_conflict as c

ROOT = Path(__file__).resolve().parents[3]
SIDE = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
)
TOOL = SIDE / "tool"
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import tranche9  # noqa: E402


class Surfaces(unittest.TestCase):
    def test_integrity_source_access_and_no_runtime(self):
        from pygrc.models import GRC9V4

        with patch.object(
            GRC9V4, "step", side_effect=AssertionError("status ran native step")
        ):
            v = tranche9.tranche9_conflict_status(ROOT)
            self.assertEqual([r["family"] for r in v["records"]], list(c.FAMILIES))
            self.assertTrue(v["user_accepted"])
            from p995_acceptance import DIGEST

            self.assertEqual(v["acceptance_digest"], DIGEST)
            self.assertFalse(c.read(ROOT, "C_OS")["user_accepted"])
            self.assertFalse(v["full_GRC9V4_conformance"])
            for ref in v["source_refs"]:
                raw, bound = tranche9.tranche9_conflict_source(ROOT, ref["path"])
                self.assertEqual(c.sha(raw), bound["sha256"])
            with self.assertRaises(KeyError):
                tranche9.tranche9_conflict_source(ROOT, "../secret")

    def test_missing_altered_and_promoted_results_reject(self):
        original = c.read(ROOT, "C_OS")
        for kind in (
            "source",
            "missing_source",
            "scope",
            "acceptance",
            "conformance",
            "failure",
            "reset",
            "rollback",
            "boundary",
            "missing_boundary",
            "repeat",
        ):
            with self.subTest(kind=kind):
                v = json.loads(json.dumps(original))
                e = v["evidence"]
                if kind == "source":
                    v["source_refs"][0]["sha256"] = "0" * 64
                elif kind == "missing_source":
                    v["source_refs"] = [
                        r
                        for r in v["source_refs"]
                        if not r["path"].endswith("grc_9_v4_legacy.py")
                    ]
                elif kind == "scope":
                    v["family"] = "A_OS"
                elif kind == "acceptance":
                    v["user_accepted"] = True
                elif kind == "conformance":
                    v["full_GRC9V4_conformance"] = True
                elif kind == "failure":
                    e["rejection"]["failure"]["code"] = "target_readmission_failure"
                elif kind == "reset":
                    e["replay_reset"]["reset_native_parity"] = False
                elif kind == "rollback":
                    e["rejection"]["after_snapshot_sha256"] = "0" * 64
                elif kind == "boundary":
                    e["boundaries"][1]["candidate_count"] = 1
                elif kind == "missing_boundary":
                    e["boundaries"].pop()
                else:
                    e["rejection"]["rejected_public_calls"] = 1
                with patch.object(c, "read", return_value=c.seal(v)):
                    with self.assertRaises(ValueError):
                        c.check(ROOT, "C_OS")

    def test_forensic_contract_preserves_bounded_authority(self):
        from grcv4_explorer.a_initializer import load_current_forensic_context
        from grcv4_explorer.forensic import contract_provenance

        context = load_current_forensic_context(ROOT, SIDE)
        actual = contract_provenance(context, "D11-G9-EC-LEGACY-DEFINED-DOMAIN")
        self.assertEqual(actual, json.loads((ROOT / c.AUTHORITY).read_bytes()))
        self.assertEqual(
            actual["rows"][0]["payload"]["support_disposition"],
            [
                "accepted_bounded_GRC9V4_compatibility_boundary_not_a_GRC9_or_GRC9V3_rewrite"
            ],
        )

    def test_http_and_real_browser_notebook_wiring(self):
        spec = importlib.util.spec_from_file_location(
            "p995_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            h = object.__new__(server.Handler)
            h.path, h.wfile = path, io.BytesIO()
            codes, headers = [], {}
            h.send_response = codes.append
            h.send_header = lambda k, v: headers.update({k: v})
            h.end_headers = lambda: None
            h.do_GET()
            return codes[-1], h.wfile.getvalue(), headers

        code, raw, headers = get("/api/tranche9/conflict")
        self.assertEqual(code, 200)
        v = json.loads(raw)
        self.assertEqual(v["iteration"], "P9-9.5")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(get("/api/tranche9/conflict?family=A_OS")[0], 404)
        self.assertEqual(get("/api/tranche9/conflict/source?path=../secret")[0], 404)
        ref = v["source_refs"][0]
        code, raw, headers = get("/api/tranche9/conflict/source?path=" + ref["path"])
        self.assertEqual(code, 200)
        self.assertEqual(c.sha(raw), headers["X-Evidence-SHA256"])
        with patch.object(
            server, "tranche9_conflict_status", side_effect=ValueError("drift")
        ):
            code, raw, _ = get("/api/tranche9/conflict")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )
        self.assertIn(
            'id="tranche9-conflict-refresh"',
            (TOOL / "phase9-web/index.html").read_text(),
        )
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        self.assertTrue(
            any(
                "tranche9_conflict_status(repo_root)" in "".join(x.get("source", []))
                for x in notebook["cells"]
            )
        )


if __name__ == "__main__":
    unittest.main()
