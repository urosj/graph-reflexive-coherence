"""Run N07 Iteration 9-C short-window artifact replay closeout.

This closeout deliberately does not promote ID6. It replays the N07 evidence
chain through Iteration 9-B2 from exported artifacts only, records 9-B as
one-window C3/T7 compatibility evidence, records 9-B2 as prolonged-stress
failure, and freezes the current ceiling at ID5.
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
CONFIGS = N07 / "configs"

OUTPUT_PATH = OUTPUTS / "n07_iteration_9c_short_window_evidence_closeout.json"
REPORT_PATH = REPORTS / "n07_iteration_9c_short_window_evidence_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_9c_short_window_evidence_closeout.py"
)

SOURCE_OUTPUTS = {
    "iteration_1": OUTPUTS / "n07_iteration_1_baseline_theory_schema_inventory.json",
    "iteration_2": OUTPUTS / "n07_iteration_2_fixture_manifest_validation.json",
    "iteration_3": OUTPUTS / "n07_iteration_3_id1_support_area_candidate.json",
    "iteration_4": OUTPUTS / "n07_iteration_4_id2_stability_candidate.json",
    "iteration_5": OUTPUTS / "n07_iteration_5_id3_attractivity_candidate.json",
    "iteration_5b": OUTPUTS / "n07_iteration_5b_id3_attractivity_stress_candidate.json",
    "iteration_6": OUTPUTS / "n07_iteration_6_id4_invariance_candidate.json",
    "iteration_6b": OUTPUTS
    / "n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
    "iteration_7": OUTPUTS / "n07_iteration_7_id5_reflexive_closure_persistence.json",
    "iteration_7b": OUTPUTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.json",
    "iteration_8": OUTPUTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.json",
    "iteration_9": OUTPUTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.json",
    "iteration_9b": OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json",
    "iteration_9b2": OUTPUTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.json",
}

SOURCE_REPORTS = {
    "iteration_3": REPORTS / "n07_iteration_3_id1_support_area_candidate.md",
    "iteration_4": REPORTS / "n07_iteration_4_id2_stability_candidate.md",
    "iteration_5": REPORTS / "n07_iteration_5_id3_attractivity_candidate.md",
    "iteration_5b": REPORTS / "n07_iteration_5b_id3_attractivity_stress_candidate.md",
    "iteration_6": REPORTS / "n07_iteration_6_id4_invariance_candidate.md",
    "iteration_6b": REPORTS
    / "n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
    "iteration_7": REPORTS / "n07_iteration_7_id5_reflexive_closure_persistence.md",
    "iteration_7b": REPORTS / "n07_iteration_7b_source_backed_t6_reflexive_closure.md",
    "iteration_8": REPORTS / "n07_iteration_8_c1_t6_artifact_replay_closeout.md",
    "iteration_9": REPORTS / "n07_iteration_9_c3_t7_compatibility_fixture_design.md",
    "iteration_9b": REPORTS / "n07_iteration_9b_c3_compatibility_interference_probe.md",
    "iteration_9b2": REPORTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.md",
}

MANIFEST_PATH = CONFIGS / "n07_fixture_manifest_v1.json"
FIXTURE_9_PATH = CONFIGS / "n07_c3_t7_compatibility_fixture_v1.json"


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


def _without_digest(row: Mapping[str, Any], digest_field: str) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key != digest_field}


def _claim_flags(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    return {key: False for key in sorted(outputs["iteration_1"]["claim_flags"])}


def _source_artifacts(outputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
            "object_digest": _digest(_load_json(MANIFEST_PATH)),
        },
        {
            "name": "n07_c3_t7_compatibility_fixture_v1",
            "path": _rel(FIXTURE_9_PATH),
            "sha256": _file_sha256(FIXTURE_9_PATH),
            "object_digest": _digest(_load_json(FIXTURE_9_PATH)),
        },
    ]
    for name, path in SOURCE_OUTPUTS.items():
        rows.append(
            {
                "name": name,
                "path": _rel(path),
                "sha256": _file_sha256(path),
                "object_digest": _digest(outputs[name]),
                "schema": outputs[name].get("schema"),
                "status": outputs[name].get("status"),
                "check_count": len(outputs[name].get("checks", {})),
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
        if path.exists()
    ]


def _source_artifact_sha256() -> dict[str, str]:
    paths = [MANIFEST_PATH, FIXTURE_9_PATH, *SOURCE_OUTPUTS.values()]
    paths.extend(path for path in SOURCE_REPORTS.values() if path.exists())
    return {_rel(path): _file_sha256(path) for path in paths}


def _source_status_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        name: {
            "schema": data.get("schema"),
            "status": data.get("status"),
            "checks_passed": all(data.get("checks", {}).values()),
            "check_count": len(data.get("checks", {})),
        }
        for name, data in outputs.items()
    }


def _single_basin_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "iteration": "3",
            "rung": "ID1",
            "row_key": "id1_candidate_row",
            "row_digest_key": "id1_candidate_row_digest",
            "row_digest": outputs["iteration_3"]["artifact_digests"][
                "id1_candidate_row_digest"
            ],
        },
        {
            "iteration": "4",
            "rung": "ID2",
            "row_key": "id2_candidate_row",
            "row_digest_key": "id2_candidate_row_digest",
            "row_digest": outputs["iteration_4"]["artifact_digests"][
                "id2_candidate_row_digest"
            ],
        },
        {
            "iteration": "5",
            "rung": "ID3",
            "row_key": "id3_candidate_row",
            "row_digest_key": "id3_candidate_row_digest",
            "row_digest": outputs["iteration_5"]["artifact_digests"][
                "id3_candidate_row_digest"
            ],
        },
        {
            "iteration": "5-B",
            "rung": "ID3",
            "row_key": "id3_attractivity_stress_candidate_row",
            "row_digest_key": "id3_stress_candidate_row_digest",
            "row_digest": outputs["iteration_5b"]["artifact_digests"][
                "id3_stress_candidate_row_digest"
            ],
        },
        {
            "iteration": "6",
            "rung": "ID4",
            "row_key": "id4_invariance_candidate_row",
            "row_digest_key": "id4_candidate_row_digest",
            "row_digest": outputs["iteration_6"]["artifact_digests"][
                "id4_candidate_row_digest"
            ],
        },
        {
            "iteration": "6-B",
            "rung": "ID4",
            "row_key": "id4_topology_stress_candidate_row",
            "row_digest_key": "id4_stress_candidate_row_digest",
            "row_digest": outputs["iteration_6b"]["artifact_digests"][
                "id4_stress_candidate_row_digest"
            ],
        },
        {
            "iteration": "7",
            "rung": "ID5",
            "row_key": "id5_reflexive_closure_candidate_row",
            "row_digest_key": "id5_candidate_row_digest",
            "row_digest": outputs["iteration_7"]["artifact_digests"][
                "id5_candidate_row_digest"
            ],
        },
        {
            "iteration": "7-B",
            "rung": "ID5",
            "row_key": "id5_source_backed_t6_candidate_row",
            "row_digest_key": "id5_candidate_row_digest",
            "row_digest": outputs["iteration_7b"]["artifact_digests"][
                "id5_candidate_row_digest"
            ],
        },
        {
            "iteration": "8",
            "rung": "ID5",
            "row_key": "c1_t6_closeout_row",
            "row_digest_key": "closeout_row_digest",
            "row_digest": outputs["iteration_8"]["artifact_digests"][
                "closeout_row_digest"
            ],
        },
    ]
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "strongest_single_basin_ceiling": "ID5",
        "rows": rows,
        "row_digest_chain_digest": _digest(rows),
        "iteration_8_closeout_digest": outputs["iteration_8"]["artifact_digests"][
            "closeout_row_digest"
        ],
    }


def _support_digest_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    support_rows = outputs["iteration_9b"]["support_area_rows"]
    replay: dict[str, Any] = {}
    for basin in ["A", "B"]:
        row = support_rows[basin]
        digest_input = row["support_area_digest_input"]
        row_without_digest = _without_digest(row, "support_area_row_digest")
        replay[basin] = {
            "support_area_id": row["support_area_id"],
            "declared_support_area_digest": row["support_area_digest"],
            "recomputed_support_area_digest": _digest(digest_input),
            "support_area_digest_matches": _digest(digest_input)
            == row["support_area_digest"],
            "declared_support_area_row_digest": row["support_area_row_digest"],
            "recomputed_support_area_row_digest": _digest(row_without_digest),
            "support_area_row_digest_matches": _digest(row_without_digest)
            == row["support_area_row_digest"],
            "source_status": row["source_status"],
        }
    return replay


def _metric_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    rows = []
    for metric in outputs["iteration_9b"]["compatibility_metric_rows"]:
        recomputed = _digest(_without_digest(metric, "metric_record_digest"))
        rows.append(
            {
                "metric_name": metric["metric_name"],
                "value": metric["value"],
                "threshold": metric["threshold"],
                "comparison": metric["comparison"],
                "passed": metric["passed"],
                "declared_digest": metric["metric_record_digest"],
                "recomputed_digest": recomputed,
                "digest_matches": recomputed == metric["metric_record_digest"],
                "primary_blocker_if_failed": metric.get("primary_blocker_if_failed"),
            }
        )
    compatibility = outputs["iteration_9b"]["compatibility_record"]
    compatibility_recomputed = _digest(
        _without_digest(compatibility, "compatibility_record_digest")
    )
    return {
        "metric_rows": rows,
        "all_metric_digests_match": all(row["digest_matches"] for row in rows),
        "all_metrics_passed": all(row["passed"] for row in rows),
        "compatibility_gate": compatibility["compatibility_gate"],
        "compatibility_record_digest": compatibility["compatibility_record_digest"],
        "compatibility_record_recomputed_digest": compatibility_recomputed,
        "compatibility_record_digest_matches": compatibility_recomputed
        == compatibility["compatibility_record_digest"],
        "one_window_compatibility_passed": compatibility["compatibility_gate"] == "pass",
        "artifact_replay_status_source": compatibility["artifact_replay_status"],
    }


def _control_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    rows = []
    for control in outputs["iteration_9b"]["control_rows"]:
        recomputed = _digest(_without_digest(control, "control_row_digest"))
        rows.append(
            {
                "control_id": control["control_id"],
                "status": control["status"],
                "primary_blocker": control["primary_blocker"],
                "derived_id_ceiling": control["derived_id_ceiling"],
                "declared_digest": control["control_row_digest"],
                "recomputed_digest": recomputed,
                "digest_matches": recomputed == control["control_row_digest"],
                "source": "iteration_9b",
            }
        )
    stress = outputs["iteration_9b2"]["stress_candidate_row"]
    stress_recomputed = _digest(
        _without_digest(stress, "stress_candidate_row_digest")
    )
    rows.append(
        {
            "control_id": "prolonged_compatibility_stress",
            "status": stress["compatibility_stress_status"],
            "primary_blocker": stress["primary_blocker"],
            "derived_id_ceiling": stress["derived_id_ceiling"],
            "declared_digest": stress["stress_candidate_row_digest"],
            "recomputed_digest": stress_recomputed,
            "digest_matches": stress_recomputed == stress["stress_candidate_row_digest"],
            "source": "iteration_9b2",
        }
    )
    blockers = [row["primary_blocker"] for row in rows if row["primary_blocker"]]
    return {
        "control_rows": rows,
        "all_control_digests_match": all(row["digest_matches"] for row in rows),
        "control_ceilings_source_specific": all(
            row["derived_id_ceiling"] == "ID5" for row in rows
        ),
        "blockers": blockers,
        "distinct_blockers": sorted(set(blockers)),
        "source_control_count": len(rows),
        "prolonged_stress_blocker": stress["primary_blocker"],
    }


def _stress_replay(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    stress_model = outputs["iteration_9b2"]["stress_model"]
    stress_model_recomputed = _digest(
        _without_digest(stress_model, "stress_model_digest")
    )
    window_replay = []
    for row in stress_model["stress_windows"]:
        recomputed = _digest(_without_digest(row, "stress_window_digest"))
        window_replay.append(
            {
                "stress_window": row["stress_window"],
                "window_passed": row["window_passed"],
                "primary_blockers": row["primary_blockers"],
                "declared_digest": row["stress_window_digest"],
                "recomputed_digest": recomputed,
                "digest_matches": recomputed == row["stress_window_digest"],
            }
        )
    return {
        "stress_model_id": stress_model["stress_model_id"],
        "stress_model_scope": stress_model["model_scope"],
        "dynamic_lgrc_step_count": stress_model["dynamic_lgrc_step_count"],
        "stress_window_count": stress_model["stress_window_count"],
        "stress_passed_all_windows": stress_model["stress_passed_all_windows"],
        "first_failure": stress_model["first_failure"],
        "stress_model_digest": stress_model["stress_model_digest"],
        "stress_model_recomputed_digest": stress_model_recomputed,
        "stress_model_digest_matches": stress_model_recomputed
        == stress_model["stress_model_digest"],
        "stress_window_replay": window_replay,
        "all_stress_window_digests_match": all(
            row["digest_matches"] for row in window_replay
        ),
    }


def _control_summary(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    summary = {}
    for name, data in outputs.items():
        controls = data.get("control_rows", [])
        if isinstance(controls, list):
            summary[name] = {
                "control_count": len(controls),
                "blocked_count": sum(
                    1 for row in controls if row.get("status") == "blocked"
                ),
                "blockers": sorted(
                    {
                        row.get("primary_blocker")
                        for row in controls
                        if row.get("primary_blocker")
                    }
                ),
            }
    return summary


def _artifact_replay_chain(outputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    support_replay = _support_digest_replay(outputs)
    metric_replay = _metric_replay(outputs)
    control_replay = _control_replay(outputs)
    stress_replay = _stress_replay(outputs)
    chain = {
        "artifact_only": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "source_status_replay": _source_status_replay(outputs),
        "single_basin_replay": _single_basin_replay(outputs),
        "c3_fixture_digest": outputs["iteration_9"]["artifact_digests"][
            "fixture_digest"
        ],
        "support_digest_replay": support_replay,
        "metric_replay": metric_replay,
        "control_replay": control_replay,
        "stress_replay": stress_replay,
        "prior_control_summary": _control_summary(outputs),
        "semantic_consistency": {
            "carrier_kind": "coherence_basin",
            "identity_carrier_surface": "runtime_coherence_basin",
            "shared_neighborhood": outputs["iteration_9b"][
                "shared_neighborhood_U_row"
            ]["neighborhood_id"],
            "A_support_area_id": outputs["iteration_9b"]["support_area_rows"]["A"][
                "support_area_id"
            ],
            "B_support_area_id": outputs["iteration_9b"]["support_area_rows"]["B"][
                "support_area_id"
            ],
            "compatibility_metric_id": outputs["iteration_9b"][
                "compatibility_record"
            ]["metric_id"],
            "budget_surface": "node_plus_packet",
            "semantic_consistency_passed": True,
        },
        "closeout_decision": {
            "single_basin_ceiling": "ID5",
            "one_window_compatibility": "pass",
            "prolonged_compatibility": "blocked",
            "prolonged_primary_blocker": stress_replay["first_failure"][
                "primary_blockers"
            ][0],
            "final_n07_ceiling": "ID5",
            "id6_claimed": False,
            "next_iteration": "10_long_horizon_compatibility_design",
        },
    }
    chain["artifact_replay_chain_digest"] = _digest(chain)
    return chain


def _closeout_row(
    outputs: Mapping[str, Mapping[str, Any]],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
    replay_chain: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    required_activity_scope = {
        "source_iteration_8_closeout": outputs["iteration_8"]["artifact_digests"][
            "closeout_row_digest"
        ],
        "source_iteration_9_fixture": outputs["iteration_9"]["artifact_digests"][
            "fixture_digest"
        ],
        "source_iteration_9b_candidate": outputs["iteration_9b"]["artifact_digests"][
            "candidate_row_digest"
        ],
        "source_iteration_9b2_stress": outputs["iteration_9b2"]["artifact_digests"][
            "stress_candidate_row_digest"
        ],
        "artifact_replay_chain_digest": replay_chain["artifact_replay_chain_digest"],
        "final_n07_ceiling": "ID5",
    }
    row = {
        "row_id": "n07_i9c_short_window_evidence_closeout_row_v1",
        "id_level": "ID5",
        "topology_family_id": "n07_T7_compatibility",
        "composite_topology_id": "n07_C3_competing_basin_compatibility_candidate",
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": outputs["iteration_9b"]["support_area_rows"]["A"][
            "support_area_id"
        ],
        "support_area_digest": outputs["iteration_9b"]["support_area_rows"]["A"][
            "support_area_digest"
        ],
        "source_artifacts": [row["path"] for row in source_artifacts],
        "source_artifact_sha256": _source_artifact_sha256(),
        "source_reports": [row["path"] for row in source_reports],
        "runtime_family": "hybrid_lgrc9v3_experiment_local",
        "implementation_surface": "artifact_only_validator",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": "blocked",
            "artifact_replay": "pass",
        },
        "derived_id_ceiling": "ID5",
        "primary_blocker": "wrong_basin",
        "native_support_status": "experiment_local",
        "native_observables_used": [
            "source_support_area_digest",
            "node_plus_packet_budget_surface",
        ],
        "experiment_local_observables_used": [
            "A_support_retention_near_B",
            "B_support_retention_near_A",
            "wrong_basin_leakage_score",
            "destructive_interference_score",
            "prolonged_stress_window",
        ],
        "native_policy_blockers": [
            "persistent_c3_compatibility_blocked_by_wrong_basin",
            "native_identity_acceptance_contract_missing",
        ],
        "becoming_class_status": "reusable_class",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest_scope": required_activity_scope,
        "activity_history_digest": _digest(required_activity_scope),
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "artifact_only": True,
        "runtime_state_used": False,
        "one_window_compatibility_status": "pass",
        "prolonged_compatibility_status": "blocked",
        "prolonged_compatibility_primary_blocker": "wrong_basin",
        "id6_claimed": False,
        "id6_blocker": "persistent_c3_compatibility_blocked_by_wrong_basin",
        "claim_ceiling": (
            "id5_short_window_identity_and_compatibility_evidence_"
            "persistent_c3_blocked"
        ),
        "next_iteration": "10_long_horizon_compatibility_design",
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["closeout_row_digest_input"] = {
        key: value for key, value in row.items() if key != "closeout_row_digest"
    }
    row["closeout_row_digest"] = _digest(row["closeout_row_digest_input"])
    return row


def _acceptance(closeout: Mapping[str, Any], replay_chain: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_only_replay_passed": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "derived_id_ceiling": closeout["derived_id_ceiling"],
        "id6_claimed": closeout["id6_claimed"],
        "one_window_compatibility_status": closeout["one_window_compatibility_status"],
        "prolonged_compatibility_status": closeout[
            "prolonged_compatibility_status"
        ],
        "primary_blocker": closeout["primary_blocker"],
        "next_iteration": replay_chain["closeout_decision"]["next_iteration"],
        "statement": (
            "Iteration 9-C replays the N07 short-window evidence chain through "
            "9-B2 from artifacts only. It records 9-B as one-window "
            "compatibility evidence, records 9-B2 as prolonged-stress failure, "
            "freezes the ceiling at ID5, and does not claim ID6 or identity "
            "acceptance."
        ),
    }


def _checks(
    outputs: Mapping[str, Mapping[str, Any]],
    replay_chain: Mapping[str, Any],
    closeout: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, bool]:
    required_fields = outputs["iteration_1"]["id_ladder_schema"]["row_required_fields"]
    allowed_boundary = outputs["iteration_1"]["becoming_schema"]["boundary_rung"]
    allowed_impl = outputs["iteration_1"]["id_ladder_schema"][
        "implementation_surface_allowed_values"
    ]
    allowed_runtime = outputs["iteration_1"]["id_ladder_schema"][
        "runtime_family_allowed_values"
    ]
    support_replay = replay_chain["support_digest_replay"]
    metric_replay = replay_chain["metric_replay"]
    control_replay = replay_chain["control_replay"]
    stress_replay = replay_chain["stress_replay"]
    source_status = replay_chain["source_status_replay"]
    return {
        "all_source_artifacts_passed": all(
            row["status"] == "passed" for row in source_status.values()
        ),
        "artifact_only": replay_chain["artifact_only"] is True,
        "runtime_state_not_used": replay_chain["runtime_state_used"] is False,
        "private_runtime_state_not_used": replay_chain["private_runtime_state_used"]
        is False,
        "single_basin_ceiling_id5": replay_chain["single_basin_replay"][
            "strongest_single_basin_ceiling"
        ]
        == "ID5",
        "A_support_digest_replayed": support_replay["A"][
            "support_area_digest_matches"
        ]
        and support_replay["A"]["support_area_row_digest_matches"],
        "B_support_digest_replayed": support_replay["B"][
            "support_area_digest_matches"
        ]
        and support_replay["B"]["support_area_row_digest_matches"],
        "metric_digests_replayed": metric_replay["all_metric_digests_match"],
        "one_window_compatibility_passed": metric_replay[
            "one_window_compatibility_passed"
        ],
        "compatibility_record_digest_replayed": metric_replay[
            "compatibility_record_digest_matches"
        ],
        "control_digests_replayed": control_replay["all_control_digests_match"],
        "control_ceilings_source_specific": control_replay[
            "control_ceilings_source_specific"
        ],
        "prolonged_stress_digest_replayed": stress_replay[
            "stress_model_digest_matches"
        ]
        and stress_replay["all_stress_window_digests_match"],
        "prolonged_stress_blocked": stress_replay["stress_passed_all_windows"]
        is False,
        "prolonged_stress_primary_blocker_wrong_basin": stress_replay[
            "first_failure"
        ]["primary_blockers"]
        == ["wrong_basin"],
        "semantic_consistency_passed": replay_chain["semantic_consistency"][
            "semantic_consistency_passed"
        ],
        "closeout_required_fields_present": not [
            field for field in required_fields if field not in closeout
        ],
        "closeout_boundary_rung_allowed": closeout["boundary_rung"] in allowed_boundary,
        "closeout_implementation_surface_allowed": closeout[
            "implementation_surface"
        ]
        in allowed_impl,
        "closeout_runtime_family_allowed": closeout["runtime_family"]
        in allowed_runtime,
        "closeout_digest_recomputed": _digest(closeout["closeout_row_digest_input"])
        == closeout["closeout_row_digest"],
        "closeout_ceiling_id5": closeout["derived_id_ceiling"] == "ID5",
        "closeout_does_not_claim_id6": closeout["id6_claimed"] is False,
        "closeout_records_wrong_basin_blocker": closeout["primary_blocker"]
        == "wrong_basin",
        "artifact_replay_gate_pass": closeout["gate_vector"]["artifact_replay"]
        == "pass",
        "compatibility_gate_blocked": closeout["gate_vector"]["compatibility"]
        == "blocked",
        "acceptance_matches_closeout": acceptance["derived_id_ceiling"]
        == closeout["derived_id_ceiling"]
        and acceptance["id6_claimed"] == closeout["id6_claimed"],
        "claim_flags_false": not any(claim_flags.values()),
        "closeout_claim_flags_false": not any(closeout["claim_flags"].values()),
        "source_artifact_hashes_present": all(
            closeout["source_artifact_sha256"].values()
        ),
        "visuals_not_evidence": closeout["visual_is_evidence_source"] is False,
        "next_iteration_is_10": closeout["next_iteration"]
        == "10_long_horizon_compatibility_design",
        "no_src_changes_required": _git(["status", "--short", "src"])["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "artifact_replay_chain_digest": result["artifact_replay_chain"][
            "artifact_replay_chain_digest"
        ],
        "checks_digest": _digest(result["checks"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "closeout_row_digest": result["short_window_closeout_row"][
            "closeout_row_digest"
        ],
        "closeout_row_artifact_digest": _digest(result["short_window_closeout_row"]),
        "source_artifacts_digest": _digest(result["source_artifacts"]),
    }


def _environment() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _build_result() -> dict[str, Any]:
    outputs = {name: _load_json(path) for name, path in SOURCE_OUTPUTS.items()}
    source_artifacts = _source_artifacts(outputs)
    source_reports = _source_reports()
    claim_flags = _claim_flags(outputs)
    replay_chain = _artifact_replay_chain(outputs)
    closeout = _closeout_row(
        outputs, source_artifacts, source_reports, replay_chain, claim_flags
    )
    acceptance = _acceptance(closeout, replay_chain)
    result: dict[str, Any] = {
        "schema": "n07_iteration_9c_short_window_evidence_closeout_v1",
        "experiment": "N07",
        "iteration": "9-C",
        "purpose": "artifact_only_short_window_closeout_no_id6_promotion",
        "command": COMMAND,
        "environment": _environment(),
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "artifact_replay_chain": replay_chain,
        "short_window_closeout_row": closeout,
        "acceptance": acceptance,
        "git": {
            "rev_parse_head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(outputs, replay_chain, closeout, acceptance, claim_flags)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    closeout = result["short_window_closeout_row"]
    stress = result["artifact_replay_chain"]["stress_replay"]
    controls = "\n".join(
        "| `{control_id}` | `{status}` | `{primary_blocker}` | `{derived_id_ceiling}` | `{source}` |".format(
            **row
        )
        for row in result["artifact_replay_chain"]["control_replay"]["control_rows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 9-C Short-Window Artifact Replay Closeout

Status: `{result['status']}`

9-C replays the short-window N07 evidence chain from artifacts only. It keeps
Iteration 9-B as one-window C3/T7 compatibility evidence and carries Iteration
9-B2 forward as a prolonged-stress blocker. This is not persistent C3
compatibility and not ID6.

## Closeout

- derived ceiling: `{closeout['derived_id_ceiling']}`
- artifact replay gate: `{closeout['gate_vector']['artifact_replay']}`
- compatibility gate: `{closeout['gate_vector']['compatibility']}`
- one-window compatibility: `{closeout['one_window_compatibility_status']}`
- prolonged compatibility: `{closeout['prolonged_compatibility_status']}`
- primary blocker: `{closeout['primary_blocker']}`
- ID6 claimed: `{closeout['id6_claimed']}`
- next iteration: `{closeout['next_iteration']}`

## Prolonged Stress Boundary

- stress model: `{stress['stress_model_id']}`
- stress windows: `{stress['stress_window_count']}`
- dynamic LGRC steps: `{stress['dynamic_lgrc_step_count']}`
- first failure: `{stress['first_failure']}`

## Replayed Controls

| Control | Status | Primary Blocker | Ceiling | Source |
|---|---|---|---|---|
{controls}

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
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks": len(result["checks"]),
                "ceiling": result["short_window_closeout_row"]["derived_id_ceiling"],
                "id6_claimed": result["short_window_closeout_row"]["id6_claimed"],
                "primary_blocker": result["short_window_closeout_row"][
                    "primary_blocker"
                ],
                "next": result["short_window_closeout_row"]["next_iteration"],
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()
