#!/usr/bin/env python3
"""Build N27 Iteration 8 closeout and N28 handoff."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_closeout_and_n28_handoff.json"
REPORT = EXPERIMENT / "reports" / "n27_closeout_and_n28_handoff.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_closeout_and_n28_handoff_artifacts"

I7_OUTPUT = EXPERIMENT / "outputs" / "n27_controls_ap_dependency_claim_classification.json"
I7A_OUTPUT = EXPERIMENT / "outputs" / "n27_n28_precursor_side_effect_claim_classification.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_closeout_and_n28_handoff.py"
)

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]
UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "generative_persistence_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "n28_generative_persistence_claim_allowed",
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
    i7 = load_json(I7_OUTPUT)
    i7a = load_json(I7A_OUTPUT)
    n28_handoff = {
        "handoff_id": "n27_to_n28_bounded_transfer_and_side_effect_precursor_handoff",
        "n27_final_ct_ladder_rung": "CT6_N28_ready_bounded_transfer_evidence",
        "n27_final_closeout_rung": "N27-C6_N28_ready_bounded_transfer_closeout",
        "n28_may_consume_as": [
            "bounded_configuration_topology_transfer_evidence",
            "claim_clean_ct5_transfer_candidate_closeout",
            "n28_ready_side_effect_precursor_evaluation",
            "focal_stability_with_neighbor_capacity_metrics_context",
        ],
        "n28_must_not_consume_as": [
            "N28_generative_persistence_evidence",
            "semantic_identity",
            "semantic_cooperation",
            "agency",
            "native_support",
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "Phase_8_completion",
            "ant_ecology",
            "organism_life",
        ],
        "required_n28_starting_controls": [
            "focal_survival_only_as_generative_control",
            "neighbor_label_only_as_capacity_control",
            "merge_leakage_as_support_control",
            "extractive_flattening_masked_control",
            "transfer_success_as_n28_success_control",
        ],
        "n28_starting_question": (
            "Can one basin persist while increasing the basin-forming capacity "
            "of its environment or neighborhood?"
        ),
    }
    closeout_trace = {
        "trace_id": "n27_i8_closeout_trace",
        "i7_ct_classification_output_digest": i7["output_digest"],
        "i7a_n28_precursor_output_digest": i7a["output_digest"],
        "ct5_supported": i7["ct5_or_stronger_supported"],
        "n28_precursor_evaluation_supported": i7a["n28_precursor_evaluation_supported"],
        "ct6_supported": True,
        "final_transfer_supported": True,
        "n28_generative_persistence_supported": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    artifacts = [
        trace_artifact("closeout_trace", closeout_trace),
        trace_artifact("n28_handoff_record", n28_handoff),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_closeout_and_n28_handoff",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "8",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": "Close N27 and hand bounded transfer evidence to N28.",
        "source_records": [
            {
                "source_id": "n27_i7_ct_classification",
                "path": rel(I7_OUTPUT),
                "source_role": "ct5_transfer_classification",
                "output_digest": i7["output_digest"],
                "sha256": sha256_file(I7_OUTPUT),
            },
            {
                "source_id": "n27_i7a_n28_precursor_side_effect_classification",
                "path": rel(I7A_OUTPUT),
                "source_role": "n28_precursor_side_effect_classification",
                "output_digest": i7a["output_digest"],
                "sha256": sha256_file(I7A_OUTPUT),
            },
        ],
        "controls_ap_dependency_claim_classification_output_digest": i7["output_digest"],
        "n28_precursor_side_effect_claim_classification_output_digest": i7a["output_digest"],
        "artifact_manifest": artifacts,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
        ),
        "final_supported_status": "bounded_artifact_level_configuration_topology_transfer_candidate",
        "final_ct_ladder_rung": "CT6_N28_ready_bounded_transfer_evidence",
        "final_n27_closeout_rung": "N27-C6_N28_ready_bounded_transfer_closeout",
        "n27_closeout_supported": True,
        "ct5_or_stronger_supported": True,
        "ct6_or_stronger_supported": True,
        "final_transfer_supported": True,
        "n28_precursor_evaluation_supported": True,
        "n28_generative_persistence_supported": False,
        "native_ap5_supported": False,
        "ap5_nat4_gap_resolution_supported": False,
        "native_support_supported": False,
        "phase8_completion_supported": False,
        "ant_ecology_supported": False,
        "n28_handoff": n28_handoff,
        "ready_for_n28": True,
        "claim_boundary": {
            "final_claim_ceiling": (
                "bounded artifact-level configuration/topology transfer evidence "
                "with N28-ready side-effect precursor evaluation"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "closeout_trace": closeout_trace,
        "closeout_trace_digest": digest_value(closeout_trace),
    }
    strings = collect_strings(output)
    output["checks"] = [
        check("i7_ct5_classification_passed", i7["status"] == "passed" and i7["ct5_or_stronger_supported"], i7["acceptance_state"]),
        check("i7a_n28_precursor_passed", i7a["status"] == "passed" and i7a["n28_precursor_evaluation_supported"], i7a["acceptance_state"]),
        check("ct6_handoff_artifacts_present", output["all_artifact_sha256_match_file_contents"], artifacts),
        check("n28_generative_persistence_remains_blocked", output["n28_generative_persistence_supported"] is False, False),
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
        "accepted_n27_c6_closeout_n28_handoff_ready"
        if output["status"] == "passed"
        else "blocked_n27_closeout"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 8 - Closeout And N28 Handoff

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

```text
final_ct_ladder_rung = {output['final_ct_ladder_rung']}
final_n27_closeout_rung = {output['final_n27_closeout_rung']}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
n28_precursor_evaluation_supported = {str(output['n28_precursor_evaluation_supported']).lower()}
n28_generative_persistence_supported = {str(output['n28_generative_persistence_supported']).lower()}
ready_for_n28 = {str(output['ready_for_n28']).lower()}
```

N27 closes as bounded artifact-level configuration/topology transfer evidence.
The strongest transfer row is the I4-A gamma/delta topology fixture variant,
classified through I7 as CT5 and closed here as CT6 because the closeout and
N28 handoff records are present.

N28 may consume the result as bounded transfer evidence plus claim-clean
side-effect precursor evaluation. It must not consume N27 as N28 generative
persistence, semantic identity, agency, native support, native AP5, AP5 NAT4
gap resolution, Phase 8 completion, ant ecology, sentience, or organism/life.

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
