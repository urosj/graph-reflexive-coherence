"""Explicit reconstruction and coordinate maps; publication stays in lifecycle.

No graph matching, fallback after failed preservation, or source-history input
to the target initializer. Both current and reset are mapped independently.
"""

from dataclasses import replace
from copy import deepcopy

from .grc_v4 import ResolvedHistoryBundlePolicy
from .grc_v4_codec import canonical_json_bytes, payload_identity, V4IdentityError, V4SchemaError
from .grc_v4_event_codec import validate_correspondence
from .grc_v4_geometry import GraphCoordinateAction, GRCV4Graph, _computed
from .grc_v4_migration import history_digest, _persistent
from .grc_v4_state import GRCV4AuthoritativeState


class EventAdmissionError(ValueError):
    """Declared event or coordinate action does not match admitted authority."""


def reconstruction_history_policy(before, target):
    from .grc_v4_initializer import HISTORY_POLICY, POLICY_ID
    a = before.geometry.reference.profile.identity_payload.candidate
    b = target.profile.identity_payload.candidate
    if b == "A" and target.profile.params_resolved.lifecycle.history_policy_id != HISTORY_POLICY:
        raise EventAdmissionError("A event target requires the accepted reference-pass history policy")

    def channel(subject, policy, disposition, loss="none", initializer=None):
        return dict(schema_version="grcv4-history-channel-policy-v1", subject=subject,
                    policy_id=policy, disposition=disposition, information_loss=loss,
                    source_history_digest=history_digest(before, subject), target_initializer_id=initializer)

    if a == "A":
        candidate = channel("candidate", "candidate_a_event_loss_reference_pass_v1" if b == "A" else
                            "archive_drop_candidate_history_v1", "explicit_loss", "candidate_history_loss",
                            POLICY_ID if b == "A" else None)
    elif b == "A":
        candidate = channel("candidate", HISTORY_POLICY, "target_initializer", initializer=POLICY_ID)
    else:
        candidate = channel("candidate", "candidate_c_rederive_no_history_v1", "rederived")
    old, new = _persistent(before.geometry.reference), _persistent(target)
    if old and new:
        carrier = channel("carrier", "event_loss_and_zero_target_carrier_v1", "whole_carrier_reset",
                          "carrier_history_loss", "canonical_zero_carrier_v1")
    elif old:
        carrier = channel("carrier", "archive_drop_carrier_history_v1", "explicit_loss", "carrier_history_loss")
    elif new:
        carrier = channel("carrier", "canonical_zero_carrier_initialization_v1", "target_initializer",
                          initializer="canonical_zero_carrier_v1")
    else:
        carrier = channel("carrier", "no_persistent_carrier_v1", "not_applicable")
    return ResolvedHistoryBundlePolicy.from_payload(dict(schema_version="grcv4-history-bundle-policy-v1",
                                                         candidate=candidate, carrier=carrier))


def reconstructed_histories(before, current, reset, target, policy, pair):
    if policy != reconstruction_history_policy(before, target):
        raise EventAdmissionError("event history policy does not bind source current/reset and target")
    needs_pair = target.profile.identity_payload.candidate == "A"
    if needs_pair != (pair is not None):
        raise EventAdmissionError("missing or extraneous event initializer pair")
    if pair is not None:
        from .grc_v4_codec import validate_initializer_payload, initializer_identity
        pair = validate_initializer_payload("pair_record", pair)
        initializer_identity("pair_payload", pair["payload"], expected=pair["initializer_pair_id"])
    states = {}
    for role, old in (("current", current), ("reset", reset)):
        weight = None
        if pair is not None:
            row = pair["payload"][role]; p = row["payload"]
            initializer_identity("construction_payload", p, expected=row["construction_id"])
            if (canonical_json_bytes(p["target_reference"]) != canonical_json_bytes(target.to_payload())
                    or tuple(p["target_C"]) != old.C):
                raise EventAdmissionError("event initializer does not bind mapped role/target")
            weight = tuple(p["W_A_init"])
        states[role] = GRCV4AuthoritativeState(old.C, weight,
            (0.0,) * len(target.graph.live_edge_ids)**2 if _persistent(target) else None)
    return states["current"], states["reset"]


def coordinate_action(source, target, record):
    # Only failures of the caller-supplied declaration are semantic negatives.
    # Construction of our own reference/state below must preserve its errors.
    try:
        value = validate_correspondence(record, source.to_payload(), target.to_payload())["payload"]
    except (V4IdentityError, V4SchemaError) as exc:
        raise EventAdmissionError(str(exc)) from exc
    vertices = {r["target_vertex_id"]: source.node_index(r["source_vertex_id"]) for r in value["vertex_map"]}
    edges = {r["target_edge_id"]: (source.live_edge_ids.index(r["source_edge_id"]), r["orientation"])
             for r in value["edge_map"]}
    return GraphCoordinateAction(source, target, tuple(vertices[n] for n in target.live_node_ids),
                                 tuple(edges[e][0] for e in target.live_edge_ids),
                                 tuple(edges[e][1] for e in target.live_edge_ids))


def signed_matrix(matrix, action):
    return tuple(tuple(_computed(action.edge_signs[i] * action.edge_signs[j] * matrix[a][b])
                       for j, b in enumerate(action.edge_permutation))
                 for i, a in enumerate(action.edge_permutation))


def coordinate_reference(source, action, backend=None):
    """Construct the exact reference action for the shipped constant-context recipes.

    The caller still declares/resolves a target; lifecycle requires exact equality
    with this reconstruction and full numerical admission, not hash similarity.
    """
    from .grc_v4_candidate_a import CandidateADifferentialReference
    from .grc_v4_profile import resolve_profile
    from .grc_v4_state import FrozenJSONMap
    if source.graph != action.source:
        raise EventAdmissionError("coordinate action source differs from reference")
    params, identity = deepcopy(source.profile.params_resolved.to_payload()), source.profile.identity_payload.to_payload()
    names = {source.graph.live_edge_ids[a]: action.target.live_edge_ids[i]
             for i, a in enumerate(action.edge_permutation)}
    remap = lambda values: {names[e]: v for e, v in values.items()}
    base = signed_matrix(source.K4_base, action)
    weights = remap(source.edge_weights.to_dict())
    params["geometry"]["K4_base_digest"] = payload_identity("k4_identity_payload",
        dict(schema_version="grcv4-k4-identity-v1", K4_base=[list(row) for row in base]))
    params["geometry"]["reference_hodge_digest"] = payload_identity("reference_hodge_identity_payload",
        dict(schema_version="grcv4-reference-hodge-identity-v1", edge_weights=weights))
    mapped_backend = None
    if source.profile.identity_payload.candidate == "C":
        candidate = params["candidate"]
        candidate["W_C_tr"] = remap(candidate["W_C_tr"])
        candidate["W_C_tr_content_digest"] = payload_identity("wctr_identity_payload",
            dict(schema_version="grcv4-wctr-identity-v1", W_C_tr=candidate["W_C_tr"]))
    else:
        if type(backend) is not CandidateADifferentialReference or backend.graph != source.graph:
            raise EventAdmissionError("coordinate action requires its source A backend")
        mapped_backend = CandidateADifferentialReference(action.target, backend.dimension,
            tuple(backend.positions[i] for i in action.vertex_permutation),
            FrozenJSONMap(remap(backend.reference_weights.to_dict())), backend.regularization)
        params["candidate"]["descriptor_backend_id"] = mapped_backend.identity
    identity["params_hash"] = payload_identity("resolved_params", params)
    return replace(source, graph=action.target, K4_base=base, edge_weights=FrozenJSONMap(weights),
                   profile=resolve_profile(params, identity)), mapped_backend


def map_representation(before, target, request, source_backend=None, target_backend=None):
    source = before.geometry.reference
    action = coordinate_action(source.graph, target.graph, request.correspondence.to_dict())
    expected, backend = coordinate_reference(source, action, source_backend)
    if expected != target or backend != target_backend:
        raise EventAdmissionError("target reference/profile/backend is not the declared coordinate action")
    def state(old):
        size = len(action.edge_permutation)
        z = None if old.Z_4 is None else signed_matrix(
            tuple(tuple(old.Z_4[i*size:(i+1)*size]) for i in range(size)), action)
        return GRCV4AuthoritativeState(tuple(old.C[i] for i in action.vertex_permutation),
            None if old.W_A is None else tuple(old.W_A[i] for i in action.edge_permutation),
            None if z is None else tuple(v for row in z for v in row))
    return replace(before, geometry=target.geometry(), context=target.context,
                   current=state(before.current), reset=state(before.reset))
