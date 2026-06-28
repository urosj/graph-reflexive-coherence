#!/usr/bin/env python3
"""Build N25.2 Iteration 5 replay and persistence matrix."""

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
OUTPUT = EXPERIMENT / "outputs" / "n25_2_replay_persistence_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_2_replay_persistence_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_replay_persistence_matrix.py"
)

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
        snapshot_path = Path(temp_dir) / "n25_2_i5_runtime_snapshot.json"
        snapshot_path.write_text(canonical_json(snapshot), encoding="utf-8")
        return LGRC9V3.load(str(snapshot_path))


def replay_child_candidate(
    *,
    candidate_id: str,
    source_iteration: str,
    source_output_digest: str,
    source_artifact_sha256: str,
    source_child_record: dict[str, Any],
    source_snapshot: dict[str, Any],
    source_snapshot_digest: str,
) -> dict[str, Any]:
    model = load_runtime_model_from_snapshot(source_snapshot)
    loaded_snapshot = model.snapshot()
    first = model.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(
            source_child_record["child_basin_state_digest"]
        ),
        snapshot_replay_artifact=loaded_snapshot,
    )
    second = model.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(
            source_child_record["child_basin_state_digest"]
        ),
        snapshot_replay_artifact=loaded_snapshot,
    )
    record = first["replay_validation_record"].to_artifact()
    second_record = second["replay_validation_record"].to_artifact()
    replay_results = {
        "artifact_replay_result": record["artifact_replay_result"],
        "snapshot_load_replay_result": record["snapshot_load_replay_result"],
        "duplicate_replay_result": record["duplicate_replay_result"],
        "time_order_replay_result": record["time_order_replay_result"],
    }
    ratios = {
        "membership_persistence_ratio": float(record["membership_persistence_ratio"]),
        "support_persistence_ratio": float(record["support_persistence_ratio"]),
        "coherence_persistence_ratio": float(record["coherence_persistence_ratio"]),
        "boundary_persistence_ratio": float(record["boundary_persistence_ratio"]),
        "flux_persistence_ratio": float(record["flux_persistence_ratio"]),
    }
    replay_passed = all(value == "passed" for value in replay_results.values())
    ratios_passed = all(value == 1.0 for value in ratios.values())
    duplicate_stable = (
        first["emitted"] is True
        and second["emitted"] is False
        and first["replay_validation_digest"] == second["replay_validation_digest"]
        and record == second_record
    )
    return {
        "candidate_id": candidate_id,
        "source_iteration": source_iteration,
        "source_output_digest": source_output_digest,
        "source_artifact_sha256": source_artifact_sha256,
        "source_child_basin_state_digest": source_child_record[
            "child_basin_state_digest"
        ],
        "source_snapshot_digest": source_snapshot_digest,
        "loaded_snapshot_digest": digest_value(loaded_snapshot),
        "runtime_emitted_child_record_only": True,
        "derived_report_only": False,
        "replay_validation_digest": str(first["replay_validation_digest"]),
        "replay_validation_record": record,
        "duplicate_replay_first_emitted": bool(first["emitted"]),
        "duplicate_replay_second_emitted": bool(second["emitted"]),
        "duplicate_replay_digest_stable": duplicate_stable,
        "artifact_replay_passed": replay_results["artifact_replay_result"] == "passed",
        "snapshot_load_replay_passed": (
            replay_results["snapshot_load_replay_result"] == "passed"
        ),
        "duplicate_replay_passed": replay_results["duplicate_replay_result"]
        == "passed",
        "time_order_replay_passed": replay_results["time_order_replay_result"]
        == "passed",
        "replay_results": replay_results,
        "persistence_ratios": ratios,
        "all_required_replay_modes_passed": replay_passed,
        "all_persistence_ratios_exact": ratios_passed,
        "mb4_replay_candidate_allowed": bool(
            first["mb4_replay_candidate_allowed"]
            and replay_passed
            and ratios_passed
            and duplicate_stable
        ),
        "mb5_or_stronger_supported": False,
        "mb6_supported": False,
        "claim_flags": record["claim_flags"],
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": "MB4 replay-backed child-basin persistence candidate; not MB5, not MB6",
    }


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    reference_row = replay_child_candidate(
        candidate_id="i4_reference_child_basin_core_0",
        source_iteration="I4",
        source_output_digest=i4["output_digest"],
        source_artifact_sha256=sha256_file(I4_OUTPUT),
        source_child_record=i4["child_basin_state_records"]["records"][0],
        source_snapshot=i4["runtime_snapshot_artifact"],
        source_snapshot_digest=i4["runtime_snapshot_digest"],
    )
    variant_row = replay_child_candidate(
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
        source_snapshot_digest=i4a["route_child_basin_variant"]["runtime_trace"][
            "final_snapshot_digest"
        ],
    )
    front_scope = {
        "source_iteration": "I4-A",
        "candidate_id": "i4a_front_capacity_boundary_birth_companion",
        "replay_scope": "not_applicable",
        "reason_code": "front_capacity_companion_emits_topology_birth_not_child_basin_state_record",
        "child_basin_replay_consumption_allowed": False,
        "mb4_replay_candidate_allowed": False,
        "mb5_or_stronger_supported": False,
        "mb6_supported": False,
    }
    replay_rows = [reference_row, variant_row]
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
        "candidate_row_count": len(replay_rows),
        "mb4_replay_candidate_count": sum(
            1 for row in replay_rows if row["mb4_replay_candidate_allowed"]
        ),
        "all_candidate_replays_passed": all(
            row["mb4_replay_candidate_allowed"] for row in replay_rows
        ),
        "front_capacity_companion_replay_scope": front_scope["replay_scope"],
        "matrix_window_count": len(replay_rows),
        "runtime_record_window_count_per_row": [
            row["replay_validation_record"]["replay_window"]["window_count"]
            for row in replay_rows
        ],
        "multi_window_child_basin_persistence_replay_status": "passed",
        "persistence_claim_kind": "replay_persistence_of_emitted_child_basin_records",
        "long_horizon_persistence_supported": False,
        "extended_multi_window_survival_under_stress_supported": False,
        "multi_window_scope_note": (
            "I5 matrix covers two source-current child-basin candidate windows; "
            "each native replay record remains a one-window runtime replay. "
            "This is not long-horizon persistence or stress-window survival."
        ),
        "duplicate_replay_semantics": (
            "first replay emits the validation record; second replay suppresses "
            "a duplicate and returns the same digest"
        ),
    }
    artifact_manifest = [
        {
            "artifact_role": "i4_replay_record",
            "json_pointer": "#/replay_rows/0",
            "digest": digest_value(reference_row),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "i4a_route_variant_replay_record",
            "json_pointer": "#/replay_rows/1",
            "digest": digest_value(variant_row),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "front_capacity_scope_record",
            "json_pointer": "#/front_capacity_companion_scope",
            "digest": digest_value(front_scope),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "i4_and_i4a_sources_ready_for_replay",
            i4["status"] == "passed"
            and i4a["status"] == "passed"
            and i4["ready_for_iteration_5_replay_persistence_matrix"] is True
            and i4a["ready_for_iteration_5_replay_persistence_matrix"] is True,
            {
                "i4_output_digest": i4["output_digest"],
                "i4a_output_digest": i4a["output_digest"],
            },
        ),
        check(
            "artifact_snapshot_duplicate_and_time_order_replay_passed",
            all(row["all_required_replay_modes_passed"] for row in replay_rows),
            [row["replay_results"] for row in replay_rows],
        ),
        check(
            "persistence_ratios_exact_for_all_child_basin_candidates",
            all(row["all_persistence_ratios_exact"] for row in replay_rows),
            [row["persistence_ratios"] for row in replay_rows],
        ),
        check(
            "duplicate_replay_stable_for_all_child_basin_candidates",
            all(row["duplicate_replay_digest_stable"] for row in replay_rows),
            [
                {
                    "candidate_id": row["candidate_id"],
                    "first_emitted": row["duplicate_replay_first_emitted"],
                    "second_emitted": row["duplicate_replay_second_emitted"],
                }
                for row in replay_rows
            ],
        ),
        check(
            "runtime_emitted_records_only",
            all(row["runtime_emitted_child_record_only"] for row in replay_rows)
            and not front_scope["child_basin_replay_consumption_allowed"],
            {
                "replayed_candidates": [row["candidate_id"] for row in replay_rows],
                "front_capacity_scope": front_scope,
            },
        ),
        check(
            "front_capacity_companion_not_replayed_as_child_basin",
            front_scope["replay_scope"] == "not_applicable"
            and front_scope["mb4_replay_candidate_allowed"] is False,
            front_scope,
        ),
        check(
            "missing_or_failed_replay_would_block_mb6",
            all(row["mb4_replay_candidate_allowed"] for row in replay_rows)
            and not any(row["mb5_or_stronger_supported"] for row in replay_rows)
            and not any(row["mb6_supported"] for row in replay_rows),
            "I5 can permit MB4 replay candidates only; controls/stress/MB6 gate remain pending",
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
            all(not any(row["claim_flags"].values()) for row in replay_rows)
            and all(flag is False for flag in unsafe_claim_flags().values()),
            {
                "replay_row_claim_flags_false": [
                    not any(row["claim_flags"].values()) for row in replay_rows
                ],
                "global_unsafe_claim_flags": unsafe_claim_flags(),
            },
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_replay_persistence_matrix",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_replay_persistence_matrix_mb4_candidates_no_mb5_no_mb6"
        ),
        "experiment": "N25.2",
        "iteration": 5,
        "command": COMMAND,
        "source_chain": {
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4a_output_digest": i4a["output_digest"],
            "i4a_artifact_sha256": sha256_file(I4A_OUTPUT),
        },
        "replay_matrix_scope": {
            "included_child_basin_candidates": [
                "i4_reference_child_basin_core_0",
                "i4a_route_variant_child_basin_core_2",
            ],
            "excluded_context_rows": ["i4a_front_capacity_boundary_birth_companion"],
            "exclusion_reason": front_scope["reason_code"],
        },
        "matrix_summary": matrix_summary,
        "replay_rows": replay_rows,
        "front_capacity_companion_scope": front_scope,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": artifact_manifest,
        "implementation_no_mutation_proof": no_mutation_proof,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "native_runtime_replay_validated",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "mb_ladder_candidate": "MB4_replay_backed_child_basin_persistence_candidate",
        "mb4_supported_candidate_count": matrix_summary["mb4_replay_candidate_count"],
        "mb5_or_stronger_supported": False,
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": [
            "control_matrix_pending_iteration_6",
            "stress_matrix_pending_iteration_7",
            "mb6_gate_pending_iteration_8",
        ],
        "required_iteration_6_controls": [
            "label_only_basin_formation_control",
            "old_basin_thickening_relabel_control",
            "transient_flow_sink_relabel_control",
            "collapse_reabsorption_relabel_control",
            "graph_visual_only_success_control",
            "hidden_producer_basin_insertion_control",
            "producer_success_as_native_support_control",
            "front_capacity_backfill_control",
            "mb5_as_mb6_relabel_control",
            "unsafe_semantic_agency_native_support_relabel_controls",
        ],
        "front_capacity_scope_carry_forward": {
            "child_basin_replay_consumption_allowed": False,
            "mb4_replay_candidate_allowed": False,
            "mb5_or_mb6_backfill_allowed": False,
            "carry_forward_to_i6_i7_as": "provenance_context_only",
        },
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": "MB4 replay-backed candidates only; not MB5, not MB6",
        "ready_for_iteration_6_fail_closed_control_matrix": True,
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

    rows = data["replay_rows"]
    summary = data["matrix_summary"]
    report = f"""# N25.2 Iteration 5 - Replay And Persistence Matrix

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I5 replays the child-basin records emitted by I4 and the I4-A route variant.
Both pass artifact replay, snapshot/load replay, duplicate replay, time-order
replay, and exact persistence-ratio checks.

```text
i4_output_digest = {data['source_chain']['i4_output_digest']}
i4a_output_digest = {data['source_chain']['i4a_output_digest']}
candidate_row_count = {summary['candidate_row_count']}
mb4_replay_candidate_count = {summary['mb4_replay_candidate_count']}
multi_window_child_basin_persistence_replay_status = {summary['multi_window_child_basin_persistence_replay_status']}
persistence_claim_kind = {summary['persistence_claim_kind']}
long_horizon_persistence_supported = false
extended_multi_window_survival_under_stress_supported = false
mb_ladder_candidate = {data['mb_ladder_candidate']}
mb5_or_stronger_supported = false
mb6_supported = false
n26_unscoped_consumption_allowed = false
```

## Replay Rows

```text
{rows[0]['candidate_id']}:
  replay_digest = {rows[0]['replay_validation_digest']}
  artifact/snapshot/duplicate/time_order = passed/passed/passed/passed
  duplicate_first_emitted/second_emitted = {str(rows[0]['duplicate_replay_first_emitted']).lower()}/{str(rows[0]['duplicate_replay_second_emitted']).lower()}
  membership/support/coherence/boundary/flux = 1.0/1.0/1.0/1.0/1.0

{rows[1]['candidate_id']}:
  replay_digest = {rows[1]['replay_validation_digest']}
  artifact/snapshot/duplicate/time_order = passed/passed/passed/passed
  duplicate_first_emitted/second_emitted = {str(rows[1]['duplicate_replay_first_emitted']).lower()}/{str(rows[1]['duplicate_replay_second_emitted']).lower()}
  membership/support/coherence/boundary/flux = 1.0/1.0/1.0/1.0/1.0
```

The matrix-level multi-window status means I5 covers two source-current
child-basin candidate windows. Each native replay record remains a one-window
runtime replay record, matching the current runtime contract. I5 therefore
supports replay persistence of emitted child-basin records, not extended
multi-window survival under stress or long-horizon child-basin persistence.

For duplicate replay, `first_emitted=true` and `second_emitted=false` means
idempotency worked: the first replay emitted the validation record, while the
second replay suppressed a duplicate and returned the same digest.

## Scope Boundary

The I4-A front-capacity boundary-birth companion is not replayed as a
child-basin row:

```text
front_capacity_replay_scope = {data['front_capacity_companion_scope']['replay_scope']}
reason = {data['front_capacity_companion_scope']['reason_code']}
```

I5 supports MB4 replay-backed child-basin persistence candidates only. It does
not run fail-closed controls, does not support MB5, does not apply the MB6
gate, and does not open N26 unscoped consumption. I6 must still fail-close
label-only basin formation, old-basin thickening, transient sink,
collapse/reabsorption relabel, visual-only success, hidden producer insertion,
producer-as-native, front-capacity backfill, MB5-as-MB6, and unsafe relabel
controls.

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
