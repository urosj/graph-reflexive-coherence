"""Seeded structure hypothesis catalog for GRC9 phenomenology discovery."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

from .grc9_manifest import (
    GRC9PredictedSignature,
    GRC9StructureHypothesis,
    generated_lane_name,
    is_generated_lane_name,
    profile_name,
)
from .grc9_mechanism_ledger import (
    GRC9MechanismLedger,
    GRC9MechanismLedgerEntry,
    RUNTIME_TESTABLE,
    default_grc9_mechanism_ledger,
)


GRC9_HYPOTHESIS_CATALOG_VERSION = "grc9_hypothesis_catalog_v1"
_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def _require_sequence(value: Any, *, field_name: str) -> Sequence[Any]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence")
    return value


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


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
class GRC9SeedControlSpec:
    control_role: str
    seed_name: str
    parameter_overrides: Mapping[str, Any]
    expected_outcome: str
    scheduled_for_generation: bool = True

    def __post_init__(self) -> None:
        _require_non_empty(self.seed_name, field_name="seed_name")
        generated_lane_name("validation_probe", self.control_role)
        _require_mapping(self.parameter_overrides, field_name="parameter_overrides")
        _require_non_empty(self.expected_outcome, field_name="expected_outcome")
        if not isinstance(self.scheduled_for_generation, bool):
            raise ValueError("scheduled_for_generation must be a boolean")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "control_role": self.control_role,
            "seed_name": self.seed_name,
            "parameter_overrides": _json_safe(self.parameter_overrides),
            "expected_outcome": self.expected_outcome,
            "scheduled_for_generation": self.scheduled_for_generation,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9SeedControlSpec:
        mapping = _require_mapping(value, field_name="seed_control")
        return cls(
            control_role=str(mapping["control_role"]),
            seed_name=str(mapping["seed_name"]),
            parameter_overrides=dict(mapping.get("parameter_overrides", {})),
            expected_outcome=str(mapping["expected_outcome"]),
            scheduled_for_generation=bool(mapping.get("scheduled_for_generation", True)),
        )


@dataclass(frozen=True)
class GRC9PerturbationSpec:
    parameter: str
    deltas: tuple[str, ...]
    parent_control_role: str = "positive_control"

    def __post_init__(self) -> None:
        _require_non_empty(self.parameter, field_name="parameter")
        if not self.deltas:
            raise ValueError("deltas must not be empty")
        generated_lane_name("validation_probe", self.parent_control_role)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "parameter": self.parameter,
            "deltas": list(self.deltas),
            "parent_control_role": self.parent_control_role,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9PerturbationSpec:
        mapping = _require_mapping(value, field_name="perturbation")
        return cls(
            parameter=str(mapping["parameter"]),
            deltas=tuple(str(item) for item in _require_sequence(mapping.get("deltas", ()), field_name="deltas")),
            parent_control_role=str(mapping.get("parent_control_role", "positive_control")),
        )


@dataclass(frozen=True)
class GRC9SeedFamilySpec:
    mechanism_id: str
    hypothesis_id: str
    phenomenon: str
    seed_family: str
    profile_version: int
    node_count: int | str
    row_column_occupancy: Mapping[str, Any]
    active_inactive_port_pattern: Mapping[str, Any]
    conductance_assignment: Mapping[str, Any]
    coherence_placement: Mapping[str, Any]
    boundary_edge_pattern: Mapping[str, Any]
    expected_lifecycle: tuple[str, ...]
    positive_controls: tuple[GRC9SeedControlSpec, ...]
    negative_controls: tuple[GRC9SeedControlSpec, ...]
    perturbations: tuple[GRC9PerturbationSpec, ...]
    predicted_signatures: tuple[GRC9PredictedSignature, ...]
    runtime_status: str
    scheduled_for_generation: bool

    def __post_init__(self) -> None:
        _require_non_empty(self.mechanism_id, field_name="mechanism_id")
        if not isinstance(self.hypothesis_id, str) or not _TOKEN_RE.fullmatch(self.hypothesis_id):
            raise ValueError("hypothesis_id must use lowercase snake_case")
        _require_non_empty(self.phenomenon, field_name="phenomenon")
        _require_non_empty(self.seed_family, field_name="seed_family")
        profile_name(self.phenomenon, self.profile_version)
        generated_lane_name(self.seed_family, "positive_control")
        if isinstance(self.node_count, bool) or not isinstance(self.node_count, int | str):
            raise ValueError("node_count must be an integer or descriptive string")
        if isinstance(self.node_count, int) and self.node_count <= 0:
            raise ValueError("node_count must be positive")
        for field_name in (
            "row_column_occupancy",
            "active_inactive_port_pattern",
            "conductance_assignment",
            "coherence_placement",
            "boundary_edge_pattern",
        ):
            _require_mapping(getattr(self, field_name), field_name=field_name)
        if not self.expected_lifecycle:
            raise ValueError("expected_lifecycle must not be empty")
        if self.runtime_status == RUNTIME_TESTABLE and not (
            self.positive_controls or self.negative_controls
        ):
            raise ValueError("testable seed families need at least one control")
        if self.runtime_status == RUNTIME_TESTABLE and not self.predicted_signatures:
            raise ValueError("testable seed families need predicted signatures")
        if self.runtime_status != RUNTIME_TESTABLE and self.scheduled_for_generation:
            raise ValueError("non-testable seed families cannot be scheduled")

    @property
    def profile(self) -> str:
        return profile_name(self.phenomenon, self.profile_version)

    @property
    def lanes(self) -> tuple[str, ...]:
        return tuple(
            generated_lane_name(self.seed_family, control.control_role)
            for control in (*self.positive_controls, *self.negative_controls)
        )

    def to_structure_hypothesis(
        self,
        ledger_entry: GRC9MechanismLedgerEntry,
    ) -> GRC9StructureHypothesis:
        if ledger_entry.mechanism_id != self.mechanism_id:
            raise ValueError("ledger_entry does not match seed family mechanism_id")
        if ledger_entry.runtime_status != self.runtime_status:
            raise ValueError("seed family runtime_status must copy the ledger entry")
        return GRC9StructureHypothesis(
            hypothesis_id=self.hypothesis_id,
            target_phenomenon=self.phenomenon,
            runtime_status=self.runtime_status,
            paper_sources=ledger_entry.paper_sources,
            graph_preconditions=dict(ledger_entry.graph_preconditions),
            seed_family=self.seed_family,
            seed_parameters={
                "node_count": self.node_count,
                "row_column_occupancy": dict(self.row_column_occupancy),
                "active_inactive_port_pattern": dict(self.active_inactive_port_pattern),
                "conductance_assignment": dict(self.conductance_assignment),
                "coherence_placement": dict(self.coherence_placement),
                "boundary_edge_pattern": dict(self.boundary_edge_pattern),
                "expected_lifecycle": list(self.expected_lifecycle),
                "positive_controls": [
                    item.to_mapping() for item in self.positive_controls
                ],
                "negative_controls": [
                    item.to_mapping() for item in self.negative_controls
                ],
                "perturbations": [item.to_mapping() for item in self.perturbations],
                "scheduled_for_generation": self.scheduled_for_generation,
            },
            generator="generate_grc9_seed",
            predicted_signatures=self.predicted_signatures,
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "hypothesis_id": self.hypothesis_id,
            "phenomenon": self.phenomenon,
            "seed_family": self.seed_family,
            "profile": self.profile,
            "profile_version": self.profile_version,
            "node_count": self.node_count,
            "row_column_occupancy": _json_safe(self.row_column_occupancy),
            "active_inactive_port_pattern": _json_safe(self.active_inactive_port_pattern),
            "conductance_assignment": _json_safe(self.conductance_assignment),
            "coherence_placement": _json_safe(self.coherence_placement),
            "boundary_edge_pattern": _json_safe(self.boundary_edge_pattern),
            "expected_lifecycle": list(self.expected_lifecycle),
            "positive_controls": [item.to_mapping() for item in self.positive_controls],
            "negative_controls": [item.to_mapping() for item in self.negative_controls],
            "perturbations": [item.to_mapping() for item in self.perturbations],
            "predicted_signatures": [
                item.to_mapping() for item in self.predicted_signatures
            ],
            "runtime_status": self.runtime_status,
            "scheduled_for_generation": self.scheduled_for_generation,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9SeedFamilySpec:
        mapping = _require_mapping(value, field_name="seed_family")
        return cls(
            mechanism_id=str(mapping["mechanism_id"]),
            hypothesis_id=str(mapping["hypothesis_id"]),
            phenomenon=str(mapping["phenomenon"]),
            seed_family=str(mapping["seed_family"]),
            profile_version=int(mapping.get("profile_version", 1)),
            node_count=mapping["node_count"],
            row_column_occupancy=dict(mapping["row_column_occupancy"]),
            active_inactive_port_pattern=dict(mapping["active_inactive_port_pattern"]),
            conductance_assignment=dict(mapping["conductance_assignment"]),
            coherence_placement=dict(mapping["coherence_placement"]),
            boundary_edge_pattern=dict(mapping["boundary_edge_pattern"]),
            expected_lifecycle=tuple(str(item) for item in mapping["expected_lifecycle"]),
            positive_controls=tuple(
                GRC9SeedControlSpec.from_mapping(item)
                for item in mapping.get("positive_controls", [])
            ),
            negative_controls=tuple(
                GRC9SeedControlSpec.from_mapping(item)
                for item in mapping.get("negative_controls", [])
            ),
            perturbations=tuple(
                GRC9PerturbationSpec.from_mapping(item)
                for item in mapping.get("perturbations", [])
            ),
            predicted_signatures=_to_signatures(mapping.get("predicted_signatures", [])),
            runtime_status=str(mapping["runtime_status"]),
            scheduled_for_generation=bool(mapping.get("scheduled_for_generation", False)),
        )


@dataclass(frozen=True)
class GRC9HypothesisCatalog:
    seed_families: tuple[GRC9SeedFamilySpec, ...]
    catalog_version: str = GRC9_HYPOTHESIS_CATALOG_VERSION

    def __post_init__(self) -> None:
        if self.catalog_version != GRC9_HYPOTHESIS_CATALOG_VERSION:
            raise ValueError(f"catalog_version must be {GRC9_HYPOTHESIS_CATALOG_VERSION!r}")
        hypothesis_ids = [item.hypothesis_id for item in self.seed_families]
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError("hypothesis ids must be unique")
        seed_families = [item.seed_family for item in self.seed_families]
        if len(seed_families) != len(set(seed_families)):
            raise ValueError("seed families must be unique")

    def by_mechanism_id(self) -> Mapping[str, GRC9SeedFamilySpec]:
        return {item.mechanism_id: item for item in self.seed_families}

    def generated_profiles(self) -> tuple[str, ...]:
        return tuple(item.profile for item in self.seed_families)

    def generated_lanes(self) -> tuple[str, ...]:
        lanes: list[str] = []
        for item in self.seed_families:
            lanes.extend(item.lanes)
        return tuple(lanes)

    def to_structure_hypotheses(
        self,
        ledger: GRC9MechanismLedger,
    ) -> tuple[GRC9StructureHypothesis, ...]:
        ledger_by_id = ledger.by_id()
        return tuple(
            item.to_structure_hypothesis(ledger_by_id[item.mechanism_id])
            for item in self.seed_families
        )

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "catalog_version": self.catalog_version,
            "seed_families": [item.to_mapping() for item in self.seed_families],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9HypothesisCatalog:
        mapping = _require_mapping(value, field_name="hypothesis_catalog")
        return cls(
            catalog_version=str(mapping.get("catalog_version", GRC9_HYPOTHESIS_CATALOG_VERSION)),
            seed_families=tuple(
                GRC9SeedFamilySpec.from_mapping(item)
                for item in mapping.get("seed_families", [])
            ),
        )


def _control(
    role: str,
    seed_name: str,
    expected_outcome: str,
    **parameter_overrides: Any,
) -> GRC9SeedControlSpec:
    return GRC9SeedControlSpec(
        control_role=role,
        seed_name=seed_name,
        parameter_overrides=parameter_overrides,
        expected_outcome=expected_outcome,
    )


def _perturb(parameter: str, *deltas: str) -> GRC9PerturbationSpec:
    return GRC9PerturbationSpec(parameter=parameter, deltas=tuple(deltas))


def _family(
    ledger: GRC9MechanismLedger,
    *,
    mechanism_id: str,
    hypothesis_id: str,
    seed_family: str,
    node_count: int | str,
    row_column_occupancy: Mapping[str, Any],
    active_inactive_port_pattern: Mapping[str, Any],
    conductance_assignment: Mapping[str, Any],
    coherence_placement: Mapping[str, Any],
    boundary_edge_pattern: Mapping[str, Any],
    expected_lifecycle: tuple[str, ...],
    positive_controls: tuple[GRC9SeedControlSpec, ...],
    negative_controls: tuple[GRC9SeedControlSpec, ...],
    perturbations: tuple[GRC9PerturbationSpec, ...],
    scheduled_for_generation: bool,
) -> GRC9SeedFamilySpec:
    entry = ledger.by_id()[mechanism_id]
    return GRC9SeedFamilySpec(
        mechanism_id=mechanism_id,
        hypothesis_id=hypothesis_id,
        phenomenon=entry.phenomenon,
        seed_family=seed_family,
        profile_version=1,
        node_count=node_count,
        row_column_occupancy=row_column_occupancy,
        active_inactive_port_pattern=active_inactive_port_pattern,
        conductance_assignment=conductance_assignment,
        coherence_placement=coherence_placement,
        boundary_edge_pattern=boundary_edge_pattern,
        expected_lifecycle=expected_lifecycle,
        positive_controls=positive_controls,
        negative_controls=negative_controls,
        perturbations=perturbations,
        predicted_signatures=entry.predicted_telemetry_fields,
        runtime_status=entry.runtime_status,
        scheduled_for_generation=scheduled_for_generation,
    )


def default_grc9_hypothesis_catalog(
    ledger: GRC9MechanismLedger | None = None,
) -> GRC9HypothesisCatalog:
    """Return the initial seeded GRC9 structure hypothesis catalog."""

    ledger = ledger or default_grc9_mechanism_ledger()
    seed_families = (
        _family(
            ledger,
            mechanism_id="grc9_mech_spark_precursor",
            hypothesis_id="grc9_hypothesis_spark_precursor_v1",
            seed_family="spark_precursor",
            node_count=10,
            row_column_occupancy={"parent": "all 3x3 ports occupied", "neighbors": "one per parent port"},
            active_inactive_port_pattern={"parent_active_ports": list(range(1, 10)), "inactive_parent_ports": []},
            conductance_assignment={"mode": "column_imbalance", "center_column": 2},
            coherence_placement={"parent": "sink-biased", "neighbors": "column-graded"},
            boundary_edge_pattern={"old_boundary": "one edge per port", "columns": "balanced count with tunable weights"},
            expected_lifecycle=("saturated sink", "spark evidence", "optional expansion"),
            positive_controls=(
                _control("positive_control", "spark_precursor_positive_control", "column proxy spark gate passes", active_degree=9),
            ),
            negative_controls=(
                _control("negative_control", "spark_precursor_negative_control", "no spark because one port is inactive", active_degree=8),
            ),
            perturbations=(_perturb("spark_threshold", "-10%", "+10%"), _perturb("column_conductance", "-10%", "+10%")),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_expansion_module",
            hypothesis_id="grc9_hypothesis_expansion_module_v1",
            seed_family="expansion_module",
            node_count="parent plus generated module",
            row_column_occupancy={"module": "core plus three primary satellites", "internal_spine": "ports 2,5,8 to satellite port 5"},
            active_inactive_port_pattern={"module_internal_ports": "canonical spine occupied", "new_boundary_capacity": "inactive"},
            conductance_assignment={"internal_bond_mode": "fixed", "boundary_weights": "copied from parent"},
            coherence_placement={"parent_mass": "transferred to satellites", "ratios": [1 / 3, 1 / 3, 1 / 3]},
            boundary_edge_pattern={"reassignment": "by source port column"},
            expected_lifecycle=("spark", "module_created", "budget_preserved"),
            positive_controls=(
                _control("positive_control", "expansion_module_positive_control", "module with at least four nodes is created", target_effective_degree=30),
            ),
            negative_controls=(
                _control("negative_control", "expansion_module_negative_control", "no expansion when spark precondition is absent", active_degree=8),
            ),
            perturbations=(_perturb("target_effective_degree", "-1", "+7"), _perturb("bond_weight", "-10%", "+10%")),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_column_preserving_reassignment",
            hypothesis_id="grc9_hypothesis_column_reassignment_v1",
            seed_family="column_reassignment",
            node_count=10,
            row_column_occupancy={"parent": "all columns populated", "boundary": "distinct column-labeled edge families"},
            active_inactive_port_pattern={"parent_active_ports": list(range(1, 10)), "post_expansion_capacity": "satellite-local"},
            conductance_assignment={"boundary_columns": "weak/medium/strong by column"},
            coherence_placement={"parent": "sink-biased", "neighbors": "column-specific"},
            boundary_edge_pattern={"columns": {"C1": 3, "C2": 3, "C3": 3}},
            expected_lifecycle=("spark", "module_created", "boundary_reassigned_by_column"),
            positive_controls=(
                _control("positive_control", "column_reassignment_positive_control", "reassigned counts match old column families", boundary_columns="balanced"),
            ),
            negative_controls=(
                _control("negative_control", "column_reassignment_negative_control", "no reassignment without expansion", active_degree=8),
            ),
            perturbations=(_perturb("boundary_column_weight", "-10%", "+10%"), _perturb("boundary_edge_count", "-1", "+1")),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_growth_pressure",
            hypothesis_id="grc9_hypothesis_growth_pressure_v1",
            seed_family="growth_pressure",
            node_count=6,
            row_column_occupancy={"parent": "one inactive low-index port", "front": "outward flux gradient"},
            active_inactive_port_pattern={"parent_active_ports": [1, 2, 3, 4], "candidate_birth_port": 5},
            conductance_assignment={"outward_path": "high", "control_path": "low"},
            coherence_placement={"parent": "front-biased", "outside": "lower coherence"},
            boundary_edge_pattern={"front": "single controlled outward boundary"},
            expected_lifecycle=("outward_pressure", "child_attached"),
            positive_controls=(
                _control("positive_control", "growth_pressure_positive_control", "birth probability rises and child attaches", birth_lambda="nominal"),
            ),
            negative_controls=(
                _control("negative_control", "growth_pressure_negative_control", "birth pressure remains below effective threshold", outward_flux="low"),
            ),
            perturbations=(_perturb("birth_lambda", "-10%", "+10%"), _perturb("outward_flux", "-10%", "+10%")),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_row_tensor_regime",
            hypothesis_id="grc9_hypothesis_row_tensor_v1",
            seed_family="row_tensor_regime",
            node_count=7,
            row_column_occupancy={"row_heavy": "row 1 dominates", "balanced_control": "all rows balanced"},
            active_inactive_port_pattern={"occupied_rows": [1, 2, 3], "inactive_ports": "controlled by row"},
            conductance_assignment={"row_1": "high", "row_2": "medium", "row_3": "low"},
            coherence_placement={"gradient": "row-specific mismatch"},
            boundary_edge_pattern={"rows": "same column distribution across rows"},
            expected_lifecycle=("row_tensor_anisotropy", "stable_no_event_optional"),
            positive_controls=(
                _control("positive_control", "row_tensor_positive_control", "row tensor anisotropy increases", row_bias=1),
            ),
            negative_controls=(
                _control("negative_control", "row_tensor_negative_control", "balanced rows suppress anisotropy", row_bias=0),
            ),
            perturbations=(_perturb("row_conductance_bias", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_column_diagnostic_regime",
            hypothesis_id="grc9_hypothesis_column_diagnostic_v1",
            seed_family="column_diagnostic_regime",
            node_count=10,
            row_column_occupancy={"column_profiles": "one near-zero column diagnostic and two controls"},
            active_inactive_port_pattern={"candidate_columns": [1, 2, 3], "active_ports": "column-complete"},
            conductance_assignment={"column_proxy": "alternating row signs produce small H"},
            coherence_placement={"column_2": "near cancellation", "other_columns": "nonzero"},
            boundary_edge_pattern={"columns": "separable by polarity family"},
            expected_lifecycle=("column_proxy_candidate", "spark_precursor_optional"),
            positive_controls=(
                _control("positive_control", "column_diagnostic_positive_control", "column proxy candidate count increases", proxy_column=2),
            ),
            negative_controls=(
                _control("negative_control", "column_diagnostic_negative_control", "no column diagnostic near-zero condition", proxy_column=None),
            ),
            perturbations=(_perturb("column_proxy_balance", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_coarse_graining_roundtrip",
            hypothesis_id="grc9_hypothesis_coarse_profile_v1",
            seed_family="coarse_profile_sparsity",
            node_count=5,
            row_column_occupancy={"profiles": "dense, mixed, and near-one-hot columns"},
            active_inactive_port_pattern={"ports": "column-complete on sampled nodes"},
            conductance_assignment={"fields": ["conductance", "signed_flux"]},
            coherence_placement={"profiles": "one-hot and dense controls"},
            boundary_edge_pattern={"columns": "stable column pools"},
            expected_lifecycle=("coarse_fields_available", "split_roundtrip_diagnostic"),
            positive_controls=(
                _control("positive_control", "coarse_profile_positive_control", "profile sparsity reflects near-one-hot design", profile="one_hot"),
            ),
            negative_controls=(
                _control("negative_control", "coarse_profile_negative_control", "dense profiles reduce sparsity", profile="dense"),
            ),
            perturbations=(_perturb("profile_sparsity", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_budget_correction",
            hypothesis_id="grc9_hypothesis_budget_correction_v1",
            seed_family="budget_correction",
            node_count=5,
            row_column_occupancy={"budget_probe": "minimal connected graph"},
            active_inactive_port_pattern={"ports": "small active subset"},
            conductance_assignment={"mode": "budget-neutral unless perturbation enabled"},
            coherence_placement={"budget": "controlled total perturbation"},
            boundary_edge_pattern={"boundary": "none required"},
            expected_lifecycle=("budget_perturbation", "budget_corrected"),
            positive_controls=(
                _control("positive_control", "budget_correction_positive_control", "budget correction path is recorded", budget_error="small_positive"),
            ),
            negative_controls=(
                _control("negative_control", "budget_correction_negative_control", "no correction when budget is already exact", budget_error=0),
            ),
            perturbations=(_perturb("budget_error", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_quiescent_basin",
            hypothesis_id="grc9_hypothesis_quiescent_basin_v1",
            seed_family="quiescent_basin",
            node_count=6,
            row_column_occupancy={"balanced": "rows and columns balanced around stable sink"},
            active_inactive_port_pattern={"active_ports": [1, 2, 3, 4, 5], "inactive_ports": [6, 7, 8, 9], "pressure": "low"},
            conductance_assignment={"mode": "symmetric_balanced"},
            coherence_placement={"sink": "stable", "neighbors": "lower balanced"},
            boundary_edge_pattern={"boundary": "no outward pressure"},
            expected_lifecycle=("stable_sink", "no_spark", "no_growth"),
            positive_controls=(
                _control("no_event_control", "quiescent_basin_no_event_control", "no lifecycle events and stable basin", event_activity=0),
            ),
            negative_controls=(
                _control("negative_control", "quiescent_basin_negative_control", "small perturbation remains below event thresholds", perturbation="small"),
            ),
            perturbations=(_perturb("conductance_noise", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_transport_pathway",
            hypothesis_id="grc9_hypothesis_transport_pathway_v1",
            seed_family="transport_pathway",
            node_count=8,
            row_column_occupancy={"paths": "competing short and long paths"},
            active_inactive_port_pattern={"source_ports": "two path exits", "target_ports": "two path entries"},
            conductance_assignment={"short_path": "low", "long_path": "high"},
            coherence_placement={"source": "high", "target": "low"},
            boundary_edge_pattern={"paths": "asymmetric conductance alternatives"},
            expected_lifecycle=("flux_routing", "strongest_flux_path_identified"),
            positive_controls=(
                _control("positive_control", "transport_pathway_positive_control", "strongest flux follows high-conductance path", high_path="long"),
            ),
            negative_controls=(
                _control("negative_control", "transport_pathway_negative_control", "balanced paths reduce routing contrast", high_path=None),
            ),
            perturbations=(_perturb("path_conductance_ratio", "-10%", "+10%"),),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_identity_fission_persistence",
            hypothesis_id="grc9_hypothesis_fission_candidate_v1",
            seed_family="fission_candidate",
            node_count="post-expansion module plus two basin attractors",
            row_column_occupancy={"module": "two pole columns with bridge column"},
            active_inactive_port_pattern={"poles": "boundary-coupled", "bridge": "weak"},
            conductance_assignment={"pole_to_boundary": "strong", "core_bridge": "weak"},
            coherence_placement={"poles": "two attractor-biased masses"},
            boundary_edge_pattern={"columns": "two persistent sink basins"},
            expected_lifecycle=("expansion", "two_sink_persistence", "fission_confirmed_optional"),
            positive_controls=(
                _control("positive_control", "fission_candidate_positive_control", "two sinks persist through configured window", persistence_delta=5),
            ),
            negative_controls=(
                _control("negative_control", "fission_candidate_negative_control", "basins merge before persistence window closes", bridge_conductance="high"),
            ),
            perturbations=(_perturb("bridge_conductance", "-10%", "+10%"), _perturb("minimum_basin_mass", "-10%", "+10%")),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9_mech_adiabatic_expansion",
            hypothesis_id="grc9_hypothesis_adiabatic_expansion_v1",
            seed_family="adiabatic_expansion",
            node_count="parent plus generated module",
            row_column_occupancy={"module": "same as expansion module"},
            active_inactive_port_pattern={"module": "substep-dependent"},
            conductance_assignment={"schedule": "phased in"},
            coherence_placement={"schedule": "phased transfer"},
            boundary_edge_pattern={"reassignment": "phased"},
            expected_lifecycle=("deferred_until_runtime_support",),
            positive_controls=(),
            negative_controls=(),
            perturbations=(),
            scheduled_for_generation=False,
        ),
    )
    return GRC9HypothesisCatalog(seed_families=seed_families)


__all__ = [
    "GRC9_HYPOTHESIS_CATALOG_VERSION",
    "GRC9HypothesisCatalog",
    "GRC9PerturbationSpec",
    "GRC9SeedControlSpec",
    "GRC9SeedFamilySpec",
    "default_grc9_hypothesis_catalog",
]
