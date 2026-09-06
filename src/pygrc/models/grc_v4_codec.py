"""V4 I-JSON/JCS and schema primitives, not model or operation admission.

No state/model, repository, vector-builder, network or legacy codec imports.
Optional dependencies are loaded at request time; importing older families
does not require the V4 extra. Hashing proves payload identity, not scientific
validity, graph ordering, runtime support or receipt/lifecycle acceptance.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from hashlib import sha256
import importlib
from importlib import resources
import json
import math
import re
from types import ModuleType
from typing import Literal, TypeAlias, cast

JSONValue: TypeAlias = (
    "None | bool | int | float | str | list[JSONValue] | dict[str, JSONValue]"
)

RELEASE_ID = (
    "grcv4-spec-release-sha256:"
    "9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f"
)
_ASSET_PACKAGE = "pygrc.models.grc_v4_assets"
_INDEX_SHA256 = "c1ac9d8d3bb924f29b775bd9863a33a454da41e98c57ef0b8bb3c24171fafc9f"


class V4DependencyError(RuntimeError):
    """A requested V4 primitive lacks its declared optional dependency."""


class V4AssetError(RuntimeError):
    """A packaged accepted asset is missing or has the wrong identity."""


class V4WireError(ValueError):
    """Malformed JSON or data outside the V4 I-JSON domain."""


class V4SchemaError(ValueError):
    """Data does not satisfy the selected closed contract schema."""


class V4DecodeShapeError(V4WireError):
    """JSON parsed, but the transport record shape is invalid; no admission."""


class V4IdentityError(ValueError):
    """An identity-bearing payload and a supplied identifier disagree."""


def _dependency(name: str) -> ModuleType:
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise V4DependencyError(
            f"V4 requires {name}; install the pygrc[v4] extra"
        ) from exc


def _copy_json(value: object, active: set[int]) -> JSONValue:
    if value is None or type(value) is bool:
        return value
    if type(value) is str:
        try:
            value.encode("utf-8")
        except UnicodeError as exc:
            raise V4WireError("lone surrogate is not I-JSON") from exc
        return value
    if type(value) is int:
        if abs(value) > 2**53 - 1:
            raise V4WireError("integer outside the I-JSON safe range")
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise V4WireError("nonfinite number")
        if value == 0 and math.copysign(1, value) < 0:
            raise V4WireError("negative zero")
        return value
    if not isinstance(value, Mapping) and type(value) not in (list, tuple):
        raise V4WireError("expected JSON scalars, ordered arrays or string maps")
    if id(value) in active:
        raise V4WireError("cyclic JSON input")
    active.add(id(value))
    try:
        if isinstance(value, Mapping):
            result: dict[str, JSONValue] = {}
            for key, item in value.items():
                if type(key) is not str:
                    raise V4WireError("JSON keys must be strings")
                _copy_json(key, active)
                if key in result:
                    raise V4WireError("duplicate JSON key")
                result[key] = _copy_json(item, active)
            return result
        if isinstance(value, (tuple, list)):
            return [_copy_json(item, active) for item in value]
        raise V4WireError("expected JSON array")
    finally:
        active.remove(id(value))


def json_value(value: object) -> JSONValue:
    """Defensively copy primitive configuration, without coercion or admission."""
    try:
        return _copy_json(value, set())
    except RecursionError as exc:
        raise V4WireError("JSON nesting exceeds the interpreter limit") from exc


def _pairs(items: list[tuple[str, JSONValue]]) -> dict[str, JSONValue]:
    result: dict[str, JSONValue] = {}
    for key, value in items:
        if key in result:
            raise V4WireError("duplicate JSON key")
        result[key] = value
    return result


def _integer(token: str) -> int:
    if token == "-0":
        raise V4WireError("negative zero")
    return int(token)


def _constant(token: str) -> None:
    raise V4WireError(f"non-JSON constant: {token}")


def _floating(token: str) -> float:
    result = float(token)
    significand = token.lower().split("e", 1)[0]
    if result == 0 and any(digit in significand for digit in "123456789"):
        # A positive beat must not silently become the zero-duration branch.
        # Ordinary binary64 rounding is retained, but nonzero-to-zero
        # underflow is an out-of-range wire value, not a numeric default.
        raise V4WireError("nonzero number underflows the binary64 range")
    return result


def decode_json(data: bytes | str) -> JSONValue:
    """Strict configuration JSON: integer-shaped tokens must be safe integers.

    This is NOT the inverse of JCS for large binary64 values. Use the explicit
    decode_canonical_json path to reconstruct canonical identity payloads.
    Neither decoder constructs an admitted operation or scientific state.
    """
    if type(data) not in (bytes, str):
        raise V4WireError("wire input must be UTF-8 bytes or text")
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        return json_value(json.loads(
            text, object_pairs_hook=_pairs, parse_int=_integer,
            parse_float=_floating, parse_constant=_constant,
        ))
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, V4WireError):
            raise
        raise V4WireError("malformed UTF-8 JSON") from exc


def canonical_json_bytes(value: object) -> bytes:
    """RFC 8785 bytes after V4's stronger I-JSON input checks."""
    detached = json_value(value)
    return cast(bytes, _dependency("rfc8785").dumps(detached))


def _canonical_integer(token: str) -> int | float:
    value = _integer(token)
    if abs(value) <= 2**53 - 1:
        return value
    # JCS emits integer-shaped tokens for some already-admitted binary64
    # values. Their original Python scalar type is not present on the wire.
    # Exact re-encoding below rejects tokens changed by binary64 rounding.
    return float(token)


def decode_canonical_json(data: bytes | str) -> JSONValue:
    """Decode ONLY the exact JCS image of the existing binary64 value domain.

    Large integer-shaped tokens mean binary64 here, explicitly, not arbitrary
    precision integers. Re-encoding must match every input byte: for example
    9007199254740993 rejects, while the canonical image of float(2**53) works.
    Native oversized integers still fail json_value/canonical_json_bytes;
    count/index fields still require their safe-integer schema and typed
    resolution. This primitive does not itself perform schema admission.
    """
    if type(data) not in (bytes, str):
        raise V4WireError("canonical input must be UTF-8 bytes or text")
    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        raw = text.encode("utf-8")
        value = json_value(json.loads(
            text, object_pairs_hook=_pairs, parse_int=_canonical_integer,
            parse_float=_floating, parse_constant=_constant,
        ))
        if canonical_json_bytes(value) != raw:
            raise V4WireError("not exact canonical binary64 JSON")
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        if isinstance(exc, V4WireError):
            raise
        raise V4WireError("malformed canonical UTF-8 JSON") from exc


def load_contract_schema() -> dict[str, JSONValue]:
    """Verify installed bytes before parsing; return an unshared schema copy."""
    try:
        package = resources.files(_ASSET_PACKAGE)
        index_bytes = package.joinpath("asset-index.json").read_bytes()
        if sha256(index_bytes).hexdigest() != _INDEX_SHA256:
            raise V4AssetError("packaged asset index identity mismatch")
        index = json.loads(index_bytes)
        if index["release_id"] != RELEASE_ID:
            raise V4AssetError("wrong accepted release")
        loaded: dict[str, bytes] = {}
        for entry in index["files"]:
            name = entry["name"]  # Names are pinned by the code-bound index hash.
            raw = package.joinpath(name).read_bytes()
            if sha256(raw).hexdigest() != entry["sha256"]:
                raise V4AssetError(f"packaged asset identity mismatch: {name}")
            loaded[name] = raw
        manifest = json.loads(loaded["grc-v4-specification-release.json"])
        if manifest["release_id"] != RELEASE_ID:
            raise V4AssetError("packaged manifest release mismatch")
        release_preimage = canonical_json_bytes(manifest["release_identity_payload"])
        if RELEASE_ID != "grcv4-spec-release-sha256:" + sha256(
            release_preimage
        ).hexdigest():
            raise V4AssetError("release preimage identity mismatch")
        schema = decode_json(loaded["grc-v4-contract-schema.json"])
        if not isinstance(schema, dict):
            raise V4AssetError("schema is not an object")
        return schema
    except (OSError, ImportError, ValueError, KeyError, TypeError) as exc:
        raise V4AssetError("accepted packaged assets unavailable or invalid") from exc


def _identity_pattern(
    validator: object, pattern: str, instance: JSONValue, schema: object
) -> Iterator[object]:
    # All patterns in the pinned schema are whole identity grammars. Python's
    # '$' also matches before a final newline; the normative IDs do not.
    if isinstance(instance, str) and re.fullmatch(pattern, instance) is None:
        yield _dependency("jsonschema").ValidationError(
            "identifier does not match the complete contract grammar"
        )


def validate_payload(schema_ref: str, value: object) -> dict[str, JSONValue]:
    """Closed-schema data validation only; returns detached primitive fields."""
    data = json_value(value)
    schema = load_contract_schema()
    name = schema_ref.removeprefix("#/$defs/")
    definitions = schema["$defs"]
    if not isinstance(definitions, dict) or name not in definitions:
        raise V4SchemaError("unknown local contract definition")
    # Only the pinned local definitions can be selected. All their references
    # are fragments, so no caller schema or remote resolution enters this path.
    schema["$ref"] = "#/$defs/" + name
    js = _dependency("jsonschema")
    validator_class = js.validators.extend(
        js.Draft202012Validator, {"pattern": _identity_pattern}
    )
    validator = validator_class(schema)
    error = next(validator.iter_errors(data), None)
    if error is not None:
        path = "/".join(str(part) for part in error.absolute_path)
        raise V4SchemaError(f"{name}/{path}: {error.message}")
    if not isinstance(data, dict):
        raise V4SchemaError("identity/record payload must be an object")
    return data


def decode_record_payload(
    schema_ref: str, data: bytes | str, *,
    encoding: Literal["configuration", "canonical"] = "configuration",
) -> dict[str, JSONValue]:
    """Decode the generic request transport shapes owned by P9-2.3.

    Malformed JSON and shape-invalid input raise before an operation exists.
    Semantic constraints deliberately absent from an input schema must be
    handled by that operation's admission owner, not translated here.
    No automatic retry through the other numeric route is permitted.
    This is not a harness, snapshot or GRC9 request decoding entry point.
    """
    if type(schema_ref) is not str:
        raise TypeError("request schema selector must be a string")
    if schema_ref not in ("step_request_input", "migration_request"):
        raise V4SchemaError("unsupported generic request transport schema")
    if type(encoding) is not str or encoding not in ("configuration", "canonical"):
        raise TypeError("encoding must select configuration or canonical")
    value = decode_json(data) if encoding == "configuration" else decode_canonical_json(data)
    try:
        return validate_payload(schema_ref, value)
    except V4SchemaError as exc:
        raise V4DecodeShapeError(str(exc)) from exc


# Payload schema -> exact normative prefix. No arbitrary caller prefix or
# inferred wrapper. Generic codec support does not authorize GRC9V4 mechanics.
_IDENTITY_PREFIXES = {
    "resolved_params": "grcv4-params-sha256",
    "profile_identity_payload": "grcv4-profile-sha256",
    "profile_template_payload": "grcv4-profile-template-sha256",
    "candidate_a_profile_template_payload": "grcv4-profile-template-sha256",
    "candidate_c_profile_template_payload": "grcv4-profile-template-sha256",
    "resolved_specialization": "grc9v4-params-sha256",
    "specialization_identity_payload": "grc9v4-specialization-sha256",
    "complete_model_identity_payload": "grc9v4-model-sha256",
    "port_graph_payload": "grc-graph-sha256",
    "reset_payload": "grcv4-reset-sha256",
    "grcv4_reset_payload": "grcv4-reset-sha256",
    "grc9v4_reset_payload": "grcv4-reset-sha256",
    "scientific_state_payload": "grcv4-state-sha256",
    "lifecycle_envelope_payload": "grcv4-lifecycle-sha256",
    "expansion_event_identity_payload": "grc-event-sha256",
    "mapped_topology_event_identity_payload": "grc-event-sha256",
    "commit_payload": "grc-commit-sha256",
    "authoritative_state_identity_payload": "grcv4-authoritative-sha256",
    "wctr_identity_payload": "grcv4-wctr-sha256",
    "resource_transform_identity_payload": "grcv4-resource-transform-sha256",
    "history_channel_policy_identity_payload": "grcv4-history-policy-sha256",
    "history_bundle_identity_payload": "grcv4-history-map-sha256",
    "expansion_history_identity_payload": "grcv4-history-map-sha256",
    "history_content_identity_payload": "grcv4-history-content-sha256",
    "expansion_policy_identity_payload": "grc9v4-expansion-policy-sha256",
    "k4_identity_payload": "grcv4-k4-sha256",
    "reference_hodge_identity_payload": "grcv4-hodge-sha256",
    **{
        name + "_receipt_identity_payload": "grc-receipt-sha256"
        for name in (
            "topology_event", "step_commit", "reset", "rebase",
            "profile_migration", "charge", "history_disposition",
            "legacy_compatibility", "failure",
        )
    },
}


def payload_identity(
    schema_ref: str, value: object, *, expected: str | None = None
) -> str:
    """Recompute a named preimage identity; mismatches never repair inputs."""
    name = schema_ref.removeprefix("#/$defs/")
    if name not in _IDENTITY_PREFIXES:
        raise V4SchemaError("definition is not an identity preimage")
    data = validate_payload(name, value)
    identifier = _IDENTITY_PREFIXES[name] + ":" + sha256(
        canonical_json_bytes(data)
    ).hexdigest()
    if expected is not None and identifier != expected:
        raise V4IdentityError(f"{name}: supplied identity does not match payload")
    return identifier
