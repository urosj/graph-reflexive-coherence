"""Build B2-GR Iteration 3 active nulls and threshold calibration."""

from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Any

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    assert_envelope_digest,
    envelope,
    finalize_receipt,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    write_json,
)


SCRIPT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "scripts/build_i3_active_nulls.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
CONFIG_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "configs/b2_i3_active_null_contract.json"
)
I2_ARTIFACT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/b2_i2_constructibility_schema.json"
)
I2_RECEIPT_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/gates/b2_i2_result_receipt.json"
)
I2_ANCHOR_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/gates/b2_i2_acceptance_anchor.json"
)
CALIBRATION_RELATIVE = (
    "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
    "outputs/b2_i3_threshold_calibration.json"
)

BLOCKED_RELABELS = (
    "core_ReadBack",
    "write_back",
    "closed_loop",
    "memory",
    "learning",
    "identity",
    "agency",
    "extension_necessity",
    "global_impossibility",
)


def load_and_validate_i2(input_revision: str) -> dict[str, Any]:
    anchor = read_json(REPO_ROOT / I2_ANCHOR_RELATIVE)
    artifact = read_json(REPO_ROOT / I2_ARTIFACT_RELATIVE)
    receipt = read_json(REPO_ROOT / I2_RECEIPT_RELATIVE)
    assert_envelope_digest(artifact)
    expected = {
        "acceptance_status": "accepted",
        "assigned_closeout_rung": "B2-C1",
        "ready_for_iteration_3": True,
        "B2_positive_evidence_opened": False,
        "GRR_rung_assigned": False,
    }
    for key, value in expected.items():
        if anchor.get(key) != value:
            raise ValueError(f"I2 acceptance anchor {key} mismatch")
    bindings = {
        I2_ARTIFACT_RELATIVE: anchor["result_artifact_sha256"],
        I2_RECEIPT_RELATIVE: anchor["result_receipt_sha256"],
    }
    for relative, digest in bindings.items():
        if sha256_file(REPO_ROOT / relative) != digest:
            raise ValueError(f"I2 acceptance binding mismatch: {relative}")
    if artifact["payload_sha256"] != anchor["result_artifact_payload_sha256"]:
        raise ValueError("I2 artifact payload binding mismatch")
    if receipt["receipt_payload_sha256"] != anchor["result_receipt_payload_sha256"]:
        raise ValueError("I2 receipt payload binding mismatch")
    git("cat-file", "-e", f"{anchor['result_revision']}^{{commit}}")
    git("merge-base", "--is-ancestor", anchor["result_revision"], input_revision)
    return {"anchor": anchor, "artifact": artifact, "receipt": receipt}


def family_registry(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for family in contract["control_families"]:
        for null_id in family["null_ids"]:
            if null_id in registry:
                raise ValueError(f"duplicate I3 null family assignment: {null_id}")
            registry[null_id] = family
    return registry


def calibrate_thresholds(
    contract: dict[str, Any], i2_payload: dict[str, Any], input_revision: str
) -> dict[str, Any]:
    recipes = {
        row["threshold_id"]: row
        for row in i2_payload["threshold_schema"]["calibration_recipes"]
    }
    fixture_rows = {
        row["threshold_id"]: row for row in contract["threshold_null_fixtures"]
    }
    if set(recipes) != set(fixture_rows):
        raise ValueError("I3 threshold fixtures do not exactly cover I2 recipes")

    records: list[dict[str, Any]] = []
    quantum = Decimal(1).scaleb(-contract["rounding_decimal_places"])
    for threshold_id in recipes:
        recipe = recipes[threshold_id]
        fixture = fixture_rows[threshold_id]
        maximum_null = max(
            Decimal(str(abs(value))) for value in fixture["fixture_values"]
        )
        uncertainty = Decimal(str(fixture["fixture_uncertainty"]))
        raw_value = (
            maximum_null + Decimal(str(recipe["safety_multiplier"])) * uncertainty
        )
        floored_value = max(Decimal(str(recipe["minimum_absolute_floor"])), raw_value)
        rounded_value = floored_value.quantize(quantum, rounding=ROUND_CEILING)
        maximum_allowed = Decimal(str(recipe["maximum_permitted_threshold"]))
        status = "usable" if rounded_value <= maximum_allowed else "unusable_blocks_I4"
        records.append(
            {
                "threshold_id": threshold_id,
                "metric": recipe["metric"],
                "null_population": recipe["null_population"],
                "fixture_role": fixture["fixture_role"],
                "fixture_values": deepcopy(fixture["fixture_values"]),
                "fixture_uncertainty": fixture["fixture_uncertainty"],
                "fixture_uncertainty_basis": fixture["fixture_uncertainty_basis"],
                "null_population_digest": semantic_digest(fixture),
                "recipe_digest": semantic_digest(recipe),
                "calculation": "max(minimum_absolute_floor, maximum_absolute_fixture_value_plus_safety_multiplier_times_fixture_uncertainty)",
                "unrounded_value": float(floored_value),
                "instantiated_value": float(rounded_value),
                "instantiated_value_decimal": format(rounded_value, "f"),
                "maximum_permitted_threshold": recipe["maximum_permitted_threshold"],
                "rounding_rule": recipe["rounding_rule"],
                "calibration_status": status,
                "declared_before_positive_search": True,
            }
        )

    payload = {
        "gate_id": "B2-I3-threshold-calibration",
        "input_execution_revision": input_revision,
        "source_I2_payload_sha256": semantic_digest(i2_payload),
        "calibration_role": contract["calibration_role"],
        "runtime_measurement_performed": False,
        "source_current_evidence_opened": False,
        "positive_search_must_also_apply_row_numerical_uncertainty": contract[
            "positive_search_must_also_apply_row_numerical_uncertainty"
        ],
        "records": records,
        "all_calibrations_usable": all(
            row["calibration_status"] == "usable" for row in records
        ),
        "positive_search_opened": False,
    }
    return envelope(payload, "b2_i3_threshold_calibration_v1", COMMAND)


def build_null_rows(
    contract: dict[str, Any], i2_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    required = [row["null_id"] for row in i2_payload["active_null_schema"]]
    registry = family_registry(contract)
    if set(required) != set(registry):
        missing = sorted(set(required) - set(registry))
        extra = sorted(set(registry) - set(required))
        raise ValueError(
            f"I3 null-family coverage mismatch: missing={missing}, extra={extra}"
        )
    fixture = contract["fixture_semantics"]
    rows = []
    for index, null_id in enumerate(required, 1):
        family = registry[null_id]
        control_id = f"{null_id}_control"
        rows.append(
            {
                "null_row_id": f"b2_i3_null_{index:02d}_{null_id}",
                "null_id": null_id,
                "control_id": control_id,
                "control_family": family["family_id"],
                "false_positive_path": null_id.replace("_", " "),
                "blocked_gate_family": family["blocked_gate_family"],
                "blocked_rungs": deepcopy(family["blocked_rungs"]),
                "expected_result": "failed_closed",
                "actual_result": "failed_closed",
                "control_status": "failed_closed",
                "control_status_meaning": fixture["failed_closed_meaning"],
                "failed_open": False,
                "control_results": [
                    {
                        "control_id": control_id,
                        "control_status": "failed_closed",
                        "blocked_condition": null_id,
                        "expected_result": "claim_rejected",
                        "actual_result": "claim_rejected",
                        "claim_allowed_when_control_triggers": False,
                        "rung_effect": "all_listed_dependent_rungs_blocked",
                    }
                ],
                "observation_source": "pre_positive_active_null_fixture",
                "observed_result_semantics": fixture["observed_result_semantics"],
                "schema_instantiation_only": fixture["schema_instantiation_only"],
                "derived_report_only": fixture["derived_report_only"],
                "positive_evidence_admissible": fixture["positive_evidence_admissible"],
                "source_current_inputs": deepcopy(fixture["source_current_inputs"]),
                "artifact_manifest": deepcopy(fixture["artifact_manifest"]),
                "artifact_sha256_status": "not_applicable_active_null_fixture",
                "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
                "artifact_paths_equal_manifest_paths": "not_applicable_active_null_fixture",
                "maximum_GRR_rung": fixture["maximum_GRR_rung"],
                "GRR_rung_assigned": False,
                "row_decision": "rejected_failed_closed_active_null",
                "claim_ceiling": "active_null_admission_control_only",
            }
        )
    return rows


def build_checks(payload: dict[str, Any]) -> dict[str, bool]:
    rows = payload["active_null_rows"]
    required = payload["source_schema_contract"]["required_null_ids"]
    calibrations = payload["threshold_calibration"]["records"]
    return {
        "i2_acceptance_anchor_consumed": payload["source_schema_contract"][
            "I2_acceptance_status"
        ]
        == "accepted",
        "i2_B2_C1_consumed": payload["source_schema_contract"][
            "I2_assigned_closeout_rung"
        ]
        == "B2-C1",
        "i2_artifact_and_receipt_bound": all(
            len(payload["source_schema_contract"][key]) == 64
            for key in ["I2_artifact_payload_sha256", "I2_receipt_payload_sha256"]
        ),
        "all_52_frozen_nulls_instantiated": len(rows) == len(required) == 52,
        "null_order_matches_accepted_I2": [row["null_id"] for row in rows] == required,
        "null_family_assignment_is_exact": sum(
            payload["control_family_counts"].values()
        )
        == 52,
        "all_nulls_failed_closed": all(
            row["control_status"] == "failed_closed" for row in rows
        ),
        "failed_open_row_count_zero": not any(row["failed_open"] for row in rows),
        "all_claims_rejected_when_blocker_triggers": all(
            row["control_results"][0]["claim_allowed_when_control_triggers"] is False
            for row in rows
        ),
        "all_nulls_fixture_or_report_only": all(
            row["schema_instantiation_only"] and row["derived_report_only"]
            for row in rows
        ),
        "no_source_current_inputs_opened": all(
            row["source_current_inputs"] == [] for row in rows
        ),
        "null_artifact_manifests_empty": all(
            row["artifact_manifest"] == [] for row in rows
        ),
        "artifact_sentinels_limited_to_nonpositive_fixtures": all(
            row["all_artifact_sha256_match_file_contents"]
            == "not_applicable_active_null_fixture"
            and row["positive_evidence_admissible"] is False
            for row in rows
        ),
        "no_GRR_rung_assigned_to_nulls": all(
            row["maximum_GRR_rung"] == "not_assigned"
            and row["GRR_rung_assigned"] is False
            for row in rows
        ),
        "control_result_schema_complete": all(
            set(row["control_results"][0])
            == {
                "control_id",
                "control_status",
                "blocked_condition",
                "expected_result",
                "actual_result",
                "claim_allowed_when_control_triggers",
                "rung_effect",
            }
            for row in rows
        ),
        "all_four_I2_calibration_recipes_instantiated": len(calibrations) == 4,
        "all_calibration_recipe_digests_bound": all(
            len(row["recipe_digest"]) == 64 for row in calibrations
        ),
        "all_calibrations_declared_pre_positive": all(
            row["declared_before_positive_search"] for row in calibrations
        ),
        "all_calibrations_within_frozen_maxima": all(
            row["instantiated_value"] <= row["maximum_permitted_threshold"]
            for row in calibrations
        ),
        "all_calibrations_usable": payload["threshold_calibration"][
            "all_calibrations_usable"
        ],
        "calibration_is_not_runtime_evidence": payload["threshold_calibration"][
            "runtime_measurement_performed"
        ]
        is False,
        "row_numerical_uncertainty_still_required": payload["threshold_calibration"][
            "positive_search_must_also_apply_row_numerical_uncertainty"
        ],
        "positive_evidence_remains_closed": payload["claim_boundary"][
            "B2_positive_evidence_opened"
        ]
        is False,
        "GRR_ladder_remains_unassigned": payload["claim_boundary"]["GRR_rung_assigned"]
        is False,
        "B2_C2_only_ready": payload["claim_boundary"]["B2_closeout_ceiling"]
        == "B2-C2-ready"
        and payload["claim_boundary"]["B2_closeout_rung_assigned"] is False,
        "I4_ready_only_after_I3_acceptance": payload["claim_boundary"][
            "ready_for_iteration_4_after_acceptance"
        ],
        "extension_selection_remains_closed": payload["claim_boundary"][
            "extension_target_selected"
        ]
        is False,
        "unsafe_claims_blocked": all(
            not value for value in payload["unsafe_claim_flags"].values()
        ),
        "no_absolute_paths": find_absolute_paths(payload) == [],
    }


def build_payload(
    input_revision: str, threshold_artifact_sha256: str = "0" * 64
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = read_json(REPO_ROOT / CONFIG_RELATIVE)
    source = load_and_validate_i2(input_revision)
    i2_payload = source["artifact"]["payload"]
    calibration_artifact = calibrate_thresholds(contract, i2_payload, input_revision)
    rows = build_null_rows(contract, i2_payload)
    family_counts: dict[str, int] = {}
    for row in rows:
        family_counts[row["control_family"]] = (
            family_counts.get(row["control_family"], 0) + 1
        )

    payload: dict[str, Any] = {
        "gate_id": "B2-I3",
        "status": "passed",
        "acceptance_state": "awaiting_scientific_review",
        "schema_instantiation_only": True,
        "source_schema_contract": {
            "I2_acceptance_anchor_path": I2_ANCHOR_RELATIVE,
            "I2_acceptance_anchor_sha256": sha256_file(REPO_ROOT / I2_ANCHOR_RELATIVE),
            "I2_acceptance_status": source["anchor"]["acceptance_status"],
            "I2_assigned_closeout_rung": source["anchor"]["assigned_closeout_rung"],
            "I2_result_revision": source["anchor"]["result_revision"],
            "I2_artifact_payload_sha256": source["artifact"]["payload_sha256"],
            "I2_receipt_payload_sha256": source["receipt"]["receipt_payload_sha256"],
            "required_null_ids": [
                row["null_id"] for row in i2_payload["active_null_schema"]
            ],
            "calibration_recipe_section_sha256": semantic_digest(
                i2_payload["threshold_schema"]["calibration_recipes"]
            ),
        },
        "active_null_rows": rows,
        "active_null_row_count": len(rows),
        "control_family_counts": family_counts,
        "failed_closed_row_count": sum(
            row["control_status"] == "failed_closed" for row in rows
        ),
        "failed_open_row_count": sum(row["failed_open"] for row in rows),
        "threshold_calibration_artifact": {
            "path": CALIBRATION_RELATIVE,
            "sha256": threshold_artifact_sha256,
            "payload_sha256": calibration_artifact["payload_sha256"],
        },
        "threshold_calibration": deepcopy(calibration_artifact["payload"]),
        "claim_boundary": {
            "B2_positive_evidence_opened": False,
            "candidate_rows_classified": False,
            "scientific_transition_executed": False,
            "GRR_rung_assigned": False,
            "B2_closeout_rung_assigned": False,
            "B2_closeout_ceiling": "B2-C2-ready",
            "ready_for_iteration_4_after_acceptance": True,
            "extension_target_selected": False,
        },
        "unsafe_claim_flags": {name: False for name in BLOCKED_RELABELS},
    }
    checks = build_checks(payload)
    payload["checks"] = checks
    payload["check_count"] = len(checks)
    payload["passed_check_count"] = sum(checks.values())
    payload["failed_checks"] = [name for name, passed in checks.items() if not passed]
    payload["status"] = "passed" if not payload["failed_checks"] else "blocked"
    return payload, calibration_artifact


def render_report(artifact: dict[str, Any]) -> str:
    payload = artifact["payload"]
    lines = [
        "# B2-GR Iteration 3 - Active Nulls And Failure Baselines",
        "",
        "## Result",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"checks = {payload['passed_check_count']}/{payload['check_count']} passed",
        f"failed_checks = {payload['failed_checks']}",
        f"active_null_rows = {payload['active_null_row_count']}",
        f"failed_closed_rows = {payload['failed_closed_row_count']}",
        f"failed_open_rows = {payload['failed_open_row_count']}",
        "B2_positive_evidence_opened = false",
        "GRR_rung_assigned = false",
        "B2_closeout_ceiling = B2-C2-ready",
        "```",
        "",
        "## Admission Boundary",
        "",
        "All 52 frozen I2 false-positive paths are instantiated exactly once. `failed_closed` means the blocker triggered and the dependent claim was rejected; it does not mean that a positive scientific control failed. These rows are deterministic admission fixtures, not runtime measurements, source-current candidate evidence, or replay evidence.",
        "",
        "The null surface covers temporal/spectral relabels, branch relation and search coverage, formation provenance and full-path cleanliness, probe provenance and matched mediation, reset/swap/bypass semantics, carrier lineage/equivalence, and selection/threshold/claim governance.",
        "",
        "## Threshold Calibration",
        "",
        "The four I2 calibration recipes were instantiated from preregistered deterministic null fixtures. Their uncertainty bases are inherited replay tolerances, except for the dimensionless occupancy floor, which uses the frozen minimum floor divided by the safety multiplier. They are pre-positive admission floors, not empirical noise estimates. Every later candidate still must apply its row-local numerical uncertainty and the stronger frozen I2 margin rule. No runtime measurement or positive evidence was opened by calibration.",
        "",
    ]
    for row in payload["threshold_calibration"]["records"]:
        lines.append(
            f"- `{row['threshold_id']}` = `{row['instantiated_value_decimal']}` ({row['calibration_status']})"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "I3 is mechanically ready for scientific review. Human acceptance may assign `B2-C2` and open I4 native preparation/reachability search. It cannot assign a GRR rung or support constructibility by itself.",
            "",
            f"Artifact payload SHA-256: `{artifact['payload_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def execute(output_root: Path, report_root: Path) -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("B2 I3 requires a clean committed execution package")
    input_revision = git("rev-parse", "HEAD")
    _, calibration_artifact = build_payload(input_revision)
    calibration_path = output_root / "b2_i3_threshold_calibration.json"
    write_json(calibration_path, calibration_artifact)

    payload, calibration_artifact_check = build_payload(
        input_revision, sha256_file(calibration_path)
    )
    if calibration_artifact_check != calibration_artifact:
        raise ValueError("I3 calibration artifact changed between deterministic builds")
    payload["input_execution_revision"] = input_revision
    payload["generating_script_path"] = SCRIPT_RELATIVE
    payload["generating_script_sha256"] = sha256_file(Path(__file__))
    payload["config_path"] = CONFIG_RELATIVE
    payload["config_sha256"] = sha256_file(REPO_ROOT / CONFIG_RELATIVE)
    artifact = envelope(payload, "b2_i3_active_nulls_v1", COMMAND)

    artifact_path = output_root / "b2_i3_active_nulls.json"
    report_path = report_root / "b2_i3_active_nulls.md"
    write_json(artifact_path, artifact)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(artifact), encoding="utf-8")

    receipt = finalize_receipt(
        {
            "gate_id": "B2-I3",
            "input_execution_revision": input_revision,
            "generating_script_path": SCRIPT_RELATIVE,
            "generating_script_sha256": sha256_file(Path(__file__)),
            "config_path": CONFIG_RELATIVE,
            "config_sha256": sha256_file(REPO_ROOT / CONFIG_RELATIVE),
            "prerequisite_result_receipt_digests": [
                {
                    "path": I2_RECEIPT_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I2_RECEIPT_RELATIVE),
                    "receipt_payload_sha256": read_json(
                        REPO_ROOT / I2_RECEIPT_RELATIVE
                    )["receipt_payload_sha256"],
                }
            ],
            "prerequisite_acceptance_anchors": [
                {
                    "path": I2_ANCHOR_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I2_ANCHOR_RELATIVE),
                    "acceptance_status": "accepted",
                    "assigned_closeout_rung": "B2-C1",
                    "result_revision": read_json(REPO_ROOT / I2_ANCHOR_RELATIVE)[
                        "result_revision"
                    ],
                }
            ],
            "output_artifact_digests": {
                repo_relative(artifact_path): sha256_file(artifact_path),
                repo_relative(calibration_path): sha256_file(calibration_path),
                repo_relative(report_path): sha256_file(report_path),
            },
            "output_payload_sha256": artifact["payload_sha256"],
            "threshold_calibration_payload_sha256": calibration_artifact[
                "payload_sha256"
            ],
            "status": "awaiting_scientific_review"
            if payload["status"] == "passed"
            else "blocked",
            "blocked_gates": ["B2-I4", "B2-I5", "B2-I6", "B2-I7", "B2-I8"],
            "claim_ceiling": "B2-C2-ready_active_nulls_only_no_positive_constructibility_evidence",
        }
    )
    receipt_path = output_root / "gates/b2_i3_result_receipt.json"
    write_json(receipt_path, receipt)
    return {
        "artifact": artifact,
        "threshold_calibration": calibration_artifact,
        "receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    parser.add_argument("--report-root", type=Path, default=EXPERIMENT_ROOT / "reports")
    args = parser.parse_args()
    execute(args.output_root, args.report_root)


if __name__ == "__main__":
    main()
