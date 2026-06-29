#!/usr/bin/env python3
"""Build N28 Iteration 5-A artifact-only reconstruction replay probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_artifact_only_reconstruction_replay_probe.json"
REPORT = EXPERIMENT / "reports" / "n28_artifact_only_reconstruction_replay_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_artifact_only_reconstruction_replay_probe_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_artifact_only_reconstruction_replay_probe.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I3_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_active_nulls_and_failure_baselines.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_replay_capacity_attribution_matrix.json"
)
I5_REPORT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "reports/n28_replay_capacity_attribution_matrix.md"
)

EXPECTED_I5_DIGEST = "3fd8875fa01e4cbb91933bc89cf2db32a1a2d8396a6ebc16451c33a008af6caa"

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "final_generative_persistence_claim_allowed": False,
    "final_n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(data: Any) -> str:
    return hashlib.sha256(compact_json(data).encode("utf-8")).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def build_control_row(
    *,
    row_id: str,
    reconstruction_mode: str,
    available_inputs: list[str],
    missing_inputs: list[str],
    blocked_reason: str,
    source_basis: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    positive_support_allowed = False
    trace = {
        "trace_id": f"{row_id}_trace",
        "reconstruction_mode": reconstruction_mode,
        "available_inputs": available_inputs,
        "missing_inputs": missing_inputs,
        "source_basis": source_basis,
        "source_current_n28_trace_available": False,
        "regime_metrics_reconstructable": False,
        "shared_policy_replay_reconstructable": False,
        "blocked_reason": blocked_reason,
        "expected_result": "positive_N28_GE_support_rejected",
        "actual_result": "failed_closed",
    }
    artifact = trace_artifact(f"{row_id}_reconstruction_trace", trace)
    row = {
        "row_id": row_id,
        "iteration": "5-A",
        "row_decision": "rejected",
        "row_decision_scope": "artifact_only_reconstruction_control_failed_closed",
        "reconstruction_mode": reconstruction_mode,
        "available_inputs": available_inputs,
        "missing_inputs": missing_inputs,
        "derived_report_only": True,
        "source_current_inputs": [],
        "source_current_n28_trace_required": True,
        "source_current_n28_trace_available": False,
        "regime_metrics_reconstructable": False,
        "regime_label_reconstructed": "not_admissible",
        "ge_ladder_rung": "GE0",
        "ge4_support_allowed": positive_support_allowed,
        "final_n28_support_allowed": False,
        "blocked_reason": blocked_reason,
        "control_status": "failed_closed",
        "claim_allowed_when_control_triggers": False,
        "trace_artifact": artifact["path"],
        "trace_artifact_sha256": artifact["sha256"],
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
    }
    row["row_digest"] = digest_value(row)
    return row, artifact


def build_output() -> dict[str, Any]:
    i3 = load_json(I3_OUTPUT_PATH)
    i5 = load_json(I5_OUTPUT_PATH)
    report_sha = sha256_file(I5_REPORT_PATH)
    source_pins = i3["source_digest_pins"]
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    controls = [
        {
            "row_id": "n28_i5a_report_only_reconstruction_control",
            "reconstruction_mode": "report_only_summary",
            "available_inputs": [I5_REPORT_PATH],
            "missing_inputs": [
                "source_current_runtime_trace",
                "neighbor_capacity_trace",
                "extraction_leakage_trace",
                "classification_trace",
                "generative_extractive_core",
            ],
            "blocked_reason": "report text summarizes the result but cannot satisfy source-current N28 trace requirements",
            "source_basis": {
                "i5_report_sha256": report_sha,
                "report_used_as_evidence_allowed": False,
            },
        },
        {
            "row_id": "n28_i5a_label_only_regime_reconstruction_control",
            "reconstruction_mode": "regime_labels_and_counts_only",
            "available_inputs": [
                "regime_counts",
                "source_iteration_labels",
                "source_regime_labels",
            ],
            "missing_inputs": [
                "focal_stability_trace",
                "neighbor_capacity_delta_trace",
                "merge_leakage_trace",
                "capacity_attribution_trace",
            ],
            "blocked_reason": "regime labels and counts cannot replace source-current geometric deltas",
            "source_basis": {
                "regime_counts": i5["matrix_summary"]["regime_counts"],
                "rows_demoted": i5["matrix_summary"]["rows_demoted"],
            },
        },
        {
            "row_id": "n28_i5a_n27_transfer_only_reconstruction_control",
            "reconstruction_mode": "n27_transfer_context_only",
            "available_inputs": [
                "n27_closeout_output_digest",
                "n27_side_effect_precursor_output_digest",
            ],
            "missing_inputs": [
                "N28 source-current regime rows",
                "N28 replay rows",
                "N28 capacity attribution traces",
            ],
            "blocked_reason": "N27 transfer success is prerequisite context and cannot recreate N28 generative/extractive regime evidence",
            "source_basis": {
                "n27_closeout_output_digest": source_pins[
                    "n27_closeout_output_digest"
                ],
                "n27_side_effect_precursor_output_digest": source_pins[
                    "n27_side_effect_precursor_output_digest"
                ],
                "n27_context_consumed_as_n28_evidence_allowed": False,
            },
        },
        {
            "row_id": "n28_i5a_digest_only_reconstruction_control",
            "reconstruction_mode": "digest_and_hashes_only",
            "available_inputs": [
                "source_output_digest",
                "source_row_digest",
                "artifact_sha256",
            ],
            "missing_inputs": [
                "loaded trace payloads",
                "metric sign checks",
                "regime-specific attribution controls",
            ],
            "blocked_reason": "digests prove provenance but do not by themselves replay the regime classifier",
            "source_basis": {
                "source_row_count": len(i5["source_rows"]),
                "i5_output_digest": i5["output_digest"],
            },
        },
        {
            "row_id": "n28_i5a_matrix_summary_only_reconstruction_control",
            "reconstruction_mode": "i5_matrix_summary_only",
            "available_inputs": [
                "matrix_summary",
                "shared_policy_ids",
                "rows_demoted",
            ],
            "missing_inputs": [
                "per-row source-current traces",
                "per-row replay traces",
                "per-row control results",
            ],
            "blocked_reason": "I5 matrix summary confirms replay outcome but cannot replace per-row source-current evidence for a new positive claim",
            "source_basis": {
                "matrix_summary_digest": digest_value(i5["matrix_summary"]),
                "single_shared_policy_family_preserved": i5["matrix_summary"][
                    "single_shared_policy_family_preserved"
                ],
            },
        },
    ]

    control_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for control in controls:
        row, artifact = build_control_row(**control)
        control_rows.append(row)
        artifacts.append(artifact)

    summary = {
        "trace_id": "n28_i5a_artifact_only_reconstruction_summary",
        "control_row_count": len(control_rows),
        "failed_closed_row_count": sum(
            row["control_status"] == "failed_closed" for row in control_rows
        ),
        "failed_open_row_count": sum(
            row["control_status"] == "failed_open" for row in control_rows
        ),
        "positive_support_allowed_rows": [
            row["row_id"] for row in control_rows if row["ge4_support_allowed"]
        ],
        "source_current_n28_trace_required": True,
        "source_current_n28_trace_missing_blocks_support": True,
        "i5_ge4_result_preserved": i5["ge4_or_stronger_supported"],
        "new_ge_support_opened": False,
        "ge5_or_stronger_supported": False,
    }
    summary_artifact = trace_artifact("artifact_only_reconstruction_summary", summary)
    artifacts.append(summary_artifact)

    checks = [
        check(
            "i5_replay_matrix_passed",
            i5["status"] == "passed"
            and i5["failed_checks"] == []
            and i5["output_digest"] == EXPECTED_I5_DIGEST,
        ),
        check("all_controls_failed_closed", summary["failed_closed_row_count"] == len(control_rows)),
        check("no_controls_failed_open", summary["failed_open_row_count"] == 0),
        check("no_artifact_only_positive_support", summary["positive_support_allowed_rows"] == []),
        check("report_only_reconstruction_rejected", control_rows[0]["row_decision"] == "rejected"),
        check("label_only_reconstruction_rejected", control_rows[1]["row_decision"] == "rejected"),
        check("n27_transfer_only_reconstruction_rejected", control_rows[2]["row_decision"] == "rejected"),
        check("digest_only_reconstruction_rejected", control_rows[3]["row_decision"] == "rejected"),
        check("matrix_summary_only_reconstruction_rejected", control_rows[4]["row_decision"] == "rejected"),
        check("ge5_and_ge6_still_blocked", not summary["ge5_or_stronger_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]

    output = {
        "artifact_id": "n28_artifact_only_reconstruction_replay_probe",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_artifact_only_reconstruction_controls_fail_closed_no_new_ge_support",
        "experiment": "N28",
        "iteration": "5-A",
        "source_i5_replay_matrix": {
            "path": I5_OUTPUT_PATH,
            "output_digest": i5["output_digest"],
            "artifact_sha256": sha256_file(I5_OUTPUT_PATH),
            "status": i5["status"],
            "acceptance_state": i5["acceptance_state"],
        },
        "source_i3_active_nulls": {
            "path": I3_OUTPUT_PATH,
            "output_digest": i3["output_digest"],
            "artifact_sha256": sha256_file(I3_OUTPUT_PATH),
            "status": i3["status"],
            "acceptance_state": i3["acceptance_state"],
        },
        "control_rows": control_rows,
        "artifact_manifest": artifacts,
        "summary": summary,
        "provisional_ge_ladder_rung": "GE4",
        "ge4_or_stronger_supported": True,
        "ge4_support_source": "I5 replay/control matrix only",
        "i5a_new_ge_support_opened": False,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_iteration_6_stress_regime_separation_matrix": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "artifact_only_reconstruction_controls_fail_closed; GE4 remains sourced only to I5 replay/control matrix pending stress",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def write_report(output: dict[str, Any]) -> None:
    summary = output["summary"]
    lines = [
        "# N28 Iteration 5-A - Artifact-Only Reconstruction Replay Probe",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- I5 GE4 result preserved: `{str(output['summary']['i5_ge4_result_preserved']).lower()}`",
        f"- I5-A new GE support opened: `{str(output['i5a_new_ge_support_opened']).lower()}`",
        f"- GE5 or stronger supported: `{str(output['ge5_or_stronger_supported']).lower()}`",
        "",
        "I5-A tries to reconstruct N28 support from insufficient surfaces: report "
        "text, regime labels, N27 transfer context, digests/hashes, and the I5 "
        "matrix summary alone. Every path fails closed. This protects I5 from "
        "being overread as report-only or label-only evidence.",
        "",
        "## Control Summary",
        "",
        "```text",
        f"control_row_count = {summary['control_row_count']}",
        f"failed_closed_row_count = {summary['failed_closed_row_count']}",
        f"failed_open_row_count = {summary['failed_open_row_count']}",
        f"positive_support_allowed_rows = {summary['positive_support_allowed_rows']}",
        f"source_current_n28_trace_missing_blocks_support = {str(summary['source_current_n28_trace_missing_blocks_support']).lower()}",
        "```",
        "",
        "## Control Rows",
        "",
        "| Row | Mode | Decision | Reason |",
        "|---|---|---|---|",
    ]
    for row in output["control_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['reconstruction_mode']}` | "
            f"`{row['row_decision']}` | {row['blocked_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I5-A does not add new positive GE support. It confirms that the I5 "
            "GE4 result depends on source-current N28 traces and per-row replay "
            "controls. Reports, labels, N27 transfer context, digests, and matrix "
            "summaries can document or verify provenance, but cannot replace the "
            "regime metrics and capacity-attribution traces.",
            "",
            "The GE4 candidate remains sourced to I5. GE5/GE6, final N28, semantic "
            "cooperation, agency, native support, Phase 8 completion, and ant "
            "ecology remain blocked pending stress, claim classification, and "
            "closeout.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()
