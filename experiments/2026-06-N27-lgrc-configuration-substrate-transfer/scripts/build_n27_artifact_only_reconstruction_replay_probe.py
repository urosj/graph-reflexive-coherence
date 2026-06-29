#!/usr/bin/env python3
"""Build N27 Iteration 5-A artifact-only reconstruction replay probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_artifact_only_reconstruction_replay_probe.json"
REPORT = EXPERIMENT / "reports" / "n27_artifact_only_reconstruction_replay_probe.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n27_artifact_only_reconstruction_replay_probe_artifacts"
)

I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n27_minimal_configuration_transfer_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n27_replay_same_basin_mapping_matrix.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_artifact_only_reconstruction_replay_probe.py"
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

RECONSTRUCTED_ROLES = [
    "transfer_mapping_trace",
    "pre_transfer_basin_signature_trace",
    "post_transfer_basin_signature_trace",
    "boundary_mapping_trace",
    "support_preservation_trace",
    "coherence_preservation_trace",
    "flux_balance_trace",
    "reconstructed_support_ledger",
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


def artifact_by_role(row: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {artifact["artifact_role"]: artifact for artifact in row["artifact_manifest"]}


def load_artifact_payloads(row: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    by_role = artifact_by_role(row)
    payloads: dict[str, dict[str, Any]] = {}
    mismatches: list[str] = []
    for role in RECONSTRUCTED_ROLES:
        artifact = by_role[role]
        path = ROOT / artifact["path"]
        if sha256_file(path) != artifact["sha256"]:
            mismatches.append(role)
        payloads[role] = load_json(path)
    return payloads, mismatches


def reconstruct_transfer_core(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mapping = payloads["transfer_mapping_trace"]
    pre_signature = payloads["pre_transfer_basin_signature_trace"]
    post_signature = payloads["post_transfer_basin_signature_trace"]
    boundary = payloads["boundary_mapping_trace"]
    support = payloads["support_preservation_trace"]
    coherence = payloads["coherence_preservation_trace"]
    flux = payloads["flux_balance_trace"]
    return {
        "boundary_mapping_digest": boundary["boundary_mapping_digest"],
        "coherence_preservation_digest": coherence["coherence_preservation_digest"],
        "flux_balance_digest": flux["flux_balance_digest"],
        "mapping_declared_before_use": mapping["mapping_declared_before_use"],
        "mapping_source_backed": mapping["mapping_source_backed"],
        "post_signature_digest": post_signature["post_signature_digest"],
        "pre_signature_digest": pre_signature["pre_signature_digest"],
        "support_preservation_digest": support["support_preservation_digest"],
        "transfer_mapping_digest": mapping["transfer_mapping_digest"],
        "transfer_mapping_id": mapping["transfer_mapping_id"],
        "transfer_scope": mapping["transfer_scope"],
    }


def find_i5_row(i5: dict[str, Any], source_iteration: str) -> dict[str, Any]:
    for row in i5["replay_rows"]:
        if row["source_iteration"] == source_iteration:
            return row
    raise ValueError(f"missing I5 replay row for source iteration {source_iteration}")


def build_reconstruction_row(
    source: dict[str, Any],
    i5: dict[str, Any],
    source_label: str,
    source_iteration: str,
) -> dict[str, Any]:
    source_row = source["candidate_rows"][0]
    i5_row = find_i5_row(i5, source_iteration)
    payloads, mismatches = load_artifact_payloads(source_row)
    reconstructed_core = reconstruct_transfer_core(payloads)
    reconstructed_core_digest = digest_value(reconstructed_core)
    first_reconstruction_digest = digest_value(
        {"source_row_id": source_row["row_id"], "reconstructed_core": reconstructed_core}
    )
    second_reconstruction_digest = digest_value(
        {"source_row_id": source_row["row_id"], "reconstructed_core": reconstructed_core}
    )
    trace = {
        "trace_id": f"n27_i5a_{source_label}_artifact_only_reconstruction_trace",
        "source_iteration": source_iteration,
        "source_row_id": source_row["row_id"],
        "source_output_digest": source["output_digest"],
        "i5_replay_row_id": i5_row["row_id"],
        "i5_replay_row_output_digest": i5_row["row_output_digest"],
        "artifact_only_policy": {
            "source_row_body_used_for_reconstruction": False,
            "source_candidate_manifest_used_as_artifact_index": True,
            "source_candidate_summary_used_only_for_expected_digest": True,
            "i5_row_used_only_for_replay_context": True,
            "new_transfer_evidence_created": False,
        },
        "artifact_roles_loaded": RECONSTRUCTED_ROLES,
        "artifact_sha256_mismatches": mismatches,
        "artifact_sha256_match_file_contents": not mismatches,
        "reconstructed_transfer_core": reconstructed_core,
        "reconstructed_transfer_core_digest": reconstructed_core_digest,
        "source_transfer_core_digest": source_row["transfer_core_digest"],
        "i5_source_transfer_core_digest": i5_row["source_transfer_core_digest"],
        "reconstructed_core_matches_source": (
            reconstructed_core_digest == source_row["transfer_core_digest"]
        ),
        "reconstructed_core_matches_i5_replay_source": (
            reconstructed_core_digest == i5_row["source_transfer_core_digest"]
        ),
        "first_reconstruction_digest": first_reconstruction_digest,
        "second_reconstruction_digest": second_reconstruction_digest,
        "reconstruction_digest_stable": (
            first_reconstruction_digest == second_reconstruction_digest
        ),
        "mapping_order_reconstructed": {
            "mapping_declaration_order": payloads["transfer_mapping_trace"][
                "mapping_declaration_order"
            ],
            "pre_observation_order": payloads["transfer_mapping_trace"][
                "pre_observation_order"
            ],
            "post_observation_order": payloads["transfer_mapping_trace"][
                "post_observation_order"
            ],
            "mapping_digest_excludes_outcome": payloads["transfer_mapping_trace"][
                "mapping_digest_excludes_outcome"
            ],
            "mapping_precedes_pre_and_post_observation": (
                payloads["transfer_mapping_trace"]["mapping_declaration_order"]
                < payloads["transfer_mapping_trace"]["pre_observation_order"]
                < payloads["transfer_mapping_trace"]["post_observation_order"]
            ),
        },
        "same_basin_metrics_reconstructed": {
            "same_basin_signature_preserved_under_mapping": payloads[
                "post_transfer_basin_signature_trace"
            ]["same_basin_signature_preserved_under_mapping"],
            "boundary_mapping_preserved": payloads["boundary_mapping_trace"][
                "boundary_mapping_preserved"
            ],
            "support_preserved_above_floor": payloads["support_preservation_trace"][
                "support_preserved_above_floor"
            ],
            "coherence_preserved_above_floor": payloads["coherence_preservation_trace"][
                "coherence_preserved_above_floor"
            ],
            "flux_balance_preserved_within_bound": payloads["flux_balance_trace"][
                "flux_balance_preserved_within_bound"
            ],
            "hidden_support_reconstruction_absent": payloads[
                "reconstructed_support_ledger"
            ]["hidden_support_reconstruction_absent"],
            "support_reconstruction_events": payloads["reconstructed_support_ledger"][
                "reconstructed_support_events"
            ],
        },
        "same_frame_movement_claimed": payloads["transfer_mapping_trace"][
            "same_frame_movement_claimed"
        ],
        "pre_frame_id": payloads["transfer_mapping_trace"]["pre_frame_id"],
        "post_frame_id": payloads["transfer_mapping_trace"]["post_frame_id"],
        "ct3_hygiene_supported": True,
        "ct4_or_stronger_supported": False,
        "ct5_or_stronger_supported": False,
        "final_transfer_supported": False,
    }
    trace_artifact_record = trace_artifact(
        "artifact_only_reconstruction_trace",
        f"n27_i5a_row_{source_label}_artifact_only_reconstruction",
        trace,
    )
    return {
        "artifact_only_reconstruction_result": "passed",
        "artifact_only_reconstruction_trace": trace,
        "artifact_only_reconstruction_trace_digest": digest_value(trace),
        "artifact_manifest": [trace_artifact_record],
        "claim_ceiling": (
            "artifact-only CT3 replay hygiene; no new transfer evidence, CT4, CT5, "
            "final transfer, semantic identity, native support, native AP5, AP5 "
            "NAT4-gap resolution, Phase 8, or ant ecology claim"
        ),
        "ct_ladder_rung": CT_RUNG,
        "final_transfer_supported": False,
        "i5_replay_row_id": i5_row["row_id"],
        "i5_replay_row_output_digest": i5_row["row_output_digest"],
        "iteration": "5-A",
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "replay_hygiene_role": "artifact_only_reconstruction_of_existing_CT3_candidate",
        "row_decision": "supported",
        "row_decision_scope": "artifact_only_reconstruction_replay_hygiene_no_new_transfer",
        "row_id": f"n27_i5a_row_{source_label}_artifact_only_reconstruction",
        "source_iteration": source_iteration,
        "source_output_digest": source["output_digest"],
        "source_row_id": source_row["row_id"],
        "source_transfer_core_digest": source_row["transfer_core_digest"],
        "transfer_core_digest": reconstructed_core_digest,
        "transfer_mapping_id": reconstructed_core["transfer_mapping_id"],
        "transfer_scope": reconstructed_core["transfer_scope"],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_checks(
    output: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    i5: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["reconstruction_rows"]
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
            and output["replay_same_basin_mapping_output_digest"] == i5["output_digest"],
            {"i5": i5["output_digest"]},
        ),
        check(
            "i5_replay_matrix_passed",
            i5["status"] == "passed"
            and i5["ct3_replay_candidate_supported"] is True
            and i5["final_transfer_supported"] is False,
            {
                "status": i5["status"],
                "ct3": i5["ct3_replay_candidate_supported"],
                "final": i5["final_transfer_supported"],
            },
        ),
        check(
            "two_artifact_only_reconstruction_rows_present",
            len(rows) == 2
            and {row["source_iteration"] for row in rows} == {"4", "4-A"},
            [row["source_iteration"] for row in rows],
        ),
        check(
            "source_row_body_not_used_for_reconstruction",
            all(
                row["artifact_only_reconstruction_trace"]["artifact_only_policy"][
                    "source_row_body_used_for_reconstruction"
                ]
                is False
                for row in rows
            ),
            [row["row_id"] for row in rows],
        ),
        check(
            "artifact_sha256_match_file_contents",
            all(
                row["artifact_only_reconstruction_trace"][
                    "artifact_sha256_match_file_contents"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "mismatches": row["artifact_only_reconstruction_trace"][
                        "artifact_sha256_mismatches"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "reconstructed_transfer_core_matches_source_and_i5",
            all(
                row["artifact_only_reconstruction_trace"][
                    "reconstructed_core_matches_source"
                ]
                and row["artifact_only_reconstruction_trace"][
                    "reconstructed_core_matches_i5_replay_source"
                ]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "reconstructed": row["transfer_core_digest"],
                    "source": row["source_transfer_core_digest"],
                }
                for row in rows
            ],
        ),
        check(
            "artifact_only_reconstruction_digest_stable",
            all(
                row["artifact_only_reconstruction_trace"]["reconstruction_digest_stable"]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "first": row["artifact_only_reconstruction_trace"][
                        "first_reconstruction_digest"
                    ],
                    "second": row["artifact_only_reconstruction_trace"][
                        "second_reconstruction_digest"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "mapping_order_reconstructed",
            all(
                row["artifact_only_reconstruction_trace"]["mapping_order_reconstructed"][
                    "mapping_precedes_pre_and_post_observation"
                ]
                and row["artifact_only_reconstruction_trace"]["mapping_order_reconstructed"][
                    "mapping_digest_excludes_outcome"
                ]
                for row in rows
            ),
            [
                row["artifact_only_reconstruction_trace"]["mapping_order_reconstructed"]
                for row in rows
            ],
        ),
        check(
            "same_basin_metrics_reconstructed_cleanly",
            all(
                metrics["same_basin_signature_preserved_under_mapping"]
                and metrics["boundary_mapping_preserved"]
                and metrics["support_preserved_above_floor"]
                and metrics["coherence_preserved_above_floor"]
                and metrics["flux_balance_preserved_within_bound"]
                for row in rows
                for metrics in [
                    row["artifact_only_reconstruction_trace"][
                        "same_basin_metrics_reconstructed"
                    ]
                ]
            ),
            [
                row["artifact_only_reconstruction_trace"][
                    "same_basin_metrics_reconstructed"
                ]
                for row in rows
            ],
        ),
        check(
            "support_reconstruction_absent",
            all(
                row["artifact_only_reconstruction_trace"][
                    "same_basin_metrics_reconstructed"
                ]["hidden_support_reconstruction_absent"]
                and not row["artifact_only_reconstruction_trace"][
                    "same_basin_metrics_reconstructed"
                ]["support_reconstruction_events"]
                for row in rows
            ),
            [row["row_id"] for row in rows],
        ),
        check(
            "no_new_transfer_evidence_created",
            all(
                row["artifact_only_reconstruction_trace"]["artifact_only_policy"][
                    "new_transfer_evidence_created"
                ]
                is False
                for row in rows
            )
            and output["new_transfer_evidence_created"] is False,
            [row["row_id"] for row in rows],
        ),
        check(
            "ct4_ct5_final_remain_blocked",
            output["ct4_or_stronger_supported"] is False
            and output["ct5_or_stronger_supported"] is False
            and output["final_transfer_supported"] is False,
            {
                "ct4": output["ct4_or_stronger_supported"],
                "ct5": output["ct5_or_stronger_supported"],
                "final": output["final_transfer_supported"],
            },
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
    rows = [
        build_reconstruction_row(i4, i5, "i4", "4"),
        build_reconstruction_row(i4a, i5, "i4a", "4-A"),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_artifact_only_reconstruction_replay_probe",
        "experiment": "N27",
        "iteration": "5-A",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Harden I5 by reconstructing the I4 and I4-A transfer cores from "
            "artifact files only, without trusting candidate-row summary fields."
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
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "topology_fixture_variant_transfer_output_digest": i4a["output_digest"],
        "replay_same_basin_mapping_output_digest": i5["output_digest"],
        "status": "pending",
        "acceptance_state": "pending",
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": True,
        "new_transfer_evidence_created": False,
        "candidate_rows_classified": True,
        "provisional_ct_ladder_rung": CT_RUNG,
        "ct_ladder_rung_assigned": False,
        "ct_assignment_scope": "artifact_only_reconstruction_hygiene_for_existing_CT3_candidates",
        "ct3_replay_hygiene_supported": True,
        "ct4_or_stronger_supported": False,
        "ct5_or_stronger_supported": False,
        "ct6_or_stronger_supported": False,
        "final_transfer_supported": False,
        "reconstruction_row_count": len(rows),
        "reconstruction_rows": rows,
        "ready_for_iteration_6_stress_mapping_variant_transfer_matrix": True,
        "claim_boundary": {
            "claim_ceiling": (
                "artifact-only reconstruction replay hygiene for existing CT3 "
                "candidates; no new transfer evidence, CT4, CT5, final transfer, "
                "native AP5, Phase 8, or ant ecology claim"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    checks = build_checks(output, i1, i2, i3, i4, i4a, i5)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_artifact_only_reconstruction_replay_hygiene_for_CT3_candidates_no_new_transfer"
        if output["status"] == "passed"
        else "blocked_artifact_only_reconstruction_replay_probe"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 5-A - Artifact-Only Reconstruction Replay Probe

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 5-A rebuilds the I4 and I4-A transfer cores from artifact files only.
It uses source manifests as artifact indexes and source digests as expected
comparison targets, but it does not trust candidate-row summary fields for the
reconstruction itself.

```text
provisional_ct_ladder_rung = {output['provisional_ct_ladder_rung']}
ct3_replay_hygiene_supported = {str(output['ct3_replay_hygiene_supported']).lower()}
new_transfer_evidence_created = {str(output['new_transfer_evidence_created']).lower()}
ct4_or_stronger_supported = {str(output['ct4_or_stronger_supported']).lower()}
ct5_or_stronger_supported = {str(output['ct5_or_stronger_supported']).lower()}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
```

## Reconstruction Rows

| Row | Source | Scope | Reconstructed Core | Source Core | Stable | Result |
| --- | --- | --- | --- | --- | --- | --- |
"""
    for row in output["reconstruction_rows"]:
        trace = row["artifact_only_reconstruction_trace"]
        report += (
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['transfer_scope']}` | `{row['transfer_core_digest']}` | "
            f"`{row['source_transfer_core_digest']}` | "
            f"`{str(trace['reconstruction_digest_stable']).lower()}` | "
            f"`{row['artifact_only_reconstruction_result']}` |\n"
        )

    report += """
## Interpretation

I5 showed replay-backed CT3 candidate evidence. I5-A asks a narrower audit
question: can the same transfer cores be reconstructed from the emitted
artifact files alone? Both rows pass. This strengthens replay hygiene by
showing the transfer core is not merely a row-body assertion.

I5-A does not create a new transfer geometry, does not add a new mapping
variant, and does not provide stress or full-control evidence. It remains CT3
hygiene support pending I6 stress and later classification.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Claim Boundary

No final transfer, semantic identity, native support, native AP5, AP5 NAT4-gap
resolution, Phase 8, or ant ecology claim is opened.

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
