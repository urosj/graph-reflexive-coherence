"""Bounded same-graph profile maps; no solver, lifecycle owner or initializer guess.

P9-7.2a implements preserving, zero-initializing and lossy maps. C-to-A uses
the accepted target-reference-pass producer; a declaration or supplied W array
alone cannot discharge that obligation.
"""

from dataclasses import replace
from typing import Any

from .grc_v4 import ResolvedHistoryBundlePolicy
from .grc_v4_codec import canonical_json_bytes, payload_identity
from .grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
from .grc_v4_state import GRCV4AuthoritativeState


class MigrationAdmissionError(ValueError):
    """A declared migration lacks the required map/history authority."""


def history_digest(inputs: GeometryStageInputs, subject: str) -> str | None:
    """Current then reset, in the bound graph's edge/tensor order.

    The two equal-length halves are independently meaningful; do not bind only
    live history. Graph/profile and both authority preimages are in the receipt.
    """
    field = {"candidate": "W_A", "carrier": "Z_4"}[subject]
    current, reset = getattr(inputs.current, field), getattr(inputs.reset, field)
    if current is None and reset is None:
        return None
    if current is None or reset is None:
        raise MigrationAdmissionError("current/reset history populations disagree")
    return payload_identity("history_content_identity_payload", dict(
        schema_version="grcv4-history-content-identity-v1", subject=subject,
        content=list(current + reset)))


def _persistent(reference: GRCV4ReferenceGeometry) -> bool:
    return reference.profile.identity_payload.realization in ("PC", "CI+PC")


def carrier_contract(reference: GRCV4ReferenceGeometry) -> dict[str, Any]:
    """Carrier authority excludes the added/removed immediate CI path only."""
    params = reference.profile.params_resolved.to_payload()
    realization = params["realization"]
    return dict(
        graph=reference.graph.to_payload(), K4_base=reference.K4_base,
        edge_weights=reference.edge_weights.to_dict(), context=reference.context.to_payload(),
        common=params["common"], candidate=params["candidate"], geometry=params["geometry"],
        carrier={key: realization[key] for key in (
            "tau_PC", "radius", "carrier_norm_id", "source_envelope_id", "writer_id")},
    )


def migration_history_policy(
    before: GeometryStageInputs, target: GRCV4ReferenceGeometry,
) -> ResolvedHistoryBundlePolicy:
    """Construct the required declaration, not proof of target admission.

    Consumers must recompute it from their own current and reset authority.
    This helper cannot supply missing backend/initializer or target support.
    """
    source = before.geometry.reference
    a, b = source.profile.identity_payload.candidate, target.profile.identity_payload.candidate
    from .grc_v4_initializer import HISTORY_POLICY, POLICY_ID
    if a == "C" and b == "A" and target.profile.params_resolved.lifecycle.history_policy_id != HISTORY_POLICY:
        raise MigrationAdmissionError("C-to-A requires an admitted target reference-current initializer source for current and reset")

    def channel(subject: str, policy: str, disposition: str,
                loss: str = "none", initializer: str | None = None) -> dict[str, Any]:
        return dict(schema_version="grcv4-history-channel-policy-v1", subject=subject,
                    policy_id=policy, disposition=disposition,
                    source_history_digest=history_digest(before, subject),
                    target_initializer_id=initializer, information_loss=loss)

    if a == "A" and b == "A":
        candidate = channel("candidate", "identity_candidate_history_v1", "exact_transport")
    elif a == "A":
        candidate = channel("candidate", "archive_drop_candidate_history_v1", "explicit_loss", "candidate_history_loss")
    elif b == "A":
        candidate = channel("candidate", HISTORY_POLICY, "target_initializer", initializer=POLICY_ID)
    else:
        candidate = channel("candidate", "candidate_c_rederive_no_history_v1", "rederived")
    old, new = _persistent(source), _persistent(target)
    if old and new and a == b:
        if canonical_json_bytes(carrier_contract(source)) != canonical_json_bytes(carrier_contract(target)):
            raise MigrationAdmissionError("persistent history preservation requires exact carrier/K4/geometry/writer/tau/norm/domain identity")
        carrier = channel("carrier", "identity_carrier_history_v1", "exact_transport")
    elif old and new:
        carrier = channel("carrier", "loss_and_zero_target_carrier_v1", "whole_carrier_reset",
                          "carrier_history_loss", "canonical_zero_carrier_v1")
    elif new:
        carrier = channel("carrier", "canonical_zero_carrier_initialization_v1", "target_initializer",
                          initializer="canonical_zero_carrier_v1")
    elif old:
        carrier = channel("carrier", "archive_drop_carrier_history_v1", "explicit_loss", "carrier_history_loss")
    else:
        carrier = channel("carrier", "no_persistent_carrier_v1", "not_applicable")
    return ResolvedHistoryBundlePolicy.from_payload(dict(
        schema_version="grcv4-history-bundle-policy-v1", candidate=candidate, carrier=carrier))


def map_migration(
    before: GeometryStageInputs, target: GRCV4ReferenceGeometry,
    policy: ResolvedHistoryBundlePolicy,
    initializer_pair: dict | None = None,
) -> GeometryStageInputs:
    """Public map: authenticate any supplied reconstruction, not just its hash."""
    if initializer_pair is not None:
        from .grc_v4_initializer import CandidateAReferencePassPair
        initializer_pair = CandidateAReferencePassPair.from_record(initializer_pair).to_record()
    return _map_migration(before, target, policy, initializer_pair)


def _map_migration(before, target, policy, initializer_pair=None) -> GeometryStageInputs:
    # Lifecycle-owned pairs were computed live or authenticated during import.
    # Publication rechecks their identities/endpoints without repeating numerics.
    """Apply the declared whole-current/reset map, without performing a beat."""
    source = before.geometry.reference
    if source.graph != target.graph:
        raise MigrationAdmissionError("profile migration cannot change graph or edge order")
    if source.pairings.vertex != target.pairings.vertex:
        raise MigrationAdmissionError("identity resource migration requires unchanged vertex measure")
    expected = migration_history_policy(before, target)
    if policy != expected:
        raise MigrationAdmissionError("migration history policy does not bind the required current/reset map")
    same = source.profile.identity_payload.candidate == target.profile.identity_payload.candidate
    needs_initializer = not same and target.profile.identity_payload.candidate == "A"
    if needs_initializer != (initializer_pair is not None):
        raise MigrationAdmissionError("missing or extraneous initializer pair")
    if initializer_pair is not None:
        from .grc_v4_codec import validate_initializer_payload, initializer_identity
        record = validate_initializer_payload("pair_record", initializer_pair)
        initializer_identity("pair_payload", record["payload"], expected=record["initializer_pair_id"])
        for role, old in (("current", before.current), ("reset", before.reset)):
            row = record["payload"][role]
            p = row["payload"]
            initializer_identity("construction_payload", p, expected=row["construction_id"])
            if (canonical_json_bytes(p["target_reference"]) != canonical_json_bytes(target.to_payload())
                    or tuple(p["target_C"]) != old.C):
                raise MigrationAdmissionError("initializer pair does not bind requested target inputs")

    def state(old: GRCV4AuthoritativeState, role: str) -> GRCV4AuthoritativeState:
        weight = old.W_A if target.profile.identity_payload.candidate == "A" else None
        if needs_initializer:
            weight = tuple(initializer_pair["payload"][role]["payload"]["W_A_init"])
        carrier = ((old.Z_4 if same and _persistent(source) else
                    (0.0,) * len(target.graph.live_edge_ids)**2) if _persistent(target) else None)
        return GRCV4AuthoritativeState(old.C, weight, carrier)

    return replace(before, geometry=target.geometry(), context=target.context,
                   current=state(before.current, "current"), reset=state(before.reset, "reset"))
