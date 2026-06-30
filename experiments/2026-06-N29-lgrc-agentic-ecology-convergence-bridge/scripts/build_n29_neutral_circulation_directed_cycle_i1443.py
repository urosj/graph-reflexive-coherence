#!/usr/bin/env python3
"""Build N29 I14.4-3 native directed-circulation cycle search."""

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
    "build_n29_neutral_circulation_directed_cycle_i1443.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
I1442 = EXPERIMENT / "outputs" / "n29_neutral_circulation_native_search_i1442.json"
N28_OUTPUTS = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
)

OUT = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_i1443.json"
REPORT = EXPERIMENT / "reports" / "n29_neutral_circulation_directed_cycle_i1443.md"

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


def row_source_current(row: dict[str, Any]) -> bool:
    if row.get("derived_report_only") is True:
        return False
    if row.get("producer_mediated_loop_closure_candidate") is True:
        return False
    if row.get("source_current_inputs"):
        return True
    return bool(row.get("all_artifact_sha256_match_file_contents") is True)


def consumes_prior_changed_medium(row: dict[str, Any], prior_row_id: str) -> bool:
    dependency = row.get("closure_dependency_trace") or row.get("composition_dependency_trace") or {}
    if dependency.get("second_leg_consumes_forward_changed_distribution") is True:
        return True
    if dependency.get("reverse_leg_consumes_forward_changed_distribution") is True:
        return True
    text = json.dumps(row, sort_keys=True, ensure_ascii=True)
    consumption_tokens = (
        "consumes_prior_changed_medium",
        "consumes_forward_changed_distribution",
        "source_current_input_from_prior_leg",
        "later_internal_dependence",
    )
    return prior_row_id in text and any(token in text for token in consumption_tokens)


def returns_to_starting_pattern_class(row: dict[str, Any]) -> bool:
    dependency = row.get("closure_dependency_trace") or row.get("composition_dependency_trace") or {}
    if dependency.get("later_forward_side_state_depends_on_reverse_leg") is True:
        return True
    if dependency.get("later_a_class_state_depends_on_second_leg") is True:
        return True
    text = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return "returns_to_starting_pattern_class" in text or "later_A_class" in text


def scan_native_neutral_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(N28_OUTPUTS.glob("*.json")):
        data = load_json(path)
        for row in data.get("candidate_rows") or []:
            trace = row.get("capacity_attribution_trace") or {}
            if trace.get("neutral_circulation_detected") is not True:
                continue
            rows.append(
                {
                    "source_path": str(path.relative_to(ROOT)),
                    "source_artifact_id": data.get("artifact_id", "not_recorded"),
                    "source_output_digest": data.get("output_digest", "not_recorded"),
                    "row_id": row.get("row_id", "not_recorded"),
                    "row_digest": row.get("row_digest", "not_recorded"),
                    "source_current_native": row_source_current(row),
                    "mechanism_class": trace.get("mechanism_class"),
                    "inflow_lobe_capacity_delta": trace.get("inflow_lobe_capacity_delta"),
                    "outflow_lobe_capacity_delta": trace.get("outflow_lobe_capacity_delta"),
                    "buffer_lobe_capacity_delta": trace.get("buffer_lobe_capacity_delta"),
                    "neutral_circulation_detected": True,
                    "consumes_i4f_changed_medium": consumes_prior_changed_medium(row, FORWARD_ROW_ID),
                    "returns_to_starting_pattern_class": returns_to_starting_pattern_class(row),
                }
            )
    return rows


def directed_cycle_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    forward_rows = [
        row
        for row in rows
        if row["source_current_native"] and row["row_id"] == FORWARD_ROW_ID
    ]
    second_rows = [
        row
        for row in rows
        if row["source_current_native"]
        and row["row_id"] != FORWARD_ROW_ID
        and row["consumes_i4f_changed_medium"]
        and row["returns_to_starting_pattern_class"]
    ]
    for first in forward_rows:
        for second in second_rows:
            pairs.append(
                {
                    "first_leg_row_id": first["row_id"],
                    "second_leg_row_id": second["row_id"],
                    "first_leg_mechanism_class": first["mechanism_class"],
                    "second_leg_mechanism_class": second["mechanism_class"],
                    "directed_cycle_supported": True,
                }
            )
    return pairs


def build_record() -> dict[str, Any]:
    i144 = load_json(I144)
    i1442 = load_json(I1442)
    rows = scan_native_neutral_rows()
    pairs = directed_cycle_pairs(rows)
    cycle_found = len(pairs) > 0
    search = {
        "definition": "directed_closed_dependency_cycle_not_reverse_bounce",
        "loop_requirement": [
            "forward leg A changes local capacity distribution",
            "later forward leg B consumes A's changed distribution as source-current input",
            "later A-side or A-class state depends on B's changed distribution",
        ],
        "not_required": [
            "opposite-orientation sign inversion",
            "bounce-back over the same channel",
            "label-swapped reverse leg",
        ],
        "native_rows_scanned": rows,
        "directed_cycle_pairs": pairs,
    }
    row = {
        "row_id": "n29_i14_4_3_native_directed_circulation_cycle_search",
        "row_decision": "blocked",
        "row_decision_scope": "native_directed_cycle_absent_under_broader_loop_definition",
        "native_forward_neutral_circulation_leg_found": any(
            item["row_id"] == FORWARD_ROW_ID and item["source_current_native"] for item in rows
        ),
        "native_directed_cycle_found": cycle_found,
        "native_closed_environmental_circulation_supported": False,
        "producer_fallback_used": False,
        "i14_4_2_reverse_only_scope_corrected": True,
        "why_i14_4_3_differs": (
            "I14.4-2 searched for an opposite-orientation reverse leg. I14.4-3 "
            "uses the broader loop definition: all legs may point forward, as "
            "long as their ordered dependencies close back to the starting "
            "pattern class."
        ),
        "claim_ceiling": "native_directed_circulation_cycle_search_blocked_no_ordered_dependency_cycle",
        "blocked_reason": (
            "Native neutral-circulation rows exist, but none records a later "
            "forward leg that consumes the I4-F changed medium and returns "
            "dependency to the starting pattern class."
        ),
        "native_directed_cycle_search": search,
        "remaining_debt": [
            "native LGRC needs ordered multi-leg circulation telemetry over changed medium states",
            "I14.4-1 remains a producer-mediated bridge candidate for how closure could work",
            "a future native directed cycle need not be opposite-orientation, but it must be source-current and dependency-closed",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_neutral_circulation_directed_cycle_i1443",
        "experiment_id": "N29",
        "title": "Prototype D I14.4-3 Native Directed Circulation Cycle Search",
        "iteration": "I14.4-3",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_native_directed_cycle_absent_broader_loop_definition_recorded",
        "source_artifacts": [
            source_artifact("n29_i14_4_single_direction_circulation", I144, i144),
            source_artifact("n29_i14_4_2_native_reverse_search", I1442, i1442),
        ],
        "native_directed_cycle_search_row": row,
        "native_directed_cycle_found": cycle_found,
        "native_closed_environmental_circulation_supported": False,
        "producer_fallback_used": False,
        "ready_for_i14d_i14e": False,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("broader_loop_definition_recorded", row["i14_4_2_reverse_only_scope_corrected"] is True),
            check("native_forward_leg_found", row["native_forward_neutral_circulation_leg_found"] is True),
            check("producer_fallback_not_used", row["producer_fallback_used"] is False),
            check("native_directed_cycle_absent", row["native_directed_cycle_found"] is False),
            check("native_closed_loop_blocked", row["native_closed_environmental_circulation_supported"] is False),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_4_3_native_directed_cycle_search"
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["native_directed_cycle_search_row"]
    lines = [
        "# Prototype D I14.4-3 Native Directed Circulation Cycle Search",
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
        f"native_directed_cycle_found = {str(data['native_directed_cycle_found']).lower()}",
        f"native_closed_environmental_circulation_supported = {str(data['native_closed_environmental_circulation_supported']).lower()}",
        f"producer_fallback_used = {str(data['producer_fallback_used']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        "```",
        "",
        "## Difference From I14.4-2",
        "",
        row["why_i14_4_3_differs"],
        "",
        "A loop can be a directed cycle, not a bounce-back. It can move forward",
        "from one pattern to another and then forward again into a later state",
        "that closes dependency back to the starting pattern class. I14.4-3",
        "therefore does not require sign-inverted opposite orientation.",
        "",
        "## Interpretation",
        "",
        "Under this broader loop definition, the native result is still negative",
        "for the current source set. Native neutral-circulation rows exist, but",
        "none records a later source-current leg that consumes the I4-F changed",
        "medium and returns dependency to the starting pattern class.",
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
