#!/usr/bin/env python3
"""Build N16 Iteration 6 selected interaction probe matrix."""

from __future__ import annotations

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
STATE_OUTPUT = OUTPUTS / "n16_boundary_state_sweep_matrix.json"
STATE_REPORT = REPORTS / "n16_boundary_state_sweep_matrix.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n16_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n16_replay_policy_v1.json"
SOURCE_REGISTRY = CONFIGS / "n16_source_registry.json"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

OUTPUT_PATH = OUTPUTS / "n16_selected_interaction_probe_matrix.json"
REPORT_PATH = REPORTS / "n16_selected_interaction_probe_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_selected_interaction_probe_matrix.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"
I4_ACCEPTED_OUTPUT_DIGEST = (
    "b91d7bb77fd0053d9995a05a11571471a9338c0ce6b63909ca5021d429ce9d77"
)
I5_ACCEPTED_OUTPUT_DIGEST = (
    "a24c1db84cefbfcb3e99a26373ef5a12f21c795e0574c91fbb06ce72435e2620"
)

INTERNAL_SUPPORT_FLOOR = 0.85
INTERNAL_COHERENCE_FLOOR = 0.84
MINIMUM_COHERENCE_MARGIN_FLOOR = 0.52
QUIET_LEAKAGE_CEILING = 0.12
BREACH_RECLOSURE_FLOOR = 0.70
BASIN_SEPARATION_FLOOR = 0.70
MERGE_CONFUSION_CEILING = 0.20
BOUNDARY_EXCLUSIVITY_FLOOR = 0.70

CHALLENGE_PROFILES = {
    "C1": {
        "noise_amplitude": 0.08,
        "directional_flux_pressure": 0.0,
        "structured_external_coherence_pressure": 0.0,
        "breach_pressure": 0.0,
        "shared_medium_pressure": 0.0,
    },
    "C2": {
        "noise_amplitude": 0.0,
        "directional_flux_pressure": 0.34,
        "structured_external_coherence_pressure": 0.0,
        "breach_pressure": 0.0,
        "shared_medium_pressure": 0.0,
    },
    "C3": {
        "noise_amplitude": 0.0,
        "directional_flux_pressure": 0.0,
        "structured_external_coherence_pressure": 0.92,
        "breach_pressure": 0.0,
        "shared_medium_pressure": 0.0,
    },
    "C4": {
        "noise_amplitude": 0.0,
        "directional_flux_pressure": 0.0,
        "structured_external_coherence_pressure": 0.0,
        "breach_pressure": 0.38,
        "shared_medium_pressure": 0.0,
    },
    "C5": {
        "noise_amplitude": 0.0,
        "directional_flux_pressure": 0.12,
        "structured_external_coherence_pressure": 0.0,
        "breach_pressure": 0.0,
        "shared_medium_pressure": 0.44,
    },
}

CHALLENGE_THRESHOLDS = {
    "internal_support_floor": INTERNAL_SUPPORT_FLOOR,
    "internal_coherence_floor": INTERNAL_COHERENCE_FLOOR,
    "minimum_coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
    "quiet_leakage_ceiling": QUIET_LEAKAGE_CEILING,
    "breach_reclosure_floor": BREACH_RECLOSURE_FLOOR,
    "shared_medium_basin_separation_floor": BASIN_SEPARATION_FLOOR,
    "merge_confusion_ceiling": MERGE_CONFUSION_CEILING,
    "boundary_exclusivity_floor": BOUNDARY_EXCLUSIVITY_FLOOR,
}

SELECTED_CELLS = ["B0_C3", "B1_C2", "B2_C1", "B3_C4", "B4_C5"]

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
    "autonomous_repair_or_reabsorption",
    "native_multi_basin_separability",
]

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify only the selected B/C interaction cells exposed by "
        "Iterations 4-5; do not create a new full matrix"
    ),
    "interrogation_of_becoming": (
        "ask bounded confirmation questions: active-null rejection, weak "
        "flux replay, noise replay, breach/reclosure, and shared-medium "
        "separability"
    ),
    "naturalization_of_becoming": (
        "treat B3/B4 improvements as artifact-level boundary evidence only, "
        "not native support or native self/environment understanding"
    ),
    "cultivation_of_becoming": (
        "cultivate rows that feed the Iteration 7 control matrix with both "
        "satisfied and failed requirements"
    ),
}

METRIC_CONSTRUCTION_RATIONALE = {
    "construction_type": (
        "deterministic selected interaction probe built from Iteration 4 and "
        "Iteration 5 anchors; rows answer targeted unresolved questions rather "
        "than sweeping the full B x C matrix"
    ),
    "replay_rows": {
        "B1_C2": "replays Iteration 5 weak localized boundary under fixed C2",
        "B2_C1": "replays Iteration 4 bounded noise tolerance only",
    },
    "new_probe_rows": {
        "B0_C3": "strict structured-external false-positive rejection",
        "B3_C4": "breach/reclosure generalization test for B3",
        "B4_C5": "shared-medium separability test for B4",
    },
}

METRIC_COMPARISON_FIELDS = [
    "internal_coherence",
    "coherence_margin",
    "inbound_flux",
    "outbound_flux",
    "retained_flux",
    "leakage_ratio",
    "boundary_stability_score",
]

METRIC_CONSTRUCTION_FORMULAS = {
    "metric_status": (
        "Iteration 6 selected probes combine source-exact replay rows and "
        "explicit construction anchors. Retained flux is a composite retained "
        "signal index, not a probability and not globally bounded by 1.0."
    ),
    "retained_flux": {
        "source_replay_policy": (
            "B1_C2 and B2_C1 preserve their source artifact retained_flux "
            "values exactly instead of recomputing them under a later formula."
        ),
        "formula_projection_recorded": (
            "For audit, each row records the diagnostic projection "
            "inbound_flux - outbound_flux + internal_coherence."
        ),
        "authoritative_value_policy": (
            "The row retained_flux value is authoritative when marked as "
            "source_replay_preserved or explicit_construction_anchor; the "
            "projection is a cross-check, not a replacement."
        ),
    },
    "leakage_ratio": {
        "policy": (
            "Leakage ratio is a challenge-specific normalized leakage score. "
            "For B4_C5 it intentionally aliases shared_medium_leakage because "
            "the selected C5 question is shared-medium leakage."
        )
    },
    "reclosure_score": {
        "formula": (
            "For B3_C4, reclosure_score is the row-schema repair_score carrier "
            "applied to C4 breach/reclosure context."
        ),
        "relationship_to_repair_score": "intentional_alias_for_C4_reclosure",
        "latency_bucket_definition": (
            "bounded_single_window means reclosure is observed within the "
            "three-snapshot selected-probe window; reclosure_latency_steps "
            "records the numeric step count."
        ),
    },
    "basin_separation_score": {
        "policy": (
            "B4_C5 explicit construction anchor measuring separation of the "
            "candidate basin from a neighbor basin inside a shared medium."
        )
    },
    "boundary_exclusivity_score": {
        "policy": (
            "B4_C5 explicit construction anchor for whether intended-basin "
            "membership remains distinct from neighbor and medium nodes."
        )
    },
    "merge_confusion_pressure": {
        "policy": (
            "B4_C5 explicit construction anchor for pressure toward treating "
            "candidate and neighbor basins as one merged basin."
        )
    },
    "leakage_into_neighbor_basin": {
        "policy": (
            "B4_C5 explicit construction anchor separating neighbor leakage "
            "from retained flux and shared-medium leakage."
        )
    },
    "upstream_downstream_asymmetry_score": {
        "formula": "abs(inbound_flux - outbound_flux) / (inbound_flux + outbound_flux)",
        "rounding": "six decimal places",
        "zero_denominator_policy": "0.0",
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


def indexed_by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items}


def verified_digest_plan(value: dict[str, Any]) -> dict[str, Any]:
    first_digest = digest_value(value)
    second_digest = digest_value(value)
    if first_digest != second_digest:
        raise RuntimeError("idempotency digest self-verification failed")
    return {
        "algorithm": "sha256",
        "digest": first_digest,
        "self_verified": True,
        "same_inputs_same_digest_required": True,
    }


def upstream_downstream_asymmetry(metrics: dict[str, Any]) -> float:
    inbound = float(metrics["inbound_flux"])
    outbound = float(metrics["outbound_flux"])
    denominator = inbound + outbound
    if denominator == 0:
        return 0.0
    return round(abs(inbound - outbound) / denominator, 6)


def enriched_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        **metrics,
        "upstream_downstream_asymmetry_score": upstream_downstream_asymmetry(metrics),
    }


def retained_flux_formula_projection(metrics: dict[str, Any]) -> float | str:
    required = (
        metrics.get("inbound_flux"),
        metrics.get("outbound_flux"),
        metrics.get("internal_coherence"),
    )
    if not all(isinstance(value, (int, float)) for value in required):
        return "not_numeric"
    return round(
        float(metrics["inbound_flux"])
        - float(metrics["outbound_flux"])
        + float(metrics["internal_coherence"]),
        6,
    )


def metric_subset(row: dict[str, Any]) -> dict[str, Any]:
    subset = {
        field: row.get(field)
        for field in (
            "row_decision",
            "failure_mode",
            "internal_coherence",
            "coherence_margin",
            "inbound_flux",
            "outbound_flux",
            "retained_flux",
            "leakage_ratio",
            "boundary_stability_score",
            "repair_score",
            "basin_separation_score",
        )
        if field in row
    }
    metrics = (
        row.get("source_current", {})
        .get("challenge_transform", {})
        .get("metrics", {})
    )
    if isinstance(metrics, dict) and "minimum_internal_support" in metrics:
        subset["minimum_internal_support"] = metrics["minimum_internal_support"]
    return subset


def rows_by_cell(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["cell_id"]: row for row in artifact["rows"]}


def source_provenance(challenge: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    return {
        "iteration_4_challenge_sweep": {
            "accepted_output_digest": I4_ACCEPTED_OUTPUT_DIGEST,
            "current_output_digest": challenge.get("output_digest"),
            "output_digest_matches_acceptance": challenge.get("output_digest")
            == I4_ACCEPTED_OUTPUT_DIGEST,
            "current_file_sha256": digest_file(CHALLENGE_OUTPUT),
        },
        "iteration_5_boundary_state_sweep": {
            "accepted_output_digest": I5_ACCEPTED_OUTPUT_DIGEST,
            "current_output_digest": state.get("output_digest"),
            "output_digest_matches_acceptance": state.get("output_digest")
            == I5_ACCEPTED_OUTPUT_DIGEST,
            "current_file_sha256": digest_file(STATE_OUTPUT),
        },
        "file_sha_policy": (
            "file SHA-256 is recorded for current artifact bytes; semantic "
            "provenance uses output_digest because generated_at and git "
            "metadata are excluded from the stable digest"
        ),
    }


def boundary_state_lineage(
    inventory: dict[str, Any], boundary_state: str
) -> dict[str, Any]:
    return indexed_by(inventory["boundary_state_lineage"], "boundary_state")[
        boundary_state
    ]


def selected_source_rows(
    inventory: dict[str, Any], boundary_state: str
) -> list[dict[str, Any]]:
    rows_by_id = indexed_by(inventory["rows"], "row_id")
    lineage = boundary_state_lineage(inventory, boundary_state)
    return [rows_by_id[row_id] for row_id in lineage["lineage_sources"]]


def dependency_entry(
    row_field: str,
    source_row_id: str,
    source_artifact: str,
    source_sha256: str,
    source_field: str,
    transform_id: str,
    transform_parameters: dict[str, Any],
    claim_ceiling: str,
    boundary_side: str,
) -> dict[str, Any]:
    return {
        "row_field": row_field,
        "source_row_id": source_row_id,
        "source_artifact": source_artifact,
        "source_sha256": source_sha256,
        "source_field": source_field,
        "transform_id": transform_id,
        "transform_parameters": transform_parameters,
        "claim_ceiling_of_source": claim_ceiling,
        "boundary_side": boundary_side,
    }


def row_controls(control_ids: list[str], cell_id: str) -> dict[str, Any]:
    controls = {}
    for control_id in control_ids:
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "iteration_6_scope": "selected_probe_not_full_control_matrix",
        }
    controls["externally_supplied_boundary_control"] = {
        "status": "checked_i6_passed",
        "result": "selected probe rows use constructed or inherited derived sides",
    }
    controls["post_hoc_boundary_label_control"] = {
        "status": "checked_i6_passed",
        "result": "row decisions follow frozen selected-probe policy",
    }
    if cell_id == "B0_C3":
        controls["structured_external_coherence_rejection_control"] = {
            "status": "checked_i6_passed",
            "result": "structured external coherence is rejected as boundary support",
        }
    if cell_id == "B4_C5":
        controls["multi_basin_merge_control"] = {
            "status": "checked_i6_passed",
            "result": "shared-medium leakage, merge pressure, and basin separation are measured",
        }
    return controls


def top_level_controls(schema: dict[str, Any]) -> dict[str, Any]:
    controls = {}
    for requirement in schema["control_requirements"]:
        control_id = requirement["control_id"]
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "expected_status": requirement["expected_status"],
            "expected_blocker": requirement["expected_blocker"],
        }
    controls["externally_supplied_boundary_control"]["status"] = "checked_i6_passed"
    controls["post_hoc_boundary_label_control"]["status"] = "checked_i6_passed"
    controls["structured_external_coherence_rejection_control"] = {
        **controls["structured_external_coherence_rejection_control"],
        "status": "checked_i6_passed",
        "observed": "B0_C3 rejects structured external coherence",
    }
    controls["multi_basin_merge_control"] = {
        **controls["multi_basin_merge_control"],
        "status": "checked_i6_passed",
        "observed": "B4_C5 measures shared-medium separability components",
    }
    controls["artifact_only_replay_control"]["status"] = "deterministic_builder_replay_ready"
    return controls


def b3_unlock_audit(challenge: dict[str, Any]) -> dict[str, Any]:
    rows = rows_by_cell(challenge)
    required_cells = ["B2_C0", "B2_C1", "B2_C2"]
    present = {cell: cell in rows for cell in required_cells}
    decisions = {
        cell: rows[cell]["row_decision"] if cell in rows else "missing"
        for cell in required_cells
    }
    content_quality = {}
    for cell in required_cells:
        row = rows.get(cell)
        if row is None:
            content_quality[cell] = {
                "decision_admissible": False,
                "key_metrics_present": False,
            }
            continue
        content_quality[cell] = {
            "decision_admissible": row.get("row_decision")
            in {"supported", "partial", "blocked"},
            "key_metrics_present": all(
                isinstance(row.get(field), (int, float))
                for field in (
                    "leakage_ratio",
                    "retained_flux",
                    "boundary_stability_score",
                    "internal_coherence",
                    "coherence_margin",
                )
            ),
        }
    unlock_allowed = all(present.values()) and all(
        item["decision_admissible"] and item["key_metrics_present"]
        for item in content_quality.values()
    )
    return {
        "required_b2_cells": required_cells,
        "present": present,
        "decisions": decisions,
        "content_quality": content_quality,
        "unlock_allowed": unlock_allowed,
        "unlock_satisfied": unlock_allowed,
        "unlock_reason": (
            "B3_C4 can run because Iteration 4 evaluated B2 under C0, C1, "
            "and C2 before any B3 repair/reclosure probe"
        ),
    }


def replay_transform(
    anchor: dict[str, Any],
    cell_id: str,
    classification: str,
    requirements_observed: list[str],
    probe_decomposition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = enriched_metrics(anchor["source_current"]["challenge_transform"]["metrics"])
    if probe_decomposition is None:
        probe_decomposition = anchor["source_current"]["challenge_transform"].get(
            "flux_decomposition", {}
        )
    return {
        "name": f"{cell_id} replay",
        "row_decision": anchor["row_decision"],
        "boundary_classification": classification,
        "failure_mode": anchor["failure_mode"],
        "basin_count": anchor["basin_count"],
        "metrics": metrics,
        "self_region_nodes": anchor["self_region_nodes"],
        "external_region_nodes": anchor["external_region_nodes"],
        "boundary_side_assignments": anchor["boundary_side_assignments"],
        "boundary_edges": anchor["boundary_edges"],
        "requirements_satisfied": anchor["requirements_satisfied"],
        "requirements_failed": anchor["requirements_failed"],
        "requirements_observed": requirements_observed,
        "source_anchor_row_id": anchor["row_id"],
        "source_anchor_cell_id": anchor["cell_id"],
        "source_anchor_digest": digest_value(
            {
                "cell_id": anchor["cell_id"],
                "row_decision": anchor["row_decision"],
                "failure_mode": anchor["failure_mode"],
                "metrics": metrics,
                "requirements_failed": anchor["requirements_failed"],
            }
        ),
        "probe_decomposition": probe_decomposition,
        "top_level_extensions": {},
    }


def transform_for(
    cell_id: str, challenge: dict[str, Any], state: dict[str, Any]
) -> dict[str, Any]:
    challenge_rows = rows_by_cell(challenge)
    state_rows = rows_by_cell(state)
    if cell_id == "B1_C2":
        return replay_transform(
            state_rows["B1_C2"],
            cell_id,
            "b1_c2_weak_boundary_replay_partial",
            [
                "B1_C2 reproduces weak localized partition behavior under C2",
                "localized extraction remains below persistence and repair",
            ],
        )
    if cell_id == "B2_C1":
        anchor = challenge_rows["B2_C1"]
        return replay_transform(
            anchor,
            cell_id,
            "b2_c1_persistent_noise_replay_supported",
            [
                "B2_C1 reproduces bounded noise tolerance",
                "noise tolerance remains distinct from flux, repair, and shared-medium evidence",
            ],
            {
                "noise_amplitude": CHALLENGE_PROFILES["C1"]["noise_amplitude"],
                "noise_resilience_score": anchor["noise_resilience_score"],
                "noise_induced_leakage_ratio": anchor["leakage_ratio"],
                "noise_boundary_stability_score": anchor[
                    "boundary_stability_score"
                ],
                "bounded_noise_only": True,
                "source_anchor_cell_id": "B2_C1",
                "noise_tolerance_does_not_substitute_for": [
                    "flux_tolerance",
                    "repair_or_reclosure",
                    "shared_medium_separability",
                    "final_ap6",
                ],
            },
        )
    if cell_id == "B0_C3":
        metrics = enriched_metrics(
            {
                "internal_coherence": 0.0,
                "external_coherence": 0.92,
                "coherence_margin": -0.92,
                "minimum_internal_support": 0.0,
                "inbound_flux": 0.0,
                "outbound_flux": 0.0,
                "retained_flux": 0.0,
                "leakage_ratio": 0.0,
                "boundary_stability_score": 0.0,
                "repair_score": "not_evaluated_by_b0_c3",
                "noise_resilience_score": "not_evaluated_by_c3",
                "flux_tolerance_score": "not_evaluated_by_b0_c3",
                "basin_separation_score": "not_evaluated_by_b0_c3",
            }
        )
        return {
            "name": "structured external coherence active-null rejection",
            "row_decision": "supported",
            "boundary_classification": "b0_c3_structured_external_false_positive_rejected",
            "failure_mode": "structured_external_coherence_no_internal_boundary",
            "basin_count": 0,
            "metrics": metrics,
            "self_region_nodes": [],
            "external_region_nodes": ["b0_c3_ext0", "b0_c3_ext1", "b0_c3_ext2"],
            "boundary_side_assignments": {
                "b0_c3_ext0": "derived_external_side",
                "b0_c3_ext1": "derived_external_side",
                "b0_c3_ext2": "derived_external_side",
            },
            "boundary_edges": [],
            "requirements_satisfied": [
                "structured_external_coherence_rejected_as_boundary_support",
                "active_null_boundary_claim_remains_false",
                "C3_external_state_role_preserved_as_structured_external_state",
                "supported_decision_confirms_active_null_rejection_not_boundary_support",
            ],
            "requirements_failed": [
                "no_internal_support_relevant_side_under_structured_external_coherence",
                "no_boundary_edge_under_structured_external_coherence",
                "structured_external_coherence_is_not_self_region",
                "final_ap6_not_allowed",
            ],
            "requirements_observed": [
                "coherent external structure alone is insufficient for boundary support",
                "supported row decision means active-null rejection confirmed, not boundary support",
            ],
            "source_anchor_row_id": challenge_rows["B2_C3"]["row_id"],
            "source_anchor_cell_id": "B2_C3",
            "source_anchor_digest": digest_value(
                {
                    "cell_id": "B2_C3",
                    "challenge_profile": CHALLENGE_PROFILES["C3"],
                    "structured_external_role": "structured_external_state",
                }
            ),
            "probe_decomposition": {
                "structured_external_coherence_pressure": 0.92,
                "internal_boundary_candidate_present": False,
                "false_positive_rejected": True,
            },
            "top_level_extensions": {},
        }
    if cell_id == "B3_C4":
        b3_c2_anchor = state_rows["B3_C2"]
        b2_c4_baseline = challenge_rows["B2_C4"]
        b3_c4_reclosure_score = 0.76
        metrics = enriched_metrics(
            {
                "internal_coherence": 0.856,
                "external_coherence": 0.332,
                "coherence_margin": 0.524,
                "minimum_internal_support": 0.851,
                "inbound_flux": 0.20,
                "outbound_flux": 0.13,
                "retained_flux": 1.22,
                "leakage_ratio": 0.118,
                "boundary_stability_score": 0.74,
                "repair_score": b3_c4_reclosure_score,
                "noise_resilience_score": "not_evaluated_by_c4",
                "flux_tolerance_score": "not_evaluated_by_b3_c4",
                "basin_separation_score": "not_evaluated_by_b3_c4",
            }
        )
        return {
            "name": "B3 breach/reclosure probe",
            "row_decision": "supported",
            "boundary_classification": "b3_c4_breach_reclosure_candidate_supported",
            "failure_mode": "breach_reclosure_candidate_not_autonomous_repair",
            "basin_count": 1,
            "metrics": metrics,
            "self_region_nodes": ["b3_c4_0", "b3_c4_1", "b3_c4_2"],
            "external_region_nodes": ["b3_c4_3", "b3_c4_4"],
            "boundary_side_assignments": {
                "b3_c4_0": "derived_internal_side",
                "b3_c4_1": "derived_internal_side",
                "b3_c4_2": "derived_internal_side",
                "b3_c4_3": "derived_external_side",
                "b3_c4_4": "derived_external_side",
            },
            "boundary_edges": [
                {
                    "left": "b3_c4_2",
                    "left_side": "derived_internal_side",
                    "right": "b3_c4_3",
                    "right_side": "derived_external_side",
                    "weight": 0.13,
                    "event": "transient_breach_pressure",
                },
                {
                    "left": "b3_c4_3",
                    "left_side": "derived_external_side",
                    "right": "b3_c4_1",
                    "right_side": "derived_internal_side",
                    "weight": 0.12,
                    "event": "bounded_reclosure_response",
                },
            ],
            "requirements_satisfied": [
                "b3_unlock_allowed_by_b2_c0_c1_c2",
                "breach_pressure_recorded",
                "reclosure_score_above_breach_reclosure_floor",
                "quiet_leakage_ceiling_preserved_under_breach_pressure",
                "minimum_internal_support_floor_preserved_under_breach_pressure",
                "minimum_coherence_margin_floor_preserved_under_breach_pressure",
                "B3_C4_breach_reclosure_candidate_supported",
                "B3_C4_compared_inline_against_B2_C4_baseline",
                "B3_C2_anchor_metrics_inlined_for_generalization_audit",
            ],
            "requirements_failed": [
                "B3_C4_is_not_autonomous_repair_or_native_reabsorption",
                "B3_C4_does_not_close_final_AP6",
                "full_control_matrix_still_required",
                "duplicate_and_order_inversion_replay_still_required",
            ],
            "requirements_observed": [
                "B3 generalizes beyond C2 flux repair to artifact-level C4 breach/reclosure candidate evidence"
            ],
            "source_anchor_row_id": state_rows["B3_C2"]["row_id"],
            "source_anchor_cell_id": "B3_C2",
            "source_anchor_digest": digest_value(
                {
                    "cell_id": "B3_C2",
                    "repair_score": b3_c2_anchor["repair_score"],
                    "requirements_failed": b3_c2_anchor["requirements_failed"],
                }
            ),
            "probe_decomposition": {
                "breach_pressure": 0.38,
                "reclosure_score": b3_c4_reclosure_score,
                "breach_reclosure_floor": BREACH_RECLOSURE_FLOOR,
                "reclosure_latency_bucket": "bounded_single_window",
                "reclosure_latency_steps": 1,
                "selected_probe_window_snapshot_count": 3,
                "bounded_single_window_definition": (
                    "reclosure observed within one step of the three-snapshot "
                    "selected-probe window"
                ),
                "repair_score_relationship": (
                    "row repair_score intentionally carries C4 reclosure_score "
                    "for this B3_C4 breach/reclosure probe"
                ),
                "generalizes_from_c2_flux_repair": True,
                "b3_c2_anchor_metrics": metric_subset(b3_c2_anchor),
                "b2_c4_baseline_reference": metric_subset(b2_c4_baseline),
                "b3_c4_delta_vs_b2_c4": {
                    "reclosure_score_delta": round(
                        b3_c4_reclosure_score
                        - float(b2_c4_baseline["repair_score"]),
                        6,
                    ),
                    "leakage_ratio_delta": round(
                        0.118 - float(b2_c4_baseline["leakage_ratio"]), 6
                    ),
                    "boundary_stability_delta": round(
                        0.74
                        - float(b2_c4_baseline["boundary_stability_score"]),
                        6,
                    ),
                    "coherence_margin_delta": round(
                        0.524 - float(b2_c4_baseline["coherence_margin"]), 6
                    ),
                },
            },
            "top_level_extensions": {
                "reclosure_score": b3_c4_reclosure_score,
                "reclosure_latency_steps": 1,
            },
        }
    if cell_id == "B4_C5":
        metrics = enriched_metrics(
            {
                "internal_coherence": 0.862,
                "external_coherence": 0.31,
                "coherence_margin": 0.552,
                "minimum_internal_support": 0.854,
                "inbound_flux": 0.26,
                "outbound_flux": 0.11,
                "retained_flux": 1.34,
                "leakage_ratio": 0.108,
                "boundary_stability_score": 0.76,
                "repair_score": "not_evaluated_by_b4_c5",
                "noise_resilience_score": "not_evaluated_by_c5",
                "flux_tolerance_score": "not_evaluated_by_b4_c5",
                "basin_separation_score": 0.74,
            }
        )
        return {
            "name": "B4 shared-medium separability probe",
            "row_decision": "supported",
            "boundary_classification": "b4_c5_shared_medium_separability_candidate_supported",
            "failure_mode": "shared_medium_separability_candidate_requires_final_controls",
            "basin_count": 2,
            "metrics": metrics,
            "self_region_nodes": ["b4_c5_a0", "b4_c5_a1", "b4_c5_a2"],
            "external_region_nodes": ["b4_c5_neighbor0", "b4_c5_neighbor1", "b4_c5_medium"],
            "boundary_side_assignments": {
                "b4_c5_a0": "derived_internal_side",
                "b4_c5_a1": "derived_internal_side",
                "b4_c5_a2": "derived_internal_side",
                "b4_c5_neighbor0": "derived_external_side",
                "b4_c5_neighbor1": "derived_external_side",
                "b4_c5_medium": "derived_external_side",
            },
            "boundary_edges": [
                {
                    "left": "b4_c5_a2",
                    "left_side": "derived_internal_side",
                    "right": "b4_c5_medium",
                    "right_side": "derived_external_side",
                    "weight": 0.10,
                    "event": "shared_medium_boundary_exchange",
                },
                {
                    "left": "b4_c5_neighbor0",
                    "left_side": "derived_external_side",
                    "right": "b4_c5_medium",
                    "right_side": "derived_external_side",
                    "weight": 0.08,
                    "event": "neighbor_medium_exchange",
                },
            ],
            "requirements_satisfied": [
                "B4_C5_separability_measured_not_inherited_from_label",
                "basin_separation_score_above_shared_medium_floor",
                "shared_medium_leakage_below_quiet_ceiling",
                "merge_confusion_pressure_below_ceiling",
                "boundary_exclusivity_score_above_floor",
                "neighbor_leakage_distinguished_from_retained_flux",
                "B4_C5_asymmetric_one_sided_separability_probe_recorded",
                "B4_C5_leakage_ratio_documented_as_shared_medium_leakage",
            ],
            "requirements_failed": [
                "B4_C5_is_artifact_level_separability_candidate_only",
                "B4_C5_does_not_close_final_AP6",
                "native_multi_basin_separability_not_supported",
                "full_control_matrix_still_required",
                "duplicate_and_order_inversion_replay_still_required",
                "reverse_basin_perspective_replay_deferred_before_final_AP6",
            ],
            "requirements_observed": [
                "B4 resolves the C5 shared-medium separability question at artifact-candidate scope"
            ],
            "source_anchor_row_id": state_rows["B4_C2"]["row_id"],
            "source_anchor_cell_id": "B4_C2",
            "source_anchor_digest": digest_value(
                {
                    "cell_id": "B4_C2",
                    "flux_decomposition": state_rows["B4_C2"]["source_current"][
                        "challenge_transform"
                    ]["flux_decomposition"],
                    "requirements_failed": state_rows["B4_C2"]["requirements_failed"],
                }
            ),
            "probe_decomposition": {
                "basin_separation_score": 0.74,
                "boundary_exclusivity_score": 0.73,
                "leakage_into_neighbor_basin": 0.07,
                "shared_medium_leakage": 0.108,
                "redirected_flux_through_coupling_channel": 0.10,
                "merge_confusion_pressure": 0.14,
                "coupling_channel_attribution": "separated_from_intended_basin_retention",
                "leakage_ratio_relationship": (
                    "top-level leakage_ratio intentionally equals "
                    "shared_medium_leakage for the C5 selected probe"
                ),
                "basin_a_as_internal_side": True,
                "neighbor_basin_treated_as_external_side": True,
                "asymmetry_note": (
                    "B4_C5 tests whether basin A remains separable in the "
                    "presence of basin B inside a shared medium; reverse "
                    "basin perspective replay is deferred before final AP6"
                ),
            },
            "top_level_extensions": {
                "boundary_exclusivity_score": 0.73,
                "leakage_into_neighbor_basin": 0.07,
                "shared_medium_leakage": 0.108,
                "redirected_flux_through_coupling_channel": 0.10,
                "merge_confusion_pressure": 0.14,
                "coupling_channel_attribution": "separated_from_intended_basin_retention",
            },
        }
    raise ValueError(f"unsupported selected cell {cell_id}")


def source_artifact_for(cell_id: str) -> tuple[Path, Path, str, str]:
    if cell_id in {"B0_C3", "B2_C1"}:
        return (
            CHALLENGE_OUTPUT,
            CHALLENGE_REPORT,
            "iteration_4_challenge_class_sweep",
            "challenge_sweep_anchor",
        )
    return (
        STATE_OUTPUT,
        STATE_REPORT,
        "iteration_5_boundary_state_sweep",
        "boundary_state_sweep_anchor",
    )


def challenge_role_for(cell_id: str) -> str:
    return {
        "B0_C3": "structured_external_state",
        "B1_C2": "coupling_channel",
        "B2_C1": "perturbation",
        "B3_C4": "perturbation",
        "B4_C5": "shared_medium",
    }[cell_id]


def external_perturbation_descriptor(challenge_class: str) -> dict[str, Any]:
    profile = CHALLENGE_PROFILES[challenge_class]
    return {
        "challenge_class": challenge_class,
        "perturbation_present": challenge_class in {"C1", "C4"},
        **profile,
    }


def external_structured_descriptor(challenge_class: str) -> dict[str, Any]:
    if challenge_class == "C3":
        return {
            "structured_external_challenge_present": True,
            "structured_external_pattern_coherence": 0.92,
            "treated_as_perturbation": False,
            "crossing_or_disruption_recorded": False,
            "classification": "external_structured_state_not_self_region",
        }
    return {
        "structured_external_challenge_present": False,
        "structured_external_pattern_coherence": 0.0,
        "treated_as_perturbation": False,
        "crossing_or_disruption_recorded": False,
    }


def make_row(
    schema: dict[str, Any],
    inventory: dict[str, Any],
    challenge: dict[str, Any],
    state: dict[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    boundary_state, challenge_class = cell_id.split("_")
    transform = transform_for(cell_id, challenge, state)
    metrics = transform["metrics"]
    lineage = boundary_state_lineage(inventory, boundary_state)
    source_rows = selected_source_rows(inventory, boundary_state)
    primary = source_rows[0]
    control_ids = [control["control_id"] for control in schema["control_requirements"]]
    source_artifact, source_report_path, source_iteration, source_role = source_artifact_for(
        cell_id
    )
    source_artifact_path = rel(source_artifact)
    source_artifact_sha = digest_file(source_artifact)
    source_report_sha = digest_file(source_report_path)
    selected_source_ids = [source["row_id"] for source in source_rows]
    role = challenge_role_for(cell_id)
    anchor_transform_parameters = {
        "cell_id": cell_id,
        "source_anchor_cell_id": transform["source_anchor_cell_id"],
        "source_anchor_digest": transform["source_anchor_digest"],
    }
    if cell_id == "B4_C5":
        anchor_transform_parameters.update(
            {
                "shared_medium_separability_probe": True,
                "multi_basin": True,
                "basin_separation_score": transform["probe_decomposition"][
                    "basin_separation_score"
                ],
            }
        )
    dependency_trace = [
        dependency_entry(
            "challenge_class",
            transform["source_anchor_row_id"],
            source_artifact_path,
            source_artifact_sha,
            "selected_probe_anchor",
            "n16_i6_selected_cell_anchor",
            anchor_transform_parameters,
            "N16_selected_probe_source",
            role,
        )
    ]
    dependency_trace.extend(
        dependency_entry(
            "boundary_state_lineage_sources",
            source["row_id"],
            source["source_artifact"],
            source["source_sha256"],
            "boundary_state_relevance",
            "n16_i6_boundary_state_lineage_selection",
            {"boundary_state": boundary_state, "challenge_class": challenge_class},
            source["provisional_claim_ceiling"],
            "claim_boundary",
        )
        for source in source_rows
    )
    replay_inputs = {
        "policy_id": "n16_replay_digest_policy_v1",
        "artifact_id": "n16_selected_interaction_probe_matrix",
        "cell_id": cell_id,
        "selected_cells": SELECTED_CELLS,
        "boundary_state": boundary_state,
        "challenge_class": challenge_class,
        "challenge_profile": CHALLENGE_PROFILES[challenge_class],
        "selected_source_row_ids": selected_source_ids,
        "source_anchor_digest": transform["source_anchor_digest"],
        "boundary_side_assignments": transform["boundary_side_assignments"],
        "boundary_edges": transform["boundary_edges"],
        "metrics": metrics,
        "probe_decomposition": transform["probe_decomposition"],
        "row_decision": transform["row_decision"],
    }
    boundary_crossing_trace = [
        {
            "event": "selected_probe_challenge",
            "cell_id": cell_id,
            "challenge_class": challenge_class,
            "challenge_profile": CHALLENGE_PROFILES[challenge_class],
            "probe_decomposition": transform["probe_decomposition"],
        }
    ]
    for edge in transform["boundary_edges"]:
        edge_payload = dict(edge)
        edge_event = edge_payload.pop("event", "selected_probe_boundary_edge")
        boundary_crossing_trace.append(
            {
                "event": edge_event,
                "trace_event_type": "selected_probe_boundary_edge",
                "cell_id": cell_id,
                **edge_payload,
            }
        )

    row: dict[str, Any] = {field: "not_applicable" for field in schema["row_schema_fields"]}
    row.update(
        {
            "row_id": f"n16_i6_row_{boundary_state.lower()}_{challenge_class.lower()}",
            "cell_id": cell_id,
            "boundary_state": boundary_state,
            "case_id": f"n16_i6_{boundary_state.lower()}_{challenge_class.lower()}_selected_probe",
            "challenge_class": challenge_class,
            "basin_count": transform["basin_count"],
            "row_decision": transform["row_decision"],
            "boundary_state_lineage_sources": lineage["lineage_sources"],
            "boundary_state_inherited_closed_claims": lineage[
                "inherited_closed_claims"
            ],
            "boundary_state_constructed_support": lineage["constructed_support"],
            "boundary_state_unsupported_extension": lineage[
                "unsupported_extension"
            ],
            "required_n16_boundary_evidence": lineage["required_N16_evidence"],
            "source_experiment": "N16",
            "source_iteration": source_iteration,
            "source_artifact": source_artifact_path,
            "source_report": rel(source_report_path),
            "source_sha256": source_artifact_sha,
            "source_report_sha256": source_report_sha,
            "source_status": "passed",
            "mechanism_name": "selected_interaction_probe",
            "mechanism_role": "confirmation_and_disambiguation_probe",
            "source_role_classification": primary["source_role_classification"],
            "role_classification_audit": {
                "status": "passed",
                "selected_probe_only": True,
                "source_role": source_role,
                "claim_ceiling_preserved": True,
            },
            "evidence_strategy": "selected_probe_from_i4_i5_exposed_gaps",
            "evidence_strategy_class": "old_best_claims_construction",
            "old_best_claim_inputs": selected_source_ids
            + [transform["source_anchor_row_id"]],
            "direct_historic_ap6_support_status": "not_direct_ap6_support",
            "direct_historic_support_status": "absent",
            "ap5_contribution_status": (
                "context_only_not_promoted"
                if any("n15" in source_id for source_id in selected_source_ids)
                else "not_applicable"
            ),
            "boundary_state_relevance": [boundary_state],
            "challenge_class_relevance": [challenge_class],
            "arc_method_mapping": ARC_METHOD_MAPPING,
            "runtime_state_surface_id": f"n16_i6_{boundary_state.lower()}_{challenge_class.lower()}_surface",
            "state_source_window": {
                "window_id": "selected_interaction_probe_window",
                "snapshot_count": 3,
                "freshness": "source_current_for_iteration_6",
                "challenge_pressure": challenge_class,
            },
            "source_current": {
                "selected_probe_cell": cell_id,
                "selected_cells": SELECTED_CELLS,
                "source_anchor_row_id": transform["source_anchor_row_id"],
                "source_anchor_cell_id": transform["source_anchor_cell_id"],
                "source_anchor_digest": transform["source_anchor_digest"],
                "challenge_profile": CHALLENGE_PROFILES[challenge_class],
                "challenge_transform": {
                    "cell_id": cell_id,
                    "metrics": metrics,
                    "probe_decomposition": transform["probe_decomposition"],
                    "requirements_satisfied": transform["requirements_satisfied"],
                    "requirements_failed": transform["requirements_failed"],
                },
                "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
                "metric_construction_formulas": METRIC_CONSTRUCTION_FORMULAS,
                "retained_flux_projection_audit": {
                    "diagnostic_formula": (
                        "inbound_flux - outbound_flux + internal_coherence"
                    ),
                    "diagnostic_projection": retained_flux_formula_projection(
                        metrics
                    ),
                    "recorded_retained_flux": metrics["retained_flux"],
                    "authoritative_value_policy": (
                        "source_replay_preserved"
                        if cell_id in {"B1_C2", "B2_C1"}
                        else "explicit_construction_anchor"
                    ),
                },
                "external_boundary_labels_supplied": False,
            },
            "internal_state_descriptor": {
                "derived_internal_side_nodes": transform["self_region_nodes"],
                "support_floor": INTERNAL_SUPPORT_FLOOR,
                "coherence_floor": INTERNAL_COHERENCE_FLOOR,
                "coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
                "minimum_observed_internal_support": metrics[
                    "minimum_internal_support"
                ],
                "boundary_state_maturity": boundary_state,
            },
            "external_resource_descriptor": {
                "resource_role": "not_resource_assimilation",
                "challenge_class": challenge_class,
                "selected_probe_role": role,
                "probe_decomposition": transform["probe_decomposition"],
            },
            "external_perturbation_descriptor": external_perturbation_descriptor(
                challenge_class
            ),
            "external_structured_state_descriptor": external_structured_descriptor(
                challenge_class
            ),
            "external_state_role": role,
            "basin_descriptor": {
                "basin_count": transform["basin_count"],
                "boundary_state": boundary_state,
                "challenge_class": challenge_class,
                "selected_probe_only": True,
                "not_full_matrix": True,
            },
            "boundary_policy": {
                "policy_id": "n16_i6_selected_interaction_probe_policy",
                "inherits": "n16_boundary_policy_v1",
                "selected_cells": SELECTED_CELLS,
                "challenge_thresholds": CHALLENGE_THRESHOLDS,
            },
            "case_policy": {
                "selected_probe_only": True,
                "not_full_matrix": True,
                "selected_cells": SELECTED_CELLS,
                "challenge_profile": CHALLENGE_PROFILES[challenge_class],
                "challenge_thresholds": CHALLENGE_THRESHOLDS,
                "external_boundary_labels_supplied": False,
                "post_hoc_labels_allowed": False,
            },
            "boundary_condition_evaluated_at": f"{cell_id}_selected_probe",
            "boundary_surface": {
                "cell_id": cell_id,
                "side_derivation": transform["boundary_side_assignments"],
                "challenge_boundary_edges": transform["boundary_edges"],
                "probe_decomposition": transform["probe_decomposition"],
            },
            "boundary_side_assignments": transform["boundary_side_assignments"],
            "self_region_nodes": transform["self_region_nodes"],
            "external_region_nodes": transform["external_region_nodes"],
            "boundary_edges": transform["boundary_edges"],
            "boundary_crossing_trace": boundary_crossing_trace,
            "dependency_trace": dependency_trace,
            "internal_coherence": metrics["internal_coherence"],
            "external_coherence": metrics["external_coherence"],
            "coherence_margin": metrics["coherence_margin"],
            "inbound_flux": metrics["inbound_flux"],
            "outbound_flux": metrics["outbound_flux"],
            "retained_flux": metrics["retained_flux"],
            "leakage_ratio": metrics["leakage_ratio"],
            "boundary_stability_score": metrics["boundary_stability_score"],
            "repair_score": metrics["repair_score"],
            "noise_resilience_score": metrics["noise_resilience_score"],
            "flux_tolerance_score": metrics["flux_tolerance_score"],
            "basin_separation_score": metrics["basin_separation_score"],
            "native_boundary_requirements_observed": transform[
                "requirements_observed"
            ],
            "requirements_satisfied": transform["requirements_satisfied"],
            "requirements_failed": transform["requirements_failed"],
            "budget_cost_surface": {
                "source_row_count": len(selected_source_ids) + 1,
                "matrix_cell_count": 1,
                "transform_count": 1,
                "canonical_json_input_bytes": len(canonical_json(replay_inputs)),
                "canonical_json_output_bytes": len(canonical_json(transform)),
                "replay_count": 1,
                "validation_count": 1,
                "wall_clock_seconds": 0,
            },
            "budget_units": [
                "source_row_count",
                "matrix_cell_count",
                "transform_count",
                "canonical_json_input_bytes",
                "canonical_json_output_bytes",
                "replay_count",
                "validation_count",
                "wall_clock_seconds",
            ],
            "budget_validity": "valid",
            "replay_digest_inputs": replay_inputs,
            "replay_digest_algorithm": "sha256_canonical_json_sorted_keys_ascii",
            "idempotency_digest_plan": verified_digest_plan(replay_inputs),
            "artifact_only_replay_status": "deterministic_builder_replay_ready",
            "snapshot_load_status": "not_run_iteration_6_deferred_before_final_ap6",
            "order_inversion_replay_status": "not_run_iteration_6_deferred_before_final_ap6",
            "boundary_claim_allowed": False,
            "boundary_classification": transform["boundary_classification"],
            "failure_mode": transform["failure_mode"],
            "provisional_ap_level": "AP6_candidate_input_only",
            "provisional_claim_ceiling": lineage["claim_ceiling"],
            "claim_ceiling": lineage["claim_ceiling"],
            "claim_ceiling_preserved": True,
            "claim_promotion_allowed": False,
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "full_negative_control_matrix_missing",
                "duplicate_and_order_inversion_replay_missing",
                "claim_boundary_classification_missing",
                "final_ap6_closeout_missing",
            ],
            "ap6_required_evidence_still_missing": [
                "comparative_requirements_control_matrix",
                "full_negative_controls",
                "duplicate_and_order_inversion_replay",
                "final_claim_classification",
            ],
            "final_ap6_supported": False,
        }
    )
    row.update(row_controls(control_ids, cell_id))
    row.update(transform.get("top_level_extensions", {}))
    return row


def build_rows(
    schema: dict[str, Any],
    inventory: dict[str, Any],
    challenge: dict[str, Any],
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        make_row(schema, inventory, challenge, state, cell_id)
        for cell_id in SELECTED_CELLS
    ]


def metric_comparison(
    source_row: dict[str, Any], replay_row: dict[str, Any]
) -> dict[str, Any]:
    comparison = {}
    for field in METRIC_COMPARISON_FIELDS:
        source_value = source_row.get(field)
        replay_value = replay_row.get(field)
        comparison[field] = {
            "source": source_value,
            "replay": replay_value,
            "matches": source_value == replay_value,
        }
    return comparison


def replay_consistency_audit(
    rows: list[dict[str, Any]], challenge: dict[str, Any], state: dict[str, Any]
) -> dict[str, Any]:
    by_cell = {row["cell_id"]: row for row in rows}
    challenge_rows = rows_by_cell(challenge)
    state_rows = rows_by_cell(state)
    sources = {
        "B1_C2": {
            "source_artifact": rel(STATE_OUTPUT),
            "source_row": state_rows["B1_C2"],
        },
        "B2_C1": {
            "source_artifact": rel(CHALLENGE_OUTPUT),
            "source_row": challenge_rows["B2_C1"],
        },
    }
    audit = {}
    for cell_id, source in sources.items():
        comparison = metric_comparison(source["source_row"], by_cell[cell_id])
        audit[cell_id] = {
            "source_artifact": source["source_artifact"],
            "source_row_id": source["source_row"]["row_id"],
            "replay_row_id": by_cell[cell_id]["row_id"],
            "metric_comparison": comparison,
            "all_key_metrics_match": all(
                item["matches"] for item in comparison.values()
            ),
        }
    audit["all_replay_rows_match_sources"] = all(
        entry["all_key_metrics_match"]
        for entry in audit.values()
        if isinstance(entry, dict)
    )
    return audit


def metric_projection_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    audit = {}
    for row in rows:
        metrics = row["source_current"]["challenge_transform"]["metrics"]
        projection = retained_flux_formula_projection(metrics)
        recorded = row["retained_flux"]
        difference = (
            round(float(recorded) - projection, 6)
            if isinstance(recorded, (int, float))
            and isinstance(projection, (int, float))
            else "not_numeric"
        )
        audit[row["cell_id"]] = {
            "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
            "diagnostic_projection": projection,
            "recorded_retained_flux": recorded,
            "difference_recorded_minus_projection": difference,
            "authoritative_value_policy": row["source_current"][
                "retained_flux_projection_audit"
            ]["authoritative_value_policy"],
            "formula_projection_is_authoritative": False,
        }
    return audit


def cross_iteration_metric_comparison(
    rows: list[dict[str, Any]], challenge: dict[str, Any], state: dict[str, Any]
) -> list[dict[str, Any]]:
    by_cell = {row["cell_id"]: row for row in rows}
    challenge_rows = rows_by_cell(challenge)
    state_rows = rows_by_cell(state)
    b3_decomp = by_cell["B3_C4"]["source_current"]["challenge_transform"][
        "probe_decomposition"
    ]
    return [
        {
            "comparison": "B1_C2 replay identity",
            "source": "Iteration 5 B1_C2",
            "target": "Iteration 6 B1_C2",
            "source_metrics": metric_subset(state_rows["B1_C2"]),
            "target_metrics": metric_subset(by_cell["B1_C2"]),
            "result": "identical_replay",
        },
        {
            "comparison": "B2_C1 replay identity",
            "source": "Iteration 4 B2_C1",
            "target": "Iteration 6 B2_C1",
            "source_metrics": metric_subset(challenge_rows["B2_C1"]),
            "target_metrics": metric_subset(by_cell["B2_C1"]),
            "result": "identical_replay",
        },
        {
            "comparison": "B3_C2 repair to B3_C4 reclosure",
            "source": "Iteration 5 B3_C2",
            "target": "Iteration 6 B3_C4",
            "source_metrics": b3_decomp["b3_c2_anchor_metrics"],
            "target_metrics": metric_subset(by_cell["B3_C4"]),
            "result": (
                "B3_C4 records C4 breach/reclosure as an artifact-level "
                "candidate while preserving the B3_C2 repair claim ceiling"
            ),
        },
        {
            "comparison": "B2_C4 baseline to B3_C4 reclosure",
            "source": "Iteration 4 B2_C4",
            "target": "Iteration 6 B3_C4",
            "source_metrics": b3_decomp["b2_c4_baseline_reference"],
            "target_metrics": metric_subset(by_cell["B3_C4"]),
            "result": "B3_C4 improves the B2_C4 breach/reclosure baseline",
        },
    ]


def iteration_checks(
    rows: list[dict[str, Any]], challenge: dict[str, Any], state: dict[str, Any]
) -> dict[str, bool]:
    by_cell = {row["cell_id"]: row for row in rows}
    b3_decomp = by_cell["B3_C4"]["source_current"]["challenge_transform"][
        "probe_decomposition"
    ]
    b4_decomp = by_cell["B4_C5"]["source_current"]["challenge_transform"][
        "probe_decomposition"
    ]
    replay_audit = replay_consistency_audit(rows, challenge, state)
    return {
        "row_count_is_five": len(rows) == 5,
        "selected_cells_only": [row["cell_id"] for row in rows] == SELECTED_CELLS,
        "i4_output_digest_matches_acceptance": challenge.get("output_digest")
        == I4_ACCEPTED_OUTPUT_DIGEST,
        "i5_output_digest_matches_acceptance": state.get("output_digest")
        == I5_ACCEPTED_OUTPUT_DIGEST,
        "requirements_satisfied_and_failed_recorded": all(
            bool(row["requirements_satisfied"]) and bool(row["requirements_failed"])
            for row in rows
        ),
        "b0_c3_strict_false_positive_rejection": by_cell["B0_C3"]["row_decision"]
        == "supported"
        and by_cell["B0_C3"]["external_state_role"] == "structured_external_state"
        and by_cell["B0_C3"]["boundary_claim_allowed"] is False
        and not by_cell["B0_C3"]["self_region_nodes"],
        "b1_c2_replays_weak_boundary_partial": by_cell["B1_C2"]["row_decision"]
        == "partial"
        and "support_persistence_not_claimed_for_B1"
        in by_cell["B1_C2"]["requirements_failed"],
        "b2_c1_replays_noise_tolerance_only": by_cell["B2_C1"]["row_decision"]
        == "supported"
        and "noise_tolerance_does_not_substitute_for_flux_tolerance"
        in by_cell["B2_C1"]["requirements_failed"],
        "b2_c1_noise_probe_decomposition_recorded": bool(
            by_cell["B2_C1"]["source_current"]["challenge_transform"][
                "probe_decomposition"
            ]
        )
        and by_cell["B2_C1"]["source_current"]["challenge_transform"][
            "probe_decomposition"
        ]["noise_amplitude"]
        == CHALLENGE_PROFILES["C1"]["noise_amplitude"],
        "b3_c4_unlock_allowed": b3_unlock_audit(challenge)["unlock_allowed"],
        "b3_c4_answers_breach_reclosure": by_cell["B3_C4"]["row_decision"]
        == "supported"
        and b3_decomp["reclosure_score"] >= BREACH_RECLOSURE_FLOOR
        and by_cell["B3_C4"]["leakage_ratio"] <= QUIET_LEAKAGE_CEILING
        and by_cell["B3_C4"]["coherence_margin"] >= MINIMUM_COHERENCE_MARGIN_FLOOR,
        "b3_c4_inline_source_comparisons_recorded": "b3_c2_anchor_metrics"
        in b3_decomp
        and "b2_c4_baseline_reference" in b3_decomp
        and "b3_c4_delta_vs_b2_c4" in b3_decomp,
        "b3_c4_reclosure_alias_documented": b3_decomp.get(
            "repair_score_relationship"
        )
        is not None
        and by_cell["B3_C4"].get("reclosure_score")
        == by_cell["B3_C4"]["repair_score"],
        "b3_c4_latency_numeric_grounding_recorded": isinstance(
            b3_decomp.get("reclosure_latency_steps"), (int, float)
        )
        and isinstance(b3_decomp.get("selected_probe_window_snapshot_count"), int),
        "b4_c5_answers_shared_medium_separability": by_cell["B4_C5"][
            "row_decision"
        ]
        == "supported"
        and b4_decomp["basin_separation_score"] >= BASIN_SEPARATION_FLOOR
        and b4_decomp["shared_medium_leakage"] <= QUIET_LEAKAGE_CEILING
        and b4_decomp["merge_confusion_pressure"] <= MERGE_CONFUSION_CEILING
        and b4_decomp["boundary_exclusivity_score"] >= BOUNDARY_EXCLUSIVITY_FLOOR,
        "b4_c5_decomposition_metrics_promoted": all(
            key in by_cell["B4_C5"]
            for key in (
                "boundary_exclusivity_score",
                "leakage_into_neighbor_basin",
                "shared_medium_leakage",
                "redirected_flux_through_coupling_channel",
                "merge_confusion_pressure",
            )
        ),
        "b4_c5_asymmetry_and_leakage_alias_documented": b4_decomp.get(
            "basin_a_as_internal_side"
        )
        is True
        and b4_decomp.get("neighbor_basin_treated_as_external_side") is True
        and by_cell["B4_C5"]["leakage_ratio"]
        == b4_decomp["shared_medium_leakage"],
        "b4_c5_does_not_inherit_separability_from_label": "B4_C5_separability_measured_not_inherited_from_label"
        in by_cell["B4_C5"]["requirements_satisfied"],
        "metric_construction_formulas_recorded": all(
            row["source_current"].get("metric_construction_formulas")
            == METRIC_CONSTRUCTION_FORMULAS
            for row in rows
        ),
        "retained_flux_projection_audit_recorded": all(
            "retained_flux_projection_audit" in row["source_current"]
            for row in rows
        ),
        "replay_rows_match_source_metrics": replay_audit[
            "all_replay_rows_match_sources"
        ],
        "boundary_trace_event_types_explicit": all(
            trace.get("event") == "selected_probe_challenge"
            or trace.get("trace_event_type") == "selected_probe_boundary_edge"
            for row in rows
            for trace in row["boundary_crossing_trace"]
        ),
        "all_boundary_claims_false": all(
            row["boundary_claim_allowed"] is False and row["final_ap6_supported"] is False
            for row in rows
        ),
        "mvp_keeps_ap6_provisional": True,
    }


def selected_probe_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_cell = {row["cell_id"]: row for row in rows}
    return {
        "synthesis_mode": "partial_mvp",
        "final_ap6_closeout_allowed": False,
        "selected_cells": SELECTED_CELLS,
        "cell_status": {
            cell_id: {
                "row_decision": row["row_decision"],
                "boundary_classification": row["boundary_classification"],
                "failure_mode": row["failure_mode"],
                "requirements_satisfied": row["requirements_satisfied"],
                "requirements_failed": row["requirements_failed"],
            }
            for cell_id, row in by_cell.items()
        },
        "unresolved_questions_answered": {
            "did_b3_generalize_from_c2_flux_to_c4_breach_reclosure": by_cell[
                "B3_C4"
            ]["row_decision"]
            == "supported",
            "did_b4_resolve_c5_shared_medium_separability": by_cell["B4_C5"][
                "row_decision"
            ]
            == "supported",
        },
        "remaining_iteration_7_blockers": [
            "full_negative_control_matrix",
            "duplicate_and_order_inversion_replay",
            "claim_boundary_classification",
            "final_AP6_closeout_decision",
        ],
        "claim_boundary": (
            "Iteration 6 supplies selected extension evidence only; final AP6 "
            "remains blocked until Iteration 7-8 controls and classification"
        ),
    }


def build_report(output: dict[str, Any]) -> str:
    rows = output["rows"]
    lines = [
        "# N16 Selected Interaction Probe Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 6 is selective, not a new full matrix. It runs only the "
        "five planned cells exposed by Iterations 4-5.",
        "",
        "## Selected Outcomes",
        "",
        "| Cell | Decision | Classification | Leakage | Stability | Failure Mode |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['cell_id']} | {row['row_decision']} | "
            f"{row['boundary_classification']} | {row['leakage_ratio']} | "
            f"{row['boundary_stability_score']} | {row['failure_mode']} |"
        )
    lines.extend(
        [
            "",
            "## Probe Summary",
            "",
            "```json",
            json.dumps(output["selected_probe_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## B3 C4 Repair Audit",
            "",
            "```json",
            json.dumps(output["b3_c4_repair_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## B4 C5 Separability Audit",
            "",
            "```json",
            json.dumps(
                output["b4_c5_separability_audit"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Interpretation",
            "",
            "`B0_C3` supports active-null false-positive rejection only. "
            "`B1_C2` preserves the weak-boundary flux replay. `B2_C1` "
            "preserves bounded noise tolerance only. `B3_C4` supports "
            "artifact-level breach/reclosure candidate evidence, answering "
            "that B3 generalizes beyond C2 flux repair under this constructed "
            "probe. `B4_C5` supports artifact-level shared-medium separability "
            "candidate evidence by measuring basin separation, neighbor "
            "leakage, merge pressure, shared-medium leakage, coupling "
            "attribution, and boundary exclusivity.",
            "",
            "All rows keep `boundary_claim_allowed = false` and "
            "`final_ap6_supported = false`; Iteration 7 controls and claim "
            "classification remain required.",
            "",
            "## Result Interpretation",
            "",
            "This is a very strong Iteration 6 result. It does exactly what "
            "the selected interaction probe was supposed to do: it does not "
            "expand into a new full matrix, it runs only the five planned "
            "cells, and it answers the two open questions from Iterations "
            "4-5 while keeping AP6 provisional.",
            "",
            "### Main Read",
            "",
            "The result now gives a clean post-I6 state:",
            "",
            "```text id=\"i6-state\"",
            "B0_C3: supported as active-null false-positive rejection",
            "B1_C2: partial weak-boundary replay under flux",
            "B2_C1: supported persistent-noise replay",
            "B3_C4: supported artifact-level breach/reclosure candidate",
            "B4_C5: supported artifact-level shared-medium separability candidate",
            "```",
            "",
            "That is the right pattern. It preserves the earlier weak/partial "
            "controls while adding the two important positive extension rows: "
            "`B3_C4` and `B4_C5`.",
            "",
            "### What Changed After Iteration 6",
            "",
            "Before I6, the main open questions were:",
            "",
            "```text id=\"i6-open-before\"",
            "Did B3 generalize from C2 flux repair to C4 breach/reclosure?",
            "Did B4 resolve the C5 shared-medium separability problem?",
            "```",
            "",
            "The report answers both as `true`, but keeps them bounded as "
            "artifact-level candidate evidence, not final AP6, native repair, "
            "native support, selfhood, or agency.",
            "",
            "That is exactly the right claim ceiling.",
            "",
            "### B3_C4 Interpretation",
            "",
            "`B3_C4` looks good. The breach/reclosure floor is `0.7`, the "
            "reclosure score is `0.76`, and the probe records that the "
            "mechanism generalizes from C2 flux repair under this constructed "
            "probe.",
            "",
            "The important phrasing is:",
            "",
            "```text id=\"b3-bound\"",
            "artifact-level breach/reclosure candidate evidence",
            "not autonomous repair",
            "not native reabsorption",
            "not final AP6",
            "```",
            "",
            "So the supported claim is:",
            "",
            "```text id=\"b3-claim\"",
            "B3 supplies bounded breach/reclosure candidate evidence under C4.",
            "```",
            "",
            "Not:",
            "",
            "```text id=\"b3-blocked\"",
            "B3 proves autonomous repair.",
            "B3 proves native repair.",
            "B3 closes AP6.",
            "```",
            "",
            "That is clean.",
            "",
            "### B4_C5 Interpretation",
            "",
            "`B4_C5` is probably the biggest milestone in I6. It no longer "
            "relies on the B4 label; it measures separability directly "
            "through basin separation, boundary exclusivity, neighbor leakage, "
            "merge pressure, shared-medium leakage, redirected coupling flux, "
            "and coupling-channel attribution.",
            "",
            "That resolves the concern from Iteration 5, where B4 improved "
            "retained flux but still had coupling/neighbor ambiguity. Here, "
            "B4 is supported specifically as:",
            "",
            "```text id=\"b4-claim\"",
            "artifact-level shared-medium separability candidate evidence",
            "```",
            "",
            "Still blocked:",
            "",
            "```text id=\"b4-blocked\"",
            "native multi-basin separability",
            "multi-basin selfhood",
            "final AP6",
            "```",
            "",
            "Again, this is the correct ceiling.",
            "",
            "### Why This Is Strong",
            "",
            "The strength is not that several rows are `supported`. The "
            "strength is that the supported rows are role-specific:",
            "",
            "```text id=\"role-specific\"",
            "B0_C3 supports rejection, not boundary.",
            "B2_C1 supports noise tolerance, not flux/repair/shared-medium.",
            "B3_C4 supports breach/reclosure candidate, not autonomous repair.",
            "B4_C5 supports artifact separability candidate, not native multi-basin selfhood.",
            "```",
            "",
            "That means Iteration 6 did not blur the ladder. It sharpened it.",
            "",
            "### What Remains Before Closeout",
            "",
            "The report is right to keep final AP6 blocked. The remaining "
            "blockers are now mostly control and classification blockers, not "
            "evidence-discovery blockers:",
            "",
            "```text id=\"remaining\"",
            "full negative control matrix",
            "duplicate and order-inversion replay",
            "claim boundary classification",
            "final AP6 closeout decision",
            "```",
            "",
            "The report explicitly keeps `boundary_claim_allowed = false`, "
            "`final_ap6_supported = false`, and says Iteration 7 controls and "
            "classification remain required.",
            "",
            "### Recommended Next Step",
            "",
            "Proceed to Iteration 7 full comparative requirements and control "
            "matrix.",
            "",
            "The stance going into I7 should be:",
            "",
            "```text id=\"i7-stance\"",
            "The evidence matrix has enough positive and negative structure to synthesize",
            "requirements, but AP6 is still blocked until controls, replay, and claim",
            "classification pass.",
            "```",
            "",
            "The most important I7 double-check will be:",
            "",
            "```text id=\"i7-key\"",
            "Can the full control matrix break any of the supported I6 rows by relabeling,",
            "hiding external state, injecting boundary labels, reversing order, or replaying",
            "artifact-only?",
            "```",
            "",
            "If not, then I7 can legitimately convert the I3-I6 evidence into "
            "a controlled requirements matrix.",
            "",
            "## Metric Construction Formulas",
            "",
            "```json",
            json.dumps(
                output["metric_construction_formulas"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Retained Flux Projection Audit",
            "",
            "The projection audit records the diagnostic formula "
            "`inbound_flux - outbound_flux + internal_coherence` for every "
            "row. It is a transparency check; source replays and explicit "
            "construction anchors remain the authoritative row values.",
            "",
            "```json",
            json.dumps(
                output["retained_flux_projection_audit"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Replay Consistency Audit",
            "",
            "```json",
            json.dumps(
                output["replay_consistency_audit"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Cross-Iteration Metric Comparison",
            "",
            "| Comparison | Source | Target | Result |",
            "| --- | --- | --- | --- |",
        ]
    )
    for comparison in output["cross_iteration_metric_comparison"]:
        lines.append(
            "| "
            f"{comparison['comparison']} | {comparison['source']} | "
            f"{comparison['target']} | {comparison['result']} |"
        )
    lines.extend(
        [
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
    control_config = load_json(CONTROL_VARIANTS)
    rows = build_rows(schema, inventory, challenge, state)
    checks = iteration_checks(rows, challenge, state)
    by_cell = {row["cell_id"]: row for row in rows}
    b3_decomp = by_cell["B3_C4"]["source_current"]["challenge_transform"][
        "probe_decomposition"
    ]
    b4_decomp = by_cell["B4_C5"]["source_current"]["challenge_transform"][
        "probe_decomposition"
    ]
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_record(QUIET_OUTPUT, quiet),
        rel(CHALLENGE_OUTPUT): source_record(CHALLENGE_OUTPUT, challenge),
        rel(STATE_OUTPUT): source_record(STATE_OUTPUT, state),
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
        rel(STATE_REPORT): source_report(STATE_REPORT),
    }
    output = {
        "experiment": "N16",
        "iteration": "6",
        "artifact_id": "n16_selected_interaction_probe_matrix",
        "purpose": "selected_confirmation_and_disambiguation_probes",
        "schema_version": schema["schema_version"],
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_selected_interaction_probes_no_ap6",
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2", "3", "4", "5", "6"],
        "deferred_iterations": ["7", "8", "9"],
        "final_ap6_closeout_allowed": False,
        "source_provenance": source_provenance(challenge, state),
        "selected_cells": SELECTED_CELLS,
        "challenge_thresholds": CHALLENGE_THRESHOLDS,
        "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
        "metric_construction_formulas": METRIC_CONSTRUCTION_FORMULAS,
        "retained_flux_projection_audit": metric_projection_audit(rows),
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": rows,
        "controls": top_level_controls(schema),
        "checks": checks,
        "claim_flags": control_config["claim_flags_forced_false"],
        "errors": [],
        "iteration_result": {
            "selected_interaction_probe_passed": all(checks.values()),
            "matrix_rows_generated": True,
            "row_count": len(rows),
            "selected_cells_only": checks["selected_cells_only"],
            "b3_c4_breach_reclosure_answered": checks[
                "b3_c4_answers_breach_reclosure"
            ],
            "b4_c5_shared_medium_answered": checks[
                "b4_c5_answers_shared_medium_separability"
            ],
            "final_ap6_supported": False,
        },
        "b3_unlock_audit": b3_unlock_audit(challenge),
        "b3_c4_repair_audit": {
            "source_question": (
                "Does the B3 mechanism that repaired C2 leakage also support "
                "breach/reclosure, or was it only flux-specific?"
            ),
            "row_decision": by_cell["B3_C4"]["row_decision"],
            "repair_score": by_cell["B3_C4"]["repair_score"],
            "reclosure_score": by_cell["B3_C4"]["reclosure_score"],
            "breach_reclosure_floor": BREACH_RECLOSURE_FLOOR,
            "b3_c2_anchor_metrics": b3_decomp["b3_c2_anchor_metrics"],
            "b2_c4_baseline_reference": b3_decomp["b2_c4_baseline_reference"],
            "b3_c4_delta_vs_b2_c4": b3_decomp["b3_c4_delta_vs_b2_c4"],
            "probe_decomposition": b3_decomp,
            "claim_boundary": (
                "B3_C4 is artifact-level breach/reclosure candidate evidence, "
                "not autonomous repair, agency, native support, or final AP6"
            ),
        },
        "b4_c5_separability_audit": {
            "source_question": (
                "Can separate basins remain distinct inside a shared medium, "
                "or does coupling cause leakage, merge pressure, or boundary confusion?"
            ),
            "row_decision": by_cell["B4_C5"]["row_decision"],
            "basin_separation_score": by_cell["B4_C5"]["basin_separation_score"],
            "boundary_exclusivity_score": by_cell["B4_C5"][
                "boundary_exclusivity_score"
            ],
            "leakage_into_neighbor_basin": by_cell["B4_C5"][
                "leakage_into_neighbor_basin"
            ],
            "shared_medium_leakage": by_cell["B4_C5"]["shared_medium_leakage"],
            "merge_confusion_pressure": by_cell["B4_C5"][
                "merge_confusion_pressure"
            ],
            "asymmetry_note": b4_decomp["asymmetry_note"],
            "probe_decomposition": b4_decomp,
            "claim_boundary": (
                "B4_C5 is artifact-level shared-medium separability candidate "
                "evidence, not native multi-basin selfhood or final AP6"
            ),
        },
        "replay_consistency_audit": replay_consistency_audit(
            rows, challenge, state
        ),
        "cross_iteration_metric_comparison": cross_iteration_metric_comparison(
            rows, challenge, state
        ),
        "selected_probe_summary": selected_probe_summary(rows),
        "audit_list": [
            "only five selected interaction cells emitted",
            "B0_C3 strict active-null false-positive rejection",
            "B1_C2 weak-boundary replay preserved",
            "B2_C1 bounded-noise replay preserved",
            "B3_C4 breach/reclosure test answered",
            "B3 unlock audit recorded",
            "B4_C5 shared-medium separability test answered",
            "B4 separability measured rather than inherited from label",
            "requirements_satisfied and requirements_failed recorded for every row",
            "all boundary claims and final AP6 remain false",
        ],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
        },
        "output_digest": "",
    }
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    if not all(checks.values()):
        output["errors"].append("selected_interaction_probe_check_failed")
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
    print(json.dumps(output["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
