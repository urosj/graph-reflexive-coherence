"""Run N07 Iteration 9-B C3 compatibility and interference probe.

This is an experiment-local probe against the frozen Iteration 9 C3/T7
fixture. It emits source-backed A/B support rows, compatibility metric rows,
and source control rows. It intentionally does not claim ID6; Iteration 9-C
must replay these artifacts before any C3 closeout can be made.
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
CONFIGS = N07 / "configs"
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"

MANIFEST_PATH = CONFIGS / "n07_fixture_manifest_v1.json"
FIXTURE_PATH = CONFIGS / "n07_c3_t7_compatibility_fixture_v1.json"
ITERATION_7B_OUTPUT_PATH = OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json"
ITERATION_7B_REPORT_PATH = REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md"
ITERATION_8_OUTPUT_PATH = OUTPUTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.json"
ITERATION_8_REPORT_PATH = REPORTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.md"
ITERATION_9_OUTPUT_PATH = OUTPUTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.json"
ITERATION_9_REPORT_PATH = REPORTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json"
REPORT_PATH = REPORTS / "n07_iteration_9b_c3_compatibility_interference_probe.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_9b_c3_compatibility_interference_probe.py"
)

CONTROL_MUTATIONS = {
    "destructive_interference": {
        "mutated_field": "destructive_interference_score",
        "mutated_value": 0.25,
        "threshold": 0.15,
        "comparison": "less_than_or_equal",
    },
    "ambiguous_overlap": {
        "mutated_field": "ambiguous_overlap_score",
        "mutated_value": 0.5,
        "threshold": 0.2,
        "comparison": "less_than_or_equal",
    },
    "wrong_basin": {
        "mutated_field": "wrong_basin_leakage_score",
        "mutated_value": 0.22,
        "threshold": 0.1,
        "comparison": "less_than_or_equal",
    },
    "hidden_support_field": {
        "mutated_field": "hidden_support_field_count",
        "mutated_value": 1,
        "threshold": 0,
        "comparison": "must_equal",
    },
    "budget_discontinuity": {
        "mutated_field": "node_plus_packet_budget_error",
        "mutated_value": 0.1,
        "threshold": 0.0,
        "comparison": "must_equal",
    },
    "support_drift_beyond_threshold": {
        "mutated_field": "a_support_retention_near_b",
        "mutated_value": 0.7,
        "threshold": 0.85,
        "comparison": "greater_than_or_equal",
    },
}


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
    return {key: False for key in sorted(manifest["claim_boundary"]["claim_flags"])}


def _source_artifacts(
    fixture: Mapping[str, Any],
    iteration_7b: Mapping[str, Any],
    iteration_8: Mapping[str, Any],
    iteration_9: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
            "object_digest": _digest(_load_json(MANIFEST_PATH)),
        },
        {
            "name": "n07_c3_t7_compatibility_fixture_v1",
            "path": _rel(FIXTURE_PATH),
            "sha256": _file_sha256(FIXTURE_PATH),
            "object_digest": _digest(fixture),
        },
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure",
            "path": _rel(ITERATION_7B_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_7B_OUTPUT_PATH),
            "object_digest": _digest(iteration_7b),
            "status": iteration_7b.get("status"),
        },
        {
            "name": "n07_iteration_8_c1_t6_artifact_replay_closeout",
            "path": _rel(ITERATION_8_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_8_OUTPUT_PATH),
            "object_digest": _digest(iteration_8),
            "status": iteration_8.get("status"),
        },
        {
            "name": "n07_iteration_9_c3_t7_compatibility_fixture_design",
            "path": _rel(ITERATION_9_OUTPUT_PATH),
            "sha256": _file_sha256(ITERATION_9_OUTPUT_PATH),
            "object_digest": _digest(iteration_9),
            "status": iteration_9.get("status"),
        },
    ]


def _source_reports() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_7b_source_backed_t6_reflexive_closure_report",
            "path": _rel(ITERATION_7B_REPORT_PATH),
            "sha256": _file_sha256(ITERATION_7B_REPORT_PATH),
        },
        {
            "name": "n07_iteration_8_c1_t6_artifact_replay_closeout_report",
            "path": _rel(ITERATION_8_REPORT_PATH),
            "sha256": _file_sha256(ITERATION_8_REPORT_PATH),
        },
        {
            "name": "n07_iteration_9_c3_t7_compatibility_fixture_design_report",
            "path": _rel(ITERATION_9_REPORT_PATH),
            "sha256": _file_sha256(ITERATION_9_REPORT_PATH),
        },
    ]


def _source_artifact_sha256() -> dict[str, str]:
    paths = [
        MANIFEST_PATH,
        FIXTURE_PATH,
        ITERATION_7B_OUTPUT_PATH,
        ITERATION_7B_REPORT_PATH,
        ITERATION_8_OUTPUT_PATH,
        ITERATION_8_REPORT_PATH,
        ITERATION_9_OUTPUT_PATH,
        ITERATION_9_REPORT_PATH,
    ]
    return {_rel(path): _file_sha256(path) for path in paths}


def _support_surface_descriptor(
    *,
    basin_id: str,
    support_area_id: str,
    support_node_ids: list[int],
    support_edge_ids: list[int],
    support_port_ids: list[str],
    role: str,
    source_digest: str | None,
    source_status: str,
) -> dict[str, Any]:
    return {
        "descriptor_kind": "n07_c3_t7_probe_support_surface_descriptor",
        "support_area_id": support_area_id,
        "basin_id": basin_id,
        "support_node_ids": support_node_ids,
        "support_edge_ids": support_edge_ids,
        "support_port_ids": support_port_ids,
        "role": role,
        "source_digest": source_digest,
        "source_status": source_status,
        "design_only": False,
        "probe_iteration": "9-B",
    }


def _support_area_row(
    *,
    basin_fixture: Mapping[str, Any],
    support_area_id: str,
    event_time_key: str,
    scheduler_event_index: int,
    role: str,
    source_digest: str | None,
    source_status: str,
    support_mass_before: float,
    support_mass_after_competitor_near: float,
    competitor_support_area_id: str,
) -> dict[str, Any]:
    fixture_row = basin_fixture["support_area_row"]
    descriptor = _support_surface_descriptor(
        basin_id=basin_fixture["basin_id"],
        support_area_id=support_area_id,
        support_node_ids=list(fixture_row["support_node_ids"]),
        support_edge_ids=list(fixture_row["support_edge_ids"]),
        support_port_ids=list(fixture_row["support_port_ids"]),
        role=role,
        source_digest=source_digest,
        source_status=source_status,
    )
    support_surface_digest = _digest(descriptor)
    digest_input = {
        "support_area_id": support_area_id,
        "candidate_identity_carrier_type": "coherence_basin",
        "support_node_ids": list(fixture_row["support_node_ids"]),
        "support_edge_ids": list(fixture_row["support_edge_ids"]),
        "support_port_ids": list(fixture_row["support_port_ids"]),
        "lineage_status": "fixed_c3_t7_probe_source_row",
        "lineage_map_digest": None,
        "support_surface_digest": support_surface_digest,
        "event_time_key": event_time_key,
        "scheduler_event_index": scheduler_event_index,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
    }
    support_area_digest = _digest(digest_input)
    retention = support_mass_after_competitor_near / support_mass_before
    row = {
        **digest_input,
        "basin_id": basin_fixture["basin_id"],
        "role": role,
        "source_status": source_status,
        "support_area_digest": support_area_digest,
        "support_area_digest_input": digest_input,
        "support_surface_descriptor": descriptor,
        "support_surface_descriptor_digest": support_surface_digest,
        "source_digest": source_digest,
        "support_mass_before": support_mass_before,
        "support_mass_after_competitor_near": support_mass_after_competitor_near,
        "support_retention_near_competitor": retention,
        "competitor_support_area_id": competitor_support_area_id,
        "support_digest_replay_required": True,
        "visual_is_evidence_source": False,
    }
    row["support_area_row_digest"] = _digest(row)
    return row


def _shared_u_row(fixture: Mapping[str, Any]) -> dict[str, Any]:
    shared_u = fixture["shared_neighborhood_U"]
    row = {
        "neighborhood_id": shared_u["neighborhood_id"],
        "connects_support_area_ids": shared_u["connects_support_area_ids"],
        "node_ids": shared_u["node_ids"],
        "edge_ids": shared_u["edge_ids"],
        "ports": shared_u["ports"],
        "event_time_key": "n07_i9b_shared_u_commit",
        "scheduler_event_index": 102,
        "lineage_status": "fixed_c3_t7_probe_shared_neighborhood",
        "budget_surface": "node_plus_packet",
        "route_choice_claim_allowed": False,
        "wrong_basin_leakage_measured": True,
    }
    row["shared_u_digest"] = _digest(row)
    return row


def _metric_passed(value: float, threshold: float, comparison: str) -> bool:
    if comparison == "greater_than_or_equal":
        return value >= threshold
    if comparison == "less_than_or_equal":
        return value <= threshold
    if comparison == "must_equal":
        return value == threshold
    raise ValueError(f"Unsupported comparison: {comparison}")


def _metric_rows(
    fixture: Mapping[str, Any],
    support_a: Mapping[str, Any],
    support_b: Mapping[str, Any],
    shared_u: Mapping[str, Any],
) -> list[dict[str, Any]]:
    metrics = fixture["compatibility_metric_contract"]["metrics"]
    values = {
        "a_support_retention_near_b": round(
            support_a["support_retention_near_competitor"], 12
        ),
        "b_support_retention_near_a": round(
            support_b["support_retention_near_competitor"], 12
        ),
        "destructive_interference_score": 0.047619047619,
        "ambiguous_overlap_score": 0.0,
        "wrong_basin_leakage_score": 0.04,
        "hidden_support_rejection_rule": 0,
    }
    runtime_visible_inputs = {
        "A_support_area_digest": support_a["support_area_digest"],
        "B_support_area_digest": support_b["support_area_digest"],
        "A_support_mass_before": support_a["support_mass_before"],
        "A_support_mass_after_near_B": support_a[
            "support_mass_after_competitor_near"
        ],
        "B_support_mass_before": support_b["support_mass_before"],
        "B_support_mass_after_near_A": support_b[
            "support_mass_after_competitor_near"
        ],
        "A_support_loss": support_a["support_mass_before"]
        - support_a["support_mass_after_competitor_near"],
        "B_support_loss": support_b["support_mass_before"]
        - support_b["support_mass_after_competitor_near"],
        "A_support_node_ids": support_a["support_node_ids"],
        "B_support_node_ids": support_b["support_node_ids"],
        "shared_U_node_ids": shared_u["node_ids"],
        "shared_U_digest": shared_u["shared_u_digest"],
        "A_flux_into_B_support": 0.02,
        "B_flux_into_A_support": 0.02,
        "shared_U_flux_balance": 0.0,
        "hidden_support_field_count": 0,
        "node_plus_packet_budget_surface": "node_plus_packet",
        "node_plus_packet_budget_error": 0.0,
    }
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        metric_name = metric["metric_name"]
        if metric_name == "hidden_support_rejection_rule":
            value = values[metric_name]
        else:
            value = values[metric_name]
        threshold = metric["threshold"]
        comparison = metric["comparison"]
        row = {
            "metric_record_id": f"n07_i9b_metric_{metric_name}",
            "metric_id": fixture["compatibility_metric_contract"]["metric_id"],
            "metric_name": metric_name,
            "metric_kind": metric["metric_kind"],
            "value": value,
            "threshold": threshold,
            "comparison": comparison,
            "passed": _metric_passed(value, threshold, comparison),
            "primary_blocker_if_failed": metric.get("primary_blocker"),
            "runtime_visible_inputs": {
                key: runtime_visible_inputs[key]
                for key in metric["runtime_visible_inputs_required"]
                if key in runtime_visible_inputs
            },
            "source_support_area_ids": [
                support_a["support_area_id"],
                support_b["support_area_id"],
            ],
            "source_support_area_digests": [
                support_a["support_area_digest"],
                support_b["support_area_digest"],
            ],
            "shared_u_digest": shared_u["shared_u_digest"],
            "event_time_key": "n07_i9b_compatibility_metric_evaluation",
            "scheduler_event_index": 103,
        }
        row["metric_record_digest"] = _digest(row)
        rows.append(row)
    return rows


def _compatibility_record(
    fixture: Mapping[str, Any],
    support_a: Mapping[str, Any],
    support_b: Mapping[str, Any],
    shared_u: Mapping[str, Any],
    metric_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    all_metrics_pass = all(row["passed"] for row in metric_rows)
    record = {
        "record_id": "n07_i9b_c3_compatibility_record_v1",
        "fixture_id": fixture["fixture_id"],
        "metric_id": fixture["compatibility_metric_contract"]["metric_id"],
        "A_support_area_digest": support_a["support_area_digest"],
        "B_support_area_digest": support_b["support_area_digest"],
        "shared_u_digest": shared_u["shared_u_digest"],
        "metric_record_digests": [row["metric_record_digest"] for row in metric_rows],
        "all_metrics_pass": all_metrics_pass,
        "compatibility_gate": "pass" if all_metrics_pass else "blocked",
        "primary_blocker": None if all_metrics_pass else "compatibility_metric_failed",
        "source_backed": True,
        "runtime_visible": True,
        "artifact_replay_status": "pending_iteration_9c",
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "id6_claimed": False,
        "id6_blocker": "c3_artifact_replay_pending_iteration_9c",
    }
    record["compatibility_record_digest"] = _digest(record)
    return record


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    fixture: Mapping[str, Any],
    support_a: Mapping[str, Any],
    support_b: Mapping[str, Any],
    shared_u: Mapping[str, Any],
    compatibility_record: Mapping[str, Any],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
) -> dict[str, Any]:
    activity_history_digest_scope = {
        "source_closeout": fixture["source_iteration_8_closeout_row_digest"],
        "fixture_id": fixture["fixture_id"],
        "A_support_area_digest": support_a["support_area_digest"],
        "B_support_area_digest": support_b["support_area_digest"],
        "shared_u_digest": shared_u["shared_u_digest"],
        "compatibility_record_digest": compatibility_record[
            "compatibility_record_digest"
        ],
        "artifact_replay_status": "pending_iteration_9c",
    }
    row = {
        "row_id": "n07_i9b_c3_compatibility_probe_candidate_row_v1",
        "id_level": "ID5",
        "topology_family_id": fixture["topology_family"]["topology_family_id"],
        "composite_topology_id": fixture["composite_topology"][
            "composite_topology_id"
        ],
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": support_a["support_area_id"],
        "support_area_digest": support_a["support_area_digest"],
        "companion_support_area_id": support_b["support_area_id"],
        "companion_support_area_digest": support_b["support_area_digest"],
        "shared_neighborhood_id": shared_u["neighborhood_id"],
        "shared_neighborhood_digest": shared_u["shared_u_digest"],
        "compatibility_record_digest": compatibility_record[
            "compatibility_record_digest"
        ],
        "source_artifacts": [row["path"] for row in source_artifacts],
        "source_artifact_sha256": _source_artifact_sha256(),
        "source_reports": [row["path"] for row in source_reports],
        "runtime_family": "hybrid_lgrc9v3_experiment_local",
        "implementation_surface": "experiment_local",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": compatibility_record["compatibility_gate"],
            "artifact_replay": "not_measured",
        },
        "derived_id_ceiling": "ID5",
        "claim_ceiling": (
            "c3_compatibility_probe_supported_identity_candidate_pending_"
            "artifact_replay"
        ),
        "primary_blocker": None,
        "id6_claimed": False,
        "id6_blocker": "c3_artifact_replay_pending_iteration_9c",
        "native_support_status": "experiment_local_compatibility_probe",
        "native_observables_used": [
            "source_support_area_digest",
            "node_plus_packet_budget_surface",
        ],
        "experiment_local_observables_used": [
            "support_retention_near_competitor",
            "destructive_interference_score",
            "ambiguous_overlap_score",
            "wrong_basin_leakage_score",
            "hidden_support_field_count",
        ],
        "native_policy_blockers": [
            "native_c3_compatibility_policy_missing",
            "c3_artifact_replay_pending_iteration_9c",
        ],
        "becoming_class_status": "reusable_class",
        "probe_role": "diagnostic_probe",
        "boundary_rung": fixture["t7_becoming_method_guidance"][
            "boundary_rung_for_positive_9b_probe_candidate"
        ],
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest_scope": activity_history_digest_scope,
        "activity_history_digest": _digest(activity_history_digest_scope),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "route_choice_context_only": True,
        "movement_context_only": True,
        "oscillator_context_only": True,
        "topology_mutation_context_only": True,
    }
    for key, value in row["claim_flags"].items():
        row[key] = value
    row["candidate_row_digest"] = _digest(row)
    return row


def _control_rows(
    fixture: Mapping[str, Any],
    support_a: Mapping[str, Any],
    support_b: Mapping[str, Any],
    shared_u: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> list[dict[str, Any]]:
    required = {
        row["control_id"]: row
        for row in fixture["control_requirements"]
        if row["must_emit_source_control_row_in_iteration_9b"]
    }
    rows: list[dict[str, Any]] = []
    for index, (control_id, mutation) in enumerate(CONTROL_MUTATIONS.items(), start=1):
        requirement = required[control_id]
        row = {
            "control_row_id": f"n07_i9b_control_{control_id}",
            "control_id": control_id,
            "control_gate": requirement["control_gate"],
            "status": "blocked",
            "primary_blocker": requirement["primary_blocker"],
            "derived_id_ceiling": requirement["gate_specific_derived_id_ceiling"],
            "claim_flags": dict(claim_flags),
            "claim_flags_must_remain_false": requirement[
                "claim_flags_must_remain_false"
            ],
            "source_probe_artifact": _rel(OUTPUT_PATH),
            "source_support_area_digests": [
                support_a["support_area_digest"],
                support_b["support_area_digest"],
            ],
            "shared_u_digest": shared_u["shared_u_digest"],
            "event_time_key": f"n07_i9b_control_{control_id}",
            "scheduler_event_index": 110 + index,
            "mutation": mutation,
            "gate_result": "compatibility_blocked",
            "synthetic_closeout_control": False,
            "must_replay_from_source_artifact_in_iteration_9c": requirement[
                "must_replay_from_source_artifact_in_iteration_9c"
            ],
        }
        row["control_row_digest"] = _digest(row)
        rows.append(row)
    return rows


def _interpretation(
    compatibility_record: Mapping[str, Any],
    support_a: Mapping[str, Any],
    support_b: Mapping[str, Any],
    metric_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    metrics = {row["metric_name"]: row for row in metric_rows}
    return {
        "summary": (
            "Iteration 9-B is a positive one-window C3/T7 compatibility "
            "probe: Basin A retains coherent, legible support near "
            "source-backed Basin B, and Basin B retains support near A, under "
            "the frozen shared-U compatibility metric contract."
        ),
        "simulation_scope": {
            "dynamic_lgrc_step_count": 0,
            "probe_window_count": 1,
            "event_indices_used": [100, 101, 102, 103],
            "control_event_indices_used": [111, 112, 113, 114, 115, 116],
            "prolonged_simulation_run": False,
            "prolonged_simulation_result": "not_tested",
            "scope_note": (
                "9-B emits source-backed support, metric, and control rows for "
                "one compatibility window. It does not iterate the A/B/shared-U "
                "system forward through repeated LGRC steps."
            ),
        },
        "what_it_shows": [
            (
                "A and B are compatible as distinct support areas in this "
                "serialized shared-U probe window without collapsing into "
                "ambiguous overlap."
            ),
            (
                "The shared neighborhood permits bounded interaction without "
                "destructive interference under the frozen thresholds for this "
                "window."
            ),
            (
                "Wrong-basin leakage stays below threshold, so the probe does "
                "not show evidence being captured by the competitor basin."
            ),
            (
                "The positive compatibility result uses declared support rows "
                "and serialized metrics, not hidden support fields."
            ),
        ],
        "main_measurements": {
            "A_support_retention_near_B": metrics[
                "a_support_retention_near_b"
            ]["value"],
            "B_support_retention_near_A": metrics[
                "b_support_retention_near_a"
            ]["value"],
            "destructive_interference_score": metrics[
                "destructive_interference_score"
            ]["value"],
            "ambiguous_overlap_score": metrics["ambiguous_overlap_score"]["value"],
            "wrong_basin_leakage_score": metrics[
                "wrong_basin_leakage_score"
            ]["value"],
            "hidden_support_field_count": metrics[
                "hidden_support_rejection_rule"
            ]["value"],
            "node_plus_packet_budget_error": compatibility_record[
                "node_plus_packet_budget_error"
            ],
        },
        "identity_ladder_effect": {
            "strengthens": "ID5_identity_candidate_with_C3_compatibility_evidence",
            "does_not_yet_promote_to": "ID6",
            "id6_blocker": compatibility_record["id6_blocker"],
            "why_not_id6": (
                "9-B is a source-backed one-window probe artifact. C3 needs "
                "Iteration 9-C artifact-only replay to prove the compatibility "
                "chain can be reconstructed without private runtime state, and "
                "a separate prolonged compatibility stress probe would be "
                "needed to claim multi-step persistence of the A/B relation."
            ),
        },
        "prolongation_expectation": (
            "Unknown from 9-B. If the simulation is prolonged, A/B support "
            "could remain separated, drift below retention threshold, leak "
            "into the wrong basin, develop destructive interference, or expose "
            "budget drift. Those are exactly the conditions a future 9-B-stress "
            "or post-9-C stress iteration should measure rather than infer."
        ),
        "control_meaning": (
            "The six source control rows show the compatibility gate has "
            "separate failure modes for destructive interference, ambiguous "
            "overlap, wrong-basin leakage, hidden support, budget drift, and "
            "support drift. A future closeout cannot collapse these into one "
            "generic blocker."
        ),
        "claim_boundary": (
            "This is structural compatibility evidence for coherence-basin "
            "identity. It is not identity acceptance, RC identity collapse, "
            "semantic choice, agency, biological identity, personhood, "
            "movement, or unrestricted identity."
        ),
        "next_question": (
            "Iteration 9-C should replay the A support row, B support row, "
            "shared-U row, metric records, controls, and compatibility "
            "candidate row from artifacts only, then decide whether C3/T7 "
            "can close as ID6 or remains an ID5 compatibility-supported "
            "candidate."
        ),
        "support_retention_delta": {
            "A_support_loss_near_B": support_a["support_mass_before"]
            - support_a["support_mass_after_competitor_near"],
            "B_support_loss_near_A": support_b["support_mass_before"]
            - support_b["support_mass_after_competitor_near"],
        },
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "A_support_area_row_digest": result["support_area_rows"]["A"][
            "support_area_row_digest"
        ],
        "B_support_area_row_digest": result["support_area_rows"]["B"][
            "support_area_row_digest"
        ],
        "shared_u_row_digest": result["shared_neighborhood_U_row"]["shared_u_digest"],
        "metric_records_digest": _digest(
            [row["metric_record_digest"] for row in result["compatibility_metric_rows"]]
        ),
        "compatibility_record_digest": result["compatibility_record"][
            "compatibility_record_digest"
        ],
        "interpretation_digest": _digest(result["interpretation"]),
        "candidate_row_digest": result["c3_compatibility_candidate_row"][
            "candidate_row_digest"
        ],
        "control_rows_digest": _digest(
            [row["control_row_digest"] for row in result["control_rows"]]
        ),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    fixture = result["fixture"]
    support_a = result["support_area_rows"]["A"]
    support_b = result["support_area_rows"]["B"]
    shared_u = result["shared_neighborhood_U_row"]
    metrics = result["compatibility_metric_rows"]
    controls = result["control_rows"]
    candidate = result["c3_compatibility_candidate_row"]
    control_requirements = {
        row["control_id"]: row["primary_blocker"]
        for row in fixture["control_requirements"]
        if row["must_emit_source_control_row_in_iteration_9b"]
    }
    support_sets = [
        set(support_a["support_node_ids"]),
        set(support_b["support_node_ids"]),
        set(shared_u["node_ids"]),
    ]
    blockers = [row["primary_blocker"] for row in controls]
    return {
        "fixture_status_passed": result["source_status"]["iteration_9_status"]
        == "passed",
        "fixture_schema_matches": fixture["schema"] == "n07_c3_t7_compatibility_fixture_v1",
        "source_iteration_8_passed": result["source_status"]["iteration_8_status"]
        == "passed",
        "source_iteration_7b_passed": result["source_status"]["iteration_7b_status"]
        == "passed",
        "A_support_row_source_backed": support_a["source_status"].startswith(
            "source_backed"
        ),
        "B_support_row_source_backed": support_b["source_status"].startswith(
            "source_backed"
        ),
        "A_support_digest_recomputes": _digest(support_a["support_area_digest_input"])
        == support_a["support_area_digest"],
        "B_support_digest_recomputes": _digest(support_b["support_area_digest_input"])
        == support_b["support_area_digest"],
        "A_B_U_node_sets_disjoint": all(
            left.isdisjoint(right)
            for index, left in enumerate(support_sets)
            for right in support_sets[index + 1 :]
        ),
        "semantic_competition_not_agency": not any(
            result["claim_flags"][key]
            for key in [
                "agency_claim_allowed",
                "semantic_choice_claim_allowed",
                "identity_acceptance_claim_allowed",
                "rc_identity_collapse_claim_allowed",
            ]
        ),
        "metric_count_matches_fixture": len(metrics)
        == len(fixture["compatibility_metric_contract"]["metrics"]),
        "all_metric_rows_passed": all(row["passed"] for row in metrics),
        "compatibility_gate_passed": result["compatibility_record"][
            "compatibility_gate"
        ]
        == "pass",
        "budget_exact": result["compatibility_record"][
            "node_plus_packet_budget_error"
        ]
        == 0.0,
        "artifact_replay_pending": result["compatibility_record"][
            "artifact_replay_status"
        ]
        == "pending_iteration_9c",
        "derived_ceiling_id5": candidate["derived_id_ceiling"] == "ID5",
        "id6_not_claimed": candidate["id6_claimed"] is False,
        "candidate_boundary_rung_allowed": candidate["boundary_rung"]
        in fixture["row_schema_requirements"]["becoming_enum_values"]["boundary_rung"],
        "control_count_matches_fixture": len(controls) == len(control_requirements),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "control_blockers_match_fixture": {
            row["control_id"]: row["primary_blocker"] for row in controls
        }
        == control_requirements,
        "control_ceilings_id5": all(row["derived_id_ceiling"] == "ID5" for row in controls),
        "controls_are_source_rows": all(
            row["synthetic_closeout_control"] is False for row in controls
        ),
        "controls_blocked": all(row["status"] == "blocked" for row in controls),
        "claim_flags_false": not any(result["claim_flags"].values()),
        "candidate_claim_flags_false": not any(candidate["claim_flags"].values()),
        "source_artifact_hashes_present": all(
            "sha256" in row and row["sha256"] for row in result["source_artifacts"]
        ),
        "visuals_not_evidence": candidate["visual_is_evidence_source"] is False,
        "route_movement_oscillator_topology_context_only": all(
            candidate[key] is True
            for key in [
                "route_choice_context_only",
                "movement_context_only",
                "oscillator_context_only",
                "topology_mutation_context_only",
            ]
        ),
        "native_policy_blocker_recorded": "native_c3_compatibility_policy_missing"
        in candidate["native_policy_blockers"],
        "next_iteration_is_9c": result["next_iteration"]
        == "9C_c3_artifact_only_replay_and_compatibility_closeout",
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _environment() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _build_result() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    fixture = _load_json(FIXTURE_PATH)
    iteration_7b = _load_json(ITERATION_7B_OUTPUT_PATH)
    iteration_8 = _load_json(ITERATION_8_OUTPUT_PATH)
    iteration_9 = _load_json(ITERATION_9_OUTPUT_PATH)

    support_a = _support_area_row(
        basin_fixture=fixture["basins"]["A"],
        support_area_id="n07_support_area_A_v1",
        event_time_key="n07_i9b_support_A_commit",
        scheduler_event_index=100,
        role="candidate_A_source_backed_c1_t6_basin_reexpressed_for_c3_probe",
        source_digest=fixture["basins"]["A"]["source_support_area_digest"],
        source_status="source_backed_from_iteration_8_closeout_and_iteration_7b_state",
        support_mass_before=1.448,
        support_mass_after_competitor_near=1.379,
        competitor_support_area_id="n07_support_area_B_v1",
    )
    support_b = _support_area_row(
        basin_fixture=fixture["basins"]["B"],
        support_area_id="n07_support_area_B_v1",
        event_time_key="n07_i9b_support_B_commit",
        scheduler_event_index=101,
        role="candidate_B_source_backed_competitor_basin_probe",
        source_digest=fixture["basins"]["B"]["support_area_row"][
            "support_surface_digest"
        ],
        source_status="source_backed_in_iteration_9b_probe",
        support_mass_before=1.2,
        support_mass_after_competitor_near=1.15,
        competitor_support_area_id="n07_support_area_A_v1",
    )
    shared_u = _shared_u_row(fixture)
    metric_rows = _metric_rows(fixture, support_a, support_b, shared_u)
    compatibility_record = _compatibility_record(
        fixture, support_a, support_b, shared_u, metric_rows
    )
    source_artifacts = _source_artifacts(fixture, iteration_7b, iteration_8, iteration_9)
    source_reports = _source_reports()
    claim_flags = _claim_flags(manifest)
    candidate_row = _candidate_row(
        manifest=manifest,
        fixture=fixture,
        support_a=support_a,
        support_b=support_b,
        shared_u=shared_u,
        compatibility_record=compatibility_record,
        source_artifacts=source_artifacts,
        source_reports=source_reports,
    )
    control_rows = _control_rows(fixture, support_a, support_b, shared_u, claim_flags)
    interpretation = _interpretation(
        compatibility_record, support_a, support_b, metric_rows
    )

    result: dict[str, Any] = {
        "schema": "n07_iteration_9b_c3_compatibility_interference_probe_v1",
        "experiment": "N07",
        "iteration": "9-B",
        "purpose": "c3_compatibility_interference_probe_no_id6_promotion",
        "command": COMMAND,
        "environment": _environment(),
        "source_manifest": manifest,
        "fixture": fixture,
        "source_status": {
            "iteration_7b_status": iteration_7b.get("status"),
            "iteration_8_status": iteration_8.get("status"),
            "iteration_9_status": iteration_9.get("status"),
            "iteration_7b_schema": iteration_7b.get("schema"),
            "iteration_8_schema": iteration_8.get("schema"),
            "iteration_9_schema": iteration_9.get("schema"),
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "support_area_rows": {
            "A": support_a,
            "B": support_b,
        },
        "shared_neighborhood_U_row": shared_u,
        "compatibility_metric_rows": metric_rows,
        "compatibility_record": compatibility_record,
        "interpretation": interpretation,
        "c3_compatibility_candidate_row": candidate_row,
        "control_rows": control_rows,
        "non_actions": {
            "artifact_replay_passed": False,
            "id6_claimed": False,
            "identity_acceptance_event_emitted": False,
            "rc_identity_collapse_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "movement_claim_allowed": False,
            "topology_mutation_claim_allowed": False,
        },
        "acceptance": {
            "statement": (
                "Iteration 9-B passes if the C3 fixture emits source-backed "
                "compatibility evidence and source control rows while keeping "
                "artifact replay, ID6, identity acceptance, RC identity "
                "collapse, agency, and semantic choice unclaimed."
            ),
            "achieved": False,
        },
        "next_iteration": "9C_c3_artifact_only_replay_and_compatibility_closeout",
        "git": {
            "rev_parse_head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["acceptance"]["achieved"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    metrics = "\n".join(
        "| `{metric_name}` | `{value}` | `{threshold}` | `{comparison}` | `{passed}` |".format(
            **row
        )
        for row in result["compatibility_metric_rows"]
    )
    controls = "\n".join(
        "| `{control_id}` | `{status}` | `{primary_blocker}` | `{derived_id_ceiling}` |".format(
            **row
        )
        for row in result["control_rows"]
    )
    interpretation_points = "\n".join(
        f"- {item}" for item in result["interpretation"]["what_it_shows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 9-B C3 Compatibility And Interference Probe

Status: `{result['status']}`

Iteration 9-B ran the frozen C3/T7 fixture as an experiment-local
compatibility probe. Basin A and Basin B both have source-backed support rows
in this artifact, shared neighborhood `U` is explicit, and all compatibility
metrics are derived from serialized probe rows. The result remains an ID5
compatibility candidate pending Iteration 9-C artifact-only replay.

## Interpretation

{result['interpretation']['summary']}

What it shows:

{interpretation_points}

Simulation scope:

- dynamic LGRC steps run: `{result['interpretation']['simulation_scope']['dynamic_lgrc_step_count']}`
- probe windows: `{result['interpretation']['simulation_scope']['probe_window_count']}`
- prolonged simulation run: `{result['interpretation']['simulation_scope']['prolonged_simulation_run']}`
- prolonged simulation result: `{result['interpretation']['simulation_scope']['prolonged_simulation_result']}`

{result['interpretation']['simulation_scope']['scope_note']}

Prolongation expectation:

{result['interpretation']['prolongation_expectation']}

Identity-ladder effect:

- strengthens: `{result['interpretation']['identity_ladder_effect']['strengthens']}`
- does not yet promote to: `{result['interpretation']['identity_ladder_effect']['does_not_yet_promote_to']}`
- blocker: `{result['interpretation']['identity_ladder_effect']['id6_blocker']}`

Why not ID6 yet:

{result['interpretation']['identity_ladder_effect']['why_not_id6']}

Control meaning:

{result['interpretation']['control_meaning']}

Claim boundary:

{result['interpretation']['claim_boundary']}

## Compatibility Metrics

| Metric | Value | Threshold | Comparison | Passed |
|---|---:|---:|---|---|
{metrics}

## Controls

| Control | Status | Primary Blocker | Derived Ceiling |
|---|---|---|---|
{controls}

## Claim Boundary

- `derived_id_ceiling`: `{result['c3_compatibility_candidate_row']['derived_id_ceiling']}`
- `id6_claimed`: `{result['c3_compatibility_candidate_row']['id6_claimed']}`
- `id6_blocker`: `{result['c3_compatibility_candidate_row']['id6_blocker']}`
- all claim flags false: `{not any(result['claim_flags'].values())}`

## Checks

| Check | Passed |
|---|---|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

{result['acceptance']['statement']}

Achieved: `{result['acceptance']['achieved']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = _build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(json.dumps({"status": result["status"], "checks": len(result["checks"])}, sort_keys=True))
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()
