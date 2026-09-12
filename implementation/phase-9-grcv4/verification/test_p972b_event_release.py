"""Package/declaration and isolated charge checks; no lifecycle/transport runs."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import build_p972b_event_release as r
import build_p972b_contract as b
from pygrc.models import grc_v4_event_codec as c
from pygrc.models import grc_v4_codec as old
from test_p972b_contract import EventContractTests


class JointPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = b.read(r.VECTORS)
        cls.manifest = b.read(r.RELEASE)
        EventContractTests.setUpClass()
        cls.legacy = EventContractTests()

    def validate(self, name, value):
        return c.validate_event_payload("representation/" + name, value)

    def map_check(self, record=None, source=None, target=None):
        return c.validate_correspondence(self.v["correspondence_record"] if record is None else record,
            self.v["source_graph"] if source is None else source, self.v["target_graph"] if target is None else target)

    def rehash(self, record):
        record["correspondence_id"] = b.identity("grcv4-coordinate-map-sha256", record["payload"])

    def test_exact_package_pins_and_inherited_bytes(self):
        for name, raw in r.build().items():
            self.assertEqual((b.ROOT / name).read_bytes(), raw, name)
        self.assertEqual(c.EVENT_RELEASE_ID, self.manifest["release_id"])
        self.assertEqual(c._MANIFEST_SHA256, sha256((b.ROOT / r.RELEASE).read_bytes()).hexdigest())
        self.assertEqual(self.manifest["release_id"], b.identity("grcv4-spec-release-sha256", self.manifest["release_identity_payload"]))
        self.assertEqual(len(c.load_event_schemas()), 4)
        for name in b.FROZEN:
            self.assertEqual((b.ROOT / name).read_bytes(), subprocess.check_output(["git", "show", "ed61c1d:" + name], cwd=b.ROOT))

    def test_correspondence_and_wire_identities(self):
        self.assertEqual(self.map_check(), self.v["correspondence_record"])
        self.assertEqual(c.validate_representation_request(self.v["request"], self.v["source_graph"]), self.v["request"])
        bad = deepcopy(self.v["request"]); bad["source_graph_digest"] = "grc-graph-sha256:" + "0" * 64
        with self.assertRaises(old.V4IdentityError): c.validate_representation_request(bad, self.v["source_graph"])
        for name in ("request", "operation_identity_payload", "receipt_payload"):
            self.validate(name, self.v[name])
        for row in self.v["canonical_vectors"]:
            value = self.v
            for key in row["pointer"].split("/"):
                value = value[key]
            self.assertEqual(old.canonical_json_bytes(value).decode(), row["canonical_jcs_utf8"])
            if row["identity_prefix"] == "grc-commit-sha256":
                self.assertEqual(b.identity(row["identity_prefix"], value), row["expected_identifier"])
            else:
                name = "correspondence_payload" if row["pointer"].endswith("/payload") else row["pointer"]
                self.assertEqual(c.representation_identity(name, value, expected=row["expected_identifier"]), row["expected_identifier"])
        for operation, metadata in (("other-operation", {}), ("other-operation", {"note": "diagnostic"})):
            request = deepcopy(self.v["request"]); request.update(operation_id=operation, metadata=metadata)
            self.validate("request", request)
            # Neither request-only field occurs in the operation preimage.
            self.assertNotIn("operation_id", self.v["operation_identity_payload"])
            self.assertNotIn("metadata", self.v["operation_identity_payload"])

    def test_bijection_order_endpoints_and_sign_fail_closed_after_rehash(self):
        mutations = (
            lambda p: p["vertex_map"].pop(),
            lambda p: p["vertex_map"].reverse(),
            lambda p: p["vertex_map"][0].update(target_vertex_id="x"),
            lambda p: p["vertex_map"][0].update(target_vertex_id="missing"),
            lambda p: p["edge_map"].pop(),
            lambda p: p["edge_map"].reverse(),
            lambda p: p["edge_map"][0].update(target_edge_id="reverse"),
            lambda p: p["edge_map"][0].update(target_edge_id="missing"),
            lambda p: p["edge_map"][1].update(orientation=1),
            lambda p: p["edge_map"][2].update(orientation=0),
            lambda p: p["edge_map"][2].update(orientation=True),
            lambda p: p.update(source_graph_digest="grc-graph-sha256:" + "0" * 64),
        )
        for mutate in mutations:
            record = deepcopy(self.v["correspondence_record"]); mutate(record["payload"]); self.rehash(record)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                self.map_check(record)
        for kind in ("duplicate", "endpoint"):
            source = deepcopy(self.v["source_graph"])
            if kind == "duplicate":
                source["oriented_edges"][1]["edge_id"] = "e"
            else:
                source["oriented_edges"][2]["tail_node_id"] = "missing"
            record = deepcopy(self.v["correspondence_record"])
            record["payload"]["source_graph_digest"] = b.identity("grc-graph-sha256", source); self.rehash(record)
            with self.assertRaises(ValueError):
                self.map_check(record, source)

    def test_loop_sign_and_parallel_correspondence_are_explicit_not_guessed(self):
        record = deepcopy(self.v["correspondence_record"])
        record["payload"]["edge_map"][2]["orientation"] = 1
        self.rehash(record)
        self.map_check(record)  # Both signs have identical loop incidence, different declared action.
        self.assertNotEqual(record["correspondence_id"], self.v["correspondence_record"]["correspondence_id"])
        record = deepcopy(self.v["correspondence_record"])
        record["payload"]["edge_map"][0].update(target_edge_id="reverse", orientation=-1)
        record["payload"]["edge_map"][1].update(target_edge_id="e2", orientation=1)
        self.rehash(record); self.map_check(record)
        self.assertNotEqual(record["correspondence_id"], self.v["correspondence_record"]["correspondence_id"])

    def test_closed_shapes_identity_suffixes_and_no_loss_or_initializer(self):
        examples = {"correspondence_payload": self.v["correspondence_record"]["payload"],
                    "correspondence_record": self.v["correspondence_record"], "request": self.v["request"],
                    "operation_identity_payload": self.v["operation_identity_payload"], "receipt_payload": self.v["receipt_payload"]}
        for name, value in examples.items():
            for key in value:
                bad = deepcopy(value); del bad[key]
                with self.subTest(schema=name, missing=key), self.assertRaises(ValueError): self.validate(name, bad)
            bad = deepcopy(value); bad["initializer_pair_id"] = "unwanted"
            with self.assertRaises(ValueError): self.validate(name, bad)
        for k, v in (("actual_charge_delta", 1), ("information_losses", ["candidate_history_loss"])):
            bad = deepcopy(self.v["receipt_payload"]); bad["core"][k] = v
            with self.assertRaises(ValueError): self.validate("receipt_payload", bad)
        bad = deepcopy(self.v["correspondence_record"]); bad["correspondence_id"] += "\n"
        with self.assertRaises(ValueError): self.validate("correspondence_record", bad)
        for s in ("candidate", "carrier"):
            bad = deepcopy(self.v["receipt_payload"]); bad["history"][s]["disposition"] = "target_initializer"
            with self.assertRaises(ValueError): self.validate("receipt_payload", bad)

    def mixed_snapshot(self):
        snap = self.legacy.mixed_snapshot()
        snap.update(implementation_layout_id=c.REPRESENTATION_LAYOUT, specification_release_id=c.EVENT_RELEASE_ID)
        row = self.legacy.transition(0)
        row.update(request=deepcopy(self.v["request"]), initializer_pair=None)
        group = deepcopy(self.v["operation_group"])
        head = snap["commit_records"][-1]["payload"]["emitted_receipt_ids"][0]
        group["receipts"][0]["identity_payload"]["core"]["parent_receipt_ids"] = [head]
        self.rehash_group(group)
        c.validate_representation_group(group, previous_primary_receipt_id=head)
        rid = group["receipts"][0]["receipt_id"]
        row["commit_id"] = group["commit_record"]["commit_id"]
        snap["transition_records"].append(row)
        snap["receipt_ledger"].extend(group["receipts"])
        snap["commit_records"].append(group["commit_record"])
        snap["lifecycle"]["receipt_ids"].append(rid)
        snap["lifecycle_digest"] = b.identity("grcv4-lifecycle-sha256", snap["lifecycle"])
        return snap

    @staticmethod
    def rehash_group(group):
        envelope = group["receipts"][0]
        envelope["receipt_id"] = b.identity("grc-receipt-sha256", envelope["identity_payload"])
        record = group["commit_record"]
        record["payload"]["emitted_receipt_ids"] = [envelope["receipt_id"]]
        record["commit_id"] = b.identity("grc-commit-sha256", record["payload"])
        envelope["commit_id"] = record["commit_id"]

    def test_complete_singleton_group_identity_links_and_previous_head(self):
        group = deepcopy(self.v["operation_group"])
        self.assertEqual(c.validate_representation_group(group, previous_primary_receipt_id=None), group)
        head = "grc-receipt-sha256:" + "1" * 64
        group["receipts"][0]["identity_payload"]["core"]["parent_receipt_ids"] = [head]
        self.rehash_group(group)
        out = c.validate_representation_group(group, previous_primary_receipt_id=head)
        out["receipts"].clear()
        self.assertEqual(len(group["receipts"]), 1)
        with self.assertRaises(ValueError): c.validate_representation_group(group, previous_primary_receipt_id=None)
        with self.assertRaises(ValueError): c.validate_representation_group(group, previous_primary_receipt_id="grc-receipt-sha256:" + "2" * 64)
        mutations = (
            lambda g: g["receipts"].clear(),
            lambda g: g["receipts"].extend(deepcopy(g["receipts"]) * 3),
            lambda g: g["commit_record"]["payload"]["emitted_receipt_ids"].append(head),
            lambda g: g["commit_record"].update(commit_id="grc-commit-sha256:" + "1" * 64),
            lambda g: g["receipts"][0].update(commit_id="grc-commit-sha256:" + "2" * 64),
            lambda g: g["receipts"][0].update(receipt_id=head),
            lambda g: g["receipts"][0]["identity_payload"]["core"]["parent_receipt_ids"].append(head),
        )
        for mutate in mutations:
            bad = deepcopy(group); mutate(bad)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                c.validate_representation_group(bad, previous_primary_receipt_id=head)
        for key, value in (("operation_id", "different"), ("source_state_digest", "grcv4-state-sha256:" + "1" * 64),
                           ("target_state_digest", "grcv4-state-sha256:" + "2" * 64)):
            bad = deepcopy(group); bad["commit_record"]["payload"][key] = value; self.rehash_group(bad)
            with self.assertRaises(old.V4IdentityError): c.validate_representation_group(bad, previous_primary_receipt_id=head)

    def test_charge_order_meaning_and_complete_embedded_evidence(self):
        from fractions import Fraction
        from pygrc.models.grc_v4_geometry import GRCV4Graph, VertexScalar
        from pygrc.models.grc_v4_transport import ChargeEvaluation
        from tests.models.test_grc_v4_transport import charge_profile

        source = (1.0, 2**-53, 2**-53)
        target = (2**-53, 2**-53, 1.0)
        self.assertEqual(sum(map(Fraction, source)), sum(map(Fraction, target)))
        graph = GRCV4Graph(("a", "b", "c"), ())
        profile = charge_profile(absolute_tolerance=2**-52, relative_tolerance=0)
        checks = [ChargeEvaluation(VertexScalar(graph, values), 1.0, profile) for values in (source, target)]
        self.assertTrue(all(x.admitted for x in checks))
        self.assertEqual(checks[1].actual - checks[0].actual, 2**-52)
        self.assertFalse(ChargeEvaluation(VertexScalar(graph, target), 1.0,
                                         charge_profile(absolute_tolerance=0, relative_tolerance=0)).admitted)
        receipt = deepcopy(self.v["receipt_payload"])
        self.assertEqual(receipt["core"]["actual_charge_delta"], 0)
        for role, evaluation in zip(("source", "target"), checks):
            self.assertEqual(receipt["charge"]["current"][role], evaluation.receipt_values())
        self.validate("receipt_payload", receipt)
        for role in ("current", "reset"):
            for endpoint in ("source", "target"):
                for key in ("target_charge", "admitted_charge", "residual"):
                    bad = deepcopy(receipt); del bad["charge"][role][endpoint][key]
                    with self.assertRaises(ValueError): self.validate("receipt_payload", bad)
        for mutation in (
            lambda p: p["charge"].update(delta_semantics="reduced_charge_difference"),
            lambda p: p["charge"]["reset"]["source"].update(residual=-0.0),
            lambda p: p["core"].update(actual_charge_delta=2**-52),
            lambda p: p["core"].update(resource_transform_digest="grcv4-resource-transform-sha256:" + "0" * 64),
            lambda p: p["core"].update(history_bundle_digest="grcv4-history-map-sha256:" + "0" * 64),
        ):
            bad = deepcopy(receipt); mutation(bad)
            with self.assertRaises(ValueError): self.validate("receipt_payload", bad)
        # No weakening of the old auxiliary core to make the new group fit.
        auxiliary = dict(schema_version="grcv4-charge-receipt-v1", core=receipt["core"], **checks[1].receipt_values())
        with self.assertRaises(ValueError): old.validate_payload("charge_receipt_identity_payload", auxiliary)

    def test_joint_and_mixed_layout_dispatch_not_model_restore(self):
        fallback = self.legacy.mixed_snapshot(); fallback["specification_release_id"] = c.EVENT_RELEASE_ID
        self.assertEqual(c.event_snapshot_payload(fallback), fallback)
        mixed = self.mixed_snapshot()
        self.assertEqual(c.event_snapshot_payload(mixed), mixed)
        self.assertEqual(len(mixed["transition_records"]), 6)
        for value in (mixed, fallback):
            with self.assertRaises(ValueError): old.snapshot_payload(value)
            for release in (old.RELEASE_ID, old.INITIALIZER_RELEASE_ID, "grcv4-spec-release-sha256:" + "0" * 64):
                bad = deepcopy(value); bad["specification_release_id"] = release
                with self.assertRaises(old.V4IdentityError): c.event_snapshot_payload(bad)
        bad = deepcopy(mixed); bad["transition_records"][-1]["initializer_pair"] = deepcopy(self.legacy.pair)
        with self.assertRaises(ValueError): c.event_snapshot_payload(bad)
        bad = deepcopy(mixed); bad["implementation_layout_id"] = c.EVENT_LAYOUT
        with self.assertRaises(ValueError): c.event_snapshot_payload(bad)
        bad = deepcopy(fallback); bad["implementation_layout_id"] = old.INITIALIZER_SNAPSHOT_LAYOUT_ID
        with self.assertRaises(ValueError): c.event_snapshot_payload(bad)

    def test_missing_altered_and_rehashed_impostor_assets_reject(self):
        original = c.resources.files
        class Broken:
            def __init__(self, real, name, content): self.real, self.name, self.content = real, name, content
            def joinpath(self, name):
                if name != self.name: return self.real.joinpath(name)
                return self
            def read_bytes(self):
                if self.content is None: raise FileNotFoundError("missing contract asset")
                return self.content
        for filename in ("grc-v4-event-contract-release.json", *c._SCHEMAS):
            for content in (None, b"{}\n"):
                with self.subTest(file=filename), patch.object(c.resources, "files", side_effect=lambda name:
                        Broken(original(name), filename, content)), self.assertRaises(old.V4AssetError):
                    c.load_event_schemas()
        impostor = deepcopy(self.manifest)
        impostor["release_identity_payload"]["representation_policy_id"] = "impostor"
        impostor["release_id"] = b.identity("grcv4-spec-release-sha256", impostor["release_identity_payload"])
        with patch.object(c.resources, "files", side_effect=lambda name: Broken(original(name),
                "grc-v4-event-contract-release.json", json.dumps(impostor).encode())), self.assertRaises(old.V4AssetError):
            c.load_event_schemas()

    def test_fresh_process_package_lookup_is_not_repository_cwd_dependent(self):
        env = dict(os.environ, PYTHONPATH=str(b.ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-c", "from pygrc.models.grc_v4_event_codec import load_event_schemas; assert len(load_event_schemas()) == 4; print('package lookup passed')"],
                                cwd=Path(sys.executable).parent, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "package lookup passed")


if __name__ == "__main__":
    unittest.main()
