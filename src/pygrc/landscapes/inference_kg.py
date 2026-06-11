"""Dynamic knowledge-graph view over inferred landscape primitives.

The export in this module is intentionally a view of the existing
`LandscapeSeed` primitive language. It does not define a separate ontology.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference_basin import infer_landscape_basin_seed
from .inference_compare import (
    LandscapeInferenceComparisonReport,
    compare_landscape_seeds,
)
from .inference_junction import infer_landscape_junction_seed
from .inference_loader import LandscapeInferenceArtifactLoadResult
from .inference_pheromone import infer_landscape_pheromone_seed
from .inference_ridge import infer_landscape_ridge_seed
from .inference_substrate import (
    LandscapeInferenceEvidenceSubstrate,
    build_landscape_inference_evidence_substrate,
)
from .inference_valley import infer_landscape_valley_seed
from .io import landscape_seed_to_data, save_landscape_seed
from .seed import (
    BasinSeedPrimitive,
    JunctionSeedPrimitive,
    LandscapePrimitive,
    LandscapeSeed,
    PlateauSeedPrimitive,
    RidgeSeedPrimitive,
    ValleySeedPrimitive,
)


KG_VIEW_EXPORT_VERSION = "landscape_inference_iter9_v1"


def infer_combined_observed_landscape_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    authored_seed: LandscapeSeed | None = None,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
) -> LandscapeSeed:
    """Run all Iteration 3-7 classifiers and merge their observed primitives."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    classifier_seeds = (
        infer_landscape_basin_seed(
            load_result,
            substrate=resolved_substrate,
            authored_seed=authored_seed,
        ),
        infer_landscape_valley_seed(
            load_result,
            substrate=resolved_substrate,
            authored_seed=authored_seed,
        ),
        infer_landscape_ridge_seed(load_result, substrate=resolved_substrate),
        infer_landscape_junction_seed(load_result, substrate=resolved_substrate),
        infer_landscape_pheromone_seed(load_result, substrate=resolved_substrate),
    )

    primitives_by_id: dict[str, LandscapePrimitive] = {}
    for primitive in load_result.inferred_seed.primitives:
        primitives_by_id[primitive.id] = primitive
    for seed in classifier_seeds:
        for primitive in seed.primitives:
            primitives_by_id.setdefault(primitive.id, primitive)

    extensions = dict(load_result.inferred_seed.extensions)
    for seed in classifier_seeds:
        for key, value in seed.extensions.items():
            if key != "landscape_inference":
                extensions[key] = value
    extensions["landscape_inference_combined_summary"] = canonicalize_json_value(
        {
            "export_version": KG_VIEW_EXPORT_VERSION,
            "classifier_count": len(classifier_seeds),
            "primitive_count": len(primitives_by_id),
            "primitive_counts_by_type": dict(
                sorted(Counter(primitive.type for primitive in primitives_by_id.values()).items())
            ),
        }
    )
    return LandscapeSeed(
        seed_schema=load_result.inferred_seed.seed_schema,
        seed_version=load_result.inferred_seed.seed_version,
        meta=load_result.inferred_seed.meta,
        constitutive_profile=load_result.inferred_seed.constitutive_profile,
        primitives=sorted(primitives_by_id.values(), key=lambda primitive: primitive.id),
        transport_intent=list(load_result.inferred_seed.transport_intent),
        geometry_hints=load_result.inferred_seed.geometry_hints,
        extensions=extensions,
    )


def landscape_seed_to_dynamic_kg_view(
    seed: LandscapeSeed,
    *,
    source_seed_path: str | Path | None = None,
    observed_seed_path: str | Path | None = None,
    source_artifact_root: str | Path | None = None,
    comparison_report: LandscapeInferenceComparisonReport | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic KG-style view over landscape seed primitives."""

    nodes = tuple(_kg_node(primitive) for primitive in sorted(seed.primitives, key=lambda item: item.id))
    edges = _kg_edges(seed.primitives)
    comparison = (
        comparison_report.to_mapping()
        if isinstance(comparison_report, LandscapeInferenceComparisonReport)
        else comparison_report
    )
    return canonicalize_json_value(
        {
            "export_version": KG_VIEW_EXPORT_VERSION,
            "view_kind": "dynamic_knowledge_graph_export",
            "ontology_source": "pygrc_landscape_seed_primitives",
            "introduces_new_ontology": False,
            "seed_name": seed.meta.name,
            "source_kind": seed.meta.source_kind,
            "source_seed_path": None if source_seed_path is None else str(source_seed_path),
            "observed_seed_path": None if observed_seed_path is None else str(observed_seed_path),
            "source_artifact_root": None if source_artifact_root is None else str(source_artifact_root),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": list(nodes),
            "edges": list(edges),
            "comparison_summary": None if comparison is None else _comparison_summary(comparison),
        }
    )


def write_dynamic_kg_view(
    seed: LandscapeSeed,
    output_path: str | Path,
    *,
    source_seed_path: str | Path | None = None,
    observed_seed_path: str | Path | None = None,
    source_artifact_root: str | Path | None = None,
    comparison_report: LandscapeInferenceComparisonReport | Mapping[str, Any] | None = None,
) -> Path:
    """Write a deterministic KG-view JSON artifact."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            landscape_seed_to_dynamic_kg_view(
                seed,
                source_seed_path=source_seed_path,
                observed_seed_path=observed_seed_path,
                source_artifact_root=source_artifact_root,
                comparison_report=comparison_report,
            ),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def write_inferred_landscape_and_kg_view(
    load_result: LandscapeInferenceArtifactLoadResult,
    output_root: str | Path,
    *,
    authored_seed: LandscapeSeed | None = None,
    source_seed_path: str | Path | None = None,
) -> dict[str, Any]:
    """Infer an observed landscape, compare it, and export a KG view."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    observed_seed = infer_combined_observed_landscape_seed(
        load_result,
        authored_seed=authored_seed,
    )
    observed_seed_path = root / "observed_landscape_seed.json"
    save_landscape_seed(observed_seed, observed_seed_path)
    comparison_report = None
    comparison_path = None
    if authored_seed is not None:
        comparison_report = compare_landscape_seeds(authored_seed, observed_seed)
        comparison_path = root / "authored_vs_observed_comparison.json"
        comparison_path.write_text(
            json.dumps(comparison_report.to_mapping(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    kg_view_path = write_dynamic_kg_view(
        observed_seed,
        root / "dynamic_kg_view.json",
        source_seed_path=source_seed_path,
        observed_seed_path=observed_seed_path,
        source_artifact_root=load_result.artifact_root,
        comparison_report=comparison_report,
    )
    return canonicalize_json_value(
        {
            "artifact_root": str(load_result.artifact_root),
            "runtime_family": load_result.source_runtime_family,
            "observed_seed_path": str(observed_seed_path),
            "kg_view_path": str(kg_view_path),
            "comparison_path": None if comparison_path is None else str(comparison_path),
            "primitive_count": len(observed_seed.primitives),
            "primitive_counts_by_type": dict(
                sorted(Counter(primitive.type for primitive in observed_seed.primitives).items())
            ),
        }
    )


def _kg_node(primitive: LandscapePrimitive) -> dict[str, Any]:
    evidence = primitive.extensions.get("landscape_inference", {})
    inference_extension_keys = tuple(
        sorted(key for key in primitive.extensions if key.startswith("landscape_inference"))
    )
    evidence_payload = _mapping_value(evidence, "evidence")
    if evidence_payload is None:
        evidence_payload = {"extension_keys": list(inference_extension_keys)}
    return canonicalize_json_value(
        {
            "id": primitive.id,
            "primitive_type": primitive.type,
            "label": primitive.label or primitive.id,
            "role": primitive.role,
            "tags": list(primitive.tags),
            "authority": _mapping_value(evidence, "authority"),
            "confidence": _mapping_value(evidence, "confidence"),
            "classifier_id": _mapping_value(evidence, "classifier_id"),
            "relationship_to_authored": _mapping_value(evidence, "relationship_to_authored"),
            "evidence": evidence_payload,
            "inference_extension_keys": list(inference_extension_keys),
        }
    )


def _kg_edges(primitives: Sequence[LandscapePrimitive]) -> tuple[dict[str, Any], ...]:
    primitive_ids = {primitive.id for primitive in primitives}
    edges: list[dict[str, Any]] = []
    for primitive in sorted(primitives, key=lambda item: item.id):
        edges.extend(_primitive_edges(primitive, primitive_ids))
    return tuple(sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["relation"], edge["id"])))


def _primitive_edges(
    primitive: LandscapePrimitive,
    primitive_ids: set[str],
) -> tuple[dict[str, Any], ...]:
    edges: list[dict[str, Any]] = []
    if isinstance(primitive, BasinSeedPrimitive | PlateauSeedPrimitive):
        if primitive.parent_id:
            edges.append(_edge(primitive.parent_id, primitive.id, "contains", primitive.id))
        for boundary_id in primitive.boundary_ids:
            edges.append(_edge(primitive.id, boundary_id, "bounded_by", primitive.id))
    if isinstance(primitive, RidgeSeedPrimitive):
        if primitive.owner_id:
            edges.append(_edge(primitive.owner_id, primitive.id, "owns_boundary", primitive.id))
        for adjacent_id in primitive.adjacent_ids:
            edges.append(_edge(primitive.id, adjacent_id, "separates_or_touches", primitive.id))
    if isinstance(primitive, ValleySeedPrimitive):
        if primitive.from_id:
            edges.append(_edge(primitive.from_id, primitive.id, "opens_into_channel", primitive.id))
        if primitive.to_id:
            edges.append(_edge(primitive.id, primitive.to_id, "channels_to", primitive.id))
    if isinstance(primitive, JunctionSeedPrimitive):
        if primitive.host_id:
            edges.append(_edge(primitive.host_id, primitive.id, "hosts_junction", primitive.id))
        for target_id in primitive.branch_target_ids:
            edges.append(_edge(primitive.id, target_id, "routes_to", primitive.id))
    return tuple(edge for edge in edges if edge["source"] in primitive_ids or edge["target"] in primitive_ids)


def _edge(source: str, target: str, relation: str, primitive_id: str) -> dict[str, Any]:
    return {
        "id": f"{relation}:{source}->{target}:{primitive_id}",
        "source": source,
        "target": target,
        "relation": relation,
        "primitive_id": primitive_id,
    }


def _mapping_value(
    mapping: object,
    key: str,
    *,
    default: Any = None,
) -> Any:
    if isinstance(mapping, Mapping):
        return mapping.get(key, default)
    return default


def _comparison_summary(comparison: Mapping[str, Any]) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "classifier_id": comparison.get("classifier_id"),
            "classifier_version": comparison.get("classifier_version"),
            "relationship_counts": comparison.get("relationship_counts", {}),
            "candidate_count": comparison.get("candidate_count"),
        }
    )


__all__ = [
    "KG_VIEW_EXPORT_VERSION",
    "infer_combined_observed_landscape_seed",
    "landscape_seed_to_dynamic_kg_view",
    "write_dynamic_kg_view",
    "write_inferred_landscape_and_kg_view",
]
