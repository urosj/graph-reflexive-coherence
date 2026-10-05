"""Focused retained-evidence and surface pressure; no native numerical campaign."""

import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

import tranche8_evidence as index
import tranche8_source_reuse as bridge

sys.path.insert(0, str(index.ROOT / index.SIDE / "tool/src"))
from grcv4_explorer import tranche8 as api  # noqa: E402


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = index.checked()

    def test_complete_population_and_separate_acceptance(self):
        v = self.value
        self.assertEqual({r["family"] for r in v["profiles"]}, set(index.FAMILIES))
        c = v["coverage"]
        self.assertEqual((c["accepted_cells"], c["required_cells"], c["pending_cells"]), (162, 322, 160))
        self.assertEqual(sum(r["pending_cells"] > 0 for r in c["families"]), 5)
        self.assertEqual(next(r["required_cells"] for r in c["families"] if r["family"] == "C_PC"), 34)
        failures = [r for run in c["runs"] for r in run["cases"] if not r["case_passed"]]
        self.assertEqual(len(failures), 2)
        self.assertTrue(all(r["event_committed"] and r["first_failure"] for r in failures))
        self.assertFalse(c["aggregate_closed"])
        self.assertFalse(v["verification"]["native_trajectories_rerun"])
        self.assertFalse(any(r["runtime_accepted"] for r in v["configuration"]["families"]))
        self.assertEqual(v["future"]["new_public_support"], [])

    def test_cci_acceptance_is_separate_and_original_failure_preserved(self):
        c = self.value["coverage"]
        row = next(r for r in c["families"] if r["family"] == "C_CI")
        self.assertEqual(row["accepted_cells"], 32)
        run = next(r for r in c["runs"] if r["family"] == "C_CI")
        self.assertEqual(run["acceptance"]["anchor"], "scoped-user-acceptance")
        self.assertEqual(run["status"], "accepted_bounded")
        self.assertEqual(run["execution_partition"]["retained_cases"], 8)
        self.assertEqual(len(run["original_attempt"]["failures"]), 1)
        failure = run["original_attempt"]["failures"][0]
        self.assertTrue(failure["event_committed"])
        self.assertFalse(failure["case_passed"])
        self.assertEqual(failure["first_failure"]["kind"], "operational_timeout")
        self.assertEqual(row["executed_pending_cells"], 0)
        self.assertEqual(row["accepted_cells"], 2 * run["passed_cases"])
        ref = run["results"]
        self.assertIsNone(ref["revision"])
        self.assertEqual(ref["basis"], "pinned_execution_with_separate_scoped_user_acceptance")
        with patch.object(index, "checked", return_value=self.value), patch.object(api, "_index", return_value=index):
            raw, actual = api.tranche8_source(index.ROOT, ref["path"])
            self.assertEqual(actual, ref)
            self.assertEqual(index.hashlib.sha256(raw).hexdigest(), ref["sha256"])
        original = Path.read_bytes
        path = index.ROOT / ref["path"]
        with patch.object(Path, "read_bytes", lambda p: b"forged" if p == path else original(p)):
            with self.assertRaisesRegex(ValueError, "accepted C_CI source drift"):
                index.Sources(index.ROOT).raw(ref["path"])

    def test_mutated_source_and_missing_git_never_fall_back(self):
        path = index.ROOT / index.BASE / "P9-8.4a-Coverage.json"
        original = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda p: original(p) + b" " if p == path else original(p)):
            with self.assertRaisesRegex(ValueError, "source drift"):
                index.build()
        with patch.object(index, "git", side_effect=FileNotFoundError("Git history unavailable")):
            with self.assertRaises(FileNotFoundError):
                index.build()

    def test_aci_acceptance_is_separate_from_execution(self):
        c = self.value["coverage"]
        row = next(r for r in c["families"] if r["family"] == "A_CI")
        run = next(r for r in c["runs"] if r["family"] == "A_CI")
        self.assertEqual((row["accepted_cells"], row["executed_pending_cells"]), (32, 0))
        self.assertEqual(c["accepted_cells"], 162)
        self.assertEqual(run["status"], "accepted_bounded")
        self.assertEqual(run["acceptance"]["anchor"], "scoped-user-acceptance")
        self.assertEqual(run["passed_cases"], 16)
        ref = run["results"]
        self.assertEqual(ref["basis"], "pinned_execution_with_separate_scoped_user_acceptance")
        with patch.object(index, "checked", return_value=self.value), patch.object(api, "_index", return_value=index):
            raw, actual = api.tranche8_source(index.ROOT, ref["path"])
            self.assertEqual(ref, actual)
            self.assertEqual(index.hashlib.sha256(raw).hexdigest(), ref["sha256"])
            execution = json.loads(raw)
            self.assertFalse(execution["user_accepted"])
            self.assertFalse(execution["aggregate_closed"])
        original = Path.read_bytes
        path = index.ROOT / ref["path"]
        with patch.object(Path, "read_bytes", lambda p: b"forged" if p == path else original(p)):
            with self.assertRaisesRegex(ValueError, "accepted A_CI source drift"):
                index.Sources(index.ROOT).raw(ref["path"])

    def test_generated_projection_cannot_supply_its_own_authority(self):
        original = Path.read_text
        with patch.object(index, "build", return_value=self.value), patch.object(
                Path, "read_text", lambda p, *a, **k: "forged" if p == index.ROOT / index.ASSET else original(p, *a, **k)):
            with self.assertRaisesRegex(ValueError, "browser evidence drift"):
                index.checked()

    def test_cpc_acceptance_is_separate_from_execution(self):
        coverage = self.value["coverage"]
        row = next(r for r in coverage["families"] if r["family"] == "C_PC")
        run = next(r for r in coverage["runs"] if r["family"] == "C_PC")
        self.assertEqual((row["accepted_cells"], row["executed_pending_cells"], row["pending_cells"]), (34, 0, 0))
        self.assertEqual(coverage["executed_pending_cells"], 0)
        self.assertEqual(run["status"], "accepted_bounded")
        self.assertEqual(run["acceptance"]["anchor"], "scoped-user-acceptance")
        self.assertEqual(run["passed_cases"], 17)
        self.assertTrue(any("C-PC-CARRIER-RESET" in r["case_id"] for r in run["cases"]))
        ref = run["results"]
        self.assertEqual(ref["basis"], "pinned_execution_with_separate_scoped_user_acceptance")
        with patch.object(index, "checked", return_value=self.value), patch.object(api, "_index", return_value=index):
            raw, actual = api.tranche8_source(index.ROOT, ref["path"])
            self.assertEqual(actual, ref)
            self.assertFalse(json.loads(raw)["user_accepted"])
            self.assertFalse(json.loads(raw)["aggregate_closed"])
        original = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda p: b"forged" if p == index.ROOT / ref["path"] else original(p)):
            with self.assertRaisesRegex(ValueError, "accepted C_PC source drift"):
                index.Sources(index.ROOT).raw(ref["path"])

    def test_aci_compaction_restores_exact_accepted_execution(self):
        from pygrc.models.grc_v4_codec import canonical_json_bytes

        raw = index.Sources(index.ROOT).raw(index.BASE + "P9-8.4b-ACIResults.json")
        value = json.loads(raw)
        compact = (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n").encode()
        self.assertEqual(raw, compact)
        # Formatting is reversible: even the accepted file's original byte
        # identity is recoverable, not merely numerically equivalent values.
        original = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
        self.assertEqual(index.hashlib.sha256(original).hexdigest(),
                         "2d2dbec6eb6c07db9b4fd996fe2d231a6ec2bb43682202a9f176c776c13f9466")
        self.assertLess(len(raw), 0.501 * len(original))
        record_digest = value.pop("record_digest")
        self.assertEqual(record_digest, "8b2691fc8623142e40ddc891379cb5e6c9450408190789fbb30448dbde1336a3")
        self.assertEqual(index.hashlib.sha256(canonical_json_bytes(value)).hexdigest(), record_digest)

    def test_bridge_rejects_third_identity_and_live_drift(self):
        name, row = next(iter(bridge.record()["changes"].items()))
        self.assertEqual(bridge.retained_bindings({name: row["after_sha256"]}), {name: row["before_sha256"]})
        with self.assertRaisesRegex(ValueError, "unrelated identity"):
            bridge.retained_bindings({name: "0" * 64})
        original = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda p: b"drift" if p == index.ROOT / name else original(p)):
            with self.assertRaisesRegex(ValueError, "unreviewed change"):
                bridge.retained_bindings({name: row["after_sha256"]})
        name, sha = next(iter(bridge.record()["additions"].items()))
        self.assertEqual(bridge.retained_bindings({name: sha}), {})
        with self.assertRaisesRegex(ValueError, "historical-roster addition"):
            bridge.retained_bindings({name: "0" * 64})
        self.assertEqual(bridge.retained_bindings({"unknown.py": "0" * 64}), {"unknown.py": "0" * 64})

    def test_exact_source_route_and_traversal_rejection(self):
        with patch.object(index, "checked", return_value=self.value), patch.object(api, "_index", return_value=index):
            raw, ref = api.tranche8_source(index.ROOT, index.HANDOFF)
            self.assertEqual(raw, index.git(index.ROOT, "show", index.CHECKPOINT + ":" + index.HANDOFF))
            self.assertEqual(ref["basis"], "historical_git")
            for name in ("../pyproject.toml", "/etc/passwd", "unlisted.json"):
                with self.assertRaises(KeyError):
                    api.tranche8_source(index.ROOT, name)

    def test_linear_composition_preserves_exact_stage_and_rejects_unknown_roster(self):
        import c_rg2b_g2_source_reuse as previous
        import g2_source_reuse as composed
        name = "tests/models/test_grc_v4_profile.py"
        current = {name: bridge.p.sha((index.ROOT / name).read_bytes())}
        self.assertEqual(bridge.through(current, "c_rg2b_g2_source_reuse"), previous.retained_bindings(current))
        for _, expected in bridge.projections(current):
            self.assertTrue(composed.matches(expected, current))
        self.assertFalse(composed.matches({}, {"unregistered.py": "0" * 64}))
        self.assertFalse(composed.matches({"missing.py": "0" * 64}, {}))

    def test_real_notebook_cell_clears_stale_output_on_failure(self):
        notebook = json.loads((index.ROOT / index.SIDE / "tool/notebooks/phase9_verification.ipynb").read_text())
        cell = next(c for c in notebook["cells"] if c["id"] == "query-tranche8")
        namespace = dict(Path=Path, repo_root=index.ROOT, phase9_tranche8="old-success")
        with patch.object(api, "tranche8_status", side_effect=ValueError("source drift")):
            with self.assertRaises(ValueError):
                exec("".join(cell["source"]), namespace)
        self.assertIsNone(namespace["phase9_tranche8"])

    def test_actual_numeric_view_has_cross_language_status_digest(self):
        from grcv4_explorer.phase9_verification import status_digest
        from grcv4_explorer.tooling import managed_node
        payload = {"tranche8_evidence": self.value, "numeric_pressure": [1.0, 1e-7, -0.0, 1e20]}
        script = "import {createHash} from 'node:crypto'; import {canonical} from './" + index.SIDE + "tool/phase9-web/verification.js'; let s=''; for await(const b of process.stdin)s+=b; console.log(createHash('sha256').update(canonical(JSON.parse(s))).digest('hex'));"
        actual = subprocess.check_output([str(managed_node()), "--input-type=module", "-e", script],
                                         cwd=index.ROOT, input=json.dumps(payload).encode()).decode().strip()
        self.assertEqual(status_digest(payload), actual)


if __name__ == "__main__":
    unittest.main(verbosity=2)
