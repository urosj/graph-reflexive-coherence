"""Retained evidence, versioned subjects, API/browser/notebook; no native rerun."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import lzma
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9101b_target_compatibility as checker
import p9101b_acceptance as acceptance

ROOT = checker.ROOT
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import target_compatibility as surface  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class TargetSurfaceTests(unittest.TestCase):
    def test_checked_targets_and_rehashed_mutations(self):
        value = surface.target_compatibility_status(ROOT)
        self.assertEqual(value["tests_run"], 12)
        self.assertEqual(value["original_target_surface_cells"], 16)
        self.assertEqual(value["explicit_basin_successor_surface_cells"], 16)
        self.assertTrue(value["user_accepted"])
        self.assertTrue(value["P9_10_1b_closed"])
        self.assertFalse(value["P9_10_1_closed"])
        self.assertEqual(value["remaining_work"], ["P9-10.1c"])
        for row in value["rows"]:
            self.assertNotEqual(
                row["versions"][0]["subject"]["model_identity"],
                row["versions"][1]["subject"]["model_identity"],
            )
        for field in ("subject", "rejection", "scope", "source", "roster"):
            record, ref = checker.load(ROOT, "C_OS")
            bad = deepcopy(record)
            if field == "subject":
                bad["evidence"]["v1"]["subject"]["model_identity"] = "source-only"
            elif field == "rejection":
                bad["evidence"]["v1"]["outcome"] = "rejected"
            elif field == "scope":
                bad["full_GRC9V4_conformance"] = True
            elif field == "source":
                bad["source_refs"][0]["sha256"] = "0" * 64
            else:
                bad["tests"].pop()
            with patch.object(checker, "load", return_value=(checker.seal(bad), ref)):
                with self.assertRaises(ValueError):
                    checker.check(ROOT, "C_OS")
        bad = deepcopy(checker.status(ROOT))
        bad["user_accepted"] = True
        with patch.object(checker, "status", return_value=checker.seal(bad)):
            with self.assertRaises(ValueError):
                surface.target_compatibility_status(ROOT)
        original = Path.read_bytes
        for field in (
            "user_accepted",
            "P9_10_1b_closed",
            "P9_10_1_closed",
            "full_GRC9V4_conformance",
        ):
            bad = deepcopy(acceptance.decision(ROOT))
            bad[field] = not bad[field]
            raw = json.dumps(checker.seal(bad)).encode()
            with patch.object(
                Path,
                "read_bytes",
                lambda p: raw if p == ROOT / acceptance.PATH else original(p),
            ):
                with self.assertRaisesRegex(ValueError, "acceptance decision or scope"):
                    surface.target_compatibility_status(ROOT)

    def test_sources_http_and_notebook(self):
        spec = importlib.util.spec_from_file_location(
            "target_evidence_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        handler = server.Handler.__new__(server.Handler)
        codes = []
        handler.send_response = codes.append
        handler.send_header = lambda *args: None
        handler.end_headers = lambda: None
        handler.path = "/api/tranche10/targets"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes, [200])
        value = json.loads(handler.wfile.getvalue())
        self.assertEqual(value, surface.target_compatibility_status(ROOT))
        handler.path = "/target-compatibility.js"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 200)
        self.assertEqual(
            handler.wfile.getvalue(),
            (TOOL / "phase9-web/target-compatibility.js").read_bytes(),
        )
        for row in value["records"]:
            raw, ref = surface.target_compatibility_source(ROOT, row["path"])
            self.assertEqual(checker.sha(raw), ref["sha256"])
            data = json.loads(
                lzma.decompress(raw) if row["path"].endswith(".xz") else raw
            )
            self.assertEqual(data["record_digest"], row["record_digest"])
        for row in value["source_refs"]:
            raw, ref = surface.target_compatibility_source(ROOT, row["path"])
            self.assertEqual(checker.sha(raw), ref["sha256"])
        handler.path = (
            "/api/tranche10/targets/source?path=" + value["records"][0]["path"]
        )
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 200)
        self.assertEqual(
            checker.sha(handler.wfile.getvalue()), value["records"][0]["sha256"]
        )
        handler.path = "/api/tranche10/targets/source?path=../outside"
        handler.wfile = BytesIO()
        handler.do_GET()
        self.assertEqual(codes[-1], 404)
        handler.path = "/api/tranche10/targets"
        with patch.object(
            server, "target_compatibility_status", side_effect=ValueError("drift")
        ):
            handler.wfile = BytesIO()
            handler.do_GET()
            self.assertEqual(codes[-1], 503)
            self.assertEqual(set(json.loads(handler.wfile.getvalue())), {"error"})
        book = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_bytes())
        cell = next(c for c in book["cells"] if c.get("id") == "expanded-targets")
        code = compile("".join(cell["source"]), "expanded-target-cell", "exec")
        ns = dict(repo_root=ROOT)
        exec(code, ns)
        self.assertEqual(ns["phase9_expanded_targets"], value)
        with patch.object(
            surface, "target_compatibility_status", side_effect=ValueError("drift")
        ):
            with self.assertRaises(ValueError):
                exec(code, ns)
            self.assertIsNone(ns["phase9_expanded_targets"])

    def test_browser_exact_scope_and_stale_output(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedTargets,targetLoader} from './target-compatibility.js';
import {canonicalBasin} from './basin.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedTargets(value),value);
for(const edit of [v=>v.user_accepted=false,v=>v.P9_10_1b_closed=false,v=>v.P9_10_1_closed=true,
 v=>v.full_GRC9V4_conformance=true,v=>v.rows[0].versions[0].outcome='rejected',
 v=>v.rows[0].versions[1].subject=v.rows[0].versions[0].subject,v=>v.records.pop(),
 v=>v.other_six_source_cells_executed=24,v=>v.families.push('A_OS')]) {
 const bad=structuredClone(value);edit(bad);delete bad.record_digest;
 bad.record_digest=createHash('sha256').update(canonicalBasin(bad)).digest('hex');
 await assert.rejects(checkedTargets(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=targetLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag}));
await load();assert.ok(output.children.length>12);assert.match(status.textContent,/bounded accepted/);assert.match(status.textContent,/P9-10.1 remains open/);
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
assert.match(readFileSync('index.html','utf8'),/id="targets-refresh"/);
"""
        result = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", js],
            cwd=TOOL / "phase9-web",
            input=json.dumps(surface.target_compatibility_status(ROOT)),
            text=True,
            capture_output=True,
            timeout=30,
            env=tool_environment(),
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
