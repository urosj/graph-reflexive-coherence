"""Explicit basin specialization successor; frozen v1 codecs stay unchanged."""

from hashlib import sha256

from .grc_v4_codec import canonical_json_bytes, payload_identity, validate_payload
from .grc_v4_state import FrozenJSONMap

POLICY_ID = "grc9v4-terminal-flow-regions-v1"
POLICY = {"schema_version": "grc9v4-basin-policy-v1", "policy_id": POLICY_ID}
_VERSIONS = {
    "resolved_specialization": "grc9v4-resolved-specialization",
    "specialization_identity_payload": "grc9v4-specialization-identity",
    "complete_model_identity_payload": "grc9v4-complete-identity",
}
_PREFIXES = {
    "resolved_specialization": "grc9v4-params-sha256:",
    "specialization_identity_payload": "grc9v4-specialization-sha256:",
    "complete_model_identity_payload": "grc9v4-model-sha256:",
}


def validate_specialization(name, value):
    data = FrozenJSONMap(value).to_dict()
    version = data.get("schema_version")
    base = _VERSIONS[name]
    if version == base + "-v1":
        return validate_payload(name, data)
    if version != base + "-v2":
        raise ValueError("unsupported specialization schema")
    old = dict(data, schema_version=base + "-v1")
    if name == "resolved_specialization":
        if old.pop("basin_policy", None) != POLICY:
            raise ValueError("explicit accepted basin policy required")
    elif name == "specialization_identity_payload":
        if old.pop("basin_policy_id", None) != POLICY_ID:
            raise ValueError("explicit basin policy identity required")
    validate_payload(name, old)
    return data


def specialization_identity(name, value, *, expected=None):
    data = validate_specialization(name, value)
    if data["schema_version"].endswith("-v1"):
        return payload_identity(name, data, expected=expected)
    result = _PREFIXES[name] + sha256(canonical_json_bytes(data)).hexdigest()
    if expected is not None and result != expected:
        raise ValueError("specialization identity differs from exact preimage")
    return result


def has_basin(specialization):
    return (
        specialization.resolved["schema_version"]
        == _VERSIONS["resolved_specialization"] + "-v2"
    )


def model_identity(profile_id, specialization):
    return specialization_identity(
        "complete_model_identity_payload",
        dict(
            schema_version="grc9v4-complete-identity-v2"
            if has_basin(specialization)
            else "grc9v4-complete-identity-v1",
            grcv4_complete_profile_id=profile_id,
            specialization_id=specialization.specialization_id,
        ),
    )
