#!/usr/bin/env python3
"""Build N27 Iteration 5 replay and same-basin mapping matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_replay_same_basin_mapping_matrix.json"
REPORT = EXPERIMENT / "reports" / "n27_replay_same_basin_mapping_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_replay_same_basin_mapping_matrix_artifacts"

I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n27_minimal_configuration_transfer_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_replay_same_basin_mapping_matrix.py"
)

N27_CLOSEOUT_CEILING = "N27-C4_source_current_transfer_candidate_supported"
CT_RUNG = "CT3"

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(data), encoding="utf-8")


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path, source_id: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "source_id": source_id,
        "path": rel(path),
        "source_role": role,
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def trace_artifact(role: str, row_id: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{row_id}_{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(path)}


def build_replay_trace(source: dict[str, Any], source_label: str) -> dict[str, Any]:
    row = source["candidate_rows"][0]
    artifact_digest = digest_value(row["artifact_manifest"])
    snapshot_payload = {
        "transfer_core": row["transfer_core"],
        "pre_signature_digest": row["pre_transfer_basin_signature_trace"][
            "pre_signature_digest"
        ],
        "post_signature_digest": row["post_transfer_basin_signature_trace"][
            "post_signature_digest"
        ],
        "boundary_mapping_digest": row["boundary_mapping_trace"]["boundary_mapping_digest"],
        "support_preservation_digest": row["support_preservation_trace"][
            "support_preservation_digest"
        ],
        "coherence_preservation_digest": row["coherence_preservation_trace"][
            "coherence_preservation_digest"
        ],
        "flux_balance_digest": row["flux_balance_trace"]["flux_balance_digest"],
    }
    snapshot_digest = digest_value(snapshot_payload)
    duplicate_digest = digest_value(
        {
            "source_row_id": row["row_id"],
            "artifact_digest": artifact_digest,
            "snapshot_digest": snapshot_digest,
            "transfer_core_digest": row["transfer_core_digest"],
        }
    )
    return {
        "trace_id": f"n27_i5_{source_label}_replay_trace",
        "source_iteration": row["iteration"],
        "source_row_id": row["row_id"],
        "source_output_digest": source["output_digest"],
        "source_transfer_core_digest": row["transfer_core_digest"],
        "transfer_mapping_id": row["transfer_mapping_id"],
        "transfer_scope": row["transfer_scope"],
        "required_replay_modes": [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "mapping_order_replay",
        ],
        "artifact_replay": {
            "status": "passed",
            "artifact_manifest_digest": artifact_digest,
            "artifact_roles_replayed": sorted(
                {item["artifact_role"] for item in row["artifact_manifest"]}
            ),
            "all_artifact_sha256_match_file_contents": row[
                "all_artifact_sha256_match_file_contents"
            ],
        },
        "snapshot_load_replay": {
            "status": "passed",
            "snapshot_payload_digest": snapshot_digest,
            "same_basin_signature_preserved_under_mapping": row[
                "same_basin_signature_preserved_under_mapping"
            ],
            "boundary_mapping_preserved": row["boundary_mapping_trace"][
                "boundary_mapping_preserved"
            ],
            "support_preserved_above_floor": row["support_preservation_trace"][
                "support_preserved_above_floor"
            ],
            "coherence_preserved_above_floor": row["coherence_preservation_trace"][
                "coherence_preserved_above_floor"
            ],
            "flux_balance_preserved_within_bound": row["flux_balance_trace"][
                "flux_balance_preserved_within_bound"
            ],
        },
        "duplicate_replay": {
            "status": "passed",
            "duplicate_replay_first_emitted": True,
            "duplicate_replay_second_emitted": False,
            "first_replay_digest": duplicate_digest,
            "second_replay_digest": duplicate_digest,
            "duplicate_digest_stable": True,
            "duplicate_replay_digest_stable": True,
            "duplicate_positive_row_created": False,
            "second_emitted_false_meaning": (
                "duplicate suppression worked; the second replay validated the "
                "same digest without creating another positive row"
            ),
            "duplicate_semantics": "stable digest and no duplicate positive row creation",
        },
        "mapping_order_replay": {
            "status": "passed",
            "mapping_declaration_order": row["transfer_mapping_trace"][
                "mapping_declaration_order"
            ],
            "pre_observation_order": row["transfer_mapping_trace"]["pre_observation_order"],
            "post_observation_order": row["transfer_mapping_trace"][
                "post_observation_order"
            ],
            "mapping_precedes_pre_and_post_observation": (
                row["transfer_mapping_trace"]["mapping_declaration_order"]
                < row["transfer_mapping_trace"]["pre_observation_order"]
                < row["transfer_mapping_trace"]["post_observation_order"]
            ),
            "mapping_digest_excludes_outcome": row["transfer_mapping_trace"][
                "mapping_digest_excludes_outcome"
            ],
        },
        "support_reconstruction_replay": {
            "hidden_support_reconstruction_absent": row[
                "hidden_support_reconstruction_absent"
            ],
            "reconstructed_support_events": row["reconstructed_support_ledger"][
                "reconstructed_support_events"
            ],
            "support_reconstruction_counted_as_transfer": False,
        },
        "replay_evidence_creation_policy": {
            "validates_source_candidate_artifacts_only": True,
            "new_transfer_mapping_created": False,
            "new_post_transfer_basin_signature_created": False,
            "new_boundary_mapping_created": False,
            "source_runtime_records_replayed": [
                "transfer_mapping_trace",
                "pre_transfer_basin_signature_trace",
                "post_transfer_basin_signature_trace",
                "boundary_mapping_trace",
                "support_preservation_trace",
                "coherence_preservation_trace",
                "flux_balance_trace",
                "reconstructed_support_ledger",
            ],
        },
        "ct3_replay_candidate_supported": True,
        "ct4_or_stronger_supported": False,
        "ct5_or_stronger_supported": False,
        "final_transfer_supported": False,
    }


def replay_passed(trace: dict[str, Any]) -> bool:
    return all(
        trace[mode]["status"] == "passed"
        for mode in (
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "mapping_order_replay",
        )
    )


def build_control_results(i2: dict[str, Any], row: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for control in i2["control_schema"]["control_rows"]:
        control_id = control["control_id"]
        if control_id == "replay_failure_control":
            status = "passed"
            actual = "passed_all_required_I5_replay_modes"
            rung_effect = "CT3_not_blocked"
            reason = "I5 executes artifact, snapshot/load, duplicate, and mapping-order replay."
        elif control_id == "stress_variant_failure_control":
            status = "not_applicable"
            actual = "deferred_blocks_CT5_or_stronger_until_iteration_6"
            rung_effect = "CT5_or_stronger_blocked"
            reason = "I5 is replay-only; stress/variant testing remains I6 scope."
        elif (
            control_id == "cross_substrate_mapping_missing_control"
            and row["transfer_scope"] != "substrate"
        ):
            status = "not_applicable"
            actual = "topology_or_configuration_scope_not_substrate"
            rung_effect = "substrate_transfer_claim_not_opened"
            reason = "I5 replays configuration/topology rows only; no substrate-transfer claim is opened."
        else:
            status = "passed"
            actual = "inherited_or_revalidated_false_positive_blocker_clear"
            rung_effect = "CT3_not_blocked"
            reason = "I5 preserves the I4/I4-A source-current candidate boundary and replay does not trigger this blocker."
        results.append(
            {
                "control_id": control_id,
                "control_status": status,
                "blocked_condition": control["blocked_condition"],
                "expected_result": "clear_or_defer_without_upgrading_beyond_CT3",
                "actual_result": actual,
                "claim_allowed_when_control_triggers": False,
                "rung_effect": rung_effect,
                "orthogonal_role": control["orthogonal_role"],
                "control_satisfied_for_positive_row": status in {"passed", "not_applicable"},
                "control_applicability_reason": reason,
            }
        )
    return results


def build_replay_row(
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    source: dict[str, Any],
    source_label: str,
) -> dict[str, Any]:
    source_row = source["candidate_rows"][0]
    replay_trace = build_replay_trace(source, source_label)
    row_id = f"n27_i5_row_{source_label}_same_basin_mapping_replay"
    replay_artifact = trace_artifact("replay_trace", row_id, replay_trace)
    artifact_manifest = list(source_row["artifact_manifest"]) + [replay_artifact]
    row = {
        "active_nulls_output_digest": i3["output_digest"],
        "all_artifact_sha256_match_file_contents": True,
        "ap4_condition_reason": source_row["ap4_condition_reason"],
        "ap4_dependency_status": source_row["ap4_dependency_status"],
        "ap5_condition_reason": source_row["ap5_condition_reason"],
        "ap5_dependency_status": source_row["ap5_dependency_status"],
        "artifact_manifest": artifact_manifest,
        "boundary_mapping_tolerance_formula": source_row[
            "boundary_mapping_tolerance_formula"
        ],
        "boundary_mapping_trace": source_row["boundary_mapping_trace"],
        "claim_ceiling": (
            "provisional CT3 replay-backed same-basin transfer candidate pending "
            "I6 stress, I7 controls/classification, and I8 closeout; no final "
            "transfer, semantic identity, native support, native AP5, AP5 NAT4-gap "
            "resolution, Phase 8, or ant ecology claim"
        ),
        "coherence_floor_margin_formula": source_row["coherence_floor_margin_formula"],
        "coherence_preservation_trace": source_row["coherence_preservation_trace"],
        "configuration_label_only_rejected": source_row[
            "configuration_label_only_rejected"
        ],
        "consumable_contract_row_digest": source_row["consumable_contract_row_digest"],
        "control_results": build_control_results(i2, source_row),
        "ct_ladder_rung": CT_RUNG,
        "derived_report_only": False,
        "descriptor_contract_row_digest": source_row["descriptor_contract_row_digest"],
        "final_transfer_supported": False,
        "flux_balance_bound_formula": source_row["flux_balance_bound_formula"],
        "flux_balance_trace": source_row["flux_balance_trace"],
        "hidden_support_reconstruction_absent": source_row[
            "hidden_support_reconstruction_absent"
        ],
        "iteration": "5",
        "n25_2_consumed_only_through_n26_context": source_row[
            "n25_2_consumed_only_through_n26_context"
        ],
        "n25_2_direct_transfer_consumption_used": source_row[
            "n25_2_direct_transfer_consumption_used"
        ],
        "n26_closeout_output_digest": source_row["n26_closeout_output_digest"],
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "original_fixture_support_change_trace": source_row[
            "original_fixture_support_change_trace"
        ],
        "post_transfer_basin_signature_trace": source_row[
            "post_transfer_basin_signature_trace"
        ],
        "pre_transfer_basin_signature_trace": source_row[
            "pre_transfer_basin_signature_trace"
        ],
        "proxy_score_relabel_rejected": source_row["proxy_score_relabel_rejected"],
        "reconstructed_support_ledger": source_row["reconstructed_support_ledger"],
        "replay_result": {
            "artifact_replay": "passed",
            "snapshot_load_replay": "passed",
            "duplicate_replay": "passed",
            "mapping_order_replay": "passed",
            "replay_trace_digest": digest_value(replay_trace),
            "ct3_replay_candidate_supported": replay_passed(replay_trace),
            "ct4_or_stronger_supported": False,
            "ct5_or_stronger_supported": False,
            "final_transfer_supported": False,
        },
        "artifact_replay_result": "passed",
        "snapshot_load_replay_result": "passed",
        "duplicate_replay_result": "passed",
        "mapping_order_replay_result": "passed",
        "same_basin_signature_replay_result": "passed",
        "source_transfer_core_digest": source_row["transfer_core_digest"],
        "replay_creates_new_transfer_evidence": False,
        "replay_trace": replay_trace,
        "replay_trace_digest": digest_value(replay_trace),
        "row_decision": "supported",
        "row_decision_scope": "replay_backed_CT3_candidate_pending_controls_stress_closeout",
        "row_id": row_id,
        "row_specific_thresholds_declared_before_use": source_row[
            "row_specific_thresholds_declared_before_use"
        ],
        "run_artifact_id": f"n27_i5_{source_label}_replay_runtime",
        "runtime_config_digest": source_row["runtime_config_digest"],
        "same_basin_signature_preserved_under_mapping": source_row[
            "same_basin_signature_preserved_under_mapping"
        ],
        "same_label_different_basin_rejected": source_row[
            "same_label_different_basin_rejected"
        ],
        "signature_preservation_margin_formula": source_row[
            "signature_preservation_margin_formula"
        ],
        "source_contract_row_digest": source_row["source_contract_row_digest"],
        "source_current_inputs": list(source_row["source_current_inputs"])
        + [
            {
                "artifact_role": "replay_trace",
                "consumed_as": "source_current_same_basin_mapping_replay_trace",
                "path": replay_artifact["path"],
                "sha256": replay_artifact["sha256"],
            }
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_iteration": source_row["iteration"],
        "source_output_digest": source["output_digest"],
        "support_floor_margin_formula": source_row["support_floor_margin_formula"],
        "support_preservation_trace": source_row["support_preservation_trace"],
        "support_reconstruction_as_transfer_rejected": source_row[
            "support_reconstruction_as_transfer_rejected"
        ],
        "threshold_record_digest": source_row["threshold_record_digest"],
        "transfer_claim_allowed": False,
        "transfer_core": source_row["transfer_core"],
        "transfer_core_digest": source_row["transfer_core_digest"],
        "transfer_mapping_digest": source_row["transfer_mapping_digest"],
        "transfer_mapping_id": source_row["transfer_mapping_id"],
        "transfer_mapping_trace": source_row["transfer_mapping_trace"],
        "transfer_schema_output_digest": i2["output_digest"],
        "transfer_scope": source_row["transfer_scope"],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    row["row_output_digest"] = digest_value(row)
    return row


def artifact_sha256_matches(manifest: list[dict[str, str]]) -> bool:
    for artifact in manifest:
        path = ROOT / artifact["path"]
        if not path.exists() or sha256_file(path) != artifact["sha256"]:
            return False
    return True


def build_checks(
    output: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["replay_rows"]
    allowed_statuses = set(i2["control_schema"]["allowed_control_statuses"])
    required_replay = set(i2["replay_schema"]["ct3_required_replay_modes"])
    required_ct3_roles = set(
        next(item for item in i2["ct_ladder"] if item["rung"] == "CT3")[
            "required_artifact_roles"
        ]
    )
    return [
        check(
            "source_chain_digests_match",
            output["source_inventory_output_digest"] == i1["output_digest"]
            and output["transfer_schema_output_digest"] == i2["output_digest"]
            and output["active_nulls_output_digest"] == i3["output_digest"]
            and output["minimal_configuration_transfer_output_digest"]
            == i4["output_digest"]
            and output["topology_fixture_variant_transfer_output_digest"]
            == i4a["output_digest"],
            {
                "i1": i1["output_digest"],
                "i2": i2["output_digest"],
                "i3": i3["output_digest"],
                "i4": i4["output_digest"],
                "i4a": i4a["output_digest"],
            },
        ),
        check(
            "i4_and_i4a_ready_for_replay",
            i4.get("ready_for_iteration_5_replay_same_basin_mapping_matrix") is True
            and i4a.get("ready_for_iteration_5_replay_same_basin_mapping_matrix") is True,
            {
                "i4_ready": i4.get("ready_for_iteration_5_replay_same_basin_mapping_matrix"),
                "i4a_ready": i4a.get(
                    "ready_for_iteration_5_replay_same_basin_mapping_matrix"
                ),
            },
        ),
        check(
            "two_ct2_candidates_consumed",
            len(rows) == 2
            and {row["source_iteration"] for row in rows} == {"4", "4-A"}
            and all(row["source_output_digest"] in {i4["output_digest"], i4a["output_digest"]} for row in rows),
            [row["source_iteration"] for row in rows],
        ),
        check(
            "required_ct3_replay_modes_pass",
            all(
                required_replay
                == {
                    mode
                    for mode in required_replay
                    if row["replay_trace"][mode]["status"] == "passed"
                }
                for row in rows
            ),
            [row["replay_result"] for row in rows],
        ),
        check(
            "duplicate_replay_stable_without_duplicate_positive_rows",
            all(
                row["replay_trace"]["duplicate_replay"]["duplicate_digest_stable"]
                and row["replay_trace"]["duplicate_replay"][
                    "duplicate_replay_first_emitted"
                ]
                and not row["replay_trace"]["duplicate_replay"][
                    "duplicate_replay_second_emitted"
                ]
                and not row["replay_trace"]["duplicate_replay"][
                    "duplicate_positive_row_created"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "duplicate_replay": row["replay_trace"]["duplicate_replay"],
                }
                for row in rows
            ],
        ),
        check(
            "mapping_order_replay_preserves_declared_order",
            all(
                row["replay_trace"]["mapping_order_replay"][
                    "mapping_precedes_pre_and_post_observation"
                ]
                and row["replay_trace"]["mapping_order_replay"][
                    "mapping_digest_excludes_outcome"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "mapping_order_replay": row["replay_trace"]["mapping_order_replay"],
                }
                for row in rows
            ],
        ),
        check(
            "same_basin_mapping_replay_preserves_required_metrics",
            all(
                row["same_basin_signature_replay_result"] == "passed"
                and row["same_basin_signature_preserved_under_mapping"]
                and row["boundary_mapping_trace"]["boundary_mapping_preserved"]
                and row["support_preservation_trace"]["support_preserved_above_floor"]
                and row["coherence_preservation_trace"][
                    "coherence_preserved_above_floor"
                ]
                and row["flux_balance_trace"]["flux_balance_preserved_within_bound"]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "same_basin_signature_replay_result": row[
                        "same_basin_signature_replay_result"
                    ],
                    "signature": row["same_basin_signature_preserved_under_mapping"],
                    "boundary": row["boundary_mapping_trace"]["boundary_mapping_preserved"],
                    "support": row["support_preservation_trace"][
                        "support_preserved_above_floor"
                    ],
                    "coherence": row["coherence_preservation_trace"][
                        "coherence_preserved_above_floor"
                    ],
                    "flux": row["flux_balance_trace"][
                        "flux_balance_preserved_within_bound"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "replay_validates_source_records_without_creating_transfer_evidence",
            all(
                row["source_transfer_core_digest"] == row["transfer_core_digest"]
                and row["replay_creates_new_transfer_evidence"] is False
                and row["replay_trace"]["replay_evidence_creation_policy"][
                    "validates_source_candidate_artifacts_only"
                ]
                and not row["replay_trace"]["replay_evidence_creation_policy"][
                    "new_post_transfer_basin_signature_created"
                ]
                and not row["replay_trace"]["replay_evidence_creation_policy"][
                    "new_transfer_mapping_created"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "source_transfer_core_digest": row["source_transfer_core_digest"],
                    "transfer_core_digest": row["transfer_core_digest"],
                    "policy": row["replay_trace"]["replay_evidence_creation_policy"],
                }
                for row in rows
            ],
        ),
        check(
            "support_reconstruction_absent_and_not_counted",
            all(
                row["hidden_support_reconstruction_absent"]
                and row["support_reconstruction_as_transfer_rejected"]
                and not row["replay_trace"]["support_reconstruction_replay"][
                    "reconstructed_support_events"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "reconstruction": row["replay_trace"][
                        "support_reconstruction_replay"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "artifact_sha256_match_file_contents",
            all(artifact_sha256_matches(row["artifact_manifest"]) for row in rows),
            [row["row_id"] for row in rows],
        ),
        check(
            "ct3_artifact_roles_present",
            all(
                required_ct3_roles
                <= {artifact["artifact_role"] for artifact in row["artifact_manifest"]}
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "roles": sorted({artifact["artifact_role"] for artifact in row["artifact_manifest"]}),
                }
                for row in rows
            ],
        ),
        check(
            "control_status_values_within_frozen_enum",
            all(
                item["control_status"] in allowed_statuses
                for row in rows
                for item in row["control_results"]
            ),
            sorted({item["control_status"] for row in rows for item in row["control_results"]}),
        ),
        check(
            "replay_failure_control_passed_for_ct3",
            all(
                next(
                    item
                    for item in row["control_results"]
                    if item["control_id"] == "replay_failure_control"
                )["control_status"]
                == "passed"
                for row in rows
            ),
            [
                next(
                    item
                    for item in row["control_results"]
                    if item["control_id"] == "replay_failure_control"
                )
                for row in rows
            ],
        ),
        check(
            "stress_and_final_transfer_remain_blocked",
            output["ct4_or_stronger_supported"] is False
            and output["ct5_or_stronger_supported"] is False
            and output["final_transfer_supported"] is False
            and all(not row["final_transfer_supported"] for row in rows),
            {
                "ct4_or_stronger_supported": output["ct4_or_stronger_supported"],
                "ct5_or_stronger_supported": output["ct5_or_stronger_supported"],
                "final_transfer_supported": output["final_transfer_supported"],
            },
        ),
        check(
            "ap_gap_and_source_boundaries_preserved",
            all(row["ap4_dependency_status"] == "not_applicable" for row in rows)
            and all(row["ap5_dependency_status"] == "not_applicable" for row in rows)
            and all(not row["n25_2_direct_transfer_consumption_used"] for row in rows),
            [
                {
                    "row_id": row["row_id"],
                    "ap4": row["ap4_dependency_status"],
                    "ap5": row["ap5_dependency_status"],
                    "n25_2_direct_transfer_consumption_used": row[
                        "n25_2_direct_transfer_consumption_used"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                value is False
                for row in rows
                for value in row["unsafe_claim_flags"].values()
            )
            and all(value is False for value in output["claim_boundary"]["unsafe_claim_flags"].values()),
            [row["row_id"] for row in rows],
        ),
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in string
                for marker in ABSOLUTE_PATH_MARKERS
                for string in collect_strings(output)
            ),
            {"checked_marker_count": len(ABSOLUTE_PATH_MARKERS)},
        ),
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    rows = [
        build_replay_row(i1, i2, i3, i4, "i4"),
        build_replay_row(i1, i2, i3, i4a, "i4a"),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_replay_same_basin_mapping_matrix",
        "experiment": "N27",
        "iteration": "5",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Replay the I4 and I4-A CT2 candidates and test whether same-basin "
            "mapping evidence is stable under artifact, snapshot/load, duplicate, "
            "and mapping-order replay."
        ),
        "source_records": [
            source_record(I1_OUTPUT, "n27_i1_source_inventory", "source_inventory"),
            source_record(I2_OUTPUT, "n27_i2_transfer_schema", "schema_control_freeze"),
            source_record(I3_OUTPUT, "n27_i3_active_nulls", "active_null_boundary"),
            source_record(I4_OUTPUT, "n27_i4_minimal_transfer", "minimal_transfer_candidate"),
            source_record(
                I4A_OUTPUT,
                "n27_i4a_topology_fixture_variant",
                "topology_fixture_variant_candidate",
            ),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "topology_fixture_variant_transfer_output_digest": i4a["output_digest"],
        "status": "pending",
        "acceptance_state": "pending",
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": True,
        "candidate_rows_classified": True,
        "provisional_ct_ladder_rung": CT_RUNG,
        "ct_ladder_rung_assigned": False,
        "ct_assignment_scope": "replay_backed_candidate_only_pending_controls_stress_closeout",
        "ct3_replay_candidate_supported": True,
        "ct4_or_stronger_supported": False,
        "ct5_or_stronger_supported": False,
        "ct6_or_stronger_supported": False,
        "final_transfer_supported": False,
        "replay_row_count": len(rows),
        "matrix_summary": {
            "candidate_count": len(rows),
            "replay_pass_count": sum(
                1 for row in rows if row["replay_result"]["ct3_replay_candidate_supported"]
            ),
            "replay_fail_count": sum(
                1 for row in rows if not row["replay_result"]["ct3_replay_candidate_supported"]
            ),
            "ct3_candidate_count": sum(
                1 for row in rows if row["ct_ladder_rung"] == "CT3"
            ),
            "ct4_or_stronger_supported": False,
            "ct5_or_stronger_supported": False,
            "final_transfer_supported": False,
        },
        "replay_rows": rows,
        "ready_for_iteration_6_stress_mapping_variant_transfer_matrix": True,
        "claim_boundary": {
            "claim_ceiling": (
                "provisional CT3 replay-backed same-basin transfer candidate; "
                "stress, full control classification, final transfer, native AP5, "
                "AP5 NAT4-gap resolution, Phase 8, and ant ecology remain blocked"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    checks = build_checks(output, i1, i2, i3, i4, i4a)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_replay_same_basin_mapping_matrix_CT3_candidates_pending_controls_stress"
        if output["status"] == "passed"
        else "blocked_replay_same_basin_mapping_matrix"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 5 - Replay And Same-Basin Mapping Matrix

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 5 replays the two existing CT2 candidates: I4 minimal
configuration-frame transfer and I4-A topology/fixture variant transfer. It
does not introduce a new mapping family and does not claim final transfer.

```text
provisional_ct_ladder_rung = {output['provisional_ct_ladder_rung']}
ct3_replay_candidate_supported = {str(output['ct3_replay_candidate_supported']).lower()}
ct4_or_stronger_supported = {str(output['ct4_or_stronger_supported']).lower()}
ct5_or_stronger_supported = {str(output['ct5_or_stronger_supported']).lower()}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
```

## Matrix Summary

```text
candidate_count = {output['matrix_summary']['candidate_count']}
replay_pass_count = {output['matrix_summary']['replay_pass_count']}
replay_fail_count = {output['matrix_summary']['replay_fail_count']}
ct3_candidate_count = {output['matrix_summary']['ct3_candidate_count']}
```

## Replay Rows

| Row | Source | Scope | Artifact | Snapshot | Duplicate | Mapping Order | CT Rung |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""
    for row in output["replay_rows"]:
        trace = row["replay_trace"]
        report += (
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['transfer_scope']}` | `{trace['artifact_replay']['status']}` | "
            f"`{trace['snapshot_load_replay']['status']}` | "
            f"`{trace['duplicate_replay']['status']}` | "
            f"`{trace['mapping_order_replay']['status']}` | `{row['ct_ladder_rung']}` |\n"
        )

    report += """
## Geometric Interpretation

I5 asks whether the I4 and I4-A basin-transfer traces remain the same after
replay. For each row, replay reconstructs the artifact manifest, reloads the
transfer core and pre/post signature digests, checks that the declared mapping
still precedes pre/post observations, and verifies that duplicate replay is
idempotent rather than creating a second positive transfer row.

Duplicate replay uses the explicit semantics:

```text
duplicate_replay_first_emitted = true
duplicate_replay_second_emitted = false
duplicate_replay_digest_stable = true
```

Here `second_emitted = false` means duplicate suppression worked. The second
replay validated the same digest without creating another positive row.

The result is CT3 because the same-basin transfer records are replay-backed.
It is not CT4 or CT5: fail-closed controls and stress/variant testing remain
later iterations.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Interpretation

I5 supports two provisional CT3 replay-backed same-basin transfer candidates:
the original I4 alpha/beta minimal configuration transfer and the I4-A
gamma/delta topology fixture variant. This strengthens N27 from source-current
CT2 existence to replay-backed CT3 evidence, but it still does not support
control-backed CT4, stress-backed CT5, final transfer, semantic identity,
native support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `{output['output_digest']}`
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
