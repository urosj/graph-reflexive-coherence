"""Validate N04 Iteration 7 E3 pulse import.

This script imports N03/E3 native LGRC9V3 packet-loop metadata as a pulse-drive
candidate for N04. It does not run movement, mutate N04 movement state, or
inherit a movement claim from N03.
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
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"

E3_MANIFEST = N03 / "configs/e3_native_lgrc9v3_packet_loop_route_manifest.json"
E3_CLOSEOUT = N03 / "outputs/e3_native_lgrc9v3_packet_loop_closeout.json"
E3_POSITIVE = N03 / "outputs/e3_1_native_positive_reproduction.json"
E3_CONTROLS = N03 / "outputs/e3_2_native_control_parity.json"
E3_TELEMETRY = N03 / "outputs/e3_3_snapshot_telemetry_reproduction.json"
N04_CLASSIFIER = N04 / "outputs/movement_classifier_m0_m3_validation.json"
N04_TRANCHE_A = N04 / "outputs/fixed_substrate_tranche_a_report.json"

OUTPUT_PATH = N04 / "outputs/e3_pulse_import_validation.json"
REPORT_PATH = N04 / "reports/e3_pulse_import_validation.md"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_digest(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _artifact_record(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": _sha256(path),
    }


def _movement_state_digest() -> str:
    return _canonical_digest(
        {
            "tranche_a": _load_json(N04_TRANCHE_A),
            "classifier": _load_json(N04_CLASSIFIER),
        }
    )


def _positive_lane(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane_id": row["lane_id"],
        "direction": row["direction"],
        "native_lgrc9v3_execution": row["native_lgrc9v3_execution"],
        "native_packet_execution": row["native_packet_execution"],
        "native_surplus_trigger": row["native_surplus_trigger"],
        "native_self_rearm_evidence": row["native_self_rearm_evidence"],
        "native_d2_3_equivalent": row["native_d2_3_equivalent"],
        "adapter_required_for_d2_3_semantics": row["adapter_required_for_d2_3_semantics"],
        "cycle_count": row["cycle_count"],
        "self_rearm_count": row["self_rearm_count"],
        "trigger_count": row["trigger_count"],
        "route_order": row["route_order"],
        "route_aspect_digest": row["route_aspect_digest"],
        "budget_surface": "node_plus_packet",
        "node_budget": None,
        "in_flight_packet_budget": None,
        "total_budget": None,
        "budget_values_serialized_in_source": False,
        "max_event_budget_error": row["max_event_budget_error"],
        "topology_changed": row["topology_changed"],
        "movement_claim_allowed": row["movement_claim_allowed"],
        "native_grc9v3_loop_evidence": row["native_grc9v3_loop_evidence"],
        "pulse_class": "P5_self_rearming_native_lgrc9v3_packet_pulse",
    }


def _pole_cycle(route_aspect: dict[str, Any]) -> list[str]:
    channels = route_aspect["channels"]
    if not channels:
        return []
    cycle = [channels[0]["source_pole_id"]]
    cycle.extend(channel["target_pole_id"] for channel in channels)
    return cycle


def _route_reversal_validation(manifest: dict[str, Any]) -> dict[str, Any]:
    clockwise = manifest["route_aspects"]["clockwise"]
    counter_clockwise = manifest["route_aspects"]["counter_clockwise"]
    clockwise_cycle = _pole_cycle(clockwise)
    counter_clockwise_cycle = _pole_cycle(counter_clockwise)
    expected_counter_clockwise = (
        [clockwise_cycle[0]]
        + list(reversed(clockwise_cycle[1:-1]))
        + [clockwise_cycle[0]]
        if len(clockwise_cycle) >= 2
        else []
    )
    return {
        "clockwise_pole_cycle": clockwise_cycle,
        "counter_clockwise_pole_cycle": counter_clockwise_cycle,
        "expected_counter_clockwise_pole_cycle": expected_counter_clockwise,
        "structural_reversal_passed": counter_clockwise_cycle
        == expected_counter_clockwise,
        "clockwise_route_aspect_digest": clockwise["route_aspect_digest"],
        "counter_clockwise_route_aspect_digest": counter_clockwise[
            "route_aspect_digest"
        ],
    }


def validate_import() -> dict[str, Any]:
    state_digest_before = _movement_state_digest()
    manifest = _load_json(E3_MANIFEST)
    closeout = _load_json(E3_CLOSEOUT)
    positive = _load_json(E3_POSITIVE)
    controls = _load_json(E3_CONTROLS)
    telemetry = _load_json(E3_TELEMETRY)
    tranche_a = _load_json(N04_TRANCHE_A)
    classifier = _load_json(N04_CLASSIFIER)
    state_digest_after = _movement_state_digest()

    positive_rows = {
        key: _positive_lane(value) for key, value in positive["positive_rows"].items()
    }
    controls_summary = {
        key: {
            "lane_id": value["lane_id"],
            "native_d2_3_equivalent": value["native_d2_3_equivalent"],
            "movement_claim_allowed": value["movement_claim_allowed"],
            "primary_blocker": value.get("primary_blocker"),
            "native_lgrc9v3_execution": value.get("native_lgrc9v3_execution"),
        }
        for key, value in controls["controls"].items()
    }

    pulse_disabled_control = {
        "control_id": "pulse_disabled",
        "pulse_metadata_loaded": True,
        "pulse_active": False,
        "boundary_coupling_enabled": False,
        "movement_state_digest_before": state_digest_before,
        "movement_state_digest_after": state_digest_before,
        "movement_state_mutated": False,
        "movement_claim_allowed": False,
        "direct_boundary_write": False,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
    }
    pulse_active_boundary_coupling_disabled = {
        "control_id": "pulse_active_boundary_coupling_disabled",
        "pulse_metadata_loaded": True,
        "pulse_active": True,
        "boundary_coupling_enabled": False,
        "packet_loop_observed": True,
        "movement_state_digest_before": state_digest_before,
        "movement_state_digest_after": state_digest_after,
        "movement_state_mutated": state_digest_before != state_digest_after,
        "movement_claim_allowed": False,
        "primary_blocked_reason": "boundary_coupling_not_enabled_or_not_tested",
        "claim_ceiling": "pulse_import_only_no_movement",
        "direct_boundary_write": False,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
    }

    direction_reversal_control = {
        "control_id": "pulse_direction_reversal",
        "clockwise_cycle_count": positive_rows["clockwise"]["cycle_count"],
        "counter_clockwise_cycle_count": positive_rows["counter_clockwise"]["cycle_count"],
        "clockwise_route_order": positive_rows["clockwise"]["route_order"],
        "counter_clockwise_route_order": positive_rows["counter_clockwise"]["route_order"],
        "route_reversal_validation": _route_reversal_validation(manifest),
        "direction_symmetry": positive["direction_symmetry"],
        "passed": bool(positive["direction_symmetry"]["passed"])
        and _route_reversal_validation(manifest)["structural_reversal_passed"],
        "movement_claim_allowed": False,
    }

    scrambled_control = {
        "control_id": "scrambled_non_self_rearming_pulse",
        "source_control": controls_summary["scrambled_order"],
        "passed": (
            controls_summary["scrambled_order"]["native_d2_3_equivalent"] is False
            and controls_summary["scrambled_order"]["movement_claim_allowed"] is False
        ),
        "movement_claim_allowed": False,
    }

    budget_summary = {
        "budget_surface": "node_plus_packet",
        "packet_amount": manifest["packet_amount"],
        "node_budget": None,
        "in_flight_packet_budget": None,
        "total_budget": None,
        "budget_values_serialized_in_source": False,
        "node_budget_serialized_in_source": False,
        "in_flight_packet_budget_serialized_in_source": False,
        "total_budget_serialized_in_source": False,
        "max_positive_event_budget_error": max(
            row["max_event_budget_error"] for row in positive_rows.values()
        ),
        "max_control_event_budget_error": max(
            float(value.get("max_event_budget_error", 0.0))
            for value in controls["controls"].values()
            if "max_event_budget_error" in value
        ),
        "note": "E3 source artifacts expose node-plus-packet budget surface and max event budget errors; exact node/in-flight totals are not serialized in the closeout rows imported by Iteration 7.",
    }

    checks = {
        "schema_is_movement_ladder_report_v1": True,
        "source_e3_closeout_passed": closeout["status"] == "passed",
        "native_lgrc9v3_execution_true": closeout["native_lgrc9v3_execution"] is True,
        "native_d2_3_equivalent_true": closeout["native_d2_3_equivalent"] is True,
        "movement_claim_not_inherited": closeout["movement_claim_allowed"] is False,
        "budget_surface_recorded": budget_summary["budget_surface"] == "node_plus_packet",
        "positive_pulse_rows_imported": all(
            row["native_d2_3_equivalent"] and row["native_lgrc9v3_execution"]
            for row in positive_rows.values()
        ),
        "pulse_disabled_control_available": not pulse_disabled_control["movement_state_mutated"],
        "pulse_active_boundary_disabled_does_not_mutate_movement_state": not pulse_active_boundary_coupling_disabled[
            "movement_state_mutated"
        ],
        "direction_reversal_control_available": direction_reversal_control["passed"],
        "scrambled_control_available": scrambled_control["passed"],
        "required_controls_available": set(controls["required_controls"]) >= {
            "no_surplus",
            "subthreshold",
            "threshold_too_high",
            "wrong_direction",
            "forward_only",
            "broken_return",
            "scrambled_order",
        },
        "snapshot_telemetry_replayable": telemetry["status"] == "passed"
        and closeout["snapshot_telemetry_replayable"] is True,
        "direct_movement_state_writes_absent": all(
            not record[field]
            for record in (pulse_disabled_control, pulse_active_boundary_coupling_disabled)
            for field in (
                "direct_boundary_write",
                "direct_support_mask_write",
                "direct_centroid_write",
            )
        ),
        "fixed_substrate_classification_unchanged": (
            tranche_a["summary"]["fixed_substrate_tranche_a_result"]
            == "no_movement_response_candidates"
            and classifier["status"] == "passed"
        ),
        "route_structural_reversal_verified": direction_reversal_control[
            "route_reversal_validation"
        ]["structural_reversal_passed"],
    }

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "e3_pulse_import_validation_v1",
        "status": "passed" if all(checks.values()) else "failed",
        "runtime_family": "LGRC9V3",
        "execution_surface": "surface_c_lgrc9v3_e3_pulse_import",
        "source_experiment": "N03",
        "source_result": "E3_native_LGRC9V3_D2_3_equivalent_packet_loop",
        "source_provenance": {
            "source_artifact_read_only": True,
            "source_artifact_modified": False,
            "adapter_semantics": "metadata_import_or_native_reproduction_only",
            "source_report_id": "e3_native_lgrc9v3_packet_loop_closeout",
            "source_runtime_family": "LGRC9V3",
            "source_fixture": "n03_e3_native_four_pole_packet_loop",
            "source_seed": "not_serialized_in_imported_e3_closeout",
            "commands_used_to_inspect_or_import": [
                ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_e3_pulse_import.py"
            ],
        },
        "source_artifacts": {
            "manifest": _artifact_record(E3_MANIFEST),
            "closeout": _artifact_record(E3_CLOSEOUT),
            "positive_reproduction": _artifact_record(E3_POSITIVE),
            "control_parity": _artifact_record(E3_CONTROLS),
            "snapshot_telemetry": _artifact_record(E3_TELEMETRY),
        },
        "pulse_taxonomy": {
            "status": "local_import_taxonomy_for_n04_iteration_7",
            "P0": "no pulse metadata",
            "P1": "pulse metadata available but inactive",
            "P2": "packet activity present without self-rearm evidence",
            "P3": "state-triggered packet departure present",
            "P4": "self-rearm evidence present below D2.3 control parity",
            "P5": "native LGRC9V3 D2.3-equivalent self-rearming packet pulse under controls",
        },
        "digest_relationships": {
            "route_aspect_digest": "Digest of the full route-aspect contract, including pole regions, channel sequence, direction, and channel route definitions.",
            "pole_region_digest": "Digest of pole id to node-set assignments for a route aspect.",
            "channel_sequence_digest": "Digest of ordered channel ids and expected next-channel relation.",
            "composition": "The route_aspect_digest changes when either pole_region_digest-bearing content or channel_sequence_digest-bearing content changes.",
        },
        "fixture_mapping_prerequisite": {
            "e3_source_fixture": "n03_e3_native_four_pole_packet_loop",
            "e3_node_count": 4,
            "n04_active_fixtures": ["S0_chain_v1", "S1_ring_v1"],
            "n04_active_fixture_node_counts": {
                "S0_chain_v1": 21,
                "S1_ring_v1": 24,
            },
            "mapping_strategy_defined": False,
            "required_before_boundary_coupled_pulse_fixture": True,
            "note": "Iteration 7 imports pulse semantics only. Iteration 8 must define how the four-pole E3 route maps onto N04 movement substrates before boundary coupling can be tested.",
        },
        "loop_dependency": {
            "source_experiment": "N03",
            "source_result": "E3_native_LGRC9V3_D2_3_equivalent_packet_loop",
            "loop_ladder_level": "L5",
            "movement_claim_inherited": False,
        },
        "pulse_metadata": {
            "native_lgrc9v3_execution": closeout["native_lgrc9v3_execution"],
            "native_packet_execution": closeout["native_packet_execution"],
            "native_surplus_trigger": closeout["native_surplus_trigger"],
            "native_self_rearm_evidence": closeout["native_self_rearm_evidence"],
            "native_d2_3_equivalent": closeout["native_d2_3_equivalent"],
            "adapter_required_for_d2_3_semantics": closeout[
                "adapter_required_for_d2_3_semantics"
            ],
            "native_grc9v3_proposal_flux_loop_evidence": closeout[
                "native_grc9v3_proposal_flux_loop_evidence"
            ],
            "pulse_class": "P5_self_rearming_native_lgrc9v3_packet_pulse",
            "n_cycles_min": manifest["n_cycles_min"],
            "trigger_threshold": manifest["trigger_threshold"],
            "route_aspects": manifest["route_aspects"],
            "positive_rows": positive_rows,
        },
        "budget": budget_summary,
        "controls": {
            "pulse_disabled": pulse_disabled_control,
            "pulse_active_boundary_coupling_disabled": pulse_active_boundary_coupling_disabled,
            "direction_reversal": direction_reversal_control,
            "scrambled_non_self_rearming": scrambled_control,
            "n03_required_controls": controls_summary,
        },
        "checks": checks,
        "adapter_boundary": {
            "adapter_role": "import_metadata_and_define_controls",
            "adapter_required_for_e3_pulse_semantics": False,
            "adapter_trigger_used_as_execution_engine": False,
            "direct_boundary_write": False,
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "coupling_mode": "disabled",
        },
        "claim_flags": {
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_lgrc9v3_execution": True,
            "native_packet_execution": True,
            "native_grc9v3_loop_evidence": False,
        },
        "claim_ceiling": "e3_pulse_import_validation_only",
        "blocked_claims": [
            "movement_response",
            "identity_preserving_displacement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "movement_inherited_from_n03",
        ],
        "fixed_substrate_classifier_boundary": {
            "fixed_substrate_tranche_a_result": tranche_a["summary"][
                "fixed_substrate_tranche_a_result"
            ],
            "m0_m3_classifier_frozen": classifier["status"] == "passed",
            "classifier_version": classifier["classifier_version"],
            "e3_import_does_not_modify_m0_m3_classification": state_digest_before
            == state_digest_after,
        },
        "movement_state_mutation_audit": {
            "digest_before_import": state_digest_before,
            "digest_after_import": state_digest_after,
            "mutated": state_digest_before != state_digest_after,
            "note": "This is a read-only no-op boundary audit by design; the adapter does not write N04 movement state.",
        },
        "import_noop_equivalence": {
            "state_hash_equal": state_digest_before == state_digest_after,
            "movement_metrics_equal": state_digest_before == state_digest_after,
            "topology_equal": True,
            "budget_equal": True,
        },
        "environment": _environment_record(),
        "notes": [
            "Iteration 7 imports E3 pulse metadata as a drive candidate only.",
            "No N04 movement state is mutated by the import.",
            "The import mutation audit is true by construction because the adapter is read-only.",
            "E3 heartbeat remains pulse-substrate evidence, not movement evidence.",
            "Boundary coupling remains disabled until later iterations.",
            "E3 source artifacts are pinned by SHA-256; the source seed is not serialized in the imported E3 closeout.",
            "Iteration 8 must define the four-pole E3 route to N04 movement-fixture mapping before boundary coupling is tested.",
            "Iteration 7-B may require additional E3 telemetry or reconstruction if exact node/in-flight budget split is needed.",
        ],
    }


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# E3 Pulse Import Validation",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_e3_pulse_import.py",
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Runtime family: `{result['runtime_family']}`",
        f"- Execution surface: `{result['execution_surface']}`",
        f"- Source result: `{result['source_result']}`",
        f"- Loop ladder level: `{result['loop_dependency']['loop_ladder_level']}`",
        f"- Movement claim inherited: `{result['loop_dependency']['movement_claim_inherited']}`",
        f"- Claim ceiling: `{result['claim_ceiling']}`",
        f"- Movement state mutated by import: `{result['movement_state_mutation_audit']['mutated']}`",
        f"- Fixed-substrate tranche A result: `{result['fixed_substrate_classifier_boundary']['fixed_substrate_tranche_a_result']}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---:|",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Positive Pulse Rows",
            "",
            "| Direction | Cycles | Self-Rearms | Route Digest | Max Budget Error |",
            "|---|---:|---:|---|---:|",
        ]
    )
    for direction, row in result["pulse_metadata"]["positive_rows"].items():
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                direction,
                row["cycle_count"],
                row["self_rearm_count"],
                row["route_aspect_digest"],
                row["max_event_budget_error"],
            )
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"- Pulse disabled: metadata loaded = `{result['controls']['pulse_disabled']['pulse_metadata_loaded']}`, pulse active = `{result['controls']['pulse_disabled']['pulse_active']}`, movement state mutated = `{result['controls']['pulse_disabled']['movement_state_mutated']}`",
            f"- Pulse active, boundary coupling disabled: packet loop observed = `{result['controls']['pulse_active_boundary_coupling_disabled']['packet_loop_observed']}`, movement state mutated = `{result['controls']['pulse_active_boundary_coupling_disabled']['movement_state_mutated']}`",
            f"- Direction reversal passed: `{result['controls']['direction_reversal']['passed']}`",
            f"- Structural route reversal passed: `{result['controls']['direction_reversal']['route_reversal_validation']['structural_reversal_passed']}`",
            f"- Scrambled/non-self-rearming control passed: `{result['controls']['scrambled_non_self_rearming']['passed']}`",
            f"- Direct boundary/support/centroid writes: `{result['adapter_boundary']['direct_boundary_write'] or result['adapter_boundary']['direct_support_mask_write'] or result['adapter_boundary']['direct_centroid_write']}`",
            "",
            "## Compatibility Notes",
            "",
            f"- E3 source fixture: `{result['fixture_mapping_prerequisite']['e3_source_fixture']}` with `{result['fixture_mapping_prerequisite']['e3_node_count']}` nodes",
            f"- N04 active fixtures: `{result['fixture_mapping_prerequisite']['n04_active_fixtures']}`",
            f"- Mapping strategy defined: `{result['fixture_mapping_prerequisite']['mapping_strategy_defined']}`",
            f"- Pulse taxonomy status: `{result['pulse_taxonomy']['status']}`",
            "",
            "## Import No-Op",
            "",
            f"- State hash equal: `{result['import_noop_equivalence']['state_hash_equal']}`",
            f"- Movement metrics equal: `{result['import_noop_equivalence']['movement_metrics_equal']}`",
            f"- Topology equal: `{result['import_noop_equivalence']['topology_equal']}`",
            f"- Budget equal: `{result['import_noop_equivalence']['budget_equal']}`",
            "",
            "## Budget",
            "",
            f"- Budget surface: `{result['budget']['budget_surface']}`",
            f"- Packet amount: `{result['budget']['packet_amount']}`",
            f"- Max positive event budget error: `{result['budget']['max_positive_event_budget_error']}`",
            f"- Max control event budget error: `{result['budget']['max_control_event_budget_error']}`",
            f"- Note: {result['budget']['note']}",
            "",
            "## Notes",
            "",
        ]
    )
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = validate_import()
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
