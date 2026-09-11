"""Spec wire/declaration pressure only; never authenticates an initializer output.

No current solve, producer, migration, numerical campaign or release generation.
The supplement remains unimplemented until its separate runtime follow-through.
"""

from copy import deepcopy
from hashlib import sha256
import json
import math
import sys
import unittest

import verify_p972a_proposal as v

sys.path.insert(0, str(v.p.ROOT / "src"))

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
from pygrc.models.grc_v4_codec import canonical_json_bytes, decode_canonical_json, snapshot_payload, validate_payload
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_profile import resolve_profile


def identity(prefix, payload):
    return prefix + ":" + sha256(canonical_json_bytes(payload)).hexdigest()


def rehash(pair):
    for role in ("current", "reset"):
        row = pair["payload"][role]
        row["construction_id"] = identity("grcv4-a-reference-pass-construction-sha256", row["payload"])
    pair["initializer_pair_id"] = identity("grcv4-a-reference-pass-pair-sha256", pair["payload"])


class SpecificationPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((v.p.ROOT / v.SUPPLEMENT_SCHEMA).read_text())
        cls.base = json.loads((v.p.ROOT / "specs/grc-v4-contract-schema.json").read_text())
        cls.vectors = json.loads((v.p.ROOT / v.SUPPLEMENT_VECTORS).read_text())
        cls.registry = Registry().with_resources(
            (doc["$id"], Resource.from_contents(doc)) for doc in (cls.base, cls.schema))
        Draft202012Validator.check_schema(cls.schema)
        cls.policy = cls.schema["$defs"]["static_policy"]["const"]

    def validate(self, name, value):
        canonical_json_bytes(value)  # I-JSON is a separate prerequisite to JSON Schema.
        Draft202012Validator(
            {"$ref": self.schema["$id"] + "#/$defs/" + name}, registry=self.registry).validate(value)

    def pair(self):
        return deepcopy(self.vectors["pair_record"])

    def declaration(self, pair):
        """Check recoverable declarations/IDs, NOT recomputation or final admission."""
        self.validate("pair_record", pair)
        for role in ("current", "reset"):
            record = pair["payload"][role]
            payload = record["payload"]
            self.assertEqual(record["construction_id"], identity(
                "grcv4-a-reference-pass-construction-sha256", payload))
            ref = GRCV4ReferenceGeometry.from_payload(payload["target_reference"])
            backend = CandidateADifferentialReference.from_payload(payload["differential_reference"])
            self.assertEqual(ref.graph, backend.graph)
            self.assertEqual(ref.profile.params_resolved.candidate.descriptor_backend_id, backend.identity)
            self.assertEqual(ref.edge_weights, backend.reference_weights)
            nv, ne = len(ref.graph.live_node_ids), len(ref.graph.live_edge_ids)
            self.assertEqual(len(payload["target_C"]), nv)
            self.assertEqual(len(payload["W_A_init"]), ne)
            self.assertTrue(all(x >= ref.profile.params_resolved.candidate.W_floor for x in payload["W_A_init"]))
            if payload["derived"] is not None:
                self.assertEqual(len(payload["derived"]["W_base"]), ne)
                self.assertEqual(len(payload["derived"]["Phi_base"]), nv)
                self.assertEqual(len(payload["derived"]["J_ref"]), ne)
        current, reset = (pair["payload"][r]["payload"] for r in ("current", "reset"))
        for name in ("policy", "target_reference", "differential_reference"):
            # Initial constant-zero context: the complete fixed inputs coincide.
            self.assertEqual(current[name], reset[name])
        self.assertEqual(pair["initializer_pair_id"], identity(
            "grcv4-a-reference-pass-pair-sha256", pair["payload"]))
        return {"declaration_valid": True, "construction_authenticated": False,
                "final_target_admitted": False, "migration_executed": False}

    def test_published_wire_vectors_and_claim_ceiling(self):
        self.assertEqual(self.vectors["scope"],
                         "canonical_shape_and_identity_only_not_producer_or_migration_execution")
        self.assertEqual(self.vectors["policy_id"], identity("grcv4-a-initializer-policy-sha256", self.policy))
        result = self.declaration(self.pair())
        self.assertTrue(result["declaration_valid"])
        self.assertFalse(any(result[k] for k in result if k != "declaration_valid"))
        receipt = self.vectors["synthetic_receipt_record"]
        self.validate("migration_receipt_payload", receipt["payload"])
        self.assertEqual(receipt["receipt_id"], identity("grc-receipt-sha256", receipt["payload"]))
        self.assertEqual(receipt["payload"]["initializer_pair_id"], self.pair()["initializer_pair_id"])
        self.assertEqual(decode_canonical_json(canonical_json_bytes(self.pair())), self.pair())
        for row in self.vectors["canonical_vectors"]:
            payload = self.vectors
            for key in row["payload_pointer"].split("/")[1:]:
                payload = payload[key]
            self.assertEqual(row["canonical_jcs_utf8"].encode(), canonical_json_bytes(payload))
            self.assertEqual(row["expected_identifier"], identity(row["identity_prefix"], payload))

    def test_directional_candidate_history_and_receipt_shape(self):
        policy = dict(schema_version="grcv4-history-channel-policy-v1", subject="candidate",
                      policy_id=self.policy["history_policy_id"], disposition="target_initializer",
                      source_history_digest=None, target_initializer_id=self.policy["policy_id"], information_loss="none")
        self.validate("candidate_history_policy", policy)
        for key, bad_value in (("information_loss", "candidate_history_loss"),
                               ("source_history_digest", "grcv4-history-content-sha256:" + "0" * 64),
                               ("target_initializer_id", self.pair()["initializer_pair_id"])):
            bad = deepcopy(policy); bad[key] = bad_value
            with self.subTest(field=key), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.validate("candidate_history_policy", bad)
        receipt = self.vectors["synthetic_receipt_record"]["payload"]
        for key, bad_value in (("actual_charge_delta", 1), ("information_losses", ["candidate_history_loss"]),
                               ("target_model_identity", "grc9v4-model-sha256:" + "0" * 64)):
            bad = deepcopy(receipt); bad["core"][key] = bad_value
            with self.subTest(field=key), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.validate("migration_receipt_payload", bad)

    def test_closed_records_reject_missing_extra_and_recursive_output_fields(self):
        sample = self.pair()["payload"]["current"]["payload"]
        examples = {"construction_payload": sample, "static_policy": self.policy,
                    "pair_record": self.pair(), "pair_payload": self.pair()["payload"],
                    "target_reference": sample["target_reference"],
                    "differential_reference": sample["differential_reference"],
                    "migration_receipt_payload": self.vectors["synthetic_receipt_record"]["payload"]}
        for name, value in examples.items():
            for key in value:
                bad = deepcopy(value); del bad[key]
                with self.subTest(schema=name, missing=key), self.assertRaises((ValidationError, ValueError, AssertionError)):
                    self.validate(name, bad)
            bad = deepcopy(value); bad["unknown_load_bearing_field"] = 1
            with self.subTest(schema=name, extra=True), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.validate(name, bad)
        for key in ("source_W", "source_Z", "reference_current", "descriptors", "construction_id"):
            bad = deepcopy(sample); bad[key] = []
            with self.subTest(forbidden_input=key), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.validate("construction_payload", bad)

    def test_unknown_and_old_recipe_identities_are_not_admitted(self):
        for key in self.policy:
            bad = deepcopy(self.policy); bad[key] = 2 if key == "passes" else "unknown_or_old_recipe"
            with self.subTest(key=key), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.validate("static_policy", bad)
        for value in (False, -0.0, math.inf, math.nan, 2**53):
            bad = self.pair(); bad["payload"]["current"]["payload"]["target_C"][0] = value
            with self.subTest(value=value), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.declaration(bad)
        with self.assertRaises((ValidationError, ValueError, AssertionError)):
            decode_canonical_json('{"role":"current","role":"reset"}')

    def test_identity_and_recipe_mutations_reject_even_after_record_rehash(self):
        for mutate in (
            lambda x: x["target_C"].append(0),
            lambda x: x["W_A_init"].clear(),
            lambda x: x["W_A_init"].__setitem__(0, 0),
            lambda x: x["differential_reference"]["positions"].pop(),
            lambda x: x["differential_reference"]["reference_weights"].update(extra=1),
            lambda x: x["differential_reference"].update(regularization=2),
            lambda x: x["target_reference"]["profile"]["identity_payload"].update(params_hash="grcv4-params-sha256:" + "0" * 64),
            lambda x: x["target_reference"]["profile"]["params_resolved"]["lifecycle"].update(history_policy_id="candidate_a_explicit_reference_initialization_log_history_v1"),
            lambda x: x["target_reference"]["context"]["value"].update(U=1),
            lambda x: x["target_reference"]["graph"]["oriented_edges"][0].update(head_node_id="missing"),
        ):
            bad = self.pair(); mutate(bad["payload"]["current"]["payload"]); rehash(bad)
            with self.subTest(mutation=mutate), self.assertRaises((ValidationError, ValueError, AssertionError)):
                self.declaration(bad)

    def test_roles_and_static_before_output_identity(self):
        pair = self.pair(); current, reset = (pair["payload"][r] for r in ("current", "reset"))
        self.assertNotEqual(current["construction_id"], reset["construction_id"])
        for name in ("target_C", "W_A_init", "target_reference", "differential_reference"):
            self.assertEqual(current["payload"][name], reset["payload"][name])
        wrong = self.pair(); wrong["payload"]["reset"] = deepcopy(wrong["payload"]["current"]); rehash(wrong)
        with self.assertRaises((ValidationError, ValueError, AssertionError)):
            self.declaration(wrong)
        changed = self.pair(); changed["payload"]["reset"]["payload"]["target_C"][0] = 0.25; rehash(changed)
        # Changed C changes invocation/pair IDs, never the pre-existing profile.
        self.assertNotEqual(changed["initializer_pair_id"], pair["initializer_pair_id"])
        self.assertEqual(changed["payload"]["reset"]["payload"]["target_reference"], reset["payload"]["target_reference"])
        self.assertFalse(self.declaration(changed)["construction_authenticated"])

    def test_derived_outputs_require_future_recomputation_not_shape_promotion(self):
        pair = self.pair()
        for role in ("current", "reset"):
            pair["payload"][role]["payload"]["derived"] = dict(W_base=[1], Phi_base=[0, 0], J_ref=[0])
        rehash(pair)
        self.assertFalse(self.declaration(pair)["construction_authenticated"])
        pair["payload"]["reset"]["payload"]["derived"]["J_ref"] = [123]
        rehash(pair)
        # Deliberately wrong arithmetic can satisfy shapes/IDs: producer checks are forward work.
        self.assertFalse(self.declaration(pair)["construction_authenticated"])
        pair["payload"]["reset"]["payload"]["derived"]["J_ref"].append(0); rehash(pair)
        with self.assertRaises(AssertionError):
            self.declaration(pair)

    def test_old_release_receipt_rejects_new_shape_and_policy_change_changes_profile(self):
        with self.assertRaises((ValidationError, ValueError, AssertionError)):
            validate_payload("profile_migration_receipt_identity_payload", self.vectors["synthetic_receipt_record"]["payload"])
        original = self.pair()["payload"]["current"]["payload"]["target_reference"]["profile"]
        params = deepcopy(original["params_resolved"]); ip = deepcopy(original["identity_payload"])
        params["lifecycle"]["history_policy_id"] = "candidate_a_explicit_reference_initialization_log_history_v1"
        ip["params_hash"] = identity("grcv4-params-sha256", params)
        old = resolve_profile(params, ip)
        self.assertNotEqual(old.complete_profile_id, original["complete_profile_id"])
        with self.assertRaises((ValidationError, ValueError, AssertionError)):
            self.validate("profile", old.to_payload())

    def test_snapshot_shape_is_closed_but_unknown_release_is_not_admission(self):
        # Synthetic wire envelope, not an initialized or committed live state.
        ref = self.pair()["payload"]["current"]["payload"]["target_reference"]
        digest = lambda prefix: prefix + ":" + "0" * 64
        state = dict(schema_version="grcv4-scientific-state-v1", active_model_identity=ref["profile"]["complete_profile_id"],
                     graph_digest=digest("grc-graph-sha256"), orientation_identity="synthetic-wire-order",
                     step_index=0, time=0, authoritative=dict(C=[0, 0], W_A=[1], Z_4=None),
                     reset_digest=digest("grcv4-reset-sha256"), Q_target=0,
                     context_contract_id="constant_zero_context_v1", context_value_digest=None)
        reset = {k: deepcopy(state[k]) for k in ("active_model_identity", "graph_digest", "orientation_identity",
                                                "authoritative", "Q_target", "context_contract_id")}
        reset["schema_version"] = "grcv4-reset-baseline-v1"
        snapshot = dict(schema_version="grcv4-snapshot-v1", model_family="GRCV4",
                        implementation_layout_id="pygrc-generic-initializer-migration-snapshot-v1",
                        receipt_parent_policy_id="grcv4-previous-successful-primary-v1",
                        specification_release_id=digest("grcv4-spec-release-sha256"), reference=ref,
                        scientific_state=state, scientific_state_digest=digest("grcv4-state-sha256"),
                        reset=reset, reset_digest=digest("grcv4-reset-sha256"), receipt_ledger=[], commit_records=[],
                        lifecycle=dict(schema_version="grcv4-lifecycle-envelope-v1",
                                       scientific_state_digest=digest("grcv4-state-sha256"), receipt_ids=[]),
                        lifecycle_digest=digest("grcv4-lifecycle-sha256"), reference_registry=[ref],
                        differential_reference_registry=[], transition_records=[])
        self.validate("snapshot_payload", snapshot)
        # Old production codec rejects the new layout; hash syntax is not release authority.
        with self.assertRaises(ValueError):
            snapshot_payload(snapshot)
        for key in snapshot:
            bad = deepcopy(snapshot); del bad[key]
            with self.subTest(missing=key), self.assertRaises(ValidationError):
                self.validate("snapshot_payload", bad)
        for key, value in (("implementation_layout_id", "pygrc-generic-migration-snapshot-v1"),
                           ("specification_release_id", v.p.ABUNDANCE_RELEASE_ID),
                           ("injected_output_registry", [])):
            bad = deepcopy(snapshot); bad[key] = value
            with self.subTest(field=key), self.assertRaises(ValidationError):
                self.validate("snapshot_payload", bad)


if __name__ == "__main__":
    unittest.main()
