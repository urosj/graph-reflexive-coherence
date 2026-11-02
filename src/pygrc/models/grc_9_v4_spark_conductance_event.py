"""Exact A_OS histories: preserve every old W and seed three new edges at one."""

from hashlib import sha256

from .grc_v4_codec import canonical_json_bytes, payload_identity
from .grc_v4_spark_conductance import ExactConductanceState
from .grc_v4_spark_state import ExactResources


def archive(config):
    return {role: getattr(config, role).to_payload() for role in ("current", "reset")}


def history_policy(config):
    content = {
        "schema_version": "grcv4-exact-conductance-history-v1",
        "subject": "candidate",
        "content": archive(config),
    }
    candidate = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "candidate",
        "policy_id": "candidate_a_exact_old_edge_lineage_positive_bond_seed_v1",
        "disposition": "exact_transport",
        "information_loss": "none",
        "source_history_digest": "grcv4-history-content-sha256:"
        + sha256(canonical_json_bytes(content)).hexdigest(),
        "target_initializer_id": "grc9v4_new_internal_edge_positive_bond_seed_v1",
    }
    carrier = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "carrier",
        "policy_id": "carrier_not_applicable_v1",
        "disposition": "not_applicable",
        "information_loss": "none",
        "source_history_digest": None,
        "target_initializer_id": None,
    }
    return dict(
        schema_version="grc9v4-expansion-history-policy-v2",
        candidate=candidate,
        carrier=carrier,
        **{
            role + "_history_policy_digest": payload_identity(
                "history_channel_policy_identity_payload",
                {
                    "schema_version": "grcv4-history-channel-policy-identity-v1",
                    "policy": policy,
                },
            )
            for role, policy in (("candidate", candidate), ("carrier", carrier))
        },
    )


def capture(config, kernel):
    return {
        "policy_id": "preserve_old_W_seed_three_internal_edges_v1",
        "disposition": "exact_transport",
        "information_loss": "none",
        "source_archive": archive(config),
        "history_policy": history_policy(config),
        "source_edge_ids": list(config.reference.graph.live_edge_ids),
        "fresh_source_reads": {
            role: kernel.readmission(getattr(config, role)).to_dict()
            for role in ("current", "reset")
        },
    }


def target(state, graph, matrix):
    if type(state) is not ExactConductanceState:
        raise ValueError("both A_OS conductance histories required")
    old = dict(zip(state.graph.live_edge_ids, state.W_A, strict=True))
    if (
        not set(old) <= set(graph.live_edge_ids)
        or len(set(graph.live_edge_ids) - set(old)) != 3
    ):
        raise ValueError("complete old-edge lineage and three new edges required")
    resources = ExactResources.transfer(state, graph, matrix)
    return ExactConductanceState(
        graph,
        resources.C,
        resources.charge,
        tuple(old.get(edge, "1") for edge in graph.live_edge_ids),
    )
