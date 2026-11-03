"""Compact archive provenance, exact replay, hostile edits and fresh-checkout use."""

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import p991a5_native_spark_compact as compact
import p991a5_native_spark_compact_epoch as epoch
from cos_native_spark_oracle import matrix
from p991a5_native_spark_verify import verify_step

ROOT = compact.ROOT
SIDE = (
    ROOT
    / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
)
sys.path.insert(0, str(SIDE / "src"))
from grcv4_explorer import spark_native_campaign as native
from grcv4_explorer.errors import SourceAdmissionError


class COSCompactTests(unittest.TestCase):
    def test_all_exact_states_endpoints_and_full_old_stream_independence(self):
        original = Path.open
        removed = {ROOT / compact.FILES[r] for r in compact.EXPECTED}

        def no_full(path, *args, **kwargs):
            if path in removed:
                raise AssertionError("obsolete full stream was accessed")
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", no_full):
            value = compact.check(ROOT)
            view = native.native_campaign(ROOT)
            self.assertEqual(value["exact_reconstructed_transitions"], 753)
            self.assertEqual(view["roles"], compact.original_record(ROOT)["roles"])
            self.assertLess(view["evidence_storage"]["compressed_bytes"], 5 * 2**20)
            self.assertFalse(value["history_rewritten"])
            self.assertEqual(value["numerical_steps_executed"], 0)

    def test_all_ten_full_samples_reconstruct_and_independently_verify(self):
        inputs = next(compact.stream(compact.FILES["inputs"]))
        graph = inputs["target_configuration"]["reference"]["graph"]
        replay = compact.Reconstruction(graph)
        count = 0
        for index, role in enumerate(compact.EXPECTED):
            cert = inputs["certificates"][index]
            for full in compact.full_samples(role):
                row = compact.project(full)
                self.assertEqual(replay.restore(row), full)
                self.assertEqual(
                    verify_step(
                        graph,
                        full["stage"],
                        matrix(cert["operands"]["U"]),
                        cert["proof"]["full_step_error"],
                    ),
                    full["independent_error_upper"],
                )
                count += 1
        self.assertEqual(count, 10)

    def test_rehashed_wrong_operands_cannot_reconstruct_original_record(self):
        inputs = next(compact.stream(compact.FILES["inputs"]))
        replay = compact.Reconstruction(
            inputs["target_configuration"]["reference"]["graph"]
        )
        original = compact.project(next(compact.full_samples("current")))
        for kind in ("before", "after", "flux", "gain", "error", "chain"):
            changed = deepcopy(original)
            if kind in ("before", "after", "flux"):
                changed["stage"][kind][0] = "1/2"
            elif kind == "gain":
                changed["local_gain"] = 99
            elif kind == "error":
                changed["independent_error_upper"] = "0"
            else:
                changed["original_previous_record_digest"] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                replay.restore(compact.seal(changed))

    def test_side_tool_rejects_rehashed_manifest_and_changed_compact_bytes(self):
        original = Path.open
        for name in (
            compact.MANIFEST,
            compact.COMPACT["current"],
            compact.SAMPLES,
            compact.SELF,
        ):
            if name == compact.MANIFEST:
                value = json.loads((ROOT / name).read_bytes())
                value["exact_reconstructed_transitions"] = 752
                raw = json.dumps(compact.seal(value)).encode()
            else:
                raw = (ROOT / name).read_bytes() + b"changed"

            def altered(path, *args, name=name, raw=raw, **kwargs):
                return (
                    BytesIO(raw)
                    if path == ROOT / name
                    else original(path, *args, **kwargs)
                )

            with (
                patch.object(Path, "open", altered),
                self.subTest(name=name),
                self.assertRaises(SourceAdmissionError),
            ):
                native.native_campaign(ROOT)

    def test_finite_storage_successor_preserves_every_accepted_epoch(self):
        self.assertEqual(
            epoch.manifest(ROOT), json.loads((ROOT / epoch.PATH).read_bytes())
        )
        for name in epoch.CHANGED:
            self.assertEqual(
                epoch.previous_bytes(ROOT, name), epoch.original(ROOT, name)
            )
        for name in (
            "p991a6_arg2b_epoch",
            "p991a6_crg2b_epoch",
            "p991a6_acipc_campaign_epoch",
            "p991a6_aci_epoch",
            "p991a6_aos_epoch",
            "p991a5_native_spark_epoch",
        ):
            module = __import__(name)
            raw = (ROOT / module.PATH).read_bytes()
            self.assertEqual(
                raw,
                subprocess.check_output(
                    ["git", "show", epoch.REVISION + ":" + module.PATH], cwd=ROOT
                ),
            )
        epoch.validated_history(ROOT)
        original = Path.read_bytes
        name = next(iter(epoch.CHANGED))
        with (
            patch.object(
                Path,
                "read_bytes",
                lambda path: (
                    original(path) + (b"changed" if path == ROOT / name else b"")
                ),
            ),
            self.assertRaises(ValueError),
        ):
            epoch.previous_bytes(ROOT, name)

    def test_batched_history_rejects_changed_manifests_and_immutable_preimages(self):
        original = Path.read_bytes
        historical = "implementation/phase-9-grcv4/tranche-9/" + epoch.HISTORY[0][1]
        for name in (epoch.PATH, historical):
            changed = json.loads(original(ROOT / name))
            changed["old_execution_relabelled"] = True
            raw = json.dumps(epoch.seal(changed)).encode()
            with (
                patch.object(
                    Path,
                    "read_bytes",
                    lambda path, name=name, raw=raw: (
                        raw if path == ROOT / name else original(path)
                    ),
                ),
                self.subTest(name=name),
                self.assertRaises(ValueError),
            ):
                epoch.validated_history(ROOT)
        original_blob = epoch.git_blob

        def forged(root, revision, name):
            raw = original_blob(root, revision, name)
            return raw + b"changed" if revision == "86a68d3d" else raw

        with patch.object(epoch, "git_blob", forged), self.assertRaises(ValueError):
            epoch.validated_history(ROOT)

    def test_original_summary_and_runtime_have_no_changes(self):
        for name in [
            compact.RECORD + ".xz",
            compact.BASE + "P9-9.1a.5-Execution.json.xz",
        ]:
            self.assertEqual(
                (ROOT / name).read_bytes(),
                subprocess.check_output(
                    ["git", "show", epoch.REVISION + ":" + name], cwd=ROOT
                ),
            )
        changed = subprocess.check_output(
            ["git", "diff", epoch.REVISION, "--name-only", "--", "src/"],
            cwd=ROOT,
            text=True,
        )
        self.assertEqual(changed, "")
        value = compact.checked_manifest(ROOT)
        self.assertEqual(
            value["original_campaign_sha256"],
            sha256((ROOT / compact.RECORD).read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
