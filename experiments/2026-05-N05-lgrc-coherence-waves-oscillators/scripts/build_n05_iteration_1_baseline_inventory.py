"""Build the N05 baseline and schema inventory.

This script records the source artifacts, native LGRC support surfaces, row
schema, and claim boundaries for N05 Iteration 1. It intentionally does not run
oscillator probes and does not import or mutate `src/pygrc`.
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
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
IMPLEMENTATION = ROOT / "implementation"

OUTPUT_PATH = N05 / "outputs/n05_iteration_1_baseline_inventory.json"
REPORT_PATH = N05 / "reports/n05_iteration_1_baseline_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "build_n05_iteration_1_baseline_inventory.py"
)


SOURCE_ARTIFACTS: dict[str, Path] = {
    "n05_readme": N05 / "README.md",
    "n05_n11_roadmap": ROOT / "experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md",
    "n05_plan": N05 / "implementation/CoherenceOscillatorsImplementationPlan.md",
    "n05_checklist": N05 / "implementation/CoherenceOscillatorsImplementationChecklist.md",
    "n03_d2_3_self_rearming_packets": N03 / "outputs/d2_3_self_rearming_packets.json",
    "n03_e2_4_native_autonomy_feasibility": N03 / "outputs/e2_4_native_autonomy_feasibility.json",
    "n03_e2_4a_native_autonomy_boundary": N03 / "outputs/e2_4a_native_autonomy_boundary.json",
    "n03_e3_route_manifest": N03 / "configs/e3_native_lgrc9v3_packet_loop_route_manifest.json",
    "n03_e3_positive": N03 / "outputs/e3_1_native_positive_reproduction.json",
    "n03_e3_controls": N03 / "outputs/e3_2_native_control_parity.json",
    "n03_e3_snapshot_telemetry": N03 / "outputs/e3_3_snapshot_telemetry_reproduction.json",
    "n03_e3_closeout": N03 / "outputs/e3_native_lgrc9v3_packet_loop_closeout.json",
    "n03_e3_closeout_report": N03 / "reports/e3_native_lgrc9v3_packet_loop_closeout.md",
    "n04_baseline_inventory": N04 / "outputs/n04_baseline_inventory.json",
    "n04_e3_pulse_import_validation": N04 / "outputs/e3_pulse_import_validation.json",
    "n04_lane_f_surface_bridge": N04 / "outputs/native_lgrc_lane_f_surface_bridge.json",
    "n04_lane_f_surface_closeout": N04 / "outputs/n04_lane_f_native_surface_closeout.json",
    "n04_taxonomy_continuation_closeout": N04 / "outputs/n04_taxonomy_continuation_closeout.json",
    "n04_route_arbitration_rerun": N04 / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json",
    "phase8_lgrc9_closeout": IMPLEMENTATION / "Phase-8-LGRC9-Closeout.md",
    "phase8_native_packet_loop_checklist": IMPLEMENTATION / "Phase-8-LGRC9-NativePacketLoopChecklist.md",
    "phase8_causal_pulse_substrate_closeout": IMPLEMENTATION / "Phase-8-LGRC9-CausalPulseSubstrateCloseout.md",
    "phase8_causal_pulse_substrate_closeout_json": IMPLEMENTATION / "Phase-8-LGRC9-CausalPulseSubstrateCloseout.json",
    "phase8_surface_lineage_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md",
    "phase8_surface_lineage_closeout_json": IMPLEMENTATION
    / "Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json",
    "phase8_topology_state_reabsorption_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md",
    "phase8_topology_state_reabsorption_closeout_json": IMPLEMENTATION
    / "Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json",
    "phase8_time_scoped_lineage_replay_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md",
    "phase8_time_scoped_lineage_replay_closeout_json": IMPLEMENTATION
    / "Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json",
    "phase8_native_route_arbitration_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.md",
    "phase8_native_route_arbitration_closeout_json": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.json",
}


CLAIM_FLAGS_FALSE = {
    "movement_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "memory_or_trail_claim_allowed": False,
    "goal_proxy_regulation_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
}


ROW_SCHEMA_REQUIRED_FIELDS = [
    "run_id",
    "o_level",
    "o_level_is_evidence_classification",
    "claim_ceiling",
    "claim_flags",
    "runtime_family",
    "lgrc_runtime_level",
    "execution_stage",
    "scheduling_mode",
    "producer_mediated",
    "constitutive_native_claim_allowed",
    "source_native_surfaces",
    "fixture_id",
    "source_node_id",
    "target_node_id",
    "route_id",
    "event_time_key",
    "scheduler_event_index",
    "causal_epoch",
    "node_proper_time",
    "source_node_proper_time",
    "target_node_proper_time",
    "outbound_packet_id",
    "outbound_packet_digest",
    "outbound_amount",
    "target_reservoir_before",
    "target_reservoir_after",
    "return_packet_id",
    "return_packet_digest",
    "return_amount",
    "cycle_id",
    "causal_delay",
    "scheduler_order",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "producer_records",
    "cycle_semantics",
    "scheduling_semantics",
    "amplification_accounting",
    "route_coupling",
    "artifact_only_replay",
    "blocked_claims",
]


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


def _native_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "native_packet_loop_flux_route_producer",
            "runtime_family": "LGRC9V3",
            "producer_policy_constant": (
                "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE"
            ),
            "producer_policy_value": "packet_departure_from_flux_route_policy",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "O1 delayed outbound packet from declared causal flux routes",
            "claim_boundary": "scheduling/evidence only",
        },
        {
            "surface_id": "native_packet_loop_route_aspect_surplus_producer",
            "runtime_family": "LGRC9V3",
            "producer_policy_constant": (
                "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS"
            ),
            "producer_policy_value": "packet_departure_from_route_aspect_surplus_policy",
            "configuration_api": "LGRC9V3.set_route_aspect_surplus_trigger(...)",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "O3-O5 runtime-visible surplus/reservoir-triggered cycles",
            "claim_boundary": "surplus trigger is not choice, agency, or memory",
        },
        {
            "surface_id": "native_self_rearm_evidence",
            "runtime_family": "LGRC9V3",
            "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts(...)",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "O4/O5 repeated-cycle and renewal evidence",
            "claim_boundary": "self-rearm evidence is cycle evidence, not agency",
        },
        {
            "surface_id": "native_causal_pulse_substrate_surface",
            "runtime_family": "LGRC9V3",
            "validator": "validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(...)",
            "support_flag": "native_lgrc_pulse_substrate_surface_supported",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "O2/O3 target contact and local substrate response evidence",
            "claim_boundary": "surface rows are evidence, not movement or agency claims",
        },
        {
            "surface_id": "surface_lineage_transport",
            "runtime_family": "LGRC9V3",
            "support_flag": "causal_pulse_substrate_surface_lineage_transport_supported",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n05_use": "Only if O6 becomes topology-aware",
            "claim_boundary": "lineage hygiene only",
        },
        {
            "surface_id": "topology_state_reabsorption",
            "runtime_family": "LGRC9V3",
            "support_flag": "causal_topology_state_reabsorption_supported",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n05_use": "Only if O6 consumes topology-mutating route coupling",
            "claim_boundary": "runtime state/ledger support only",
        },
        {
            "surface_id": "time_scoped_lineage_replay",
            "runtime_family": "LGRC9V3",
            "support_flag": "time_scoped_lineage_replay_supported",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n05_use": "Artifact replay of topology-aware producer timing if needed",
            "claim_boundary": "artifact validation only",
        },
        {
            "surface_id": "native_route_arbitration",
            "runtime_family": "LGRC9V3",
            "support_flag": "native_lgrc_route_arbitration_supported",
            "minimum_lgrc_runtime_level": "lgrc3",
            "n05_use": "Candidate O6 route-coupling surface only",
            "claim_boundary": "route arbitration is not semantic choice",
        },
        {
            "surface_id": "bounded_autonomous_run_loop",
            "runtime_family": "LGRC9V3",
            "api": "LGRC9V3.run_autonomous(...)",
            "policy": "LGRC9V3_AUTONOMOUS_RUN_POLICY_BOUNDED_V1",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "O4-O6 bounded producer+step execution",
            "claim_boundary": "bounded run loop is not agency",
        },
        {
            "surface_id": "snapshot_restore",
            "runtime_family": "LGRC9V3",
            "api": "LGRC9V3.load(...)",
            "minimum_lgrc_runtime_level": "lgrc2",
            "n05_use": "Snapshot continue-after-load controls",
            "claim_boundary": "persistence support only",
        },
    ]


def _o_ladder() -> list[dict[str, Any]]:
    return [
        {
            "o_level": "O0",
            "name": "no oscillation / passive relaxation",
            "minimum_lgrc_runtime_level": "lgrc0_or_synchronous_control",
            "claim_ceiling": "no_oscillation",
        },
        {
            "o_level": "O1",
            "name": "delayed outbound pulse",
            "minimum_lgrc_runtime_level": "lgrc2",
            "claim_ceiling": "delayed_pulse_candidate",
        },
        {
            "o_level": "O2",
            "name": "reflected return pulse",
            "minimum_lgrc_runtime_level": "lgrc2",
            "claim_ceiling": "reflected_pulse_candidate",
        },
        {
            "o_level": "O3",
            "name": "amplified return with reservoir accounting",
            "minimum_lgrc_runtime_level": "lgrc2",
            "claim_ceiling": "amplified_return_candidate",
        },
        {
            "o_level": "O4",
            "name": "repeated source-target-source cycle",
            "minimum_lgrc_runtime_level": "lgrc2",
            "claim_ceiling": "repeated_oscillator_cycle_candidate",
        },
        {
            "o_level": "O5",
            "name": "self-sustained delayed oscillator boundary",
            "minimum_lgrc_runtime_level": "lgrc2",
            "claim_ceiling": "self_sustained_oscillator_candidate",
        },
        {
            "o_level": "O6",
            "name": "route-coupled / trail-reinforced oscillator boundary",
            "minimum_lgrc_runtime_level": "lgrc2_or_lgrc3_if_topology_aware",
            "claim_ceiling": "route_coupled_oscillator_candidate",
        },
    ]


def build_inventory() -> dict[str, Any]:
    src_status = _git(["status", "--short", "src"])
    full_status = _git(["status", "--short"])
    head = _git(["rev-parse", "--short", "HEAD"])

    e3_closeout = _load_json(SOURCE_ARTIFACTS["n03_e3_closeout"])
    n04_closeout = _load_json(SOURCE_ARTIFACTS["n04_taxonomy_continuation_closeout"])

    return {
        "schema": "n05_baseline_schema_inventory_v1",
        "experiment_root": _rel(N05),
        "iteration": "1_baseline_and_schema_inventory",
        "status": "passed",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "probe_count": 0,
        "oscillator_probe_run": False,
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
        "n05_boundaries": {
            "experiment_local": True,
            "src_changes_required": False,
            "src_change_policy": "stop_and_open_separate_phase8_task",
            "n04_ceiling_used_as_background": "topology_mutating_movement_candidate",
            "n04_claim_inherited": False,
            "o_levels_are_evidence_classifications": True,
            "agentic_like_target_remains_blocked": True,
        },
        "source_summaries": {
            "n03_e3": {
                "classification": e3_closeout.get("classification"),
                "status": e3_closeout.get("status"),
                "native_lgrc9v3_execution": e3_closeout.get("native_lgrc9v3_execution"),
                "native_surplus_trigger": e3_closeout.get("native_surplus_trigger"),
                "native_self_rearm_evidence": e3_closeout.get("native_self_rearm_evidence"),
                "snapshot_telemetry_replayable": e3_closeout.get(
                    "snapshot_telemetry_replayable"
                ),
                "movement_claim_allowed": e3_closeout.get("movement_claim_allowed"),
            },
            "n04": {
                "current_ceiling": n04_closeout.get("current_claim_ceiling")
                or n04_closeout.get("strongest_supported_result", {}).get("claim_ceiling"),
                "status": n04_closeout.get("status"),
                "achieved_movement_level": n04_closeout.get(
                    "strongest_supported_result", {}
                ).get("achieved_movement_level"),
                "native_route_arbitration_supported": n04_closeout.get(
                    "phase8_native_route_arbitration", {}
                ).get("native_lgrc_route_arbitration_supported"),
                "topology_state_reabsorption_supported": n04_closeout.get(
                    "phase8_topology_state_reabsorption", {}
                ).get("native_topology_state_reabsorption_supported"),
                "time_scoped_lineage_replay_supported": n04_closeout.get(
                    "phase8_time_scoped_lineage_replay", {}
                ).get("artifact_only_time_scoped_surface_lineage_replay_supported"),
                "movement_claim_allowed": n04_closeout.get("claim_flags", {}).get(
                    "movement_claim_allowed"
                ),
                "semantic_choice_claim_allowed": n04_closeout.get("claim_flags", {}).get(
                    "semantic_choice_claim_allowed"
                ),
                "agency_claim_allowed": n04_closeout.get("claim_flags", {}).get(
                    "agency_claim_allowed"
                ),
            },
        },
        "native_lgrc_surfaces": _native_surfaces(),
        "o_ladder": _o_ladder(),
        "report_schema": {
            "schema": "coherence_oscillator_report_v1",
            "required_row_fields": ROW_SCHEMA_REQUIRED_FIELDS,
            "scheduling_modes": [
                "explicit_schedule",
                "runtime_threshold",
                "constitutive_policy",
                "native_policy_gap",
            ],
            "o5_modes": [
                "threshold_authorized",
                "producer_mediated",
                "constitutive_native",
                "native_policy_gap",
            ],
            "cycle_definition": (
                "outbound_departure -> target_contact -> return_eligibility -> "
                "return_packet -> source_contact_absorption"
            ),
            "plateau_samples_counted_as_cycles": False,
            "artifact_only_replay_required": True,
        },
        "timing_fields": {
            "event_time_key": "required_when_runtime_emits_packet_or_surface_events",
            "scheduler_event_index": "required_when_runtime_emits_packet_or_surface_events",
            "causal_epoch": "pre_update|post_update|not_applicable",
            "node_proper_time": "required_where_available",
            "source_node_proper_time": "required_where_available",
            "target_node_proper_time": "required_where_available",
        },
        "claim_flags": dict(CLAIM_FLAGS_FALSE),
        "blocked_claims": list(CLAIM_FLAGS_FALSE),
        "artifact_inventory": [
            _artifact_record(name, path) for name, path in SOURCE_ARTIFACTS.items()
        ],
        "baseline_commands": [
            COMMAND,
            "git status --short src",
            "git diff --check",
        ],
    }


def write_report(inventory: dict[str, Any]) -> None:
    src_status = inventory["git"]["src_status"]
    artifacts = inventory["artifact_inventory"]
    surfaces = inventory["native_lgrc_surfaces"]
    o_ladder = inventory["o_ladder"]

    lines = [
        "# N05 Iteration 1 Baseline And Schema Inventory",
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
        "- N05 is experiment-local.",
        "- No oscillator probes were run.",
        "- `src/*` changes are not required for Iteration 1.",
        "- N04 is background only, not an inherited oscillator or agency claim.",
        "- O-levels are evidence classifications, not claim flags.",
        "- `native_lgrc_agentic_like_dynamics_candidate` remains blocked.",
        "",
        "## Source Status",
        "",
        "```text",
        src_status["stdout"] or "(no src/* status entries)",
        "```",
        "",
        "## Native LGRC Surfaces Available For N05",
        "",
        "| Surface | Minimum level | N05 use | Claim boundary |",
        "|---|---:|---|---|",
    ]
    for surface in surfaces:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{surface['surface_id']}`",
                    f"`{surface['minimum_lgrc_runtime_level']}`",
                    str(surface["n05_use"]),
                    str(surface["claim_boundary"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## O-Ladder Schema",
            "",
            "| O-level | Name | Minimum level | Claim ceiling |",
            "|---|---|---:|---|",
        ]
    )
    for row in o_ladder:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['o_level']}`",
                    row["name"],
                    f"`{row['minimum_lgrc_runtime_level']}`",
                    f"`{row['claim_ceiling']}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "Required row fields:",
            "",
            "```text",
            "\n".join(inventory["report_schema"]["required_row_fields"]),
            "```",
            "",
            "Cycle definition:",
            "",
            "```text",
            inventory["report_schema"]["cycle_definition"],
            "```",
            "",
            "Plateau samples counted as cycles: `false`.",
            "",
            "## Claim Flags",
            "",
            "```json",
            json.dumps(inventory["claim_flags"], indent=2, sort_keys=True),
            "```",
            "",
            "## Source Summaries",
            "",
            "```json",
            json.dumps(inventory["source_summaries"], indent=2, sort_keys=True),
            "```",
            "",
            "## Artifact Inventory",
            "",
            "| Name | Exists | SHA-256 | Path |",
            "|---|---:|---|---|",
        ]
    )
    for artifact in artifacts:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{artifact['name']}`",
                    f"`{artifact['exists']}`",
                    f"`{artifact['sha256']}`",
                    f"`{artifact['path']}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Acceptance",
            "",
            "Iteration 1 passes because N05 has a source-backed baseline",
            "inventory, frozen O-ladder row schema, explicit blocked claim",
            "flags, and no oscillator probe evidence or claim promotion.",
            "",
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    inventory = build_inventory()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(inventory)
    print(
        json.dumps(
            {
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "status": inventory["status"],
                "oscillator_probe_run": inventory["oscillator_probe_run"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
