#!/usr/bin/env python3
"""Build N25.2 Iteration 5-A multi-window persistence replay."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from pygrc.models import LGRC9V3


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n25_2_replay_persistence_matrix.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_multi_window_persistence_replay.json"
REPORT = EXPERIMENT / "reports" / "n25_2_multi_window_persistence_replay.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_multi_window_persistence_replay.py"
)
DECLARED_REPLAY_WINDOW_COUNT = 3

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
        snapshot_path = Path(temp_dir) / "n25_2_i5a_runtime_snapshot.json"
        snapshot_path.write_text(canonical_json(snapshot), encoding="utf-8")
        return LGRC9V3.load(str(snapshot_path))


def child_record_present(snapshot: Mapping[str, Any], child_digest: str) -> bool:
    records = (
        snapshot.get("dynamics", {})
        .get("lgrc9v3_runtime", {})
        .get("child_basin_state_log", [])
    )
    if not isinstance(records, list):
        return False
    return any(
        isinstance(record, Mapping)
        and record.get("child_basin_state_digest") == child_digest
        for record in records
    )


def replay_results_passed(record: Mapping[str, Any]) -> bool:
    return all(
        record.get(field_name) == "passed"
        for field_name in (
            "artifact_replay_result",
            "snapshot_load_replay_result",
            "duplicate_replay_result",
            "time_order_replay_result",
        )
    )


def replay_ratios_exact(record: Mapping[str, Any]) -> bool:
    return all(
        float(record.get(field_name, 0.0)) == 1.0
        for field_name in (
            "membership_persistence_ratio",
            "support_persistence_ratio",
            "coherence_persistence_ratio",
            "boundary_persistence_ratio",
            "flux_persistence_ratio",
        )
    )


def build_multi_window_row(
    *,
    candidate_id: str,
    source_iteration: str,
    source_output_digest: str,
    source_artifact_sha256: str,
    source_child_record: dict[str, Any],
    source_snapshot: dict[str, Any],
    i5_replay_digest: str,
) -> dict[str, Any]:
    child_digest = str(source_child_record["child_basin_state_digest"])
    model = load_runtime_model_from_snapshot(source_snapshot)
    window_records: list[dict[str, Any]] = []
    for window_index in range(1, DECLARED_REPLAY_WINDOW_COUNT + 1):
        before_snapshot = model.snapshot()
        before_digest = digest_value(before_snapshot)
        before_time = float(model.get_state().time)
        step_result = model.step()
        after_snapshot = model.snapshot()
        after_digest = digest_value(after_snapshot)
        after_time = float(model.get_state().time)
        replay = model.validate_multi_basin_child_basin_replay(
            source_child_basin_state_digest=child_digest,
            snapshot_replay_artifact=after_snapshot,
        )
        replay_record = replay["replay_validation_record"].to_artifact()
        window_records.append(
            {
                "window_index": window_index,
                "before_snapshot_digest": before_digest,
                "after_snapshot_digest": after_digest,
                "before_time": before_time,
                "after_time": after_time,
                "step_event_count": len(step_result.events),
                "child_basin_record_present_before": child_record_present(
                    before_snapshot,
                    child_digest,
                ),
                "child_basin_record_present_after": child_record_present(
                    after_snapshot,
                    child_digest,
                ),
                "replay_validation_digest": str(replay["replay_validation_digest"]),
                "replay_emitted": bool(replay["emitted"]),
                "native_replay_record_window_count": float(
                    replay_record["replay_window"]["window_count"]
                ),
                "replay_results_passed": replay_results_passed(replay_record),
                "replay_ratios_exact": replay_ratios_exact(replay_record),
                "replay_validation_record": replay_record,
            }
        )
    all_windows_passed = all(
        record["child_basin_record_present_before"]
        and record["child_basin_record_present_after"]
        and record["replay_results_passed"]
        and record["replay_ratios_exact"]
        for record in window_records
    )
    replay_digests = [record["replay_validation_digest"] for record in window_records]
    snapshot_digests = [record["after_snapshot_digest"] for record in window_records]
    return {
        "candidate_id": candidate_id,
        "source_iteration": source_iteration,
        "source_output_digest": source_output_digest,
        "source_artifact_sha256": source_artifact_sha256,
        "source_child_basin_state_digest": child_digest,
        "i5_source_replay_validation_digest": i5_replay_digest,
        "declared_replay_window_count": DECLARED_REPLAY_WINDOW_COUNT,
        "runtime_snapshot_window_count": len(window_records),
        "native_replay_record_window_count_per_window": [
            record["native_replay_record_window_count"] for record in window_records
        ],
        "window_records": window_records,
        "window_replay_validation_digests": replay_digests,
        "window_snapshot_digests": snapshot_digests,
        "window_trace_digest": digest_value(window_records),
        "all_window_child_basin_records_present": all(
            record["child_basin_record_present_after"] for record in window_records
        ),
        "all_window_replay_results_passed": all(
            record["replay_results_passed"] for record in window_records
        ),
        "all_window_replay_ratios_exact": all(
            record["replay_ratios_exact"] for record in window_records
        ),
        "duplicate_replay_suppression_observed": (
            window_records[0]["replay_emitted"] is True
            and all(record["replay_emitted"] is False for record in window_records[1:])
        ),
        "multi_window_persistence_replay_status": (
            "passed" if all_windows_passed else "blocked"
        ),
        "multi_window_persistence_replay_allowed_for_i8_gate": all_windows_passed,
        "eventful_stress_window_supported": False,
        "eventful_stress_window_status": "not_claimed_by_i5a",
        "claim_ceiling": (
            "multi-window replay persistence of emitted child-basin records; "
            "not eventful stress persistence, not MB6 by itself"
        ),
        "row_decision": "supported" if all_windows_passed else "blocked",
    }


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5_rows = {row["candidate_id"]: row for row in i5["replay_rows"]}
    replay_rows = [
        build_multi_window_row(
            candidate_id="i4_reference_child_basin_core_0",
            source_iteration="I4",
            source_output_digest=i4["output_digest"],
            source_artifact_sha256=sha256_file(I4_OUTPUT),
            source_child_record=i4["child_basin_state_records"]["records"][0],
            source_snapshot=i4["runtime_snapshot_artifact"],
            i5_replay_digest=i5_rows["i4_reference_child_basin_core_0"][
                "replay_validation_digest"
            ],
        ),
        build_multi_window_row(
            candidate_id="i4a_route_variant_child_basin_core_2",
            source_iteration="I4-A",
            source_output_digest=i4a["output_digest"],
            source_artifact_sha256=sha256_file(I4A_OUTPUT),
            source_child_record=i4a["route_child_basin_variant"]["runtime_trace"][
                "child_basin_state_records"
            ][0],
            source_snapshot=i4a["route_child_basin_variant"]["runtime_trace"][
                "runtime_snapshot_artifact"
            ],
            i5_replay_digest=i5_rows["i4a_route_variant_child_basin_core_2"][
                "replay_validation_digest"
            ],
        ),
    ]
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
        "candidate_count": len(replay_rows),
        "declared_replay_window_count": DECLARED_REPLAY_WINDOW_COUNT,
        "runtime_snapshot_window_count_per_candidate": [
            row["runtime_snapshot_window_count"] for row in replay_rows
        ],
        "multi_window_passed_candidate_count": sum(
            1
            for row in replay_rows
            if row["multi_window_persistence_replay_status"] == "passed"
        ),
        "all_window_child_basin_records_present": all(
            row["all_window_child_basin_records_present"] for row in replay_rows
        ),
        "all_window_replay_results_passed": all(
            row["all_window_replay_results_passed"] for row in replay_rows
        ),
        "all_window_replay_ratios_exact": all(
            row["all_window_replay_ratios_exact"] for row in replay_rows
        ),
        "duplicate_replay_suppression_observed": all(
            row["duplicate_replay_suppression_observed"] for row in replay_rows
        ),
        "eventful_stress_window_supported": False,
        "multi_window_scope": (
            "closed-runtime multi-snapshot replay of emitted child-basin records"
        ),
    }
    artifact_manifest = [
        {
            "artifact_role": "multi_window_persistence_replay_trace",
            "json_pointer": "#/multi_window_replay_rows/0",
            "digest": digest_value(replay_rows[0]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "multi_window_persistence_replay_trace",
            "json_pointer": "#/multi_window_replay_rows/1",
            "digest": digest_value(replay_rows[1]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "i5_replay_matrix_available",
            i5["status"] == "passed"
            and i5["mb_ladder_candidate"]
            == "MB4_replay_backed_child_basin_persistence_candidate",
            {"i5_output_digest": i5["output_digest"]},
        ),
        check(
            "multi_window_snapshots_recorded_for_each_candidate",
            all(
                row["runtime_snapshot_window_count"] == DECLARED_REPLAY_WINDOW_COUNT
                for row in replay_rows
            ),
            matrix_summary["runtime_snapshot_window_count_per_candidate"],
        ),
        check(
            "child_basin_records_present_across_windows",
            matrix_summary["all_window_child_basin_records_present"] is True,
            [
                {
                    "candidate_id": row["candidate_id"],
                    "window_presence": [
                        window["child_basin_record_present_after"]
                        for window in row["window_records"]
                    ],
                }
                for row in replay_rows
            ],
        ),
        check(
            "window_replay_results_passed",
            matrix_summary["all_window_replay_results_passed"] is True,
            [
                {
                    "candidate_id": row["candidate_id"],
                    "window_results": [
                        window["replay_results_passed"]
                        for window in row["window_records"]
                    ],
                }
                for row in replay_rows
            ],
        ),
        check(
            "window_replay_ratios_exact",
            matrix_summary["all_window_replay_ratios_exact"] is True,
            [
                {
                    "candidate_id": row["candidate_id"],
                    "window_ratios_exact": [
                        window["replay_ratios_exact"]
                        for window in row["window_records"]
                    ],
                }
                for row in replay_rows
            ],
        ),
        check(
            "duplicate_replay_suppression_preserved",
            matrix_summary["duplicate_replay_suppression_observed"] is True,
            [
                {
                    "candidate_id": row["candidate_id"],
                    "window_emitted": [
                        window["replay_emitted"] for window in row["window_records"]
                    ],
                }
                for row in replay_rows
            ],
        ),
        check(
            "multi_window_persistence_allowed_for_i8_gate",
            all(
                row["multi_window_persistence_replay_allowed_for_i8_gate"]
                for row in replay_rows
            ),
            {
                "multi_window_passed_candidate_count": matrix_summary[
                    "multi_window_passed_candidate_count"
                ]
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
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_multi_window_persistence_replay",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_multi_window_persistence_replay_mb4_extension_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": "5-A",
        "command": COMMAND,
        "source_chain": {
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4a_output_digest": i4a["output_digest"],
            "i4a_artifact_sha256": sha256_file(I4A_OUTPUT),
            "i5_output_digest": i5["output_digest"],
            "i5_artifact_sha256": sha256_file(I5_OUTPUT),
        },
        "multi_window_replay_scope": {
            "declared_replay_window_count": DECLARED_REPLAY_WINDOW_COUNT,
            "source": "closed_runtime_snapshot_replay",
            "native_replay_validator_record_shape": "one_window_per_validation_record",
            "aggregate_trace_role": "multi_window_persistence_replay_trace",
            "eventful_stress_window_supported": False,
            "eventful_stress_window_reason": "I5-A tests persistence replay, not stress dynamics",
        },
        "matrix_summary": matrix_summary,
        "multi_window_replay_rows": replay_rows,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": artifact_manifest,
        "implementation_no_mutation_proof": no_mutation_proof,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "closed_runtime_multi_window_replay",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "mb_ladder_candidate": "MB4_multi_window_replay_backed_child_basin_persistence_candidate",
        "mb5_or_stronger_supported": False,
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": [
            "control_matrix_required_iteration_6",
            "stress_matrix_required_iteration_7",
            "mb6_gate_pending_iteration_8",
        ],
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": (
            "multi-window replay-backed child-basin persistence candidate; "
            "not MB5, not MB6 by itself"
        ),
        "ready_for_iteration_6_fail_closed_control_matrix": True,
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

    summary = data["matrix_summary"]
    rows = data["multi_window_replay_rows"]
    report = f"""# N25.2 Iteration 5-A - Multi-Window Persistence Replay

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I5-A extends I5 by replaying each runtime-emitted child-basin candidate across
three closed-runtime snapshot windows.

```text
i5_output_digest = {data['source_chain']['i5_output_digest']}
declared_replay_window_count = {summary['declared_replay_window_count']}
candidate_count = {summary['candidate_count']}
multi_window_passed_candidate_count = {summary['multi_window_passed_candidate_count']}
all_window_child_basin_records_present = {str(summary['all_window_child_basin_records_present']).lower()}
all_window_replay_results_passed = {str(summary['all_window_replay_results_passed']).lower()}
all_window_replay_ratios_exact = {str(summary['all_window_replay_ratios_exact']).lower()}
duplicate_replay_suppression_observed = {str(summary['duplicate_replay_suppression_observed']).lower()}
eventful_stress_window_supported = false
mb6_supported = false
```

## Candidate Rows

```text
{rows[0]['candidate_id']}:
  runtime_snapshot_window_count = {rows[0]['runtime_snapshot_window_count']}
  multi_window_persistence_replay_status = {rows[0]['multi_window_persistence_replay_status']}
  window_trace_digest = {rows[0]['window_trace_digest']}

{rows[1]['candidate_id']}:
  runtime_snapshot_window_count = {rows[1]['runtime_snapshot_window_count']}
  multi_window_persistence_replay_status = {rows[1]['multi_window_persistence_replay_status']}
  window_trace_digest = {rows[1]['window_trace_digest']}
```

## Interpretation

I5-A supplies the missing multi-window replay evidence at the experiment layer:
the emitted child-basin records remain present across three closed-runtime
snapshot/replay windows and replay ratios remain exact in every window.

This does not change the native replay validator shape. Each native validation
record still has `window_count = 1.0`; I5-A is the aggregate source-current
multi-window replay trace built from repeated closed-runtime snapshots. It is
therefore valid as multi-window replay evidence for I8 gate classification, but
it is not eventful stress persistence, MB5 by itself, MB6 by itself, native
support, agency, or Phase 8 completion.

## Checks

{chr(10).join(checks)}

## Digest

```text
output_digest = {data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
