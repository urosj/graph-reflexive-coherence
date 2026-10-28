"""Pressure exact support identity, prerequisite acceptance and honest exclusions."""

from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import p996_support_review as c
import p996_acceptance as acceptance

ROOT = c.ROOT
TOOL = ROOT / c.SIDE / "tool"
sys.path.insert(0, str(TOOL / "src"))


class SupportReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pygrc.models import GRC9V4
        from pygrc.models.grc_9_v3 import GRC9V3

        with (
            patch.object(
                GRC9V4,
                "from_config",
                side_effect=AssertionError("review constructs runtime"),
            ),
            patch.object(
                GRC9V4, "step", side_effect=AssertionError("review executes V4")
            ),
            patch.object(
                GRC9V3, "step", side_effect=AssertionError("review executes V3")
            ),
        ):
            cls.data = c.inputs(ROOT)
            cls.value = c.assemble(ROOT, cls.data)

    def test_current_reconciliation_and_exact_scope(self):
        self.assertEqual(c.read(ROOT, c.PATH), self.value)
        self.assertEqual(self.value["inherited_test_methods"], 105)
        self.assertEqual(self.value["new_native_steps"], 0)
        self.assertFalse(self.value["native_execution"])
        for row in self.value["rows"]:
            self.assertNotEqual(
                row["source"]["complete_profile_id"],
                row["enabled_expansion_target"]["complete_profile_id"],
            )
            self.assertEqual(
                row["missing_mandatory_capabilities"], ["basin_attributes"]
            )
            self.assertEqual(
                {r["model_identity"] for r in row["disabled_cells"]},
                {row["source"]["model_identity"]},
            )
        self.assertEqual(
            {r["support_disposition"] for r in self.value["authority"]},
            {"indeterminate_requires_review"},
        )

    def test_prerequisite_and_identity_pressure(self):
        for kind in (
            "unaccepted",
            "stage",
            "family",
            "cell_identity",
            "public_identity",
            "optional",
            "completion",
            "widen_matrix",
        ):
            with self.subTest(kind=kind):
                data = deepcopy(self.data)
                if kind == "unaccepted":
                    data["accepted"]["9.5"]["user_accepted"] = False
                elif kind == "stage":
                    del data["accepted"]["9.4a"]
                elif kind == "family":
                    del data["records"]["9.5"]["C_CI"]
                elif kind == "cell_identity":
                    row = next(
                        r for r in data["matrix"]["cells"] if r["family"] == "C_OS"
                    )
                    row["model_identity"] = data["records"]["9.1b"]["C_OS"]["evidence"][
                        "mixed_snapshot"
                    ]["state"]["model_identity"]
                elif kind == "public_identity":
                    data["records"]["9.4b"]["C_OS"]["evidence"]["construction"][
                        "active_model_identity"
                    ] = "grc9v4-model-sha256:" + "0" * 64
                elif kind == "optional":
                    data["records"]["9.4b"]["A_CI"]["evidence"]["construction"][
                        "capabilities"
                    ].append("completed_spark")
                elif kind == "completion":
                    state = data["records"]["9.1b"]["C_OS"]["evidence"][
                        "mixed_snapshot"
                    ]["initial"]
                    state["specialization"]["resolved"]["spark"][
                        "child_stabilization"
                    ] = {}
                else:
                    data["matrix"]["counts"]["bounded_accepted"] = 40
                with self.assertRaises((ValueError, TypeError)):
                    c.assemble(ROOT, data)

    def test_resealed_claim_and_hold_mutations_reject(self):
        for kind in (
            "full",
            "accepted",
            "new_support",
            "drop_hold",
            "target_scope",
            "basin",
            "optional",
            "numerics",
        ):
            with self.subTest(kind=kind):
                value = deepcopy(self.value)
                if kind == "full":
                    value["full_GRC9V4_conformance"] = True
                elif kind == "accepted":
                    value["user_accepted"] = True
                elif kind == "new_support":
                    value["new_G2_G3_support"] = ["A_OS"]
                elif kind == "drop_hold":
                    value["open_items"].pop(0)
                elif kind == "target_scope":
                    value["rows"][0]["expanded_target_disabled_surfaces"] = "accepted"
                elif kind == "basin":
                    value["rows"][0]["missing_mandatory_capabilities"] = []
                elif kind == "optional":
                    value["optional_completion"]["executed"] = True
                else:
                    value["native_execution"] = True
                with patch.object(c, "build", return_value=self.value):
                    with self.assertRaises(ValueError):
                        c.check(ROOT, c.seal(value))

    def test_current_runtime_drift_rejects(self):
        original = Path.read_bytes
        target = ROOT / "src/pygrc/models/grc_9_v4.py"

        def drift(path):
            raw = original(path)
            return raw + b"# unrelated runtime change\n" if path == target else raw

        with patch.object(Path, "read_bytes", drift):
            with self.assertRaises(ValueError):
                c4 = c.c4b
                c4.check(ROOT, "C_OS")

    def test_acceptance_preserves_original_review_and_rejects_widening(self):
        accepted = acceptance.decision(ROOT)
        self.assertTrue(accepted["user_accepted"])
        self.assertFalse(self.value["user_accepted"])
        self.assertFalse(accepted["full_GRC9V4_conformance"])
        original = Path.read_bytes
        for kind in ("acceptance", "conformance", "holds", "subject"):
            value = deepcopy(accepted)
            if kind == "acceptance":
                value["user_accepted"] = False
            elif kind == "conformance":
                value["full_GRC9V4_conformance"] = True
            elif kind == "holds":
                value["remaining_holds"].pop()
            else:
                value["evidence"]["record_digest"] = "0" * 64
            raw = json.dumps(c.seal(value)).encode()

            def altered(path):
                return raw if path == ROOT / acceptance.PATH else original(path)

            with self.subTest(kind=kind), patch.object(Path, "read_bytes", altered):
                with self.assertRaises(ValueError):
                    acceptance.decision(ROOT)

    def test_actual_http_sources_and_notebook_wiring(self):
        # The class fixture has authenticated the full chain once; exercise HTTP
        # and projection without redundantly re-reading the same large checkpoints.
        spec = importlib.util.spec_from_file_location(
            "p996_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            h = object.__new__(server.Handler)
            h.path, h.wfile = path, io.BytesIO()
            codes = []
            h.send_response = codes.append
            h.send_header = lambda *args: None
            h.end_headers = lambda: None
            h.do_GET()
            return codes[-1], h.wfile.getvalue()

        with patch.object(c, "build", return_value=self.value):
            code, raw = get("/api/tranche9/support")
            self.assertEqual(code, 200)
            v = json.loads(raw)
            self.assertFalse(v["full_GRC9V4_conformance"])
            self.assertTrue(v["user_accepted"])
            self.assertEqual(v["acceptance_digest"], acceptance.DIGEST)
            self.assertEqual(len(v["open_items"]), 3)
            for ref in v["source_refs"]:
                code, raw = get("/api/tranche9/support/source?path=" + ref["path"])
                self.assertEqual(code, 200)
                self.assertEqual(c.sha(raw), ref["sha256"])
            self.assertEqual(get("/api/tranche9/support?family=A_OS")[0], 404)
            self.assertEqual(get("/api/tranche9/support/source?path=../secret")[0], 404)
        with patch.object(
            server, "tranche9_support_status", side_effect=ValueError("drift")
        ):
            code, raw = get("/api/tranche9/support")
            self.assertEqual(code, 503)
            self.assertEqual(
                json.loads(raw)["evidence_state"], "unavailable_not_admitted"
            )
        self.assertIn(
            'id="tranche9-support-refresh"',
            (TOOL / "phase9-web/index.html").read_text(),
        )
        notebook = json.loads(
            (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
        )
        self.assertTrue(
            any(
                "tranche9_support_status(repo_root)" in "".join(x.get("source", []))
                for x in notebook["cells"]
            )
        )


if __name__ == "__main__":
    unittest.main()
