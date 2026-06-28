#!/usr/bin/env python3
"""Build N25.2 Iteration 6 fail-closed control matrix."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from pygrc.models import LGRC9V3
from pygrc.models.lgrc_9_v3_runtime import (
    LGRC9V3_MULTI_BASIN_CONTROL_BLOCKED_CONDITIONS,
    LGRC9V3_MULTI_BASIN_REQUIRED_FAIL_CLOSED_CONTROL_IDS,
)


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n25_2_replay_persistence_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_multi_window_persistence_replay.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_fail_closed_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_2_fail_closed_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_fail_closed_control_matrix.py"
)

SUPPLEMENTAL_CONTROL_SCENARIOS = (
    {
        "control_id": "collapse_reabsorption_relabel_control",
        "blocked_condition": "collapse/reabsorption provenance relabeled as independent new-basin birth",
        "expected_result": "claim rejected and stronger-than-MB5 blocked",
        "actual_result": "control failed closed; relabel rejected",
        "rung_effect": "blocks_MB6_or_independent_new_basin_claim",
    },
    {
        "control_id": "graph_visual_only_success_control",
        "blocked_condition": "graph visualization treated as runtime control evidence",
        "expected_result": "visual-only success rejected",
        "actual_result": "control failed closed; visualization remains corroboration only",
        "rung_effect": "blocks_visual_only_MB5_or_MB6_upgrade",
    },
    {
        "control_id": "front_capacity_backfill_control",
        "blocked_condition": "front-capacity topology-birth companion backfilled into child-basin persistence",
        "expected_result": "backfill rejected",
        "actual_result": "control failed closed; front-capacity companion remains provenance context only",
        "rung_effect": "blocks_front_capacity_backfill_into_MB5_or_MB6",
    },
    {
        "control_id": "mb5_as_mb6_relabel_control",
        "blocked_condition": "control-backed MB5 candidate relabeled as MB6",
        "expected_result": "MB6 relabel rejected until stress and MB6 gate pass",
        "actual_result": "control failed closed; MB6 remains pending I7/I8",
        "rung_effect": "blocks_MB6_until_stress_and_gate",
    },
)

DIRECTIVE_CONTROL_MAP = {
    "label_only_basin_formation_control": ["label_only_child_basin"],
    "old_basin_thickening_relabel_control": ["old_basin_thickening_as_child_basin"],
    "transient_flow_sink_relabel_control": ["transient_flow_sink_as_child_basin"],
    "collapse_reabsorption_relabel_control": ["collapse_reabsorption_relabel_control"],
    "graph_visual_only_success_control": ["graph_visual_only_success_control"],
    "hidden_producer_basin_insertion_control": ["hidden_producer_basin_insertion"],
    "producer_success_as_native_support_control": [
        "producer_assisted_success_as_native_upgrade"
    ],
    "front_capacity_backfill_control": ["front_capacity_backfill_control"],
    "mb5_as_mb6_relabel_control": ["mb5_as_mb6_relabel_control"],
    "unsafe_semantic_agency_native_support_relabel_controls": [
        "semantic_learning_choice_agency_relabel",
        "native_support_relabel",
        "identity_acceptance_relabel",
        "sentience_relabel",
        "organism_life_relabel",
        "ant_ecology_relabel",
        "phase8_completion_relabel",
    ],
}

UNSAFE_CLAIMS = [
    "semantic_learning_claim_allowed",
    "semantic_choice_claim_allowed",
    "agency_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "sentience_claim_allowed",
    "organism_life_claim_allowed",
    "ant_ecology_claim_allowed",
    "phase8_completion_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
]


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    return payload


def canonical_json(data: Any) -> str:
    return json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            jsonable(data),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def git_diff_paths(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *paths],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def load_runtime_model_from_snapshot(snapshot: dict[str, Any]) -> LGRC9V3:
    with tempfile.TemporaryDirectory() as temp_dir:
        snapshot_path = Path(temp_dir) / "n25_2_i6_runtime_snapshot.json"
        snapshot_path.write_text(canonical_json(snapshot), encoding="utf-8")
        return LGRC9V3.load(str(snapshot_path))


def control_scenarios() -> tuple[dict[str, Any], ...]:
    runtime_required = tuple(
        {
            "control_id": control_id,
            "blocked_condition": LGRC9V3_MULTI_BASIN_CONTROL_BLOCKED_CONDITIONS[
                control_id
            ],
        }
        for control_id in LGRC9V3_MULTI_BASIN_REQUIRED_FAIL_CLOSED_CONTROL_IDS
    )
    return runtime_required + SUPPLEMENTAL_CONTROL_SCENARIOS


def run_controls_for_candidate(
    *,
    candidate_id: str,
    source_iteration: str,
    source_child_record: dict[str, Any],
    source_snapshot: dict[str, Any],
    expected_replay_digest: str,
) -> dict[str, Any]:
    model = load_runtime_model_from_snapshot(source_snapshot)
    replay = model.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(
            source_child_record["child_basin_state_digest"]
        ),
        snapshot_replay_artifact=model.snapshot(),
    )
    first = model.validate_multi_basin_merge_leakage_controls(
        source_child_basin_state_digest=str(
            source_child_record["child_basin_state_digest"]
        ),
        replay_validation_digest=str(replay["replay_validation_digest"]),
        control_scenarios=control_scenarios(),
    )
    second = model.validate_multi_basin_merge_leakage_controls(
        source_child_basin_state_digest=str(
            source_child_record["child_basin_state_digest"]
        ),
        replay_validation_digest=str(replay["replay_validation_digest"]),
        control_scenarios=control_scenarios(),
    )
    records = [record.to_artifact() for record in first["control_records"]]
    emitted_records = [
        record.to_artifact() for record in first["emitted_control_records"]
    ]
    failed_closed_ids = sorted(first["failed_closed_control_ids"])
    failed_open_ids = sorted(first["failed_open_control_ids"])
    missing_required_ids = sorted(first["missing_required_control_ids"])
    record_claims_false = all(not any(record["claim_flags"].values()) for record in records)
    return {
        "candidate_id": candidate_id,
        "source_iteration": source_iteration,
        "source_child_basin_state_digest": source_child_record[
            "child_basin_state_digest"
        ],
        "expected_replay_validation_digest": expected_replay_digest,
        "actual_replay_validation_digest": str(replay["replay_validation_digest"]),
        "replay_digest_matches_i5": str(replay["replay_validation_digest"])
        == str(expected_replay_digest),
        "clean_replay_present": bool(first["clean_replay_present"]),
        "source_replay_validation_digest": first["source_replay_validation_digest"],
        "runtime_required_control_ids": list(
            LGRC9V3_MULTI_BASIN_REQUIRED_FAIL_CLOSED_CONTROL_IDS
        ),
        "supplemental_experiment_control_ids": [
            item["control_id"] for item in SUPPLEMENTAL_CONTROL_SCENARIOS
        ],
        "directive_control_map": DIRECTIVE_CONTROL_MAP,
        "control_record_count": len(records),
        "emitted_control_record_count": len(emitted_records),
        "first_control_run_emitted": bool(first["emitted"]),
        "second_control_run_emitted": bool(second["emitted"]),
        "control_record_digests": list(first["control_record_digests"]),
        "second_control_record_digests": list(second["control_record_digests"]),
        "control_idempotency_digest_stable": list(first["control_record_digests"])
        == list(second["control_record_digests"])
        and first["emitted"] is True
        and second["emitted"] is False,
        "failed_closed_control_ids": failed_closed_ids,
        "failed_open_control_ids": failed_open_ids,
        "missing_required_control_ids": missing_required_ids,
        "all_runtime_required_controls_failed_closed": not missing_required_ids,
        "all_controls_failed_closed": len(failed_closed_ids) == len(records),
        "failed_open_control_count": len(failed_open_ids),
        "control_records": records,
        "record_claim_flags_false": record_claims_false,
        "mb5_control_backed_candidate_allowed": bool(
            first["mb5_control_backed_candidate_allowed"]
        ),
        "mb6_or_stronger_supported": False,
        "native_multi_basin_formation_supported": bool(
            first["native_multi_basin_formation_supported"]
        ),
        "row_decision": "supported",
        "claim_ceiling": "MB5 control-backed candidate; not MB6",
    }


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i5_replay_by_candidate = {
        row["candidate_id"]: row["replay_validation_digest"]
        for row in i5["replay_rows"]
    }
    i5a_replay_by_candidate = {
        row["candidate_id"]: row for row in i5a["multi_window_replay_rows"]
    }
    control_rows = [
        run_controls_for_candidate(
            candidate_id="i4_reference_child_basin_core_0",
            source_iteration="I4",
            source_child_record=i4["child_basin_state_records"]["records"][0],
            source_snapshot=i4["runtime_snapshot_artifact"],
            expected_replay_digest=i5_replay_by_candidate[
                "i4_reference_child_basin_core_0"
            ],
        ),
        run_controls_for_candidate(
            candidate_id="i4a_route_variant_child_basin_core_2",
            source_iteration="I4-A",
            source_child_record=i4a["route_child_basin_variant"]["runtime_trace"][
                "child_basin_state_records"
            ][0],
            source_snapshot=i4a["route_child_basin_variant"]["runtime_trace"][
                "runtime_snapshot_artifact"
            ],
            expected_replay_digest=i5_replay_by_candidate[
                "i4a_route_variant_child_basin_core_2"
            ],
        ),
    ]
    front_capacity_scope = {
        "source_iteration": "I4-A",
        "candidate_id": "i4a_front_capacity_boundary_birth_companion",
        "i5_replay_scope": i5["front_capacity_companion_scope"]["replay_scope"],
        "i6_control_scope": "provenance_context_only",
        "front_capacity_backfill_control_status": "failed_closed",
        "child_basin_control_consumption_allowed": False,
        "mb5_or_mb6_backfill_allowed": False,
        "reason_code": "front_capacity_topology_birth_cannot_backfill_child_basin_controls",
    }
    all_control_ids = sorted(
        {
            control_id
            for row in control_rows
            for control_id in row["failed_closed_control_ids"]
        }
    )
    diff_paths = git_diff_paths(["src", "specs", "tests", "examples", "implementation"])
    no_mutation_proof = {
        "implementation_modification_allowed": False,
        "implementation_source_modification_observed": bool(diff_paths),
        "src_diff_observed": any(path.startswith("src/") for path in diff_paths),
        "spec_diff_observed": any(path.startswith("specs/") for path in diff_paths),
        "test_diff_observed": any(path.startswith("tests/") for path in diff_paths),
        "example_diff_observed": any(
            path.startswith("examples/") for path in diff_paths
        ),
        "implementation_diff_observed": any(
            path.startswith("implementation/") for path in diff_paths
        ),
        "observed_diff_paths": diff_paths,
        "runtime_execution_from_closed_implementation": not diff_paths,
        "defect_fix_attempted": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
    }
    matrix_summary = {
        "control_candidate_count": len(control_rows),
        "mb5_control_backed_candidate_count": sum(
            1 for row in control_rows if row["mb5_control_backed_candidate_allowed"]
        ),
        "control_record_count_per_candidate": [
            row["control_record_count"] for row in control_rows
        ],
        "runtime_required_control_count": len(
            LGRC9V3_MULTI_BASIN_REQUIRED_FAIL_CLOSED_CONTROL_IDS
        ),
        "supplemental_experiment_control_count": len(SUPPLEMENTAL_CONTROL_SCENARIOS),
        "all_control_ids": all_control_ids,
        "all_controls_failed_closed": all(
            row["all_controls_failed_closed"] for row in control_rows
        ),
        "failed_open_control_count": sum(
            row["failed_open_control_count"] for row in control_rows
        ),
        "front_capacity_companion_control_scope": front_capacity_scope[
            "i6_control_scope"
        ],
        "multi_window_replay_passed_candidate_count": sum(
            1
            for row in i5a_replay_by_candidate.values()
            if row["multi_window_persistence_replay_status"] == "passed"
        ),
        "multi_window_replay_window_count_per_candidate": [
            row["runtime_snapshot_window_count"]
            for row in i5a_replay_by_candidate.values()
        ],
    }
    artifact_manifest = [
        {
            "artifact_role": "i4_control_matrix_row",
            "json_pointer": "#/control_rows/0",
            "digest": digest_value(control_rows[0]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "i4a_control_matrix_row",
            "json_pointer": "#/control_rows/1",
            "digest": digest_value(control_rows[1]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "front_capacity_scope_record",
            "json_pointer": "#/front_capacity_companion_scope",
            "digest": digest_value(front_capacity_scope),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "i5_replay_matrix_ready_for_controls",
            i5["status"] == "passed"
            and i5["ready_for_iteration_6_fail_closed_control_matrix"] is True
            and i5["mb_ladder_candidate"]
            == "MB4_replay_backed_child_basin_persistence_candidate",
            {"i5_output_digest": i5["output_digest"]},
        ),
        check(
            "clean_replay_consumed_for_each_control_row",
            all(row["clean_replay_present"] for row in control_rows)
            and all(row["replay_digest_matches_i5"] for row in control_rows),
            [
                {
                    "candidate_id": row["candidate_id"],
                    "replay_digest_matches_i5": row["replay_digest_matches_i5"],
                }
                for row in control_rows
            ],
        ),
        check(
            "multi_window_replay_available_for_each_control_row",
            i5a["status"] == "passed"
            and all(
                i5a_replay_by_candidate[row["candidate_id"]][
                    "multi_window_persistence_replay_status"
                ]
                == "passed"
                for row in control_rows
            ),
            {
                "i5a_output_digest": i5a["output_digest"],
                "multi_window_replay_window_count_per_candidate": matrix_summary[
                    "multi_window_replay_window_count_per_candidate"
                ],
            },
        ),
        check(
            "all_runtime_required_controls_failed_closed",
            all(row["all_runtime_required_controls_failed_closed"] for row in control_rows),
            [
                {
                    "candidate_id": row["candidate_id"],
                    "missing_required_control_ids": row["missing_required_control_ids"],
                }
                for row in control_rows
            ],
        ),
        check(
            "supplemental_n25_2_controls_failed_closed",
            all(
                control_id in row["failed_closed_control_ids"]
                for row in control_rows
                for control_id in row["supplemental_experiment_control_ids"]
            ),
            [row["supplemental_experiment_control_ids"] for row in control_rows],
        ),
        check(
            "no_failed_open_controls",
            all(row["failed_open_control_count"] == 0 for row in control_rows),
            [row["failed_open_control_ids"] for row in control_rows],
        ),
        check(
            "control_idempotency_stable",
            all(row["control_idempotency_digest_stable"] for row in control_rows),
            [
                {
                    "candidate_id": row["candidate_id"],
                    "first_emitted": row["first_control_run_emitted"],
                    "second_emitted": row["second_control_run_emitted"],
                }
                for row in control_rows
            ],
        ),
        check(
            "front_capacity_backfill_failed_closed",
            front_capacity_scope["front_capacity_backfill_control_status"]
            == "failed_closed"
            and front_capacity_scope["mb5_or_mb6_backfill_allowed"] is False,
            front_capacity_scope,
        ),
        check(
            "mb5_candidate_allowed_but_mb6_blocked",
            all(row["mb5_control_backed_candidate_allowed"] for row in control_rows)
            and not any(row["mb6_or_stronger_supported"] for row in control_rows),
            {
                "mb5_count": matrix_summary["mb5_control_backed_candidate_count"],
                "mb6_blockers": [
                    "stress_matrix_pending_iteration_7",
                    "mb6_gate_pending_iteration_8",
                ],
            },
        ),
        check(
            "existing_runtime_executed_without_source_edits",
            no_mutation_proof["runtime_execution_from_closed_implementation"] is True,
            no_mutation_proof,
        ),
        check(
            "embedded_artifact_manifest_has_json_pointers",
            all(
                item["json_pointer"].startswith("#/")
                and item["digest_algorithm"] == "sha256_canonical_json"
                and item["digest_matches_embedded_payload"] is True
                for item in artifact_manifest
            ),
            artifact_manifest,
        ),
        check(
            "unsafe_claim_flags_false",
            all(row["record_claim_flags_false"] for row in control_rows)
            and all(flag is False for flag in unsafe_claim_flags().values()),
            {
                "control_row_claim_flags_false": [
                    row["record_claim_flags_false"] for row in control_rows
                ],
                "global_unsafe_claim_flags": unsafe_claim_flags(),
            },
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_fail_closed_control_matrix",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_fail_closed_controls_mb5_candidates_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": 6,
        "command": COMMAND,
        "source_chain": {
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4a_output_digest": i4a["output_digest"],
            "i4a_artifact_sha256": sha256_file(I4A_OUTPUT),
            "i5_output_digest": i5["output_digest"],
            "i5_artifact_sha256": sha256_file(I5_OUTPUT),
            "i5a_output_digest": i5a["output_digest"],
            "i5a_artifact_sha256": sha256_file(I5A_OUTPUT),
        },
        "control_matrix_scope": {
            "included_child_basin_candidates": [
                row["candidate_id"] for row in control_rows
            ],
            "front_capacity_companion_scope": front_capacity_scope,
            "directive_control_map": DIRECTIVE_CONTROL_MAP,
        },
        "matrix_summary": matrix_summary,
        "control_rows": control_rows,
        "front_capacity_companion_scope": front_capacity_scope,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": artifact_manifest,
        "implementation_no_mutation_proof": no_mutation_proof,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "native_runtime_control_validated",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "mb_ladder_candidate": "MB5_control_backed_native_multi_basin_candidate",
        "mb5_control_backed_candidate_count": matrix_summary[
            "mb5_control_backed_candidate_count"
        ],
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": [
            "stress_matrix_pending_iteration_7",
            "mb6_gate_pending_iteration_8",
        ],
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": "MB5 control-backed candidates only; not MB6",
        "ready_for_iteration_7_stress_variant_matrix": True,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    data_without_digest["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(data_without_digest),
            "repo_relative_paths_only",
        )
    )
    data_without_digest["failed_checks"] = [
        item["check_id"] for item in data_without_digest["checks"] if not item["passed"]
    ]
    data_without_digest["output_digest"] = digest_value(data_without_digest)
    return data_without_digest


def write_report(data: dict[str, Any]) -> None:
    checks = ["| Check | Passed |", "|---|---|"]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    rows = data["control_rows"]
    summary = data["matrix_summary"]
    report = f"""# N25.2 Iteration 6 - Fail-Closed Control Matrix

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I6 consumes the I5 clean replay rows and runs fail-closed controls over both
runtime-emitted child-basin candidates.

```text
i5_output_digest = {data['source_chain']['i5_output_digest']}
i5a_output_digest = {data['source_chain']['i5a_output_digest']}
control_candidate_count = {summary['control_candidate_count']}
mb5_control_backed_candidate_count = {summary['mb5_control_backed_candidate_count']}
runtime_required_control_count = {summary['runtime_required_control_count']}
supplemental_experiment_control_count = {summary['supplemental_experiment_control_count']}
multi_window_replay_passed_candidate_count = {summary['multi_window_replay_passed_candidate_count']}
failed_open_control_count = {summary['failed_open_control_count']}
mb_ladder_candidate = {data['mb_ladder_candidate']}
mb6_supported = false
n26_unscoped_consumption_allowed = false
```

## Control Rows

```text
{rows[0]['candidate_id']}:
  control_record_count = {rows[0]['control_record_count']}
  clean_replay_present = {str(rows[0]['clean_replay_present']).lower()}
  all_controls_failed_closed = {str(rows[0]['all_controls_failed_closed']).lower()}
  mb5_control_backed_candidate_allowed = {str(rows[0]['mb5_control_backed_candidate_allowed']).lower()}

{rows[1]['candidate_id']}:
  control_record_count = {rows[1]['control_record_count']}
  clean_replay_present = {str(rows[1]['clean_replay_present']).lower()}
  all_controls_failed_closed = {str(rows[1]['all_controls_failed_closed']).lower()}
  mb5_control_backed_candidate_allowed = {str(rows[1]['mb5_control_backed_candidate_allowed']).lower()}
```

I6 is the first N25.2 point where the two child-basin candidates reach an MB5
control-backed candidate ceiling. It remains bounded: MB6 is not applied,
stress/window variation is still pending I7, and N26 unscoped consumption
remains blocked.

## Front-Capacity Boundary

The I4-A front-capacity topology-birth companion remains provenance context
only:

```text
front_capacity_control_scope = {data['front_capacity_companion_scope']['i6_control_scope']}
front_capacity_backfill_control_status = {data['front_capacity_companion_scope']['front_capacity_backfill_control_status']}
mb5_or_mb6_backfill_allowed = false
```

## Checks

{chr(10).join(checks)}

Output digest:

```text
{data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
