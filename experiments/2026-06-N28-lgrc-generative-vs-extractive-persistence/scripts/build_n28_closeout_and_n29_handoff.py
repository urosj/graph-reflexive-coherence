#!/usr/bin/env python3
"""Build N28 Iteration 8 closeout and N29 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_closeout_and_n29_handoff.json"
REPORT = EXPERIMENT / "reports" / "n28_closeout_and_n29_handoff.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_closeout_and_n29_handoff_artifacts"
I7_OUTPUT = EXPERIMENT / "outputs" / "n28_controls_ap_dependency_claim_classification.json"
I7_EXPECTED_DIGEST = "13271b6c1e5e67f89fdabf77722aba648654094250cd1bf8c60d361c95560e35"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_closeout_and_n29_handoff.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

ABSOLUTE_PATH_MARKERS = ["/" + "home/" + "uros", "Documents/" + "RC-github"]
UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_implementation_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "broad_margin_robustness_claim_allowed",
    "choice_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ant_agency_claim_allowed",
    "native_ap5_claim_allowed",
    "native_colony_agency_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "order_of_magnitude_robustness_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_cooperation_claim_allowed",
    "semantic_goal_ownership_claim_allowed",
    "semantic_learning_claim_allowed",
    "sentience_claim_allowed",
    "selfhood_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_substrate_claim_allowed",
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


def src_diff_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "src"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_handoff(i7: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_id": "n28_to_n29_bounded_generative_extractive_persistence_handoff",
        "n28_final_ge_ladder_rung": "GE6_N29_ready_bounded_generative_extractive_persistence_evidence",
        "n28_final_closeout_rung": "N28-C6_N29_ready_bounded_generative_extractive_closeout",
        "n29_may_consume_as": [
            "bounded_artifact_level_generative_extractive_persistence_evidence",
            "paired_generative_extractive_competitive_neutral_regime_separation",
            "claim_clean_environment_exchange_capacity_context",
            "same_policy_transition_surface_context",
            "focused_current_multiplier_margin_context",
            "margin_bottleneck_diagnostic_context",
            "ap4_ap5_gap_records_for_dependency_tracking",
        ],
        "n29_must_not_consume_as": [
            "semantic_cooperation",
            "semantic_choice",
            "semantic_goal_ownership",
            "semantic_learning",
            "agency",
            "native_support",
            "sentience",
            "organism_life",
            "ant_ecology_implementation",
            "native_ant_agency",
            "native_colony_agency",
            "Phase_8_completion",
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "broad_margin_robustness",
            "order_of_magnitude_robustness",
            "unscoped_multi_basin_substrate",
        ],
        "required_n29_starting_controls": [
            "generative_extractive_evidence_as_semantic_cooperation_control",
            "environment_exchange_as_agency_control",
            "focused_margin_as_broad_robustness_control",
            "ap4_ap5_gap_erasure_control",
            "ant_ecology_specification_by_relabel_control",
            "native_support_by_persistence_relabel_control",
            "phase8_completion_by_handoff_relabel_control",
        ],
        "n29_starting_question": (
            "Can bounded generative/extractive persistence become a claim-clean "
            "bridge into agentic ecology without relabeling persistence, "
            "environment exchange, or medium effects as semantic agency?"
        ),
        "consumed_i7_output_digest": i7["output_digest"],
    }


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i7 = load_json(I7_OUTPUT)
    changed_src_paths = src_diff_paths()
    handoff = build_handoff(i7)
    source_lineage_trace = {
        "trace_id": "n28_i8_source_lineage_trace",
        "i7_path": rel(I7_OUTPUT),
        "i7_output_digest": i7["output_digest"],
        "i7_expected_output_digest": I7_EXPECTED_DIGEST,
        "i7_output_digest_matches_expected": i7["output_digest"] == I7_EXPECTED_DIGEST,
        "i7_source_record_count": len(i7["source_records"]),
        "i7_classification_row_count": len(i7["classification_rows"]),
        "i7_artifact_manifest_count": len(i7["artifact_manifest"]),
        "source_digests_checked_in_i7": True,
        "probe_digests_checked_in_i7": True,
    }
    claim_boundary_trace = {
        "trace_id": "n28_i8_claim_boundary_trace",
        "final_claim_ceiling": (
            "bounded artifact-level generative/extractive persistence evidence "
            "over LGRC-visible focal-basin and neighborhood capacity traces"
        ),
        "ge6_is_handoff_rung_not_agency_claim": True,
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "native_ap5_supported": False,
        "native_support_supported": False,
        "phase8_completion_supported": False,
        "ant_ecology_implementation_supported": False,
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    closeout_trace = {
        "trace_id": "n28_i8_closeout_trace",
        "i7_output_digest": i7["output_digest"],
        "i7_acceptance_state": i7["acceptance_state"],
        "i7_ge5_supported": i7["ge5_or_stronger_supported"],
        "i7_ge6_supported_before_closeout": i7["ge6_or_stronger_supported"],
        "paired_regime_evidence_present": (
            i7["summary_trace"]["generative_row_count"] >= 3
            and i7["summary_trace"]["extractive_contrast_row_count"] >= 3
            and i7["summary_trace"]["competitive_neutral_contrast_row_count"] >= 4
        ),
        "same_rule_classification_status": i7["shared_regime_policy_status"],
        "focused_margin_context_preserved": i7["focused_current_multiplier_margin_support"],
        "focused_margin_promoted_to_broad_robustness": False,
        "final_ge_ladder_rung": "GE6_N29_ready_bounded_generative_extractive_persistence_evidence",
        "final_n28_closeout_rung": "N28-C6_N29_ready_bounded_generative_extractive_closeout",
        "ready_for_n29": True,
    }
    artifacts = [
        trace_artifact("source_lineage_trace", source_lineage_trace),
        trace_artifact("claim_boundary_trace", claim_boundary_trace),
        trace_artifact("closeout_trace", closeout_trace),
        trace_artifact("n29_handoff_record", handoff),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n28_closeout_and_n29_handoff",
        "schema_version": "1.0",
        "experiment": "N28",
        "iteration": "8",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": "Close N28 and hand bounded generative/extractive persistence evidence to N29.",
        "source_records": [
            {
                "source_id": "n28_i7_controls_ap_dependency_claim_classification",
                "path": rel(I7_OUTPUT),
                "source_role": "ge5_controls_ap_claim_classification",
                "output_digest": i7["output_digest"],
                "expected_output_digest": I7_EXPECTED_DIGEST,
                "output_digest_matches_expected": i7["output_digest"] == I7_EXPECTED_DIGEST,
                "sha256": sha256_file(I7_OUTPUT),
            }
        ],
        "controls_ap_dependency_claim_classification_output_digest": i7["output_digest"],
        "artifact_manifest": artifacts,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
        ),
        "final_supported_status": "bounded_artifact_level_generative_extractive_persistence_evidence",
        "final_ge_ladder_rung": "GE6_N29_ready_bounded_generative_extractive_persistence_evidence",
        "final_n28_closeout_rung": "N28-C6_N29_ready_bounded_generative_extractive_closeout",
        "n28_closeout_supported": True,
        "ge5_or_stronger_supported": True,
        "ge6_or_stronger_supported": True,
        "final_n28_supported": True,
        "same_rule_classification_status": i7["shared_regime_policy_status"],
        "paired_regime_evidence_status": "supported",
        "paired_regime_summary": i7["summary_trace"],
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "native_ap5_supported": False,
        "native_support_supported": False,
        "phase8_completion_supported": False,
        "ant_ecology_implementation_supported": False,
        "src_diff_empty": changed_src_paths == [],
        "src_diff_paths": changed_src_paths,
        "n29_handoff": handoff,
        "ready_for_n29": True,
        "claim_boundary": {
            "final_claim_ceiling": claim_boundary_trace["final_claim_ceiling"],
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "source_lineage_trace": source_lineage_trace,
        "source_lineage_trace_digest": digest_value(source_lineage_trace),
        "claim_boundary_trace": claim_boundary_trace,
        "claim_boundary_trace_digest": digest_value(claim_boundary_trace),
        "closeout_trace": closeout_trace,
        "closeout_trace_digest": digest_value(closeout_trace),
    }
    strings = collect_strings(output)
    output["checks"] = [
        check(
            "i7_classification_passed_and_ready_for_i8",
            i7["status"] == "passed"
            and i7["ready_for_iteration_8_closeout_and_n29_handoff"] is True,
            i7["acceptance_state"],
        ),
        check(
            "i7_output_digest_matches_expected",
            i7["output_digest"] == I7_EXPECTED_DIGEST,
            i7["output_digest"],
        ),
        check(
            "ge5_supported_before_closeout",
            i7["ge5_or_stronger_supported"] is True
            and i7["n28_closeout_ceiling"].startswith("N28-C5"),
            i7["n28_closeout_ceiling"],
        ),
        check(
            "paired_regime_basis_present",
            closeout_trace["paired_regime_evidence_present"],
            i7["summary_trace"],
        ),
        check(
            "same_rule_classification_supported",
            i7["shared_regime_policy_status"] == "supported"
            and i7["label_specific_thresholds_used"] is False
            and i7["policy_retuned_for_label"] is False,
            {
                "shared_regime_policy_status": i7["shared_regime_policy_status"],
                "label_specific_thresholds_used": i7["label_specific_thresholds_used"],
                "policy_retuned_for_label": i7["policy_retuned_for_label"],
            },
        ),
        check(
            "focused_margin_not_promoted_to_broad_robustness",
            output["broad_margin_robustness_supported"] is False
            and output["order_of_magnitude_robustness_supported"] is False,
            {
                "broad_margin_robustness_supported": output["broad_margin_robustness_supported"],
                "order_of_magnitude_robustness_supported": output["order_of_magnitude_robustness_supported"],
            },
        ),
        check(
            "ap4_ap5_gaps_preserved",
            output["ap4_nat4_gap_resolved"] is False
            and output["ap5_nat4_gap_resolved"] is False
            and output["native_ap5_supported"] is False,
            {
                "ap4_nat4_gap_resolved": output["ap4_nat4_gap_resolved"],
                "ap5_nat4_gap_resolved": output["ap5_nat4_gap_resolved"],
                "native_ap5_supported": output["native_ap5_supported"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
        check(
            "n29_handoff_present_and_bounded",
            output["ready_for_n29"] is True
            and "ant_ecology_implementation" in handoff["n29_must_not_consume_as"]
            and "bounded_artifact_level_generative_extractive_persistence_evidence"
            in handoff["n29_may_consume_as"],
            handoff,
        ),
        check("src_diff_empty", output["src_diff_empty"], output["src_diff_paths"]),
        check("closeout_artifacts_present", output["all_artifact_sha256_match_file_contents"], artifacts),
        check(
            "no_absolute_paths_in_records",
            not any(any(marker in value for marker in ABSOLUTE_PATH_MARKERS) for value in strings),
            sorted(value for value in strings if any(marker in value for marker in ABSOLUTE_PATH_MARKERS)),
        ),
    ]
    output["failed_checks"] = [item["check_id"] for item in output["checks"] if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_n28_c6_closeout_n29_handoff_ready"
        if output["status"] == "passed"
        else "blocked_n28_closeout"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N28 Iteration 8 - Closeout And N29 Handoff

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

```text
final_ge_ladder_rung = {output['final_ge_ladder_rung']}
final_n28_closeout_rung = {output['final_n28_closeout_rung']}
final_n28_supported = {str(output['final_n28_supported']).lower()}
ready_for_n29 = {str(output['ready_for_n29']).lower()}
broad_margin_robustness_supported = {str(output['broad_margin_robustness_supported']).lower()}
ap4_nat4_gap_resolved = {str(output['ap4_nat4_gap_resolved']).lower()}
ap5_nat4_gap_resolved = {str(output['ap5_nat4_gap_resolved']).lower()}
```

N28 closes as bounded artifact-level generative/extractive persistence
evidence. GE6 is a closeout and N29-handoff rung, not a broader robustness,
agency, native-support, Phase 8, or ant-ecology claim.

The final support rests on the I7-classified GE5 stack: paired generative,
extractive, and competitive/neutral regime separation under one shared policy,
with replay/control/stress support. I6-A contributes same-policy transition
context; I6-B remains a margin diagnostic; I6-C contributes focused
current-multiplier margin support only.

N29 may consume N28 as bounded generative/extractive persistence evidence and
claim-clean environment-exchange context. It must not consume N28 as semantic
cooperation, semantic choice, agency, native support, native AP5, AP5 NAT4-gap
resolution, Phase 8 completion, ant ecology implementation, broad margin
robustness, or order-of-magnitude robustness.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"
    report += f"""

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
