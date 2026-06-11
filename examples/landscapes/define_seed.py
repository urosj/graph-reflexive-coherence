"""Define and save a normalized landscape seed.

What this example does:
    Builds a `LandscapeSeed` directly in Python, validates it, and writes it
    as YAML under `outputs/examples/landscapes/seeds/`.

Why it is needed:
    New users should see the shape of a landscape seed before loading one from
    disk. A seed is source-side data: basins, valleys, junctions, transport
    intent, geometry hints, and optional family-specific extensions.

Runtime boundary:
    This script does not run GRC9V3. It only defines source data. Runtime
    lowering and execution are shown in `run_seed_grc9v3.py`.

References:
    docs/reference/LandscapeLanguage-ReferenceGuide.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if SRC_ROOT.exists() and str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.landscapes import (  # noqa: E402
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapeSeed,
    RidgeSeedPrimitive,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedGeometryHints,
    SeedPotential,
    SeedTransportIntent,
    ValleySeedPrimitive,
    save_landscape_seed,
    validate_landscape_seed,
)


OUTPUT_ROOT = Path("outputs/examples/landscapes")
SEED_PATH = OUTPUT_ROOT / "seeds/example-grcl9v3-hybrid-spark.seed.yaml"


def build_example_seed() -> LandscapeSeed:
    """Build a small seed-backed GRCL9V3 landscape declaration.

    What is generic:
        `meta`, `constitutive_profile`, `primitives`, `transport_intent`, and
        `geometry_hints` are normalized landscape seed fields.

    What is family-specific:
        The `extensions["grcl9v3"]` payloads declare GRCL9V3 source terms. The
        later lowering script extracts and compiles those terms before
        constructing a GRC9V3 runtime state.
    """

    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(
            name="Example GRCL9V3 Hybrid Spark Landscape",
            source_kind="manual_seed",
            source_reference="examples/landscapes/define_seed.py",
            source_schema_version="0.1",
            source_domain="grcl9v3",
            description=(
                "Small seed-backed GRCL9V3 critical-region declaration for "
                "landscape examples."
            ),
            tags=["example", "landscape", "grcl9v3", "hybrid_spark"],
            translator_name="manual_example",
            translator_version="0.1",
            translation_mode="semantic_enrichment",
            translation_notes=[
                "This is source-side landscape data, not runtime evidence.",
                "Runtime events are produced only after lowering and execution.",
            ],
        ),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.5,
            zeta_c=0.8,
            kappa_c=1.0,
            dt=0.1,
            potential=SeedPotential(type="double_well", params={"a": 1.0, "b": 1.2}),
        ),
        primitives=[
            JunctionSeedPrimitive(
                id="candidate",
                type="saddle",
                coherence_prior=1.0,
                chart_center_hint=[0.5, 0.5],
                branch_target_ids=["support_a", "support_b", "support_c"],
                extensions={
                    "grcl9v3": {
                        "term_kind": "critical_region",
                        "term_id": "example_hybrid_spark_critical",
                        "region_id": "candidate",
                        "source_role": "positive_control",
                        "profile": {
                            "criticality": "hybrid_spark_gate",
                            "saturation": {
                                "active_degree": 9,
                                "port_chart": "nine_port_candidate",
                            },
                            "spark_gate_intent": "hybrid_hessian_tensor",
                            "spark_threshold": 0.05,
                        },
                    }
                },
            ),
            JunctionSeedPrimitive(
                id="hessian_profile",
                host_id="candidate",
                branch_target_ids=["support_a", "support_b"],
                extensions={
                    "grcl9v3": {
                        "term_kind": "tensor_hessian_profile",
                        "term_id": "example_hybrid_spark_hessian",
                        "region_id": "candidate",
                        "source_role": "positive_control",
                        "profile": {
                            "hessian_backend": "row_basis_diagonal",
                            "row_basis_profile": {
                                "hessian_mode": "anisotropic",
                                "basis": "row_basis_diagonal",
                            },
                            "signed_history_required": False,
                        },
                    }
                },
            ),
            RidgeSeedPrimitive(
                id="tensor_profile",
                owner_id="candidate",
                adjacent_ids=["support_b"],
                extensions={
                    "grcl9v3": {
                        "term_kind": "tensor_hessian_profile",
                        "term_id": "example_hybrid_spark_tensor",
                        "region_id": "candidate",
                        "source_role": "positive_control",
                        "profile": {
                            "anisotropy_axis": "row_2",
                            "tensor_profile": {
                                "tensor_mode": "anisotropic",
                                "row_mismatch": "high",
                            },
                        },
                    }
                },
            ),
            ValleySeedPrimitive(
                id="column_channel",
                from_id="support_a",
                to_id="candidate",
                extensions={
                    "grcl9v3": {
                        "term_kind": "valley_channel",
                        "term_id": "example_hybrid_spark_column_channel",
                        "region_id": "candidate",
                        "source_role": "positive_control",
                        "profile": {
                            "target_column": 2,
                            "cancellation_mode": "near_cancellation",
                            "column_profile": {"column_2": "near_cancellation"},
                        },
                    }
                },
            ),
            BasinSeedPrimitive(id="support_a", coherence_prior=0.5),
            BasinSeedPrimitive(id="support_b", coherence_prior=0.5),
            BasinSeedPrimitive(id="support_c", coherence_prior=0.5),
        ],
        transport_intent=[
            SeedTransportIntent(
                id="column_flow_hint",
                mode="directed_bias",
                sources=["support_a"],
                targets=["candidate"],
                carrier_id="column_channel",
                notes="Source-side transport intent; runtime flux is not claimed here.",
            )
        ],
        geometry_hints=SeedGeometryHints(
            source_chart="example_planar_hint",
            coordinate_convention="unit_square",
        ),
        extensions={
            "grcl9v3": {
                "contract_version": "grcl9v3.landscape_example.v1",
                "grcl9v3_required": True,
                "example_name": "hybrid_spark_gate_positive_control",
                "manifest_entry_id": "grcl9v3_lowering_hybrid_spark_gate_v1",
                "motif_id": "grc9v3-motif-s0006-hybrid-spark-gate-positive-control",
                "expected_selector_ids": [
                    "hybrid_spark_events",
                    "hybrid_tensor_available",
                ],
                "notes": {
                    "boundary": "source preconditions only",
                    "runtime_target": "GRC9V3 after lowering",
                },
            }
        },
    )


def save_example_seed() -> LandscapeSeed:
    """Validate and save the example seed."""

    seed = build_example_seed()
    validate_landscape_seed(seed)
    save_landscape_seed(seed, SEED_PATH)
    return seed


def _summary(seed: LandscapeSeed) -> dict[str, Any]:
    return {
        "path": str(SEED_PATH),
        "name": seed.meta.name,
        "primitive_count": len(seed.primitives),
        "primitive_ids": [primitive.id for primitive in seed.primitives],
        "transport_intent_count": len(seed.transport_intent),
        "extension_namespaces": sorted(seed.extensions),
    }


def main() -> None:
    seed = save_example_seed()
    print("Defined landscape seed")
    print(json.dumps(_summary(seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
