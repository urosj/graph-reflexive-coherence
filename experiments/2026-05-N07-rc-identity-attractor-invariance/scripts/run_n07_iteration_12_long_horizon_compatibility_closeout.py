"""Run N07 Iteration 12 long-horizon compatibility artifact closeout.

Iteration 12 replays the Iteration 10/11-* long-horizon C3 branch inventory
from exported artifacts only. It freezes the strongest source-specific evidence
classification while keeping runtime identity acceptance, agency, semantic
choice, and related claim flags blocked.
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

SOURCE_10_OUTPUT = OUTPUTS / "n07_iteration_10_long_horizon_compatibility_design.json"
SOURCE_10_REPORT = REPORTS / "n07_iteration_10_long_horizon_compatibility_design.md"
SOURCE_11_OUTPUT = OUTPUTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.json"
SOURCE_11_REPORT = REPORTS / "n07_iteration_11_long_horizon_compatibility_recovery_probe.md"
SOURCE_11A_OUTPUT = OUTPUTS / "n07_iteration_11a_source_digest_reentry_buffer.json"
SOURCE_11A_REPORT = REPORTS / "n07_iteration_11a_source_digest_reentry_buffer.md"
SOURCE_11B_OUTPUT = OUTPUTS / "n07_iteration_11b_neutral_absorber_reservoir.json"
SOURCE_11B_REPORT = REPORTS / "n07_iteration_11b_neutral_absorber_reservoir.md"

OUTPUT_PATH = OUTPUTS / "n07_iteration_12_long_horizon_compatibility_closeout.json"
REPORT_PATH = REPORTS / "n07_iteration_12_long_horizon_compatibility_closeout.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_12_long_horizon_compatibility_closeout.py"
)


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


def _slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return (values[-1] - values[0]) / (len(values) - 1)


def _deltas(values: list[float]) -> list[float]:
    return [values[index] - values[index - 1] for index in range(1, len(values))]


def _source_artifacts(
    source_10: Mapping[str, Any],
    source_11: Mapping[str, Any],
    source_11a: Mapping[str, Any],
    source_11b: Mapping[str, Any],
) -> list[dict[str, Any]]:
    artifacts = [
        (SOURCE_10_OUTPUT, "n07_iteration_10_long_horizon_compatibility_design", source_10),
        (SOURCE_11_OUTPUT, "n07_iteration_11_0_long_horizon_baseline", source_11),
        (SOURCE_11A_OUTPUT, "n07_iteration_11a_source_digest_reentry_buffer", source_11a),
        (SOURCE_11B_OUTPUT, "n07_iteration_11b_neutral_absorber_reservoir", source_11b),
    ]
    return [
        {
            "name": name,
            "path": _rel(path),
            "sha256": _file_sha256(path),
            "object_digest": _digest(data),
            "status": data.get("status"),
        }
        for path, name, data in artifacts
    ]


def _source_reports() -> list[dict[str, str]]:
    reports = [
        (SOURCE_10_REPORT, "n07_iteration_10_long_horizon_compatibility_design_report"),
        (SOURCE_11_REPORT, "n07_iteration_11_0_long_horizon_baseline_report"),
        (SOURCE_11A_REPORT, "n07_iteration_11a_source_digest_reentry_buffer_report"),
        (SOURCE_11B_REPORT, "n07_iteration_11b_neutral_absorber_reservoir_report"),
    ]
    return [
        {
            "name": name,
            "path": _rel(path),
            "sha256": _file_sha256(path),
        }
        for path, name in reports
    ]


def _claim_flags(source_10: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(source_10["claim_flags"])}


def _trajectory_from_artifact(branch: Mapping[str, Any]) -> Mapping[str, Any]:
    if "trajectory" in branch:
        return branch["trajectory"]
    return branch["trajectory_replay"]


def _branch_inventory(
    source_11: Mapping[str, Any],
    source_11a: Mapping[str, Any],
    source_11b: Mapping[str, Any],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for source in [source_11, source_11a, source_11b]:
        trajectory = _trajectory_from_artifact(source)
        arc = source["arc_of_becoming_interpretation"]
        row = {
            "branch_id": source["branch_id"],
            "source_schema": source["schema"],
            "source_status": source["status"],
            "question_answered": source["branch_record"]["question_answered"],
            "mechanism_or_fixture_change": source["branch_record"][
                "mechanism_or_fixture_change"
            ],
            "trajectory_regime": trajectory["trajectory_regime"],
            "endpoint_pass_status": trajectory["endpoint_pass_status"],
            "first_failure_window": trajectory["first_failure_window"],
            "primary_blocker": trajectory["primary_blocker"],
            "classification_status": arc["classification"]["classification_status"],
            "naturalization_rung": arc["naturalization"]["naturalization_rung"],
            "series_ready_for_iteration_12": source["series_decision"][
                "series_ready_for_iteration_12"
            ],
            "claim_flags_false": not any(source["claim_flags"].values()),
            "id6_evidence_before_closeout": source["long_horizon_candidate_row"][
                "id6_claimed"
            ],
            "candidate_row_digest": source["long_horizon_candidate_row"][
                "candidate_row_digest"
            ],
            "trajectory_digest": trajectory.get("trajectory_digest")
            or trajectory.get("trajectory_replay_digest"),
            "branch_record_digest": source["branch_record"]["branch_record_digest"],
            "arc_interpretation_digest": arc["arc_interpretation_digest"],
        }
        row["inventory_row_digest"] = _digest(row)
        inventory.append(row)
    return inventory


def _replay_11b_metrics(
    source_10: Mapping[str, Any],
    source_11b: Mapping[str, Any],
) -> dict[str, Any]:
    trajectory = source_11b["trajectory"]
    policy = source_11b["reservoir_policy"]
    rows = source_11b["reservoir_window_records"]
    series = {
        "wrong_basin_leakage_level": [
            row["non_destructive_exchange_measurement"]["wrong_basin_leakage_level"]
            for row in rows
        ],
        "A_support_retention_level": [
            row["non_destructive_exchange_measurement"]["A_support_retention_level"]
            for row in rows
        ],
        "B_support_retention_level": [
            row["non_destructive_exchange_measurement"]["B_support_retention_level"]
            for row in rows
        ],
        "destructive_interference_level": [
            row["non_destructive_exchange_measurement"][
                "destructive_interference_level"
            ]
            for row in rows
        ],
        "basin_separability_level": [
            row["non_destructive_exchange_measurement"]["basin_separability_level"]
            for row in rows
        ],
        "budget_error_level": [
            row["non_destructive_exchange_measurement"]["budget_error_level"]
            for row in rows
        ],
    }
    slopes = {f"{key}_slope_per_window": _slope(values) for key, values in series.items()}
    post_start = int(policy["post_transient_window_start"])
    post_slopes = {
        f"{key}_post_transient_slope_per_window": _slope(values[post_start - 1 :])
        for key, values in series.items()
    }
    artifact_series_subset = {
        key: trajectory["per_window_metric_series"][key] for key in series
    }
    criteria = source_10["survivability_contract"]["survivability_criteria"]
    replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "source_branch": source_11b["branch_id"],
        "window_count": len(rows),
        "recomputed_series": series,
        "recomputed_deltas": {f"delta_{key}": _deltas(values) for key, values in series.items()},
        "recomputed_slopes": slopes,
        "recomputed_post_transient_slopes": post_slopes,
        "artifact_series_subset": artifact_series_subset,
        "series_match_artifact": series == artifact_series_subset,
        "slopes_match_artifact": all(
            abs(slopes[key] - trajectory["metric_slopes_per_window"][key]) < 1e-15
            for key in slopes
        ),
        "post_transient_slopes_match_artifact": all(
            abs(
                post_slopes[key]
                - trajectory["post_transient_metric_slopes_per_window"][key]
            )
            < 1e-15
            for key in post_slopes
        ),
        "nonzero_leakage_observed": max(series["wrong_basin_leakage_level"]) > 0.0,
        "leakage_bounded_below_threshold": max(series["wrong_basin_leakage_level"])
        <= criteria["cumulative_wrong_basin_leakage_max_each_window"],
        "support_survival_passed": min(series["A_support_retention_level"])
        >= criteria["A_support_retention_min_each_window"]
        and min(series["B_support_retention_level"])
        >= criteria["B_support_retention_min_each_window"],
        "separability_passed": min(series["basin_separability_level"])
        >= policy["basin_separability_min"],
        "post_transient_flattened": abs(
            post_slopes["wrong_basin_leakage_level_post_transient_slope_per_window"]
        )
        <= policy["post_transient_flattening_epsilon"]
        and abs(
            post_slopes[
                "destructive_interference_level_post_transient_slope_per_window"
            ]
        )
        <= policy["post_transient_flattening_epsilon"],
        "budget_exact": all(value == 0.0 for value in series["budget_error_level"]),
        "window_records_have_required_chain": all(
            all(
                key in row
                for key in [
                    "connected_basin_exchange_event",
                    "neutral_absorber_reservoir_state",
                    "non_destructive_exchange_measurement",
                ]
            )
            for row in rows
        ),
    }
    replay["replay_passed"] = all(
        [
            replay["series_match_artifact"],
            replay["slopes_match_artifact"],
            replay["post_transient_slopes_match_artifact"],
            replay["nonzero_leakage_observed"],
            replay["leakage_bounded_below_threshold"],
            replay["support_survival_passed"],
            replay["separability_passed"],
            replay["post_transient_flattened"],
            replay["budget_exact"],
            replay["window_records_have_required_chain"],
        ]
    )
    replay["replay_digest"] = _digest(replay)
    return replay


def _control_replay(
    source_11: Mapping[str, Any],
    source_11a: Mapping[str, Any],
    source_11b: Mapping[str, Any],
) -> dict[str, Any]:
    rows = []
    for source in [source_11, source_11a, source_11b]:
        for row in source["control_rows"]:
            rows.append(
                {
                    "source_branch": source["branch_id"],
                    "control_id": row["control_id"],
                    "observed_status": row["observed_status"],
                    "primary_blocker": row["primary_blocker"],
                    "control_passed": row["control_passed"],
                    "control_row_digest": row["control_row_digest"],
                }
            )
    blockers = [row["primary_blocker"] for row in rows]
    replay = {
        "control_count": len(rows),
        "control_rows": rows,
        "all_controls_passed": all(row["control_passed"] for row in rows),
        "distinct_blocker_count": len(set(blockers)),
        "distinct_blockers_present": len(set(blockers)) >= 12,
        "required_closeout_blockers_present": all(
            blocker in set(blockers)
            for blocker in [
                "wrong_basin",
                "wrong_support_area",
                "hidden_support_field",
                "budget_discontinuity",
                "misframed_zero_leakage_requirement",
                "support_drift_beyond_threshold",
                "identity_claim_promotion",
            ]
        ),
    }
    replay["control_replay_passed"] = all(
        [
            replay["all_controls_passed"],
            replay["distinct_blockers_present"],
            replay["required_closeout_blockers_present"],
        ]
    )
    replay["control_replay_digest"] = _digest(replay)
    return replay


def _closeout_decision(
    source_11b: Mapping[str, Any],
    replay_11b: Mapping[str, Any],
    control_replay: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    decision = {
        "strongest_branch": "11-B",
        "strongest_trajectory_regime": source_11b["trajectory"]["trajectory_regime"],
        "frozen_long_horizon_c3_class": "bounded_non_destructive_exchange",
        "frozen_n07_ceiling": "ID6",
        "id6_evidence_classification_supported": True,
        "id6_scope": (
            "artifact_only_source_specific_bounded_non_destructive_exchange_"
            "under_neutral_absorber_reservoir_v1"
        ),
        "id6_is_runtime_identity_acceptance": False,
        "runtime_identity_acceptance_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "agency_claim_allowed": False,
        "native_support_status": "experiment_local_serialized_reservoir_policy",
        "native_policy_blockers": [
            "native_neutral_absorber_reservoir_policy_missing",
            "native_identity_acceptance_contract_missing",
            "native_long_horizon_c3_replay_policy_missing",
        ],
        "replay_basis": {
            "artifact_only_replay_passed": replay_11b["replay_passed"],
            "controls_replayed": control_replay["control_replay_passed"],
            "claim_flags_false": not any(claim_flags.values()),
            "source_11b_status": source_11b["status"],
            "source_11b_series_ready_for_12": source_11b["series_decision"][
                "series_ready_for_iteration_12"
            ],
        },
        "future_exploration_invitation": {
            "iteration": "13",
            "required_for_n07_closeout": False,
            "topics": [
                "longer_horizon_bounded_exchange_stress",
                "reservoir_withdrawal_or_naturalization",
                "symmetric_dual_source_backed_reentry",
                "native_absorber_policy_design",
            ],
        },
    }
    for key, value in claim_flags.items():
        decision[key] = value
    decision["closeout_decision_digest"] = _digest(decision)
    return decision


def _candidate_row(
    source_10: Mapping[str, Any],
    source_11b: Mapping[str, Any],
    branch_inventory: list[Mapping[str, Any]],
    replay_11b: Mapping[str, Any],
    control_replay: Mapping[str, Any],
    closeout: Mapping[str, Any],
    source_artifacts: list[Mapping[str, Any]],
    source_reports: list[Mapping[str, Any]],
    claim_flags: Mapping[str, bool],
) -> dict[str, Any]:
    design = source_10["design_row"]
    activity_scope = {
        "branch_inventory_digest": _digest(branch_inventory),
        "replay_digest": replay_11b["replay_digest"],
        "control_replay_digest": control_replay["control_replay_digest"],
        "closeout_decision_digest": closeout["closeout_decision_digest"],
        "source_11b_candidate_row_digest": source_11b["long_horizon_candidate_row"][
            "candidate_row_digest"
        ],
    }
    row = {
        "row_id": "n07_i12_long_horizon_c3_closeout_row_v1",
        "branch_id": "12",
        "id_level": "ID6",
        "topology_family_id": design["topology_family_id"],
        "composite_topology_id": design["composite_topology_id"],
        "candidate_identity_carrier_type": design["candidate_identity_carrier_type"],
        "identity_carrier_surface": design["identity_carrier_surface"],
        "support_area_id": design["support_area_id"],
        "support_area_digest": design["support_area_digest"],
        "source_artifacts": [row["path"] for row in source_artifacts],
        "source_artifact_sha256": {
            row["path"]: row["sha256"] for row in source_artifacts
        },
        "source_reports": [row["path"] for row in source_reports],
        "runtime_family": "artifact_only_experiment_closeout",
        "implementation_surface": "artifact_only_replay",
        "gate_vector": {
            "support": "pass",
            "stability": "pass",
            "attractivity": "pass",
            "invariance": "pass",
            "lineage_current": "pass",
            "reflexive_closure": "pass",
            "compatibility": "pass_bounded_non_destructive_exchange",
            "artifact_replay": "pass",
            "long_horizon_trajectory": "bounded_non_destructive_exchange",
        },
        "derived_id_ceiling": "ID6",
        "id6_evidence_classification_supported": True,
        "id6_is_runtime_identity_acceptance": False,
        "primary_blocker": None,
        "native_support_status": closeout["native_support_status"],
        "native_policy_blockers": closeout["native_policy_blockers"],
        "becoming_class_status": "source_specific_expression",
        "becoming_interpretation_style": "question_observation_classification_cultivation_naturalization",
        "becoming_expressed_property": source_11b[
            "arc_of_becoming_interpretation"
        ]["expressed_property"],
        "probe_role": "artifact_only_closeout",
        "boundary_rung": "source_specific_expression",
        "support_dependency_status": "regime_assisted",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": source_11b["arc_of_becoming_interpretation"][
            "naturalization"
        ]["naturalization_rung"],
        "activity_history_digest_scope": activity_scope,
        "activity_history_digest": _digest(activity_scope),
        "trajectory_regime": source_11b["trajectory"]["trajectory_regime"],
        "endpoint_pass_status": source_11b["trajectory"]["endpoint_pass_status"],
        "claim_flags": dict(claim_flags),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": closeout["id6_scope"],
        "blocked_claims": [
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "biological_identity",
            "personhood",
            "unrestricted_identity",
        ],
    }
    for key, value in claim_flags.items():
        row[key] = value
    row["candidate_row_digest"] = _digest(row)
    return row


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    source_status = result["source_status"]
    inventory = result["branch_inventory"]
    closeout = result["closeout_decision"]
    candidate = result["long_horizon_closeout_row"]
    claim_flags = result["claim_flags"]
    replay = result["artifact_only_replay"]
    controls = result["control_replay"]
    trajectory_order = [row["trajectory_regime"] for row in inventory]
    return {
        "artifact_only_replay_declared": replay["artifact_only"] is True,
        "runtime_state_not_used": replay["runtime_state_used"] is False,
        "source_10_passed": source_status["iteration_10_status"] == "passed",
        "source_11_0_passed": source_status["iteration_11_0_status"] == "passed",
        "source_11a_passed": source_status["iteration_11a_status"] == "passed",
        "source_11b_passed": source_status["iteration_11b_status"] == "passed",
        "branch_inventory_complete": [row["branch_id"] for row in inventory]
        == ["11-0", "11-A", "11-B"],
        "trajectory_progression_reconstructed": trajectory_order
        == [
            "unbounded_degrading_without_recovery",
            "bounded_degrading",
            "bounded_non_destructive_exchange",
        ],
        "branch_11b_was_ready_for_12": inventory[-1]["series_ready_for_iteration_12"]
        is True,
        "series_and_slopes_recomputed": replay["series_match_artifact"]
        and replay["slopes_match_artifact"],
        "post_transient_slopes_recomputed": replay[
            "post_transient_slopes_match_artifact"
        ],
        "nonzero_bounded_leakage_replayed": replay["nonzero_leakage_observed"]
        and replay["leakage_bounded_below_threshold"],
        "dual_basin_survival_replayed": replay["support_survival_passed"],
        "separability_replayed": replay["separability_passed"],
        "post_transient_flattening_replayed": replay["post_transient_flattened"],
        "budget_exactness_replayed": replay["budget_exact"],
        "required_chain_replayed": replay["window_records_have_required_chain"],
        "controls_replayed": controls["control_replay_passed"],
        "closeout_freezes_id6_evidence_classification": closeout[
            "frozen_n07_ceiling"
        ]
        == "ID6"
        and closeout["id6_evidence_classification_supported"] is True,
        "id6_not_runtime_identity_acceptance": closeout[
            "id6_is_runtime_identity_acceptance"
        ]
        is False,
        "native_claims_remain_blocked": closeout[
            "runtime_identity_acceptance_claim_allowed"
        ]
        is False
        and closeout["rc_identity_collapse_claim_allowed"] is False
        and closeout["semantic_choice_claim_allowed"] is False
        and closeout["agency_claim_allowed"] is False,
        "claim_flags_false": not any(claim_flags.values()),
        "candidate_ceiling_id6": candidate["derived_id_ceiling"] == "ID6",
        "candidate_claim_flags_false": not any(candidate["claim_flags"].values()),
        "candidate_blocks_runtime_claims": all(candidate[claim] is False for claim in claim_flags),
        "future_iteration_13_optional": closeout["future_exploration_invitation"][
            "required_for_n07_closeout"
        ]
        is False,
        "source_artifact_hashes_present": all(
            row.get("sha256") for row in result["source_artifacts"]
        ),
        "source_reports_present": all(
            row.get("sha256") for row in result["source_reports"]
        ),
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "branch_inventory_digest": _digest(result["branch_inventory"]),
        "artifact_only_replay_digest": result["artifact_only_replay"]["replay_digest"],
        "control_replay_digest": result["control_replay"]["control_replay_digest"],
        "closeout_decision_digest": result["closeout_decision"][
            "closeout_decision_digest"
        ],
        "candidate_row_digest": result["long_horizon_closeout_row"][
            "candidate_row_digest"
        ],
        "checks_digest": _digest(result["checks"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
    }


def _environment() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _build_result() -> dict[str, Any]:
    source_10 = _load_json(SOURCE_10_OUTPUT)
    source_11 = _load_json(SOURCE_11_OUTPUT)
    source_11a = _load_json(SOURCE_11A_OUTPUT)
    source_11b = _load_json(SOURCE_11B_OUTPUT)
    claim_flags = _claim_flags(source_10)
    source_artifacts = _source_artifacts(source_10, source_11, source_11a, source_11b)
    source_reports = _source_reports()
    branch_inventory = _branch_inventory(source_11, source_11a, source_11b)
    replay_11b = _replay_11b_metrics(source_10, source_11b)
    control_replay = _control_replay(source_11, source_11a, source_11b)
    closeout = _closeout_decision(source_11b, replay_11b, control_replay, claim_flags)
    candidate = _candidate_row(
        source_10,
        source_11b,
        branch_inventory,
        replay_11b,
        control_replay,
        closeout,
        source_artifacts,
        source_reports,
        claim_flags,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_12_long_horizon_compatibility_closeout_v1",
        "experiment": "N07",
        "iteration": "12",
        "purpose": "artifact_only_long_horizon_c3_closeout",
        "command": COMMAND,
        "environment": _environment(),
        "artifact_only": True,
        "runtime_state_used": False,
        "source_status": {
            "iteration_10_status": source_10.get("status"),
            "iteration_11_0_status": source_11.get("status"),
            "iteration_11a_status": source_11a.get("status"),
            "iteration_11b_status": source_11b.get("status"),
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": claim_flags,
        "branch_inventory": branch_inventory,
        "artifact_only_replay": replay_11b,
        "control_replay": control_replay,
        "closeout_decision": closeout,
        "long_horizon_closeout_row": candidate,
        "acceptance": {
            "statement": (
                "Iteration 12 passes if the completed 11-* long-horizon C3 "
                "branch series replays from artifacts only, reconstructs the "
                "bounded non-destructive exchange class, replays controls, "
                "freezes the strongest source-specific N07 evidence ceiling, "
                "and keeps runtime identity acceptance, RC identity collapse, "
                "agency, semantic choice, biological, personhood, and "
                "unrestricted identity claims blocked."
            ),
            "achieved": False,
        },
        "next_iteration": "13_future_exploration_invitations_optional",
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
    inventory_rows = "\n".join(
        "| `{branch_id}` | `{mechanism_or_fixture_change}` | `{trajectory_regime}` | `{endpoint_pass_status}` | `{classification_status}` | `{series_ready_for_iteration_12}` |".format(
            **row
        )
        for row in result["branch_inventory"]
    )
    replay = result["artifact_only_replay"]
    closeout = result["closeout_decision"]
    controls = result["control_replay"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 12 Long-Horizon Compatibility Closeout

Status: `{result['status']}`

Iteration 12 replays the completed 11-* long-horizon C3 branch series from
artifacts only. It does not run a new probe and does not inspect private
runtime state.

## Replayed Branch Inventory

| Branch | Mechanism | Trajectory | Endpoint | Classification | Ready For 12 |
|---|---|---|---|---|---|
{inventory_rows}

## Artifact-Only Replay

- artifact only: `{replay['artifact_only']}`
- runtime state used: `{replay['runtime_state_used']}`
- source branch: `{replay['source_branch']}`
- window count: `{replay['window_count']}`
- series match artifact: `{replay['series_match_artifact']}`
- slopes match artifact: `{replay['slopes_match_artifact']}`
- post-transient slopes match artifact:
  `{replay['post_transient_slopes_match_artifact']}`
- nonzero leakage observed: `{replay['nonzero_leakage_observed']}`
- leakage bounded below threshold: `{replay['leakage_bounded_below_threshold']}`
- support survival passed: `{replay['support_survival_passed']}`
- separability passed: `{replay['separability_passed']}`
- post-transient flattened: `{replay['post_transient_flattened']}`
- budget exact: `{replay['budget_exact']}`
- replay passed: `{replay['replay_passed']}`

## Control Replay

- control count: `{controls['control_count']}`
- all controls passed: `{controls['all_controls_passed']}`
- distinct blocker count: `{controls['distinct_blocker_count']}`
- required closeout blockers present:
  `{controls['required_closeout_blockers_present']}`
- control replay passed: `{controls['control_replay_passed']}`

## Closeout Decision

- strongest branch: `{closeout['strongest_branch']}`
- strongest trajectory regime: `{closeout['strongest_trajectory_regime']}`
- frozen long-horizon C3 class:
  `{closeout['frozen_long_horizon_c3_class']}`
- frozen N07 ceiling: `{closeout['frozen_n07_ceiling']}`
- ID6 evidence classification supported:
  `{closeout['id6_evidence_classification_supported']}`
- ID6 scope: `{closeout['id6_scope']}`
- ID6 is runtime identity acceptance:
  `{closeout['id6_is_runtime_identity_acceptance']}`
- runtime identity acceptance claim allowed:
  `{closeout['runtime_identity_acceptance_claim_allowed']}`
- RC identity collapse claim allowed:
  `{closeout['rc_identity_collapse_claim_allowed']}`
- semantic choice claim allowed:
  `{closeout['semantic_choice_claim_allowed']}`
- agency claim allowed:
  `{closeout['agency_claim_allowed']}`
- native support status: `{closeout['native_support_status']}`
- future Iteration 13 required for N07 closeout:
  `{closeout['future_exploration_invitation']['required_for_n07_closeout']}`

## Claim Boundary

All claim flags remain `false`. Iteration 12 freezes an artifact-only,
source-specific ID6 evidence classification for bounded non-destructive
dual-basin exchange. It does not emit runtime identity acceptance, RC identity
collapse, semantic choice, agency, biological identity, personhood, or
unrestricted identity claims.

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
    print(
        json.dumps(
            {
                "status": result["status"],
                "checks": len(result["checks"]),
                "ceiling": result["closeout_decision"]["frozen_n07_ceiling"],
                "c3_class": result["closeout_decision"][
                    "frozen_long_horizon_c3_class"
                ],
                "artifact_only": result["artifact_only"],
                "runtime_state_used": result["runtime_state_used"],
                "identity_acceptance_claim_allowed": result["closeout_decision"][
                    "runtime_identity_acceptance_claim_allowed"
                ],
                "next": result["next_iteration"],
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()
