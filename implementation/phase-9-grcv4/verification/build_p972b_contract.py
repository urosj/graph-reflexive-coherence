"""Deterministic event wire examples; no producer, event, release or acceptance.

Prints/checks derived artifacts only. Callers apply changes with apply_patch.
"""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from pygrc.models.grc_v4_codec import canonical_json_bytes

BASE = "grc-v4-contract-schema.json"
INIT = "grc-v4-a-initializer-schema.json"
SCHEMA = "specs/grc-v4-topology-event-schema.json"
VECTORS = "specs/grc-v4-topology-event-vectors.json"
SPEC = "specs/grc-v4-topology-event-spec.md"
REVIEW = "implementation/phase-9-grcv4/tranche-7/P9-7.2b-ContractExtension.md"
LAYOUT = "pygrc-generic-topology-event-snapshot-v1"
HISTORY = "candidate_a_target_reference_pass_initialization_log_history_v1"
INITIALIZER = "grcv4-a-target-reference-pass-v1"
FROZEN = (
    "specs/" + BASE, "specs/" + INIT,
    "specs/grc-v4-a-initializer-vectors.json", "specs/grc-v4-a-initializer-spec.md",
    "specs/grc-v4-a-initializer-release.json", "specs/grc-v4-specification-release.json",
    "implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md",
    "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    "implementation/investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassAuthority.json",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportProvenanceSupplement.json",
)


def read(name):
    return json.loads((ROOT / name).read_text())


def identity(prefix, value):
    return prefix + ":" + sha256(canonical_json_bytes(value)).hexdigest()


def ref(file, name):
    return {"$ref": file + "#/$defs/" + name}


def imported(value, file):
    """Copied shapes retain their original reference resolution base."""
    if isinstance(value, list):
        return [imported(x, file) for x in value]
    if isinstance(value, dict):
        return {k: file + v if k == "$ref" and v.startswith("#") else imported(v, file)
                for k, v in value.items()}
    return value


def policies(a, b, old, new, source_digest):
    def channel(subject, policy, disposition, present, initializer=None, loss="none"):
        return dict(schema_version="grcv4-history-channel-policy-v1", subject=subject,
                    policy_id=policy, disposition=disposition,
                    source_history_digest=source_digest if present else None,
                    target_initializer_id=initializer, information_loss=loss)
    if b == "A":
        candidate = channel("candidate", HISTORY if a == "C" else "candidate_a_event_loss_reference_pass_v1",
                            "target_initializer" if a == "C" else "explicit_loss", a == "A",
                            INITIALIZER, "none" if a == "C" else "candidate_history_loss")
    else:
        candidate = channel("candidate", "candidate_c_rederive_no_history_v1" if a == "C" else "archive_drop_candidate_history_v1",
                            "rederived" if a == "C" else "explicit_loss", a == "A",
                            loss="none" if a == "C" else "candidate_history_loss")
    if old and new:
        carrier = channel("carrier", "event_loss_and_zero_target_carrier_v1", "whole_carrier_reset", True,
                          "canonical_zero_carrier_v1", "carrier_history_loss")
    elif old:
        carrier = channel("carrier", "archive_drop_carrier_history_v1", "explicit_loss", True,
                          loss="carrier_history_loss")
    elif new:
        carrier = channel("carrier", "canonical_zero_carrier_initialization_v1", "target_initializer", False,
                          "canonical_zero_carrier_v1")
    else:
        carrier = channel("carrier", "no_persistent_carrier_v1", "not_applicable", False)
    return dict(schema_version="grcv4-history-bundle-policy-v1", candidate=candidate, carrier=carrier)


def schema():
    base, init = read("specs/" + BASE)["$defs"], read("specs/" + INIT)["$defs"]
    defs = {}
    cases = [policies(a, b, old, new, "present") for a in "AC" for b in "AC"
             for old in (False, True) for new in (False, True)]
    for subject in ("candidate", "carrier"):
        variants = []
        for bundle in cases:
            props = {k: ref(BASE, "history_content_id") if k == "source_history_digest" and v == "present"
                     else {"const": v} for k, v in bundle[subject].items()}
            variant = {"allOf": [ref(BASE, "history_channel_policy"), {"properties": props}]}
            if variant not in variants:
                variants.append(variant)
        defs[subject + "_policy"] = {"oneOf": variants}
    defs["history_policy"] = {"allOf": [ref(BASE, "history_bundle_policy"), {"properties": {
        s: ref("", s + "_policy") for s in ("candidate", "carrier")}}]}
    defs["event_request"] = {"allOf": [ref(BASE, "mapped_topology_event_request"), {
        "properties": {"history_policy": ref("", "history_policy")}}]}
    for subject in ("candidate", "carrier"):
        variants = []
        for a in "AC":
            for b in "AC":
                for old in (False, True):
                    for new in (False, True):
                        policy = policies(a, b, old, new, "present")[subject]
                        target_present = b == "A" if subject == "candidate" else new
                        props = {k: ref(BASE, "history_content_id") if k == "source_history_digest" and v == "present"
                                 else {"const": v} for k, v in policy.items()
                                 if k in ("subject", "disposition", "source_history_digest", "information_loss")}
                        props["target_history_digest"] = ref(BASE, "history_content_id") if target_present else {"type": "null"}
                        variant = {"allOf": [ref(BASE, "history_channel_receipt"), {"properties": props}]}
                        if variant not in variants:
                            variants.append(variant)
        defs[subject + "_receipt"] = {"oneOf": variants}
    receipt = imported(base["topology_event_receipt_identity_payload"], BASE)
    receipt["required"].append("initializer_pair_id")
    receipt["properties"]["schema_version"] = {"const": "grcv4-topology-event-receipt-v2"}
    receipt["properties"]["initializer_pair_id"] = {"oneOf": [
        {"type": "null"}, {"type": "string", "pattern": "^grcv4-a-reference-pass-pair-sha256:[0-9a-f]{64}$"}]}
    receipt["properties"]["history"] = {"allOf": [ref(BASE, "history_bundle_receipt"), {"properties": {
        s: ref("", s + "_receipt") for s in ("candidate", "carrier")}}]}
    receipt["allOf"] = [{"if": {"properties": {"history": {"properties": {"candidate": {"properties": {
        "target_history_digest": {"type": "null"}}}}}}},
        "then": {"properties": {"initializer_pair_id": {"type": "null"}}},
        "else": {"properties": {"initializer_pair_id": {"type": "string"}}}}]
    receipt["properties"]["core"] = {"allOf": [ref(BASE, "receipt_core"), {"properties": {
        "source_model_identity": ref(BASE, "grcv4_profile_id"),
        "target_model_identity": ref(BASE, "grcv4_profile_id"),
        "information_losses": {"enum": [[], ["candidate_history_loss"], ["carrier_history_loss"],
                                         ["candidate_history_loss", "carrier_history_loss"]]}}}]}
    receipt["description"] = "Pair presence, channel losses and endpoint linkage require semantic validation; this is not execution evidence."
    defs["event_receipt_payload"] = receipt
    transition = imported(init["transition_record"], INIT)
    event_condition = {"properties": {"request": {"properties": {"schema_version": {
        "const": "grcv4-mapped-topology-event-request-v1"}}}}}
    a_condition = {"properties": {"request": {"properties": {"history_policy": {"properties": {
        "candidate": {"properties": {"target_initializer_id": {"const": INITIALIZER}}}}}}}}}
    # Legacy v1 C_OS rows retain their original request/policy aliases. They
    # must be matched to original v1 receipts during semantic archive replay.
    legacy = {"allOf": [ref(BASE, "mapped_topology_event_request"), {"properties": {
        "history_policy": {"properties": {
            "candidate": {"properties": {"policy_id": {"enum": ["candidate_c_no_independent_history_v1",
                                                                     "candidate_c_rederive_no_history_v1"]},
                                           "disposition": {"const": "rederived"},
                                           "source_history_digest": {"type": "null"},
                                           "target_initializer_id": {"type": "null"},
                                           "information_loss": {"const": "none"}}},
            "carrier": {"properties": {"policy_id": {"enum": ["no_persistent_carrier_v1", "carrier_not_applicable_v1"]},
                                         "disposition": {"const": "not_applicable"}}}}}}}]}
    defs["legacy_event_request"] = legacy
    transition["allOf"] = [{"if": event_condition, "then": {
        "properties": {"request": {"anyOf": [ref("", "event_request"), ref("", "legacy_event_request")]}},
        "allOf": [{"if": a_condition,
                   "then": {"properties": {"initializer_pair": ref(INIT, "pair_record")}},
                   "else": {"properties": {"initializer_pair": {"type": "null"}}}}]}}]
    # Match channel population to archived state shapes. Profile identities,
    # coordinate lengths and actual history digests still require replay.
    def at(keys, value):
        for key in reversed(keys):
            value = {"properties": {key: value}}
        return value
    for subject, field in (("candidate", "W_A"), ("carrier", "Z_4")):
        source_absent = at(["request", "history_policy", subject, "source_history_digest"], {"type": "null"})
        target_absent = at(["request", "history_policy", subject, "target_initializer_id"], {"type": "null"})
        for endpoint, absent in (("source", source_absent), ("target", target_absent)):
            coordinate_rules = lambda kind: {"allOf": [at([row, "authoritative", field], {"type": kind})
                                                       for row in (endpoint, endpoint + "_reset")]}
            transition["allOf"][0]["then"]["allOf"].append(
                {"if": absent, "then": coordinate_rules("null"), "else": coordinate_rules("array")})
    c_to_a = {"allOf": [at(["source", "authoritative", "W_A"], {"type": "null"}),
                         at(["target", "authoritative", "W_A"], {"type": "array"})]}
    transition["allOf"][0]["else"] = {
        "if": c_to_a, "then": {"properties": {"initializer_pair": ref(INIT, "pair_record")}},
        "else": {"properties": {"initializer_pair": {"type": "null"}}}}
    defs["transition_record"] = transition
    envelope = imported(init["receipt_envelope"], INIT)
    envelope["properties"]["identity_payload"]["oneOf"].append(ref("", "event_receipt_payload"))
    defs["receipt_envelope"] = envelope
    snapshot = imported(init["snapshot_payload"], INIT)
    snapshot["properties"]["implementation_layout_id"] = {"const": LAYOUT}
    snapshot["properties"]["specification_release_id"]["not"] = {"enum": [
        read("specs/grc-v4-specification-release.json")["release_id"],
        read("specs/grc-v4-a-initializer-release.json")["release_id"]]}
    snapshot["properties"]["receipt_ledger"]["items"] = ref("", "receipt_envelope")
    snapshot["properties"]["transition_records"]["items"] = ref("", "transition_record")
    snapshot["description"] = "New event layout only. Unknown releases are not admission; legacy rows retain version-specific semantics."
    defs["snapshot_payload"] = snapshot
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://github.com/urosj/graph-reflexive-coherence/" + SCHEMA,
            "title": "GRCV4 topology-event fallback binding", "$defs": defs}


def build():
    for name in FROZEN:
        if (ROOT / name).read_bytes() != subprocess.check_output(["git", "show", "ed61c1d:" + name], cwd=ROOT):
            raise ValueError("accepted source changed: " + name)
    inherited = read("specs/grc-v4-a-initializer-vectors.json")
    pair = inherited["pair_record"]
    digest = "grcv4-history-content-sha256:" + "0" * 64
    cases = [dict(source_candidate=a, target_candidate=b, source_persistent=old, target_persistent=new,
                  history_policy=policies(a, b, old, new, digest))
             for a in "AC" for b in "AC" for old in (False, True) for new in (False, True)]
    receipts = []
    for a, b, old, new in [("A", "A", True, True), ("C", "A", False, True), ("A", "C", True, False)]:
        policy = policies(a, b, old, new, digest)
        payload = deepcopy(inherited["synthetic_receipt_record"]["payload"])
        payload["schema_version"] = "grcv4-topology-event-receipt-v2"
        payload["event_id"] = "grc-event-sha256:" + "0" * 64
        payload["core"]["operation_id"] = "synthetic-event-wire-not-an-execution"
        payload["core"]["actual_charge_delta"] = 0.5
        payload["core"]["history_bundle_digest"] = identity("grcv4-history-map-sha256", dict(
            schema_version="grcv4-history-bundle-identity-v1", history_bundle=policy))
        payload["core"]["information_losses"] = [policy[s]["information_loss"] for s in ("candidate", "carrier")
                                                  if policy[s]["information_loss"] != "none"]
        for s, present in (("candidate", b == "A"), ("carrier", new)):
            payload["history"][s] = {k: policy[s][k] for k in (
                "subject", "disposition", "source_history_digest", "information_loss")}
            payload["history"][s]["target_history_digest"] = digest if present else None
        payload["initializer_pair_id"] = pair["initializer_pair_id"] if b == "A" else None
        core = payload["core"]
        event = dict(schema_version="grcv4-mapped-topology-event-identity-v1",
                     **{k: core[k] for k in ("source_state_digest", "source_graph_digest", "target_graph_digest",
                                             "resource_transform_digest", "history_bundle_digest")},
                     target_profile_id=core["target_model_identity"])
        payload["event_id"] = identity("grc-event-sha256", event)
        receipts.append(dict(history_policy=policy, event_identity_payload=event, payload=payload,
                             receipt_id=identity("grc-receipt-sha256", payload),
                             canonical_jcs_utf8=canonical_json_bytes(payload).decode()))
    doc = schema()
    data = lambda x: (json.dumps(x, indent=2) + "\n").encode()
    vectors = dict(schema_version="grcv4-topology-event-wire-vectors-v1",
                   scope="synthetic_shape_identity_and_declaration_only_not_event_execution",
                   source_bindings={n: sha256((ROOT / n).read_bytes()).hexdigest()
                                    for n in sorted((*FROZEN, SPEC, REVIEW))},
                   schema_sha256=sha256(data(doc)).hexdigest(),
                   pair_record=pair, policy_cases=cases, synthetic_receipts=receipts)
    return {SCHEMA: data(doc), VECTORS: data(vectors)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    for name, expected in build().items():
        if (ROOT / name).read_bytes() != expected:
            raise ValueError("event contract artifact drift: " + name)
    print("P972B_EVENT_CONTRACT_ARTIFACTS_PASS runtime_executed=false released=false")
