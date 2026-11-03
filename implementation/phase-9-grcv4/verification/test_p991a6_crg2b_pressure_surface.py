"""Bounded pressure publication, provenance, numerical replay and scope guards."""

import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
import p991a6_crg2b_pressure as pressure
from grcv4_explorer import spark_native_crg2b_pressure as view
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.errors import SourceAdmissionError


class CRG2bPressureSurfaceTests(unittest.TestCase):
    def test_numerical_replay_and_no_endpoint_scope(self):
        value = pressure.check(ROOT, numerical=True)
        self.assertEqual(value["tests_passed"], 15)
        self.assertEqual(
            value["measurements"]["exact_tube_boundary_witness_checks"], 84
        )
        self.assertFalse(value["runtime_changed"])
        self.assertFalse(value["native_endpoint_verified"])
        self.assertEqual(value["full_trajectory_runs"], 0)
        self.assertLess((ROOT / value["evidence"]["path"]).stat().st_size, 1024**2)
        self.assertEqual(view.native_crg2b_pressure(ROOT)["tests_passed"], 15)

    def test_rehashed_forgeries_reject(self):
        original = view.load_json_object
        for key, change in (
            ("native_endpoint_verified", True),
            ("full_trajectory_runs", 1),
            ("source_bindings", []),
            ("tests_passed", 16),
            ("measurements", {}),
        ):

            def altered(path, key=key, change=change):
                value = deepcopy(original(path))
                value[key] = change
                value["record_digest"] = record_digest(value, "record_digest")
                return value

            with (
                patch.object(view, "load_json_object", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                view.native_crg2b_pressure(ROOT)

    def test_changed_pressure_code_or_operand_evidence_rejects(self):
        original = Path.open
        for name in (
            pressure.HERE + "crg2b_native_spark_pressure_oracle.py",
            pressure.EVIDENCE,
        ):
            bad = (ROOT / name).read_bytes() + b"changed"

            def altered(path, *args, name=name, bad=bad, **kwargs):
                return (
                    BytesIO(bad)
                    if path == ROOT / name
                    else original(path, *args, **kwargs)
                )

            with (
                patch.object(Path, "open", altered),
                self.assertRaises(SourceAdmissionError),
            ):
                view.native_crg2b_pressure(ROOT)

    def test_http_routes_and_combined_view_fail_closed(self):
        from grcv4_explorer.spark_native_crg2b import native_crg2b

        spec = importlib.util.spec_from_file_location(
            "crg2b_pressure_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.command = "GET"
        handler.send_response = lambda code, message=None: codes.append(code)
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        for route in (
            "/api/native-spark/c-rg2b/pressure",
            "/api/native-spark/c-rg2b/pressure/source",
        ):
            handler.path = route
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 200)
            expected = (
                (ROOT / pressure.RECORD).read_bytes()
                if route.endswith("/source")
                else json.dumps(view.native_crg2b_pressure(ROOT)).encode()
            )
            self.assertEqual(json.loads(handler.wfile.getvalue()), json.loads(expected))
        handler.path = "/api/native-spark/c-rg2b/pressure?campaign=true"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 503)
        self.assertEqual(
            native_crg2b(ROOT)["pressure"], view.native_crg2b_pressure(ROOT)
        )
        with (
            patch.object(
                view,
                "checked_record",
                side_effect=SourceAdmissionError("stale pressure"),
            ),
            self.assertRaises(SourceAdmissionError),
        ):
            native_crg2b(ROOT)


if __name__ == "__main__":
    unittest.main()
