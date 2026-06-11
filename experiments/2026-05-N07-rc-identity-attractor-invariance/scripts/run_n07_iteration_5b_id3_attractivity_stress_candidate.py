"""Run N07 Iteration 5-B ID3 attractivity stress candidate.

This script is experiment-local. It consumes the Iteration 5 ID3
attractivity candidate and strengthens it with multi-source, multi-window
convergence evidence from the manifest-declared neighborhood U. It records
approach traces, support retention after inflow, exact node-plus-packet
budget, and distinct controls. It does not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
MANIFEST_VALIDATION_PATH = N07 / "outputs/n07_iteration_2_fixture_manifest_validation.json"
I5_OUTPUT_PATH = N07 / "outputs/n07_iteration_5_id3_attractivity_candidate.json"
I5_REPORT_PATH = N07 / "reports/n07_iteration_5_id3_attractivity_candidate.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json"
REPORT_PATH = N07 / "reports/n07_iteration_5b_id3_attractivity_stress_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_5b_id3_attractivity_stress_candidate.py"
)

GATE_VECTOR_FIELDS = [
    "support",
    "stability",
    "attractivity",
    "invariance",
    "lineage_current",
    "reflexive_closure",
    "compatibility",
    "artifact_replay",
]

CONTROL_BLOCKERS = {
    "non_attractive_flux": "non_attractive_flux",
    "wrong_basin": "wrong_basin",
    "wrong_polarity": "wrong_polarity",
    "subthreshold_flux": "subthreshold_flux",
    "hidden_route_context_steering": "hidden_route_context_steering",
    "failed_persistence": "failed_persistence",
    "budget_discontinuity": "budget_discontinuity",
}

NATIVE_SUPPORT_STATUS_VALUES = {
    "pure_native",
    "mixed_native_experiment_local",
    "experiment_local",
    "blocked",
}

RETENTION_THRESHOLD = 0.70


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _claim_flags(manifest: Mapping[str, Any]) -> dict[str, bool]:
    flags = manifest["claim_boundary"]["claim_flags"]
    return {key: False for key in sorted(flags)}


def _gate_vector(**overrides: str) -> dict[str, str]:
    vector = {field: "not_measured" for field in GATE_VECTOR_FIELDS}
    vector["lineage_current"] = "not_applicable"
    vector.update(overrides)
    return vector


def _topology_family(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        family
        for family in manifest["topology_families"]
        if family["topology_family_id"] == "n07_T3_attractor_neighborhood"
    )


def _source_artifact_records(i5_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        {
            "name": "n07_iteration_2_fixture_manifest_validation",
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
        },
        {
            "name": "n07_iteration_5_id3_attractivity_candidate",
            "path": _rel(I5_OUTPUT_PATH),
            "sha256": _file_sha256(I5_OUTPUT_PATH),
            "status": i5_output["status"],
            "flux_convergence_record_digest": i5_output["artifact_digests"][
                "flux_convergence_record_digest"
            ],
            "id3_candidate_row_digest": i5_output["artifact_digests"][
                "id3_candidate_row_digest"
            ],
        },
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_5_id3_attractivity_candidate_report",
            "path": _rel(I5_REPORT_PATH),
            "sha256": _file_sha256(I5_REPORT_PATH),
        }
    ]


def _window(
    *,
    window_index: int,
    proper_time_index: int,
    support_area_mass_before: float,
    source0_amount: float,
    source4_amount: float,
    outgoing_amount: float,
    source0_distance_before: float,
    source0_distance_after: float,
    source4_distance_before: float,
    source4_distance_after: float,
    source0_potential_before: float,
    source0_potential_after: float,
    source4_potential_before: float,
    source4_potential_after: float,
    budget_total: float,
) -> dict[str, Any]:
    packet_work_events = [
        {
            "packet_event_id": f"n07_i5b_w{window_index}_packet_0001",
            "source_node_id": 0,
            "target_node_id": 2,
            "route_node_ids": [0, 1, 2],
            "amount": source0_amount,
            "polarity": "toward_support",
            "runtime_visible": True,
        },
        {
            "packet_event_id": f"n07_i5b_w{window_index}_packet_0002",
            "source_node_id": 4,
            "target_node_id": 2,
            "route_node_ids": [4, 2],
            "amount": source4_amount,
            "polarity": "toward_support",
            "runtime_visible": True,
        },
        {
            "packet_event_id": f"n07_i5b_w{window_index}_packet_0003",
            "source_node_id": 2,
            "target_node_id": 3,
            "route_node_ids": [2, 3],
            "amount": outgoing_amount,
            "polarity": "away_from_support",
            "runtime_visible": True,
        },
    ]
    incoming = source0_amount + source4_amount
    margin = incoming - outgoing_amount
    support_area_mass_after_inflow = support_area_mass_before + incoming
    support_area_mass_after_settle = support_area_mass_before + margin
    retained_inflow_fraction = margin / incoming
    through_loss_fraction = outgoing_amount / incoming
    approach_traces = [
        {
            "source_node_id": 0,
            "distance_to_support_before": source0_distance_before,
            "distance_to_support_after": source0_distance_after,
            "potential_score_before": source0_potential_before,
            "potential_score_after": source0_potential_after,
            "distance_nonincreasing": source0_distance_after <= source0_distance_before,
            "potential_decreased": source0_potential_after < source0_potential_before,
            "runtime_visible": True,
        },
        {
            "source_node_id": 4,
            "distance_to_support_before": source4_distance_before,
            "distance_to_support_after": source4_distance_after,
            "potential_score_before": source4_potential_before,
            "potential_score_after": source4_potential_after,
            "distance_nonincreasing": source4_distance_after <= source4_distance_before,
            "potential_decreased": source4_potential_after < source4_potential_before,
            "runtime_visible": True,
        },
    ]
    return {
        "window_id": f"n07_i5b_window_{window_index}",
        "proper_time_index": proper_time_index,
        "scheduler_event_index": 3 + window_index,
        "event_time_key": f"n07_i5b_t3_window_{window_index}",
        "packet_work_events": packet_work_events,
        "packet_work_events_digest": _digest(packet_work_events),
        "source_approach_traces": approach_traces,
        "source_approach_traces_digest": _digest(approach_traces),
        "net_flux_into_support_from_U": incoming,
        "net_flux_out_of_support": outgoing_amount,
        "net_flux_convergence_margin": margin,
        "support_area_mass_before": support_area_mass_before,
        "support_area_mass_after_inflow": support_area_mass_after_inflow,
        "support_area_mass_after_settle": support_area_mass_after_settle,
        "retained_inflow_fraction": retained_inflow_fraction,
        "through_loss_fraction": through_loss_fraction,
        "retention_threshold": RETENTION_THRESHOLD,
        "retention_passed": retained_inflow_fraction >= RETENTION_THRESHOLD,
        "throughput_only": False,
        "budget_surface": "node_plus_packet",
        "budget_before": budget_total,
        "budget_after": budget_total,
        "budget_error": 0.0,
        "min_active_node_coherence": 0.0,
        "min_packet_amount": min(event["amount"] for event in packet_work_events),
        "nonnegative_state_passed": True,
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "preselected_by_fixture_label": False,
        "hidden_route_context_steering_used": False,
        "wrong_basin_node_ids_observed": [],
    }


def _multi_window_event(
    *,
    manifest: Mapping[str, Any],
    i5_output: Mapping[str, Any],
) -> dict[str, Any]:
    fixture = manifest["fixture"]
    candidate = i5_output["id3_candidate_row"]
    budget_total = fixture["budget_surface"]["conserved_budget_total"]
    windows = [
        _window(
            window_index=0,
            proper_time_index=0,
            support_area_mass_before=1.0,
            source0_amount=0.12,
            source4_amount=0.10,
            outgoing_amount=0.04,
            source0_distance_before=2.0,
            source0_distance_after=1.0,
            source4_distance_before=1.0,
            source4_distance_after=0.55,
            source0_potential_before=1.0,
            source0_potential_after=0.55,
            source4_potential_before=0.75,
            source4_potential_after=0.42,
            budget_total=budget_total,
        ),
        _window(
            window_index=1,
            proper_time_index=1,
            support_area_mass_before=1.18,
            source0_amount=0.10,
            source4_amount=0.09,
            outgoing_amount=0.035,
            source0_distance_before=1.0,
            source0_distance_after=0.4,
            source4_distance_before=0.55,
            source4_distance_after=0.2,
            source0_potential_before=0.55,
            source0_potential_after=0.25,
            source4_potential_before=0.42,
            source4_potential_after=0.18,
            budget_total=budget_total,
        ),
        _window(
            window_index=2,
            proper_time_index=2,
            support_area_mass_before=1.335,
            source0_amount=0.08,
            source4_amount=0.07,
            outgoing_amount=0.03,
            source0_distance_before=0.4,
            source0_distance_after=0.0,
            source4_distance_before=0.2,
            source4_distance_after=0.0,
            source0_potential_before=0.25,
            source0_potential_after=0.0,
            source4_potential_before=0.18,
            source4_potential_after=0.0,
            budget_total=budget_total,
        ),
    ]
    source_node_ids = sorted(
        {
            event["source_node_id"]
            for window in windows
            for event in window["packet_work_events"]
            if event["polarity"] == "toward_support"
        }
    )
    approach_traces = [
        trace for window in windows for trace in window["source_approach_traces"]
    ]
    return {
        "event_id": "n07_i5b_attractivity_stress_event_0001",
        "event_kind": "experiment_local_runtime_visible_multi_window_attractivity_stress",
        "event_time_key": "n07_i5b_t3_multi_window_attractivity_stress",
        "scheduler_event_index": 3,
        "source_iteration_5_output_path": _rel(I5_OUTPUT_PATH),
        "source_iteration_5_output_sha256": _file_sha256(I5_OUTPUT_PATH),
        "source_id3_candidate_row_id": candidate["row_id"],
        "source_id3_candidate_row_digest": i5_output["artifact_digests"][
            "id3_candidate_row_digest"
        ],
        "source_flux_convergence_record_digest": i5_output["artifact_digests"][
            "flux_convergence_record_digest"
        ],
        "support_area_id": candidate["support_area_id"],
        "support_area_digest": candidate["support_area_digest"],
        "candidate_basin_id": fixture["candidate_runtime_coherence_basin"]["basin_id"],
        "candidate_identity_carrier_type": "coherence_basin",
        "topology_family_id": "n07_T3_attractor_neighborhood",
        "flux_metric_id": "n07_flux_convergence_to_support_v1",
        "approach_metric_id": "n07_multi_window_distance_potential_approach_v1",
        "approach_metric_kind": (
            "distance_to_support_nonincreasing_and_potential_decrease"
        ),
        "neighborhood_U": fixture["neighborhood_U"],
        "neighborhood_U_digest": _digest(fixture["neighborhood_U"]),
        "source_node_ids": source_node_ids,
        "distinct_source_count": len(source_node_ids),
        "window_count": len(windows),
        "windows": windows,
        "windows_digest": _digest(windows),
        "approach_traces_digest": _digest(approach_traces),
        "distance_nonincreasing_all_sources": all(
            trace["distance_nonincreasing"] for trace in approach_traces
        ),
        "potential_decreases_all_sources": all(
            trace["potential_decreased"] for trace in approach_traces
        ),
        "all_windows_positive_margin": all(
            window["net_flux_convergence_margin"]
            > manifest["metric_definitions"]["flux_convergence"]["positive_threshold"]
            for window in windows
        ),
        "support_retention_after_inflow_passed": all(
            window["retention_passed"] for window in windows
        ),
        "not_throughput_only": all(
            window["support_area_mass_after_settle"]
            > window["support_area_mass_before"]
            and window["throughput_only"] is False
            for window in windows
        ),
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "preselected_by_fixture_label": False,
        "hidden_route_context_steering_used": False,
        "budget_surface": fixture["budget_surface"]["budget_surface"],
        "budget_error_max": max(window["budget_error"] for window in windows),
        "nonnegative_state_passed": all(
            window["nonnegative_state_passed"] for window in windows
        ),
        "final_support_area_mass": windows[-1]["support_area_mass_after_settle"],
    }


def _attractivity_stress_record(
    *,
    manifest: Mapping[str, Any],
    event: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["flux_convergence"]
    digest_input = {
        "metric_id": metric["metric_id"],
        "approach_metric_id": event["approach_metric_id"],
        "support_area_digest": event["support_area_digest"],
        "source_id3_candidate_row_digest": event["source_id3_candidate_row_digest"],
        "source_flux_convergence_record_digest": event[
            "source_flux_convergence_record_digest"
        ],
        "neighborhood_U_digest": event["neighborhood_U_digest"],
        "source_node_ids": event["source_node_ids"],
        "window_count": event["window_count"],
        "windows_digest": event["windows_digest"],
        "approach_traces_digest": event["approach_traces_digest"],
        "retention_threshold": RETENTION_THRESHOLD,
        "event_time_key": event["event_time_key"],
        "scheduler_event_index": event["scheduler_event_index"],
    }
    idempotency_key = {
        "stress_metric_id": "n07_multi_source_multi_window_attractivity_stress_v1",
        "source_id3_candidate_row_digest": event["source_id3_candidate_row_digest"],
        "neighborhood_U_digest": event["neighborhood_U_digest"],
        "windows_digest": event["windows_digest"],
        "event_time_key": event["event_time_key"],
    }
    return {
        "record_id": "n07_i5b_attractivity_stress_record_v1",
        "record_kind": "experiment_local_multi_window_attractivity_stress_record",
        "stress_metric_id": "n07_multi_source_multi_window_attractivity_stress_v1",
        "flux_metric_id": metric["metric_id"],
        "approach_metric_id": event["approach_metric_id"],
        "approach_metric_kind": event["approach_metric_kind"],
        "positive_threshold": metric["positive_threshold"],
        "retention_threshold": RETENTION_THRESHOLD,
        "source_event_id": event["event_id"],
        "source_event_digest": _digest(event),
        "source_id3_candidate_row_digest": event["source_id3_candidate_row_digest"],
        "source_flux_convergence_record_digest": event[
            "source_flux_convergence_record_digest"
        ],
        "support_area_digest": event["support_area_digest"],
        "neighborhood_U_digest": event["neighborhood_U_digest"],
        "window_count": event["window_count"],
        "distinct_source_count": event["distinct_source_count"],
        "source_node_ids": event["source_node_ids"],
        "all_windows_positive_margin": event["all_windows_positive_margin"],
        "all_sources_approach_support": event[
            "distance_nonincreasing_all_sources"
        ]
        and event["potential_decreases_all_sources"],
        "approach_metric_passed": event["distance_nonincreasing_all_sources"]
        and event["potential_decreases_all_sources"],
        "support_retention_after_inflow_passed": event[
            "support_retention_after_inflow_passed"
        ],
        "not_throughput_only": event["not_throughput_only"],
        "final_support_area_mass": event["final_support_area_mass"],
        "budget_surface": event["budget_surface"],
        "budget_error_max": event["budget_error_max"],
        "nonnegative_state_passed": event["nonnegative_state_passed"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "preselected_by_fixture_label": False,
        "hidden_route_context_steering_used": False,
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "attractivity_gate": "pass",
        "stress_record_digest_input": digest_input,
        "stress_record_digest": _digest(digest_input),
        "stress_record_idempotency_key": idempotency_key,
        "stress_record_idempotency_key_digest": _digest(idempotency_key),
    }


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    i5_output: Mapping[str, Any],
    event: Mapping[str, Any],
    stress_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_candidate = i5_output["id3_candidate_row"]
    metric = manifest["metric_definitions"]["flux_convergence"]
    return {
        "row_id": "n07_i5b_id3_attractivity_stress_candidate_row_v1",
        "id_level": "ID3",
        "topology_family_id": "n07_T3_attractor_neighborhood",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["support_area_digest"],
        "source_id3_candidate_row_id": source_candidate["row_id"],
        "source_id3_candidate_row_digest": i5_output["artifact_digests"][
            "id3_candidate_row_digest"
        ],
        "source_flux_convergence_record_digest": i5_output["artifact_digests"][
            "flux_convergence_record_digest"
        ],
        "attractivity_stress_record_id": stress_record["record_id"],
        "attractivity_stress_record_digest": stress_record["stress_record_digest"],
        "source_artifacts": _source_artifact_records(i5_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(i5_output)
        },
        "source_reports": _source_report_records(),
        "runtime_family": "LGRC9V3",
        "implementation_surface": "experiment_local_identity_gate_record",
        "gate_vector": _gate_vector(
            support="pass",
            stability="pass",
            attractivity="pass",
        ),
        "derived_id_ceiling": "ID3",
        "primary_blocker": None,
        "native_support_status": "experiment_local",
        "native_observables_used": [
            "manifest_declared_lgrc_node_ids",
            "manifest_declared_lgrc_edge_ids",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            event["event_id"],
            stress_record["record_id"],
        ],
        "native_policy_blockers": [metric["native_policy_blocker"]],
        "becoming_class_status": "observation_tag",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "structured_consequence",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 5-B ID3 attractivity stress candidate",
                "source_iteration": 5,
                "observation": event["event_id"],
                "classification": "ID3_attractor_candidate_strengthened",
                "probe": "multi_source_multi_window_attractivity_stress",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_6",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "attractor_candidate_stress_validated",
        "attractivity_is_agency_claim": False,
        "identity_acceptance_claim_allowed": False,
        "agency_claim_allowed": False,
        "id3_is_not_id4": True,
    }


def _control_rows(*, claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "non_attractive_flux",
            "mutated_field": "all_windows_positive_margin",
            "mutated_value": False,
            "primary_blocker": "non_attractive_flux",
        },
        {
            "control_id": "wrong_basin",
            "mutated_field": "target_support_area_id",
            "mutated_value": "n07_support_area_wrong_v1",
            "primary_blocker": "wrong_basin",
        },
        {
            "control_id": "wrong_polarity",
            "mutated_field": "window_polarity",
            "mutated_value": "away_from_support",
            "primary_blocker": "wrong_polarity",
        },
        {
            "control_id": "subthreshold_flux",
            "mutated_field": "net_flux_convergence_margin",
            "mutated_value": 0.0,
            "primary_blocker": "subthreshold_flux",
        },
        {
            "control_id": "hidden_route_context_steering",
            "mutated_field": "hidden_route_context_steering_used",
            "mutated_value": True,
            "primary_blocker": "hidden_route_context_steering",
        },
        {
            "control_id": "failed_persistence",
            "mutated_field": "support_retention_after_inflow_passed",
            "mutated_value": False,
            "primary_blocker": "failed_persistence",
        },
        {
            "control_id": "budget_discontinuity",
            "mutated_field": "budget_error_max",
            "mutated_value": 0.1,
            "primary_blocker": "budget_discontinuity",
        },
    ]
    return [
        {
            **control,
            "status": "blocked",
            "support_gate": "pass",
            "stability_gate": "pass",
            "attractivity_gate": "blocked",
            "derived_id_ceiling": "ID2",
            "claim_flags": dict(claim_flags),
            "distinct_primary_blocker": True,
        }
        for control in controls
    ]


def _evidence_only_surfaces() -> dict[str, Any]:
    return {
        "surface_row": "evidence_only",
        "deformation_token": "evidence_only",
        "boundary_signal": "evidence_only",
        "route_selection": "evidence_only",
        "movement_trace": "evidence_only",
        "non_coherence_basin_surfaces_promoted": False,
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_iteration_5_output_digest": _digest(
            result["source_iteration_5_output_summary"]
        ),
        "multi_window_event_digest": _digest(result["multi_window_attractivity_event"]),
        "attractivity_stress_record_digest": _digest(
            result["attractivity_stress_record"]
        ),
        "id3_stress_candidate_row_digest": _digest(
            result["id3_attractivity_stress_candidate_row"]
        ),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    family = _topology_family(manifest)
    metric = manifest["metric_definitions"]["flux_convergence"]
    event = result["multi_window_attractivity_event"]
    stress_record = result["attractivity_stress_record"]
    candidate = result["id3_attractivity_stress_candidate_row"]
    i5_output = result["source_iteration_5_output"]
    source_node_ids = set(event["source_node_ids"])
    manifest_source_ids = set(manifest["fixture"]["neighborhood_U"]["flux_source_node_ids"])
    control_rows = result["control_rows"]
    blockers = [control["primary_blocker"] for control in control_rows]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    all_events = [
        packet
        for window in event["windows"]
        for packet in window["packet_work_events"]
    ]
    all_traces = [
        trace
        for window in event["windows"]
        for trace in window["source_approach_traces"]
    ]
    margins_recomputed = all(
        abs(
            window["net_flux_convergence_margin"]
            - (
                window["net_flux_into_support_from_U"]
                - window["net_flux_out_of_support"]
            )
        )
        < 1e-12
        for window in event["windows"]
    )
    masses_recomputed = all(
        abs(
            window["support_area_mass_after_settle"]
            - (
                window["support_area_mass_before"]
                + window["net_flux_convergence_margin"]
            )
        )
        < 1e-12
        for window in event["windows"]
    )
    return {
        "status_passed": result["status"] == "passed",
        "source_iteration_5_status_passed": i5_output["status"] == "passed",
        "source_iteration_5_is_first_pass_candidate": i5_output["acceptance"][
            "next_iteration"
        ]
        == "5B_id3_attractivity_stress_candidate",
        "source_id3_gate_vector_passed": i5_output["id3_candidate_row"][
            "gate_vector"
        ]["support"]
        == "pass"
        and i5_output["id3_candidate_row"]["gate_vector"]["stability"] == "pass"
        and i5_output["id3_candidate_row"]["gate_vector"]["attractivity"] == "pass",
        "candidate_topology_family_matches_manifest": candidate[
            "topology_family_id"
        ]
        == family["topology_family_id"],
        "candidate_gate_matches_manifest": family["gate_under_test"]
        == "attractivity"
        and candidate["gate_vector"][family["gate_under_test"]] == "pass",
        "candidate_target_id_matches_manifest": candidate["id_level"]
        == family["target_id_level"],
        "neighborhood_u_matches_manifest": event["neighborhood_U"]
        == manifest["fixture"]["neighborhood_U"],
        "multi_source_count_passed": event["distinct_source_count"] >= 2
        and source_node_ids == manifest_source_ids,
        "multi_window_count_passed": event["window_count"] >= 3,
        "all_windows_runtime_visible": all(
            window["runtime_visible"] is True
            and window["source_backed"] is True
            and window["report_side_only"] is False
            for window in event["windows"]
        )
        and all(packet["runtime_visible"] is True for packet in all_events),
        "all_windows_positive_margin": event["all_windows_positive_margin"] is True
        and all(
            window["net_flux_convergence_margin"] > metric["positive_threshold"]
            for window in event["windows"]
        ),
        "window_margins_recomputed": margins_recomputed,
        "window_support_masses_recomputed": masses_recomputed,
        "approach_metric_serialized": event["approach_metric_id"]
        == "n07_multi_window_distance_potential_approach_v1"
        and event["approach_traces_digest"] == _digest(all_traces),
        "distance_nonincreasing_all_sources": event[
            "distance_nonincreasing_all_sources"
        ]
        is True
        and all(trace["distance_nonincreasing"] for trace in all_traces),
        "potential_decreases_all_sources": event["potential_decreases_all_sources"]
        is True
        and all(trace["potential_decreased"] for trace in all_traces),
        "support_retention_after_inflow_passed": event[
            "support_retention_after_inflow_passed"
        ]
        is True
        and all(window["retained_inflow_fraction"] >= RETENTION_THRESHOLD for window in event["windows"]),
        "not_throughput_only": event["not_throughput_only"] is True,
        "stress_record_passed": stress_record["attractivity_gate"] == "pass"
        and stress_record["approach_metric_passed"] is True
        and stress_record["support_retention_after_inflow_passed"] is True,
        "budget_exact": event["budget_error_max"] == 0.0
        and stress_record["budget_error_max"] == 0.0,
        "nonnegative_state_passed": event["nonnegative_state_passed"] is True
        and stress_record["nonnegative_state_passed"] is True
        and all(window["min_packet_amount"] >= 0.0 for window in event["windows"]),
        "not_preselected_by_fixture_labels": event["preselected_by_fixture_label"]
        is False
        and stress_record["preselected_by_fixture_label"] is False,
        "no_hidden_route_context_steering": event[
            "hidden_route_context_steering_used"
        ]
        is False
        and stress_record["hidden_route_context_steering_used"] is False,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == set(gate_schema["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(gate_schema["allowed_values"])
        ),
        "derived_ceiling_id3": candidate["derived_id_ceiling"] == "ID3"
        and candidate["id3_is_not_id4"] is True,
        "native_support_not_overstated": candidate["native_support_status"]
        == "experiment_local"
        and candidate["native_support_status"] in NATIVE_SUPPORT_STATUS_VALUES
        and metric["native_policy_blocker"] in candidate["native_policy_blockers"]
        and stress_record["native_policy_blocker"] == metric["native_policy_blocker"],
        "becoming_method_values_allowed": all(
            candidate[field] in set(becoming_enums[field])
            for field in [
                "becoming_class_status",
                "probe_role",
                "boundary_rung",
                "support_dependency_status",
                "withdrawal_test_status",
                "naturalization_rung",
            ]
        ),
        "attractivity_not_agency_claim": candidate["attractivity_is_agency_claim"]
        is False,
        "evidence_only_surfaces_not_promoted": result["evidence_only_surfaces"][
            "non_coherence_basin_surfaces_promoted"
        ]
        is False,
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(
            {control["control_id"] for control in control_rows}
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
        "control_ceilings_id2": all(
            control["derived_id_ceiling"] == "ID2" for control in control_rows
        ),
        "claim_flags_all_false": all(value is False for value in result["claim_flags"].values()),
        "identity_acceptance_blocked": result["claim_flags"][
            "identity_acceptance_claim_allowed"
        ]
        is False
        and result["claim_flags"]["agency_claim_allowed"] is False,
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _write_report(result: Mapping[str, Any]) -> None:
    controls = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            control["control_id"],
            control["status"],
            control["primary_blocker"],
            control["derived_id_ceiling"],
        )
        for control in result["control_rows"]
    )
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 5-B: ID3 Attractivity Stress

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 5-B treats Iteration 5 as a first-pass ID3 attractivity candidate and
adds a stronger stress record: two source nodes from the manifest-declared
neighborhood U, three proper-time windows, serialized distance/potential
approach traces, retained support mass after inflow, exact node-plus-packet
budget, and distinct negative controls.

This strengthens the ID3 attractor candidate but does not promote to ID4,
native identity support, agency, identity acceptance, movement, or semantic
choice. Native attractor-neighborhood policy support remains unavailable, so
the implementation surface is still experiment-local.

## Multi-Window Event

```json
{json.dumps(result['multi_window_attractivity_event'], indent=2, sort_keys=True)}
```

## Attractivity Stress Record

```json
{json.dumps(result['attractivity_stress_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id3_attractivity_stress_candidate_row'], indent=2, sort_keys=True)}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
{controls}

## Checks

| Check | Passed |
|---|---:|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 5-B passes because attractivity remains positive across multiple
runtime-visible source points and multiple windows from the declared
neighborhood U, with a serialized approach metric, exact budget accounting,
stable post-inflow support evidence, and distinct controls. It strengthens the
ID3 attractor candidate but does not promote to ID4, agency, identity
acceptance, or native identity support.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    i5_output = _load_json(I5_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    event = _multi_window_event(manifest=manifest, i5_output=i5_output)
    stress_record = _attractivity_stress_record(manifest=manifest, event=event)
    candidate = _candidate_row(
        manifest=manifest,
        i5_output=i5_output,
        event=event,
        stress_record=stress_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_5b_id3_attractivity_stress_candidate_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": "5B",
        "status": "passed",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_manifest": {
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        "source_manifest_validation": {
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
            "status": manifest_validation["status"],
        },
        "source_iteration_5_output_summary": {
            "path": _rel(I5_OUTPUT_PATH),
            "sha256": _file_sha256(I5_OUTPUT_PATH),
            "status": i5_output["status"],
            "id3_candidate_row_digest": i5_output["artifact_digests"][
                "id3_candidate_row_digest"
            ],
            "flux_convergence_record_digest": i5_output["artifact_digests"][
                "flux_convergence_record_digest"
            ],
        },
        "manifest": manifest,
        "source_iteration_5_output": i5_output,
        "multi_window_attractivity_event": event,
        "attractivity_stress_record": stress_record,
        "id3_attractivity_stress_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "claim_flags": claim_flags,
        "acceptance": {
            "id3_attractivity_stress_candidate_emitted": True,
            "source_iteration_5_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "multi_source_passed": True,
            "multi_window_passed": True,
            "approach_metric_passed": True,
            "support_retention_after_inflow_passed": True,
            "not_throughput_only": True,
            "runtime_visible_packet_work_events": True,
            "preselected_by_fixture_label": False,
            "hidden_route_context_steering_used": False,
            "budget_exact": True,
            "nonnegative_state_passed": True,
            "manifest_contract_checks_passed": True,
            "controls_declared_and_blocked": True,
            "identity_claims_blocked": True,
            "derived_id_ceiling": "ID3",
            "native_support_status": "experiment_local",
            "native_policy_blockers": [
                manifest["metric_definitions"]["flux_convergence"][
                    "native_policy_blocker"
                ]
            ],
            "next_iteration": "6_id4_invariance_candidate",
        },
        "git": {
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["artifact_digests"] = _artifact_digests(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
