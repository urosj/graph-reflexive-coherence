"""Shared capability vocabulary and family capability profiles for PyGRC."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import UnsupportedCapabilityError


SINGLE_WEIGHT_EDGES = "single_weight_edges"
MULTI_METRIC_EDGES = "multi_metric_edges"
PORT_GRAPH = "port_graph"
MECHANICAL_REFINEMENT = "mechanical_refinement"
COLUMN_COARSE_GRAINING = "column_coarse_graining"
BASIN_ATTRIBUTES = "basin_attributes"
HIERARCHY_TRACKING = "hierarchy_tracking"
CHOICE_COLLAPSE_SEMANTICS = "choice_collapse_semantics"
QUADRATURE_BUDGET = "quadrature_budget"
INTRINSIC_FRAME = "intrinsic_frame"
HOST_EMBEDDING_FRAME = "host_embedding_frame"
BOUNDARY_BARRIER = "boundary_barrier"
CAUSAL_LAYER = "causal_layer"
ANISOTROPIC_EDGES = "anisotropic_edges"
MULTISCALE_SIGMA = "multiscale_sigma"
IDENTITY_BASINS = "identity_basins"
PROXY_SPARKS = "proxy_sparks"
SOFT_SPLIT = "soft_split"
FRONT_BIRTH = "front_birth"
BUDGET_PRESERVATION = "budget_preservation"

ALL_CAPABILITIES = frozenset(
    {
        SINGLE_WEIGHT_EDGES,
        MULTI_METRIC_EDGES,
        PORT_GRAPH,
        MECHANICAL_REFINEMENT,
        COLUMN_COARSE_GRAINING,
        BASIN_ATTRIBUTES,
        HIERARCHY_TRACKING,
        CHOICE_COLLAPSE_SEMANTICS,
        QUADRATURE_BUDGET,
        INTRINSIC_FRAME,
        HOST_EMBEDDING_FRAME,
        BOUNDARY_BARRIER,
        CAUSAL_LAYER,
        ANISOTROPIC_EDGES,
        MULTISCALE_SIGMA,
        IDENTITY_BASINS,
        PROXY_SPARKS,
        SOFT_SPLIT,
        FRONT_BIRTH,
        BUDGET_PRESERVATION,
    }
)


@dataclass(frozen=True)
class CapabilityProfile:
    """Capability requirements and boundaries for one model family."""

    family: str
    required: frozenset[str]
    optional: frozenset[str]
    forbidden: frozenset[str]

    def validate_claims(self, claimed: set[str]) -> None:
        unknown = claimed - ALL_CAPABILITIES
        if unknown:
            raise UnsupportedCapabilityError(
                f"{self.family} advertises unknown capabilities: {sorted(unknown)}"
            )

        missing = self.required - claimed
        if missing:
            raise UnsupportedCapabilityError(
                f"{self.family} is missing required capabilities: {sorted(missing)}"
            )

        forbidden = self.forbidden & claimed
        if forbidden:
            raise UnsupportedCapabilityError(
                f"{self.family} must not claim capabilities: {sorted(forbidden)}"
            )

        allowed = self.required | self.optional
        unsupported = claimed - allowed
        if unsupported:
            raise UnsupportedCapabilityError(
                f"{self.family} advertises capabilities outside its profile: "
                f"{sorted(unsupported)}"
            )


GRCV2_CAPABILITY_PROFILE = CapabilityProfile(
    family="GRCV2",
    required=frozenset(
        {
            SINGLE_WEIGHT_EDGES,
            MULTI_METRIC_EDGES,
            IDENTITY_BASINS,
            PROXY_SPARKS,
            SOFT_SPLIT,
            FRONT_BIRTH,
            BUDGET_PRESERVATION,
        }
    ),
    optional=frozenset(
        {
            INTRINSIC_FRAME,
            HOST_EMBEDDING_FRAME,
            BOUNDARY_BARRIER,
            CAUSAL_LAYER,
            ANISOTROPIC_EDGES,
            MULTISCALE_SIGMA,
        }
    ),
    forbidden=frozenset(
        {
            BASIN_ATTRIBUTES,
            HIERARCHY_TRACKING,
            CHOICE_COLLAPSE_SEMANTICS,
            QUADRATURE_BUDGET,
            PORT_GRAPH,
            MECHANICAL_REFINEMENT,
            COLUMN_COARSE_GRAINING,
        }
    ),
)

GRCV3_CAPABILITY_PROFILE = CapabilityProfile(
    family="GRCV3",
    required=frozenset(
        {
            BASIN_ATTRIBUTES,
            MULTI_METRIC_EDGES,
            HIERARCHY_TRACKING,
            QUADRATURE_BUDGET,
            CHOICE_COLLAPSE_SEMANTICS,
        }
    ),
    optional=frozenset(
        {
            INTRINSIC_FRAME,
            HOST_EMBEDDING_FRAME,
            BOUNDARY_BARRIER,
            CAUSAL_LAYER,
            ANISOTROPIC_EDGES,
            MULTISCALE_SIGMA,
        }
    ),
    forbidden=frozenset(),
)

GRC9_CAPABILITY_PROFILE = CapabilityProfile(
    family="GRC9",
    required=frozenset(
        {
            PORT_GRAPH,
            MECHANICAL_REFINEMENT,
            COLUMN_COARSE_GRAINING,
            SINGLE_WEIGHT_EDGES,
            MULTI_METRIC_EDGES,
            INTRINSIC_FRAME,
        }
    ),
    optional=frozenset(
        {
            BOUNDARY_BARRIER,
            CAUSAL_LAYER,
            ANISOTROPIC_EDGES,
            MULTISCALE_SIGMA,
        }
    ),
    forbidden=frozenset(
        {
            BASIN_ATTRIBUTES,
            HIERARCHY_TRACKING,
            CHOICE_COLLAPSE_SEMANTICS,
            HOST_EMBEDDING_FRAME,
            QUADRATURE_BUDGET,
        }
    ),
)

GRC9V3_CAPABILITY_PROFILE = CapabilityProfile(
    family="GRC9V3",
    required=frozenset(
        {
            PORT_GRAPH,
            MECHANICAL_REFINEMENT,
            COLUMN_COARSE_GRAINING,
            BASIN_ATTRIBUTES,
            HIERARCHY_TRACKING,
            MULTI_METRIC_EDGES,
            CHOICE_COLLAPSE_SEMANTICS,
            QUADRATURE_BUDGET,
            INTRINSIC_FRAME,
        }
    ),
    optional=frozenset(
        {
            BOUNDARY_BARRIER,
            CAUSAL_LAYER,
            ANISOTROPIC_EDGES,
            MULTISCALE_SIGMA,
        }
    ),
    forbidden=frozenset({HOST_EMBEDDING_FRAME}),
)

FAMILY_CAPABILITY_PROFILES = {
    "GRCV2": GRCV2_CAPABILITY_PROFILE,
    "GRCV3": GRCV3_CAPABILITY_PROFILE,
    "GRC9": GRC9_CAPABILITY_PROFILE,
    "GRC9V3": GRC9V3_CAPABILITY_PROFILE,
}
