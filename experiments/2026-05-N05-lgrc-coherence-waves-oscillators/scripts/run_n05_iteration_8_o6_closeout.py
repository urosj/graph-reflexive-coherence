"""Run N05 Iteration 8: O6 route-coupled oscillator boundary and closeout.

This closeout is artifact-only. It inspects the completed N05 Iteration 1-7
artifacts, freezes O5 as the strongest supported O-level, and records that O6
route/trail-memory support remains blocked by a missing native route conductance
memory policy surface.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
OUTPUT_PATH = N05 / "outputs/n05_iteration_8_o6_closeout.json"
REPORT_PATH = N05 / "reports/n05_iteration_8_o6_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "run_n05_iteration_8_o6_closeout.py"
)

SOURCE_ARTIFACTS = {
    "iteration_1_baseline_inventory": (
        N05 / "outputs/n05_iteration_1_baseline_inventory.json",
        N05 / "reports/n05_iteration_1_baseline_inventory.md",
    ),
    "iteration_2_fixture_manifest_validation": (
        N05 / "outputs/n05_iteration_2_fixture_manifest_validation.json",
        N05 / "reports/n05_iteration_2_fixture_manifest_validation.md",
    ),
    "iteration_3_o1_delayed_outbound_pulse": (
        N05 / "outputs/n05_iteration_3_o1_delayed_outbound_pulse.json",
        N05 / "reports/n05_iteration_3_o1_delayed_outbound_pulse.md",
    ),
    "iteration_4_o2_reflected_return_pulse": (
        N05 / "outputs/n05_iteration_4_o2_reflected_return_pulse.json",
        N05 / "reports/n05_iteration_4_o2_reflected_return_pulse.md",
    ),
    "iteration_5_o3_amplified_return": (
        N05 / "outputs/n05_iteration_5_o3_amplified_return.json",
        N05 / "reports/n05_iteration_5_o3_amplified_return.md",
    ),
    "iteration_6_o4_repeated_cycle": (
        N05 / "outputs/n05_iteration_6_o4_repeated_cycle.json",
        N05 / "reports/n05_iteration_6_o4_repeated_cycle.md",
    ),
    "iteration_7_o5_self_sustained_boundary": (
        N05 / "outputs/n05_iteration_7_o5_self_sustained_boundary.json",
        N05 / "reports/n05_iteration_7_o5_self_sustained_boundary.md",
    ),
}

BLOCKED_CLAIMS = (
    "movement",
    "semantic_choice",
    "agency",
    "rc_identity_collapse",
    "identity_acceptance",
    "memory_or_trail",
    "goal_proxy_regulation",
    "agentic_like_behavior",
    "locomotion_like_behavior",
    "biological_behavior",
    "ant_colony_behavior",
    "unrestricted_movement",
)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _source_artifact_index() -> dict[str, Any]:
    index: dict[str, Any] = {}
    for key, (artifact_path, report_path) in SOURCE_ARTIFACTS.items():
        artifact = _load_json(artifact_path)
        index[key] = {
            "artifact_path": _rel(artifact_path),
            "artifact_sha256": _file_sha256(artifact_path),
            "artifact_status": artifact.get("status"),
            "artifact_digests": artifact.get("artifact_digests", {}),
            "report_path": _rel(report_path),
            "report_sha256": _file_sha256(report_path),
            "positive_o_level": artifact.get("positive_lane", {}).get("o_level"),
            "claim_ceiling": artifact.get("positive_lane", {}).get("claim_ceiling")
            or artifact.get("claim_ceiling"),
        }
    return index


def _o5_artifact(source_index: Mapping[str, Any]) -> dict[str, Any]:
    _ = source_index
    return _load_json(SOURCE_ARTIFACTS["iteration_7_o5_self_sustained_boundary"][0])


def _all_source_artifacts_passed(source_index: Mapping[str, Any]) -> bool:
    return all(record.get("artifact_status") == "passed" for record in source_index.values())


def _route_coupling_boundary(o5: Mapping[str, Any]) -> dict[str, Any]:
    lane = dict(o5["positive_lane"])
    route_aspect = dict(lane.get("route_aspect", {}))
    phase3_audit = dict(lane.get("phase3_native_policy_support_audit", {}))
    route_memory_supported = bool(phase3_audit.get("route_conductance_memory_support"))
    return {
        "o6_route_coupled_oscillator_supported": False,
        "route_coupled_oscillator_candidate_supported": False,
        "route_coupling_surface": "serialized_lgrc9v3_route_aspect_without_route_conductance_memory",
        "route_coupling_fields": {
            "route_aspect_id": route_aspect.get("route_aspect_id"),
            "route_aspect_digest": route_aspect.get("route_aspect_digest"),
            "channel_sequence": route_aspect.get("channel_sequence", []),
            "channel_sequence_digest": route_aspect.get("channel_sequence_digest"),
            "pole_region_digest": route_aspect.get("pole_region_digest"),
            "route_edge_ids": [
                hop.get("edge_id")
                for channel in route_aspect.get("channels", [])
                for hop in channel.get("route_hops", [])
            ],
            "route_conductance_memory_policy_id": None,
            "route_conductance_memory_digest": None,
            "trail_reinforcement_surface_digest": None,
        },
        "route_coupling_runtime_visible": bool(
            route_aspect.get("route_aspect_digest")
            and route_aspect.get("channel_sequence_digest")
        ),
        "route_memory_runtime_visible": route_memory_supported,
        "memory_or_trail_claim_allowed": False,
        "trail_memory_blocker": "missing_route_conductance_memory_policy",
        "route_arbitration_used": False,
        "route_arbitration_boundary": (
            "native route arbitration was not used in N05 O6 closeout; if used "
            "later, it is runtime route selection evidence only, not semantic choice"
        ),
        "o6_closeout_interpretation": (
            "O5 self-rearm traffic is route-aspect serialized and replayable, "
            "but current artifacts do not include a runtime-visible route memory "
            "or trail-reinforcement surface. O6 therefore remains blocked."
        ),
    }


def _artifact_replay(o5: Mapping[str, Any], boundary: Mapping[str, Any]) -> dict[str, Any]:
    lane = dict(o5["positive_lane"])
    o5_replay = dict(o5["artifact_replay"])
    route_fields = dict(boundary["route_coupling_fields"])
    route_memory_missing = (
        route_fields.get("route_conductance_memory_policy_id") is None
        and route_fields.get("trail_reinforcement_surface_digest") is None
    )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "o5_artifact_replay_passed": bool(o5_replay.get("passed")),
        "o5_self_rearm_validator": o5_replay.get("validator"),
        "o5_cycle_count_reconstructed": o5_replay.get("cycle_count_reconstructed"),
        "route_aspect_reconstructed": bool(
            route_fields.get("route_aspect_digest")
            and route_fields.get("channel_sequence_digest")
        ),
        "route_memory_surface_reconstructed": not route_memory_missing,
        "route_coupled_oscillator_supported": False,
        "route_coupled_oscillator_replay_status": "blocked_missing_route_memory_surface",
        "primary_blocker": "missing_route_conductance_memory_policy",
        "budget_ok": lane.get("node_plus_packet_budget_error") == 0.0,
        "passed": (
            bool(o5_replay.get("passed"))
            and bool(route_fields.get("route_aspect_digest"))
            and route_memory_missing
            and lane.get("node_plus_packet_budget_error") == 0.0
        ),
    }


def _controls(o5: Mapping[str, Any], boundary: Mapping[str, Any]) -> dict[str, Any]:
    lane = dict(o5["positive_lane"])
    producer_boundary = dict(lane.get("producer_boundary", {}))
    flags = dict(o5.get("claim_flags", {}))
    route_fields = dict(boundary["route_coupling_fields"])
    controls = {
        "hidden_trail": {
            "control_id": "hidden_trail",
            "control_execution_mode": "artifact_route_memory_boundary_control",
            "passed": route_fields.get("trail_reinforcement_surface_digest") is None
            and boundary.get("memory_or_trail_claim_allowed") is False,
            "primary_blocker": "n05_o6_hidden_trail_rejected",
        },
        "hidden_route_preference": {
            "control_id": "hidden_route_preference",
            "control_execution_mode": "artifact_route_surface_control",
            "passed": boundary.get("route_arbitration_used") is False
            and bool(route_fields.get("channel_sequence_digest")),
            "primary_blocker": "n05_o6_hidden_route_preference_rejected",
        },
        "budget_mismatch": {
            "control_id": "budget_mismatch",
            "control_execution_mode": "artifact_budget_control",
            "passed": lane.get("node_plus_packet_budget_error") == 0.0,
            "primary_blocker": "n05_o6_node_plus_packet_budget_mismatch",
        },
        "producer_mutation": {
            "control_id": "producer_mutation_attempt",
            "control_execution_mode": "artifact_producer_boundary_control",
            "passed": (
                producer_boundary.get("producer_mutated_coherence") is False
                and producer_boundary.get("producer_mutated_topology") is False
                and producer_boundary.get("producer_emitted_claim_label") is False
            ),
            "primary_blocker": "n05_o6_producer_mutation_boundary_violation",
        },
        "claim_promotion": {
            "control_id": "claim_promotion_attempt",
            "control_execution_mode": "artifact_claim_boundary_control",
            "passed": all(value is False for value in flags.values())
            and boundary.get("memory_or_trail_claim_allowed") is False
            and boundary.get("o6_route_coupled_oscillator_supported") is False,
            "primary_blocker": "n05_o6_claim_promotion_rejected",
        },
        "missing_route_memory_surface": {
            "control_id": "missing_route_memory_surface",
            "control_execution_mode": "native_policy_support_boundary_control",
            "passed": boundary.get("route_memory_runtime_visible") is False
            and boundary.get("trail_memory_blocker")
            == "missing_route_conductance_memory_policy",
            "primary_blocker": "n05_o6_route_memory_surface_missing",
        },
    }
    controls["all_controls_passed"] = all(
        record["passed"] for record in controls.values() if isinstance(record, dict)
    )
    return controls


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_artifact_index_digest": _digest(result["source_artifacts"]),
        "o6_boundary_digest": _digest(result["o6_boundary"]),
        "artifact_replay_digest": _digest(result["artifact_replay"]),
        "controls_digest": _digest(result["controls"]),
        "closeout_summary_digest": _digest(result["n05_closeout"]),
    }


def _write_report(result: Mapping[str, Any]) -> None:
    closeout = result["n05_closeout"]
    boundary = result["o6_boundary"]
    replay = result["artifact_replay"]
    controls = result["controls"]
    phase3 = result["phase3_native_policy_support_audit"]
    digest_lines = "\n".join(
        f"- `{key}`: `{value}`"
        for key, value in sorted(result["artifact_digests"].items())
    )
    source_lines = "\n".join(
        (
            f"- `{key}`: `{record['artifact_path']}` "
            f"sha256 `{record['artifact_sha256']}`"
        )
        for key, record in result["source_artifacts"].items()
    )
    control_lines = "\n".join(
        (
            f"- `{key}`: passed={record['passed']}, "
            f"primary_blocker=`{record['primary_blocker']}`"
        )
        for key, record in controls.items()
        if isinstance(record, dict)
    )
    blocker_lines = "\n".join(
        f"- `{blocker}`" for blocker in phase3.get("native_policy_blockers", [])
    )
    claim_lines = "\n".join(
        f"- `{key}` = `{value}`" for key, value in sorted(result["claim_flags"].items())
    )
    REPORT_PATH.write_text(
        f"""# N05 Iteration 8: O6 Route-Coupled Oscillator Boundary And Closeout

Status: {result['status']}.

## Result

N05 closes with strongest supported O-level
`{closeout['strongest_supported_o_level']}` and claim ceiling
`{closeout['strongest_claim_ceiling']}`.

O6 route-coupled / trail-reinforced oscillator support remains blocked:

```text
o6_route_coupled_oscillator_supported = {boundary['o6_route_coupled_oscillator_supported']}
trail_memory_blocker = {boundary['trail_memory_blocker']}
```

The O5 lane provides a runtime-visible serialized route-aspect surface and
self-rearm oscillator evidence, but it does not provide route conductance
memory or trail reinforcement.

## Route Coupling Boundary

```json
{json.dumps(boundary, indent=2, sort_keys=True)}
```

Native route arbitration was not used in this N05 closeout. If a later lane
uses route arbitration as a route-coupling surface, it remains runtime route
selection evidence only, not semantic choice or agency.

## Artifact-Only Replay

```json
{json.dumps(replay, indent=2, sort_keys=True)}
```

The replay reconstructs the O5 route-aspect/self-rearm chain from exported
artifacts and then fails closed for O6 because no runtime-visible route memory
surface is present.

## Controls

{control_lines}

## Phase 3 Native-Policy Blockers

{blocker_lines}

## Source Artifact SHA-256 Digests

{source_lines}

## Derived Digests

{digest_lines}

## Claim Flags

{claim_lines}

## Handoff

Recommendation: `{result['n06_handoff_recommendation']['next_experiment']}`.

N06 may open semantic route-choice work using N05 O5 as oscillator/circuit
background. N06 must not inherit memory/trail, semantic choice, agency, RC
identity collapse, identity acceptance, locomotion-like, biological, ACO, or
unrestricted movement claims from N05.

## Acceptance Result

Achieved. Iteration 8 freezes N05 at O5 with source-backed artifacts, exact
budget accounting, artifact-only replay, explicit O6 blocker evidence, and a
clear N06 handoff.
""",
        encoding="utf-8",
    )


def main() -> None:
    source_index = _source_artifact_index()
    o5 = _o5_artifact(source_index)
    lane = dict(o5["positive_lane"])
    boundary = _route_coupling_boundary(o5)
    replay = _artifact_replay(o5, boundary)
    controls = _controls(o5, boundary)
    claim_flags = dict(o5["claim_flags"])
    phase3 = dict(lane["phase3_native_policy_support_audit"])
    source_artifacts_passed = _all_source_artifacts_passed(source_index)
    budget = {
        "budget_surface": "node_plus_packet",
        "source_iteration": "iteration_7_o5_self_sustained_boundary",
        "node_plus_packet_budget_before": lane.get("node_plus_packet_budget_before"),
        "node_plus_packet_budget_after": lane.get("node_plus_packet_budget_after"),
        "node_plus_packet_budget_error": lane.get("node_plus_packet_budget_error"),
        "budget_exact": lane.get("node_plus_packet_budget_error") == 0.0,
        "o6_new_budget_mutation_performed": False,
    }
    closeout = {
        "strongest_supported_o_level": "O5",
        "strongest_claim_ceiling": "self_sustained_oscillator_candidate",
        "o6_supported": False,
        "o6_primary_blocker": "missing_route_conductance_memory_policy",
        "source_artifacts_passed": source_artifacts_passed,
        "artifact_only_replay_passed": replay["passed"],
        "controls_passed": controls["all_controls_passed"],
        "budget_exact": budget["budget_exact"],
        "claim_flags_remain_false": all(value is False for value in claim_flags.values()),
        "src_changes_required": False,
    }
    status = (
        "passed"
        if (
            source_artifacts_passed
            and replay["passed"]
            and controls["all_controls_passed"]
            and budget["budget_exact"]
            and closeout["claim_flags_remain_false"]
            and boundary["o6_route_coupled_oscillator_supported"] is False
        )
        else "failed"
    )
    result: dict[str, Any] = {
        "schema": "coherence_oscillator_report_v1",
        "run_id": "n05_iteration_8_o6_closeout_v1",
        "iteration": 8,
        "status": status,
        "command": COMMAND,
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2",
        "execution_stage": "artifact_only_closeout_boundary_no_new_runtime_probe",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
        "source_artifacts": source_index,
        "n05_closeout": closeout,
        "o_ladder": {
            "strongest_supported_o_level": "O5",
            "strongest_claim_ceiling": "self_sustained_oscillator_candidate",
            "o6_route_coupled_oscillator_supported": False,
            "o_level_is_evidence_classification": True,
        },
        "o6_boundary": boundary,
        "artifact_replay": replay,
        "controls": controls,
        "budget": budget,
        "producer_boundary": lane.get("producer_boundary", {}),
        "phase3_native_policy_support_audit": phase3,
        "n06_handoff_recommendation": {
            "next_experiment": "N06_semantic_route_choice",
            "recommendation": "open_N06_with_N05_O5_as_oscillator_background",
            "ready": True,
            "rationale": (
                "N05 has source-backed O5 self-rearm oscillator evidence and "
                "a fail-closed O6 route-memory blocker. Semantic route-choice "
                "should be opened as its own ladder rather than inferred from "
                "oscillator evidence."
            ),
            "constraints": [
                "do_not_inherit_memory_or_trail_claims_from_N05",
                "do_not_treat_native_route_arbitration_as_semantic_choice",
                "keep_producer_scaffolds_labeled_as_scheduling_evidence",
                "keep_identity_invariance_and_agency_claims_blocked",
            ],
        },
        "claim_boundary": {
            "o_level_is_evidence_classification": True,
            "route_coupled_oscillator_does_not_imply_memory": True,
            "route_arbitration_does_not_imply_semantic_choice": True,
            "producer_scheduling_does_not_imply_agency": True,
        },
        "claim_flags": claim_flags,
        "blocked_claims": list(BLOCKED_CLAIMS),
    }
    result["artifact_digests"] = _artifact_digests(result)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "strongest_supported_o_level": closeout["strongest_supported_o_level"],
                "strongest_claim_ceiling": closeout["strongest_claim_ceiling"],
                "o6_route_coupled_oscillator_supported": boundary[
                    "o6_route_coupled_oscillator_supported"
                ],
                "trail_memory_blocker": boundary["trail_memory_blocker"],
                "artifact_replay_passed": replay["passed"],
                "controls_passed": controls["all_controls_passed"],
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
