"""LGRC9V3 causal-history constants, schema fields, and validation helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import math
from typing import Any, Final

from pygrc.core import (
    digest_canonical_data,
    EdgeId,
    InvalidParamsError,
    InvalidStateTransitionError,
    NodeId,
    SnapshotCompatibilityError,
)

from .grc_9_v3_state import GRC9V3State



LGRC9_FAMILY_PHASE: Final[str] = "LGRC-9"
LGRC9_RUNTIME_FAMILY: Final[str] = "LGRC9"
LGRCV3_FAMILY_PHASE: Final[str] = "LGRC-V3"
LGRCV3_RUNTIME_FAMILY: Final[str] = "LGRCV3"
LGRC9V3_RUNTIME_FAMILY: Final[str] = "LGRC9V3"

LGRC9V3_CAUSAL_MODES_KEY: Final[str] = "causal_history"
LGRC9V3_CAUSAL_ARTIFACT_KEY: Final[str] = "causal_history"

CAUSAL_LAYER_MODE_ANNOTATION: Final[str] = "annotation"
CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL: Final[str] = (
    "fixed_topology_semicausal"
)
CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY: Final[str] = (
    "packetized_fixed_topology"
)
CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY: Final[str] = (
    "topology_changing_causal_history"
)

LGRC_RUNTIME_LEVEL_LGRC0: Final[str] = "lgrc0"
LGRC_RUNTIME_LEVEL_LGRC1: Final[str] = "lgrc1"
LGRC_RUNTIME_LEVEL_LGRC2: Final[str] = "lgrc2"
LGRC_RUNTIME_LEVEL_LGRC3: Final[str] = "lgrc3"

LAPSE_POLICY_BOUNDED_DENSITY_TENSION: Final[str] = "bounded_density_tension"
# Unit lapse means N_i = 1 for every node; it is the lapse policy used by the
# synchronous-limit reduction test described in the LGRC-9 paper.
LAPSE_POLICY_UNIT: Final[str] = "unit"

EDGE_DELAY_POLICY_GEOMETRY_BASELINE: Final[str] = "geometry_baseline"
EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL: Final[str] = "grcv3_temporal_label"
EDGE_DELAY_POLICY_CONSTANT_DELAY: Final[str] = "constant_delay"

EVENT_TIME_POLICY_DERIVED_FROM_SYNCHRONOUS_STEP: Final[str] = (
    "derived_from_synchronous_step"
)
EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY: Final[str] = "explicit_event_time_key"
EVENT_TIME_POLICY_SYNCHRONOUS_LIMIT: Final[str] = "synchronous_limit"

PROPER_TIME_POLICY_ANNOTATION: Final[str] = "annotation"
PROPER_TIME_POLICY_GLOBAL_SCHEDULER: Final[str] = "global_scheduler"
PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER: Final[str] = "local_event_frontier"
PROPER_TIME_POLICY_SYNCHRONOUS_LIMIT: Final[str] = "synchronous_limit"

CAUSAL_DISTANCE_POLICY_EDGE_DELAY_SHORTEST_PATH: Final[str] = (
    "edge_delay_shortest_path"
)
CAUSAL_DISTANCE_POLICY_DISABLED: Final[str] = "disabled"

CAUSAL_CONE_POLICY_BOUNDED_SHORTEST_PATH: Final[str] = "bounded_shortest_path"
CAUSAL_CONE_POLICY_DISABLED: Final[str] = "disabled"

CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION: Final[str] = "derived_annotation"
CAUSAL_BASIN_CORE_POLICY_DISABLED: Final[str] = "disabled"

FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE: Final[str] = (
    "inverse_base_conductance"
)
FUNCTIONAL_DISTANCE_POLICY_INVERSE_FLUX_COUPLING: Final[str] = (
    "inverse_flux_coupling"
)
FUNCTIONAL_DISTANCE_POLICY_INVERSE_COMBINED_COUPLING: Final[str] = (
    "inverse_combined_coupling"
)

LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE: Final[str] = "lgrc0_causal_annotation"
LGRC9V3_DERIVED_EVIDENCE_CLASS: Final[str] = "derived_annotation"
LGRC9V3_CAUSAL_ARTIFACT_KIND: Final[str] = "lgrc9v3_causal_annotation"
LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_causal_annotation_v1"
)
LGRC9V3_ANNOTATION_MODE_VERSION: Final[str] = "lgrc0_annotation_v1"
LGRC9V3_LGRC1_DIAGNOSTIC_SOURCE: Final[str] = (
    "lgrc1_fixed_topology_eligibility"
)
LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS: Final[str] = "fixed_topology_semicausal"
LGRC9V3_LGRC1_ARTIFACT_KIND: Final[str] = "lgrc9v3_fixed_topology_eligibility"
LGRC9V3_LGRC1_ARTIFACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_fixed_topology_eligibility_v1"
)
LGRC9V3_LGRC1_MODE_VERSION: Final[str] = "lgrc1_fixed_topology_semicausal_v1"
LGRC9V3_LGRC2_PACKET_CONTRACT_KIND: Final[str] = "lgrc9v3_packet_contract"
LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_packet_contract_v1"
)
LGRC9V3_LGRC2_PACKET_LEDGER_KIND: Final[str] = "lgrc9v3_packet_ledger"
LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_packet_ledger_v1"
)
LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND: Final[str] = (
    "lgrc9v3_packet_processing_result"
)
LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_packet_processing_result_v1"
)
LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND: Final[str] = (
    "lgrc9v3_packet_arrival_eligibility"
)
LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_packet_arrival_eligibility_v1"
)
LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND: Final[str] = (
    "lgrc9v3_pending_flux_ledger"
)
LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_pending_flux_ledger_v1"
)
LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND: Final[str] = (
    "lgrc9v3_topology_contract"
)
LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_topology_contract_v1"
)
LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND: Final[str] = (
    "lgrc9v3_refinement_packet_transport_result"
)
LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_refinement_packet_transport_result_v1"
)
LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND: Final[str] = (
    "lgrc9v3_proper_time_inheritance_result"
)
LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_proper_time_inheritance_result_v1"
)
LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND: Final[str] = (
    "lgrc9v3_collapse_reabsorption_result"
)
LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_collapse_reabsorption_result_v1"
)
LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND: Final[str] = (
    "lgrc9v3_collapse_reabsorption_packet_transport_result"
)
LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_collapse_reabsorption_packet_transport_result_v1"
)
LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND: Final[str] = (
    "lgrc9v3_proper_time_identity_persistence_evaluation"
)
LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_proper_time_identity_persistence_evaluation_v1"
)
LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_proper_time_identity_acceptance_event_v1"
)
LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND: Final[str] = (
    "lgrc9v3_topology_event_replay_validation"
)
LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_topology_event_replay_validation_v1"
)
LGRC9V3_LGRC3_POLICY_CONTRACT_KIND: Final[str] = (
    "lgrc9v3_collapse_identity_policy_contract"
)
LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_collapse_identity_policy_contract_v1"
)
LGRC9V3_LGRC2_MODE_VERSION: Final[str] = "lgrc2_packetized_fixed_topology_v1"
LGRC9V3_LGRC3_MODE_VERSION: Final[str] = "lgrc3_topology_contract_v1"
LGRC9V3_PACKETIZED_EVIDENCE_CLASS: Final[str] = "packetized_causal_flux"
LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS: Final[str] = (
    "packet_arrival_eligibility"
)
LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS: Final[str] = "compact_pending_flux"
LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS: Final[str] = "topology_contract"
LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS: Final[str] = (
    "refinement_packet_transport"
)
LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS: Final[str] = (
    "proper_time_inheritance"
)
LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS: Final[str] = (
    "collapse_reabsorption"
)
LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS: Final[str] = (
    "collapse_reabsorption_packet_transport"
)
LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS: Final[str] = (
    "proper_time_identity_persistence_evaluation"
)
LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS: Final[str] = (
    "proper_time_identity_acceptance"
)
LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS: Final[str] = (
    "topology_event_replay_validation"
)
LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS: Final[str] = (
    "collapse_identity_policy_contract"
)
LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE: Final[str] = (
    "redirect_to_selected_sink_or_settle_self_loop"
)
LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT: Final[str] = (
    "exact_directed_channel_arrival_lineage"
)
LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT: Final[str] = (
    "uniform_parent_proper_time"
)
LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0: Final[str] = (
    "explicit_or_default_tau0"
)
LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY: Final[str] = (
    "selected_sink_clock_continuity"
)
LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP: Final[str] = (
    "explicit_lineage_transfer_map"
)
LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING: Final[str] = (
    "budget_conserving_transfer"
)
LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL: Final[str] = (
    "sink_local_proper_time"
)
LGRC9V3_IDENTITY_CLOCK_POLICY_LINEAGE: Final[str] = "lineage_proper_time"
LGRC9V3_IDENTITY_CLOCK_POLICY_BASIN_AGGREGATE: Final[str] = (
    "basin_aggregate_proper_time"
)
LGRC9V3_IDENTITY_CLOCK_POLICY_CAUSAL_FRONTIER: Final[str] = (
    "causal_frontier_time"
)
LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY: Final[str] = (
    "local_median_delay_multiplier"
)
LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER: Final[float] = 4.0

LGRC9V3_PACKET_EVENT_KIND_DEPARTURE: Final[str] = "lgrc9v3_packet_departure"
LGRC9V3_PACKET_EVENT_KIND_ARRIVAL: Final[str] = "lgrc9v3_packet_arrival"
LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT: Final[str] = (
    "lgrc9v3_refinement_topology_event"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT: Final[str] = (
    "lgrc9v3_refinement_packet_transport"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE: Final[str] = (
    "lgrc9v3_proper_time_inheritance"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE: Final[str] = (
    "lgrc9v3_causal_collapse"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION: Final[str] = (
    "lgrc9v3_causal_reabsorption"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE: Final[str] = (
    "lgrc9v3_proper_time_identity_acceptance"
)
LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH: Final[str] = (
    "lgrc9v3_causal_boundary_birth"
)
LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY: Final[str] = (
    "event_time_key_then_scheduler_event_index_then_event_id"
)
LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED: Final[str] = (
    "departure_plus_edge_causal_delay"
)
LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT: Final[str] = (
    "explicit_for_fixture_or_replay"
)

LGRC9V3_PACKET_STATE_SCHEDULED: Final[str] = "scheduled"
LGRC9V3_PACKET_STATE_IN_FLIGHT: Final[str] = "in_flight"
LGRC9V3_PACKET_STATE_ARRIVED: Final[str] = "arrived"
LGRC9V3_PACKET_STATE_CANCELLED: Final[str] = "cancelled"

LGRC9V3_PACKET_BUDGET_INVARIANT: Final[str] = "sum_node_coherence_plus_packets"
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX: Final[str] = (
    "grc9v3_outward_flux_probability"
)
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT: Final[str] = (
    "parent_debit"
)
LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0: Final[str] = (
    "explicit_or_tau0"
)

LGRC9V3_AUTONOMOUS_PRODUCER_CONTRACT_KIND: Final[str] = (
    "lgrc9v3_autonomous_event_production_contract"
)
LGRC9V3_AUTONOMOUS_PRODUCER_CONTRACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_autonomous_event_production_contract_v1"
)
LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_KIND: Final[str] = (
    "lgrc9v3_autonomous_event_production_result"
)
LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_autonomous_event_production_result_v1"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_KIND: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_contract"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_contract_v1"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_row"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_row_v1"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_lineage_record"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_lineage_record_v1"
)
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND: Final[str] = (
    "lgrc9v3_topology_state_reabsorption_record"
)
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_topology_state_reabsorption_record_v1"
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND: Final[str] = (
    "lgrc9v3_native_route_candidate_record"
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_native_route_candidate_record_v1"
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND: Final[str] = (
    "lgrc9v3_native_route_candidate_set_record"
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_native_route_candidate_set_record_v1"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND: Final[str] = (
    "lgrc9v3_native_route_arbitration_record"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_native_route_arbitration_record_v1"
)
LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_KIND: Final[str] = (
    "lgrc9v3_multi_basin_post_refinement_flow_window_record"
)
LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_multi_basin_post_refinement_flow_window_record_v1"
)
LGRC9V3_CHILD_BASIN_STATE_RECORD_KIND: Final[str] = (
    "lgrc9v3_child_basin_state_record"
)
LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_child_basin_state_record_v1"
)
LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_KIND: Final[str] = (
    "lgrc9v3_multi_basin_replay_validation_record"
)
LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_multi_basin_replay_validation_record_v1"
)
LGRC9V3_MULTI_BASIN_CONTROL_RECORD_KIND: Final[str] = (
    "lgrc9v3_multi_basin_merge_leakage_control_record"
)
LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION: Final[str] = (
    "lgrc9v3_multi_basin_merge_leakage_control_record_v1"
)
LGRC9V3_ROUTE_ASPECT_KIND: Final[str] = "lgrc9v3_route_aspect"
LGRC9V3_ROUTE_ASPECT_SCHEMA_VERSION: Final[str] = "lgrc9v3_route_aspect_v1"
LGRC9V3_ROUTE_ASPECT_EVIDENCE_CLASS: Final[str] = "route_aspect_contract"
LGRC9V3_ROUTE_ASPECT_DIRECTION_CLOCKWISE: Final[str] = "clockwise"
LGRC9V3_ROUTE_ASPECT_DIRECTION_COUNTER_CLOCKWISE: Final[str] = "counter_clockwise"
LGRC9V3_ROUTE_ASPECT_DIRECTION_CUSTOM: Final[str] = "custom"
LGRC9V3_ROUTE_ASPECT_DIRECTIONS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_ROUTE_ASPECT_DIRECTION_CLOCKWISE,
        LGRC9V3_ROUTE_ASPECT_DIRECTION_COUNTER_CLOCKWISE,
        LGRC9V3_ROUTE_ASPECT_DIRECTION_CUSTOM,
    }
)
LGRC9V3_AUTONOMY_MODE_VERSION: Final[str] = "lgrc9v3_autonomy_v1"
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_MODE_VERSION: Final[str] = (
    "lgrc9v3_causal_pulse_substrate_surface_v1"
)
LGRC9V3_AUTONOMOUS_PRODUCER_EVIDENCE_CLASS: Final[str] = (
    "autonomous_event_production"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_EVIDENCE_CLASS: Final[str] = (
    "causal_pulse_substrate_surface"
)
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE: Final[str] = (
    "packet_departure_from_flux_route_policy"
)
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS: Final[str] = (
    "packet_departure_from_route_aspect_surplus_policy"
)
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL: Final[str] = (
    "boundary_birth_trial_policy"
)
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING: Final[
    str
] = "packet_departure_from_pulse_substrate_coupling_policy"
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY: Final[
    str
] = "packet_departure_from_feedback_eligibility_policy"
LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1: Final[str] = "bounded_lgrc9v3_v1"
LGRC9V3_AUTONOMOUS_PRODUCER_QUEUE_OWNERSHIP_POLICY: Final[str] = (
    "producers_enqueue_step_consumes"
)
LGRC9V3_AUTONOMOUS_PRODUCER_IDEMPOTENCY_POLICY: Final[str] = (
    "causal_surface_digest_once"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY: Final[str] = (
    "producer_policy_disabled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_POLICY_NOT_IMPLEMENTED: Final[str] = (
    "producer_policy_not_implemented"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK: Final[str] = (
    "no_eligible_work"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP: Final[str] = (
    "idempotent_causal_surface_already_produced"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED: Final[str] = (
    "packet_departure_scheduled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED: Final[str] = (
    "surplus_trigger_packet_departure_scheduled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD: Final[str] = (
    "surplus_trigger_subthreshold"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED: Final[str] = (
    "boundary_birth_trial_scheduled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED: Final[str] = (
    "pulse_substrate_coupling_disabled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD: Final[
    str
] = "pulse_substrate_coupling_subthreshold"
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED: Final[str] = (
    "pulse_substrate_coupling_packet_departure_scheduled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED: Final[str] = (
    "feedback_coupled_pulse_disabled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD: Final[str] = (
    "feedback_coupled_pulse_subthreshold"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY: Final[str] = (
    "feedback_coupled_pulse_wrong_polarity"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH: Final[str] = (
    "feedback_coupled_pulse_order_mismatch"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED: Final[str] = (
    "feedback_coupled_pulse_packet_departure_scheduled"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED: Final[str] = (
    "surface_row_superseded_by_topology_event"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED: Final[str] = (
    "producer_stale_surface_read_blocked"
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED: Final[
    str
] = "topology_state_reabsorption_required_before_producer_scheduling"
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS: Final[str] = (
    "emit_committed_packet_contact_rows"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED: Final[str] = (
    "disabled"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE: Final[
    str
] = "transport_or_supersede_committed_topology_events"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE: Final[str] = (
    "lineage_rebase_active_state_and_packet_ledger"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES: Final[str] = (
    "score_ordered_topology_route_candidates"
)
LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED: Final[str] = "disabled"
LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY: Final[str] = (
    "post_refinement_child_basin_replay"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE: Final[str] = (
    "native_route_arbitration_selected_highest_score"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE: Final[
    str
] = "native_route_arbitration_selected_declared_local_preference"
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES: Final[str] = (
    "native_route_arbitration_no_candidates"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE: Final[str] = (
    "native_route_arbitration_unresolved_tie"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED: Final[str] = (
    "native_route_arbitration_policy_disabled"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID: Final[str] = (
    "native_route_arbitration_budget_invalid"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID: Final[str] = (
    "native_route_arbitration_order_invalid"
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED: Final[str] = (
    "native_route_arbitration_hidden_input_rejected"
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID: Final[
    str
] = "score_desc_then_candidate_id"
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING: Final[str] = (
    "digest_ascending"
)
LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED: Final[str] = "fail_closed"
LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER: Final[str] = (
    "declared_runtime_visible_tiebreaker"
)
LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE: Final[str] = "collapse"
LGRC9V3_NATIVE_ROUTE_INTENT_REABSORB: Final[str] = "reabsorb"
LGRC9V3_NATIVE_ROUTE_INTENT_SPLIT: Final[str] = "split"
LGRC9V3_NATIVE_ROUTE_INTENT_MERGE: Final[str] = "merge"
LGRC9V3_NATIVE_ROUTE_INTENT_REDIRECT: Final[str] = "redirect"
LGRC9V3_MULTI_BASIN_REPLAY_STATUS_PASSED: Final[str] = "passed"
LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_CLOSED: Final[str] = "failed_closed"
LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_OPEN: Final[str] = "failed_open"
LGRC9V3_MULTI_BASIN_REPLAY_STATUS_NOT_RUN: Final[str] = "not_run"
LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_CLOSED: Final[str] = "failed_closed"
LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_OPEN: Final[str] = "failed_open"
LGRC9V3_MULTI_BASIN_CONTROL_STATUS_PASSED: Final[str] = "passed"
LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATIVE_SOURCE_CURRENT: Final[str] = (
    "native_source_current"
)
LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_PRODUCER_ASSISTED: Final[str] = (
    "producer_assisted"
)
LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATURALIZATION_DEBT: Final[str] = (
    "naturalization_debt"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED: Final[str] = (
    "replay_declared_surface_update_policy"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION: Final[str] = (
    "surface_update_policy_v1"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY: Final[str] = "node_only"
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE: Final[str] = (
    "derived_surface_accounting"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY: Final[str] = (
    "fixed_topology"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED: Final[str] = (
    "topology_lineage_deferred"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED: Final[str] = (
    "transported_topology_lineage"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED: Final[str] = (
    "superseded_by_topology_event"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED: Final[str] = (
    "transported"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED: Final[str] = (
    "superseded"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3: Final[str] = (
    "surface_lineage_transport_requires_lgrc3"
)
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED: Final[str] = "rebased"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED: Final[str] = "merged"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_SUPERSEDED: Final[str] = "superseded"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REJECTED: Final[str] = "rejected"
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3: Final[str] = (
    "topology_state_reabsorption_requires_lgrc3"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS: Final[str] = (
    "local_support_mass"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE: Final[str] = (
    "boundary_polarity_score"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE: Final[str] = (
    "proper_time_phase"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION: Final[str] = (
    "surface_deformation"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT: Final[str] = (
    "route_local_pulse_contact"
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY: Final[str] = (
    "feedback_eligibility"
)

_ALLOWED_CAUSAL_LAYER_MODES: Final[frozenset[str]] = frozenset(
    {
        CAUSAL_LAYER_MODE_ANNOTATION,
        CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL,
        CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
        CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    }
)
_ALLOWED_RUNTIME_LEVELS: Final[frozenset[str]] = frozenset(
    {
        LGRC_RUNTIME_LEVEL_LGRC0,
        LGRC_RUNTIME_LEVEL_LGRC1,
        LGRC_RUNTIME_LEVEL_LGRC2,
        LGRC_RUNTIME_LEVEL_LGRC3,
    }
)
_ALLOWED_LAPSE_POLICIES: Final[frozenset[str]] = frozenset(
    {LAPSE_POLICY_BOUNDED_DENSITY_TENSION, LAPSE_POLICY_UNIT}
)
_ALLOWED_EDGE_DELAY_POLICIES: Final[frozenset[str]] = frozenset(
    {
        EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
        EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL,
        EDGE_DELAY_POLICY_CONSTANT_DELAY,
    }
)
_ALLOWED_EVENT_TIME_POLICIES: Final[frozenset[str]] = frozenset(
    {
        EVENT_TIME_POLICY_DERIVED_FROM_SYNCHRONOUS_STEP,
        EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY,
        EVENT_TIME_POLICY_SYNCHRONOUS_LIMIT,
    }
)
_ALLOWED_PROPER_TIME_POLICIES: Final[frozenset[str]] = frozenset(
    {
        PROPER_TIME_POLICY_ANNOTATION,
        PROPER_TIME_POLICY_GLOBAL_SCHEDULER,
        PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER,
        PROPER_TIME_POLICY_SYNCHRONOUS_LIMIT,
    }
)
_ALLOWED_CAUSAL_DISTANCE_POLICIES: Final[frozenset[str]] = frozenset(
    {
        CAUSAL_DISTANCE_POLICY_EDGE_DELAY_SHORTEST_PATH,
        CAUSAL_DISTANCE_POLICY_DISABLED,
    }
)
_ALLOWED_CAUSAL_CONE_POLICIES: Final[frozenset[str]] = frozenset(
    {CAUSAL_CONE_POLICY_BOUNDED_SHORTEST_PATH, CAUSAL_CONE_POLICY_DISABLED}
)
_ALLOWED_CAUSAL_BASIN_CORE_POLICIES: Final[frozenset[str]] = frozenset(
    {
        CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION,
        CAUSAL_BASIN_CORE_POLICY_DISABLED,
    }
)
_ALLOWED_FUNCTIONAL_DISTANCE_POLICIES: Final[frozenset[str]] = frozenset(
    {
        FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE,
        FUNCTIONAL_DISTANCE_POLICY_INVERSE_FLUX_COUPLING,
        FUNCTIONAL_DISTANCE_POLICY_INVERSE_COMBINED_COUPLING,
    }
)
_ALLOWED_CAUSAL_BOUNDARY_BIRTH_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED,
        LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    }
)
_ALLOWED_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCES: Final[frozenset[str]] = (
    frozenset({LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT})
)
_ALLOWED_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICIES: Final[frozenset[str]] = (
    frozenset({LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0})
)
LGRC9V3_AUTONOMOUS_PRODUCER_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
        LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    }
)
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_CODES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_POLICY_NOT_IMPLEMENTED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED,
        LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICIES: Final[
    frozenset[str]
] = frozenset(
    {
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE,
    }
)
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED,
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE,
    }
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    }
)
LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED,
        LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY,
    }
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_CODES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    }
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_SELECTED_REASON_CODES: Final[frozenset[str]] = (
    frozenset(
        {
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE,
        }
    )
)
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_KEYS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
        LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING,
    }
)
LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
        LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER,
    }
)
LGRC9V3_NATIVE_ROUTE_INTENTS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        LGRC9V3_NATIVE_ROUTE_INTENT_REABSORB,
        LGRC9V3_NATIVE_ROUTE_INTENT_SPLIT,
        LGRC9V3_NATIVE_ROUTE_INTENT_MERGE,
        LGRC9V3_NATIVE_ROUTE_INTENT_REDIRECT,
    }
)
LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS: Final[frozenset[str]] = (
    frozenset(
        {
            "hidden_fixture_array",
            "hidden_fixture_state",
            "experiment_if_else",
            "preselected_sink_id",
            "posthoc_threshold",
            "report_code",
        }
    )
)
LGRC9V3_MULTI_BASIN_REPLAY_STATUSES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_MULTI_BASIN_REPLAY_STATUS_PASSED,
        LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_CLOSED,
        LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_OPEN,
        LGRC9V3_MULTI_BASIN_REPLAY_STATUS_NOT_RUN,
    }
)
LGRC9V3_MULTI_BASIN_CONTROL_STATUSES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_MULTI_BASIN_CONTROL_STATUS_PASSED,
        LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_CLOSED,
        LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_OPEN,
    }
)
LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_CLASSES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATIVE_SOURCE_CURRENT,
        LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_PRODUCER_ASSISTED,
        LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATURALIZATION_DEBT,
    }
)
LGRC9V3_MULTI_BASIN_FORBIDDEN_INPUTS: Final[frozenset[str]] = frozenset(
    set(LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS)
    | {
        "hidden_fixture_basin",
        "label_only_child_basin",
        "old_basin_thickening_as_child_basin",
        "old_basin_thickening_only",
        "transient_flow_sink_as_child_basin",
        "transient_flow_sink",
        "merge_leakage_as_success",
        "hidden_producer_basin_insertion",
        "producer_assisted_success_as_native_upgrade",
        "producer_success_as_native_upgrade",
        "post_hoc_membership_selection",
        "posthoc_membership_selection",
    }
)
LGRC9V3_MULTI_BASIN_FORBIDDEN_CLAIM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "claim_promotion",
        "movement_claim_allowed",
        "loop_driven_movement_claim_allowed",
        "locomotion_like_claim_allowed",
        "adaptive_topology_entry_allowed",
        "native_m6",
        "biological_claim_allowed",
        "agency_claim_allowed",
        "semantic_choice_claim_allowed",
        "choice_or_agency_claim_allowed",
        "native_lgrc_choice_selection_claim_allowed",
        "rc_identity_collapse_claim_allowed",
        "rc_identity_through_topology_claim_allowed",
        "identity_acceptance_claim_allowed",
        "topology_mutating_movement_claim_allowed",
        "unrestricted_movement_claim_allowed",
        "native_multi_basin_formation_claim_allowed",
        "BF6_claim_allowed",
        "independent_new_basin_claim_allowed",
        "semantic_learning_claim_allowed",
        "native_support_claim_allowed",
        "sentience_claim_allowed",
        "organism_life_claim_allowed",
        "ant_ecology_claim_allowed",
        "unrestricted_autonomy_claim_allowed",
        "phase8_completion_claim_allowed",
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KINDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_SURFACES: Final[
    frozenset[str]
] = frozenset(
    {
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_STATUSES: Final[frozenset[str]] = (
    frozenset(
        {
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED,
        }
    )
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED,
    }
)
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_SUPERSEDED,
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REJECTED,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS: Final[frozenset[str]] = (
    frozenset(
        {
            "hidden_fixture_state",
            "hidden_fixture_array",
            "preauthored_itinerary",
            "scripted_peak_sequence",
            "node_coherence",
            "packet_coherence",
            "node_coherence_total",
            "in_flight_packet_total",
            "conserved_budget_total",
            "node_plus_packet_budget",
            "support_mask",
            "centroid",
            "displacement",
            "topology",
            "direct_centroid_write",
            "direct_support_mask_write",
            "direct_displacement_write",
            "direct_topology_write",
            "claim_promotion",
            "movement_claim_allowed",
            "loop_driven_movement_claim_allowed",
            "locomotion_like_claim_allowed",
            "adaptive_topology_entry_allowed",
            "native_m6",
            "biological_claim_allowed",
            "agency_claim_allowed",
            "semantic_choice_claim_allowed",
            "choice_or_agency_claim_allowed",
            "native_lgrc_choice_selection_claim_allowed",
            "rc_identity_collapse_claim_allowed",
            "rc_identity_through_topology_claim_allowed",
            "identity_acceptance_claim_allowed",
            "topology_mutating_movement_claim_allowed",
            "unrestricted_movement_claim_allowed",
        }
    )
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_PRODUCER_WRITABLE_FIELDS: Final[
    frozenset[str]
] = frozenset({"producer_records", "scheduling_eligibility"})
LGRC9V3_PACKET_EVENT_KINDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
        LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
    }
)
LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH,
        LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT,
        LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT,
        LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE,
    }
)
LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE: Final[frozenset[str]] = (
    frozenset(
        {
            LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
            LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION,
            LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
        }
    )
)
LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS: Final[frozenset[str]] = frozenset(
    set(LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE)
    | set(LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE)
)
LGRC9V3_PACKET_STATES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_PACKET_STATE_SCHEDULED,
        LGRC9V3_PACKET_STATE_IN_FLIGHT,
        LGRC9V3_PACKET_STATE_ARRIVED,
        LGRC9V3_PACKET_STATE_CANCELLED,
    }
)
LGRC9V3_PROPER_TIME_TRANSFER_POLICIES: Final[frozenset[str]] = frozenset(
    {LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY}
)
LGRC9V3_LINEAGE_TRANSFER_POLICIES: Final[frozenset[str]] = frozenset(
    {LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP}
)
LGRC9V3_BUDGET_TRANSFER_POLICIES: Final[frozenset[str]] = frozenset(
    {LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING}
)
LGRC9V3_IDENTITY_CLOCK_POLICIES: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
        LGRC9V3_IDENTITY_CLOCK_POLICY_LINEAGE,
        LGRC9V3_IDENTITY_CLOCK_POLICY_BASIN_AGGREGATE,
        LGRC9V3_IDENTITY_CLOCK_POLICY_CAUSAL_FRONTIER,
    }
)
LGRC9V3_IDENTITY_THRESHOLD_POLICIES: Final[frozenset[str]] = frozenset(
    {LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY}
)


@dataclass(frozen=True)
class LGRC9V3PacketFieldNames:
    """Stable serialized field names for LGRC-2 packet records."""

    packet_id: str = "packet_id"
    packet_state: str = "packet_state"
    source_node_id: str = "source_node_id"
    target_node_id: str = "target_node_id"
    edge_id: str = "edge_id"
    amount: str = "amount"
    departure_event_id: str = "departure_event_id"
    arrival_event_id: str = "arrival_event_id"
    departure_event_time_key: str = "departure_event_time_key"
    arrival_event_time_key: str = "arrival_event_time_key"
    departure_scheduler_event_index: str = "departure_scheduler_event_index"
    arrival_scheduler_event_index: str = "arrival_scheduler_event_index"
    source_lineage_id: str = "source_lineage_id"
    target_lineage_id: str = "target_lineage_id"


@dataclass(frozen=True)
class LGRC9V3PacketLedgerFieldNames:
    """Stable serialized field names for LGRC-2 packet ledger artifacts."""

    packet_records: str = "packet_records"
    packet_event_records: str = "packet_event_records"
    event_queue_records: str = "event_queue_records"
    event_queue_tie_break_policy: str = "event_queue_tie_break_policy"
    packet_budget_invariant: str = "packet_budget_invariant"
    node_coherence_total: str = "node_coherence_total"
    in_flight_packet_total: str = "in_flight_packet_total"
    conserved_budget_total: str = "conserved_budget_total"
    budget_before: str = "budget_before"
    budget_after: str = "budget_after"
    budget_error: str = "budget_error"
    fixed_topology_signature: str = "fixed_topology_signature"


@dataclass(frozen=True)
class LGRC9V3PendingFluxFieldNames:
    """Stable serialized field names for compact pending-flux entries."""

    entry_id: str = "entry_id"
    source_node_id: str = "source_node_id"
    target_node_id: str = "target_node_id"
    edge_id: str = "edge_id"
    arrival_event_time_key: str = "arrival_event_time_key"
    source_lineage_id: str = "source_lineage_id"
    target_lineage_id: str = "target_lineage_id"
    amount_total: str = "amount_total"
    packet_count: str = "packet_count"
    packet_ids: str = "packet_ids"
    departure_event_time_keys: str = "departure_event_time_keys"


@dataclass(frozen=True)
class LGRC9V3TopologyContractFieldNames:
    """Stable serialized field names for the LGRC-3 topology contract."""

    topology_event_id: str = "topology_event_id"
    topology_event_kind: str = "topology_event_kind"
    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    event_time_key: str = "event_time_key"
    source_candidate_event_id: str = "source_candidate_event_id"
    source_expansion_event_id: str = "source_expansion_event_id"
    pre_topology_signature: str = "pre_topology_signature"
    post_topology_signature: str = "post_topology_signature"
    refinement_lineage_map: str = "refinement_lineage_map"
    expanded_node_id: str = "expanded_node_id"
    parent_node_id: str = "parent_node_id"
    child_node_id: str = "child_node_id"
    replacement_node_ids: str = "replacement_node_ids"
    internal_edge_ids: str = "internal_edge_ids"
    parent_to_child_node_lineage: str = "parent_to_child_node_lineage"
    boundary_reassignment_map: str = "boundary_reassignment_map"
    old_parent_port: str = "old_parent_port"
    new_endpoint_port: str = "new_endpoint_port"
    old_parent_column: str = "old_parent_column"
    new_endpoint_column: str = "new_endpoint_column"
    packet_transport_records: str = "packet_transport_records"
    source_packet_ids: str = "source_packet_ids"
    source_pending_flux_entry_ids: str = "source_pending_flux_entry_ids"
    transported_packet_ids: str = "transported_packet_ids"
    amount_total: str = "amount_total"
    proper_time_inheritance_records: str = "proper_time_inheritance_records"
    parent_proper_time: str = "parent_proper_time"
    child_proper_time: str = "child_proper_time"
    internal_edge_delay: str = "internal_edge_delay"
    proper_time_inheritance_policy: str = "proper_time_inheritance_policy"
    internal_edge_delay_policy: str = "internal_edge_delay_policy"
    budget_before: str = "budget_before"
    budget_after: str = "budget_after"
    budget_error: str = "budget_error"
    identity_acceptance_emitted: str = "identity_acceptance_emitted"


@dataclass(frozen=True)
class LGRC9V3PacketTransportFieldNames:
    """Stable serialized field names for LGRC-3 packet transport records."""

    transport_record_id: str = "transport_record_id"
    source_packet_id: str = "source_packet_id"
    transported_packet_id: str = "transported_packet_id"
    source_pending_flux_entry_ids: str = "source_pending_flux_entry_ids"
    packet_state: str = "packet_state"
    amount: str = "amount"
    edge_id: str = "edge_id"
    source_node_id_before: str = "source_node_id_before"
    source_node_id_after: str = "source_node_id_after"
    target_node_id_before: str = "target_node_id_before"
    target_node_id_after: str = "target_node_id_after"
    source_lineage_id_before: str = "source_lineage_id_before"
    source_lineage_id_after: str = "source_lineage_id_after"
    target_lineage_id_before: str = "target_lineage_id_before"
    target_lineage_id_after: str = "target_lineage_id_after"
    endpoint_transported: str = "endpoint_transported"
    old_parent_port: str = "old_parent_port"
    new_endpoint_port: str = "new_endpoint_port"
    old_parent_column: str = "old_parent_column"
    new_endpoint_column: str = "new_endpoint_column"


@dataclass(frozen=True)
class LGRC9V3CollapseReabsorptionFieldNames:
    """Stable serialized field names for future collapse/reabsorption events."""

    topology_event_id: str = "topology_event_id"
    topology_event_kind: str = "topology_event_kind"
    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    event_time_key: str = "event_time_key"
    node_proper_time: str = "node_proper_time"
    competing_sink_ids: str = "competing_sink_ids"
    selected_sink_id: str = "selected_sink_id"
    losing_sink_ids: str = "losing_sink_ids"
    lineage_transfer_map: str = "lineage_transfer_map"
    source_lineage_ids: str = "source_lineage_ids"
    target_lineage_id: str = "target_lineage_id"
    transferred_node_ids: str = "transferred_node_ids"
    transferred_packet_ids: str = "transferred_packet_ids"
    transferred_pending_flux_entry_ids: str = "transferred_pending_flux_entry_ids"
    coherence_transfer_amount: str = "coherence_transfer_amount"
    budget_before: str = "budget_before"
    budget_after: str = "budget_after"
    budget_error: str = "budget_error"
    budget_transfer_policy: str = "budget_transfer_policy"
    lineage_transfer_policy: str = "lineage_transfer_policy"
    proper_time_transfer_policy: str = "proper_time_transfer_policy"
    identity_acceptance_emitted: str = "identity_acceptance_emitted"


@dataclass(frozen=True)
class LGRC9V3ProperTimeIdentityFieldNames:
    """Stable serialized field names for future proper-time identity events."""

    topology_event_id: str = "topology_event_id"
    topology_event_kind: str = "topology_event_kind"
    source_topology_event_ids: str = "source_topology_event_ids"
    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    event_time_key: str = "event_time_key"
    sink_node_id: str = "sink_node_id"
    lineage_id: str = "lineage_id"
    basin_node_ids: str = "basin_node_ids"
    identity_clock_policy: str = "identity_clock_policy"
    threshold_calibration_policy: str = "threshold_calibration_policy"
    proper_time_persistence_threshold: str = "proper_time_persistence_threshold"
    threshold_multiplier: str = "threshold_multiplier"
    local_median_edge_delay: str = "local_median_edge_delay"
    window_start_event_time_key: str = "window_start_event_time_key"
    window_end_event_time_key: str = "window_end_event_time_key"
    observed_persistence_duration: str = "observed_persistence_duration"
    budget_before: str = "budget_before"
    budget_after: str = "budget_after"
    budget_error: str = "budget_error"
    identity_acceptance_allowed: str = "identity_acceptance_allowed"
    identity_acceptance_emitted: str = "identity_acceptance_emitted"


@dataclass(frozen=True)
class LGRC9V3AutonomousProducerFieldNames:
    """Stable field names for autonomous producer evidence records."""

    producer_policy: str = "producer_policy"
    producer_version: str = "producer_version"
    reason_code: str = "reason_code"
    trigger_node_id: str = "trigger_node_id"
    trigger_edge_id: str = "trigger_edge_id"
    thresholds: str = "thresholds"
    observed_evidence: str = "observed_evidence"
    scheduled_event_kind: str = "scheduled_event_kind"
    scheduled_event_time_key: str = "scheduled_event_time_key"
    scheduled_event_id: str = "scheduled_event_id"
    causal_surface_digest: str = "causal_surface_digest"
    idempotency_key: str = "idempotency_key"
    queued_work_consumed: str = "queued_work_consumed"
    topology_mutated: str = "topology_mutated"


@dataclass(frozen=True)
class LGRC9V3CausalPulseSubstrateSurfaceFieldNames:
    """Stable serialized field names for causal pulse-substrate surface rows."""

    surface_id: str = "surface_id"
    schema_version: str = "schema_version"
    surface_policy_id: str = "surface_policy_id"
    surface_policy_enabled: str = "surface_policy_enabled"
    surface_policy_validated: str = "surface_policy_validated"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    route_aspect_id: str = "route_aspect_id"
    route_aspect_digest: str = "route_aspect_digest"
    pulse_event_id: str = "pulse_event_id"
    pulse_packet_id: str = "pulse_packet_id"
    pulse_event_kind: str = "pulse_event_kind"
    pulse_channel_id: str = "pulse_channel_id"
    pulse_route_step: str = "pulse_route_step"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    node_proper_time: str = "node_proper_time"
    source_node_id: str = "source_node_id"
    target_node_id: str = "target_node_id"
    contact_amount: str = "contact_amount"
    surface_state_id: str = "surface_state_id"
    surface_state_digest: str = "surface_state_digest"
    surface_kind: str = "surface_kind"
    surface_nodes: str = "surface_nodes"
    surface_values_before: str = "surface_values_before"
    surface_values_after: str = "surface_values_after"
    runtime_visible_inputs: str = "runtime_visible_inputs"
    surface_update_policy: str = "surface_update_policy"
    surface_budget_surface: str = "surface_budget_surface"
    surface_budget_before: str = "surface_budget_before"
    surface_budget_after: str = "surface_budget_after"
    surface_budget_error: str = "surface_budget_error"
    lineage_status: str = "lineage_status"
    producer_records: str = "producer_records"
    claim_flags: str = "claim_flags"
    surface_digest: str = "surface_digest"


@dataclass(frozen=True)
class LGRC9V3CausalPulseSubstrateSurfaceLineageFieldNames:
    """Stable serialized field names for surface lineage records."""

    surface_lineage_record_id: str = "surface_lineage_record_id"
    schema_version: str = "schema_version"
    surface_lineage_policy_id: str = "surface_lineage_policy_id"
    surface_lineage_transport_enabled: str = "surface_lineage_transport_enabled"
    surface_lineage_transport_validated: str = "surface_lineage_transport_validated"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    causal_layer_mode: str = "causal_layer_mode"
    source_surface_id: str = "source_surface_id"
    source_surface_digest: str = "source_surface_digest"
    topology_event_id: str = "topology_event_id"
    topology_event_kind: str = "topology_event_kind"
    topology_event_digest: str = "topology_event_digest"
    topology_event_committed: str = "topology_event_committed"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    lineage_transfer_map: str = "lineage_transfer_map"
    lineage_transfer_map_digest: str = "lineage_transfer_map_digest"
    source_surface_nodes: str = "source_surface_nodes"
    target_surface_nodes: str = "target_surface_nodes"
    source_surface_ports: str = "source_surface_ports"
    target_surface_ports: str = "target_surface_ports"
    lineage_action: str = "lineage_action"
    lineage_status: str = "lineage_status"
    surface_budget_surface: str = "surface_budget_surface"
    surface_budget_before: str = "surface_budget_before"
    surface_budget_after: str = "surface_budget_after"
    surface_budget_error: str = "surface_budget_error"
    node_plus_packet_budget_before: str = "node_plus_packet_budget_before"
    node_plus_packet_budget_after: str = "node_plus_packet_budget_after"
    node_plus_packet_budget_error: str = "node_plus_packet_budget_error"
    transported_surface_id: str = "transported_surface_id"
    transported_surface_digest: str = "transported_surface_digest"
    superseded_surface_id: str = "superseded_surface_id"
    producer_stale_read_blocker: str = "producer_stale_read_blocker"
    claim_flags: str = "claim_flags"
    idempotency_key: str = "idempotency_key"
    lineage_record_digest: str = "lineage_record_digest"


@dataclass(frozen=True)
class LGRC9V3TopologyStateReabsorptionFieldNames:
    """Stable serialized field names for topology-state reabsorption records."""

    topology_state_reabsorption_record_id: str = (
        "topology_state_reabsorption_record_id"
    )
    schema_version: str = "schema_version"
    topology_state_reabsorption_policy_id: str = (
        "topology_state_reabsorption_policy_id"
    )
    topology_state_reabsorption_enabled: str = (
        "topology_state_reabsorption_enabled"
    )
    topology_state_reabsorption_validated: str = (
        "topology_state_reabsorption_validated"
    )
    lgrc_runtime_level: str = "lgrc_runtime_level"
    causal_layer_mode: str = "causal_layer_mode"
    topology_event_id: str = "topology_event_id"
    topology_event_kind: str = "topology_event_kind"
    topology_event_digest: str = "topology_event_digest"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    lineage_transfer_map: str = "lineage_transfer_map"
    lineage_transfer_map_digest: str = "lineage_transfer_map_digest"
    source_node_ids: str = "source_node_ids"
    target_node_ids: str = "target_node_ids"
    retired_node_ids: str = "retired_node_ids"
    source_edge_ids: str = "source_edge_ids"
    target_edge_ids: str = "target_edge_ids"
    retired_edge_ids: str = "retired_edge_ids"
    node_state_before: str = "node_state_before"
    node_state_after: str = "node_state_after"
    edge_state_before: str = "edge_state_before"
    edge_state_after: str = "edge_state_after"
    packet_ledger_digest_before: str = "packet_ledger_digest_before"
    packet_ledger_digest_after: str = "packet_ledger_digest_after"
    active_node_state_total_before: str = "active_node_state_total_before"
    active_node_state_total_after: str = "active_node_state_total_after"
    packet_ledger_node_total_before: str = "packet_ledger_node_total_before"
    packet_ledger_node_total_after: str = "packet_ledger_node_total_after"
    packet_ledger_in_flight_packet_total_before: str = (
        "packet_ledger_in_flight_packet_total_before"
    )
    packet_ledger_in_flight_packet_total_after: str = (
        "packet_ledger_in_flight_packet_total_after"
    )
    packet_ledger_conserved_budget_total_before: str = (
        "packet_ledger_conserved_budget_total_before"
    )
    packet_ledger_conserved_budget_total_after: str = (
        "packet_ledger_conserved_budget_total_after"
    )
    node_plus_packet_budget_before: str = "node_plus_packet_budget_before"
    node_plus_packet_budget_after: str = "node_plus_packet_budget_after"
    node_plus_packet_budget_error: str = "node_plus_packet_budget_error"
    active_state_digest_before: str = "active_state_digest_before"
    active_state_digest_after: str = "active_state_digest_after"
    state_reabsorption_action: str = "state_reabsorption_action"
    claim_flags: str = "claim_flags"
    idempotency_key: str = "idempotency_key"
    topology_state_reabsorption_digest: str = "topology_state_reabsorption_digest"


@dataclass(frozen=True)
class LGRC9V3NativeRouteCandidateFieldNames:
    """Stable serialized field names for native route candidates."""

    candidate_route_id: str = "candidate_route_id"
    schema_version: str = "schema_version"
    native_route_arbitration_policy_id: str = "native_route_arbitration_policy_id"
    native_route_arbitration_enabled: str = "native_route_arbitration_enabled"
    candidate_set_id: str = "candidate_set_id"
    candidate_source_surface_digest: str = "candidate_source_surface_digest"
    candidate_source_producer_record_id: str = (
        "candidate_source_producer_record_id"
    )
    candidate_source_topology_state_reabsorption_digest: str = (
        "candidate_source_topology_state_reabsorption_digest"
    )
    route_intent: str = "route_intent"
    candidate_topology_event_kind: str = "candidate_topology_event_kind"
    candidate_competing_sink_ids: str = "candidate_competing_sink_ids"
    candidate_losing_sink_ids: str = "candidate_losing_sink_ids"
    candidate_selected_sink_id: str = "candidate_selected_sink_id"
    candidate_transferred_node_ids: str = "candidate_transferred_node_ids"
    candidate_lineage_transfer_map: str = "candidate_lineage_transfer_map"
    candidate_lineage_transfer_map_digest: str = (
        "candidate_lineage_transfer_map_digest"
    )
    candidate_source_node_ids: str = "candidate_source_node_ids"
    candidate_target_node_ids: str = "candidate_target_node_ids"
    candidate_retired_node_ids: str = "candidate_retired_node_ids"
    candidate_source_edge_ids: str = "candidate_source_edge_ids"
    candidate_target_edge_ids: str = "candidate_target_edge_ids"
    candidate_retired_edge_ids: str = "candidate_retired_edge_ids"
    candidate_route_score: str = "candidate_route_score"
    candidate_score_components: str = "candidate_score_components"
    candidate_budget_prediction: str = "candidate_budget_prediction"
    candidate_order_key: str = "candidate_order_key"
    candidate_runtime_visible_inputs: str = "candidate_runtime_visible_inputs"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    causal_layer_mode: str = "causal_layer_mode"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    claim_flags: str = "claim_flags"
    candidate_route_digest: str = "candidate_route_digest"


@dataclass(frozen=True)
class LGRC9V3NativeRouteCandidateSetFieldNames:
    """Stable serialized field names for native route candidate sets."""

    candidate_set_id: str = "candidate_set_id"
    schema_version: str = "schema_version"
    native_route_arbitration_policy_id: str = "native_route_arbitration_policy_id"
    native_route_arbitration_enabled: str = "native_route_arbitration_enabled"
    arbitration_window_id: str = "arbitration_window_id"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    candidate_route_digests: str = "candidate_route_digests"
    candidate_set_order_key: str = "candidate_set_order_key"
    unresolved_tie_policy: str = "unresolved_tie_policy"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    causal_layer_mode: str = "causal_layer_mode"
    claim_flags: str = "claim_flags"
    idempotency_key: str = "idempotency_key"
    candidate_set_digest: str = "candidate_set_digest"


@dataclass(frozen=True)
class LGRC9V3NativeRouteArbitrationFieldNames:
    """Stable serialized field names for native route-arbitration records."""

    native_route_arbitration_record_id: str = "native_route_arbitration_record_id"
    schema_version: str = "schema_version"
    native_route_arbitration_policy_id: str = "native_route_arbitration_policy_id"
    native_route_arbitration_enabled: str = "native_route_arbitration_enabled"
    candidate_set_id: str = "candidate_set_id"
    candidate_set_digest: str = "candidate_set_digest"
    selected_candidate_route_id: str = "selected_candidate_route_id"
    selected_candidate_route_digest: str = "selected_candidate_route_digest"
    rejected_candidate_route_digests: str = "rejected_candidate_route_digests"
    arbitration_reason_code: str = "arbitration_reason_code"
    arbitration_score: str = "arbitration_score"
    arbitration_rule: str = "arbitration_rule"
    arbitration_runtime_visible_inputs: str = "arbitration_runtime_visible_inputs"
    selected_topology_event_id: str = "selected_topology_event_id"
    selected_topology_event_digest: str = "selected_topology_event_digest"
    event_time_key: str = "event_time_key"
    scheduler_event_index: str = "scheduler_event_index"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    causal_layer_mode: str = "causal_layer_mode"
    claim_flags: str = "claim_flags"
    idempotency_key: str = "idempotency_key"
    native_route_arbitration_digest: str = "native_route_arbitration_digest"


LGRC9V3_PACKET_FIELD_NAMES: Final[LGRC9V3PacketFieldNames] = (
    LGRC9V3PacketFieldNames()
)
LGRC9V3_PACKET_LEDGER_FIELD_NAMES: Final[LGRC9V3PacketLedgerFieldNames] = (
    LGRC9V3PacketLedgerFieldNames()
)
LGRC9V3_PENDING_FLUX_FIELD_NAMES: Final[LGRC9V3PendingFluxFieldNames] = (
    LGRC9V3PendingFluxFieldNames()
)
LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES: Final[
    LGRC9V3TopologyContractFieldNames
] = LGRC9V3TopologyContractFieldNames()
LGRC9V3_PACKET_TRANSPORT_FIELD_NAMES: Final[
    LGRC9V3PacketTransportFieldNames
] = LGRC9V3PacketTransportFieldNames()
LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES: Final[
    LGRC9V3CollapseReabsorptionFieldNames
] = LGRC9V3CollapseReabsorptionFieldNames()
LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES: Final[
    LGRC9V3ProperTimeIdentityFieldNames
] = LGRC9V3ProperTimeIdentityFieldNames()
LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES: Final[
    LGRC9V3AutonomousProducerFieldNames
] = LGRC9V3AutonomousProducerFieldNames()
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES: Final[
    LGRC9V3CausalPulseSubstrateSurfaceFieldNames
] = LGRC9V3CausalPulseSubstrateSurfaceFieldNames()
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_FIELD_NAMES: Final[
    LGRC9V3CausalPulseSubstrateSurfaceLineageFieldNames
] = LGRC9V3CausalPulseSubstrateSurfaceLineageFieldNames()
LGRC9V3_TOPOLOGY_STATE_REABSORPTION_FIELD_NAMES: Final[
    LGRC9V3TopologyStateReabsorptionFieldNames
] = LGRC9V3TopologyStateReabsorptionFieldNames()
LGRC9V3_NATIVE_ROUTE_CANDIDATE_FIELD_NAMES: Final[
    LGRC9V3NativeRouteCandidateFieldNames
] = LGRC9V3NativeRouteCandidateFieldNames()
LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_FIELD_NAMES: Final[
    LGRC9V3NativeRouteCandidateSetFieldNames
] = LGRC9V3NativeRouteCandidateSetFieldNames()
LGRC9V3_NATIVE_ROUTE_ARBITRATION_FIELD_NAMES: Final[
    LGRC9V3NativeRouteArbitrationFieldNames
] = LGRC9V3NativeRouteArbitrationFieldNames()

LGRC9V3_PACKET_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_PACKET_FIELD_NAMES.packet_id,
        LGRC9V3_PACKET_FIELD_NAMES.packet_state,
        LGRC9V3_PACKET_FIELD_NAMES.source_node_id,
        LGRC9V3_PACKET_FIELD_NAMES.target_node_id,
        LGRC9V3_PACKET_FIELD_NAMES.edge_id,
        LGRC9V3_PACKET_FIELD_NAMES.amount,
        LGRC9V3_PACKET_FIELD_NAMES.departure_event_time_key,
        LGRC9V3_PACKET_FIELD_NAMES.arrival_event_time_key,
    }
)
LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.topology_event_id,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.topology_event_kind,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.source_expansion_event_id,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.pre_topology_signature,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.post_topology_signature,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.refinement_lineage_map,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.expanded_node_id,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.replacement_node_ids,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.parent_to_child_node_lineage,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.boundary_reassignment_map,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_before,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_after,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_error,
    }
)
LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.topology_event_id,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.source_packet_ids,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.source_pending_flux_entry_ids,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.transported_packet_ids,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.amount_total,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_before,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_after,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.budget_error,
        LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.identity_acceptance_emitted,
    }
)
LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS: Final[frozenset[str]] = (
    frozenset(
        {
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.topology_event_id,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.topology_event_kind,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.scheduler_event_index,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.checkpoint_index,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.event_time_key,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.proper_time_inheritance_records,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.expanded_node_id,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.replacement_node_ids,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.internal_edge_ids,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.parent_proper_time,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.child_proper_time,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.internal_edge_delay,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.proper_time_inheritance_policy,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.internal_edge_delay_policy,
            LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES.identity_acceptance_emitted,
        }
    )
)
LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.topology_event_id,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.topology_event_kind,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.event_time_key,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.competing_sink_ids,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.selected_sink_id,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.losing_sink_ids,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.lineage_transfer_map,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.coherence_transfer_amount,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.budget_before,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.budget_after,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.budget_error,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.budget_transfer_policy,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.lineage_transfer_policy,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.proper_time_transfer_policy,
        LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES.identity_acceptance_emitted,
    }
)
LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.topology_event_id,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.topology_event_kind,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.source_topology_event_ids,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.event_time_key,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.sink_node_id,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.lineage_id,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.identity_clock_policy,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.threshold_calibration_policy,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.proper_time_persistence_threshold,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.threshold_multiplier,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.local_median_edge_delay,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.window_start_event_time_key,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.window_end_event_time_key,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.observed_persistence_duration,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.budget_before,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.budget_after,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.budget_error,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.identity_acceptance_allowed,
        LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES.identity_acceptance_emitted,
    }
)
LGRC9V3_AUTONOMOUS_PRODUCER_REQUIRED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.producer_policy,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.producer_version,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.reason_code,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.thresholds,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.observed_evidence,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.scheduled_event_kind,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.scheduled_event_time_key,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.causal_surface_digest,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.idempotency_key,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.queued_work_consumed,
        LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES.topology_mutated,
    }
)
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_REQUIRED_FIELDS: Final[
    frozenset[str]
] = frozenset(vars(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES).values())
LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS: Final[
    Mapping[str, tuple[str, ...]]
] = {
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS: (
        "node_coherence",
        "support_mask",
    ),
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE: (
        "node_coherence",
        "front_mask",
        "rear_mask",
    ),
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE: (
        "node_proper_time",
        "contact_nodes",
    ),
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION: (
        "node_coherence",
        "node_proper_time",
        "surface_nodes",
    ),
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT: (
        "committed_packet_event",
        "route_aspect_digest",
        "pulse_channel_id",
    ),
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY: (
        "committed_surface_rows",
        "eligibility_thresholds",
        "producer_policy",
    ),
}



@dataclass(frozen=True)
class LGRC9V3TimingFieldNames:
    """Stable serialized timing field names for LGRC9V3 artifacts."""

    scheduler_event_index: str = "scheduler_event_index"
    checkpoint_index: str = "checkpoint_index"
    event_time_key: str = "event_time_key"
    node_proper_time: str = "node_proper_time"
    node_last_update_proper_time: str = "node_last_update_proper_time"
    edge_causal_delay: str = "edge_causal_delay"
    lapse: str = "lapse"
    causal_history_log: str = "causal_history_log"
    causal_layer_mode: str = "causal_layer_mode"
    lgrc_runtime_level: str = "lgrc_runtime_level"
    lapse_policy: str = "lapse_policy"
    edge_delay_policy: str = "edge_delay_policy"
    event_time_policy: str = "event_time_policy"
    proper_time_accumulation_policy: str = "proper_time_accumulation_policy"
    causal_distance_policy: str = "causal_distance_policy"
    causal_cone_policy: str = "causal_cone_policy"
    causal_basin_core_policy: str = "causal_basin_core_policy"
    require_fixed_topology_for_lgrc1: str = "require_fixed_topology_for_lgrc1"
    require_fixed_topology_for_lgrc2: str = "require_fixed_topology_for_lgrc2"


LGRC9V3_TIMING_FIELD_NAMES: Final[LGRC9V3TimingFieldNames] = (
    LGRC9V3TimingFieldNames()
)

LGRC9V3_TIMING_ALIASES: Final[dict[str, str]] = {
    "scheduler_event_index": "kappa",
    "checkpoint_index": "k",
    "event_time_key": "T_e",
    "node_proper_time": "tau_i",
    "edge_causal_delay": "tau_ij",
}

LGRC9V3_DEFAULT_CAUSAL_MODES: Final[dict[str, Any]] = {
    "causal_layer_mode": CAUSAL_LAYER_MODE_ANNOTATION,
    "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC0,
    "lapse_policy": LAPSE_POLICY_BOUNDED_DENSITY_TENSION,
    "edge_delay_policy": EDGE_DELAY_POLICY_GEOMETRY_BASELINE,
    "event_time_policy": EVENT_TIME_POLICY_DERIVED_FROM_SYNCHRONOUS_STEP,
    "proper_time_accumulation_policy": PROPER_TIME_POLICY_ANNOTATION,
    "causal_distance_policy": CAUSAL_DISTANCE_POLICY_EDGE_DELAY_SHORTEST_PATH,
    "causal_cone_policy": CAUSAL_CONE_POLICY_BOUNDED_SHORTEST_PATH,
    "causal_basin_core_policy": CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION,
    "require_fixed_topology_for_lgrc1": True,
    "require_fixed_topology_for_lgrc2": True,
    "causal_boundary_birth_allowed": False,
    "causal_boundary_birth_policy": LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED,
    "causal_boundary_birth_coherence_source": (
        LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT
    ),
    "causal_boundary_birth_edge_delay_policy": (
        LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0
    ),
    "causal_topology_integration_allowed": False,
    "causal_spark_expansion_allowed": False,
    "causal_refinement_packet_transport_allowed": False,
    "causal_proper_time_inheritance_allowed": False,
    "causal_collapse_reabsorption_allowed": False,
    "causal_identity_acceptance_allowed": False,
    "causal_pulse_substrate_surface_enabled": False,
    "causal_pulse_substrate_surface_policy": (
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
    ),
    "causal_pulse_substrate_surface_validated": False,
    "causal_pulse_substrate_surface_lineage_transport_enabled": False,
    "causal_pulse_substrate_surface_lineage_transport_policy": (
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED
    ),
    "causal_pulse_substrate_surface_lineage_transport_validated": False,
    "causal_pulse_substrate_surface_lineage_transport_supported": False,
    "causal_topology_state_reabsorption_enabled": False,
    "causal_topology_state_reabsorption_policy": (
        LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED
    ),
    "causal_topology_state_reabsorption_validated": False,
    "causal_topology_state_reabsorption_supported": False,
    "native_lgrc_route_arbitration_enabled": False,
    "native_lgrc_route_arbitration_policy": (
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
    ),
    "native_lgrc_route_arbitration_validated": False,
    "native_lgrc_route_arbitration_supported": False,
    "native_lgrc_multi_basin_formation_enabled": False,
    "native_lgrc_multi_basin_formation_policy": (
        LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED
    ),
    "native_lgrc_multi_basin_formation_validated": False,
    "native_lgrc_multi_basin_formation_supported": False,
}
LGRC9V3_CAUSAL_MODE_KEYS: Final[frozenset[str]] = frozenset(
    LGRC9V3_DEFAULT_CAUSAL_MODES
)


def _require_choice(
    modes: Mapping[str, Any],
    *,
    key: str,
    allowed: frozenset[str],
) -> str:
    value = modes[key]
    if not isinstance(value, str) or value not in allowed:
        raise InvalidParamsError(f"{key} must be one of {sorted(allowed)}")
    return value


def validate_lgrc9v3_causal_modes(
    modes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return validated LGRC9V3 causal-history modes.

    These modes are model-parameter semantics. A future LGRC9V3 model should
    store them under ``constitutive_semantic_modes["causal_history"]``.
    Consumers should use ``LGRC9V3_CAUSAL_MODES_KEY`` for that nested key.
    Telemetry/checkpoint artifacts should copy the resolved values under a
    same-named ``"causal_history"`` evidence block.
    """

    raw_modes = {} if modes is None else dict(modes)
    unknown = set(raw_modes) - LGRC9V3_CAUSAL_MODE_KEYS
    if unknown:
        raise InvalidParamsError(
            f"LGRC9V3 causal modes contain unknown keys: {sorted(unknown)}"
        )

    resolved = dict(LGRC9V3_DEFAULT_CAUSAL_MODES)
    resolved.update(raw_modes)

    causal_layer_mode = _require_choice(
        resolved,
        key="causal_layer_mode",
        allowed=_ALLOWED_CAUSAL_LAYER_MODES,
    )
    runtime_level = _require_choice(
        resolved,
        key="lgrc_runtime_level",
        allowed=_ALLOWED_RUNTIME_LEVELS,
    )
    _require_choice(resolved, key="lapse_policy", allowed=_ALLOWED_LAPSE_POLICIES)
    _require_choice(
        resolved,
        key="edge_delay_policy",
        allowed=_ALLOWED_EDGE_DELAY_POLICIES,
    )
    _require_choice(
        resolved,
        key="event_time_policy",
        allowed=_ALLOWED_EVENT_TIME_POLICIES,
    )
    proper_time_policy = _require_choice(
        resolved,
        key="proper_time_accumulation_policy",
        allowed=_ALLOWED_PROPER_TIME_POLICIES,
    )
    _require_choice(
        resolved,
        key="causal_distance_policy",
        allowed=_ALLOWED_CAUSAL_DISTANCE_POLICIES,
    )
    _require_choice(
        resolved,
        key="causal_cone_policy",
        allowed=_ALLOWED_CAUSAL_CONE_POLICIES,
    )
    _require_choice(
        resolved,
        key="causal_basin_core_policy",
        allowed=_ALLOWED_CAUSAL_BASIN_CORE_POLICIES,
    )

    require_fixed_topology = resolved["require_fixed_topology_for_lgrc1"]
    if not isinstance(require_fixed_topology, bool):
        raise InvalidParamsError("require_fixed_topology_for_lgrc1 must be a boolean")
    require_fixed_topology_lgrc2 = resolved["require_fixed_topology_for_lgrc2"]
    if not isinstance(require_fixed_topology_lgrc2, bool):
        raise InvalidParamsError("require_fixed_topology_for_lgrc2 must be a boolean")
    boundary_birth_allowed = resolved["causal_boundary_birth_allowed"]
    if not isinstance(boundary_birth_allowed, bool):
        raise InvalidParamsError("causal_boundary_birth_allowed must be a boolean")
    boundary_birth_policy = _require_choice(
        resolved,
        key="causal_boundary_birth_policy",
        allowed=_ALLOWED_CAUSAL_BOUNDARY_BIRTH_POLICIES,
    )
    _require_choice(
        resolved,
        key="causal_boundary_birth_coherence_source",
        allowed=_ALLOWED_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCES,
    )
    _require_choice(
        resolved,
        key="causal_boundary_birth_edge_delay_policy",
        allowed=_ALLOWED_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICIES,
    )
    if boundary_birth_allowed and (
        boundary_birth_policy == LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "causal_boundary_birth_allowed=true requires an active "
            "causal_boundary_birth_policy"
        )
    if (
        not boundary_birth_allowed
        and boundary_birth_policy
        != LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active causal_boundary_birth_policy requires "
            "causal_boundary_birth_allowed=true"
        )
    topology_integration_allowed = resolved["causal_topology_integration_allowed"]
    spark_expansion_allowed = resolved["causal_spark_expansion_allowed"]
    refinement_packet_transport_allowed = resolved[
        "causal_refinement_packet_transport_allowed"
    ]
    proper_time_inheritance_allowed = resolved[
        "causal_proper_time_inheritance_allowed"
    ]
    collapse_reabsorption_allowed = resolved["causal_collapse_reabsorption_allowed"]
    identity_acceptance_allowed = resolved["causal_identity_acceptance_allowed"]
    pulse_surface_enabled = resolved["causal_pulse_substrate_surface_enabled"]
    pulse_surface_validated = resolved["causal_pulse_substrate_surface_validated"]
    pulse_surface_lineage_enabled = resolved[
        "causal_pulse_substrate_surface_lineage_transport_enabled"
    ]
    pulse_surface_lineage_validated = resolved[
        "causal_pulse_substrate_surface_lineage_transport_validated"
    ]
    pulse_surface_lineage_supported = resolved[
        "causal_pulse_substrate_surface_lineage_transport_supported"
    ]
    topology_state_reabsorption_enabled = resolved[
        "causal_topology_state_reabsorption_enabled"
    ]
    topology_state_reabsorption_validated = resolved[
        "causal_topology_state_reabsorption_validated"
    ]
    topology_state_reabsorption_supported = resolved[
        "causal_topology_state_reabsorption_supported"
    ]
    native_route_arbitration_enabled = resolved[
        "native_lgrc_route_arbitration_enabled"
    ]
    native_route_arbitration_validated = resolved[
        "native_lgrc_route_arbitration_validated"
    ]
    native_route_arbitration_supported = resolved[
        "native_lgrc_route_arbitration_supported"
    ]
    native_multi_basin_enabled = resolved[
        "native_lgrc_multi_basin_formation_enabled"
    ]
    native_multi_basin_validated = resolved[
        "native_lgrc_multi_basin_formation_validated"
    ]
    native_multi_basin_supported = resolved[
        "native_lgrc_multi_basin_formation_supported"
    ]
    for key, value in (
        ("causal_topology_integration_allowed", topology_integration_allowed),
        ("causal_spark_expansion_allowed", spark_expansion_allowed),
        (
            "causal_refinement_packet_transport_allowed",
            refinement_packet_transport_allowed,
        ),
        (
            "causal_proper_time_inheritance_allowed",
            proper_time_inheritance_allowed,
        ),
        ("causal_collapse_reabsorption_allowed", collapse_reabsorption_allowed),
        ("causal_identity_acceptance_allowed", identity_acceptance_allowed),
        ("causal_pulse_substrate_surface_enabled", pulse_surface_enabled),
        ("causal_pulse_substrate_surface_validated", pulse_surface_validated),
        (
            "causal_pulse_substrate_surface_lineage_transport_enabled",
            pulse_surface_lineage_enabled,
        ),
        (
            "causal_pulse_substrate_surface_lineage_transport_validated",
            pulse_surface_lineage_validated,
        ),
        (
            "causal_pulse_substrate_surface_lineage_transport_supported",
            pulse_surface_lineage_supported,
        ),
        (
            "causal_topology_state_reabsorption_enabled",
            topology_state_reabsorption_enabled,
        ),
        (
            "causal_topology_state_reabsorption_validated",
            topology_state_reabsorption_validated,
        ),
        (
            "causal_topology_state_reabsorption_supported",
            topology_state_reabsorption_supported,
        ),
        ("native_lgrc_route_arbitration_enabled", native_route_arbitration_enabled),
        (
            "native_lgrc_route_arbitration_validated",
            native_route_arbitration_validated,
        ),
        (
            "native_lgrc_route_arbitration_supported",
            native_route_arbitration_supported,
        ),
        (
            "native_lgrc_multi_basin_formation_enabled",
            native_multi_basin_enabled,
        ),
        (
            "native_lgrc_multi_basin_formation_validated",
            native_multi_basin_validated,
        ),
        (
            "native_lgrc_multi_basin_formation_supported",
            native_multi_basin_supported,
        ),
    ):
        if not isinstance(value, bool):
            raise InvalidParamsError(f"{key} must be a boolean")
    pulse_surface_policy = _require_choice(
        resolved,
        key="causal_pulse_substrate_surface_policy",
        allowed=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICIES,
    )
    pulse_surface_lineage_policy = _require_choice(
        resolved,
        key="causal_pulse_substrate_surface_lineage_transport_policy",
        allowed=LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICIES,
    )
    topology_state_reabsorption_policy = _require_choice(
        resolved,
        key="causal_topology_state_reabsorption_policy",
        allowed=LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICIES,
    )
    native_route_arbitration_policy = _require_choice(
        resolved,
        key="native_lgrc_route_arbitration_policy",
        allowed=LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICIES,
    )
    native_multi_basin_policy = _require_choice(
        resolved,
        key="native_lgrc_multi_basin_formation_policy",
        allowed=LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICIES,
    )
    if pulse_surface_enabled and (
        pulse_surface_policy == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "causal_pulse_substrate_surface_enabled=true requires an active "
            "causal_pulse_substrate_surface_policy"
        )
    if (
        not pulse_surface_enabled
        and pulse_surface_policy
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active causal_pulse_substrate_surface_policy requires "
            "causal_pulse_substrate_surface_enabled=true"
        )
    if pulse_surface_validated and not pulse_surface_enabled:
        raise InvalidParamsError(
            "causal_pulse_substrate_surface_validated=true requires "
            "causal_pulse_substrate_surface_enabled=true"
        )
    if pulse_surface_lineage_enabled and (
        pulse_surface_lineage_policy
        == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "causal_pulse_substrate_surface_lineage_transport_enabled=true "
            "requires an active lineage transport policy"
        )
    if (
        not pulse_surface_lineage_enabled
        and pulse_surface_lineage_policy
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active surface lineage transport policy requires "
            "causal_pulse_substrate_surface_lineage_transport_enabled=true"
        )
    if pulse_surface_lineage_validated and not pulse_surface_lineage_enabled:
        raise InvalidParamsError(
            "causal_pulse_substrate_surface_lineage_transport_validated=true "
            "requires lineage transport enabled=true"
        )
    if pulse_surface_lineage_supported and not pulse_surface_lineage_validated:
        raise InvalidParamsError(
            "causal_pulse_substrate_surface_lineage_transport_supported=true "
            "requires lineage transport validation"
        )
    if pulse_surface_lineage_enabled and not pulse_surface_enabled:
        raise InvalidParamsError(
            "surface lineage transport requires native causal pulse-substrate "
            "surface enabled=true"
        )
    if pulse_surface_lineage_enabled and (
        runtime_level != LGRC_RUNTIME_LEVEL_LGRC3
        or causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    ):
        raise InvalidParamsError(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3
        )
    if topology_state_reabsorption_enabled and (
        topology_state_reabsorption_policy
        == LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "causal_topology_state_reabsorption_enabled=true requires an "
            "active topology-state reabsorption policy"
        )
    if (
        not topology_state_reabsorption_enabled
        and topology_state_reabsorption_policy
        != LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active topology-state reabsorption policy requires "
            "causal_topology_state_reabsorption_enabled=true"
        )
    if (
        topology_state_reabsorption_validated
        and not topology_state_reabsorption_enabled
    ):
        raise InvalidParamsError(
            "causal_topology_state_reabsorption_validated=true requires "
            "causal_topology_state_reabsorption_enabled=true"
        )
    if (
        topology_state_reabsorption_supported
        and not topology_state_reabsorption_validated
    ):
        raise InvalidParamsError(
            "causal_topology_state_reabsorption_supported=true requires "
            "topology-state reabsorption validation"
        )
    if topology_state_reabsorption_enabled and not topology_integration_allowed:
        raise InvalidParamsError(
            "topology-state reabsorption requires "
            "causal_topology_integration_allowed=true"
        )
    if topology_state_reabsorption_enabled and (
        runtime_level != LGRC_RUNTIME_LEVEL_LGRC3
        or causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    ):
        raise InvalidParamsError(
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3
        )
    if native_route_arbitration_enabled and (
        native_route_arbitration_policy
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "native_lgrc_route_arbitration_enabled=true requires an active "
            "route-arbitration policy"
        )
    if (
        not native_route_arbitration_enabled
        and native_route_arbitration_policy
        != LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active native_lgrc_route_arbitration_policy requires "
            "native_lgrc_route_arbitration_enabled=true"
        )
    if native_route_arbitration_validated and not native_route_arbitration_enabled:
        raise InvalidParamsError(
            "native_lgrc_route_arbitration_validated=true requires "
            "native_lgrc_route_arbitration_enabled=true"
        )
    if native_route_arbitration_supported and not native_route_arbitration_validated:
        raise InvalidParamsError(
            "native_lgrc_route_arbitration_supported=true requires "
            "native route-arbitration validation"
        )
    if native_route_arbitration_enabled and (
        runtime_level != LGRC_RUNTIME_LEVEL_LGRC3
        or causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    ):
        raise InvalidParamsError("native_lgrc_route_arbitration_requires_lgrc3")
    if native_route_arbitration_enabled and not topology_integration_allowed:
        raise InvalidParamsError(
            "native route arbitration requires "
            "causal_topology_integration_allowed=true"
        )
    if native_route_arbitration_enabled and not pulse_surface_lineage_supported:
        raise InvalidParamsError(
            "native route arbitration requires supported surface-lineage transport"
        )
    if native_route_arbitration_enabled and not topology_state_reabsorption_supported:
        raise InvalidParamsError(
            "native route arbitration requires supported topology-state reabsorption"
        )
    if native_multi_basin_enabled and (
        native_multi_basin_policy
        == LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "native_lgrc_multi_basin_formation_enabled=true requires an "
            "active multi-basin formation policy"
        )
    if (
        not native_multi_basin_enabled
        and native_multi_basin_policy
        != LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED
    ):
        raise InvalidParamsError(
            "active native_lgrc_multi_basin_formation_policy requires "
            "native_lgrc_multi_basin_formation_enabled=true"
        )
    if native_multi_basin_validated and not native_multi_basin_enabled:
        raise InvalidParamsError(
            "native_lgrc_multi_basin_formation_validated=true requires "
            "native_lgrc_multi_basin_formation_enabled=true"
        )
    if native_multi_basin_supported and not native_multi_basin_validated:
        raise InvalidParamsError(
            "native_lgrc_multi_basin_formation_supported=true requires "
            "multi-basin formation validation"
        )
    if native_multi_basin_enabled and (
        runtime_level != LGRC_RUNTIME_LEVEL_LGRC3
        or causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    ):
        raise InvalidParamsError("native_lgrc_multi_basin_formation_requires_lgrc3")
    if native_multi_basin_enabled and not topology_integration_allowed:
        raise InvalidParamsError(
            "native multi-basin formation requires "
            "causal_topology_integration_allowed=true"
        )
    if pulse_surface_enabled and (
        causal_layer_mode != CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY
        and not pulse_surface_lineage_enabled
    ):
        raise InvalidParamsError(
            "native causal pulse-substrate surface v1 requires "
            "packetized fixed-topology LGRC-2 execution"
        )
    if (
        spark_expansion_allowed
        or refinement_packet_transport_allowed
        or proper_time_inheritance_allowed
        or collapse_reabsorption_allowed
        or identity_acceptance_allowed
    ) and not topology_integration_allowed:
        raise InvalidParamsError(
            "active LGRC topology sub-policies require "
            "causal_topology_integration_allowed=true"
        )
    if refinement_packet_transport_allowed and not spark_expansion_allowed:
        raise InvalidParamsError(
            "causal_refinement_packet_transport_allowed requires "
            "causal_spark_expansion_allowed=true"
        )
    if proper_time_inheritance_allowed and not spark_expansion_allowed:
        raise InvalidParamsError(
            "causal_proper_time_inheritance_allowed requires "
            "causal_spark_expansion_allowed=true"
        )

    if runtime_level == LGRC_RUNTIME_LEVEL_LGRC0:
        if causal_layer_mode != CAUSAL_LAYER_MODE_ANNOTATION:
            raise InvalidParamsError(
                "lgrc0 requires causal_layer_mode='annotation'"
            )
        if proper_time_policy != PROPER_TIME_POLICY_ANNOTATION:
            raise InvalidParamsError(
                "lgrc0 requires proper_time_accumulation_policy='annotation'"
            )

    if runtime_level == LGRC_RUNTIME_LEVEL_LGRC1:
        if causal_layer_mode != CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL:
            raise InvalidParamsError(
                "lgrc1 requires causal_layer_mode='fixed_topology_semicausal'"
            )
        if proper_time_policy == PROPER_TIME_POLICY_ANNOTATION:
            raise InvalidParamsError(
                "lgrc1 requires an operational proper-time accumulation policy"
            )
        if not require_fixed_topology:
            raise InvalidParamsError(
                "lgrc1 requires require_fixed_topology_for_lgrc1=true in v1"
            )

    if runtime_level in {LGRC_RUNTIME_LEVEL_LGRC0, LGRC_RUNTIME_LEVEL_LGRC1}:
        if pulse_surface_enabled:
            raise InvalidParamsError(
                "causal pulse-substrate surface row emission requires LGRC-2 "
                "or higher"
            )

    if runtime_level == LGRC_RUNTIME_LEVEL_LGRC2:
        if causal_layer_mode != CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY:
            raise InvalidParamsError(
                "lgrc2 requires causal_layer_mode='packetized_fixed_topology'"
            )
        if proper_time_policy == PROPER_TIME_POLICY_ANNOTATION:
            raise InvalidParamsError(
                "lgrc2 requires an operational proper-time accumulation policy"
            )
        if not require_fixed_topology_lgrc2:
            raise InvalidParamsError(
                "lgrc2 requires require_fixed_topology_for_lgrc2=true"
            )
        if boundary_birth_allowed:
            raise InvalidParamsError("causal boundary birth requires lgrc3")
        if topology_integration_allowed:
            raise InvalidParamsError("active topology integration requires lgrc3")
        if (
            pulse_surface_enabled
            and pulse_surface_policy
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
        ):
            raise InvalidParamsError(
                "active causal pulse-substrate surface requires active policy"
            )

    if runtime_level == LGRC_RUNTIME_LEVEL_LGRC3:
        if causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY:
            raise InvalidParamsError(
                "lgrc3 requires "
                "causal_layer_mode='topology_changing_causal_history'"
            )
        if proper_time_policy == PROPER_TIME_POLICY_ANNOTATION:
            raise InvalidParamsError(
                "lgrc3 requires an operational proper-time accumulation policy"
            )

    return resolved


def validate_lgrc9v3_autonomous_producer_policy(policy: str) -> str:
    """Return a validated autonomous producer policy id."""

    if policy not in LGRC9V3_AUTONOMOUS_PRODUCER_POLICIES:
        raise InvalidParamsError(
            "autonomous producer policy must be one of "
            f"{sorted(LGRC9V3_AUTONOMOUS_PRODUCER_POLICIES)}"
        )
    return str(policy)


def build_lgrc9v3_autonomous_surface_digest(surface: Mapping[str, Any]) -> str:
    """Return the canonical digest used for producer idempotency."""

    return digest_canonical_data({"lgrc9v3_autonomous_surface": dict(surface)})


def build_lgrc9v3_autonomous_production_record_id(
    *,
    producer_policy: str,
    causal_surface_digest: str,
    reason_code: str,
    trigger_node_id: int | None = None,
    trigger_edge_id: int | None = None,
    scheduled_event_kind: str | None = None,
    scheduled_event_time_key: float | None = None,
) -> str:
    """Build a deterministic autonomous producer evidence row id."""

    digest = digest_canonical_data(
        {
            "producer_policy": producer_policy,
            "causal_surface_digest": causal_surface_digest,
            "reason_code": reason_code,
            "trigger_node_id": trigger_node_id,
            "trigger_edge_id": trigger_edge_id,
            "scheduled_event_kind": scheduled_event_kind,
            "scheduled_event_time_key": scheduled_event_time_key,
        }
    )
    return f"lgrc9v3-producer-record-{digest[:24]}"


@dataclass(frozen=True)
class LGRC9V3AutonomousProductionRecord:
    """One auditable producer reason row.

    A record can either describe scheduled work or explain why no work was
    scheduled. It never represents consumed work; only ``step()`` consumes
    queued causal events.
    """

    record_id: str
    producer_policy: str
    producer_version: str
    reason_code: str
    causal_surface_digest: str
    idempotency_key: str
    thresholds: Mapping[str, Any] = field(default_factory=dict)
    observed_evidence: Mapping[str, Any] = field(default_factory=dict)
    trigger_node_id: int | None = None
    trigger_edge_id: int | None = None
    scheduled_event_kind: str | None = None
    scheduled_event_time_key: float | None = None
    scheduled_event_id: str | None = None
    queued_work_consumed: bool = False
    topology_mutated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id:
            raise ValueError("record_id must be a non-empty string")
        validate_lgrc9v3_autonomous_producer_policy(self.producer_policy)
        if self.producer_version != LGRC9V3_AUTONOMY_MODE_VERSION:
            raise ValueError("producer_version must match LGRC9V3 autonomy mode")
        if self.reason_code not in LGRC9V3_AUTONOMOUS_PRODUCER_REASON_CODES:
            raise ValueError("unsupported autonomous producer reason_code")
        if not isinstance(self.causal_surface_digest, str) or not (
            self.causal_surface_digest
        ):
            raise ValueError("causal_surface_digest must be a non-empty string")
        if not isinstance(self.idempotency_key, str) or not self.idempotency_key:
            raise ValueError("idempotency_key must be a non-empty string")
        for field_name in ("trigger_node_id", "trigger_edge_id"):
            value = getattr(self, field_name)
            if value is not None and int(value) < 0:
                raise ValueError(f"{field_name} must be >= 0 when provided")
        if self.scheduled_event_time_key is not None:
            _nonnegative_float(
                self.scheduled_event_time_key,
                context="scheduled_event_time_key",
            )
        if not isinstance(self.queued_work_consumed, bool):
            raise ValueError("queued_work_consumed must be boolean")
        if not isinstance(self.topology_mutated, bool):
            raise ValueError("topology_mutated must be boolean")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible autonomous producer record."""

        return {
            "record_id": self.record_id,
            "producer_policy": self.producer_policy,
            "producer_version": self.producer_version,
            "reason_code": self.reason_code,
            "trigger_node_id": None
            if self.trigger_node_id is None
            else int(self.trigger_node_id),
            "trigger_edge_id": None
            if self.trigger_edge_id is None
            else int(self.trigger_edge_id),
            "thresholds": dict(self.thresholds),
            "observed_evidence": dict(self.observed_evidence),
            "scheduled_event_kind": self.scheduled_event_kind,
            "scheduled_event_time_key": None
            if self.scheduled_event_time_key is None
            else float(self.scheduled_event_time_key),
            "scheduled_event_id": self.scheduled_event_id,
            "causal_surface_digest": self.causal_surface_digest,
            "idempotency_key": self.idempotency_key,
            "queued_work_consumed": self.queued_work_consumed,
            "topology_mutated": self.topology_mutated,
        }


@dataclass(frozen=True)
class LGRC9V3AutonomousProductionResult:
    """Auditable result for one autonomous producer invocation."""

    producer_policy: str
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    causal_surface_digest: str
    production_records: tuple[LGRC9V3AutonomousProductionRecord, ...]
    producer_version: str = LGRC9V3_AUTONOMY_MODE_VERSION
    queue_ownership_policy: str = LGRC9V3_AUTONOMOUS_PRODUCER_QUEUE_OWNERSHIP_POLICY
    idempotency_policy: str = LGRC9V3_AUTONOMOUS_PRODUCER_IDEMPOTENCY_POLICY
    queued_work_consumed: bool = False
    topology_mutated: bool = False
    state_mutated: bool = False
    collapse_reabsorption_emitted: bool = False
    identity_acceptance_emitted: bool = False

    def __post_init__(self) -> None:
        validate_lgrc9v3_autonomous_producer_policy(self.producer_policy)
        if self.producer_version != LGRC9V3_AUTONOMY_MODE_VERSION:
            raise ValueError("producer_version must match LGRC9V3 autonomy mode")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        if int(self.checkpoint_index) < 0:
            raise ValueError("checkpoint_index must be >= 0")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if not isinstance(self.causal_surface_digest, str) or not (
            self.causal_surface_digest
        ):
            raise ValueError("causal_surface_digest must be a non-empty string")
        if self.queue_ownership_policy != (
            LGRC9V3_AUTONOMOUS_PRODUCER_QUEUE_OWNERSHIP_POLICY
        ):
            raise ValueError("unsupported queue_ownership_policy")
        if self.idempotency_policy != LGRC9V3_AUTONOMOUS_PRODUCER_IDEMPOTENCY_POLICY:
            raise ValueError("unsupported idempotency_policy")
        for field_name in (
            "queued_work_consumed",
            "topology_mutated",
            "state_mutated",
            "collapse_reabsorption_emitted",
            "identity_acceptance_emitted",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be boolean")
        if self.queued_work_consumed:
            raise ValueError("autonomous producers must not consume queued work")
        if self.collapse_reabsorption_emitted or self.identity_acceptance_emitted:
            raise ValueError(
                "collapse/reabsorption and identity are outside autonomy v1"
            )

    @property
    def scheduled_event_count(self) -> int:
        """Number of records that scheduled work."""

        return sum(
            1
            for record in self.production_records
            if record.scheduled_event_kind is not None
        )

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible producer invocation artifact."""

        return {
            "artifact_kind": LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_KIND,
            "artifact_schema_version": (
                LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_AUTONOMY_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": LGRC9V3_AUTONOMOUS_PRODUCER_EVIDENCE_CLASS,
            "producer_policy": self.producer_policy,
            "producer_version": self.producer_version,
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "causal_surface_digest": self.causal_surface_digest,
            "queue_ownership_policy": self.queue_ownership_policy,
            "idempotency_policy": self.idempotency_policy,
            "production_records": [
                record.to_artifact() for record in self.production_records
            ],
            "record_count": len(self.production_records),
            "scheduled_event_count": self.scheduled_event_count,
            "queued_work_consumed": self.queued_work_consumed,
            "topology_mutated": self.topology_mutated,
            "state_mutated": self.state_mutated,
            "collapse_reabsorption_emitted": self.collapse_reabsorption_emitted,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
        }


def build_lgrc9v3_disabled_autonomous_production_result(
    *,
    scheduler_event_index: int,
    checkpoint_index: int,
    event_time_key: float,
    causal_surface_digest: str,
) -> LGRC9V3AutonomousProductionResult:
    """Build the disabled/no-op autonomous producer result."""

    idempotency_key = (
        f"{LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED}:"
        f"{causal_surface_digest}"
    )
    record = LGRC9V3AutonomousProductionRecord(
        record_id=build_lgrc9v3_autonomous_production_record_id(
            producer_policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
            causal_surface_digest=causal_surface_digest,
            reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
        ),
        producer_policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
        producer_version=LGRC9V3_AUTONOMY_MODE_VERSION,
        reason_code=LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY,
        causal_surface_digest=causal_surface_digest,
        idempotency_key=idempotency_key,
        thresholds={},
        observed_evidence={"producer_enabled": False},
    )
    return LGRC9V3AutonomousProductionResult(
        producer_policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
        scheduler_event_index=int(scheduler_event_index),
        checkpoint_index=int(checkpoint_index),
        event_time_key=float(event_time_key),
        causal_surface_digest=causal_surface_digest,
        production_records=(record,),
    )


def restore_lgrc9v3_autonomous_production_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3AutonomousProductionRecord:
    """Restore one autonomous producer record from artifact data."""

    mapping = _require_artifact_mapping(artifact, context="production_record")
    trigger_node = mapping.get("trigger_node_id")
    trigger_edge = mapping.get("trigger_edge_id")
    return LGRC9V3AutonomousProductionRecord(
        record_id=_artifact_string(mapping.get("record_id"), context="record_id"),
        producer_policy=_artifact_string(
            mapping.get("producer_policy"),
            context="producer_policy",
        ),
        producer_version=_artifact_string(
            mapping.get("producer_version"),
            context="producer_version",
        ),
        reason_code=_artifact_string(mapping.get("reason_code"), context="reason_code"),
        causal_surface_digest=_artifact_string(
            mapping.get("causal_surface_digest"),
            context="causal_surface_digest",
        ),
        idempotency_key=_artifact_string(
            mapping.get("idempotency_key"),
            context="idempotency_key",
        ),
        thresholds=dict(
            _require_artifact_mapping(
                mapping.get("thresholds", {}),
                context="thresholds",
            )
        ),
        observed_evidence=dict(
            _require_artifact_mapping(
                mapping.get("observed_evidence", {}),
                context="observed_evidence",
            )
        ),
        trigger_node_id=None
        if trigger_node is None
        else _artifact_int(trigger_node, context="trigger_node_id"),
        trigger_edge_id=None
        if trigger_edge is None
        else _artifact_int(trigger_edge, context="trigger_edge_id"),
        scheduled_event_kind=_artifact_optional_string(
            mapping.get("scheduled_event_kind"),
            context="scheduled_event_kind",
        ),
        scheduled_event_time_key=_artifact_optional_float(
            mapping.get("scheduled_event_time_key"),
            context="scheduled_event_time_key",
        ),
        scheduled_event_id=_artifact_optional_string(
            mapping.get("scheduled_event_id"),
            context="scheduled_event_id",
        ),
        queued_work_consumed=_artifact_bool(
            mapping.get("queued_work_consumed"),
            context="queued_work_consumed",
        ),
        topology_mutated=_artifact_bool(
            mapping.get("topology_mutated"),
            context="topology_mutated",
        ),
    )


def restore_lgrc9v3_autonomous_production_result_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3AutonomousProductionResult:
    """Restore an autonomous producer invocation result artifact."""

    mapping = _require_artifact_mapping(artifact, context="production_result")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_KIND
    ):
        raise SnapshotCompatibilityError("unsupported autonomous result kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported autonomous result schema version"
        )
    if (
        _artifact_string(mapping.get("mode_version"), context="mode_version")
        != LGRC9V3_AUTONOMY_MODE_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported autonomous mode version")
    raw_records = mapping.get("production_records", [])
    if not isinstance(raw_records, list):
        raise SnapshotCompatibilityError("production_records must be a list")
    result = LGRC9V3AutonomousProductionResult(
        producer_policy=_artifact_string(
            mapping.get("producer_policy"),
            context="producer_policy",
        ),
        producer_version=_artifact_string(
            mapping.get("producer_version"),
            context="producer_version",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            mapping.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        causal_surface_digest=_artifact_string(
            mapping.get("causal_surface_digest"),
            context="causal_surface_digest",
        ),
        queue_ownership_policy=_artifact_string(
            mapping.get("queue_ownership_policy"),
            context="queue_ownership_policy",
        ),
        idempotency_policy=_artifact_string(
            mapping.get("idempotency_policy"),
            context="idempotency_policy",
        ),
        production_records=tuple(
            restore_lgrc9v3_autonomous_production_record_artifact(record)
            for record in raw_records
        ),
        queued_work_consumed=_artifact_bool(
            mapping.get("queued_work_consumed"),
            context="queued_work_consumed",
        ),
        topology_mutated=_artifact_bool(
            mapping.get("topology_mutated"),
            context="topology_mutated",
        ),
        state_mutated=_artifact_bool(
            mapping.get("state_mutated"),
            context="state_mutated",
        ),
        collapse_reabsorption_emitted=_artifact_bool(
            mapping.get("collapse_reabsorption_emitted"),
            context="collapse_reabsorption_emitted",
        ),
        identity_acceptance_emitted=_artifact_bool(
            mapping.get("identity_acceptance_emitted"),
            context="identity_acceptance_emitted",
        ),
    )
    if int(mapping.get("record_count", len(result.production_records))) != len(
        result.production_records
    ):
        raise SnapshotCompatibilityError("record_count does not match records")
    if int(
        mapping.get("scheduled_event_count", result.scheduled_event_count)
    ) != result.scheduled_event_count:
        raise SnapshotCompatibilityError(
            "scheduled_event_count does not match records"
        )
    return result


@dataclass(frozen=True)
class LGRC9V3CausalPulseSubstrateSurfacePolicy:
    """Default-off policy contract for native pulse-substrate surface rows.

    The policy is an activation gate. It does not emit rows, schedule work,
    mutate coherence, or prove support by being enabled.
    """

    surface_policy_id: str
    surface_policy: str = LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED
    surface_policy_enabled: bool = False
    surface_policy_validated: bool = False
    coupling_producer_enabled: bool = False
    feedback_producer_enabled: bool = False
    supported: bool = False
    required_lgrc_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    fixed_topology_only: bool = True
    topology_lineage_status: str = LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED

    def __post_init__(self) -> None:
        if not isinstance(self.surface_policy_id, str) or not self.surface_policy_id:
            raise ValueError("surface_policy_id must be a non-empty string")
        if self.surface_policy not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICIES:
            raise ValueError("unsupported causal pulse-substrate surface policy")
        for field_name in (
            "surface_policy_enabled",
            "surface_policy_validated",
            "coupling_producer_enabled",
            "feedback_producer_enabled",
            "supported",
            "fixed_topology_only",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be boolean")
        if self.required_lgrc_level not in (
            LGRC_RUNTIME_LEVEL_LGRC2,
            LGRC_RUNTIME_LEVEL_LGRC3,
        ):
            raise ValueError("causal pulse-substrate surface requires LGRC-2 or higher")
        if (
            self.topology_lineage_status
            not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_STATUSES
        ):
            raise ValueError("unsupported topology lineage status")
        if self.surface_policy == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED:
            if self.surface_policy_enabled:
                raise ValueError("disabled surface policy cannot be enabled")
            if self.coupling_producer_enabled or self.feedback_producer_enabled:
                raise ValueError("disabled surface policy cannot enable producers")
        if self.supported and not self.surface_policy_validated:
            raise ValueError("surface support requires validation")
        if self.fixed_topology_only and (
            self.topology_lineage_status
            != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED
        ):
            raise ValueError("fixed-topology v1 must defer LGRC-3 lineage transport")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible policy artifact."""

        return {
            "surface_policy_id": self.surface_policy_id,
            "surface_policy": self.surface_policy,
            "surface_policy_enabled": self.surface_policy_enabled,
            "surface_policy_validated": self.surface_policy_validated,
            "coupling_producer_enabled": self.coupling_producer_enabled,
            "feedback_producer_enabled": self.feedback_producer_enabled,
            "native_lgrc_pulse_substrate_supported": self.supported,
            "required_lgrc_level": self.required_lgrc_level,
            "fixed_topology_only": self.fixed_topology_only,
            "topology_lineage_status": self.topology_lineage_status,
            "disabled_semantics": {
                "surface_rows_emitted": False,
                "producers_evaluate_eligibility": False,
            }
            if not self.surface_policy_enabled
            else {
                "surface_rows_emitted": True,
                "producers_evaluate_eligibility": (
                    self.coupling_producer_enabled
                    or self.feedback_producer_enabled
                ),
            },
        }


@dataclass(frozen=True)
class LGRC9V3CausalPulseSubstrateSurfaceRow:
    """Passive evidence row for packet/substrate contact.

    Creating a row records evidence only. It never mutates coherence, support,
    centroid, displacement, topology, or claim state.
    """

    surface_id: str
    surface_policy_id: str
    surface_policy_enabled: bool
    route_aspect_id: str
    route_aspect_digest: str
    pulse_event_id: str
    pulse_packet_id: str
    pulse_event_kind: str
    pulse_channel_id: str
    pulse_route_step: int
    event_time_key: float
    scheduler_event_index: int
    node_proper_time: Mapping[int, float]
    source_node_id: int
    target_node_id: int
    contact_amount: float
    surface_state_id: str
    surface_state_digest: str
    surface_kind: str
    surface_nodes: Sequence[int]
    surface_values_before: Mapping[str, Any]
    surface_values_after: Mapping[str, Any]
    runtime_visible_inputs: Sequence[str]
    surface_update_policy: Mapping[str, Any]
    surface_budget_surface: str
    surface_budget_before: float
    surface_budget_after: float
    surface_budget_error: float
    lineage_status: str
    producer_records: Sequence[Mapping[str, Any]] = ()
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    surface_policy_validated: bool = False
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC2
    schema_version: str = LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION
    surface_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "surface_id",
            "surface_policy_id",
            "route_aspect_id",
            "route_aspect_digest",
            "pulse_event_id",
            "pulse_packet_id",
            "pulse_event_kind",
            "pulse_channel_id",
            "surface_state_id",
            "surface_state_digest",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.schema_version != (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION
        ):
            raise ValueError("unsupported causal pulse-substrate row schema")
        for field_name in ("surface_policy_enabled", "surface_policy_validated"):
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be boolean")
        if self.surface_kind not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KINDS:
            raise ValueError("unsupported surface_kind")
        if self.lgrc_runtime_level not in (
            LGRC_RUNTIME_LEVEL_LGRC2,
            LGRC_RUNTIME_LEVEL_LGRC3,
        ):
            raise ValueError("surface row requires LGRC-2 or higher")
        if self.pulse_event_kind not in (
            LGRC9V3_PACKET_EVENT_KIND_DEPARTURE,
            LGRC9V3_PACKET_EVENT_KIND_ARRIVAL,
        ):
            raise ValueError(
                "surface row source event must be a packet departure or arrival"
            )
        _validate_causal_pulse_substrate_surface_update_policy(
            self.surface_update_policy,
            self.surface_kind,
        )
        if (
            self.surface_budget_surface
            not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_SURFACES
        ):
            raise ValueError("unsupported surface_budget_surface")
        if self.lineage_status != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY:
            raise ValueError("surface row v1 requires fixed_topology lineage_status")
        if int(self.pulse_route_step) < 0:
            raise ValueError("pulse_route_step must be >= 0")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        for field_name in ("source_node_id", "target_node_id"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        if not self.surface_nodes:
            raise ValueError("surface_nodes must not be empty")
        if any(int(node_id) < 0 for node_id in self.surface_nodes):
            raise ValueError("surface_nodes must be nonnegative node ids")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        _positive_float(self.contact_amount, context="contact_amount")
        _finite_float(self.surface_budget_before, context="surface_budget_before")
        _finite_float(self.surface_budget_after, context="surface_budget_after")
        _finite_float(self.surface_budget_error, context="surface_budget_error")
        if (
            abs(
                (float(self.surface_budget_after) - float(self.surface_budget_before))
                - float(self.surface_budget_error)
            )
            > 1e-12
        ):
            raise ValueError(
                "surface_budget_error must equal "
                "surface_budget_after - surface_budget_before"
            )
        _validate_surface_runtime_inputs(
            self.surface_kind,
            tuple(str(item) for item in self.runtime_visible_inputs),
        )
        _reject_forbidden_surface_keys(
            self.surface_values_before,
            context="surface_values_before",
        )
        _reject_forbidden_surface_keys(
            self.surface_values_after,
            context="surface_values_after",
        )
        _reject_forbidden_surface_keys(
            self.producer_records,
            context="producer_records",
        )
        for key, value in self.claim_flags.items():
            if not isinstance(key, str) or not isinstance(value, bool):
                raise ValueError("claim_flags must map strings to booleans")
            if key in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS and value:
                raise ValueError(f"surface row cannot promote claim flag: {key}")
        expected_digest = build_lgrc9v3_causal_pulse_substrate_surface_digest(
            self.to_artifact(include_digest=False)
        )
        if self.surface_digest is None:
            object.__setattr__(self, "surface_digest", expected_digest)
        elif self.surface_digest != expected_digest:
            raise ValueError("surface_digest does not match canonical row digest")

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        """Return a JSON-compatible surface row artifact."""

        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND,
            "artifact_schema_version": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_EVIDENCE_CLASS,
            "surface_id": self.surface_id,
            "schema_version": self.schema_version,
            "surface_policy_id": self.surface_policy_id,
            "surface_policy_enabled": self.surface_policy_enabled,
            "surface_policy_validated": self.surface_policy_validated,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "route_aspect_id": self.route_aspect_id,
            "route_aspect_digest": self.route_aspect_digest,
            "pulse_event_id": self.pulse_event_id,
            "pulse_packet_id": self.pulse_packet_id,
            "pulse_event_kind": self.pulse_event_kind,
            "pulse_channel_id": self.pulse_channel_id,
            "pulse_route_step": int(self.pulse_route_step),
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "node_proper_time": {
                str(int(node_id)): float(value)
                for node_id, value in sorted(self.node_proper_time.items())
            },
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "contact_amount": float(self.contact_amount),
            "surface_state_id": self.surface_state_id,
            "surface_state_digest": self.surface_state_digest,
            "surface_kind": self.surface_kind,
            "surface_nodes": [int(node_id) for node_id in self.surface_nodes],
            "surface_values_before": dict(self.surface_values_before),
            "surface_values_after": dict(self.surface_values_after),
            "runtime_visible_inputs": [str(item) for item in self.runtime_visible_inputs],
            "surface_update_policy": dict(self.surface_update_policy),
            "surface_budget_surface": self.surface_budget_surface,
            "surface_budget_before": float(self.surface_budget_before),
            "surface_budget_after": float(self.surface_budget_after),
            "surface_budget_error": float(self.surface_budget_error),
            "lineage_status": self.lineage_status,
            "producer_records": [dict(record) for record in self.producer_records],
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["surface_digest"] = self.surface_digest
        return artifact


def build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy(
    *,
    surface_policy_id: str = "native_causal_pulse_substrate_surface_disabled_v1",
) -> LGRC9V3CausalPulseSubstrateSurfacePolicy:
    """Build the default-off native pulse-substrate surface policy."""

    return LGRC9V3CausalPulseSubstrateSurfacePolicy(
        surface_policy_id=surface_policy_id,
    )


def build_lgrc9v3_causal_pulse_substrate_surface_contract_artifact() -> dict[str, Any]:
    """Return the native causal pulse-substrate surface contract artifact."""

    disabled_policy = (
        build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy()
    )
    return {
        "artifact_kind": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_KIND,
        "artifact_schema_version": (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_SCHEMA_VERSION
        ),
        "mode_version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "evidence_class": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_EVIDENCE_CLASS,
        "required_lgrc_level": LGRC_RUNTIME_LEVEL_LGRC2,
        "min_lgrc_level": 2,
        "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
        "fixed_topology_only": True,
        "topology_lineage_status": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED,
        "node_plus_packet_budget_invariant": LGRC9V3_PACKET_BUDGET_INVARIANT,
        "surface_accounting_separate_from_lgrc_budget": True,
        "claim_accounting_separate_from_surface_accounting": True,
        "producers_emit_claims": False,
        "producers_mutate_coherence": False,
        "producer_writable_fields": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_PRODUCER_WRITABLE_FIELDS
        ),
        "system_only_fields": [
            "surface_id",
            "schema_version",
            "surface_policy_id",
            "surface_policy_enabled",
            "surface_policy_validated",
            "lgrc_runtime_level",
            "surface_state_digest",
            "surface_budget_surface",
            "surface_budget_before",
            "surface_budget_after",
            "surface_budget_error",
            "lineage_status",
            "claim_flags",
            "surface_digest",
        ],
        "digest_specification": {
            "algorithm": "sha256",
            "canonicalization": "digest_canonical_data JSON canonical form",
            "excluded_fields": ["surface_digest"],
        },
        "surface_update_policy_schema": {
            "required_fields": [
                "policy_id",
                "version",
                "activation_gate",
                "allowed_surface_kinds",
            ],
            "policy_id": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED
            ),
            "version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION,
        },
        "synchronous_limit_behavior": {
            "surface_inert_without_packet_contact_events": True,
            "uniform_proper_time_rows_are_structurally_valid": True,
            "causal_advantage_claim_allowed": False,
        },
        "surface_policy": disabled_policy.to_artifact(),
        "surface_kinds": sorted(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KINDS),
        "surface_kind_runtime_visible_inputs": {
            key: list(value)
            for key, value in sorted(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS.items()
            )
        },
        "surface_policies": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICIES
        ),
        "surface_budget_surfaces": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_SURFACES
        ),
        "lineage_statuses": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_STATUSES
        ),
        "surface_lineage_transport": {
            "enabled": False,
            "validated": False,
            "supported": False,
            "required_lgrc_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "causal_layer_mode": (
                CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
            ),
            "policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED
            ),
            "policies": sorted(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICIES
            ),
            "lineage_actions": sorted(
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTIONS
            ),
            "idempotency_key_fields": [
                "source_surface_digest",
                "topology_event_digest",
                "surface_lineage_policy_id",
                "lineage_action",
                "lineage_transfer_map_digest",
            ],
            "topology_event_digest": {
                "algorithm": "sha256",
                "canonicalization": "digest_canonical_data JSON canonical form",
                "excluded_fields": ["topology_event_digest"],
            },
            "port_fields": {
                "source_surface_ports": "optional_kind_specific",
                "target_surface_ports": "optional_kind_specific",
            },
        },
        "forbidden_surface_keys": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS
        ),
        "surface_row_required_fields": sorted(
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_REQUIRED_FIELDS
        ),
        "surface_row_field_names": dict(
            vars(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES)
        ),
        "surface_lineage_record_field_names": dict(
            vars(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_FIELD_NAMES)
        ),
        "native_claim_flags": {
            "native_causal_pulse_substrate_surface_enabled": False,
            "native_causal_pulse_substrate_surface_validated": False,
            "native_lgrc_pulse_substrate_supported": False,
            "native_causal_pulse_substrate_surface_lineage_transport_enabled": (
                False
            ),
            "native_causal_pulse_substrate_surface_lineage_transport_validated": (
                False
            ),
            "native_causal_pulse_substrate_surface_lineage_transport_supported": (
                False
            ),
            "native_pulse_substrate_coupling_producer_enabled": False,
            "native_feedback_coupled_pulse_producer_enabled": False,
            "native_m6": False,
            "movement_claim_allowed": False,
        },
    }


def build_lgrc9v3_causal_pulse_substrate_surface_digest(
    surface_row: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one surface row."""

    payload = dict(surface_row)
    payload.pop("surface_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_causal_pulse_substrate_surface_row": payload}
    )


def build_lgrc9v3_topology_event_digest(
    topology_event_artifact: Mapping[str, Any],
) -> str:
    """Return a stable derived digest for one topology event artifact."""

    payload = dict(topology_event_artifact)
    payload.pop("topology_event_digest", None)
    # The arbitration digest can back-reference this topology-event digest, so
    # keep it out of the event identity to avoid circular digest dependencies.
    payload.pop("native_route_arbitration_digest", None)
    return digest_canonical_data({"lgrc9v3_topology_event": payload})


def build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest(
    lineage_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one surface-lineage record."""

    payload = dict(lineage_record)
    payload.pop("lineage_record_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_causal_pulse_substrate_surface_lineage_record": payload}
    )


def build_lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_key(
    *,
    source_surface_digest: str,
    topology_event_digest: str,
    surface_lineage_policy_id: str,
    lineage_action: str,
    lineage_transfer_map_digest: str,
) -> str:
    """Return the lineage record idempotency key."""

    return digest_canonical_data(
        {
            "source_surface_digest": _nonempty_string(
                source_surface_digest,
                context="source_surface_digest",
            ),
            "topology_event_digest": _nonempty_string(
                topology_event_digest,
                context="topology_event_digest",
            ),
            "surface_lineage_policy_id": _nonempty_string(
                surface_lineage_policy_id,
                context="surface_lineage_policy_id",
            ),
            "lineage_action": _nonempty_string(
                lineage_action,
                context="lineage_action",
            ),
            "lineage_transfer_map_digest": _nonempty_string(
                lineage_transfer_map_digest,
                context="lineage_transfer_map_digest",
            ),
        }
    )


def build_lgrc9v3_topology_state_reabsorption_record_digest(
    reabsorption_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one state reabsorption record."""

    payload = dict(reabsorption_record)
    payload.pop("topology_state_reabsorption_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_topology_state_reabsorption_record": payload}
    )


def build_lgrc9v3_topology_state_reabsorption_idempotency_key(
    *,
    topology_event_digest: str,
    lineage_transfer_map_digest: str,
    topology_state_reabsorption_policy_id: str,
    state_reabsorption_action: str,
    packet_ledger_digest_before: str,
    active_state_digest_before: str,
) -> str:
    """Return the canonical topology-state reabsorption idempotency key."""

    return digest_canonical_data(
        {
            "topology_event_digest": _nonempty_string(
                topology_event_digest,
                context="topology_event_digest",
            ),
            "lineage_transfer_map_digest": _nonempty_string(
                lineage_transfer_map_digest,
                context="lineage_transfer_map_digest",
            ),
            "topology_state_reabsorption_policy_id": _nonempty_string(
                topology_state_reabsorption_policy_id,
                context="topology_state_reabsorption_policy_id",
            ),
            "state_reabsorption_action": _nonempty_string(
                state_reabsorption_action,
                context="state_reabsorption_action",
            ),
            "packet_ledger_digest_before": _nonempty_string(
                packet_ledger_digest_before,
                context="packet_ledger_digest_before",
            ),
            "active_state_digest_before": _nonempty_string(
                active_state_digest_before,
                context="active_state_digest_before",
            ),
        }
    )


def build_lgrc9v3_native_route_candidate_record_digest(
    candidate_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one native route candidate."""

    payload = dict(candidate_record)
    payload.pop("candidate_route_digest", None)
    return digest_canonical_data({"lgrc9v3_native_route_candidate_record": payload})


def build_lgrc9v3_native_route_candidate_set_record_digest(
    candidate_set_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one native route candidate set."""

    payload = dict(candidate_set_record)
    payload.pop("candidate_set_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_native_route_candidate_set_record": payload}
    )


def build_lgrc9v3_native_route_candidate_set_idempotency_key(
    *,
    native_route_arbitration_policy_id: str,
    arbitration_window_id: str,
    event_time_key: float,
    candidate_route_digests: Sequence[str],
    candidate_set_order_key: str,
) -> str:
    """Return the canonical native route candidate-set idempotency key."""

    return digest_canonical_data(
        {
            "native_route_arbitration_policy_id": _nonempty_string(
                native_route_arbitration_policy_id,
                context="native_route_arbitration_policy_id",
            ),
            "arbitration_window_id": _nonempty_string(
                arbitration_window_id,
                context="arbitration_window_id",
            ),
            "event_time_key": _finite_float(event_time_key, context="event_time_key"),
            "candidate_route_digests": [
                _nonempty_string(digest, context="candidate_route_digests[]")
                for digest in candidate_route_digests
            ],
            "candidate_set_order_key": _nonempty_string(
                candidate_set_order_key,
                context="candidate_set_order_key",
            ),
        }
    )


def build_lgrc9v3_native_route_arbitration_record_digest(
    arbitration_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one route-arbitration record."""

    payload = dict(arbitration_record)
    payload.pop("native_route_arbitration_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_native_route_arbitration_record": payload}
    )


def build_lgrc9v3_native_route_arbitration_idempotency_key(
    *,
    native_route_arbitration_policy_id: str,
    candidate_set_digest: str,
    selected_candidate_route_digest: str | None,
    arbitration_reason_code: str,
    arbitration_rule: str,
    selected_topology_event_id: str | None,
) -> str:
    """Return the canonical native route-arbitration idempotency key."""

    return digest_canonical_data(
        {
            "native_route_arbitration_policy_id": _nonempty_string(
                native_route_arbitration_policy_id,
                context="native_route_arbitration_policy_id",
            ),
            "candidate_set_digest": _nonempty_string(
                candidate_set_digest,
                context="candidate_set_digest",
            ),
            "selected_candidate_route_digest": selected_candidate_route_digest or "",
            "arbitration_reason_code": _nonempty_string(
                arbitration_reason_code,
                context="arbitration_reason_code",
            ),
            "arbitration_rule": _nonempty_string(
                arbitration_rule,
                context="arbitration_rule",
            ),
            "selected_topology_event_id": selected_topology_event_id or "",
        }
    )


def build_lgrc9v3_multi_basin_flow_window_record_digest(
    flow_window_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one post-refinement flow window."""

    payload = dict(flow_window_record)
    payload.pop("post_refinement_flow_window_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_multi_basin_post_refinement_flow_window_record": payload}
    )


def build_lgrc9v3_child_basin_state_record_digest(
    child_basin_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one child-basin state record."""

    payload = dict(child_basin_record)
    payload.pop("child_basin_state_digest", None)
    return digest_canonical_data({"lgrc9v3_child_basin_state_record": payload})


def build_lgrc9v3_multi_basin_replay_validation_record_digest(
    replay_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one multi-basin replay record."""

    payload = dict(replay_record)
    payload.pop("replay_validation_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_multi_basin_replay_validation_record": payload}
    )


def build_lgrc9v3_multi_basin_control_record_digest(
    control_record: Mapping[str, Any],
) -> str:
    """Return the stable canonical digest for one merge/leakage control record."""

    payload = dict(control_record)
    payload.pop("control_record_digest", None)
    return digest_canonical_data(
        {"lgrc9v3_multi_basin_merge_leakage_control_record": payload}
    )


@dataclass(frozen=True)
class LGRC9V3CausalPulseSubstrateSurfaceLineageRecord:
    """Evidence transport or supersession for a surface row after topology.

    The record is passive schema evidence. It does not emit topology changes,
    mutate coherence, or make movement claims.
    """

    surface_lineage_record_id: str
    surface_lineage_policy_id: str
    surface_lineage_transport_enabled: bool
    source_surface_id: str
    source_surface_digest: str
    topology_event_id: str
    topology_event_kind: str
    topology_event_digest: str
    event_time_key: float
    scheduler_event_index: int
    checkpoint_index: int
    lineage_transfer_map: Mapping[str, str]
    source_surface_nodes: Sequence[int]
    target_surface_nodes: Sequence[int]
    lineage_action: str
    lineage_status: str
    surface_budget_surface: str
    surface_budget_before: float
    surface_budget_after: float
    surface_budget_error: float
    node_plus_packet_budget_before: float
    node_plus_packet_budget_after: float
    node_plus_packet_budget_error: float
    surface_lineage_transport_validated: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    source_surface_ports: Sequence[str] | None = None
    target_surface_ports: Sequence[str] | None = None
    transported_surface_id: str | None = None
    transported_surface_digest: str | None = None
    superseded_surface_id: str | None = None
    producer_stale_read_blocker: str | None = None
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = (
        LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION
    )
    idempotency_key: str | None = None
    lineage_record_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "surface_lineage_record_id",
            "surface_lineage_policy_id",
            "source_surface_id",
            "source_surface_digest",
            "topology_event_id",
            "topology_event_kind",
            "topology_event_digest",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION
        ):
            raise ValueError("unsupported surface lineage record schema")
        for field_name in (
            "surface_lineage_transport_enabled",
            "surface_lineage_transport_validated",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be boolean")
        if not self.surface_lineage_transport_enabled:
            raise ValueError("surface lineage record requires enabled transport policy")
        if self.lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC3:
            raise ValueError(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3)
        if (
            self.causal_layer_mode
            != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
        ):
            raise ValueError(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3)
        if self.topology_event_kind not in LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS:
            raise ValueError("unsupported topology_event_kind")
        if self.lineage_action not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTIONS:
            raise ValueError("unsupported lineage_action")
        if self.lineage_status not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_STATUSES:
            raise ValueError("unsupported lineage_status")
        expected_status = (
            LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED
            if self.lineage_action
            == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
            else LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED
        )
        if self.lineage_status != expected_status:
            raise ValueError("lineage_status must match lineage_action")
        if not self.lineage_transfer_map:
            raise ValueError("lineage_transfer_map must not be empty")
        for key, value in self.lineage_transfer_map.items():
            _nonempty_string(key, context="lineage_transfer_map.key")
            _nonempty_string(value, context=f"lineage_transfer_map[{key}]")
        if not self.source_surface_nodes:
            raise ValueError("source_surface_nodes must not be empty")
        if any(int(node_id) < 0 for node_id in self.source_surface_nodes):
            raise ValueError("source_surface_nodes must be nonnegative node ids")
        if self.lineage_action == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED:
            if not self.target_surface_nodes:
                raise ValueError("transported records require target_surface_nodes")
            if not self.transported_surface_id or not self.transported_surface_digest:
                raise ValueError("transported records require transported surface ids")
        if any(int(node_id) < 0 for node_id in self.target_surface_nodes):
            raise ValueError("target_surface_nodes must be nonnegative node ids")
        for field_name in ("source_surface_ports", "target_surface_ports"):
            ports = getattr(self, field_name)
            if ports is not None:
                for port in ports:
                    _nonempty_string(port, context=f"{field_name}[]")
        if self.lineage_action == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED:
            if not self.superseded_surface_id:
                raise ValueError("superseded records require superseded_surface_id")
            if not self.producer_stale_read_blocker:
                raise ValueError(
                    "superseded records require producer_stale_read_blocker"
                )
        if (
            self.surface_budget_surface
            not in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_SURFACES
        ):
            raise ValueError("unsupported surface_budget_surface")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        if int(self.checkpoint_index) < 0:
            raise ValueError("checkpoint_index must be >= 0")
        _finite_float(self.surface_budget_before, context="surface_budget_before")
        _finite_float(self.surface_budget_after, context="surface_budget_after")
        _finite_float(self.surface_budget_error, context="surface_budget_error")
        _finite_float(
            self.node_plus_packet_budget_before,
            context="node_plus_packet_budget_before",
        )
        _finite_float(
            self.node_plus_packet_budget_after,
            context="node_plus_packet_budget_after",
        )
        _finite_float(
            self.node_plus_packet_budget_error,
            context="node_plus_packet_budget_error",
        )
        if (
            abs(
                (float(self.surface_budget_after) - float(self.surface_budget_before))
                - float(self.surface_budget_error)
            )
            > 1e-12
        ):
            raise ValueError(
                "surface_budget_error must equal "
                "surface_budget_after - surface_budget_before"
            )
        if (
            abs(
                (
                    float(self.node_plus_packet_budget_after)
                    - float(self.node_plus_packet_budget_before)
                )
                - float(self.node_plus_packet_budget_error)
            )
            > 1e-12
        ):
            raise ValueError(
                "node_plus_packet_budget_error must equal "
                "node_plus_packet_budget_after - node_plus_packet_budget_before"
            )
        for key, value in self.claim_flags.items():
            if not isinstance(key, str) or not isinstance(value, bool):
                raise ValueError("claim_flags must map strings to booleans")
            if key in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS and value:
                raise ValueError(f"lineage record cannot promote claim flag: {key}")
        lineage_transfer_map_digest = digest_canonical_data(
            {"lineage_transfer_map": dict(sorted(self.lineage_transfer_map.items()))}
        )
        expected_idempotency_key = (
            build_lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_key(
                source_surface_digest=self.source_surface_digest,
                topology_event_digest=self.topology_event_digest,
                surface_lineage_policy_id=self.surface_lineage_policy_id,
                lineage_action=self.lineage_action,
                lineage_transfer_map_digest=lineage_transfer_map_digest,
            )
        )
        if self.idempotency_key is None:
            object.__setattr__(self, "idempotency_key", expected_idempotency_key)
        elif self.idempotency_key != expected_idempotency_key:
            raise ValueError("idempotency_key does not match canonical lineage key")
        expected_digest = (
            build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest(
                self.to_artifact(include_digest=False)
            )
        )
        if self.lineage_record_digest is None:
            object.__setattr__(self, "lineage_record_digest", expected_digest)
        elif self.lineage_record_digest != expected_digest:
            raise ValueError(
                "lineage_record_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        """Return a JSON-compatible surface-lineage record."""

        artifact: dict[str, Any] = {
            "artifact_kind": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND
            ),
            "artifact_schema_version": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_EVIDENCE_CLASS,
            "surface_lineage_record_id": self.surface_lineage_record_id,
            "schema_version": self.schema_version,
            "surface_lineage_policy_id": self.surface_lineage_policy_id,
            "surface_lineage_transport_enabled": (
                self.surface_lineage_transport_enabled
            ),
            "surface_lineage_transport_validated": (
                self.surface_lineage_transport_validated
            ),
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "source_surface_id": self.source_surface_id,
            "source_surface_digest": self.source_surface_digest,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": self.topology_event_kind,
            "topology_event_digest": self.topology_event_digest,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "lineage_transfer_map": dict(sorted(self.lineage_transfer_map.items())),
            "source_surface_nodes": [
                int(node_id) for node_id in self.source_surface_nodes
            ],
            "target_surface_nodes": [
                int(node_id) for node_id in self.target_surface_nodes
            ],
            "source_surface_ports": (
                None
                if self.source_surface_ports is None
                else [str(port) for port in self.source_surface_ports]
            ),
            "target_surface_ports": (
                None
                if self.target_surface_ports is None
                else [str(port) for port in self.target_surface_ports]
            ),
            "lineage_action": self.lineage_action,
            "lineage_status": self.lineage_status,
            "surface_budget_surface": self.surface_budget_surface,
            "surface_budget_before": float(self.surface_budget_before),
            "surface_budget_after": float(self.surface_budget_after),
            "surface_budget_error": float(self.surface_budget_error),
            "node_plus_packet_budget_before": float(
                self.node_plus_packet_budget_before
            ),
            "node_plus_packet_budget_after": float(
                self.node_plus_packet_budget_after
            ),
            "node_plus_packet_budget_error": float(
                self.node_plus_packet_budget_error
            ),
            "transported_surface_id": self.transported_surface_id,
            "transported_surface_digest": self.transported_surface_digest,
            "superseded_surface_id": self.superseded_surface_id,
            "producer_stale_read_blocker": self.producer_stale_read_blocker,
            "claim_flags": dict(sorted(self.claim_flags.items())),
            "idempotency_key": self.idempotency_key,
        }
        if include_digest:
            artifact["lineage_record_digest"] = self.lineage_record_digest
        return artifact


@dataclass(frozen=True)
class LGRC9V3TopologyStateReabsorptionRecord:
    """Evidence that a committed topology event rebased live state and ledger.

    The record is schema evidence only. Runtime mutation is added in later
    iterations and must remain attributable to committed topology machinery.
    """

    topology_state_reabsorption_record_id: str
    topology_state_reabsorption_policy_id: str
    topology_state_reabsorption_enabled: bool
    topology_event_id: str
    topology_event_kind: str
    topology_event_digest: str
    topology_event_committed: bool
    event_time_key: float
    scheduler_event_index: int
    checkpoint_index: int
    lineage_transfer_map: Mapping[str, str]
    source_node_ids: Sequence[int]
    target_node_ids: Sequence[int]
    retired_node_ids: Sequence[int]
    source_edge_ids: Sequence[int]
    target_edge_ids: Sequence[int]
    retired_edge_ids: Sequence[int]
    node_state_before: Mapping[int, float]
    node_state_after: Mapping[int, float]
    edge_state_before: Mapping[int, Mapping[int, float]]
    edge_state_after: Mapping[int, Mapping[int, float]]
    packet_ledger_digest_before: str
    packet_ledger_digest_after: str
    active_node_state_total_before: float
    active_node_state_total_after: float
    packet_ledger_node_total_before: float
    packet_ledger_node_total_after: float
    packet_ledger_in_flight_packet_total_before: float
    packet_ledger_in_flight_packet_total_after: float
    packet_ledger_conserved_budget_total_before: float
    packet_ledger_conserved_budget_total_after: float
    node_plus_packet_budget_before: float
    node_plus_packet_budget_after: float
    node_plus_packet_budget_error: float
    active_state_digest_before: str
    active_state_digest_after: str
    state_reabsorption_action: str
    topology_state_reabsorption_validated: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION
    idempotency_key: str | None = None
    topology_state_reabsorption_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "topology_state_reabsorption_record_id",
            "topology_state_reabsorption_policy_id",
            "topology_event_id",
            "topology_event_kind",
            "topology_event_digest",
            "packet_ledger_digest_before",
            "packet_ledger_digest_after",
            "active_state_digest_before",
            "active_state_digest_after",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported topology-state reabsorption schema")
        for field_name in (
            "topology_state_reabsorption_enabled",
            "topology_state_reabsorption_validated",
            "topology_event_committed",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ValueError(f"{field_name} must be boolean")
        if not self.topology_event_committed:
            raise ValueError(
                "topology-state reabsorption requires committed topology event"
            )
        if not self.topology_state_reabsorption_enabled:
            raise ValueError(
                "topology-state reabsorption record requires enabled policy"
            )
        if (
            self.topology_state_reabsorption_policy_id
            == LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED
        ):
            raise ValueError(
                "topology-state reabsorption record requires active policy"
            )
        if self.lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC3:
            raise ValueError(LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3)
        if (
            self.causal_layer_mode
            != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
        ):
            raise ValueError(LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3)
        if self.topology_event_kind not in LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS:
            raise ValueError("unsupported topology_event_kind")
        if self.state_reabsorption_action not in LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTIONS:
            raise ValueError("unsupported state_reabsorption_action")
        if not self.lineage_transfer_map:
            raise ValueError("lineage_transfer_map must not be empty")
        for key, value in self.lineage_transfer_map.items():
            _nonempty_string(key, context="lineage_transfer_map.key")
            _nonempty_string(value, context=f"lineage_transfer_map[{key}]")
        for field_name in (
            "source_node_ids",
            "target_node_ids",
            "retired_node_ids",
            "source_edge_ids",
            "target_edge_ids",
            "retired_edge_ids",
        ):
            for item in getattr(self, field_name):
                if int(item) < 0:
                    raise ValueError(f"{field_name} must contain nonnegative ids")
        if not self.source_node_ids:
            raise ValueError("source_node_ids must not be empty")
        missing_lineage_sources = {
            str(int(node_id))
            for node_id in self.source_node_ids
            if str(int(node_id)) not in self.lineage_transfer_map
        }
        if missing_lineage_sources:
            raise ValueError(
                "lineage_transfer_map must cover every source_node_id"
            )
        if self.state_reabsorption_action in {
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED,
            LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED,
        } and not self.target_node_ids:
            raise ValueError("rebased or merged records require target_node_ids")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        if int(self.checkpoint_index) < 0:
            raise ValueError("checkpoint_index must be >= 0")
        for field_name in ("node_state_before", "node_state_after"):
            mapping = getattr(self, field_name)
            if not mapping:
                raise ValueError(f"{field_name} must not be empty")
            for node_id, coherence in mapping.items():
                if int(node_id) < 0:
                    raise ValueError(f"{field_name} keys must be nonnegative ids")
                _finite_float(coherence, context=f"{field_name}[{node_id}]")
        for field_name in ("edge_state_before", "edge_state_after"):
            for edge_id, edge_values in getattr(self, field_name).items():
                if int(edge_id) < 0:
                    raise ValueError(f"{field_name} keys must be nonnegative ids")
                for value_key, value in edge_values.items():
                    if int(value_key) < 0:
                        raise ValueError(
                            f"{field_name}[{edge_id}] keys must be nonnegative ids"
                        )
                    _finite_float(value, context=f"{field_name}[{edge_id}][{value_key}]")
        for field_name in (
            "active_node_state_total_before",
            "active_node_state_total_after",
            "packet_ledger_node_total_before",
            "packet_ledger_node_total_after",
            "packet_ledger_in_flight_packet_total_before",
            "packet_ledger_in_flight_packet_total_after",
            "packet_ledger_conserved_budget_total_before",
            "packet_ledger_conserved_budget_total_after",
        ):
            _finite_float(getattr(self, field_name), context=field_name)
        node_state_before_total = sum(float(value) for value in self.node_state_before.values())
        node_state_after_total = sum(float(value) for value in self.node_state_after.values())
        if abs(node_state_before_total - float(self.active_node_state_total_before)) > 1e-12:
            raise ValueError(
                "active_node_state_total_before must equal sum(node_state_before)"
            )
        if abs(node_state_after_total - float(self.active_node_state_total_after)) > 1e-12:
            raise ValueError(
                "active_node_state_total_after must equal sum(node_state_after)"
            )
        if (
            abs(
                float(self.packet_ledger_node_total_before)
                - float(self.active_node_state_total_before)
            )
            > 1e-12
        ):
            raise ValueError(
                "packet_ledger_node_total_before must match active state total"
            )
        if (
            abs(
                float(self.packet_ledger_node_total_after)
                - float(self.active_node_state_total_after)
            )
            > 1e-12
        ):
            raise ValueError(
                "packet_ledger_node_total_after must match active state total"
            )
        if (
            abs(
                (
                    float(self.packet_ledger_node_total_before)
                    + float(self.packet_ledger_in_flight_packet_total_before)
                )
                - float(self.packet_ledger_conserved_budget_total_before)
            )
            > 1e-12
        ):
            raise ValueError(
                "packet ledger before totals must sum to conserved budget"
            )
        if (
            abs(
                (
                    float(self.packet_ledger_node_total_after)
                    + float(self.packet_ledger_in_flight_packet_total_after)
                )
                - float(self.packet_ledger_conserved_budget_total_after)
            )
            > 1e-12
        ):
            raise ValueError(
                "packet ledger after totals must sum to conserved budget"
            )
        _finite_float(
            self.node_plus_packet_budget_before,
            context="node_plus_packet_budget_before",
        )
        _finite_float(
            self.node_plus_packet_budget_after,
            context="node_plus_packet_budget_after",
        )
        _finite_float(
            self.node_plus_packet_budget_error,
            context="node_plus_packet_budget_error",
        )
        if (
            abs(
                float(self.node_plus_packet_budget_before)
                - float(self.packet_ledger_conserved_budget_total_before)
            )
            > 1e-12
        ):
            raise ValueError(
                "node_plus_packet_budget_before must match packet ledger "
                "conserved budget before"
            )
        if (
            abs(
                float(self.node_plus_packet_budget_after)
                - float(self.packet_ledger_conserved_budget_total_after)
            )
            > 1e-12
        ):
            raise ValueError(
                "node_plus_packet_budget_after must match packet ledger "
                "conserved budget after"
            )
        if (
            abs(
                (
                    float(self.node_plus_packet_budget_after)
                    - float(self.node_plus_packet_budget_before)
                )
                - float(self.node_plus_packet_budget_error)
            )
            > 1e-12
        ):
            raise ValueError(
                "node_plus_packet_budget_error must equal "
                "node_plus_packet_budget_after - node_plus_packet_budget_before"
            )
        for key, value in self.claim_flags.items():
            if not isinstance(key, str) or not isinstance(value, bool):
                raise ValueError("claim_flags must map strings to booleans")
            if key in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS and value:
                raise ValueError(
                    "topology-state reabsorption record cannot promote claim "
                    f"flag: {key}"
                )
        lineage_transfer_map_digest = digest_canonical_data(
            {"lineage_transfer_map": dict(sorted(self.lineage_transfer_map.items()))}
        )
        expected_idempotency_key = (
            build_lgrc9v3_topology_state_reabsorption_idempotency_key(
                topology_event_digest=self.topology_event_digest,
                lineage_transfer_map_digest=lineage_transfer_map_digest,
                topology_state_reabsorption_policy_id=(
                    self.topology_state_reabsorption_policy_id
                ),
                state_reabsorption_action=self.state_reabsorption_action,
                packet_ledger_digest_before=self.packet_ledger_digest_before,
                active_state_digest_before=self.active_state_digest_before,
            )
        )
        if self.idempotency_key is None:
            object.__setattr__(self, "idempotency_key", expected_idempotency_key)
        elif self.idempotency_key != expected_idempotency_key:
            raise ValueError(
                "idempotency_key does not match canonical topology-state "
                "reabsorption key"
            )
        expected_digest = build_lgrc9v3_topology_state_reabsorption_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.topology_state_reabsorption_digest is None:
            object.__setattr__(
                self,
                "topology_state_reabsorption_digest",
                expected_digest,
            )
        elif self.topology_state_reabsorption_digest != expected_digest:
            raise ValueError(
                "topology_state_reabsorption_digest does not match canonical "
                "record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        """Return a JSON-compatible topology-state reabsorption record."""

        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "topology_state_reabsorption",
            "topology_state_reabsorption_record_id": (
                self.topology_state_reabsorption_record_id
            ),
            "schema_version": self.schema_version,
            "topology_state_reabsorption_policy_id": (
                self.topology_state_reabsorption_policy_id
            ),
            "topology_state_reabsorption_enabled": (
                self.topology_state_reabsorption_enabled
            ),
            "topology_state_reabsorption_validated": (
                self.topology_state_reabsorption_validated
            ),
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": self.topology_event_kind,
            "topology_event_digest": self.topology_event_digest,
            "topology_event_committed": self.topology_event_committed,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "lineage_transfer_map": dict(sorted(self.lineage_transfer_map.items())),
            "lineage_transfer_map_digest": digest_canonical_data(
                {
                    "lineage_transfer_map": dict(
                        sorted(self.lineage_transfer_map.items())
                    )
                }
            ),
            "source_node_ids": [int(node_id) for node_id in self.source_node_ids],
            "target_node_ids": [int(node_id) for node_id in self.target_node_ids],
            "retired_node_ids": [int(node_id) for node_id in self.retired_node_ids],
            "source_edge_ids": [int(edge_id) for edge_id in self.source_edge_ids],
            "target_edge_ids": [int(edge_id) for edge_id in self.target_edge_ids],
            "retired_edge_ids": [int(edge_id) for edge_id in self.retired_edge_ids],
            "node_state_before": _string_keyed_float_map(self.node_state_before),
            "node_state_after": _string_keyed_float_map(self.node_state_after),
            "edge_state_before": _string_keyed_nested_float_map(
                self.edge_state_before
            ),
            "edge_state_after": _string_keyed_nested_float_map(self.edge_state_after),
            "packet_ledger_digest_before": self.packet_ledger_digest_before,
            "packet_ledger_digest_after": self.packet_ledger_digest_after,
            "active_node_state_total_before": float(
                self.active_node_state_total_before
            ),
            "active_node_state_total_after": float(
                self.active_node_state_total_after
            ),
            "packet_ledger_node_total_before": float(
                self.packet_ledger_node_total_before
            ),
            "packet_ledger_node_total_after": float(
                self.packet_ledger_node_total_after
            ),
            "packet_ledger_in_flight_packet_total_before": float(
                self.packet_ledger_in_flight_packet_total_before
            ),
            "packet_ledger_in_flight_packet_total_after": float(
                self.packet_ledger_in_flight_packet_total_after
            ),
            "packet_ledger_conserved_budget_total_before": float(
                self.packet_ledger_conserved_budget_total_before
            ),
            "packet_ledger_conserved_budget_total_after": float(
                self.packet_ledger_conserved_budget_total_after
            ),
            "node_plus_packet_budget_before": float(
                self.node_plus_packet_budget_before
            ),
            "node_plus_packet_budget_after": float(self.node_plus_packet_budget_after),
            "node_plus_packet_budget_error": float(self.node_plus_packet_budget_error),
            "active_state_digest_before": self.active_state_digest_before,
            "active_state_digest_after": self.active_state_digest_after,
            "state_reabsorption_action": self.state_reabsorption_action,
            "claim_flags": dict(sorted(self.claim_flags.items())),
            "idempotency_key": self.idempotency_key,
        }
        if include_digest:
            artifact["topology_state_reabsorption_digest"] = (
                self.topology_state_reabsorption_digest
            )
        return artifact


def _validate_native_route_runtime_context(
    *,
    enabled: bool,
    policy_id: str,
    lgrc_runtime_level: str,
    causal_layer_mode: str,
    context: str,
) -> None:
    if not isinstance(enabled, bool):
        raise ValueError(f"{context} enabled flag must be boolean")
    if policy_id not in LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICIES:
        raise ValueError("unsupported native route-arbitration policy")
    if not enabled:
        raise ValueError(f"{context} requires native route arbitration enabled")
    if policy_id == LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED:
        raise ValueError(f"{context} requires active native route-arbitration policy")
    if lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC3:
        raise ValueError("native_lgrc_route_arbitration_requires_lgrc3")
    if causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY:
        raise ValueError("native_lgrc_route_arbitration_requires_lgrc3")


def _validate_native_route_claim_flags(
    claim_flags: Mapping[str, bool],
    *,
    context: str,
) -> None:
    for key, value in claim_flags.items():
        if not isinstance(key, str) or not isinstance(value, bool):
            raise ValueError(f"{context} claim_flags must map strings to booleans")
        if key in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS and value:
            raise ValueError(f"{context} cannot promote claim flag: {key}")


def _validate_native_route_inputs(inputs: Sequence[str], *, context: str) -> tuple[str, ...]:
    if not isinstance(inputs, Sequence) or isinstance(inputs, (str, bytes)):
        raise ValueError(f"{context} must be a sequence")
    resolved = tuple(_nonempty_string(str(value), context=f"{context}[]") for value in inputs)
    if not resolved:
        raise ValueError(f"{context} must not be empty")
    forbidden = set(resolved).intersection(
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS
    )
    if forbidden:
        raise ValueError(
            "native route-arbitration inputs contain hidden inputs: "
            f"{sorted(forbidden)}"
        )
    return resolved


def _validate_native_route_budget_prediction(
    budget_prediction: Mapping[str, float],
) -> dict[str, float]:
    required = {
        "node_plus_packet_budget_before",
        "node_plus_packet_budget_after",
        "node_plus_packet_budget_error",
    }
    missing = required - set(budget_prediction)
    if missing:
        raise ValueError(
            f"candidate_budget_prediction missing fields: {sorted(missing)}"
        )
    parsed = {
        str(key): _finite_float(value, context=f"candidate_budget_prediction[{key}]")
        for key, value in budget_prediction.items()
    }
    if (
        abs(
            (
                parsed["node_plus_packet_budget_after"]
                - parsed["node_plus_packet_budget_before"]
            )
            - parsed["node_plus_packet_budget_error"]
        )
        > 1e-12
    ):
        raise ValueError(
            "candidate budget error must equal after - before"
        )
    return dict(sorted(parsed.items()))


def _lineage_transfer_map_digest(lineage_transfer_map: Mapping[str, str]) -> str:
    return digest_canonical_data(
        {"lineage_transfer_map": dict(sorted(lineage_transfer_map.items()))}
    )


def _validate_multi_basin_runtime_context(
    *,
    enabled: bool,
    policy_id: str,
    lgrc_runtime_level: str,
    causal_layer_mode: str,
    context: str,
) -> None:
    if not isinstance(enabled, bool):
        raise ValueError(f"{context} enabled flag must be boolean")
    if policy_id not in LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICIES:
        raise ValueError("unsupported native multi-basin formation policy")
    if not enabled:
        raise ValueError(f"{context} requires native multi-basin formation enabled")
    if policy_id == LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED:
        raise ValueError(f"{context} requires active multi-basin formation policy")
    if lgrc_runtime_level != LGRC_RUNTIME_LEVEL_LGRC3:
        raise ValueError("native_lgrc_multi_basin_formation_requires_lgrc3")
    if causal_layer_mode != CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY:
        raise ValueError("native_lgrc_multi_basin_formation_requires_lgrc3")


def _validate_multi_basin_claim_flags(
    claim_flags: Mapping[str, bool],
    *,
    context: str,
) -> None:
    for key, value in claim_flags.items():
        if not isinstance(key, str) or not isinstance(value, bool):
            raise ValueError(f"{context} claim_flags must map strings to booleans")
        if key in LGRC9V3_MULTI_BASIN_FORBIDDEN_CLAIM_KEYS and value:
            raise ValueError(f"{context} cannot promote claim flag: {key}")


def _validate_multi_basin_inputs(
    inputs: Sequence[str],
    *,
    context: str,
) -> tuple[str, ...]:
    if not isinstance(inputs, Sequence) or isinstance(inputs, (str, bytes)):
        raise ValueError(f"{context} must be a sequence")
    resolved = tuple(_nonempty_string(str(value), context=f"{context}[]") for value in inputs)
    if not resolved:
        raise ValueError(f"{context} must not be empty")
    forbidden = set(resolved).intersection(LGRC9V3_MULTI_BASIN_FORBIDDEN_INPUTS)
    if forbidden:
        raise ValueError(
            "multi-basin formation inputs contain hidden or relabel inputs: "
            f"{sorted(forbidden)}"
        )
    return resolved


def _validate_multi_basin_budget_trace(
    budget_trace: Mapping[str, float],
    *,
    context: str,
) -> dict[str, float]:
    required = {
        "node_plus_packet_budget_before",
        "node_plus_packet_budget_after",
        "node_plus_packet_budget_error",
    }
    missing = required - set(budget_trace)
    if missing:
        raise ValueError(f"{context} missing fields: {sorted(missing)}")
    resolved = {
        _nonempty_string(str(key), context=f"{context}.key"): _finite_float(
            value,
            context=f"{context}[{key}]",
        )
        for key, value in budget_trace.items()
    }
    before = resolved["node_plus_packet_budget_before"]
    after = resolved["node_plus_packet_budget_after"]
    error = resolved["node_plus_packet_budget_error"]
    if abs((after - before) - error) > 1e-9:
        raise ValueError(f"{context} error must equal after-before")
    return dict(sorted(resolved.items()))


def _validate_multi_basin_float_map(
    values: Mapping[Any, Any],
    *,
    context: str,
) -> dict[str, float]:
    if not isinstance(values, Mapping):
        raise ValueError(f"{context} must be a mapping")
    resolved = {
        _nonempty_string(str(key), context=f"{context}.key"): _finite_float(
            value,
            context=f"{context}[{key}]",
        )
        for key, value in values.items()
    }
    if not resolved:
        raise ValueError(f"{context} must not be empty")
    return dict(sorted(resolved.items()))


def _validate_multi_basin_sequence_map(
    values: Mapping[Any, Sequence[int]],
    *,
    context: str,
) -> dict[str, tuple[int, ...]]:
    if not isinstance(values, Mapping):
        raise ValueError(f"{context} must be a mapping")
    resolved = {
        _nonempty_string(str(key), context=f"{context}.key"): _nonnegative_int_tuple(
            tuple(int(value) for value in sequence),
            context=f"{context}[{key}]",
        )
        for key, sequence in values.items()
    }
    if not resolved:
        raise ValueError(f"{context} must not be empty")
    return dict(sorted(resolved.items()))


def _validate_multi_basin_ratio(value: Any, *, context: str) -> float:
    resolved = _finite_float(value, context=context)
    if resolved < 0.0 or resolved > 1.0:
        raise ValueError(f"{context} must be in [0, 1]")
    return resolved


def _validate_multi_basin_replay_status(value: str, *, context: str) -> str:
    resolved = _nonempty_string(value, context=context)
    if resolved not in LGRC9V3_MULTI_BASIN_REPLAY_STATUSES:
        raise ValueError(f"{context} must be a declared replay status")
    return resolved


def _validate_multi_basin_control_status(value: str, *, context: str) -> str:
    resolved = _nonempty_string(value, context=context)
    if resolved not in LGRC9V3_MULTI_BASIN_CONTROL_STATUSES:
        raise ValueError(f"{context} must be a declared control status")
    return resolved


@dataclass(frozen=True)
class LGRC9V3NativeRouteCandidateRecord:
    """One topology-route candidate before native route arbitration."""

    candidate_route_id: str
    native_route_arbitration_policy_id: str
    native_route_arbitration_enabled: bool
    candidate_set_id: str
    candidate_source_surface_digest: str
    route_intent: str
    candidate_topology_event_kind: str
    candidate_competing_sink_ids: Sequence[int]
    candidate_losing_sink_ids: Sequence[int]
    candidate_selected_sink_id: int
    candidate_transferred_node_ids: Sequence[int]
    candidate_lineage_transfer_map: Mapping[str, str]
    candidate_source_node_ids: Sequence[int]
    candidate_target_node_ids: Sequence[int]
    candidate_retired_node_ids: Sequence[int]
    candidate_source_edge_ids: Sequence[int]
    candidate_target_edge_ids: Sequence[int]
    candidate_retired_edge_ids: Sequence[int]
    candidate_route_score: float
    candidate_score_components: Mapping[str, float]
    candidate_budget_prediction: Mapping[str, float]
    candidate_order_key: str
    candidate_runtime_visible_inputs: Sequence[str]
    event_time_key: float
    scheduler_event_index: int
    candidate_source_producer_record_id: str | None = None
    candidate_source_topology_state_reabsorption_digest: str | None = None
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION
    candidate_route_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "candidate_route_id",
            "native_route_arbitration_policy_id",
            "candidate_set_id",
            "candidate_source_surface_digest",
            "route_intent",
            "candidate_topology_event_kind",
            "candidate_order_key",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported native route candidate schema")
        _validate_native_route_runtime_context(
            enabled=self.native_route_arbitration_enabled,
            policy_id=self.native_route_arbitration_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="native route candidate",
        )
        if self.route_intent not in LGRC9V3_NATIVE_ROUTE_INTENTS:
            raise ValueError("unsupported route_intent")
        if self.candidate_topology_event_kind not in LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS:
            raise ValueError("unsupported candidate_topology_event_kind")
        competing = _nonnegative_int_tuple(
            tuple(int(value) for value in self.candidate_competing_sink_ids),
            context="candidate_competing_sink_ids",
        )
        losing = tuple(
            _nonnegative_int(value, context="candidate_losing_sink_ids[]")
            for value in self.candidate_losing_sink_ids
        )
        selected = _nonnegative_int(
            self.candidate_selected_sink_id,
            context="candidate_selected_sink_id",
        )
        if selected not in competing:
            raise ValueError("candidate_selected_sink_id must be in competing sinks")
        if selected in losing:
            raise ValueError("candidate_losing_sink_ids cannot include selected sink")
        if not set(losing).issubset(set(competing)):
            raise ValueError("candidate_losing_sink_ids must be competing sinks")
        transferred = _nonnegative_int_tuple(
            tuple(int(value) for value in self.candidate_transferred_node_ids),
            context="candidate_transferred_node_ids",
        )
        _nonnegative_int_tuple(
            tuple(int(value) for value in self.candidate_source_node_ids),
            context="candidate_source_node_ids",
        )
        _nonnegative_int_tuple(
            tuple(int(value) for value in self.candidate_target_node_ids),
            context="candidate_target_node_ids",
        )
        for field_name in (
            "candidate_retired_node_ids",
            "candidate_source_edge_ids",
            "candidate_target_edge_ids",
            "candidate_retired_edge_ids",
        ):
            tuple(
                _nonnegative_int(value, context=f"{field_name}[]")
                for value in getattr(self, field_name)
            )
        if not self.candidate_lineage_transfer_map:
            raise ValueError("candidate_lineage_transfer_map must not be empty")
        lineage_map = {
            _nonempty_string(str(key), context="candidate_lineage_transfer_map.key"): (
                _nonempty_string(
                    str(value),
                    context=f"candidate_lineage_transfer_map[{key}]",
                )
            )
            for key, value in self.candidate_lineage_transfer_map.items()
        }
        missing_lineage = {
            str(int(node_id))
            for node_id in transferred
            if str(int(node_id)) not in lineage_map
        }
        if missing_lineage:
            raise ValueError(
                "candidate_lineage_transfer_map must cover transferred nodes"
            )
        score = _finite_float(self.candidate_route_score, context="candidate_route_score")
        score_components = {
            _nonempty_string(str(key), context="candidate_score_components.key"): (
                _finite_float(value, context=f"candidate_score_components[{key}]")
            )
            for key, value in self.candidate_score_components.items()
        }
        if not score_components:
            raise ValueError("candidate_score_components must not be empty")
        hidden_score_keys = set(score_components).intersection(
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS
        )
        if hidden_score_keys:
            raise ValueError(
                "candidate_score_components contain hidden inputs: "
                f"{sorted(hidden_score_keys)}"
            )
        if abs(sum(score_components.values()) - score) > 1e-12:
            raise ValueError(
                "candidate_route_score must equal sum(candidate_score_components)"
            )
        _validate_native_route_budget_prediction(self.candidate_budget_prediction)
        _validate_native_route_inputs(
            self.candidate_runtime_visible_inputs,
            context="candidate_runtime_visible_inputs",
        )
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        _validate_native_route_claim_flags(
            self.claim_flags,
            context="native route candidate",
        )
        expected_digest = build_lgrc9v3_native_route_candidate_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.candidate_route_digest is None:
            object.__setattr__(self, "candidate_route_digest", expected_digest)
        elif self.candidate_route_digest != expected_digest:
            raise ValueError(
                "candidate_route_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "native_route_arbitration",
            "candidate_route_id": self.candidate_route_id,
            "schema_version": self.schema_version,
            "native_route_arbitration_policy_id": (
                self.native_route_arbitration_policy_id
            ),
            "native_route_arbitration_enabled": (
                self.native_route_arbitration_enabled
            ),
            "candidate_set_id": self.candidate_set_id,
            "candidate_source_surface_digest": self.candidate_source_surface_digest,
            "candidate_source_producer_record_id": (
                self.candidate_source_producer_record_id
            ),
            "candidate_source_topology_state_reabsorption_digest": (
                self.candidate_source_topology_state_reabsorption_digest
            ),
            "route_intent": self.route_intent,
            "candidate_topology_event_kind": self.candidate_topology_event_kind,
            "candidate_competing_sink_ids": [
                int(value) for value in self.candidate_competing_sink_ids
            ],
            "candidate_losing_sink_ids": [
                int(value) for value in self.candidate_losing_sink_ids
            ],
            "candidate_selected_sink_id": int(self.candidate_selected_sink_id),
            "candidate_transferred_node_ids": [
                int(value) for value in self.candidate_transferred_node_ids
            ],
            "candidate_lineage_transfer_map": dict(
                sorted(
                    (str(key), str(value))
                    for key, value in self.candidate_lineage_transfer_map.items()
                )
            ),
            "candidate_lineage_transfer_map_digest": _lineage_transfer_map_digest(
                {
                    str(key): str(value)
                    for key, value in self.candidate_lineage_transfer_map.items()
                }
            ),
            "candidate_source_node_ids": [
                int(value) for value in self.candidate_source_node_ids
            ],
            "candidate_target_node_ids": [
                int(value) for value in self.candidate_target_node_ids
            ],
            "candidate_retired_node_ids": [
                int(value) for value in self.candidate_retired_node_ids
            ],
            "candidate_source_edge_ids": [
                int(value) for value in self.candidate_source_edge_ids
            ],
            "candidate_target_edge_ids": [
                int(value) for value in self.candidate_target_edge_ids
            ],
            "candidate_retired_edge_ids": [
                int(value) for value in self.candidate_retired_edge_ids
            ],
            "candidate_route_score": float(self.candidate_route_score),
            "candidate_score_components": {
                str(key): float(value)
                for key, value in sorted(self.candidate_score_components.items())
            },
            "candidate_budget_prediction": {
                str(key): float(value)
                for key, value in sorted(self.candidate_budget_prediction.items())
            },
            "candidate_order_key": self.candidate_order_key,
            "candidate_runtime_visible_inputs": [
                str(value) for value in self.candidate_runtime_visible_inputs
            ],
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["candidate_route_digest"] = self.candidate_route_digest
        return artifact


@dataclass(frozen=True)
class LGRC9V3NativeRouteCandidateSetRecord:
    """A deterministic set of native route candidates in one arbitration window."""

    candidate_set_id: str
    native_route_arbitration_policy_id: str
    native_route_arbitration_enabled: bool
    arbitration_window_id: str
    event_time_key: float
    scheduler_event_index: int
    candidate_route_digests: Sequence[str]
    candidate_set_order_key: str
    unresolved_tie_policy: str
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION
    idempotency_key: str | None = None
    candidate_set_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "candidate_set_id",
            "native_route_arbitration_policy_id",
            "arbitration_window_id",
            "candidate_set_order_key",
            "unresolved_tie_policy",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if (
            self.schema_version
            != LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION
        ):
            raise ValueError("unsupported native route candidate set schema")
        _validate_native_route_runtime_context(
            enabled=self.native_route_arbitration_enabled,
            policy_id=self.native_route_arbitration_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="native route candidate set",
        )
        digests = tuple(
            _nonempty_string(str(digest), context="candidate_route_digests[]")
            for digest in self.candidate_route_digests
        )
        if len(set(digests)) != len(digests):
            raise ValueError("candidate_route_digests must not contain duplicates")
        if self.candidate_set_order_key not in (
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_KEYS
        ):
            raise ValueError("unsupported candidate_set_order_key")
        if (
            self.candidate_set_order_key
            == LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING
            and tuple(sorted(digests)) != digests
        ):
            raise ValueError(
                "digest_ascending candidate sets require sorted route digests"
            )
        if self.unresolved_tie_policy not in LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICIES:
            raise ValueError("unsupported unresolved_tie_policy")
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        _validate_native_route_claim_flags(
            self.claim_flags,
            context="native route candidate set",
        )
        expected_idempotency_key = build_lgrc9v3_native_route_candidate_set_idempotency_key(
            native_route_arbitration_policy_id=self.native_route_arbitration_policy_id,
            arbitration_window_id=self.arbitration_window_id,
            event_time_key=self.event_time_key,
            candidate_route_digests=digests,
            candidate_set_order_key=self.candidate_set_order_key,
        )
        if self.idempotency_key is None:
            object.__setattr__(self, "idempotency_key", expected_idempotency_key)
        elif self.idempotency_key != expected_idempotency_key:
            raise ValueError(
                "idempotency_key does not match canonical candidate-set key"
            )
        expected_digest = build_lgrc9v3_native_route_candidate_set_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.candidate_set_digest is None:
            object.__setattr__(self, "candidate_set_digest", expected_digest)
        elif self.candidate_set_digest != expected_digest:
            raise ValueError(
                "candidate_set_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "native_route_arbitration",
            "candidate_set_id": self.candidate_set_id,
            "schema_version": self.schema_version,
            "native_route_arbitration_policy_id": (
                self.native_route_arbitration_policy_id
            ),
            "native_route_arbitration_enabled": (
                self.native_route_arbitration_enabled
            ),
            "arbitration_window_id": self.arbitration_window_id,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "candidate_route_digests": [
                str(digest) for digest in self.candidate_route_digests
            ],
            "candidate_set_order_key": self.candidate_set_order_key,
            "unresolved_tie_policy": self.unresolved_tie_policy,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
            "idempotency_key": self.idempotency_key,
        }
        if include_digest:
            artifact["candidate_set_digest"] = self.candidate_set_digest
        return artifact


@dataclass(frozen=True)
class LGRC9V3NativeRouteArbitrationRecord:
    """Native record selecting or rejecting one route from a candidate set."""

    native_route_arbitration_record_id: str
    native_route_arbitration_policy_id: str
    native_route_arbitration_enabled: bool
    candidate_set_id: str
    candidate_set_digest: str
    rejected_candidate_route_digests: Sequence[str]
    arbitration_reason_code: str
    arbitration_score: float
    arbitration_rule: str
    arbitration_runtime_visible_inputs: Sequence[str]
    event_time_key: float
    scheduler_event_index: int
    selected_candidate_route_id: str | None = None
    selected_candidate_route_digest: str | None = None
    selected_topology_event_id: str | None = None
    selected_topology_event_digest: str | None = None
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION
    idempotency_key: str | None = None
    native_route_arbitration_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "native_route_arbitration_record_id",
            "native_route_arbitration_policy_id",
            "candidate_set_id",
            "candidate_set_digest",
            "arbitration_reason_code",
            "arbitration_rule",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if (
            self.schema_version
            != LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION
        ):
            raise ValueError("unsupported native route-arbitration schema")
        if self.arbitration_reason_code not in LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_CODES:
            raise ValueError("unsupported arbitration_reason_code")
        if (
            self.arbitration_reason_code
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED
        ):
            if self.native_route_arbitration_enabled:
                raise ValueError("policy-disabled record cannot be enabled")
            if (
                self.native_route_arbitration_policy_id
                != LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED
            ):
                raise ValueError("policy-disabled record requires disabled policy")
        else:
            _validate_native_route_runtime_context(
                enabled=self.native_route_arbitration_enabled,
                policy_id=self.native_route_arbitration_policy_id,
                lgrc_runtime_level=self.lgrc_runtime_level,
                causal_layer_mode=self.causal_layer_mode,
                context="native route arbitration",
            )
        selected_reason = (
            self.arbitration_reason_code
            in LGRC9V3_NATIVE_ROUTE_ARBITRATION_SELECTED_REASON_CODES
        )
        if selected_reason:
            for field_name in (
                "selected_candidate_route_id",
                "selected_candidate_route_digest",
                "selected_topology_event_id",
            ):
                if getattr(self, field_name) is None:
                    raise ValueError(f"{field_name} is required for selected route")
                _nonempty_string(getattr(self, field_name), context=field_name)
        else:
            if self.selected_candidate_route_id or self.selected_candidate_route_digest:
                raise ValueError("non-selected arbitration records cannot select route")
            if self.selected_topology_event_id or self.selected_topology_event_digest:
                raise ValueError(
                    "non-selected arbitration records cannot select topology event"
                )
        rejected = tuple(
            _nonempty_string(str(digest), context="rejected_candidate_route_digests[]")
            for digest in self.rejected_candidate_route_digests
        )
        if len(set(rejected)) != len(rejected):
            raise ValueError(
                "rejected_candidate_route_digests must not contain duplicates"
            )
        if self.selected_candidate_route_digest in rejected:
            raise ValueError("rejected candidates cannot include selected route")
        _finite_float(self.arbitration_score, context="arbitration_score")
        _validate_native_route_inputs(
            self.arbitration_runtime_visible_inputs,
            context="arbitration_runtime_visible_inputs",
        )
        _nonnegative_float(self.event_time_key, context="event_time_key")
        if int(self.scheduler_event_index) < 0:
            raise ValueError("scheduler_event_index must be >= 0")
        _validate_native_route_claim_flags(
            self.claim_flags,
            context="native route arbitration",
        )
        expected_idempotency_key = build_lgrc9v3_native_route_arbitration_idempotency_key(
            native_route_arbitration_policy_id=self.native_route_arbitration_policy_id,
            candidate_set_digest=self.candidate_set_digest,
            selected_candidate_route_digest=self.selected_candidate_route_digest,
            arbitration_reason_code=self.arbitration_reason_code,
            arbitration_rule=self.arbitration_rule,
            selected_topology_event_id=self.selected_topology_event_id,
        )
        if self.idempotency_key is None:
            object.__setattr__(self, "idempotency_key", expected_idempotency_key)
        elif self.idempotency_key != expected_idempotency_key:
            raise ValueError(
                "idempotency_key does not match canonical route-arbitration key"
            )
        expected_digest = build_lgrc9v3_native_route_arbitration_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.native_route_arbitration_digest is None:
            object.__setattr__(
                self,
                "native_route_arbitration_digest",
                expected_digest,
            )
        elif self.native_route_arbitration_digest != expected_digest:
            raise ValueError(
                "native_route_arbitration_digest does not match canonical "
                "record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "native_route_arbitration",
            "native_route_arbitration_record_id": (
                self.native_route_arbitration_record_id
            ),
            "schema_version": self.schema_version,
            "native_route_arbitration_policy_id": (
                self.native_route_arbitration_policy_id
            ),
            "native_route_arbitration_enabled": (
                self.native_route_arbitration_enabled
            ),
            "candidate_set_id": self.candidate_set_id,
            "candidate_set_digest": self.candidate_set_digest,
            "selected_candidate_route_id": self.selected_candidate_route_id,
            "selected_candidate_route_digest": self.selected_candidate_route_digest,
            "rejected_candidate_route_digests": [
                str(digest) for digest in self.rejected_candidate_route_digests
            ],
            "arbitration_reason_code": self.arbitration_reason_code,
            "arbitration_score": float(self.arbitration_score),
            "arbitration_rule": self.arbitration_rule,
            "arbitration_runtime_visible_inputs": [
                str(value) for value in self.arbitration_runtime_visible_inputs
            ],
            "selected_topology_event_id": self.selected_topology_event_id,
            "selected_topology_event_digest": self.selected_topology_event_digest,
            "event_time_key": float(self.event_time_key),
            "scheduler_event_index": int(self.scheduler_event_index),
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
            "idempotency_key": self.idempotency_key,
        }
        if include_digest:
            artifact["native_route_arbitration_digest"] = (
                self.native_route_arbitration_digest
            )
        return artifact


@dataclass(frozen=True)
class LGRC9V3MultiBasinFlowWindowRecord:
    """Post-refinement runtime window for later child-basin extraction."""

    post_refinement_flow_window_id: str
    native_multi_basin_policy_id: str
    native_multi_basin_enabled: bool
    source_topology_event_id: str
    source_topology_event_digest: str
    source_expansion_id: str
    pre_refinement_topology_signature: str
    post_refinement_topology_signature: str
    refinement_lineage_map: Mapping[str, str]
    window_start_event_time_key: float
    window_end_event_time_key: float
    window_scheduler_indices: Sequence[int]
    node_support_trace: Mapping[Any, Any]
    node_coherence_trace: Mapping[Any, Any]
    edge_flux_trace: Mapping[Any, Any]
    packet_flux_trace: Mapping[Any, Any]
    node_plus_packet_budget_trace: Mapping[str, float]
    runtime_visible_inputs: Sequence[str]
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION
    post_refinement_flow_window_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "post_refinement_flow_window_id",
            "native_multi_basin_policy_id",
            "source_topology_event_id",
            "source_topology_event_digest",
            "source_expansion_id",
            "pre_refinement_topology_signature",
            "post_refinement_topology_signature",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported multi-basin flow-window schema")
        _validate_multi_basin_runtime_context(
            enabled=self.native_multi_basin_enabled,
            policy_id=self.native_multi_basin_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="multi-basin flow window",
        )
        if not self.refinement_lineage_map:
            raise ValueError("refinement_lineage_map must not be empty")
        for key, value in self.refinement_lineage_map.items():
            _nonempty_string(str(key), context="refinement_lineage_map.key")
            _nonempty_string(str(value), context=f"refinement_lineage_map[{key}]")
        start = _nonnegative_float(
            self.window_start_event_time_key,
            context="window_start_event_time_key",
        )
        end = _nonnegative_float(
            self.window_end_event_time_key,
            context="window_end_event_time_key",
        )
        if end < start:
            raise ValueError("window_end_event_time_key must be >= start")
        _nonnegative_int_tuple(
            tuple(int(value) for value in self.window_scheduler_indices),
            context="window_scheduler_indices",
        )
        _validate_multi_basin_float_map(
            self.node_support_trace,
            context="node_support_trace",
        )
        _validate_multi_basin_float_map(
            self.node_coherence_trace,
            context="node_coherence_trace",
        )
        _validate_multi_basin_float_map(self.edge_flux_trace, context="edge_flux_trace")
        _validate_multi_basin_float_map(
            self.packet_flux_trace,
            context="packet_flux_trace",
        )
        _validate_multi_basin_budget_trace(
            self.node_plus_packet_budget_trace,
            context="node_plus_packet_budget_trace",
        )
        _validate_multi_basin_inputs(
            self.runtime_visible_inputs,
            context="runtime_visible_inputs",
        )
        _validate_multi_basin_claim_flags(
            self.claim_flags,
            context="multi-basin flow window",
        )
        expected_digest = build_lgrc9v3_multi_basin_flow_window_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.post_refinement_flow_window_digest is None:
            object.__setattr__(
                self,
                "post_refinement_flow_window_digest",
                expected_digest,
            )
        elif self.post_refinement_flow_window_digest != expected_digest:
            raise ValueError(
                "post_refinement_flow_window_digest does not match canonical digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "multi_basin_formation",
            "post_refinement_flow_window_id": self.post_refinement_flow_window_id,
            "schema_version": self.schema_version,
            "native_multi_basin_policy_id": self.native_multi_basin_policy_id,
            "native_multi_basin_enabled": self.native_multi_basin_enabled,
            "source_topology_event_id": self.source_topology_event_id,
            "source_topology_event_digest": self.source_topology_event_digest,
            "source_expansion_id": self.source_expansion_id,
            "pre_refinement_topology_signature": self.pre_refinement_topology_signature,
            "post_refinement_topology_signature": (
                self.post_refinement_topology_signature
            ),
            "refinement_lineage_map": dict(
                sorted((str(key), str(value)) for key, value in self.refinement_lineage_map.items())
            ),
            "refinement_lineage_map_digest": _lineage_transfer_map_digest(
                {
                    str(key): str(value)
                    for key, value in self.refinement_lineage_map.items()
                }
            ),
            "window_start_event_time_key": float(self.window_start_event_time_key),
            "window_end_event_time_key": float(self.window_end_event_time_key),
            "window_scheduler_indices": [
                int(value) for value in self.window_scheduler_indices
            ],
            "node_support_trace": {
                str(key): float(value)
                for key, value in sorted(self.node_support_trace.items(), key=lambda item: str(item[0]))
            },
            "node_coherence_trace": {
                str(key): float(value)
                for key, value in sorted(self.node_coherence_trace.items(), key=lambda item: str(item[0]))
            },
            "edge_flux_trace": {
                str(key): float(value)
                for key, value in sorted(self.edge_flux_trace.items(), key=lambda item: str(item[0]))
            },
            "packet_flux_trace": {
                str(key): float(value)
                for key, value in sorted(self.packet_flux_trace.items(), key=lambda item: str(item[0]))
            },
            "node_plus_packet_budget_trace": {
                str(key): float(value)
                for key, value in sorted(self.node_plus_packet_budget_trace.items())
            },
            "runtime_visible_inputs": [
                str(value) for value in self.runtime_visible_inputs
            ],
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["post_refinement_flow_window_digest"] = (
                self.post_refinement_flow_window_digest
            )
        return artifact


@dataclass(frozen=True)
class LGRC9V3ChildBasinStateRecord:
    """Source-current child-basin candidate extracted from a flow window."""

    child_basin_state_record_id: str
    native_multi_basin_policy_id: str
    native_multi_basin_enabled: bool
    source_flow_window_digest: str
    child_basin_core_ids: Sequence[int]
    child_basin_membership_by_core: Mapping[Any, Sequence[int]]
    child_basin_support_floor_records: Mapping[Any, Any]
    child_basin_coherence_floor_records: Mapping[Any, Any]
    child_basin_boundary_records: Mapping[Any, Any]
    child_basin_flux_records: Mapping[Any, Any]
    old_basin_relation_trace: Mapping[str, str]
    merge_leakage_trace: Mapping[Any, Any]
    producer_residue_classification: str
    runtime_visible_inputs: Sequence[str]
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION
    child_basin_membership_digest: str | None = None
    child_basin_state_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "child_basin_state_record_id",
            "native_multi_basin_policy_id",
            "source_flow_window_digest",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported child-basin state schema")
        _validate_multi_basin_runtime_context(
            enabled=self.native_multi_basin_enabled,
            policy_id=self.native_multi_basin_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="child-basin state",
        )
        cores = _nonnegative_int_tuple(
            tuple(int(value) for value in self.child_basin_core_ids),
            context="child_basin_core_ids",
        )
        membership = _validate_multi_basin_sequence_map(
            self.child_basin_membership_by_core,
            context="child_basin_membership_by_core",
        )
        for core_id in cores:
            key = str(core_id)
            if key not in membership:
                raise ValueError("child_basin_membership_by_core must cover cores")
            if core_id not in membership[key]:
                raise ValueError("child membership for each core must include the core")
        for field_name in (
            "child_basin_support_floor_records",
            "child_basin_coherence_floor_records",
            "child_basin_boundary_records",
            "child_basin_flux_records",
            "merge_leakage_trace",
        ):
            _validate_multi_basin_float_map(
                getattr(self, field_name),
                context=field_name,
            )
        if not self.old_basin_relation_trace:
            raise ValueError("old_basin_relation_trace must not be empty")
        for key, value in self.old_basin_relation_trace.items():
            _nonempty_string(str(key), context="old_basin_relation_trace.key")
            _nonempty_string(str(value), context=f"old_basin_relation_trace[{key}]")
        if (
            self.producer_residue_classification
            not in LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_CLASSES
        ):
            raise ValueError("unsupported producer_residue_classification")
        _validate_multi_basin_inputs(
            self.runtime_visible_inputs,
            context="runtime_visible_inputs",
        )
        _validate_multi_basin_claim_flags(
            self.claim_flags,
            context="child-basin state",
        )
        expected_membership_digest = digest_canonical_data(
            {"child_basin_membership_by_core": membership}
        )
        if self.child_basin_membership_digest is None:
            object.__setattr__(
                self,
                "child_basin_membership_digest",
                expected_membership_digest,
            )
        elif self.child_basin_membership_digest != expected_membership_digest:
            raise ValueError(
                "child_basin_membership_digest does not match canonical membership"
            )
        expected_digest = build_lgrc9v3_child_basin_state_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.child_basin_state_digest is None:
            object.__setattr__(self, "child_basin_state_digest", expected_digest)
        elif self.child_basin_state_digest != expected_digest:
            raise ValueError(
                "child_basin_state_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        membership = {
            str(key): [int(value) for value in values]
            for key, values in sorted(
                self.child_basin_membership_by_core.items(),
                key=lambda item: str(item[0]),
            )
        }
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_CHILD_BASIN_STATE_RECORD_KIND,
            "artifact_schema_version": LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION,
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "multi_basin_formation",
            "child_basin_state_record_id": self.child_basin_state_record_id,
            "schema_version": self.schema_version,
            "native_multi_basin_policy_id": self.native_multi_basin_policy_id,
            "native_multi_basin_enabled": self.native_multi_basin_enabled,
            "source_flow_window_digest": self.source_flow_window_digest,
            "child_basin_core_ids": [
                int(value) for value in self.child_basin_core_ids
            ],
            "child_basin_membership_by_core": membership,
            "child_basin_membership_digest": self.child_basin_membership_digest,
            "child_basin_support_floor_records": {
                str(key): float(value)
                for key, value in sorted(self.child_basin_support_floor_records.items(), key=lambda item: str(item[0]))
            },
            "child_basin_coherence_floor_records": {
                str(key): float(value)
                for key, value in sorted(self.child_basin_coherence_floor_records.items(), key=lambda item: str(item[0]))
            },
            "child_basin_boundary_records": {
                str(key): float(value)
                for key, value in sorted(self.child_basin_boundary_records.items(), key=lambda item: str(item[0]))
            },
            "child_basin_flux_records": {
                str(key): float(value)
                for key, value in sorted(self.child_basin_flux_records.items(), key=lambda item: str(item[0]))
            },
            "old_basin_relation_trace": dict(sorted(self.old_basin_relation_trace.items())),
            "merge_leakage_trace": {
                str(key): float(value)
                for key, value in sorted(self.merge_leakage_trace.items(), key=lambda item: str(item[0]))
            },
            "producer_residue_classification": self.producer_residue_classification,
            "runtime_visible_inputs": [
                str(value) for value in self.runtime_visible_inputs
            ],
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["child_basin_state_digest"] = self.child_basin_state_digest
        return artifact


@dataclass(frozen=True)
class LGRC9V3MultiBasinReplayValidationRecord:
    """Artifact replay and persistence result for one child-basin state."""

    replay_validation_id: str
    native_multi_basin_policy_id: str
    native_multi_basin_enabled: bool
    source_child_basin_state_digest: str
    artifact_replay_result: str
    snapshot_load_replay_result: str
    duplicate_replay_result: str
    time_order_replay_result: str
    membership_persistence_ratio: float
    support_persistence_ratio: float
    coherence_persistence_ratio: float
    boundary_persistence_ratio: float
    flux_persistence_ratio: float
    replay_window: Mapping[Any, Any]
    replay_failure_modes: Sequence[str]
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION
    replay_validation_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "replay_validation_id",
            "native_multi_basin_policy_id",
            "source_child_basin_state_digest",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if (
            self.schema_version
            != LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION
        ):
            raise ValueError("unsupported multi-basin replay schema")
        _validate_multi_basin_runtime_context(
            enabled=self.native_multi_basin_enabled,
            policy_id=self.native_multi_basin_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="multi-basin replay validation",
        )
        for field_name in (
            "artifact_replay_result",
            "snapshot_load_replay_result",
            "duplicate_replay_result",
            "time_order_replay_result",
        ):
            _validate_multi_basin_replay_status(
                getattr(self, field_name),
                context=field_name,
            )
        for field_name in (
            "membership_persistence_ratio",
            "support_persistence_ratio",
            "coherence_persistence_ratio",
            "boundary_persistence_ratio",
            "flux_persistence_ratio",
        ):
            _validate_multi_basin_ratio(getattr(self, field_name), context=field_name)
        _validate_multi_basin_float_map(self.replay_window, context="replay_window")
        for value in self.replay_failure_modes:
            _nonempty_string(str(value), context="replay_failure_modes[]")
        _validate_multi_basin_claim_flags(
            self.claim_flags,
            context="multi-basin replay validation",
        )
        expected_digest = build_lgrc9v3_multi_basin_replay_validation_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.replay_validation_digest is None:
            object.__setattr__(self, "replay_validation_digest", expected_digest)
        elif self.replay_validation_digest != expected_digest:
            raise ValueError(
                "replay_validation_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "multi_basin_formation",
            "replay_validation_id": self.replay_validation_id,
            "schema_version": self.schema_version,
            "native_multi_basin_policy_id": self.native_multi_basin_policy_id,
            "native_multi_basin_enabled": self.native_multi_basin_enabled,
            "source_child_basin_state_digest": self.source_child_basin_state_digest,
            "artifact_replay_result": self.artifact_replay_result,
            "snapshot_load_replay_result": self.snapshot_load_replay_result,
            "duplicate_replay_result": self.duplicate_replay_result,
            "time_order_replay_result": self.time_order_replay_result,
            "membership_persistence_ratio": float(self.membership_persistence_ratio),
            "support_persistence_ratio": float(self.support_persistence_ratio),
            "coherence_persistence_ratio": float(self.coherence_persistence_ratio),
            "boundary_persistence_ratio": float(self.boundary_persistence_ratio),
            "flux_persistence_ratio": float(self.flux_persistence_ratio),
            "replay_window": {
                str(key): float(value)
                for key, value in sorted(self.replay_window.items(), key=lambda item: str(item[0]))
            },
            "replay_failure_modes": [
                str(value) for value in self.replay_failure_modes
            ],
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["replay_validation_digest"] = self.replay_validation_digest
        return artifact


@dataclass(frozen=True)
class LGRC9V3MultiBasinControlRecord:
    """One fail-closed merge/leakage or relabel control result."""

    control_record_id: str
    native_multi_basin_policy_id: str
    native_multi_basin_enabled: bool
    source_child_basin_state_digest: str
    control_id: str
    control_status: str
    blocked_condition: str
    expected_result: str
    actual_result: str
    claim_allowed_when_control_triggers: bool
    rung_effect: str
    merge_leakage_metrics: Mapping[Any, Any]
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    claim_flags: Mapping[str, bool] = field(default_factory=dict)
    schema_version: str = LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION
    control_record_digest: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "control_record_id",
            "native_multi_basin_policy_id",
            "source_child_basin_state_digest",
            "control_id",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "rung_effect",
        ):
            _nonempty_string(getattr(self, field_name), context=field_name)
        if self.schema_version != LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported multi-basin control schema")
        _validate_multi_basin_runtime_context(
            enabled=self.native_multi_basin_enabled,
            policy_id=self.native_multi_basin_policy_id,
            lgrc_runtime_level=self.lgrc_runtime_level,
            causal_layer_mode=self.causal_layer_mode,
            context="multi-basin control",
        )
        status = _validate_multi_basin_control_status(
            self.control_status,
            context="control_status",
        )
        if not isinstance(self.claim_allowed_when_control_triggers, bool):
            raise ValueError("claim_allowed_when_control_triggers must be boolean")
        if status != LGRC9V3_MULTI_BASIN_CONTROL_STATUS_PASSED and (
            self.claim_allowed_when_control_triggers
        ):
            raise ValueError("triggered controls cannot allow multi-basin claims")
        _validate_multi_basin_float_map(
            self.merge_leakage_metrics,
            context="merge_leakage_metrics",
        )
        _validate_multi_basin_claim_flags(
            self.claim_flags,
            context="multi-basin control",
        )
        expected_digest = build_lgrc9v3_multi_basin_control_record_digest(
            self.to_artifact(include_digest=False)
        )
        if self.control_record_digest is None:
            object.__setattr__(self, "control_record_digest", expected_digest)
        elif self.control_record_digest != expected_digest:
            raise ValueError(
                "control_record_digest does not match canonical record digest"
            )

    def to_artifact(self, *, include_digest: bool = True) -> dict[str, Any]:
        artifact: dict[str, Any] = {
            "artifact_kind": LGRC9V3_MULTI_BASIN_CONTROL_RECORD_KIND,
            "artifact_schema_version": (
                LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "evidence_class": "multi_basin_formation",
            "control_record_id": self.control_record_id,
            "schema_version": self.schema_version,
            "native_multi_basin_policy_id": self.native_multi_basin_policy_id,
            "native_multi_basin_enabled": self.native_multi_basin_enabled,
            "source_child_basin_state_digest": self.source_child_basin_state_digest,
            "control_id": self.control_id,
            "control_status": self.control_status,
            "blocked_condition": self.blocked_condition,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "claim_allowed_when_control_triggers": (
                self.claim_allowed_when_control_triggers
            ),
            "rung_effect": self.rung_effect,
            "merge_leakage_metrics": {
                str(key): float(value)
                for key, value in sorted(self.merge_leakage_metrics.items(), key=lambda item: str(item[0]))
            },
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "causal_layer_mode": self.causal_layer_mode,
            "claim_flags": dict(sorted(self.claim_flags.items())),
        }
        if include_digest:
            artifact["control_record_digest"] = self.control_record_digest
        return artifact


def restore_lgrc9v3_multi_basin_flow_window_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3MultiBasinFlowWindowRecord:
    """Restore one post-refinement flow-window record."""

    mapping = _require_artifact_mapping(artifact, context="multi_basin_flow_window")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin flow-window kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin flow-window schema")
    return LGRC9V3MultiBasinFlowWindowRecord(
        post_refinement_flow_window_id=_artifact_string(
            mapping.get("post_refinement_flow_window_id"),
            context="post_refinement_flow_window_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_multi_basin_policy_id=_artifact_string(
            mapping.get("native_multi_basin_policy_id"),
            context="native_multi_basin_policy_id",
        ),
        native_multi_basin_enabled=_artifact_bool(
            mapping.get("native_multi_basin_enabled"),
            context="native_multi_basin_enabled",
        ),
        source_topology_event_id=_artifact_string(
            mapping.get("source_topology_event_id"),
            context="source_topology_event_id",
        ),
        source_topology_event_digest=_artifact_string(
            mapping.get("source_topology_event_digest"),
            context="source_topology_event_digest",
        ),
        source_expansion_id=_artifact_string(
            mapping.get("source_expansion_id"),
            context="source_expansion_id",
        ),
        pre_refinement_topology_signature=_artifact_string(
            mapping.get("pre_refinement_topology_signature"),
            context="pre_refinement_topology_signature",
        ),
        post_refinement_topology_signature=_artifact_string(
            mapping.get("post_refinement_topology_signature"),
            context="post_refinement_topology_signature",
        ),
        refinement_lineage_map={
            _artifact_string(key, context="refinement_lineage_map.key"): (
                _artifact_string(value, context=f"refinement_lineage_map[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("refinement_lineage_map"),
                context="refinement_lineage_map",
            ).items()
        },
        window_start_event_time_key=_artifact_float(
            mapping.get("window_start_event_time_key"),
            context="window_start_event_time_key",
        ),
        window_end_event_time_key=_artifact_float(
            mapping.get("window_end_event_time_key"),
            context="window_end_event_time_key",
        ),
        window_scheduler_indices=tuple(
            _artifact_int(value, context="window_scheduler_indices[]")
            for value in mapping.get("window_scheduler_indices", [])
        ),
        node_support_trace=dict(
            _require_artifact_mapping(
                mapping.get("node_support_trace"),
                context="node_support_trace",
            )
        ),
        node_coherence_trace=dict(
            _require_artifact_mapping(
                mapping.get("node_coherence_trace"),
                context="node_coherence_trace",
            )
        ),
        edge_flux_trace=dict(
            _require_artifact_mapping(
                mapping.get("edge_flux_trace"),
                context="edge_flux_trace",
            )
        ),
        packet_flux_trace=dict(
            _require_artifact_mapping(
                mapping.get("packet_flux_trace"),
                context="packet_flux_trace",
            )
        ),
        node_plus_packet_budget_trace={
            _artifact_string(key, context="node_plus_packet_budget_trace.key"): (
                _artifact_float(value, context=f"node_plus_packet_budget_trace[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("node_plus_packet_budget_trace"),
                context="node_plus_packet_budget_trace",
            ).items()
        },
        runtime_visible_inputs=tuple(
            _artifact_string(value, context="runtime_visible_inputs[]")
            for value in mapping.get("runtime_visible_inputs", [])
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        post_refinement_flow_window_digest=_artifact_string(
            mapping.get("post_refinement_flow_window_digest"),
            context="post_refinement_flow_window_digest",
        ),
    )


def restore_lgrc9v3_child_basin_state_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3ChildBasinStateRecord:
    """Restore one child-basin state record."""

    mapping = _require_artifact_mapping(artifact, context="child_basin_state")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_CHILD_BASIN_STATE_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported child-basin state kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported child-basin state schema")
    return LGRC9V3ChildBasinStateRecord(
        child_basin_state_record_id=_artifact_string(
            mapping.get("child_basin_state_record_id"),
            context="child_basin_state_record_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_multi_basin_policy_id=_artifact_string(
            mapping.get("native_multi_basin_policy_id"),
            context="native_multi_basin_policy_id",
        ),
        native_multi_basin_enabled=_artifact_bool(
            mapping.get("native_multi_basin_enabled"),
            context="native_multi_basin_enabled",
        ),
        source_flow_window_digest=_artifact_string(
            mapping.get("source_flow_window_digest"),
            context="source_flow_window_digest",
        ),
        child_basin_core_ids=tuple(
            _artifact_int(value, context="child_basin_core_ids[]")
            for value in mapping.get("child_basin_core_ids", [])
        ),
        child_basin_membership_by_core={
            _artifact_string(key, context="child_basin_membership_by_core.key"): (
                tuple(
                    _artifact_int(
                        value,
                        context=f"child_basin_membership_by_core[{key}][]",
                    )
                    for value in values
                )
            )
            for key, values in _require_artifact_mapping(
                mapping.get("child_basin_membership_by_core"),
                context="child_basin_membership_by_core",
            ).items()
        },
        child_basin_support_floor_records=dict(
            _require_artifact_mapping(
                mapping.get("child_basin_support_floor_records"),
                context="child_basin_support_floor_records",
            )
        ),
        child_basin_coherence_floor_records=dict(
            _require_artifact_mapping(
                mapping.get("child_basin_coherence_floor_records"),
                context="child_basin_coherence_floor_records",
            )
        ),
        child_basin_boundary_records=dict(
            _require_artifact_mapping(
                mapping.get("child_basin_boundary_records"),
                context="child_basin_boundary_records",
            )
        ),
        child_basin_flux_records=dict(
            _require_artifact_mapping(
                mapping.get("child_basin_flux_records"),
                context="child_basin_flux_records",
            )
        ),
        old_basin_relation_trace={
            _artifact_string(key, context="old_basin_relation_trace.key"): (
                _artifact_string(value, context=f"old_basin_relation_trace[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("old_basin_relation_trace"),
                context="old_basin_relation_trace",
            ).items()
        },
        merge_leakage_trace=dict(
            _require_artifact_mapping(
                mapping.get("merge_leakage_trace"),
                context="merge_leakage_trace",
            )
        ),
        producer_residue_classification=_artifact_string(
            mapping.get("producer_residue_classification"),
            context="producer_residue_classification",
        ),
        runtime_visible_inputs=tuple(
            _artifact_string(value, context="runtime_visible_inputs[]")
            for value in mapping.get("runtime_visible_inputs", [])
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        child_basin_membership_digest=_artifact_string(
            mapping.get("child_basin_membership_digest"),
            context="child_basin_membership_digest",
        ),
        child_basin_state_digest=_artifact_string(
            mapping.get("child_basin_state_digest"),
            context="child_basin_state_digest",
        ),
    )


def restore_lgrc9v3_multi_basin_replay_validation_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3MultiBasinReplayValidationRecord:
    """Restore one multi-basin replay validation record."""

    mapping = _require_artifact_mapping(artifact, context="multi_basin_replay")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin replay kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin replay schema")
    return LGRC9V3MultiBasinReplayValidationRecord(
        replay_validation_id=_artifact_string(
            mapping.get("replay_validation_id"),
            context="replay_validation_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_multi_basin_policy_id=_artifact_string(
            mapping.get("native_multi_basin_policy_id"),
            context="native_multi_basin_policy_id",
        ),
        native_multi_basin_enabled=_artifact_bool(
            mapping.get("native_multi_basin_enabled"),
            context="native_multi_basin_enabled",
        ),
        source_child_basin_state_digest=_artifact_string(
            mapping.get("source_child_basin_state_digest"),
            context="source_child_basin_state_digest",
        ),
        artifact_replay_result=_artifact_string(
            mapping.get("artifact_replay_result"),
            context="artifact_replay_result",
        ),
        snapshot_load_replay_result=_artifact_string(
            mapping.get("snapshot_load_replay_result"),
            context="snapshot_load_replay_result",
        ),
        duplicate_replay_result=_artifact_string(
            mapping.get("duplicate_replay_result"),
            context="duplicate_replay_result",
        ),
        time_order_replay_result=_artifact_string(
            mapping.get("time_order_replay_result"),
            context="time_order_replay_result",
        ),
        membership_persistence_ratio=_artifact_float(
            mapping.get("membership_persistence_ratio"),
            context="membership_persistence_ratio",
        ),
        support_persistence_ratio=_artifact_float(
            mapping.get("support_persistence_ratio"),
            context="support_persistence_ratio",
        ),
        coherence_persistence_ratio=_artifact_float(
            mapping.get("coherence_persistence_ratio"),
            context="coherence_persistence_ratio",
        ),
        boundary_persistence_ratio=_artifact_float(
            mapping.get("boundary_persistence_ratio"),
            context="boundary_persistence_ratio",
        ),
        flux_persistence_ratio=_artifact_float(
            mapping.get("flux_persistence_ratio"),
            context="flux_persistence_ratio",
        ),
        replay_window=dict(
            _require_artifact_mapping(
                mapping.get("replay_window"),
                context="replay_window",
            )
        ),
        replay_failure_modes=tuple(
            _artifact_string(value, context="replay_failure_modes[]")
            for value in mapping.get("replay_failure_modes", [])
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        replay_validation_digest=_artifact_string(
            mapping.get("replay_validation_digest"),
            context="replay_validation_digest",
        ),
    )


def restore_lgrc9v3_multi_basin_control_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3MultiBasinControlRecord:
    """Restore one multi-basin merge/leakage control record."""

    mapping = _require_artifact_mapping(artifact, context="multi_basin_control")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_MULTI_BASIN_CONTROL_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin control kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported multi-basin control schema")
    return LGRC9V3MultiBasinControlRecord(
        control_record_id=_artifact_string(
            mapping.get("control_record_id"),
            context="control_record_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_multi_basin_policy_id=_artifact_string(
            mapping.get("native_multi_basin_policy_id"),
            context="native_multi_basin_policy_id",
        ),
        native_multi_basin_enabled=_artifact_bool(
            mapping.get("native_multi_basin_enabled"),
            context="native_multi_basin_enabled",
        ),
        source_child_basin_state_digest=_artifact_string(
            mapping.get("source_child_basin_state_digest"),
            context="source_child_basin_state_digest",
        ),
        control_id=_artifact_string(mapping.get("control_id"), context="control_id"),
        control_status=_artifact_string(
            mapping.get("control_status"),
            context="control_status",
        ),
        blocked_condition=_artifact_string(
            mapping.get("blocked_condition"),
            context="blocked_condition",
        ),
        expected_result=_artifact_string(
            mapping.get("expected_result"),
            context="expected_result",
        ),
        actual_result=_artifact_string(
            mapping.get("actual_result"),
            context="actual_result",
        ),
        claim_allowed_when_control_triggers=_artifact_bool(
            mapping.get("claim_allowed_when_control_triggers"),
            context="claim_allowed_when_control_triggers",
        ),
        rung_effect=_artifact_string(mapping.get("rung_effect"), context="rung_effect"),
        merge_leakage_metrics=dict(
            _require_artifact_mapping(
                mapping.get("merge_leakage_metrics"),
                context="merge_leakage_metrics",
            )
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        control_record_digest=_artifact_string(
            mapping.get("control_record_digest"),
            context="control_record_digest",
        ),
    )


def restore_lgrc9v3_native_route_candidate_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3NativeRouteCandidateRecord:
    """Restore one native route-candidate record."""

    mapping = _require_artifact_mapping(artifact, context="native_route_candidate")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported native route candidate kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported native route candidate schema")
    return LGRC9V3NativeRouteCandidateRecord(
        candidate_route_id=_artifact_string(
            mapping.get("candidate_route_id"),
            context="candidate_route_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_route_arbitration_policy_id=_artifact_string(
            mapping.get("native_route_arbitration_policy_id"),
            context="native_route_arbitration_policy_id",
        ),
        native_route_arbitration_enabled=_artifact_bool(
            mapping.get("native_route_arbitration_enabled"),
            context="native_route_arbitration_enabled",
        ),
        candidate_set_id=_artifact_string(
            mapping.get("candidate_set_id"),
            context="candidate_set_id",
        ),
        candidate_source_surface_digest=_artifact_string(
            mapping.get("candidate_source_surface_digest"),
            context="candidate_source_surface_digest",
        ),
        candidate_source_producer_record_id=_artifact_optional_string(
            mapping.get("candidate_source_producer_record_id"),
            context="candidate_source_producer_record_id",
        ),
        candidate_source_topology_state_reabsorption_digest=(
            _artifact_optional_string(
                mapping.get("candidate_source_topology_state_reabsorption_digest"),
                context="candidate_source_topology_state_reabsorption_digest",
            )
        ),
        route_intent=_artifact_string(mapping.get("route_intent"), context="route_intent"),
        candidate_topology_event_kind=_artifact_string(
            mapping.get("candidate_topology_event_kind"),
            context="candidate_topology_event_kind",
        ),
        candidate_competing_sink_ids=tuple(
            _artifact_int(value, context="candidate_competing_sink_ids[]")
            for value in mapping.get("candidate_competing_sink_ids", [])
        ),
        candidate_losing_sink_ids=tuple(
            _artifact_int(value, context="candidate_losing_sink_ids[]")
            for value in mapping.get("candidate_losing_sink_ids", [])
        ),
        candidate_selected_sink_id=_artifact_int(
            mapping.get("candidate_selected_sink_id"),
            context="candidate_selected_sink_id",
        ),
        candidate_transferred_node_ids=tuple(
            _artifact_int(value, context="candidate_transferred_node_ids[]")
            for value in mapping.get("candidate_transferred_node_ids", [])
        ),
        candidate_lineage_transfer_map={
            _artifact_string(key, context="candidate_lineage_transfer_map.key"): (
                _artifact_string(
                    value,
                    context=f"candidate_lineage_transfer_map[{key}]",
                )
            )
            for key, value in _require_artifact_mapping(
                mapping.get("candidate_lineage_transfer_map"),
                context="candidate_lineage_transfer_map",
            ).items()
        },
        candidate_source_node_ids=tuple(
            _artifact_int(value, context="candidate_source_node_ids[]")
            for value in mapping.get("candidate_source_node_ids", [])
        ),
        candidate_target_node_ids=tuple(
            _artifact_int(value, context="candidate_target_node_ids[]")
            for value in mapping.get("candidate_target_node_ids", [])
        ),
        candidate_retired_node_ids=tuple(
            _artifact_int(value, context="candidate_retired_node_ids[]")
            for value in mapping.get("candidate_retired_node_ids", [])
        ),
        candidate_source_edge_ids=tuple(
            _artifact_int(value, context="candidate_source_edge_ids[]")
            for value in mapping.get("candidate_source_edge_ids", [])
        ),
        candidate_target_edge_ids=tuple(
            _artifact_int(value, context="candidate_target_edge_ids[]")
            for value in mapping.get("candidate_target_edge_ids", [])
        ),
        candidate_retired_edge_ids=tuple(
            _artifact_int(value, context="candidate_retired_edge_ids[]")
            for value in mapping.get("candidate_retired_edge_ids", [])
        ),
        candidate_route_score=_artifact_float(
            mapping.get("candidate_route_score"),
            context="candidate_route_score",
        ),
        candidate_score_components={
            _artifact_string(key, context="candidate_score_components.key"): (
                _artifact_float(value, context=f"candidate_score_components[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("candidate_score_components"),
                context="candidate_score_components",
            ).items()
        },
        candidate_budget_prediction={
            _artifact_string(key, context="candidate_budget_prediction.key"): (
                _artifact_float(value, context=f"candidate_budget_prediction[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("candidate_budget_prediction"),
                context="candidate_budget_prediction",
            ).items()
        },
        candidate_order_key=_artifact_string(
            mapping.get("candidate_order_key"),
            context="candidate_order_key",
        ),
        candidate_runtime_visible_inputs=tuple(
            _artifact_string(value, context="candidate_runtime_visible_inputs[]")
            for value in mapping.get("candidate_runtime_visible_inputs", [])
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        candidate_route_digest=_artifact_string(
            mapping.get("candidate_route_digest"),
            context="candidate_route_digest",
        ),
    )


def restore_lgrc9v3_native_route_candidate_set_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3NativeRouteCandidateSetRecord:
    """Restore one native route-candidate set record."""

    mapping = _require_artifact_mapping(artifact, context="native_route_candidate_set")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported native route candidate set kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported native route candidate set schema"
        )
    return LGRC9V3NativeRouteCandidateSetRecord(
        candidate_set_id=_artifact_string(
            mapping.get("candidate_set_id"),
            context="candidate_set_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_route_arbitration_policy_id=_artifact_string(
            mapping.get("native_route_arbitration_policy_id"),
            context="native_route_arbitration_policy_id",
        ),
        native_route_arbitration_enabled=_artifact_bool(
            mapping.get("native_route_arbitration_enabled"),
            context="native_route_arbitration_enabled",
        ),
        arbitration_window_id=_artifact_string(
            mapping.get("arbitration_window_id"),
            context="arbitration_window_id",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        candidate_route_digests=tuple(
            _artifact_string(value, context="candidate_route_digests[]")
            for value in mapping.get("candidate_route_digests", [])
        ),
        candidate_set_order_key=_artifact_string(
            mapping.get("candidate_set_order_key"),
            context="candidate_set_order_key",
        ),
        unresolved_tie_policy=_artifact_string(
            mapping.get("unresolved_tie_policy"),
            context="unresolved_tie_policy",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        idempotency_key=_artifact_string(
            mapping.get("idempotency_key"),
            context="idempotency_key",
        ),
        candidate_set_digest=_artifact_string(
            mapping.get("candidate_set_digest"),
            context="candidate_set_digest",
        ),
    )


def restore_lgrc9v3_native_route_arbitration_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3NativeRouteArbitrationRecord:
    """Restore one native route-arbitration record."""

    mapping = _require_artifact_mapping(artifact, context="native_route_arbitration")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported native route arbitration kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported native route arbitration schema"
        )
    return LGRC9V3NativeRouteArbitrationRecord(
        native_route_arbitration_record_id=_artifact_string(
            mapping.get("native_route_arbitration_record_id"),
            context="native_route_arbitration_record_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        native_route_arbitration_policy_id=_artifact_string(
            mapping.get("native_route_arbitration_policy_id"),
            context="native_route_arbitration_policy_id",
        ),
        native_route_arbitration_enabled=_artifact_bool(
            mapping.get("native_route_arbitration_enabled"),
            context="native_route_arbitration_enabled",
        ),
        candidate_set_id=_artifact_string(
            mapping.get("candidate_set_id"),
            context="candidate_set_id",
        ),
        candidate_set_digest=_artifact_string(
            mapping.get("candidate_set_digest"),
            context="candidate_set_digest",
        ),
        selected_candidate_route_id=_artifact_optional_string(
            mapping.get("selected_candidate_route_id"),
            context="selected_candidate_route_id",
        ),
        selected_candidate_route_digest=_artifact_optional_string(
            mapping.get("selected_candidate_route_digest"),
            context="selected_candidate_route_digest",
        ),
        rejected_candidate_route_digests=tuple(
            _artifact_string(value, context="rejected_candidate_route_digests[]")
            for value in mapping.get("rejected_candidate_route_digests", [])
        ),
        arbitration_reason_code=_artifact_string(
            mapping.get("arbitration_reason_code"),
            context="arbitration_reason_code",
        ),
        arbitration_score=_artifact_float(
            mapping.get("arbitration_score"),
            context="arbitration_score",
        ),
        arbitration_rule=_artifact_string(
            mapping.get("arbitration_rule"),
            context="arbitration_rule",
        ),
        arbitration_runtime_visible_inputs=tuple(
            _artifact_string(value, context="arbitration_runtime_visible_inputs[]")
            for value in mapping.get("arbitration_runtime_visible_inputs", [])
        ),
        selected_topology_event_id=_artifact_optional_string(
            mapping.get("selected_topology_event_id"),
            context="selected_topology_event_id",
        ),
        selected_topology_event_digest=_artifact_optional_string(
            mapping.get("selected_topology_event_digest"),
            context="selected_topology_event_digest",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        idempotency_key=_artifact_string(
            mapping.get("idempotency_key"),
            context="idempotency_key",
        ),
        native_route_arbitration_digest=_artifact_string(
            mapping.get("native_route_arbitration_digest"),
            context="native_route_arbitration_digest",
        ),
    )


def restore_lgrc9v3_causal_pulse_substrate_surface_policy_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CausalPulseSubstrateSurfacePolicy:
    """Restore a causal pulse-substrate surface policy artifact."""

    mapping = _require_artifact_mapping(artifact, context="surface_policy")
    return LGRC9V3CausalPulseSubstrateSurfacePolicy(
        surface_policy_id=_artifact_string(
            mapping.get("surface_policy_id"),
            context="surface_policy_id",
        ),
        surface_policy=_artifact_string(
            mapping.get("surface_policy"),
            context="surface_policy",
        ),
        surface_policy_enabled=_artifact_bool(
            mapping.get("surface_policy_enabled"),
            context="surface_policy_enabled",
        ),
        surface_policy_validated=_artifact_bool(
            mapping.get("surface_policy_validated"),
            context="surface_policy_validated",
        ),
        coupling_producer_enabled=_artifact_bool(
            mapping.get("coupling_producer_enabled"),
            context="coupling_producer_enabled",
        ),
        feedback_producer_enabled=_artifact_bool(
            mapping.get("feedback_producer_enabled"),
            context="feedback_producer_enabled",
        ),
        supported=_artifact_bool(
            mapping.get("native_lgrc_pulse_substrate_supported"),
            context="native_lgrc_pulse_substrate_supported",
        ),
        required_lgrc_level=_artifact_string(
            mapping.get("required_lgrc_level"),
            context="required_lgrc_level",
        ),
        fixed_topology_only=_artifact_bool(
            mapping.get("fixed_topology_only"),
            context="fixed_topology_only",
        ),
        topology_lineage_status=_artifact_string(
            mapping.get("topology_lineage_status"),
            context="topology_lineage_status",
        ),
    )


def restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CausalPulseSubstrateSurfaceLineageRecord:
    """Restore one causal pulse-substrate surface lineage record."""

    mapping = _require_artifact_mapping(artifact, context="surface_lineage_record")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND
    ):
        raise SnapshotCompatibilityError("unsupported surface lineage artifact kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported surface lineage schema version"
        )
    return LGRC9V3CausalPulseSubstrateSurfaceLineageRecord(
        surface_lineage_record_id=_artifact_string(
            mapping.get("surface_lineage_record_id"),
            context="surface_lineage_record_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        surface_lineage_policy_id=_artifact_string(
            mapping.get("surface_lineage_policy_id"),
            context="surface_lineage_policy_id",
        ),
        surface_lineage_transport_enabled=_artifact_bool(
            mapping.get("surface_lineage_transport_enabled"),
            context="surface_lineage_transport_enabled",
        ),
        surface_lineage_transport_validated=_artifact_bool(
            mapping.get("surface_lineage_transport_validated"),
            context="surface_lineage_transport_validated",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        source_surface_id=_artifact_string(
            mapping.get("source_surface_id"),
            context="source_surface_id",
        ),
        source_surface_digest=_artifact_string(
            mapping.get("source_surface_digest"),
            context="source_surface_digest",
        ),
        topology_event_id=_artifact_string(
            mapping.get("topology_event_id"),
            context="topology_event_id",
        ),
        topology_event_kind=_artifact_string(
            mapping.get("topology_event_kind"),
            context="topology_event_kind",
        ),
        topology_event_digest=_artifact_string(
            mapping.get("topology_event_digest"),
            context="topology_event_digest",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            mapping.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        lineage_transfer_map={
            _artifact_string(key, context="lineage_transfer_map.key"): (
                _artifact_string(value, context=f"lineage_transfer_map[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("lineage_transfer_map"),
                context="lineage_transfer_map",
            ).items()
        },
        source_surface_nodes=tuple(
            _artifact_int(node_id, context="source_surface_nodes[]")
            for node_id in mapping.get("source_surface_nodes", [])
        ),
        target_surface_nodes=tuple(
            _artifact_int(node_id, context="target_surface_nodes[]")
            for node_id in mapping.get("target_surface_nodes", [])
        ),
        source_surface_ports=None
        if mapping.get("source_surface_ports") is None
        else tuple(
            _artifact_string(port, context="source_surface_ports[]")
            for port in mapping.get("source_surface_ports", [])
        ),
        target_surface_ports=None
        if mapping.get("target_surface_ports") is None
        else tuple(
            _artifact_string(port, context="target_surface_ports[]")
            for port in mapping.get("target_surface_ports", [])
        ),
        lineage_action=_artifact_string(
            mapping.get("lineage_action"),
            context="lineage_action",
        ),
        lineage_status=_artifact_string(
            mapping.get("lineage_status"),
            context="lineage_status",
        ),
        surface_budget_surface=_artifact_string(
            mapping.get("surface_budget_surface"),
            context="surface_budget_surface",
        ),
        surface_budget_before=_artifact_float(
            mapping.get("surface_budget_before"),
            context="surface_budget_before",
        ),
        surface_budget_after=_artifact_float(
            mapping.get("surface_budget_after"),
            context="surface_budget_after",
        ),
        surface_budget_error=_artifact_float(
            mapping.get("surface_budget_error"),
            context="surface_budget_error",
        ),
        node_plus_packet_budget_before=_artifact_float(
            mapping.get("node_plus_packet_budget_before"),
            context="node_plus_packet_budget_before",
        ),
        node_plus_packet_budget_after=_artifact_float(
            mapping.get("node_plus_packet_budget_after"),
            context="node_plus_packet_budget_after",
        ),
        node_plus_packet_budget_error=_artifact_float(
            mapping.get("node_plus_packet_budget_error"),
            context="node_plus_packet_budget_error",
        ),
        transported_surface_id=_artifact_optional_string(
            mapping.get("transported_surface_id"),
            context="transported_surface_id",
        ),
        transported_surface_digest=_artifact_optional_string(
            mapping.get("transported_surface_digest"),
            context="transported_surface_digest",
        ),
        superseded_surface_id=_artifact_optional_string(
            mapping.get("superseded_surface_id"),
            context="superseded_surface_id",
        ),
        producer_stale_read_blocker=_artifact_optional_string(
            mapping.get("producer_stale_read_blocker"),
            context="producer_stale_read_blocker",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        idempotency_key=_artifact_string(
            mapping.get("idempotency_key"),
            context="idempotency_key",
        ),
        lineage_record_digest=_artifact_string(
            mapping.get("lineage_record_digest"),
            context="lineage_record_digest",
        ),
    )


def restore_lgrc9v3_topology_state_reabsorption_record_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3TopologyStateReabsorptionRecord:
    """Restore one topology-state reabsorption record."""

    mapping = _require_artifact_mapping(
        artifact,
        context="topology_state_reabsorption_record",
    )
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND
    ):
        raise SnapshotCompatibilityError(
            "unsupported topology-state reabsorption artifact kind"
        )
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported topology-state reabsorption schema version"
        )
    return LGRC9V3TopologyStateReabsorptionRecord(
        topology_state_reabsorption_record_id=_artifact_string(
            mapping.get("topology_state_reabsorption_record_id"),
            context="topology_state_reabsorption_record_id",
        ),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        topology_state_reabsorption_policy_id=_artifact_string(
            mapping.get("topology_state_reabsorption_policy_id"),
            context="topology_state_reabsorption_policy_id",
        ),
        topology_state_reabsorption_enabled=_artifact_bool(
            mapping.get("topology_state_reabsorption_enabled"),
            context="topology_state_reabsorption_enabled",
        ),
        topology_state_reabsorption_validated=_artifact_bool(
            mapping.get("topology_state_reabsorption_validated"),
            context="topology_state_reabsorption_validated",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level"),
            context="lgrc_runtime_level",
        ),
        causal_layer_mode=_artifact_string(
            mapping.get("causal_layer_mode"),
            context="causal_layer_mode",
        ),
        topology_event_id=_artifact_string(
            mapping.get("topology_event_id"),
            context="topology_event_id",
        ),
        topology_event_kind=_artifact_string(
            mapping.get("topology_event_kind"),
            context="topology_event_kind",
        ),
        topology_event_digest=_artifact_string(
            mapping.get("topology_event_digest"),
            context="topology_event_digest",
        ),
        topology_event_committed=_artifact_bool(
            mapping.get("topology_event_committed"),
            context="topology_event_committed",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            mapping.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        lineage_transfer_map={
            _artifact_string(key, context="lineage_transfer_map.key"): (
                _artifact_string(value, context=f"lineage_transfer_map[{key}]")
            )
            for key, value in _require_artifact_mapping(
                mapping.get("lineage_transfer_map"),
                context="lineage_transfer_map",
            ).items()
        },
        source_node_ids=tuple(
            _artifact_int(node_id, context="source_node_ids[]")
            for node_id in mapping.get("source_node_ids", [])
        ),
        target_node_ids=tuple(
            _artifact_int(node_id, context="target_node_ids[]")
            for node_id in mapping.get("target_node_ids", [])
        ),
        retired_node_ids=tuple(
            _artifact_int(node_id, context="retired_node_ids[]")
            for node_id in mapping.get("retired_node_ids", [])
        ),
        source_edge_ids=tuple(
            _artifact_int(edge_id, context="source_edge_ids[]")
            for edge_id in mapping.get("source_edge_ids", [])
        ),
        target_edge_ids=tuple(
            _artifact_int(edge_id, context="target_edge_ids[]")
            for edge_id in mapping.get("target_edge_ids", [])
        ),
        retired_edge_ids=tuple(
            _artifact_int(edge_id, context="retired_edge_ids[]")
            for edge_id in mapping.get("retired_edge_ids", [])
        ),
        node_state_before=_parse_artifact_float_map(
            mapping,
            key="node_state_before",
        ),
        node_state_after=_parse_artifact_float_map(mapping, key="node_state_after"),
        edge_state_before=_parse_artifact_nested_float_map(
            mapping,
            key="edge_state_before",
        ),
        edge_state_after=_parse_artifact_nested_float_map(
            mapping,
            key="edge_state_after",
        ),
        packet_ledger_digest_before=_artifact_string(
            mapping.get("packet_ledger_digest_before"),
            context="packet_ledger_digest_before",
        ),
        packet_ledger_digest_after=_artifact_string(
            mapping.get("packet_ledger_digest_after"),
            context="packet_ledger_digest_after",
        ),
        active_node_state_total_before=_artifact_float(
            mapping.get("active_node_state_total_before"),
            context="active_node_state_total_before",
        ),
        active_node_state_total_after=_artifact_float(
            mapping.get("active_node_state_total_after"),
            context="active_node_state_total_after",
        ),
        packet_ledger_node_total_before=_artifact_float(
            mapping.get("packet_ledger_node_total_before"),
            context="packet_ledger_node_total_before",
        ),
        packet_ledger_node_total_after=_artifact_float(
            mapping.get("packet_ledger_node_total_after"),
            context="packet_ledger_node_total_after",
        ),
        packet_ledger_in_flight_packet_total_before=_artifact_float(
            mapping.get("packet_ledger_in_flight_packet_total_before"),
            context="packet_ledger_in_flight_packet_total_before",
        ),
        packet_ledger_in_flight_packet_total_after=_artifact_float(
            mapping.get("packet_ledger_in_flight_packet_total_after"),
            context="packet_ledger_in_flight_packet_total_after",
        ),
        packet_ledger_conserved_budget_total_before=_artifact_float(
            mapping.get("packet_ledger_conserved_budget_total_before"),
            context="packet_ledger_conserved_budget_total_before",
        ),
        packet_ledger_conserved_budget_total_after=_artifact_float(
            mapping.get("packet_ledger_conserved_budget_total_after"),
            context="packet_ledger_conserved_budget_total_after",
        ),
        node_plus_packet_budget_before=_artifact_float(
            mapping.get("node_plus_packet_budget_before"),
            context="node_plus_packet_budget_before",
        ),
        node_plus_packet_budget_after=_artifact_float(
            mapping.get("node_plus_packet_budget_after"),
            context="node_plus_packet_budget_after",
        ),
        node_plus_packet_budget_error=_artifact_float(
            mapping.get("node_plus_packet_budget_error"),
            context="node_plus_packet_budget_error",
        ),
        active_state_digest_before=_artifact_string(
            mapping.get("active_state_digest_before"),
            context="active_state_digest_before",
        ),
        active_state_digest_after=_artifact_string(
            mapping.get("active_state_digest_after"),
            context="active_state_digest_after",
        ),
        state_reabsorption_action=_artifact_string(
            mapping.get("state_reabsorption_action"),
            context="state_reabsorption_action",
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        idempotency_key=_artifact_string(
            mapping.get("idempotency_key"),
            context="idempotency_key",
        ),
        topology_state_reabsorption_digest=_artifact_string(
            mapping.get("topology_state_reabsorption_digest"),
            context="topology_state_reabsorption_digest",
        ),
    )


def restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3CausalPulseSubstrateSurfaceRow:
    """Restore one causal pulse-substrate surface row."""

    mapping = _require_artifact_mapping(artifact, context="surface_row")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND
    ):
        raise SnapshotCompatibilityError("unsupported surface row artifact kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported surface row schema version")
    return LGRC9V3CausalPulseSubstrateSurfaceRow(
        surface_id=_artifact_string(mapping.get("surface_id"), context="surface_id"),
        schema_version=_artifact_string(
            mapping.get("schema_version"),
            context="schema_version",
        ),
        surface_policy_id=_artifact_string(
            mapping.get("surface_policy_id"),
            context="surface_policy_id",
        ),
        surface_policy_enabled=_artifact_bool(
            mapping.get("surface_policy_enabled"),
            context="surface_policy_enabled",
        ),
        surface_policy_validated=_artifact_bool(
            mapping.get("surface_policy_validated"),
            context="surface_policy_validated",
        ),
        lgrc_runtime_level=_artifact_string(
            mapping.get("lgrc_runtime_level", LGRC_RUNTIME_LEVEL_LGRC2),
            context="lgrc_runtime_level",
        ),
        route_aspect_id=_artifact_string(
            mapping.get("route_aspect_id"),
            context="route_aspect_id",
        ),
        route_aspect_digest=_artifact_string(
            mapping.get("route_aspect_digest"),
            context="route_aspect_digest",
        ),
        pulse_event_id=_artifact_string(
            mapping.get("pulse_event_id"),
            context="pulse_event_id",
        ),
        pulse_packet_id=_artifact_string(
            mapping.get("pulse_packet_id"),
            context="pulse_packet_id",
        ),
        pulse_event_kind=_artifact_string(
            mapping.get("pulse_event_kind"),
            context="pulse_event_kind",
        ),
        pulse_channel_id=_artifact_string(
            mapping.get("pulse_channel_id"),
            context="pulse_channel_id",
        ),
        pulse_route_step=_artifact_int(
            mapping.get("pulse_route_step"),
            context="pulse_route_step",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        node_proper_time={
            int(node_id): _artifact_float(value, context=f"node_proper_time[{node_id}]")
            for node_id, value in _require_artifact_mapping(
                mapping.get("node_proper_time", {}),
                context="node_proper_time",
            ).items()
        },
        source_node_id=_artifact_int(
            mapping.get("source_node_id"),
            context="source_node_id",
        ),
        target_node_id=_artifact_int(
            mapping.get("target_node_id"),
            context="target_node_id",
        ),
        contact_amount=_artifact_float(
            mapping.get("contact_amount"),
            context="contact_amount",
        ),
        surface_state_id=_artifact_string(
            mapping.get("surface_state_id"),
            context="surface_state_id",
        ),
        surface_state_digest=_artifact_string(
            mapping.get("surface_state_digest"),
            context="surface_state_digest",
        ),
        surface_kind=_artifact_string(
            mapping.get("surface_kind"),
            context="surface_kind",
        ),
        surface_nodes=tuple(
            _artifact_int(node_id, context="surface_nodes[]")
            for node_id in mapping.get("surface_nodes", [])
        ),
        surface_values_before=dict(
            _require_artifact_mapping(
                mapping.get("surface_values_before", {}),
                context="surface_values_before",
            )
        ),
        surface_values_after=dict(
            _require_artifact_mapping(
                mapping.get("surface_values_after", {}),
                context="surface_values_after",
            )
        ),
        runtime_visible_inputs=tuple(
            _artifact_string(item, context="runtime_visible_inputs[]")
            for item in mapping.get("runtime_visible_inputs", [])
        ),
        surface_update_policy=_require_artifact_mapping(
            mapping.get("surface_update_policy"),
            context="surface_update_policy",
        ),
        surface_budget_surface=_artifact_string(
            mapping.get("surface_budget_surface"),
            context="surface_budget_surface",
        ),
        surface_budget_before=_artifact_float(
            mapping.get("surface_budget_before"),
            context="surface_budget_before",
        ),
        surface_budget_after=_artifact_float(
            mapping.get("surface_budget_after"),
            context="surface_budget_after",
        ),
        surface_budget_error=_artifact_float(
            mapping.get("surface_budget_error"),
            context="surface_budget_error",
        ),
        lineage_status=_artifact_string(
            mapping.get("lineage_status"),
            context="lineage_status",
        ),
        producer_records=tuple(
            _require_artifact_mapping(record, context="producer_records[]")
            for record in mapping.get("producer_records", [])
        ),
        claim_flags={
            _artifact_string(key, context="claim_flags.key"): _artifact_bool(
                value,
                context=f"claim_flags[{key}]",
            )
            for key, value in _require_artifact_mapping(
                mapping.get("claim_flags", {}),
                context="claim_flags",
            ).items()
        },
        surface_digest=_artifact_string(
            mapping.get("surface_digest"),
            context="surface_digest",
        ),
    )


def _validate_surface_runtime_inputs(
    surface_kind: str,
    runtime_visible_inputs: tuple[str, ...],
) -> None:
    required = set(LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS[surface_kind])
    actual = set(runtime_visible_inputs)
    missing = required - actual
    if missing:
        raise ValueError(
            "runtime_visible_inputs missing required inputs for "
            f"{surface_kind}: {sorted(missing)}"
        )


def _validate_causal_pulse_substrate_surface_update_policy(
    policy: Mapping[str, Any],
    surface_kind: str,
) -> None:
    mapping = _require_artifact_mapping(policy, context="surface_update_policy")
    required = {"policy_id", "version", "activation_gate", "allowed_surface_kinds"}
    missing = required - set(mapping)
    if missing:
        raise ValueError(f"surface_update_policy missing fields: {sorted(missing)}")
    if (
        _artifact_string(mapping.get("policy_id"), context="surface_update_policy.policy_id")
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED
    ):
        raise ValueError("unsupported surface_update_policy policy_id")
    if (
        _artifact_string(mapping.get("version"), context="surface_update_policy.version")
        != LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION
    ):
        raise ValueError("unsupported surface_update_policy version")
    activation_gate = _artifact_string(
        mapping.get("activation_gate"),
        context="surface_update_policy.activation_gate",
    )
    if activation_gate not in {"committed_packet_event", "disabled"}:
        raise ValueError("unsupported surface_update_policy activation_gate")
    allowed = tuple(
        _artifact_string(item, context="surface_update_policy.allowed_surface_kinds[]")
        for item in mapping.get("allowed_surface_kinds", ())
    )
    if not allowed:
        raise ValueError("surface_update_policy allowed_surface_kinds must not be empty")
    unknown = set(allowed) - LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KINDS
    if unknown:
        raise ValueError(f"unknown surface kinds in update policy: {sorted(unknown)}")
    if surface_kind not in allowed:
        raise ValueError("surface_update_policy does not allow surface_kind")


def _reject_forbidden_surface_keys(value: Any, *, context: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS:
                raise ValueError(f"{context} contains forbidden key: {key}")
            _reject_forbidden_surface_keys(nested, context=f"{context}.{key}")
    elif isinstance(value, list | tuple):
        for index, nested in enumerate(value):
            _reject_forbidden_surface_keys(nested, context=f"{context}[{index}]")


def _finite_float(value: Any, *, context: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{context} must be a finite number") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{context} must be finite")
    return numeric


def _positive_float(value: Any, *, context: str) -> float:
    numeric = _finite_float(value, context=context)
    if numeric <= 0.0:
        raise ValueError(f"{context} must be > 0")
    return numeric


def _nonnegative_float(value: Any, *, context: str) -> float:
    numeric = _finite_float(value, context=context)
    if numeric < 0.0:
        raise ValueError(f"{context} must be >= 0")
    return numeric


def derive_lgrc9v3_packet_arrival_event_time_key(
    *,
    departure_event_time_key: float,
    edge_id: EdgeId,
    edge_causal_delay: Mapping[EdgeId, float],
) -> float:
    """Derive the normal LGRC-2 packet arrival event-time key.

    The returned value is ``T_arrive`` for event-queue ordering:

    ``T_arrive = T_depart + tau_ij``.

    It is not the source or target node's local proper time. The delay mapping
    must be the edge-delay surface captured for the packet scheduling/departure
    decision; later topology or state changes do not retroactively reschedule
    this packet.
    """

    departure_key = _nonnegative_float(
        departure_event_time_key,
        context="departure_event_time_key",
    )
    resolved_edge_id = int(edge_id)
    if resolved_edge_id < 0:
        raise ValueError("edge_id must be >= 0")
    if resolved_edge_id not in edge_causal_delay:
        raise ValueError(f"edge_causal_delay missing edge {resolved_edge_id}")
    delay = _positive_float(
        edge_causal_delay[resolved_edge_id],
        context=f"edge_causal_delay[{resolved_edge_id}]",
    )
    return _finite_float(
        departure_key + delay,
        context="arrival_event_time_key",
    )


def _live_edge_ids(state: GRC9V3State) -> tuple[EdgeId, ...]:
    return tuple(
        sorted(int(edge_id) for edge_id in state.topology.iter_live_edge_ids())
    )


def _live_node_ids(state: GRC9V3State) -> tuple[NodeId, ...]:
    return tuple(sorted(int(node_id) for node_id in state.topology.iter_live_node_ids()))


def _topology_signature(state: GRC9V3State) -> dict[str, Any]:
    edge_records: list[dict[str, Any]] = []
    for edge_id in _live_edge_ids(state):
        endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
        edge_records.append(
            {
                "edge_id": int(edge_id),
                "endpoints": [
                    [int(endpoint_a[0]), int(endpoint_a[1])],
                    [int(endpoint_b[0]), int(endpoint_b[1])],
                ],
            }
        )
    return {
        "node_ids": [int(node_id) for node_id in _live_node_ids(state)],
        "edge_records": edge_records,
    }


def _validate_fixed_topology_signature(
    state: GRC9V3State,
    *,
    previous_topology_signature: Mapping[str, Any] | None,
) -> dict[str, Any]:
    current_signature = _topology_signature(state)
    if previous_topology_signature is None:
        return current_signature
    if dict(previous_topology_signature) != current_signature:
        raise InvalidStateTransitionError(
            "LGRC-1 fixed-topology eligibility requires unchanged topology"
        )
    return current_signature


def _coherence_budget(state: GRC9V3State) -> float:
    total = _finite_float(state.remainder, context="state.remainder")
    for node_id in _live_node_ids(state):
        if node_id not in state.nodes:
            raise ValueError(f"node state missing for live node {node_id}")
        total += _finite_float(
            state.nodes[node_id].coherence,
            context=f"node_coherence[{node_id}]",
        )
    return total


def _node_coherence_total(state: GRC9V3State) -> float:
    total = 0.0
    for node_id in _live_node_ids(state):
        if node_id not in state.nodes:
            raise ValueError(f"node state missing for live node {node_id}")
        total += _finite_float(
            state.nodes[node_id].coherence,
            context=f"node_coherence[{node_id}]",
        )
    return total


def _string_keyed_float_map(values: Mapping[int, float]) -> dict[str, float]:
    return {str(int(key)): float(value) for key, value in sorted(values.items())}


def _string_keyed_nested_float_map(
    values: Mapping[int, Mapping[int, float]],
) -> dict[str, dict[str, float]]:
    return {
        str(int(key)): _string_keyed_float_map(nested)
        for key, nested in sorted(values.items())
    }


def _string_keyed_sequence_map(
    values: Mapping[int, Sequence[int]],
) -> dict[str, list[int]]:
    return {
        str(int(key)): [int(value) for value in sequence]
        for key, sequence in sorted(values.items())
    }


def _require_artifact_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return value


def _artifact_bool(value: Any, *, context: str) -> bool:
    if not isinstance(value, bool):
        raise SnapshotCompatibilityError(f"{context} must be a boolean")
    return value


def _artifact_int(value: Any, *, context: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SnapshotCompatibilityError(f"{context} must be an integer")
    return int(value)


def _artifact_float(value: Any, *, context: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise SnapshotCompatibilityError(f"{context} must be a finite number") from exc
    if not math.isfinite(numeric):
        raise SnapshotCompatibilityError(f"{context} must be finite")
    return numeric


def _artifact_optional_float(value: Any, *, context: str) -> float | None:
    if value is None:
        return None
    numeric = _artifact_float(value, context=context)
    if numeric < 0.0:
        raise SnapshotCompatibilityError(f"{context} must be >= 0")
    return numeric


def _artifact_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str):
        raise SnapshotCompatibilityError(f"{context} must be a string")
    return value


def _parse_artifact_float_map(
    payload: Mapping[str, Any],
    *,
    key: str,
) -> dict[int, float]:
    mapping = _require_artifact_mapping(payload.get(key, {}), context=key)
    parsed: dict[int, float] = {}
    for raw_key, raw_value in mapping.items():
        try:
            int_key = int(raw_key)
        except (TypeError, ValueError) as exc:
            raise SnapshotCompatibilityError(f"{key} keys must be integers") from exc
        parsed[int_key] = _artifact_float(raw_value, context=f"{key}[{raw_key}]")
    return dict(sorted(parsed.items()))


def _parse_artifact_nested_float_map(
    payload: Mapping[str, Any],
    *,
    key: str,
) -> dict[int, dict[int, float]]:
    mapping = _require_artifact_mapping(payload.get(key, {}), context=key)
    parsed: dict[int, dict[int, float]] = {}
    for raw_key, raw_value in mapping.items():
        try:
            int_key = int(raw_key)
        except (TypeError, ValueError) as exc:
            raise SnapshotCompatibilityError(f"{key} keys must be integers") from exc
        parsed[int_key] = _parse_artifact_float_map(
            {"nested": raw_value},
            key="nested",
        )
    return dict(sorted(parsed.items()))


def _parse_artifact_sequence_map(
    payload: Mapping[str, Any],
    *,
    key: str,
) -> dict[int, tuple[int, ...]]:
    mapping = _require_artifact_mapping(payload.get(key, {}), context=key)
    parsed: dict[int, tuple[int, ...]] = {}
    for raw_key, raw_value in mapping.items():
        try:
            int_key = int(raw_key)
        except (TypeError, ValueError) as exc:
            raise SnapshotCompatibilityError(f"{key} keys must be integers") from exc
        if not isinstance(raw_value, list):
            raise SnapshotCompatibilityError(f"{key}[{raw_key}] must be a list")
        parsed[int_key] = tuple(
            _artifact_int(value, context=f"{key}[{raw_key}][]")
            for value in raw_value
        )
    return dict(sorted(parsed.items()))


def _parse_artifact_string_map(
    payload: Mapping[str, Any],
    *,
    key: str,
) -> dict[int, str]:
    mapping = _require_artifact_mapping(payload.get(key, {}), context=key)
    parsed: dict[int, str] = {}
    for raw_key, raw_value in mapping.items():
        try:
            int_key = int(raw_key)
        except (TypeError, ValueError) as exc:
            raise SnapshotCompatibilityError(f"{key} keys must be integers") from exc
        parsed[int_key] = _artifact_string(raw_value, context=f"{key}[{raw_key}]")
    return dict(sorted(parsed.items()))


def _artifact_optional_string(value: Any, *, context: str) -> str | None:
    if value is None:
        return None
    return _artifact_string(value, context=context)


def _artifact_nonempty_string(value: Any, *, context: str) -> str:
    resolved = _artifact_string(value, context=context)
    if not resolved:
        raise SnapshotCompatibilityError(f"{context} must be non-empty")
    return resolved


def _nonempty_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} must be a non-empty string")
    return value


def _nonnegative_int(value: Any, *, context: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{context} must be an integer")
    resolved = int(value)
    if resolved < 0:
        raise ValueError(f"{context} must be >= 0")
    return resolved


def _nonnegative_int_tuple(values: Sequence[int], *, context: str) -> tuple[int, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError(f"{context} must be a sequence")
    resolved = tuple(
        _nonnegative_int(value, context=f"{context}[]") for value in values
    )
    if not resolved:
        raise ValueError(f"{context} must be non-empty")
    return resolved


@dataclass(frozen=True)
class LGRC9V3RouteAspectHop:
    """One directed node/edge hop inside a route-aspect channel."""

    source_node_id: NodeId
    target_node_id: NodeId
    edge_id: EdgeId

    def __post_init__(self) -> None:
        _nonnegative_int(self.source_node_id, context="source_node_id")
        _nonnegative_int(self.target_node_id, context="target_node_id")
        _nonnegative_int(self.edge_id, context="edge_id")
        if int(self.source_node_id) == int(self.target_node_id):
            raise ValueError("route-aspect hop must connect distinct nodes")

    def to_artifact(self) -> dict[str, int]:
        """Return a JSON-compatible route hop."""

        return {
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "edge_id": int(self.edge_id),
        }


@dataclass(frozen=True)
class LGRC9V3RouteAspectChannel:
    """One pole-to-pole channel made of directed route hops."""

    channel_id: str
    source_pole_id: str
    target_pole_id: str
    route_hops: tuple[LGRC9V3RouteAspectHop, ...]
    expected_next_channel_id: str | None = None

    def __post_init__(self) -> None:
        _nonempty_string(self.channel_id, context="channel_id")
        _nonempty_string(self.source_pole_id, context="source_pole_id")
        _nonempty_string(self.target_pole_id, context="target_pole_id")
        if self.source_pole_id == self.target_pole_id:
            raise ValueError("route-aspect channel must connect distinct poles")
        if not self.route_hops:
            raise ValueError("route-aspect channel requires route_hops")
        for index, hop in enumerate(self.route_hops):
            if not isinstance(hop, LGRC9V3RouteAspectHop):
                raise ValueError("route_hops must contain route-aspect hops")
            if index > 0:
                previous = self.route_hops[index - 1]
                if int(previous.target_node_id) != int(hop.source_node_id):
                    raise ValueError("route-aspect channel hops must be contiguous")
        if self.expected_next_channel_id is not None:
            _nonempty_string(
                self.expected_next_channel_id,
                context="expected_next_channel_id",
            )

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible route channel."""

        return {
            "channel_id": self.channel_id,
            "source_pole_id": self.source_pole_id,
            "target_pole_id": self.target_pole_id,
            "expected_next_channel_id": self.expected_next_channel_id,
            "route_hops": [hop.to_artifact() for hop in self.route_hops],
        }

    def to_identity_artifact(self) -> dict[str, Any]:
        """Return channel fields that participate in route identity."""

        return self.to_artifact()


@dataclass(frozen=True)
class LGRC9V3RouteAspect:
    """Serializable pole/channel route-aspect contract for native packet loops."""

    route_aspect_id: str
    direction: str
    pole_regions: Mapping[str, Sequence[NodeId]]
    channels: tuple[LGRC9V3RouteAspectChannel, ...]
    channel_sequence: tuple[str, ...]
    closed_loop: bool = True
    artifact_kind: str = LGRC9V3_ROUTE_ASPECT_KIND
    artifact_schema_version: str = LGRC9V3_ROUTE_ASPECT_SCHEMA_VERSION
    runtime_family: str = LGRC9V3_RUNTIME_FAMILY
    evidence_class: str = LGRC9V3_ROUTE_ASPECT_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        _nonempty_string(self.route_aspect_id, context="route_aspect_id")
        if self.direction not in LGRC9V3_ROUTE_ASPECT_DIRECTIONS:
            raise ValueError("unsupported route-aspect direction")
        if not isinstance(self.closed_loop, bool):
            raise ValueError("closed_loop must be boolean")
        if self.artifact_kind != LGRC9V3_ROUTE_ASPECT_KIND:
            raise ValueError("unsupported route-aspect artifact kind")
        if self.artifact_schema_version != LGRC9V3_ROUTE_ASPECT_SCHEMA_VERSION:
            raise ValueError("unsupported route-aspect schema version")
        if self.runtime_family != LGRC9V3_RUNTIME_FAMILY:
            raise ValueError("unsupported route-aspect runtime family")
        if self.evidence_class != LGRC9V3_ROUTE_ASPECT_EVIDENCE_CLASS:
            raise ValueError("unsupported route-aspect evidence class")
        if not self.pole_regions:
            raise ValueError("route-aspect requires pole_regions")
        normalized_poles: dict[str, tuple[int, ...]] = {}
        assigned_pole_nodes: set[int] = set()
        for pole_id, node_ids in self.pole_regions.items():
            resolved_pole_id = _nonempty_string(pole_id, context="pole_id")
            resolved_node_ids = _nonnegative_int_tuple(
                tuple(int(node_id) for node_id in node_ids),
                context=f"pole_regions[{resolved_pole_id}]",
            )
            if len(set(resolved_node_ids)) != len(resolved_node_ids):
                raise ValueError("pole region node ids must be unique")
            overlapping_nodes = assigned_pole_nodes.intersection(resolved_node_ids)
            if overlapping_nodes:
                raise ValueError("pole regions must not overlap")
            assigned_pole_nodes.update(resolved_node_ids)
            normalized_poles[resolved_pole_id] = tuple(sorted(resolved_node_ids))
        object.__setattr__(self, "pole_regions", dict(sorted(normalized_poles.items())))
        if not self.channels:
            raise ValueError("route-aspect requires channels")
        channel_by_id: dict[str, LGRC9V3RouteAspectChannel] = {}
        for channel in self.channels:
            if not isinstance(channel, LGRC9V3RouteAspectChannel):
                raise ValueError("channels must contain route-aspect channels")
            if channel.channel_id in channel_by_id:
                raise ValueError("route-aspect channel ids must be unique")
            if channel.source_pole_id not in normalized_poles:
                raise ValueError("channel source pole missing from pole_regions")
            if channel.target_pole_id not in normalized_poles:
                raise ValueError("channel target pole missing from pole_regions")
            channel_by_id[channel.channel_id] = channel
        if not self.channel_sequence:
            raise ValueError("route-aspect requires channel_sequence")
        if len(set(self.channel_sequence)) != len(self.channel_sequence):
            raise ValueError("channel_sequence entries must be unique")
        if set(self.channel_sequence) != set(channel_by_id):
            raise ValueError("channel_sequence must reference every channel exactly once")
        for index, channel_id in enumerate(self.channel_sequence):
            channel = channel_by_id[channel_id]
            next_id = self.channel_sequence[(index + 1) % len(self.channel_sequence)]
            next_channel = channel_by_id[next_id]
            if channel.expected_next_channel_id is not None:
                if channel.expected_next_channel_id != next_id:
                    raise ValueError("expected_next_channel_id must match sequence")
            if channel.target_pole_id != next_channel.source_pole_id:
                raise ValueError("channel_sequence must be pole-contiguous")
        if self.closed_loop:
            first = channel_by_id[self.channel_sequence[0]]
            last = channel_by_id[self.channel_sequence[-1]]
            if last.target_pole_id != first.source_pole_id:
                raise ValueError("closed route-aspect sequence must return to start")
        object.__setattr__(
            self,
            "channels",
            tuple(channel_by_id[channel_id] for channel_id in self.channel_sequence),
        )
        object.__setattr__(self, "channel_sequence", tuple(self.channel_sequence))

    @property
    def pole_region_digest(self) -> str:
        """Digest over pole-region ids and node masks."""

        return digest_canonical_data({"pole_regions": self._pole_regions_artifact()})

    @property
    def channel_sequence_digest(self) -> str:
        """Digest over the declared channel order."""

        return digest_canonical_data(
            {"channel_sequence": [str(value) for value in self.channel_sequence]}
        )

    @property
    def route_aspect_digest(self) -> str:
        """Digest over the complete route-aspect identity."""

        return digest_canonical_data(self.to_identity_artifact())

    def _pole_regions_artifact(self) -> dict[str, list[int]]:
        return {
            str(pole_id): [int(node_id) for node_id in node_ids]
            for pole_id, node_ids in sorted(self.pole_regions.items())
        }

    def expected_next_channel_by_channel(self) -> dict[str, str]:
        """Return the route-order successor for every channel."""

        return {
            str(channel_id): str(
                self.channel_sequence[
                    (index + 1) % len(self.channel_sequence)
                ]
            )
            for index, channel_id in enumerate(self.channel_sequence)
        }

    def to_identity_artifact(self) -> dict[str, Any]:
        """Return canonical route-aspect identity fields."""

        return {
            "route_aspect_id": self.route_aspect_id,
            "direction": self.direction,
            "closed_loop": self.closed_loop,
            "pole_regions": self._pole_regions_artifact(),
            "channels": [
                channel.to_identity_artifact() for channel in self.channels
            ],
            "channel_sequence": [str(value) for value in self.channel_sequence],
        }

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible route-aspect artifact."""

        return {
            "artifact_kind": self.artifact_kind,
            "artifact_schema_version": self.artifact_schema_version,
            "runtime_family": self.runtime_family,
            "evidence_class": self.evidence_class,
            **self.to_identity_artifact(),
            "expected_next_channel_by_channel": self.expected_next_channel_by_channel(),
            "route_aspect_digest": self.route_aspect_digest,
            "pole_region_digest": self.pole_region_digest,
            "channel_sequence_digest": self.channel_sequence_digest,
        }


def restore_lgrc9v3_route_aspect_hop_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3RouteAspectHop:
    """Restore one route-aspect hop from artifact data."""

    mapping = _require_artifact_mapping(artifact, context="route_aspect_hop")
    return LGRC9V3RouteAspectHop(
        source_node_id=_artifact_int(
            mapping.get("source_node_id"),
            context="source_node_id",
        ),
        target_node_id=_artifact_int(
            mapping.get("target_node_id"),
            context="target_node_id",
        ),
        edge_id=_artifact_int(mapping.get("edge_id"), context="edge_id"),
    )


def restore_lgrc9v3_route_aspect_channel_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3RouteAspectChannel:
    """Restore one route-aspect channel from artifact data."""

    mapping = _require_artifact_mapping(artifact, context="route_aspect_channel")
    raw_hops = mapping.get("route_hops", [])
    if not isinstance(raw_hops, list):
        raise SnapshotCompatibilityError("route_hops must be a list")
    return LGRC9V3RouteAspectChannel(
        channel_id=_artifact_nonempty_string(
            mapping.get("channel_id"),
            context="channel_id",
        ),
        source_pole_id=_artifact_nonempty_string(
            mapping.get("source_pole_id"),
            context="source_pole_id",
        ),
        target_pole_id=_artifact_nonempty_string(
            mapping.get("target_pole_id"),
            context="target_pole_id",
        ),
        expected_next_channel_id=_artifact_optional_string(
            mapping.get("expected_next_channel_id"),
            context="expected_next_channel_id",
        ),
        route_hops=tuple(
            restore_lgrc9v3_route_aspect_hop_artifact(
                _require_artifact_mapping(hop, context="route_hops[]")
            )
            for hop in raw_hops
        ),
    )


def restore_lgrc9v3_route_aspect_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3RouteAspect:
    """Restore a route-aspect contract from artifact data."""

    mapping = _require_artifact_mapping(artifact, context="route_aspect")
    if (
        _artifact_string(mapping.get("artifact_kind"), context="artifact_kind")
        != LGRC9V3_ROUTE_ASPECT_KIND
    ):
        raise SnapshotCompatibilityError("unsupported route-aspect kind")
    if (
        _artifact_string(
            mapping.get("artifact_schema_version"),
            context="artifact_schema_version",
        )
        != LGRC9V3_ROUTE_ASPECT_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError("unsupported route-aspect schema version")
    raw_poles = _require_artifact_mapping(
        mapping.get("pole_regions"),
        context="pole_regions",
    )
    pole_regions: dict[str, tuple[int, ...]] = {}
    for pole_id, raw_nodes in raw_poles.items():
        if not isinstance(raw_nodes, list):
            raise SnapshotCompatibilityError("pole region nodes must be a list")
        pole_regions[_artifact_nonempty_string(pole_id, context="pole_id")] = tuple(
            _artifact_int(node_id, context=f"pole_regions[{pole_id}][]")
            for node_id in raw_nodes
        )
    raw_channels = mapping.get("channels", [])
    if not isinstance(raw_channels, list):
        raise SnapshotCompatibilityError("channels must be a list")
    raw_sequence = mapping.get("channel_sequence", [])
    if not isinstance(raw_sequence, list):
        raise SnapshotCompatibilityError("channel_sequence must be a list")
    route_aspect = LGRC9V3RouteAspect(
        route_aspect_id=_artifact_nonempty_string(
            mapping.get("route_aspect_id"),
            context="route_aspect_id",
        ),
        direction=_artifact_nonempty_string(mapping.get("direction"), context="direction"),
        closed_loop=_artifact_bool(mapping.get("closed_loop"), context="closed_loop"),
        pole_regions=pole_regions,
        channels=tuple(
            restore_lgrc9v3_route_aspect_channel_artifact(
                _require_artifact_mapping(channel, context="channels[]")
            )
            for channel in raw_channels
        ),
        channel_sequence=tuple(
            _artifact_nonempty_string(channel_id, context="channel_sequence[]")
            for channel_id in raw_sequence
        ),
    )
    for digest_key, current_digest in (
        ("route_aspect_digest", route_aspect.route_aspect_digest),
        ("pole_region_digest", route_aspect.pole_region_digest),
        ("channel_sequence_digest", route_aspect.channel_sequence_digest),
    ):
        if mapping.get(digest_key) is not None:
            recorded = _artifact_nonempty_string(
                mapping.get(digest_key),
                context=digest_key,
            )
            if recorded != current_digest:
                raise SnapshotCompatibilityError(f"{digest_key} mismatch")
    return route_aspect


def validate_lgrc9v3_route_aspect(
    route_aspect: LGRC9V3RouteAspect,
    *,
    state: GRC9V3State | None = None,
) -> LGRC9V3RouteAspect:
    """Validate a route aspect, optionally against a concrete GRC9V3 state."""

    if not isinstance(route_aspect, LGRC9V3RouteAspect):
        raise TypeError("route_aspect must be LGRC9V3RouteAspect")
    if state is None:
        return route_aspect
    live_nodes = set(_live_node_ids(state))
    live_edges = set(_live_edge_ids(state))
    for pole_id, node_ids in route_aspect.pole_regions.items():
        for node_id in node_ids:
            if int(node_id) not in live_nodes:
                raise InvalidStateTransitionError(
                    f"route-aspect pole {pole_id} references non-live node {node_id}"
                )
    for channel in route_aspect.channels:
        for hop in channel.route_hops:
            if int(hop.source_node_id) not in live_nodes:
                raise InvalidStateTransitionError(
                    f"route-aspect source node {hop.source_node_id} is not live"
                )
            if int(hop.target_node_id) not in live_nodes:
                raise InvalidStateTransitionError(
                    f"route-aspect target node {hop.target_node_id} is not live"
                )
            if int(hop.edge_id) not in live_edges or int(hop.edge_id) not in state.port_edges:
                raise InvalidStateTransitionError(
                    f"route-aspect edge {hop.edge_id} is not live"
                )
            edge_source, edge_target = state.topology.edge_ports(int(hop.edge_id))
            if int(edge_source[0]) != int(hop.source_node_id) or int(
                edge_target[0]
            ) != int(hop.target_node_id):
                raise InvalidStateTransitionError(
                    "route-aspect hop edge must match source -> target direction"
                )
    return route_aspect


def compile_lgrc9v3_route_aspect_to_causal_flux_routes(
    route_aspect: LGRC9V3RouteAspect,
    *,
    amount: float | None = None,
    amount_fraction: float | None = None,
    arrival_event_time_key: float | None = None,
) -> dict[int, list[dict[str, Any]]]:
    """Compile route-aspect hops to the existing node/edge route mapping."""

    validate_lgrc9v3_route_aspect(route_aspect)
    if amount is not None and amount_fraction is not None:
        raise ValueError("amount and amount_fraction are mutually exclusive")
    if amount is not None:
        _nonnegative_float(amount, context="amount")
    if amount_fraction is not None:
        _nonnegative_float(amount_fraction, context="amount_fraction")
    if arrival_event_time_key is not None:
        _nonnegative_float(arrival_event_time_key, context="arrival_event_time_key")
    routes: dict[int, list[dict[str, Any]]] = {}
    channel_by_id = {channel.channel_id: channel for channel in route_aspect.channels}
    for channel_id in route_aspect.channel_sequence:
        channel = channel_by_id[channel_id]
        for hop in channel.route_hops:
            route: dict[str, Any] = {
                "target_node_id": int(hop.target_node_id),
                "edge_id": int(hop.edge_id),
                "route_aspect_id": route_aspect.route_aspect_id,
                "route_aspect_digest": route_aspect.route_aspect_digest,
                "channel_id": channel.channel_id,
                "source_pole_id": channel.source_pole_id,
                "target_pole_id": channel.target_pole_id,
                "expected_next_channel_id": (
                    route_aspect.expected_next_channel_by_channel()[channel.channel_id]
                ),
            }
            if amount is not None:
                route["amount"] = float(amount)
            if amount_fraction is not None:
                route["amount_fraction"] = float(amount_fraction)
            if arrival_event_time_key is not None:
                route["arrival_event_time_key"] = float(arrival_event_time_key)
            routes.setdefault(int(hop.source_node_id), []).append(route)
    return {source_id: routes[source_id] for source_id in sorted(routes)}


__all__ = [
    'CAUSAL_BASIN_CORE_POLICY_DERIVED_ANNOTATION',
    'CAUSAL_BASIN_CORE_POLICY_DISABLED',
    'CAUSAL_CONE_POLICY_BOUNDED_SHORTEST_PATH',
    'CAUSAL_CONE_POLICY_DISABLED',
    'CAUSAL_DISTANCE_POLICY_DISABLED',
    'CAUSAL_DISTANCE_POLICY_EDGE_DELAY_SHORTEST_PATH',
    'CAUSAL_LAYER_MODE_ANNOTATION',
    'CAUSAL_LAYER_MODE_FIXED_TOPOLOGY_SEMICAUSAL',
    'CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY',
    'CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY',
    'EDGE_DELAY_POLICY_CONSTANT_DELAY',
    'EDGE_DELAY_POLICY_GEOMETRY_BASELINE',
    'EDGE_DELAY_POLICY_GRCV3_TEMPORAL_LABEL',
    'EVENT_TIME_POLICY_DERIVED_FROM_SYNCHRONOUS_STEP',
    'EVENT_TIME_POLICY_EXPLICIT_EVENT_TIME_KEY',
    'EVENT_TIME_POLICY_SYNCHRONOUS_LIMIT',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_BASE_CONDUCTANCE',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_COMBINED_COUPLING',
    'FUNCTIONAL_DISTANCE_POLICY_INVERSE_FLUX_COUPLING',
    'LAPSE_POLICY_BOUNDED_DENSITY_TENSION',
    'LAPSE_POLICY_UNIT',
    'LGRC9V3CollapseReabsorptionFieldNames',
    'LGRC9V3AutonomousProducerFieldNames',
    'LGRC9V3AutonomousProductionRecord',
    'LGRC9V3AutonomousProductionResult',
    'LGRC9V3CausalPulseSubstrateSurfaceFieldNames',
    'LGRC9V3CausalPulseSubstrateSurfaceLineageFieldNames',
    'LGRC9V3CausalPulseSubstrateSurfaceLineageRecord',
    'LGRC9V3CausalPulseSubstrateSurfacePolicy',
    'LGRC9V3CausalPulseSubstrateSurfaceRow',
    'LGRC9V3NativeRouteArbitrationFieldNames',
    'LGRC9V3NativeRouteArbitrationRecord',
    'LGRC9V3NativeRouteCandidateFieldNames',
    'LGRC9V3NativeRouteCandidateRecord',
    'LGRC9V3NativeRouteCandidateSetFieldNames',
    'LGRC9V3NativeRouteCandidateSetRecord',
    'LGRC9V3ChildBasinStateRecord',
    'LGRC9V3MultiBasinControlRecord',
    'LGRC9V3MultiBasinFlowWindowRecord',
    'LGRC9V3MultiBasinReplayValidationRecord',
    'LGRC9V3PacketFieldNames',
    'LGRC9V3PacketLedgerFieldNames',
    'LGRC9V3PacketTransportFieldNames',
    'LGRC9V3PendingFluxFieldNames',
    'LGRC9V3ProperTimeIdentityFieldNames',
    'LGRC9V3RouteAspect',
    'LGRC9V3RouteAspectChannel',
    'LGRC9V3RouteAspectHop',
    'LGRC9V3TimingFieldNames',
    'LGRC9V3TopologyContractFieldNames',
    'LGRC9V3TopologyStateReabsorptionFieldNames',
    'LGRC9V3TopologyStateReabsorptionRecord',
    'LGRC9V3_ANNOTATION_DIAGNOSTIC_SOURCE',
    'LGRC9V3_ANNOTATION_MODE_VERSION',
    'LGRC9V3_AUTONOMOUS_PRODUCER_CONTRACT_KIND',
    'LGRC9V3_AUTONOMOUS_PRODUCER_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_AUTONOMOUS_PRODUCER_EVIDENCE_CLASS',
    'LGRC9V3_AUTONOMOUS_PRODUCER_FIELD_NAMES',
    'LGRC9V3_AUTONOMOUS_PRODUCER_IDEMPOTENCY_POLICY',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICIES',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS',
    'LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING',
    'LGRC9V3_AUTONOMOUS_PRODUCER_QUEUE_OWNERSHIP_POLICY',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_CODES',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_BOUNDARY_BIRTH_TRIAL_SCHEDULED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_DISABLED_POLICY',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_DISABLED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_ORDER_MISMATCH',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_IDEMPOTENT_SKIP',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_NO_ELIGIBLE_WORK',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PACKET_DEPARTURE_SCHEDULED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_POLICY_NOT_IMPLEMENTED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_DISABLED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SUBTHRESHOLD',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_STALE_SURFACE_READ_BLOCKED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURFACE_ROW_SUPERSEDED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_TOPOLOGY_STATE_REABSORPTION_REQUIRED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD',
    'LGRC9V3_AUTONOMOUS_PRODUCER_REQUIRED_FIELDS',
    'LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_KIND',
    'LGRC9V3_AUTONOMOUS_PRODUCTION_RESULT_SCHEMA_VERSION',
    'LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1',
    'LGRC9V3_AUTONOMY_MODE_VERSION',
    'LGRC9V3_BUDGET_TRANSFER_POLICIES',
    'LGRC9V3_BUDGET_TRANSFER_POLICY_CONSERVING',
    'LGRC9V3_CAUSAL_ARTIFACT_KEY',
    'LGRC9V3_CAUSAL_ARTIFACT_KIND',
    'LGRC9V3_CAUSAL_ARTIFACT_SCHEMA_VERSION',
    'LGRC9V3_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCE_PARENT_DEBIT',
    'LGRC9V3_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0',
    'LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_DISABLED',
    'LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX',
    'LGRC9V3_CAUSAL_MODES_KEY',
    'LGRC9V3_CAUSAL_MODE_KEYS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_FORBIDDEN_SURFACE_KEYS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_BOUNDARY_POLARITY_SCORE',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_FEEDBACK_ELIGIBILITY',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_LOCAL_SUPPORT_MASS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_PROPER_TIME_PHASE',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_ROUTE_LOCAL_PULSE_CONTACT',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_KIND_SURFACE_DEFORMATION',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_DEFERRED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_FIXED_TOPOLOGY',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_SUPERSEDED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTIONS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_BLOCKER_REQUIRES_LGRC3',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_SUPERSEDED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_STATUSES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_PRODUCER_WRITABLE_FIELDS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_DERIVED_SURFACE',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_NODE_ONLY',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_BUDGET_SURFACES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_KIND',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_EVIDENCE_CLASS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_FIELD_NAMES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KIND_INPUTS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_KINDS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_FIELD_NAMES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICIES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_DISABLED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_POLICY_TRANSPORT_SUPERSEDE',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_KIND',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_LINEAGE_RECORD_SCHEMA_VERSION',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_MODE_VERSION',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICIES',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_DISABLED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_REQUIRED_FIELDS',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_KIND',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_ROW_SCHEMA_VERSION',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_REPLAY_DECLARED',
    'LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_UPDATE_POLICY_VERSION',
    'LGRC9V3_COLLAPSE_PACKET_TRANSPORT_EVIDENCE_CLASS',
    'LGRC9V3_COLLAPSE_PACKET_TRANSPORT_POLICY_REDIRECT_OR_SETTLE',
    'LGRC9V3_COLLAPSE_REABSORPTION_EVIDENCE_CLASS',
    'LGRC9V3_COLLAPSE_REABSORPTION_FIELD_NAMES',
    'LGRC9V3_COLLAPSE_REABSORPTION_REQUIRED_FIELDS',
    'LGRC9V3_DEFAULT_CAUSAL_MODES',
    'LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER',
    'LGRC9V3_DERIVED_EVIDENCE_CLASS',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_FIELD_NAMES',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_FORBIDDEN_INPUTS',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICIES',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_DISABLED',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_CODES',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_DECLARED_LOCAL_PREFERENCE',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_KIND',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_RECORD_SCHEMA_VERSION',
    'LGRC9V3_NATIVE_ROUTE_ARBITRATION_SELECTED_REASON_CODES',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_FIELD_NAMES',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_KIND',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_RECORD_SCHEMA_VERSION',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_DIGEST_ASCENDING',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_KEYS',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_FIELD_NAMES',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_KIND',
    'LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_RECORD_SCHEMA_VERSION',
    'LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE',
    'LGRC9V3_NATIVE_ROUTE_INTENT_MERGE',
    'LGRC9V3_NATIVE_ROUTE_INTENT_REABSORB',
    'LGRC9V3_NATIVE_ROUTE_INTENT_REDIRECT',
    'LGRC9V3_NATIVE_ROUTE_INTENT_SPLIT',
    'LGRC9V3_NATIVE_ROUTE_INTENTS',
    'LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICIES',
    'LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_DECLARED_TIEBREAKER',
    'LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED',
    'LGRC9V3_CHILD_BASIN_STATE_RECORD_KIND',
    'LGRC9V3_CHILD_BASIN_STATE_RECORD_SCHEMA_VERSION',
    'LGRC9V3_MULTI_BASIN_CONTROL_RECORD_KIND',
    'LGRC9V3_MULTI_BASIN_CONTROL_RECORD_SCHEMA_VERSION',
    'LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_CLOSED',
    'LGRC9V3_MULTI_BASIN_CONTROL_STATUS_FAILED_OPEN',
    'LGRC9V3_MULTI_BASIN_CONTROL_STATUS_PASSED',
    'LGRC9V3_MULTI_BASIN_CONTROL_STATUSES',
    'LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_KIND',
    'LGRC9V3_MULTI_BASIN_FLOW_WINDOW_RECORD_SCHEMA_VERSION',
    'LGRC9V3_MULTI_BASIN_FORBIDDEN_CLAIM_KEYS',
    'LGRC9V3_MULTI_BASIN_FORBIDDEN_INPUTS',
    'LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_CLASSES',
    'LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATIVE_SOURCE_CURRENT',
    'LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_NATURALIZATION_DEBT',
    'LGRC9V3_MULTI_BASIN_PRODUCER_RESIDUE_PRODUCER_ASSISTED',
    'LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_CLOSED',
    'LGRC9V3_MULTI_BASIN_REPLAY_STATUS_FAILED_OPEN',
    'LGRC9V3_MULTI_BASIN_REPLAY_STATUS_NOT_RUN',
    'LGRC9V3_MULTI_BASIN_REPLAY_STATUS_PASSED',
    'LGRC9V3_MULTI_BASIN_REPLAY_STATUSES',
    'LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_KIND',
    'LGRC9V3_MULTI_BASIN_REPLAY_VALIDATION_RECORD_SCHEMA_VERSION',
    'LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICIES',
    'LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_DISABLED',
    'LGRC9V3_NATIVE_MULTI_BASIN_FORMATION_POLICY_POST_REFINEMENT_REPLAY',
    'LGRC9V3_IDENTITY_CLOCK_POLICIES',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_BASIN_AGGREGATE',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_CAUSAL_FRONTIER',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_LINEAGE',
    'LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL',
    'LGRC9V3_IDENTITY_THRESHOLD_POLICIES',
    'LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY',
    'LGRC9V3_INTERNAL_EDGE_DELAY_POLICY_EXPLICIT_OR_TAU0',
    'LGRC9V3_LGRC1_ARTIFACT_KIND',
    'LGRC9V3_LGRC1_ARTIFACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC1_DIAGNOSTIC_SOURCE',
    'LGRC9V3_LGRC1_MODE_VERSION',
    'LGRC9V3_LGRC2_MODE_VERSION',
    'LGRC9V3_LGRC2_PACKET_CONTRACT_KIND',
    'LGRC9V3_LGRC2_PACKET_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PACKET_LEDGER_KIND',
    'LGRC9V3_LGRC2_PACKET_LEDGER_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_KIND',
    'LGRC9V3_LGRC2_PACKET_PROCESSING_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_KIND',
    'LGRC9V3_LGRC2_PENDING_FLUX_LEDGER_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_KIND',
    'LGRC9V3_LGRC3_COLLAPSE_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_KIND',
    'LGRC9V3_LGRC3_COLLAPSE_REABSORPTION_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_MODE_VERSION',
    'LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_KIND',
    'LGRC9V3_LGRC3_PACKET_TRANSPORT_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_EVIDENCE_CLASS',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_KIND',
    'LGRC9V3_LGRC3_POLICY_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_KIND',
    'LGRC9V3_LGRC3_PROPER_TIME_INHERITANCE_RESULT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_KIND',
    'LGRC9V3_LGRC3_TOPOLOGY_CONTRACT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS',
    'LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_IN_SCOPE',
    'LGRC9V3_LGRC3_TOPOLOGY_EVENT_KINDS_OUT_OF_SCOPE',
    'LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_KIND',
    'LGRC9V3_LGRC3_TOPOLOGY_REPLAY_VALIDATION_SCHEMA_VERSION',
    'LGRC9V3_LINEAGE_TRANSFER_POLICIES',
    'LGRC9V3_LINEAGE_TRANSFER_POLICY_EXPLICIT_MAP',
    'LGRC9V3_PACKETIZED_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_KIND',
    'LGRC9V3_PACKET_ARRIVAL_ELIGIBILITY_SCHEMA_VERSION',
    'LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_DELAY_DERIVED',
    'LGRC9V3_PACKET_ARRIVAL_EVENT_TIME_POLICY_EXPLICIT',
    'LGRC9V3_PACKET_BUDGET_INVARIANT',
    'LGRC9V3_PACKET_EVENT_KINDS',
    'LGRC9V3_PACKET_EVENT_KIND_ARRIVAL',
    'LGRC9V3_PACKET_EVENT_KIND_DEPARTURE',
    'LGRC9V3_PACKET_EVENT_QUEUE_TIE_BREAK_POLICY',
    'LGRC9V3_PACKET_FIELD_NAMES',
    'LGRC9V3_PACKET_LEDGER_FIELD_NAMES',
    'LGRC9V3_PACKET_REQUIRED_FIELDS',
    'LGRC9V3_PACKET_STATES',
    'LGRC9V3_PACKET_STATE_ARRIVED',
    'LGRC9V3_PACKET_STATE_CANCELLED',
    'LGRC9V3_PACKET_STATE_IN_FLIGHT',
    'LGRC9V3_PACKET_STATE_SCHEDULED',
    'LGRC9V3_PACKET_TRANSPORT_EVIDENCE_CLASS',
    'LGRC9V3_PACKET_TRANSPORT_FIELD_NAMES',
    'LGRC9V3_PACKET_TRANSPORT_REQUIRED_FIELDS',
    'LGRC9V3_PENDING_FLUX_COMPACTION_POLICY_EXACT',
    'LGRC9V3_PENDING_FLUX_EVIDENCE_CLASS',
    'LGRC9V3_PENDING_FLUX_FIELD_NAMES',
    'LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES',
    'LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS',
    'LGRC9V3_PROPER_TIME_INHERITANCE_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_INHERITANCE_POLICY_UNIFORM_PARENT',
    'LGRC9V3_PROPER_TIME_INHERITANCE_REQUIRED_FIELDS',
    'LGRC9V3_PROPER_TIME_TRANSFER_POLICIES',
    'LGRC9V3_PROPER_TIME_TRANSFER_POLICY_SELECTED_SINK_CONTINUITY',
    'LGRC9V3_REFINEMENT_LINEAGE_REQUIRED_FIELDS',
    'LGRC9V3_ROUTE_ASPECT_DIRECTION_CLOCKWISE',
    'LGRC9V3_ROUTE_ASPECT_DIRECTION_COUNTER_CLOCKWISE',
    'LGRC9V3_ROUTE_ASPECT_DIRECTION_CUSTOM',
    'LGRC9V3_ROUTE_ASPECT_DIRECTIONS',
    'LGRC9V3_ROUTE_ASPECT_EVIDENCE_CLASS',
    'LGRC9V3_ROUTE_ASPECT_KIND',
    'LGRC9V3_ROUTE_ASPECT_SCHEMA_VERSION',
    'LGRC9V3_RUNTIME_FAMILY',
    'LGRC9V3_SEMICAUSAL_EVIDENCE_CLASS',
    'LGRC9V3_TIMING_ALIASES',
    'LGRC9V3_TIMING_FIELD_NAMES',
    'LGRC9V3_TOPOLOGY_CONTRACT_EVIDENCE_CLASS',
    'LGRC9V3_TOPOLOGY_CONTRACT_FIELD_NAMES',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_BOUNDARY_BIRTH',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_PROPER_TIME_INHERITANCE',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REABSORPTION',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT',
    'LGRC9V3_TOPOLOGY_EVENT_KIND_REFINEMENT_PACKET_TRANSPORT',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_MERGED',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REBASED',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_REJECTED',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTION_SUPERSEDED',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_ACTIONS',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_BLOCKER_REQUIRES_LGRC3',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_FIELD_NAMES',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICIES',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_DISABLED',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_POLICY_LINEAGE_REBASE',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_KIND',
    'LGRC9V3_TOPOLOGY_STATE_REABSORPTION_RECORD_SCHEMA_VERSION',
    'LGRC9V3_TOPOLOGY_REPLAY_VALIDATION_EVIDENCE_CLASS',
    'LGRC9_FAMILY_PHASE',
    'LGRC9_RUNTIME_FAMILY',
    'LGRC_RUNTIME_LEVEL_LGRC0',
    'LGRC_RUNTIME_LEVEL_LGRC1',
    'LGRC_RUNTIME_LEVEL_LGRC2',
    'LGRC_RUNTIME_LEVEL_LGRC3',
    'LGRCV3_FAMILY_PHASE',
    'LGRCV3_RUNTIME_FAMILY',
    'PROPER_TIME_POLICY_ANNOTATION',
    'PROPER_TIME_POLICY_GLOBAL_SCHEDULER',
    'PROPER_TIME_POLICY_LOCAL_EVENT_FRONTIER',
    'PROPER_TIME_POLICY_SYNCHRONOUS_LIMIT',
    '_ALLOWED_CAUSAL_BASIN_CORE_POLICIES',
    '_ALLOWED_CAUSAL_BOUNDARY_BIRTH_COHERENCE_SOURCES',
    '_ALLOWED_CAUSAL_BOUNDARY_BIRTH_EDGE_DELAY_POLICIES',
    '_ALLOWED_CAUSAL_BOUNDARY_BIRTH_POLICIES',
    '_ALLOWED_CAUSAL_CONE_POLICIES',
    '_ALLOWED_CAUSAL_DISTANCE_POLICIES',
    '_ALLOWED_CAUSAL_LAYER_MODES',
    '_ALLOWED_EDGE_DELAY_POLICIES',
    '_ALLOWED_EVENT_TIME_POLICIES',
    '_ALLOWED_FUNCTIONAL_DISTANCE_POLICIES',
    '_ALLOWED_LAPSE_POLICIES',
    '_ALLOWED_PROPER_TIME_POLICIES',
    '_ALLOWED_RUNTIME_LEVELS',
    '_artifact_bool',
    '_artifact_float',
    '_artifact_int',
    '_artifact_optional_float',
    '_artifact_optional_string',
    '_artifact_string',
    '_coherence_budget',
    '_finite_float',
    '_live_edge_ids',
    '_live_node_ids',
    '_node_coherence_total',
    '_nonnegative_float',
    '_parse_artifact_float_map',
    '_parse_artifact_nested_float_map',
    '_parse_artifact_sequence_map',
    '_parse_artifact_string_map',
    '_positive_float',
    '_require_artifact_mapping',
    '_require_choice',
    '_string_keyed_float_map',
    '_string_keyed_nested_float_map',
    '_string_keyed_sequence_map',
    '_topology_signature',
    '_validate_fixed_topology_signature',
    'build_lgrc9v3_autonomous_production_record_id',
    'build_lgrc9v3_autonomous_surface_digest',
    'build_lgrc9v3_causal_pulse_substrate_surface_contract_artifact',
    'build_lgrc9v3_causal_pulse_substrate_surface_digest',
    'build_lgrc9v3_causal_pulse_substrate_surface_lineage_idempotency_key',
    'build_lgrc9v3_causal_pulse_substrate_surface_lineage_record_digest',
    'build_lgrc9v3_disabled_autonomous_production_result',
    'build_lgrc9v3_disabled_causal_pulse_substrate_surface_policy',
    'build_lgrc9v3_child_basin_state_record_digest',
    'build_lgrc9v3_multi_basin_control_record_digest',
    'build_lgrc9v3_multi_basin_flow_window_record_digest',
    'build_lgrc9v3_multi_basin_replay_validation_record_digest',
    'build_lgrc9v3_native_route_arbitration_idempotency_key',
    'build_lgrc9v3_native_route_arbitration_record_digest',
    'build_lgrc9v3_native_route_candidate_record_digest',
    'build_lgrc9v3_native_route_candidate_set_idempotency_key',
    'build_lgrc9v3_native_route_candidate_set_record_digest',
    'build_lgrc9v3_topology_event_digest',
    'build_lgrc9v3_topology_state_reabsorption_idempotency_key',
    'build_lgrc9v3_topology_state_reabsorption_record_digest',
    'compile_lgrc9v3_route_aspect_to_causal_flux_routes',
    'derive_lgrc9v3_packet_arrival_event_time_key',
    'restore_lgrc9v3_autonomous_production_record_artifact',
    'restore_lgrc9v3_autonomous_production_result_artifact',
    'restore_lgrc9v3_causal_pulse_substrate_surface_policy_artifact',
    'restore_lgrc9v3_causal_pulse_substrate_surface_lineage_record_artifact',
    'restore_lgrc9v3_causal_pulse_substrate_surface_row_artifact',
    'restore_lgrc9v3_child_basin_state_record_artifact',
    'restore_lgrc9v3_multi_basin_control_record_artifact',
    'restore_lgrc9v3_multi_basin_flow_window_record_artifact',
    'restore_lgrc9v3_multi_basin_replay_validation_record_artifact',
    'restore_lgrc9v3_native_route_arbitration_record_artifact',
    'restore_lgrc9v3_native_route_candidate_record_artifact',
    'restore_lgrc9v3_native_route_candidate_set_record_artifact',
    'restore_lgrc9v3_route_aspect_artifact',
    'restore_lgrc9v3_topology_state_reabsorption_record_artifact',
    'restore_lgrc9v3_route_aspect_channel_artifact',
    'restore_lgrc9v3_route_aspect_hop_artifact',
    'validate_lgrc9v3_autonomous_producer_policy',
    'validate_lgrc9v3_causal_modes',
    'validate_lgrc9v3_route_aspect',
]
