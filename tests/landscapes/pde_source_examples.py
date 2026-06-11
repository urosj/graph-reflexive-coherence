"""Representative PDE landscape source examples for Phase L tests."""

from __future__ import annotations


def build_cell_like_source() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "meta": {
            "name": "Cell-Like",
            "description": "Representative conservative translation fixture.",
            "domain": "2d",
            "author": "RC Landscape Iteration 1",
            "date": "2026-02-16",
            "tags": ["cell", "fixture"],
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
            "compile_policy": {"profile_transform": "none"},
        },
        "geometry": {
            "distance_mode": "euclidean",
        },
        "compile": {
            "composition_mode": "blend",
            "value_range": {"mode": "clamp", "min": 0.0, "max": 1.0},
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": False,
            "direction": "none",
            "magnitude": 0.0,
            "channels": [],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.34,
                "coherence": 0.85,
            },
            {
                "type": "ridge",
                "name": "plasma_membrane",
                "parent": "cytoplasm",
                "ridge_type": "boundary",
                "inner_radius": 0.34,
                "outer_radius": 0.37,
                "interior_coherence": 0.85,
                "exterior_coherence": 0.15,
                "shape_mode": "ellipse",
                "orientation_deg": 90.0,
            },
            {
                "type": "basin",
                "name": "nucleus",
                "parent": "cytoplasm",
                "center": [0.46, 0.54],
                "radius": 0.12,
                "coherence": 0.94,
            },
            {
                "type": "valley",
                "name": "nucleus_channel",
                "from": "cytoplasm",
                "to": "nucleus",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.56,
                "control_points": [[0.49, 0.52], [0.48, 0.53]],
            },
        ],
    }


def build_fixture_cell1_source() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "meta": {
            "name": "Cell-1",
            "description": "Cell-0 plus nucleus basin and nucleus ridge.",
            "domain": "2d",
            "author": "RC Landscape Iteration 1",
            "date": "2026-02-16",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
            "compile_policy": {"profile_transform": "none"},
        },
        "compile": {
            "composition_mode": "blend",
            "value_range": {"mode": "clamp", "min": 0.0, "max": 1.0},
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": False,
            "direction": "none",
            "magnitude": 0.0,
            "channels": [],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.33,
                "coherence": 0.85,
            },
            {
                "type": "ridge",
                "name": "plasma_membrane",
                "parent": "cytoplasm",
                "ridge_type": "boundary",
                "inner_radius": 0.33,
                "outer_radius": 0.36,
                "interior_coherence": 0.85,
                "exterior_coherence": 0.15,
            },
            {
                "type": "basin",
                "name": "nucleus",
                "parent": "cytoplasm",
                "center": [0.46, 0.54],
                "radius": 0.12,
                "coherence": 0.94,
            },
            {
                "type": "ridge",
                "name": "nuclear_envelope",
                "parent": "nucleus",
                "ridge_type": "boundary",
                "inner_radius": 0.12,
                "outer_radius": 0.14,
                "interior_coherence": 0.94,
                "exterior_coherence": 0.85,
            },
        ],
    }


def build_routing_source() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "meta": {
            "name": "Routing Example",
            "description": "Hub-and-branch landscape.",
            "domain": "2d",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
        },
        "compile": {
            "composition_mode": "blend",
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": True,
            "direction": "custom",
            "magnitude": 0.4,
            "channels": [
                {
                    "name": "channel_junction_to_mito1",
                    "type": "valley",
                    "from": "routing_junction",
                    "to": "mitochondrion_1",
                    "weight": 0.8,
                }
            ],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.34,
                "coherence": 0.85,
            },
            {
                "type": "basin",
                "name": "routing_junction",
                "parent": "cytoplasm",
                "center": [0.52, 0.56],
                "radius": 0.04,
                "coherence": 0.77,
            },
            {
                "type": "basin",
                "name": "mitochondrion_1",
                "parent": "cytoplasm",
                "center": [0.34, 0.44],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito1",
                "from": "routing_junction",
                "to": "mitochondrion_1",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.53,
                "control_points": [[0.46, 0.53], [0.4, 0.48]],
            },
        ],
    }


def build_cell4_like_source() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "meta": {
            "name": "Cell-4-Like",
            "description": "Cell-like routing hub preserved conservatively.",
            "domain": "2d",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
        },
        "compile": {
            "composition_mode": "blend",
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": False,
            "direction": "none",
            "magnitude": 0.0,
            "channels": [],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.34,
                "coherence": 0.85,
            },
            {
                "type": "basin",
                "name": "nucleus",
                "parent": "cytoplasm",
                "center": [0.46, 0.54],
                "radius": 0.12,
                "coherence": 0.94,
            },
            {
                "type": "basin",
                "name": "mitochondrion_1",
                "parent": "cytoplasm",
                "center": [0.34, 0.44],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "basin",
                "name": "mitochondrion_2",
                "parent": "cytoplasm",
                "center": [0.62, 0.42],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "basin",
                "name": "mitochondrion_3",
                "parent": "cytoplasm",
                "center": [0.58, 0.66],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "basin",
                "name": "routing_junction",
                "parent": "cytoplasm",
                "center": [0.52, 0.56],
                "radius": 0.04,
                "coherence": 0.77,
            },
            {
                "type": "ridge",
                "name": "routing_junction_ridge",
                "parent": "routing_junction",
                "ridge_type": "internal",
                "inner_radius": 0.04,
                "outer_radius": 0.05,
                "interior_coherence": 0.77,
                "exterior_coherence": 0.64,
            },
            {
                "type": "valley",
                "name": "channel_nucleus_to_junction",
                "from": "nucleus",
                "to": "routing_junction",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.56,
                "control_points": [[0.49, 0.56], [0.51, 0.56]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito1",
                "from": "routing_junction",
                "to": "mitochondrion_1",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.53,
                "control_points": [[0.46, 0.53], [0.4, 0.48]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito2",
                "from": "routing_junction",
                "to": "mitochondrion_2",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.53,
                "control_points": [[0.56, 0.52], [0.6, 0.47]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito3",
                "from": "routing_junction",
                "to": "mitochondrion_3",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.52,
                "control_points": [[0.56, 0.61], [0.57, 0.64]],
            },
        ],
    }


def build_fixture_cell4_source() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "meta": {
            "name": "Cell-4",
            "description": (
                "Cell-3 plus saddle-like routing junction represented by a small "
                "hub basin and branch valleys."
            ),
            "domain": "2d",
            "author": "RC Landscape Iteration 1",
            "date": "2026-02-16",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
            "compile_policy": {
                "profile_transform": "band_remap",
                "band_remap": {
                    "source": [0.15, 0.95],
                    "target": [0.12, 0.98],
                },
            },
        },
        "compile": {
            "composition_mode": "blend",
            "value_range": {"mode": "clamp", "min": 0.0, "max": 1.0},
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": False,
            "direction": "none",
            "magnitude": 0.0,
            "channels": [],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.34,
                "coherence": 0.85,
            },
            {
                "type": "ridge",
                "name": "plasma_membrane",
                "parent": "cytoplasm",
                "ridge_type": "boundary",
                "inner_radius": 0.34,
                "outer_radius": 0.37,
                "interior_coherence": 0.85,
                "exterior_coherence": 0.15,
            },
            {
                "type": "basin",
                "name": "nucleus",
                "parent": "cytoplasm",
                "center": [0.46, 0.54],
                "radius": 0.12,
                "coherence": 0.94,
            },
            {
                "type": "ridge",
                "name": "nuclear_envelope",
                "parent": "nucleus",
                "ridge_type": "boundary",
                "inner_radius": 0.12,
                "outer_radius": 0.14,
                "interior_coherence": 0.94,
                "exterior_coherence": 0.85,
            },
            {
                "type": "basin",
                "name": "mitochondrion_1",
                "parent": "cytoplasm",
                "center": [0.34, 0.44],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "ridge",
                "name": "mito_membrane_1",
                "parent": "mitochondrion_1",
                "ridge_type": "boundary",
                "inner_radius": 0.06,
                "outer_radius": 0.074,
                "interior_coherence": 0.8,
                "exterior_coherence": 0.75,
            },
            {
                "type": "basin",
                "name": "mitochondrion_2",
                "parent": "cytoplasm",
                "center": [0.62, 0.42],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "ridge",
                "name": "mito_membrane_2",
                "parent": "mitochondrion_2",
                "ridge_type": "boundary",
                "inner_radius": 0.06,
                "outer_radius": 0.074,
                "interior_coherence": 0.8,
                "exterior_coherence": 0.75,
            },
            {
                "type": "basin",
                "name": "mitochondrion_3",
                "parent": "cytoplasm",
                "center": [0.58, 0.66],
                "radius": 0.06,
                "coherence": 0.8,
            },
            {
                "type": "ridge",
                "name": "mito_membrane_3",
                "parent": "mitochondrion_3",
                "ridge_type": "boundary",
                "inner_radius": 0.06,
                "outer_radius": 0.074,
                "interior_coherence": 0.8,
                "exterior_coherence": 0.75,
            },
            {
                "type": "basin",
                "name": "routing_junction",
                "parent": "cytoplasm",
                "center": [0.52, 0.56],
                "radius": 0.04,
                "coherence": 0.77,
            },
            {
                "type": "ridge",
                "name": "routing_junction_ridge",
                "parent": "routing_junction",
                "ridge_type": "internal",
                "inner_radius": 0.04,
                "outer_radius": 0.05,
                "interior_coherence": 0.77,
                "exterior_coherence": 0.64,
            },
            {
                "type": "valley",
                "name": "channel_nucleus_to_junction",
                "from": "nucleus",
                "to": "routing_junction",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.56,
                "control_points": [[0.49, 0.56], [0.51, 0.56]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito1",
                "from": "routing_junction",
                "to": "mitochondrion_1",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.53,
                "control_points": [[0.46, 0.53], [0.4, 0.48]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito2",
                "from": "routing_junction",
                "to": "mitochondrion_2",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.53,
                "control_points": [[0.56, 0.52], [0.6, 0.47]],
            },
            {
                "type": "valley",
                "name": "channel_junction_to_mito3",
                "from": "routing_junction",
                "to": "mitochondrion_3",
                "path_type": "bezier",
                "width": 0.03,
                "coherence": 0.52,
                "control_points": [[0.56, 0.61], [0.57, 0.64]],
            },
        ],
    }


def build_periodic_source() -> dict[str, object]:
    return {
        "schema_version": "2.0.0",
        "meta": {
            "name": "Periodic Example",
            "description": "Seam-spanning support on a torus.",
            "domain": "2d",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
        },
        "geometry": {
            "distance_mode": "periodic_torus",
            "period_x": 1.0,
            "period_y": 1.0,
        },
        "compile": {
            "composition_mode": "blend",
            "mass_normalization": {"mode": "target_mass", "target": 12.5},
        },
        "primitives": [
            {
                "type": "basin",
                "name": "seam_left",
                "center": [0.95, 0.5],
                "radius": 0.09,
                "coherence": 0.83,
            },
            {
                "type": "basin",
                "name": "seam_right",
                "center": [0.05, 0.5],
                "radius": 0.09,
                "coherence": 0.83,
            },
        ],
    }


def build_fixture_s6_source() -> dict[str, object]:
    return {
        "schema_version": "2.0.0",
        "meta": {
            "name": "S6 Periodic Seam Ring",
            "description": (
                "Canonical strict S6 substrate family with periodic seam-spanning "
                "support and wrapped channel coupling."
            ),
            "domain": "2d",
            "author": "RC Landscape Iteration 2",
            "date": "2026-04-02",
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
            "compile_policy": {"profile_transform": "none"},
        },
        "geometry": {
            "distance_mode": "periodic_torus",
            "period_x": 1.0,
            "period_y": 1.0,
        },
        "compile": {
            "composition_mode": "blend",
            "value_range": {"mode": "clamp", "min": 0.0, "max": 1.0},
            "mass_normalization": {"mode": "none"},
        },
        "initial_flux": {
            "enabled": False,
            "direction": "none",
            "magnitude": 0.0,
            "channels": [],
        },
        "primitives": [
            {
                "type": "basin",
                "name": "seam_left",
                "center": [0.95, 0.5],
                "radius": 0.09,
                "coherence": 0.83,
            },
            {
                "type": "ridge",
                "name": "seam_left_boundary",
                "parent": "seam_left",
                "ridge_type": "boundary",
                "inner_radius": 0.09,
                "outer_radius": 0.11,
                "interior_coherence": 0.83,
                "exterior_coherence": 0.25,
            },
            {
                "type": "basin",
                "name": "seam_right",
                "center": [0.05, 0.5],
                "radius": 0.09,
                "coherence": 0.83,
            },
            {
                "type": "ridge",
                "name": "seam_right_boundary",
                "parent": "seam_right",
                "ridge_type": "boundary",
                "inner_radius": 0.09,
                "outer_radius": 0.11,
                "interior_coherence": 0.83,
                "exterior_coherence": 0.25,
            },
            {
                "type": "valley",
                "name": "seam_channel",
                "from": "seam_left",
                "to": "seam_right",
                "path_type": "straight",
                "width": 0.05,
                "coherence": 0.32,
            },
        ],
    }


def build_explicit_plateau_and_saddle_source() -> dict[str, object]:
    return {
        "schema_version": "1.1.0",
        "meta": {
            "name": "Explicit Plateau And Saddle",
            "description": "Source-authentic plateau and saddle passthrough example.",
            "domain": "2d",
            "tags": ["explicit-structures"],
        },
        "params": {
            "lambda_C": 1.0,
            "xi_C": 1.5,
            "zeta_C": 0.8,
            "kappa_C": 1.0,
            "dt": 0.001,
        },
        "potential": {
            "type": "double_well",
            "params": {"a": 1.0, "b": 1.2},
        },
        "compile": {
            "composition_mode": "blend",
            "mass_normalization": {"mode": "none"},
        },
        "primitives": [
            {
                "type": "plateau",
                "name": "routing_plateau",
                "parent": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.1,
                "coherence": 0.7,
                "hosted_primitive_ids": ["nucleus", "decision_saddle"],
                "stability_class": "neutral",
                "role": "routing_surface",
                "notes": "Explicit source plateau.",
            },
            {
                "type": "basin",
                "name": "cytoplasm",
                "center": [0.5, 0.5],
                "radius": 0.34,
                "coherence": 0.85,
            },
            {
                "type": "basin",
                "name": "nucleus",
                "parent": "routing_plateau",
                "center": [0.46, 0.54],
                "radius": 0.12,
                "coherence": 0.94,
            },
            {
                "type": "saddle",
                "name": "decision_saddle",
                "host_id": "routing_plateau",
                "branch_target_ids": ["nucleus", "cytoplasm"],
                "coherence": 0.5,
                "center": [0.52, 0.5],
                "junction_role": "decision_point",
                "notes": "Explicit source saddle.",
            },
        ],
    }
