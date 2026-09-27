"""Explicit P9-7.2b contract package decoder, not a model lifecycle dispatcher.

No model construction, numerical solver, resource/history transport or mutable
registry. Older codec/layout semantics remain unchanged. Package lookup uses
installed resources only and schema resolution is offline.
"""

import json
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from importlib import resources
from typing import Any, cast

from . import grc_v4_codec as base

EVENT_RELEASE_ID = "grcv4-spec-release-sha256:a6861c38271f3f4ea41fae35807c399255353c384c44a9455f334556df6cdec8"
_MANIFEST_SHA256 = "e1ae563880b03cab512e5481f2db556032853bf8d558eeed689ec09e577ea699"
EVENT_LAYOUT = "pygrc-generic-topology-event-snapshot-v1"
REPRESENTATION_LAYOUT = "pygrc-generic-coordinate-transport-snapshot-v1"
POLICY_ID = "grcv4-pure-representation-transport-v1"
_PACKAGE = "pygrc.models.grc_v4_assets"
_SCHEMAS = ("grc-v4-topology-event-schema.json", "grc-v4-representation-transport-schema.json")


@lru_cache(maxsize=1)
def _event_bindings(manifest_bytes: bytes, initializer_bytes: bytes) -> dict[str, str]:
    manifest = json.loads(manifest_bytes)
    payload = manifest["release_identity_payload"]
    initializer = cast(dict[str, Any], base._parsed_schema(initializer_bytes))
    if (manifest["release_id"] != EVENT_RELEASE_ID or
            EVENT_RELEASE_ID != _hash("grcv4-spec-release-sha256", payload) or
            payload["predecessor_release_id"] != base.INITIALIZER_RELEASE_ID or
            payload["snapshot_layout_ids"] != [EVENT_LAYOUT, REPRESENTATION_LAYOUT] or
            payload["representation_policy_id"] != POLICY_ID or
            payload["initializer_static_policy_digest"] != _hash(
                "grcv4-a-initializer-policy-sha256", initializer["$defs"]["static_policy"]["const"])):
        raise base.V4AssetError("event contract release mismatch")
    rows = payload["artifact_bindings"]
    bindings = {row["path"]: row["sha256"] for row in rows}
    if len(bindings) != len(rows):
        raise base.V4AssetError("duplicate event contract member")
    return bindings


@lru_cache(maxsize=1)
def _event_schemas(raws: tuple[bytes, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(cast(dict[str, Any], base._parsed_schema(raw)) for raw in raws)


def _load_event_schemas() -> tuple[tuple[dict[str, Any], ...], tuple[bytes, ...]]:
    """Read and check each asset; retain only private, verified schema content."""
    inherited = (base._load_contract_schema(), base._load_initializer_schema())
    try:
        package = resources.files(_PACKAGE)
        raw = package.joinpath("grc-v4-event-contract-release.json").read_bytes()
        if base._asset_digest(raw) != _MANIFEST_SHA256:
            raise base.V4AssetError("event contract manifest identity mismatch")
        bindings = _event_bindings(raw, inherited[1][1])
        loaded = []
        for filename in ("grc-v4-contract-schema.json", "grc-v4-a-initializer-schema.json", *_SCHEMAS):
            raw = package.joinpath(filename).read_bytes()
            if base._asset_digest(raw) != bindings["specs/" + filename]:
                raise base.V4AssetError("event contract schema mismatch: " + filename)
            loaded.append(raw)
        raws = tuple(loaded)
        return _event_schemas(raws), raws
    except (OSError, ImportError, ValueError, KeyError, TypeError) as exc:
        raise base.V4AssetError("event contract assets unavailable or invalid") from exc


def load_event_schemas() -> tuple[dict[str, Any], ...]:
    """Verify exact package pins on every lookup; return detached schemas."""
    schemas, _ = _load_event_schemas()
    return tuple(deepcopy(schema) for schema in schemas)


@lru_cache(maxsize=1)
def _event_registry(raws: tuple[bytes, ...]) -> Any:
    referencing = base._dependency("referencing")
    return referencing.Registry().with_resources(
        (s["$id"], referencing.Resource.from_contents(s)) for s in _event_schemas(raws)
    )


@lru_cache(maxsize=64)
def _event_validator(raws: tuple[bytes, ...], name: str) -> Any:
    family, _, definition = name.partition("/")
    schema = _event_schemas(raws)[2 if family == "event" else 3]
    js = base._dependency("jsonschema")
    validator_class = js.validators.extend(
        js.Draft202012Validator, {"pattern": base._identity_pattern}
    )
    return validator_class(
        {"$ref": schema["$id"] + "#/$defs/" + definition},
        registry=_event_registry(raws),
    )


def _hash(prefix: str, payload: object) -> str:
    return prefix + ":" + sha256(base.canonical_json_bytes(payload)).hexdigest()


def validate_event_payload(
    name: str, value: object, *, release_id: object = EVENT_RELEASE_ID
) -> dict[str, Any]:
    """Validate detached wire data; not numerical or profile/operation admission.

    Names are explicitly qualified as event/<definition> or
    representation/<definition>. Old schema versions cannot be reinterpreted.
    """
    if release_id != EVENT_RELEASE_ID:
        raise base.V4IdentityError("unknown event contract release")
    data = base.json_value(value)
    schemas, raws = _load_event_schemas()
    family, separator, definition = name.partition("/")
    if not separator or family not in ("event", "representation"):
        raise base.V4SchemaError("unknown event contract schema family")
    schema = schemas[2 if family == "event" else 3]
    if definition not in schema["$defs"]:
        raise base.V4SchemaError("unknown event contract definition")
    base._dependency("referencing")
    base._dependency("jsonschema")
    validator = _event_validator(raws, name)
    error = base._validation_error(validator, data, raws, name)
    if error is not None or not isinstance(data, dict):
        raise base.V4SchemaError("event contract " + name + ": " + (error.message if error else "expected object"))
    return data


def representation_identity(name, value, *, expected=None):
    prefixes = {"correspondence_payload": "grcv4-coordinate-map-sha256",
                "operation_identity_payload": "grcv4-representation-change-sha256",
                "receipt_payload": "grc-receipt-sha256"}
    if name not in prefixes:
        raise base.V4SchemaError("unknown representation identity domain")
    data = validate_event_payload("representation/" + name, value)
    result = _hash(prefixes[name], data)
    if expected is not None and expected != result:
        raise base.V4IdentityError("representation identity differs from preimage")
    return result


def event_snapshot_payload(value):
    """Explicit new-package wire dispatcher. Model restoration is still absent."""
    data = base.json_value(value)
    if not isinstance(data, dict):
        raise base.V4SchemaError("expected event snapshot object")
    family = {EVENT_LAYOUT: "event", REPRESENTATION_LAYOUT: "representation"}.get(data.get("implementation_layout_id"))
    if family is None:
        raise base.V4SchemaError("unsupported event contract snapshot layout")
    return validate_event_payload(family + "/snapshot_payload", data, release_id=data.get("specification_release_id"))


def validate_representation_group(value, *, previous_primary_receipt_id):
    """Check a singleton group's declared identities/links, not ledger or numerics.

    The caller must supply the actual previous head (None at ledger start).
    This local check does not authenticate that head or execute the operation.
    """
    data = validate_event_payload("representation/operation_group", value)
    record = data["commit_record"]
    commit = record["payload"]
    envelope = data["receipts"][0]
    receipt = envelope["identity_payload"]
    rid = representation_identity("receipt_payload", receipt, expected=envelope["receipt_id"])
    cid = _hash("grc-commit-sha256", commit)
    if record["commit_id"] != cid or envelope["commit_id"] != cid or commit["emitted_receipt_ids"] != [rid]:
        raise base.V4IdentityError("representation group commit/receipt links disagree")
    core = receipt["core"]
    if any(commit[k] != core[k] for k in ("operation_id", "source_state_digest", "target_state_digest")):
        raise base.V4IdentityError("representation group endpoint/operation declarations disagree")
    expected = [] if previous_primary_receipt_id is None else [previous_primary_receipt_id]
    if core["parent_receipt_ids"] != expected or previous_primary_receipt_id == rid:
        raise base.V4IdentityError("representation group previous-primary declaration disagrees")
    return data


def validate_correspondence(record, source_graph, target_graph):
    """Authenticate graph correspondence declarations, not W/Z transport."""
    data = validate_event_payload("representation/correspondence_record", record)
    representation_identity("correspondence_payload", data["payload"], expected=data["correspondence_id"])
    source = base.validate_payload("serialized_graph_payload", source_graph)
    target = base.validate_payload("serialized_graph_payload", target_graph)
    p = data["payload"]
    for role, graph in (("source", source), ("target", target)):
        if p[role + "_graph_digest"] != _hash("grc-graph-sha256", graph):
            raise base.V4IdentityError("correspondence graph digest mismatch")
        nodes = graph["live_node_ids"]
        edges = graph["oriented_edges"]
        if len({e["edge_id"] for e in edges}) != len(edges) or any(
                e[k] not in nodes for e in edges for k in ("tail_node_id", "head_node_id")):
            raise base.V4SchemaError("ambiguous edge identity or unknown graph endpoint")
    vertices, edges = p["vertex_map"], p["edge_map"]
    if ([r["source_vertex_id"] for r in vertices] != source["live_node_ids"] or
            len(vertices) != len(target["live_node_ids"]) or
            {r["target_vertex_id"] for r in vertices} != set(target["live_node_ids"])):
        raise base.V4SchemaError("vertex correspondence is not a complete ordered bijection")
    source_edges, target_edges = source["oriented_edges"], target["oriented_edges"]
    if ([r["source_edge_id"] for r in edges] != [e["edge_id"] for e in source_edges] or
            len(edges) != len(target_edges) or
            {r["target_edge_id"] for r in edges} != {e["edge_id"] for e in target_edges}):
        raise base.V4SchemaError("edge correspondence is not a complete ordered bijection")
    node_map = {r["source_vertex_id"]: r["target_vertex_id"] for r in vertices}
    target_by_id = {e["edge_id"]: e for e in target_edges}
    for row, edge in zip(edges, source_edges):
        mapped = (node_map[edge["tail_node_id"]], node_map[edge["head_node_id"]])
        wanted = target_by_id[row["target_edge_id"]]
        endpoints = (wanted["tail_node_id"], wanted["head_node_id"])
        if mapped != (endpoints if row["orientation"] == 1 else endpoints[::-1]):
            raise base.V4SchemaError("edge orientation/endpoints contradict declared vertex map")
    return data


def validate_representation_request(value, source_graph):
    """Check request/map graph linkage; source state/profile admission is later."""
    data = validate_event_payload("representation/request", value)
    record = validate_correspondence(data["correspondence"], source_graph, data["target_graph"])
    if data["source_graph_digest"] != record["payload"]["source_graph_digest"]:
        raise base.V4IdentityError("representation request and map source disagree")
    return data
