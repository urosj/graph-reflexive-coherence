"""Operation-local reuse of checked lifecycle preimages; never a replay permit.

Receipt-ID tuples and the operation's privately detached stage reference are
retained. Public captures and numerical admission remain with their owners.
Scope exit discards operation memoization,
including on failure; nested operations and threads have independent scopes.
The privately owned archive retains only its incremental receipt hash state.
"""

from dataclasses import dataclass, field
from functools import wraps
from hashlib import sha256
from typing import Any

from . import grc_v4_codec as codec


def _scope():
    context = codec._OPERATION_CONTEXT.get()
    return None if context is None else context.evidence


def _envelope_parts(scientific_id):
    """Derive the canonical framing from the codec; reject a changed layout."""
    encoded = codec.canonical_json_bytes(_envelope(scientific_id, ()))
    head, separator, tail = encoded.partition(b"[]")
    if head != b'{"receipt_ids":' or not separator:
        raise codec.V4IdentityError("unsupported canonical lifecycle envelope layout")
    return head + b"[", b"]" + tail


def _receipt_bytes(receipt_ids):
    # Encode elements rather than slicing a serializer's array delimiters.
    return b",".join(codec.canonical_json_bytes(value) for value in receipt_ids)


def _envelope(scientific_id, receipt_ids):
    return {
        "schema_version": "grcv4-lifecycle-envelope-v1",
        "scientific_state_digest": scientific_id,
        "receipt_ids": list(receipt_ids),
    }


@dataclass(frozen=True, slots=True, eq=False)
class _ReceiptEvidence:
    """Private SHA state before closing the canonical receipt array.

    Hash copies preserve exact legacy identities. Extending a checked prefix
    processes only new IDs and never mutates a previously published hash state.
    This proves array grammar, not receipt authenticity or scientific claims.
    """

    count: int
    _hash: Any = field(repr=False)

    @classmethod
    def from_ids(cls, receipt_ids):
        checked = codec.validate_payload("lifecycle_envelope_payload", _envelope("grcv4-state-sha256:" + "0" * 64, receipt_ids))
        return cls._checked(tuple(checked["receipt_ids"]))

    @classmethod
    def _checked(cls, receipt_ids):
        head, _ = _envelope_parts("grcv4-state-sha256:" + "0" * 64)
        digest = sha256(head)
        digest.update(_receipt_bytes(receipt_ids))
        return cls(len(receipt_ids), digest)

    def extend(self, receipt_ids):
        checked = codec.validate_payload("lifecycle_envelope_payload", _envelope("grcv4-state-sha256:" + "0" * 64, receipt_ids))
        receipt_ids = tuple(checked["receipt_ids"])
        digest = self._hash.copy()
        if receipt_ids:
            if self.count:
                digest.update(b",")
            digest.update(_receipt_bytes(receipt_ids))
        return type(self)(self.count + len(receipt_ids), digest)

    def identity(self, scientific_id):
        small = codec.validate_payload("lifecycle_envelope_payload", _envelope(scientific_id, ()))
        _, tail = _envelope_parts(small["scientific_state_digest"])
        digest = self._hash.copy()
        digest.update(tail)
        return "grcv4-lifecycle-sha256:" + digest.hexdigest()


class _OperationEvidence:
    """Bound retained prefixes and identities independently of trial count."""

    def __init__(self):
        self.aliases = []
        self.prefixes = {}
        self.identities = {}
        self.seeds = []
        self.reference = None

    def seed(self, prefix, receipt_ids):
        """Only the archive owner may supply a checked, unexposed prefix."""
        if prefix.count != len(receipt_ids):
            raise ValueError("receipt prefix count differs from owned ledger")
        if len(self.seeds) < 8:
            self.seeds.append((receipt_ids, prefix))

    def lifecycle(self, scientific_id, receipt_ids):
        # Forced mutation and subclasses do not gain trust from Python equality.
        # Unrecognized input follows the original full schema/identity path.
        if type(scientific_id) is not str or type(receipt_ids) is not tuple:
            return codec.payload_identity("lifecycle_envelope_payload", _envelope(scientific_id, receipt_ids))
        codec._load_contract_schema()
        codec._dependency("jsonschema")
        codec._dependency("referencing")
        alias = next((row for row in self.aliases if row[0] is receipt_ids), None)
        if alias is None:
            if any(type(value) is not str for value in receipt_ids):
                return codec.payload_identity("lifecycle_envelope_payload", _envelope(scientific_id, receipt_ids))
            prefix = next((fact for ids, fact in self.seeds if receipt_ids == ids), None)
            if prefix is None:
                encoded = codec.canonical_json_bytes(list(receipt_ids))
                prefix = self.prefixes.get(encoded)
                if prefix is None:
                    if len(self.prefixes) >= 8:
                        return codec.payload_identity("lifecycle_envelope_payload", _envelope(scientific_id, receipt_ids))
                    # Full admission once per exact ordered prefix, not merely
                    # a supplied digest or a claim that its IDs are strings.
                    codec.validate_payload("lifecycle_envelope_payload", _envelope(scientific_id, receipt_ids))
                    prefix = _ReceiptEvidence._checked(receipt_ids)
                    self.prefixes[encoded] = prefix
            if len(self.aliases) >= 128:
                self.aliases.clear()
            # Retain the actual immutable object, with a bounded identity scan.
            alias = (receipt_ids, prefix)
            self.aliases.append(alias)
        key = (alias[1], scientific_id)
        known = self.identities.get(key)
        if known is not None:
            return known
        # Each distinct state digest adds only a fixed-size suffix to a
        # copy of the checked prefix's internal SHA state. No rehash of IDs.
        identifier = alias[1].identity(scientific_id)
        if len(self.identities) < 256:
            self.identities[key] = identifier
        return identifier


def _lifecycle_identity(scientific_id, receipt_ids):
    scope = _scope()
    if scope is None:
        return codec.payload_identity("lifecycle_envelope_payload", _envelope(scientific_id, receipt_ids))
    return scope.lifecycle(scientific_id, receipt_ids)


def _seed_receipts(prefix, receipt_ids):
    scope = _scope()
    if scope is not None:
        scope.seed(prefix, receipt_ids)


def _own_stage_reference(reference):
    """Register only the operation's freshly detached, fully admitted root."""
    scope = _scope()
    if scope is not None:
        if scope.reference is not None and scope.reference is not reference:
            raise ValueError("operation already owns a different stage reference")
        scope.reference = reference


def _owns_stage_reference(reference):
    scope = _scope()
    return scope is not None and scope.reference is not None and scope.reference is reference


def _operation_evidence(function):
    @wraps(function)
    def owned_operation(*args, **kwargs):
        with codec._operation_contract_assets(_OperationEvidence()):
            return function(*args, **kwargs)
    return owned_operation
