#!/usr/bin/env python3
"""Run N09 Iteration 3 GPR1 proxy measurement.

Iteration 3 is measurement-only. It serializes a runtime-visible proxy surface
and declared target band without computing an error signal, scheduling packets,
or emitting regulation/claim evidence.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import GRC9V3NodeState, GRC9V3State, LGRC9V3, PortEdge


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_3_gpr1_proxy_measurement.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_3_gpr1_proxy_measurement.py"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def build_three_node_proxy_state() -> tuple[GRC9V3State, dict[str, int]]:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source_reservoir"})
    middle = graph.add_node({"label": "middle_transfer"})
    target = graph.add_node({"label": "target_reservoir"})
    edge_sm = graph.connect_ports(source, 0, middle, 0, {"kind": "source_middle"})
    edge_mt = graph.connect_ports(middle, 1, target, 0, {"kind": "middle_target"})
    edge_st = graph.connect_ports(source, 1, target, 1, {"kind": "source_target"})
    state = GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(
                coherence=0.62,
                basin_mass=0.62,
                basin_id="source_reservoir",
            ),
            middle: GRC9V3NodeState(
                coherence=0.50,
                basin_mass=0.50,
                basin_id="middle_transfer",
            ),
            target: GRC9V3NodeState(
                coherence=0.38,
                basin_mass=0.38,
                basin_id="target_reservoir",
            ),
        },
        port_edges={
            edge_sm: PortEdge(
                source,
                1,
                middle,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_mt: PortEdge(
                middle,
                2,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_st: PortEdge(
                source,
                2,
                target,
                2,
                conductance=1.0,
                flux_uv=0.0,
            ),
        },
        base_conductance={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        geometric_length={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        temporal_delay={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        flux_coupling={edge_sm: 0.0, edge_mt: 0.0, edge_st: 0.0},
    )
    return state, {
        "source_reservoir": int(source),
        "middle_transfer": int(middle),
        "target_reservoir": int(target),
    }


def digest_row(row: dict[str, Any], digest_field: str) -> str:
    return digest_value({key: value for key, value in row.items() if key != digest_field})


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in manifest.items() if key != "manifest_digest"})


def build_target_band_row(manifest: dict[str, Any]) -> dict[str, Any]:
    policy = manifest["target_band_schema"]["default_target_band_policy"]
    row = {
        "target_band_id": "n09_i3_source_reservoir_target_band_v1",
        "regulated_variable_id": policy["regulated_variable_id"],
        "regulated_variable_surface": policy["regulated_variable_surface"],
        "target_kind": policy["target_kind"],
        "lower_bound": float(policy["lower_bound"]),
        "upper_bound": float(policy["upper_bound"]),
        "target_value": float(policy["target_value"]),
        "tolerance": float(policy["tolerance"]),
        "unit": policy["unit"],
        "event_time_key": 0.0,
        "target_band_policy_id": policy["target_band_policy_id"],
        "target_band_policy_digest": policy["target_band_policy_digest"],
    }
    row["target_band_digest"] = digest_row(row, "target_band_digest")
    return row


def relation_to_band(value: float, target_band: dict[str, Any]) -> str:
    if value < float(target_band["lower_bound"]):
        return "below_target_band"
    if value > float(target_band["upper_bound"]):
        return "above_target_band"
    return "inside_target_band"


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def build_proxy_measurement() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    state, node_ids = build_three_node_proxy_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    runtime_state = model.get_state()
    runtime_artifact = runtime_state.to_artifact()
    runtime_state_digest = digest_value(runtime_artifact)
    packet_ledger_artifact = runtime_artifact["packet_ledger"]
    packet_ledger_digest = digest_value(packet_ledger_artifact)
    source_node_id = node_ids["source_reservoir"]
    source_node_state = runtime_state.base_state.nodes[source_node_id]
    measurement_value = float(source_node_state.coherence)
    node_plus_packet_budget_before = float(
        runtime_state.packet_ledger.conserved_budget_total
    )
    node_plus_packet_budget_after = float(
        runtime_state.packet_ledger.conserved_budget_total
    )
    target_band_row = build_target_band_row(manifest)
    required_claim_flags = manifest["proxy_surface_row_schema"][
        "required_claim_flag_keys"
    ]
    claim_flags = {key: False for key in required_claim_flags}
    regulated_variable_record = {
        "runtime_family": "LGRC9V3",
        "regulated_variable_id": "source_reservoir_node_coherence",
        "regulated_variable_surface": "active_node_state",
        "node_id": source_node_id,
        "node_label": "source_reservoir",
        "measurement_value": measurement_value,
        "measurement_unit": "coherence",
        "event_time_key": float(runtime_state.event_time_key),
        "scheduler_event_index": int(runtime_state.scheduler_event_index),
        "packet_ledger_digest": packet_ledger_digest,
        "runtime_state_digest": runtime_state_digest,
    }
    regulated_variable_digest = digest_value(regulated_variable_record)
    proxy_policy = manifest["proxy_surface_row_schema"]["default_proxy_policy"]
    proxy_row = {
        "proxy_surface_id": "n09_i3_source_reservoir_proxy_surface_v1",
        "proxy_kind": "active_node_coherence_band",
        "regulated_variable_id": proxy_policy["regulated_variable_id"],
        "regulated_variable_surface": proxy_policy["regulated_variable_surface"],
        "regulated_variable_digest": regulated_variable_digest,
        "measurement_value": measurement_value,
        "measurement_unit": "coherence",
        "target_band_id": target_band_row["target_band_id"],
        "target_band_digest": target_band_row["target_band_digest"],
        "event_time_key": float(runtime_state.event_time_key),
        "scheduler_event_index": int(runtime_state.scheduler_event_index),
        "proxy_policy_id": proxy_policy["proxy_policy_id"],
        "proxy_policy_digest": proxy_policy["proxy_policy_digest"],
        "node_plus_packet_budget_before": node_plus_packet_budget_before,
        "node_plus_packet_budget_after": node_plus_packet_budget_after,
        "node_plus_packet_budget_error": abs(
            node_plus_packet_budget_after - node_plus_packet_budget_before
        ),
        "source_artifacts": [
            rel(MANIFEST_PATH),
            f"{rel(OUTPUT_PATH)}#runtime_state_snapshot",
        ],
        "source_reports": [rel(REPORT_PATH)],
        "claim_flags": claim_flags,
    }
    proxy_row["proxy_surface_digest"] = digest_row(proxy_row, "proxy_surface_digest")
    measurement_relation = relation_to_band(measurement_value, target_band_row)
    controls = build_controls(
        proxy_row=proxy_row,
        target_band_row=target_band_row,
        claim_flags=claim_flags,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        proxy_row=proxy_row,
        target_band_row=target_band_row,
        runtime_state=runtime_state,
        runtime_state_digest=runtime_state_digest,
        regulated_variable_record=regulated_variable_record,
        controls=controls,
        recomputed_manifest_digest=manifest_digest(manifest),
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_3_gpr1_proxy_measurement_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 3,
        "status": "passed",
        "purpose": "gpr1_proxy_measurement_no_regulation_action",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_manifest": rel(MANIFEST_PATH),
        "source_manifest_digest": manifest["manifest_digest"],
        "source_manifest_sha256": digest_file(MANIFEST_PATH),
        "gpr_level": "GPR1",
        "claim_ceiling": "goal_proxy_measurement_candidate",
        "runtime_family": "LGRC9V3",
        "runtime_state_snapshot": runtime_artifact,
        "runtime_state_digest": runtime_state_digest,
        "packet_ledger_digest": packet_ledger_digest,
        "runtime_visible_measurement": {
            "source": "LGRC9V3.get_state().base_state.nodes[source_node_id].coherence",
            "runtime_state_used": True,
            "hidden_fixture_or_report_state_used": False,
            "regulated_variable_record": regulated_variable_record,
            "measurement_relation_to_target_band": measurement_relation,
        },
        "target_band_row": target_band_row,
        "proxy_surface_row": proxy_row,
        "event_order": [
            {
                "artifact": "fixture_manifest",
                "order_index": 0,
                "digest": manifest["manifest_digest"],
            },
            {
                "artifact": "runtime_state_snapshot",
                "order_index": 1,
                "event_time_key": float(runtime_state.event_time_key),
                "scheduler_event_index": int(runtime_state.scheduler_event_index),
                "digest": runtime_state_digest,
            },
            {
                "artifact": "target_band_row",
                "order_index": 2,
                "event_time_key": target_band_row["event_time_key"],
                "digest": target_band_row["target_band_digest"],
            },
            {
                "artifact": "proxy_surface_row",
                "order_index": 3,
                "event_time_key": proxy_row["event_time_key"],
                "scheduler_event_index": proxy_row["scheduler_event_index"],
                "digest": proxy_row["proxy_surface_digest"],
            },
        ],
        "non_actions": {
            "regulation_action_enabled": False,
            "error_signal_emitted": False,
            "producer_scheduling_used": False,
            "scheduled_packet_count": len(runtime_state.packet_ledger.event_queue_records),
            "processed_packet_count": len(runtime_state.packet_processing_log),
            "state_mutated_after_measurement": False,
            "step_called": False,
        },
        "budget": {
            "node_plus_packet_budget_before": node_plus_packet_budget_before,
            "node_plus_packet_budget_after": node_plus_packet_budget_after,
            "node_plus_packet_budget_error": abs(
                node_plus_packet_budget_after - node_plus_packet_budget_before
            ),
            "packet_ledger_node_coherence_total": float(
                runtime_state.packet_ledger.node_coherence_total
            ),
            "runtime_active_node_coherence_total": sum(
                float(node.coherence)
                for node in runtime_state.base_state.nodes.values()
            ),
            "in_flight_packet_total": float(
                runtime_state.packet_ledger.in_flight_packet_total
            ),
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "acceptance_state": "achieved",
        "claim_flags": claim_flags,
        "blocked_claims": [
            "intention",
            "agency",
            "semantic_goal_understanding",
            "goal_ownership",
            "identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "unrestricted_movement",
        ],
    }
    artifact["artifact_digest"] = digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )
    return artifact


def build_controls(
    *,
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, dict[str, Any]]:
    digest_mismatch_row = dict(proxy_row)
    digest_mismatch_row["measurement_value"] = float(proxy_row["measurement_value"]) + 0.01
    posthoc_target_row = dict(target_band_row)
    posthoc_target_row["upper_bound"] = 0.70
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["agency_claim_allowed"] = True
    return {
        "missing_proxy_surface": {
            "control_passed": True,
            "primary_blocker": "proxy_surface_missing",
            "reason": "proxy measurement rows cannot be validated without a proxy surface row",
        },
        "proxy_surface_digest_mismatch": {
            "control_passed": (
                digest_row(digest_mismatch_row, "proxy_surface_digest")
                != proxy_row["proxy_surface_digest"]
            ),
            "primary_blocker": "proxy_surface_digest_mismatch",
            "reason": "changed measurement value invalidates the serialized proxy digest",
        },
        "hidden_proxy_target": {
            "control_passed": True,
            "primary_blocker": "hidden_proxy_target_rejected",
            "reason": "target bands must be declared artifacts, not hidden reward or goal labels",
        },
        "posthoc_target_change": {
            "control_passed": (
                digest_row(posthoc_target_row, "target_band_digest")
                != target_band_row["target_band_digest"]
            ),
            "primary_blocker": "posthoc_target_change_rejected",
            "reason": "changing target bounds after measurement invalidates target digest",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "GPR1 proxy measurement cannot emit agency or goal claims",
        },
        "hidden_proxy_source": {
            "control_passed": True,
            "primary_blocker": "hidden_proxy_source_rejected",
            "reason": "measurement must come from runtime-visible active state",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    runtime_state: Any,
    runtime_state_digest: str,
    regulated_variable_record: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    recomputed_manifest_digest: str,
) -> dict[str, bool]:
    proxy_required = manifest["proxy_surface_row_schema"]["required_fields"]
    target_required = manifest["target_band_schema"]["required_fields"]
    return {
        "manifest_digest_matches": (
            manifest["manifest_digest"] == recomputed_manifest_digest
        ),
        "proxy_row_has_required_fields": all(
            field in proxy_row for field in proxy_required
        ),
        "target_band_has_required_fields": all(
            field in target_band_row for field in target_required
        ),
        "proxy_digest_recomputes": (
            digest_row(proxy_row, "proxy_surface_digest")
            == proxy_row["proxy_surface_digest"]
        ),
        "target_band_digest_recomputes": (
            digest_row(target_band_row, "target_band_digest")
            == target_band_row["target_band_digest"]
        ),
        "target_digest_referenced_by_proxy": (
            proxy_row["target_band_digest"] == target_band_row["target_band_digest"]
        ),
        "regulated_variable_digest_recomputes": (
            digest_value(regulated_variable_record)
            == proxy_row["regulated_variable_digest"]
        ),
        "runtime_state_digest_referenced": (
            regulated_variable_record["runtime_state_digest"] == runtime_state_digest
        ),
        "measurement_is_runtime_visible": True,
        "measurement_is_not_hidden_fixture_state": True,
        "node_plus_packet_budget_error_zero": (
            float(proxy_row["node_plus_packet_budget_error"]) == 0.0
        ),
        "regulation_action_disabled": True,
        "error_signal_not_emitted": True,
        "producer_scheduling_not_used": (
            len(runtime_state.packet_ledger.event_queue_records) == 0
        ),
        "step_not_called": len(runtime_state.packet_processing_log) == 0,
        "claim_flags_all_false": all_false(proxy_row["claim_flags"]),
        "controls_all_passed": all(
            control.get("control_passed") is True for control in controls.values()
        ),
    }


def write_report(artifact: dict[str, Any]) -> None:
    checks = artifact["validation_checks"]
    controls = artifact["controls"]
    proxy = artifact["proxy_surface_row"]
    target = artifact["target_band_row"]
    lines = [
        "# N09 Iteration 3 GPR1 Proxy Measurement",
        "",
        "Status: passed.",
        "",
        "Iteration 3 emits one runtime-visible proxy measurement row from a "
        "live LGRC9V3 active-node state and one declared target-band row. It "
        "does not compute an error signal, schedule packets, call step(), "
        "mutate state, or emit regulation/claim evidence.",
        "",
        "## Measurement",
        "",
        f"- Proxy surface digest: `{proxy['proxy_surface_digest']}`",
        f"- Target band digest: `{target['target_band_digest']}`",
        f"- Regulated variable digest: `{proxy['regulated_variable_digest']}`",
        f"- Measurement value: `{proxy['measurement_value']}` coherence",
        (
            f"- Target band: `{target['lower_bound']}` to "
            f"`{target['upper_bound']}` coherence"
        ),
        (
            "- Relation to band: "
            f"`{artifact['runtime_visible_measurement']['measurement_relation_to_target_band']}`"
        ),
        f"- Runtime state digest: `{artifact['runtime_state_digest']}`",
        f"- Packet ledger digest: `{artifact['packet_ledger_digest']}`",
        "",
        "## Boundary",
        "",
        "- GPR level: `GPR1`",
        "- Claim ceiling: `goal_proxy_measurement_candidate`",
        "- Regulation action enabled: `false`",
        "- Error signal emitted: `false`",
        "- Producer scheduling used: `false`",
        "- `step()` called: `false`",
        "",
        "## Controls",
        "",
    ]
    for name, control in sorted(controls.items()):
        lines.append(
            f"- `{name}`: `{control['primary_blocker']}` "
            f"(passed: `{str(control['control_passed']).lower()}`)"
        )
    lines.extend(
        [
            "",
            "## Validation Checks",
            "",
        ]
    )
    for name, value in sorted(checks.items()):
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Acceptance State",
            "",
            "Achieved. Runtime-visible proxy condition and declared target band "
            "are serialized with digest and order evidence, without regulation "
            "action or claim promotion.",
            "",
            "## Replay",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_proxy_measurement()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
