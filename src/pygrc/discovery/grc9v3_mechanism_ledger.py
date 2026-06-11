"""Mechanism ledger for GRC9V3 phenomenology discovery."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


GRC9V3_MECHANISM_LEDGER_VERSION = "grc9v3_phenomenology_mechanism_ledger_v1"

GRC9V3_RUNTIME_TESTABLE = "testable"
GRC9V3_RUNTIME_CAPABILITY_GATED = "capability_gated"
GRC9V3_RUNTIME_DEFERRED = "deferred"
GRC9V3_RUNTIME_OUT_OF_SCOPE = "out_of_scope"

GRC9V3_OWNERSHIP_GRC9_MECHANICAL = "grc9_mechanical"
GRC9V3_OWNERSHIP_GRCV3_SEMANTIC = "grcv3_semantic"
GRC9V3_OWNERSHIP_HYBRID = "grc9v3_hybrid"
GRC9V3_OWNERSHIP_SHARED_RUNTIME = "shared_runtime"

_RUNTIME_STATUSES = frozenset(
    {
        GRC9V3_RUNTIME_TESTABLE,
        GRC9V3_RUNTIME_CAPABILITY_GATED,
        GRC9V3_RUNTIME_DEFERRED,
        GRC9V3_RUNTIME_OUT_OF_SCOPE,
    }
)
_OWNERSHIPS = frozenset(
    {
        GRC9V3_OWNERSHIP_GRC9_MECHANICAL,
        GRC9V3_OWNERSHIP_GRCV3_SEMANTIC,
        GRC9V3_OWNERSHIP_HYBRID,
        GRC9V3_OWNERSHIP_SHARED_RUNTIME,
    }
)


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_token_sequence(values: Sequence[str], *, field_name: str) -> None:
    if not values:
        raise ValueError(f"{field_name} must not be empty")
    for index, value in enumerate(values):
        _require_non_empty(value, field_name=f"{field_name}[{index}]")


def _validate_runtime_status(value: str) -> None:
    if value not in _RUNTIME_STATUSES:
        raise ValueError(f"runtime_status must be one of {tuple(sorted(_RUNTIME_STATUSES))}")


def _validate_ownership(values: Sequence[str]) -> None:
    _validate_token_sequence(values, field_name="ownership")
    for value in values:
        if value not in _OWNERSHIPS:
            raise ValueError(f"ownership must contain only {tuple(sorted(_OWNERSHIPS))}")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


@dataclass(frozen=True)
class GRC9V3SourceReference:
    source: str
    section: str
    equation: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.source, field_name="source")
        _require_non_empty(self.section, field_name="section")

    def to_mapping(self) -> Mapping[str, Any]:
        return {"source": self.source, "section": self.section, "equation": self.equation}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3SourceReference:
        return cls(
            source=str(value["source"]),
            section=str(value["section"]),
            equation=str(value.get("equation", "")),
        )


@dataclass(frozen=True)
class GRC9V3PredictedSignature:
    field_path: str
    predicate: str
    expected_type: str

    def __post_init__(self) -> None:
        _require_non_empty(self.field_path, field_name="field_path")
        _require_non_empty(self.predicate, field_name="predicate")
        _require_non_empty(self.expected_type, field_name="expected_type")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "field_path": self.field_path,
            "predicate": self.predicate,
            "expected_type": self.expected_type,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3PredictedSignature:
        return cls(
            field_path=str(value["field_path"]),
            predicate=str(value["predicate"]),
            expected_type=str(value["expected_type"]),
        )


def _to_source_refs(
    values: Sequence[GRC9V3SourceReference | Mapping[str, Any]],
) -> tuple[GRC9V3SourceReference, ...]:
    return tuple(
        item
        if isinstance(item, GRC9V3SourceReference)
        else GRC9V3SourceReference.from_mapping(item)
        for item in values
    )


def _to_signatures(
    values: Sequence[GRC9V3PredictedSignature | Mapping[str, Any]],
) -> tuple[GRC9V3PredictedSignature, ...]:
    return tuple(
        item
        if isinstance(item, GRC9V3PredictedSignature)
        else GRC9V3PredictedSignature.from_mapping(item)
        for item in values
    )


@dataclass(frozen=True)
class GRC9V3MechanismLedgerEntry:
    mechanism_id: str
    phenomenon: str
    ownership: tuple[str, ...]
    phase7_sources: tuple[GRC9V3SourceReference, ...]
    parent_family_sources: tuple[GRC9V3SourceReference, ...]
    equations: tuple[str, ...]
    step_loop_refs: tuple[str, ...]
    thresholds: Mapping[str, Any]
    policy_choices: Mapping[str, Any]
    graph_preconditions: Mapping[str, Any]
    state_preconditions: Mapping[str, Any]
    parameter_knobs: tuple[str, ...]
    predicted_telemetry_fields: tuple[GRC9V3PredictedSignature, ...]
    predicted_event_sequence: tuple[str, ...]
    visual_evidence_surfaces: tuple[str, ...]
    runtime_status: str
    runtime_blockers: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.mechanism_id, field_name="mechanism_id")
        _require_non_empty(self.phenomenon, field_name="phenomenon")
        _validate_ownership(self.ownership)
        _validate_runtime_status(self.runtime_status)
        if not self.phase7_sources:
            raise ValueError("phase7_sources must not be empty")
        if not self.parent_family_sources:
            raise ValueError("parent_family_sources must not be empty")
        if self.runtime_status == GRC9V3_RUNTIME_TESTABLE:
            if not self.predicted_telemetry_fields:
                raise ValueError("testable mechanisms must map to telemetry fields")
            if self.runtime_blockers:
                raise ValueError("testable mechanisms cannot record runtime_blockers")
        else:
            if not self.runtime_blockers:
                raise ValueError("non-testable mechanisms must record runtime_blockers")
        if self.runtime_status == GRC9V3_RUNTIME_CAPABILITY_GATED:
            if not any("capability" in blocker for blocker in self.runtime_blockers):
                raise ValueError("capability-gated mechanisms must name a capability blocker")

    @property
    def testable_with_current_runtime(self) -> bool:
        return self.runtime_status == GRC9V3_RUNTIME_TESTABLE

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "phenomenon": self.phenomenon,
            "ownership": list(self.ownership),
            "phase7_sources": [item.to_mapping() for item in self.phase7_sources],
            "parent_family_sources": [
                item.to_mapping() for item in self.parent_family_sources
            ],
            "equations": list(self.equations),
            "step_loop_refs": list(self.step_loop_refs),
            "thresholds": _json_safe(self.thresholds),
            "policy_choices": _json_safe(self.policy_choices),
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "state_preconditions": _json_safe(self.state_preconditions),
            "parameter_knobs": list(self.parameter_knobs),
            "predicted_telemetry_fields": [
                item.to_mapping() for item in self.predicted_telemetry_fields
            ],
            "predicted_event_sequence": list(self.predicted_event_sequence),
            "visual_evidence_surfaces": list(self.visual_evidence_surfaces),
            "runtime_status": self.runtime_status,
            "runtime_blockers": list(self.runtime_blockers),
            "testable_with_current_runtime": self.testable_with_current_runtime,
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3MechanismLedgerEntry:
        return cls(
            mechanism_id=str(value["mechanism_id"]),
            phenomenon=str(value["phenomenon"]),
            ownership=tuple(str(item) for item in value.get("ownership", [])),
            phase7_sources=_to_source_refs(value.get("phase7_sources", [])),
            parent_family_sources=_to_source_refs(value.get("parent_family_sources", [])),
            equations=tuple(str(item) for item in value.get("equations", [])),
            step_loop_refs=tuple(str(item) for item in value.get("step_loop_refs", [])),
            thresholds=dict(value.get("thresholds", {})),
            policy_choices=dict(value.get("policy_choices", {})),
            graph_preconditions=dict(value.get("graph_preconditions", {})),
            state_preconditions=dict(value.get("state_preconditions", {})),
            parameter_knobs=tuple(str(item) for item in value.get("parameter_knobs", [])),
            predicted_telemetry_fields=_to_signatures(
                value.get("predicted_telemetry_fields", [])
            ),
            predicted_event_sequence=tuple(
                str(item) for item in value.get("predicted_event_sequence", [])
            ),
            visual_evidence_surfaces=tuple(
                str(item) for item in value.get("visual_evidence_surfaces", [])
            ),
            runtime_status=str(value["runtime_status"]),
            runtime_blockers=tuple(str(item) for item in value.get("runtime_blockers", [])),
            notes=str(value.get("notes", "")),
        )


@dataclass(frozen=True)
class GRC9V3MechanismLedger:
    entries: tuple[GRC9V3MechanismLedgerEntry, ...]
    ledger_version: str = GRC9V3_MECHANISM_LEDGER_VERSION

    def __post_init__(self) -> None:
        if self.ledger_version != GRC9V3_MECHANISM_LEDGER_VERSION:
            raise ValueError(
                f"ledger_version must be {GRC9V3_MECHANISM_LEDGER_VERSION!r}"
            )
        ids = [entry.mechanism_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("mechanism ids must be unique")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "ledger_version": self.ledger_version,
            "entries": [entry.to_mapping() for entry in self.entries],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3MechanismLedger:
        return cls(
            ledger_version=str(
                value.get("ledger_version", GRC9V3_MECHANISM_LEDGER_VERSION)
            ),
            entries=tuple(
                GRC9V3MechanismLedgerEntry.from_mapping(item)
                for item in value.get("entries", [])
            ),
        )

    def by_id(self) -> Mapping[str, GRC9V3MechanismLedgerEntry]:
        return {entry.mechanism_id: entry for entry in self.entries}

    def runtime_status_for(self, mechanism_id: str) -> str:
        return self.by_id()[mechanism_id].runtime_status


def hypothesis_runtime_status_matches_grc9v3_ledger(
    hypothesis: Mapping[str, Any],
    ledger_entry: GRC9V3MechanismLedgerEntry,
) -> bool:
    """Return whether a hypothesis copied runtime status from its ledger entry."""

    return str(hypothesis.get("runtime_status")) == ledger_entry.runtime_status


def _phase7(section: str, equation: str = "") -> GRC9V3SourceReference:
    return GRC9V3SourceReference(
        source="implementation/Phase-7-EquationMap.md",
        section=section,
        equation=equation,
    )


def _loop(step: str) -> GRC9V3SourceReference:
    return GRC9V3SourceReference(
        source="implementation/Phase-7-StepLoop.md",
        section=step,
    )


def _paper(section: str, equation: str = "") -> GRC9V3SourceReference:
    return GRC9V3SourceReference(
        source="papers/2026-04-GRC-9.md",
        section=section,
        equation=equation,
    )


def _spec(source: str, section: str, equation: str = "") -> GRC9V3SourceReference:
    return GRC9V3SourceReference(source=source, section=section, equation=equation)


def _sig(
    field_path: str,
    predicate: str,
    expected_type: str,
) -> GRC9V3PredictedSignature:
    return GRC9V3PredictedSignature(
        field_path=field_path,
        predicate=predicate,
        expected_type=expected_type,
    )


def _common_visuals(*extra: str) -> tuple[str, ...]:
    return (
        "behavior_trajectories",
        "event_timeline",
        "graph_sequence",
        *extra,
    )


def default_grc9v3_mechanism_ledger() -> GRC9V3MechanismLedger:
    """Return the initial Phase 7 GRC9V3 phenomenology mechanism ledger."""

    entries = (
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_hybrid_spark_gate",
            phenomenon="hybrid_spark_gate",
            ownership=(
                GRC9V3_OWNERSHIP_GRC9_MECHANICAL,
                GRC9V3_OWNERSHIP_GRCV3_SEMANTIC,
                GRC9V3_OWNERSHIP_HYBRID,
            ),
            phase7_sources=(
                _phase7("Operator Map: Hybrid spark candidate"),
                _loop("Step 13 detect_hybrid_spark_candidates"),
            ),
            parent_family_sources=(
                _paper("8.2 Spark criterion", "Eq. 12"),
                _paper("Appendix G: GRC-v3 lift", "Eq. G8"),
            ),
            equations=(
                "active_degree(candidate)=9",
                "Eq. G8: lambda_min(signed_hessian_row_basis) < epsilon_spark",
                "Eq. 12 fast proxy: min_b |H_s^(b)| < epsilon_spark",
                "candidate requires basin-interior evidence",
            ),
            step_loop_refs=("13 detect_hybrid_spark_candidates",),
            thresholds={"active_degree": 9, "epsilon_spark": "runtime configured"},
            policy_choices={"hessian_backend": ("row_basis_diagonal", "weighted_least_squares")},
            graph_preconditions={
                "requires_full_saturation": True,
                "requires_candidate_sink_or_basin_node": True,
            },
            state_preconditions={
                "requires_basin_interior_gate": True,
                "requires_signed_hessian_degeneracy": True,
            },
            parameter_knobs=(
                "epsilon_spark",
                "hessian_backend",
                "coherence_placement",
                "port_saturation_pattern",
            ),
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9v3.port_chart.saturated_node_count", "> 0", "int"),
                _sig(
                    "family_extensions.grc9v3.row_basis_differential.current_min_signed_hessian_min",
                    "< epsilon_spark",
                    "float",
                ),
                _sig(
                    "family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count",
                    "> 0",
                    "int",
                ),
            ),
            predicted_event_sequence=("hybrid_spark_candidate",),
            visual_evidence_surfaces=_common_visuals("node_overlay", "port_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Primary GRC9V3 gate is Appendix G Eq. G8. Eq. 12 column "
                "diagnostic remains a fast GRC9 proxy/fallback, not the same "
                "quantity as the row-basis signed Hessian."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_column_diagnostic_proxy",
            phenomenon="column_diagnostic_proxy",
            ownership=(GRC9V3_OWNERSHIP_GRC9_MECHANICAL, GRC9V3_OWNERSHIP_HYBRID),
            phase7_sources=(
                _phase7("Operator Map: Hybrid spark candidate"),
                _loop("Step 13 detect_hybrid_spark_candidates"),
            ),
            parent_family_sources=(
                _paper("8.2 Spark criterion", "Eq. 11"),
                _paper("8.2 Spark criterion", "Eq. 12"),
            ),
            equations=(
                "Eq. 11: H_s^(b) is the per-column curvature/coherence proxy",
                "Eq. 12: min_b |H_s^(b)| < epsilon_spark can trigger the fast proxy gate",
            ),
            step_loop_refs=("13 detect_hybrid_spark_candidates",),
            thresholds={"epsilon_spark": "runtime configured"},
            policy_choices={"column_proxy_role": "fast GRC9 proxy for spark evidence"},
            graph_preconditions={
                "requires_column_family_edges": True,
                "requires_controlled_column_coherence_difference": True,
            },
            state_preconditions={"requires_column_proxy_diagnostic_surface": True},
            parameter_knobs=("target_column", "column_conductance", "column_coherence_gradient"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.hybrid_tensor.row_mismatch_sum_max",
                    "indirect magnitude proxy for the designed column imbalance",
                    "float",
                ),
                _sig(
                    "family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max",
                    "indirect anisotropy proxy for the designed column imbalance",
                    "float",
                ),
                _sig(
                    "family_extensions.grc9v3.port_chart.column_occupancy_totals",
                    "target column family present",
                    "mapping",
                ),
            ),
            predicted_event_sequence=("hybrid_spark_candidate",),
            visual_evidence_surfaces=_common_visuals("node_overlay", "port_overlay"),
            runtime_status=GRC9V3_RUNTIME_CAPABILITY_GATED,
            runtime_blockers=(
                "capability direct per-column H_s^(b) telemetry is required for standalone column-diagnostic motifs",
            ),
            notes=(
                "Standalone ledger entry for the paper Eq. 11 per-column "
                "diagnostic H_s^(b). Current GRC9V3 telemetry exposes the "
                "effect through hybrid spark and tensor surfaces rather than a "
                "dedicated column-diagnostic group, so this mechanism is not "
                "accepted as directly testable yet."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_spark_to_expansion",
            phenomenon="spark_to_expansion",
            ownership=(GRC9V3_OWNERSHIP_GRC9_MECHANICAL, GRC9V3_OWNERSHIP_HYBRID),
            phase7_sources=(
                _phase7("Operator Map: Mechanical expansion"),
                _loop("Step 14 apply_mechanical_expansion"),
            ),
            parent_family_sources=(
                _paper("8.3 Spark expansion", "Eq. 13-16"),
                _spec("specs/grc-v3-spec.md", "Hierarchy after refinement"),
            ),
            equations=("Eq. 13: n=ceil((D_eff - 2) / 7)", "sum distribution_weights=1"),
            step_loop_refs=(
                "14 apply_mechanical_expansion",
                "15 refresh_after_expansion",
            ),
            thresholds={"target_effective_degree": "D_eff"},
            policy_choices={"expansion_distribution_mode": ("equal", "custom")},
            graph_preconditions={
                "requires_hybrid_spark_candidate": True,
                "requires_external_port_capacity": True,
            },
            state_preconditions={"requires_fixed_budget_target": True},
            parameter_knobs=(
                "target_effective_degree",
                "expansion_distribution_mode",
                "distribution_weights",
            ),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.event_domain",
                    "expansion on event row",
                    "string",
                ),
                _sig(
                    "family_extensions.grc9v3.expansion_evidence.requested_node_count",
                    ">= 4",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9v3.budget_correction.budget_error",
                    "finite",
                    "float",
                ),
            ),
            predicted_event_sequence=("hybrid_spark_candidate", "hybrid_mechanical_expansion"),
            visual_evidence_surfaces=_common_visuals("module_overlay", "edge_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "The paper formula is Eq. 13 without a max(4, ...) floor. "
                "Any canonical core-plus-three-satellites minimum is an "
                "implementation/module-shape convention, not the paper equation."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_appendix_e_cell_division",
            phenomenon="appendix_e_cell_division",
            ownership=(GRC9V3_OWNERSHIP_HYBRID, GRC9V3_OWNERSHIP_GRCV3_SEMANTIC),
            phase7_sources=(
                _phase7("Operator Map: Completed hybrid spark"),
                _loop("Steps 16-18 child stabilization and hierarchy"),
            ),
            parent_family_sources=(
                _paper("Appendix E: Identity fission / cell division"),
                _spec("specs/grc-v3-spec.md", "Hierarchy update"),
            ),
            equations=(
                "completed_spark requires child-basin stabilization",
                "hierarchy(parent) includes stabilized children",
            ),
            step_loop_refs=(
                "16 evaluate_child_basin_stabilization",
                "17 register_completed_hybrid_sparks",
                "18 update_hierarchy",
            ),
            thresholds={"daughter_sink_count": ">= 2"},
            policy_choices={"fixture": "appendix_e_cell_division"},
            graph_preconditions={"requires_post_expansion_module": True},
            state_preconditions={"requires_two_stabilized_child_sinks": True},
            parameter_knobs=("child_stabilization_threshold", "module_basin_mass"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.hybrid_spark_state.completed_hybrid_spark_count",
                    "> 0",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9v3.representative_appendix_e_summary.daughter_sink_count",
                    ">= 2",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9v3.hierarchy_state.max_hierarchy_depth",
                    "> 0",
                    "int",
                ),
            ),
            predicted_event_sequence=(
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
            ),
            visual_evidence_surfaces=_common_visuals("module_overlay", "choice_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Representative runtime fixture for the Appendix E cell-division "
                "pattern: mechanical expansion must be followed by child-basin "
                "stabilization before hierarchy is claimed."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_choice_collapse",
            phenomenon="choice_collapse",
            ownership=(GRC9V3_OWNERSHIP_GRCV3_SEMANTIC,),
            phase7_sources=(
                _phase7("Operator Map: Choice detection"),
                _loop("Step 19 update_choice_collapse_learning"),
            ),
            parent_family_sources=(
                _spec("specs/grc-v3-spec.md", "Choice/collapse semantics"),
                _spec("specs/grc-9-v3-spec.md", "Choice over GRC9 port-flux successors"),
            ),
            equations=("compatibility score separation > epsilon_choice",),
            step_loop_refs=("19 update_choice_collapse_learning",),
            thresholds={"epsilon_choice": "runtime configured", "epsilon_collapse": "runtime configured"},
            policy_choices={"choice_backend": "deterministic baseline"},
            graph_preconditions={"requires_competing_successor_basins": True},
            state_preconditions={"requires_choice_registry_surface": True},
            parameter_knobs=("epsilon_choice", "epsilon_collapse", "compatibility_gap"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.choice_collapse.choice_regime_count",
                    "> 0",
                    "int",
                ),
                _sig(
                    "family_extensions.grc9v3.choice_collapse.collapse_registry_count",
                    ">= 0",
                    "int",
                ),
            ),
            predicted_event_sequence=("choice_detected", "collapse"),
            visual_evidence_surfaces=_common_visuals("choice_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Choice/collapse is inherited semantic logic evaluated over the "
                "settled GRC9 port-flux successor landscape."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_growth_pressure",
            phenomenon="growth_pressure",
            ownership=(
                GRC9V3_OWNERSHIP_GRC9_MECHANICAL,
                GRC9V3_OWNERSHIP_GRCV3_SEMANTIC,
            ),
            phase7_sources=(
                _phase7("Operator Map: Boundary behavior"),
                _loop("Step 20 apply_growth"),
            ),
            parent_family_sources=(
                _paper("8.4 Growth rule"),
                _spec("specs/grc-9-v3-spec.md", "Hybrid growth state"),
            ),
            equations=("p_birth = 1 - exp(-lambda_birth * outward_flux_pressure)",),
            step_loop_refs=("20 apply_growth",),
            thresholds={"lambda_birth": "runtime configured"},
            policy_choices={"birth_rule_mode": "outward_flux_pressure"},
            graph_preconditions={"requires_inactive_parent_port": True},
            state_preconditions={"requires_growth_enabled": True},
            parameter_knobs=("lambda_birth", "outward_flux_pressure", "inactive_port"),
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9v3.growth_state.growth_event_count", "> 0", "int"),
                _sig(
                    "family_extensions.grc9v3.growth_state.last_birth_probability",
                    "> 0",
                    "float",
                ),
            ),
            predicted_event_sequence=("growth",),
            visual_evidence_surfaces=_common_visuals("port_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Growth is a GRC9 port mutation driven by outward pressure, "
                "while attached nodes must carry GRC9V3 semantic state."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_quadrature_budget_preservation",
            phenomenon="quadrature_budget_preservation",
            ownership=(GRC9V3_OWNERSHIP_GRCV3_SEMANTIC,),
            phase7_sources=(
                _phase7("Operator Map: Quadrature budget"),
                _loop("Step 23 enforce_quadrature_budget"),
            ),
            parent_family_sources=(
                _spec("specs/grc-v3-spec.md", "Quadrature budget"),
                _spec("specs/grc-9-v3-spec.md", "Budget on GRC9 values"),
            ),
            equations=("B=sum_i mu_i*C_i",),
            step_loop_refs=("23 enforce_quadrature_budget",),
            thresholds={"budget_error_tolerance": "runtime configured"},
            policy_choices={"budget_correction_method": ("uniform_shift", "simplex_projection")},
            graph_preconditions={"may_follow_topology_change": True},
            state_preconditions={"requires_budget_target": True},
            parameter_knobs=("quadrature_mode", "budget_correction_method", "budget_target"),
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9v3.budget_correction.budget_error", "finite", "float"),
                _sig(
                    "family_extensions.grc9v3.budget_correction.budget_correction_method",
                    "non_empty",
                    "string",
                ),
            ),
            predicted_event_sequence=("budget",),
            visual_evidence_surfaces=("report_panel", "trajectory_panel"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Budget is interpreted semantically as a quadrature invariant "
                "over GRC9V3 node coherence, including after topology changes."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_hessian_backend_comparison",
            phenomenon="hessian_backend_comparison",
            ownership=(GRC9V3_OWNERSHIP_GRCV3_SEMANTIC, GRC9V3_OWNERSHIP_HYBRID),
            phase7_sources=(
                _phase7("Hessian Backend Rule", "Eq. G3"),
                _loop("Step 2 compute_signed_hessian_row_basis_pre_flux"),
            ),
            parent_family_sources=(
                _paper("Appendix G: Row-basis Hessian", "Eq. G3"),
                _spec("specs/grc-v3-spec.md", "Appendix A weighted least-squares Hessian"),
            ),
            equations=(
                "row_basis_diagonal is the baseline Eq. G3 backend",
                "weighted_least_squares is a comparison backend",
            ),
            step_loop_refs=("2 compute_signed_hessian_row_basis_pre_flux",),
            thresholds={"backend_difference": "selector configured"},
            policy_choices={"hessian_backend": ("row_basis_diagonal", "weighted_least_squares")},
            graph_preconditions={"requires_same_graph_pair": True},
            state_preconditions={"requires_paired_backend_runs": True},
            parameter_knobs=("hessian_backend", "coherence_placement", "edge_geometry"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.row_basis_differential.hessian_backend",
                    "changes across pair",
                    "string",
                ),
                _sig(
                    "family_extensions.grc9v3.row_basis_differential.weighted_least_squares_hessian_available",
                    "true for WLS pair",
                    "bool",
                ),
            ),
            predicted_event_sequence=(),
            visual_evidence_surfaces=("comparison_panel", "trajectory_panel"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Row-basis diagonal Hessian is the Appendix G baseline. "
                "Weighted least squares is a comparison backend from GRCV3, "
                "not the default GRC9V3 equation."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_transport_basin_rerouting",
            phenomenon="transport_basin_rerouting",
            ownership=(GRC9V3_OWNERSHIP_GRC9_MECHANICAL, GRC9V3_OWNERSHIP_HYBRID),
            phase7_sources=(
                _phase7("Operator Map: Flux-topology sinks/basins"),
                _loop("Steps 8-12 flux, identities, basin validation"),
            ),
            parent_family_sources=(
                _spec("specs/grc-9-spec.md", "Port graph transport"),
                _spec("specs/grc-v3-spec.md", "Identity basin validation"),
            ),
            equations=("successor(i)=argmax positive flux", "basins follow successor map"),
            step_loop_refs=(
                "8 compute_flux",
                "11 detect_flux_topology_identities",
                "12 validate_geometric_basin_seeds",
            ),
            thresholds={"flux_gap": "selector configured"},
            policy_choices={"edge_label_selection": "all"},
            graph_preconditions={"requires_competing_flux_paths": True},
            state_preconditions={"requires_identity_refresh": True},
            parameter_knobs=("base_conductance", "coherence_gradient", "edge_labels"),
            predicted_telemetry_fields=(
                _sig("family_extensions.grc9v3.transport.flux_abs_sum", "> 0", "float"),
                _sig("family_extensions.grc9v3.identity_basin.sink_count", ">= 1", "int"),
                _sig("family_extensions.grc9v3.identity_basin.basin_count", ">= 1", "int"),
            ),
            predicted_event_sequence=(),
            visual_evidence_surfaces=_common_visuals("edge_overlay"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Transport/basin rerouting tests how GRC9 flux topology and "
                "GRCV3-style basin validation interact on the same port graph."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_coarse_cache_invalidation",
            phenomenon="coarse_cache_invalidation",
            ownership=(GRC9V3_OWNERSHIP_SHARED_RUNTIME,),
            phase7_sources=(
                _phase7("Operator Map: Column coarse-graining"),
                _loop("Step 25 refresh_or_invalidate_coarse_cache"),
            ),
            parent_family_sources=(
                _spec("specs/grc-9-spec.md", "Column coarse-graining"),
                _spec("specs/grc-9-v3-spec.md", "Hybrid cache hygiene"),
            ),
            equations=("topology_or_value_change invalidates derived coarse cache",),
            step_loop_refs=("25 refresh_or_invalidate_coarse_cache",),
            thresholds={},
            policy_choices={"coarse_cache_refresh_mode": "optional"},
            graph_preconditions={"requires_topology_or_value_mutation": True},
            state_preconditions={"requires_coarse_cache_surface": True},
            parameter_knobs=("coarse_cache_state", "mutation_kind"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.coarse_cache.coarse_cache_state",
                    "non_empty",
                    "string",
                ),
                _sig(
                    "family_extensions.grc9v3.coarse_cache.coarse_cache_invalidated",
                    "is bool",
                    "bool",
                ),
                _sig(
                    "family_extensions.grc9v3.coarse_cache.coarse_cache_invalidation_reason",
                    "primary invalidation signal when invalidated",
                    "string",
                ),
            ),
            predicted_event_sequence=("coarse",),
            visual_evidence_surfaces=("report_panel",),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "The invalidation reason is the primary Phase T-GRC9V3 signal; "
                "state and boolean invalidation alone are insufficient."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_quiescent_hybrid_control",
            phenomenon="quiescent_hybrid_control",
            ownership=(GRC9V3_OWNERSHIP_HYBRID,),
            phase7_sources=(_loop("Full canonical Phase 7 step order"),),
            parent_family_sources=(
                _spec("specs/grc-9-spec.md", "Stable port graph control"),
                _spec("specs/grc-v3-spec.md", "Stable basin control"),
            ),
            equations=("no lifecycle gate crosses threshold",),
            step_loop_refs=("1-26 full step loop",),
            thresholds={"all_event_thresholds": "below trigger"},
            policy_choices={"run_role": "no_event_control"},
            graph_preconditions={"requires_no_full_saturation": True, "requires_low_outward_pressure": True},
            state_preconditions={"requires_no_signed_hessian_degeneracy": True},
            parameter_knobs=("active_degree", "signed_hessian_min", "outward_flux_pressure"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count",
                    "== 0",
                    "int",
                ),
                _sig("family_extensions.grc9v3.growth_state.growth_event_count", "== 0", "int"),
            ),
            predicted_event_sequence=(),
            visual_evidence_surfaces=("trajectory_panel", "report_panel"),
            runtime_status=GRC9V3_RUNTIME_TESTABLE,
            notes=(
                "Negative-control mechanism for proving that stable hybrid "
                "runtime structures do not cross lifecycle thresholds."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_signed_crossing_spark",
            phenomenon="signed_crossing_spark",
            ownership=(GRC9V3_OWNERSHIP_GRCV3_SEMANTIC, GRC9V3_OWNERSHIP_HYBRID),
            phase7_sources=(
                _phase7("Optional capability-gated surfaces"),
                _loop("Step 13 optional signed-crossing gate"),
            ),
            parent_family_sources=(
                _paper("8.2 Spark criterion", "Eq. 12 optional signed criterion"),
                _paper("Appendix G: GRC-v3 lift", "Eq. G8"),
            ),
            equations=("H_s^(b)(k) * H_s^(b)(k-1) < 0 for some column b",),
            step_loop_refs=("13 detect_hybrid_spark_candidates",),
            thresholds={"sign_crossing": "strict sign change"},
            policy_choices={"spark_signed_crossing": True},
            graph_preconditions={"requires_full_saturation": True},
            state_preconditions={"requires_previous_column_diagnostic_history": True},
            parameter_knobs=("spark_signed_crossing", "previous_column_diagnostic"),
            predicted_telemetry_fields=(
                _sig(
                    "family_extensions.grc9v3.row_basis_differential.previous_min_signed_hessian_available",
                    "is true",
                    "bool",
                ),
                _sig(
                    "family_extensions.grc9v3.hybrid_spark_state.signed_crossing_status",
                    "available",
                    "string/object",
                ),
            ),
            predicted_event_sequence=("hybrid_spark_candidate",),
            visual_evidence_surfaces=("trajectory_panel", "event_timeline"),
            runtime_status=GRC9V3_RUNTIME_CAPABILITY_GATED,
            runtime_blockers=("capability spark_signed_crossing must be enabled and history-backed",),
            notes=(
                "The paper criterion is per-column H_s^(b), not a global "
                "signed-Hessian minimum. Current telemetry only exposes the "
                "capability/status surface, so accepted motifs must wait for "
                "history-backed column diagnostic evidence."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_boundary_barrier_ghost",
            phenomenon="boundary_barrier_ghost",
            ownership=(GRC9V3_OWNERSHIP_SHARED_RUNTIME, GRC9V3_OWNERSHIP_GRC9_MECHANICAL),
            phase7_sources=(
                _phase7("Backend And Config Surface"),
                _loop("Step 21 apply_boundary_behavior"),
            ),
            parent_family_sources=(
                _spec("specs/grc-9-spec.md", "Boundary modes"),
                _spec("specs/grc-9-v3-spec.md", "Boundary capability contract"),
            ),
            equations=("boundary_mode in {barrier, ghost} requires boundary_barrier capability",),
            step_loop_refs=("21 apply_boundary_behavior",),
            thresholds={},
            policy_choices={"boundary_mode": ("barrier", "ghost")},
            graph_preconditions={"requires_boundary_edges": True},
            state_preconditions={"requires_boundary_barrier_capability": True},
            parameter_knobs=("boundary_mode",),
            predicted_telemetry_fields=(),
            predicted_event_sequence=("boundary",),
            visual_evidence_surfaces=("graph_sequence",),
            runtime_status=GRC9V3_RUNTIME_CAPABILITY_GATED,
            runtime_blockers=("capability boundary_barrier is reserved until runtime support exists",),
            notes=(
                "Barrier and ghost boundary modes are preserved as future "
                "mechanisms but cannot be promoted to motifs until the runtime "
                "claims boundary_barrier capability."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_source_language_lowering",
            phenomenon="source_language_lowering",
            ownership=(GRC9V3_OWNERSHIP_SHARED_RUNTIME,),
            phase7_sources=(
                GRC9V3SourceReference(
                    source="implementation/GRC9V3-PhenomenologyDiscovery-Plan.md",
                    section="Iteration 10: Source-Language Handoff",
                ),
            ),
            parent_family_sources=(
                _spec("specs/grc-9-v3-spec.md", "Source lowering deferred"),
                _spec("specs/grc-v3-spec.md", "Source/runtime boundary"),
            ),
            equations=("runtime motif catalog precedes source claim",),
            step_loop_refs=(),
            thresholds={},
            policy_choices={"source_language": "deferred"},
            graph_preconditions={"requires_reviewed_runtime_motif": True},
            state_preconditions={},
            parameter_knobs=(),
            predicted_telemetry_fields=(),
            predicted_event_sequence=(),
            visual_evidence_surfaces=(),
            runtime_status=GRC9V3_RUNTIME_DEFERRED,
            runtime_blockers=("requires reviewed GRC9V3 runtime motif catalog first",),
            notes=(
                "Source-language work is intentionally downstream of reviewed "
                "pure-runtime GRC9V3 motifs."
            ),
        ),
        GRC9V3MechanismLedgerEntry(
            mechanism_id="grc9v3_mech_lorentzian_observer_layer",
            phenomenon="lorentzian_observer_layer",
            ownership=(GRC9V3_OWNERSHIP_SHARED_RUNTIME,),
            phase7_sources=(
                GRC9V3SourceReference(
                    source="implementation/GRC9V3-PhenomenologyDiscovery-Plan.md",
                    section="Boundaries",
                ),
            ),
            parent_family_sources=(
                _spec("specs/grc-9-v3-spec.md", "Non-claims"),
                _spec("specs/grc-9-spec.md", "Analytic labels are not Lorentzian time"),
            ),
            equations=("temporal_delay is an analytic label, not proper time",),
            step_loop_refs=(),
            thresholds={},
            policy_choices={"observer_local_views": "out_of_scope"},
            graph_preconditions={},
            state_preconditions={},
            parameter_knobs=(),
            predicted_telemetry_fields=(),
            predicted_event_sequence=(),
            visual_evidence_surfaces=(),
            runtime_status=GRC9V3_RUNTIME_OUT_OF_SCOPE,
            runtime_blockers=(
                "Lorentzian and observer-local semantics are outside GRC9V3 phenomenology discovery",
            ),
            notes=(
                "Temporal-delay labels remain analytic runtime labels here; "
                "they do not license Lorentzian or observer-local claims."
            ),
        ),
    )
    return GRC9V3MechanismLedger(entries=entries)


__all__ = [
    "GRC9V3_MECHANISM_LEDGER_VERSION",
    "GRC9V3_RUNTIME_CAPABILITY_GATED",
    "GRC9V3_RUNTIME_DEFERRED",
    "GRC9V3_RUNTIME_OUT_OF_SCOPE",
    "GRC9V3_RUNTIME_TESTABLE",
    "GRC9V3_OWNERSHIP_GRC9_MECHANICAL",
    "GRC9V3_OWNERSHIP_GRCV3_SEMANTIC",
    "GRC9V3_OWNERSHIP_HYBRID",
    "GRC9V3_OWNERSHIP_SHARED_RUNTIME",
    "GRC9V3MechanismLedger",
    "GRC9V3MechanismLedgerEntry",
    "GRC9V3PredictedSignature",
    "GRC9V3SourceReference",
    "default_grc9v3_mechanism_ledger",
    "hypothesis_runtime_status_matches_grc9v3_ledger",
]
