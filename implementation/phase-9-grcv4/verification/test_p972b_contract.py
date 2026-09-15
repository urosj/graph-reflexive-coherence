"""Event contract pressure only: no initializer/event execution or release grant."""

from copy import deepcopy
from hashlib import sha256
import json
import math
import re
import unittest

import build_p972b_contract as b
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from pygrc.models.grc_v4_codec import (
    canonical_json_bytes, decode_canonical_json, snapshot_payload,
    validate_initializer_payload, validate_payload,
)


class EventContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = b.read(b.SCHEMA)
        cls.vectors = b.read(b.VECTORS)
        cls.init = b.read("specs/" + b.INIT)
        cls.base = b.read("specs/" + b.BASE)
        cls.registry = Registry().with_resources((doc["$id"], Resource.from_contents(doc))
                                                 for doc in (cls.schema, cls.init, cls.base))
        cls.pair = cls.vectors["pair_record"]

    def validate(self, name, value):
        canonical_json_bytes(value)
        Draft202012Validator({"$ref": self.schema["$id"] + "#/$defs/" + name},
                             registry=self.registry).validate(value)

    def receipt_links(self, row, pair):
        """Wire/declaration links only; does not recompute numerical outputs."""
        p, policy = row["payload"], row["history_policy"]
        self.validate("event_receipt_payload", p)
        self.validate("history_policy", policy)
        self.assertEqual(row["receipt_id"], b.identity("grc-receipt-sha256", p))
        self.assertEqual(row["canonical_jcs_utf8"].encode(), canonical_json_bytes(p))
        event = row["event_identity_payload"]
        validate_payload("mapped_topology_event_identity_payload", event)
        self.assertEqual(p["event_id"], b.identity("grc-event-sha256", event))
        for key in ("source_state_digest", "source_graph_digest", "target_graph_digest",
                    "resource_transform_digest", "history_bundle_digest"):
            self.assertEqual(event[key], p["core"][key])
        self.assertEqual(event["target_profile_id"], p["core"]["target_model_identity"])
        self.assertEqual(p["core"]["history_bundle_digest"], b.identity("grcv4-history-map-sha256", dict(
            schema_version="grcv4-history-bundle-identity-v1", history_bundle=policy)))
        losses = []
        for s in ("candidate", "carrier"):
            for k in ("subject", "disposition", "source_history_digest", "information_loss"):
                self.assertEqual(p["history"][s][k], policy[s][k])
            if policy[s]["information_loss"] != "none":
                losses.append(policy[s]["information_loss"])
        self.assertEqual(p["core"]["information_losses"], losses)
        if policy["candidate"]["target_initializer_id"] is None:
            self.assertIsNone(pair)
            self.assertIsNone(p["initializer_pair_id"])
        else:
            self.assertIsNotNone(pair)
            validate_initializer_payload("pair_record", pair)
            self.assertEqual(p["initializer_pair_id"], pair["initializer_pair_id"])
            self.assertEqual(pair["initializer_pair_id"], b.identity("grcv4-a-reference-pass-pair-sha256", pair["payload"]))
            for role in ("current", "reset"):
                r = pair["payload"][role]
                self.assertEqual(r["payload"]["role"], role)
                self.assertEqual(r["construction_id"], b.identity("grcv4-a-reference-pass-construction-sha256", r["payload"]))
        return {"wire_linkage_checked": True, "producer_authenticated": False, "event_executed": False}

    def request(self, index=4):
        ref = self.pair["payload"]["current"]["payload"]["target_reference"]
        core = self.vectors["synthetic_receipts"][0]["payload"]["core"]
        return dict(schema_version="grcv4-mapped-topology-event-request-v1", operation_id="synthetic",
                    source_state_digest=core["source_state_digest"], source_graph_digest=core["source_graph_digest"],
                    target_graph=deepcopy(ref["graph"]), target_profile_id=core["target_model_identity"],
                    resource_transform=dict(schema_version="grcv4-resource-event-transform-v1", policy_id="synthetic-map",
                                            source_vertex_ids=[0, 1], target_vertex_ids=[0, 1],
                                            row_major_coefficients=[1, 0, 0, 1], target_increment=[0.5, 0]),
                    history_policy=deepcopy(self.vectors["policy_cases"][index]["history_policy"]), metadata={})

    def snapshot(self):
        ref = deepcopy(self.pair["payload"]["current"]["payload"]["target_reference"])
        digest = lambda name: name + ":" + "0" * 64
        state = dict(schema_version="grcv4-scientific-state-v1", active_model_identity=ref["profile"]["complete_profile_id"],
                     graph_digest=digest("grc-graph-sha256"), orientation_identity="synthetic-wire-order", step_index=0,
                     time=0, authoritative=dict(C=[0, 0], W_A=[1], Z_4=None), reset_digest=digest("grcv4-reset-sha256"),
                     Q_target=0, context_contract_id="constant_zero_context_v1", context_value_digest=None)
        reset = {k: deepcopy(state[k]) for k in ("active_model_identity", "graph_digest", "orientation_identity",
                                                "authoritative", "Q_target", "context_contract_id")}
        reset["schema_version"] = "grcv4-reset-baseline-v1"
        return dict(schema_version="grcv4-snapshot-v1", model_family="GRCV4", implementation_layout_id=b.LAYOUT,
                    receipt_parent_policy_id="grcv4-previous-successful-primary-v1",
                    specification_release_id=digest("grcv4-spec-release-sha256"), reference=ref, scientific_state=state,
                    scientific_state_digest=digest("grcv4-state-sha256"), reset=reset, reset_digest=digest("grcv4-reset-sha256"),
                    receipt_ledger=[], commit_records=[], lifecycle=dict(schema_version="grcv4-lifecycle-envelope-v1",
                    scientific_state_digest=digest("grcv4-state-sha256"), receipt_ids=[]), lifecycle_digest=digest("grcv4-lifecycle-sha256"),
                    reference_registry=[ref], differential_reference_registry=[], transition_records=[])

    def transition(self, index=0):
        snap = self.snapshot()
        row = dict(commit_id="grc-commit-sha256:" + "0" * 64, request=self.request(index),
                   source=deepcopy(snap["scientific_state"]), source_reset=deepcopy(snap["reset"]),
                   target=deepcopy(snap["scientific_state"]), target_reset=deepcopy(snap["reset"]), initializer_pair=None)
        if row["request"]["history_policy"]["candidate"]["target_initializer_id"] is not None:
            row["initializer_pair"] = deepcopy(self.pair)
        case = self.vectors["policy_cases"][index]
        for endpoint in ("source", "target"):
            for name in (endpoint, endpoint + "_reset"):
                authority = row[name]["authoritative"]
                authority["W_A"] = [1] if case[endpoint + "_candidate"] == "A" else None
                authority["Z_4"] = [0] if case[endpoint + "_persistent"] else None
        return row

    def test_artifacts_and_frozen_sources(self):
        Draft202012Validator.check_schema(self.schema)
        for name, expected in b.build().items():
            self.assertEqual((b.ROOT / name).read_bytes(), expected)
        self.assertEqual(self.vectors["scope"], "synthetic_shape_identity_and_declaration_only_not_event_execution")
        self.assertEqual(self.vectors["schema_sha256"], sha256((b.ROOT / b.SCHEMA).read_bytes()).hexdigest())

    def test_legacy_aliases_are_finite_and_not_new_fallback_aliases(self):
        for candidate in ("candidate_c_no_independent_history_v1", "candidate_c_rederive_no_history_v1"):
            for carrier in ("no_persistent_carrier_v1", "carrier_not_applicable_v1"):
                row = self.transition(12)  # Synthetic nonpersistent C -> C.
                policy = row["request"]["history_policy"]
                policy["candidate"]["policy_id"] = candidate
                policy["carrier"]["policy_id"] = carrier
                self.validate("legacy_event_request", row["request"])
                self.validate("transition_record", row)
                if candidate != "candidate_c_rederive_no_history_v1" or carrier != "no_persistent_carrier_v1":
                    with self.assertRaises(ValidationError):
                        self.validate("event_request", row["request"])
                for subject in ("candidate", "carrier"):
                    bad = deepcopy(row)
                    bad["request"]["history_policy"][subject]["policy_id"] = "unknown-legacy-alias"
                    # Updating a digest cannot make this alias pass the local
                    # shape, let alone the deferred historical endpoint lookup.
                    for name, value in (("legacy_event_request", bad["request"]), ("transition_record", bad)):
                        with self.subTest(subject=subject, schema=name), self.assertRaises(ValidationError):
                            self.validate(name, value)

    def mixed_snapshot(self):
        """Complete synthetic wire envelope, NOT a coherent executed trajectory.

        Includes all five operation classes; endpoint/profile placeholders
        deliberately make no source-reconstruction or numerical admission claim.
        """
        snap = self.snapshot()
        for i, (index, version) in enumerate(((8, "grcv4-profile-migration-receipt-v2"),
                                             (0, "grcv4-profile-migration-receipt-v1"),
                                             (0, "grcv4-topology-event-receipt-v2"),
                                             (12, "grcv4-topology-event-receipt-v2"),
                                             (12, "grcv4-topology-event-receipt-v1"))):
            row = self.transition(index)
            row["request"]["operation_id"] = "synthetic-mixed-wire-" + str(i)
            if "migration" in version:
                req = row["request"]
                for k in ("source_graph_digest", "target_graph", "resource_transform", "metadata"):
                    del req[k]
                req.update(schema_version="grcv4-migration-request-v1", target_context_value={}, migration_policy=dict(
                    schema_version="grcv4-migration-policy-v1", policy_id="typed_bidirectional_profile_migration_v1",
                    resource_policy_id="identity_resource_transport_v1", target_readmission_policy_id="full_target_fail_closed_v1"))
                if version.endswith("v1"):
                    row["initializer_pair"] = None
                    req["history_policy"]["candidate"].update(policy_id="identity_candidate_history_v1",
                        disposition="exact_transport", information_loss="none", target_initializer_id=None)
            p = deepcopy(self.vectors["synthetic_receipts"][1]["payload"])
            p["schema_version"] = version
            if "migration" in version:
                del p["event_id"]
            p["initializer_pair_id"] = row["initializer_pair"]["initializer_pair_id"] if row["initializer_pair"] else None
            if version.endswith("v1"):
                del p["initializer_pair_id"]
            core = p["core"]
            core.update(operation_id=row["request"]["operation_id"], actual_charge_delta=0, information_losses=[])
            policy = row["request"]["history_policy"]
            core["history_bundle_digest"] = b.identity("grcv4-history-map-sha256", dict(
                schema_version="grcv4-history-bundle-identity-v1", history_bundle=policy))
            for subject, field in (("candidate", "W_A"), ("carrier", "Z_4")):
                p["history"][subject] = {k: policy[subject][k] for k in (
                    "subject", "disposition", "source_history_digest", "information_loss")}
                p["history"][subject]["target_history_digest"] = (
                    "grcv4-history-content-sha256:" + "0" * 64 if row["target"]["authoritative"][field] is not None else None)
                if policy[subject]["information_loss"] != "none":
                    core["information_losses"].append(policy[subject]["information_loss"])
            rid = b.identity("grc-receipt-sha256", p)
            commit = dict(schema_version="grcv4-commit-payload-v1", operation_id=core["operation_id"],
                          source_state_digest=core["source_state_digest"], target_state_digest=core["target_state_digest"],
                          emitted_receipt_ids=[rid], target_step_index=0, target_time=0)
            cid = b.identity("grc-commit-sha256", commit)
            row["commit_id"] = cid
            snap["transition_records"].append(row)
            snap["receipt_ledger"].append(dict(schema_version="grcv4-successful-receipt-envelope-v1",
                                              receipt_id=rid, commit_id=cid, identity_payload=p))
            snap["commit_records"].append(dict(commit_id=cid, payload=commit))
            snap["lifecycle"]["receipt_ids"].append(rid)
        snap["lifecycle_digest"] = b.identity("grcv4-lifecycle-sha256", snap["lifecycle"])
        return snap

    def test_mixed_version_wire_envelope_and_unknown_release(self):
        snap = self.mixed_snapshot()
        self.validate("snapshot_payload", snap)
        self.assertEqual(len(snap["transition_records"]), 5)
        self.assertEqual([r["initializer_pair"] is not None for r in snap["transition_records"]],
                         [True, False, True, False, False])
        for row, receipt, commit in zip(snap["transition_records"], snap["receipt_ledger"], snap["commit_records"]):
            self.assertEqual(row["commit_id"], commit["commit_id"])
            self.assertEqual(receipt["commit_id"], commit["commit_id"])
            self.assertEqual(receipt["receipt_id"], b.identity("grc-receipt-sha256", receipt["identity_payload"]))
            self.assertEqual(commit["commit_id"], b.identity("grc-commit-sha256", commit["payload"]))
        # The production codec must not admit even a full wire-shaped archive
        # under an unknown release. Passing schema is not release dispatch.
        with self.assertRaises(ValueError):
            snapshot_payload(snap)
        for i in range(5):
            bad = deepcopy(snap)
            row = bad["transition_records"][i]
            row["initializer_pair"] = None if row["initializer_pair"] else deepcopy(self.pair)
            with self.subTest(operation=i), self.assertRaises(ValidationError):
                self.validate("snapshot_payload", bad)

    def test_all_sixteen_policy_cases_against_independent_loss_table(self):
        candidate = {"AA": ("explicit_loss", "candidate_history_loss", True, b.INITIALIZER),
                     "AC": ("explicit_loss", "candidate_history_loss", True, None),
                     "CA": ("target_initializer", "none", False, b.INITIALIZER),
                     "CC": ("rederived", "none", False, None)}
        carrier = {(False, False): ("not_applicable", "none", False, None),
                   (False, True): ("target_initializer", "none", False, "canonical_zero_carrier_v1"),
                   (True, False): ("explicit_loss", "carrier_history_loss", True, None),
                   (True, True): ("whole_carrier_reset", "carrier_history_loss", True, "canonical_zero_carrier_v1")}
        seen = set()
        for row in self.vectors["policy_cases"]:
            key = (row["source_candidate"] + row["target_candidate"], row["source_persistent"], row["target_persistent"])
            self.assertNotIn(key, seen); seen.add(key)
            self.validate("history_policy", row["history_policy"])
            for s, expected in (("candidate", candidate[key[0]]), ("carrier", carrier[key[1:]])):
                p = row["history_policy"][s]
                self.assertEqual((p["disposition"], p["information_loss"], p["source_history_digest"] is not None,
                                  p["target_initializer_id"]), expected)
        self.assertEqual(len(seen), 16)

    def test_mislabeled_losses_initializer_and_inferred_identity_reject(self):
        for case in self.vectors["policy_cases"]:
            for subject in ("candidate", "carrier"):
                original = case["history_policy"]
                p = original[subject]
                mutations = {"policy_id": "unadmitted-identity-or-map", "disposition": "exact_transport",
                             "source_history_digest": None if p["source_history_digest"] else "grcv4-history-content-sha256:" + "0" * 64,
                             "information_loss": "none" if p["information_loss"] != "none" else subject + "_history_loss",
                             "target_initializer_id": "unadmitted_initializer"}
                for k, value in mutations.items():
                    bad = deepcopy(original); bad[subject][k] = value
                    with self.subTest(subject=subject, field=k), self.assertRaises(ValidationError):
                        self.validate("history_policy", bad)

    def test_receipts_pair_links_and_canonical_identities(self):
        for row in self.vectors["synthetic_receipts"]:
            pair = self.pair if row["payload"]["initializer_pair_id"] else None
            checked = self.receipt_links(row, pair)
            self.assertFalse(checked["producer_authenticated"] or checked["event_executed"])
            for key, value in (("initializer_pair_id", None if pair else self.pair["initializer_pair_id"]),
                               ("schema_version", "grcv4-topology-event-receipt-v1")):
                bad = deepcopy(row["payload"]); bad[key] = value
                with self.assertRaises(ValidationError):
                    self.validate("event_receipt_payload", bad)
        bad = deepcopy(self.vectors["synthetic_receipts"][0])
        bad["payload"]["core"]["information_losses"] = []
        bad["receipt_id"] = b.identity("grc-receipt-sha256", bad["payload"])
        bad["canonical_jcs_utf8"] = canonical_json_bytes(bad["payload"]).decode()
        with self.assertRaises(AssertionError):
            self.receipt_links(bad, self.pair)

    def test_role_pair_rehash_is_not_output_authentication(self):
        pair = deepcopy(self.pair)
        pair["payload"]["reset"] = deepcopy(pair["payload"]["current"])
        with self.assertRaises(ValueError):
            validate_initializer_payload("pair_record", pair)
        pair = deepcopy(self.pair)
        pair["payload"]["reset"]["payload"]["W_A_init"][0] = 123
        r = pair["payload"]["reset"]
        r["construction_id"] = b.identity("grcv4-a-reference-pass-construction-sha256", r["payload"])
        pair["initializer_pair_id"] = b.identity("grcv4-a-reference-pass-pair-sha256", pair["payload"])
        row = deepcopy(self.vectors["synthetic_receipts"][0])
        row["payload"]["initializer_pair_id"] = pair["initializer_pair_id"]
        row["receipt_id"] = b.identity("grc-receipt-sha256", row["payload"])
        row["canonical_jcs_utf8"] = canonical_json_bytes(row["payload"]).decode()
        self.assertFalse(self.receipt_links(row, pair)["producer_authenticated"])

    def test_event_transition_pair_presence(self):
        for index in range(16):
            row = self.transition(index)
            self.validate("transition_record", row)
            bad = deepcopy(row)
            bad["initializer_pair"] = None if row["initializer_pair"] else deepcopy(self.pair)
            with self.subTest(index=index), self.assertRaises(ValidationError):
                self.validate("transition_record", bad)
            for endpoint in ("source", "source_reset", "target", "target_reset"):
                for field in ("W_A", "Z_4"):
                    bad = deepcopy(row)
                    bad[endpoint]["authoritative"][field] = None if row[endpoint]["authoritative"][field] is not None else [0]
                    with self.subTest(index=index, endpoint=endpoint, field=field), self.assertRaises(ValidationError):
                        self.validate("transition_record", bad)

    def test_migration_pair_rule_is_not_widened_by_event_layout(self):
        for index in range(16):
            row = self.transition(index)
            request = row["request"]
            request["schema_version"] = "grcv4-migration-request-v1"
            del request["source_graph_digest"], request["target_graph"], request["resource_transform"]
            del request["metadata"]
            request["migration_policy"] = dict(schema_version="grcv4-migration-policy-v1",
                policy_id="typed_bidirectional_profile_migration_v1", resource_policy_id="identity_resource_transport_v1",
                target_readmission_policy_id="full_target_fail_closed_v1")
            request["target_context_value"] = {}
            case = self.vectors["policy_cases"][index]
            needs_pair = case["source_candidate"] == "C" and case["target_candidate"] == "A"
            row["initializer_pair"] = deepcopy(self.pair) if needs_pair else None
            # Wire shape only: original migration policies/admission remain
            # semantic checks and are not replaced by these event declarations.
            self.validate("transition_record", row)
            row["initializer_pair"] = None if needs_pair else deepcopy(self.pair)
            with self.subTest(index=index), self.assertRaises(ValidationError):
                self.validate("transition_record", row)

    def test_closed_records_and_no_caller_output_inputs(self):
        examples = {"event_request": self.request(), "event_receipt_payload": self.vectors["synthetic_receipts"][0]["payload"],
                    "transition_record": self.transition(), "snapshot_payload": self.snapshot()}
        for name, value in examples.items():
            self.validate(name, value)
            for key in value:
                bad = deepcopy(value); del bad[key]
                with self.subTest(schema=name, missing=key), self.assertRaises(ValidationError):
                    self.validate(name, bad)
            bad = deepcopy(value); bad["caller_W_or_flux"] = [1]
            with self.subTest(schema=name), self.assertRaises(ValidationError):
                self.validate(name, bad)

    def test_ijson_and_resource_wire_rejections(self):
        for value in (True, -1, math.inf, math.nan, -0.0, 2**53):
            bad = self.request(); bad["resource_transform"]["row_major_coefficients"][0] = value
            with self.subTest(value=value), self.assertRaises((ValueError, ValidationError)):
                self.validate("event_request", bad)
        with self.assertRaises(ValueError):
            decode_canonical_json('{"initializer_pair":null,"initializer_pair":null}')

    def test_old_release_layout_and_receipt_are_not_silently_extended(self):
        snap = self.snapshot()
        self.validate("snapshot_payload", snap)
        for release in ("specs/grc-v4-specification-release.json", "specs/grc-v4-a-initializer-release.json"):
            bad = deepcopy(snap); bad["specification_release_id"] = b.read(release)["release_id"]
            with self.assertRaises(ValidationError):
                self.validate("snapshot_payload", bad)
        for layout in ("pygrc-generic-migration-snapshot-v1", "pygrc-generic-initializer-migration-snapshot-v1"):
            bad = deepcopy(snap); bad["implementation_layout_id"] = layout
            with self.assertRaises(ValidationError):
                self.validate("snapshot_payload", bad)
        with self.assertRaises(ValueError):
            snapshot_payload(snap)  # A new hash-shaped release is not production admission.
        for row in self.vectors["synthetic_receipts"]:
            with self.assertRaises(ValueError):
                validate_payload("topology_event_receipt_identity_payload", row["payload"])
            with self.assertRaises(ValueError):
                validate_initializer_payload("receipt_envelope", dict(schema_version="grcv4-successful-receipt-envelope-v1",
                    receipt_id=row["receipt_id"], commit_id="grc-commit-sha256:" + "0" * 64, identity_payload=row["payload"]))

    def test_links_are_portable_and_resolve(self):
        for name in (b.SPEC, b.REVIEW):
            path = b.ROOT / name
            text = path.read_text()
            self.assertNotRegex(text, r"/home/|/tmp/|Downloads")
            targets = re.findall(r"\]\(([^)]+)\)", text) + re.findall(r"^\[[^\]]+\]: (\S+)", text, re.M)
            for target in targets:
                filename, _, anchor = target.partition("#")
                linked = path.parent / filename
                self.assertTrue(linked.is_file(), (name, target))
                if anchor:
                    headers = re.findall(r"^#+ (.+)$", linked.read_text(), re.M)
                    anchors = [re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headers]
                    self.assertIn(anchor, anchors)


if __name__ == "__main__":
    unittest.main()
