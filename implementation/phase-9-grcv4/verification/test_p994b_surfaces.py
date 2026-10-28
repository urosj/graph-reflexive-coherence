"""Public status stays bounded and never executes runtime integration."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import p994b_public_api as c

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
            v = tranche9.tranche9_public_status(ROOT)
            self.assertEqual(len(v["records"]), 7)
            self.assertEqual(len(v["contract_matrix"]), 10)
            self.assertEqual(v["contract_families"], list(c.CONTRACT_FAMILIES))
            self.assertTrue(v["user_accepted"])
            self.assertTrue(v["public_api"])
            raw, ref = tranche9.tranche9_public_source(
                ROOT, v["source_refs"][0]["path"]
            )
            self.assertEqual(c.sha(raw), ref["sha256"])
            with self.assertRaises(KeyError):
                tranche9.tranche9_public_source(ROOT, "../secret")
        original = c.read(ROOT, "C_OS")
        for kind in ("input", "promotion", "scope", "role"):
            v = json.loads(json.dumps(original))
            if kind == "input":
                v["source_refs"][0]["sha256"] = "0" * 64
            elif kind == "promotion":
                v["full_GRC9V4_conformance"] = True
            elif kind == "scope":
                v["family"] = "A_OS"
            else:
                v["evidence"]["branch_crossings"]["both_directions"] = False
            with patch.object(c, "read", return_value=c.seal(v)):
                with self.assertRaises(ValueError):
                    c.check(ROOT, "C_OS")

    def test_contract_scope_and_axes_reject_drift(self):
        original = c.read(ROOT, "contracts")
        for kind in ("missing", "carrier", "schema", "execution"):
            v = json.loads(json.dumps(original))
            rows = v["evidence"]["families"]
            if kind == "missing":
                rows.pop()
            elif kind == "carrier":
                rows[0]["authoritative_fields"].append("Z_4")
            elif kind == "schema":
                rows[0]["realization_parameter_schema"] = "ci_params"
            else:
                v["evidence"]["execution_scope"]["available"].append("A_OS")
            with patch.object(c, "read", return_value=c.seal(v)):
                with self.assertRaises(ValueError):
                    c.check(ROOT, "contracts")

    def test_architecture_evidence_and_runtime_successor_reject_drift(self):
        original = c.read(ROOT, "architecture")
        for case, key in (
            ("artifact_transfer", "dropped_prefix_rejected"),
            ("execution_selection", "registered_owner_does_not_enable"),
            ("accepted_replay", "checkpoint_bytes_equal"),
            ("accepted_crossing_replay", "checkpoint_bytes_equal"),
            ("branch_ownership", "sole_receipt_ledger"),
            ("branch_ownership", "no_nested_enabled_owner"),
        ):
            value = json.loads(json.dumps(original))
            value["evidence"][case][key] = False
            with patch.object(c, "read", return_value=c.seal(value)):
                with self.assertRaises(ValueError):
                    c.check(ROOT, "architecture")
        import p994b_runtime_successor as successor
        import p994b_source_compatibility as compatibility

        original_bytes = Path.read_bytes
        for name, row in successor.SOURCES.items():
            for expected in row["predecessors"]:
                self.assertEqual(
                    compatibility.execution_sha(ROOT, name, expected), expected
                )

                def changed(path):
                    raw = original_bytes(path)
                    return raw + b"# unrelated drift\n" if path == ROOT / name else raw

                with patch.object(Path, "read_bytes", changed):
                    self.assertNotEqual(
                        compatibility.execution_sha(ROOT, name, expected), expected
                    )

    def test_http_and_actual_wiring(self):
        spec = importlib.util.spec_from_file_location(
            "p994b_server", TOOL / "scripts/serve_phase9.py"
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

        code, raw, headers = get("/api/tranche9/public")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["iteration"], "P9-9.4b")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(get("/api/tranche9/public?family=A_OS")[0], 404)
        self.assertEqual(get("/api/tranche9/public/source?path=../secret")[0], 404)
        with patch.object(
            server, "tranche9_public_status", side_effect=ValueError("drift")
        ):
            code, raw, _ = get("/api/tranche9/public")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )
        self.assertIn(
            'id="tranche9-public-refresh"',
            (TOOL / "phase9-web/index.html").read_text(),
        )
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        self.assertTrue(
            any(
                "tranche9_public_status(repo_root)" in "".join(x.get("source", []))
                for x in notebook["cells"]
            )
        )

    def test_export_successor_is_exact(self):
        import p994b_source_compatibility as s
        import subprocess

        old = subprocess.check_output(
            ["git", "show", s.BASELINE + ":" + s.EXPORT], cwd=ROOT
        )
        digest = s.sha(old)
        self.assertEqual(s.execution_sha(ROOT, s.EXPORT, digest), digest)
        original = Path.read_bytes

        def changed(path):
            data = original(path)
            return data + b"# unrelated drift\n" if path == ROOT / s.EXPORT else data

        with patch.object(Path, "read_bytes", changed):
            self.assertNotEqual(s.execution_sha(ROOT, s.EXPORT, digest), digest)

    def test_tranche8_history_remains_retrievable_without_execution(self):
        import p984i_first_group as retained
        import p985_status
        import p986_acceptance
        from pygrc.models import grc_9_v4_lifecycle as events
        from pygrc.models import grc_9_v4_owner as enabled

        with (
            patch.object(
                events,
                "prepare_expansion",
                side_effect=AssertionError("metadata executed event"),
            ),
            patch.object(
                enabled,
                "prepare_enabled",
                side_effect=AssertionError("metadata executed enabled action"),
            ),
        ):
            for family in c.FAMILIES:
                value = p985_status._view(ROOT, family)
                self.assertEqual(value["status"], "accepted")
                self.assertFalse(value["current_code_conformance_inferred"])
                ref = next(
                    r
                    for r in value["source_refs"]
                    if r["path"] == "src/pygrc/models/grc_9_v4_lifecycle.py"
                )
                self.assertEqual(ref["basis"], "historical_git")
                self.assertEqual(c.sha(retained.authenticate(ROOT, ref)), ref["sha256"])
            value = p986_acceptance.status(ROOT, "first_group")
            self.assertEqual(value["status"], "accepted_bounded_first_group")
            self.assertFalse(value["aggregate_closed"])
            for ref in value["source_refs"]:
                if ref["path"] in (
                    "src/pygrc/models/grc_9_v4_lifecycle.py",
                    "implementation/phase-9-grcv4/verification/p985_status.py",
                ):
                    self.assertEqual(
                        c.sha(retained.authenticate(ROOT, ref)), ref["sha256"]
                    )


if __name__ == "__main__":
    unittest.main()
