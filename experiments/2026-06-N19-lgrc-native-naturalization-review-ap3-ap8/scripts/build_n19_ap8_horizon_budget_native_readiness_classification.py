#!/usr/bin/env python3
"""Build N19 Iteration 6 AP8 horizon/budget native-readiness classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-19T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8"
INVENTORY = EXPERIMENT / "outputs" / "n19_ap3_ap8_source_inventory.json"
SCHEMA = EXPERIMENT / "outputs" / "n19_naturalization_schema_v1.json"
OUTPUT = EXPERIMENT / "outputs" / "n19_ap8_horizon_budget_native_readiness_classification.json"
REPORT = EXPERIMENT / "reports" / "n19_ap8_horizon_budget_native_readiness_classification.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "scripts/build_n19_ap8_horizon_budget_native_readiness_classification.py"
)

PHASE8_READY_DERIVATION = (
    "phase8_ready = true only when nat_level = NAT4 and all NAT4 gates pass"
)

NAT4_GATES = [
    "native_policy_or_telemetry_surface_name_present",
    "record_schema_sketch_present",
    "default_off_flags_present",
    "enabled_validated_supported_separation_present",
    "runtime_visible_inputs_source_backed",
    "state_mutation_owner_specified",
    "budget_surface_specified",
    "telemetry_requirements_specified",
    "snapshot_replay_requirements_specified",
    "negative_controls_specified",
    "non_rc_quantity_audit_passes",
    "claim_flags_forced_false",
    "phase8_opened_false",
    "native_support_opened_false",
    "src_diff_empty_true",
]

N18 = "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def source_record(path: str) -> dict[str, Any]:
    source_path = ROOT / path
    data = load_json(source_path)
    return {
        "path": path,
        "sha256": sha256_file(source_path),
        "output_digest": str(data.get("output_digest", "not_recorded")),
        "status": str(data.get("status", "not_recorded")),
    }


def report_record(path: str) -> dict[str, Any]:
    report_path = ROOT / path
    return {"path": path, "sha256": sha256_file(report_path)}


def source_digest_map(paths: list[str]) -> dict[str, str]:
    return {path: sha256_file(ROOT / path) for path in paths}


def source_output_digest_map(paths: list[str]) -> dict[str, str]:
    return {path: str(load_json(ROOT / path).get("output_digest", "not_recorded")) for path in paths}


def source_status_map(paths: list[str]) -> dict[str, str]:
    return {path: str(load_json(ROOT / path).get("status", "not_recorded")) for path in paths}


def false_claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    return {flag: False for flag in schema["candidate_row_schema"]["claim_flags_forced_false"]}


def gate_results(overrides: dict[str, bool]) -> dict[str, bool]:
    result = {gate: False for gate in NAT4_GATES}
    result.update(overrides)
    return result


def all_nat4_gates_pass(row: dict[str, Any]) -> bool:
    results = row.get("nat4_gate_results", {})
    return set(results) == set(NAT4_GATES) and all(results.values())


def no_absolute_paths(value: Any) -> bool:
    if isinstance(value, dict):
        return all(no_absolute_paths(item) for item in value.values())
    if isinstance(value, list):
        return all(no_absolute_paths(item) for item in value)
    if isinstance(value, str):
        forbidden = ["/" + "home/", "/" + "tmp/", "/" + "Users/", "C:" + "\\", "\\" + "Users\\"]
        return not any(marker in value for marker in forbidden)
    return True


def closeout_metadata(inventory: dict[str, Any]) -> dict[str, str]:
    for row in inventory["source_rows"]:
        if row["source_experiment"] == "N18":
            return {
                "source_final_supported_ap_level": row["source_final_supported_ap_level"],
                "source_final_claim_ceiling": row["source_final_claim_ceiling"],
            }
    raise KeyError("N18")


def top(data: dict[str, Any], key: str, default: Any = "not_recorded") -> Any:
    return data.get(key, default)


def check_detail(data: dict[str, Any], check_id: str, default: Any = "not_recorded") -> Any:
    for check in data.get("checks", []):
        if check.get("check_id") == check_id:
            return check.get("detail", default)
    return default


def row_base(
    *,
    row_id: str,
    source_iteration_or_closeout: str,
    artifacts: list[str],
    reports: list[str],
    inventory: dict[str, Any],
    schema: dict[str, Any],
    artifact_supported: bool,
    artifact_claim_scope: str,
    native_question: str,
    primary_disposition: str,
    nat_level: str,
    phase8_ready: bool,
    native_surface: str,
    runtime_visible_inputs: list[str],
    native_state_needed: list[str],
    state_mutation_owner: str,
    record_schema_sketch: dict[str, Any],
    default_off_flags: dict[str, bool],
    enabled_validated_supported_separation: dict[str, bool],
    budget_surface: dict[str, Any],
    telemetry_requirements: list[str],
    snapshot_replay_requirements: list[str],
    negative_controls: list[str],
    non_rc_quantity_audit: dict[str, Any],
    minimal_producer_code_needed: list[str],
    implementation_boundary: str,
    blocked_claims: list[str],
    row_decision: str,
    nat4_gate_results: dict[str, bool],
    evidence_notes: list[str],
    blockers_to_next_level: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = closeout_metadata(inventory)
    row = {
        "row_id": row_id,
        "source_experiment": "N18",
        "source_iteration_or_closeout": source_iteration_or_closeout,
        "source_artifacts": [source_record(path) for path in artifacts],
        "source_reports": [report_record(path) for path in reports],
        "source_sha256": source_digest_map(artifacts),
        "source_output_digest": source_output_digest_map(artifacts),
        "source_status": source_status_map(artifacts),
        "source_final_supported_ap_level": metadata["source_final_supported_ap_level"],
        "source_final_claim_ceiling": metadata["source_final_claim_ceiling"],
        "artifact_supported": artifact_supported,
        "artifact_claim_scope": artifact_claim_scope,
        "native_question": native_question,
        "primary_disposition": primary_disposition,
        "secondary_tags": [],
        "nat_level": nat_level,
        "phase8_ready": phase8_ready,
        "phase8_ready_derivation": PHASE8_READY_DERIVATION,
        "native_policy_or_telemetry_surface_name": native_surface,
        "runtime_visible_inputs": runtime_visible_inputs,
        "native_state_needed": native_state_needed,
        "state_mutation_owner": state_mutation_owner,
        "record_schema_sketch": record_schema_sketch,
        "default_off_flags": default_off_flags,
        "enabled_validated_supported_separation": enabled_validated_supported_separation,
        "budget_surface": budget_surface,
        "telemetry_requirements": telemetry_requirements,
        "snapshot_replay_requirements": snapshot_replay_requirements,
        "negative_controls": negative_controls,
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "minimal_producer_code_needed": minimal_producer_code_needed,
        "implementation_boundary": implementation_boundary,
        "claim_flags": false_claim_flags(schema),
        "blocked_claims": blocked_claims,
        "phase8_opened": False,
        "native_support_opened": False,
        "src_diff_empty": True,
        "row_decision": row_decision,
        "nat4_gate_results": nat4_gate_results,
        "evidence_notes": evidence_notes,
        "blockers_to_next_level": blockers_to_next_level,
    }
    if extra:
        row.update(extra)
    row["row_digest"] = digest_value(row)
    return row


def build_rows(inventory: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    closeout_path = f"{N18}/outputs/n18_closeout_and_handoff.json"
    schema_path = f"{N18}/outputs/n18_long_horizon_schema_v1.json"
    horizon_path = f"{N18}/outputs/n18_horizon_window_sweep.json"
    support_path = f"{N18}/outputs/n18_support_proxy_stress_matrix.json"
    route_path = f"{N18}/outputs/n18_route_memory_stress_matrix.json"
    environment_path = f"{N18}/outputs/n18_environment_resource_stress_matrix.json"
    shared_path = f"{N18}/outputs/n18_shared_medium_stress_matrix.json"
    shared_margin_path = f"{N18}/outputs/n18_shared_medium_margin_probe.json"
    classification_path = f"{N18}/outputs/n18_long_horizon_control_and_classification_matrix.json"

    closeout = load_json(ROOT / closeout_path)
    horizon = load_json(ROOT / horizon_path)
    support = load_json(ROOT / support_path)
    route = load_json(ROOT / route_path)
    environment = load_json(ROOT / environment_path)
    shared = load_json(ROOT / shared_path)
    shared_margin = load_json(ROOT / shared_margin_path)
    classification = load_json(ROOT / classification_path)

    closeout_result = closeout["closeout_result"]
    classification_result = classification["classification_result"]
    horizon_envelope = horizon["source_backed_horizon_envelope"]
    i8_i8a = closeout["i8_i8a_relationship"]
    replay_controls = closeout["final_replay_and_controls"]

    common_negative_controls = [
        "stale state replay",
        "single-axis stale support",
        "single-axis stale memory",
        "single-axis stale selection",
        "single-axis stale proxy/target",
        "single-axis stale boundary",
        "single-axis stale loop feedback",
        "order inversion",
        "post-hoc long-horizon stitching",
        "budget overrun",
        "artifact-only reconstruction mismatch",
        "hidden native support relabel",
        "semantic agency relabel",
        "Phase 8/native implementation relabel",
    ]

    rows: list[dict[str, Any]] = []
    rows.append(
        row_base(
            row_id="n19_i6_row_01_n18_limited_h4_horizon_envelope_telemetry_nat4",
            source_iteration_or_closeout="N18 I4 horizon sweep, I9 classification, and I10 closeout",
            artifacts=[closeout_path, schema_path, horizon_path, classification_path],
            reports=[
                f"{N18}/reports/n18_closeout_and_handoff.md",
                f"{N18}/reports/n18_horizon_window_sweep.md",
                f"{N18}/reports/n18_long_horizon_control_and_classification_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="limited artifact-level AP8 h4/L5 horizon envelope evidence",
            native_question=(
                "Can the N18 h4 horizon envelope become Phase-8-ready native horizon "
                "validation telemetry without widening to h8, h16, or general AP8?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_limited_horizon_envelope_validation_telemetry",
            runtime_visible_inputs=[
                "supported_windows",
                "partial_windows",
                "blocked_windows",
                "max_supported_horizon",
                "horizon_extrapolation_allowed",
                "highest_positive_stress_ladder_rung",
                "final_supported_ap_level",
                "final_claim_ceiling",
            ],
            native_state_needed=[
                "source-current horizon window id",
                "relative window count",
                "horizon decision per window",
                "horizon extrapolation blocker",
                "limited AP8 claim ceiling",
            ],
            state_mutation_owner="future native horizon-envelope validation telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_limited_horizon_envelope_validation_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "max_supported_horizon": "h4",
                "supported_windows": ["h2", "h4"],
                "partial_windows": ["h8"],
                "blocked_windows": ["h16"],
                "horizon_extrapolation_allowed": False,
                "general_ap8_claim_allowed": False,
            },
            default_off_flags={
                "native_horizon_envelope_telemetry_enabled": False,
                "native_general_ap8_enabled": False,
                "native_horizon_extrapolation_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "max_supported_horizon": closeout_result["max_supported_horizon"],
                "highest_positive_stress_ladder_rung": closeout_result[
                    "highest_positive_stress_ladder_rung"
                ],
                "minimum_budget_headroom_classified_stack": closeout_result[
                    "minimum_budget_headroom_classified_stack"
                ],
                "horizon_extrapolation_allowed": closeout_result[
                    "horizon_extrapolation_allowed"
                ],
            },
            telemetry_requirements=[
                "record supported, partial, and blocked horizon windows separately",
                "record max_supported_horizon as h4 before claim classification",
                "record h8 partial and h16 rejected as blockers, not pending successes",
                "record limited AP8 claim ceiling with every horizon envelope row",
            ],
            snapshot_replay_requirements=[
                "artifact-only replay of horizon sweep and closeout fields",
                "snapshot/load replay of horizon envelope",
                "reject horizon extrapolation beyond h4",
                "reject h8/h16 recovery without new source-backed rows",
            ],
            negative_controls=common_negative_controls
            + [
                "limited AP8 as general AP8",
                "h8 partial as supported horizon",
                "h16 rejected as recoverable horizon",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "general AP8",
                    "unbounded horizon persistence",
                    "native support",
                    "unrestricted autonomy",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off native horizon-envelope telemetry surface",
                "add horizon-window decision digest",
                "add h8/h16 extrapolation blocker records",
                "add limited-claim-ceiling replay digest",
            ],
            implementation_boundary=(
                "N19 classifies h4 envelope readiness only. It does not recover h8/h16, "
                "support general AP8, or implement native horizon persistence."
            ),
            blocked_claims=[
                "general AP8",
                "h8/h16 extrapolation",
                "unbounded long-horizon persistence",
                "native support",
                "fully native integration",
                "unrestricted autonomy",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N18 closes as AP8_limited_artifact_candidate, not general AP8.",
                "The final supported horizon is h4; h8 remains partial and h16 remains rejected.",
                "The h4/L5 envelope is the maximum supported stress/horizon envelope consumed by N19.",
            ],
            blockers_to_next_level=[
                "h8 and h16 are not recovered",
                "horizon extrapolation remains disallowed",
                "NAT5/NAT6 are out of scope for N19",
            ],
            extra={
                "source_horizon_envelope": horizon_envelope,
                "closeout_horizon_boundary": {
                    "final_supported_ap_level": closeout_result["final_supported_ap_level"],
                    "final_claim_ceiling": closeout_result["final_claim_ceiling"],
                    "max_supported_horizon": closeout_result["max_supported_horizon"],
                    "h8_recovered": closeout_result["h8_recovered"],
                    "h16_recovered": closeout_result["h16_recovered"],
                    "general_ap8_supported": closeout_result["general_ap8_supported"],
                },
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i6_row_02_n18_budget_replay_control_telemetry_nat4",
            source_iteration_or_closeout="N18 I9 classification and I10 replay/control closeout",
            artifacts=[closeout_path, classification_path],
            reports=[
                f"{N18}/reports/n18_closeout_and_handoff.md",
                f"{N18}/reports/n18_long_horizon_control_and_classification_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="artifact-level AP8 replay, budget, stale-state, and control cleanliness",
            native_question=(
                "Can N18 replay, budget, stale-state, and control telemetry become a "
                "Phase-8-ready native validation surface?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_long_horizon_budget_replay_control_telemetry",
            runtime_visible_inputs=[
                "minimum_budget_headroom_classified_stack",
                "artifact_only_reconstruction_status",
                "duplicate_replay_status",
                "snapshot_load_replay_status",
                "order_inversion_control_status",
                "post_hoc_stitching_control_status",
                "stale_state_control_status",
                "single_axis_stale_control_statuses",
                "budget_overrun_control_status",
            ],
            native_state_needed=[
                "budget headroom record",
                "replay digest matrix",
                "negative control matrix",
                "single-axis stale-control matrix",
                "budget overrun blocker",
                "artifact-only reconstruction digest",
            ],
            state_mutation_owner="future native long-horizon replay/budget validator",
            record_schema_sketch={
                "surface_id": "native_long_horizon_budget_replay_control_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "minimum_budget_headroom": "float",
                "replay_matrix_digest": "sha256",
                "negative_control_matrix_digest": "sha256",
                "stale_axis_control_digest": "sha256",
                "budget_overrun_claim_allowed": False,
            },
            default_off_flags={
                "native_long_horizon_replay_control_telemetry_enabled": False,
                "native_budget_claim_admission_enabled": False,
                "native_support_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "minimum_budget_headroom_classified_stack": closeout_result[
                    "minimum_budget_headroom_classified_stack"
                ],
                "artifact_only_reconstruction": replay_controls["artifact_only_reconstruction"],
                "duplicate_replay": replay_controls["duplicate_replay"],
                "snapshot_load_replay": replay_controls["snapshot_load_replay"],
                "order_inversion_control": replay_controls["order_inversion_control"],
                "post_hoc_stitching_control": replay_controls["post_hoc_stitching_control"],
            },
            telemetry_requirements=[
                "record budget headroom beside every positive long-horizon claim row",
                "record replay digest stability for artifact-only, duplicate, and snapshot/load replay",
                "record order inversion and post-hoc stitching as failed-closed controls",
                "record each single-axis stale control separately",
                "record budget overrun as failed-closed blocker",
            ],
            snapshot_replay_requirements=[
                "artifact-only reconstruction stable",
                "duplicate replay stable",
                "snapshot/load replay stable",
                "order-inversion control fails closed as expected",
                "post-hoc stitching control fails closed as expected",
                "single-axis stale controls fail closed as expected",
            ],
            negative_controls=common_negative_controls,
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden runtime state",
                    "hidden native support",
                    "post-hoc stitched horizon",
                    "stale source axis",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off long-horizon replay/control telemetry surface",
                "add budget-headroom and budget-overrun digests",
                "add single-axis stale-control records for support, memory, selection, proxy, boundary, and loop feedback",
                "add replay digest over source rows, horizon envelope, budget surface, and claim flags",
            ],
            implementation_boundary=(
                "N19 classifies validation telemetry readiness. It does not implement native replay, "
                "native support, or Phase 8."
            ),
            blocked_claims=[
                "artifact replay as native support",
                "hidden native support",
                "native implementation",
                "general AP8",
                "agency",
                "semantic action/perception",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N18 I9 validates replay/control cleanliness before closeout.",
                "N18 I10 records artifact-only, duplicate, and snapshot/load replay as stable.",
                "Order inversion, post-hoc stitching, budget overrun, and single-axis stale controls fail closed as expected.",
            ],
            blockers_to_next_level=[
                "native replay/control implementation is not present",
                "native support remains false",
                "NAT5/NAT6 are out of scope for N19",
            ],
            extra={
                "final_replay_and_controls": replay_controls,
                "classification_replay_matrix": classification["replay_matrix"],
                "classification_negative_control_matrix": classification["negative_control_matrix"],
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i6_row_03_n18_cross_axis_bottleneck_telemetry_nat4",
            source_iteration_or_closeout="N18 I5-I8A stress stack and I10 bottleneck closeout",
            artifacts=[
                closeout_path,
                support_path,
                route_path,
                environment_path,
                shared_path,
                shared_margin_path,
                classification_path,
            ],
            reports=[
                f"{N18}/reports/n18_support_proxy_stress_matrix.md",
                f"{N18}/reports/n18_route_memory_stress_matrix.md",
                f"{N18}/reports/n18_environment_resource_stress_matrix.md",
                f"{N18}/reports/n18_shared_medium_stress_matrix.md",
                f"{N18}/reports/n18_shared_medium_margin_probe.md",
                f"{N18}/reports/n18_closeout_and_handoff.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=True,
            artifact_claim_scope="artifact-level h4/L5 cross-axis continuity and bottleneck telemetry",
            native_question=(
                "Can N18 cross-axis continuity and boundary-to-loop-feedback bottleneck "
                "telemetry become Phase-8-ready without treating I8-A as a replacement for I8?"
            ),
            primary_disposition="phase8_ready_native_policy_candidate",
            nat_level="NAT4",
            phase8_ready=True,
            native_surface="native_cross_axis_continuity_bottleneck_telemetry",
            runtime_visible_inputs=[
                "support_proxy_axis_status",
                "route_memory_axis_status",
                "environment_resource_axis_status",
                "shared_medium_axis_status",
                "boundary_to_loop_feedback_score",
                "minimum_loop_feedback_score_supported_h4_rows",
                "minimum_budget_headroom_supported_h4_rows",
                "i8_i8a_relationship",
                "principal_bottleneck_link",
            ],
            native_state_needed=[
                "per-axis continuity score records",
                "cross-axis linked continuity record",
                "principal bottleneck axis/link/score",
                "I8 equality-at-floor shared-medium row",
                "I8-A margin evidence row with non-replacement role",
            ],
            state_mutation_owner="future native cross-axis continuity telemetry recorder",
            record_schema_sketch={
                "surface_id": "native_cross_axis_continuity_bottleneck_telemetry",
                "enabled": False,
                "validated": False,
                "supported": False,
                "principal_bottleneck_axis": "loop_feedback",
                "principal_bottleneck_link": "boundary_to_loop_feedback",
                "principal_bottleneck_score": 0.8,
                "i8a_replaces_i8": False,
                "general_shared_medium_robustness_supported": False,
            },
            default_off_flags={
                "native_cross_axis_continuity_telemetry_enabled": False,
                "native_shared_medium_generalization_enabled": False,
                "native_autonomy_inference_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": False,
                "supported": False,
                "phase8_ready_candidate": True,
            },
            budget_surface={
                "required": True,
                "i8_boundary_to_loop_feedback_score": i8_i8a["i8_boundary_to_loop_feedback_score"],
                "i8_budget_headroom": i8_i8a["i8_budget_headroom"],
                "i8a_boundary_to_loop_feedback_score": i8_i8a["i8a_boundary_to_loop_feedback_score"],
                "i8a_budget_headroom": i8_i8a["i8a_budget_headroom"],
                "principal_bottleneck_score": closeout_result["principal_bottleneck_score"],
            },
            telemetry_requirements=[
                "record cross-axis continuity by axis and link",
                "record boundary_to_loop_feedback as the principal bottleneck",
                "record I8 minimal equality-at-floor support separately from I8-A margin evidence",
                "record I8-A as additional robustness evidence, not replacement",
                "record general shared-medium robustness as blocked",
            ],
            snapshot_replay_requirements=[
                "replay I5-I8A source rows with fixed h4/L5 policy",
                "reject dropped boundary_to_loop_feedback variants",
                "reject hidden budget relief, threshold relaxation, and horizon shortening",
                "reject I8-A replacement or averaging-away of I8 bottleneck",
            ],
            negative_controls=common_negative_controls
            + [
                "dropped boundary_to_loop_feedback",
                "hidden budget relief",
                "threshold relaxation",
                "horizon shortening",
                "I8-A as I8 replacement",
                "general shared-medium robustness relabel",
                "drift as autonomy",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "unmeasured autonomy",
                    "averaged-away bottleneck",
                    "hidden budget relief",
                    "general shared-medium robustness",
                ],
            },
            minimal_producer_code_needed=[
                "add default-off cross-axis continuity telemetry surface",
                "add principal bottleneck axis/link/score record",
                "add I8/I8-A role-separation record",
                "add controls for dropped feedback, budget relief, threshold relaxation, and horizon shortening",
            ],
            implementation_boundary=(
                "The row is bottleneck telemetry readiness only. It does not widen N18 beyond h4/L5 "
                "and does not infer autonomy from drift or margin. The boundary_to_loop_feedback "
                "bottleneck is recorded as a Phase 8 validation requirement, not resolved."
            ),
            blocked_claims=[
                "general shared-medium robustness",
                "I8-A as I8 replacement",
                "autonomous adaptation",
                "unrestricted autonomy",
                "general AP8",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="supported",
            nat4_gate_results=gate_results({gate: True for gate in NAT4_GATES}),
            evidence_notes=[
                "N18 names boundary_to_loop_feedback as the principal bottleneck.",
                "I8 has boundary_to_loop_feedback score 0.8 and budget headroom 0.01.",
                "I8-A has better margin but is additional evidence, not replacement for the I8 edge case.",
                "The final classification remains conservative and bounded by the original I8 bottleneck.",
                "N19 records the bottleneck for future validation; it does not claim the bottleneck is solved.",
            ],
            blockers_to_next_level=[
                "general shared-medium robustness remains blocked",
                "horizon remains h4/L5",
                "NAT5/NAT6 are out of scope for N19",
            ],
            extra={
                "stress_family_summaries": {
                    "support_proxy": support["family_summary"],
                    "route_memory": route["family_summary"],
                    "environment_resource": environment["family_summary"],
                    "shared_medium": shared["family_summary"],
                    "shared_medium_margin": shared_margin["family_summary"],
                },
                "i8_i8a_relationship": i8_i8a,
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i6_row_04_n18_h8_h16_general_ap8_extrapolation_blocker",
            source_iteration_or_closeout="N18 horizon sweep, I9 classification, and I10 closeout blockers",
            artifacts=[closeout_path, horizon_path, classification_path],
            reports=[
                f"{N18}/reports/n18_closeout_and_handoff.md",
                f"{N18}/reports/n18_horizon_window_sweep.md",
                f"{N18}/reports/n18_long_horizon_control_and_classification_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="blocked upgrade from limited h4 AP8 to h8/h16 or general AP8",
            native_question=(
                "Can N18 limited h4/L5 evidence be treated as h8, h16, or general AP8 evidence?"
            ),
            primary_disposition="implementation_gap_blocker",
            nat_level="NAT2",
            phase8_ready=False,
            native_surface="native_horizon_extrapolation_evidence_required",
            runtime_visible_inputs=[
                "h8_partial_status",
                "h16_rejected_status",
                "general_ap8_supported_false",
                "horizon_extrapolation_allowed_false",
                "final_blockers",
            ],
            native_state_needed=[
                "source-backed h8 supported rows",
                "source-backed h16 supported rows",
                "budget-valid replay over longer windows",
                "negative controls that fail closed at longer horizon",
                "claim boundary preserving limited-vs-general AP8",
            ],
            state_mutation_owner="future longer-horizon producer/validator",
            record_schema_sketch={
                "blocked_upgrade_id": "h8_h16_general_ap8_extrapolation_blocker",
                "current_max_supported_horizon": "h4",
                "h8_status": "partial",
                "h16_status": "rejected",
                "general_ap8_supported": False,
                "phase8_ready_candidate": False,
            },
            default_off_flags={
                "native_h8_h16_extrapolation_enabled": False,
                "native_general_ap8_enabled": False,
            },
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={
                "required": True,
                "status": "blocked_until_h8_h16_supported_source_rows_exist",
                "horizon_extrapolation_allowed": False,
            },
            telemetry_requirements=[
                "record h8 as partial, not recovered",
                "record h16 as rejected, not recovered",
                "record general AP8 as blocked",
                "record horizon extrapolation as disallowed",
            ],
            snapshot_replay_requirements=[
                "replay h4 envelope without widening",
                "reject h8/h16 promotion without source-backed support rows",
                "reject limited AP8 as general AP8",
            ],
            negative_controls=[
                "h8 partial as supported",
                "h16 rejected as supported",
                "limited AP8 as general AP8",
                "long-horizon drift as autonomy",
                "artifact replay as native support",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "hidden h8 support",
                    "hidden h16 support",
                    "general AP8",
                    "native support",
                ],
            },
            minimal_producer_code_needed=[
                "produce supported h8 and h16 source rows under frozen policy",
                "record longer-window budget and replay controls",
                "record longer-window stale-axis and post-hoc stitching controls",
                "preserve limited/general AP8 distinction in claim boundary",
            ],
            implementation_boundary=(
                "This is a replayable blocker. NAT2 describes source-backed blocker evidence, "
                "not native readiness."
            ),
            blocked_claims=[
                "h8 recovery",
                "h16 recovery",
                "horizon extrapolation",
                "general AP8",
                "unrestricted autonomy",
                "native support",
                "Phase 8 opened",
                "AP9",
            ],
            row_decision="blocked",
            nat4_gate_results=gate_results(
                {
                    "native_policy_or_telemetry_surface_name_present": True,
                    "record_schema_sketch_present": True,
                    "default_off_flags_present": True,
                    "enabled_validated_supported_separation_present": True,
                    "state_mutation_owner_specified": True,
                    "budget_surface_specified": True,
                    "telemetry_requirements_specified": True,
                    "snapshot_replay_requirements_specified": True,
                    "negative_controls_specified": True,
                    "non_rc_quantity_audit_passes": True,
                    "claim_flags_forced_false": True,
                    "phase8_opened_false": True,
                    "native_support_opened_false": True,
                    "src_diff_empty_true": True,
                }
            ),
            evidence_notes=[
                "NAT2 describes replayable blocker evidence only; row_decision remains blocked and phase8_ready remains false.",
                "N18 final blockers preserve general_ap8_blocked and h8_h16_extrapolation_blocked.",
                "The limited h4/L5 result must not be widened without new source-backed h8/h16 evidence.",
            ],
            blockers_to_next_level=[
                "h8 partial window not recovered",
                "h16 rejected window not recovered",
                "general AP8 unsupported",
                "horizon extrapolation disallowed",
            ],
            extra={
                "source_blockers": [
                    blocker
                    for blocker in closeout["final_blockers"]
                    if blocker["blocker_id"]
                    in {"general_ap8_blocked", "h8_h16_extrapolation_blocked"}
                ],
            },
        )
    )
    rows.append(
        row_base(
            row_id="n19_i6_row_05_n18_native_support_agency_ap8_relabels_rejected",
            source_iteration_or_closeout="N18 closeout claim boundary and I9 controls",
            artifacts=[closeout_path, classification_path],
            reports=[
                f"{N18}/reports/n18_closeout_and_handoff.md",
                f"{N18}/reports/n18_long_horizon_control_and_classification_matrix.md",
            ],
            inventory=inventory,
            schema=schema,
            artifact_supported=False,
            artifact_claim_scope="unsafe relabel controls over limited artifact-level AP8 evidence",
            native_question=(
                "Can N18 limited artifact-level AP8 evidence be relabeled as native support, "
                "Phase 8 implementation, agency, semantic action/perception, identity, or life?"
            ),
            primary_disposition="unsafe_relabel_rejected",
            nat_level="NAT0",
            phase8_ready=False,
            native_surface="not_applicable_relabel_rejected",
            runtime_visible_inputs=[],
            native_state_needed=[],
            state_mutation_owner="not_applicable",
            record_schema_sketch={"relabel_claim": "string", "claim_allowed": False},
            default_off_flags={"unsafe_ap8_relabel_enabled": False},
            enabled_validated_supported_separation={
                "enabled": False,
                "validated": True,
                "supported": False,
                "phase8_ready_candidate": False,
            },
            budget_surface={"required": False, "reason": "claim-control row"},
            telemetry_requirements=["record rejected relabel and source claim boundary"],
            snapshot_replay_requirements=["replay unsafe claim flags as false"],
            negative_controls=[
                "artifact replay as native support",
                "limited AP8 as general AP8",
                "long-horizon closure as semantic agency",
                "drift as autonomy",
                "identity acceptance from continuity",
                "Phase 8/native implementation relabel",
                "organism/life relabel",
            ],
            non_rc_quantity_audit={
                "passes": True,
                "non_rc_quantities_required": False,
                "blocked_hidden_quantities": [
                    "native support",
                    "agency",
                    "semantic action",
                    "semantic perception",
                    "identity acceptance",
                    "organism/life",
                ],
            },
            minimal_producer_code_needed=[
                "none for this rejected relabel; preserve controls in any future horizon/budget surface"
            ],
            implementation_boundary="Rejected relabel row; no implementation path.",
            blocked_claims=[
                "native support",
                "Phase 8 implementation",
                "agency",
                "intention",
                "choice",
                "semantic action",
                "semantic perception",
                "semantic goal ownership",
                "selfhood",
                "identity acceptance",
                "organism/life behavior",
                "fully native agentic-like integration",
                "unrestricted autonomy",
                "general AP8",
                "AP9",
            ],
            row_decision="rejected",
            nat4_gate_results=gate_results({}),
            evidence_notes=[
                "N18 closeout explicitly says artifact replay is not native support.",
                "Phase 8 remains unopened and native support remains false.",
                "Long-horizon agentic-like closure remains artifact-level and does not support agency, semantic action/perception, identity, or life.",
            ],
            blockers_to_next_level=["unsafe relabel has no native-readiness promotion path"],
        )
    )
    return rows


def validate_rows(rows: list[dict[str, Any]], schema: dict[str, Any]) -> list[dict[str, Any]]:
    required_fields = set(schema["candidate_row_schema"]["required_fields"])
    primary_dispositions = set(schema["enums"]["primary_disposition"])
    nat_levels = set(schema["enums"]["nat_level"])
    row_decisions = set(schema["enums"]["row_decision"])
    claim_flags = set(schema["candidate_row_schema"]["claim_flags_forced_false"])
    row_ids = {row["row_id"] for row in rows}
    expected_ids = {
        "n19_i6_row_01_n18_limited_h4_horizon_envelope_telemetry_nat4",
        "n19_i6_row_02_n18_budget_replay_control_telemetry_nat4",
        "n19_i6_row_03_n18_cross_axis_bottleneck_telemetry_nat4",
        "n19_i6_row_04_n18_h8_h16_general_ap8_extrapolation_blocker",
        "n19_i6_row_05_n18_native_support_agency_ap8_relabels_rejected",
    }
    checks = [
        {
            "check_id": "required_ap8_rows_present",
            "passed": row_ids == expected_ids,
            "detail": sorted(row_ids),
        },
        {
            "check_id": "all_required_schema_fields_present",
            "passed": all(required_fields.issubset(row) for row in rows),
            "detail": {
                row["row_id"]: sorted(required_fields - set(row))
                for row in rows
                if not required_fields.issubset(row)
            },
        },
        {
            "check_id": "primary_dispositions_valid",
            "passed": all(row["primary_disposition"] in primary_dispositions for row in rows),
            "detail": {row["row_id"]: row["primary_disposition"] for row in rows},
        },
        {
            "check_id": "nat_levels_valid",
            "passed": all(row["nat_level"] in nat_levels for row in rows),
            "detail": {row["row_id"]: row["nat_level"] for row in rows},
        },
        {
            "check_id": "row_decisions_valid",
            "passed": all(row["row_decision"] in row_decisions for row in rows),
            "detail": {row["row_id"]: row["row_decision"] for row in rows},
        },
        {
            "check_id": "phase8_ready_derivation_enforced",
            "passed": all(
                row["phase8_ready"] == (row["nat_level"] == "NAT4" and all_nat4_gates_pass(row))
                for row in rows
            ),
            "detail": {
                row["row_id"]: {
                    "nat_level": row["nat_level"],
                    "phase8_ready": row["phase8_ready"],
                    "all_nat4_gates_pass": all_nat4_gates_pass(row),
                }
                for row in rows
            },
        },
        {
            "check_id": "nat4_rows_have_all_gates_passed",
            "passed": all(all_nat4_gates_pass(row) for row in rows if row["nat_level"] == "NAT4"),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
        },
        {
            "check_id": "claim_flags_forced_false_all_rows",
            "passed": all(
                set(row["claim_flags"]) == claim_flags
                and all(value is False for value in row["claim_flags"].values())
                for row in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "phase8_and_native_support_not_opened",
            "passed": all(not row["phase8_opened"] and not row["native_support_opened"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "source_digests_present",
            "passed": all(row["source_sha256"] and row["source_output_digest"] for row in rows),
            "detail": len(rows),
        },
        {
            "check_id": "source_scope_is_n18_only",
            "passed": all(row["source_experiment"] == "N18" for row in rows),
            "detail": sorted({row["source_experiment"] for row in rows}),
        },
        {
            "check_id": "max_supported_horizon_h4_preserved",
            "passed": any(
                row["row_id"] == "n19_i6_row_01_n18_limited_h4_horizon_envelope_telemetry_nat4"
                and row["source_horizon_envelope"]["max_supported_horizon"] == "h4"
                and row["source_horizon_envelope"]["partial_windows"] == ["h8"]
                and row["source_horizon_envelope"]["blocked_windows"] == ["h16"]
                for row in rows
            ),
            "detail": "h4 supported, h8 partial, h16 blocked",
        },
        {
            "check_id": "boundary_to_loop_feedback_bottleneck_preserved",
            "passed": any(
                row["row_id"] == "n19_i6_row_03_n18_cross_axis_bottleneck_telemetry_nat4"
                and row["record_schema_sketch"]["principal_bottleneck_link"]
                == "boundary_to_loop_feedback"
                and row["record_schema_sketch"]["principal_bottleneck_score"] == 0.8
                for row in rows
            ),
            "detail": "boundary_to_loop_feedback score 0.8 remains named bottleneck",
        },
        {
            "check_id": "h8_h16_general_ap8_blocker_present",
            "passed": any(
                row["row_id"] == "n19_i6_row_04_n18_h8_h16_general_ap8_extrapolation_blocker"
                and row["row_decision"] == "blocked"
                and "general AP8" in row["blocked_claims"]
                and "h8 recovery" in row["blocked_claims"]
                and "h16 recovery" in row["blocked_claims"]
                for row in rows
            ),
            "detail": "limited AP8 not widened",
        },
        {
            "check_id": "artifact_replay_native_support_relabel_rejected",
            "passed": any(
                row["row_id"] == "n19_i6_row_05_n18_native_support_agency_ap8_relabels_rejected"
                and row["row_decision"] == "rejected"
                and "native support" in row["blocked_claims"]
                and any("artifact replay is not native support" in note for note in row["evidence_notes"])
                for row in rows
            ),
            "detail": "artifact replay remains artifact-level",
        },
        {
            "check_id": "native_horizon_budget_requirements_recorded",
            "passed": all(
                row["telemetry_requirements"]
                and row["minimal_producer_code_needed"]
                for row in rows
                if row["nat_level"] == "NAT4"
            ),
            "detail": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(rows),
            "detail": "all row paths are relative",
        },
        {
            "check_id": "src_diff_empty_recorded_true",
            "passed": all(row["src_diff_empty"] is True for row in rows),
            "detail": len(rows),
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N19 Iteration 6 - AP8 Horizon And Budget Native-Readiness Classification",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"row_count = {artifact['row_count']}",
        f"phase8_ready_row_count = {artifact['classification_summary']['phase8_ready_row_count']}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Classification rows:",
        "",
        "| Row | Disposition | NAT | Decision | Phase 8 Ready | Surface |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in artifact["candidate_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["row_id"],
                    row["primary_disposition"],
                    row["nat_level"],
                    row["row_decision"],
                    str(row["phase8_ready"]).lower(),
                    row["native_policy_or_telemetry_surface_name"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Main interpretation:",
            "",
            "```text",
            artifact["interpretation"]["main_read"],
            "```",
            "",
            "Scope boundary:",
            "",
            "```text",
            artifact["interpretation"]["scope_boundary"],
            "```",
            "",
            "Classification summary:",
            "",
            "```json",
            json.dumps(artifact["classification_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = load_json(INVENTORY)
    schema = load_json(SCHEMA)
    rows = build_rows(inventory, schema)
    checks = [
        {
            "check_id": "source_inventory_passed",
            "passed": inventory.get("status") == "passed",
            "detail": rel(INVENTORY),
        },
        {
            "check_id": "schema_freeze_passed",
            "passed": schema.get("status") == "passed"
            and schema.get("candidate_rows_classified") is False,
            "detail": rel(SCHEMA),
        },
    ] + validate_rows(rows, schema)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact = {
        "artifact_id": "n19_ap8_horizon_budget_native_readiness_classification",
        "schema_version": "n19_ap8_horizon_budget_native_readiness_classification_v1",
        "experiment": "2026-06-N19-lgrc-native-naturalization-review-ap3-ap8",
        "iteration": 6,
        "status": "passed" if not failed_checks else "failed",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Classify N18 limited AP8 h4/L5 horizon, budget, replay, cross-axis "
            "continuity, and claim-boundary evidence as native-readiness surfaces or blockers."
        ),
        "source_inventory": {
            "path": rel(INVENTORY),
            "sha256": sha256_file(INVENTORY),
            "output_digest": inventory["output_digest"],
        },
        "schema_source": {
            "path": rel(SCHEMA),
            "sha256": sha256_file(SCHEMA),
            "output_digest": schema["output_digest"],
        },
        "candidate_rows": rows,
        "row_count": len(rows),
        "classification_summary": {
            "classified_sources": ["N18"],
            "nat4_rows": [row["row_id"] for row in rows if row["nat_level"] == "NAT4"],
            "nat2_rows": [row["row_id"] for row in rows if row["nat_level"] == "NAT2"],
            "rejected_rows": [row["row_id"] for row in rows if row["row_decision"] == "rejected"],
            "blocked_rows": [row["row_id"] for row in rows if row["row_decision"] == "blocked"],
            "phase8_ready_row_count": sum(1 for row in rows if row["phase8_ready"]),
            "ap8_phase8_ready_surfaces": [
                row["native_policy_or_telemetry_surface_name"]
                for row in rows
                if row["phase8_ready"]
            ],
            "final_supported_ap_level": closeout_metadata(inventory)["source_final_supported_ap_level"],
            "final_claim_ceiling": closeout_metadata(inventory)["source_final_claim_ceiling"],
            "max_supported_horizon": "h4",
            "highest_positive_stress_ladder_rung": "L5",
            "principal_bottleneck_link": "boundary_to_loop_feedback",
            "principal_bottleneck_score": 0.8,
            "h8_h16_extrapolation_status": "blocked",
            "general_ap8_status": "blocked",
            "artifact_replay_native_support_relabel_status": "rejected",
        },
        "interpretation": {
            "main_read": (
                "Iteration 6 classifies N18 as Phase-8-ready native validation telemetry "
                "for a limited h4/L5 AP8 envelope: horizon envelope telemetry, replay/budget "
                "control telemetry, and cross-axis bottleneck telemetry are NAT4. The result "
                "remains limited and artifact-level."
            ),
            "scope_boundary": (
                "h8 and h16 remain unrecovered, general AP8 remains blocked, and "
                "boundary_to_loop_feedback remains the named bottleneck. Artifact replay is "
                "not native support, and N19 does not open Phase 8 or native implementation."
            ),
            "not_supported": [
                "general AP8",
                "h8 recovery",
                "h16 recovery",
                "native support",
                "Phase 8 implementation",
                "agency",
                "semantic action",
                "semantic perception",
                "identity acceptance",
                "organism/life behavior",
                "unrestricted autonomy",
                "AP9",
            ],
        },
        "phase8_opened": False,
        "native_support_opened": False,
        "ap9_opened": False,
        "src_diff_empty": True,
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()
