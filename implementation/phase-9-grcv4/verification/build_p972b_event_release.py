"""Joint contract package, not event/coordinate execution. No filesystem writes."""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import build_p972b_contract as b

SPEC = "specs/grc-v4-representation-transport-spec.md"
SCHEMA = "specs/grc-v4-representation-transport-schema.json"
VECTORS = "specs/grc-v4-representation-transport-vectors.json"
RELEASE = "specs/grc-v4-event-contract-release.json"
BUILDER = "implementation/phase-9-grcv4/verification/build_p972b_event_release.py"
TEST = "implementation/phase-9-grcv4/verification/test_p972b_event_release.py"
REVIEW = "implementation/phase-9-grcv4/tranche-7/P9-7.2b-PackageBinding.md"
DECODER = "src/pygrc/models/grc_v4_event_codec.py"
ASSETS = "src/pygrc/models/grc_v4_assets/"
POLICY = "grcv4-pure-representation-transport-v1"
LAYOUT = "pygrc-generic-coordinate-transport-snapshot-v1"
FALLBACK = Path(b.SCHEMA).name


def obj(properties):
    return dict(type="object", required=list(properties), additionalProperties=False, properties=properties)


def schema():
    base = b.read("specs/" + b.BASE)["$defs"]
    init = b.read("specs/" + b.INIT)["$defs"]
    fallback = b.read(b.SCHEMA)["$defs"]
    ref = b.ref
    d = {}
    for name, prefix in (("correspondence_id", "grcv4-coordinate-map-sha256"),
                         ("representation_id", "grcv4-representation-change-sha256")):
        d[name] = dict(type="string", pattern="^" + prefix + ":[0-9a-f]{64}$")
    vertex = {"type": ["string", "integer"]}
    edge = {"type": "string", "minLength": 1}
    d["correspondence_payload"] = obj(dict(
        schema_version={"const": "grcv4-coordinate-map-v1"}, policy_id={"const": POLICY},
        source_graph_digest=ref(b.BASE, "graph_id"), target_graph_digest=ref(b.BASE, "graph_id"),
        vertex_map=dict(type="array", items=obj(dict(source_vertex_id=vertex, target_vertex_id=vertex))),
        edge_map=dict(type="array", items=obj(dict(source_edge_id=edge, target_edge_id=edge,
                                                   orientation={"type": "integer", "enum": [-1, 1]})))))
    d["correspondence_record"] = obj(dict(correspondence_id=ref("", "correspondence_id"),
                                          payload=ref("", "correspondence_payload")))
    d["request"] = obj(dict(schema_version={"const": "grcv4-representation-transport-request-v1"},
        operation_id={"type": "string", "minLength": 1}, source_state_digest=ref(b.BASE, "state_id"),
        source_graph_digest=ref(b.BASE, "graph_id"), target_graph=ref(b.BASE, "serialized_graph_payload"),
        target_profile_id=ref(b.BASE, "grcv4_profile_id"), correspondence=ref("", "correspondence_record"),
        metadata={"type": "object"}))
    d["operation_identity_payload"] = obj(dict(schema_version={"const": "grcv4-representation-change-identity-v1"},
        policy_id={"const": POLICY}, source_state_digest=ref(b.BASE, "state_id"),
        source_graph_digest=ref(b.BASE, "graph_id"), target_graph_digest=ref(b.BASE, "graph_id"),
        target_profile_id=ref(b.BASE, "grcv4_profile_id"), correspondence_id=ref("", "correspondence_id")))
    core = b.imported(base["receipt_core"], b.BASE)
    for k in ("resource_transform_digest", "history_bundle_digest"):
        core["required"].remove(k); del core["properties"][k]
    for k in ("source_model_identity", "target_model_identity"):
        core["properties"][k] = ref(b.BASE, "grcv4_profile_id")
    core["properties"]["actual_charge_delta"] = {"const": 0}
    core["properties"]["information_losses"] = {"const": []}
    core["properties"]["parent_receipt_ids"]["maxItems"] = 1
    evaluation = obj({k: ref(b.BASE, "finite_number") for k in
                      ("target_charge", "admitted_charge", "residual")})
    d["charge_evidence"] = obj(dict(
        schema_version={"const": "grcv4-representation-charge-evidence-v1"},
        delta_semantics={"const": "exact_coordinate_action"},
        **{role: obj(dict(source=evaluation, target=evaluation)) for role in ("current", "reset")}))
    for subject in ("candidate", "carrier"):
        variants = []
        for present in (False, True):
            props = dict(subject={"const": subject}, information_loss={"const": "none"},
                         disposition={"const": "exact_transport" if present else
                                      "rederived" if subject == "candidate" else "not_applicable"})
            for k in ("source_history_digest", "target_history_digest"):
                props[k] = ref(b.BASE, "history_content_id") if present else {"type": "null"}
            variants.append({"allOf": [ref(b.BASE, "history_channel_receipt"), {"properties": props}]})
        d[subject + "_receipt"] = {"oneOf": variants}
    d["receipt_payload"] = obj(dict(schema_version={"const": "grcv4-representation-transport-receipt-v1"},
        core=core, representation_id=ref("", "representation_id"), correspondence_id=ref("", "correspondence_id"),
        charge=ref("", "charge_evidence"),
        history={"allOf": [ref(b.BASE, "history_bundle_receipt"), {"properties": {
            s: ref("", s + "_receipt") for s in ("candidate", "carrier")}}]}))
    row = b.imported(init["transition_record"], b.INIT)
    row["properties"]["request"] = ref("", "request")
    row["properties"]["initializer_pair"] = {"type": "null"}
    d["representation_transition"] = row
    d["transition_record"] = {"oneOf": [ref("", "representation_transition"), ref(FALLBACK, "transition_record")]}
    envelope = b.imported(fallback["receipt_envelope"], FALLBACK)
    envelope["properties"]["identity_payload"]["oneOf"].append(ref("", "receipt_payload"))
    d["receipt_envelope"] = envelope
    primary_envelope = deepcopy(envelope)
    primary_envelope["properties"]["identity_payload"] = ref("", "receipt_payload")
    commit = b.imported(base["commit_payload"], b.BASE)
    commit["properties"]["emitted_receipt_ids"].update(minItems=1, maxItems=1)
    d["operation_group"] = obj(dict(
        commit_record=obj(dict(commit_id=ref(b.BASE, "commit_id"), payload=commit)),
        receipts=dict(type="array", minItems=1, maxItems=1, items=primary_envelope)))
    snapshot = b.imported(fallback["snapshot_payload"], FALLBACK)
    snapshot["properties"]["implementation_layout_id"] = {"const": LAYOUT}
    snapshot["properties"]["transition_records"]["items"] = ref("", "transition_record")
    snapshot["properties"]["receipt_ledger"]["items"] = ref("", "receipt_envelope")
    snapshot["description"] = "Mixed-version wire shape only; explicit joint release lookup and whole-operation replay remain required."
    d["snapshot_payload"] = snapshot
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id":
            "https://github.com/urosj/graph-reflexive-coherence/" + SCHEMA,
            "title": "GRCV4 pure representation-transport binding", "$defs": d}


def vectors():
    source = dict(schema_version="grcv4-serialized-graph-v1", live_node_ids=["u", "v", "w"], oriented_edges=[
        dict(edge_id="e", tail_node_id="u", head_node_id="v"),
        dict(edge_id="parallel", tail_node_id="u", head_node_id="v"),
        dict(edge_id="loop", tail_node_id="w", head_node_id="w")])
    target = dict(schema_version="grcv4-serialized-graph-v1", live_node_ids=["z", "x", "y"], oriented_edges=[
        dict(edge_id="loop2", tail_node_id="x", head_node_id="x"),
        dict(edge_id="reverse", tail_node_id="z", head_node_id="y"),
        dict(edge_id="e2", tail_node_id="y", head_node_id="z")])
    payload = dict(schema_version="grcv4-coordinate-map-v1", policy_id=POLICY,
        source_graph_digest=b.identity("grc-graph-sha256", source), target_graph_digest=b.identity("grc-graph-sha256", target),
        vertex_map=[dict(source_vertex_id=s, target_vertex_id=t) for s, t in zip(("u", "v", "w"), ("y", "z", "x"))],
        edge_map=[dict(source_edge_id=s, target_edge_id=t, orientation=sign)
                  for s, t, sign in (("e", "e2", 1), ("parallel", "reverse", -1), ("loop", "loop2", -1))])
    record = dict(correspondence_id=b.identity("grcv4-coordinate-map-sha256", payload), payload=payload)
    fake = lambda prefix: prefix + ":" + "0" * 64
    request = dict(schema_version="grcv4-representation-transport-request-v1", operation_id="synthetic-coordinate-wire",
        source_state_digest=fake("grcv4-state-sha256"), source_graph_digest=payload["source_graph_digest"], target_graph=target,
        target_profile_id=fake("grcv4-profile-sha256"), correspondence=record, metadata={})
    operation = dict(schema_version="grcv4-representation-change-identity-v1", policy_id=POLICY,
        source_state_digest=request["source_state_digest"], source_graph_digest=payload["source_graph_digest"],
        target_graph_digest=payload["target_graph_digest"], target_profile_id=request["target_profile_id"],
        correspondence_id=record["correspondence_id"])
    core = deepcopy(b.read(b.VECTORS)["synthetic_receipts"][0]["payload"]["core"])
    for k in ("resource_transform_digest", "history_bundle_digest"):
        del core[k]
    core.update(operation_id=request["operation_id"], source_graph_digest=payload["source_graph_digest"],
                target_graph_digest=payload["target_graph_digest"], actual_charge_delta=0, information_losses=[])
    receipt = dict(schema_version="grcv4-representation-transport-receipt-v1", core=core,
        representation_id=b.identity("grcv4-representation-change-sha256", operation),
        correspondence_id=record["correspondence_id"], history=dict(schema_version="grcv4-history-bundle-receipt-v1"))
    # Synthetic charge-order witness, not an executed admitted model crossing.
    receipt["charge"] = dict(schema_version="grcv4-representation-charge-evidence-v1",
        delta_semantics="exact_coordinate_action",
        current=dict(source=dict(target_charge=1, admitted_charge=1, residual=0),
                     target=dict(target_charge=1, admitted_charge=1 + 2**-52, residual=2**-52)),
        reset=dict(source=dict(target_charge=1, admitted_charge=1, residual=0),
                   target=dict(target_charge=1, admitted_charge=1, residual=0)))
    for s in ("candidate", "carrier"):
        receipt["history"][s] = dict(subject=s, disposition="exact_transport", information_loss="none",
                                    source_history_digest=fake("grcv4-history-content-sha256"),
                                    target_history_digest=fake("grcv4-history-content-sha256"))
    cases = dict(source_graph=source, target_graph=target, correspondence_record=record, request=request,
                 operation_identity_payload=operation, receipt_payload=receipt)
    rid = b.identity("grc-receipt-sha256", receipt)
    commit = dict(schema_version="grcv4-commit-payload-v1", operation_id=core["operation_id"],
                  source_state_digest=core["source_state_digest"], target_state_digest=core["target_state_digest"],
                  emitted_receipt_ids=[rid], target_step_index=0, target_time=0)
    cid = b.identity("grc-commit-sha256", commit)
    cases["operation_group"] = dict(commit_record=dict(commit_id=cid, payload=commit), receipts=[dict(
        schema_version="grcv4-successful-receipt-envelope-v1", receipt_id=rid, commit_id=cid, identity_payload=receipt)])
    identities = [("correspondence_record/payload", "grcv4-coordinate-map-sha256"),
                  ("operation_identity_payload", "grcv4-representation-change-sha256"),
                  ("receipt_payload", "grc-receipt-sha256"),
                  ("operation_group/commit_record/payload", "grc-commit-sha256")]
    rows = []
    for pointer, prefix in identities:
        value = cases
        for key in pointer.split("/"):
            value = value[key]
        rows.append(dict(pointer=pointer, canonical_jcs_utf8=b.canonical_json_bytes(value).decode(),
                         identity_prefix=prefix, expected_identifier=b.identity(prefix, value)))
    return dict(schema_version="grcv4-representation-wire-vectors-v1",
                scope="synthetic_wire_and_correspondence_declaration_not_transport_execution",
                **cases, canonical_vectors=rows)


def build():
    # The accepted fallback shapes and examples retain their semantics.
    for name, expected in b.build().items():
        if (b.ROOT / name).read_bytes() != expected:
            raise ValueError("fallback artifacts stale: " + name)
    original = json.loads(subprocess.check_output(["git", "show", "8594d9d:" + b.VECTORS], cwd=b.ROOT))
    live = b.read(b.VECTORS)
    for key in ("pair_record", "policy_cases", "synthetic_receipts"):
        if original[key] != live[key]:
            raise ValueError("accepted fallback example changed: " + key)
    if (b.ROOT / b.SCHEMA).read_bytes() != subprocess.check_output(["git", "show", "8594d9d:" + b.SCHEMA], cwd=b.ROOT):
        raise ValueError("accepted fallback schema changed")
    data = lambda x: (json.dumps(x, indent=2) + "\n").encode()
    outputs = {SCHEMA: data(schema()), VECTORS: data(vectors())}
    sources = set(b.FROZEN) | {b.SCHEMA, b.VECTORS, b.SPEC, b.REVIEW, SPEC, SCHEMA, VECTORS, BUILDER, TEST, REVIEW}
    raw = lambda name: outputs[name] if name in outputs else (b.ROOT / name).read_bytes()
    init = b.read("specs/grc-v4-a-initializer-release.json")
    policy = b.read("specs/" + b.INIT)["$defs"]["static_policy"]["const"]
    payload = dict(schema_version="grcv4-event-contract-release-identity-v1",
        predecessor_release_id=init["release_id"],
        accepted_scope_commit=subprocess.check_output(["git", "rev-parse", "8594d9d"], cwd=b.ROOT, text=True).strip(),
        artifact_bindings=[dict(path=n, sha256=sha256(raw(n)).hexdigest()) for n in sorted(sources)],
        initializer_static_policy_digest=b.identity("grcv4-a-initializer-policy-sha256", policy),
        snapshot_layout_ids=[b.LAYOUT, LAYOUT],
        receipt_schemas=["grcv4-topology-event-receipt-v2", "grcv4-representation-transport-receipt-v1"],
        representation_policy_id=POLICY)
    manifest = dict(schema_version="grcv4-event-contract-release-v1",
        release_id=b.identity("grcv4-spec-release-sha256", payload), release_identity_payload=payload,
        claim_ceiling="Contract wire/declaration admission only; no model lifecycle execution, covariance acceptance or new G2/G3 support.")
    outputs[RELEASE] = data(manifest)
    for name in (b.SCHEMA, SCHEMA, RELEASE):
        outputs[ASSETS + Path(name).name] = raw(name) if name != RELEASE else outputs[RELEASE]
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    for name, expected in build().items():
        if (b.ROOT / name).read_bytes() != expected:
            raise ValueError("joint contract package drift: " + name)
    print("P972B_EVENT_PACKAGE_PASS runtime_executed=false")
