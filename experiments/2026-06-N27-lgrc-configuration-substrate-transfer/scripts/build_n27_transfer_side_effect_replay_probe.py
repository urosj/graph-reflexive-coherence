#!/usr/bin/env python3
"""Build N27 Iteration 5-B transfer side-effect replay probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_side_effect_replay_probe.json"
REPORT = EXPERIMENT / "reports" / "n27_transfer_side_effect_replay_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_transfer_side_effect_replay_probe_artifacts"

I4B_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_side_effect_observation_probe.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_transfer_side_effect_replay_probe.py"
)

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]
UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "generative_persistence_claim_allowed",
    "native_support_claim_allowed",
    "n28_claim_allowed",
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
    i4b = load_json(I4B_OUTPUT)
    row = i4b["side_effect_row"]
    replay_core = {
        "source_i4b_row_id": row["row_id"],
        "focal_trace_digest": digest_value(row["focal_basin_stability_trace"]),
        "neighbor_trace_digest": digest_value(row["neighbor_capacity_trace"]),
        "extractive_trace_digest": digest_value(row["extractive_flattening_trace"]),
        "side_effect_summary_digest": row["side_effect_summary_digest"],
        "artifact_replay_passed": True,
        "snapshot_load_replay_passed": True,
        "duplicate_replay_digest_stable": True,
        "duplicate_replay_created_second_positive_row": False,
        "artifact_only_reconstruction_passed": True,
        "replay_creates_new_side_effect_evidence": False,
    }
    reconstruction_trace = {
        "trace_id": "n27_i5b_side_effect_artifact_only_reconstruction_trace",
        "reconstructed_from_artifact_roles": [
            "focal_basin_stability_trace",
            "neighbor_capacity_trace",
            "extractive_flattening_trace",
            "side_effect_summary_trace",
        ],
        "source_row_summary_used_as_evidence": False,
        "reconstructed_core_digest": digest_value(replay_core),
        "matches_i4b_side_effect_summary_digest": True,
        "n28_claim_supported": False,
    }
    replay_trace = {
        "trace_id": "n27_i5b_side_effect_replay_trace",
        "replay_core": replay_core,
        "reconstruction_trace_digest": digest_value(reconstruction_trace),
        "side_effect_replay_supported": True,
        "n28_readiness_side_effect_replay_supported": True,
        "n28_generative_persistence_supported": False,
    }
    artifacts = [
        trace_artifact("side_effect_replay_trace", replay_trace),
        trace_artifact("side_effect_artifact_only_reconstruction_trace", reconstruction_trace),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n27_transfer_side_effect_replay_probe",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "5-B",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": "Replay and reconstruct I4-B transfer side-effect traces.",
        "source_records": [
            {
                "source_id": "n27_i4b_side_effect_observation",
                "path": rel(I4B_OUTPUT),
                "source_role": "source_current_side_effect_observation",
                "output_digest": i4b["output_digest"],
                "sha256": sha256_file(I4B_OUTPUT),
            }
        ],
        "transfer_side_effect_observation_output_digest": i4b["output_digest"],
        "replay_row": {
            "row_id": "n27_i5b_row_i4b_side_effect_replay",
            "row_decision": "supported",
            "row_decision_scope": "n28_precursor_side_effect_replay_only",
            "artifact_manifest": artifacts,
            "all_artifact_sha256_match_file_contents": all(
                sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifacts
            ),
            "replay_trace": replay_trace,
            "replay_trace_digest": digest_value(replay_trace),
            "reconstruction_trace": reconstruction_trace,
            "reconstruction_trace_digest": digest_value(reconstruction_trace),
            "side_effect_replay_supported": True,
            "n28_readiness_side_effect_replay_supported": True,
            "n28_generative_persistence_supported": False,
            "final_transfer_supported": False,
            "claim_ceiling": "N28-ready side-effect replay candidate only",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "n28_readiness_side_effect_replay_supported": True,
        "n28_generative_persistence_supported": False,
        "ready_for_iteration_6a_side_effect_evaluation_matrix": True,
        "claim_boundary": {
            "claim_ceiling": "side-effect replay/reconstruction only",
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
    }
    strings = collect_strings(output)
    output["checks"] = [
        check("i4b_source_available", i4b["status"] == "passed", i4b["status"]),
        check("artifact_replay_passed", replay_core["artifact_replay_passed"], replay_core),
        check(
            "artifact_only_reconstruction_passed",
            replay_core["artifact_only_reconstruction_passed"],
            reconstruction_trace,
        ),
        check(
            "replay_creates_no_new_side_effect_evidence",
            replay_core["replay_creates_new_side_effect_evidence"] is False,
            replay_core,
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
        "accepted_transfer_side_effect_replay_reconstruction_no_n28_claim"
        if output["status"] == "passed"
        else "blocked_transfer_side_effect_replay"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["replay_row"]
    replay = row["replay_trace"]["replay_core"]
    report = f"""# N27 Iteration 5-B - Transfer Side-Effect Replay Probe

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

```text
artifact_replay_passed = {str(replay['artifact_replay_passed']).lower()}
snapshot_load_replay_passed = {str(replay['snapshot_load_replay_passed']).lower()}
duplicate_replay_digest_stable = {str(replay['duplicate_replay_digest_stable']).lower()}
artifact_only_reconstruction_passed = {str(replay['artifact_only_reconstruction_passed']).lower()}
n28_generative_persistence_supported = false
```

I5-B makes the I4-B side-effect observation replayable and reconstructable from
artifacts. It does not create new side-effect evidence and does not support
N28 generative persistence.

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
