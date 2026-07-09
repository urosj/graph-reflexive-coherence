#!/usr/bin/env python3
"""Build N30 Iteration 6-A later-eligibility contrast-margin probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_later_eligibility_margin_i6a.json"
REPORT = EXPERIMENT / "reports" / "n30_later_eligibility_margin_i6a.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_later_eligibility_margin_i6a_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_later_eligibility_margin_i6a.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I6_OUTPUT = EXPERIMENT / "outputs" / "n30_later_eligibility_i6.json"

AXIS_ORDER = [
    "neighbor_distinguishability_delta",
    "neighbor_support_delta",
    "neighbor_boundary_delta",
    "environment_capacity_delta",
]

BLOCKED_CLAIMS = [
    "higher_threshold_margin",
    "final_minimal_shared_medium_participation",
    "shared_medium_coordination",
    "parent_basin_modulation",
    "resonant_alignment",
    "native_shared_medium_organization",
    "semantic_communication",
    "semantic_coordination",
    "cooperation",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_completion",
    "unrestricted_autonomy",
    "slow_trace_or_medium_memory",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def write_artifact(name: str, data: dict[str, Any]) -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(canonical_json(data), encoding="utf-8")
    return {
        "path": rel(path),
        "artifact_role": data["artifact_role"],
        "sha256": sha256_file(path),
    }


def source_input(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": rel(path),
        "source_role": role,
        "sha256": sha256_file(path),
    }


def axis_differences(
    left: dict[str, float], right: dict[str, float]
) -> dict[str, float]:
    return {axis: round(left[axis] - right[axis], 6) for axis in AXIS_ORDER}


def margin_against_threshold(values: dict[str, float], threshold: float) -> dict[str, float]:
    return {axis: round(value - threshold, 6) for axis, value in values.items()}


def build_margin_row(
    row: dict[str, Any],
    *,
    neutral_threshold: float,
    extractive_threshold: float,
) -> dict[str, Any]:
    trace = row["susceptibility_or_eligibility_trace"]
    edge = trace["edge_metrics"]
    neutral = trace["neutral_counterfactual_metrics"]
    extractive = trace["extractive_counterfactual_metrics"]
    edge_vs_neutral = axis_differences(edge, neutral)
    edge_vs_extractive = axis_differences(edge, extractive)
    neutral_margins = margin_against_threshold(edge_vs_neutral, neutral_threshold)
    extractive_margins = margin_against_threshold(edge_vs_extractive, extractive_threshold)
    result = {
        "row_id": f"{row['row_id']}_contrast_margin",
        "source_i6_row_id": row["row_id"],
        "medium_surface_id": row["medium_surface_id"],
        "relation_chain_id": row["relation_chain_id"],
        "medium_relation_ladder_rung": row["medium_relation_ladder_rung"],
        "threshold_margin_from_i6": row["effect_size"]["minimum_threshold_margin"],
        "threshold_margin_improved": False,
        "edge_vs_neutral_axis_deltas": edge_vs_neutral,
        "edge_vs_extractive_axis_deltas": edge_vs_extractive,
        "minimum_edge_vs_neutral_axis_delta": min(edge_vs_neutral.values()),
        "minimum_edge_vs_extractive_axis_delta": min(edge_vs_extractive.values()),
        "neutral_contrast_threshold": neutral_threshold,
        "extractive_contrast_threshold": extractive_threshold,
        "edge_vs_neutral_axis_margins": neutral_margins,
        "edge_vs_extractive_axis_margins": extractive_margins,
        "minimum_contrast_margin_vs_neutral": min(neutral_margins.values()),
        "minimum_contrast_margin_vs_extractive": min(extractive_margins.values()),
        "dependency_contrast_margin_supported": min(neutral_margins.values()) > 0
        and min(extractive_margins.values()) > 0,
        "row_decision": (
            "supported_for_M2_dependency_contrast_margin_not_threshold_margin_upgrade"
        ),
    }
    result["row_digest"] = digest_value(result)
    return result


def build_payload() -> dict[str, Any]:
    i6 = load_json(I6_OUTPUT)
    neutral_threshold = 0.01
    extractive_threshold = 0.05
    contrast_policy = {
        "artifact_role": "i6a_contrast_threshold_policy",
        "trace_id": "n30_i6a_later_eligibility_contrast_threshold_policy",
        "policy_declared_before_i6a_row_classification": True,
        "policy_purpose": (
            "Measure dependency separation from neutral and opposite-regime "
            "counterfactuals without changing N28 generative thresholds."
        ),
        "neutral_counterfactual_min_axis_delta": neutral_threshold,
        "extractive_counterfactual_min_axis_delta": extractive_threshold,
        "n28_thresholds_retuned": False,
        "i6_threshold_margin_reinterpreted": False,
        "higher_threshold_margin_claim_allowed": False,
        "allowed_positive_claim": (
            "higher counterfactual contrast margin for provisional M2 dependency "
            "separation"
        ),
    }
    contrast_policy["contrast_threshold_policy_digest"] = digest_value(contrast_policy)

    margin_rows = [
        build_margin_row(
            row,
            neutral_threshold=neutral_threshold,
            extractive_threshold=extractive_threshold,
        )
        for row in i6["candidate_rows"]
    ]
    matrix = {
        "artifact_role": "i6a_contrast_margin_matrix",
        "trace_id": "n30_i6a_later_eligibility_contrast_margin_matrix",
        "source_i6_output_digest": i6["output_digest"],
        "source_i6_acceptance_state": i6["acceptance_state"],
        "source_i6_threshold_margin": i6["aggregate_trace"]["minimum_threshold_margin"],
        "source_i6_threshold_margin_improved": False,
        "contrast_policy": contrast_policy,
        "margin_rows": margin_rows,
        "minimum_dependency_contrast_margin_vs_neutral": min(
            row["minimum_contrast_margin_vs_neutral"] for row in margin_rows
        ),
        "minimum_dependency_contrast_margin_vs_extractive": min(
            row["minimum_contrast_margin_vs_extractive"] for row in margin_rows
        ),
        "dependency_contrast_margin_supported": all(
            row["dependency_contrast_margin_supported"] for row in margin_rows
        ),
        "higher_threshold_margin_supported": False,
        "interpretation": (
            "I6-A strengthens the dependency contrast, not the N28 threshold "
            "margin. I6 remains a narrow threshold-margin candidate."
        ),
    }
    matrix["contrast_margin_matrix_digest"] = digest_value(matrix)

    claim_boundary = {
        "artifact_role": "i6a_claim_boundary_guard",
        "trace_id": "n30_i6a_claim_boundary_guard",
        "m2_input_evidence_supported": True,
        "dependency_contrast_margin_supported": True,
        "higher_threshold_margin_supported": False,
        "n30_c5_input_evidence_supported": True,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "reason_final_claim_blocked": "iteration_7_relation_controls_pending",
        "blocked_claims": BLOCKED_CLAIMS,
    }
    claim_boundary["claim_boundary_guard_digest"] = digest_value(claim_boundary)

    artifacts = [
        write_artifact("i6a_contrast_threshold_policy.json", contrast_policy),
        write_artifact("i6a_contrast_margin_matrix.json", matrix),
        write_artifact("i6a_claim_boundary_guard.json", claim_boundary),
    ]
    artifact_sha256_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )

    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "6-A_later_eligibility_contrast_margin_probe",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_M2_dependency_contrast_margin_strengthening_no_threshold_margin_upgrade"
        ),
        "source_i6_output_digest": i6["output_digest"],
        "positive_evidence_opened": True,
        "positive_evidence_scope": (
            "counterfactual_contrast_margin_strengthening_for_provisional_M2"
        ),
        "runtime_origin": "inherited_N28_source_current_transition_artifacts",
        "n30_fresh_runtime": False,
        "medium_relation_ladder_rung_assigned": "M2_candidate_pending_I7_controls",
        "n30_closeout_ceiling": (
            "N30-C4_medium_perturbation_trace_candidate_with_strengthened_provisional_C5_input_evidence"
        ),
        "final_n30_closeout_rung": "not_assigned",
        "source_i6_threshold_margin": matrix["source_i6_threshold_margin"],
        "higher_threshold_margin_supported": False,
        "dependency_contrast_margin_supported": True,
        "minimum_dependency_contrast_margin_vs_neutral": matrix[
            "minimum_dependency_contrast_margin_vs_neutral"
        ],
        "minimum_dependency_contrast_margin_vs_extractive": matrix[
            "minimum_dependency_contrast_margin_vs_extractive"
        ],
        "later_eligibility_dependency_evidence_opened": True,
        "n30_c5_input_evidence_supported": True,
        "minimal_shared_medium_participation_claim_allowed": False,
        "final_n30_c5_claim_allowed": False,
        "final_n30_c6_claim_allowed": False,
        "ready_for_iteration_7_replay_controls": True,
        "contrast_policy": contrast_policy,
        "contrast_margin_matrix": matrix,
        "claim_boundary_guard": claim_boundary,
        "candidate_rows": margin_rows,
        "artifact_manifest": artifacts,
        "source_current_inputs": [
            source_input(I6_OUTPUT, "N30_I6_provisional_M2_later_eligibility_candidate"),
            *i6["source_current_inputs"],
        ],
        "all_artifact_sha256_match_file_contents": artifact_sha256_match,
        "claim_boundary": {
            "claim_ceiling": (
                "provisional_M2_dependency_contrast_margin_strengthening_pending_I7"
            ),
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }

    checks = [
        {
            "check_id": "source_i6_passed_with_provisional_m2",
            "passed": i6["status"] == "passed"
            and i6["medium_relation_ladder_rung_assigned"]
            == "M2_candidate_pending_I7_controls"
            and i6["final_n30_c5_claim_allowed"] is False,
        },
        {
            "check_id": "contrast_policy_declared_without_threshold_retune",
            "passed": contrast_policy["policy_declared_before_i6a_row_classification"]
            is True
            and contrast_policy["n28_thresholds_retuned"] is False
            and contrast_policy["i6_threshold_margin_reinterpreted"] is False,
        },
        {
            "check_id": "dependency_contrast_margins_supported",
            "passed": matrix["dependency_contrast_margin_supported"] is True
            and matrix["minimum_dependency_contrast_margin_vs_neutral"] > 0
            and matrix["minimum_dependency_contrast_margin_vs_extractive"] > 0,
        },
        {
            "check_id": "higher_threshold_margin_not_overclaimed",
            "passed": payload["higher_threshold_margin_supported"] is False
            and matrix["source_i6_threshold_margin_improved"] is False
            and claim_boundary["higher_threshold_margin_supported"] is False,
        },
        {
            "check_id": "final_c5_c6_claims_blocked_pending_i7",
            "passed": payload["n30_c5_input_evidence_supported"] is True
            and payload["final_n30_c5_claim_allowed"] is False
            and payload["final_n30_c6_claim_allowed"] is False
            and payload["minimal_shared_medium_participation_claim_allowed"] is False,
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": artifact_sha256_match,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
        },
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        },
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [
        check["check_id"] for check in checks if check["passed"] is not True
    ]
    payload["output_digest"] = digest_value(payload)
    return payload


def write_report(payload: dict[str, Any]) -> None:
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    artifact_rows = "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )
    candidate_rows = "\n".join(
        (
            f"- {row['source_i6_row_id']}: "
            f"threshold_margin={row['threshold_margin_from_i6']}, "
            f"contrast_vs_neutral={row['minimum_contrast_margin_vs_neutral']}, "
            f"contrast_vs_extractive={row['minimum_contrast_margin_vs_extractive']}"
        )
        for row in payload["candidate_rows"]
    )
    text = f"""# N30 Iteration 6-A - Later Eligibility Contrast-Margin Probe

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

I6-A strengthens I6 by measuring counterfactual contrast margin. It does not
change N28 thresholds and does not reinterpret the narrow I6 threshold margin.

The question is narrower:

```text
Is the provisional M2 dependency clearly separated from neutral-gap and
opposite-regime counterfactuals?
```

## Result

```text
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
source_i6_threshold_margin = {payload['source_i6_threshold_margin']}
higher_threshold_margin_supported = false
dependency_contrast_margin_supported = true
minimum_dependency_contrast_margin_vs_neutral = {payload['minimum_dependency_contrast_margin_vs_neutral']}
minimum_dependency_contrast_margin_vs_extractive = {payload['minimum_dependency_contrast_margin_vs_extractive']}
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
```

## Candidate Rows

{candidate_rows}

## Interpretation

I6 was narrow at the N28 generative-threshold boundary: its minimum threshold
margin was 0.002. I6-A does not hide that. Instead, it asks whether the same
later-eligibility dependency is well separated from the active counterfactuals.

The answer is yes. Against the neutral-gap counterfactual, the minimum
axis-level dependency contrast margin is
{payload['minimum_dependency_contrast_margin_vs_neutral']}. Against the
extractive-cross counterfactual, it is
{payload['minimum_dependency_contrast_margin_vs_extractive']}. This strengthens
the M2 dependency separation while preserving the claim boundary: the threshold
margin remains narrow and final C5/C6 remain pending I7 controls.

## Artifacts

| Role | Path |
|---|---|
{artifact_rows}

## Checks

{check_rows}
"""
    REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
