"""Lowering manifest contract for GRCL-9V3 Revision 1."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


GRCL9V3_LOWERING_MANIFEST_VERSION = "grcl9v3_lowering_manifest_v1"
GRCL9V3_SOURCE_SCHEMA_VERSION = "grcl9v3.source.v1"

GRCL9V3_ACCEPTED_SOURCE_CONSTRUCT_KINDS = frozenset(
    {
        "hybrid_spark_region",
        "row_basis_hessian_profile",
        "hybrid_tensor_profile",
        "column_proxy_fallback_profile",
        "expansion_refinement_region",
        "choice_collapse_region",
        "growth_locus",
        "transport_rerouting_region",
        "appendix_e_division_region",
        "quiescent_hybrid_region",
    }
)
GRCL9V3_OWNERSHIP_TAGS = frozenset(
    {
        "grc9_mechanical",
        "grcv3_semantic",
        "grc9v3_hybrid",
        "shared_runtime",
    }
)
GRCL9V3_CONTROL_ROLES = frozenset(
    {
        "positive_control",
        "negative_control",
        "no_event_control",
        "complex_control",
        "perturbation_control",
    }
)
GRCL9V3_BASE_NON_CLAIMS = (
    "no_grcl9v3_lowering_result_claim",
    "no_runtime_event_claim",
    "no_lorentzian_causal_layer_claim",
    "no_visual_only_promotion",
    "runtime_evidence_required",
)
GRCL9V3_TELEMETRY_FIELD_PREFIX = "family_extensions.grc9v3."
GRCL9V3_LOWERING_CARRIER_PREFIXES = (
    "extensions.grcl9v3",
    "node_payload.grcl9v3_",
    "edge_payload.grcl9v3_",
    "cached_quantities.grcl9v3_",
)

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_REVIEWED_MOTIF_ID_RE = re.compile(r"^grc9v3-motif-[a-z0-9]+(?:-[a-z0-9]+)*$")
_FORBIDDEN_RUNTIME_RESULT_KEYS = frozenset(
    {
        "event_counts_by_kind",
        "event_history",
        "events",
        "spark_happened",
        "expansion_happened",
        "choice_happened",
        "collapse_happened",
        "growth_happened",
        "daughter_sink_confirmed",
        "solved_flux",
        "solved_tensor",
        "solved_diagnostic",
        "observed_evidence_fields",
    }
)
_EXPECTED_SOURCE_CANDIDATE_MOTIF_IDS = frozenset(
    {
        "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
        "grc9v3-motif-s0006-spark-to-expansion-positive-control",
        "grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
        "grc9v3-motif-s0006-choice-collapse-positive-control",
        "grc9v3-motif-s0006-growth-pressure-positive-control",
        "grc9v3-motif-s0008-complex-spark-expansion-hierarchy-complex-control",
        "grc9v3-motif-s0008-complex-spark-expansion-choice-collapse-complex-control",
        "grc9v3-motif-s0008-complex-expansion-growth-budget-coarse-complex-control",
    }
)
_EXPECTED_FUTURE_VOCABULARY_MOTIF_IDS = frozenset(
    {
        "grc9v3-motif-s0006-hybrid-spark-gate-negative-control",
        "grc9v3-motif-s0006-spark-to-expansion-negative-control",
        "grc9v3-motif-s0006-appendix-e-cell-division-negative-control",
        "grc9v3-motif-s0006-choice-collapse-negative-control",
        "grc9v3-motif-s0006-growth-pressure-negative-control",
        "grc9v3-motif-s0006-budget-preservation-negative-control",
        "grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
        "grc9v3-motif-s0006-transport-basin-rerouting-negative-control",
        "grc9v3-motif-s0006-coarse-cache-invalidation-negative-control",
        "grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
        "grc9v3-motif-s0008-complex-spark-choice-no-saturation-perturbation-perturbation-control",
        "grc9v3-motif-s0008-complex-growth-low-birth-perturbation-perturbation-control",
    }
)
_EXPECTED_RUNTIME_ONLY_MOTIF_IDS = frozenset(
    {
        "grc9v3-motif-s0006-budget-preservation-positive-control",
        "grc9v3-motif-s0006-hessian-backend-comparison-baseline-control",
        "grc9v3-motif-s0006-hessian-backend-comparison-positive-control",
        "grc9v3-motif-s0006-coarse-cache-invalidation-positive-control",
        "grc9v3-motif-s0008-complex-hessian-row-basis-complex-control",
        "grc9v3-motif-s0008-complex-hessian-weighted-least-squares-complex-control",
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


def _validate_reviewed_motif_id(value: str, *, field_name: str) -> None:
    _require_string(value, field_name=field_name)
    if not _REVIEWED_MOTIF_ID_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use reviewed GRC9V3 motif-id format")


def _reject_runtime_result_keys(value: Any, *, field_name: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text in _FORBIDDEN_RUNTIME_RESULT_KEYS:
                raise ValueError(
                    f"{field_name} must not contain runtime-result key {key_text!r}"
                )
            _reject_runtime_result_keys(item, field_name=f"{field_name}.{key_text}")
    elif isinstance(value, Sequence) and not isinstance(value, str):
        for index, item in enumerate(value):
            _reject_runtime_result_keys(item, field_name=f"{field_name}[{index}]")


def _validate_lowering_carrier(value: str) -> None:
    _require_string(value, field_name="lowering_carriers[]")
    if not any(value == prefix or value.startswith(prefix) for prefix in GRCL9V3_LOWERING_CARRIER_PREFIXES):
        raise ValueError("lowering_carriers must use GRCL-9V3 carrier namespaces")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


def _validate_grc9v3_field_path(field_path: str) -> None:
    if "event_counts_by_kind" in field_path:
        raise ValueError("telemetry field paths must not use event_counts_by_kind")
    if not field_path.startswith(GRCL9V3_TELEMETRY_FIELD_PREFIX):
        raise ValueError(
            f"telemetry field paths must use {GRCL9V3_TELEMETRY_FIELD_PREFIX}*"
        )


@dataclass(frozen=True)
class GRCL9V3TelemetryExpectation:
    """Field-backed telemetry expectation for a lowered GRCL-9V3 fixture."""

    field_path: str
    surface: str
    predicate: str
    expected_type: str | None = None
    required: bool = True

    def __post_init__(self) -> None:
        _require_string(self.field_path, field_name="field_path")
        _validate_grc9v3_field_path(self.field_path)
        _require_string(self.surface, field_name="surface")
        _require_string(self.predicate, field_name="predicate")
        _optional_string(self.expected_type, field_name="expected_type")
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
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3TelemetryExpectation:
        mapping = _require_mapping(value, field_name="telemetry_expectation")
        return cls(
            field_path=_require_string(mapping.get("field_path"), field_name="field_path"),
            surface=_require_string(mapping.get("surface"), field_name="surface"),
            predicate=_require_string(mapping.get("predicate"), field_name="predicate"),
            expected_type=_optional_string(
                mapping.get("expected_type"),
                field_name="expected_type",
            ),
            required=_require_bool(mapping.get("required", True), field_name="required"),
        )


@dataclass(frozen=True)
class GRCL9V3LoweringControl:
    """Source fixture control linked to a reviewed S0014 handoff motif."""

    control_role: str
    source_fixture_name: str
    source_construct_id: str
    reviewed_motif_id: str
    s0014_lane: str
    expected_outcome: str
    selector_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_token(self.control_role, field_name="control_role")
        if self.control_role not in GRCL9V3_CONTROL_ROLES:
            raise ValueError(
                f"control_role must be one of {tuple(sorted(GRCL9V3_CONTROL_ROLES))}"
            )
        _validate_token(self.source_fixture_name, field_name="source_fixture_name")
        _validate_token(self.source_construct_id, field_name="source_construct_id")
        _validate_reviewed_motif_id(self.reviewed_motif_id, field_name="reviewed_motif_id")
        _validate_token(self.s0014_lane, field_name="s0014_lane")
        _require_string(self.expected_outcome, field_name="expected_outcome")
        for selector_id in self.selector_ids:
            _validate_token(selector_id, field_name="selector_ids[]")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "control_role": self.control_role,
            "source_fixture_name": self.source_fixture_name,
            "source_construct_id": self.source_construct_id,
            "reviewed_motif_id": self.reviewed_motif_id,
            "s0014_lane": self.s0014_lane,
            "expected_outcome": self.expected_outcome,
            "selector_ids": list(self.selector_ids),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3LoweringControl:
        mapping = _require_mapping(value, field_name="lowering_control")
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
            reviewed_motif_id=_require_string(
                mapping.get("reviewed_motif_id"),
                field_name="reviewed_motif_id",
            ),
            s0014_lane=_require_string(mapping.get("s0014_lane"), field_name="s0014_lane"),
            expected_outcome=_require_string(
                mapping.get("expected_outcome"),
                field_name="expected_outcome",
            ),
            selector_ids=_string_tuple(mapping.get("selector_ids", ()), field_name="selector_ids"),
        )


@dataclass(frozen=True)
class GRCL9V3LoweringManifestEntry:
    """One manifest entry mapping S0014 source candidates to GRCL-9V3 lowering."""

    entry_id: str
    phenomenon: str
    source_construct_kinds: tuple[str, ...]
    ownership_tags: tuple[str, ...]
    graph_preconditions: Mapping[str, Any]
    required_source_knobs: tuple[str, ...]
    lowering_carriers: tuple[str, ...]
    expected_telemetry: tuple[GRCL9V3TelemetryExpectation, ...]
    controls: tuple[GRCL9V3LoweringControl, ...]
    non_claims: tuple[str, ...] = GRCL9V3_BASE_NON_CLAIMS
    notes: str = ""

    def __post_init__(self) -> None:
        _validate_token(self.entry_id, field_name="entry_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        if not self.source_construct_kinds:
            raise ValueError("source_construct_kinds must not be empty")
        for construct_kind in self.source_construct_kinds:
            if construct_kind not in GRCL9V3_ACCEPTED_SOURCE_CONSTRUCT_KINDS:
                raise ValueError(f"unsupported source construct kind {construct_kind!r}")
        if not self.ownership_tags:
            raise ValueError("ownership_tags must not be empty")
        for ownership in self.ownership_tags:
            if ownership not in GRCL9V3_OWNERSHIP_TAGS:
                raise ValueError(f"unsupported ownership tag {ownership!r}")
        _require_mapping(self.graph_preconditions, field_name="graph_preconditions")
        _reject_runtime_result_keys(self.graph_preconditions, field_name="graph_preconditions")
        if not self.required_source_knobs:
            raise ValueError("required_source_knobs must not be empty")
        for knob in self.required_source_knobs:
            _validate_token(knob, field_name="required_source_knobs[]")
        if not self.lowering_carriers:
            raise ValueError("lowering_carriers must not be empty")
        for carrier in self.lowering_carriers:
            _validate_lowering_carrier(carrier)
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
    def reviewed_motif_ids(self) -> tuple[str, ...]:
        return tuple(item.reviewed_motif_id for item in self.controls)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "entry_id": self.entry_id,
            "phenomenon": self.phenomenon,
            "source_construct_kinds": list(self.source_construct_kinds),
            "ownership_tags": list(self.ownership_tags),
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "required_source_knobs": list(self.required_source_knobs),
            "lowering_carriers": list(self.lowering_carriers),
            "expected_telemetry": [item.to_mapping() for item in self.expected_telemetry],
            "controls": [item.to_mapping() for item in self.controls],
            "non_claims": list(self.non_claims),
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3LoweringManifestEntry:
        mapping = _require_mapping(value, field_name="lowering_manifest_entry")
        return cls(
            entry_id=_require_string(mapping.get("entry_id"), field_name="entry_id"),
            phenomenon=_require_string(mapping.get("phenomenon"), field_name="phenomenon"),
            source_construct_kinds=_string_tuple(
                mapping.get("source_construct_kinds", ()),
                field_name="source_construct_kinds",
            ),
            ownership_tags=_string_tuple(
                mapping.get("ownership_tags", ()),
                field_name="ownership_tags",
            ),
            graph_preconditions=dict(
                _require_mapping(
                    mapping.get("graph_preconditions", {}),
                    field_name="graph_preconditions",
                )
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
                GRCL9V3TelemetryExpectation.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("expected_telemetry", ()),
                    field_name="expected_telemetry",
                )
            ),
            controls=tuple(
                GRCL9V3LoweringControl.from_mapping(item)
                for item in _require_sequence(mapping.get("controls", ()), field_name="controls")
            ),
            non_claims=_string_tuple(
                mapping.get("non_claims", GRCL9V3_BASE_NON_CLAIMS),
                field_name="non_claims",
            ),
            notes=str(mapping.get("notes", "")),
        )


@dataclass(frozen=True)
class GRCL9V3FutureVocabularyRecord:
    """S0014 record that is useful but needs source vocabulary before lowering."""

    motif_id: str
    phenomenon: str
    lane_name: str
    catalog_category: str
    required_vocabulary: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        _validate_reviewed_motif_id(self.motif_id, field_name="motif_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        _validate_token(self.lane_name, field_name="lane_name")
        _validate_token(self.catalog_category, field_name="catalog_category")
        if not self.required_vocabulary:
            raise ValueError("required_vocabulary must not be empty")
        for item in self.required_vocabulary:
            _require_string(item, field_name="required_vocabulary[]")
        _require_string(self.notes, field_name="notes")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "phenomenon": self.phenomenon,
            "lane_name": self.lane_name,
            "catalog_category": self.catalog_category,
            "required_vocabulary": list(self.required_vocabulary),
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3FutureVocabularyRecord:
        mapping = _require_mapping(value, field_name="future_vocabulary_record")
        return cls(
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            phenomenon=_require_string(mapping.get("phenomenon"), field_name="phenomenon"),
            lane_name=_require_string(mapping.get("lane_name"), field_name="lane_name"),
            catalog_category=_require_string(
                mapping.get("catalog_category"),
                field_name="catalog_category",
            ),
            required_vocabulary=_string_tuple(
                mapping.get("required_vocabulary", ()),
                field_name="required_vocabulary",
            ),
            notes=_require_string(mapping.get("notes"), field_name="notes"),
        )


@dataclass(frozen=True)
class GRCL9V3RuntimeOnlyExclusion:
    """S0014 record intentionally excluded from Revision 1 source ontology."""

    motif_id: str
    phenomenon: str
    lane_name: str
    reason: str

    def __post_init__(self) -> None:
        _validate_reviewed_motif_id(self.motif_id, field_name="motif_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        _validate_token(self.lane_name, field_name="lane_name")
        _require_string(self.reason, field_name="reason")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "phenomenon": self.phenomenon,
            "lane_name": self.lane_name,
            "reason": self.reason,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3RuntimeOnlyExclusion:
        mapping = _require_mapping(value, field_name="runtime_only_exclusion")
        return cls(
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            phenomenon=_require_string(mapping.get("phenomenon"), field_name="phenomenon"),
            lane_name=_require_string(mapping.get("lane_name"), field_name="lane_name"),
            reason=_require_string(mapping.get("reason"), field_name="reason"),
        )


@dataclass(frozen=True)
class GRCL9V3LoweringManifest:
    """GRCL-9V3 lowering manifest rooted in the S0014 source handoff."""

    entries: tuple[GRCL9V3LoweringManifestEntry, ...]
    future_vocabulary_records: tuple[GRCL9V3FutureVocabularyRecord, ...]
    runtime_only_exclusions: tuple[GRCL9V3RuntimeOnlyExclusion, ...]
    manifest_version: str = GRCL9V3_LOWERING_MANIFEST_VERSION
    source_schema_version: str = GRCL9V3_SOURCE_SCHEMA_VERSION
    source_handoff_path: str = (
        "outputs/grc9v3/phenomenology_discovery/sessions/S0014/"
        "source_language_handoff.json"
    )
    output_root: str = "outputs/grcl9v3/lowering"

    def __post_init__(self) -> None:
        if self.manifest_version != GRCL9V3_LOWERING_MANIFEST_VERSION:
            raise ValueError(
                f"manifest_version must be {GRCL9V3_LOWERING_MANIFEST_VERSION!r}"
            )
        if self.source_schema_version != GRCL9V3_SOURCE_SCHEMA_VERSION:
            raise ValueError(f"source_schema_version must be {GRCL9V3_SOURCE_SCHEMA_VERSION!r}")
        if not self.entries:
            raise ValueError("entries must not be empty")
        entry_ids = [item.entry_id for item in self.entries]
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("entry_id values must be unique")
        motif_ids = self.source_candidate_motif_ids()
        if len(motif_ids) != len(set(motif_ids)):
            raise ValueError("reviewed_motif_id values must be unique")
        future_ids = [item.motif_id for item in self.future_vocabulary_records]
        if len(future_ids) != len(set(future_ids)):
            raise ValueError("future vocabulary motif_id values must be unique")
        runtime_ids = [item.motif_id for item in self.runtime_only_exclusions]
        if len(runtime_ids) != len(set(runtime_ids)):
            raise ValueError("runtime-only motif_id values must be unique")
        overlap = set(motif_ids) & set(future_ids) | set(motif_ids) & set(runtime_ids) | set(future_ids) & set(runtime_ids)
        if overlap:
            raise ValueError("motif ids must not overlap across manifest dispositions")

    def by_entry_id(self) -> Mapping[str, GRCL9V3LoweringManifestEntry]:
        return {item.entry_id: item for item in self.entries}

    def source_candidate_motif_ids(self) -> tuple[str, ...]:
        return tuple(motif_id for item in self.entries for motif_id in item.reviewed_motif_ids)

    def future_vocabulary_motif_ids(self) -> tuple[str, ...]:
        return tuple(item.motif_id for item in self.future_vocabulary_records)

    def runtime_only_motif_ids(self) -> tuple[str, ...]:
        return tuple(item.motif_id for item in self.runtime_only_exclusions)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "source_schema_version": self.source_schema_version,
            "source_handoff_path": self.source_handoff_path,
            "output_root": self.output_root,
            "entries": [item.to_mapping() for item in self.entries],
            "future_vocabulary_records": [
                item.to_mapping() for item in self.future_vocabulary_records
            ],
            "runtime_only_exclusions": [
                item.to_mapping() for item in self.runtime_only_exclusions
            ],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRCL9V3LoweringManifest:
        mapping = _require_mapping(value, field_name="lowering_manifest")
        return cls(
            manifest_version=_require_string(
                mapping.get("manifest_version", GRCL9V3_LOWERING_MANIFEST_VERSION),
                field_name="manifest_version",
            ),
            source_schema_version=_require_string(
                mapping.get("source_schema_version", GRCL9V3_SOURCE_SCHEMA_VERSION),
                field_name="source_schema_version",
            ),
            source_handoff_path=_require_string(
                mapping.get(
                    "source_handoff_path",
                    "outputs/grc9v3/phenomenology_discovery/sessions/S0014/"
                    "source_language_handoff.json",
                ),
                field_name="source_handoff_path",
            ),
            output_root=_require_string(
                mapping.get("output_root", "outputs/grcl9v3/lowering"),
                field_name="output_root",
            ),
            entries=tuple(
                GRCL9V3LoweringManifestEntry.from_mapping(item)
                for item in _require_sequence(mapping.get("entries", ()), field_name="entries")
            ),
            future_vocabulary_records=tuple(
                GRCL9V3FutureVocabularyRecord.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("future_vocabulary_records", ()),
                    field_name="future_vocabulary_records",
                )
            ),
            runtime_only_exclusions=tuple(
                GRCL9V3RuntimeOnlyExclusion.from_mapping(item)
                for item in _require_sequence(
                    mapping.get("runtime_only_exclusions", ()),
                    field_name="runtime_only_exclusions",
                )
            ),
        )


def _expect(
    field_path: str,
    *,
    surface: str,
    predicate: str,
    expected_type: str,
    required: bool = True,
) -> GRCL9V3TelemetryExpectation:
    return GRCL9V3TelemetryExpectation(
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
) -> GRCL9V3LoweringControl:
    return GRCL9V3LoweringControl(
        control_role=role,
        source_fixture_name=fixture,
        source_construct_id=construct_id,
        reviewed_motif_id=motif_id,
        s0014_lane=lane,
        expected_outcome=expected_outcome,
        selector_ids=tuple(selector_ids),
    )


def _entry(
    *,
    entry_id: str,
    phenomenon: str,
    source_construct_kinds: tuple[str, ...],
    ownership_tags: tuple[str, ...],
    graph_preconditions: Mapping[str, Any],
    required_source_knobs: tuple[str, ...],
    lowering_carriers: tuple[str, ...],
    expected_telemetry: tuple[GRCL9V3TelemetryExpectation, ...],
    controls: tuple[GRCL9V3LoweringControl, ...],
    notes: str,
) -> GRCL9V3LoweringManifestEntry:
    return GRCL9V3LoweringManifestEntry(
        entry_id=entry_id,
        phenomenon=phenomenon,
        source_construct_kinds=source_construct_kinds,
        ownership_tags=ownership_tags,
        graph_preconditions=graph_preconditions,
        required_source_knobs=required_source_knobs,
        lowering_carriers=lowering_carriers,
        expected_telemetry=expected_telemetry,
        controls=controls,
        notes=notes,
    )


def _future(
    motif_id: str,
    phenomenon: str,
    lane_name: str,
    catalog_category: str,
    required_vocabulary: tuple[str, ...],
    notes: str,
) -> GRCL9V3FutureVocabularyRecord:
    return GRCL9V3FutureVocabularyRecord(
        motif_id=motif_id,
        phenomenon=phenomenon,
        lane_name=lane_name,
        catalog_category=catalog_category,
        required_vocabulary=required_vocabulary,
        notes=notes,
    )


def _runtime_only(
    motif_id: str,
    phenomenon: str,
    lane_name: str,
    reason: str,
) -> GRCL9V3RuntimeOnlyExclusion:
    return GRCL9V3RuntimeOnlyExclusion(
        motif_id=motif_id,
        phenomenon=phenomenon,
        lane_name=lane_name,
        reason=reason,
    )


def default_grcl9v3_lowering_manifest() -> GRCL9V3LoweringManifest:
    """Return the Revision 1 GRCL-9V3 lowering manifest."""

    common_carriers = (
        "extensions.grcl9v3",
        "node_payload.grcl9v3_construct_id",
        "edge_payload.grcl9v3_construct_id",
        "cached_quantities.grcl9v3_provenance",
        "cached_quantities.grcl9v3_motif_registry",
        "cached_quantities.grcl9v3_assembly_policy",
    )
    entries = (
        _entry(
            entry_id="grcl9v3_lowering_hybrid_spark_gate_v1",
            phenomenon="hybrid_spark_gate",
            source_construct_kinds=(
                "hybrid_spark_region",
                "row_basis_hessian_profile",
                "hybrid_tensor_profile",
                "column_proxy_fallback_profile",
            ),
            ownership_tags=("grc9v3_hybrid", "grcv3_semantic", "grc9_mechanical"),
            graph_preconditions={
                "saturated_identity_region": True,
                "row_basis_gate": "structurally_plausible",
                "column_proxy_fallback": "recorded",
            },
            required_source_knobs=(
                "candidate_region_id",
                "saturation_profile",
                "hessian_gate_profile",
                "tensor_profile",
                "spark_threshold",
            ),
            lowering_carriers=common_carriers
            + (
                "cached_quantities.grcl9v3_expected_saturated_node_ids",
                "cached_quantities.grcl9v3_expected_tensor_hotspot_node_ids",
            ),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_candidate_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_completed_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.hybrid_spark_state",
                    surface="steps.jsonl",
                    predicate="available",
                    expected_type="object",
                ),
                _expect(
                    "family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean",
                    surface="steps.jsonl",
                    predicate="finite",
                    expected_type="float",
                ),
            ),
            controls=(
                _control(
                    "positive_control",
                    "hybrid_spark_gate_positive_control",
                    "hybrid_spark_gate_positive_control",
                    "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
                    "hybrid_spark_gate_positive_control",
                    "hybrid spark candidate and completion evidence are observed",
                    "hybrid_spark_events",
                    "hybrid_tensor_available",
                ),
            ),
            notes="Source declares hybrid spark preconditions; runtime decides event outcome.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_spark_to_expansion_v1",
            phenomenon="spark_to_expansion",
            source_construct_kinds=(
                "hybrid_spark_region",
                "expansion_refinement_region",
            ),
            ownership_tags=("grc9v3_hybrid", "grc9_mechanical"),
            graph_preconditions={
                "saturated_refinement_parent": True,
                "effective_degree_target": "declared",
                "expansion_policy": "declared",
            },
            required_source_knobs=(
                "candidate_region_id",
                "target_effective_degree",
                "expansion_distribution_mode",
                "coherence_transfer_ratios",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_saturated_node_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_mechanical_expansion_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.expansion_summary",
                    surface="run_summary.json",
                    predicate="available",
                    expected_type="object",
                ),
                _expect(
                    "family_extensions.grc9v3.hierarchy_state",
                    surface="steps.jsonl",
                    predicate="available after expansion",
                    expected_type="object",
                ),
            ),
            controls=(
                _control(
                    "positive_control",
                    "spark_to_expansion_positive_control",
                    "spark_to_expansion_positive_control",
                    "grc9v3-motif-s0006-spark-to-expansion-positive-control",
                    "spark_to_expansion_positive_control",
                    "spark-to-expansion event sequence is observed",
                    "hybrid_expansion_events",
                ),
            ),
            notes="Expansion source preserves policy and graph preconditions, not event history.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_appendix_e_cell_division_v1",
            phenomenon="appendix_e_cell_division",
            source_construct_kinds=(
                "hybrid_spark_region",
                "expansion_refinement_region",
                "appendix_e_division_region",
            ),
            ownership_tags=("grc9v3_hybrid", "grc9_mechanical", "grcv3_semantic"),
            graph_preconditions={
                "parent_region": "spark_capable",
                "daughter_candidate_regions": 2,
                "module_basin_support": "declared",
            },
            required_source_knobs=(
                "parent_region_id",
                "daughter_region_a",
                "daughter_region_b",
                "target_effective_degree",
                "module_basin_support",
            ),
            lowering_carriers=common_carriers
            + (
                "cached_quantities.grcl9v3_expected_appendix_e_region_ids",
                "cached_quantities.grcl9v3_bridge_edge_ids",
            ),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.representative_appendix_e_summary",
                    surface="run_summary.json",
                    predicate="available for Appendix E fixture",
                    expected_type="object",
                ),
                _expect(
                    "family_extensions.grc9v3.hierarchy_state",
                    surface="steps.jsonl",
                    predicate="child link evidence available",
                    expected_type="object",
                ),
                _expect(
                    "family_extensions.grc9v3.final_identity_basin_summary",
                    surface="run_summary.json",
                    predicate="daughter sink evidence available",
                    expected_type="object",
                ),
            ),
            controls=(
                _control(
                    "positive_control",
                    "appendix_e_cell_division_positive_control",
                    "appendix_e_cell_division_positive_control",
                    "grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
                    "appendix_e_cell_division_positive_control",
                    "Appendix E representative division evidence is observed",
                    "appendix_e_summary",
                ),
            ),
            notes="Source declares daughter candidate geometry; confirmation remains runtime evidence.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_choice_collapse_v1",
            phenomenon="choice_collapse",
            source_construct_kinds=("choice_collapse_region",),
            ownership_tags=("grcv3_semantic", "grc9v3_hybrid"),
            graph_preconditions={
                "competing_basin_pair": True,
                "collapse_target_region": "declared",
                "compatibility_policy": "declared",
            },
            required_source_knobs=(
                "choice_region_id",
                "basin_region_a",
                "basin_region_b",
                "collapse_target_region",
                "compatibility_profile",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_choice_region_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.choice_detected_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.collapse_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.choice_collapse",
                    surface="steps.jsonl",
                    predicate="available",
                    expected_type="object",
                ),
            ),
            controls=(
                _control(
                    "positive_control",
                    "choice_collapse_positive_control",
                    "choice_collapse_positive_control",
                    "grc9v3-motif-s0006-choice-collapse-positive-control",
                    "choice_collapse_positive_control",
                    "choice and collapse telemetry evidence is observed",
                    "choice_collapse_events",
                ),
            ),
            notes="Source declares Morse-style basin competition, not a collapse result.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_growth_pressure_v1",
            phenomenon="growth_pressure",
            source_construct_kinds=("growth_locus",),
            ownership_tags=("grc9_mechanical", "grc9v3_hybrid"),
            graph_preconditions={
                "inactive_boundary_port": True,
                "outward_flux_pressure": "localized",
                "lambda_birth": "declared",
            },
            required_source_knobs=(
                "parent_region_id",
                "inactive_parent_port",
                "outward_pressure_profile",
                "lambda_birth",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_growth_locus_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.growth_count",
                    surface="run_summary.json",
                    predicate="> 0 for pass fixture",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.growth_state",
                    surface="steps.jsonl",
                    predicate="available",
                    expected_type="object",
                ),
                _expect(
                    "family_extensions.grc9v3.transport.flux_abs_sum",
                    surface="steps.jsonl",
                    predicate="finite",
                    expected_type="float",
                ),
            ),
            controls=(
                _control(
                    "positive_control",
                    "growth_pressure_positive_control",
                    "growth_pressure_positive_control",
                    "grc9v3-motif-s0006-growth-pressure-positive-control",
                    "growth_pressure_positive_control",
                    "growth event evidence is observed",
                    "growth_events",
                ),
            ),
            notes="Growth source declares inactive-port pressure; runtime computes birth.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_complex_spark_expansion_hierarchy_v1",
            phenomenon="complex_spark_expansion_hierarchy_complex_control",
            source_construct_kinds=(
                "hybrid_spark_region",
                "expansion_refinement_region",
                "appendix_e_division_region",
            ),
            ownership_tags=("grc9v3_hybrid", "grc9_mechanical", "grcv3_semantic"),
            graph_preconditions={
                "connected_multi_stage_graph": True,
                "spark_expansion_hierarchy_chain": "declared",
            },
            required_source_knobs=(
                "parent_region_id",
                "target_effective_degree",
                "hierarchy_region_profile",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_appendix_e_region_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_spark_completed_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.hierarchy_state",
                    surface="steps.jsonl",
                    predicate="child link evidence available",
                    expected_type="object",
                ),
            ),
            controls=(
                _control(
                    "complex_control",
                    "complex_spark_expansion_hierarchy_complex_control",
                    "complex_spark_expansion_hierarchy_complex_control",
                    "grc9v3-motif-s0008-complex-spark-expansion-hierarchy-complex-control",
                    "complex_spark_expansion_hierarchy_complex_control",
                    "connected spark, expansion, and hierarchy evidence is observed",
                    "complex_hierarchy_sequence",
                ),
            ),
            notes="Complex source candidate combines simpler source constructs in one graph.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_complex_spark_expansion_choice_collapse_v1",
            phenomenon="complex_spark_expansion_choice_collapse_complex_control",
            source_construct_kinds=(
                "hybrid_spark_region",
                "expansion_refinement_region",
                "choice_collapse_region",
            ),
            ownership_tags=("grc9v3_hybrid", "grc9_mechanical", "grcv3_semantic"),
            graph_preconditions={
                "connected_multi_stage_graph": True,
                "choice_after_expansion": "declared",
            },
            required_source_knobs=(
                "parent_region_id",
                "target_effective_degree",
                "choice_region_id",
                "collapse_target_region",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_choice_region_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_mechanical_expansion_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.choice_detected_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.collapse_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
            ),
            controls=(
                _control(
                    "complex_control",
                    "complex_spark_expansion_choice_collapse_complex_control",
                    "complex_spark_expansion_choice_collapse_complex_control",
                    "grc9v3-motif-s0008-complex-spark-expansion-choice-collapse-complex-control",
                    "complex_spark_expansion_choice_collapse_complex_control",
                    "connected spark, expansion, choice, and collapse evidence is observed",
                    "complex_choice_collapse_sequence",
                ),
            ),
            notes="Complex source candidate tests interaction between refinement and collapse geometry.",
        ),
        _entry(
            entry_id="grcl9v3_lowering_complex_expansion_growth_budget_coarse_v1",
            phenomenon="complex_expansion_growth_budget_coarse_complex_control",
            source_construct_kinds=(
                "hybrid_spark_region",
                "expansion_refinement_region",
                "growth_locus",
            ),
            ownership_tags=("grc9v3_hybrid", "grc9_mechanical", "shared_runtime"),
            graph_preconditions={
                "connected_multi_stage_graph": True,
                "growth_lobe_after_expansion": "declared",
                "budget_and_coarse": "runtime_diagnostics_only",
            },
            required_source_knobs=(
                "parent_region_id",
                "target_effective_degree",
                "growth_locus_id",
                "lambda_birth",
            ),
            lowering_carriers=common_carriers
            + ("cached_quantities.grcl9v3_expected_growth_locus_ids",),
            expected_telemetry=(
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.hybrid_mechanical_expansion_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.lifecycle_event_counts.growth_count",
                    surface="run_summary.json",
                    predicate="> 0",
                    expected_type="int",
                ),
                _expect(
                    "family_extensions.grc9v3.budget_correction.budget_error",
                    surface="run_summary.json",
                    predicate="near zero after runtime correction",
                    expected_type="float",
                ),
                _expect(
                    "family_extensions.grc9v3.coarse_cache.coarse_cache_invalidated",
                    surface="steps.jsonl",
                    predicate="observed as runtime diagnostic",
                    expected_type="bool",
                    required=False,
                ),
            ),
            controls=(
                _control(
                    "complex_control",
                    "complex_expansion_growth_budget_coarse_complex_control",
                    "complex_expansion_growth_budget_coarse_complex_control",
                    "grc9v3-motif-s0008-complex-expansion-growth-budget-coarse-complex-control",
                    "complex_expansion_growth_budget_coarse_complex_control",
                    "connected expansion and growth evidence is observed; budget/coarse remain diagnostics",
                    "complex_growth_sequence",
                ),
            ),
            notes="Budget and coarse-cache signals remain runtime diagnostics, not source constructs.",
        ),
    )
    future_records = (
        _future(
            "grc9v3-motif-s0006-hybrid-spark-gate-negative-control",
            "hybrid_spark_gate",
            "hybrid_spark_gate_negative_control",
            "negative_control",
            ("source-level control role", "absence-of-event expectation"),
            "Negative control needs explicit source pass/fail vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-spark-to-expansion-negative-control",
            "spark_to_expansion",
            "spark_to_expansion_negative_control",
            "negative_control",
            ("source-level control role", "sub-threshold refinement condition"),
            "Expansion negative control needs source perturbation vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-appendix-e-cell-division-negative-control",
            "appendix_e_cell_division",
            "appendix_e_cell_division_negative_control",
            "negative_control",
            ("source-level daughter-region fail condition",),
            "Appendix E negative control needs explicit source failure semantics.",
        ),
        _future(
            "grc9v3-motif-s0006-choice-collapse-negative-control",
            "choice_collapse",
            "choice_collapse_negative_control",
            "negative_control",
            ("source-level choice suppression", "collapse target absence"),
            "Choice/collapse negative control needs source control vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-growth-pressure-negative-control",
            "growth_pressure",
            "growth_pressure_negative_control",
            "negative_control",
            ("low birth-pressure source control",),
            "Growth negative control needs low-pressure fixture vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-budget-preservation-negative-control",
            "budget_preservation",
            "budget_preservation_negative_control",
            "negative_control",
            ("budget perturbation control role",),
            "Budget controls are useful but not source ontology in Revision 1.",
        ),
        _future(
            "grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
            "transport_basin_rerouting",
            "transport_basin_rerouting_positive_control",
            "mechanism_diagnostic_motif",
            ("source-level route preference", "basin redirection predicate"),
            "Transport rerouting is source-relevant but needs explicit vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-transport-basin-rerouting-negative-control",
            "transport_basin_rerouting",
            "transport_basin_rerouting_negative_control",
            "negative_control",
            ("route suppression control",),
            "Transport negative control should wait for route vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0006-coarse-cache-invalidation-negative-control",
            "coarse_cache_invalidation",
            "coarse_cache_invalidation_negative_control",
            "negative_control",
            ("cache diagnostic control role",),
            "Coarse-cache controls remain runtime diagnostics unless source need is proven.",
        ),
        _future(
            "grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
            "quiescent_hybrid_control",
            "quiescent_hybrid_control_no_event_control",
            "quiescent_control",
            ("quiescent source role", "absence-of-event expectation"),
            "Quiescent source controls need explicit no-event fixture vocabulary.",
        ),
        _future(
            "grc9v3-motif-s0008-complex-spark-choice-no-saturation-perturbation-perturbation-control",
            "complex_spark_choice_no_saturation_perturbation_perturbation_control",
            "complex_spark_choice_no_saturation_perturbation_perturbation_control",
            "negative_control",
            ("complex perturbation source role", "no-saturation perturbation"),
            "Complex perturbation controls should follow after positive source fixtures.",
        ),
        _future(
            "grc9v3-motif-s0008-complex-growth-low-birth-perturbation-perturbation-control",
            "complex_growth_low_birth_perturbation_perturbation_control",
            "complex_growth_low_birth_perturbation_perturbation_control",
            "negative_control",
            ("complex perturbation source role", "low-birth perturbation"),
            "Complex growth perturbation controls should follow after growth source vocabulary.",
        ),
    )
    runtime_only = (
        _runtime_only(
            "grc9v3-motif-s0006-budget-preservation-positive-control",
            "budget_preservation",
            "budget_preservation_positive_control",
            "Budget preservation is a runtime invariant/diagnostic, not source ontology.",
        ),
        _runtime_only(
            "grc9v3-motif-s0006-hessian-backend-comparison-baseline-control",
            "hessian_backend_comparison",
            "hessian_backend_comparison_baseline_control",
            "Backend comparison stays runtime diagnostic unless it changes lifecycle outcome.",
        ),
        _runtime_only(
            "grc9v3-motif-s0006-hessian-backend-comparison-positive-control",
            "hessian_backend_comparison",
            "hessian_backend_comparison_positive_control",
            "Backend comparison stays runtime diagnostic unless it changes lifecycle outcome.",
        ),
        _runtime_only(
            "grc9v3-motif-s0006-coarse-cache-invalidation-positive-control",
            "coarse_cache_invalidation",
            "coarse_cache_invalidation_positive_control",
            "Coarse-cache invalidation is runtime cache hygiene, not source ontology.",
        ),
        _runtime_only(
            "grc9v3-motif-s0008-complex-hessian-row-basis-complex-control",
            "complex_hessian_row_basis_complex_control",
            "complex_hessian_row_basis_complex_control",
            "Hessian backend/tensor comparator is runtime diagnostic.",
        ),
        _runtime_only(
            "grc9v3-motif-s0008-complex-hessian-weighted-least-squares-complex-control",
            "complex_hessian_weighted_least_squares_complex_control",
            "complex_hessian_weighted_least_squares_complex_control",
            "Hessian backend/tensor comparator is runtime diagnostic.",
        ),
    )
    manifest = GRCL9V3LoweringManifest(
        entries=entries,
        future_vocabulary_records=future_records,
        runtime_only_exclusions=runtime_only,
    )
    if set(manifest.source_candidate_motif_ids()) != _EXPECTED_SOURCE_CANDIDATE_MOTIF_IDS:
        raise AssertionError("default manifest no longer covers expected S0014 source candidates")
    if set(manifest.future_vocabulary_motif_ids()) != _EXPECTED_FUTURE_VOCABULARY_MOTIF_IDS:
        raise AssertionError("default manifest no longer covers expected S0014 vocabulary records")
    if set(manifest.runtime_only_motif_ids()) != _EXPECTED_RUNTIME_ONLY_MOTIF_IDS:
        raise AssertionError("default manifest no longer covers expected S0014 runtime-only records")
    return manifest


def validate_grcl9v3_manifest_against_handoff(
    manifest: GRCL9V3LoweringManifest,
    handoff_path: str | Path | None = None,
) -> Mapping[str, Any]:
    """Validate manifest disposition ids against the S0014 source handoff JSON."""

    source_path = Path(handoff_path or manifest.source_handoff_path)
    if not source_path.exists():
        raise FileNotFoundError(2, "source handoff missing", str(source_path))
    handoff = json.loads(source_path.read_text(encoding="utf-8"))
    source_ids = _handoff_ids(handoff, "source_expression_candidates")
    future_ids = _handoff_ids(handoff, "requires_new_source_vocabulary")
    runtime_ids = _handoff_ids(handoff, "runtime_only")
    manifest_source_ids = set(manifest.source_candidate_motif_ids())
    manifest_future_ids = set(manifest.future_vocabulary_motif_ids())
    manifest_runtime_ids = set(manifest.runtime_only_motif_ids())
    mismatches = {
        "missing_source_candidate_ids": sorted(source_ids - manifest_source_ids),
        "extra_source_candidate_ids": sorted(manifest_source_ids - source_ids),
        "missing_future_vocabulary_ids": sorted(future_ids - manifest_future_ids),
        "extra_future_vocabulary_ids": sorted(manifest_future_ids - future_ids),
        "missing_runtime_only_ids": sorted(runtime_ids - manifest_runtime_ids),
        "extra_runtime_only_ids": sorted(manifest_runtime_ids - runtime_ids),
    }
    if any(mismatches.values()):
        raise ValueError(f"GRCL-9V3 manifest drifted from handoff: {mismatches}")
    return {
        "source_handoff_path": str(source_path),
        "source_expression_candidate_count": len(source_ids),
        "future_vocabulary_count": len(future_ids),
        "runtime_only_count": len(runtime_ids),
    }


def _handoff_ids(handoff: Mapping[str, Any], key: str) -> set[str]:
    return {
        str(item.get("motif_id", ""))
        for item in handoff.get(key, ())
        if isinstance(item, Mapping) and item.get("motif_id")
    }


__all__ = [
    "GRCL9V3_ACCEPTED_SOURCE_CONSTRUCT_KINDS",
    "GRCL9V3_BASE_NON_CLAIMS",
    "GRCL9V3_CONTROL_ROLES",
    "GRCL9V3_LOWERING_CARRIER_PREFIXES",
    "GRCL9V3_LOWERING_MANIFEST_VERSION",
    "GRCL9V3_OWNERSHIP_TAGS",
    "GRCL9V3_SOURCE_SCHEMA_VERSION",
    "GRCL9V3_TELEMETRY_FIELD_PREFIX",
    "GRCL9V3FutureVocabularyRecord",
    "GRCL9V3LoweringControl",
    "GRCL9V3LoweringManifest",
    "GRCL9V3LoweringManifestEntry",
    "GRCL9V3RuntimeOnlyExclusion",
    "GRCL9V3TelemetryExpectation",
    "default_grcl9v3_lowering_manifest",
    "validate_grcl9v3_manifest_against_handoff",
]
