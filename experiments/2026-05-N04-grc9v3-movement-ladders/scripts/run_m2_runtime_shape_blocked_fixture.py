#!/usr/bin/env python3
"""Build the Iteration 11-B runtime fixture for M2.

The fixture is deliberately shape-blocked: it preserves budget and identity,
passes displacement and directed boundary reassignment, then fails the profile
similarity gate so the frozen M0-M3 classifier stops at M2.
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
SCRIPTS = N04 / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_movement_classifier as classifier  # noqa: E402
import validate_movement_observables as observables  # noqa: E402


OUTPUT_PATH = N04 / "outputs/m2_runtime_shape_blocked_fixture.json"
REPORT_PATH = N04 / "reports/m2_runtime_shape_blocked_fixture.md"
TIMESERIES_DIR = N04 / "outputs/m2_runtime_shape_blocked_timeseries"
RUN_ID = "S0_chain_v1_M2_shape_degraded_boundary_handoff"
LANE_ID = "M2_shape_degraded_boundary_handoff"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_m2_runtime_shape_blocked_fixture.py"
)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _write_timeseries(
    fixture_id: str,
    states: list[list[float]],
    obs: dict[str, Any],
) -> dict[str, Any]:
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)
    path = TIMESERIES_DIR / f"{LANE_ID}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for step, values in enumerate(states):
            handle.write(
                json.dumps(
                    {
                        "step": step,
                        "run_id": RUN_ID,
                        "lane_id": LANE_ID,
                        "fixture_id": fixture_id,
                        "centroid": obs["centroid"]["x_t"][step],
                        "support_mask": obs["support_tracking"]["support_mask_t"][step],
                        "mass": obs["shape"]["mass_t"][step],
                        "width": obs["shape"]["width_t"][step],
                        "budget": obs["conservation"]["budget_t"][step],
                        "coherence_by_node": {
                            str(index): value for index, value in enumerate(values)
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    return {
        "path": _rel(path),
        "sha256": _sha256(path),
        "row_count": len(states),
    }


def _build_states(fixture: dict[str, Any], base: list[float]) -> list[list[float]]:
    shifted = observables._translate_profile(fixture, base, 1)
    degraded = list(shifted)

    # Create a directed boundary handoff while locally degrading the profile.
    # This keeps total mass fixed after projection and makes profile similarity
    # the M3 blocker.
    transfer_mass = 0.40
    for node in [15, 16]:
        degraded[node] += transfer_mass / 2.0
    for node in [11, 12]:
        degraded[node] -= transfer_mass / 2.0
    degraded = observables._project_nonnegative_simplex(degraded, sum(base))
    return [list(base), degraded]


def _claim_flags() -> dict[str, bool]:
    return {
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "movement_claim_inherited_from_n03": False,
        "native_lgrc9v3_e3_pulse_used": False,
        "native_grc9v3_proposal_flux_control_used": False,
        "native_m6": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
    }


def _classifier_item(
    fixture_id: str,
    states: list[list[float]],
    obs: dict[str, Any],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    budget_passed = obs["conservation"]["budget_abs_error_max"] <= thresholds["epsilon_budget"]
    displacement_passed = (
        obs["centroid"]["delta_x_abs"] >= thresholds["effective_displacement_min"]
    )
    identity_passed = (
        obs["support_tracking"]["identity_mass_ratio_min"]
        >= thresholds["identity_mass_ratio_min"]
    )
    shape_passed = (
        obs["shape"]["width_relative_change_max"]
        <= thresholds["width_relative_change_max"]
        and obs["profile_similarity"]["aligned"] >= thresholds["profile_similarity_min"]
    )
    boundary_reassignment_passed = (
        obs["boundary_flips"]["front_entered_mass"] > 0.0
        and obs["boundary_flips"]["rear_left_mass"] > 0.0
    )
    return {
        "source": "iteration_11b_runtime_shape_blocked_fixture",
        "run_id": RUN_ID,
        "fixture_id": fixture_id,
        "lane_or_case_id": LANE_ID,
        "budget_passed": budget_passed,
        "displacement_passed": displacement_passed,
        "identity_passed": identity_passed,
        "shape_passed": shape_passed,
        "topology_passed": obs["topology"]["topology_changed"] is False,
        "nonnegative_passed": all(value >= -1e-12 for state in states for value in state),
        "centroid_displacement": obs["centroid"]["delta_x_total"],
        "centroid_displacement_abs": obs["centroid"]["delta_x_abs"],
        "width_relative_change_max": obs["shape"]["width_relative_change_max"],
        "profile_similarity": obs["profile_similarity"]["aligned"],
        "budget_surface": obs["conservation"]["budget_surface"],
        "identity_level_input": obs["support_tracking"]["identity_continuity_level"],
        "boundary_flip_count": obs["boundary_flip_count"],
        "front_entered_mass": obs["boundary_flips"]["front_entered_mass"],
        "rear_left_mass": obs["boundary_flips"]["rear_left_mass"],
        "boundary_reassignment_passed": boundary_reassignment_passed,
        "diagnostic_signal": "runtime_shape_failure_after_boundary_handoff",
        "m0_subtype_hint": None,
        "claim_flags": _claim_flags(),
    }


def _write_report(payload: dict[str, Any]) -> None:
    result = payload["classification"]
    metrics = payload["metrics"]
    checks = payload["checks"]
    lines = [
        "# Iteration 11-B M2 Runtime Shape-Blocked Fixture",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This fixture provides a runtime timeseries for the M2 rung. It is not a",
        "movement claim and it is not native LGRC telemetry. The lane intentionally",
        "passes displacement, identity, budget, topology, and directed boundary",
        "reassignment, then fails the profile similarity gate so M3 remains blocked.",
        "",
        "## Classification",
        "",
        f"- movement_level: `{result['movement_level']}`",
        f"- diagnostic_subtype: `{result['diagnostic_subtype']}`",
        f"- primary_blocked_reason: `{result['primary_blocked_reason']}`",
        f"- movement_claim_allowed: `{result['movement_claim_allowed']}`",
        "",
        "## Metrics",
        "",
        f"- centroid displacement: `{metrics['centroid_displacement']}`",
        f"- effective displacement threshold: `{payload['metric_thresholds']['effective_displacement_min']}`",
        f"- front entered mass: `{metrics['front_entered_mass']}`",
        f"- rear left mass: `{metrics['rear_left_mass']}`",
        f"- identity mass ratio min: `{metrics['identity_mass_ratio_min']}`",
        f"- width relative change max: `{metrics['width_relative_change_max']}`",
        f"- profile similarity aligned: `{metrics['profile_similarity_aligned']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in checks.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- `{payload['timeseries']['path']}`",
            f"- `{_rel(OUTPUT_PATH)}`",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report() -> dict[str, Any]:
    manifest = observables._load_json(observables.MANIFEST_PATH)
    initializer = observables._load_json(observables.INITIALIZER_PATH)
    metrics = manifest["metric_defaults"]
    null_envelope = manifest["null_displacement_envelope"]
    thresholds = {
        "effective_displacement_min": max(
            float(metrics["configured_displacement_min"]),
            float(null_envelope["mean"])
            + float(metrics["null_calibration_k"]) * float(null_envelope["std"]),
        ),
        "epsilon_budget": float(metrics["epsilon_budget"]),
        "width_relative_change_max": float(metrics["width_relative_change_max"]),
        "profile_similarity_min": float(metrics["profile_similarity_min"]),
        "identity_mass_ratio_min": float(metrics["identity_mass_ratio_min"]),
    }

    fixture_id = "S0_chain_v1"
    fixture = manifest["fixtures"][fixture_id]
    base_lane = initializer["lane_results"][f"{fixture_id}:B0"]
    base = observables._node_values(base_lane, int(fixture["node_count"]))
    direction = float(fixture["front_rear_definition"]["direction_vector"][0])
    states = _build_states(fixture, base)
    obs = observables._observables(
        fixture,
        states,
        direction,
        direction_source="configured",
        identity_gate_min=thresholds["identity_mass_ratio_min"],
        topology_changed=False,
    )
    timeseries = _write_timeseries(fixture_id, states, obs)
    item = _classifier_item(fixture_id, states, obs, thresholds)
    result = classifier._classify(item)
    metrics_out = {
        "centroid_displacement": obs["centroid"]["delta_x_total"],
        "centroid_displacement_abs": obs["centroid"]["delta_x_abs"],
        "front_entered_mass": obs["boundary_flips"]["front_entered_mass"],
        "rear_left_mass": obs["boundary_flips"]["rear_left_mass"],
        "identity_mass_ratio_min": obs["support_tracking"]["identity_mass_ratio_min"],
        "width_relative_change_max": obs["shape"]["width_relative_change_max"],
        "profile_similarity_aligned": obs["profile_similarity"]["aligned"],
        "budget_abs_error_max": obs["conservation"]["budget_abs_error_max"],
        "nonnegative_min": min(min(state) for state in states),
    }
    checks = {
        "budget_gate_passed": item["budget_passed"],
        "displacement_gate_passed": item["displacement_passed"],
        "identity_gate_passed": item["identity_passed"],
        "boundary_reassignment_gate_passed": item["boundary_reassignment_passed"],
        "shape_gate_failed": not item["shape_passed"],
        "profile_gate_is_shape_blocker": (
            obs["profile_similarity"]["aligned"] < thresholds["profile_similarity_min"]
        ),
        "classified_as_m2": result["movement_level"]
        == "M2_identity_preserving_displacement",
        "primary_blocker_shape": result["primary_blocked_reason"] == "shape_gate_failed",
        "movement_claims_blocked": (
            not result["movement_claim_allowed"]
            and not any(result["claim_flags"].values())
            and not any(_claim_flags().values())
        ),
        "timeseries_emitted": timeseries["row_count"] == len(states)
        and bool(timeseries["sha256"]),
    }
    payload = {
        "schema": "n04_iteration_11b_m2_runtime_shape_blocked_fixture_v1",
        "report_kind": "m2_runtime_shape_blocked_fixture",
        "status": "passed" if all(checks.values()) else "failed",
        "run_id": RUN_ID,
        "lane_id": LANE_ID,
        "fixture_id": fixture_id,
        "runtime_family": "experiment_local",
        "native_lgrc9v3_e3_pulse_used": False,
        "native_grc9v3_proposal_flux_control_used": False,
        "claim_ceiling": "M2_identity_preserving_displacement_evidence_only",
        "metric_thresholds": thresholds,
        "metrics": metrics_out,
        "observables": obs,
        "classifier_input": item,
        "classification": result,
        "timeseries": timeseries,
        "checks": checks,
        "notes": [
            "Iteration 11-B unblocks M2 as a runtime timeseries visual reference.",
            "The lane is intentionally shape-blocked by profile similarity, so it does not promote to M3.",
            "This is experiment-local N04 evidence, not native LGRC telemetry.",
            "Movement and broader claim flags remain blocked.",
        ],
        "command": COMMAND,
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "git_diff_check": _run_git(["diff", "--check"]),
        },
    }
    return payload


def main() -> None:
    payload = build_report()
    _write_json(OUTPUT_PATH, payload)
    _write_report(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "movement_level": payload["classification"]["movement_level"],
                "timeseries": payload["timeseries"]["path"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
