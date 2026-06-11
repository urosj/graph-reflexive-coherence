"""Runtime structure hypothesis catalog for GRC9V3 discovery."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

from .grc9_manifest import generated_lane_name, is_generated_lane_name
from .grc9v3_mechanism_ledger import (
    GRC9V3MechanismLedger,
    GRC9V3MechanismLedgerEntry,
    GRC9V3PredictedSignature,
    GRC9V3_RUNTIME_TESTABLE,
    default_grc9v3_mechanism_ledger,
)


GRC9V3_HYPOTHESIS_CATALOG_VERSION = "grc9v3_hypothesis_catalog_v1"

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_PROFILE_RE = re.compile(r"^grc9v3_discovery_[a-z0-9]+(?:_[a-z0-9]+)*_v[1-9][0-9]*$")


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_token(value: str, *, field_name: str) -> None:
    _require_non_empty(value, field_name=field_name)
    if not _TOKEN_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use lowercase snake_case tokens")


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


def grc9v3_profile_name(phenomenon: str, version: int) -> str:
    """Return the standard GRC9V3 discovery profile name."""

    _validate_token(phenomenon, field_name="phenomenon")
    if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
        raise ValueError("version must be a positive integer")
    return f"grc9v3_discovery_{phenomenon}_v{version}"


def is_grc9v3_discovery_profile_name(value: str) -> bool:
    return isinstance(value, str) and _PROFILE_RE.fullmatch(value) is not None


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
class GRC9V3SeedControlSpec:
    control_role: str
    seed_name: str
    parameter_overrides: Mapping[str, Any]
    expected_outcome: str
    scheduled_for_generation: bool = True

    def __post_init__(self) -> None:
        generated_lane_name("validation_probe", self.control_role)
        _validate_token(self.seed_name, field_name="seed_name")
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
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3SeedControlSpec:
        mapping = _require_mapping(value, field_name="seed_control")
        return cls(
            control_role=str(mapping["control_role"]),
            seed_name=str(mapping["seed_name"]),
            parameter_overrides=dict(mapping.get("parameter_overrides", {})),
            expected_outcome=str(mapping["expected_outcome"]),
            scheduled_for_generation=bool(mapping.get("scheduled_for_generation", True)),
        )


@dataclass(frozen=True)
class GRC9V3PerturbationSpec:
    parameter: str
    deltas: tuple[str, ...]
    parent_control_role: str = "positive_control"

    def __post_init__(self) -> None:
        _validate_token(self.parameter, field_name="parameter")
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
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3PerturbationSpec:
        mapping = _require_mapping(value, field_name="perturbation")
        return cls(
            parameter=str(mapping["parameter"]),
            deltas=tuple(
                str(item)
                for item in _require_sequence(mapping.get("deltas", ()), field_name="deltas")
            ),
            parent_control_role=str(mapping.get("parent_control_role", "positive_control")),
        )


@dataclass(frozen=True)
class GRC9V3SeedFamilySpec:
    mechanism_id: str
    hypothesis_id: str
    phenomenon: str
    ownership: tuple[str, ...]
    seed_family: str
    profile_version: int
    node_count: int | str
    graph_preconditions: Mapping[str, Any]
    state_preconditions: Mapping[str, Any]
    port_occupancy_pattern: Mapping[str, Any]
    conductance_assignment: Mapping[str, Any]
    coherence_placement: Mapping[str, Any]
    basin_hierarchy_setup: Mapping[str, Any]
    expected_lifecycle: tuple[str, ...]
    positive_controls: tuple[GRC9V3SeedControlSpec, ...]
    negative_controls: tuple[GRC9V3SeedControlSpec, ...]
    perturbations: tuple[GRC9V3PerturbationSpec, ...]
    predicted_signatures: tuple[GRC9V3PredictedSignature, ...]
    predicted_event_sequence: tuple[str, ...]
    required_checkpoint_overlays: tuple[str, ...]
    runtime_status: str
    scheduled_for_generation: bool

    def __post_init__(self) -> None:
        _require_non_empty(self.mechanism_id, field_name="mechanism_id")
        _validate_token(self.hypothesis_id, field_name="hypothesis_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        _validate_token(self.seed_family, field_name="seed_family")
        grc9v3_profile_name(self.phenomenon, self.profile_version)
        generated_lane_name(self.seed_family, "positive_control")
        if not self.ownership:
            raise ValueError("ownership must not be empty")
        if isinstance(self.node_count, bool) or not isinstance(self.node_count, int | str):
            raise ValueError("node_count must be an integer or descriptive string")
        if isinstance(self.node_count, int) and self.node_count <= 0:
            raise ValueError("node_count must be positive")
        for field_name in (
            "graph_preconditions",
            "state_preconditions",
            "port_occupancy_pattern",
            "conductance_assignment",
            "coherence_placement",
            "basin_hierarchy_setup",
        ):
            _require_mapping(getattr(self, field_name), field_name=field_name)
        if not self.expected_lifecycle:
            raise ValueError("expected_lifecycle must not be empty")
        if self.runtime_status == GRC9V3_RUNTIME_TESTABLE:
            if not (self.positive_controls or self.negative_controls):
                raise ValueError("testable seed families need at least one control")
            if not self.predicted_signatures:
                raise ValueError("testable seed families need predicted signatures")
            if not self.scheduled_for_generation:
                raise ValueError("testable seed families must be scheduled")
        elif self.scheduled_for_generation:
            raise ValueError("non-testable seed families cannot be scheduled")

    @property
    def profile(self) -> str:
        return grc9v3_profile_name(self.phenomenon, self.profile_version)

    @property
    def lanes(self) -> tuple[str, ...]:
        return tuple(
            generated_lane_name(self.seed_family, control.control_role)
            for control in (*self.positive_controls, *self.negative_controls)
        )

    def to_structure_hypothesis(
        self,
        ledger_entry: GRC9V3MechanismLedgerEntry,
    ) -> Mapping[str, Any]:
        if ledger_entry.mechanism_id != self.mechanism_id:
            raise ValueError("ledger_entry does not match seed family mechanism_id")
        if ledger_entry.runtime_status != self.runtime_status:
            raise ValueError("seed family runtime_status must copy the ledger entry")
        return {
            "hypothesis_id": self.hypothesis_id,
            "target_phenomenon": self.phenomenon,
            "runtime_status": self.runtime_status,
            "ownership": list(self.ownership),
            "mechanism_id": self.mechanism_id,
            "phase7_sources": [item.to_mapping() for item in ledger_entry.phase7_sources],
            "parent_family_sources": [
                item.to_mapping() for item in ledger_entry.parent_family_sources
            ],
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "state_preconditions": _json_safe(self.state_preconditions),
            "seed_family": self.seed_family,
            "seed_parameters": {
                "node_count": self.node_count,
                "port_occupancy_pattern": _json_safe(self.port_occupancy_pattern),
                "conductance_assignment": _json_safe(self.conductance_assignment),
                "coherence_placement": _json_safe(self.coherence_placement),
                "basin_hierarchy_setup": _json_safe(self.basin_hierarchy_setup),
                "expected_lifecycle": list(self.expected_lifecycle),
                "positive_controls": [
                    item.to_mapping() for item in self.positive_controls
                ],
                "negative_controls": [
                    item.to_mapping() for item in self.negative_controls
                ],
                "perturbations": [item.to_mapping() for item in self.perturbations],
                "required_checkpoint_overlays": list(self.required_checkpoint_overlays),
                "scheduled_for_generation": self.scheduled_for_generation,
            },
            "generator": "generate_grc9v3_seed",
            "predicted_signatures": [
                item.to_mapping() for item in self.predicted_signatures
            ],
            "predicted_event_sequence": list(self.predicted_event_sequence),
        }

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "hypothesis_id": self.hypothesis_id,
            "phenomenon": self.phenomenon,
            "ownership": list(self.ownership),
            "seed_family": self.seed_family,
            "profile": self.profile,
            "profile_version": self.profile_version,
            "node_count": self.node_count,
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "state_preconditions": _json_safe(self.state_preconditions),
            "port_occupancy_pattern": _json_safe(self.port_occupancy_pattern),
            "conductance_assignment": _json_safe(self.conductance_assignment),
            "coherence_placement": _json_safe(self.coherence_placement),
            "basin_hierarchy_setup": _json_safe(self.basin_hierarchy_setup),
            "expected_lifecycle": list(self.expected_lifecycle),
            "positive_controls": [item.to_mapping() for item in self.positive_controls],
            "negative_controls": [item.to_mapping() for item in self.negative_controls],
            "perturbations": [item.to_mapping() for item in self.perturbations],
            "predicted_signatures": [
                item.to_mapping() for item in self.predicted_signatures
            ],
            "predicted_event_sequence": list(self.predicted_event_sequence),
            "required_checkpoint_overlays": list(self.required_checkpoint_overlays),
            "runtime_status": self.runtime_status,
            "scheduled_for_generation": self.scheduled_for_generation,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3SeedFamilySpec:
        mapping = _require_mapping(value, field_name="seed_family")
        return cls(
            mechanism_id=str(mapping["mechanism_id"]),
            hypothesis_id=str(mapping["hypothesis_id"]),
            phenomenon=str(mapping["phenomenon"]),
            ownership=tuple(str(item) for item in mapping.get("ownership", ())),
            seed_family=str(mapping["seed_family"]),
            profile_version=int(mapping.get("profile_version", 1)),
            node_count=mapping["node_count"],
            graph_preconditions=dict(mapping["graph_preconditions"]),
            state_preconditions=dict(mapping["state_preconditions"]),
            port_occupancy_pattern=dict(mapping["port_occupancy_pattern"]),
            conductance_assignment=dict(mapping["conductance_assignment"]),
            coherence_placement=dict(mapping["coherence_placement"]),
            basin_hierarchy_setup=dict(mapping["basin_hierarchy_setup"]),
            expected_lifecycle=tuple(str(item) for item in mapping["expected_lifecycle"]),
            positive_controls=tuple(
                GRC9V3SeedControlSpec.from_mapping(item)
                for item in mapping.get("positive_controls", [])
            ),
            negative_controls=tuple(
                GRC9V3SeedControlSpec.from_mapping(item)
                for item in mapping.get("negative_controls", [])
            ),
            perturbations=tuple(
                GRC9V3PerturbationSpec.from_mapping(item)
                for item in mapping.get("perturbations", [])
            ),
            predicted_signatures=_to_signatures(mapping.get("predicted_signatures", [])),
            predicted_event_sequence=tuple(
                str(item) for item in mapping.get("predicted_event_sequence", [])
            ),
            required_checkpoint_overlays=tuple(
                str(item) for item in mapping.get("required_checkpoint_overlays", [])
            ),
            runtime_status=str(mapping["runtime_status"]),
            scheduled_for_generation=bool(mapping.get("scheduled_for_generation", False)),
        )


@dataclass(frozen=True)
class GRC9V3HypothesisCatalog:
    seed_families: tuple[GRC9V3SeedFamilySpec, ...]
    catalog_version: str = GRC9V3_HYPOTHESIS_CATALOG_VERSION

    def __post_init__(self) -> None:
        if self.catalog_version != GRC9V3_HYPOTHESIS_CATALOG_VERSION:
            raise ValueError(
                f"catalog_version must be {GRC9V3_HYPOTHESIS_CATALOG_VERSION!r}"
            )
        hypothesis_ids = [item.hypothesis_id for item in self.seed_families]
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError("hypothesis ids must be unique")
        seed_families = [item.seed_family for item in self.seed_families]
        if len(seed_families) != len(set(seed_families)):
            raise ValueError("seed families must be unique")

    def by_mechanism_id(self) -> Mapping[str, GRC9V3SeedFamilySpec]:
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
        ledger: GRC9V3MechanismLedger,
    ) -> tuple[Mapping[str, Any], ...]:
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
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9V3HypothesisCatalog:
        mapping = _require_mapping(value, field_name="hypothesis_catalog")
        return cls(
            catalog_version=str(
                mapping.get("catalog_version", GRC9V3_HYPOTHESIS_CATALOG_VERSION)
            ),
            seed_families=tuple(
                GRC9V3SeedFamilySpec.from_mapping(item)
                for item in mapping.get("seed_families", [])
            ),
        )


def _control(
    role: str,
    seed_name: str,
    expected_outcome: str,
    **parameter_overrides: Any,
) -> GRC9V3SeedControlSpec:
    return GRC9V3SeedControlSpec(
        control_role=role,
        seed_name=seed_name,
        parameter_overrides=parameter_overrides,
        expected_outcome=expected_outcome,
    )


def _perturb(parameter: str, *deltas: str) -> GRC9V3PerturbationSpec:
    return GRC9V3PerturbationSpec(parameter=parameter, deltas=tuple(deltas))


def _family(
    ledger: GRC9V3MechanismLedger,
    *,
    mechanism_id: str,
    hypothesis_id: str,
    seed_family: str,
    node_count: int | str,
    port_occupancy_pattern: Mapping[str, Any],
    conductance_assignment: Mapping[str, Any],
    coherence_placement: Mapping[str, Any],
    basin_hierarchy_setup: Mapping[str, Any],
    expected_lifecycle: tuple[str, ...],
    positive_controls: tuple[GRC9V3SeedControlSpec, ...] = (),
    negative_controls: tuple[GRC9V3SeedControlSpec, ...] = (),
    perturbations: tuple[GRC9V3PerturbationSpec, ...] = (),
    additional_predicted_signatures: tuple[GRC9V3PredictedSignature, ...] = (),
    required_checkpoint_overlays: tuple[str, ...] = (),
    scheduled_for_generation: bool = False,
) -> GRC9V3SeedFamilySpec:
    entry = ledger.by_id()[mechanism_id]
    return GRC9V3SeedFamilySpec(
        mechanism_id=mechanism_id,
        hypothesis_id=hypothesis_id,
        phenomenon=entry.phenomenon,
        ownership=entry.ownership,
        seed_family=seed_family,
        profile_version=1,
        node_count=node_count,
        graph_preconditions=entry.graph_preconditions,
        state_preconditions=entry.state_preconditions,
        port_occupancy_pattern=port_occupancy_pattern,
        conductance_assignment=conductance_assignment,
        coherence_placement=coherence_placement,
        basin_hierarchy_setup=basin_hierarchy_setup,
        expected_lifecycle=expected_lifecycle,
        positive_controls=positive_controls,
        negative_controls=negative_controls,
        perturbations=perturbations,
        predicted_signatures=(
            entry.predicted_telemetry_fields + additional_predicted_signatures
        ),
        predicted_event_sequence=entry.predicted_event_sequence,
        required_checkpoint_overlays=required_checkpoint_overlays,
        runtime_status=entry.runtime_status,
        scheduled_for_generation=scheduled_for_generation,
    )


def default_grc9v3_hypothesis_catalog(
    ledger: GRC9V3MechanismLedger | None = None,
) -> GRC9V3HypothesisCatalog:
    """Return the initial pure-runtime GRC9V3 hypothesis catalog."""

    ledger = ledger or default_grc9v3_mechanism_ledger()
    seed_families = (
        _family(
            ledger,
            mechanism_id="grc9v3_mech_hybrid_spark_gate",
            hypothesis_id="grc9v3_hypothesis_hybrid_spark_gate_v1",
            seed_family="hybrid_spark_gate",
            node_count=10,
            port_occupancy_pattern={
                "candidate_node": "all nine ports occupied",
                "neighbors": "one neighbor per port",
                "negative_control": "one inactive port",
            },
            conductance_assignment={"mode": "signed_hessian_degeneracy_probe"},
            coherence_placement={"candidate": "basin-interior low-Hessian"},
            basin_hierarchy_setup={"basin_id": "spark_candidate_basin", "depth": 0},
            expected_lifecycle=("hybrid_spark_candidate",),
            positive_controls=(
                _control(
                    "positive_control",
                    "hybrid_spark_gate_positive_control",
                    "saturation, basin, and signed-Hessian gates pass",
                    active_degree=9,
                    signed_hessian_min="below_epsilon",
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "hybrid_spark_gate_negative_control",
                    "candidate fails because saturation is incomplete",
                    active_degree=8,
                ),
            ),
            perturbations=(
                _perturb("epsilon_spark", "-10%", "+10%"),
                _perturb("signed_hessian_min", "-10%", "+10%"),
            ),
            required_checkpoint_overlays=("node_overlay", "port_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_spark_to_expansion",
            hypothesis_id="grc9v3_hypothesis_spark_to_expansion_v1",
            seed_family="spark_to_expansion",
            node_count="candidate plus generated expansion module",
            port_occupancy_pattern={"candidate_node": "saturated", "module_ports": "generated"},
            conductance_assignment={"external_ports": "controlled D_eff", "internal_bonds": "fixed"},
            coherence_placement={"parent_mass": "distributed to module satellites"},
            basin_hierarchy_setup={"parent": "pre-expansion sink", "children": "not claimed until stabilization"},
            expected_lifecycle=("hybrid_spark_candidate", "hybrid_mechanical_expansion"),
            positive_controls=(
                _control(
                    "positive_control",
                    "spark_to_expansion_positive_control",
                    "candidate expands into a module",
                    target_effective_degree=30,
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "spark_to_expansion_negative_control",
                    "no expansion without candidate",
                    active_degree=8,
                ),
            ),
            perturbations=(_perturb("target_effective_degree", "-1", "+7"),),
            required_checkpoint_overlays=("node_overlay", "port_overlay", "module_overlay", "edge_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_column_diagnostic_proxy",
            hypothesis_id="grc9v3_hypothesis_column_diagnostic_proxy_v1",
            seed_family="column_diagnostic_proxy",
            node_count=10,
            port_occupancy_pattern={
                "candidate_node": "column family ports controlled independently",
                "target_column": "near cancellation or imbalance",
            },
            conductance_assignment={"target_column": "controlled proxy magnitude"},
            coherence_placement={"target_column": "near Eq. 11 cancellation"},
            basin_hierarchy_setup={"basin_id": "column_proxy_probe_basin"},
            expected_lifecycle=("column_diagnostic_proxy", "hybrid_spark_candidate_optional"),
            positive_controls=(),
            negative_controls=(),
            perturbations=(),
            required_checkpoint_overlays=("node_overlay", "port_overlay"),
            scheduled_for_generation=False,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_appendix_e_cell_division",
            hypothesis_id="grc9v3_hypothesis_appendix_e_cell_division_v1",
            seed_family="appendix_e_cell_division",
            node_count="representative Appendix E module graph",
            port_occupancy_pattern={"candidate": "saturated", "daughter_regions": "two sink-capable regions"},
            conductance_assignment={"daughter_regions": "separable conductance basins"},
            coherence_placement={"module": "mass sufficient for two daughter sinks"},
            basin_hierarchy_setup={"parent": "root basin", "children": "two stabilized daughters"},
            expected_lifecycle=(
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
            ),
            positive_controls=(
                _control(
                    "positive_control",
                    "appendix_e_cell_division_positive_control",
                    "completed hybrid spark produces two daughter sinks",
                    daughter_sink_count=2,
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "appendix_e_cell_division_negative_control",
                    "child stabilization fails when daughter basin mass is too low",
                    daughter_sink_count=1,
                ),
            ),
            perturbations=(_perturb("module_basin_mass", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay", "module_overlay", "port_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_choice_collapse",
            hypothesis_id="grc9v3_hypothesis_choice_collapse_v1",
            seed_family="choice_collapse",
            node_count=12,
            port_occupancy_pattern={"choice_node": "two competing successor basins"},
            conductance_assignment={"winner_path": "strong", "loser_path": "weak"},
            coherence_placement={"choice_node": "between two attractors"},
            basin_hierarchy_setup={"basins": "two post-expansion candidate basins"},
            expected_lifecycle=("choice_detected", "collapse"),
            positive_controls=(
                _control(
                    "positive_control",
                    "choice_collapse_positive_control",
                    "choice separates and collapse registry updates",
                    compatibility_gap="high",
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "choice_collapse_negative_control",
                    "ambiguous compatibility avoids collapse",
                    compatibility_gap="low",
                ),
            ),
            perturbations=(_perturb("compatibility_gap", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay", "choice_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_growth_pressure",
            hypothesis_id="grc9v3_hypothesis_growth_pressure_v1",
            seed_family="growth_pressure",
            node_count=8,
            port_occupancy_pattern={"parent": "one inactive boundary port", "front": "outward flux"},
            conductance_assignment={"front_edge": "high outward pressure"},
            coherence_placement={"parent": "front-biased"},
            basin_hierarchy_setup={"parent_basin": "stable pre-growth basin"},
            expected_lifecycle=("growth",),
            positive_controls=(
                _control(
                    "positive_control",
                    "growth_pressure_positive_control",
                    "inactive port attaches a child",
                    lambda_birth="high",
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "growth_pressure_negative_control",
                    "low lambda or pressure avoids child attachment",
                    lambda_birth="low",
                ),
            ),
            perturbations=(_perturb("lambda_birth", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay", "port_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_quadrature_budget_preservation",
            hypothesis_id="grc9v3_hypothesis_budget_preservation_v1",
            seed_family="budget_preservation",
            node_count=8,
            port_occupancy_pattern={"graph": "small connected post-mutation graph"},
            conductance_assignment={"mutation": "expansion or growth perturbation"},
            coherence_placement={"budget": "controlled before/after perturbation"},
            basin_hierarchy_setup={"quadrature_mode": "unit_measure"},
            expected_lifecycle=("budget",),
            positive_controls=(
                _control(
                    "positive_control",
                    "budget_preservation_positive_control",
                    "budget error is corrected after mutation",
                    budget_correction_method="simplex_projection",
                    budget_error=0.25,
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "budget_preservation_negative_control",
                    "no correction needed when budget is already closed",
                    budget_error=0,
                ),
            ),
            perturbations=(_perturb("budget_error", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay",),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_hessian_backend_comparison",
            hypothesis_id="grc9v3_hypothesis_hessian_backend_comparison_v1",
            seed_family="hessian_backend_comparison",
            node_count=9,
            port_occupancy_pattern={"same_graph_pair": "row-basis and WLS paired runs"},
            conductance_assignment={"geometry": "asymmetric enough to separate backends"},
            coherence_placement={"candidate": "near backend-sensitive Hessian threshold"},
            basin_hierarchy_setup={"basin_seed": "backend-sensitive"},
            expected_lifecycle=("backend_pair_comparison",),
            positive_controls=(
                _control(
                    "baseline_control",
                    "hessian_backend_row_basis_baseline",
                    "row-basis diagonal backend run",
                    hessian_backend="row_basis_diagonal",
                ),
                _control(
                    "positive_control",
                    "hessian_backend_wls_comparison",
                    "weighted least-squares comparison run",
                    hessian_backend="weighted_least_squares",
                ),
            ),
            negative_controls=(),
            perturbations=(_perturb("coherence_placement", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay",),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_transport_basin_rerouting",
            hypothesis_id="grc9v3_hypothesis_transport_basin_rerouting_v1",
            seed_family="transport_basin_rerouting",
            node_count=11,
            port_occupancy_pattern={"junction": "two competing successor paths"},
            conductance_assignment={"path_a": "strong short path", "path_b": "weak long path"},
            coherence_placement={"gradient": "rerouting-sensitive"},
            basin_hierarchy_setup={"basins": "successor-map derived"},
            expected_lifecycle=("transport_update", "basin_reroute"),
            positive_controls=(
                _control(
                    "positive_control",
                    "transport_basin_rerouting_positive_control",
                    "flux gap reroutes successor basin",
                    flux_gap="high",
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "transport_basin_rerouting_negative_control",
                    "balanced paths avoid reroute",
                    flux_gap="low",
                ),
            ),
            perturbations=(_perturb("path_conductance_ratio", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay", "edge_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_coarse_cache_invalidation",
            hypothesis_id="grc9v3_hypothesis_coarse_cache_invalidation_v1",
            seed_family="coarse_cache_invalidation",
            node_count=8,
            port_occupancy_pattern={"cache_graph": "small connected graph with topology mutation"},
            conductance_assignment={"mutation_edge": "added or removed by lifecycle event"},
            coherence_placement={"value_mutation": "small continuity update"},
            basin_hierarchy_setup={"cache": "prepopulated coarse state"},
            expected_lifecycle=("coarse",),
            positive_controls=(
                _control(
                    "positive_control",
                    "coarse_cache_invalidation_positive_control",
                    "topology mutation invalidates coarse cache",
                    mutation_kind="topology_changed",
                ),
            ),
            negative_controls=(
                _control(
                    "negative_control",
                    "coarse_cache_invalidation_negative_control",
                    "unchanged graph keeps coarse cache warm",
                    mutation_kind="none",
                ),
            ),
            perturbations=(_perturb("mutation_strength", "-10%", "+10%"),),
            required_checkpoint_overlays=("node_overlay", "edge_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_quiescent_hybrid_control",
            hypothesis_id="grc9v3_hypothesis_quiescent_hybrid_control_v1",
            seed_family="quiescent_hybrid_control",
            node_count=6,
            port_occupancy_pattern={"all_nodes": "below saturation"},
            conductance_assignment={"graph": "balanced low flux"},
            coherence_placement={"all_nodes": "stable non-degenerate field"},
            basin_hierarchy_setup={"basin": "single stable sink"},
            expected_lifecycle=("quiescent_stable_window",),
            positive_controls=(
                _control(
                    "no_event_control",
                    "quiescent_hybrid_no_event_control",
                    "no spark, expansion, growth, choice, or collapse",
                    active_degree_max=5,
                ),
            ),
            negative_controls=(),
            perturbations=(_perturb("active_degree_max", "-1", "+1"),),
            required_checkpoint_overlays=("node_overlay", "port_overlay"),
            scheduled_for_generation=True,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_signed_crossing_spark",
            hypothesis_id="grc9v3_hypothesis_signed_crossing_spark_v1",
            seed_family="signed_crossing_spark",
            node_count=10,
            port_occupancy_pattern={"candidate": "saturated with signed history"},
            conductance_assignment={"history_pair": "opposite signed Hessian windows"},
            coherence_placement={"candidate": "sign-crossing threshold"},
            basin_hierarchy_setup={"history": "requires previous signed Hessian"},
            expected_lifecycle=("capability_gated_signed_crossing",),
            required_checkpoint_overlays=("node_overlay", "port_overlay"),
            scheduled_for_generation=False,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_boundary_barrier_ghost",
            hypothesis_id="grc9v3_hypothesis_boundary_barrier_ghost_v1",
            seed_family="boundary_barrier_ghost",
            node_count=6,
            port_occupancy_pattern={"boundary": "requires non-prune boundary"},
            conductance_assignment={"boundary_edge": "reserved"},
            coherence_placement={"boundary": "reserved"},
            basin_hierarchy_setup={"boundary": "reserved"},
            expected_lifecycle=("capability_gated_boundary",),
            required_checkpoint_overlays=("edge_overlay",),
            scheduled_for_generation=False,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_source_language_lowering",
            hypothesis_id="grc9v3_hypothesis_source_language_lowering_v1",
            seed_family="source_language_lowering",
            node_count="requires reviewed runtime motif",
            port_occupancy_pattern={"source": "deferred"},
            conductance_assignment={"source": "deferred"},
            coherence_placement={"source": "deferred"},
            basin_hierarchy_setup={"source": "deferred"},
            expected_lifecycle=("deferred_until_reviewed_motif_catalog",),
            required_checkpoint_overlays=(),
            scheduled_for_generation=False,
        ),
        _family(
            ledger,
            mechanism_id="grc9v3_mech_lorentzian_observer_layer",
            hypothesis_id="grc9v3_hypothesis_lorentzian_observer_layer_v1",
            seed_family="lorentzian_observer_layer",
            node_count="out of scope",
            port_occupancy_pattern={"observer": "out_of_scope"},
            conductance_assignment={"observer": "out_of_scope"},
            coherence_placement={"observer": "out_of_scope"},
            basin_hierarchy_setup={"observer": "out_of_scope"},
            expected_lifecycle=("out_of_scope_non_claim",),
            required_checkpoint_overlays=(),
            scheduled_for_generation=False,
        ),
    )
    return GRC9V3HypothesisCatalog(seed_families=seed_families)


__all__ = [
    "GRC9V3_HYPOTHESIS_CATALOG_VERSION",
    "GRC9V3HypothesisCatalog",
    "GRC9V3PerturbationSpec",
    "GRC9V3SeedControlSpec",
    "GRC9V3SeedFamilySpec",
    "default_grc9v3_hypothesis_catalog",
    "grc9v3_profile_name",
    "is_grc9v3_discovery_profile_name",
]
