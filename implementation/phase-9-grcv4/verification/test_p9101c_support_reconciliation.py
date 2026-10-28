"""Exact identity joins, honest scope and accessible current support; no native run."""

from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9101c_support_reconciliation as c
import p9101c_acceptance as acceptance

ROOT = c.ROOT
TOOL = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import tranche10_support as surface  # noqa: E402
from grcv4_explorer.phase9_verification import _profile_next_gate  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


class SupportReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pygrc.models import GRC9V4
        from pygrc.models.grc_9_v3 import GRC9V3
        from pygrc.models import grc_9_v4_basin as basin

        with (
            patch.object(
                GRC9V4, "from_config", side_effect=AssertionError("native construction")
            ),
            patch.object(GRC9V4, "step", side_effect=AssertionError("native V4 step")),
            patch.object(GRC9V3, "step", side_effect=AssertionError("native V3 step")),
            patch.object(
                basin, "_read_once", side_effect=AssertionError("native basin read")
            ),
        ):
            cls.data = c.inputs(ROOT)
            cls.value = c.assemble(ROOT, cls.data)
            with patch.object(c, "build", return_value=cls.value):
                cls.published = acceptance.status(ROOT)

    def test_acceptance_preserves_evidence_and_rejects_scope_drift(self):
        self.assertTrue(self.published["user_accepted"])
        self.assertTrue(self.published["P9_10_1c_closed"])
        self.assertTrue(self.published["P9_10_1_closed"])
        self.assertFalse(self.value["P9_10_1_closed"])
        self.assertFalse(self.published["full_GRC9V4_conformance"])
        self.assertEqual(self.published["authority"], self.value["authority"])
        self.assertEqual(self.published["open_items"], self.value["open_items"])
        self.assertIn("P9-10.2", self.published["next_work"])
        from pathlib import Path

        read = Path.read_bytes
        path = ROOT / acceptance.PATH
        original = json.loads(read(path))
        for field, changed in (
            ("P9_10_1_closed", False),
            ("full_GRC9V4_conformance", True),
            ("remaining_hold_ids", []),
            ("direct_target_evidence", []),
        ):
            bad = deepcopy(original)
            bad[field] = changed
            raw = json.dumps(c.seal(bad)).encode()
            with (
                self.subTest(field=field),
                patch.object(
                    Path, "read_bytes", lambda p: raw if p == path else read(p)
                ),
                self.assertRaises(ValueError),
            ):
                acceptance.decision(ROOT, self.value)

    def test_exact_subjects_and_retained_restrictions(self):
        self.assertEqual(json.loads((ROOT / c.PATH).read_bytes()), self.value)
        self.assertEqual(
            [r["id"] for r in self.value["resolved_holds"]],
            ["basin_surface", "target_identity_scope"],
        )
        self.assertEqual(
            [r["id"] for r in self.value["open_items"]], ["umbrella_compatibility"]
        )
        self.assertFalse(
            self.value["open_items"][0]["blocking_bounded_four_family_closure"]
        )
        self.assertTrue(
            self.value["open_items"][0][
                "blocking_umbrella_capability_and_full_conformance"
            ]
        )
        self.assertEqual(self.value["source_matrix_counts"]["bounded_accepted"], 16)
        self.assertEqual(
            self.value["source_matrix_counts"]["unselected_not_executed"], 24
        )
        self.assertFalse(self.value["P9_10_1_closed"])
        self.assertEqual(self.value["authority"], self.data["historical"]["authority"])
        for row in self.value["rows"]:
            old = next(
                r
                for r in self.data["historical"]["rows"]
                if r["family"] == row["family"]
            )
            for k, v in row["inherited_limits"].items():
                self.assertEqual(v, old[k])
            v1, v2 = row["expanded_target_compatibility"]
            self.assertEqual(v1["subject"], old["enabled_expansion_target"])
            self.assertEqual(
                v1["basin"]["status"], "historical_v1_without_basin_policy"
            )
            self.assertNotEqual(
                v1["subject"]["model_identity"], v2["subject"]["model_identity"]
            )
            self.assertNotEqual(
                row["basin_pressure_expansion_v2"]["subject"], v2["subject"]
            )
            self.assertFalse(v2["basin"]["independent_equation_pressure_transferred"])
            direct = v2["basin"]["direct_independent_check"]
            self.assertEqual(direct["native_role_captures"], 4)
            self.assertFalse(direct["user_accepted"])
            self.assertFalse(direct["exact_root_signs_claimed"])
            self.assertEqual(
                [b["label"] for b in direct["boundaries"]], list(c.exact_basin.LABELS)
            )
            for boundary in direct["boundaries"]:
                self.assertEqual(boundary["subject"], v2["subject"])
            self.assertEqual(
                [o["role"] for o in v2["basin"]["observations"]], ["current", "reset"]
            )

    def test_identity_acceptance_and_evidence_substitution_reject(self):
        for kind in (
            "unaccepted_a",
            "unaccepted_b",
            "missing_family",
            "source_alias",
            "pressure_alias",
            "refusal",
            "wrong_role",
            "forty",
            "authority",
            "optional",
            "direct_target_alias",
        ):
            with self.subTest(kind=kind):
                d = deepcopy(self.data)
                record = d["target_records"]["C_OS"]["evidence"]["v2"]
                if kind == "unaccepted_a":
                    d["basin"]["user_accepted"] = False
                elif kind == "direct_target_alias":
                    direct, _ = d["exact_target_basin"]["C_OS"]
                    direct["subject"] = d["historical"]["rows"][0]["source"]
                elif kind == "unaccepted_b":
                    d["targets"]["P9_10_1b_closed"] = False
                elif kind == "missing_family":
                    del d["basin_records"]["A_PC"]
                elif kind == "source_alias":
                    record["subject"] = d["historical"]["rows"][0]["source"]
                elif kind == "pressure_alias":
                    o = next(
                        o
                        for o in d["basin_records"]["C_OS"]["evidence"]["observations"]
                        if o["label"] == "after_supported_expansion"
                    )
                    record["subject"] = c.subject(o["saved_native_state"])[0]
                    record["final_checkpoint"]["owner"]["state"] = o[
                        "saved_native_state"
                    ]
                    record["final_checkpoint"]["owner"]["basin"] = o["observations"]
                elif kind == "refusal":
                    record["outcome"] = "rejected"
                elif kind == "wrong_role":
                    from pygrc.models.grc_9_v4_basin import observation

                    v = record["final_checkpoint"]["owner"]["basin"][
                        "reset_observation"
                    ]
                    v["binding"]["role"] = "current"
                    record["final_checkpoint"]["owner"]["basin"][
                        "reset_observation"
                    ] = observation(v["binding"], v["witness"])
                elif kind == "forty":
                    d["historical"]["matrix_counts"]["bounded_accepted"] = 40
                elif kind == "authority":
                    d["historical"]["authority"][0]["support_disposition"] = "normative"
                else:
                    d["historical"]["optional_completion"]["executed"] = True
                with self.assertRaises((ValueError, KeyError, AssertionError)):
                    c.assemble(ROOT, d)

    def test_resealed_result_mutations_and_source_drift_reject(self):
        with patch.object(c, "build", return_value=self.value):
            for kind in (
                "acceptance",
                "closure",
                "full",
                "erase_limit",
                "borrow_pressure",
                "numerics",
            ):
                v = deepcopy(self.value)
                if kind == "acceptance":
                    v["user_accepted"] = True
                elif kind == "closure":
                    v["P9_10_1_closed"] = True
                elif kind == "full":
                    v["full_GRC9V4_conformance"] = True
                elif kind == "erase_limit":
                    v["open_items"] = []
                elif kind == "borrow_pressure":
                    v["rows"][0]["expanded_target_compatibility"][1]["basin"][
                        "independent_equation_pressure_transferred"
                    ] = True
                else:
                    v["rows"][0]["inherited_limits"]["numerical_scope"] = "all graphs"
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    c.check(ROOT, c.seal(v))
        # The actual loader must reject changed execution source bytes even
        # without a numerical rerun; no mocked build in this pressure case.
        from pathlib import Path

        read = Path.read_bytes
        target = ROOT / "src/pygrc/models/grc_9_v4_api_lifecycle.py"
        with patch.object(
            Path,
            "read_bytes",
            lambda p: read(p) + b"# drift\n" if p == target else read(p),
        ):
            with self.assertRaises(ValueError):
                c.inputs(ROOT)

    def test_http_sources_notebook_and_current_status_wiring(self):
        spec = importlib.util.spec_from_file_location(
            "support_successor_server", TOOL / "scripts/serve_phase9.py"
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)

        def get(path):
            h = server.Handler.__new__(server.Handler)
            h.path, h.wfile = path, BytesIO()
            codes = []
            h.send_response = codes.append
            h.send_header = lambda *args: None
            h.end_headers = lambda: None
            h.do_GET()
            return codes[-1], h.wfile.getvalue()

        # The fixture authenticated the chain once. Reuse it to test access
        # without repeating all accepted source/classification reads per link.
        with patch.object(c, "build", return_value=self.value):
            code, raw = get("/api/tranche10/support")
            self.assertEqual(code, 200)
            self.assertEqual(json.loads(raw), self.published)
            for r in self.published["source_refs"]:
                code, raw = get("/api/tranche10/support/source?path=" + r["path"])
                self.assertEqual(code, 200)
                self.assertEqual(c.sha(raw), r["sha256"])
            self.assertEqual(
                get("/api/tranche10/support/source?path=../secret")[0], 404
            )
            self.assertEqual(get("/api/tranche10/support?family=A_OS")[0], 404)
            code, raw = get("/tranche10-support.js")
            self.assertEqual(code, 200)
            self.assertEqual(
                raw, (TOOL / "phase9-web/tranche10-support.js").read_bytes()
            )
            book = json.loads(
                (TOOL / "notebooks/phase9_verification.ipynb").read_bytes()
            )
            cell = next(c for c in book["cells"] if c.get("id") == "p9101c-support")
            ns = dict(repo_root=ROOT)
            code = compile("".join(cell["source"]), "current-support-cell", "exec")
            exec(code, ns)
            self.assertEqual(ns["phase9_current_support"], self.published)
            with patch.object(
                surface, "tranche10_support_status", side_effect=ValueError("drift")
            ):
                with self.assertRaises(ValueError):
                    exec(code, ns)
                self.assertIsNone(ns["phase9_current_support"])
        with patch.object(
            server, "tranche10_support_status", side_effect=ValueError("drift")
        ):
            code, raw = get("/api/tranche10/support")
            self.assertEqual(code, 503)
            self.assertEqual(set(json.loads(raw)), {"error"})
        self.assertEqual(
            _profile_next_gate(
                dict(tranche9_support={}, tranche10_support=self.published)
            ),
            self.published["next_work"],
        )
        self.assertIn(
            "profile_views['tranche10_support'] = tranche10_support_status(root)",
            (TOOL / "src/grcv4_explorer/phase9_verification.py").read_text(),
        )

    def test_browser_scope_history_and_failure_clearing(self):
        js = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkedReconciledSupport,reconciledSupportLoader} from './tranche10-support.js';
import {canonical} from './verification.js';
const value=JSON.parse(readFileSync(0,'utf8'));
assert.deepEqual(await checkedReconciledSupport(value),value);
for(const edit of [v=>v.user_accepted=false,v=>v.P9_10_1_closed=false,
 v=>v.full_GRC9V4_conformance=true,v=>v.open_items=[],v=>v.resolved_holds.pop(),
 v=>v.source_matrix_counts.bounded_accepted=40,
 v=>v.rows[0].expanded_target_compatibility[1].basin.independent_equation_pressure_transferred=true,
 v=>v.rows[0].expanded_target_compatibility[1].basin.direct_independent_check.boundaries.pop(),
 v=>v.rows[0].expanded_target_compatibility[1].subject=v.rows[0].basin_pressure_expansion_v2.subject]) {
 const bad=structuredClone(value);edit(bad);delete bad.record_digest;
 bad.record_digest=createHash('sha256').update(canonical(bad)).digest('hex');
 await assert.rejects(checkedReconciledSupport(bad));
}
const output={children:[],replaceChildren(){this.children=[]},append(e){this.children.push(e)}},status={};
let ok=true;
const load=reconciledSupportLoader(output,status,async()=>({ok,json:async()=>value}),tag=>({tag}));
await load();assert.match(status.textContent,/Two holds resolved/);assert.match(status.textContent,/bounded P9-10.1 closed/);
assert(output.children.some(e=>e.textContent?.includes('different exact target')));
assert.equal(output.children.filter(e=>e.textContent?.includes('New direct independent basin checks')).length,4);
assert.equal(output.children.filter(e=>e.textContent==='after_disabled_return').length,4);
assert(output.children.some(e=>e.textContent?.includes('24 unselected')));
ok=false;await load();assert.equal(output.children.length,0);assert.match(status.textContent,/unavailable/);
const html=readFileSync('index.html','utf8');assert.match(html,/id="tranche10-support-refresh"/);assert.match(html,/historical support review/);
"""
        r = subprocess.run(
            [str(managed_node()), "--input-type=module", "-e", js],
            input=json.dumps(self.published),
            cwd=TOOL / "phase9-web",
            text=True,
            capture_output=True,
            timeout=30,
            env=tool_environment(),
        )
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
