"""A_PC event: preserve W lineage and explicitly archive/reset the full Z."""

from . import grc_9_v4_spark_carrier_event as carrier
from . import grc_9_v4_spark_conductance_event as conductance
from .grc_v4_spark_adaptive_carrier import ExactAdaptiveCarrierState
from .grc_v4_spark_conductance import ExactConductanceState


def history_policy(config):
    value = conductance.history_policy(config)
    z = carrier.history_policy(config)
    value["carrier"] = z["carrier"]
    value["carrier_history_policy_digest"] = z["carrier_history_policy_digest"]
    return value


def capture(config, kernel):
    # Both channel archives bind the entire C/W/Z subject, once per role.
    policy = history_policy(config)
    reads = {
        role: kernel.readmission(getattr(config, role)).to_dict()
        for role in ("current", "reset")
    }
    common = {
        "source_archive": conductance.archive(config),
        "history_policy": policy,
        "fresh_source_reads": reads,
    }
    w = dict(
        common,
        policy_id="preserve_old_W_seed_three_internal_edges_v1",
        disposition="exact_transport",
        information_loss="none",
        source_edge_ids=list(config.reference.graph.live_edge_ids),
    )
    z = dict(
        common,
        policy_id="event_loss_and_zero_target_carrier_v1",
        disposition="whole_carrier_reset",
        information_loss="carrier_history_loss",
        target_initializer_id="canonical_zero_carrier_v1",
        native_release=False,
    )
    return w, z


def target(state, graph, matrix):
    if type(state) is not ExactAdaptiveCarrierState:
        raise ValueError("both full A_PC histories required")
    cw = conductance.target(
        ExactConductanceState(state.graph, state.C, state.charge, state.W_A),
        graph,
        matrix,
    )
    m = len(graph.oriented_edges)
    return ExactAdaptiveCarrierState(
        graph, cw.C, cw.charge, cw.W_A, tuple(("0",) * m for _ in range(m))
    )
