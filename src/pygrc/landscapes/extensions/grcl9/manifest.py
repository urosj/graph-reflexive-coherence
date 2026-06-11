"""Lowering manifest contract for GRCL-9 Revision 1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any


GRCL9_LOWERING_MANIFEST_VERSION = "grcl9_lowering_manifest_v1"
GRCL9_SOURCE_SCHEMA_VERSION = "grcl9.source.v1"

GRCL9_ACCEPTED_SOURCE_CONSTRUCT_KINDS = frozenset(
    {
        "spark_candidate_region",
        "column_proxy_profile",
        "instability_profile",
        "expansion_refinement_region",
        "growth_locus",
        "post_expansion_fission_geometry",
    }
)
GRCL9_SPARK_GATE_INTENTS = frozenset(
    {"saturation_column_proxy", "saturation_instability"}
)
GRCL9_RESERVED_SPARK_GATE_INTENTS = frozenset({"saturation_sign_crossing"})
GRCL9_BASE_NON_CLAIMS = (
    "no_runtime_event_injection",
    "no_solved_flux",
    "no_solved_diagnostic",
    "no_source_level_fission_confirmation",
    "no_grcv3_hierarchy_semantics",
    "no_lorentzian_causal_layer",
    "no_observer_local_semantics",
)

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_CONTROL_ROLES = frozenset({"pass_control", "fail_control", "low_control", "high_control"})
_EXPECTED_S0026_ACCEPTED_MOTIF_IDS = frozenset(
    {
        "grc9-motif-s0006-spark-column-proxy-eps-pass",
        "grc9-motif-s0006-spark-column-proxy-eps-fail",
        "grc9-motif-s0006-spark-instability-tau-pass",
        "grc9-motif-s0006-spark-instability-tau-fail",
        "grc9-motif-s0006-spark-to-expansion-d-eff-low",
        "grc9-motif-s0006-spark-to-expansion-d-eff-high",
        "grc9-motif-s0006-growth-pressure-lambda-high",
        "grc9-motif-s0006-growth-pressure-lambda-low",
        "grc9-motif-s0006-post-expansion-fission-min-mass-pass",
        "grc9-motif-s0006-post-expansion-fission-min-mass-fail",
    }
)


def _require_string(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _optional_string(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name=field_name)


def _require_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def _require_sequence(value: Any, *, field_name: str) -> Sequence[Any]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence")
    return value


def _string_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    return tuple(
        _require_string(item, field_name=f"{field_name}[{index}]")
        for index, item in enumerate(_require_sequence(value, field_name=field_name))
    )


def _validate_token(value: str, *, field_name: str) -> None:
    _require_string(value, field_name=field_name)
    if not _TOKEN_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use lowercase snake-case tokens")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


def _validate_grc9_field_path(field_path: str) -> None:
    if "event_counts_by_kind" in field_path:
        raise ValueError("telemetry field paths must not use event_counts_by_kind")
    if not field_path.startswith("family_extensions.grc9."):
        raise ValueError("telemetry field paths must use family_extensions.grc9.*")


@dataclass(frozen=True)
class GRCL9TelemetryExpectation:
    """Field-backed telemetry expectation for a lowered source fixture."""

    field_path: str
    surface: str
    predicate: str
    expected_type: str | None = None
    required: bool = True

    def __post_init__(self) -> None:
        _require_string(self.field_path, field_name="field_path")
        _validate_grc9_field_path(self.field_path)
        _require_string(self.surface, field_name="surface")
        _require_string(self.predicate, field_name="predicate")
        _require_bool(self.required, field_name="required")

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "field_path": self.field_path,
            "surface": self.surface,
            "predicate": self.predicate,
            "required": self.required,
        }
        if self.expected_type is not None:
            payload["expected_type"] = self.expected_type
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9TelemetryExpectation:
        mapping = _require_mapping(value, field_name="telemetry_expectation")
        return cls(
            field_path=_require_string(mapping.get("field_path"), field_name="field_path"),
            surface=_require_string(mapping.get("surface"), field_name="surface"),
            predicate=_require_string(mapping.get("predicate"), field_name="predicate"),
            expected_type=_optional_string(mapping.get("expected_type"), field_name="expected_type"),
            required=_require_bool(mapping.get("required", True), field_name="required"),
        )


@dataclass(frozen=True)
class GRCL9LoweringPassFailControl:
    """Source fixture control linked to an accepted S0026 motif."""

    control_role: str
    source_fixture_name: str
    source_construct_id: str
    accepted_motif_id: str
    s0026_lane: str
    expected_outcome: str
    selector_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_token(self.control_role, field_name="control_role")
        if self.control_role not in _CONTROL_ROLES:
            raise ValueError(f"control_role must be one of {tuple(sorted(_CONTROL_ROLES))}")
        _validate_token(self.source_fixture_name, field_name="source_fixture_name")
        _validate_token(self.source_construct_id, field_name="source_construct_id")
        _require_string(self.accepted_motif_id, field_name="accepted_motif_id")
        _validate_token(self.s0026_lane, field_name="s0026_lane")
        _require_string(self.expected_outcome, field_name="expected_outcome")
        for selector_id in self.selector_ids:
            _validate_token(selector_id, field_name="selector_ids[]")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "control_role": self.control_role,
            "source_fixture_name": self.source_fixture_name,
            "source_construct_id": self.source_construct_id,
            "accepted_motif_id": self.accepted_motif_id,
            "s0026_lane": self.s0026_lane,
            "expected_outcome": self.expected_outcome,
            "selector_ids": list(self.selector_ids),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9LoweringPassFailControl:
        mapping = _require_mapping(value, field_name="pass_fail_control")
        return cls(
            control_role=_require_string(mapping.get("control_role"), field_name="control_role"),
            source_fixture_name=_require_string(
                mapping.get("source_fixture_name"),
                field_name="source_fixture_name",
            ),
            source_construct_id=_require_string(
                mapping.get("source_construct_id"),
                field_name="source_construct_id",
            ),
            accepted_motif_id=_require_string(
                mapping.get("accepted_motif_id"),
                field_name="accepted_motif_id",
            ),
            s0026_lane=_require_string(mapping.get("s0026_lane"), field_name="s0026_lane"),
            expected_outcome=_require_string(
                mapping.get("expected_outcome"),
                field_name="expected_outcome",
            ),
            selector_ids=_string_tuple(mapping.get("selector_ids", ()), field_name="selector_ids"),
        )


@dataclass(frozen=True)
class GRCL9LoweringManifestEntry:
    """One manifest entry mapping a reviewed motif family to GRCL-9 lowering."""

    entry_id: str
    phenomenon: str
    seed_family: str
    source_construct_kinds: tuple[str, ...]
    graph_preconditions: Mapping[str, Any]
    required_source_knobs: tuple[str, ...]
    lowering_carriers: tuple[str, ...]
    expected_telemetry: tuple[GRCL9TelemetryExpectation, ...]
    controls: tuple[GRCL9LoweringPassFailControl, ...]
    non_claims: tuple[str, ...] = GRCL9_BASE_NON_CLAIMS
    notes: str = ""

    def __post_init__(self) -> None:
        _validate_token(self.entry_id, field_name="entry_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        _validate_token(self.seed_family, field_name="seed_family")
        if not self.source_construct_kinds:
            raise ValueError("source_construct_kinds must not be empty")
        for construct_kind in self.source_construct_kinds:
            if construct_kind not in GRCL9_ACCEPTED_SOURCE_CONSTRUCT_KINDS:
                raise ValueError(f"unsupported source construct kind {construct_kind!r}")
        _require_mapping(self.graph_preconditions, field_name="graph_preconditions")
        if not self.required_source_knobs:
            raise ValueError("required_source_knobs must not be empty")
        for knob in self.required_source_knobs:
            _validate_token(knob, field_name="required_source_knobs[]")
        if not self.lowering_carriers:
            raise ValueError("lowering_carriers must not be empty")
        for carrier in self.lowering_carriers:
            _require_string(carrier, field_name="lowering_carriers[]")
        if not self.expected_telemetry:
            raise ValueError("expected_telemetry must not be empty")
        if not self.controls:
            raise ValueError("controls must not be empty")
        control_ids = [item.source_construct_id for item in self.controls]
        if len(control_ids) != len(set(control_ids)):
            raise ValueError("source_construct_id values must be unique per entry")
        for non_claim in self.non_claims:
            _validate_token(non_claim, field_name="non_claims[]")

    @property
    def accepted_motif_ids(self) -> tuple[str, ...]:
        return tuple(item.accepted_motif_id for item in self.controls)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "entry_id": self.entry_id,
            "phenomenon": self.phenomenon,
            "seed_family": self.seed_family,
            "source_construct_kinds": list(self.source_construct_kinds),
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "required_source_knobs": list(self.required_source_knobs),
            "lowering_carriers": list(self.lowering_carriers),
            "expected_telemetry": [item.to_mapping() for item in self.expected_telemetry],
            "controls": [item.to_mapping() for item in self.controls],
            "non_claims": list(self.non_claims),
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9LoweringManifestEntry:
        mapping = _require_mapping(value, field_name="lowering_manifest_entry")
        return cls(
            entry_id=_require_string(mapping.get("entry_id"), field_name="entry_id"),
            phenomenon=_require_string(mapping.get("phenomenon"), field_name="phenomenon"),
            seed_family=_require_string(mapping.get("seed_family"), field_name="seed_family"),
            source_construct_kinds=_string_tuple(
                mapping.get("source_construct_kinds", ()),
                field_name="source_construct_kinds",
            ),
            graph_preconditions=dict(
                _require_mapping(mapping.get("graph_preconditions", {}), field_name="graph_preconditions")
            ),
            required_source_knobs=_string_tuple(
                mapping.get("required_source_knobs", ()),
                field_name="required_source_knobs",
            ),
            lowering_carriers=_string_tuple(
                mapping.get("lowering_carriers", ()),
                field_name="lowering_carriers",
            ),
            expected_telemetry=tuple(
                GRCL9TelemetryExpectation.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("expected_telemetry", ()),
                    field_name="expected_telemetry",
                )
            ),
            controls=tuple(
                GRCL9LoweringPassFailControl.from_mapping(item)
                for item in _require_sequence(mapping.get("controls", ()), field_name="controls")
            ),
            non_claims=_string_tuple(
                mapping.get("non_claims", GRCL9_BASE_NON_CLAIMS),
                field_name="non_claims",
            ),
            notes=str(mapping.get("notes", "")),
        )


@dataclass(frozen=True)
class GRCL9LoweringManifest:
    """GRCL-9 lowering manifest rooted in the S0026 suitability handoff."""

    entries: tuple[GRCL9LoweringManifestEntry, ...]
    manifest_version: str = GRCL9_LOWERING_MANIFEST_VERSION
    source_schema_version: str = GRCL9_SOURCE_SCHEMA_VERSION
    source_catalog_path: str = (
        "outputs/grc9/phenomenology_discovery/sessions/S0026/"
        "grcl9_suitability_catalog.md"
    )
    output_root: str = "outputs/grcl9/lowering"

    def __post_init__(self) -> None:
        if self.manifest_version != GRCL9_LOWERING_MANIFEST_VERSION:
            raise ValueError(f"manifest_version must be {GRCL9_LOWERING_MANIFEST_VERSION!r}")
        if self.source_schema_version != GRCL9_SOURCE_SCHEMA_VERSION:
            raise ValueError(f"source_schema_version must be {GRCL9_SOURCE_SCHEMA_VERSION!r}")
        if not self.entries:
            raise ValueError("entries must not be empty")
        entry_ids = [item.entry_id for item in self.entries]
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("entry_id values must be unique")
        seed_families = [item.seed_family for item in self.entries]
        if len(seed_families) != len(set(seed_families)):
            raise ValueError("seed_family values must be unique")
        motif_ids = [motif_id for item in self.entries for motif_id in item.accepted_motif_ids]
        if len(motif_ids) != len(set(motif_ids)):
            raise ValueError("accepted_motif_id values must be unique")

    def by_entry_id(self) -> Mapping[str, GRCL9LoweringManifestEntry]:
        return {item.entry_id: item for item in self.entries}

    def by_seed_family(self) -> Mapping[str, GRCL9LoweringManifestEntry]:
        return {item.seed_family: item for item in self.entries}

    def accepted_motif_ids(self) -> tuple[str, ...]:
        return tuple(motif_id for item in self.entries for motif_id in item.accepted_motif_ids)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "source_schema_version": self.source_schema_version,
            "source_catalog_path": self.source_catalog_path,
            "output_root": self.output_root,
            "entries": [item.to_mapping() for item in self.entries],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9LoweringManifest:
        mapping = _require_mapping(value, field_name="lowering_manifest")
        return cls(
            manifest_version=_require_string(
                mapping.get("manifest_version", GRCL9_LOWERING_MANIFEST_VERSION),
                field_name="manifest_version",
            ),
            source_schema_version=_require_string(
                mapping.get("source_schema_version", GRCL9_SOURCE_SCHEMA_VERSION),
                field_name="source_schema_version",
            ),
            source_catalog_path=_require_string(
                mapping.get(
                    "source_catalog_path",
                    "outputs/grc9/phenomenology_discovery/sessions/S0026/"
                    "grcl9_suitability_catalog.md",
                ),
                field_name="source_catalog_path",
            ),
            output_root=_require_string(
                mapping.get("output_root", "outputs/grcl9/lowering"),
                field_name="output_root",
            ),
            entries=tuple(
                GRCL9LoweringManifestEntry.from_mapping(item)
                for item in _require_sequence(mapping.get("entries", ()), field_name="entries")
            ),
        )


def _expect(
    field_path: str,
    *,
    surface: str,
    predicate: str,
    expected_type: str,
    required: bool = True,
) -> GRCL9TelemetryExpectation:
    return GRCL9TelemetryExpectation(
        field_path=field_path,
        surface=surface,
        predicate=predicate,
        expected_type=expected_type,
        required=required,
    )


def _control(
    role: str,
    fixture: str,
    construct_id: str,
    motif_id: str,
    lane: str,
    expected_outcome: str,
    *selector_ids: str,
) -> GRCL9LoweringPassFailControl:
    return GRCL9LoweringPassFailControl(
        control_role=role,
        source_fixture_name=fixture,
        source_construct_id=construct_id,
        accepted_motif_id=motif_id,
        s0026_lane=lane,
        expected_outcome=expected_outcome,
        selector_ids=tuple(selector_ids),
    )


def _entry(
    *,
    entry_id: str,
    phenomenon: str,
    seed_family: str,
    source_construct_kinds: tuple[str, ...],
    graph_preconditions: Mapping[str, Any],
    required_source_knobs: tuple[str, ...],
    lowering_carriers: tuple[str, ...],
    expected_telemetry: tuple[GRCL9TelemetryExpectation, ...],
    controls: tuple[GRCL9LoweringPassFailControl, ...],
    notes: str,
) -> GRCL9LoweringManifestEntry:
    return GRCL9LoweringManifestEntry(
        entry_id=entry_id,
        phenomenon=phenomenon,
        seed_family=seed_family,
        source_construct_kinds=source_construct_kinds,
        graph_preconditions=graph_preconditions,
        required_source_knobs=required_source_knobs,
        lowering_carriers=lowering_carriers,
        expected_telemetry=expected_telemetry,
        controls=controls,
        notes=notes,
    )


def default_grcl9_lowering_manifest() -> GRCL9LoweringManifest:
    """Return the Revision 1 GRCL-9 lowering manifest."""

    common_carriers = (
        "extensions.grcl9",
        "node_payload.grcl9_source_construct_id",
        "edge_payload.grcl9_source_construct_id",
        "cached_quantities.grcl9_provenance",
        "cached_quantities.grcl9_motif_registry",
        "cached_quantities.grcl9_assembly_policy",
    )
    entries = (
        _entry(
            entry_id="grcl9_lowering_spark_column_proxy_v1",
            phenomenon="spark",
            seed_family="spark_column_proxy_emitter",
            source_construct_kinds=("spark_candidate_region", "column_proxy_profile"),
            graph_preconditions={
                "saturated_candidate_node": True,
                "target_column_diagnostic": "near_epsilon",
                "spark_gate_intent": "saturation_column_proxy",
            },
            required_source_knobs=(
                "candidate_id",
                "coherence_allocation",
                "neighbor_coherence_profile",
                "target_column",
                "spark_threshold",
                "spark_gate_intent",
            ),
            lowering_carriers=common_carriers
            + (
                "cached_quantities.grcl9_expected_saturated_node_ids",
                "cached_quantities.grcl9_expected_column_proxy_candidate_ids",
            ),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count",
                    surface="run_summary.json",
                    predicate="pass > 0 and fail == 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count",
                    surface="run_summary.json",
                    predicate="pass > 0 and fail == 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.spark_evidence.spark_kind",
                    surface="events.jsonl",
                    predicate="pass contains saturation_column_proxy",
                    expected_type="string",
                ),
            ),
            controls=(
                _control(
                    "pass_control",
                    "spark_column_proxy_eps_pass",
                    "spark_column_proxy_eps_pass",
                    "grc9-motif-s0006-spark-column-proxy-eps-pass",
                    "spark_column_proxy_eps_pass",
                    "column proxy spark evidence is observed",
                    "spark_column_proxy_count",
                ),
                _control(
                    "fail_control",
                    "spark_column_proxy_eps_fail",
                    "spark_column_proxy_eps_fail",
                    "grc9-motif-s0006-spark-column-proxy-eps-fail",
                    "spark_column_proxy_eps_fail",
                    "column proxy spark evidence is absent",
                    "spark_column_proxy_count",
                ),
            ),
            notes="Column-proxy source lowers diagnostic preconditions, not a spark event.",
        ),
        _entry(
            entry_id="grcl9_lowering_spark_instability_v1",
            phenomenon="spark",
            seed_family="spark_instability_emitter",
            source_construct_kinds=("spark_candidate_region", "instability_profile"),
            graph_preconditions={
                "saturated_candidate_node": True,
                "row_tensor_anisotropy": "controlled",
                "cut_support_proxy": "controlled",
                "spark_gate_intent": "saturation_instability",
            },
            required_source_knobs=(
                "candidate_id",
                "coherence_allocation",
                "row_anisotropy_profile",
                "support_cut_profile",
                "tau_instability",
                "spark_gate_intent",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9_expected_saturated_node_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max",
                    surface="run_summary.json",
                    predicate="pass >= fail",
                    expected_type="float",
                ),
                _expect(
                    "family_extensions.grc9.lifecycle_event_counts.spark_instability_count",
                    surface="run_summary.json",
                    predicate="pass > 0 and fail == 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.spark_evidence.instability_score",
                    surface="events.jsonl",
                    predicate="pass contains finite score",
                    expected_type="float",
                ),
            ),
            controls=(
                _control(
                    "pass_control",
                    "spark_instability_tau_pass",
                    "spark_instability_tau_pass",
                    "grc9-motif-s0006-spark-instability-tau-pass",
                    "spark_instability_tau_pass",
                    "instability spark evidence is observed",
                    "spark_instability_count",
                ),
                _control(
                    "fail_control",
                    "spark_instability_tau_fail",
                    "spark_instability_tau_fail",
                    "grc9-motif-s0006-spark-instability-tau-fail",
                    "spark_instability_tau_fail",
                    "instability spark evidence is absent",
                    "spark_instability_count",
                ),
            ),
            notes="Instability source lowers row tensor and cut/support geometry only.",
        ),
        _entry(
            entry_id="grcl9_lowering_expansion_refinement_v1",
            phenomenon="expansion",
            seed_family="spark_to_expansion_emitter",
            source_construct_kinds=("spark_candidate_region", "expansion_refinement_region"),
            graph_preconditions={
                "saturated_spark_capable_parent": True,
                "target_effective_degree": "declared",
                "boundary_reassignment": "column_preserving",
            },
            required_source_knobs=(
                "candidate_id",
                "target_effective_degree",
                "module_size_formula",
                "bond_weight_mode",
                "coherence_transfer_mode",
                "coherence_transfer_ratios",
            ),
            lowering_carriers=common_carriers
            + (
                "cached_quantities.grcl9_expected_saturated_node_ids",
                "cached_quantities.grcl9_bridge_edge_ids",
            ),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9.lifecycle_event_counts.expansion_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.expansion_summary.max_module_node_count",
                    surface="run_summary.json",
                    predicate="high >= low",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.expansion_evidence.target_effective_degree",
                    surface="events.jsonl",
                    predicate="matches source target",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.expansion_evidence.coherence_transfer_ratios",
                    surface="events.jsonl",
                    predicate="sum ~= 1",
                    expected_type="list[float]",
                ),
            ),
            controls=(
                _control(
                    "low_control",
                    "spark_to_expansion_d_eff_low",
                    "spark_to_expansion_d_eff_low",
                    "grc9-motif-s0006-spark-to-expansion-d-eff-low",
                    "spark_to_expansion_d_eff_low",
                    "lower D_eff expansion module is observed",
                    "expansion_module_size",
                ),
                _control(
                    "high_control",
                    "spark_to_expansion_d_eff_high",
                    "spark_to_expansion_d_eff_high",
                    "grc9-motif-s0006-spark-to-expansion-d-eff-high",
                    "spark_to_expansion_d_eff_high",
                    "higher D_eff expansion module is observed",
                    "expansion_module_size",
                ),
            ),
            notes="Expansion source preserves policy; runtime decides whether expansion occurs.",
        ),
        _entry(
            entry_id="grcl9_lowering_growth_pressure_v1",
            phenomenon="growth",
            seed_family="growth_pressure_emitter",
            source_construct_kinds=("growth_locus",),
            graph_preconditions={
                "inactive_parent_port": True,
                "outward_flux_pressure": "localized",
                "birth_rule": "outward_flux_pressure",
            },
            required_source_knobs=(
                "parent_id",
                "inactive_parent_port",
                "pressure_profile",
                "birth_rule",
                "lambda_birth",
            ),
            lowering_carriers=common_carriers,
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9.lifecycle_event_counts.growth_count",
                    surface="run_summary.json",
                    predicate="high >= low",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.growth_evidence.outward_flux_pressure",
                    surface="events.jsonl",
                    predicate="finite when growth event exists",
                    expected_type="float",
                ),
                _expect(
                    "family_extensions.grc9.growth_evidence.birth_probability",
                    surface="events.jsonl",
                    predicate="finite when emitted",
                    expected_type="float",
                    required=False,
                ),
                _expect(
                    "family_extensions.grc9.growth_summary.birth_probability_max",
                    surface="run_summary.json",
                    predicate="finite when emitted",
                    expected_type="float",
                    required=False,
                ),
            ),
            controls=(
                _control(
                    "high_control",
                    "growth_pressure_lambda_high",
                    "growth_pressure_lambda_high",
                    "grc9-motif-s0006-growth-pressure-lambda-high",
                    "growth_pressure_lambda_high",
                    "higher lambda birth pressure is observed",
                    "growth_count",
                ),
                _control(
                    "low_control",
                    "growth_pressure_lambda_low",
                    "growth_pressure_lambda_low",
                    "grc9-motif-s0006-growth-pressure-lambda-low",
                    "growth_pressure_lambda_low",
                    "lower lambda suppresses or reduces growth evidence",
                    "growth_count",
                ),
            ),
            notes="Growth source declares pressure structure and lambda, not a birth event.",
        ),
        _entry(
            entry_id="grcl9_lowering_post_expansion_fission_v1",
            phenomenon="fission",
            seed_family="post_expansion_fission_emitter",
            source_construct_kinds=("post_expansion_fission_geometry",),
            graph_preconditions={
                "two_sink_capable_regions": True,
                "separable_conductance_geometry": True,
                "minimum_basin_mass": "declared",
                "persistence_window": "declared",
            },
            required_source_knobs=(
                "module_region_id",
                "sink_region_a",
                "sink_region_b",
                "identity_fission_min_basin_mass",
                "identity_fission_persistence_delta",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9_bridge_edge_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count",
                    surface="run_summary.json",
                    predicate="pass > fail",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps",
                    surface="run_summary.json",
                    predicate="pass >= fail",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9.identity_abundance.basin_size_max",
                    surface="steps.jsonl",
                    predicate="supports min-mass comparison",
                    expected_type="int",
                ),
            ),
            controls=(
                _control(
                    "pass_control",
                    "post_expansion_fission_min_mass_pass",
                    "post_expansion_fission_min_mass_pass",
                    "grc9-motif-s0006-post-expansion-fission-min-mass-pass",
                    "post_expansion_fission_min_mass_pass",
                    "two sink-capable regions satisfy min-mass evidence",
                    "fission_confirmed_count",
                ),
                _control(
                    "fail_control",
                    "post_expansion_fission_min_mass_fail",
                    "post_expansion_fission_min_mass_fail",
                    "grc9-motif-s0006-post-expansion-fission-min-mass-fail",
                    "post_expansion_fission_min_mass_fail",
                    "two sink-capable regions fail min-mass evidence",
                    "fission_confirmed_count",
                ),
            ),
            notes=(
                "Fission source lowers two sink-capable regions with separable "
                "conductance geometry; it does not claim runtime-computed basins."
            ),
        ),
    )
    manifest = GRCL9LoweringManifest(entries=entries)
    if set(manifest.accepted_motif_ids()) != _EXPECTED_S0026_ACCEPTED_MOTIF_IDS:
        raise AssertionError("default manifest no longer covers the expected S0026 motifs")
    return manifest
