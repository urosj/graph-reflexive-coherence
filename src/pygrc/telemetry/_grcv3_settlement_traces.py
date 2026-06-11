"""Private GRCV3 settlement and reentry trace builders."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.landscapes import load_landscape_seed
from pygrc.models import DEFAULT_GRCV3_LANDSCAPE_PROFILE

from ._grcv3_trace_utils import (
    _apply_grcv3_descendant_secondary_role_prune,
    _build_grcv3_descendant_neighborhood_aggregate,
    _build_grcv3_event_locus_record,
    _build_grcv3_failure_trace_model,
    _build_grcv3_failure_trace_step_observation,
    _build_grcv3_lane_neighborhood_boundary_summary,
    _build_grcv3_secondary_neighbor_role_summary,
    _build_grcv3_settlement_regime_summary,
    _collect_grcv3_split_descendant_candidate_sites,
    _collect_grcv3_split_descendant_site_summaries,
    _compare_grcv3_seed_family_payloads,
    _grcv3_event_anchor_node_id,
    _grcv3_node_descends_from_anchor,
    _update_grcv3_node_snapshot_cache,
)


def _build_grcv3_settlement_reentry_lane_trace(
    *,
    seed_path: str | Path,
    profile_name: str,
    primitive_id: str,
    num_steps: int,
    secondary_neighbor_role_prune: str | None = None,
) -> dict[str, Any]:
    resolved_seed_path, seed, model = _build_grcv3_failure_trace_model(
        seed_path,
        profile_name=profile_name,
    )
    snapshot_cache: dict[int, dict[str, Any]] = {}
    _update_grcv3_node_snapshot_cache(model, snapshot_cache)
    steps = [
        {
            "step_index": 0,
            "observation": _build_grcv3_failure_trace_step_observation(
                model,
                primitive_id=primitive_id,
            ),
        }
    ]
    tracked_kinds = {"spark_candidate", "split_init", "spark", "split_complete"}
    event_loci: list[dict[str, Any]] = []
    first_anchor_node_id = None
    first_split_complete_step = None
    first_reentry_gate_pass_step = None
    first_reentry_candidate_step = None
    counterfactual_applied_step = None
    counterfactual_removed_edges: list[dict[str, Any]] = []
    descendant_records: list[dict[str, Any]] = []
    for _ in range(num_steps):
        step = model.step()
        _update_grcv3_node_snapshot_cache(model, snapshot_cache)
        step_index = int(step.step_index)
        steps.append(
            {
                "step_index": step_index,
                "observation": _build_grcv3_failure_trace_step_observation(
                    model,
                    primitive_id=primitive_id,
                    event_kinds=tuple(event.kind for event in step.events),
                ),
            }
        )
        for event in step.events:
            if event.kind in tracked_kinds:
                event_loci.append(
                    _build_grcv3_event_locus_record(
                        step_index,
                        event=event,
                        snapshot_cache=snapshot_cache,
                    )
                )
        if first_anchor_node_id is None:
            first_candidate_event = next(
                (event for event in step.events if event.kind == "spark_candidate"),
                None,
            )
            if first_candidate_event is not None:
                first_anchor_node_id = _grcv3_event_anchor_node_id(
                    first_candidate_event.payload
                    if isinstance(first_candidate_event.payload, Mapping)
                    else {}
                )
        if first_anchor_node_id is None:
            continue
        if first_split_complete_step is None:
            for event in step.events:
                if event.kind != "split_complete":
                    continue
                payload = event.payload if isinstance(event.payload, Mapping) else {}
                anchor_node_id = _grcv3_event_anchor_node_id(payload)
                if anchor_node_id is None:
                    continue
                if _grcv3_node_descends_from_anchor(
                    int(anchor_node_id),
                    anchor_node_id=int(first_anchor_node_id),
                    snapshot_cache=snapshot_cache,
                ):
                    first_split_complete_step = step_index
                    break
        if (
            secondary_neighbor_role_prune is not None
            and first_split_complete_step is not None
            and counterfactual_applied_step is None
        ):
            counterfactual_removed_edges = _apply_grcv3_descendant_secondary_role_prune(
                model,
                anchor_node_id=int(first_anchor_node_id),
                target_motif_role=str(secondary_neighbor_role_prune),
                snapshot_cache=snapshot_cache,
            )
            _update_grcv3_node_snapshot_cache(model, snapshot_cache)
            counterfactual_applied_step = step_index
        if first_split_complete_step is None or step_index < first_split_complete_step:
            continue
        descendant_sites = _collect_grcv3_split_descendant_site_summaries(
            model,
            anchor_node_id=int(first_anchor_node_id),
            snapshot_cache=snapshot_cache,
        )
        descendant_candidate_sites = _collect_grcv3_split_descendant_candidate_sites(
            step_index=step_index,
            events=list(step.events),
            anchor_node_id=int(first_anchor_node_id),
            snapshot_cache=snapshot_cache,
        )
        descendant_records.append(
            {
                "step_index": step_index,
                "descendant_sites": descendant_sites,
                "descendant_candidate_sites": descendant_candidate_sites,
            }
        )
        if first_reentry_gate_pass_step is None and any(
            bool(site.get("candidate_gate_pass")) for site in descendant_sites
        ):
            first_reentry_gate_pass_step = step_index
        if first_reentry_candidate_step is None and descendant_candidate_sites:
            first_reentry_candidate_step = step_index
    regime = _build_grcv3_settlement_regime_summary(
        steps=[
            {
                "step_index": int(record["step_index"]),
                "lane": record["observation"],
            }
            for record in steps
        ],
        side="lane",
        event_loci=event_loci,
    )
    return {
        "seed_name": seed.meta.name,
        "seed_path": resolved_seed_path.as_posix(),
        "regime": regime,
        "first_anchor_site": regime["first_lifecycle_anchor"]["site"],
        "first_split_complete_step": first_split_complete_step,
        "first_reentry_gate_pass_step": first_reentry_gate_pass_step,
        "first_reentry_candidate_step": first_reentry_candidate_step,
        "secondary_neighbor_role_prune": secondary_neighbor_role_prune,
        "counterfactual_applied_step": counterfactual_applied_step,
        "counterfactual_removed_edges": counterfactual_removed_edges,
        "descendant_records": descendant_records,
    }


def _diagnose_grcv3_settlement_reentry_blocker(
    *,
    baseline_lane: Mapping[str, Any],
    comparison_lane: Mapping[str, Any],
) -> str:
    if baseline_lane.get("first_reentry_candidate_step") is None:
        return "baseline_lane_has_no_post_split_reentry_reference"
    comparison_descendant_sites = [
        site
        for record in list(comparison_lane.get("descendant_records", []))
        if isinstance(record, Mapping)
        for site in list(record.get("descendant_sites", []))
        if isinstance(site, Mapping)
    ]
    if not comparison_descendant_sites:
        return "derived_child_sites_do_not_persist_after_first_split"
    if comparison_lane.get("first_reentry_gate_pass_step") is None:
        if all(not bool(site.get("gradient_below_threshold")) for site in comparison_descendant_sites):
            return "derived_child_sites_never_settle_enough_to_enter_spark_gate"
        return "derived_child_sites_settle_but_do_not_form_candidate_eigen_signature"
    if comparison_lane.get("first_reentry_candidate_step") is None:
        return "derived_child_sites_pass_gate_but_fail_later_runtime_transition"
    return "comparison_lane_reenters_like_baseline"


def build_grcv3_landscape_settlement_reentry_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Trace why one settlement regime re-enters through split children while another does not."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    baseline_lane = _build_grcv3_settlement_reentry_lane_trace(
        seed_path=baseline_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    comparison_lane = _build_grcv3_settlement_reentry_lane_trace(
        seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "baseline_seed_name": baseline_lane["seed_name"],
        "baseline_seed_path": baseline_lane["seed_path"],
        "comparison_seed_name": comparison_lane["seed_name"],
        "comparison_seed_path": comparison_lane["seed_path"],
        "baseline_lane": baseline_lane,
        "comparison_lane": comparison_lane,
        "diagnosed_reentry_blocker": _diagnose_grcv3_settlement_reentry_blocker(
            baseline_lane=baseline_lane,
            comparison_lane=comparison_lane,
        ),
    }


def _diagnose_grcv3_settlement_reentry_neighborhood_boundary(
    *,
    baseline_summary: Mapping[str, Any],
    comparison_summary: Mapping[str, Any],
) -> str:
    baseline_matched_record = baseline_summary.get("matched_step_record")
    comparison_matched_record = comparison_summary.get("matched_step_record")
    if not isinstance(baseline_matched_record, Mapping) or not isinstance(
        comparison_matched_record, Mapping
    ):
        return "no_matched_post_split_descendant_record"
    baseline_aggregate = baseline_matched_record.get("aggregate", {})
    comparison_aggregate = comparison_matched_record.get("aggregate", {})
    baseline_roles = {
        str(value)
        for value in list(baseline_aggregate.get("common_neighbor_motif_roles", []))
    }
    comparison_roles = {
        str(value)
        for value in list(comparison_aggregate.get("common_neighbor_motif_roles", []))
    }
    if (
        "basin_load_carrier" in baseline_roles
        and "basin_load_carrier" not in comparison_roles
        and "ridge_support" in comparison_roles
    ):
        return "derived_child_reentry_correlates_with_carrier_neighbor_vs_ridge_support_neighbor_mix"
    return "no_clear_descendant_neighbor_role_boundary_detected"


def build_grcv3_landscape_settlement_reentry_neighborhood_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Trace descendant neighborhood signatures at the post-split reentry boundary."""

    reentry_trace = build_grcv3_landscape_settlement_reentry_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    matched_step_index = reentry_trace["baseline_lane"]["first_reentry_gate_pass_step"]
    baseline_summary = _build_grcv3_lane_neighborhood_boundary_summary(
        reentry_trace["baseline_lane"],
        matched_step_index=matched_step_index,
    )
    comparison_summary = _build_grcv3_lane_neighborhood_boundary_summary(
        reentry_trace["comparison_lane"],
        matched_step_index=matched_step_index,
    )
    return {
        **reentry_trace,
        "matched_step_index": matched_step_index,
        "baseline_neighborhood_boundary": baseline_summary,
        "comparison_neighborhood_boundary": comparison_summary,
        "diagnosed_neighborhood_boundary": _diagnose_grcv3_settlement_reentry_neighborhood_boundary(
            baseline_summary=baseline_summary,
            comparison_summary=comparison_summary,
        ),
    }


def _diagnose_grcv3_settlement_reentry_support_isolation(
    *,
    baseline_summary: Mapping[str, Any],
    comparison_summary: Mapping[str, Any],
) -> str:
    baseline_record = baseline_summary.get("matched_step_record")
    comparison_record = comparison_summary.get("matched_step_record")
    if not isinstance(baseline_record, Mapping) or not isinstance(comparison_record, Mapping):
        return "no_matched_post_split_descendant_record"
    baseline_aggregate = baseline_record.get("aggregate", {})
    comparison_aggregate = comparison_record.get("aggregate", {})
    baseline_support = _build_grcv3_secondary_neighbor_role_summary(
        baseline_aggregate
    )
    comparison_support = _build_grcv3_secondary_neighbor_role_summary(
        comparison_aggregate
    )
    if (
        baseline_support["degree_set"] == comparison_support["degree_set"]
        and abs(
            float(baseline_support["support_weight"])
            - float(comparison_support["support_weight"])
        )
        < 0.05
        and baseline_support["secondary_roles"] == ["basin_load_carrier"]
        and comparison_support["secondary_roles"] == ["ridge_support"]
    ):
        return "reentry_correlates_with_secondary_carrier_neighbor_rather_than_secondary_ridge_support"
    return "secondary_neighbor_isolation_inconclusive"


def build_grcv3_landscape_settlement_reentry_support_isolation_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Isolate the secondary non-support neighbor role at the descendant reentry boundary."""

    neighborhood_trace = build_grcv3_landscape_settlement_reentry_neighborhood_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    baseline_record = neighborhood_trace["baseline_neighborhood_boundary"]["matched_step_record"]
    comparison_record = neighborhood_trace["comparison_neighborhood_boundary"]["matched_step_record"]
    baseline_support_summary = _build_grcv3_secondary_neighbor_role_summary(
        {}
        if not isinstance(baseline_record, Mapping)
        else dict(baseline_record.get("aggregate", {}))
    )
    comparison_support_summary = _build_grcv3_secondary_neighbor_role_summary(
        {}
        if not isinstance(comparison_record, Mapping)
        else dict(comparison_record.get("aggregate", {}))
    )
    return {
        **neighborhood_trace,
        "baseline_support_isolation": baseline_support_summary,
        "comparison_support_isolation": comparison_support_summary,
        "diagnosed_support_isolation": _diagnose_grcv3_settlement_reentry_support_isolation(
            baseline_summary=neighborhood_trace["baseline_neighborhood_boundary"],
            comparison_summary=neighborhood_trace["comparison_neighborhood_boundary"],
        ),
    }


def build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Run decisive descendant-edge counterfactuals on the isolated secondary support roles."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    natural_trace = build_grcv3_landscape_settlement_reentry_support_isolation_trace(
        baseline_seed_path=baseline_seed_path,
        comparison_seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    baseline_counterfactual_lane = _build_grcv3_settlement_reentry_lane_trace(
        seed_path=baseline_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        secondary_neighbor_role_prune="basin_load_carrier",
    )
    comparison_counterfactual_lane = _build_grcv3_settlement_reentry_lane_trace(
        seed_path=comparison_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        secondary_neighbor_role_prune="ridge_support",
    )
    diagnosis = "secondary_support_counterfactual_inconclusive"
    if (
        natural_trace["baseline_lane"]["first_reentry_candidate_step"] is not None
        and baseline_counterfactual_lane["first_reentry_candidate_step"] is None
        and natural_trace["comparison_lane"]["first_reentry_candidate_step"] is None
        and comparison_counterfactual_lane["first_reentry_candidate_step"] is None
    ):
        diagnosis = (
            "secondary_basin_load_carrier_is_necessary_but_removing_secondary_ridge_support_is_not_sufficient"
        )
    return {
        **natural_trace,
        "baseline_counterfactual_lane": baseline_counterfactual_lane,
        "comparison_counterfactual_lane": comparison_counterfactual_lane,
        "diagnosed_counterfactual_boundary": diagnosis,
    }


def _build_grcv3_secondary_support_authorability_lane_summary(
    *,
    seed_path: str | Path,
    profile_name: str,
    primitive_id: str,
    num_steps: int,
) -> dict[str, Any]:
    trace = build_grcv3_landscape_settlement_reentry_support_isolation_trace(
        baseline_seed_path=seed_path,
        comparison_seed_path=seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    return {
        "seed_name": trace["baseline_seed_name"],
        "seed_path": trace["baseline_seed_path"],
        "first_reentry_gate_pass_step": trace["baseline_lane"]["first_reentry_gate_pass_step"],
        "first_reentry_candidate_step": trace["baseline_lane"]["first_reentry_candidate_step"],
        "secondary_roles": list(trace["baseline_support_isolation"]["secondary_roles"]),
        "support_weight": float(trace["baseline_support_isolation"]["support_weight"]),
        "target_condition_present": (
            trace["baseline_lane"]["first_reentry_candidate_step"] is not None
            and list(trace["baseline_support_isolation"]["secondary_roles"])
            == ["basin_load_carrier"]
        ),
    }


def build_grcv3_landscape_secondary_support_authorability_trace(
    *,
    structural_path_seed_path: str | Path,
    explicit_path_seed_path: str | Path,
    structural_direct_seed_path: str | Path,
    explicit_direct_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Test whether existing structural vocabulary already authors the secondary-support condition."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    structural_path_summary = _build_grcv3_secondary_support_authorability_lane_summary(
        seed_path=structural_path_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    explicit_path_summary = _build_grcv3_secondary_support_authorability_lane_summary(
        seed_path=explicit_path_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    structural_direct_summary = _build_grcv3_secondary_support_authorability_lane_summary(
        seed_path=structural_direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )
    explicit_direct_summary = _build_grcv3_secondary_support_authorability_lane_summary(
        seed_path=explicit_direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
    )

    resolved_structural_path_seed_path = Path(structural_path_seed_path)
    resolved_explicit_path_seed_path = Path(explicit_path_seed_path)
    resolved_structural_direct_seed_path = Path(structural_direct_seed_path)
    resolved_explicit_direct_seed_path = Path(explicit_direct_seed_path)
    structural_path_seed = load_landscape_seed(resolved_structural_path_seed_path)
    explicit_path_seed = load_landscape_seed(resolved_explicit_path_seed_path)
    structural_direct_seed = load_landscape_seed(resolved_structural_direct_seed_path)
    explicit_direct_seed = load_landscape_seed(resolved_explicit_direct_seed_path)

    prioritized_families = [
        "transfer_mediation",
        "interior_load_carriers",
        "channel_geometry",
        "boundary_geometry",
    ]
    path_to_explicit_comparison = _compare_grcv3_seed_family_payloads(
        structural_path_seed,
        explicit_path_seed,
        family_names=[*prioritized_families, "settlement_regime"],
    )
    structural_path_to_direct_comparison = _compare_grcv3_seed_family_payloads(
        structural_path_seed,
        structural_direct_seed,
        family_names=prioritized_families,
    )
    diagnosis = "secondary_support_authorability_inconclusive"
    if (
        structural_path_summary["target_condition_present"]
        and explicit_path_summary["target_condition_present"]
        and not structural_direct_summary["target_condition_present"]
        and not explicit_direct_summary["target_condition_present"]
        and path_to_explicit_comparison["transfer_mediation"]["same"]
        and not path_to_explicit_comparison["settlement_regime"]["same"]
        and not structural_path_to_direct_comparison["transfer_mediation"]["same"]
        and structural_path_to_direct_comparison["interior_load_carriers"]["same"]
        and structural_path_to_direct_comparison["channel_geometry"]["same"]
        and structural_path_to_direct_comparison["boundary_geometry"]["same"]
    ):
        diagnosis = (
            "existing_transfer_mediation_already_authors_descendant_secondary_basin_load_carrier_support_condition"
        )
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "structural_path_seed_path": resolved_structural_path_seed_path.as_posix(),
        "explicit_path_seed_path": resolved_explicit_path_seed_path.as_posix(),
        "structural_direct_seed_path": resolved_structural_direct_seed_path.as_posix(),
        "explicit_direct_seed_path": resolved_explicit_direct_seed_path.as_posix(),
        "structural_path_summary": structural_path_summary,
        "explicit_path_summary": explicit_path_summary,
        "structural_direct_summary": structural_direct_summary,
        "explicit_direct_summary": explicit_direct_summary,
        "path_to_explicit_comparison": path_to_explicit_comparison,
        "structural_path_to_direct_comparison": structural_path_to_direct_comparison,
        "diagnosed_authorability_result": diagnosis,
    }
