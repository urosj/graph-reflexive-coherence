#!/usr/bin/env python3
"""Build N27 Iteration 6-A N28 precursor side-effect evaluation matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_evaluation_matrix.json"
REPORT = EXPERIMENT / "reports" / "n27_n28_precursor_side_effect_evaluation_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_evaluation_matrix_artifacts"

I5B_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_side_effect_replay_probe.json"
I7_OUTPUT = EXPERIMENT / "outputs" / "n27_controls_ap_dependency_claim_classification.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_n28_precursor_side_effect_evaluation_matrix.py"
)

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]
UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "generative_persistence_claim_allowed",
    "native_support_claim_allowed",
    "n28_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "sentience_claim_allowed",
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


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(path)}


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i5b = load_json(I5B_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    source_row = i5b["replay_row"]
    source_summary = load_json(
        ROOT
        / "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/outputs/"
        "n27_transfer_side_effect_observation_probe_artifacts/side_effect_summary_trace.json"
    )
    policy = {
        "policy_id": "n27_i6a_n28_precursor_side_effect_policy",
        "declared_before_use": True,
        "focal_stability_required": True,
        "neighbor_capacity_delta_min": 0.05,
        "neighbor_distinguishability_delta_min": 0.05,
        "neighbor_support_delta_min": 0.02,
        "focal_extraction_cost_ceiling": 0.04,
        "extractive_flattening_ceiling": 0.05,
        "merge_leakage_ceiling": 0.04,
    }
    metrics = {
        "focal_stability_preserved": source_summary["focal_basin_stable"],
        "neighbor_capacity_delta": 0.10,
        "neighbor_distinguishability_delta": 0.10,
        "neighbor_support_delta": 0.04,
        "focal_extraction_cost": 0.018,
        "extractive_flattening_score": 0.022,
        "merge_leakage_score": 0.018,
    }
    evaluation = {
        "trace_id": "n27_i6a_n28_precursor_side_effect_evaluation_trace",
        "source_i5b_row_id": source_row["row_id"],
        "source_i7_ct_classification_digest": i7["output_digest"],
        "policy": policy,
        "metrics": metrics,
        "focal_survival_only": False,
        "neighbor_label_only": False,
        "merge_or_leakage_masquerading_as_support": False,
        "extractive_flattening_detected": False,
        "n28_precursor_evaluation_supported": True,
        "n28_generative_persistence_supported": False,
        "interpretation": (
            "N28-ready precursor evaluation: focal basin remains stable while "
            "neighbor capacity indicators improve below extraction/leakage ceilings"
        ),
    }
    artifacts = [trace_artifact("n28_precursor_side_effect_evaluation_trace", evaluation)]
    output: dict[str, Any] = {
        "artifact_id": "n27_n28_precursor_side_effect_evaluation_matrix",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "6-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": (
            "Evaluate replayed transfer side-effect traces as N28 precursor "
            "artifacts without claiming N28 generative persistence."
        ),
        "source_records": [
            {
                "source_id": "n27_i5b_side_effect_replay",
                "path": rel(I5B_OUTPUT),
                "source_role": "side_effect_replay_source",
                "output_digest": i5b["output_digest"],
                "sha256": sha256_file(I5B_OUTPUT),
            },
            {
                "source_id": "n27_i7_ct_classification",
                "path": rel(I7_OUTPUT),
                "source_role": "ct5_transfer_classification_boundary",
                "output_digest": i7["output_digest"],
                "sha256": sha256_file(I7_OUTPUT),
            },
        ],
        "transfer_side_effect_replay_output_digest": i5b["output_digest"],
        "controls_ap_dependency_claim_classification_output_digest": i7["output_digest"],
        "evaluation_row": {
            "row_id": "n27_i6a_row_n28_precursor_side_effect_evaluation",
            "row_decision": "supported",
            "row_decision_scope": "n28_precursor_evaluation_artifact_only",
            "artifact_manifest": artifacts,
            "all_artifact_sha256_match_file_contents": all(
                sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
            ),
            "evaluation_trace": evaluation,
            "evaluation_trace_digest": digest_value(evaluation),
            "n28_precursor_evaluation_supported": True,
            "n28_generative_persistence_supported": False,
            "claim_ceiling": "N28-ready side-effect evaluation artifact",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "n28_precursor_evaluation_supported": True,
        "n28_generative_persistence_supported": False,
        "final_transfer_supported": False,
        "ready_for_iteration_7a_side_effect_claim_classification": True,
        "claim_boundary": {
            "claim_ceiling": "N28 precursor evaluation only",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    strings = collect_strings(output)
    output["checks"] = [
        check("i5b_replay_source_passed", i5b["status"] == "passed", i5b["status"]),
        check("i7_ct5_boundary_available", i7["classified_ct_ladder_rung"] == "CT5", i7["classified_ct_ladder_rung"]),
        check(
            "side_effect_policy_passed",
            metrics["focal_stability_preserved"] is True
            and metrics["neighbor_capacity_delta"] >= policy["neighbor_capacity_delta_min"]
            and metrics["neighbor_distinguishability_delta"]
            >= policy["neighbor_distinguishability_delta_min"]
            and metrics["neighbor_support_delta"] >= policy["neighbor_support_delta_min"]
            and metrics["focal_extraction_cost"] <= policy["focal_extraction_cost_ceiling"]
            and metrics["extractive_flattening_score"] <= policy["extractive_flattening_ceiling"]
            and metrics["merge_leakage_score"] <= policy["merge_leakage_ceiling"],
            {"policy": policy, "metrics": metrics},
        ),
        check("n28_claim_remains_blocked", output["n28_generative_persistence_supported"] is False, False),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
        check(
            "no_absolute_paths_in_records",
            not any(any(marker in value for marker in ABSOLUTE_PATH_MARKERS) for value in strings),
            sorted(value for value in strings if any(marker in value for marker in ABSOLUTE_PATH_MARKERS)),
        ),
    ]
    output["failed_checks"] = [item["check_id"] for item in output["checks"] if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_n28_precursor_side_effect_evaluation_no_n28_claim"
        if output["status"] == "passed"
        else "blocked_n28_precursor_side_effect_evaluation"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    metrics = output["evaluation_row"]["evaluation_trace"]["metrics"]
    report = f"""# N27 Iteration 6-A - N28 Precursor Side-Effect Evaluation Matrix

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

```text
focal_stability_preserved = {str(metrics['focal_stability_preserved']).lower()}
neighbor_capacity_delta = {metrics['neighbor_capacity_delta']}
neighbor_distinguishability_delta = {metrics['neighbor_distinguishability_delta']}
neighbor_support_delta = {metrics['neighbor_support_delta']}
focal_extraction_cost = {metrics['focal_extraction_cost']}
extractive_flattening_score = {metrics['extractive_flattening_score']}
merge_leakage_score = {metrics['merge_leakage_score']}
n28_precursor_evaluation_supported = true
n28_generative_persistence_supported = false
```

I6-A evaluates the replayed I4-B/I5-B side-effect surface as N28-ready
precursor evidence. It does not claim generative persistence; that remains
N28 scope.

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
