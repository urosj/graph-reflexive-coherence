"""Discovery, comparison and portable selection pressure; no numerical execution."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "configuration_catalog", ROOT / "examples/grcv4/catalog.py"
)
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)


class RetainedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = cli.Catalog()

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.main(list(args))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_all_ten_native_pairs_and_twenty_two_generic_runs(self):
        rows = self.catalog.rows()
        self.assertEqual(len(rows), 42)
        self.assertFalse([r for r in rows if r["status"] == "stale"])
        for family in cli.FAMILIES:
            for size, counts in [
                ("small", ((10, 9), (17, 16))),
                ("large", ((100, 400), (107, 407))),
            ]:
                item = self.catalog.inspect(f"native-{size}-{family}")
                for side, (n, m) in zip(("source", "target"), counts, strict=True):
                    g = item["configurations"][side]["graph_summary"]
                    self.assertEqual(
                        (g["vertices"], g["edges"], g["components"]), (n, m, 1)
                    )
                    self.assertLessEqual(g["maximum_degree"], 9)
                if size == "large":
                    expected = (
                        "rejected"
                        if family.endswith("RG2b")
                        else "certificate-passed"
                        if family in {"A_CI", "A_CI_PC", "A_PC", "C_PC"}
                        else "incomplete"
                    )
                    self.assertEqual(item["status"], expected)
                    self.assertEqual(item["acceptance"], "not_accepted")
        self.assertEqual(sum(r["model"] == "GRCV4" for r in rows), 22)

    def test_every_side_selects_and_verifies_with_original_graph_and_profile(self):
        for name in self.catalog.entries:
            record = self.catalog.inspect(name)
            for side, config in record["configurations"].items():
                with self.subTest(name=name, side=side):
                    selected = self.catalog.selection(name, side)
                    self.assertEqual(selected["configuration"], config)
                    restored = cli.json_read(json.dumps(selected))
                    self.assertEqual(
                        self.catalog.verify_selection(restored)["status"], "unchanged"
                    )
                    self.assertFalse(Path(restored["catalog"]).is_absolute())

    def test_decoded_bounds_and_actual_differences(self):
        small = self.catalog.inspect("native-small-A_PC")
        large = self.catalog.inspect("native-large-A_PC")
        self.assertEqual(
            small["configurations"]["source"]["parameters"]["resource_radius"], 16
        )
        self.assertEqual(
            large["configurations"]["source"]["parameters"]["resource_radius"], 32
        )
        result = cli.compare([small, large], "source")
        fields = {d["field"] for d in result["differences"]}
        self.assertTrue(
            {
                "graph.vertices",
                "graph.edges",
                "parameters.geometry.kappa_H",
                "parameters.realization.radius",
                "decoded_bounds.resource_radius",
                "graph_content",
                "history_content",
                "acceptance",
            }
            <= fields
        )
        self.assertNotIn("ordinary_dt", fields)

    def test_comparison_preserves_numeric_boolean_absent_and_history_distinctions(self):
        a = self.catalog.inspect("native-small-A_OS")
        b = deepcopy(a)
        b["id"] = "changed"
        params = b["configurations"]["source"]["profile"]["params_resolved"][
            "candidate"
        ]
        a["configurations"]["source"]["profile"]["params_resolved"]["candidate"][
            "probe"
        ] = 1
        params["probe"] = 1.0
        self.assertEqual(cli.compare([a, b], "source")["differences"], [])
        params["probe"] = True
        self.assertEqual(
            cli.compare([a, b], "source")["differences"][0]["field"],
            "parameters.candidate.probe",
        )
        params["probe"] = None
        del a["configurations"]["source"]["profile"]["params_resolved"]["candidate"][
            "probe"
        ]
        diff = cli.compare([a, b], "source")["differences"][0]
        self.assertFalse(diff["values"][a["id"]]["present"])
        self.assertTrue(diff["values"][b["id"]]["present"])
        b["configurations"]["source"]["roles"]["current"]["probe"] = 0
        self.assertIn(
            "history_content",
            {d["field"] for d in cli.compare([a, b], "source")["differences"]},
        )

    def test_filters_and_json_export(self):
        code, out, err = self.invoke(
            "list",
            "--family",
            "A_CI+PC",
            "--min-vertices",
            "50",
            "--status",
            "certificate-passed",
            "--json",
        )
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([r["id"] for r in json.loads(out)], ["native-large-A_CI_PC"])
        code, out, _ = self.invoke("list", "--side", "target", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)), 20)
        code, out, _ = self.invoke(
            "list",
            "--model",
            "GRCV4",
            "--scenario",
            "generic-grid",
            "--max-vertices",
            "12",
            "--max-edges",
            "17",
            "--json",
        )
        self.assertEqual(len(json.loads(out)), 5)
        code, out, _ = self.invoke(
            "list", "--family", "a_pc", "--kappa-h", "0.075", "--json"
        )
        self.assertEqual([r["id"] for r in json.loads(out)], ["generic-branch-A_PC"])
        _, out, _ = self.invoke("list", "--min-vertices", "1000", "--json")
        self.assertEqual(json.loads(out), [])

    def test_readable_output_and_failure_messages(self):
        code, out, _ = self.invoke("show", "native-large-A_CI_PC")
        self.assertEqual(code, 0)
        self.assertIn("resource_radius: 32.0", out)
        self.assertIn("geometry_radius: 0.0009765625", out)
        self.assertIn("not_accepted", out)
        self.assertNotIn("0x1.", out)
        _, out, _ = self.invoke("compare", "native-small-A_PC", "native-large-A_PC")
        self.assertLess(max(map(len, out.splitlines())), 150)
        for args in [
            ("list", "--min-vertices", "12", "--max-vertices", "3"),
            ("list", "--kappa-h", "nan"),
            ("list", "--min-edges", "-1"),
            ("show", "generic-branch-A_OS", "--side", "target"),
            ("compare", "native-small-A_OS", "native-small-A_OS"),
        ]:
            with self.subTest(args=args):
                code, _, err = self.invoke(*args)
                self.assertEqual(code, 2)
                self.assertNotIn("Traceback", err)
        _, _, err = self.invoke("show", "native-small-A_O")
        self.assertIn("native-small-A_OS", err)

    def test_selection_cli_roundtrip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "selected.json"
            self.assertEqual(
                self.invoke(
                    "select",
                    "native-large-A_PC",
                    "--side",
                    "target",
                    "--output",
                    str(path),
                )[0],
                0,
            )
            before = path.read_bytes()
            code, out, _ = self.invoke("verify-selection", str(path), "--json")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["side"], "target")
            self.assertEqual(
                self.invoke("select", "native-small-A_PC", "--output", str(path))[0], 2
            )
            self.assertEqual(path.read_bytes(), before)

    def test_fresh_isolated_interpreter_has_no_numerical_imports(self):
        script = f"import runpy,sys; sys.argv=['catalog.py','list','--min-vertices','1000']; runpy.run_path({str(ROOT / 'examples/grcv4/catalog.py')!r},run_name='__main__')"
        # Catch main's intentional exit, then examine the fresh interpreter.
        script = (
            "import sys\ntry:\n "
            + script
            + "\nexcept SystemExit as e:\n assert e.code == 0\nassert not any(n.split('.')[0] in {'pygrc','numpy','scipy','tests','flint'} for n in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", script],
            capture_output=True,
            text=True,
            cwd=ROOT.parent,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_small_c_retention_is_bound_and_matches_existing_rg_evidence(self):
        data = json.loads(
            (
                ROOT
                / "implementation/phase-9-grcv4/tranche-8/P9-8.3-CatalogSmallCInputs.json"
            ).read_text()
        )
        for binding in data["source_bindings"]:
            self.catalog.artifact(binding)
        evidence = json.loads(
            (
                ROOT
                / "implementation/phase-9-grcv4/tranche-8/P9-8.3C-RG2b-Validation.json"
            ).read_text()
        )["numerical_observations"]
        record = self.catalog.inspect("native-small-C_RG2b")
        for side in ("source", "target"):
            self.assertEqual(
                record["configurations"][side]["profile"]["complete_profile_id"],
                evidence[side + "_profile"],
            )

    def test_probe_scope_and_missing_histories_cannot_look_successful(self):
        c = cli.Catalog()
        name = "native-large-A_PC"
        ref = c.entry(name)["admission"]
        report = c.artifact(ref, parse=True)
        original = c.artifact
        for change in (
            "family",
            "prepared_digest",
            "physical_steps",
            "missing_role",
            "unknown_status",
        ):
            altered = deepcopy(report)
            if change == "missing_role":
                del altered["source"]["reset"]
            elif change == "unknown_status":
                altered["target"]["current"]["status"] = "accepted"
            else:
                altered[change] = 1 if change == "physical_steps" else "wrong"

            def artifact(reference, *, parse=False, result=altered):
                if reference == ref and parse:
                    return result
                return original(reference, parse=parse)

            with (
                self.subTest(change=change),
                patch.object(c, "artifact", side_effect=artifact),
                self.assertRaises(cli.CatalogError),
            ):
                c.selection(name, "source")

    def test_saved_selection_uses_its_own_catalog_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_catalog = cli.Catalog
            catalog = real_catalog()
            # Only one entry is needed; retain its exact data and evidence paths.
            item = catalog.entry("generic-grid-3x4-C_OS")
            (root / "inventory.json").write_text(
                json.dumps(
                    {"schema": "grc-configuration-catalog-v1", "entries": [item]}
                )
            )
            for ref in [item["data"], *item["evidence"]]:
                dest = root / ref["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / ref["path"], dest)
            selection = real_catalog("inventory.json", root).selection(
                item["id"], "source"
            )
            saved = root / "selection.json"
            saved.write_text(json.dumps(selection))
            with patch.object(
                cli, "Catalog", side_effect=lambda path: real_catalog(path, root)
            ):
                code, out, _ = self.invoke("verify-selection", str(saved), "--json")
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(out)["status"], "unchanged")


class CatalogMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.item = deepcopy(cli.Catalog().entry("generic-grid-3x4-C_OS"))
        self.name = self.item["id"]
        for ref in [self.item["data"], *self.item["evidence"]]:
            dest = self.root / ref["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / ref["path"], dest)
        self.path = "inventory.json"
        self.write_catalog()

    def write_catalog(self, extra=()):
        (self.root / self.path).write_text(
            json.dumps(
                {
                    "schema": "grc-configuration-catalog-v1",
                    "entries": [self.item, *extra],
                }
            )
        )
        return cli.Catalog(self.path, self.root)

    def test_changed_data_or_evidence_remains_visible_and_blocks_selection(self):
        for ref in [self.item["data"], *self.item["evidence"]]:
            with self.subTest(path=ref["path"]):
                path = self.root / ref["path"]
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                c = cli.Catalog(self.path, self.root)
                rows = c.rows()
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["status"], "stale")
                self.assertIn("artifact changed", rows[0]["error"])
                with self.assertRaises(cli.CatalogError):
                    c.selection(self.name, "source")
                path.write_bytes(original)

    def test_missing_file_remains_visible(self):
        (self.root / self.item["data"]["path"]).unlink()
        self.assertEqual(cli.Catalog(self.path, self.root).rows()[0]["status"], "stale")

    def test_rehashed_selection_tampering_never_changes_authority(self):
        c = cli.Catalog(self.path, self.root)
        saved = c.selection(self.name, "source")
        for field in ("parameters", "evidence", "side", "purpose"):
            changed = deepcopy(saved)
            if field == "parameters":
                changed["configuration"]["profile"]["params_resolved"]["geometry"][
                    "kappa_H"
                ] = 1
            elif field == "evidence":
                changed["recorded_evidence"]["status"] = "bounded-runtime"
            else:
                changed[field] = "target" if field == "side" else "runtime_accepted"
            changed.pop("selection_digest")
            changed["selection_digest"] = cli.digest(changed)
            with self.subTest(field=field), self.assertRaises(cli.CatalogError):
                c.verify_selection(changed)

    def test_new_inventory_entry_does_not_invalidate_existing_choice(self):
        c = cli.Catalog(self.path, self.root)
        saved = c.selection(self.name, "source")
        new = deepcopy(self.item)
        new["id"] = "another-experiment"
        updated = self.write_catalog([new])
        self.assertEqual(updated.verify_selection(saved)["status"], "unchanged")
        self.assertEqual(
            updated.selection(new["id"], "source")["configuration"],
            saved["configuration"],
        )
        self.item["notes"].append("Evidence scope reviewed again")
        changed = self.write_catalog([new])
        with self.assertRaises(cli.CatalogError):
            changed.verify_selection(saved)

    def test_invalid_catalog_and_relative_path_escape(self):
        with self.assertRaisesRegex(cli.CatalogError, "duplicate configuration"):
            self.write_catalog([self.item])
        self.write_catalog()
        for path in ("../outside.json", "/absolute.json"):
            with self.subTest(path=path), self.assertRaises(cli.CatalogError):
                cli.Catalog(path, self.root)
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "escape").symlink_to(outside, target_is_directory=True)
            self.item["data"]["path"] = "escape/data.json"
            self.assertEqual(self.write_catalog().rows()[0]["status"], "stale")

    def test_family_adapter_and_schema_mismatch(self):
        original = deepcopy(self.item)
        for key, value in [
            ("format", "unrecognized"),
            ("model", "GRC9V4"),
            ("family", "Z_OS"),
        ]:
            self.item = deepcopy(original)
            self.item[key] = value
            with self.subTest(key=key), self.assertRaises(cli.CatalogError):
                self.write_catalog()
        self.item = original
        self.item["family"] = "A_OS"
        self.assertEqual(self.write_catalog().rows()[0]["status"], "stale")

    def test_strict_json_and_pointer(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', "[Infinity]", "[1e999]"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                cli.json_read(raw)
        self.assertEqual(cli.pointer({"a/b": {"~": [17]}}, "/a~1b/~0/0"), 17)

    def test_graph_counts_include_components_loops_and_typed_node_ids(self):
        graph = {
            "live_node_ids": [1, "1", 2],
            "oriented_edges": [
                {"tail_node_id": 1.0, "head_node_id": "1"},
                {"tail_node_id": 1, "head_node_id": 1},
            ],
        }
        self.assertEqual(
            cli.graph_summary(graph),
            {
                "vertices": 3,
                "edges": 2,
                "components": 2,
                "cycle_rank": 1,
                "maximum_degree": 3,
            },
        )
        graph["live_node_ids"].append(1.0)
        with self.assertRaises(cli.CatalogError):
            cli.graph_summary(graph)
        graph["live_node_ids"] = [1]
        with self.assertRaises(cli.CatalogError):
            cli.graph_summary(graph)


if __name__ == "__main__":
    unittest.main()
