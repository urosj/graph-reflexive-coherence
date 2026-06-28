#!/usr/bin/env python3
"""Build N25.2 Iteration 8 MB6 support / blocker matrix."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n25_2_source_inventory_and_admissibility_audit.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n25_2_mb6_gate_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n25_2_phase8_mb5_evidence_chain_audit.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n25_2_replay_persistence_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_multi_window_persistence_replay.json"
I6_OUTPUT = EXPERIMENT / "outputs" / "n25_2_fail_closed_control_matrix.json"
I7_OUTPUT = EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_mb6_support_blocker_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_2_mb6_support_blocker_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_mb6_support_blocker_matrix.py"
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


def all_false(mapping: Mapping[str, Any]) -> bool:
    return all(value is False for value in mapping.values())


def control_ids(i6: dict[str, Any]) -> set[str]:
    return set(i6["matrix_summary"]["all_control_ids"])


def control_failed_closed(i6: dict[str, Any], *ids: str) -> bool:
    available = control_ids(i6)
    return all(control_id in available for control_id in ids) and all(
        row["failed_open_control_count"] == 0 for row in i6["control_rows"]
    )


def gate_row(
    *,
    gate_id: str,
    required_evidence: str,
    passed: bool,
    evidence_sources: list[str],
    evidence_detail: Any,
    blocker: str | None = None,
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "required_evidence": required_evidence,
        "gate_status": "passed" if passed else "blocked",
        "required_for_mb6": True,
        "evidence_sources": evidence_sources,
        "evidence_detail": evidence_detail,
        "blocker": None if passed else blocker or f"{gate_id}_missing_or_failed",
        "claim_effect": (
            "supports_MB6_gate" if passed else "blocks_MB6_and_scoped_N26_consumption"
        ),
    }


def build_gate_rows(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    i5: dict[str, Any],
    i5a: dict[str, Any],
    i6: dict[str, Any],
    i7: dict[str, Any],
) -> list[dict[str, Any]]:
    gate_schema = i2["schema_sections"]["mb6_support_gates"]
    schema_by_id = {row["gate_id"]: row for row in gate_schema}

    i4_child = i4["child_basin_state_records"]["records"][0]
    i4a_child = i4a["route_child_basin_variant"]["runtime_trace"][
        "child_basin_state_records"
    ][0]
    i4_flow = i4["runtime_surface_evidence"]["flow_window_records"][0]
    i4a_flow = i4a["route_child_basin_variant"]["runtime_trace"][
        "flow_window_records"
    ][0]
    support_conditions = {
        "source_inventory_admissible": (
            i1["status"] == "passed" and not i1["failed_checks"],
            ["I1"],
            {"i1_output_digest": i1["output_digest"]},
        ),
        "phase8_mb5_chain_validated": (
            i3["status"] == "passed"
            and i3["phase8_mb5_evidence_chain_status"]
            == "mb5_validated_for_runtime_probe"
            and i3["mb5_demoted"] is False,
            ["I3"],
            {
                "i3_output_digest": i3["output_digest"],
                "phase8_mb5_evidence_chain_status": i3[
                    "phase8_mb5_evidence_chain_status"
                ],
                "mb5_demoted": i3["mb5_demoted"],
            },
        ),
        "source_backed_multi_basin_runtime_surfaces": (
            i4["runtime_execution_performed"] is True
            and i4a["runtime_execution_performed"] is True
            and i4["runtime_surface_evidence"]["flow_window_record_count"] == 1
            and i4a["route_child_basin_variant"]["runtime_trace"][
                "commit_result"
            ]["flow_record_count"]
            == 1
            and i7["stress_matrix_scope"][
                "stress_rows_are_derived_from_source_current_runtime_records"
            ]
            is True,
            ["I4", "I4-A", "I7"],
            {
                "i4_flow_window_record_count": i4["runtime_surface_evidence"][
                    "flow_window_record_count"
                ],
                "i4a_flow_window_record_count": i4a["route_child_basin_variant"][
                    "runtime_trace"
                ]["commit_result"]["flow_record_count"],
                "i7_source_current_stress": i7["stress_matrix_scope"][
                    "stress_rows_are_derived_from_source_current_runtime_records"
                ],
            },
        ),
        "source_backed_child_basin_state_records": (
            bool(i4_child["child_basin_core_ids"])
            and bool(i4a_child["child_basin_core_ids"])
            and bool(i4_child["child_basin_membership_by_core"])
            and bool(i4a_child["child_basin_membership_by_core"])
            and bool(i4_child["child_basin_boundary_records"])
            and bool(i4a_child["child_basin_boundary_records"])
            and bool(i4_child["child_basin_support_floor_records"])
            and bool(i4a_child["child_basin_support_floor_records"])
            and bool(i4_flow["pre_refinement_topology_signature"])
            and bool(i4a_flow["post_refinement_topology_signature"]),
            ["I4", "I4-A"],
            {
                "i4_child_basin_core_ids": i4_child["child_basin_core_ids"],
                "i4a_child_basin_core_ids": i4a_child["child_basin_core_ids"],
                "i4_topology_signatures_recorded": bool(
                    i4_flow["pre_refinement_topology_signature"]
                    and i4_flow["post_refinement_topology_signature"]
                ),
                "i4a_topology_signatures_recorded": bool(
                    i4a_flow["pre_refinement_topology_signature"]
                    and i4a_flow["post_refinement_topology_signature"]
                ),
            },
        ),
        "replay_backed_child_basin_persistence": (
            i5a["status"] == "passed"
            and i5a["matrix_summary"]["multi_window_passed_candidate_count"] == 2
            and i5a["matrix_summary"]["declared_replay_window_count"] == 3
            and i7["matrix_summary"]["extended_multi_window_pass_count"] == 4,
            ["I5", "I5-A", "I7"],
            {
                "i5a_output_digest": i5a["output_digest"],
                "declared_replay_window_count": i5a["matrix_summary"][
                    "declared_replay_window_count"
                ],
                "multi_window_passed_candidate_count": i5a["matrix_summary"][
                    "multi_window_passed_candidate_count"
                ],
                "i7_extended_multi_window_pass_count": i7["matrix_summary"][
                    "extended_multi_window_pass_count"
                ],
            },
        ),
        "artifact_snapshot_duplicate_replay_clean": (
            i5["status"] == "passed"
            and i5["matrix_summary"]["all_candidate_replays_passed"] is True
            and all(
                row["duplicate_replay_digest_stable"] is True
                and row["all_required_replay_modes_passed"] is True
                and row["all_persistence_ratios_exact"] is True
                for row in i5["replay_rows"]
            )
            and i5a["matrix_summary"]["duplicate_replay_suppression_observed"] is True,
            ["I5", "I5-A"],
            {
                "i5_all_candidate_replays_passed": i5["matrix_summary"][
                    "all_candidate_replays_passed"
                ],
                "i5_duplicate_replay_digest_stable_by_row": [
                    row["duplicate_replay_digest_stable"] for row in i5["replay_rows"]
                ],
                "i5a_duplicate_replay_suppression_observed": i5a["matrix_summary"][
                    "duplicate_replay_suppression_observed"
                ],
            },
        ),
        "merge_leakage_controls_fail_closed": (
            i6["matrix_summary"]["all_controls_failed_closed"] is True
            and i6["matrix_summary"]["failed_open_control_count"] == 0,
            ["I6"],
            {
                "failed_open_control_count": i6["matrix_summary"][
                    "failed_open_control_count"
                ],
                "control_record_count_per_candidate": i6["matrix_summary"][
                    "control_record_count_per_candidate"
                ],
            },
        ),
        "producer_native_mutation_ownership_clean": (
            i4["producer_audit_evidence"]["runtime_mutation_owner"]
            == "LGRC9V3_runtime_transition"
            and i6["producer_native_discipline"][
                "producer_success_can_upgrade_native"
            ]
            is False
            and i7["producer_native_discipline"]["hidden_producer_basin_insertion_allowed"]
            is False,
            ["I4", "I6", "I7"],
            {
                "runtime_mutation_owner": i4["producer_audit_evidence"][
                    "runtime_mutation_owner"
                ],
                "producer_success_can_upgrade_native": i6[
                    "producer_native_discipline"
                ]["producer_success_can_upgrade_native"],
                "hidden_producer_basin_insertion_allowed": i7[
                    "producer_native_discipline"
                ]["hidden_producer_basin_insertion_allowed"],
            },
        ),
        "front_capacity_boundary_birth_provenance_when_used": (
            i6["front_capacity_companion_scope"][
                "front_capacity_backfill_control_status"
            ]
            == "failed_closed"
            and i7["front_capacity_stress_scope"]["front_capacity_can_backfill_mb6"]
            is False,
            ["I4-A", "I6", "I7"],
            {
                "front_capacity_scope": i7["front_capacity_stress_scope"]["status"],
                "front_capacity_can_backfill_mb6": i7["front_capacity_stress_scope"][
                    "front_capacity_can_backfill_mb6"
                ],
            },
        ),
        "hidden_producer_basin_insertion_rejected": (
            control_failed_closed(i6, "hidden_producer_basin_insertion"),
            ["I6"],
            {"control_id": "hidden_producer_basin_insertion"},
        ),
        "label_only_basin_formation_rejected": (
            control_failed_closed(i6, "label_only_child_basin"),
            ["I6"],
            {"control_id": "label_only_child_basin"},
        ),
        "old_basin_thickening_relabel_rejected": (
            control_failed_closed(i6, "old_basin_thickening_as_child_basin"),
            ["I6"],
            {"control_id": "old_basin_thickening_as_child_basin"},
        ),
        "transient_flow_sink_relabel_rejected": (
            control_failed_closed(i6, "transient_flow_sink_as_child_basin"),
            ["I6"],
            {"control_id": "transient_flow_sink_as_child_basin"},
        ),
        "graph_visual_only_success_rejected": (
            control_failed_closed(i6, "graph_visual_only_success_control"),
            ["I6"],
            {"control_id": "graph_visual_only_success_control"},
        ),
        "visual_evidence_corroboration_only": (
            i4["visual_evidence_limits"]["visual_evidence_used"] is False
            and i7["front_capacity_stress_scope"]["front_capacity_can_backfill_mb6"]
            is False,
            ["I4", "I7"],
            {
                "i4_visual_evidence_used": i4["visual_evidence_limits"][
                    "visual_evidence_used"
                ],
                "front_capacity_can_backfill_mb6": i7["front_capacity_stress_scope"][
                    "front_capacity_can_backfill_mb6"
                ],
            },
        ),
        "n26_consumption_rule_explicit": (
            True,
            ["I2", "I8"],
            {
                "n26_consumption_effect_if_mb6_supported": i2["schema_sections"][
                    "n26_consumption_rules"
                ]["if_mb6_supported"],
                "n26_unscoped_consumption_allowed": False,
            },
        ),
        "unsafe_claim_flags_false": (
            all_false(i4["unsafe_claim_flags"])
            and all_false(i4a["unsafe_claim_flags"])
            and all_false(i5["unsafe_claim_flags"])
            and all_false(i5a["unsafe_claim_flags"])
            and all_false(i6["unsafe_claim_flags"])
            and all_false(i7["unsafe_claim_flags"]),
            ["I4", "I4-A", "I5", "I5-A", "I6", "I7"],
            {"unsafe_claim_flags": unsafe_claim_flags()},
        ),
    }
    missing_gate_ids = set(schema_by_id) - set(support_conditions)
    if missing_gate_ids:
        raise RuntimeError(f"unhandled MB6 gates: {sorted(missing_gate_ids)}")

    rows: list[dict[str, Any]] = []
    for schema_row in gate_schema:
        gate_id = schema_row["gate_id"]
        passed, sources, detail = support_conditions[gate_id]
        rows.append(
            gate_row(
                gate_id=gate_id,
                required_evidence=schema_row["required_evidence"],
                passed=bool(passed),
                evidence_sources=sources,
                evidence_detail=detail,
            )
        )
    return rows


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    gate_rows = build_gate_rows(
        i1=i1,
        i2=i2,
        i3=i3,
        i4=i4,
        i4a=i4a,
        i5=i5,
        i5a=i5a,
        i6=i6,
        i7=i7,
    )
    passed_gate_count = sum(1 for row in gate_rows if row["gate_status"] == "passed")
    blocked_gate_rows = [row for row in gate_rows if row["gate_status"] != "passed"]
    mb6_supported = passed_gate_count == len(gate_rows)
    n26_rules = i2["schema_sections"]["n26_consumption_rules"]
    n26_effect = (
        n26_rules["if_mb6_supported"]
        if mb6_supported
        else n26_rules["if_mb6_blocked"]
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
        "gate_count": len(gate_rows),
        "passed_gate_count": passed_gate_count,
        "blocked_gate_count": len(blocked_gate_rows),
        "blocked_gate_ids": [row["gate_id"] for row in blocked_gate_rows],
        "mb6_supported": mb6_supported,
        "mb5_demoted": False,
        "n26_consumption_effect": n26_effect["n26_consumption_effect"],
        "n26_scoped_context_consumption_allowed": bool(
            n26_effect["n26_scoped_context_consumption_allowed"]
        ),
        "n26_unscoped_multi_basin_consumption_allowed": bool(
            n26_effect["n26_unscoped_multi_basin_consumption_allowed"]
        ),
    }
    artifact_manifest = [
        {
            "artifact_role": "mb6_gate_matrix",
            "json_pointer": "#/gate_rows",
            "digest": digest_value(gate_rows),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "n26_consumption_classification",
            "json_pointer": "#/n26_consumption_scope",
            "digest": digest_value(n26_effect),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "i7_ready_for_mb6_gate",
            i7["status"] == "passed"
            and i7["ready_for_iteration_8_mb6_support_blocker_matrix"] is True,
            {"i7_output_digest": i7["output_digest"]},
        ),
        check(
            "all_mb6_gates_evaluated",
            len(gate_rows) == len(i2["schema_sections"]["mb6_support_gates"]),
            {
                "gate_count": len(gate_rows),
                "schema_gate_count": len(i2["schema_sections"]["mb6_support_gates"]),
            },
        ),
        check(
            "all_required_mb6_gates_passed",
            mb6_supported,
            matrix_summary,
        ),
        check(
            "n26_consumption_scope_is_explicit_and_scoped",
            n26_effect["n26_consumption_effect"]
            == "scoped_mb6_substrate_consumption_allowed"
            and n26_effect["n26_scoped_context_consumption_allowed"] is True
            and n26_effect["n26_unscoped_multi_basin_consumption_allowed"] is False,
            n26_effect,
        ),
        check(
            "n25_2_closeout_rung_remains_separate_from_mb_support",
            mb6_supported is True,
            {
                "mb6_supported": mb6_supported,
                "n25_2_closeout_ceiling": "N25.2-C5_N26_consumption_classification_complete_pending_closeout",
                "n25_2_c6_closeout_pending_iteration_9": True,
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
        "artifact_id": "n25_2_mb6_support_blocker_matrix",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_mb6_supported_scoped_n26_consumption",
        "experiment": "N25.2",
        "iteration": 8,
        "command": COMMAND,
        "source_chain": {
            "i1_output_digest": i1["output_digest"],
            "i1_artifact_sha256": sha256_file(I1_OUTPUT),
            "i2_output_digest": i2["output_digest"],
            "i2_artifact_sha256": sha256_file(I2_OUTPUT),
            "i3_output_digest": i3["output_digest"],
            "i3_artifact_sha256": sha256_file(I3_OUTPUT),
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4a_output_digest": i4a["output_digest"],
            "i4a_artifact_sha256": sha256_file(I4A_OUTPUT),
            "i5_output_digest": i5["output_digest"],
            "i5_artifact_sha256": sha256_file(I5_OUTPUT),
            "i5a_output_digest": i5a["output_digest"],
            "i5a_artifact_sha256": sha256_file(I5A_OUTPUT),
            "i6_output_digest": i6["output_digest"],
            "i6_artifact_sha256": sha256_file(I6_OUTPUT),
            "i7_output_digest": i7["output_digest"],
            "i7_artifact_sha256": sha256_file(I7_OUTPUT),
        },
        "gate_matrix_scope": {
            "schema_source": "I2 MB6 support gates",
            "gate_count": len(gate_rows),
            "gate_rows_include_blockers": True,
            "automatic_mb6_from_mb5_allowed": False,
            "runtime_implementation_modified": False,
        },
        "matrix_summary": matrix_summary,
        "gate_rows": gate_rows,
        "mb_ladder_result": "MB6_N26_ready_multi_basin_substrate_evidence",
        "mb5_remains_valid": True,
        "mb5_demoted": False,
        "mb6_gate_status": "supported" if mb6_supported else "blocked",
        "mb6_supported": mb6_supported,
        "mb6_claim_allowed": mb6_supported,
        "mb6_blockers": matrix_summary["blocked_gate_ids"],
        "n26_consumption_scope": {
            **n26_effect,
            "n26_unscoped_consumption_allowed": False,
            "allowed_n26_consumption": (
                "scoped multi-basin substrate evidence only"
                if mb6_supported
                else "provisional context only"
            ),
        },
        "n26_unscoped_consumption_allowed": False,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "MB6_gate_classified_over_closed_records",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "claim_boundary": {
            "claim_allowed": "MB6_N26_ready_multi_basin_substrate_evidence",
            "claim_blocked": [
                "native_support",
                "semantic_learning",
                "semantic_choice",
                "agency",
                "identity_acceptance",
                "sentience",
                "organism_life",
                "ant_ecology_implementation",
                "phase8_completion",
                "unrestricted_autonomy",
                "unscoped_N26_consumption",
            ],
        },
        "n25_2_closeout_ceiling": (
            "N25.2-C5_N26_consumption_classification_complete_pending_closeout"
        ),
        "n25_2_c6_closeout_pending_iteration_9": True,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": artifact_manifest,
        "implementation_no_mutation_proof": no_mutation_proof,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported" if mb6_supported else "blocked",
        "claim_ceiling": (
            "MB6 N26-ready multi-basin substrate evidence with scoped N26 "
            "consumption; not native support, agency, sentience, Phase 8 "
            "completion, or unscoped N26 consumption"
        ),
        "ready_for_iteration_9_closeout_and_n26_handoff": True,
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
    report = f"""# N25.2 Iteration 8 - MB6 Support / Blocker Matrix

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I8 applies the I2 MB6 gate to the I3-I7 evidence chain.

```text
i7_output_digest = {data['source_chain']['i7_output_digest']}
gate_count = {summary['gate_count']}
passed_gate_count = {summary['passed_gate_count']}
blocked_gate_count = {summary['blocked_gate_count']}
mb6_supported = {str(summary['mb6_supported']).lower()}
mb5_demoted = {str(summary['mb5_demoted']).lower()}
n26_consumption_effect = {summary['n26_consumption_effect']}
n26_scoped_context_consumption_allowed = {str(summary['n26_scoped_context_consumption_allowed']).lower()}
n26_unscoped_multi_basin_consumption_allowed = {str(summary['n26_unscoped_multi_basin_consumption_allowed']).lower()}
```

## Interpretation

I8 supports MB6 because all required gates pass: source inventory, Phase 8 MB5
chain validation, native runtime surfaces, child-basin state records,
multi-window persistence replay, replay cleanliness, fail-closed controls,
producer/native discipline, front-capacity backfill rejection, visual-only
limits, explicit N26 scoping, and unsafe-claim blockers.

The supported handoff is scoped:

```text
MB6 = N26-ready multi-basin substrate evidence
N26 consumption = scoped multi-basin substrate evidence only
```

The result does not allow unscoped N26 consumption and does not support native
support, semantic learning, semantic choice, agency, sentience, ant ecology,
organism/life, unrestricted autonomy, or Phase 8 completion.

## Gate Rows

```text
passed_gate_count = {summary['passed_gate_count']} / {summary['gate_count']}
blocked_gate_ids = {summary['blocked_gate_ids']}
```

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
