#!/usr/bin/env python3
"""Build N29 I14.4-2 native-only neutral-circulation closure search."""

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
    "build_n29_neutral_circulation_native_search_i1442.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
I1441 = EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
N28_OUTPUTS = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
)

OUT = EXPERIMENT / "outputs" / "n29_neutral_circulation_native_search_i1442.json"
REPORT = EXPERIMENT / "reports" / "n29_neutral_circulation_native_search_i1442.md"

FORWARD_ROW_ID = "n28_i4f_row_higher_margin_neutral_circulation_contrast"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def direction_for(trace: dict[str, Any]) -> str:
    inflow = trace.get("inflow_lobe_capacity_delta")
    outflow = trace.get("outflow_lobe_capacity_delta")
    if not isinstance(inflow, (int, float)) or not isinstance(outflow, (int, float)):
        return "missing_lobe_delta"
    if inflow > 0 and outflow < 0:
        return "forward_orientation"
    if inflow < 0 and outflow > 0:
        return "reverse_orientation"
    return "not_opposite_orientation"


def consumes_forward_post_state(row: dict[str, Any]) -> bool:
    dependency = row.get("closure_dependency_trace") or row.get("composition_dependency_trace") or {}
    if dependency.get("reverse_leg_consumes_forward_changed_distribution") is True:
        return True
    if dependency.get("second_leg_consumes_forward_changed_distribution") is True:
        return True
    source_ids = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return FORWARD_ROW_ID in source_ids and "consumes_forward" in source_ids


def row_source_current(row: dict[str, Any]) -> bool:
    if row.get("derived_report_only") is True:
        return False
    if row.get("producer_mediated_loop_closure_candidate") is True:
        return False
    if row.get("producer_mediated_phase_bridge") is True:
        return False
    if row.get("source_current_inputs"):
        return True
    return bool(row.get("all_artifact_sha256_match_file_contents") is True)


def scan_native_neutral_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    scanned: list[dict[str, Any]] = []
    forward: list[dict[str, Any]] = []
    reverse: list[dict[str, Any]] = []
    for path in sorted(N28_OUTPUTS.glob("*.json")):
        data = load_json(path)
        for row in data.get("candidate_rows") or []:
            trace = row.get("capacity_attribution_trace") or {}
            if trace.get("neutral_circulation_detected") is not True:
                continue
            direction = direction_for(trace)
            record = {
                "source_path": str(path.relative_to(ROOT)),
                "source_artifact_id": data.get("artifact_id", "not_recorded"),
                "source_output_digest": data.get("output_digest", "not_recorded"),
                "row_id": row.get("row_id", "not_recorded"),
                "row_digest": row.get("row_digest", "not_recorded"),
                "source_current_native": row_source_current(row),
                "producer_mediated": False,
                "direction": direction,
                "inflow_lobe_capacity_delta": trace.get("inflow_lobe_capacity_delta"),
                "outflow_lobe_capacity_delta": trace.get("outflow_lobe_capacity_delta"),
                "buffer_lobe_capacity_delta": trace.get("buffer_lobe_capacity_delta"),
                "neutral_circulation_detected": True,
                "consumes_forward_post_state": consumes_forward_post_state(row),
            }
            scanned.append(record)
            if record["source_current_native"] and direction == "forward_orientation":
                forward.append(record)
            if (
                record["source_current_native"]
                and direction == "reverse_orientation"
                and record["consumes_forward_post_state"]
            ):
                reverse.append(record)
    return scanned, forward, reverse


def build_record() -> dict[str, Any]:
    i144 = load_json(I144)
    i1441 = load_json(I1441)
    scanned, forward_rows, reverse_rows = scan_native_neutral_rows()
    native_reverse_leg_found = len(reverse_rows) > 0
    row = {
        "row_id": "n29_i14_4_2_native_neutral_circulation_closure_search",
        "row_decision": "blocked",
        "row_decision_scope": "native_only_reverse_leg_absent_closed_loop_blocked",
        "native_forward_neutral_circulation_leg_found": len(forward_rows) > 0,
        "native_reverse_opposite_orientation_leg_found": native_reverse_leg_found,
        "native_reverse_leg_consumes_forward_post_state": native_reverse_leg_found,
        "native_closed_environmental_circulation_supported": False,
        "producer_fallback_used": False,
        "producer_mediated_i14_4_1_consumed_as_context_only": True,
        "closed_environmental_circulation_loop_claim_allowed": False,
        "claim_ceiling": "native_only_closed_circulation_search_blocked_reverse_leg_absent",
        "blocked_reason": (
            "No source-current native opposite-orientation neutral-circulation leg "
            "was found that consumes the I4-F forward post-state."
        ),
        "native_search_result": {
            "scanned_native_neutral_row_count": len(scanned),
            "forward_orientation_native_row_count": len(forward_rows),
            "reverse_orientation_native_consuming_forward_row_count": len(reverse_rows),
            "candidate_rows_scanned": scanned,
        },
        "remaining_debt": [
            "native LGRC needs a runtime mechanism that emits the reverse leg from the changed medium state",
            "I14.4-1 producer-mediated reverse leg remains bridge evidence only",
            "I14-D/I14-E cannot validate native closed circulation without a native reverse leg",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_neutral_circulation_native_search_i1442",
        "experiment_id": "N29",
        "title": "Prototype D I14.4-2 Native-Only Neutral Circulation Closure Search",
        "iteration": "I14.4-2",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_native_only_reverse_leg_absent_closed_loop_blocked",
        "source_artifacts": [
            source_artifact("n29_i14_4_single_direction_circulation", I144, i144),
            source_artifact("n29_i14_4_1_producer_loop_context_only", I1441, i1441),
        ],
        "native_search_row": row,
        "native_forward_neutral_circulation_leg_found": row[
            "native_forward_neutral_circulation_leg_found"
        ],
        "native_reverse_opposite_orientation_leg_found": row[
            "native_reverse_opposite_orientation_leg_found"
        ],
        "native_closed_environmental_circulation_supported": False,
        "producer_fallback_used": False,
        "ready_for_i14d_i14e": False,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("native_forward_leg_found", row["native_forward_neutral_circulation_leg_found"] is True),
            check("producer_fallback_not_used", row["producer_fallback_used"] is False),
            check("native_reverse_leg_absent", row["native_reverse_opposite_orientation_leg_found"] is False),
            check("native_closed_loop_blocked", row["native_closed_environmental_circulation_supported"] is False),
            check("i14_4_1_context_does_not_upgrade_native", row["producer_mediated_i14_4_1_consumed_as_context_only"] is True),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_4_2_native_only_search"
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["native_search_row"]
    lines = [
        "# Prototype D I14.4-2 Native-Only Neutral Circulation Closure Search",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Summary",
        "",
        "```text",
        f"native_forward_neutral_circulation_leg_found = {str(data['native_forward_neutral_circulation_leg_found']).lower()}",
        f"native_reverse_opposite_orientation_leg_found = {str(data['native_reverse_opposite_orientation_leg_found']).lower()}",
        f"native_closed_environmental_circulation_supported = {str(data['native_closed_environmental_circulation_supported']).lower()}",
        f"producer_fallback_used = {str(data['producer_fallback_used']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.4-2 is the native-only answer to the I14.4/I14.4-1 split. It finds",
        "native/source-current forward neutral-circulation rows, but it does not",
        "find a native opposite-orientation row that consumes the I4-F forward",
        "post-state. Therefore native closed environmental circulation remains",
        "blocked. The I14.4-1 producer-mediated bridge remains useful as a",
        "missing-mechanism probe, but it is not allowed to upgrade the native row.",
        "",
        f"Blocked reason: {row['blocked_reason']}",
        "",
        "## Remaining Debt",
        "",
    ]
    lines.extend(f"- {item}" for item in row["remaining_debt"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |"
        for check_row in data["checks"]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    data = build_record()
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
