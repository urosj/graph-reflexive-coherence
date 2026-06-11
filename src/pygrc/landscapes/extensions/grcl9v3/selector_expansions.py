"""Vocabulary-facing GRCL-9V3 selector expansion contract."""

from __future__ import annotations

from collections.abc import Mapping


GRCL9V3_SELECTOR_EXPANSION_VERSION = "grcl9v3_selector_expansions_v1"

GRCL9V3_SOURCE_SELECTOR_EXPANSIONS: Mapping[str, tuple[str, ...]] = {
    "hybrid_spark_events": (
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
    ),
    "hybrid_tensor_available": (
        "tensor_trace_present",
        "tensor_anisotropy_present",
        "row_mismatch_sum_present",
        "tensor_hotspot_sample_present",
    ),
    "hybrid_expansion_events": (
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
    ),
    "appendix_e_summary": (
        "appendix_e_completed",
        "appendix_e_daughter_sinks",
        "appendix_e_hierarchy_recorded",
        "hybrid_spark_candidate_present",
        "mechanical_expansion_present",
        "hybrid_spark_completed_present",
    ),
    "appendix_e_no_completion": (
        "appendix_e_no_completion",
    ),
    "choice_collapse_events": (
        "choice_detected_present",
        "collapse_event_present",
        "collapse_registry_present",
    ),
    "no_choice_collapse_events": (
        "no_choice_detected_events",
        "no_collapse_events",
    ),
    "growth_events": (
        "growth_event_present",
        "birth_probability_recorded",
        "growth_child_recorded",
    ),
    "front_growth_provenance": (
        "front_growth_provenance_present",
    ),
    "pressure_boundary_growth_provenance": (
        "pressure_boundary_growth_provenance_present",
    ),
    "closed_front_no_growth": (
        "no_growth_events",
        "no_front_growth_provenance_present",
    ),
    "growth_reduction": (
        "growth_reduction_observed",
    ),
    "growth_before_collapse": (
        "growth_before_collapse_observed",
    ),
    "basin_assignment_learning": (
        "learning_state_present",
        "collapsed_sink_recorded",
    ),
    "growth_collapse_relay_diagnostics": (
        "growth_child_later_collapsed_sink",
        "collapsed_sink_later_growth_parent",
        "full_growth_collapse_relay",
    ),
    "no_growth_events": (
        "no_growth_events",
    ),
    "transport_rerouting_signature": (
        "transport_flux_present",
        "transport_potential_range_present",
        "positive_flux_edges_present",
        "tensor_anisotropy_present",
        "row_mismatch_sum_present",
        "tensor_hotspot_sample_present",
    ),
    "hessian_row_basis_diagnostic": (
        "hessian_row_basis_backend",
        "weighted_least_squares_unavailable",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "hessian_weighted_least_squares_diagnostic": (
        "hessian_weighted_least_squares_backend",
        "weighted_least_squares_available",
        "tensor_trace_present",
        "previous_signed_hessian_available",
    ),
    "no_lifecycle_events": (
        "no_lifecycle_events",
    ),
}


def grcl9v3_source_selector_expansions() -> Mapping[str, tuple[str, ...]]:
    """Return the source-selector to field-selector expansion mapping."""

    return dict(GRCL9V3_SOURCE_SELECTOR_EXPANSIONS)


__all__ = [
    "GRCL9V3_SELECTOR_EXPANSION_VERSION",
    "GRCL9V3_SOURCE_SELECTOR_EXPANSIONS",
    "grcl9v3_source_selector_expansions",
]
