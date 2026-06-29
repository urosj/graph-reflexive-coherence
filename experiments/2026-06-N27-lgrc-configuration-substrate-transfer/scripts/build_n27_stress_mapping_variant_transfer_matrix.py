#!/usr/bin/env python3
"""Build N27 Iteration 6 stress / mapping-variant transfer matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_stress_mapping_variant_transfer_matrix.json"
REPORT = EXPERIMENT / "reports" / "n27_stress_mapping_variant_transfer_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_stress_mapping_variant_transfer_matrix_artifacts"

I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n27_minimal_configuration_transfer_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n27_replay_same_basin_mapping_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n27_artifact_only_reconstruction_replay_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_stress_mapping_variant_transfer_matrix.py"
)

N27_CLOSEOUT_CEILING = "N27-C4_source_current_transfer_candidate_supported"

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

STRESS_POLICY = {
    "policy_id": "n27_i6_bounded_mapping_variant_stress_policy",
    "declared_before_use": True,
    "declaration_order": 0,
    "stress_rows": [
        {
            "stress_id": "boundary_tightening_0_05",
            "boundary_margin_cost": 0.05,
            "support_margin_cost": 0.0,
            "coherence_margin_cost": 0.0,
            "flux_margin_cost": 0.0,
        },
        {
            "stress_id": "support_drawdown_0_008",
            "boundary_margin_cost": 0.0,
            "support_margin_cost": 0.008,
            "coherence_margin_cost": 0.0,
            "flux_margin_cost": 0.0,
        },
        {
            "stress_id": "coherence_drawdown_0_012",
            "boundary_margin_cost": 0.0,
            "support_margin_cost": 0.0,
            "coherence_margin_cost": 0.012,
            "flux_margin_cost": 0.0,
        },
        {
            "stress_id": "flux_pressure_0_02",
            "boundary_margin_cost": 0.0,
            "support_margin_cost": 0.0,
            "coherence_margin_cost": 0.0,
            "flux_margin_cost": 0.02,
        },
        {
            "stress_id": "combined_moderate_mapping_stress",
            "boundary_margin_cost": 0.03,
            "support_margin_cost": 0.005,
            "coherence_margin_cost": 0.006,
            "flux_margin_cost": 0.01,
        },
    ],
    "pass_rule": "all residual margins must remain greater than or equal to zero",
    "ct5_assignment_note": (
        "I6 may support stress/variant evidence, but CT5 ladder assignment remains "
        "pending I7 full controls because the frozen CT5 artifact role includes a "
        "control trace."
    ),
}


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


def find_i5_row(i5: dict[str, Any], source_iteration: str) -> dict[str, Any]:
    for row in i5["replay_rows"]:
        if row["source_iteration"] == source_iteration:
            return row
    raise ValueError(f"missing I5 row for source iteration {source_iteration}")


def find_i5a_row(i5a: dict[str, Any], source_iteration: str) -> dict[str, Any]:
    for row in i5a["reconstruction_rows"]:
        if row["source_iteration"] == source_iteration:
            return row
    raise ValueError(f"missing I5-A row for source iteration {source_iteration}")


def base_margins(replay_row: dict[str, Any]) -> dict[str, float]:
    return {
        "boundary": replay_row["boundary_mapping_trace"]["boundary_mapping_margin"],
        "support": replay_row["support_preservation_trace"]["support_floor_margin"],
        "coherence": replay_row["coherence_preservation_trace"][
            "coherence_floor_margin"
        ],
        "flux": replay_row["flux_balance_trace"]["flux_balance_margin"],
        "signature": replay_row["post_transfer_basin_signature_trace"][
            "signature_preservation_margin"
        ],
    }


def apply_stress(margins: dict[str, float]) -> list[dict[str, Any]]:
    stress_results: list[dict[str, Any]] = []
    for stress in STRESS_POLICY["stress_rows"]:
        residuals = {
            "boundary": round(margins["boundary"] - stress["boundary_margin_cost"], 12),
            "support": round(margins["support"] - stress["support_margin_cost"], 12),
            "coherence": round(
                margins["coherence"] - stress["coherence_margin_cost"], 12
            ),
            "flux": round(margins["flux"] - stress["flux_margin_cost"], 12),
            "signature": margins["signature"],
        }
        failed_axes = [
            axis for axis in ("boundary", "support", "coherence", "flux") if residuals[axis] < 0
        ]
        stress_results.append(
            {
                "stress_id": stress["stress_id"],
                "stress_costs": {
                    "boundary": stress["boundary_margin_cost"],
                    "support": stress["support_margin_cost"],
                    "coherence": stress["coherence_margin_cost"],
                    "flux": stress["flux_margin_cost"],
                },
                "residual_margins": residuals,
                "stress_passed": not failed_axes,
                "failed_axes": failed_axes,
            }
        )
    return stress_results


def build_stress_row(
    source_iteration: str,
    source_label: str,
    i5: dict[str, Any],
    i5a: dict[str, Any],
) -> dict[str, Any]:
    replay_row = find_i5_row(i5, source_iteration)
    reconstruction_row = find_i5a_row(i5a, source_iteration)
    margins = base_margins(replay_row)
    stress_results = apply_stress(margins)
    all_stress_passed = all(item["stress_passed"] for item in stress_results)
    failed_stress_ids = [item["stress_id"] for item in stress_results if not item["stress_passed"]]
    stress_trace = {
        "trace_id": f"n27_i6_{source_label}_stress_variant_trace",
        "source_iteration": source_iteration,
        "source_replay_row_id": replay_row["row_id"],
        "source_reconstruction_row_id": reconstruction_row["row_id"],
        "transfer_mapping_id": replay_row["transfer_mapping_id"],
        "transfer_scope": replay_row["transfer_scope"],
        "source_transfer_core_digest": replay_row["transfer_core_digest"],
        "artifact_only_reconstruction_digest": reconstruction_row[
            "transfer_core_digest"
        ],
        "stress_policy": STRESS_POLICY,
        "base_margins": margins,
        "stress_results": stress_results,
        "all_stress_rows_passed": all_stress_passed,
        "failed_stress_ids": failed_stress_ids,
        "baseline_boundary_at_floor": margins["boundary"] == 0,
        "stress_failure_mode": (
            "none"
            if all_stress_passed
            else "declared_stress_exceeds_available_margin"
        ),
        "new_transfer_evidence_created": False,
        "stress_variant_trace_role": "stress_existing_replay_backed_transfer_candidate",
    }
    trace_record = trace_artifact("stress_variant_trace", f"n27_i6_row_{source_label}_stress", stress_trace)
    control_trace = {
        "trace_id": f"n27_i6_{source_label}_stress_control_trace",
        "trace_scope": "stress_control_trace_only_not_full_i7_control_matrix",
        "stress_variant_failure_control_status": "passed"
        if all_stress_passed
        else "failed_closed",
        "stress_variant_failure_control_meaning": (
            "stress envelope passed"
            if all_stress_passed
            else "stress blocker triggered and stronger stress claim was rejected"
        ),
        "ct5_assignment_allowed_before_i7_controls": False,
        "ct5_assignment_blocker": "full_control_trace_pending_iteration_7",
    }
    control_record = trace_artifact("control_trace", f"n27_i6_row_{source_label}_stress", control_trace)
    return {
        "artifact_manifest": [trace_record, control_record],
        "base_margins": margins,
        "claim_ceiling": (
            "stress/variant evidence over an existing CT3 candidate; CT5 ladder "
            "assignment remains pending I7 controls and final transfer remains blocked"
        ),
        "control_trace": control_trace,
        "control_trace_digest": digest_value(control_trace),
        "ct_ladder_rung": "CT5_candidate_pending_controls"
        if all_stress_passed
        else "CT3_stress_limited",
        "ct5_assignment_allowed": False,
        "ct5_assignment_blocker": "full_control_trace_pending_iteration_7",
        "ct5_stress_variant_candidate_supported": all_stress_passed,
        "final_transfer_supported": False,
        "iteration": "6",
        "new_transfer_evidence_created": False,
        "row_decision": "supported" if all_stress_passed else "partial",
        "row_decision_scope": (
            "bounded_stress_variant_candidate_pending_i7_controls"
            if all_stress_passed
            else "replay_backed_candidate_stress_limited_by_declared_margin"
        ),
        "row_id": f"n27_i6_row_{source_label}_stress_mapping_variant",
        "source_iteration": source_iteration,
        "source_output_digest": replay_row["source_output_digest"],
        "source_replay_row_id": replay_row["row_id"],
        "source_reconstruction_row_id": reconstruction_row["row_id"],
        "source_transfer_core_digest": replay_row["transfer_core_digest"],
        "stress_failure_mode": stress_trace["stress_failure_mode"],
        "stress_trace": stress_trace,
        "stress_trace_digest": digest_value(stress_trace),
        "transfer_core_digest": replay_row["transfer_core_digest"],
        "transfer_mapping_id": replay_row["transfer_mapping_id"],
        "transfer_scope": replay_row["transfer_scope"],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


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
    i5: dict[str, Any],
    i5a: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["stress_rows"]
    return [
        check(
            "source_chain_digests_match",
            output["source_inventory_output_digest"] == i1["output_digest"]
            and output["transfer_schema_output_digest"] == i2["output_digest"]
            and output["active_nulls_output_digest"] == i3["output_digest"]
            and output["minimal_configuration_transfer_output_digest"]
            == i4["output_digest"]
            and output["topology_fixture_variant_transfer_output_digest"]
            == i4a["output_digest"]
            and output["replay_same_basin_mapping_output_digest"] == i5["output_digest"]
            and output["artifact_only_reconstruction_replay_output_digest"]
            == i5a["output_digest"],
            {"i5": i5["output_digest"], "i5a": i5a["output_digest"]},
        ),
        check(
            "i5_and_i5a_ready_for_stress",
            i5["status"] == "passed"
            and i5a["status"] == "passed"
            and i5["ct3_replay_candidate_supported"] is True
            and i5a["ct3_replay_hygiene_supported"] is True,
            {
                "i5_status": i5["status"],
                "i5a_status": i5a["status"],
                "i5_ct3": i5["ct3_replay_candidate_supported"],
                "i5a_hygiene": i5a["ct3_replay_hygiene_supported"],
            },
        ),
        check(
            "stress_rows_cover_i4_and_i4a_separately",
            len(rows) == 2
            and {row["source_iteration"] for row in rows} == {"4", "4-A"},
            [row["source_iteration"] for row in rows],
        ),
        check(
            "stress_policy_declared_before_use",
            output["stress_policy"]["declared_before_use"] is True
            and output["stress_policy"]["declaration_order"] == 0,
            output["stress_policy"],
        ),
        check(
            "i4_boundary_at_floor_exposed",
            any(
                row["source_iteration"] == "4"
                and row["base_margins"]["boundary"] == 0
                and row["row_decision"] == "partial"
                and "boundary_tightening_0_05" in row["stress_trace"]["failed_stress_ids"]
                for row in rows
            ),
            [row for row in rows if row["source_iteration"] == "4"],
        ),
        check(
            "i4a_passes_declared_stress_envelope",
            any(
                row["source_iteration"] == "4-A"
                and row["row_decision"] == "supported"
                and row["ct5_stress_variant_candidate_supported"] is True
                and row["stress_trace"]["all_stress_rows_passed"] is True
                for row in rows
            ),
            [row for row in rows if row["source_iteration"] == "4-A"],
        ),
        check(
            "stress_variant_evidence_does_not_create_new_transfer",
            all(row["new_transfer_evidence_created"] is False for row in rows)
            and output["new_transfer_evidence_created"] is False,
            [row["row_id"] for row in rows],
        ),
        check(
            "stress_artifact_sha256_match_file_contents",
            all(artifact_sha256_matches(row["artifact_manifest"]) for row in rows),
            [row["row_id"] for row in rows],
        ),
        check(
            "ct5_assignment_deferred_until_i7_controls",
            output["ct5_stress_variant_candidate_supported"] is True
            and output["ct5_assignment_allowed"] is False
            and output["ct5_assignment_blocker"] == "full_control_trace_pending_iteration_7"
            and output["ct5_or_stronger_supported"] is False,
            {
                "candidate": output["ct5_stress_variant_candidate_supported"],
                "allowed": output["ct5_assignment_allowed"],
                "blocker": output["ct5_assignment_blocker"],
            },
        ),
        check(
            "final_transfer_remains_blocked",
            output["final_transfer_supported"] is False
            and all(not row["final_transfer_supported"] for row in rows),
            {"final_transfer_supported": output["final_transfer_supported"]},
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
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    rows = [
        build_stress_row("4", "i4", i5, i5a),
        build_stress_row("4-A", "i4a", i5, i5a),
    ]
    supported_stress_rows = [
        row for row in rows if row["ct5_stress_variant_candidate_supported"]
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_stress_mapping_variant_transfer_matrix",
        "experiment": "N27",
        "iteration": "6",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Stress replay-backed CT3 transfer candidates across boundary, support, "
            "coherence, flux, and mapping-variant pressure while preserving claim "
            "ceilings."
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
            source_record(
                I5_OUTPUT,
                "n27_i5_replay_same_basin_mapping",
                "replay_same_basin_mapping_matrix",
            ),
            source_record(
                I5A_OUTPUT,
                "n27_i5a_artifact_only_reconstruction",
                "artifact_only_reconstruction_hygiene",
            ),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "topology_fixture_variant_transfer_output_digest": i4a["output_digest"],
        "replay_same_basin_mapping_output_digest": i5["output_digest"],
        "artifact_only_reconstruction_replay_output_digest": i5a["output_digest"],
        "status": "pending",
        "acceptance_state": "pending",
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": True,
        "new_transfer_evidence_created": False,
        "candidate_rows_classified": True,
        "provisional_ct_ladder_rung": "CT5_candidate_pending_controls",
        "ct_ladder_rung_assigned": False,
        "ct_assignment_scope": "stress_variant_candidate_pending_i7_controls_and_closeout",
        "ct3_replay_candidate_supported": True,
        "ct5_stress_variant_candidate_supported": bool(supported_stress_rows),
        "ct5_assignment_allowed": False,
        "ct5_assignment_blocker": "full_control_trace_pending_iteration_7",
        "ct5_or_stronger_supported": False,
        "ct6_or_stronger_supported": False,
        "final_transfer_supported": False,
        "stress_policy": STRESS_POLICY,
        "stress_matrix_summary": {
            "candidate_count": len(rows),
            "stress_pass_count": len(supported_stress_rows),
            "stress_limited_count": len(rows) - len(supported_stress_rows),
            "i4_boundary_at_floor_exposed": True,
            "i4a_topology_variant_stress_candidate_supported": any(
                row["source_iteration"] == "4-A"
                and row["ct5_stress_variant_candidate_supported"]
                for row in rows
            ),
            "full_matrix_broad_stress_support": all(
                row["ct5_stress_variant_candidate_supported"] for row in rows
            ),
        },
        "iteration_7_handoff": {
            "handoff_status": "ready_for_full_controls_ap_dependency_claim_classification",
            "i6_control_trace_scope": "stress_control_trace_only_not_full_i7_control_matrix",
            "i4_consumption": {
                "source_iteration": "4",
                "consume_as": "CT3_replay_backed_stress_limited_candidate",
                "ct5_contribution_allowed": False,
                "demote_below_ct3_without_new_control_failure": False,
            },
            "i4a_consumption": {
                "source_iteration": "4-A",
                "consume_as": "CT5_candidate_evidence_pending_i7_controls",
                "ct5_assignment_allowed_before_i7": False,
                "ct5_assignment_blocker": "full_control_trace_pending_iteration_7",
            },
            "required_i7_validations": [
                "all_frozen_controls_run_or_explicitly_not_applicable",
                "failed_open_controls_equal_zero",
                "same_label_movement_proxy_relabel_support_reconstruction_controls_clean",
                "n26_not_counted_as_transfer_evidence",
                "n25_2_not_directly_consumed",
                "ap4_ap5_row_local_statuses_valid",
                "native_ap5_and_ap5_nat4_gap_resolution_blocked",
                "semantic_identity_native_support_phase8_ant_ecology_claims_false",
            ],
        },
        "stress_rows": rows,
        "ready_for_iteration_7_controls_ap_dependency_claim_classification": True,
        "claim_boundary": {
            "claim_ceiling": (
                "bounded stress/variant evidence candidate pending I7 controls; "
                "final transfer, native AP5, AP5 NAT4-gap resolution, Phase 8, "
                "and ant ecology remain blocked"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    checks = build_checks(output, i1, i2, i3, i4, i4a, i5, i5a)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_stress_mapping_variant_candidate_pending_i7_controls_no_final_transfer"
        if output["status"] == "passed"
        else "blocked_stress_mapping_variant_transfer_matrix"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 6 - Stress / Mapping-Variant Transfer Matrix

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 6 stress-tests the two replay-backed CT3 candidates. It exposes the
I4 boundary-at-floor limitation and tests whether I4-A's distinct topology
fixture has enough positive margin to survive the declared stress envelope.

```text
ct5_stress_variant_candidate_supported = {str(output['ct5_stress_variant_candidate_supported']).lower()}
ct5_assignment_allowed = {str(output['ct5_assignment_allowed']).lower()}
ct5_assignment_blocker = {output['ct5_assignment_blocker']}
ct5_or_stronger_supported = {str(output['ct5_or_stronger_supported']).lower()}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
```

## Stress Rows

| Row | Source | Scope | Decision | Stress Candidate | Failed Stress Rows |
| --- | --- | --- | --- | --- | --- |
"""
    for row in output["stress_rows"]:
        failed = ", ".join(row["stress_trace"]["failed_stress_ids"]) or "none"
        report += (
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['transfer_scope']}` | `{row['row_decision']}` | "
            f"`{str(row['ct5_stress_variant_candidate_supported']).lower()}` | "
            f"`{failed}` |\n"
        )

    report += """
## Geometric Interpretation

I6 keeps the two mapping families separate. The I4 alpha/beta row remains a
valid replay-backed CT3 candidate, but its boundary margin was already exactly
at floor, so a boundary-tightening stress row fails closed. This does not
invalidate I4; it records the narrowness of that transfer surface.

The I4-A gamma/delta topology fixture row has positive boundary, support,
coherence, and flux margins. It survives the declared bounded stress envelope,
so it becomes stress/variant candidate evidence. The result still does not
assign CT5 because the frozen CT5 role also requires a full control trace,
which is I7 scope.

## I7 Handoff

I7 must consume I6 asymmetrically. The I4 alpha/beta row remains
replay-backed CT3 evidence, but it is stress-limited and does not contribute
to CT5. The I4-A gamma/delta row is CT5-candidate evidence only: CT5
assignment remains blocked until the full I7 control matrix, AP4/AP5
dependency checks, and claim classification pass with no failed-open controls.

The I6 control trace is only a stress-control trace. It is not the full I7
control matrix.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Interpretation

I6 strengthens N27 by showing that the distinct topology/fixture variant can
survive bounded stress, while the minimal I4 row is correctly classified as
stress-limited at its boundary edge. This is stress/variant candidate evidence
pending I7 controls. It is not final transfer, semantic identity, native
support, native AP5, AP5 NAT4-gap resolution, Phase 8, or ant ecology.

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
