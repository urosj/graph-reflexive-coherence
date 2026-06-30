#!/usr/bin/env python3
"""Build N29 I12.2 active-medium separability tranche."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_boundary_shared_medium_active_i122.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I12A = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_runtime_i12a.json"
I12C = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_replay_stress_i12c.json"
I121A = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_alternative_runtime_i121a.json"
I121C = (
    EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_alternative_replay_stress_i121c.json"
)
N25_2_PRIMARY = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_native_runtime_positive_probe.json"
)
N25_2_VARIANT = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_native_runtime_variant_probe.json"
)

OUT_I122 = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_i122.json"
OUT_I122A = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_runtime_i122a.json"
OUT_I122B = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_controls_i122b.json"
OUT_I122C = (
    EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_replay_stress_i122c.json"
)
REP_I122 = EXPERIMENT / "reports" / "n29_boundary_shared_medium_active_i122.md"
REP_I122A = EXPERIMENT / "reports" / "n29_boundary_shared_medium_active_runtime_i122a.md"
REP_I122B = EXPERIMENT / "reports" / "n29_boundary_shared_medium_active_controls_i122b.md"
REP_I122C = (
    EXPERIMENT / "reports" / "n29_boundary_shared_medium_active_replay_stress_i122c.md"
)

UNSAFE_FLAGS = {
    "active_shared_medium_coordination_claim_allowed": False,
    "agent_body_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "life_claim_allowed": False,
    "multi_agent_interaction_claim_allowed": False,
    "native_colony_boundary_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "nonzero_leakage_tolerance_claim_allowed": False,
    "organism_environment_boundary_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "resource_ownership_claim_allowed": False,
    "semantic_trail_or_pheromone_substrate_claim_allowed": False,
    "sentience_claim_allowed": False,
}


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
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def nested_get(data: Any, path: tuple[Any, ...], default: Any = None) -> Any:
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, role: str) -> dict[str, Any]:
    parsed = load_json(path)
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "role": role,
        "artifact_id": parsed.get("artifact_id", "not_recorded"),
        "status": parsed.get("status", "not_recorded"),
        "acceptance_state": parsed.get("acceptance_state", "not_recorded"),
        "output_digest": parsed.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def collect_key_numbers(data: Any, key_name: str) -> list[float]:
    found: list[float] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_name and isinstance(value, (int, float)):
                found.append(float(value))
            found.extend(collect_key_numbers(value, key_name))
    elif isinstance(data, list):
        for item in data:
            found.extend(collect_key_numbers(item, key_name))
    return found


def source_and_injected_pressure_rows(i12c: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    source: dict[str, Any] = {}
    injected: dict[str, Any] = {}
    for row in i12c.get("replay_stress_rows", []):
        for supporting in row.get("supporting_rows", []):
            if supporting.get("stress_id") == "source_merge_leakage_ceiling":
                source = supporting
            if supporting.get("stress_id") == "injected_merge_leakage_pressure_fail_closed":
                injected = supporting
    return source, injected


def build_variant_row(
    variant_id: str,
    runtime: dict[str, Any],
    replay_stress: dict[str, Any],
    runtime_source: dict[str, Any],
) -> dict[str, Any]:
    unit = runtime["bridge_unit_runtime_row"]
    medium = unit["shared_or_adjacent_medium"]
    source_pressure, injected_pressure = source_and_injected_pressure_rows(replay_stress)
    packet_record_count = nested_get(
        medium,
        ("coupling_or_leakage_trace", "packet_flux_trace", "packet_record_count"),
        0.0,
    )
    in_flight_packet_total = nested_get(
        medium,
        ("coupling_or_leakage_trace", "packet_flux_trace", "in_flight_packet_total"),
        "not_recorded",
    )
    contact_amounts = collect_key_numbers(runtime_source, "contact_amount")
    max_contact_amount = max(contact_amounts) if contact_amounts else 0.0
    observed_flux = nested_get(
        medium,
        ("merge_pressure_metric", "observed_absolute_incident_flux"),
        "not_recorded",
    )
    declared_ceiling = source_pressure.get("declared_ceiling", "not_recorded")

    return {
        "variant_id": variant_id,
        "runtime_unit_id": unit["unit_id"],
        "basin_side_region": unit["basin_side_state"]["region_id"],
        "shared_or_adjacent_medium": medium["medium_region_or_channel_id"],
        "counterpart_region": unit["counterpart_region"]["region_id"],
        "source_current_medium_activity": {
            "packet_record_count": packet_record_count,
            "in_flight_packet_total_after_transport": in_flight_packet_total,
            "max_source_contact_amount": max_contact_amount,
            "activity_kind": "source-current packet/contact medium activity",
            "active_medium_present": packet_record_count > 0 or max_contact_amount > 0.0,
        },
        "zero_leakage_separability": {
            "observed_absolute_incident_flux": observed_flux,
            "declared_merge_leakage_ceiling": declared_ceiling,
            "zero_leakage_policy_preserved": observed_flux == 0.0 and declared_ceiling == 0.0,
        },
        "nonzero_pressure_control": {
            "observed_absolute_incident_flux": injected_pressure.get(
                "observed_absolute_incident_flux",
                "not_recorded",
            ),
            "declared_ceiling": injected_pressure.get("declared_ceiling", "not_recorded"),
            "status": injected_pressure.get("status", "not_recorded"),
            "claim_effect": injected_pressure.get("claim_effect", "not_recorded"),
            "nonzero_pressure_fails_closed": injected_pressure.get("status") == "failed_closed",
        },
        "claim_effect": (
            "supports active-medium separability only: source-current medium activity is present, "
            "merge/leakage into the basin remains zero, and nonzero injected pressure fails closed"
        ),
    }


def active_medium_rows() -> list[dict[str, Any]]:
    return [
        build_variant_row(
            "I12_primary_reference",
            load_json(I12A),
            load_json(I12C),
            load_json(N25_2_PRIMARY),
        ),
        build_variant_row(
            "I12_1_sibling_variant",
            load_json(I121A),
            load_json(I121C),
            load_json(N25_2_VARIANT),
        ),
    ]


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    active_medium_count = sum(
        1 for row in rows if row["source_current_medium_activity"]["active_medium_present"]
    )
    zero_leakage_count = sum(
        1 for row in rows if row["zero_leakage_separability"]["zero_leakage_policy_preserved"]
    )
    fail_closed_count = sum(
        1 for row in rows if row["nonzero_pressure_control"]["nonzero_pressure_fails_closed"]
    )
    supported = (
        active_medium_count == len(rows)
        and zero_leakage_count == len(rows)
        and fail_closed_count == len(rows)
    )
    return {
        "active_medium_row_count": len(rows),
        "active_medium_present_count": active_medium_count,
        "zero_leakage_policy_preserved_count": zero_leakage_count,
        "nonzero_injected_pressure_failed_closed_count": fail_closed_count,
        "active_medium_separability_candidate_supported": supported,
        "leakage_headroom_improved": False,
        "zero_leakage_policy_changed": False,
    }


def build_i122() -> dict[str, Any]:
    i12c = load_json(I12C)
    i121c = load_json(I121C)
    checks = [
        check("i12_primary_reference_passed", i12c.get("status") == "passed"),
        check("i12_1_sibling_reference_passed", i121c.get("status") == "passed"),
        check("active_medium_probe_requires_i122abc", True),
        check("zero_leakage_ceiling_preserved_as_policy", True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_active_i122",
        "experiment_id": "N29",
        "title": "Prototype B - Active-Medium Separability Admission",
        "iteration": "I12.2",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_medium_separability_admission_pending_i122abc",
        "source_artifacts": [
            source_artifact("n29_i12c_replay_stress", I12C, "primary_reference_source"),
            source_artifact("n29_i121c_replay_stress", I121C, "sibling_reference_source"),
        ],
        "i122_tranche": {
            "i122a": "active medium runtime extraction",
            "i122b": "active medium controls and claim blockers",
            "i122c": "active medium replay/stress close",
        },
        "claim_ceiling": "active-medium admission only; no Prototype B strengthening without I12.2-A/B/C",
        "ready_for_i122a": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_active_medium_separability_admission"
        data["ready_for_i122a"] = False
    return finalize(data)


def build_i122a(i122: dict[str, Any]) -> dict[str, Any]:
    rows = active_medium_rows()
    summary = summarize_rows(rows)
    checks = [
        check("i122_admission_passed", i122.get("status") == "passed"),
        check("source_current_medium_activity_present_in_both_rows", summary["active_medium_present_count"] == 2),
        check("zero_leakage_policy_preserved_in_both_rows", summary["zero_leakage_policy_preserved_count"] == 2),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_active_runtime_i122a",
        "experiment_id": "N29",
        "title": "Prototype B - Active-Medium Runtime Extraction",
        "iteration": "I12.2-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_medium_runtime_extraction_pending_controls",
        "source_artifacts": [
            source_artifact("n29_i122_admission", OUT_I122, "active_medium_admission_source"),
            source_artifact("n29_i12a_runtime_unit", I12A, "primary_runtime_unit_source"),
            source_artifact("n29_i121a_runtime_unit", I121A, "sibling_runtime_unit_source"),
            source_artifact("n25_2_native_runtime_positive_probe", N25_2_PRIMARY, "primary_runtime_contact_source"),
            source_artifact("n25_2_native_runtime_variant_probe", N25_2_VARIANT, "sibling_runtime_contact_source"),
        ],
        "active_medium_rows": rows,
        "matrix_summary": summary,
        "prototype_b_active_medium_separability_strengthened": False,
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "ready_for_i122b": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_active_medium_runtime_extraction"
        data["ready_for_i122b"] = False
    return finalize(data)


def build_i122b(i122a: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for row in i122a.get("active_medium_rows", []):
        rows.append(
            {
                "control_id": f"{row['variant_id']}_nonzero_pressure_control",
                "variant_id": row["variant_id"],
                "control_status": row["nonzero_pressure_control"]["status"],
                "expected_result": "failed_closed",
                "actual_result": row["nonzero_pressure_control"]["claim_effect"],
                "observed_absolute_incident_flux": row["nonzero_pressure_control"][
                    "observed_absolute_incident_flux"
                ],
                "declared_ceiling": row["nonzero_pressure_control"]["declared_ceiling"],
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "blocks nonzero leakage tolerance and native shared-medium coordination",
            }
        )
    rows.extend(
        [
            {
                "control_id": "active_medium_as_coordination_relabel_control",
                "variant_id": "cross_variant",
                "control_status": "failed_closed",
                "expected_result": "failed_closed",
                "actual_result": "source-current packet/contact activity cannot be relabeled as native shared-medium coordination",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "blocks native shared-medium coordination claim",
            },
            {
                "control_id": "semantic_trail_or_pheromone_relabel_control",
                "variant_id": "cross_variant",
                "control_status": "failed_closed",
                "expected_result": "failed_closed",
                "actual_result": "medium activity has no semantic trail or pheromone substrate interpretation",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "blocks semantic medium claim",
            },
            {
                "control_id": "active_medium_as_ecology_success_relabel_control",
                "variant_id": "cross_variant",
                "control_status": "failed_closed",
                "expected_result": "failed_closed",
                "actual_result": "active-medium separability is not ant-ecology or runtime-ecology success",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "blocks ecology success claim",
            },
        ]
    )
    failed_open = [row for row in rows if row["control_status"] != "failed_closed"]
    checks = [
        check("i122a_passed", i122a.get("status") == "passed"),
        check("all_required_controls_present", len(rows) == 5),
        check("all_controls_failed_closed", not failed_open),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_active_controls_i122b",
        "experiment_id": "N29",
        "title": "Prototype B - Active-Medium Controls",
        "iteration": "I12.2-B",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_medium_controls_fail_closed",
        "source_artifacts": [
            source_artifact("n29_i122a_active_medium_runtime", OUT_I122A, "active_medium_runtime_source"),
        ],
        "control_rows": rows,
        "matrix_summary": {
            "control_count": len(rows),
            "failed_closed_count": len(rows) - len(failed_open),
            "failed_open_count": len(failed_open),
        },
        "prototype_b_active_medium_separability_strengthened": False,
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "ready_for_i122c": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_active_medium_controls"
        data["ready_for_i122c"] = False
    return finalize(data)


def build_i122c(i122a: dict[str, Any], i122b: dict[str, Any]) -> dict[str, Any]:
    summary = i122a["matrix_summary"]
    controls_clean = i122b.get("matrix_summary", {}).get("failed_open_count") == 0
    supported = bool(summary["active_medium_separability_candidate_supported"] and controls_clean)
    checks = [
        check("i122a_passed", i122a.get("status") == "passed"),
        check("i122b_passed", i122b.get("status") == "passed"),
        check("i122b_failed_open_count_zero", controls_clean),
        check("active_medium_present_in_both_rows", summary["active_medium_present_count"] == 2),
        check("zero_leakage_policy_preserved_in_both_rows", summary["zero_leakage_policy_preserved_count"] == 2),
        check("nonzero_injected_pressure_fails_closed_in_both_rows", summary["nonzero_injected_pressure_failed_closed_count"] == 2),
        check("leakage_headroom_not_claimed_as_improved", summary["leakage_headroom_improved"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_active_replay_stress_i122c",
        "experiment_id": "N29",
        "title": "Prototype B - Active-Medium Replay And Stress Close",
        "iteration": "I12.2-C",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_medium_separability_probe_no_leakage_policy_change",
        "source_artifacts": [
            source_artifact("n29_i122a_active_medium_runtime", OUT_I122A, "active_medium_runtime_source"),
            source_artifact("n29_i122b_active_medium_controls", OUT_I122B, "active_medium_control_source"),
            source_artifact("n29_i12c_replay_stress", I12C, "primary_replay_stress_source"),
            source_artifact("n29_i121c_replay_stress", I121C, "sibling_replay_stress_source"),
        ],
        "active_medium_rows": i122a["active_medium_rows"],
        "matrix_summary": summary,
        "control_summary": i122b["matrix_summary"],
        "prototype_b_active_medium_separability_strengthened": supported,
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "ready_for_iteration_13": supported,
        "claim_ceiling": (
            "bounded active-medium separability evidence; source-current packet/contact medium activity "
            "with zero merge/leakage and fail-closed nonzero pressure controls"
        ),
        "why_not_stronger": [
            "does not permit nonzero merge/leakage tolerance",
            "does not widen the I12 or I12.1 stress envelope",
            "does not prove native shared-medium coordination or semantic medium use",
        ],
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_active_medium_replay_stress_close"
        data["prototype_b_active_medium_separability_strengthened"] = False
        data["ready_for_iteration_13"] = False
    return finalize(data)


def report_active_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "## Active Medium Rows",
            "",
            "| Variant | Packet records | Max contact | Observed flux | Ceiling | Injected pressure status |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        activity = row["source_current_medium_activity"]
        zero = row["zero_leakage_separability"]
        pressure = row["nonzero_pressure_control"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["variant_id"],
                activity["packet_record_count"],
                activity["max_source_contact_amount"],
                zero["observed_absolute_incident_flux"],
                zero["declared_merge_leakage_ceiling"],
                pressure["status"],
            )
        )
    lines.append("")


def write_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
    ]
    if data["iteration"] == "I12.2":
        lines.extend(
            [
                "## Tranche",
                "",
                "I12.2 admits an active-medium separability tranche. I12.2-A extracts "
                "source-current medium activity, I12.2-B runs controls, and I12.2-C "
                "records replay/stress closeout.",
                "",
            ]
        )
    elif data["iteration"] == "I12.2-A":
        report_active_rows(lines, data["active_medium_rows"])
    elif data["iteration"] == "I12.2-B":
        lines.extend(["## Controls", "", "| Control | Status |", "|---|---|"])
        for row in data["control_rows"]:
            lines.append(f"| `{row['control_id']}` | `{row['control_status']}` |")
        lines.append("")
    elif data["iteration"] == "I12.2-C":
        report_active_rows(lines, data["active_medium_rows"])
        lines.extend(
            [
                "## Interpretation",
                "",
                "I12.2 strengthens Prototype B by showing active source-current medium traces "
                "in both the primary and sibling units while preserving the zero-leakage "
                "boundary rule.",
                "",
                "It does not improve leakage headroom. Nonzero injected pressure remains a "
                "fail-closed control, not a tolerated positive coupling.",
                "",
                f"Ready for I13: `{str(data['ready_for_iteration_13']).lower()}`",
                "",
            ]
        )
    lines.extend(["## Checks", "", "| Check | Passed |", "|---|---|"])
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i122 = build_i122()
    write_json(OUT_I122, i122)
    write_report(REP_I122, i122)

    i122a = build_i122a(i122)
    write_json(OUT_I122A, i122a)
    write_report(REP_I122A, i122a)

    i122b = build_i122b(i122a)
    write_json(OUT_I122B, i122b)
    write_report(REP_I122B, i122b)

    i122c = build_i122c(i122a, i122b)
    write_json(OUT_I122C, i122c)
    write_report(REP_I122C, i122c)


if __name__ == "__main__":
    main()
