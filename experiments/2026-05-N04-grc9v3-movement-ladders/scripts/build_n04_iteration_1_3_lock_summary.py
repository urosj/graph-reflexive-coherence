"""Build the N04 Iterations 1-3 lock summary.

The lock summary freezes the handoff, fixture, lane, metric, initializer,
projection, coordinate, claim, and source-change boundaries before Iteration 4
adds movement observables.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
BASELINE_PATH = N04 / "outputs/n04_baseline_inventory.json"
MANIFEST_PATH = N04 / "configs/movement_fixture_manifest_v1.json"
FIXTURE_VALIDATION_PATH = N04 / "outputs/movement_fixture_manifest_validation.json"
INITIALIZER_VALIDATION_PATH = N04 / "outputs/movement_initializer_validation.json"
OUTPUT_PATH = N04 / "outputs/n04_iteration_1_3_lock_summary.json"
REPORT_PATH = N04 / "reports/n04_iteration_1_3_lock_summary.md"


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


def build_summary() -> dict[str, Any]:
    baseline = _load_json(BASELINE_PATH)
    manifest = _load_json(MANIFEST_PATH)
    fixture_validation = _load_json(FIXTURE_VALIDATION_PATH)
    initializer_validation = _load_json(INITIALIZER_VALIDATION_PATH)
    src_status = _git(["status", "--short", "src"])

    active_fixtures = [
        fixture_id
        for fixture_id, fixture in manifest["fixtures"].items()
        if fixture.get("status") != "deferred"
    ]
    deferred_fixtures = [
        fixture_id
        for fixture_id, fixture in manifest["fixtures"].items()
        if fixture.get("status") == "deferred"
    ]

    lock_flags = {
        "handoff_frozen": baseline["n03_e3_handoff"]["native_d2_3_equivalent"] is True
        and baseline["n03_e3_handoff"]["movement_claim_allowed"] is False,
        "fixtures_frozen": fixture_validation["status"] == "passed",
        "lanes_frozen": set(manifest["lanes"]) == {
            "U0",
            "B0",
            "B1",
            "B1_reversed",
            "K1",
            "K1_reversed",
        },
        "metric_defaults_frozen": set(manifest["metric_defaults"]) >= {
            "epsilon_budget",
            "configured_displacement_min",
            "null_calibration_k",
            "identity_mass_ratio_min",
            "width_relative_change_max",
            "profile_similarity_min",
        },
        "topology_policy_frozen": set(manifest.get("topology_policy", {})) >= {
            "fixed_substrate_required",
            "topology_changed_required",
            "topology_changed_allowed",
        },
        "initializer_formulas_frozen": initializer_validation["checks"]["formulas_serialized"],
        "projection_policy_frozen": initializer_validation["checks"]["projection_declared"],
        "coordinate_policy_frozen": all(
            "coordinate_policy" in manifest["fixtures"][fixture_id]
            for fixture_id in active_fixtures
        ),
        "claim_flags_frozen": baseline["n04_boundaries"]["movement_claim_inherited_from_n03"]
        is False,
        "src_unchanged": src_status["stdout"] == "",
        "topology_disabled": manifest["topology_events_enabled"] is False,
    }

    return {
        "schema": "n04_iteration_1_3_lock_summary_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            ".venv/bin/python "
            "experiments/2026-05-N04-grc9v3-movement-ladders/scripts/"
            "build_n04_iteration_1_3_lock_summary.py"
        ),
        "status": "passed" if all(lock_flags.values()) else "failed",
        "lock_flags": lock_flags,
        "active_fixtures": active_fixtures,
        "deferred_fixtures": deferred_fixtures,
        "lane_names": sorted(manifest["lanes"]),
        "metric_defaults": manifest["metric_defaults"],
        "topology_policy": manifest["topology_policy"],
        "null_displacement_envelope": manifest["null_displacement_envelope"],
        "initializer_defaults": manifest["initializer_defaults"],
        "initializer_formulas": manifest["initializer_formulas"],
        "projection_policy": "conserved_nonnegative_simplex",
        "coordinate_policies": {
            fixture_id: manifest["fixtures"][fixture_id]["coordinate_policy"]
            for fixture_id in active_fixtures
        },
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
        },
        "src_status": src_status,
        "input_artifacts": {
            "baseline_inventory": BASELINE_PATH.relative_to(ROOT).as_posix(),
            "fixture_manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "fixture_validation": FIXTURE_VALIDATION_PATH.relative_to(ROOT).as_posix(),
            "initializer_validation": INITIALIZER_VALIDATION_PATH.relative_to(ROOT).as_posix(),
        },
    }


def write_report(summary: dict[str, Any]) -> None:
    lines = [
        "# N04 Iterations 1-3 Lock Summary",
        "",
        "Command:",
        "",
        "```bash",
        summary["command"],
        "```",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Lock Flags",
        "",
        "| Flag | Passed |",
        "|---|---:|",
    ]
    for key, value in summary["lock_flags"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Frozen Surfaces",
            "",
            f"- Active fixtures: `{summary['active_fixtures']}`",
            f"- Deferred fixtures: `{summary['deferred_fixtures']}`",
            f"- Lanes: `{summary['lane_names']}`",
            f"- Projection policy: `{summary['projection_policy']}`",
            f"- Null displacement calibrated: `{summary['null_displacement_envelope']['calibrated']}`",
            "- Strong movement claims remain blocked until null calibration and movement gates pass.",
            "",
            "## Source Status",
            "",
            "```text",
            summary["src_status"]["stdout"] or "(no src/* status entries)",
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    summary = build_summary()
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if summary["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
