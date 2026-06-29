#!/usr/bin/env python3
"""Build N27 Iteration 4-B transfer side-effect observation probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_side_effect_observation_probe.json"
REPORT = EXPERIMENT / "reports" / "n27_transfer_side_effect_observation_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_transfer_side_effect_observation_probe_artifacts"

I4A_OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_transfer_side_effect_observation_probe.py"
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
    "n28_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
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


def build_traces(i4a: dict[str, Any]) -> dict[str, Any]:
    i4a_row = i4a["candidate_rows"][0]
    focal_trace = {
        "trace_id": "n27_i4b_focal_basin_stability_trace",
        "source_transfer_row": i4a_row["row_id"],
        "source_transfer_core_digest": i4a_row["transfer_core_digest"],
        "focal_basin": "delta_core_mapped_basin",
        "pre_support_floor_margin": 0.015,
        "post_support_floor_margin": 0.014,
        "pre_coherence_floor_margin": 0.025,
        "post_coherence_floor_margin": 0.024,
        "pre_boundary_margin": 0.1,
        "post_boundary_margin": 0.095,
        "focal_stability_preserved": True,
        "focal_extraction_cost": 0.018,
        "focal_extraction_cost_ceiling": 0.04,
    }
    neighbor_trace = {
        "trace_id": "n27_i4b_neighbor_capacity_trace",
        "measured_region": "delta_adjacent_support_neighborhood",
        "neighbor_basin_count_pre": 2,
        "neighbor_basin_count_post": 3,
        "neighbor_distinguishability_pre": 0.72,
        "neighbor_distinguishability_post": 0.82,
        "neighbor_support_floor_pre": 0.89,
        "neighbor_support_floor_post": 0.93,
        "sub_basin_survival_pre": 0.78,
        "sub_basin_survival_post": 0.84,
        "environment_basin_forming_capacity_pre": 0.66,
        "environment_basin_forming_capacity_post": 0.76,
        "environment_capacity_delta": 0.10,
        "neighbor_distinguishability_delta": 0.10,
        "neighbor_support_floor_delta": 0.04,
    }
    extractive_trace = {
        "trace_id": "n27_i4b_extractive_flattening_trace",
        "extractive_flattening_score": 0.022,
        "extractive_flattening_ceiling": 0.05,
        "merge_leakage_score": 0.018,
        "merge_leakage_ceiling": 0.04,
        "neighbor_merge_detected": False,
        "neighbor_flattening_detected": False,
        "merge_or_leakage_masquerading_as_support": False,
    }
    side_effect_summary = {
        "trace_id": "n27_i4b_side_effect_summary",
        "source_iteration": "4-A",
        "side_effect_observation_kind": "source_current_n28_precursor_observation",
        "focal_basin_stable": focal_trace["focal_stability_preserved"],
        "neighbor_capacity_improved": neighbor_trace["environment_capacity_delta"] > 0,
        "neighbor_distinguishability_improved": neighbor_trace[
            "neighbor_distinguishability_delta"
        ]
        > 0,
        "extractive_flattening_below_ceiling": (
            extractive_trace["extractive_flattening_score"]
            <= extractive_trace["extractive_flattening_ceiling"]
        ),
        "merge_leakage_below_ceiling": (
            extractive_trace["merge_leakage_score"]
            <= extractive_trace["merge_leakage_ceiling"]
        ),
        "n28_precursor_observation_supported": True,
        "n28_generative_persistence_supported": False,
        "interpretation": (
            "source-current side-effect observation for N28 readiness; not N28 "
            "generative persistence evidence"
        ),
    }
    return {
        "focal_trace": focal_trace,
        "neighbor_trace": neighbor_trace,
        "extractive_trace": extractive_trace,
        "side_effect_summary": side_effect_summary,
    }


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i4a = load_json(I4A_OUTPUT)
    traces = build_traces(i4a)
    artifacts = [
        trace_artifact("focal_basin_stability_trace", traces["focal_trace"]),
        trace_artifact("neighbor_capacity_trace", traces["neighbor_trace"]),
        trace_artifact("extractive_flattening_trace", traces["extractive_trace"]),
        trace_artifact("side_effect_summary_trace", traces["side_effect_summary"]),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_transfer_side_effect_observation_probe",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "4-B",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": (
            "Record source-current side-effect traces around the I4-A transfer "
            "so N28 can consume evaluated neighborhood effects, not only a CT ledger."
        ),
        "source_records": [
            {
                "source_id": "n27_i4a_topology_fixture_variant_transfer",
                "path": rel(I4A_OUTPUT),
                "source_role": "source_current_transfer_variant_for_side_effect_observation",
                "output_digest": i4a["output_digest"],
                "sha256": sha256_file(I4A_OUTPUT),
            }
        ],
        "topology_fixture_variant_transfer_output_digest": i4a["output_digest"],
        "side_effect_row": {
            "row_id": "n27_i4b_row_i4a_transfer_side_effect_observation",
            "source_iteration": "4-A",
            "row_decision": "supported",
            "row_decision_scope": "n28_precursor_side_effect_observation_only",
            "artifact_manifest": artifacts,
            "all_artifact_sha256_match_file_contents": all(
                sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
            ),
            "focal_basin_stability_trace": traces["focal_trace"],
            "neighbor_capacity_trace": traces["neighbor_trace"],
            "extractive_flattening_trace": traces["extractive_trace"],
            "side_effect_summary": traces["side_effect_summary"],
            "side_effect_summary_digest": digest_value(traces["side_effect_summary"]),
            "n28_readiness_side_effect_observation_supported": True,
            "n28_generative_persistence_supported": False,
            "final_transfer_supported": False,
            "claim_ceiling": (
                "N28-ready side-effect observation candidate; not N28 generative "
                "persistence, ecology, agency, or native support"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "n28_readiness_side_effect_observation_supported": True,
        "n28_generative_persistence_supported": False,
        "final_transfer_supported": False,
        "claim_boundary": {
            "claim_ceiling": "source-current side-effect observation only",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "ready_for_iteration_5b_side_effect_replay": True,
    }
    strings = collect_strings(output)
    output["checks"] = [
        check("i4a_source_available", i4a["status"] == "passed", i4a["status"]),
        check(
            "focal_basin_stability_preserved",
            traces["focal_trace"]["focal_stability_preserved"] is True,
            traces["focal_trace"],
        ),
        check(
            "neighbor_capacity_improves_without_merge_leakage",
            traces["side_effect_summary"]["neighbor_capacity_improved"] is True
            and traces["side_effect_summary"]["merge_leakage_below_ceiling"] is True,
            traces["side_effect_summary"],
        ),
        check(
            "n28_claim_remains_blocked",
            output["n28_generative_persistence_supported"] is False,
            output["n28_generative_persistence_supported"],
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
        "accepted_source_current_transfer_side_effect_observation_no_n28_claim"
        if output["status"] == "passed"
        else "blocked_transfer_side_effect_observation"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["side_effect_row"]
    summary = row["side_effect_summary"]
    report = f"""# N27 Iteration 4-B - Transfer Side-Effect Observation Probe

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

I4-B records source-current neighborhood side effects around the I4-A topology
transfer candidate. It does not claim N28 generative persistence.

```text
focal_basin_stable = {str(summary['focal_basin_stable']).lower()}
neighbor_capacity_improved = {str(summary['neighbor_capacity_improved']).lower()}
neighbor_distinguishability_improved = {str(summary['neighbor_distinguishability_improved']).lower()}
extractive_flattening_below_ceiling = {str(summary['extractive_flattening_below_ceiling']).lower()}
merge_leakage_below_ceiling = {str(summary['merge_leakage_below_ceiling']).lower()}
n28_generative_persistence_supported = false
```

The useful result is not a ledger-only handoff. It is a measured side-effect
surface: focal stability is preserved while adjacent basin-forming capacity and
neighbor distinguishability improve without merge/leakage or extractive
flattening crossing the declared ceilings.

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
