"""Build the N04 movement-ladders baseline inventory.

This script records the N03/E3 handoff artifacts and the local execution
boundary for N04 Iteration 1. It intentionally does not import or mutate
`src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/n04_baseline_inventory.json"
REPORT_PATH = N04 / "reports/n04_baseline_inventory.md"


E3_ARTIFACTS = {
    "route_manifest": N03 / "configs/e3_native_lgrc9v3_packet_loop_route_manifest.json",
    "e3_0_baseline": N03 / "outputs/e3_0_dependency_and_fixture_baseline.json",
    "e3_1_positive": N03 / "outputs/e3_1_native_positive_reproduction.json",
    "e3_2_controls": N03 / "outputs/e3_2_native_control_parity.json",
    "e3_3_snapshot_telemetry": N03 / "outputs/e3_3_snapshot_telemetry_reproduction.json",
    "e3_closeout": N03 / "outputs/e3_native_lgrc9v3_packet_loop_closeout.json",
    "e3_visualization": N03 / "reports/e3_native_lgrc9v3_packet_loop_visualization.svg",
    "e3_animation_report": N03 / "reports/e3_native_lgrc9v3_packet_loop_animation.md",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data
    return {"value": data}


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


def _artifact_record(name: str, path: Path) -> dict[str, Any]:
    return {
        "name": name,
        "path": _rel(path),
        "exists": path.exists(),
        "sha256": _sha256(path),
    }


def build_inventory() -> dict[str, Any]:
    closeout = _load_json(E3_ARTIFACTS["e3_closeout"])
    e3_positive = _load_json(E3_ARTIFACTS["e3_1_positive"])
    route_manifest = _load_json(E3_ARTIFACTS["route_manifest"])
    src_status = _git(["status", "--short", "src"])
    full_status = _git(["status", "--short"])
    head = _git(["rev-parse", "--short", "HEAD"])

    positive_rows = e3_positive.get("positive_rows", {})
    clockwise = positive_rows.get("clockwise", {})
    counter_clockwise = positive_rows.get("counter_clockwise", {})

    return {
        "schema": "n04_baseline_inventory_v1",
        "experiment_root": "experiments/2026-05-N04-grc9v3-movement-ladders",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            ".venv/bin/python "
            "experiments/2026-05-N04-grc9v3-movement-ladders/scripts/"
            "build_n04_baseline_inventory.py"
        ),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "platform": platform.platform(),
        },
        "environment": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", ""),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "gpu_required": False,
        },
        "git": {
            "head": head,
            "src_status": src_status,
            "src_paths_modified": [
                line.strip()
                for line in src_status["stdout"].splitlines()
                if line.strip()
            ],
            "working_tree_status": full_status,
        },
        "n04_boundaries": {
            "experiment_local": True,
            "src_changes_required": False,
            "src_paths_modified": [],
            "src_change_policy": "stop_and_open_separate_core_task",
            "movement_claim_inherited_from_n03": False,
            "adaptive_topology_entry_allowed": False,
        },
        "n03_e3_handoff": {
            "classification": closeout.get("classification"),
            "status": closeout.get("status"),
            "loop_ladder_level_for_n04": "L5",
            "loop_ladder_level_interpretation": (
                "Native LGRC9V3 self-rearming packetized pulse substrate; "
                "movement remains unopened."
            ),
            "native_lgrc9v3_execution": closeout.get("native_lgrc9v3_execution"),
            "native_packet_execution": closeout.get("native_packet_execution"),
            "native_surplus_trigger": closeout.get("native_surplus_trigger"),
            "native_self_rearm_evidence": closeout.get("native_self_rearm_evidence"),
            "native_d2_3_equivalent": closeout.get("native_d2_3_equivalent"),
            "movement_claim_allowed": closeout.get("movement_claim_allowed"),
            "native_grc9v3_proposal_flux_loop_evidence": closeout.get(
                "native_grc9v3_proposal_flux_loop_evidence"
            ),
            "snapshot_telemetry_replayable": closeout.get("snapshot_telemetry_replayable"),
            "controls_passed": closeout.get("controls_passed"),
            "two_layer_result": closeout.get("two_layer_result"),
        },
        "e3_positive_summary": {
            "classification": e3_positive.get("classification"),
            "direction_symmetry": e3_positive.get("direction_symmetry"),
            "clockwise": {
                "cycle_count": clockwise.get("cycle_count"),
                "self_rearm_count": clockwise.get("self_rearm_count"),
                "trigger_count": clockwise.get("trigger_count"),
                "max_event_budget_error": clockwise.get("max_event_budget_error"),
                "topology_changed": clockwise.get("topology_changed"),
                "route_aspect_digest": clockwise.get("route_aspect_digest"),
            },
            "counter_clockwise": {
                "cycle_count": counter_clockwise.get("cycle_count"),
                "self_rearm_count": counter_clockwise.get("self_rearm_count"),
                "trigger_count": counter_clockwise.get("trigger_count"),
                "max_event_budget_error": counter_clockwise.get("max_event_budget_error"),
                "topology_changed": counter_clockwise.get("topology_changed"),
                "route_aspect_digest": counter_clockwise.get("route_aspect_digest"),
            },
        },
        "route_manifest_summary": {
            "manifest_id": route_manifest.get("manifest_id"),
            "execution_engine": route_manifest.get("execution_engine"),
            "n_cycles_min": route_manifest.get("n_cycles_min"),
            "packet_amount": route_manifest.get("packet_amount"),
            "claim_boundary": route_manifest.get("claim_boundary"),
            "route_aspect_ids": {
                key: value.get("route_aspect_id")
                for key, value in route_manifest.get("route_aspects", {}).items()
                if isinstance(value, dict)
            },
        },
        "artifact_inventory": [
            _artifact_record(name, path) for name, path in E3_ARTIFACTS.items()
        ],
        "runtime_surfaces": [
            {
                "surface_id": "surface_a_fixed_substrate_metrics",
                "runtime_family": "experiment_local",
                "purpose": "movement metrics, fixed-substrate nulls, classifier",
                "movement_claim_source": "N04 only",
            },
            {
                "surface_id": "surface_b_grc9v3_control",
                "runtime_family": "GRC9V3",
                "purpose": "proposal-flux control and negative comparison",
                "movement_claim_source": "N04 only",
            },
            {
                "surface_id": "surface_c_lgrc9v3_e3_pulse",
                "runtime_family": "LGRC9V3",
                "purpose": "native E3 pulse substrate for later P4/P5 lanes",
                "movement_claim_source": "N04 only; no inherited movement claim",
            },
        ],
        "baseline_commands": [
            (
                ".venv/bin/python "
                "experiments/2026-05-N04-grc9v3-movement-ladders/scripts/"
                "build_n04_baseline_inventory.py"
            ),
            "git status --short src",
            "git diff --check",
        ],
    }


def write_report(inventory: dict[str, Any]) -> None:
    handoff = inventory["n03_e3_handoff"]
    e3 = inventory["e3_positive_summary"]
    route = inventory["route_manifest_summary"]
    artifacts = inventory["artifact_inventory"]
    src_status = inventory["git"]["src_status"]

    lines = [
        "# N04 Baseline Inventory",
        "",
        f"Generated: `{inventory['generated_at_utc']}`",
        "",
        "Command:",
        "",
        "```bash",
        inventory["command"],
        "```",
        "",
        "## Boundary",
        "",
        "- N04 is experiment-local.",
        "- `src/*` changes are not required for Iteration 1.",
        "- N03/E3 supplies pulse-substrate evidence only.",
        "- Movement claims are not inherited from N03.",
        "- Adaptive topology remains blocked.",
        f"- Experiment root: `{inventory['experiment_root']}`",
        "",
        "## Source Status",
        "",
        "```text",
        src_status["stdout"] or "(no src/* status entries)",
        "```",
        "",
        "## Environment",
        "",
        f"- Python executable: `{inventory['python']['executable']}`",
        f"- Python version: `{inventory['python']['version']}`",
        f"- Platform: `{inventory['python']['platform']}`",
        f"- `PYTHONPATH`: `{inventory['environment']['PYTHONPATH']}`",
        f"- `VIRTUAL_ENV`: `{inventory['environment']['VIRTUAL_ENV']}`",
        f"- GPU required: `{inventory['environment']['gpu_required']}`",
        "",
        "## N03/E3 Handoff",
        "",
        f"- classification: `{handoff.get('classification')}`",
        f"- status: `{handoff.get('status')}`",
        f"- N04 input loop ladder level: `{handoff.get('loop_ladder_level_for_n04')}`",
        f"- loop level interpretation: `{handoff.get('loop_ladder_level_interpretation')}`",
        f"- native LGRC9V3 execution: `{handoff.get('native_lgrc9v3_execution')}`",
        f"- native packet execution: `{handoff.get('native_packet_execution')}`",
        f"- native surplus trigger: `{handoff.get('native_surplus_trigger')}`",
        f"- native self-rearm evidence: `{handoff.get('native_self_rearm_evidence')}`",
        f"- native D2.3 equivalent: `{handoff.get('native_d2_3_equivalent')}`",
        f"- movement claim allowed: `{handoff.get('movement_claim_allowed')}`",
        f"- native GRC9V3 proposal-flux loop evidence: "
        f"`{handoff.get('native_grc9v3_proposal_flux_loop_evidence')}`",
        f"- controls passed: `{handoff.get('controls_passed')}`",
        f"- snapshot/telemetry replayable: `{handoff.get('snapshot_telemetry_replayable')}`",
        "",
        "## E3 Positive Rows",
        "",
        f"- classification: `{e3.get('classification')}`",
        f"- direction symmetry: `{e3.get('direction_symmetry')}`",
        f"- clockwise: `{e3.get('clockwise')}`",
        f"- counter-clockwise: `{e3.get('counter_clockwise')}`",
        "",
        "## Route Manifest",
        "",
        f"- manifest id: `{route.get('manifest_id')}`",
        f"- execution engine: `{route.get('execution_engine')}`",
        f"- minimum cycles: `{route.get('n_cycles_min')}`",
        f"- packet amount: `{route.get('packet_amount')}`",
        f"- route aspects: `{route.get('route_aspect_ids')}`",
        "",
        "## Artifacts",
        "",
        "| Name | Exists | SHA-256 | Path |",
        "|---|---:|---|---|",
    ]
    for artifact in artifacts:
        lines.append(
            "| {name} | {exists} | `{sha}` | `{path}` |".format(
                name=artifact["name"],
                exists=artifact["exists"],
                sha=artifact["sha256"] or "",
                path=artifact["path"],
            )
        )
    lines.extend(
        [
            "",
            "## Baseline Commands",
            "",
        ]
    )
    for command in inventory["baseline_commands"]:
        lines.append(f"- `{command}`")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    OUTPUT_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(inventory)
    print(json.dumps({"status": "passed", "output": _rel(OUTPUT_PATH), "report": _rel(REPORT_PATH)}, sort_keys=True))


if __name__ == "__main__":
    main()
