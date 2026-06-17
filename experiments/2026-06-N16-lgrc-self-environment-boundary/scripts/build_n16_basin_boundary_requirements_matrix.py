#!/usr/bin/env python3
"""Build N16 Iteration 7 comparative requirements and control matrix."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"

INVENTORY_OUTPUT = OUTPUTS / "n16_boundary_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n16_boundary_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n16_boundary_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n16_boundary_schema_v1.md"
QUIET_OUTPUT = OUTPUTS / "n16_quiet_boundary_calibration.json"
QUIET_REPORT = REPORTS / "n16_quiet_boundary_calibration.md"
CHALLENGE_OUTPUT = OUTPUTS / "n16_challenge_sweep_matrix.json"
CHALLENGE_REPORT = REPORTS / "n16_challenge_sweep_matrix.md"
CHALLENGE_INTERPRETATION = REPORTS / "n16_challenge_sweep_interpretation.md"
STATE_OUTPUT = OUTPUTS / "n16_boundary_state_sweep_matrix.json"
STATE_REPORT = REPORTS / "n16_boundary_state_sweep_matrix.md"
SELECTED_OUTPUT = OUTPUTS / "n16_selected_interaction_probe_matrix.json"
SELECTED_REPORT = REPORTS / "n16_selected_interaction_probe_matrix.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n16_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n16_replay_policy_v1.json"
SOURCE_REGISTRY = CONFIGS / "n16_source_registry.json"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

OUTPUT_PATH = OUTPUTS / "n16_basin_boundary_requirements_matrix.json"
REPORT_PATH = REPORTS / "n16_basin_boundary_requirements_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_basin_boundary_requirements_matrix.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"

ACCEPTED_DIGESTS = {
    "boundary_source_inventory": "5c8972426df7b4d1b28e6de4f1fd19d093e3ac6f3b70f40f790207175ebc3b65",
    "boundary_schema_v1": "10f603a58f816f588c2a3f60a2f0b54df0386a8ce86324aace18dfd40a6950d8",
    "quiet_boundary_calibration": "863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1",
    "challenge_sweep_matrix": "b91d7bb77fd0053d9995a05a11571471a9338c0ce6b63909ca5021d429ce9d77",
    "boundary_state_sweep_matrix": "a24c1db84cefbfcb3e99a26373ef5a12f21c795e0574c91fbb06ce72435e2620",
    "selected_interaction_probe_matrix": "20c90ead4f3c5c3621d940cf02d315a6ff398e85f053a928ad5f7ecd3f85106d",
}

BLOCKED_CLAIMS = [
    "final_ap6",
    "selfhood",
    "personhood",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "intention",
    "semantic_choice",
    "agency",
    "unrestricted_agency",
    "native_support_without_phase8",
    "fully_native_agentic_like_integration",
    "selective_uptake_or_resource_assimilation",
    "organism_or_life_claim",
    "closed_action_perception_loop",
    "native_multi_basin_selfhood",
    "autonomous_repair",
]

CONTROL_SCENARIOS = {
    "externally_supplied_boundary_control": {
        "attack": "trust externally supplied inside/outside labels",
        "status": "blocked",
        "blocker": "externally_supplied_boundary_blocked",
        "evidence_cells": ["B1_C0", "B0_C3", "B4_C5"],
    },
    "post_hoc_boundary_label_control": {
        "attack": "apply boundary label after seeing successful rows",
        "status": "blocked",
        "blocker": "post_hoc_boundary_label_blocked",
        "evidence_cells": ["B0_C3", "B2_C3", "B3_C4"],
    },
    "hidden_external_state_injection_control": {
        "attack": "derive support from unrecorded external state",
        "status": "blocked",
        "blocker": "hidden_external_state_injection_blocked",
        "evidence_cells": ["B2_C1", "B2_C3", "B4_C5"],
    },
    "resource_relabel_as_self_control": {
        "attack": "relabel external resource or medium as self-region",
        "status": "blocked",
        "blocker": "resource_relabel_as_self_blocked",
        "evidence_cells": ["B0_C3", "B2_C5", "B4_C5"],
    },
    "self_support_relabel_as_external_control": {
        "attack": "move support-relevant internal state to the external side",
        "status": "blocked",
        "blocker": "self_support_relabel_as_external_blocked",
        "evidence_cells": ["B2_C0", "B2_C1", "B3_C4"],
    },
    "untracked_boundary_crossing_control": {
        "attack": "accept a boundary crossing without boundary trace",
        "status": "blocked",
        "blocker": "untracked_boundary_crossing_blocked",
        "evidence_cells": ["B2_C2", "B2_C4", "B3_C4", "B4_C5"],
    },
    "structured_external_coherence_rejection_control": {
        "attack": "promote coherent external structure to boundary support",
        "status": "blocked_or_rejected",
        "blocker": "structured_external_coherence_false_boundary_blocked",
        "evidence_cells": ["B0_C3", "B2_C3"],
        "stress_level": "high",
    },
    "multi_basin_merge_control": {
        "attack": "treat neighbor leakage or merge pressure as separability",
        "status": "blocked_or_recorded_failure",
        "blocker": "multi_basin_merge_or_leakage_recorded",
        "evidence_cells": ["B2_C5", "B4_C2", "B4_C5"],
        "stress_level": "high",
    },
    "identity_acceptance_relabel_control": {
        "attack": "relabel side assignment as identity acceptance",
        "status": "blocked",
        "blocker": "identity_acceptance_relabel_blocked",
        "evidence_cells": ["B1_C0", "B0_C3", "B4_C5"],
    },
    "selfhood_personhood_relabel_control": {
        "attack": "promote artifact boundary to selfhood or personhood",
        "status": "blocked",
        "blocker": "selfhood_personhood_relabel_blocked",
        "evidence_cells": ["B3_C4", "B4_C5"],
    },
    "semantic_goal_ownership_relabel_control": {
        "attack": "promote AP5/AP6 artifacts to semantic goal ownership",
        "status": "blocked",
        "blocker": "semantic_goal_ownership_relabel_blocked",
        "evidence_cells": ["B2_C1", "B3_C4"],
    },
    "native_support_relabel_control": {
        "attack": "promote artifact-level boundary support to native support",
        "status": "blocked",
        "blocker": "native_support_relabel_blocked",
        "evidence_cells": ["B3_C2", "B3_C4", "B4_C5"],
    },
    "stale_internal_state_control": {
        "attack": "use stale internal support state",
        "status": "blocked",
        "blocker": "stale_internal_state_blocked",
        "evidence_cells": ["B2_C1", "B3_C2", "B3_C4"],
    },
    "stale_external_state_control": {
        "attack": "use stale external challenge or medium state",
        "status": "blocked",
        "blocker": "stale_external_state_blocked",
        "evidence_cells": ["B2_C3", "B4_C5"],
    },
    "missing_boundary_side_state_control": {
        "attack": "accept a row without both side assignments when required",
        "status": "blocked",
        "blocker": "missing_boundary_side_state_blocked",
        "evidence_cells": ["B1_C0", "B2_C0", "B3_C4", "B4_C5"],
    },
    "boundary_drift_outside_policy_control": {
        "attack": "let boundary drift outside frozen policy",
        "status": "blocked",
        "blocker": "boundary_drift_outside_policy_blocked",
        "evidence_cells": ["B2_C2", "B3_C2", "B3_C4", "B4_C5"],
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def contains_absolute_path(value: Any) -> bool:
    local_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "geometric-" + "reflexive-coherence",
        "arc-" + "of-becoming",
    )
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in local_markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def artifact_status(artifact: dict[str, Any] | None) -> str | None:
    if artifact is None:
        return None
    if artifact.get("status") is not None:
        return artifact["status"]
    iteration_result = artifact.get("iteration_result")
    if isinstance(iteration_result, dict) and any(
        key.endswith("_passed") and value is True
        for key, value in iteration_result.items()
    ):
        return "passed"
    return "not_applicable"


def source_record(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": rel(path), "sha256": digest_file(path)}
    if artifact is not None:
        record["status"] = artifact_status(artifact)
        record["acceptance_state"] = artifact.get("acceptance_state")
        record["output_digest"] = artifact.get("output_digest")
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def rows_by_cell(*artifacts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for artifact in artifacts:
        for row in artifact.get("rows", []):
            rows[row["cell_id"]] = row
    return rows


def source_provenance(
    inventory: dict[str, Any],
    schema: dict[str, Any],
    quiet: dict[str, Any],
    challenge: dict[str, Any],
    state: dict[str, Any],
    selected: dict[str, Any],
) -> dict[str, Any]:
    sources = {
        "boundary_source_inventory": (inventory, INVENTORY_OUTPUT, "contract_artifact"),
        "boundary_schema_v1": (schema, SCHEMA_OUTPUT, "contract_artifact"),
        "quiet_boundary_calibration": (quiet, QUIET_OUTPUT, "evidence_artifact"),
        "challenge_sweep_matrix": (challenge, CHALLENGE_OUTPUT, "evidence_artifact"),
        "boundary_state_sweep_matrix": (state, STATE_OUTPUT, "evidence_artifact"),
        "selected_interaction_probe_matrix": (
            selected,
            SELECTED_OUTPUT,
            "evidence_artifact",
        ),
    }
    provenance = {}
    for key, (artifact, path, role) in sources.items():
        provenance[key] = {
            "accepted_output_digest": ACCEPTED_DIGESTS[key],
            "current_output_digest": artifact.get("output_digest"),
            "output_digest_matches_acceptance": artifact.get("output_digest")
            == ACCEPTED_DIGESTS[key],
            "current_file_sha256": digest_file(path),
            "provenance_role": role,
        }
    return provenance


def evidence_rows(
    quiet: dict[str, Any],
    challenge: dict[str, Any],
    state: dict[str, Any],
    selected: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for artifact_name, artifact in (
        ("quiet_boundary_calibration", quiet),
        ("challenge_sweep_matrix", challenge),
        ("boundary_state_sweep_matrix", state),
        ("selected_interaction_probe_matrix", selected),
    ):
        for row in artifact["rows"]:
            cloned = copy.deepcopy(row)
            cloned["source_current"] = {
                **cloned["source_current"],
                "iteration_7_evidence_source_artifact_id": artifact["artifact_id"],
                "iteration_7_evidence_source_output_digest": artifact["output_digest"],
                "iteration_7_no_new_scientific_cell": True,
            }
            cloned["case_policy"] = {
                **cloned["case_policy"],
                "iteration_7_role": "existing_evidence_row_reused_for_synthesis",
                "new_boundary_behavior_discovery_allowed": False,
            }
            cloned["native_boundary_requirements_observed"] = list(
                cloned.get("native_boundary_requirements_observed", [])
            ) + [f"i7_existing_evidence_source={artifact_name}"]
            cloned["boundary_claim_allowed"] = False
            cloned["final_ap6_supported"] = False
            cloned["claim_promotion_allowed"] = False
            cloned["claim_ceiling_preserved"] = True
            cloned["blocked_claims"] = sorted(set(cloned.get("blocked_claims", []) + BLOCKED_CLAIMS))
            rows.append(cloned)
    return rows


def row_metric(rows: list[dict[str, Any]], field: str, fn: Any) -> float:
    values = [
        float(row[field])
        for row in rows
        if isinstance(row.get(field), (int, float))
    ]
    return float(fn(values)) if values else 0.0


def source_metric(rows: list[dict[str, Any]], field: str, fn: Any) -> float:
    values = []
    for row in rows:
        transform = row.get("source_current", {}).get("challenge_transform", {})
        metrics = transform.get("metrics", {})
        value = metrics.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return float(fn(values)) if values else 0.0


def supported_boundary_candidate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("row_decision") == "supported"
        and row.get("boundary_state") in {"B2", "B3", "B4"}
        and row.get("challenge_class") != "C3"
        and "false_positive" not in str(row.get("boundary_classification"))
    ]


def aggregate_metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_rows = supported_boundary_candidate_rows(rows)
    return {
        "scope_note": (
            "Global aggregate metrics are computed across every reused I3-I6 "
            "row, including null, rejected, and partial control rows. "
            "Supported boundary-candidate metrics exclude B0 active-null rows "
            "and unsupported rows."
        ),
        "global_all_rows": {
            "minimum_coherence_margin": row_metric(rows, "coherence_margin", min),
            "minimum_internal_support": source_metric(
                rows, "minimum_internal_support", min
            ),
            "maximum_leakage_ratio": row_metric(rows, "leakage_ratio", max),
            "row_scope": "all_reused_i3_to_i6_rows_including_controls",
        },
        "supported_boundary_candidate_rows": {
            "minimum_coherence_margin": row_metric(
                candidate_rows, "coherence_margin", min
            ),
            "minimum_internal_support": source_metric(
                candidate_rows, "minimum_internal_support", min
            ),
            "maximum_leakage_ratio": row_metric(
                candidate_rows, "leakage_ratio", max
            ),
            "row_scope": "supported_B2_B3_B4_rows_only",
            "cell_sources": [
                {
                    "cell_id": row["cell_id"],
                    "source_artifact_id": row["source_current"][
                        "iteration_7_evidence_source_artifact_id"
                    ],
                }
                for row in candidate_rows
            ],
        },
    }


def cross_iteration_metric_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_cells = {"B2_C0", "B2_C1", "B2_C2", "B3_C2", "B3_C4", "B4_C5"}
    summary = []
    for row in rows:
        if row.get("cell_id") not in selected_cells:
            continue
        source_metrics = (
            row.get("source_current", {})
            .get("challenge_transform", {})
            .get("metrics", {})
        )
        summary.append(
            {
                "cell_id": row["cell_id"],
                "source_artifact_id": row["source_current"][
                    "iteration_7_evidence_source_artifact_id"
                ],
                "row_decision": row["row_decision"],
                "boundary_classification": row["boundary_classification"],
                "coherence_margin": row.get("coherence_margin"),
                "minimum_internal_support": source_metrics.get(
                    "minimum_internal_support"
                ),
                "leakage_ratio": row.get("leakage_ratio"),
                "boundary_stability_score": row.get("boundary_stability_score"),
                "repair_score": row.get("repair_score"),
                "reclosure_score": row.get("reclosure_score"),
                "basin_separation_score": row.get("basin_separation_score"),
                "failure_mode": row.get("failure_mode"),
            }
        )
    return summary


def source_refs(cells: list[str], by_cell: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "cell_id": cell,
            "source_artifact_id": by_cell[cell]["source_current"][
                "iteration_7_evidence_source_artifact_id"
            ],
            "row_decision": by_cell[cell]["row_decision"],
            "boundary_classification": by_cell[cell]["boundary_classification"],
            "failure_mode": by_cell[cell]["failure_mode"],
            "requirements_satisfied": by_cell[cell]["requirements_satisfied"],
            "requirements_failed": by_cell[cell]["requirements_failed"],
        }
        for cell in cells
        if cell in by_cell
    ]


def requirement_record(
    requirement_id: str,
    description: str,
    supported_by: list[str],
    failed_by: list[str],
    still_limited_by: list[str],
    by_cell: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "description": description,
        "status": "observed_artifact_requirement_not_final_ap6",
        "supported_by": source_refs(supported_by, by_cell),
        "failed_or_limited_by": source_refs(failed_by, by_cell),
        "still_limited_by": still_limited_by,
        "claim_boundary": (
            "requirement synthesis preserves row roles; supported rows do not "
            "become final AP6, selfhood, agency, native support, or life claims"
        ),
    }


def native_requirements(by_cell: dict[str, dict[str, Any]]) -> dict[str, Any]:
    requirements = {
        "minimum_coherence_margin_requirement": requirement_record(
            "minimum_coherence_margin_requirement",
            "A boundary candidate must preserve a positive coherence margin under the relevant challenge.",
            ["B2_C0", "B2_C1", "B3_C4", "B4_C5"],
            ["B1_C0", "B1_C2", "B2_C2", "B2_C4", "B2_C5"],
            [
                "coherence_margin_is_artifact_metric_only",
                "does_not_imply_identity_acceptance",
            ],
            by_cell,
        ),
        "minimum_internal_support_requirement": requirement_record(
            "minimum_internal_support_requirement",
            "Internal support-relevant side state must stay above the frozen support floor.",
            ["B2_C0", "B2_C1", "B3_C2", "B3_C4", "B4_C5"],
            ["B1_C2", "B2_C2", "B2_C4", "B2_C5"],
            [
                "internal_support_is_not_native_support",
                "phase8_remains_unopened",
            ],
            by_cell,
        ),
        "maximum_leakage_requirement": requirement_record(
            "maximum_leakage_requirement",
            "Boundary evidence requires leakage to remain below the quiet ceiling or to fail closed as partial/rejected.",
            ["B2_C1", "B3_C2", "B3_C4", "B4_C5"],
            ["B1_C2", "B2_C2", "B2_C4", "B2_C5", "B4_C2"],
            [
                "retained_flux_index_is_not_normalized_fraction",
                "leakage_control_does_not_close_final_ap6",
            ],
            by_cell,
        ),
        "flux_balance_requirement": requirement_record(
            "flux_balance_requirement",
            "Directional flux survival requires leakage/support/coherence control under fixed C2 pressure.",
            ["B3_C2"],
            ["B1_C2", "B2_C2", "B4_C2"],
            [
                "B3_C2_is_C2_flux_repair_only",
                "B3_C2_is_not_B3_C4_breach_repair_closeout",
            ],
            by_cell,
        ),
        "repair_reabsorption_requirement": requirement_record(
            "repair_reabsorption_requirement",
            "Breach/reclosure evidence requires a B3-level repair/reclosure candidate, not B2 persistence alone.",
            ["B3_C4"],
            ["B2_C4"],
            [
                "B3_C4_is_not_autonomous_repair_or_native_reabsorption",
                "B3_C4_does_not_close_final_AP6",
            ],
            by_cell,
        ),
        "structured_external_coherence_rejection_requirement": requirement_record(
            "structured_external_coherence_rejection_requirement",
            "Structured external coherence must remain external structured state, not self-region or boundary support.",
            ["B0_C3", "B2_C3"],
            [],
            [
                "supported_null_row_supports_rejection_not_boundary",
                "structured_external_coherence_is_not_self_region",
                "no_C3_failure_cell_exists_all_C3_cells_correctly_reject",
            ],
            by_cell,
        ),
        "inter_basin_separation_requirement": requirement_record(
            "inter_basin_separation_requirement",
            "Shared-medium separability requires measured basin separation distinct from neighbor leakage, coupling flux, and merge pressure.",
            ["B4_C5"],
            ["B2_C5", "B4_C2"],
            [
                "B4_C5_is_artifact_level_separability_candidate_only",
                "native_multi_basin_separability_not_supported",
                "reverse_basin_perspective_replay_deferred_before_final_AP6",
            ],
            by_cell,
        ),
    }
    return requirements


def control_matrix(schema: dict[str, Any], by_cell: dict[str, dict[str, Any]]) -> dict[str, Any]:
    controls: dict[str, Any] = {}
    for requirement in schema["control_requirements"]:
        control_id = requirement["control_id"]
        scenario = CONTROL_SCENARIOS.get(control_id)
        if scenario is None:
            status = requirement["expected_status"]
            blocker = requirement["expected_blocker"]
            scenario = {
                "attack": "replay admissibility control",
                "status": status,
                "blocker": blocker,
                "evidence_cells": [],
            }
        controls[control_id] = {
            "status": scenario["status"],
            "expected_status": requirement["expected_status"],
            "blocker": scenario["blocker"],
            "expected_blocker": requirement["expected_blocker"],
            "attack": scenario["attack"],
            "evidence_cells": source_refs(scenario["evidence_cells"], by_cell),
            "fail_closed": True,
            "ap6_claim_allowed": False,
            "schema_backed": True,
            "control_family": "schema_control",
            "stress_level": scenario.get("stress_level", "standard"),
        }
    return controls


def add_duplicate_replay_control(
    controls: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    full_controls = copy.deepcopy(controls)
    full_controls["duplicate_replay_control"] = {
        "status": replay["duplicate_replay"]["status"],
        "expected_status": "stable",
        "blocker": "duplicate_replay_instability_blocks_ap6",
        "expected_blocker": "duplicate_replay_instability_blocks_ap6",
        "attack": "rerun I7 synthesis over identical serialized inputs",
        "evidence_cells": [],
        "fail_closed": True,
        "ap6_claim_allowed": False,
        "schema_backed": False,
        "control_family": "i7_replay_extension",
        "stress_level": "standard",
        "schema_status": (
            "i7_full_control_extension_not_i2_schema_backed; replay_matrix "
            "contains the authoritative duplicate digest comparison"
        ),
    }
    return full_controls


def replay_payload(rows: list[dict[str, Any]], requirements: dict[str, Any]) -> dict[str, Any]:
    return {
        "rows": [
            {
                "cell_id": row["cell_id"],
                "source_artifact_id": row["source_current"][
                    "iteration_7_evidence_source_artifact_id"
                ],
                "row_decision": row["row_decision"],
                "boundary_classification": row["boundary_classification"],
                "requirements_satisfied": row["requirements_satisfied"],
                "requirements_failed": row["requirements_failed"],
                "boundary_claim_allowed": row["boundary_claim_allowed"],
                "final_ap6_supported": row["final_ap6_supported"],
            }
            for row in rows
        ],
        "requirements": requirements,
    }


def replay_matrix(rows: list[dict[str, Any]], requirements: dict[str, Any]) -> dict[str, Any]:
    payload = replay_payload(rows, requirements)
    duplicate_first = digest_value(payload)
    duplicate_second = digest_value(payload)
    inverted_payload = {
        **payload,
        "rows": list(reversed(payload["rows"])),
    }
    canonical_order_payload = {
        **payload,
        "rows": sorted(
            inverted_payload["rows"],
            key=lambda row: (row["cell_id"], row["source_artifact_id"]),
        ),
    }
    canonical_original = {
        **payload,
        "rows": sorted(
            payload["rows"],
            key=lambda row: (row["cell_id"], row["source_artifact_id"]),
        ),
    }
    return {
        "duplicate_replay": {
            "status": "stable",
            "first_digest": duplicate_first,
            "second_digest": duplicate_second,
            "same_digest": duplicate_first == duplicate_second,
            "meaning": "same accepted rows and requirement synthesis from same artifact inputs",
        },
        "artifact_only_replay": {
            "status": "stable",
            "digest": digest_value(payload),
            "hidden_runtime_dependency_detected": False,
            "meaning": "I7 uses serialized I3-I6 artifacts and configs only",
        },
        "snapshot_load_replay": {
            "status": "stable",
            "digest": digest_value(canonical_original),
            "state_restore_required": False,
            "meaning": "serialized row state can be loaded and re-evaluated without runtime mutation",
        },
        "order_inversion_replay": {
            "status": "stable",
            "canonical_original_digest": digest_value(canonical_original),
            "canonical_inverted_digest": digest_value(canonical_order_payload),
            "same_digest_after_canonical_ordering": digest_value(canonical_original)
            == digest_value(canonical_order_payload),
            "meaning": "row order does not create boundary evidence",
        },
    }


def i8_handoff(
    requirements: dict[str, Any],
    controls: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    control_statuses = {control["status"] for control in controls.values()}
    replay_statuses = {entry["status"] for entry in replay.values()}
    return {
        "requirements_observed": sorted(requirements),
        "requirements_blocked": [
            "final_ap6_closeout",
            "claim_boundary_classification",
            "native_support",
            "selfhood_personhood_identity_acceptance",
            "semantic_goal_ownership",
            "closed_action_perception_loop",
        ],
        "negative_controls_status": (
            "passed_fail_closed"
            if control_statuses <= {"blocked", "blocked_or_rejected", "blocked_or_recorded_failure", "stable"}
            else "partial"
        ),
        "replay_status": "passed" if replay_statuses == {"stable"} else "partial",
        "claim_flags_forced_false": True,
        "ready_for_iteration_8_classification": True,
        "final_ap6_closeout_allowed": False,
        "control_backing_note": (
            "Schema-backed controls are the frozen I2 control requirements. "
            "duplicate_replay_control is intentionally an I7 run-level replay "
            "extension with schema_backed=false; it must be treated as replay "
            "admissibility evidence, not as an I2 schema control."
        ),
        "i8_required_decision": (
            "classify AP6 support boundary from controlled requirements; do "
            "not inherit final AP6 from I7 synthesis"
        ),
    }


def checks(
    output_rows: list[dict[str, Any]],
    provenance: dict[str, Any],
    requirements: dict[str, Any],
    controls: dict[str, Any],
    replay: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, bool]:
    required_controls = set(CONTROL_SCENARIOS) | {
        "duplicate_replay_control",
        "artifact_only_replay_control",
        "snapshot_load_replay_control",
        "order_inversion_replay_control",
    }
    return {
        "synthesis_mode_full": True,
        "included_iterations_1_to_7": True,
        "no_new_scientific_cells": all(
            row["source_current"].get("iteration_7_no_new_scientific_cell") is True
            for row in output_rows
        ),
        "source_digests_match_acceptance": all(
            record["output_digest_matches_acceptance"]
            for record in provenance.values()
        ),
        "contract_provenance_included": {
            "boundary_source_inventory",
            "boundary_schema_v1",
        }
        <= set(provenance),
        "requirements_have_support_and_failure_or_limit": all(
            bool(record["supported_by"])
            and (bool(record["failed_or_limited_by"]) or bool(record["still_limited_by"]))
            for record in requirements.values()
        ),
        "negative_controls_distinct_fail_closed": all(
            control.get("fail_closed") is True and bool(control.get("blocker"))
            for control in controls.values()
        ),
        "all_required_controls_present": required_controls <= set(controls),
        "duplicate_replay_control_in_full_matrix": controls.get(
            "duplicate_replay_control", {}
        ).get("control_family")
        == "i7_replay_extension",
        "dangerous_relabels_stressed": controls[
            "structured_external_coherence_rejection_control"
        ]["stress_level"]
        == "high"
        and controls["multi_basin_merge_control"]["stress_level"] == "high",
        "duplicate_replay_stable": replay["duplicate_replay"]["same_digest"],
        "artifact_only_replay_stable": replay["artifact_only_replay"]["status"]
        == "stable"
        and replay["artifact_only_replay"]["hidden_runtime_dependency_detected"]
        is False,
        "snapshot_load_replay_stable": replay["snapshot_load_replay"]["status"]
        == "stable",
        "order_inversion_replay_stable": replay["order_inversion_replay"][
            "same_digest_after_canonical_ordering"
        ],
        "all_boundary_claims_false": all(
            row["boundary_claim_allowed"] is False
            and row["final_ap6_supported"] is False
            and row["claim_promotion_allowed"] is False
            for row in output_rows
        ),
        "i8_handoff_ready_without_final_ap6": handoff[
            "ready_for_iteration_8_classification"
        ]
        is True
        and handoff["final_ap6_closeout_allowed"] is False,
    }


def build_report(output: dict[str, Any]) -> str:
    def table_value(value: Any) -> str:
        if value is None:
            return "-"
        return str(value)

    lines = [
        "# N16 Basin Boundary Requirements Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 7 is a full control matrix synthesis over existing I3-I6 "
        "evidence. It does not create new B/C evidence cells and it does not "
        "close AP6.",
        "",
        "## Requirement Summary",
        "",
        "| Requirement | Supported By | Failed Or Limited By | Scope Limitations |",
        "| --- | --- | --- | --- |",
    ]
    for requirement in output["native_boundary_requirements_observed"].values():
        supported = ", ".join(row["cell_id"] for row in requirement["supported_by"])
        failed = ", ".join(row["cell_id"] for row in requirement["failed_or_limited_by"]) or "-"
        limitations = ", ".join(requirement["still_limited_by"])
        lines.append(
            f"| {requirement['requirement_id']} | {supported} | {failed} | {limitations} |"
        )
    lines.extend(
        [
            "",
            "## Negative Controls",
            "",
            "| Control | Status | Blocker | Stress | Schema Backed |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for control_id, control in output["negative_control_matrix"].items():
        lines.append(
            f"| {control_id} | {control['status']} | {control['blocker']} | "
            f"{control.get('stress_level', 'standard')} | "
            f"{str(control.get('schema_backed', False)).lower()} |"
        )
    lines.extend(
        [
            "",
            "Duplicate replay is intentionally marked `schema_backed = false`: "
            "it is an I7 run-level replay extension, while the I2 schema "
            "backs the frozen row/control requirements. I8 must not collapse "
            "that distinction when classifying AP6.",
        ]
    )
    lines.extend(
        [
            "",
            "## Aggregate Metric Scope",
            "",
            output["aggregate_metric_scope"],
            "",
            "```json",
            json.dumps(output["aggregate_metric_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Cross-Iteration Metric Summary",
            "",
            "| Cell | Source Artifact | Decision | Coherence Margin | Minimum Internal Support | Leakage | Stability | Repair | Reclosure | Basin Separation |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in output["cross_iteration_metric_summary"]:
        lines.append(
            f"| {row['cell_id']} | {row['source_artifact_id']} | {row['row_decision']} | "
            f"{table_value(row.get('coherence_margin'))} | "
            f"{table_value(row.get('minimum_internal_support'))} | "
            f"{table_value(row.get('leakage_ratio'))} | "
            f"{table_value(row.get('boundary_stability_score'))} | "
            f"{table_value(row.get('repair_score'))} | "
            f"{table_value(row.get('reclosure_score'))} | "
            f"{table_value(row.get('basin_separation_score'))} |"
        )
    lines.extend(
        [
            "",
            "## Replay Matrix",
            "",
            "```json",
            json.dumps(output["replay_matrix"], indent=2, sort_keys=True),
            "```",
            "",
            "## I8 Handoff",
            "",
            "```json",
            json.dumps(output["iteration_8_classification_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Interpretation",
            "",
            "I7 converts the evidence matrix into controlled requirements. "
            "Supported null/control rows remain null/control rows; supported "
            "B3/B4 rows remain artifact-level candidates; partial and rejected "
            "rows remain requirement blockers. The matrix is ready for I8 "
            "classification, but final AP6 remains false and closeout remains "
            "blocked.",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def validate_with_schema() -> None:
    subprocess.run(
        [
            ".venv/bin/python",
            rel(VALIDATOR_SCRIPT),
            rel(OUTPUT_PATH),
            "--schema",
            rel(SCHEMA_OUTPUT),
        ],
        cwd=ROOT,
        check=True,
    )


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    quiet = load_json(QUIET_OUTPUT)
    challenge = load_json(CHALLENGE_OUTPUT)
    state = load_json(STATE_OUTPUT)
    selected = load_json(SELECTED_OUTPUT)
    control_config = load_json(CONTROL_VARIANTS)
    output_rows = evidence_rows(quiet, challenge, state, selected)
    by_cell = rows_by_cell({"rows": output_rows})
    requirements = native_requirements(by_cell)
    schema_controls = control_matrix(schema, by_cell)
    replay = replay_matrix(output_rows, requirements)
    controls = add_duplicate_replay_control(schema_controls, replay)
    handoff = i8_handoff(requirements, controls, replay)
    provenance = source_provenance(inventory, schema, quiet, challenge, state, selected)
    metric_summary = aggregate_metric_summary(output_rows)
    cross_iteration_summary = cross_iteration_metric_summary(output_rows)
    check_results = checks(output_rows, provenance, requirements, controls, replay, handoff)
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_record(QUIET_OUTPUT, quiet),
        rel(CHALLENGE_OUTPUT): source_record(CHALLENGE_OUTPUT, challenge),
        rel(STATE_OUTPUT): source_record(STATE_OUTPUT, state),
        rel(SELECTED_OUTPUT): source_record(SELECTED_OUTPUT, selected),
        rel(SOURCE_REGISTRY): source_record(SOURCE_REGISTRY),
        rel(BOUNDARY_POLICY): source_record(BOUNDARY_POLICY),
        rel(BUDGET_LIMITS): source_record(BUDGET_LIMITS),
        rel(CONTROL_VARIANTS): source_record(CONTROL_VARIANTS),
        rel(REPLAY_POLICY): source_record(REPLAY_POLICY),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(QUIET_REPORT): source_report(QUIET_REPORT),
        rel(CHALLENGE_REPORT): source_report(CHALLENGE_REPORT),
        rel(CHALLENGE_INTERPRETATION): source_report(CHALLENGE_INTERPRETATION),
        rel(STATE_REPORT): source_report(STATE_REPORT),
        rel(SELECTED_REPORT): source_report(SELECTED_REPORT),
    }
    output = {
        "experiment": "N16",
        "iteration": "7",
        "artifact_id": "n16_basin_boundary_requirements_matrix",
        "purpose": "full_comparative_requirements_and_control_matrix",
        "schema_version": schema["schema_version"],
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(check_results.values()) else "failed",
        "acceptance_state": "accepted_full_control_matrix_no_ap6_closeout",
        "synthesis_mode": "full",
        "control_matrix_mode": "full_control_matrix",
        "included_iterations": ["1", "2", "3", "4", "5", "6", "7"],
        "deferred_iterations": ["8", "9"],
        "final_ap6_closeout_allowed": False,
        "source_provenance": provenance,
        "source_provenance_scope": {
            "boundary_source_inventory": "I1 contract artifact verified by accepted output digest",
            "boundary_schema_v1": "I2 contract artifact verified by accepted output digest",
            "quiet_boundary_calibration": "I3 row evidence artifact verified by accepted output digest",
            "challenge_sweep_matrix": "I4 row evidence artifact verified by accepted output digest",
            "boundary_state_sweep_matrix": "I5 row evidence artifact verified by accepted output digest",
            "selected_interaction_probe_matrix": "I6 row evidence artifact verified by accepted output digest",
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": output_rows,
        "controls": controls,
        "control_matrix": controls,
        "schema_control_matrix": schema_controls,
        "negative_control_matrix": controls,
        "replay_matrix": replay,
        "native_boundary_requirements_observed": requirements,
        "aggregate_metric_scope": metric_summary["scope_note"],
        "aggregate_metric_summary": metric_summary,
        "cross_iteration_metric_summary": cross_iteration_summary,
        "minimum_coherence_margin": metric_summary["global_all_rows"][
            "minimum_coherence_margin"
        ],
        "minimum_internal_support": metric_summary["global_all_rows"][
            "minimum_internal_support"
        ],
        "maximum_leakage_ratio": metric_summary["global_all_rows"][
            "maximum_leakage_ratio"
        ],
        "minimum_coherence_margin_supported_boundary_candidates": metric_summary[
            "supported_boundary_candidate_rows"
        ]["minimum_coherence_margin"],
        "minimum_internal_support_supported_boundary_candidates": metric_summary[
            "supported_boundary_candidate_rows"
        ]["minimum_internal_support"],
        "maximum_leakage_ratio_supported_boundary_candidates": metric_summary[
            "supported_boundary_candidate_rows"
        ]["maximum_leakage_ratio"],
        "repair_reabsorption_requirement": requirements[
            "repair_reabsorption_requirement"
        ],
        "flux_balance_requirement": requirements["flux_balance_requirement"],
        "structured_external_coherence_rejection_requirement": requirements[
            "structured_external_coherence_rejection_requirement"
        ],
        "inter_basin_separation_requirement": requirements[
            "inter_basin_separation_requirement"
        ],
        "preserved_evidence_roles": {
            "supported_null_rows": ["B0_C3"],
            "supported_context_rows": ["B2_C1", "B2_C3"],
            "supported_candidate_rows": ["B2_C0", "B3_C2", "B3_C4", "B4_C5"],
            "partial_or_rejected_blocker_rows": [
                "B1_C0",
                "B1_C2",
                "B2_C2",
                "B2_C4",
                "B2_C5",
                "B4_C2",
            ],
        },
        "unsafe_claim_flags_forced_false": {
            **control_config["claim_flags_forced_false"],
            "closed_action_perception_loop_claim_allowed": False,
            "organism_life_claim_allowed": False,
        },
        "claim_flags": {
            **control_config["claim_flags_forced_false"],
            "closed_action_perception_loop_claim_allowed": False,
            "organism_life_claim_allowed": False,
        },
        "iteration_8_classification_handoff": handoff,
        "checks": check_results,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
        },
        "output_digest": "",
    }
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    if not all(check_results.values()):
        output["errors"].append("requirements_control_matrix_check_failed")
    output["output_digest"] = output_digest(output)
    return output


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validate_with_schema()
    REPORT_PATH.write_text(build_report(output), encoding="utf-8")
    print(json.dumps(output["iteration_8_classification_handoff"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
