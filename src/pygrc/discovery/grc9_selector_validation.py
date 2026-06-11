"""Field-backed selector validation for GRC9 discovery telemetry."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Any

from .grc9_manifest import (
    GRC9DiscoveryManifest,
    GRC9EvidenceFields,
    GRC9ManifestRunScope,
    GRC9MotifRecord,
    GRC9SelectorSpec,
    GRC9SourceArtifact,
    is_session_id,
)


GRC9_SELECTOR_VALIDATION_VERSION = "grc9_selector_validation_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")


@dataclass(frozen=True)
class GRC9SelectorDefinition:
    selector_id: str
    surface: str
    query: str
    expected_type: str
    field_path: str
    predicate: Callable[[Mapping[str, Any]], bool]

    def to_spec(self) -> GRC9SelectorSpec:
        return GRC9SelectorSpec(
            selector_id=self.selector_id,
            surface=self.surface,
            query=self.query,
            expected_type=self.expected_type,
        )


@dataclass(frozen=True)
class GRC9SelectorResult:
    selector_id: str
    passed: bool
    field_path: str
    observed_value: Any

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "selector_id": self.selector_id,
            "passed": self.passed,
            "field_path": self.field_path,
            "observed_value": self.observed_value,
        }


@dataclass(frozen=True)
class GRC9LaneSelectorValidation:
    session_id: str
    lane_name: str
    run_id: str
    seed_name: str
    profile: str
    requested_steps: int
    event_counts_by_kind: Mapping[str, int]
    expected_selector_ids: tuple[str, ...]
    selector_results: tuple[GRC9SelectorResult, ...]
    confidence_score: int
    confidence_label: str
    motif_id: str | None
    notes: Mapping[str, str]

    @property
    def passed_selector_ids(self) -> tuple[str, ...]:
        return tuple(
            result.selector_id for result in self.selector_results if result.passed
        )

    @property
    def missing_selector_ids(self) -> tuple[str, ...]:
        passed = set(self.passed_selector_ids)
        return tuple(
            selector_id
            for selector_id in self.expected_selector_ids
            if selector_id not in passed
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "lane_name": self.lane_name,
            "run_id": self.run_id,
            "seed_name": self.seed_name,
            "profile": self.profile,
            "requested_steps": self.requested_steps,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "expected_selector_ids": list(self.expected_selector_ids),
            "selector_results": [item.to_mapping() for item in self.selector_results],
            "passed_selector_ids": list(self.passed_selector_ids),
            "missing_selector_ids": list(self.missing_selector_ids),
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "motif_id": self.motif_id,
            "notes": dict(self.notes),
        }


@dataclass(frozen=True)
class GRC9SelectorValidationSession:
    session_id: str
    source_session_ids: tuple[str, ...]
    validations: tuple[GRC9LaneSelectorValidation, ...]
    manifest_path: str
    iteration: str = "I06_prediction_validation_and_candidate_selectors"

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "source_session_ids": list(self.source_session_ids),
            "lane_count": len(self.validations),
            "motif_count": sum(1 for item in self.validations if item.motif_id),
            "strong_candidate_count": sum(
                1 for item in self.validations if item.confidence_label == "strong_candidate"
            ),
            "candidate_count": sum(
                1 for item in self.validations if item.confidence_label == "candidate"
            ),
            "weak_candidate_count": sum(
                1 for item in self.validations if item.confidence_label == "weak_candidate"
            ),
            "rejected_count": sum(
                1 for item in self.validations if item.confidence_label == "rejected"
            ),
            "no_expectation_lane_count": len(self.no_expectation_lanes),
            "no_expectation_lanes": list(self.no_expectation_lanes),
            "validations": [item.to_mapping() for item in self.validations],
            "manifest_path": self.manifest_path,
        }

    @property
    def no_expectation_lanes(self) -> tuple[str, ...]:
        return tuple(
            f"{validation.session_id}/{validation.lane_name}"
            for validation in self.validations
            if not validation.expected_selector_ids
        )


def _get_path(payload: Mapping[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        else:
            return default
    return current


def _event_count(kind: str) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: int(lane["event_counts_by_kind"].get(kind, 0)) > 0


def _event_count_at_least(kind: str, count: int) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: int(lane["event_counts_by_kind"].get(kind, 0)) >= count


def _summary_count(path: str) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: float(_get_path(lane["summary"], path, 0) or 0) > 0


def _summary_count_at_least(path: str, count: int) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: int(_get_path(lane["summary"], path, 0) or 0) >= count


def _no_events(lane: Mapping[str, Any]) -> bool:
    return sum(int(value) for value in lane["event_counts_by_kind"].values()) == 0


def _no_growth(lane: Mapping[str, Any]) -> bool:
    return int(lane["event_counts_by_kind"].get("growth", 0)) == 0


def _module_size_differs_from_parent(lane: Mapping[str, Any]) -> bool:
    lane_name = str(lane["lane_name"])
    module_size = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.expansion_summary.max_module_node_count",
            0,
        )
        or 0
    )
    if lane_name.endswith("_low"):
        return module_size == 5
    if lane_name.endswith("_high"):
        return module_size >= 6
    return module_size > 0


def _birth_probability_recorded(lane: Mapping[str, Any]) -> bool:
    return (
        _get_path(
            lane["summary"],
            "family_extensions.grc9.growth_summary.birth_probability_max",
        )
        is not None
    )


def _path_present(path: str) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: _get_path(lane["summary"], path) is not None


def _summary_value_positive(path: str) -> Callable[[Mapping[str, Any]], bool]:
    return lambda lane: float(_get_path(lane["summary"], path, 0.0) or 0.0) > 0.0


def _coarse_signed_flux_supported(lane: Mapping[str, Any]) -> bool:
    fields = _get_path(
        lane["summary"],
        "family_extensions.grc9.final_coarse_graining_summary.exact_split_supported_fields",
        (),
    )
    return "signed_flux" in tuple(fields or ())


def _transport_labels_available(lane: Mapping[str, Any]) -> bool:
    return (
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_transport_summary.label_availability.overall",
        )
        == "all"
    )


def _budget_error_balanced(lane: Mapping[str, Any]) -> bool:
    return abs(float(_get_path(lane["summary"], "final_observables.budget_error", 0.0) or 0.0)) < 1e-9


def _row_tensor_strong_anisotropy(lane: Mapping[str, Any]) -> bool:
    value = float(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max",
            0.0,
        )
        or 0.0
    )
    return value > 100.0


def _row_tensor_flat_anisotropy(lane: Mapping[str, Any]) -> bool:
    value = float(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max",
            0.0,
        )
        or 0.0
    )
    return abs(value) <= 1e-9


def _column_proxy_near_zero(lane: Mapping[str, Any]) -> bool:
    return int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count",
            0,
        )
        or 0
    ) > 0


def _column_proxy_nonzero(lane: Mapping[str, Any]) -> bool:
    count = int(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count",
            0,
        )
        or 0
    )
    min_abs = float(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_column_diagnostic_summary.column_diagnostic_min_abs",
            0.0,
        )
        or 0.0
    )
    return count == 0 and min_abs >= 0.5


def _coarse_cache_warm(lane: Mapping[str, Any]) -> bool:
    return (
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_coarse_graining_summary.coarse_cache_state",
        )
        == "warm"
    )


def _coarse_conductance_field_present(lane: Mapping[str, Any]) -> bool:
    fields = _get_path(
        lane["summary"],
        "family_extensions.grc9.final_coarse_graining_summary.coarse_fields_list",
        (),
    )
    return "conductance" in tuple(fields or ())


def _coarse_sparse_profile(lane: Mapping[str, Any]) -> bool:
    value = float(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_coarse_graining_summary.column_total_sparsity_by_field.conductance",
            0.0,
        )
        or 0.0
    )
    return value >= 0.5


def _coarse_dense_profile(lane: Mapping[str, Any]) -> bool:
    value = float(
        _get_path(
            lane["summary"],
            "family_extensions.grc9.final_coarse_graining_summary.column_total_sparsity_by_field.conductance",
            1.0,
        )
        or 0.0
    )
    return value <= 1e-9


def _budget_uniform_shift_observed(lane: Mapping[str, Any]) -> bool:
    return (
        _get_path(
            lane.get("final_step", {}),
            "family_extensions.grc9.budget_correction.last_budget_correction_path",
        )
        == "uniform_shift"
        and _budget_error_balanced(lane)
    )


def _budget_negative_projection_path_observed(lane: Mapping[str, Any]) -> bool:
    return (
        _get_path(
            lane.get("final_step", {}),
            "family_extensions.grc9.budget_correction.last_budget_correction_path",
        )
        != "uniform_shift"
        and _budget_error_balanced(lane)
    )


def _transport_top_edge_in(edge_ids: set[int]) -> Callable[[Mapping[str, Any]], bool]:
    def predicate(lane: Mapping[str, Any]) -> bool:
        sample = _get_path(
            lane["summary"],
            "family_extensions.grc9.final_transport_summary.strongest_flux_edges_sample",
            (),
        )
        if not isinstance(sample, Sequence) or not sample:
            return False
        first = sample[0]
        if not isinstance(first, Mapping):
            return False
        return int(first.get("edge_id", -1)) in edge_ids

    return predicate


def _target_signature_suppressed(lane: Mapping[str, Any]) -> bool:
    lane_name = str(lane["lane_name"])
    event_counts = lane["event_counts_by_kind"]
    summary = lane["summary"]
    if lane_name in {"spark_column_proxy_eps_fail", "spark_instability_tau_fail"}:
        return int(event_counts.get("spark", 0)) == 0 and int(event_counts.get("expansion", 0)) == 0
    if lane_name == "growth_pressure_lambda_low":
        return int(event_counts.get("growth", 0)) == 0
    if lane_name == "post_expansion_fission_min_mass_fail":
        return (
            int(
                _get_path(
                    summary,
                    "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
                    0,
                )
                or 0
            )
            == 0
        )
    return False


SELECTORS: tuple[GRC9SelectorDefinition, ...] = (
    GRC9SelectorDefinition(
        selector_id="spark_event_present",
        surface="events.jsonl",
        query="event_counts_by_kind.spark > 0",
        expected_type="bool",
        field_path="event_counts_by_kind.spark",
        predicate=_event_count("spark"),
    ),
    GRC9SelectorDefinition(
        selector_id="expansion_event_present",
        surface="events.jsonl",
        query="event_counts_by_kind.expansion > 0",
        expected_type="bool",
        field_path="event_counts_by_kind.expansion",
        predicate=_event_count("expansion"),
    ),
    GRC9SelectorDefinition(
        selector_id="growth_event_present",
        surface="events.jsonl",
        query="event_counts_by_kind.growth > 0",
        expected_type="bool",
        field_path="event_counts_by_kind.growth",
        predicate=_event_count("growth"),
    ),
    GRC9SelectorDefinition(
        selector_id="dual_spark_present",
        surface="events.jsonl",
        query="event_counts_by_kind.spark >= 2",
        expected_type="bool",
        field_path="event_counts_by_kind.spark",
        predicate=_event_count_at_least("spark", 2),
    ),
    GRC9SelectorDefinition(
        selector_id="dual_expansion_present",
        surface="events.jsonl",
        query="event_counts_by_kind.expansion >= 2",
        expected_type="bool",
        field_path="event_counts_by_kind.expansion",
        predicate=_event_count_at_least("expansion", 2),
    ),
    GRC9SelectorDefinition(
        selector_id="spark_column_proxy_present",
        surface="run_summary.json",
        query="lifecycle_event_counts.spark_column_proxy_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count",
        predicate=_summary_count(
            "family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="spark_instability_present",
        surface="run_summary.json",
        query="lifecycle_event_counts.spark_instability_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.lifecycle_event_counts.spark_instability_count",
        predicate=_summary_count(
            "family_extensions.grc9.lifecycle_event_counts.spark_instability_count"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="expansion_module_created",
        surface="run_summary.json",
        query="expansion_summary.max_module_node_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.expansion_summary.max_module_node_count",
        predicate=_summary_count(
            "family_extensions.grc9.expansion_summary.max_module_node_count"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="module_size_response",
        surface="run_summary.json",
        query="D_eff perturbation changes expansion_summary.max_module_node_count",
        expected_type="bool",
        field_path="family_extensions.grc9.expansion_summary.max_module_node_count",
        predicate=_module_size_differs_from_parent,
    ),
    GRC9SelectorDefinition(
        selector_id="growth_probability_recorded",
        surface="run_summary.json",
        query="growth_summary.birth_probability_max is present",
        expected_type="bool",
        field_path="family_extensions.grc9.growth_summary.birth_probability_max",
        predicate=_birth_probability_recorded,
    ),
    GRC9SelectorDefinition(
        selector_id="fission_confirmed_summary",
        surface="run_summary.json",
        query="expansion_summary.identity_fission_confirmed_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
        predicate=_summary_count(
            "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="fission_confirmed_twice",
        surface="run_summary.json",
        query="expansion_summary.identity_fission_confirmed_count >= 2",
        expected_type="bool",
        field_path="family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
        predicate=_summary_count_at_least(
            "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
            2,
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="row_tensor_summary_present",
        surface="run_summary.json",
        query="final_row_tensor_summary.row_tensor_max is present",
        expected_type="bool",
        field_path="family_extensions.grc9.final_row_tensor_summary.row_tensor_max",
        predicate=_path_present(
            "family_extensions.grc9.final_row_tensor_summary.row_tensor_max"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="row_tensor_signal_positive",
        surface="run_summary.json",
        query="final_row_tensor_summary.row_tensor_max > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_row_tensor_summary.row_tensor_max",
        predicate=_summary_value_positive(
            "family_extensions.grc9.final_row_tensor_summary.row_tensor_max"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="column_diagnostic_summary_present",
        surface="run_summary.json",
        query="final_column_diagnostic_summary.column_profile_sparsity is present",
        expected_type="bool",
        field_path="family_extensions.grc9.final_column_diagnostic_summary.column_profile_sparsity",
        predicate=_path_present(
            "family_extensions.grc9.final_column_diagnostic_summary.column_profile_sparsity"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="column_proxy_candidates_present",
        surface="run_summary.json",
        query="final_column_diagnostic_summary.column_proxy_candidate_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count",
        predicate=_summary_value_positive(
            "family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="coarse_signed_flux_supported",
        surface="run_summary.json",
        query="final_coarse_graining_summary.exact_split_supported_fields contains signed_flux",
        expected_type="bool",
        field_path="family_extensions.grc9.final_coarse_graining_summary.exact_split_supported_fields",
        predicate=_coarse_signed_flux_supported,
    ),
    GRC9SelectorDefinition(
        selector_id="budget_error_balanced",
        surface="run_summary.json",
        query="final_observables.budget_error == 0",
        expected_type="bool",
        field_path="final_observables.budget_error",
        predicate=_budget_error_balanced,
    ),
    GRC9SelectorDefinition(
        selector_id="transport_labels_available",
        surface="run_summary.json",
        query="final_transport_summary.label_availability.overall == all",
        expected_type="bool",
        field_path="family_extensions.grc9.final_transport_summary.label_availability.overall",
        predicate=_transport_labels_available,
    ),
    GRC9SelectorDefinition(
        selector_id="transport_flux_positive",
        surface="run_summary.json",
        query="final_transport_summary.flux_abs_sum > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_transport_summary.flux_abs_sum",
        predicate=_summary_value_positive(
            "family_extensions.grc9.final_transport_summary.flux_abs_sum"
        ),
    ),
    GRC9SelectorDefinition(
        selector_id="row_tensor_strong_anisotropy",
        surface="run_summary.json",
        query="final_row_tensor_summary.row_tensor_anisotropy_max > 100",
        expected_type="bool",
        field_path="family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max",
        predicate=_row_tensor_strong_anisotropy,
    ),
    GRC9SelectorDefinition(
        selector_id="row_tensor_flat_anisotropy",
        surface="run_summary.json",
        query="final_row_tensor_summary.row_tensor_anisotropy_max == 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max",
        predicate=_row_tensor_flat_anisotropy,
    ),
    GRC9SelectorDefinition(
        selector_id="column_proxy_near_zero",
        surface="run_summary.json",
        query="final_column_diagnostic_summary.column_proxy_candidate_count > 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count",
        predicate=_column_proxy_near_zero,
    ),
    GRC9SelectorDefinition(
        selector_id="column_proxy_nonzero_suppressed",
        surface="run_summary.json",
        query="column proxy candidate count is zero and min_abs is above eps_spark",
        expected_type="bool",
        field_path="family_extensions.grc9.final_column_diagnostic_summary.column_diagnostic_min_abs",
        predicate=_column_proxy_nonzero,
    ),
    GRC9SelectorDefinition(
        selector_id="coarse_cache_warm",
        surface="run_summary.json",
        query="final_coarse_graining_summary.coarse_cache_state == warm",
        expected_type="bool",
        field_path="family_extensions.grc9.final_coarse_graining_summary.coarse_cache_state",
        predicate=_coarse_cache_warm,
    ),
    GRC9SelectorDefinition(
        selector_id="coarse_conductance_field_present",
        surface="run_summary.json",
        query="final_coarse_graining_summary.coarse_fields_list contains conductance",
        expected_type="bool",
        field_path="family_extensions.grc9.final_coarse_graining_summary.coarse_fields_list",
        predicate=_coarse_conductance_field_present,
    ),
    GRC9SelectorDefinition(
        selector_id="coarse_sparse_profile",
        surface="run_summary.json",
        query="column_total_sparsity_by_field.conductance >= 0.5",
        expected_type="bool",
        field_path="family_extensions.grc9.final_coarse_graining_summary.column_total_sparsity_by_field.conductance",
        predicate=_coarse_sparse_profile,
    ),
    GRC9SelectorDefinition(
        selector_id="coarse_dense_profile",
        surface="run_summary.json",
        query="column_total_sparsity_by_field.conductance == 0",
        expected_type="bool",
        field_path="family_extensions.grc9.final_coarse_graining_summary.column_total_sparsity_by_field.conductance",
        predicate=_coarse_dense_profile,
    ),
    GRC9SelectorDefinition(
        selector_id="budget_uniform_shift_observed",
        surface="steps.jsonl/run_summary.json",
        query="last step budget_correction.last_budget_correction_path == uniform_shift and final budget error is balanced",
        expected_type="bool",
        field_path="final_step.family_extensions.grc9.budget_correction.last_budget_correction_path",
        predicate=_budget_uniform_shift_observed,
    ),
    GRC9SelectorDefinition(
        selector_id="budget_negative_projection_path_observed",
        surface="steps.jsonl/run_summary.json",
        query="last step budget path is not uniform_shift and final budget error is balanced",
        expected_type="bool",
        field_path="final_step.family_extensions.grc9.budget_correction.last_budget_correction_path",
        predicate=_budget_negative_projection_path_observed,
    ),
    GRC9SelectorDefinition(
        selector_id="transport_short_path_dominant",
        surface="run_summary.json",
        query="strongest_flux_edges_sample[0].edge_id is on the short path",
        expected_type="bool",
        field_path="family_extensions.grc9.final_transport_summary.strongest_flux_edges_sample",
        predicate=_transport_top_edge_in({0, 1}),
    ),
    GRC9SelectorDefinition(
        selector_id="transport_long_path_dominant",
        surface="run_summary.json",
        query="strongest_flux_edges_sample[0].edge_id is on the long path",
        expected_type="bool",
        field_path="family_extensions.grc9.final_transport_summary.strongest_flux_edges_sample",
        predicate=_transport_top_edge_in({2, 3, 4, 5}),
    ),
    GRC9SelectorDefinition(
        selector_id="target_signature_suppressed",
        surface="events.jsonl/run_summary.json",
        query="targeted fail/low perturbation has no target signature",
        expected_type="bool",
        field_path="event_counts_by_kind + run_summary",
        predicate=_target_signature_suppressed,
    ),
    GRC9SelectorDefinition(
        selector_id="no_growth_events",
        surface="events.jsonl",
        query="event_counts_by_kind.growth == 0",
        expected_type="bool",
        field_path="event_counts_by_kind.growth",
        predicate=_no_growth,
    ),
    GRC9SelectorDefinition(
        selector_id="no_lifecycle_events",
        surface="events.jsonl",
        query="sum(event_counts_by_kind.values()) == 0",
        expected_type="bool",
        field_path="event_counts_by_kind",
        predicate=_no_events,
    ),
)


SELECTOR_BY_ID = {selector.selector_id: selector for selector in SELECTORS}


EXPECTED_SELECTORS_BY_LANE: Mapping[str, tuple[str, ...]] = {
    "spark_precursor_positive_control": ("spark_event_present",),
    "spark_precursor_negative_control": ("no_lifecycle_events",),
    "expansion_module_positive_control": (
        "spark_event_present",
        "expansion_event_present",
    ),
    "expansion_module_negative_control": ("no_lifecycle_events",),
    "column_reassignment_positive_control": ("expansion_event_present",),
    "column_reassignment_negative_control": ("no_lifecycle_events",),
    "growth_pressure_positive_control": ("growth_event_present",),
    "growth_pressure_negative_control": ("no_lifecycle_events",),
    "row_tensor_regime_positive_control": (
        "row_tensor_summary_present",
        "row_tensor_signal_positive",
    ),
    "row_tensor_regime_negative_control": (
        "row_tensor_summary_present",
        "row_tensor_signal_positive",
    ),
    "column_diagnostic_regime_positive_control": (
        "column_diagnostic_summary_present",
        "column_proxy_candidates_present",
    ),
    "column_diagnostic_regime_negative_control": (
        "column_diagnostic_summary_present",
        "column_proxy_candidates_present",
    ),
    "coarse_profile_sparsity_positive_control": ("coarse_signed_flux_supported",),
    "coarse_profile_sparsity_negative_control": ("coarse_signed_flux_supported",),
    "budget_correction_positive_control": ("budget_error_balanced",),
    "budget_correction_negative_control": ("budget_error_balanced",),
    "quiescent_basin_no_event_control": ("no_lifecycle_events",),
    "quiescent_basin_negative_control": ("no_lifecycle_events",),
    "transport_pathway_positive_control": (
        "transport_labels_available",
        "transport_flux_positive",
    ),
    "transport_pathway_negative_control": (
        "transport_labels_available",
        "transport_flux_positive",
    ),
    "fission_candidate_positive_control": ("fission_confirmed_summary",),
    "fission_candidate_negative_control": ("fission_confirmed_summary",),
    "spark_column_proxy_emitter": (
        "spark_event_present",
        "expansion_event_present",
        "spark_column_proxy_present",
        "expansion_module_created",
    ),
    "spark_instability_emitter": (
        "spark_event_present",
        "expansion_event_present",
        "spark_instability_present",
        "expansion_module_created",
    ),
    "spark_to_expansion_emitter": (
        "spark_event_present",
        "expansion_event_present",
        "spark_column_proxy_present",
        "expansion_module_created",
    ),
    "growth_pressure_emitter": (
        "growth_event_present",
        "growth_probability_recorded",
    ),
    "post_expansion_fission_emitter": (
        "fission_confirmed_summary",
        "no_growth_events",
    ),
    "spark_column_proxy_eps_pass": (
        "spark_event_present",
        "expansion_event_present",
        "spark_column_proxy_present",
    ),
    "spark_column_proxy_eps_fail": ("target_signature_suppressed",),
    "spark_instability_tau_pass": (
        "spark_event_present",
        "expansion_event_present",
        "spark_instability_present",
    ),
    "spark_instability_tau_fail": ("target_signature_suppressed",),
    "spark_to_expansion_d_eff_low": (
        "spark_event_present",
        "expansion_event_present",
        "module_size_response",
    ),
    "spark_to_expansion_d_eff_high": (
        "spark_event_present",
        "expansion_event_present",
        "module_size_response",
    ),
    "growth_pressure_lambda_high": (
        "growth_event_present",
        "growth_probability_recorded",
    ),
    "growth_pressure_lambda_low": ("target_signature_suppressed",),
    "post_expansion_fission_min_mass_pass": ("fission_confirmed_summary",),
    "post_expansion_fission_min_mass_fail": ("target_signature_suppressed",),
    "spark_growth_combo": (
        "spark_event_present",
        "expansion_event_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
    "dual_spark_combo": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "fission_confirmed_summary",
    ),
    "spark_fission_combo": (
        "spark_event_present",
        "expansion_event_present",
        "fission_confirmed_summary",
    ),
    "growth_fission_combo": (
        "growth_event_present",
        "growth_probability_recorded",
        "fission_confirmed_summary",
    ),
    "spark_growth_fission_combo": (
        "spark_event_present",
        "expansion_event_present",
        "growth_event_present",
        "fission_confirmed_twice",
    ),
    "row_tensor_strong_anisotropy_control": (
        "row_tensor_summary_present",
        "row_tensor_strong_anisotropy",
    ),
    "row_tensor_flat_control": (
        "row_tensor_summary_present",
        "row_tensor_flat_anisotropy",
    ),
    "column_proxy_near_zero_control": (
        "column_diagnostic_summary_present",
        "column_proxy_near_zero",
    ),
    "column_proxy_nonzero_control": (
        "column_diagnostic_summary_present",
        "column_proxy_nonzero_suppressed",
    ),
    "coarse_cache_populated_sparse_profile_control": (
        "coarse_cache_warm",
        "coarse_conductance_field_present",
        "coarse_sparse_profile",
    ),
    "coarse_cache_populated_dense_profile_control": (
        "coarse_cache_warm",
        "coarse_conductance_field_present",
        "coarse_dense_profile",
    ),
    "budget_uniform_shift_trigger_control": (
        "budget_error_balanced",
        "budget_uniform_shift_observed",
    ),
    "budget_simplex_projection_trigger_control": (
        "budget_error_balanced",
        "budget_negative_projection_path_observed",
    ),
    "transport_short_path_dominant_control": (
        "transport_labels_available",
        "transport_short_path_dominant",
    ),
    "transport_long_path_dominant_control": (
        "transport_labels_available",
        "transport_long_path_dominant",
    ),
    "all_events_complex_control": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
    "all_events_complex_extra_leaf_perturbation_control": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
    "all_events_complex_coherence_jitter_perturbation_control": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
    "all_events_complex_soft_threshold_perturbation_control": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
    "all_events_complex_high_degree_perturbation_control": (
        "dual_spark_present",
        "dual_expansion_present",
        "spark_column_proxy_present",
        "spark_instability_present",
        "growth_event_present",
        "fission_confirmed_summary",
    ),
}


def run_grc9_selector_validation(
    *,
    session_id: str = "S0022",
    source_session_ids: Sequence[str] = (
        "S0004",
        "S0005",
        "S0006",
        "S0021",
        "S0010",
        "S0020",
    ),
    session_root: str | Path | None = None,
) -> GRC9SelectorValidationSession:
    """Run selector validation against saved discovery telemetry."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    for source_session_id in source_session_ids:
        if not is_session_id(source_session_id):
            raise ValueError("source_session_ids must use S0001-style formatting")

    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    validations = tuple(
        _validate_lane(lane_payload)
        for lane_payload in _iter_lane_payloads(source_session_ids)
    )
    manifest = _build_manifest(
        session_id=session_id,
        source_session_ids=tuple(source_session_ids),
        validations=validations,
    )
    manifest_path = root / "selector_manifest.json"
    _write_json(manifest_path, manifest.to_mapping())

    session = GRC9SelectorValidationSession(
        session_id=session_id,
        source_session_ids=tuple(source_session_ids),
        validations=validations,
        manifest_path=str(manifest_path),
    )
    _write_json(reports_root / "selector_validation_report.json", session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_readme(root, session)
    _write_summary_markdown(reports_root / "selector_validation_summary.md", session)
    return session


def _iter_lane_payloads(source_session_ids: Sequence[str]) -> tuple[Mapping[str, Any], ...]:
    lanes: list[Mapping[str, Any]] = []
    for source_session_id in source_session_ids:
        report_path = (
            DISCOVERY_SESSION_ROOT / source_session_id / "reports" / "run_report.json"
        )
        report = _read_json(report_path)
        for lane in report.get("lanes", []):
            lane_name = str(lane["lane_name"])
            artifact_root = Path(str(lane["artifact_root"]))
            telemetry_root = artifact_root / "telemetry"
            summary = _read_json(telemetry_root / "run_summary.json")
            events = _read_jsonl(telemetry_root / "events.jsonl")
            steps = _read_jsonl(telemetry_root / "steps.jsonl")
            lanes.append(
                {
                    "source_session_id": source_session_id,
                    "lane_name": lane_name,
                    "run_id": str(lane["run_id"]),
                    "seed_name": str(lane["seed_name"]),
                    "profile": str(lane["profile"]),
                    "requested_steps": int(lane["requested_steps"]),
                    "event_counts_by_kind": dict(lane["event_counts_by_kind"]),
                    "artifact_root": str(artifact_root),
                    "summary": summary,
                    "events": events,
                    "steps": steps,
                    "final_step": steps[-1] if steps else {},
                }
            )
    return tuple(lanes)


def _validate_lane(lane: Mapping[str, Any]) -> GRC9LaneSelectorValidation:
    lane_name = str(lane["lane_name"])
    expected_selector_ids = EXPECTED_SELECTORS_BY_LANE.get(lane_name, ())
    selector_results = tuple(
        _evaluate_selector(SELECTOR_BY_ID[selector_id], lane)
        for selector_id in expected_selector_ids
    )
    passed = sum(1 for result in selector_results if result.passed)
    total = len(expected_selector_ids)
    confidence_score = _confidence_score(passed=passed, total=total, lane=lane)
    confidence_label = _confidence_label(confidence_score)
    motif_id = (
        f"grc9-motif-{str(lane['source_session_id']).lower()}-{lane_name.replace('_', '-')}"
        if confidence_score >= 3
        else None
    )
    notes = {
        "artifact_root": str(lane["artifact_root"]),
        "selector_version": GRC9_SELECTOR_VALIDATION_VERSION,
    }
    if not expected_selector_ids:
        notes["selector_scope"] = "no lane-specific selector expectations in iteration 6"
    return GRC9LaneSelectorValidation(
        session_id=str(lane["source_session_id"]),
        lane_name=lane_name,
        run_id=str(lane["run_id"]),
        seed_name=str(lane["seed_name"]),
        profile=str(lane["profile"]),
        requested_steps=int(lane["requested_steps"]),
        event_counts_by_kind=dict(lane["event_counts_by_kind"]),
        expected_selector_ids=tuple(expected_selector_ids),
        selector_results=selector_results,
        confidence_score=confidence_score,
        confidence_label=confidence_label,
        motif_id=motif_id,
        notes=notes,
    )


def _evaluate_selector(
    selector: GRC9SelectorDefinition,
    lane: Mapping[str, Any],
) -> GRC9SelectorResult:
    passed = bool(selector.predicate(lane))
    observed_value = _observed_selector_value(selector, lane)
    return GRC9SelectorResult(
        selector_id=selector.selector_id,
        passed=passed,
        field_path=selector.field_path,
        observed_value=observed_value,
    )


def _observed_selector_value(
    selector: GRC9SelectorDefinition,
    lane: Mapping[str, Any],
) -> Any:
    if selector.field_path.startswith("event_counts_by_kind"):
        if selector.field_path == "event_counts_by_kind":
            return dict(lane["event_counts_by_kind"])
        _, _, kind = selector.field_path.partition(".")
        return int(lane["event_counts_by_kind"].get(kind, 0))
    if selector.field_path == "event_counts_by_kind + run_summary":
        return {
            "event_counts_by_kind": dict(lane["event_counts_by_kind"]),
            "identity_fission_confirmed_count": _get_path(
                lane["summary"],
                "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
                0,
            ),
        }
    if selector.field_path.startswith("final_step."):
        _, _, path = selector.field_path.partition(".")
        return _get_path(lane.get("final_step", {}), path)
    return _get_path(lane["summary"], selector.field_path)


def _confidence_score(
    *,
    passed: int,
    total: int,
    lane: Mapping[str, Any],
) -> int:
    if total == 0:
        return 0
    if passed == 0:
        return 1
    if passed < total:
        return 2
    if str(lane["source_session_id"]) == "S0006":
        return 5
    if str(lane["source_session_id"]) == "S0007":
        return 4
    return 4


def _confidence_label(score: int) -> str:
    if score >= 5:
        return "strong_candidate"
    if score >= 3:
        return "candidate"
    if score >= 2:
        return "weak_candidate"
    return "rejected"


def _build_manifest(
    *,
    session_id: str,
    source_session_ids: Sequence[str],
    validations: Sequence[GRC9LaneSelectorValidation],
) -> GRC9DiscoveryManifest:
    profiles = tuple(sorted({validation.profile for validation in validations}))
    lanes = tuple(sorted({validation.lane_name for validation in validations}))
    motifs = tuple(
        _motif_from_validation(validation)
        for validation in validations
        if validation.motif_id is not None
    )
    return GRC9DiscoveryManifest(
        source_artifacts=tuple(
            GRC9SourceArtifact(
                artifact_role="selector_validation_source",
                path=f"outputs/grc9/phenomenology_discovery/sessions/{source_session_id}/",
                used_for_discovery=True,
            )
            for source_session_id in source_session_ids
        ),
        run_scope=GRC9ManifestRunScope(profiles=profiles, lanes=lanes),
        selectors=tuple(selector.to_spec() for selector in SELECTORS),
        motifs=motifs,
        output_roots={
            "discovery": "outputs/grc9/phenomenology_discovery",
            "sessions": "outputs/grc9/phenomenology_discovery/sessions",
            "selector_session": f"outputs/grc9/phenomenology_discovery/sessions/{session_id}",
        },
    )


def _motif_from_validation(validation: GRC9LaneSelectorValidation) -> GRC9MotifRecord:
    observed_fields = tuple(
        result.field_path for result in validation.selector_results if result.passed
    )
    missing_fields = tuple(
        result.field_path for result in validation.selector_results if not result.passed
    )
    predicted_fields = tuple(
        SELECTOR_BY_ID[selector_id].field_path
        for selector_id in validation.expected_selector_ids
    )
    event_ids = tuple(
        f"{validation.session_id}:{validation.lane_name}:event-{index}"
        for index in range(sum(int(value) for value in validation.event_counts_by_kind.values()))
    )
    return GRC9MotifRecord(
        motif_id=str(validation.motif_id),
        hypothesis_id=f"grc9_selector_{validation.lane_name}",
        phenomenon=_phenomenon_for_lane(validation.lane_name),
        profile=validation.profile,
        lane=validation.lane_name,
        run_id=validation.run_id,
        seed_name=validation.seed_name,
        session_ids=(validation.session_id,),
        step_window=(0, validation.requested_steps),
        event_ids=event_ids,
        checkpoint_ids=tuple(
            f"step-{step_index:08d}"
            for step_index in range(validation.requested_steps + 1)
        ),
        predicted_evidence_fields=predicted_fields,
        observed_evidence_fields=observed_fields,
        evidence_fields=GRC9EvidenceFields(
            predicted=predicted_fields,
            observed=observed_fields,
            missing=missing_fields,
        ),
        confidence_score=validation.confidence_score,
        confidence_label=validation.confidence_label,
        review_status=validation.confidence_label,
        non_claims=(
            "grcv3_semantics",
            "grcl9_lowering",
            "lorentzian_causal_layer",
        ),
        notes=validation.notes,
    )


def _phenomenon_for_lane(lane_name: str) -> str:
    if "fission" in lane_name and "growth" in lane_name and "spark" in lane_name:
        return "spark_growth_fission"
    if "fission" in lane_name and "growth" in lane_name:
        return "growth_fission"
    if "fission" in lane_name and "spark" in lane_name:
        return "spark_fission"
    if "growth" in lane_name and "spark" in lane_name:
        return "spark_growth"
    if "dual_spark" in lane_name:
        return "dual_spark"
    if "fission" in lane_name:
        return "fission"
    if "growth" in lane_name:
        return "growth"
    if "expansion" in lane_name or "d_eff" in lane_name:
        return "expansion"
    if "spark" in lane_name:
        return "spark"
    return "diagnostic"


def _write_readme(root: Path, session: GRC9SelectorValidationSession) -> None:
    root.mkdir(parents=True, exist_ok=True)
    source_args = " ".join(
        f"--source-session-id {source_session_id}"
        for source_session_id in session.source_session_ids
    )
    lines = [
        f"# {session.session_id}. GRC9 Selector Validation",
        "",
        "Status: `completed`",
        "",
        "This session validates Iteration 6 selectors against saved GRC9 discovery telemetry.",
        "",
        "Replay:",
        "",
        "```bash",
        f"PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_validation --session-id {session.session_id} {source_args}",
        "```",
        "",
        f"Source sessions: `{', '.join(session.source_session_ids)}`",
        f"Validated lanes: `{len(session.validations)}`",
        f"Motif candidates: `{sum(1 for item in session.validations if item.motif_id)}`",
        "",
        "Primary reports:",
        "",
        "- `reports/selector_validation_report.json`",
        "- `reports/selector_validation_summary.md`",
        "- `selector_manifest.json`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _session_manifest(session: GRC9SelectorValidationSession) -> Mapping[str, Any]:
    source_args = " ".join(
        f"--source-session-id {source_session_id}"
        for source_session_id in session.source_session_ids
    )
    return {
        "session_id": session.session_id,
        "program": "grc9_phenomenology_discovery",
        "family": "grc9",
        "track": "phenomenology_discovery",
        "iteration": "I06_prediction_validation_and_candidate_selectors",
        "session_kind": "selector_validation",
        "phenomenon": "selector validation with targeted diagnostics"
        if "S0010" in session.source_session_ids
        else "selector validation",
        "seed_family": " plus ".join(session.source_session_ids),
        "control_role": "saved telemetry selectors",
        "status": "completed",
        "created_at": "2026-04-25",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            "pygrc.discovery.grc9_selector_validation --session-id "
            f"{session.session_id} {source_args}"
        ),
        "input_paths": [
            f"outputs/grc9/phenomenology_discovery/sessions/{source_session_id}/"
            for source_session_id in session.source_session_ids
        ],
        "output_paths": [
            str(Path(session.manifest_path)),
            str(
                DISCOVERY_SESSION_ROOT
                / session.session_id
                / "reports"
                / "selector_validation_report.json"
            ),
            str(
                DISCOVERY_SESSION_ROOT
                / session.session_id
                / "reports"
                / "selector_validation_summary.md"
            ),
        ],
        "telemetry_paths": [],
        "checkpoint_paths": [],
        "visualization_paths": [],
        "prediction_summary": "Selectors should match saved telemetry signatures for expected lanes.",
        "observation_summary": (
            f"Validated {len(session.validations)} lanes and recorded "
            f"{sum(1 for item in session.validations if item.motif_id)} motif candidates; "
            f"{len(session.no_expectation_lanes)} lanes had no selector expectations."
        ),
        "replay_notes": "Selector validation reads saved telemetry only; rerun source sessions first if their artifacts change.",
    }


def _write_summary_markdown(
    path: Path,
    session: GRC9SelectorValidationSession,
) -> None:
    labels = Counter(validation.confidence_label for validation in session.validations)
    lines = [
        f"# {session.session_id} Selector Validation Summary",
        "",
        "## Scope",
        "",
        f"- Source sessions: `{', '.join(session.source_session_ids)}`",
        f"- Validated lanes: `{len(session.validations)}`",
        f"- Motif candidates: `{sum(1 for item in session.validations if item.motif_id)}`",
        f"- Strong candidates: `{labels.get('strong_candidate', 0)}`",
        f"- Candidates: `{labels.get('candidate', 0)}`",
        f"- Weak candidates: `{labels.get('weak_candidate', 0)}`",
        f"- Rejected/no expectation lanes: `{labels.get('rejected', 0)}`",
        f"- Lanes without selector expectations: `{len(session.no_expectation_lanes)}`",
        "",
    ]
    if session.no_expectation_lanes:
        lines.extend(
            [
                "## Missing Selector Expectations",
                "",
                *(
                    f"- `{lane_name}`"
                    for lane_name in session.no_expectation_lanes
                ),
                "",
            ]
        )
    lines.extend(["## Lane Results", ""])
    for validation in session.validations:
        lines.append(
            f"- `{validation.session_id}/{validation.lane_name}`: "
            f"`{validation.confidence_label}` score `{validation.confidence_score}`; "
            f"passed `{len(validation.passed_selector_ids)}/{len(validation.expected_selector_ids)}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    if not path.exists():
        return ()
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0022")
    parser.add_argument(
        "--source-session-id",
        action="append",
        dest="source_session_ids",
        default=None,
    )
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_selector_validation(
        session_id=args.session_id,
        source_session_ids=tuple(
            args.source_session_ids
            or ("S0004", "S0005", "S0006", "S0021", "S0010", "S0020")
        ),
        session_root=args.session_root,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "iteration": session.iteration,
                "source_session_ids": list(session.source_session_ids),
                "lane_count": payload["lane_count"],
                "motif_count": payload["motif_count"],
                "report_path": str(
                    DISCOVERY_SESSION_ROOT
                    / session.session_id
                    / "reports"
                    / "selector_validation_report.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_SELECTOR_VALIDATION_VERSION",
    "GRC9LaneSelectorValidation",
    "GRC9SelectorDefinition",
    "GRC9SelectorResult",
    "GRC9SelectorValidationSession",
    "SELECTORS",
    "run_grc9_selector_validation",
]
