"""Private GRCV3 failure, candidate, and settlement-locus trace builders."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pygrc.models import DEFAULT_GRCV3_LANDSCAPE_PROFILE

from ._grcv3_trace_utils import (
    _build_grcv3_candidate_site_summary,
    _build_grcv3_event_locus_record,
    _build_grcv3_failure_trace_model,
    _build_grcv3_failure_trace_step_observation,
    _build_grcv3_settlement_regime_summary,
    _center_negative_curvature_run_length,
    _grcv3_realized_key_to_node_id,
    _update_grcv3_node_snapshot_cache,
)
from ._telemetry_utils import _to_plain_data


_FAILURE_TRACE_CURVATURE_DELTA_THRESHOLD = 0.1
_FAILURE_TRACE_PROBE_GRADIENT_DELTA_THRESHOLD = 0.1


def _failure_trace_probe_gradient_delta(
    baseline_probe_roles: Mapping[str, Mapping[str, Any]],
    comparison_probe_roles: Mapping[str, Mapping[str, Any]],
) -> float:
    shared_roles = set(baseline_probe_roles) & set(comparison_probe_roles)
    if not shared_roles:
        return 0.0
    return max(
        abs(
            float(baseline_probe_roles[role].get("gradient_norm", 0.0))
            - float(comparison_probe_roles[role].get("gradient_norm", 0.0))
        )
        for role in shared_roles
    )


def _detect_failure_trace_divergence_reason(
    *,
    baseline: Mapping[str, Any],
    comparison: Mapping[str, Any],
) -> str | None:
    baseline_center = baseline.get("center_site")
    comparison_center = comparison.get("center_site")
    if isinstance(baseline_center, Mapping) and isinstance(comparison_center, Mapping):
        if bool(baseline_center.get("spark_candidate_regime")) != bool(
            comparison_center.get("spark_candidate_regime")
        ):
            return "spark_candidate_regime_divergence"
        if bool(baseline_center.get("geometric_validation_pass")) != bool(
            comparison_center.get("geometric_validation_pass")
        ):
            return "geometric_validation_divergence"
        baseline_curvature = baseline_center.get("min_signed_eigenvalue")
        comparison_curvature = comparison_center.get("min_signed_eigenvalue")
        if baseline_curvature is not None and comparison_curvature is not None:
            if (
                abs(float(baseline_curvature) - float(comparison_curvature))
                > _FAILURE_TRACE_CURVATURE_DELTA_THRESHOLD
            ):
                return "weak_axis_curvature_divergence"
    probe_gradient_delta = _failure_trace_probe_gradient_delta(
        baseline.get("probe_roles", {}),
        comparison.get("probe_roles", {}),
    )
    if probe_gradient_delta > _FAILURE_TRACE_PROBE_GRADIENT_DELTA_THRESHOLD:
        return "probe_shell_gradient_norm_divergence"
    return None


def _diagnose_grcv3_failure_trace(
    steps: list[dict[str, Any]],
) -> str:
    early_step = next((step for step in steps if int(step["step_index"]) >= 1), None)
    if early_step is None:
        return "final_candidate_transition_blocked_after_geometry_near_correct"
    baseline = early_step["baseline"]
    comparison = early_step["comparison"]
    baseline_edge_roles = baseline.get("edge_roles", {})
    comparison_edge_roles = comparison.get("edge_roles", {})
    baseline_direct_transfer_flux = float(
        baseline_edge_roles.get("basin_patch_load_carrier_transfer", {}).get(
            "total_abs_flux",
            0.0,
        )
    )
    comparison_probe_ingress_flux = float(
        comparison_edge_roles.get("basin_patch_transfer_path_egress", {}).get(
            "total_abs_flux",
            0.0,
        )
    ) + float(
        comparison_edge_roles.get("basin_patch_transfer_mediation_spill", {}).get(
            "total_abs_flux",
            0.0,
        )
    )
    if (
        baseline_direct_transfer_flux > 0.0
        and comparison_probe_ingress_flux
        < 0.25 * baseline_direct_transfer_flux
    ):
        return "ingress_never_reaches_probe_shell_strongly_enough"
    baseline_center = baseline.get("center_site")
    comparison_center = comparison.get("center_site")
    if isinstance(baseline_center, Mapping) and isinstance(comparison_center, Mapping):
        baseline_curvature = baseline_center.get("min_signed_eigenvalue")
        comparison_curvature = comparison_center.get("min_signed_eigenvalue")
        if baseline_curvature is not None and comparison_curvature is not None:
            curvature_delta = abs(
                float(baseline_curvature) - float(comparison_curvature)
            )
            if curvature_delta > _FAILURE_TRACE_CURVATURE_DELTA_THRESHOLD:
                return "probe_shell_ingress_arrives_but_fails_to_form_weak_axis_geometry"
    return "final_candidate_transition_blocked_after_geometry_near_correct"


def build_grcv3_landscape_path_failure_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Compare the direct and path-mediated `rich.v4` lanes step-by-step."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    (
        resolved_baseline_seed_path,
        baseline_seed,
        baseline_model,
    ) = _build_grcv3_failure_trace_model(
        baseline_seed_path,
        profile_name=profile_name,
    )
    (
        resolved_comparison_seed_path,
        comparison_seed,
        comparison_model,
    ) = _build_grcv3_failure_trace_model(
        comparison_seed_path,
        profile_name=profile_name,
    )
    steps = [
        {
            "step_index": 0,
            "baseline": _build_grcv3_failure_trace_step_observation(
                baseline_model,
                primitive_id=primitive_id,
            ),
            "comparison": _build_grcv3_failure_trace_step_observation(
                comparison_model,
                primitive_id=primitive_id,
            ),
        }
    ]
    for _ in range(num_steps):
        baseline_step = baseline_model.step()
        comparison_step = comparison_model.step()
        steps.append(
            {
                "step_index": int(baseline_step.step_index),
                "baseline": _build_grcv3_failure_trace_step_observation(
                    baseline_model,
                    primitive_id=primitive_id,
                    event_kinds=tuple(event.kind for event in baseline_step.events),
                ),
                "comparison": _build_grcv3_failure_trace_step_observation(
                    comparison_model,
                    primitive_id=primitive_id,
                    event_kinds=tuple(event.kind for event in comparison_step.events),
                ),
            }
        )
    earliest_material_divergence_step = None
    earliest_material_divergence_reason = None
    for step in steps:
        if reason := _detect_failure_trace_divergence_reason(
            baseline=step["baseline"],
            comparison=step["comparison"],
        ):
            earliest_material_divergence_step = int(step["step_index"])
            earliest_material_divergence_reason = reason
            break
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "baseline_seed_name": baseline_seed.meta.name,
        "baseline_seed_path": resolved_baseline_seed_path.as_posix(),
        "comparison_seed_name": comparison_seed.meta.name,
        "comparison_seed_path": resolved_comparison_seed_path.as_posix(),
        "steps": steps,
        "earliest_material_divergence_step": earliest_material_divergence_step,
        "earliest_material_divergence_reason": earliest_material_divergence_reason,
        "diagnosed_failure_mode": _diagnose_grcv3_failure_trace(steps),
    }


def _diagnose_candidate_transition_blocker(
    candidate_sites: list[dict[str, Any]],
) -> str:
    comparison_sites = [
        site["comparison_site"]
        for site in candidate_sites
        if isinstance(site.get("comparison_site"), Mapping)
    ]
    if not comparison_sites:
        return "baseline_candidate_sites_do_not_exist_in_comparison"
    if all(not bool(site.get("candidate_gate_pass")) for site in comparison_sites):
        if all(not bool(site.get("gradient_below_threshold")) for site in comparison_sites):
            return "candidate_sites_never_settle_enough_to_enter_spark_gate"
        return "candidate_sites_settle_but_do_not_form_candidate_eigen_signature"
    return "candidate_sites_settle_but_fail_later_runtime_transition"


def build_grcv3_landscape_candidate_transition_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Trace why one lane reaches `spark_candidate` while another does not."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    (
        resolved_baseline_seed_path,
        baseline_seed,
        baseline_model,
    ) = _build_grcv3_failure_trace_model(
        baseline_seed_path,
        profile_name=profile_name,
    )
    (
        resolved_comparison_seed_path,
        comparison_seed,
        comparison_model,
    ) = _build_grcv3_failure_trace_model(
        comparison_seed_path,
        profile_name=profile_name,
    )
    steps = [
        {
            "step_index": 0,
            "baseline": _build_grcv3_failure_trace_step_observation(
                baseline_model,
                primitive_id=primitive_id,
            ),
            "comparison": _build_grcv3_failure_trace_step_observation(
                comparison_model,
                primitive_id=primitive_id,
            ),
        }
    ]
    baseline_first_candidate_step = None
    baseline_candidate_sites: list[dict[str, Any]] = []
    comparison_first_candidate_step = None
    comparison_candidate_sites: list[dict[str, Any]] = []
    for _ in range(num_steps):
        baseline_step = baseline_model.step()
        comparison_step = comparison_model.step()
        step_record = {
            "step_index": int(baseline_step.step_index),
            "baseline": _build_grcv3_failure_trace_step_observation(
                baseline_model,
                primitive_id=primitive_id,
                event_kinds=tuple(event.kind for event in baseline_step.events),
            ),
            "comparison": _build_grcv3_failure_trace_step_observation(
                comparison_model,
                primitive_id=primitive_id,
                event_kinds=tuple(event.kind for event in comparison_step.events),
            ),
        }
        steps.append(step_record)
        if comparison_first_candidate_step is None:
            comparison_candidate_events = [
                event for event in comparison_step.events if event.kind == "spark_candidate"
            ]
            if comparison_candidate_events:
                comparison_first_candidate_step = int(comparison_step.step_index)
                for event in comparison_candidate_events:
                    event_payload = event.payload if isinstance(event.payload, Mapping) else {}
                    comparison_node_id = int(event_payload["node_id"])
                    comparison_candidate_sites.append(
                        {
                            "event_payload": {
                                str(key): _to_plain_data(value)
                                for key, value in event_payload.items()
                            },
                            "comparison_site": {
                                **_build_grcv3_candidate_site_summary(
                                    comparison_model,
                                    node_id=comparison_node_id,
                                ),
                                "gradient_norm": float(
                                    event_payload.get("gradient_norm", 0.0)
                                ),
                                "signed_eigenvalues": list(
                                    event_payload.get("signed_eigenvalues", [])
                                ),
                                "gradient_below_threshold": float(
                                    event_payload.get("gradient_norm", 0.0)
                                )
                                < float(event_payload.get("epsilon_gradient", 0.0)),
                                "weak_eigen_below_spark": bool(
                                    event_payload.get("signed_eigenvalues", [])
                                )
                                and float(event_payload["signed_eigenvalues"][0])
                                < float(event_payload.get("epsilon_spark", 0.0)),
                                "stable_eigenvalues_above_hessian": all(
                                    float(value)
                                    > float(event_payload.get("epsilon_hessian", 0.0))
                                    for value in list(event_payload.get("signed_eigenvalues", []))[1:]
                                ),
                                "candidate_gate_pass": True,
                            },
                        }
                    )
        if baseline_first_candidate_step is not None:
            continue
        candidate_events = [
            event for event in baseline_step.events if event.kind == "spark_candidate"
        ]
        if not candidate_events:
            continue
        baseline_first_candidate_step = int(baseline_step.step_index)
        comparison_realized_key_map = _grcv3_realized_key_to_node_id(comparison_model)
        for event in candidate_events:
            event_payload = event.payload if isinstance(event.payload, Mapping) else {}
            baseline_node_id = int(event_payload["node_id"])
            baseline_payload = baseline_model.get_state().topology.node_payload(baseline_node_id)
            realized_key = str(baseline_payload.get("realized_key"))
            comparison_node_id = comparison_realized_key_map.get(realized_key)
            baseline_candidate_sites.append(
                {
                    "event_payload": {
                        str(key): _to_plain_data(value)
                        for key, value in event_payload.items()
                    },
                    "baseline_site": {
                        **_build_grcv3_candidate_site_summary(
                            baseline_model,
                            node_id=baseline_node_id,
                        ),
                        "gradient_norm": float(event_payload.get("gradient_norm", 0.0)),
                        "signed_eigenvalues": list(
                            event_payload.get("signed_eigenvalues", [])
                        ),
                        "gradient_below_threshold": float(
                            event_payload.get("gradient_norm", 0.0)
                        )
                        < float(event_payload.get("epsilon_gradient", 0.0)),
                        "weak_eigen_below_spark": bool(
                            event_payload.get("signed_eigenvalues", [])
                        )
                        and float(event_payload["signed_eigenvalues"][0])
                        < float(event_payload.get("epsilon_spark", 0.0)),
                        "stable_eigenvalues_above_hessian": all(
                            float(value) > float(event_payload.get("epsilon_hessian", 0.0))
                            for value in list(event_payload.get("signed_eigenvalues", []))[1:]
                        ),
                        "candidate_gate_pass": True,
                    },
                    "comparison_site": (
                        None
                        if comparison_node_id is None
                        else _build_grcv3_candidate_site_summary(
                            comparison_model,
                            node_id=comparison_node_id,
                        )
                    ),
                }
            )
    diagnosed_transition_blocker = _diagnose_candidate_transition_blocker(
        baseline_candidate_sites
    )
    baseline_center_negative_run_length = None
    comparison_center_negative_run_length = None
    if baseline_first_candidate_step is not None:
        baseline_center_negative_run_length = _center_negative_curvature_run_length(
            steps,
            side="baseline",
            end_step_index=baseline_first_candidate_step,
        )
        comparison_center_negative_run_length = _center_negative_curvature_run_length(
            steps,
            side="comparison",
            end_step_index=baseline_first_candidate_step,
        )
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "baseline_seed_name": baseline_seed.meta.name,
        "baseline_seed_path": resolved_baseline_seed_path.as_posix(),
        "comparison_seed_name": comparison_seed.meta.name,
        "comparison_seed_path": resolved_comparison_seed_path.as_posix(),
        "steps": steps,
        "baseline_first_candidate_step": baseline_first_candidate_step,
        "comparison_first_candidate_step": comparison_first_candidate_step,
        "baseline_center_negative_curvature_run_length_at_candidate_step": (
            baseline_center_negative_run_length
        ),
        "comparison_center_negative_curvature_run_length_at_baseline_candidate_step": (
            comparison_center_negative_run_length
        ),
        "baseline_candidate_sites": baseline_candidate_sites,
        "comparison_candidate_sites": comparison_candidate_sites,
        "diagnosed_transition_blocker": diagnosed_transition_blocker,
    }


def build_grcv3_landscape_settlement_locus_regime_trace(
    *,
    baseline_seed_path: str | Path,
    comparison_seed_path: str | Path,
    profile_name: str = DEFAULT_GRCV3_LANDSCAPE_PROFILE,
    primitive_id: str = "spindle_core",
    num_steps: int,
) -> dict[str, Any]:
    """Characterize the operative settlement locus in two spark-forming lanes."""

    if num_steps <= 0:
        raise ValueError("num_steps must be > 0")
    (
        resolved_baseline_seed_path,
        baseline_seed,
        baseline_model,
    ) = _build_grcv3_failure_trace_model(
        baseline_seed_path,
        profile_name=profile_name,
    )
    (
        resolved_comparison_seed_path,
        comparison_seed,
        comparison_model,
    ) = _build_grcv3_failure_trace_model(
        comparison_seed_path,
        profile_name=profile_name,
    )
    baseline_snapshot_cache: dict[int, dict[str, Any]] = {}
    comparison_snapshot_cache: dict[int, dict[str, Any]] = {}
    _update_grcv3_node_snapshot_cache(baseline_model, baseline_snapshot_cache)
    _update_grcv3_node_snapshot_cache(comparison_model, comparison_snapshot_cache)
    steps = [
        {
            "step_index": 0,
            "baseline": _build_grcv3_failure_trace_step_observation(
                baseline_model,
                primitive_id=primitive_id,
            ),
            "comparison": _build_grcv3_failure_trace_step_observation(
                comparison_model,
                primitive_id=primitive_id,
            ),
        }
    ]
    baseline_event_loci: list[dict[str, Any]] = []
    comparison_event_loci: list[dict[str, Any]] = []
    tracked_kinds = {"spark_candidate", "split_init", "spark", "split_complete"}
    for _ in range(num_steps):
        baseline_step = baseline_model.step()
        comparison_step = comparison_model.step()
        _update_grcv3_node_snapshot_cache(baseline_model, baseline_snapshot_cache)
        _update_grcv3_node_snapshot_cache(comparison_model, comparison_snapshot_cache)
        steps.append(
            {
                "step_index": int(baseline_step.step_index),
                "baseline": _build_grcv3_failure_trace_step_observation(
                    baseline_model,
                    primitive_id=primitive_id,
                    event_kinds=tuple(event.kind for event in baseline_step.events),
                ),
                "comparison": _build_grcv3_failure_trace_step_observation(
                    comparison_model,
                    primitive_id=primitive_id,
                    event_kinds=tuple(event.kind for event in comparison_step.events),
                ),
            }
        )
        for event in baseline_step.events:
            if event.kind in tracked_kinds:
                baseline_event_loci.append(
                    _build_grcv3_event_locus_record(
                        int(baseline_step.step_index),
                        event=event,
                        snapshot_cache=baseline_snapshot_cache,
                    )
                )
        for event in comparison_step.events:
            if event.kind in tracked_kinds:
                comparison_event_loci.append(
                    _build_grcv3_event_locus_record(
                        int(comparison_step.step_index),
                        event=event,
                        snapshot_cache=comparison_snapshot_cache,
                    )
                )
    return {
        "profile_name": profile_name,
        "primitive_id": primitive_id,
        "num_steps": num_steps,
        "baseline_seed_name": baseline_seed.meta.name,
        "baseline_seed_path": resolved_baseline_seed_path.as_posix(),
        "comparison_seed_name": comparison_seed.meta.name,
        "comparison_seed_path": resolved_comparison_seed_path.as_posix(),
        "steps": steps,
        "baseline_regime": _build_grcv3_settlement_regime_summary(
            steps=steps,
            side="baseline",
            event_loci=baseline_event_loci,
        ),
        "comparison_regime": _build_grcv3_settlement_regime_summary(
            steps=steps,
            side="comparison",
            event_loci=comparison_event_loci,
        ),
    }
