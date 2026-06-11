"""Private GRCV3 collapse trace builders."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.landscapes import load_landscape_seed
from pygrc.models import DEFAULT_GRCV3_LANDSCAPE_PROFILE, GRCV3

from ._grcv3_trace_utils import (
    _build_grcv3_event_anchor_site_summary,
    _build_grcv3_event_locus_record,
    _build_grcv3_failure_trace_model,
    _build_grcv3_failure_trace_step_observation,
    _build_grcv3_settlement_regime_summary,
    _build_grcv3_split_descendant_site_summary,
    _compare_grcv3_seed_family_payloads,
    _default_grcv3_choice_collapse_overrides,
    _grcv3_event_anchor_node_id,
    _grcv3_optional_node_id,
    _ordered_unique_site_kinds,
    _update_grcv3_node_snapshot_cache,
)
from ._telemetry_utils import _to_plain_data


def _build_grcv3_collapse_event_record(
    step_index: int,
    *,
    event: Any,
    model: GRCV3,
    snapshot_cache: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    payload = event.payload if isinstance(event.payload, Mapping) else {}
    source_node_id = _grcv3_event_anchor_node_id(payload)
    sink_node_id = _grcv3_optional_node_id(payload.get("collapsed_sink_id"))
    source_site_summary = (
        None
        if source_node_id is None
        else _build_grcv3_split_descendant_site_summary(
            model,
            node_id=int(source_node_id),
            snapshot_cache=snapshot_cache,
        )
    )
    sink_site_summary = (
        None
        if sink_node_id is None
        else _build_grcv3_split_descendant_site_summary(
            model,
            node_id=int(sink_node_id),
            snapshot_cache=snapshot_cache,
        )
    )
    return {
        "step_index": int(step_index),
        "event_kind": str(event.kind),
        "source_site": _build_grcv3_event_anchor_site_summary(
            source_node_id,
            snapshot_cache=snapshot_cache,
        ),
        "source_site_summary": source_site_summary,
        "sink_site": _build_grcv3_event_anchor_site_summary(
            sink_node_id,
            snapshot_cache=snapshot_cache,
        ),
        "sink_site_summary": sink_site_summary,
        "event_payload": {
            str(key): _to_plain_data(value)
            for key, value in payload.items()
        },
    }


def _collapse_record_has_split_child_participation(
    record: Mapping[str, Any],
) -> bool:
    for key in ("source_site", "sink_site"):
        site = record.get(key)
        if isinstance(site, Mapping) and site.get("site_kind") == "split_child":
            return True
    return False


def _build_grcv3_collapse_lane_trace(
    *,
    seed_path: str | Path,
    profile_name: str,
    primitive_id: str,
    num_steps: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    overrides = _default_grcv3_choice_collapse_overrides(
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    resolved_seed_path, seed, model = _build_grcv3_failure_trace_model(
        seed_path,
        profile_name=profile_name,
        overrides=overrides,
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
    regime_event_loci: list[dict[str, Any]] = []
    choice_records: list[dict[str, Any]] = []
    collapse_records: list[dict[str, Any]] = []
    regime_event_kinds = {"spark_candidate", "split_init", "spark", "split_complete"}
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
            if event.kind in regime_event_kinds:
                regime_event_loci.append(
                    _build_grcv3_event_locus_record(
                        step_index,
                        event=event,
                        snapshot_cache=snapshot_cache,
                    )
                )
            elif event.kind == "choice_detected":
                choice_records.append(
                    _build_grcv3_event_locus_record(
                        step_index,
                        event=event,
                        snapshot_cache=snapshot_cache,
                    )
                )
            elif event.kind == "collapse":
                collapse_records.append(
                    _build_grcv3_collapse_event_record(
                        step_index,
                        event=event,
                        model=model,
                        snapshot_cache=snapshot_cache,
                    )
                )
    regime = _build_grcv3_settlement_regime_summary(
        steps=[
            {
                "step_index": int(record["step_index"]),
                "lane": record["observation"],
            }
            for record in steps
        ],
        side="lane",
        event_loci=regime_event_loci,
    )
    first_spark_site = regime["first_lifecycle_anchor"]["site"]
    first_spark_step = regime["first_event_steps"]["spark"]
    first_split_complete_step = regime["first_event_steps"]["split_complete"]
    first_choice_step = None if not choice_records else int(choice_records[0]["step_index"])
    first_collapse_step = None if not collapse_records else int(collapse_records[0]["step_index"])
    first_collapse_source_site = (
        None if not collapse_records else collapse_records[0].get("source_site")
    )
    first_collapse_sink_site = (
        None if not collapse_records else collapse_records[0].get("sink_site")
    )
    first_collapse_records_at_step = (
        []
        if first_collapse_step is None
        else [
            record
            for record in collapse_records
            if int(record["step_index"]) == int(first_collapse_step)
        ]
    )
    first_collapse_source_summary = None
    if (
        first_collapse_source_site is not None
        and first_collapse_source_site.get("node_id") is not None
    ):
        first_collapse_source_summary = _build_grcv3_split_descendant_site_summary(
            model,
            node_id=int(first_collapse_source_site["node_id"]),
            snapshot_cache=snapshot_cache,
        )
    first_collapse_sink_summary = None
    if (
        first_collapse_sink_site is not None
        and first_collapse_sink_site.get("node_id") is not None
    ):
        first_collapse_sink_summary = _build_grcv3_split_descendant_site_summary(
            model,
            node_id=int(first_collapse_sink_site["node_id"]),
            snapshot_cache=snapshot_cache,
        )
    later_collapse_records = (
        []
        if first_split_complete_step is None
        else [
            record
            for record in collapse_records
            if int(record["step_index"]) > int(first_split_complete_step)
        ]
    )
    return {
        "seed_name": seed.meta.name,
        "seed_path": resolved_seed_path.as_posix(),
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "regime": regime,
        "first_spark_site": first_spark_site,
        "first_spark_step": first_spark_step,
        "first_choice_step": first_choice_step,
        "choice_detected_records": choice_records,
        "first_split_complete_step": first_split_complete_step,
        "first_collapse_step": first_collapse_step,
        "first_collapse_source_site": first_collapse_source_site,
        "first_collapse_sink_site": first_collapse_sink_site,
        "first_collapse_source_summary": first_collapse_source_summary,
        "first_collapse_sink_summary": first_collapse_sink_summary,
        "first_collapse_records_at_step": first_collapse_records_at_step,
        "collapse_records": collapse_records,
        "collapse_source_site_kinds": sorted(
            {
                str(record["source_site"]["site_kind"])
                for record in collapse_records
                if isinstance(record.get("source_site"), Mapping)
                and record["source_site"].get("site_kind") is not None
            }
        ),
        "collapse_sink_site_kinds": sorted(
            {
                str(record["sink_site"]["site_kind"])
                for record in collapse_records
                if isinstance(record.get("sink_site"), Mapping)
                and record["sink_site"].get("site_kind") is not None
            }
        ),
        "collapse_source_matches_first_spark_locus_family": (
            isinstance(first_spark_site, Mapping)
            and isinstance(first_collapse_source_site, Mapping)
            and first_spark_site.get("site_kind") == first_collapse_source_site.get("site_kind")
        ),
        "collapse_after_split_occurs": (
            first_split_complete_step is not None
            and any(
                int(record["step_index"]) > int(first_split_complete_step)
                for record in collapse_records
            )
        ),
        "later_split_child_collapse_participation": any(
            _collapse_record_has_split_child_participation(record)
            for record in later_collapse_records
        ),
        "later_split_child_collapse_records": [
            record
            for record in later_collapse_records
            if _collapse_record_has_split_child_participation(record)
        ],
    }


def build_grcv3_landscape_collapse_lane_trace(
    *,
    seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str,
    num_steps: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Trace collapse loci for one seed under the recorded choice/collapse envelope."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    return _build_grcv3_collapse_lane_trace(
        seed_path=seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )


def _grcv3_collapse_relation_to_first_spark(lane: Mapping[str, Any]) -> str:
    first_spark_site = lane.get("first_spark_site")
    first_collapse_source_site = lane.get("first_collapse_source_site")
    if not isinstance(first_spark_site, Mapping):
        return "collapse_without_prior_spark"
    if not isinstance(first_collapse_source_site, Mapping):
        return "no_collapse_observed"
    if first_spark_site.get("site_kind") == first_collapse_source_site.get("site_kind"):
        return "collapse_from_same_locus_family_as_first_spark"
    return "collapse_from_different_locus_family_than_first_spark"


def _summarize_grcv3_collapse_lane_for_survey(
    lane_name: str,
    lane: Mapping[str, Any],
) -> dict[str, Any]:
    first_spark_site = lane.get("first_spark_site")
    first_collapse_source_site = lane.get("first_collapse_source_site")
    first_collapse_sink_site = lane.get("first_collapse_sink_site")
    return {
        "lane_name": lane_name,
        "seed_name": lane.get("seed_name"),
        "seed_path": lane.get("seed_path"),
        "choice_backend": lane.get("choice_backend"),
        "first_choice_step": lane.get("first_choice_step"),
        "first_spark_site": first_spark_site,
        "first_collapse_step": lane.get("first_collapse_step"),
        "first_collapse_source_site": first_collapse_source_site,
        "first_collapse_sink_site": first_collapse_sink_site,
        "collapse_source_site_kinds": list(lane.get("collapse_source_site_kinds", [])),
        "collapse_sink_site_kinds": list(lane.get("collapse_sink_site_kinds", [])),
        "collapse_after_split_occurs": bool(lane.get("collapse_after_split_occurs")),
        "later_split_child_collapse_participation": bool(
            lane.get("later_split_child_collapse_participation")
        ),
        "collapse_relative_to_first_spark": _grcv3_collapse_relation_to_first_spark(lane),
        "collapse_record_count": len(list(lane.get("collapse_records", []))),
    }


def _diagnose_grcv3_broad_collapse_survey(
    lane_summaries: list[Mapping[str, Any]],
) -> str:
    if not lane_summaries:
        return "no_collapse_lanes_surveyed"
    collapse_capable = [
        lane
        for lane in lane_summaries
        if lane.get("first_collapse_step") is not None
    ]
    if not collapse_capable:
        return "surveyed_lanes_do_not_reach_collapse_under_recorded_envelopes"
    source_site_kinds = {
        str(lane["first_collapse_source_site"]["site_kind"])
        for lane in collapse_capable
        if isinstance(lane.get("first_collapse_source_site"), Mapping)
        and lane["first_collapse_source_site"].get("site_kind") is not None
    }
    sink_site_kinds = {
        str(lane["first_collapse_sink_site"]["site_kind"])
        for lane in collapse_capable
        if isinstance(lane.get("first_collapse_sink_site"), Mapping)
        and lane["first_collapse_sink_site"].get("site_kind") is not None
    }
    relations = {
        str(lane.get("collapse_relative_to_first_spark"))
        for lane in collapse_capable
    }
    if len(collapse_capable) >= 2 and (
        len(source_site_kinds) > 1
        or len(sink_site_kinds) > 1
        or len(relations) > 1
    ):
        return (
            "recorded_collapse_lanes_are_plural_and_heterogeneous_so_broader_"
            "controlled_comparison_is_still_required"
        )
    return "recorded_collapse_lanes_are_broadly_coherent_under_current_survey"


def build_grcv3_landscape_broad_collapse_survey(
    *,
    lane_specs: tuple[Mapping[str, Any], ...],
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Survey the broader recorded collapse-capable lanes beyond the narrow spindle audit."""

    lane_summaries: list[dict[str, Any]] = []
    for spec in lane_specs:
        lane_name = str(spec["lane_name"])
        lane = build_grcv3_landscape_collapse_lane_trace(
            seed_path=Path(spec["seed_path"]),
            profile_name=str(spec["profile_name"]),
            primitive_id=str(spec["primitive_id"]),
            num_steps=int(spec["num_steps"]),
            epsilon_choice=epsilon_choice,
            epsilon_collapse=epsilon_collapse,
        )
        lane_summaries.append(_summarize_grcv3_collapse_lane_for_survey(lane_name, lane))
    return {
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "lane_count": len(lane_summaries),
        "collapse_capable_lane_count": sum(
            1 for lane in lane_summaries if lane.get("first_collapse_step") is not None
        ),
        "lane_summaries": lane_summaries,
        "collapse_without_prior_spark_lane_names": [
            lane["lane_name"]
            for lane in lane_summaries
            if lane.get("collapse_relative_to_first_spark") == "collapse_without_prior_spark"
        ],
        "collapse_after_split_lane_names": [
            lane["lane_name"]
            for lane in lane_summaries
            if bool(lane.get("collapse_after_split_occurs"))
        ],
        "later_split_child_collapse_lane_names": [
            lane["lane_name"]
            for lane in lane_summaries
            if bool(lane.get("later_split_child_collapse_participation"))
        ],
        "diagnosed_broadened_collapse_read": _diagnose_grcv3_broad_collapse_survey(
            lane_summaries
        ),
    }


def _diagnose_grcv3_pre_spark_collapse_decomposition(
    *,
    baseline_lane: Mapping[str, Any],
    comparison_lane: Mapping[str, Any],
    family_comparison: Mapping[str, Any],
) -> str:
    baseline_source = baseline_lane.get("first_collapse_source_site")
    comparison_source = comparison_lane.get("first_collapse_source_site")
    baseline_sink = baseline_lane.get("first_collapse_sink_site")
    comparison_sink = comparison_lane.get("first_collapse_sink_site")
    if (
        baseline_lane.get("first_spark_site") is None
        and comparison_lane.get("first_spark_site") is None
        and isinstance(baseline_source, Mapping)
        and isinstance(comparison_source, Mapping)
        and baseline_source.get("site_kind") == "basin_support"
        and comparison_source.get("site_kind") == "basin_support"
        and isinstance(baseline_sink, Mapping)
        and isinstance(comparison_sink, Mapping)
        and baseline_sink.get("site_kind") != comparison_sink.get("site_kind")
        and not family_comparison["realization"]["same"]
        and not family_comparison["interfaces"]["same"]
        and not family_comparison["boundary_geometry"]["same"]
        and not family_comparison["channel_geometry"]["same"]
    ):
        return (
            "pre_spark_collapse_sink_difference_tracks_existing_junction_vs_boundary_channel_structure_"
            "so_no_new_collapse_family_is_justified_yet"
        )
    return "pre_spark_collapse_decomposition_inconclusive"


def build_grcv3_landscape_pre_spark_collapse_decomposition_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    baseline_profile_name: str,
    comparison_profile_name: str,
    baseline_primitive_id: str,
    comparison_primitive_id: str,
    baseline_num_steps: int,
    comparison_num_steps: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Compare the two recorded pre-spark collapse lanes as one collapse cluster."""

    if baseline_num_steps <= 0:
        raise ValueError("baseline_num_steps must be > 0")
    if comparison_num_steps <= 0:
        raise ValueError("comparison_num_steps must be > 0")
    baseline_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=baseline_seed_path,
        profile_name=baseline_profile_name,
        primitive_id=baseline_primitive_id,
        num_steps=baseline_num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    comparison_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=comparison_seed_path,
        profile_name=comparison_profile_name,
        primitive_id=comparison_primitive_id,
        num_steps=comparison_num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    resolved_baseline_seed_path = Path(baseline_seed_path)
    resolved_comparison_seed_path = Path(comparison_seed_path)
    baseline_seed = load_landscape_seed(resolved_baseline_seed_path)
    comparison_seed = load_landscape_seed(resolved_comparison_seed_path)
    prioritized_families = [
        "realization",
        "local_geometry",
        "interfaces",
        "boundary_geometry",
        "channel_geometry",
    ]
    family_comparison = _compare_grcv3_seed_family_payloads(
        baseline_seed,
        comparison_seed,
        family_names=prioritized_families,
    )
    return {
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "baseline_seed_path": resolved_baseline_seed_path.as_posix(),
        "comparison_seed_path": resolved_comparison_seed_path.as_posix(),
        "baseline_profile_name": baseline_profile_name,
        "comparison_profile_name": comparison_profile_name,
        "baseline_primitive_id": baseline_primitive_id,
        "comparison_primitive_id": comparison_primitive_id,
        "baseline_num_steps": baseline_num_steps,
        "comparison_num_steps": comparison_num_steps,
        "baseline_lane": baseline_lane,
        "comparison_lane": comparison_lane,
        "family_comparison": family_comparison,
        "diagnosed_pre_spark_collapse_decomposition": _diagnose_grcv3_pre_spark_collapse_decomposition(
            baseline_lane=baseline_lane,
            comparison_lane=comparison_lane,
            family_comparison=family_comparison,
        ),
    }


def _diagnose_grcv3_post_spark_collapse_boundary(
    *,
    baseline_lane: Mapping[str, Any],
    blocked_control_lane: Mapping[str, Any],
    refined_control_lane: Mapping[str, Any],
    baseline_to_blocked_comparison: Mapping[str, Any],
    baseline_to_refined_comparison: Mapping[str, Any],
) -> str:
    same_structure_families = (
        "interfaces",
        "boundary_geometry",
        "channel_geometry",
        "interior_load_carriers",
        "local_geometry",
    )
    blocked_only_transfer_mediation_differs = (
        not baseline_to_blocked_comparison["transfer_mediation"]["same"]
        and all(
            baseline_to_blocked_comparison[family_name]["same"]
            for family_name in same_structure_families
        )
    )
    refined_only_transfer_mediation_differs = (
        not baseline_to_refined_comparison["transfer_mediation"]["same"]
        and all(
            baseline_to_refined_comparison[family_name]["same"]
            for family_name in same_structure_families
        )
    )
    if (
        baseline_lane.get("first_spark_site", {}).get("site_kind") == "carrier_site"
        and refined_control_lane.get("first_spark_site", {}).get("site_kind") == "carrier_site"
        and blocked_control_lane.get("first_spark_site", {}).get("site_kind")
        == "basin_support"
        and baseline_lane.get("first_collapse_source_site", {}).get("site_kind")
        == "basin_center"
        and baseline_lane.get("first_collapse_sink_site", {}).get("site_kind")
        == "basin_support"
        and refined_control_lane.get("first_collapse_source_site", {}).get("site_kind")
        == "basin_center"
        and refined_control_lane.get("first_collapse_sink_site", {}).get("site_kind")
        == "basin_support"
        and blocked_control_lane.get("first_collapse_source_site", {}).get("site_kind")
        == "carrier_site"
        and blocked_control_lane.get("first_collapse_sink_site", {}).get("site_kind")
        == "ridge_support"
        and blocked_only_transfer_mediation_differs
        and refined_only_transfer_mediation_differs
    ):
        return (
            "existing_transfer_mediation_center_coupling_classes_already_author_"
            "post_spark_collapse_boundary"
        )
    return "post_spark_collapse_boundary_inconclusive"


def build_grcv3_landscape_post_spark_collapse_boundary_trace(
    *,
    baseline_seed_path: str | Path,
    blocked_control_seed_path: str | Path,
    refined_control_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Compare the saved post-spark collapse lane against tight transfer-mediation controls."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    baseline_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=baseline_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    blocked_control_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=blocked_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    refined_control_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    prioritized_families = [
        "transfer_mediation",
        "interfaces",
        "boundary_geometry",
        "channel_geometry",
        "interior_load_carriers",
        "local_geometry",
    ]
    baseline_seed = load_landscape_seed(Path(baseline_seed_path))
    blocked_control_seed = load_landscape_seed(Path(blocked_control_seed_path))
    refined_control_seed = load_landscape_seed(Path(refined_control_seed_path))
    baseline_to_blocked_comparison = _compare_grcv3_seed_family_payloads(
        baseline_seed,
        blocked_control_seed,
        family_names=prioritized_families,
    )
    baseline_to_refined_comparison = _compare_grcv3_seed_family_payloads(
        baseline_seed,
        refined_control_seed,
        family_names=prioritized_families,
    )
    return {
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "baseline_seed_path": Path(baseline_seed_path).as_posix(),
        "blocked_control_seed_path": Path(blocked_control_seed_path).as_posix(),
        "refined_control_seed_path": Path(refined_control_seed_path).as_posix(),
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "baseline_lane": baseline_lane,
        "blocked_control_lane": blocked_control_lane,
        "refined_control_lane": refined_control_lane,
        "baseline_to_blocked_comparison": baseline_to_blocked_comparison,
        "baseline_to_refined_comparison": baseline_to_refined_comparison,
        "diagnosed_post_spark_collapse_boundary": _diagnose_grcv3_post_spark_collapse_boundary(
            baseline_lane=baseline_lane,
            blocked_control_lane=blocked_control_lane,
            refined_control_lane=refined_control_lane,
            baseline_to_blocked_comparison=baseline_to_blocked_comparison,
            baseline_to_refined_comparison=baseline_to_refined_comparison,
        ),
    }


def _summarize_grcv3_post_window_collapse_behavior(
    lane: Mapping[str, Any],
    *,
    late_window_start_step: int,
    baseline_pattern: tuple[str | None, str | None],
) -> dict[str, Any]:
    post_window_collapse_records = [
        record
        for record in list(lane.get("collapse_records", []))
        if int(record["step_index"]) > int(late_window_start_step)
    ]
    first_post_window_collapse_record = (
        None if not post_window_collapse_records else post_window_collapse_records[0]
    )
    first_post_window_matching_baseline_pattern_record = next(
        (
            record
            for record in post_window_collapse_records
            if (
                record.get("source_site", {}).get("site_kind"),
                record.get("sink_site", {}).get("site_kind"),
            )
            == baseline_pattern
        ),
        None,
    )
    return {
        "late_window_start_step": int(late_window_start_step),
        "post_window_collapse_count": len(post_window_collapse_records),
        "first_post_window_collapse_record": first_post_window_collapse_record,
        "first_post_window_collapse_step": (
            None
            if first_post_window_collapse_record is None
            else int(first_post_window_collapse_record["step_index"])
        ),
        "post_window_collapse_source_site_kinds": sorted(
            {
                str(record["source_site"]["site_kind"])
                for record in post_window_collapse_records
                if isinstance(record.get("source_site"), Mapping)
                and record["source_site"].get("site_kind") is not None
            }
        ),
        "post_window_collapse_sink_site_kinds": sorted(
            {
                str(record["sink_site"]["site_kind"])
                for record in post_window_collapse_records
                if isinstance(record.get("sink_site"), Mapping)
                and record["sink_site"].get("site_kind") is not None
            }
        ),
        "first_post_window_matching_baseline_pattern_record": (
            first_post_window_matching_baseline_pattern_record
        ),
        "first_post_window_matching_baseline_pattern_step": (
            None
            if first_post_window_matching_baseline_pattern_record is None
            else int(first_post_window_matching_baseline_pattern_record["step_index"])
        ),
        "eventually_matches_baseline_collapse_pattern_after_window": (
            first_post_window_matching_baseline_pattern_record is not None
        ),
        "has_distinct_post_window_collapse_before_baseline_match": any(
            (
                record.get("source_site", {}).get("site_kind"),
                record.get("sink_site", {}).get("site_kind"),
            )
            != baseline_pattern
            for record in post_window_collapse_records
            if first_post_window_matching_baseline_pattern_record is None
            or int(record["step_index"])
            < int(first_post_window_matching_baseline_pattern_record["step_index"])
        ),
    }


def _diagnose_grcv3_post_spark_late_window_stability(
    *,
    baseline_post_window: Mapping[str, Any],
    blocked_post_window: Mapping[str, Any],
    refined_post_window: Mapping[str, Any],
) -> str:
    if (
        baseline_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
        and refined_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
        and blocked_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
        and blocked_post_window.get("has_distinct_post_window_collapse_before_baseline_match")
    ):
        return (
            "blocked_control_eventually_reaches_baseline_collapse_pattern_only_after_"
            "a_distinct_carrier_split_child_cascade_so_late_window_interpretation_remains_open"
        )
    if (
        not blocked_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
        and blocked_post_window.get("post_window_collapse_count", 0) > 0
    ):
        return "blocked_control_remains_distinct_through_late_window"
    return "post_spark_late_window_stability_inconclusive"


def build_grcv3_landscape_post_spark_late_window_stability_trace(
    *,
    baseline_seed_path: str | Path,
    blocked_control_seed_path: str | Path,
    refined_control_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
    late_window_start_step: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Widen the post-spark boundary pass to test whether the blocked control converges later."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if late_window_start_step < 0:
        raise ValueError("late_window_start_step must be >= 0")
    boundary_trace = build_grcv3_landscape_post_spark_collapse_boundary_trace(
        baseline_seed_path=baseline_seed_path,
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    baseline_lane = boundary_trace["baseline_lane"]
    blocked_control_lane = boundary_trace["blocked_control_lane"]
    refined_control_lane = boundary_trace["refined_control_lane"]
    baseline_pattern = (
        baseline_lane.get("first_collapse_source_site", {}).get("site_kind"),
        baseline_lane.get("first_collapse_sink_site", {}).get("site_kind"),
    )
    baseline_post_window = _summarize_grcv3_post_window_collapse_behavior(
        baseline_lane,
        late_window_start_step=late_window_start_step,
        baseline_pattern=baseline_pattern,
    )
    blocked_post_window = _summarize_grcv3_post_window_collapse_behavior(
        blocked_control_lane,
        late_window_start_step=late_window_start_step,
        baseline_pattern=baseline_pattern,
    )
    refined_post_window = _summarize_grcv3_post_window_collapse_behavior(
        refined_control_lane,
        late_window_start_step=late_window_start_step,
        baseline_pattern=baseline_pattern,
    )
    return {
        **boundary_trace,
        "late_window_start_step": int(late_window_start_step),
        "baseline_post_window": baseline_post_window,
        "blocked_control_post_window": blocked_post_window,
        "refined_control_post_window": refined_post_window,
        "diagnosed_post_spark_late_window_stability": _diagnose_grcv3_post_spark_late_window_stability(
            baseline_post_window=baseline_post_window,
            blocked_post_window=blocked_post_window,
            refined_post_window=refined_post_window,
        ),
    }


def _diagnose_grcv3_post_spark_delay_authorability(
    *,
    blocked_post_window: Mapping[str, Any],
    refined_post_window: Mapping[str, Any],
    blocked_to_refined_comparison: Mapping[str, Any],
) -> str:
    same_structure_families = (
        "interfaces",
        "boundary_geometry",
        "channel_geometry",
        "interior_load_carriers",
        "local_geometry",
    )
    if (
        not blocked_to_refined_comparison["transfer_mediation"]["same"]
        and all(
            blocked_to_refined_comparison[family_name]["same"]
            for family_name in same_structure_families
        )
        and blocked_post_window.get("has_distinct_post_window_collapse_before_baseline_match")
        and blocked_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
        and not refined_post_window.get("has_distinct_post_window_collapse_before_baseline_match")
        and refined_post_window.get("eventually_matches_baseline_collapse_pattern_after_window")
    ):
        return (
            "existing_transfer_mediation_center_coupling_classes_already_author_"
            "blocked_lane_late_cascade_delay_before_shared_convergence"
        )
    return "post_spark_delay_authorability_inconclusive"


def build_grcv3_landscape_post_spark_delay_authorability_trace(
    *,
    baseline_seed_path: str | Path,
    blocked_control_seed_path: str | Path,
    refined_control_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
    late_window_start_step: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Test whether the blocked late-cascade delay is already authored by existing transfer mediation."""

    late_window_trace = build_grcv3_landscape_post_spark_late_window_stability_trace(
        baseline_seed_path=baseline_seed_path,
        blocked_control_seed_path=blocked_control_seed_path,
        refined_control_seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        late_window_start_step=late_window_start_step,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    blocked_control_seed = load_landscape_seed(Path(blocked_control_seed_path))
    refined_control_seed = load_landscape_seed(Path(refined_control_seed_path))
    blocked_to_refined_comparison = _compare_grcv3_seed_family_payloads(
        blocked_control_seed,
        refined_control_seed,
        family_names=[
            "transfer_mediation",
            "interfaces",
            "boundary_geometry",
            "channel_geometry",
            "interior_load_carriers",
            "local_geometry",
        ],
    )
    return {
        **late_window_trace,
        "blocked_to_refined_comparison": blocked_to_refined_comparison,
        "diagnosed_post_spark_delay_authorability": _diagnose_grcv3_post_spark_delay_authorability(
            blocked_post_window=late_window_trace["blocked_control_post_window"],
            refined_post_window=late_window_trace["refined_control_post_window"],
            blocked_to_refined_comparison=blocked_to_refined_comparison,
        ),
    }


def _diagnose_grcv3_post_collapse_geometry_exclusion(
    *,
    blocked_trace: Mapping[str, Any],
    refined_trace: Mapping[str, Any],
    blocked_to_refined_comparison: Mapping[str, Any],
) -> str:
    blocked_initial = blocked_trace.get("blocked_initial_collapse_record")
    blocked_reroute = blocked_trace.get("blocked_first_post_initial_reroute_record")
    blocked_match = blocked_trace.get("blocked_first_shared_pattern_record")
    same_structure_families = (
        "interfaces",
        "boundary_geometry",
        "channel_geometry",
        "interior_load_carriers",
        "local_geometry",
    )
    if (
        isinstance(blocked_initial, Mapping)
        and isinstance(blocked_reroute, Mapping)
        and isinstance(blocked_match, Mapping)
        and blocked_initial.get("sink_site", {}).get("site_kind") == "ridge_support"
        and blocked_reroute.get("sink_site", {}).get("site_kind") == "split_child"
        and blocked_match.get("sink_site", {}).get("site_kind") == "basin_support"
        and not blocked_to_refined_comparison["transfer_mediation"]["same"]
        and all(
            blocked_to_refined_comparison[family_name]["same"]
            for family_name in same_structure_families
        )
        and not refined_trace["refined_has_distinct_pre_shared_reroute"]
    ):
        return (
            "existing_transfer_mediation_center_coupling_classes_already_author_"
            "geometry_mediated_shift_away_from_initial_collapsed_sink"
        )
    return "post_collapse_geometry_exclusion_inconclusive"


def build_grcv3_landscape_post_collapse_geometry_exclusion_trace(
    *,
    blocked_control_seed_path: str | Path,
    refined_control_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
    late_window_start_step: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Trace how geometry reroutes the blocked lane away from its initial collapsed sink."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    if late_window_start_step < 0:
        raise ValueError("late_window_start_step must be >= 0")
    blocked_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=blocked_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    refined_lane = build_grcv3_landscape_collapse_lane_trace(
        seed_path=refined_control_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    baseline_pattern = (
        refined_lane.get("first_collapse_source_site", {}).get("site_kind"),
        refined_lane.get("first_collapse_sink_site", {}).get("site_kind"),
    )
    blocked_records = list(blocked_lane.get("collapse_records", []))
    refined_records = list(refined_lane.get("collapse_records", []))
    blocked_initial_collapse_record = None if not blocked_records else blocked_records[0]
    blocked_initial_step = (
        None
        if blocked_initial_collapse_record is None
        else int(blocked_initial_collapse_record["step_index"])
    )
    blocked_post_initial_records = [
        record
        for record in blocked_records
        if blocked_initial_step is None
        or int(record["step_index"]) > int(blocked_initial_step)
    ]
    blocked_first_post_initial_reroute_record = next(
        (
            record
            for record in blocked_post_initial_records
            if record.get("sink_site", {}).get("site_kind")
            != (
                None
                if blocked_initial_collapse_record is None
                else blocked_initial_collapse_record.get("sink_site", {}).get("site_kind")
            )
        ),
        None,
    )
    blocked_first_shared_pattern_record = next(
        (
            record
            for record in blocked_post_initial_records
            if (
                record.get("source_site", {}).get("site_kind"),
                record.get("sink_site", {}).get("site_kind"),
            )
            == baseline_pattern
        ),
        None,
    )
    refined_first_shared_pattern_record = next(
        (
            record
            for record in refined_records
            if (
                record.get("source_site", {}).get("site_kind"),
                record.get("sink_site", {}).get("site_kind"),
            )
            == baseline_pattern
        ),
        None,
    )
    refined_has_distinct_pre_shared_reroute = any(
        (
            record.get("source_site", {}).get("site_kind"),
            record.get("sink_site", {}).get("site_kind"),
        )
        != baseline_pattern
        for record in refined_records
        if refined_first_shared_pattern_record is None
        or int(record["step_index"]) < int(refined_first_shared_pattern_record["step_index"])
    )
    blocked_to_refined_comparison = _compare_grcv3_seed_family_payloads(
        load_landscape_seed(Path(blocked_control_seed_path)),
        load_landscape_seed(Path(refined_control_seed_path)),
        family_names=[
            "transfer_mediation",
            "interfaces",
            "boundary_geometry",
            "channel_geometry",
            "interior_load_carriers",
            "local_geometry",
        ],
    )
    blocked_post_window_records = [
        record
        for record in blocked_records
        if int(record["step_index"]) > int(late_window_start_step)
    ]
    return {
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "blocked_control_seed_path": Path(blocked_control_seed_path).as_posix(),
        "refined_control_seed_path": Path(refined_control_seed_path).as_posix(),
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "late_window_start_step": int(late_window_start_step),
        "blocked_control_lane": blocked_lane,
        "refined_control_lane": refined_lane,
        "blocked_initial_collapse_record": blocked_initial_collapse_record,
        "blocked_first_post_initial_reroute_record": blocked_first_post_initial_reroute_record,
        "blocked_first_shared_pattern_record": blocked_first_shared_pattern_record,
        "refined_first_shared_pattern_record": refined_first_shared_pattern_record,
        "blocked_post_window_sink_kind_sequence": _ordered_unique_site_kinds(
            blocked_post_window_records,
            key="sink_site",
        ),
        "blocked_post_window_source_kind_sequence": _ordered_unique_site_kinds(
            blocked_post_window_records,
            key="source_site",
        ),
        "refined_has_distinct_pre_shared_reroute": refined_has_distinct_pre_shared_reroute,
        "blocked_to_refined_comparison": blocked_to_refined_comparison,
        "diagnosed_post_collapse_geometry_exclusion": _diagnose_grcv3_post_collapse_geometry_exclusion(
            blocked_trace={
                "blocked_initial_collapse_record": blocked_initial_collapse_record,
                "blocked_first_post_initial_reroute_record": blocked_first_post_initial_reroute_record,
                "blocked_first_shared_pattern_record": blocked_first_shared_pattern_record,
            },
            refined_trace={
                "refined_has_distinct_pre_shared_reroute": refined_has_distinct_pre_shared_reroute,
            },
            blocked_to_refined_comparison=blocked_to_refined_comparison,
        ),
    }


def _diagnose_grcv3_collapse_trace(
    *,
    direct_lane: Mapping[str, Any],
    path_lane: Mapping[str, Any],
    split_path_lane: Mapping[str, Any],
    split_direct_lane: Mapping[str, Any],
) -> str:
    lanes = [direct_lane, path_lane, split_path_lane, split_direct_lane]
    path_lanes = [path_lane, split_path_lane]
    direct_lanes = [direct_lane, split_direct_lane]
    if all(lane.get("first_collapse_step") is not None for lane in path_lanes) and all(
        lane.get("first_collapse_step") is None for lane in direct_lanes
    ):
        if all(
            lane.get("first_collapse_source_site", {}).get("site_kind") == "basin_support"
            and lane.get("first_collapse_sink_site", {}).get("site_kind") == "carrier_site"
            for lane in path_lanes
        ) and not any(
            bool(lane.get("later_split_child_collapse_participation"))
            for lane in path_lanes
        ):
            return (
                "collapse_is_path_regime_specific_support_to_carrier_resolution_and_"
                "not_split_child_driven_under_current_structure"
            )
    if any(lane.get("first_collapse_step") is None for lane in lanes):
        return "some_selected_lanes_do_not_reach_collapse_under_the_recorded_choice_envelope"
    initial_lanes = [direct_lane, path_lane]
    if all(
        bool(lane.get("collapse_source_matches_first_spark_locus_family"))
        for lane in initial_lanes
    ):
        if bool(split_path_lane.get("later_split_child_collapse_participation")) and not bool(
            split_direct_lane.get("later_split_child_collapse_participation")
        ):
            return (
                "collapse_follows_existing_settlement_structure_and_later_split_child_"
                "participation_is_regime_specific"
            )
        if not bool(split_path_lane.get("later_split_child_collapse_participation")) and not bool(
            split_direct_lane.get("later_split_child_collapse_participation")
        ):
            return "collapse_stays_with_initial_spark_locus_under_current_structure"
    return "collapse_locus_pattern_is_mixed_and_requires_further_lane_extension_before_schema_change"


def build_grcv3_landscape_collapse_regime_trace(
    *,
    direct_seed_path: str | Path,
    path_seed_path: str | Path,
    split_path_seed_path: str | Path,
    split_direct_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
    epsilon_choice: float,
    epsilon_collapse: float,
) -> dict[str, Any]:
    """Characterize collapse loci across the saved spindle-lane controls."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    direct_lane = _build_grcv3_collapse_lane_trace(
        seed_path=direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    path_lane = _build_grcv3_collapse_lane_trace(
        seed_path=path_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    split_path_lane = _build_grcv3_collapse_lane_trace(
        seed_path=split_path_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    split_direct_lane = _build_grcv3_collapse_lane_trace(
        seed_path=split_direct_seed_path,
        profile_name=profile_name,
        primitive_id=primitive_id,
        num_steps=num_steps,
        epsilon_choice=epsilon_choice,
        epsilon_collapse=epsilon_collapse,
    )
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "choice_backend": {
            "name": "sink_compatibility",
            "epsilon_choice": float(epsilon_choice),
            "epsilon_collapse": float(epsilon_collapse),
        },
        "direct_lane": direct_lane,
        "path_lane": path_lane,
        "split_path_lane": split_path_lane,
        "split_direct_lane": split_direct_lane,
        "diagnosed_collapse_read": _diagnose_grcv3_collapse_trace(
            direct_lane=direct_lane,
            path_lane=path_lane,
            split_path_lane=split_path_lane,
            split_direct_lane=split_direct_lane,
        ),
    }
