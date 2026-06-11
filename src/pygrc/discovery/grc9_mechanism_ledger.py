"""Mechanism ledger for GRC9 phenomenology discovery."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .grc9_manifest import (
    GRC9PredictedSignature,
    GRC9SourceReference,
    GRC9StructureHypothesis,
)


GRC9_MECHANISM_LEDGER_VERSION = "grc9_mechanism_ledger_v1"

RUNTIME_TESTABLE = "testable"
RUNTIME_DEFERRED = "deferred"
RUNTIME_RESERVED_FUTURE = "reserved_future"
RUNTIME_OUT_OF_SCOPE = "out_of_scope"

_RUNTIME_STATUSES = frozenset(
    {
        RUNTIME_TESTABLE,
        RUNTIME_DEFERRED,
        RUNTIME_RESERVED_FUTURE,
        RUNTIME_OUT_OF_SCOPE,
    }
)


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_runtime_status(value: str) -> None:
    if value not in _RUNTIME_STATUSES:
        raise ValueError(f"runtime_status must be one of {tuple(sorted(_RUNTIME_STATUSES))}")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


def _to_source_refs(values: Sequence[GRC9SourceReference | Mapping[str, Any]]) -> tuple[GRC9SourceReference, ...]:
    return tuple(
        item
        if isinstance(item, GRC9SourceReference)
        else GRC9SourceReference.from_mapping(item)
        for item in values
    )


def _to_signatures(
    values: Sequence[GRC9PredictedSignature | Mapping[str, Any]],
) -> tuple[GRC9PredictedSignature, ...]:
    return tuple(
        item
        if isinstance(item, GRC9PredictedSignature)
        else GRC9PredictedSignature.from_mapping(item)
        for item in values
    )


@dataclass(frozen=True)
class GRC9MechanismLedgerEntry:
    mechanism_id: str
    phenomenon: str
    paper_sources: tuple[GRC9SourceReference, ...]
    spec_sources: tuple[GRC9SourceReference, ...]
    equations: tuple[str, ...]
    inequalities: tuple[str, ...]
    thresholds: Mapping[str, Any]
    policy_choices: Mapping[str, Any]
    graph_preconditions: Mapping[str, Any]
    predicted_telemetry_fields: tuple[GRC9PredictedSignature, ...]
    runtime_status: str
    runtime_blockers: tuple[str, ...] = ()
    testable_with_current_runtime: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.mechanism_id, field_name="mechanism_id")
        _require_non_empty(self.phenomenon, field_name="phenomenon")
        _validate_runtime_status(self.runtime_status)
        if self.runtime_status == RUNTIME_TESTABLE and not self.testable_with_current_runtime:
            raise ValueError("testable mechanisms must set testable_with_current_runtime")
        if self.runtime_status != RUNTIME_TESTABLE and self.testable_with_current_runtime:
            raise ValueError("non-testable mechanisms cannot set testable_with_current_runtime")
        if self.runtime_status != RUNTIME_TESTABLE and not self.runtime_blockers:
            raise ValueError("non-testable mechanisms must record runtime_blockers")
        if self.runtime_status == RUNTIME_TESTABLE and not self.predicted_telemetry_fields:
            raise ValueError("testable mechanisms must map to predicted telemetry fields")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "phenomenon": self.phenomenon,
            "paper_sources": [item.to_mapping() for item in self.paper_sources],
            "spec_sources": [item.to_mapping() for item in self.spec_sources],
            "equations": list(self.equations),
            "inequalities": list(self.inequalities),
            "thresholds": _json_safe(self.thresholds),
            "policy_choices": _json_safe(self.policy_choices),
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "predicted_telemetry_fields": [
                item.to_mapping() for item in self.predicted_telemetry_fields
            ],
            "runtime_status": self.runtime_status,
            "runtime_blockers": list(self.runtime_blockers),
            "testable_with_current_runtime": self.testable_with_current_runtime,
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9MechanismLedgerEntry:
        return cls(
            mechanism_id=str(value["mechanism_id"]),
            phenomenon=str(value["phenomenon"]),
            paper_sources=_to_source_refs(value.get("paper_sources", [])),
            spec_sources=_to_source_refs(value.get("spec_sources", [])),
            equations=tuple(str(item) for item in value.get("equations", [])),
            inequalities=tuple(str(item) for item in value.get("inequalities", [])),
            thresholds=dict(value.get("thresholds", {})),
            policy_choices=dict(value.get("policy_choices", {})),
            graph_preconditions=dict(value.get("graph_preconditions", {})),
            predicted_telemetry_fields=_to_signatures(
                value.get("predicted_telemetry_fields", [])
            ),
            runtime_status=str(value["runtime_status"]),
            runtime_blockers=tuple(str(item) for item in value.get("runtime_blockers", [])),
            testable_with_current_runtime=bool(value.get("testable_with_current_runtime", False)),
            notes=str(value.get("notes", "")),
        )


@dataclass(frozen=True)
class GRC9MechanismLedger:
    entries: tuple[GRC9MechanismLedgerEntry, ...]
    ledger_version: str = GRC9_MECHANISM_LEDGER_VERSION

    def __post_init__(self) -> None:
        if self.ledger_version != GRC9_MECHANISM_LEDGER_VERSION:
            raise ValueError(f"ledger_version must be {GRC9_MECHANISM_LEDGER_VERSION!r}")
        ids = [entry.mechanism_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("mechanism ids must be unique")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "ledger_version": self.ledger_version,
            "entries": [entry.to_mapping() for entry in self.entries],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9MechanismLedger:
        return cls(
            ledger_version=str(value.get("ledger_version", GRC9_MECHANISM_LEDGER_VERSION)),
            entries=tuple(
                GRC9MechanismLedgerEntry.from_mapping(item)
                for item in value.get("entries", [])
            ),
        )

    def by_id(self) -> Mapping[str, GRC9MechanismLedgerEntry]:
        return {entry.mechanism_id: entry for entry in self.entries}

    def runtime_status_for(self, mechanism_id: str) -> str:
        return self.by_id()[mechanism_id].runtime_status


def hypothesis_runtime_status_matches_ledger(
    hypothesis: GRC9StructureHypothesis,
    ledger_entry: GRC9MechanismLedgerEntry,
) -> bool:
    """Return whether a hypothesis copied runtime status from its ledger entry."""

    return hypothesis.runtime_status == ledger_entry.runtime_status


def _paper(section: str, equation: str = "") -> GRC9SourceReference:
    return GRC9SourceReference(
        source="papers/2026-04-GRC-9.md",
        section=section,
        equation=equation,
    )


def _spec(section: str) -> GRC9SourceReference:
    return GRC9SourceReference(source="specs/grc-9-spec.md", section=section)


def _sig(field_path: str, predicate: str, expected_type: str) -> GRC9PredictedSignature:
    return GRC9PredictedSignature(
        field_path=field_path,
        predicate=predicate,
        expected_type=expected_type,
    )


def default_grc9_mechanism_ledger() -> GRC9MechanismLedger:
    """Return the initial GRC9 paper/spec mechanism ledger."""

    entries = (
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_spark_precursor",
            phenomenon="spark_precursor",
            paper_sources=(_paper("8.2 Spark criterion", "Eq. 12"), _paper("Appendix D.1")),
            spec_sources=(_spec("Spark rule"),),
            equations=("deg_act(s)=9", "Spark(s)=saturation and instability-or-column-proxy"),
            inequalities=("min_b |H_s^(b)| < epsilon_spark",),
            thresholds={"active_degree": 9, "spark_threshold": "epsilon_spark"},
            policy_choices={"near_saturation": "deferred", "sign_crossing": "history-dependent"},
            graph_preconditions={
                "requires_full_saturation": True,
                "requires_column_diagnostic": True,
                "requires_sink_candidate": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.port_chart.saturated_node_count", "> 0", "int"),
                _sig(
                    "family_extensions.grc9.column_diagnostic.column_proxy_candidate_count",
                    ">= 0",
                    "int",
                ),
                _sig("family_extensions.grc9.spark_evidence.saturation_gate_pass", "is true", "bool"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
            notes="Canonical spark seeds should rely on full saturation, not optional near-saturation.",
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_expansion_module",
            phenomenon="expansion_module",
            paper_sources=(_paper("8.3 Spark expansion", "Eq. 13-16"),),
            spec_sources=(_spec("Expansion policy parameters"),),
            equations=("n = max(4, ceil((D_eff - 2) / 7))", "sum_b p_b = 1"),
            inequalities=("D_eff >= 0",),
            thresholds={"target_effective_degree": "D_eff"},
            policy_choices={
                "expansion_distribution_mode": ("equal", "custom"),
                "bond_weight_mode": ("fixed", "column_geometric_mean", "custom"),
                "expansion_schedule": "instantaneous",
            },
            graph_preconditions={
                "requires_spark_event": True,
                "requires_parent_sink": True,
                "requires_external_boundary_edges": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.expansion_evidence.module_node_count", ">= 4", "int"),
                _sig(
                    "family_extensions.grc9.expansion_evidence.coherence_transfer_ratios_sum",
                    "close_to 1.0",
                    "float",
                ),
                _sig("family_extensions.grc9.expansion_evidence.internal_edge_count", ">= 3", "int"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_column_preserving_reassignment",
            phenomenon="column_preserving_reassignment",
            paper_sources=(_paper("8.3.3 Reassignment of the old boundary", "Eq. 15"),),
            spec_sources=(_spec("Mechanical expansion"),),
            equations=("old edge on port r maps to satellite s_b where b=column(r)",),
            inequalities=(),
            thresholds={},
            policy_choices={"tie_break": "deterministic column family reassignment"},
            graph_preconditions={
                "requires_boundary_edges_by_column": True,
                "requires_expansion_event": True,
            },
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9.expansion_evidence.reassigned_edge_count_by_column",
                    "matches seed column families",
                    "object",
                ),
                _sig("checkpoint.module_overlays", "present", "object"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_growth_pressure",
            phenomenon="growth_pressure",
            paper_sources=(_paper("8.4 Seed/front propagation", "Eq. 17"),),
            spec_sources=(_spec("Step order growth"),),
            equations=("p_birth(i)=1-exp(-lambda F_i^out)",),
            inequalities=("F_i^out >= 0", "0 <= p_birth <= 1"),
            thresholds={"birth_lambda": "lambda"},
            policy_choices={"parent_selection_mode": "outward_flux_parent_selection"},
            graph_preconditions={
                "requires_inactive_parent_port": True,
                "requires_outward_flux_gradient": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.growth_evidence.outward_flux_pressure", ">= 0", "float"),
                _sig("family_extensions.grc9.growth_evidence.birth_probability", "in [0,1]", "float"),
                _sig("family_extensions.grc9.growth_evidence.selected_parent_port", "present", "int"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_row_tensor_regime",
            phenomenon="row_tensor_regime",
            paper_sources=(_paper("2. Local coherence tensor", "Eq. 1"), _paper("Rows vs columns")),
            spec_sources=(_spec("Row tensor"),),
            equations=("K_i accumulates density, row mismatch, and flux feedback terms"),
            inequalities=(),
            thresholds={},
            policy_choices={"frame_mode": "fixed_port_chart"},
            graph_preconditions={
                "requires_controlled_row_occupancy": True,
                "requires_conductance_asymmetry": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.row_tensor.row_tensor_mean", "finite", "float"),
                _sig("family_extensions.grc9.row_tensor.row_tensor_anisotropy_max", ">= 0", "float"),
                _sig("family_extensions.grc9.row_tensor.row_mismatch_term_max", ">= 0", "float"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_column_diagnostic_regime",
            phenomenon="column_diagnostic_regime",
            paper_sources=(_paper("8.2 Spark criterion", "Eq. 11"),),
            spec_sources=(_spec("Spark rule"),),
            equations=("H_s^(b)=sum_a (-1)^(a+1) w_{s,a,b}(C_j-C_s)"),
            inequalities=("min_b |H_s^(b)| < epsilon_spark"),
            thresholds={"spark_threshold": "epsilon_spark"},
            policy_choices={"spark_threshold_mode": ("absolute", "calibrated_fraction")},
            graph_preconditions={
                "requires_controlled_column_profiles": True,
                "requires_column_conductance_variation": True,
            },
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9.column_diagnostic.column_diagnostic_min_abs",
                    "finite",
                    "float",
                ),
                _sig(
                    "family_extensions.grc9.column_diagnostic.column_profile_sparsity",
                    "in [0,1]",
                    "float",
                ),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_coarse_graining_roundtrip",
            phenomenon="coarse_graining_profile_sparsity",
            paper_sources=(_paper("9. Invertible column coarse-graining", "Eq. 20-22"), _paper("Appendix D.3")),
            spec_sources=(_spec("Column coarse graining"),),
            equations=("Split(G(X)) = X", "G(Split(bar X, pi)) = (bar X, pi)"),
            inequalities=("bar X_{i,b} >= 0", "pi_{i,.,b} in simplex"),
            thresholds={},
            policy_choices={"signed_flux_mode": ("signed_lossless", "signed_compressed")},
            graph_preconditions={
                "requires_column_fields": True,
                "requires_profile_sparsity_variation": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.coarse_graining.coarse_fields_list", "nonempty", "list"),
                _sig("family_extensions.grc9.coarse_graining.coarse_field_types", "present", "object"),
                _sig(
                    "family_extensions.grc9.coarse_graining.profile_compression_mode",
                    "present-or-missing_surface",
                    "string",
                ),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
            notes="Compressed storage itself remains diagnostic-only; round-trip fields are testable.",
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_budget_correction",
            phenomenon="budget_correction",
            paper_sources=(_paper("7. Global invariance", "Eq. 8-9"),),
            spec_sources=(_spec("Budget preservation"),),
            equations=("sum_i C_i = B", "C <- Proj_Delta_B(C)"),
            inequalities=("C_i >= 0 for simplex projection",),
            thresholds={"budget_error_tolerance": "runtime configured"},
            policy_choices={"budget_preservation_policy": ("uniform_shift", "simplex_projection")},
            graph_preconditions={
                "requires_budget_perturbation": True,
                "requires_budget_policy_config": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.budget_correction.budget_error", "near 0", "float"),
                _sig(
                    "family_extensions.grc9.budget_correction.last_budget_correction_path",
                    "present",
                    "string",
                ),
                _sig("family_extensions.grc9.budget_evidence.budget_error_before", "finite", "float"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_quiescent_basin",
            phenomenon="quiescent_basin",
            paper_sources=(_paper("8.1 Identities and abundance", "Eq. 10"),),
            spec_sources=(_spec("Diagnostics"),),
            equations=("successor map selects max positive outflow",),
            inequalities=("spark_count = 0", "growth_count = 0"),
            thresholds={"event_activity": 0},
            policy_choices={"control_role": "no_event_control"},
            graph_preconditions={
                "requires_balanced_conductance": True,
                "requires_no_saturation": True,
                "requires_low_outward_pressure": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.identity_abundance.sink_count", "stable", "int"),
                _sig("family_extensions.grc9.identity_abundance.basin_size_max", "stable", "int"),
                _sig("family_extensions.grc9.lifecycle_counts.spark_confirmed_count", "== 0", "int"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_transport_pathway",
            phenomenon="transport_pathway",
            paper_sources=(_paper("Reflexive loop and flux law", "Eq. 6-7"), _paper("Appendix I.4")),
            spec_sources=(_spec("Transport diagnostics"),),
            equations=("J_ij = -eta w_ij (Phi_i - Phi_j)",),
            inequalities=(),
            thresholds={},
            policy_choices={"edge_label_selection": "runtime configured"},
            graph_preconditions={
                "requires_asymmetric_conductance_paths": True,
                "requires_potential_gradient": True,
            },
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.transport.flux_abs_sum", ">= 0", "float"),
                _sig("family_extensions.grc9.transport.strongest_flux_edges_sample", "present", "list"),
                _sig("family_extensions.grc9.transport.label_availability", "present-or-missing_surface", "object"),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_identity_fission_persistence",
            phenomenon="fission_candidate",
            paper_sources=(_paper("Appendix E. Identity fission"),),
            spec_sources=(_spec("Identity basin diagnostics"),),
            equations=("|S^(k+t) intersection {s_A,s_B}| = 2 over persistence window",),
            inequalities=("basin_mass >= identity_fission_min_basin_mass",),
            thresholds={
                "identity_fission_persistence_delta": "seed/runtime configured",
                "identity_fission_min_basin_mass": "seed/runtime configured",
            },
            policy_choices={"fission_evaluator": "persistence_window"},
            graph_preconditions={
                "requires_post_expansion_two_sink_geometry": True,
                "requires_persistence_window": True,
            },
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9.expansion_summary.identity_fission_candidate_count",
                    ">= 0",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
                    ">= 0",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps",
                    ">= 0",
                    "int",
                ),
            ),
            runtime_status=RUNTIME_TESTABLE,
            testable_with_current_runtime=True,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_adiabatic_expansion",
            phenomenon="adiabatic_expansion",
            paper_sources=(_paper("8.3.5 Optional gradualization"),),
            spec_sources=(_spec("Expansion policy parameters"),),
            equations=("theta in [0,1] over tau_exp substeps",),
            inequalities=("tau_exp in [5,20] typical",),
            thresholds={"expansion_schedule_tau": "tau_exp"},
            policy_choices={"expansion_schedule": "adiabatic"},
            graph_preconditions={"requires_expansion_event": True},
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9.expansion_evidence.expansion_substeps", "> 1", "int"),
            ),
            runtime_status=RUNTIME_DEFERRED,
            runtime_blockers=("runtime currently treats expansion as instantaneous",),
            testable_with_current_runtime=False,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_boundary_barrier_ghost",
            phenomenon="boundary_barrier_ghost",
            paper_sources=(_paper("Appendix I.1 Boundary geometry"),),
            spec_sources=(_spec("Boundary behavior"),),
            equations=(),
            inequalities=(),
            thresholds={},
            policy_choices={"boundary_mode": ("barrier", "ghost")},
            graph_preconditions={"requires_low_coherence_boundary_support": True},
            predicted_telemetry_fields=(),
            runtime_status=RUNTIME_RESERVED_FUTURE,
            runtime_blockers=("boundary barrier and ghost modes are reserved future capabilities",),
            testable_with_current_runtime=False,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_ternary_identity_tree",
            phenomenon="ternary_identity_tree",
            paper_sources=(_paper("Appendix D.4 Ternary tree extraction"),),
            spec_sources=(_spec("Discrete multiscale extraction"),),
            equations=("column-restricted subgraphs produce up to three children",),
            inequalities=(),
            thresholds={},
            policy_choices={"tree_extraction": "visualization/extraction"},
            graph_preconditions={"requires_column_restricted_subgraph_extraction": True},
            predicted_telemetry_fields=(),
            runtime_status=RUNTIME_RESERVED_FUTURE,
            runtime_blockers=("ternary identity tree extraction is not implemented as runtime telemetry",),
            testable_with_current_runtime=False,
        ),
        GRC9MechanismLedgerEntry(
            mechanism_id="grc9_mech_lorentzian_observer_frc",
            phenomenon="lorentzian_observer_frc",
            paper_sources=(_paper("Appendix I.4-I.5"),),
            spec_sources=(_spec("Capability boundaries"),),
            equations=(),
            inequalities=(),
            thresholds={},
            policy_choices={"reserved_semantics": ("lorentzian", "observer", "frc_sigma")},
            graph_preconditions={},
            predicted_telemetry_fields=(),
            runtime_status=RUNTIME_OUT_OF_SCOPE,
            runtime_blockers=(
                "Lorentzian causal layer, observer-local views, and FRC sigma fields are outside core GRC9 discovery",
            ),
            testable_with_current_runtime=False,
        ),
    )
    return GRC9MechanismLedger(entries=entries)


__all__ = [
    "GRC9_MECHANISM_LEDGER_VERSION",
    "GRC9MechanismLedger",
    "GRC9MechanismLedgerEntry",
    "RUNTIME_DEFERRED",
    "RUNTIME_OUT_OF_SCOPE",
    "RUNTIME_RESERVED_FUTURE",
    "RUNTIME_TESTABLE",
    "default_grc9_mechanism_ledger",
    "hypothesis_runtime_status_matches_ledger",
]
