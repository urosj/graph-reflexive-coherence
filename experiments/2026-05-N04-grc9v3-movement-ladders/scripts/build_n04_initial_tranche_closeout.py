#!/usr/bin/env python3
"""Close the initial N04 fixed-substrate/M0-M6 tranche.

This is a boundary marker. It preserves the strongest bounded M6 candidate and
hands off to Iterations 13-19; it does not close N04 or promote broader movement claims.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/n04_initial_tranche_closeout.json"
REPORT_PATH = N04 / "reports/n04_initial_tranche_closeout.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_initial_tranche_closeout.py"
)


ARTIFACTS = {
    "fixed_substrate_tranche_a": N04 / "outputs/fixed_substrate_tranche_a_report.json",
    "m0_m3_classifier": N04 / "outputs/movement_classifier_m0_m3_validation.json",
    "m2_runtime_shape_blocked": N04 / "outputs/m2_runtime_shape_blocked_fixture.json",
    "boundary_coupled_pulse_fixture": N04 / "outputs/boundary_coupled_pulse_report.json",
    "m4_m5_classifier": N04 / "outputs/loop_driven_movement_m4_m5_report.json",
    "lane_b_direction_parity": N04 / "outputs/n04_lane_b_direction_parity_closeout.json",
    "native_m6_validator": N04 / "outputs/native_m6_same_fixture_validator.json",
    "native_m6_audit": N04 / "outputs/native_m6_validation_checklist_audit.json",
    "visual_reference": N04 / "outputs/m_taxonomy_visual_reference.json",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _m0_m3_summary(classifier: dict[str, Any]) -> dict[str, Any]:
    classifications = classifier["classifications"]
    levels: dict[str, int] = {}
    for row in classifications.values():
        level = row["movement_level"]
        levels[level] = levels.get(level, 0) + 1
    fixed = [
        row
        for row in classifications.values()
        if row.get("source") == "iteration_5_fixed_substrate"
    ]
    return {
        "distribution": levels,
        "fixed_substrate_all_m0": all(
            row["movement_level"].startswith("M0") for row in fixed
        ),
        "fixed_substrate_claims_blocked": all(
            row["movement_claim_allowed"] is False for row in fixed
        ),
    }


def build_closeout() -> dict[str, Any]:
    data = {key: _load_json(path) for key, path in ARTIFACTS.items()}
    records = {key: _artifact_record(path) for key, path in ARTIFACTS.items()}
    native_m6 = data["native_m6_validator"]
    m2 = data["m2_runtime_shape_blocked"]
    lane_b = data["lane_b_direction_parity"]
    visual = data["visual_reference"]

    blocked_claims = {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "unrestricted_movement_claim_allowed": False,
    }
    source_of_truth_by_rung = {
        "M0": [
            records["fixed_substrate_tranche_a"]["path"],
            records["m0_m3_classifier"]["path"],
        ],
        "M1": [
            "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_timeseries/S0_chain_v1_basin_replacement.jsonl",
            records["m0_m3_classifier"]["path"],
        ],
        "M2": [
            records["m2_runtime_shape_blocked"]["path"],
            "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl",
        ],
        "M3": [
            "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_timeseries/S0_chain_v1_shape_preserving_shift.jsonl",
            records["m0_m3_classifier"]["path"],
        ],
        "M4": [
            records["boundary_coupled_pulse_fixture"]["path"],
            records["m4_m5_classifier"]["path"],
        ],
        "M5": [records["lane_b_direction_parity"]["path"]],
        "M6": [
            records["native_m6_validator"]["path"],
            records["native_m6_audit"]["path"],
        ],
    }
    checks = {
        "all_source_artifacts_present": all(path.exists() for path in ARTIFACTS.values()),
        "fixed_substrate_claims_remain_blocked": _m0_m3_summary(
            data["m0_m3_classifier"]
        )["fixed_substrate_claims_blocked"],
        "m2_runtime_fixture_passed": m2["status"] == "passed"
        and m2["classification"]["movement_level"] == "M2_identity_preserving_displacement",
        "m5_direction_parity_supported": lane_b["status"] == "passed"
        and lane_b["claim_ceiling"] == "m5_direction_parity_supported_boundary_response",
        "native_m6_same_fixture_candidate_passed": native_m6["status"] == "passed"
        and native_m6["claim_flags"]["native_m6"] is True
        and native_m6["claim_flags"]["native_m6_candidate_gate_passed"] is True,
        "broader_claims_blocked": all(value is False for value in blocked_claims.values()),
        "taxonomy_continuation_opened": True,
        "visual_reference_current": visual["status"] == "passed"
        and len(visual["records"]) == 7,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_initial_tranche_closeout_v1",
        "iteration": "12",
        "status": "passed" if all(checks.values()) else "failed",
        "tranche": "initial_fixed_substrate_m0_m6",
        "result": "closed_with_taxonomy_handoff",
        "next_iteration": "13_taxonomy_inventory",
        "strongest_current_ceiling": "native_m6_same_fixture_self_renewal_candidate",
        "claim_flags": {
            **blocked_claims,
            "native_m6": native_m6["claim_flags"]["native_m6"],
            "native_m6_candidate_gate_passed": native_m6["claim_flags"][
                "native_m6_candidate_gate_passed"
            ],
        },
        "source_artifacts": records,
        "source_of_truth_by_rung": source_of_truth_by_rung,
        "m0_m3_summary": _m0_m3_summary(data["m0_m3_classifier"]),
        "m2_runtime_summary": {
            "movement_level": m2["classification"]["movement_level"],
            "primary_blocked_reason": m2["classification"]["primary_blocked_reason"],
            "centroid_displacement": m2["metrics"]["centroid_displacement"],
            "profile_similarity_aligned": m2["metrics"]["profile_similarity_aligned"],
        },
        "m5_summary": {
            "claim_ceiling": lane_b["claim_ceiling"],
            "primary_result": lane_b["primary_result"],
        },
        "m6_summary": {
            "claim_ceiling": native_m6["claim_ceiling"],
            "movement_substrate": native_m6["movement_substrate"],
            "forward_dx": native_m6["direction_parity"]["forward_centroid_delta"],
            "reversed_dx": native_m6["direction_parity"]["reversed_centroid_delta"],
            "forward_self_renewed_cycles": native_m6["forward"][
                "self_renewed_cycle_count"
            ],
            "reversed_self_renewed_cycles": native_m6["reversed"][
                "self_renewed_cycle_count"
            ],
            "profile_similarity": native_m6["forward"]["profile_similarity"],
            "width_relative_change": native_m6["forward"]["width_relative_change"],
        },
        "blocked_claims": list(blocked_claims),
        "taxonomy_continuation": {
            "purpose": (
                "Inventory and separate movement taxonomy classes across centroid, "
                "boundary, shape, deformation, basin identity, self-renewal, geometry, "
                "and topology axes."
            ),
            "first_artifacts": [
                "outputs/n04_taxonomy_inventory_v1.json",
                "reports/n04_taxonomy_inventory_v1.md",
            ],
            "adaptive_topology_status": "blocked_until_explicit_topology_controls",
        },
        "checks": checks,
        "environment": {
            "command": COMMAND,
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "git_diff_check": _run_git(["diff", "--check"]),
        },
    }


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# N04 Initial Tranche Closeout",
        "",
        f"Status: `{payload['status']}`",
        f"Result: `{payload['result']}`",
        f"Next iteration: `{payload['next_iteration']}`",
        "",
        "## Claim Ceiling",
        "",
        f"- strongest current ceiling: `{payload['strongest_current_ceiling']}`",
        f"- native_m6: `{payload['claim_flags']['native_m6']}`",
        f"- native_m6_candidate_gate_passed: `{payload['claim_flags']['native_m6_candidate_gate_passed']}`",
        f"- movement_claim_allowed: `{payload['claim_flags']['movement_claim_allowed']}`",
        "",
        "This closes the initial fixed-substrate/M0-M6 tranche. It does not close N04.",
        "",
        "## Source Of Truth By Rung",
        "",
    ]
    for rung, paths in payload["source_of_truth_by_rung"].items():
        lines.append(f"### {rung}")
        for path in paths:
            lines.append(f"- `{path}`")
        lines.append("")
    lines.extend(
        [
            "## Summaries",
            "",
            f"- M2: `{payload['m2_runtime_summary']['movement_level']}` with `{payload['m2_runtime_summary']['primary_blocked_reason']}`.",
            f"- M5: `{payload['m5_summary']['claim_ceiling']}`.",
            f"- M6: `{payload['m6_summary']['claim_ceiling']}` on `{payload['m6_summary']['movement_substrate']}`.",
            "",
            "## Blocked Claims",
            "",
        ]
    )
    for claim in payload["blocked_claims"]:
        lines.append(f"- `{claim}`")
    lines.extend(
        [
            "",
            "## Taxonomy Continuation Handoff",
            "",
            payload["taxonomy_continuation"]["purpose"],
            "",
            "First artifacts:",
            "",
        ]
    )
    for artifact in payload["taxonomy_continuation"]["first_artifacts"]:
        lines.append(f"- `{artifact}`")
    lines.extend(
        [
            "",
            f"Adaptive topology status: `{payload['taxonomy_continuation']['adaptive_topology_status']}`",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    for key, value in payload["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Acceptance",
            "",
            "Iteration 12 closes the initial N04 fixed-substrate/M0-M6 tranche and opens Iterations 13-19 as a movement-taxonomy/topology search sequence. The closeout preserves the bounded native M6 same-fixture candidate and the M0-M6 evidence ladder, but it does not permit adaptive-topology, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement claims.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = build_closeout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "next_iteration": payload["next_iteration"],
            },
            sort_keys=True,
        )
    )
    if payload["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
