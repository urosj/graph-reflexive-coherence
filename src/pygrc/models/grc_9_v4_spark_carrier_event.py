"""PC event history ownership: archive both roles, explicitly zero the full target."""

from hashlib import sha256

from .grc_v4_codec import canonical_json_bytes, payload_identity
from .grc_v4_spark_carrier import ExactCarrierState
from .grc_v4_spark_state import ExactResources


def archive(config):
    return {role: getattr(config, role).to_payload() for role in ("current", "reset")}


def history_policy(config):
    content = {
        "schema_version": "grcv4-exact-carrier-history-v1",
        "subject": "carrier",
        "content": archive(config),
    }
    candidate = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "candidate",
        "policy_id": "candidate_c_rederive_no_history_v1",
        "disposition": "rederived",
        "source_history_digest": None,
        "target_initializer_id": None,
        "information_loss": "none",
    }
    carrier = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "carrier",
        "policy_id": "whole_carrier_reset_with_loss_receipt_v1",
        "disposition": "whole_carrier_reset",
        "source_history_digest": "grcv4-history-content-sha256:"
        + sha256(canonical_json_bytes(content)).hexdigest(),
        "target_initializer_id": "zero_carrier_v1",
        "information_loss": "carrier_history_loss",
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
            for role, policy in [("candidate", candidate), ("carrier", carrier)]
        },
    )


def capture(config, kernel):
    return {
        "policy_id": "event_loss_and_zero_target_carrier_v1",
        "disposition": "whole_carrier_reset",
        "information_loss": "carrier_history_loss",
        "target_initializer_id": "canonical_zero_carrier_v1",
        "source_archive": archive(config),
        "history_policy": history_policy(config),
        "native_release": False,
        "fresh_source_reads": {
            role: kernel.readmission(getattr(config, role)).to_dict()
            for role in ("current", "reset")
        },
    }


def target(state, graph, matrix):
    if type(state) is not ExactCarrierState:
        raise ValueError("both PC histories required")
    return ExactCarrierState.zero(ExactResources.transfer(state, graph, matrix))
