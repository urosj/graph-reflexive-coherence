"""Built-in minimal GRCL-9 source fixtures for Revision 1."""

from __future__ import annotations

from collections.abc import Mapping

from .manifest import GRCL9LoweringManifestEntry, default_grcl9_lowering_manifest
from .schema import (
    GRCL9BridgePolicy,
    GRCL9ColumnProxyProfile,
    GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus,
    GRCL9InstabilityProfile,
    GRCL9PostExpansionFissionGeometry,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
)


GRCL9_SOURCE_FIXTURE_NAMES = (
    "spark_column_proxy_eps_pass",
    "spark_column_proxy_eps_fail",
    "spark_instability_tau_pass",
    "spark_instability_tau_fail",
    "spark_to_expansion_d_eff_low",
    "spark_to_expansion_d_eff_high",
    "growth_pressure_lambda_high",
    "growth_pressure_lambda_low",
    "post_expansion_fission_min_mass_pass",
    "post_expansion_fission_min_mass_fail",
)


def default_grcl9_source_fixtures() -> tuple[GRCL9SourceDocument, ...]:
    """Return the first GRCL-9 source fixtures linked to the lowering manifest."""

    manifest_by_seed_family = default_grcl9_lowering_manifest().by_seed_family()
    fixtures = (
        _spark_column_proxy_fixture(
            "spark_column_proxy_eps_pass",
            manifest_by_seed_family["spark_column_proxy_emitter"],
            target_column=2,
            diagnostic_mode="near_epsilon",
            spark_threshold=0.02,
        ),
        _spark_column_proxy_fixture(
            "spark_column_proxy_eps_fail",
            manifest_by_seed_family["spark_column_proxy_emitter"],
            target_column=2,
            diagnostic_mode="off_epsilon",
            spark_threshold=0.02,
        ),
        _spark_instability_fixture(
            "spark_instability_tau_pass",
            manifest_by_seed_family["spark_instability_emitter"],
            row_bias="strong_row_1",
            cut_support_mode="high_cut_low_support",
            tau_instability=0.25,
        ),
        _spark_instability_fixture(
            "spark_instability_tau_fail",
            manifest_by_seed_family["spark_instability_emitter"],
            row_bias="balanced_rows",
            cut_support_mode="balanced_cut_support",
            tau_instability=0.95,
        ),
        _expansion_fixture(
            "spark_to_expansion_d_eff_low",
            manifest_by_seed_family["spark_to_expansion_emitter"],
            target_effective_degree=16,
        ),
        _expansion_fixture(
            "spark_to_expansion_d_eff_high",
            manifest_by_seed_family["spark_to_expansion_emitter"],
            target_effective_degree=44,
        ),
        _growth_fixture(
            "growth_pressure_lambda_high",
            manifest_by_seed_family["growth_pressure_emitter"],
            lambda_birth=2.0,
            pressure_class="high",
        ),
        _growth_fixture(
            "growth_pressure_lambda_low",
            manifest_by_seed_family["growth_pressure_emitter"],
            lambda_birth=0.05,
            pressure_class="low",
        ),
        _fission_fixture(
            "post_expansion_fission_min_mass_pass",
            manifest_by_seed_family["post_expansion_fission_emitter"],
            identity_fission_min_basin_mass=0.0,
            bridge_class="weak_bridge_with_two_poles",
        ),
        _fission_fixture(
            "post_expansion_fission_min_mass_fail",
            manifest_by_seed_family["post_expansion_fission_emitter"],
            identity_fission_min_basin_mass=0.90,
            bridge_class="weak_bridge_with_under_mass_pole",
        ),
    )
    if tuple(item.fixture_name for item in fixtures) != GRCL9_SOURCE_FIXTURE_NAMES:
        raise AssertionError("fixture ordering drifted from GRCL9_SOURCE_FIXTURE_NAMES")
    return fixtures


def grcl9_source_fixture_by_name() -> Mapping[str, GRCL9SourceDocument]:
    """Return Revision 1 source fixtures keyed by fixture name."""

    return {fixture.fixture_name: fixture for fixture in default_grcl9_source_fixtures()}


def _document(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    constructs: tuple[object, ...],
) -> GRCL9SourceDocument:
    matching_controls = [
        control for control in entry.controls if control.source_fixture_name == fixture_name
    ]
    if len(matching_controls) != 1:
        raise ValueError(f"fixture {fixture_name!r} is not linked to manifest entry {entry.entry_id!r}")
    control = matching_controls[0]
    return GRCL9SourceDocument(
        fixture_name=fixture_name,
        manifest_entry_id=entry.entry_id,
        expected_selector_ids=control.selector_ids,
        bridge_policy=GRCL9BridgePolicy(conductance_hint=0.001),
        constructs=constructs,  # type: ignore[arg-type]
        expected_telemetry=entry.expected_telemetry,
        notes=(
            "Source fixture declares GRCL-9 mechanical preconditions only; "
            "runtime evidence is validated after GRC9 replay."
        ),
    )


def _spark_region(
    fixture_name: str,
    *,
    motif_id: str,
    spark_gate_intent: str,
    profile: Mapping[str, object],
) -> GRCL9SparkCandidateRegion:
    return GRCL9SparkCandidateRegion(
        construct_id=f"{fixture_name}_spark_region",
        motif_id=motif_id,
        candidate_id="candidate",
        coherence_allocation={
            "candidate": 1.0,
            "neighbors": 0.5,
            "profile": dict(profile),
        },
        neighbor_coherence_profile={
            "port_occupancy": "all_nine_ports",
            "profile": dict(profile),
        },
        spark_gate_intent=spark_gate_intent,
    )


def _spark_column_proxy_fixture(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    *,
    target_column: int,
    diagnostic_mode: str,
    spark_threshold: float,
) -> GRCL9SourceDocument:
    motif_id = "spark_column_proxy"
    profile = {
        "target_column": target_column,
        "diagnostic_mode": diagnostic_mode,
        "spark_threshold": spark_threshold,
    }
    return _document(
        fixture_name,
        entry,
        (
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                spark_gate_intent="saturation_column_proxy",
                profile=profile,
            ),
            GRCL9ColumnProxyProfile(
                construct_id=f"{fixture_name}_column_profile",
                motif_id=motif_id,
                candidate_id="candidate",
                target_column=target_column,
                cancellation_mode="cancellation" if diagnostic_mode == "near_epsilon" else "imbalance",
                conductance_profile={
                    "column": target_column,
                    "row_pattern": "balanced_pairs" if diagnostic_mode == "near_epsilon" else "unbalanced_pairs",
                    "spark_threshold": spark_threshold,
                },
                coherence_profile={
                    "column": target_column,
                    "diagnostic_mode": diagnostic_mode,
                },
            ),
        ),
    )


def _spark_instability_fixture(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    *,
    row_bias: str,
    cut_support_mode: str,
    tau_instability: float,
) -> GRCL9SourceDocument:
    motif_id = "spark_instability"
    profile = {
        "row_bias": row_bias,
        "cut_support_mode": cut_support_mode,
        "tau_instability": tau_instability,
    }
    return _document(
        fixture_name,
        entry,
        (
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                spark_gate_intent="saturation_instability",
                profile=profile,
            ),
            GRCL9InstabilityProfile(
                construct_id=f"{fixture_name}_instability_profile",
                motif_id=motif_id,
                candidate_id="candidate",
                row_anisotropy_profile={
                    "row_bias": row_bias,
                    "basis_terms": ("coherence", "mismatch", "flux_feedback"),
                },
                support_cut_profile={
                    "mode": cut_support_mode,
                    "proxy": "cut_out_over_cut_plus_support",
                },
                tau_instability=tau_instability,
            ),
        ),
    )


def _expansion_fixture(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    *,
    target_effective_degree: int,
) -> GRCL9SourceDocument:
    motif_id = "expansion_refinement"
    profile = {
        "target_effective_degree": target_effective_degree,
        "module_policy": "canonical_three_satellite",
    }
    return _document(
        fixture_name,
        entry,
        (
            _spark_region(
                fixture_name,
                motif_id=motif_id,
                spark_gate_intent="saturation_column_proxy",
                profile=profile,
            ),
            GRCL9ExpansionRefinementRegion(
                construct_id=f"{fixture_name}_expansion_region",
                motif_id=motif_id,
                candidate_id="candidate",
                target_effective_degree=target_effective_degree,
                module_size_formula="max(1, ceil((D_eff - 2) / 7))",
                bond_weight_mode="fixed",
                coherence_transfer_mode="equal",
                coherence_transfer_ratios=(1 / 3, 1 / 3, 1 / 3),
            ),
        ),
    )


def _growth_fixture(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    *,
    lambda_birth: float,
    pressure_class: str,
) -> GRCL9SourceDocument:
    return _document(
        fixture_name,
        entry,
        (
            GRCL9GrowthLocus(
                construct_id=f"{fixture_name}_growth_locus",
                motif_id="growth_pressure",
                parent_id="parent",
                inactive_parent_port=5,
                pressure_profile={
                    "class": pressure_class,
                    "boundary": "single_inactive_port",
                    "pressure_formula": "one_minus_exp_minus_lambda_flux",
                },
                birth_rule="outward_flux_pressure",
                lambda_birth=lambda_birth,
            ),
        ),
    )


def _fission_fixture(
    fixture_name: str,
    entry: GRCL9LoweringManifestEntry,
    *,
    identity_fission_min_basin_mass: float,
    bridge_class: str,
) -> GRCL9SourceDocument:
    return _document(
        fixture_name,
        entry,
        (
            GRCL9PostExpansionFissionGeometry(
                construct_id=f"{fixture_name}_fission_geometry",
                motif_id="post_expansion_fission",
                module_region_id="module",
                sink_region_a="sink_a",
                sink_region_b="sink_b",
                identity_fission_min_basin_mass=identity_fission_min_basin_mass,
                identity_fission_persistence_delta=3,
                separable_conductance_geometry=True,
            ),
        ),
    )
