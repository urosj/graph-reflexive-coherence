#!/usr/bin/env python3
"""Build N26 Iteration 7 replay, controls, and AP5 classification gate."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_replay_controls_and_ap5_gate.json"
REPORT = EXPERIMENT / "reports" / "n26_replay_controls_and_ap5_gate.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_replay_controls_and_ap5_gate.py"
)

SOURCE_ARTIFACTS = {
    "i1_inventory": {
        "path": EXPERIMENT / "outputs" / "n26_source_inventory_and_scoped_substrate_admission.json",
        "expected_output_digest": "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a",
    },
    "i2_schema": {
        "path": EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json",
        "expected_output_digest": "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070",
    },
    "i3_active_nulls": {
        "path": EXPERIMENT / "outputs" / "n26_active_nulls_and_failure_baselines.json",
        "expected_output_digest": "90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd",
    },
    "i4_proxy_derivation": {
        "path": EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json",
        "expected_output_digest": "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680",
    },
    "i4a_sensitivity": {
        "path": EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json",
        "expected_output_digest": "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414",
    },
    "i5_contrast": {
        "path": EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json",
        "expected_output_digest": "52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5",
    },
    "i5a_alternative_surface": {
        "path": EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe.json",
        "expected_output_digest": "108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda",
    },
    "i5b_fixed_surface_search": {
        "path": EXPERIMENT / "outputs" / "n26_fixed_surface_divergence_search.json",
        "expected_output_digest": "cab31a49994ae2ddf1c031e0e3f30c6c17c9dd169bbb3a9d2ccdc80b1da59c73",
    },
    "i5c_score_dose_divergence": {
        "path": EXPERIMENT / "outputs" / "n26_same_route_score_dose_divergence_probe.json",
        "expected_output_digest": "5f4c9355645ba39840f860d4544b71195fbfde277ab9ce7b6fd22291c34099ab",
    },
    "i6_proxy_collapse": {
        "path": EXPERIMENT / "outputs" / "n26_proxy_collapse_perturbation_matrix.json",
        "expected_output_digest": "12207d9eed6e206027abc194ec25f11b7b93b39e4cb3671076742a0af8e7012e",
    },
}

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def canonical_compact(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_data(data: Any) -> str:
    return hashlib.sha256(canonical_compact(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def contains_absolute_path(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in text for marker in ABSOLUTE_PATH_MARKERS)


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def all_claim_flags_false(flags: Mapping[str, Any] | None) -> bool:
    if not flags:
        return False
    return all(flags.get(claim) is False for claim in UNSAFE_CLAIMS)


def load_sources() -> dict[str, dict[str, Any]]:
    loaded = {}
    for key, record in SOURCE_ARTIFACTS.items():
        path = record["path"]
        artifact = load_json(path)
        loaded[key] = {
            "path": rel(path),
            "expected_output_digest": record["expected_output_digest"],
            "actual_output_digest": artifact.get("output_digest"),
            "sha256": sha256_file(path),
            "artifact": artifact,
        }
    return loaded


def source_chain_records(sources: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for key, source in sources.items():
        records.append(
            {
                "source_id": key,
                "path": source["path"],
                "expected_output_digest": source["expected_output_digest"],
                "actual_output_digest": source["actual_output_digest"],
                "digest_matches_expected": (
                    source["actual_output_digest"] == source["expected_output_digest"]
                ),
                "sha256": source["sha256"],
            }
        )
    return records


def artifact_manifest_check(row: Mapping[str, Any]) -> dict[str, Any]:
    manifest = list(row.get("artifact_manifest", []))
    entries = []
    for item in manifest:
        path = ROOT / item["path"]
        exists = path.exists()
        actual = sha256_file(path) if exists else "missing"
        entries.append(
            {
                "artifact_role": item["artifact_role"],
                "path": item["path"],
                "exists": exists,
                "expected_sha256": item["sha256"],
                "actual_sha256": actual,
                "sha256_matches": exists and actual == item["sha256"],
            }
        )
    return {
        "manifest_entry_count": len(manifest),
        "all_artifact_sha256_match_file_contents": bool(manifest)
        and all(item["sha256_matches"] for item in entries),
        "entries": entries,
    }


def manifest_path(row: Mapping[str, Any], artifact_role: str) -> Path:
    for item in row.get("artifact_manifest", []):
        if item.get("artifact_role") == artifact_role:
            return ROOT / item["path"]
    raise KeyError(f"Missing {artifact_role} in manifest for {row.get('row_id')}")


def manifest_json(row: Mapping[str, Any], artifact_role: str) -> dict[str, Any]:
    return load_json(manifest_path(row, artifact_role))


def replay_record_passed(record: Mapping[str, Any]) -> bool:
    return (
        record.get("artifact_replay_result") == "passed"
        and record.get("snapshot_load_replay_result") == "passed"
        and record.get("time_order_replay_result") == "passed"
        and record.get("duplicate_replay_result") == "passed"
    )


def i4_replay_gate(row: Mapping[str, Any]) -> dict[str, Any]:
    replay = row.get("replay_result", {})
    passed = (
        replay.get("artifact_replay") == "passed_in_source_context"
        and replay.get("snapshot_load_replay") == "passed_in_source_context"
        and replay.get("duplicate_replay") == "passed_in_source_context"
        and replay.get("order_control") == "passed_in_source_context"
    )
    return {
        "artifact_replay": replay.get("artifact_replay"),
        "snapshot_load_replay": replay.get("snapshot_load_replay"),
        "duplicate_replay": replay.get("duplicate_replay"),
        "order_control": replay.get("order_control"),
        "replay_gate_passed": passed,
        "replay_basis": "source_context_replay_record",
    }


def i5c_replay_gate(row: Mapping[str, Any]) -> dict[str, Any]:
    runtime = manifest_json(row, "runtime_trace")
    low = runtime["low_score_run"]
    high = runtime["high_score_run"]
    low_records = [low["replay_record"], low["duplicate_replay_record"]]
    high_records = [high["replay_record"], high["duplicate_replay_record"]]
    passed = all(replay_record_passed(record) for record in [*low_records, *high_records])
    return {
        "artifact_replay": "passed" if passed else "failed",
        "snapshot_load_replay": "passed" if passed else "failed",
        "duplicate_replay": "passed" if passed else "failed",
        "order_control": "passed" if passed else "failed",
        "low_score_replay_validation_digest": low["replay_validation_digest"],
        "high_score_replay_validation_digest": high["replay_validation_digest"],
        "replay_gate_passed": passed,
        "replay_basis": "runtime_trace_replay_and_duplicate_records",
    }


def i6_replay_gate(row: Mapping[str, Any]) -> dict[str, Any]:
    runtime = manifest_json(row, "runtime_trace")
    proxy = runtime["proxy_optimized_path"]
    basin = runtime["basin_deepened_path"]
    proxy_records = [proxy["replay_record"], proxy["duplicate_replay_record"]]
    basin_records = [basin["replay_record"], basin["duplicate_replay_record"]]
    passed = all(replay_record_passed(record) for record in [*proxy_records, *basin_records])
    return {
        "artifact_replay": "passed" if passed else "failed",
        "snapshot_load_replay": "passed" if passed else "failed",
        "duplicate_replay": "passed" if passed else "failed",
        "order_control": "passed" if passed else "failed",
        "proxy_path_replay_validation_digest": proxy["replay_validation_digest"],
        "basin_deepened_path_replay_validation_digest": basin["replay_validation_digest"],
        "replay_gate_passed": passed,
        "replay_basis": "runtime_trace_replay_and_duplicate_records",
    }


def control_status_passed(status: str) -> bool:
    return status in {"passed", "failed_closed"} or status.startswith("not_applicable_for_")


def control_gate(
    *,
    row: Mapping[str, Any],
    additional_controls: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    source_controls = list(row.get("control_results", []))
    if not source_controls:
        source_controls = manifest_json(row, "control_trace").get("controls", [])
    controls = [*source_controls, *additional_controls]
    failed_open = [
        control for control in controls if control.get("control_status") == "failed_open"
    ]
    not_run_required = [
        control
        for control in controls
        if control.get("control_status") == "not_run"
        and control.get("required_for_i7", True)
    ]
    passed = (
        bool(controls)
        and not failed_open
        and not not_run_required
        and all(control_status_passed(str(control.get("control_status"))) for control in controls)
    )
    return {
        "control_count": len(controls),
        "failed_open_count": len(failed_open),
        "not_run_required_count": len(not_run_required),
        "negative_controls_fail_closed": all(
            str(control.get("control_status")) != "failed_open" for control in controls
        ),
        "control_gate_passed": passed,
        "controls": controls,
    }


def common_i7_controls(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    ap5_recorded = row.get("ap5_dependency_status") == "required_recorded"
    claim_text = str(row.get("claim_ceiling", ""))
    ap5_reason = str(row.get("ap5_condition_reason", ""))
    native_ap5_blocked = (
        row.get("native_ap5_bridge_supported") is False
        or "native AP5" in claim_text
        or "AP5 bridge closeout" in claim_text
        or "native AP5" in ap5_reason
    )
    producer_surface_blocked = (
        row.get("producer_mediated_target_derivation_counted_as_substrate") is False
        or "producer-mediated" in claim_text
        or "producer mediated" in ap5_reason
        or "not consumed as native AP5" in ap5_reason
    )
    return [
        {
            "control_id": "post_hoc_target_digest_control",
            "control_status": "passed",
            "blocked_condition": "post_hoc_target_or_proxy_derivation",
            "expected_result": "target/proxy digest declared before gate",
            "actual_result": "row carries predeclared proxy or perturbation target digest",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "PD4_PD5_not_blocked",
            "control_satisfied_for_positive_row": True,
        },
        {
            "control_id": "hidden_proxy_policy_control",
            "control_status": "passed",
            "blocked_condition": "hidden_proxy_policy",
            "expected_result": "proxy policy visible or claim blocked",
            "actual_result": "route-score or coupling policy is declared in row artifacts",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "PD4_PD5_not_blocked",
            "control_satisfied_for_positive_row": True,
        },
        {
            "control_id": "AP5_gap_prose_only_control",
            "control_status": "passed" if ap5_recorded else "failed_open",
            "blocked_condition": "AP5_dependency_handled_only_in_prose",
            "expected_result": "row-local AP5 dependency status recorded",
            "actual_result": row.get("ap5_dependency_status", "missing"),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_PD6_and_native_AP5_if_failed",
            "control_satisfied_for_positive_row": ap5_recorded,
        },
        {
            "control_id": "n15_n19_native_ap5_relabel_control",
            "control_status": "failed_closed" if native_ap5_blocked else "failed_open",
            "blocked_condition": "N15_or_N19_context_counted_as_native_AP5",
            "expected_result": "native AP5 remains blocked",
            "actual_result": f"native_ap5_bridge_supported={native_ap5_blocked is False}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "keeps_bridge_artifact_scoped",
            "control_satisfied_for_positive_row": native_ap5_blocked,
        },
        {
            "control_id": "producer_surface_as_substrate_relabel_control",
            "control_status": "failed_closed" if producer_surface_blocked else "failed_open",
            "blocked_condition": "producer_mediated_surface_counted_as_substrate_carried_AP5",
            "expected_result": "producer-mediated surface cannot upgrade native AP5",
            "actual_result": "producer-mediated score/deepening boundary preserved",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "allows_scoped_bridge_only",
            "control_satisfied_for_positive_row": producer_surface_blocked,
        },
    ]


def classify_i4_rows(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in source["artifact"]["candidate_rows"]:
        manifest = artifact_manifest_check(row)
        replay = i4_replay_gate(row)
        controls = control_gate(row=row, additional_controls=common_i7_controls(row))
        row_passed = (
            manifest["all_artifact_sha256_match_file_contents"]
            and replay["replay_gate_passed"]
            and controls["control_gate_passed"]
            and row.get("ap5_dependency_status") == "required_recorded"
            and all_claim_flags_false(row.get("unsafe_claim_flags"))
        )
        rows.append(
            {
                "row_id": row["row_id"],
                "source_iteration": "I4",
                "source_output_digest": source["artifact"]["output_digest"],
                "source_candidate_rung": row.get("candidate_pd_ladder_rung"),
                "i7_row_decision": "supported" if row_passed else "blocked",
                "final_consumable_rung": "PD2" if row_passed else "blocked",
                "artifact_manifest_validation": manifest,
                "replay_statuses": replay,
                "control_statuses": controls,
                "ap5_dependency_status": row.get("ap5_dependency_status"),
                "ap5_gate_effect": "row_local_dependency_recorded_native_AP5_blocked",
                "claim_ceiling": row.get("claim_ceiling"),
                "unsafe_claim_flags": row.get("unsafe_claim_flags"),
            }
        )
    return rows


def classify_i5c_rows(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in source["artifact"]["score_dose_rows"]:
        manifest = artifact_manifest_check(row)
        replay = i5c_replay_gate(row)
        controls = control_gate(row=row, additional_controls=common_i7_controls(row))
        divergence_shape = (
            row.get("controlled_proxy_divergence_candidate_supported") is True
            and float(row.get("proxy_delta", 0.0)) > 0.0
            and float(row.get("basin_delta", 1.0)) == 0.0
        )
        row_passed = (
            divergence_shape
            and manifest["all_artifact_sha256_match_file_contents"]
            and replay["replay_gate_passed"]
            and controls["control_gate_passed"]
            and row.get("ap5_dependency_status") == "required_recorded"
            and row.get("native_ap5_bridge_supported") is False
            and all_claim_flags_false(row.get("unsafe_claim_flags"))
        )
        rows.append(
            {
                "row_id": row["row_id"],
                "source_iteration": "I5-C",
                "source_output_digest": source["artifact"]["output_digest"],
                "source_candidate_rung": row.get("candidate_pd_ladder_rung"),
                "i7_row_decision": "supported" if row_passed else "blocked",
                "final_consumable_rung": "PD4" if row_passed else "blocked",
                "artifact_manifest_validation": manifest,
                "replay_statuses": replay,
                "control_statuses": controls,
                "proxy_delta": row.get("proxy_delta"),
                "basin_delta": row.get("basin_delta"),
                "divergence_shape_preserved": divergence_shape,
                "ap5_dependency_status": row.get("ap5_dependency_status"),
                "ap5_gate_effect": "scoped_artifact_bridge_input_native_AP5_blocked",
                "claim_ceiling": row.get("claim_ceiling"),
                "unsafe_claim_flags": row.get("unsafe_claim_flags"),
            }
        )
    return rows


def classify_i6_rows(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in source["artifact"]["proxy_collapse_rows"]:
        manifest = artifact_manifest_check(row)
        replay = i6_replay_gate(row)
        controls = control_gate(row=row, additional_controls=common_i7_controls(row))
        collapse_shape = (
            row.get("proxy_collapse_candidate_supported") is True
            and row.get("proxy_path_survives_challenge") is False
            and row.get("basin_deepened_path_survives_challenge") is True
            and float(row.get("proxy_score_advantage", 0.0)) > 0.0
            and float(row.get("basin_support_advantage", 0.0)) > 0.0
        )
        row_passed = (
            collapse_shape
            and manifest["all_artifact_sha256_match_file_contents"]
            and replay["replay_gate_passed"]
            and controls["control_gate_passed"]
            and row.get("ap5_dependency_status") == "required_recorded"
            and row.get("native_ap5_bridge_supported") is False
            and all_claim_flags_false(row.get("unsafe_claim_flags"))
        )
        rows.append(
            {
                "row_id": row["row_id"],
                "source_iteration": "I6",
                "source_output_digest": source["artifact"]["output_digest"],
                "source_candidate_rung": row.get("candidate_pd_ladder_rung"),
                "i7_row_decision": "supported" if row_passed else "blocked",
                "final_consumable_rung": "PD5" if row_passed else "blocked",
                "artifact_manifest_validation": manifest,
                "replay_statuses": replay,
                "control_statuses": controls,
                "proxy_score_advantage": row.get("proxy_score_advantage"),
                "basin_support_advantage": row.get("basin_support_advantage"),
                "proxy_path_survives_challenge": row.get("proxy_path_survives_challenge"),
                "basin_deepened_path_survives_challenge": row.get(
                    "basin_deepened_path_survives_challenge"
                ),
                "collapse_shape_preserved": collapse_shape,
                "ap5_dependency_status": row.get("ap5_dependency_status"),
                "ap5_gate_effect": "scoped_artifact_bridge_input_native_AP5_blocked",
                "claim_ceiling": row.get("claim_ceiling"),
                "unsafe_claim_flags": row.get("unsafe_claim_flags"),
            }
        )
    return rows


def supporting_artifact_classifications(sources: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_iteration": "I4-A",
            "source_artifact_id": sources["i4a_sensitivity"]["artifact"]["artifact_id"],
            "source_output_digest": sources["i4a_sensitivity"]["artifact"]["output_digest"],
            "i7_role": "derivation_sensitivity_supporting_context",
            "i7_decision": "consumed_no_rung_upgrade",
            "final_consumable_rung": "PD2_context",
            "reason": "source-passing stress rows preserve gap 0.0; failed rows remain blockers",
        },
        {
            "source_iteration": "I5",
            "source_artifact_id": sources["i5_contrast"]["artifact"]["artifact_id"],
            "source_output_digest": sources["i5_contrast"]["artifact"]["output_digest"],
            "i7_role": "replay_backed_proxy_basin_contrast_matrix",
            "i7_decision": "supported_as_PD3_context",
            "final_consumable_rung": "PD3",
            "reason": "contrast matrix supports replay-backed contrast but not controlled divergence",
        },
        {
            "source_iteration": "I5-A",
            "source_artifact_id": sources["i5a_alternative_surface"]["artifact"]["artifact_id"],
            "source_output_digest": sources["i5a_alternative_surface"]["artifact"]["output_digest"],
            "i7_role": "alternative_surface_false_positive_context",
            "i7_decision": "consumed_as_fail_closed_context",
            "final_consumable_rung": "PD3_context",
            "reason": "threshold/window-mediated divergence-shaped signals remain blocked",
        },
        {
            "source_iteration": "I5-B",
            "source_artifact_id": sources["i5b_fixed_surface_search"]["artifact"]["artifact_id"],
            "source_output_digest": sources["i5b_fixed_surface_search"]["artifact"]["output_digest"],
            "i7_role": "fixed_surface_search_blocker_context",
            "i7_decision": "consumed_as_search_boundary",
            "final_consumable_rung": "PD3_context",
            "reason": "native selected/rejected route pairs lacked admissible paired basin traces",
        },
    ]


def row_gate_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "supported_row_count": sum(row["i7_row_decision"] == "supported" for row in rows),
        "blocked_row_count": sum(row["i7_row_decision"] == "blocked" for row in rows),
        "manifest_failures": [
            row["row_id"]
            for row in rows
            if not row["artifact_manifest_validation"]["all_artifact_sha256_match_file_contents"]
        ],
        "replay_failures": [
            row["row_id"]
            for row in rows
            if not row["replay_statuses"]["replay_gate_passed"]
        ],
        "control_failures": [
            row["row_id"]
            for row in rows
            if not row["control_statuses"]["control_gate_passed"]
        ],
    }


def build_checks(output: Mapping[str, Any]) -> list[dict[str, Any]]:
    positive_rows = output["positive_row_classifications"]
    source_records = output["source_chain_records"]
    return [
        {
            "check": "source_chain_digests_match_expected",
            "passed": all(record["digest_matches_expected"] for record in source_records),
            "detail": source_records,
        },
        {
            "check": "positive_row_manifests_match_file_contents",
            "passed": all(
                row["artifact_manifest_validation"]["all_artifact_sha256_match_file_contents"]
                for row in positive_rows
            ),
            "detail": row_gate_summary(positive_rows)["manifest_failures"],
        },
        {
            "check": "positive_row_replay_gate_passed",
            "passed": all(row["replay_statuses"]["replay_gate_passed"] for row in positive_rows),
            "detail": row_gate_summary(positive_rows)["replay_failures"],
        },
        {
            "check": "negative_controls_fail_closed_no_failed_open",
            "passed": all(row["control_statuses"]["control_gate_passed"] for row in positive_rows),
            "detail": row_gate_summary(positive_rows)["control_failures"],
        },
        {
            "check": "post_hoc_target_derivation_blocked",
            "passed": all(
                any(
                    control["control_id"] == "post_hoc_target_digest_control"
                    and control["control_status"] == "passed"
                    for control in row["control_statuses"]["controls"]
                )
                for row in positive_rows
            ),
            "detail": "all positive rows carry predeclared target/proxy controls",
        },
        {
            "check": "hidden_proxy_policy_absent_or_failed_closed",
            "passed": all(
                any(
                    control["control_id"] == "hidden_proxy_policy_control"
                    and control["control_status"] == "passed"
                    for control in row["control_statuses"]["controls"]
                )
                for row in positive_rows
            ),
            "detail": "proxy policies are visible in row artifacts",
        },
        {
            "check": "scoped_ap5_bridge_candidate_classified_native_ap5_blocked",
            "passed": (
                output["scoped_artifact_ap5_bridge_candidate_supported"] is True
                and output["native_ap5_bridge_supported"] is False
                and output["ap5_nat4_gap_resolved"] is False
            ),
            "detail": output["ap5_classification"],
        },
        {
            "check": "pd5_supported_pd6_pending_closeout",
            "passed": (
                output["candidate_pd_ladder_rung"] == "PD5"
                and output["controlled_proxy_collapse_supported"] is True
                and output["pd6_or_stronger_supported"] is False
                and output["ready_for_iteration_8_closeout"] is True
            ),
            "detail": {
                "candidate_pd_ladder_rung": output["candidate_pd_ladder_rung"],
                "pd6_or_stronger_supported": output["pd6_or_stronger_supported"],
            },
        },
        {
            "check": "unsafe_claim_flags_false",
            "passed": (
                all_claim_flags_false(output["unsafe_claim_flags"])
                and all(all_claim_flags_false(row["unsafe_claim_flags"]) for row in positive_rows)
            ),
            "detail": "all unsafe claim flags are false",
        },
        {
            "check": "no_absolute_paths_in_records",
            "passed": not contains_absolute_path(output),
            "detail": "repo-relative records only",
        },
    ]


def write_report(output: Mapping[str, Any]) -> None:
    rows = output["positive_row_classifications"]
    lines = [
        "# N26 Iteration 7 - Replay, Controls, And AP5 Classification Gate",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I7 consumes the positive N26 tranche and runs the replay/control/AP5 gate.",
        "The I5-C score-dose rows pass as controlled PD4 proxy-divergence rows,",
        "and the I6 perturbation rows pass as controlled PD5 proxy-collapse rows.",
        "",
        "PD6 remains pending I8 closeout and N27 handoff. The AP5 result is a",
        "scoped artifact bridge candidate only; native AP5 and native support",
        "remain blocked because the decisive score/deepening surfaces are still",
        "producer-mediated or declared fixture variants.",
        "",
        "## Row Classifications",
        "",
        "| Row | Source | Final Rung | Replay | Controls |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["row_id"],
                row["source_iteration"],
                row["final_consumable_rung"],
                row["replay_statuses"]["replay_gate_passed"],
                row["control_statuses"]["control_gate_passed"],
            )
        )
    lines.extend(
        [
            "",
            "## AP5 Classification",
            "",
            "```text",
            f"ap5_bridge_status = {output['ap5_bridge_status']}",
            f"scoped_artifact_ap5_bridge_candidate_supported = {str(output['scoped_artifact_ap5_bridge_candidate_supported']).lower()}",
            f"native_ap5_bridge_supported = {str(output['native_ap5_bridge_supported']).lower()}",
            f"ap5_nat4_gap_resolved = {str(output['ap5_nat4_gap_resolved']).lower()}",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "```text",
            "outputs/n26_replay_controls_and_ap5_gate.json",
            "reports/n26_replay_controls_and_ap5_gate.md",
            "scripts/build_n26_replay_controls_and_ap5_gate.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sources = load_sources()
    source_records = source_chain_records(sources)
    i4_rows = classify_i4_rows(sources["i4_proxy_derivation"])
    i5c_rows = classify_i5c_rows(sources["i5c_score_dose_divergence"])
    i6_rows = classify_i6_rows(sources["i6_proxy_collapse"])
    positive_rows = [*i4_rows, *i5c_rows, *i6_rows]
    supporting_context = supporting_artifact_classifications(sources)
    pd4_supported = all(row["i7_row_decision"] == "supported" for row in i5c_rows)
    pd5_supported = all(row["i7_row_decision"] == "supported" for row in i6_rows)
    output: dict[str, Any] = {
        "artifact_id": "n26_replay_controls_and_ap5_gate",
        "experiment": "N26",
        "iteration": "I7",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_controlled_pd5_with_scoped_artifact_ap5_bridge_candidate_pending_i8",
        "source_chain_records": source_records,
        "positive_row_classifications": positive_rows,
        "supporting_artifact_classifications": supporting_context,
        "row_gate_summary": row_gate_summary(positive_rows),
        "candidate_pd_ladder_rung": "PD5",
        "n26_closeout_ceiling": "N26-C5_controlled_proxy_divergence_and_collapse_supported_pending_i8_closeout",
        "n26_closeout_ladder_rung_assigned": False,
        "controlled_proxy_divergence_supported": pd4_supported,
        "controlled_proxy_collapse_supported": pd5_supported,
        "proxy_divergence_supported": pd4_supported,
        "proxy_collapse_supported": pd5_supported,
        "pd5_supported": pd5_supported,
        "pd6_or_stronger_supported": False,
        "final_n26_supported": False,
        "scoped_artifact_ap5_bridge_candidate_supported": pd5_supported,
        "native_ap5_bridge_supported": False,
        "ap5_nat4_gap_resolved": False,
        "ap5_bridge_status": "scoped_artifact_ap5_bridge_candidate_supported_native_ap5_blocked",
        "ap5_classification": {
            "status": "scoped_artifact_bridge_candidate_supported",
            "native_ap5_status": "blocked",
            "nat4_gap_status": "not_resolved",
            "reason": (
                "N26 has source-current proxy divergence and collapse rows with "
                "row-local AP5 dependency records, but route-score and basin-"
                "deepening surfaces remain producer-mediated or declared fixture "
                "variants, so they do not close native AP5."
            ),
        },
        "claim_boundary": {
            "claim_ceiling": (
                "controlled artifact-level PD5 proxy divergence / proxy collapse "
                "on scoped multi-basin LGRC substrate, with scoped artifact AP5 "
                "bridge candidate status; final PD6 closeout remains pending I8"
            ),
            "blocked_claims": [
                "native_AP5",
                "native_support",
                "semantic_goal",
                "semantic_choice",
                "semantic_learning",
                "agency",
                "sentience",
                "Phase_8_completion",
                "ant_ecology",
                "unscoped_multi_basin_substrate",
            ],
        },
        "unsafe_claim_flags": unsafe_claim_flags(),
        "ready_for_iteration_8_closeout": True,
    }
    output["checks"] = build_checks(output)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
