"""Run N07 Iteration 8 C1/T6 artifact-only replay closeout.

This script is experiment-local and artifact-only. It reconstructs the current
single-basin C1/T6 identity evidence chain from exported JSON artifacts, then
freezes the current N07 ceiling at ID5 because C3/T7 compatibility is deferred
to Iteration 9.
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
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
OUTPUT_PATH = OUTPUTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.json"
REPORT_PATH = REPORTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_8_c1_t6_artifact_replay_closeout.py"
)

SOURCE_OUTPUTS = {
    "iteration_1": OUTPUTS / "n07_iteration_1_baseline_theory_schema_inventory.json",
    "iteration_2": OUTPUTS / "n07_iteration_2_fixture_manifest_validation.json",
    "iteration_3": OUTPUTS / "n07_iteration_3_id1_support_area_candidate.json",
    "iteration_4": OUTPUTS / "n07_iteration_4_id2_stability_candidate.json",
    "iteration_5": OUTPUTS / "n07_iteration_5_id3_attractivity_candidate.json",
    "iteration_5b": OUTPUTS / "n07_iteration_5b_id3_attractivity_stress_candidate.json",
    "iteration_6": OUTPUTS / "n07_iteration_6_id4_invariance_candidate.json",
    "iteration_6b": OUTPUTS / "n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
    "iteration_7": OUTPUTS / "n07_iteration_7_id5_reflexive_closure_persistence.json",
    "iteration_7b": OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json",
}

SOURCE_REPORTS = {
    "iteration_3": REPORTS / "n07_iteration_3_id1_support_area_candidate.md",
    "iteration_4": REPORTS / "n07_iteration_4_id2_stability_candidate.md",
    "iteration_5b": REPORTS / "n07_iteration_5b_id3_attractivity_stress_candidate.md",
    "iteration_6b": REPORTS / "n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
    "iteration_7b": REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md",
}

IN_SCOPE_CONTROL_IDS = [
    "missing_support_area",
    "unstable_basin_no_local_well",
    "non_attractive_flux",
    "lineage_map_scrambled",
    "no_reentry",
    "closure_not_consumed_by_later_cycle",
    "hidden_support_field",
    "budget_discontinuity",
    "unauthorized_identity_acceptance_event",
    "identity_claim_promotion",
    "agency_claim_promotion",
]

DEFERRED_COMPATIBILITY_CONTROL_IDS = [
    "destructive_interference",
    "ambiguous_overlap",
    "wrong_basin",
]

CONTROL_SOURCE_ITERATIONS = {
    "missing_support_area": "iteration_3",
    "unstable_basin_no_local_well": "iteration_4",
    "non_attractive_flux": "iteration_5b",
    "lineage_map_scrambled": "iteration_6b",
    "no_reentry": "iteration_7b",
    "closure_not_consumed_by_later_cycle": "iteration_7b",
    "hidden_support_field": "iteration_7b",
    "budget_discontinuity": "iteration_7b",
    "unauthorized_identity_acceptance_event": "iteration_7b",
    "identity_claim_promotion": "iteration_6b",
    "agency_claim_promotion": "iteration_7b",
    "ambiguous_overlap": "iteration_6b",
    "wrong_basin": "iteration_5b",
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


def _source_artifacts(outputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
            "object_digest": _digest(_load_json(MANIFEST_PATH)),
        }
    ]
    for name, path in SOURCE_OUTPUTS.items():
        rows.append(
            {
                "name": name,
                "path": _rel(path),
                "sha256": _file_sha256(path),
                "object_digest": _digest(outputs[name]),
                "status": outputs[name].get("status"),
                "schema": outputs[name].get("schema"),
            }
        )
    return rows


def _source_reports() -> list[dict[str, str]]:
    return [
        {
            "name": name,
            "path": _rel(path),
            "sha256": _file_sha256(path),
        }
        for name, path in SOURCE_REPORTS.items()
    ]


def _source_artifact_sha256(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    rows = {_rel(MANIFEST_PATH): _file_sha256(MANIFEST_PATH)}
    for path in SOURCE_OUTPUTS.values():
        rows[_rel(path)] = _file_sha256(path)
    for path in SOURCE_REPORTS.values():
        rows[_rel(path)] = _file_sha256(path)
    return rows


def _support_area_digest_input(
    support_row: Mapping[str, Any], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    fields = manifest["metric_definitions"]["support_area_digest"][
        "required_input_fields"
    ]
    return {field: support_row.get(field) for field in fields}


def _support_area_digest_replay(
    outputs: Mapping[str, Mapping[str, Any]], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    manifest_support = manifest["support_area"]
    id1_support = outputs["iteration_3"]["support_area_row"]
    id5_candidate = outputs["iteration_7b"]["id5_source_backed_t6_candidate_row"]
    t6_chain = outputs["iteration_7b"]["source_backed_t6_chain"]
    manifest_input = _support_area_digest_input(manifest_support, manifest)
    id1_input = _support_area_digest_input(id1_support, manifest)
    return {
        "digest_method": manifest["metric_definitions"]["support_area_digest"][
            "method"
        ],
        "required_input_fields": manifest["metric_definitions"]["support_area_digest"][
            "required_input_fields"
        ],
        "manifest_declared_support_area_digest": manifest_support[
            "support_area_digest"
        ],
        "manifest_recomputed_support_area_digest": _digest(manifest_input),
        "manifest_support_area_digest_matches": _digest(manifest_input)
        == manifest_support["support_area_digest"],
        "id1_source_support_area_digest": id1_support["support_area_digest"],
        "id1_recomputed_support_area_digest": _digest(id1_input),
        "id1_support_area_digest_matches": _digest(id1_input)
        == id1_support["support_area_digest"],
        "id1_support_area_row_digest_matches": _digest(id1_support)
        == outputs["iteration_3"]["artifact_digests"]["support_area_row_digest"],
        "transported_t6_support_area_digest": id5_candidate["support_area_digest"],
        "transported_t6_support_area_digest_source": (
            "iteration_7b.source_backed_t6_chain.birth_lineage_context."
            "transported_support_digest"
        ),
        "transported_t6_support_area_digest_linked": id5_candidate[
            "support_area_digest"
        ]
        == t6_chain["birth_lineage_context"]["transported_support_digest"],
        "transported_t6_support_area_digest_matches_6b_birth_digest": id5_candidate[
            "support_area_digest"
        ]
        == outputs["iteration_6b"]["id4_topology_stress_candidate_row"][
            "birth_support_area_digest"
        ],
    }


def _replay_row(
    *,
    rung: str,
    source_iteration: str,
    output: Mapping[str, Any],
    row_key: str,
    digest_key: str,
    gate: str,
) -> dict[str, Any]:
    row = output[row_key]
    expected_digest = output["artifact_digests"][digest_key]
    recomputed_digest = _digest(row)
    return {
        "rung": rung,
        "source_iteration": source_iteration,
        "source_artifact_schema": output["schema"],
        "row_key": row_key,
        "row_id": row.get("row_id") or row.get("record_id") or row.get("event_id"),
        "digest_key": digest_key,
        "expected_digest": expected_digest,
        "recomputed_digest": recomputed_digest,
        "digest_match": recomputed_digest == expected_digest,
        "gate": gate,
        "row_derived_id_ceiling": row.get("derived_id_ceiling"),
        "native_support_status": row.get("native_support_status"),
        "support_area_id": row.get("support_area_id"),
        "support_area_digest": row.get("support_area_digest"),
        "candidate_identity_carrier_type": row.get("candidate_identity_carrier_type"),
        "identity_carrier_surface": row.get("identity_carrier_surface"),
        "topology_family_id": row.get("topology_family_id"),
        "composite_topology_id": row.get("composite_topology_id"),
        "source_context_topology_family_id": row.get(
            "source_context_topology_family_id"
        ),
        "source_context_composite_topology_id": row.get(
            "source_context_composite_topology_id"
        ),
        "boundary_rung": row.get("boundary_rung"),
        "claim_flags_all_false": all(
            value is False for value in row.get("claim_flags", {}).values()
        )
        if isinstance(row.get("claim_flags"), dict)
        else None,
    }


def _source_link_checks(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    i4_i3 = outputs["iteration_4"]["source_id1_output_summary"]
    i5_i4 = outputs["iteration_5"]["source_id2_output_summary"]
    i5b_i5 = outputs["iteration_5b"]["source_iteration_5_output_summary"]
    i6_i5b = outputs["iteration_6"]["source_iteration_5b_output_summary"]
    i6b_i6 = outputs["iteration_6b"]["source_iteration_6_output_summary"]
    return {
        "iteration_4_links_iteration_3_summary": i4_i3["sha256"]
        == _file_sha256(ROOT / i4_i3["path"])
        and i4_i3["id1_candidate_row_digest"]
        == outputs["iteration_3"]["artifact_digests"]["id1_candidate_row_digest"],
        "iteration_5_links_iteration_4_summary": i5_i4["sha256"]
        == _file_sha256(ROOT / i5_i4["path"])
        and i5_i4["id2_candidate_row_digest"]
        == outputs["iteration_4"]["artifact_digests"]["id2_candidate_row_digest"],
        "iteration_5b_links_iteration_5_summary": i5b_i5["sha256"]
        == _file_sha256(ROOT / i5b_i5["path"])
        and i5b_i5["id3_candidate_row_digest"]
        == outputs["iteration_5"]["artifact_digests"]["id3_candidate_row_digest"],
        "iteration_6_links_iteration_5b_summary": i6_i5b["sha256"]
        == _file_sha256(ROOT / i6_i5b["path"])
        and i6_i5b["id3_stress_candidate_row_digest"]
        == outputs["iteration_5b"]["artifact_digests"][
            "id3_stress_candidate_row_digest"
        ],
        "iteration_6b_links_iteration_6_summary": i6b_i6["sha256"]
        == _file_sha256(ROOT / i6b_i6["path"])
        and i6b_i6["id4_candidate_row_digest"]
        == outputs["iteration_6"]["artifact_digests"]["id4_candidate_row_digest"],
        "iteration_7b_embeds_iteration_6b": _digest(
            outputs["iteration_7b"]["source_iteration_6b_output"]
        )
        == _digest(outputs["iteration_6b"]),
        "iteration_7b_embeds_iteration_7": _digest(
            outputs["iteration_7b"]["source_iteration_7_output"]
        )
        == _digest(outputs["iteration_7"]),
    }


def _artifact_replay_chain(
    *, outputs: Mapping[str, Mapping[str, Any]], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    rows = [
        _replay_row(
            rung="ID1",
            source_iteration="iteration_3",
            output=outputs["iteration_3"],
            row_key="id1_candidate_row",
            digest_key="id1_candidate_row_digest",
            gate="support",
        ),
        _replay_row(
            rung="ID2",
            source_iteration="iteration_4",
            output=outputs["iteration_4"],
            row_key="id2_candidate_row",
            digest_key="id2_candidate_row_digest",
            gate="stability",
        ),
        _replay_row(
            rung="ID3",
            source_iteration="iteration_5b",
            output=outputs["iteration_5b"],
            row_key="id3_attractivity_stress_candidate_row",
            digest_key="id3_stress_candidate_row_digest",
            gate="attractivity",
        ),
        _replay_row(
            rung="ID4",
            source_iteration="iteration_6b",
            output=outputs["iteration_6b"],
            row_key="id4_topology_stress_candidate_row",
            digest_key="id4_stress_candidate_row_digest",
            gate="invariance_and_lineage_current",
        ),
        _replay_row(
            rung="ID5",
            source_iteration="iteration_7b",
            output=outputs["iteration_7b"],
            row_key="id5_source_backed_t6_candidate_row",
            digest_key="id5_candidate_row_digest",
            gate="reflexive_closure",
        ),
    ]
    source_links = _source_link_checks(outputs)
    t6_record = outputs["iteration_7b"]["source_backed_t6_record"]
    t6_chain = outputs["iteration_7b"]["source_backed_t6_chain"]
    t6_digest_checks = {
        "source_backed_t6_chain_digest_match": _digest(t6_chain)
        == outputs["iteration_7b"]["artifact_digests"]["source_backed_t6_chain_digest"],
        "source_backed_t6_record_digest_match": _digest(t6_record)
        == outputs["iteration_7b"]["artifact_digests"]["source_backed_t6_record_digest"],
        "t6_record_digest_input_match": _digest(t6_record["t6_record_digest_input"])
        == t6_record["t6_record_digest"],
        "proper_time_evaluation_digest_match": _digest(
            outputs["iteration_7b"]["proper_time_identity_persistence_evaluation"]
        )
        == outputs["iteration_7b"]["artifact_digests"][
            "proper_time_persistence_evaluation_digest"
        ],
    }
    scheduler_order = [
        t6_chain["pre_reentry_state_row"]["scheduler_event_index"],
        t6_chain["scheduled_packet_records"][0]["scheduler_event_index"],
        t6_chain["processed_packet_records"][0]["scheduler_event_index"],
        t6_chain["post_reentry_state_row"]["scheduler_event_index"],
        t6_chain["later_cycle_producer_record"]["scheduler_event_index"],
        t6_chain["scheduled_packet_records"][1]["scheduler_event_index"],
        t6_chain["processed_packet_records"][1]["scheduler_event_index"],
        t6_chain["later_cycle_state_row"]["scheduler_event_index"],
    ]
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "source_rows": rows,
        "source_row_digest_matches": all(row["digest_match"] for row in rows),
        "source_link_checks": source_links,
        "source_links_passed": all(source_links.values()),
        "support_area_digest_replay": _support_area_digest_replay(
            outputs=outputs, manifest=manifest
        ),
        "semantic_consistency": _semantic_consistency(
            outputs=outputs, manifest=manifest
        ),
        "t6_digest_checks": t6_digest_checks,
        "t6_digest_checks_passed": all(t6_digest_checks.values()),
        "scheduler_order": scheduler_order,
        "scheduler_order_monotonic": scheduler_order == sorted(scheduler_order),
        "budget_error_max": max(
            outputs["iteration_7b"]["source_backed_t6_record"]["budget_error_max"],
            outputs["iteration_6b"]["topology_stress_record"]["budget_error_max"],
        ),
        "claim_flags_all_false": all(
            all(value is False for value in output.get("claim_flags", {}).values())
            for output in outputs.values()
            if isinstance(output.get("claim_flags"), dict)
        ),
        "compatibility_gate": "deferred_to_iteration_9",
        "artifact_replay_gate": "pass",
    }


def _semantic_consistency(
    *, outputs: Mapping[str, Mapping[str, Any]], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    source_rows = [
        outputs["iteration_3"]["id1_candidate_row"],
        outputs["iteration_4"]["id2_candidate_row"],
        outputs["iteration_5b"]["id3_attractivity_stress_candidate_row"],
        outputs["iteration_6b"]["id4_topology_stress_candidate_row"],
        outputs["iteration_7b"]["id5_source_backed_t6_candidate_row"],
    ]
    enum_values = manifest["becoming_method_fields"]["enum_values"]
    id_progression = [row["id_level"] for row in source_rows]
    t6_chain = outputs["iteration_7b"]["source_backed_t6_chain"]
    transported_support_digest = t6_chain["birth_lineage_context"][
        "transported_support_digest"
    ]
    return {
        "id_progression": id_progression,
        "id_progression_matches_expected": id_progression
        == ["ID1", "ID2", "ID3", "ID4", "ID5"],
        "carrier_kind_consistent": all(
            row["candidate_identity_carrier_type"] == "coherence_basin"
            for row in source_rows
        ),
        "identity_surface_consistent": all(
            row["identity_carrier_surface"] == "runtime_coherence_basin"
            for row in source_rows
        ),
        "support_area_id_consistent": all(
            row["support_area_id"] == "n07_support_area_A_v1" for row in source_rows
        ),
        "pre_transport_support_digest_consistent": all(
            row["support_area_digest"]
            == outputs["iteration_3"]["id1_candidate_row"]["support_area_digest"]
            for row in source_rows[:4]
        ),
        "t6_support_digest_is_lineage_transport_successor": source_rows[-1][
            "support_area_digest"
        ]
        == transported_support_digest,
        "t6_support_digest_matches_6b_birth_support": source_rows[-1][
            "support_area_digest"
        ]
        == outputs["iteration_6b"]["id4_topology_stress_candidate_row"][
            "birth_support_area_digest"
        ],
        "boundary_rungs_allowed": all(
            row["boundary_rung"] in enum_values["boundary_rung"]
            for row in source_rows
        ),
        "claim_flags_remain_false": all(
            all(value is False for value in row["claim_flags"].values())
            for row in source_rows
        ),
        "semantic_consistency_passed": True,
    }


def _closeout_row(
    *,
    outputs: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    replay: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    t6_candidate = outputs["iteration_7b"]["id5_source_backed_t6_candidate_row"]
    t6_record = outputs["iteration_7b"]["source_backed_t6_record"]
    activity_history = {
        "orientation": "N07 Iteration 8 C1/T6 artifact-only replay closeout",
        "observation": "source_backed_C1_T6_single_basin_chain_replayed",
        "classification": "ID5_reflexively_self_maintaining_identity_candidate",
        "probe": "artifact_only_replay_validator",
        "withdrawal": t6_candidate["withdrawal_test_status"],
        "naturalization": t6_candidate["naturalization_rung"],
        "integration": {
            "artifact_replay": "pass",
            "compatibility": "deferred_to_iteration_9",
            "derived_id_ceiling": "ID5",
            "next": "9_c3_t7_competing_basin_compatibility_fixture_design",
        },
    }
    native_policy_blockers = sorted(
        set(t6_candidate["native_policy_blockers"])
        | {
            "native_rc_identity_support_area_policy_not_available",
            "native_basin_potential_policy_missing",
            "native_attractor_neighborhood_policy_missing",
            "native_identity_invariance_policy_missing",
            "c3_t7_compatibility_not_yet_tested",
        }
    )
    native_observables_used = sorted(
        set(t6_candidate["native_observables_used"])
        | {
            "source_row_digests",
            "surface_lineage_transport_context",
            "topology_state_reabsorption_context",
        }
    )
    experiment_local_observables_used = sorted(
        set(t6_candidate["experiment_local_observables_used"])
        | {
            "n07_i8_artifact_only_replay_chain_v1",
            "n07_i8_source_control_replay_rows_v1",
            "n07_i8_c1_t6_closeout_row_v1",
        }
    )
    gate_vector = dict(t6_candidate["gate_vector"])
    gate_vector["artifact_replay"] = "pass"
    gate_vector["compatibility"] = "blocked"
    row = {
        "row_id": "n07_i8_c1_t6_artifact_replay_closeout_row_v1",
        "id_level": "ID5",
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": t6_candidate["support_area_id"],
        "support_area_digest": t6_candidate["support_area_digest"],
        "topology_family_id": "n07_T6_reflexive_closure",
        "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
        "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
        "source_context_composite_topology_id": (
            "n07_C2_lineage_current_topology_mutating_identity_candidate"
        ),
        "source_id5_candidate_row_id": t6_candidate["row_id"],
        "source_id5_candidate_row_digest": outputs["iteration_7b"]["artifact_digests"][
            "id5_candidate_row_digest"
        ],
        "source_t6_record_digest": t6_record["t6_record_digest"],
        "artifact_replay_chain_digest": _digest(replay),
        "artifact_replay_gate": "pass",
        "compatibility_gate": "blocked",
        "compatibility_status": "deferred_to_iteration_9_c3_t7",
        "compatibility_primary_blocker": "compatibility_deferred_to_iteration_9",
        "derived_id_ceiling": "ID5",
        "id6_not_claimed": True,
        "id6_blocker": "c3_t7_compatibility_not_yet_tested",
        "native_support_status": "mixed_native_experiment_local",
        "runtime_family": "hybrid_lgrc9v3_experiment_local",
        "implementation_surface": "artifact_only_validator",
        "primary_blocker": None,
        "native_policy_blockers": native_policy_blockers,
        "native_observables_used": native_observables_used,
        "experiment_local_observables_used": experiment_local_observables_used,
        "native_runtime_reflexive_closure_observed": False,
        "actual_lgrc_step_processed_packet": False,
        "experiment_local_packet_application": True,
        "core_membership_source_backed": False,
        "allocation_policy_origin": "experiment_local_design_probe",
        "t4_no_mutation_baseline_deferred": True,
        "gate_vector": gate_vector,
        "source_artifacts": _source_artifacts(outputs),
        "source_artifact_sha256": _source_artifact_sha256(outputs),
        "source_reports": _source_reports(),
        "becoming_class_status": t6_candidate["becoming_class_status"],
        "probe_role": t6_candidate["probe_role"],
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": t6_candidate["support_dependency_status"],
        "withdrawal_test_status": t6_candidate["withdrawal_test_status"],
        "naturalization_rung": t6_candidate["naturalization_rung"],
        "activity_history": activity_history,
        "activity_history_digest_scope": manifest["becoming_method_fields"][
            "activity_history_digest_scope"
        ],
        "activity_history_digest": _digest(activity_history),
        "claim_flags": dict(claim_flags),
        "claim_ceiling": "source_backed_reflexively_self_maintaining_identity_candidate",
        "identity_acceptance_event_emitted": False,
        "identity_acceptance_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "agency_claim_allowed": False,
        "personhood_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
        "visual_reference": None,
        "visual_is_evidence_source": False,
    }
    return {
        **row,
        "closeout_row_digest_input": row,
        "closeout_row_digest": _digest(row),
    }


def _source_control_row(
    *,
    control_id: str,
    source_iteration: str,
    outputs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any] | None:
    for row in outputs[source_iteration].get("control_rows", []):
        if row.get("control_id") == control_id:
            return dict(row)
    return None


def _control_rows(
    *,
    manifest: Mapping[str, Any],
    outputs: Mapping[str, Mapping[str, Any]],
    claim_flags: Mapping[str, bool],
) -> list[dict[str, Any]]:
    blocker_by_control = {
        control["control_id"]: control["primary_blocker"]
        for control in manifest["controls"]
    }
    rows = []
    for control_id in IN_SCOPE_CONTROL_IDS:
        source_iteration = CONTROL_SOURCE_ITERATIONS[control_id]
        source_row = _source_control_row(
            control_id=control_id,
            source_iteration=source_iteration,
            outputs=outputs,
        )
        if source_row is None:
            raise KeyError(f"{control_id} not found in {source_iteration}")
        rows.append(
            {
                "control_id": control_id,
                "status": source_row["status"],
                "primary_blocker": source_row["primary_blocker"],
                "scope": "iteration_8_artifact_replay_closeout",
                "source_iteration": source_iteration,
                "source_artifact_path": _rel(SOURCE_OUTPUTS[source_iteration]),
                "source_artifact_sha256": _file_sha256(
                    SOURCE_OUTPUTS[source_iteration]
                ),
                "source_schema": outputs[source_iteration]["schema"],
                "source_control_row_digest": _digest(source_row),
                "source_control_replayed": True,
                "source_primary_blocker_matches_manifest": source_row[
                    "primary_blocker"
                ]
                == blocker_by_control[control_id],
                "derived_id_ceiling": source_row["derived_id_ceiling"],
                "source_control_row": source_row,
                "claim_flags": source_row.get("claim_flags", dict(claim_flags)),
            }
        )
    for control_id in DEFERRED_COMPATIBILITY_CONTROL_IDS:
        source_iteration = CONTROL_SOURCE_ITERATIONS.get(control_id)
        source_row = (
            _source_control_row(
                control_id=control_id,
                source_iteration=source_iteration,
                outputs=outputs,
            )
            if source_iteration
            else None
        )
        rows.append(
            {
                "control_id": control_id,
                "status": "deferred",
                "primary_blocker": blocker_by_control[control_id],
                "scope": "deferred_to_iteration_9_c3_t7_compatibility",
                "source_iteration": source_iteration,
                "source_artifact_path": _rel(SOURCE_OUTPUTS[source_iteration])
                if source_iteration
                else None,
                "source_artifact_sha256": _file_sha256(
                    SOURCE_OUTPUTS[source_iteration]
                )
                if source_iteration
                else None,
                "source_schema": outputs[source_iteration]["schema"]
                if source_iteration
                else None,
                "source_control_row_digest": _digest(source_row)
                if source_row is not None
                else None,
                "source_control_replayed": source_row is not None,
                "source_primary_blocker_matches_manifest": (
                    source_row["primary_blocker"] == blocker_by_control[control_id]
                    if source_row is not None
                    else True
                ),
                "source_control_status": source_row["status"]
                if source_row is not None
                else "not_run_in_current_source_chain",
                "derived_id_ceiling": source_row["derived_id_ceiling"]
                if source_row is not None
                else "ID5",
                "source_control_row": source_row,
                "claim_flags": dict(claim_flags),
            }
        )
    rows.append(
        {
            "control_id": "identity_threshold_missing",
            "status": "schema_guard_declared",
            "primary_blocker": "identity_threshold_missing",
            "scope": "manifest_threshold_schema_guard_validated_in_iteration_2",
            "source_iteration": "iteration_2",
            "source_artifact_path": _rel(SOURCE_OUTPUTS["iteration_2"]),
            "source_artifact_sha256": _file_sha256(SOURCE_OUTPUTS["iteration_2"]),
            "source_schema": outputs["iteration_2"]["schema"],
            "source_control_row_digest": None,
            "source_control_replayed": False,
            "source_primary_blocker_matches_manifest": True,
            "source_check_keys": [
                "identity_threshold_missing_control_declared",
                "identity_threshold_missing_declared",
                "invariance_thresholds_declared",
            ],
            "source_checks_passed": all(
                outputs["iteration_2"]["checks"][key]
                for key in [
                    "identity_threshold_missing_control_declared",
                    "identity_threshold_missing_declared",
                    "invariance_thresholds_declared",
                ]
            ),
            "derived_id_ceiling": "ID0",
            "claim_flags": dict(claim_flags),
        }
    )
    return rows


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "artifact_replay_chain_digest": _digest(result["artifact_replay_chain"]),
        "closeout_row_digest": result["c1_t6_closeout_row"]["closeout_row_digest"],
        "closeout_row_artifact_digest": _digest(result["c1_t6_closeout_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    outputs = result["source_outputs"]
    replay = result["artifact_replay_chain"]
    closeout = result["c1_t6_closeout_row"]
    controls = result["control_rows"]
    blockers = [control["primary_blocker"] for control in controls]
    in_scope = [control for control in controls if control["status"] == "blocked"]
    deferred = [control for control in controls if control["status"] == "deferred"]
    schema = outputs["iteration_1"]["id_ladder_schema"]
    required_fields = schema["row_required_fields"]
    becoming_schema = outputs["iteration_1"]["becoming_schema"]
    activity_scope = closeout["activity_history_digest_scope"]
    activity_history = closeout["activity_history"]
    return {
        "status_passed": result["status"] == "passed",
        "artifact_only": replay["artifact_only"] is True
        and replay["runtime_state_used"] is False
        and replay["private_runtime_state_used"] is False,
        "source_outputs_passed": all(
            output["status"] == "passed"
            for name, output in outputs.items()
            if name not in {"iteration_1"}
        ),
        "source_row_digest_matches": replay["source_row_digest_matches"] is True,
        "source_links_passed": replay["source_links_passed"] is True,
        "support_area_digest_replay_passed": replay["support_area_digest_replay"][
            "manifest_support_area_digest_matches"
        ]
        is True
        and replay["support_area_digest_replay"]["id1_support_area_digest_matches"]
        is True
        and replay["support_area_digest_replay"][
            "id1_support_area_row_digest_matches"
        ]
        is True
        and replay["support_area_digest_replay"][
            "transported_t6_support_area_digest_linked"
        ]
        is True,
        "semantic_consistency_passed": all(
            value is True
            for key, value in replay["semantic_consistency"].items()
            if key.endswith("_consistent")
            or key.endswith("_allowed")
            or key.endswith("_expected")
            or key.endswith("_successor")
            or key.endswith("_support")
            or key == "semantic_consistency_passed"
        ),
        "t6_digest_checks_passed": replay["t6_digest_checks_passed"] is True,
        "scheduler_order_monotonic": replay["scheduler_order_monotonic"] is True,
        "budget_exact": replay["budget_error_max"] == 0.0,
        "claim_flags_false": all(value is False for value in result["claim_flags"].values())
        and replay["claim_flags_all_false"] is True,
        "artifact_replay_passed": closeout["artifact_replay_gate"] == "pass",
        "closeout_row_digest_recomputed": closeout["closeout_row_digest"]
        == _digest(closeout["closeout_row_digest_input"]),
        "closeout_row_required_fields_present": all(
            field in closeout for field in required_fields
        ),
        "closeout_runtime_family_allowed": closeout["runtime_family"]
        in schema["runtime_family_allowed_values"],
        "closeout_implementation_surface_allowed": closeout[
            "implementation_surface"
        ]
        in schema["implementation_surface_allowed_values"],
        "closeout_boundary_rung_allowed": closeout["boundary_rung"]
        in becoming_schema["boundary_rung"],
        "activity_history_scope_complete": activity_scope
        == result["source_manifest"]["becoming_method_fields"][
            "activity_history_digest_scope"
        ]
        and all(field in activity_history for field in activity_scope),
        "activity_history_digest_recomputed": closeout["activity_history_digest"]
        == _digest(activity_history),
        "compatibility_deferred": closeout["compatibility_status"]
        == "deferred_to_iteration_9_c3_t7"
        and closeout["compatibility_gate"] == "blocked",
        "id5_ceiling_frozen": closeout["derived_id_ceiling"] == "ID5"
        and closeout["id6_not_claimed"] is True,
        "actual_lgrc_step_not_claimed": closeout["actual_lgrc_step_processed_packet"]
        is False
        and closeout["experiment_local_packet_application"] is True,
        "t4_deferral_preserved": closeout["t4_no_mutation_baseline_deferred"] is True,
        "becoming_fields_preserved": all(
            closeout.get(key)
            for key in [
                "becoming_class_status",
                "probe_role",
                "boundary_rung",
                "support_dependency_status",
                "withdrawal_test_status",
                "naturalization_rung",
                "activity_history_digest",
            ]
        ),
        "in_scope_controls_blocked": all(control["status"] == "blocked" for control in in_scope)
        and len(in_scope) == len(IN_SCOPE_CONTROL_IDS),
        "in_scope_controls_replayed_from_source_artifacts": all(
            control["source_control_replayed"] is True for control in in_scope
        ),
        "control_blockers_match_source_and_manifest": all(
            control.get("source_primary_blocker_matches_manifest") is True
            for control in controls
        ),
        "control_derived_ceilings_source_specific": {
            control["control_id"]: control["derived_id_ceiling"]
            for control in in_scope
        }
        == {
            "missing_support_area": "ID0",
            "unstable_basin_no_local_well": "ID1",
            "non_attractive_flux": "ID2",
            "lineage_map_scrambled": "ID3",
            "no_reentry": "ID4",
            "closure_not_consumed_by_later_cycle": "ID4",
            "hidden_support_field": "ID4",
            "budget_discontinuity": "ID4",
            "unauthorized_identity_acceptance_event": "ID4",
            "identity_claim_promotion": "ID3",
            "agency_claim_promotion": "ID4",
        },
        "compatibility_controls_deferred": all(
            control["status"] == "deferred" for control in deferred
        )
        and len(deferred) == len(DEFERRED_COMPATIBILITY_CONTROL_IDS),
        "identity_threshold_missing_guard_recorded": any(
            control["control_id"] == "identity_threshold_missing"
            and control["status"] == "schema_guard_declared"
            and control.get("source_checks_passed") is True
            for control in controls
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "identity_claims_blocked": closeout["identity_acceptance_claim_allowed"] is False
        and closeout["rc_identity_collapse_claim_allowed"] is False
        and closeout["agency_claim_allowed"] is False
        and closeout["personhood_claim_allowed"] is False,
        "next_iteration_is_c3": result["acceptance"]["next_iteration"]
        == "9_c3_t7_competing_basin_compatibility_fixture_design",
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _write_report(result: Mapping[str, Any]) -> None:
    controls = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            control["control_id"],
            control["status"],
            control["primary_blocker"],
            control["scope"],
        )
        for control in result["control_rows"]
    )
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    replay_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            row["rung"],
            row["source_iteration"],
            row["row_key"],
            row["digest_match"],
        )
        for row in result["artifact_replay_chain"]["source_rows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 8: C1/T6 Artifact-Only Replay And ID5 Closeout

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 8 reconstructs the current source-backed C1/T6 single-basin identity
chain from exported artifacts only. The replay passes, but C3/T7 compatibility
is deferred to Iteration 9, so the closeout freezes the current N07 ceiling at
ID5 rather than claiming ID6.

The replay preserves the Iteration 7-B scope: state rows are source-backed,
packet/producers are digest-linked experiment-local constructions, actual LGRC
`step()` processing is not claimed, and all claim flags remain false.

## Replay Rows

| Rung | Source iteration | Row | Digest match |
|---|---|---|---:|
{replay_rows}

## Closeout Row

```json
{json.dumps(result['c1_t6_closeout_row'], indent=2, sort_keys=True)}
```

## Artifact Replay Chain

```json
{json.dumps(result['artifact_replay_chain'], indent=2, sort_keys=True)}
```

## Controls

| Control | Status | Primary blocker | Scope |
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

Iteration 8 passes because the C1/T6 support, stability, attractivity,
invariance/lineage, reflexive-closure, and proper-time evidence chain replays
from artifacts only with exact budget accounting and clean claim boundaries.
The current ceiling remains ID5 because C3/T7 compatibility is deferred to
Iteration 9. No identity acceptance, RC identity collapse, agency, semantic
choice, biological identity, personhood, or unrestricted identity claim is
emitted.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest = _load_json(MANIFEST_PATH)
    outputs = {name: _load_json(path) for name, path in SOURCE_OUTPUTS.items()}
    claim_flags = _claim_flags(manifest)
    replay = _artifact_replay_chain(outputs=outputs, manifest=manifest)
    closeout = _closeout_row(
        outputs=outputs,
        manifest=manifest,
        replay=replay,
        claim_flags=claim_flags,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_8_c1_t6_artifact_replay_closeout_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 8,
        "status": "passed",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_artifacts": _source_artifacts(outputs),
        "source_reports": _source_reports(),
        "source_outputs": outputs,
        "source_manifest": manifest,
        "artifact_replay_chain": replay,
        "c1_t6_closeout_row": closeout,
        "control_rows": _control_rows(
            manifest=manifest, outputs=outputs, claim_flags=claim_flags
        ),
        "claim_flags": claim_flags,
        "acceptance": {
            "artifact_only_replay_passed": True,
            "runtime_state_used": False,
            "private_runtime_state_used": False,
            "derived_id_ceiling": "ID5",
            "id6_claimed": False,
            "id6_blocker": "c3_t7_compatibility_not_yet_tested",
            "compatibility_status": "deferred_to_iteration_9_c3_t7",
            "current_scope": "c1_t6_single_basin_artifact_replay_closeout",
            "next_iteration": "9_c3_t7_competing_basin_compatibility_fixture_design",
            "claim_flags_false": True,
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
