"""Private shared helpers for GRCV3 trace experiments."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    build_backend_selection,
    build_backend_selection_payload,
)
from pygrc.landscapes import load_landscape_seed
from pygrc.models import (
    DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    GRCV3,
    build_grcv3_from_landscape_seed,
    resolve_grcv3_landscape_params,
)

from ._grcv3_extensions import (
    _build_grcv3_observed_interior_site,
    _signed_hessian_eigenvalues,
)
from ._telemetry_utils import _to_plain_data, _vector_norm


def _build_grcv3_failure_trace_model(
    seed_path: str | Path,
    *,
    profile_name: str,
    overrides: Mapping[str, Any] | None = None,
) -> tuple[Path, Any, GRCV3]:
    resolved_seed_path = Path(seed_path)
    seed = load_landscape_seed(resolved_seed_path)
    params = resolve_grcv3_landscape_params(
        seed,
        profile_name=profile_name,
        overrides=overrides,
        validate_seed=False,
    )
    model = build_grcv3_from_landscape_seed(
        seed,
        params=params,
        profile_name=profile_name,
        validate_seed=False,
    )
    model.rebuild_basin_attributes()
    model.rebuild_identity_state()
    return resolved_seed_path, seed, model


def _default_grcv3_choice_collapse_overrides(
    *,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    return {
        "constitutive_semantic_modes": {
            BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                [
                    build_backend_selection(
                        category="choice",
                        name="sink_compatibility",
                        params={
                            "epsilon_choice": float(epsilon_choice),
                            "epsilon_collapse": float(epsilon_collapse),
                        },
                    )
                ]
            )
        }
    }


def _build_grcv3_failure_trace_node_summary(
    model: GRCV3,
    *,
    node_id: int,
) -> dict[str, Any]:
    state = model.get_state()
    attributes = state.nodes[node_id]
    return {
        "node_id": int(node_id),
        "gradient_norm": float(_vector_norm(attributes.gradient)),
        "net_flux_norm": float(_vector_norm(attributes.net_flux)),
        "potential": float(state.potential.get(node_id, 0.0)),
        "coherence": float(attributes.coherence),
        "min_signed_eigenvalue": (
            min(ordered_eigenvalues)
            if (ordered_eigenvalues := _signed_hessian_eigenvalues(model, node_id=node_id))
            else None
        ),
        "max_signed_eigenvalue": (
            max(ordered_eigenvalues)
            if (ordered_eigenvalues := _signed_hessian_eigenvalues(model, node_id=node_id))
            else None
        ),
    }


def _build_grcv3_failure_trace_probe_roles(
    model: GRCV3,
    *,
    primitive_id: str,
) -> dict[str, dict[str, Any]]:
    state = model.get_state()
    probe_role_maps = state.cached_quantities.get(
        "landscape_grcv3_probe_role_node_ids_by_primitive_id",
        {},
    )
    if not isinstance(probe_role_maps, Mapping):
        return {}
    probe_role_map = probe_role_maps.get(primitive_id, {})
    if not isinstance(probe_role_map, Mapping):
        return {}
    return {
        str(role): _build_grcv3_failure_trace_node_summary(model, node_id=int(node_id))
        for role, node_id in sorted(probe_role_map.items())
        if int(node_id) in state.nodes
    }


def _build_grcv3_failure_trace_path_nodes(
    model: GRCV3,
    *,
    primitive_id: str,
) -> dict[str, Any]:
    state = model.get_state()
    path_node_maps = state.cached_quantities.get(
        "landscape_grcv3_transfer_path_node_ids_by_pair_by_primitive_id",
        {},
    )
    if not isinstance(path_node_maps, Mapping):
        return {"path_node_count": 0, "nodes": {}}
    path_node_map = path_node_maps.get(primitive_id, {})
    if not isinstance(path_node_map, Mapping):
        return {"path_node_count": 0, "nodes": {}}
    nodes = {
        str(pair_label): _build_grcv3_failure_trace_node_summary(model, node_id=int(node_id))
        for pair_label, node_id in sorted(path_node_map.items())
        if int(node_id) in state.nodes
    }
    return {
        "path_node_count": len(nodes),
        "nodes": nodes,
    }


def _build_grcv3_failure_trace_edge_roles(
    model: GRCV3,
    *,
    primitive_id: str,
) -> dict[str, dict[str, Any]]:
    state = model.get_state()
    edge_roles = {
        "basin_patch_support_spoke",
        "basin_patch_load_carrier_transfer",
        "basin_patch_transfer_path_ingress",
        "basin_patch_transfer_path_egress",
        "basin_patch_transfer_mediation_spill",
    }
    summaries = {
        edge_role: {
            "edge_count": 0,
            "total_conductance": 0.0,
            "total_abs_flux": 0.0,
        }
        for edge_role in edge_roles
    }
    for edge_id in state.topology.iter_live_edge_ids():
        payload = state.topology.edge_payload(edge_id)
        if str(payload.get("primitive_id")) != primitive_id:
            continue
        metadata = payload.get("metadata", {})
        edge_role = (
            str(metadata.get("motif_edge_role"))
            if isinstance(metadata, Mapping)
            else str(payload.get("edge_role"))
        )
        if edge_role not in summaries:
            continue
        node_a, _ = state.topology.edge_endpoints(edge_id)
        summaries[edge_role]["edge_count"] += 1
        summaries[edge_role]["total_conductance"] += float(
            state.base_conductance.get(edge_id, 0.0)
        )
        summaries[edge_role]["total_abs_flux"] += abs(
            float(state.flux.get((edge_id, node_a), 0.0))
        )
    return {edge_role: dict(sorted(summary.items())) for edge_role, summary in sorted(summaries.items())}


def _build_grcv3_failure_trace_step_observation(
    model: GRCV3,
    *,
    primitive_id: str,
    event_kinds: tuple[str, ...] = (),
) -> dict[str, Any]:
    probe_roles = _build_grcv3_failure_trace_probe_roles(
        model,
        primitive_id=primitive_id,
    )
    probe_gradient_values = [
        float(summary.get("gradient_norm", 0.0)) for summary in probe_roles.values()
    ]
    center_site = _build_grcv3_observed_interior_site(model, primitive_id=primitive_id)
    return {
        "center_site": (
            None
            if center_site is None
            else {
                "primitive_id": center_site.primitive_id,
                "node_id": center_site.node_id,
                "gradient_norm": center_site.gradient_norm,
                "min_signed_eigenvalue": center_site.min_signed_eigenvalue,
                "max_signed_eigenvalue": center_site.max_signed_eigenvalue,
                "weak_mode_signed_curvature": center_site.weak_mode_signed_curvature,
                "gradient_gate_pass": center_site.gradient_gate_pass,
                "geometric_validation_pass": center_site.geometric_validation_pass,
                "spark_candidate_regime": center_site.spark_candidate_regime,
            }
        ),
        "probe_roles": probe_roles,
        "probe_gradient_spread": (
            max(probe_gradient_values) - min(probe_gradient_values)
            if probe_gradient_values
            else 0.0
        ),
        "path_nodes": _build_grcv3_failure_trace_path_nodes(
            model,
            primitive_id=primitive_id,
        ),
        "edge_roles": _build_grcv3_failure_trace_edge_roles(
            model,
            primitive_id=primitive_id,
        ),
        "event_kinds": list(event_kinds),
    }


def _build_grcv3_candidate_gate_summary(
    *,
    gradient_norm: float,
    signed_eigenvalues: list[float] | tuple[float, ...],
    eps_gradient: float,
    eps_hessian: float,
    eps_spark: float,
) -> dict[str, Any]:
    ordered_eigenvalues = sorted(float(value) for value in signed_eigenvalues)
    return {
        "gradient_norm": float(gradient_norm),
        "signed_eigenvalues": list(ordered_eigenvalues),
        "epsilon_gradient": float(eps_gradient),
        "epsilon_hessian": float(eps_hessian),
        "epsilon_spark": float(eps_spark),
        "gradient_below_threshold": float(gradient_norm) < float(eps_gradient),
        "weak_eigen_below_spark": bool(ordered_eigenvalues)
        and float(ordered_eigenvalues[0]) < float(eps_spark),
        "stable_eigenvalues_above_hessian": all(
            float(value) > float(eps_hessian) for value in ordered_eigenvalues[1:]
        ),
        "candidate_gate_pass": (
            float(gradient_norm) < float(eps_gradient)
            and bool(ordered_eigenvalues)
            and float(ordered_eigenvalues[0]) < float(eps_spark)
            and all(float(value) > float(eps_hessian) for value in ordered_eigenvalues[1:])
        ),
    }


def _build_grcv3_candidate_site_summary(
    model: GRCV3,
    *,
    node_id: int,
) -> dict[str, Any]:
    state = model.get_state()
    payload = state.topology.node_payload(node_id)
    metadata = payload.get("metadata", {})
    gate_summary = _build_grcv3_candidate_gate_summary(
        gradient_norm=float(_vector_norm(state.nodes[node_id].gradient)),
        signed_eigenvalues=_signed_hessian_eigenvalues(model, node_id=node_id),
        eps_gradient=float(model.get_params().evolution["eps_gradient"]),
        eps_hessian=float(model.get_params().evolution["eps_hessian"]),
        eps_spark=float(model.get_params().evolution["eps_spark"]),
    )
    return {
        "node_id": int(node_id),
        "realized_key": str(payload.get("realized_key")),
        "motif_role": str(payload.get("motif_role")),
        "role_label": (
            str(metadata.get("grcv3_role_label"))
            if isinstance(metadata, Mapping) and metadata.get("grcv3_role_label") is not None
            else None
        ),
        "coherence": float(state.nodes[node_id].coherence),
        "net_flux_norm": float(_vector_norm(state.nodes[node_id].net_flux)),
        "potential": float(state.potential.get(node_id, 0.0)),
        **gate_summary,
    }


def _grcv3_realized_key_to_node_id(model: GRCV3) -> dict[str, int]:
    state = model.get_state()
    return {
        str(payload.get("realized_key")): int(node_id)
        for node_id in state.topology.iter_live_node_ids()
        if (payload := state.topology.node_payload(node_id)).get("realized_key") is not None
    }


def _update_grcv3_node_snapshot_cache(
    model: GRCV3,
    cache: dict[int, dict[str, Any]],
) -> None:
    state = model.get_state()
    for node_id in state.topology.iter_live_node_ids():
        payload = state.topology.node_payload(node_id)
        metadata = payload.get("metadata", {})
        cache[int(node_id)] = {
            "node_id": int(node_id),
            "kind": (
                str(payload.get("kind"))
                if payload.get("kind") is not None
                else None
            ),
            "motif_role": (
                str(payload.get("motif_role"))
                if payload.get("motif_role") is not None
                else None
            ),
            "realized_key": (
                str(payload.get("realized_key"))
                if payload.get("realized_key") is not None
                else None
            ),
            "role_label": (
                str(metadata.get("grcv3_role_label"))
                if isinstance(metadata, Mapping) and metadata.get("grcv3_role_label") is not None
                else None
            ),
            "parent_node_id": (
                int(payload.get("parent_node_id"))
                if payload.get("parent_node_id") is not None
                else None
            ),
            "child_index": (
                int(payload.get("child_index"))
                if payload.get("child_index") is not None
                else None
            ),
        }


def _grcv3_site_kind_from_snapshot(snapshot: Mapping[str, Any] | None) -> str | None:
    if snapshot is None:
        return None
    motif_role = snapshot.get("motif_role")
    kind = snapshot.get("kind")
    if motif_role == "basin_load_carrier":
        return "carrier_site"
    if motif_role == "basin_transfer_path_node":
        return "path_node"
    if kind == "split_child":
        return "split_child"
    if motif_role is not None:
        return str(motif_role)
    if kind is not None:
        return str(kind)
    return None


def _build_grcv3_event_anchor_site_summary(
    node_id: int | None,
    *,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any] | None:
    if node_id is None:
        return None
    snapshot = snapshot_cache.get(int(node_id))
    if snapshot is None:
        return {
            "node_id": int(node_id),
            "site_kind": None,
            "motif_role": None,
            "realized_key": None,
            "role_label": None,
            "parent_node_id": None,
            "child_index": None,
        }
    return {
        "node_id": int(node_id),
        "site_kind": _grcv3_site_kind_from_snapshot(snapshot),
        "motif_role": snapshot.get("motif_role"),
        "realized_key": snapshot.get("realized_key"),
        "role_label": snapshot.get("role_label"),
        "parent_node_id": snapshot.get("parent_node_id"),
        "child_index": snapshot.get("child_index"),
    }


def _grcv3_event_anchor_node_id(payload: Mapping[str, Any]) -> int | None:
    for key in ("node_id", "parent_node_id", "basin_id", "parent_basin_id"):
        value = payload.get(key)
        if value is not None:
            return int(value)
    return None


def _build_grcv3_event_locus_record(
    step_index: int,
    *,
    event: Any,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    payload = event.payload if isinstance(event.payload, Mapping) else {}
    anchor_node_id = _grcv3_event_anchor_node_id(payload)
    return {
        "step_index": int(step_index),
        "event_kind": str(event.kind),
        "registry_key": (
            str(payload.get("registry_key"))
            if payload.get("registry_key") is not None
            else None
        ),
        "anchor_site": _build_grcv3_event_anchor_site_summary(
            anchor_node_id,
            snapshot_cache=snapshot_cache,
        ),
        "event_payload": {
            str(key): _to_plain_data(value)
            for key, value in payload.items()
        },
    }


def _build_grcv3_settlement_regime_summary(
    *,
    steps: list[dict[str, Any]],
    side: str,
    event_loci: list[dict[str, Any]],
) -> dict[str, Any]:
    tracked_kinds = ("spark_candidate", "split_init", "spark", "split_complete")
    loci_by_kind: dict[str, list[dict[str, Any]]] = {
        kind: [record for record in event_loci if record["event_kind"] == kind]
        for kind in tracked_kinds
    }
    first_event_steps = {
        kind: (
            None if not loci_by_kind[kind] else int(loci_by_kind[kind][0]["step_index"])
        )
        for kind in tracked_kinds
    }
    first_candidate = loci_by_kind["spark_candidate"][0] if loci_by_kind["spark_candidate"] else None
    first_candidate_site = None if first_candidate is None else first_candidate.get("anchor_site")
    first_candidate_step = first_event_steps["spark_candidate"]
    pre_first_candidate_signature = None
    if first_candidate_step is not None and first_candidate_step > 0:
        pre_step = steps[first_candidate_step - 1][side]
        pre_first_candidate_signature = {
            "step_index": int(first_candidate_step - 1),
            "center_min_signed_eigenvalue": pre_step["center_site"]["min_signed_eigenvalue"],
            "probe_gradient_spread": pre_step["probe_gradient_spread"],
            "path_node_count": pre_step["path_nodes"]["path_node_count"],
        }
    first_anchor_node_id = None
    if isinstance(first_candidate_site, Mapping) and first_candidate_site.get("node_id") is not None:
        first_anchor_node_id = int(first_candidate_site["node_id"])
    first_lifecycle_records: dict[str, dict[str, Any] | None] = {}
    for kind in tracked_kinds:
        match = None
        for record in loci_by_kind[kind]:
            site = record.get("anchor_site")
            if (
                first_anchor_node_id is not None
                and isinstance(site, Mapping)
                and site.get("node_id") is not None
                and int(site["node_id"]) == first_anchor_node_id
            ):
                match = record
                break
        first_lifecycle_records[kind] = match
    lifecycle_anchor_ids = [
        int(record["anchor_site"]["node_id"])
        for record in first_lifecycle_records.values()
        if isinstance(record, Mapping)
        and isinstance(record.get("anchor_site"), Mapping)
        and record["anchor_site"].get("node_id") is not None
    ]
    later_candidate_records = (
        []
        if not loci_by_kind["spark_candidate"]
        else loci_by_kind["spark_candidate"][1:]
    )
    later_candidate_site_kinds = [
        record["anchor_site"]["site_kind"]
        for record in later_candidate_records
        if isinstance(record.get("anchor_site"), Mapping)
    ]
    regime_label = None
    if isinstance(first_candidate_site, Mapping):
        regime_label = {
            "carrier_site": "carrier_site_regime",
            "path_node": "path_node_regime",
            "split_child": "split_child_regime",
        }.get(first_candidate_site.get("site_kind"), "other_regime")
    return {
        "first_event_steps": first_event_steps,
        "pre_first_candidate_signature": pre_first_candidate_signature,
        "first_candidate_sites": [
            record["anchor_site"]
            for record in loci_by_kind["spark_candidate"]
            if first_candidate_step is not None
            and int(record["step_index"]) == int(first_candidate_step)
        ],
        "first_lifecycle_anchor": {
            "site": first_candidate_site,
            "stable_through_split_complete": (
                len(set(lifecycle_anchor_ids)) == 1 and len(lifecycle_anchor_ids) >= 3
            ),
            "spark_candidate": first_lifecycle_records["spark_candidate"],
            "split_init": first_lifecycle_records["split_init"],
            "spark": first_lifecycle_records["spark"],
            "split_complete": first_lifecycle_records["split_complete"],
        },
        "later_candidate_migration": {
            "occurs": bool(later_candidate_records),
            "site_kinds": sorted({kind for kind in later_candidate_site_kinds if kind is not None}),
            "records": later_candidate_records,
        },
        "event_loci_by_kind": loci_by_kind,
        "regime_label": regime_label,
    }


def _center_negative_curvature_run_length(
    steps: list[dict[str, Any]],
    *,
    side: str,
    end_step_index: int,
) -> int:
    run_length = 0
    for step_index in range(end_step_index, -1, -1):
        center_site = steps[step_index].get(side, {}).get("center_site")
        if not isinstance(center_site, Mapping):
            break
        min_signed_eigenvalue = center_site.get("min_signed_eigenvalue")
        if min_signed_eigenvalue is None or float(min_signed_eigenvalue) >= 0.0:
            break
        run_length += 1
    return run_length


def _grcv3_optional_node_id(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _grcv3_node_descends_from_anchor(
    node_id: int,
    *,
    anchor_node_id: int,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> bool:
    current_node_id = int(node_id)
    target_node_id = int(anchor_node_id)
    visited: set[int] = set()
    while current_node_id not in visited:
        visited.add(current_node_id)
        if current_node_id == target_node_id:
            return True
        snapshot = snapshot_cache.get(current_node_id)
        if not isinstance(snapshot, Mapping):
            return False
        parent_node_id = snapshot.get("parent_node_id")
        if parent_node_id is None:
            return False
        current_node_id = int(parent_node_id)
    return False


def _build_grcv3_split_descendant_site_summary(
    model: GRCV3,
    *,
    node_id: int,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    state = model.get_state()
    anchor_site = _build_grcv3_event_anchor_site_summary(
        int(node_id),
        snapshot_cache=snapshot_cache,
    )
    candidate_site = _build_grcv3_candidate_site_summary(
        model,
        node_id=int(node_id),
    )
    neighborhood_records: list[dict[str, Any]] = []
    total_weight_by_neighbor_site_kind: dict[str, float] = {}
    total_weight_by_neighbor_motif_role: dict[str, float] = {}
    for edge_id in state.topology.incident_edge_ids(int(node_id)):
        node_a, node_b = state.topology.edge_endpoints(edge_id)
        neighbor_node_id = int(node_b if node_a == int(node_id) else node_a)
        neighbor_site = _build_grcv3_event_anchor_site_summary(
            neighbor_node_id,
            snapshot_cache=snapshot_cache,
        )
        edge_payload = state.topology.edge_payload(edge_id)
        edge_weight = float(state.base_conductance.get(edge_id, 0.0))
        neighbor_site_kind = (
            None
            if not isinstance(neighbor_site, Mapping)
            else neighbor_site.get("site_kind")
        )
        neighbor_motif_role = (
            None
            if not isinstance(neighbor_site, Mapping)
            else neighbor_site.get("motif_role")
        )
        if isinstance(neighbor_site_kind, str):
            total_weight_by_neighbor_site_kind[neighbor_site_kind] = (
                float(total_weight_by_neighbor_site_kind.get(neighbor_site_kind, 0.0))
                + edge_weight
            )
        if isinstance(neighbor_motif_role, str):
            total_weight_by_neighbor_motif_role[neighbor_motif_role] = (
                float(total_weight_by_neighbor_motif_role.get(neighbor_motif_role, 0.0))
                + edge_weight
            )
        neighborhood_records.append(
            {
                "edge_id": int(edge_id),
                "edge_kind": (
                    str(edge_payload.get("kind"))
                    if edge_payload.get("kind") is not None
                    else None
                ),
                "edge_weight": edge_weight,
                "neighbor_site": neighbor_site,
            }
        )
    return {
        **({} if anchor_site is None else anchor_site),
        **candidate_site,
        "neighborhood_signature": {
            "degree": len(neighborhood_records),
            "neighbor_site_kinds": sorted(
                {
                    str(record["neighbor_site"]["site_kind"])
                    for record in neighborhood_records
                    if isinstance(record.get("neighbor_site"), Mapping)
                    and record["neighbor_site"].get("site_kind") is not None
                }
            ),
            "neighbor_motif_roles": sorted(
                {
                    str(record["neighbor_site"]["motif_role"])
                    for record in neighborhood_records
                    if isinstance(record.get("neighbor_site"), Mapping)
                    and record["neighbor_site"].get("motif_role") is not None
                }
            ),
            "edge_kinds": sorted(
                {
                    str(record["edge_kind"])
                    for record in neighborhood_records
                    if record.get("edge_kind") is not None
                }
            ),
            "total_weight_by_neighbor_site_kind": {
                key: float(value)
                for key, value in sorted(total_weight_by_neighbor_site_kind.items())
            },
            "total_weight_by_neighbor_motif_role": {
                key: float(value)
                for key, value in sorted(total_weight_by_neighbor_motif_role.items())
            },
            "records": neighborhood_records,
        },
    }


def _collect_grcv3_split_descendant_site_summaries(
    model: GRCV3,
    *,
    anchor_node_id: int,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    state = model.get_state()
    descendant_sites: list[dict[str, Any]] = []
    for node_id in sorted(state.topology.iter_live_node_ids()):
        payload = state.topology.node_payload(node_id)
        if payload.get("kind") != "split_child":
            continue
        if not _grcv3_node_descends_from_anchor(
            int(node_id),
            anchor_node_id=int(anchor_node_id),
            snapshot_cache=snapshot_cache,
        ):
            continue
        descendant_sites.append(
            _build_grcv3_split_descendant_site_summary(
                model,
                node_id=int(node_id),
                snapshot_cache=snapshot_cache,
            )
        )
    return descendant_sites


def _collect_grcv3_split_descendant_candidate_sites(
    *,
    step_index: int,
    events: list[Any],
    anchor_node_id: int,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    descendant_candidate_sites: list[dict[str, Any]] = []
    for event in events:
        if event.kind != "spark_candidate":
            continue
        payload = event.payload if isinstance(event.payload, Mapping) else {}
        node_id = _grcv3_event_anchor_node_id(payload)
        if node_id is None:
            continue
        anchor_site = _build_grcv3_event_anchor_site_summary(
            int(node_id),
            snapshot_cache=snapshot_cache,
        )
        if not isinstance(anchor_site, Mapping):
            continue
        if anchor_site.get("site_kind") != "split_child":
            continue
        if not _grcv3_node_descends_from_anchor(
            int(node_id),
            anchor_node_id=int(anchor_node_id),
            snapshot_cache=snapshot_cache,
        ):
            continue
        descendant_candidate_sites.append(
            {
                "step_index": int(step_index),
                "event_kind": str(event.kind),
                "anchor_site": anchor_site,
                "event_payload": {
                    str(key): _to_plain_data(value)
                    for key, value in payload.items()
                },
            }
        )
    return descendant_candidate_sites


def _apply_grcv3_descendant_secondary_role_prune(
    model: GRCV3,
    *,
    anchor_node_id: int,
    target_motif_role: str,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    state = model.get_state()
    removed_edges: list[dict[str, Any]] = []
    descendant_ids = [
        int(node_id)
        for node_id in sorted(state.topology.iter_live_node_ids())
        if _grcv3_node_descends_from_anchor(
            int(node_id),
            anchor_node_id=int(anchor_node_id),
            snapshot_cache=snapshot_cache,
        )
    ]
    for node_id in descendant_ids:
        payload = state.topology.node_payload(node_id)
        if payload.get("kind") != "split_child":
            continue
        for edge_id in list(state.topology.incident_edge_ids(node_id)):
            node_a, node_b = state.topology.edge_endpoints(edge_id)
            neighbor_id = int(node_b if node_a == node_id else node_a)
            if not state.topology.has_node(neighbor_id):
                continue
            neighbor_payload = state.topology.node_payload(neighbor_id)
            if neighbor_payload.get("motif_role") != target_motif_role:
                continue
            edge_payload = state.topology.edge_payload(edge_id)
            removed_edges.append(
                {
                    "edge_id": int(edge_id),
                    "child_node_id": int(node_id),
                    "neighbor_node_id": int(neighbor_id),
                    "neighbor_motif_role": str(target_motif_role),
                    "edge_kind": (
                        str(edge_payload.get("kind"))
                        if edge_payload.get("kind") is not None
                        else None
                    ),
                }
            )
            state.topology.remove_edge(edge_id)
            state.base_conductance.pop(edge_id, None)
            for flux_key in tuple(state.flux):
                if int(flux_key[0]) == int(edge_id):
                    state.flux.pop(flux_key, None)
    model._cleanup_state_against_live_topology()
    model._refresh_after_topology_change()
    return removed_edges


def _build_grcv3_descendant_neighborhood_aggregate(
    descendant_sites: list[dict[str, Any]],
) -> dict[str, Any]:
    if not descendant_sites:
        return {
            "site_count": 0,
            "degree_set": [],
            "common_neighbor_site_kinds": [],
            "common_neighbor_motif_roles": [],
            "mean_gradient_norm": None,
            "mean_net_flux_norm": None,
            "mean_potential": None,
            "mean_total_weight_by_neighbor_site_kind": {},
            "mean_total_weight_by_neighbor_motif_role": {},
        }
    degree_set = sorted(
        {
            int(site.get("neighborhood_signature", {}).get("degree", 0))
            for site in descendant_sites
        }
    )
    site_kind_sets = [
        {
            str(value)
            for value in list(site.get("neighborhood_signature", {}).get("neighbor_site_kinds", []))
        }
        for site in descendant_sites
    ]
    motif_role_sets = [
        {
            str(value)
            for value in list(site.get("neighborhood_signature", {}).get("neighbor_motif_roles", []))
        }
        for site in descendant_sites
    ]
    common_neighbor_site_kinds = (
        sorted(set.intersection(*site_kind_sets))
        if site_kind_sets
        else []
    )
    common_neighbor_motif_roles = (
        sorted(set.intersection(*motif_role_sets))
        if motif_role_sets
        else []
    )
    mean_gradient_norm = sum(float(site.get("gradient_norm", 0.0)) for site in descendant_sites) / len(
        descendant_sites
    )
    mean_net_flux_norm = sum(float(site.get("net_flux_norm", 0.0)) for site in descendant_sites) / len(
        descendant_sites
    )
    mean_potential = sum(float(site.get("potential", 0.0)) for site in descendant_sites) / len(
        descendant_sites
    )
    site_kind_weight_totals: dict[str, float] = {}
    motif_role_weight_totals: dict[str, float] = {}
    for site in descendant_sites:
        neighborhood = site.get("neighborhood_signature", {})
        for key, value in dict(
            neighborhood.get("total_weight_by_neighbor_site_kind", {})
        ).items():
            site_kind_weight_totals[str(key)] = float(site_kind_weight_totals.get(str(key), 0.0)) + float(
                value
            )
        for key, value in dict(
            neighborhood.get("total_weight_by_neighbor_motif_role", {})
        ).items():
            motif_role_weight_totals[str(key)] = float(
                motif_role_weight_totals.get(str(key), 0.0)
            ) + float(value)
    return {
        "site_count": len(descendant_sites),
        "degree_set": degree_set,
        "common_neighbor_site_kinds": common_neighbor_site_kinds,
        "common_neighbor_motif_roles": common_neighbor_motif_roles,
        "mean_gradient_norm": float(mean_gradient_norm),
        "mean_net_flux_norm": float(mean_net_flux_norm),
        "mean_potential": float(mean_potential),
        "mean_total_weight_by_neighbor_site_kind": {
            key: float(value / len(descendant_sites))
            for key, value in sorted(site_kind_weight_totals.items())
        },
        "mean_total_weight_by_neighbor_motif_role": {
            key: float(value / len(descendant_sites))
            for key, value in sorted(motif_role_weight_totals.items())
        },
    }


def _build_grcv3_lane_neighborhood_boundary_summary(
    lane: Mapping[str, Any],
    *,
    matched_step_index: int | None,
) -> dict[str, Any]:
    descendant_records = [
        record
        for record in list(lane.get("descendant_records", []))
        if isinstance(record, Mapping)
    ]
    matched_record = next(
        (
            record
            for record in descendant_records
            if matched_step_index is not None and int(record.get("step_index", -1)) == int(matched_step_index)
        ),
        None,
    )
    final_record = None if not descendant_records else descendant_records[-1]
    return {
        "first_split_complete_step": lane.get("first_split_complete_step"),
        "first_reentry_gate_pass_step": lane.get("first_reentry_gate_pass_step"),
        "first_reentry_candidate_step": lane.get("first_reentry_candidate_step"),
        "matched_step_record": (
            None
            if not isinstance(matched_record, Mapping)
            else {
                "step_index": int(matched_record["step_index"]),
                "aggregate": _build_grcv3_descendant_neighborhood_aggregate(
                    list(matched_record.get("descendant_sites", []))
                ),
                "descendant_sites": list(matched_record.get("descendant_sites", [])),
            }
        ),
        "final_record": (
            None
            if not isinstance(final_record, Mapping)
            else {
                "step_index": int(final_record["step_index"]),
                "aggregate": _build_grcv3_descendant_neighborhood_aggregate(
                    list(final_record.get("descendant_sites", []))
                ),
                "descendant_sites": list(final_record.get("descendant_sites", [])),
            }
        ),
    }


def _build_grcv3_secondary_neighbor_role_summary(
    aggregate: Mapping[str, Any],
) -> dict[str, Any]:
    mean_weights = {
        str(key): float(value)
        for key, value in dict(
            aggregate.get("mean_total_weight_by_neighbor_motif_role", {})
        ).items()
    }
    secondary_roles = sorted(
        role for role in mean_weights if role != "basin_support"
    )
    secondary_weights = {
        role: float(mean_weights[role])
        for role in secondary_roles
    }
    return {
        "degree_set": list(aggregate.get("degree_set", [])),
        "common_neighbor_motif_roles": list(
            aggregate.get("common_neighbor_motif_roles", [])
        ),
        "support_weight": float(mean_weights.get("basin_support", 0.0)),
        "secondary_roles": secondary_roles,
        "secondary_role_weights": secondary_weights,
    }


def _build_grcv3_seed_family_payloads(
    seed: Any,
    *,
    family_name: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for primitive in list(getattr(seed, "primitives", [])):
        extensions = getattr(primitive, "extensions", {})
        if not isinstance(extensions, Mapping):
            continue
        grcv3_extension = extensions.get("grcv3")
        if not isinstance(grcv3_extension, Mapping):
            continue
        if family_name not in grcv3_extension:
            continue
        records.append(
            {
                "primitive_id": str(getattr(primitive, "id")),
                "primitive_type": str(getattr(primitive, "type")),
                "payload": _to_plain_data(grcv3_extension[family_name]),
            }
        )
    return records


def _compare_grcv3_seed_family_payloads(
    left_seed: Any,
    right_seed: Any,
    *,
    family_names: list[str],
) -> dict[str, Any]:
    comparisons: dict[str, Any] = {}
    for family_name in family_names:
        left_payloads = _build_grcv3_seed_family_payloads(left_seed, family_name=family_name)
        right_payloads = _build_grcv3_seed_family_payloads(right_seed, family_name=family_name)
        comparisons[family_name] = {
            "same": left_payloads == right_payloads,
            "left_payloads": left_payloads,
            "right_payloads": right_payloads,
        }
    return comparisons


def _ordered_unique_site_kinds(
    records: list[Mapping[str, Any]],
    *,
    key: str,
) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for record in records:
        site = record.get(key)
        if not isinstance(site, Mapping):
            continue
        site_kind = site.get("site_kind")
        if not isinstance(site_kind, str) or site_kind in seen:
            continue
        seen.add(site_kind)
        ordered.append(site_kind)
    return ordered
