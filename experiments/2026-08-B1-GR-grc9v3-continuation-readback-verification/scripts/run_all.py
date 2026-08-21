"""Serial B1-GR gate orchestrator. Only GRV0 is executable at P0."""

from __future__ import annotations

import argparse
from pathlib import Path

from artifact_io import EXPERIMENT_ROOT, git, sha256_file, write_json
from capture_repository_baseline import capture
from gate_receipts import finalize_receipt, validate_receipt
from serialize_theory_contract import serialize


def grv0_output_paths(output_root: Path) -> list[Path]:
    receipt_path = output_root / "gates/grv0_result_receipt.json"
    return sorted(
        path
        for path in output_root.rglob("*")
        if path.is_file() and path.name != ".gitkeep" and path != receipt_path
    )


def write_report(capture_result: dict[str, object], output_paths: list[Path]) -> Path:
    baseline = capture_result["baseline"]
    payload = baseline["payload"]  # type: ignore[index]
    report = EXPERIMENT_ROOT / "reports/b1_grv0_baseline_admission.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# B1-GR GRV0 Baseline Admission",
        "",
        "## Result",
        "",
        "```text",
        "gate = GRV0",
        "mechanical_status = passed",
        "scientific_acceptance = awaiting_human_review",
        "candidate_closeout_ceiling = GRV-C1",
        "positive_evidence_opened = false",
        "runtime_change_authorized = false",
        "```",
        "",
        "GRV0 admits only the exact specification, source identities, clean test",
        "baseline, package schemas, numerical policy, and preregistered envelope.",
        "It provides no continuation, retention, read-back, or write-back evidence.",
        "",
        "## Baseline",
        "",
        f"- Execution revision: `{payload['experiment_execution_revision']}`",
        f"- Substrate base revision: `{payload['substrate_base_revision']}`",
        f"- Theory revision: `{payload['theory_revision']}`",
        f"- Specification SHA-256: `{payload['specification_sha256']}`",
        f"- Existing tests: `{payload['test_result']}` ({payload['test_counts']['run']} run, {payload['test_counts']['skipped']} skipped)",
        f"- Test log: `{payload['test_log_path']}`",
        "",
        "## Acceptance Boundary",
        "",
        "The result receipt is mechanical provenance, not scientific acceptance.",
        "GRV1 remains blocked until an authorized human reviews the committed GRV0",
        "result revision and records a separate accepted anchor.",
        "",
        "## Emitted Artifacts",
        "",
    ]
    lines.extend(f"- `{path.relative_to(EXPERIMENT_ROOT).as_posix()}`" for path in sorted(output_paths))
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv0() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV0 requires a clean committed P0 input revision")
    output_root = EXPERIMENT_ROOT / "outputs"
    serialize(output_root)
    captured = capture(output_root, clean_input_already_verified=True)
    output_paths = grv0_output_paths(output_root)
    report = write_report(captured, output_paths)
    output_paths.append(report)
    baseline_payload = captured["baseline"]["payload"]
    receipt = finalize_receipt({
        "gate_id": "GRV0",
        "input_execution_revision": baseline_payload["experiment_execution_revision"],
        "substrate_base_revision": baseline_payload["substrate_base_revision"],
        "input_experiment_tree_sha256": baseline_payload["experiment_tree_sha256"],
        "prerequisite_result_receipt_digests": [],
        "prerequisite_acceptance_anchors": [],
        "output_artifact_digests": {path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path) for path in sorted(output_paths)},
        "status": "awaiting_scientific_review",
        "blocked_gates": [f"GRV{index}" for index in range(1, 9)],
        "claim_ceiling": "GRV-C1_candidate_pending_authorized_human_acceptance_no_scientific_evidence",
    })
    validate_receipt(receipt)
    write_json(output_root / "gates/grv0_result_receipt.json", receipt)
    print("GRV0 mechanically validated; scientific acceptance anchor is pending.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=[f"GRV{index}" for index in range(9)], required=True)
    args = parser.parse_args()
    if args.gate != "GRV0":
        anchor = EXPERIMENT_ROOT / f"outputs/gates/grv{int(args.gate[-1]) - 1}_acceptance_anchor.json"
        if not anchor.exists():
            raise SystemExit(f"{args.gate} blocked: prerequisite accepted anchor is missing")
        raise SystemExit(f"{args.gate} is not executable in the P0 package revision")
    run_grv0()


if __name__ == "__main__":
    main()
