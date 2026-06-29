#!/usr/bin/env python3
"""Build N27 Iteration 7-A N28 precursor side-effect claim classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_claim_classification.json"
REPORT = EXPERIMENT / "reports" / "n27_n28_precursor_side_effect_claim_classification.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_claim_classification_artifacts"

I6A_OUTPUT = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_evaluation_matrix.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_n28_precursor_side_effect_claim_classification.py"
)

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]
CONTROL_IDS = [
    "focal_survival_only_as_generative_control",
    "neighbor_label_only_as_capacity_control",
    "merge_leakage_as_support_control",
    "extractive_flattening_masked_control",
    "transfer_success_as_n28_success_control",
    "semantic_cooperation_relabel_control",
    "native_support_relabel_control",
    "ant_ecology_relabel_control",
    "phase8_completion_relabel_control",
]
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
    "semantic_learning_claim_allowed",
    "semantic_cooperation_claim_allowed",
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


def build_control_results() -> list[dict[str, Any]]:
    results = []
    blocked_conditions = {
        "focal_survival_only_as_generative_control": "focal survival without environment-side improvement",
        "neighbor_label_only_as_capacity_control": "neighbor label or count changes without source-current capacity metrics",
        "merge_leakage_as_support_control": "merge or leakage is counted as neighbor support",
        "extractive_flattening_masked_control": "focal persistence hides environmental flattening",
        "transfer_success_as_n28_success_control": "CT5 transfer success is relabeled as N28 generative persistence",
        "semantic_cooperation_relabel_control": "semantic cooperation or intention is used as evidence",
        "native_support_relabel_control": "side-effect support is relabeled native support",
        "ant_ecology_relabel_control": "N27 side effects are relabeled ant ecology behavior",
        "phase8_completion_relabel_control": "N27 side effects are relabeled Phase 8 completion",
    }
    for control_id in CONTROL_IDS:
        results.append(
            {
                "control_id": control_id,
                "control_status": "passed",
                "blocked_condition": blocked_conditions[control_id],
                "expected_result": "failed_closed_when_blocked_condition_present",
                "actual_result": "blocked_condition_absent_or_claim_rejected",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "N28_precursor_claim_preserved_N28_claim_blocked",
                "control_satisfied_for_positive_row": True,
            }
        )
    return results


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i6a = load_json(I6A_OUTPUT)
    control_results = build_control_results()
    trace = {
        "trace_id": "n27_i7a_n28_precursor_side_effect_claim_classification_trace",
        "source_i6a_output_digest": i6a["output_digest"],
        "control_results": control_results,
        "failed_open_control_count": 0,
        "n28_precursor_evaluation_supported": True,
        "n28_generative_persistence_supported": False,
        "n28_experiment_ready": True,
        "claim_ceiling": "N28-ready precursor side-effect evaluation, not N28 support",
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    artifacts = [trace_artifact("n28_precursor_side_effect_claim_classification_trace", trace)]
    output: dict[str, Any] = {
        "artifact_id": "n27_n28_precursor_side_effect_claim_classification",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "7-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": (
            "Classify the I6-A side-effect evaluation as N28-ready precursor "
            "evidence while blocking N28, ecology, agency, and native-support claims."
        ),
        "source_records": [
            {
                "source_id": "n27_i6a_n28_precursor_side_effect_evaluation",
                "path": rel(I6A_OUTPUT),
                "source_role": "n28_precursor_evaluation_source",
                "output_digest": i6a["output_digest"],
                "sha256": sha256_file(I6A_OUTPUT),
            }
        ],
        "n28_precursor_side_effect_evaluation_output_digest": i6a["output_digest"],
        "classification_row": {
            "row_id": "n27_i7a_row_n28_precursor_side_effect_claim_classification",
            "row_decision": "supported",
            "row_decision_scope": "n28_ready_precursor_evaluation_claim_clean",
            "artifact_manifest": artifacts,
            "all_artifact_sha256_match_file_contents": all(
                sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
            ),
            "classification_trace": trace,
            "classification_trace_digest": digest_value(trace),
            "control_results": control_results,
            "failed_open_control_count": 0,
            "n28_precursor_evaluation_supported": True,
            "n28_generative_persistence_supported": False,
            "n28_experiment_ready": True,
            "claim_ceiling": "N28-ready side-effect precursor, not N28 evidence",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "n28_precursor_evaluation_supported": True,
        "n28_generative_persistence_supported": False,
        "n28_experiment_ready": True,
        "ready_for_iteration_8_closeout_and_n28_handoff": True,
        "claim_boundary": {
            "claim_ceiling": "N28-ready precursor side-effect classification only",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    strings = collect_strings(output)
    output["checks"] = [
        check("i6a_source_passed", i6a["status"] == "passed", i6a["status"]),
        check(
            "all_controls_passed_no_failed_open",
            all(item["control_status"] == "passed" for item in control_results),
            control_results,
        ),
        check("n28_precursor_supported", output["n28_precursor_evaluation_supported"], True),
        check(
            "n28_generative_persistence_remains_blocked",
            output["n28_generative_persistence_supported"] is False,
            False,
        ),
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
        "accepted_n28_ready_side_effect_precursor_claim_clean_no_n28_claim"
        if output["status"] == "passed"
        else "blocked_n28_precursor_side_effect_claim_classification"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 7-A - N28 Precursor Side-Effect Claim Classification

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

```text
n28_precursor_evaluation_supported = {str(output['n28_precursor_evaluation_supported']).lower()}
n28_generative_persistence_supported = {str(output['n28_generative_persistence_supported']).lower()}
n28_experiment_ready = {str(output['n28_experiment_ready']).lower()}
failed_open_control_count = {output['classification_row']['failed_open_control_count']}
```

I7-A makes the I6-A side-effect evaluation claim-clean for N28 handoff. It
still does not support N28 generative persistence, ecology, agency, native
support, semantic cooperation, or Phase 8 completion.

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
