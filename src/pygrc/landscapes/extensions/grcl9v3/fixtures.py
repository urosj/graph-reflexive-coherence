"""Built-in minimal GRCL-9V3 source fixtures for Revision 1."""

from __future__ import annotations

from collections.abc import Mapping

from .manifest import GRCL9V3LoweringManifestEntry, default_grcl9v3_lowering_manifest
from .schema import (
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3BridgePolicy,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3ColumnProxyFallbackProfile,
    GRCL9V3ExpansionRefinementRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3HybridTensorProfile,
    GRCL9V3RowBasisHessianProfile,
    GRCL9V3QuiescentHybridRegion,
    GRCL9V3SourceDocument,
    GRCL9V3TransportReroutingRegion,
)


GRCL9V3_SOURCE_FIXTURE_NAMES = (
    "hybrid_spark_gate_positive_control",
    "hybrid_spark_gate_negative_control",
    "spark_to_expansion_positive_control",
    "spark_to_expansion_negative_control",
    "appendix_e_cell_division_positive_control",
    "appendix_e_cell_division_negative_control",
    "choice_collapse_positive_control",
    "choice_collapse_negative_control",
    "growth_pressure_positive_control",
    "growth_pressure_negative_control",
    "transport_basin_rerouting_positive_control",
    "quiescent_hybrid_control_no_event_control",
)

_MOTIF_IDS = {
    "hybrid_spark_gate_positive_control": "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
    "hybrid_spark_gate_negative_control": "grc9v3-motif-s0006-hybrid-spark-gate-negative-control",
    "spark_to_expansion_positive_control": "grc9v3-motif-s0006-spark-to-expansion-positive-control",
    "spark_to_expansion_negative_control": "grc9v3-motif-s0006-spark-to-expansion-negative-control",
    "appendix_e_cell_division_positive_control": "grc9v3-motif-s0006-appendix-e-cell-division-positive-control",
    "appendix_e_cell_division_negative_control": "grc9v3-motif-s0006-appendix-e-cell-division-negative-control",
    "choice_collapse_positive_control": "grc9v3-motif-s0006-choice-collapse-positive-control",
    "choice_collapse_negative_control": "grc9v3-motif-s0006-choice-collapse-negative-control",
    "growth_pressure_positive_control": "grc9v3-motif-s0006-growth-pressure-positive-control",
    "growth_pressure_negative_control": "grc9v3-motif-s0006-growth-pressure-negative-control",
    "transport_basin_rerouting_positive_control": "grc9v3-motif-s0006-transport-basin-rerouting-positive-control",
    "quiescent_hybrid_control_no_event_control": "grc9v3-motif-s0006-quiescent-hybrid-control-no-event-control",
}


def default_grcl9v3_source_fixtures() -> tuple[GRCL9V3SourceDocument, ...]:
    """Return the first GRCL-9V3 source fixtures linked to the manifest."""

    manifest = default_grcl9v3_lowering_manifest()
    entries = manifest.by_entry_id()
    fixtures = (
        _hybrid_spark_fixture(
            "hybrid_spark_gate_positive_control",
            entries["grcl9v3_lowering_hybrid_spark_gate_v1"],
            source_role="positive_control",
            active_degree=9,
            tensor_mode="anisotropic",
        ),
        _future_hybrid_spark_fixture(
            "hybrid_spark_gate_negative_control",
            source_role="negative_control",
            active_degree=7,
            tensor_mode="stable",
            selector_ids=("no_lifecycle_events",),
        ),
        _expansion_fixture(
            "spark_to_expansion_positive_control",
            entries["grcl9v3_lowering_spark_to_expansion_v1"],
            source_role="positive_control",
            active_degree=9,
            target_effective_degree=30,
        ),
        _future_expansion_fixture(
            "spark_to_expansion_negative_control",
            source_role="negative_control",
            active_degree=8,
            target_effective_degree=30,
            selector_ids=("no_lifecycle_events",),
        ),
        _appendix_e_fixture(
            "appendix_e_cell_division_positive_control",
            entries["grcl9v3_lowering_appendix_e_cell_division_v1"],
            source_role="positive_control",
            module_support="balanced_daughter_support",
        ),
        _future_appendix_e_fixture(
            "appendix_e_cell_division_negative_control",
            source_role="negative_control",
            module_support="daughter_support_below_minimum",
            selector_ids=("appendix_e_no_completion",),
        ),
        _choice_fixture(
            "choice_collapse_positive_control",
            entries["grcl9v3_lowering_choice_collapse_v1"],
            source_role="positive_control",
            compatibility="high_contrast",
        ),
        _future_choice_fixture(
            "choice_collapse_negative_control",
            source_role="negative_control",
            compatibility="low_contrast",
            selector_ids=("no_choice_collapse_events",),
        ),
        _growth_fixture(
            "growth_pressure_positive_control",
            entries["grcl9v3_lowering_growth_pressure_v1"],
            source_role="positive_control",
            lambda_birth=1.4,
            pressure="high_outward_pressure",
        ),
        _future_growth_fixture(
            "growth_pressure_negative_control",
            source_role="negative_control",
            lambda_birth=0.02,
            pressure="low_outward_pressure",
            selector_ids=("no_growth_events",),
        ),
        _future_transport_fixture(
            "transport_basin_rerouting_positive_control",
            source_role="positive_control",
            selector_ids=("transport_rerouting_signature",),
        ),
        _future_quiescent_fixture(
            "quiescent_hybrid_control_no_event_control",
            source_role="no_event_control",
            selector_ids=("no_lifecycle_events",),
        ),
    )
    if tuple(item.fixture_name for item in fixtures) != GRCL9V3_SOURCE_FIXTURE_NAMES:
        raise AssertionError("fixture ordering drifted from GRCL9V3_SOURCE_FIXTURE_NAMES")
    return fixtures


def grcl9v3_source_fixture_by_name() -> Mapping[str, GRCL9V3SourceDocument]:
    """Return Revision 1 source fixtures keyed by fixture name."""

    return {fixture.fixture_name: fixture for fixture in default_grcl9v3_source_fixtures()}


def _document(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    constructs: tuple[object, ...],
) -> GRCL9V3SourceDocument:
    controls = [control for control in entry.controls if control.source_fixture_name == fixture_name]
    if len(controls) != 1:
        raise ValueError(f"fixture {fixture_name!r} is not linked to {entry.entry_id!r}")
    control = controls[0]
    return GRCL9V3SourceDocument(
        fixture_name=fixture_name,
        manifest_entry_id=entry.entry_id,
        expected_selector_ids=control.selector_ids,
        bridge_policy=GRCL9V3BridgePolicy(conductance_hint=0.001),
        constructs=constructs,  # type: ignore[arg-type]
        expected_telemetry=entry.expected_telemetry,
        notes={
            "boundary": "source fixture declares GRCL-9V3 preconditions only",
            "runtime_validation": "Phase T-GRC9V3 telemetry after replay",
        },
    )


def _future_document(
    fixture_name: str,
    *,
    selector_ids: tuple[str, ...],
    constructs: tuple[object, ...],
) -> GRCL9V3SourceDocument:
    manifest = default_grcl9v3_lowering_manifest()
    motif_ids = {str(construct.motif_id) for construct in constructs}  # type: ignore[attr-defined]
    if len(motif_ids) != 1:
        raise ValueError("future-vocabulary fixtures must use exactly one motif_id")
    motif_id = next(iter(motif_ids))
    future_by_motif = {record.motif_id: record for record in manifest.future_vocabulary_records}
    record = future_by_motif.get(motif_id)
    if record is None:
        raise ValueError(f"fixture {fixture_name!r} is not linked to a future-vocabulary record")

    return GRCL9V3SourceDocument(
        fixture_name=fixture_name,
        manifest_entry_id=f"future_vocabulary_{record.phenomenon}_v1",
        expected_selector_ids=selector_ids,
        bridge_policy=GRCL9V3BridgePolicy(conductance_hint=0.001),
        constructs=constructs,  # type: ignore[arg-type]
        expected_telemetry=(),
        notes={
            "boundary": "future-vocabulary source fixture declares preconditions only",
            "selector_dependency": "selector ids are resolved when field-backed selectors are added",
            "runtime_validation": "selector validation after lowering and replay",
        },
    )


def _spark_region(
    fixture_name: str,
    *,
    motif_id: str,
    source_role: str,
    active_degree: int,
    ownership: str = "grc9v3_hybrid",
) -> GRCL9V3HybridSparkRegion:
    return GRCL9V3HybridSparkRegion(
        construct_id=f"{fixture_name}_spark_region",
        motif_id=motif_id,
        source_role=source_role,
        ownership=ownership,
        expected_selector_ids=("hybrid_spark_events",),
        candidate_region_id="candidate",
        saturation_profile={
            "active_degree": active_degree,
            "port_chart": "nine_port_candidate",
        },
        spark_gate_intent="hybrid_hessian_tensor",
        spark_threshold=0.05,
    )


def _hessian_profile(
    fixture_name: str,
    *,
    motif_id: str,
    source_role: str,
    tensor_mode: str,
) -> GRCL9V3RowBasisHessianProfile:
    return GRCL9V3RowBasisHessianProfile(
        construct_id=f"{fixture_name}_hessian_profile",
        motif_id=motif_id,
        source_role=source_role,
        ownership="grcv3_semantic",
        candidate_region_id="candidate",
        row_basis_profile={
            "hessian_mode": tensor_mode,
            "basis": "row_basis_diagonal",
        },
    )


def _tensor_profile(
    fixture_name: str,
    *,
    motif_id: str,
    source_role: str,
    tensor_mode: str,
) -> GRCL9V3HybridTensorProfile:
    return GRCL9V3HybridTensorProfile(
        construct_id=f"{fixture_name}_tensor_profile",
        motif_id=motif_id,
        source_role=source_role,
        ownership="grc9v3_hybrid",
        region_id="candidate",
        anisotropy_axis="row_2" if tensor_mode == "anisotropic" else "row_1",
        tensor_profile={
            "tensor_mode": tensor_mode,
            "row_mismatch": "high" if tensor_mode == "anisotropic" else "low",
        },
    )


def _column_proxy(
    fixture_name: str,
    *,
    motif_id: str,
    source_role: str,
    mode: str,
) -> GRCL9V3ColumnProxyFallbackProfile:
    return GRCL9V3ColumnProxyFallbackProfile(
        construct_id=f"{fixture_name}_column_proxy",
        motif_id=motif_id,
        source_role=source_role,
        ownership="grc9_mechanical",
        candidate_region_id="candidate",
        target_column=2,
        cancellation_mode=mode,
        column_profile={"column_2": mode},
    )


def _hybrid_spark_fixture(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    *,
    source_role: str,
    active_degree: int,
    tensor_mode: str,
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _document(
        fixture_name,
        entry,
        (
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                active_degree=active_degree,
            ),
            _hessian_profile(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                tensor_mode=tensor_mode,
            ),
            _tensor_profile(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                tensor_mode=tensor_mode,
            ),
            _column_proxy(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                mode="near_cancellation",
            ),
        ),
    )


def _future_hybrid_spark_fixture(
    fixture_name: str,
    *,
    source_role: str,
    active_degree: int,
    tensor_mode: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                active_degree=active_degree,
            ),
            _hessian_profile(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                tensor_mode=tensor_mode,
            ),
            _tensor_profile(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                tensor_mode=tensor_mode,
            ),
        ),
    )


def _expansion_fixture(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    *,
    source_role: str,
    active_degree: int,
    target_effective_degree: int,
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _document(
        fixture_name,
        entry,
        (
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                active_degree=active_degree,
            ),
            GRCL9V3ExpansionRefinementRegion(
                construct_id=f"{fixture_name}_expansion_region",
                motif_id=motif_id,
                source_role=source_role,
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                target_effective_degree=target_effective_degree,
                expansion_distribution_mode="equal",
            ),
        ),
    )


def _future_expansion_fixture(
    fixture_name: str,
    *,
    source_role: str,
    active_degree: int,
    target_effective_degree: int,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                source_role=source_role,
                active_degree=active_degree,
            ),
            GRCL9V3ExpansionRefinementRegion(
                construct_id=f"{fixture_name}_expansion_region",
                motif_id=motif_id,
                source_role=source_role,
                ownership="grc9_mechanical",
                candidate_region_id="candidate",
                target_effective_degree=target_effective_degree,
            ),
        ),
    )


def _appendix_e_fixture(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    *,
    source_role: str,
    module_support: str,
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _document(
        fixture_name,
        entry,
        _appendix_e_constructs(fixture_name, motif_id, source_role, module_support),
    )


def _future_appendix_e_fixture(
    fixture_name: str,
    *,
    source_role: str,
    module_support: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    motif_id = _MOTIF_IDS[fixture_name]
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=_appendix_e_constructs(fixture_name, motif_id, source_role, module_support),
    )


def _appendix_e_constructs(
    fixture_name: str,
    motif_id: str,
    source_role: str,
    module_support: str,
) -> tuple[object, ...]:
    return (
        _spark_region(
            fixture_name,
            motif_id=motif_id,
            source_role=source_role,
            active_degree=9,
        ),
        GRCL9V3ExpansionRefinementRegion(
            construct_id=f"{fixture_name}_expansion_region",
            motif_id=motif_id,
            source_role=source_role,
            ownership="grc9_mechanical",
            candidate_region_id="candidate",
            target_effective_degree=30,
        ),
        GRCL9V3AppendixEDivisionRegion(
            construct_id=f"{fixture_name}_division_region",
            motif_id=motif_id,
            source_role=source_role,
            ownership="grc9v3_hybrid",
            parent_region_id="parent",
            daughter_region_a="daughter_a",
            daughter_region_b="daughter_b",
            module_basin_support={"support_mode": module_support},
        ),
    )


def _choice_fixture(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    *,
    source_role: str,
    compatibility: str,
) -> GRCL9V3SourceDocument:
    return _document(
        fixture_name,
        entry,
        (_choice_construct(fixture_name, _MOTIF_IDS[fixture_name], source_role, compatibility),),
    )


def _future_choice_fixture(
    fixture_name: str,
    *,
    source_role: str,
    compatibility: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(_choice_construct(fixture_name, _MOTIF_IDS[fixture_name], source_role, compatibility),),
    )


def _choice_construct(
    fixture_name: str,
    motif_id: str,
    source_role: str,
    compatibility: str,
) -> GRCL9V3ChoiceCollapseRegion:
    return GRCL9V3ChoiceCollapseRegion(
        construct_id=f"{fixture_name}_choice_region",
        motif_id=motif_id,
        source_role=source_role,
        ownership="grcv3_semantic",
        choice_region_id="choice_region",
        basin_region_a="basin_a",
        basin_region_b="basin_b",
        collapse_target_region="basin_a",
        compatibility_profile={"compatibility": compatibility},
    )


def _growth_fixture(
    fixture_name: str,
    entry: GRCL9V3LoweringManifestEntry,
    *,
    source_role: str,
    lambda_birth: float,
    pressure: str,
) -> GRCL9V3SourceDocument:
    return _document(
        fixture_name,
        entry,
        (_growth_construct(fixture_name, _MOTIF_IDS[fixture_name], source_role, lambda_birth, pressure),),
    )


def _future_growth_fixture(
    fixture_name: str,
    *,
    source_role: str,
    lambda_birth: float,
    pressure: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(_growth_construct(fixture_name, _MOTIF_IDS[fixture_name], source_role, lambda_birth, pressure),),
    )


def _growth_construct(
    fixture_name: str,
    motif_id: str,
    source_role: str,
    lambda_birth: float,
    pressure: str,
) -> GRCL9V3GrowthLocus:
    return GRCL9V3GrowthLocus(
        construct_id=f"{fixture_name}_growth_locus",
        motif_id=motif_id,
        source_role=source_role,
        ownership="grc9_mechanical",
        parent_region_id="parent",
        inactive_parent_port=5,
        outward_pressure_profile={"pressure": pressure},
        lambda_birth=lambda_birth,
    )


def _future_transport_fixture(
    fixture_name: str,
    *,
    source_role: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(
            GRCL9V3TransportReroutingRegion(
                construct_id=f"{fixture_name}_transport_region",
                motif_id=_MOTIF_IDS[fixture_name],
                source_role=source_role,
                ownership="shared_runtime",
                route_region_id="route",
                source_region_id="source",
                sink_region_id="sink",
                route_preference_profile={"corridor": "preferred"},
            ),
        ),
    )


def _future_quiescent_fixture(
    fixture_name: str,
    *,
    source_role: str,
    selector_ids: tuple[str, ...],
) -> GRCL9V3SourceDocument:
    return _future_document(
        fixture_name,
        selector_ids=selector_ids,
        constructs=(
            GRCL9V3QuiescentHybridRegion(
                construct_id=f"{fixture_name}_quiescent_region",
                motif_id=_MOTIF_IDS[fixture_name],
                source_role=source_role,
                ownership="grc9v3_hybrid",
                region_id="quiet",
                stability_margin_profile={"active_degree": 5, "pressure": "low"},
            ),
        ),
    )
