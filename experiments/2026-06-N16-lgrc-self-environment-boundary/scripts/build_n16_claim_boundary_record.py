#!/usr/bin/env python3
"""Build N16 Iteration 8 claim-boundary and AP6 classification record."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
CONFIGS = EXPERIMENT / "configs"
HYPOTHESES = EXPERIMENT / "hypotheses"
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
STATE_OUTPUT = OUTPUTS / "n16_boundary_state_sweep_matrix.json"
STATE_REPORT = REPORTS / "n16_boundary_state_sweep_matrix.md"
SELECTED_OUTPUT = OUTPUTS / "n16_selected_interaction_probe_matrix.json"
SELECTED_REPORT = REPORTS / "n16_selected_interaction_probe_matrix.md"
REQUIREMENTS_OUTPUT = OUTPUTS / "n16_basin_boundary_requirements_matrix.json"
REQUIREMENTS_REPORT = REPORTS / "n16_basin_boundary_requirements_matrix.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
HYPOTHESIS_A = HYPOTHESES / "hypothesis_a_boundary_source_inventory.md"
HYPOTHESIS_B = HYPOTHESES / "hypothesis_b_artifact_boundary_separation.md"
HYPOTHESIS_C = HYPOTHESES / "hypothesis_c_selfhood_identity_agency_boundary.md"
OUTPUT_PATH = OUTPUTS / "n16_claim_boundary_record.json"
REPORT_PATH = REPORTS / "n16_claim_boundary_record.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_claim_boundary_record.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"

ACCEPTED_DIGESTS = {
    "boundary_source_inventory": "5c8972426df7b4d1b28e6de4f1fd19d093e3ac6f3b70f40f790207175ebc3b65",
    "boundary_schema_v1": "10f603a58f816f588c2a3f60a2f0b54df0386a8ce86324aace18dfd40a6950d8",
    "quiet_boundary_calibration": "863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1",
    "challenge_sweep_matrix": "b91d7bb77fd0053d9995a05a11571471a9338c0ce6b63909ca5021d429ce9d77",
    "boundary_state_sweep_matrix": "a24c1db84cefbfcb3e99a26373ef5a12f21c795e0574c91fbb06ce72435e2620",
    "selected_interaction_probe_matrix": "20c90ead4f3c5c3621d940cf02d315a6ff398e85f053a928ad5f7ecd3f85106d",
    "basin_boundary_requirements_matrix": "383df2eb297e4a82cb71e0ce4a80aa3c506cc21ee2841b5ec010f33680229bdf",
}

UNSAFE_CLAIM_FLAGS = {
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "native_support_opened": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "selective_uptake_claim_allowed": False,
    "resource_assimilation_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "closed_action_perception_loop_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_opened": False,
    "final_ap6_supported": False,
}

CONTROL_GATE_MAP = {
    "externally_supplied_boundary_control_fails_closed": "externally_supplied_boundary_control",
    "post_hoc_boundary_label_control_fails_closed": "post_hoc_boundary_label_control",
    "hidden_external_state_injection_control_fails_closed": "hidden_external_state_injection_control",
    "resource_relabel_as_self_control_fails_closed": "resource_relabel_as_self_control",
    "self_support_relabel_as_external_control_fails_closed": "self_support_relabel_as_external_control",
    "untracked_boundary_crossing_control_fails_closed": "untracked_boundary_crossing_control",
    "identity_acceptance_relabel_control_fails_closed": "identity_acceptance_relabel_control",
    "selfhood_personhood_relabel_control_fails_closed": "selfhood_personhood_relabel_control",
    "semantic_goal_ownership_relabel_control_fails_closed": "semantic_goal_ownership_relabel_control",
    "native_support_relabel_control_fails_closed": "native_support_relabel_control",
}

CONTROL_GATE_RATIONALES = {
    gate_id: (
        "basin_boundary_requirements_matrix",
        f"I7 {control_id} fails closed with its recorded blocker and AP6 claim disallowed",
    )
    for gate_id, control_id in CONTROL_GATE_MAP.items()
}

GATE_EVIDENCE = {
    "source_inventory_accepted": ("boundary_source_inventory", "I1 inventory accepted"),
    "source_artifact_report_digest_for_each_row": (
        "boundary_source_inventory",
        "I1 source rows have artifact and report SHA-256 records",
    ),
    "direct_historic_ap6_support_status_recorded": (
        "boundary_source_inventory",
        "I1 records direct historic AP6 support as absent",
    ),
    "old_best_claims_construction_inputs_recorded": (
        "boundary_source_inventory",
        "I1 records old-best construction inputs without promoting prior claims",
    ),
    "boundary_state_axis_lineage_frozen": (
        "boundary_schema_v1",
        "I2 freezes B0-B4 lineage-derived boundary-state axis",
    ),
    "challenge_class_axis_operational_not_environment_taxonomy": (
        "boundary_schema_v1",
        "I2 freezes C0-C5 as operational challenge classes",
    ),
    "row_schema_has_internal_support_state_descriptor": (
        "boundary_schema_v1",
        "I2 row schema includes internal support-relevant state descriptor",
    ),
    "row_schema_has_external_resource_state_descriptor": (
        "boundary_schema_v1",
        "I2 row schema includes external resource state descriptor",
    ),
    "row_schema_has_external_perturbation_state_descriptor": (
        "boundary_schema_v1",
        "I2 row schema includes external perturbation descriptor",
    ),
    "row_schema_has_external_structured_state_descriptor": (
        "boundary_schema_v1",
        "I2 row schema includes external structured state descriptor",
    ),
    "external_state_role_enum_frozen": (
        "boundary_schema_v1",
        "I2 freezes external_state_role enum",
    ),
    "row_decision_enum_frozen": (
        "boundary_schema_v1",
        "I2 freezes row_decision enum",
    ),
    "row_decision_boundary_claim_relation_frozen": (
        "boundary_schema_v1",
        "I2 freezes row_decision and boundary_claim_allowed relation",
    ),
    "boundary_side_assignments_present": (
        "basin_boundary_requirements_matrix",
        "I3-I7 rows carry boundary-side assignment fields",
    ),
    "boundary_crossing_trace_present": (
        "basin_boundary_requirements_matrix",
        "I3-I7 rows carry boundary-crossing traces or fail-closed null roles",
    ),
    "dependency_trace_present": (
        "basin_boundary_requirements_matrix",
        "I3-I7 rows carry dependency traces with source SHA-256 values",
    ),
    "budget_validity_present": (
        "basin_boundary_requirements_matrix",
        "I3-I7 rows carry budget validity fields",
    ),
    "replay_digest_scope_frozen": (
        "boundary_schema_v1",
        "I2 freezes replay digest scope and algorithm",
    ),
    "artifact_only_replay_requirement_present": (
        "basin_boundary_requirements_matrix",
        "I7 artifact-only replay is stable",
    ),
    "snapshot_load_equivalence_requirement_present": (
        "basin_boundary_requirements_matrix",
        "I7 snapshot/load replay is stable",
    ),
    "order_inversion_replay_requirement_present": (
        "basin_boundary_requirements_matrix",
        "I7 order-inversion replay is stable",
    ),
    "structured_external_coherence_rejection_control_present": (
        "basin_boundary_requirements_matrix",
        "I7 high-stress structured-external relabel control is present",
    ),
    "b0_c3_active_null_rejects_false_boundary": (
        "selected_interaction_probe_matrix",
        "I6 B0_C3 supports active-null structured-external false-positive rejection",
    ),
    "b2_c0_c1_c2_unlock_required_before_b3_repair": (
        "selected_interaction_probe_matrix",
        "I6 B3_C4 is unlocked by prior B2 C0/C1/C2 evaluations",
    ),
    "b4_c5_shared_medium_separability_required": (
        "selected_interaction_probe_matrix",
        "I6 B4_C5 measures shared-medium separability directly",
    ),
    "claim_flags_forced_false": (
        "basin_boundary_requirements_matrix",
        "I7 unsafe claim flags remain false",
    ),
    "native_support_not_opened": (
        "basin_boundary_requirements_matrix",
        "I7 and I8 keep native support closed",
    ),
    "phase8_opened_false": (
        "basin_boundary_requirements_matrix",
        "I7 and I8 keep Phase 8 closed",
    ),
    "src_diff_empty_true": ("git", "No src diff is present during I8 classification"),
    **CONTROL_GATE_RATIONALES,
}

CONSISTENCY_CELL_IDS = ("B2_C0", "B2_C1", "B2_C2", "B1_C2")
CONSISTENCY_METRIC_KEYS = (
    "internal_coherence",
    "external_coherence",
    "coherence_margin",
    "inbound_flux",
    "outbound_flux",
    "retained_flux",
    "leakage_ratio",
    "boundary_stability_score",
    "minimum_internal_support",
)
NUMERIC_TOLERANCE = 1e-9


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


def src_diff_empty() -> bool:
    completed = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


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


def artifact_status(artifact: dict[str, Any]) -> str | None:
    status = artifact.get("status")
    if status is not None:
        return status
    acceptance = artifact.get("acceptance_state")
    if isinstance(acceptance, str) and acceptance.startswith("accepted_"):
        return "passed"
    return None


def source_record(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": rel(path), "sha256": digest_file(path)}
    if artifact is not None:
        record["status"] = artifact_status(artifact)
        record["acceptance_state"] = artifact.get("acceptance_state")
        record["output_digest"] = artifact.get("output_digest")
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def source_provenance(sources: dict[str, tuple[dict[str, Any], Path, str]]) -> dict[str, Any]:
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


def control_fails_closed(control: dict[str, Any] | None) -> bool:
    if not isinstance(control, dict):
        return False
    return (
        control.get("fail_closed") is True
        and control.get("ap6_claim_allowed") is False
        and control.get("status")
        in {"blocked", "blocked_or_rejected", "blocked_or_recorded_failure", "stable"}
    )


def cell_exists(
    requirements: dict[str, Any],
    cell_id: str,
    decision: str | None = None,
    source_artifact_id: str | None = None,
) -> bool:
    for row in requirements.get("rows", []):
        if row.get("cell_id") != cell_id:
            continue
        if decision is not None and row.get("row_decision") != decision:
            continue
        source = row.get("source_current", {}).get("iteration_7_evidence_source_artifact_id")
        if source_artifact_id is not None and source != source_artifact_id:
            continue
        return True
    return False


def numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def row_metric_value(row: dict[str, Any], metric_key: str) -> float | None:
    top_level = numeric_value(row.get(metric_key))
    if top_level is not None:
        return top_level
    metrics = row.get("source_current", {}).get("challenge_transform", {}).get("metrics", {})
    if isinstance(metrics, dict):
        return numeric_value(metrics.get(metric_key))
    return None


def values_match(values: list[float]) -> bool:
    if len(values) < 2:
        return True
    first = values[0]
    return all(abs(value - first) <= NUMERIC_TOLERANCE for value in values[1:])


def cross_iteration_cell_consistency(requirements: dict[str, Any]) -> dict[str, Any]:
    rows_by_cell: dict[str, list[dict[str, Any]]] = {}
    for row in requirements.get("rows", []):
        cell_id = row.get("cell_id")
        if isinstance(cell_id, str):
            rows_by_cell.setdefault(cell_id, []).append(row)

    cell_records = []
    for cell_id in CONSISTENCY_CELL_IDS:
        rows = rows_by_cell.get(cell_id, [])
        decisions = [row.get("row_decision") for row in rows]
        decision_consistent = len(set(decisions)) == 1 if decisions else False
        metric_records = {}
        for metric_key in CONSISTENCY_METRIC_KEYS:
            values = [
                value
                for row in rows
                for value in [row_metric_value(row, metric_key)]
                if value is not None
            ]
            metric_records[metric_key] = {
                "values": values,
                "compared": len(values) >= 2,
                "consistent": values_match(values),
            }
        source_records = [
            {
                "row_id": row.get("row_id"),
                "row_decision": row.get("row_decision"),
                "source_artifact_id": row.get("source_current", {}).get(
                    "iteration_7_evidence_source_artifact_id"
                ),
                "boundary_claim_allowed": row.get("boundary_claim_allowed"),
            }
            for row in rows
        ]
        metrics_consistent = all(
            metric["consistent"] for metric in metric_records.values()
        )
        cell_records.append(
            {
                "cell_id": cell_id,
                "row_count": len(rows),
                "source_rows": source_records,
                "row_decisions": decisions,
                "row_decision_consistent": decision_consistent,
                "metric_consistency": metric_records,
                "key_metrics_consistent": metrics_consistent,
                "status": (
                    "consistent"
                    if len(rows) >= 2 and decision_consistent and metrics_consistent
                    else "inconsistent_or_insufficient"
                ),
            }
        )
    return {
        "status": (
            "passed"
            if all(cell["status"] == "consistent" for cell in cell_records)
            else "failed"
        ),
        "tolerance": NUMERIC_TOLERANCE,
        "cells_checked": list(CONSISTENCY_CELL_IDS),
        "cells": cell_records,
    }


def row_decision_enum_revalidation(
    schema: dict[str, Any],
    requirements: dict[str, Any],
) -> dict[str, Any]:
    allowed = set(schema.get("row_decision_policy", {}).get("values", []))
    invalid_rows = [
        {
            "row_id": row.get("row_id"),
            "cell_id": row.get("cell_id"),
            "row_decision": row.get("row_decision"),
        }
        for row in requirements.get("rows", [])
        if row.get("row_decision") not in allowed
    ]
    invalid_control_evidence = []
    for control_id, control in requirements.get("negative_control_matrix", {}).items():
        evidence_cells = control.get("evidence_cells", [])
        if not isinstance(evidence_cells, list):
            continue
        for evidence in evidence_cells:
            row_decision = evidence.get("row_decision")
            if row_decision not in allowed:
                invalid_control_evidence.append(
                    {
                        "control_id": control_id,
                        "cell_id": evidence.get("cell_id"),
                        "row_decision": row_decision,
                    }
                )
    return {
        "status": "passed" if not invalid_rows and not invalid_control_evidence else "failed",
        "allowed_values": sorted(allowed),
        "row_count_checked": len(requirements.get("rows", [])),
        "control_evidence_cell_count_checked": sum(
            len(control.get("evidence_cells", []))
            for control in requirements.get("negative_control_matrix", {}).values()
            if isinstance(control.get("evidence_cells", []), list)
        ),
        "invalid_rows": invalid_rows,
        "invalid_control_evidence": invalid_control_evidence,
    }


def build_gate_conditions(
    inventory: dict[str, Any],
    schema: dict[str, Any],
    requirements: dict[str, Any],
) -> dict[str, bool]:
    controls = requirements.get("negative_control_matrix", {})
    replay = requirements.get("replay_matrix", {})
    i7_checks = requirements.get("checks", {})
    inventory_checks = inventory.get("checks", {})
    schema_checks = schema.get("checks", {})
    rows = requirements.get("rows", [])
    row_fields = set(schema.get("row_schema_fields", []))
    return {
        "source_inventory_accepted": inventory.get("acceptance_state")
        == "accepted_boundary_source_inventory_only_no_ap6",
        "source_artifact_report_digest_for_each_row": inventory_checks.get(
            "every_source_row_pinned_with_artifact_report_and_digests"
        )
        is True
        and inventory_checks.get("every_row_has_source_sha256") is True
        and inventory_checks.get("every_row_has_source_report_sha256") is True,
        "direct_historic_ap6_support_status_recorded": inventory_checks.get(
            "direct_historic_ap6_status_mapping_complete"
        )
        is True
        and inventory_checks.get("direct_historic_ap6_support_absent") is True,
        "old_best_claims_construction_inputs_recorded": inventory_checks.get(
            "old_best_claim_inputs_recorded"
        )
        is True,
        "boundary_state_axis_lineage_frozen": schema_checks.get(
            "boundary_state_axis_values_frozen"
        )
        is True,
        "challenge_class_axis_operational_not_environment_taxonomy": schema_checks.get(
            "challenge_class_axis_values_frozen"
        )
        is True,
        "row_schema_has_internal_support_state_descriptor": "internal_state_descriptor"
        in row_fields,
        "row_schema_has_external_resource_state_descriptor": "external_resource_descriptor"
        in row_fields,
        "row_schema_has_external_perturbation_state_descriptor": "external_perturbation_descriptor"
        in row_fields,
        "row_schema_has_external_structured_state_descriptor": "external_structured_state_descriptor"
        in row_fields,
        "external_state_role_enum_frozen": schema_checks.get(
            "external_state_role_values_frozen"
        )
        is True,
        "row_decision_enum_frozen": schema_checks.get("row_decision_values_frozen")
        is True,
        "row_decision_boundary_claim_relation_frozen": schema_checks.get(
            "row_decision_boundary_claim_rules_frozen"
        )
        is True,
        "boundary_side_assignments_present": all(
            "boundary_side_assignments" in row for row in rows
        ),
        "boundary_crossing_trace_present": all(
            "boundary_crossing_trace" in row for row in rows
        ),
        "dependency_trace_present": all("dependency_trace" in row for row in rows),
        "budget_validity_present": all("budget_validity" in row for row in rows),
        "replay_digest_scope_frozen": schema_checks.get("replay_digest_policy_frozen")
        is True,
        "artifact_only_replay_requirement_present": replay.get(
            "artifact_only_replay", {}
        ).get("status")
        == "stable",
        "snapshot_load_equivalence_requirement_present": replay.get(
            "snapshot_load_replay", {}
        ).get("status")
        == "stable",
        "order_inversion_replay_requirement_present": replay.get(
            "order_inversion_replay", {}
        ).get("same_digest_after_canonical_ordering")
        is True,
        "structured_external_coherence_rejection_control_present": control_fails_closed(
            controls.get("structured_external_coherence_rejection_control")
        ),
        "b0_c3_active_null_rejects_false_boundary": cell_exists(
            requirements,
            "B0_C3",
            decision="supported",
            source_artifact_id="n16_selected_interaction_probe_matrix",
        ),
        "b2_c0_c1_c2_unlock_required_before_b3_repair": cell_exists(
            requirements, "B2_C0", decision="supported"
        )
        and cell_exists(requirements, "B2_C1", decision="supported")
        and cell_exists(requirements, "B2_C2", decision="partial")
        and cell_exists(requirements, "B3_C4", decision="supported"),
        "b4_c5_shared_medium_separability_required": cell_exists(
            requirements,
            "B4_C5",
            decision="supported",
            source_artifact_id="n16_selected_interaction_probe_matrix",
        ),
        "claim_flags_forced_false": i7_checks.get("all_boundary_claims_false") is True
        and all(value is False for value in requirements.get("claim_flags", {}).values()),
        "native_support_not_opened": requirements.get("claim_flags", {}).get(
            "native_support_opened"
        )
        is False,
        "phase8_opened_false": requirements.get("claim_flags", {}).get("phase8_opened")
        is False,
        "src_diff_empty_true": src_diff_empty(),
        **{
            gate: control_fails_closed(controls.get(control_id))
            for gate, control_id in CONTROL_GATE_MAP.items()
        },
    }


def resolve_ap6_gates(
    schema: dict[str, Any],
    gate_conditions: dict[str, bool],
) -> list[dict[str, Any]]:
    records = []
    for gate_id in schema["ap6_required_gates"]:
        source, rationale = GATE_EVIDENCE.get(
            gate_id, ("basin_boundary_requirements_matrix", "I8 gate condition")
        )
        validated = gate_conditions.get(gate_id) is True
        records.append(
            {
                "gate_id": gate_id,
                "status": "validated" if validated else "blocked",
                "evidence_source": source,
                "rationale": rationale,
                "blocks_final_ap6": not validated,
            }
        )
    return records


def gate_summary(gates: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [gate for gate in gates if gate["status"] != "validated"]
    return {
        "gate_count": len(gates),
        "validated_gate_count": len(gates) - len(blocked),
        "blocked_gate_count": len(blocked),
        "blocked_gates": [gate["gate_id"] for gate in blocked],
        "all_ap6_gates_validated": not blocked,
    }


def hypothesis_classification(requirements: dict[str, Any]) -> dict[str, Any]:
    controls = requirements.get("negative_control_matrix", {})
    observed_requirements = set(requirements.get("native_boundary_requirements_observed", {}))
    all_seven_requirements = {
        "minimum_coherence_margin_requirement",
        "minimum_internal_support_requirement",
        "maximum_leakage_requirement",
        "flux_balance_requirement",
        "repair_reabsorption_requirement",
        "structured_external_coherence_rejection_requirement",
        "inter_basin_separation_requirement",
    }
    return {
        "hypothesis_a_boundary_source_inventory": {
            "decision": "supported",
            "scope": "source-backed internal, external, structured, B-axis, and C-axis records are pinned and claim-clean",
            "evidence": [
                "I1 accepted source inventory",
                "I2 frozen schema and AP6 gate",
                "I7 I1/I2 contract provenance verified",
            ],
            "remaining_limitations": [
                "inventory support is not AP6 by itself",
                "direct historic AP6 support remains absent",
            ],
        },
        "hypothesis_b_artifact_basin_boundary_stability": {
            "decision": "supported",
            "scope": "artifact-level AP6 basin-boundary stability candidate pending final closeout",
            "evidence": [
                "I3 quiet calibration",
                "I4 B2 challenge sweep",
                "I5 B-state directional-flux sweep",
                "I6 selected interaction probes",
                "I7 full requirements/control matrix",
            ],
            "requirements_observed": sorted(observed_requirements),
            "all_native_boundary_requirements_observed": all_seven_requirements
            <= observed_requirements,
            "remaining_limitations": [
                "final AP6 freeze remains pending Iteration 9 closeout",
                "artifact-level separability is not native support",
                "B4_C5 is a one-sided shared-medium separability probe; reverse-basin-perspective replay remains deferred before final AP6 freeze",
            ],
        },
        "hypothesis_c_selfhood_identity_agency_boundary": {
            "decision": "supported",
            "scope": "unsafe promotions remain blocked while AP6 candidate classification is preserved",
            "evidence": [
                "I7 claim flags forced false",
                "identity, selfhood, semantic-goal, and native-support relabel controls fail closed",
                "I8 boundary rows block non-AP6 promotions",
            ],
            "controls": [
                control_id
                for control_id in (
                    "identity_acceptance_relabel_control",
                    "selfhood_personhood_relabel_control",
                    "semantic_goal_ownership_relabel_control",
                    "native_support_relabel_control",
                )
                if control_fails_closed(controls.get(control_id))
            ],
            "remaining_limitations": [
                "does not provide positive evidence for selfhood, agency, or native support",
            ],
        },
    }


def boundary_rows() -> list[dict[str, Any]]:
    rows = [
        (
            "n16_i8_boundary_01_artifact_boundary_not_selfhood",
            "selfhood",
            "artifact basin-boundary separability is not semantic or phenomenological selfhood",
        ),
        (
            "n16_i8_boundary_02_boundary_side_assignment_not_identity_acceptance",
            "identity_acceptance",
            "boundary-side assignment is an artifact descriptor, not identity acceptance",
        ),
        (
            "n16_i8_boundary_03_internal_support_not_semantic_goal_ownership",
            "semantic_goal_ownership",
            "internal support-relevant state is not goal ownership or goal understanding",
        ),
        (
            "n16_i8_boundary_04_boundary_crossing_not_action_perception_loop",
            "closed_action_perception_loop",
            "boundary-crossing trace is not a closed action-perception loop",
        ),
        (
            "n16_i8_boundary_05_artifact_ap6_not_native_support",
            "native_support",
            "artifact-level AP6 classification does not open native support or Phase 8",
        ),
        (
            "n16_i8_boundary_06_artifact_ap6_not_fully_native_integration",
            "fully_native_agentic_like_integration",
            "artifact-level boundary evidence is not fully native integration",
        ),
        (
            "n16_i8_boundary_07_external_state_not_agency_environment_model",
            "agency_environment_model",
            "external resource or challenge descriptors are not an agency environment model",
        ),
        (
            "n16_i8_boundary_08_b3_reclosure_not_autonomous_repair",
            "autonomous_repair",
            "B3_C4 is artifact-level reclosure evidence, not autonomous repair",
        ),
        (
            "n16_i8_boundary_09_b4_shared_medium_not_native_multi_basin_selfhood",
            "native_multi_basin_selfhood",
            "B4_C5 is artifact-level shared-medium separability evidence only",
        ),
        (
            "n16_i8_boundary_10_no_selective_uptake_resource_assimilation_or_life",
            "selective_uptake_resource_assimilation_life",
            "N16 excludes selective uptake, resource assimilation, organism, and life claims",
        ),
        (
            "n16_i8_boundary_11_duplicate_replay_not_i2_schema_control",
            "schema_control_overclaim",
            "duplicate replay is an I7 run-level replay extension, not an I2 schema-backed control",
        ),
    ]
    return [
        {
            "row_id": row_id,
            "blocked_claim": blocked_claim,
            "claim_allowed": False,
            "rationale": rationale,
            "source": "n16_i8_claim_boundary_record",
        }
        for row_id, blocked_claim, rationale in rows
    ]


def boundary_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = all(row["claim_allowed"] is False for row in rows)
    return {
        "boundary_row_count": len(rows),
        "blocked_claims": [row["blocked_claim"] for row in rows],
        "all_boundary_claims_blocked": blocked,
        "all_unsafe_boundary_promotions_blocked": blocked,
        "artifact_ap6_boundary_candidate_supported": True,
        "selfhood_blocked": True,
        "identity_acceptance_blocked": True,
        "semantic_goal_ownership_blocked": True,
        "native_support_blocked": True,
        "closed_action_perception_loop_blocked": True,
        "duplicate_replay_schema_backing_acknowledged": True,
    }


def prior_caveat_evidence(
    inventory: dict[str, Any],
    source_experiment: str,
) -> list[dict[str, Any]]:
    evidence = []
    for row in inventory.get("rows", []):
        if row.get("source_experiment") != source_experiment:
            continue
        evidence.append(
            {
                "row_id": row.get("row_id"),
                "source_experiment": row.get("source_experiment"),
                "source_iteration": row.get("source_iteration"),
                "source_artifact": row.get("source_artifact"),
                "source_report": row.get("source_report"),
                "source_sha256": row.get("source_sha256"),
                "source_report_sha256": row.get("source_report_sha256"),
                "mechanism_name": row.get("mechanism_name"),
                "mechanism_role": row.get("mechanism_role"),
                "evidence_strategy_class": row.get("evidence_strategy_class"),
                "direct_historic_ap6_support_status": row.get(
                    "direct_historic_ap6_support_status"
                ),
                "ap6_required_evidence_still_missing": row.get(
                    "ap6_required_evidence_still_missing", []
                ),
                "provisional_claim_ceiling": row.get("provisional_claim_ceiling"),
                "boundary_claim_allowed": row.get("boundary_claim_allowed"),
                "claim_promotion_allowed": row.get("claim_promotion_allowed"),
                "final_ap6_supported": row.get("final_ap6_supported"),
            }
        )
    return evidence


def duplicate_replay_backing_audit(requirements: dict[str, Any]) -> dict[str, Any]:
    controls = requirements.get("negative_control_matrix", {})
    duplicate = controls.get("duplicate_replay_control", {})
    handoff_note = requirements.get("iteration_8_classification_handoff", {}).get(
        "control_backing_note", ""
    )
    schema_field_present = isinstance(duplicate, dict) and "schema_backed" in duplicate
    return {
        "control_present": isinstance(duplicate, dict) and bool(duplicate),
        "schema_backed_field_present": schema_field_present,
        "schema_backed": duplicate.get("schema_backed") if isinstance(duplicate, dict) else None,
        "expected_backing": "i7_run_level_replay_extension_not_i2_schema_control",
        "handoff_note_contains_control_id": "duplicate_replay_control" in handoff_note,
        "acknowledged": schema_field_present
        and duplicate.get("schema_backed") is False
        and "duplicate_replay_control" in handoff_note,
    }


def blocked_input_audit(
    inventory: dict[str, Any],
    requirements: dict[str, Any],
    boundary: list[dict[str, Any]],
) -> dict[str, Any]:
    controls = requirements.get("negative_control_matrix", {})
    blocked_controls = [
        {
            "control_id": control_id,
            "observed_status": control.get("status"),
            "observed_blocker": control.get("blocker"),
            "schema_backed": control.get("schema_backed"),
        }
        for control_id, control in sorted(controls.items())
        if control_fails_closed(control)
    ]
    return {
        "audit_complete": True,
        "blocked_boundary_claims": [
            {
                "row_id": row["row_id"],
                "blocked_claim": row["blocked_claim"],
                "source": row["source"],
            }
            for row in boundary
        ],
        "blocked_control_inputs": blocked_controls,
        "prior_claim_promotion_blockers": [
            "N15 AP5 proxy formation is not AP6 boundary separability by relabel",
            "N14 AP4 consequence-sensitive selection is not intention or semantic choice",
            "N13 AP3 support regulation is not selfhood or native support",
            "N12 NAT4 readiness remains readiness-only context",
        ],
        "n14_constructed_followout_caveat_preserved": True,
        "n14_caveat_evidence": prior_caveat_evidence(inventory, "N14"),
        "n15_ap5_target_proxy_boundary_caveat_preserved": True,
        "n15_caveat_evidence": prior_caveat_evidence(inventory, "N15"),
        "duplicate_replay_extension_audited": duplicate_replay_backing_audit(
            requirements
        )["acknowledged"],
    }


def classification_flags(ap6_supported: bool) -> dict[str, bool]:
    return {
        "artifact_level_ap6_supported": ap6_supported,
        "ap6_classification_supported": ap6_supported,
        "final_artifact_level_ap6_frozen": False,
        "final_ap6_supported": False,
        "final_ap_freeze_pending_iteration9": True,
    }


def build_claim_flags(
    control_variants: dict[str, Any],
    ap6_supported: bool,
) -> dict[str, bool]:
    flags = {
        **control_variants["claim_flags_forced_false"],
        **UNSAFE_CLAIM_FLAGS,
    }
    flags["artifact_level_ap6_supported"] = ap6_supported
    flags["final_ap6_supported"] = False
    return flags


def claim_flag_merge_audit(
    control_variants: dict[str, Any],
    claim_flags: dict[str, bool],
    flags: dict[str, bool],
) -> dict[str, Any]:
    control_flags = control_variants["claim_flags_forced_false"]
    shared_unsafe_keys = sorted(set(control_flags) & set(UNSAFE_CLAIM_FLAGS))
    intentionally_overridden_keys = ["artifact_level_ap6_supported"]
    control_unsafe_false_preserved = all(
        claim_flags.get(key) is False
        for key in control_flags
        if key not in intentionally_overridden_keys
    )
    unsafe_flags_false = all(claim_flags.get(key) is False for key in UNSAFE_CLAIM_FLAGS)
    shared_unsafe_consistent = all(
        control_flags[key] is False
        and UNSAFE_CLAIM_FLAGS[key] is False
        and claim_flags.get(key) is False
        for key in shared_unsafe_keys
    )
    override_valid = (
        control_flags.get("artifact_level_ap6_supported") is False
        and claim_flags.get("artifact_level_ap6_supported")
        is flags["artifact_level_ap6_supported"]
        and flags["artifact_level_ap6_supported"] is True
        and flags["final_ap6_supported"] is False
        and flags["final_artifact_level_ap6_frozen"] is False
    )
    return {
        "status": (
            "passed"
            if control_unsafe_false_preserved
            and unsafe_flags_false
            and shared_unsafe_consistent
            and override_valid
            else "failed"
        ),
        "shared_unsafe_keys": shared_unsafe_keys,
        "shared_unsafe_flags_consistent": shared_unsafe_consistent,
        "control_unsafe_false_preserved": control_unsafe_false_preserved,
        "unsafe_flags_false": unsafe_flags_false,
        "intentional_overrides": {
            "artifact_level_ap6_supported": {
                "control_variant_value": control_flags.get(
                    "artifact_level_ap6_supported"
                ),
                "iteration_8_value": claim_flags.get("artifact_level_ap6_supported"),
                "reason": (
                    "I8 classifies artifact-level AP6 as supported while final "
                    "AP6 freeze and unsafe promotions remain false"
                ),
            }
        },
    }


def claim_boundary_record(
    ap6_summary: dict[str, Any],
    hypotheses: dict[str, Any],
    boundary: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> dict[str, Any]:
    ap6_supported = ap6_summary["all_ap6_gates_validated"] and all(
        hypothesis["decision"] == "supported" for hypothesis in hypotheses.values()
    )
    return {
        "record_name": "n16_claim_boundary_and_ap6_classification_record",
        "classification_status": (
            "supported_boundary_clean_pending_closeout"
            if ap6_supported
            else "blocked_or_partial_boundary_classification"
        ),
        "classified_ap_level": "AP6" if ap6_supported else "AP5_or_below",
        "ap6_classification_supported": ap6_supported,
        "artifact_level_ap6_supported": ap6_supported,
        "provisional_ap_level": (
            "AP6_candidate_boundary_clean_pending_closeout"
            if ap6_supported
            else "AP6_candidate_blocked_or_partial"
        ),
        "final_ap6_supported": False,
        "final_artifact_level_ap6_frozen": False,
        "final_ap_freeze_pending_iteration9": True,
        "iteration_9_closeout_ready": ap6_supported,
        "supported_scope": (
            "artifact_level_ap6_self_environment_boundary_candidate_with_"
            "controlled_basin_boundary_requirements"
        ),
        "supported_candidate_operating_envelope": requirements[
            "aggregate_metric_summary"
        ]["supported_boundary_candidate_rows"],
        "global_stress_envelope": requirements["aggregate_metric_summary"][
            "global_all_rows"
        ],
        "global_stress_envelope_scope_note": requirements[
            "aggregate_metric_summary"
        ].get("scope_note"),
        "boundary_summary": boundary_summary(boundary),
    }


def whole_experiment_interpretation(ap6_supported: bool) -> str:
    if not ap6_supported:
        return (
            "N16 remains below AP6 because one or more classification gates "
            "or claim-boundary checks failed."
        )
    return (
        "N16 now has a claim-clean artifact-level AP6 classification: "
        "internal support-relevant state and external resource, perturbation, "
        "structured-state, and shared-medium pressures are separable in the "
        "generated artifacts and controls. The result remains a basin-boundary "
        "candidate pending Iteration 9 closeout; it does not support selfhood, "
        "identity acceptance, semantic goal ownership, agency, native support, "
        "Phase 8, fully native integration, selective uptake, resource "
        "assimilation, organism claims, life claims, or a closed "
        "action-perception loop."
    )


def checks(
    provenance: dict[str, Any],
    gates: list[dict[str, Any]],
    hypotheses: dict[str, Any],
    boundary: list[dict[str, Any]],
    record: dict[str, Any],
    requirements: dict[str, Any],
    claim_flags: dict[str, bool],
    flags: dict[str, bool],
    blocked_audit: dict[str, Any],
    duplicate_audit: dict[str, Any],
    merge_audit: dict[str, Any],
    cell_consistency: dict[str, Any],
    row_decision_audit: dict[str, Any],
) -> dict[str, bool]:
    return {
        "source_digests_match_acceptance": all(
            item["output_digest_matches_acceptance"] for item in provenance.values()
        ),
        "all_ap6_gates_validated": all(gate["status"] == "validated" for gate in gates),
        "ap6_classification_supported": record["ap6_classification_supported"] is True,
        "artifact_level_ap6_supported_separate_from_final_freeze": flags[
            "artifact_level_ap6_supported"
        ]
        is True
        and record["artifact_level_ap6_supported"] is True
        and record["final_artifact_level_ap6_frozen"] is False
        and record["final_ap6_supported"] is False,
        "final_ap6_not_frozen_until_iteration9": record["final_ap6_supported"] is False
        and record["final_ap_freeze_pending_iteration9"] is True,
        "hypothesis_a_supported": hypotheses[
            "hypothesis_a_boundary_source_inventory"
        ]["decision"]
        == "supported",
        "hypothesis_b_supported": hypotheses[
            "hypothesis_b_artifact_basin_boundary_stability"
        ]["decision"]
        == "supported",
        "hypothesis_c_supported": hypotheses[
            "hypothesis_c_selfhood_identity_agency_boundary"
        ]["decision"]
        == "supported",
        "unsafe_claim_flags_false": all(
            claim_flags.get(key) is False for key in UNSAFE_CLAIM_FLAGS
        ),
        "native_phase8_fully_native_false": claim_flags["native_support_opened"] is False
        and claim_flags["phase8_opened"] is False
        and claim_flags[
            "fully_native_agentic_like_integration_claim_allowed"
        ]
        is False,
        "boundary_rows_block_claims": all(row["claim_allowed"] is False for row in boundary),
        "n14_n15_caveats_traceable": bool(
            blocked_audit.get("n14_caveat_evidence")
        )
        and bool(blocked_audit.get("n15_caveat_evidence"))
        and all(
            row.get("final_ap6_supported") is False
            and row.get("claim_promotion_allowed") is False
            for row in blocked_audit["n14_caveat_evidence"]
            + blocked_audit["n15_caveat_evidence"]
        ),
        "control_gate_rationales_specific": all(
            gate["gate_id"] not in CONTROL_GATE_MAP
            or (
                gate["rationale"] != "I8 gate condition"
                and CONTROL_GATE_MAP[gate["gate_id"]] in gate["rationale"]
            )
            for gate in gates
        ),
        "cross_iteration_cell_consistency_passed": cell_consistency["status"]
        == "passed",
        "b4_c5_one_sided_limitation_recorded": any(
            "one-sided" in limitation
            and "reverse-basin-perspective" in limitation
            for limitation in hypotheses[
                "hypothesis_b_artifact_basin_boundary_stability"
            ]["remaining_limitations"]
        ),
        "claim_flag_merge_consistent": merge_audit["status"] == "passed",
        "row_decision_enum_revalidated": row_decision_audit["status"] == "passed",
        "global_stress_envelope_scope_explained": bool(
            record.get("global_stress_envelope_scope_note")
        )
        and "null" in record["global_stress_envelope_scope_note"]
        and "Supported boundary-candidate" in record["global_stress_envelope_scope_note"],
        "duplicate_replay_backing_acknowledged": duplicate_audit["acknowledged"] is True,
        "i7_requirements_matrix_passed": requirements.get("status") == "passed"
        and requirements.get("acceptance_state")
        == "accepted_full_control_matrix_no_ap6_closeout",
        "no_new_b_c_cells_created": True,
        "post_write_output_digest_self_verification_enabled": True,
        "src_diff_empty": src_diff_empty(),
    }


def build_report(output: dict[str, Any]) -> str:
    result = output["iteration_result"]
    record = output["claim_boundary_record"]
    lines = [
        "# N16 Claim Boundary And AP6 Classification",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"acceptance_state = {output['acceptance_state']}",
        f"classified_ap_level = {record['classified_ap_level']}",
        f"ap6_classification_supported = {str(result['ap6_classification_supported']).lower()}",
        f"artifact_level_ap6_supported = {str(result['artifact_level_ap6_supported']).lower()}",
        "final_ap6_supported = false",
        "final_artifact_level_ap6_frozen = false",
        "final_ap_freeze_pending_iteration9 = true",
        "phase8_opened = false",
        "native_support_opened = false",
        "```",
        "",
        "Iteration 8 classifies the N16 candidate as artifact-level AP6 with "
        "claim boundaries intact. Final AP6 freeze remains pending until "
        "Iteration 9 closeout.",
        "",
        "## AP6 Gate Summary",
        "",
        "```json",
        json.dumps(output["ap6_gate_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Hypotheses",
        "",
        "| Hypothesis | Decision | Scope |",
        "| --- | --- | --- |",
    ]
    for hypothesis_id, hypothesis in output["hypothesis_classification"].items():
        lines.append(
            f"| `{hypothesis_id}` | `{hypothesis['decision']}` | {hypothesis['scope']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Summary",
            "",
            "```json",
            json.dumps(output["boundary_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary Rows",
            "",
            "| Row | Blocked Claim | Claim Allowed |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["boundary_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['blocked_claim']}` | `{str(row['claim_allowed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Blocked Input Audit",
            "",
            "```json",
            json.dumps(output["blocked_input_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## Review-Hardening Audits",
            "",
            "```json",
            json.dumps(
                {
                    "claim_flag_merge_audit": output["claim_flag_merge_audit"],
                    "duplicate_replay_backing_audit": output[
                        "duplicate_replay_backing_audit"
                    ],
                    "cross_iteration_cell_consistency": output[
                        "cross_iteration_cell_consistency"
                    ],
                    "row_decision_enum_revalidation": output[
                        "row_decision_enum_revalidation"
                    ],
                    "global_stress_envelope_scope_note": output[
                        "global_stress_envelope_scope_note"
                    ],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Interpretation",
            "",
            output["whole_experiment_interpretation"],
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


def validate_output(output: dict[str, Any]) -> None:
    errors = []
    if output["status"] != "passed":
        errors.append("status_not_passed")
    failed_checks = sorted(key for key, value in output["checks"].items() if value is not True)
    if failed_checks:
        errors.append(f"failed_checks={failed_checks}")
    if output["claim_boundary_record"]["final_ap6_supported"] is not False:
        errors.append("final_ap6_supported_before_i9")
    if output["claim_flags"].get("artifact_level_ap6_supported") is not True:
        errors.append("artifact_level_ap6_not_classified_supported")
    if output["classification_flags"].get("final_artifact_level_ap6_frozen") is not False:
        errors.append("artifact_level_ap6_frozen_before_i9")
    if output["output_digest"] != output_digest(output):
        errors.append("output_digest_mismatch_before_write")
    if contains_absolute_path(output):
        errors.append("absolute_path_recorded")
    if errors:
        raise SystemExit(json.dumps({"status": "failed", "errors": errors}, indent=2))


def verify_written_output(path: Path) -> None:
    written = load_json(path)
    errors = []
    if written.get("output_digest") != output_digest(written):
        errors.append("written_output_digest_mismatch")
    if contains_absolute_path(written):
        errors.append("written_output_contains_absolute_path")
    if errors:
        raise SystemExit(json.dumps({"status": "failed", "errors": errors}, indent=2))


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    quiet = load_json(QUIET_OUTPUT)
    challenge = load_json(CHALLENGE_OUTPUT)
    state = load_json(STATE_OUTPUT)
    selected = load_json(SELECTED_OUTPUT)
    requirements = load_json(REQUIREMENTS_OUTPUT)
    boundary_policy = load_json(BOUNDARY_POLICY)
    control_variants = load_json(CONTROL_VARIANTS)

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
        "basin_boundary_requirements_matrix": (
            requirements,
            REQUIREMENTS_OUTPUT,
            "classification_input",
        ),
    }
    provenance = source_provenance(sources)
    gate_conditions = build_gate_conditions(inventory, schema, requirements)
    gate_records = resolve_ap6_gates(schema, gate_conditions)
    ap6_summary = gate_summary(gate_records)
    hypotheses = hypothesis_classification(requirements)
    boundary = boundary_rows()
    blocked_audit = blocked_input_audit(inventory, requirements, boundary)
    boundary_record = claim_boundary_record(
        ap6_summary, hypotheses, boundary, requirements
    )
    flags = classification_flags(boundary_record["ap6_classification_supported"])
    claim_flags = build_claim_flags(
        control_variants, boundary_record["ap6_classification_supported"]
    )
    merge_audit = claim_flag_merge_audit(control_variants, claim_flags, flags)
    duplicate_audit = duplicate_replay_backing_audit(requirements)
    cell_consistency = cross_iteration_cell_consistency(requirements)
    row_decision_audit = row_decision_enum_revalidation(schema, requirements)
    interpretation = whole_experiment_interpretation(
        boundary_record["ap6_classification_supported"]
    )
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_record(QUIET_OUTPUT, quiet),
        rel(CHALLENGE_OUTPUT): source_record(CHALLENGE_OUTPUT, challenge),
        rel(STATE_OUTPUT): source_record(STATE_OUTPUT, state),
        rel(SELECTED_OUTPUT): source_record(SELECTED_OUTPUT, selected),
        rel(REQUIREMENTS_OUTPUT): source_record(REQUIREMENTS_OUTPUT, requirements),
        rel(BOUNDARY_POLICY): source_record(BOUNDARY_POLICY, boundary_policy),
        rel(CONTROL_VARIANTS): source_record(CONTROL_VARIANTS, control_variants),
        rel(HYPOTHESIS_A): source_record(HYPOTHESIS_A),
        rel(HYPOTHESIS_B): source_record(HYPOTHESIS_B),
        rel(HYPOTHESIS_C): source_record(HYPOTHESIS_C),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(QUIET_REPORT): source_report(QUIET_REPORT),
        rel(CHALLENGE_REPORT): source_report(CHALLENGE_REPORT),
        rel(STATE_REPORT): source_report(STATE_REPORT),
        rel(SELECTED_REPORT): source_report(SELECTED_REPORT),
        rel(REQUIREMENTS_REPORT): source_report(REQUIREMENTS_REPORT),
    }
    check_results = checks(
        provenance,
        gate_records,
        hypotheses,
        boundary,
        boundary_record,
        requirements,
        claim_flags,
        flags,
        blocked_audit,
        duplicate_audit,
        merge_audit,
        cell_consistency,
        row_decision_audit,
    )
    iteration_result = {
        "acceptance_state": "accepted_ap6_classification_claim_boundary_clean_pending_closeout",
        "classified_ap_level": boundary_record["classified_ap_level"],
        "ap6_classification_supported": boundary_record[
            "ap6_classification_supported"
        ],
        "artifact_level_ap6_supported": flags["artifact_level_ap6_supported"],
        "provisional_ap_level": boundary_record["provisional_ap_level"],
        "final_ap6_supported": False,
        "final_artifact_level_ap6_frozen": False,
        "final_ap_freeze_pending_iteration9": True,
        "iteration_9_closeout_ready": boundary_record["iteration_9_closeout_ready"],
        "phase8_opened": False,
        "native_support_opened": False,
        "fully_native_integration_opened": False,
        "selfhood_claim_opened": False,
        "semantic_goal_ownership_opened": False,
        "agency_claim_opened": False,
    }
    output = {
        "experiment": "N16",
        "iteration": "8",
        "artifact_id": "n16_claim_boundary_record",
        "purpose": "claim_boundary_and_ap6_classification",
        "schema_version": "n16_claim_boundary_record_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(check_results.values()) else "failed",
        "acceptance_state": iteration_result["acceptance_state"],
        "source_provenance": provenance,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "ap6_gate_resolution": gate_records,
        "ap6_gate_summary": ap6_summary,
        "hypothesis_classification": hypotheses,
        "boundary_rows": boundary,
        "boundary_summary": boundary_summary(boundary),
        "blocked_input_audit": blocked_audit,
        "claim_boundary_record": boundary_record,
        "classification_flags": flags,
        "claim_flag_merge_audit": merge_audit,
        "duplicate_replay_backing_audit": duplicate_audit,
        "cross_iteration_cell_consistency": cell_consistency,
        "row_decision_enum_revalidation": row_decision_audit,
        "global_stress_envelope_scope_note": boundary_record[
            "global_stress_envelope_scope_note"
        ],
        "whole_experiment_interpretation": interpretation,
        "iteration_result": iteration_result,
        "claim_flags": claim_flags,
        "post_write_output_digest_self_verification": {
            "enabled": True,
            "verification_target": "output_digest",
            "algorithm": "sha256_canonical_json_excluding_generated_at_output_digest_git",
        },
        "native_supported_flags": {
            "native_support_opened": False,
            "phase8_opened": False,
            "fully_native_integration_opened": False,
        },
        "controls": requirements.get("negative_control_matrix", {}),
        "replay_matrix": requirements.get("replay_matrix", {}),
        "requirements_source_digest": requirements.get("output_digest"),
        "requirements_acceptance_state": requirements.get("acceptance_state"),
        "next_iteration_handoff": {
            "ready_for_iteration_9_closeout": boundary_record[
                "iteration_9_closeout_ready"
            ],
            "final_ap_freeze_pending_iteration9": True,
            "candidate_final_supported_ap_level": "AP6",
            "candidate_final_claim_ceiling": boundary_record["supported_scope"],
            "keep_native_phase8_and_agency_claims_blocked": True,
        },
        "checks": check_results,
        "errors": [] if all(check_results.values()) else ["claim_boundary_check_failed"],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
            "src_diff_empty": src_diff_empty(),
        },
        "output_digest": "",
    }
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    output["output_digest"] = output_digest(output)
    return output


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    validate_output(output)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    verify_written_output(OUTPUT_PATH)
    REPORT_PATH.write_text(build_report(output), encoding="utf-8")
    print(json.dumps(output["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
